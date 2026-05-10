---
layout: default
title: "Java Concurrency"
parent: "Technical Dictionary"
nav_order: 12
has_children: true
permalink: /java-concurrency/
---

# Java Concurrency

Java threading, synchronization, concurrent data structures, executors, virtual threads, Project Loom, and the Java Memory Model.

**Keywords:** JCC-001–JCC-096 (96 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| JCC-001 | Why Concurrency Is Hard | ★☆☆ |
| JCC-002 | The Thread Safety Problem: A Mental Model | ★☆☆ |
| JCC-003 | Java Concurrency Approach: History and Philosophy | ★☆☆ |
| JCC-004 | Concurrency vs Parallelism in Java | ★☆☆ |
| JCC-005 | The Java Concurrency Ecosystem Map | ★☆☆ |
| JCC-006 | Thread (Java) | ★☆☆ |
| JCC-007 | Runnable | ★☆☆ |
| JCC-008 | Callable | ★☆☆ |
| JCC-009 | Future | ★☆☆ |
| JCC-037 | Thread Groups (Legacy) | ★☆☆ |
| JCC-012 | Java Concurrency Interview Preparation Guide | ★☆☆ |
| JCC-013 | Thread Lifecycle | ★★☆ |
| JCC-014 | Thread States | ★★☆ |
| JCC-038 | synchronized | ★★☆ |
| JCC-039 | Race Condition | ★★☆ |
| JCC-040 | Executor | ★★☆ |
| JCC-041 | ExecutorService | ★★☆ |
| JCC-042 | Semaphore (Java) | ★★☆ |
| JCC-043 | CountDownLatch | ★★☆ |
| JCC-044 | BlockingQueue | ★★☆ |
| JCC-015 | ScheduledExecutorService | ★★☆ |
| JCC-045 | CompletableFuture Composition Patterns | ★★☆ |
| JCC-046 | Parallel Streams | ★★☆ |
| JCC-016 | Fork-Join Framework Pattern | ★★☆ |
| JCC-017 | Thread Interruption and Cancellation | ★★☆ |
| JCC-047 | CompletionService | ★★☆ |
| JCC-048 | Condition Interface (Lock Conditions) | ★★☆ |
| JCC-049 | Daemon Threads | ★★☆ |
| JCC-050 | Thread Priority | ★★☆ |
| JCC-051 | ThreadFactory | ★★☆ |
| JCC-018 | Immutable Object Pattern | ★★☆ |
| JCC-019 | Producer-Consumer Pattern | ★★☆ |
| JCC-052 | Liveness Issues (Livelock / Starvation) | ★★☆ |
| JCC-053 | Concurrent Queue Variants (LinkedBlockingQueue, SynchronousQueue, DelayQueue) | ★★☆ |
| JCC-020 | Thread Safety Annotations (@GuardedBy, @ThreadSafe) | ★★☆ |
| JCC-054 | synchronized Block vs synchronized Method | ★★☆ |
| JCC-055 | CompletableFuture | ★★★ |
| JCC-056 | volatile | ★★★ |
| JCC-057 | wait notify notifyAll | ★★★ |
| JCC-058 | ReentrantLock | ★★★ |
| JCC-059 | ReadWriteLock | ★★★ |
| JCC-060 | StampedLock | ★★★ |
| JCC-061 | ThreadLocal | ★★★ |
| JCC-062 | Java Memory Model (JMM) | ★★★ |
| JCC-063 | CAS (Compare-And-Swap) | ★★★ |
| JCC-064 | Optimistic Locking (Java) | ★★★ |
| JCC-065 | ThreadPoolExecutor | ★★★ |
| JCC-066 | ForkJoinPool | ★★★ |
| JCC-067 | Virtual Threads (Project Loom) | ★★★ |
| JCC-068 | Carrier Thread | ★★★ |
| JCC-069 | Continuation | ★★★ |
| JCC-070 | CyclicBarrier | ★★★ |
| JCC-071 | Phaser | ★★★ |
| JCC-072 | ConcurrentHashMap | ★★★ |
| JCC-073 | CopyOnWriteArrayList | ★★★ |
| JCC-074 | Atomic Classes | ★★★ |
| JCC-075 | VarHandle | ★★★ |
| JCC-021 | Structured Concurrency | ★★★ |
| JCC-022 | Scoped Values | ★★★ |
| JCC-023 | Thread Dump Analysis | ★★★ |
| JCC-024 | Deadlock Detection (Java) | ★★★ |
| JCC-025 | Lock Striping | ★★★ |
| JCC-026 | Actor Model | ★★★ |
| JCC-027 | Concurrency Architecture Patterns in Java | ★★★ |
| JCC-076 | Virtual Thread Migration Strategy (Loom) | ★★★ |
| JCC-077 | Concurrent System Design at Scale | ★★★ |
| JCC-078 | Lock-Free Algorithm Strategy | ★★★ |
| JCC-079 | Thread Model Selection Framework | ★★★ |
| JCC-080 | Java Memory Model Specification Deep Dive | ★★★ |
| JCC-081 | Lock-Free Data Structure Design | ★★★ |
| JCC-082 | Concurrent Algorithm Research | ★★★ |
| JCC-083 | Structured Concurrency Design Principles | ★★★ |
| JCC-084 | Concurrency-First Thinking | ★★★ |
| JCC-085 | Shared State Risk Intuition | ★★★ |
| JCC-086 | Thread Safety Trade-off Framing | ★★★ |
| JCC-087 | Amdahl's Law | ★★★ |
| JCC-088 | Thread Pinning (Virtual Threads Problem) | ★★★ |
| JCC-028 | JMM Happens-Before - Deep Rules | ★★★ |
| JCC-029 | Lock-Free Data Structures | ★★★ |
| JCC-030 | Memory Visibility Diagnostics (jstack, JFR) | ★★★ |
| JCC-031 | False Sharing (Java Context) | ★★★ |
| JCC-032 | Busy-Wait vs Blocking | ★★★ |
| JCC-033 | JSR 133 - Java Memory Model Specification | ★★★ |
| JCC-089 | Project Loom Design Rationale | ★★★ |
| JCC-090 | Structured Concurrency Theory | ★★★ |
| JCC-010 | Reactive Streams Specification | ★★★ |
| JCC-091 | Actor Model Theory (Erlang / Akka Roots) | ★★★ |
| JCC-092 | Lock-Free Algorithm Theory (CAS Foundations) | ★★★ |
| JCC-034 | ABA Problem | ★★★ |
| JCC-035 | Work-Stealing Algorithm | ★★★ |
| JCC-036 | Double-Checked Locking Pattern | ★★★ |
| JCC-093 | ExecutorService Rejection Policies | ★★★ |
| JCC-011 | Java Reactive Programming (RxJava) | ★★★ |
| JCC-094 | Async Request Handling with Virtual Threads | ★★★ |
| JCC-095 | JMH Benchmarking for Concurrent Code | ★★★ |
| JCC-096 | Project Loom Migration Strategy | ★★★ |
