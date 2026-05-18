---
id: OSY-088
title: NUMA Anti-Pattern
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-057, OSY-058, OSY-085
used_by: []
related: OSY-057, OSY-085, OSY-093, OSY-116
tags:
  - NUMA
  - anti-pattern
  - performance
  - memory
  - JVM
  - production
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 88
permalink: /technical-mastery/osy/numa-anti-pattern/
---

## TL;DR

NUMA anti-patterns cause 30-100% performance degradation on
multi-socket servers. Common anti-patterns: JVM heap allocated
on one NUMA node (startup thread first-touch), thread pool
mixed across nodes, and memory allocator ignoring NUMA topology.
Recognition and fix can double application throughput on
multi-socket machines.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-088 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | NUMA, anti-pattern, performance degradation, JVM tuning, memory topology |
| **Prerequisites** | OSY-057, OSY-058, OSY-085 |

---

### NUMA Refresher

```
NUMA (Non-Uniform Memory Access) in a 2-socket server:
  
  CPU 0 (8 cores)  ---  Memory Node 0 (128GB)
       |               |
  QPI/UPI link (cross-socket interconnect)
       |               |
  CPU 1 (8 cores)  ---  Memory Node 1 (128GB)
  
  Local access: CPU 0 reads from Node 0 memory
    Latency: ~70ns (normal DRAM)
    
  Remote access: CPU 0 reads from Node 1 memory
    Latency: ~120ns (cross-socket interconnect)
    Penalty: 1.7x slower per access
```

---

### Anti-Pattern 1: JVM First-Touch on Wrong Node

```
BAD: Default JVM startup (most common production mistake)
  
  Problem mechanism:
    1. JVM starts; main thread runs on CPU core 0 (Node 0)
    2. JVM allocates heap via mmap (virtual, no physical pages yet)
    3. JVM startup thread touches all heap pages (ClassLoader,
       runtime init, or -XX:+AlwaysPreTouch)
    4. Linux first-touch policy: physical pages on Node 0
    5. All heap pages allocated on NUMA Node 0
    6. JVM creates 16 worker threads (OS distributes to cores)
       - 8 threads on Node 0, 8 threads on Node 1
    7. Node 1 threads: ALL object access is remote (120ns latency)
    
  Result:
    50% of threads experience 1.7x memory latency for every
    object field access, array element access, or GC operation.
    Benchmark: 40% throughput reduction on a typical JVM workload.
    
  Symptom detection:
    numastat -p java
    Expected output if anti-pattern:
      Node 0:   3.8GB (local)    Node 1:   0.2GB (local)
      Node 0 remote: 0.1GB       Node 1 remote: 3.7GB ← BAD!
    
  Why it's hard to spot:
    - Application works correctly; just slower
    - no error, no warning
    - Degradation proportional to working set size
    - Worse on write-heavy workloads (cache coherency protocol)
    
GOOD: Fix 1 - numactl interleave
  
  numactl --interleave=all java -jar application.jar
  
  Effect: allocates pages round-robin across all NUMA nodes
  Result: Node 0 and Node 1 each get ~50% of heap pages
  Access: thread on Node 1 accesses 50% local, 50% remote
    (vs 100% remote without fix)
  Improvement: typically 30-50% throughput increase on NUMA servers
  
GOOD: Fix 2 - JVM NUMA-awareness
  
  java -XX:+UseNUMA -jar application.jar
  
  Effect: G1GC allocates regions per-thread (TLAB) on the NUMA
    node local to the allocating thread
  Result: threads allocate and initially access their own data locally
  Best for: applications where allocation and first use are on same thread
  Limitation: GC may move objects between nodes over time
```

---

### Anti-Pattern 2: Thread Pool Spanning NUMA Nodes

```
BAD: Shared thread pool across all CPUs
  
  Typical configuration:
    ThreadPoolExecutor pool = new ThreadPoolExecutor(
        32, 32, 0, SECONDS, new LinkedBlockingQueue<>());
    
  Problem: tasks execute on any available thread in the pool.
  If a task was allocated on Node 0, it may execute on Node 1.
  Memory access: all object accesses are remote (120ns).
  
  Worst case: producer allocates objects on Node 0 (request thread)
    Consumer thread pool: distributed across both nodes
    All consumption is remote for 50% of threads
    
GOOD: NUMA-local thread pools
  
  // Two pools, one per NUMA node
  // Pin threads to specific CPUs via JNI or library
  // (requires native thread affinity API in Linux)
  
  Practical alternative in Java:
    ForkJoinPool.commonPool() with -XX:+UseNUMA: uses NUMA-aware
    thread scheduling to prefer local memory access
    
  For critical paths: use Netty with NUMA-aware event loops
    Netty 4.x: EpollEventLoopGroup respects CPU affinity
    numactl --cpunodebind=0 <process> for pinning to one node
```

---

### Anti-Pattern 3: Memory-Intensive Native Code

```
BAD: JNI/native libraries ignoring NUMA
  
  RocksDB (Java), LevelDB, off-heap buffers (Netty's DirectBuffer):
    All use native malloc; default: glibc ptmalloc
    ptmalloc: NUMA-unaware; allocates on any node
    
  Problem: a Netty I/O worker thread on Node 1 allocates
    a DirectByteBuffer: Linux places it on Node 1 (ptmalloc local)
    Then: passes the buffer to a handler thread on Node 0
    Result: handler reads remote memory (all buffer accesses remote)
    
GOOD: Use jemalloc with NUMA support
  
  LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so java ...
  
  Or: use NUMA-aware allocators in native code directly:
    numa_alloc_onnode(size, node) - allocate on specific NUMA node
    numa_alloc_interleaved(size) - interleaved allocation
    
  For containers (single NUMA node per container):
    Docker: cpuset and memory pinning to one NUMA node
    --cpuset-cpus="0-7" --cpuset-mems="0"
    -> Eliminates cross-NUMA entirely (single node container)
```

---

### Detection Checklist

```
Step 1: Check server topology
  lscpu | grep NUMA
  numactl --hardware
  Look for: "NUMA node(s): 2" or more = NUMA server
  
Step 2: Check if JVM is NUMA-aware
  jcmd PID VM.flags | grep NUMA
  # Look for: -XX:+UseNUMA or absence of it
  
Step 3: Check current NUMA balance
  numastat -p java
  # Look for: large "other_node" value relative to total
  
Step 4: Monitor in production
  pidstat -p PID 1 | grep numa   # Linux 4.x+
  perf stat -e numa_miss,numa_hit -p PID -- sleep 30
  
Step 5: Fix and verify improvement
  # Before fix: numastat shows 40% remote access
  numactl --interleave=all java -jar app.jar &
  # After fix: numastat shows < 5% remote access
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "NUMA only matters for huge servers" | NUMA matters on any multi-socket server, including common 2-socket configurations (e.g., 2x Intel Xeon E5 = 2 NUMA nodes). A 64-core server with 2 sockets has NUMA. Even 30% remote access degradation on 64 cores is significant. |
| "JVM's G1GC handles NUMA automatically" | G1GC with -XX:+UseNUMA is NUMA-aware for heap region allocation. But WITHOUT this flag (default), G1GC is NUMA-unaware and first-touch determines physical placement. Default production JVM startup is NUMA-hostile. |
| "Containers solve NUMA problems" | Containers with default settings make NUMA worse: the container may be scheduled across NUMA nodes. FIX: pin containers to a single NUMA node with Docker `--cpuset-mems=0 --cpuset-cpus=0-7`. Then there's no cross-NUMA at all within the container. |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Diagnosis | Fix |
|---------|---------|-----------|-----|
| All heap on Node 0 | P99 latency 50-100% worse on NUMA server | `numastat -p java`: huge remote_node | `numactl --interleave=all` or `-XX:+UseNUMA` |
| Thread pool across nodes | Variable throughput; hard to reproduce | `perf stat numa_hit/miss`; `pidstat -p PID` | Pin pools per node; `-XX:+UseNUMA` |
| Off-heap NUMA mismatch | Netty/direct buffer latency high | `numastat`: remote node growing | `jemalloc` with NUMA support; pin container |
| Container NUMA split | Container processes run on both nodes | `docker stats`; `numastat` shows split | `--cpuset-cpus --cpuset-mems` to one node |

---

### Related Keywords

**NUMA concepts:** OSY-057 (NUMA architecture), OSY-058 (NUMA memory allocation)

**JVM intersection:** OSY-085 (OS-JVM interaction), OSY-125 (OS-aware JVM tuning)

**Related tuning:** OSY-093 (CPU affinity and pinning), OSY-116 (performance tuning framework)

---

### Quick Reference Card

| Question | Answer |
|----------|--------|
| Detect NUMA server | `lscpu \| grep NUMA` or `numactl --hardware` |
| Detect JVM NUMA issue | `numastat -p java`; look for remote_node |
| Quick fix | `numactl --interleave=all java -jar app.jar` |
| JVM flag | `-XX:+UseNUMA` (G1GC heap interleave) |
| Container fix | `--cpuset-cpus=0-7 --cpuset-mems=0` |
| Native alloc | `LD_PRELOAD=libjemalloc.so` or `numa_alloc_*` |
