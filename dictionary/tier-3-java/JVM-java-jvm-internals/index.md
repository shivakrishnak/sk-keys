---
layout: default
title: "Java & JVM Internals"
parent: "Technical Dictionary"
nav_order: 7
has_children: true
permalink: /jvm/
---

# Java & JVM Internals

JVM architecture, memory model, garbage collection algorithms, JIT compilation, GraalVM, AOT compilation, and JVM specification theory.

**Keywords:** JVM-001--JVM-075 (75 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| JVM-001 | What Is the JVM - A Mental Model | ★☆☆ |
| JVM-002 | Why the JVM Was Invented | ★☆☆ |
| JVM-003 | JVM vs JRE vs JDK | ★☆☆ |
| JVM-004 | How Java Code Runs - Bytecode to Execution | ★★☆ |
| JVM-005 | The JVM Ecosystem Map (OpenJDK, GraalVM, Languages) | ★☆☆ |
| JVM-006 | JRE | ★☆☆ |
| JVM-007 | JDK | ★☆☆ |
| JVM-008 | Bytecode | ★★☆ |
| JVM-009 | Class Loader | ★★☆ |
| JVM-010 | Stack Memory | ★★☆ |
| JVM-011 | Heap Memory | ★★☆ |
| JVM-012 | Metaspace | ★★☆ |
| JVM-013 | Stack Frame | ★★★ |
| JVM-014 | Operand Stack | ★★★ |
| JVM-015 | Local Variable Table | ★★★ |
| JVM-016 | Object Header | ★★★ |
| JVM-017 | Escape Analysis | ★★★ |
| JVM-018 | Memory Barrier | ★★★ |
| JVM-019 | Happens-Before | ★★★ |
| JVM-020 | GC Roots | ★★★ |
| JVM-021 | Reference Types (Strong, Soft, Weak, Phantom) | ★★★ |
| JVM-022 | Young Generation | ★★☆ |
| JVM-023 | Eden Space | ★★☆ |
| JVM-024 | Survivor Space | ★★☆ |
| JVM-025 | Old Generation | ★★☆ |
| JVM-026 | Minor GC | ★★☆ |
| JVM-027 | Major GC | ★★★ |
| JVM-028 | Full GC | ★★★ |
| JVM-029 | Stop-The-World (STW) | ★★★ |
| JVM-030 | Serial GC | ★★☆ |
| JVM-031 | Parallel GC | ★★☆ |
| JVM-032 | CMS (Concurrent Mark Sweep) | ★★★ |
| JVM-033 | G1GC | ★★★ |
| JVM-034 | ZGC | ★★★ |
| JVM-035 | Shenandoah GC | ★★★ |
| JVM-036 | GC Tuning | ★★★ |
| JVM-037 | GC Logs | ★★☆ |
| JVM-038 | GC Pause | ★★★ |
| JVM-039 | Throughput vs Latency (GC) | ★★★ |
| JVM-040 | Finalization | ★★★ |
| JVM-041 | JIT Compiler | ★★★ |
| JVM-042 | C1 C2 Compiler | ★★★ |
| JVM-043 | Tiered Compilation | ★★★ |
| JVM-044 | Method Inlining | ★★★ |
| JVM-045 | Deoptimization | ★★★ |
| JVM-046 | OSR (On-Stack Replacement) | ★★★ |
| JVM-047 | AOT (Ahead-of-Time Compilation) | ★★★ |
| JVM-048 | GraalVM | ★★★ |
| JVM-049 | Native Image | ★★★ |
| JVM-050 | TLAB (Thread Local Allocation Buffer) | ★★★ |
| JVM-051 | Safepoint | ★★★ |
| JVM-052 | Card Table | ★★★ |
| JVM-053 | Write Barrier | ★★★ |
| JVM-054 | Remembered Set | ★★★ |
| JVM-055 | GC Tuning Strategy for Production JVMs | ★★★ |
| JVM-056 | JVM Architecture Decisions at Scale | ★★★ |
| JVM-057 | JVM Selection Framework (HotSpot vs GraalVM) | ★★★ |
| JVM-058 | Heap Sizing and Memory Planning Strategy | ★★★ |
| JVM-059 | JVM Observability Strategy | ★★★ |
| JVM-060 | JVM Specification Deep Dive | ★★★ |
| JVM-061 | GC Algorithm Design Principles | ★★★ |
| JVM-062 | JIT Compilation Research (Truffle, Graal IR) | ★★★ |
| JVM-063 | JVM Language Design (Bytecode Targeting) | ★★★ |
| JVM-064 | JVM-First Debugging Mental Model | ★★★ |
| JVM-065 | Performance Intuition via JVM Internals | ★★★ |
| JVM-066 | GC Trade-off Framing | ★★★ |
| JVM-067 | Method Area | ★★☆ |
| JVM-068 | PC Register (Program Counter) | ★★★ |
| JVM-069 | Native Method Stack | ★★★ |
| JVM-070 | JVM Flags (-Xms, -Xmx, -XX: Flags) | ★★☆ |
| JVM-071 | Heap Dump | ★★☆ |
| JVM-072 | Thread Dump | ★★☆ |
| JVM-073 | Class Loading Delegation Model | ★★★ |
| JVM-074 | Compressed OOPs | ★★★ |
| JVM-075 | Class Data Sharing (CDS / AppCDS) | ★★★ |