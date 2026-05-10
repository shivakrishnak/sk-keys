---
id: JLG-047
title: "Project Valhalla: Value Types and Primitives"
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★★★
depends_on: JLG-001, JLG-046
used_by: JLG-051
related: JLG-048, JLG-049, JLG-052
tags:
  - java
  - advanced
  - internals
  - deep-dive
status: complete
version: 3
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /jlg/project-valhalla-value-types-and-primitives/
---

# JLG-047 - Project Valhalla: Value Types and Primitives

⚡ TL;DR - Project Valhalla adds value classes to Java: identity-free objects stored inline in arrays and fields without heap allocation or boxing, eliminating the fundamental performance gap between primitives and objects.

| Field | Value |
|---|---|
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]], [[JLG-046 - Java Language Specification Deep Dive]] |
| **Used by** | [[JLG-051 - Language Feature Trade-off Framing]] |
| **Related** | [[JLG-048 - Project Panama - Foreign Function and Memory API]], [[JLG-049 - Java Language Design History and Rationale]], [[JLG-052 - Java Ecosystem Selection Framework]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Java has a fundamental duality: 8 primitive types (`int`, `long`, `double`, etc.) stored inline in memory, and objects stored on the heap with a header, a pointer, and GC overhead. To use primitives in generic collections, they must be boxed: `int` becomes `Integer`, `double` becomes `Double`. Every boxed value is a separate heap object with a 16-byte header. An `ArrayList<Integer>` of 1 million integers uses 24MB instead of the 4MB an `int[]` would use, and accessing each element requires a pointer dereference.

**THE BREAKING POINT:**

For numerical computing, scientific computing, financial calculations, and data-intensive applications, the boxing overhead is not acceptable. Java cannot compete with C++/Rust for these workloads because `List<Double>` is 6x larger and 3x slower than `double[]`. The JVM's flat, dense memory layouts (which the CPU's prefetcher loves) are unavailable for generic Java data structures.

**THE INVENTION MOMENT:**

**Project Valhalla** (Brian Goetz, 2014-present) introduces **value classes** as a third kind of type (alongside primitive types and reference types). A value class is identity-free: no `==` identity comparison, no synchronisation (no monitor), no `null` reference. Values are stored inline in memory: in arrays as flat sequences, in fields directly in the enclosing object. No heap allocation, no pointer dereference.

**EVOLUTION:**

- **2014:** Project Valhalla kick-off; John Rose's original design sketches
- **2017:** JEP 169 (value types) first incubation; significant API design iterations
- **2021:** JEP 401 (primitive classes) draft - more radical design
- **2023:** LW1/LW2 prototypes available for testing
- **2024:** JEP 401 (value classes and objects) Third Preview (expected Java 23/24)
- **2025:** Target: Java 25 LTS inclusion (as finalised feature)

---

### 📘 Textbook Definition

**Project Valhalla** extends the Java type system with **value classes** (declared `value class`). Key properties:

- **Identity-free:** no object identity; `==` compares value (like primitives)
- **Inline storage:** stored directly in arrays and enclosing object fields; no heap allocation
- **Immutable:** all fields must be `final` (enables safe inline storage without aliasing)
- **Null-unrestricted:** primitive value types cannot be `null`; value objects retain nullability
- **Generic specialisation:** `List<int>` and `List<double>` become possible without boxing

---

### ⏱️ Understand It in 30 Seconds

**One line:** Value classes give Java the performance of primitives with the expressiveness of objects: inline storage, no boxing, no pointer indirection.

> Project Valhalla is like converting Java's data model from a warehouse of numbered storage lockers (heap objects each with a header and pointer) to a flat shelf where items sit directly in position (inline storage). Looking up item 500 in a locker warehouse means following 500 pointers. Looking up item 500 on a flat shelf is one memory read at a fixed offset. CPUs love flat shelves; they hate pointer chasing.

**One insight:** The phrase "codes like a class, works like an int" summarises Valhalla's design goal. You write `value class Point(int x, int y) {}` and get the programming model of a class with the memory layout of two adjacent `int`s in an array.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Objects with identity require pointer indirection; identity-free objects can be stored inline
2. Mutable inline objects would require defensive copying on every read; therefore value classes must be immutable
3. Generics specialisation requires the JIT to generate separate code for `List<int>` and `List<double>` (like C++ templates); existing erasure-based generics are incompatible
4. Null is an identity concept (null = absence of a reference); identity-free value types cannot be null
5. The memory layout improvement is most significant for arrays: `ValueClass[]` stores fields directly; `Object[]` stores pointers

**DERIVED DESIGN:**

From invariant 1 → `value class Point { final int x, y; }` stored in `Point[]` lays out as `[x0,y0,x1,y1,...,xN,yN]` in memory - cache-line-friendly.
From invariant 3 → Valhalla needs new bytecodes and JIT specialisation; not a simple language change.
From invariant 5 → a `Point[]` of 1 million elements: with value class = 8MB (2 ints × 4 bytes × 1M); with object reference = 16MB header + 8MB pointers + fragmented heap.

**THE TRADE-OFFS:**

**Gain:** Elimination of boxing for numeric/small-data types in generic collections; cache-friendly memory layout for arrays; GC pressure reduction from fewer heap objects.

**Cost:** Immutability constraint; no identity means no `synchronized` on value instances; complex JVM/JIT changes required; language/library migration effort.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The duality between primitives and objects is Java's foundational design tension. Value classes resolve it.

**Accidental:** The 10-year timeline of Project Valhalla reflects the difficulty of retrofitting value types into a JVM and language ecosystem that was designed around reference types and erasure-based generics.

---

### 🧪 Thought Experiment

**SETUP:** A financial risk engine performs Monte Carlo simulation: 10 million iterations, each computing a `Complex` number result (real + imaginary). Today, `Complex` is a class. Consider the memory implications.

**WHAT HAPPENS WITHOUT VALUE CLASSES:**

10 million `Complex` objects = 10 million heap allocations, each with a 16-byte header, 2 double fields (16 bytes), total 32 bytes × 10M = 320MB. GC must scan and potentially move all 10 million objects. Cache locality: random heap locations; each access potentially a cache miss.

**WHAT HAPPENS WITH VALUE CLASSES:**

```java
value class Complex {
    final double real;
    final double imag;
}
Complex[] results = new Complex[10_000_000];
```

Memory layout: `[real0, imag0, real1, imag1, ...]` = 16 bytes × 10M = 160MB. No GC objects to scan. Sequential memory access = hardware prefetcher works perfectly. Measured speedup for Monte Carlo: 3-5x on typical hardware.

**THE INSIGHT:**

The performance improvement from value classes is not just about fewer objects; it is about cache-line-friendly linear memory access replacing pointer-chased random access.

---

### 🧠 Mental Model / Analogy

> Project Valhalla's value types are like the difference between a filing cabinet (reference types) and a spreadsheet (value types). A filing cabinet stores each record in a separate physical folder (heap object); finding record 500 means pulling out the 500th folder from a cabinet. A spreadsheet stores records in consecutive rows; record 500 is at row 500. The spreadsheet is faster to scan because it is dense and sequential; the CPU's memory prefetcher can read ahead. Valhalla turns Java's filing cabinets into spreadsheets for appropriate data types.

**Element mapping:**
- Filing cabinet folder → heap object with header and pointer
- Spreadsheet row → value class stored inline
- Finding a folder → pointer dereference (cache miss risk)
- Reading a spreadsheet row → sequential memory access (cache hit)
- Folder type label → object reference type (with identity)
- Spreadsheet column format → value class type (without identity)

Where this analogy breaks down: spreadsheets are always 2D; value class arrays can hold arbitrarily nested value structures, not just flat rows.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java is adding a new kind of class that stores data directly in memory rather than on the heap. When you have a million of them, they sit next to each other in memory like an array of numbers, not scattered across the heap. This makes programs faster, especially for number-crunching and data-intensive code.

**Level 2 - How to use it (junior developer):**
Expected syntax (based on current JEP 401 draft):
```java
// Declare a value class:
value class Point {
    int x;
    int y;
    // fields implicitly final in value class
    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

// Use in array (stored inline):
Point[] points = new Point[1_000_000];
// points[i] stored at fixed offset i*8
// No heap allocation per element
```

**Level 3 - How it works (mid-level engineer):**
Value classes require JVM changes at multiple levels. The JVM needs new bytecodes for loading/storing value types inline (not through object references). The JIT must generate specialised code paths: `acmpeq` (reference equality) is meaningless for value types; value comparison requires field-by-field comparison. The heap layout of arrays changes: `int[]` stores 4 bytes per element; `Point[]` stores 8 bytes per element inline. Null is handled by a separate nullable wrapper type; a `Point?[]` can contain null at the cost of a null bit per slot.

**Level 4 - Why it was designed this way (senior/staff):**
The "codes like a class, works like an int" design was chosen over simpler alternatives (structs like C#, records without identity) because Java needed a path to retrofit existing generic libraries. The JDK's `List<E>`, `Map<K,V>` etc. must work with value types without complete rewrites. This requires both the language (value class syntax) and JVM (new bytecodes), and the runtime (JIT specialisation) to change simultaneously. The 10-year timeline reflects the constraint that existing Java bytecode must remain valid; no breaking changes to the JVM spec.

**Expert Thinking Cues:**
- "Primitive classes" (non-nullable value classes) and "value objects" (nullable) are separate categories in current Valhalla design; the distinction matters for null safety
- Generic specialisation (`List<int>`) requires changes to erasure; this is the most complex aspect and may arrive after basic value classes
- Early Valhalla prototypes measured 2-8x throughput improvement for complex number arithmetic in JDK benchmarks

---

### ⚙️ How It Works (Mechanism)

```
Memory Layout Comparison:

Reference Object Array (today):
  ComplexRef[]
  [ptr0, ptr1, ptr2, ...]   <- 8 bytes each
    |
    v
  [hdr|real0|imag0]         <- separate heap
  [hdr|real1|imag1]
  [hdr|real2|imag2]
  Each access = pointer dereference

Value Class Array (Valhalla):
  ComplexVal[]
  [real0|imag0|real1|imag1|real2|imag2|...]
  <- 16 bytes each, sequential memory
  Access index i = base + i*16 (direct)

JVM Changes Required:
  - New bytecodes: vload, vstore, vaload
  - New type descriptor format in classfiles
  - JIT specialisation for value types
  - GC: value arrays are not scanned for refs
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Define value class]
  value class Point { int x, y; }
     |
     ← YOU ARE HERE (expected Java 23/24+)
     |
[Compiler generates new bytecodes]
  vload, vstore, vaload/vastore
     |
[JIT generates specialised machine code]
  Point[] → flat 8-byte stride
  No pointer indirection in loops
     |
[Array stored flat in JVM heap]
  GC skips value arrays (no references)
     |
[CPU prefetches sequential data]
  Cache-line-friendly access pattern
```

**FAILURE PATH:**

Value class used where identity is expected: `synchronized(point)` compilation error. `point == other` compiles but compares field values, not identity. These are design-time constraints, not runtime failures.

**WHAT CHANGES AT SCALE:**

At scale, value classes most impact memory-intensive batch processing. A processing pipeline that today generates 10M intermediate objects per second (GC pressure) could use value classes to eliminate all intermediate allocation. GC pause frequency drops proportionally.

---

### 💻 Code Example

**Current workaround vs expected Valhalla:**

```java
// BAD: today's Complex using boxing
// in generic context:
List<Complex> list = new ArrayList<>();
// Each Complex: 32 bytes on heap
// Pointer indirection per access
// GC must scan all references

// BAD: today's best workaround (raw arrays):
double[] reals = new double[N];
double[] imags = new double[N];
// Memory-efficient but poor abstraction

// GOOD: expected Valhalla value class
// (JEP 401, preview in Java 23/24):
value class Complex {
    double real;
    double imag;
    // JVM stores inline: 16 bytes per element
    // No heap allocation, no GC scanning

    Complex add(Complex other) {
        return new Complex(
            real + other.real,
            imag + other.imag
        );
        // No heap allocation - returns by value
    }
}

// Generic usage (requires specialisation):
// List<Complex> = each element stored inline
// Expected later in Valhalla roadmap
```

**How to test / verify correctness:**

```bash
# Access Valhalla preview features:
# Build OpenJDK with Valhalla patches:
# https://openjdk.org/projects/valhalla/

# Run Valhalla preview with flags:
java --enable-preview \
  -source 23 \
  ComplexBenchmark.java

# JMH benchmark to measure improvement:
# Compare ArrayList<ComplexRef>
# vs double[] paired arrays
# vs expected ArrayList<ComplexVal>
```

---

### ⚖️ Comparison Table

| Type | Java Today | C# Struct | Valhalla Value Class | Rust Value Type |
|---|---|---|---|---|
| Identity | Yes (Object) | No (struct) | No | No |
| Null | Yes | No (default 0) | Nullable variant | Option<T> |
| Inline arrays | int[] only | struct[] | Yes | Yes |
| Generics | Erased (boxing) | Boxing | Specialised (planned) | Monomorphised |
| Mutability | Field-level | Mutable | Immutable | Default immutable |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Valhalla replaces records" | Records (Java 16) are reference types with structural equality. Valhalla value classes are identity-free inline types. Records may eventually become value classes, but they serve different purposes today. |
| "Valhalla ships in Java 21" | Valhalla is in active development. As of 2024, JEP 401 is in preview. Stable finalisation is targeted for Java 25 LTS. Do not use in production yet. |
| "Value classes can be null" | Primitive classes (non-nullable value classes) cannot be null. Value objects (nullable variant) can be null. The distinction determines memory layout. |
| "Valhalla makes generics like C++ templates" | Generic specialisation (`List<int>`) is a separate, later phase of Valhalla. Initial value classes work with object generics through boxing. Full specialisation comes later. |
| "Value classes are just records" | Records are shorthand for data-carrier reference classes with auto-generated equals/hashCode. Value classes are a JVM type change with different memory semantics. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Using value class where identity is expected**

**Symptom:** Compilation error: "Cannot synchronize on a value type." Or: equality semantics change (two equal values are `==` equal).

**Root Cause:** Code written expecting reference semantics (`synchronized`, identity-based `HashMap` keys, `==` identity check) used with value class.

**Diagnostic:**
```bash
# Compiler will reject invalid uses at compile
# time in final Valhalla design:
# javac --enable-preview will show errors for
# synchronized(valueInstance)
# identity-based Set membership
```

**Fix:** Use `synchronized` blocks on a separate lock object, not on the value instance. Use value-semantic equality for collections.

**Prevention:** Design value classes for data aggregation only; not for identity-based patterns like locks or identity maps.

---

**Mode 2: Mixed value/reference performance expectations**

**Symptom:** Benchmark shows no improvement after converting class to value class. Memory usage unchanged.

**Root Cause:** Value class used in `List<ValueClass>` which still uses erased Object array (boxing required). Generic specialisation not yet available.

**Diagnostic:**
```bash
# Profile memory allocation:
async-profiler -d 30 -e alloc \
  -f alloc.html <pid>
# If ValueClass shows in allocation flame
# graph, boxing is occurring
```

**Fix:** Use typed arrays `ValueClass[]` directly instead of `List<ValueClass>` until generic specialisation is available.

**Prevention:** Benchmark with and without value classes in array vs List context. Value class performance improvement currently requires typed arrays.

---

**Mode 3: Attempting to add value class to pre-Valhalla JDK (Version mismatch)**

**Symptom:** `error: value classes are a preview feature and are disabled by default`.

**Root Cause:** Project Valhalla features are preview/incubator; require specific JDK version and `--enable-preview` flag.

**Diagnostic:**
```bash
java --version
# Must be JDK 23+ with Valhalla support
# Or Valhalla early access build:
# https://jdk.java.net/valhalla/
```

**Fix:** Use Valhalla early-access JDK with `--enable-preview`. Do not use in production until feature is finalised.

**Prevention:** Track JEP 401 status. Subscribe to OpenJDK mailing lists for Valhalla timeline updates.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JLG-001 - What Is Java - History and Philosophy]] - JVM type system; primitives vs objects
- [[JLG-046 - Java Language Specification Deep Dive]] - JMM implications for value types

**Builds On This (learn these next):**
- [[JLG-048 - Project Panama - Foreign Function and Memory API]] - native memory layout; complements value types
- [[JLG-051 - Language Feature Trade-off Framing]] - when to adopt preview features

**Alternatives / Comparisons:**
- C# structs - similar inline value types; available since C# 1.0; Java is 25 years behind
- Kotlin inline classes - single-value wrappers with compile-time inlining; not full value semantics

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Value classes: identity-free JVM types  |
|               | stored inline without heap allocation   |
| PROBLEM       | Boxing `int` to `Integer` wastes memory;|
|               | Object arrays cannot be cache-efficient |
| KEY INSIGHT   | "Codes like a class, works like an int" |
|               | - inline storage, immutable, no identity|
| USE WHEN      | (Java 25+ when finalised) numerical data,|
|               | record-like aggregates in hot loops     |
| AVOID WHEN    | Before finalisation; where identity      |
|               | semantics needed; mutable shared state  |
| TRADE-OFF     | Cache-efficient flat storage vs          |
|               | immutability constraint, no null, no sync|
| ONE-LINER     | value class Point { int x, y; } stores  |
|               | inline in arrays; no boxing, no GC obj  |
| NEXT EXPLORE  | JLG-048 (Panama FFM),                   |
|               | JLG-051 (Feature trade-offs)            |
+----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Value classes eliminate boxing overhead: `Point[]` stores fields inline without heap allocation or pointer indirection
2. Value classes are identity-free: no `synchronized`, no `null` (primitive variant), equality is structural like primitives
3. Project Valhalla is still in development (2024); target is Java 25 LTS; use typed arrays today as the workaround

**Interview one-liner:** "Project Valhalla adds value classes to Java: identity-free, immutable types that store fields inline in arrays without heap allocation. This resolves Java's fundamental boxing overhead - `ValueClass[]` stores data at consecutive memory offsets like `int[]`, eliminating the pointer-per-element indirection of `Object[]`; expected to finalise in Java 25 LTS."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** *Data layout determines performance at scale.* The performance difference between `int[]` and `Integer[]` in Java is not about algorithm complexity; it is about memory layout. Dense, sequential, typed arrays match how CPU caches and prefetchers work. Pointer-chased structures (linked lists, object reference arrays) defeat hardware prefetching. This principle applies everywhere: database column stores vs row stores, struct-of-arrays vs array-of-structs in C++, flat message buffers (Protocol Buffers/FlatBuffers) vs nested JSON.

**Where else this pattern appears:**
- **Column-store databases (Parquet, Iceberg):** store all values of a column together; range scans on one column read sequential memory; row stores require skipping unrelated fields
- **C++ struct-of-arrays pattern:** separate arrays for each field instead of array of structs; enables SIMD vectorisation because the same field of multiple elements is contiguous
- **FlatBuffers/Cap'n Proto vs JSON:** zero-copy binary formats lay data inline at fixed offsets; access by offset computation not pointer dereference; same principle as Valhalla value arrays

---

### 💡 The Surprising Truth

Project Valhalla was announced in 2014 by Brian Goetz with the goal of shipping "in the next few years." As of 2024, it has been in development for 10 years - longer than the entire development of Java 1.0 through Java 8. The delay is not caused by lack of engineering talent; the JDK team includes some of the world's best JVM engineers. The delay is caused by a fundamental constraint: the JVM specification has never had a breaking change in 30 years, and value types require significant changes to the JVM classfile format, bytecode set, and generic type system. Every design decision must be backwards-compatible with all 30 years of Java code. C# introduced structs in version 1.0; Rust was designed with value semantics from the start. Java is retrofitting value types into a reference-type JVM designed before value types were considered necessary.

---

### 🧠 Think About This Before We Continue

**Question 1 (E - First Principles):** Value classes must be immutable (all fields `final`). This constraint exists because mutable inline values would require defensive copying: passing a `MutablePoint` to a method would need to copy all fields to prevent the method from modifying the caller's value. Explain why this copying requirement would eliminate the performance advantage of value classes, and why the immutability constraint is the correct design choice rather than mandating copying.

*Hint:* Consider what happens when a `MutablePoint` stored at `array[0]` is passed to a function. The function receives a copy or a reference. If a copy, the original is unchanged but every method call allocates. If a reference, the function can modify the original, breaking value semantics. Research how Kotlin's `data class` and C#'s `readonly struct` handle this trade-off.

**Question 2 (B - Scale):** A data processing pipeline processes 100 million Point3D(x,y,z) objects per second. Today, `Point3D` is a class: 100 million heap allocations per second, 2.4GB/s heap allocation rate, 90ms GC pauses every 2 seconds. With Valhalla value classes, Point3D would be stored inline. Estimate the GC pause frequency improvement, and identify what other parts of the pipeline would need to change to realise the full benefit.

*Hint:* If Point3D instances are allocated and discarded within one generation, the improvement is in young GC collection frequency. Research how the JVM's TLAB (Thread-Local Allocation Buffer) rate affects minor GC frequency. Also consider: if the pipeline stores Point3D in `List<Point3D>`, the boxing issue persists until generic specialisation arrives.

**Question 3 (C - Design Trade-off):** Kotlin `inline class` wraps a single value in a named type that is erased at compile time (the wrapper is removed; only the underlying type remains). Java records provide structural equality for reference types. Valhalla value classes provide inline storage and identity-free semantics. For a new Java financial library representing monetary amounts (`Money(long cents, Currency currency)`), compare the trade-offs of using: (a) a regular class, (b) a Java record, (c) a Kotlin inline class with a data class, and (d) a future Valhalla value class.

*Hint:* A `Money` record today allocates on the heap but has structural equality and pattern matching support. A Kotlin inline class can only wrap a single field (so `Money` needs wrapping tricks). A Valhalla value class with two fields would store both inline. Consider null safety, serialisation compatibility, and library API design in each case.
