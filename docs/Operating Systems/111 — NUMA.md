---
layout: default
title: "NUMA"
parent: "Operating Systems"
nav_order: 111
permalink: /operating-systems/numa/
number: "0111"
category: Operating Systems
difficulty: ★★★
depends_on: Virtual Memory, Cache Line, Context Switch
used_by: JVM GC tuning, Database buffer pools, HPC, Kubernetes NUMA-aware scheduling
related: False Sharing, Cache Line, UMA, CPU affinity, numactl
tags:
  - os
  - hardware
  - memory
  - performance
  - deep-dive
---

# 111 — NUMA

⚡ TL;DR — NUMA (Non-Uniform Memory Access) means different CPUs in a multi-socket server have different latency to different memory banks; ignoring topology causes invisible 2–4× slowdowns.

| #0111           | Category: Operating Systems                                                 | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Memory, Cache Line, Context Switch                                  |                 |
| **Used by:**    | JVM GC tuning, Database buffer pools, HPC, Kubernetes NUMA-aware scheduling |                 |
| **Related:**    | False Sharing, Cache Line, UMA, CPU affinity, numactl                       |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT (SMP / UMA):
Symmetric Multi-Processing (SMP) with Uniform Memory Access: all CPUs share one memory bus to one memory bank. Every CPU has the same latency to any address. Easy to program — no memory placement decisions needed.

THE BREAKING POINT:
A server with 32 cores sharing one memory bus hits a bandwidth bottleneck. The bus becomes the bottleneck, not the CPUs. Scaling past ~8 cores on a single bus requires multiple memory banks. The only question is: how do you connect them?

THE INVENTION MOMENT:
NUMA connects each CPU socket to its own local memory bank, with inter-socket links (HyperTransport for AMD, QPI/UPI for Intel) for cross-socket access. Local memory: 60–80ns latency, full bandwidth. Remote memory (other socket): 120–160ns latency, shared bandwidth. This scales to 256+ cores — but now latency is non-uniform, and the OS and application must know about it.

### 📘 Textbook Definition

**NUMA (Non-Uniform Memory Access)** is a multi-processor memory architecture where memory access latency depends on the physical location of the memory relative to the accessing CPU. A NUMA system has multiple **nodes**, each containing one or more CPUs and a portion of system RAM (**local memory**). A CPU accesses its local memory with lower latency and higher bandwidth than it accesses **remote memory** (memory attached to another node). The OS exposes NUMA topology via `/sys/devices/system/node/` and tools like `numactl`, and optionally allocates memory on the node nearest to the accessing CPU (**NUMA-local allocation**).

### ⏱️ Understand It in 30 Seconds

**One line:**
In a multi-socket server, RAM next to your CPU is fast, RAM next to the other CPU is 2–4× slower — NUMA-aware code always uses local RAM.

**One analogy:**

> Your office has two desks (CPUs) with their own file drawers (local memory). Grabbing a file from your own drawer takes 10 seconds (60ns). Grabbing a file from the other desk's drawer takes 25 seconds (150ns) — you have to walk over and ask. If you spend all day grabbing files from the wrong drawer, you're 2.5× slower. Solution: keep your files in your drawer.

**One insight:**
The latency difference (1.5–4×) is invisible in profilers that don't attribute memory latency by NUMA node. A 30% throughput degradation in a JVM application running on a NUMA server can often be fully explained by NUMA-remote memory accesses in the GC allocator.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Each NUMA node has: local CPUs, local DRAM, local L3 cache (often).
2. Inter-node links have bandwidth limits — remote accesses compete for link bandwidth.
3. OS default allocation policy: allocate on the node of the first-touching thread.
4. Context switches can move a thread to a different NUMA node, making previously-local memory now remote.

DERIVED DESIGN:
The OS NUMA allocator (Linux: `libnuma`, `mbind()`, `set_mempolicy()`) attempts **first-touch allocation**: the first thread to access a page determines its NUMA node. For a thread pool, if the OS scheduler migrates threads across nodes (context switch to a different CPU socket), their heap memory remains on the original node — now all accesses are remote. NUMA-aware applications: (1) pin threads to specific NUMA nodes (`numactl --cpunodebind=0`), (2) allocate memory from the same node as the operating thread (`numactl --membind=0`), (3) pre-touch memory from the thread that will use it.

THE TRADE-OFFS:
Gain: Scales to 100+ cores without single memory bus bottleneck; full bandwidth per node.
Cost: Remote accesses significantly slower; thread migration can silently cause remote accesses; interleaved workloads (random shared data) can't benefit from locality; OS/application complexity to manage placement.

### 🧪 Thought Experiment

SETUP:
2-socket server: Node 0 (CPUs 0–15, 64GB RAM), Node 1 (CPUs 16–31, 64GB RAM). JVM starts on CPUs 0–15, allocates heap on Node 0.

NORMAL OPERATION:

- All JVM heap accesses: CPU 0–15 → Node 0 → 60ns → excellent
- GC runs: G1 GC threads (0–15) scan heap on Node 0 → local → fast

NUMA FAILURE MODE:

- Kubernetes migrates a Pod to CPUs 16–31 (Node 1)
- JVM heap is still on Node 0 (pre-allocated, not migrated)
- Every object access: CPU 16–31 → cross-link → Node 0 → 150ns
- 2.5× memory latency → GC pauses increase by 2–3× → stop-the-world pauses spike
- Application appears to degrade without any code change

THE INSIGHT:
This is the silent NUMA problem: everything looks fine in CPU utilization and GC counters until you check `numastat -c <PID>` and see 90% remote hits.

### 🧠 Mental Model / Analogy

> NUMA is like a two-floor library. The first floor (Node 0) has Reference A–M; second floor (Node 1) has Reference N–Z. Librarians on the first floor (CPUs) can instantly grab A–M books. N–Z requires climbing stairs. If you're studying only A–M, stay on the first floor. If your work was moved to the second floor but your books are on the first floor, you spend half your time on the stairs.

> The `numactl` tool is like having a librarian who keeps your books on the same floor as your desk.

Where the analogy breaks down: unlike floors of a library, you can interleave NUMA memory across nodes (`--interleave=all`) to spread the load — useful when random access patterns mean no single node has all your data.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Modern servers have multiple CPU chips. Each chip has its own RAM block. Accessing RAM "owned" by the other chip is slower. Software that ignores this runs 1.5–4× slower than it could. NUMA-aware software keeps each CPU working in its own RAM region.

**Level 2 — How to use it (junior developer):**
On production: check NUMA topology with `numactl --hardware`. Run JVM workloads with `numactl --cpunodebind=0 --membind=0 java ...` to pin to node 0. For Elasticsearch/Kafka, pin each JVM instance to one NUMA node and give it half the total heap. Use `numastat -c <PID>` to check remote hit ratio (should be < 10%). In Kubernetes, enable TopologyManager with `single-numa-node` policy for latency-sensitive pods.

**Level 3 — How it works (mid-level engineer):**
Linux NUMA policy is per-virtual-memory-area (VMA). `set_mempolicy(MPOL_BIND, nodemask, maxnode)` binds future allocations to specified nodes. `mbind(addr, len, MPOL_BIND, nodemask, maxnode, 0)` rebinds existing mappings (triggers page migration). `move_pages()` migrates specific pages between nodes. JVM options: `-XX:+UseNUMA` enables NUMA-aware allocator in HotSpot — each GC thread allocates in its local node's portion of the Eden space. Linux's `AutoNUMA` (kernel 3.8+) transparently migrates pages to the accessing node by detecting remote hits via hardware PMU counters.

**Level 4 — Why it was designed this way (senior/staff):**
NUMA topology is a direct consequence of the memory controller location choice: shared memory controller (UMA) → bus saturation at scale; per-socket memory controller (NUMA) → linear bandwidth scaling. The trade-off is correctness: UMA means any code is automatically NUMA-optimal; NUMA means any code is potentially NUMA-suboptimal unless explicitly managed. The OS attempts to hide this via AutoNUMA (transparent page migration) but at the cost of extra memory bandwidth for the access-pattern sampling. The "right" solution is application-aware NUMA: databases (Oracle, PostgreSQL, Cassandra) have explicit NUMA zone managers; JVM G1 has per-node regions. The long-term trend (AMD EPYC, Intel Xeon 3rd gen) is toward chiplet-based designs with multiple sub-nodes even per socket (NUMA within a socket), making NUMA topology even more important.

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────────┐
│                  DUAL-SOCKET NUMA TOPOLOGY                 │
├────────────────────────────────────────────────────────────┤
│  Socket 0 (Node 0)          Socket 1 (Node 1)             │
│  ┌───────────────────┐       ┌───────────────────┐        │
│  │ CPU 0–15          │◄─────►│ CPU 16–31         │        │
│  │ L3 Cache (32MB)   │ QPI   │ L3 Cache (32MB)   │        │
│  │ Memory Ctrl       │◄─────►│ Memory Ctrl       │        │
│  └────────┬──────────┘       └────────┬──────────┘        │
│           │ 60ns local                │ 60ns local        │
│  ┌────────┴──────────┐       ┌────────┴──────────┐        │
│  │    DDR5 64GB      │       │    DDR5 64GB      │        │
│  └───────────────────┘       └───────────────────┘        │
│                                                            │
│  CPU0 → Node0 mem: 60ns (local)                           │
│  CPU0 → Node1 mem: 150ns (remote, crosses QPI link)       │
└────────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

NUMA-AWARE JVM STARTUP:

```
numactl --cpunodebind=0 --membind=0 java -XX:+UseNUMA -Xmx56g App
  → OS: restrict CPUs to Node 0 (CPUs 0–15)
  → OS: allocate all memory from Node 0's 64GB
  → JVM: UseNUMA splits heap into per-node regions
  → G1 GC: allocates Eden regions from local NUMA node
  → GC threads: prefetch from local memory controller
  → All accesses: local → 60ns
  → Zero remote hits → maximum GC throughput
```

FAILURE PATH (thread migration without pinning):

```
JVM running on CPUs 0–15, heap on Node 0
  → OS load balancer migrates threads to CPUs 16–31
  → Heap stays on Node 0 (no page migration)
  → All heap accesses now remote: 150ns
  → GC pause times: 2–3× increase
  → Diagnosis: numastat -c <PID> → high remote ratio
  → Fix: re-pin with numactl or K8s topology policy
```

### 💻 Code Example

Example 1 — Check NUMA topology:

```bash
# Hardware topology
numactl --hardware
# Output: 2 nodes, node 0: cpus 0-15, mem 65536 MB
#                  node 1: cpus 16-31, mem 65536 MB
#         node distances: 0 1
#                       0: 10 21
#                       1: 21 10

# NUMA hit/miss ratio for running process
numastat -c $(pgrep -f MyApp)
# "Numa_miss" high = pages allocated remote → problem

# Real-time NUMA stats
watch -n 1 "numastat -c $(pgrep java)"
```

Example 2 — Pin JVM to NUMA node:

```bash
# Run Kafka broker pinned to NUMA node 0
numactl \
  --cpunodebind=0 \
  --membind=0 \
  java -server \
       -XX:+UseNUMA \
       -XX:+UseG1GC \
       -Xms28g -Xmx28g \
       -cp kafka.jar kafka.Kafka server.properties

# Verify with numastat after startup
numastat -c $(pgrep -f kafka.Kafka)
```

Example 3 — Java NUMA-aware allocation (-XX:+UseNUMA):

```java
// With -XX:+UseNUMA, HotSpot G1 creates per-NUMA-node regions
// No code change needed — JVM handles placement
// BUT: heap is split proportionally to NUMA nodes
// If 2 nodes, G1 allocates 50% of Eden on each node
// Threads on Node 0 get Node 0 Eden regions → local allocations
// This only works if JVM threads are pinned to consistent nodes!

// Force NUMA-local thread affinity in native code (Linux)
// (No standard Java API — use JNA or JNI)
/*
#include <numaif.h>
// Bind calling thread's future allocations to node 0
unsigned long nodemask = 1UL;
set_mempolicy(MPOL_BIND, &nodemask, sizeof(nodemask)*8);
*/
```

Example 4 — Kubernetes NUMA-aware pod scheduling:

```yaml
# kubelet config: enable NUMA-aware scheduling
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
topologyManagerPolicy: "single-numa-node"
topologyManagerScope: "pod"
---
# Pod requesting NUMA-local resources
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: latency-sensitive-app
      resources:
        requests:
          cpu: "8" # Must be whole NUMA-node CPUs
          memory: "32Gi" # Will be allocated on same NUMA node
        limits:
          cpu: "8"
          memory: "32Gi"
      # With single-numa-node policy: 8 CPUs + 32GB on SAME node
```

### ⚖️ Comparison Table

| Architecture                  | Access Latency       | Bandwidth Scaling    | Complexity      | Use For                |
| ----------------------------- | -------------------- | -------------------- | --------------- | ---------------------- |
| UMA (Uniform)                 | Equal for all        | Limited (shared bus) | None            | Up to ~8 cores         |
| **NUMA**                      | Non-uniform (1.5–4×) | Linear with nodes    | Medium          | 8–hundreds of cores    |
| NUMA within socket (AMD EPYC) | Multiple sub-nodes   | Very high            | High            | Latest-gen AMD servers |
| NUMA-aware app                | Minimal remote hits  | Near-local           | High (explicit) | Databases, HPC, JVM    |

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                       |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| "NUMA is only relevant for HPC or databases"                   | Any multi-socket server running JVM, Elasticsearch, or Kafka benefits significantly from NUMA-aware configuration                             |
| "Linux AutoNUMA handles this transparently"                    | AutoNUMA migrates pages but adds overhead; explicit pinning is always faster and more predictable                                             |
| "Interleaved allocation (-interleave=all) is the safe default" | Interleave helps random-access workloads but reduces throughput for sequential workloads vs strict local binding                              |
| "More sockets = more NUMA nodes (always)"                      | Modern AMD EPYC has multiple NUMA nodes per socket (NUMA within a die); topology can be complex                                               |
| "Setting -XX:+UseNUMA is enough"                               | UseNUMA only helps if JVM threads are actually running on consistent NUMA nodes; without CPU pinning, threads migrate and the benefit is lost |

### 🚨 Failure Modes & Diagnosis

**1. Silent NUMA Remote Hit Degradation**

Symptom: Java application has 2–3× worse GC pause times on production server vs local machine; CPU utilization looks normal.

Root Cause: Production server is multi-socket (NUMA); JVM heap allocated on Node 0, but OS migrated JVM threads to Node 1; all heap accesses are now remote.

Diagnostic:

```bash
# Check NUMA topology first
lscpu | grep -E "NUMA|Socket"

# Check hit/miss ratio for JVM process
numastat -c $(pgrep java)
# Numa_miss >> 0 = remote accesses happening

# Check which CPUs JVM is running on
ps -o pid,psr -p $(pgrep java) | head -5
# psr = processor; if scattered across sockets = problem
```

Fix: `numactl --cpunodebind=0 --membind=0 java ...` to pin to Node 0.

Prevention: Add NUMA topology check to deployment runbook; configure Kubernetes `topologyManagerPolicy: single-numa-node`.

---

**2. GC Thread NUMA Mismatch in G1**

Symptom: G1 GC pause times are good during warm-up but degrade after extended runtime.

Root Cause: `-XX:+UseNUMA` splits heap into NUMA regions, but application threads (not GC threads) started accessing cross-NUMA regions due to object graph traversal; GC threads working on remote regions.

Diagnostic:

```bash
# Enable GC logging with NUMA detail
java -XX:+UseNUMA -Xlog:gc+numa=debug -Xlog:gc -Xmx8g ...
# Look for: "NUMA allocation fail" or high remote access in GC logs
```

Fix: Review object layout — ensure hot objects are allocated on the same NUMA node as their accessing threads.

---

**3. Kubernetes Pod Eviction Due to NUMA Memory Pressure**

Symptom: Pod with NUMA-pinned memory (single-numa-node policy) fails to schedule or is evicted when the target NUMA node is memory-pressured even though total system RAM is available.

Root Cause: `single-numa-node` TopologyManager policy requires all resources on one node; if Node 0 has < 32GB free but Node 1 has 60GB free, a 32GB-requesting pod can't be placed on Node 0 and scheduling fails.

Diagnostic:

```bash
kubectl describe pod <pod-name>
# Look for: "Topology Affinity Error" or "TopologyAffinityError"
kubectl get node <node> -o json | \
  jq '.status.allocatable["memory"]'
# Check per-NUMA node availability: not available in standard kubectl
numactl --hardware  # on the host: check per-node free memory
```

Fix: Use `best-effort` TopologyManager policy for workloads that can tolerate cross-NUMA access; reserve `single-numa-node` for strict latency requirements.

Prevention: Monitor per-NUMA-node memory utilization; don't overcommit individual nodes.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — NUMA allocation determines which physical node backs virtual pages
- `Cache Line` — cache coherence across NUMA nodes is the primary latency driver
- `Context Switch` — thread migration across NUMA nodes makes previously-local memory remote

**Builds On This (learn these next):**

- `False Sharing` — false sharing across cache lines is compounded in NUMA; remote cache line ping-pong is even more expensive
- `Cache Line` — cache line ownership must be transferred across the inter-socket link on remote access

**Alternatives / Comparisons:**

- `UMA (Uniform Memory Access)` — single-socket or small multi-core servers; lower peak scaling but uniform latency
- `CPU affinity (taskset)` — CPU-level pinning; numactl also sets memory policy (more complete)
- `FPGA / GPU NUMA` — PCIe devices create their own NUMA-like non-uniform topology for GPU memory access

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multi-socket memory architecture where    │
│              │ local RAM is 1.5–4× faster than remote    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single memory bus can't scale to 100+     │
│ SOLVES       │ cores; NUMA enables linear scaling        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Thread migration = memory becomes remote  │
│              │ without any code change                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any production multi-socket server;       │
│              │ Elasticsearch, JVM, databases, HPC        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-socket servers: no NUMA to worry   │
│              │ about; unnecessary complexity             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Linear bandwidth scaling vs application   │
│              │ complexity to maintain locality           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Keep threads and their data on the       │
│              │  same CPU socket — or pay 2–4× latency"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ False Sharing → Cache Line → CPU affinity  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** AMD EPYC processors (Milan, Genoa) use a chiplet design where a single "socket" contains multiple Core Compute Dies (CCDs), each with their own L3 cache. Memory access between CCDs on the same socket has latency similar to cross-socket NUMA on Intel. Linux reports these as multiple NUMA nodes within a single socket. If you have a 2-socket EPYC 7763 (64 cores/socket, 8 CCDs/socket), how many NUMA nodes does the OS report, and what does this mean for `numactl --cpunodebind=0` — is node 0 a full socket or a single CCD?

**Q2.** Consider a Cassandra node (Java, G1 GC) with `-XX:+UseNUMA` on a 4-socket NUMA machine. Cassandra's Memtable (write buffer) is a concurrent skip list shared by all threads. When a write comes in, the Memtable entry is allocated on the NUMA node of the writing thread. When a read arrives (from a different thread on a different NUMA node), it traverses the skip list and hits entries scattered across all NUMA nodes. With `UseNUMA`, is G1 able to keep GC work local to each node for this workload? Design a NUMA-aware Memtable architecture that would preserve NUMA locality for both reads and writes.
