---
id: CSF-038
title: Immutability
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
  - pattern
status: draft
version: 2
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /csf/immutability/
---

# CSF-036 - Immutability

⚡ TL;DR - Immutability means a value cannot be changed after creation; this eliminates entire classes of concurrency bugs and makes code dramatically easier to reason about.

| CSF-036         | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-004, CSF-014, CSF-035             |                 |
| **Used by:**    | CSF-043, CSF-044, CSF-057, CSF-052    |                 |
| **Related:**    | CSF-004, CSF-043, CSF-052, CSF-064    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a mutable world, any object can be changed by any code that
has a reference to it. A list passed to a function might be
sorted, filtered, or cleared. Thread A modifies a shared map
while Thread B reads it. Defensive copying is the only safety
mechanism — and it's expensive and easy to forget.

**THE BREAKING POINT:**
Multicore CPUs made mutable shared state catastrophic. Two threads
writing to the same object without synchronisation produces data
corruption. Adding locks everywhere creates deadlock potential.
The fundamental problem: mutable shared state is the root cause
of most concurrency bugs.

**THE INVENTION MOMENT:**
Functional languages (Lisp, Haskell, Erlang) made immutability
the default. The insight: if values never change, sharing them
between threads is always safe — no locks needed. Modern
languages brought this mainstream: Java's `final`, Kotlin's `val`,
Rust's default-immutable bindings, Scala's `val`.

**EVOLUTION:**
Persistent data structures (Clojure, Scala) made immutability
practical for collections: instead of copying the entire
collection on update, they share structure. A "new" vector with
one element added shares all other elements with the original.
This made immutability cheap as well as safe.

---

### 📘 Textbook Definition

**Immutability** is the property of an object or value that
prevents it from being modified after creation. An **immutable
object** exposes no mutating methods; all "updates" return new
objects. An **immutable variable** (binding) cannot be reassigned
after initialisation. Immutability eliminates temporal coupling:
the need to reason about _when_ a value was modified.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Immutable values never change after creation: share freely, no locks needed, no surprises.

**One analogy:**

> An immutable value is like a published book. Once printed, it
> can't be edited. Any two readers can read it simultaneously
> without conflict. To make a new edition, you print a new book
> (create a new value). The old book still exists.

**One insight:**
If a value can never change, you never need to wonder "who
modified this?" or "what was the value when?". Immutability
eliminates an entire category of debugging: temporal coupling bugs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An immutable value, once created, is a permanent fact.
2. Sharing immutable values is always thread-safe.
3. Immutable objects are their own defensive copies.
4. "Updating" an immutable value means creating a new value.
5. Persistent data structures make immutable updates cheap via structural sharing.

**DERIVED DESIGN:**

- `final` in Java — immutable binding (reference can't change)
- `String` in Java/Python — immutable value (contents can't change)
- `val` in Kotlin/Scala — immutable binding
- `let` (not `var`) in Rust — default immutable (mutation requires `mut`)
- `freeze()` in JavaScript — shallow immutability
- Persistent collections in Clojure/Scala — immutable + cheap updates

**THE TRADE-OFFS:**
**Gain:** Thread safety, referential transparency, easier testing,
free caching (immutable == safe to cache).
**Cost:** "Updates" require new allocations; more GC pressure
(mitigated by persistent data structures).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Some data must change (counters, queues).
**Accidental:** Mutating objects that don't need to be mutable,
mutable default arguments in Python, aliased mutation bugs.

---

### 🧪 Thought Experiment

**SETUP:**
Two threads process a user's shopping cart simultaneously.

**MUTABLE CART:**

```java
// Thread A: applies discount
cart.setTotal(cart.getTotal() * 0.9);
// Thread B: adds item (concurrently)
cart.addItem(new Item("Shoes", 50));
// Result: lost update or corrupted total
```

**IMMUTABLE CART:**

```java
// Thread A: creates discounted cart
Cart discounted = cart.withDiscount(0.9); // new cart, original unchanged
// Thread B: creates cart with item
Cart withShoes = cart.withItem(new Item("Shoes", 50)); // new cart
// No race: neither thread modifies the shared cart
```

**THE INSIGHT:**
Immutability doesn't prevent change — it prevents _shared
change_. Each operation produces a new value. The original is
never modified. No synchronisation needed.

---

### 🧠 Mental Model / Analogy

> Immutable values are like photographs. You can share a photograph
> with anyone — no matter how many people look at it, the photo
> doesn't change. To have a "different" photo, you take a new one.
> Mutable values are like a whiteboard — anyone can erase and
> rewrite, and you must coordinate who has the marker.

**Element mapping:**

- Photograph = immutable value
- Sharing photographs = passing immutable references (no copying needed)
- Taking a new photo = creating an updated value
- Whiteboard = mutable shared state
- Marker = write lock

Where this analogy breaks down: taking a "new photo" (allocating
a new object) has a cost; persistent data structures minimise
this by sharing unchanged parts.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An immutable thing can never be changed after it's created.
A name written in permanent marker vs pencil. You can't modify
the permanent-marker name; you write a new one instead.

**Level 2 - How to use it (junior developer):**
Use `final` for fields that don't change. Use `String` instead
of `StringBuilder` for values you don't need to mutate.
Return new objects from methods instead of mutating parameters.
Use Java's `Collections.unmodifiableList()` or `List.of()` for
immutable collections.

**Level 3 - How it works (mid-level engineer):**
Persistent data structures (Clojure's PersistentVector,
Scala's immutable collections) use _structural sharing_:
a 32-way trie where updating one element creates a new path
from root to the leaf (O(log32 n) = ~5 nodes) while reusing
all unchanged nodes. Appending to a 1,000-element vector
allocates ~5 nodes, not 1,001.

**Level 4 - Why it was designed this way (senior/staff):**
Immutability is the foundation of _referential transparency_: an
expression that can be replaced by its value without changing
program behaviour. This property enables memoisation, equational
reasoning, and compile-time evaluation. Haskell's type system
encodes _where_ mutation is allowed (only in `IO` monads), making
mutation explicit and controlled at the type level.

**Expert Thinking Cues:**

- When reviewing a class: which fields truly need to be mutable?
- When seeing a concurrency bug: is the root cause mutable shared state?
- When designing an API: can "updates" return new objects instead of mutating?

---

### ⚙️ How It Works (Mechanism)

**Java String immutability:**

```java
// String pool: same "hello" literal reused (safe because immutable)
String a = "hello";
String b = "hello";
assert a == b; // true (same pool object)

// Mutation creates new object
String c = a.toUpperCase(); // new String("HELLO")
assert a == "hello"; // original unchanged
```

**Persistent vector (Clojure-style, simplified):**

```
Original: [1,2,3,4,5]  root -> [node1][node2]
Update v[2]=99:        new_root -> [new_node1][node2]
                                  ^ shares node2 (unchanged)
```

**Rust default immutability:**

```rust
let x = 5; // immutable by default
x = 6; // compile error!
let mut y = 5; // explicitly opt into mutability
y = 6; // fine
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
value created: User{name="Alice", age=30}  ← YOU ARE HERE
  Thread A reads name: "Alice" -- safe
  Thread B reads age: 30 -- safe (simultaneous, no lock)
  Thread C: user.withAge(31)
    -> creates NEW User{name="Alice", age=31}
    -> original unchanged
    -> Thread A still sees age=30 in original reference
```

**FAILURE PATH:**

- Shallow immutability: `final List<String> list` — reference is final but contents mutable
- Python mutable default arguments: `def f(lst=[]):` — shared across calls
- Aliased mutation: two variables point to same mutable object; one mutates it

---

### ⚖️ Comparison Table

| Approach                  | Thread Safe    | Update Cost | Memory           | Example                  |
| ------------------------- | -------------- | ----------- | ---------------- | ------------------------ |
| Mutable object            | No             | O(1)        | No overhead      | Java bean, Python dict   |
| Immutable + copy-on-write | Yes            | O(n)        | O(n) per update  | Java record + copy       |
| Persistent data structure | Yes            | O(log n)    | Shared structure | Clojure PersistentVector |
| Rust ownership            | Compile-time   | O(1)        | Zero overhead    | Rust `mut` variables     |
| `final` field (Java)      | Reference safe | N/A         | None             | `final int x = 5`        |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                    |
| --------------------------------------- | ------------------------------------------------------------------------------------------ |
| "`final` in Java means immutable"       | `final` means the _reference_ can't change; the _object_ it points to may still be mutable |
| "Immutability doubles memory usage"     | Persistent data structures share structure; overhead is O(log n) not O(n)                  |
| "Immutability is only for FP languages" | Java records, Python `namedtuple`, C++ `const` are mainstream immutability                 |
| "Immutable objects are slow"            | They're often faster due to cache friendliness, free thread safety, and memoisation        |
| "Strings in C are immutable"            | C strings are `char[]` — mutable by default. Java/Python strings are immutable             |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Shallow Immutability Trap**
**Symptom:** `final List` modified by callee; caller sees unexpected changes.
**Root Cause:** `final` only immutabilises the reference, not the object.
**Fix:**

```java
// BAD: list contents still mutable
private final List<String> items = new ArrayList<>();

// GOOD: contents also immutable
private final List<String> items = List.of("a", "b", "c");
```

**Mode 2: Python Mutable Default Argument**
**Symptom:** Function accumulates state across calls unexpectedly.
**Root Cause:** Default argument is evaluated once at definition time.
**Fix:**

```python
# BAD: shared mutable default
def add(item, lst=[]):
    lst.append(item)
    return lst

# GOOD: None sentinel + local init
def add(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

**Mode 3: Aliased Mutation**
**Symptom:** Object changes without any obvious mutation in your code.
**Root Cause:** Two variables reference the same mutable object.
**Fix:** Use defensive copy or immutable types. `new ArrayList<>(original)` creates independent copy.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-004 - Functional Programming]]
- [[CSF-014 - Variables, Types, and Scope]]

**Builds On This (learn these next):**

- [[CSF-043 - Pure Functions and Side Effects]]
- [[CSF-052 - Concurrency Anti-Patterns (Shared State)]]

**Alternatives / Comparisons:**

- Mutable shared state with locks (synchronisation approach)
- Software transactional memory (CSF-064) — controlled mutation

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Values that cannot be changed after   │
│                 creation                             │
│ PROBLEM         Mutable shared state = concurrency    │
│ IT SOLVES       bugs + temporal coupling              │
│ KEY INSIGHT     Share immutable values freely:        │
│                 no locks, no surprises               │
│ USE WHEN        Data shared across threads; cached    │
│                 values; domain objects                │
│ AVOID WHEN      Counters, queues, accumulators        │
│                 (truly stateful constructs)           │
│ TRADE-OFF       Safety vs allocation cost             │
│                 (mitigated by structural sharing)     │
│ ONE-LINER       Values that never change can always   │
│                 be safely shared                     │
│ NEXT EXPLORE    CSF-043, CSF-052, CSF-064             │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Immutable values never change: share freely across threads, no locks required.
2. Java `final` immutabilises the _reference_, not the _object_ — the contents can still be mutated.
3. Persistent data structures make immutable updates cheap via structural sharing (O(log n) not O(n)).

**Interview one-liner:**
"Immutable values cannot be changed after creation; they can be shared across threads without synchronisation, eliminating data races and temporal coupling at the cost of new allocations on every update."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Default to immutability. Make mutability opt-in and explicit.
Every mutable field is a bet that the mutation will be correctly
synchronised across all callers for the lifetime of the program.
Most fields don't need to win that bet.

**Where else this pattern appears:**

- **Event sourcing** — events are immutable facts; state is derived by replaying them
- **Git commits** — each commit is immutable; history is a chain of immutable snapshots
- **HTTP caching** — immutable content (hashed URLs) can be cached indefinitely

---

### 💡 The Surprising Truth

The Java `String` class has been immutable since Java 1.0 — and
this is one reason the JVM can intern strings: the same `"hello"`
literal in multiple places can point to a single object in the
string pool. This small design choice saves millions of objects
in large applications. But `StringBuffer` (1.0) and `StringBuilder`
(1.5) exist precisely because immutable String made concatenation
in a loop O(n²). The lesson: immutability is the right default,
but some algorithms genuinely require mutation.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** React's state is supposed to be
immutable: you call `setState(newState)` instead of mutating
directly. But JavaScript objects are mutable. What actually
happens when a developer mutates state directly (`this.state.x = 5`),
and why does React break?

_Hint:_ Research how React's reconciliation/diffing uses reference
equality checks. What does `shouldComponentUpdate` and `PureComponent`
assume about state?

**Q2 (Scale):** Kafka treats messages as immutable, append-only
logs. What properties does this give Kafka that a traditional
mutable message queue (where messages are deleted on consumption)
doesn't have? What are the trade-offs?

_Hint:_ Consider consumer groups re-reading from offset 0, audit
trails, and the storage implications of never deleting messages.

**Q3 (Design Trade-off):** Clojure's `atom` allows mutable state
using compare-and-swap (CAS), while all other data structures are
immutable. Why is CAS on an atom safer than a mutable field in Java,
and what does this reveal about the right granularity for mutability?

_Hint:_ Research Clojure's atom semantics, `swap!`, and how CAS
is used. What invariant does the CAS operation preserve?
