---
id: LNX-054
title: "LVM - Logical Volume Manager"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-059, LNX-039
used_by: LNX-088, LNX-049
related: LNX-059, LNX-049, LNX-039
tags: [LVM, logical-volume, physical-volume, volume-group, pvs, vgs, lvs, lvcreate, snapshot]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/lnx/lvm-logical-volume-manager/
---

## TL;DR

LVM (Logical Volume Manager) adds a virtualization layer between physical
disks and filesystems: Physical Volumes (PVs, raw disks/partitions) ->
Volume Group (VG, pool of storage) -> Logical Volumes (LVs, virtual disks
with filesystems). Benefits: resize filesystems while mounted (extend),
span multiple disks transparently, instant snapshots for backups. Key
commands: `pvs`/`vgs`/`lvs` (display), `pvcreate`/`vgcreate`/`lvcreate`
(create), `lvextend` + `resize2fs`/`xfs_growfs` (grow), `lvcreate -s`
(snapshot). Common cloud pattern: root disk is an LVM LV, easily extended.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-054 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | LVM, logical volume, physical volume, volume group, pvs, vgs, lvs, snapshot |
| **Prerequisites** | LNX-059, LNX-039 |

---

### The Problem This Solves

**Problem 1**: A server's `/var` filesystem is 80% full. The server has
one more physical disk. Without LVM: resize is difficult (offline, backup/
restore). With LVM: `vgextend vg0 /dev/sdb` (add disk to pool), `lvextend -L +100G /dev/vg0/var` (grow LV), `resize2fs /dev/vg0/var` (grow filesystem) - all online, while `/var` is mounted.

**Problem 2**: You need a consistent backup of a database. The database
can't be paused for hours. LVM snapshot: `lvcreate -s -L 10G /dev/vg0/mysql`
creates an instant, point-in-time snapshot. Back up from the snapshot while
the database continues running. Remove the snapshot when done.

---

### Textbook Definition

**Physical Volume (PV)**: A raw disk or partition prepared for LVM use by
`pvcreate`. Contains LVM metadata and physical extents (PEs, usually 4 MB
blocks).

**Volume Group (VG)**: A pool of storage created from one or more PVs.
LVM allocates logical extents from the VG's pool of physical extents.

**Logical Volume (LV)**: A virtual disk carved from a VG. Has a size in
extents, a name, and a device path (`/dev/VG_NAME/LV_NAME`). Formatted
with a filesystem and mounted. Can be thin-provisioned, mirrored, or
striped.

**Physical Extent (PE)**: The allocation unit (default 4 MB). LVs are
allocated in extents. An LV's size in extents = its actual size / PE size.

**Snapshot**: A special LV that records changes to the origin LV. Initially
shares all blocks with the origin. On write to origin: the old block is
copied to the snapshot first (CoW). Snapshot size = maximum change expected.

---

### Understand It in 30 Seconds

```bash
# === Display LVM status ===
pvs            # physical volumes (PV, VG, capacity, free)
vgs            # volume groups (total, free, LV count)
lvs            # logical volumes (name, VG, size, type)
pvdisplay      # detailed PV info
vgdisplay      # detailed VG info
lvdisplay      # detailed LV info

# === Create LVM from scratch ===
# 1. Initialize physical volumes:
pvcreate /dev/sdb /dev/sdc

# 2. Create volume group:
vgcreate vg_data /dev/sdb /dev/sdc
# Now vg_data has the combined capacity of sdb + sdc

# 3. Create logical volumes:
lvcreate -n lv_app -L 50G vg_data       # 50 GB LV named lv_app
lvcreate -n lv_logs -L 30G vg_data      # 30 GB LV named lv_logs
lvcreate -n lv_backup -l 100%FREE vg_data # use remaining space

# 4. Create filesystem:
mkfs.xfs /dev/vg_data/lv_app
mkfs.ext4 /dev/vg_data/lv_logs

# 5. Mount:
mount /dev/vg_data/lv_app /app
# Add to /etc/fstab:
echo "/dev/vg_data/lv_app /app xfs defaults 0 0" >> /etc/fstab

# === Extend an LV (online, while mounted) ===
# Option 1: Extend by amount:
lvextend -L +50G /dev/vg_data/lv_app     # add 50 GB
lvextend -l +100%FREE /dev/vg_data/lv_app  # use all remaining VG free space

# Option 2: Extend AND resize filesystem in one command:
lvextend -L +50G -r /dev/vg_data/lv_app
# -r = --resizefs (auto-runs resize2fs or xfs_growfs)

# Manual filesystem resize:
resize2fs /dev/vg_data/lv_logs          # ext4: grow to match LV size
xfs_growfs /app                          # XFS: grow (must specify mount point)

# === Add new disk to existing VG ===
pvcreate /dev/sdd                        # initialize new disk
vgextend vg_data /dev/sdd               # add to VG
# VG free space immediately increases
lvextend -L +200G -r /dev/vg_data/lv_app  # now extend the LV

# === LVM Snapshots ===
# Create snapshot (freeze point in time):
lvcreate -s -n snap_app -L 10G /dev/vg_data/lv_app
# snap_app: starts empty, grows as lv_app changes (CoW)
# 10G = max expected changes before backup completes

# Mount and back up from snapshot:
mount -o ro /dev/vg_data/snap_app /mnt/snap
rsync -av /mnt/snap/ /backup/app-$(date +%Y%m%d)/

# Remove snapshot when done:
umount /mnt/snap
lvremove /dev/vg_data/snap_app

# === Shrink an LV (DANGER - only ext4, must be unmounted) ===
umount /dev/vg_data/lv_logs
e2fsck -f /dev/vg_data/lv_logs
resize2fs /dev/vg_data/lv_logs 20G      # shrink filesystem FIRST
lvreduce -L 20G /dev/vg_data/lv_logs   # then shrink LV (MUST be <= FS size)
mount /dev/vg_data/lv_logs /var/log
```

---

### First Principles

**LVM layer diagram:**
```
                LVM Layer Stack

Physical:   [/dev/sdb 500G] [/dev/sdc 500G]
                |                |
Physical       PV: sdb          PV: sdc
Volumes:      +----|-----------------|----+
              |    Volume Group: vg0     |
Volume         |    1000 GB total         |
Group:         |    200 GB free           |
              +---+------+--------+-------+
                  |      |        |
Logical     [lv_app] [lv_logs] [lv_db]
Volumes:    300 GB    100 GB   400 GB
                  |
         /dev/vg0/lv_app (device path)
                  |
          mkfs.ext4 -> /app (mount point)

Application sees: /app (300 GB, growing as needed)
Application doesn't know: which physical disk, how many disks, how fragmented

Data blocks can span physical disks:
  lv_db 400 GB: 300 GB on sdb + 100 GB on sdc (striping optional)
  Default: contiguous on first available PV, then overflow to next
```

**Snapshot CoW mechanics:**
```
Before snapshot:
  lv_app: [A][B][C][D][E]...[Z]
  snap_app: (empty, points to lv_app)

Write to lv_app block B (modified to B'):
  1. lv_app block B is copied to snap_app FIRST
  2. lv_app block B is overwritten with B'

After write:
  lv_app: [A][B'][C][D][E]...[Z]   <- B' is new data
  snap_app: [B]                     <- B is preserved original

Read from snap_app block B: returns [B] (original, not B')
Read from snap_app block A: returns [A] from lv_app (not in snap = unchanged)

Snapshot full = snapshot overflows:
  If snap_app's 10 GB fills up before backup finishes:
  snapshot is INVALIDATED (becomes unusable)
  lv_app continues fine (snapshot failure doesn't affect origin)
```

---

### Thought Experiment

Migrating data from old disk to new disk online:

```bash
# Scenario: sdb (500GB) is old/slow HDD, need to replace with sdc (1TB SSD)
# lv_data lives on sdb (via vg_data)
# Goal: move lv_data to sdc without downtime

# Step 1: Add new disk to VG:
pvcreate /dev/sdc
vgextend vg_data /dev/sdc

# Step 2: Move extents from sdb to sdc:
pvmove /dev/sdb /dev/sdc
# This moves all extents offline to online
# Can take hours for large volumes
# Progress: watch pvs -a (sdb free space increases, sdc decreases)
# pvmove is safe to interrupt (it's journaled) and can be resumed

# Step 3: Remove old disk from VG:
vgreduce vg_data /dev/sdb
pvremove /dev/sdb

# Done: lv_data now lives entirely on sdc (1TB SSD)
# No downtime, no data loss, no filesystem unmount

# Verify:
pvs    # sdb should no longer appear
vgs    # vg_data should show 1TB capacity (the sdc)
lvs    # lv_data still exists, same mount point, same data

# More selective: move only specific LV:
pvmove -n lv_data /dev/sdb /dev/sdc
# Moves only the extents belonging to lv_data
```

---

### Mental Model / Analogy

```
LVM = a flexible warehouse storage system

Physical Volumes (PVs) = the physical warehouses
  - /dev/sdb = Warehouse A (500 sqm)
  - /dev/sdc = Warehouse B (500 sqm)

Volume Group (VG) = the unified storage pool
  - "Storage Pool Alpha" = 1000 sqm (A + B combined)
  - Inventory managed centrally regardless of which building

Logical Volumes (LVs) = virtual storage units rented from the pool
  - "Section App": 300 sqm (might use space from A, B, or both)
  - "Section Logs": 100 sqm
  - Management doesn't care WHICH building the space is in

Extending a section:
  - Manager says "Section App needs 50 more sqm"
  - Storage pool allocates from whichever building has free space
  - Section App's renters don't need to move (filesystem stays mounted)

Snapshot:
  - Take a photo of Section App at exactly 14:00
  - Continue using Section App normally
  - Use the photo for backup reference
  - Any changes to Section App AFTER 14:00: the original blocks
    are preserved in the "photo storage" before overwriting

pvmove = moving the actual boxes from Warehouse A to B
  - Happens in background, renters (applications) don't notice
  - Eventually: all of A's boxes are in B, A is empty, can return A
```

---

### Gradual Depth - Five Levels

**Level 1:**
Understand the three layers: PV (disk) -> VG (pool) -> LV (virtual disk).
`pvs`/`vgs`/`lvs` to display. `lvextend -r` + resize to grow online.
Snapshots for backups. Most VMs use LVM by default (RHEL/CentOS installs
to LVM, Ubuntu Server prompts for LVM).

**Level 2:**
`pvmove` for non-destructive disk migration. `vgextend`/`vgreduce` for
adding/removing disks. Thin provisioning (`lvcreate --thin -V`): allocate
more than physical storage (useful in dev environments). Linear vs striped
LVs: striped spreads I/O across multiple PVs (better throughput). LVM
mirroring: write to two PVs simultaneously for redundancy.

**Level 3:**
Thin pools and thin volumes: a thin pool LV holds actual blocks; thin volumes
map to it on write. Enables overcommit and efficient snapshots. LVM2 merging
snapshots: `lvconvert --merge /dev/vg/snap` merges snapshot back to origin
(rollback). RAID via LVM: `lvcreate --type raid5 -n lv_raid5 -l 100%FREE vg0`
(software RAID within LVM). `pvck` for PV metadata validation. Backing up
LVM metadata: `vgcfgbackup /etc/lvm/backup/`.

**Level 4:**
LVM cache (`lvmcache`): use fast SSD to cache reads/writes from slow HDD
(`lvcreate --type cache`). LVM writecache: a faster variant of cache. LVM
VDO (Virtual Data Optimizer): inline deduplication and compression at the
LVM layer (RHEL 8+, `lvcreate --type vdo`). LVM on LUKS (disk encryption):
`cryptsetup luksFormat /dev/sdb` -> `cryptsetup open` -> `pvcreate` ->
`vgcreate`. Or LUKS on LVM: `pvcreate /dev/sdb` -> `vgcreate` -> `lvcreate`
-> `cryptsetup luksFormat /dev/vg/lv`.

**Level 5:**
LVM event daemon (lvmetad): caches metadata to avoid scanning all PVs
on every command. `systemctl status lvm2-lvmetad`. LVM global filter:
`/etc/lvm/lvm.conf` `filter` setting to include/exclude disks. Critical
for shared storage (SANs): LVM must filter out disks managed by other hosts
to prevent corruption. Clustered LVM (clvmd/lvmlockd): allows shared VGs
across multiple nodes with distributed locking. Used in RHEL cluster (Pacemaker
+ LVM for HA storage). OpenStack Cinder LVM driver: provisions block storage
volumes as LVM LVs on storage nodes, exports via iSCSI.

---

### Code Example

**BAD - LVM mistakes:**
```bash
# BAD 1: Shrinking LV before filesystem:
lvreduce -L 20G /dev/vg0/lv_data    # NEVER DO THIS FIRST
# Data loss! LV shrinks below filesystem -> filesystem corruption
# Always: reduce filesystem FIRST, then LV

# BAD 2: Snapshot too small:
lvcreate -s -n snap -L 1G /dev/vg0/lv_big_db   # 1 GB for 200 GB database
# If database has 5 GB of changes during backup: snapshot overflows = INVALID
# Snapshot invalidation: lvs shows "Imp(s) overflow"
# Rule: snapshot size = expected write rate * backup duration + 20% margin

# BAD 3: Forgetting resize2fs after lvextend:
lvextend -L +50G /dev/vg0/lv_data
# Filesystem still sees old size! mount shows old capacity
# Run: resize2fs /dev/vg0/lv_data (for ext4)
# Or: xfs_growfs /data_mount (for XFS)
# Or: use -r flag: lvextend -r -L +50G /dev/vg0/lv_data (combined)

# BAD 4: Extending XFS by wrong path:
xfs_growfs /dev/vg0/lv_data   # WRONG - XFS needs mount point, not device
xfs_growfs /data               # CORRECT - must specify mount point
```

**GOOD - LVM expansion workflow with verification:**
```bash
#!/bin/bash
# lvm-expand.sh: safely extend an LV and its filesystem

LV="/dev/vg_data/lv_app"
MOUNT="/app"
ADD_SIZE="50G"

echo "=== Pre-expansion state ==="
lvs "$LV"
df -h "$MOUNT"

# Check VG has enough free space:
VG=$(lvs --noheadings -o vg_name "$LV" | tr -d ' ')
VG_FREE=$(vgs --noheadings --units g -o vg_free "$VG" | tr -d 'g ')
echo "VG $VG has ${VG_FREE}G free"

# Get numeric add size:
ADD_NUM=${ADD_SIZE%G}
if (( $(echo "$VG_FREE < $ADD_NUM" | bc -l) )); then
    echo "ERROR: Not enough free space in VG (need ${ADD_SIZE}, have ${VG_FREE}G)"
    exit 1
fi

echo ""
echo "=== Extending $LV by $ADD_SIZE ==="
# -r = resize filesystem automatically
lvextend -L +"$ADD_SIZE" -r "$LV"
if [[ $? -ne 0 ]]; then
    echo "ERROR: lvextend failed"
    exit 1
fi

echo ""
echo "=== Post-expansion state ==="
lvs "$LV"
df -h "$MOUNT"
echo "SUCCESS: $LV extended by $ADD_SIZE"
```

---

### Comparison Table

| Feature | LVM | Raw Partitions | ZFS |
|---------|-----|---------------|-----|
| **Online resize** | Yes (extend) | No | Yes |
| **Span multiple disks** | Yes | No | Yes |
| **Snapshots** | Yes (CoW) | No | Yes (efficient) |
| **RAID** | Yes (LVM RAID) | No (separate mdadm) | Yes (RAID-Z) |
| **Complexity** | Medium | Low | High |
| **Filesystem independent** | Yes | N/A | ZFS only |
| **Cloud-native** | Common | Becoming rare | Limited cloud support |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Extending a Logical Volume also extends the filesystem" | NO. `lvextend` only grows the LV (the block device). The filesystem running on it still thinks it's the old size. You MUST also run `resize2fs /dev/VG/LV` (ext4) or `xfs_growfs /mountpoint` (XFS) to grow the filesystem into the new space. `lvextend -r` does both in one command and is the recommended approach. |
| "LVM snapshots are free (no performance cost)" | Snapshots add write overhead on the ORIGIN LV, not just the snapshot. On every write to the origin, LVM first copies the original block to the snapshot (CoW). This roughly halves write throughput to the origin LV while a snapshot exists. For databases: never leave a snapshot running longer than needed. Use snapshots only during active backup windows, then delete them. |
| "Shrinking a Logical Volume is symmetric with extending" | Dangerous and asymmetric. Extending is safe online. Shrinking REQUIRES: (1) unmounting the filesystem, (2) running e2fsck, (3) shrinking the FILESYSTEM to target size, (4) THEN shrinking the LV to target size or slightly larger. Do them in the wrong order or shrink LV smaller than filesystem = data corruption. XFS CANNOT be shrunk at all. Only ext2/3/4 supports offline shrink. |
| "LVM replaces the need for RAID" | LVM provides spanning (concatenation) and can do mirroring (via lvm mirror/raid), but without RAID 5/6 parity by default. LVM + mdadm RAID is a common combination (RAID for redundancy, LVM for flexibility). LVM's built-in RAID (`--type raid5`) is available but mdadm is more mature for complex RAID. Cloud environments often use storage backends (EBS, Ceph) that provide redundancy below the LVM layer. |
| "LVM data is inaccessible without LVM" | LVM metadata is stored on the PVs. If you know the exact LV structure, data blocks can be read directly even without LVM tools. `pvdisplay`, `vgcfgrestore`, and `pvscan --cache` can recover from corrupted LVM metadata. `testdisk` can scan for LVM structures. The data is there - LVM is just the addressing layer. This matters for disaster recovery. |

---

### Failure Modes & Diagnosis

**LVM volume not found after reboot:**
```bash
# Symptom: /dev/vg_data/lv_app doesn't exist after reboot
# Errors in journal: "Failed to mount /app"

# Step 1: Check if PVs are detected:
pvs -a     # -a shows all, even if VG is not active
# or: pvscan --cache (scan and rebuild device mapper cache)
pvscan

# Step 2: Check if VG is active:
vgs
vgchange -ay vg_data    # activate all LVs in vg_data

# Step 3: If PVs show but VG doesn't activate - duplicate UUIDs:
# (Can happen when cloning VM images with LVM):
vgdisplay 2>&1 | grep -i duplicate
# Fix: change PV UUID on the duplicate:
pvchange --uuid /dev/sdb

# Step 4: Missing PV (disk failure):
vgs
# vg_data: shows 1 PV missing (degraded state)
# If mirror/RAID: volume may still be accessible
# If linear + missing PV: data on that PV is lost

# Step 5: Partial activation (for recovery when PV missing):
vgchange -ay --partial vg_data  # activate even with missing PV
# Can access LVs on surviving PVs (data on missing PV = gone)

# After fixing root cause:
vgscan
vgchange -ay
systemctl daemon-reload
mount -a    # remount all fstab entries
```

---

### Related Keywords

**Foundational:**
LNX-059 (Disk Partitioning), LNX-039 (Mounting Filesystems)

**Builds on this:**
LNX-049 (Filesystem Types), LNX-088 (Disk Performance)

**Related:**
LNX-102 (Storage Architecture at Scale)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `pvs` / `pvdisplay` | List/detail physical volumes |
| `vgs` / `vgdisplay` | List/detail volume groups |
| `lvs` / `lvdisplay` | List/detail logical volumes |
| `pvcreate /dev/sdX` | Initialize disk for LVM |
| `vgcreate VG /dev/sdX` | Create volume group |
| `lvcreate -n NAME -L SIZE VG` | Create logical volume |
| `lvextend -r -L +SizeG LV` | Extend LV and filesystem |
| `lvcreate -s -n SNAP -L SIZE LV` | Create snapshot |
| `pvmove /dev/old /dev/new` | Migrate data between disks |
| `vgextend VG /dev/sdX` | Add disk to volume group |

**3 things to remember:**
1. `lvextend` alone grows the block device - MUST also run `resize2fs` or `xfs_growfs` (or use `-r` flag)
2. Shrink: filesystem FIRST (smaller), then LV - never LV first (data loss!)
3. Snapshots add write overhead to origin LV; delete when backup is done

---

### Transferable Wisdom

LVM concepts appear directly in: AWS EBS (Elastic Block Store) = cloud's
version of LVM; volumes can be detached, grown, snapshotted without
downtime. LVM snapshots = foundation for VM snapshots (VMware, KVM, AWS
AMIs). Docker volumes on LVM: when Docker uses the devicemapper storage
driver (older), it creates LVM thin volumes per container. Kubernetes
persistent volumes via OpenStack Cinder or vSphere provision storage using
LVM-equivalent operations. The mental model (pool of storage -> virtual
volumes with dynamic sizing) is universal in storage systems.

---

### The Surprising Truth

LVM snapshots are routinely misunderstood to "back up" data. They don't.
A snapshot is a CoW overlay on the SAME storage device. If the disk fails,
BOTH the origin LV AND the snapshot are gone. Snapshots protect against
LOGICAL corruption (wrong file deleted, bad application update) but not
against PHYSICAL failure (disk dies). The correct use: (1) quiesce the
database (or use `fsfreeze`), (2) take snapshot (instant), (3) continue
normal operation, (4) copy snapshot data to ANOTHER storage location (network
backup, tape, object storage), (5) verify backup, (6) delete snapshot.
Step 4 is the actual "backup" - the snapshot is just a temporary mechanism
to get a consistent point-in-time view while the system stays online. Many
teams skip step 4 and think the snapshot IS the backup. This is why companies
lose data: the disk fails, taking both the original data and the "backup
snapshot" with it.

---

### Mastery Checklist

- [ ] Understands the three-layer LVM model (PV, VG, LV)
- [ ] Can extend an LV and filesystem online without downtime
- [ ] Can add a new disk to an existing VG and use the new space
- [ ] Can create and use LVM snapshots for consistent backups
- [ ] Knows the safe order for LV shrink operations (filesystem first)

---

### Think About This

1. A production database server has a 200 GB LV at 95% full. The VG has
   50 GB free. A new 1 TB disk is available. Outline the complete sequence
   of commands to: (a) add the new disk, (b) extend the LV by 500 GB,
   (c) grow the XFS filesystem, (d) verify the result - all without any
   downtime or data loss.

2. After taking an LVM snapshot for backup, `lvs` shows the snapshot is
   at 98% full with the backup only 40% complete. The backup server has
   slowed down unexpectedly. What will happen if the snapshot fills to 100%?
   What are your options in the next 5 minutes to save the backup?

3. After a hardware failure, a VG with two PVs (sdb and sdc) reports one
   PV as missing. The VG was created as linear (not RAID). You can still
   mount some LVs but not others. Explain: which LVs are still accessible
   vs inaccessible? How does LVM determine which data is on which PV?
   What is the path to data recovery for the inaccessible LVs?

---

### Interview Deep-Dive

**Foundational:**
Q: Explain the three layers of LVM and how you would extend a logical volume while the filesystem is mounted.
A: LVM has three layers: (1) Physical Volumes (PVs): raw disks or partitions initialized with `pvcreate`. They contribute storage to the pool in 4MB allocation units called physical extents. (2) Volume Group (VG): a pool created by combining PVs (`vgcreate`). The VG manages allocation of physical extents across all member PVs. (3) Logical Volumes (LVs): virtual block devices carved from the VG (`lvcreate`). They have a filesystem (ext4, XFS) and are mounted. The OS and applications see only the LV - they don't know or care about underlying physical disks. To extend a mounted filesystem: (a) Ensure the VG has free space: `vgs` (check "VFree" column). If not enough, add a disk: `pvcreate /dev/sdb && vgextend vg_data /dev/sdb`. (b) Extend the LV: `lvextend -L +50G /dev/vg_data/lv_app`. This grows the block device. (c) Grow the filesystem: ext4: `resize2fs /dev/vg_data/lv_app`. XFS: `xfs_growfs /mountpoint`. Both support online growth (mounted). Combined in one step: `lvextend -r -L +50G /dev/vg_data/lv_app` (-r = --resizefs = auto-resize filesystem). Verify: `df -h /app` shows the new size.

**Expert:**
Q: Design a backup strategy for a MySQL database using LVM snapshots that ensures consistency and doesn't impact production performance.
A: The challenge: MySQL writes continuously, plain file backup would be inconsistent. LVM snapshot provides a consistent point-in-time view. Strategy: (1) PREPARE MySQL for consistent snapshot: `mysql -e "FLUSH TABLES WITH READ LOCK;"` (acquires global read lock - all writes queued, reads continue). Or for InnoDB-only: use `FLUSH NO_WRITE_TO_BINLOG BINARY LOGS` and rely on InnoDB's crash-consistent snapshot. (2) RECORD binlog position (for point-in-time recovery later): `mysql -e "SHOW MASTER STATUS;"` (save binlog file and position). (3) TAKE LVM SNAPSHOT instantly: `lvcreate -s -n mysql_snap -L 20G /dev/vg0/lv_mysql`. 20G for expected changes during the backup window. Snapshot creation is near-instant (milliseconds). (4) RELEASE MySQL lock: `mysql -e "UNLOCK TABLES;"`. MySQL continues writing normally. Total lock time: ~1 second (just the snapshot creation). (5) MOUNT the snapshot: `mount -o ro /dev/vg0/mysql_snap /mnt/snap`. (6) BACKUP from snapshot (not from live volume): `rsync -av /mnt/snap/ /backup/$(date +%Y%m%d)/` OR `xtrabackup --backup --target-dir=/backup/...` on the snapshot directory. This doesn't impact production I/O (reads from snapshot, which reads unchanged blocks directly from origin - origin write amplification only for new writes after snapshot). (7) VERIFY backup: `mysqlcheck --all-databases --source-dir=/backup/...`. (8) REMOVE snapshot: `umount /mnt/snap && lvremove /dev/vg0/mysql_snap`. Performance: snapshot overhead during backup = every write to lv_mysql causes the old block to be copied to snapshot first. For a write-heavy MySQL: this adds ~10-30% write latency. Mitigation: take snapshots during off-peak hours, use read replicas for backup instead of production master, or use MySQL's native backup (Xtrabackup) which is LVM-snapshot-aware.
