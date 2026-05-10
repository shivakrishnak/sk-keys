---
id: JCC-002
title: "The Thread Safety Problem: A Mental Model"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★☆☆
depends_on: JCC-001
used_by: JCC-014, JCC-038, JCC-040, JCC-044, JCC-015
related: JCC-001, JCC-044, JCC-015
tags:
  - java
  - concurrency
  - foundational
  - mental-model
  - thread-safety
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 2
permalink: /jcc/the-thread-safety-problem-a-mental-model/
---

# JCC-002 - The Thread Safety Problem: A Mental Model

⚡ TL;DR - A class is thread-safe when it behaves correctly when accessed from multiple threads simultaneously, with no need for external synchronization by the caller.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | JCC-001                                     |     |
| **Used by:**    | JCC-014, JCC-038, JCC-040, JCC-044, JCC-015 |     |
| **Related:**    | JCC-001, JCC-044, JCC-015                   |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You write a `Counter` class with an `increment()` method. It works perfectly in every test. You deploy it. A week later, a production audit reveals the counter is off by thousands. You add more tests - they all pass. The problem only manifests under concurrent load. Without a mental model for thread safety, you have no systematic way to reason about what is safe and what is not.

**THE BREAKING POINT:**
A team of four engineers each writes a class they "think" is thread-safe. They compose them together. The system fails under load in ways no individual class would predict. Without shared vocabulary and a structured framework for reasoning about thread safety, a team cannot build reliable concurrent software.

**THE INVENTION MOMENT:**
Brian Goetz's _Java Concurrency in Practice_ gave the field a structured vocabulary: **thread-safe**, **conditionally thread-safe**, **not thread-safe**, **immutable**, **thread-hostile**. This entry systematizes that vocabulary into a mental model you can apply mechanically to any class or design.

**EVOLUTION:**
The model applies to all Java concurrency tools from Java 1.0 through Java 21. Virtual Threads (Project Loom) change the threading model but do NOT eliminate the need for thread safety - they simply make it cheaper to have many threads, which increases the probability of concurrent access to shared state.

---

### 📘 Textbook Definition

**Thread safety** is a property of a class or method: an object is **thread-safe** if it behaves correctly (preserves its invariants and produces correct results) when accessed concurrently by multiple threads, regardless of how the runtime schedules those threads, without requiring additional coordination from the caller. Thread safety is not binary - it exists on a spectrum from fully immutable (always safe) through explicitly synchronized (safe with correct lock usage) to thread-hostile (cannot be made safe at all without redesign).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Thread safety means the class is responsible for its own correctness under concurrent access - the caller does not need to think about it.

**One analogy:**

> A vending machine is thread-safe: each button press is isolated, the machine handles concurrent button presses without dispensing the wrong item or getting stuck. A shared notebook is not thread-safe: two people writing simultaneously produce illegible scrawl. The machine encapsulates the coordination; the notebook requires the users to coordinate externally.

**One insight:**
Thread safety is about **invariants**, not about methods. A class has invariants (e.g., "balance is never negative", "size equals actual element count"). Thread safety means those invariants hold even under arbitrary concurrent access.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Thread safety is a class-level property**, not a method-level property. If any method can violate a class invariant under concurrent access, the class is not thread-safe.
2. **The three requirements for thread safety:** visibility (threads see current values), atomicity (compound operations complete without interleaving), ordering (operations happen in a consistent sequence).
3. **Immutability is the strongest guarantee** - an object with no mutable state requires no synchronization and is always thread-safe.
4. **Encapsulation enables thread safety** - if mutable state is fully encapsulated (no leaked references), the class can enforce synchronization on all state accesses internally.

**DERIVED DESIGN:**
Given invariant 3 (immutability): design classes to be immutable by default. Only introduce mutability where performance demands it. This is why `String`, `Integer`, and all JVM boxed types are immutable.

Given invariant 4 (encapsulation): never publish a reference to mutable internal state. `return Collections.unmodifiableList(internalList)` instead of `return internalList`. A leaked reference bypasses all internal synchronization.

**THE TRADE-OFFS:**
**Gain:** Thread-safe classes can be composed freely - the caller does not need to reason about concurrent access.
**Cost:** Synchronization has overhead. Over-synchronization (making everything `synchronized`) causes contention and reduces performance.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any mutable state accessed by multiple threads requires some form of coordination. This cost is irreducible.
**Accidental:** Most complexity comes from shared mutable state that could be avoided. Stateless objects, immutable value objects, and thread-local state reduce the problem domain significantly.

---

### 🧪 Thought Experiment

**SETUP:**
A `LazyCache<K,V>` class has a `get(K key)` method: if the key is not in the map, compute the value and cache it. Two threads call `get("user-42")` simultaneously.

**WHAT HAPPENS WITHOUT THREAD SAFETY:**
Thread A checks `containsKey("user-42")` - returns false. Thread B checks `containsKey("user-42")` - also returns false. Both threads compute the value. Thread A inserts it. Thread B overwrites it. If the computation is idempotent, this is just wasted work. If it has side effects (assigning an ID, sending an email), the bug is catastrophic.

**WHAT HAPPENS WITH THREAD SAFETY:**
Using `ConcurrentHashMap.computeIfAbsent(key, fn)`, the atomic check-and-insert guarantees the function runs at most once per key. Callers compose freely - no external lock needed.

**THE INSIGHT:**
Thread safety is not about preventing concurrent execution - it is about ensuring that concurrent execution does not violate class invariants. The invariant here is "each key is computed at most once." A thread-safe implementation enforces this invariant internally.

---

### 🧠 Mental Model / Analogy

> A bank vault with a single combination lock vs. a bank vault with individual locked safety-deposit boxes. The single lock (coarse-grained) means one person at a time - very safe but slow. The individual boxes (fine-grained) let multiple people access different boxes simultaneously - equally safe, much faster.

Element mapping:

- **Bank vault** = the object's mutable state
- **Combination lock** = `synchronized(this)` - one thread at a time
- **Individual safety-deposit boxes** = fine-grained locks or `ConcurrentHashMap` segments
- **Customer with a key** = thread accessing the object
- **Vault rules enforced by staff** = the class's internal synchronization

Where this analogy breaks down: a real vault's state is physically partitioned into boxes. Object state is often interconnected (invariants span multiple fields), making fine-grained locking harder to reason about.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Thread safety means a class handles being used by multiple people simultaneously, without mixing up their data or corrupting its own state. A safe class takes care of the coordination internally so the user does not have to think about it.

**Level 2 - How to use it (junior developer):**
When using a JDK class, check its documentation. `ArrayList` is not thread-safe (use `CopyOnWriteArrayList` or `Collections.synchronizedList()`). `HashMap` is not thread-safe (use `ConcurrentHashMap`). `StringBuilder` is not thread-safe (use `String` or `StringBuffer`). When writing your own class, protect all accesses to mutable fields with `synchronized` blocks or use `Atomic*` classes.

**Level 3 - How it works (mid-level engineer):**
Thread safety requires addressing all three failure modes. Use `volatile` or locks for visibility of shared variables. Use `synchronized` blocks or atomic operations for atomicity of compound operations. Ensure the happens-before chain is unbroken between writers and readers. A class that gets visibility right but not atomicity still fails: `if (map.containsKey(k)) return map.get(k)` is not atomic even with a `ConcurrentHashMap`.

**Level 4 - Why it was designed this way (senior/staff):**
Thread safety is fundamentally about invariant preservation. A class defines invariants (state validity conditions). Under single-threaded execution, invariants can be temporarily broken and restored within a method call. Under concurrent execution, another thread can observe the invariant-broken intermediate state. Thread safety means either (a) the invariant is never broken (immutability), (b) the intermediate state is invisible to other threads (atomic operations, lock-protected critical sections), or (c) the intermediate state is documented and acceptable (e.g., `ConcurrentHashMap.size()` is approximate).

**Expert Thinking Cues:**

- "What are the invariants of this class? Which ones span multiple fields?"
- "Is there shared mutable state? Can I eliminate it with immutability or thread-local state?"
- "If two threads enter this method simultaneously, what intermediate states can each observe?"

---

### ⚙️ How It Works (Mechanism)

**THE THREAD SAFETY SPECTRUM:**

```
Immutable ──► Stateless ──► Thread-Safe ──► Conditional ──► Not Safe
(String)   (no fields)   (AtomicInteger)   (syncList)     (ArrayList)
```

**IMMUTABLE:** No mutable state. No synchronization needed. All fields `final`, set in constructor. Examples: `String`, `Integer`, `LocalDate`.

**STATELESS:** No fields at all (or only final fields referencing immutable objects). Each method call is self-contained. Stateless servlets, stateless Spring beans. Always thread-safe.

**THREAD-SAFE:** Has mutable state, all state access internally synchronized. Callers need no external coordination. Examples: `AtomicInteger`, `ConcurrentHashMap`, `BlockingQueue` implementations.

**CONDITIONALLY THREAD-SAFE:** Individual operations are thread-safe, but compound operations are not. `Collections.synchronizedList()` - each `add()` and `get()` is atomic, but `if (!list.contains(x)) list.add(x)` requires an external lock.

**NOT THREAD-SAFE:** `ArrayList`, `HashMap`, `StringBuilder`. Safe for single-threaded use or when access is externally synchronized.

**THREAD-HOSTILE:** Cannot be made safe even with external synchronization. Modifies global/static state in a way inherently uncoordinated across threads.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (designing a thread-safe class):**

```
Identify mutable state
    │
    ▼
Can state be eliminated? ──YES──► Use immutable/final
    │ NO                           ← YOU ARE HERE
    ▼
Accessed by one thread? ──YES──► Use ThreadLocal
    │ NO
    ▼
Choose synchronization:
  ├─ Simple counter → AtomicInteger
  ├─ Map → ConcurrentHashMap
  ├─ Compound op → synchronized block
  └─ Complex invariants → ReentrantLock
```

**FAILURE PATH:**
The most common failure: individual methods are `synchronized` but callers combine them into non-atomic compound operations. The class appears thread-safe but is not.

**WHAT CHANGES AT SCALE:**
At scale, thread safety becomes a performance problem. Coarse-grained locking serializes throughput. Solutions: reduce shared state, partition state (sharding), use non-blocking algorithms (CAS), or switch from shared state to message passing.

---

### ⚖️ Comparison Table

| Safety Level       | Mutable State       | Sync Required         | Examples                             | Composable? |
| ------------------ | ------------------- | --------------------- | ------------------------------------ | ----------- |
| Immutable          | No                  | No                    | `String`, `Integer`                  | Yes         |
| Stateless          | No fields           | No                    | Stateless servlet                    | Yes         |
| Thread-safe        | Yes, guarded        | Internal              | `AtomicInteger`, `ConcurrentHashMap` | Yes         |
| Conditionally safe | Yes, guarded        | External for compound | `synchronizedList`                   | No          |
| Not thread-safe    | Yes, unguarded      | External required     | `ArrayList`, `HashMap`               | No          |
| Thread-hostile     | Global side effects | Cannot fix            | Static mutable singletons            | No          |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                 |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "A `synchronized` method makes the class thread-safe"     | It prevents concurrent execution of that method, but compound operations across multiple calls are still unsafe. Thread safety is about class-level invariants, not individual methods. |
| "Thread-safe collections make my code thread-safe"        | `ConcurrentHashMap` does not fix `if (!map.containsKey(k)) map.put(k, v)` - still a race. Use `putIfAbsent` or `computeIfAbsent`.                                                       |
| "Immutable objects are slow because of defensive copying" | JVMs optimize immutable objects well - they can be freely shared, cached, and JIT-eliminated. Savings in synchronization usually outweigh copying costs.                                |
| "Read-only operations don't need synchronization"         | A `get()` on a non-volatile, non-synchronized field may return a stale value. Reads require the same visibility guarantees as writes.                                                   |
| "Thread safety only matters for setters"                  | Getters returning mutable object references leak internal state, bypassing all synchronization.                                                                                         |
| "My class is thread-safe because concurrent tests passed" | Tests rarely achieve the interleavings that cause bugs. Formal reasoning about invariants and happens-before is required.                                                               |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Leaked Mutable Reference**
**Symptom:** Thread-safe class is observed to have corrupted state despite all methods being synchronized.
**Root Cause:** A method returns a reference to an internal mutable collection or array, bypassing all internal synchronization.
**Diagnostic:**

```bash
grep -n "return .*List\|return .*Map\|return .*\[\]" \
  src/main/java/
```

**Fix:**

```java
// BAD: leaks internal mutable state
public List<String> getItems() { return items; }

// GOOD: unmodifiable view
public List<String> getItems() {
    return Collections.unmodifiableList(items);
}
```

**Prevention:** Never return a reference to internal mutable state.

---

**Failure Mode 2: Compound Operation Race**
**Symptom:** Individually synchronized operations work correctly, but combined usage produces wrong results.
**Root Cause:** The check-then-act pattern is not atomic even when each individual operation is synchronized.
**Diagnostic:**

```bash
jstack <pid> | grep -B5 -A30 "BLOCKED"
```

**Fix:**

```java
// BAD: check and put are individually safe, not atomic together
if (!concurrentMap.containsKey(key)) {
    concurrentMap.put(key, value); // race
}

// GOOD: single atomic operation
concurrentMap.computeIfAbsent(key, k -> computeValue(k));
```

**Prevention:** Identify compound operations and use atomic equivalents or a single lock scope.

---

**Failure Mode 3: Unsafe Publication (Security)**
**Symptom:** A freshly constructed object is visible to other threads in a partially initialized state.
**Root Cause:** The reference is published (made visible to other threads) before the constructor completes.
**Diagnostic:**

```bash
grep -n "new Thread(this)\|bus.register(this)\|listener.add(this)" \
  src/main/java/
```

**Fix:**

```java
// BAD: 'this' escapes before constructor completes
class Service {
    Service(EventBus bus) {
        bus.register(this); // 'this' escapes
        this.cache = new HashMap<>();
    }
}

// GOOD: factory method ensures full construction first
class Service {
    static Service create(EventBus bus) {
        Service s = new Service();
        bus.register(s); // fully constructed
        return s;
    }
}
```

**Prevention:** Never let `this` escape a constructor.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-001 - Why Concurrency Is Hard]] - the three root causes this model addresses
- [[JCC-044 - Java Memory Model (JMM)]] - formal definition of visibility and ordering

**Builds On This (learn these next):**

- [[JCC-014 - synchronized]] - the primary Java tool for enforcing thread safety
- [[JCC-038 - volatile]] - visibility without mutual exclusion
- [[JCC-015 - Race Condition]] - detailed analysis of the atomicity failure
- [[JCC-054 - ConcurrentHashMap]] - canonical thread-safe collection

**Alternatives / Comparisons:**

- [[JCC-043 - ThreadLocal]] - eliminate sharing rather than synchronize it
- [[JCC-055 - CopyOnWriteArrayList]] - thread safety via immutable snapshots
- [[JCC-056 - Atomic Classes]] - lock-free thread safety for single variables

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Framework for reasoning about safety │
│ PROBLEM       │ Concurrent access breaks invariants  │
│ KEY INSIGHT   │ Safety = invariants hold under conc. │
│ USE WHEN      │ Designing any shared-state class     │
│ AVOID WHEN    │ N/A - it is a design lens, not a tool│
│ TRADE-OFF     │ Safety enforcement vs. throughput    │
│ ONE-LINER     │ Safe = class invariants hold always  │
│ NEXT EXPLORE  │ JCC-014 synchronized, JCC-054 CHM    │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Thread safety is about invariants, not individual methods.
2. Immutability is the strongest form of thread safety.
3. Compound operations require atomic treatment even with thread-safe collections.

**Interview one-liner:**
"A thread-safe class preserves its invariants under arbitrary concurrent access - visibility, atomicity, and ordering are all enforced internally so the caller requires no external coordination."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Encapsulate coordination. The entity that owns the state is responsible for correctness of concurrent access. Callers should not need to know about or coordinate the internal synchronization strategy.

**Where else this pattern appears:**

- **Database ACID transactions:** The database engine enforces atomicity and isolation internally. Applications do not manually prevent other queries from reading mid-transaction state.
- **React `useState` hook:** React batches state updates internally so the UI always reflects a consistent snapshot.
- **OS file system:** Kernel `open()`/`write()`/`close()` operations are internally atomic and isolated between processes.

---

### 💡 The Surprising Truth

The most battle-hardened Java engineers often say: "The best synchronization is no synchronization." The majority of thread-safety bugs in production Java systems come from shared mutable state that should never have been shared in the first place. Designing for immutability, statelessness, or message-passing eliminates entire categories of bugs before a single lock is written. `ConcurrentHashMap` and `AtomicInteger` are last resorts, not primary tools. The primary tool is design: minimizing the surface area of shared mutable state.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** A Spring `@Service` bean is a singleton by default. If it has an instance field `private Map<String, Object> cache = new HashMap<>()`, is it thread-safe? What is the exact failure mode and minimum change to fix it?
_Hint:_ Consider how many threads share the same bean instance in a web server handling concurrent requests.

**Q2 (C - Design Trade-off):** A developer proposes making every field `volatile` to ensure visibility. This eliminates the visibility problem. What problems does it NOT solve, and what performance cost does it introduce?
_Hint:_ Review which of the three root causes `volatile` addresses. Consider what a memory barrier costs at the CPU level.

**Q3 (D - Root Cause):** Two threads use `Collections.synchronizedList()`. Thread A iterates the list. Thread B removes an element mid-iteration. A `ConcurrentModificationException` is thrown despite `synchronizedList` being "thread-safe." Why does this happen?
_Hint:_ Look at the javadoc for `Collections.synchronizedList()` and the note about iteration requiring an external lock.
