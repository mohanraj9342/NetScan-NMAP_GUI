import socket
import threading
import time
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ---------------------------
# Service Map (extend freely)
# ---------------------------
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
    3306: 'MySQL', 3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-Alt'
}

# ---------------------------
# Colour Palette
# ---------------------------
C = {
    "bg":           "#0d1117",   # deepest background
    "surface":      "#161b22",   # card / panel background
    "surface2":     "#1c2330",   # slightly lighter
    "border":       "#30363d",   # subtle border
    "accent":       "#238636",   # green accent (Start / open port)
    "accent_hover": "#2ea043",
    "danger":       "#da3633",   # Stop / error
    "danger_hover": "#f85149",
    "primary":      "#1f6feb",   # blue accent (Save / meta)
    "primary_hover":"#388bfd",
    "neutral":      "#21262d",   # Clear button
    "neutral_hover":"#30363d",
    "text":         "#e6edf3",   # primary text
    "text_dim":     "#8b949e",   # muted text
    "text_meta":    "#58a6ff",   # blue info text
    "text_success": "#3fb950",   # open port
    "text_error":   "#f85149",   # error
    "text_warn":    "#d29922",   # warning
    "progress_bg":  "#21262d",
    "progress_fill":"#1f6feb",
    "header_top":   "#0d1117",
    "header_bot":   "#161b22",
}

FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_SUB    = ("Segoe UI", 9)
FONT_LABEL  = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 10, "bold")
FONT_MONO   = ("Consolas", 10)
FONT_BADGE  = ("Segoe UI", 8, "bold")
FONT_STAT   = ("Segoe UI", 9)

# ---------------------------
# Scanner Worker  (unchanged)
# ---------------------------
class PortScanner:
    def __init__(self, target, start_port, end_port, timeout=0.5, max_workers=500):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.max_workers = max_workers
        self._stop_event = threading.Event()

        self.total_ports = max(0, end_port - start_port + 1)
        self.scanned_count = 0
        self.open_ports = []
        self.error_count = 0
        self._lock = threading.Lock()
        self.result_queue = queue.Queue()

    def stop(self):
        self._stop_event.set()

    def _scan_port(self, port):
        if self._stop_event.is_set():
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.target, port))
            if result == 0:
                service = COMMON_PORTS.get(port, 'Unknown')
                with self._lock:
                    self.open_ports.append((port, service))
                self.result_queue.put(('open', port, service))
        except Exception as e:
            with self._lock:
                self.error_count += 1
            self.result_queue.put(('error', port, str(e)))
        finally:
            with self._lock:
                self.scanned_count += 1
            self.result_queue.put(('progress', self.scanned_count, self.total_ports))

    def resolve_target(self):
        return socket.gethostbyname(self.target)

    def run(self):
        port_queue = queue.Queue()
        for port in range(self.start_port, self.end_port + 1):
            port_queue.put(port)

        worker_count = max(1, min(self.max_workers, self.total_ports))
        threads = []

        for _ in range(worker_count):
            t = threading.Thread(target=self._queue_worker, args=(port_queue,), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.result_queue.put(('done', None, None))

    def _queue_worker(self, port_queue):
        while not self._stop_event.is_set():
            try:
                port = port_queue.get_nowait()
            except queue.Empty:
                return
            try:
                self._scan_port(port)
            finally:
                port_queue.task_done()


# ---------------------------
# Reusable Widget Helpers
# ---------------------------
def dark_entry(parent, width=20, **kw):
    """A tk.Entry styled for the dark theme."""
    e = tk.Entry(
        parent,
        width=width,
        bg=C["surface2"],
        fg=C["text"],
        insertbackground=C["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=C["border"],
        highlightcolor=C["primary"],
        font=FONT_LABEL,
        **kw,
    )
    return e


class DarkButton(tk.Frame):
    """Flat button using Frame+Label — works reliably on all Python/tkinter versions."""

    def __init__(self, parent, text, command=None,
                 bg=C["neutral"], hover=C["neutral_hover"],
                 fg=C["text"], font=FONT_BOLD,
                 width=120, height=32, radius=6, **kw):
        # Determine parent background for the outer frame border
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = C["bg"]

        super().__init__(parent, bg=parent_bg, **kw)

        self._bg = bg
        self._hover = hover
        self._fg = fg
        self._disabled = False
        self._command = command

        self._inner = tk.Frame(self, bg=bg, padx=14, pady=0)
        self._inner.pack(fill="both", expand=True, padx=0, pady=0)

        self._lbl = tk.Label(
            self._inner, text=text, font=font,
            bg=bg, fg=fg,
            height=2,
            cursor="hand2",
        )
        self._lbl.pack(fill="both", expand=True)

        for widget in (self, self._inner, self._lbl):
            widget.bind("<Enter>",          self._on_enter)
            widget.bind("<Leave>",          self._on_leave)
            widget.bind("<ButtonPress-1>",  self._on_press)
            widget.bind("<ButtonRelease-1>",self._on_release)

    def _on_enter(self, _e=None):
        if not self._disabled:
            self._inner.config(bg=self._hover)
            self._lbl.config(bg=self._hover)

    def _on_leave(self, _e=None):
        if not self._disabled:
            self._inner.config(bg=self._bg)
            self._lbl.config(bg=self._bg)

    def _on_press(self, _e=None):
        if not self._disabled:
            # Slightly darken on press (reuse base colour)
            self._inner.config(bg=self._bg)
            self._lbl.config(bg=self._bg)

    def _on_release(self, _e=None):
        if not self._disabled:
            self._inner.config(bg=self._hover)
            self._lbl.config(bg=self._hover)
            if self._command:
                self._command()

    def configure_state(self, state):
        if state == "disabled":
            self._disabled = True
            self._inner.config(bg=C["border"])
            self._lbl.config(bg=C["border"], fg=C["text_dim"], cursor="")
        else:
            self._disabled = False
            self._inner.config(bg=self._bg)
            self._lbl.config(bg=self._bg, fg=self._fg, cursor="hand2")

    def set_text(self, text):
        self._lbl.config(text=text)


class AnimatedProgressBar(tk.Canvas):
    """Custom dark progress bar with percentage label and shimmer."""

    def __init__(self, parent, width=600, height=18, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=C["surface"], highlightthickness=0, **kw)
        self._max = 100
        self._val = 0
        self._width = width
        self._height = height
        # track background
        self.create_rectangle(0, 0, width, height,
                               fill=C["progress_bg"], outline="")
        # filled bar
        self._bar  = self.create_rectangle(0, 0, 0, height,
                                            fill=C["progress_fill"], outline="")
        # percentage text
        self._pct  = self.create_text(width // 2, height // 2,
                                       text="0%", fill=C["text"], font=FONT_BADGE)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self._width = event.width
        self.coords(self._pct, self._width // 2, self._height // 2)
        self._redraw()

    def set(self, value, maximum):
        self._val = value
        self._max = max(maximum, 1)
        self._redraw()

    def reset(self):
        self._val = 0
        self._max = 100
        self._redraw()

    def _redraw(self):
        fraction = min(self._val / self._max, 1.0)
        fill_w = int(self._width * fraction)
        pct = int(fraction * 100)
        self.coords(self._bar, 0, 0, fill_w, self._height)
        # Switch text colour for contrast
        txt_col = C["text"] if fraction > 0.45 else C["text_dim"]
        self.itemconfig(self._pct, text=f"{pct}%", fill=txt_col)


class StatusBadge(tk.Frame):
    """Coloured pill badge showing current status text."""

    _COLOURS = {
        "Idle":       ("#8b949e", C["surface2"]),
        "Scanning":   ("#1f6feb", "#0d2044"),
        "Completed":  ("#3fb950", "#0d2b1a"),
        "Stopped":    ("#d29922", "#2b1d00"),
        "Stopping":   ("#d29922", "#2b1d00"),
    }

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["surface"], **kw)
        self._lbl = tk.Label(self, text=" IDLE ", font=FONT_BADGE,
                              bg=C["surface2"], fg="#8b949e",
                              padx=8, pady=2, relief="flat")
        self._lbl.pack()

    def set(self, status_text):
        key = status_text.split("…")[0].split(".")[0].strip().capitalize()
        # Normalise "Scanning..." → "Scanning"
        key = key.rstrip(".")
        if "scanning" in status_text.lower():
            key = "Scanning"
        fg, bg = self._COLOURS.get(key, ("#8b949e", C["surface2"]))
        self._lbl.config(text=f"  {status_text.upper()[:20]}  ", fg=fg, bg=bg)


# ---------------------------
# Main GUI
# ---------------------------
class ScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NMAP — Network Port Scanner")
        self.geometry("960x680")
        self.minsize(820, 600)
        self.configure(bg=C["bg"])

        self.scanner_thread = None
        self.scanner = None
        self.start_time = None
        self.poll_after_ms = 40
        self.max_error_lines = 10
        self.error_lines_shown = 0

        self.profiles = {
            "Custom":      (1,    1024),
            "Top 100":     (1,     100),
            "Top 1000":    (1,    1000),
            "Common Web":  (80,   8080),
            "Full Scan":   (1,   65535),
        }

        self.var_open_count = tk.IntVar(value=0)
        self.var_error_count = tk.IntVar(value=0)
        self.var_rate       = tk.StringVar(value="0.0 p/s")
        self.var_elapsed    = tk.StringVar(value="0.00s")
        self.var_profile    = tk.StringVar(value="Custom")

        self._build_ui()
        self.bind("<Return>",     lambda _: self.start_scan())
        self.bind("<Control-s>",  lambda _: self.save_results())
        self.bind("<Escape>",     lambda _: self.stop_scan())

    # ================================================
    # UI Construction
    # ================================================
    def _build_ui(self):
        self._build_header()
        self._build_settings_panel()
        self._build_stats_bar()
        self._build_progress_panel()
        self._build_console()

    # ---- Header ----
    def _build_header(self):
        hdr = tk.Frame(self, bg=C["surface"], pady=0)
        hdr.pack(fill="x")

        # Left: icon + text
        left = tk.Frame(hdr, bg=C["surface"])
        left.pack(side="left", fill="y", padx=(18, 0), pady=14)

        icon_canvas = tk.Canvas(left, width=40, height=40,
                                 bg=C["surface"], highlightthickness=0)
        icon_canvas.pack(side="left", padx=(0, 12))
        self._draw_shield(icon_canvas, 20, 20, 18)

        text_frame = tk.Frame(left, bg=C["surface"])
        text_frame.pack(side="left")

        tk.Label(text_frame, text="Network Port Scanner",
                 font=FONT_TITLE, bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(text_frame, text="Fast TCP port scanner with live progress & profile presets",
                 font=FONT_SUB, bg=C["surface"], fg=C["text_dim"]).pack(anchor="w")

        # Right: keyboard shortcuts hint
        right = tk.Frame(hdr, bg=C["surface"])
        right.pack(side="right", padx=18, pady=14)
        hints = [("↵ Start", C["text_success"]),
                 ("  Esc Stop", C["text_warn"]),
                 ("  Ctrl+S Save", C["text_meta"])]
        row = tk.Frame(right, bg=C["surface"])
        row.pack(anchor="e")
        for hint_txt, col in hints:
            tk.Label(row, text=hint_txt, font=FONT_SUB,
                     bg=C["surface"], fg=col).pack(side="left")

        # Separator line
        sep = tk.Frame(self, bg=C["border"], height=1)
        sep.pack(fill="x")

    def _draw_shield(self, canvas, cx, cy, r):
        """Simple shield / radar icon using canvas primitives."""
        # Outer arc
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                            outline=C["primary"], width=2)
        # Inner circle
        canvas.create_oval(cx - r//2, cy - r//2, cx + r//2, cy + r//2,
                            outline=C["text_success"], width=1)
        # Crosshair
        canvas.create_line(cx, cy - r, cx, cy + r, fill=C["border"], width=1)
        canvas.create_line(cx - r, cy, cx + r, cy, fill=C["border"], width=1)
        # Dot
        canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                            fill=C["primary"], outline="")

    # ---- Settings Panel ----
    def _build_settings_panel(self):
        card = self._card(self, title="⚙  Scan Settings", pady_inner=(12, 8))

        # Row 0 — Target
        tk.Label(card, text="Target IP / Hostname", font=FONT_LABEL,
                 bg=C["surface"], fg=C["text_dim"]).grid(
            row=0, column=0, padx=(0, 8), pady=6, sticky="e")

        self.ent_target = dark_entry(card, width=38)
        self.ent_target.grid(row=0, column=1, padx=(0, 16), pady=6, sticky="ew")

        tk.Label(card, text="Profile", font=FONT_LABEL,
                 bg=C["surface"], fg=C["text_dim"]).grid(
            row=0, column=2, padx=(0, 8), pady=6, sticky="e")

        # Style the combobox
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                         fieldbackground=C["surface2"],
                         background=C["surface2"],
                         foreground=C["text"],
                         selectbackground=C["primary"],
                         selectforeground=C["text"],
                         bordercolor=C["border"],
                         arrowcolor=C["text_dim"])
        style.map("Dark.TCombobox", fieldbackground=[("readonly", C["surface2"])])

        self.cmb_profile = ttk.Combobox(
            card, width=13, state="readonly",
            textvariable=self.var_profile,
            values=list(self.profiles.keys()),
            style="Dark.TCombobox",
        )
        self.cmb_profile.grid(row=0, column=3, padx=(0, 0), pady=6, sticky="w")
        self.cmb_profile.bind("<<ComboboxSelected>>", self.on_profile_selected)

        # Row 1 — Port range
        tk.Label(card, text="Start Port", font=FONT_LABEL,
                 bg=C["surface"], fg=C["text_dim"]).grid(
            row=1, column=0, padx=(0, 8), pady=6, sticky="e")

        self.ent_start = dark_entry(card, width=10)
        self.ent_start.insert(0, "1")
        self.ent_start.grid(row=1, column=1, padx=(0, 16), pady=6, sticky="w")

        tk.Label(card, text="End Port", font=FONT_LABEL,
                 bg=C["surface"], fg=C["text_dim"]).grid(
            row=1, column=2, padx=(0, 8), pady=6, sticky="e")

        self.ent_end = dark_entry(card, width=10)
        self.ent_end.insert(0, "1024")
        self.ent_end.grid(row=1, column=3, padx=(0, 0), pady=6, sticky="w")

        # Row 2 — Buttons
        btn_row = tk.Frame(card, bg=C["surface"])
        btn_row.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 4))

        self.btn_start = DarkButton(
            btn_row, text="▶  Start Scan",
            command=self.start_scan,
            bg=C["accent"], hover=C["accent_hover"],
            fg="#ffffff", width=130, height=34,
        )
        self.btn_start.pack(side="left")
        self.btn_start.config(cursor="hand2")

        self.btn_stop = DarkButton(
            btn_row, text="■  Stop",
            command=self.stop_scan,
            bg=C["danger"], hover=C["danger_hover"],
            fg="#ffffff", width=100, height=34,
        )
        self.btn_stop.pack(side="left", padx=(10, 0))
        self.btn_stop.configure_state("disabled")

        self.btn_clear = DarkButton(
            btn_row, text="✕  Clear",
            command=self.clear_results,
            bg=C["neutral"], hover=C["neutral_hover"],
            fg=C["text"], width=100, height=34,
        )
        self.btn_clear.pack(side="left", padx=(10, 0))
        self.btn_clear.config(cursor="hand2")

        self.btn_save = DarkButton(
            btn_row, text="💾  Save Results",
            command=self.save_results,
            bg=C["primary"], hover=C["primary_hover"],
            fg="#ffffff", width=140, height=34,
        )
        self.btn_save.pack(side="right")
        self.btn_save.configure_state("disabled")

        card.grid_columnconfigure(1, weight=1)

    # ---- Stats Bar ----
    def _build_stats_bar(self):
        bar = tk.Frame(self, bg=C["surface"], pady=0)
        bar.pack(fill="x", padx=14, pady=(8, 0))

        # Status badge
        badge_wrap = tk.Frame(bar, bg=C["surface"])
        badge_wrap.pack(side="left")
        tk.Label(badge_wrap, text="Status", font=FONT_STAT,
                 bg=C["surface"], fg=C["text_dim"]).pack(anchor="w")
        self.status_badge = StatusBadge(badge_wrap)
        self.status_badge.pack(anchor="w")

        def stat_item(parent, label, var, icon=""):
            f = tk.Frame(parent, bg=C["surface"])
            f.pack(side="left", padx=20)
            tk.Label(f, text=label, font=FONT_STAT,
                     bg=C["surface"], fg=C["text_dim"]).pack(anchor="w")
            tk.Label(f, textvariable=var, font=FONT_BOLD,
                     bg=C["surface"], fg=C["text"]).pack(anchor="w")

        stat_item(bar, "🟢 Open Ports",  self.var_open_count)
        stat_item(bar, "⚠  Errors",      self.var_error_count)
        stat_item(bar, "⏱ Elapsed",      self.var_elapsed)
        stat_item(bar, "⚡ Scan Rate",   self.var_rate)

    # ---- Progress Panel ----
    def _build_progress_panel(self):
        wrap = tk.Frame(self, bg=C["bg"])
        wrap.pack(fill="x", padx=14, pady=(8, 0))

        self.progress_bar = AnimatedProgressBar(wrap, height=20)
        self.progress_bar.pack(fill="x", expand=True)

    # ---- Console ----
    def _build_console(self):
        card = self._card(self, title="⬛  Scan Console", pady_inner=(8, 8))

        self.txt_results = tk.Text(
            card,
            height=16,
            wrap="none",
            background=C["bg"],
            foreground=C["text"],
            insertbackground=C["text"],
            selectbackground=C["primary"],
            relief="flat",
            font=FONT_MONO,
            padx=10,
            pady=8,
        )
        self.txt_results.pack(fill="both", expand=True, side="left")

        yscroll = tk.Scrollbar(card, orient="vertical",
                                command=self.txt_results.yview,
                                bg=C["surface2"], troughcolor=C["bg"],
                                relief="flat", width=10)
        yscroll.pack(side="right", fill="y")
        self.txt_results.configure(yscrollcommand=yscroll.set)

        # Text tags
        self.txt_results.tag_configure("info",    foreground=C["text"])
        self.txt_results.tag_configure("success", foreground=C["text_success"], font=(FONT_MONO[0], FONT_MONO[1], "bold"))
        self.txt_results.tag_configure("error",   foreground=C["text_error"])
        self.txt_results.tag_configure("warn",    foreground=C["text_warn"])
        self.txt_results.tag_configure("meta",    foreground=C["text_meta"])
        self.txt_results.tag_configure("sep",     foreground=C["border"])
        self.txt_results.configure(state="disabled")

        # Welcome message
        self._welcome()

    def _welcome(self):
        lines = [
            ("═" * 60 + "\n",                          "sep"),
            ("  NetScan  —  Network Port Scanner\n", "meta"),
            ("  Type a target and press Start Scan (or ↵)\n", "info"),
            ("═" * 60 + "\n",                          "sep"),
        ]
        self.txt_results.configure(state="normal")
        for text, tag in lines:
            self.txt_results.insert(tk.END, text, tag)
        self.txt_results.configure(state="disabled")

    # ---- Card helper ----
    def _card(self, parent, title="", pady_inner=(10, 8)):
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        outer.pack(fill="x" if "Console" not in title else "both",
                   expand="Console" in title,
                   padx=14, pady=(8, 0))

        inner = tk.Frame(outer, bg=C["surface"])
        inner.pack(fill="both", expand=True)

        if title:
            hdr = tk.Frame(inner, bg=C["surface2"], pady=5)
            hdr.pack(fill="x")
            tk.Label(hdr, text=f"  {title}", font=FONT_BOLD,
                     bg=C["surface2"], fg=C["text"]).pack(anchor="w", padx=6)
            tk.Frame(inner, bg=C["border"], height=1).pack(fill="x")

        content = tk.Frame(inner, bg=C["surface"],
                            padx=14, pady=pady_inner[0])
        content.pack(fill="both", expand=True)
        return content

    # ================================================
    # Event Handlers
    # ================================================
    def on_profile_selected(self, _event=None):
        profile = self.var_profile.get()
        if profile not in self.profiles:
            return
        start_port, end_port = self.profiles[profile]
        self.ent_start.delete(0, tk.END)
        self.ent_start.insert(0, str(start_port))
        self.ent_end.delete(0, tk.END)
        self.ent_end.insert(0, str(end_port))

    def start_scan(self):
        if self.scanner_thread and self.scanner_thread.is_alive():
            messagebox.showinfo("Scanner", "A scan is already running.")
            return

        target = self.ent_target.get().strip()
        if not target:
            messagebox.showerror("Input Error", "Please enter a target IP or hostname.")
            return

        try:
            start_port = int(self.ent_start.get().strip())
            end_port   = int(self.ent_end.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Ports must be integers.")
            return

        if not (0 <= start_port <= 65535 and 0 <= end_port <= 65535 and start_port <= end_port):
            messagebox.showerror("Input Error", "Port range must be within 0–65535 and start ≤ end.")
            return

        timeout     = 0.5
        max_threads = 500

        self.scanner = PortScanner(target, start_port, end_port,
                                    timeout=timeout, max_workers=max_threads)
        self.error_lines_shown = 0
        self.var_open_count.set(0)
        self.var_error_count.set(0)
        self.var_rate.set("0.0 p/s")
        self.progress_bar.reset()

        try:
            resolved_ip = self.scanner.resolve_target()
            self.append_text("\n" + "═" * 60 + "\n", "sep")
            self.append_text(f"  Target : {target}  ({resolved_ip})\n", "meta")
            self.append_text(f"  Range  : {start_port} – {end_port}"
                             f"  │  Workers: {max_threads}  │  Timeout: {timeout}s\n", "meta")
            self.append_text("═" * 60 + "\n\n", "sep")
        except Exception as e:
            messagebox.showerror("Resolution Error",
                                  f"Failed to resolve '{target}'.\n{e}")
            self.scanner = None
            return

        self.btn_start.configure_state("disabled")
        self.btn_stop.configure_state("normal")
        self.btn_stop.config(cursor="hand2")
        self.btn_save.configure_state("disabled")

        self.start_time = time.time()
        self.status_badge.set("Scanning...")
        self.update_elapsed()

        self.scanner_thread = threading.Thread(target=self.scanner.run, daemon=True)
        self.scanner_thread.start()
        self.after(self.poll_after_ms, self.poll_results)

    def stop_scan(self):
        if self.scanner:
            self.scanner.stop()
            self.status_badge.set("Stopping...")

    def clear_results(self):
        self.txt_results.configure(state="normal")
        self.txt_results.delete("1.0", tk.END)
        self.txt_results.configure(state="disabled")
        self.progress_bar.reset()
        self.status_badge.set("Idle")
        self.var_elapsed.set("0.00s")
        self.var_open_count.set(0)
        self.var_error_count.set(0)
        self.var_rate.set("0.0 p/s")
        self.btn_save.configure_state("disabled")
        self._welcome()

    def save_results(self):
        if not self.scanner or not self.scanner.open_ports:
            messagebox.showinfo("Save Results", "No open ports to save.")
            return

        default_name = f"open_ports_{int(time.time())}.txt"
        file_path = filedialog.asksaveasfilename(
            title="Save results",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"NetScan Pro — Scan Results\n")
                f.write(f"Target : {self.ent_target.get().strip()}\n")
                f.write(f"Date   : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 40 + "\n\n")
                f.write("Open Ports:\n")
                for port, service in sorted(self.scanner.open_ports, key=lambda x: x[0]):
                    f.write(f"  Port {port:>5}  ({service})\n")
                f.write(f"\nTotal open: {len(self.scanner.open_ports)}\n")
                f.write(f"Errors    : {self.scanner.error_count}\n")
            messagebox.showinfo("Saved", f"Results saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file.\n{e}")

    # ================================================
    # UI Helpers
    # ================================================
    def append_text(self, text, level="info"):
        self.txt_results.configure(state="normal")
        self.txt_results.insert(tk.END, text, level)
        self.txt_results.see(tk.END)
        self.txt_results.configure(state="disabled")

    def update_elapsed(self):
        if self.start_time and self.status_badge._lbl["text"].strip().lower() in (
                "scanning...", "stopping...", "scanning", "stopping"):
            elapsed = time.time() - self.start_time
            self.var_elapsed.set(f"{elapsed:.2f}s")
            if self.scanner and elapsed > 0:
                rate = self.scanner.scanned_count / elapsed
                self.var_rate.set(f"{rate:.1f} p/s")
            self.after(200, self.update_elapsed)

    def poll_results(self):
        if not self.scanner:
            return

        try:
            while True:
                msg_type, a, b = self.scanner.result_queue.get_nowait()

                if msg_type == 'open':
                    port, service = a, b
                    self.append_text(
                        f"  [+]  Port {port:<6}  {service}\n", "success")
                    self.var_open_count.set(len(self.scanner.open_ports))

                elif msg_type == 'progress':
                    scanned, total = a, b
                    self.progress_bar.set(scanned, total)
                    self.status_badge.set(f"Scanning... {scanned}/{total}")

                elif msg_type == 'error':
                    port, error_text = a, b
                    self.var_error_count.set(self.scanner.error_count)
                    if self.error_lines_shown < self.max_error_lines:
                        self.append_text(
                            f"  [!]  Port {port}: {error_text}\n", "error")
                        self.error_lines_shown += 1

                elif msg_type == 'done':
                    total_open = len(self.scanner.open_ports)
                    was_stopped = (self.scanner._stop_event.is_set()
                                   and self.scanner.scanned_count < self.scanner.total_ports)

                    self.append_text("\n" + "═" * 60 + "\n", "sep")
                    if was_stopped:
                        self.append_text("  Scan stopped by user.\n", "warn")
                        self.status_badge.set("Stopped")
                    else:
                        self.append_text("  Scan complete.\n", "meta")
                        self.status_badge.set("Completed")

                    self.append_text(f"  Open ports  : {total_open}\n", "meta")
                    self.append_text(f"  Errors      : {self.scanner.error_count}\n", "meta")
                    elapsed = (time.time() - self.start_time) if self.start_time else 0
                    self.append_text(f"  Elapsed     : {elapsed:.2f}s\n", "meta")
                    self.append_text("═" * 60 + "\n", "sep")

                    self.var_open_count.set(total_open)
                    self.var_error_count.set(self.scanner.error_count)

                    if self.scanner.error_count > self.max_error_lines:
                        hidden = self.scanner.error_count - self.max_error_lines
                        self.append_text(
                            f"  … {hidden} additional errors not shown.\n", "warn")

                    self.btn_start.configure_state("normal")
                    self.btn_start.config(cursor="hand2")
                    self.btn_stop.configure_state("disabled")
                    self.btn_save.configure_state(
                        "normal" if total_open else "disabled")
                    if total_open:
                        self.btn_save.config(cursor="hand2")
                    self.start_time = None
                    return

        except queue.Empty:
            pass

        if self.scanner_thread and self.scanner_thread.is_alive():
            self.after(self.poll_after_ms, self.poll_results)
        else:
            badge_text = self.status_badge._lbl["text"].strip().lower()
            if "scanning" in badge_text or "stopping" in badge_text:
                was_stopped = (self.scanner and self.scanner._stop_event.is_set()
                               and self.scanner.scanned_count < self.scanner.total_ports)
                self.status_badge.set("Stopped" if was_stopped else "Completed")
            self.btn_start.configure_state("normal")
            self.btn_start.config(cursor="hand2")
            self.btn_stop.configure_state("disabled")
            if self.scanner and self.scanner.open_ports:
                self.btn_save.configure_state("normal")
                self.btn_save.config(cursor="hand2")


# ---------------------------
# Entry Point
# ---------------------------
def main():
    if sys.platform.startswith("win"):
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 7)
        except Exception:
            pass

    app = ScannerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
