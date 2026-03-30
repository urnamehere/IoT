---
title: "Lab: BLE Device Reconnaissance"
level: Advanced
description: "Scan, enumerate, and analyze Bluetooth Low Energy devices"
estimated_time: "60 minutes"
tools:
  - gatttool
  - bettercap
  - nRF Connect
objectives:
  - Scan for BLE devices
  - Enumerate GATT services
  - Read and write characteristics
  - Identify security weaknesses
---

# Lab: BLE Device Reconnaissance

## Overview

Bluetooth Low Energy (BLE) is used extensively in IoT devices -- smart locks, fitness trackers, medical devices, beacons, and home automation products. Many BLE devices have weak or nonexistent authentication, allowing nearby attackers to read sensitive data, send unauthorized commands, or perform replay attacks.

In this lab you will scan for BLE devices, enumerate their GATT (Generic Attribute Profile) services and characteristics, read and write data, and identify common security weaknesses.

## Prerequisites

### Hardware

- A Linux machine with a Bluetooth adapter that supports BLE (Bluetooth 4.0+)
- At least one BLE device to test (smart bulb, fitness tracker, BLE-enabled Arduino/ESP32, etc.)
- Optional: a dedicated BLE sniffer (e.g., Ubertooth One, nRF52840 dongle)

### Software

```bash
sudo apt update
sudo apt install -y bluez bluetooth btscanner
```

Install bettercap:

```bash
sudo apt install -y bettercap
```

Install Python BLE tools:

```bash
pip3 install bleak
```

For mobile testing, install **nRF Connect** from Nordic Semiconductor on your Android or iOS device (available on app stores for free).

### Verify your Bluetooth adapter

```bash
hciconfig -a
```

You should see your adapter listed (e.g., `hci0`). If it shows `DOWN`, bring it up:

```bash
sudo hciconfig hci0 up
```

Verify BLE support:

```bash
sudo btmgmt info
```

Look for `le` in the supported settings.

> **Legal Notice:** Only test BLE devices you own. Interacting with other people's Bluetooth devices without permission may violate local laws.

---

## Part 1: Scanning for BLE Devices

### Step 1: Scan with bluetoothctl

The `bluetoothctl` utility is the modern replacement for `hcitool`.

```bash
bluetoothctl
```

Inside the interactive prompt:

```
[bluetooth]# scan on
```

You will see devices appear as they are discovered:

```
[NEW] Device AA:BB:CC:DD:EE:01 SmartLock-Pro
[NEW] Device AA:BB:CC:DD:EE:02 FitBand
[NEW] Device AA:BB:CC:DD:EE:03 LED-Bulb-Living
[NEW] Device AA:BB:CC:DD:EE:04 Unknown
```

Let the scan run for 30-60 seconds to find all nearby devices. Stop scanning:

```
[bluetooth]# scan off
```

List all discovered devices:

```
[bluetooth]# devices
```

Exit bluetoothctl:

```
[bluetooth]# exit
```

### Step 2: Scan with hcitool (legacy but useful)

```bash
sudo hcitool lescan
```

This displays BLE device addresses and names. Press `Ctrl-C` to stop.

For a more detailed scan that shows RSSI (signal strength):

```bash
sudo hcitool lescan --duplicates | head -30
```

### Step 3: Scan with bettercap

Bettercap provides a powerful BLE scanning module with more detail:

```bash
sudo bettercap -eval 'ble.recon on'
```

After a few seconds, view discovered devices:

```
> ble.show
```

**Expected output:**

```
+-----------------+-------------------+------+-------+------------+
|      RSSI       |      Address      | Name | Flags | Connectable|
+-----------------+-------------------+------+-------+------------+
| -45 dBm         | AA:BB:CC:DD:EE:01 | SmartLock-Pro | 0x06 | true |
| -62 dBm         | AA:BB:CC:DD:EE:02 | FitBand       | 0x06 | true |
| -78 dBm         | AA:BB:CC:DD:EE:03 | LED-Bulb      | 0x02 | true |
+-----------------+-------------------+------+-------+------------+
```

**What to observe:**
- **RSSI:** Signal strength helps estimate distance. Closer devices have higher (less negative) values.
- **Connectable:** If `true`, you can establish a GATT connection.
- **Flags:** Advertising flags indicate BLE capabilities.

To exit bettercap:

```
> exit
```

---

## Part 2: Enumerating GATT Services and Characteristics

GATT is the framework BLE devices use to expose data. Data is organized into:
- **Services:** Groups of related features (identified by UUID)
- **Characteristics:** Individual data points within a service (also identified by UUID)
- **Descriptors:** Metadata about characteristics

### Step 4: Connect and enumerate with gatttool

Replace `AA:BB:CC:DD:EE:01` with your target device's address.

#### Interactive mode

```bash
gatttool -b AA:BB:CC:DD:EE:01 -I
```

Inside the interactive prompt:

```
[AA:BB:CC:DD:EE:01][LE]> connect
Attempting to connect to AA:BB:CC:DD:EE:01
Connection successful
```

Discover all primary services:

```
[AA:BB:CC:DD:EE:01][LE]> primary
attr handle: 0x0001, end grp handle: 0x0007 uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x0008, end grp handle: 0x000b uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x000c, end grp handle: 0x0015 uuid: 0000fff0-0000-1000-8000-00805f9b34fb
```

**Common standard service UUIDs:**

| UUID | Service |
|------|---------|
| 0x1800 | Generic Access |
| 0x1801 | Generic Attribute |
| 0x180A | Device Information |
| 0x180F | Battery Service |
| 0x1812 | Human Interface Device |
| 0xFFF0 | Vendor-specific (custom) |

Discover all characteristics:

```
[AA:BB:CC:DD:EE:01][LE]> characteristics
handle: 0x0002, char properties: 0x02, char value handle: 0x0003, uuid: 00002a00-0000-1000-8000-00805f9b34fb
handle: 0x0004, char properties: 0x02, char value handle: 0x0005, uuid: 00002a01-0000-1000-8000-00805f9b34fb
handle: 0x000d, char properties: 0x0a, char value handle: 0x000e, uuid: 0000fff1-0000-1000-8000-00805f9b34fb
handle: 0x0010, char properties: 0x12, char value handle: 0x0011, uuid: 0000fff2-0000-1000-8000-00805f9b34fb
```

**Characteristic properties flags:**

| Bit | Property | Meaning |
|-----|----------|---------|
| 0x02 | Read | You can read this value |
| 0x04 | Write Without Response | Write without acknowledgment |
| 0x08 | Write | Write with acknowledgment |
| 0x10 | Notify | Device pushes updates to you |
| 0x20 | Indicate | Like notify, but with acknowledgment |
| 0x0A | Read + Write | Both read and write allowed |

### Step 5: Read characteristic values

Read the Device Name (UUID 0x2A00):

```
[AA:BB:CC:DD:EE:01][LE]> char-read-hnd 0x0003
Characteristic value/descriptor: 53 6d 61 72 74 4c 6f 63 6b
```

Decode the hex to ASCII:

```bash
echo "53 6d 61 72 74 4c 6f 63 6b" | xxd -r -p
# Output: SmartLock
```

Read all readable characteristics systematically:

```
[AA:BB:CC:DD:EE:01][LE]> char-read-hnd 0x0005
[AA:BB:CC:DD:EE:01][LE]> char-read-hnd 0x000e
[AA:BB:CC:DD:EE:01][LE]> char-read-hnd 0x0011
```

Record every value. Vendor-specific characteristics (UUID starting with `FFF`) often contain sensitive data like device state, configuration, or authentication tokens.

### Step 6: Enumerate with bettercap

Bettercap can also enumerate GATT:

```bash
sudo bettercap -eval 'ble.recon on'
```

Then enumerate a specific device:

```
> ble.enum AA:BB:CC:DD:EE:01
```

This outputs all services, characteristics, and their properties in a formatted table.

---

## Part 3: Reading and Writing Characteristics

### Step 7: Write to a characteristic

In gatttool interactive mode, write a value to a writable characteristic:

```
[AA:BB:CC:DD:EE:01][LE]> char-write-req 0x000e 01
Characteristic value was written successfully
```

This writes the byte `0x01` to handle `0x000e`. Common write patterns for IoT devices:

| Byte(s) | Common Meaning |
|---------|---------------|
| `01` | ON / Unlock / Enable |
| `00` | OFF / Lock / Disable |
| `FF` | Maximum value (brightness, volume) |

### Step 8: Subscribe to notifications

If a characteristic supports Notify (0x10), subscribe by writing `0x0100` to its Client Characteristic Configuration Descriptor (CCCD), which is typically at handle + 1:

```
[AA:BB:CC:DD:EE:01][LE]> char-write-req 0x0012 0100
```

Now the device will push updates to you:

```
Notification handle = 0x0011 value: 48 65 61 72 74 52 61 74 65 3a 37 32
```

Decode:

```bash
echo "48 65 61 72 74 52 61 74 65 3a 37 32" | xxd -r -p
# Output: HeartRate:72
```

### Step 9: Use a Python script for automated enumeration

Create a script using the `bleak` library for more sophisticated interaction:

```bash
cat << 'PYEOF' > /tmp/ble_enum.py
#!/usr/bin/env python3
"""Enumerate all GATT services and characteristics of a BLE device."""

import asyncio
import sys
from bleak import BleakClient, BleakScanner

async def enumerate_device(address):
    print(f"[*] Connecting to {address}...")
    async with BleakClient(address) as client:
        print(f"[+] Connected: {client.is_connected}")
        print(f"\n{'='*60}")
        print(f"GATT Services and Characteristics")
        print(f"{'='*60}")

        for service in client.services:
            print(f"\n[Service] {service.uuid} - {service.description}")
            for char in service.characteristics:
                props = ', '.join(char.properties)
                print(f"  [Char] {char.uuid} | Handle: {char.handle} | Props: {props}")

                # Attempt to read if readable
                if 'read' in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        hex_val = value.hex()
                        try:
                            ascii_val = value.decode('utf-8', errors='replace')
                        except Exception:
                            ascii_val = '(not UTF-8)'
                        print(f"         Value (hex): {hex_val}")
                        print(f"         Value (ascii): {ascii_val}")
                    except Exception as e:
                        print(f"         Read error: {e}")

                for desc in char.descriptors:
                    print(f"    [Desc] {desc.uuid} | Handle: {desc.handle}")

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <BLE_ADDRESS>")
    sys.exit(1)

asyncio.run(enumerate_device(sys.argv[1]))
PYEOF
```

Run it:

```bash
python3 /tmp/ble_enum.py AA:BB:CC:DD:EE:01
```

---

## Part 4: Identifying Security Weaknesses

### Step 10: Check for common BLE vulnerabilities

Work through this checklist for each BLE device you analyze:

#### 1. No pairing or bonding required

If you can connect and interact with characteristics without any pairing process, the device has no link-layer security.

**Test:** Simply connect with gatttool. If it works without prompting for a PIN or passkey, authentication is absent.

```bash
gatttool -b AA:BB:CC:DD:EE:01 -I -t random
> connect
# If "Connection successful" with no pairing prompt = no authentication
```

#### 2. Just Works pairing (no MITM protection)

Even if pairing is required, "Just Works" mode provides encryption but no authentication. An attacker can perform a man-in-the-middle attack during pairing.

**Indicators:**
- No PIN entry required during pairing
- No numeric comparison displayed
- No out-of-band channel used

#### 3. Static or predictable PINs

Some devices use a fixed PIN like `000000` or `123456`. Try common values if pairing is requested.

#### 4. Writable characteristics without authentication

**Critical security issue.** If sensitive characteristics (e.g., lock/unlock commands) can be written without prior authentication:

```
> char-write-req 0x000e 01
Characteristic value was written successfully
```

If the write succeeds and the device acts on it, any nearby attacker can send the same command.

#### 5. Sensitive data in advertisements

Some devices broadcast sensitive information in their advertising packets (visible to all nearby devices without connecting).

Use bettercap to inspect advertising data:

```
> ble.recon on
> ble.show
```

Look for device state, sensor readings, or identifiers in the advertisement payload.

#### 6. No replay protection

If a device accepts the same command bytes repeatedly without any nonce, counter, or session token, it is vulnerable to replay attacks.

**Test:** Capture a write command, disconnect, reconnect, and send the exact same bytes.

#### 7. Firmware update over BLE without verification

Check for a DFU (Device Firmware Update) service (UUID `0xFE59` for Nordic DFU or similar vendor-specific UUIDs). If firmware can be uploaded over BLE without signature verification, an attacker can flash malicious firmware.

---

## Part 5: Advanced -- BLE Sniffing with Ubertooth or nRF Sniffer

If you have a dedicated BLE sniffer, you can capture raw BLE packets from the air, including packets between two other devices.

### Using Ubertooth One

```bash
# Install Ubertooth tools
sudo apt install -y ubertooth

# Capture BLE packets and pipe to Wireshark
ubertooth-btle -f -c /tmp/ble_capture.pcap
```

Open the capture in Wireshark:

```bash
wireshark /tmp/ble_capture.pcap &
```

Use the display filter `btle` to see BLE link-layer packets.

### Using nRF Sniffer with Wireshark

1. Flash the nRF Sniffer firmware onto an nRF52840 dongle.
2. Install the Wireshark nRF Sniffer plugin.
3. Open Wireshark, select the nRF Sniffer interface.
4. Select the target device's address to follow its connection.

This lets you see the actual GATT read/write operations between a phone app and the target device, which is invaluable for understanding proprietary protocols.

---

## Analysis Checklist

After completing the lab, document your findings using this template:

```
## BLE Device Assessment: [Device Name]
### Address: AA:BB:CC:DD:EE:01

### Pairing
- Pairing required: Yes / No
- Pairing method: Just Works / Passkey / Numeric Comparison / OOB
- MITM protection: Yes / No

### GATT Services
| Service UUID | Description | Custom? |
|-------------|-------------|---------|
| 0x1800 | Generic Access | No |
| 0xFFF0 | Vendor Custom | Yes |

### Writable Characteristics (Security-Relevant)
| Handle | UUID | Auth Required? | Effect |
|--------|------|---------------|--------|
| 0x000e | 0xFFF1 | No | Unlocks device |

### Vulnerabilities Found
1. No authentication required to connect
2. Lock/unlock command writable by any connected client
3. Static PIN used for pairing (000000)
4. Sensor data broadcast in advertising packets
```

---

## Review Questions

1. What is the maximum range of BLE, and how does this affect the practical risk of BLE attacks?
2. Explain the difference between BLE Legacy Pairing and LE Secure Connections. Which is more secure and why?
3. Why is "Just Works" pairing considered insecure even though it provides encryption?
4. How could a BLE smart lock implement proper authentication at the application layer, even without secure pairing?
5. What is a GATT spoofing attack, and how could it be used to intercept sensitive data?

---

## Cleanup

```bash
# Bring down the Bluetooth adapter if desired
sudo hciconfig hci0 down

# Remove temporary files
rm -f /tmp/ble_enum.py /tmp/ble_capture.pcap
```

## Next Steps

- Try the **Challenge: Unlock the BLE Lock** to apply these skills in a CTF scenario.
- Experiment with BLE spoofing using bettercap: `ble.recon on; ble.clone AA:BB:CC:DD:EE:01`.
- Explore BLE Man-in-the-Middle attacks with GATTacker or BtleJuice (in a controlled lab only).
