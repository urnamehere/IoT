---
title: "Logic Analyzers"
level: Intermediate
description: "Decode digital communications between chips"
order: 2
---

# Logic Analyzers

## What Do Logic Analyzers Capture?

A logic analyzer captures digital signals over time. Unlike an oscilloscope, which shows analog voltage waveforms, a logic analyzer records whether a signal is high (1) or low (0) at each sample point. This makes it ideal for understanding how chips on an IoT device communicate with each other.

With a logic analyzer you can:

- **Decode UART traffic** between a processor and a radio module
- **Capture SPI communication** between a CPU and flash memory (potentially extracting firmware)
- **Monitor I2C bus traffic** between sensors and controllers
- **Reverse-engineer proprietary protocols** by observing timing and bit patterns
- **Debug timing issues** in communication between components

In IoT security research, logic analyzers are essential when you need to go beyond the serial console and understand what data flows between components on the circuit board.

## Hardware Options

### Budget: Saleae Logic Clones / FX2-Based Analyzers ($8-20)

These devices are based on the Cypress FX2LP chip and are widely available on Amazon and AliExpress, often marketed as "24MHz 8-channel logic analyzers."

**Specifications:**
- 8 channels
- Up to 24 MHz sampling rate (often only reliable at 12 MHz)
- USB 2.0 interface
- Supported by sigrok/PulseView (open-source)

**Pros:**
- Extremely cheap ($8-15)
- Good enough for UART (up to ~1 Mbps), I2C (up to 400 kHz), and slower SPI
- Widely supported by open-source software

**Cons:**
- Limited sampling rate means you cannot reliably capture fast SPI (10+ MHz)
- No analog capability
- Build quality varies; some arrive dead
- Limited input voltage range (typically 0-5V)

**Best for:** Beginners, UART decoding, slow I2C/SPI, learning the fundamentals.

### Mid-Range: DSLogic Plus ($150)

- 16 channels
- Up to 400 MHz sampling rate
- USB 2.0 with onboard memory buffer
- Cross-platform software (DSView, also works with sigrok)
- Good balance of price and performance

### Professional: Saleae Logic Pro 8/16 ($500-1,000)

**Specifications:**
- 8 or 16 channels
- Up to 100 MHz digital, 50 MS/s analog
- USB 3.0 interface
- Mixed-signal capability (digital + analog simultaneously)

**Pros:**
- Excellent build quality and reliability
- Superb software (Saleae Logic 2) with protocol decoders, measurements, and export
- Analog channels let you see signal integrity issues
- Higher sampling rates handle fast SPI and other high-speed protocols
- Great customer support and regular software updates

**Cons:**
- Expensive for hobbyists
- May be overkill for basic UART/I2C work

**Best for:** Professional security researchers, consulting work, capturing high-speed protocols.

### Recommendation

Start with a **$10 FX2-based analyzer** and sigrok/PulseView. When you hit its limitations (usually when dealing with fast SPI or needing reliable captures under time pressure), invest in a Saleae or DSLogic.

## Software: sigrok and PulseView

[sigrok](https://sigrok.org/) is the open-source signal analysis framework. PulseView is its graphical frontend. Together they support dozens of hardware devices and over 100 protocol decoders.

### Installation

```bash
# Debian/Ubuntu
sudo apt install sigrok pulseview

# Fedora
sudo dnf install sigrok-cli pulseview

# macOS
brew install sigrok-cli pulseview

# Windows
# Download the installer from https://sigrok.org/wiki/Downloads
```

### Configuring udev Rules (Linux)

Without udev rules, you need root to access the analyzer:

```bash
# Create udev rules for common logic analyzers
sudo tee /etc/udev/rules.d/60-sigrok.rules << 'RULES'
# FX2-based analyzers (Saleae clones, etc.)
SUBSYSTEM=="usb", ATTRS{idVendor}=="0925", ATTRS{idProduct}=="3881", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b4", ATTRS{idProduct}=="8613", MODE="0666"
# Saleae Logic
SUBSYSTEM=="usb", ATTRS{idVendor}=="21a9", MODE="0666"
# DSLogic
SUBSYSTEM=="usb", ATTRS{idVendor}=="2a0e", MODE="0666"
RULES

sudo udevadm control --reload-rules
sudo udevadm trigger
```

### PulseView Basics

1. **Launch PulseView:** `pulseview` from the terminal
2. **Select your device** from the dropdown (e.g., "fx2lafw" for FX2-based analyzers)
3. **Set the sample rate:** Start with 1 MHz for UART, 4-10 MHz for I2C, 10-24 MHz for SPI
4. **Set the sample count:** 1M-10M samples is usually sufficient
5. **Click "Run"** to start capturing
6. **Add protocol decoders** via the decoder menu (yellow/green icon)

### Command-Line Usage with sigrok-cli

```bash
# List connected devices
sigrok-cli --scan

# Capture 1 million samples at 4 MHz from an fx2lafw device
sigrok-cli -d fx2lafw -c samplerate=4000000 --samples 1000000 -o capture.sr

# Capture and decode UART on channel D0 at 115200 baud
sigrok-cli -d fx2lafw -c samplerate=1000000 --samples 1000000 \
  -P uart:baudrate=115200:rx=D0

# Capture and decode SPI on channels D0-D3
sigrok-cli -d fx2lafw -c samplerate=12000000 --samples 2000000 \
  -P spi:clk=D0:miso=D1:mosi=D2:cs=D3

# Capture and decode I2C on channels D0-D1
sigrok-cli -d fx2lafw -c samplerate=4000000 --samples 1000000 \
  -P i2c:scl=D0:sda=D1
```

## Decoding Common IoT Protocols

### UART

UART is asynchronous and uses two data lines (TX and RX). To decode it:

1. Connect one channel to the TX line you want to monitor
2. Connect GND to the device's ground
3. Set sample rate to at least 4x the baud rate (e.g., 460800 Hz for 115200 baud)
4. In PulseView, add the "UART" decoder and configure:
   - **RX/TX:** Select the correct channel
   - **Baud rate:** 115200 (most common) or auto-detect
   - **Data bits:** 8
   - **Parity:** None
   - **Stop bits:** 1

**What to look for:** ASCII text (shell commands, log output), binary protocol data, credentials passed in plaintext.

### SPI (Serial Peripheral Interface)

SPI uses four signals. Connect channels to:

| Signal | Name | Description |
|--------|------|-------------|
| CLK/SCK | Serial Clock | Clock signal from master |
| MOSI | Master Out, Slave In | Data from CPU to peripheral |
| MISO | Master In, Slave Out | Data from peripheral to CPU |
| CS/SS | Chip Select | Active low, selects the target device |

**Sample rate:** At least 4x the SPI clock frequency. If SPI runs at 10 MHz, sample at 40+ MHz (this is where cheap analyzers struggle).

**What to look for in IoT security:**
- SPI flash read commands (0x03) during boot -- this is the device reading its firmware
- Write commands to flash memory during updates
- Data being written to external storage

**Extracting firmware via SPI capture:**

```bash
# Capture SPI traffic during boot with sigrok-cli
sigrok-cli -d fx2lafw -c samplerate=12000000 --samples 10000000 \
  -P spi:clk=D0:miso=D1:mosi=D2:cs=D3 \
  -A spi=miso-data > spi_dump.txt
```

### I2C (Inter-Integrated Circuit)

I2C uses two signals:

| Signal | Name | Description |
|--------|------|-------------|
| SCL | Serial Clock | Clock line |
| SDA | Serial Data | Bidirectional data line |

**Sample rate:** At least 4x the I2C clock speed. Standard mode runs at 100 kHz, fast mode at 400 kHz.

In PulseView, add the "I2C" decoder and assign SCL and SDA to the correct channels. You will see:

- Device addresses (7-bit, shown in hex)
- Read vs write operations
- The data bytes being transferred

**What to look for:** EEPROM reads (addresses 0x50-0x57 are common), sensor data, cryptographic key material stored in secure elements.

## Physical Setup Guide

### Step 1: Identify the Signals

Before connecting the logic analyzer, you need to know which pins carry which signals. Use a multimeter to find ground, then refer to chip datasheets or use the logic analyzer itself to identify clock lines (they have regular periodic signals).

### Step 2: Connect Ground First

**Always connect the logic analyzer's GND to the target device's GND.** This establishes a common voltage reference. Without a ground connection, the analyzer cannot accurately read logic levels.

### Step 3: Connect Signal Channels

Use short jumper wires or hook probes to connect analyzer channels to the signals of interest. Keep wires as short as possible to reduce noise, especially at higher frequencies.

### Step 4: Configure and Capture

- Set the sample rate appropriately for the protocol
- Set a trigger if needed (e.g., trigger on falling edge of CS for SPI)
- Capture enough samples to see complete transactions

### Step 5: Add Decoders and Analyze

Apply the appropriate protocol decoder in PulseView, verify the decoded output makes sense, and export the results.

## Practical Examples

### Example 1: Sniffing Communication Between a Router CPU and Its SPI Flash

Many routers store their firmware on an external SPI flash chip. By connecting a logic analyzer to the SPI lines between the CPU and flash, you can capture the firmware as it is read during boot.

1. Identify the SPI flash chip (usually a small 8-pin SOIC package, labeled 25Q64, W25Q128, etc.)
2. Look up the pinout in the datasheet
3. Connect logic analyzer channels to CLK, MOSI, MISO, and CS
4. Power on the router and capture
5. Decode the SPI traffic and extract the MISO data (flash read responses)

### Example 2: Monitoring I2C Sensor Data on a Smart Home Device

A smart thermostat might use I2C to communicate with temperature and humidity sensors.

1. Identify the I2C pull-up resistors on the PCB (usually 4.7k ohm near the sensor)
2. Connect to SDA and SCL
3. Capture traffic and decode
4. Map device addresses to specific sensors using the I2C address table from datasheets

### Example 3: Capturing UART Debug Output at an Unknown Baud Rate

1. Connect one channel to the suspected UART TX line
2. Capture at a high sample rate (e.g., 4 MHz)
3. Look at the shortest pulse width in the capture
4. Calculate: baud rate = 1 / (shortest pulse width in seconds)
5. Apply the UART decoder with the calculated baud rate

## Tips for Better Captures

- **Use the highest sample rate your analyzer supports** for the protocol you are capturing. Undersampling causes decoding errors.
- **Set triggers** to avoid capturing long periods of idle bus traffic. Trigger on the chip select going low (SPI) or on a start condition (I2C).
- **Label your channels** in PulseView for clarity when working with multiple signals.
- **Save captures** as .sr files so you can revisit them later without needing the hardware setup.
- **Use sigrok-cli for scripted captures** when you need to repeat the same capture many times (e.g., across multiple boot cycles).
- **Check for crosstalk** if you see unexpected transitions. Rerouting wires or shortening them usually fixes this.
