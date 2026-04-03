# NetScan Pro — Network Port Scanner GUI

A fast TCP port scanner with a modern dark-themed graphical user interface built with Python and Tkinter.

## What's New (Latest Update)

### GUI Overhaul — NetScan Pro
The application has been fully redesigned with a professional dark theme inspired by modern developer tooling. Key visual and functional improvements include:

- **Rebranded as *NetScan Pro*** with a branded header, radar/target icon, and keyboard-shortcut hints
- **Full dark theme** — custom `#0d1117` deep background, surface cards, and a consistent colour palette throughout
- **Custom animated buttons** — `Start Scan`, `Stop`, `Clear`, and `Save Results` buttons with hover and press colour transitions
- **Live animated progress bar** — custom-drawn bar showing a real-time percentage label (`0%` → `100%`)
- **Status badge** — colour-coded pill that changes dynamically: grey = Idle, blue = Scanning, green = Completed, amber = Stopped/Stopping
- **Live stats row** — Open Ports, Errors, Elapsed Time, and Scan Rate displayed as live-updating stat blocks with icons
- **Improved Scan Console** — welcome message on launch, separator lines between scans, bold open-port rows, better visual hierarchy
- **Richer saved reports** — saved `.txt` files now include target host, scan date/time, and summary totals
- **New scan profile** — added *Full Scan* (ports 1–65535) to the profile presets dropdown
- **Python 3.14 compatibility fix** — replaced the `tk.Canvas`-based button implementation with a `tk.Frame + tk.Label` approach to resolve a ``_tkinter.TclError`` that occurred on Python 3.14 when canvas drawing commands were called before widget placement

---

## Features

- **Modern dark UI** – professional GitHub-style dark theme with surface cards, borders, and accent colours
- **Profile presets** – instantly set port ranges with: Custom, Top 100, Top 1000, Common Web, Full Scan
- **Fixed worker-pool scanning** – efficient concurrent scanning (up to 500 threads) without creating one thread per port
- **Service identification** – automatically labels well-known ports (FTP, SSH, HTTP, HTTPS, MySQL, RDP, VNC, etc.)
- **Real-time progress** – animated progress bar with percentage, elapsed-time counter, and scan-rate (ports/sec) update live
- **Status badge** – colour-coded pill reflects the current scan state at a glance
- **Stop at any time** – cancel a running scan gracefully with the Stop button or `Esc`
- **Runtime error visibility** – scan errors shown in the console with a final hidden-error count
- **Save results** – export discovered open ports to a `.txt` file with target, timestamp, and totals
- **Keyboard shortcuts** – `Enter` to start, `Ctrl+S` to save, `Esc` to stop
- **Cross-platform** – runs on Windows, macOS, and Linux (Python 3.7+)

---

## Requirements

- Python **3.7 or newer** (tested up to Python 3.14)
- Tkinter (included in the standard Python distribution; on Debian/Ubuntu install `python3-tk`)

No third-party packages are required.

---

## Installation

```bash
git clone https://github.com/techtrainer20/nmap_portscan_gui.git
cd nmap_portscan_gui
```

---

## Usage

```bash
python portscanergui.py
```

1. Enter the **Target** — an IP address (e.g. `192.168.1.1`) or hostname (e.g. `scanme.nmap.org`).
2. Choose a **Profile** from the dropdown or manually set **Start Port** and **End Port**.
3. Click **▶ Start Scan** (or press `Enter`). Open ports appear in real time in the Scan Console.
4. Click **■ Stop** (or press `Esc`) to cancel a scan early.
5. After a scan completes, click **💾 Save Results** (or press `Ctrl+S`) to export the open-port list.

---

## Detected Services

The following ports are automatically labelled:

| Port | Service   |
|------|-----------|
| 21   | FTP       |
| 22   | SSH       |
| 23   | Telnet    |
| 25   | SMTP      |
| 53   | DNS       |
| 80   | HTTP      |
| 110  | POP3      |
| 143  | IMAP      |
| 443  | HTTPS     |
| 3306 | MySQL     |
| 3389 | RDP       |
| 5900 | VNC       |
| 8080 | HTTP-Alt  |

Ports not in the list are reported as `Unknown`.

---

## Project Structure

```
nmap_portscan_gui/
├── portscanergui.py   # Main application (scanner + GUI)
├── docs/              # GitHub Pages website folder
│   ├── index.html
│   ├── styles.css
│   └── .nojekyll
└── README.md
```

---

## GitHub Pages Hosting

This project includes a ready-to-host website in the `docs` folder.

1. Push this repository to GitHub.
2. Open your repository on GitHub.
3. Go to **Settings > Pages**.
4. Under **Build and deployment**, choose:
   - **Source**: Deploy from a branch
   - **Branch**: `main` (or your default branch)
   - **Folder**: `/docs`
5. Save the settings and wait for deployment.

After deployment, your project website will be available at:

`https://<your-username>.github.io/<your-repository-name>/`

---

## Roadmap

- [x] Scan profile presets (Top 100, Top 1000, Common Web, Full Scan)
- [x] Modern dark-themed GUI with live animated progress
- [x] Status badge, live stat counters, and keyboard shortcuts
- [x] Python 3.14 compatibility
- [ ] Export results in CSV and JSON formats
- [ ] Optional banner grabbing for deeper service fingerprinting
- [ ] **AI API Integration** *(Coming Soon)* — We plan to integrate a free AI API (e.g. Google Gemini or OpenAI) to automatically analyse scan results and generate a **full human-readable security report**, highlighting open ports, potential vulnerabilities, and recommended remediation steps — all from within the app.

---

## Disclaimer

Use this tool only on hosts and networks you own or have explicit permission to scan. Unauthorized port scanning may be illegal in your jurisdiction.

---

## License

This project is released under the [MIT License](https://opensource.org/licenses/MIT).
