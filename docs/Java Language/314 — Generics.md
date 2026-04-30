---
layout: default
title: "Generics"
parent: "Java Language"
nav_order: 314
permalink: /java-language/generics/
---
# 314 — Generics

`#java` `#intermediate` `#generics` `#typesystem`

⚡ TL;DR — Compile-time type parameters that eliminate casts, prevent ClassCastException at runtime, and allow reusable, type-safe data structures and algorithms.

| #314 | category: Java Language
|:---|:---|:---|
| **Depends on:** | Type System, Object, Collections | |
| **Used by:** | Collections Framework, Streams API, Optional, Spring Framework | |

---

### 📘 Textbook Definition

Generics enable types (classes and interfaces) to be parameterized — you write code that works with different types while retaining type safety checked at compile time. Introduced in Java 5, they are implemented via **type erasure**: the compiler enforces type constraints and then removes the type information, producing the same bytecode as pre-generics code.

---

### 🟢 Simple Definition (Easy)

Generics let you write a `Box<T>` once and use it as `Box<String>`, `Box<Integer>`, or `Box<MyClass>` — the compiler checks you put the right thing in and you never need to cast when taking it out.

---

### 🔵 Simple Definition (Elaborated)

Before generics (Java 1.4), `List` stored `Object` and every retrieval required an explicit cast — which could fail at runtime. Generics move that error to **compile time**: `List<String>` tells the compiler every element is a `String`, so no cast is needed and a wrong type inserted is caught immediately. The cost: type info is erased at runtime (see Type Erasure #054).

---

### 🔩 First Principles Explanation

**The core problem:**
```
// Pre-generics: ClassCastException waiting to happen
List names = new ArrayList();
names.add("Alice");
names.add(42);             // compiles fine!
String s = (String) names.get(1); // runtime CRASH
```

**The insight:**
> "If we can tell the compiler what type a container holds, it can reject wrong insertions at compile time and eliminate casts at retrieval."

```
// With generics: compiler catches the error
List<String> names = new ArrayList<>();
names.add("Alice");
names.add(42);        // COMPILE ERROR: incompatible types
String s = names.get(0);  // no cast needed, always safe
```

---

### ❓ Why Does This Exist (Why Before What)

Runtime `ClassCastException` is the worst kind of bug — invisible until code runs in production. Generics turn a runtime crash into a compile-time error. They also eliminate cast noise, making code cleaner and expressing intent clearly.

---

### 🧠 Mental Model / Analogy

> Generics are like a typed filing cabinet. A plain `List` is an unlabelled drawer — you can put anything in, but when you reach in, you don't know what you'll find. A `List<String>` is a drawer labelled "Strings only" — the clerk (compiler) rejects anything else, and you always know exactly what you're getting.

---

### ⚙️ How It Works (Mechanism)

```
Generic constructs:

1. Generic class / interface
   class Box<T> { T value; }
   interface Comparable<T> { int compareTo(T other); }

2. Generic method
   <T> T first(List<T> list) { return list.get(0); }

3. Bounded type parameter
   <T extends Comparable<T>> T max(T a, T b) { ... }
   // T must implement Comparable<T>

4. Multiple bounds
   <T extends Serializable & Cloneable> ...

5. Wildcard (see #055)
   List<? extends Number>  // read-only view of Number subtypes
   List<? super Integer>   // writable for Integer and subtypes

Type inference (Java 7+ diamond):
   Box<String> b = new Box<>();  // compiler infers String
```

---

### 🔄 How It Connects (Mini-Map)

```
[Generics] ──defines type params──► [Type Parameter T, E, K, V]
    │                                        │
    ├── erased at compile time ──────────► [Type Erasure #054]
    │                                        │
    ├── wildcards ──────────────────────► [Bounded Wildcards #055]
    │
    └── covariance/invariance ──────────► [Covariance/Contravariance #056]
```

---

### 💻 Code Example

```java
// 1. Generic class
class Box<T> {
    private T value;
    public Box(T value) { this.value = value; }
    public T get() { return value; }
}

Box<String>  strBox = new Box<>("hello");  // T = String
Box<Integer> intBox = new Box<>(42);       // T = Integer
String s = strBox.get();      // no cast
Integer i = intBox.get();     // no cast

// 2. Generic method — works on any Comparable type
public static <T extends Comparable<T>> T max(T a, T b) {
    return (a.compareTo(b) >= 0) ? a : b;
}
String  sm = max("apple", "banana");  // returns "banana"
Integer im = max(10, 20);             // returns 20

// 3. Generic interface — implement Comparable for your type
class Temperature implements Comparable<Temperature> {
    double celsius;
    public int compareTo(Temperature other) {
        return Double.compare(this.celsius, other.celsius);
    }
}

// 4. Pair utility class
class Pair<A, B> {
    final A first;
    final B second;
    Pair(A first, B second) { this.first = first; this.second = second; }
    static <A,B> Pair<A,B> of(A a, B b) { return new Pair<>(a, b); }
}
Pair<String, Integer> p = Pair.of("age", 30);
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Generics work at runtime | Type info is erased — `List<String>` is just `List` at runtime |
| `List<Dog>` is a `List<Animal>` | Generics are invariant — use wildcards for variance |
| Can create generic arrays: `new T[10]` | Illegal — type erasure makes this unsafe |
| `instanceof` works with generics | `list instanceof List<String>` is illegal due to erasure |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Raw types**
```java
List list = new ArrayList();  // raw type — bypasses all generics safety
list.add("hello");
list.add(42);                 // compiles! no protection
```
Fix: always parameterize. Enable `-Xlint:unchecked` compiler warning.

**Pitfall 2: Unchecked cast from raw types**
```java
List raw = getSomeLegacyList();
List<String> typed = (List<String>) raw;  // compiles with warning
typed.get(0);  // may throw ClassCastException if raw contained non-String
```
Fix: validate elements before casting; wrap legacy code at boundaries.

**Pitfall 3: Cannot use primitives**
```java
List<int> list = ...  // COMPILE ERROR — must use Integer
```
Fix: use wrapper types (`Integer`, `Long`), accept autoboxing overhead.

---

### 🔗 Related Keywords

- **Type Erasure (#054)** — why generic type info disappears at runtime; root of all generic limitations
- **Bounded Wildcards (#055)** — `? extends T` / `? super T` — real-world generics flexibility
- **Covariance/Contravariance (#056)** — why `List<Dog>` is NOT a `List<Animal>`
- **Collections Framework** — the primary consumer of generics in Java
- **Reflection** — required to recover some type info at runtime (via `ParameterizedType`)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Type-safe parameterization at compile time;   │
│              │ erased to Object at runtime                   │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Creating reusable containers, algorithms,     │
│              │ utility classes that work with any type       │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Raw types (legacy) — always parameterize      │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Write once; compile-time safety for all types│
│              │  — no casts, no ClassCastException"           │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Type Erasure → Bounded Wildcards → PECS       │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** Why can't you write `new T[10]` inside a generic class, even though `T` feels like a type at compile time?
**Q2.** What is the "diamond problem" that the diamond operator `<>` (Java 7) solves?
**Q3.** Why is `List<Dog>` not assignable to `List<Animal>`, even though `Dog extends Animal`?

