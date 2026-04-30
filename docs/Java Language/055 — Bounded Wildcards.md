---
layout: default
title: "Bounded Wildcards"
parent: "Java Language"
nav_order: 55
permalink: /java-language/bounded-wildcards/
number: "055"
category: Java Language
difficulty: ★★★
depends_on: Generics, Type Erasure, Subtyping
used_by: Collections API, Stream API, Utility Methods
tags: #java #advanced #generics #wildcards #pecs
---

# 055 — Bounded Wildcards

`#java` `#advanced` `#generics` `#wildcards` `#pecs`

⚡ TL;DR — `? extends T` (upper-bounded, read-only) and `? super T` (lower-bounded, write-only) enable flexible generic APIs; remember **PECS: Producer Extends, Consumer Super**.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ #055         │ Category: Java Language              │ Difficulty: ★★★           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ Generics, Type Erasure, Subtyping                                 │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ Collections API, Stream API, Utility Methods                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Textbook Definition

Bounded wildcards parameterize generic types with an unknown type that is constrained either to be a **subtype of T** (`? extends T` — upper bound / covariant) or a **supertype of T** (`? super T` — lower bound / contravariant). The unbounded wildcard `?` means any type. The **PECS principle** (Producer Extends, Consumer Super) governs when to use each.

---

## 🟢 Simple Definition (Easy)

- `List<? extends Number>` — a list of **some number subtype** (Integer, Double…); you can **read** Numbers out, but can't **add** anything.
- `List<? super Integer>` — a list of **some Integer supertype** (Integer, Number, Object); you can **add** Integers, but reads come back as `Object`.

---

## 🔵 Simple Definition (Elaborated)

Wildcards solve the problem that `List<Integer>` is NOT a `List<Number>` (generics are invariant). You need them to write utility methods that work across a family of related types. The restriction on reads/writes is not arbitrary — it's the only way to guarantee type safety while allowing flexibility.

---

## 🔩 First Principles Explanation

**Why generics are invariant:**
```
List<Integer> ints = new ArrayList<>();
List<Number>  nums = ints;   // if allowed…
nums.add(3.14);              // adds Double into a List<Integer> — CRASH!
```

**Upper bound (extends) — safe to READ:**
```
List<? extends Number> list = new ArrayList<Integer>();
Number n = list.get(0);   // safe: whatever type it is, it IS-A Number
list.add(1);              // ILLEGAL: compiler can't know if Integer is safe here
// (what if list is actually a List<Double>?)
```

**Lower bound (super) — safe to WRITE:**
```
List<? super Integer> list = new ArrayList<Number>();
list.add(42);             // safe: Integer IS-A Number IS-A Object — always fits
Object o = list.get(0);  // returns Object — can't know the exact type
```

---

## ❓ Why Does This Exist (Why Before What)

Without wildcards, you'd have to write separate methods for `List<Integer>`, `List<Double>`, etc. With wildcards, one method handles all numeric lists. They're the mechanism that makes the Collections API's sort/copy/fill methods work generically.

---

## 🧠 Mental Model / Analogy

> `? extends T` is a **read-only dispenser** — you know everything coming out is at least a `T`, but you can't put anything in (you don't know the exact type of the container).
> `? super T` is a **write-only funnel** — you can pour `T`s in because any super-container of T can hold them, but what you pull out is just "something" (Object).

---

## ⚙️ How It Works (Mechanism)

```
PECS rule: Producer Extends, Consumer Super

  If the generic list PRODUCES values you READ → use extends
  If the generic list CONSUMES values you WRITE → use super

Examples from Collections API:
  Collections.sort(List<T> list, Comparator<? super T> c)
    → Comparator CONSUMES T (compares them) → super
  Collections.copy(List<? super T> dest, List<? extends T> src)
    → src PRODUCES (you read from it) → extends
    → dest CONSUMES (you write to it) → super

Unbounded wildcard List<?>:
  → No writes (except null), reads return Object
  → Use when method is truly type-agnostic (e.g., print size)
```

---

## 🔄 How It Connects (Mini-Map)

```
[Generics invariant] → can't use List<Dog> as List<Animal>
       ↓ solution
[? extends Animal]  → read-only view of Animal subtypes (covariant)
[? super Dog]       → write view for Dog and ancestors (contravariant)
[?]                 → unbounded, truly unknown type
       ↓ governs
[PECS: Producer Extends, Consumer Super]
```

---

## 💻 Code Example

```java
// 1. Upper bound (extends) — read-only producer
void printNumbers(List<? extends Number> list) {
    for (Number n : list) {             // safe read
        System.out.println(n.doubleValue());
    }
    // list.add(1);  COMPILE ERROR — type is unknown subtype of Number
}
printNumbers(new ArrayList<Integer>());   // ✓
printNumbers(new ArrayList<Double>());    // ✓

// 2. Lower bound (super) — write-only consumer
void addNumbers(List<? super Integer> list) {
    list.add(1);   // safe write — Integer fits any supertype of Integer
    list.add(2);
    // Integer i = list.get(0);  // COMPILE ERROR — returns Object
    Object o = list.get(0);      // ok
}
addNumbers(new ArrayList<Integer>());  // ✓
addNumbers(new ArrayList<Number>());   // ✓
addNumbers(new ArrayList<Object>());   // ✓

// 3. PECS in action — Collections.copy re-implementation
static <T> void copy(List<? super T> dest, List<? extends T> src) {
    for (T element : src) {      // src produces T (extends)
        dest.add(element);       // dest consumes T (super)
    }
}

// 4. Unbounded wildcard — truly type-agnostic
void printList(List<?> list) {
    for (Object obj : list) System.out.println(obj);
}
printList(List.of(1, 2, 3));     // ✓
printList(List.of("a", "b"));    // ✓
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `List<? extends Number>` can hold any Number | It references a list of ONE specific subtype (read-only) |
| `List<?>` means `List<Object>` | `List<?>` is unknown type; `List<Object>` is concretely Object |
| PECS only applies to Collections | Applies to any generic consumer/producer pattern |
| Lower bound `super` is rare | Comparator, Predicate, Consumer all use `? super T` |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Confusing extends and super**
Using `? extends T` when you need to write = compile errors that look mysterious.
Fix: apply PECS — "will I read (produce) or write (consume)?"

**Pitfall 2: Capture errors**
```java
void reverse(List<?> list) {
    for (int i = 0, j = list.size()-1; i < j; i++, j--) {
        Object tmp = list.get(i);
        list.set(i, list.get(j));   // COMPILE ERROR: set takes captured type
        list.set(j, tmp);
    }
}
// Fix: use a helper method to capture the type
private <T> void swap(List<T> list, int i, int j) {
    T tmp = list.get(i); list.set(i, list.get(j)); list.set(j, tmp);
}
```

---

## 🔗 Related Keywords

- **Generics (#053)** — wildcards extend generic type parameterization
- **Type Erasure (#054)** — `?` is erased to `Object`/bound at runtime
- **Covariance/Contravariance (#056)** — the conceptual model behind extends/super
- **Comparator** — canonical example of `? super T` in the JDK
- **Collections.copy / sort** — canonical examples of PECS in action

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ PECS: Producer Extends, Consumer Super        │
│              │ extends = safe read; super = safe write       │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Writing utility methods that must work with   │
│              │ a family of related generic types             │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use when a concrete type param works;   │
│              │ wildcards reduce what you can do              │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "extends: I read from it; super: I write to it│
│              │  — PECS is the rule"                          │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Covariance/Contravariance → PECS → JDK APIs   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** Why is it safe to read from `List<? extends Number>` but not write to it?
**Q2.** Why does `Collections.sort` take `Comparator<? super T>` instead of `Comparator<T>`?
**Q3.** What is "wildcard capture" and when does the compiler force you to use a helper method?

