---
title: "Wireshark"
level: Beginner
description: "Packet capture and protocol analysis for IoT traffic"
order: 2
---

# Wireshark

## What Is Wireshark?

Wireshark is the world's most widely used network protocol analyzer. It captures packets flowing across a network interface and presents them in a human-readable format with deep protocol dissection. For IoT security, Wireshark lets you:

- See exactly what data an IoT device sends and to whom
- Determine if communications are encrypted or sent in plaintext
- Identify protocols in use (MQTT, CoAP, HTTP, DNS, mDNS, custom TCP/UDP)
- Capture credentials transmitted in the clear
- Detect firmware update mechanisms and potentially intercept update files
- Analyze proprietary protocols by examining raw packet data
- Verify whether security controls (TLS, authentication) are actually in use

## Installation

```bash
# Debian/Ubuntu
sudo apt install wireshark
# During installation, select "Yes" to allow non-root users to capture
# Add your user to the wireshark group:
sudo usermod -aG wireshark $USER
# Log out and back in

# Fedora
sudo dnf install wireshark wireshark-cli
sudo usermod -aG wireshark $USER

# macOS
brew install --cask wireshark

# Windows
# Download from https://www.wireshark.org/download.html
# Install with Npcap (packet capture driver)
```

### Command-Line Alternative: tshark

tshark is Wireshark's command-line counterpart. It is useful for remote capture, scripting, and headless systems.

```bash
# Capture on interface eth0 and write to file
sudo tshark -i eth0 -w capture.pcapng

# Capture with a display filter
sudo tshark -i eth0 -Y "mqtt" -w mqtt_traffic.pcapng

# Read and filter a capture file
tshark -r capture.pcapng -Y "mqtt.topic"
```

## Capture Basics

### Selecting the Right Interface

IoT traffic capture depends on your network position:

- **Wired (Ethernet):** Capture on the interface connected to the same network segment as the IoT device. If using a switch, you may need to configure port mirroring/SPAN.
- **Wi-Fi monitor mode:** Capture raw 802.11 frames to see Wi-Fi IoT traffic without being part of the network. Requires a compatible wireless adapter.
- **Loopback:** Capture traffic between local applications (useful when testing IoT cloud APIs from your machine).

### Setting Up Port Mirroring

To capture traffic from IoT devices on a switched network, configure your switch to mirror the IoT device's port to your capture port:

```
# Example for a managed switch (syntax varies by vendor):
# Cisco:
monitor session 1 source interface GigabitEthernet0/1
monitor session 1 destination interface GigabitEthernet0/24

# Most consumer routers don't support port mirroring.
# Alternatives:
#   - Use a network tap ($20-50 for a passive Ethernet tap)
#   - Set up ARP spoofing with ettercap or arpspoof (authorized testing only)
#   - Place a transparent bridge (Linux box with two NICs) between the device and router
```

### Starting a Capture

1. Launch Wireshark
2. Select the network interface
3. (Optional) Set a capture filter to reduce the volume:

```
# Capture only traffic from/to a specific IoT device
host 192.168.1.42

# Capture only MQTT traffic
port 1883

# Capture traffic from an IoT device, excluding your SSH session
host 192.168.1.42 and not port 22

# Capture only UDP traffic (CoAP, mDNS, etc.)
udp
```

4. Click the blue shark fin button (or press Ctrl+E) to start
5. Let it run while the device performs the actions you want to analyze
6. Stop the capture (Ctrl+E or the red square button)
7. Save the capture (File > Save As, use .pcapng format)

### Capture Tips for IoT

- **Capture during device boot.** Many IoT devices perform interesting network activity at startup: NTP sync, DNS lookups, cloud service registration, firmware update checks.
- **Capture during setup/pairing.** Device provisioning often reveals cloud endpoints, API keys, and authentication mechanisms.
- **Capture for extended periods.** Some devices only "phone home" periodically (every few minutes or hours).
- **Capture during firmware updates.** This can reveal the update server URL and whether the firmware is downloaded over an encrypted channel.

## Display Filters for IoT Protocols

Display filters let you isolate specific traffic from a capture. They are applied after capture and do not affect what is recorded.

### MQTT (Message Queuing Telemetry Transport)

```
# All MQTT traffic
mqtt

# MQTT CONNECT packets (show client ID, username, password)
mqtt.msgtype == 1

# MQTT PUBLISH packets (show topic and payload data)
mqtt.msgtype == 3

# Filter by MQTT topic name
mqtt.topic contains "temperature"
mqtt.topic contains "sensor"

# MQTT messages with QoS 0 (no confirmation)
mqtt.qos == 0

# Show MQTT credentials (CONNECT packets often contain plaintext credentials)
mqtt.username
mqtt.passwd
```

### CoAP (Constrained Application Protocol)

```
# All CoAP traffic
coap

# CoAP GET requests
coap.code == 1

# CoAP POST requests
coap.code == 2

# CoAP responses (2.05 Content)
coap.code == 69

# Filter by CoAP URI path
coap.opt.uri_path contains "sensor"
```

### Zigbee

Zigbee capture requires either a specialized sniffer (like the TI CC2531 USB dongle) or a compatible SDR setup. Once captured:

```
# All Zigbee traffic
zbee_nwk

# Zigbee APS layer
zbee_aps

# Zigbee ZCL (Cluster Library) commands
zbee_zcl

# Zigbee network key transport (look for key material)
zbee_aps.cmd.key

# Filter by Zigbee network address
zbee_nwk.src == 0x1234
```

### Bluetooth Low Energy (BLE)

BLE capture requires a dedicated sniffer (Ubertooth One, Nordic nRF Sniffer, or Ellisys). Once captured:

```
# All BLE traffic
btle

# BLE advertising packets
btle.advertising_header

# BLE data packets
btle.data_header

# ATT (Attribute Protocol) operations
btatt

# GATT read/write requests
btatt.opcode == 0x0a  # Read request
btatt.opcode == 0x12  # Write request
```

### HTTP (Web Interfaces)

```
# All HTTP traffic
http

# HTTP requests only
http.request

# HTTP responses only
http.response

# Filter by URL path
http.request.uri contains "/api/"
http.request.uri contains "firmware"
http.request.uri contains "update"

# Find credentials in POST data
http.request.method == "POST"

# Find specific content types (firmware downloads are often octet-stream)
http.content_type contains "octet-stream"
```

### DNS (Reveals Cloud Endpoints)

```
# All DNS traffic
dns

# DNS queries only
dns.flags.response == 0

# DNS responses only
dns.flags.response == 1

# Queries for specific domains
dns.qry.name contains "amazonaws"
dns.qry.name contains "azure"
dns.qry.name contains "tuya"

# Find cloud service endpoints the device communicates with
dns.qry.name contains "api"
dns.qry.name contains "iot"
```

### mDNS / DNS-SD (Service Discovery)

```
# All mDNS traffic (multicast DNS on port 5353)
mdns

# DNS-SD service discovery
dns.qry.name contains "_tcp.local"
dns.qry.name contains "_mqtt._tcp"
dns.qry.name contains "_http._tcp"
dns.qry.name contains "_coap._udp"
```

### TLS (Check Encryption Quality)

```
# All TLS traffic
tls

# TLS Client Hello (shows what the device supports)
tls.handshake.type == 1

# TLS Server Hello (shows what was negotiated)
tls.handshake.type == 2

# Check TLS version (look for outdated versions)
tls.record.version == 0x0301  # TLS 1.0 (insecure)
tls.record.version == 0x0302  # TLS 1.1 (insecure)
tls.record.version == 0x0303  # TLS 1.2 (acceptable)

# Certificate exchange
tls.handshake.type == 11
```

### General Utility Filters

```
# Traffic to/from a specific device
ip.addr == 192.168.1.42

# Traffic to external IPs only (not local network)
ip.addr == 192.168.1.42 and not ip.dst == 192.168.1.0/24

# Only show TCP connections being established
tcp.flags.syn == 1 and tcp.flags.ack == 0

# Large packets (possible firmware download)
frame.len > 1400

# Packets containing a specific string
frame contains "password"
frame contains "admin"
frame contains "root"
```

## Following Streams

One of Wireshark's most powerful features is the ability to reconstruct and display an entire conversation between two endpoints.

### TCP Stream

Right-click on any TCP packet and select **Follow > TCP Stream**. This shows you the complete conversation in a readable format. Useful for:

- Reading HTTP request/response pairs in full
- Viewing MQTT message exchanges
- Seeing plaintext protocols like Telnet in their entirety

### UDP Stream

Right-click on a UDP packet and select **Follow > UDP Stream**. Useful for:

- CoAP request/response pairs
- DNS transaction analysis
- Custom UDP protocols

### TLS Stream (Decrypted)

If you have the pre-master secret log or the server's private key, Wireshark can decrypt TLS traffic:

1. Go to **Edit > Preferences > Protocols > TLS**
2. Set the **(Pre)-Master-Secret log filename** to your key log file
3. Follow the TLS stream to see decrypted content

**Getting the pre-master secret log:**

```bash
# Set this environment variable before launching the IoT device's companion app
# or a browser accessing the device's web interface:
export SSLKEYLOGFILE=/tmp/ssl_keys.log

# Then launch the application (e.g., curl, browser, or Python script)
curl --insecure https://192.168.1.42/api/status
```

## Exporting Data

### Export Specific Packets

**File > Export Specified Packets** lets you save a subset of packets based on the current display filter. Useful for sharing only the relevant traffic.

### Export HTTP Objects

**File > Export Objects > HTTP** lists all files transferred over HTTP. This can capture:

- Firmware update files downloaded by the device
- Configuration files
- Web interface assets (which may contain API endpoints and credentials)

### Export Packet Bytes

Right-click on a specific field in the packet details pane and select **Export Packet Bytes** to save raw binary data. Useful for extracting firmware payloads or binary protocol data.

### Export to CSV

```bash
# Export specific fields to CSV using tshark
tshark -r capture.pcapng -T fields \
  -e frame.time -e ip.src -e ip.dst -e tcp.dstport -e mqtt.topic -e mqtt.msg \
  -Y "mqtt.msgtype == 3" \
  -E header=y -E separator=, > mqtt_messages.csv
```

## IoT-Specific Analysis Tips

### 1. Identify All External Endpoints

After capturing traffic from a device, find out where it communicates:

```bash
# List all unique destination IPs (using tshark)
tshark -r capture.pcapng -T fields -e ip.dst \
  -Y "ip.src == 192.168.1.42" | sort -u

# List all DNS queries the device made
tshark -r capture.pcapng -T fields -e dns.qry.name \
  -Y "ip.src == 192.168.1.42 and dns.flags.response == 0" | sort -u
```

### 2. Check for Plaintext Credentials

Many IoT devices still transmit credentials in plaintext:

```bash
# Search for common credential patterns
tshark -r capture.pcapng -Y "frame contains \"password\" or frame contains \"passwd\"" \
  -T fields -e frame.number -e ip.src -e ip.dst -e data.text

# Check MQTT CONNECT packets for credentials
tshark -r capture.pcapng -Y "mqtt.msgtype == 1" \
  -T fields -e mqtt.clientid -e mqtt.username -e mqtt.passwd

# Check HTTP Basic auth
tshark -r capture.pcapng -Y "http.authorization" \
  -T fields -e ip.src -e http.authorization
```

### 3. Analyze Firmware Update Process

```
# Filter for large downloads during update
http.content_length > 100000

# Look for common firmware file names
http.request.uri contains "firmware"
http.request.uri contains ".bin"
http.request.uri contains ".img"
http.request.uri contains "update"
http.request.uri contains "upgrade"
```

If the firmware is downloaded over HTTP (not HTTPS), you can extract it directly from the capture using **File > Export Objects > HTTP**.

### 4. Detect Insecure Protocol Usage

Create a checklist and verify each item:

- Is the device using MQTT on port 1883 (unencrypted) instead of 8883 (TLS)?
- Is the web interface HTTP (port 80) instead of HTTPS (443)?
- Is Telnet (port 23) open instead of SSH (port 22)?
- Are DNS queries going to a hardcoded DNS server instead of the network's DNS?
- Is the device using TLS 1.0 or 1.1 (check Client Hello messages)?
- Are certificates being validated? (Look for self-signed certs in the TLS handshake)

### 5. Profile Device Behavior Over Time

```bash
# Capture for 24 hours
sudo tshark -i eth0 -f "host 192.168.1.42" -w iot_24hr.pcapng -a duration:86400

# Then analyze communication patterns:
# - How often does it phone home?
# - Does it communicate with unexpected endpoints?
# - Does it transmit data at unusual times?
# - How much data does it send/receive?
```

### 6. Create a Protocol Dissector for Custom Protocols

If you encounter a custom binary protocol, you can write a Wireshark dissector in Lua:

```lua
-- Save as ~/.local/lib/wireshark/plugins/custom_iot.lua

local custom_proto = Proto("custom_iot", "Custom IoT Protocol")

local f_cmd = ProtoField.uint8("custom_iot.cmd", "Command", base.HEX)
local f_len = ProtoField.uint16("custom_iot.len", "Length", base.DEC)
local f_data = ProtoField.bytes("custom_iot.data", "Data")

custom_proto.fields = { f_cmd, f_len, f_data }

function custom_proto.dissector(buffer, pinfo, tree)
    if buffer:len() < 3 then return end

    pinfo.cols.protocol = "CustomIoT"
    local subtree = tree:add(custom_proto, buffer(), "Custom IoT Protocol")

    subtree:add(f_cmd, buffer(0,1))
    subtree:add(f_len, buffer(1,2))

    local data_len = buffer(1,2):uint()
    if buffer:len() >= 3 + data_len then
        subtree:add(f_data, buffer(3, data_len))
    end
end

-- Register on a specific TCP port
local tcp_table = DissectorTable.get("tcp.port")
tcp_table:add(12345, custom_proto)
```

Reload Wireshark (**Analyze > Reload Lua Plugins** or Ctrl+Shift+L) and traffic on port 12345 will be decoded using your custom dissector.

## Useful Wireshark Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+E | Start/stop capture |
| Ctrl+F | Find packet |
| Ctrl+G | Go to packet number |
| Ctrl+Shift+L | Reload Lua plugins |
| Ctrl+/ | Apply display filter |
| Right-click > Follow > TCP Stream | Reconstruct conversation |
| Right-click > Apply as Filter | Quick filter on selected field |
| Ctrl+Shift+E | Export packet dissections |

## Combining Wireshark with Other Tools

- **Use Nmap first** to identify devices and open ports, then capture traffic on those ports with Wireshark.
- **Use tcpdump for remote capture** and analyze the pcap file in Wireshark:
  ```bash
  # Capture on a remote device (e.g., a router running OpenWrt)
  ssh root@router "tcpdump -i br-lan -w -" > remote_capture.pcapng
  ```
- **Use mitmproxy** to intercept HTTPS traffic from IoT companion apps, then import the key log into Wireshark.
- **Use Wireshark's I/O graph** (Statistics > I/O Graphs) to visualize traffic patterns over time and identify periodic communication.
