---
id: LNX-053
title: "/sys Filesystem (hardware, devices, kernel objects)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-050, LNX-052
used_by: LNX-086, LNX-076
related: LNX-052, LNX-086, LNX-050
tags: [/sys, sysfs, udev, device-tree, hardware, kernel-objects, kobject, uevent]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/lnx/sys-filesystem/
---

## TL;DR

`/sys` (sysfs) is a virtual filesystem exposing the kernel's device model:
hardware devices, buses, drivers, and kernel objects as a directory hierarchy.
`/sys/class/net/eth0/` has network interface settings. `/sys/block/sda/`
has disk info. `/sys/class/net/eth0/speed` shows link speed. `/sys/bus/`
has PCI, USB device listings. Unlike `/proc` (process-centric), `/sys`
is hardware/object-centric. udev uses `/sys` to detect device changes and
auto-load drivers. Many files in `/sys` are writable (e.g., disk I/O
schedulers, power settings, LED controls). Not for general-purpose use -
prefer `ip`, `lsblk`, `lspci` for reading.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-053 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | /sys, sysfs, udev, kobject, device model, hardware, uevent, modalias |
| **Prerequisites** | LNX-050, LNX-052 |

---

### The Problem This Solves

**Problem 1**: You need to change the I/O scheduler for a specific disk from
`mq-deadline` to `none` (for NVMe) at runtime without rebooting. Writing
to `/sys/block/nvme0n1/queue/scheduler` does exactly this.

**Problem 2**: A USB device is plugged in. How does the kernel know which
module to load? udev reads the device's `modalias` attribute from
`/sys/bus/usb/devices/...` and calls `modprobe` with that alias.

**Problem 3**: You need to find the MAC address, link speed, and MTU of a
network interface without using `ip` (e.g., from a script that doesn't trust
PATH). All of this is in `/sys/class/net/eth0/`.

---

### Textbook Definition

**/sys filesystem (sysfs)**: A virtual filesystem (no disk backing) that
exposes the Linux kernel's device model. Represents: devices (physical and
virtual), buses (PCI, USB, platform), device drivers, kernel objects (kobjects).
Mounted at `/sys` automatically during boot.

**kobject (kernel object)**: The base type for all objects in the kernel's
device model. Each kobject appears as a directory in sysfs. Attributes
(file/directory inside the kobject directory) expose data or accept commands.
Reference-counted; created/destroyed as devices attach/detach.

**uevents**: Kernel events sent to userspace when sysfs objects are created
or destroyed (device plug/unplug). udevd listens for uevents via a netlink
socket and triggers rules (load drivers, create /dev entries, run scripts).

---

### Understand It in 30 Seconds

```bash
# === sysfs structure overview ===
ls /sys/
# block/ bus/ class/ dev/ devices/ firmware/ fs/ kernel/ module/ power/

# block/ : block devices
ls /sys/block/
# sda  sdb  nvme0n1  ...

# class/ : device classes (network, input, etc.)
ls /sys/class/
# block  input  net  power_supply  rtc  tty  ...

# bus/ : hardware buses
ls /sys/bus/
# pci  usb  platform  i2c  ...

# === Network interfaces ===
ls /sys/class/net/
# eth0  lo  docker0  wlan0  ...

cat /sys/class/net/eth0/speed         # link speed (Mbps): 1000
cat /sys/class/net/eth0/duplex        # full or half
cat /sys/class/net/eth0/address       # MAC address
cat /sys/class/net/eth0/mtu           # MTU (default 1500)
cat /sys/class/net/eth0/operstate     # up/down/unknown
cat /sys/class/net/eth0/statistics/rx_bytes  # received bytes

# Set MTU via sysfs (or use ip link):
echo 9000 > /sys/class/net/eth0/mtu   # enable jumbo frames

# === Block devices ===
ls /sys/block/sda/
# dev  device/  holders/  queue/  slaves/  stat  subsystem  uevent

cat /sys/block/sda/size               # total size in 512-byte sectors
cat /sys/block/sda/queue/rotational   # 0=SSD, 1=HDD
cat /sys/block/sda/queue/scheduler    # current I/O scheduler
cat /sys/block/sda/queue/nr_requests  # I/O queue depth

# Change I/O scheduler:
cat /sys/block/sda/queue/scheduler
# [mq-deadline] kyber bfq none
echo none > /sys/block/nvme0n1/queue/scheduler      # best for NVMe
echo mq-deadline > /sys/block/sda/queue/scheduler   # good for HDDs
echo bfq > /sys/block/sda/queue/scheduler           # desktop/interactive

# Optimal queue depth for SSD:
echo 128 > /sys/block/sda/queue/nr_requests
# Optimal for HDD:
echo 1 > /sys/block/sda/queue/nr_requests   # HDDs benefit from minimal queue

# === PCI devices ===
ls /sys/bus/pci/devices/
# 0000:00:00.0  0000:00:1f.0  ...

# Read device info:
PCIDEV="0000:00:1f.2"
cat /sys/bus/pci/devices/$PCIDEV/vendor    # hex vendor ID
cat /sys/bus/pci/devices/$PCIDEV/device    # hex device ID
cat /sys/bus/pci/devices/$PCIDEV/class     # device class
cat /sys/bus/pci/devices/$PCIDEV/driver    # symlink to driver (or no file)

# === modalias: device-to-driver mapping ===
cat /sys/bus/pci/devices/0000:02:00.0/modalias
# pci:v00008086d00001521sv...
# This is what udev passes to modprobe for automatic driver loading

# === USB devices ===
ls /sys/bus/usb/devices/
cat /sys/bus/usb/devices/1-1/idVendor     # USB vendor ID
cat /sys/bus/usb/devices/1-1/idProduct    # USB product ID
cat /sys/bus/usb/devices/1-1/product      # Product name string
cat /sys/bus/usb/devices/1-1/manufacturer # Manufacturer string

# === Power management ===
cat /sys/class/net/eth0/device/power/control  # auto or on
echo on > /sys/class/net/eth0/device/power/control  # disable power management

# === Hardware info helpers (prefer these over raw sysfs) ===
lspci                        # list PCI devices (reads /sys/bus/pci)
lsusb                        # list USB devices (reads /sys/bus/usb)
lsblk                        # list block devices (reads /sys/block)
ip link show                 # network interfaces (reads /sys/class/net)
```

---

### First Principles

**sysfs directory hierarchy:**
```
/sys/
  block/
    sda -> ../devices/pci0000:00/0000:00:1f.2/ata1/host0/.../sda
    nvme0n1 -> ../devices/pci0000:00/0000:03:00.0/nvme/nvme0/nvme0n1

  bus/
    pci/
      devices/
        0000:00:00.0/   <- each PCI device by bus:device.function
      drivers/
        ahci/           <- SATA controller driver
        nvme/           <- NVMe driver
    usb/
      devices/
        usb1/           <- USB controller
        1-1/            <- device at port 1

  class/
    net/
      eth0 -> ../../devices/pci0000:00/.../net/eth0
    block/
      sda -> ../../devices/pci.../sda
    input/
      event0/           <- input events (keyboard, mouse)

  devices/
    pci0000:00/         <- the real device tree
      0000:00:1f.2/     <- SATA controller
        ata1/           <- ATA interface
          host0/        <- SCSI host
            ...
              sda/      <- the actual disk object

The class/ and bus/ directories are SYMLINKS into devices/
This means: multiple views of the same physical device
```

**How udev uses sysfs for auto device configuration:**
```
1. Hardware event: USB drive plugged in

2. Kernel creates kobject in /sys/bus/usb/devices/1-1/

3. Kernel sends uevent (via netlink):
   ACTION=add
   DEVPATH=/bus/usb/devices/1-1
   SUBSYSTEM=usb
   MODALIAS=usb:v0781p5594d...

4. udevd receives uevent, processes rules in /lib/udev/rules.d/:
   SUBSYSTEM=="usb", ATTR{idVendor}=="0781", ATTR{idProduct}=="5594", \
     SYMLINK+="sandisk_usb"
   (Rules can: set permissions, create symlinks, run programs, load modules)

5. Default rule triggers: kmod load "$MODALIAS"
   -> modprobe usb_storage (found via modalias match in modules.alias)
   -> kernel USB mass storage driver loads

6. Driver creates block device:
   uevent for /sys/block/sdb: ACTION=add
   udevd processes: creates /dev/sdb

7. User can now mount /dev/sdb
```

---

### Thought Experiment

Optimizing I/O schedulers via sysfs:

```bash
# NVMe SSDs: optimal scheduler is "none" (no reordering needed)
# Traditional HDDs: need scheduler to reorder I/O for seek optimization

# Check current schedulers:
for disk in /sys/block/*/; do
    name=$(basename "$disk")
    rot=$(cat "$disk/queue/rotational" 2>/dev/null)
    sched=$(cat "$disk/queue/scheduler" 2>/dev/null)
    type=$( [[ "$rot" == "0" ]] && echo "SSD/NVMe" || echo "HDD")
    echo "$name ($type): $sched"
done
# nvme0n1 (SSD/NVMe): [none] mq-deadline kyber
# sda (HDD): [mq-deadline] kyber bfq none

# Apply optimal schedulers:
for disk in /sys/block/*/; do
    rot=$(cat "$disk/queue/rotational" 2>/dev/null)
    if [[ "$rot" == "0" ]]; then
        echo none > "$disk/queue/scheduler"   # NVMe/SSD
    else
        echo mq-deadline > "$disk/queue/scheduler"  # HDD
    fi
done

# Verify:
cat /sys/block/nvme0n1/queue/scheduler  # should show: [none]
cat /sys/block/sda/queue/scheduler      # should show: [mq-deadline]

# Persistent (via udev rules):
# /etc/udev/rules.d/60-scheduler.rules
cat > /etc/udev/rules.d/60-scheduler.rules << 'EOF'
# NVMe: no scheduler
ACTION=="add|change", KERNEL=="nvme[0-9]*", \
  ATTR{queue/rotational}=="0", \
  ATTR{queue/scheduler}="none"

# HDD: mq-deadline
ACTION=="add|change", KERNEL=="sd[a-z]", \
  ATTR{queue/rotational}=="1", \
  ATTR{queue/scheduler}="mq-deadline"

# SSD: mq-deadline (still benefits from some merging)
ACTION=="add|change", KERNEL=="sd[a-z]", \
  ATTR{queue/rotational}=="0", \
  ATTR{queue/scheduler}="mq-deadline"
EOF

# Apply without reboot:
udevadm trigger --subsystem-match=block
```

---

### Mental Model / Analogy

```
/sys = the building's facilities management panel
  (every wire, pipe, and circuit exposed and labeled)

/sys/class/ = organized by function (power outlets, switches, etc.)
  /sys/class/net/ = all network sockets in the building
  /sys/class/block/ = all power outlets
  /sys/class/input/ = all light switches and thermostats

/sys/bus/ = organized by how things connect
  /sys/bus/pci/ = devices connected via PCI backplane
  /sys/bus/usb/ = devices connected via USB ports

/sys/devices/ = the actual floor plan (where things physically are)
  (class/ and bus/ are just labeled directories of the same rooms)

kobject = a labeled room with attributes written on the door
  door = directory in sysfs
  attributes = files in that directory
  reading a file = checking the label
  writing a file = sending an instruction

udev = the building's auto-configuration system
  watches for new rooms appearing (uevent)
  reads the labels (modalias, subsystem, vendor)
  loads the right equipment (kernel modules)
  creates the right control panel entry (/dev/sdX)

Reading sysfs = checking the facilities panel
Writing sysfs = flipping a switch on the panel
  (change I/O scheduler, adjust power, set LED brightness)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`/sys/class/net/IFACE/` (network interface info), `/sys/block/DISK/` (block
device info), `/sys/block/DISK/queue/scheduler` (I/O scheduler). Know that
sysfs is the kernel's device model, mounted at `/sys`, and udev uses it for
automatic device configuration. Prefer `ip`, `lsblk`, `lspci` for reading
device info (they read sysfs but present it better).

**Level 2:**
`modalias` attribute (device identity for module loading). udev rules
(`/etc/udev/rules.d/`): match on SUBSYSTEM, ATTR, ENV; actions: RUN,
SYMLINK, NAME. `udevadm monitor` (watch uevents in real-time). `udevadm
info --query=all /sys/class/net/eth0` (full attribute dump). `udevadm test
/sys/class/block/sda` (simulate udev processing).

**Level 3:**
`/sys/kernel/mm/` (memory management): hugepages, transparent huge pages,
NUMA. `/sys/kernel/tracing/` (kernel tracing interface for ftrace). CPU
frequency: `/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`. Power
management: `/sys/class/power_supply/` (battery info). `/sys/class/leds/`
(LED control on embedded). ACPI: `/sys/firmware/acpi/`. EFI variables:
`/sys/firmware/efi/efivars/`.

**Level 4:**
sysfs and NUMA: `/sys/devices/system/node/` for NUMA topology. PCI power
management: `/sys/bus/pci/devices/*/power/`. Runtime PM: runtime power
management via sysfs. kobject reference counting: sysfs entries persist
as long as the kobject exists (linked to device lifecycle). Writing to
`/sys/bus/pci/drivers/DRIVER/bind` or `unbind`: manually bind/unbind
PCI devices to drivers (used for VFIO passthrough to VMs).

**Level 5:**
sysfs vs configfs: sysfs is kernel-driven (created by kernel when objects
exist). configfs is USER-driven (userspace creates entries, kernel uses them
- used by USB gadget framework, iSCSI target configuration). sysfs and
container isolation: containers get their own view of some `/sys` parts via
mount namespaces, but `/sys` is generally shared (security implication).
Kubernetes with `securityContext.allowPrivilegeEscalation=false` still allows
reading `/sys` but restricts writing. VFIO (Virtual Function I/O): uses
sysfs bind/unbind to reassign PCI devices from host drivers to `vfio-pci`
driver for VM passthrough.

---

### Code Example

**BAD - reading hardware info the wrong way:**
```bash
# BAD: Parsing raw sysfs directly for device listing:
for d in /sys/bus/pci/devices/*/vendor; do
    vendor=$(cat "$d")
    device=$(cat "${d%vendor}device")
    echo "PCI vendor=$vendor device=$device"
done
# 0x8086 0x1521  <- barely readable, no description

# GOOD: Use lspci (reads sysfs but decodes vendor/device IDs):
lspci -v              # human-readable with descriptions
lspci -nn             # shows both description and IDs: [8086:1521]
lspci -k              # shows which kernel driver is bound

# BAD: Writing I/O scheduler wrong:
echo "noop" > /sys/block/sda/queue/scheduler
# "noop" is the old name! On modern kernels: "none"
# Check valid schedulers:
cat /sys/block/sda/queue/scheduler
# [mq-deadline] kyber bfq none  <- only these are valid

# GOOD: Check available schedulers first:
cat /sys/block/sda/queue/scheduler
# Write only a valid value:
echo mq-deadline > /sys/block/sda/queue/scheduler
# Verify:
cat /sys/block/sda/queue/scheduler
# [mq-deadline] kyber bfq none  <- brackets show current
```

**GOOD - sysfs for monitoring and configuration:**
```bash
#!/bin/bash
# hardware-info.sh: Collect key hardware info from sysfs

echo "=== Network Interfaces ==="
for iface in /sys/class/net/*/; do
    name=$(basename "$iface")
    [[ "$name" == "lo" ]] && continue
    
    operstate=$(cat "$iface/operstate" 2>/dev/null || echo "unknown")
    speed=$(cat "$iface/speed" 2>/dev/null || echo "unknown")
    mtu=$(cat "$iface/mtu" 2>/dev/null || echo "unknown")
    mac=$(cat "$iface/address" 2>/dev/null || echo "unknown")
    
    printf "%-15s state=%-5s speed=%-8s mtu=%-6s mac=%s\n" \
        "$name" "$operstate" "${speed}Mbps" "$mtu" "$mac"
done

echo ""
echo "=== Block Devices ==="
for dev in /sys/block/*/; do
    name=$(basename "$dev")
    [[ "$name" == loop* ]] && continue
    
    size_sectors=$(cat "$dev/size" 2>/dev/null || echo 0)
    size_gb=$(echo "scale=1; $size_sectors * 512 / 1024 / 1024 / 1024" | bc 2>/dev/null || echo "?")
    rot=$(cat "$dev/queue/rotational" 2>/dev/null || echo "?")
    sched=$(cat "$dev/queue/scheduler" 2>/dev/null | grep -o '\[[^]]*\]' | tr -d '[]' || echo "?")
    type=$([[ "$rot" == "0" ]] && echo "SSD/NVMe" || echo "HDD")
    
    printf "%-12s %-10s size=%-8s scheduler=%s\n" \
        "$name" "$type" "${size_gb}GB" "$sched"
done

echo ""
echo "=== I/O Scheduler Recommendations ==="
for dev in /sys/block/sd* /sys/block/nvme*; do
    [[ -e "$dev" ]] || continue
    name=$(basename "$dev")
    rot=$(cat "$dev/queue/rotational" 2>/dev/null)
    current=$(cat "$dev/queue/scheduler" 2>/dev/null | grep -o '\[[^]]*\]' | tr -d '[]')
    
    if [[ "$rot" == "0" ]]; then
        recommended="none"
    else
        recommended="mq-deadline"
    fi
    
    if [[ "$current" == "$recommended" ]]; then
        echo "$name: OK (current=$current)"
    else
        echo "$name: SUBOPTIMAL (current=$current, recommended=$recommended)"
        echo "  Fix: echo $recommended > $dev/queue/scheduler"
    fi
done
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "/proc and /sys serve the same purpose" | Different focus. `/proc` is process-centric (one directory per PID) plus general system info and kernel parameters. `/sys` is hardware/device-centric (the kernel's object model). `/proc/sys/` has tunable kernel parameters. `/sys/` has device attributes and hardware configuration. They overlap slightly but serve different use cases: use `/proc` for process info and kernel parameters, `/sys` for device/hardware interaction. |
| "Writing to /sys files is always safe" | Writing to `/sys` directly modifies kernel state. Errors in values can cause hardware malfunction (e.g., wrong MTU crashes networking), driver crashes (wrong I/O scheduler for unsupported device type), or simply be silently ignored (kernel validates values). Always check valid values first (`cat /sys/block/sda/queue/scheduler` shows available options in brackets). |
| "udev only handles /dev entries" | udev does much more: loads kernel modules via `modprobe` (for device driver binding), creates persistent device names (udev rules can name USB drives by serial number), runs scripts on device events (mount filesystems, configure IP on network connect), sets device permissions, manages device power states, and creates symlinks in /dev and /run. The `MODALIAS` mechanism for module auto-loading is pure udev. |
| "All hardware appears in /sys" | Only hardware known to the kernel appears in `/sys`. Unsupported hardware (no driver) still appears in `/sys/bus/pci/devices/` but without a driver symlink (`ls /sys/bus/pci/devices/*/driver` shows nothing). Virtual devices (loopback interfaces, virtual bridges) appear in `/sys/class/net/` but have no corresponding bus entry. Some embedded hardware uses device tree firmware descriptions not visible in standard sysfs paths. |
| "Changing /sys settings persists across reboot" | No. `/sys` is a virtual filesystem - all changes are in kernel RAM and lost on reboot. For persistence: use udev rules (`/etc/udev/rules.d/`) to apply settings whenever a device is detected (at boot or hotplug), or use systemd services/tmpfiles.d for boot-time configuration. I/O scheduler changes via udev rules are the standard persistent approach. |

---

### Failure Modes & Diagnosis

**Device not working after reboot (scheduler, power, settings):**
```bash
# Symptom: Applied optimal I/O scheduler but reverted after reboot
echo none > /sys/block/nvme0n1/queue/scheduler   # works now, gone after reboot

# Fix: persistent via udev rules:
cat > /etc/udev/rules.d/60-ioscheduler.rules << 'EOF'
# NVMe: none (best for NVMe with native multi-queue)
ACTION=="add|change", SUBSYSTEM=="block", KERNEL=="nvme[0-9]*n[0-9]*", \
  ATTR{queue/scheduler}="none"

# SATA SSD: mq-deadline  
ACTION=="add|change", SUBSYSTEM=="block", KERNEL=="sd[a-z]", \
  ATTR{queue/rotational}=="0", \
  ATTR{queue/scheduler}="mq-deadline"
EOF

# Apply immediately (without reboot):
udevadm trigger --subsystem-match=block
udevadm settle   # wait for udev to finish

# Verify:
cat /sys/block/nvme0n1/queue/scheduler  # should show: [none]

# Debug udev rule evaluation:
udevadm test /sys/block/nvme0n1 2>&1 | grep -E "scheduler|ATTR"
```

---

### Related Keywords

**Foundational:**
LNX-050 (Kernel Modules), LNX-052 (/proc Filesystem)

**Builds on this:**
LNX-086 (Kernel Parameters), LNX-076 (I/O Schedulers)

**Related:**
LNX-086, LNX-076 (I/O Schedulers and tuning)

---

### Quick Reference Card

| Path | Purpose |
|------|---------|
| `/sys/class/net/IFACE/` | Network interface attributes |
| `/sys/block/DISK/queue/scheduler` | I/O scheduler |
| `/sys/block/DISK/queue/rotational` | 0=SSD, 1=HDD |
| `/sys/block/DISK/size` | Size in 512-byte sectors |
| `/sys/bus/pci/devices/*/driver` | Which driver is bound |
| `/sys/bus/*/devices/*/modalias` | Device identity for modprobe |
| `/sys/kernel/mm/transparent_hugepage/` | THP settings |

**3 things to remember:**
1. `/sys` is the kernel's hardware object model; `/proc` is process/parameter-focused
2. `/sys` changes are NOT persistent - use udev rules or systemd for persistence
3. udev reads `modalias` from `/sys` to auto-load kernel modules for new devices

---

### Transferable Wisdom

sysfs concepts appear in: Docker daemon reads `/sys/class/net/` to enumerate
network interfaces for creating virtual networks. cgroup v2 filesystem is
at `/sys/fs/cgroup/` (same virtual filesystem concept as sysfs, kernel
generates data on read). Kubernetes kubelet reads `/sys/block/` for disk
info and writes I/O scheduler settings via udev or startup scripts.
`/sys/class/power_supply/` is how laptop battery tools (upower, battery
applets) read battery level without special privileges.

udev's modalias mechanism appears in broader patterns: Kubernetes device
plugins (GPUs, FPGAs reported through similar discovery mechanism), cloud
provider instance metadata (AWS EC2 `curl http://169.254.169.254/latest/meta-data/`
is analogous - device info available via a special interface), Windows Device
Manager (same concept: device detected, driver matched by hardware ID,
driver loaded).

---

### The Surprising Truth

sysfs was created in Linux 2.5 (2002) specifically to REPLACE the ad-hoc
mess of `/proc` that had accumulated over years. Linus Torvalds was
increasingly unhappy with random kernel data being dumped into `/proc` with
no consistent structure. The kernel developers designed sysfs to have a strict
rule: sysfs attributes must be SCALAR (one value per file). You cannot write
multiple values to one sysfs file. This is the "one attribute, one file"
rule, enforced by code review. Unfortunately, this rule wasn't enforced
retroactively in `/proc` (which has multi-value files like `/proc/meminfo`
and `/proc/cpuinfo`). The rule also doesn't always hold in practice - some
sysfs files do contain multiple values. But the intent is there. The strict
design of sysfs means that parsing sysfs files is reliable: `cat /sys/class/net/eth0/speed`
always returns exactly one number. This predictability is why monitoring
tools prefer sysfs for device data over parsing `/proc` (which has more
complex, multi-value formats requiring careful parsing).

---

### Mastery Checklist

- [ ] Understands the role of /sys as the kernel's hardware object model
- [ ] Can read key device attributes (network, block devices) from /sys
- [ ] Can change I/O schedulers via /sys/block/DISK/queue/scheduler
- [ ] Understands how udev uses /sys for automatic module loading
- [ ] Knows that /sys changes are not persistent (use udev rules)

---

### Think About This

1. A new NVMe SSD is installed and you want to set its I/O scheduler to
   `none` permanently. Write: (a) the sysfs path to verify the current
   scheduler, (b) the command to change it immediately, (c) a udev rule
   that applies this setting automatically whenever the device is detected
   at boot or hotplug. Why can't you simply add an `echo none > ...`
   command to `/etc/rc.local`?

2. A script needs to determine, for each block device, whether it is a
   spinning HDD or SSD, to apply different I/O queue depths. The script
   must work without using `lsblk` (only raw sysfs). Write the loop
   that reads `/sys/block/*/queue/rotational` and outputs the device
   name and type.

3. A USB keyboard stops working. `lsusb` shows the device. `dmesg`
   shows the kernel detected it. But no `/dev/input/event*` was created.
   Walk through the chain: kernel detection -> sysfs entry creation ->
   uevent -> udev processing -> device node creation. At which step
   did it fail, and how would you diagnose using `udevadm`?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between /proc and /sys in Linux?
A: Both are virtual filesystems (no disk backing, kernel-generated data), but they serve different purposes: `/proc` is PROCESS-centric and GENERAL: one directory per PID with process information, plus general system data (`/proc/cpuinfo`, `/proc/meminfo`) and kernel parameters (`/proc/sys/`). It evolved organically and lacks strict structure - files can have multiple values, arbitrary formats. `/sys` is HARDWARE/OBJECT-centric: exposes the kernel's device model (kobjects, buses, drivers, devices) as a strict directory hierarchy. The "one value per file" rule (usually followed) makes it machine-parseable. `/sys` was created specifically to clean up the mess in `/proc`. Practical differences: for process information: use `/proc/PID/`. For device information: use `/sys/class/`, `/sys/bus/`, `/sys/block/`. For kernel tuning: use `/proc/sys/` (sysctl). For hardware configuration (I/O scheduler, power management, network tuning): use `/sys/`. For automatic device management (udev): udev reads from `/sys` (uevent, modalias, device attributes). Example: when you plug in a USB drive, the kernel creates `/sys/bus/usb/devices/1-1/` (sysfs entry). udev reads `modalias` from that entry and calls `modprobe usb_storage`. The driver creates `/dev/sdb`. The data path through `/sys` is what makes the whole device detection pipeline work.

**Intermediate:**
Q: How do udev rules work, and how would you write a rule to apply the "none" I/O scheduler to all NVMe devices at boot?
A: udev rules are in `/etc/udev/rules.d/` or `/lib/udev/rules.d/` (*.rules files, processed in alphanumeric order). Rule syntax: match conditions on the left (KEY==VALUE), actions on the right (KEY=VALUE or RUN, SYMLINK, etc.). For I/O scheduler: `ACTION=="add|change"` (when device appears or changes), `SUBSYSTEM=="block"` (only block devices), `KERNEL=="nvme[0-9]*n[0-9]*"` (NVMe naming pattern), `ATTR{queue/scheduler}="none"` (write "none" to the scheduler attribute). Full rule file `/etc/udev/rules.d/60-ioscheduler.rules`: `ACTION=="add|change", SUBSYSTEM=="block", KERNEL=="nvme[0-9]*n[0-9]*", ATTR{queue/scheduler}="none"`. Apply immediately (without reboot): `udevadm trigger --subsystem-match=block`. Verify: `cat /sys/block/nvme0n1/queue/scheduler` should show `[none]`. How to test a rule before applying: `udevadm test /sys/block/nvme0n1 2>&1 | grep scheduler`. The `60-` prefix controls rule order (lower numbers processed first). `ATTR{}` reads or writes sysfs attributes. Difference from `ENV{MODALIAS}`: ATTR reads from sysfs, ENV reads from the uevent environment.
