---
layout: default
title: "Generics"
parent: "Java Language"
nav_order: 314
permalink: /java-language/generics/
number: "314"
category: Java Language
difficulty: ★★☆
depends_on: "Type Erasure, Bounded Wildcards, Object class"
used_by: "Collections, Stream API, Optional, Comparable, Spring generics"
tags: #java, #generics, #type-safety, #collections, #compile-time
---

# 314 — Generics

`#java` `#generics` `#type-safety` `#collections` `#compile-time`

⚡ TL;DR — **Generics** add compile-time type parameters to classes and methods, eliminating casts and enabling type-safe containers like `List<String>` — all type info is erased at runtime (Type Erasure).

| #314 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Type Erasure, Bounded Wildcards, Object class | |
| **Used by:** | Collections, Stream API, Optional, Comparable, Spring generics | |

---

### 📘 Textbook Definition

**Generics** (Java 5, JSR-14): a mechanism for parameterizing types and methods with type variables, enabling compile-time type checking and eliminating the need for explicit casts. A generic type is declared with one or more type parameters: `class Box<T>`, `interface Comparable<T>`, `<T extends Comparable<T>> T max(T a, T b)`. Type parameters are replaced at use site: `Box<String>` binds `T=String`. At runtime, all generic type information is erased (Type Erasure) — `Box<String>` and `Box<Integer>` share one `Box.class`. Generics provide safety at compile-time only; the JVM sees only raw types at runtime.

---

### 🟢 Simple Definition (Easy)

Before generics: `List list = new ArrayList(); list.add("hello"); String s = (String) list.get(0);` — cast required, ClassCastException possible at runtime if wrong type added. With generics: `List<String> list = new ArrayList<>(); list.add("hello"); String s = list.get(0);` — no cast, compiler rejects `list.add(42)` at compile time. Generics = compile-time type checking that prevents entire classes of runtime type errors.

---

### 🔵 Simple Definition (Elaborated)

Generics solve the raw type problem: a `List` before Java 5 could hold any `Object` — you couldn't know at compile time what type of elements were inside. Generics let you say: "This list holds only `String`" — the compiler enforces it. Key restriction: Java generics work through Type Erasure — `List<String>` becomes `List` at runtime. You cannot do `new T()`, `T.class`, or `instanceof List<String>`. The type parameter exists only at compile time for safety; the JVM never sees it.

---

### 🔩 First Principles Explanation

**Generic classes, methods, bounded types, and PECS:**

```
GENERIC CLASS:

  // Unbounded generic class:
  public class Box<T> {
      private T value;
      public Box(T value) { this.value = value; }
      public T get() { return value; }
  }
  
  Box<String> stringBox = new Box<>("hello");
  String s = stringBox.get();  // no cast; compiler knows type
  
  Box<Integer> intBox = new Box<>(42);
  Integer i = intBox.get();
  
  // Type safety:
  Box<String> b = new Box<>(42);  // COMPILE ERROR: incompatible types

BOUNDED TYPE PARAMETER:

  // Upper bound: T must be a subtype of Number
  public class NumberBox<T extends Number> {
      private T value;
      public double doubleValue() { return value.doubleValue(); }  // safe: Number has doubleValue()
  }
  
  NumberBox<Integer> ok = new NumberBox<>(42);  // Integer extends Number ✓
  NumberBox<String> no = new NumberBox<>("x");  // COMPILE ERROR: String does not extend Number

GENERIC METHOD:

  // Type parameter declared on method:
  public static <T extends Comparable<T>> T max(T a, T b) {
      return a.compareTo(b) >= 0 ? a : b;
  }
  
  String larger = max("apple", "banana");  // T inferred as String
  Integer bigger = max(10, 20);            // T inferred as Integer
  
WILDCARD vs TYPE PARAMETER:

  // Wildcards: for use-site flexibility
  void printAll(List<?> list) {            // any type; read-only
      for (Object o : list) System.out.println(o);
  }
  
  // Upper-bounded wildcard: read producer (PECS: Producer Extends)
  double sumList(List<? extends Number> list) {
      double sum = 0;
      for (Number n : list) sum += n.doubleValue();
      return sum;
  }
  // sumList(List<Integer>) ✓, sumList(List<Double>) ✓
  // list.add(1.5) → COMPILE ERROR: can't add to ? extends Number (unknown exact type)
  
  // Lower-bounded wildcard: write consumer (PECS: Consumer Super)
  void addNumbers(List<? super Integer> list) {
      list.add(1); list.add(2);  // safe: list accepts Integer or supertype
  }
  // addNumbers(List<Integer>) ✓, addNumbers(List<Number>) ✓, addNumbers(List<Object>) ✓
  
  // PECS RULE: Producer Extends, Consumer Super
  // Reading from a collection (producer) → ? extends T
  // Writing to a collection (consumer) → ? super T

TYPE ERASURE CONSEQUENCES:

  At runtime: List<String> == List<Integer> (same raw type List.class)
  
  ILLEGAL at compile time:
  if (list instanceof List<String>) { ... }  // can't check generic type at runtime
  T obj = new T();                            // can't instantiate type parameter
  T[] arr = new T[10];                        // can't create generic array
  Class<T> clazz = T.class;                   // can't get .class of type parameter
  
  WORKAROUND for T.class — pass Class<T> explicitly:
  public <T> T fromJson(String json, Class<T> type) {
      return objectMapper.readValue(json, type);
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Generics (pre-Java 5):
- `List list = new ArrayList(); list.add("hello"); list.add(42);` — no compile-time error
- `String s = (String) list.get(1);` — `ClassCastException` at runtime: cast failed
- All collection code littered with casts; type errors caught only at runtime

WITH Generics:
→ `List<String>` rejects `list.add(42)` at compile time. No casts. Type errors are compile errors, not runtime exceptions. Code is self-documenting about intent.

---

### 🧠 Mental Model / Analogy

> A labeled storage bin at a warehouse. Raw type (`List`): an unlabeled bin — you can put anything in it, but when you reach in and grab something, you might pull out a shoe when you expected a book (ClassCastException). Generic type (`List<String>`): a bin with a "Books Only" label — the warehouse system (compiler) rejects any attempt to put a shoe in. When you pull something out, it's guaranteed to be a book (no cast needed). The label exists on the bin (compile-time); the actual storage mechanism (runtime) is identical for all labeled bins.

"Unlabeled bin" = raw `List` (pre-Java 5 style — accepts any Object)
"Books Only label" = type parameter `<String>` — compiler enforces the constraint
"Compiler rejects shoes" = compile error when adding wrong type
"Guaranteed to be a book when pulled out" = no cast required on `list.get(0)`
"Storage mechanism identical for all bins" = Type Erasure — `List.class` for all `List<T>`

---

### ⚙️ How It Works (Mechanism)

```
GENERIC TYPE ERASURE IN BYTECODE:

  Source:                         Bytecode (after erasure):
  List<String> list = ...;    →   List list = ...;
  String s = list.get(0);    →   String s = (String) list.get(0);  ← cast inserted by compiler
  
  class Box<T> { T get(); }  →   class Box { Object get(); }  ← T replaced by Object
  class Box<T extends Number> { T get(); } → class Box { Number get(); }  ← T replaced by bound
  
  BRIDGE METHODS (compiler-generated for overriding):
  
  interface Comparable<T> { int compareTo(T o); }
  class MyString implements Comparable<MyString> {
      public int compareTo(MyString o) { ... }
  }
  
  Compiler generates bridge method:
  public int compareTo(Object o) {   // bridge: erased signature
      return compareTo((MyString) o);  // delegates to typed version
  }
  // Enables polymorphic dispatch through erased types
```

---

### 🔄 How It Connects (Mini-Map)

```
Pre-Java 5: raw types → ClassCastException at runtime
        │
        ▼
Generics ◄──── (you are here)
(type parameters; compile-time safety; erased at runtime)
        │
        ├── Type Erasure: the mechanism that removes generic type info at runtime
        ├── Bounded Wildcards: ? extends T, ? super T — covariance/contravariance
        ├── Collections: List<T>, Map<K,V>, Set<T> — primary use of generics
        └── Stream API: Stream<T>, Optional<T> — generic functional constructs
```

---

### 💻 Code Example

```java
// GENERIC CLASS:
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

Pair<String, Integer> nameAge = new Pair<>("Alice", 30);
String name = nameAge.getFirst();   // no cast
int age = nameAge.getSecond();      // no cast (unboxed)

// GENERIC METHOD:
public static <T> List<T> repeat(T item, int count) {
    List<T> result = new ArrayList<>(count);
    for (int i = 0; i < count; i++) result.add(item);
    return result;
}
List<String> repeated = repeat("hello", 3);  // ["hello", "hello", "hello"]

// BOUNDED: T extends Comparable
public static <T extends Comparable<T>> T clamp(T value, T min, T max) {
    if (value.compareTo(min) < 0) return min;
    if (value.compareTo(max) > 0) return max;
    return value;
}
int clamped = clamp(150, 0, 100);   // → 100

// PECS — Collections.copy:
// <T> void copy(List<? super T> dest, List<? extends T> src)
// dest: consumer (write T into it) → super T
// src: producer (read T from it) → extends T
List<Number> dest = new ArrayList<>(Arrays.asList(0.0, 0.0));
List<Integer> src = Arrays.asList(1, 2);
Collections.copy(dest, src);  // works: Integer extends Number
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `List<Animal>` is a supertype of `List<Dog>` | Generic types are invariant. `List<Dog>` is NOT a `List<Animal>`, even though `Dog extends Animal`. This is by design: if it were allowed, you could add a `Cat` to a `List<Dog>` via the `List<Animal>` reference. Use wildcards: `List<? extends Animal>` for read-only access. |
| You can create a generic array: `T[] arr = new T[10]` | Illegal due to type erasure. The JVM cannot create an array of an unknown type at runtime. Workaround: `@SuppressWarnings("unchecked") T[] arr = (T[]) new Object[10]` — unsafe cast. Or use `ArrayList<T>` which avoids the array creation problem. |
| Raw types and generics can be freely mixed | Mixing generates "unchecked" warnings and breaks type safety. Assigning `List<String>` to `List` (raw) and then adding an `Integer` compiles with a warning but causes `ClassCastException` at runtime when the list is read as `List<String>`. Never use raw types in new code. |

---

### 🔥 Pitfalls in Production

**Heap pollution: unchecked cast bypasses generic type safety:**

```java
// ANTI-PATTERN — unchecked cast hides type mismatch:
@SuppressWarnings("unchecked")
public static <T> T unsafeCast(Object obj) {
    return (T) obj;  // unchecked: T is erased, cast always "succeeds" at runtime
}

// CALLER:
String s = unsafeCast(42);  // compiles! Integer boxed to Object, then (T) = String at compile
// When 's' is USED: ClassCastException thrown at point of use, NOT at the cast
System.out.println(s.length());  // ClassCastException: Integer cannot be cast to String

// The dangerous part: the exception is thrown far from the cast, making debugging hard.

// FIX — use Class<T> for safe cast:
public static <T> T safeCast(Object obj, Class<T> type) {
    return type.cast(obj);  // throws ClassCastException immediately if wrong type
}

String s = safeCast(42, String.class);      // ClassCastException immediately
String s2 = safeCast("hello", String.class); // safe
```

---

### 🔗 Related Keywords

- `Type Erasure` — why `List<String>` and `List<Integer>` are the same at runtime
- `Bounded Wildcards` — `? extends T` and `? super T` for flexible generic APIs
- `Covariance / Contravariance` — invariance of Java generics vs. array covariance
- `Collections` — `List<T>`, `Map<K,V>`, `Set<T>` are the primary use case for generics
- `Stream API` — `Stream<T>`, `Optional<T>` — functional generics in Java 8+

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Type parameters → compile-time safety.  │
│              │ Erased at runtime. No casts needed.     │
├──────────────┼───────────────────────────────────────────┤
│ PECS         │ Producer Extends: List<? extends Number> │
│              │ Consumer Super:   List<? super Integer>  │
├──────────────┼───────────────────────────────────────────┤
│ ILLEGAL      │ new T(); T.class; instanceof List<String>│
│              │ new T[n]; all erased at runtime          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "'Books Only' bin: compiler enforces     │
│              │  type at compile time; runtime bin is   │
│              │  just 'Object' underneath."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Type Erasure → Bounded Wildcards →        │
│              │ Covariance → Collections → Streams       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java generic arrays are illegal (`new T[n]`), but `ArrayList<T>` works fine internally using `Object[]` with an unchecked cast. Examine the JDK source of `ArrayList`: how does it create and resize its internal array without knowing `T`? And why does returning `T` from `get(int index)` work correctly at the call site even though internally it's an `Object[]`?

**Q2.** Spring's `@Autowired` uses reflection to inject beans of type `Service<OrderEvent>` — but due to type erasure, `Service<OrderEvent>` and `Service<PaymentEvent>` both have erased type `Service` at runtime. How does Spring's `ResolvableType` (part of the core framework) work around type erasure to distinguish between `Service<OrderEvent>` and `Service<PaymentEvent>` beans?
