---
id: LNX-118
title: "cgroup Limits as SLA Contracts (Cross-Domain Transfer)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-057, LNX-117
used_by: LNX-119
related: LNX-057, LNX-117, LNX-119, LNX-120
tags: [cgroups, cgroup-v2, cpu-max, cpu-weight, memory-min, memory-max, memory-high, io-max, sla-contracts, qos, quality-of-service, resource-guarantee, resource-limit, kubernetes-requests, kubernetes-limits, connection-pool, thread-pool, rate-limiting, traffic-shaping, dscp, bandwidth-cgroup, resource-contention, noisy-neighbor, work-conserving, cpu-bandwidth, cfs-bandwidth, period-quota, systemd-slices, resource-model, minimum-guarantee, maximum-ceiling, sharing-policy]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 118
permalink: /technical-mastery/lnx/cgroup-limits-as-sla-contracts-cross-domain/
---

## TL;DR

**Meta-insight**: cgroup v2 resource limits are a precise implementation of
**SLA/QoS contract concepts** from networking, cloud computing, and operations.
The cgroup v2 model defines three components for any resource:
(1) **minimum guarantee** (floor): `cpu.weight` (CPU shares), `memory.min`
(guaranteed memory - never reclaimed even under pressure),
(2) **maximum ceiling** (cap): `cpu.max` (CPU bandwidth quota), `memory.max`
(hard OOM limit), `io.max` (I/O bandwidth limit),
(3) **sharing policy** (contention behavior): `cpu.weight` (proportional share
when CPU is contested). This **exact three-part model** appears everywhere:
Kubernetes `requests` (guarantee) + `limits` (ceiling) + priority class (sharing),
database connection pools `minIdle` (guarantee) + `maxActive` (ceiling) +
queue policy (sharing), thread pools `corePoolSize` + `maximumPoolSize` + rejection
handler, API rate limiting `burst` (peak) + `sustained` (floor) + queuing strategy,
QoS in networking (DSCP/WFQ: guaranteed bandwidth + peak bandwidth + drop policy).
Understanding cgroups = understanding resource management universally.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-118 |
| **Difficulty** | ★★★ Advanced (Pattern recognition) |
| **Category** | Linux |
| **Tags** | cgroups, SLA, QoS, resource management, Kubernetes, connection pool, rate limiting |
| **Prerequisites** | LNX-057 (cgroups), LNX-117 (namespace pattern) |

---

### The Problem This Solves

**The noisy neighbor problem**: In any multi-tenant system, an unrestricted
tenant can consume all shared resources, degrading everyone else's performance.
Without resource contracts: one busy container starves others; one heavy DB
query monopolizes connection pool; one API client exhausts rate limits. The
three-part contract (minimum + maximum + sharing) is the general solution.
Understanding cgroups deeply transfers directly to: Kubernetes capacity planning,
database connection pool tuning, thread pool configuration, API rate limit design.

---

### Textbook Definition

**cgroup (Control Group)**: A Linux kernel mechanism to limit, account for, and
isolate the resource usage (CPU, memory, disk I/O, network) of a collection of
processes.

**cgroup v2 (unified hierarchy)**: The unified cgroup hierarchy (kernel 4.5+,
recommended since 5.2). All resource controllers (cpu, memory, io, pid) operate
under one unified tree. Supersedes cgroup v1's separate hierarchies per controller.

**Resource contract components**:
- Minimum guarantee: the minimum amount of resource a cgroup is guaranteed even
  under system-wide resource pressure.
- Maximum ceiling: the hard upper limit on resource consumption, regardless of
  available capacity.
- Sharing policy: when resource is contested, how is it divided among competing
  cgroups (proportional share by weight).

---

### Understand It in 30 Seconds

```bash
# === cgroup v2 resource contract: three parts ===

# cgroup directory for a service:
ls /sys/fs/cgroup/myservice/
# cpu.max        <- MAXIMUM CEILING
# cpu.weight     <- SHARING POLICY (and minimum guarantee via proportion)
# memory.min     <- MINIMUM GUARANTEE
# memory.max     <- MAXIMUM CEILING
# memory.high    <- SOFT LIMIT (pressure trigger before OOM)
# io.max         <- I/O MAXIMUM

# ===== CPU: the three-part contract =====

# SHARING: when CPU is contested, myservice gets proportional share
cat /sys/fs/cgroup/myservice/cpu.weight
# 100  <- default weight (higher = more CPU when contested)

# If myservice.weight=200, other.weight=100:
# contested CPU: myservice gets 2/3, other gets 1/3
# (proportional allocation by weight)

# MAXIMUM CEILING: burst prevention (quota/period)
cat /sys/fs/cgroup/myservice/cpu.max
# 200000 100000
# ^quota  ^period (both in microseconds)
# "can use 200ms of CPU per 100ms period" = 2 vCPU maximum
# Even if 8 idle CPUs: capped at 2 vCPU (hard quota!)

# ===== Memory: the three-part contract =====

cat /sys/fs/cgroup/myservice/memory.min
# 536870912  <- 512MB: MINIMUM GUARANTEE
# "never reclaim this memory even under OOM pressure"

cat /sys/fs/cgroup/myservice/memory.high
# 1073741824  <- 1GB: SOFT LIMIT
# "above 1GB: throttle allocation, trigger reclaim"
# Processes slow down but don't die

cat /sys/fs/cgroup/myservice/memory.max
# 2147483648  <- 2GB: HARD MAXIMUM
# "above 2GB: OOM killer fires"

# ===== I/O: the three-part contract =====

cat /sys/fs/cgroup/myservice/io.max
# 8:0 rbps=104857600 wbps=52428800 riops=1000 wiops=500
# Device 8:0 (sda): read 100MB/s, write 50MB/s, 1000r IOPS, 500w IOPS

# ===== Kubernetes: SAME three-part model =====

# Kubernetes pod spec:
cat deployment.yaml | grep -A 10 resources:
# resources:
#   requests:            # = MINIMUM GUARANTEE
#     cpu: "500m"        # 0.5 vCPU guaranteed (cpu.weight proportioned)
#     memory: "256Mi"    # 256MB guaranteed (memory.min)
#   limits:              # = MAXIMUM CEILING
#     cpu: "2"           # 2 vCPU max (cpu.max = 200000 100000)
#     memory: "512Mi"    # 512MB max (memory.max = 536870912)

# Kubernetes Priority Class = SHARING POLICY
# PriorityClass: system-critical (value: 1000000000)
# PriorityClass: high (value: 1000)
# PriorityClass: low (value: 10)
# When node is CPU-contested: higher priority class gets preference

# ===== Connection pool: SAME three-part model =====

# HikariCP (Java connection pool):
# spring:
#   datasource:
#     hikari:
#       minimum-idle: 5           # MINIMUM GUARANTEE (always 5 ready)
#       maximum-pool-size: 20     # MAXIMUM CEILING (never more than 20)
#       connection-timeout: 30000 # SHARING POLICY (queue wait time)

# ===== Thread pool: SAME three-part model =====

# Java ThreadPoolExecutor:
# new ThreadPoolExecutor(
#     5,      // corePoolSize    = MINIMUM GUARANTEE (always 5 threads ready)
#     20,     // maximumPoolSize = MAXIMUM CEILING (never more than 20)
#     60, TimeUnit.SECONDS,      // SHARING POLICY (idle thread keepalive)
#     new LinkedBlockingQueue<>(100),  // queue policy when at maximum
#     new AbortPolicy()          // rejection handler (drop or wait)
# );
```

---

### First Principles

```
THE FUNDAMENTAL RESOURCE MANAGEMENT PROBLEM:

Shared resource R (CPU, memory, network bandwidth, DB connections, threads)
N competing consumers (C1, C2, ... CN)
Total capacity: T units of R

Without a contract: first-come-first-served
  C1 is busy: uses T units
  C2-CN: starved
  "Noisy neighbor" problem: one consumer degrades all others

Naive solution: strict equal division
  Each consumer gets T/N
  Problem: when C2-CN are idle, C1 can't use their quota
  "Work-non-conserving" = wastes capacity when consumers are quiet

The CORRECT solution: three-part contract
  MINIMUM GUARANTEE (G): each consumer gets at least G
    - Ensures no starvation under contention
    - G must be <= T/N (can't promise more than total)
  
  MAXIMUM CEILING (M): each consumer gets at most M
    - Prevents monopolization
    - M can be > T/N (can "burst" if others are idle)
  
  SHARING POLICY (W, weight): when contested, allocate proportionally
    - C1 has weight 200, C2 has weight 100
    - contested: C1 gets 2/3, C2 gets 1/3
    - "Work-conserving": idle consumer's share is redistributed
    - Only hits maximum ceiling when explicitly capped (cpu.max)

cgroup v2 CPU model:

    cpu.weight = sharing policy (proportional share under contention)
    cpu.max = $QUOTA $PERIOD
    "use at most QUOTA microseconds every PERIOD microseconds"
    QUOTA/PERIOD = max vCPU fraction (e.g. 200000/100000 = 2 vCPU max)
    
    "Minimum guarantee" for CPU: there is no memory.min equivalent for CPU!
    cpu.weight only guarantees proportional share UNDER CONTENTION.
    If CPU is idle: all consumers can use 100% (work-conserving).
    
    Implementation: CFS (Completely Fair Scheduler) + CFS bandwidth control
    cpu.weight -> CFS entity's weight -> scheduler time slices
    cpu.max -> CFS bandwidth pool: quota refilled every period
    When bandwidth pool exhausted: cgroup throttled until next period

cgroup v2 Memory model:

    memory.min = hard guarantee (never evict these pages)
    memory.low = soft guarantee (prefer not to evict below this)
    memory.high = soft limit (throttle allocation above this)
    memory.max = hard limit (OOM kill if reached)
    
    Memory guarantees work during global memory pressure:
    OOM killer: respects memory.min (won't take below min)
    kswapd (page reclaim): respects memory.low (prefers other cgroups)

THE THREE-PART CONTRACT PATTERN (generalized):

    Every resource management system that works correctly uses:
    
    | Component    | Purpose                            |
    | ------------ | ---------------------------------- |
    | Minimum (G)  | SLA floor: prevents starvation     |
    | Maximum (M)  | Cap: prevents monopolization       |
    | Policy (W)   | Fairness: proportional contention  |
    
    Without G: noisy neighbor starves well-behaved consumers
    Without M: one tenant can burst to monopolize
    Without W: equal division wastes idle capacity

MAPPING TO KUBERNETES:

    requests.cpu -> cpu.weight (proportional allocation in CFS)
    requests.memory -> memory.min (guaranteed pages)
    limits.cpu -> cpu.max (hard CPU quota)
    limits.memory -> memory.max (hard OOM limit)
    PriorityClass.value -> preemption priority (which pod loses resources first)
    
    QoS Class (determined by requests vs limits):
    BestEffort: no requests, no limits -> lowest priority, first to OOM
    Burstable: requests < limits -> some guarantee, can burst
    Guaranteed: requests == limits -> predictable, last to OOM
    
    "Guaranteed" QoS = cpu.max set to cpu.weight value
    (no burst allowed; requests == limits -> no headroom for burst)

MAPPING TO NETWORKING (QoS):

    DSCP (DiffServ Code Point): priority marking on IP packets
    Expedited Forwarding (EF): lowest latency, highest priority
    Assured Forwarding (AF): guaranteed bandwidth class
    Best Effort (BE): no guarantee
    
    These are the SHARING POLICY (W):
    EF packets: highest weight in WFQ (Weighted Fair Queuing)
    AF packets: medium weight
    BE packets: lowest weight
    
    Traffic shaping (Token Bucket):
    Token rate = MINIMUM GUARANTEE (sustained rate, tokens replenish)
    Burst size = MAXIMUM CEILING (burst capacity in tokens)
    When tokens exhausted: SHARING POLICY (queue or drop)
    
    Explicit analogy:
    cgroup cpu.weight 200 -> DSCP EF marking (high priority in contention)
    cgroup cpu.max 2.0 vCPU -> Token bucket: rate=2 vCPU (ceiling)
    cgroup memory.min 512MB -> Guaranteed bandwidth (AF PHB in MPLS)

MAPPING TO CONNECTION POOLS AND THREAD POOLS:

    HikariCP:
    minimum-idle = memory.min (always this many ready connections)
    maximum-pool-size = memory.max (never more)
    connectionTimeout = sharing policy (how long to wait for a connection)
    
    Java ThreadPoolExecutor:
    corePoolSize = memory.min (keep alive at minimum)
    maximumPoolSize = memory.max (never exceed)
    keepAliveTime = eviction policy (idle thread TTL, like page reclaim)
    queue = buffer (like memory.high: absorbs bursts before hard limit)
    rejectionHandler = OOM policy (what happens when queue is full)

MAPPING TO RATE LIMITING (API GATEWAY):

    Token bucket rate limiter:
    refill rate = MINIMUM GUARANTEE (sustained request rate)
    bucket capacity = MAXIMUM CEILING (burst allowance)
    "retry-after" header = SHARING POLICY (back-pressure signal)
    
    Token bucket is mathematically equivalent to CFS bandwidth:
    CPU tokens = bucket tokens
    cpu.max 200ms per 100ms = 2000 tokens per second (refill rate)
    "burst" = local token accumulation up to bucket capacity
    "throttle" = wait for token refill = CFS period end
```

---

### Thought Experiment

Designing a fair multi-tenant system from first principles:

```bash
# Scenario: three web services sharing a 4-core machine
# Service A: low-traffic (background jobs)
# Service B: medium-traffic (API server)
# Service C: high-traffic (critical user-facing)

# WRONG approach: equal division (4 cores / 3 services = 1.33 cores each)
# Problem: A and B are often idle; C needs bursting ability

# RIGHT approach: three-part contracts

# Service A (background):
mkdir -p /sys/fs/cgroup/service-a
# Weight = 100 (share: 100/800 = 12.5% when contested)
echo 100 > /sys/fs/cgroup/service-a/cpu.weight
# Max: can burst to 1 vCPU (uses idle capacity from B/C)
echo "100000 100000" > /sys/fs/cgroup/service-a/cpu.max
# Memory: guaranteed 256MB, max 1GB
echo 268435456 > /sys/fs/cgroup/service-a/memory.min  # 256MB
echo 1073741824 > /sys/fs/cgroup/service-a/memory.max # 1GB

# Service B (API server):
mkdir -p /sys/fs/cgroup/service-b
# Weight = 200 (share: 200/800 = 25% when contested)
echo 200 > /sys/fs/cgroup/service-b/cpu.weight
# Max: can burst to 2 vCPU
echo "200000 100000" > /sys/fs/cgroup/service-b/cpu.max
# Memory: guaranteed 512MB, max 2GB
echo 536870912  > /sys/fs/cgroup/service-b/memory.min  # 512MB
echo 2147483648 > /sys/fs/cgroup/service-b/memory.max  # 2GB

# Service C (critical user-facing):
mkdir -p /sys/fs/cgroup/service-c
# Weight = 500 (share: 500/800 = 62.5% when contested)
echo 500 > /sys/fs/cgroup/service-c/cpu.weight
# Max: can burst to 4 vCPU (full machine when others idle)
echo "400000 100000" > /sys/fs/cgroup/service-c/cpu.max
# Memory: guaranteed 1GB, max 3GB
echo 1073741824 > /sys/fs/cgroup/service-c/memory.min  # 1GB
echo 3221225472 > /sys/fs/cgroup/service-c/memory.max  # 3GB

# === What happens under load scenarios ===

# Scenario 1: Only C is busy (A and B idle)
# C can use ALL 4 cores (cpu.max=4 vCPU, others not using their quota)
# "Work-conserving": idle capacity redistributed to active cgroups

# Scenario 2: All three are busy simultaneously
# CPU shares: A gets 12.5%, B gets 25%, C gets 62.5%
# 4 cores contested: A=0.5 core, B=1 core, C=2.5 cores
# A is capped at 1 vCPU (cpu.max): A gets 0.5 (below cap, fine)
# B is capped at 2 vCPU: B gets 1 (below cap, fine)
# C is capped at 4 vCPU: C gets 2.5 (below cap, fine)
# Total: 0.5+1+2.5=4 cores - perfect utilization!

# Scenario 3: Memory pressure (OOM condition)
# OOM killer selection order: worst OOM score = most memory
# memory.min respected: A's 256MB protected, B's 512MB protected, C's 1GB protected
# OOM kills processes OVER their min, weighted by oom_score_adj

# === Verify with systemd (practical cgroup v2 management) ===

# systemd uses cgroup v2 slices:
systemctl set-property service-a.service CPUWeight=100 CPUQuota=100%
systemctl set-property service-b.service CPUWeight=200 CPUQuota=200%
systemctl set-property service-c.service CPUWeight=500 CPUQuota=400%
systemctl set-property service-a.service MemoryMin=256M MemoryMax=1G
systemctl set-property service-b.service MemoryMin=512M MemoryMax=2G
systemctl set-property service-c.service MemoryMin=1G MemoryMax=3G

# Verify effective settings:
systemctl show service-c.service -p CPUWeight,CPUQuotaPerSecUSec
# CPUWeight=500
# CPUQuotaPerSecUSec=4000000  <- 4000ms per second = 4 vCPU

cat /sys/fs/cgroup/system.slice/service-c.service/cpu.max
# 400000 100000  <- 400ms quota per 100ms period = 4 vCPU
```

---

### Mental Model / Analogy

```
cgroup contracts = Hotel room guarantees

Hotel resource: rooms (finite supply, say 100 rooms)
Multiple groups of guests: A (10 guests), B (30 guests), C (60 guests)
The hotel needs a fair policy.

BAD policy: first-come-first-served
  Group A books all 100 rooms (they arrived first)
  Groups B and C: no rooms! (noisy neighbor problem)

BAD policy: strict equal division (33 rooms each)
  Group B only has 20 guests: 13 rooms sit empty
  Group C has 60 guests: needs more rooms
  Can't use B's empty rooms -> waste! (not work-conserving)

GOOD policy: three-part contract

  Minimum guarantee:
  Group A: guaranteed at least 5 rooms (always reserved for them)
  Group B: guaranteed at least 15 rooms
  Group C: guaranteed at least 30 rooms
  Total reserved: 50 rooms (50 rooms "float" for bursting)

  Maximum ceiling:
  Group A: never more than 20 rooms (to prevent monopolization)
  Group B: never more than 40 rooms
  Group C: never more than 80 rooms
  (maximums can add up to >100 because they won't all hit max simultaneously)

  Sharing policy (when all 100 rooms are in demand):
  Group A: weight 100 -> 10% of contested rooms
  Group B: weight 300 -> 30% of contested rooms
  Group C: weight 600 -> 60% of contested rooms

  What this looks like in practice:
  
  Quiet evening (only 30 rooms needed):
  Each group gets what they need, minimum is guaranteed
  A uses 5 rooms, B uses 15, C uses 10 - total 30, 70 empty
  
  Busy weekend (all 100 rooms needed):
  A gets 10 (10% of 100, but bounded by max 20) -> 10
  B gets 30 (30% of 100, bounded by max 40) -> 30
  C gets 60 (60% of 100, bounded by max 80) -> 60
  Total: 100 = perfect utilization

Kubernetes translation:
  Pod requests.cpu = minimum room guarantee
  Pod limits.cpu = maximum room ceiling
  PriorityClass = group weight (sharing policy)
  
Connection pool translation:
  minimum-idle = guaranteed rooms (always ready)
  maximum-pool-size = maximum rooms (never exceed)
  connection-timeout = how long to wait for a room
  "Room service" = connection to database

Rate limiter translation:
  burst capacity = maximum ceiling (peak demand handled)
  sustained rate = minimum guarantee (always available)
  token refill rate = sharing policy (fairness over time)
```

---

### Gradual Depth - Five Levels

**Level 1:**
What cgroups are: kernel mechanism to limit process resource usage.
The two types: v1 (separate hierarchy per controller) and v2 (unified hierarchy).
Basic configuration: cpu.max (CPU limit), memory.max (memory limit). Container
runtime mapping: Docker --cpus=2 = cpu.max=200000/100000.

**Level 2:**
Three-part resource model: guarantee (min), ceiling (max), sharing policy (weight).
CPU: cpu.weight for proportional share, cpu.max for hard quota. Memory: memory.min
(hard guarantee), memory.high (soft limit, throttling), memory.max (OOM trigger).
I/O: io.max for per-device limits. Kubernetes requests/limits/PriorityClass mapping.

**Level 3:**
CFS (Completely Fair Scheduler) and CFS bandwidth control: how cpu.weight translates
to scheduler time slices (runtime entity weight). Bandwidth accounting: quota
consumed per period, refilled at period start, throttled when quota exhausted.
Memory pressure propagation: how memory.high triggers kswapd, how memory.min
protects pages during global OOM. systemd unit resource properties and their
cgroup mapping.

**Level 4:**
cgroup v2 I/O model: per-device limits in io.max. The difference between weight-based
I/O (io.weight) and rate-based (io.max). PSI (Pressure Stall Information): per-cgroup
resource pressure metrics (cpu.pressure, memory.pressure, io.pressure). How to use
PSI for autoscaling decisions. cgroup delegation: allowing non-root users to manage
sub-cgroups (systemd user instances). eBPF and cgroups: bpf-prog attached to cgroup
for per-cgroup network policy (cgroup BPF).

**Level 5:**
The fundamental work-conserving property: cgroups guarantee minimum and ceiling but
allow redistribution of idle quota. This is non-trivial for CPU: CFS bandwidth (cpu.max)
is NOT work-conserving by default when quota is exhausted (process is throttled even if
other cgroups have idle time). Solution: cpu.idle and cpu.burst (kernel 5.14+) for
controlled bursting. Memory.min is work-conserving (pages above min are reclaimable).
The PSI signal used for multi-resource scheduling decisions: how Google's resourced
daemon uses PSI to pre-empt cgroups under multi-dimensional pressure. The connection
to NUMA: memory.min guarantees don't specify which NUMA node's memory. NUMA-aware
cgroup allocation remains an open research area.

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "cpu.weight alone guarantees minimum CPU" | cpu.weight guarantees proportional share ONLY when CPU IS CONTESTED. When the system is idle: all cgroups can use 100% of CPU (work-conserving). When system load exceeds capacity: cgroups get proportional share based on weight. Example: weight=100 cgroup on a system with total weight=1000 gets ~10% of CPU UNDER CONTENTION. If system is at 20% load, that cgroup can use up to 20% (more than its proportional 10% share, because CPU is idle). To guarantee a minimum floor regardless of other cgroups: use cpu.max on OTHER cgroups (cap them) AND ensure your cgroup's cpu.weight share is sufficient. In practice: the Kubernetes requests.cpu = cpu.weight (proportional scheduling), limits.cpu = cpu.max (hard cap). A pod with requests.cpu=500m but NO limits.cpu: can use 100% if others are idle. A pod WITH limits.cpu=500m: capped at 500m even if 100 cores are idle. This is the requests vs limits semantic: requests = sharing, limits = ceiling. |
| "Kubernetes memory limits work the same as CPU limits" | CPU and memory have fundamentally different resource models. CPU is TIME-SHARING (elastic, flows in time). Memory is SPACE-SHARING (persistent, occupies space). CPU limit (cpu.max): when quota exhausted, process THROTTLED (pauses, waits for next period). Zero data loss. Memory limit (memory.max): when exceeded, OOM KILLER fires (process KILLED). Data loss if in-flight work discarded. This is why the guidance differs: CPU over-commitment is safe (worst case: slowdown). Memory over-commitment is risky (worst case: OOM kill in production). The operational difference: CPU limit = "don't monopolize" (throttle as protection). Memory limit = "don't exceed" (OOM kill as protection). The Kubernetes QoS classes exist because of this: "Guaranteed" QoS (requests=limits) means: predicatable CPU AND OOM-safe memory. "Burstable" QoS: CPU can burst (good), but memory can OOM if limit is too low (careful). |
| "cgroup v2 is just a new API for cgroup v1" | cgroup v2 is a fundamentally different architecture, not just a new API. cgroup v1 had SEPARATE hierarchies per controller: a process could be in one cgroup for CPU control and a DIFFERENT cgroup for memory control. This caused inconsistency: a container's CPU cgroup and memory cgroup could diverge. cgroup v2 uses a UNIFIED HIERARCHY: one tree, all controllers applied to the same cgroup. A process is in exactly one place in the hierarchy. This unification enables: (1) Coordinated pressure handling: when memory is under pressure, the cgroup that owns memory ALSO owns CPU, so the kernel can make holistic decisions. (2) PSI (Pressure Stall Information): cross-resource pressure metrics that make sense because all resources are in one hierarchy. (3) Delegation: non-root can manage subtrees consistently. The kernel recommendation since 5.2: use cgroup v2. Docker 20.10+ and Kubernetes 1.25+ default to cgroup v2. Key difference in practice: cgroup v1 cpu controller: cpu.shares (proportional, v2 uses cpu.weight). cgroup v1 memory limit: memory.limit_in_bytes (v2: memory.max). Command to check: stat -fc %T /sys/fs/cgroup/ (cgroup2 = v2, tmpfs = v1). |
| "Setting memory.max higher than physical RAM prevents OOM" | memory.max higher than physical RAM does NOT prevent OOM. When the sum of all cgroups' allocated memory exceeds available RAM + swap, the OOM killer fires regardless of memory.max settings. memory.max is a CEILING (max this cgroup can use), not a guarantee that memory is available. The OOM killer fires when: (1) A process tries to allocate memory AND (2) The system cannot reclaim enough memory AND (3) Swap is exhausted (or not configured). memory.max prevents ONE cgroup from monopolizing memory, but doesn't conjure memory from thin air. The interaction: if system total memory is 16GB and you set 10 cgroups each with memory.max=8GB, the total ceiling is 80GB but actual memory is 16GB. Under load, OOM will fire for processes that exceed their cgroup's ACTUAL share. The correct design: set memory.max based on realistic peak usage analysis, not "as high as possible." memory.min = realistic minimum needed. memory.max = 2-3x memory.min as burst headroom. memory.high = memory.max * 0.8 (soft limit to trigger reclaim before OOM). |

---

### Failure Modes & Diagnosis

```bash
# === Container throttled despite "idle" host ===

# Symptom: container is slow, host shows only 30% CPU usage

# Diagnosis: check if cgroup is throttled
# cgroup v2:
cat /sys/fs/cgroup/mycontainer/cpu.stat
# nr_throttled 15234      <- number of throttling periods
# throttled_usec 4521023  <- total microseconds throttled
# throttled_usec/nr_throttled = 296us per period throttled
# That's significant!

# Check CPU quota:
cat /sys/fs/cgroup/mycontainer/cpu.max
# 100000 100000  <- 100ms quota per 100ms period = 1 vCPU max
# Container is capped at 1 vCPU even if 8 cores are idle!

# Fix: increase cpu.max OR convert to cpu.weight-only
# (weight allows bursting when CPU is idle)
echo "max 100000" > /sys/fs/cgroup/mycontainer/cpu.max
# "max" = no ceiling, only weight-based scheduling

# For Kubernetes (set via requests/limits):
# Current: limits.cpu: "1" -> cpu.max=100000/100000
# Fix: increase limits.cpu: "4" or remove limits.cpu entirely

# Kubernetes: check if pod is being throttled:
kubectl top pod myapp-pod
# NAME          CPU(cores)   MEMORY(bytes)
# myapp-pod      998m         512Mi  <- 998 millicores = hitting 1 vCPU limit!

# Check with cAdvisor metrics (Prometheus):
# container_cpu_throttled_seconds_total{container="myapp"}
# container_cpu_throttling_ratio = throttled / (throttled + not throttled)
# If ratio > 0.25 (25%): investigate cpu.max settings

# === OOM kill diagnosis ===

# Process was OOM killed:
dmesg | grep -A 10 "Killed process" | tail -20
# [12345.678] Out of memory: Killed process 9876 (java) 
#   total-vm:8192000kB, anon-rss:4194304kB, oom_score_adj:0
# Killed!

# Check memory limits:
cat /sys/fs/cgroup/mycontainer/memory.max
# 536870912  <- 512MB limit
# Process used 4GB -> exceeded 512MB -> OOM killed

# Check memory usage over time:
cat /sys/fs/cgroup/mycontainer/memory.stat | head -20
# anon 4294967296   <- 4GB anonymous (heap) memory
# file 134217728    <- 128MB file cache
# kernel 16777216   <- 16MB kernel memory

# Fix: increase memory.max (if legitimate workload)
# OR: fix application memory leak (if unexpected growth)

# PSI (Pressure Stall Information) - proactive monitoring:
cat /sys/fs/cgroup/mycontainer/memory.pressure
# some avg10=0.50 avg60=0.10 avg300=0.02 total=45678
# "50% of the last 10 seconds, at least 1 task was stalled waiting for memory"
# High avg10 = memory pressure RIGHT NOW -> investigate before OOM

cat /sys/fs/cgroup/mycontainer/cpu.pressure
# some avg10=15.30 avg60=8.20 avg300=2.10 total=12345678
# "15.3% of last 10 seconds, at least 1 task was throttled waiting for CPU"
```

---

### Related Keywords

**Foundational:**
LNX-057 (cgroups internals), LNX-117 (namespace as address space)

**Builds on this:**
LNX-119 (Unix philosophy), LNX-120 (performance reasoning), LNX-121 (permission models)

**Related:**
LNX-117 (namespace pattern), LNX-120 (first-principles performance)

---

### Quick Reference Card

| cgroup v2 knob | SLA analog | Kubernetes analog |
|----------------|-----------|-------------------|
| cpu.weight | Proportional share | requests.cpu (scheduling) |
| cpu.max | Traffic shaping rate | limits.cpu |
| memory.min | Guaranteed bandwidth | requests.memory |
| memory.high | Soft SLA threshold | (no direct analog) |
| memory.max | Hard cap | limits.memory |
| io.max | I/O QoS ceiling | (no direct analog in K8s) |
| PSI | SLA violation signal | Custom Prometheus alerts |

**3 things to remember:**
1. Three-part resource contract: MINIMUM guarantee (floor, memory.min, requests), MAXIMUM ceiling (cpu.max, memory.max, limits), SHARING policy (cpu.weight, PriorityClass). Any resource management system that works correctly has all three. Missing one = either starvation (no min), monopolization (no max), or waste (no work-conserving sharing).
2. CPU is time-shared (throttle on over-limit, recovers next period). Memory is space-shared (OOM kill on over-limit, process dies). This is why CPU limits = safe over-commission, memory limits = risky. Set memory requests close to actual usage, limits 1.5-2x higher.
3. PSI (Pressure Stall Information): /sys/fs/cgroup/X/cpu.pressure and memory.pressure. avg10 > 20% = resource pressure happening NOW. Use PSI for proactive alerting before throttling or OOM becomes a problem.

---

### Transferable Wisdom

The three-part resource contract (minimum guarantee + maximum ceiling + sharing policy)
is the universal pattern for resource management. It appears in: TCP congestion control
(guaranteed minimum rate, max window size, AIMD sharing), HTTP/2 stream priority
(weight = sharing, priority = minimum guarantee), CPU scheduling (CFS weight + quota),
memory allocation (NUMA node affinity + max allocation), database transactions
(lock timeout = max wait, priority = sharing). Recognizing this pattern enables
cross-domain reasoning: debugging a throttled container (check cpu.max quota) is
cognitively identical to debugging a rate-limited API (check token bucket capacity)
or a starved thread pool (check corePoolSize). The diagnostic question is always:
"Which of the three parts is misconfigured - is the ceiling too low, the guarantee
too high, or the sharing policy unfair?" The operational implication: always configure
all three parts explicitly. Missing any one = undefined behavior under contention.
Operational pattern: START with conservative limits (lower ceiling), monitor PSI/throttle
metrics, relax ceiling as you understand workload. Don't start with high limits and
discover OOM kill in production.

---

### The Surprising Truth

The cgroup CPU bandwidth control (cpu.max, implementing the quota/period model) was
directly inspired by **network traffic shaping**. The engineers who designed it
explicitly borrowed the Token Bucket algorithm from networking: CPU time "tokens" are
refilled at a rate of QUOTA per PERIOD; when tokens are exhausted, the cgroup is
"throttled" (paused until next period). This is mathematically identical to a network
token bucket with rate=QUOTA/PERIOD and burst=QUOTA.

The implication: everything you know about network rate limiting (token bucket, leaky
bucket, burst capacity) directly applies to CPU cgroup bandwidth. And because the
same three-part model (guarantee + ceiling + sharing) is reused across CPU, memory,
I/O, and network, tuning a cgroup correctly teaches you to tune ALL resource-constrained
systems. The kernel engineers, by reusing the same conceptual model across resource
types, gave us a unified mental model for all resource management. The PSI
(Pressure Stall Information) metrics are the "SLA violation signal" that completes
the model: guarantee + ceiling + sharing + monitoring = complete resource contract.

---

### Mastery Checklist

- [ ] Can configure cpu.weight, cpu.max, memory.min, memory.max for a production service
- [ ] Understands the difference: cpu.weight = sharing policy, cpu.max = hard ceiling
- [ ] Knows Kubernetes requests/limits map to cgroup v2 knobs and their behavior
- [ ] Can read PSI metrics and interpret resource pressure signals
- [ ] Can explain the pattern in 3+ non-Linux contexts (connection pool, thread pool, rate limiter)

---

### Think About This

1. The Kubernetes QoS class system defines three tiers: Guaranteed (requests=limits),
   Burstable (requests<limits), BestEffort (no requests or limits). This maps directly
   to the three-part contract model, but with a twist: BestEffort pods have NO minimum
   guarantee and can be killed first under memory pressure. Analyze: what problem does
   BestEffort solve that wouldn't be solved by simply having low-weight Burstable pods?
   In what workload scenario is BestEffort the correct QoS class to use? (Hint: batch
   jobs, dev/test environments.) What are the risks of using BestEffort for production
   services and why do organizations often accidentally end up with BestEffort pods?
   (Hint: missing resource spec in deployment yaml.)

2. PSI (Pressure Stall Information) measures the percentage of time tasks are stalled
   waiting for a resource. It provides three averages: avg10, avg60, avg300 (10-second,
   60-second, 5-minute). This is analogous to load average in Linux (1, 5, 15 minutes).
   Design a container autoscaler that uses PSI signals rather than CPU percentage to
   trigger scaling. What are the advantages of PSI-based autoscaling over traditional
   CPU-utilization-based autoscaling? (Hint: CPU utilization can be 30% but PSI can
   show high stall time due to CPU throttling.) What PSI threshold would you use for
   scale-out trigger? How would you combine PSI across multiple resource types (cpu,
   memory, io) for a holistic scaling decision?

3. The token bucket model for CPU bandwidth (cpu.max) is NOT work-conserving: when
   a cgroup's quota is exhausted in a period, it CANNOT borrow unused quota from other
   cgroups (even if they're idle). But cpu.weight IS work-conserving (idle cgroups'
   shares are redistributed). This means: using cpu.max creates predictable but
   potentially wasteful scheduling. Using ONLY cpu.weight provides flexibility but no
   hard ceiling. Design the ideal CPU resource policy for: (a) a latency-sensitive
   payment processing service, (b) a batch ML training job, (c) a shared development
   environment. For each: which cgroup v2 knobs would you use and why? What are the
   trade-offs between predictability and efficiency in each case?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between Kubernetes requests and limits, and what Linux kernel mechanism implements each?
A: KUBERNETES REQUESTS vs LIMITS: Requests = minimum guarantee (floor). Limits = maximum ceiling. These map to different cgroup v2 mechanisms. REQUESTS.CPU: When the scheduler places a pod on a node, requests.cpu is used for NODE SELECTION (scheduler ensures node has enough unallocated CPU). At runtime, requests.cpu translates to cpu.weight (proportional CPU share in CFS). If system is idle: pod can use MORE than requests.cpu. Under contention: cpu.weight ensures proportional share. Example: requests.cpu=500m with total node weight=4000: this pod gets 500/4000 = 12.5% of CPU under full contention. LIMITS.CPU: Translates to cpu.max (CFS bandwidth quota). Hard ceiling: even if all other 16 cores are idle, pod capped at limits.cpu. Example: limits.cpu=2 -> cpu.max=200000/100000 (200ms quota per 100ms period = 2 vCPU). When quota exhausted: process throttled (pauses), waits for next period. REQUESTS.MEMORY: Used for scheduling (node selection) AND sets memory.min (guaranteed pages - kernel won't reclaim below this even under OOM pressure). LIMITS.MEMORY: Translates to memory.max. Hard ceiling: processes that exceed memory.max trigger the OOM killer and are killed. QoS CLASSES: Guaranteed (requests==limits): cpu.max set equal to cpu.weight denominator (no burst), memory.min==memory.max (no burst). Predictable, OOM-safe. Burstable (requests<limits): can burst to limits when resources available. BestEffort (no requests/limits): no cgroup limits set, first to OOM. PRACTICAL TUNING: Set requests = actual measured usage (p95 over 1 week). Set limits.cpu = 2-4x requests (allow bursting). Set limits.memory = 1.5-2x requests.memory (buffer against spikes). Never set limits.cpu too low: CPU throttling causes latency spikes (GC pauses, request timeouts) without any alerting.

**Expert:**
Q: Explain the three-part resource contract model and how it appears in cgroups, Kubernetes, connection pools, and networking QoS.
A: THE THREE-PART CONTRACT: Every resource management system that works correctly implements: (1) MINIMUM GUARANTEE: resource this consumer always gets, even under system-wide contention. (2) MAXIMUM CEILING: resource this consumer can never exceed, even when others are idle. (3) SHARING POLICY: when contested, how resource is divided among consumers proportionally. These three parts together solve the noisy neighbor problem while remaining work-conserving (idle capacity is redistributed). CGROUP V2 MAPPING: Minimum guarantee: memory.min (pages guaranteed under OOM), cpu.weight provides proportional share (not a hard floor, but ensures you get SOME CPU). Maximum ceiling: cpu.max (hard CPU quota), memory.max (hard OOM trigger), io.max (per-device I/O rate). Sharing policy: cpu.weight (proportional weight when contested), memory.high (pressure-based sharing signal). KUBERNETES MAPPING: Minimum guarantee: requests.cpu (scheduling), requests.memory (cgroup memory.min). Maximum ceiling: limits.cpu (cgroup cpu.max), limits.memory (cgroup memory.max). Sharing policy: PriorityClass (which pods lose resources first under pressure). HIKARICP CONNECTION POOL MAPPING: Minimum guarantee: minimum-idle (always this many connections ready). Maximum ceiling: maximum-pool-size (never more than this many connections). Sharing policy: connection-timeout (how long a thread waits for a connection from the pool). NETWORKING QoS (DiffServ): Minimum guarantee: Assured Forwarding (AF) guaranteed bandwidth per class. Maximum ceiling: peak rate limiting via token bucket. Sharing policy: DSCP marking + WFQ (Weighted Fair Queuing) weight. TOKEN BUCKET (rate limiting): Minimum guarantee: sustained refill rate (tokens per second). Maximum ceiling: bucket capacity (maximum burst). Sharing policy: queue-and-retry vs drop-on-overflow (backpressure vs shed load). WHY ALL THREE ARE NEEDED: Without minimum: noisy neighbor causes starvation (C consumes all; A starved). Without maximum: unlimited consumer monopolizes (one bad actor takes everything). Without sharing policy: equal division wastes idle capacity (C idle, A can't use C's capacity). The pattern insight: if you understand cgroup v2 tuning, you can tune connection pools, thread pools, and rate limiters using the same mental model. Debug cgroup throttling = debug connection pool exhaustion = debug API rate limiting: all follow the three-part contract diagnostic: which component (guarantee/ceiling/sharing) is misconfigured?
