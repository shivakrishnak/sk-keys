---
layout: default
title: "Integer Cache"
parent: "Java Language"
nav_order: 313
permalink: /java-language/integer-cache/
number: "313"
category: Java Language
difficulty: ★★★
depends_on: "Autoboxing / Unboxing, String Pool, Heap Memory"
used_by: "Integer comparison, autoboxing behavior, JVM performance tuning"
tags: #java, #jvm, #cache, #integers, #wrappers, #autoboxing
---

# 313 — Integer Cache

`#java` `#jvm` `#cache` `#integers` `#wrappers` `#autoboxing`

⚡ TL;DR — JVM caches `Integer` objects for -128..127; within this range `Integer.valueOf(42) == Integer.valueOf(42)` is `true` (same instance). Outside: `false`. Always use `.equals()`.

| #313            | Category: Java Language                                         | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Autoboxing / Unboxing, String Pool, Heap Memory                 |                 |
| **Used by:**    | Integer comparison, autoboxing behavior, JVM performance tuning |                 |

---

### 📘 Textbook Definition

The **Integer Cache** is an optimization in `java.lang.Integer.valueOf(int i)`: the JVM pre-allocates and caches `Integer` objects for values in the range -128 to 127 (inclusive). Calls to `Integer.valueOf(i)` within this range return the same cached instance; calls outside this range allocate a new `Integer` heap object. Analogous caches exist for `Byte` (-128..127, all values), `Short` (-128..127), `Long` (-128..127), `Boolean` (TRUE and FALSE), and `Character` (0..127). The upper bound of the `Integer` cache is configurable via `-XX:AutoBoxCacheMax=<N>` (JVM flag); the lower bound is always -128. This behavior affects autoboxing and identity comparisons (`==`).

---

### 🟢 Simple Definition (Easy)

The JVM pre-creates 256 `Integer` objects (from -128 to 127) at startup and reuses them. `Integer a = 127; Integer b = 127; a == b → true` — same cached object. `Integer a = 128; Integer b = 128; a == b → false` — two separate new objects created. This is why you must always use `.equals()` for `Integer` comparison: `==` only works reliably within the cache range.

---

### 🔵 Simple Definition (Elaborated)

Why -128 to 127? These are the values representable in one signed byte — common small numbers used in everyday programming (counters, status codes, loop bounds). The JVM designers chose to cache them to avoid repeated allocation. The tricky part: the cache is invisible. `Integer a = 127; Integer b = 127; a == b` looks wrong (comparing objects with `==`) but happens to be `true` because both variables reference the same cached object. `Integer a = 128; Integer b = 128; a == b` looks identical but returns `false`. This inconsistency is a classic Java interview question and a real source of subtle bugs.

---

### 🔩 First Principles Explanation

**Integer Cache implementation and all wrapper caches:**

```
INTEGER CACHE IMPLEMENTATION (JDK source, java.lang.Integer):

  private static class IntegerCache {
      static final int low = -128;
      static final int high;
      static final Integer cache[];

      static {
          // Upper bound: 127 by default; configurable via JVM flag:
          int h = 127;
          String integerCacheHighPropValue =
              VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
          if (integerCacheHighPropValue != null) {
              int i = parseInt(integerCacheHighPropValue);
              i = Math.max(i, 127);         // minimum 127
              h = Math.min(i, Integer.MAX_VALUE - (-low) - 1);
          }
          high = h;

          cache = new Integer[(high - low) + 1];
          int j = low;
          for (int k = 0; k < cache.length; k++)
              cache[k] = new Integer(j++);
          // cache[-128] = new Integer(-128)
          // cache[-127] = new Integer(-127)
          // ...
          // cache[127]  = new Integer(127)
      }
  }

  public static Integer valueOf(int i) {
      if (i >= IntegerCache.low && i <= IntegerCache.high)
          return IntegerCache.cache[i + (-IntegerCache.low)];  // O(1) array lookup
      return new Integer(i);  // heap allocation
  }

CACHE RANGE BY TYPE:

  Type        | Cache Range        | Notes
  ──────────────────────────────────────────────────────
  Byte        | -128 .. 127        | All possible byte values; always cached
  Short       | -128 .. 127        | Subset of Short range
  Integer     | -128 .. 127        | Configurable upper bound
  Long        | -128 .. 127        | Not configurable
  Boolean     | false, true        | Only two instances exist
  Character   | '\u0000'..'\u007F' | (0..127): ASCII chars

IDENTITY COMPARISON BEHAVIOR:

  Integer a = 127;   Integer b = 127;    a == b → TRUE  (cache hit)
  Integer a = 128;   Integer b = 128;    a == b → FALSE (cache miss)
  Integer a = -128;  Integer b = -128;   a == b → TRUE  (cache boundary)
  Integer a = -129;  Integer b = -129;   a == b → FALSE (below cache)

  new Integer(127) == new Integer(127) → FALSE (constructor bypasses cache)
  Integer.valueOf(127) == Integer.valueOf(127) → TRUE

CONFIGURING THE UPPER BOUND:

  JVM flag:  -XX:AutoBoxCacheMax=1000
  Maps to:   java.lang.Integer.IntegerCache.high=1000

  Effect:    Integer.valueOf(500) == Integer.valueOf(500) → TRUE
  Risk:      code that "works" with default cache (≤127) may break if cache extended;
             code that relies on == failing above 127 will malfunction if cache extended.

  RECOMMENDATION: Never rely on Integer == behavior. Always .equals().

LONG CACHE: non-configurable, always -128..127:
  Long a = 127L;  Long b = 127L;  a == b → TRUE
  Long a = 128L;  Long b = 128L;  a == b → FALSE
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Integer Cache:

- `Integer.valueOf(1)` called millions of times: millions of heap allocations for the same small values
- GC pressure from short-lived Integer objects for common values (0, 1, -1, loop counters)

WITH Integer Cache:
→ Pre-allocated array; `valueOf()` returns cached instances for common values — zero allocation, zero GC overhead for the most frequently used integer values.

---

### 🧠 Mental Model / Analogy

> A hotel with permanent rooms reserved for the most frequent guests (-128 to 127). When a VIP frequent guest (value ≤127) checks in: they get their pre-reserved permanent room (same room, every visit). When a new guest (value >127) checks in: they get a freshly made room (new object, new allocation). Two VIPs with the same reservation number check in: same room → `==` works. Two new guests both requesting room 200: two different rooms → `==` fails, `.equals()` checks if they have the same preferences (same content).

"Pre-reserved permanent room" = cached `Integer` instance in `IntegerCache.cache[]`
"Same room, every visit" = `Integer.valueOf(50) == Integer.valueOf(50)` → true
"New guest: freshly made room" = `new Integer(500)` → distinct heap object
"Two new guests, room 200" = `Integer a = 500, b = 500; a == b → false`
"Same preferences (content)" = `.equals()` compares numeric value regardless of identity

---

### ⚙️ How It Works (Mechanism)

```
INTEGER CACHE LOOKUP (array-indexed, O(1)):

  Integer.valueOf(50):
  50 >= -128 && 50 <= 127 → cache hit
  return cache[50 - (-128)] = cache[178]  ← pre-allocated Integer(50)

  Integer.valueOf(200):
  200 > 127 → cache miss
  return new Integer(200)  ← heap allocation

  Memory:
  IntegerCache.cache: Integer[-128], Integer[-127], ..., Integer[127]
                       (256 objects, allocated at class loading time)
  Each Integer: ~16 bytes → total cache: ~4KB (negligible)
```

---

### 🔄 How It Connects (Mini-Map)

```
Autoboxing calls Integer.valueOf(int)
        │
        ▼
Integer Cache ◄──── (you are here)
(-128..127 cached; outside range: new heap object; affects == comparison)
        │
        ├── Autoboxing / Unboxing: cache affects == behavior on autoboxed Integer
        ├── String Pool: analogous caching for String literals
        └── Boolean: TRUE/FALSE are singleton instances (always ==)
```

---

### 💻 Code Example

```java
// CACHE RANGE DEMO:
Integer a = 127, b = 127;
System.out.println(a == b);      // true  (cached)
System.out.println(a.equals(b)); // true

Integer c = 128, d = 128;
System.out.println(c == d);      // false (uncached — different heap objects)
System.out.println(c.equals(d)); // true  (content equal)

// AUTOBOXING INTERACTS WITH CACHE:
int x = 50;
Integer p = x;  // autoboxing → Integer.valueOf(50) → cached instance
Integer q = x;  // autoboxing → Integer.valueOf(50) → SAME cached instance
System.out.println(p == q); // true (both from cache)

// CONSTRUCTOR BYPASSES CACHE:
Integer e = new Integer(127);   // deprecated Java 9+, removed Java 17+
Integer f = new Integer(127);
System.out.println(e == f); // false (constructor always creates new object)

// CORRECT APPROACH: always .equals():
Integer score1 = getScore();  // may return any value
Integer score2 = getScore();
if (score1.equals(score2)) { ... }  // safe for any value

// OTHER WRAPPER CACHES:
Boolean t1 = true, t2 = true;
System.out.println(t1 == t2); // true (Boolean.TRUE singleton)

Character ch1 = 'A', ch2 = 'A';
System.out.println(ch1 == ch2); // true ('A' = 65, within 0..127 cache)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                         |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Integer Cache is a JVM global singleton shared across classloaders | Each classloader has its own `IntegerCache`. In multi-classloader environments (OSGi, app servers), `Integer.valueOf(50)` from two different classloaders → two different objects → `==` fails even within cache range.         |
| `-XX:AutoBoxCacheMax` applies to all wrapper types                 | Only `Integer` has a configurable upper bound. `Long`, `Short`, `Byte`, `Character` have fixed cache ranges and are not configurable.                                                                                           |
| Avoiding `new Integer(x)` is only about deprecation                | `new Integer(x)` is deprecated (Java 9) and removed (Java 17) because it bypasses the cache, allocates unnecessarily, and signals intent to compare with `==` (which will always fail). Use `Integer.valueOf(x)` or autoboxing. |

---

### 🔥 Pitfalls in Production

**Subtle `==` comparison bug that passes unit tests but fails in production:**

```java
// ANTI-PATTERN: production code uses == on Integer return values:
public class OrderProcessor {
    public Integer getOrderStatus(String orderId) {
        return statusMap.getOrDefault(orderId, 0);  // returns 0 for unknown
    }
}

// CALLER:
Integer status = processor.getOrderStatus("ORD-001");
if (status == 0) {  // works in tests: 0 is cached, == true
    handleUnknown();
}

// PROBLEM: works for status 0..127 (cached).
// If status codes change to include 200 (HTTP-style):
// status == 200 → ALWAYS false (200 > 127, new heap object each call)
// Bug: handleSuccess never called even when status is SUCCESS=200.

// FIX: always .equals() or unbox to primitive:
if (status.equals(0)) { ... }     // correct: content comparison
if (status == 0) { ... }          // BAD: relies on cache range
int statusPrimitive = status;     // unbox → compare as primitive int
if (statusPrimitive == 200) { ... } // safe: primitive == is always value comparison
```

---

### 🔗 Related Keywords

- `Autoboxing / Unboxing` — Integer Cache is used by `Integer.valueOf()` called during autoboxing
- `String Pool` — analogous JVM-level caching for String literals
- `Heap Memory` — cache misses (values > 127) allocate on the heap
- `Boolean` — `Boolean.TRUE` and `Boolean.FALSE` are always singletons
- `Flyweight Pattern` — Integer Cache is a classic Flyweight Pattern implementation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ JVM pre-caches Integer -128..127.        │
│              │ Same instance for cached values.         │
│              │ Outside range: new heap object.          │
├──────────────┼───────────────────────────────────────────┤
│ CACHE RANGES │ Byte: all values │ Integer: -128..127+   │
│              │ Long: -128..127  │ Boolean: TRUE/FALSE   │
│              │ Character: 0..127│                       │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ NEVER use == to compare Integer objects. │
│              │ Always use .equals() or unbox to int.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hotel pre-reserved rooms -128..127:     │
│              │  same guest → same room. Room 200:       │
│              │  freshly made, different each time."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Autoboxing → String Pool →               │
│              │ Flyweight Pattern → Boolean.TRUE          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Integer Cache is initialized in a static initializer block (`IntegerCache.static{}`). When does this initialization happen — at JVM startup, or lazily on first `Integer.valueOf()` call? What happens if two threads call `Integer.valueOf()` simultaneously for the first time (class loading thread-safety)?

**Q2.** The `-XX:AutoBoxCacheMax=N` flag extends the Integer Cache upper bound. If you extend it to 10,000 in a web application that parses user-submitted integer IDs, what is the memory implication? And can an attacker exploit this to cause a memory exhaustion? (Think about how many distinct Integer objects would be cached if your user IDs range from 1 to 1,000,000.)
