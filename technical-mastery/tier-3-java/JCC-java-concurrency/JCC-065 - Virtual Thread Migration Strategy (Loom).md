---
id: JCC-076
title: "Virtual Thread Migration Strategy (Loom)"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-049, JCC-017, JCC-064
used_by: JCC-066, JCC-068
related: JCC-049, JCC-064, JCC-068
tags:
  - java
  - concurrency
  - advanced
  - architecture
  - performance
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/jcc/virtual-thread-migration-strategy-loom/
---

⚡ TL;DR - Migrating to Virtual Threads in Java 21 is not a drop-in replacement: you must replace thread pool tuning with virtual threads, eliminate `ThreadLocal` misuse, fix `synchronized` pinning, and re-examine connection pool sizing.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | JCC-049, JCC-017, JCC-064 |     |
| **Used by:**    | JCC-066, JCC-068          |     |
| **Related:**    | JCC-049, JCC-064, JCC-068 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams hear "Virtual Threads are just drop-in replacements for thread pools" and change one line: `Executors.newFixedThreadPool(200)` to `Executors.newVirtualThreadPerTaskExecutor()`. The service deploys. Throughput does not improve. Latency degrades. Thread dumps show VT threads "pinned." `ThreadLocal` variables hold stale request-scoped data across unrelated requests. The team reverts and concludes "Virtual Threads don't work."

**THE BREAKING POINT:**
Without a migration strategy, three classes of problems appear: (1) `synchronized` blocks pin Virtual Threads to carrier threads, eliminating VT's concurrency benefit on those paths; (2) `ThreadLocal` caches sized for 200-thread pools now scale to 10,000 VT threads, consuming gigabytes of memory; (3) connection pools sized for 200 threads become the bottleneck when 10,000 VT threads compete for 200 connections.

**THE INVENTION MOMENT:**
Virtual Thread migration is a three-phase engineering effort: **identify** blocking patterns and `ThreadLocal` usage, **fix** pinning and cache issues, **resize** dependent resources (connection pools, semaphores). This entry systematizes the migration decision tree.

**EVOLUTION:**
Java 21 (LTS): Virtual Threads stable. Java 22-23: JEP 491 proposes making `synchronized` VT-friendly (eliminating pinning). Java 24+: Pinning fix expected to land, removing a major migration obstacle. Migration strategy must account for target Java version.

---

### 📘 Textbook Definition

**Virtual Thread migration strategy** is the set of code, configuration, and architecture changes required to successfully replace platform thread pools with `Executors.newVirtualThreadPerTaskExecutor()` (or `Thread.ofVirtual()`) in a Java 21+ application. The strategy addresses four migration concerns: **thread pool replacement** (removing manual pool sizing), **pinning elimination** (replacing `synchronized` with `ReentrantLock`), **ThreadLocal cleanup** (preventing memory bloat at VT scale), and **resource pool resizing** (connection pools, semaphores). Done correctly, the migration reduces latency and increases throughput for I/O-bound services with minimal code changes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Virtual Thread migration = swap thread pool + fix synchronized + clean ThreadLocal + resize connection pools.

**One analogy:**

> Migrating to Virtual Threads is like switching from a bus system (fixed-route, fixed-seat platform threads) to an on-demand ride-share (Virtual Threads spun up per request). The switch works well only if the road network (connection pools), traffic rules (synchronized blocks), and passenger habits (ThreadLocal) are updated to match the new model.

**One insight:**
Virtual Threads eliminate the OS thread as the concurrency bottleneck, but they expose every other concurrency bottleneck more clearly: connection pool limits, synchronized pinning, and ThreadLocal memory grow proportionally with concurrency, not thread count. Migration is as much about removing old assumptions as adding new infrastructure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Virtual Threads are cheap to create** - create one per request/task. Do not pool them.
2. **Blocking inside a `synchronized` block pins the VT to its carrier thread** - this blocks a carrier thread (OS thread), eliminating VT's concurrency benefit on that path.
3. **`ThreadLocal` variables are per-VT** - with 100,000 VTs, 100,000 ThreadLocal copies exist simultaneously. Caches stored in ThreadLocal multiply by VT count.
4. **Connection pools are still bounded** - 10,000 VTs competing for 20 DB connections: 9,980 VTs block on the pool. This is expected and correct, but pool sizing must be deliberate.

**DERIVED DESIGN:**
Given invariant 2: replace all `synchronized` blocks on hot paths with `ReentrantLock` (VT-aware; does not pin). Given invariant 3: audit all `ThreadLocal` usages; replace connection/buffer caches with shared pools; use `ScopedValue` (Java 21 preview, stable in Java 23) for request-scoped data.

**THE TRADE-OFFS:**

**Gain:** Dramatically higher I/O-bound concurrency, simpler thread pool sizing (no manual tuning), full stack traces per request.

**Cost:** Migration effort, pinning risk from `synchronized` in library code, connection pool pressure, ThreadLocal memory if not cleaned up.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** I/O-bound concurrency requires a large number of concurrent tasks. Virtual Threads solve this structurally.

**Accidental:** `synchronized` pinning, ThreadLocal bloat, connection pool starvation. These are implementation artifacts of the platform thread world that must be cleaned up.

---

### 🧪 Thought Experiment

**SETUP:**
A Spring Boot service handles 5,000 concurrent requests. Each request does one DB query (10ms) and one HTTP call (50ms). The original design: `Tomcat` with 200 platform threads.

**WITH 200 PLATFORM THREADS:**
200 threads x (10ms DB + 50ms HTTP) = 200 threads x 60ms average occupation.
Throughput = 200 / 0.060s = ~3,333 req/s maximum.
Latency spikes when all 200 threads are occupied and requests queue up.

**MIGRATING TO VIRTUAL THREADS (naive):**
Change Tomcat thread pool to Virtual Threads. Now 5,000 requests each get a VT. 5,000 VTs block on DB queries and HTTP calls. The JVM handles the blocking efficiently. Throughput ceiling moves to the DB connection limit.

**WHAT CAN GO WRONG:**
DB connection pool is still 20. 5,000 VTs compete for 20 connections. 4,980 VTs block efficiently (correct), but if DB cannot handle 5,000 concurrent query submissions, DB becomes the bottleneck.
`synchronized (dbConnectionCache)` on a hot path - all VTs trying to acquire DB connections pin to carrier threads - OOM on carrier threads.

**THE INSIGHT:**
Virtual Thread migration shifts the bottleneck from thread count to resource limits (connections, external service capacity). This is the correct bottleneck - it is fundamental, not artificial. The migration is successful if the bottleneck is now DB/network capacity, not thread count.

---

### 🧠 Mental Model / Analogy

> Migrating to Virtual Threads is like upgrading a warehouse from 200 dedicated workers (platform threads) to on-demand gig workers (Virtual Threads). The upgrade works - you can now process 10,000 orders simultaneously. But you must also upgrade: the loading dock (connection pool) from 10 bays to 200 bays, remove lockers assigned to each worker (ThreadLocal), and replace locked filing cabinets (synchronized) with open-shelf systems (ReentrantLock). The workers are now unlimited; the infrastructure must match.

Element mapping:

- **Dedicated workers** = platform threads in a fixed pool
- **Gig workers** = Virtual Threads (one per task)
- **Loading dock capacity** = database connection pool size
- **Assigned lockers** = ThreadLocal variables
- **Locked filing cabinet** = `synchronized` block causing pinning
- **Open shelf** = `ReentrantLock` (non-pinning)

Where this analogy breaks down: gig workers have variable skill and reliability; Virtual Threads are identical to platform threads in behavior (just lighter weight).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Virtual Thread migration is the process of safely replacing expensive platform thread pools with cheap Virtual Threads, while fixing a few known incompatibilities so the performance gains actually materialize.

**Level 2 - How to use it (junior developer):**
For Spring Boot 3.2+ (Java 21+):

```yaml
# application.properties - enable Virtual Threads in Tomcat
spring.threads.virtual.enabled=true
```

This is the minimum change. Then audit logs for JVM pinning warnings and check connection pool sizing.

**Level 3 - How it works (mid-level engineer):**
Virtual Thread migration involves 4 steps:

1. **Enable VT executor** (`newVirtualThreadPerTaskExecutor()` or `spring.threads.virtual.enabled=true`)
2. **Diagnose pinning** (JVM flag `-Djdk.tracePinnedThreads=full`, look for `synchronized` on blocking hot paths)
3. **Fix pinning** (replace `synchronized` with `ReentrantLock`)
4. **Resize connection pools** (size for desired concurrency, not thread count)

**Level 4 - Why it was designed this way (senior/staff):**
The migration challenges are inherent to Project Loom's design decision to implement Virtual Threads as coroutines scheduled on a small pool of carrier (OS) threads. When a VT encounters a blocking operation, it unmounts from the carrier - unless it is inside a `synchronized` block (native monitor), where it must stay mounted (pinned). This constraint exists because JVM object monitors are tied to OS threads. The long-term fix (JEP 491, Java 24) re-implements `synchronized` to be VT-aware, eliminating pinning. Until then, migration requires replacing `synchronized` with `ReentrantLock` on blocking-critical paths.

**Expert Thinking Cues:**

- "Where does my application block? Those are the VT-eligible paths."
- "Which paths use `synchronized` AND block? Those need `ReentrantLock`."
- "What resources are shared across requests? Those need proper pooling at the new concurrency scale."

---

### ⚙️ How It Works (Mechanism)

**Step 1 - Replace Thread Pool:**

```java
// BAD: manually tuned platform thread pool
ExecutorService exec = Executors.newFixedThreadPool(200);

// GOOD: Virtual Thread per task (Java 21+)
ExecutorService exec =
    Executors.newVirtualThreadPerTaskExecutor();
// Do NOT pool Virtual Threads - create per task
```

**Step 2 - Diagnose and Fix Pinning:**

```bash
# Enable pinning diagnostics
-Djdk.tracePinnedThreads=full
# Output shows file:line where pinning occurs
```

```java
// BAD: synchronized wraps blocking call - causes pinning
synchronized (this) {
    result = database.query(sql); // blocks -> pinned!
}

// GOOD: ReentrantLock is VT-aware (no pinning)
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    result = database.query(sql); // blocks, unmounts VT
} finally {
    lock.unlock();
}
```

**Step 3 - Fix ThreadLocal Bloat:**

```java
// BAD: thread-local connection cache
// At 50,000 VTs: 50,000 connection objects in memory
ThreadLocal<Connection> connCache = new ThreadLocal<>();

// GOOD: shared connection pool (HikariCP)
DataSource pool = createHikariPool(maxPoolSize);
// Use ScopedValue for request-scoped data (Java 21+)
ScopedValue<RequestContext> CTX = ScopedValue.newInstance();
ScopedValue.where(CTX, new RequestContext(req))
    .run(() -> handleRequest());
```

**Step 4 - Resize Connection Pools:**

```java
// BAD: pool sized for thread count (200)
cfg.setMaximumPoolSize(200);

// GOOD: size for actual DB capacity
cfg.setMaximumPoolSize(400); // if DB handles 400 concurrent
// VTs exceeding pool size block efficiently waiting
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MIGRATION DECISION FLOW:**

```
Start: Java 21+, want Virtual Threads
    |
    +- Step 1: Instrument
    |   -Djdk.tracePinnedThreads=full
    |   Profile ThreadLocal usage, pool size
    |
    +- Step 2: Identify issues
    |   Pinning? -> synchronized wrapping blocking
    |   ThreadLocal caches? -> multiplies per VT
    |   Connection pool too small? -> starves  <- YOU ARE
      HERE
    |
    +- Step 3: Fix
    |   synchronized -> ReentrantLock
    |   ThreadLocal caches -> shared pools
    |   Resize connection pools
    |
    +- Step 4: Enable VT executor
    |   newVirtualThreadPerTaskExecutor()
    |   spring.threads.virtual.enabled=true
    |
    +- Step 5: Load test and observe
        VT count, pinning events, pool wait times
```

**FAILURE PATH:**
Skip Steps 2-3, go straight to Step 4. Pinned VTs exhaust carrier threads. Throughput worse than before. Team reverts. True cause: synchronized on blocking hot path not fixed.

**WHAT CHANGES AT SCALE:**
At high concurrency (100,000+ VTs), carrier thread exhaustion from pinning becomes severe. The `ForkJoinPool` carrier pool defaults to CPU core count (e.g., 8). If all 8 carrier threads are pinned, 99,992 VTs are stalled. The symptom looks like 100% CPU with near-zero throughput.

---

### ⚖️ Comparison Table

| Aspect                  | Platform Thread Pool    | Virtual Thread Per Task |
| ----------------------- | ----------------------- | ----------------------- |
| Creation cost           | High (OS thread)        | Near-zero (JVM-managed) |
| Optimal for             | I/O + CPU mix, Java <21 | I/O-heavy, Java 21+     |
| Thread count            | Manual tuning required  | Automatic (1 per task)  |
| Blocking                | Wastes OS thread        | Unmounts from carrier   |
| `synchronized` blocking | Fine                    | Pins carrier (problem!) |
| ThreadLocal memory      | Scales with pool size   | Scales with VT count    |
| Stack trace quality     | Full                    | Full                    |
| Pool warmup             | Needed                  | Not needed              |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                         |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| "VTs eliminate the need for connection pools"       | Connection pools are MORE important. Without bounds, 10,000 VTs could open 10,000 DB connections, exhausting the DB.            |
| "All `synchronized` blocks cause pinning"           | Pinning only occurs when a VT blocks (I/O, sleep, lock wait) INSIDE a `synchronized` block. Pure-CPU synchronized does not pin. |
| "VTs are faster than platform threads for CPU work" | VTs have no CPU advantage. They benefit only I/O-bound workloads.                                                               |
| "Pooling VTs improves performance"                  | Pooling VTs is an anti-pattern. VTs are cheap to create; pooling reintroduces pool-sizing problems.                             |
| "`ScopedValue` completely replaces `ThreadLocal`"   | `ScopedValue` replaces ThreadLocal for request-scoped propagation. ThreadLocal remains appropriate for other uses.              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Carrier Thread Exhaustion from Pinning**
**Symptom:** After VT migration, throughput is worse. CPU is high but threads are mostly BLOCKED.

**Root Cause:** Hot paths use `synchronized` wrapping blocking calls. All carrier threads pinned.

**Diagnostic:**

```bash
-Djdk.tracePinnedThreads=full
# Output: Thread[...] pinned at Service.doWork:87
# synchronized block wrapping database.query()
```

**Fix:** Replace `synchronized` wrapping blocking code with `ReentrantLock`.

**Prevention:** Before migration, search for `synchronized` + blocking patterns.

---

**Failure Mode 2: ThreadLocal Memory Bloat**
**Symptom:** Heap grows 10-100x after VT migration. OOM errors under load.

**Root Cause:** ThreadLocal caches instantiated per-VT. 100,000 VTs = 100,000 cache copies.

**Diagnostic:**

```bash
jmap -histo <pid> | head -30
# Large counts of types previously stored in ThreadLocal
```

**Fix:**

```java
// BAD: ThreadLocal resource - multiplies per VT
ThreadLocal<Connection> CONN = new ThreadLocal<>();

// GOOD: shared pool managed by HikariCP
```

**Prevention:** Audit all `ThreadLocal` usages before migration. Replace resource caches with shared pools.

---

**Failure Mode 3: Connection Pool Starvation**
**Symptom:** After VT migration, DB timeouts increase. "Timeout waiting for connection from pool."

**Root Cause:** Pool sized for old thread count (200). With VTs, 10,000 requests compete for 200 connections.

**Diagnostic:**

```bash
# HikariCP Micrometer metric
hikaricp_connections_pending{pool="HikariPool-1"}
# High value = pool too small
```

**Fix:**

```java
// Increase pool size to match DB capacity
cfg.setMaximumPoolSize(500);
cfg.setConnectionTimeout(3000);
```

**Prevention:** Before migration, determine actual DB connection capacity. Size pool to DB capacity, not thread pool size.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-049 - Virtual Threads (Project Loom)]] - VT fundamentals before migration
- [[JCC-017 - ExecutorService]] - the service being replaced

**Builds On This (learn these next):**

- [[JCC-066 - Concurrent System Design at Scale]] - system design with VTs
- [[JCC-068 - Thread Model Selection Framework]] - when to use VTs vs. reactive

**Alternatives / Comparisons:**

- [[JCC-064 - Concurrency Architecture Patterns in Java]] - patterns context
- [[JCC-049 - Virtual Threads (Project Loom)]] - the underlying feature

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ VT migration checklist: 4 steps    │
│ PROBLEM       │ Naive VT swap causes new failures  │
│ KEY INSIGHT   │ Fix sync pinning + resize pools    │
│ USE WHEN      │ Java 21+, I/O-bound services       │
│ AVOID WHEN    │ CPU-bound workloads (VTs no help)  │
│ TRADE-OFF     │ Migration effort vs. throughput    │
│ ONE-LINER     │ VT swap + fix pinning + pools      │
│ NEXT EXPLORE  │ JCC-066 Scale, JCC-068 Selection   │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Replace `synchronized`-wrapping-blocking with `ReentrantLock` before enabling VTs.
2. Audit all `ThreadLocal` caches - they scale with VT count, not thread pool size.
3. Resize connection pools based on DB capacity, not thread count.

**Interview one-liner:**
"Virtual Thread migration requires four changes: enable VT executor, eliminate synchronized pinning by replacing with ReentrantLock, replace ThreadLocal caches with shared pools, and resize connection pools to DB capacity - skipping any step causes the migration to underperform or fail."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When upgrading a concurrency model, the upgrade removes one bottleneck but reveals the next. Thread count was the bottleneck with platform threads; connection/resource limits become the bottleneck with VTs. Every architectural upgrade shifts, not removes, the system's bottleneck - plan for the next one.

**Where else this pattern appears:**

- **Node.js async I/O migration:** Moving from blocking to async I/O reveals DB connection limits and external API rate limits - the same pattern of the bottleneck shifting to the I/O resource limit.
- **Go goroutines:** Goroutine-heavy services hit the same pattern: goroutine count is cheap, but DB connections and external service limits become the ceiling.
- **HikariCP pool sizing guidance:** "You want a small pool, saturated with threads waiting for connections." This wisdom predates VTs but perfectly describes the VT connection pool model.

---

### 💡 The Surprising Truth

The biggest performance gain from Virtual Threads in many production systems does not come from increased throughput - it comes from dramatically simpler code. With platform threads, developers write complex async code (CompletableFuture chains, reactive streams, callback pyramids) to avoid blocking expensive threads. With Virtual Threads, they write blocking code (simple, sequential, debuggable) and get the same throughput. The gain is not just in the runtime - it is in developer productivity, code readability, and debuggability. Stack traces become readable again. Debuggers work correctly. For many teams, the 10x reduction in code complexity is more valuable than the 2-3x throughput improvement.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A library your service depends on uses `synchronized` extensively. You cannot modify it. You want to migrate to VTs. What are your options and their trade-offs?
_Hint:_ Consider: using the library on platform threads only, waiting for library update, replacing the library, or measuring actual pinning impact with `-Djdk.tracePinnedThreads`.

**Q2 (A - System Interaction):** Spring Boot 3.2 enables VTs for Tomcat with one property. How does this interact with Spring's `@Transactional`, which binds a `Connection` to the current thread? Does the transaction still work correctly?
_Hint:_ Spring binds transaction state to `ThreadLocal`. Consider what happens when a VT unmounts mid-transaction - is the ThreadLocal state preserved on the VT?

**Q3 (E - First Principles):** VT stacks default to 256KB (expandable). If a service creates 1,000,000 VTs simultaneously, what is the theoretical memory requirement? How does lazy stack allocation change this estimate?
_Hint:_ VT stacks are lazily allocated by the JVM. What does lazy allocation mean for VTs mostly blocking on I/O with shallow stacks?
