---
id: JCC-055
title: Concurrency-First Thinking
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-001, JCC-056, JCC-002, JCC-020
used_by:
related: JCC-056, JCC-057, JCC-001
tags:
  - java
  - concurrency
  - advanced
  - mental-model
  - bestpractice
  - architecture
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /jcc/concurrency-first-thinking/
---

# JCC-055 - Concurrency-First Thinking

⚡ TL;DR - Concurrency-first thinking means identifying shared mutable state and thread boundaries at design time, not after a production race condition forces a retrofit.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | JCC-001, JCC-056, JCC-002, JCC-020 |     |
| **Related:**    | JCC-056, JCC-057, JCC-001          |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Developers write a class as if it will always run on a single thread. After deployment, a race condition surfaces in production - usually under load on a Friday afternoon. The fix is a `synchronized` retrofit: add locks around the class's methods. But retrofitting is dangerous. Locks change the class's observable behavior (lock ordering, contention). New bugs are introduced. The entire class must be re-analyzed for deadlock potential.

**THE BREAKING POINT:**
A senior engineer reviews a pull request and asks: "Is this class thread-safe?" Nobody knows. The class was written without considering concurrency. Its shared state is not documented. Its invariants are not stated. The answer requires reading 500 lines of code and reasoning about all possible thread interleavings. The review is blocked. This is the cost of concurrency-last thinking.

**THE INVENTION MOMENT:**
Brian Goetz's "Java Concurrency in Practice" (2006) introduces the concept of documenting thread-safety: annotate classes as `@ThreadSafe`, `@NotThreadSafe`, or `@Immutable`. More fundamentally, it argues that thread-safety is a design-time decision, not a retrofit. The book introduces the discipline: identify shared state → categorize by access pattern → choose synchronization policy → document it.

**EVOLUTION:**
2006: JCIP establishes the discipline. 2013-: Project Loom research reinforces that thread model choice (platform vs. virtual threads) is a design-time architectural decision. 2023: Java 21 structured concurrency makes lifetime a design-time concern. The discipline extends: not just "is this thread-safe?" but "what is this task's lifetime, and who owns its cancellation?"

---

### 📘 Textbook Definition

**Concurrency-first thinking** is a design discipline in which thread-safety, shared state identification, synchronization policy, and thread model selection are treated as first-class design concerns - addressed during system and class design, not added after functional implementation. It encompasses: (1) identifying which state is shared across threads, (2) choosing a thread-safety mechanism by construction (immutability, confinement, synchronization, lock-free), (3) documenting the synchronization policy explicitly, and (4) selecting the appropriate thread model (platform threads, virtual threads, reactive) before writing code.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Think about what is shared, who accesses it, and how it is protected before writing the first line of concurrent code.

**One analogy:**

> Concurrency-first thinking is like fire-code compliance for buildings. A fire code engineer reviews blueprints BEFORE construction: are escape routes clear? Are sprinklers placed correctly? Are fire doors in the right locations? Retrofitting a fire exit into a completed building is expensive and disruptive. Similarly, retrofitting thread-safety into a completed class is expensive and error-prone. Review the "blueprint" (class design) before coding.

**One insight:**
The most effective concurrency technique is elimination: if a class has no shared mutable state, it requires no synchronization. Concurrency-first thinking starts with "how do I make this state immutable or thread-confined?" not "how do I synchronize this mutable state?"

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **State ownership:** Every piece of mutable state has exactly one owner. Concurrent access requires explicit transfer of ownership or explicit sharing with synchronization.
2. **Thread-safety is a property of the class, not the method:** You cannot make individual methods thread-safe in isolation. Thread-safety requires reasoning about the entire class's state.
3. **The synchronization policy must be documented:** "Uses internal locking on `this`" or "requires caller to hold lock X" or "immutable" must be stated. Undocumented = unsafe to reason about.
4. **Prefer thread-safety by construction:** Immutability > confinement > synchronization > lock-free. Each choice from left to right adds complexity.

**DERIVED DESIGN:**
The concurrency-first design process:

1. List all instance/class state (fields, mutable objects referenced by fields).
2. Classify each: accessed by single thread only? Accessed by multiple threads?
3. For multi-thread accessed state: immutable? confined? published? synchronized?
4. Choose the synchronization policy: which lock guards which state.
5. Document in Javadoc: `@GuardedBy`, `@ThreadSafe`, `@Immutable`.

**THE TRADE-OFFS:**
**Gain:** Bugs caught at design review. Clear ownership model. Easier code review (synchronization policy is explicit). No surprise production race conditions.
**Cost:** Slower initial development. Requires discipline. Some state identification is not obvious (especially with dependency injection and framework-managed beans).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Shared mutable state requires synchronization. This is irreducible.
**Accidental:** Undocumented synchronization policy, implicit shared state, untested concurrency assumptions. All avoidable with concurrency-first thinking.

---

### 🧪 Thought Experiment

**SETUP:**
You are designing a service class that counts processed requests and caches the last result per user.

**CONCURRENCY-LAST DESIGN:**

```java
// BAD: no concurrency thought at design time
class RequestProcessor {
    private int processedCount = 0;
    private Map<String, Result> lastResult = new HashMap<>();

    public Result process(String userId, Request req) {
        processedCount++;  // RACE: non-atomic increment
        Result r = compute(req);
        lastResult.put(userId, r); // RACE: unsynchronized write
        return r;
    }
}
```

This class is broken under concurrent access. Retrofit requires: change `processedCount` to `AtomicInteger`, change `lastResult` to `ConcurrentHashMap` - but are these changes sufficient? Are there compound operations that need atomicity? Without thinking about this at design time, we may still have bugs.

**CONCURRENCY-FIRST DESIGN:**

1. State: `processedCount` (simple counter, no read-compute-write chain needed: `AtomicLong`). `lastResult` (last result per user, concurrent reads and writes: `ConcurrentHashMap`). No compound operations needed on both together.
2. Thread-safety mechanism: lock-free (`AtomicLong` + `ConcurrentHashMap`).
3. Document: `@ThreadSafe`.

**THE INSIGHT:**
The design-time question is not "which lock?" but "what is the access pattern for each piece of state?" This question must be answered before writing code.

---

### 🧠 Mental Model / Analogy

> Concurrency-first thinking is like thinking about database transactions during schema design. A good database architect asks: what data will be read together? What will be written together? Which reads need to be consistent with which writes? These questions determine index design, transaction boundaries, and isolation levels - all before any SQL is written. Concurrency-first thinking applies the same discipline to shared memory: what state is accessed together? What needs to be atomic? What is the isolation boundary (a `synchronized` block, an atomic field, or immutability)?

Element mapping:

- **Table schema** = class fields
- **Transaction boundaries** = synchronized blocks / atomic operations
- **Read-write mix** = access pattern (read-heavy, write-heavy, mixed)
- **Index** = data structure choice (ConcurrentHashMap, CopyOnWriteArrayList)

Where this analogy breaks down: database transactions are serializable by default. Java concurrency requires explicit synchronization. The default in Java is NO protection.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Concurrency-first thinking means asking "who will access this data at the same time?" when designing a class, not after bugs appear in production.

**Level 2 - How to use it (junior developer):**
When writing a class, ask: (1) Will this class be used by multiple threads? (2) Which fields will be read/written by multiple threads? (3) For each such field: use `final` if possible, `volatile` for visibility-only, `AtomicXxx` for simple operations, `synchronized` for compound operations. Document with `@GuardedBy`.

**Level 3 - How it works (mid-level engineer):**
Apply the JCIP checklist: identify all shared state. For each shared state variable, document what guards it (`@GuardedBy("this")` or `@GuardedBy("lock")`). Ensure all accesses to that state hold the specified guard. Verify no compound check-then-act sequences on shared state are left unguarded.

**Level 4 - Why it was designed this way (senior/staff):**
Concurrency-first is a response to a systematic failure mode: the ad hoc addition of `synchronized` to address symptoms (production crashes) rather than root causes (unsynchronized shared state). At the architectural level, concurrency-first thinking extends to service design: which microservices share state? (None, by design.) Which share a database? (That's the shared state.) What are the transaction boundaries? Thread model selection (thread-per-request, event loop, reactive) is a concurrency-first architectural decision that affects the entire codebase.

**Expert Thinking Cues:**

- "What is the synchronization policy for this class? Is it documented?"
- "Is there any shared mutable state that I have not explicitly thought about?"
- "Can I eliminate sharing entirely through confinement or immutability?"

---

### ⚙️ How It Works (Mechanism)

**CONCURRENCY-FIRST CLASS DESIGN:**

```java
/**
 * Thread-safe request processor.
 * State:
 *   processedCount - guarded by AtomicLong (lock-free)
 *   lastResultCache - guarded by ConcurrentHashMap (lock-free)
 */
@ThreadSafe
class RequestProcessor {
    // Lock-free counter: no compound read-modify-write
    private final AtomicLong processedCount = new AtomicLong();

    // Thread-safe map: concurrent reads/writes, no compound ops
    private final ConcurrentHashMap<String, Result> cache =
        new ConcurrentHashMap<>();

    public Result process(String userId, Request req) {
        processedCount.incrementAndGet(); // atomic, lock-free
        Result r = compute(req);
        cache.put(userId, r); // thread-safe
        return r;
    }

    public long getProcessedCount() {
        return processedCount.get(); // volatile read
    }
}
```

**THREAD-SAFETY BY CONSTRUCTION (IMMUTABILITY):**

```java
// BAD: mutable state with no synchronization thought
class Config {
    public String host;
    public int port;
    public Config(String h, int p) { host=h; port=p; }
}

// GOOD: immutable by construction, no synchronization needed
final class Config {
    private final String host;
    private final int port;
    public Config(String host, int port) {
        this.host = host;
        this.port = port;
    }
    public String host() { return host; }
    public int port() { return port; }
}
// @Immutable: no synchronization required anywhere
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CONCURRENCY-FIRST DESIGN PROCESS:**

```
1. List class state:
   fields: counter, cache, config
                |
2. Classify access:
   counter: multi-thread RW <- YOU ARE HERE
   cache: multi-thread RW
   config: immutable after construction
                |
3. Choose mechanism:
   counter -> AtomicLong (simple increment)
   cache -> ConcurrentHashMap (concurrent map)
   config -> final fields (immutability)
                |
4. Document synchronization policy:
   @ThreadSafe
   @GuardedBy("AtomicLong") for counter
   @GuardedBy("ConcurrentHashMap") for cache
                |
5. Verify: code review checks all accesses use the policy
```

**FAILURE PATH:**
Skip step 2: miss that `cache` is shared. Use `HashMap` instead of `ConcurrentHashMap`. Concurrent `put()` operations corrupt the map's internal structure. `HashMap` is not thread-safe under concurrent modifications - data corruption, `ConcurrentModificationException`, or infinite loop in `get()` (Java 6 bug).

**WHAT CHANGES AT SCALE:**
At service level, concurrency-first thinking extends to: stateless services (no shared mutable state between requests), immutable configuration (loaded once, never modified), event sourcing (append-only state, no concurrent modification). These architectural patterns are the service-level application of the same principle: eliminate sharing before attempting to synchronize it.

---

### ⚖️ Comparison Table

| Approach               | Thread-Safety            | Complexity | When to Use                                  |
| ---------------------- | ------------------------ | ---------- | -------------------------------------------- |
| Immutability           | Perfect (no sync needed) | Low        | Configuration, value objects, DTOs           |
| Thread Confinement     | Perfect (no sharing)     | Low        | Per-request state, ThreadLocal               |
| Synchronized           | Correct (with care)      | Medium     | Compound operations, complex invariants      |
| Lock-Free (Atomic)     | Correct                  | Medium     | Simple counters, flags, single-field updates |
| Concurrent Collections | Correct for map ops      | Low        | Caches, shared data stores                   |
| No protection          | Broken                   | Zero       | Single-threaded only                         |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                     |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "I'll add synchronization later if needed"                     | Race conditions in production are harder to diagnose and fix than design-time decisions. The retrofit is always more expensive and error-prone than getting it right first.                                                 |
| "If my tests pass, the class is thread-safe"                   | Functional tests do not expose most race conditions. Thread interleavings are timing-dependent. A class can pass 10,000 tests and still have a race condition that appears only under specific production load.             |
| "Spring beans are single-instance so they must be thread-safe" | Spring singleton beans ARE shared across threads. They are the canonical example of shared mutable state. Any mutable field in a Spring service is a potential race condition.                                              |
| "Making all methods synchronized is safe"                      | Synchronized methods guarantee individual method atomicity. They do NOT guarantee that compound operations across methods (check-then-act, read-modify-write spanning two method calls) are atomic.                         |
| "This class won't be used concurrently"                        | This assumption is almost always wrong for any class used in a web application or shared service. Document the assumption and ensure it is enforced (e.g., by only instantiating the class inside a single thread's scope). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Unsynchronized Spring Bean State**
**Symptom:** Intermittent wrong results in web application. Values from one user's request appear in another user's response.
**Root Cause:** A `@Service` or `@Component` bean has a mutable instance field (e.g., `private List<X> buffer`) that is written per request without synchronization.
**Diagnostic:**

```bash
# Find all mutable instance fields in @Service/@Component classes
grep -rn "@Service\|@Component" src/ -l | \
  xargs grep -l "private [^f].*;" | head -20
# Review each for non-final, non-volatile mutable fields
```

**Fix:**

```java
// BAD: mutable state in singleton Spring bean
@Service
class ReportService {
    private List<String> buffer = new ArrayList<>();  // RACE!
    public void generate(String item) { buffer.add(item); }
}

// GOOD: stateless (move state to method scope)
@Service
class ReportService {
    public Report generate(List<String> items) {
        // items is a parameter, not shared state
        return new Report(items);
    }
}
```

**Prevention:** Spring singleton beans should be stateless. Any mutable state should be per-request (in method parameters or local variables), not instance fields.

---

**Failure Mode 2: Check-Then-Act Race (Compound Operation)**
**Symptom:** Duplicate records in database. Two threads pass a uniqueness check simultaneously and both insert.
**Root Cause:** `if (!exists(key)) insert(key)` is not atomic. Two threads can both evaluate `exists` as false before either inserts.
**Diagnostic:**

```bash
# Look for if-then-insert patterns without transactions
grep -rn "if.*!.*exist.*\|if.*null.*insert" src/ | \
  grep -v "@Transactional\|synchronized"
```

**Fix:**

```java
// BAD: check-then-act race
if (!cache.containsKey(key)) {
    cache.put(key, computeValue(key));
}

// GOOD: atomic putIfAbsent
cache.computeIfAbsent(key, k -> computeValue(k));
```

**Prevention:** Use atomic compound operations: `computeIfAbsent`, `putIfAbsent`, `CAS`, or database UNIQUE constraints + retry.

---

**Failure Mode 3: ThreadLocal Memory Leak in Thread Pools**
**Symptom:** Memory grows over time. Heap analysis shows large `ThreadLocal` values accumulating.
**Root Cause:** `ThreadLocal` variables set per-request are never removed. In a thread pool, threads are reused. `ThreadLocal` values from previous requests persist in pooled threads.
**Diagnostic:**

```bash
# Heap dump + MAT analysis: look for ThreadLocalMap entries
jmap -dump:format=b,file=heap.hprof <pid>
# In MAT: search for ThreadLocal -> find large retained heaps
```

**Fix:**

```java
// BAD: ThreadLocal not cleaned up
static final ThreadLocal<UserContext> ctx = new ThreadLocal<>();
public void handle(Request r) {
    ctx.set(new UserContext(r.userId())); // set, never remove
    process();
}

// GOOD: always clean up in finally
public void handle(Request r) {
    try {
        ctx.set(new UserContext(r.userId()));
        process();
    } finally {
        ctx.remove(); // always clean up
    }
}
```

**Prevention:** Use `try-finally` around all `ThreadLocal.set()` calls. Consider `ScopedValue` (Java 21+) instead of `ThreadLocal` - `ScopedValue` is automatically scoped and cleaned up.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-001 - Thread Safety]] - the foundational concept
- [[JCC-002 - Race Conditions]] - what happens without concurrency-first thinking
- [[JCC-020 - Java Memory Model (JMM)]] - visibility rules for shared state

**Builds On This (learn these next):**

- [[JCC-056 - Shared State Risk Intuition]] - deeper pattern recognition for shared state
- [[JCC-057 - Thread Safety Trade-off Framing]] - choosing between approaches

**Alternatives / Comparisons:**

- [[JCC-046 - Concurrency Architecture Patterns in Java]] - applying these principles at the system level

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Design discipline: identify shared │
│               │ state and sync policy at design    │
│ PROBLEM       │ Concurrency retrofit = bugs        │
│ KEY INSIGHT   │ Thread-safety by construction >    │
│               │ thread-safety by retrofit          │
│ USE WHEN      │ Always - before writing any class  │
│               │ used in a multi-thread context     │
│ AVOID WHEN    │ Provably single-thread only code   │
│ TRADE-OFF     │ Design time investment vs. prod    │
│               │ incident time                      │
│ ONE-LINER     │ List state, classify access,       │
│               │ choose mechanism, document it      │
│ NEXT EXPLORE  │ JCC-056 Shared State Risk Intuition│
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Identify shared mutable state at design time, not after production incidents.
2. Prefer thread-safety by construction: immutability > confinement > synchronization.
3. Spring singleton beans are shared. Stateless > stateful for beans.

**Interview one-liner:**
"Concurrency-first thinking means identifying which class state is shared across threads at design time, choosing the synchronization policy (immutability, confinement, lock, lock-free) before writing code, and documenting it explicitly - because retrofitting thread-safety after the fact is error-prone and expensive."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Safety properties (thread-safety, memory safety, type safety) are cheapest to enforce at design time. The cost curve for fixing safety issues grows exponentially: design-time fix costs 1x, code review costs 3x, test discovery costs 10x, production incident costs 100x. Any discipline that moves safety concerns earlier in the development lifecycle has a high ROI.

**Where else this pattern appears:**

- **Type-driven design (Haskell, Rust):** Making illegal states unrepresentable in the type system is "correctness-first thinking" - the type system catches bugs at compile time instead of runtime. Same principle: make correctness the path of least resistance.
- **Security threat modeling (STRIDE):** Security architects enumerate threats during design, not after penetration testing. "Security-first thinking" is the same move: classify assets, identify threats, choose mitigations before coding.
- **Database normalization:** Eliminating data duplication during schema design prevents update anomalies. Concurrency-first thinking's "eliminate sharing" maps to normalization's "eliminate redundancy" - both make a class of bug structurally impossible.

---

### 💡 The Surprising Truth

The "stateless service" recommendation in microservices architecture is not primarily a scalability concern - it is a concurrency-first design decision. A stateless service has no shared mutable instance state between requests, which means it has no synchronization requirements, no race conditions, and no thread-safety bugs by construction. The recommendation that "services should be stateless" is actually the service-level application of the concurrency design principle "eliminate sharing." When architects say "don't store state in the service, store it in the database," they are applying concurrency-first thinking at the architecture level: push mutable state to a system (the database) that is specifically designed to manage concurrent access safely.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** A Spring `@Service` class has a `@Autowired` dependency that is a prototype-scoped bean (new instance per injection). Is the prototype bean's state "shared" between threads? Does the `@Service` class need to synchronize access to it?
_Hint:_ The `@Service` is a singleton. The prototype bean is injected ONCE at creation time - the same instance is shared across all threads accessing the service. Prototype scope does not prevent sharing when injected into a singleton.

**Q2 (B - Scale):** At the microservices level, "stateless services" solve the shared state problem by pushing state to a database. But the database itself becomes the shared mutable state. What concurrency-first mechanisms does a database provide that a Java class does not have by default?
_Hint:_ Transactions, isolation levels, MVCC, optimistic/pessimistic locking, UNIQUE constraints. The database is a specialized concurrent state manager. What can Java code learn from how databases handle shared state?

**Q3 (C - Design Trade-off):** `CopyOnWriteArrayList` is thread-safe and requires no external synchronization. It achieves this by copying the entire backing array on every write. When is this the WRONG thread-safety mechanism, even though it is technically correct?
_Hint:_ Consider a list with 10,000 elements that is written to frequently. What is the memory and time cost of each write? What access pattern makes `CopyOnWriteArrayList` the right choice?
