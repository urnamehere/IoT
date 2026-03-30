---
title: "Challenge: Firmware Secrets"
level: Intermediate
description: "A firmware image contains hardcoded credentials. Extract them."
points: 200
hints:
  - "Start with binwalk -e"
  - "Look in /etc/ directories"
  - "The password is base64 encoded"
---

# Challenge: Firmware Secrets

## Scenario

Your company acquired a batch of IoT smart sensors from a third-party manufacturer. Before deploying them on the corporate network, the security team needs to verify that the firmware does not contain hardcoded credentials or backdoors. You have obtained a copy of the firmware image. Your mission is to extract the filesystem, find the hidden credentials, and retrieve the flag.

## Objectives

1. Extract the firmware image using appropriate tools.
2. Navigate the extracted filesystem.
3. Locate hardcoded credentials hidden within configuration files.
4. Decode the obfuscated password to retrieve the flag.

## Rules

- You may use any tools available on your analysis machine (Binwalk, strings, grep, find, base64, etc.).
- The flag format is `FLAG{some_text_here}`.
- Do not execute any extracted binaries on your host system (use a VM or container if you want to run them).
- Time limit: 30 minutes.

---

## Challenge Environment Setup (For Instructors)

Use the following script to create the practice firmware image. This builds a fake SquashFS filesystem embedded in a firmware-like binary.

```bash
#!/bin/bash
# Create the challenge firmware image

WORKDIR=$(mktemp -d)
FSROOT="$WORKDIR/rootfs"

# Build a minimal filesystem
mkdir -p "$FSROOT"/{bin,etc,etc/config,var/www,usr/lib,tmp}

# /etc/passwd with a backdoor account
cat << 'EOF' > "$FSROOT/etc/passwd"
root:x:0:0:root:/root:/bin/sh
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
sensoradmin:x:0:0:Sensor Admin:/root:/bin/sh
EOF

# /etc/shadow with a weak hash
cat << 'EOF' > "$FSROOT/etc/shadow"
root:$1$xyz$abc123hashnotreal:18000:0:99999:7:::
sensoradmin:$1$ctf$7mJgBPKEFh7SUvBG5.F/k.:18000:0:99999:7:::
EOF

# Hidden config file with base64-encoded credentials
cat << 'EOF' > "$FSROOT/etc/config/sensor.conf"
# Sensor Configuration
[network]
mode=dhcp
fallback_ip=192.168.4.1

[cloud]
endpoint=https://api.sensorcloud.example.com/v2
api_key=sk-prod-8f3a2b1c4d5e6f7890abcdef

[management]
# Remote management credentials
admin_user=superadmin
admin_pass=RkxBR3tmaXJtdzRyM19zM2NyM3RzX2V4cDBzM2R9
# DO NOT CHANGE - factory default for provisioning
EOF

# A web interface config with more secrets
cat << 'EOF' > "$FSROOT/var/www/config.php"
<?php
// Database configuration
define('DB_HOST', 'localhost');
define('DB_USER', 'sensor_db');
define('DB_PASS', 'factoryDBpass!2023');
define('DB_NAME', 'sensordata');

// API token for cloud sync
define('CLOUD_TOKEN', 'eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYWRtaW4ifQ.fakesignature');
?>
EOF

# SSL private key left in the filesystem
mkdir -p "$FSROOT/etc/ssl/private"
openssl genrsa 2048 2>/dev/null > "$FSROOT/etc/ssl/private/server.key"

# An init script that reveals the update server
cat << 'EOF' > "$FSROOT/etc/init.d/S99cloud"
#!/bin/sh
# Cloud sync daemon
CLOUD_USER="updater"
CLOUD_PASS="upd4t3_s3rv1c3!"
wget -q "http://update.sensorcloud.example.com/check?auth=${CLOUD_USER}:${CLOUD_PASS}" -O /tmp/update_status
EOF
chmod +x "$FSROOT/etc/init.d/S99cloud"

# Build the SquashFS image
mksquashfs "$FSROOT" "$WORKDIR/rootfs.sqsh" -comp gzip -quiet

# Create a fake firmware header and combine
python3 -c "
import struct, os
header = b'SENS'                          # Magic bytes
header += struct.pack('<I', 0x00010003)   # Version 1.3
header += struct.pack('<I', os.path.getsize('$WORKDIR/rootfs.sqsh'))
header += b'\x00' * (64 - len(header))   # Pad header to 64 bytes
with open('$WORKDIR/rootfs.sqsh', 'rb') as f:
    sqsh_data = f.read()
with open('/tmp/ctf_sensor_firmware_v1.3.bin', 'wb') as f:
    f.write(header)
    f.write(sqsh_data)
"

echo "[+] Firmware image created: /tmp/ctf_sensor_firmware_v1.3.bin"

# Cleanup
rm -rf "$WORKDIR"
```

**Place the generated firmware file where participants can download it** (e.g., an HTTP server on the challenge network or a shared directory).

---

## Getting Started

Download the firmware image to your analysis machine:

```bash
mkdir -p ~/ctf-firmware && cd ~/ctf-firmware
# Replace with the actual download URL provided by your instructor
wget http://challenge-server/ctf_sensor_firmware_v1.3.bin
```

Think about:
- What tools can identify the contents of a binary firmware file?
- How are IoT filesystems typically packaged inside firmware images?
- Where do Linux systems store credentials and configuration?
- What encoding might be used to obfuscate a password?

---

<details>
<summary><strong>Hint 1 (click to reveal)</strong></summary>

Run Binwalk to identify what is inside the firmware image:

```bash
binwalk ctf_sensor_firmware_v1.3.bin
```

Then extract it:

```bash
binwalk -e ctf_sensor_firmware_v1.3.bin
```

</details>

<details>
<summary><strong>Hint 2 (click to reveal)</strong></summary>

After extraction, navigate into the SquashFS root and look in the `/etc/` directory tree. Configuration files often store credentials:

```bash
find . -path '*/etc/*' -type f
```

Pay attention to files with `.conf` extensions.

</details>

<details>
<summary><strong>Hint 3 (click to reveal)</strong></summary>

The flag is hidden as a base64-encoded password. Look for strings that look like base64 (alphanumeric with possible `=` padding). Decode with:

```bash
echo "the_base64_string" | base64 -d
```

</details>

---

<details>
<summary><strong>Full Walkthrough (click to reveal)</strong></summary>

### Step 1: Analyze the firmware image

```bash
cd ~/ctf-firmware
file ctf_sensor_firmware_v1.3.bin
```

Output shows a generic binary file. Run Binwalk:

```bash
binwalk ctf_sensor_firmware_v1.3.bin
```

**Expected output:**

```
DECIMAL       HEXADECIMAL     DESCRIPTION
-----------------------------------------------------------
0             0x0             None
64            0x40            Squashfs filesystem, little endian, version 4.0, ...
```

Binwalk identifies a SquashFS filesystem starting at offset 64.

### Step 2: Extract the filesystem

```bash
binwalk -e ctf_sensor_firmware_v1.3.bin
cd _ctf_sensor_firmware_v1.3.bin.extracted/
ls -la
```

You should see a `squashfs-root/` directory.

```bash
cd squashfs-root/
ls -la
```

### Step 3: Search for credentials

Start by checking the usual locations:

```bash
cat etc/passwd
```

Notice the `sensoradmin` account with UID 0 (root-level access).

```bash
cat etc/shadow
```

Note the password hash for `sensoradmin`. This can be cracked, but it is not the flag.

Now search more broadly:

```bash
grep -rnI 'pass' etc/
```

**Output:**

```
etc/config/sensor.conf:admin_pass=RkxBR3tmaXJtdzRyM19zM2NyM3RzX2V4cDBzM2R9
etc/init.d/S99cloud:CLOUD_PASS="upd4t3_s3rv1c3!"
```

### Step 4: Decode the obfuscated password

The string `RkxBR3tmaXJtdzRyM19zM2NyM3RzX2V4cDBzM2R9` in `sensor.conf` looks like base64 (no special characters, appropriate length). Decode it:

```bash
echo "RkxBR3tmaXJtdzRyM19zM2NyM3RzX2V4cDBzM2R9" | base64 -d
```

**Output:**

```
FLAG{firmw4r3_s3cr3ts_exp0s3d}
```

### Step 5: Document all findings

The flag is: **`FLAG{firmw4r3_s3cr3ts_exp0s3d}`**

But a thorough analyst would also report these additional findings:

| Finding | Location | Severity |
|---------|----------|----------|
| Root-level backdoor account (`sensoradmin`) | `/etc/passwd` | Critical |
| Crackable password hash | `/etc/shadow` | Critical |
| Base64-encoded admin credentials | `/etc/config/sensor.conf` | Critical |
| Hardcoded API key | `/etc/config/sensor.conf` | High |
| Database credentials in web config | `/var/www/config.php` | Critical |
| Cloud JWT token | `/var/www/config.php` | High |
| SSL private key shipped in firmware | `/etc/ssl/private/server.key` | Critical |
| Update server credentials in init script | `/etc/init.d/S99cloud` | Critical |

### What you learned

- Firmware images often contain full filesystems that can be trivially extracted.
- Credentials are frequently hardcoded in configuration files and scripts.
- Base64 is encoding, not encryption -- it provides zero security.
- A single firmware image can expose an entire product line if credentials are shared across devices.

</details>

---

## Scoring

| Criteria | Points |
|----------|--------|
| Successfully extracted the firmware filesystem | 40 |
| Found the sensor.conf configuration file | 30 |
| Decoded the base64 password to get the flag | 80 |
| Documented additional security findings (bonus) | 50 |
| **Total** | **200** |
