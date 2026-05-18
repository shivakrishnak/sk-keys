---
id: CSF-030
title: Immutability
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-024, CSF-016
used_by: CSF-048, JCC-010, DBF-003
related: CSF-028, CSF-058, JLG-005, JCC-001
tags: [immutability, final, records, value-objects, thread-safety]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/csf/immutability/
---

⚡ TL;DR - An immutable object cannot change state after
creation. Java immutables: Strings, primitives, `final` fields,
records (Java 14+), and `List.of()`. Immutable objects are
thread-safe by definition and eliminate defensive copy overhead.

| #030 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-024 (Functional Programming), CSF-016 (Encapsulation) | |
| **Used by:** | CSF-048 (Concurrency Anti-Patterns), JCC-010 (Thread Safety) | |
| **Related:** | CSF-028 (Side Effects), CSF-058 (Referential Transparency), JCC-001 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Mutable objects can be changed by anyone holding a reference.
When a `Customer` object is passed to `EmailService.send(customer)`,
can the caller guarantee that `send()` does not modify
`customer`? Can two threads pass the same `customer` to
two different services simultaneously without a race condition?
With mutable objects, the answer is: only if you trust
every method that receives the object, and only if every
access is synchronized. At scale, this trust breaks down.

**THE BREAKING POINT:**

In concurrent systems (web servers, async processing),
mutable shared state creates race conditions. The canonical
example: a `User` object is fetched from the DB and cached.
If the cache returns the SAME mutable object to every
caller, two concurrent requests may simultaneously mutate
it (e.g., updating `lastLogin` and `loyaltyPoints`), producing
corrupted state. The fix for mutable shared state: either
synchronize every access (complex, error-prone, performance
cost) or make the object immutable (free).

**THE INVENTION MOMENT:**

Immutability as a design principle is inherent to mathematics
(numbers do not change; operations produce new numbers).
In programming, LISP and Haskell formalized it: all data
is immutable by default; "modification" creates a new value.
Java made `String` immutable from version 1.0 (1996) -
a conscious decision for thread-safety and security (a
`String` passed to a security check cannot be mutated
after the check). Java 14+ `record` types (finalized
in Java 16) made value-object immutability idiomatic.

---

### 📘 Textbook Definition

An immutable object is one whose state cannot change after
it is created. All fields are set in the constructor and
cannot be modified thereafter. Immutability in Java is
achieved through: (1) declaring all fields `final`;
(2) not providing setter methods; (3) ensuring mutable
objects in fields are never shared (defensive copies
of arrays, lists); (4) not allowing subclassing (declare
class `final` or use a private constructor + factory).
Java records (Java 16+) provide syntactic sugar for
immutable value types: `record Point(int x, int y) {}`
generates an immutable class with `final` fields, canonical
constructor, `equals`, `hashCode`, and `toString`. The
key property of immutable objects: they are inherently
thread-safe - there is no state to corrupt because there
is no mutation. Immutable objects can be freely shared
across threads without synchronization.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Immutable objects cannot change after creation - they are
safe to share across threads and caches without defensive
copying or synchronization.

**One analogy:**

> A dollar bill is immutable. You cannot change its serial
> number, denomination, or face. If you want "one dollar
> more," you get a NEW dollar bill. Multiple people can
> hold copies of the same dollar bill's number and never
> interfere with each other because neither can modify it.
>
> A mutable "dollar bill" would allow anyone holding it
> to change its denomination. Sharing it between two people
> would require a lock ("only one person can access it
> at a time"), defensive copies ("I'll give you a copy
> so we each have our own"), or trust that neither will
> modify it. None of these scale.

**One insight:**

`String` in Java is immutable. That is why `String.substring()`,
`String.toUpperCase()`, and `String.trim()` return NEW
strings instead of modifying the existing one. That is
also why `String` is safe to use as a key in `HashMap`
(its `hashCode()` never changes). If `String` were mutable,
you could insert a string as a key, mutate it, and the
key would be "lost" in the map because the bucket position
was computed from the old `hashCode`. Immutability makes
`String` a reliable, safe, shareable value - and this
was a deliberate design decision in Java 1.0.

---

### 🔩 First Principles Explanation

**WHAT MAKES AN OBJECT TRULY IMMUTABLE:**

```
┌─────────────────────────────────────────────────────┐
│     Immutability Checklist (all required)           │
├─────────────────────────────────────────────────────┤
│ 1. All fields are FINAL (assigned once in ctor)     │
│ 2. No setter methods                                │
│ 3. No methods that modify fields                    │
│ 4. Class is FINAL (or uses private ctor) to         │
│    prevent mutable subclasses                       │
│ 5. Mutable field types (arrays, List, etc.) are     │
│    defensively copied in the constructor and never  │
│    exposed as mutable references                    │
└─────────────────────────────────────────────────────┘
```

**DEEP IMMUTABILITY vs SHALLOW:**

```java
// SHALLOW IMMUTABILITY (broken - final reference to mutable content)
final class Order {
    private final List<Item> items; // final reference
    Order(List<Item> items) {
        this.items = items; // stores the CALLER's list!
    }
    List<Item> getItems() { return items; } // exposes mutable ref!
}
// Caller can: order.getItems().add(newItem); // MUTATES THE ORDER!
// Also: the constructor's List<Item> argument could be modified
// externally after construction!

// DEEP IMMUTABILITY (correct)
final class Order {
    private final List<Item> items;
    Order(List<Item> items) {
        // Defensive copy in constructor:
        this.items = List.copyOf(items); // immutable copy
    }
    List<Item> getItems() {
        return items; // safe: items is already unmodifiable
    }
}
```

**THE TRADE-OFFS:**

**Gain:** Thread-safety for free (no synchronization needed).
No defensive copies needed at USE sites (only at construction).
Safe as HashMap keys (hashCode is stable).
Simple reasoning (object state is fixed at construction).
No temporal coupling (cannot be "half-initialized").

**Cost:** Every "modification" creates a new object.
For hot paths with frequent small modifications (e.g., building
a string character by character), this is memory-intensive.
Mitigation: use mutable builders for construction (`StringBuilder`
builds a mutable string; `toString()` returns an immutable one).

---

### 🧪 Thought Experiment

**SETUP:**

A currency amount in a financial system. Team A makes
it mutable; Team B makes it immutable.

```java
// Team A: Mutable Money (dangerous)
class Money {
    BigDecimal amount;
    String currency;
    void add(Money other) { this.amount = this.amount.add(other.amount); }
}

Money balance = new Money(100, "USD");
Money tax = new Money(10, "USD");
balance.add(tax); // balance is now 110
// Problem: 'tax' reference can be shared;
// tax.add(something) changes 'tax' everywhere it is used.
// Two threads calling balance.add() concurrently = race condition.

// Team B: Immutable Money (safe)
record Money(BigDecimal amount, String currency) {
    Money add(Money other) {
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
Money balance = new Money(new BigDecimal("100"), "USD");
Money tax = new Money(new BigDecimal("10"), "USD");
Money total = balance.add(tax); // balance unchanged; total is new
// Both 'balance' and 'total' exist simultaneously.
// Neither can be corrupted by concurrent access.
```

**THE LESSON:**

Immutable `Money` enables: (1) sharing the same object
across threads with zero synchronization, (2) using it
as a `HashMap` key safely, (3) passing it to any method
without defensive copying, (4) holding references to
both "before" and "after" values simultaneously.
The cost: one more object on the heap per "modification."
For a financial system processing 1000 transactions/second,
this is trivial overhead.

---

### 🎯 Mental Model / Analogy

**THE PHOTOGRAPH ANALOGY:**

A mutable object is a whiteboard - anyone can walk up
and erase or rewrite it. To safely share what is written,
you must either: stand guard (synchronization), give
each person a photocopy (defensive copy), or trust everyone
not to change it (faith-based).

An immutable object is a photograph of the whiteboard.
The photo cannot be changed. You can give the same photo
to 100 people simultaneously and no one's copy is affected
by others. If you want a "different" whiteboard, you take
a new photo of a modified version. The original photo
always shows what was on the whiteboard at the moment
it was taken.

**MEMORY HOOK:**

"Immutable = photograph. Mutable = whiteboard.
Photographs are safe to share. Whiteboards need guards.
Java records = automatic photograph factory."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
An immutable object cannot be changed after creation.
Like a printed book - you cannot change the words once
it is printed. If you want a different version, you print
a new book.

**Level 2 - Student:**
`String` is immutable in Java. `str.toUpperCase()` returns
a NEW string; it does not change `str`. Immutable objects
are safe to use from multiple threads simultaneously because
no one can change them. `final` fields help but are not
sufficient for full immutability.

**Level 3 - Professional:**
Full immutability requires: `final` class, `final` fields,
defensive copies of mutable parameters, no exposed mutable
references. Java 16+ `record` provides all of this
automatically (except for fields with mutable types -
you must still defensively copy those). `Collections.
unmodifiableList()` wraps a mutable list to prevent external
modification (but the underlying list can still be mutated
by the original holder). `List.of()` and `List.copyOf()`
create truly unmodifiable, null-rejecting lists.
`BigDecimal`, `Integer`, `Long`, `LocalDate`, `LocalDateTime`,
`UUID` - all immutable in the JDK.

**Level 4 - Senior Engineer:**
Immutable value objects in Domain-Driven Design (DDD):
`Money`, `Address`, `PhoneNumber`, `DateRange` are value
objects - identified by their values, not their identity.
They MUST be immutable: two `Money(100, "USD")` objects
are equal and interchangeable; there is no notion of
"the same Money object being modified." `records` in Java
are ideal DDD value objects: automatic `equals`/`hashCode`
based on field values, canonical constructor, compact
notation. Persistent data structures (Vavr, Clojure):
immutable `HashMap`, `List`, `Vector` that share structure
between "before" and "after" versions (structural sharing).
An append to an immutable Vavr `List` is O(1): it creates
a new node pointing to the old list; the old list is unchanged.

**Level 5 - Expert:**
Immutability and the JMM (Java Memory Model): correctly
constructed immutable objects are visible to all threads
WITHOUT synchronization - the JMM guarantees that `final`
fields written in the constructor are visible to all readers
after the constructor completes, as long as `this` does not
escape the constructor. This is the "safe publication"
guarantee. If `this` escapes before the constructor completes
(e.g., registering `this` with a listener inside the constructor),
the `final` fields may not yet be visible to other threads.
Project Valhalla (Java future): "primitive objects" or
value types - immutable objects that can be flattened into
arrays and stack frames without heap allocation, providing
the immutability semantics of records with the performance
of primitives. A `record Money(long cents)` may eventually
be a value type: copied by value, zero heap allocation,
cache-line-friendly when stored in arrays.

---

### ⚙️ How It Works (Formal Basis)

**JAVA MEMORY MODEL AND FINAL FIELDS:**

The JMM provides a special guarantee for `final` fields:
all writes to `final` fields in a constructor complete
before any thread sees the reference to the constructed
object. This means: if an immutable object is CORRECTLY
published (not via a data race on the reference variable),
all threads will see the correct, fully initialized values
of all `final` fields - without synchronization.

```java
// Safe publication: the immutable object reference
// is published via a volatile field or a synchronized block.
class Registry {
    volatile Config config; // volatile ensures visibility

    void updateConfig(Map<String, String> props) {
        // Create new immutable Config (fully initialized before publish)
        Config newConfig = new Config(props); // Config is immutable
        this.config = newConfig; // atomic write (volatile) - safe publish
    }
}
// Any thread reading this.config sees a fully initialized Config.
// No locking required because Config is immutable.
```

**`List.of()` vs `Collections.unmodifiableList()`:**

```
┌───────────────────────────────────────────────────────┐
│ List.of(1,2,3)                                        │
│   - Truly unmodifiable (no underlying mutable list)   │
│   - null elements: throw NullPointerException         │
│   - No defensive copy needed - IS the final data      │
│                                                       │
│ Collections.unmodifiableList(mutableList)             │
│   - A VIEW over the mutable list                      │
│   - The original mutableList CAN still be modified!   │
│   - Modifications to original are visible through view│
│   - null elements: allowed (from original list)       │
│                                                       │
│ List.copyOf(mutableList)                              │
│   - Creates an immutable copy of the input list       │
│   - Original list changes NOT reflected in copy       │
│   - null elements: throw NullPointerException         │
└───────────────────────────────────────────────────────┘
```

---

### 🔄 System Design Implications

**IMMUTABILITY IN CACHING:**

Immutable objects are ideal cache values. A mutable object
in a cache requires either synchronization on every read
(defeating the cache's purpose) or a defensive copy on
every return (O(n) per read). An immutable cached object:
return the reference directly, no synchronization, no copy.

**WHAT CHANGES AT SCALE:**

At 10x object creation: creating immutable objects per
transformation (e.g., processing a stream of 1M events)
generates significant GC pressure. Mitigation: use mutable
builders in the hot path (`StringBuilder`, `Map.Builder`)
and build the final immutable object only at the end.

At 100x cache size: immutable objects are cache-friendly.
The same object can be stored in multiple caches simultaneously.
A mutable object in multiple caches can diverge if one
cache "updates" its copy. Immutable objects guarantee
cache coherence by design.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Broken Immutability**

```java
// BAD: Final reference to mutable content - false immutability
final class Order {
    private final List<Item> items;
    // BUG 1: stores caller's list - caller can mutate it
    Order(List<Item> items) { this.items = items; }
    // BUG 2: returns mutable reference - caller can add items
    List<Item> getItems() { return items; }
}

Order order = new Order(mutableItems);
mutableItems.add(newItem); // silently mutates 'order'!
order.getItems().remove(0); // silently mutates 'order'!

// GOOD: Fully immutable Order
final class Order {
    private final List<Item> items;
    Order(List<Item> items) {
        // Defensive copy using List.copyOf (immutable, null-safe)
        this.items = List.copyOf(items);
    }
    List<Item> getItems() {
        return items; // safe: already unmodifiable
    }
    // "Modification" returns a new Order with the item added
    Order withItem(Item item) {
        List<Item> newItems = new ArrayList<>(this.items);
        newItems.add(item);
        return new Order(newItems); // new immutable Order
    }
}
```

**Example 2 - Java Record as Immutable Value Object**

```java
// Record: immutable value type, Java 16+
// Generates: final class, final fields, canonical ctor,
// equals/hashCode (by value), toString.
record Money(BigDecimal amount, String currency) {
    // Compact constructor for validation:
    Money {
        Objects.requireNonNull(amount, "amount required");
        Objects.requireNonNull(currency, "currency required");
        if (amount.compareTo(BigDecimal.ZERO) < 0)
            throw new IllegalArgumentException("amount negative");
    }

    Money add(Money other) {
        if (!this.currency.equals(other.currency))
            throw new CurrencyMismatchException(currency, other.currency);
        return new Money(this.amount.add(other.amount), currency);
    }
}

// Usage: value equality, not identity
Money price = new Money(new BigDecimal("29.99"), "USD");
Money tax   = new Money(new BigDecimal("2.40"),  "USD");
Money total = price.add(tax);
// price and tax unchanged; total is new.
assertEquals(price.add(tax), total); // equals by value!
```

**Testing/Verification:**

```java
@Test
void immutableOrderNotAffectedByExternalListMutation() {
    List<Item> mutableList = new ArrayList<>();
    mutableList.add(new Item("Widget"));

    Order order = new Order(mutableList);
    assertEquals(1, order.getItems().size());

    mutableList.add(new Item("Gadget")); // mutate after construction

    // Immutable Order is not affected:
    assertEquals(1, order.getItems().size());
}

@Test
void withItemReturnsNewOrderLeavingOriginalUnchanged() {
    Order original = new Order(List.of(new Item("Widget")));
    Order augmented = original.withItem(new Item("Gadget"));

    assertEquals(1, original.getItems().size()); // unchanged
    assertEquals(2, augmented.getItems().size()); // new Order
}
```

---

### ⚖️ Comparison Table

| Approach | Thread-Safe? | Defensive Copy at Use? | Null-Safe? | Java API |
|---|---|---|---|---|
| Mutable object (no sync) | No | Yes, always | N/A | POJO with setters |
| Mutable object (synchronized) | Yes | No (lock protects) | N/A | `synchronized` blocks |
| `Collections.unmodifiableList(list)` | Partial (view only; underlying mutable) | No | No | `java.util.Collections` |
| `List.of(a, b, c)` | Yes | No | Yes (no nulls) | Java 9+ |
| `List.copyOf(list)` | Yes | No (copy is immutable) | Yes (no nulls) | Java 10+ |
| Java `record` | Yes (for `final` primitive/immutable fields) | Depends on field types | No (unless enforced in compact ctor) | Java 16+ |
| Fully immutable class (manual) | Yes | No | If enforced in ctor | Manually implemented |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `final` field = immutable object | `final` means the reference cannot be reassigned. If the field type is a mutable object (`List`, `Date`, `byte[]`), the CONTENT is still mutable. `private final List<Item> items` prevents reassignment of `items` but NOT `items.add(x)`. Full immutability requires defensive copies and unmodifiable wrappers. |
| `Collections.unmodifiableList()` creates an immutable list | It creates an unmodifiable VIEW. The underlying list is still mutable. If the original list (held by the list's creator) is modified, the "unmodifiable" view reflects the change. For true immutability: `List.of()` (new list) or `List.copyOf()` (copy of existing). |
| Java records are always fully immutable | Records have `final` fields, but if a field type is mutable (e.g., `record Order(List<Item> items)`), the items can still be mutated via `order.items().add(x)`. A defensive copy in the compact constructor is required for true immutability of mutable field types. |
| Immutable objects are always slower than mutable ones | For read-heavy, sharing-heavy patterns (caches, DTOs, value objects), immutable objects are faster: no synchronization overhead, no defensive copy at read sites. The cost is at write sites (new object per "modification"). Profile the actual use pattern before assuming performance direction. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Defensive Copy Missing - Silent Mutation**

**Symptom:** A service returns an order from its cache.
A caller adds an item to the returned list. Subsequent
callers see the extra item (the cached order has been
silently mutated).

**Root Cause:** The cached `Order` object returned a
reference to its internal mutable list without a defensive copy.

```java
// BAD: Internal mutable list exposed
class OrderCache {
    Map<String, Order> cache;
    // Order.getItems() returns mutable List<Item>
    // Caller mutates: orderCache.get(id).getItems().add(item)
    // - corrupts the cached Order!
}

// GOOD: Return unmodifiable view or copy
// In Order:
List<Item> getItems() {
    return Collections.unmodifiableList(items);
    // or: return List.copyOf(items); (null-safe, truly unmodifiable)
}
// Any caller attempt to add: throws UnsupportedOperationException
// immediately - fails fast and visibly.
```

---

**Security Note:**

Immutability is a security feature. The Java security
architecture depends on `String` being immutable: when
a file path is validated and then passed to the OS for
file opening, the path cannot be changed between validation
and use ("time-of-check to time-of-use" TOCTOU attack
requires mutation). An immutable `String` validated path
cannot be mutated after the check. Similarly, `final`
fields in security-sensitive classes (class loaders,
permission objects) cannot be changed after construction
even if the object is somehow obtained by malicious code.
Always prefer immutable types for security-critical data:
paths, tokens, credentials in transit (in-memory).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Functional Programming` (CSF-024) - immutability
  is the foundation of FP; the paradigm that makes
  immutability a design goal
- `Encapsulation` (CSF-016) - immutability is the
  strictest form of encapsulation: no part of an object's
  state can be modified after creation

**Builds On This (learn these next):**
- `Concurrency Anti-Patterns` (CSF-048) - shared mutable
  state (the absence of immutability) is the root cause
  of concurrency bugs
- `Java Thread Safety` (JCC-001) - immutable objects
  are thread-safe by definition; the entry details the
  formal JMM guarantees

**Alternatives / Comparisons:**
- `Side Effects` (CSF-028) - mutation (the opposite of
  immutability) is the primary category of side effect
- `Referential Transparency` (CSF-058) - enabled by
  immutability: expressions over immutable values can
  always be replaced by their evaluated result

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ DEFINITION   │ Object cannot change state after        │
│              │ construction. All fields set in ctor.   │
├──────────────┼─────────────────────────────────────────┤
│ CHECKLIST    │ final class, final fields, no setters,  │
│              │ defensive copy of mutable inputs,       │
│              │ no exposed mutable references           │
├──────────────┼─────────────────────────────────────────┤
│ JAVA TOOLS   │ record (Java 16+): automatic immutable  │
│              │ List.of(): immutable list, no nulls     │
│              │ List.copyOf(): immutable copy of list   │
├──────────────┼─────────────────────────────────────────┤
│ THREAD SAFE  │ Immutable = thread-safe by definition   │
│              │ No synchronization needed for reads     │
│              │ JMM final field guarantee: safe publish │
├──────────────┼─────────────────────────────────────────┤
│ PITFALL      │ final List = reference final, NOT content│
│              │ Must use List.copyOf() for deep immutability│
├──────────────┼─────────────────────────────────────────┤
│ DDD USE      │ Value objects: Money, Address, DateRange │
│              │ Java record = ideal DDD value object    │
├──────────────┼─────────────────────────────────────────┤
│ ONE-LINER    │ "Immutable = no state change after ctor.│
│              │ Thread-safe for free. Use records for   │
│              │ value objects. List.of() not .unmodifiable│
│              │ for truly immutable collections."       │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ JCC-001 (Thread Safety), CSF-028 (Side Effects)│
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. True immutability requires: `final` class, `final` fields,
   NO setters, defensive copies of mutable inputs (`List.copyOf`),
   and no exposed mutable references.
2. `final` on a reference field does NOT make the referenced
   object immutable. `private final List<Item> items` still
   allows `items.add(x)`. Use `List.copyOf()` for true
   list immutability.
3. Immutable objects are thread-safe by definition. The JMM
   guarantees `final` field visibility after correct publication.
   No `synchronized` or `volatile` needed to safely share
   correctly constructed immutable objects.

**Interview one-liner:**
"An immutable object cannot change state after creation.
Requirements: final class, final fields, no setters, defensive
copies of mutable inputs. Java records provide this automatically.
Immutable objects are thread-safe by definition (JMM final
field guarantee), making them ideal for shared caches, value
objects, and concurrent domain models without locking."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Immutability eliminates an entire class of bugs by making
the problematic pattern (mutation of shared state) impossible.
The engineering insight: the cost of immutability (creating
new objects per "modification") is paid at write time;
the benefit (no synchronization, no defensive copies,
no state corruption bugs) is reaped at every read.
In most systems, reads vastly outnumber writes. Immutability
optimizes for the common case.

**Where else this pattern appears:**

- **HTTP response objects** - HTTP responses are immutable:
  once sent, they cannot be modified. The immutability
  is enforced by the protocol. `HttpServletResponse` in
  Java Servlet API is mutable (you can set headers before
  flushing), but once committed (`response.flushBuffer()`),
  it becomes effectively immutable. Framework designers
  enforce immutability at commit to prevent header-modification-after-write bugs.
- **Git commits** - a Git commit hash is a content-addressed
  SHA-1 of the commit content. The commit is immutable:
  the hash identifies the exact content. "Changing" a
  commit (amend) creates a NEW commit with a new hash.
  The original commit still exists in the reflog. This
  is immutability applied to version control: history is
  append-only and unchangeable.
- **Event logs in event sourcing** - events in an event-
  sourced system are immutable. Once an event is appended
  to the log, it is never modified. To "undo" an action,
  you append a compensating event. The immutability of
  the event log is what makes the system auditable,
  replayable, and temporally queryable.

---

### 💡 The Surprising Truth

Java's `String` immutability was controversial when Java
was designed (1995). In C, strings are mutable character
arrays. Many early Java developers asked: "Why can't
I change a character in a String? This wastes memory!"
The designers' answer: immutable strings enable string
interning (the JVM maintains a pool of string literals;
all references to `"hello"` share the same object because
it cannot change), are secure (a path validated before
being passed to the OS cannot be mutated to point to a
different path), and are thread-safe (no synchronization
needed). Twenty-five years later, this decision looks
prophetic: `String` is the most-used type in Java programs,
used as HashMap keys (works correctly because hashCode
is stable), passed across thread boundaries (safe because
immutable), and stored in caches (safe because content
never changes). The "wasted memory" from immutability
is dwarfed by the bugs that NEVER occur because of it.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IMPLEMENT]** Create a fully immutable `Address`
   class with fields for street, city, state, and zip.
   Demonstrate that: (a) a caller cannot mutate the
   object after construction, (b) two `Address` objects
   with the same values are `equals()`, (c) the object
   can be safely used as a `HashMap` key.

2. **[CONVERT]** Take a mutable `UserProfile` class with
   setters and convert it to an immutable `record`.
   Handle the case where one field is a `List<Tag>`:
   ensure the record's `tags()` method returns an
   unmodifiable view.

3. **[DISTINGUISH]** Given three implementations of
   an "immutable" list field: (a) `final List<Item> items`,
   (b) `Collections.unmodifiableList(items)`, (c) `List.
   copyOf(items)` - demonstrate which are truly immutable,
   which fail for which operations, and when each is appropriate.

4. **[THREAD-SAFE]** Explain why this code is safe without
   `synchronized`: `final class Config { private final
   Map<String,String> props; Config(Map<String,String> p)
   { this.props = Map.copyOf(p); } String get(String k)
   { return props.get(k); } }`. Reference the JMM `final`
   field guarantee in your explanation.

5. **[DDD APPLY]** Model a `Money` value object using
   a Java `record` with a compact constructor that validates
   non-null currency and non-negative amount. Implement
   `add(Money)`, `multiply(BigDecimal)`, and `negate()`
   methods that each return new `Money` objects.

---

### 🧠 Think About This Before We Continue

**Q1.** A developer creates an immutable `User` record
with a `List<Role> roles` field. They use `List.of(roles)`
in the compact constructor. A colleague points out that
`Role` objects are mutable (they have a `setName()` method).
Is the `User` record truly immutable? What guarantees
does it provide and what does it NOT guarantee?

*Hint: The `User` record is shallow-immutable: the `roles`
list itself cannot be modified (it is `List.of()`). But
the individual `Role` objects in the list ARE mutable.
Anyone with a reference to a `Role` in the list can call
`role.setName("HackedRole")`. The `User` record prevents
adding/removing roles from the list but not mutating
the Role objects. True deep immutability requires that
Role itself be immutable (also a record or a correctly
designed immutable class). This is called the distinction
between "shallow" and "deep" immutability.*

**Q2.** The JMM guarantees that `final` fields are safely
visible to all threads after a correctly constructed
immutable object is published. What does "correctly
published" mean, and what publication mechanisms are NOT
safe?

*Hint: Safe publication: publishing via a volatile field,
a `java.util.concurrent` lock, a thread-safe collection,
static initializer, or `final` field. Unsafe publication:
publishing via a non-volatile, non-synchronized field
(plain field assignment visible to other threads). The
JMM's guarantee: if the reference to an immutable object
is safely published (via a volatile write or similar),
all readers see the complete, final-field-initialized
object. If published via a plain (non-volatile) field,
another thread might see the reference before the final
fields are written, observing partial initialization.*

---

### 🎯 Interview Deep-Dive

**Q1: "Why is String immutable in Java? What would break
if it were mutable?"**

*Why they ask:* Classic Java design question that tests
understanding of memory model, security, and collection design.

*Strong answer includes:*
- String pool / interning: the JVM interns string literals
  in a pool. Multiple references to `"hello"` share one
  object. If `String` were mutable, one caller modifying
  `"hello"` would affect all other references to the
  same pooled string.
- HashMap keys: `String` is the most common `HashMap`
  key. The map stores the key's `hashCode` (bucket position).
  A mutable `String` key could be modified after insertion,
  changing its `hashCode`, making the entry "lost" (stored
  in the old bucket, not findable in the new bucket).
- Security: path strings passed to security checks cannot
  be mutated between the check and use (prevents TOCTOU attacks).
- Thread safety: immutable strings can be shared across
  threads without synchronization - critical for a type
  used everywhere in concurrent Java code.

**Q2: "What is the difference between `List.of()`,
`List.copyOf()`, and `Collections.unmodifiableList()`?"**

*Why they ask:* Common API confusion. Tests understanding
of the semantic difference between "view" and "copy."

*Strong answer includes:*
- `List.of(a, b, c)`: creates a new unmodifiable list
  from the given elements. Not a copy of an existing list.
  No null elements. Throws on add/remove/set.
- `List.copyOf(existingList)`: creates an unmodifiable
  copy of an existing list. If the original changes, the
  copy does NOT reflect the change (it is a copy, not a view).
  No null elements.
- `Collections.unmodifiableList(mutableList)`: creates
  an unmodifiable VIEW over the original mutable list.
  If the original changes, the view DOES reflect the change.
  Allows null elements. Modification attempts on the view
  throw `UnsupportedOperationException`.
- Practical advice: for truly immutable lists, prefer
  `List.of()` or `List.copyOf()`. Use `unmodifiableList`
  only when you need a "read-only window" into a mutable list.

**Q3: "How do Java records relate to immutability, and
when would you NOT use a record?"**

*Why they ask:* Tests knowledge of Java 16+ features and
their design intent.

*Strong answer includes:*
- Record provides: all fields `final`, canonical constructor,
  `equals`/`hashCode` by component values, `toString`,
  no-setters. Ideal for DTOs, value objects, event types,
  configuration snapshots.
- Limitations: (1) cannot extend a class (can implement
  interfaces), (2) all fields are `final` - cannot be
  used for entities that require identity-based `equals`
  (e.g., JPA entities need `@Id`-based identity, not
  field-value equality), (3) mutable field types (arrays,
  `List`) still require defensive copies in the compact
  constructor, (4) serialization: records are `Serializable`
  but need care with `serialVersionUID` if used as API
  contracts.
- When NOT to use: JPA/Hibernate entities (need mutable
  proxy support), objects with complex lifecycle (stateful
  beans), or when inheritance is required.
- When to prefer: DTOs, event payloads, immutable domain
  value objects (Money, Address, DateRange), API response
  models, `Optional`-alternative containers.

> Entry stub. Generate full content using Master Prompt v4.0.
