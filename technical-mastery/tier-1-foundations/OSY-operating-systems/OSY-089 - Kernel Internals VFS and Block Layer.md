---
id: OSY-089
title: Kernel Internals VFS and Block Layer
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-005, OSY-006, OSY-016, OSY-017
used_by: []
related: OSY-088, OSY-090, OSY-096
tags:
  - VFS
  - block-layer
  - kernel
  - filesystem
  - I/O-stack
  - internals
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 89
permalink: /technical-mastery/osy/kernel-internals-vfs/
---

## TL;DR

The Linux I/O stack: application syscall (read/write) ->
VFS (virtual filesystem abstraction) -> specific filesystem
(ext4, btrfs) -> page cache -> block layer -> I/O scheduler
-> device driver -> hardware. Understanding each layer
explains latency sources: cache hits, filesystem journal
writes, I/O queue depth, and NVMe-specific tuning.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-089 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | VFS, block layer, page cache, I/O stack, filesystem |
| **Prerequisites** | OSY-005, OSY-006, OSY-016, OSY-017 |

---

### The Linux I/O Stack

```
Application: read(fd, buf, n)
      |
      v
VFS (Virtual Filesystem Switch)
  - Unified interface: dentry cache, inode cache
  - Dispatches to specific filesystem
      |
      v
Filesystem (ext4, btrfs, xfs, tmpfs, overlay...)
  - Translates file offsets to block numbers
  - Manages metadata (inodes, directories, extents)
  - Journal/WAL (ext4 journal, btrfs CoW log)
      |
      v
Page Cache (Linux buffer cache)
  - 4KB pages; file data cached in kernel memory
  - read(): if page present -> copy to user space (no disk I/O)
  - write(): write to page cache (dirty); async flush to disk
  - cat /proc/meminfo | grep -E 'Cached|Buffers'
      |
      v (cache miss)
Block Layer
  - BIO (Block I/O): merges/sorts requests by block number
  - I/O scheduler:
      CFQ (HDD): round-robin fairness per process
      deadline (HDD/SSD): latency guarantees
      mq-deadline (multiqueue): NVMe-aware
      none (NVMe, io_uring): no scheduling needed
      bfq (desktop): bandwidth fairness
      |
      v
Device Driver
  - SCSI, SATA, NVMe driver
  - NVMe: 64K submission queues (parallel hardware queues)
  - SATA: 1 queue, 32 commands
      |
      v
Hardware (SSD, HDD, NVMe)
  - NVMe: 100 microsecond latency, millions IOPS
  - SATA SSD: 200 microsecond latency, 100K IOPS
  - HDD: 10ms latency, 200 IOPS
```

---

### VFS Layer: Key Data Structures

```
VFS provides a common interface across all filesystems.
Three core objects:
  
  1. inode (index node):
     - Represents a file (not the name; just the data)
     - Contains: file size, permissions, timestamps, block locations
     - Does NOT contain the filename
     - struct inode: 648 bytes in kernel
     - inode cache: hot inodes kept in kernel memory
     
  2. dentry (directory entry):
     - Maps filename -> inode number
     - Cached in dentry cache (dcache)
     - Path resolution: /var/log/app.log
       Walks: / (root dentry) -> var (dentry) -> log (dentry) -> app.log
     - dcache hit: ~100 nanoseconds; miss: filesystem lookup
     
  3. file (open file descriptor):
     - Per-open-file state: position, flags, f_op (operations)
     - Points to: dentry, inode
     - fd in user space -> file struct in kernel
     
  Path walk (stat("/etc/passwd")):
    1. Start from / or CWD (cached dentry)
    2. Lookup "etc" in dcache; if miss: read directory inode
    3. Lookup "passwd" in dcache; if miss: read etc directory
    4. Return inode metadata (stat struct to user)
    With warm dcache: no disk I/O; just memory traversal
    
  VFS operations (function pointers in inode->i_op):
    lookup, create, unlink, mkdir, symlink, rename, ...
    Each filesystem implements these; VFS calls them uniformly
```

---

### Page Cache Internals

```
Page cache = kernel's disk read/write buffer

For read(fd, buf, n):
  1. VFS calls filesystem's read() implementation
  2. Filesystem checks page cache for required blocks
  3. Cache hit:
     - Copy page to user buffer (zero_copy possible with mmap)
     - Returns immediately
  4. Cache miss:
     - Submits bio (Block I/O) to block layer
     - Caller blocks (or returns EAGAIN for O_NONBLOCK)
     - I/O completes: page added to cache
     - Data copied to user buffer
     
For write(fd, buf, n):
  1. Writes to page cache immediately (dirty page)
  2. Returns to application (no disk I/O)
  3. Background: pdflush/writeback threads flush dirty pages
  4. Flush policy: vm.dirty_ratio, vm.dirty_background_ratio
     vm.dirty_ratio = 20 (flush when 20% of RAM is dirty)
     vm.dirty_background_ratio = 10 (background flush at 10%)
     
  fsync(fd): flush specific file's dirty pages to disk
  sync(): flush all dirty pages
  
  Cache eviction:
    LRU (Least Recently Used) approximation
    Two lists: active (recently accessed), inactive (candidate eviction)
    OOM pressure: inactive pages evicted first
    mmap pages: same eviction as regular page cache
    
  Direct I/O (O_DIRECT):
    Bypasses page cache entirely
    Reads/writes go directly to hardware
    Used by: databases (own cache), backup tools
    Requirement: buffer must be aligned to 512B or 4KB (device sector size)
    
  mmap and page cache:
    mmap(fd): maps file pages into virtual address space
    Access to mmap'd memory = access to page cache pages
    Benefits: no copy between kernel and user space
    Benefits: multiple processes can share same file pages
    Kafka consumer: reads log segments via page cache;
      producer writes are in cache; consumer reads often cache-hot
```

---

### I/O Scheduler and Block Layer

```
I/O scheduler sits between filesystem layer and device driver.
Purpose: optimize request order for device characteristics.
  
  HDD (spinning disk):
    Seek time: 5-10ms; sequential I/O: 100MB/s
    Best scheduler: deadline or mq-deadline
    Merges nearby block requests (reduces seeks)
    Sorts by sector number (elevator algorithm)
    
  SATA SSD:
    No seek time; uniform random access
    But: still has a single command queue (NCQ: 32 commands)
    Scheduler: mq-deadline with reduced depth
    
  NVMe SSD:
    Multiple parallel hardware queues (64K per CPU)
    No need for software scheduling
    Scheduler: none (or mq-deadline for QoS)
    Direct submission to hardware queues
    
  Viewing and changing scheduler:
    cat /sys/block/sda/queue/scheduler
    echo mq-deadline > /sys/block/nvme0n1/queue/scheduler
    echo none > /sys/block/nvme0n1/queue/scheduler
    
  Queue depth:
    /sys/block/nvme0n1/queue/nr_requests (default: 128)
    For NVMe: increasing to 1024+ improves IOPS under load
    iostat: if util near 100% but qdepth low: increase nr_requests
    
  BIO (Block I/O Request):
    BIO merging: two adjacent writes -> one BIO request
    Improves throughput; may increase latency (wait for merge window)
    cfq.back_seek_max, cfq.slice_idle: legacy CFQ tuning
    For NVMe none scheduler: no merging; submit immediately
```

---

### Failure Mode: I/O Wait

```
Symptom: top shows wa (iowait) > 20%; application latency spikes
  
  Diagnosis:
    iostat -xz 1
    Look at: await (avg I/O latency), util (device utilization)
    util 100%: device saturated
    await >> svctm: large queue; I/O requests wait in queue
    
    iotop: per-process I/O usage
    iotop -o: show only processes doing I/O
    
  Causes:
    1. Random reads from cold page cache (large working set)
       Fix: increase RAM for page cache, add read-ahead
       echo 256 > /sys/block/sda/queue/read_ahead_kb
       
    2. Lots of dirty page flushing
       Watch: cat /proc/meminfo | grep Dirty
       Fix: lower vm.dirty_ratio; increase flush frequency
       
    3. Journal writes (ext4 journaled data mode)
       Fix: change to data=ordered or data=writeback mode
       
    4. Synchronous writes (fsync per transaction)
       Postgres: commit_delay, synchronous_commit=off (analytics only)
       MySQL: innodb_flush_log_at_trx_commit=2 (durability trade-off)
       
    5. I/O scheduler wrong for device type
       NVMe with CFQ scheduler: CPU overhead, no benefit
       Fix: switch to none scheduler for NVMe
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "write() immediately writes to disk" | write() writes to page cache (dirty page). The OS flushes dirty pages to disk asynchronously via pdflush/writeback threads. To guarantee disk persistence: call fsync() after write(). Without fsync(), a crash after write() can lose data. |
| "O_DIRECT is faster than buffered I/O" | O_DIRECT eliminates the page cache copy - useful when you have your own cache (databases). But for workloads where the same data is read multiple times, buffered I/O (page cache) is significantly faster because repeated reads hit cache. O_DIRECT forces every read to go to hardware. |
| "NVMe doesn't need an I/O scheduler" | NVMe doesn't need an ELEVATOR scheduler (no seek optimization). But `mq-deadline` can still provide request latency guarantees (deadlines) under very high IOPS. For pure throughput: `none`. For latency guarantees: `mq-deadline`. |

---

### Quick Reference Card

| Layer | Key Concept | Tuning |
|-------|-------------|--------|
| VFS | dentry cache, inode cache | RAM (caches auto-grow) |
| Page cache | all file I/O buffered here | `vm.dirty_ratio`; `drop_caches` |
| Filesystem | journal mode | `data=ordered` vs `data=writeback` |
| Block layer | I/O scheduler | `echo none > /sys/block/nvme0/queue/scheduler` |
| Device | queue depth | `/sys/block/nvme0/queue/nr_requests` |
| Diagnosis | `iostat -xz 1` | `util`, `await`, `svctm` |
