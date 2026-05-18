---
id: LNX-083
title: "Linux OOM Killer (vm.swappiness, oom_score, memory.max)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-074, LNX-072
used_by: LNX-094, LNX-083
related: LNX-074, LNX-072, LNX-077, LNX-094
tags: [oom-killer, oom_score, oom_score_adj, vm.swappiness, memory.max, memory-pressure, cgroup-memory, overcommit, dmesg-oom, process-killing, swap, memory-overcommit, kernel-memory-management]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 83
permalink: /technical-mastery/lnx/linux-oom-killer/
---

## TL;DR

When Linux runs out of physical memory and cannot reclaim enough, the
**OOM Killer** (Out-Of-Memory Killer) selects and kills a process to
free memory. Selection: process with highest **`oom_score`** dies first.
Score = rough % of total RAM used by process + adjustments from
`oom_score_adj` (-1000=never kill, +1000=kill first). Check: `cat
/proc/[pid]/oom_score`. Protect critical processes: `echo -1000 >
/proc/[pid]/oom_score_adj`. **`vm.swappiness`** (0-200): controls
preference for swapping pages vs reclaiming cache (0=prefer cache reclaim,
100=balance, default=60). **cgroup v2 `memory.max`**: hard memory limit
per cgroup - OOM kills processes IN that cgroup only (not system-wide).
Diagnose: `dmesg | grep -i "oom\|killed"`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-083 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | OOM killer, oom_score, vm.swappiness, memory.max, cgroup memory, overcommit, memory pressure |
| **Prerequisites** | LNX-074 (Memory subsystem), LNX-072 (Cgroups) |

---

### The Problem This Solves

**Problem 1**: A system runs 20 services. One service has a memory leak
and gradually allocates all available RAM + swap. Other services start
failing with `ENOMEM` (out of memory) errors. The kernel invokes the OOM
Killer to terminate the highest-`oom_score` process (ideally the leaking
service). If `oom_score_adj` is set correctly: the leaking process is
killed, critical services (database, SSH) are protected.

**Problem 2**: A Kubernetes pod has a memory limit of 512MB. The application
inside the pod allocates 600MB. The cgroup v2 `memory.max = 512m` triggers
an OOM event WITHIN that cgroup - only the pod's processes are killed. Other
pods on the node are unaffected. This is cgroup-scoped OOM: isolation prevents
one pod's memory leak from impacting the entire node.

---

### Textbook Definition

**Linux OOM Killer**: A kernel subsystem that handles out-of-memory conditions
by selecting and killing processes. Invoked when: memory allocation fails after
all reclaim attempts (swap, page cache eviction). The OOM killer scores all
processes by `oom_score` and kills the highest-scored process.

**`oom_score`**: Per-process score (0-1000) calculated by the kernel.
Represents approximately what percentage of system memory the process uses.
Adjusted by `oom_score_adj`. Formula (simplified): `oom_score ≈ (RSS +
swap + pagetable) / total_memory * 1000 + oom_score_adj`.

**`oom_score_adj`**: User-settable adjustment (-1000 to +1000). Default: 0.
-1000 = never kill this process (disables OOM killing). +1000 = always prefer
killing this process. Set by `systemd` unit `OOMScoreAdjust=` or `echo`.

**`vm.swappiness`** (0-200): Controls the kernel's balance between
swapping anonymous pages (process heap/stack) and reclaiming file-backed
pages (page cache). 0: strongly prefer reclaiming page cache before swapping.
100: balanced swap and reclaim. 200: aggressively swap. Default: 60.

**Memory overcommit**: Linux allows processes to allocate more virtual
memory than physical memory exists. `mmap()`/`malloc()` never fails due
to insufficient RAM. Physical pages are allocated ONLY when written
(demand paging). Overcommit behavior: `vm.overcommit_memory` (0=heuristic,
1=always allow, 2=never allow more than commit limit).

---

### Understand It in 30 Seconds

```bash
# === Check OOM scores ===
# View oom_score for a process:
cat /proc/$(pidof java)/oom_score
# 423  <- 42.3% of system memory, high risk of being killed

# View oom_score_adj:
cat /proc/$(pidof java)/oom_score_adj
# 0    <- default, no adjustment

# Protect a critical process from OOM killing:
echo -1000 > /proc/$(pidof postgres)/oom_score_adj
# Now postgres will never be killed by OOM killer

# Make a process a preferred OOM kill target:
echo 1000 > /proc/$(pidof batch_job)/oom_score_adj
# batch_job will be killed first when OOM occurs

# === OOM diagnosis ===
# Check for recent OOM events:
dmesg | grep -i "oom\|killed\|out of memory" | tail -20
# Or:
journalctl -k | grep -i oom | tail -20

# Example OOM dmesg output:
# kernel: [12345.678] oom-kill:constraint=CONSTRAINT_NONE,nodemask=(null),
#   cpuset=/,mems_allowed=0,global_oom,task_memcg=/system.slice/myapp.service,
#   task=myapp,pid=1234,uid=1000
# kernel: [12345.679] Out of memory: Killed process 1234 (myapp)
#   total-vm:8GB, anon-rss:4GB, file-rss:512MB, shmem-rss:0kB

# Find who was killed:
dmesg | grep "Killed process"
# Killed process 1234 (myapp) total-vm:8388608kB, anon-rss:4194304kB

# === cgroup v2 memory limits ===
# Set memory limit for a cgroup:
echo "512M" > /sys/fs/cgroup/myapp/memory.max

# Check current memory usage:
cat /sys/fs/cgroup/myapp/memory.current
# 268435456  <- 256MB currently used

# Check OOM events for a cgroup:
cat /sys/fs/cgroup/myapp/memory.events
# low 0
# high 0
# max 3     <- memory.max was hit 3 times
# oom 1     <- OOM kill occurred 1 time
# oom_kill 1

# Set memory soft limit (throttle before OOM):
echo "400M" > /sys/fs/cgroup/myapp/memory.high
# At 400MB: kernel starts reclaiming aggressively (throttle)
# At 512MB: OOM kill

# === vm.swappiness ===
cat /proc/sys/vm/swappiness    # current value
# 60  <- default

# For databases (prefer keeping memory, avoid swap):
sysctl -w vm.swappiness=1      # nearly never swap
# Persistent: /etc/sysctl.d/99-db.conf: vm.swappiness=1

# For general servers (default):
sysctl -w vm.swappiness=60

# Check swap usage:
free -h
# total   used    free   shared  buff/cache  available
# Mem:    32G     16G    2G      1G          13G         14G
# Swap:   8G      2G     6G      <- 2GB being swapped (maybe normal)

swapon -s   # swap devices and sizes

# Monitor memory pressure:
vmstat 1 5
# procs -----------memory---------- ---swap-- -----io----
# r  b    swpd   free   buff  cache   si   so    bi    bo
# 1  0  204800 512000  64000 8G       10   20  1024  512
#                                     ^--- si/so = swap in/out per sec
# si > 0: pages being swapped in (swap is being READ) -> memory pressure!

# === Memory overcommit ===
cat /proc/sys/vm/overcommit_memory
# 0  <- heuristic (allows some overcommit)
# 1  <- always allow (never fail malloc)
# 2  <- never overcommit (strict)

cat /proc/sys/vm/overcommit_ratio
# 50  <- with overcommit=2: max commit = RAM * 50% + swap

# Current commit limit:
cat /proc/meminfo | grep Committed
# CommitLimit:   33554432 kB  <- max allowed virtual allocation
# Committed_AS:  12345678 kB  <- currently allocated virtual memory
```

---

### First Principles

**How the OOM killer selects victims:**
```
Trigger condition:
  Process calls malloc() / mmap()
  Kernel tries to allocate physical page
  
  Allocation path:
  1. Free page available? -> FAST PATH: return page
  2. Page cache can be reclaimed? -> evict clean cache page
  3. Swap configured and vm.swappiness > 0?
     -> swap out least-recently-used anonymous pages
  4. After swap/reclaim: still insufficient? -> OOM!
  
OOM killer algorithm:
  1. Scan all processes (excluding kernel threads)
  2. For each process, calculate oom_score:
     
     badness = (process_rss + swap_used + pagetable) / total_ram * 1000
     
     total_rss includes:
       - Process own anonymous pages (heap, stack)
       - Shared memory weighted by 1/n_users
       - Memory-mapped files
     
     Adjustments:
       + child processes (add half of children's badness)
       + root processes: subtract 3% (slight root protection)
     
     Final: min(0, max(1000, badness + oom_score_adj))
  
  3. Kill the process with highest score
     (highest score = worst offender = largest memory user)
  
  4. Send SIGKILL to that process
  5. Wait for pages to be freed
  6. Retry the original allocation
  7. If still OOM: kill next highest score process
  
Special cases:
  oom_score_adj = -1000: process is EXCLUDED from OOM killing
    systemd sets this for critical system services
    Used for: init (PID 1), getty (terminal access), ssh daemon
  
  oom_score_adj = +1000: HIGHEST priority for killing
    Kubernetes sets this for Burstable and BestEffort pods
    Java processes with large heaps often have high oom_score
    naturally (they allocate lots of RAM upfront)

cgroup-scoped OOM vs global OOM:
  
  Global OOM:
    System-wide memory exhaustion
    OOM killer scans ALL processes
    Highest oom_score process killed
    Can kill ANY process on the system
  
  cgroup OOM (memory.max exceeded):
    Only the CGROUP that exceeded its limit triggers OOM
    OOM killer only scans processes IN THAT CGROUP
    Kills highest-score process within the cgroup
    Processes OUTSIDE the cgroup are completely unaffected
    
    This is why Kubernetes pod memory limits are safe:
      Pod A uses 600MB > 512MB limit -> kills Pod A's process
      Pod B: completely unaffected (different cgroup)
```

**vm.swappiness mechanics:**
```
Linux memory is:
  Anonymous memory: heap, stack (must swap to use later)
  File-backed pages: page cache (can evict and re-read from disk)

vm.swappiness controls the RATIO:
  High swappiness: prefer swapping anonymous pages
    Pro: keeps page cache (fast filesystem access)
    Con: processes get swapped out, resume slowly (hard page faults)
  
  Low swappiness: prefer evicting page cache
    Pro: processes stay in RAM (no hard page faults)
    Con: filesystem operations re-read from disk more often

Kubernetes setting (vm.swappiness=0 recommended on nodes):
  Containers should NOT use swap
  Reason: with swap, a container can use MORE than its memory.max
  This makes memory limits unreliable
  K8S expectation: if a process needs more memory than available,
  it should OOM (controlled) rather than slowly degrading via swap

Database recommendation (vm.swappiness=1 or 0):
  Databases manage their own buffer pools
  They NEED to stay in RAM (swapping = severe latency)
  Swapping to disk means queries take seconds instead of milliseconds
  vm.swappiness=1: keep anonymous memory (buffer pool) in RAM
  Still allows SOME swap for emergency situations

vm.swappiness effects:
  swappiness = 0:   swap ONLY when anonymous memory cannot be reclaimed
  swappiness = 1:   very reluctant to swap
  swappiness = 60:  balanced (default, Linux desktop/server)
  swappiness = 100: equal probability for swap vs page cache reclaim
  swappiness = 200: aggressively swap anonymous pages (keeps page cache)
                    Good for: in-memory databases, read-heavy workloads
```

---

### Thought Experiment

Java application OOM diagnosis:

```bash
# Scenario: a Java microservice is being killed sporadically
# No obvious memory leak in the code

# Step 1: Check if OOM kill is happening:
dmesg | grep -i "killed\|oom" | grep "java"
# kernel: [98765.432] Out of memory: Killed process 5678 (java)
#   total-vm:4096MB, anon-rss:2048MB, file-rss:512MB

# Step 2: Check the oom_score:
cat /proc/$(pidof java)/oom_score
# 750  <- very high! 75% of system RAM

# Step 3: Check if this is Java heap overuse:
jstat -gc $(pidof java) 1s 5
# S0C    S1C    S0U    S1U     EC       EU       OC       OU
# 512.0  512.0  0.0    512.0   4096.0   3800.0   8192.0   7000.0
# OC=Old Gen capacity 8192MB, OU=7000MB used (85% full!)
# + EU=Eden 3800/4096MB -> GC not keeping up

# Step 4: Check Kubernetes memory limits:
kubectl describe pod myjava-pod | grep -A5 "Limits"
# Limits:
#   memory: 2Gi  <- container limited to 2GB

# But Java heap is bigger than the limit?
# Java sees SYSTEM memory (say 16GB), sets default heap to 4GB
# Container memory limit is 2GB -> OOM kill!

# Fix: set explicit JVM heap flags:
# JAVA_OPTS="-Xms512m -Xmx1536m"
# Plus: -XX:+ExitOnOutOfMemoryError (fail fast instead of being killed)
# Plus: -XX:MaxMetaspaceSize=256m (bound metaspace too)

# Step 5: Verify after fix:
dmesg | grep oom   # should be quiet
kubectl top pod myjava-pod   # memory usage should stay < 2Gi

# Step 6: Protect from future OOM kills (systemd service):
# /etc/systemd/system/myapp.service:
# [Service]
# OOMScoreAdjust=-500   # harder to kill than normal processes
```

---

### Mental Model / Analogy

```
OOM Killer = emergency triage at an overflowing hospital

Hospital = Linux system
Memory = available beds
Patients = processes
Memory usage = how many beds each patient occupies

Normal operation:
  New patient arrives (malloc)
  Check available beds
  Assign bed (allocate physical page)
  
Bed shortage (memory pressure):
  Step 1: Move patients to outpatient care (swap to disk)
    vm.swappiness=60: balance between swapping and discharging
    vm.swappiness=1: discharge other patients first, keep serious cases
  
  Step 2: Discharge stable patients (evict page cache)
    File-backed pages = visitors with beds (can be asked to leave)
    Re-admitted easily (re-read from disk)
  
Critical shortage (OOM):
  Emergency protocol activated (OOM Killer)
  Triage officer (OOM killer) scores patients:
    Score = how many beds this patient is consuming
    oom_score = beds_used / total_beds * 1000
  
  oom_score_adj = priority card:
    -1000: VIP patient (never discharge, e.g., the hospital director)
           systemd sets this for init, ssh daemon
    +1000: "Send home first if beds needed" (batch job, temporary service)
    0: normal patient
  
  Triage officer selects HIGHEST SCORE patient:
    Kill (discharge) that patient
    Free up their beds (physical memory)
    Re-admit the patient who needed a bed (retry allocation)

cgroup memory.max = private ward with fixed beds:
  Kubernetes pod = private ward with 10 beds (512MB limit)
  Ward OOM: ward is full, triage within the ward only
  NEVER evicts patients from other wards (other pods)
  Global hospital beds unchanged
  
  This is WHY Kubernetes memory limits are important:
    Without limit: one leaking pod can trigger system-wide OOM
    With limit: pod OOM stays contained within that pod

vm.swappiness = preference for different bed types:
  Regular beds (RAM) = fast patient recovery
  Camp beds (swap) = slower, uncomfortable
  
  swappiness=0: only use camp beds when absolutely necessary
               (databases: keep buffer pool in regular beds)
  swappiness=60: balanced, use camp beds somewhat freely
  swappiness=200: aggressively move to camp beds to keep visiting room clear
               (page cache free for frequent visitors = file I/O intensive)
```

---

### Gradual Depth - Five Levels

**Level 1:**
OOM killer concept: kills processes when RAM is exhausted. `dmesg | grep oom`
to see kills. Check `oom_score` in `/proc/PID/oom_score`. Swap: extends RAM
to disk, but slower. `free -h` to see memory and swap usage.

**Level 2:**
`oom_score_adj`: protect processes (-1000) or target them (+1000). cgroup
`memory.max`: pod-scoped OOM limits. `vm.swappiness`: tune swap preference.
vmstat `si`/`so` for swap I/O. Memory overcommit concept. Kubernetes memory
requests vs limits.

**Level 3:**
OOM score calculation algorithm. Memory overcommit modes (0/1/2). `vm.overcommit_ratio`.
cgroup v2 `memory.high` (soft limit) vs `memory.max` (hard limit). Memory
events via `memory.events`. OOM notifier (oom_killer_adj). `vm.panic_on_oom`
for high-availability systems.

**Level 4:**
Kernel memory reclaim path: `__alloc_pages` -> zone watermarks -> reclaim ->
OOM. Zone watermarks: min, low, high. Kswapd daemon (background page reclaim).
Direct reclaim vs kswapd. Memory pressure notifications (cgroup v2
`memory.pressure`). PSI (Pressure Stall Information): `io`, `cpu`, `memory`
pressure files. NUMA OOM: node-local memory exhaustion triggers OOM even
if system has free memory on other nodes.

**Level 5:**
OOM killer source: `mm/oom_kill.c`. `oom_badness()` function. OOM notifier
chain: `register_oom_notifier()` for kernel drivers. Transparent Huge Pages
OOM interaction: 2MB THP allocation fails even with 1.5MB free. Cgroup v2
memory controller: LRU lists per cgroup. Container memory accounting: shared
libraries counted once vs per-process. `memfd_secret()`: allocations invisible
to OOM killer. ZRAM (compressed swap): swap pages to RAM (compressed). PSI
as Kubernetes eviction signal.

---

### Code Example

**BAD - OOM configuration mistakes:**
```bash
# BAD 1: Java process with default heap on constrained container:
# Pod YAML:
# resources:
#   limits:
#     memory: "2Gi"
# 
# Java launched with:
# java -jar app.jar   <- no heap flags!
# 
# JVM defaults: Xmx = 25% of system RAM = 25% of 16GB host = 4GB
# Container memory limit: 2GB
# Result: Java tries to allocate 4GB, gets OOM-killed at 2GB
# Error in dmesg: "Killed process XXX (java) ... anon-rss:2048MB"

# GOOD: Explicit JVM heap flags for containers:
# java -Xms256m -Xmx1536m \
#      -XX:MaxMetaspaceSize=256m \
#      -XX:+UseContainerSupport \   # JDK 10+: read cgroup memory limits
#      -XX:MaxRAMPercentage=75.0 \  # use 75% of container memory limit
#      -XX:+ExitOnOutOfMemoryError \  # fail fast, don't limp
#      -jar app.jar

# BAD 2: Not setting oom_score_adj for critical services:
# Critical database running with oom_score = 800
# Batch job also running with oom_score = 200
# Memory spike -> kernel kills the DATABASE (higher score)
# Entire application breaks

# GOOD: Protect critical services and target batch jobs:
# For the database (systemd service file):
# [Service]
# OOMScoreAdjust=-900   # very hard to kill

# For the batch job:
# [Service]
# OOMScoreAdjust=500    # preferred kill target

# Verify:
cat /proc/$(pidof postgres)/oom_score_adj   # should be -900
cat /proc/$(pidof batch)/oom_score_adj      # should be 500

# BAD 3: Ignoring vm.swappiness on database hosts:
# Default swappiness=60 on a PostgreSQL server
# Kernel decides to swap pg_shared_memory pages to disk
# Next query: page fault -> 50-200ms disk read to restore
# pg stat: "blk_read_time" in pg_stat_bgwriter increases
# Application sees random query latency spikes

# GOOD: Set swappiness for database workloads:
sysctl -w vm.swappiness=1    # temporary
echo "vm.swappiness=1" >> /etc/sysctl.d/99-postgres.conf
sysctl -p /etc/sysctl.d/99-postgres.conf    # persistent
```

**GOOD - OOM monitoring and prevention:**
```bash
# Monitor OOM events in real time:
monitor_oom() {
    echo "Monitoring for OOM events (Ctrl+C to stop)..."
    # Method 1: kernel ring buffer:
    dmesg -w | grep -i "oom\|killed" &
    
    # Method 2: journald:
    journalctl -k -f | grep -i "oom\|killed" &
    
    # Method 3: cgroup memory events for specific cgroup:
    local cgroup=${1:-$(cat /proc/self/cgroup | grep '^0::' | cut -d: -f3)}
    
    while true; do
        local oom_count=$(grep ^oom_kill /sys/fs/cgroup$cgroup/memory.events | awk '{print $2}')
        echo "$(date): cgroup oom_kill events: $oom_count"
        sleep 10
    done
}

# Set up OOM protection for all processes in a service group:
protect_service_from_oom() {
    local service_pattern=$1
    local adj_value=${2:--500}
    
    for pid in $(pgrep -f "$service_pattern"); do
        current=$(cat /proc/$pid/oom_score_adj 2>/dev/null)
        echo "PID $pid ($(cat /proc/$pid/comm)): $current -> $adj_value"
        echo "$adj_value" > /proc/$pid/oom_score_adj 2>/dev/null
    done
}

protect_service_from_oom "postgres" -900
protect_service_from_oom "redis-server" -800

# Check memory pressure using PSI (Pressure Stall Information):
cat /proc/pressure/memory
# some avg10=0.12 avg60=0.08 avg300=0.05 total=12345678
# full avg10=0.00 avg60=0.00 avg300=0.00 total=0
# 
# "some": at least 1 CPU stalled waiting for memory > 0% = memory contention
# "full": ALL CPUs stalled = severe memory pressure
# avg10=0.12: 0.12% of time in the last 10s, CPUs were stalled on memory
# Values > 5-10%: significant memory pressure, investigate

# Kubernetes: PSI is used as eviction signal
# Memory.pressure.some > threshold -> evict pods
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "The OOM killer always kills the right (guilty) process" | The OOM killer selects based on `oom_score` (memory usage), NOT on which process caused the OOM condition. If a batch job slowly leaks memory but the database has been running for hours accumulating working set, the database may have a higher `oom_score` and gets killed - even though it's the batch job's fault. The OOM killer has no knowledge of "who caused this." It's a heuristic: kill the biggest user. This is why `oom_score_adj` is critical: explicitly tell the kernel which processes are expendable (+1000) and which are critical (-1000). The killer is LAST RESORT, not a smart memory manager. |
| "vm.swappiness=0 means no swap is ever used" | vm.swappiness=0 does NOT completely disable swap. It means the kernel strongly prefers evicting page cache over swapping anonymous memory, but swap can still be used when all other reclaim fails. To completely prevent swap use: `swapoff -a` (disable swap devices) or set `memory.swap.max=0` in cgroup v2 (prevent swap for a specific cgroup). Note: kernel 5.8+ changed swappiness=0 behavior slightly - it now CAN swap if memory is truly critical. For Kubernetes nodes wanting zero-swap: both configure `swapoff` AND set `--fail-swap-on` kubelet flag to prevent accidental swap re-enabling. |
| "Memory limits in Kubernetes are like reservations" | Memory LIMITS and REQUESTS are different. `resources.requests.memory` = the MINIMUM guaranteed. The scheduler uses requests to decide which node has enough room. `resources.limits.memory` = the MAXIMUM allowed. Exceeding limits triggers OOM kill (cgroup `memory.max`). Exceeding requests does NOT trigger OOM - you can burst above requests (up to limits). If no limit is set: the process can use all node memory (limited by `oom_score` globally). Requests without limits = dangerous on shared nodes (no upper bound). Limits without requests = Kubernetes sets requests = limits (no burst capacity). Both set with requests < limits = burstable QoS class (can use more than reserved, but can be killed). |
| "After OOM kill, the system recovers immediately" | OOM kill is not atomic recovery. After killing a process: freed pages may take time to be returned to the pool (THP compaction, page cache accounting). If the OOM condition was severe, the system may immediately trigger another OOM kill cycle for a different process. In extreme cases: OOM kill cascade kills multiple processes before freeing enough memory. Additionally: the killed process may be a critical service daemon - `systemd` restarts it, but during restart: dependent services may fail. Applications that detect peer services are down start retrying, increasing memory pressure. OOM kill rarely "solves" the problem on its own - the root cause (memory leak, insufficient RAM, misconfigured limits) must be addressed. |

---

### Failure Modes & Diagnosis

**OOM diagnosis workflow:**
```bash
# Complete OOM investigation:

# Step 1: Confirm OOM kill happened:
dmesg | grep -B5 -A10 "Out of memory\|Killed process" | head -50
# Look for:
# [timestamp] oom-kill: constraint=CONSTRAINT_NONE...
# [timestamp] Out of memory: Killed process PID (NAME) total-vm:SIZE
# total-vm = virtual memory size (may be large due to JVM/overcommit)
# anon-rss = actual anonymous RAM used
# file-rss = file-backed RAM (page cache for this process)

# Step 2: Understand which cgroup triggered it:
# In dmesg: "task_memcg=/kubepods/pod123/container456"
# This tells you which pod/container was OOM-killed

# Step 3: Check Kubernetes events:
kubectl get events -n mynamespace --sort-by='.lastTimestamp' | grep -i oom
# LAST SEEN   TYPE      REASON    OBJECT    MESSAGE
# 5m          Warning   OOMKilled deployment/myapp   ...

# Step 4: Look at memory usage trends before OOM:
# Prometheus query (if available):
# container_memory_working_set_bytes{pod="mypod"} over past 1h
# Shows: steady increase? Sudden spike? Periodic growth?

# Step 5: Check current memory stats:
cat /proc/meminfo
# MemTotal:       32GB
# MemFree:        512MB  <- almost zero!
# MemAvailable:   1.2GB  <- includes reclaimable cache
# Cached:         8GB    <- page cache (reclaimable)
# SwapTotal:      8GB
# SwapFree:       100MB  <- swap almost full!

# Available vs Free:
# MemFree: physically free pages (0 overhead to use)
# MemAvailable: estimate including reclaimable cache
# Use MemAvailable, not MemFree, for "how much memory is left"

# Step 6: Find the memory-heavy processes:
ps aux --sort=-%mem | head -15
# Or with RSS in MB:
ps -eo pid,comm,rss --sort=-rss | head -10 | \
    awk '{printf "%d\t%s\t%.1fMB\n", $1, $2, $3/1024}'

# Step 7: Check per-process oom_score:
for pid in $(ps -eo pid --no-headers | head -20); do
    score=$(cat /proc/$pid/oom_score 2>/dev/null)
    comm=$(cat /proc/$pid/comm 2>/dev/null)
    adj=$(cat /proc/$pid/oom_score_adj 2>/dev/null)
    printf "%4d %s (adj=%s): %s\n" "$score" "$comm" "$adj" "$pid"
done | sort -rn | head -10
```

---

### Related Keywords

**Foundational:**
LNX-074 (Memory subsystem), LNX-072 (Cgroups)

**Builds on this:**
LNX-094 (Memory pressure diagnosis), LNX-086 (Kernel parameters tuning)

**Related:**
LNX-077 (CFS scheduler), LNX-075 (Transparent Huge Pages)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `cat /proc/PID/oom_score` | Current OOM score for process |
| `echo -1000 > /proc/PID/oom_score_adj` | Protect process from OOM kill |
| `dmesg \| grep -i oom` | Find recent OOM events |
| `cat /proc/meminfo` | Memory statistics |
| `cat /proc/pressure/memory` | PSI memory pressure |
| `cat /sys/fs/cgroup/.../memory.events` | OOM events per cgroup |
| `sysctl vm.swappiness` | Current swappiness value |
| `free -h` | Memory and swap usage summary |
| `vmstat 1 \| awk '$8>0'` | Show seconds with swap activity |

**3 things to remember:**
1. OOM killer kills highest `oom_score` (biggest RAM user), not the "guilty" process; use `oom_score_adj=-1000` to protect critical services
2. cgroup `memory.max` scopes OOM to within the cgroup; Kubernetes pod limits = cgroup limits = safe isolation
3. `vm.swappiness=1` for databases (avoid swapping working set); check `dmesg | grep oom` for OOM kills

---

### Transferable Wisdom

OOM killer heuristics appear in: JVM garbage collection (G1GC, ZGC kill
long-lived objects when heap pressure is high), Kubernetes pod eviction
(evicts Pods in order: BestEffort -> Burstable -> Guaranteed, similar to
OOM score ranking), database buffer pool management (PostgreSQL evicts pages
from shared_buffers in clock-sweep order - analogous to vm.swappiness-driven
reclaim). Memory pressure signals (PSI) are used in: Kubernetes eviction
manager (memory.pressure triggers pod eviction before OOM kill), Android
Low Memory Killer (LMKD - per-process OOM adj like Linux), ChromeOS tab
discarding. The `oom_score_adj` protection pattern: assign costs/priorities
to resources so the "least valuable" is sacrificed first. Same pattern as:
circuit breaker pattern (shed load from least-critical services), database
query priority (long-running queries killed before short interactive ones),
AWS Spot Instance interruption (cheapest instances terminated first). Platform
engineers: Kubernetes Guaranteed QoS class (requests = limits) sets
`oom_score_adj = -997` (high protection). Burstable QoS: lower protection.
BestEffort: highest OOM score = first to be killed. This maps directly to
the Linux OOM mechanism.

---

### The Surprising Truth

The Linux OOM killer has been called one of the most criticized subsystems
in the Linux kernel - and it was famously described by Linus Torvalds as
"fundamentally broken" in a kernel mailing list post. The core complaint:
the OOM killer kills processes REACTIVELY (after the system is in crisis)
rather than PROACTIVELY (before the crisis occurs). By the time OOM is
triggered, the system is often thrashing (doing little useful work, spending
all time on reclaim), and the kill may be too little, too late, or kill
the wrong process. The preferred alternative for production systems: NEVER
let the system reach OOM in the first place. This means: (1) Set proper
cgroup memory limits (kill within the cgroup before global OOM). (2) Use
`memory.high` (soft limit) to throttle before hitting `memory.max`. (3)
Monitor PSI `memory.some` and add capacity or restart services when it
rises. (4) For Kubernetes: configure proper Pod memory limits and use
VPA (Vertical Pod Autoscaler) to right-size them. The dirty secret:
many production Linux systems effectively have `vm.overcommit_memory=1`
(always allow allocation) meaning they CAN'T tell processes "no memory
available" - they just silently overcommit and eventually OOM-kill something.
This is why "I never run out of memory, it just crashes" is a common
experience: `malloc()` never returned NULL, but OOM killed the process
anyway.

---

### Mastery Checklist

- [ ] Can check `oom_score` and `oom_score_adj` for processes and protect critical services
- [ ] Can use `dmesg | grep oom` to find OOM events and interpret the output
- [ ] Understands `vm.swappiness` trade-offs: when to use 1 (databases) vs 60 (default)
- [ ] Can use cgroup `memory.max` and `memory.events` to diagnose container OOM
- [ ] Knows why cgroup-scoped OOM (Kubernetes limits) is safer than system-wide OOM

---

### Think About This

1. A Java microservice in Kubernetes runs fine for 24 hours then gets OOM-killed.
   The memory limit is 2Gi. You notice `memory.events` shows `high 15 max 3
   oom_kill 1`. Walk through your investigation: what does each event type mean,
   how would you use `jmap -heap` or JVM flags to diagnose the Java heap, what
   would you check in Prometheus to understand the 24-hour pattern, and what
   changes would you make to the JVM flags and Kubernetes resource spec?

2. A production database (PostgreSQL) server starts seeing query latency spikes
   (P99 increases from 5ms to 500ms) every few hours. `vmstat` shows `si` (swap
   in) values of 500-1000 pages/second during the spikes. Explain the exact
   mechanism: what is being swapped, why PostgreSQL's shared_buffers pages could
   end up in swap, why this causes latency, and what you'd change in `/etc/sysctl.d/`
   to prevent it.

3. Design the OOM protection strategy for a multi-service system with: (a) PostgreSQL
   database (cannot be killed), (b) Redis cache (restart-safe), (c) 3 web servers
   (restart-safe), (d) a batch processing job (expendable). Assign `oom_score_adj`
   values and explain the reasoning. How would you automate applying these scores
   when processes restart?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the Linux OOM killer and how does it decide which process to kill?
A: The Linux OOM (Out-Of-Memory) killer is a kernel subsystem that activates when the system cannot satisfy a memory allocation request after exhausting all other options (swap, page cache reclaim). The decision algorithm: each process has an `oom_score` (0-1000) representing roughly what percentage of total system memory it's using. Score calculation: (anonymous RSS + swap usage + pagetable memory) / total_memory * 1000, adjusted for shared memory. The process with the highest score (biggest memory user) is killed first. CUSTOMIZATION: `oom_score_adj` (-1000 to +1000) lets administrators influence the scoring. `-1000` = never kill (kernel exempts this process). `+1000` = always prefer killing (for expendable workloads). Set via `/proc/PID/oom_score_adj` or systemd unit's `OOMScoreAdjust=`. CONTAINER SCOPING: When cgroup `memory.max` is set, OOM within that cgroup kills only processes inside it (not system-wide). This is why Kubernetes memory limits protect other pods on the node - each pod has its own `memory.max` cgroup. DIAGNOSIS: `dmesg | grep -i oom` shows kill events with process name, PID, and memory usage. `cat /proc/PID/oom_score` shows current risk for any process. PRACTICAL: Never rely on OOM killer for memory management - prevent OOM via proper limits, monitoring PSI, and auto-scaling. OOM kills critical processes is a symptom of incorrect sizing or memory leaks.

**Expert:**
Q: Explain the vm.swappiness setting, why it matters differently for databases vs containers, and what happens at the memory reclaim level.
A: `vm.swappiness` (0-200) controls the kernel's RELATIVE PREFERENCE between two forms of memory reclaim: (1) swapping anonymous pages (process heap/stack) to disk, and (2) evicting file-backed pages (page cache) from memory. MECHANISM: The kernel maintains two LRU lists: anonymous LRU (heap, stack) and file LRU (cached files). The swap_tendency formula: `swap_tendency = mapped_ratio + (100 - vm.swappiness) / 2`. Higher swappiness = more willing to scan anonymous LRU and swap pages. Lower swappiness = prefer scanning file LRU and evicting clean cache pages. DATABASES (vm.swappiness=1): A PostgreSQL shared_buffers allocation or a JVM heap are anonymous memory. If the kernel swaps them to disk: the next access causes a hard page fault (100-500ms to swap back in). For a database query that should complete in 5ms, a swap-in causes a 100-500ms stall. `pg_stat_bgwriter.buffers_clean` increases as PostgreSQL must re-read blocks. Setting swappiness=1 says: "only swap when absolutely necessary." The database's working set stays in RAM. The trade-off: page cache is more aggressively evicted, so repeated file reads are slightly slower - acceptable for databases that manage their own buffer pool. CONTAINERS: Kubernetes nodes should use `vm.swappiness=0` and `swapoff`. Reason: container memory limits (`memory.max`) are meaningless if the container can swap beyond them. A container with `memory.max=512MB` but swap available can effectively use 512MB RAM + unlimited swap, violating the isolation guarantee. With swap disabled: when the container hits 512MB, OOM kill occurs immediately (predictable, contained). SWAPPINESS=200 USE CASE: Read-heavy workloads where page cache (hot files) is more valuable than heap. Aggressively swap out idle processes, keep frequently accessed files in page cache.
