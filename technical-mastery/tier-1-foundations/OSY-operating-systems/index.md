---
layout: default
title: "Operating Systems"
parent: "Technical Mastery"
nav_order: 3
has_children: true
permalink: /technical-mastery/osy/
---

# Operating Systems

Processes, threads, scheduling, virtual memory, I/O models,
file systems, synchronization primitives, and OS internals
for production engineers.

**Keywords:** OSY-001–OSY-143 (143 terms)

| ID | Keyword | Level | Difficulty | Tags |
|----|---------|-------|------------|------|
| OSY-001 | The Operating System Problem (Why OS Exists) | L0 | 🌱 | |
| OSY-002 | OS as the Hardware Abstraction Layer | L0 | 🌱 | |
| OSY-003 | Why Software Engineers Must Know OS Internals | L0 | 🌱 | |
| OSY-004 | Operating Systems Landscape (Linux, macOS, Windows, RTOS) | L0 | 🌱 | |
| OSY-005 | How OS Knowledge Impacts Application Performance | L0 | 🌱 | |
| OSY-006 | Process (Definition and Lifecycle) | L1 | ★☆☆ | |
| OSY-007 | Thread (Definition and vs Process) | L1 | ★☆☆ | |
| OSY-008 | System Call (the Kernel Gateway) | L1 | ★☆☆ | |
| OSY-009 | Kernel Space vs User Space | L1 | ★☆☆ | |
| OSY-010 | Context Switch | L1 | ★☆☆ | |
| OSY-011 | CPU Scheduling Overview | L1 | ★☆☆ | |
| OSY-012 | Virtual Memory Concept | L1 | ★☆☆ | |
| OSY-013 | Memory Management Unit (MMU) | L1 | ★☆☆ | |
| OSY-014 | File System Overview | L1 | ★☆☆ | |
| OSY-015 | Blocking vs Non-Blocking I/O | L1 | ★☆☆ | |
| OSY-016 | Interrupt and Trap | L1 | ★☆☆ | |
| OSY-017 | Mutex (Mutual Exclusion Lock) | L1 | ★☆☆ | |
| OSY-018 | Semaphore | L1 | ★☆☆ | |
| OSY-019 | Process Creation (fork and exec) | L1 | ★☆☆ | |
| OSY-020 | Thread Creation (pthreads, Java Thread, Virtual Threads) | L1 | ★☆☆ | |
| OSY-021 | Basic OS Monitoring Tools (ps, top, htop, free, vmstat) | L1 | ★☆☆ | 🔧 |
| OSY-022 | Top 10 OS Interview Questions (Foundational) | L1 | ★☆☆ | 🎯 |
| OSY-023 | Build and Inspect a Process (OS Lab Phase 1) | L1 | ★☆☆ | 🏋️ 🔨 |
| OSY-024 | OS Concepts Quick Reference Card | L1 | ★☆☆ | 🔁 |
| OSY-025 | Ignoring System Call Overhead Anti-Pattern | L1 | ★☆☆ | ⚠️ anti-minor |
| OSY-026 | CPU Scheduling Algorithms (FCFS, SJF, Round Robin, Priority) | L2 | ★★☆ | |
| OSY-027 | Deadlock (Definition and Coffman Conditions) | L2 | ★★☆ | |
| OSY-028 | Deadlock Prevention, Avoidance, and Detection | L2 | ★★☆ | |
| OSY-029 | Race Condition and Critical Section | L2 | ★★☆ | |
| OSY-030 | Mutex vs Semaphore vs Monitor | L2 | ★★☆ | |
| OSY-031 | Paging and Page Tables | L2 | ★★☆ | |
| OSY-032 | Page Replacement Algorithms (LRU, LFU, FIFO, Clock) | L2 | ★★☆ | |
| OSY-033 | Memory Layout of a Process (Stack, Heap, Code, Data) | L2 | ★★☆ | |
| OSY-034 | File System Operations (open, read, write, close, seek) | L2 | ★★☆ | |
| OSY-035 | Inter-Process Communication (Pipes, Message Queues, Shared Memory) | L2 | ★★☆ | |
| OSY-036 | Signals and Signal Handlers | L2 | ★★☆ | |
| OSY-037 | Blocking vs Non-Blocking vs Asynchronous I/O | L2 | ★★☆ | |
| OSY-038 | Thread-Safe Programming Basics | L2 | ★★☆ | |
| OSY-039 | Busy-Waiting Anti-Pattern | L2 | ★★☆ | ⚠️ anti-major |
| OSY-040 | Thread Pool vs Thread-per-Task Decision Guide | L2 | ★★☆ | 🧭 |
| OSY-041 | Build a Multi-Process Server - Phase 2 (IPC and Signals) | L2 | ★★☆ | 🔨 |
| OSY-042 | OS Interview Essentials - Working Level | L2 | ★★☆ | 🎯 |
| OSY-043 | strace (System Call Tracer) | L2 | ★★☆ | 🔧 |
| OSY-044 | lsof and netstat (File Descriptors and Sockets) | L2 | ★★☆ | 🔧 |
| OSY-045 | OS Working Level Self-Assessment | L2 | ★★☆ | 🔁 |
| OSY-046 | Testing Concurrent Programs (Basics) | L2 | ★★☆ | 🧪 |
| OSY-047 | Segmentation vs Paging Decision Guide | L2 | ★★☆ | 🧭 |
| OSY-048 | OS Threading Mental Model (Orchestra Analogy) | L2 | ★★☆ | |
| OSY-049 | Explain Deadlock at Every Level | L2 | ★★☆ | 🎓 |
| OSY-050 | Busy-Wait vs Sleep-Wait Kata | L2 | ★★☆ | 🏋️ |
| OSY-051 | Process vs Thread Decision Guide | L2 | ★★☆ | 🧭 |
| OSY-052 | File Descriptor Leak Anti-Pattern | L2 | ★★☆ | ⚠️ anti-major |
| OSY-053 | Signal-Based IPC Exercise | L2 | ★★☆ | 🏋️ |
| OSY-054 | Virtual Memory Deep Dive (TLB, Page Fault Handling) | L3 | ★★☆ | |
| OSY-055 | Demand Paging and Working Set Model | L3 | ★★☆ | |
| OSY-056 | Memory-Mapped Files (mmap) | L3 | ★★☆ | |
| OSY-057 | Copy-on-Write (COW) Mechanism | L3 | ★★☆ | |
| OSY-058 | NUMA Architecture and Memory Locality | L3 | ★★☆ | |
| OSY-059 | CPU Cache Hierarchy and Cache Line Sharing | L3 | ★★☆ | |
| OSY-060 | False Sharing Anti-Pattern | L3 | ★★☆ | ⚠️ anti-major |
| OSY-061 | Lock-Free Data Structures (CAS Operations) | L3 | ★★☆ | |
| OSY-062 | Spinlock vs Mutex Selection Framework | L3 | ★★☆ | 🧭 |
| OSY-063 | Condition Variables and Monitor Pattern | L3 | ★★☆ | |
| OSY-064 | Priority Inversion and Priority Inheritance | L3 | ★★☆ | |
| OSY-065 | Completely Fair Scheduler (CFS) Internals | L3 | ★★☆ | |
| OSY-066 | Real-Time Scheduling (SCHED_FIFO, SCHED_RR) | L3 | ★★☆ | |
| OSY-067 | I/O Scheduler Types (CFQ, Deadline, NOOP, BFQ) | L3 | ★★☆ | |
| OSY-068 | epoll and Event-Driven I/O | L3 | ★★☆ | |
| OSY-069 | Zero-Copy Techniques (sendfile, splice) | L3 | ★★☆ | |
| OSY-070 | Memory Overcommit and OOM Killer | L3 | ★★☆ | |
| OSY-071 | OS-Level Security (DAC, MAC, SELinux, AppArmor) | L3 | ★★☆ | 🔒 |
| OSY-072 | Process Isolation and Namespaces (Container Foundation) | L3 | ★★☆ | |
| OSY-073 | Inode and File System Data Structures | L3 | ★★☆ | |
| OSY-074 | Journaling File Systems (ext4, XFS, btrfs) | L3 | ★★☆ | |
| OSY-075 | Thread-per-Request Anti-Pattern | L3 | ★★☆ | ⚠️ anti-major |
| OSY-076 | OS Kernel Version Upgrade Strategy | L3 | ★★☆ | 🔄 |
| OSY-077 | strace Intermediate - Tracing System Calls in Production | L3 | ★★☆ | 🔧 📊 |
| OSY-078 | perf stat and CPU Counter Analysis | L3 | ★★☆ | 🔧 ⚡ |
| OSY-079 | Testing Concurrent Programs (TSan, Helgrind) | L3 | ★★☆ | 🧪 |
| OSY-080 | POSIX Standards and Portability | L3 | ★★☆ | 📋 |
| OSY-081 | OS System Design Interview Patterns | L3 | ★★☆ | 🎯 |
| OSY-082 | Explain Virtual Memory at Every Level | L3 | ★★☆ | 🎓 |
| OSY-083 | OS Intermediate Self-Assessment | L3 | ★★☆ | 🔁 |
| OSY-084 | Build a Concurrent Server - Phase 3 (Sync and Memory) | L3 | ★★☆ | 🔨 🏋️ |
| OSY-085 | OS and JVM Thread Interaction (Safepoints, Scheduling) | L3 | ★★☆ | |
| OSY-086 | OS Architecture Evolution (Monolithic vs Microkernel vs Exokernel) | L3 | ★★☆ | 🔄 |
| OSY-087 | Linux Kernel Module Basics | L3 | ★★☆ | |
| OSY-088 | Ignoring NUMA Locality Anti-Pattern | L3 | ★★☆ | ⚠️ anti-minor |
| OSY-089 | Kernel Internals (VFS, Block Layer, System Call Dispatch) | L4 | ★★★ | |
| OSY-090 | Page Cache and Buffer Cache Internals | L4 | ★★★ | |
| OSY-091 | Memory Pressure and Reclaim Algorithm | L4 | ★★★ | |
| OSY-092 | Huge Pages (THP) and Memory Fragmentation | L4 | ★★★ | |
| OSY-093 | CPU Affinity and Thread Pinning (taskset, sched_setaffinity) | L4 | ★★★ | 🔧 |
| OSY-094 | Lock Contention Profiling (perf lock, ftrace) | L4 | ★★★ | 🔧 |
| OSY-095 | Kernel Bypass Networking (DPDK) | L4 | ★★★ | |
| OSY-096 | io_uring - Next-Generation Async I/O Internals | L4 | ★★★ | |
| OSY-097 | eBPF for Production Observability | L4 | ★★★ | 📊 🔧 |
| OSY-098 | OS Performance Profiling with Flamegraphs (Brendan Gregg) | L4 | ★★★ | 🔧 ⚡ |
| OSY-099 | Context Switch Overhead Measurement and Reduction | L4 | ★★★ | ⚡ |
| OSY-100 | Production Memory Leak Diagnosis (pmap, smaps, valgrind) | L4 | ★★★ | 🔧 |
| OSY-101 | OOM Killer Trigger Analysis and Prevention | L4 | ★★★ | 📊 |
| OSY-102 | Meltdown and Spectre (2018) - Kernel Security Implications | L4 | ★★★ | 🔴 |
| OSY-103 | Dirty COW (CVE-2016-5195) - Race Condition in Kernel | L4 | ★★★ | 🔴 |
| OSY-104 | ASLR (Address Space Layout Randomization) | L4 | ★★★ | |
| OSY-105 | cgroups (Control Groups) v1 and v2 Internals | L4 | ★★★ | |
| OSY-106 | Linux Namespaces Deep Dive (Container Security Foundation) | L4 | ★★★ | |
| OSY-107 | OS Security Hardening (CIS Linux Benchmark) | L4 | ★★★ | 📋 |
| OSY-108 | OS Patch Management and CVE Response | L4 | ★★★ | 📋 |
| OSY-109 | Diagnosing High Context Switch Rate in JVM Applications | L4 | ★★★ | |
| OSY-110 | Diagnosing I/O Wait (iowait, iostat, blktrace) | L4 | ★★★ | 🔧 |
| OSY-111 | Unbounded Thread Creation Anti-Pattern | L4 | ★★★ | ⚠️ anti-critical |
| OSY-112 | OS Expert Mastery Verification | L4 | ★★★ | 🔁 |
| OSY-113 | Production OS Observability Lab - Phase 4 (Diagnosis) | L4 | ★★★ | 🔨 🏋️ |
| OSY-114 | OS Deep-Dive Interview Questions | L4 | ★★★ | 🎯 |
| OSY-115 | Teach OS Internals to Juniors (5 Hard Questions They Ask) | L4 | ★★★ | 🎓 |
| OSY-116 | OS Performance Tuning Framework (CPU, Memory, I/O) | L4 | ★★★ | 🧭 ⚡ |
| OSY-117 | OS Compliance and Audit Checklist (SOC2, CIS, POSIX) | L4 | ★★★ | 📋 |
| OSY-118 | Container and OS Security Interaction | L4 | ★★★ | |
| OSY-119 | OS Selection Framework for Production Workloads | L5 | ★★★ | 🧭 |
| OSY-120 | Kernel Parameter Tuning Strategy at Fleet Scale (sysctl) | L5 | ★★★ | |
| OSY-121 | OS Observability Platform Design (eBPF, Prometheus, Grafana) | L5 | ★★★ | |
| OSY-122 | Container vs VM Resource Isolation Architecture | L5 | ★★★ | |
| OSY-123 | Multi-Tenant OS Resource Governance (cgroups and Namespaces) | L5 | ★★★ | |
| OSY-124 | OS Upgrade Strategy (Rolling Updates, Canary, Blue-Green) | L5 | ★★★ | 🔄 |
| OSY-125 | OS-Aware JVM Tuning Architecture | L5 | ★★★ | |
| OSY-126 | Capacity Planning Using OS Metrics (CPU, Memory, I/O) | L5 | ★★★ | |
| OSY-127 | Architecture Decision Record - OS Baseline for Production | L5 | ★★★ | |
| OSY-128 | OS Staff-Level Interview Scenarios | L5 | ★★★ | 🎯 |
| OSY-129 | Snowflake Server Configuration Anti-Pattern | L5 | ★★★ | ⚠️ anti-major |
| OSY-130 | OS Platform Architecture Design - Phase 5 (Fleet Governance) | L5 | ★★★ | 🔨 |
| OSY-131 | Dijkstra's THE Operating System (1968) | L6 | ★★★ | 📖 |
| OSY-132 | Unix Philosophy (Ritchie and Thompson, 1974) | L6 | ★★★ | 📖 |
| OSY-133 | Mach Microkernel (Rashid et al. 1985) and Its Influence | L6 | ★★★ | 📖 |
| OSY-134 | Linux Kernel Origin (Torvalds, 1991) and Architecture | L6 | ★★★ | 📖 |
| OSY-135 | Popek-Goldberg Virtualization Requirements (1974) | L6 | ★★★ | 📖 |
| OSY-136 | Exokernel Design (Engler et al. 1995) | L6 | ★★★ | 📖 |
| OSY-137 | Open Problems in OS Research (Memory Safety, Scheduling) | L6 | ★★★ | |
| OSY-138 | Writing an OS from Scratch (OSDev, RISC-V Bare Metal) | L6 | ★★★ | 🏋️ |
| OSY-139 | OS Internals as JVM Performance Mental Model | META | ★★★ | 🧠 |
| OSY-140 | Lock Contention as Traffic Congestion (Pattern Bridge) | META | ★★★ | 🔗 |
| OSY-141 | OS Scheduling Principles Transfer to Distributed Systems | META | ★★★ | 🧠 |
| OSY-142 | Resource Starvation Reasoning (OS to Any Queuing System) | META | ★★★ | 🧠 |
| OSY-143 | OS First-Principles Thinking Under Production Load | META | ★★★ | 🧠 |
