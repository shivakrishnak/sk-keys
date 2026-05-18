---
id: OSY-021
title: "Basic OS Monitoring Tools (ps, top, htop, free, vmstat)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-006, OSY-012
used_by: OSY-043, OSY-079
related: OSY-043, OSY-044, OSY-079
tags:
  - foundational
  - tools
  - monitoring
  - ps
  - top
  - vmstat
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/osy/os-monitoring-tools/
---

## TL;DR

`ps`, `top`/`htop`, `free`, and `vmstat` are the first-
responder tools for OS diagnosis. They answer: what's
running? Who's using CPU? How much RAM is free? How
fast are context switches? Every production engineer
must know these before touching any other tool.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-021 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | ps, top, htop, free, vmstat, monitoring |
| **Prerequisites** | OSY-006, OSY-012 |

---

### Essential Commands and What They Show

**`ps aux` - Process snapshot**

```bash
# ps aux: all processes with full info
ps aux | sort -k3 -rn | head -10  # top 10 by CPU
ps aux | sort -k4 -rn | head -10  # top 10 by MEM

# Output columns:
# USER    PID  %CPU  %MEM    VSZ     RSS   STAT  COMMAND
# java   42381  85.0  12.5  8192m   2048m  Sl   java -jar app.jar

# VSZ = virtual memory (allocated) - often large, not real usage
# RSS = resident set size = actual RAM in use
# STAT: S=sleeping, R=running, D=disk wait, Z=zombie, T=stopped
```

**`top` / `htop` - Live CPU and process monitor**

```bash
# top: built-in, live process view
top -H -p <PID>   # show threads (-H) of specific process

# Key fields in top header:
# load average: 0.5 1.2 2.1  (1min, 5min, 15min)
# load > nCPU: system overloaded
# %us: user CPU, %sy: kernel CPU, %wa: I/O wait, %id: idle

# htop: enhanced top (may need: apt install htop)
# Allows: scroll through processes, tree view (F5),
#         kill processes (F9), sort by column (F6)
# For JVM: shows all Java threads with thread IDs
```

**`free -h` - Memory overview**

```bash
$ free -h
              total  used  free  shared  buff/cache  available
Mem:           16G   4.2G   512M    234M       11.3G      10.8G
Swap:           0B     0B    0B

# KEY: "available" = what applications can actually use
# "buff/cache" = page cache (instantly reclaimable)
# "free" is misleadingly small - OS always uses RAM for cache
# Healthy: available > 1GB, swap used = 0B

# Java OOM debugging:
# VIRT (in ps/top) is JVM's virtual memory claim
# RSS (in ps/top) = physical RAM in use = "used" in free output
```

**`vmstat 1` - System-wide activity per second**

```bash
$ vmstat 1 5   # 5 samples, 1 second interval
procs   memory         swap    io     system   cpu
r  b    swpd   free   bi   bo   in    cs   us sy id wa
2  0    0    524288  100  200  1200 12000  45 10 40  5
3  0    0    520000  100  200  1300 15000  50 12 35  3

# r = threads in run queue (waiting for CPU)
# b = threads blocked on I/O  
# cs = context switches/second (key metric!)
# us/sy = user/kernel CPU %
# wa = % time waiting for I/O (iowait)
# in = interrupts/second

# r > nCPU: CPU-bound bottleneck
# b > 2: I/O bottleneck
# cs > 100000/s: too many threads/context switches
# wa > 20%: disk I/O bottleneck
```

---

### Reading a System Under Stress

```bash
# Scenario: Java app slow, diagnosing

# 1. Check CPU
top -b -n1 | head -20
# If us% (user) > 80%: CPU-bound; check what's running
# If wa% (iowait) > 20%: I/O-bound; check disk

# 2. Check memory pressure
free -h
# If available < 500MB: memory pressure; may be swapping
cat /proc/meminfo | grep -E "SwapUsed|Dirty|Writeback"

# 3. Check context switches
vmstat 1 5
# cs > 100K/s: thread count too high for CPU count

# 4. Check specific process
ps aux | grep java
# Look at RSS vs expected heap size

# 5. Check if JVM threads are the source
top -H -p $(pgrep java)
# Shows all JVM threads; find the CPU hog thread
# Note its TID, convert to hex, look in jstack output
```

---

### Textbook Definition

`ps`, `top`, `free`, and `vmstat` are standard Unix
process and system monitoring utilities. They read from
the /proc virtual filesystem (process-specific data under
/proc/PID/) and kernel accounting structures to provide
real-time visibility into CPU utilization, memory usage,
process states, and system activity rates.

---

### Understand It in 30 Seconds

These four tools are the vital signs for a Linux server:
- `ps`: patient list (who's here and alive)
- `top`: heart rate monitor (live activity)
- `free`: blood volume (memory available)
- `vmstat`: systemic activity (system throughput)

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "free memory in `free` output shows how much you can use" | The `free` column is truly unused RAM (misleadingly small). Use `available` column - it includes reclaimable page cache |
| "%CPU in top > 100% means there's a bug" | On multi-core systems, `top` shows 100% per core. A process at 800% is using 8 full CPU cores - correct behavior for a CPU-bound multi-threaded application |

---

### Mastery Checklist

- [ ] Can interpret `ps aux` output (VSZ vs RSS, process states)
- [ ] Reads vmstat cs column for context switch rate
- [ ] Knows `available` in `free` (not `free`) is usable memory
- [ ] Uses `top -H -p <PID>` to inspect JVM threads
