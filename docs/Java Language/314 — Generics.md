---
layout: default
title: "Generics"
parent: "Java Language"
nav_order: 314
permalink: /java-language/generics/
number: "0314"
category: Java Language
difficulty: ★★☆
depends_on: Type Systems (Static vs Dynamic), Autoboxing / Unboxing, Inheritance
used_by: Type Erasure, Bounded Wildcards, Stream API, Collections Framework
related: Type Erasure, Bounded Wildcards, Covariance / Contravariance
tags:
  - java
  - generics
  - type-safety
  - intermediate
  - deep-dive
---

# 0314 — Generics

⚡ TL;DR — Generics let you write type-safe collections and algorithms once, then reuse them for any type — catching type errors at compile time instead of runtime.

| #0314 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Type Systems (Static vs Dynamic), Autoboxing / Unboxing, Inheritance | |
| **Used by:** | Type Erasure, Bounded Wildcards, Stream API, Collections Framework | |
| **Related:** | Type Erasure, Bounded Wildcards, Covariance / Contravariance | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Java 1.5, all collections stored `Object`. To use a `List` of `String`, you wrote `List list = new ArrayList()`, added strings freely, but had to cast on every retrieval: `String s = (String) list.get(0)`. Nothing stopped you from accidentally adding an `Integer` to a list intended for `String`. The `ClassCastException` only appeared at runtime — often in production, deep in code paths that weren't thoroughly tested.

**THE BREAKING POINT:**
A payment service stores `List<PaymentEvent>` as a raw `List`. A junior engineer accidentally calls `list.add(new AuditEvent())`. The code compiles. The service runs fine all day — until the payment processor iterates the list and casts each element to `PaymentEvent`. Then `ClassCastException` crashes the nightly batch. The bug was introduced 3 weeks earlier in a different class. The stack trace points nowhere useful.

**THE INVENTION MOMENT:**
This is exactly why **Generics** were created — to parameterise classes and methods by type, so the compiler can verify type correctness at compile time, eliminating an entire class of runtime `ClassCastException` bugs while also removing the need for explicit casts.

---

### 📘 Textbook Definition

**Generics** are a compile-time type-parameterisation mechanism introduced in Java 5 (JSR 14) that allow classes, interfaces, and methods to operate on parameterised types. A generic type declaration such as `class Box<T>` defines a family of types — `Box<String>`, `Box<Integer>`, etc. — each enforcing type safety independently. At runtime, type parameters are erased by the compiler (Type Erasure), so a single compiled class file serves all instantiations. This provides type safety at zero runtime cost.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write a class once that works safely for any type, with the compiler checking types for you.

**One analogy:**
> A vending machine labelled "Snacks Only" won't let you insert a drink — it's parameterised by product type. A generic `Box<T>` is the same: once you say `Box<String>`, only strings go in and come out, and the compiler enforces this.

**One insight:**
Generics move type errors from runtime (a `ClassCastException` in production) to compile time (a red squiggly in your IDE). The same information that previously blew up at 2am during a batch job now shows up as a compilation error you fix before lunch.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A generic type is a template — `List<T>` is not a type itself, but a blueprint that becomes a concrete type when `T` is bound (e.g., `List<String>`).
2. Type safety is enforced by the compiler only — at runtime, type parameters are erased (see Type Erasure entry).
3. A parameterised type is invariant by default: `List<String>` is NOT a `List<Object>`, even though `String extends Object`.

**DERIVED DESIGN:**
Given invariant 1, we need a syntax for declaring type parameters: `<T>` on class declarations, and `<T>` on method declarations. Given invariant 2, there's no runtime overhead — generics are purely a compile-time feature. Given invariant 3, if you need flexibility, you use wildcards (`? extends T`, `? super T`) rather than widening the type parameter.

```java
// Generic class: T is the type parameter
public class Box<T> {
    private T value;

    public void set(T value) { this.value = value; }
    public T get() { return value; }
}

// Generic method: <T> declared on the method itself
public static <T> List<T> repeat(T item, int times) {
    List<T> result = new ArrayList<>();
    for (int i = 0; i < times; i++) result.add(item);
    return result;
}
```

```
┌────────────────────────────────────────────────┐
│          Generic Type Instantiation            │
│                                                │
│  Box<T>  ← type parameter (compile-time only) │
│    ↓                                           │
│  Box<String>   → compiler checks: only String  │
│  Box<Integer>  → compiler checks: only Integer │
│  Box<Employee> → compiler checks: only Employee│
│                                                │
│  All three compile to the SAME bytecode:       │
│  Box (raw type) using Object internally        │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Compile-time type safety, elimination of explicit casts, better IDE support and refactoring.
**Cost:** Type Erasure means no runtime type information for the generic parameter; invariance of parameterised types surprises developers familiar with covariant arrays.

---

### 🧪 Thought Experiment

**SETUP:**
Two versions of a `Pair` class — one raw, one generic. Both store two values.

**WHAT HAPPENS WITHOUT GENERICS:**
```java
Pair pair = new Pair();
pair.setFirst("Alice");
pair.setSecond(42);
String name = (String) pair.getSecond(); // ClassCastException at runtime!
```
The compiler is silent. The error surfaces only when `getSecond()` is cast.

**WHAT HAPPENS WITH GENERICS:**
```java
Pair<String, String> pair = new Pair<>();
pair.setFirst("Alice");
pair.setSecond(42); // COMPILE ERROR: incompatible types
```
The compiler rejects `42` immediately. The bug never reaches runtime.

**THE INSIGHT:**
Type parameters shift the burden of proof from the developer (manually ensuring every cast is correct) to the compiler (mechanically verifying all assignments). The correctness guarantee is now built into the type system, not maintained by human vigilance.

---

### 🧠 Mental Model / Analogy

> A generic class is like a shipping container template that says "this container holds ONE item type." When you order a "String container," the dock workers know to refuse anything that isn't a string. When you order an "Integer container," integers only. The same container design works for both — only the label changes.

- "Container template" → generic class (`Box<T>`)
- "Item type label" → type parameter (`T` bound to `String` or `Integer`)
- "Dock workers refusing wrong items" → compiler rejecting type mismatches
- "Same container design" → single compiled class file (Type Erasure)

Where this analogy breaks down: Real containers can be relabelled at runtime. Generic type parameters cannot — they are erased at runtime, so a `Box<String>` and `Box<Integer>` are indistinguishable in the JVM heap.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Generics let you say "this list holds only Strings" and have the compiler enforce that rule. Without generics, a list could hold anything and you'd only discover type mistakes when the program crashed.

**Level 2 — How to use it (junior developer):**
Declare generic types with `<T>` syntax: `List<String> names = new ArrayList<>()`. The diamond operator `<>` lets the compiler infer the type from context. For generic methods, declare `<T>` before the return type: `public <T> T identity(T value)`. Avoid raw types (`List` without type parameter) — they disable type checking entirely.

**Level 3 — How it works (mid-level engineer):**
Generics are enforced only at compile time. The compiler inserts casts and checks, then erases the type information: `List<String>` becomes `List` in bytecode. This means you cannot do `new T[]`, `instanceof List<String>`, or `new ArrayList<T>()` inside a generic class body because `T` is unknown at runtime. Use `Class<T>` tokens or `@SuppressWarnings("unchecked")` when you must work around erasure.

**Level 4 — Why it was designed this way (senior/staff):**
Generics were added to Java with backward compatibility as the primary constraint: existing raw-type code (thousands of libraries) had to remain compilable and interoperable. This forced erasure-based generics rather than reified generics (which C# chose). Erasure means the JVM bytecode is unchanged — no new instruction set needed. The downside is loss of runtime type information, wildcards and unbounded type parameters become tricky, and some type-safe patterns (like creating generic arrays) are impossible without unsafe casts. Project Valhalla (ongoing) aims to address this with specialised generics but must still preserve backward compatibility.

---

### ⚙️ How It Works (Mechanism)

Generics work in two phases: **compile-time enforcement** and **erasure**.

**Phase 1 — Type checking:**
The compiler uses the declared type bounds to verify every assignment, method call, and return statement involving a generic type. If you pass a `String` where a `List<Integer>` element is expected, the compiler produces a type error. This is normal static type checking, just parameterised.

**Phase 2 — Erasure:**
After type checking, the compiler replaces all type parameters with their upper bound (`Object` if unbounded, or the first bound in a bounded declaration). It also inserts implicit casts at every point where a generic type is used concretely.

```java
// Source code:
public <T> T identity(T value) { return value; }
String s = identity("hello");

// After erasure (equivalent bytecode):
public Object identity(Object value) { return value; }
String s = (String) identity("hello"); // cast inserted by compiler
```

**Wildcard capture:**
`List<?>` is not the same as `List<Object>`. A `List<?>` is a list of some unknown type — you can read from it (as `Object`) but cannot add elements (except `null`). This is how the compiler enforces read-only safety for covariant use cases.

```
┌────────────────────────────────────────────────┐
│           Generics Erasure Pipeline            │
│                                                │
│  Source: List<String> list                     │
│      ↓ javac type checking                     │
│  Compile-time: enforces String-only ops        │
│      ↓ javac erasure                           │
│  Bytecode: List list (raw)                     │
│      + implicit casts at each usage site       │
│      ↓ JVM runtime                             │
│  No type parameter visible at runtime          │
└────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[Source: List<String> names = new ArrayList<>()] ← YOU ARE HERE
    → [Compiler type-checks all add/get operations]
    → [Erasure: List names = new ArrayList()]
    → [Bytecode with inserted casts]
    → [JVM executes: type parameters invisible]
    → [Runtime: ClassCastException impossible for
       generic operations]
```

**FAILURE PATH:**
```
[Raw type used: List list = new ArrayList()]
    → [Compiler: unchecked warning issued]
    → [Developer ignores warning]
    → [Mixed types added at runtime]
    → [ClassCastException on retrieval]
    → [Stack trace: unhelpful — points to get() call]
```

**WHAT CHANGES AT SCALE:**
At scale, generics have zero runtime cost — erasure means the same bytecode handles all parameterisations. The compile-time savings are amplified: a bug caught in a generic utility class prevents errors across every callsite in a large codebase. The main scaling concern is API design — overly complex generic signatures (multiple bounded wildcards, recursive type parameters) slow compilation and hurt readability.

---

### 💻 Code Example

Example 1 — Basic generic class:
```java
// Generic Pair: holds two values of specified types
public class Pair<A, B> {
    private final A first;
    private final B second;

    public Pair(A first, B second) {
        this.first = first;
        this.second = second;
    }

    public A getFirst() { return first; }
    public B getSecond() { return second; }
}

// Usage — compile-time type safety:
Pair<String, Integer> nameAge = new Pair<>("Alice", 30);
String name = nameAge.getFirst();   // no cast needed
Integer age  = nameAge.getSecond(); // no cast needed
```

Example 2 — Generic method:
```java
// BAD: raw type, no safety, requires cast
public static List findAll(List source, Class type) {
    List result = new ArrayList();
    for (Object o : source)
        if (type.isInstance(o)) result.add(o);
    return result;  // cast required at callsite
}

// GOOD: generic, type-safe, no cast required
public static <T> List<T> findAll(
    List<?> source, Class<T> type
) {
    List<T> result = new ArrayList<>();
    for (Object o : source)
        if (type.isInstance(o)) result.add(type.cast(o));
    return result;  // no cast at callsite
}
```

Example 3 — Bounded type parameters:
```java
// T must extend Comparable<T> to allow sorting
public static <T extends Comparable<T>> T max(
    List<T> items
) {
    T max = items.get(0);
    for (T item : items)
        if (item.compareTo(max) > 0) max = item;
    return max;
}

// Works for any Comparable type:
max(List.of(3, 1, 4, 1, 5));       // Integer
max(List.of("pear", "apple", "cherry")); // String
```

Example 4 — Avoiding raw type warnings:
```java
// BAD: raw type — compiler warning, unsafe
List items = new ArrayList();
items.add("hello");
items.add(42);  // silently added — ClassCastException later

// GOOD: proper parameterisation
List<String> items = new ArrayList<>();
items.add("hello");
// items.add(42);  // COMPILE ERROR — caught immediately
```

---

### ⚖️ Comparison Table

| Approach | Type Safety | Flexibility | Runtime Overhead | Best For |
|---|---|---|---|---|
| **Generics (Java)** | Compile-time | High (wildcards) | Zero (erasure) | All new code |
| Raw types | None | Maximum | None | Legacy interop only |
| Object-based | None | Maximum | Cast cost | Pre-Java 5 code |
| Reified generics (C#) | Compile+Runtime | High | Small overhead | When runtime type needed |

How to choose: Use generics in all new Java code without exception. Use raw types only when integrating with pre-Java-5 libraries. Never use `Object` as a substitute for a proper generic type parameter.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `List<String>` is a subtype of `List<Object>` | Parameterised types are invariant. `List<String>` is NOT a `List<Object>`. You cannot pass `List<String>` where `List<Object>` is expected. Use `List<? extends Object>` or `List<?>` for covariant read-only use |
| Generics work at runtime | Type parameters are erased at runtime. `list instanceof List<String>` is a compile error. At runtime, there is only `List` |
| `new T()` works inside a generic class | You cannot instantiate a type parameter directly (`new T()`). Use a `Supplier<T>` or `Class<T>` factory pattern instead |
| `T[]` is a safe way to create a generic array | Creating generic arrays (`new T[10]`) is unchecked and produces a compiler warning. Use `List<T>` instead, or `(T[]) new Object[10]` with the `@SuppressWarnings("unchecked")` annotation |
| Wildcards (`?`) and type parameters (`T`) are the same | `T` captures a specific type that can be referenced across a method; `?` is an unknown type you cannot refer to by name. `<T> void copy(List<T> src, List<T> dst)` ensures same type; `void print(List<?> list)` accepts any list |

---

### 🚨 Failure Modes & Diagnosis

**Heap Pollution via Raw Types**

**Symptom:**
`ClassCastException` thrown inside JDK library code (e.g., `ArrayList.get()`) with no obvious cast in user code. Stack trace is confusing.

**Root Cause:**
A raw-type `List` was used somewhere in the call chain, allowing elements of the wrong type to be inserted. The cast the compiler inserted (via erasure) fires later when the element is retrieved and the erased cast fails.

**Diagnostic:**
```bash
# Compile with -Xlint:unchecked to catch raw type usage:
javac -Xlint:unchecked MyService.java
# All "unchecked" warnings indicate potential heap pollution sites
```

**Fix:**
```java
// BAD: raw type enables heap pollution
List list = repository.findAll(); // unchecked warning
list.add(new WrongType());        // silently accepted

// GOOD: parameterised type prevents insertion
List<PaymentEvent> events = repository.findAll();
// events.add(new WrongType()); // COMPILE ERROR
```

**Prevention:** Enable `-Xlint:unchecked` in your build and treat all unchecked warnings as errors.

---

**Unchecked Cast Suppression Hiding Real Bugs**

**Symptom:**
`@SuppressWarnings("unchecked")` scattered throughout the codebase. Occasional `ClassCastException` at runtime that's hard to trace.

**Root Cause:**
Developers suppress the unchecked cast warning without understanding why the cast is safe, masking genuine type errors.

**Diagnostic:**
```bash
grep -rn "@SuppressWarnings.*unchecked" --include="*.java" .
# Review each site: is the cast provably safe?
```

**Fix:**
```java
// BAD: blind suppression
@SuppressWarnings("unchecked")
List<String> names = (List<String>) cache.get("names");

// GOOD: validate before cast, or use typed API
Object cached = cache.get("names");
if (cached instanceof List<?> list) {
    // Java 16+ pattern matching instanceof
    List<String> names = list.stream()
        .filter(String.class::isInstance)
        .map(String.class::cast)
        .collect(toList());
}
```

**Prevention:** Use a generic cache interface (`Cache<K,V>`) rather than `Cache<String, Object>`.

---

**Invariance Surprise — Cannot Pass `List<Subtype>` as `List<Supertype>`**

**Symptom:**
Compile error "incompatible types: `List<Dog>` cannot be converted to `List<Animal>`" despite `Dog extends Animal`.

**Root Cause:**
Parameterised types are invariant. If `List<Dog>` were a `List<Animal>`, you could add a `Cat` via the `Animal` reference, corrupting the `Dog` list.

**Diagnostic:**
```bash
# javac error: incompatible types
javac -verbose MyApp.java 2>&1 | grep "incompatible"
```

**Fix:**
```java
// BAD: fails to compile
void processAnimals(List<Animal> animals) { ... }
processAnimals(new ArrayList<Dog>()); // ERROR

// GOOD: use upper-bounded wildcard
void processAnimals(List<? extends Animal> animals) { ... }
processAnimals(new ArrayList<Dog>());  // OK
```

**Prevention:** Use `? extends T` for read-only collection parameters, `? super T` for write-only collection parameters (Producer Extends, Consumer Super — PECS rule).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Type Systems (Static vs Dynamic)` — generics are a compile-time static typing feature; understanding type systems explains why type safety matters
- `Inheritance` — generics interact with inheritance via wildcards and bounded type parameters; understanding the class hierarchy is prerequisite
- `Autoboxing / Unboxing` — generic collections use wrapper types; autoboxing makes primitives work with generics transparently

**Builds On This (learn these next):**
- `Type Erasure` — the mechanism that implements generics on the JVM; explains all the surprising limitations of generics
- `Bounded Wildcards` — extends generics with `? extends T` and `? super T` for flexible covariant and contravariant use
- `Stream API` — heavily uses generics; understanding generics makes Stream types comprehensible

**Alternatives / Comparisons:**
- `Covariance / Contravariance` — the broader theory behind why generic wildcards work the way they do
- `Reflection` — can work with generic types at runtime via `ParameterizedType`, but loses compile-time safety

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Compile-time type parameterisation for    │
│              │ classes, interfaces, and methods          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Raw Object collections caused             │
│ SOLVES       │ ClassCastException at runtime             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Type parameters are ERASED at runtime —  │
│              │ safety is compile-time only               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Writing reusable containers, utilities,   │
│              │ or algorithms that work for any type      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ You need runtime type info (use           │
│              │ Class<T> token or instanceof instead)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Compile-time safety vs no runtime type   │
│              │ info (erasure); invariance surprises      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Write once, type-check for every type"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Type Erasure → Bounded Wildcards →        │
│              │ Covariance / Contravariance               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a method `public static <T> void swap(List<T> list, int i, int j)` that swaps two elements. A colleague points out that `public static void swap(List<?> list, int i, int j)` would also compile. Trace exactly what happens inside each version when you try to implement the swap using a temporary variable — specifically, at which line does each version fail to compile and why, and which signature is actually implementable?

**Q2.** Java arrays are covariant: `String[] sa = new String[1]; Object[] oa = sa; oa[0] = 42;` compiles but throws `ArrayStoreException` at runtime. Java generic collections are invariant: `List<String> ls = new ArrayList<>(); List<Object> lo = ls;` fails at compile time. Both approaches were language design choices. Explain the precise trade-off each approach makes between compile-time safety and runtime safety, and why the Java team made different choices for arrays versus generics.

