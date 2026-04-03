<h1 align="center">NetScan NMAP_GUI</h1>
<p align="center">A fast TCP port scanner with a modern dark-themed GUI built with Python & Tkinter</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" />
</p>

---

## ⚡ Quick Start

```bash
git clone https://github.com/mohanraj9342/NetScan-NMAP_GUI.git
cd NetScan-NMAP_GUI
python portscanergui.py
```

> **Requires:** Python 3.7+ · Tkinter (built-in on most systems)
> On Debian/Ubuntu: `sudo apt install python3-tk`

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎨 **Dark UI** | GitHub-style dark theme with surface cards and accent colours |
| ⚙️ **Profile Presets** | One-click ranges: Custom, Top 100, Top 1000, Common Web, Full Scan |
| ⚡ **Fast Scanning** | Up to 500 concurrent threads with a fixed worker-pool |
| 🏷️ **Service Labels** | Auto-identifies FTP, SSH, HTTP, HTTPS, MySQL, RDP, VNC & more |
| 📊 **Live Progress** | Animated bar with %, scan rate (ports/sec), and elapsed time |
| 🔴 **Status Badge** | Colour-coded pill: grey = Idle · blue = Scanning · green = Done · amber = Stopped |
| 💾 **Save Results** | Export open ports to `.txt` with target, timestamp & totals |
| ⌨️ **Keyboard Shortcuts** | `Enter` start · `Esc` stop · `Ctrl+S` save |

---

## 🖥️ How to Use

1. **Enter a target** — IP address (`192.168.1.1`) or hostname (`scanme.nmap.org`)
2. **Pick a profile** from the dropdown, or type a custom port range
3. Press **▶ Start Scan** or hit `Enter`
4. Watch open ports appear live in the Scan Console
5. Press **■ Stop** or `Esc` to cancel at any time
6. Click **💾 Save Results** or `Ctrl+S` to export when done

---

## 🔍 Detected Services

<details>
<summary>Click to expand port → service map</summary>

| Port | Service  | Port | Service  |
|------|----------|------|----------|
| 21   | FTP      | 143  | IMAP     |
| 22   | SSH      | 443  | HTTPS    |
| 23   | Telnet   | 3306 | MySQL    |
| 25   | SMTP     | 3389 | RDP      |
| 53   | DNS      | 5900 | VNC      |
| 80   | HTTP     | 8080 | HTTP-Alt |
| 110  | POP3     |      |          |

> Ports not in this list are reported as `Unknown`

</details>

---

## 🗂️ Project Structure

```
NetScan-NMAP_GUI/
├── portscanergui.py   ← Main app (scanner + GUI)
└── README.md
```

---

## 🗺️ Roadmap

- [x] Scan profile presets (Top 100, Top 1000, Common Web, Full Scan)
- [x] Modern dark-themed GUI with animated progress bar
- [x] Live status badge, stat counters & keyboard shortcuts
- [x] Python 3.14 compatibility fix
- [ ] Export results as CSV / JSON
- [ ] Banner grabbing for deeper service fingerprinting
- [ ] **🤖 AI API Integration** *(Coming Soon)* — Integrate Google Gemini / OpenAI to auto-generate a full security report from scan results, highlighting risks and remediation steps

---

## 📋 Changelog

<details>
<summary><strong>v2.0 — GUI Overhaul (Latest)</strong></summary>

- Rebranded to **NetScan Pro** with radar icon and keyboard-shortcut hints in header
- Full dark theme (`#0d1117` base) with card panels and consistent colour palette
- Custom `DarkButton` with hover & press colour transitions
- `AnimatedProgressBar` with live percentage label
- `StatusBadge` colour-coded pill for scan state
- Live stats row: Open Ports · Errors · Elapsed · Scan Rate
- Improved Scan Console with welcome message and scan separators
- Richer `.txt` exports (target, date, totals)
- Added **Full Scan** profile (ports 1–65535)
- Fixed `_tkinter.TclError` crash on **Python 3.14**

</details>

---

## ⚠️ Disclaimer

> Use this tool **only** on hosts and networks you own or have explicit permission to scan.
> Unauthorized port scanning may be illegal in your jurisdiction.

---

## 📄 License

Released under the [MIT License](https://opensource.org/licenses/MIT).
