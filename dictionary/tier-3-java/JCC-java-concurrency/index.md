---
layout: default
title: "Java Concurrency"
parent: "Technical Dictionary"
nav_order: 9
has_children: true
permalink: /java-concurrency/
---

# Java Concurrency

Java threading, synchronization, concurrent data structures, executors, virtual threads, Project Loom, and the Java Memory Model.

**Keywords:** JCC-010–JCC-077 (68 terms · 40 original + 28 gap-fill)

> ⚠️ **Duplicates:** `JCC-001–JCC-009` are pre-existing duplicate files matching `JCC-037–JCC-043` and `JCC-046–JCC-047`. Canonical entries start at `JCC-010`. IDs JCC-001–009 are reserved for future reassignment.

| ID      | Keyword                                          | Difficulty |
|---------|--------------------------------------------------|------------|
| JCC-010 | Thread (Java)                                    | ★☆☆        |
| JCC-011 | Runnable                                         | ★☆☆        |
| JCC-012 | Callable                                         | ★★☆        |
| JCC-013 | Future                                           | ★★☆        |
| JCC-014 | CompletableFuture                                | ★★★        |
| JCC-015 | Thread Lifecycle                                 | ★★☆        |
| JCC-016 | Thread States                                    | ★★☆        |
| JCC-017 | synchronized                                     | ★★☆        |
| JCC-018 | volatile                                         | ★★★        |
| JCC-019 | wait / notify / notifyAll                        | ★★★        |
| JCC-020 | ReentrantLock                                    | ★★★        |
| JCC-021 | ReadWriteLock                                    | ★★★        |
| JCC-022 | StampedLock                                      | ★★★        |
| JCC-023 | ThreadLocal                                      | ★★★        |
| JCC-024 | Java Memory Model (JMM)                          | ★★★        |
| JCC-025 | Race Condition                                   | ★★☆        |
| JCC-026 | CAS (Compare-And-Swap)                           | ★★★        |
| JCC-027 | Optimistic Locking (Java)                        | ★★★        |
| JCC-028 | Executor                                         | ★★☆        |
| JCC-029 | ExecutorService                                  | ★★☆        |
| JCC-030 | ThreadPoolExecutor                               | ★★★        |
| JCC-031 | ForkJoinPool                                     | ★★★        |
| JCC-032 | Virtual Threads (Project Loom)                   | ★★★        |
| JCC-033 | Carrier Thread                                   | ★★★        |
| JCC-034 | Continuation                                     | ★★★        |
| JCC-035 | Semaphore (Java)                                 | ★★☆        |
| JCC-036 | CountDownLatch                                   | ★★☆        |
| JCC-037 | CyclicBarrier                                    | ★★★        |
| JCC-038 | Phaser                                           | ★★★        |
| JCC-039 | BlockingQueue                                    | ★★☆        |
| JCC-040 | ConcurrentHashMap                                | ★★★        |
| JCC-041 | CopyOnWriteArrayList                             | ★★★        |
| JCC-042 | Atomic Classes                                   | ★★★        |
| JCC-043 | VarHandle                                        | ★★★        |
| JCC-044 | Structured Concurrency                           | ★★★        |
| JCC-045 | Scoped Values                                    | ★★★        |
| JCC-046 | Thread Dump Analysis                             | ★★★        |
| JCC-047 | Deadlock Detection (Java)                        | ★★★        |
| JCC-048 | Lock Striping                                    | ★★★        |
| JCC-049 | Actor Model                                      | ★★★        |
| JCC-050 | Concurrency vs Parallelism (Java Context)        | ★☆☆        |
| JCC-051 | Thread Safety (Concept)                          | ★☆☆        |
| JCC-052 | Shared State Problem                             | ★☆☆        |
| JCC-053 | Deadlock (Conceptual)                            | ★☆☆        |
| JCC-054 | Immutable Object Pattern                         | ★★☆        |
| JCC-055 | Thread Pool (Conceptual)                         | ★★☆        |
| JCC-056 | Producer-Consumer Pattern                        | ★★☆        |
| JCC-057 | Liveness Issues (Livelock / Starvation)          | ★★☆        |
| JCC-058 | ScheduledExecutorService                         | ★★☆        |
| JCC-059 | CompletableFuture Composition Patterns           | ★★☆        |
| JCC-060 | Parallel Streams                                 | ★★☆        |
| JCC-061 | Fork-Join Framework Pattern                      | ★★☆        |
| JCC-062 | Thread Interruption and Cancellation             | ★★☆        |
| JCC-063 | CompletionService                                | ★★☆        |
| JCC-064 | Condition Interface (Lock Conditions)            | ★★☆        |
| JCC-065 | Amdahl's Law                                     | ★★★        |
| JCC-066 | Thread Pinning (Virtual Threads Problem)         | ★★★        |
| JCC-067 | JMM Happens-Before — Deep Rules                  | ★★★        |
| JCC-068 | Lock-Free Data Structures                        | ★★★        |
| JCC-069 | Memory Visibility Diagnostics (jstack, JFR)      | ★★★        |
| JCC-070 | False Sharing (Java Context)                     | ★★★        |
| JCC-071 | Busy-Wait vs Blocking                            | ★★★        |
| JCC-072 | JSR 133 — Java Memory Model Specification        | 🔬          |
| JCC-073 | Project Loom Design Rationale                    | 🔬          |
| JCC-074 | Structured Concurrency Theory                    | 🔬          |
| JCC-075 | Reactive Streams Specification                   | 🔬          |
| JCC-076 | Actor Model Theory (Erlang / Akka Roots)         | 🔬          |
| JCC-077 | Lock-Free Algorithm Theory (CAS Foundations)     | 🔬          |
