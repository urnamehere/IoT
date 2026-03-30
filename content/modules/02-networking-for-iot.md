---
title: "Networking Basics for IoT"
order: 2
level: Beginner
description: "TCP/IP, WiFi, BLE, Zigbee, MQTT, CoAP — how IoT devices talk"
estimated_time: "60 minutes"
prerequisites:
  - "Module 1: IoT Fundamentals"
related_labs:
  - lab-packet-capture
---

## TCP/IP Fundamentals for IoT

Before diving into IoT-specific protocols, you need a solid understanding of how networks work. Even wireless IoT protocols eventually connect to IP networks.

### The TCP/IP Model for IoT

```
┌─────────────────────────────┐
│   Application Layer         │  MQTT, CoAP, HTTP, AMQP
├─────────────────────────────┤
│   Transport Layer           │  TCP, UDP
├─────────────────────────────┤
│   Network Layer             │  IPv4, IPv6, 6LoWPAN
├─────────────────────────────┤
│   Link Layer                │  WiFi, Ethernet, BLE, Zigbee, LoRa
└─────────────────────────────┘
```

### Key Ports for IoT Security

When scanning for IoT devices, these are the ports you'll look for:

| Port | Protocol | Service |
|------|----------|---------|
| 22 | TCP | SSH (device management) |
| 23 | TCP | Telnet (insecure remote access) |
| 80 | TCP | HTTP (web interface) |
| 443 | TCP | HTTPS (secure web interface) |
| 554 | TCP | RTSP (IP cameras) |
| 1883 | TCP | MQTT (unencrypted) |
| 5683 | UDP | CoAP (unencrypted) |
| 8080 | TCP | HTTP alternate (web interfaces) |
| 8443 | TCP | HTTPS alternate |
| 8883 | TCP | MQTT over TLS |
| 49152+ | TCP/UDP | UPnP, mDNS, custom services |

## WiFi Security for IoT

Most consumer IoT devices connect via WiFi. Understanding WiFi security is essential.

### WPA2 vs WPA3

**WPA2 (most current IoT devices)**:
- Uses a Pre-Shared Key (PSK) or Enterprise (802.1X) authentication
- Vulnerable to offline dictionary attacks if the handshake is captured
- KRACK attack (2017) demonstrated protocol-level vulnerability
- Still the most common WiFi security on IoT devices

**WPA3 (newer devices)**:
- Uses SAE (Simultaneous Authentication of Equals) — resistant to offline attacks
- Forward secrecy — captured traffic can't be decrypted later
- Enhanced Open (OWE) — encryption even on open networks
- Still rare on IoT devices due to hardware requirements

### WiFi Security Concerns for IoT

```
Common issues:
1. Devices that only support WPA2-PSK (no Enterprise)
2. Devices that fall back to open networks during setup
3. Hard-coded WiFi credentials in firmware
4. No certificate validation for HTTPS connections
5. mDNS/UPnP services exposing device info on the LAN
```

## Bluetooth Low Energy (BLE)

BLE is the dominant protocol for short-range IoT communication — fitness trackers, smart locks, medical devices, beacons.

### BLE Architecture

```
┌──────────────────────────┐
│      Application         │  Custom profiles
├──────────────────────────┤
│      GATT (Generic       │  Services & Characteristics
│      Attribute Profile)  │
├──────────────────────────┤
│      ATT (Attribute      │  Read/Write/Notify operations
│      Protocol)           │
├──────────────────────────┤
│      L2CAP               │  Logical link control
├──────────────────────────┤
│      Link Layer          │  Advertising, connections
├──────────────────────────┤
│      Physical Layer      │  2.4 GHz radio, 40 channels
└──────────────────────────┘
```

### GATT — The Heart of BLE Communication

GATT (Generic Attribute Profile) defines how BLE devices exchange data:

- **Services**: Groups of related functionality (e.g., "Heart Rate Service")
- **Characteristics**: Individual data points within a service (e.g., "Heart Rate Measurement")
- **Descriptors**: Metadata about characteristics

Each service and characteristic is identified by a UUID:
- **Standard UUIDs**: Defined by the Bluetooth SIG (e.g., `0x180D` = Heart Rate)
- **Custom UUIDs**: 128-bit UUIDs defined by the manufacturer

### BLE Security Modes

| Mode | Level | Description |
|------|-------|-------------|
| Mode 1 Level 1 | No security | No encryption, no authentication |
| Mode 1 Level 2 | Unauthenticated | Encrypted but no MITM protection |
| Mode 1 Level 3 | Authenticated | Encrypted with MITM protection |
| Mode 1 Level 4 | Secure Connections | LE Secure Connections with AES-CMAC |

**Security concern**: Many IoT devices use Mode 1 Level 1 (no security) or Level 2 (no MITM protection). This means commands can be sniffed and replayed.

### Scanning for BLE Devices

```bash
# Using hcitool (Linux)
sudo hcitool lescan

# Using bluetoothctl
bluetoothctl
> scan on

# Example output:
# [NEW] Device AA:BB:CC:DD:EE:FF SmartLock-1234
# [NEW] Device 11:22:33:44:55:66 FitBand
```

## Zigbee and Z-Wave

### Zigbee

Zigbee is a mesh networking protocol popular in home automation (Philips Hue, Samsung SmartThings):

- **Frequency**: 2.4 GHz (global), 868 MHz (Europe), 915 MHz (Americas)
- **Range**: 10-100 meters
- **Topology**: Star, tree, or mesh
- **Security**: AES-128 encryption with network key
- **Vulnerability**: If the network key is captured during pairing, all traffic can be decrypted

### Z-Wave

Z-Wave is a proprietary protocol for home automation:

- **Frequency**: Sub-1 GHz (varies by region: 908.42 MHz US, 868.42 MHz EU)
- **Range**: 30-100 meters
- **Topology**: Mesh network
- **Security**: S2 framework with ECDH key exchange (newer devices)
- **Vulnerability**: Older Z-Wave devices (S0 security) use a known key exchange flaw

## MQTT Deep Dive

MQTT is critical to understand for IoT security. Let's go deeper.

### How MQTT Works

```
Publisher                    Broker                     Subscriber
   │                          │                            │
   │── CONNECT ──────────────>│                            │
   │<── CONNACK ──────────────│                            │
   │                          │                            │
   │                          │<── CONNECT ────────────────│
   │                          │── CONNACK ────────────────>│
   │                          │                            │
   │                          │<── SUBSCRIBE (topic) ──────│
   │                          │── SUBACK ─────────────────>│
   │                          │                            │
   │── PUBLISH (topic, msg) ─>│                            │
   │                          │── PUBLISH (topic, msg) ───>│
```

### MQTT Security Issues

**1. No Authentication by Default**

Many MQTT brokers are deployed without authentication:

```bash
# Connecting to an unauthenticated broker
mosquitto_sub -h broker.example.com -t '#'
# '#' subscribes to ALL topics — see everything
```

**2. No Encryption by Default**

MQTT on port 1883 is plaintext. All messages, including credentials, are visible:

```bash
# Capturing MQTT traffic with tcpdump
sudo tcpdump -i eth0 -A port 1883
```

**3. Topic Authorization**

Even with authentication, many brokers don't implement topic-level authorization. Any authenticated user can subscribe to any topic.

**4. Retained Messages**

Retained messages persist on the broker. Sensitive data in retained messages remains accessible to new subscribers.

### Setting Up a Test MQTT Broker

```bash
# Install Mosquitto broker and clients
sudo apt install mosquitto mosquitto-clients

# Start the broker
sudo systemctl start mosquitto

# Subscribe to all topics in one terminal
mosquitto_sub -h localhost -t '#' -v

# Publish a test message in another terminal
mosquitto_pub -h localhost -t 'test/hello' -m 'Hello IoT World'
```

## CoAP (Constrained Application Protocol)

CoAP is the REST of constrained IoT. It's like HTTP but designed for tiny devices over UDP.

### CoAP vs HTTP

| Feature | CoAP | HTTP |
|---------|------|------|
| Transport | UDP | TCP |
| Overhead | 4-byte header | Large headers |
| Methods | GET, PUT, POST, DELETE | Full HTTP methods |
| Observe | Built-in (like WebSocket) | Requires polling or WebSocket |
| Security | DTLS | TLS |
| Discovery | `/.well-known/core` | No standard |

### CoAP Resource Discovery

```bash
# Discover resources on a CoAP server
coap-client -m get coap://device.local/.well-known/core

# Example response:
# </temperature>;rt="sensor";ct=0,
# </humidity>;rt="sensor";ct=0,
# </config>;rt="config";ct=50
```

## Network Segmentation for IoT

A critical defensive measure is network segmentation — keeping IoT devices on a separate network:

```
┌─────────────────────────────────────────┐
│           Main Network (VLAN 1)          │
│   Laptops, phones, servers               │
├─────────────────────────────────────────┤
│           IoT Network (VLAN 10)          │
│   Smart home devices, cameras, sensors   │
│   No access to main network              │
│   Internet access restricted             │
├─────────────────────────────────────────┤
│           Guest Network (VLAN 20)        │
│   Visitor devices                        │
└─────────────────────────────────────────┘
```

### Why This Matters

If an attacker compromises an IoT device, segmentation prevents them from:
- Accessing your computers and files
- Pivoting to other devices on the network
- Intercepting your personal traffic

## Practical Exercise

Try these commands to explore IoT network traffic in your lab:

```bash
# 1. Start Wireshark and filter for IoT protocols
# Display filter: mqtt or coap or zbee_nwk or btatt

# 2. Scan your local network for IoT devices
nmap -sV --open -p 22,23,80,443,554,1883,5683,8080,8883 192.168.1.0/24

# 3. Check for open MQTT brokers
nmap -p 1883 --script mqtt-subscribe 192.168.1.0/24
```

## Key Takeaways

- IoT devices use a mix of standard (TCP/IP) and specialized (BLE, Zigbee) protocols
- MQTT is the most common IoT messaging protocol — and often deployed insecurely
- BLE is dominant for short-range consumer IoT — and frequently lacks proper security
- Network segmentation is the single most impactful defensive measure
- Understanding these protocols is essential before you can test their security

## Next Steps

Proceed to [Module 3: Setting Up Your Lab](/modules/03-setting-up-your-lab) to build your testing environment, or try [Lab: IoT Protocol Analysis](/labs/lab-packet-capture) to start capturing real MQTT traffic.
