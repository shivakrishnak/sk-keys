---
layout: default
title: "Java & JVM Internals"
parent: "Documentation"
nav_order: 1
has_children: true
permalink: /java/
---
# Java & JVM Internals

## JVM Architecture, Memory Management & Execution Engine

This section covers the Java Virtual Machine internals: bytecode execution, class loading,
memory model (heap, stack, metaspace), garbage collection algorithms, JIT compilation,
and low-level JVM mechanisms.

### Topics Covered

- **JVM Architecture** — JVM, JRE, JDK, Bytecode
- **Class Loading** — Class Loader, Dynamic Loading
- **Memory Model** — Stack Memory, Heap Memory, Metaspace, Object Header
- **Execution** — Stack Frame, Operand Stack, Local Variable Table
- **GC Algorithms** — Serial, Parallel, CMS, G1GC, ZGC, Shenandoah
- **GC Internals** — Young/Old Generation, Eden, Survivor, Minor/Major/Full GC, Stop-The-World
- **JIT Compiler** — C1/C2, Tiered Compilation, Method Inlining, Deoptimisation
- **Advanced** — Escape Analysis, GraalVM, Native Image, TLAB, Safepoint

---

## Keywords (001–050)

| # | Keyword | # | Keyword |
|---|---------|---|---------|
| 001 | [JVM (Java Virtual Machine)](./001%20—%20JVM%20(Java%20Virtual%20Machine).md) | 026 | Parallel GC |
| 002 | [JRE (Java Runtime Environment)](./002%20—%20JRE%20(Java%20Runtime%20Environment).md) | 027 | CMS (Concurrent Mark Sweep) |
| 003 | [JDK (Java Development Kit)](./003%20—JDK%20(Java%20Development%20Kit).md) | 028 | G1GC |
| 004 | [Bytecode](./004%20—Bytecode.md) | 029 | ZGC |
| 005 | [Class Loader](./005%20—%20Class%20Loader.md) | 030 | Shenandoah GC |
| 006 | [Stack Memory](./006%20—%20Stack%20Memory.md) | 031 | GC Tuning |
| 007 | [Heap Memory](./007%20—%20Heap%20Memory.md) | 032 | GC Logs |
| 008 | [Metaspace](./008%20—%20Metaspace.md) | 033 | GC Pause |
| 009 | [Stack Frame](./009%20—%20Stack%20Frame.md) | 034 | Throughput vs Latency (GC) |
| 010 | [Operand Stack](./010%20—%20Operand%20Stack.md) | 035 | Finalization |
| 011 | [Local Variable Table](./011%20—%20Local%20Variable%20Table.md) | 036 | JIT Compiler |
| 012 | [Object Header](./012%20—%20Object%20Header.md) | 037 | C1 / C2 Compiler |
| 013 | [Escape Analysis](./013%20—%20Escape%20Analysis.md) | 038 | Tiered Compilation |
| 014 | [Memory Barrier](./014%20—%20Memory%20Barrier.md) | 039 | Method Inlining |
| 015 | [Happens-Before](./015%20—%20Happens-Before.md) | 040 | Deoptimization |
| 016 | [GC Roots](./016%20—%20GC%20Roots.md) | 041 | OSR (On-Stack Replacement) |
| 017 | [Reference Types](./017%20—%20Reference%20Types%20(Strong%2C%20Soft%2C%20Weak%2C%20Phantom).md) | 042 | AOT (Ahead-of-Time Compilation) |
| 018 | [Young Generation](./018%20—%20Young%20Generation.md) | 043 | GraalVM |
| 019 | [Eden Space](./019%20—%20Eden%20Space.md) | 044 | Native Image |
| 020 | [Survivor Space](./020%20—%20Survivor%20Space.md) | 045 | TLAB (Thread Local Allocation Buffer) |
| 021 | [Minor GC](./021%20—%20Minor%20GC.md) | 046 | Safepoint |
| 022 | [Major GC](./022%20—%20Major%20GC.md) | 047 | Card Table |
| 023 | [Full GC](./023%20—%20Full%20GC.md) | 048 | Write Barrier |
| 024 | [Stop-The-World (STW)](./024%20—%20Stop-The-World%20(STW).md) | 049 | Remembered Set |
| 025 | [Serial GC](./025%20—%20Serial%20GC.md) | 050 | String Pool / String Interning |
