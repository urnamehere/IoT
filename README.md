# IoT Security Research Learning Tool

A comprehensive, interactive learning platform for IoT security — from absolute beginner to advanced researcher. Learn with hands-on labs, real hardware guides, open-source software tools, and CTF-style challenges.

## What This Is

This is a locally-hosted web application that guides you through a structured IoT security curriculum. Whether you've never touched a microcontroller or you're an experienced pentester looking to specialize in IoT, this tool meets you where you are.

## Features

- **Structured Curriculum** — 8 modules from "What is IoT?" to advanced firmware exploitation
- **Hands-On Labs** — Practical exercises you run locally with real tools
- **Hardware Guides** — What to buy, how to connect it, what each tool does
- **Software Toolkit** — Curated open-source tools with setup guides and usage walkthroughs
- **CTF Challenges** — Progressive capture-the-flag challenges to test your skills
- **Progress Tracking** — Track your completion across modules, labs, and challenges

## Quick Start

```bash
# Clone the repository
git clone https://github.com/urnamehere/iot.git
cd iot

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python scripts/init_db.py

# Run the application
python run.py
```

Then open your browser to `http://localhost:5000`.

## Curriculum Overview

| # | Module | Level | Topics |
|---|--------|-------|--------|
| 1 | IoT Fundamentals | Beginner | What is IoT, architectures, common protocols |
| 2 | Networking Basics for IoT | Beginner | TCP/IP, WiFi, BLE, Zigbee, MQTT, CoAP |
| 3 | Setting Up Your Lab | Beginner | Hardware purchases, software installation, lab environment |
| 4 | Reconnaissance & Scanning | Intermediate | Shodan, Nmap, network mapping, device fingerprinting |
| 5 | Firmware Analysis | Intermediate | Extraction, reverse engineering, finding secrets |
| 6 | Hardware Hacking | Intermediate | UART, JTAG, SPI, I2C, logic analyzers, soldering |
| 7 | Radio & Wireless Attacks | Advanced | SDR, replay attacks, BLE sniffing, Zigbee exploitation |
| 8 | Exploitation & Reporting | Advanced | Vulnerability chaining, CVE writing, responsible disclosure |

## Hardware You'll Need

The curriculum is designed so you can start with **zero hardware** and progressively invest as you advance. See Module 3 for detailed buying guides at three budget tiers:

- **Free Tier** — Software-only labs, emulators, and virtual devices
- **Starter Kit (~$50-100)** — USB-UART adapter, basic multimeter, Raspberry Pi
- **Full Lab (~$200-400)** — Logic analyzer, SDR dongle, BLE sniffer, soldering station

## Software Tools Covered

- **Nmap** — Network scanning and device discovery
- **Wireshark** — Packet capture and protocol analysis
- **Binwalk** — Firmware extraction and analysis
- **Ghidra** — Reverse engineering (NSA's open-source tool)
- **Firmwalker** — Firmware filesystem analysis
- **EMBA** — Firmware security analysis framework
- **GNURadio** — Software-defined radio processing
- **Bettercap** — Network attack and monitoring
- **Shodan** — Internet-connected device search engine
- **MQTT Explorer** — MQTT protocol testing

## Project Structure

```
IoT/
├── app/                          # Flask web application
│   ├── __init__.py               # App factory
│   ├── models.py                 # Database models (progress tracking)
│   ├── routes.py                 # Route handlers
│   ├── static/                   # CSS, JS, images
│   └── templates/                # Jinja2 HTML templates
├── content/                      # All learning content (Markdown + YAML)
│   ├── modules/                  # Curriculum modules
│   ├── labs/                     # Hands-on lab exercises
│   ├── challenges/               # CTF-style challenges
│   ├── hardware/                 # Hardware tool guides
│   └── software/                 # Software tool guides
├── scripts/                      # Utility scripts
│   └── init_db.py                # Database initialization
├── tests/                        # Test suite
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
└── config.py                     # Application configuration
```

## Contributing

Contributions are welcome! See the MIT License for terms. Areas where help is especially appreciated:

- New lab exercises and CTF challenges
- Hardware tool reviews and guides
- Translations
- Bug fixes and UI improvements

## Disclaimer

This tool is for **authorized security research and education only**. Always obtain proper authorization before testing devices you do not own. The authors are not responsible for misuse of any techniques or tools described herein.

## License

MIT License - see [LICENSE](LICENSE) for details.
