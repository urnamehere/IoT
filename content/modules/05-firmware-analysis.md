---
title: "Firmware Analysis"
order: 5
level: Intermediate
description: "Extract, analyze, and reverse engineer IoT device firmware"
estimated_time: "90 minutes"
prerequisites:
  - "Module 4: Recon & Scanning"
related_labs:
  - "lab-firmware-extraction"
---

# Module 5: Firmware Analysis

## Introduction

Firmware is the software embedded directly into IoT devices. Unlike traditional desktop or server software, firmware runs on constrained hardware, often without the protections of a full operating system. This makes it a prime target for security researchers. Analyzing firmware can reveal hardcoded credentials, vulnerable libraries, insecure configurations, and exploitable logic flaws that affect millions of deployed devices.

In this module, you will learn how to obtain, extract, and analyze IoT device firmware using both manual techniques and automated tools.

---

## What Is Firmware?

Firmware is a specific class of software that provides low-level control for a device's hardware. It typically includes:

- **Bootloader** -- initializes hardware and loads the main operating system or application code (e.g., U-Boot, GRUB for embedded systems).
- **Kernel** -- often a Linux kernel (but sometimes an RTOS like FreeRTOS, Zephyr, or VxWorks).
- **Root filesystem** -- contains binaries, libraries, configuration files, and web interfaces.
- **NVRAM / configuration partitions** -- stores device-specific settings, Wi-Fi credentials, and user data.

| Component         | Purpose                                | Common Formats               |
|--------------------|----------------------------------------|------------------------------|
| Bootloader         | Hardware init, loads kernel            | U-Boot image, raw binary     |
| Kernel             | OS core                               | uImage, zImage, FIT image    |
| Root filesystem    | User-space binaries and configs        | SquashFS, JFFS2, CramFS      |
| NVRAM              | Runtime configuration storage          | Raw key-value, TLV            |
| Web interface      | Device management UI                   | HTML/JS/Lua in rootfs        |

---

## Obtaining Firmware

### Method 1: Downloading from the Vendor

The easiest approach is to check the manufacturer's support website. Many vendors publish firmware update files for their products.

```bash
# Example: downloading firmware from a vendor's website
wget https://downloads.example-vendor.com/firmware/router-v2.1.4.bin

# Some vendors use FTP servers
ftp ftp.vendor-example.com
# Navigate to /pub/firmware/ and download
```

**Tips for finding firmware downloads:**

- Check the product support page for "firmware update" or "software download" links.
- Search for the device model number along with "firmware download" or "firmware .bin".
- Look at FTP servers -- some vendors expose open FTP directories.
- Check the Wayback Machine for discontinued products whose pages have been removed.
- Community forums sometimes host mirrors of firmware files.

### Method 2: Intercepting OTA Updates

Many IoT devices update over the air (OTA). You can intercept these updates by setting up a man-in-the-middle proxy.

```bash
# Set up mitmproxy to intercept HTTP/HTTPS traffic from the device
mitmproxy --mode transparent --showhost

# Or use Burp Suite with a transparent proxy configuration
# Configure your network so that device traffic routes through your proxy
```

If the device uses HTTPS without certificate pinning, you can install your CA certificate and decrypt the traffic to capture the firmware download URL.

### Method 3: Extracting from Flash Memory

When firmware is not available online, you can read it directly from the flash memory chip on the device's PCB. This requires physical access and basic hardware tools.

```bash
# Using flashrom with an SPI programmer (e.g., CH341A)
flashrom -p ch341a_spi -r firmware_dump.bin

# Verify the dump by reading twice and comparing
flashrom -p ch341a_spi -r firmware_dump_2.bin
md5sum firmware_dump.bin firmware_dump_2.bin
```

Common flash chip types you will encounter:

| Chip Type | Interface | Common Tools           |
|-----------|-----------|------------------------|
| SPI NOR   | SPI       | CH341A, Bus Pirate     |
| SPI NAND  | SPI       | CH341A (with support)  |
| eMMC      | MMC       | eMMC reader, SD adapter|
| Parallel NOR | Parallel | TL866II+           |

---

## Extracting Firmware with Binwalk

Binwalk is the essential tool for firmware analysis. It scans binary files for embedded file signatures, compressed archives, and filesystem images.

### Basic Scanning

```bash
# Scan the firmware file for recognized signatures
binwalk firmware.bin
```

Example output:

```
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             uImage header, header size: 64 bytes, ...
64            0x40            LZMA compressed data, properties: 0x5D, ...
1245184       0x130000        Squashfs filesystem, little endian, version 4.0, ...
```

### Automated Extraction

```bash
# Extract all recognized components automatically
binwalk -e firmware.bin

# For recursive extraction (extracts archives within archives)
binwalk -eM firmware.bin
```

This creates a directory (e.g., `_firmware.bin.extracted/`) containing the extracted components.

### Entropy Analysis

Entropy analysis helps identify encrypted or compressed regions in the firmware.

```bash
# Generate an entropy graph
binwalk -E firmware.bin
```

- **High entropy (close to 1.0):** Compressed or encrypted data.
- **Low entropy (close to 0.0):** Uncompressed data, strings, padding.
- **Flat high entropy across the entire image:** Likely encrypted firmware -- extraction will not work without the decryption key.

### Manual Extraction with dd

Sometimes Binwalk's automatic extraction fails. You can use `dd` to manually carve out sections.

```bash
# Extract a SquashFS filesystem starting at offset 0x130000 (1245184 decimal)
dd if=firmware.bin of=squashfs.img bs=1 skip=1245184

# Then mount or extract with unsquashfs
unsquashfs squashfs.img
```

---

## Filesystem Analysis with Firmwalker

Once you have extracted the root filesystem, Firmwalker automates the search for interesting files and potential vulnerabilities.

```bash
# Clone and run Firmwalker
git clone https://github.com/craigz28/firmwalker.git
cd firmwalker
./firmwalker.sh /path/to/extracted/rootfs/
```

Firmwalker searches for:

- Configuration files (`*.conf`, `*.cfg`, `*.ini`)
- Password files (`/etc/passwd`, `/etc/shadow`)
- SSL certificates and private keys
- Shell scripts that may contain credentials
- Database files
- Web server configurations
- References to URLs, IPs, and email addresses

### Manual Filesystem Exploration

Even with automated tools, manual inspection is invaluable. Here are key areas to investigate:

```bash
# Check for password files
cat etc/passwd
cat etc/shadow

# Look for hardcoded credentials in config files
grep -ri "password" etc/
grep -ri "passwd" etc/
grep -ri "secret" etc/
grep -ri "api_key" etc/

# Examine web application files
ls -la www/ var/www/ usr/share/www/

# Check for SSH keys
find . -name "*.pem" -o -name "*.key" -o -name "id_rsa" -o -name "authorized_keys"

# Look for startup scripts
ls etc/init.d/
cat etc/rc.local

# Check crontabs
cat etc/crontab
ls etc/cron.d/
```

---

## Finding Hardcoded Credentials and API Keys

Hardcoded credentials are one of the most common and dangerous vulnerabilities in IoT firmware. Manufacturers frequently embed default passwords, API keys, and encryption keys directly in the firmware.

### Common Patterns to Search For

```bash
# Search for common credential patterns in the extracted filesystem
grep -rn "admin" --include="*.conf" --include="*.lua" --include="*.sh" .
grep -rn "root:" etc/shadow
grep -rn "DEFAULT_PASSWORD" .
grep -rn "api[_-]key" .
grep -rn "token" --include="*.json" --include="*.conf" .

# Search for base64-encoded strings (often used to obfuscate credentials)
grep -rPo "[A-Za-z0-9+/]{20,}={0,2}" . | head -50

# Search for private keys
grep -rn "BEGIN RSA PRIVATE KEY" .
grep -rn "BEGIN EC PRIVATE KEY" .

# Search for URLs with embedded credentials
grep -rn "http.*:.*@" .
```

### Strings Analysis

The `strings` utility extracts printable character sequences from binary files. This is useful for analyzing compiled binaries that may contain hardcoded values.

```bash
# Extract strings from a binary
strings -n 8 usr/bin/management_daemon | grep -i pass
strings -n 8 usr/bin/management_daemon | grep -i key
strings -n 8 usr/bin/management_daemon | grep -i secret
strings -n 8 usr/bin/management_daemon | grep "http"

# Look for interesting strings in shared libraries too
strings -n 8 usr/lib/libconfig.so
```

---

## Identifying Vulnerable Libraries

IoT devices often ship with outdated and vulnerable versions of common libraries. Identifying these is a critical part of firmware analysis.

### Manual Version Checking

```bash
# Check the version of common libraries
# OpenSSL
strings usr/lib/libssl.so | grep "OpenSSL"

# BusyBox (contains many common Unix utilities)
strings usr/bin/busybox | grep "BusyBox v"

# D-Link, TP-Link, and many other routers use lighttpd or mini_httpd
strings usr/sbin/httpd | grep -i "server:"

# Check for known vulnerable libraries
find . -name "libcurl*" -exec strings {} \; | grep "libcurl/"
find . -name "libsqlite*" -exec strings {} \; | grep "SQLite"
```

### Using CVE Databases

Once you identify library versions, cross-reference them against vulnerability databases:

| Resource                     | URL                                        |
|------------------------------|--------------------------------------------|
| NIST NVD                     | https://nvd.nist.gov/                      |
| CVE Details                  | https://www.cvedetails.com/                |
| Exploit-DB                   | https://www.exploit-db.com/                |
| OSV (Open Source Vulns)      | https://osv.dev/                           |

---

## Static Analysis with Ghidra

Ghidra is a free reverse engineering tool developed by the NSA. It supports many architectures commonly found in IoT devices, including ARM, MIPS, and PowerPC.

### Getting Started with Ghidra for Firmware

```bash
# Launch Ghidra
ghidraRun

# Create a new project, then import the binary you want to analyze
# File -> Import File -> select the binary (e.g., usr/bin/httpd)
```

**Key steps for IoT binary analysis in Ghidra:**

1. **Identify the architecture** -- check the ELF header or use `file` and `readelf`:
   ```bash
   file usr/bin/httpd
   # Output: ELF 32-bit LSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), ...

   readelf -h usr/bin/httpd
   ```

2. **Import and auto-analyze** -- Ghidra will detect the architecture and run its auto-analysis suite, including function identification, cross-references, and string analysis.

3. **Search for dangerous functions** -- look for calls to known unsafe functions:
   - `strcpy`, `strcat` -- buffer overflow risks
   - `sprintf`, `vsprintf` -- format string risks
   - `system`, `popen`, `execve` -- command injection risks
   - `gets` -- always vulnerable to buffer overflow

4. **Trace user input** -- follow data from network input functions (`recv`, `read`) through to dangerous sinks (`system`, `strcpy`).

5. **Examine authentication logic** -- locate login handlers and trace the password comparison logic. Look for:
   - Hardcoded comparison strings
   - Weak comparison logic (comparing only a prefix)
   - Authentication bypass paths

### Ghidra Scripting

Ghidra supports scripting in Java and Python. A useful script to find dangerous function calls:

```python
# Ghidra Python script: find_dangerous_calls.py
# Run from Ghidra's Script Manager

from ghidra.program.model.symbol import SymbolType

dangerous_functions = [
    "strcpy", "strcat", "sprintf", "gets",
    "system", "popen", "execve", "exec"
]

function_manager = currentProgram.getFunctionManager()
symbol_table = currentProgram.getSymbolTable()

for func_name in dangerous_functions:
    symbols = symbol_table.getSymbols(func_name)
    for symbol in symbols:
        refs = getReferencesTo(symbol.getAddress())
        for ref in refs:
            caller = function_manager.getFunctionContaining(ref.getFromAddress())
            if caller:
                print("DANGEROUS: {}() called from {} at {}"
                      .format(func_name, caller.getName(), ref.getFromAddress()))
```

---

## Automated Analysis with EMBA

EMBA (Embedded Analyzer) is a comprehensive firmware analysis framework that automates many of the manual steps described above.

### Installing and Running EMBA

```bash
# Clone EMBA
git clone https://github.com/e-m-b-a/emba.git
cd emba

# Install dependencies (requires root)
sudo ./installer.sh

# Run a basic firmware analysis
sudo ./emba.sh -f /path/to/firmware.bin -l /path/to/output/

# Run with full analysis including CVE checking
sudo ./emba.sh -f /path/to/firmware.bin -l /path/to/output/ -F
```

### What EMBA Checks

EMBA performs a broad set of analyses automatically:

- **Binary analysis** -- identifies architectures, checks for security features (NX, ASLR, stack canaries, RELRO, PIE).
- **Vulnerability identification** -- matches library versions against CVE databases.
- **Credential search** -- finds hardcoded passwords, keys, and tokens.
- **Configuration review** -- checks for insecure configurations.
- **Cryptographic analysis** -- identifies weak or broken cryptographic usage.
- **Network analysis** -- identifies listening services and open ports in firmware.

### Reading EMBA Output

EMBA generates an HTML report. Key sections to review:

| Section                | What to Look For                                |
|------------------------|-------------------------------------------------|
| S05 - Firmware details | Architecture, OS, filesystem type               |
| S09 - Binary analysis  | Binaries without NX, canaries, RELRO            |
| S25 - Kernel analysis  | Kernel version, known kernel vulnerabilities     |
| S35 - Network          | Hardcoded IPs, listening services                |
| S40 - Weak passwords   | Default or empty passwords                       |
| S120 - CVE mapping     | Known CVEs mapped to identified software         |

---

## Common Firmware Vulnerabilities

### 1. Hardcoded Credentials

The most prevalent issue. Credentials embedded in firmware are accessible to anyone who downloads or extracts the firmware.

```
# Example: hardcoded root password in /etc/shadow
root:$1$abc$D3f4ultP4ssw0rdH4sh:0:0:root:/root:/bin/sh
```

### 2. Command Injection

Web interfaces in IoT devices frequently pass user input to shell commands without sanitization.

```c
// Vulnerable C code example
void handle_ping(char *target) {
    char cmd[256];
    // User-controlled 'target' is injected directly into a shell command
    sprintf(cmd, "ping -c 4 %s", target);
    system(cmd);  // If target = "8.8.8.8; cat /etc/shadow", game over
}
```

### 3. Buffer Overflows

Embedded systems often lack memory protections, making buffer overflows particularly dangerous.

```c
// Vulnerable code -- no bounds checking
void parse_request(int sock) {
    char buffer[128];
    read(sock, buffer, 1024);  // reads up to 1024 bytes into a 128-byte buffer
}
```

### 4. Insecure Update Mechanisms

- Firmware updates downloaded over HTTP (not HTTPS).
- No signature verification on firmware images.
- Symmetric encryption keys embedded in the firmware itself.

### 5. Debug Interfaces Left Enabled

- Telnet or SSH services running with default credentials.
- Debug web pages accessible without authentication.
- UART console access without a password prompt.

---

## Practical Exercise

1. Download a known-vulnerable firmware image (e.g., from the Damn Vulnerable Router Firmware project or firmware images on exploit-db).
2. Scan it with Binwalk and extract the filesystem.
3. Run Firmwalker against the extracted filesystem.
4. Manually search for hardcoded credentials and interesting configuration files.
5. Identify the versions of key libraries (OpenSSL, BusyBox, etc.) and check for known CVEs.
6. Open a key binary in Ghidra and locate calls to `system()` or `strcpy()`.

---

## Summary

Firmware analysis is a foundational skill in IoT security research. The workflow generally follows this pattern:

1. **Obtain** the firmware (download, intercept, or dump from flash).
2. **Extract** the contents (Binwalk, manual carving).
3. **Enumerate** interesting files (Firmwalker, manual search).
4. **Identify** vulnerabilities (credentials, outdated libraries, unsafe code).
5. **Reverse engineer** key binaries (Ghidra, radare2).
6. **Automate** where possible (EMBA for comprehensive analysis).

The vulnerabilities you discover during firmware analysis often become the foundation for building full exploit chains, which we will cover in later modules.

---

## Additional Resources

- [Binwalk Documentation](https://github.com/ReFirmLabs/binwalk)
- [Ghidra Official Site](https://ghidra-sre.org/)
- [EMBA Firmware Analyzer](https://github.com/e-m-b-a/emba)
- [Firmware Analysis Toolkit (FAT)](https://github.com/attify/firmware-analysis-toolkit)
- [OWASP Firmware Security Testing Methodology](https://owasp.org/www-project-firmware-security-testing-methodology/)
- Craig Smith, *The Car Hacker's Handbook* (firmware analysis chapters)
- Aaron Guzman & Aditya Gupta, *IoT Penetration Testing Cookbook*
