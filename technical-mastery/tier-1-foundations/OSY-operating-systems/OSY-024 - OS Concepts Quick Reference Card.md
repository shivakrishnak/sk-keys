---
id: OSY-024
title: OS Concepts Quick Reference Card
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-001, OSY-006, OSY-007, OSY-008, OSY-009, OSY-010, OSY-011, OSY-012
used_by: []
related: OSY-045, OSY-083, OSY-112
tags:
  - reference
  - cheat-sheet
  - retention
  - quick-reference
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/osy/quick-reference/
---

## TL;DR

Quick reference for all foundational OS concepts. Use
for rapid review before interviews, during incidents,
or as a daily reference until these facts are in muscle
memory.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-024 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | quick reference, cheat sheet, retention |
| **Prerequisites** | OSY-001 through OSY-021 |

---

### Core Concepts Quick Reference

**Process and Thread**

| Concept | Key Fact |
|---------|---------|
| Process | Program + execution state + own address space |
| Thread | Execution unit sharing process address space |
| PCB | Process Control Block: state, registers, memory map, FDs |
| Process states | New, Ready, Running, Blocked, Terminated |
| Zombie | Exited process, exit status not collected by parent |
| fork() return | 0 in child, child PID in parent |
| Thread stack | 512KB-8MB per OS thread (private, not shared) |
| Virtual thread | JVM-level, ~few KB, ~200ns creation, Java 21+ |

**Memory**

| Concept | Key Fact |
|---------|---------|
| Virtual memory | Each process sees own contiguous address space |
| MMU | Hardware CPU component: virtual -> physical translation |
| TLB | MMU's cache for recent address translations |
| Page size | 4KB (standard), 2MB (huge page) |
| Page fault | Access to unmapped virtual address, kernel handles |
| VIRT (ps) | Virtual memory claimed by process |
| RSS/RES | Resident Set Size = actual physical RAM in use |
| Page cache | OS cache of file data in RAM (shown as "cached" in free) |

**CPU and Scheduling**

| Concept | Key Fact |
|---------|---------|
| Context switch | Save current thread state, load next thread state |
| Thread switch cost | ~1-10 microseconds |
| Process switch cost | ~10-100 microseconds (TLB flush) |
| Linux scheduler | CFS (Completely Fair Scheduler), red-black tree |
| Time quantum | ~4ms default (CFS variable, not fixed) |
| Nice value | -20 (highest priority) to +19 (lowest priority) |
| SCHED_FIFO | Real-time, no preemption by CFS |
| Load average | 1-min / 5-min / 15-min avg runnable thread count |

**Synchronization**

| Concept | Key Fact |
|---------|---------|
| Mutex | Binary lock with ownership (only locker can unlock) |
| Semaphore | Integer counter, any thread can V() |
| Monitor | Mutex + condition variable (Java: synchronized object) |
| Race condition | Non-atomic shared data access = undefined behavior |
| Deadlock | Circular wait: A holds X wants Y, B holds Y wants X |
| Deadlock prevention | Always acquire locks in consistent global order |

**System Calls and Kernel**

| Concept | Key Fact |
|---------|---------|
| System call | User -> Kernel mode transition for privileged op |
| Kernel mode | Ring 0, full hardware access |
| User mode | Ring 3, restricted, all applications |
| Syscall mechanism | SYSCALL instruction (x86-64) |
| Syscall cost | ~100-300ns (no I/O), us-ms (with I/O) |
| Interrupt | Async hardware event that preempts current thread |
| Trap | Sync exception from program (page fault, syscall) |

**Key Tools and Commands**

| Tool | Primary Use |
|------|------------|
| `ps aux` | Snapshot of all processes |
| `top -H -p PID` | Live threads of a process |
| `free -h` | Memory overview (use `available` column) |
| `vmstat 1` | System activity (cs = context switches) |
| `strace -p PID` | System calls made by a process |
| `lsof -p PID` | Open file descriptors of a process |
| `cat /proc/PID/status` | Process PCB summary |
| `cat /proc/PID/maps` | Virtual memory map |

**Key Numbers to Remember**

| Metric | Typical Value |
|--------|--------------|
| Thread context switch | 1-10 microseconds |
| Process context switch | 10-100 microseconds |
| System call (no I/O) | 100-300 nanoseconds |
| Page fault (cold) | 1-10 microseconds (RAM) |
| Page fault (swap) | 1-10 milliseconds (disk) |
| TLB hit | ~1 cycle |
| TLB miss | ~50-100 cycles |
| Fork a 4GB JVM | ~1ms (COW, only page table copied) |
| Create OS thread | 10-50 microseconds |
| Create virtual thread | ~200 nanoseconds |

---

### Mastery Checklist

- [ ] Can recite the process states and transitions
- [ ] Knows the 5 key numbers (thread switch, syscall, TLB miss, etc.)
- [ ] Can match each tool to its primary diagnostic use
- [ ] Knows mutex vs semaphore ownership distinction
