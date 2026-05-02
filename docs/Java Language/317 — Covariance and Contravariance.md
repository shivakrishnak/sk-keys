---
layout: default
title: "Covariance / Contravariance"
parent: "Java Language"
nav_order: 317
permalink: /java-language/covariance-contravariance/
number: "317"
category: Java Language
difficulty: ★★★
depends_on: "Generics, Bounded Wildcards, Type Erasure, Inheritance"
used_by: "Generics API design, Comparator, Function, Kotlin in/out, type systems"
tags: #java, #generics, #covariance, #contravariance, #type-theory, #wildcards
---

# 317 — Covariance / Contravariance

`#java` `#generics` `#covariance` `#contravariance` `#type-theory` `#wildcards`

⚡ TL;DR — **Covariance** preserves subtype order (`Dog[]` is `Animal[]`); **contravariance** reverses it (`Consumer<Animal>` is usable as `Consumer<Dog>`). Java arrays are covariant (unsafely); generics are invariant; wildcards simulate both.

| #317 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Generics, Bounded Wildcards, Type Erasure, Inheritance | |
| **Used by:** | Generics API design, Comparator, Function, Kotlin in/out, type systems | |

---

### 📘 Textbook Definition

**Covariance**: if `B extends A`, then `T<B>` is a subtype of `T<A>` — the subtype relationship is preserved. **Contravariance**: if `B extends A`, then `T<A>` is a subtype of `T<B>` — the relationship is reversed. **Invariance**: neither — `T<A>` and `T<B>` are unrelated regardless of A and B's relationship. Java array types are covariant: `String[]` is a subtype of `Object[]`. Java generic types are invariant: `List<String>` is NOT a subtype of `List<Object>`. Java wildcards simulate variance: `List<? extends T>` is covariant; `List<? super T>` is contravariant. The subtype variance problem is rooted in the Liskov Substitution Principle: covariant return types are safe; covariant parameter types are not.

---

### 🟢 Simple Definition (Easy)

Covariance: `Dog` is an `Animal`, so `Dog[]` is an `Animal[]`. Makes intuitive sense. Contravariance: a method that processes `Animal` objects should also be usable to process `Dog` objects (a more specific case). Invariance: `List<Dog>` is NOT a `List<Animal>` — you can't use a dog list where an animal list is expected (because someone might add a `Cat` to it through the animal list reference). Java arrays: covariant (but unsafe). Java generics: invariant (safe). Java wildcards: let you choose covariance or contravariance per use site.

---

### 🔵 Simple Definition (Elaborated)

Why are Java generics invariant? If `List<Dog>` were a `List<Animal>`: `List<Dog> dogs = new ArrayList<>(); List<Animal> animals = dogs; animals.add(new Cat());` — now `dogs` contains a `Cat`. `Dog d = dogs.get(0);` → ClassCastException. This exact problem exists with arrays (Java arrays ARE covariant): `Dog[] dogs = new Dog[1]; Object[] objs = dogs; objs[0] = new Cat();` → `ArrayStoreException` at runtime. Arrays chose covariance for convenience (Java 1.0 needed arrays to work with sort algorithms); generics chose invariance for safety.

---

### 🔩 First Principles Explanation

**Array covariance pitfall, generic invariance, and variance via wildcards:**

```
COVARIANCE (arrays — unsafe):

  class Animal {}
  class Dog extends Animal {}
  class Cat extends Animal {}
  
  Dog[] dogs = new Dog[1];
  Animal[] animals = dogs;    // OK: Dog[] IS-A Animal[] (covariant)
  animals[0] = new Cat();     // Compiles! But runtime: ArrayStoreException
  // JVM checks element type at array store time — runtime safety check
  
  // This is the "array covariance problem" — subtype relationship allows type-unsafe writes

INVARIANCE (generics — safe):

  List<Dog> dogList = new ArrayList<>();
  List<Animal> animalList = dogList;  // COMPILE ERROR: invariant generics
  // Prevents: animalList.add(new Cat()) → ClassCastException later
  
  // Invariant: List<Dog> and List<Animal> are UNRELATED types
  // (even though Dog extends Animal)

COVARIANCE VIA WILDCARD (? extends — read-only):

  List<? extends Animal> covariantList = dogList;  // OK: covariant reference
  Animal a = covariantList.get(0);   // safe: always an Animal (or subtype)
  covariantList.add(new Dog());      // COMPILE ERROR: write unsafe (unknown exact subtype)
  
  // Use case: reading from collection; method that processes any Animal list
  static void processAnimals(List<? extends Animal> animals) {
      for (Animal a : animals) a.makeSound();  // read only ✓
  }
  processAnimals(dogList);  // List<Dog> ✓
  processAnimals(catList);  // List<Cat> ✓

CONTRAVARIANCE VIA WILDCARD (? super — write-safe):

  // Contravariance: if B extends A, Consumer<A> is a Consumer<B>
  // A method that processes Animals can certainly process Dogs (more specific)
  
  List<? super Dog> contravariantList = new ArrayList<Animal>();  // OK
  contravariantList.add(new Dog());     // safe: whatever supertype it is, accepts Dog
  contravariantList.add(new Husky());   // safe: Husky extends Dog ✓
  Animal a = contravariantList.get(0);  // COMPILE ERROR: type is ? super Dog (might be Object)
  Object o = contravariantList.get(0);  // OK: everything is Object
  
  // Real example: Comparator<? super T>
  // A Comparator<Animal> can compare Dogs (knows how to compare all Animals)
  Comparator<Animal> byName = Comparator.comparing(Animal::getName);
  List<Dog> dogs2 = Arrays.asList(new Dog("Rex"), new Dog("Buddy"));
  dogs2.sort(byName);  // Comparator<Animal> works for List<Dog> ✓ (contravariance)

FUNCTION VARIANCE:

  // Function<A, B>: contravariant in A (input), covariant in B (output)
  
  Function<Object, Dog> objectToDog = obj -> new Dog();
  Function<String, Animal> stringToAnimal = objectToDog;
  // Wait — is this valid? Let's check:
  // Input: String is more specific than Object
  //   → Function<Object,...> accepts String (contravariance: Object super String ✓)
  // Output: Dog is more specific than Animal
  //   → Function<..., Dog> returns Dog, which IS-A Animal (covariance ✓)
  // Result: Function<Object, Dog> can be used as Function<String, Animal>
  
  // Java functional types (Kotlin is explicit):
  // java.util.function.Function<? super T, ? extends R> — PECS applied to Function

KOTLIN DECLARATION-SITE VARIANCE:

  // Java: use-site variance (wildcards at each use site)
  // Kotlin: declaration-site variance (in/out modifiers on class declaration)
  
  // Covariant producer (Kotlin):
  interface Producer<out T> { fun produce(): T }  // out T = covariant
  // Producer<Dog> IS-A Producer<Animal>
  
  // Contravariant consumer (Kotlin):
  interface Consumer<in T> { fun consume(item: T) }  // in T = contravariant
  // Consumer<Animal> IS-A Consumer<Dog>
  
  // In Java: must redeclare ? extends / ? super at each use site
  // In Kotlin: declared once on the class = cleaner for consistently covariant/contravariant types
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT understanding variance:
- Overly restrictive generic APIs (exact types only: `Comparator<Dog>` doesn't work for `List<Husky>`)
- Array covariance bugs: `ArrayStoreException` at runtime
- PECS rules seem arbitrary without variance theory

WITH variance theory:
→ Understand WHY `Comparator<? super T>` lets one comparator work for subtypes. Understand WHY generic types are invariant. Design APIs with the right variance for each type parameter.

---

### 🧠 Mental Model / Analogy

> Covariance: a "Dog Handler Needed" sign accepting a "Dog Handler" (subtype fills supertype role). A Dog Handler CAN handle Animals if needed — their specialization is contained within the animal role. Contravariance: a "General Animal Handler" is MORE useful than a "Dog Handler Only" when you need someone to handle dogs — the animal handler can do anything a dog-specific handler does and more. Invariance: a "Dog Kennel" is NOT an "Animal Kennel" because you could sneak in a cat — the kennel's WRITING behavior breaks the contract.

"Dog Handler fills Animal Handler role" = covariance: `Dog extends Animal → Dog[] is Animal[]`
"General Animal Handler handles dogs" = contravariance: `Consumer<Animal>` works for `Dog`
"Dog Kennel ≠ Animal Kennel (cat sneaking in)" = invariance of `List<Dog>` ≠ `List<Animal>`

---

### ⚙️ How It Works (Mechanism)

```
VARIANCE SUMMARY TABLE:

  Type         | Relationship              | Java mechanism
  ─────────────────────────────────────────────────────────────
  Dog[] IS     | Animal[] (covariant)      | Java arrays — inherently covariant
  List<Dog>    | NOT List<Animal>          | Java generics — invariant by default
  List<Dog> IS | List<? extends Animal>   | ? extends = covariant reading
  List<Anim> IS| List<? super Dog>         | ? super = contravariant writing
  
  LISKOV CHECK FOR COVARIANT PARAMETER (WHY IT'S UNSAFE):
  
  class Animal { void eat(Animal food); }
  class Dog extends Animal {
      // If covariant: void eat(Dog food)  ← UNSAFE: breaks LSP
      // Dog.eat(Dog) is MORE restrictive than Animal.eat(Animal)
      // → violates Liskov: Dog can't be used where Animal is expected
  }
  
  Covariant RETURN type: safe (more specific return = always satisfies "is-a")
  Covariant PARAMETER type: unsafe (more restrictive parameter breaks substitutability)
  
  Java: return types are covariant (allowed to narrow return type in subclass)
  Java: parameter types are invariant (same signature required for overriding)
```

---

### 🔄 How It Connects (Mini-Map)

```
Subtype relationships + generics create variance questions
        │
        ▼
Covariance / Contravariance ◄──── (you are here)
(covariant: subtype preserves; contravariant: reverses; invariant: unrelated)
        │
        ├── Bounded Wildcards: Java's mechanism for use-site covariance/contravariance
        ├── Generics: invariant by default; wildcards add flexibility
        ├── Liskov Substitution Principle: theoretical foundation for safe variance
        └── Kotlin in/out: declaration-site variance alternative
```

---

### 💻 Code Example

```java
// ARRAY COVARIANCE — DANGEROUS:
String[] strings = {"a", "b", "c"};
Object[] objects = strings;          // OK: String[] is Object[] (covariant)
objects[0] = 42;                     // ArrayStoreException at runtime!
// JVM checks at runtime: 42 (Integer) cannot be stored in String[]

// GENERIC INVARIANCE — SAFE:
List<String> strList = List.of("a", "b");
// List<Object> objList = strList;  // COMPILE ERROR: invariant

// COVARIANCE VIA WILDCARD — READ-ONLY:
List<? extends CharSequence> seq = strList;  // String extends CharSequence
CharSequence cs = seq.get(0);  // safe: always a CharSequence
// seq.add("x");  // COMPILE ERROR: can't add to ? extends wildcard

// CONTRAVARIANCE VIA WILDCARD — WRITE-SAFE:
List<? super String> supers = new ArrayList<Object>();
supers.add("hello");   // safe: String goes into Object list ✓
supers.add("world");   // safe
Object o = supers.get(0);  // only Object guaranteed on read

// COMPARATOR CONTRAVARIANCE:
Comparator<CharSequence> byLength = Comparator.comparingInt(CharSequence::length);
List<String> words = Arrays.asList("banana", "apple", "cherry");
// Collections.sort uses Comparator<? super String>:
words.sort(byLength);  // Comparator<CharSequence> works for List<String> ✓
System.out.println(words);  // [apple, banana, cherry]
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java arrays being covariant is good design | Array covariance in Java is widely considered a design mistake. It provides no useful feature (generics `? extends` solve the same problem safely) while enabling `ArrayStoreException` at runtime. It exists for backward compatibility with Java 1.0 before generics existed. |
| Contravariance means reversing method behavior | Contravariance is a subtype relationship — `Consumer<Animal>` is substitutable where `Consumer<Dog>` is expected (because Animal is "bigger" — can do more). It doesn't reverse behavior; it reverses the direction of the subtype relationship for that parameterized type. |
| Java generics are always invariant | Java generics are invariant by default. Wildcards (`? extends`, `? super`) provide use-site covariance and contravariance. Declaration-site variance (like Kotlin's `in`/`out`) is not available in Java — each use site must declare its variance. |

---

### 🔥 Pitfalls in Production

**ArrayStoreException from array covariance:**

```java
// ANTI-PATTERN — relying on array covariance for generic collections:
// Common in legacy code before generics:
public static void shuffle(Object[] array) { ... }

// Usage with typed array:
Integer[] ints = {1, 2, 3};
shuffle(ints);  // works: Integer[] IS Object[]

// DANGEROUS variant:
public static void fillWithNulls(Object[] array) {
    Arrays.fill(array, "NULL_PLACEHOLDER");  // ArrayStoreException if array is Integer[]!
}
fillWithNulls(ints);  // ArrayStoreException: String cannot be stored in Integer[]

// FIX — use generic method:
public static <T> void fillWithNulls(T[] array, T value) {
    Arrays.fill(array, value);  // type-checked: value must be T
}
// Or use Collection<T> instead of T[]:
public static <T> void fillCollection(List<? super T> list, T value) { ... }
```

---

### 🔗 Related Keywords

- `Bounded Wildcards` — Java's use-site mechanism for covariance (`? extends`) and contravariance (`? super`)
- `Generics` — invariant by default; wildcards layer variance on top
- `Liskov Substitution Principle` — theoretical basis for safe subtype behavior
- `Kotlin in/out` — declaration-site variance: cleaner than Java's use-site wildcards
- `Arrays` — covariant in Java; leads to ArrayStoreException when misused

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COVARIANCE   │ Subtype relation preserved.              │
│              │ Dog[] IS Animal[]. List<? extends Animal>│
│              │ → safe for reading; CANNOT write        │
├──────────────┼───────────────────────────────────────────┤
│ CONTRAVARIANCE│ Subtype relation reversed.              │
│              │ Consumer<Animal> works for Dog input.    │
│              │ List<? super Dog> → safe to write Dog    │
├──────────────┼───────────────────────────────────────────┤
│ INVARIANCE   │ List<Dog> NOT List<Animal>. Default for  │
│              │ Java generics. Safe.                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Dog[] = Animal[] → cat sneaks in.      │
│              │  List<Dog> ≠ List<Animal> → safe.       │
│              │  Wildcard = controlled unsafe."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Wildcards → Generics → LSP →     │
│              │ Kotlin in/out → Type Theory              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java allows covariant return types in subclass overrides: `Animal produce()` can be overridden as `Dog produce()` in a Dog-producing subclass. But parameter types must match exactly for true method overriding (widening parameters creates overloading, not overriding). Why is covariant return safe (LSP-preserving) but covariant parameter unsafe (LSP-violating)? Use the Liskov Substitution Principle to explain.

**Q2.** Kotlin's type system has `List<out T>` (covariant, read-only) and `MutableList<T>` (invariant, read-write) as separate interfaces. Java has one `List<T>` (mutable) with wildcard `List<? extends T>` at use sites. What are the practical consequences of this design difference when building a library API in Java vs Kotlin — specifically around how callers interact with collection parameters?
