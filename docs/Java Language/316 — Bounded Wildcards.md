---
layout: default
title: "Bounded Wildcards"
parent: "Java Language"
nav_order: 316
permalink: /java-language/bounded-wildcards/
number: "316"
category: Java Language
difficulty: ★★★
depends_on: "Generics, Type Erasure, Covariance / Contravariance"
used_by: "Collections utility methods, generic API design, Spring generics"
tags: #java, #generics, #wildcards, #pecs, #covariance, #contravariance
---

# 316 — Bounded Wildcards

`#java` `#generics` `#wildcards` `#pecs` `#covariance` `#contravariance`

⚡ TL;DR — **Bounded wildcards** extend generic flexibility: `? extends T` (upper bound, read-only) and `? super T` (lower bound, write-safe). Rule: **PECS — Producer Extends, Consumer Super**.

| #316            | Category: Java Language                                          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Generics, Type Erasure, Covariance / Contravariance              |                 |
| **Used by:**    | Collections utility methods, generic API design, Spring generics |                 |

---

### 📘 Textbook Definition

**Bounded wildcards** are generic type arguments that express constraints on an unknown type `?`. **Upper-bounded wildcard** (`? extends T`): the unknown type is `T` or a subtype of `T` — safe for reading (produces `T` or subtypes), unsafe for writing (exact subtype unknown). **Lower-bounded wildcard** (`? super T`): the unknown type is `T` or a supertype of `T` — safe for writing `T` instances, read only as `Object`. The **PECS** principle (Joshua Bloch, "Effective Java") summarizes the usage rule: _Producer Extends, Consumer Super_. Unbounded wildcard (`?`): equivalent to `? extends Object`; useful when the type doesn't matter (reading as Object or using non-type-dependent methods).

---

### 🟢 Simple Definition (Easy)

`List<? extends Number>`: I can read `Number` values from this list (any Number subtype). I can't add anything (don't know the exact subtype). `List<? super Integer>`: I can add `Integer` values to this list (it accepts Integer or wider). I can only read `Object`. PECS: if your method reads from a collection → `extends`; if it writes → `super`. If it does both → use an exact type parameter `T`.

---

### 🔵 Simple Definition (Elaborated)

Why does `List<Dog>` not work as a `List<Animal>` (invariance)? Because if it did: `List<Dog> dogs = ...; List<Animal> animals = dogs; animals.add(new Cat());` — now `dogs` contains a `Cat`. Wildcards provide controlled flexibility: `List<? extends Animal>` — read-only view of any list of animals (or subtypes). `List<? super Dog>` — any list that can hold dogs (safe for adding dogs, reading only as Object). `Collections.copy(List<? super T> dest, List<? extends T> src)` — canonical PECS example: src produces T, dest consumes T.

---

### 🔩 First Principles Explanation

**PECS decision making + all wildcard scenarios:**

```
WILDCARD SCENARIOS:

  1. UPPER-BOUNDED: List<? extends Number>

     List<Integer> ints = List.of(1, 2, 3);
     List<Double> doubles = List.of(1.1, 2.2);

     // Works with both:
     double sum(List<? extends Number> list) {
         double total = 0;
         for (Number n : list) total += n.doubleValue();  // read as Number ✓
         return total;
     }
     sum(ints);    // List<Integer> ✓ (Integer extends Number)
     sum(doubles); // List<Double>  ✓ (Double extends Number)

     // CANNOT WRITE to ? extends Number:
     void add(List<? extends Number> list) {
         list.add(1);    // COMPILE ERROR — is it List<Integer>? List<Double>? Unknown.
         list.add(1.0);  // COMPILE ERROR
         list.add(null); // Only null can be added (has no type)
     }

  2. LOWER-BOUNDED: List<? super Integer>

     // Works with: List<Integer>, List<Number>, List<Object>
     void addIntegers(List<? super Integer> list) {
         list.add(1);   // safe: Integer can be added to List<Integer>, List<Number>, List<Object>
         list.add(2);
     }

     List<Integer> intList = new ArrayList<>();
     List<Number> numList = new ArrayList<>();
     List<Object> objList = new ArrayList<>();

     addIntegers(intList); // ✓
     addIntegers(numList); // ✓
     addIntegers(objList); // ✓

     // READ from ? super Integer → only Object:
     void readFromSuper(List<? super Integer> list) {
         Integer i = list.get(0);  // COMPILE ERROR — could be Number or Object
         Object o = list.get(0);   // OK — all types are Object
     }

  3. PECS APPLIED — Collections.copy:

     public static <T> void copy(List<? super T> dest, List<? extends T> src) {
         for (int i = 0; i < src.size(); i++) {
             T element = src.get(i);  // read from src (extends T: produces T)
             dest.set(i, element);    // write to dest (super T: consumes T)
         }
     }

     // Use:
     List<Integer> source = Arrays.asList(1, 2, 3);
     List<Number> destination = new ArrayList<>(Arrays.asList(0.0, 0.0, 0.0));
     Collections.copy(destination, source);
     // T inferred as Integer
     // dest: List<? super Integer> → List<Number> ✓ (Number super Integer)
     // src: List<? extends Integer> → List<Integer> ✓ (Integer extends Integer)

  4. UNBOUNDED WILDCARD: List<?>

     // Use when type doesn't matter:
     void printAll(List<?> list) {
         for (Object element : list) {
             System.out.println(element);  // read as Object ✓
         }
     }
     // Can call with List<String>, List<Integer>, any List<X>
     // Cannot add (except null) — unknown type

     // list.size(), list.clear(), list.isEmpty() work — not type-dependent

  5. WILDCARD CAPTURE — compiler trick:

     // Compiler can infer T from ?:
     static <T> void swap(List<T> list, int i, int j) {
         T temp = list.get(i); list.set(i, list.get(j)); list.set(j, temp);
     }

     static void swapHelper(List<?> list, int i, int j) {
         swap(list, i, j);  // compiler infers T (wildcard capture helper)
     }

DECISION GUIDE:

  I only READ from the collection  → List<? extends T>  (upper bound)
  I only WRITE to the collection   → List<? super T>    (lower bound)
  I read AND write                 → List<T>            (exact type parameter)
  I don't care about type at all   → List<?>            (unbounded wildcard)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT bounded wildcards:

- `sum(List<Number>)` can't be called with `List<Integer>` (invariant generics)
- Must write N overloads: `sum(List<Integer>)`, `sum(List<Double>)`, `sum(List<Long>)`

WITH bounded wildcards:
→ `sum(List<? extends Number>)` works for any numeric list. Single method, flexible for all subtypes. PECS provides clear rules for when to use each bound.

---

### 🧠 Mental Model / Analogy

> A vending machine and a coin sorter. Upper bound (`? extends Number`): a vending machine slot that accepts coins — any denomination works (Integer, Double subtype). You can look at what denomination is in the slot, but you can't put a specific denomination back (don't know if it accepts dimes or quarters). Lower bound (`? super Integer`): a coin sorter that accepts any box big enough for a penny (Integer or bigger: Number box, Object box). You can put pennies in any of those boxes. But when you reach in and pull something out, you only know it's "something" (Object) — could be a penny, could be a quarter, could be any coin.

"Vending slot (any denomination works)" = `? extends Number` — reads any Number subtype
"Can't put specific denomination back" = can't add to `? extends` collection
"Coin sorter box accepting pennies" = `? super Integer` — accepts Integer or wider
"Put pennies (Integer) in any box" = can add Integer to `? super Integer` list
"Pull out: only know it's 'something'" = reading from `? super` gives only `Object`

---

### ⚙️ How It Works (Mechanism)

```
TYPE CHECKING WITH WILDCARDS:

  List<? extends Number> exList = new ArrayList<Integer>();

  // GET: compiler knows the erased type is at most Number (the bound)
  Number n = exList.get(0);  // safe: actual type is Integer, which is-a Number

  // SET: compiler refuses (could be List<Integer> or List<Double> or List<Long>)
  exList.add(new Integer(5));  // ERROR: required capture#1 of ? extends Number

  // WHY: if allowed: exList.add(5.0) would break type safety for List<Integer>

  List<? super Integer> supList = new ArrayList<Number>();

  // SET: compiler knows Integer can go into any supertype of Integer
  supList.add(5);   // safe: Number (or Object) always has room for Integer

  // GET: compiler only knows it's a supertype of Integer, so only Object guaranteed
  Number n = supList.get(0);  // ERROR: might be List<Object>, not List<Number>
  Object o = supList.get(0);  // safe: everything is an Object
```

---

### 🔄 How It Connects (Mini-Map)

```
Generic invariance blocks natural subtype relationships in generic contexts
        │
        ▼
Bounded Wildcards ◄──── (you are here)
(? extends T: covariant read-only; ? super T: contravariant write-safe)
        │
        ├── Generics: wildcards are the use-site variance mechanism for Java generics
        ├── Covariance / Contravariance: ? extends = covariance; ? super = contravariance
        ├── PECS: the practical rule for choosing which bound to use
        └── Collections.sort / Collections.copy: canonical PECS examples in JDK
```

---

### 💻 Code Example

```java
// PECS IN PRACTICE:

// Producer (reading): sum values from any numeric list
static double sumAll(List<? extends Number> numbers) {
    return numbers.stream().mapToDouble(Number::doubleValue).sum();
}
sumAll(List.of(1, 2, 3));        // List<Integer> ✓
sumAll(List.of(1.5, 2.5, 3.5)); // List<Double>  ✓

// Consumer (writing): fill a list with integers
static void fillWithIntegers(List<? super Integer> list, int count) {
    for (int i = 0; i < count; i++) list.add(i);
}
List<Number> nums = new ArrayList<>();
fillWithIntegers(nums, 5);  // List<Number> ✓ (Number super Integer)
List<Object> objs = new ArrayList<>();
fillWithIntegers(objs, 3);  // List<Object> ✓ (Object super Integer)

// BOTH (use exact type T):
static <T> void transfer(List<? extends T> src, List<? super T> dst) {
    dst.addAll(src);
}

// Spring example — ApplicationEventMulticaster:
// void multicastEvent(ApplicationEvent event, ResolvableType eventType)
// → uses ? super to accept listeners for supertype events
```

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                                              |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `List<? extends Number>` allows adding `Number` objects    | False. `? extends Number` is read-only for any element (null is the only addable value). The wildcard means "some specific subtype of Number, unknown which" — adding any Number subtype would be unsafe for some actual types.                                                      |
| Unbounded wildcard `List<?>` is the same as `List<Object>` | `List<?>` accepts `List<String>`, `List<Integer>`, any `List<X>`. `List<Object>` only accepts `List<Object>`. You can assign `List<String>` to `List<?>` but not to `List<Object>`. And `List<?>` is read-only (can't add); `List<Object>` is writable.                              |
| PECS only applies to collections                           | PECS applies to any generic parameterized type used as a producer (you read from it) or consumer (you write to it). A `Supplier<? extends T>` produces T. A `Consumer<? super T>` consumes T. Java's `Function<? super T, ? extends R>` follows PECS for both input and output type. |

---

### 🔥 Pitfalls in Production

**Using wrong bound makes method needlessly restrictive:**

```java
// ANTI-PATTERN — overly restrictive exact type:
public static double sumNumbers(List<Number> numbers) {
    return numbers.stream().mapToDouble(Number::doubleValue).sum();
}

// sumNumbers(List<Integer> intList) → COMPILE ERROR
// sumNumbers(List<Double> doubleList) → COMPILE ERROR
// Forces callers to create List<Number> with explicit casts — painful!

// FIX — use upper bound (PECS: method reads from list → extends):
public static double sumNumbers(List<? extends Number> numbers) {
    return numbers.stream().mapToDouble(Number::doubleValue).sum();
}
// Now works with List<Integer>, List<Double>, List<Long>, List<Number>

// SIMILAR PATTERN: Comparator with lower bound:
// BAD:
static <T extends Comparable<T>> void sortList(List<T> list) { ... }

// GOOD — works with types whose supertype implements Comparable:
static <T extends Comparable<? super T>> void sortList(List<T> list) { ... }
// Handles: List<LocalDate> where LocalDate extends ChronoLocalDate implements Comparable<ChronoLocalDate>
// T = LocalDate; Comparable<? super LocalDate> → Comparable<ChronoLocalDate> ✓
```

---

### 🔗 Related Keywords

- `Generics` — wildcards are use-site variance for Java's generic type system
- `Covariance / Contravariance` — `? extends` = covariance; `? super` = contravariance
- `Type Erasure` — wildcards are erased at runtime; type checking is compile-time only
- `Collections.copy` — canonical PECS example in the JDK standard library
- `Comparable / Comparator` — PECS pattern applies to sorting utilities

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ ? extends T: read-only covariant bound.  │
│              │ ? super T: write-safe contravariant.     │
│              │ PECS: Producer Extends, Consumer Super.  │
├──────────────┼───────────────────────────────────────────┤
│ READ FROM    │ List<? extends T> → reads as T           │
│ WRITE TO     │ List<? super T>   → add T safely         │
│ BOTH         │ List<T>           → exact type param     │
│ DON'T CARE   │ List<?>           → read as Object only  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Vending slot: accepts any coin          │
│              │  (extends). Coin sorter: accepts         │
│              │  pennies in any box (super)."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Covariance / Contravariance →             │
│              │ Generics → Type Erasure → Comparable     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `Collections.sort(List<T> list, Comparator<? super T> c)` — the Comparator uses lower bound `? super T`, not `Comparator<T>`. Why? If `T = LocalDate` and you have a `Comparator<ChronoLocalDate>` (a supertype comparator), should you be able to sort `List<LocalDate>` with it? What would break if the bound were `Comparator<T>` instead?

**Q2.** Java wildcards are "use-site variance" — you declare variance at each use site (`? extends`, `? super`). Kotlin uses "declaration-site variance" — you declare `out T` (covariant) or `in T` (contravariant) on the class itself. What is the practical difference? Can you think of cases where declaration-site variance would be cleaner than Java's use-site wildcards?
