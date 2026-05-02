---
layout: default
title: "Autoboxing / Unboxing"
parent: "Java Language"
nav_order: 312
permalink: /java-language/autoboxing-unboxing/
number: "312"
category: Java Language
difficulty: ★★☆
depends_on: "Primitives, Integer Cache, Heap Memory"
used_by: "Collections, Stream API, generics, arithmetic with wrapper types"
tags: #java, #primitives, #wrappers, #performance, #nullpointerexception
---

# 312 — Autoboxing / Unboxing

`#java` `#primitives` `#wrappers` `#performance` `#nullpointerexception`

⚡ TL;DR — **Autoboxing** is automatic `int → Integer` conversion; **unboxing** is `Integer → int`. Convenient but hides heap allocations and NPE traps when the wrapper is `null`.

| #312 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Primitives, Integer Cache, Heap Memory | |
| **Used by:** | Collections, Stream API, generics, arithmetic with wrapper types | |

---

### 📘 Textbook Definition

**Autoboxing** (Java 5+): the automatic conversion performed by the compiler when a primitive value (e.g., `int`) is used in a context that requires its wrapper class (`Integer`). The compiler inserts a call to `Integer.valueOf(int)`. **Unboxing**: the reverse — automatic conversion from a wrapper object to a primitive by the compiler inserting a call to `intValue()`. Key detail: `Integer.valueOf(int)` uses the Integer Cache for values -128..127 (returning a cached instance); outside that range it allocates a new `Integer` on the heap. Unboxing a `null` reference throws `NullPointerException`.

---

### 🟢 Simple Definition (Easy)

Java has two worlds: primitive `int` (stack, fast, 4 bytes) and wrapper `Integer` (heap object, slower, needed for collections). Autoboxing: Java automatically wraps `int` into `Integer` when needed (e.g., adding to a `List<Integer>`). Unboxing: automatically unwraps `Integer` back to `int` when arithmetic is needed. The convenience is real — but behind it: heap allocations, GC pressure, and the risk of NPE when unboxing `null`.

---

### 🔵 Simple Definition (Elaborated)

Before Java 5: `List<Integer> list = new ArrayList<>(); list.add(Integer.valueOf(42));` — manual. Java 5+: `list.add(42);` — compiler inserts `Integer.valueOf(42)` for you. Unboxing: `int x = list.get(0);` — compiler inserts `.intValue()`. The danger: if `list.get(0)` returns `null` (nulled-out entry), the `.intValue()` call throws `NullPointerException` — no obvious `null` dereference visible in your code. Performance: `list.add(42)` in a loop of 10 million iterations: 10 million `Integer` allocations on the heap, GC pressure, cache misses — vs. a primitive array: zero allocations.

---

### 🔩 First Principles Explanation

**Compiler desugaring and Integer Cache interaction:**

```
AUTOBOXING DESUGARING:

  Source:              Compiler generates:
  Integer i = 42;  →  Integer i = Integer.valueOf(42);
  
  Integer.valueOf(int i):
  if (i >= -128 && i <= 127) {
      return IntegerCache.cache[i + 128];  // cached instance
  }
  return new Integer(i);  // new heap allocation
  
UNBOXING DESUGARING:

  Source:              Compiler generates:
  int j = i;       →  int j = i.intValue();
  
  NullPointerException trap:
  Integer i = null;
  int j = i;       →  int j = i.intValue();  // NPE: i is null!

AUTOBOXING IN COLLECTIONS:

  List<Integer> list = new ArrayList<>();
  for (int k = 0; k < 1_000_000; k++) {
      list.add(k);  // 1,000,000 Integer.valueOf(k) calls
                    // k < 128: returns cached instances
                    // k >= 128: new Integer(k) → heap allocation
  }
  // Each Integer: 16 bytes (object header 12 + int 4)
  // Total: ~15MB heap for the Integer objects + ArrayList backing array
  // Primitive int[]: 4MB (4 bytes × 1M)
  // Avoid: use int[] or IntStream when performance matters

COMPARISON TRAP:

  Integer a = 1000;
  Integer b = 1000;
  System.out.println(a == b);  // false! (both outside -128..127, different heap objects)
  System.out.println(a.equals(b)); // true (content comparison)
  
  Integer a = 100;
  Integer b = 100;
  System.out.println(a == b);  // true (both from Integer Cache: same instance)
  
  → ALWAYS use .equals() for Integer comparison (see Integer Cache #313)

NULL UNBOXING NPE (COMMON BUG):

  Map<String, Integer> scores = new HashMap<>();
  scores.put("alice", null);  // intentional null
  
  int aliceScore = scores.get("alice");  // NPE! unboxes null Integer → intValue() on null
  
  // FIX 1: null check:
  Integer val = scores.get("alice");
  int aliceScore = (val != null) ? val : 0;
  
  // FIX 2: Map.getOrDefault:
  int aliceScore = scores.getOrDefault("alice", 0);
  
  // FIX 3: Optional:
  int aliceScore = Optional.ofNullable(scores.get("alice")).orElse(0);

PERFORMANCE-SENSITIVE CODE:

  // BAD: autoboxing in tight loop
  Long sum = 0L;  // Long wrapper
  for (int i = 0; i < 1_000_000; i++) {
      sum += i;  // unbox sum (longValue()) + i, then rebox result → 1M Long allocations
  }
  
  // GOOD: primitive
  long sum = 0L;
  for (int i = 0; i < 1_000_000; i++) {
      sum += i;  // pure primitive arithmetic: zero allocations
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Autoboxing:
- Java generics work only with reference types (due to type erasure → Object)
- `List<int>` is impossible; must use `List<Integer>` with manual boxing/unboxing
- Verbose: `list.add(Integer.valueOf(42));`, `int x = list.get(0).intValue();`

WITH Autoboxing:
→ `list.add(42);`, `int x = list.get(0);` — readable, ergonomic. Generics usable with numeric types without verbose boilerplate.

---

### 🧠 Mental Model / Analogy

> A money exchange counter at an airport. Primitive `int`: your local currency (fast, in your wallet). Wrapper `Integer`: foreign currency in an envelope (needs to be processed, slower, takes up more space). Autoboxing: handing the cashier your local cash, which they automatically seal in an envelope (boxing). Unboxing: opening the envelope to take the cash out. If the cashier gives you an empty envelope (null Integer) and you try to open it for cash → "Empty envelope: nothing inside" (NullPointerException). The convenience of auto-exchange hides the cost of each envelope.

"Local currency (fast, wallet)" = primitive `int` (stack, zero-allocation)
"Foreign currency in envelope" = `Integer` (heap object, needs boxing/unboxing)
"Cashier seals in envelope" = compiler inserts `Integer.valueOf(int)`
"Opening envelope" = compiler inserts `.intValue()`
"Empty envelope" = `null` Integer reference
"NPE on empty envelope" = `NullPointerException` on unboxing null

---

### ⚙️ How It Works (Mechanism)

```
JAVAP DISASSEMBLY — autoboxing/unboxing visible:

  Source:
  public void demo() {
      Integer x = 42;      // autoboxing
      int y = x;           // unboxing
  }
  
  Bytecode (javap -c):
  public void demo();
    Code:
       0: bipush        42
       2: invokestatic  Integer.valueOf(int)  ← autoboxing: compiler inserts
       5: astore_1
       6: aload_1
       7: invokevirtual Integer.intValue()    ← unboxing: compiler inserts
      10: istore_2
      11: return
```

---

### 🔄 How It Connects (Mini-Map)

```
Primitive int vs. Object reference in Java
        │
        ▼
Autoboxing / Unboxing ◄──── (you are here)
(int ↔ Integer; compiler-generated valueOf() / intValue(); heap impact)
        │
        ├── Integer Cache (#313): valueOf() returns cached instances for -128..127
        ├── String Pool (#311): similar caching pattern for String literals
        ├── Collections: require Object types → autoboxing enables numeric collections
        └── Stream API: IntStream avoids autoboxing for primitive int streams
```

---

### 💻 Code Example

```java
// AUTOBOXING CONVENIENCE:
List<Integer> scores = new ArrayList<>();
scores.add(95);   // autoboxing: Integer.valueOf(95)
scores.add(100);  // autoboxing: Integer.valueOf(100) — cached instance!

// UNBOXING IN ARITHMETIC:
int total = 0;
for (Integer score : scores) {
    total += score;  // unboxing: score.intValue()
}

// NPE TRAP — null unboxing:
Map<String, Integer> map = new HashMap<>();
map.put("x", null);
int val = map.get("x");  // NullPointerException — never visible from source

// COMPARISON TRAP:
Integer a = 500, b = 500;
System.out.println(a == b);     // false (> 127, different heap objects)
System.out.println(a.equals(b)); // true

// PERFORMANCE: prefer primitives in hot paths:
// Bad (1M Integer allocations):
Long sum = 0L;
for (int i = 0; i < 1_000_000; i++) sum += i;

// Good (zero allocations):
long sum = 0L;
for (int i = 0; i < 1_000_000; i++) sum += i;

// STREAMS: use primitive streams to avoid boxing:
int sumPrimitive = IntStream.rangeClosed(1, 1_000_000).sum();  // no boxing
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Autoboxing/unboxing has no performance cost | Each boxing creates a heap allocation (for values outside -128..127). In tight loops, this causes GC pressure. Benchmark: `Long sum = 0L; for(...) sum += i` is measurably slower than `long sum = 0L`. |
| `Integer a = 100; Integer b = 100; a == b` is always true | Only for values in the Integer Cache range (-128..127). The cache range for `Integer` can be extended with `-XX:AutoBoxCacheMax`, but relying on this is fragile. Always use `.equals()`. |
| Unboxing is safe if the list was populated with real integers | A `List<Integer>` can hold `null` (unlike `int[]`). If any entry is null and you iterate with `for (int x : list)`, you'll get NPE on the null entry. |

---

### 🔥 Pitfalls in Production

**NullPointerException from unboxing null in return types:**

```java
// ANTI-PATTERN — service returns Integer (nullable), caller unboxes:
public Integer getTimeoutMs(String service) {
    return configMap.get(service);  // may return null if not configured
}

// CALLER:
int timeout = getTimeoutMs("payment-service");  // NPE if not configured!

// FIX 1: return primitive with documented default:
public int getTimeoutMs(String service) {
    Integer val = configMap.get(service);
    return val != null ? val : DEFAULT_TIMEOUT_MS;
}

// FIX 2: return Optional<Integer>:
public Optional<Integer> getTimeoutMs(String service) {
    return Optional.ofNullable(configMap.get(service));
}
// Caller:
int timeout = getTimeoutMs("payment-service").orElse(DEFAULT_TIMEOUT_MS);
```

---

### 🔗 Related Keywords

- `Integer Cache` — `Integer.valueOf()` caches -128..127; affects autoboxing behavior
- `String Pool` — analogous JVM-level caching for String literals
- `Stream API` — `IntStream`/`LongStream`/`DoubleStream` avoid autoboxing for numeric pipelines
- `Heap Memory` — each autoboxed value outside cache range allocates on the heap
- `Generics` — the reason boxing exists: Java generics require Object, not primitives

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Compiler auto-converts int↔Integer.      │
│              │ Hides heap allocations + NPE traps.      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Collections, generics, Stream API — all  │
│              │ require Object types; autoboxing bridges │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Hot loops; never autobox in tight inner  │
│              │ loops; use IntStream / int[] instead     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Currency exchange: auto-seals primitive │
│              │  in object envelope. Empty envelope →   │
│              │  NPE when opened."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Integer Cache → String Pool →             │
│              │ Generics → IntStream → Heap Memory       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The JVM's `Integer.valueOf()` caches -128..127 by default. This means autoboxing `42` always returns the same `Integer` instance — a subtle invariant relied on by some code. If someone runs with `-XX:AutoBoxCacheMax=1000`, values up to 1000 are also cached. Can you think of code that would behave correctly with the default cache but produce wrong results if the cache range is extended?

**Q2.** Java's `Optional<Integer>` vs `OptionalInt`: `Optional<Integer>` stores a boxed `Integer` (heap allocation); `OptionalInt` stores an `int` directly (no boxing). In a service that returns an optional numeric config value called millions of times per second, which would you use and why?
