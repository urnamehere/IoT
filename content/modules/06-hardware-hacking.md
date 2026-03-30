---
title: "Hardware Hacking"
order: 6
level: Intermediate
description: "Physical interfaces, debug ports, and hardware-level attacks"
estimated_time: "120 minutes"
prerequisites:
  - "Module 3: Lab Setup"
  - "Module 5: Firmware Analysis"
related_labs:
  - "lab-uart-connection"
---

# Module 6: Hardware Hacking

## Introduction

Hardware hacking is the practice of interacting with the physical components of an IoT device to extract information, gain access, or modify its behavior. While software-only analysis can reveal many vulnerabilities, physical access to the hardware opens an entirely new attack surface. Manufacturers often leave debug interfaces enabled, use unprotected flash memory, and fail to implement tamper detection -- all of which a security researcher can exploit.

This module covers the essential hardware hacking skills for IoT security research, from visual PCB inspection to reading flash chips and interfacing with debug ports.

---

## Safety Precautions

Before working with hardware, keep these safety guidelines in mind:

- **Disconnect power** before probing or soldering.
- **Use ESD protection** -- wear an anti-static wrist strap or touch a grounded metal surface regularly.
- **Be cautious with mains voltage** -- some IoT devices (smart plugs, smart switches) contain mains AC voltage internally. Never probe a device that is connected to mains power.
- **Work in a well-ventilated area** when soldering. Use a fume extractor.
- **Wear safety glasses** when desoldering or cutting PCB traces.

---

## Essential Hardware Tools

| Tool                        | Purpose                                    | Approximate Cost |
|-----------------------------|--------------------------------------------|------------------|
| Multimeter                  | Measuring voltage, continuity, resistance  | $20 - $50        |
| USB-UART adapter (FTDI/CP2102) | Serial console connection               | $5 - $15         |
| Logic analyzer (Saleae or clone) | Decoding digital protocols             | $10 - $500       |
| Bus Pirate                  | Multi-protocol interface tool              | $30 - $40        |
| SPI flash programmer (CH341A) | Reading/writing SPI flash chips          | $5 - $10         |
| Soldering iron              | Attaching wires, desoldering components    | $30 - $100       |
| Hot air rework station      | Removing/replacing surface-mount parts     | $50 - $200       |
| Magnifying glass / microscope | Inspecting tiny PCB components           | $20 - $100       |
| JTAG debugger (J-Link, ST-Link) | On-chip debugging                      | $20 - $400       |
| Flux and solder wire        | Soldering consumables                      | $10 - $20        |

---

## PCB Inspection and Component Identification

The first step in hardware hacking is opening the device and inspecting the printed circuit board (PCB).

### Opening the Device

- Look for screws (often hidden under rubber feet or stickers).
- Use plastic spudgers to pry open snap-fit enclosures without damage.
- Some devices use tamper-evident seals -- document these before breaking them.

### Identifying Key Components

Examine the PCB and identify:

1. **Main SoC/MCU** -- the primary processor. Note the manufacturer and part number printed on the chip package.
2. **Flash memory** -- stores the firmware. Look for chips labeled with manufacturers like Winbond (25Qxx), Macronix (MX25Lxx), or Spansion.
3. **RAM** -- volatile memory, usually near the SoC.
4. **Power regulators** -- voltage regulators that step down input voltage. Identify voltage rails (3.3V, 1.8V, 5V).
5. **Antenna / RF module** -- Wi-Fi, Bluetooth, Zigbee, or LoRa radios.
6. **Debug headers** -- unpopulated pin headers or test points for UART, JTAG, or SWD.

```
Tip: Photograph the PCB (both sides) at high resolution before you begin
probing. You can annotate the photos later to document your findings.
Search for chip part numbers online to find datasheets -- these reveal
pinouts, operating voltages, and communication interfaces.
```

### Reading Chip Markings

Chip markings follow manufacturer-specific conventions. Here are common patterns:

| Chip Marking Example | Manufacturer | Type                   |
|----------------------|--------------|------------------------|
| W25Q128JVSQ          | Winbond      | 128Mbit SPI NOR Flash  |
| ESP32-WROOM-32       | Espressif    | Wi-Fi/BT SoC module    |
| STM32F103C8T6        | STMicro      | ARM Cortex-M3 MCU      |
| MT7621A              | MediaTek     | MIPS-based router SoC  |
| RTL8196E             | Realtek      | MIPS-based router SoC  |
| CC2530               | Texas Instr. | Zigbee SoC             |
| nRF52832             | Nordic Semi  | BLE SoC                |

---

## Finding Debug Ports

### UART (Universal Asynchronous Receiver-Transmitter)

UART is the most commonly found debug interface on IoT devices. It provides serial console access, which often drops you into a root shell or a bootloader console.

**UART typically uses 3-4 pins:**

| Pin | Function                                |
|-----|-----------------------------------------|
| TX  | Transmit (data from device to you)      |
| RX  | Receive (data from you to device)       |
| GND | Ground reference                        |
| VCC | Power (DO NOT connect this to your adapter -- use it only for identification) |

### Finding UART Pins with a Multimeter

1. **Identify GND:** Set your multimeter to continuity mode. Touch one probe to a known ground point (e.g., the ground pin of the power jack or a large ground plane) and probe each pin/test point. Pins that show continuity are ground.

2. **Identify VCC:** Set your multimeter to DC voltage mode. Power on the device and measure the voltage of each unidentified pin relative to GND. A pin reading a steady 3.3V or 5V is likely VCC.

3. **Identify TX:** With the device powered on and booting, measure voltage on remaining pins. The TX pin will fluctuate during boot (as it transmits data). It rests at the logic-high voltage (3.3V or 5V) when idle.

4. **Identify RX:** The remaining pin is typically RX. It will read at a steady voltage or float.

### Using a Logic Analyzer for UART Identification

A logic analyzer provides a more reliable method for identifying UART pins and determining the baud rate.

```bash
# Using sigrok/PulseView with a logic analyzer
# Connect probes to suspected UART pins
# Capture data during device boot
# Use the UART decoder in PulseView

# Auto-detect baud rate with a logic analyzer:
# Common baud rates to try: 9600, 19200, 38400, 57600, 115200
```

### Connecting to UART

```bash
# Connect your USB-UART adapter:
#   Adapter GND  ->  Device GND
#   Adapter TX   ->  Device RX
#   Adapter RX   ->  Device TX
#   DO NOT connect VCC

# Open a serial terminal with the correct baud rate
# Using screen:
screen /dev/ttyUSB0 115200

# Using minicom:
minicom -D /dev/ttyUSB0 -b 115200

# Using picocom (recommended):
picocom -b 115200 /dev/ttyUSB0

# Using Python pyserial:
python3 -m serial.tools.miniterm /dev/ttyUSB0 115200
```

**What you might see on UART:**

- Bootloader output (U-Boot, CFE, RedBoot)
- Kernel boot messages (Linux kernel log)
- Login prompt (sometimes with default or no password)
- Root shell (no authentication required -- jackpot!)
- Debug/diagnostic output

```
Example UART output during boot:

U-Boot 1.1.3 (Oct 12 2021)
Board: Ralink APSoC DRAM:  64 MB
relocate_code Pointer at: 83fb0000
flash manufacture id: ef, device id 40 18
...
BusyBox v1.19.4 (2021-10-12 09:44:33 CST) built-in shell (ash)
Enter 'help' for a list of built-in commands.

/ #
```

### JTAG (Joint Test Action Group)

JTAG is a more powerful debug interface that provides direct access to the CPU, memory, and flash. It is commonly used for on-chip debugging during development.

**Standard JTAG pins:**

| Pin  | Function                    |
|------|-----------------------------|
| TDI  | Test Data In                |
| TDO  | Test Data Out               |
| TCK  | Test Clock                  |
| TMS  | Test Mode Select            |
| TRST | Test Reset (optional)       |
| GND  | Ground                      |

**Finding JTAG pins:**

- Look for unpopulated headers with 10, 14, or 20 pins -- these often follow standard JTAG connector pinouts.
- Use the JTAGulator tool to automatically identify JTAG pins on unknown headers.
- Use the JTAGenum Arduino sketch as a low-cost alternative.

```bash
# Using OpenOCD with a JTAG adapter (e.g., FTDI-based)
openocd -f interface/ftdi/your_adapter.cfg -f target/stm32f1x.cfg

# Once connected, you can:
# - Halt the CPU
# - Read/write memory
# - Dump firmware from flash
# - Set breakpoints
# - Single-step through code
```

### SWD (Serial Wire Debug)

SWD is a two-pin alternative to JTAG used primarily on ARM Cortex-M microcontrollers.

| Pin   | Function        |
|-------|-----------------|
| SWDIO | Data I/O        |
| SWCLK | Clock           |
| GND   | Ground          |

```bash
# Using OpenOCD with an ST-Link adapter for SWD
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg

# Dump firmware via SWD
# In OpenOCD telnet session (port 4444):
> halt
> flash read_image firmware_dump.bin 0x08000000 0x100000
```

---

## SPI and I2C Bus Sniffing

### SPI (Serial Peripheral Interface)

SPI is commonly used to communicate with flash memory chips. By sniffing the SPI bus, you can capture firmware reads and writes in real time.

**SPI signals:**

| Signal | Function                         |
|--------|----------------------------------|
| MOSI   | Master Out Slave In (data to chip) |
| MISO   | Master In Slave Out (data from chip) |
| SCLK   | Serial Clock                     |
| CS     | Chip Select (active low)         |

```bash
# Sniffing SPI with a logic analyzer and sigrok
sigrok-cli -d fx2lafw -C D0=MOSI,D1=MISO,D2=SCLK,D3=CS \
    -P spi:clk=SCLK:mosi=MOSI:miso=MISO:cs=CS \
    --samples 1000000
```

### I2C (Inter-Integrated Circuit)

I2C is a two-wire protocol used to communicate with EEPROMs, sensors, and other peripherals.

| Signal | Function      |
|--------|---------------|
| SDA    | Serial Data   |
| SCL    | Serial Clock  |

```bash
# Scanning for I2C devices with a Bus Pirate
# Connect SDA and SCL to the Bus Pirate
# In Bus Pirate terminal:
> m   # select mode
> 4   # I2C
> 3   # 100kHz
> (1) # macro: I2C address scan
```

---

## Reading Flash Memory Chips

### In-Circuit Reading

You can sometimes read a flash chip while it is still soldered to the board by connecting directly to its pins.

```bash
# Using a SOIC-8 test clip on the flash chip (while desoldered or with
# the SoC held in reset to prevent bus contention)
flashrom -p ch341a_spi -r firmware.bin

# Verify the read
flashrom -p ch341a_spi -r firmware_verify.bin
diff firmware.bin firmware_verify.bin
```

### Desoldering and Reading

For more reliable reads, you may need to desolder the flash chip:

1. Apply flux around all pins of the flash chip.
2. Use a hot air rework station at 300-350 degrees Celsius.
3. Gently lift the chip once all solder joints are molten.
4. Place the chip in a socket adapter (e.g., SOIC-8 to DIP-8) connected to your programmer.
5. Read the chip with flashrom.

---

## Soldering Basics for Security Research

You do not need to be an expert solderer, but basic skills are essential.

### Essential Soldering Skills

1. **Through-hole soldering** -- attaching wires to PCB test points and pin headers.
2. **Fine-pitch wire soldering** -- connecting thin wires (30 AWG) to small test pads.
3. **Drag soldering** -- soldering fine-pitch surface-mount headers.
4. **Desoldering** -- removing components using solder wick or a desoldering pump.

### Tips for Security Research Soldering

```
- Use thin wire (30 AWG wire-wrap wire) for connecting to small test points.
- Apply flux liberally -- it makes solder flow better.
- Use a temperature-controlled iron at 300-350 degrees Celsius for lead-free solder.
- Tin your iron tip and your wire before attempting to join them.
- Secure the board with a PCB holder or "helping hands" tool.
- Practice on scrap boards before working on your target device.
```

---

## Side-Channel Attack Concepts

Side-channel attacks extract information from the physical implementation of a system rather than from weaknesses in the algorithm itself.

### Types of Side-Channel Attacks

| Attack Type          | What Is Measured                     | Example Target               |
|----------------------|--------------------------------------|------------------------------|
| Power analysis       | Current consumption during operations | Cryptographic key extraction |
| Timing analysis      | Time taken for operations            | Password comparison bypass   |
| Electromagnetic (EM) | EM emissions during processing       | Key recovery from emissions  |
| Acoustic             | Sound produced by components         | Key recovery from coil whine |

### Simple Power Analysis (SPA) and Differential Power Analysis (DPA)

Power analysis attacks measure the electrical power consumed by a device while it performs cryptographic operations. Different operations (and different data values) consume different amounts of power.

```
Conceptual workflow for a power analysis attack:

1. Connect a current sense resistor in series with the device's power supply.
2. Use an oscilloscope to measure the voltage drop across the resistor.
3. Trigger the cryptographic operation repeatedly with known inputs.
4. Collect thousands of power traces.
5. Use statistical analysis (correlation, difference of means) to recover
   the secret key byte by byte.
```

**Tools for power analysis:**

- ChipWhisperer (open-source hardware and software platform)
- Riscure Inspector
- Custom setups with oscilloscopes and current probes

### Timing Attacks

If a device compares a password byte-by-byte and returns early on the first mismatch, an attacker can measure the response time to determine how many bytes were correct.

```python
# Conceptual timing attack on a serial console login
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200)

def try_password(password):
    ser.write(password.encode() + b'\n')
    start = time.perf_counter_ns()
    response = ser.readline()
    elapsed = time.perf_counter_ns() - start
    return elapsed

# Measure timing for each first character
for c in 'abcdefghijklmnopqrstuvwxyz0123456789':
    t = try_password(c + 'A' * 7)  # pad to expected length
    print(f"{c}: {t} ns")
# The character with the longest time is likely correct (one more
# comparison was performed before rejection)
```

---

## Voltage Glitching Introduction

Voltage glitching (fault injection) involves briefly disrupting the power supply to a microcontroller to cause it to skip instructions, corrupt data, or bypass security checks.

### How Glitching Works

1. The attacker identifies a critical moment during execution (e.g., a password check).
2. A very brief voltage drop (or spike) is introduced at that precise moment.
3. The CPU may skip the comparison instruction, causing it to take the "success" branch regardless of the input.

### Glitching Targets

- **Secure boot bypass** -- glitch during signature verification to skip the check.
- **Readout protection bypass** -- glitch during the check that prevents firmware readout via debug interfaces.
- **Authentication bypass** -- glitch during password comparison.

### Tools for Glitching

| Tool              | Type                | Cost         |
|-------------------|---------------------|--------------|
| ChipWhisperer     | Voltage + clock     | $50 - $300   |
| PicoGlitcher      | Voltage (Pico-based)| $20 - $50    |
| Custom MOSFET circuit | Voltage          | $10 - $30    |

```python
# ChipWhisperer basic glitch setup (conceptual)
import chipwhisperer as cw

scope = cw.scope()
target = cw.target(scope)

# Configure glitch parameters
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.glitch.trigger_src = "ext_single"

# Set glitch width and offset (these require tuning)
scope.glitch.width = 5.0        # glitch width as % of clock period
scope.glitch.offset = 20.0      # offset from trigger
scope.glitch.repeat = 1         # number of glitch pulses

# Arm the glitch and trigger it during the target operation
scope.arm()
target.simpleserial_write('p', password_attempt)
scope.capture()
response = target.simpleserial_read('r', 1)
```

---

## Practical Exercise

1. Open a consumer IoT device (a cheap IP camera, smart plug, or old router).
2. Photograph the PCB and identify the main SoC, flash chip, and any debug headers.
3. Use a multimeter to identify UART pins (GND, VCC, TX, RX).
4. Connect a USB-UART adapter and capture boot output.
5. Attempt to interact with the boot console (try pressing keys during boot to interrupt U-Boot).
6. If possible, identify the flash chip and read it with a SPI programmer.

---

## Summary

Hardware hacking provides access to information and interfaces that are invisible from a purely software-based perspective. Debug ports like UART and JTAG are frequently left enabled in production devices, providing direct access to bootloaders, shells, and firmware. Flash memory chips can be read directly, bypassing any software protections. Advanced techniques like side-channel analysis and fault injection can defeat even hardware-based security measures.

The skills learned in this module complement the firmware analysis techniques from Module 5 -- together, they form a complete methodology for assessing the security of IoT devices at every layer.

---

## Additional Resources

- [JTAGulator](http://www.jtagulator.com/)
- [ChipWhisperer](https://www.newae.com/chipwhisperer)
- [OpenOCD Documentation](https://openocd.org/doc/html/index.html)
- [Bus Pirate Documentation](http://dangerousprototypes.com/docs/Bus_Pirate)
- [flashrom](https://flashrom.org/)
- Colin O'Flynn, *Hardware Hacking Handbook*
- Jasper van Woudenberg & Colin O'Flynn, *The Hardware Hacking Handbook*
