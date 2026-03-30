---
title: "Software-Defined Radio (SDR)"
level: Advanced
description: "Receive and transmit radio signals for wireless security research"
order: 3
---

# Software-Defined Radio (SDR)

## What Is SDR?

Traditional radios use fixed hardware circuits to tune, demodulate, and decode radio signals. A Software-Defined Radio moves most of that processing into software. The hardware is a broadband receiver (and sometimes transmitter) that digitizes raw radio frequency (RF) signals and passes them to your computer, where software handles everything else.

For IoT security research, SDR is essential because a huge number of IoT devices communicate wirelessly using protocols that your standard Wi-Fi adapter or Bluetooth dongle cannot intercept:

- **433 MHz / 868 MHz / 915 MHz:** Garage door openers, weather stations, smart home sensors, alarm systems
- **Sub-GHz proprietary protocols:** Many industrial IoT sensors, smart meters, remote controls
- **Zigbee (2.4 GHz):** Smart home devices (though specialized tools like the Zigbee sniffer from TI are often better)
- **LoRa (various sub-GHz bands):** Long-range IoT sensors
- **Bluetooth Low Energy (2.4 GHz):** Fitness trackers, beacons, medical devices (specialized tools often preferred)
- **Custom RF protocols:** Proprietary wireless links used by many IoT products

## Hardware Options

### RTL-SDR v3/v4 ($25-35) -- Receive Only

The RTL-SDR is built around DVB-T TV tuner chips (RTL2832U + R820T2). Originally intended for watching digital TV in Europe, hackers discovered the chips could be used as general-purpose wideband receivers.

**Specifications:**
- **Frequency range:** 24 MHz - 1.766 GHz (v3), 24 MHz - 1.766 GHz with improved performance (v4)
- **Bandwidth:** Up to 2.4 MHz (stable at ~2 MHz)
- **ADC resolution:** 8-bit
- **Interface:** USB 2.0
- **Transmit:** No -- receive only

**Pros:**
- Incredibly cheap for what it does
- Massive community and documentation
- Covers most sub-GHz IoT bands (433 MHz, 868 MHz, 915 MHz)
- Many software tools support it natively

**Cons:**
- Cannot transmit (cannot replay or inject signals)
- 8-bit ADC limits dynamic range
- 2 MHz bandwidth is narrow for some applications
- Cannot receive below 24 MHz without hardware modification (direct sampling mode extends to ~500 kHz with reduced performance)

**Best for:** Learning SDR fundamentals, passive monitoring of sub-GHz IoT devices, spectrum analysis on a budget.

### HackRF One ($300-350) -- Transmit and Receive

**Specifications:**
- **Frequency range:** 1 MHz - 6 GHz
- **Bandwidth:** Up to 20 MHz
- **ADC/DAC resolution:** 8-bit
- **Interface:** USB 2.0 (High Speed)
- **Transmit:** Yes, half-duplex (cannot TX and RX simultaneously)

**Pros:**
- Transmit capability enables replay attacks, signal injection, and protocol testing
- Very wide frequency range covers almost all IoT bands
- 20 MHz bandwidth captures wider signals
- Open-source hardware and firmware
- Large community, well-documented

**Cons:**
- Half-duplex (cannot receive while transmitting)
- 8-bit ADC same as RTL-SDR
- Transmit power is low (~10 dBm) -- sufficient for short-range testing only
- More expensive than RTL-SDR

**Best for:** Active IoT security testing, replay attacks against rolling-code-free systems, transmitting test signals, wide-spectrum monitoring.

### Other Notable Options

| Device | Price | Key Feature | Notes |
|--------|-------|-------------|-------|
| **YARD Stick One** | $100 | Sub-GHz TX/RX specialist | Optimized for 300-928 MHz, great for garage doors and alarm systems |
| **LimeSDR Mini** | $200 | Full-duplex TX/RX | 10 MHz - 3.5 GHz, 12-bit ADC, better signal quality |
| **Airspy Mini** | $100 | High-quality RX | 24-1700 MHz, 12-bit ADC, better dynamic range than RTL-SDR |
| **PlutoSDR** | $150 | Full-duplex, 12-bit | 325 MHz - 3.8 GHz, good for 2.4 GHz work |
| **BladeRF 2.0** | $480+ | High-performance full-duplex | 47 MHz - 6 GHz, 12-bit, FPGA onboard |

### Recommendation Path

1. **Start with RTL-SDR** ($25) to learn the fundamentals
2. **Add a YARD Stick One** ($100) when you need sub-GHz transmit capability
3. **Get a HackRF One** ($300) when you need wideband transmit across many frequencies

## Antenna Selection

The antenna matters as much as the SDR itself. A poorly matched antenna can reduce your effective range by orders of magnitude.

### Key Concepts

- **Frequency matching:** Antennas are designed for specific frequency ranges. A 433 MHz antenna is nearly useless at 915 MHz.
- **Connector types:** Most SDRs use SMA connectors. RTL-SDR v3 uses SMA, HackRF uses SMA. Ensure your antenna connector matches or use an adapter.
- **Polarization:** Match the antenna polarization to the signal source (vertical, horizontal, or circular).

### Recommended Antennas

| Frequency Range | Antenna Type | Approximate Cost |
|----------------|-------------|-----------------|
| Wideband (general) | Telescopic whip (included with RTL-SDR) | $0 (included) |
| 433 MHz | Quarter-wave whip (17.3 cm) | $5-10 |
| 868/915 MHz | Quarter-wave whip (8-8.6 cm) | $5-10 |
| 433 + 868/915 MHz | Dual-band antenna | $10-15 |
| 1090 MHz (ADS-B) | Tuned 1090 MHz antenna or DIY spider | $10-20 |
| Wideband directional | Log-periodic or discone | $30-60 |

**For IoT security testing,** a set of quarter-wave whip antennas for 433 MHz and 915 MHz plus the stock telescopic antenna covers most scenarios.

## Software Setup

### GNURadio

GNURadio is the flagship open-source SDR framework. It provides a visual flowgraph editor (GNURadio Companion) and a massive library of signal processing blocks.

```bash
# Ubuntu/Debian
sudo apt install gnuradio gnuradio-dev gr-osmosdr

# Fedora
sudo dnf install gnuradio gnuradio-devel gr-osmosdr

# macOS
brew install gnuradio

# Verify installation
gnuradio-companion &
```

GNURadio has a steep learning curve. Start with the built-in tutorials and the official guided tutorials at https://wiki.gnuradio.org/index.php/Tutorials.

### GQRX (Linux/macOS)

GQRX is a simple SDR receiver application built on GNURadio. It provides a spectrum display and waterfall, audio demodulation, and basic recording.

```bash
# Ubuntu/Debian
sudo apt install gqrx-sdr

# macOS
brew install --cask gqrx

# Launch
gqrx
```

**Quick start with GQRX:**
1. Select your device (RTL-SDR, HackRF, etc.)
2. Set the center frequency (e.g., 433.92 MHz for common IoT devices)
3. Click "Play" to start receiving
4. Select a demodulation mode (AM, FM, etc.)
5. Look for signal spikes on the waterfall display when IoT devices transmit

### SDR# (Windows)

SDR# (SDRSharp) is the most popular Windows SDR application.

1. Download from https://airspy.com/download/
2. Extract and run `install-rtlsdr.bat` (for RTL-SDR support)
3. Run `SDRSharp.exe`
4. Select your SDR from the source dropdown
5. Configure the center frequency and sample rate
6. Click "Play"

### Universal Radio Hacker (URH)

URH is specifically designed for reverse-engineering wireless protocols. It combines signal capture, demodulation, protocol analysis, and signal generation in one tool.

```bash
# Install via pip
pip install urh

# Or on Ubuntu
sudo apt install urh

# Launch
urh
```

**URH is excellent for IoT security because it:**
- Automatically detects modulation type (ASK/OOK, FSK, PSK)
- Demodulates signals and shows the raw bits
- Groups bits into messages and identifies fields
- Supports protocol analysis and fuzzing
- Can generate and transmit modified signals (with HackRF)

### rtl_433

Specifically built for decoding data from sensors that transmit on 433.92 MHz (and other ISM bands). Supports hundreds of device types out of the box.

```bash
# Install
sudo apt install rtl-433
# Or build from source: https://github.com/merbanan/rtl_433

# Listen for all known device types
rtl_433

# Listen on a specific frequency
rtl_433 -f 915000000

# Output as JSON (useful for logging and analysis)
rtl_433 -F json

# Save raw signal for later analysis
rtl_433 -S all
```

This tool instantly decodes signals from weather stations, tire pressure monitors, door/window sensors, and many other IoT devices. It is the fastest way to start seeing real IoT data.

## Legal Considerations

**Receiving signals is generally legal in most jurisdictions.** Passive listening with an RTL-SDR is lawful in the US, EU, and most other countries, though there may be restrictions on acting on intercepted communications (e.g., you can receive a pager signal but using the information may be illegal).

**Transmitting is heavily regulated.** Before transmitting any signal:

1. **Know your local regulations.** In the US, the FCC regulates all radio transmissions. In the EU, each country has a national frequency authority.
2. **ISM bands** (433 MHz, 868 MHz, 915 MHz, 2.4 GHz) allow low-power unlicensed transmissions, but with power limits and duty cycle restrictions.
3. **Never transmit on frequencies you are not authorized to use.** Transmitting on aircraft, emergency, or military frequencies is a serious criminal offense.
4. **Use a Faraday cage or shielded enclosure** for testing. A simple metal box with an internal antenna prevents your signals from reaching beyond the enclosure.
5. **Use attenuators** to reduce transmit power for close-range testing.
6. **Get a ham radio license** (easy exam in most countries) for access to amateur bands and a better understanding of RF regulations.
7. **Document your authorization** when testing client devices. Written permission to test wireless security should be part of your engagement scope.

**For IoT security research, the safest approach is:**
- Use receive-only equipment (RTL-SDR) for passive reconnaissance
- Perform transmit testing inside a shielded enclosure
- Get explicit written authorization before testing any device you do not own

## First Exercises

### Exercise 1: Listen to FM Radio

This verifies your setup works and familiarizes you with the software.

```bash
# With GQRX: set frequency to a known FM station (e.g., 101.1 MHz)
# Set mode to WFM (Wideband FM)
# You should hear the radio station

# With command line (rtl_fm):
rtl_fm -f 101.1e6 -M fm -s 200000 -r 48000 - | aplay -r 48000 -f S16_LE
```

### Exercise 2: Receive Weather Station Data

Many wireless weather stations transmit on 433.92 MHz using simple OOK (On-Off Keying) modulation.

```bash
# Use rtl_433 to automatically decode weather station transmissions
rtl_433 -f 433920000

# Example output:
# time: 2026-03-30 14:22:15
# model: Acurite-Tower  id: 2845  channel: A
# temperature_C: 22.300  humidity: 45  battery_ok: 1
```

### Exercise 3: Capture and Analyze a 433 MHz Remote Control Signal

1. Open URH or GQRX, tune to 433.92 MHz
2. Press a button on a cheap 433 MHz remote (garage door learning remote, wireless doorbell, etc.)
3. Observe the signal burst on the waterfall display
4. In URH, record the signal, let it auto-detect the modulation, and examine the bit pattern
5. Press the button multiple times and compare -- does the code change each time (rolling code) or stay the same (fixed code)?

### Exercise 4: Monitor the ISM Band Spectrum

```bash
# Use rtl_power to create a heatmap of activity in the 433 MHz ISM band
rtl_power -f 430M:440M:10k -g 40 -i 10 -e 1h ism_band.csv

# Visualize with heatmap.py (from the rtl-sdr-misc repository)
python3 heatmap.py ism_band.csv ism_band.png
```

This reveals which frequencies in the band are actively being used by devices in your vicinity.

## Using SDR for IoT Security Research

### Reconnaissance: Identify Wireless IoT Devices

Before interacting with a device, identify what frequencies and protocols it uses:

1. **Check FCC filings:** Search the FCC ID (printed on the device label) at https://fccid.io to find test reports that reveal operating frequencies, modulation types, and power levels.
2. **Wideband scanning:** Use `rtl_power` or GQRX to scan a wide band and observe when the device transmits.
3. **Use rtl_433** to check if the device uses a known protocol.

### Replay Attacks

Some IoT devices use fixed codes -- the same signal opens the gate or disarms the sensor every time. To test:

1. Capture the signal with URH or `rtl_433 -S all`
2. Analyze whether the code changes between transmissions
3. If fixed, replay the captured signal using HackRF and `hackrf_transfer`:

```bash
# Record a raw signal
hackrf_transfer -r signal.raw -f 433920000 -s 2000000 -g 40 -l 32

# Replay the signal
hackrf_transfer -t signal.raw -f 433920000 -s 2000000 -x 30
```

**Important:** Only test this on devices you own or have explicit authorization to test. Modern garage doors and security systems use rolling codes that defeat simple replay attacks.

### Protocol Reverse Engineering

For devices using unknown proprietary protocols:

1. Capture multiple transmissions under different conditions (different commands, different data values)
2. Use URH to demodulate and align the bit streams
3. Look for patterns: preamble, sync word, device ID, command bytes, data payload, checksum
4. Modify individual fields and retransmit to observe the device's behavior
5. Document the protocol structure for further analysis

### Jamming Detection and Testing

While jamming itself is illegal, testing whether a security device is vulnerable to jamming (and whether it detects jamming attempts) is part of a thorough security assessment:

- Does the alarm system detect interference on its communication channel?
- Does it fail open (insecure) or fail closed (secure) when communication is disrupted?
- Does it alert the user when jamming is detected?

These tests should be performed in a shielded enclosure and only with explicit authorization.
