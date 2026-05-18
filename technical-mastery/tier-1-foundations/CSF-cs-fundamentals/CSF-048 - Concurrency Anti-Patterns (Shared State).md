---
id: CSF-048
title: "Concurrency Anti-Patterns (Shared State)"
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-047, JCC-001
used_by: JCC-010, DST-015
related: CSF-047, JCC-001, DST-015
tags: [race-condition, deadlock, shared-state, thread-safety, livelock]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/csf/concurrency-anti-patterns-shared-state/
---

⚡ TL;DR - Concurrency anti-patterns: race condition (lost
update from unsynchronized shared write), deadlock (two
threads each hold a lock the other needs), livelock (both
yield, neither progresses). Solutions: immutability,
lock ordering, atomic operations, message passing.

| #048 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-047 (Concurrency vs Parallelism), JCC-001 (Java Concurrency) | |
| **Used by:** | JCC-010 (Advanced Concurrency), DST-015 (Distributed Concurrency) | |
| **Related:** | CSF-047 (Concurrency), DST-015 (Distributed Locking) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A banking application allows two concurrent transfers from
the same account. Thread A checks balance ($1,000), reads,
computes new balance ($700 after $300 withdrawal). Thread B
checks balance ($1,000), reads, computes new balance ($200
after $800 withdrawal). Thread A writes $700. Thread B writes
$200. Final balance: $200 - but $1,100 was withdrawn from
an account with $1,000. The account should be at -$100 (which
the bank should have prevented) or at least one transfer
should have been rejected. Instead: both succeeded and
$100 was created from nothing. This is a race condition.

**THE BREAKING POINT:**

Race conditions are invisible in testing. In development,
one thread typically runs to completion before another starts.
The race only occurs under high concurrency (production load).
A race that corrupts data occurs at a rate proportional to
the probability that two threads hit the critical section
simultaneously. With 1,000 TPS: the race that triggers in
1/10,000 concurrent executions causes roughly 100 corruptions
per day. Financial data corruption, inventory overselling,
and authentication bypass bugs all have this pattern.

**THE INVENTION MOMENT:**

The formal definition of a race condition by Dijkstra (1965)
and subsequent development of semaphores, mutual exclusion
(mutex), and monitors gave programmers the vocabulary and
tools to describe and fix concurrent access bugs. Java's
`synchronized` keyword, `volatile`, `java.util.concurrent`
(Java 5), and lock-free algorithms via `AtomicInteger` etc.
are the Java evolution. Modern approaches add structural
solutions: immutable data (no race condition without mutable
state), message passing (Akka actors, channels), and STM
(Software Transactional Memory in Clojure).

---

### 📘 Textbook Definition

**Race condition:** A bug where the output of a concurrent
operation depends on the relative timing of events (scheduling
order of threads). When two or more threads read-modify-write
shared mutable state without synchronization, the result
is non-deterministic.

**Data race:** The specific case where two threads access
the same memory location concurrently, at least one access
is a write, and the accesses are not synchronized. Causes
undefined behavior in some languages (C/C++); corrupted
state in Java.

**Deadlock:** A situation where two or more threads each
hold a resource and are waiting to acquire a resource
held by the other. All threads are blocked permanently.

**Livelock:** Threads are not blocked (they are running)
but are unable to make progress because they keep responding
to each other's state changes (both back off simultaneously,
then retry simultaneously, indefinitely).

**Starvation:** A thread is perpetually denied access to
a resource (CPU, lock) because other threads always take
priority.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Race condition = unsynchronized shared write = corrupted state.
Deadlock = thread A waits for B's lock; B waits for A's lock
= both blocked forever.

**One analogy:**

> Race condition: two people edit the same Google Doc section
> simultaneously. Each reads "paragraph 1" and types their change.
> One overwrites the other. The last write wins - regardless
> of which was "intended" to be the final version.

> Deadlock: two drivers on a one-lane bridge from opposite
> sides. Neither backs up. Both wait for the other to move.
> Neither ever moves.

> Livelock: the same drivers, each politely backed up to let
> the other through. They both backed up simultaneously.
> Both try to advance simultaneously. Both back up simultaneously.
> Infinitely. Polite deadlock.

**One insight:**

In Spring Boot, singleton-scoped `@Service` beans are shared
across all threads (all requests use the same instance).
If a singleton bean has instance-level mutable state (a field
that is set per-request), that field is a race condition.
The fix: stateless beans (no mutable instance fields), or
request-scoped beans, or `ThreadLocal`. Many Spring security
bugs are caused by developers storing per-request data
in singleton bean fields.

---

### 🔩 First Principles Explanation

**RACE CONDITION MECHANICS:**

```
┌──────────────────────────────────────────────────────┐
│ counter = 0; // shared mutable state                 │
│                                                      │
│ Thread A:                 Thread B:                  │
│ 1. read counter (0)       1. read counter (0)        │
│ 2. compute 0 + 1 = 1      2. compute 0 + 1 = 1       │
│ 3. write counter = 1      3. write counter = 1       │
│                                                      │
│ Result: counter = 1 (not 2!)                         │
│ Expected: counter = 2 (two increments)               │
│                                                      │
│ The "check-then-act" is NOT atomic in Java without   │
│ explicit synchronization.                            │
│ counter++ compiles to: read, increment, write.       │
│ Three separate operations. Race window between them. │
│                                                      │
│ Fix (atomic operation):                              │
│   AtomicInteger counter = new AtomicInteger(0);      │
│   counter.incrementAndGet(); // atomic read-modify-write│
└──────────────────────────────────────────────────────┘
```

**DEADLOCK MECHANICS:**

```
┌──────────────────────────────────────────────────────┐
│ Thread A:                   Thread B:                │
│ 1. lock(resourceA)          1. lock(resourceB)       │
│ 2. ... (holding A)          2. ... (holding B)       │
│ 3. lock(resourceB) ← WAIT   3. lock(resourceA) ← WAIT│
│                                                      │
│ Thread A waits for B to release resourceB.           │
│ Thread B waits for A to release resourceA.           │
│ Circular wait -> neither ever proceeds. Deadlock.    │
│                                                      │
│ Coffman conditions for deadlock (all must hold):     │
│ 1. Mutual exclusion: resource exclusive to one thread│
│ 2. Hold and wait: thread holds and waits for more    │
│ 3. No preemption: resource not forcibly taken        │
│ 4. Circular wait: cycle in wait-for graph            │
│                                                      │
│ Fix: consistent lock ordering.                       │
│ BOTH threads: lock(lower-id resource) THEN lock(higher-id)│
│ Thread A: lock(A), then lock(B)                      │
│ Thread B: lock(A), then lock(B) [same order = no cycle]│
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE DOUBLE-CHECKED LOCKING TRAP:**

```java
// BROKEN (Java 1.4 and earlier, and in some cases still)
class Singleton {
    private static Singleton instance;

    static Singleton getInstance() {
        if (instance == null) {                 // check 1
            synchronized (Singleton.class) {
                if (instance == null) {          // check 2
                    instance = new Singleton();  // NOT atomic!
                }
            }
        }
        return instance;
    }
}
// Problem: `instance = new Singleton()` involves:
// 1. Allocate memory
// 2. Initialize object fields
// 3. Assign reference to `instance`
// Steps 2 and 3 may be REORDERED by CPU/JIT.
// Another thread sees non-null `instance` at check 1
// but the object is only partially initialized (step 2 not done).
// Accessing the partially-initialized object -> undefined behavior.

// FIX: volatile prevents reordering
private static volatile Singleton instance;
// Now: assignment to `instance` is the last thing that happens
// (volatile has acquire-release semantics)
```

**THE LESSON:**

The Java Memory Model (JMM) allows the CPU and JIT to
reorder instructions for performance, subject to constraints.
Without `volatile` or `synchronized`, another thread may
observe a partially-constructed object. This is not
a theoretical concern: it caused production crashes in
popular frameworks (Apache commons-lang, JDK itself in
some versions). The fix is simple (`volatile`), but the
bug is nearly impossible to reproduce in testing because
the reordering happens probabilistically under specific
CPU and JIT conditions.

---

### 🎯 Mental Model / Analogy

**CRITICAL SECTION AS SINGLE-STALL BATHROOM:**

Multiple people (threads) need to use the bathroom (access
shared state). The lock on the door is `synchronized`.
Only one person inside at a time (mutual exclusion). Others
wait outside (blocked).

If the person inside never leaves (infinite loop, exception
swallowed, forgot to unlock) -> everyone outside waits forever
(deadlock variant: lock not released).

If two people each hold a key to each other's locker (which
they need to get into the bathroom) -> deadlock.

**MEMORY HOOK:**

"Race: unsynchronized read-modify-write. Lost updates.
Fix: AtomicXxx, synchronized, CAS.
Deadlock: circular lock dependency. Fix: lock ordering.
Livelock: both retry simultaneously. Fix: randomized backoff.
`volatile`: visibility (no reordering), not atomicity.
`synchronized`: both visibility AND atomicity.
Prefer immutable data > message passing > locking."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Race: two kids each grab the last cookie at the same time.
They both think they have it, but the jar ends up empty.
Deadlock: kid A won't put down toy B; kid B won't put down
toy A. Neither gets to play. They wait forever.

**Level 2 - Student:**
```java
// Race condition:
int count = 0;
// Thread A and B both run: count++ (not atomic)
// Result: count may be 1 instead of 2

// Fix:
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet(); // atomic
```

**Level 3 - Professional:**
CAS (Compare-And-Swap): the foundation of lock-free algorithms.
`AtomicInteger.compareAndSet(expected, update)`: atomically:
if value == expected, set to update; return true. Else return false.
The caller retries until CAS succeeds. No lock needed.
CPU-level atomic instruction (LOCK CMPXCHG on x86).

**Level 4 - Senior Engineer:**
Java `Lock` API vs `synchronized`:
`ReentrantLock`: tryLock(timeout) avoids deadlock (fails
rather than blocking forever). Fairness option (FIFO ordering
prevents starvation). Multiple conditions on one lock
(`Condition.await()` vs `Object.wait()`). `StampedLock`:
optimistic reading (no lock acquisition, check for write
after read), upgrading to write lock. Higher throughput for
read-heavy workloads than `ReentrantReadWriteLock`.

**Level 5 - Expert:**
ABA problem in lock-free CAS: Thread A reads value = 1.
Thread B changes 1 -> 2 -> 1 (back to 1). Thread A's CAS
succeeds (value is still 1). But the state is NOT the same:
B's intermediate changes may have had side effects. Fix:
`AtomicStampedReference` - adds a version counter that
increments on every update. CAS checks both value AND stamp.

---

### ⚙️ How It Works (Formal Basis)

**JAVA MEMORY MODEL (JMM):**

```
┌──────────────────────────────────────────────────────┐
│ Java Memory Model: happens-before guarantees         │
│                                                      │
│ Rules:                                               │
│ 1. Monitor rule: unlock HAPPENS-BEFORE next lock     │
│ 2. Volatile rule: write HAPPENS-BEFORE next read     │
│ 3. Thread start: start() HAPPENS-BEFORE thread run   │
│ 4. Thread join: run HAPPENS-BEFORE join() return     │
│                                                      │
│ WITHOUT happens-before: thread may see stale values  │
│ (cached in register or L1 cache, not flushed to main)│
│                                                      │
│ volatile:                                            │
│   - Reads always from main memory                    │
│   - Writes always to main memory                     │
│   - No reordering around volatile access             │
│   - Ensures visibility, NOT atomicity                │
│   - volatile int x; x++ is STILL not atomic         │
│     (read, increment, write are 3 ops)               │
│                                                      │
│ synchronized:                                        │
│   - Mutual exclusion (one thread at a time)          │
│   - Visibility (same as volatile on entry/exit)      │
│   - Atomicity of the critical section                │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Race Condition in Counter**

```java
// BAD: non-atomic increment (race condition)
class UnsafeCounter {
    private int count = 0; // shared mutable state

    void increment() {
        count++;  // NOT atomic: read, increment, write
        // Race window between read and write
    }

    int get() { return count; }
}

// GOOD option 1: synchronized (mutex)
class SynchronizedCounter {
    private int count = 0;

    synchronized void increment() { count++; } // atomic block
    synchronized int get() { return count; }
}

// GOOD option 2: AtomicInteger (lock-free CAS)
class AtomicCounter {
    private final AtomicInteger count = new AtomicInteger(0);

    void increment() { count.incrementAndGet(); } // CPU atomic
    int get() { return count.get(); }
}
// AtomicInteger is faster than synchronized for high contention
// because CAS does not block - it retries without OS involvement
```

**Example 2 - Deadlock Reproduction and Fix**

```java
// BAD: lock ordering inconsistency -> potential deadlock
class BankAccount {
    private final Object lock = new Object();
    private double balance;

    static void transfer(BankAccount from, BankAccount to, double amount) {
        synchronized (from.lock) {      // Thread A locks account1
            synchronized (to.lock) {    // Thread A waits for account2
                // Thread B: locks account2 first, waits for account1
                // -> DEADLOCK with Thread B doing reverse transfer
                from.balance -= amount;
                to.balance += amount;
            }
        }
    }
}

// GOOD: consistent lock ordering by identity (System.identityHashCode)
static void transfer(BankAccount from, BankAccount to, double amount) {
    BankAccount first, second;
    if (System.identityHashCode(from) < System.identityHashCode(to)) {
        first = from; second = to;
    } else {
        first = to; second = from;
    }
    synchronized (first.lock) {
        synchronized (second.lock) {
            // Both Thread A and B acquire in same order: no cycle
            from.balance -= amount;
            to.balance += amount;
        }
    }
}
```

---

### ⚖️ Comparison Table

| Problem | Symptom | Root Cause | Fix |
|---|---|---|---|
| Race condition | Lost updates, corrupted state | Unsynchronized shared write | AtomicXxx, synchronized, CAS |
| Deadlock | All threads blocked permanently | Circular lock dependency | Lock ordering, tryLock(timeout) |
| Livelock | CPU active, no progress | Both threads yield simultaneously | Randomized backoff, priority |
| Starvation | Thread never proceeds | Always preempted by others | Fair lock (ReentrantLock(true)) |
| Data race | Undefined/stale reads | No happens-before between threads | volatile, synchronized, AtomicXxx |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`volatile` makes an operation thread-safe" | `volatile` ensures VISIBILITY (all threads see the latest written value) and prevents instruction reordering around the volatile access. It does NOT provide atomicity. `volatile int x; x++` is still a race condition: read (main memory), increment (register), write (main memory) are three separate operations. Another thread can interleave between read and write. Use `AtomicInteger` for atomic increment. |
| "Synchronized methods are always slow" | `synchronized` with no or low contention (one thread at a time accessing the section) is very fast in modern JVMs: it uses biased locking, then thin locks, and only escalates to OS-level mutexes under contention. For most application-level shared state, the overhead of `synchronized` is negligible. Profile before optimizing to lock-free. |
| "Using concurrent collections prevents all race conditions" | `ConcurrentHashMap` makes individual operations (get, put) thread-safe. But check-then-act sequences are NOT atomic: `if (!map.containsKey(k)) map.put(k, v)` is a race condition even with `ConcurrentHashMap`. Two threads may both check, both find absent, both put. Use `map.putIfAbsent(k, v)` or `map.computeIfAbsent(k, f)` for atomic check-then-put. |
| "Deadlocks always cause obvious hangs" | Deadlocks in production may appear as: requests timing out (not hanging), inconsistent throughput (some requests succeed, some hang), specific combinations of operations hanging but not all. A partial deadlock (2 of 200 threads deadlocked) may show as slightly degraded throughput until the thread pool is exhausted. Thread dumps are the diagnostic: any thread in state `BLOCKED` waiting for a lock held by another BLOCKED thread is a deadlock. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Deadlock in Production**

**Symptom:** Specific API endpoints hang and time out.
Health check endpoint still responds (it does not acquire
the deadlocked locks). CPU is low (threads are BLOCKED,
not running). Application becomes progressively less
responsive as more thread pool threads deadlock.

**Diagnosis:**
```bash
# Take a thread dump
jcmd <pid> Thread.print > thread_dump.txt
# Or: kill -3 <pid> on Linux (sends SIGQUIT -> JVM prints thread dump)

# Look for BLOCKED threads:
# "Thread-A" #42 prio=5 os_prio=0 tid=... nid=... waiting for monitor entry
#   java.lang.Thread.State: BLOCKED (on object monitor)
#     at com.example.BankAccount.transfer(BankAccount.java:15)
#     - waiting to lock <0x00000006c0012345> (a BankAccount)
#     - locked <0x00000006c0056789> (a BankAccount)
# "Thread-B" #43 ... BLOCKED
#     - waiting to lock <0x00000006c0056789>
#     - locked <0x00000006c0012345>
# -> DEADLOCK: A waiting for B's lock, B waiting for A's lock
```

**Fix:** Implement consistent lock ordering. Or use `tryLock(timeout)`:
if the second lock cannot be acquired within the timeout,
release the first lock and retry. Prevents deadlock at
the cost of retry logic.

**Failure Mode 2: Race Condition in Payment Processing**

**Symptom:** Occasional duplicate payments or incorrect
balances in a payment service. The bug reproduces rarely
and only under high load. Individual test cases pass.

**Root Cause:** A service reads balance, computes new balance,
and writes - but the read and write are not in the same
database transaction. Two concurrent requests for the same
account both read the same balance.

**Diagnosis:** Look for `SELECT` followed by an `UPDATE`
in separate database calls (not in one transaction).

**Fix:** Use database-level atomic operations:
`UPDATE accounts SET balance = balance - :amount WHERE id = :id AND balance >= :amount`
(conditional update: no intermediate read). Check rows affected
to detect if the condition was not met (balance insufficient).
Or use SELECT FOR UPDATE (pessimistic locking) within a
single transaction.

---

**Security Note:**

Race conditions are a SECURITY vulnerability class (CWE-362).
TOCTOU (Time-of-Check/Time-of-Use) vulnerabilities in
security-sensitive code allow bypassing access controls:
1. Check: `if (user.isAdmin()) { ... }`
2. Gap: between check and action, user's role may change
3. Action: `adminOperation()` - executed even though user
   is no longer admin
This class of vulnerability causes authentication bypasses,
privilege escalation, and financial fraud in production systems.
Fix: check authorization within the same atomic operation
as the action (database transaction, synchronized block,
or JWT claim verified at each step). Never separate the
authorization check from the authorized action in concurrent code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Concurrency vs Parallelism` (CSF-047) - anti-patterns
  are specific failure modes of concurrent programming
- `Java Concurrency` (JCC-001) - Java-specific implementation
  of synchronization primitives

**Builds On This (learn these next):**
- `Advanced Java Concurrency` (JCC-010) - ReentrantLock,
  StampedLock, CompletableFuture, structured concurrency
- `Distributed Locking` (DST-015) - race conditions and
  deadlocks at the distributed system level

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ RACE COND.   │ Unsynchronized shared write             │
│              │ Fix: AtomicXxx, synchronized, CAS      │
│              │ volatile = visibility, NOT atomicity    │
├──────────────┼─────────────────────────────────────────┤
│ DEADLOCK     │ Circular lock dependency                │
│              │ Fix: consistent lock ordering           │
│              │ Or: tryLock(timeout) + retry            │
├──────────────┼─────────────────────────────────────────┤
│ LIVELOCK     │ Both yield simultaneously forever       │
│              │ Fix: randomized backoff, priority       │
├──────────────┼─────────────────────────────────────────┤
│ STARVATION   │ Thread never gets the lock              │
│              │ Fix: ReentrantLock(true) = fair lock    │
├──────────────┼─────────────────────────────────────────┤
│ SINGLETON    │ Spring @Service singletons: stateless!  │
│ BEAN SAFETY  │ No mutable instance fields in beans     │
├──────────────┼─────────────────────────────────────────┤
│ DIAGNOSE     │ jcmd <pid> Thread.print                │
│              │ BLOCKED + circular wait = deadlock      │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ JCC-001 (Java Concurrency), DST-015     │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Race condition = read-modify-write on shared mutable state
   without synchronization. `count++` is THREE operations;
   another thread can interleave between read and write.
   Fix: use `AtomicInteger.incrementAndGet()` (CAS = one CPU
   instruction) or `synchronized`. `volatile` alone is NOT
   enough for atomicity.
2. Deadlock requires four conditions (Coffman): mutual exclusion,
   hold-and-wait, no preemption, circular wait. Fix one condition
   to prevent deadlock. Practical fix: CONSISTENT LOCK ORDERING
   (always acquire locks in the same global order regardless
   of which thread). `tryLock(timeout)` avoids deadlock
   by failing rather than blocking forever.
3. Spring `@Service` singleton beans: no mutable instance state.
   If a field changes per-request, it is a race condition.
   Fix: stateless bean (no mutable fields), or request-scoped
   bean, or `ThreadLocal` (cleaned up in `finally`). Review
   every singleton bean for instance-level state.

**Interview one-liner:**
"Race condition = unsynchronized shared mutable state causes
non-deterministic outcomes. Fix: `AtomicXxx` for lock-free
CAS, `synchronized` for mutual exclusion + visibility.
`volatile` only ensures visibility, not atomicity. Deadlock =
circular lock dependency; fix with consistent lock ordering.
Spring singleton beans must be stateless (no mutable instance
fields); per-request state belongs in request scope or ThreadLocal."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The root cause of all concurrency bugs is mutable shared
state. Eliminate one of the three components (mutable, shared,
state) to eliminate the bug:
- Eliminate MUTABLE: use immutable data. Immutable objects
  can be shared without synchronization. Java records,
  Kotlin data classes with `val` fields, `Collections.unmodifiableList()`.
- Eliminate SHARED: use thread-local state. `ThreadLocal<T>`
  in Java. Go goroutines with local variables (not shared via goroutine).
- Eliminate STATE: use message passing. Akka actors: each
  actor has private mutable state; state is only modified
  by messages received sequentially. No shared state between actors.
This principle: "shared mutable state is the root of all
concurrency evil" is why functional programming (immutable
by default), actor systems (message passing, no shared state),
and CSP (channels, not shared memory) are growing in popularity
for concurrent systems.

**Where else this pattern appears:**

- **Kafka consumer group semantics** - Kafka prevents race
  conditions by assigning each partition to exactly ONE consumer
  in a group at a time. Multiple consumers cannot process
  the same partition simultaneously. The partition assignment
  is the "lock." If two consumers could process the same
  partition, messages would be processed twice (race condition
  on consumer state). The single-partition-per-consumer
  guarantee is Kafka's concurrency safety mechanism.
- **Database MVCC (Multiversion Concurrency Control)** -
  MVCC prevents read-write conflicts without locking.
  Each transaction reads a SNAPSHOT of the database at
  the start of the transaction (immutable view). Writes
  create new versions. Read transactions never block on
  write transactions (they read old versions). This is
  the database implementation of "eliminate mutable shared
  state during reading": readers see an immutable snapshot.
- **CRDTs (Conflict-free Replicated Data Types)** - In
  distributed systems, concurrent updates to the same data
  on different replicas cause conflicts (race conditions
  at network scale). CRDTs are data structures designed
  to merge concurrent updates deterministically without
  coordination. They eliminate the race condition at the
  distributed level by constraining the data structure
  to merge operations that are always convergent.

---

### 💡 The Surprising Truth

The `java.util.Hashtable` class (Java 1.0) was designed
to be "thread-safe" - every method is `synchronized`.
Yet `Hashtable` is still broken under concurrent use.
The problem: individual operations are atomic, but
compound operations are not. `if (!hashtable.containsKey(k))
hashtable.put(k, v)` is a race condition even with
`Hashtable`: two threads may both check (both see absent),
both put (both write). The "thread-safe" class does not
make compound operations thread-safe. `ConcurrentHashMap`
was introduced in Java 5 with operations like `putIfAbsent(k, v)`
that are ATOMICALLY compound. The lesson: "thread-safe class"
means individual method calls are atomic; it does NOT mean
ANY sequence of calls on the object is thread-safe.
Compound operations require either: (1) a single atomic
compound method, (2) external synchronization around the
compound operation, or (3) a redesign that avoids compound
check-then-act patterns. This is one of the most common
misunderstandings about thread safety in Java.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** Review a Spring Boot service class that
   has a `private List<Event> eventLog = new ArrayList<>()`
   instance field. Identify: is this a race condition?
   Under what conditions? What are 3 different fixes
   and their trade-offs?

2. **[REPRODUCE]** Write a test that reliably demonstrates
   a race condition in a counter using `CountDownLatch` to
   synchronize 100 threads to start simultaneously.
   Show that the final count is less than 100 without
   synchronization and exactly 100 with `AtomicInteger`.

3. **[DIAGNOSE]** Given a thread dump where multiple threads
   are in state `BLOCKED` with circular lock references,
   identify the deadlock, determine which resources are
   involved, and propose two different fixes.

4. **[FIX]** Implement a thread-safe in-memory session cache
   using `ConcurrentHashMap.computeIfAbsent()`. Explain why
   `computeIfAbsent` prevents the race condition that
   `if (!map.containsKey(k)) map.put(k, v)` does not.

5. **[DESIGN]** Design a thread-safe order service that
   prevents concurrent requests from overselling inventory.
   Compare: pessimistic locking (SELECT FOR UPDATE),
   optimistic locking (version field + CAS update),
   and application-level synchronized block. Recommend
   one and justify.

---

### 🧠 Think About This Before We Continue

**Q1.** A Java singleton (`@Service` in Spring) has a method
that caches an API response in an instance field:
```java
@Service
class CurrencyService {
    private Map<String, BigDecimal> rates; // instance state

    BigDecimal getRate(String currency) {
        if (rates == null || rates.isEmpty()) {
            rates = fetchRatesFromExternalApi(); // I/O call
        }
        return rates.get(currency);
    }
}
```
This runs in a high-concurrency Spring Boot application (200 threads).
List all the concurrency problems this code has.

*Hint:
1. Race condition on `rates == null` check: two threads may
   both see null, both call `fetchRatesFromExternalApi()`.
   Both create a new map. Second write overwrites first.
   Any thread that got a reference to the first map while
   the second is being written may see inconsistent state.
2. Visibility: writes to `rates` (a reference) are not
   guaranteed visible across threads without volatile or
   synchronized (Java Memory Model).
3. Not atomic: `rates == null || rates.isEmpty()` and
   `rates = fetchRates()` are separate operations. Between
   them, another thread may have set rates.
4. Partial initialization: if `fetchRatesFromExternalApi()`
   throws mid-execution, `rates` may be partially set or remain null.
5. Potential NPE: if `rates.get(currency)` is called while
   `rates` is being set in another thread.
Fix options: (a) initialize in `@PostConstruct` (single-threaded
startup, then read-only). (b) use `volatile Map<String,BigDecimal> rates`
+ double-checked locking. (c) use `ConcurrentHashMap` +
`computeIfAbsent`. (d) make the method `synchronized`.*

**Q2.** `ReentrantLock` has a `tryLock(long timeout, TimeUnit unit)` method.
How does this prevent deadlock? What is the risk of using
`tryLock` without careful implementation?

*Hint: `tryLock(timeout)` prevents deadlock by FAILING FAST:
instead of blocking until the lock is acquired (potentially
forever in a deadlock), it waits only `timeout` time.
If the lock is not acquired in that time, it returns `false`
and the thread can release the lock it holds and retry later.
This breaks the "hold and wait" Coffman condition: if the
second lock is unavailable, the thread does NOT hold the
first lock while waiting indefinitely.
Risk of tryLock without careful implementation:
(1) LIVELOCK: if Thread A and Thread B both fail to acquire
each other's lock at the same timeout, release their own lock,
and retry with the same timeout, they may retry simultaneously
and fail again, indefinitely. Fix: randomized backoff
(retry after random delay between min and max).
(2) Lock not released on false return: if the code does not
properly release the first lock after tryLock fails for
the second, resources leak.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is a race condition? How do you prevent it in Java?"**

*Why they ask:* Foundational concurrency question. Every senior dev must know this.

*Strong answer includes:*
- Race condition: the outcome depends on the relative timing
  of concurrent threads accessing shared mutable state.
  `count++` is three operations (read, increment, write);
  two threads interleaving produce a lost update.
- Prevention options:
  1. `synchronized`: mutual exclusion, only one thread in
     the critical section. Ensures visibility + atomicity.
  2. `AtomicInteger`: lock-free CAS. Faster under contention.
  3. Immutable data: no shared mutable state = no race.
  4. Thread confinement: state never shared (ThreadLocal).
  5. `volatile`: visibility only (no atomicity - not sufficient
     for read-modify-write).
- Real example: Spring singleton bean with mutable instance
  field. Multiple request threads share the bean instance.
  Fix: stateless bean, or `synchronized` method, or `AtomicXxx`.

**Q2: "Explain deadlock. How do you detect it in a running JVM?"**

*Why they ask:* Production incident knowledge. Tests ability to diagnose.

*Strong answer includes:*
- Deadlock: Thread A holds lock 1, waits for lock 2. Thread B
  holds lock 2, waits for lock 1. Circular wait = no progress.
- Detection in production: thread dump via `jcmd <pid> Thread.print`
  or `kill -3 <pid>`. Look for multiple threads in `BLOCKED`
  state with circular lock dependencies. JVM thread dump
  includes a "Found one Java-level deadlock:" section that
  explicitly names deadlocked threads.
- Prevention: consistent lock ordering (always acquire locks
  in the same global order). `tryLock(timeout)` to fail rather
  than wait forever.

**Q3: "What is the difference between `synchronized` and `volatile`?"**

*Why they ask:* Common Java concurrency interview question.
Tests JMM knowledge.

*Strong answer includes:*
- `volatile`:
  - Ensures visibility: all writes immediately visible to
    all threads (no CPU cache without flush).
  - Prevents instruction reordering around the volatile access.
  - Does NOT provide atomicity. `volatile int x; x++` = race.
  - Used for: flags, status fields, one-writer-many-reader.
  - Example: `private volatile boolean running = true;`
    stopped from another thread: all threads see the update.
- `synchronized`:
  - Ensures mutual exclusion: only one thread in the block.
  - Ensures visibility (same as volatile on enter/exit).
  - Provides atomicity of the entire synchronized block.
  - Heavier: may involve OS mutex under contention.
  - Used for: read-modify-write, compound operations,
    all cases where atomicity is needed.
