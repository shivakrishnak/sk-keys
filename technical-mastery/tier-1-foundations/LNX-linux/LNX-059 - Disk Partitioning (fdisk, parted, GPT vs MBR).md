---
id: LNX-059
title: "Disk Partitioning (fdisk, parted, GPT vs MBR)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-049, LNX-039
used_by: LNX-054, LNX-088
related: LNX-054, LNX-049, LNX-039
tags: [fdisk, parted, GPT, MBR, UEFI, partitioning, lsblk, blkid, fstab, gdisk]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/lnx/disk-partitioning/
---

## TL;DR

Disk partitioning splits a disk into independent regions. Two partition
table formats: **MBR** (Master Boot Record - legacy): max 4 primary partitions,
max 2 TB disk, 512-byte first sector with partition table. **GPT** (GUID
Partition Table - modern): 128 partitions, 9.4 ZB max, required for UEFI
boot. Tools: `fdisk` (MBR + GPT, interactive), `gdisk` (GPT-only), `parted`
(both, scriptable). `lsblk` to list block devices, `blkid` for UUIDs,
`/etc/fstab` for persistent mounts. Growing a live partition: `growpart`
(expand partition table entry) + `resize2fs`/`xfs_growfs` (expand filesystem).
Cloud VMs use GPT by default.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-059 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | fdisk, parted, GPT, MBR, UEFI, partitioning, lsblk, blkid, fstab, growpart |
| **Prerequisites** | LNX-049 (Filesystems), LNX-039 (Mounting) |

---

### The Problem This Solves

**Problem 1**: A cloud VM starts with a 20 GB root disk. The disk is
expanded to 100 GB in the cloud console. But `df -h` still shows 20 GB.
The partition table entry and the filesystem both need to be updated:
`growpart /dev/xvda 1` expands the partition, then `resize2fs /dev/xvda1`
expands the filesystem. This is the most common cloud sysadmin task.

**Problem 2**: A new 4 TB disk needs to be partitioned. MBR supports max
2 TB - using `fdisk` on a 4 TB disk will silently create a broken partition
beyond the 2 TB boundary. GPT is required for >2 TB disks. Use `gdisk`
or `parted --script /dev/sdb mklabel gpt`.

---

### Textbook Definition

**Partition table**: Metadata at the beginning of a disk that describes
how the disk is divided into partitions. Each entry: start sector, end sector,
partition type (filesystem type hint, not enforced).

**MBR (Master Boot Record)**: The first 512 bytes of a disk. Contains:
446 bytes of boot code, 64 bytes of partition table (4 entries of 16 bytes
each = max 4 primary partitions), 2 bytes magic number (0x55AA). One primary
partition can be an "extended" partition containing "logical" partitions.
Maximum disk size: 2^32 sectors * 512 bytes = 2 TB.

**GPT (GUID Partition Table)**: Modern standard (part of UEFI spec).
Protective MBR in sector 0 (for backward compatibility). GPT header in
sector 1 (GUID, backup GPT location). Partition array: 128 entries by
default, each 128 bytes. Backup GPT header at last sector. No 2 TB limit
(64-bit LBA addressing = 9.4 ZB max).

**EFI System Partition (ESP)**: Required for UEFI boot. Type: `EFI System`
(C12A7328-F81F-11D2-BA4B-00A0C93EC93B). FAT32 formatted. Contains boot
loader files. Typically 100-512 MB, mounted at `/boot/efi`.

---

### Understand It in 30 Seconds

```bash
# === List all block devices ===
lsblk                           # tree view of disks and partitions
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT  # with details
lsblk -f                        # with filesystem info and UUIDs

# === Get partition info ===
fdisk -l /dev/sda               # show partition table (MBR or GPT)
gdisk -l /dev/sda               # GPT-centric view
parted /dev/sda print           # parted view

# === Get UUIDs (for fstab) ===
blkid /dev/sda1                 # UUID, TYPE (filesystem), LABEL
blkid -t TYPE=ext4              # all ext4 partitions
ls -la /dev/disk/by-uuid/       # symlinks by UUID

# === MBR partitioning with fdisk ===
fdisk /dev/sdb     # interactive
# Commands: n (new), d (delete), p (print), t (type), w (write), q (quit)
# n -> p (primary) -> 1 (partition number) -> enter (default start) -> +50G (size)
# t -> 82 (Linux swap), 83 (Linux data), 8e (LVM), b (FAT32)
# w -> write changes

# Non-interactive fdisk (for scripts):
echo -e "n\np\n1\n\n+50G\nw" | fdisk /dev/sdb

# === GPT partitioning with gdisk ===
gdisk /dev/sdb     # interactive (same commands as fdisk but GPT)
# o -> new GPT table
# n -> new partition
# i -> partition info
# p -> print table
# w -> write

# === GPT partitioning with parted (scriptable) ===
parted --script /dev/sdb \
    mklabel gpt \
    mkpart primary ext4 1MiB 100GiB \
    mkpart primary linux-swap 100GiB 108GiB \
    mkpart primary ext4 108GiB 100%
parted /dev/sdb print           # verify

# === Format partitions ===
mkfs.ext4 /dev/sdb1             # format first partition as ext4
mkfs.xfs /dev/sdb2              # format as XFS
mkswap /dev/sdb3                # format as swap
swapon /dev/sdb3                # activate swap

# === Mount and fstab ===
mount /dev/sdb1 /data

# Get UUID for fstab:
blkid /dev/sdb1
# /dev/sdb1: UUID="abc123-..." TYPE="ext4"

# Add to /etc/fstab (always use UUID, not device name):
# UUID=abc123-...  /data  ext4  defaults  0  2
echo "UUID=$(blkid -s UUID -o value /dev/sdb1) /data ext4 defaults 0 2" \
    >> /etc/fstab

# Test fstab without reboot:
mount -a        # mount all unmounted fstab entries
findmnt --verify   # verify fstab is correct

# === Expand cloud VM disk (most common operation) ===
# After expanding disk in cloud console (AWS/GCP/Azure):
lsblk               # confirm disk size changed (e.g., 20G -> 100G)
# But: partition still shows 20G, filesystem 20G

# Step 1: Expand the partition entry:
growpart /dev/xvda 1   # grow partition 1 on xvda
# or: parted /dev/xvda resizepart 1 100%

# Step 2: Expand the filesystem:
resize2fs /dev/xvda1        # ext4 (can be done online)
xfs_growfs /                # XFS (specify mount point, online)

# Verify:
lsblk
df -h
```

---

### First Principles

**MBR vs GPT layout comparison:**
```
MBR disk layout:
  Sector 0 (512 bytes):
    [0-445]   Boot code (446 bytes)
    [446-461] Partition 1 (16 bytes)
    [462-477] Partition 2 (16 bytes)
    [478-493] Partition 3 (16 bytes)
    [494-509] Partition 4 (16 bytes)
    [510-511] Magic: 0x55 0xAA

  Each partition entry (16 bytes):
    1B  status (0x80=bootable)
    3B  CHS start (legacy)
    1B  type (83=Linux, 82=swap, 8e=LVM, ...)
    3B  CHS end (legacy)
    4B  LBA start sector (32-bit)
    4B  LBA total sectors (32-bit)

  Max sectors: 2^32 = 4,294,967,296
  At 512 bytes/sector: 4,294,967,296 * 512 = 2 TB maximum

GPT disk layout:
  Sector 0: Protective MBR (type 0xEE in partition entry)
  Sector 1: GPT header
    - Signature, revision, header size
    - CRC32 of header
    - Location of backup GPT (last sector)
    - GUID of disk
    - First/last usable LBA
    - Partition array start LBA (sector 2)
    - Number of partition entries (128 default)
    - Size of each entry (128 bytes)
  Sectors 2-33: Partition array (128 entries * 128 bytes = 16,384 bytes)
    Each entry:
      16B  Partition type GUID
      16B  Unique partition GUID
      8B   Start LBA (64-bit)
      8B   End LBA (64-bit)
      8B   Attribute flags
      72B  Partition name (UTF-16LE)
  Last 33 sectors: Backup GPT header + backup partition array

  64-bit LBA: 2^64 sectors * 512 bytes = 9.4 ZB maximum
```

**fstab field explanation:**
```
/etc/fstab format:
  device    mount-point   fs-type  options         dump  fsck-order

  UUID=...  /             ext4     defaults         0     1
  UUID=...  /boot/efi     vfat     umask=0077       0     1
  UUID=...  /data         xfs      defaults,noatime 0     2
  UUID=...  swap          swap     defaults         0     0

  options:
    defaults = rw,suid,dev,exec,auto,nouser,async
    noatime  = don't update access time on read (performance)
    ro       = read-only
    nofail   = don't fail boot if device missing
    _netdev  = network device (wait for network before mount)

  dump (field 5): 0=no backup, 1=backup with dump (mostly unused)

  fsck-order (field 6):
    0 = no fsck at boot
    1 = root filesystem (checked first)
    2 = other filesystems (checked after root, in parallel if same number)
    Use 0 for swap, network, virtual filesystems
    Use 1 for root, 2 for others

  DANGER: wrong fstab = system won't boot!
  Always test with: mount -a (before rebooting)
  Recovery: boot with rescue disk, fix /etc/fstab
```

---

### Thought Experiment

Complete disk setup for a new data disk:

```bash
#!/bin/bash
# new-disk-setup.sh: Initialize, partition, format, mount a new disk

DISK="/dev/sdb"
MOUNT_POINT="/data"

# Step 1: Verify disk exists and is empty:
lsblk "$DISK"
# Should show: sdb  0B TYPE=disk

# Step 2: Create GPT partition table:
parted --script "$DISK" mklabel gpt

# Step 3: Create single partition using all space:
# Start at 1MiB (alignment): avoids alignment issues on some SSDs
# End at 100%: use all space
parted --script "$DISK" \
    mkpart primary xfs 1MiB 100%
# Note: "xfs" is just a label hint, mkfs.xfs is the real format step

# Step 4: Verify partition:
parted "$DISK" print
lsblk "$DISK"   # should show: sdb / sdb1

# Step 5: Format as XFS (fast, good for large files):
mkfs.xfs -L data-disk /dev/sdb1    # -L sets a label

# Step 6: Get UUID:
UUID=$(blkid -s UUID -o value /dev/sdb1)
echo "Partition UUID: $UUID"

# Step 7: Create mount point:
mkdir -p "$MOUNT_POINT"

# Step 8: Mount temporarily and verify:
mount /dev/sdb1 "$MOUNT_POINT"
df -h "$MOUNT_POINT"
# Should show the new disk capacity

# Step 9: Add to fstab for persistence:
# BACKUP fstab first!
cp /etc/fstab /etc/fstab.bak.$(date +%Y%m%d)

# Add entry using UUID (not device name - device names can change):
echo "UUID=$UUID $MOUNT_POINT xfs defaults,noatime 0 2" >> /etc/fstab

# Step 10: Verify fstab:
umount "$MOUNT_POINT"
mount -a        # should remount from fstab
findmnt --verify  # check for fstab errors
df -h "$MOUNT_POINT"   # verify mounted correctly

echo "Done: $DISK formatted and mounted at $MOUNT_POINT"
```

---

### Mental Model / Analogy

```
Disk = an empty building lot

Partition table = the property survey + zoning map
  MBR = old zoning (max 4 plots, max lot size 2 acres, survey in first page)
  GPT = modern zoning (128 plots, huge lot allowed, survey in first + last page)

Partitions = individual plots on the lot
  Plot 1: /dev/sdb1 (50 GB for /data)
  Plot 2: /dev/sdb2 (8 GB for swap)
  Plot 3: /dev/sdb3 (remaining space)

Formatting = building a specific type of structure on a plot
  mkfs.ext4 = build a warehouse (good for general use)
  mkfs.xfs  = build a high-throughput distribution center
  mkswap    = build a parking lot (swap space, not for files)

UUID = the official property address ID (permanent)
Device name = the street address (can change if roads are renumbered)
  /dev/sdb might become /dev/sdc if a new disk is added before it
  UUID never changes - even if the disk moves to a different port

/etc/fstab = the property management handbook
  Tells the OS: "at startup, attach plot UUID=abc123 to location /data"
  Wrong fstab = OS can't find the properties it expects = boot failure

growpart = expanding a plot by changing the survey boundary
  The lot physically got bigger (cloud expanded the disk)
  But the survey still shows the old boundary
  growpart updates the survey to reflect reality
  resize2fs = build on the newly surveyed land (expand the filesystem)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`lsblk` and `fdisk -l` for listing. `fdisk` for MBR, `gdisk` for GPT
(interactive - same interface). `mkfs.ext4`, `mkfs.xfs` for formatting.
`blkid` for UUIDs. `/etc/fstab` basics: device, mount point, type, options,
dump, fsck. `mount -a` to test fstab. `growpart` + `resize2fs` for cloud
disk expansion (most common sysadmin task).

**Level 2:**
`parted` for scripted partitioning (automation-friendly). Partition alignment
(1MiB start = aligned to 2048 sectors = modern standard). Partition types:
Linux (8300), Linux swap (8200), LVM (8e00 in MBR, 8300 in GPT), EFI System
(ef00). `sgdisk` for scripted GPT: `sgdisk --clear --new=0:0:0 --typecode=0:8300 /dev/sdb`.
`partprobe /dev/sdb` to re-read partition table without reboot.
`findmnt --verify` for fstab validation.

**Level 3:**
Alignment details: SSDs use 4K physical sectors (512e = 512-byte logical,
4K physical). Align to 4K for optimal performance: start at 2048 sectors
(1 MiB) ensures alignment. `4KN` drives (advanced format): use `parted` with
`--align optimal`. RAID alignment: start partition at 1 MiB + RAID chunk
size boundary for RAID sets. EFI System Partition (ESP): required for UEFI,
FAT32, 260-512 MB, mounted at `/boot/efi`, UEFI reads boot loader from here.

**Level 4:**
UEFI vs BIOS boot: BIOS reads boot code from MBR sector 0 (446 bytes),
loads the bootloader. UEFI reads the ESP, finds EFI applications (GRUB2
as `grubx64.efi`), executes them directly. Secure Boot: UEFI verifies
EFI applications are signed by trusted keys. GRUB2 on GPT/UEFI: `grub-install
--target=x86_64-efi`. Hybrid MBR/GPT: `gdisk -z` hybrid for legacy compatibility.
Cloud disk images: typically GPT, UEFI, single large partition with separate
`/boot/efi` on newer distributions.

**Level 5:**
Partition table backup and recovery: `sgdisk --backup=/root/sdb-gpt.bin /dev/sdb`
(backup) and `sgdisk --load-backup=/root/sdb-gpt.bin /dev/sdb` (restore).
GPT self-healing: if primary GPT header is corrupted, `gdisk` can rebuild
from backup GPT at end of disk. `testdisk`: recover deleted partitions by
scanning for filesystem signatures. NVMe namespace concept: NVMe has
"namespaces" (like partitions at the hardware protocol level) in addition
to Linux partitions. SR-IOV and NVMe multipath: advanced storage sharing.
`dm-multipath`: multiple paths to same LUN as single device.

---

### Code Example

**BAD - partitioning mistakes:**
```bash
# BAD 1: Using device name instead of UUID in fstab:
echo "/dev/sdb1 /data ext4 defaults 0 2" >> /etc/fstab
# If a new disk is added before sdb, it might become sdc
# sdb1 now refers to something else -> wrong filesystem mounted!
# ALWAYS use UUID in /etc/fstab

# GOOD: always use UUID:
UUID=$(blkid -s UUID -o value /dev/sdb1)
echo "UUID=$UUID /data ext4 defaults 0 2" >> /etc/fstab

# BAD 2: Forgetting to test fstab before reboot:
echo "UUID=wrong-uuid /data ext4 defaults 0 2" >> /etc/fstab
reboot    # OOPS: boot hangs waiting for UUID that doesn't exist
# If using "nofail" option, it won't hang but /data won't be mounted

# GOOD: always test fstab:
mount -a               # mounts all unmounted fstab entries
findmnt --verify       # validates all fstab entries exist and are correct
# If any error: fix BEFORE rebooting

# BAD 3: Using fdisk for a 3 TB disk:
fdisk /dev/sdb         # MBR: 2 TB limit!
# Creates partition spanning 3 TB but the table only supports 2 TB
# Data beyond 2 TB boundary is silently inaccessible or corrupted

# GOOD: use gdisk or parted for any new disk (GPT is always better):
gdisk /dev/sdb          # GPT: 9.4 ZB limit, 128 partitions
# Or:
parted --script /dev/sdb mklabel gpt
```

**GOOD - cloud disk expansion (complete workflow):**
```bash
#!/bin/bash
# expand-root-disk.sh: Expand root partition after cloud disk resize

# Verify disk was actually expanded:
DISK_SIZE=$(lsblk /dev/xvda --noheadings --output SIZE | head -1)
echo "Disk size: $DISK_SIZE"

PART_SIZE=$(lsblk /dev/xvda1 --noheadings --output SIZE | head -1)
echo "Partition size: $PART_SIZE"

FS_SIZE=$(df -h / | awk 'NR==2{print $2}')
echo "Filesystem size: $FS_SIZE"

# Step 1: Expand partition to fill disk:
# growpart is safe on live partitions (including root)
growpart /dev/xvda 1
echo "After growpart:"
lsblk /dev/xvda

# Step 2: Expand filesystem:
FS_TYPE=$(df -T / | awk 'NR==2{print $2}')
echo "Filesystem type: $FS_TYPE"

case "$FS_TYPE" in
    ext4|ext3|ext2)
        resize2fs /dev/xvda1     # online resize (no unmount needed)
        ;;
    xfs)
        xfs_growfs /             # online resize (specify mount point)
        ;;
    *)
        echo "Unknown filesystem type: $FS_TYPE"
        exit 1
        ;;
esac

# Step 3: Verify:
df -h /
echo "Done: root filesystem expanded"
```

---

### Comparison Table

| Feature | MBR | GPT |
|---------|-----|-----|
| **Max disk size** | 2 TB | 9.4 ZB (practically unlimited) |
| **Max partitions** | 4 primary (or 3+extended) | 128 |
| **Boot standard** | BIOS (legacy) | UEFI (modern) or BIOS with protective MBR |
| **Redundancy** | None (single copy at sector 0) | Backup copy at end of disk |
| **Partition GUID** | No (type byte only) | Yes (unique GUID per partition) |
| **Partition names** | No | Yes (up to 72 bytes UTF-16) |
| **CRC checksums** | No | Yes (CRC32 on header + table) |
| **Cloud VMs** | Older AMIs | Modern AMIs, GCP, Azure |
| **Use when** | Legacy hardware, VMs requiring BIOS | Any new disk or system |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "fdisk only works with MBR disks" | Modern fdisk (util-linux 2.26+, standard on RHEL 7+, Ubuntu 16.04+) fully supports GPT. Older fdisk (especially on RHEL 6 and Ubuntu 14.04) was MBR-only. `gdisk` was created specifically as a GPT-native tool with the same interface as MBR fdisk. Always check `fdisk --version` - if it's modern, it handles GPT fine. `fdisk -l` will show "Disklabel type: gpt" or "msdos" (MBR). |
| "Growing a partition requires unmounting the filesystem" | It depends on the tool and partition position. `growpart` can extend a partition that is currently mounted, including the root filesystem. `resize2fs` can grow ext4 online (while mounted). `xfs_growfs` can grow XFS online. The limitation: SHRINKING almost always requires unmounting. Extending the LAST partition on a disk is safe online. Extending a non-last partition (there's something after it) is not possible without moving the next partition. Cloud VMs almost always have one large data partition as the last (often only) partition, making online growth straightforward. |
| "Partition type codes in fdisk tell the OS what filesystem to use" | The partition type code (83 for Linux, 82 for swap, 8e for LVM) is a HINT that tools use for display and auto-detection. The OS does NOT use the type code to determine the filesystem. `mount` reads the actual filesystem superblock to determine the type. You can format a partition with `mkfs.xfs` even if the partition type says "Linux" (83) and mount it as XFS. The type code is largely cosmetic. Exception: UEFI reads the partition type GUID to find the EFI System Partition - so the EFI type GUID (ef00) is functionally meaningful. |
| "Using /dev/sdb1 in fstab is fine if the disk is always the same" | Device names (`/dev/sda`, `/dev/sdb`) are assigned by the kernel in the ORDER disks are discovered at boot. If a new disk is added, or a disk fails and is replaced, the ordering can change. What was `/dev/sdb` might become `/dev/sdc`. UUID-based mounts (`UUID=...`) are immune to this - the UUID is stored in the filesystem superblock and doesn't change when the disk moves. On cloud instances, device name mappings can differ from what the cloud console shows (AWS: `/dev/xvdf` vs `/dev/sdf`). Always use UUID. |
| "GPT is only needed for disks over 2 TB" | GPT is the right choice for ALL new disks, regardless of size. Benefits: 128 partitions (vs 4 primary), unique GUIDs per partition, CRC checksums for error detection, backup copy at end of disk (self-healing), required for UEFI boot on system disks, partition names for documentation. The only reason to use MBR is legacy compatibility: BIOS-only systems (rare), very old hardware or VMs that require MBR. New installations: use GPT by default. |

---

### Failure Modes & Diagnosis

**fstab error causing boot failure:**
```bash
# Symptom: system drops to emergency shell at boot with message:
# "Failed to mount /data" or "You are in emergency mode"

# From emergency shell:
mount -o remount,rw /    # remount root as writable (often needed)
vi /etc/fstab            # fix the problematic entry

# Alternatively - comment out the problematic line:
# UUID=wrong-uuid  /data  ext4  defaults  0  2
# becomes:
# #UUID=wrong-uuid  /data  ext4  defaults  0  2

# Or add "nofail" option to prevent boot failure for non-critical mounts:
# UUID=abc123  /data  ext4  defaults,nofail  0  2
# nofail: continue boot even if this mount fails

# After fixing:
mount -a             # try mounting all fstab entries
# If no errors: reboot safely

# Prevention: always test before reboot:
findmnt --verify     # validates all fstab entries
# Checks: UUID exists (blkid), mount point exists, filesystem type matches
```

---

### Related Keywords

**Foundational:**
LNX-049 (Filesystem Types), LNX-039 (Mounting)

**Builds on this:**
LNX-054 (LVM), LNX-088 (Disk Performance)

**Related:**
LNX-049, LNX-054

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `lsblk` | List block devices (tree view) |
| `fdisk -l /dev/sda` | Show partition table |
| `blkid /dev/sda1` | Show UUID and filesystem type |
| `fdisk /dev/sdb` | Interactive MBR/GPT partitioning |
| `gdisk /dev/sdb` | Interactive GPT partitioning |
| `parted --script /dev/sdb mklabel gpt` | Script-friendly GPT init |
| `mkfs.ext4 /dev/sdb1` | Format partition as ext4 |
| `growpart /dev/xvda 1` | Expand partition to disk size |
| `resize2fs /dev/xvda1` | Expand ext4 filesystem (online) |
| `xfs_growfs /mount` | Expand XFS filesystem (online) |

**3 things to remember:**
1. Always use UUID (not device name) in `/etc/fstab` - device names change, UUIDs don't
2. GPT for all new disks: 128 partitions, no 2 TB limit, checksums, backup header
3. After cloud disk resize: `growpart` (expand partition entry) THEN `resize2fs` or `xfs_growfs` (expand filesystem)

---

### Transferable Wisdom

Disk partitioning concepts appear in: AWS EBS volumes use GPT internally.
`growpart` is the standard tool for AWS Auto Scaling instances that start
small and grow. Kubernetes PVC expansion: when a PVC is expanded, the cloud
volume grows, then `resize2fs` runs (often handled by the CSI driver).
Docker volumes on cloud instances: same growpart + resize2fs pattern.
The concept of "partition = address range on block device, filesystem = 
structure within that range" appears in: database tablespaces (a tablespace
is a partition of a filesystem, and the DB creates its own addressing),
object storage (S3 bucket = namespace, not a partition), virtual disk images
(`.vmdk`, `.qcow2` files = virtual block devices with their own partition tables).

---

### The Surprising Truth

The MBR partition table has a bug that affects many Linux users without them
knowing: when you create a partition with `fdisk` and start from sector 2048
(the modern default for alignment), the partition table has 2047 sectors of
"wasted" space before the first partition. On a 512-byte sector disk, that's
1,047,040 bytes = ~1 MB wasted. This is intentional and correct! 2048 sectors
= 1 MiB alignment, which ensures the partition is aligned to 4K physical
sector boundaries (required for modern SSDs) and to RAID stripe boundaries.
Old versions of fdisk (before 2010) started partitions at sector 63 - which
is aligned to nothing meaningful and causes ~10-15% performance loss on modern
SSDs due to misaligned writes spanning two physical 4K sectors. If you have
any Linux partition that starts at sector 63 (check: `fdisk -l | grep "63$"`),
that partition is misaligned. The fix requires backing up data, repartitioning
from sector 2048, and restoring. This affects millions of systems that were
installed before 2012 that have never had their disks repartitioned.

---

### Mastery Checklist

- [ ] Can list block devices (lsblk) and show partition tables (fdisk -l)
- [ ] Can create GPT partitions using gdisk or parted
- [ ] Can format, mount, and add filesystem to /etc/fstab using UUID
- [ ] Can expand a cloud VM disk (growpart + resize2fs/xfs_growfs)
- [ ] Understands MBR vs GPT differences and when each is appropriate

---

### Think About This

1. An AWS EC2 instance has a 20 GB root EBS volume at 95% capacity. You
   expand the EBS volume to 100 GB in the AWS console. List every command
   needed to make the OS use the full 100 GB, in the correct order. Explain
   what each command does and why it's needed. Assume the root filesystem
   is ext4 on `/dev/xvda1`.

2. You need to add a persistent data disk to a server with these requirements:
   (a) The disk is 8 TB (rules out MBR), (b) it must be mounted at `/data`
   after every reboot, (c) the mount must not cause boot failure if the disk
   is missing (for cloud environments), (d) formatted for large sequential I/O.
   Provide the complete sequence of commands, explaining each choice.

3. After adding a line to `/etc/fstab` and rebooting, the server boots into
   emergency mode. You have access to the console (but not the full OS).
   Walk through the recovery procedure. Why does a bad fstab entry cause
   boot failure? What option could have prevented this?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between MBR and GPT partition tables, and when should you use each?
A: MBR (Master Boot Record) is the legacy standard from the 1980s. It stores the partition table in the first 512 bytes of the disk: 446 bytes of boot code, 64 bytes for 4 partition entries (16 bytes each), 2 bytes magic. Limitations: only 4 primary partitions, maximum disk size 2 TB (32-bit LBA at 512 bytes/sector = 2^32 * 512 = 2 TB), single point of failure (no backup). GPT (GUID Partition Table) is the modern standard, part of the UEFI specification. It stores partition info in sectors 1-33 with a backup copy at the end of the disk. 128 partition entries by default, 64-bit LBA addressing (9.4 ZB max), each partition has a unique GUID, CRC32 checksums detect corruption, partition names for documentation. UEFI boot requires GPT (technically possible to UEFI boot from MBR but non-standard). When to use: GPT = always for new disks, required for >2 TB, required for UEFI boot, better reliability. MBR = only for legacy BIOS systems that explicitly require it, or very old VMs/hardware. Practically: any cloud instance, any modern server or desktop should use GPT. The protective MBR in sector 0 of a GPT disk ensures old tools that only understand MBR see the disk as "has one partition covering the whole disk" and don't accidentally overwrite it.

**Expert:**
Q: A cloud VM's root disk was expanded from 20 GB to 100 GB. The OS still shows 20 GB. Walk through the exact diagnosis and repair procedure.
A: Three layers need to be updated: physical disk, partition table, filesystem. DIAGNOSIS: First, confirm the physical disk is larger: `lsblk /dev/xvda` - shows "100G" for the disk. Then: `lsblk /dev/xvda1` - still shows "20G" (partition hasn't grown). Then: `df -h /` - still shows "20G" (filesystem hasn't grown). This is the expected pattern: cloud console expanded the block device, but partition table and filesystem are unchanged. REPAIR: Step 1 - Expand the partition: `growpart /dev/xvda 1`. This updates the partition table entry for partition 1 to use the full disk. It uses a combination of `parted` and `partprobe` internally. Safe on live root filesystem. Verify: `lsblk /dev/xvda1` now shows "100G". Step 2 - Expand the filesystem: if ext4: `resize2fs /dev/xvda1` (online growth, no unmount needed, takes seconds). If XFS: `xfs_growfs /` (online growth, specify mount point, nearly instant). If LVM: `pvresize /dev/xvda1` then `lvextend -r -L +80G /dev/VG/LV`. Verify: `df -h /` now shows "100G". AUTOMATION: AWS provides `cloud-utils-growpart` package with `growpart`. Many modern cloud AMIs run this automatically at boot via `cloud-init` when it detects disk size changed. Best practice for cloud instances: use user-data scripts or `cloud-init` to auto-expand, and add `nofail` to `/etc/fstab` for data volumes to prevent boot failures in cloud environments.
