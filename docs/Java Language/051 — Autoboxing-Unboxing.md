---
layout: default
title: "Autoboxing / Unboxing"
parent: "Java Language"
nav_order: 51
permalink: /java-language/autoboxing-unboxing/
number: "051"
category: Java Language
difficulty: ★☆☆
depends_on: Primitive Types, Wrapper Classes
used_by: Collections, Generics, Streams
tags: #java #foundational #internals
---

# 051 — Autoboxing / Unboxing

`#java` `#foundational` `#internals`

⚡ TL;DR — Automatic conversion between primitive types (`int`) and their wrapper classes (`Integer`) — transparent but carries hidden performance costs.

| #051 | Category: Java Language | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Primitive Types, Wrapper Classes | |
| **Used by:** | Collections, Generics, Streams | |

---

### 📘 Textbook Definition

**Autoboxing** is the automatic conversion of a primitive type to its corresponding wrapper class (`int` → `Integer`, `double` → `Double`, etc.) when required by the context (e.g., adding to a collection). **Unboxing** is the reverse: automatic extraction of the primitive value from a wrapper object. Both are performed by the Java compiler, which inserts the necessary conversion calls transparently.

---

### 🟢 Simple Definition (Easy)

Java can automatically wrap an `int` into an `Integer` (autoboxing) and unwrap an `Integer` back into an `int` (unboxing) — so you can put primitives into collections without manual conversion.

---

### 🔵 Simple Definition (Elaborated)

Since generic collections like `List<Integer>` cannot hold primitives directly (generics are erased to `Object`), Java transparently calls `Integer.valueOf(42)` when you write `list.add(42)`. The convenience is real, but the cost is real too: each autoboxing creates a heap object, which means GC pressure and potential `NullPointerException` when unboxing a null wrapper.

---

### 🔩 First Principles Explanation

**The core problem:**
Java has both primitives (`int`, `double`) for performance and object wrappers (`Integer`, `Double`) for use with generics and collections. Manually converting between them is verbose.

**The compiler insert:**
```java
// What you write:
List<Integer> list = new ArrayList<>();
list.add(42);          // autoboxing
int val = list.get(0); // unboxing

// What the compiler generates:
list.add(Integer.valueOf(42));       // autoboxing
int val = list.get(0).intValue();   // unboxing
```

---

### 🧠 Mental Model / Analogy

> Autoboxing is like an automatic coin wrapper at a bank. You pour in loose coins (primitives), the machine wraps them into rolls (wrapper objects). Unboxing is opening the roll to get the coins back. The bank (JVM) handles the wrapping automatically — but every wrap/unwrap takes a small amount of time.

---

### ⚙️ How It Works (Mechanism)

```
Autoboxing: primitive → wrapper
  int    → Integer    (Integer.valueOf(int))
  long   → Long       (Long.valueOf(long))
  double → Double     (Double.valueOf(double))
  char   → Character  (Character.valueOf(char))
  boolean→ Boolean    (Boolean.valueOf(boolean))

Unboxing: wrapper → primitive
  Integer → int    (intValue())
  Double  → double (doubleValue())
  etc.

Integer Cache (important!):
  Integer.valueOf(-128 to 127) → cached, same object
  Integer.valueOf(128+)        → new object each time
```

---

### 💻 Code Example

```java
// Autoboxing in action
List<Integer> scores = new ArrayList<>();
scores.add(95);   // autoboxing: 95 → Integer.valueOf(95)
scores.add(87);

// Unboxing in action
int first = scores.get(0);  // unboxing: Integer.intValue()

// NullPointerException trap
Integer nullable = null;
int value = nullable;  // NullPointerException! unboxing null

// Performance trap — autoboxing in tight loop
Long sum = 0L;  // Long (not long) — autoboxes on every iteration!
for (long i = 0; i < 1_000_000; i++) {
    sum += i;  // creates 1,000,000 Long objects → GC pressure
}

// Fix: use primitive
long sumFast = 0L;  // primitive long — no boxing
for (long i = 0; i < 1_000_000; i++) {
    sumFast += i;  // no allocation, no GC
}

// == comparison trap
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true (cached range)

Integer x = 128;
Integer y = 128;
System.out.println(x == y);  // false (different objects!)
System.out.println(x.equals(y)); // true (use equals for values)
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Autoboxing is free | Each box creates a heap allocation → GC pressure |
| `Integer a == Integer b` compares values | `==` compares references; use `.equals()` for value equality |
| Autoboxing never causes NPE | Unboxing a `null` wrapper throws `NullPointerException` |
| The integer cache covers all values | Only -128 to 127 is cached; values outside create new objects |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Autoboxing in hot loop**
Using `Long` (wrapper) instead of `long` (primitive) in a loop that runs millions of times.
Fix: always use primitives in performance-critical paths; use `OptionalLong`, `LongStream` where needed.

**Pitfall 2: NPE from unboxing**
Method returns `Integer` (can be null); caller uses as `int` directly.
Fix: null-check before unboxing; use `Objects.requireNonNullElse()` or `Optional`.

**Pitfall 3: Identity comparison on cached integers**
`if (a == b)` where a, b are `Integer` objects — works for small values (cache), silently broken for large.
Fix: always use `.equals()` for `Integer`, `Long`, `Double` comparisons.

---

### 🔗 Related Keywords

- **Integer Cache** — the JVM caches Integer values -128 to 127 to avoid repeated allocation
- **Generics** — require wrapper types, making autoboxing necessary for collections
- **Primitive Types** — the non-object types that autoboxing wraps
- **NullPointerException** — the risk when unboxing a null wrapper reference

---

### 📌 Quick Reference Card


```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Automatic int↔Integer conversion — convenient │
│              │ but has allocation cost and NPE risk          │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Working with collections/generics that        │
│              │ require wrapper types                         │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Hot loops; performance-critical code — use    │
│              │ primitive arrays or primitive streams          │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Convenient conversion between int and Integer│
│              │  — transparent but not free"                  │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Integer Cache --> Generics --> Type Erasure    │
└─────────────────────────────────────────────────────────────┘
```
### 🧠 Think About This Before We Continue

**Q1.** Why does unboxing a null `Integer` cause a `NullPointerException`?
**Q2.** Why does `Integer a = 127; Integer b = 127; a == b` return `true` but not for 128?
**Q3.** How would you detect autoboxing overhead in production code?

