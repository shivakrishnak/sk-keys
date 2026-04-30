---
layout: default
title: "Integer Cache"
parent: "Java Language"
nav_order: 52
permalink: /java-language/integer-cache/
---
# 052 — Integer Cache

`#java` `#internals` `#intermediate` `#jvm`

⚡ TL;DR — The JVM caches `Integer` objects for values -128 to 127; `Integer.valueOf()` returns the same cached instance for these values, making `==` work — but only in this range.

| #052 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Autoboxing, Integer.valueOf | |
| **Used by:** | Autoboxing, String Pool, Performance Analysis | |

---

### 📘 Textbook Definition

The Integer Cache is a JVM optimization where `Integer.valueOf(int)` returns cached `Integer` instances for values in the range -128 to 127 (inclusive). For values in this range, repeated calls return the same object reference. For values outside this range, a new `Integer` object is created each time. The upper bound of the cache can be extended via the JVM flag `-XX:AutoBoxCacheMax=<size>`.

---

### 🟢 Simple Definition (Easy)

Java pre-creates and reuses `Integer` objects for small numbers (-128 to 127). So `Integer.valueOf(100)` always returns the **same object** — but `Integer.valueOf(200)` creates a **new object** every time.

---

### 🔵 Simple Definition (Elaborated)

This optimization exists because small integers are extremely common in programs (loop counters, flags, indices). By caching them, autoboxing small values becomes nearly free (no allocation). But this creates a subtle trap: `==` comparison works for cached values (same object) and silently fails for values outside the cache (different objects with same value).

---

### 🔩 First Principles Explanation

**The code behind it (`Integer.java` source):**
```java
public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i <= IntegerCache.high)
        return IntegerCache.cache[i + (-IntegerCache.low)];
    return new Integer(i);
}
```

**The cache is initialized at JVM startup:**
```java
// Integer.IntegerCache static initializer
// Populates cache[-128] through cache[127]
// Default high = 127, configurable via -XX:AutoBoxCacheMax
```

---

### 🧠 Mental Model / Analogy

> The Integer cache is like a post office that pre-stamps the most common envelope sizes (small numbers). If you need a #10 envelope (value under 127), they hand you one from the shelf — same physical envelope every time. If you need a custom size (128+), they make a new one on the spot. Two people asking for a #10 get the identical envelope; two people asking for custom size get different envelopes that look the same.

---

### ⚙️ How It Works (Mechanism)

```
Integer cache in JVM memory:

  JVM startup → IntegerCache.cache[] allocated
  cache[0]   → Integer(-128)
  cache[1]   → Integer(-127)
  ...
  cache[255] → Integer(127)

  Integer.valueOf(100):
    100 is in [-128, 127] → return cache[100 + 128] = cache[228]
    Same object reference every time ✓

  Integer.valueOf(128):
    128 > 127 → return new Integer(128)
    New object each call ✗ (different references)

Extend cache (at JVM startup):
  java -XX:AutoBoxCacheMax=1000 MyApp
  → Caches -128 to 1000
```

---

### 💻 Code Example

```java
// Cache range: identity comparison works
Integer a = 127;
Integer b = 127;
System.out.println(a == b);      // true  (same cached object)
System.out.println(a.equals(b)); // true

// Outside cache: identity comparison breaks
Integer x = 128;
Integer y = 128;
System.out.println(x == y);      // false (different new objects!)
System.out.println(x.equals(y)); // true  (equals uses value)

// The autoboxing connection
Integer i1 = 100;   // → Integer.valueOf(100) → cached
Integer i2 = 100;   // → Integer.valueOf(100) → same cached object
System.out.println(i1 == i2);  // true

// Same applies to: Byte, Short, Long, Character
Long l1 = 100L;
Long l2 = 100L;
System.out.println(l1 == l2);  // true  (Long has same -128 to 127 cache)

Long l3 = 200L;
Long l4 = 200L;
System.out.println(l3 == l4);  // false

// Interview classic trap
public static void main(String[] args) {
    Integer a = 1000;
    Integer b = 1000;
    if (a == b) {
        System.out.println("equal");    // NOT printed
    } else {
        System.out.println("not equal"); // printed
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Integer cache works for all values | Only -128 to 127 (configurable upper bound only) |
| Only Integer has a cache | Byte, Short, Long (-128 to 127), Character (0 to 127) also cached |
| Autoboxing always creates new objects | For cached range, autoboxing returns cached instance |
| Extending cache is always beneficial | Large cache = larger JVM startup memory; benefit depends on workload |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using == on Integer in business logic**
`if (order.getStatus() == OrderStatus.ACTIVE)` where status is `Integer` — works in test (small values), breaks in prod with large IDs.
Fix: use `.equals()` for all wrapper comparisons; never `==`.

**Pitfall 2: Relying on cache behavior in tests**
Tests pass with small values (cached, same reference); production fails with large values (new objects).
Fix: use `.equals()` everywhere; never depend on `==` for correctness.

---

### 🔗 Related Keywords

- **Autoboxing** — calls `Integer.valueOf()` which uses the cache
- **String Pool** — analogous concept for String literals
- **== vs equals()** — core issue the cache creates/masks
- **JVM Flags** — `-XX:AutoBoxCacheMax` extends the cache upper bound

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Integer.valueOf() caches -128 to 127;        │
│              │ == works in this range only                   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Understanding autoboxing performance;        │
│              │ debugging == comparison bugs                  │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Never rely on cache for correctness;         │
│              │ always use .equals() for value comparison     │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Small integers are shared objects; large ones│
│              │  are not — never use == on Integer"           │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Autoboxing --> String Pool --> == vs equals() │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** Why does `Integer.valueOf(100) == Integer.valueOf(100)` return `true` but `new Integer(100) == new Integer(100)` return `false`?
**Q2.** Besides Integer, which other wrapper types have a similar cache?
**Q3.** When would extending the Integer cache with `-XX:AutoBoxCacheMax` be beneficial?

