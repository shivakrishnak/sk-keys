---
id: OSY-101
title: OOM Killer Analysis
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-070, OSY-091, OSY-100
used_by: []
related: OSY-100, OSY-102, OSY-105
tags:
  - OOM-killer
  - Linux
  - memory
  - diagnosis
  - oom_score
  - production
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 101
permalink: /technical-mastery/osy/oom-killer-analysis/
---

## TL;DR

The Linux OOM killer is invoked when memory is exhausted and
reclaim fails. It scores all processes by badness (RSS, swap,
priority) and kills the highest-scoring process. Engineers
must understand OOM selection algorithm, oom_score_adj tuning
(-1000 to +1000), and container OOM (Kubernetes eviction vs
OOM kill) to protect critical processes.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-101 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | OOM killer, oom_score_adj, badness score, container OOM, protection |
| **Prerequisites** | OSY-070, OSY-091, OSY-100 |

---

### OOM Killer Trigger Sequence

```
OOM kill is a last resort. Trigger sequence:
  
  1. Process tries to allocate memory
  2. Kernel checks: free pages available? -> NO
  3. Kernel tries to reclaim:
     a. Evict clean file cache pages
     b. Flush dirty pages and evict
     c. Swap anonymous pages (if swap enabled)
  4. After all reclaim attempts: still not enough memory?
  5. OOM killer activated
  
  OOM killer selects victim:
    Iterates all processes
    Computes badness score for each
    Kills the process with highest badness score
    
  Badness score formula (simplified):
    base = (process RSS + swap + page tables) / total_RAM * 1000
    Adjusted by:
      oom_score_adj (admin-set, -1000 to +1000)
      Root processes: slight reduction
      Children of the guilty process: higher score
    
  Final score: badness = base + oom_score_adj
    Score -1000: protected (never killed)
    Score 0: neutral (default)
    Score +1000: kill me first
```

---

### Detecting OOM Events

```bash
# Method 1: dmesg (most reliable)
dmesg | grep -i 'out of memory\|oom\|killed process'
# Output includes:
#   timestamp
#   "Killed process 12345 (java) total-vm:4194304kB, anon-rss:3145728kB"
#   OOM score: "oom_score_adj 0"
#   Which process triggered the OOM (not just the victim)

# Method 2: /var/log/syslog or /var/log/kern.log
grep -i oom /var/log/syslog | tail -20
grep -i 'killed process' /var/log/kern.log | tail -10

# Method 3: journald
journalctl -k | grep -i oom | tail -20
journalctl -k --since "1 hour ago" | grep -E 'oom|killed'

# Method 4: oom_kill metric (in kernel)
# Monitor continuously:
watch -n 5 'cat /proc/vmstat | grep oom_kill'
# vm.oom_kill: total OOM kills since boot

# Method 5: Container / Kubernetes
# Pod was OOM killed (exit code 137 = SIGKILL):
kubectl describe pod $POD_NAME | grep -A 3 "OOM\|exit code 137"
# Last State: OOMKilled = True
# Exit Code: 137

# Prometheus: node_vmstat_oom_kill counter
# Alert: increase in node_vmstat_oom_kill = OOM event
```

---

### oom_score_adj Tuning

```bash
# View current OOM score of a process:
cat /proc/$PID/oom_score      # actual score (0-1000)
cat /proc/$PID/oom_score_adj  # adjustment (-1000 to +1000)

# Protect a critical process:
# Set oom_score_adj to -1000 (never kill)
echo -1000 > /proc/$PID/oom_score_adj

# For a systemd service (persistent across restarts):
# In /etc/systemd/system/my-service.service:
# [Service]
# OOMScoreAdjust=-1000

# Make a process more likely to be killed first:
echo 500 > /proc/$PID/oom_score_adj

# Example protection strategy for a multi-service host:
# Critical: database, Kafka
# OOMScoreAdjust=-500 (protected, but not immune)
# Application servers:
# OOMScoreAdjust=0 (default, fair game)
# Batch workers:
# OOMScoreAdjust=500 (kill these first)
# Monitoring agent:
# OOMScoreAdjust=-200 (prefer to keep)

# Redis documentation: explicitly recommends
# oom_score_adj = -500 for production Redis
```

---

### Container OOM Kill vs Kubernetes Eviction

```
Two separate OOM mechanisms in Kubernetes:
  
  1. Container OOM kill (kernel-level):
     Trigger: container's memory.limit_in_bytes exceeded
     Mechanism: kernel OOM killer (cgroup-aware)
     Victim: process within the container with highest OOM score
     Signal: SIGKILL (exit code 137)
     Pod status: OOMKilled
     Restart: depends on restartPolicy (Usually: Always)
     
  2. Node memory pressure eviction (Kubernetes-level):
     Trigger: node MemAvailable < eviction threshold (default 100Mi)
     Mechanism: kubelet evicts pods based on QoS class
     Order: BestEffort -> Burstable -> Guaranteed (last)
     Signal: SIGTERM then SIGKILL after grace period
     Pod status: Evicted (not OOMKilled)
     Action: pod rescheduled on another node
     
  Kubernetes QoS classes:
    Guaranteed: requests == limits for ALL containers
      -> Protected from eviction (last to go)
    Burstable: requests < limits (partial guarantee)
      -> Evicted if using above requests under node pressure
    BestEffort: no requests/limits set
      -> Evicted first
      
  Best practice for production JVMs:
    Set Java requests == limits (Guaranteed QoS)
    Use MaxRAMPercentage=75 (leave headroom for native memory)
    Monitor: container_memory_working_set_bytes
    Alert: when > 85% of limit
    
  JVM in container (Java 11+):
    UseContainerSupport=true (default): reads cgroup limits
    MaxRAMPercentage=75:
      Container limit 4GB: heap max = 3GB
      Remaining 1GB: for metaspace, code cache, threads, GC
```

---

### OOM Killer in Production

```
Scenario: Java microservice OOM killed nightly

Investigation steps:
  1. Confirm OOM: dmesg | grep 'Killed process'
     -> Found: "Killed process 5432 (java)"
     
  2. Check what triggered it (not just victim):
     dmesg | grep -B 20 'Killed process 5432'
     -> Shows memory state at OOM time
     -> "oom-kill:constraint=CONSTRAINT_MEMCG"
     -> cgroup memory limit was exceeded (not host OOM)
     
  3. Check which cgroup:
     dmesg | grep 'oom_memcg='
     -> Container or cgroup name
     
  4. Check if it's heap or native:
     Before the kill: was heap at maximum?
     If heap < -Xmx and RSS > limit: native memory leak
     
  5. Common causes of nightly kills:
     a. Daily batch job: high memory workload at 2am
        Fix: memory-based autoscaling or increase limit
     b. Memory leak accumulating over the day
        Fix: heap dump analysis (schedule before nightly window)
     c. Redis BGSAVE fork + THP: 2x memory during backup
        Fix: disable THP; schedule BGSAVE with memory headroom
     d. GC needs 2x heap during full GC
        Fix: ensure free memory = heap * 1.5 at all times
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "The process that caused OOM is killed" | The OOM killer kills the process with the HIGHEST badness score, not necessarily the one that triggered the allocation failure. A small process triggering OOM might survive while a large, unprotected process (like a JVM with high RSS) gets killed instead. This is why oom_score_adj is critical. |
| "OOM kill means out of disk space" | OOM kill = Out Of Memory kill. Disk space is separate (df -h). OOM kill: process killed because RAM was exhausted. Disk full: file write returns ENOSPC error. Two completely different conditions. |
| "Container OOM kill = node is out of memory" | Container OOM kill is cgroup-scoped. If a container's memory.limit_in_bytes = 2GB and it exceeds 2GB, the kernel kills a process within THAT cgroup, even if the node has 100GB free. This is memory isolation, not actual system memory exhaustion. |

---

### Quick Reference Card

| Task | Command |
|------|---------|
| Find recent OOM kills | `dmesg \| grep -i 'killed process'` |
| View OOM score | `cat /proc/$PID/oom_score` |
| Protect a process | `echo -1000 > /proc/$PID/oom_score_adj` |
| Systemd protection | `OOMScoreAdjust=-1000` in service file |
| Kubernetes OOM status | `kubectl describe pod` -> OOMKilled |
| Container OOM metrics | `container_oom_events_total` (Prometheus) |
| Total OOM kills (kernel) | `cat /proc/vmstat \| grep oom_kill` |
