---
title: "Reconnaissance & Scanning"
order: 4
level: Intermediate
description: "Finding, fingerprinting, and mapping IoT devices"
estimated_time: "75 minutes"
prerequisites:
  - "Module 2: Networking for IoT"
  - "Module 3: Lab Setup"
related_labs:
  - lab-device-discovery
---

## Reconnaissance Overview

Reconnaissance (recon) is the first phase of any security assessment. For IoT, this means finding devices, identifying what they are, and understanding their attack surface.

There are two types:

- **Passive recon**: Gathering information without directly interacting with the target (OSINT, Shodan, public documentation)
- **Active recon**: Directly scanning and probing devices (Nmap, service enumeration)

## Passive Reconnaissance

### Shodan — The Search Engine for IoT

Shodan indexes internet-connected devices. It's the most powerful passive recon tool for IoT research.

```
# Shodan search examples (shodan.io)

# Find MQTT brokers
port:1883 mqtt

# Find specific device types
"Server: GoAhead-Webs" port:80     # IP cameras
"Server: Boa" port:80               # Embedded web servers
"220 Welcome to" port:21            # FTP on IoT devices

# Filter by country
port:1883 country:US

# Find devices with default pages
http.title:"Router" port:80
http.title:"DVR" port:80
```

### OSINT for IoT Manufacturers

Before testing a device, research the manufacturer:

- **FCC ID database** (fcc.gov/oet/ea/fccid): Search by FCC ID on the device label to find internal photos, schematics, and test reports
- **Manufacturer documentation**: User manuals often reveal default credentials, port numbers, and protocols
- **CVE databases**: Search for known vulnerabilities (cvedetails.com, nvd.nist.gov)
- **GitHub**: Search for manufacturer name — leaked source code, SDKs, and tools
- **Firmware download pages**: Many manufacturers host firmware updates publicly

```bash
# Search for known CVEs related to a device
# Example: Search for vulnerabilities in TP-Link cameras
searchsploit tp-link camera

# Or use the NVD API
curl "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=tp-link+camera"
```

## Active Reconnaissance with Nmap

Nmap is your primary active scanning tool. Here are IoT-specific techniques:

### Basic Device Discovery

```bash
# Ping sweep — find live hosts
nmap -sn 192.168.1.0/24

# Fast port scan of common IoT ports
nmap -F -sV 192.168.1.0/24

# Comprehensive IoT port scan
nmap -sV -p 22,23,80,443,554,1883,5683,8080,8443,8883,49152-49155 192.168.1.0/24
```

### Service Detection and Version Scanning

```bash
# Detailed service version detection
nmap -sV --version-intensity 5 -p- 192.168.1.100

# Example output for an IP camera:
# PORT     STATE SERVICE    VERSION
# 80/tcp   open  http       GoAhead-Webs httpd
# 554/tcp  open  rtsp       HiSilicon IP camera rtspd
# 8080/tcp open  http-proxy Embedded web server
# 23/tcp   open  telnet     BusyBox telnetd
```

### Nmap Scripts for IoT

Nmap's NSE (Nmap Scripting Engine) has IoT-specific scripts:

```bash
# MQTT broker enumeration
nmap -p 1883 --script mqtt-subscribe 192.168.1.100

# UPnP device discovery
nmap -sU -p 1900 --script upnp-info 192.168.1.0/24

# HTTP enumeration (web interfaces)
nmap -p 80,8080 --script http-title,http-headers,http-robots.txt 192.168.1.0/24

# Banner grabbing
nmap -sV --script banner -p 21,22,23,80 192.168.1.0/24

# Default credential checking
nmap -p 23 --script telnet-brute --script-args userdb=users.txt,passdb=passwords.txt 192.168.1.100
```

### OS and Device Fingerprinting

```bash
# OS detection
nmap -O 192.168.1.100

# Aggressive scan (OS + version + scripts + traceroute)
nmap -A 192.168.1.100

# Typical IoT OS fingerprints:
# - "Linux 2.6.X - 3.X" — Most embedded Linux devices
# - "Linux 4.X" — Newer embedded devices
# - "FreeRTOS" — Microcontroller-based devices
# - "VxWorks" — Industrial IoT devices
```

## Network Mapping

### Discovering Network Topology

```bash
# ARP scan (faster than ping for local networks)
arp-scan -l

# Discover all services on the network
nmap -sV --open 192.168.1.0/24 -oX scan_results.xml

# Convert Nmap XML to a visual map
# Use Zenmap (Nmap's GUI) or tools like Maltego
```

### Identifying IoT Device Types

Common indicators that a device is IoT:

| Indicator | Likely Device Type |
|-----------|-------------------|
| GoAhead-Webs on port 80 | IP camera or embedded device |
| Boa HTTPd | Older embedded device |
| BusyBox telnetd on port 23 | Linux-based IoT device |
| RTSP on port 554 | IP camera |
| MQTT on port 1883 | IoT sensor/actuator |
| CoAP on port 5683 | Constrained IoT device |
| UPnP on port 1900 | Smart home device |
| mDNS on port 5353 | Apple HomeKit / Bonjour device |
| SSDP responses | Smart TV, media device |

### MAC Address Vendor Lookup

The first 3 bytes of a MAC address identify the manufacturer:

```bash
# Check a MAC address vendor
# Online: macvendors.com
# Or use arp to see MACs on your network
arp -a

# Common IoT MAC prefixes:
# B8:27:EB — Raspberry Pi
# DC:A6:32 — Raspberry Pi (newer)
# 60:01:94 — Espressif (ESP8266/ESP32)
# 24:0A:C4 — Espressif (ESP32)
# CC:50:E3 — TP-Link
# 00:17:88 — Philips Hue
```

## Monitoring Network Traffic

### Passive Traffic Analysis

```bash
# Capture all traffic on the IoT network
sudo tcpdump -i eth0 -w iot_capture.pcap

# Filter for specific protocols
sudo tcpdump -i eth0 port 1883 -w mqtt_traffic.pcap
sudo tcpdump -i eth0 port 5683 -w coap_traffic.pcap

# Watch for broadcast/multicast (device discovery)
sudo tcpdump -i eth0 broadcast or multicast
```

### Identifying Unencrypted Communications

```bash
# Look for plaintext HTTP
sudo tcpdump -i eth0 -A port 80 | grep -i "password\|token\|key\|secret"

# Look for plaintext MQTT
sudo tcpdump -i eth0 -A port 1883

# Check for DNS requests (reveals what services devices call home to)
sudo tcpdump -i eth0 port 53
```

## Documenting Your Findings

Create a structured report for each device you discover:

```markdown
## Device Assessment: [Device Name]

**Basic Info:**
- IP Address: 192.168.1.100
- MAC Address: 60:01:94:XX:XX:XX (Espressif)
- Open Ports: 80 (HTTP), 1883 (MQTT)
- OS Fingerprint: Linux 4.x (embedded)
- Firmware Version: [if discoverable]

**Services:**
- Port 80: GoAhead-Webs 2.5 — Web configuration interface
- Port 1883: Mosquitto MQTT — No authentication required

**Potential Issues:**
- [ ] No MQTT authentication
- [ ] HTTP (not HTTPS) for web interface
- [ ] Telnet enabled (port 23)

**Next Steps:**
- Capture MQTT traffic to identify data exposure
- Test web interface for default credentials
- Check for firmware update availability
```

## Key Takeaways

- Start with passive recon (Shodan, OSINT) before active scanning
- Nmap with service detection and NSE scripts is essential for IoT assessment
- MAC addresses and service banners help identify device types
- Monitor traffic to find unencrypted communications
- Document everything systematically

## Next Steps

With devices discovered and mapped, move to [Module 5: Firmware Analysis](/modules/05-firmware-analysis) to extract and examine the software running on these devices, or try [Lab: IoT Device Discovery](/labs/lab-device-discovery) for hands-on practice.
