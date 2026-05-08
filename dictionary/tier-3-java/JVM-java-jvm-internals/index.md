---
layout: default
title: "Java & JVM Internals"
parent: "Technical Dictionary"
nav_order: 7
has_children: true
permalink: /java/
---

# Java & JVM Internals

JVM architecture, memory model, garbage collection algorithms, JIT compilation, GraalVM, AOT, and creator-level JVM specification theory.

**Keywords:** JVM-002–JVM-075 (74 terms · 50 original + 24 gap-fill)

> ⚠️ **Duplicate:** `JVM-001` (`G1GC.md`) is a pre-existing duplicate of `JVM-030` (`G1GC`). Canonical entries start at `JVM-002`. `JVM-001` reserved for future reassignment.

| ID      | Keyword                                          | Difficulty |
|---------|--------------------------------------------------|------------|
| JVM-002 | JVM                                              | ★☆☆        |
| JVM-003 | JRE                                              | ★☆☆        |
| JVM-004 | JDK                                              | ★☆☆        |
| JVM-005 | Bytecode                                         | ★★☆        |
| JVM-006 | Class Loader                                     | ★★☆        |
| JVM-007 | Stack Memory                                     | ★★☆        |
| JVM-008 | Heap Memory                                      | ★★☆        |
| JVM-009 | Metaspace                                        | ★★☆        |
| JVM-010 | Stack Frame                                      | ★★★        |
| JVM-011 | Operand Stack                                    | ★★★        |
| JVM-012 | Local Variable Table                             | ★★★        |
| JVM-013 | Object Header                                    | ★★★        |
| JVM-014 | Escape Analysis                                  | ★★★        |
| JVM-015 | Memory Barrier                                   | ★★★        |
| JVM-016 | Happens-Before                                   | ★★★        |
| JVM-017 | GC Roots                                         | ★★★        |
| JVM-018 | Reference Types (Strong, Soft, Weak, Phantom)    | ★★★        |
| JVM-019 | Young Generation                                 | ★★☆        |
| JVM-020 | Eden Space                                       | ★★☆        |
| JVM-021 | Survivor Space                                   | ★★☆        |
| JVM-022 | Old Generation                                   | ★★☆        |
| JVM-023 | Minor GC                                         | ★★☆        |
| JVM-024 | Major GC                                         | ★★★        |
| JVM-025 | Full GC                                          | ★★★        |
| JVM-026 | Stop-The-World (STW)                             | ★★★        |
| JVM-027 | Serial GC                                        | ★★☆        |
| JVM-028 | Parallel GC                                      | ★★☆        |
| JVM-029 | CMS (Concurrent Mark Sweep)                      | ★★★        |
| JVM-030 | G1GC                                             | ★★★        |
| JVM-031 | ZGC                                              | ★★★        |
| JVM-032 | Shenandoah GC                                    | ★★★        |
| JVM-033 | GC Tuning                                        | ★★★        |
| JVM-034 | GC Logs                                          | ★★☆        |
| JVM-035 | GC Pause                                         | ★★★        |
| JVM-036 | Throughput vs Latency (GC)                       | ★★★        |
| JVM-037 | Finalization                                     | ★★★        |
| JVM-038 | JIT Compiler                                     | ★★★        |
| JVM-039 | C1 / C2 Compiler                                 | ★★★        |
| JVM-040 | Tiered Compilation                               | ★★★        |
| JVM-041 | Method Inlining                                  | ★★★        |
| JVM-042 | Deoptimization                                   | ★★★        |
| JVM-043 | OSR (On-Stack Replacement)                       | ★★★        |
| JVM-044 | AOT (Ahead-of-Time Compilation)                  | ★★★        |
| JVM-045 | GraalVM                                          | ★★★        |
| JVM-046 | Native Image                                     | ★★★        |
| JVM-047 | TLAB (Thread Local Allocation Buffer)            | ★★★        |
| JVM-048 | Safepoint                                        | ★★★        |
| JVM-049 | Card Table                                       | ★★★        |
| JVM-050 | Write Barrier                                    | ★★★        |
| JVM-051 | Remembered Set                                   | ★★★        |
| JVM-052 | What is the JVM (Layperson Overview)             | ★☆☆        |
| JVM-053 | Java Platform Independence                       | ★☆☆        |
| JVM-054 | JVM Languages (Kotlin, Scala, Groovy)            | ★☆☆        |
| JVM-055 | Garbage Collection (Basic Concept)               | ★☆☆        |
| JVM-056 | Classpath                                        | ★☆☆        |
| JVM-057 | JVM Flags Overview (-Xmx, -Xms, -XX:)           | ★★☆        |
| JVM-058 | Memory Allocation (Eden → Survivor → Old Flow)   | ★★☆        |
| JVM-059 | Object Lifecycle in JVM                          | ★★☆        |
| JVM-060 | Class File Format                                | ★★☆        |
| JVM-061 | JVM Execution Engine                             | ★★☆        |
| JVM-062 | Code Cache                                       | ★★★        |
| JVM-063 | Method Area vs Metaspace                         | ★★★        |
| JVM-064 | JVM Diagnostic Tools (jcmd, jstack, jmap)        | ★★★        |
| JVM-065 | Out-of-Memory Error Types (and Diagnosis)        | ★★★        |
| JVM-066 | Heap Dump Analysis                               | ★★★        |
| JVM-067 | JIT Thresholds and Tiered Compilation Flags      | ★★★        |
| JVM-068 | Speculative Optimizations                        | ★★★        |
| JVM-069 | Epsilon GC (No-Op GC)                            | ★★★        |
| JVM-070 | JVM Specification (JVMS)                         | 🔬          |
| JVM-071 | Generational Hypothesis Theory                   | 🔬          |
| JVM-072 | Project Valhalla (JVM Value Objects)             | 🔬          |
| JVM-073 | Project Lilliput (Compact Object Headers)        | 🔬          |
| JVM-074 | CRaC (Coordinated Restore at Checkpoint)         | 🔬          |
| JVM-075 | LLVM vs JVM Architecture Comparison              | 🔬          |
