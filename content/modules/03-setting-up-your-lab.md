---
title: "Setting Up Your Lab"
order: 3
level: Beginner
description: "Build your IoT security testing environment at any budget"
estimated_time: "90 minutes"
prerequisites:
  - "Module 1: IoT Fundamentals"
---

## Overview

Before you can test IoT security, you need a lab. The good news: you can start with zero hardware investment and build up as your skills grow.

This module covers three budget tiers, software setup, and how to create a safe practice environment.

> **Important**: Only test devices you own or have explicit written authorization to test. Unauthorized testing of IoT devices is illegal in most jurisdictions.

## Budget Tier 1: Free (Software Only)

You can learn a surprising amount with just software. Here's your free starter kit:

### Operating System

**Kali Linux** is the standard for security testing. Options for running it:

```bash
# Option A: Virtual Machine (recommended for beginners)
# Download from kali.org and run in VirtualBox or VMware

# Option B: Docker (lightweight, good for tools)
docker pull kalilinux/kali-rolling
docker run -it kalilinux/kali-rolling /bin/bash

# Option C: WSL2 on Windows
wsl --install -d kali-linux
```

### Essential Software Tools

Install these tools (most come pre-installed on Kali):

```bash
# Network analysis
sudo apt install nmap wireshark tshark

# MQTT tools
sudo apt install mosquitto mosquitto-clients
pip install mqtt-explorer

# Firmware analysis
sudo apt install binwalk firmware-mod-kit
pip install firmwalker

# General utilities
sudo apt install curl jq python3-pip
```

### Practice Targets (No Hardware Needed)

- **Mosquitto broker**: Run locally to practice MQTT attacks
- **Damn Vulnerable Router Firmware (DVRF)**: Practice firmware analysis
- **IoTGoat**: OWASP's deliberately vulnerable IoT firmware
- **EMUX (formerly ARM-X)**: Emulates IoT device firmware for testing

```bash
# Set up a local vulnerable MQTT broker
# mosquitto.conf with no authentication
echo "allow_anonymous true" > /tmp/mosquitto.conf
echo "listener 1883" >> /tmp/mosquitto.conf
mosquitto -c /tmp/mosquitto.conf
```

## Budget Tier 2: Starter Kit ($50-100)

Ready for hardware? Here's your first shopping list:

### Essential Hardware

| Item | Price | Purpose |
|------|-------|---------|
| USB-UART adapter (CP2102 or FT232RL) | $5-8 | Serial console access |
| Basic digital multimeter | $15-25 | Pin identification, voltage checks |
| Raspberry Pi (any model) | $15-35 | Target device, network tools |
| Breadboard + jumper wires | $5-10 | Making connections |
| MicroSD card (32GB) | $5-8 | For Raspberry Pi |

**Total: ~$45-85**

### Setting Up Your Raspberry Pi as a Target

```bash
# 1. Flash Raspberry Pi OS Lite to your SD card
# 2. Enable SSH on first boot
touch /boot/ssh

# 3. Install vulnerable services for practice
sudo apt update
sudo apt install mosquitto telnetd vsftpd

# 4. Configure Mosquitto without authentication
sudo nano /etc/mosquitto/mosquitto.conf
# Add: allow_anonymous true

# 5. Enable telnet (intentionally insecure for practice)
sudo systemctl enable telnetd
```

### Your First Hardware Exercise

Connect your USB-UART adapter to the Raspberry Pi's GPIO UART pins:

```
USB-UART Adapter     Raspberry Pi
────────────         ──────────────
TX  ──────────────── RX (GPIO 15, Pin 10)
RX  ──────────────── TX (GPIO 14, Pin 8)
GND ──────────────── GND (Pin 6)
```

```bash
# Connect via serial console (Linux/Mac)
screen /dev/ttyUSB0 115200

# Or using minicom
minicom -D /dev/ttyUSB0 -b 115200
```

## Budget Tier 3: Full Lab ($200-400)

For serious IoT security research:

### Advanced Hardware

| Item | Price | Purpose |
|------|-------|---------|
| Everything from Tier 2 | ~$75 | Base kit |
| Saleae Logic 8 (or clone) | $10-150 | Protocol decoding (SPI, I2C, UART) |
| RTL-SDR dongle + antenna | $25-35 | Software-defined radio |
| Soldering iron kit | $25-40 | Component access, modifications |
| Bus Pirate or similar | $30-40 | Bus interaction tool |
| nRF52840 dongle | $10-15 | BLE sniffing |
| Old IoT devices (thrift store) | $10-30 | Real targets to practice on |

**Total: ~$185-385**

### Where to Find Practice Devices

- **Thrift stores**: Old routers, IP cameras, smart plugs
- **Estate sales / garage sales**: Smart home devices
- **eBay "for parts"**: Broken IoT devices (you only need the PCB)
- **Recycling centers**: Discarded electronics

> **Tip**: Even a "broken" IoT device is perfect for hardware hacking practice. You're after the PCB, not a working product.

## Setting Up Your Lab Network

Create an isolated network for testing:

```
┌─────────────────────────────────────────────┐
│              Your Main Network               │
│         (keep this separate!)                │
└──────────────────┬──────────────────────────┘
                   │
            ┌──────┴──────┐
            │  Lab Router  │  (old router, dedicated)
            └──────┬──────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───┴───┐   ┌─────┴────┐  ┌─────┴────┐
│ Kali  │   │ Target   │  │ Target   │
│ Linux │   │ Device 1 │  │ Device 2 │
└───────┘   └──────────┘  └──────────┘
```

### Quick Lab Network Setup

```bash
# Option 1: Use a dedicated old router
# - Connect Kali and target devices to this router
# - Don't connect it to your main network/internet

# Option 2: Create a virtual network
# Using VirtualBox internal network:
# 1. Set Kali VM to "Internal Network" (name: iotlab)
# 2. Set target VMs to same "Internal Network"

# Option 3: USB WiFi adapter as access point
sudo apt install hostapd dnsmasq
# Configure as an access point for IoT devices to connect to
```

## Docker-Based Lab Environment

For a portable, reproducible lab:

```bash
# Create a docker-compose.yml for your IoT lab
mkdir ~/iot-lab && cd ~/iot-lab
```

```yaml
# docker-compose.yml
version: '3'
services:
  mqtt-broker:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf

  mqtt-explorer:
    image: smeagolworms4/mqtt-explorer
    ports:
      - "4000:4000"

  vulnerable-web:
    image: vulnerables/web-dvwa
    ports:
      - "8080:80"
```

```bash
# Start the lab
docker-compose up -d

# Verify services
nmap -sV localhost -p 1883,4000,8080
```

## Safety Checklist

Before you start testing, verify:

- [ ] You own the device or have written authorization
- [ ] Your lab network is isolated from your main network
- [ ] You have backups of any device firmware before modifying
- [ ] You understand the legal framework in your jurisdiction
- [ ] You're not testing on devices connected to critical infrastructure
- [ ] Your testing tools are up to date

## Organizing Your Research

Create a standard directory structure for your research:

```bash
mkdir -p ~/iot-research/{targets,firmware,captures,notes,tools}

# For each target device:
mkdir -p ~/iot-research/targets/device-name/{
  firmware,photos,serial-logs,network-captures,findings
}
```

Keep detailed notes. A finding you can't reproduce or explain is worthless. Document:
- Device make, model, firmware version
- Every step you took
- Screenshots and terminal output
- Network captures (.pcap files)

## Key Takeaways

- You can start learning IoT security for free using software tools and emulators
- A $50-100 starter kit adds real hardware interaction
- A $200-400 full lab covers nearly all IoT security research scenarios
- Lab isolation is critical — never test on your production network
- Documentation is as important as the testing itself

## Next Steps

With your lab set up, proceed to [Module 4: Reconnaissance & Scanning](/modules/04-recon-and-scanning) to start finding and fingerprinting IoT devices.
