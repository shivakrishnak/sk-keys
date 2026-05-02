---
layout: default
title: "Covariance / Contravariance"
parent: "Java Language"
nav_order: 317
permalink: /java-language/covariance-contravariance/
number: "0317"
category: Java Language
difficulty: ★★★
depends_on: Generics, Bounded Wildcards, Type Erasure, Inheritance
used_by: Stream API, Functional Interfaces, Bounded Wildcards
related: Bounded Wildcards, Generics, Type Erasure
tags:
  - java
  - generics
  - type-safety
  - deep-dive
  - advanced
---

# 0317 — Covariance / Contravariance

⚡ TL;DR — Covariance means a container of subtype is usable as a container of supertype (read-safe); contravariance is the reverse (write-safe); invariance allows neither — Java generics are invariant by default but support both via wildcards.

| #0317 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Generics, Bounded Wildcards, Type Erasure, Inheritance | |
| **Used by:** | Stream API, Functional Interfaces, Bounded Wildcards | |
| **Related:** | Bounded Wildcards, Generics, Type Erasure | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Consider two operations: (1) reading animals from a shelter and printing them — works safely with any subtype; (2) adding animals to a shelter — must respect the specific type the shelter holds. Without a formal vocabulary for when subtype substitution is safe, developers either over-restrict APIs (every method duplicated per subtype) or under-restrict them (accepting `Object` everywhere and casting manually, risking runtime errors).

**THE BREAKING POINT:**
A team builds a generic pipeline framework. `Processor<T>` transforms T values. A `LoggingProcessor<Object>` should work anywhere a `Processor<String>` is expected — after all, a processor that handles any Object certainly handles Strings. But parameterised types are invariant: `Processor<Object>` is rejected where `Processor<String>` is expected. The team falls back to raw types, losing all safety.

**THE INVENTION MOMENT:**
This is exactly why the formal theory of **Covariance and Contravariance** was applied to Java generics — to give developers a precise language for expressing "this generic parameter is safe to widen" or "safe to narrow", captured in Java as `? extends T` and `? super T`.

---

### 📘 Textbook Definition

**Covariance** is the property of a type constructor `F` such that if `A <: B` (A is a subtype of B), then `F<A> <: F<B>`. In Java, `List<? extends Animal>` is covariant over `Animal` — `List<Dog>` satisfies it because `Dog <: Animal`. **Contravariance** is the reverse: `A <: B` implies `F<B> <: F<A>`. `Comparator<? super Dog>` is contravariant — `Comparator<Animal>` satisfies it. **Invariance** means neither direction holds; Java's plain `List<T>` is invariant — `List<Dog>` is not a `List<Animal>` and vice versa. Java supports both covariance and contravariance through use-site wildcards.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Covariance: my output type can widen. Contravariance: my input type can widen.

**One analogy:**
> A fruit bowl can hold apples (covariant output — you accept a "bowl of apples" as a "bowl of fruit" when looking for fruit to eat). A fruit juicer accepts apples (contravariant input — a "juicer of any fruit" works when you have apples to juice). But a fruit sorter that both takes and returns the same specific variety must be invariant.

**One insight:**
The direction of variance depends on whether the type is in a "producer" (output) or "consumer" (input) position. A function's return type is covariant; its parameter type is contravariant. This is why `Function<? super T, ? extends R>` — the standard functional interface in Java — is written exactly that way.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Covariant positions are "read-only" for the type: if I know the container holds a subtype of T, I can safely read T from it.
2. Contravariant positions are "write-only" for the type: if I know the container accepts a supertype of T, I can safely write T into it.
3. Invariant positions require exact type match: both reads and writes of the exact type must be safe simultaneously.

**DERIVED DESIGN:**
Consider `List<T>`:
- Read (`get()`) returns `T` — covariant position; `List<Dog>` can supply `Animal` (Dog is-a Animal).
- Write (`add(T)`) takes `T` — contravariant position; `List<Animal>` can accept `Dog` (Dog is-a Animal).

Since `List<T>` has both a read and a write operation, it must be invariant to be safe in both directions simultaneously. This is Liskov Substitution at the generic level.

**Variance in function types:**
A function `Function<A, B>` taking A and returning B is:
- Contravariant in A (input): `Function<Animal, B>` works where `Function<Dog, B>` is needed
- Covariant in B (output): `Function<A, Dog>` works where `Function<A, Animal>` is needed

```
Function<? super Dog, ? extends Animal>
    →  accepts Animal  (contravariant in input)
    →  returns Dog     (covariant in output)
```

```
┌────────────────────────────────────────────────┐
│       Variance Direction Summary               │
│                                                │
│  Position   Variance      Java wildcard        │
│  ─────────────────────────────────────         │
│  Output (T) Covariant     ? extends T          │
│  Input  (T) Contravariant ? super T            │
│  Both       Invariant     T (exact)            │
│                                                │
│  Dog <: Animal                                 │
│  List<Dog>  <: List<? extends Animal>  ✓       │
│  List<Dog>  <: List<Animal>            ✗       │
│  Comp<Animal> <: Comp<? super Dog>     ✓       │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Formal framework for type-safe generality; enables expressing "read-only" and "write-only" contracts in the type system.
**Cost:** Complexity — understanding variance requires abstract thinking about type relationships; incorrect variance annotations create subtle bugs or overly complex API signatures.

---

### 🧪 Thought Experiment

**SETUP:**
Java arrays are covariant (unlike generics). `Dog[] dogs` can be assigned to `Animal[] animals`. Watch what happens.

WITHOUT ENFORCEMENT:
```java
Dog[] dogs = new Dog[1];
Animal[] animals = dogs; // covariant assignment — OK
animals[0] = new Cat();  // runtime: ArrayStoreException!
// The JVM checks the actual array type at write time
```
Arrays are covariant — which enables read flexibility — but the JVM must check every write, adding runtime overhead.

WITH GENERICS INVARIANCE:
```java
List<Dog> dogs = new ArrayList<>();
// List<Animal> animals = dogs; // COMPILE ERROR
// The compiler prevents the covariant assignment
// No runtime check needed — safety is compile-time
```

**THE INSIGHT:**
Java made arrays covariant (pre-generics era, for convenience) and pays with `ArrayStoreException` at runtime. Java made generics invariant and pays with more complex wildcard syntax. The trade-off is: covariant arrays = simple syntax but runtime risk; invariant generics = complex wildcards but compile-time safety. Wildcards (`? extends T`) add back controlled covariance without the runtime risk, because they prohibit writes.

---

### 🧠 Mental Model / Analogy

> Imagine type variance as a one-way valve. A covariant valve lets subtypes flow out to supertype containers (output valve: narrow → wide). A contravariant valve lets supertypes flow into subtype containers (input valve: wide → narrow). An invariant container has no valve — nothing flows in either direction unless it's exactly the right type.

- "Covariant output valve" → `? extends T` — Dog flows out as Animal.
- "Contravariant input valve" → `? super T` — Animal comparator accepted for Dog input.
- "Invariant container" → `T` exact — only exact type passes.

Where this analogy breaks down: Real valves are symmetric — a covariant valve would also allow wide types to "pour in" from above. Generic covariance (`? extends T`) specifically prohibits writing to prevent type corruption, which has no direct physical valve analogy.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you have a box of red apples, you can always hand it to someone who asked for a box of fruit — because apples are fruit. This is covariance: boxes of more-specific things can substitute for boxes of less-specific things, when you're only taking things out.

**Level 2 — How to use it (junior developer):**
For method parameters that only read from a collection, use `? extends T` (covariant). For parameters that only write into a collection, use `? super T` (contravariant). For `Comparator`, `Consumer`, and similar "input" functional interfaces, prefer `? super T` for maximum flexibility. The type of a lambda's return type is covariant; its parameter types are contravariant.

**Level 3 — How it works (mid-level engineer):**
Variance is a property of type constructors with respect to their type arguments. Java's wildcard type system encodes variance at use sites. The formal rules: if `F<T>` is covariant in `T`, then `A <: B ⟹ F<A> <: F<B>`. You observe this in the JDK's `Iterable<T>` — its only method `iterator()` returns a type using `T` in covariant position, so `Iterable<Dog>` safely satisfies `Iterable<? extends Animal>`.

**Level 4 — Why it was designed this way (senior/staff):**
Kotlin and Scala adopted declaration-site variance (annotate `T` as `in` or `out` at class definition). Java adopted use-site variance (wildcards at the call site). Declaration-site requires the library author to specify variance once; all users benefit automatically. Use-site requires every user to add wildcards. Java chose use-site because it was retrofitted to an existing type system without modifying class declarations — backward compatibility again. C#'s generics (introduced later than Java's) chose declaration-site, resulting in cleaner APIs (`IEnumerable<out T>`) at the cost of more restricted class design.

---

### ⚙️ How It Works (Mechanism)

**Subtyping rules for parameterised types:**

Given: `Dog <: Animal <: Object`

| Type | Subtype of | Reason |
|---|---|---|
| `List<Dog>` | `List<? extends Animal>` | Dog extends Animal |
| `List<Animal>` | `List<? extends Animal>` | Animal extends Animal |
| `List<Animal>` | `List<? super Dog>` | Animal super Dog |
| `List<Object>` | `List<? super Dog>` | Object super Dog |
| `List<Dog>` | NOT `List<Animal>` | Invariant — no relation |
| `List<Animal>` | NOT `List<Dog>` | Invariant — no relation |

**Variance in functional interfaces:**
```java
// Function<T, R>: contravariant in T, covariant in R
// Most flexible form:
Function<? super Dog, ? extends Number> f;

// This accepts:
Function<Animal, Integer> f1 = d -> 1;  // OK
// Animal super Dog (contravariant input)
// Integer extends Number (covariant output)
f = f1;  // compiles

// Comparator<T>: contravariant in T
// Comparator<Animal> works for List<Dog>.sort()
Comparator<Animal> byName =
    Comparator.comparing(Animal::getName);
List<Dog> dogs = getDogs();
dogs.sort(byName);  // dogs.sort(Comparator<? super Dog>)
// Animal super Dog — contravariant satisfied
```

**Detecting variance violations:**
The compiler uses variance rules during assignment and parameter checking. A violation produces the "incompatible types" or "cannot be applied" error.

```bash
# Show exact type checking in verbose mode:
javac -verbose MyClass.java 2>&1 | grep "error\|warning"

# IntelliJ: hover over a red underline in generic code
# to see the exact type mismatch explanation
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[Source: dogs.sort(animalComparator)]
    → [dogs is List<Dog>]
    → [sort() signature: Comparator<? super Dog>]
    → [animalComparator is Comparator<Animal>]
    → [Check: Animal super Dog?] ← YOU ARE HERE
    → [YES: Animal is a supertype of Dog]
    → [Contravariant: Comparator<Animal> accepted]
    → [Sort proceeds: compare(Dog, Dog) via Animal methods]
    → [Type-safe: no casts, no runtime failures]
```

**FAILURE PATH:**
```
[Source: void display(List<Animal> animals)]
    → [Caller: display(dogList) where dogList = List<Dog>]
    → [Compiler: List<Dog> not a subtype of List<Animal>]
    → [Invariance violation — compile error]
    → [Fix: change parameter to List<? extends Animal>]
    → [Or: fix design to use exact type consistently]
```

**WHAT CHANGES AT SCALE:**
In large frameworks (Spring, Guice, Kafka client APIs), variance errors are amplified across thousands of callsites. A library that uses `List<ConcreteType>` where `List<? extends Base>` would be appropriate forces every user to duplicate or convert data. Correct variance annotation in library APIs saves downstream developers significant boilerplate across large codebases.

---

### 💻 Code Example

Example 1 — Covariance in collection reading:
```java
// Without covariance: three redundant methods
void printDogs(List<Dog> dogs)   { ... }
void printCats(List<Cat> cats)   { ... }
void printBirds(List<Bird> birds){ ... }

// With covariance: one method for all subtypes
void print(List<? extends Animal> animals) {
    animals.forEach(a ->
        System.out.println(a.getName())
    );
}
print(dogs);   // OK
print(cats);   // OK
print(birds);  // OK
```

Example 2 — Contravariance in comparators:
```java
Comparator<Animal> byAge =
    Comparator.comparingInt(Animal::getAge);

// Contravariant: Comparator<Animal> works for
// sorting List<Dog> because Animal super Dog
List<Dog> dogs = new ArrayList<>(getDogs());
dogs.sort(byAge);         // OK — contravariant
dogs.sort(byAge.reversed()); // OK
dogs.sort(
    byAge.thenComparing(Dog::getBreed)
); // OK
```

Example 3 — Function variance: PECS for functions:
```java
// Most general function type:
// consume any Animal, produce some Number
Function<? super Animal, ? extends Number> f =
    (Animal a) -> a.getAge();

// Can assign more specific function:
Function<Animal, Integer> specific =
    Animal::getAge;
f = specific; // OK: contravariant in, covariant out
```

Example 4 — Array covariance trap vs generic safety:
```java
// Arrays: covariant (dangerous)
Animal[] animalArr = new Dog[3]; // compiles!
animalArr[0] = new Cat();        // ArrayStoreException!

// Generics: invariant (safe at compile time)
// List<Animal> animalList = new ArrayList<Dog>(); // ERROR
// ^ Compile error catches the problem before runtime

// Use wildcard for safe covariant reads:
List<? extends Animal> safeList = new ArrayList<Dog>();
Animal first = safeList.get(0); // OK — covariant read
// safeList.add(new Cat());      // ERROR — write blocked
```

---

### ⚖️ Comparison Table

| Language | Variance Style | When Declared | Flexibility | Safety |
|---|---|---|---|---|
| **Java** | Use-site (wildcards) | At usage | High | Compile-time |
| Kotlin | Declaration-site (`in`/`out`) | At class def | Medium | Compile-time |
| C# | Declaration-site (`in`/`out`) | At class def | Medium | Compile-time |
| Scala | Both (`+T`/`-T` + `_`) | Both sites | Very high | Compile-time |
| TypeScript | Structural + bivariant fns | Inference | High | Compile-time (loose) |

How to choose: In Java you have no choice — use wildcards (`? extends`, `? super`) at call sites. If you control a Kotlin or Scala API, prefer declaration-site variance for cleaner library APIs.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java generics are covariant like arrays | Arrays are covariant (pre-generics design); generics are invariant. `String[] <: Object[]` is true; `List<String> <: List<Object>` is false |
| Covariance means any subtype can be assigned | Covariance in Java (`? extends T`) only applies to reads. Writes are prohibited because the exact subtype is unknown |
| A method returning `List<Dog>` is covariant | The method's return type is in a covariant position, but `List<Dog>` itself is an invariant type. Covariance applies to the method's signature context, not the list's mutability |
| Contravariance is rare in Java | `Comparator<? super T>` appears in every sort operation. `Consumer<? super T>` in `forEach`. Every functional interface in a consuming position should be contravariant |
| Invariance is a limitation to work around | Invariance is the correct default when a container is both read from and written to. It prevents `ArrayStoreException`-style bugs at compile time |
| `Function<Dog, Number>` is a subtype of `Function<Animal, Object>` | In Java, `Function<Dog, Number>` is NOT a subtype of `Function<Animal, Object>` directly. Only when the parameter uses wildcards: `Function<? super Dog, ? extends Object>` is satisfied by `Function<Animal, Number>` |

---

### 🚨 Failure Modes & Diagnosis

**Invariance Preventing Reuse — API Too Specific**

**Symptom:**
Library users constantly write adapter code to convert `List<Subtype>` to `List<BaseType>` before calling library methods. Code like `new ArrayList<Animal>(dogList)` appears everywhere.

**Root Cause:**
Library method accepts `List<Animal>` but callers have `List<Dog>`. Invariance requires exact match. The allocation of a new list is unnecessary — the data is identical, only the declared type differs.

**Diagnostic:**
```bash
# Search for conversion patterns in caller code:
grep -rn "new ArrayList<.*>(.*List)" --include="*.java" .
# Each hit may indicate an invariance workaround
```

**Fix:**
```java
// BAD: forces List<Animal> — callers must convert
List<Animal> findSick(List<Animal> animals) { ... }

// GOOD: accepts any animal subtype list
List<Animal> findSick(List<? extends Animal> animals) {
    // Read-only access — ? extends is correct
}
```

**Prevention:** Apply PECS during initial API design. Every collection parameter that is only read should be `? extends T`.

---

**ArrayStoreException from Array Covariance**

**Symptom:**
`ArrayStoreException` at runtime on an array write operation that appears type-safe from the variable declaration.

**Root Cause:**
Array covariance allows `Dog[] → Animal[]` assignment. When a `Cat` is written through the `Animal[]` reference, the JVM's runtime type check (every array write is checked) detects the mismatch.

**Diagnostic:**
```bash
# Stack trace shows ArrayStoreException at array store:
# java.lang.ArrayStoreException: Cat cannot be stored in Dog[]
# Use -verbose:gc to check if it correlates with GC pressure

# Find covariant array assignments:
grep -rn "\[\] " --include="*.java" . | grep "= new.*\[\]"
```

**Fix:**
```java
// BAD: array covariance allows unsafe write later
Animal[] animals = new Dog[5]; // covariant — compiles
animals[0] = new Cat();        // ArrayStoreException!

// GOOD: use List with wildcards for safe covariance
List<? extends Animal> animals = new ArrayList<Dog>();
// animals.add(new Cat()); // compile error — safe
```

**Prevention:** Prefer `List<? extends T>` over covariant array assignments when the collection type needs to be widened.

---

**Wrong Variance Direction on Consumer Parameter**

**Symptom:**
A utility method that adds elements to a collection fails for all subtype collections. Users are confused — intuitively the method "should work."

**Root Cause:**
The method uses `? extends T` (covariant) for a write-only parameter. The compiler correctly rejects writes via covariant wildcards.

**Diagnostic:**
```bash
javac MyUtil.java
# error: no suitable method found for add(T)
# method Collection.add(CAP#1) is not applicable
# (argument mismatch; T cannot be converted to CAP#1)
```

**Fix:**
```java
// BAD: covariant wildcard on consumer (write) param
void addAll(
    T item, Collection<? extends T> target
) {
    target.add(item); // ERROR: can't write through extends
}

// GOOD: contravariant wildcard for write
void addAll(
    T item, Collection<? super T> target
) {
    target.add(item); // OK: super allows write
}
```

**Prevention:** Apply PECS consistently — consumer parameters always use `? super T`, never `? extends T`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Generics` — covariance and contravariance are properties of generic types; basic generics knowledge is required
- `Bounded Wildcards` — `? extends T` and `? super T` are the Java mechanism for expressing variance; these are the tools implementing the theory
- `Inheritance` — variance is defined in terms of the subtype hierarchy; the `Dog <: Animal` relationship drives all variance rules

**Builds On This (learn these next):**
- `Functional Interfaces` — `Function<T,R>`, `Comparator<T>`, `Consumer<T>` — each has a well-defined variance position; understanding variance makes these interfaces' wildcard signatures obvious
- `Stream API` — Stream's collector and comparator parameters use variance extensively; understanding covariance makes Stream APIs intuitive

**Alternatives / Comparisons:**
- `Bounded Wildcards` — the Java syntax that implements covariance/contravariance at use sites
- `Type Erasure` — the mechanism that forces Java to use use-site rather than declaration-site variance

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Formal rules for when a container of      │
│              │ subtype safely substitutes for supertype  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without variance rules, generic APIs are  │
│ SOLVES       │ either unsafe or impossibly restrictive   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Output (return) positions are covariant   │
│              │ (can widen). Input (param) positions are  │
│              │ contravariant (can widen input type).     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing generic APIs — decide per       │
│              │ parameter: producer? (extends) consumer?  │
│              │ (super) both? (exact type)                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Invariant containers are correct for      │
│              │ mutable shared state — avoid wildcards    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ API flexibility vs type complexity;       │
│              │ reusability vs readability                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Outputs widen up, inputs widen down"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Functional Interfaces → Stream API →      │
│              │ Method References                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kotlin's `List<T>` is declared as `interface List<out T>` (covariant), making `List<Dog>` a subtype of `List<Animal>` without wildcards. Java's `List<T>` is invariant. Both languages target the JVM. Explain precisely how Kotlin achieves declaration-site covariance given that the JVM has no native variance support — specifically what the Kotlin compiler generates in bytecode to implement `out T` safely — and what operations Kotlin's `List<out T>` prohibits as a consequence.

**Q2.** The `BiFunction<T, U, R>` interface represents a function taking two arguments. If you need a `BiFunction` that can accept any `Animal` and any `Vehicle` and return any specific `Event` subtype, write the most general possible type signature using variance annotations, then trace through whether `BiFunction<Dog, Car, CollisionEvent>` satisfies it — checking each of the three type parameters' variance independently.

