---
title: "Lab: Firmware Extraction & Analysis"
level: Intermediate
description: "Extract and analyze firmware from a practice image"
estimated_time: "60 minutes"
tools:
  - Binwalk
  - Firmwalker
  - strings
objectives:
  - Extract a firmware image
  - Navigate the extracted filesystem
  - Find hardcoded credentials
  - Identify vulnerable components
---

# Lab: Firmware Extraction & Analysis

## Overview

IoT device firmware often contains hardcoded credentials, private keys, configuration files, and vulnerable software components. In this lab you will download a practice firmware image, extract its filesystem using Binwalk, and systematically search for security-relevant information.

## Prerequisites

- A Linux machine (Kali Linux recommended)
- Root or sudo access
- Internet connection (to download the practice firmware)

### Install required tools

```bash
sudo apt update
sudo apt install -y binwalk squashfs-tools mtd-utils gzip bzip2 p7zip-full unzip \
  jefferson cramfsck sasquatch firmware-mod-kit
```

Install Firmwalker:

```bash
cd /opt
sudo git clone https://github.com/craigz28/firmwalker.git
sudo chmod +x /opt/firmwalker/firmwalker.sh
```

Install additional analysis tools:

```bash
sudo apt install -y foremost hexedit xxd file
```

---

## Step 1: Obtain a Practice Firmware Image

For this lab, use the Damn Vulnerable Router Firmware (DVRF) project, which is designed for learning.

```bash
mkdir -p ~/firmware-lab && cd ~/firmware-lab

# Download DVRF
wget https://github.com/praetorian-inc/DVRF/releases/download/v0.3/DVRF_v03.bin \
  -O DVRF_v03.bin
```

If DVRF is unavailable, you can also use firmware images from:
- **IoTGoat:** `https://github.com/OWASP/IoTGoat`
- **Firmware samples on firmware.re**
- **OpenWrt images** (for a safe, legal alternative): `https://downloads.openwrt.org/`

Verify the download:

```bash
file DVRF_v03.bin
md5sum DVRF_v03.bin
```

The `file` command should indicate a binary file, possibly identifying it as a specific format.

---

## Step 2: Initial Reconnaissance

Before extracting, gather information about the firmware image.

### Examine the file type

```bash
file DVRF_v03.bin
```

### Check the entropy

High-entropy regions suggest compressed or encrypted sections:

```bash
binwalk -E DVRF_v03.bin
```

This generates an entropy graph. Flat high-entropy blocks indicate compression. If the entire file has uniform high entropy, it may be encrypted (which is much harder to analyze).

### Search for readable strings

Get a first look at what is inside:

```bash
strings DVRF_v03.bin | head -100
```

Look for:
- URLs and IP addresses
- Usernames and passwords
- File paths (e.g., `/etc/passwd`, `/www/`)
- Software version strings
- Copyright notices (reveal the device vendor)

Filter for specific patterns:

```bash
# Find potential passwords
strings DVRF_v03.bin | grep -iE 'passw|secret|key|token|admin|root'

# Find URLs
strings DVRF_v03.bin | grep -iE 'http://|https://|ftp://'

# Find email addresses
strings DVRF_v03.bin | grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Find IP addresses
strings DVRF_v03.bin | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}'
```

---

## Step 3: Extract the Firmware with Binwalk

### Scan without extracting

First, see what Binwalk identifies inside the image:

```bash
binwalk DVRF_v03.bin
```

**Expected output (example):**

```
DECIMAL       HEXADECIMAL     DESCRIPTION
------------------------------------------------------------
0             0x0             TRX firmware header, little endian, ...
28            0x1C            LZMA compressed data, properties: 0x5D, ...
1048612       0x100024        Squashfs filesystem, little endian, version 4.0, ...
```

This tells you there is a compressed kernel starting near the beginning and a SquashFS filesystem further in.

### Extract everything

```bash
binwalk -e DVRF_v03.bin
```

**Flags explained:**
- `-e` -- Extract identified file types automatically

This creates a directory named `_DVRF_v03.bin.extracted/`.

### Alternative: force extraction with Matryoshka mode

If the first pass does not fully extract nested archives:

```bash
binwalk -Me DVRF_v03.bin
```

**Flags explained:**
- `-M` -- Matryoshka (recursively scan extracted files)
- `-e` -- Extract

---

## Step 4: Navigate the Extracted Filesystem

```bash
cd _DVRF_v03.bin.extracted/
ls -la
```

Look for a `squashfs-root/` directory, which contains the device's root filesystem.

```bash
cd squashfs-root/
ls -la
```

You should see a standard Linux directory structure:

```
bin/  dev/  etc/  lib/  mnt/  proc/  sbin/  tmp/  usr/  var/  www/
```

### Explore key directories

```bash
# View the filesystem structure
find . -type f | head -50

# Check what architecture the binaries are compiled for
file bin/busybox

# List web server files
ls -la www/

# List configuration files
ls -la etc/
```

---

## Step 5: Hunt for Hardcoded Credentials

This is the most critical part of firmware analysis. Credentials are frequently left in configuration files, scripts, and binaries.

### Check passwd and shadow files

```bash
cat etc/passwd
```

Look for:
- Accounts with UID 0 (root-level access)
- Accounts with password hashes inline (older systems)
- Non-standard user accounts

```bash
cat etc/shadow 2>/dev/null
```

If `shadow` is readable, attempt to crack any password hashes with John the Ripper:

```bash
sudo john etc/shadow --wordlist=/usr/share/wordlists/rockyou.txt
```

### Search configuration files for credentials

```bash
# Search for password patterns in all files
grep -rnI 'password' etc/ 2>/dev/null
grep -rnI 'passwd' etc/ 2>/dev/null
grep -rnI 'secret' etc/ 2>/dev/null
grep -rnI 'api_key' etc/ 2>/dev/null
grep -rnI 'token' etc/ 2>/dev/null

# Search for base64-encoded strings (potential obfuscated credentials)
grep -rnI '[A-Za-z0-9+/]\{20,\}=\{0,2\}' etc/ 2>/dev/null
```

### Check for SSH keys

```bash
find . -name 'id_rsa' -o -name 'id_dsa' -o -name 'id_ecdsa' -o -name '*.pem' -o -name '*.key'
```

If you find private keys, note them. Reused private keys across devices of the same model are a common vulnerability.

### Check web application files

```bash
# Look in web directories for hardcoded credentials
grep -rnI 'password' www/ 2>/dev/null
grep -rnI 'admin' www/ 2>/dev/null

# Look for database connection strings
grep -rnI 'mysql\|sqlite\|postgres' www/ 2>/dev/null
grep -rnI 'jdbc:' www/ 2>/dev/null
```

### Check startup scripts

```bash
cat etc/init.d/* 2>/dev/null | grep -iE 'passw|secret|key|credential'
cat etc/rc.d/* 2>/dev/null | grep -iE 'passw|secret|key|credential'
```

---

## Step 6: Run Firmwalker for Automated Analysis

Firmwalker automates many of the searches above and generates a comprehensive report.

```bash
cd ~/firmware-lab/_DVRF_v03.bin.extracted/squashfs-root/
/opt/firmwalker/firmwalker.sh . /tmp/firmwalker_report.txt
```

Review the report:

```bash
less /tmp/firmwalker_report.txt
```

Firmwalker checks for:
- Password files and shadow files
- SSL certificates and private keys
- Configuration files (`.conf`, `.cfg`, `.ini`)
- Database files
- Shell scripts with credentials
- Binary files linked against insecure libraries
- URLs, IP addresses, and email addresses

---

## Step 7: Identify Vulnerable Components

### Check software versions

```bash
# Look for version strings in binaries
strings bin/busybox | head -5

# Check library versions
ls -la lib/
strings lib/libc.so.* | grep -i 'version\|release'

# Look for package manifests
find . -name '*.ipk' -o -name '*.opk' -o -name 'Packages' 2>/dev/null
```

### Check for known vulnerable software

Once you have version numbers, cross-reference them against vulnerability databases:

- **NVD (National Vulnerability Database):** https://nvd.nist.gov/
- **CVE Details:** https://www.cvedetails.com/
- **Exploit-DB:** https://www.exploit-db.com/

For example, if you find `Dropbear SSH 2016.74`, search for CVEs associated with that version.

### Check for dangerous binary capabilities

```bash
# Find SUID binaries (can be used for privilege escalation)
find . -perm -4000 -type f

# Find world-writable files
find . -perm -0002 -type f

# Find binaries without stack protection
# (requires cross-compilation toolchain awareness)
file bin/* | grep -i 'not stripped'
```

---

## Step 8: Document Your Findings

Create a structured report of everything you discovered.

**Sample findings template:**

```
## Firmware Analysis Report
### Target: DVRF_v03.bin

**Architecture:** MIPS Little Endian
**Filesystem:** SquashFS v4.0
**Kernel:** Linux (version from strings output)

### Critical Findings

1. **Hardcoded root password**
   - Location: etc/shadow
   - Hash: $1$xxxx$xxxx
   - Cracked password: [result]
   - Risk: Critical

2. **Embedded SSH private key**
   - Location: etc/dropbear/dropbear_rsa_host_key
   - Risk: High (shared across all devices of this model)

3. **Cleartext API credentials**
   - Location: www/cgi-bin/config.cgi
   - Credential: admin / factorydefault
   - Risk: Critical

4. **Outdated BusyBox version**
   - Version: 1.x.x
   - Known CVEs: CVE-XXXX-XXXX
   - Risk: Medium

### Recommendations
- Remove hardcoded credentials; use per-device provisioning.
- Update BusyBox and other libraries to patched versions.
- Do not ship debug SSH keys in production firmware.
```

---

## Review Questions

1. What is the difference between SquashFS and JFFS2 filesystems? Why are they commonly used in IoT firmware?
2. Why might `binwalk -E` (entropy analysis) show a completely flat, high-entropy graph? What does this mean for analysis?
3. How can a manufacturer prevent firmware extraction and analysis? What are the limitations of each approach?
4. Why are hardcoded credentials especially dangerous in IoT devices compared to traditional software?
5. What is the risk of a shared SSH host key across all units of the same device model?

---

## Cleanup

```bash
rm -rf ~/firmware-lab
rm -f /tmp/firmwalker_report.txt
```

## Next Steps

- Proceed to **Lab: UART Serial Console Access** to learn how to physically connect to IoT devices.
- Try analyzing firmware from a different device or a more complex image.
- Explore dynamic analysis by emulating the extracted firmware with QEMU: `sudo apt install qemu-user-static` and run extracted binaries.
