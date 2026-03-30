---
title: "Lab: UART Serial Console Access"
level: Intermediate
description: "Identify UART pins and connect to a device's serial console"
estimated_time: "45 minutes"
tools:
  - Multimeter
  - USB-UART adapter
  - minicom/screen
objectives:
  - Identify UART pins on a PCB
  - Determine baud rate
  - Connect and interact with the serial console
---

# Lab: UART Serial Console Access

## Overview

UART (Universal Asynchronous Receiver/Transmitter) is a serial communication interface found on nearly every IoT device's circuit board. Manufacturers use it during development and debugging, and they frequently leave the UART pads accessible in production hardware. Connecting to UART can give you a root shell, bootloader access, and full visibility into the device's boot process.

In this lab you will learn to identify UART pins on a PCB, determine the correct baud rate, and establish a serial console session.

## Prerequisites

### Hardware

- An IoT device to examine (old router, IP camera, smart plug, etc.)
- A digital multimeter (DMM)
- A USB-to-UART adapter (also called USB-to-TTL serial adapter). Common chipsets:
  - **CP2102** (recommended, widely compatible)
  - **FT232RL** (FTDI-based, reliable)
  - **CH340G** (inexpensive, works well on Linux)
- Jumper wires (female-to-female or female-to-male, depending on your header type)
- Soldering iron and solder (only if the UART pads have no header installed)

### Software

- A Linux machine with USB support
- `minicom` or `screen` installed
- `baudrate.py` or `stty` for baud rate detection

```bash
sudo apt update
sudo apt install -y minicom screen picocom
```

> **Safety Warning:** Always disconnect the device from mains power before working on the PCB. Use only low-voltage (3.3V or 5V) USB-UART adapters. Never connect your adapter's VCC pin unless you are certain of the voltage level.

---

## Step 1: Open the Device and Locate the PCB

1. Remove screws from the device enclosure (check under rubber feet and labels).
2. Carefully separate the casing. Use a plastic spudger to avoid damaging clips.
3. Locate the main circuit board.

**What to look for on the PCB:**

UART headers typically appear as a row of 3 to 5 pads or pins, often near the edge of the board or close to the main processor. Common patterns include:

- **4-pin header:** VCC, GND, TX, RX
- **3-pin header:** GND, TX, RX (no VCC)
- **Unpopulated through-holes:** A row of holes with no pins soldered in
- **Test pads:** Labeled TP1, TP2, etc., or J1, J2, etc.

Look for silkscreen labels on the PCB such as:
- `TX`, `RX`, `GND`, `VCC`, `3V3`
- `UART`, `CONSOLE`, `DEBUG`, `SERIAL`
- `J1`, `JP1`, `HDR1`

---

## Step 2: Identify Pins with a Multimeter

If the pins are not labeled, use your multimeter to identify each one.

### Find Ground (GND)

1. Set your multimeter to **continuity mode** (the beep mode).
2. Place one probe on a known ground point. This is usually:
   - The outer metal shield of a USB port
   - The negative terminal of a large capacitor
   - Any large copper plane on the board
3. Touch the other probe to each of the suspected UART pins.
4. The pin that gives a continuity beep is **GND**.

### Find VCC (if present)

1. Power on the device (be careful with exposed PCB).
2. Set your multimeter to **DC voltage mode**.
3. Place the black probe on the identified GND pin.
4. Touch the red probe to each remaining pin.
5. A pin showing a steady **3.3V** or **5.0V** is likely **VCC**.

> **Important:** Note whether VCC is 3.3V or 5V. Your USB-UART adapter must match this voltage. Connecting a 5V adapter to a 3.3V device can damage it.

### Find TX (Transmit)

1. Keep the device powered on.
2. With the multimeter in DC voltage mode (black probe on GND):
3. Touch each remaining pin. The **TX** pin will show a fluctuating voltage between 0V and 3.3V (or 5V), especially during boot when the device outputs serial data.
4. TX often rests at a high logic level (3.3V) when idle.

**Alternative method:** Use an oscilloscope or logic analyzer if available. TX will show clear data waveforms during boot.

### Find RX (Receive)

1. The remaining pin is most likely **RX**.
2. RX typically shows a steady high voltage (pulled up) or floats near the logic high level.
3. RX will not show data activity unless something is transmitting to it.

### Pin identification summary

| Pin | Multimeter Behavior | Notes |
|-----|---------------------|-------|
| GND | Continuity with ground plane | Always identify first |
| VCC | Steady 3.3V or 5.0V | Do NOT connect this to your adapter |
| TX  | Fluctuates during boot, high when idle | Connect to adapter's RX |
| RX  | Steady high or floating | Connect to adapter's TX |

---

## Step 3: Connect the USB-UART Adapter

### Wiring

Make the following connections with jumper wires:

| Device Pin | Adapter Pin | Notes |
|-----------|-------------|-------|
| GND | GND | Always connect ground first |
| TX | RX | Device transmit to adapter receive |
| RX | TX | Device receive from adapter transmit |
| VCC | -- | **Do NOT connect VCC.** Power the device from its own supply. |

> **Critical:** TX connects to RX and RX connects to TX. This is a crossover connection. If you connect TX-to-TX you will see no output.

### Plug in the adapter

Connect the USB-UART adapter to your Linux machine. Verify it is detected:

```bash
dmesg | tail -10
```

You should see something like:

```
usb 1-1: cp210x converter now attached to ttyUSB0
```

Confirm the device node exists:

```bash
ls -la /dev/ttyUSB0
```

If it appears as `/dev/ttyACM0` instead, use that path in subsequent commands.

### Set permissions

```bash
sudo chmod 666 /dev/ttyUSB0
# Or add your user to the dialout group (persistent):
sudo usermod -aG dialout $USER
```

---

## Step 4: Determine the Baud Rate

The baud rate must match between the device and your terminal. If it is wrong, you will see garbled characters.

### Common IoT baud rates

Try these in order (most common first):

| Baud Rate | Prevalence |
|-----------|-----------|
| **115200** | Most common for modern IoT devices |
| **9600** | Common for simple microcontrollers |
| **57600** | Occasionally used |
| **38400** | Less common |
| **19200** | Older devices |
| **230400** | High-speed debug consoles |
| **1500000** | Some newer SoCs (less common) |

### Method 1: Trial and error with minicom

Start with 115200 (most likely):

```bash
minicom -D /dev/ttyUSB0 -b 115200
```

Power cycle the device (unplug and replug its power). If you see readable boot messages, you have the correct baud rate. If you see garbage characters, exit minicom (`Ctrl-A`, then `X`) and try the next rate:

```bash
minicom -D /dev/ttyUSB0 -b 9600
```

### Method 2: Automated detection with baudrate.py

Download and use the baudrate detection script:

```bash
wget https://raw.githubusercontent.com/devttys0/baudrate/master/baudrate.py -O /tmp/baudrate.py
sudo python3 /tmp/baudrate.py -p /dev/ttyUSB0
```

This tool cycles through common baud rates and lets you visually confirm which one produces readable output.

### Method 3: Logic analyzer

If you have a USB logic analyzer (e.g., Saleae Logic), connect it to the TX pin and capture data during device boot. The analyzer software can auto-detect the baud rate from the waveform timing.

---

## Step 5: Connect and Interact with the Serial Console

### Using minicom

```bash
minicom -D /dev/ttyUSB0 -b 115200
```

**Minicom keyboard shortcuts:**
- `Ctrl-A`, then `Z` -- Help menu
- `Ctrl-A`, then `X` -- Exit
- `Ctrl-A`, then `L` -- Capture to file
- `Ctrl-A`, then `E` -- Toggle local echo

To log the entire session to a file:

```bash
minicom -D /dev/ttyUSB0 -b 115200 -C /tmp/uart_log.txt
```

### Using screen

```bash
screen /dev/ttyUSB0 115200
```

**Screen keyboard shortcuts:**
- `Ctrl-A`, then `\` -- Exit and kill session
- `Ctrl-A`, then `H` -- Toggle logging to `screenlog.0`

### Using picocom

```bash
picocom -b 115200 /dev/ttyUSB0
```

**Picocom keyboard shortcuts:**
- `Ctrl-A`, then `Ctrl-X` -- Exit

---

## Step 6: Interact with the Boot Process

Power cycle the device while your serial console is connected. You should see:

### Bootloader output

```
U-Boot 1.1.3 (Oct 15 2018)
Board: Ralink APSoC DRAM: 32 MB
relocate_code Pointer at: 81fb0000
flash manufacture id: ef, device id 40 17
...
Hit any key to stop autoboot: 3
```

**Action:** Press any key quickly to interrupt the boot process and enter the bootloader shell. This is often U-Boot on embedded Linux devices.

### U-Boot commands to try

```bash
# Print environment variables (may contain credentials or network config)
printenv

# Show boot arguments
bootargs

# List flash partitions
mtdparts

# Boot from a different source (e.g., TFTP)
tftpboot
```

### Linux boot messages

If you do not interrupt the bootloader, the device continues to Linux:

```
Linux version 2.6.36 (builder@server) ...
...
Please press Enter to activate this console.
```

### Getting a shell

- Many devices drop you directly into a root shell after boot.
- Some present a login prompt. Try common default credentials:
  - `root` / (empty password)
  - `root` / `root`
  - `admin` / `admin`
  - `root` / `password`
  - Check the device manufacturer's documentation for defaults.

---

## Step 7: Explore the Running System

Once you have a shell, gather information:

```bash
# Check who you are
whoami
id

# View running processes
ps aux

# Check network configuration
ifconfig
ip addr

# View mounted filesystems
mount
df -h

# Read configuration files
cat /etc/passwd
cat /etc/shadow

# Look for interesting files
find / -name '*.conf' 2>/dev/null
find / -name '*.key' -o -name '*.pem' 2>/dev/null

# Check for listening services
netstat -tlnp

# View the kernel command line
cat /proc/cmdline

# Check firmware version
cat /etc/version 2>/dev/null
cat /etc/firmware_version 2>/dev/null
```

---

## Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| No output at all | Wrong pins, wrong baud rate, or TX/RX swapped | Double-check wiring; swap TX and RX; try other baud rates |
| Garbled characters | Wrong baud rate | Try all common baud rates |
| Output but no input accepted | RX not connected or wrong pin | Verify RX wiring |
| Adapter not detected | Driver issue | Install `cp210x`, `ftdi_sio`, or `ch341` driver |
| Device resets when connecting | VCC connected or voltage mismatch | Disconnect VCC; verify voltage levels (3.3V vs 5V) |
| Only see boot messages, then nothing | Console disabled after boot | Try interrupting bootloader; check if `console=` kernel arg is set |

---

## Review Questions

1. Why do manufacturers leave UART accessible on production devices? What are the risks?
2. What is the difference between UART, SPI, I2C, and JTAG? When would you use each for hardware hacking?
3. Why should you never connect the VCC pin from your adapter to the target device?
4. What can an attacker do with bootloader (U-Boot) access that they cannot do from a normal user shell?
5. How can a manufacturer protect against UART-based attacks?

---

## Cleanup

- Disconnect all jumper wires from the target device.
- Safely close the device enclosure.
- Remove temporary files:

```bash
rm -f /tmp/uart_log.txt /tmp/baudrate.py
```

## Next Steps

- Proceed to **Lab: BLE Device Reconnaissance** to explore wireless IoT attack surfaces.
- Try connecting UART to a different device and compare the boot process.
- Explore JTAG connections for deeper hardware debugging access.
