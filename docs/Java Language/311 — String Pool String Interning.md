---
layout: default
title: "String Pool / String Interning"
parent: "Java Language"
nav_order: 311
permalink: /java-language/string-pool-string-interning/
number: "0311"
category: Java Language
difficulty: ★★☆
depends_on:
  - Heap Memory
  - Metaspace
  - JVM
  - String
used_by:
  - Autoboxing / Unboxing
  - Integer Cache
related:
  - Integer Cache
  - Autoboxing / Unboxing
  - Heap Memory
  - Metaspace
tags:
  - java
  - jvm
  - memory
  - intermediate
  - java-internals
---

# 0311 — String Pool / String Interning

⚡ TL;DR — The String Pool is a JVM-maintained cache of String literals that ensures identical string values share a single heap object, eliminating redundant memory for repeated strings.

| #0311 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Heap Memory, Metaspace, JVM | |
| **Used by:** | Autoboxing / Unboxing, Integer Cache | |
| **Related:** | Integer Cache, Autoboxing / Unboxing, Heap Memory | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every time Java code evaluates the string literal `"hello"` in two different places, it would create two separate heap objects, both containing `h-e-l-l-o`. In a server application with hundreds of classes each containing string literals like `"application/json"`, `"Content-Type"`, `"GET"`, `"POST"`, each class load creates a fresh copy of each literal. Even more: `"application/json"` appears in 80 different classes, creating 80 separate 32-byte objects holding the same content.

**THE BREAKING POINT:**
A content platform has 10,000 articles, each stored with a MIME type of `"text/html"`. Without a string pool, each article object holds a separate `String` instance. 10,000 × (16 bytes header + 8 bytes char pointer + length/hash = ~40 bytes) = 400KB for identical content. In a JVM processing millions of HTTP headers, duplicated `"Content-Type"` strings alone waste megabytes.

**THE INVENTION MOMENT:**
This is exactly why the **String Pool** was created — to maintain a de-duplicated table of String instances so all string literals with identical content share one JVM object.

---

### 📘 Textbook Definition

The **String Pool** (also called the "String Table" or "Intern Pool") is a hash table maintained by the JVM containing unique `String` instances. String literals declared in Java source code (e.g., `"hello"`) are automatically interned — placed in the pool during class loading. Two literals with the same value always resolve to the same pool entry, sharing a single heap object. The `String.intern()` method allows runtime-created strings to be explicitly pooled. As of Java 7+, the String Pool resides in the Java heap (previously in PermGen/Metaspace in Java 6), making pool contents eligible for GC when no longer reachable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Java maintains a dictionary of strings — if two identical strings exist, they share one memory object.

**One analogy:**
> Imagine a school using the same textbook edition in 30 classrooms. Instead of buying 30 copies of "The Complete Grammar Guide" for each classroom wall (one sign per room), the school has ONE authorized copy in the library, and each classroom has a laminated card saying "refer to library copy, shelf 3." The String Pool is that library card system — one real copy, many references.

**One insight:**
String Pool lookup uses `==` (reference equality) after interning. This is why `"hello" == "hello"` is `true` (both refer to the same pooled String object), but `new String("hello") == new String("hello")` is `false` (two new heap objects outside the pool). This `==` quirk causes some of the most common Java bugs among beginners — and is exactly why the rule "always use `.equals()` for String comparison" exists.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. `String` is immutable in Java — the same String object can be safely shared by any number of references.
2. String literals in Java source are known at compile time — they can be deduplicated at class load.
3. `String.intern()` provides a runtime hook to join the pool explicitly.

**DERIVED DESIGN:**

**Compile-time interning:**
At compile time, the Java compiler places string literal values in the class file's constant pool. At class loading, the JVM resolves these constants against the String Table (the runtime String Pool). If a matching entry exists: return the existing reference. If not: create a new String object, add to table, return reference.

**Runtime interning:**
`str.intern()` computes the hash of `str`'s content, looks up the String Table, and either returns an existing matching entry or adds `str` to the table.

```
┌────────────────────────────────────────────────┐
│          String Pool Mechanism                 │
│                                                │
│  Class loading: constant "application/json"    │
│                                                │
│  String Table lookup:                          │
│    hash("application/json") = 0x7A2B           │
│    table[0x7A2B]? → found!                     │
│    return existing String reference            │
│                                                │
│  OR:                                           │
│    not found → create new String               │
│    table[0x7A2B] = new String object           │
│    return new String reference                 │
│                                                │
│  Pool entry: weak reference (Java 7+)          │
│    → GC can collect if no strong refs          │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Memory savings for repeated string literals; reference equality check for interned strings is O(1).
**Cost:** String Table is a global concurrent hash table (contention under high intern() rate); String Pool GC is less efficient than normal object GC (requires table scan); `.intern()` has non-trivial overhead (~100ns for lookup hit).

---

### 🧪 Thought Experiment

**SETUP:**
Two ways to check if a configuration value equals "debug":

```java
String logLevel = getConfigValue("log.level"); // "debug"
if (logLevel == "debug") { ... }    // WRONG!
if (logLevel.equals("debug")) { ... } // RIGHT
```

WITHOUT UNDERSTANDING STRING POOL:
Developer assumes `==` works like `.equals()`. It works in testing (where `getConfigValue` returns a literal) but fails in production (where the value comes from a file read — creating a new non-pool String).

WITH UNDERSTANDING:
`getConfigValue("log.level")` reads from a file, creating a new String: `new String("debug")`. This new String is NOT in the pool. `logLevel == "debug"` compares two different object references → `false`. The `if` block never executes. Config has no effect.

**THE INSIGHT:**
The String Pool is an optimization, not a language contract. Any String not explicitly interned (via `intern()` or being a literal) lives outside the pool. Always use `.equals()` for String value comparison — reference equality (`==`) only works reliably for pool members.

---

### 🧠 Mental Model / Analogy

> The String Pool is like a post office's address book. The address book has one canonical entry for each address. When a letter (string) arrives, the post office checks: "is this address already in the book?" If yes, use the existing entry number. If no, register it. Every letter to "123 Main St" gets the same address book entry number — they all point to the same canonical representation.

- "Address book entry" → String Pool entry.
- "New letter arrives" → new String literal or intern() call.
- "Entry number" → reference to the single canonical String object.
- "Checking the book" → String Table hash table lookup.
- "Two letters same address" → two literals or interned strings with same content share one object.

Where this analogy breaks down: Our address book persists forever. Java's String Pool can lose entries via GC if no strong references to the pooled String remain outside the pool — the pool uses weak references (Java 7+).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Java keeps one copy of every repeated text string in a shared dictionary. When your code has `"hello"` written in 50 places, Java only stores the actual text once and lets all 50 places point to the same storage — saving memory.

**Level 2 — How to use it (junior developer):**
String literals are pooled automatically — no action needed. Rule: always compare Strings with `.equals()`, never `==`. If you need to intern runtime Strings: `str.intern()`. Do NOT spam `intern()` — the String Table is global and calling `intern()` on every incoming HTTP parameter can cause GC issues.

**Level 3 — How it works (mid-level engineer):**
The JVM String Table is a concurrent hash table with a fixed number of buckets (configurable via `-XX:StringTableSize`, default 65,536 in Java 8, 1,000,003 in Java 11+, prime numbers for good hash distribution). At class load: each string constant in the class constant pool is resolved via the String Table. `String.intern()` computes the string's hash, probes the table, and either returns the existing entry or inserts a new one. On lookup collision: chain through the bucket's linked list. The table entries are weak references — if no strong reference to a pooled String exists outside the table, GC can collect it and remove the entry.

**Level 4 — Why it was designed this way (senior/staff):**
Moving the String Pool from PermGen (Java 6) to the Heap (Java 7) was a significant design improvement. PermGen was a fixed-size, non-GC'd memory area — a PermGen String Pool could fill with interned Strings and cause `OutOfMemoryError: PermGen space` with no way to reclaim them. In the heap, pooled strings are GC'd like normal objects (via weak references). The table itself (the hash structure) remains in the heap metadata region, but the String object data lives in the heap. The Java 11+ pooling behavior for string deduplication by G1GC (`-XX:+UseStringDeduplication`) is a DIFFERENT mechanism from interning: it doesn't affect identity equality (`==`), only de-duplicates the backing `char[]`/`byte[]` arrays of String objects. Both mechanisms target the same problem from different angles.

---

### ⚙️ How It Works (Mechanism)

**String Table operations:**
```
intern() algorithm:
  1. Compute hash: str.hashCode()
  2. bucket = hash % StringTableSize
  3. Walk bucket's chain: compare each entry by value (.equals())
  4. Found: return existing String reference
  5. Not found: add str to chain, return str

Complexity:
  Lookup: O(n) worst case (bucket chain length)
  Average: O(1) with good hash distribution
  StringTableSize should be prime for good distribution
```

**Literal interning at class load:**
```java
// Source code:
String s = "hello";

// Class file constant pool (#2 = "hello"):
// LDC #2  ← load constant from pool

// JVM at class load:
// Resolve constant #2 → call String.intern("hello")
// Return reference to pooled String
// All LDC "hello" instructions in this and other classes
// return the same object reference
```

**G1GC String Deduplication (different from interning):**
```bash
# Enable G1 String deduplication:
java -XX:+UseG1GC \
     -XX:+UseStringDeduplication \
     -XX:+PrintStringDeduplicationStatistics MyApp

# This de-duplicates the backing byte[] arrays of Strings,
# NOT the String objects themselves.
# Does NOT affect == comparison.
```

**String Table resizing:**
```bash
# Java 11+ auto-sizes the table. For Java 8:
java -XX:StringTableSize=131072 MyApp  # larger prime
# For very high intern() usage:
java -XX:StringTableSize=1048573 MyApp  # ~1M entries
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[Java class loads with literal "Content-Type"]
    → [LDC bytecode: load constant]
    → [JVM: String Table lookup for "Content-Type"]  ← YOU ARE HERE
    → [Found: return existing reference]
    → [All classes with "Content-Type" literal: same reference]
    → [Memory: 1 String object, N references]

AT RUNTIME with intern():
[String fromNetwork = "Content-Type" + "" (runtime concat)]
    → [Not in pool initially]
    → [fromNetwork.intern() → String Table lookup]
    → [Return canonical pool reference]
    → [fromNetwork == "Content-Type" now true]
```

**FAILURE PATH:**
```
[Excessive runtime intern() calls]
    → [String Table grows: millions of entries]
    → [Concurrent GC of String Table: table scan overhead]
    → [Minor GC pause extends: clearing dead table entries]
    → [Fix: reduce intern() usage, use explicit caches instead]
```

**WHAT CHANGES AT SCALE:**
In a high-volume service interning thousands of distinct strings per second (e.g., interning HTTP header names), the String Table becomes a global contention point. Each `intern()` call acquires a table segment lock. At scale with 100 threads each calling `intern()` 10,000 times/second = 1M intern calls/second — String Table becomes a lock contention bottleneck. Alternative: explicit `ConcurrentHashMap<String, String>` application-level cache with `computeIfAbsent` for explicit deduplication without the JVM table overhead.

---

### 💻 Code Example

Example 1 — The classic == vs equals trap:
```java
// Very common Java interview question / bug:
String a = "hello";
String b = "hello";
String c = new String("hello");
String d = new String("hello").intern();

System.out.println(a == b);         // true  (same pool entry)
System.out.println(a == c);         // false (c is on heap, not pool)
System.out.println(a == d);         // true  (d is interned = pool entry)
System.out.println(c.equals(d));    // true  (same content)

// RULE: ALWAYS use .equals() for String value comparison
```

Example 2 — Safe string comparison patterns:
```java
// BAD: Dangerous == comparison
if (status == "active") { ... }  // fragile!

// GOOD: Always equals()
if ("active".equals(status)) { ... }  // null-safe if status might be null
// Or:
if (status != null && status.equals("active")) { ... }
// Or Java 7+ Objects.equals:
if (Objects.equals(status, "active")) { ... }
```

Example 3 — When intern() is appropriate:
```java
// APPROPRIATE: Interning known-finite-set strings
// (e.g., HTTP method names, status names, protocol tokens)
public class HttpMethod {
    public static final String GET = "GET".intern();
    public static final String POST = "POST".intern();
    // Now GET == "GET" and POST == "POST" in all contexts
}

// INAPPROPRIATE: Interning arbitrary user input
// BAD: This will fill the String Table with unbounded entries!
public void processRequest(HttpRequest req) {
    String username = req.getParam("username").intern(); // DANGER!
}
```

Example 4 — Monitoring String Pool statistics:
```bash
# Check String Table statistics at runtime:
jcmd <pid> VM.stringtable

# Sample output:
# StringTable statistics:
# Number of buckets       :   1048576   = 536870912 bytes, each 512
# Number of entries       :    523456   = 523456 entries
# Number of literals      :    412345
# Average bucket size     :        2
# Maximum bucket size     :       17
# Load factor             :    0.499

# Large maximum bucket size (>15) = poor hash distribution
# → increase StringTableSize to larger prime
```

---

### ⚖️ Comparison Table

| String Creation Method | In Pool? | == with literal? | GC Eligible? | Memory Impact |
|---|---|---|---|---|
| `"hello"` (literal) | Yes (auto-interned) | Yes | Yes (weak ref) | Shared object |
| `new String("hello")` | No | No | Yes (normal) | New object |
| `"hello".intern()` | No-op (already there) | Yes | Yes (weak ref) | No change |
| `new String("hello").intern()` | Yes (after intern()) | Yes | Yes (weak ref) | Shared object |
| `String.format("hello %s", x)` | No | No | Yes (normal) | New object |

How to choose: Use string literals for constants. Never use `new String("literal")` — wasteful. Reserve `intern()` for explicitly managing deduplication of a finite known set of values.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All Strings go into the pool | Only string literals and explicitly `.intern()`'d strings are pooled. `new String(...)`, `String.format(...)`, concatenation results are NOT pooled unless explicitly interned |
| String pool prevents memory leaks | Before Java 7, the pool was in PermGen — excessive interning DID cause `OutOfMemoryError` and could not be GC'd. In Java 7+, pooled strings CAN be GC'd via weak references |
| `==` for String comparison works when both are literals | It works for literals but is UNSAFE in general. As soon as either string comes from runtime computation (file read, DB query, user input), it's NOT in the pool and `==` fails |
| `intern()` is free | `intern()` involves a concurrent hash table lookup (global lock segments). At high volume, it is a contention point and significantly slower than `.equals()` |
| String.intern() always returns the same object as the literal | `String.intern()` returns the canonical pool entry. If the literal was loaded first, it's the literal's object. If `intern()` was called on a runtime string first, that runtime string becomes the canonical entry — the literal's reference resolves to it thereafter |

---

### 🚨 Failure Modes & Diagnosis

**String Table OOM (PermGen Era — Java 6)**

**Symptom:**
`OutOfMemoryError: PermGen space` in Java 6 applications with heavy `intern()` usage.

**Root Cause:**
Java 6 stores the String Pool in PermGen (fixed size, not GC'd by default). Every interned string permanently occupies PermGen.

**Diagnostic Command / Tool:**
```bash
# Java 6 monitoring:
jmap -permstat <pid>
# Count interned String entries in PermGen
```

**Fix:**
Upgrade to Java 8+ (pool moved to heap). Or stop interning arbitrary strings.

**Prevention:**
In Java 8+: not applicable. String Pool is GCable.

---

**Excessive intern() Calls Causing GC Overhead**

**Symptom:**
Minor GC pause times increase gradually over hours. GC stats show growing String Table. Eventually GC spends significant time clearing dead String Table entries.

**Root Cause:**
Code paths call `intern()` on arbitrary user-input strings (e.g., request parameters, JSON field values). Millions of unique strings enter the pool; most are short-lived but the table maintains weak references until the next GC.

**Diagnostic Command / Tool:**
```bash
jcmd <pid> VM.stringtable
# Monitor "Number of entries" growing → intern() abuse
```

**Fix:**
Remove `intern()` from hot paths processing user input. Use `ConcurrentHashMap<String, String>` for explicit, controlled deduplication with limited size.

**Prevention:**
Code review: `intern()` should only appear in constants, enum-like values, or controlled finite value sets.

---

**`==` String Comparison Bug in Boolean Test**

**Symptom:**
Configuration-driven behavior not working in production. Works in unit tests. Bug is intermittent and hard to reproduce.

**Root Cause:**
Code uses `==` to compare strings. In tests, the value comes from a literal (pool) and matches. In production, the value comes from file/DB/network — not in pool — and `==` returns false.

**Diagnostic Command / Tool:**
```java
// Add debug logging to identify:
log.debug("Expected '{}' ({}), Got '{}' ({})",
    expected, System.identityHashCode(expected),
    actual, System.identityHashCode(actual));
// Different identity hash codes confirm different objects
```

**Fix:**
Replace all `==` String comparisons with `.equals()` or `Objects.equals()`. Add Checkstyle rule: warn on String `==` comparison.

**Prevention:**
Add Checkstyle or SpotBugs rule to flag `==` comparisons involving String types.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Heap Memory` — the String Pool (Java 7+) lives in the heap; understanding heap structure explains where pool objects reside
- `JVM` — the String Pool is a JVM-managed table; the JVM allocates and manages it during class loading

**Builds On This (learn these next):**
- `Integer Cache` — the same "cache small values" pattern applied to integers; understanding String Pool makes Integer Cache's design obvious
- `Autoboxing / Unboxing` — autoboxing uses the Integer Cache; understanding the caching pattern from String Pool prepares you for autoboxing nuances

**Alternatives / Comparisons:**
- `Integer Cache` — Java's equivalent deduplication cache for Integer values -128 to 127; same pattern, different type
- `G1GC String Deduplication` — a GC-level optimization that deduplicates String backing arrays without affecting identity equality; complementary but distinct from String interning

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ JVM hash table holding one canonical       │
│              │ String object per unique string value      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Duplicate string objects waste memory for  │
│ SOLVES       │ repeated string values (literals, constants)│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ String literals are ALWAYS pooled; runtime │
│              │ Strings are NOT unless explicitly intern()'d│
│              │ → NEVER use == for String value comparison  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (automatic for literals). Use       │
│              │ intern() only for finite known value sets  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never intern() user-input or dynamic       │
│              │ strings — causes String Table bloat        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Memory savings vs intern() overhead        │
│              │ and == comparison pitfalls                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One library book, many readers —          │
│              │  but always check the content, not the     │
│              │  shelf number"                             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Integer Cache → Autoboxing → Generics      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice processes JSON payloads where field names (`"userId"`, `"transactionId"`, `"amount"`) repeat millions of times per day. A developer suggests using `.intern()` on all JSON field names during parsing to reduce memory. Another developer says this is dangerous. Who is right, and what specific metric would you measure in production to determine whether interning JSON field names provides a net benefit or a net harm? Include the exact JVM diagnostic command you would use.

**Q2.** Java's String Pool uses weak references so pooled strings can be GC'd. But the String Table hash structure (the buckets and chains) is NOT weakly referenced — it has to be scanned during GC to find and remove entries for collected strings. At 10 million pooled strings in the table, estimate the GC overhead of scanning the String Table on each Minor GC, and explain why this overhead grows super-linearly as the table fills beyond its initial bucket count (hint: consider hash chain length distribution).

