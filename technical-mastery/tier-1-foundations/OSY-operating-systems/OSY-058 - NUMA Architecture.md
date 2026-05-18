---
id: OSY-058
title: NUMA Architecture
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-054, OSY-011
used_by: OSY-088, OSY-093, OSY-120
related: OSY-059, OSY-088, OSY-093
tags:
  - NUMA
  - memory-topology
  - multi-socket
  - numa-aware
  - performance
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/osy/numa-architecture/
---

## TL;DR

NUMA (Non-Uniform Memory Access): in multi-socket servers,
each CPU socket has its own local memory bank. Accessing
local memory: ~100ns; accessing remote memory (other socket):
~300ns. NUMA-unaware applications silently pay 3x memory
latency. Java needs `-XX:+UseNUMA` to allocate heap memory
from the local NUMA node for each thread.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-058 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | NUMA, multi-socket, memory latency, UseNUMA, numactl |
| **Prerequisites** | OSY-054, OSY-011 |

---

### NUMA Topology Explained

```
Modern server: 2-socket NUMA (typical cloud VM is single-socket)
  
  Socket 0              Socket 1
  --------              --------
  Core 0                Core 8
  Core 1    ----QPI---- Core 9
  Core 2    (Intel UPI) Core 10
  Core 3                Core 11
  |                     |
  Memory 0              Memory 1
  (64GB)                (64GB)
  
  UPI (Intel Ultra Path Interconnect): ~100GB/s
  DDR4 local bandwidth: ~50GB/s per channel
  
Memory access latency:
  Core 0 -> Memory 0 (local):   ~70-100ns    (fast)
  Core 0 -> Memory 1 (remote): ~140-200ns   (slow, 2x)
  
  At 3GHz processor: 100ns = 300 clock cycles
  Remote: 600 clock cycles wasted per cache miss
  
  Impact on throughput:
    NUMA-local: 100% memory bandwidth
    NUMA-remote: ~50-60% bandwidth (limited by UPI)
  
Why NUMA exists:
  Alternative (UMA = Uniform Memory Access): all CPUs share
    one memory controller -> memory bus becomes bottleneck
    at 8+ cores. NUMA scales memory bandwidth with socket count.
```

---

### Checking NUMA Topology

```bash
# Show NUMA node count and CPU assignment:
numactl --hardware
# available: 2 nodes (0-1)
# node 0 cpus: 0 1 2 3 4 5 6 7  (8 physical cores)
# node 0 size: 65536 MB
# node 1 cpus: 8 9 10 11 12 13 14 15
# node 1 size: 65536 MB
# node distances:
# node   0   1
#   0:  10  21    <- local=10, remote=21 (2.1x slower)
#   1:  21  10

# Alternate: lscpu
lscpu | grep -i numa
# NUMA node(s):  2
# NUMA node0 CPU(s): 0-7
# NUMA node1 CPU(s): 8-15

# Show NUMA memory usage:
numastat
# Per-node: numa_hit, numa_miss, numa_foreign, local_node, other_node
# numa_miss: accesses that required remote memory fetch
# numa_foreign: memory allocated on this node but accessed remotely

# Monitor NUMA misses in real-time:
numastat -c -z  # -c = compact, -z = skip zero rows
```

---

### NUMA Anti-Patterns and Their Cost

```
Anti-Pattern 1: Memory bound to wrong NUMA node

  Default Linux policy: first-touch allocation
    Page allocated on the NUMA node of the CPU that first touches it
    
  Problem: if JVM started by Node 0 CPU, ALL heap allocated on Node 0
  When threads run on Node 1 CPUs (task migration or NUMA-unaware):
    ALL memory accesses = remote (2x slower!)
  
  Symptom: numastat shows numa_miss or other_node > 10%
  
Anti-Pattern 2: Thread migration across NUMA nodes

  Linux scheduler may migrate a thread from Node 0 to Node 1
    to balance CPU load (default autoNUMA behavior)
  Thread now has local CPUs on Node 1 but memory on Node 0
    -> All reads and writes from that thread = remote
  
  Diagnosis:
    perf stat -e node-loads,node-load-misses -p PID -- sleep 60
    node-load-misses / node-loads > 5-10% = problem

Anti-Pattern 3: Allocate-then-migrate (worst for databases)

  JVM startup: heap allocated on Node 0 (startup thread on Node 0)
  Application: spread across both nodes
  Memory accesses from Node 1 threads: all remote
  
  Cost example: 10GB heap, 50% remote access, 2x slower RAM:
    Effective RAM bandwidth halved
    GC pause times: double (GC touches all heap)
    L3 cache miss performance: 2x slower
```

---

### NUMA-Aware Configuration

```bash
# Pin entire JVM to one NUMA node (eliminates NUMA issues):
numactl --membind=0 --cpunodebind=0 java -jar app.jar
# Both memory and CPUs from node 0
# Loses 50% of CPU capacity on 2-socket server
# USE WHEN: single-node latency matters more than throughput

# Interleave memory across nodes (maximize total bandwidth):
numactl --interleave=all java -jar app.jar
# Each page allocated round-robin across nodes
# No locality but no remote-access penalty either
# USE WHEN: working set is larger than one node's memory

# Java NUMA-aware heap:
java -XX:+UseNUMA -XX:+UseParallelGC -jar app.jar
# UseNUMA: allocates Eden/Survivor spaces from local NUMA node
# Each thread's allocation buffer (TLAB) = local NUMA node memory
# Note: UseNUMA works with Parallel GC, G1, and ZGC
#   (not all GC collectors support NUMA equally well)

# Advanced: check if NUMA is being used:
java -XX:+UseNUMA -XX:+PrintGCDetails -jar app.jar 2>&1 | grep -i numa
# Should see: UseNUMA=true, NUMA node count reported
```

---

### Java NUMA Configuration Details

```java
// GC selection for NUMA:
//
// Parallel GC + UseNUMA:
//   Best NUMA support; each GC thread has NUMA-local memory
//   -XX:+UseParallelGC -XX:+UseNUMA
//
// G1GC + UseNUMA (Java 14+):
//   Improved NUMA support; regions allocated NUMA-locally
//   -XX:+UseG1GC -XX:+UseNUMA
//
// ZGC + NUMA (Java 14+):
//   Excellent: ZGC was designed NUMA-aware from start
//   -XX:+UseZGC  (NUMA enabled automatically)
//
// Shenandoah:
//   Some NUMA awareness but less than ZGC
//
// Check NUMA in action (add to JVM flags):
//   -Xlog:gc*:file=gc.log:time,level,tags
//   grep -i numa gc.log

// Production tuning: identify NUMA topology first
public class NumaInfo {
    public static void main(String[] args) throws Exception {
        // Java doesn't expose NUMA API directly
        // Use: numactl --hardware before starting JVM
        // Then set: -XX:+UseNUMA if multi-node
        ProcessBuilder pb = new ProcessBuilder("numactl", "--hardware");
        pb.redirectErrorStream(true);
        Process p = pb.start();
        System.out.println(new String(p.getInputStream().readAllBytes()));
    }
}
```

---

### NUMA in Cloud Environments

```
AWS instance types:
  m5.large, m5.xlarge, c5.large: single NUMA node
    (vCPUs from same socket, or single socket)
  m5.metal, c5.metal (bare metal): NUMA topology preserved
  m5.24xlarge: may have 2 NUMA nodes
    -> Check: numactl --hardware on instance
  
  For most cloud JVM workloads: single NUMA node = no issue
  For large bare-metal instances (96+ vCPUs): NUMA critical
  
  Rule of thumb:
    < 32 vCPUs: probably single NUMA node (don't worry)
    32-64 vCPUs: check numactl (could be 2 NUMA nodes)
    > 64 vCPUs: very likely multiple NUMA nodes (configure!)
    
Kubernetes + NUMA:
  Pod affinity: you cannot guarantee NUMA node in standard K8s
  TopologyManager: k8s 1.18+ feature
    Align CPU + memory resources to same NUMA node
    QoS class Guaranteed with exclusive CPUs required
  CPUManager: assign exclusive CPUs to container (no sharing)
  MemoryManager (k8s 1.21+): allocate memory from local NUMA node
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "NUMA only matters for HPC, not regular Java services" | Any multi-socket server running a Java service with significant memory traffic benefits from NUMA awareness. A 2-socket server with NUMA-unaware JVM can have all GC pauses doubled and memory throughput halved. It is common in enterprise servers (DB servers, payment processing, batch jobs) |
| "UseNUMA always improves performance" | UseNUMA helps when: threads are NUMA-local to their allocations. UseNUMA can HURT when: your GC is not NUMA-aware (e.g., old CMS GC), or when the heap is too small to span multiple nodes meaningfully. Always benchmark before enabling in production |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| Local vs remote latency | Local: ~100ns; Remote: ~200ns (2x penalty) |
| Check topology | `numactl --hardware` |
| JVM flag | `-XX:+UseNUMA` (works with Parallel, G1, ZGC) |
| numactl pin | `numactl --membind=0 --cpunodebind=0 java ...` |
| Cloud NUMA | Single socket most instances; bare metal may be multi-NUMA |
| numastat | Monitor numa_miss / other_node for remote access rate |
