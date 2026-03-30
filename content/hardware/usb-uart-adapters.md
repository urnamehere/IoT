---
title: "USB-UART Adapters"
level: Beginner
description: "Your first hardware hacking tool - connecting to serial consoles"
order: 1
---

# USB-UART Adapters

## What Are USB-UART Adapters?

A USB-UART adapter (also called a USB-to-serial or USB-to-TTL adapter) is a small board that converts USB signals from your computer into UART (Universal Asynchronous Receiver/Transmitter) serial signals. UART is the most common debug interface found on IoT devices. Manufacturers leave serial consoles exposed on circuit boards during development for debugging, and they frequently ship in production hardware without being disabled.

When you connect to a device's UART interface, you often get:

- A boot log showing the entire startup sequence
- A root shell with no authentication
- A login prompt (sometimes with default credentials)
- Debug output revealing firmware versions, memory addresses, and configuration details

This makes USB-UART adapters the single most important tool for anyone starting in IoT hardware hacking.

## Popular Models

### CP2102 (Silicon Labs)

- **Price:** $2-5
- **Max baud rate:** 1,000,000 bps
- **Voltage levels:** 3.3V (most common versions)
- **Driver support:** Excellent on all platforms
- **Notes:** The most widely recommended beginner adapter. Many boards come with 6-pin headers. Look for versions with a 3.3V/5V voltage selector jumper.

### FT232RL (FTDI)

- **Price:** $5-15 (genuine), $2-4 (clones)
- **Max baud rate:** 3,000,000 bps
- **Voltage levels:** 3.3V and 5V selectable
- **Driver support:** Excellent, but FTDI once released a driver update that bricked clones
- **Notes:** Industry standard for reliability. If buying, get a genuine FTDI chip from a reputable source. The FT232H variant also supports SPI, I2C, and JTAG.

### CH340G (WCH)

- **Price:** $1-3
- **Max baud rate:** 2,000,000 bps
- **Voltage levels:** 3.3V and 5V
- **Driver support:** Good on Linux (built-in), requires driver install on macOS/Windows
- **Notes:** Cheapest option. Works fine for most tasks. Very common on budget Arduino clones.

### Recommendation for Beginners

Buy a **CP2102 module with a 3.3V/5V jumper** ($3-5 on Amazon or AliExpress). It covers 90% of use cases. Later, consider an **FT232H** breakout board for its multi-protocol support.

## Wiring: TX, RX, and GND

UART requires a minimum of three connections:

| Adapter Pin | Device Pin | Purpose |
|-------------|------------|---------|
| TX (Transmit) | RX (Receive) | Adapter sends data to device |
| RX (Receive) | TX (Transmit) | Device sends data to adapter |
| GND (Ground) | GND (Ground) | Common ground reference |

**Critical rule: TX connects to RX, and RX connects to TX.** This is a crossover connection. The adapter's transmit line feeds the device's receive line and vice versa.

### Wiring Diagram

```
USB-UART Adapter          IoT Device PCB
┌──────────────┐          ┌──────────────┐
│           TX ├──────────┤ RX           │
│           RX ├──────────┤ TX           │
│          GND ├──────────┤ GND          │
│          VCC │   (DO    │ VCC          │
│              │   NOT    │              │
│              │ CONNECT  │              │
│              │ BLINDLY) │              │
└──────────────┘          └──────────────┘
```

### VCC: When to Connect and When Not To

- **Do NOT connect VCC** if the target device has its own power supply (plugged in, battery, etc.). Connecting VCC in this case can damage either the device or the adapter.
- **Connect VCC only** if you need to power the target board from the adapter AND you are certain of the voltage requirements.
- When in doubt, **leave VCC disconnected** and power the target device normally.

## Voltage Levels: 3.3V vs 5V

This is where beginners damage hardware. UART signals swing between 0V (logic low) and a reference voltage (logic high). The two common levels are:

- **3.3V logic:** Most modern IoT devices, ESP8266/ESP32, Raspberry Pi, ARM-based routers
- **5V logic:** Arduino Uno, some older devices, some industrial equipment

**Sending 5V signals into a 3.3V device can permanently destroy the chip.** Always check the device's operating voltage before connecting.

### How to Determine the Voltage Level

1. **Check the datasheet** for the main processor on the device
2. **Measure with a multimeter:** With the device powered on, measure the voltage on a known UART TX pin relative to ground. If it reads around 3.3V, use 3.3V mode.
3. **Look at the voltage regulator** on the PCB. If you see a 3.3V regulator near the processor, the UART is almost certainly 3.3V.

### Setting Your Adapter's Voltage

- **CP2102 with jumper:** Move the jumper to the correct position
- **FT232RL breakout:** Usually has a solder jumper or switch
- **If no selector exists:** Buy a version that matches your target, or use a logic level converter ($1-2)

## Software Setup

### Linux

Most adapters work out of the box. The device appears as `/dev/ttyUSB0` (or `/dev/ttyACM0`).

```bash
# Check if the adapter is detected
dmesg | tail -20
# Look for lines like: "cp210x converter now attached to ttyUSB0"

# Install a serial terminal
sudo apt install minicom screen picocom

# Connect using screen (simplest)
sudo screen /dev/ttyUSB0 115200

# Connect using minicom (more features)
sudo minicom -D /dev/ttyUSB0 -b 115200

# Connect using picocom (recommended - clean and simple)
sudo picocom -b 115200 /dev/ttyUSB0

# Fix permission issues (add yourself to the dialout group)
sudo usermod -aG dialout $USER
# Log out and back in for this to take effect
```

### macOS

```bash
# Install drivers if needed (CH340 requires a driver, CP2102/FTDI usually work)
# Download CH340 driver from wch-ic.com

# The device appears as /dev/tty.usbserial-XXXX or /dev/tty.SLAB_USBtoUART
ls /dev/tty.usb*

# Install a serial terminal
brew install minicom picocom

# Connect
picocom -b 115200 /dev/tty.usbserial-0001
```

### Windows

1. Install the appropriate driver (CP2102, FTDI, or CH340 from the manufacturer's website)
2. Open Device Manager and note the COM port number (e.g., COM3)
3. Use **PuTTY** (free): Select "Serial," enter the COM port and baud rate
4. Or use **Tera Term** (free, popular in hardware circles)

### Common Baud Rates

Most IoT devices use one of these baud rates:

| Baud Rate | Common Usage |
|-----------|-------------|
| 9600 | Some sensors, GPS modules |
| 38400 | Some older devices |
| 57600 | Some embedded systems |
| **115200** | **Most common for IoT devices** |
| 230400 | Some newer devices |
| 460800 | ESP32 boot output |
| 921600 | High-speed debug output |

If you connect and see garbage characters, you probably have the wrong baud rate. Try 115200 first, then 9600, then others.

**Auto-detecting baud rate:** Use `baudrate.py` from the [devttys0 toolkit](https://github.com/devttys0/baudrate):

```bash
python baudrate.py -p /dev/ttyUSB0
```

## Common Use Cases in IoT Security

### 1. Getting a Root Shell

Many IoT devices drop you into a root shell via UART with zero authentication:

```
U-Boot 2014.04 (Oct 15 2019)
...
Starting kernel ...
...
/ #       <-- root shell, no login required
```

### 2. Interrupting the Bootloader

Press a key during boot (often Enter, Space, or a specific key sequence) to enter the bootloader (usually U-Boot):

```
Hit any key to stop autoboot: 3
=> help
=> printenv      # Show all environment variables
=> setenv bootargs "console=ttyS0,115200 single"  # Boot to single-user mode
```

### 3. Capturing Boot Logs

Even if the shell is locked down, the boot log often reveals:

- Kernel version and compile flags
- Filesystem mount points
- Network configuration
- Running services
- Hardcoded credentials in startup scripts

### 4. Firmware Recovery

When a device is bricked, UART access combined with the bootloader often provides a way to reflash firmware via TFTP or XMODEM.

## Safety Tips

1. **Never connect VCC unless you know exactly what you are doing.** Power the target device with its normal power supply.
2. **Always verify voltage levels** before connecting. A 5V signal on a 3.3V pin destroys silicon.
3. **Connect GND first** before TX/RX to establish a common reference.
4. **Do not short pins together.** Use individual jumper wires, not ribbon cables that might bridge adjacent pins.
5. **Start with the device powered off,** make your connections, then power on the device to capture the full boot log.
6. **Use header pins or test clips** rather than holding bare wires against pads. A hook probe or pogo pin jig makes connections reliable and avoids accidental shorts.
7. **Keep your adapter away from high-voltage sections** of the PCB (mains power, PoE, motor drivers).

## Recommended Purchases

| Item | Price | Notes |
|------|-------|-------|
| CP2102 USB-UART (3.3V/5V) | $3-5 | Primary adapter |
| Dupont jumper wires (M-F and F-F) | $3-5 | For making connections |
| Hook clip test leads | $5-8 | Grab small test points without soldering |
| Breadboard | $3-5 | Useful for organizing connections |
| Pin headers (2.54mm) | $2-3 | Solder onto unpopulated UART pads |

**Total starter kit cost: under $20.**
