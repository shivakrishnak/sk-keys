---
layout: default
title: "String Pool / String Interning"
parent: "Java Language"
nav_order: 311
permalink: /java-language/string-pool/
number: "311"
category: Java Language
difficulty: ★★☆
depends_on: "Heap Memory, Metaspace, Object Header"
used_by: "String comparison, String deduplication, JVM memory optimization"
tags: #java, #jvm, #strings, #memory, #interning
---

# 311 — String Pool / String Interning

`#java` `#jvm` `#strings` `#memory` `#interning`

⚡ TL;DR — The **String Pool** is a JVM-managed cache of String literals in the heap; String interning means storing only one copy of equal strings. `==` works on literals; use `.equals()` everywhere else.

| #311            | Category: Java Language                                          | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Heap Memory, Metaspace, Object Header                            |                 |
| **Used by:**    | String comparison, String deduplication, JVM memory optimization |                 |

---

### 📘 Textbook Definition

The **String Pool** (also called the String Intern Pool or String Constant Pool) is a special region in the Java heap where the JVM stores a single canonical copy of each distinct String literal. When the JVM encounters a String literal (e.g., `"hello"`), it checks the pool: if the string already exists, the existing reference is returned; if not, a new String object is added to the pool. `String.intern()` explicitly requests the pool: if the pool contains a string `.equals()` to the caller, return that pooled instance; otherwise add and return. Prior to Java 7, the pool lived in PermGen; from Java 7+ it was moved to the heap, allowing pooled strings to be garbage-collected.

---

### 🟢 Simple Definition (Easy)

String literals in Java are automatically deduplicated. `"hello" == "hello"` is `true` because both refer to the same object in the String pool. `new String("hello") == "hello"` is `false` because `new String(...)` creates a fresh heap object, bypassing the pool. The pool saves memory when many variables hold equal strings. Always compare strings with `.equals()`, not `==`.

---

### 🔵 Simple Definition (Elaborated)

A university library: instead of printing a separate copy of every textbook for every student, the library maintains one canonical copy and lends out references. String pool: the JVM's library for String objects. `"hello"` at line 10 and `"hello"` at line 500 in the same program: same object, two references. Memory saving: significant for applications that process lots of repetitive strings (HTTP headers, field names, status codes). `new String("hello")`: like a student printing their own private copy — separate object, even though content is identical.

---

### 🔩 First Principles Explanation

**String immutability + pool mechanics:**

```
STRING POOL MECHANICS:

  String literal: "hello"
  JVM process:
  1. Look up "hello" in String pool (hashtable-based lookup)
  2a. Found → return existing reference (no new allocation)
  2b. Not found → create String object, add to pool, return reference

  String.intern():
  String s = new String("hello");  // new heap object, NOT in pool
  String t = s.intern();           // adds "hello" to pool (if absent), returns pooled ref
  s == t  → false  (s is heap, t is pool)
  t == "hello" → true  (both are the same pooled object)

  Pool location by JVM version:
  Java 6:  PermGen (size limited by -XX:MaxPermSize; OutOfMemoryError: PermGen space)
  Java 7+: Heap    (GC can collect unused pooled strings; -XX:StringTableSize=65536)
  Java 8+: Metaspace for class metadata, but pool is on heap

  Pool size (hash table buckets):
  Default: 65,536 buckets (Java 11+)
  If millions of distinct strings interned: collisions → performance degrades
  Tuning: -XX:StringTableSize=131072 (power of 2)

COMPILE-TIME vs RUNTIME:

  // Compile-time constants → pooled:
  String a = "hello";
  String b = "hello";
  String c = "hel" + "lo";  // constant folding → "hello" at compile time
  a == b → true
  a == c → true

  // Runtime concatenation → NOT pooled:
  String prefix = "hel";
  String d = prefix + "lo";  // computed at runtime → new String on heap
  a == d → false
  a.equals(d) → true

  // Intern to pool:
  String e = d.intern();
  a == e → true

JAVA 8 STRING DEDUPLICATION (G1 GC):

  Different from interning:
  -XX:+UseG1GC -XX:+UseStringDeduplication
  G1 GC: during minor GC, identifies duplicate char[] arrays backing different String objects
  Replaces duplicate char[] with a single shared copy
  Reduces heap pressure WITHOUT changing reference identity
  String A == String B → still false (different objects, same backing array)

  WHEN TO USE INTERN:
  - Known high-cardinality repeated strings: HTTP header names, XML element names, DB column names
  - Enables == comparison (fast) instead of .equals() (character-by-character)
  - Risk: if strings are not truly repeated, intern() adds GC pressure (pool entries held strongly)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT String Pool:

- Every occurrence of `"OK"` in HTTP responses creates a new heap object → thousands of identical String objects → GC pressure
- No way to use identity comparison (`==`) safely

WITH String Pool:
→ One canonical `"OK"` object shared across all references. `==` comparison on literals is O(1) pointer comparison vs O(n) `.equals()`. Memory-efficient for repetitive string workloads.

---

### 🧠 Mental Model / Analogy

> A post office that stamps all identical letters with the same tracking number. When you send a letter with text "Hello World," the post office checks: "Do we already have this exact letter in our registry?" If yes — give you the registry copy's tracking number. If no — file it and give you a new number. Two senders with identical letters → same tracking number → same object. Opening one envelope gives you the same content as the other.

"Registry of canonical letters" = String pool (hash table indexed by string content)
"Tracking number" = object reference (memory address)
"Two senders, same letter" = two `"hello"` literals → same reference
"`new String("hello")`" = bypassing the registry; requesting a private new copy
"`String.intern()`" = asking the post office to check the registry and return the canonical copy
"Same tracking number → `==` works" = reference equality on pooled strings is safe

---

### ⚙️ How It Works (Mechanism)

```
BYTECODE VIEW:

  Java source:          Bytecode:
  String a = "hello";  ldc "hello"  ← loads from constant pool; pool lookup
  String b = "hello";  ldc "hello"  ← same constant pool entry → same reference

  new String("hello")  new java.lang.String
                       ldc "hello"   ← arg: pooled string passed to constructor
                       invokespecial  ← creates NEW heap object copying content

  String.intern():
  Native method → looks up in StringTable (C++ hash table in JVM)
  Thread-safe: synchronized per bucket
  Performance: fast for small pools; degrades with millions of distinct strings

MEMORY LAYOUT:

  String Pool (heap, StringTable):  ┌──────────────────┐
  "hello" ────────────────────────► │ String@0x7f3c    │
  "world" ────────────────────────► │ String@0x7f4a    │
                                    └──────────────────┘

  new String("hello"):              ┌──────────────────┐
  Separate heap object ───────────► │ String@0x8a21    │ ← different address
                                    └──────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
String literal in source code
        │
        ▼
String Pool (JVM StringTable)
(deduplication; reference caching; heap-resident from Java 7+)
        │
        ├── Heap Memory: pool lives in heap (Java 7+); subject to GC
        ├── Autoboxing/Unboxing: similar caching for Integer (-128..127)
        └── String.intern(): explicit pool membership request
```

---

### 💻 Code Example

```java
// POOL BEHAVIOR:
String a = "hello";          // pooled
String b = "hello";          // same pooled instance
String c = new String("hello"); // new heap object

System.out.println(a == b);  // true  (same pool reference)
System.out.println(a == c);  // false (pool vs. heap)
System.out.println(a.equals(c)); // true  (content equal)

// INTERN:
String d = c.intern();  // returns pooled "hello"
System.out.println(a == d);  // true

// RUNTIME CONCATENATION:
String prefix = "hel";
String e = prefix + "lo";    // runtime: new heap object
System.out.println(a == e);  // false
System.out.println(a == e.intern()); // true (after intern)

// BEST PRACTICE: ALWAYS use .equals() for string comparison
// Never rely on == unless you explicitly manage internment
if (status.equals("OK")) { ... }     // correct
if (status == "OK") { ... }          // WRONG — UB unless both interned
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                       |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| All String objects are in the pool                | Only String literals and `.intern()` results are pooled. `new String("x")` creates a separate heap object.                                                                                    |
| The String pool is in PermGen                     | Since Java 7, the String pool lives in the heap and can be GC'd. PermGen (or Metaspace) holds class metadata, not the String pool.                                                            |
| `intern()` is always safe for memory optimization | Interning millions of distinct strings fills the pool; entries are held strongly (won't be GC'd while pool exists). Use with caution; prefer G1's `UseStringDeduplication` for passive dedup. |

---

### 🔥 Pitfalls in Production

**Using `==` for String comparison leads to intermittent bugs:**

```java
// ANTI-PATTERN:
String status = request.getParameter("status");  // value from HTTP request: NOT pooled
if (status == "active") {  // ALWAYS false — different objects even if content matches
    doActiveThing();
}

// FIX:
if ("active".equals(status)) {  // content comparison: correct
    doActiveThing();
}
// Use the literal on the left: guards against NullPointerException if status is null
// "active".equals(null) → false (no NPE)
// status.equals("active") → NullPointerException if status is null
```

---

### 🔗 Related Keywords

- `Autoboxing / Unboxing` — similar JVM caching mechanism for Integer (-128..127)
- `Heap Memory` — String pool resides in heap (Java 7+)
- `String.intern()` — explicit method to add/retrieve from String pool
- `G1 GC String Deduplication` — passive dedup of String backing arrays without reference sharing
- `StringBuilder` — use for building strings; `+` in loops creates many intermediate Strings

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ JVM caches String literals. Same literal │
│              │ → same object. Use .equals() always.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Memory optimization for high-repetition │
│              │ strings; intern() for explicit caching  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Interning millions of distinct strings  │
│              │ (pool GC pressure); always prefer G1    │
│              │ StringDedup for passive dedup           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Post office canonical copy: 'hello'    │
│              │  stored once, all literals point to it."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Autoboxing → Integer Cache →             │
│              │ Heap Memory → G1 GC → StringBuilder     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `String.intern()` in Java 6 put strings in PermGen (fixed size), making it a common source of `OutOfMemoryError: PermGen space` in applications that interned large volumes of user-provided strings. What changed in Java 7 that solved this? And why is it still risky to call `intern()` on arbitrary user input even in Java 7+?

**Q2.** The JVM's StringTable is a fixed-size hash table. At high string cardinality (millions of interned strings), hash collisions cause `O(n)` lookup degradation. `-XX:StringTableSize` lets you resize the table. How do you diagnose StringTable pressure in production, and what JVM flags give you StringTable statistics?
