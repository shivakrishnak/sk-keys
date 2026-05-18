---
id: OSY-137
title: Open Problems in OS Design
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-131, OSY-133, OSY-135, OSY-136
used_by: []
related: OSY-135, OSY-136, OSY-138
tags:
  - open-problems
  - research
  - OS-future
  - formal-verification
  - heterogeneous
  - security
  - frontier
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 137
permalink: /technical-mastery/osy/open-problems-os-design/
---

## TL;DR

OS research in 2024 is alive: key open problems include
formally verifying large kernels, managing heterogeneous
hardware (CPUs + GPUs + DPUs + FPGAs in one system),
achieving memory safety in kernel code without performance
loss, and scheduling for NVM (non-volatile memory that blurs
the line between storage and RAM). These unsolved problems
directly affect production Java services at the frontier.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-137 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | open problems, OS research, formal verification, heterogeneous computing, memory safety, NVM |
| **Prerequisites** | OSY-131, OSY-133, OSY-135, OSY-136 |

---

### Open Problem 1: Formally Verifying Large Kernels

```
Status: Partially solved (small kernels); unsolved (Linux)

What's been achieved:
  seL4 (2009): formal proof of microkernel correctness (~9000 lines)
  CompCert (2006): formally verified C compiler
  
What remains unsolved:
  Linux kernel: 30+ million lines of code
  No feasible path to formal verification at this scale
  
  Why it matters:
    Critical infrastructure (hospitals, power grids, aircraft):
    runs Linux; kernel bugs have life-or-death consequences
    
    Critical kernel bugs in recent years:
      Dirty COW (2016): privilege escalation in copy-on-write
      LogJam4 (2021): container escape via cgroups
      These: discoverable by formal methods if kernel were verified
      
Current research approaches:
  Rust in Linux kernel (merged 2022):
    Memory safety: Rust prevents use-after-free, buffer overflow
    NOT full verification: prevents a class of bugs but not all
    
  Bounded model checking:
    Check specific kernel functions, not entire kernel
    Tools: CBMC, VeriFast
    Limitation: cannot verify all possible execution paths
    
  Automated invariant discovery:
    Use static analysis to find likely bugs
    Tools: Clang Static Analyzer, Coverity
    Not formal proof but significantly reduces bug density
    
Why this will remain unsolved for years:
  Linux: adds 70,000+ patches per year
  Formal proofs: require stable code; hard to maintain with rapid change
  Economic incentive: Linux works well enough; ROI for full formal proof unclear
```

---

### Open Problem 2: Heterogeneous Hardware Management

```
Status: Active research area; no satisfying solution

Modern hardware landscape (a server in 2024):
  CPU: 32-128 cores (x86 or ARM)
  GPU: 4-8 GPUs (for ML inference)
  DPU (Data Processing Unit): network offload (SmartNIC)
  FPGA: custom logic acceleration (financial, networking)
  NVMe SSD: 10-20 million IOPS
  Optane (3D XPoint): byte-addressable persistent memory
  
  Each has: different programming model, memory model, failure mode
  
OS challenges:
  1. Unified address space across heterogeneous memory
     CPU DRAM: cache-coherent, NUMA-aware
     GPU HBM: separate memory, explicit transfer required
     Persistent memory (PMEM): byte-addressable but persistent
     
     How do you present these to applications transparently?
     Should Java heap span CPU DRAM + GPU HBM? How?
     
  2. Scheduling across processors
     Traditional: schedule threads on CPUs
     Modern: some work belongs on GPU; some on DPU; some on CPU
     Who decides? When? At what granularity?
     
  3. Cache coherence across processor types
     CPU cache hierarchy: coherent (same view of memory)
     CPU + GPU: different caches, no hardware coherence
     Explicit: copy-in / copy-out required
     Future: CCIX, CXL (Compute Express Link) for cache coherence
     
  Current workarounds:
    CUDA (NVIDIA): explicit GPU memory management
    OpenCL: vendor-neutral but complex
    SYCL, oneAPI: Intel's attempt at unified model
    Java: Panama project provides safe native memory access
    
  The open problem:
    A unified OS abstraction that lets applications
    express "this data should be on GPU memory" or
    "this function should run on the DPU" without
    application-specific knowledge of the hardware topology
```

---

### Open Problem 3: Memory Safety in Kernel Code

```
Status: Partial progress (Rust in Linux); fundamental tension unsolved

The problem:
  ~70% of Linux CVEs: memory safety issues
    Use-after-free, buffer overflow, null dereference, race conditions
    All preventable with memory-safe languages
    
  Why not rewrite Linux in Rust?
    Linux: 30M lines; 50+ years of optimized C code
    Full rewrite: impossible (Tanenbaum tried; Minix never replaced Linux)
    
Current approach: gradual Rust introduction
  Rust in Linux: approved for new drivers and subsystems (2022+)
  First Rust drivers: GPU drivers, Android Binder IPC
  
  Challenges:
    Unsafe Rust still allowed: kernel needs low-level access
    C-Rust interoperability: generating correct bindings
    Performance: Rust zero-cost abstractions; but proof...?
    
  Tension: unsafe code boundaries
    Kernel code MUST do unsafe things: modify page tables, handle hardware
    Rust's "unsafe" block: allows these; but marks the boundary
    Benefit: unsafe code is explicit, auditable
    Limitation: unsafe code can still have bugs
    
  eBPF as a partial answer:
    Run safe programs in kernel context (verified at load time)
    eBPF verifier: checks safety properties before execution
    Limitation: not general kernel code; restricted execution model
    
Research directions:
  Language-Based Security: Cyclone (C superset with checked pointers)
  Proof-Carrying Code: programs carry proofs of safety properties
  Capability Hardware: CHERI (pointer capabilities in hardware)
    CHERI: memory-safe pointer model at hardware level
    No language changes: existing C code becomes memory-safe
    Status: Research prototype; not in mainstream x86/ARM
```

---

### Open Problem 4: Scheduling for Non-Volatile Memory

```
Status: Early research; no production solution for Java

Traditional memory hierarchy:
  Register (< 1ns) -> L1 cache (1ns) -> L2 (4ns) -> L3 (12ns)
  -> DRAM (60-100ns) -> SSD (100us) -> HDD (10ms)
  
  Clear tier boundary: fast volatile (cache/DRAM) vs slow persistent (disk)
  OS design: assumes this boundary
  
Non-volatile memory (Optane, 3D XPoint, emerging NVM):
  Byte-addressable: can read/write with CPU load/store instructions
  Persistent: survives power loss
  Latency: ~200-300ns (between DRAM and SSD)
  
  This BREAKS the traditional assumption:
    DRAM: fast, volatile
    NVM: medium-fast, PERSISTENT
    NVM can be used as: extended RAM (large, cheaper) or fast storage
    
OS challenges for NVM:
  1. File system on NVM:
     Traditional FS: block interface; not optimized for byte-addressable
     NOVA, PMFS: experimental NVM-aware file systems
     Direct Access (DAX): bypass page cache, access NVM directly
     
  2. Java heap on NVM:
     Could store Java heap on NVM:
     After JVM crash: heap survives -> faster recovery
     Open question: how does GC work with persistent heap?
     References in heap: must still be valid after restart
     This requires: persistent memory transactional semantics
     
  3. Scheduling and persistence:
     Traditional: flush to disk = slow; deferred writeback acceptable
     NVM: persistence is instant (or nearly so)
     Does OS need to track "what has been persisted" differently?
     Store fences (CLFLUSH, CLWB) become performance critical
     
  Current Java state:
    Persistent collections on NVM: experimental (Pmem.io, LLPL)
    Main use: memcached-like cache that survives restarts
    No standard Java API; no mainstream adoption
    
  Research: 2024 state
    Intel Optane: discontinued 2022 (business reasons, not technical)
    But: NAND-based PM emerging; CXL memory pooling
    Long term: memory pools accessible over PCIe (CXL 3.0)
    This will require new OS scheduler awareness
```

---

### Open Problem 5: Scheduler for Diverse Latency Requirements

```
Current state: CFS scheduler (Linux) optimizes for throughput fairness
  Not designed for: mixing ultra-low-latency and batch workloads
  
Real-world tension:
  A Kubernetes node: running both
    Real-time payment processing: 1ms p99 SLO
    Batch analytics job: can use all available CPU
    
  Current solutions:
    CPU pinning + isolation (isolcpus): dedicates CPUs
    cgroup CPU quota: limits batch job
    Nice values: adjusts priority
    
  What's missing:
    Latency-aware scheduling: "ensure this thread gets CPU
    within 500 microseconds of being runnable"
    Current CFS: no such guarantee without real-time priority
    
  Research directions:
    BORE (Burst-Oriented Response Enhancer): improves interactivity
    Mainline Linux 6.6: Extensible Scheduler (sched_ext)
    sched_ext: allows BPF programs to implement custom schedulers
    -> First: allows experimentation without kernel patches
    -> Applications can specify their own scheduling policies via BPF
    
  Implication for Java:
    With sched_ext: JVM GC threads could specify:
    "preempt this thread only after 10ms; not in middle of STW pause"
    Currently: OS preempts GC threads like any other
    Future: GC-aware scheduling via BPF scheduler programs
```

---

### Why These Problems Matter for Java Engineers

| Problem | Current Impact | Future Impact |
|---------|---------------|---------------|
| Kernel verification | CVEs affect container security | Provably-safe kernel reduces attack surface |
| Heterogeneous HW | Java GPU (TornadoVM, CUDA) is complex | Unified API for CPU+GPU in Java |
| Memory safety | Kernel bugs cause JVM crashes | Rust kernel reduces JVM-killing kernel bugs |
| NVM scheduling | Experimental persistent Java heaps | Persistent heap recovery from crashes |
| Latency scheduling | GC pauses unpredictable under load | GC-aware scheduler prevents long pauses |
