---
layout: default
title: "Swap Management"
parent: "Linux"
nav_order: 153
permalink: /linux/swap-management/
number: "0153"
category: Linux
difficulty: ★★☆
depends_on: Linux File System Hierarchy, Operating Systems
used_by: Linux Performance Tuning, Java & JVM Internals, Kubernetes
related: Memory (free, vmstat), Cgroups, Linux Performance Tuning
tags:
  - linux
  - os
  - performance
  - intermediate
---

# 153 — Swap Management

⚡ TL;DR — Swap is disk space the kernel uses as overflow when physical RAM is exhausted — it prevents out-of-memory crashes but at the cost of dramatically slower access; tuning `vm.swappiness` and swap placement determines when and how aggressively the kernel uses it.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
When a Linux system runs out of physical RAM, the OOM (Out-Of-Memory) killer fires. It picks a process — often the largest one — and kills it. If you're unlucky, that's the database. Or the web server. Or the init process. Without swap, any workload that briefly exceeds physical RAM causes immediate, unrecoverable process termination.

**THE BREAKING POINT:**
A batch job starts at 2 AM and allocates more memory than expected. At 2:17 AM the OOM killer triggers and terminates the primary database process. The entire service goes down. The incident postmortem: "we had no swap configured".

**THE INVENTION MOMENT:**
Swap is the safety valve. With swap, the kernel moves rarely-accessed memory pages ("cold" pages) to disk, freeing physical RAM for the batch job. The database stays running. Performance degrades — pages must be read back from disk when accessed — but degraded performance is better than complete failure.

---

### 📘 Textbook Definition

**Swap** is a designated area of disk (a swap partition or swap file) used by the Linux kernel's virtual memory manager as an extension of physical RAM. When the kernel's page replacement algorithm determines that physical RAM needs to be reclaimed, it "swaps out" pages — writes them to the swap area and removes them from physical memory. When a process accesses a swapped-out page, a **page fault** triggers and the kernel reads the page back from swap (swaps in), which can stall the process for milliseconds.

**vm.swappiness** (0-200, default 60) controls how aggressively the kernel swaps anonymous memory (heap, stack) relative to reclaiming page cache. Lower values favour keeping process memory in RAM; higher values allow more aggressive swapping.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Swap is a disk-based RAM overflow valve — it prevents OOM kills but trades performance for availability.

**One analogy:**

> Swap is like a self-storage unit for RAM. When your home (RAM) is full, you move boxes (memory pages) you haven't opened recently to a storage unit (swap/disk). You can still access those boxes — but you have to drive to the storage unit first (10-1000× slower than home). The goal is to keep the home functional by moving cold stuff out, not to use storage as primary living space.

**One insight:**
On an NVMe SSD, a swap read takes ~100μs. A RAM access takes ~100ns. That's 1000× slower. On a spinning HDD, swap reads take ~5-10ms — 50,000× slower. Any workload that actively uses swap will degrade severely. Swap is a last resort, not a performance feature.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Swap moves pages that haven't been accessed recently, not randomly.
2. Anonymous pages (heap, stack) compete with page cache for RAM.
3. `swappiness` controls this balance, not whether swapping occurs at all.
4. Swap space does not increase performance — it trades latency for availability.
5. A system actively swapping is close to failure — investigate immediately.

**DERIVED DESIGN:**
The kernel's page frame reclaim algorithm (PFRA) uses an LRU-like clock algorithm with two lists: active and inactive. Pages move from active → inactive when not accessed recently. When memory pressure builds, inactive pages are candidates for reclaim. For page-cache pages (file-backed), reclaim means discarding (re-read from disk if needed). For anonymous pages (process heap/stack), reclaim requires writing to swap first.

`vm.swappiness` biases the algorithm: at 60 (default), the kernel balances between reclaiming page cache and swapping anonymous memory. At 10 (common server tuning), it strongly prefers reclaiming page cache over swapping. At 0 (not "disable swap" — just very reluctant), it will only swap when absolutely necessary.

**THE TRADE-OFFS:**
**Gain:** OOM prevention; virtual memory overcommit becomes possible; cold data moved out of RAM gives hot data more space.
**Cost:** Active swap causes severe latency spikes; disk I/O from swapping competes with application I/O; debugging swap pressure is complex.

---

### 🧪 Thought Experiment

**SETUP:**
A server runs a web application (using 6GB RAM), a background analytics job that occasionally needs 4GB, and the OS page cache (using ~4GB). Total RAM: 12GB. Peak demand: 14GB.

**WITHOUT SWAP:**
When the analytics job starts and needs 4GB, it pushes total demand to 14GB. The kernel tries to reclaim but there's no escape valve. OOM killer fires. It targets the largest memory user — the web application (6GB). Web service goes down.

**WITH SWAP (swappiness=10):**
When demand reaches 12GB, the kernel begins reclaiming. With swappiness=10, it prefers to evict page cache first (4GB of it). But page cache is needed for file reads. So it keeps frequently-accessed cache and swaps out the analytics job's cold pages. Performance degrades but nothing dies. When the analytics job finishes and memory pressure drops, swapped pages are reclaimed.

**WITH SWAP (swappiness=0):**
The kernel resists swapping until the very last moment — only swapping when it cannot find any other reclaim target. Page cache gets evicted aggressively instead. For a database server where page cache is precious (it caches hot database blocks), swappiness=1 is often preferred over 0.

**THE INSIGHT:**
Swap is not about accommodating chronically-undersized servers — it's about absorbing transient peaks and preventing catastrophic OOM kills. A system that never touches swap is correctly sized; a system that constantly touches swap is undersized.

---

### 🧠 Mental Model / Analogy

> The kernel's memory manager is like a librarian with a desk (RAM) and a warehouse (swap). Books currently being read sit on the desk. Books that haven't been opened recently get moved to the warehouse to make room. If someone asks for a warehoused book, the librarian fetches it — it takes longer but the library stays open. `swappiness` is the librarian's policy for how quickly they move books to the warehouse vs. just returning books to the shelves (page cache eviction).

- "Desk" → RAM
- "Warehouse" → swap space
- "Moving book to warehouse" → swapping out
- "Fetching from warehouse" → swap-in page fault
- "Returns books to shelves" → page cache eviction (reclaiming file-backed pages)

Where this analogy breaks down: the librarian can return a file-backed book cheaply (re-read from original); anonymous pages (heap) have no "original" on disk, so they must be written to swap first — more expensive.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Swap is extra memory space borrowed from disk. When the computer runs out of regular memory (RAM), it moves data it isn't currently using to swap on the disk. This is much slower than RAM but prevents the computer from running out of memory entirely and crashing programs.

**Level 2 — How to use it (junior developer):**
`swapon -s` shows active swap. `free -h` shows RAM and swap usage. `vmstat 1` shows swap activity in real time. To add a swap file: `fallocate -l 4G /swapfile; chmod 600 /swapfile; mkswap /swapfile; swapon /swapfile`. Add to `/etc/fstab` for persistence. Set swappiness: `sysctl vm.swappiness=10`. Make permanent: add `vm.swappiness=10` to `/etc/sysctl.conf`.

**Level 3 — How it works (mid-level engineer):**
The kernel uses kswapd (a background kernel thread) to proactively reclaim pages when free memory drops below the `vm.min_free_kbytes` watermark. Direct reclaim occurs in interrupt context when a process tries to allocate memory and the system is under pressure — this causes latency spikes in the allocating process. Pages are selected for swap using the LRU clock algorithm; recently-accessed pages (referenced bit set) are moved back to the active list; old unreferenced pages become candidates. Swap I/O goes through the block layer — on SSDs, multiple pages can be read/written in parallel. The zswap kernel feature compresses swap pages in RAM before writing to disk, potentially avoiding the swap I/O entirely for compressible data.

**Level 4 — Why it was designed this way (senior/staff):**
Linux's virtual memory system makes a fundamental distinction between file-backed pages (mmap'd files, executable text segments, page cache) and anonymous pages (malloc heap, stack, anonymous mmap). File-backed pages can be evicted without writing to swap — the file on disk is the backing store. Anonymous pages have no disk backing except swap. This distinction drives the swappiness trade-off: evict more page cache (hurts file I/O) or swap anonymous pages (hurts process latency). The default of 60 was chosen for desktop workloads; database servers (whose page cache IS their performance) typically use swappiness=1-10.

---

### ⚙️ How It Works (Mechanism)

**Check swap status:**

```bash
# Show all swap areas with usage
swapon -s
swapon --show  # (same, more readable)

# RAM and swap in human-readable format
free -h
# Output:
#        total   used   free  shared  buff/cache  avail
# Mem:    15Gi   8.2Gi  1.1Gi  0.5Gi  6.1Gi      6.7Gi
# Swap:    4Gi   100Mi  3.9Gi

# Detailed swap stats
vmstat 1     # si/so columns: swap-in/swap-out KB/s
cat /proc/meminfo | grep -i swap
cat /proc/vmstat | grep -E 'pswpin|pswpout'

# Per-process swap usage
for pid in /proc/[0-9]*/status; do
  comm=$(grep Name "$pid" 2>/dev/null | awk '{print $2}')
  swap=$(grep VmSwap "$pid" 2>/dev/null | awk '{print $2}')
  [ -n "$swap" ] && [ "$swap" -gt 0 ] && \
    echo "$swap KB $comm"
done | sort -rn | head -10
```

**Create and manage swap:**

```bash
# Create a 4GB swap file
fallocate -l 4G /swapfile   # instant allocation
# OR: dd if=/dev/zero of=/swapfile bs=1M count=4096
chmod 600 /swapfile          # security: only root can read
mkswap /swapfile             # format as swap
swapon /swapfile             # activate immediately

# Verify
swapon -s

# Persist across reboots
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Disable swap temporarily
swapoff /swapfile   # moves all swap content back to RAM!
# (will fail if insufficient free RAM)

# Set swap priority (multiple swap areas)
swapon -p 10 /swapfile     # higher priority = used first
swapon -p 5  /dev/sdb1     # lower priority
```

**Tuning swappiness:**

```bash
# Check current value (default 60)
cat /proc/sys/vm/swappiness
sysctl vm.swappiness

# Set temporarily
sysctl -w vm.swappiness=10

# Set permanently
echo 'vm.swappiness=10' >> /etc/sysctl.conf
sysctl -p  # apply without reboot

# Recommended values:
# 60  — default (desktop workloads)
# 10  — general server recommendation
# 1   — database servers (keep page cache in RAM)
# 0   — disable swap-preference (not disabling swap!)
# 100 — aggressive swapping (embedded/low-latency)

# vm.vfs_cache_pressure (default 100)
# Lower = keep dentries/inodes in RAM longer
# For servers with many files:
sysctl -w vm.vfs_cache_pressure=50
```

**zswap (compressed swap cache):**

```bash
# Enable zswap (compress pages before writing to swap)
echo 1 > /sys/module/zswap/parameters/enabled

# Check zswap stats
cat /sys/kernel/debug/zswap/pool_total_size
cat /sys/kernel/debug/zswap/stored_pages

# Configure compressor
echo lz4 > /sys/module/zswap/parameters/compressor
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  MEMORY PRESSURE EVENT: Swap I/O begins        │
└────────────────────────────────────────────────┘

 Free memory drops below vm.min_free_kbytes
       │
       ▼
 kswapd kernel thread wakes up
       │
       ▼
 Scan LRU lists for candidate pages
       │
   ┌───┴──────────────────┐
   │                      │
   ▼                      ▼
File-backed pages    Anonymous pages
(page cache)         (heap, stack)
   │                      │
   ▼                      ▼
If not dirty:         Write to swap area
  evict (free)        (swap-out I/O)
If dirty:
  writeback first
       │                  │
       └────────┬─────────┘
                ▼
        Free RAM recovered
                │
                ▼
 Process later accesses swapped page
                │
                ▼
 Page fault → kernel reads from swap (swap-in I/O)
                │  NVMe: ~100μs, HDD: ~5ms
                ▼
 Page restored to RAM, process resumes
```

**FAILURE PATH:**
If `swapoff` is called while swap is heavily used but free RAM < swap usage, `swapoff` blocks trying to move all swap pages back to RAM. If RAM cannot accommodate them all, `swapoff` fails with "Cannot allocate memory". The system remains in a degraded state with partial swap disabled.

---

### 💻 Code Example

**Example 1 — Swap monitoring script:**

```bash
#!/bin/bash
# Alert on high swap usage
WARN_THRESHOLD=25  # % of swap used
CRIT_THRESHOLD=75

SWAP_TOTAL=$(free | awk '/Swap/{print $2}')
SWAP_USED=$(free | awk '/Swap/{print $3}')

[ "$SWAP_TOTAL" -eq 0 ] && { echo "No swap"; exit 0; }

PCT=$(( SWAP_USED * 100 / SWAP_TOTAL ))

if [ "$PCT" -ge "$CRIT_THRESHOLD" ]; then
  echo "CRITICAL: Swap ${PCT}% used" \
       "(${SWAP_USED}/${SWAP_TOTAL} KB)"
  # Show top swap consumers
  for pid in /proc/[0-9]*/status; do
    comm=$(grep ^Name "$pid" 2>/dev/null \
      | awk '{print $2}')
    swap=$(grep VmSwap "$pid" 2>/dev/null \
      | awk '{print $2}')
    echo "$swap $comm"
  done | sort -rn | head -5
elif [ "$PCT" -ge "$WARN_THRESHOLD" ]; then
  echo "WARNING: Swap ${PCT}% used"
else
  echo "OK: Swap ${PCT}% used"
fi
```

**Example 2 — Optimal swap configuration for a database server:**

```bash
#!/bin/bash
# Apply production database server memory settings

# Minimal swapping: keep database page cache in RAM
sysctl -w vm.swappiness=1

# Aggressive page cache retention
sysctl -w vm.vfs_cache_pressure=50

# Ensure memory overcommit is controlled
sysctl -w vm.overcommit_memory=2
sysctl -w vm.overcommit_ratio=80

# Apply permanently
cat >> /etc/sysctl.d/99-db-memory.conf << 'EOF'
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.overcommit_memory=2
vm.overcommit_ratio=80
EOF

echo "Database memory settings applied"
```

**Example 3 — Kubernetes node swap handling:**

```bash
# Kubernetes historically required swap DISABLED
# Check:
swapon -s    # must return no output
free -h      # Swap: 0

# Disable swap now:
swapoff -a

# Disable in fstab (prevent re-enable on reboot):
sed -i '/swap/d' /etc/fstab
# OR comment out:
sed -i 's/^\([^#].*swap.*\)$/#\1/' /etc/fstab

# Kubernetes 1.28+: swap support added (alpha)
# Requires kubelet configuration:
# --feature-gates=NodeSwap=true
# --memory-swap-behavior=LimitedSwap
```

---

### ⚖️ Comparison Table

| Approach       | OOM Prevention | Performance             | Complexity | Best For                          |
| -------------- | -------------- | ----------------------- | ---------- | --------------------------------- |
| No swap        | No             | Best                    | None       | Kubernetes nodes (controlled env) |
| Swap file      | Yes            | Poor (HDD) / Fair (SSD) | Low        | General servers                   |
| Swap partition | Yes            | Same as file            | Moderate   | Traditional setup                 |
| **zswap**      | Yes (better)   | Better (compressed)     | Moderate   | Modern servers                    |
| zram           | Yes            | Best (in-RAM compress)  | Moderate   | Memory-constrained desktops       |
| Oversized RAM  | N/A            | Best                    | High cost  | Production databases              |

How to choose: Kubernetes nodes → disable swap; production databases → swap with swappiness=1; general servers → 1-2× RAM swap file on SSD with swappiness=10; memory-constrained systems → zswap or zram.

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                             |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| vm.swappiness=0 disables swap                       | swappiness=0 means "avoid swapping anonymous memory unless unavoidable" — the kernel can still swap; to actually prevent swapping, use `swapoff -a` |
| More swap = more memory                             | Swap is not free memory — actively using swap severely degrades performance; it's a safety valve, not a memory upgrade                              |
| Disabling swap improves performance                 | Only if the workload never exceeds RAM; if OOM killer fires instead, killing a critical process is far worse than some swap latency                 |
| Swap on SSD is the same as RAM                      | SSD swap access (~100μs) is still 1000× slower than RAM (~100ns); intensive swap on SSD will degrade performance and wear the SSD                   |
| Setting swappiness for one container affects others | swappiness is a system-wide kernel parameter; per-cgroup swappiness is available in cgroups v1 via `memory.swappiness`                              |

---

### 🚨 Failure Modes & Diagnosis

**High Swap Usage Causing Latency Spikes**

**Symptom:**
Application periodically stalls for hundreds of milliseconds. `vmstat 1` shows non-zero `si` (swap-in) values.

**Root Cause:**
Pages swapped out during low-traffic periods are being accessed during high-traffic periods, causing page faults that stall application threads.

**Diagnostic Command:**

```bash
# Watch swap I/O in real time
vmstat 1 | awk 'NR>2 {
  if ($7+$8 > 0) print "SWAP I/O: si="$7 " so="$8
}'

# Find which processes are using swap
for pid in /proc/[0-9]*/status; do
  swap=$(grep VmSwap "$pid" 2>/dev/null | awk '{print $2}')
  name=$(grep ^Name "$pid" 2>/dev/null | awk '{print $2}')
  [ "$swap" -gt 1000 ] 2>/dev/null && \
    echo "$swap KB: $name ($(dirname $pid | grep -oP '\d+'))"
done | sort -rn | head -10
```

**Fix:**

1. Reduce `vm.swappiness` to 1-10 to prevent future swapping.
2. Add RAM to bring the working set into physical memory.
3. Investigate which processes are unexpectedly large and optimise them.
4. If running Kubernetes: size nodes so pods fit in RAM with no swap needed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Linux File System Hierarchy` — swap files live in the filesystem hierarchy; understanding mount points and disk layout is foundational
- `Operating Systems` — virtual memory, paging, and the MMU are the foundational OS concepts that swap implements at the hardware level

**Builds On This (learn these next):**

- `Memory (free, vmstat)` — the monitoring tools for memory and swap pressure
- `Cgroups` — cgroups v1 allows per-cgroup swappiness control; cgroups v2 integrates swap limits with memory limits
- `Linux Performance Tuning` — swap tuning (swappiness, zswap, huge pages) is a major component of Linux memory performance tuning

**Alternatives / Comparisons:**

- `zram` — creates a compressed block device in RAM as swap; no disk I/O, but uses CPU for compression; good for memory-constrained systems
- `zswap` — kernel feature that compresses pages in RAM before writing to disk; hybrid approach reducing disk swap writes
- `OOM Killer` — the alternative to swap; when no swap exists and memory is exhausted, the OOM killer selects and terminates processes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Disk area used as overflow RAM; kernel    │
│              │ writes cold pages to disk to free RAM     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Physical RAM exhaustion → OOM kill;       │
│ SOLVES       │ swap provides a safety valve              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ swappiness=0 ≠ swap disabled; SSD swap    │
│              │ is still 1000× slower than RAM            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Transient memory spikes; servers where    │
│              │ OOM kill is catastrophic                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Kubernetes nodes (require swap off);      │
│              │ performance-critical real-time workloads  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ OOM protection vs latency; availability   │
│              │ vs performance under memory pressure      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A safety valve — prevents OOM crashes    │
│              │  but at 1000× the cost of RAM access"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ zswap → cgroups memory limits → OOM killer│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes cluster with `vm.swappiness=60` (default) is running mixed workloads: a latency-sensitive API service and a batch ML training job. The API service occasionally shows P99 latency spikes of 500ms that correlate with the ML job's memory allocation bursts. Trace the exact kernel mechanism causing these latency spikes (hint: what happens to the API service's pages during the ML job's allocation burst), and design a solution using a combination of cgroups, swappiness configuration, and Kubernetes resource management to eliminate the spikes.

**Q2.** Your monitoring shows a production server is using 40% of its 8GB swap consistently. The VM's RAM is 32GB. The application team insists the server "needs more RAM" but your capacity team says "the system is not OOM-ing so swap is working as intended". Who is right, and what specific `vmstat` and `/proc/meminfo` metrics would you examine to determine whether this is (a) healthy use of swap for cold data, or (b) active swap thrashing indicating genuine memory pressure that requires action?
