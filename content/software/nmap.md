---
title: "Nmap"
level: Beginner
description: "Network scanner for device discovery and service enumeration"
order: 1
---

# Nmap

## What Is Nmap?

Nmap (Network Mapper) is the standard tool for network discovery and security auditing. In IoT security, Nmap is your starting point for answering fundamental questions:

- What devices are on this network?
- What ports and services are open on each device?
- What operating system or firmware is a device running?
- Are there known vulnerabilities in the exposed services?

IoT devices often expose services that traditional IT devices do not: MQTT brokers, CoAP endpoints, UPnP services, Telnet with default credentials, custom REST APIs, and debugging interfaces. Nmap helps you find all of these.

## Installation

```bash
# Debian/Ubuntu
sudo apt install nmap

# Fedora/RHEL
sudo dnf install nmap

# macOS
brew install nmap

# Windows
# Download the installer from https://nmap.org/download.html
# The Windows version includes Zenmap (GUI) and Npcap (packet capture driver)

# Verify installation
nmap --version
```

## Basic Scanning

### Host Discovery

Before scanning ports, find out what devices are on the network:

```bash
# Ping sweep -- find live hosts on a subnet
sudo nmap -sn 192.168.1.0/24

# ARP discovery (LAN only, more reliable than ping for IoT devices that block ICMP)
sudo nmap -PR -sn 192.168.1.0/24

# Discover hosts without ping (some IoT devices don't respond to ping)
sudo nmap -Pn -sn 192.168.1.0/24
```

**Tip:** Many IoT devices block ICMP ping. If a ping sweep misses devices you know are there, use ARP discovery (`-PR`) on local networks or skip host discovery entirely with `-Pn`.

### Port Scanning

```bash
# Scan the top 1000 ports on a single device
nmap 192.168.1.100

# Scan all 65535 TCP ports (takes longer but thorough)
nmap -p- 192.168.1.100

# Scan specific ports commonly found on IoT devices
nmap -p 22,23,80,443,1883,5683,8080,8443,8883,49152 192.168.1.100

# UDP scan (important! many IoT protocols use UDP)
sudo nmap -sU -p 53,67,123,161,443,5353,5683,47808 192.168.1.100

# Combined TCP and UDP scan
sudo nmap -sS -sU -p T:22,23,80,443,1883,8080,U:53,161,5353,5683 192.168.1.100
```

### Service and Version Detection

```bash
# Detect service versions on open ports
nmap -sV 192.168.1.100

# Aggressive service detection (sends more probes, slower but more accurate)
nmap -sV --version-intensity 5 192.168.1.100

# OS detection
sudo nmap -O 192.168.1.100

# Combined: version detection + OS detection + default scripts
sudo nmap -A 192.168.1.100
```

## IoT-Specific Scan Techniques

### Common IoT Ports and Services

| Port | Protocol | Service | Notes |
|------|----------|---------|-------|
| 22 | TCP | SSH | Remote shell access |
| 23 | TCP | Telnet | Unencrypted shell (very common on IoT) |
| 80 | TCP | HTTP | Web admin interface |
| 443 | TCP | HTTPS | Encrypted web interface |
| 554 | TCP | RTSP | IP camera streams |
| 1883 | TCP | MQTT | IoT messaging (unencrypted) |
| 5353 | UDP | mDNS | Service discovery |
| 5683 | UDP | CoAP | Constrained Application Protocol |
| 8080 | TCP | HTTP Alt | Alternative web interface |
| 8443 | TCP | HTTPS Alt | Alternative encrypted web interface |
| 8883 | TCP | MQTT/TLS | IoT messaging (encrypted) |
| 47808 | UDP | BACnet | Building automation |
| 49152+ | TCP | UPnP | Universal Plug and Play |

### Comprehensive IoT Scan Profile

```bash
# Full IoT scan: common TCP and UDP ports with version detection
sudo nmap -sS -sU \
  -p T:21-23,25,53,80,81,443,554,1883,2323,3000,3306,4443,5000,5555,\
6667,8000,8080,8443,8888,9090,9100,10000,49152-49155 \
  -p U:53,67,69,123,161,500,1900,4500,5353,5683,47808 \
  -sV --version-intensity 3 \
  -O \
  --open \
  192.168.1.0/24

# Explanation of flags:
#   -sS        TCP SYN scan (fast, stealthy)
#   -sU        UDP scan (essential for IoT protocols)
#   -p T:...   Specific TCP ports
#   -p U:...   Specific UDP ports
#   -sV        Service version detection
#   -O         OS detection
#   --open     Only show open ports (reduces noise)
```

### Scanning for Specific IoT Device Types

```bash
# Find IP cameras (RTSP + HTTP)
nmap -p 554,80,8080,8554 --open 192.168.1.0/24

# Find MQTT brokers
nmap -p 1883,8883 --open 192.168.1.0/24

# Find devices with Telnet (often with default creds)
nmap -p 23,2323 --open 192.168.1.0/24

# Find UPnP devices
sudo nmap -sU -p 1900 --open 192.168.1.0/24

# Find BACnet building automation devices
sudo nmap -sU -p 47808 --open 192.168.1.0/24
```

## Useful NSE Scripts for IoT

Nmap Scripting Engine (NSE) scripts extend Nmap with protocol-specific probes and vulnerability checks. Many scripts are included by default; others can be added.

### MQTT Scripts

```bash
# Subscribe to an MQTT broker and list topics (checks for unauthenticated access)
nmap -p 1883 --script mqtt-subscribe 192.168.1.100

# This script connects to the broker without credentials and attempts to
# subscribe to the '#' wildcard topic. If it succeeds, the broker allows
# unauthenticated access -- a critical security issue.
```

### CoAP Scripts

```bash
# Discover CoAP resources (equivalent to /.well-known/core)
nmap -p 5683 -sU --script coap-resources 192.168.1.100

# CoAP is commonly used by constrained IoT devices. The resource discovery
# endpoint lists all available resources, often without authentication.
```

### HTTP Scripts (Web Interfaces)

```bash
# Enumerate web server info and directories
nmap -p 80,8080,443 --script http-title,http-server-header,http-robots-txt 192.168.1.100

# Check for default credentials on web interfaces
nmap -p 80 --script http-default-accounts 192.168.1.100

# Crawl web application
nmap -p 80 --script http-enum 192.168.1.100

# Check for firmware update endpoints
nmap -p 80 --script http-methods,http-title 192.168.1.100
```

### UPnP Scripts

```bash
# Discover and enumerate UPnP services
nmap -sU -p 1900 --script upnp-info 192.168.1.100

# UPnP is a goldmine for IoT security research. Devices advertise their
# capabilities, and many allow unauthenticated control of device functions.
```

### Telnet and SSH Scripts

```bash
# Check for Telnet with no authentication or default credentials
nmap -p 23 --script telnet-ntlm-info,telnet-encryption 192.168.1.100

# Check SSH configuration
nmap -p 22 --script ssh2-enum-algos,ssh-auth-methods 192.168.1.100

# Brute-force Telnet (use with caution and authorization)
nmap -p 23 --script telnet-brute \
  --script-args userdb=users.txt,passdb=passwords.txt 192.168.1.100
```

### RTSP Scripts (IP Cameras)

```bash
# Find accessible RTSP streams
nmap -p 554 --script rtsp-url-brute 192.168.1.100

# Discover RTSP methods
nmap -p 554 --script rtsp-methods 192.168.1.100
```

### Running Multiple Scripts

```bash
# Run all default scripts (safe and useful)
nmap -sC -sV -p 22,23,80,443,1883,5683 192.168.1.100

# Run all scripts in a category
nmap --script discovery -p 80 192.168.1.100

# Run specific scripts with arguments
nmap -p 1883 --script mqtt-subscribe \
  --script-args "mqtt-subscribe.topic=#" 192.168.1.100
```

## Scan Profiles for IoT Networks

### Quick Reconnaissance (1-2 minutes)

```bash
# Fast host discovery and top ports
sudo nmap -sn -PR 192.168.1.0/24 -oG - | grep "Up" | awk '{print $2}' > live_hosts.txt
nmap -sV --top-ports 100 -iL live_hosts.txt -oA quick_scan
```

### Standard Assessment (10-30 minutes)

```bash
sudo nmap -sS -sU \
  -p T:1-1000,1883,2323,5000,8080,8443,8883 \
  -p U:53,161,1900,5353,5683 \
  -sV -sC -O \
  --open \
  -oA standard_scan \
  192.168.1.0/24
```

### Deep Assessment (1+ hours)

```bash
# Full TCP port scan with aggressive version detection
sudo nmap -sS -p- -sV --version-all -O \
  --script "default or discovery or vuln" \
  -oA deep_scan \
  192.168.1.100

# Follow up with full UDP scan on interesting hosts
sudo nmap -sU -p- --max-retries 1 --max-scan-delay 10 \
  -oA udp_deep_scan \
  192.168.1.100
```

## Output Formats

Nmap supports several output formats. Always save your scan results.

```bash
# Normal output (human-readable)
nmap -oN scan_results.txt 192.168.1.0/24

# XML output (parseable by other tools)
nmap -oX scan_results.xml 192.168.1.0/24

# Grepable output (easy to parse with grep/awk)
nmap -oG scan_results.gnmap 192.168.1.0/24

# All formats at once
nmap -oA scan_results 192.168.1.0/24
# Creates: scan_results.nmap, scan_results.xml, scan_results.gnmap
```

### Parsing Nmap Output

```bash
# Extract open ports from grepable output
grep "open" scan_results.gnmap | awk '{print $2, $4}'

# Convert XML to HTML report
xsltproc scan_results.xml -o scan_results.html

# Parse XML with Python
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('scan_results.xml')
for host in tree.findall('.//host'):
    addr = host.find('.//address[@addrtype=\"ipv4\"]')
    if addr is not None:
        ip = addr.get('addr')
        ports = host.findall('.//port[state[@state=\"open\"]]')
        for port in ports:
            print(f'{ip}:{port.get(\"portid\")} {port.find(\"service\").get(\"name\",\"unknown\")}')
"
```

## Practical Examples

### Example 1: Mapping a Smart Home Network

```bash
# Step 1: Find all devices
sudo nmap -sn -PR 192.168.1.0/24 -oG discovery.gnmap

# Step 2: Quick scan of live hosts for IoT-relevant ports
nmap -sV -p 22,23,80,443,554,1883,5353,8080,8443,8883,49152 \
  --open -oA smart_home_scan \
  $(grep Up discovery.gnmap | awk '{print $2}' | tr '\n' ' ')

# Step 3: Deep dive on interesting devices
# (example: device at 192.168.1.42 has MQTT on 1883)
nmap -sV -sC -p 1883 --script mqtt-subscribe 192.168.1.42
```

### Example 2: Finding IP Cameras with Exposed Streams

```bash
# Scan for RTSP and HTTP
nmap -p 554,80,8080 --open --script rtsp-url-brute,http-title \
  -oA camera_scan 192.168.1.0/24

# Look for cameras with default credentials
nmap -p 80 --script http-default-accounts \
  --script-args http-default-accounts.category=web-cam \
  192.168.1.0/24
```

### Example 3: Identifying Devices with Default Telnet Access

```bash
# Find Telnet services
nmap -p 23,2323 --open -sV 192.168.1.0/24

# Try common IoT default credentials
nmap -p 23 --script telnet-brute \
  --script-args 'userdb=/usr/share/nmap/nselib/data/usernames.lst,\
passdb=/usr/share/nmap/nselib/data/passwords.lst,brute.firstonly=true' \
  192.168.1.100
```

## Tips and Best Practices

1. **Always get authorization** before scanning networks you do not own. Unauthorized port scanning may be illegal in your jurisdiction.

2. **Start with host discovery** (`-sn`) before port scanning. Scanning dead hosts wastes time.

3. **Do not forget UDP.** Many IoT protocols (CoAP, mDNS, SNMP, BACnet) use UDP. Skipping UDP scans means missing critical services.

4. **Use `--open`** to filter output to only open ports. IoT scans across many hosts produce a lot of noise otherwise.

5. **Save all scan results** with `-oA`. You will want to compare scans over time and share results with your team.

6. **Adjust timing for fragile devices.** Some IoT devices crash when scanned aggressively. Use `-T2` (polite timing) or `--max-rate 100` for sensitive environments:

   ```bash
   nmap -T2 --max-rate 100 -p 80,443 192.168.1.100
   ```

7. **Use the `--reason` flag** to understand why Nmap reports a port as open, closed, or filtered:

   ```bash
   nmap --reason -p 23,80 192.168.1.100
   ```

8. **Scan from multiple network positions** when possible. Some devices expose different services on different network interfaces (e.g., a management port only accessible from a specific VLAN).

9. **Combine with other tools.** Use Nmap for discovery, then Wireshark for traffic analysis, and specialized tools (MQTT Explorer, CoAP clients) for protocol-specific testing.
