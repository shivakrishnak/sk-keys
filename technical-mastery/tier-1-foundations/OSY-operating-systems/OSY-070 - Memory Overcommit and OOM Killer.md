---
id: OSY-070
title: Memory Overcommit and OOM Killer
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-012, OSY-054, OSY-057
used_by: OSY-091, OSY-100, OSY-101
related: OSY-057, OSY-091, OSY-101
tags:
  - OOM-killer
  - overcommit
  - vm.overcommit_memory
  - memory-pressure
  - oom_score_adj
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/osy/memory-overcommit-oom-killer/
---

## TL;DR

Linux memory overcommit lets processes allocate more virtual
memory than physical RAM. When physical RAM is actually
exhausted, the OOM (Out of Memory) killer selects a process
to kill using an `oom_score` algorithm (considers RSS, CPU
time, runtime). Redis requires `vm.overcommit_memory=1`
for fork()-based BGSAVE. Containers: OOM kill means
SIGKILL to the container, not just one process.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-070 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | OOM killer, overcommit, oom_score_adj, Redis, container OOM |
| **Prerequisites** | OSY-012, OSY-054, OSY-057 |

---

### Memory Overcommit Policy

```
vm.overcommit_memory (sysctl):
  0 (default - heuristic):
    Kernel uses heuristic to decide if allocation is safe
    malloc() of "reasonable" size: always allowed
    malloc() of all RAM at once: may be denied
    Problem: heuristic is unpredictable
    
  1 (always overcommit):
    Every malloc()/mmap() always succeeds regardless of free RAM
    Physical pages allocated lazily on first write (demand paging)
    Required for: Redis (fork() for BGSAVE needs to "succeed" immediately)
    Risk: system can silently commit 10x physical RAM
    
  2 (never overcommit):
    Total virtual memory <= physical RAM + swap * overcommit_ratio
    malloc() returns NULL when limit reached (fail fast)
    Used for: safety-critical systems that cannot be OOM-killed
    Rare in production (too restrictive for JVM and many libs)
    
vm.overcommit_ratio (only when overcommit_memory=2):
  Percentage of physical RAM allowed as overcommit
  Default: 50
  Total commit = RAM + swap_space * (overcommit_ratio/100)

Check current overcommit:
  cat /proc/sys/vm/overcommit_memory
  cat /proc/meminfo | grep -i commit
  # CommitLimit: max committed memory
  # Committed_AS: currently committed
```

---

### OOM Killer: Selection Algorithm

```
When physical RAM exhausted AND no more swap:
  Kernel invokes OOM killer
  
OOM Score calculation for each process:
  oom_score = (RSS in pages / total_pages) * 1000
  + adjustments for: swap usage, time running, forks
  
  Higher oom_score = MORE likely to be killed
  Kernel also considers: is this a system service? child of root?
  
  oom_score_adj: per-process adjustment (-1000 to +1000)
    -1000: completely immune from OOM kill
    -500:  strongly protected
    0:     default
    +500:  more likely to be killed
    +1000: always kill first
    
  Check:
    cat /proc/PID/oom_score        # current OOM score
    cat /proc/PID/oom_score_adj    # current adjustment
    
  Set (as root):
    echo -500 > /proc/PID/oom_score_adj  # protect this process
    echo +200 > /proc/PID/oom_score_adj  # sacrifice this process

Systemd services:
  OOMScoreAdjust=-1000 in service file -> never killed by OOM
  [Service]
  OOMScoreAdjust=-1000
  
Kubernetes:
  QoS Guaranteed: oom_score_adj = -998 (very protected)
  QoS Burstable: oom_score_adj = 2-999 (proportional)
  QoS BestEffort: oom_score_adj = 1000 (killed first)
```

---

### Redis and Overcommit

```
Why Redis needs vm.overcommit_memory=1:
  
  Redis BGSAVE: fork() to create child process
  fork() conceptually doubles memory requirement
  (parent + child both claim all of Redis's RSS)
  
  With overcommit_memory=0 (heuristic):
    If Redis RSS is 50% of RAM:
    fork() commit check: will this exceed RAM?
    Heuristic may say NO -> "Cannot allocate memory"
    BGSAVE fails -> no RDB snapshot
    
  With overcommit_memory=1:
    fork() always succeeds (virtual memory is free)
    COW ensures physical memory used only by dirtied pages
    BGSAVE creates snapshot without double-memory cost
    (unless high write rate during BGSAVE -> COW amplification)
    
  Redis startup warning:
    "WARNING overcommit_memory is set to 0. Background save may fail
    under low memory condition. To fix this issue add
    'vm.overcommit_memory = 1' to /etc/sysctl.conf"
    
  Set permanently:
    echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
    sysctl -p
```

---

### OOM in Containers and Kubernetes

```
Container OOM kill:
  cgroup memory.limit_in_bytes: hard memory cap
  When container exceeds limit: OOM killer fires
  
  Difference from bare metal:
    Bare metal OOM: kills one process, system survives
    Container OOM: cgroup OOM -> kills ALL processes in cgroup
    = kills the entire container (Docker exits, K8s restarts pod)
  
  Kubernetes OOM events:
    kubectl describe pod <name> | grep -A 5 OOMKilled
    # Containers:
    #   my-app:
    #     State:          Terminated
    #     Reason:         OOMKilled
    #     Exit Code:      137  (= 128 + 9 = SIGKILL)
    
  Exit code 137 = SIGKILL = OOM kill (or manual kill -9)
  
  Diagnosis:
    kubectl top pod <pod>    # current memory usage
    kubectl logs --previous  # logs before restart
    dmesg on node:
      OOM killer: "Out of memory: Killed process X java ..."
    
  Prevention:
    1. Set correct memory limits (profiling-based, not guessing)
    2. JVM: -XX:MaxRAMPercentage=75 (leave headroom for JVM non-heap)
    3. Monitor: container_memory_working_set_bytes vs limits
    4. Alert at 80% of limit
    
  Java-specific OOM:
    java.lang.OutOfMemoryError: Java heap space -> NOT container OOM
    (JVM's heap GC cannot free memory)
    java.lang.OutOfMemoryError: unable to create native thread
    (JVM exhausted system resources)
    Container OOM kill: no Java exception, just SIGKILL
    (no heap dump, no graceful shutdown - be aware!)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "OOM kill only happens when you have too many Java objects" | Java heap OutOfMemoryError and Linux OOM killer are completely separate mechanisms. Java heap OOM: JVM can't fit objects in heap (GC cannot free). Linux OOM kill: the entire process (or container) is SIGKILLed by the kernel when system RAM is exhausted. Container OOM kill produces no Java stack trace - the process just dies with exit code 137 |
| "vm.overcommit_memory=1 is dangerous and should never be set" | Overcommit=1 is the standard recommendation for Redis and is safe in practice because of COW. Virtual memory overcommit lets processes fork() without physical RAM doubling. The actual risk (OOM) is managed by setting appropriate cgroup limits and monitoring. Without overcommit=1, Redis BGSAVE reliability degrades |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| overcommit=0 | Heuristic (default); blocks "obviously" oversize allocations |
| overcommit=1 | Always allow; required for Redis fork() reliability |
| overcommit=2 | Strict cap; fail malloc() rather than OOM kill later |
| oom_score_adj | -1000 = immune; +1000 = first to die |
| Kubernetes OOM | Exit code 137; SIGKILL; no heap dump; pod restarts |
| JVM -XX:MaxRAMPercentage | Set heap relative to container limits (e.g., 75%) |
