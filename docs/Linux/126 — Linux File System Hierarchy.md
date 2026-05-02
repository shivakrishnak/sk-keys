---
layout: default
title: "Linux File System Hierarchy"
parent: "Linux"
nav_order: 126
permalink: /linux/linux-file-system-hierarchy/
number: "0126"
category: Linux
difficulty: ★☆☆
depends_on: Operating System, File System, Kernel
used_by: Shell Scripting, Package Managers, File Permissions, SSH
related: File Permissions, Symbolic Links, /proc File System
tags:
  - linux
  - os
  - foundational
  - internals
---

# 126 — Linux File System Hierarchy

⚡ TL;DR — Linux organises every file on the system into one unified tree rooted at `/`, with each directory serving a specific, standardised purpose defined by the FHS.

| #126            | Category: Linux                                          | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Operating System, File System, Kernel                    |                 |
| **Used by:**    | Shell Scripting, Package Managers, File Permissions, SSH |                 |
| **Related:**    | File Permissions, Symbolic Links, /proc File System      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine every Linux distribution placing configuration files wherever it pleased — one distro puts Apache's config in `/etc/httpd`, another in `/usr/local/apache/conf`, another in `/home/www/config`. A shell script written for Ubuntu fails silently on CentOS. A package manager can't predict where to install binaries. An admin switching between servers spends hours hunting for files. Without a standard layout, every system becomes an island.

**THE BREAKING POINT:**
When the number of files on a Unix system grew into the hundreds of thousands, the absence of conventions created real operational failures: install scripts overwrote system binaries, log rotation tools missed critical log directories, and backup scripts captured the wrong partitions. System recovery after a failure was guesswork.

**THE INVENTION MOMENT:**
The Filesystem Hierarchy Standard (FHS) was created to define where every category of file belongs on a UNIX-like system. Linux adopted it wholesale. Now every tool, every script, every admin expectation is anchored to a known map. This is exactly why the Linux File System Hierarchy exists.

---

### 📘 Textbook Definition

The **Linux File System Hierarchy** is a tree-structured namespace rooted at `/` (root) that organises all files, directories, devices, and virtual file systems on a Linux installation. It is defined by the **Filesystem Hierarchy Standard (FHS)**, maintained by the Linux Foundation. Every path on a Linux system is an absolute location within this single tree, regardless of which physical device or network share the underlying storage resides on. Mount points allow external storage to be grafted onto the tree, maintaining the unified namespace. The hierarchy separates concerns by purpose: system binaries (`/bin`, `/sbin`), user binaries (`/usr`), configuration (`/etc`), variable data (`/var`), temporary files (`/tmp`), process metadata (`/proc`), and device nodes (`/dev`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Linux has one giant directory tree starting at `/`; every file and device in the entire system is somewhere inside it.

**One analogy:**

> Think of a company building. The entire building is `/`. `/etc` is the admin office where all official policies and configurations are filed. `/bin` is the tool room with essential equipment. `/home` is the employees' personal offices. `/var` is the mailroom — things constantly arrive and leave. `/tmp` is the whiteboard — anything written here may be erased when the cleaning crew (reboot) comes in.

**One insight:**
The key insight is that Linux has **one tree**, not one per disk. A second hard drive, a USB stick, and a network share all appear as subdirectories within the same tree. The OS hides the physical complexity behind a unified path namespace.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every file has exactly one absolute path from root `/`.
2. Directories are files (everything in Linux is a file).
3. Mount points graft arbitrary storage into the tree at any node.

**DERIVED DESIGN:**
Given that one tree must represent every resource — local disk, NFS share, hardware device, kernel data — the designers had to choose a partitioning criterion. They chose **purpose/category** rather than physical location. This leads to the FHS layout where the separation of concerns is temporal and access-pattern based:

- Files that rarely change (`/bin`, `/lib`) can be on a read-only filesystem.
- Files that change constantly (`/var/log`, `/tmp`) need a separate fast partition.
- Per-machine configuration (`/etc`) must be backed up differently than user data (`/home`).
- Virtual filesystems (`/proc`, `/sys`) are never on disk at all — they are kernel data structures projected as files.

```
LINUX DIRECTORY TREE (partial):

/                   ← root of everything
├── bin/            ← essential user binaries (ls, cp, cat)
├── sbin/           ← system binaries (root-only tools)
├── etc/            ← configuration files (text, editable)
├── home/           ← user home directories
│   └── alice/
├── root/           ← root user's home
├── var/            ← variable data (logs, spools, databases)
│   ├── log/
│   └── cache/
├── tmp/            ← temporary files (cleared on reboot)
├── usr/            ← user programs (second major subtree)
│   ├── bin/        ← non-essential user binaries
│   ├── lib/        ← libraries for /usr/bin
│   └── local/      ← admin-installed software
├── lib/            ← libraries for /bin and /sbin
├── dev/            ← device nodes (sda, tty, null, random)
├── proc/           ← virtual: kernel/process data
├── sys/            ← virtual: hardware/driver data
├── boot/           ← kernel image, bootloader
├── mnt/            ← manual mount points
└── media/          ← auto-mounted removable media
```

**THE TRADE-OFFS:**
**Gain:** Universal predictability — any script, tool, or admin finds files where expected on any FHS-compliant system.
**Cost:** Rigidity — installing software outside the standard paths (e.g., in `/opt` or `/usr/local`) requires care to avoid conflicts, and some non-standard distros or container images diverge, breaking assumptions.

---

### 🧪 Thought Experiment

**SETUP:**
You write a deployment script for your web app that reads its config from `/etc/myapp/config.yaml`, writes logs to `/var/log/myapp/`, and stores uploaded files in `/var/data/myapp/`. You deploy to production.

**WHAT HAPPENS WITHOUT THE HIERARCHY STANDARD:**
Your colleague sets up a second server and places config in `/opt/myapp/config.yaml` because "that's where we put apps." Your deployment script fails with `File not found`. The on-call engineer, unfamiliar with the second server's layout, spends 30 minutes hunting for where the config actually lives. Logs end up in three different places. Backup policies miss `/opt`.

**WHAT HAPPENS WITH THE HIERARCHY STANDARD:**
Every FHS-compliant server agrees: config → `/etc/`, logs → `/var/log/`, binaries → `/usr/bin/`. Your script runs identically on every server. The backup tool knows to include `/etc` and `/var`. Log rotation tools find `/var/log/myapp/` automatically. The on-call engineer goes straight to `/etc/myapp/config.yaml` without guessing.

**THE INSIGHT:**
The hierarchy is a shared contract. Scripts, tools, and humans are all clients of the same API. When everyone honours the contract, the entire ecosystem becomes predictable at zero runtime cost.

---

### 🧠 Mental Model / Analogy

> Think of the FHS as a city zoning map. `/` is the entire city. Residential zones (`/home`), industrial zones (`/var`), government buildings (`/etc`), public parks (`/tmp`) — each zone has rules about what can be placed there. Just as a city building inspector can walk into any compliant building and find the fire exits in the expected location, a sysadmin can walk into any FHS-compliant Linux box and find the configuration in `/etc`.

- "Residential zones" → `/home` (user personal files)
- "Government buildings" → `/etc` (system-wide configuration)
- "Industrial zones" → `/var` (logs, databases, spools)
- "Public parks" → `/tmp` (ephemeral scratch space)
- "Underground utilities" → `/proc`, `/sys` (kernel plumbing)
- "City hall / essential services" → `/bin`, `/sbin`, `/lib`

**Where this analogy breaks down:** unlike a city where zones are geographically separate, Linux directories can be on the same physical disk or on completely different ones — the zoning is logical, not physical.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Linux keeps all its files in one giant folder structure, like a tree. The top is called `/` (the root). Every file on the computer — programs, settings, your documents — lives somewhere inside this tree. There are conventions about which kind of file goes where so everyone can find things.

**Level 2 — How to use it (junior developer):**
Know the essential directories: `/etc` for config files, `/var/log` for logs, `/home/<username>` for your files, `/tmp` for throwaway files. When installing a service, put configs in `/etc/servicename/`, logs go to `/var/log/servicename/`. Use `ls /` to see the top level. Use `man hier` for the full specification.

**Level 3 — How it works (mid-level engineer):**
The hierarchy is implemented through the VFS (Virtual File System) layer in the kernel, which presents a unified tree regardless of the underlying filesystem type (ext4, xfs, tmpfs, nfs). Mount points (`/proc`, `/sys`, `/dev`) are virtual — they have no corresponding blocks on disk. The kernel populates them dynamically. `/proc` entries are generated on-the-fly when a process reads them; no I/O to disk occurs. `/tmp` is often mounted as `tmpfs` (RAM-backed), making it much faster than disk but volatile across reboots.

**Level 4 — Why it was designed this way (senior/staff):**
The split between `/` (essential early-boot tools) and `/usr` (the bulk of userland) is a historical artifact from the days when `/usr` lived on a separate disk mounted after boot. Modern systems have largely unified these via symlinks (on systemd distros, `/bin` → `/usr/bin`). The `/opt` directory was added for "optional" software packages that don't fit the FHS layout — commonly used by commercial software like Oracle DB or Google Chrome to avoid polluting `/usr/local`. Immutable infrastructure patterns in containers often place the entire application in `/app` or `/srv` because the container image itself provides isolation, making FHS conventions less critical there.

---

### ⚙️ How It Works (Mechanism)

The kernel boots and mounts the root filesystem at `/`. Every subsequent filesystem must be **mounted** at a directory inside the existing tree:

```
┌──────────────────────────────────────────────────────┐
│        LINUX FILESYSTEM MOUNT ARCHITECTURE           │
├──────────────────────────────────────────────────────┤
│                      /  (root)                       │
│           mounted from /dev/sda1 (ext4)              │
│                                                      │
│  /etc    /home     /var      /proc    /sys   /tmp     │
│           │         │         │                │     │
│        /dev/sda2  /dev/sdb1  [kernel  [kernel tmpfs]  │
│        (ext4)     (xfs)      virtual] virtual]       │
└──────────────────────────────────────────────────────┘
```

When you access `/home/alice/notes.txt`:

1. Kernel walks the directory tree from `/`.
2. At `/home`, VFS checks the mount table — `/home` is mounted from `/dev/sda2`.
3. Kernel hands off to the ext4 driver for `/dev/sda2`.
4. Ext4 resolves `alice/notes.txt` within its tree.
5. Returns file content to the process.

When you access `/proc/1/status`:

1. Kernel walks to `/proc` — mount table shows `procfs` virtual FS.
2. Kernel generates the content of `status` on the fly from the process table for PID 1.
3. Nothing is read from disk. No file exists.

**Key directories in detail:**

| Directory | Purpose                                     | Notes                                  |
| --------- | ------------------------------------------- | -------------------------------------- |
| `/bin`    | Essential binaries (`ls`, `cp`, `bash`)     | Symlink → `/usr/bin` on modern distros |
| `/sbin`   | System admin binaries (`fdisk`, `iptables`) | Symlink → `/usr/sbin`                  |
| `/etc`    | Configuration files                         | Text files; human-editable             |
| `/home`   | User home directories                       | Per-user writable space                |
| `/var`    | Variable data                               | Logs, mail spools, databases           |
| `/tmp`    | Temporary files                             | Cleared on reboot (tmpfs)              |
| `/usr`    | User programs hierarchy                     | Largest subtree                        |
| `/lib`    | Shared libraries for `/bin`, `/sbin`        | `.so` files                            |
| `/dev`    | Device nodes                                | Block and char devices                 |
| `/proc`   | Process/kernel virtual FS                   | No disk I/O                            |
| `/sys`    | Hardware/driver virtual FS                  | No disk I/O                            |
| `/opt`    | Optional/third-party software               | Self-contained installs                |
| `/srv`    | Service data (web roots, FTP data)          | Optional                               |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
App requests open("/var/log/app/server.log")
    ↓
Kernel VFS layer receives syscall
    ↓
VFS walks path: / → var → log → app
    ↓
At /var: consults mount table
    ← YOU ARE HERE (/var is on /dev/sdb1, xfs)
    ↓
XFS driver resolves "log/app/server.log"
    ↓
Returns file descriptor to process
    ↓
App writes log entry via fd
```

**FAILURE PATH:**

```
/var partition fills to 100%
    ↓
App write() returns ENOSPC
    ↓
App crashes or loses log entries
    ↓
Observable: "No space left on device" in kernel log
```

**WHAT CHANGES AT SCALE:**
At scale, `/var/log` becomes a hotspot. High-throughput services write millions of log lines/second; placing `/var` on a slow shared disk causes write stalls. Production systems dedicate separate fast SSDs or use in-memory log buffers with async flush. `/tmp` on `tmpfs` is standard; at high concurrency, tmpfs contention can appear in `perf` traces as memory bandwidth saturation.

---

### 💻 Code Example

**Example 1 — Navigating the hierarchy:**

```bash
# Show the root tree (first two levels)
ls -la /

# Find all config files for nginx
ls /etc/nginx/

# Find where a binary lives
which nginx
# → /usr/sbin/nginx

# Find what package owns a file
dpkg -S /usr/sbin/nginx        # Debian/Ubuntu
rpm -qf /usr/sbin/nginx        # RHEL/CentOS
```

**Example 2 — Standard placement for a new service:**

```bash
# BAD: scattering files in non-standard locations
mkdir /root/myapp
cp config.yaml /root/myapp/
./myapp > /root/myapp.log 2>&1

# GOOD: follow FHS conventions
sudo mkdir -p /etc/myapp          # config
sudo mkdir -p /var/log/myapp      # logs
sudo mkdir -p /var/lib/myapp      # persistent data
sudo cp config.yaml /etc/myapp/
sudo useradd -r -s /sbin/nologin myapp  # service user
sudo chown -R myapp:myapp /var/log/myapp /var/lib/myapp
```

**Example 3 — Checking disk usage per hierarchy node:**

```bash
# Where is disk space being consumed?
du -sh /* 2>/dev/null | sort -rh | head -10

# Check /var specifically (often fills first)
du -sh /var/* 2>/dev/null | sort -rh | head -10

# Check what's mounted where
df -h
# or
findmnt
```

---

### ⚖️ Comparison Table

| Approach                    | Predictability | Flexibility | Best For                    |
| --------------------------- | -------------- | ----------- | --------------------------- |
| **FHS standard layout**     | High           | Medium      | All system-level services   |
| `/opt/<vendor>/<app>`       | Medium         | High        | Commercial/third-party apps |
| Container `/app` convention | Medium         | High        | Containerised workloads     |
| Nix/Guix store paths        | Very high      | High        | Reproducible builds         |

**How to choose:** Use FHS for system services and packages managed by the distro's package manager. Use `/opt` for self-contained third-party installs. In containers, FHS matters less — use a clean `/app` layout since the container image provides the isolation.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `/bin` and `/usr/bin` are different directories  | On modern systemd distros, `/bin` is a symlink to `/usr/bin`; they are the same directory                                   |
| Files in `/tmp` are deleted periodically         | `/tmp` is cleared on reboot, not continuously; `systemd-tmpfiles` may clean files older than 10 days on some distros        |
| `/proc` is a real filesystem on disk             | `/proc` is a virtual filesystem (procfs) generated by the kernel entirely in memory                                         |
| `/root` is the root of the filesystem            | `/root` is the home directory of the `root` user; the root of the filesystem is `/`                                         |
| `/usr` stands for "user"                         | Originally yes; in modern usage it means "Unix System Resources" — it holds the bulk of the system's programs and libraries |
| Moving files between directories is always cheap | Moving across filesystem boundaries (different mount points) requires a copy + delete, not just an inode rename             |

---

### 🚨 Failure Modes & Diagnosis

**Full /var Partition**

**Symptom:**
Services fail to start or write logs; `journalctl` shows "No space left on device"; databases refuse writes.

**Root Cause:**
`/var` holds logs, spools, and database files. Unrotated logs or a runaway process can fill it. Since many services write to `/var`, a full `/var` brings down unrelated services.

**Diagnostic Command:**

```bash
df -h /var
du -sh /var/* 2>/dev/null | sort -rh | head -20
```

**Fix:**

```bash
# Clear old logs (safe)
journalctl --vacuum-size=500M
find /var/log -name "*.log.*" -mtime +7 -delete
```

**Prevention:**
Mount `/var` on a separate partition with adequate headroom; configure `logrotate` for every service.

---

**Wrong Path Used for Config (Works Locally, Fails in Production)**

**Symptom:**
App finds config in development but fails in staging/production with "config file not found."

**Root Cause:**
Developer placed config in a non-standard path (`~/myapp/config.yaml`); production service runs as a different user with no access to that path.

**Diagnostic Command:**

```bash
# Check where the process is actually looking
strace -e openat ./myapp 2>&1 | grep config
```

**Fix:**
Move config to `/etc/myapp/config.yaml`; update app to read from that path.

**Prevention:**
Always use FHS-standard paths for service config from day one; codify in Dockerfile or systemd unit file.

---

**Symlink Confusion (/bin vs /usr/bin)**

**Symptom:**
A script hardcodes `#!/bin/bash`; on a system where `/bin` is a symlink to `/usr/bin`, it works. On an older system without the symlink, it may break (or vice versa for unusual Busybox setups).

**Root Cause:**
The `/bin` → `/usr/bin` merge happened gradually across distros; scripts written for one assumption fail on the other.

**Diagnostic Command:**

```bash
ls -la /bin
# If it shows: /bin -> usr/bin, they are merged
```

**Fix:**
Use `/usr/bin/env bash` in shebang lines for portability; avoid hardcoded paths for interpreters.

**Prevention:**
Use `#!/usr/bin/env bash` universally; test scripts on target distros.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Operating System` — the Linux kernel provides the VFS layer that implements the hierarchy
- `File System` — ext4, xfs, tmpfs are the underlying filesystems mounted into the tree

**Builds On This (learn these next):**

- `File Permissions (chmod, chown)` — permission rules apply to every node in the hierarchy
- `Shell Scripting` — scripts rely on standard paths to locate binaries and config
- `Package Managers (apt, yum, dnf)` — package managers install files into FHS-defined locations
- `Symbolic Links / Hard Links` — used to maintain FHS compatibility while merging directories

**Alternatives / Comparisons:**

- `/proc File System` — virtual filesystem mounted at `/proc`; a specialised node in the hierarchy
- `/sys File System` — hardware/driver interface mounted at `/sys`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One unified directory tree from /         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No standard = files anywhere; scripts     │
│ SOLVES       │ and tools break across systems            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ /proc and /sys are kernel data in         │
│              │ memory — no disk I/O ever                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — it's the layout of the OS        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't put app data in /bin or /etc root   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Predictability vs. install flexibility    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The map every Linux admin memorises      │
│              │  to navigate any server in seconds"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ File Permissions → Users and Groups →     │
│              │ /proc File System                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Docker container starts from a minimal Alpine Linux image. The image does not follow FHS conventions — binaries are in `/bin` (no `/usr/bin` merge), and `/etc` contains only a handful of files. Your entrypoint script uses `#!/usr/bin/env bash`, but the container fails immediately. Walk through the exact lookup chain the kernel executes when resolving `/usr/bin/env`, and explain why the failure occurs and what two different fixes exist.

**Q2.** A production system mounts `/var` on its own 50 GB partition, but `/tmp` is on the root partition. A data-processing job writes 60 GB of temporary files to `/tmp`. The root partition fills up, killing the SSH daemon (which can no longer write to its `/var/run` pid file). Trace why killing SSH is the observable symptom of a `/tmp` overflow, and describe how `tmpfs` mount configuration would have prevented this.
