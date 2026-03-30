---
title: "Multimeters for Hardware Hacking"
level: Beginner
description: "Essential tool for identifying pins, voltages, and connections"
order: 4
---

# Multimeters for Hardware Hacking

## Why You Need a Multimeter

Before you can connect any tool to an IoT device's circuit board, you need to answer basic questions:

- **Which pin is ground?** You cannot connect a UART adapter or logic analyzer without a ground reference.
- **What voltage is this pin?** Connecting a 5V signal to a 3.3V chip destroys it.
- **Are these two points connected?** Tracing connections on a multi-layer PCB is impossible visually but trivial with continuity mode.
- **Is this debug header populated?** Sometimes pads exist but are not connected to anything.
- **Is the device powered on?** Verifying power rails are active before attempting communication.

A multimeter is the first tool you reach for when examining an unknown PCB. It costs less than a failed experiment would.

## Basic Measurements

### DC Voltage

Measures the voltage difference between two points. In hardware hacking, you use this to:

- Identify power rails (1.8V, 3.3V, 5V, 12V)
- Determine the logic level of UART/SPI/I2C signals
- Verify a pin is actually active and not floating
- Check battery voltage

**How to measure:**
1. Set the dial to **V DC** (often marked with a solid line and dashes: ⎓)
2. Connect the **black probe to ground** (a known ground point, metal shield, or ground plane)
3. Touch the **red probe to the point** you want to measure
4. Read the voltage on the display

```
Common voltage readings and what they mean:
  0.0V  -- Ground, or pin is not connected/active
  1.8V  -- Low-voltage logic (some modern SoCs)
  3.3V  -- Standard logic level for most IoT devices
  5.0V  -- USB power, Arduino-style logic level
 12.0V  -- Common power input for routers, cameras
  0.0-0.4V on a "high" pin  -- Possible ground or pulled-low pin
  Fluctuating rapidly       -- Data line with active traffic
```

### Continuity

Tests whether two points are electrically connected (near-zero resistance). The meter beeps when continuity is detected.

This is the **single most useful mode for hardware hacking.** You will use it constantly to:

- Find ground pins (they will have continuity with the metal shield or barrel jack ground)
- Trace where a debug header connects to on the PCB
- Verify solder joints
- Identify which pins on a header are connected to which chip pins
- Find unpopulated UART pads by tracing from the processor's TX/RX pins

**How to use:**
1. Set the dial to the **continuity symbol** (looks like a sound wave or diode symbol with a line: )))
2. Touch both probes together -- the meter should beep (confirming it works)
3. Touch one probe to a known point and the other to the point you are testing
4. A beep means the points are electrically connected

**Critical tip:** Always test continuity with the **device powered off.** Testing continuity on a powered circuit can give false readings and may damage the meter.

### Resistance

Measures resistance in ohms. In hardware hacking, you use this to:

- Identify pull-up and pull-down resistors on communication lines
- Distinguish between connected and unconnected pins (open = infinite resistance)
- Verify component values

**How to measure:**
1. Set the dial to **Ω** (ohms)
2. **Power off the device** -- measuring resistance on a powered circuit gives incorrect readings
3. Touch probes to the two ends of the component or path
4. Read the value

```
Common readings:
  0-2 Ω      -- Direct connection (wire, trace, or short)
  4.7 kΩ     -- Typical I2C pull-up resistor
  10 kΩ      -- Common pull-up/pull-down value
  OL / ∞     -- No connection (open circuit)
```

## Recommended Models for Beginners

### Budget Tier ($15-20)

**AstroAI DM6000AR** or **Kaiweets HT118A**

- Auto-ranging (no need to manually select measurement range)
- DC/AC voltage, resistance, continuity with buzzer
- Backlit display
- Good enough for 95% of hardware hacking tasks
- Available on Amazon

### Mid Tier ($25-30)

**UNI-T UT61E** or **ANENG AN8008**

- True RMS (more accurate AC measurements, not critical for DC work)
- Better accuracy and resolution
- Faster continuity buzzer response (important when probing many points quickly)
- Data hold and min/max functions

### Professional ($50+)

**Fluke 101/106** or **Brymen BM235**

- Extremely reliable and accurate
- Better safety ratings (CAT III/IV for higher voltage work)
- Worth it if you work on mains-powered devices

### What to Look For

- **Auto-ranging:** Eliminates the need to guess the measurement range
- **Fast continuity buzzer:** A slow buzzer is painful when tracing dozens of connections. Test this in the store if possible -- touch and release the probes quickly and listen for a responsive beep.
- **Backlit display:** You will often work in dim conditions
- **Test lead quality:** Budget meters often ship with flimsy probes. Budget $5-10 for a set of sharp-tipped probes or hook probes.

## Using Continuity Mode to Trace PCB Connections

This is the core hardware hacking technique with a multimeter. Here is a step-by-step process for mapping a debug header on an unknown device:

### Step 1: Find Ground

1. Power off the device
2. Set the meter to continuity mode
3. Place one probe on a known ground point:
   - The outer barrel of the DC power jack
   - The metal USB connector shell
   - The metal RF shield on the PCB
   - A large copper pour or fill visible on the PCB (often ground)
4. Touch the other probe to each pin on the debug header
5. Any pin that beeps is a ground pin

### Step 2: Identify Power Pins

1. Power on the device
2. Switch to DC voltage mode
3. Place the black probe on the ground pin you just identified
4. Touch the red probe to each remaining header pin
5. Record the voltage on each pin
6. Pins reading 3.3V or 5V steadily are likely VCC (power) pins

### Step 3: Identify Data Pins

After eliminating ground and power pins, the remaining pins are likely data pins (UART TX, UART RX, JTAG, etc.):

1. Still in voltage mode with the device powered on and booting
2. UART TX typically reads around 3.3V when idle and briefly dips during data transmission
3. UART RX is an input and may float or read near VCC
4. Connect a USB-UART adapter and try communicating

### Step 4: Cross-Reference with the Processor Datasheet

1. Identify the main processor on the PCB (read the chip markings)
2. Find the datasheet and locate the UART TX/RX pin numbers
3. Use continuity mode (device powered off) to trace from the processor's UART pins to the debug header
4. This confirms which header pin is TX and which is RX

## Identifying UART Pins Without a Datasheet

When you find a row of 4 pins (or pads) on a PCB, they often follow this pattern:

```
Pin 1: VCC  (3.3V or 5V)
Pin 2: TX   (transmit - data from device)
Pin 3: RX   (receive - data to device)
Pin 4: GND  (ground)
```

But the order varies. Here is how to identify them systematically:

1. **Find GND** using continuity mode (see above)
2. **Find VCC** using voltage mode -- it reads a steady 3.3V or 5V
3. **Find TX** -- in voltage mode, it reads close to VCC when idle but you may see slight fluctuations during boot. If you have a serial terminal connected through a USB-UART adapter, try connecting this pin to your adapter's RX -- if you see data, this is TX.
4. **Find RX** -- the remaining pin. It may float (unstable voltage reading) or be held at VCC by a pull-up resistor.

### The "JTagulator" Approach (Manual Version)

If the pinout is completely unknown and you have more than 4 pins, you can systematically try combinations:

1. Connect GND
2. Connect each remaining pin one at a time to your USB-UART adapter's RX
3. Open a serial terminal at 115200 baud
4. Reboot the device
5. The pin that produces readable text is TX
6. Once TX is found, try connecting each remaining pin to your adapter's TX and sending characters -- the pin that produces echo or a response is RX

## Measuring Voltage Levels on Debug Headers

### Why Voltage Levels Matter

Before connecting any tool to a debug header, measure the voltage levels:

```bash
# Decision tree:
#
# Measured voltage on TX pin when idle:
#   ~1.8V --> Use a 1.8V logic level adapter (uncommon, some newer SoCs)
#   ~3.3V --> Set your USB-UART adapter to 3.3V mode
#   ~5.0V --> Set your USB-UART adapter to 5V mode
#   0V    --> Pin may be disabled, or you have the wrong pin
#   Fluctuating 0-3.3V --> Active data transmission (good sign!)
```

### Checking Signal Integrity

If your serial connection produces garbled output:

1. Measure the voltage on the TX line -- confirm it matches your adapter's logic level
2. Check that GND is solidly connected (resistance < 2 ohm between your adapter's GND and the device's GND)
3. Try a different baud rate
4. Check for voltage droop -- if the VCC line is sagging below the expected voltage, the device may have power issues

## Safety

### For You

- **Never probe mains voltage** (110/240V AC) with a meter rated only for low voltage. Budget meters often have a CAT I or no rating. If the device plugs into a wall outlet, be aware that some internal components carry lethal voltages.
- **One hand rule:** When probing powered circuits, keep one hand in your pocket. This prevents a current path through your chest if you accidentally contact a high voltage.
- **Inspect your test leads** for damaged insulation before each use.

### For the Device

- **Always check your meter's mode** before touching probes to a circuit. If the meter is set to current mode (amps) and you probe across a voltage source, you create a short circuit through the meter's low-resistance current shunt. This can blow the meter's fuse or damage the circuit.
- **Do not force probes** into tight spaces where they might bridge adjacent pins or traces.
- **Use the right probe tips** -- fine-point probes for small SMD pads, hook probes for test points you need to hold onto.

### For Your Measurements

- **Measure voltage with the device in its normal operating state.** Some pins change voltage depending on the device's state (booting vs idle vs active).
- **Account for tolerance.** A "3.3V" rail might actually read 3.28V or 3.35V. This is normal.
- **Battery-powered readings change over time.** A device with a dying battery may show lower voltage levels than expected.

## Essential Accessories

| Item | Price | Purpose |
|------|-------|---------|
| Fine-point probe tips | $5-8 | Reach small SMD pads and vias |
| Hook probes / IC hook clips | $5-8 | Clip onto pins for hands-free measurement |
| Probe-to-jumper adapters | $3-5 | Connect multimeter probes to breadboard wires |
| Silicone test leads (replacement) | $8-12 | More flexible and durable than stock leads |
| Third hand / PCB holder | $10-15 | Hold the PCB steady while probing |

## Quick Reference Card

```
Task                          Mode          What to Look For
─────────────────────────────────────────────────────────────
Find ground pins              Continuity    Beep = ground
Find power pins               DC Voltage    Steady 3.3V or 5V
Find UART TX                  DC Voltage    ~3.3V idle, flickers on boot
Find UART RX                  DC Voltage    May float or pull to VCC
Check before connecting       DC Voltage    Match adapter voltage level
Trace PCB connections         Continuity    Beep = connected
Verify pull-up resistors      Resistance    4.7k-10k typical for I2C
Check for shorts              Continuity    Beep where there shouldn't be one
Test solder joints            Continuity    No beep = cold joint or break
```
