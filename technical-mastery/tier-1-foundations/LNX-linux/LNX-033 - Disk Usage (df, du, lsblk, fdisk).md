---
id: LNX-033
title: "Disk Usage (df, du, lsblk, fdisk)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-007, LNX-008
used_by: LNX-039, LNX-025
related: LNX-039, LNX-025, LNX-054
tags: [df, du, lsblk, fdisk, disk-usage, filesystem, block-device, storage, inodes]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/lnx/disk-usage/
---

## TL;DR

Four tools for disk: `df -h` (filesystem usage - "is my disk full?"),
`du -sh *` (directory sizes - "what's using the space?"), `lsblk`
(block devices - "what disks and partitions exist?"), `fdisk -l`
(partition table details - "how is the disk partitioned?"). Production
triage: disk alert fires -> `df -h` (which filesystem) -> `du -sh /*`
(which directory) -> narrow down recursively. Disk full kills
applications, corrupts databases, and halts logs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-033 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | df, du, lsblk, fdisk, disk usage, storage, block devices, inodes |
| **Prerequisites** | LNX-007, LNX-008 |

---

### The Problem This Solves

"Disk full" is one of the most common production emergencies. Database
writes fail. Log rotation fails. Application can't write temp files.
The entire system becomes unstable. The immediate need: find what's
consuming space in the next 5 minutes. `df -h` and `du -sh` answer
this. Secondary need: understand the disk layout before adding/expanding
storage. `lsblk` and `fdisk` answer this.

---

### Textbook Definition

**df** (disk free): Reports filesystem-level disk space usage. Shows
how much space is used and available per mounted filesystem. `-h` = human-readable.

**du** (disk usage): Reports space used by files and directories.
`-s` = summary (total only). `-h` = human readable. Recursively
calculates space used by a directory tree.

**lsblk** (list block devices): Shows block devices (disks, partitions,
LVM logical volumes) in a tree structure. Shows size, type, mount point.

**fdisk**: Manipulates disk partition tables. `fdisk -l` = list all
partition tables (read-only). Can create, delete, and modify partitions.
`parted` is the modern alternative for GPT disks.

---

### Understand It in 30 Seconds

```bash
# FILESYSTEM USAGE (is my disk full?):
df -h               # all filesystems, human readable
df -h /             # just the root filesystem
df -h /var          # specific path's filesystem
df -i               # inode usage (files, not space)

# DIRECTORY SIZES (what's using the space?):
du -sh /var/log     # total size of /var/log
du -sh *            # size of each item in current directory
du -sh /* 2>/dev/null | sort -rh | head -20  # largest root dirs
du -sh /var/* 2>/dev/null | sort -rh | head -10  # largest in /var

# BLOCK DEVICES (what disks/partitions exist?):
lsblk               # tree view of all block devices
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT  # specific columns

# PARTITION TABLE (how is disk structured?):
sudo fdisk -l                # all disks
sudo fdisk -l /dev/sda       # specific disk

# Find largest files specifically:
find /var -type f -size +100M -ls 2>/dev/null | sort -k 7 -rn
```

---

### First Principles

**df vs du - why they differ:**
`df` asks the filesystem: "how many blocks are used?" (kernel-reported).
`du` walks the directory tree and sums file sizes. They can differ because:
- Files that are deleted but still open by a process: df shows the space
  as used (the kernel still has the inode), du doesn't see the file
  (deleted from directory). This is the classic "deleted file not freeing space" case.
- Sparse files: df may count the allocated space, du may report the logical size.
- Filesystem overhead (metadata, journal) counted by df, not by du.

**inode vs block usage:**
Each file uses: (1) data blocks (the actual content), (2) one inode (metadata:
permissions, timestamps, pointers to blocks). `df -h` = block usage. `df -i` = inode usage.
A filesystem can run out of inodes while still having free blocks: millions of tiny
files exhaust the inode table. Symptoms: "No space left on device" error but `df -h`
shows available space. `df -i` will show 100% inode usage.

---

### Thought Experiment

Disk alert: `/var` at 95%. You have 5 minutes before the application fails.

```bash
# Minute 1: where is the space?
df -h /var           # confirms /var is the full filesystem

# Minute 2: what directory in /var?
du -sh /var/* 2>/dev/null | sort -rh | head -10
# Output:
# 45G  /var/log
# 8G   /var/cache
# 2G   /var/lib

# Minute 3: what's in /var/log?
du -sh /var/log/* 2>/dev/null | sort -rh | head -10
# Output:
# 40G  /var/log/myapp
# 3G   /var/log/nginx

# Minute 4: largest files in /var/log/myapp
ls -lhS /var/log/myapp | head -10
# Output: debug.log  40G  (log level is DEBUG in production!)

# Minute 5: emergency space reclaim
# Option A: truncate active log file (don't delete open files!)
> /var/log/myapp/debug.log    # empty the file without deleting
# Option B: find and delete old rotated logs
find /var/log/myapp -name "*.log.*" -mtime +7 -delete
# Option C: change log level to WARN immediately (reduce future growth)
```

---

### Mental Model / Analogy

Disk investigation tools are like **measuring a filing cabinet:**

```
df -h = "How full is the entire cabinet?"
  Cabinet has 100 drawers total.
  Used: 95 drawers. Free: 5.
  
du -sh * = "Which section uses how many drawers?"
  Legal section: 45 drawers
  Finance: 25 drawers  
  HR: 20 drawers
  
du -sh on the biggest = "What's IN Legal?"
  2023 cases: 30 drawers (found it!)
  2024 cases: 15 drawers
  
lsblk = "How many cabinets are there and where are they?"
  Cabinet A: 100 drawers (mounted as /)
  Cabinet B: 50 drawers (mounted as /data)
  Cabinet C: 200 drawers (not mounted)
  
fdisk -l = "What are the physical dimensions and divisions of each cabinet?"
  Cabinet A: Total 200 drawers
    - Section 1 (partition 1): 100 drawers = Cabinet A (/)
    - Section 2 (partition 2): 100 drawers = swap space
```

---

### Gradual Depth - Five Levels

**Level 1:**
`df -h` (disk full?) and `du -sh * | sort -rh` (what's big?). These
two commands diagnose 90% of disk-full situations.

**Level 2:**
`du -sh /* 2>/dev/null | sort -rh | head` for top-level, then drill
down recursively. `df -i` for inode exhaustion. `lsblk` to see disk
structure. `ls -lhS` (sort by size) to find largest files in a directory.

**Level 3:**
`find /path -size +100M -type f -ls` for large file discovery.
`lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT,UUID` for full device info.
Interpreting `df` columns: Used + Available != Size (reserved blocks).
ext4 reserves 5% by default for root. `tune2fs -m 1 /dev/sda1` reduces
to 1% (frees space on non-root filesystems).

**Level 4:**
`lsof | grep deleted` for deleted-but-open files wasting space.
`blockdev --getsize64 /dev/sda` raw device size.
Thin-provisioned storage: physical disk < advertised size (overcommit).
`df` shows filesystem view, not physical reality.
`iostat -xz 1` for disk I/O performance (separate from space).

**Level 5:**
`ncdu` = ncurses disk usage viewer (interactive, like a file manager for
disk usage - extremely useful for manual investigation). For cloud/containers:
Docker `du` often misleads (volumes, overlay fs). `docker system df` for
Docker-specific storage. EBS volumes on AWS: `df -h` shows filesystem usage,
but EBS capacity is shown in AWS console. Growing a live volume: `lvextend` +
`resize2fs` (LVM) or `growpart` + `resize2fs` (non-LVM). All without reboot.

---

### Code Example

**BAD - disk investigation mistakes:**
```bash
# BAD 1: du on root with all filesystems (includes /proc, /sys)
du -sh /*
# /proc and /sys are virtual filesystems - du gets confused
# Use: du -sx /* (x = one filesystem only) or exclude them
du -sh /* --exclude=/proc --exclude=/sys 2>/dev/null

# BAD 2: deleting files while processes have them open
rm /var/log/myapp/app.log
# df still shows space used! The process has the file open.
# Space freed only when process closes the file.
# CORRECT: truncate instead:
> /var/log/myapp/app.log    # empty file without deleting

# BAD 3: not checking inodes when "disk full" but space available
df -h    # shows 50% space available!
# But: df -i shows 100% inodes used
# App still gets "no space left on device" because no inodes available
# Fix: find and delete millions of tiny temp files
find /tmp -type f -mtime +1 -delete
```

**GOOD - systematic disk analysis:**
```bash
# Complete disk space triage script:
disk_triage() {
    echo "=== FILESYSTEM USAGE ==="
    df -h
    
    echo ""
    echo "=== INODE USAGE ==="
    df -i | awk 'NR==1 || $5+0 > 50' | head -20
    # Show filesystems with >50% inode usage
    
    echo ""
    echo "=== TOP 10 DIRS BY SIZE (/) ==="
    du -sx /* 2>/dev/null | sort -rn | head -10 | \
        awk '{printf "%s\t%s\n", $1*512, $2}' | \
        while read bytes dir; do
            echo "$(( bytes / 1024 / 1024 ))M $dir"
        done
    
    echo ""
    echo "=== LARGE FILES (>500MB) ==="
    find / -xdev -type f -size +500M \
        -printf "%s %p\n" 2>/dev/null | \
        sort -rn | head -10 | \
        awk '{printf "%.0fM %s\n", $1/1024/1024, $2}'
    
    echo ""
    echo "=== DELETED FILES STILL OPEN ==="
    lsof 2>/dev/null | grep deleted | \
        awk '{print $7, $9}' | sort -rn | head -10
}

# Quick space recovery:
recover_space() {
    echo "Cleaning package cache..."
    apt-get clean 2>/dev/null || yum clean all 2>/dev/null
    
    echo "Vacuuming systemd journal to 500MB..."
    journalctl --vacuum-size=500M
    
    echo "Deleting old temp files..."
    find /tmp -type f -mtime +1 -delete 2>/dev/null
    find /var/tmp -type f -mtime +7 -delete 2>/dev/null
    
    echo "Disk usage after cleanup:"
    df -h
}
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "du and df should always match" | They can differ significantly. Deleted-but-open files are counted by df (kernel tracks the space) but not du (file not in directory). Filesystem reserved space (ext4's 5% root reserve), sparse files, and journal overhead also cause differences. `df - du != 0` is normal. |
| "Deleting large files immediately frees space" | Only if no process has the file open. If a log file is being written by an application, deleting it removes the directory entry but the data blocks are freed only when the application closes the file. Use `lsof | grep deleted` to find these. Fix: truncate the file (`> filename`) instead of deleting, or restart the application. |
| "df shows all disk space" | df only shows MOUNTED filesystems. A disk that is present but not mounted (visible in `lsblk`) won't appear in `df`. Similarly, LVM volumes that aren't mounted, network filesystems that are disconnected, and tmpfs (RAM-based) show differently. |
| "inode exhaustion is rare" | Inode exhaustion is common in: mail server spool directories, PHP session directories, npm node_modules trees (millions of tiny files), container image layer directories. `df -i` should be part of any disk monitoring setup alongside `df -h`. |
| "du -s / shows total disk usage" | `du -s /` sums all files accessible from root, which may traverse network mounts (NFS), virtual filesystems (/proc, /sys - though these are usually empty), and other mount points. Use `du -sx /` (x = stay on one filesystem) for accurate local disk usage. |

---

### Failure Modes & Diagnosis

**"No space left on device" but df shows space available:**
```bash
# Case A: inode exhaustion
df -i /var     # check inode usage
# If 100%: find and delete many small files
find /var/spool/mqueue -type f | wc -l  # mail queue?
find /tmp -type f | wc -l              # temp files?
# Delete old ones: find /var/spool/mqueue -mtime +7 -delete

# Case B: reserved blocks
df -h /var     # shows 5% reserved even if "full"
# Root reserves blocks for root user only
# As root, you can still write even when df shows 100%
# Non-root processes get ENOSPC
# Fix: reduce reserved blocks on non-root filesystem
tune2fs -m 1 /dev/sdb1   # reduce to 1% (saves ~5% of disk)

# Case C: file being created larger than df says is available
# Solution: find and kill or truncate the growing file
lsof -n | sort -k 7 -rn | head -10  # sort open files by size
```

---

### Related Keywords

**Foundational:**
LNX-007 (FHS), LNX-008 (Files)

**Builds on this:**
LNX-039 (Mounting Filesystems), LNX-054 (LVM)

**Related:**
LNX-025 (find - finding large files), LNX-088 (Disk Performance)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `df -h` | Filesystem usage (human readable) |
| `df -i` | Inode usage |
| `du -sh /path` | Directory total size |
| `du -sh * \| sort -rh \| head` | Largest items here |
| `du -sx /* 2>/dev/null \| sort -rn` | Largest root dirs |
| `lsblk` | List block devices |
| `lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT` | Detailed block info |
| `sudo fdisk -l` | Partition tables |
| `find / -size +500M -type f` | Large files |
| `lsof \| grep deleted` | Deleted open files |

**3 things to remember:**
1. `df -h` shows filesystem space, `df -i` shows inode count - BOTH can be "full"
2. Deleted files still holding space: use `lsof | grep deleted` to find them
3. `du -sh * | sort -rh` narrows down the culprit directory by directory

---

### Transferable Wisdom

The df/du investigation pattern (top-down directory narrowing) is the same
as profiling in software: start at the highest level, find the largest consumer,
drill down. This approach appears in: CPU profiling (flame graphs, top -> narrow),
memory profiling (heap dump analysis), query optimization (EXPLAIN ANALYZE
-> find the slow node), network analysis (total bandwidth -> per-host -> per-flow).
The pattern: measure aggregate, identify the dominant contributor, recurse.

The inode exhaustion problem (resource A looks fine, resource B is exhausted)
is a template for: thread pool exhaustion (CPU fine, but no threads available),
connection pool exhaustion (network fine, but no connections available),
file descriptor exhaustion (disk fine, but `ulimit -n` exceeded). Diagnose
by checking ALL limited resources, not just the obvious one.

---

### The Surprising Truth

The `df` command's output "Use%" column can exceed 100% temporarily. When
a filesystem hits its limit but root's reserved space is being used (by the
root user or system processes), non-root processes get ENOSPC (disk full)
while df shows 101% or more. Additionally: on some cloud storage systems,
thin provisioning means the ADVERTISED capacity is much larger than the actual
physical capacity - multiple VMs share the same physical disk expecting
not everyone will actually use their full allocation. This is the storage
equivalent of airline overbooking. When all VMs fill up simultaneously:
the cloud storage tier fails, often catastrophically and simultaneously for
all VMs sharing that pool. Understanding the difference between provisioned
capacity and physical capacity is critical for cloud storage planning.

---

### Mastery Checklist

- [ ] Can identify disk usage by filesystem with df -h
- [ ] Can narrow down disk usage by directory with du -sh
- [ ] Can identify inode exhaustion with df -i
- [ ] Can list block devices and their mount points with lsblk
- [ ] Can find deleted files still holding space with lsof | grep deleted

---

### Think About This

1. `df -h /var` shows 95% used. You run `du -sh /var/*` and get a total
   that is only 40% of the filesystem size. Where is the rest of the space?
   List three possible explanations for why df and du would differ by this
   much.

2. Your application writes a 10MB file, then deletes it, repeatedly in
   a loop. After 1 hour, `df -h` shows the filesystem nearly full but
   there are no large files visible. `du -sh /*` doesn't account for the
   missing space. What is causing this, and how do you diagnose and fix it?

3. A new server has `/dev/sda` (the OS disk) and `/dev/sdb` (a 1TB data
   disk). `lsblk` shows `/dev/sdb` but `df -h` does not show it. What
   steps do you need to take to make this 1TB disk available at `/data`,
   and how do you ensure it's automatically mounted after a reboot?

---

### Interview Deep-Dive

**Foundational:**
Q: A server disk is 95% full and you need to find what's taking up space. Walk me through the investigation.
A: Systematic top-down investigation: (1) `df -h` - identify WHICH filesystem is full (it could be `/var` not `/` even if the alert says "disk full"). (2) If `/var`: `du -sh /var/* 2>/dev/null | sort -rh | head -10` - find the largest directories. (3) Drill into the largest: e.g., `/var/log` is biggest -> `du -sh /var/log/* | sort -rh | head`. (4) Find the actual large files: `ls -lhS /var/log/myapp | head` or `find /var -type f -size +100M -ls 2>/dev/null`. (5) Check for deleted-but-open files: `lsof | grep deleted | sort -k 7 -rn | head`. These won't show in du. (6) Check inodes: `df -i` - you might have space but no inodes (millions of tiny files). (7) Quick recovery: truncate active log files (`> /var/log/myapp/app.log`), delete old archived logs (`find /var/log -name "*.gz" -mtime +7 -delete`), clean package cache (`apt clean`), vacuum systemd journal (`journalctl --vacuum-size=500M`).

**Intermediate:**
Q: What is the difference between df and du, and why might they report very different numbers?
A: `df` queries the filesystem kernel structure directly - it reports how many blocks the filesystem considers used vs available. `du` walks the directory tree and sums file sizes it encounters. They differ because: (1) Deleted but open files: if a process has a file open and another process deletes it (removes the directory entry), `du` doesn't see it (no directory entry), but `df` counts the blocks as used (the kernel keeps the file alive until all FDs are closed). Common cause of "disk full but du doesn't show it" - fix with `lsof | grep deleted`. (2) Reserved blocks: ext4 reserves 5% of blocks for root. This space is counted as "used" by df (taken from Available, not actually in Use%), but du won't see it as any file's space. (3) Filesystem metadata: journal, lost+found, superblock - overhead counted by df, invisible to du. (4) Sparse files: a file with holes (sparse) has a large logical size (what du reports) but fewer actual data blocks (what df counts). (5) Hard links: du counts hard-linked files once, but df counts the blocks once regardless. The gap is a diagnostic clue: if `df - du` is large, investigate deleted-open files first.

**Expert:**
Q: A server's `/var` filesystem is completely full. The critical service is down because it can't write temp files. You cannot restart the service (it's a stateful process that must not be interrupted). What are your options?
A: Options in order of impact and safety: (1) Truncate large active log files (safest): `> /var/log/myapp/app.log`. This empties the file without removing it - processes with the file open can continue writing. Frees space immediately without touching running processes. (2) Find and kill processes with deleted-open files: `lsof | grep deleted | awk '{print $2}' | sort -u`. Killing these processes closes their file descriptors and frees the space. This impacts those processes but not the critical service. (3) Free space on other filesystems and bind-mount: if `/tmp` is on a separate filesystem with space, bind-mount it to provide temporary space. `mount --bind /data/tmp /var/cache/myapp/tmp`. (4) Extend the filesystem without downtime (LVM): `lvextend -L +5G /dev/mapper/vg-var && resize2fs /dev/mapper/vg-var`. Requires LVM setup. Zero downtime, filesystem grows while mounted. (5) Add a bind mount from another location: if `/mnt/extra` has space, create a directory there and bind mount it to the specific subdirectory that's filling up. (6) Delete package cache: `apt clean` or `yum clean all` - safe, reclaimable space. (7) Vacuum journal: `journalctl --vacuum-size=200M`. For the root cause: ensure log rotation is configured (`logrotate`), implement log-level controls (production should be WARN or ERROR, not DEBUG/TRACE), set up disk usage monitoring alerts at 80% to act before emergencies.
