---
layout: default
title: "Java & JVM Internals"
parent: "Technical Dictionary"
nav_order: 10
has_children: true
permalink: /jvm/
---

# Java & JVM Internals

JVM architecture, bytecode, class loading, garbage collection (Serial, G1, ZGC), memory model (heap, stack, Metaspace), JIT compilation, performance profiling, and GraalVM.

**Keywords:** JVM-001–JVM-080 (80 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| JVM-001 | What Is the JVM - A Mental Model | ★☆☆ |
| JVM-002 | Why the JVM Was Invented | ★☆☆ |
| JVM-003 | JVM vs JRE vs JDK | ★☆☆ |
| JVM-008 | The JVM Ecosystem Map (OpenJDK, GraalVM, Languages) | ★☆☆ |
| JVM-004 | JRE | ★☆☆ |
| JVM-005 | JDK | ★☆☆ |
| JVM-006 | JVM Interview Preparation Guide | ★☆☆ |
| JVM-009 | How Java Code Runs - Bytecode to Execution | ★★☆ |
| JVM-010 | Bytecode | ★★☆ |
| JVM-011 | Class Loader | ★★☆ |
| JVM-012 | Stack Memory | ★★☆ |
| JVM-013 | Heap Memory | ★★☆ |
| JVM-025 | Metaspace | ★★☆ |
| JVM-026 | Young Generation | ★★☆ |
| JVM-027 | Eden Space | ★★☆ |
| JVM-028 | Survivor Space | ★★☆ |
| JVM-029 | Old Generation | ★★☆ |
| JVM-030 | Minor GC | ★★☆ |
| JVM-031 | Serial GC | ★★☆ |
| JVM-032 | Parallel GC | ★★☆ |
| JVM-033 | GC Logs | ★★☆ |
| JVM-014 | Method Area | ★★☆ |
| JVM-015 | Heap Dump | ★★☆ |
| JVM-016 | Thread Dump | ★★☆ |
| JVM-017 | Stack Frame | ★★★ |
| JVM-018 | Operand Stack | ★★★ |
| JVM-034 | Local Variable Table | ★★★ |
| JVM-035 | Object Header | ★★★ |
| JVM-036 | Escape Analysis | ★★★ |
| JVM-019 | Memory Barrier | ★★★ |
| JVM-020 | Happens-Before | ★★★ |
| JVM-037 | GC Roots | ★★★ |
| JVM-038 | Reference Types (Strong, Soft, Weak, Phantom) | ★★★ |
| JVM-039 | Major GC | ★★★ |
| JVM-040 | Full GC | ★★★ |
| JVM-041 | Stop-The-World (STW) | ★★★ |
| JVM-021 | CMS (Concurrent Mark Sweep) | ★★★ |
| JVM-042 | G1GC | ★★★ |
| JVM-043 | ZGC | ★★★ |
| JVM-044 | Shenandoah GC | ★★★ |
| JVM-045 | GC Tuning | ★★★ |
| JVM-046 | GC Pause | ★★★ |
| JVM-047 | Throughput vs Latency (GC) | ★★★ |
| JVM-048 | Finalization | ★★★ |
| JVM-049 | JIT Compiler | ★★★ |
| JVM-050 | C1 C2 Compiler | ★★★ |
| JVM-051 | Tiered Compilation | ★★★ |
| JVM-052 | Method Inlining | ★★★ |
| JVM-053 | Deoptimization | ★★★ |
| JVM-054 | OSR (On-Stack Replacement) | ★★★ |
| JVM-055 | AOT (Ahead-of-Time Compilation) | ★★★ |
| JVM-056 | GraalVM | ★★★ |
| JVM-057 | Native Image | ★★★ |
| JVM-058 | TLAB (Thread Local Allocation Buffer) | ★★★ |
| JVM-059 | Safepoint | ★★★ |
| JVM-060 | Card Table | ★★★ |
| JVM-061 | Write Barrier | ★★★ |
| JVM-062 | Remembered Set | ★★★ |
| JVM-063 | GC Tuning Strategy for Production JVMs | ★★★ |
| JVM-064 | JVM Architecture Decisions at Scale | ★★★ |
| JVM-065 | JVM Selection Framework (HotSpot vs GraalVM) | ★★★ |
| JVM-066 | Heap Sizing and Memory Planning Strategy | ★★★ |
| JVM-067 | JVM Observability Strategy | ★★★ |
| JVM-068 | JVM Specification Deep Dive | ★★★ |
| JVM-069 | GC Algorithm Design Principles | ★★★ |
| JVM-070 | JIT Compilation Research (Truffle, Graal IR) | ★★★ |
| JVM-022 | JVM Language Design (Bytecode Targeting) | ★★★ |
| JVM-071 | JVM-First Debugging Mental Model | ★★★ |
| JVM-072 | Performance Intuition via JVM Internals | ★★★ |
| JVM-073 | GC Trade-off Framing | ★★★ |
| JVM-023 | PC Register (Program Counter) | ★★★ |
| JVM-024 | Native Method Stack | ★★★ |
| JVM-074 | JVM Safepoints and Stop-the-World Events | ★★★ |
| JVM-075 | Class Loading Delegation Model | ★★★ |
| JVM-076 | Compressed OOPs | ★★★ |
| JVM-076 | Class Data Sharing (CDS / AppCDS) | ★★★ |
| JVM-077 | GraalVM Truffle Framework | ★★★ |
| JVM-078 | JVM Bytecode Instrumentation | ★★★ |
| JVM-079 | JVM Startup Optimization (AppCDS, AOT) | ★★★ |
| JVM-080 | JVM Flags Reference and Tuning Guide | ★★★ |
