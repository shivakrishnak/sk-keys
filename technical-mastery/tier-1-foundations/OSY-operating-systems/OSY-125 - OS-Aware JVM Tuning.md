---
id: OSY-125
title: OS-Aware JVM Tuning
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-085, OSY-099, OSY-116, OSY-120
used_by: []
related: OSY-116, OSY-120, OSY-126
tags:
  - JVM
  - tuning
  - NUMA
  - huge-pages
  - GC
  - container
  - OS-aware
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 125
permalink: /technical-mastery/osy/os-aware-jvm-tuning/
---

## TL;DR

JVM performance is deeply tied to OS behavior: NUMA topology
affects heap allocation latency, THP affects GC pause times,
cgroup limits affect -Xmx decisions, and CPU scheduler affects
GC pause predictability. OS-aware JVM tuning: use huge pages
for large heaps, pin JVM to NUMA node, set -Xmx relative to
cgroup limit (not host RAM), and disable THP for predictable GC.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-125 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | JVM tuning, NUMA, huge pages, GC, cgroup, OS-JVM interaction |
| **Prerequisites** | OSY-085, OSY-099, OSY-116, OSY-120 |

---

### JVM and NUMA Topology

```
NUMA (Non-Uniform Memory Access):
  Multi-socket servers: each CPU socket has "local" RAM
  Accessing local RAM: fast (< 100ns)
  Accessing remote RAM (cross-NUMA): slow (100-300ns)
  
  Example: 2-socket server (common in enterprise)
    Socket 0: CPUs 0-15, RAM 0-128GB
    Socket 1: CPUs 16-31, RAM 128-256GB
    
    JVM on CPUs 0-15: ideally uses RAM 0-128GB
    If JVM allocates on wrong NUMA node: 2-3x memory latency
    
JVM NUMA awareness:

  Default JVM (no NUMA flag): allocates heap anywhere
    GC threads may run on CPU 0 while heap pages are on Node 1
    Remote memory access during GC: increases GC pause
    
  JVM NUMA-aware (-XX:+UseNUMA):
    G1GC, Parallel GC: support UseNUMA
    Effect: prefer local NUMA node for heap allocation
    GC parallel tasks: distributed across NUMA nodes
    
  Command:
    java -XX:+UseNUMA -XX:+UseG1GC \
         -Xmx16g -jar app.jar
         
  Force NUMA binding (stronger):
    numactl --membind=0 --cpunodebind=0 java \
      -Xmx16g -jar app.jar
    # All memory AND CPUs from NUMA node 0 only
    # JVM cannot exceed node 0 memory
    # For 32GB node: max -Xmx is about 28GB (leave room for OS + native)
    
  NUMA-aware allocation test:
    numastat -p $PID
    # Shows: how much memory from each NUMA node
    # Healthy: most from local node
    # Problem: significant cross-node allocation
```

---

### Huge Pages and JVM GC Interaction

```
THP and G1GC regions:
  G1GC region size: 1MB-32MB (based on heap size)
  THP page size: 2MB
  
  When THP collapses 4KB pages to 2MB:
    G1GC holding many 4KB pages for a region
    THP: "I'll collapse these to 2MB for efficiency"
    Collapse: zero out new 2MB page, copy data
    Cost: per 2MB page collapse = CPU cycles
    Pattern: happens during GC pause (allocating new regions)
    -> Adds latency to GC pause
    
  For large heaps (> 8GB): THP collapser is active frequently
  Impact: GC pause spikes of 50-200ms from THP alone

Recommended JVM huge page configuration:

  Option A: Disable THP, use explicit huge pages (best for predictability)
  
    # Disable THP:
    echo never > /sys/kernel/mm/transparent_hugepage/enabled
    
    # Pre-allocate explicit huge pages:
    sysctl vm.nr_hugepages=16384  # 16384 * 2MB = 32GB
    
    # JVM: use explicit huge pages
    java -XX:+UseLargePages \
         -XX:LargePageSizeInBytes=2m \
         -Xmx30g -jar app.jar
    
    # Verify:
    grep HugePages /proc/meminfo
    # HugePages_Total: 16384
    # HugePages_Free: 1384  (most in use by JVM)
    
  Option B: THP madvise (compromise)
    echo madvise > /sys/kernel/mm/transparent_hugepage/enabled
    
    # JVM: explicitly request huge pages for heap
    java -XX:+UseTransparentHugePages \
         -Xmx16g -jar app.jar
    # JVM calls madvise(MADV_HUGEPAGE) on heap
    # Only JVM heap gets THP; other processes use 4KB pages
    # Reduces THP interference but doesn't eliminate it
    
  Huge pages and JVM startup:
    -XX:+AlwaysPreTouch: touch all pages at startup
    Combined with huge pages: all heap mapped at startup
    Effect: no page faults during runtime; predictable latency
    Cost: longer startup time; all pages pinned from start
    
  Java command with full OS-aware heap config:
    java \
      -XX:+UseG1GC \
      -XX:+UseNUMA \
      -XX:+UseLargePages \
      -XX:+AlwaysPreTouch \
      -XX:LargePageSizeInBytes=2m \
      -XX:InitiatingHeapOccupancyPercent=45 \
      -Xmx30g -Xms30g \  # same min/max: no heap resize
      -jar app.jar
```

---

### JVM in Containers (cgroup-Aware)

```
JVM < JDK 8u191 (old behavior - DANGEROUS in containers):
  Reads /proc/cpuinfo: sees ALL host CPUs
  Reads /proc/meminfo: sees ALL host RAM
  Sets default GC threads: based on host CPU count
  Sets default heap: based on host RAM
  
  Container with 4GB limit on 128GB host with 64 CPUs:
    JVM GC threads: 16-24 (based on 64 host CPUs, not 2 container CPUs)
    JVM default heap: 32GB (25% of 128GB, not 25% of 4GB)
    Result: JVM tries to use 32GB in 4GB container -> OOM
    
JDK 8u191+ / JDK 10+ (cgroup-aware - correct):
  -XX:+UseContainerSupport (default ON in JDK 8u191+)
  Reads cgroup cpu.quota / cpu.period: sees container CPU limit
  Reads cgroup memory.limit_in_bytes: sees container memory limit
  
  Container: 2 CPUs, 4GB RAM
  JVM cgroup-aware:
    GC threads: 2 (based on container CPUs)
    Default heap: 1GB (25% of 4GB container RAM)
    
  Explicit settings (always preferred over defaults):
    java \
      -XX:+UseContainerSupport \
      -XX:MaxRAMPercentage=75.0 \   # 75% of container memory
      -XX:InitialRAMPercentage=50.0 \
      -XX:MinRAMPercentage=50.0 \
      -XX:ActiveProcessorCount=2 \   # explicit CPU count
      -jar app.jar
      
  Calculation for 4GB container:
    MaxRAMPercentage=75.0: heap = 3GB
    Native memory budget: 4GB - 3GB = 1GB
    Thread stacks: 50 threads * 512KB = 25MB
    Metaspace: ~256MB default
    Off-heap (NIO): configure per app
    Total native: ~500MB < 1GB (safe)
    
  WARNING: MaxRAMPercentage=75 may be too high if:
    Many threads (large stack memory)
    Heavy Netty/NIO usage (large direct buffers)
    Large Metaspace (many classes, Spring auto-config)
    Use 65-70% if uncertain; monitor container RSS vs limit

JVM CPU tuning in containers:
  -XX:ActiveProcessorCount=N: explicit CPU count
  -XX:ParallelGCThreads=N: GC worker threads
  -XX:ConcGCThreads=N: concurrent GC threads (G1)
  
  Relationship:
    ConcGCThreads = max(1, ParallelGCThreads/4)
    ParallelGCThreads = max(8, ActiveProcessorCount * 5/8)
    
  For 4 vCPU container:
    ParallelGCThreads = max(8, 4 * 5/8) = max(8, 2) = 8
    But 4 vCPUs: 8 GC threads is too many!
    Explicit: -XX:ParallelGCThreads=4 -XX:ConcGCThreads=1
```

---

### OS Scheduler and GC Pause Predictability

```
Java GC stop-the-world (STW) pauses:
  GC must stop all application threads simultaneously
  Duration: depends on heap region being collected
  
  OS scheduler impact on STW:
    Application threads: must be preempted simultaneously
    OS might preempt a GC thread during STW
    If GC thread preempted: pause extends until it resumes
    
  Reducing scheduler impact:
    1. CPU pinning: GC threads on dedicated CPUs
       taskset -c 0-3 java ...  # pin JVM to CPUs 0-3
       Benefit: no CPU contention with other processes
       
    2. Real-time scheduling priority (use carefully!):
       sudo chrt -r 10 -p $PID  # set SCHED_RR priority
       Java flag: -XX:GCThreadPriority=-1 (max priority)
       WARNING: real-time priority can starve other processes
       Only for latency-critical JVMs on dedicated hosts
       
    3. CPU isolation:
       Kernel boot: isolcpus=4-7 (remove CPUs from OS scheduler)
       Start Java: taskset -c 4-7 java ...
       Result: CPUs 4-7 are ONLY for this JVM
       No other process will preempt GC threads
```

---

### OS-Aware JVM Checklist

| Setting | What to Check | Action |
|---------|-------------|--------|
| NUMA | `numactl --hardware` -> multiple nodes? | `+UseNUMA` flag |
| THP | `cat /sys/kernel/mm/transparent_hugepage/enabled` | Set to `madvise` or `never` |
| Huge pages | `grep HugePages /proc/meminfo` | Enable for heaps > 8GB |
| cgroup limits | Container? JDK < 8u191? | Upgrade JDK or set explicit flags |
| MaxRAMPercentage | Container memory limit? | Set 65-75% of container limit |
| AlwaysPreTouch | Latency-sensitive startup? | Enable for predictable latency |
| CPU pinning | Shared host? | taskset or isolcpus for dedicated CPUs |
| GC threads | Container vCPU count? | Explicit ParallelGCThreads |
