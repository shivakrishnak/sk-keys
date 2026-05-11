---
layout: default
title: "Java Concurrency - Diagnostics"
parent: "Java Concurrency"
grand_parent: "Interview Mastery"
nav_order: 5
permalink: /interview/java-concurrency/diagnostics/
topic: Java Concurrency
subtopic: Diagnostics
keywords:
  - Deadlock Detection and Thread Dump Analysis
  - Testing Concurrent Code
  - Producer-Consumer Pattern
difficulty_range: mixed
status: in-progress
version: 2
---

**Keywords covered in this file:**

- [Deadlock Detection and Thread Dump Analysis](#deadlock-detection-and-thread-dump-analysis)
- [Testing Concurrent Code](#testing-concurrent-code)
- [Producer-Consumer Pattern](#producer-consumer-pattern)

# Deadlock Detection and Thread Dump Analysis

**TL;DR** - Deadlock occurs when two or more threads wait forever for locks held by each other; detection requires thread dump analysis using `jstack`, `jcmd`, or VisualVM to identify the circular wait chain.

---

### 🔥 The Problem This Solves

**THE 3AM SCENARIO:**
Your application becomes unresponsive. CPU is near 0%. Threads are alive but doing nothing. No errors in logs. No exceptions. The application is silently frozen. This is a deadlock - threads are permanently blocked waiting for locks that will never be released.

---

### How Deadlocks Happen

```
CLASSIC DEADLOCK:
Thread A: lock(resource1), then lock(resource2)
Thread B: lock(resource2), then lock(resource1)

Timeline:
  T1: Thread A acquires lock on resource1
  T2: Thread B acquires lock on resource2
  T3: Thread A tries to lock resource2 -> BLOCKED
  T4: Thread B tries to lock resource1 -> BLOCKED
  --> Both wait forever (circular wait)
```

**Four conditions (ALL must hold for deadlock):**

1. **Mutual exclusion:** Resource can't be shared
2. **Hold and wait:** Thread holds one resource while waiting for another
3. **No preemption:** Locks can't be forcibly taken
4. **Circular wait:** A waits for B, B waits for A

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 💻 Code Example

```java
// BAD: Deadlock-prone - inconsistent lock ordering
class TransferService {
    void transfer(Account from, Account to,
            BigDecimal amount) {
        synchronized (from) {    // Lock A first
            synchronized (to) {  // Then lock B
                from.debit(amount);
                to.credit(amount);
            }
        }
    }
}
// Thread 1: transfer(acctA, acctB, 100)
//   locks acctA, waits for acctB
// Thread 2: transfer(acctB, acctA, 50)
//   locks acctB, waits for acctA
// DEADLOCK!

// GOOD: Consistent lock ordering by ID
class TransferService {
    void transfer(Account from, Account to,
            BigDecimal amount) {
        Account first = from.getId() < to.getId()
            ? from : to;
        Account second = from.getId() < to.getId()
            ? to : from;
        synchronized (first) {
            synchronized (second) {
                from.debit(amount);
                to.credit(amount);
            }
        }
    }
}

// GOOD: Use tryLock with timeout
class TransferService {
    void transfer(Account from, Account to,
            BigDecimal amount) {
        boolean gotBoth = false;
        try {
            if (from.getLock()
                    .tryLock(1, SECONDS)) {
                try {
                    if (to.getLock()
                            .tryLock(1, SECONDS)) {
                        gotBoth = true;
                        from.debit(amount);
                        to.credit(amount);
                    }
                } finally {
                    if (!gotBoth)
                        from.getLock().unlock();
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        if (!gotBoth) throw new RetryException();
    }
}
```

---

### Thread Dump Analysis

```bash
# Capture thread dump
jcmd <pid> Thread.print > thread_dump.txt
# or
jstack <pid> > thread_dump.txt
# or
kill -3 <pid>  # Linux, outputs to stdout/stderr
```

**Reading a deadlock in thread dump:**

```
Found one Java-level deadlock:
=============================
"Thread-1":
  waiting to lock monitor 0x00007f..
  (object 0x000000076ab..., a Account)
  which is held by "Thread-2"

"Thread-2":
  waiting to lock monitor 0x00007f..
  (object 0x000000076ac..., a Account)
  which is held by "Thread-1"

Java stack information for threads listed above:
"Thread-1":
  at TransferService.transfer(TransferService.java:12)
  - waiting to lock <0x76ab..> (a Account)
  - locked <0x76ac..> (a Account)

"Thread-2":
  at TransferService.transfer(TransferService.java:12)
  - waiting to lock <0x76ac..> (a Account)
  - locked <0x76ab..> (a Account)
```

**What to look for:**

1. `"Found one Java-level deadlock"` - JVM auto-detects
2. `"waiting to lock"` - which lock the thread wants
3. `"which is held by"` - who holds that lock
4. Stack trace - where in your code the lock was acquired

---

### Thread States in Dumps

| State         | Meaning                          | Concern         |
| ------------- | -------------------------------- | --------------- |
| RUNNABLE      | Executing or ready               | Normal          |
| BLOCKED       | Waiting for monitor lock         | Lock contention |
| WAITING       | Waiting indefinitely (wait/park) | May be stuck    |
| TIMED_WAITING | Waiting with timeout             | Usually OK      |

**Patterns to watch for:**

- Many threads BLOCKED on same lock = lock contention (bottleneck)
- Two threads each BLOCKED waiting for the other = deadlock
- Thread WAITING on `Object.wait()` with no notifier = potential livelock

---

### Prevention Checklist

1. **Lock ordering:** Always acquire locks in a consistent global order
2. **Timeout:** Use `tryLock(timeout)` instead of `synchronized`
3. **Lock-free:** Use `AtomicReference`, `ConcurrentHashMap` instead of locks
4. **Minimize scope:** Hold locks for the shortest time possible
5. **Avoid nested locks:** If you need two locks, question the design
6. **Virtual threads:** Java 21 virtual threads with `ReentrantLock` reduce contention

---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Deadlock = circular wait on locks. Fix with consistent lock ordering or `tryLock` with timeout
2. `jcmd <pid> Thread.print` captures thread dumps; JVM auto-detects deadlocks in the output
3. Look for `BLOCKED` threads, `"waiting to lock"` chains, and stack traces showing where locks are held

**Interview one-liner:**
"I prevent deadlocks by enforcing consistent lock ordering and using tryLock with timeout instead of synchronized - when diagnosing a suspected deadlock, I capture a thread dump with jcmd and look for the 'Found Java-level deadlock' section showing the circular wait chain."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: Your production application freezes periodically but recovers after a few minutes. No deadlock found in thread dump. What's happening?**

_Why they ask:_ Tests ability to distinguish deadlock from other concurrency issues.

**Answer:**
This is likely **lock contention**, not deadlock. Many threads are BLOCKED waiting for the same lock, creating a bottleneck. When the lock holder finishes, threads unblock but new requests queue up again.

Diagnosis:

1. Capture multiple thread dumps 5 seconds apart with `jcmd <pid> Thread.print`
2. Look for the same lock appearing as "locked" by one thread and "waiting to lock" by many others
3. The BLOCKED thread count on that lock shows the contention level
4. Check if the lock holder is doing I/O (database query, HTTP call) while holding the lock

Fix: Reduce the synchronized block scope. Move I/O outside the lock. Switch to `ReadWriteLock` if reads dominate. Use `ConcurrentHashMap` instead of `synchronized(map)`. Consider lock striping (multiple locks for different data partitions).

**Q2: How would you detect a deadlock in a production JVM automatically?**

_Why they ask:_ Tests production operations knowledge.

**Answer:**

1. **JMX ThreadMXBean:** `ManagementFactory.getThreadMXBean().findDeadlockedThreads()` returns thread IDs involved in deadlock. Schedule this check periodically.

2. **Spring Boot Actuator:** `/actuator/threaddump` endpoint exposes thread dump via HTTP. Monitor for BLOCKED thread counts.

3. **APM tools:** Dynatrace, Datadog, New Relic detect deadlocks and alert automatically.

4. **Custom watchdog:**

```java
@Scheduled(fixedRate = 60_000)
public void checkForDeadlocks() {
    long[] deadlocked = ManagementFactory
        .getThreadMXBean()
        .findDeadlockedThreads();
    if (deadlocked != null) {
        alertService.critical(
            "DEADLOCK detected: "
            + deadlocked.length + " threads");
    }
}
```

**Q3: What's the difference between deadlock, livelock, and starvation?**

_Why they ask:_ Classic concurrency question testing conceptual clarity.

**Answer:**

- **Deadlock:** Threads are permanently blocked, waiting for each other. CPU = 0%. Thread state = BLOCKED. Detected by JVM automatically.

- **Livelock:** Threads are not blocked but make no progress. They keep responding to each other's actions (like two people in a hallway both stepping aside in the same direction). CPU > 0% but no useful work. Harder to detect.

- **Starvation:** One thread never gets to run because higher-priority threads always take the lock. The starved thread is perpetually BLOCKED or WAITING. Fix: use fair locks (`new ReentrantLock(true)`), though fair locks have ~10-20% lower throughput.

---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Deadlock Detection and Thread Dump Analysis. Otherwise remove this section.]

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Testing Concurrent Code

**TL;DR** - Testing concurrent code requires techniques beyond standard unit testing: `CountDownLatch` for synchronization, stress tests for race conditions, and tools like `jcstress` for formal verification.

---

### 🔥 The Problem This Solves

Regular unit tests run single-threaded. A race condition that occurs once in 10,000 executions will pass every test run. "Works on my machine" becomes "crashes in production under load."

---

### Techniques

```
TECHNIQUE 1: CountDownLatch (force interleaving)
  Create N threads, hold them at a latch
  Release all simultaneously to maximize contention

TECHNIQUE 2: Stress testing (statistical detection)
  Run the same operation 100,000 times in parallel
  If ANY run produces wrong result -> bug exists

TECHNIQUE 3: Thread.yield() injection
  Insert yield() at critical points to encourage
  context switches (not deterministic)

TECHNIQUE 4: jcstress (formal concurrency testing)
  JVM-level tool that systematically tests
  memory ordering and visibility
```

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 💻 Code Example

```java
// Testing a thread-safe counter
@RepeatedTest(100) // Run 100 times for confidence
void shouldBeThreadSafe() throws Exception {
    AtomicInteger counter = new AtomicInteger(0);
    int threadCount = 100;
    int incrementsPerThread = 1000;

    CountDownLatch startLatch =
        new CountDownLatch(1);
    CountDownLatch doneLatch =
        new CountDownLatch(threadCount);

    for (int i = 0; i < threadCount; i++) {
        new Thread(() -> {
            try {
                startLatch.await(); // Wait for signal
                for (int j = 0;
                     j < incrementsPerThread; j++) {
                    counter.incrementAndGet();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                doneLatch.countDown();
            }
        }).start();
    }

    startLatch.countDown(); // Release all threads
    doneLatch.await(10, SECONDS);

    assertThat(counter.get())
        .isEqualTo(threadCount
            * incrementsPerThread);
}

// Testing for race conditions with Awaitility
@Test
void shouldEventuallyProcess() {
    asyncService.submitTask(task);
    await().atMost(5, SECONDS)
        .pollInterval(100, MILLISECONDS)
        .until(() ->
            taskRepo.findById(task.getId())
                .getStatus()
                .equals("COMPLETED"));
}
```

---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Use `CountDownLatch` to force all threads to start simultaneously and maximize race condition exposure
2. `@RepeatedTest(100)` catches non-deterministic failures that pass on single runs
3. Awaitility is the standard for asserting async outcomes with polling

**Interview one-liner:**
"I test concurrent code with CountDownLatch for forced interleaving, @RepeatedTest for statistical confidence, and Awaitility for async assertions - but I also design for testability by preferring immutable objects and atomic operations over manual synchronization."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Testing Concurrent Code. Otherwise remove this section.]

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Producer-Consumer Pattern

**TL;DR** - Producer-Consumer decouples data production from consumption using a shared buffer (typically a `BlockingQueue`), allowing producers and consumers to operate at different speeds.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
[TODO: Concrete pain scenario. 2-4 sentences.]

**THE BREAKING POINT:**
[TODO: Specific failure. 1-2 sentences.]

**THE INVENTION MOMENT:**
"This is exactly why Producer-Consumer Pattern was created."

**EVOLUTION:**
[TODO: predecessor -> current form -> future.]

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### ⚙️ How It Works

```
[Producer 1] -\
[Producer 2] --> [BlockingQueue] --> [Consumer 1]
[Producer 3] -/       ^         \-> [Consumer 2]
                      |
              Bounded buffer
              (backpressure when full)
```

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 💻 Code Example

```java
// Producer-Consumer with BlockingQueue
public class EventProcessor {
    private final BlockingQueue<Event> queue =
        new ArrayBlockingQueue<>(1000);
    private final ExecutorService producers =
        Executors.newFixedThreadPool(3);
    private final ExecutorService consumers =
        Executors.newFixedThreadPool(2);

    public void start() {
        // Producers
        for (int i = 0; i < 3; i++) {
            producers.submit(() -> {
                while (!Thread.interrupted()) {
                    Event event = pollExternalSource();
                    queue.put(event); // blocks if full
                }
            });
        }
        // Consumers
        for (int i = 0; i < 2; i++) {
            consumers.submit(() -> {
                while (!Thread.interrupted()) {
                    Event event = queue.take(); // blocks
                    process(event);
                }
            });
        }
    }

    public void shutdown() {
        producers.shutdownNow();
        consumers.shutdown();
        consumers.awaitTermination(
            30, SECONDS);
    }
}
```

---

### BlockingQueue Implementations

| Implementation          | Bounded       | Ordering       | Best for            |
| ----------------------- | ------------- | -------------- | ------------------- |
| `ArrayBlockingQueue`    | Yes (fixed)   | FIFO           | General purpose     |
| `LinkedBlockingQueue`   | Optional      | FIFO           | High throughput     |
| `PriorityBlockingQueue` | No            | Priority       | Priority processing |
| `SynchronousQueue`      | Zero capacity | Direct handoff | Thread pools        |
| `DelayQueue`            | No            | Delay-based    | Scheduled tasks     |

---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `BlockingQueue` is the standard Java solution for producer-consumer
2. Bounded queues provide natural backpressure - producers block when the queue is full
3. `ArrayBlockingQueue` for general use; `SynchronousQueue` when you want direct handoff (like `ThreadPoolExecutor` uses)

**Interview one-liner:**
"I implement producer-consumer with a bounded ArrayBlockingQueue for natural backpressure - producers block when the queue is full, preventing memory exhaustion, while consumers block when empty, eliminating busy-waiting."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Producer-Consumer Pattern. Otherwise remove this section.]

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

