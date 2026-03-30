---
title: "Challenge: Find the Broker"
level: Beginner
description: "An MQTT broker is hiding on the network. Find it and read the secret topic."
points: 100
hints:
  - "MQTT's default port is 1883"
  - "Try subscribing to the '#' wildcard topic"
  - "The flag is published every 30 seconds"
---

# Challenge: Find the Broker

## Scenario

You have been brought in to perform a security assessment of a smart building network. Intelligence suggests that an unsecured MQTT broker is running somewhere on the network, and sensitive building automation data -- including a secret administrative flag -- is being published on it. Your mission is to find the broker, connect to it, and retrieve the flag.

## Objectives

1. Discover the MQTT broker on the network.
2. Connect to the broker without credentials.
3. Find the topic that contains the flag.
4. Retrieve the flag.

## Rules

- You may only use tools available on your assessment machine (Nmap, Mosquitto clients, Wireshark).
- The flag format is `FLAG{some_text_here}`.
- Do not modify or disrupt any services on the network.
- Time limit: 15 minutes.

## Network Information

- Your machine IP: `10.10.10.100`
- Target network range: `10.10.10.0/24`
- All devices are on the same Layer 2 segment.

---

## Challenge Environment Setup (For Instructors)

To set up this challenge, run the following on the broker machine (`10.10.10.50` or any IP on the network):

```bash
# Install Mosquitto
sudo apt install -y mosquitto mosquitto-clients

# Configure open broker
sudo tee /etc/mosquitto/conf.d/ctf.conf << 'EOF'
listener 1883 0.0.0.0
allow_anonymous true
EOF
sudo systemctl restart mosquitto

# Publish decoy data and the flag on a loop
cat << 'SCRIPT' > /tmp/ctf_publisher.sh
#!/bin/bash
while true; do
    # Decoy topics
    mosquitto_pub -h 127.0.0.1 -t "building/floor1/temperature" -m '{"temp": 22.3}'
    mosquitto_pub -h 127.0.0.1 -t "building/floor1/humidity" -m '{"humidity": 48}'
    mosquitto_pub -h 127.0.0.1 -t "building/floor2/temperature" -m '{"temp": 23.1}'
    mosquitto_pub -h 127.0.0.1 -t "building/elevator/status" -m '{"floor": 3, "direction": "up"}'
    mosquitto_pub -h 127.0.0.1 -t "building/hvac/mode" -m '{"mode": "cooling"}'

    # The flag (on a less obvious topic)
    mosquitto_pub -h 127.0.0.1 -t "building/admin/secret" -m 'FLAG{mqtt_n0_auth_1s_a_pr0blem}'

    sleep 30
done
SCRIPT
chmod +x /tmp/ctf_publisher.sh
nohup bash /tmp/ctf_publisher.sh &
```

---

## Getting Started

You know the target network is `10.10.10.0/24` and you are looking for an MQTT broker. Think about:

- What port does MQTT use by default?
- How can you quickly find hosts with that port open?
- Once you find the broker, how do you subscribe to all topics?

---

<details>
<summary><strong>Hint 1 (click to reveal)</strong></summary>

MQTT uses TCP port 1883 by default (or 8883 for TLS). Scan the network for hosts with port 1883 open:

```bash
sudo nmap -sS -p 1883 10.10.10.0/24
```

</details>

<details>
<summary><strong>Hint 2 (click to reveal)</strong></summary>

The MQTT wildcard topic `#` subscribes to all topics on the broker. Use:

```bash
mosquitto_sub -h <broker_ip> -t '#' -v
```

</details>

<details>
<summary><strong>Hint 3 (click to reveal)</strong></summary>

The flag is published every 30 seconds. Keep your subscriber running and wait for it to appear. Look for topics with words like `admin`, `secret`, or `flag`.

</details>

---

<details>
<summary><strong>Full Walkthrough (click to reveal)</strong></summary>

### Step 1: Scan for the MQTT broker

Run an Nmap scan targeting port 1883 across the network:

```bash
sudo nmap -sS -p 1883 10.10.10.0/24
```

**Expected output:**

```
Nmap scan report for 10.10.10.50
Host is up (0.0012s latency).

PORT     STATE SERVICE
1883/tcp open  mqtt
```

You found the broker at `10.10.10.50`.

### Step 2: Verify the broker with service detection

```bash
sudo nmap -sV -p 1883 10.10.10.50
```

**Expected output:**

```
PORT     STATE SERVICE VERSION
1883/tcp open  mqtt    Mosquitto MQTT 2.0.x
```

### Step 3: Subscribe to all topics

```bash
mosquitto_sub -h 10.10.10.50 -t '#' -v
```

**Expected output (wait up to 30 seconds):**

```
building/floor1/temperature {"temp": 22.3}
building/floor1/humidity {"humidity": 48}
building/floor2/temperature {"temp": 23.1}
building/elevator/status {"floor": 3, "direction": "up"}
building/hvac/mode {"mode": "cooling"}
building/admin/secret FLAG{mqtt_n0_auth_1s_a_pr0blem}
```

### Step 4: Capture the flag

The flag is: **`FLAG{mqtt_n0_auth_1s_a_pr0blem}`**

### What you learned

- Unauthenticated MQTT brokers are trivially discoverable with a port scan.
- The `#` wildcard exposes every topic and message on the broker.
- Sensitive data published to MQTT without authentication and without TLS is visible to anyone on the network.

</details>

---

## Scoring

| Criteria | Points |
|----------|--------|
| Discovered the broker IP | 25 |
| Connected to the broker | 25 |
| Retrieved the flag | 50 |
| **Total** | **100** |
