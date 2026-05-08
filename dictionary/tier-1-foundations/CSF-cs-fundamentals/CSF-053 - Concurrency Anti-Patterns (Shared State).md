---
id: CSF-053
title: Concurrency Anti-Patterns (Shared State)
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - deep-dive
  - tradeoff
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /csf/concurrency-anti-patterns-shared-state/
---

# CSF-053 - Concurrency Anti-Patterns (Shared State)

⚡ TL;DR - Shared mutable state is the root cause of race conditions, deadlocks, and data races; the solution is to either eliminate sharing (immutability, message passing) or eliminate mutation (read-only shared state).

| CSF-053         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-034, CSF-041, CSF-060             |                 |
| **Used by:**    | CSF-060                               |                 |
| **Related:**    | CSF-034, CSF-041, CSF-060             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Multi-threaded programs sharing mutable state exhibit the most
insidious bugs in software: they pass all tests, run correctly
99.9% of the time, and fail in production under load. The
bug is impossible to reproduce deterministically. The race
condition window might be 10 nanoseconds wide.

**THE BREAKING POINT:**
A bank account `balance` field accessed by two threads:
Thread 1 reads `balance=100`, Thread 2 reads `balance=100`,
Thread 1 writes `balance=150` (+50), Thread 2 writes
`balance=80` (-20 from stale 100). Final: 80. Should be:
100+50-20=130. This is a data race: a real money loss
bug. No exception was thrown. Logs show nothing unusual.

**THE INVENTION MOMENT:**
Dijkstra (1965) formalised mutual exclusion with semaphores.
Hoare (1978) proposed CSP: communicate by sending messages,
not by sharing memory. Erlang (1986) adopted this: every
process is isolated; no shared state. Haskell's STM (2005)
enabled lock-free shared state with atomicity guarantees.

**EVOLUTION:**
Modern guidance: "Do not communicate by sharing memory;
share memory by communicating" (Go proverb). Java's
`java.util.concurrent` provides safe concurrent collections
and atomic operations. Rust's ownership system prevents data
races at compile time. The trend is away from locks toward
immutability, message passing, or STM.

---

### 📘 Textbook Definition

A **data race** occurs when two threads access the same
memory location without synchronisation and at least one
access is a write. **Race condition** (broader): a bug
where the outcome depends on the relative timing of thread
operations. **Deadlock**: two or more threads each hold
a lock the other needs, waiting forever. **Livelock**:
threads keep changing state in response to each other
but make no progress. **Starvation**: a thread perpetually
denied access to a resource because other threads keep
acquiring it first.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Shared mutable state creates race conditions; the fix is to eliminate sharing (message passing), eliminate mutation (immutability), or synchronise access (locks/atomics).

**One analogy:**

> Two people editing the same Google Doc simultaneously —
> both see the old version, make different changes, and one
> overwrites the other. The solution: edit a copy and merge
> (functional), take turns editing (locking), or use real-time
> collaborative edit (CRDT/STM). All three approaches exist
> in concurrent programming.

**One insight:**
The fundamental rule: "shared mutable state is the root of all
concurrency bugs." Eliminate mutable or eliminate shared —
either direction solves the problem. Erlang eliminates
sharing; Haskell eliminates mutation. Go uses channels.
Rust uses ownership to prevent sharing.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A data race = unsynchronised concurrent read+write to the same memory.
2. Data races cause _undefined behaviour_ in C/C++; in Java, partial reads/writes are possible.
3. Deadlock requires: mutual exclusion, hold-and-wait, no preemption, circular wait.
4. Break one Coffman condition — deadlock is impossible.
5. Atomic operations (CAS) are race-free by hardware guarantee; lock-based use at a coarser granularity.

**DERIVED DESIGN:**

- `synchronized` / `ReentrantLock` — mutual exclusion; risk of deadlock
- `AtomicLong`, `AtomicReference` — lock-free atomic operations (CAS)
- `ConcurrentHashMap`, `CopyOnWriteArrayList` — safe concurrent collections
- Immutable objects — safely shared without synchronisation
- `volatile` — visibility guarantee only; not atomicity

**THE TRADE-OFFS:**
**Locking:** Simple mental model; risk of deadlock; reduces parallelism.
**Lock-free (CAS):** No deadlock; but ABA problem; complex code.
**Immutability:** No synchronisation needed; but requires copying.
**Message passing:** No shared state; but channel overhead.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Multiple threads making progress on shared state requires coordination.
**Accidental:** Mutability of domain objects that need not be mutable.

---

### 🧪 Thought Experiment

**SETUP:**
Counter class incremented from 100 threads, 1000 times each.

**BUGGY VERSION (data race):**

```java
class Counter {
    int count = 0; // not thread-safe!
    void increment() {
        count++; // read-modify-write: 3 operations, not atomic!
        // T1: reads count=5000
        // T2: reads count=5000
        // T1: writes count=5001
        // T2: writes count=5001 (lost T1's increment!)
    }
}
// Expected: 100,000. Actual: 60,000 - 99,000 (varies per run)
```

**CORRECT VERSION 1 (synchronized):**

```java
synchronized void increment() { count++; }
```

**CORRECT VERSION 2 (AtomicInteger, lock-free):**

```java
AtomicInteger count = new AtomicInteger();
void increment() { count.incrementAndGet(); }
// CAS loop: read, add 1, compareAndSet; retry if raced
```

**THE INSIGHT:**
`count++` is 3 JVM instructions: `getfield`, `iadd`, `putfield`.
Another thread can intervene between any two. The fix: make
all 3 atomic (synchronized) or use hardware-native atomic
operations (CAS).

---

### 🧠 Mental Model / Analogy

> Shared mutable state is a communal whiteboard where everyone
> writes and erases. Without rules (synchronisation), people
> write over each other, erase in-progress content, and read
> half-written updates. Immutability: use paper instead of
> whiteboard — once written, never changed. Message passing:
> have a dedicated scribe who serialises all updates.
> Locking: one person at the whiteboard at a time.

**Element mapping:**

- Whiteboard = shared mutable state
- Writers = threads
- Erasing = writing a new value over the old
- Communal chaos = data race
- "One at a time" rule = mutex/synchronized
- Dedicated scribe = single-threaded actor model

Where this analogy breaks down: hardware cache coherence protocols
ensure that threads see each other's writes eventually (visibility),
but without ordering guarantees (happens-before).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When two people edit the same file at the same time, they
overwrite each other. Concurrency bugs happen when threads
read and write the same data without coordinating.

**Level 2 - How to use it (junior developer):**
Rule 1: Never share mutable state without synchronisation.
Rule 2: Prefer immutable objects (`final` fields, records).
Rule 3: Use `AtomicInteger`/`AtomicReference` for simple
counters/references; `ConcurrentHashMap` for maps.
Rule 4: `volatile` is not enough for compound operations.

**Level 3 - How it works (mid-level engineer):**
Java Memory Model: threads can cache values. Without
synchronisation, Thread B may not see Thread A's writes.
`volatile` ensures visibility (all writes are immediately
visible to all threads) but not atomicity (read-modify-write
still races). `synchronized` ensures both visibility
and atomicity within the critical section.

**Level 4 - Why it was designed this way (senior/staff):**
Hardware: CPUs have multiple cache levels (L1/L2/L3 per core).
A write to L1 cache is not immediately visible to another
core's cache. Cache coherence protocols (MESI) ensure eventual
consistency, but the JMM's happens-before relation specifies
the _minimum_ visibility guarantees. `synchronized` on
mutual exclusion establishes happens-before: all writes
before `unlock` are visible after `lock`. This is the
foundational guarantee the JMM provides.

**Expert Thinking Cues:**

- When reviewing multi-threaded code: where is shared mutable state? Is every access synchronised?
- When seeing `volatile`: is this a compound operation? If so, volatile alone is insufficient.
- When designing services: can domain objects be immutable? What's the cost?

---

### ⚙️ How It Works (Mechanism)

**Deadlock example:**

```java
// Thread 1: locks A then B
// Thread 2: locks B then A
// Classic circular wait -> deadlock

Object lockA = new Object();
Object lockB = new Object();
Thread t1 = new Thread(() -> {
    synchronized (lockA) {
        sleep(50); // allow t2 to lock B
        synchronized (lockB) { /* work */ }
    }
});
Thread t2 = new Thread(() -> {
    synchronized (lockB) {
        synchronized (lockA) { /* work */ }
    }
});
// Fix: always acquire locks in same order (lockA before lockB)
```

**ThreadSanitizer detection:**

```bash
# Java: enable with JVM agent
java -agentlib:threadsan -jar myapp.jar

# C++/Go/Rust: built-in TSan
go test -race ./...
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (deadlock detection):**

```
Thread dump shows BLOCKED threads  ← YOU ARE HERE
  |-> jstack <pid> | grep -A 30 BLOCKED
  |-> Thread-1: waiting on lock 0x123 (held by Thread-2)
  |-> Thread-2: waiting on lock 0x456 (held by Thread-1)
  |-> Circular wait -> deadlock confirmed
  |-> Fix: establish lock ordering; use ReentrantLock.tryLock
  |-> with timeout
```

**FAILURE PATH:**

- Data race: no exception; wrong results; non-reproducible
- Deadlock: `jstack` shows BLOCKED threads in circular dependency
- Livelock: threads not BLOCKED but CPU at 100%; no progress
- ThreadSanitizer: reports exact race with stack trace

---

### ⚖️ Comparison Table

| Anti-Pattern   | Symptom                | Detection                 | Fix                                |
| -------------- | ---------------------- | ------------------------- | ---------------------------------- |
| Data race      | Wrong values, silent   | ThreadSanitizer, Helgrind | Synchronise or make immutable      |
| Race condition | Intermittent failures  | Load testing, TSan        | Identify shared state; synchronise |
| Deadlock       | Threads stuck forever  | jstack BLOCKED threads    | Fix lock ordering or use tryLock   |
| Livelock       | 100% CPU, no progress  | CPU profiler              | Add backoff; randomise retry       |
| Starvation     | Some threads never run | Thread profiler           | Fair locks (FIFO queue)            |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                         |
| ---------------------------------------------- | ------------------------------------------------------------------------------- |
| "`volatile` makes operations thread-safe"      | `volatile` ensures visibility only; `x++` on a volatile is still a data race    |
| "synchronized on different objects is safe"    | synchronized only works if all threads use the _same_ lock object               |
| "Immutable objects don't need synchronisation" | True: share freely. But object graph must be completely immutable               |
| "ThreadLocal prevents all races"               | ThreadLocal prevents sharing, but leaks in thread pools (see CSF-049)           |
| "More locking = more safety"                   | More locking increases deadlock risk; prefer immutability and atomic operations |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Data Race (Silent Corruption)**
**Symptom:** Incorrect results under load; passes unit tests.
**Diagnostic:**

```bash
# Go
go test -race ./...
# Java: use Google's ThreadSanitizer or custom ByteBuddy agent
java -agentpath:/path/to/tsan.so -jar app.jar
```

**Fix:** Synchronise, use AtomicXxx, or make the field immutable.

**Mode 2: Deadlock**
**Symptom:** Service hangs; no progress; thread pool exhausted.
**Diagnostic:**

```bash
jstack <pid> | grep -E "BLOCKED|waiting to lock"
# Look for circular: T1 waits for T2; T2 waits for T1
```

**Fix:** Establish consistent lock acquisition order.

**Mode 3: Lock Contention (Scalability Issue)**
**Symptom:** Performance degrades under concurrency; synchronized method becomes bottleneck.
**Diagnostic:**

```bash
jstack <pid> | grep -c BLOCKED
# High count: lock contention
# async-profiler: -e lock -d 30 -f flame.svg
```

**Fix:** Reduce lock scope; use `ConcurrentHashMap` instead of `HashMap + synchronized`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-034 - Immutability]]
- [[CSF-041 - Concurrency Models Introduction]]

**Builds On This (learn these next):**

- [[CSF-060 - Concurrency Models Compared (Actor, CSP, STM)]]

**Alternatives / Comparisons:**

- Actor model (Erlang, Akka): no shared state
- STM: optimistic locking
- Rust ownership: compile-time data race prevention

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Bugs from unsynchronised shared mutable│
│                 state (races, deadlocks, corruption)   │
│ PROBLEM         Intermittent failures impossible to    │
│ IT SOLVES       reproduce without load                │
│ KEY INSIGHT     Eliminate sharing OR eliminate mutation;│
│                 both solve the root cause             │
│ USE WHEN        Detecting: ThreadSanitizer, jstack      │
│ AVOID           Shared mutable state without sync      │
│ TRADE-OFF       Locking (safe) vs lock-free (complex)  │
│ ONE-LINER       Shared + mutable = race; solve by      │
│                 removing one or the other            │
│ NEXT EXPLORE    CSF-060, ThreadSanitizer, Akka         │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Shared mutable state = root cause; fix by removing sharing or mutation.
2. `volatile` ensures visibility, not atomicity; `count++` is still a race on volatile.
3. Deadlock = circular lock dependency; fix by consistent lock ordering.

**Interview one-liner:**
"Shared mutable state causes data races (unsynchronised access), race conditions (timing-dependent bugs), and deadlocks (circular lock dependencies); the solution is to eliminate sharing via message passing, eliminate mutation via immutability, or synchronise with atomics/locks."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Shared + mutable = unsafe. Any time two agents (threads,
processes, services) modify shared state concurrently, you
need a coordination protocol. The simplest protocol is
"don't share" (message passing). The next simplest is
"don't mutate" (immutability). Locking is the last resort.

**Where else this pattern appears:**

- **Distributed transactions** — two services modifying shared DB state; saga or 2PC is the protocol
- **Git merge conflicts** — two developers modify the same file; merge is the coordination protocol
- **Database locking** — `SELECT FOR UPDATE`; same idea, at database level

---

### 💡 The Surprising Truth

Rust is the first mainstream systems language to prevent data
races at compile time — not via a runtime checker, but via
the ownership system. In Rust, at any point in time, a value
can have either one mutable reference OR many immutable
references, but never both. This invariant, enforced by the
borrow checker at compile time, makes data races impossible
by construction. The bugs that take Java programmers days
to find with ThreadSanitizer simply cannot exist in safe Rust.
This is a language design decision that imposes cost (borrow
checker complexity) but provides a mathematical safety guarantee.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** A Java `HashMap` is accessed concurrently
by multiple threads — reads only, no writes. Is this safe
without synchronisation? What about `ConcurrentHashMap` for
the same read-only scenario?

_Hint:_ A `HashMap` with no writes after construction and no
mutating methods called is safe to share for reads. But can
you guarantee no writes? What if the initial population
happens in a thread that publishes the reference unsafely?

**Q2 (Scale):** A distributed system with 100 nodes all
modifying a shared counter in a central Redis. Is Redis's
`INCR` command subject to race conditions? What guarantees
does Redis provide, and how do distributed counters differ
from in-process atomic counters?

_Hint:_ Redis `INCR` is atomic on a single node. What happens
if Redis is in cluster mode and the key is distributed? What
about network partitions?

**Q3 (Design Trade-off):** Erlang/Elixir enforces the actor
model: no shared state; processes communicate only by message
passing. What performance cost does this impose compared to
shared-memory multithreading? When is the actor model's safety
worth the performance overhead?

_Hint:_ Each message is a copy (or in some implementations,
a reference-counted immutable). Compare to Java's pass-by-reference
shared memory. What's the cost of copying large objects?
