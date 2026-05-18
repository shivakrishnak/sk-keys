---
id: OSY-009
title: Kernel Space vs User Space
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-001
used_by: OSY-008, OSY-060, OSY-089
related: OSY-001, OSY-008, OSY-089
tags:
  - foundational
  - kernel
  - user-space
  - privilege-rings
  - memory-protection
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/osy/kernel-user-space/
---

## TL;DR

Kernel space is privileged memory where the OS kernel
runs with full hardware access. User space is restricted
memory where applications run. Separation enforces
protection: a bug in user space cannot corrupt the kernel.
The boundary is crossed only via system calls.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-009 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | kernel space, user space, privilege rings, protection |
| **Prerequisites** | OSY-001 |

---

### The Two Privilege Domains

```
x86-64 Virtual Address Space (48-bit, 256TB total):

High addresses (kernel space):
  0xFFFF800000000000 - 0xFFFFFFFFFFFFFFFF (128TB)
  │ Kernel code and data
  │ Interrupt handlers
  │ Device driver memory
  │ Page tables
  └─ All physical memory mapped here (kernel can access all)

Low addresses (user space):
  0x0000000000000000 - 0x00007FFFFFFFFFFF (128TB)
  │ Your application code (.text)
  │ Your application data (.data, .bss)
  │ Your heap (malloc/new)
  │ Your stacks (thread stacks)
  └─ Shared libraries (libc, etc.)

CPU enforces: user code CANNOT read/write kernel space.
  Any attempt: segmentation fault (SIGSEGV) or general
  protection fault - process terminated.
```

---

### CPU Privilege Rings

```
Ring 0 (Kernel mode):
  Full access to all hardware instructions
  Can write to any memory address
  Can halt CPU, configure MMU, manage interrupts
  Used by: OS kernel, device drivers
  
Ring 3 (User mode):
  Restricted instruction set
  Can only access memory in own address space
  Cannot execute privileged instructions (IN, OUT, HLT, etc.)
  Used by: all applications (Java, Python, C++)

(Rings 1 and 2 existed for drivers in early OS design
but are unused in modern x86 Linux/Windows)

Virtual machines:
  Hypervisor: Ring 0 (or Ring -1 with Intel VT-x)
  Guest OS kernel: Ring 0 (virtualized, appears to be Ring 0)
  Guest application: Ring 3
```

---

### Why the Separation Exists

```
Without kernel/user separation:
  A buggy Java program could:
  - Write to memory address 0x0 -> CPU vector table corruption
  - Read from device memory -> intercept keyboard input
  - Execute HLT instruction -> freeze the CPU
  - Modify page tables -> escape process isolation

With kernel/user separation:
  Buggy Java program gets SIGSEGV and is killed.
  Other processes and the kernel are unaffected.
  This is the fundamental guarantee of OS stability.

Real impact: a JVM crash (SIGSEGV) kills ONLY that JVM.
  Other JVMs, the OS, and other services continue running.
  This is why microservices > monolith for failure isolation:
  separate processes = separate address spaces = kernel
  protects each from the others.
```

---

### Kernel Mode Entry Points

```
Three ways to enter kernel mode from user space:

1. System call (intentional):
   Application calls read(), write(), open()
   CPU: executes SYSCALL instruction -> Ring 0
   
2. Hardware interrupt (asynchronous):
   Network card receives packet -> IRQ fires
   CPU: suspends current user program -> Ring 0
   Kernel: interrupt handler runs, processes packet
   CPU: IRET -> resumes user program at exact point
   
3. Fault/Exception (unintentional):
   Program accesses unmapped page -> page fault
   CPU: Ring 0, page fault handler
   Kernel: either: maps the page (stack growth, COW)
                   or: sends SIGSEGV to process
```

---

### Kernel Space Memory - What's There

```
$ cat /proc/meminfo | grep -E "(MemTotal|MemFree|Cached|Buffers)"

MemTotal:       16384MB   <- Total RAM
MemFree:          512MB   <- Truly free
Buffers:          256MB   <- Kernel I/O buffer cache
Cached:          8192MB   <- Kernel page cache (file data)

Kernel uses 8448MB for its caches - but this is instantly
reclaimed when applications need it.

$ cat /proc/kallsyms | head  <- Kernel symbol table
ffffffff81000000 T _text     <- Kernel code start
ffffffff82000000 T _etext    <- Kernel code end

These are kernel space addresses. User programs accessing
these addresses get SIGSEGV immediately.
```

---

### Textbook Definition

Kernel space is the region of a process's virtual address
space reserved for the OS kernel. It is accessible only
in kernel mode (CPU Ring 0). User space is the region
where applications execute in user mode (CPU Ring 3) with
no direct hardware access. The boundary is enforced by
the CPU's memory management unit (MMU) page table
permission bits.

---

### Understand It in 30 Seconds

Kernel space = locked server room (only sysadmins enter).
User space = open office (everyone works here).
System call = intercom: you ask the sysadmin to do
something you're not allowed to do yourself.
The CPU's MMU is the badge reader that enforces the lock.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "The OS consumes a lot of memory in kernel space" | The kernel code itself is small (Linux kernel: ~30MB). The large "kernel space" usage is the page cache, which is file data cached in RAM for performance - not kernel overhead |
| "Kernel vs user space only matters for systems programmers" | JVM native memory (off-heap), DirectByteBuffer, and Java NIO all work in user space but interact with kernel space for I/O. A Java program allocating 32GB off-heap and having frequent page faults is a kernel space interaction problem |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Kernel panic | System crash, unrecoverable | Bug in kernel code (Ring 0 fault) | Kernel driver bug; update kernel; check dmesg |
| SIGSEGV | Process killed, JVM crashes | User code accessed invalid memory | Check null pointer, buffer overflow, JVM hs_err log |
| Security | Meltdown exploit (2018) | Speculative execution read kernel memory from user space | KPTI (kernel page-table isolation) patch, performance cost |

---

### The Surprising Truth

The Meltdown vulnerability (CVE-2017-5754, 2018) allowed
user-space programs to read kernel memory by exploiting
CPU speculative execution. The CPU speculatively executed
kernel memory reads before checking Ring permissions;
even though the actual access was denied, cache timing
side-channels revealed the data. The fix - KPTI (Kernel
Page-Table Isolation) - removes kernel mappings from user
space page tables, requiring a full TLB flush on EVERY
system call. This caused 5-30% performance regression
on I/O-heavy workloads. A fundamental security guarantee
(kernel space is private) had been violated at the CPU
hardware level for years before discovery.

---

### Mastery Checklist

- [ ] Can draw the virtual address space showing kernel vs user regions
- [ ] Knows Ring 0 vs Ring 3 and what each can access
- [ ] Understands why a user-space crash cannot kill the kernel
- [ ] Knows the 3 ways to enter kernel mode (syscall, interrupt, fault)
- [ ] Can explain the Meltdown impact on kernel/user space separation
