---
title: "Ghidra"
level: Advanced
description: "NSA's open-source reverse engineering framework"
order: 4
---

# Ghidra

## What Is Ghidra?

Ghidra is a software reverse engineering (SRE) framework developed by the NSA and released as open source in 2019. It provides a suite of tools for analyzing compiled code, including a disassembler, decompiler, and scripting engine. For IoT security, Ghidra is invaluable because:

- IoT firmware contains compiled binaries (usually ARM or MIPS) that control device behavior
- These binaries implement authentication, encryption, network protocols, and command handling
- Reverse engineering reveals hardcoded credentials, backdoors, cryptographic weaknesses, command injection vulnerabilities, buffer overflows, and undocumented features
- Ghidra's decompiler turns assembly code back into readable C-like pseudocode, making analysis accessible even if you are not fluent in ARM or MIPS assembly

Ghidra is free, cross-platform, and competitive with commercial tools like IDA Pro ($2,000+).

## Installation

### Java Requirement

Ghidra requires Java Development Kit (JDK) 17 or later (Ghidra 11.x requires JDK 21+).

```bash
# Debian/Ubuntu
sudo apt install openjdk-21-jdk

# Fedora
sudo dnf install java-21-openjdk-devel

# macOS
brew install openjdk@21

# Verify Java version
java -version
# Should show: openjdk version "21.x.x" or similar
```

### Downloading and Running Ghidra

```bash
# Download the latest release from https://github.com/NationalSecurityAgency/ghidra/releases
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.3_build/ghidra_11.3_PUBLIC_20250108.zip

# Extract
unzip ghidra_*.zip
cd ghidra_*

# Run Ghidra
./ghidraRun

# On macOS, you may need to allow it in System Preferences > Security & Privacy
# On Linux, ensure JAVA_HOME is set if Ghidra cannot find Java:
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
```

### First Launch

On first launch, Ghidra displays the Project window. Before analyzing anything, accept the license agreement and let the initial setup complete. Ghidra will index its internal resources.

## Creating Projects

Ghidra organizes work into projects. Each project can contain multiple binary files (programs).

1. **File > New Project**
2. Choose **Non-Shared Project** (shared projects are for team collaboration)
3. Select a project directory and name (e.g., "RouterFirmware")
4. Click **Finish**

### Project Organization Tips

- Create one project per device or firmware version
- Import all related binaries into the same project (main application, shared libraries, bootloader)
- Use folders within the project to organize files by type or function

## Importing Binaries

### From Extracted Firmware

After extracting a firmware image with binwalk, you will have a filesystem containing ELF binaries:

```bash
# Find ELF binaries in the extracted filesystem
find _firmware.bin.extracted/squashfs-root/ -type f -executable | \
  xargs file | grep "ELF"

# Common locations:
# /bin/    -- Core system utilities (busybox, custom tools)
# /sbin/   -- System administration tools
# /usr/bin/ -- Application binaries
# /usr/lib/ -- Shared libraries
# /usr/sbin/ -- Custom daemon processes
# /www/cgi-bin/ -- Web interface CGI binaries
```

### Import Process

1. **File > Import File** (or drag and drop into the project window)
2. Select the binary file
3. Ghidra auto-detects the format. Verify:
   - **Format:** ELF, Raw Binary, PE, etc.
   - **Language:** ARM:LE:32:v7 (most common for IoT), MIPS:BE:32:default, etc.
   - **Compiler:** default or GCC
4. Click **OK**, then **OK** on the import summary
5. Double-click the file in the project window to open the CodeBrowser

### Importing Raw Binary Files (No ELF Header)

Some IoT firmware dumps lack ELF headers (e.g., bare-metal firmware dumped from flash):

1. **File > Import File**
2. In the format dropdown, select **Raw Binary**
3. Set the **Language** manually:
   - ARM Little Endian 32-bit: `ARM:LE:32:v7` (most common for Cortex-M/A)
   - ARM Big Endian: `ARM:BE:32:v7`
   - MIPS Big Endian: `MIPS:BE:32:default` (many routers)
   - MIPS Little Endian: `MIPS:LE:32:default`
4. Set the **Base Address** (check the bootloader or linker script; common values: 0x00000000, 0x08000000 for STM32, 0x80000000 for MIPS)
5. Click **Options** and configure the memory map if needed

## Auto-Analysis

When you first open a binary in the CodeBrowser, Ghidra offers to run auto-analysis. **Always click "Yes" with the default options.** This process:

- Identifies function entry points
- Disassembles code
- Runs the decompiler on each function
- Resolves cross-references
- Identifies strings and data references
- Applies known function signatures (if libraries are recognized)

Analysis can take seconds (small binary) to hours (large firmware with many libraries). The progress bar shows in the bottom-right corner.

### Improving Analysis Results

After auto-analysis completes:

```
# In the Script Manager (Window > Script Manager), run:
# - "ResolveX86orX64LinuxSyscallsScript" (for x86 Linux binaries)
# - "FindStringsScript" (finds additional strings)
# - "PropagateExternalParametersScript" (improves decompiler output)
```

For ARM/MIPS binaries, manually check that the processor mode is correct:
- ARM vs Thumb mode (for ARM processors)
- MIPS16 vs standard MIPS
- If functions look wrong, try right-clicking the address and selecting **Disassemble As** with a different mode.

## Navigating the CodeBrowser

The CodeBrowser has several key windows:

### Listing Window (Center)

The main disassembly view. Shows assembly instructions with addresses, labels, and comments. Right-click for context menu options.

### Decompiler Window (Right)

Shows C-like pseudocode for the currently selected function. This is your primary analysis tool. The decompiler output is not perfect C code, but it is far more readable than raw assembly.

```c
// Example decompiler output for a login check function:
int check_login(char *username, char *password)
{
    int result;

    if (strcmp(username, "admin") == 0) {
        if (strcmp(password, "p@ssw0rd123") == 0) {  // Hardcoded credential!
            result = 1;
        } else {
            result = 0;
        }
    } else {
        result = 0;
    }
    return result;
}
```

### Symbol Tree (Left)

Browse functions, labels, classes, and namespaces. Functions are listed alphabetically or can be sorted by address. Key categories:

- **Functions:** All identified functions
- **Labels:** Named addresses
- **Imports:** Functions called from external libraries
- **Exports:** Functions this binary exposes

### Data Type Manager (Bottom-Left)

Manage and apply data structures. You can define custom structs that match the firmware's data structures to improve decompiler output.

### Key Navigation Shortcuts

| Shortcut | Action |
|----------|--------|
| G | Go to address |
| Ctrl+Shift+E | Search for strings |
| Ctrl+Shift+F | Search memory |
| X | Show cross-references (xrefs) to current address |
| Ctrl+E | Edit function signature |
| L | Rename label/function |
| ; | Add comment |
| Ctrl+L | Retype variable |
| Alt+Left/Right | Navigate back/forward |
| Space | Toggle between Listing and Decompiler |

## Finding Interesting Functions in IoT Firmware

### Strategy 1: Search for Strings

Most IoT vulnerabilities are found by starting with interesting strings:

1. **Window > Defined Strings** -- lists all strings in the binary
2. Search for:

```
# Authentication related
password, passwd, login, auth, credential, secret, token, api_key

# Command execution
system, popen, exec, /bin/sh, /bin/bash, cmd, command

# Network related
socket, connect, bind, listen, send, recv, http, mqtt, coap

# File operations
fopen, /etc/shadow, /etc/passwd, /tmp/, /dev/

# Crypto related
AES, DES, RSA, encrypt, decrypt, key, iv, salt, hash, MD5, SHA

# Debug/backdoor
debug, test, backdoor, hidden, engineering, factory, telnet

# Error messages (lead you to error handling code and reveal logic)
"invalid password", "access denied", "authentication failed"
```

3. Double-click a string to go to its location in the data section
4. Press **X** to see all cross-references -- which functions use this string
5. Navigate to those functions and analyze the decompiler output

### Strategy 2: Follow Imports

Check what library functions the binary calls:

```
# Dangerous functions (potential buffer overflows)
strcpy, strcat, sprintf, gets, scanf
# Safe alternatives would be strncpy, strncat, snprintf, fgets

# Command execution (potential command injection)
system(), popen(), execve(), execl()

# Network functions (understand communication)
socket(), connect(), bind(), listen(), accept(), send(), recv()

# Crypto functions (check for weak crypto)
MD5(), DES_ecb_encrypt(), rand(), srand()
```

In the Symbol Tree, expand **Imports** and look for these function names. Click each one and press **X** to find where it is called.

### Strategy 3: Analyze Entry Points

For network daemons (web servers, MQTT handlers, etc.):

1. Find the `main()` function
2. Follow the initialization flow: socket creation, binding, listening
3. Find the request handler function
4. Trace how user input flows from network receive to processing

### Strategy 4: Compare Firmware Versions

Ghidra has a built-in diff tool (**Version Tracking**):

1. Import both firmware versions into the same project
2. **Tools > Version Tracking**
3. Create a new session with the two binaries
4. Run the correlators (exact match, then fuzzy match)
5. Review functions that changed between versions -- these are the patches

## Analyzing ARM and MIPS Binaries

### ARM (Most Common in Modern IoT)

ARM is the dominant architecture for IoT devices. Things to know:

- **ARM vs Thumb mode:** ARM instructions are 32-bit; Thumb instructions are 16-bit (or mixed 16/32 in Thumb-2). Many IoT binaries use Thumb mode for code density. If Ghidra disassembles garbage, try switching to Thumb mode: right-click > Disassemble As > Thumb.

- **Common ARM IoT processors:**
  - Cortex-A (application processors): Routers, cameras, smart speakers
  - Cortex-M (microcontrollers): Sensors, actuators, simple devices
  - Cortex-R (real-time): Industrial IoT, automotive

- **Calling convention:** Arguments in r0-r3, return value in r0. The decompiler handles this automatically, but knowing it helps when reading assembly.

- **System calls:** ARM Linux uses `svc #0` (supervisor call) for syscalls. The syscall number is in r7.

```assembly
# Example ARM assembly for system("reboot")
ldr   r0, ="reboot"    ; Load address of "reboot" string
bl    system            ; Call system()
```

### MIPS (Common in Routers and Network Equipment)

Many routers and networking devices use MIPS processors. Key differences:

- **Endianness:** MIPS can be big-endian (most Broadcom-based routers) or little-endian (some MediaTek). Check with `file` or `readelf -h`.

- **Delay slots:** MIPS executes the instruction AFTER a branch before the branch takes effect. Ghidra handles this in analysis, but be aware when reading raw assembly.

- **GP-relative addressing:** MIPS uses a Global Pointer (GP) register for accessing global variables. Ghidra sometimes needs help resolving GP values. If you see unresolved references:
  1. Find the GP value (often set in `__start` or at the beginning of `main`)
  2. **Edit > Tool Options > Analyzers > MIPS Constant Reference Analyzer** -- set the GP value

- **Calling convention:** Arguments in $a0-$a3, return value in $v0.

```assembly
# Example MIPS assembly for strcmp
lw    $a0, string1_addr($gp)   # Load first string address
lw    $a1, string2_addr($gp)   # Load second string address
jal   strcmp                     # Jump and link (call) strcmp
nop                              # Delay slot
```

### Setting the Correct Processor

If auto-detection fails, manually set the processor when importing:

| Device Type | Common Processor | Ghidra Language |
|-------------|-----------------|-----------------|
| Modern routers | ARM Cortex-A | ARM:LE:32:v7 |
| IP cameras | ARM Cortex-A | ARM:LE:32:v7 |
| Smart speakers | ARM Cortex-A53 | AARCH64:LE:64:v8A |
| Older routers | MIPS32 | MIPS:BE:32:default |
| Some routers | MIPS (LE) | MIPS:LE:32:default |
| STM32 devices | ARM Cortex-M | ARM:LE:32:Cortex |
| ESP32 | Xtensa | (requires Xtensa plugin) |

## Scripting Basics

Ghidra supports scripting in Java and Python (Jython). Scripts automate repetitive analysis tasks.

### Running Built-in Scripts

**Window > Script Manager** opens the script browser. Useful built-in scripts:

- **FindStringsScript:** Finds strings not caught by auto-analysis
- **SearchForAddressTablesScript:** Finds function pointer tables (common in RTOS firmware)
- **FunctionIDHeadlessAnalyzer:** Applies function signature libraries

### Writing a Python Script

```python
# FindHardcodedIPs.py -- Search for hardcoded IP addresses in strings
# Place in ~/ghidra_scripts/ or the project's scripts directory
# @category IoT
# @description Find hardcoded IP addresses in binary strings

import re

listing = currentProgram.getListing()
dataIterator = listing.getDefinedData(True)

ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

while dataIterator.hasNext():
    data = dataIterator.next()
    if data.hasStringValue():
        value = data.getValue()
        if isinstance(value, str) or isinstance(value, unicode):
            matches = ip_pattern.findall(str(value))
            if matches:
                print("Address: {} | String: {} | IPs: {}".format(
                    data.getAddress(), value, matches))
```

### Writing a Script to Find Dangerous Function Calls

```python
# FindDangerousCalls.py -- Locate calls to dangerous functions
# @category IoT
# @description Find calls to strcpy, sprintf, system, etc.

from ghidra.program.model.symbol import SymbolType

dangerous_functions = [
    "strcpy", "strcat", "sprintf", "gets", "scanf",
    "system", "popen", "execve",
    "MD5_Init", "DES_ecb_encrypt"
]

symbolTable = currentProgram.getSymbolTable()

for func_name in dangerous_functions:
    symbols = symbolTable.getSymbols(func_name)
    for sym in symbols:
        refs = getReferencesTo(sym.getAddress())
        if refs:
            print("\n--- {} ---".format(func_name))
            for ref in refs:
                caller = getFunctionContaining(ref.getFromAddress())
                caller_name = caller.getName() if caller else "unknown"
                print("  Called from {} at {}".format(
                    caller_name, ref.getFromAddress()))
```

### Running Scripts Headlessly

Ghidra can run analysis and scripts without the GUI, useful for batch processing:

```bash
# Headless analysis of a binary
/path/to/ghidra/support/analyzeHeadless \
  /path/to/project ProjectName \
  -import firmware_binary \
  -processor ARM:LE:32:v7 \
  -postScript FindDangerousCalls.py \
  -scriptlog /tmp/ghidra_output.log

# Batch process all binaries in a directory
for bin in extracted_fs/usr/bin/*; do
  /path/to/ghidra/support/analyzeHeadless \
    /path/to/project BatchAnalysis \
    -import "$bin" \
    -postScript FindDangerousCalls.py \
    -scriptlog "/tmp/ghidra_$(basename $bin).log"
done
```

## Tips for IoT Firmware Reverse Engineering

### 1. Start with the Web Interface

The web server binary (often `httpd`, `lighttpd`, `uhttpd`, `goahead`, or a custom binary) is usually the largest attack surface. It handles user input from the network and often runs as root.

### 2. Trace User Input

Identify where network data enters the program (recv, read, fgets from a socket) and follow it through the code. Look for it reaching dangerous functions (system, strcpy, sprintf) without proper validation.

### 3. Look for Backdoor Accounts

Search for strings that look like usernames or passwords. Check authentication functions for hardcoded credentials or special bypass conditions.

### 4. Understand the Command Dispatch Table

Many IoT binaries use a table mapping command strings to handler functions:

```c
struct command_entry {
    char *name;
    int (*handler)(char *args);
};

struct command_entry commands[] = {
    {"get_status", handle_status},
    {"set_config", handle_config},
    {"factory_reset", handle_reset},
    {"debug_shell", handle_debug},  // Hidden debug command!
};
```

In Ghidra, these appear as arrays of pointers. Find them by looking for cross-references from strcmp calls.

### 5. Check Crypto Implementations

- Is the device using hardcoded encryption keys?
- Is it using weak algorithms (DES, MD5 for password hashing, ECB mode)?
- Is the random number generator properly seeded, or does it use a fixed seed / time-based seed?

### 6. Rename Functions and Variables

As you understand what functions do, rename them (press L). This dramatically improves readability:

```
Before:  FUN_0001a3c4(param_1, param_2)
After:   check_admin_password(username, password)
```

Also retype variables (Ctrl+L) when you determine their types. Changing `undefined4` to `char *` makes the decompiler output much clearer.

### 7. Create Custom Data Types

Define structures that match the firmware's data structures:

1. **Window > Data Type Manager**
2. Right-click the program's data type archive > New > Structure
3. Define fields with their types and sizes
4. Apply the structure to memory locations where the data resides

### 8. Use the Function Call Graph

**Window > Function Call Graph** shows which functions call the current function and which functions it calls. This is invaluable for understanding the flow of a complex binary.

### 9. Collaborate and Save Your Work

- Add comments liberally (press `;` on any line)
- Use bookmarks (Ctrl+D) to mark interesting locations
- Export your analysis as a Ghidra project archive for sharing with team members
