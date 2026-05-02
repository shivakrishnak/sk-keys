---
layout: default
title: "/sys File System"
parent: "Linux"
nav_order: 146
permalink: /linux/sys-file-system/
number: "0146"
category: Linux
difficulty: ★★★
depends_on: /proc File System, Linux File System Hierarchy, Kernel Modules
used_by: Observability & SRE, Linux Performance Tuning, Cgroups
related: /proc File System, Kernel Modules, Cgroups
tags:
  - linux
  - os
  - internals
  - deep-dive
---

# 146 — /sys File System

⚡ TL;DR — `/sys` is a virtual filesystem that exposes the kernel's internal device and driver model as a structured hierarchy — one file per attribute, one attribute per file, for precise hardware and subsystem control.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`/proc` became a dumping ground for any kernel data anyone wanted to expose — system memory, network counters, hardware quirks, all mixed together in an ad-hoc namespace with no consistent structure. To tune a block device's scheduler or read a CPU's cache topology, you'd write ioctl() calls specific to each driver — no consistency, no discovery, no composability.

**THE BREAKING POINT:**
A storage engineer needs to change the I/O scheduler for one specific disk from `cfq` to `deadline` on a running production server. With `/proc` there's no standard location; with ioctl it requires knowing the specific device's control interface. Each driver exposes its own non-standard mechanism.

**THE INVENTION MOMENT:**
This is exactly why `/sys` (sysfs) was created. It exports the kernel's unified device model — the internal `kobject` hierarchy that tracks every device and driver — as a strict file tree where every file contains exactly one value. Every block device exposes its I/O scheduler at a predictable path; every CPU exposes its frequency at a predictable path.

---

### 📘 Textbook Definition

sysfs is a virtual filesystem (type `sysfs`) introduced in Linux 2.6 that exports the kernel's internal object hierarchy as a filesystem tree. Each directory represents a kernel object (`kobject`) — a device, driver, subsystem, or bus. Each file represents one attribute of that object (one value per file). sysfs is mounted at `/sys` and provides a structured, discoverable interface for hardware configuration and monitoring. It complements `/proc`: `/proc` handles process and global tuning; `/sys` handles hardware device model and device-specific attributes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`/sys` maps the kernel's hardware device tree to files — one attribute per file — giving structured access to every device on the system.

**One analogy:**

> `/sys` is like a building's electrical panel directory. Each circuit breaker has a clearly labelled slot (one file per attribute). You can read the breaker's status or flip it by interacting with that exact slot. Nothing bleeds over — the kitchen breaker is in its own clearly labelled spot, completely separate from the bathroom breaker.

**One insight:**
The "one file = one value" discipline makes `/sys` fundamentally different from `/proc`. Reading `/sys/block/sda/queue/scheduler` returns exactly the current scheduler. There's no need to parse multi-line output or grep for a specific field. This makes `/sys` ideal for scripted configuration.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. One file = one value. No multi-value files.
2. Every device in the kernel model has a corresponding directory.
3. The hierarchy mirrors the kernel's internal kobject tree.
4. Writes trigger kernel callbacks in the device's driver.

**DERIVED DESIGN:**
The kernel's driver model centres on `kobject` — a reference-counted object with a name, parent pointer, and attribute list. `sysfs_create_file()` creates a file backed by show()/store() callbacks; reading calls show(), writing calls store(). This means `/sys` is effectively a structured RPC interface to kernel drivers — each file is a typed, named parameter.

The hierarchy follows the device topology: `/sys/bus/` (buses like PCI, USB), `/sys/devices/` (actual devices with physical hierarchy), `/sys/class/` (logical groupings like `net/`, `block/`), `/sys/block/` (block devices). Symlinks connect the same device across multiple views.

**THE TRADE-OFFS:**
**Gain:** Strict structure, discoverable, one-value-per-file atomicity, no parsing needed.
**Cost:** Deeply nested paths are verbose; some attributes are write-once or only valid in specific device states; documentation is often sparse.

---

### 🧪 Thought Experiment

**SETUP:**
You have two SSDs in a server: `sda` (OS disk, needs low latency) and `sdb` (data disk, needs maximum throughput). You want different I/O schedulers for each.

**WHAT HAPPENS WITHOUT /sys:**
The I/O scheduler is a per-device setting deep in the block layer. Without sysfs you need a device-specific ioctl, or you modify kernel compile-time defaults (requires recompile and reboot), or you write a kernel module just to call the block layer API. None of these are feasible at runtime.

**WHAT HAPPENS WITH /sys:**

```bash
# Set low-latency scheduler for OS disk
echo "mq-deadline" > \
  /sys/block/sda/queue/scheduler

# Set high-throughput scheduler for data disk
echo "kyber" > \
  /sys/block/sdb/queue/scheduler

# Verify
cat /sys/block/sda/queue/scheduler
```

Runtime change, per-device, no reboot, no recompile. The store() callback in the block layer receives the string and switches the scheduler live.

**THE INSIGHT:**
sysfs turns driver internals into first-class, composable shell operations. The discipline of one-value-per-file is what makes this work — the caller always knows exactly what they're reading or writing.

---

### 🧠 Mental Model / Analogy

> `/sys` is like a hotel room's control panel — every room (device) has the same panel layout: thermostat, lights, TV — each labelled, each its own control. To change the temperature in room 312 (sda queue depth), you go to room 312's panel (path) and turn the thermostat knob (write a value). You never accidentally adjust room 313 and you don't need to know the hotel's wiring diagram.

- "Hotel room" → kernel device kobject
- "Control panel" → device's sysfs directory
- "Each labelled control" → one file per attribute
- "Turning a knob" → writing to a sysfs file triggers store() callback

Where this analogy breaks down: sysfs attributes don't always have safe defaults — writing an incorrect value can crash a driver or put hardware in an unrecoverable state, unlike a hotel thermostat.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`/sys` is a special folder that shows all the hardware in your computer as a file tree. Each piece of hardware has its own folder, and inside it are files that tell you about the hardware and let you change settings. Reading a file shows the current value; writing a number to it changes the setting.

**Level 2 — How to use it (junior developer):**
Common reads: `cat /sys/class/net/eth0/operstate` (network card up/down), `cat /sys/class/thermal/thermal_zone0/temp` (CPU temperature in millidegrees), `cat /sys/block/sda/size` (disk size in 512-byte blocks). Common writes: `echo 1 > /sys/class/net/eth0/carrier` (carrier detect), `echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` (CPU frequency governor).

**Level 3 — How it works (mid-level engineer):**
Every `/sys` file is backed by a `sysfs_ops` with `show()` and `store()` functions registered by the driver. `show()` is called on read and must write to a buffer, returning the number of bytes. `store()` is called on write with the string the user provided. The kernel enforces that sysfs files are ≤ PAGE_SIZE (4 KB) — preventing them from becoming `/proc`-style multi-value files. Device symlinks in `/sys/class/net/eth0/` → `/sys/devices/...` allow both logical (by function) and physical (by bus topology) navigation to the same device.

**Level 4 — Why it was designed this way (senior/staff):**
sysfs was designed by Greg Kroah-Hartman in 2.6 specifically to solve `/proc` chaos and to export the new unified device model. The kobject hierarchy was itself a major refactoring of Linux's ad-hoc driver registration code into a reference-counted, lifecycle-managed object model. The one-value-per-file rule was non-negotiable: it allows atomic reads (a single read() syscall returns one complete value), avoids parse ambiguity, and enforces driver authors to think about what each attribute means. The tension is that it generates very verbose paths — `/sys/devices/pci0000:00/0000:00:1f.2/host0/target0:0:0/0:0:0:0/block/sda/queue/scheduler` — addressed partially by the `/sys/block/` and `/sys/class/` symlink shortcuts.

---

### ⚙️ How It Works (Mechanism)

**sysfs directory structure:**

```
/sys/
├── block/           → symlinks to block devices (sda, sdb, loop0)
├── bus/             → bus subsystems (pci, usb, i2c, platform)
│   ├── pci/devices/ → symlinks to PCI devices
│   └── usb/devices/ → symlinks to USB devices
├── class/           → logical device groupings
│   ├── net/         → network interfaces (eth0, lo, docker0)
│   ├── block/       → block devices
│   └── thermal/     → thermal zones
├── dev/             → by-major:minor-number device lookup
├── devices/         → physical device hierarchy (root)
│   └── system/
│       ├── cpu/     → per-CPU attributes
│       └── memory/  → memory blocks
├── firmware/        → firmware interface (ACPI, EFI)
├── fs/              → filesystem-specific attributes
│   └── cgroup/      → cgroup hierarchy (v1)
├── kernel/          → kernel subsystem attributes
│   └── mm/          → memory management
└── module/          → loaded kernel modules
```

**Common /sys operations:**

```bash
# Network interface status
cat /sys/class/net/eth0/operstate    # up/down/unknown
cat /sys/class/net/eth0/speed        # speed in Mbps
cat /sys/class/net/eth0/statistics/rx_bytes  # bytes received
cat /sys/class/net/eth0/statistics/tx_dropped  # dropped TX

# Block device I/O scheduler
cat /sys/block/sda/queue/scheduler
# output: [mq-deadline] kyber bfq none
# (brackets show current; others are available)

# Change I/O scheduler
echo "mq-deadline" > /sys/block/sda/queue/scheduler

# Block device queue depth
cat /sys/block/sda/queue/nr_requests   # current queue depth
echo 256 > /sys/block/sda/queue/nr_requests  # increase it

# CPU frequency scaling
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# available: performance powersave ondemand schedutil
echo "performance" > \
  /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# CPU temperature (millidegrees Celsius)
cat /sys/class/thermal/thermal_zone0/temp
# divide by 1000 for degrees: 45000 → 45°C

# Memory block online/offline (for hot-plug memory)
cat /sys/devices/system/memory/memory0/state  # online/offline

# Enable/disable network interface
echo 1 > /sys/class/net/eth0/flags   # (typically use 'ip link' instead)

# PCI power management
cat /sys/bus/pci/devices/0000:00:1f.2/power/control
echo "on" > /sys/bus/pci/devices/0000:00:1f.2/power/control
```

**Reading device topology:**

```bash
# Full PCI device path for network card eth0
readlink -f /sys/class/net/eth0/device
# → /sys/devices/pci0000:00/0000:00:19.0/

# Find which NUMA node an NVMe drive is on
cat /sys/block/nvme0n1/device/numa_node

# Identify disk model
cat /sys/block/sda/device/model
cat /sys/block/sda/device/vendor

# List all network interfaces and their types
ls /sys/class/net/
for iface in /sys/class/net/*/; do
  echo "$(basename $iface): $(cat $iface/operstate)"
done
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  WRITE TO /sys: CHANGE I/O SCHEDULER        │
└─────────────────────────────────────────────┘

 Admin: echo "mq-deadline" > \
        /sys/block/sda/queue/scheduler
       │
       ▼
 VFS write() syscall
       │
       ▼
 sysfs store() dispatcher
       │  looks up kobject for sda/queue/scheduler
       ▼
 elevator_store() in block/elevator.c  ← YOU ARE HERE
       │  parses "mq-deadline" string
       ▼
 blk_mq_init_sched() called
       │  validates new scheduler name
       ▼
 Existing scheduler flushed, queue drained
       │
       ▼
 New mq-deadline scheduler initialised
       │
       ▼
 All subsequent I/Os use new scheduler
 No reboot required
```

**FAILURE PATH:**
Unsupported scheduler name → store() returns `-EINVAL` → shell: "bash: echo: write error: Invalid argument" → no change made.

**WHAT CHANGES AT SCALE:**
In large deployments, sysfs tuning is applied via configuration management (Ansible, Puppet) at boot via `udev` rules or `/etc/rc.local`. At container scale, sysfs writes to `/sys/fs/cgroup/` control resource limits for individual containers — this is how Docker and Kubernetes implement CPU and memory limits without modifying individual processes.

---

### 💻 Code Example

**Example 1 — Performance tuning script:**

```bash
#!/bin/bash
# Apply production I/O tuning for NVMe SSDs
# (run as root)

for dev in /sys/block/nvme*/; do
  devname=$(basename "$dev")

  # Use none scheduler (NVMe handles its own queueing)
  echo "none" > "${dev}queue/scheduler"

  # Increase queue depth for high-IOPS NVMe
  echo 1024 > "${dev}queue/nr_requests"

  # Disable read-ahead (SSDs don't benefit)
  echo 0 > "${dev}queue/read_ahead_kb"

  echo "Tuned $devname: scheduler=none, depth=1024"
done

# Set CPU to performance mode during business hours
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/; do
  echo "performance" > "${cpu}scaling_governor"
done
```

**Example 2 — Network interface monitoring:**

```bash
#!/bin/bash
# Monitor NIC statistics for errors
NIC=${1:-eth0}
SYS="/sys/class/net/$NIC/statistics"

while true; do
  rx_err=$(cat "$SYS/rx_errors")
  tx_err=$(cat "$SYS/tx_errors")
  rx_drop=$(cat "$SYS/rx_dropped")
  rx_bytes=$(cat "$SYS/rx_bytes")

  echo "$(date +%H:%M:%S) rx_err=$rx_err" \
       "tx_err=$tx_err rx_drop=$rx_drop" \
       "rx_MB=$(( rx_bytes / 1048576 ))"
  sleep 5
done
```

**Example 3 — udev rule to apply sysfs tuning automatically:**

```bash
# /etc/udev/rules.d/60-io-scheduler.rules
# Auto-apply scheduler when block device is added

# NVMe SSDs: no scheduler (device handles queuing)
ACTION=="add", KERNEL=="nvme[0-9]n[0-9]", \
  ATTR{queue/scheduler}="none", \
  ATTR{queue/nr_requests}="1024"

# HDDs: use bfq for fairness
ACTION=="add", KERNEL=="sd[a-z]", \
  ATTR{queue/rotational}=="1", \
  ATTR{queue/scheduler}="bfq"
```

---

### ⚖️ Comparison Table

| Interface  | Structure                    | Atomicity         | Discovery     | Best For                       |
| ---------- | ---------------------------- | ----------------- | ------------- | ------------------------------ |
| **/sys**   | Strict hierarchy, 1 val/file | Yes (single file) | Yes (ls/find) | Hardware config, device tuning |
| /proc      | Loose, multi-value files     | Partial           | Partial       | Process data, global tuning    |
| ioctl      | Per-device, binary           | Yes               | No            | Low-level device control       |
| udev rules | Event-driven                 | At hotplug        | Via udevadm   | Automated device configuration |
| sysctl     | Flat namespace               | Yes               | Via sysctl -a | Kernel networking/VM params    |

How to choose: use `/sys` for device-specific attributes (scheduler, queue depth, power management); use `/proc/sys/` (via sysctl) for global kernel parameters (TCP settings, VM swappiness); use ioctl only when sysfs doesn't expose what you need.

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                        |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| /sys and /proc serve the same purpose           | /proc is for process data and global tuning; /sys is for the hardware device model — they are complementary, not redundant                     |
| Writing to /sys is always safe to undo          | Some writes are irreversible (e.g., putting a memory block offline); always verify recovery steps before changing production hardware settings |
| /sys files persist across reboots               | /sys is a virtual filesystem; writes are lost on reboot; use udev rules or init scripts to persist settings                                    |
| All /sys attributes are documented              | Many are undocumented driver internals; always check kernel source or driver documentation before relying on specific paths                    |
| /sys/block/sda is the physical disk's only view | /sys/block/sda is a symlink to /sys/devices/pci.../...; both paths access the same kobject                                                     |

---

### 🚨 Failure Modes & Diagnosis

**Write to /sys Silently Does Nothing**

**Symptom:**
`echo "performance" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` returns no error but the governor doesn't change.

**Root Cause:**
The CPU driver doesn't support that governor, or the system is using a different power management layer (e.g., acpi-cpufreq vs intel_pstate — intel_pstate only supports `performance` and `powersave`).

**Diagnostic Command:**

```bash
# List actually available governors
cat /sys/devices/system/cpu/cpu0/cpufreq/\
scaling_available_governors

# Identify active driver
cat /sys/devices/system/cpu/cpu0/cpufreq/\
scaling_driver
```

**Fix:**
Use only governors listed in `scaling_available_governors`; check driver documentation for constraints.

**Prevention:**
Always read available options before writing new values to `/sys`.

---

**Scheduler Change Not Applied to All Disks**

**Symptom:**
I/O performance is inconsistent between disks after applying a scheduler change; one disk still uses the old scheduler.

**Root Cause:**
The script only changed the first disk; other disks need individual changes (sysfs changes are per-device, not global).

**Diagnostic Command:**

```bash
# Check all block devices' schedulers
for dev in /sys/block/*/; do
  sched=$(cat "$dev/queue/scheduler" 2>/dev/null)
  echo "$(basename $dev): $sched"
done
```

**Fix:**
Apply changes in a loop over all target devices (see Code Example 1 above).

**Prevention:**
Use udev rules to apply settings automatically to any matching device as it appears.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `/proc File System` — `/sys` was created to address limitations of `/proc`; understanding procfs first provides context
- `Linux File System Hierarchy` — `/sys` is in the standard FHS; understanding VFS is foundational
- `Kernel Modules` — loadable modules register their attributes in `/sys` via kobjects

**Builds On This (learn these next):**

- `Cgroups` — cgroup v1 hierarchies are exposed under `/sys/fs/cgroup/`; cgroup v2 is fully integrated into sysfs
- `Linux Performance Tuning` — most runtime kernel parameter tuning is done through `/sys` and `/proc/sys/`
- `Observability & SRE` — monitoring agents read hardware metrics from `/sys/class/` for CPU, memory, and network stats

**Alternatives / Comparisons:**

- `/proc File System` — handles process-level and global system parameters; less structured than sysfs
- `ioctl` — lower-level, device-specific control; required when no sysfs interface exists
- `sysctl` — command-line interface that reads/writes `/proc/sys/` parameters with named paths

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Virtual FS exposing the kernel device     │
│              │ model as a hierarchy: one file=one value  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ /proc mixed process data with hardware    │
│ SOLVES       │ config in an inconsistent, unstructured   │
│              │ namespace                                 │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Writes trigger store() callbacks in the   │
│              │ driver — sysfs is a structured driver RPC │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Tuning device parameters (I/O scheduler,  │
│              │ CPU governor, NIC queue depth)            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Changes must persist across reboots;      │
│              │ use udev rules or sysctl.conf instead     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Strict discoverability vs verbose paths;  │
│              │ atomic writes vs reboot-non-persistent    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A structured control panel for every     │
│              │  piece of hardware in the kernel"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ udev → cgroups → eBPF                    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes worker node has its CPU governor set to `powersave` by the cloud provider's default. Your latency-sensitive ML inference workload is showing high P99 latencies during CPU-intensive bursts. You change the governor to `performance` via `/sys`. Two weeks later the setting has reverted. Trace why it reverted and design a solution using both udev rules and Kubernetes node configuration to make the setting permanent and verifiable from within the cluster.

**Q2.** You're debugging why two NVMe SSDs on the same server have wildly different latency profiles despite identical hardware. You discover they're on different PCI buses and NUMA nodes. Explain what information in `/sys` would reveal this (specific file paths), how NUMA distance affects I/O performance, and what `/sys` attributes you would change to optimise each drive's performance for its specific topology.
