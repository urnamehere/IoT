---
title: "IoT Fundamentals"
order: 1
level: Beginner
description: "What is the Internet of Things, how it works, and why security matters"
estimated_time: "45 minutes"
related_labs:
  - lab-device-discovery
---

## What is the Internet of Things?

The Internet of Things (IoT) refers to the network of physical devices embedded with sensors, software, and connectivity that enables them to collect and exchange data. These aren't traditional computers — they're everyday objects made "smart" by adding computing capability and network access.

Examples of IoT devices you encounter daily:

- **Smart home**: Thermostats (Nest), voice assistants (Alexa, Google Home), smart locks, cameras
- **Wearables**: Fitness trackers, smartwatches, medical monitors
- **Industrial**: Factory sensors, SCADA systems, smart meters, fleet trackers
- **Infrastructure**: Traffic lights, water quality monitors, environmental sensors
- **Medical**: Insulin pumps, pacemakers, hospital patient monitors

By current estimates, there are over 15 billion IoT devices connected worldwide, and that number is growing rapidly.

## IoT Architecture: The Three-Layer Model

Most IoT systems follow a three-layer architecture:

### 1. Perception Layer (Edge/Device Layer)

This is the physical hardware — the "things" in IoT. It includes:

- **Sensors**: Temperature, humidity, motion, light, pressure, GPS
- **Actuators**: Motors, relays, valves, displays
- **Microcontrollers**: ESP32, Arduino, STM32, Raspberry Pi
- **Communication modules**: WiFi, BLE, Zigbee, LoRa, cellular radios

The perception layer collects data from the physical world and sends it upward.

### 2. Network Layer (Transport Layer)

This layer handles communication between devices and the cloud/server:

- **Protocols**: MQTT, CoAP, HTTP/HTTPS, AMQP, WebSocket
- **Transport**: WiFi, Ethernet, Cellular (4G/5G), LPWAN (LoRa, Sigfox)
- **Gateways**: Devices that bridge between local protocols (BLE, Zigbee) and the internet

### 3. Application Layer

Where data is processed, stored, and presented to users:

- **Cloud platforms**: AWS IoT, Azure IoT Hub, Google Cloud IoT
- **Dashboards**: Web and mobile interfaces for monitoring
- **Analytics**: Machine learning, anomaly detection, alerting
- **APIs**: Interfaces for third-party integration

## Common IoT Communication Protocols

| Protocol | Transport | Use Case | Port |
|----------|-----------|----------|------|
| MQTT | TCP | Lightweight messaging, telemetry | 1883 (8883 TLS) |
| CoAP | UDP | Constrained devices, RESTful | 5683 (5684 DTLS) |
| HTTP/REST | TCP | Web APIs, configuration | 80/443 |
| BLE | Radio | Short-range, low power | N/A (wireless) |
| Zigbee | Radio | Mesh networking, home automation | N/A (wireless) |
| LoRaWAN | Radio | Long-range, low power | N/A (wireless) |
| AMQP | TCP | Enterprise messaging | 5672 |

### MQTT — The Lingua Franca of IoT

MQTT (Message Queuing Telemetry Transport) is the most widely used IoT protocol. It uses a publish/subscribe model:

```
Device (Publisher) → MQTT Broker → Subscriber(s)

Example:
  Thermostat publishes to: home/living-room/temperature
  Phone app subscribes to: home/living-room/temperature
```

Key MQTT concepts:
- **Broker**: Central server that routes messages (e.g., Mosquitto, HiveMQ)
- **Topics**: Hierarchical strings like `home/sensor/temperature`
- **QoS Levels**: 0 (at most once), 1 (at least once), 2 (exactly once)
- **Retained messages**: Broker stores the last message for new subscribers
- **Last Will and Testament (LWT)**: Message sent if a device disconnects unexpectedly

## The IoT Attack Surface

IoT devices present a uniquely large attack surface compared to traditional IT systems:

### Device-Level Attacks
- **Default credentials**: Many devices ship with admin/admin or similar
- **Unencrypted storage**: Sensitive data stored in plaintext on flash memory
- **Debug interfaces**: UART, JTAG, SWD ports left accessible on the PCB
- **Outdated firmware**: Devices rarely get updated, running known-vulnerable software

### Network-Level Attacks
- **Unencrypted communication**: MQTT without TLS, HTTP instead of HTTPS
- **Man-in-the-middle**: Intercepting traffic between devices and cloud
- **DNS rebinding**: Accessing local IoT devices from the internet
- **Lateral movement**: Compromised IoT device used to attack the rest of the network

### Cloud/Application Attacks
- **Insecure APIs**: Missing authentication, authorization bypass
- **Data exposure**: Sensitive telemetry data accessible without authentication
- **Account takeover**: Weak password policies on companion apps

### Physical Attacks
- **Firmware extraction**: Reading flash memory to extract code and secrets
- **Bus sniffing**: Intercepting SPI/I2C/UART communications between chips
- **Glitching**: Voltage or clock manipulation to bypass security checks
- **Side-channel attacks**: Power analysis to extract cryptographic keys

## Why IoT Security Matters: Real-World Incidents

### The Mirai Botnet (2016)

The Mirai malware scanned the internet for IoT devices with default credentials (a list of just 62 username/password pairs). It compromised over 600,000 devices — mostly cameras, DVRs, and routers — and used them to launch the largest DDoS attack in history at the time, taking down major websites including Twitter, Netflix, and Reddit.

**Lesson**: Default credentials on internet-facing devices are catastrophically dangerous.

### Smart Lock Vulnerabilities

Researchers have repeatedly demonstrated vulnerabilities in smart locks:
- Locks transmitting plaintext BLE commands that could be replayed
- API endpoints allowing any authenticated user to unlock any lock
- Hardcoded encryption keys shared across all devices of the same model

**Lesson**: Physical security devices need the highest standard of digital security.

### Medical Device Risks

In 2017, the FDA recalled 465,000 pacemakers due to vulnerabilities that could allow an attacker to modify pacing commands or deplete the battery. St. Jude Medical (now Abbott) had to issue firmware updates to implanted devices.

**Lesson**: IoT security can be a matter of life and death.

### Baby Monitor Breaches

Multiple incidents of attackers accessing internet-connected baby monitors to spy on families, play sounds, or speak through the device. Most exploited default credentials or unpatched firmware.

**Lesson**: Consumer IoT devices in private spaces carry serious privacy risks.

## The OWASP IoT Top 10

The Open Web Application Security Project maintains a list of the most critical IoT security risks:

1. **Weak, guessable, or hardcoded passwords**
2. **Insecure network services**
3. **Insecure ecosystem interfaces** (web, API, cloud, mobile)
4. **Lack of secure update mechanism**
5. **Use of insecure or outdated components**
6. **Insufficient privacy protection**
7. **Insecure data transfer and storage**
8. **Lack of device management**
9. **Insecure default settings**
10. **Lack of physical hardening**

## Your IoT Security Learning Path

This course will take you through each aspect of IoT security:

1. **Networking** — Understand how IoT devices communicate
2. **Lab Setup** — Build your testing environment
3. **Reconnaissance** — Find and fingerprint devices
4. **Firmware Analysis** — Extract and reverse engineer device software
5. **Hardware Hacking** — Access physical debug interfaces
6. **Wireless Attacks** — Exploit radio communications
7. **Exploitation & Reporting** — Chain vulnerabilities and disclose responsibly

Each module builds on the previous ones, but you can jump to any topic that interests you. The hands-on labs will give you practical experience with real tools.

## Key Takeaways

- IoT devices are everywhere and often have minimal security
- The attack surface spans hardware, network, and cloud layers
- Real-world breaches have caused massive disruption and safety risks
- Understanding IoT security requires knowledge across multiple disciplines
- This course will take you from fundamentals to advanced research techniques

## Next Steps

Continue to [Module 2: Networking Basics for IoT](/modules/02-networking-for-iot) to understand how IoT devices communicate, or jump to [Lab: IoT Device Discovery](/labs/lab-device-discovery) if you want to start hands-on immediately.
