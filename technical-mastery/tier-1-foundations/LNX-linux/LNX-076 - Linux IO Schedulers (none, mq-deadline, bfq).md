---
id: LNX-076
title: "Linux I/O Schedulers (none, mq-deadline, bfq)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-009, LNX-022
used_by: LNX-088, LNX-094
related: LNX-009, LNX-088, LNX-077
tags: [io-scheduler, blk-mq, mq-deadline, bfq, none, CFQ, elevator, SSD, NVMe, request-queue, deadline, IOPS, throughput]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 76
permalink: /technical-mastery/lnx/linux-io-schedulers/
---

## TL;DR

Linux I/O schedulers determine the ORDER in which kernel delivers I/O requests
to storage devices. Modern Linux uses **multi-queue block layer (blk-mq)**.
Three schedulers: **none** (no reordering, direct to driver - best for NVMe
SSDs with internal queuing), **mq-deadline** (deadline-based, prevents
starvation, best for SSDs, databases), **bfq** (Budget Fair Queueing -
fairness across processes, best for HDDs and desktop responsiveness). Check:
`cat /sys/block/sda/queue/scheduler`. Change: `echo mq-deadline > /sys/block/
sda/queue/scheduler`. NVMe drives: use `none` (they have their own internal
queuing and optimization). SATA SSDs/HDDs: use `mq-deadline` or `bfq`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-076 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | I/O scheduler, blk-mq, mq-deadline, bfq, none, NVMe, SSD, deadline, IOPS, storage performance |
| **Prerequisites** | LNX-009 (Disk management), LNX-022 (Process management) |

---

### The Problem This Solves

**Problem 1**: A database server uses SATA SSDs and reports high I/O latency
at peak load. The I/O scheduler is `cfq` (Completely Fair Queuing - old
scheduler). CFQ distributes time slices equally but causes priority inversion:
batch backup jobs get equal I/O time as the database's latency-sensitive
queries. Switching to `mq-deadline`: database gets predictable low-latency
I/O (deadline prevents starvation), throughput improves.

**Problem 2**: A developer's Linux laptop plays video while compiling code,
and video stutters. CFQ or `none` gives the CPU-intensive compiler equal or
higher I/O priority vs the video player. `bfq` provides interactive responsiveness:
the video player gets buffered I/O priority (bfq detects low-throughput
interactive applications), compilation runs in background. Video plays smooth.

---

### Textbook Definition

**I/O scheduler (block scheduler)**: A kernel component that manages the
queue of I/O requests between the VFS/page cache and the block device driver.
It decides: which requests to issue first, how to merge adjacent requests,
how to balance fairness vs throughput vs latency.

**Multi-queue block layer (blk-mq)**: Modern I/O path architecture (kernel
3.13+, default in 4.x). Replaces single I/O queue with: software staging
queues (per-CPU) + hardware dispatch queues (per-CPU or device queue depth).
Better SSD/NVMe performance by eliminating single queue bottleneck.

**Current schedulers (blk-mq era):**
- **none** (also called `noop`): no scheduling - submit requests as-received to the hardware queue. Best for NVMe (hardware queue handles optimization)
- **mq-deadline**: adds read/write deadlines to prevent starvation. Read deadline: 500ms default. Write deadline: 5s default. Best for: databases, latency-sensitive workloads
- **bfq** (Budget Fair Queueing): hierarchical fair scheduling, tracks per-process I/O, prioritizes interactive/synchronous I/O. Best for: desktop responsiveness, mixed workloads, HDDs

**Old schedulers (single-queue, legacy, removed in kernel 5.0):**
- **cfq**: Completely Fair Queuing (popular but deprecated)
- **noop**: predecessor to `none`
- **deadline**: predecessor to `mq-deadline`

---

### Understand It in 30 Seconds

```bash
# === Check scheduler for all block devices ===
for dev in /sys/block/*/queue/scheduler; do
    disk=$(echo $dev | awk -F'/' '{print $4}')
    sched=$(cat $dev)
    echo "$disk: $sched"
done
# sda: [mq-deadline] none bfq   <- mq-deadline active (in brackets)
# nvme0n1: [none] mq-deadline bfq  <- none active (correct for NVMe!)
# sdb: none mq-deadline [bfq]    <- bfq active

# === Check for a single device ===
cat /sys/block/sda/queue/scheduler
# [mq-deadline] none bfq   <- current scheduler in brackets

# === Change scheduler (immediate, no reboot) ===
echo mq-deadline > /sys/block/sda/queue/scheduler
echo none > /sys/block/nvme0n1/queue/scheduler
echo bfq > /sys/block/sda/queue/scheduler

# === Persist across reboots ===
# Method 1: udev rule (recommended):
cat > /etc/udev/rules.d/60-scheduler.rules << 'EOF'
# NVMe: use none (hardware handles queuing)
ACTION=="add|change", KERNEL=="nvme[0-9]*n[0-9]*", \
    ATTR{queue/scheduler}="none"
# SATA SSDs (identified by rotational=0):
ACTION=="add|change", KERNEL=="sd[a-z]", \
    ATTR{queue/rotational}=="0", \
    ATTR{queue/scheduler}="mq-deadline"
# HDDs (rotational=1):
ACTION=="add|change", KERNEL=="sd[a-z]", \
    ATTR{queue/rotational}=="1", \
    ATTR{queue/scheduler}="bfq"
EOF
udevadm trigger   # apply immediately

# Method 2: kernel command line (grub):
# Add to GRUB_CMDLINE_LINUX in /etc/default/grub:
# elevator=mq-deadline
# Then: update-grub && reboot

# === Check device type ===
cat /sys/block/sda/queue/rotational
# 0 = SSD, 1 = HDD (some SSDs may report 1 incorrectly)
lsblk -o NAME,ROTA
# ROTA=1 means rotational (HDD), ROTA=0 means SSD

# === Scheduler-specific tuning ===
# mq-deadline tuning:
cat /sys/block/sda/queue/iosched/read_expire   # 500 (ms)
cat /sys/block/sda/queue/iosched/write_expire  # 5000 (ms)
cat /sys/block/sda/queue/iosched/writes_starved  # 2 (max write dispatches before reads)

# bfq tuning:
cat /sys/block/sda/queue/iosched/timeout_sync   # 125 (ms)
cat /sys/block/sda/queue/iosched/max_budget     # 0 (auto)

# none: no tunable (no scheduler, just queue depth):
cat /sys/block/nvme0n1/queue/nr_requests   # hardware queue depth
# 1023 (NVMe typically supports 1024 concurrent requests)

# === Monitor I/O scheduler effectiveness ===
iostat -x -d 1 /dev/sda
# %util: device utilization (>90% = saturated)
# await: average I/O wait time (ms) - key latency metric
# r_await, w_await: read/write wait separately
# avgrq-sz: average request size (KB)

# io latency distribution (requires blktrace or bpftrace):
bpftrace -e '
tracepoint:block:block_rq_complete {
    @us = hist((nsecs - @start[args->sector]) / 1000);
    delete(@start[args->sector]);
}
tracepoint:block:block_rq_issue {
    @start[args->sector] = nsecs;
}
END { print(@us); }
'
```

---

### First Principles

**Why I/O scheduling exists:**
```
HDD physical constraints (why scheduling matters for HDDs):
  Seek time: 3-10 ms per random seek (read/write head movement)
  Rotational delay: 0-8 ms (wait for disk to rotate to correct sector)
  Transfer time: <1 ms per 64 KB read
  
  Two random reads from opposite sides of disk:
    Seek + rotation + transfer: 12 ms each = 24 ms total
  
  With elevator scheduling (sort by disk position):
    Read sector 1000, 1010, 1020 (all sequential!)
    Seek once, transfer all three: ~5 ms total
    Savings: 79% (24ms -> 5ms)
  
  This is why CFQ/BFQ exist: reorder requests to minimize seek time

SSD/NVMe: no physical seeks (why none scheduler is best):
  All sectors equally fast to access (no head movement)
  Reordering requests = NO benefit (no seek cost to optimize)
  
  NVMe with depth=1024 hardware queue:
    1024 outstanding requests simultaneously served in parallel
    Each request has identical latency regardless of "position"
    Sequential vs random: similar performance (no seek penalty)
    
  Adding a software I/O scheduler to NVMe:
    - Reorders requests (no benefit)
    - Adds CPU overhead (scheduler lock contention, code paths)
    - Reduces parallelism (scheduler serializes somewhat)
    NET EFFECT: worse performance than none!
```

**mq-deadline scheduling algorithm:**
```
Request queues:
  Read queue: sorted by LBA position (elevator)
  Write queue: sorted by LBA position (elevator)
  
  Each request gets a DEADLINE:
    Reads: deadline = submission_time + 500ms (default)
    Writes: deadline = submission_time + 5000ms (default)

Dispatching:
  1. Check deadline queues: any request past its deadline?
     -> Dispatch that request FIRST (prevent starvation)
  2. Prefer reads over writes (read deadline shorter):
     -> read requests are more latency-sensitive
  3. Otherwise: dispatch requests in LBA order (elevator)
     -> maximizes throughput (sequential-like order)

Why reads have shorter deadline:
  Applications block on reads (synchronous: read()->return)
  Applications rarely block on writes (write->kernel returns, writes async)
  -> Read latency directly impacts application response time
  -> Write latency often hidden by write-back cache

Result:
  Databases get predictable read latency (bounded by 500ms deadline)
  Backup jobs don't starve (writes have 5s deadline, eventually served)
  Good throughput (elevator minimizes random seeks when possible)
```

**bfq algorithm:**
```
BFQ: Budget Fair Queueing
  Each process/group gets a budget (number of sectors to serve)
  Budgets are refilled based on process "class":
    Interactive processes: smaller budgets, served more often
      -> Low latency, feel responsive
    Batch processes: larger budgets, served less often
      -> High throughput, but yield to interactive
    
  Interactive detection: processes with short think times
    (quickly issues next I/O after completing current one)
    -> Classified as interactive -> higher priority
  
  Hierarchy: integrates with cgroups io controller
    -> Per-cgroup I/O fairness
    -> Different storage policies per container

BFQ vs mq-deadline:
  BFQ: better for complex fairness (HDD, mixed workloads, desktop)
  mq-deadline: better for simple predictability (SSDs, databases)
  BFQ overhead: ~3% CPU higher than mq-deadline (more complex algorithm)
```

---

### Thought Experiment

Tuning I/O scheduler for a database server:

```bash
#!/bin/bash
# I/O scheduler tuning script for a database server

# Detect device types and apply appropriate schedulers:
tune_io_scheduler() {
    local dev="$1"
    local rotational=$(cat "/sys/block/$dev/queue/rotational" 2>/dev/null)
    local vendor=$(cat "/sys/block/$dev/device/vendor" 2>/dev/null | tr -d ' ')
    
    case "$dev" in
        nvme*)
            # NVMe: hardware handles all queuing
            echo none > "/sys/block/$dev/queue/scheduler"
            # Increase queue depth (NVMe can handle 1024):
            echo 1024 > "/sys/block/$dev/queue/nr_requests"
            echo "NVMe $dev: set to none, queue=1024"
            ;;
        *)
            if [[ "$rotational" == "0" ]]; then
                # SATA SSD
                echo mq-deadline > "/sys/block/$dev/queue/scheduler"
                # Tune for database workload:
                echo 100 > "/sys/block/$dev/queue/iosched/read_expire"   # 100ms
                echo 2000 > "/sys/block/$dev/queue/iosched/write_expire"  # 2s
                echo 1 > "/sys/block/$dev/queue/iosched/writes_starved"
                echo 256 > "/sys/block/$dev/queue/nr_requests"
                echo "SSD $dev: set to mq-deadline (DB tuned)"
            else
                # HDD
                echo bfq > "/sys/block/$dev/queue/scheduler"
                echo 256 > "/sys/block/$dev/queue/nr_requests"
                echo "HDD $dev: set to bfq"
            fi
            ;;
    esac
}

# Apply to all block devices:
for dev in $(lsblk -dn -o NAME); do
    tune_io_scheduler "$dev"
done

# Baseline I/O latency measurement after change:
echo "=== I/O latency after tuning ==="
for dev in sda nvme0n1; do
    echo "Device: $dev"
    cat "/sys/block/$dev/queue/scheduler"
done

iostat -x -d 1 5 /dev/sda /dev/nvme0n1 | \
    awk 'NR>1 {print $1, "await:", $10, "ms"}'
```

---

### Mental Model / Analogy

```
I/O schedulers = different restaurant order management systems

Diners = processes making I/O requests
Kitchen = storage device (HDD or SSD)
Orders = I/O requests (reads/writes)
Order queue = I/O request queue

HDD = old-style kitchen with one cook who must physically
      walk to different cooking stations:
      Walk to pasta station -> walk to grill -> walk to prep area
      Walking = seek time (3-10 ms per seek!)
      
      Smart order management: group all pasta orders, then grill orders
      = elevator algorithm: reorder orders to minimize walking

none scheduler = "fast food kitchen" (NVMe SSD):
  10 cooks, all doing different items simultaneously (parallel queues)
  No walking needed (no disk head movement)
  Each cook is equally fast for any item (no seek time)
  Adding an order manager = just slows things down
  "none" = no manager, orders go directly to first available cook

mq-deadline scheduler = "deadline-enforcing manager":
  Sorts orders to minimize kitchen walking (elevator)
  BUT: every order gets a time stamp with a max wait time
  If order has been waiting 500ms: GO NOW, skip optimization
  Database orders (reads): 500ms deadline
  Backup orders (writes): 5000ms deadline
  No order waits more than its deadline, even if suboptimal routing
  
  Perfect for: "most orders are database reads, don't let them wait"

bfq scheduler = "fair-share restaurant":
  Tracks each customer's recent orders (process history)
  Regular quick orderers (interactive processes): served faster
  Big bulk orders (batch jobs): served slower but eventually
  Groups (cgroups): each table gets fair share of kitchen time
  
  Perfect for: "multiple customers, fair service, some VIP (interactive)"
```

---

### Gradual Depth - Five Levels

**Level 1:**
What I/O schedulers do. Three modern schedulers: none, mq-deadline, bfq.
Which to use when: none for NVMe, mq-deadline for SSDs/databases, bfq for
HDDs/desktop. Check scheduler: `/sys/block/dev/queue/scheduler`. Change it.

**Level 2:**
Multi-queue block layer (blk-mq) architecture. Software queues vs hardware
queues. Why none is optimal for NVMe. mq-deadline algorithm: read/write
deadlines, elevator ordering. bfq fairness model. `rotational` attribute.
`iostat -x` for I/O latency monitoring.

**Level 3:**
mq-deadline tuning: `read_expire`, `write_expire`, `writes_starved`.
bfq group scheduling (cgroup integration). `nr_requests` (queue depth).
Relationship to cgroup io controller. Monitoring: `blktrace`, `bpftrace`
for per-request latency. Old vs new schedulers (CFQ -> BFQ migration).

**Level 4:**
blk-mq internals: per-CPU software queues, dispatch from software to hardware
queues. `nr_hw_queues` (hardware queue count). NVMe queue depth vs latency
curve. I/O priority: `ionice` and its interaction with BFQ. PCIe NVMe vs
SATA SSD fundamental latency differences. `blktrace` + `blkparse` for I/O
trace analysis. LVM and RAID effects on scheduler choice.

**Level 5:**
I/O scheduler implementation in kernel (block/mq-deadline.c, block/bfq-*.c).
Scheduler selection in cloud VMs: virtio-blk (uses none/mq-deadline), NVMe-over-
Fabrics. Per-cgroup I/O limits with BFQ (io.weight, io.max in cgroup v2).
SCSI command queuing (NCQ) and its interaction with software scheduler. io_uring:
bypasses the I/O scheduler entirely for maximum performance. NVMe ZNS (Zoned
Namespaces) and its implications for scheduler design.

---

### Code Example

**BAD - wrong scheduler for device type:**
```bash
# BAD 1: Using bfq on a NVMe device (performance degradation):
echo bfq > /sys/block/nvme0n1/queue/scheduler

# Measure: 4K random reads (InnoDB workload):
fio --filename=/dev/nvme0n1 \
    --direct=1 --rw=randread --bs=4k \
    --ioengine=libaio --iodepth=32 \
    --numjobs=4 --runtime=30 --group_reporting \
    --name=test

# With bfq: ~150,000 IOPS, 800 us avg latency
# With none: ~350,000 IOPS, 350 us avg latency
# bfq scheduler overhead: 57% throughput loss on NVMe!

# BAD 2: Using none on a HDD shared by multiple processes:
echo none > /sys/block/sda/queue/scheduler
# Batch backup job and database running simultaneously:
# Backup: sequential writes to beginning of disk
# Database: random reads from end of disk
# With none: alternating between positions -> constant seeks
# Result: each seek 8ms, both processes suffer
# With bfq: reorder + fair scheduling -> 50% better total throughput

# GOOD 1: Proper NVMe tuning:
echo none > /sys/block/nvme0n1/queue/scheduler
# Also: ensure enough queue depth for parallelism:
cat /sys/block/nvme0n1/queue/nr_requests  # should be 1023 or more
# And: disable queue merging (NVMe is random-access optimized):
echo 0 > /sys/block/nvme0n1/queue/nomerges  # 0=all merges allowed, 2=no merges
# For NVMe: merging 4K reads has minimal benefit anyway

# GOOD 2: mq-deadline for database on SATA SSD:
echo mq-deadline > /sys/block/sda/queue/scheduler
# Tune for OLTP workload (low read latency):
echo 100 > /sys/block/sda/queue/iosched/read_expire    # 100ms (down from 500ms)
echo 2000 > /sys/block/sda/queue/iosched/write_expire  # 2s (down from 5s)
# Verify:
cat /sys/block/sda/queue/iosched/read_expire   # 100
```

---

### Comparison Table

| Scheduler | Best for | Algorithm | Overhead |
|-----------|---------|----------|---------|
| `none` | NVMe SSDs, any SSD in cloud VMs | No scheduling | Minimal |
| `mq-deadline` | SATA SSDs, databases, low-latency | Deadline + elevator | Low |
| `bfq` | HDDs, desktop, mixed/fair workloads | Fair budget + elevator | ~3% CPU |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "none scheduler means random order, which is bad" | `none` means "no reordering in the kernel" - requests go to the hardware queue in submission order. For NVMe SSDs: this is actually optimal. NVMe devices have their own internal queuing (up to 65,535 queues x 65,535 requests), internal algorithms for command reordering, and parallel hardware execution. Adding software reordering ON TOP of hardware reordering adds overhead without benefit. The "no scheduling" scheduler is the fastest for devices that don't need help. |
| "mq-deadline is a latency guarantee" | The deadline is a MAXIMUM WAIT TIME, not a guaranteed response time. A request with 500ms read deadline will be dispatched to the device WITHIN 500ms, but the device's own service time (seek + rotation + transfer for HDD, internal latency for SSD) is additional. With a busy HDD at 100% utilization: the request gets submitted to the device at 500ms but may still wait in the device's internal queue. The deadline prevents the scheduler from delaying dispatch, but can't control device service time. |
| "CFQ is better because it's more widely documented" | CFQ (Completely Fair Queuing) was removed from the kernel in 5.0 (2019). It was the default for many years and much documentation references it. Modern kernels don't have CFQ. Distributions running kernel 4.x may still have it. For modern kernels (5.0+): only `none`, `mq-deadline`, and `bfq` are available. If documentation says "use CFQ": it's outdated. The replacement for CFQ in most cases is `bfq` (similar fairness goals, better algorithm). |
| "I/O scheduler choice doesn't matter for cloud instances (VMs)" | In VMs: the guest sees a virtual block device (virtio-blk, NVMe, or paravirtualized). The guest's I/O scheduler talks to the virtual device, which then goes through the hypervisor's scheduler and the physical device scheduler. For many cloud VMs (AWS EBS, GCP PD): the underlying storage is network-attached (SAN-like), with latency 100-500 us (vs NVMe's 50-100 us). In this case: `none` or `mq-deadline` is appropriate (no seek time, network latency dominates). The guest I/O scheduler matters LESS in VMs because the hypervisor does its own scheduling - but it's not zero impact. |

---

### Failure Modes & Diagnosis

**I/O performance investigation:**
```bash
# Symptom: Database reads are slow (high await), disk not saturated

# Step 1: Basic I/O stats:
iostat -x -d 1 5 /dev/sda
# Look for: await (ms), %util, r_await, w_await
# High await with low %util: scheduler issue or queue depth issue
# High %util with any await: device saturated

# Step 2: Check scheduler:
cat /sys/block/sda/queue/scheduler
# If [bfq] on a database server: switch to mq-deadline

# Step 3: Check queue depth:
cat /sys/block/sda/queue/nr_requests  # software queue depth
cat /sys/block/sda/queue/nr_hw_queues  # hardware queues

# Step 4: Check if merging is helping or hurting:
grep . /sys/block/sda/queue/iosched/ 2>/dev/null
# Shows scheduler-specific settings

# Step 5: Detailed latency histogram:
biolatency-bpfcc -D 10 1   # 10-second histogram for /dev/sda
# Shows distribution of I/O latencies

# Fix: for database on SATA SSD:
echo mq-deadline > /sys/block/sda/queue/scheduler
echo 100 > /sys/block/sda/queue/iosched/read_expire  # 100ms read deadline

# Verify improvement:
iostat -x -d 1 10 /dev/sda
# await should decrease after scheduler change
```

---

### Related Keywords

**Foundational:**
LNX-009 (Disk management), LNX-022 (Process management)

**Builds on this:**
LNX-088 (Disk performance, fio, blktrace), LNX-094 (Performance troubleshooting)

**Related:**
LNX-072 (cgroups io controller), LNX-077 (CPU CFS scheduler)

---

### Quick Reference Card

| Device Type | Recommended Scheduler | Rationale |
|------------|---------------------|----------|
| NVMe SSD | `none` | Hardware handles queuing better |
| SATA SSD (database) | `mq-deadline` | Bounded latency, prevents starvation |
| SATA SSD (desktop) | `mq-deadline` or `bfq` | Either works |
| HDD | `bfq` | Fairness + elevator ordering |
| Cloud VM block device | `none` or `mq-deadline` | Depends on underlying storage |

| Command | Purpose |
|---------|---------|
| `cat /sys/block/sda/queue/scheduler` | Current scheduler |
| `echo mq-deadline > /sys/block/sda/queue/scheduler` | Set scheduler |
| `cat /sys/block/sda/queue/rotational` | 0=SSD, 1=HDD |
| `iostat -x -d 1` | I/O latency (await column) |

**3 things to remember:**
1. NVMe: always use `none` (hardware manages parallelism better than any software scheduler)
2. `mq-deadline`: prevents I/O starvation via deadlines (databases prefer this)
3. Check scheduler with `cat /sys/block/sda/queue/scheduler` - brackets show current

---

### Transferable Wisdom

I/O scheduler concepts transfer to: Database query schedulers (PostgreSQL's
parallel query scheduler, MySQL's InnoDB I/O thread pool): similar concepts
of work ordering, priority, and fairness. OS CPU schedulers (CFS, PREEMPT_RT):
same trade-off between fairness (BFQ = CFS) and deadline guarantees (mq-deadline
= PREEMPT_RT). Kubernetes storage class IOPS limits (io.max in cgroup v2):
the BFQ scheduler integrates with cgroup io controller for per-cgroup I/O
limits. Network traffic shaping (tc qdisc): same concept of a scheduler
deciding packet transmission order - `fq_codel` (fair + low latency) is
the network analog of BFQ. The fundamental trade-off in all schedulers:
fairness (everyone gets equal share) vs. predictability (critical tasks get
guaranteed service) vs. throughput (maximize total work done). I/O scheduler
selection is a microcosm of this: BFQ=fairness, mq-deadline=predictability,
none=maximum throughput (let hardware decide fairness).

---

### The Surprising Truth

The "none" scheduler (no scheduling) being optimal for NVMe is counterintuitive
but reveals a fundamental principle: the best scheduler is sometimes the
one that doesn't exist. When you add a scheduling layer, you're implicitly
assuming the scheduler has better information than the device. For HDDs:
the OS knows seek costs and can reorder for fewer seeks (better than the
device). For NVMe: the device has 64,000+ command queues, knows its internal
layout, and processes requests in parallel with internal optimization. Any
software reordering just ADDS overhead without improving the decision.
This is a broader systems principle: intermediary layers add value only
when they have BETTER information than the entities they mediate between.
When the "lower layer" (NVMe hardware) is smarter, the intermediary (scheduler)
should get out of the way. This same reasoning explains why modern databases
(PostgreSQL with `O_DIRECT`) bypass the page cache when they have their own
buffer management, why SR-IOV lets VMs talk directly to NIC hardware bypassing
the hypervisor, and why io_uring bypasses traditional system call overhead.
The lesson: "more software" is not always "more performance."

---

### Mastery Checklist

- [ ] Can identify the appropriate I/O scheduler for NVMe, SATA SSD, and HDD
- [ ] Can check and change the I/O scheduler and make it persistent via udev rules
- [ ] Understands why `none` is optimal for NVMe (hardware parallelism)
- [ ] Can use `iostat -x` to measure `await` latency and identify I/O bottlenecks
- [ ] Knows how to tune mq-deadline deadlines for database workloads

---

### Think About This

1. A cloud-hosted database runs on AWS EBS (network-attached block storage
   with ~200us average latency, much higher than local NVMe's 50us). The
   current I/O scheduler is `mq-deadline`. An engineer suggests switching to
   `none`. Using your knowledge of I/O scheduler purpose, explain: (a) does
   mq-deadline help or hurt for network-attached storage where there's no
   seek penalty? (b) what latency component does mq-deadline add? (c) when
   would mq-deadline still be beneficial even for network-attached storage?

2. A Kubernetes node has multiple containers: a Redis instance (latency-sensitive,
   random 4K reads), a backup job (sequential writes, background), and a
   log aggregator (sequential reads, best-effort). All share one SATA SSD.
   Design the I/O scheduling configuration: which scheduler would you use,
   how would you configure cgroup io.weight for each container, and what
   specific mq-deadline or bfq parameters would you tune?

3. You observe that `await` in `iostat` for a database's SSD is consistently
   2-3ms (versus the SSD's rated 0.1ms random read latency). The `%util`
   is only 30%. What are the possible causes of this 20-30x latency inflation
   despite low utilization? Trace through the I/O path: software queue,
   scheduler, hardware queue, device, and identify where latency could be added.

---

### Interview Deep-Dive

**Foundational:**
Q: What are the main I/O schedulers in modern Linux, and when would you use each?
A: Modern Linux (kernel 5.0+) has three I/O schedulers in the blk-mq (multi-queue block layer) framework: NONE: the simplest scheduler - no reordering, requests go directly to the hardware queue in submission order. Best for: NVMe SSDs. Reason: NVMe devices have their own internal command queuing (up to 65,535 queues, 65,535 commands each), parallel execution hardware, and internal optimization. Adding software reordering on top only adds CPU overhead without improving I/O ordering (there's no seek cost to optimize). MQ-DEADLINE: adds read and write deadlines to prevent I/O starvation, otherwise uses an elevator algorithm to reorder requests for better HDD seek performance. Read deadline: 500ms default (requests won't wait more than 500ms to be dispatched). Write deadline: 5s. Best for: database servers, SATA SSDs with mixed read/write, latency-sensitive applications. Prevents situation where writes monopolize I/O while reads starve. BFQ (Budget Fair Queueing): hierarchical fair scheduling. Tracks per-process I/O budgets, detects interactive applications (short think times), gives them priority. Integrates with cgroup I/O controller for group scheduling. Best for: HDDs (where elevator ordering and fairness matter most), desktop systems (interactive responsiveness), mixed workload servers where process-level fairness is important. SELECTION GUIDE: NVMe SSD -> none. SATA SSD + database -> mq-deadline (tune read_expire to 100ms). HDD -> bfq. Mixed container workloads on SSD -> mq-deadline + cgroup io weights.

**Expert:**
Q: Why does the multi-queue block layer (blk-mq) exist, and how does it improve I/O performance?
A: The traditional single-queue block layer (pre-blk-mq) had a fundamental scalability bottleneck: one global request queue with one spinlock. On multi-core systems with SSDs: all CPUs competed for this single lock to submit I/O requests, creating lock contention that limited I/O throughput to a fraction of what SSDs could deliver. PROBLEM: SSDs became fast enough to process 1M+ IOPS, but the single-queue block layer was limited to ~200K IOPS due to locking overhead. blk-mq solution (kernel 3.13, 2014): TWO levels of queues. SOFTWARE STAGING QUEUES: per-CPU queues. Each CPU has its own queue with its own lock. CPUs submit to their local queue - zero contention between CPUs. Requests are merged and batched in the per-CPU queue before being dispatched. HARDWARE DISPATCH QUEUES: one queue per hardware submission queue (NVMe has multiple). The scheduler runs between the staging queues and hardware queues: it can see all pending requests and make ordering decisions. DISPATCH: scheduler pulls from staging queues, applies ordering policy, submits to hardware queue(s). Benefits: near-linear scaling with CPU count (each CPU has its own submit path). NVMe with 16 hardware queues: can drive 16 CPUs concurrently, each submitting independently. Lock contention near zero. For `none` scheduler: the dispatch stage is trivial (round-robin through hardware queues), maximizing throughput. For mq-deadline/bfq: scheduling logic operates at the dispatch stage, viewing all pending requests, enabling fair/deadline ordering without the hot single-lock. The blk-mq architecture matches modern storage hardware: NVMe was designed with multi-queue in mind (NVM Express specification defines the queue model), and blk-mq's software model maps directly to NVMe's hardware model.
