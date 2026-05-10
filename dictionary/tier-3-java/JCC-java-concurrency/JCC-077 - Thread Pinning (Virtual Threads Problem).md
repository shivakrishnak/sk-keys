---
id: JCC-088
title: "Thread Pinning (Virtual Threads Problem)"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-019, JCC-052, JCC-014
used_by: JCC-080
related: JCC-053, JCC-062, JCC-025
tags:
  - java
  - concurrency
  - performance
  - advanced
  - jvm
status: complete
version: 3
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 77
permalink: /java-concurrency/thread-pinning-virtual-threads-problem/
---

# JCC-077 - THREAD PINNING (VIRTUAL THREADS PROBLEM)

⚡ **TL;DR** - Thread pinning occurs when a virtual thread is
*stuck* to its carrier thread during a blocking call inside a
`synchronized` block, preventing other virtual threads from
using that carrier.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-019 Virtual Threads (Project Loom), JCC-052 Carrier Thread, JCC-014 Future |
| Used by    | JCC-080 Memory Visibility Diagnostics              |
| Related    | JCC-053 Continuation, JCC-062 Structured Concurrency, JCC-025 Thread Interruption |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Virtual threads (Java 21) are designed to unmount from carrier
threads during blocking I/O, allowing millions of virtual threads
to run on a small carrier pool. But `synchronized` blocks prevent
unmounting - the virtual thread stays *pinned* to its carrier.
A system migrating to virtual threads can inadvertently reintroduce
the same carrier-thread starvation that platform threads had.

**THE BREAKING POINT:**
A JDBC driver uses `synchronized` internally. A virtual thread
calls `connection.executeQuery()` which internally blocks on a
`synchronized` socket read. The virtual thread cannot unmount.
The carrier thread is occupied. With 100 concurrent queries and
only 8 carriers, 8 virtual threads pin all 8 carriers. Remaining
92 virtual threads cannot run until a carrier frees.

**THE INVENTION MOMENT:**
Project Loom identified pinning as the primary compatibility issue
when adopting virtual threads in existing codebases. The JVM tracks
pinning and `jdk.VirtualThreadPinned` JFR events expose it.

**EVOLUTION:**
- **Java 21:** Virtual threads GA; `synchronized` causes pinning;
  JFR event `jdk.VirtualThreadPinned` added for detection
- **Java 24+ (planned):** JEP 491 - synchronize virtual threads
  without pinning (allowing `synchronized` to unmount like
  `ReentrantLock`). Once merged, pinning will become historical.

---

### 📘 Textbook Definition

**Thread pinning** is the state where a virtual thread cannot
unmount from its carrier thread because it is:
1. Executing code inside a `synchronized` block or method, OR
2. Executing a `native` method or `@Scope(NATIVE)` call

While pinned, the carrier is monopolised: no other virtual thread
can use it. This negates virtual thread scalability gains for the
duration of the blocking call.

**Unmounting** = virtual thread suspends and releases the carrier
(normal behaviour during `park`, `sleep`, blocking I/O).
**Pinning** = virtual thread retains the carrier (degraded
behaviour, treated like a platform thread blocking).

---

### ⏱️ Understand It in 30 Seconds

**One line:** `synchronized` blocks act like superglue - a virtual
thread stuck inside one cannot release its carrier thread to serve
others.

**One analogy:**
> Virtual threads are like Uber drivers who normally drop a passenger
> off and immediately pick up the next. Pinning is when a passenger
> locks the car door from inside - the driver cannot take another
> passenger until that lock is released, even if the passenger is
> just reading a map.

**One insight:** Replace `synchronized` with `ReentrantLock` in
blocking paths. `ReentrantLock.lock()` allows virtual thread
unmounting; `synchronized` does not (until JEP 491).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Virtual threads unmount by capturing their continuation
   (stack state) and parking. This requires the JVM to know it
   is safe to detach from the carrier.
2. `synchronized` uses native object monitors (JVM monitorenter
   instruction) that are tied to the *carrier* thread's OS stack
   frame - they cannot be transferred to another carrier.
3. `ReentrantLock` maintains lock state in Java objects (AQS),
   which travel with the virtual thread's continuation.
4. Pinning does not cause errors - it silently degrades
   performance, making virtual threads behave like platform threads.
5. The JVM compensates by potentially adding carrier threads (up to
   `jdk.virtualThreadScheduler.maxPoolSize`) when pinning is
   detected, but this is bounded and may cause resource issues.

**DERIVED DESIGN:**
The JVM cannot reimplement object monitors in pure Java without
breaking binary compatibility for `synchronized`. Hence the
temporary pinning constraint - JEP 491 addresses this with a
redesigned monitor that is continuation-aware.

**THE TRADE-OFFS:**

**Gain without fix:** Existing `synchronized` code works correctly
(just slower). No correctness issues.

**Cost:** Virtual thread scalability benefits are lost wherever
pinning occurs. Library code using `synchronized` (JDBC drivers,
many frameworks) causes hidden pinning.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Object monitors must guarantee mutual exclusion -
this requirement is non-negotiable.

**Accidental:** Tying monitors to OS threads (rather than
continuations) is an implementation choice, not a fundamental
requirement. JEP 491 removes this accidental constraint.

---

### 🧪 Thought Experiment

**SETUP:** A web server uses virtual threads for each request.
Each request calls `dao.findById()`, which internally uses JDBC
with `synchronized` socket reads. Pool has 8 carrier threads.

**WHAT HAPPENS WITH pinning:**
```
100 concurrent requests arrive
Requests 1-8: acquire carrier, execute, JDBC blocks (pinning!)
  -> 8 carriers all pinned
Requests 9-100: wait for a carrier thread to free
  -> no concurrency benefit despite virtual threads
  -> throughput = 8 concurrent ops (same as 8 platform threads)
```

**WHAT HAPPENS after replacing JDBC with R2DBC or HikariCP 6.0+:**
```
100 concurrent requests arrive
All 100 acquire carriers initially
JDBC async drivers don't use synchronized
Virtual threads unmount during DB wait
Carriers free to serve other virtual threads
-> throughput: 100 concurrent logical ops on 8 carriers
```

**THE INSIGHT:** Virtual thread benefits require that blocking code
paths be free of `synchronized` on the hot path.

---

### 🧠 Mental Model / Analogy

> Virtual threads are event-loop workers in disguise. They park
> during blocking calls and let others run. Thread pinning is like
> an event handler that makes a synchronous blocking system call -
> it freezes the event loop. The fix is the same: make blocking
> calls asynchronous or use non-blocking alternatives.

**Element mapping:**
- Event loop = ForkJoinPool carrier thread pool
- Event handler = virtual thread
- Asynchronous callback = virtual thread unmounting
- Blocking syscall = `synchronized` + blocking I/O
- Frozen event loop = pinned carrier thread
- Async OS I/O = `ReentrantLock` + blocking I/O (allows unmounting)

Where this analogy breaks down: virtual threads still use
blocking-style code (not callbacks), making the programming model
simpler than a real event loop. Pinning is a JVM-level detail,
invisible in the source code.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When a virtual thread runs inside a `synchronized` block, it is
stuck to its worker thread until it leaves - it can't take a break
to let other virtual threads use that worker.

**Level 2 - How to use it (junior developer):**
Spot and replace `synchronized` in performance-critical blocking paths:
```java
// BAD: synchronized causes pinning in virtual thread
synchronized (lock) {
    result = jdbcQuery(); // blocks here! pinning occurs
}

// GOOD: ReentrantLock allows virtual thread to unmount
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    result = jdbcQuery(); // virtual thread can unmount here
} finally { lock.unlock(); }
```

**Level 3 - How it works (mid-level engineer):**
The JVM's virtual thread scheduler (a `ForkJoinPool`) parks virtual
threads via `LockSupport.park()`. A parked virtual thread serialises
its continuation (Java stack) into a heap object, unmounts from the
carrier, and yields the carrier to the ForkJoinPool for other virtual
threads. `synchronized` uses `monitorenter` bytecode which calls
`ObjectMonitor::enter`, maintaining lock ownership via the OS thread
pointer - which cannot be transferred to a different carrier. Thus
the JVM cannot unmount a virtual thread that holds or is waiting for
a monitor.

**Level 4 - Why it was designed this way (senior/staff):**
The JVM specification ties object monitors to threads (not arbitrary
objects) for historical reasons - the specification predates virtual
threads by 25 years. Binary compatibility with existing class files
that use `monitorenter/monitorexit` bytecodes cannot be violated
without breaking every compiled library. JEP 491 solves this by
reimplementing object monitors as continuation-aware structures in
the JVM itself, maintaining binary compatibility while enabling
unmounting.

**Expert Thinking Cues:**
- Enable JFR pinning events in production: `jdk.VirtualThreadPinned`
  with threshold 20ms reveals hot pinning paths.
- Third-party library pinning: JDBC (most drivers), some Spring
  security internals, certain serialisation libraries.
- `native` methods also pin - virtual threads calling native code
  for `ProcessBuilder`, `FileInputStream` (old API) are pinned.
- Mitigation for third-party libraries: increase
  `jdk.virtualThreadScheduler.maxPoolSize` to allow compensation
  threads, but this is a band-aid not a fix.

---

### ⚙️ How It Works (Mechanism)

**Normal virtual thread lifecycle (no pinning):**
```
VT parks (sleep/I/O/ReentrantLock.lock())
  |
JVM: serialise VT continuation to heap
  |
JVM: unmount VT from carrier thread
  |
Carrier thread available for other VTs
  |
... blocking completes ...
  |
JVM: schedule VT for resumption
  |
Carrier thread (possibly different): mount + resume VT
```

**Pinned virtual thread lifecycle:**
```
VT enters synchronized block
  |
monitorenter: carrier thread pointer registered as monitor owner
  |
VT tries to block (I/O inside synchronized)
  |
JVM: cannot unmount - carrier is monitor owner
  |
Carrier thread BLOCKED (same as platform thread)
  |
JVM may add compensation thread (bounded)
  |
VT exits synchronized, monitor released, carrier freed
```

**Detection:**
```
JVM fires: jdk.VirtualThreadPinned event
  - virtualThread: VT id
  - carrierThread: carrier id
  - duration: pinning duration
  - eventThread: VT reference
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (identifying pinning hotspots):**
```
Enable JFR with VirtualThreadPinned  <- YOU ARE HERE
  |
Start application under load
  |
Run workload generating concurrent virtual thread requests
  |
JFR captures pinning events > threshold (default 20ms)
  |
Analyse: which classes/methods are pinned?
  |
Replace synchronized -> ReentrantLock in hot paths
  |
Re-run: confirm pinning events reduced/eliminated
  |
Measure: virtual thread throughput improvement
```

**FAILURE PATH:**
JFR not enabled -> pinning undetected -> throughput plateau ->
engineers blame "virtual threads don't help" -> root cause missed.

**WHAT CHANGES AT SCALE:**
- At high concurrency (thousands of virtual threads), even brief
  pinning (1ms) in a tight loop can saturate all carriers.
- Library code updated: PostgreSQL JDBC 42.7+, Tomcat 10.1+,
  HikariCP 5.1+ have reduced pinning. Keep dependencies current.

---

### 💻 Code Example

**BAD - synchronized causing pinning:**
```java
// BAD: entire I/O operation pinned to carrier
public class DataService {
    private final Object lock = new Object();

    public Data fetch(long id) {
        synchronized (lock) {
            // Any blocking I/O here pins the carrier thread
            return jdbcRepository.findById(id); // PINNING!
        }
    }
}
```

**GOOD - ReentrantLock allows unmounting:**
```java
// GOOD: virtual thread can unmount during jdbcRepository.findById
public class DataService {
    private final ReentrantLock lock = new ReentrantLock();

    public Data fetch(long id) {
        lock.lock();
        try {
            return jdbcRepository.findById(id); // no pinning
        } finally {
            lock.unlock();
        }
    }
}
```

**GOOD - enable JFR pinning detection:**
```bash
# Start JFR with virtual thread pinning events
java \
  -Djdk.tracePinnedThreads=full \
  -XX:StartFlightRecording=filename=vt.jfr,settings=default \
  -jar myapp.jar

# Or programmatically in tests:
```
```java
// Programmatic JFR event check in integration test
try (RecordingStream rs = new RecordingStream()) {
    rs.enable("jdk.VirtualThreadPinned")
        .withThreshold(Duration.ofMillis(1));
    rs.onEvent("jdk.VirtualThreadPinned", event -> {
        System.err.println("PINNING DETECTED: "
            + event.getString("eventThread") + " for "
            + event.getDuration("duration").toMillis() + "ms");
    });
    rs.startAsync();
    // Run test workload here
}
```

**GOOD - system property for console output:**
```bash
# Print pinning stack traces to stdout (dev/test only)
-Djdk.tracePinnedThreads=full
# Or short form:
-Djdk.tracePinnedThreads=short
```

**How to test / verify correctness:**
```java
@Test
void noCarrierPinningUnderConcurrentLoad() throws Exception {
    AtomicInteger pinnedCount = new AtomicInteger(0);

    try (RecordingStream rs = new RecordingStream()) {
        rs.enable("jdk.VirtualThreadPinned")
            .withThreshold(Duration.ofMillis(1));
        rs.onEvent("jdk.VirtualThreadPinned",
            e -> pinnedCount.incrementAndGet());
        rs.startAsync();

        // Run concurrent virtual thread load
        try (var scope = new StructuredTaskScope<>()) {
            for (int i = 0; i < 100; i++) {
                scope.fork(() -> dataService.fetch(1L));
            }
            scope.join();
        }
    }

    assertThat(pinnedCount.get())
        .as("No pinning events expected")
        .isZero();
}
```

---

### ⚖️ Comparison Table

| Lock type | Causes pinning? | Virtual thread unmounts? | Use in VT code |
|-----------|----------------|--------------------------|----------------|
| `synchronized` | Yes | No | Avoid in blocking paths |
| `ReentrantLock` | No | Yes | Preferred |
| `ReadWriteLock` | No | Yes | Preferred for read-heavy |
| `StampedLock` | No | Yes | For high-throughput |
| `Semaphore` | No | Yes | Safe |
| Native method | Yes | No | Unavoidable; minimise |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Pinning causes correctness issues" | Pinning only degrades performance - it never causes data corruption or deadlock. The program is correct but slow. |
| "Virtual threads avoid all platform thread limits" | Only if blocking calls are NOT inside `synchronized`. Pinned virtual threads are equivalent to blocked platform threads. |
| "Only my code causes pinning" | Third-party library code (JDBC drivers, Spring Security internals, many JDK classes) also uses `synchronized` and causes pinning. |
| "Replacing synchronized with ReentrantLock everywhere is safe" | Only when the lock also needs to protect I/O. Pure CPU-bound `synchronized` is fine even with virtual threads (pinning is only costly when blocking occurs during the pin). |
| "JEP 491 is already released" | As of Java 21, `synchronized` still causes pinning. JEP 491 targets a future release. Check your JDK version. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: No throughput improvement after virtual thread migration**

**Symptom:** Request throughput identical before/after switching
to virtual threads.

**Root Cause:** All blocking paths are inside `synchronized` blocks
(JDBC driver, Spring session management, etc.) - all requests pin
carriers.

**Diagnostic:**
```bash
java -Djdk.tracePinnedThreads=full -jar app.jar
# In output look for:
# Thread[#23,ForkJoinPool-1-worker-3,5,CarrierThreads]
#     java.lang.VirtualThread[#42]/runnable@...
#         ...at com.mysql.jdbc.*   <-- JDBC pinning
```

**Fix:** Upgrade JDBC driver (PostgreSQL 42.7.x, MySQL 9.x+), or
switch to async database driver (R2DBC).

---

**Failure Mode 2: Carrier thread pool exhaustion under load**

**Symptom:** `OutOfMemoryError` or task queue backlog when JVM
creates too many compensation threads.

**Root Cause:** JVM compensates for pinning by creating additional
carrier threads (up to `maxPoolSize`). If pinning is widespread,
many compensation threads are created.

**Diagnostic:**
```bash
# Check JVM property for max carrier threads
jcmd <pid> VM.system_properties | grep virtualThread
# Monitor: jdk.VirtualThreadPinnedCount JMX metric
```

**Fix:**
```bash
# Increase max pool size as temporary mitigation
-Djdk.virtualThreadScheduler.maxPoolSize=256
# Permanent fix: eliminate synchronized in blocking paths
```

---

**Failure Mode 3: Native method pinning from JDK classes**

**Symptom:** JFR shows pinning from `java.io.FileInputStream` or
`java.lang.ProcessImpl` calls.

**Root Cause:** Certain JDK native methods pin virtual threads.
`FileInputStream.read()` and `ProcessBuilder.start()` use native
code.

**Fix:**
```java
// BAD: FileInputStream native read pins VT
new FileInputStream("file.txt").read();

// GOOD: Use java.nio which supports async I/O
Files.readAllBytes(Path.of("file.txt"));
// Or for streaming:
AsynchronousFileChannel.open(path).read(buf, 0, null, handler);
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-019 - Virtual Threads (Project Loom)]] - the feature that
  makes pinning relevant
- [[JCC-052 - Carrier Thread]] - the OS thread that virtual threads
  mount/unmount from
- [[JCC-053 - Continuation]] - the continuation that is blocked
  during pinning

**Builds On This (learn these next):**
- [[JCC-080 - Memory Visibility Diagnostics (jstack, JFR)]] - JFR
  tools used to detect pinning
- [[JCC-062 - Structured Concurrency]] - structured approach to
  virtual thread coordination

**Alternatives / Comparisons:**
- [[JCC-040 - ReentrantLock]] - the fix for `synchronized` pinning
- [[JCC-025 - Thread Interruption and Cancellation]] - cancellation
  semantics with pinned virtual threads

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Virtual thread stuck to carrier   |
|              | during synchronized block / native |
+--------------+------------------------------------+
| PROBLEM      | Negates virtual thread scalability;|
|              | carrier blocked like platform thread|
+--------------+------------------------------------+
| KEY INSIGHT  | synchronized = pinning;            |
|              | ReentrantLock = safe for VTs       |
+--------------+------------------------------------+
| USE WHEN     | Migrating to virtual threads;      |
|              | diagnosing VT scalability plateau  |
+--------------+------------------------------------+
| AVOID WHEN   | (Avoid pinning, not the concept)   |
|              | Fix by replacing synchronized      |
+--------------+------------------------------------+
| TRADE-OFF    | Performance degradation only;      |
|              | no correctness issues from pinning |
+--------------+------------------------------------+
| ONE-LINER    | -Djdk.tracePinnedThreads=full to   |
|              | detect; replace sync -> Lock to fix|
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-080 Memory Visibility Diag,    |
|              | JCC-062 Structured Concurrency     |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. `synchronized` pins virtual threads to carriers; `ReentrantLock`
   does not.
2. Enable `-Djdk.tracePinnedThreads=full` to detect pinning in
   development.
3. Third-party libraries (JDBC drivers, Spring internals) can cause
   pinning even if your own code is clean.

**Interview one-liner:** "Thread pinning happens when a virtual
thread enters a `synchronized` block - the JVM cannot unmount it
from the carrier because object monitors are OS-thread-bound;
replace `synchronized` with `ReentrantLock` to enable unmounting."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** New runtime capabilities are
often limited by legacy API contracts that predate the innovation.
The fix requires identifying which legacy constraints are
*accidental* (implementation choice) vs *essential* (specification
requirement), then addressing accidental constraints at the
implementation level.

**Where else this pattern appears:**
- **Node.js `child_process.execSync`:** Synchronous child process
  calls block the event loop - the Node.js equivalent of thread
  pinning. The fix is identical conceptually: use async APIs.
- **Python GIL with C extensions:** A C extension that does not
  release the GIL prevents other Python threads from running - the
  Python equivalent of pinning all threads to one OS thread.
- **Database connection pool starvation:** A connection pool with
  10 connections, each held for the duration of a transaction
  including slow external calls, creates the same bottleneck:
  all "carriers" (connections) consumed by pinned work.

---

### 💡 The Surprising Truth

Thread pinning is silent by default. A Java 21 application migrated
to virtual threads can show zero throughput improvement - or even
regression - while appearing to work correctly. The JVM adds no
warning; requests complete normally; thread counts look fine; the
only symptom is that performance is identical to the platform-thread
version. Without enabling `-Djdk.tracePinnedThreads=full` or the
`jdk.VirtualThreadPinned` JFR event, engineers commonly spend days
optimising wrong parts of the system before discovering that every
request is pinning a carrier for its entire duration through a
single `synchronized` method deep in a third-party library.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** Your application uses virtual
threads and HikariCP for database connections. You notice throughput
caps at exactly 8 concurrent requests despite having 1,000 virtual
threads. The JFR shows no pinning events. What other mechanism
could explain this cap, and how would you distinguish it from
pinning?

*Hint:* Investigate `HikariCP.maximumPoolSize`, connection pool
exhaustion vs carrier exhaustion, and how virtual threads behave
when waiting for a connection vs when executing a query.

---

**Question 2 (Design Trade-off):** JEP 491 (synchronize virtual
threads without pinning) will eventually land in a future JDK.
If it does, should you migrate all `synchronized` blocks to
`ReentrantLock` today, or wait for JEP 491? What factors determine
the right migration strategy for a production system?

*Hint:* Consider compatibility risk of API changes, the timeline
of JEP 491, your JDK upgrade policy, and the performance risk of
pinning today vs the refactoring risk of lock migration.

---

**Question 3 (Root Cause):** A virtual-thread-per-task HTTP
server processes 10,000 requests/second without pinning. When you
enable Spring Security's session-based authentication, throughput
drops to 2,000 requests/second. JFR shows pinning inside Spring
Security's `HttpSession` management. Describe the root cause chain
and two mitigation strategies.

*Hint:* Study how Spring Security's `HttpSessionSecurityContextRepository`
uses `synchronized` blocks on session objects, and explore
`SecurityContextRepository` alternatives like `RequestAttributeSecurityContextRepository`.

