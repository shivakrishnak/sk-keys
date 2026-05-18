---
id: LNX-088
title: "Linux Disk Performance (fio, blktrace, I/O tuning)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-022, LNX-035
used_by: LNX-093, LNX-102
related: LNX-086, LNX-083, LNX-093, LNX-087
tags: [fio, blktrace, iostat, iops, throughput, io-scheduler, read-ahead, io-tuning, nvme, rotational, io-depth, block-size, direct-io, buffered-io, io-latency, blkparse, btt, hdparm, io-queue]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 88
permalink: /technical-mastery/lnx/linux-disk-performance/
---

## TL;DR

Linux disk performance: **fio** (Flexible I/O Tester) benchmarks storage with
configurable workload patterns (random/sequential read/write, block size,
queue depth). Key fio parameters: `iodepth` (outstanding I/Os), `bs` (block
size), `rw` (randread/randrw/read/write), `direct=1` (bypass page cache),
`numjobs` (parallel jobs). **iostat -x 1** monitors real-time disk stats:
`await` (average I/O latency ms), `util` (% of time device busy), `r/s`/`w/s`
(IOPS). **blktrace/blkparse/btt** traces block I/O at kernel level for deep
diagnosis. I/O scheduler: `none` for NVMe (NVMe has own queue management),
`mq-deadline` for HDDs. Read-ahead: `blockdev --setra 256 /dev/nvme0n1`
(128KB read-ahead). Key metric: NVMe random read at 4KB blocks should achieve
800K+ IOPS; if much lower, check queue depth and scheduler.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-088 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | fio, iostat, blktrace, IOPS, throughput, I/O scheduler, NVMe, direct I/O, block size, await |
| **Prerequisites** | LNX-022 (Storage and filesystems), LNX-035 (Memory management) |

---

### The Problem This Solves

**Problem 1**: A database server claims its storage handles 200K IOPS (per
vendor spec). But in production: only 50K IOPS achieved, with 4ms latency
instead of 100 microseconds expected from NVMe. Without measurement: assume
the hardware is defective. With fio: `fio --name=randread --bs=4k --rw=randread
--iodepth=1 --direct=1 --numjobs=1 --filename=/dev/nvme0n1 --size=10G
--runtime=60`. Result: 50K IOPS at 20 microsecond latency. With iodepth=32:
800K IOPS at 40 microsecond average. Root cause: database was using iodepth=1
(synchronous I/O), never queuing more than one I/O to the NVMe - wasting
its queue parallelism.

**Problem 2**: A storage system shows 100% util in iostat but `r/s + w/s`
is only 200 IOPS (should handle 50K). `blktrace` reveals: 90% of time is
spent in the I/O scheduler queue, not device service time. The I/O scheduler
is `cfq` (deadline-based) on NVMe - unnecessary overhead. Setting scheduler
to `none` (passthrough): utilization drops to 40%, IOPS jump to 50K.

---

### Textbook Definition

**Storage performance dimensions:**
| Metric | Unit | Workload sensitive |
|--------|------|-------------------|
| IOPS | operations/second | Block size, queue depth, random vs sequential |
| Throughput | MB/s | Block size (larger = more MB/s per operation) |
| Latency | ms or us | Queue depth (lower depth = lower latency) |
| Utilization | % | All of the above |

**I/O workload characteristics:**
- **Sequential I/O**: reading/writing consecutive blocks (large streaming reads, log writes). HDD performs well (seek amortized). NVMe excellent.
- **Random I/O**: reading/writing scattered blocks (database index lookups). HDD terrible (7200 RPM = ~120 IOPS max). NVMe excellent (800K+ IOPS).
- **Direct I/O (`O_DIRECT`)**: bypasses page cache; writes go directly to device. Used by databases.
- **Buffered I/O**: uses page cache; writes return after hitting page cache (later flushed to disk by kernel).
- **Queue depth (iodepth)**: how many I/Os outstanding simultaneously. NVMe benefits enormously from depth (parallelism). Spinning disk benefits slightly.

**Key tools:**
- **fio**: comprehensive I/O benchmarking tool (flexible workload patterns)
- **iostat**: monitor disk I/O statistics (part of sysstat)
- **blktrace/blkparse/btt**: kernel-level block I/O tracing
- **hdparm**: simple benchmark and NIC/drive settings
- **iotop**: per-process I/O monitoring
- **`/sys/block/<dev>/queue/`**: kernel block device queue parameters

---

### Understand It in 30 Seconds

```bash
# === fio benchmarks ===

# Random read IOPS (4KB blocks, queue depth 32, direct I/O):
fio --name=randread_iops \
    --filename=/dev/nvme0n1 \
    --bs=4k \              # 4KB block size
    --rw=randread \        # random reads
    --iodepth=32 \         # 32 outstanding I/Os
    --direct=1 \           # bypass page cache (test real device)
    --ioengine=libaio \    # Linux async I/O
    --numjobs=4 \          # 4 parallel threads
    --size=10G \           # 10GB test file
    --runtime=60 \         # run for 60 seconds
    --time_based \
    --group_reporting

# Output:
# randread_iops: (g=0): rw=randread, bs=(R) 4096B...
#   read: IOPS=812k, BW=3174MiB/s (3329MB/s)
#   lat (usec): min=45, max=4567, avg=157.23, stdev=89.12
#   cpu: usr=8.23%, sys=43.21%, ...

# Sequential read throughput (1MB blocks):
fio --name=seqread_bw \
    --filename=/dev/nvme0n1 \
    --bs=1m \
    --rw=read \
    --iodepth=8 \
    --direct=1 \
    --ioengine=libaio \
    --numjobs=1 \
    --size=10G \
    --runtime=60 \
    --time_based \
    --group_reporting

# Write IOPS (random, 4KB):
fio --name=randwrite_iops \
    --filename=/dev/nvme0n1 \
    --bs=4k \
    --rw=randwrite \
    --iodepth=32 \
    --direct=1 \
    --ioengine=libaio \
    --numjobs=4 \
    --size=10G \
    --runtime=60 \
    --time_based \
    --group_reporting

# Latency at low queue depth (single I/O at a time):
fio --name=latency_test \
    --filename=/dev/nvme0n1 \
    --bs=4k \
    --rw=randread \
    --iodepth=1 \          # single outstanding I/O
    --direct=1 \
    --ioengine=sync \      # sync I/O (not async)
    --numjobs=1 \
    --size=10G \
    --runtime=30 \
    --time_based \
    --group_reporting
# lat (usec): avg=100  <- ~100us at iodepth=1 for NVMe

# === iostat monitoring ===

# Extended stats, 1-second interval:
iostat -x 1
# Device  r/s   w/s  rMB/s  wMB/s   await   svctm   %util
# nvme0n1 12345  234 48.2   0.9     0.25    0.24    98.2
#          IOPS         BW     avg-lat  svc-lat  busy-percent

# Key fields:
# r/s, w/s: read/write IOPS
# rMB/s, wMB/s: read/write throughput
# await: average I/O wait time (ms) - includes queuing time
#   < 1ms: excellent (NVMe)
#   1-10ms: good (modern SSD)
#   > 100ms: slow (HDD or problem)
# svctm: service time at device (deprecated, not reliable in kernel 4+)
# %util: % of time device is busy (100% = saturated, but NVMe can still queue)

# Monitor with header:
iostat -xh 5   # every 5 seconds with human-readable

# === I/O scheduler ===

# Check current scheduler for each device:
cat /sys/block/nvme0n1/queue/scheduler
# [none] mq-deadline  <- 'none' selected (for NVMe)

cat /sys/block/sda/queue/scheduler
# mq-deadline [bfq] none  <- 'bfq' selected (for HDD)

# Change scheduler:
echo none > /sys/block/nvme0n1/queue/scheduler    # NVMe: use none
echo mq-deadline > /sys/block/sda/queue/scheduler  # HDD: use deadline

# Persistent scheduler via udev rule:
cat > /etc/udev/rules.d/60-io-scheduler.rules << 'EOF'
# NVMe: no scheduler (hardware queue)
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="none"
# SATA SSD: mq-deadline
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="0", \
    ATTR{queue/scheduler}="mq-deadline"
# HDD (rotational): bfq for fairness
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", \
    ATTR{queue/scheduler}="bfq"
EOF
udevadm control --reload-rules

# === Queue depth and read-ahead ===
# Queue depth (how many I/Os the kernel will queue):
cat /sys/block/nvme0n1/queue/nr_requests
# 64  <- kernel queue depth

# Read-ahead (how much kernel pre-reads for sequential I/O):
cat /sys/block/nvme0n1/queue/read_ahead_kb
# 128  <- 128KB read-ahead

# Change read-ahead:
blockdev --setra 512 /dev/nvme0n1    # 256KB (setra is in 512-byte units)
# OR:
echo 256 > /sys/block/nvme0n1/queue/read_ahead_kb

# For random I/O workload: reduce read-ahead (wasteful pre-reading):
echo 0 > /sys/block/nvme0n1/queue/read_ahead_kb

# Check if device is rotational:
cat /sys/block/nvme0n1/queue/rotational
# 0  <- SSD/NVMe
cat /sys/block/sda/queue/rotational
# 1  <- spinning disk

# === blktrace: deep I/O tracing ===
# Trace block I/O on device for 10 seconds:
blktrace -d /dev/nvme0n1 -w 10 -o trace

# Parse trace:
blkparse trace.blktrace.0 -o trace.txt

# Extract summary stats with btt:
blkparse -i trace.blktrace.0 -d trace.bin
btt -i trace.bin -l lat_summary
cat lat_summary.{D2C,Q2C}   # D2C: device service time, Q2C: queue time

# Quick summary from blkparse:
blkparse trace.blktrace.0 | tail -20
# Throughput:  Read: 3178.9MiB/s  Write: 0.0MiB/s
# Read: 812456 IOPS at 4.0KB avg size

# === hdparm quick test ===
# WARNING: Only a rough indicator, not for tuning decisions:
hdparm -Tt /dev/nvme0n1
#  Timing cached reads:   35244 MB in  2.00 seconds = 17622.00 MB/sec
#  Timing buffered disk reads: 7234 MB in  3.00 seconds = 2411.33 MB/sec
# (cached = RAM, buffered = actual disk read, no prior cache)
```

---

### First Principles

**Storage performance physics:**
```
NVMe vs HDD - fundamentally different physics:

Spinning Hard Disk (7200 RPM HDD):
  Read request for random 4KB block:
    1. Seek time: move arm to correct track
       Average seek: disk spins 0.5 rotation = 4.17ms
       Modern HDD: 5-10ms average seek
    2. Rotational latency: wait for correct sector to pass under head
       7200 RPM = 120 rotations/second
       Average rotational latency = 0.5 rotation = 4.17ms
    3. Transfer time: 4KB at 200MB/s = 0.02ms (negligible)
    
    Total: ~9ms per random 4KB read
    Max IOPS = 1000ms / 9ms = ~111 IOPS
    
    Sequential: amortize seek across large blocks
    1MB sequential: seek(9ms) + transfer(1MB @ 200MB/s = 5ms) = 14ms
    But 9ms is fixed cost for small blocks:
    1MB sequential throughput: 100MB/s+ (many IOPS * large blocks)

NVMe SSD (PCIe 4.0 NVMe):
  No mechanical movement: electronic switching
  Random 4KB: ~30-100 microseconds (0.03-0.1ms)
  Max random IOPS: 800,000-1,000,000+
  Sequential throughput: 7GB/s
  
  NVMe queue: supports 65535 queues * 65535 deep each
  Parallelism: NVMe NAND flash has multiple dies/planes
    Multiple I/Os queued -> different flash dies work simultaneously
    iodepth=1: one die at a time -> 100us
    iodepth=32: 32 dies in parallel -> 100us latency, 32x throughput
  
  Relationship: latency * IOPS = queue depth (Little's Law)
    If latency = 100us, iodepth = 32:
    IOPS = iodepth / latency = 32 / 0.0001 = 320,000 IOPS
    At iodepth=1: IOPS = 1 / 0.0001 = 10,000 IOPS

Block size impact:
  4KB random read on NVMe at iodepth=32:
    800K IOPS * 4KB = 3.2GB/s (within NVMe 7GB/s limit)
    Bottleneck: CPU processing overhead per I/O
    
  1MB sequential read on NVMe at iodepth=4:
    Throughput: 7GB/s (bandwidth limited)
    IOPS: 7000 IOPS (7GB/s / 1MB)
    Bottleneck: PCIe bandwidth
  
  Rule: large block size + sequential -> throughput-bound
        small block size + random -> IOPS-bound (CPU or device)
        
Direct I/O vs Buffered I/O:
  Buffered write:
    Application -> page cache (RAM)  [immediate return]
    Kernel -> disk [asynchronous, seconds later]
    Benchmark shows very high IOPS (writing to RAM)
    Not useful for measuring actual device performance!
  
  Direct I/O (O_DIRECT):
    Application -> device directly (no page cache)
    Benchmarks measure actual device performance
    Databases use O_DIRECT: they manage their own buffer cache
    
  ALWAYS use --direct=1 in fio for device benchmarking

I/O scheduler purpose and evolution:
  Old Linux (single queue):
    One hardware queue per device
    Scheduler: reorder I/O requests to minimize HDD seeks
    CFQ: fair queueing (per-process time slices)
    Deadline: prevent starvation with expiry deadlines
  
  Multi-queue (mq) Linux (kernel 3.13+):
    Multiple software queues (one per CPU core)
    Multiple hardware queues (NVMe supports 65535)
    Old schedulers replaced: mq-deadline, bfq, none
  
  For NVMe (none/noop scheduler):
    NVMe has its own internal queue management (hardware)
    Adding software scheduler: ADDS OVERHEAD, no benefit
    None = pass-through, requests go directly to NVMe queues
  
  For HDD (mq-deadline or bfq):
    mq-deadline: deadline-based to prevent starvation
    bfq (Budget Fair Queueing): per-process fairness
    HDD still benefits from request reordering (seek reduction)
```

---

### Thought Experiment

Complete disk performance investigation:

```bash
# Scenario: database reporting slow query response despite "fast" storage

# Step 1: baseline with iostat:
iostat -x 1 10
# Device  r/s  w/s  await %util
# sdb     200  50   45.2  100

# Analysis:
# 200 IOPS reads, 50 IOPS writes
# 45.2ms await: TERRIBLE for an SSD!
# 100% util: saturated
# But 250 IOPS on an SSD that should do 100K+?
# Something is blocking the I/O

# Step 2: check if device is SSD or HDD:
cat /sys/block/sdb/queue/rotational
# 0  <- SSD!
# SSD at 250 IOPS means something else wrong

# Step 3: check I/O scheduler:
cat /sys/block/sdb/queue/scheduler
# [cfq] mq-deadline none  <- CFQ! (old scheduler)
# CFQ is for HDDs, adding unnecessary overhead to SSD

# Switch to mq-deadline or none:
echo mq-deadline > /sys/block/sdb/queue/scheduler

# Step 4: check queue depth:
cat /sys/block/sdb/queue/nr_requests
# 4  <- queue depth only 4! 

# Increase queue depth:
echo 64 > /sys/block/sdb/queue/nr_requests

# Re-check iostat:
iostat -x 1 10
# Device   r/s    w/s  await %util
# sdb    12345    567    2.1  78
# Now: 12K IOPS, 2ms await, 78% util -> much better!

# Step 5: fio to find the true limit:
fio --name=db_random \
    --filename=/dev/sdb \
    --bs=4k \
    --rw=randread \
    --iodepth=32 \
    --direct=1 \
    --ioengine=libaio \
    --numjobs=4 \
    --size=10G \
    --runtime=60 \
    --time_based
# read: IOPS=89.5k, BW=350MiB/s
# lat (usec): avg=1435.12  <- 1.4ms at 32 depth

# Step 6: database application uses iodepth=1 (synchronous reads)?
# Check with blktrace:
blktrace -d /dev/sdb -w 30 -o db_trace
blkparse db_trace.blktrace.0 | grep -E "^[0-9]" | \
    awk '{print $7}' | sort | uniq -c | sort -rn | head -10
# 28765 R   <- Read requests
# Check queue depth in blktrace data:
btt -i db_trace.bin 2>&1 | grep "Q2C"
# Q2C: average wait from queue to complete = 42ms -> queue long!

# Step 7: root cause - database connection pool too small:
# 100 database threads, each doing synchronous I/O
# But db_pool_size=5: only 5 connections, only 5 concurrent I/Os
# Increase pool size -> more concurrent I/Os -> NVMe parallelism used
```

---

### Mental Model / Analogy

```
Disk I/O = restaurant kitchen analogy

Spinning disk = manual kitchen (1 chef):
  Chef must walk to ingredient shelf (seek time ~9ms)
  Walk back, cook, plate, deliver
  Max: ~110 "dishes" per second
  Sequential: prep all similar dishes at once (bulk cooking)
  Random: walk back and forth constantly (terrible efficiency)

NVMe SSD = automated kitchen (100 robot arms):
  Any ingredient retrieved in 0.1ms (no walking needed)
  100 robot arms work simultaneously (queue depth = arms available)
  
  iodepth=1: 1 robot arm working, 99 idle
    Speed: 10,000 dishes/second
  iodepth=32: 32 robot arms working in parallel
    Speed: 320,000 dishes/second (32x throughput!)
  
  The restaurant only benefits from 32 robot arms if you queue
  32 orders simultaneously. If orders come in one at a time:
  back to 10,000 dishes/second

Block size = dish complexity:
  4KB block = simple dish: robot arm takes 100ms
  1MB block = complex meal: robot arm takes 200ms
  But 1MB delivers 256x more data than 4KB!
  
  Throughput = block_size / latency
  4KB at 100us: 4KB / 0.0001s = 40MB/s per arm
  1MB at 200us: 1MB / 0.0002s = 5GB/s per arm (much more efficient!)

Direct I/O = eating at the restaurant:
  Chef cooks -> customer eats immediately
  
Buffered I/O = food delivery with staging area:
  Chef cooks -> food goes to staging area (page cache)
  Benchmark of staging area shows very fast (already hot food)
  But actual restaurant capacity hidden by staging buffer

I/O scheduler = traffic management:
  Old (CFQ): traffic lights at every intersection (adds delay)
    Necessary for HDD (prevents deadlocks, ensures fairness)
    Wasteful for NVMe (hardware manages its own traffic internally)
  
  None (NVMe): highway with on-ramps
    Cars enter highway directly, highway manages merging internally
    Software traffic lights just slow you down

iostat %util = whether chef is idle:
  100% util: chef never idle (bad for HDD = saturated)
  100% util NVMe: NVMe queue never empty (ok - can still add more!)
  NVMe at 100% util with low IOPS: queue depth too shallow
  More diners should be ordering simultaneously (increase iodepth)
```

---

### Gradual Depth - Five Levels

**Level 1:**
IOPS, throughput, latency concepts. `iostat -x 1` basics. Why HDDs are slow
for random I/O (seek time). NVMe vs SATA SSD basics. `hdparm -Tt` rough
benchmark. `iotop` to find disk I/O by process.

**Level 2:**
fio basic usage (bs, rw, iodepth, direct, numjobs). Understanding fio output
(IOPS, BW, latency percentiles). iostat field meanings (await, svctm, util).
I/O scheduler concept. `blockdev --setra` for read-ahead. Direct vs buffered
I/O. Queue depth effect on IOPS.

**Level 3:**
fio job files (.fio files for reproducible tests). Mixed read/write workloads
(randrw, rwmixread). I/O scheduler selection (none for NVMe, mq-deadline for
HDD). blktrace/blkparse/btt for detailed I/O analysis. Little's Law in I/O
(IOPS = queue_depth / latency). `iotop -a` for cumulative I/O. `iolatency`
and `biolatency` (bcc tools). `io_uring` vs libaio vs sync I/O engines in fio.

**Level 4:**
NVMe multi-queue architecture: ns-based queue isolation. io_uring zero-copy
with fixed buffers. SPDK (Storage Performance Development Kit): kernel bypass
for storage. `fio --ioengine=io_uring`. Write barriers and `fdatasync` vs
`fsync`. Database O_DIRECT patterns. `F_NOCACHE` on macOS equivalent. Storage
class memory (Optane DCPMM): DAX mode (direct access, bypasses block layer).
RAID configurations and their IOPS implications (RAID 5 write penalty). LVM
striping for parallelism across multiple devices.

**Level 5:**
NVMe over Fabrics (NVMe-oF): extends NVMe protocol over RDMA/TCP for network
storage with NVMe latency. Kernel block layer internals: `struct bio`, `struct
request`, `struct request_queue`. BIO merging (kernel combines adjacent I/O).
`blk-mq` (multi-queue block layer) architecture. Persistent memory (PMEM)
programming model: `ndctl`, `daxctl`, DAX (Direct Access) filesystem (ext4/xfs
with `-o dax`). Write amplification factor (WAF) in SSDs: how filesystem
write patterns affect SSD cell wear. Zone Namespace (ZNS) NVMe: host-managed
zone writes for SSD lifespan. Kernel trace events for block layer: `blk_rq_insert`,
`blk_rq_issue`, `blk_rq_complete`.

---

### Code Example

**BAD - benchmarking with buffered I/O:**
```bash
# BAD 1: measuring disk speed using buffered I/O (measures RAM, not disk):
time dd if=/dev/zero of=/tmp/testfile bs=1M count=1024
# 1073741824 bytes (1.1 GB, 1.0 GiB) copied, 0.234 s, 4.6 GB/s
# Wow, 4.6GB/s! ...but this is writing to page cache (RAM)
# Not disk performance at all!

# BAD 2: Single-queue sequential read after cold cache:
time dd if=/tmp/testfile of=/dev/null bs=1M
# 1.1 GB copied in 0.089s = 12 GB/s
# Still measuring page cache (file was cached from step 1)

# GOOD: Proper benchmarking with direct I/O and fio:
# First: drop caches (for testing only! never in production):
echo 3 > /proc/sys/vm/drop_caches

# Correct NVMe benchmark:
fio --name=correct_benchmark \
    --filename=/dev/nvme0n1 \
    --bs=4k \
    --rw=randread \
    --iodepth=32 \       # queue depth matching NVMe capabilities
    --direct=1 \          # bypass page cache - test real device
    --ioengine=libaio \   # async I/O for queue depth > 1
    --numjobs=4 \         # multiple jobs for parallel queues
    --size=10G \
    --runtime=60 \
    --time_based \
    --group_reporting

# Results:
# read: IOPS=812k, BW=3174MiB/s
# lat (usec): p50=152 p99=289 p999=512  <- real NVMe performance
```

**GOOD - fio job file for realistic database workload:**
```ini
# database_workload.fio - simulates OLTP database I/O pattern
[global]
ioengine=libaio
direct=1           ; O_DIRECT - bypass page cache
buffered=0
bs=4k              ; database page size
iodepth=32         ; NVMe sweet spot
runtime=120        ; 2 minutes
time_based=1
group_reporting=1

[randomread]
filename=/dev/nvme0n1
rw=randread
numjobs=4          ; 4 reader threads
size=50G           ; 50GB working set

[randomwrite]
filename=/dev/nvme0n1
rw=randwrite
numjobs=2          ; 2 writer threads (writes are fewer in OLTP)
size=50G
fdatasync=1        ; fsync after each write (durability check)
```

```bash
# Run database workload benchmark:
fio database_workload.fio

# Output analysis:
# randomread: IOPS=245k, BW=957MiB/s
#   lat (usec): p50=102, p99=245, p999=1234
# randomwrite: IOPS=45k, BW=175MiB/s  <- lower due to fdatasync overhead
#   lat (usec): p50=234, p99=1205, p999=4567  <- much higher due to fsync

# Key insight: fdatasync forces journal commit each time
# Database write IOPS is limited by sync latency, not device IOPS
# For PostgreSQL: check fsync_interval and wal_sync_method

# iostat during fio run:
iostat -x 1 | grep nvme0n1
# nvme0n1 245123 45234  957.3  175.6  0.34  100.0
#         r/s    w/s    rMB/s  wMB/s  await util
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "iostat %util=100% means the device is at maximum capacity" | `%util` means the device was busy (processing I/Os) 100% of the sample time. For HDDs: 100% util IS meaningful saturation (one head, one queue). For NVMe/SSDs: 100% util with many queues does NOT mean saturated. NVMe handles 65K queues of 65K depth. You can have 100% util at 50K IOPS on a device capable of 800K IOPS - the device is simply always busy (never idle) but has much more capacity. To determine saturation on NVMe: look at IOPS vs theoretical max and latency trends. If latency is increasing with load: saturated. `await` is a better saturation indicator than `%util` for SSDs. If `await` exceeds expected device latency (> 2ms for NVMe): likely saturated or scheduler causing queuing. |
| "Larger block size always means better throughput" | Larger block size improves throughput for SEQUENTIAL I/O where you're bandwidth-limited. For RANDOM I/O, the story is different: (1) Random 4KB vs 1MB on NVMe: at iodepth=32, 4KB achieves 3.2GB/s while 1MB achieves 7GB/s - 1MB is better. But at iodepth=1: 4KB=40MB/s, 1MB=5GB/s. For random access patterns with small block size: increase iodepth for throughput. (2) For database workloads: block size must match the database page size (typically 4KB, 8KB, 16KB). Mismatched block size causes write amplification (writing 4KB to an 8KB page = 8KB write). Always match fio block size to application's actual I/O pattern. |
| "More queue depth always improves performance" | Queue depth (iodepth in fio) controls NVMe parallelism: more depth = more concurrent I/Os = higher IOPS/throughput (up to a point). HOWEVER: latency INCREASES with queue depth (more requests queued = each request waits longer). This is Little's Law: latency = queue_depth / IOPS. At iodepth=1: 10K IOPS, 100us latency. At iodepth=32: 320K IOPS, 3.2ms latency. For latency-sensitive workloads (HFT, real-time databases): low iodepth (1-4) is better even though IOPS are lower. For throughput-sensitive workloads (backup, sequential scan): high iodepth (32-128) is better. The right queue depth depends on the application's latency requirement, not just IOPS target. |
| "fio tests on a file are as accurate as raw device tests" | Tests on a filesystem file add filesystem overhead: metadata updates, journaling, directory entry reads, VFS layer. `fio --filename=/dev/nvme0n1` (raw device) tests the actual storage hardware. `fio --filename=/data/testfile` tests filesystem + hardware. For hardware characterization: use raw device. For application validation: use filesystem (matches real workload). Also: filesystem tests with small random files may show much lower IOPS than device tests due to metadata contention (many files vs. one file). For SQLite/PostgreSQL benchmarking: use filesystem tests in the actual data directory with direct=1 to simulate the database's actual behavior. |

---

### Failure Modes & Diagnosis

**Disk performance diagnosis:**
```bash
# === Failure: application reports "slow disk" ===

# Step 1: Live monitoring:
iostat -x 1 60
# Device    r/s    w/s  await  %util
# sda        50  1200  125.3   99
# await=125ms for SSD! -> scheduler or queue depth issue

# Step 2: Check scheduler:
cat /sys/block/sda/queue/scheduler
# [cfq] mq-deadline  <- cfq on an SSD!
echo mq-deadline > /sys/block/sda/queue/scheduler
# Re-check: if await drops to < 5ms -> scheduler was the issue

# Step 3: Check if writes are dominating (1200 w/s):
# High write rate: might be dirty page writeback storm
cat /proc/meminfo | grep -E "Dirty|Writeback"
# Dirty:     52428800 kB  <- 50GB! dirty page storm
# Fix: reduce vm.dirty_ratio (see LNX-086)

# Step 4: Find which process is doing the I/O:
iotop -o  # show only active I/O processes
# 2345 python    D  0.00 B/s  1.23 GB/s  99.99 % /usr/bin/python3 backup.py
# ^ backup script doing 1.23GB/s writes -> competing with production!

# Step 5: Blktrace for request-level analysis:
blktrace -d /dev/sda -w 30 -o analysis
blkparse analysis.blktrace.0 | awk '{print $7}' | \
    sort | uniq -c | sort -rn
# 89765 W    <- mostly writes
# 1234  R    <- few reads

# Check D2C times (device service times) with btt:
blkparse -i analysis.blktrace.0 -d analysis.bin
btt -i analysis.bin 2>&1 | grep "D2C"
# D2C   |  0.000341  |  0.003456  <- avg D2C: 0.34ms, max 3.5ms
# (D2C is device service time, excludes queue wait)
# If D2C >> spec: device hardware issue (failing drive?)

# Step 6: Check disk error log:
dmesg | grep -i "error\|I/O error\|sector"
# [12345.678] sd 0:0:0:0: [sda] tag#1 FAILED Result: hostbyte=DID_OK
# Hardware errors! Replace drive.

# Step 7: Measure raw device performance to confirm hardware:
fio --name=verify \
    --filename=/dev/sda \
    --bs=4k --rw=randread \
    --iodepth=32 --direct=1 \
    --ioengine=libaio \
    --numjobs=1 --size=1G \
    --runtime=30 --time_based
# If IOPS << vendor spec: hardware failing or misconfigured
```

---

### Related Keywords

**Foundational:**
LNX-022 (Storage and filesystems), LNX-035 (Memory management)

**Builds on this:**
LNX-093 (Performance troubleshooting), LNX-102 (Storage architecture)

**Related:**
LNX-086 (sysctl dirty page tuning), LNX-087 (Tracing tools)

---

### Quick Reference Card

| Tool | Use Case |
|------|----------|
| `iostat -x 1` | Live I/O monitoring (IOPS, BW, latency, util) |
| `fio --rw=randread --direct=1 --iodepth=32` | Random read IOPS benchmark |
| `fio --rw=read --bs=1m --direct=1` | Sequential throughput benchmark |
| `iotop -o` | Per-process I/O monitoring |
| `blktrace -d /dev/sda -w 30` | Block I/O tracing |
| `echo none > /sys/block/nvme0n1/queue/scheduler` | Set NVMe scheduler |
| `cat /sys/block/nvme0n1/queue/rotational` | Check if SSD (0) or HDD (1) |

**3 things to remember:**
1. Always use `direct=1` in fio to bypass page cache - otherwise you're benchmarking RAM, not disk
2. For NVMe: set scheduler to `none` (NVMe manages its own queues; software scheduler adds overhead, reduces IOPS)
3. `iostat await` is the key latency metric: < 1ms for NVMe, 1-10ms for SATA SSD, ~10ms for HDD

---

### Transferable Wisdom

The queue depth insight (iodepth in fio, IOPS = queue_depth / latency via
Little's Law) applies to: database connection pools (pool size = queue depth,
more concurrent connections = higher throughput at cost of higher per-query
wait), HTTP connection pools, thread pools (more threads = more concurrent
work = higher throughput but higher context-switch latency). The direct I/O
vs buffered I/O trade-off (speed vs durability, cache bypass vs cache use)
maps to: database write-ahead log (WAL: direct writes for durability), Redis
AOF (append-only file with fsync for durability), Kafka segment writes with
configurable fsync. The I/O scheduler concept (hardware that manages its own
queue needs no software scheduler) appears in: NIC RSS (NIC manages its own
hardware queues, software steering is redundant), GPU compute (GPU has its own
scheduling, OS scheduler doesn't interfere). The fio workload model (configure
block size, queue depth, random vs sequential) is exactly how cloud storage
vendors characterize their offerings (EBS gp3: 16K IOPS at 16KB blocks,
1000MB/s throughput). Understanding fio lets you validate cloud storage claims
and tune application I/O patterns to match storage characteristics.

---

### The Surprising Truth

Most production databases are severely under-utilizing their NVMe storage.
A typical PostgreSQL deployment uses synchronous read I/O (iodepth=1 for each
backend process) because each query blocks waiting for the disk read to complete.
With 50 concurrent queries: effective iodepth=50 distributed across 50 process
contexts. But if only 5 connections are active at once: effective iodepth=5.
An NVMe drive capable of 800K IOPS at iodepth=32 may only deliver 30K-50K
IOPS because the application never queues enough concurrent I/Os. The fix:
`pg_prewarm` to warm the buffer cache, `max_connections` tuning, and connection
pooling (PgBouncer) to increase actual concurrency. Secondly: the `cfq` I/O
scheduler (Completely Fair Queuing) was the default Linux scheduler for over
a decade and remains default on some distros even for NVMe. CFQ adds 50-200
microseconds of software queuing overhead per I/O. On a device with 50us
hardware latency: CFQ doubles it. Switching from CFQ to `none` on NVMe
routinely doubles measured IOPS in benchmark tests. Despite this being well-
documented, cloud VMs and many Linux distributions ship with non-optimal
schedulers for their storage type. First-day production tuning: verify the
scheduler matches your storage type.

---

### Mastery Checklist

- [ ] Can run fio benchmarks with correct parameters for the workload type (random/sequential, block size, direct I/O, queue depth)
- [ ] Can interpret iostat -x output: IOPS, throughput, await latency, and saturation
- [ ] Knows which I/O scheduler to use for NVMe vs HDD and how to change it
- [ ] Understands how queue depth affects IOPS vs latency trade-off (Little's Law)
- [ ] Can use blktrace/blkparse to diagnose I/O patterns at block level

---

### Think About This

1. A cloud-based database reports its NVMe storage at 200K IOPS (vendor spec
   for the instance type). Under actual load: only 15K IOPS measured. Design
   a complete fio investigation: what workload parameters match your database
   pattern (block size, random vs sequential ratio, read vs write ratio), what
   queue depth reveals about how the database issues I/O, and what filesystem
   vs raw device comparison tells you about filesystem overhead. Propose fixes
   for each bottleneck discovered.

2. You're designing the storage configuration for a PostgreSQL server that
   needs: 50K random read IOPS (4KB blocks), 10K write IOPS with durability
   (fsync=on), and 500MB/s sequential scan throughput. You have access to:
   one NVMe drive (800K IOPS, 7GB/s), four SATA SSDs (100K IOPS each, 550MB/s
   each). Compare the options: single NVMe, RAID 0 of 4 SSDs, and RAID 10 of
   4 SSDs. Calculate expected performance for each requirement for each config,
   including RAID write penalty.

3. Explain why a database configured with `synchronous_commit=on` and
   `fsync=on` will have its write performance limited by storage latency rather
   than IOPS. Calculate: for a storage device with 200us fsync latency, what
   is the maximum write transactions per second for a single-threaded commit
   path? How would connection pooling with parallel commit threads affect this?
   What is the IOPS at that transaction rate if each transaction writes 8KB?

---

### Interview Deep-Dive

**Foundational:**
Q: What metrics does iostat show and how do you interpret them to diagnose a disk I/O bottleneck?
A: `iostat -x 1` shows extended per-device statistics every second. KEY METRICS: `r/s`, `w/s`: read and write operations per second (IOPS). Useful for: checking if IOPS are near device spec. `rMB/s`, `wMB/s`: read/write throughput. Useful for: sequential workloads and bandwidth-bound analysis. `await`: average time (ms) from I/O request to completion, including time spent in queue. This is the MOST IMPORTANT latency metric. Expected values: NVMe < 0.5ms, SATA SSD < 1ms, HDD < 10ms. If await exceeds spec: scheduler overhead, device saturation, or hardware issue. `%util`: percentage of time the device had outstanding I/Os. For HDD: 100% = saturated. For NVMe: 100% util can still handle much more (NVMe has multiple internal queues). DIAGNOSIS FLOW: Step 1: Check `%util`. If < 80%: device not saturated, look elsewhere. Step 2: Check `await`. If await >> expected: either device is slow (hardware issue), or software scheduler is adding queue time. Step 3: Check `r/s` + `w/s`. If IOPS << spec: device not being properly utilized (check iodepth in application). Step 4: Check balance of reads vs writes. High writes + high await: might be dirty page writeback storm (check /proc/meminfo Dirty). Step 5: Use `iotop -o` to find which processes are contributing the most I/O. Step 6: Correlate with application behavior: is the app the cause or a background job (backup, compaction)?

**Expert:**
Q: How does NVMe queue architecture differ from SATA SSD, and what implications does this have for Linux I/O scheduler selection and application I/O depth tuning?
A: SATA vs NVMe QUEUE ARCHITECTURE: SATA has one hardware queue of depth 32 (NCQ - Native Command Queuing, SATA 3.0+). All I/O commands from all processes go to this one queue. Linux I/O scheduler sits in front: reorders and coalesces requests before sending to the single hardware queue. BENEFIT of SATA scheduler: reduces HDD seeks (merges nearby requests), ensures fairness across processes (CFQ), prevents starvation (mq-deadline). For SSD: scheduler still adds ~10-50us overhead per I/O by holding requests for merging/reordering. NVMe has up to 65,535 hardware queues, each up to 65,535 deep. Modern Linux: one NVMe queue per CPU core (typically 4-64 queues). All core-local I/O goes to that core's queue: no cross-CPU contention. NVMe drive handles its own internal request scheduling (flash translation layer manages parallelism across NAND dies). I/O SCHEDULER IMPLICATIONS: With NVMe's hardware queuing: software scheduler serves no purpose (NVMe doesn't benefit from merge/reorder - its FTL does this). Software scheduler overhead: 10-200us per I/O. At 100us NVMe latency: scheduler can double perceived latency! Recommendation: `echo none > /sys/block/nvme*/queue/scheduler`. Exception: shared NVMe in cloud VMs where tenants compete for bandwidth - mq-deadline provides some fairness. IODEPTH IMPLICATIONS: SATA (32 queue slots): iodepth > 32 = software-queued (additional overhead). Optimal: iodepth 16-32. NVMe (65K queues): iodepth can be 128+ per queue. Multiple CPU queues * depth 32 = very high parallelism. Application iodepth in fio or libaio: determines concurrency. Via Little's Law: IOPS = iodepth / latency. At 100us latency: iodepth=1 -> 10K IOPS; iodepth=32 -> 320K IOPS; iodepth=128 -> 1.28M IOPS (approaching NVMe limit). For maximum throughput: use libaio ioengine with high iodepth. For minimum latency (trading system, real-time): use iodepth=1, accept lower IOPS.
