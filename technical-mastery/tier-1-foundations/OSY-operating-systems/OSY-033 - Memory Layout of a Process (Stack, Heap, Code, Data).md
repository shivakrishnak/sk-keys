---
id: OSY-033
title: Memory Layout of a Process (Stack, Heap, Code, Data)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-006, OSY-012, OSY-031
used_by: OSY-054, OSY-092
related: OSY-012, OSY-031, OSY-054
tags:
  - memory-layout
  - stack
  - heap
  - text-segment
  - data-segment
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/osy/process-memory-layout/
---

## TL;DR

A process's virtual address space is divided into
segments: text (code), data (globals), BSS (uninitialized),
heap (grows up), stack (grows down). Stack overflows
and heap fragmentation are the two most common memory
layout problems. JVM adds its own heap on top of the OS
process layout.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-033 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | memory layout, stack, heap, code, data segment |
| **Prerequisites** | OSY-006, OSY-012, OSY-031 |

---

### Process Memory Layout (x86-64 Linux)

```
Virtual Address Space (simplified, high->low):
+---------------------------+ <- 0xFFFFFFFFFFFFFFFF (128TB limit)
|     Kernel Space          | <- OS code, kernel data (Ring 0)
|   (inaccessible to user)  |    access -> SIGSEGV
+---------------------------+ <- 0x0000800000000000
|     Stack                 | <- grows DOWN
|  (function frames, args,  |    default limit: 8MB (ulimit -s)
|   local variables)        |    SIGSEGV if stack limit exceeded
+---------------------------+ <- stack_start (random with ASLR)
|     ...                   |
|   (mmap region)           | <- shared libraries, anonymous maps
|     ...                   |    libc.so, libpthread.so, etc.
+---------------------------+
|     Heap                  | <- grows UP (brk() / mmap())
|   (malloc, new, GC)       |    size: dynamic, grows as needed
+---------------------------+ <- end of data (brk pointer)
|     BSS                   | <- uninitialized global/static vars
|   (zero-filled at start)  |    e.g., static int counter;
+---------------------------+
|     Data                  | <- initialized global/static vars
|   (from executable file)  |    e.g., static int MAX = 100;
+---------------------------+
|     Text (Code)           | <- executable instructions (read-only)
|   (from executable file)  |    multiple processes can share this
+---------------------------+ <- 0x0000000000400000 (typical)
|     Reserved              | <- null page, not mapped
+---------------------------+ <- 0x0000000000000000
```

---

### Segments in Detail

**Text Segment (Code)**

```
- Read-only, executable
- Mapped from the ELF executable file
- Shared between processes running same executable
  (fork() doesn't copy code; same physical pages)
- Protected: write attempt -> SIGSEGV
  (prevents code injection via buffer overflow)
- Position Independent Code (PIC): addresses relative
  to PC, enables ASLR
```

**Data and BSS**

```
Data: initialized global and static variables
  static int MAX = 100;  // lives in .data section
  
BSS: uninitialized global and static (zero-filled)
  static int counter;     // lives in .bss section
  (OS zero-fills .bss at program load - no disk space)
  
Java equivalent:
  static fields of classes -> JVM metaspace / heap
  (JVM doesn't directly use OS .data/.bss for Java statics)
```

**Stack**

```
Grows DOWN from high address to low address.
Contains: function stack frames

Each frame:
  - Return address (caller's instruction pointer)
  - Saved registers (caller-saved or callee-saved)
  - Local variables (int x = 5;)
  - Function arguments (some on stack, some in registers)

Default limit: 8MB (ulimit -s on Linux)
Guard page: unmapped page just below stack limit
  Stack overflow: stack grows into guard page -> SIGSEGV

Java stack:
  Each Java thread has its own OS stack (1MB default)
  JVM frames: local variables, operand stack, method pointers
  StackOverflowError: too many nested calls (deep recursion)
  Increase: -Xss4m (per-thread stack size)
  
Stack vs Heap lifetime:
  Stack: function scope (auto-freed when function returns)
  Heap: programmer-managed or GC-managed
```

**Heap**

```
Grows UP from the BSS boundary.
Managed by: malloc (C), new (C++/Java), GC (Java)

Linux allocation:
  brk(addr): extend heap by moving brk pointer up
  mmap(NULL, size): allocate anonymous pages anywhere in mmap region
  malloc uses brk for small allocations (<128KB),
    mmap for large allocations (configurable)

Java Heap (distinct from OS heap):
  JVM allocates large mmap region at startup (Xms to Xmx)
  JVM manages its own heap internally (generational GC)
  Java 'new' doesn't call malloc -> JVM heap allocator
  
  JVM memory outside Java heap:
    Metaspace: class metadata (was PermGen before Java 8)
    Code cache: JIT-compiled native code
    Direct ByteBuffer: off-heap I/O buffers
    Thread stacks: separate per-thread OS stack allocations
```

---

### Java JVM Memory Layout

```
JVM process virtual address space:

+---------------------------+
| OS Stack (per thread)     | 1-8MB per thread (OS-managed)
+---------------------------+
| Code Cache                | JIT-compiled code (~256MB default)
+---------------------------+
| Metaspace                 | Class definitions, method bytecode
|                           | (unlimited by default, -XX:MaxMetaspace)
+---------------------------+
| JVM Java Heap             | -Xms to -Xmx (4GB default max)
|   Young gen (Eden+Survivor)|
|   Old gen                 |
+---------------------------+
| JVM native code           | JVM itself (C/C++ code)
| (text segment)            |
+---------------------------+
```

```bash
# See JVM's full memory map
pmap -x $(pgrep java) | head -30
# Shows all virtual memory regions with RSS (physical usage)

# Check JVM memory breakdown
jcmd $(pgrep java) VM.native_memory summary
# Shows: heap, metaspace, code cache, thread stacks, etc.
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Stack memory is always slower than heap" | Stack allocation is faster (just decrement stack pointer, O(1)). Heap allocation requires finding a free block (malloc bookkeeping). The speed difference is in allocation, not access |
| "Java heap = OS process heap" | JVM allocates its heap via mmap (or sometimes OS heap), but Java objects are NOT in the OS process heap area. `malloc()`/`free()` is used by JVM's own C code. Java `new` uses JVM's own heap allocator |
| "Stack overflow in Java only happens with infinite recursion" | StackOverflowError can occur with deep but finite recursion, large local variable arrays in deep call stacks, or very small -Xss value. Also: native JNI calls add their own stack frames |

---

### Failure Modes

```
1. Stack Overflow
Symptom: StackOverflowError (Java), SIGSEGV near stack limit (C)
Diagnosis: jstack shows deep call stack, bottom frame shows
  the recursive pattern
Fix: Increase -Xss OR convert recursion to iteration OR
  use tail-call elimination

2. Heap Memory Leak
Symptom: RSS grows indefinitely (not just VIRT)
Diagnosis: 
  jmap -histo <PID> | head -20  # Java object count by type
  jcmd <PID> GC.heap_info       # heap usage
Fix: Find GC root keeping objects alive; break reference

3. Native Memory Leak (off-heap)
Symptom: VIRT and RSS grow even after GC, Java heap looks OK
Diagnosis:
  pmap -x PID | sort -k3 -rn    # sorted by RSS
  jcmd PID VM.native_memory     # JVM native breakdown
Fix: DirectByteBuffer not released, C library malloc leak,
  Metaspace growth (class loading leak)
```

---

### Related Keywords

**Builds on:** OSY-006 (Process States), OSY-012 (Virtual Memory),
OSY-031 (Paging and Page Tables)

**Leads to:** OSY-054 (Virtual Memory Deep Dive),
OSY-092 (Memory Leak Diagnosis)

---

### Quick Reference Card

| Segment | Grows | Content | Limit |
|---------|-------|---------|-------|
| Text | Static | Compiled code | Executable size |
| Data/BSS | Static | Global variables | Executable size |
| Heap | Upward | Dynamic allocations | RAM/virtual |
| Stack | Downward | Function frames | 8MB default |
| mmap region | Both | Libraries, anonymous maps | Virtual space |
