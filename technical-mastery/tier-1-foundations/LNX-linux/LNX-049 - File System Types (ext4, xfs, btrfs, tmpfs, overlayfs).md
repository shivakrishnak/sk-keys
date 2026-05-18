---
id: LNX-049
title: "File System Types (ext4, xfs, btrfs, tmpfs, overlayfs)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-039, LNX-046
used_by: LNX-054, LNX-080, LNX-088
related: LNX-046, LNX-054, LNX-059
tags: [ext4, xfs, btrfs, tmpfs, overlayfs, vfat, filesystem, mkfs, mount, journaling]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/lnx/filesystem-types/
---

## TL;DR

Linux supports many filesystem types, each with different trade-offs.
**ext4**: most common, mature, journaling, fixed inode count, good general
purpose. **XFS**: high performance, large files, dynamic inodes, RHEL
default. **btrfs**: copy-on-write, snapshots, checksums, subvolumes - but
more complex. **tmpfs**: RAM-based (volatile, fast, for `/tmp`, `/run`).
**overlayfs**: union filesystem for Docker/container layers (lower=read-only,
upper=read-write). **vfat**: FAT32 for UEFI ESP and USB compatibility.
Choose ext4 for general use, XFS for large file workloads, btrfs for
snapshots/checksums.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-049 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | ext4, xfs, btrfs, tmpfs, overlayfs, vfat, filesystem, mkfs, mount |
| **Prerequisites** | LNX-039, LNX-046 |

---

### The Problem This Solves

**Problem 1**: You're setting up a 10 TB NAS for large video files. ext4's
inode structure (extent trees for large files) is fine, but XFS handles
large-file workloads with better performance and no fixed inode limit.
Which filesystem to choose depends on workload.

**Problem 2**: A staging server needs fast /tmp but the SSD is almost full.
`tmpfs` mounts a RAM-based filesystem at `/tmp` with zero disk usage.

**Problem 3**: Docker containers need to start fast without copying 2 GB of
base image. overlayfs mounts the base image as a read-only lower layer
and adds a thin writable upper layer per container - no copying.

---

### Textbook Definition

**Filesystem**: Defines how files and directories are stored and organized
on a storage device. Includes: data structures (inodes, directories, extent
trees), allocation algorithms, journaling for crash recovery.

**Journaling**: Writes a log ("journal") of pending operations before committing
them. On crash, the journal replays uncommitted operations. Prevents filesystem
corruption. Types: metadata journaling (ext4 default), full-data journaling
(slower), ordered mode (data written before metadata - ext4 default behavior).

**Copy-on-Write (CoW)**: Instead of overwriting blocks, CoW writes new data
to a new location and updates the pointer. Enables cheap snapshots (just
save the pointer tree). Used by btrfs, ZFS, overlayfs.

**Union filesystem**: Stacks multiple directories, presenting a merged view.
Lower layers are read-only. Writes go to the uppermost writable layer.
Used by overlayfs (Docker), AUFS, OverlayFS.

---

### Understand It in 30 Seconds

```bash
# === See what filesystem types are mounted ===
df -T                      # show filesystem type for each mount
mount | grep -v "^sysfs\|^proc\|^devtmpfs\|^tmpfs\|^cgroup"  # "real" mounts

# === Create filesystems ===
mkfs.ext4 /dev/sdb1        # ext4 (default options)
mkfs.xfs /dev/sdb1         # XFS
mkfs.btrfs /dev/sdb1       # btrfs
mkfs.vfat -F 32 /dev/sdb1  # FAT32 (for USB or EFI)

# === ext4 inspection ===
tune2fs -l /dev/sda1       # filesystem info (UUID, inode count, features)
tune2fs -l /dev/sda1 | grep -E "Inode count|Free inodes|Block count|Free blocks"
dumpe2fs -h /dev/sda1      # detailed ext2/3/4 info
e2fsck -n /dev/sda1        # dry-run filesystem check (don't fix, just report)

# === XFS inspection ===
xfs_info /dev/sdb1         # XFS filesystem info
xfs_repair -n /dev/sdb1    # dry-run XFS repair
xfs_db -c "frag -f" /dev/sdb1  # fragmentation check

# === btrfs ===
btrfs filesystem show      # list btrfs filesystems
btrfs subvolume list /     # list subvolumes
btrfs subvolume snapshot / /.snapshots/backup  # create snapshot
btrfs filesystem df /      # space usage (different from df!)
btrfs scrub start /        # verify data integrity (background)
btrfs scrub status /       # check scrub progress

# === tmpfs ===
mount -t tmpfs -o size=512m tmpfs /tmp    # mount 512MB RAM-based /tmp
df -h /tmp                 # shows tmpfs, size, usage
# tmpfs contents lost on reboot/unmount - volatile!

# === overlayfs (Docker uses this) ===
mkdir -p /lower /upper /work /merged
# Create overlayfs:
mount -t overlay overlay \
    -o lowerdir=/lower,upperdir=/upper,workdir=/work \
    /merged
# lower = read-only (base)
# upper = read-write (writes go here)
# merged = the combined view
# Inspect Docker overlayfs:
docker inspect CONTAINER | grep -A5 "GraphDriver"
ls /var/lib/docker/overlay2/
```

---

### First Principles

**Why different filesystems?**
```
Trade-off dimensions:
  Simplicity  <--> Features
  Performance <--> Durability
  Disk usage  <--> Snapshots
  Random I/O  <--> Sequential I/O
  Small files <--> Large files

ext4 = balanced for general use:
  - Extents (contiguous block ranges) for large file efficiency
  - Fixed inode count (allocated at mkfs time)
  - Journaling for crash recovery
  - Mature: in kernel since 2.6.28 (2008), heavily tested
  - Weakness: inode exhaustion with millions of small files

XFS = optimized for large files and high throughput:
  - Dynamic inode allocation (no fixed limit)
  - Parallel I/O (allocation groups for concurrent writes)
  - Delayed allocation (reduces fragmentation)
  - Weakness: cannot shrink filesystem (only grow)
  - Cannot recover from power failure without journal replay (journaled)
  - RHEL/CentOS/Rocky default since RHEL 7

btrfs = feature-rich, modern:
  - Copy-on-Write: every write goes to a new location
  - Snapshots: instant (just save pointer tree)
  - Checksums on data AND metadata: detects silent corruption
  - Subvolumes: separate namespace within one filesystem
  - Compression: transparent lzo/zstd/zlib compression
  - Weakness: more complex, higher CPU/memory overhead, CoW write
    amplification for random writes, repair tools less mature than ext4

tmpfs = ephemeral RAM storage:
  - Data exists ONLY in RAM (no disk backing)
  - Lost on reboot, unmount, or OOM
  - Extremely fast (RAM speeds)
  - Uses swap when RAM is full (unless configured otherwise)
  - Use: /tmp, /run, /dev/shm, /sys/fs/cgroup

overlayfs = union filesystem for containers:
  - Stacks directories: lower (read-only) + upper (read-write)
  - Reads: from lower if not in upper, from upper if modified
  - Writes: CoW to upper layer
  - Deletes: whiteout file in upper
  - Docker: each image layer is a lower directory
  - Container: upper layer is the writable container layer
```

---

### Thought Experiment

Choosing filesystem for different workloads:

```bash
# Scenario 1: Database server (MySQL, 2TB data volume)
# Access pattern: random reads/writes, 8-16KB I/O size
# Requirements: durability (no corruption), performance
mkfs.xfs -f /dev/sdb1       # XFS: good random I/O, no inode limit
# Also consider: ext4 is fine, avoid btrfs (CoW amplifies random writes)
# Mount options: noatime (no access time update per read = less I/O)
# /etc/fstab: /dev/sdb1 /data xfs defaults,noatime 0 0

# Scenario 2: Log aggregation server (millions of small log files)
# Access pattern: write-heavy small files (1-10KB each)
# Requirements: no inode exhaustion
mkfs.xfs -f /dev/sdc1       # XFS: dynamic inodes = no limit
# OR: ext4 with higher inode density:
mkfs.ext4 -T news /dev/sdc1  # "news" profile = more inodes per GB
tune2fs -l /dev/sdc1 | grep "Inode count"

# Scenario 3: Container image store (Docker)
# Access pattern: layered reads, occasional writes
# Requirements: fast container start, efficient storage
# -> overlayfs (handled automatically by Docker daemon)
# Just ensure: root filesystem is ext4 or XFS
cat /etc/docker/daemon.json
# {"storage-driver": "overlay2"}   <- default on modern Docker

# Scenario 4: High-performance temp directory for build system
# Access pattern: create/delete millions of temp files rapidly
# Requirements: fast, not persisted (lost on reboot is fine)
mount -t tmpfs -o size=8g tmpfs /tmp
# tmpfs in RAM: fastest possible, no disk wear

# Scenario 5: Backup server with snapshot capability
mkfs.btrfs /dev/sdd1        # btrfs: snapshots for daily backups
# Take daily snapshot:
btrfs subvolume snapshot /mnt/data \
    /mnt/data/.snapshots/$(date +%Y%m%d)
# List snapshots:
btrfs subvolume list /mnt/data

# Check filesystem health after storage incidents:
btrfs scrub start /mnt/data   # verify checksums on all data
btrfs scrub status /mnt/data  # check for errors found
```

---

### Mental Model / Analogy

```
Filesystem types as different types of notebooks:

ext4 = Standard lined notebook
  - Familiar, reliable, everyone knows how to use it
  - Fixed number of pages (inode count = fixed)
  - Notes erased if power fails mid-write (unless journaled)
  - Good for: everything normal

XFS = Premium professional notebook
  - More pages can be added dynamically
  - Designed for quick sequential note-taking (large files)
  - Can't make it smaller, only larger
  - Good for: databases, large files, high throughput

btrfs = Advanced notebook with special features
  - Every edit creates a new version (CoW)
  - Can take instant "photos" of all pages (snapshots)
  - Detects if pages got damaged (checksums)
  - Can split into sections (subvolumes)
  - More complex, heavier, but more capable
  - Good for: when you need snapshots or data integrity verification

tmpfs = Whiteboard (volatile)
  - Ultra fast (just write on the board)
  - Erased when you turn off the lights (reboot)
  - Perfect for scratch work, temp files

overlayfs = Transparency overlay on a printed document
  - Base document is read-only (lower layer)
  - Write on the transparency (upper layer)
  - See: combined view
  - Erase transparency: back to original
  - Docker images = stack of transparencies
```

---

### Gradual Depth - Five Levels

**Level 1:**
ext4 = default Linux filesystem (most VMs, general purpose). XFS = RHEL
default, better for large files. tmpfs = RAM-based temp (fast, volatile).
`df -T` to see filesystem types. `mkfs.ext4 /dev/sdb1` to create. `tune2fs -l`
to inspect ext4.

**Level 2:**
Journaling modes: `data=ordered` (ext4 default - writes data before metadata),
`data=journal` (safest, slowest), `data=writeback` (fastest, less safe).
`noatime` mount option: disables access time update (atime) per file read,
reduces write I/O for read-heavy workloads. btrfs subvolumes and snapshots.
ext4 `barrier=0` vs `barrier=1` (disk write barriers for data integrity).

**Level 3:**
XFS allocation groups (AGs): XFS divides the filesystem into AGs for parallel
allocation. Crucial for high-concurrency write performance. `mkfs.xfs -d
agcount=N` to set AG count. ext4 `resize2fs`: grow filesystem after disk
expansion (`lvextend` + `resize2fs`). XFS can ONLY grow (not shrink): `xfs_growfs`.
btrfs RAID: btrfs can span multiple devices with RAID 0/1/5/6/10 natively.
`btrfs device add /dev/sde /mnt/btrfs`. overlayfs metacopy optimization:
for unchanged metadata, just copies metadata to upper layer, not full file.

**Level 4:**
ext4 `data=journal` vs `fsync()` for database durability. MySQL/InnoDB
default: relies on `fsync()` after each transaction commit (`innodb_flush_log_at_trx_commit=1`).
btrfs CoW write amplification: every random write copies the entire page
(4KB minimum). For databases with 512-byte sectors and 8KB random writes:
btrfs writes 4KB per 512-byte change (8x amplification). Disable CoW for
database files: `chattr +C database.ibd`. F2FS (Flash-Friendly FileSystem):
optimized for NAND flash (eMMC, SSD), minimizes write amplification, used
in Android.

**Level 5:**
ZFS on Linux (zfsonlinux): OpenZFS port. Superior checksumming, RAID-Z,
deduplication, compression. Not in-kernel (CDDL license incompatible with GPL).
Used in TrueNAS, Proxmox. bcachefs: new kernel filesystem (merged in 6.7)
combining ext4 stability with btrfs features. io_uring and direct I/O:
bypasses page cache and some VFS overhead for high-IOPS applications (io_uring
with O_DIRECT for NVMe SSDs in databases). SPDK (Storage Performance
Development Kit): bypasses kernel filesystem and block layer entirely for
line-rate NVMe storage from userspace.

---

### Code Example

**BAD - filesystem choices that hurt production:**
```bash
# BAD 1: Using btrfs on a high-random-write database server:
mkfs.btrfs /dev/sdb1
mount /dev/sdb1 /var/lib/mysql
# Problems:
# - CoW writes amplify MySQL's random 8KB writes
# - MySQL writes to data files -> btrfs copies entire 4KB page
# - Database files fragment badly over time (CoW fragmentation)
# - MySQL performance drops 30-50% vs ext4 or XFS

# GOOD: Use XFS for database volumes:
mkfs.xfs -f /dev/sdb1
mount -o noatime,nodiratime /dev/sdb1 /var/lib/mysql
# OR: disable CoW for MySQL files on btrfs (if btrfs required):
chattr +C /var/lib/mysql    # disable CoW for directory
# (Only effective for files created AFTER setting attribute)

# BAD 2: Not accounting for inode exhaustion on ext4 for log servers:
mkfs.ext4 /dev/sdb1         # default inode ratio = one inode per 16KB
# For log server creating millions of tiny (256 byte) log files:
# Disk fills up at 100% inodes long before 100% disk space!

# GOOD: Create ext4 with higher inode density:
mkfs.ext4 -T small /dev/sdb1
# "small" profile: one inode per 1KB (16x more inodes)
# OR: specify inode ratio directly:
mkfs.ext4 -i 4096 /dev/sdb1   # one inode per 4KB bytes
# Verify:
tune2fs -l /dev/sdb1 | grep "Inode count"

# BAD 3: Forgetting noatime for read-heavy workloads:
mount /dev/sdb1 /data        # default: atime update on every read
# Every file read triggers a WRITE (atime update) -> double I/O

# GOOD: Mount with noatime:
mount -o noatime /dev/sdb1 /data
# In /etc/fstab:
# UUID=xxx /data ext4 defaults,noatime 0 2
# Or use relatime (default in modern kernels):
# Updates atime only if newer than mtime (good compromise)
mount -o relatime /dev/sdb1 /data
```

---

### Comparison Table

| Feature | ext4 | XFS | btrfs | tmpfs | overlayfs |
|---------|------|-----|-------|-------|-----------|
| **Journaling** | Yes | Yes | No (CoW) | N/A | N/A |
| **Snapshots** | No | No | Yes | No | Via upper layer |
| **Max file size** | 16 TB | 8 EB | 16 EB | RAM | Depends |
| **Inodes** | Fixed | Dynamic | Dynamic | Dynamic | Depends |
| **Checksums** | No | No | Data+Meta | N/A | N/A |
| **Shrinkable** | Yes | No | Yes | N/A | N/A |
| **Random write perf** | Good | Good | Moderate | Excellent | Good |
| **Kernel stability** | Excellent | Excellent | Good | Excellent | Excellent |
| **Best for** | General use | Large files, RHEL | Snapshots, integrity | /tmp, /run | Containers |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "btrfs is production-ready for all workloads" | btrfs is stable for READS and metadata operations but can have reliability issues with RAID 5/6 (known parity bug, avoid for critical data). btrfs for single-drive general use is fine. SUSE uses it as default (read-only snapshots for system rollback), which is a read-heavy workload. For databases or write-heavy workloads, ext4 or XFS is safer. btrfs RAID 5/6 should be avoided in production. |
| "tmpfs uses only RAM" | tmpfs uses RAM primarily but CAN use swap. When a system is under memory pressure, the kernel can swap out tmpfs pages to disk. `tmpfs` data is NOT always in RAM. It's "virtual memory based" - may be in RAM or swap. For truly RAM-only (no swap): use `ramfs` (no size limit, no swap, dangerous). `tmpfs` is the practical choice because it self-limits and can swap. |
| "ext4 and XFS have the same fsck procedure" | Very different. `e2fsck` (ext4) is powerful and can be run offline (unmounted) to fix many issues. `xfs_repair` requires the filesystem to be unmounted, and repair of a corrupted XFS is less reliable. XFS journaling means most corruption is avoided (journal replay at mount), but severe corruption may be unrecoverable without backups. This is a trade-off: XFS trusts its journal; ext4's fsck is more battle-tested. |
| "overlayfs stores all changes in the upper layer" | For most writes, yes. But deletes are implemented as "whiteout files" in the upper layer (a character device with 0,0 dev number). The lower layer file still exists; the overlayfs merge algorithm hides it when it sees the whiteout. This means deleting a large file in a container's upper layer doesn't free disk space from the lower layer - it adds a whiteout file. The lower layer (image) still has the data. `docker system prune` removes unused image layers to reclaim space. |
| "You can mount any filesystem read-write with just `mount`" | Some filesystem types require specific conditions: XFS won't mount if the journal is dirty (requires `xfs_repair`). ext4 won't mount cleanly if `needs_recovery` flag is set without first replaying the journal (`e2fsck` or normal mount). Encrypted filesystems (LUKS) need `cryptsetup open` before mounting. Network filesystems (NFS, CIFS) need network connectivity and remote server availability. |

---

### Failure Modes & Diagnosis

**ext4 filesystem corruption after power failure:**
```bash
# Symptom: system won't boot, or mount fails with errors
# "EXT4-fs error: ...", "journal superblock read failed"

# Step 1: Try mounting as read-only first
mount -o ro /dev/sda1 /mnt    # if fails -> bad superblock

# Step 2: Filesystem check (MUST be unmounted):
e2fsck -f /dev/sda1           # force check even if marked clean
e2fsck -p /dev/sda1           # auto-fix (no prompts)
e2fsck -y /dev/sda1           # answer "yes" to all questions

# Step 3: If superblock is corrupted, use backup:
mke2fs -n /dev/sda1           # show where backup superblocks are
# Example output: superblock backups at 8193, 24577, 40961, ...
e2fsck -b 8193 /dev/sda1      # use backup superblock 8193 to recover

# Step 4: For severely corrupted filesystem:
debugfs /dev/sda1             # interactive ext2/3/4 debugger
# ls - list directory
# dump <file> /tmp/recovered  # extract file from corrupted FS

# XFS equivalent:
xfs_repair /dev/sdb1          # repair XFS (must be unmounted)
xfs_repair -L /dev/sdb1       # clear log if corrupted (DATA LOSS RISK)

# Prevention: UPS, `sync` before power down, ensure filesystem not
# mounted R/W during power failures
```

---

### Related Keywords

**Foundational:**
LNX-039 (Mounting Filesystems), LNX-046 (Filesystem Internals)

**Builds on this:**
LNX-054 (LVM), LNX-080 (Container Internals), LNX-088 (Disk Performance)

**Related:**
LNX-059 (Disk Partitioning), LNX-046 (Inodes, VFS)

---

### Quick Reference Card

| Filesystem | `mkfs` command | Best for |
|-----------|---------------|---------|
| ext4 | `mkfs.ext4 /dev/sdbX` | General purpose, VMs |
| XFS | `mkfs.xfs /dev/sdbX` | Large files, RHEL default |
| btrfs | `mkfs.btrfs /dev/sdbX` | Snapshots, checksums |
| vfat/FAT32 | `mkfs.vfat -F 32 /dev/sdbX` | USB, EFI partition |
| tmpfs | `mount -t tmpfs -o size=Xm tmpfs /mnt` | /tmp, /run (volatile) |

**3 things to remember:**
1. ext4 has fixed inode count (set at mkfs); XFS has dynamic inodes - use XFS for millions of files
2. `noatime` mount option eliminates unnecessary write-on-read (reduces I/O by 10-30%)
3. overlayfs = lower (read-only image) + upper (read-write per container) = Docker layers

---

### Transferable Wisdom

Filesystem selection thinking transfers to: cloud storage tiers (S3 Standard
vs EFS vs FSx - same trade-off analysis: performance, cost, features), database
storage engines (InnoDB CoW-like MVCC similar to btrfs; MyISAM like simple
flat files), Java serialization formats (Protobuf streaming vs JSON = sequential
vs random access trade-off). Container base image design: using read-only
lower layers and thin upper layers is the same as how btrfs snapshots work -
share the common data, only store the delta.

The "journaling vs CoW" trade-off appears in databases: ext4 journaling =
write-ahead log (WAL) in PostgreSQL. btrfs CoW = MVCC storage in PostgreSQL/
InnoDB. tmpfs pattern appears in Kubernetes: emptyDir volumes are tmpfs by
default (use for fast scratch storage, cache within a pod, shared between
containers in a pod).

---

### The Surprising Truth

Docker doesn't use any of the filesystems you'd expect - it uses overlayfs,
a union filesystem that stacks directories without any traditional block
device management. A Docker image layer is just a DIRECTORY of files (not
a disk image). When you run `docker pull ubuntu`, Docker downloads compressed
tar archives for each layer and extracts them to directories under
`/var/lib/docker/overlay2/`. When a container starts, Docker mounts these
directories stacked with overlayfs in about 50 milliseconds - no copying,
no disk formatting. The "image" is just directories. This is why `docker
save` produces a tar file containing layer tar files, not a disk image (no
`dd if=/dev/sda` involved). The "container filesystem" you see inside the
container is entirely a kernel illusion created by overlayfs + mount
namespaces. This design lets 100 containers share the same Ubuntu base image
layer (the same files in the same directory), saving gigabytes of disk space.
Change one file inside the container? overlayfs CoW copies only that file
to the upper layer. The original image layer is never modified.

---

### Mastery Checklist

- [ ] Can identify filesystem type in use and choose appropriately for workload
- [ ] Can create and inspect ext4, XFS, and btrfs filesystems
- [ ] Understands inode limits in ext4 and how XFS solves this
- [ ] Understands overlayfs and how Docker uses it
- [ ] Can recover from filesystem corruption using e2fsck or xfs_repair

---

### Think About This

1. You're migrating a database from a server with ext4 to a new server
   with btrfs. The DBA reports 40% performance degradation after migration.
   Disk I/O shows high write latency. Explain the root cause and propose
   two solutions (one that disables CoW for the database, one that avoids
   it entirely at filesystem selection).

2. A Docker host has 500 GB free disk space but `docker pull` fails with
   "no space left on device." `df -h` shows `/var/lib/docker` at 15% used.
   What filesystem feature might be causing this? How would you diagnose
   and confirm? (Hint: ext4 reserves 5% for root by default, and Docker
   overlayfs can exhaust inodes.)

3. You need a fast, large temporary workspace for a build process that
   creates 50 million small files (averaging 2KB each). Total data = ~100GB.
   The server has 256 GB RAM and a 2TB NVMe SSD. Recommend a filesystem
   and explain your mount options for: (a) maximum speed with data loss OK,
   (b) balance of speed and durability.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between ext4 and XFS, and when would you choose each?
A: Both are mature, journaled filesystems, but with different strengths. ext4: The most widely used Linux filesystem. Mature (since 2008), excellent tool support (`e2fsck`, `debugfs`). Uses extent-based block allocation (contiguous ranges for large files). FIXED inode count: set at `mkfs` time based on filesystem size and inode ratio (default: 1 inode per 16KB of space). On a 1TB filesystem: ~65 million inodes. Weakness: inode exhaustion if you create millions of small files. Shrinkable with `resize2fs`. Best for: general purpose, VMs, boot volumes, application data. XFS: Default filesystem for RHEL/CentOS since RHEL 7. Designed for high-performance large-file workloads. DYNAMIC inode allocation: inodes created on demand, no fixed limit. Allocation groups (AGs) enable parallel writes without locking (critical for database performance on multi-core systems). Cannot be shrunk (only grown with `xfs_growfs`). Best for: database data volumes, log aggregation (millions of files), NFS servers, streaming workloads. Choose ext4 when: you might need to shrink the filesystem, familiarity matters, boot volume (standard). Choose XFS when: RHEL environment (already default), large files (video, backups), high concurrency, potential inode exhaustion, need to grow the filesystem online.

**Intermediate:**
Q: How does Docker use overlayfs, and what are the implications for disk space management?
A: Docker uses overlayfs as its default storage driver (`overlay2`). How it works: Each image layer is stored as a directory under `/var/lib/docker/overlay2/LAYER_HASH/diff/`. When a container starts, the Docker daemon mounts these directories using overlayfs: lower directories (image layers, read-only, stacked bottom-to-top), upper directory (container's writable layer, at `/var/lib/docker/overlay2/CONTAINER_HASH/diff/`), work directory (temporary overlayfs work directory). Result: the container sees a merged view. Reading a file: overlayfs returns the file from the uppermost layer that has it (upper first, then lower layers in order). Writing a file: overlayfs copies the file from lower layer to upper layer (Copy-on-Write), then modifies it in upper. This copy is the first write to that file. Disk space implications: (1) Image layers are SHARED. 100 containers running Ubuntu base image share the same lower layer directory - no duplication. (2) Container writable layer: only modified/created files. A container that reads but never writes uses nearly zero extra disk space. (3) Deleting a file from a lower layer: overlayfs creates a whiteout file in the upper layer (small marker file). The lower layer data still exists. To reclaim: delete the image. (4) Inode exhaustion: overlayfs on ext4 can exhaust inodes (each layer's files consume inodes from the underlying filesystem). `docker system df` shows image/container/volume disk usage. `docker system prune` removes unused layers.

**Expert:**
Q: Compare btrfs Copy-on-Write with ext4 journaling as approaches to filesystem consistency. When does each fail?
A: Two fundamentally different approaches to crash consistency: ext4 JOURNALING: Before writing to the filesystem, ext4 writes a journal entry (the intended changes as a transaction). After power failure, the journal is replayed to complete or discard incomplete transactions. The metadata is consistent (no partial writes). Failure mode: journal itself can be corrupted (power failure during journal write). Recovery: `e2fsck -b` with backup superblock. Data in ordered mode: data is written before metadata journal entry. Still possible to lose last few seconds of data. Full-data journaling (double-write) avoids this but halves write throughput. Journal also wears SSDs faster for write-heavy workloads. btrfs CoW: Writes NEVER overwrite existing data in place. New data goes to a new location. The B-tree root pointer is updated atomically (single 8-byte pointer write). If power fails: either the old root pointer (old data, consistent state) or the new root pointer (new data, consistent state) survives - never partial. Checksums on all data and metadata: detect bit-rot, silent corruption (drives returning wrong data). Failure modes: (1) Fragmentation: CoW means every write goes to a new location, so files become fragmented over time. `btrfs filesystem defragment` periodically. (2) CoW and databases: databases do 4KB-aligned random writes to pre-allocated files. btrfs copies the entire 4KB page even if only 8 bytes changed (write amplification). Workaround: `chattr +C database.file` disables CoW for that file. (3) RAID 5/6 parity bug: btrfs RAID 5/6 has a known write-hole bug (data loss on power failure during parity update). Avoid for production RAID. (4) Metadata fragmentation on full filesystems: btrfs performs poorly when the filesystem is >85% full due to metadata overhead. Use btrfs when checksums or snapshots are needed; use ext4/XFS for pure performance.
