---
id: LNX-039
title: "Mounting Filesystems (mount, umount, /etc/fstab)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-007, LNX-010, LNX-049
used_by: LNX-054, LNX-080
related: LNX-049, LNX-054, OSY-019
tags: [mount, umount, fstab, filesystem, block-device, UUID, tmpfs, bind-mount, NFS]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/lnx/mounting-filesystems/
---

## TL;DR

Mounting attaches a filesystem (from a device or network) to a directory
(mount point) in the Linux directory tree. `mount /dev/sdb1 /data` mounts
the second disk partition at `/data`. `/etc/fstab` defines persistent
mounts (automatically applied at boot via `mount -a`). Use UUID instead
of device name in fstab (device names change; UUIDs don't). `umount /data`
safely detaches. Key patterns: data disk at `/data`, tmpfs for fast temp
storage, bind mounts for containerization.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-039 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | mount, umount, fstab, UUID, tmpfs, bind mount, NFS, filesystem |
| **Prerequisites** | LNX-007, LNX-010, LNX-049 |

---

### The Problem This Solves

You add a 1 TB SSD to a server for application data. The disk is there
(`lsblk` shows it as `/dev/sdb`) but inaccessible. You need to: format it
(`mkfs.ext4 /dev/sdb1`), create a mount point (`mkdir /data`), mount it
(`mount /dev/sdb1 /data`), and make it persistent at boot (add to
`/etc/fstab`). Without fstab, every reboot leaves the disk unmounted.
Without UUID in fstab, adding another disk might change device names and
break your mounts.

---

### Textbook Definition

**Mount**: The operation of making a filesystem accessible by attaching
it to a directory (the mount point) in the existing directory tree. After
mounting, files on the filesystem are accessible under the mount point path.

**Mount point**: An empty (or existing) directory that becomes the access
point for the mounted filesystem. The original directory contents are
hidden while something is mounted there.

**Block device**: A device that stores data in fixed-size blocks (disks,
partitions, LVM volumes). `lsblk` lists block devices.

**/etc/fstab**: File System TABle. Defines what filesystems to mount
at boot. Each line: device, mount point, filesystem type, options, dump
flag, fsck pass order.

**UUID**: Universally Unique Identifier assigned to a filesystem when
formatted. Stable across reboots and disk reordering. Find with:
`blkid /dev/sdb1` or `ls -la /dev/disk/by-uuid/`.

---

### Understand It in 30 Seconds

```bash
# List block devices (disks, partitions):
lsblk
# NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
# sda      8:0    0   20G  0 disk
# +-sda1   8:1    0   19G  0 part /
# +-sda2   8:2    0    1G  0 part [SWAP]
# sdb      8:16   0    1T  0 disk
# (sdb has no partition or mount yet)

# Create partition (if needed):
fdisk /dev/sdb    # interactive: n=new partition, w=write

# Format the partition:
mkfs.ext4 /dev/sdb1

# Create mount point:
mkdir -p /data

# Mount temporarily (until reboot):
mount /dev/sdb1 /data
df -h /data      # confirm mounted

# Get the UUID (for fstab):
blkid /dev/sdb1
# /dev/sdb1: UUID="a1b2c3d4-..." TYPE="ext4"

# Make it persistent in /etc/fstab:
# UUID=a1b2c3d4-... /data ext4 defaults 0 2
# Format: device  mountpoint  fstype  options  dump  pass

# Test fstab entry without rebooting:
mount -a    # mounts everything in fstab not yet mounted
# If there's an error in fstab, this tells you BEFORE rebooting

# Unmount:
umount /data           # safe unmount
umount -l /data        # lazy: unmount when not busy (risky)

# Show currently mounted filesystems:
mount | column -t      # all mounts
df -hT                 # human-readable with type
findmnt                # tree view of mounts

# Temporary in-memory filesystem (no disk, lives in RAM):
mount -t tmpfs -o size=512m tmpfs /tmp/ramdisk

# Bind mount (re-expose a directory at another path):
mount --bind /data/logs /var/log/myapp
# Now /var/log/myapp and /data/logs are the same filesystem location
```

---

### First Principles

**The /etc/fstab format (6 fields):**
```
# Device         Mountpoint  Type   Options           Dump Pass
UUID=a1b2-...   /data       ext4   defaults           0    2
UUID=b3c4-...   /           ext4   errors=remount-ro  0    1
tmpfs           /tmp        tmpfs  size=512m,mode=1777  0    0
192.168.1.5:/share /mnt/nfs nfs   defaults,_netdev     0    0

Field 1 - Device: block device path, UUID=..., LABEL=..., or tmpfs
Field 2 - Mount point: directory where filesystem appears
Field 3 - Type: ext4, xfs, btrfs, tmpfs, nfs, vfat, auto...
Field 4 - Options: comma-separated mount options (see below)
Field 5 - Dump: 0=no backup with dump(8), 1=include. Almost always 0.
Field 6 - Pass (fsck order):
  0 = skip fsck at boot
  1 = root filesystem (check first)
  2 = other filesystems (check after root, in parallel if same pass)

Common options:
  defaults  = rw,suid,dev,exec,auto,nouser,async (sane defaults)
  noexec    = cannot execute binaries from this filesystem
  nosuid    = ignore setuid bits (security hardening)
  nodev     = no device files (security hardening)
  ro        = read-only
  _netdev   = wait for network before mounting (NFS, iSCSI)
  nofail    = don't fail boot if device missing (external drives)
  errors=remount-ro = on error, remount read-only (root filesystem)
```

---

### Thought Experiment

Adding a data disk to a production server that must survive reboots:

```bash
# WRONG: Use device name in fstab
/dev/sdb1  /data  ext4  defaults  0  2
# Problem: add another disk -> new disk becomes sdb, old sdb becomes sdc
# Boot fails because /dev/sdb1 no longer exists or is wrong disk

# RIGHT: Use UUID in fstab
UUID=$(blkid -s UUID -o value /dev/sdb1)
echo "UUID=${UUID}  /data  ext4  defaults  0  2" >> /etc/fstab

# UUID is stamped into the filesystem metadata during mkfs
# It never changes (unless you reformat)
# Even if disk moves to a different port: same UUID

# Test before trusting (CRITICAL safety step):
mount -a    # try to apply all fstab entries
# If this succeeds: good. If it fails: error shown, fix before rebooting

# Verify mount:
df -h /data
mount | grep /data

# What if the disk is missing at boot?
# Without 'nofail': boot hangs waiting for the device (timeout)
# With 'nofail': boot continues, /data just isn't mounted

# For optional external/removable drives:
UUID=${UUID}  /data  ext4  defaults,nofail,x-systemd.device-timeout=5  0  0
```

---

### Mental Model / Analogy

```
Linux directory tree = a city's street system
Filesystems = distinct territories (warehouses)
Mount = building a ROAD connecting a warehouse to the street system
Mount point = the street address where the road connects

Before mounting /dev/sdb1 at /data:
  City: just has roads, /data is an empty parking lot

After mounting:
  /data now accesses the entire warehouse (1TB disk)
  Anything you put in /data/ goes into that warehouse
  
Unmounting: road is removed. Warehouse contents still there.
            The parking lot (/data dir) is empty again.

/etc/fstab = the city planning document:
  "At city startup, connect warehouse UUID=xxx to /data"
  
tmpfs = a temporary tent city in RAM:
  Fast to access, disappears when power goes out
  No physical warehouse - everything's in memory
  
Bind mount = a BRIDGE between two existing streets:
  /var/log/myapp and /data/logs are now the same place
  Enter from either side, you're at the same location
```

---

### Gradual Depth - Five Levels

**Level 1:**
`mount /dev/sdb1 /mountpoint` to mount. `umount /mountpoint` to unmount.
`df -h` to see what's mounted and how full. `lsblk` to see block devices.
`/etc/fstab` makes mounts persistent across reboots. That covers basic
disk management.

**Level 2:**
`blkid` for UUIDs. fstab 6-field format. `mount -a` to test fstab.
`tmpfs` for RAM-based temporary storage. `noexec,nosuid,nodev` options
for security (apply to `/tmp`, `/home`). `nofail` for optional drives.
`_netdev` for network filesystems.

**Level 3:**
`findmnt` and `findmnt --tree` for mount topology. Bind mounts: `mount --bind src dst`
(also: `--rbind` for recursive bind). `mount --make-private`, `--make-shared`:
mount propagation types (how mounts in one namespace affect others).
`mountpoint -q /path` in scripts to check if path is a mount. Overlay
filesystem: `mount -t overlay overlay -o lowerdir=lower,upperdir=upper,workdir=work merged`
(the basis for Docker layers).

**Level 4:**
`systemd .mount` units: alternative to fstab with more control (`After=`,
`Before=`, `ConditionPathExists=`). `/proc/mounts` and `/proc/self/mountinfo`:
kernel's view of mounts (more detailed than /etc/mtab). Mount namespaces:
each namespace has its own mount tree (`unshare -m`). Container mounts
are separate from host mounts via mount namespaces. `pivot_root()` vs
`chroot()`: pivot_root changes the entire mount tree, used by containers
to switch to a new rootfs.

**Level 5:**
`MS_BIND`, `MS_MOVE`, `MS_SHARED`, `MS_PRIVATE`, `MS_SLAVE`, `MS_UNBINDABLE`:
the actual `mount()` syscall flags. Shared subtree propagation: key to
understanding why container mounts don't leak to host. `shiftfs` (Ubuntu):
UID/GID shifting for unprivileged bind mounts in containers. `virtiofs`
and `9p`: guest-to-host filesystem in VMs/containers. Kubernetes volume
management: hostPath, emptyDir, configMap mounts all use bind mounts and
namespace isolation under the hood.

---

### Code Example

**BAD - mount management mistakes:**
```bash
# BAD 1: Device name in fstab (unstable)
echo "/dev/sdb1  /data  ext4  defaults  0  2" >> /etc/fstab
# Add another disk -> /dev/sdb might become a different disk
# Boot failure!

# GOOD: UUID in fstab
UUID=$(blkid -s UUID -o value /dev/sdb1)
echo "UUID=${UUID}  /data  ext4  defaults  0  2" >> /etc/fstab

# BAD 2: Not testing fstab before rebooting
echo "UUID=bad-uuid  /data  ext4  defaults  0  2" >> /etc/fstab
reboot   # System might not boot! "dependency failed" or boot hangs

# GOOD: always test with mount -a first
mount -a   # will fail immediately if UUID is wrong or device missing
# Then reboot only if mount -a succeeds

# BAD 3: umount -l in production (lazy unmount - data corruption risk)
umount -l /data    # "lazy": detaches from tree immediately
                    # but actual unmount deferred until no processes
# Processes may still be writing! Potential corruption.

# GOOD: find what's holding the filesystem open:
fuser -m /data       # show processes using /data
lsof /data           # show open files in /data
# Then gracefully stop those processes, then umount normally
umount /data         # clean unmount after processes closed files
```

**GOOD - production disk mounting script:**
```bash
#!/bin/bash
# mount-data-disk.sh: Safely mount a data disk with fstab entry

DEVICE="/dev/sdb1"
MOUNT_POINT="/data"
FS_TYPE="ext4"

# Verify device exists:
if [ ! -b "$DEVICE" ]; then
    echo "Error: $DEVICE is not a block device" >&2
    exit 1
fi

# Create mount point if needed:
mkdir -p "$MOUNT_POINT"

# Get UUID (stable identifier):
UUID=$(blkid -s UUID -o value "$DEVICE")
if [ -z "$UUID" ]; then
    echo "Error: Could not get UUID for $DEVICE" >&2
    echo "Is it formatted? Run: mkfs.ext4 $DEVICE"
    exit 1
fi

echo "Device UUID: $UUID"

# Mount now:
mount "$DEVICE" "$MOUNT_POINT"
echo "Mounted $DEVICE at $MOUNT_POINT"
df -h "$MOUNT_POINT"

# Add to fstab if not already there:
if ! grep -q "$UUID" /etc/fstab; then
    # Backup fstab first:
    cp /etc/fstab /etc/fstab.bak.$(date +%Y%m%d)
    
    echo "UUID=${UUID}  ${MOUNT_POINT}  ${FS_TYPE}  defaults,nofail  0  2" \
        >> /etc/fstab
    echo "Added to /etc/fstab"
    
    # Verify fstab is valid (unmount first to properly test):
    umount "$MOUNT_POINT"
    if mount -a; then
        echo "fstab test PASSED - mount -a succeeded"
    else
        echo "ERROR: fstab test FAILED - restoring backup"
        cp /etc/fstab.bak.$(date +%Y%m%d) /etc/fstab
        mount "$DEVICE" "$MOUNT_POINT"  # re-mount manually
        exit 1
    fi
fi

echo "Done. $MOUNT_POINT is mounted and will auto-mount at boot."
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Device names like /dev/sdb are stable" | Device names (sda, sdb, sdc...) are assigned at boot time based on driver enumeration order. Adding a USB drive, changing SATA ports, or boot order can shift device names. UUIDs are stamped into the filesystem and never change (until reformatted). Always use UUIDs in fstab. |
| "umount removes data from the disk" | umount detaches the filesystem from the directory tree, making files inaccessible via that path. The data on the disk is unchanged. Think: unplugging a USB drive (safely) - data is still on the drive, just not accessible from this path. |
| "An unmounted filesystem means no data" | Unmounted means not currently accessible via the directory tree, but the data on the device is preserved. `lsblk` still shows the device. `blkid` still shows the UUID. mount it again to access data. |
| "tmpfs data is preserved across reboots" | tmpfs is RAM-based. Power cycle or reboot = all tmpfs data is GONE. For `/tmp` (often tmpfs on modern systems): yes, /tmp is cleared at reboot (intentional). Never store important data in tmpfs-backed paths. |
| "fstab errors are caught at file-save time" | `/etc/fstab` is a plain text file - no syntax validation on save. Errors are only caught when the kernel tries to mount at boot (too late!) or when you run `mount -a` manually. ALWAYS run `mount -a` after editing fstab to catch errors before rebooting. |

---

### Failure Modes & Diagnosis

**Server won't boot after fstab change:**
```bash
# System is stuck at boot: "A dependency failed for..."
# Accessed via rescue/recovery mode or boot with kernel parameter:
# At grub: append 'rescue' or 'single' to kernel command line

# In recovery mode:
mount -o remount,rw /    # make root writable

# Check what failed:
cat /etc/fstab
# Find the problematic line (wrong UUID, missing device, etc.)

# Quick fix: comment out the bad line
sed -i 's|^UUID=bad-uuid|#UUID=bad-uuid|' /etc/fstab

# Or: add nofail to prevent boot failure:
# UUID=xxx  /data  ext4  defaults,nofail  0  2
# nofail: if device missing, skip this mount (don't fail boot)

# Test and reboot:
mount -a    # verify no errors remain
reboot
```

**"Target is busy" when trying to umount:**
```bash
umount /data
# umount: /data: target is busy

# Find what's keeping it busy:
fuser -m /data     # show PIDs using /data
fuser -km /data    # kill processes using /data (WARNING: may lose data)

# Better: gracefully stop processes first:
lsof /data | grep -v PID | awk '{print $1, $2}' | sort -u
# See which application and its PID

# Stop the service, then umount:
systemctl stop myapp
umount /data    # should succeed now

# If still busy after stopping all apps:
lsof /data   # check if shell's cwd is inside /data
cd /         # move out of /data if you're in it
umount /data
```

---

### Related Keywords

**Foundational:**
LNX-007 (FHS), LNX-010 (Permissions), LNX-049 (Filesystem Types)

**Builds on this:**
LNX-054 (LVM), LNX-080 (Container Internals)

**Related:**
OSY-019 (Storage), LNX-033 (Disk Usage)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `lsblk` | List block devices |
| `blkid /dev/sdb1` | Get UUID of device |
| `mkfs.ext4 /dev/sdb1` | Format partition |
| `mount /dev/sdb1 /mountpoint` | Mount device |
| `umount /mountpoint` | Unmount |
| `mount -a` | Apply all fstab entries |
| `df -hT` | Disk usage with filesystem type |
| `findmnt` | Mount tree view |
| `fuser -m /mnt` | Processes using mount |

**fstab fields:** device UUID  mountpoint  type  options  dump  pass

**3 things to remember:**
1. Use UUID not device name in fstab (`blkid /dev/sdb1` to get UUID)
2. Always run `mount -a` after editing fstab (catch errors before reboot)
3. Add `nofail` for optional disks (prevents boot hang if disk missing)

---

### Transferable Wisdom

Mount namespaces are the foundation of container isolation: each container
gets its own mount namespace where the rootfs is a container image (overlay
filesystem), /proc and /sys are fresh namespace-specific versions, and host
mounts are NOT visible (unless explicitly bind-mounted into the container).
`docker run -v /host/path:/container/path` = bind mount inside the container's
mount namespace. Kubernetes `volumes` and `volumeMounts` = bind mounts from
the node into the container namespace.

The bind mount pattern (`mount --bind src dst`) is also used for:
- Chroot jails: bind mount /proc, /sys, /dev into chroot
- Build systems: bind mount source code into build containers
- Multi-version deployments: bind mount config from different locations
- Test isolation: bind mount empty tmpfs over sensitive directories

---

### The Surprising Truth

The root filesystem (`/`) is also "mounted" - the kernel mounts the root
filesystem before anything else runs. The boot process: BIOS/UEFI -> GRUB
loads kernel + initramfs -> kernel mounts initramfs as temporary root
(`/`) -> initramfs mounts the REAL root filesystem -> `pivot_root()` or
`switch_root()` swaps the mount tree so the real root is now `/` -> initramfs
is discarded. This is why you can mount a different root filesystem (recovery,
chroot) - "/" is just a mount like any other. `/proc`, `/sys`, `/dev` are
also mounts (virtual filesystems - no disk backing). `mount | head -20`
shows them as `proc on /proc type proc`, `sysfs on /sys type sysfs`. The
Linux directory tree is an illusion built from dozens of mount points
layered together - the file at `/proc/1/status` doesn't exist on any disk.

---

### Mastery Checklist

- [ ] Can mount a new disk partition and verify it's mounted correctly
- [ ] Can add a UUID-based entry to /etc/fstab and test it before rebooting
- [ ] Can unmount a filesystem and diagnose "target is busy" errors
- [ ] Can set up tmpfs for temporary fast storage
- [ ] Understands the 6 fields of /etc/fstab

---

### Think About This

1. You add `UUID=abc123 /data ext4 defaults 0 2` to fstab. The next
   reboot hangs at "A job is running for..." for 90 seconds and then
   proceeds without `/data` mounted. What happened? What option in fstab
   would prevent the 90-second hang? What's the difference between
   `nofail` and not having the entry at all?

2. After running `umount /data`, you check with `df -h` and the mount
   is gone. But `ls /data` still shows files! How is this possible?
   What are those files, and are they accessible? When do they become
   accessible again?

3. You need to run `chroot /mnt/recovery /bin/bash` to repair a broken
   system. Once inside the chroot, `apt install somepackage` fails because
   /proc and /sys are empty. What commands would you run BEFORE the chroot
   to fix this? Explain why these virtual filesystems need to be explicitly
   mounted.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the purpose of /etc/fstab and what happens if there's an error in it?
A: `/etc/fstab` (filesystem table) defines which filesystems to mount automatically at boot. Each line: `device mountpoint fstype options dump pass`. The `systemd-fstab-generator` converts fstab entries into systemd mount units at boot. If there's an error: (1) If a device doesn't exist and has no `nofail` option: systemd times out (90s default) waiting for the device, then marks the unit as failed. Boot continues but the mount is missing. (2) If the mount itself fails (bad UUID, wrong fstype): systemd marks it failed. If it's a critical filesystem: boot may drop to emergency mode. (3) Syntax errors: `mount -a` returns an error. Recovery: (1) Boot to recovery/rescue mode. (2) Remount root read-write: `mount -o remount,rw /`. (3) Edit `/etc/fstab` to fix or comment out the bad line. (4) Run `mount -a` to verify. (5) Reboot. Prevention: ALWAYS run `mount -a` after editing fstab. Use `nofail` for non-critical mounts. Test UUID with `blkid /dev/sdX` before adding to fstab.

**Intermediate:**
Q: What is a bind mount and when would you use one?
A: A bind mount makes a directory accessible at multiple paths simultaneously. `mount --bind /source/dir /target/dir` makes the exact same filesystem location appear at both paths. Changes at one path appear at the other (they're the same location). Use cases: (1) Container isolation: Docker bind mounts `-v /host/path:/container/path` expose host directories inside containers via bind mounts within the container's mount namespace. (2) Chroot repair: `mount --bind /proc /mnt/recovery/proc` makes the running system's /proc visible inside a chroot environment (needed for apt, dpkg, etc.). (3) Testing: bind mount a tmpfs over a directory to test "clean" state without modifying the real directory. (4) Privilege separation: bind mount a read-only view of a directory for a restricted process: `mount --bind /data /chroot/data && mount -o remount,ro,bind /chroot/data`. (5) Multiple access patterns: expose `/data/uploads` as both `/data/uploads` (full access) and `/var/www/uploads` (web server access) without duplication. In fstab: `/source/dir /target/dir none bind 0 0`.

**Expert:**
Q: Explain how Docker uses bind mounts, overlay filesystems, and mount namespaces together to isolate container filesystems.
A: Container filesystem isolation uses three mechanisms layered together: (1) Mount namespace: `clone(CLONE_NEWMNT)` or `unshare -m` creates a new namespace where the process sees a fresh mount tree. All subsequent mounts in this namespace are invisible outside it. (2) Overlay filesystem: Docker image = stack of layers. `mount -t overlay overlay -o lowerdir=layer3:layer2:layer1,upperdir=container-rw,workdir=work /merged`. The `lowerdir` is all image layers (read-only). `upperdir` is container-specific writable layer. Changes go to upperdir; reads check upperdir first, then lowerdir layers. Image layers are shared between all containers using the same image (hard-linked in storage). (3) Bind mounts for `-v /host:/container`: After the overlay mount is the container rootfs, individual host directories are bind-mounted into specific paths in the namespace. These live on top of the overlay. The full sequence for `docker run -v /host/data:/data ubuntu`: create network + IPC namespaces, then: unshare mount namespace, mount overlay as /, mount /proc, /sys, /dev, /dev/pts (all fresh instances), bind mount /host/data -> /data, pivot_root to the new rootfs, exec /bin/bash. The container now has a complete Linux filesystem view that's entirely isolated from the host. The host can see the container's mounts via `/proc/PID/mountinfo` (the container process's PID from host perspective).
