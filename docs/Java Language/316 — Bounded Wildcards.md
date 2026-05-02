---
layout: default
title: "Bounded Wildcards"
parent: "Java Language"
nav_order: 316
permalink: /java-language/bounded-wildcards/
number: "0316"
category: Java Language
difficulty: ★★★
depends_on: Generics, Type Erasure, Covariance / Contravariance, Inheritance
used_by: Stream API, Collections Framework
related: Generics, Type Erasure, Covariance / Contravariance
tags:
  - java
  - generics
  - type-safety
  - deep-dive
  - advanced
---

# 0316 — Bounded Wildcards

⚡ TL;DR — Bounded wildcards (`? extends T` and `? super T`) break the invariance of generic types, letting you safely read from a producer or write to a consumer — summarised by the PECS rule: Producer Extends, Consumer Super.

| #0316 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Generics, Type Erasure, Covariance / Contravariance, Inheritance | |
| **Used by:** | Stream API, Collections Framework | |
| **Related:** | Generics, Type Erasure, Covariance / Contravariance | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Generic types in Java are invariant: `List<Dog>` is NOT a `List<Animal>`, even though `Dog extends Animal`. This is correct for safety (you can't allow writing a `Cat` into a `List<Dog>`), but it makes reusable utility methods impossible. A method `void printAll(List<Animal> animals)` cannot be called with a `List<Dog>` — even though printing is read-only and perfectly safe.

**THE BREAKING POINT:**
A zoo application's `AnimalShelter` class has 20 methods that iterate collections: `printAnimals()`, `countHealthy()`, `findOldest()`, `exportToCsv()`. Without wildcards, every method must be duplicated for every animal subtype: `printDogs()`, `printCats()`, `printBirds()`. Adding a new animal type requires updating 20 methods. This is combinatorial explosion.

**THE INVENTION MOMENT:**
This is exactly why **Bounded Wildcards** were created — to express "I only need to read from this collection" (`? extends T`) or "I only need to write into this collection" (`? super T`), allowing reuse across related types while the compiler enforces exactly which operations are safe.

---

### 📘 Textbook Definition

**Bounded Wildcards** are generic type arguments of the form `? extends T` (upper-bounded) and `? super T` (lower-bounded) that relax the invariance of Java's parameterised types. An upper-bounded wildcard `List<? extends Animal>` accepts a `List<Dog>`, `List<Cat>`, or any `List<SubtypeOfAnimal>` — the collection can be read as `Animal` but nothing can be added (except `null`). A lower-bounded wildcard `List<? super Dog>` accepts `List<Dog>`, `List<Animal>`, or `List<Object>` — elements can be added as `Dog` but elements can only be read as `Object`. The unbounded wildcard `List<?>` is equivalent to `List<? extends Object>`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`? extends T` means "a list I can read from as T"; `? super T` means "a list I can write T into."

**One analogy:**
> A one-way revolving door is either "enter-only" or "exit-only." A producer (extends) is an exit door — things come out (reads). A consumer (super) is an enter door — things go in (writes). You can't both enter and exit through the same revolving door at the same time.

**One insight:**
The PECS rule — **P**roducer **E**xtends, **C**onsumer **S**uper — is the complete mental model. If a collection produces values you consume (you read from it), use `? extends`. If a collection consumes values you produce (you write into it), use `? super`. If you both read and write, use the exact type.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. `List<? extends T>` is covariant: safe to read elements as `T`, unsafe to write (you don't know the exact subtype).
2. `List<? super T>` is contravariant: safe to write `T` elements in, unsafe to read other than as `Object` (you don't know the exact supertype).
3. If you need both reads and writes of a specific type, use `List<T>` — the invariant form.

**DERIVED DESIGN:**
Why can't you add to `List<? extends Animal>`? Say it holds a `List<Dog>` at runtime. If you could add a `Cat`, you'd corrupt the `Dog` list. The compiler prevents this by making the element type for writes of `List<? extends Animal>` be the capture of the unknown subtype — and since the precise subtype is unknown, no concrete type (except `null`) satisfies it.

Why can you add `Dog` to `List<? super Dog>`? Say it holds a `List<Animal>`. Adding a `Dog` is safe because `Dog` is-a `Animal`. Reading back as `Object` is safe because everything is-an `Object`. But reading as `Animal` is NOT guaranteed safe — the list might actually be a `List<Object>`, not a `List<Animal>`.

```
┌────────────────────────────────────────────────┐
│         Wildcard Capability Matrix             │
│                                                │
│              READ as T    WRITE T              │
│  List<T>       ✓           ✓                  │
│  List<? ext T> ✓           ✗ (unknown subtype)│
│  List<? sup T> ✗ (→Object) ✓                  │
│  List<?>       ✗ (→Object) ✗                  │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Enables covariant and contravariant use of generic collections without sacrificing type safety.
**Cost:** Wildcard types are harder to read; wildcards cannot be combined arbitrarily; wildcard capture creates complex compiler error messages that confuse developers.

---

### 🧪 Thought Experiment

**SETUP:**
A `copy(source, destination)` method that copies elements from one list to another. Both lists hold some type of `Number`.

**WHAT HAPPENS WITHOUT BOUNDED WILDCARDS:**
```java
void copy(List<Number> src, List<Number> dst) {
    dst.addAll(src);
}
// Cannot call: copy(integers, numbers)
// where integers is List<Integer> — type mismatch
```
The method is useless for subtypes.

**WHAT HAPPENS WITH BOUNDED WILDCARDS:**
```java
void copy(
    List<? extends Number> src,  // producer: we read
    List<? super Number> dst     // consumer: we write
) {
    for (Number n : src) dst.add(n);
}
// Can call:
copy(intList, numberList);   // OK
copy(doubleList, objectList); // OK
copy(floatList, numberList);  // OK
```

**THE INSIGHT:**
By separating the concerns of reading (extends) and writing (super), the method becomes maximally flexible while the compiler still prevents `dst.add("hello")` — a String is not a Number.

---

### 🧠 Mental Model / Analogy

> Think of `? extends T` as a read-only dispensing machine for type T: guaranteed to give you T, won't take anything back. Think of `? super T` as a deposit slot accepting T: you can drop T in, but what you get back is just "stuff" (Object).

- "Dispensing machine for T" → `List<? extends T>` — `get()` returns T, `add()` rejected.
- "Deposit slot accepting T" → `List<? super T>` — `add(T)` accepted, `get()` returns Object.
- "Two-way exchange counter" → `List<T>` — both get and add work with exact type T.

Where this analogy breaks down: In reality you can call `add(null)` on a `List<? extends T>` — null is the one value without a type. The analogy treats the dispensing machine as absolutely read-only, which is not quite true.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A wildcard says "I don't know exactly which type, but I know it's related to T." The `extends` version says "it's T or something more specific." The `super` version says "it's T or something more general." This flexibility lets you write methods that work for a whole family of types.

**Level 2 — How to use it (junior developer):**
Apply PECS: if a parameter provides data to your method (you call `.get()` on it), use `? extends T`. If a parameter receives data from your method (you call `.add()` on it), use `? super T`. If you do both, use `T` exactly. Common examples: `Collections.sort(List<T> list, Comparator<? super T> c)` — the comparator consumes T, so `? super T`.

**Level 3 — How it works (mid-level engineer):**
Wildcard capture is the compiler mechanism behind wildcards. When you write `List<? extends Number> list`, the compiler creates a fresh type variable (call it `CAP#1 extends Number`) and treats `list` as `List<CAP#1>`. For reads, `CAP#1 extends Number` so the result can be upcast to `Number`. For writes, the only concrete type satisfying `CAP#1` is `null` — hence writes are rejected. This is formal subtyping: `List<? extends T>` is a supertype of `List<X>` for any `X extends T`.

**Level 4 — Why it was designed this way (senior/staff):**
Wildcards were designed to solve the use-site variance problem that erasure introduced. In a reified-generics language (like C#), you can declare covariance/contravariance on the type declaration itself (`IEnumerable<out T>`, `IComparable<in T>`). Java uses use-site variance instead — you specify the variance at the point of use, not declaration. This is more flexible (the same `List<T>` can be used covariantly in one context and contravariantly in another) but more verbose and Error-prone. The complexity is the price of erasure-based backwards compatibility.

---

### ⚙️ How It Works (Mechanism)

**Upper-bounded wildcard: `? extends T`**

When the compiler sees `List<? extends Number>`:
1. Creates a fresh capture type: `CAP#1 extends Number`.
2. Element read type: `CAP#1` — assignable to `Number` by subtype relation.
3. Element write type: must be a subtype of `CAP#1` — since `CAP#1` is unknown, only `null` qualifies.

```java
List<? extends Number> numbers = getNumbers();
Number n = numbers.get(0);   // OK: CAP#1 → Number
// numbers.add(42);           // ERROR: CAP#1 unknown
// numbers.add((Number) 3.14);// ERROR: same reason
numbers.add(null);           // OK: null has no type
```

**Lower-bounded wildcard: `? super T`**

When the compiler sees `List<? super Integer>`:
1. Creates a fresh capture type: `CAP#2 super Integer`.
2. Element write type: `Integer` — is-a CAP#2 by supertype relation.
3. Element read type: `Object` — the only guaranteed upper bound of CAP#2.

```java
List<? super Integer> container = getContainer();
container.add(42);       // OK: Integer is-a CAP#2
container.add(100);      // OK: Integer is-a CAP#2
Object obj = container.get(0);  // OK as Object only
// Integer i = container.get(0); // ERROR: might be Number
```

**Wildcard capture helper pattern:**
When you need to work with a wildcard type by name:
```java
// Cannot compile: ? has no name
public void swap(List<?> list, int i, int j) {
    list.set(i, list.set(j, list.get(i))); // ERROR
}

// Fix: capture helper method names the wildcard
public void swap(List<?> list, int i, int j) {
    swapHelper(list, i, j);
}
private <T> void swapHelper(List<T> list, int i, int j) {
    list.set(i, list.set(j, list.get(i))); // OK
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (PECS copy example):
```
[Source: List<Integer> ints]
    → [Passed as List<? extends Number>]
    → [Compiler: CAP#1 extends Number]   ← YOU ARE HERE
    → [Read: Number n = ints.get(i) OK]
    → [Write rejected by compiler]
    → [Elements safely read as Number]
    → [Destination: List<? super Number>]
    → [Write: dst.add(n) OK]
    → [Read restricted to Object]
```

**FAILURE PATH:**
```
[Developer forgets PECS, uses List<Number> both src/dst]
    → [List<Integer> cannot be passed as List<Number>]
    → [Compile error: incompatible types]
    → [Fix: add wildcards to signature]
```

**WHAT CHANGES AT SCALE:**
In large codebases, wildcards appear extensively in utility APIs (`Collections`, `Stream`, `Comparator`). Misapplication of PECS is a frequent code smell — either missing wildcards (overly restrictive API) or wildcards in both positions on the same parameter (sign of design confusion). Code reviews should flag methods that accept `List<T>` when they only read, because this unnecessarily restricts callers.

---

### 💻 Code Example

Example 1 — Upper wildcard for read-only iteration:
```java
// BAD: only accepts List<Number>, not List<Integer>
double sum(List<Number> numbers) {
    return numbers.stream()
        .mapToDouble(Number::doubleValue)
        .sum();
}

// GOOD: accepts List<Integer>, List<Double>, etc.
double sum(List<? extends Number> numbers) {
    return numbers.stream()
        .mapToDouble(Number::doubleValue)
        .sum();
}
// sum(List.of(1, 2, 3))   OK (Integer)
// sum(List.of(1.5, 2.5))  OK (Double)
```

Example 2 — Lower wildcard for accumulation into a collection:
```java
// Drain items from a source into a wider-type destination
void drain(
    Queue<Integer> source,
    Collection<? super Integer> drain
) {
    while (!source.isEmpty()) {
        drain.add(source.poll());
    }
}

Queue<Integer> q = new LinkedList<>(List.of(1,2,3));
List<Number>  numbers = new ArrayList<>();
List<Object>  objects = new ArrayList<>();
drain(q, numbers);  // OK: Number super Integer
q = new LinkedList<>(List.of(4,5,6));
drain(q, objects);  // OK: Object super Integer
```

Example 3 — Classic PECS: `copy` method (JDK Collections.copy inspired):
```java
// Producer Extends, Consumer Super
public static <T> void copy(
    List<? extends T> src,  // produces T — use extends
    List<? super T> dest    // consumes T — use super
) {
    for (T item : src) dest.add(item);
}

List<Integer> ints = List.of(1, 2, 3);
List<Number>  nums = new ArrayList<>();
copy(ints, nums); // T=Integer; src=List<Integer>,
                  // dest=List<Number> (Number super Integer)
```

Example 4 — Unbounded wildcard for type-agnostic methods:
```java
// Only need list size and class — don't care about element type
void printMetadata(List<?> list) {
    System.out.println("Size: " + list.size());
    System.out.println("Class: " + list.getClass());
    // Cannot add elements (except null)
    // Cannot read as any specific type (only Object)
}
```

---

### ⚖️ Comparison Table

| Wildcard Form | Readable As | Writable With | Accepts | Use When |
|---|---|---|---|---|
| `List<T>` | T | T | `List<T>` only | Read and write same type |
| **`List<? extends T>`** | T | null only | Any `List<X extends T>` | Read-only / producer |
| `List<? super T>` | Object only | T | Any `List<X super T>` | Write-only / consumer |
| `List<?>` | Object only | null only | Any `List` | Type-agnostic operations |

How to choose: Apply PECS. If your method only reads from the collection, use `? extends T`. If it only writes, use `? super T`. If it does both, use the exact generic type `T`. If the element type is irrelevant to your method, use `?`.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| You can add to `List<? extends Animal>` if you have an Animal | You cannot — the compiler rejects all adds except null because the exact subtype is unknown. If the list happens to be `List<Dog>`, adding a `Cat` would be a type violation |
| `List<?>` means a list of anything | `List<?>` means a list of ONE unknown type. You cannot add elements (only null), and reads return Object. It's not a free-for-all — it's a type-safe unknown |
| Lower-bounded wildcards (`? super T`) are less common so less important | `? super T` appears in every `Comparator` usage: `Comparator<? super T>` is the correct type for a comparator passed to a sort of `List<T>`. Misusing `Comparator<T>` breaks callers with subtypes |
| PECS only applies to Collection parameters | PECS applies to any generic producer/consumer relationship. `Function<? super T, ? extends R>` follows PECS: the function consumes T (input), produces R (output) |
| Wildcards can be nested arbitrarily | Wildcards cannot be nested: `List<List<?>>` is valid but `List<? extends List<?>>` creates complex wildcard capture chains that are rarely correct and always confusing |
| `? extends Object` and `?` are different | They are semantically identical. `List<?>` is shorthand for `List<? extends Object>` |

---

### 🚨 Failure Modes & Diagnosis

**API Too Restrictive — Missing extends on Producer Parameter**

**Symptom:**
Callers constantly get "incompatible types" compile errors when passing lists of subtypes. Team duplicates methods for every subtype.

**Root Cause:**
Method signature uses exact `List<T>` for a parameter that is only read. This forces callers to convert lists, duplicating data unnecessarily.

**Diagnostic:**
```bash
# Search for methods that accept List<ConcreteType> but
# only call read operations (no add/set/remove):
grep -rn "List<[A-Z]" --include="*.java" . | \
  grep -v "? extends"
# Review each callsite: does it need write access?
```

**Fix:**
```java
// BAD: restricts to exact list type
void display(List<Animal> animals) {
    animals.forEach(a -> System.out.println(a.name()));
}

// GOOD: works for any Animal subtype list
void display(List<? extends Animal> animals) {
    animals.forEach(a -> System.out.println(a.name()));
}
```

**Prevention:** Code review rule — any method parameter that is a `List<ConcreteType>` and never modified should become `List<? extends ConcreteType>`.

---

**Wildcard Capture Failure — Cannot Assign Wildcard Read to Typed Variable**

**Symptom:**
Compiler error "incompatible types: CAP#1 cannot be converted to T" when trying to use an element read from a `List<?>` in a typed context.

**Root Cause:**
Wildcard capture creates a fresh unnamed type `CAP#1` that cannot be assigned to a named type variable. The fix requires a capture helper.

**Diagnostic:**
```bash
# Compiler message like:
# error: incompatible types: CAP#1 cannot be converted to T
# where CAP#1 is a fresh type-variable
```

**Fix:**
```java
// BAD: cannot swap on List<?>
void swap(List<?> list, int i, int j) {
    Object temp = list.get(i);
    list.set(i, list.get(j));   // ERROR: CAP vs CAP
    list.set(j, temp);          // ERROR: Object vs CAP
}

// GOOD: capture helper names the wildcard
void swap(List<?> list, int i, int j) {
    swapCapture(list, i, j);
}
private <E> void swapCapture(
    List<E> list, int i, int j
) {
    E temp = list.get(i);
    list.set(i, list.get(j));
    list.set(j, temp);
}
```

**Prevention:** When you need to use an element read from a wildcard list in a write operation on the same list, always use a capture helper method.

---

**Comparator Type Mismatch Surprise**

**Symptom:**
`Collections.sort(List<Dog> dogs, Comparator<Animal> byAge)` fails to compile with "wrong first argument type."

**Root Cause:**
`Collections.sort` signature is `sort(List<T> list, Comparator<? super T> c)`. The actual wildcard `? super Dog` accepts `Comparator<Dog>`, `Comparator<Animal>`, `Comparator<Object>`. The error occurs when the sort method is misread as requiring `Comparator<T>` exactly.

**Diagnostic:**
```bash
# Read the actual JDK signature:
javap java.util.Collections | grep "sort"
# public static <T> void sort(
#   java.util.List<T>,
#   java.util.Comparator<? super T>)
```

**Fix:**
```java
// This WORKS even though comparator is Comparator<Animal>
// because Animal super Dog satisfies ? super Dog
Comparator<Animal> byAge = Comparator.comparingInt(
    Animal::getAge
);
List<Dog> dogs = getDogs();
dogs.sort(byAge);  // OK — PECS: Dog consumer super Dog
```

**Prevention:** Prefer lambda or method reference comparators (`Comparator.comparing(Dog::getName)`) which let the compiler infer types correctly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Generics` — bounded wildcards are an extension of generics; understanding basic generics is required
- `Type Erasure` — wildcards interact with erasure during capture; understanding erasure explains why the limitations of wildcards exist
- `Inheritance` — wildcards express relationships between parameterised types based on the subtype hierarchy; the hierarchy is foundational

**Builds On This (learn these next):**
- `Stream API` — extensively uses bounded wildcards in `Collector`, `Function<? super T, ? extends R>`, and `Comparator<? super T>` signatures
- `Covariance / Contravariance` — the formal theory that explains why `extends` = covariant and `super` = contravariant

**Alternatives / Comparisons:**
- `Covariance / Contravariance` — C#'s declaration-site variance (`IEnumerable<out T>`) vs Java's use-site variance (wildcards) — different approaches to the same problem
- `Generics` — plain `T` type parameters vs wildcards — the invariant baseline that wildcards relax

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Type arguments ? extends T and ? super T  │
│              │ that add variance to generic types        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Invariant generics reject List<Dog> where │
│ SOLVES       │ List<Animal> is expected, forcing          │
│              │ method duplication per subtype            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ PECS: Producer Extends, Consumer Super.   │
│              │ Extends = read-only. Super = write-only.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Writing APIs that read from collections   │
│              │ (extends) or accumulate into them (super) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need both read and write of exact type T  │
│              │ — use plain T instead of wildcards        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ API flexibility vs complex signatures;    │
│              │ reusability vs readability                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Extends = take out, Super = put in"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Covariance / Contravariance → Stream API  │
│              │ → Functional Interfaces                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The JDK method `Collections.copy(List<? super T> dest, List<? extends T> src)` is a textbook PECS example. Now consider a method `public static <T> void fill(List<? super T> list, T obj)`. A junior engineer argues this should be `List<T>` since you're writing `T` objects. Trace the exact type-checking difference between both signatures when calling `fill(new ArrayList<Number>(), 42)` — which one compiles, which fails, and why does PECS still apply even to a single-element fill operation?

**Q2.** Kotlin declares covariance and contravariance at the class declaration site (`out T`, `in T`) rather than the use site (Java wildcards). Given a Kotlin `interface Source<out T> { fun next(): T }` and its Java equivalent `interface Source { T next(); }` used as `Source<? extends T>`, trace what operations are available on each, and explain precisely why Kotlin's declaration-site variance is safer (harder to misuse) but less flexible (cannot use the same class in both covariant and contravariant positions).

