---
title: "Lab: IoT Device Discovery"
level: Beginner
description: "Find and fingerprint IoT devices on your network"
estimated_time: "30 minutes"
tools:
  - Nmap
  - Wireshark
objectives:
  - Scan a network for IoT devices
  - Identify device types from service banners
  - Map the network topology
---

# Lab: IoT Device Discovery

## Overview

In this lab you will learn how to systematically discover IoT devices on a local network using Nmap and Wireshark. By the end you will be able to identify device types, enumerate open services, and understand the attack surface that IoT devices expose.

## Prerequisites

- A Linux machine (Kali Linux recommended) or a VM with network access
- Nmap installed (`sudo apt install nmap`)
- Wireshark installed (`sudo apt install wireshark`)
- A lab network with IoT devices (real or emulated)

> **Legal Notice:** Only scan networks you own or have explicit written permission to test. Unauthorized scanning is illegal in most jurisdictions.

## Common IoT Ports Reference

Before you begin, familiarize yourself with the ports that IoT devices typically expose:

| Port | Protocol | Service | Notes |
|------|----------|---------|-------|
| 80 / 8080 | TCP | HTTP | Web management interfaces |
| 443 / 8443 | TCP | HTTPS | Encrypted web interfaces |
| 1883 | TCP | MQTT | Unencrypted message broker |
| 8883 | TCP | MQTTS | TLS-encrypted MQTT |
| 5683 | UDP | CoAP | Constrained Application Protocol |
| 22 | TCP | SSH | Secure Shell (often with default credentials) |
| 23 | TCP | Telnet | Unencrypted remote access (high risk) |
| 554 | TCP | RTSP | Real Time Streaming Protocol (IP cameras) |
| 5353 | UDP | mDNS | Multicast DNS / device discovery |
| 1900 | UDP | SSDP/UPnP | Universal Plug and Play |

---

## Step 1: Identify Your Network Range

Before scanning, determine your own IP address and the subnet you are on.

```bash
ip addr show
```

Look for the interface connected to your lab network (commonly `eth0` or `wlan0`). Note the IP address and subnet mask. For example, if your IP is `192.168.1.50/24`, your network range is `192.168.1.0/24`.

Alternatively, use:

```bash
ip route | grep default
```

This shows the default gateway, which confirms the subnet.

---

## Step 2: Host Discovery with Nmap

Start with a ping sweep to find live hosts on the network. This is fast and non-intrusive.

```bash
sudo nmap -sn 192.168.1.0/24 -oN discovery_ping.txt
```

**Flags explained:**
- `-sn` -- Ping scan only, no port scanning
- `-oN discovery_ping.txt` -- Save output in normal format

**Expected output:**

```
Nmap scan report for 192.168.1.1
Host is up (0.0025s latency).
MAC Address: AA:BB:CC:DD:EE:01 (Netgear)

Nmap scan report for 192.168.1.15
Host is up (0.015s latency).
MAC Address: AA:BB:CC:DD:EE:02 (Espressif)

Nmap scan report for 192.168.1.22
Host is up (0.008s latency).
MAC Address: AA:BB:CC:DD:EE:03 (Raspberry Pi Trading)
```

**What to look for:**
- MAC address vendor prefixes reveal device manufacturers. Espressif (ESP8266/ESP32), Raspberry Pi, and similar entries strongly suggest IoT devices.
- Note every live host for the next step.

---

## Step 3: Port Scanning IoT Targets

Now scan the discovered hosts for open ports. Target the common IoT ports listed above.

### Quick targeted scan

```bash
sudo nmap -sS -p 22,23,80,443,554,1883,5683,8080,8443,8883 192.168.1.0/24 -oN discovery_ports.txt
```

**Flags explained:**
- `-sS` -- TCP SYN scan (fast, stealthy)
- `-p` -- Specific ports to check

### Comprehensive scan of a single target

Once you identify a likely IoT device, run a deeper scan:

```bash
sudo nmap -sS -sV -O -p- 192.168.1.15 -oN target_full.txt
```

**Flags explained:**
- `-sV` -- Probe open ports to determine service and version info
- `-O` -- Enable OS detection
- `-p-` -- Scan all 65535 TCP ports

**Expected output:**

```
PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           Dropbear sshd 2019.78
80/tcp   open  http          lighttpd 1.4.55
1883/tcp open  mqtt          Mosquitto 1.6.9
8080/tcp open  http-proxy    Node.js Express framework
```

### UDP scan for CoAP and mDNS

IoT devices often use UDP-based protocols. These are missed by default TCP scans.

```bash
sudo nmap -sU -p 5353,5683,1900 192.168.1.0/24 -oN discovery_udp.txt
```

**Flags explained:**
- `-sU` -- UDP scan (slower than TCP scans, be patient)

---

## Step 4: Service Banner Grabbing

Nmap's version detection (`-sV`) grabs banners automatically, but you can also do manual banner grabbing for more control.

### Grab an MQTT broker banner

```bash
nmap -sV -p 1883 --script mqtt-subscribe 192.168.1.15
```

### Grab an HTTP banner

```bash
curl -s -I http://192.168.1.15:8080
```

Look for headers like `Server:`, `X-Powered-By:`, and response body content that reveals the device type or firmware version.

### Grab a Telnet banner

```bash
nmap -sV -p 23 --script banner 192.168.1.15
```

Many IoT devices announce their model and firmware version in the Telnet login banner.

---

## Step 5: Capture Traffic with Wireshark

Now switch to passive observation. Launch Wireshark and start capturing on the interface connected to your lab network.

```bash
sudo wireshark &
```

1. Select your network interface (e.g., `eth0`).
2. Click the blue shark fin to start capturing.

### Filter for IoT-specific traffic

Use these display filters in Wireshark:

| Filter | Purpose |
|--------|---------|
| `mqtt` | Show all MQTT traffic |
| `coap` | Show all CoAP traffic |
| `tcp.port == 1883` | MQTT on default port |
| `udp.port == 5683` | CoAP on default port |
| `mdns` | Multicast DNS device announcements |
| `ssdp` | UPnP / SSDP discovery |
| `http.request` | All HTTP requests |

### Observe mDNS announcements

Many IoT devices announce themselves via mDNS. Filter for `mdns` and look for service names like `_mqtt._tcp`, `_http._tcp`, or `_coap._udp`.

### Observe SSDP/UPnP traffic

Filter for `ssdp` to see devices advertising their presence via Universal Plug and Play.

**What to look for:**
- Device names and models in advertisement payloads
- Unencrypted data being transmitted (credentials, sensor readings)
- Broadcast or multicast traffic that reveals network topology

---

## Step 6: Map the Network Topology

Combine your findings to build a network map.

### Use Nmap's XML output for visualization

```bash
sudo nmap -sS -sV -O 192.168.1.0/24 -oX network_map.xml
```

You can import this XML file into tools like Zenmap (Nmap's GUI) or use `xsltproc` to generate an HTML report:

```bash
xsltproc network_map.xml -o network_report.html
```

### Build a manual device inventory

Create a table with your findings:

| IP Address | MAC Vendor | Open Ports | Services | Device Type (Guess) |
|------------|-----------|------------|----------|-------------------|
| 192.168.1.1 | Netgear | 80, 443 | HTTP, HTTPS | Router |
| 192.168.1.15 | Espressif | 80, 1883 | HTTP, MQTT | ESP32 Sensor |
| 192.168.1.22 | Raspberry Pi | 22, 8080 | SSH, HTTP | IoT Gateway |

---

## Step 7: Identify Security Concerns

Review your scan results and note any of the following red flags:

- **Telnet open (port 23):** Credentials are transmitted in cleartext.
- **MQTT without TLS (port 1883 vs 8883):** All messages are unencrypted.
- **Default HTTP interfaces (port 80/8080):** Often have default or weak credentials.
- **UPnP enabled:** Can be abused for port forwarding or information leakage.
- **Old software versions:** Check identified versions against CVE databases.

---

## Review Questions

1. Why is a UDP scan important when discovering IoT devices? What protocols would you miss with TCP-only scanning?
2. How can MAC address vendor prefixes help you distinguish IoT devices from laptops and phones?
3. What is the security risk of an MQTT broker listening on port 1883 with no authentication?
4. Why might an IoT device not respond to ICMP ping but still have open TCP/UDP ports?

---

## Cleanup

Remove scan output files if you no longer need them:

```bash
rm -f discovery_ping.txt discovery_ports.txt target_full.txt discovery_udp.txt network_map.xml network_report.html
```

## Next Steps

- Proceed to **Lab: IoT Protocol Analysis** to inspect the traffic from the devices you discovered.
- Try running Nmap scripts specific to IoT protocols: `nmap --script mqtt-subscribe`, `nmap --script coap-resources`.
