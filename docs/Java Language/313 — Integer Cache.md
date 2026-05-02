---
layout: default
title: "Integer Cache"
parent: "Java Language"
nav_order: 313
permalink: /java-language/integer-cache/
number: "0313"
category: Java Language
difficulty: ★★★
depends_on:
  - Autoboxing / Unboxing
  - String Pool / String Interning
  - JVM
  - Heap Memory
used_by:
  - Generics
  - Stream API
related:
  - Autoboxing / Unboxing
  - String Pool / String Interning
  - Generics
tags:
  - java
  - jvm
  - memory
  - deep-dive
  - tradeoff
---

# 0313 — Integer Cache

⚡ TL;DR — Java caches `Integer` objects from -128 to 127; boxing the same small int always returns the same object — making `==` work by coincidence for cached values but fail silently for values outside that range.

| #0313 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Autoboxing / Unboxing, String Pool / String Interning, JVM, Heap Memory | |
| **Used by:** | Generics, Stream API | |
| **Related:** | Autoboxing / Unboxing, String Pool / String Interning, Generics | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Every autoboxing operation allocates a new Integer object on the heap. In a web service processing requests where IDs, quantities, and counts are frequently small values (0–100), boxing the same value `42` a thousand times per second creates 1,000 Integer(42) objects — all with identical content, all consuming heap space, all producing garbage. Small integers are ubiquitous in nearly every program: loop counters, boolean flags (0/1), small HTTP status groups, array indices.

THE BREAKING POINT:
A high-volume order processing system uses `Map<Integer, Order>` with order quantities (usually 1–10). At 100,000 orders/second, boxing these small quantities without caching = 100,000 heap allocations/second of Integer objects — all identical content, all garbage after the operation. The GC processes 4MB/second of Integer garbage alone, causing frequent minor GCs.

THE INVENTION MOMENT:
This is exactly why the **Integer Cache** was created — to pre-allocate and cache the most commonly-used Integer values so that boxing them requires no heap allocation, only a cache lookup.

---

### 📘 Textbook Definition

The **Integer Cache** is a JVM bootstrap optimization where 256 `Integer` instances (values -128 to 127 inclusive) are pre-allocated and stored in an internal array (`IntegerCache.cache[]`) during JVM startup. Calls to `Integer.valueOf(i)` for any `i` in the cached range return a reference to the pre-existing cached object rather than allocating a new one. This behavior is specified in the Java Language Specification (JLS §5.1.7): the boxing conversion of an `int` between -128 and 127 *must* produce the same `Integer` reference. The behavior is implementation-defined for values outside this range: different JVMs may cache different ranges, but HotSpot caches only -128 to 127 by default (with the upper bound configurable via `-XX:AutoBoxCacheMax=<value>`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The JVM pre-creates Integer objects for numbers -128 to 127 so boxing them is free and always returns the same object.

**One analogy:**
> Imagine a hotel that pre-stamps envelopes numbered 1–127 and keeps them in a drawer. When a guest asks for envelope #42, the clerk immediately hands one from the drawer (no printing, instant, same envelope every time). For envelope #200, the clerk must print a new one. If two guests each request envelope #42, they get the same physical envelope — but envelope #200 would give each a different new printout.

**One insight:**
The Integer Cache turns a potential bug (relying on `==` for boxed integer comparison) into an intermittent bug — the most dangerous kind. Code that uses `==` on Integers appears to work correctly for all small values (0–127), passing every test and every review. It breaks silently only when values exceed 127 — often in production with real IDs, amounts, or counts that tests never reach. This "mostly works" behavior makes the bug extremely hard to find.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Small integers are extremely common — caching them saves significant allocation for minimal memory cost.
2. Integer.valueOf() is the entry point for autoboxing — it's the right place to intercept and cache.
3. Cached integers must be identical objects for `==` to work reliably (a benefit for the cached range, a hazard for the uncached range).

DERIVED DESIGN:
The Integer Cache implementation:
```java
// java.lang.Integer (simplified):
private static class IntegerCache {
    static final int low = -128;
    static final int high; // = 127 by default, JVM-configurable
    static final Integer[] cache;

    static {
        int h = 127;
        String integerCacheHighPropValue =
            VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
        if (integerCacheHighPropValue != null) {
            h = Math.max(127, Integer.parseInt(integerCacheHighPropValue));
        }
        high = h;
        cache = new Integer[(high - low) + 1];
        int j = low;
        for (int k = 0; k < cache.length; k++)
            cache[k] = new Integer(j++);
        // cache[0] = Integer(-128)
        // cache[127] = Integer(-1)
        // cache[128] = Integer(0)
        // cache[255] = Integer(127)
    }
}

public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i <= IntegerCache.high)
        return IntegerCache.cache[i + (-IntegerCache.low)];
    return new Integer(i);
}
```

**Memory analysis:**
256 Integer objects × 16 bytes each = 4,096 bytes = 4KB total cache.
Array pointer overhead: 256 × 4 bytes = 1KB.
Total: ~5KB — negligible.
Direct savings: every boxing of values -128..127 saves one heap allocation.

```
┌────────────────────────────────────────────────┐
│         Integer Cache Layout                   │
│                                                │
│  IntegerCache.cache[]:                         │
│  [0] → Integer(-128)                          │
│  [1] → Integer(-127)                          │
│  ...                                           │
│  [127] → Integer(-1)                          │
│  [128] → Integer(0)                           │
│  ...                                           │
│  [255] → Integer(127)                         │
│                                                │
│  Integer.valueOf(42) → cache[42 + 128] = [170]│
│  → returns same object ALWAYS                  │
│                                                │
│  Integer.valueOf(200) → new Integer(200)        │
│  → different object EVERY time                 │
└────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Zero allocation for common small int boxing; consistent `==` behavior within cached range.
Cost: 4KB of JVM bootstrap overhead; `==` comparison behavior changes at the cache boundary (creates bug opportunity); developers must remember the range boundary.

---

### 🧪 Thought Experiment

SETUP:
Senior engineer reviews code. Method compares order IDs:
```java
public boolean isSameOrder(Order a, Order b) {
    return a.getId() == b.getId();  // IDs are Integer
}
```

IN TESTING (IDs 1–100):
`getId()` returns `Integer.valueOf(1)`, which is `cache[129]`. Same object. `==` returns `true` when IDs match. All 50 unit tests pass. Code review: "looks fine, tested."

IN PRODUCTION (IDs 10,000–10,999):
`getId()` returns `Integer.valueOf(10000)`. Beyond cache → new Integer. Two calls for the same ID (10000) produce two different Integer instances. `==` compares object identity: `false`, even when the IDs are numerically equal. Orders are incorrectly treated as non-matching. Business logic fails.

THE INSIGHT:
The test coverage that matters for this bug is **value coverage**, not **path coverage**. A unit test with ID=100 covers the same code paths as ID=10000 — but produces completely different runtime behavior due to the Integer Cache boundary. This is one case where mutation testing or property-based testing (`@IntRange(min=1, max=Integer.MAX_VALUE)`) would catch what traditional tests miss.

---

### 🧠 Mental Model / Analogy

> The Integer Cache is like a vending machine stocked only with coffee for amounts $0.01 to $1.27. For those common prices, the machine dispenses from pre-stocked supply (fast, same item). For prices over $1.28, it custom-prepares an item (slower, new each time). The critical rule: two customers buying the same pre-stocked item get the "same can" to inspect. Two customers buying a custom-prepared item get different cans. A cashier comparing "this can and that can" by physically checking if they're the same object (`==`) would be confused when $0.50 items are "identical cans" but $2.00 items aren't.

"Pre-stocked items" → cached Integer objects.
"Custom-prepared" → new Integer allocation.
"Same can" → same object reference (== works).
"Different cans" → different objects (== fails despite same content).
"Cashier comparing cans" → developer using == on Integer.

Where this analogy breaks down: The vending machine doesn't pretend the custom items are in stock — it's obvious. Integer Cache makes no visible distinction between cached and non-cached returns; both look like `Integer` to the caller.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Java pre-creates the most common small numbers (from -128 to 127) as objects. Using these numbers in operations that require objects instantly gets the pre-made version instead of creating a new one — much like keeping commonly-used tools within arm's reach rather than going to the storage room each time.

**Level 2 — How to use it (junior developer):**
Be aware of the boundary. Never use `==` to compare `Integer` objects. The cache is transparent — you don't enable or configure it. For performance-critical code, know that `Integer.valueOf(n)` for n in -128..127 has no allocation cost; for n outside this range, each boxing creates a new object.

**Level 3 — How it works (mid-level engineer):**
The cache is initialized in the static initializer of `Integer.IntegerCache` during JVM bootstrap. The JLS requires that boxing of values -128 to 127 return the same object across all boxing operations in that JVM instance. The upper bound (127) can be increased to any value via JVM flag `-XX:AutoBoxCacheMax=N` — though doing so costs N×16 bytes of pre-allocated heap and may change `==` behavior for values you now include. The same caching pattern applies to: `Byte` (full range: always cached), `Short` (-128..127), `Long` (-128..127), `Character` (0..127), `Boolean` (`true`/`false` always cached).

**Level 4 — Why it was designed this way (senior/staff):**
The JLS-mandated specification of the Integer Cache (§5.1.7) was a deliberate design choice to allow JVM implementations to cache more values for performance while specifying a minimum guarantee. The minimum (-128 to 127) reflects a frequency analysis of small integer usage in typical Java programs — values in this range appear in roughly 80% of boxing operations. The configurable upper bound (`java.lang.Integer.IntegerCache.high`) acknowledges that some applications use a finite set of small IDs and could benefit from pre-caching all of them. However, no application code should rely on the cache for correctness — only JVM performance. The fact that the JLS *mandates* same-object identity for this range (not just same value) is the source of the dangerous behavior: it makes `==` accidentally work for tests using small values while hiding the bug for production values.

---

### ⚙️ How It Works (Mechanism)

**JVM property configuration:**
```bash
# Configure maximum cached Integer value:
java -XX:AutoBoxCacheMax=1000 MyApp
# Sets java.lang.Integer.IntegerCache.high = 1000
# Caches Integer(-128) through Integer(1000)
# Memory: 1129 × 16 bytes ≈ 18KB

# Increasing this is rarely beneficial unless you have
# measured specific boxing overhead for a known finite range
```

**All numeric caches:**
```java
// Byte: ALL values (-128 to 127) are cached
Byte b1 = 127; Byte b2 = 127;
System.out.println(b1 == b2);  // always true

// Short: -128 to 127 cached
// Long: -128 to 127 cached
// Character: 0 to 127 cached ('A' through '\u007F')
// Boolean: both Boolean.TRUE and Boolean.FALSE are singletons
Boolean t1 = true; Boolean t2 = true;
System.out.println(t1 == t2);  // always true (singleton)

// Float, Double: NO CACHE
Float f1 = 1.0f; Float f2 = 1.0f;
System.out.println(f1 == f2);  // false! Never == for Float/Double
```

**JVM validation of cache at startup:**
```bash
# See JVM startup system properties including IntegerCache:
java -XX:+PrintFlagsFinal \
     -version 2>&1 | grep AutoBoxCacheMax
# Output: intx AutoBoxCacheMax = 127
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Source: Integer qty = orderQuantity]  // int → Integer
    → [Compiler: Integer qty = Integer.valueOf(orderQuantity)]
    → [Runtime: orderQuantity in -128..127?]
    → [YES: return IntegerCache.cache[orderQuantity + 128]]
    → [Same object returned EVERY time]
    → [qty references pre-existing cached object]
    → [Zero heap allocation]
```

FAILURE PATH:
```
[Source: Integer id1 = entity.getId()]  // value: 50000
    → [Integer.valueOf(50000) → new Integer(50000)]
[Source: Integer id2 = entity.getId()]  // same call
    → [Integer.valueOf(50000) → different new Integer(50000)]
[Comparison: id1 == id2]
    → [false! Different objects with same value]
    → [Bug: entity deduplication fails in production]
    → [Works in dev/test with ids 1–100 (cached)]
```

WHAT CHANGES AT SCALE:
At scale, the Integer Cache's most important effect is GC. A service boxing 10 million small integers per second (-128..127 range): 0 allocations. Same service boxing 10 million large integers per second (IDs 10K+): ~320MB/second of Integer garbage. The cache directly determines whether numeric boxing is GC-free or GC-intensive for a given workload's value range.

---

### 💻 Code Example

Example 1 — Demonstrating cache boundaries:
```java
// Prove the cache boundary:
for (int i = 125; i <= 130; i++) {
    Integer a = i;  // autoboxing
    Integer b = i;  // autoboxing
    System.out.printf(
        "i=%d: a==b → %b (same object: %b)%n",
        i, a == b,
        System.identityHashCode(a) == System.identityHashCode(b)
    );
}
// Output:
// i=125: a==b → true  (same object: true)
// i=126: a==b → true  (same object: true)
// i=127: a==b → true  (same object: true)
// i=128: a==b → false (same object: false)  ← boundary!
// i=129: a==b → false (same object: false)
// i=130: a==b → false (same object: false)
```

Example 2 — Dangerous pattern in production code:
```java
// DANGEROUS: Using == for Integer comparison
public class Order {
    private Integer quantity;
    // ...

    // BUG: Works for quantities 1–127, fails for 128+
    public boolean hasSameQuantity(Order other) {
        return this.quantity == other.quantity;  // WRONG!
    }

    // FIX: Always use equals()
    public boolean hasSameQuantity(Order other) {
        return Objects.equals(this.quantity, other.quantity);
    }
}
```

Example 3 — Making Integer == safe via interning (advanced):
```java
// If you intentionally want reference equality on integers:
// Intern them explicitly (within defined range)
Integer a = Integer.valueOf(200);  // not cached
Integer b = Integer.valueOf(200);  // different object
System.out.println(a == b);  // false

// Force to cache: use the cache range
// (moving your integer ID system to use < 128 values
// is usually not practical for real-world IDs)
// Better: just use .equals() everywhere
```

Example 4 — Using the extended cache for finite domains:
```bash
# Use case: application uses thread pool IDs (1-10), 
# HTTP status codes (100-599), or fixed database IDs (1-500)
# Configure cache to cover the entire domain:
java -XX:AutoBoxCacheMax=600 MyApp

# Now Integer.valueOf(500) == Integer.valueOf(500) is true
# Warning: increases JVM startup memory by ~600 × 16 bytes
# Only do this if Integer == comparison is relied upon
# AND the range is truly finite and controlled
```

---

### ⚖️ Comparison Table

| Value Range | Boxing Result | `==` Comparison | Memory Allocation |
|---|---|---|---|
| -128 to 127 | Cached object returned | `true` (same object) | 0 bytes (cache hit) |
| 128 to MAX_INT | New object created | `false` (different objects) | ~16 bytes per boxing |
| After `-XX:AutoBoxCacheMax=N` | Cached up to N | `true` up to N | Pre-allocated at startup |
| `Boolean` true/false | Singletons | Always `true` | 0 bytes |
| `Float`, `Double` | Always new | Always `false` | ~16 bytes per boxing |

How to choose: Never rely on Integer == for correctness. The cache is a performance optimization, not a correctness feature. Use .equals() for all Integer comparisons regardless of expected value range.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Integer == always fails | Integer == works for cached values (-128 to 127). The danger is relying on this — it creates intermittent bugs when values go outside the range |
| The Integer cache range is a language constant | Only the lower bound (-128) is fixed by the JLS. The upper bound is mandated to be AT LEAST 127 but can be higher. Different JVMs may cache different ranges |
| Increasing AutoBoxCacheMax solves the == problem | Increasing the cache range makes == work for a larger range, but the bug potential is still there for any value above the new limit. The correct fix is always using equals() |
| Float and Double behave like Integer (with a cache) | Float and Double have NO cache. `Float f = 1.0f; Float g = 1.0f; f == g` is ALWAYS false. This is important for floating-point boxing |
| The Integer cache applies to integer primitives | Integer cache only applies to boxing (Integer.valueOf()). Operations on `int` primitives use no cache concept — they're values, not objects |

---

### 🚨 Failure Modes & Diagnosis

**Production Integer == Bug (Cached Boundary)**

Symptom:
A feature works perfectly in all environments (dev, test, staging, QA) but fails intermittently in production. The failure correlates with specific record IDs or counts that exceed 127 or 127 whichever threshold is set.

Root Cause:
Test fixtures use small IDs (< 128). Production data has IDs > 127. Code uses `==` for Integer comparison. The bug is conceptually present everywhere but only triggers with uncached values.

Diagnostic Command / Tool:
```bash
# Find all Integer == usages in the codebase:
grep -rn "==" --include="*.java" . | grep "Integer\|int_"
# Or use SpotBugs rule: GS_GENERIC_IDENTITY
# Or IntelliJ: Inspect Code → "Suspicious use of == or != with integer" 
```

Fix:
Global search-and-replace of `integerVar == otherInt` with `integerVar.equals(otherInt)` or `Objects.equals(integerVar, otherInt)`.

Prevention:
SpotBugs `EQ_COMPARETO_USE_OBJECT_EQUALS` or Checkstyle rule. Property-based test using random values including those > 127.

---

**AutoBoxCacheMax Set Too High — Startup Memory Waste**

Symptom:
JVM startup is slower than expected. Heap used immediately after startup is unexpectedly high (hundreds of MB).

Root Cause:
Someone set `-XX:AutoBoxCacheMax=1000000` (1 million). The cache pre-allocates 1,000,128 Integer objects at ~16 bytes each = ~16MB of heap consumed just for the Integer cache. JVM startup time increases to initialize this cache.

Diagnostic Command / Tool:
```bash
# Check effective AutoBoxCacheMax:
java -XX:+PrintFlagsFinal -version 2>&1 | grep AutoBoxCacheMax
# And:
jcmd <pid> VM.flags | grep AutoBoxCacheMax
```

Fix:
Remove or reduce the AutoBoxCacheMax flag. Only set it if specific boxing-heavy code with a controlled integer domain genuinely benefits.

Prevention:
Document JVM flag changes. Prohibit production JVM flags that are not in the approved list without performance justification.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Autoboxing / Unboxing` — the Integer Cache is part of autoboxing behavior; autoboxing context is prerequisite
- `String Pool / String Interning` — same "cache identical values" pattern; understanding String Pool makes Integer Cache's design obvious by analogy

**Builds On This (learn these next):**
- `Generics` — generics with numeric types trigger autoboxing, and Integer Cache affects their behavior; understanding the cache helps tune generic numeric code

**Alternatives / Comparisons:**
- `String Pool / String Interning` — the String-type equivalent; same identity-equality pitfall for non-cached runtime values
- `Autoboxing / Unboxing` — the mechanism that uses the Integer Cache; the two are inseparable

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Pre-created Integer objects for -128..127 │
│              │ returned from Integer.valueOf() as singletons│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Small integer boxing (loop counters, IDs,  │
│ SOLVES       │ flags) would create high GC pressure       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ == "works" for cache range BUT "fails" for │
│              │ values > 127. This intermittent bug passes  │
│              │ all tests using small test IDs and only     │
│              │ fails in production with real IDs > 127    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automatic; tune AutoBoxCacheMax only for   │
│              │ controlled finite integer domains          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never rely on == for Integer; always use   │
│              │ .equals() regardless of expected range     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Allocation savings for small ints vs ==    │
│              │ confusion for values outside range         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cached vending machine for small numbers: │
│              │  same can ≤127, new can >127"              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Generics → Type Erasure → Bounded Wildcards│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two engineers debug an issue where a `HashMap<Integer, Customer>` lookup intermittently returns `null` on a key that was just inserted. They have confirmed the key value is correct. Trace exactly what sequence of events — considering autoboxing, Integer Cache, and `HashMap` key lookup — could cause this behavior specifically when the key values transition from being always ≤127 to sometimes >127 during a system load test, and identify the exact line in the source code most likely to contain the bug.

**Q2.** Java 21 introduces "primitive classes" (Project Valhalla, JEP 401) which are value types that can be used directly in generics without boxing. If `Integer` became a primitive class in Valhalla, the Integer Cache would become unnecessary. Explain why — specifically: what property of primitive classes eliminates the need for caching, how `==` comparison would change semantics for primitive Integer, and what would happen to code that currently relies on the Integer Cache for zero-allocation boxing of values -128 to 127.

