---
id: OSY-067
title: IO Scheduler CFQ Deadline and mq-deadline
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-013, OSY-065
used_by: OSY-089, OSY-110
related: OSY-013, OSY-068, OSY-110
tags:
  - IO-scheduler
  - CFQ
  - mq-deadline
  - NVMe
  - block-layer
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 67
permalink: /technical-mastery/osy/io-scheduler/
---

## TL;DR

I/O schedulers reorder disk requests to optimize
throughput (elevator algorithm) or minimize latency
(deadline). CFQ (kernel 2.6, deprecated) gave each
process a fair share. mq-deadline (modern default for
HDDs) merges and reorders requests with a deadline.
NVMe drives: use `none` scheduler (no reordering needed;
hardware has its own queue). Wrong scheduler = 5-10x
throughput difference on HDDs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-067 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | I/O scheduler, CFQ, mq-deadline, NVMe, block layer |
| **Prerequisites** | OSY-013, OSY-065 |

---

### Why I/O Scheduling Matters for HDDs

```
Hard Drive seek time:
  Moving disk head to correct track: 5-15ms
  Rotational latency (wait for sector): 2-5ms
  Total: 7-20ms per random I/O
  
  If we process requests in arrival order:
    Request queue: sector 100, 5000, 200, 4800, 150
    Seek path: 100 -> 5000 -> 200 -> 4800 -> 150
    Total seek: huge, back-and-forth across disk
    
  Elevator algorithm (reorder by cylinder/track):
    Sorted: 100 -> 150 -> 200 -> 4800 -> 5000
    Seek: one direction sweep, then reverse
    Result: 3-5x fewer total seek operations
    
  I/O scheduler responsibility:
    Merge adjacent requests (read sector 100+101 together)
    Sort requests to minimize seek
    Ensure no request waits too long (deadline)
    Provide fairness between processes (CFQ)
    
NVMe: no mechanical seek
  NVMe drives: fully random access at same speed as sequential
  Reordering adds overhead with no benefit
  Use: noop or none scheduler (pass requests directly to driver)
  NVMe also: 64K hardware queues vs HDD's 1 queue
```

---

### Scheduler Comparison

```
CFQ (Completely Fair Queuing) - deprecated in kernel 5.0:
  Per-process I/O queues with fair share
  Each process gets equal I/O bandwidth
  Handles sequential and random well
  Designed for: mixed workloads on HDDs
  Problem: too complex for SSDs; removed in kernel 5.0

NOOP / none:
  No reordering; FIFO queue
  Minimal overhead
  Best for: NVMe, RAM disks, VMs with paravirtual storage
  
  echo none > /sys/block/nvme0n1/queue/scheduler
  
mq-deadline (modern default for HDDs):
  Multi-queue aware (modern block layer)
  Two queues: read queue + write queue
  Each request has a deadline (read: 500ms, write: 5000ms)
  Reorders for efficiency but MUST meet deadline
  Best for: databases (read latency critical)
  
BFQ (Budget Fair Queuing) - current default on many distros:
  Like CFQ but budget-based (allocates I/O time slices)
  Prioritizes interactive/latency-sensitive processes
  Desktop-friendly: prevents I/O monopolization
  
Kyber (added in kernel 4.12):
  Designed for fast NVMe/SSDs
  Token-bucket based
  Goal: balance throughput and latency
  Less commonly tuned than mq-deadline
```

---

### Checking and Changing Schedulers

```bash
# Check current scheduler for each block device:
cat /sys/block/sda/queue/scheduler
# Output: [mq-deadline] kyber bfq none
# [brackets] indicate current active scheduler

# Check for NVMe:
cat /sys/block/nvme0n1/queue/scheduler
# Should be: [none] or [mq-deadline]
# For NVMe: prefer "none"

# Change scheduler (persistent until reboot):
echo mq-deadline > /sys/block/sda/queue/scheduler
echo none > /sys/block/nvme0n1/queue/scheduler

# Make permanent (udev rule):
# /etc/udev/rules.d/60-scheduler.rules:
# ACTION=="add|change", KERNEL=="sda", ATTR{queue/scheduler}="mq-deadline"
# ACTION=="add|change", KERNEL=="nvme*", ATTR{queue/scheduler}="none"
udevadm control --reload-rules

# Tune mq-deadline read/write deadlines:
cat /sys/block/sda/queue/iosched/read_expire    # default 500ms
cat /sys/block/sda/queue/iosched/write_expire   # default 5000ms
echo 250 > /sys/block/sda/queue/iosched/read_expire  # reduce for DB
```

---

### I/O Scheduling for Databases

```bash
# Database recommendation (PostgreSQL, MySQL, MongoDB on HDD):
# mq-deadline with tuned read deadline
echo mq-deadline > /sys/block/sda/queue/scheduler
echo 100 > /sys/block/sda/queue/iosched/read_expire  # 100ms for DB reads

# Database recommendation (on NVMe):
echo none > /sys/block/nvme0n1/queue/scheduler
# Let NVMe firmware handle its own queuing

# Queue depth tuning:
cat /sys/block/nvme0n1/queue/nr_requests  # default: 256
# NVMe can handle thousands of concurrent requests
# Increase for high IOPS workloads:
echo 1024 > /sys/block/nvme0n1/queue/nr_requests

# Read-ahead tuning:
cat /sys/block/sda/queue/read_ahead_kb   # default: 128KB
# For sequential workload: increase
echo 2048 > /sys/block/sda/queue/read_ahead_kb
# For database (random I/O): reduce
echo 16 > /sys/block/sda/queue/read_ahead_kb

# Monitor I/O scheduler queue depth and latency:
iostat -x -d 1 sda
# Look for: avgqu-sz (avg queue depth), await (avg wait time)
# High await on HDD under load = I/O scheduling issue
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "The default I/O scheduler is always optimal" | Default schedulers are chosen for general workloads. A database on HDD benefits from mq-deadline with reduced read_expire. An application on NVMe using mq-deadline adds unnecessary reordering overhead; `none` is better. Always benchmark after changing schedulers |
| "NVMe doesn't need an I/O scheduler at all" | Technically correct that reordering is unnecessary for NVMe (any sector is equally fast), but a scheduler still handles: merge of adjacent requests, queue depth management, fairness between processes. The `none` scheduler just means no reordering; kernel still manages request queues |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Check scheduler | `cat /sys/block/sda/queue/scheduler` |
| NVMe best choice | `none` (no reordering overhead) |
| HDD best choice | `mq-deadline` (merge + reorder + deadline) |
| Read deadline | `read_expire`: 500ms default; reduce to 100ms for DB |
| Queue depth | `nr_requests`: increase for NVMe high IOPS |
| Read-ahead | Increase for sequential; decrease for random DB reads |
