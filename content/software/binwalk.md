---
title: "Binwalk"
level: Intermediate
description: "Firmware extraction and binary analysis tool"
order: 3
---

# Binwalk

## What Is Binwalk?

Binwalk is a tool for searching binary images for embedded files and executable code. In IoT security, its primary purpose is extracting filesystems and other components from firmware images. When you download (or dump) firmware from an IoT device, it arrives as a single binary blob that typically contains:

- A bootloader (U-Boot, etc.)
- A Linux kernel or RTOS image
- One or more filesystems (SquashFS, JFFS2, CramFS, ext2/4)
- Configuration data
- Sometimes additional resources (web interface files, certificates, scripts)

Binwalk scans the binary for magic bytes (file signatures) and can automatically extract each component, giving you access to the device's entire filesystem -- configuration files, startup scripts, hardcoded credentials, encryption keys, web applications, and compiled binaries.

## Installation

```bash
# Debian/Ubuntu (includes extraction dependencies)
sudo apt install binwalk

# Install all optional extraction tools for maximum capability
sudo apt install mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full \
  cabextract cramfsswap squashfs-tools sleuthkit default-jdk lzop srecord

# Install sasquatch (handles non-standard SquashFS, very important for IoT)
git clone https://github.com/devttys0/sasquatch.git
cd sasquatch && sudo ./build.sh

# Fedora
sudo dnf install binwalk squashfs-tools mtd-utils

# macOS
brew install binwalk
pip install jefferson  # JFFS2 extraction

# From pip (latest version)
pip install binwalk

# From source (latest development version)
git clone https://github.com/ReFirmLabs/binwalk.git
cd binwalk && sudo python3 setup.py install
```

### Why sasquatch Matters

Many IoT firmware images use modified or vendor-specific SquashFS formats with non-standard compression (LZMA variants, custom headers). The standard `unsquashfs` tool cannot extract these. `sasquatch` is a patched version that handles the non-standard variations found in real-world IoT firmware. Without it, extraction of many router and camera firmware images will fail silently, leaving you with an empty directory.

## Scanning Firmware Images

### Basic Signature Scan

```bash
# Scan a firmware image and list detected components
binwalk firmware.bin

# Example output:
# DECIMAL       HEXADECIMAL     DESCRIPTION
# ---------------------------------------------------------------
# 0             0x0             uImage header, header size: 64 bytes,
#                               image size: 1455781 bytes, ...
# 64            0x40            LZMA compressed data, properties: 0x5D,
#                               dictionary size: 8388608 bytes
# 1455872       0x163880        Squashfs filesystem, little endian,
#                               version 4.0, compression:xz, size: 6281412 bytes
```

This output tells you:
- There is a U-Boot image header at offset 0
- LZMA compressed data (likely the kernel) starts at offset 64
- A SquashFS filesystem starts at offset 0x163880 (1,455,872 bytes into the file)

### Verbose Scan

```bash
# Show more detail about each signature match
binwalk -v firmware.bin
```

### Scan with Specific Signature Types

```bash
# Only scan for filesystem signatures
binwalk -R firmware.bin

# Scan for specific magic patterns
binwalk -m /usr/share/binwalk/magic/filesystems firmware.bin

# Custom magic byte search
binwalk -R "\x68\x73\x71\x73" firmware.bin  # Search for "hsqs" (SquashFS magic)
```

### Comparing Two Firmware Versions

```bash
# Hexdiff between two firmware images to find what changed in an update
binwalk -W firmware_v1.bin firmware_v2.bin

# This highlights byte-level differences, useful for understanding
# what a firmware update patches
```

## Extracting Filesystems

### Automatic Extraction

```bash
# Extract all recognized components
binwalk -e firmware.bin

# This creates a directory: _firmware.bin.extracted/
# Inside you'll find extracted components, including the filesystem

# List what was extracted
ls -la _firmware.bin.extracted/

# Example contents:
# 40            -- LZMA compressed data (decompressed)
# 163880.squashfs -- The SquashFS filesystem
# squashfs-root/  -- Mounted/extracted SquashFS contents
```

### Manual Extraction

Sometimes automatic extraction fails or you need more control:

```bash
# Extract a specific range of bytes using dd
# Extract the SquashFS starting at offset 0x163880, size 6281412 bytes
dd if=firmware.bin of=rootfs.squashfs bs=1 skip=1455872 count=6281412

# Mount or extract the SquashFS
sudo unsquashfs rootfs.squashfs
# Or with sasquatch for non-standard variants:
sasquatch rootfs.squashfs

# Extract JFFS2 filesystems
# First, create a simulated MTD device
sudo modprobe mtdram total_size=32768 erase_size=128
sudo modprobe mtdblock
sudo dd if=jffs2_image.bin of=/dev/mtdblock0
sudo mount -t jffs2 /dev/mtdblock0 /mnt/jffs2

# Or use jefferson (Python JFFS2 extractor)
jefferson jffs2_image.bin -d output_dir
```

### Dealing with Encrypted or Obfuscated Firmware

Some manufacturers encrypt or obfuscate their firmware. Signs of encryption:

```bash
# High, uniform entropy across the entire image (see Entropy Analysis below)
binwalk -E firmware.bin

# If the entropy graph is a flat line near 1.0, the firmware is likely
# encrypted or compressed. If binwalk finds no signatures, suspect encryption.
```

Strategies for encrypted firmware:
1. Look for an older firmware version that might not be encrypted
2. Dump firmware directly from the device's flash chip (it is stored decrypted)
3. Find the decryption key in the bootloader or a previous firmware version
4. Analyze the update mechanism to understand how the device decrypts it

## Entropy Analysis

Entropy analysis measures the randomness of data at each point in the file. It reveals the structure of a firmware image visually.

```bash
# Generate an entropy graph
binwalk -E firmware.bin

# Save the entropy plot to a file
binwalk -E -J firmware.bin  # Creates a PNG file
```

### Reading the Entropy Graph

```
Entropy: 1.0 |     ████████████████████████████
             |     █                          █
         0.8 |     █                          █████████████████
             |     █                          █
         0.6 |█████                           █
             |█                               █
         0.4 |█                               █
             |█                               █
         0.2 |█                               █
             |█                               █
         0.0 └──────────────────────────────────────────────────
              0        offset -->            end

              ^        ^                      ^
              |        |                      |
           Header   Compressed kernel     Compressed filesystem
         (low entropy) (high entropy)     (high entropy)
```

**Interpretation:**
- **Low entropy (0.0-0.4):** Uncompressed data, ASCII text, headers, padding. Easy to analyze directly.
- **Medium entropy (0.4-0.7):** Executable code, structured binary data.
- **High entropy (0.8-1.0):** Compressed data OR encrypted data. Compressed data will have detectable magic bytes; encrypted data typically will not.
- **Flat line at ~1.0 with no signatures:** Almost certainly encrypted.

## Recursive Extraction

```bash
# Recursively extract all nested archives and filesystems
binwalk -eM firmware.bin

# This follows the extraction chain:
# firmware.bin -> compressed kernel + squashfs
#   squashfs -> filesystem with tar.gz files
#     tar.gz -> more files inside
# All levels are extracted automatically

# Limit recursion depth to avoid infinite loops
binwalk -eM --depth=3 firmware.bin
```

**Warning:** Recursive extraction can consume a lot of disk space. Some firmware images contain many nested layers. Monitor disk usage:

```bash
# Check extraction size
du -sh _firmware.bin.extracted/
```

## Combining with Other Tools

### Post-Extraction Analysis Workflow

After extracting a filesystem, here is a systematic approach to finding security issues:

```bash
# Navigate to the extracted filesystem
cd _firmware.bin.extracted/squashfs-root/

# 1. Find hardcoded credentials
grep -r "password" etc/ --include="*.conf" --include="*.cfg"
grep -r "passwd" etc/
cat etc/shadow  # Check for password hashes
cat etc/passwd  # Check for user accounts

# 2. Find private keys and certificates
find . -name "*.pem" -o -name "*.key" -o -name "*.crt" -o -name "*.p12"
find . -name "id_rsa" -o -name "id_dsa" -o -name "authorized_keys"

# 3. Find configuration files with sensitive data
find . -name "*.conf" -o -name "*.cfg" -o -name "*.ini" -o -name "*.json"
cat etc/config/*.conf

# 4. Examine startup scripts (reveal services, credentials, backdoors)
cat etc/init.d/*
cat etc/rc.local
cat etc/inittab

# 5. Find web application files (often contain API keys, endpoints)
find . -path "*/www/*" -o -path "*/htdocs/*" -o -path "*/webroot/*"
find . -name "*.php" -o -name "*.lua" -o -name "*.cgi"

# 6. Find compiled binaries for reverse engineering
find . -executable -type f | xargs file | grep "ELF"

# 7. Check for debug/backdoor access
grep -r "telnetd" etc/
grep -r "dropbear" etc/  # Lightweight SSH server
grep -r "backdoor\|debug\|test" etc/init.d/
```

### Using strings for Quick Wins

```bash
# Extract readable strings from a binary
strings -n 8 firmware.bin | grep -i "password\|secret\|key\|token\|api"

# Search for URLs and IP addresses
strings firmware.bin | grep -E "https?://|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"

# Find potential command injection points
strings some_binary | grep -E "system\(|popen\(|exec\(|sprintf\("
```

### Using firmwalker

[firmwalker](https://github.com/craigz28/firmwalker) automates the post-extraction analysis:

```bash
git clone https://github.com/craigz28/firmwalker.git
cd firmwalker
./firmwalker.sh /path/to/_firmware.bin.extracted/squashfs-root/
```

It automatically searches for passwords, crypto keys, URLs, email addresses, and other interesting artifacts.

### Using EMBA (Embedded Analyzer)

[EMBA](https://github.com/e-m-b-a/emba) is a comprehensive firmware analysis framework:

```bash
git clone https://github.com/e-m-b-a/emba.git
cd emba
sudo ./installer.sh
sudo ./emba -f /path/to/firmware.bin -l /path/to/output/
```

EMBA performs static analysis including binary hardening checks, CVE identification, and credential detection.

## Common Firmware Formats

### U-Boot Images

U-Boot is the most common bootloader in IoT devices. Firmware images often start with a U-Boot header:

```
Magic: 0x27051956
Header size: 64 bytes
Contains: image type, compression, load address, entry point
```

```bash
# Inspect U-Boot header
binwalk -A firmware.bin  # Look for opcodes indicating architecture
mkimage -l firmware.bin  # Use U-Boot's own tool to parse the header
```

### SquashFS

Read-only compressed filesystem. By far the most common root filesystem format in IoT devices.

```bash
# Identify SquashFS version and compression
binwalk firmware.bin | grep -i squash

# Extract
unsquashfs rootfs.squashfs      # Standard SquashFS
sasquatch rootfs.squashfs       # Non-standard variants
```

### JFFS2

Journaling Flash File System, designed for raw flash memory. Common in older devices.

```bash
# Extract with jefferson
pip install jefferson
jefferson firmware.jffs2 -d extracted_jffs2/
```

### CramFS

Compressed ROM filesystem, less common but still found in some devices.

```bash
# Extract CramFS
fsck.cramfs --extract=extracted_cramfs firmware.cramfs
```

### UBIFS

Newer flash filesystem used in some modern IoT devices.

```bash
# Extract UBIFS (requires ubi_reader)
pip install ubi_reader
ubireader_extract_files firmware.ubi
```

### Bare Metal / RTOS Firmware

Not all IoT devices run Linux. Some use bare-metal code or an RTOS (FreeRTOS, Zephyr, etc.). These do not have a filesystem to extract. Instead:

```bash
# Look for strings, function names, and configuration data
strings firmware.bin > strings_output.txt

# Analyze the binary structure
binwalk -A firmware.bin  # Architecture detection via opcode signatures

# Load into Ghidra for reverse engineering (see the Ghidra guide)
```

## Practical Workflow: Router Firmware Analysis

Here is a complete example analyzing a typical router firmware:

```bash
# Step 1: Download firmware from manufacturer's website
wget https://example.com/firmware/router_v2.1.0.bin

# Step 2: Initial scan
binwalk router_v2.1.0.bin

# Step 3: Entropy check
binwalk -E router_v2.1.0.bin

# Step 4: Extract
binwalk -eM router_v2.1.0.bin
cd _router_v2.1.0.bin.extracted/squashfs-root/

# Step 5: Check for low-hanging fruit
cat etc/shadow
# root:$1$abc123$...:0:0:99999:7:::
# -> Crack this hash with John the Ripper or hashcat

grep -r "password" etc/ usr/lib/ --include="*.lua" --include="*.sh"
# -> Found hardcoded admin password in web interface Lua script

# Step 6: Examine the web server
ls -la usr/lib/lua/
# -> Contains the router's web management application

# Step 7: Look for command injection in CGI scripts
grep -rn "os.execute\|io.popen\|luci.sys.exec" usr/lib/lua/
# -> Found unsanitized user input passed to os.execute()

# Step 8: Check for update mechanism security
grep -rn "wget\|curl\|tftp" etc/init.d/ usr/sbin/
# -> Firmware updates downloaded over HTTP without signature verification
```

## Troubleshooting

### Binwalk Finds Nothing

- The firmware may be encrypted. Check entropy.
- The firmware may use an uncommon format. Try `file firmware.bin` and `hexdump -C firmware.bin | head -20`.
- The firmware may be a partial dump. Verify the file size matches expectations.

### Extraction Fails or Produces Empty Directories

- Install `sasquatch` for non-standard SquashFS.
- Install all optional dependencies (see Installation section).
- Try manual extraction with `dd` and then use format-specific tools.
- Check if the filesystem uses an uncommon block size or compression.

### Large Number of False Positives

```bash
# Increase the minimum string length for signature matching
binwalk --length=10 firmware.bin

# Use only validated signatures (reduces false positives)
binwalk -v firmware.bin | grep -v "WARNING"
```
