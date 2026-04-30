---
layout: default
title: "Covariance / Contravariance"
parent: "Java Language"
nav_order: 56
permalink: /java-language/covariance-contravariance/
number: "056"
category: Java Language
difficulty: ★★★
depends_on: Generics, Bounded Wildcards, Subtyping
used_by: Comparable, Comparator, Collections API, TypeScript Variance
tags: #java #advanced #generics #variance #covariance
---

# 056 — Covariance / Contravariance

`#java` `#advanced` `#generics` `#variance` `#covariance`

⚡ TL;DR — Covariance (out/extends) means subtype flows out safely; contravariance (in/super) means supertype flows in safely; Java arrays are covariant (broken), generics are invariant by default.

| #056 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Generics, Bounded Wildcards, Subtyping | |
| **Used by:** | Comparable, Comparator, Collections API, TypeScript Variance | |

---

### 📘 Textbook Definition

**Variance** describes how subtyping of parameterized types relates to subtyping of their type arguments. A type constructor `F<T>` is:
- **Covariant** in T: If `A <: B` then `F<A> <: F<B>` — subtypes stay subtypes (`? extends`)
- **Contravariant** in T: If `A <: B` then `F<B> <: F<A>` — direction flips (`? super`)
- **Invariant** in T: `F<A>` and `F<B>` are unrelated regardless of A vs B (Java generics default)

---

### 🟢 Simple Definition (Easy)

- **Covariant**: A `List<Dog>` can be treated as a `List<? extends Animal>` — safe to **read** Animals out.
- **Contravariant**: A `Comparator<Animal>` can be used as a `Comparator<? super Dog>` — can **compare** any Dog.
- **Invariant**: `List<Dog>` cannot be assigned to `List<Animal>` — they are completely unrelated.

---

### 🔵 Simple Definition (Elaborated)

Java arrays are **covariant** (design mistake): `Dog[]` is a `Animal[]`. This is type-unsafe — you can write a Cat into a Dog[] through an Animal[] reference. Java generics are deliberately **invariant** to prevent this. Wildcards (`extends`/`super`) opt into covariance/contravariance explicitly where needed.

---

### 🔩 First Principles Explanation

```
Subtype relationship: Integer <: Number <: Object

COVARIANT (producer / output):
  List<Integer> <: List<? extends Number>
  Reason: only reading → you get a Number, which IS-A Number ✓
  Rule: safe when the type only appears as a RETURN type

CONTRAVARIANT (consumer / input):
  List<Number> <: List<? super Integer>
  Reason: only writing Integer → Number container accepts Integer ✓
  Rule: safe when the type only appears as a PARAMETER type

INVARIANT (both read and write):
  List<Integer> is NOT related to List<Number>
  Reason: if we allow both read+write we break type safety:
    List<Number> nums = new ArrayList<Integer>(); // if allowed…
    nums.add(3.14);  // writes Double into Integer list → CRASH

Arrays covariance (broken):
  Number[] nums = new Integer[5];  // compiles
  nums[0] = 3.14;  // ArrayStoreException at RUNTIME — not compile time
  // This is why arrays are considered a design flaw
```

---

### ❓ Why Does This Exist (Why Before What)

Without variance, generics would be completely rigid. You couldn't write a `max()` method that works for any `Comparable` subtype, or a sort that accepts any `Comparator` of supertypes. Variance is what makes generic APIs composable and reusable.

---

### 🧠 Mental Model / Analogy

> Think of variance in terms of **vending machines**:
> **Covariant (extends)** = a machine that only **dispenses** items. If it dispenses Dogs, you can use it wherever Animal dispensers are expected.
> **Contravariant (super)** = a machine that only **accepts** items. If it accepts Animals, you can use it wherever Dog-acceptors are needed (Dogs are Animals).
> **Invariant** = a machine that both accepts and dispenses. Must be exact — Dog-in/Dog-out only.

---

### ⚙️ How It Works (Mechanism)

```
Java variance summary:

Arrays:         covariant (Dog[] is Animal[]) — runtime ArrayStoreException possible
Generic params: invariant by default (List<Dog> is NOT List<Animal>)
Wildcards:
  ? extends T   covariant position  (read/output)
  ? super T     contravariant position (write/input)
  ?             bivariant (no read or write of typed value)

Declaration-site variance (Kotlin / Scala):
  // Java needs use-site variance (at each usage)
  // Kotlin: out T = covariant, in T = contravariant
  interface Source<out T> { fun next(): T }        // Kotlin covariant
  interface Sink<in T>    { fun put(item: T) }     // Kotlin contravariant
```

---

### 🔄 How It Connects (Mini-Map)

```
[Subtyping: Dog <: Animal]
       │
       ▼
[Variance rule applied to generic F<T>]
       │
       ├─► Covariant F<Dog> <: F<Animal>  →  ? extends Animal
       ├─► Contravariant F<Animal> <: F<Dog> → ? super Dog
       └─► Invariant: unrelated             →  F<T> (default generics)
```

---

### 💻 Code Example

```java
// 1. Array covariance — compiles, crashes at runtime
Animal[] animals = new Dog[3];  // covariant: Dog[] is Animal[]
animals[0] = new Cat();         // ArrayStoreException at runtime!

// 2. Generic invariance — compile error (safe)
List<Animal> animals2 = new ArrayList<Dog>();  // COMPILE ERROR
// Cannot assign List<Dog> to List<Animal>

// 3. Using covariant wildcard (extends) for reading
List<Dog> dogs = List.of(new Dog(), new Dog());
List<? extends Animal> animals3 = dogs;   // ✓ covariant
Animal a = animals3.get(0);               // ✓ safe read
// animals3.add(new Dog());               // COMPILE ERROR — no writes

// 4. Using contravariant wildcard (super) for writing
List<Animal> animalList = new ArrayList<>();
List<? super Dog> sink = animalList;      // ✓ contravariant
sink.add(new Dog());                      // ✓ safe write
// Dog d = sink.get(0);                   // COMPILE ERROR — only Object

// 5. Comparator is contravariant — canonical example
Comparator<Animal> byWeight = Comparator.comparing(Animal::getWeight);
Comparator<? super Dog> dogComparator = byWeight;  // ✓ contravariant
// A comparator that orders Animals can also order Dogs
dogs.sort(byWeight);                      // compiles with <? super Dog>

// 6. Real-world: Collections.sort
public static <T extends Comparable<? super T>> void sort(List<T> list)
// T must be Comparable to T or any supertype — contravariant compareTo
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Java generics are covariant | Invariant by default — requires `? extends` for covariance |
| Arrays being covariant is correct design | No — it's a known flaw that allows `ArrayStoreException` at runtime |
| Contravariance is unusual or rare | Every `Comparator<? super T>` and `Predicate<? super T>` uses it |
| Variance is a complex academic topic | It's the rule behind PECS; understanding it makes API design intuitive |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Arrays vs Lists — different safety guarantees**
```java
String[] strs = new String[3];
Object[] objs = strs;       // covariant — compiles
objs[0] = 42;               // ArrayStoreException at runtime!

List<String> strList = new ArrayList<>();
List<Object> objList = strList;  // COMPILE ERROR — safe!
```
Rule: prefer `List<T>` over `T[]` in API boundaries.

**Pitfall 2: Incorrect bound direction**
```java
// Trying to write to a covariant wildcard
void fillList(List<? extends Number> list, Number n) {
    list.add(n);  // COMPILE ERROR — can't write to extends wildcard
}
// Fix: change to List<? super Number> if you need to write
```

---

### 🔗 Related Keywords

- **Generics (#053)** — the parameterization system variance operates on
- **Bounded Wildcards (#055)** — `? extends` (covariant) and `? super` (contravariant)
- **Comparable / Comparator** — canonical examples of contravariance in JDK
- **Kotlin/Scala variance** — declaration-site `in`/`out` vs Java's use-site wildcards
- **PECS** — the practical rule that encodes variance for Collections use

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Covariant = safe to produce/read (extends)    │
│              │ Contravariant = safe to consume/write (super) │
│              │ Invariant = default; both directions forbidden │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Designing generic APIs; understanding why     │
│              │ List<Dog> ≠ List<Animal>                      │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — always applies; use wildcards explicitly │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Out = covariant (extends); In = contravariant │
│              │  (super); both = invariant (exact type)"      │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Wildcards → Comparator design → Kotlin │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** Why does `String[]` being assignable to `Object[]` create a runtime safety hole that `List<String>` → `List<Object>` does not?
**Q2.** Given `class Animal` and `class Dog extends Animal`, which of these compiles: `Comparator<Animal> c = (a,b) -> 0; dogs.sort(c);`?
**Q3.** What is declaration-site variance (Kotlin `out`/`in`) and how does it differ from Java's use-site wildcards?

