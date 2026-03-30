---
title: "Lab: IoT Protocol Analysis"
level: Beginner
description: "Capture and analyze MQTT and CoAP traffic"
estimated_time: "45 minutes"
tools:
  - Wireshark
  - mosquitto
  - MQTT Explorer
objectives:
  - Set up an MQTT broker
  - Capture MQTT traffic
  - Identify unencrypted data in transit
---

# Lab: IoT Protocol Analysis

## Overview

IoT devices communicate using lightweight protocols like MQTT and CoAP. In this lab you will set up a local MQTT broker, generate traffic, and use Wireshark to capture and inspect packets. You will observe firsthand how unencrypted IoT protocols expose sensitive data on the wire.

## Prerequisites

- A Linux machine (Ubuntu/Kali recommended)
- Root or sudo access
- Wireshark installed
- Mosquitto broker and clients installed
- MQTT Explorer (optional, for a graphical view)

### Install required packages

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients wireshark tshark
```

To install MQTT Explorer, download it from [mqtt-explorer.com](http://mqtt-explorer.com/) or use snap:

```bash
sudo snap install mqtt-explorer
```

---

## Part 1: Setting Up the MQTT Broker

### Step 1: Configure Mosquitto for unauthenticated access

For this lab you will intentionally run an insecure broker to demonstrate the risks. Create a minimal configuration file:

```bash
sudo tee /etc/mosquitto/conf.d/lab.conf << 'EOF'
listener 1883 0.0.0.0
allow_anonymous true
EOF
```

### Step 2: Start the broker

```bash
sudo systemctl restart mosquitto
```

Verify it is running:

```bash
sudo systemctl status mosquitto
```

Confirm port 1883 is open:

```bash
ss -tlnp | grep 1883
```

You should see output like:

```
LISTEN  0  128  0.0.0.0:1883  0.0.0.0:*  users:(("mosquitto",pid=12345,fd=5))
```

---

## Part 2: Generating MQTT Traffic

### Step 3: Open a subscriber

In one terminal window, subscribe to all topics using the wildcard `#`:

```bash
mosquitto_sub -h 127.0.0.1 -t '#' -v
```

**Flags explained:**
- `-h 127.0.0.1` -- Connect to localhost
- `-t '#'` -- Subscribe to all topics (wildcard)
- `-v` -- Verbose mode, prints topic name with each message

Leave this running.

### Step 4: Publish test messages

Open a second terminal and publish messages that simulate IoT sensor data:

```bash
# Publish a temperature reading
mosquitto_pub -h 127.0.0.1 -t 'home/livingroom/temperature' -m '{"value": 22.5, "unit": "celsius"}'

# Publish a humidity reading
mosquitto_pub -h 127.0.0.1 -t 'home/livingroom/humidity' -m '{"value": 45, "unit": "percent"}'

# Publish a simulated door lock status
mosquitto_pub -h 127.0.0.1 -t 'home/frontdoor/lock' -m '{"status": "unlocked", "pin": "1234"}'

# Publish a simulated camera feed URL
mosquitto_pub -h 127.0.0.1 -t 'home/garage/camera' -m '{"stream": "rtsp://admin:password123@192.168.1.50:554/live"}'
```

You should see all four messages appear in the subscriber terminal.

### Step 5: Simulate continuous traffic

Create a script that publishes data every few seconds:

```bash
cat << 'SCRIPT' > /tmp/iot_simulator.sh
#!/bin/bash
while true; do
    TEMP=$(echo "scale=1; 20 + $RANDOM % 100 / 10" | bc)
    HUMIDITY=$(( 30 + RANDOM % 40 ))
    mosquitto_pub -h 127.0.0.1 -t "sensor/node1/temperature" -m "{\"temp\": $TEMP}"
    mosquitto_pub -h 127.0.0.1 -t "sensor/node1/humidity" -m "{\"humidity\": $HUMIDITY}"
    mosquitto_pub -h 127.0.0.1 -t "device/status" -m "{\"device\": \"node1\", \"api_key\": \"sk-abc123secret\"}"
    sleep 3
done
SCRIPT
chmod +x /tmp/iot_simulator.sh
bash /tmp/iot_simulator.sh &
```

---

## Part 3: Capturing Traffic with Wireshark

### Step 6: Start Wireshark capture

Launch Wireshark and capture on the loopback interface (since broker and clients are on the same machine):

```bash
sudo wireshark &
```

1. Select the **Loopback: lo** interface.
2. Click the blue shark fin icon to begin capturing.

Alternatively, use `tshark` from the command line:

```bash
sudo tshark -i lo -f 'tcp port 1883' -w /tmp/mqtt_capture.pcap
```

### Step 7: Apply MQTT display filter

In Wireshark's filter bar, type:

```
mqtt
```

Press Enter. You should now see only MQTT packets.

### Step 8: Inspect MQTT packets

Click on any MQTT **Publish Message** packet. In the packet details pane, expand:

1. **MQ Telemetry Transport Protocol**
2. Look at the **Topic** field -- you will see the topic name in cleartext (e.g., `home/frontdoor/lock`).
3. Look at the **Message** field -- you will see the full payload in cleartext.

**Key observation:** The door lock PIN (`"pin": "1234"`) and the camera credentials (`admin:password123`) are fully visible to anyone capturing network traffic.

### Step 9: Examine the MQTT protocol structure

Select a **Connect** packet and observe:

- **Protocol Name:** `MQTT`
- **Protocol Level:** 4 (MQTT v3.1.1) or 5 (MQTT v5.0)
- **Connect Flags:** Shows if username/password are included
- **Client ID:** The identifier the client uses
- **Username / Password:** If present, transmitted in cleartext

Select a **Subscribe** packet and observe:

- **Topic Filter:** What topics the client requested
- **QoS Level:** Quality of Service requested (0, 1, or 2)

---

## Part 4: Analyzing CoAP Traffic

CoAP (Constrained Application Protocol) runs over UDP and is used by resource-constrained IoT devices.

### Step 10: Install a CoAP tool

```bash
sudo apt install -y libcoap2-bin
```

Or use Python's `aiocoap`:

```bash
pip3 install aiocoap
```

### Step 11: Set up a CoAP server

Create a simple CoAP server using Python:

```bash
cat << 'PYEOF' > /tmp/coap_server.py
import asyncio
import aiocoap
import aiocoap.resource

class TemperatureResource(aiocoap.resource.Resource):
    async def render_get(self, request):
        payload = b'{"temperature": 23.5, "unit": "celsius"}'
        return aiocoap.Message(payload=payload, content_format=50)

class SecretResource(aiocoap.resource.Resource):
    async def render_get(self, request):
        payload = b'{"api_key": "super-secret-key-12345"}'
        return aiocoap.Message(payload=payload, content_format=50)

async def main():
    root = aiocoap.resource.Site()
    root.add_resource(['temperature'], TemperatureResource())
    root.add_resource(['secret'], SecretResource())
    await aiocoap.Context.create_server_context(root, bind=("127.0.0.1", 5683))
    await asyncio.get_event_loop().create_future()

asyncio.run(main())
PYEOF
python3 /tmp/coap_server.py &
```

### Step 12: Query the CoAP server and capture traffic

Start a capture on the loopback interface filtering for UDP port 5683:

```bash
sudo tshark -i lo -f 'udp port 5683' -w /tmp/coap_capture.pcap &
```

Now send CoAP requests:

```bash
# Using coap-client (from libcoap2-bin)
coap-client -m get coap://127.0.0.1/temperature
coap-client -m get coap://127.0.0.1/secret
```

Or with aiocoap:

```bash
python3 -m aiocoap.cli.client --method GET coap://127.0.0.1/temperature
python3 -m aiocoap.cli.client --method GET coap://127.0.0.1/secret
```

### Step 13: Inspect CoAP packets in Wireshark

Open the saved capture:

```bash
wireshark /tmp/coap_capture.pcap &
```

Apply the display filter `coap`. Observe:

- **CoAP header:** Version, Type (CON/NON/ACK/RST), Code (GET/POST/PUT/DELETE), Message ID
- **URI-Path options:** The requested resource path in cleartext
- **Payload:** The JSON response body in cleartext

---

## Part 5: Demonstrating Why Encryption Matters

### Step 14: Compare encrypted vs. unencrypted traffic

To see the difference encryption makes, configure Mosquitto with TLS.

Generate self-signed certificates (for lab purposes only):

```bash
# Create a Certificate Authority
openssl req -new -x509 -days 365 -extensions v3_ca \
  -keyout /tmp/ca.key -out /tmp/ca.crt \
  -subj "/CN=IoT Lab CA" -nodes

# Create a server key and certificate signing request
openssl genrsa -out /tmp/server.key 2048
openssl req -new -key /tmp/server.key -out /tmp/server.csr \
  -subj "/CN=localhost"

# Sign the server certificate with the CA
openssl x509 -req -in /tmp/server.csr -CA /tmp/ca.crt \
  -CAkey /tmp/ca.key -CAcreateserial -out /tmp/server.crt -days 365
```

Create a TLS-enabled Mosquitto listener:

```bash
sudo tee /etc/mosquitto/conf.d/lab-tls.conf << 'EOF'
listener 8883 0.0.0.0
cafile /tmp/ca.crt
certfile /tmp/server.crt
keyfile /tmp/server.key
allow_anonymous true
EOF
sudo systemctl restart mosquitto
```

Now publish a message over TLS:

```bash
mosquitto_pub -h 127.0.0.1 -p 8883 \
  --cafile /tmp/ca.crt \
  -t 'home/frontdoor/lock' \
  -m '{"status": "unlocked", "pin": "1234"}'
```

Capture the TLS traffic and compare:

```bash
sudo tshark -i lo -f 'tcp port 8883' -c 20
```

**Key observation:** With TLS the payload is encrypted. You will see TLS handshake packets (Client Hello, Server Hello, Certificate) followed by **Application Data** packets whose content is opaque. The topic name, message body, and credentials are no longer visible.

---

## Analysis Questions

1. What types of sensitive data did you observe in the unencrypted MQTT capture?
2. How could an attacker on the same network exploit the information leaked by the MQTT traffic?
3. What is the difference between MQTT QoS 0, 1, and 2? How does each appear in the packet capture?
4. Why does CoAP use UDP instead of TCP? What are the security implications?
5. What additional protections beyond TLS should be applied to an MQTT broker in production?

---

## Cleanup

Stop all background processes and remove lab files:

```bash
# Stop the simulator
kill %1 2>/dev/null

# Stop the CoAP server
kill %2 2>/dev/null

# Remove lab configuration
sudo rm -f /etc/mosquitto/conf.d/lab.conf /etc/mosquitto/conf.d/lab-tls.conf
sudo systemctl restart mosquitto

# Remove temporary files
rm -f /tmp/iot_simulator.sh /tmp/coap_server.py /tmp/mqtt_capture.pcap /tmp/coap_capture.pcap
rm -f /tmp/ca.key /tmp/ca.crt /tmp/server.key /tmp/server.csr /tmp/server.crt /tmp/ca.srl
```

## Next Steps

- Proceed to **Lab: Firmware Extraction & Analysis** to look inside IoT device firmware.
- Experiment with MQTT authentication by adding `password_file` to the Mosquitto configuration and observe the CONNECT packets.
- Try using MQTT Explorer to browse topics graphically and compare with the command-line experience.
