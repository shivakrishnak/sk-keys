---
id: OSY-074
title: Journaling File System
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-013, OSY-073
used_by: OSY-089
related: OSY-073, OSY-057, OSY-089
tags:
  - journaling
  - ext4
  - XFS
  - crash-consistency
  - WAL
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 74
permalink: /technical-mastery/osy/journaling-file-system/
---

## TL;DR

Journaling ensures file system consistency after a crash
by writing a "journal entry" (log of intended changes)
before making the actual change. On recovery: replay the
journal (redo) or discard incomplete entries. ext4 uses
ordered journaling by default. XFS: full metadata journal.
The same Write-Ahead Log (WAL) principle used by databases.
Without journaling: fsck after crash can take hours.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-074 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | journaling, ext4, XFS, crash consistency, WAL, fsck |
| **Prerequisites** | OSY-013, OSY-073 |

---

### The Crash Consistency Problem

```
Problem: multi-step disk operation interrupted by power failure
  
  Creating a file requires multiple writes:
    1. Allocate inode (write inode bitmap)
    2. Write inode data
    3. Allocate data block (write data bitmap)
    4. Write directory entry
    5. Write file data
    
  Power failure after step 2 but before step 4:
    Inode exists with data
    Directory entry NOT created
    -> "Orphaned inode" (data allocated but not reachable)
    
  Power failure between step 3 and step 5:
    Directory entry exists, inode exists
    Data blocks allocated but not written
    -> File exists but contains garbage data
    
  Pre-journaling recovery: fsck (file system check)
    Scan entire filesystem to find inconsistencies
    For 1TB filesystem: can take HOURS on boot
    Modern filesystems: too large for fsck-based recovery
    
Journal (WAL for filesystem):
  Write journal entry FIRST (in journal area)
  Then write actual data
  On recovery: check journal; replay or discard
  Journal replay: seconds (not hours)
```

---

### Journal Modes

```
ext4 journal modes:
  
  writeback (fastest, least safe):
    Journal: metadata changes only
    Data: written in arbitrary order (data may not be in journal)
    After crash: metadata consistent, data may be stale
    Risk: data corruption possible (metadata says "file has data"
    but data blocks have old content or zeros)
    Use: low-value data where metadata consistency is enough
    
  ordered (default - ext4):
    Journal: metadata changes only
    Data: written to disk BEFORE metadata committed to journal
    After crash: data is consistent with metadata state
    Risk: very low; only uncommitted writes are lost
    Performance: good balance; most production uses
    
  journal (safest, slowest):
    Journal: BOTH metadata AND data
    Everything written twice: once to journal, once to disk
    After crash: can recover most recently committed data
    Performance: ~50% slower writes vs writeback
    Use: databases with O_DSYNC writes, high-integrity needs
    
XFS:
  Uses journal (log) for metadata only (like ext4 ordered)
  Designed for large files and parallel I/O
  Scales better than ext4 for very large files and many threads
  
Btrfs, ZFS:
  Copy-on-write: never overwrite in place -> always consistent
  No separate journal needed (COW IS the crash consistency mechanism)
```

---

### Connection to Database WAL

```
File system journal = Write-Ahead Log (WAL) principle
  Same concept, different level:
  
  File system journal:
    Journal area on disk (circular buffer)
    Each journal transaction: header + operations + commit
    Recovery: scan journal, re-apply committed transactions
    
  Database WAL (PostgreSQL, MySQL redo log):
    WAL file (append-only log)
    Each WAL entry: change description + LSN (Log Sequence Number)
    Commit = WAL entry durable on disk (fsync)
    Recovery: replay WAL from last checkpoint
    
  Same principle:
    Write the INTENTION (log) before the fact
    Atomically commit the log entry
    Execute actual operation (may fail)
    Recovery: check log, complete or discard
    
Database behavior on ext4 vs XFS:
  Database does its OWN WAL: doesn't rely on filesystem journal
  Uses O_DIRECT to bypass page cache (write directly to disk)
  Uses fdatasync() to ensure WAL is durable
  
  -> For databases: filesystem journal adds overhead without benefit
  -> Databases often use: ext4 without data journal (writeback mode)
     OR XFS (designed for throughput)
     OR directio mounts: mount -o data=writeback,noatime
```

---

### Performance Impact

```bash
# Check current filesystem type and journal mode:
tune2fs -l /dev/sda1 | grep -i "default mount options"
# "Default mount options:    user_xattr acl"
# + data=ordered (if not shown, ordered is default)

# Change journal mode (requires remount or /etc/fstab):
# In /etc/fstab:
# /dev/sda1 / ext4 defaults,data=ordered,noatime 0 1

# noatime: disable access time updates (big performance win)
# - Traditional: every file read updates atime (write!)
# - noatime: skip atime update on read
# - Impact: 20-30% fewer writes for read-heavy workloads
# - Safe for most applications (some use atime for expiry)
# - relatime: compromise (update atime only if older than mtime)

# Monitor journal health:
e2fsck -n /dev/sda1  # dry run check (no changes)
dumpe2fs /dev/sda1 | grep -i journal

# XFS: check journal size
xfs_info /mount/point | grep log
# log     =internal log     bsize=4096   blocks=521728, version=2
# log size: large = more transactions can be inflight

# Benchmark journal modes:
fio --name=sequential-write --rw=write --bs=4k --size=1G \
    --ioengine=sync --filename=/testfile --direct=0
# Run with different mount options to compare throughput
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Journaling guarantees no data loss on power failure" | Journaling guarantees FILE SYSTEM STRUCTURAL CONSISTENCY - inodes, directory entries, bitmaps are consistent. But uncommitted data writes are LOST on power failure (same as without journaling). For true data durability, applications must call fsync() after writes. Journaling prevents corruption; it does not prevent data loss |
| "Databases don't need to worry about filesystem crash consistency because they handle it themselves" | True that databases implement WAL. But: if using direct I/O (O_DIRECT) and proper fsync, the database manages durability correctly regardless of filesystem journal. If using buffered I/O without fsync, even database WAL doesn't protect against filesystem-level corruption caused by page cache ordering issues |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Journaling purpose | Write intent before change -> consistent recovery |
| ext4 default mode | ordered: data before metadata; fast recovery |
| journal mode | Both data + metadata; safest but 50% write overhead |
| fsck pre-journal | Full scan; hours for large filesystems |
| Journal recovery | Seconds: replay only journal area |
| noatime | Skip atime updates; 20-30% fewer writes on read-heavy |
