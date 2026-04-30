---
layout: default
title: "Type Erasure"
parent: "Java Language"
nav_order: 315
permalink: /java-language/type-erasure/
---
# 315 — Type Erasure

`#java` `#intermediate` `#generics` `#jvm` `#internals`

⚡ TL;DR — The compiler enforces generic type constraints then strips all type parameters from bytecode; `List<String>` and `List<Integer>` become identical `List` at runtime.

| #315 | category: Java Language
|:---|:---|:---|
| **Depends on:** | Generics, Bytecode, JVM | |
| **Used by:** | Reflection, Generics Limitations, Heap Pollution | |

---

### 📘 Textbook Definition

Type erasure is the process by which the Java compiler removes all generic type information during compilation, replacing type parameters with their **erasure** — `Object` for unbounded parameters, or the **upper bound** for bounded ones. The compiler also injects synthetic **bridge methods** to handle method overriding in generic subclasses. This design maintains binary compatibility with pre-Java-5 JVMs.

---

### 🟢 Simple Definition (Easy)

The compiler uses `List<String>` to check your code — but the `.class` file it produces is just `List`. At runtime, the JVM sees no difference between `List<String>` and `List<Integer>`. All the type safety happens at compile time and then disappears.

---

### 🔵 Simple Definition (Elaborated)

Java generics were designed to be backwards-compatible: code compiled with Java 5 generics had to run on existing JVMs without changes to the class format. The solution was erasure — type params are a compile-time fiction. The JVM never knows about them. This is why you can't `new T[]`, can't do `instanceof List<String>`, and can't catch a generic exception.

---

### 🔩 First Principles Explanation

**What the compiler does:**

```
Source code:                     Compiled bytecode (erased):
─────────────────────────────── ──────────────────────────────────
class Box<T> {                   class Box {
  T value;                         Object value;   // T → Object
  T get() { return value; }        Object get() { return value; }
}                                }

class NumBox<T extends Number> { class NumBox {
  T value;                         Number value;   // T → Number (bound)
  T get() { return value; }        Number get() { return value; }
}                                }
```

**Bridge methods** (inserted when overriding):
```java
// Source
class StringBox extends Box<String> {
    @Override String get() { return value; }
}
// Compiled: TWO get() methods inserted
//   String get()  — the actual override
//   Object get()  — bridge method, calls String get(), satisfies Box.get() contract
```

---

### ❓ Why Does This Exist (Why Before What)

Java had to add generics in Java 5 without breaking the billions of lines of pre-generics code already deployed. Reification (keeping type info at runtime) would have broken JVM binary compatibility. Erasure was the pragmatic choice — perfect backwards compatibility at the cost of runtime type information.

---

### 🧠 Mental Model / Analogy

> Type erasure is like writing a strict contract in pencil for an architect (compiler), who checks everything is correct and then erases the contract details when handing the blueprint to the construction crew (JVM). The crew builds exactly what the architect verified — they just don't need to know the original constraints.

---

### ⚙️ How It Works (Mechanism)

```
Erasure rules:

1. Unbounded T → Object
   Box<T>              ─erasure→  Box (uses Object)

2. Bounded T extends Foo → Foo
   Box<T extends Number> ─erasure→ Box (uses Number)

3. Multiple bounds T extends A & B → A (leftmost)
   <T extends A & B>  ─erasure→  uses A

4. Cast insertion
   String s = box.get();  becomes  String s = (String) box.get();
   (compiler inserts cast to make it type-safe despite erased internal)

5. Bridge methods
   Subclass overriding a generic method gets a synthetic bridge method
   to satisfy the erased parent's contract.

What survives erasure (accessible via Reflection):
  - Generic type info on class/interface declarations (not instances)
  - Method and field signatures → via getGenericType(), getGenericReturnType()
  - Superclass and interface type args → getGenericSuperclass()
```

---

### 🔄 How It Connects (Mini-Map)

```
[Source: List<String>]
       │ javac: type-check, insert casts
       ▼
[Bytecode: List + checkcast instructions]
       │
       ├─► Cannot do instanceof List<String>  (no type info)
       ├─► Cannot create T[]                  (no type info)
       ├─► Cannot catch ( T extends Exception) (no type info)
       └─► Can recover via Reflection ParameterizedType (class-level only)
```

---

### 💻 Code Example

```java
// Demonstrating erasure effects

// 1. Type information is gone at runtime
List<String> strings = new ArrayList<>();
List<Integer> ints    = new ArrayList<>();
System.out.println(strings.getClass() == ints.getClass()); // true — both just ArrayList

// 2. instanceof with parameterised type is illegal
if (obj instanceof List<String>) { }  // COMPILE ERROR

// 3. Cannot create generic array
class Container<T> {
    T[] array = new T[10];   // COMPILE ERROR: generic array creation
    // Workaround:
    @SuppressWarnings("unchecked")
    T[] arr = (T[]) new Object[10];  // unchecked cast — heap pollution risk
}

// 4. Casts are injected at usage sites
Box<String> b = new Box<>("hello");
String s = b.get();  // compiler inserts: (String) b.get()

// 5. Recovering type info with Reflection (class-level only, NOT instances)
class StringBox extends Box<String> {}

Type superType = StringBox.class.getGenericSuperclass();          // Box<String>
Type typeArg   = ((ParameterizedType) superType).getActualTypeArguments()[0]; // String.class
System.out.println(typeArg);   // class java.lang.String

// 6. Gson / Jackson use this trick: TypeToken captures class-level generics
Type listOfString = new TypeToken<List<String>>(){}.getType();    // preserved
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| JVM knows about generic types | JVM only sees erased types — generics are compile-only |
| Type info is completely gone | Class-level declarations survive in bytecode signatures |
| Erasure causes performance loss | No runtime overhead — erasure actually saves memory vs reification |
| You can check `x instanceof Box<String>` | Illegal — use `x instanceof Box` only |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Heap pollution**
```java
@SafeVarargs  // suppresses warning — BUT only safe if you don't write to the array
static <T> void add(T... items) {
    Object[] raw = items;
    raw[0] = "oops";  // pollutes the heap — ClassCastException later, elsewhere
}
List<Integer> ints = new ArrayList<>();
add(1, 2, 3);  // fine
add(ints);     // heap pollution — raw[0] might be written with wrong type
```

**Pitfall 2: Losing type info for deserializers**
Jackson / Gson need the full generic type to deserialize. Without a TypeReference/TypeToken, you lose the element type.
```java
// BAD: loses type info
List result = objectMapper.readValue(json, List.class);          // List of LinkedHashMap
// GOOD: preserves via class-level trick
List<MyType> result = objectMapper.readValue(json,
    new TypeReference<List<MyType>>(){});
```

---

### 🔗 Related Keywords

- **Generics (#053)** — the feature that type erasure implements
- **Bounded Wildcards (#055)** — wildcards interact with erasure's `?`-to-Object substitution
- **Heap Pollution** — when erasure causes a variable of type T to reference a non-T value
- **Reflection (#058)** — allows limited recovery of generic signatures from class metadata
- **TypeToken / TypeReference** — workaround patterns to preserve generic type info

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Generic types enforce safety at compile time  │
│              │ then are erased; JVM sees only raw types      │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Explaining why generic arrays fail, why       │
│              │ instanceof fails with type params             │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — it is always in effect                  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Generic type checks happen at compile time;  │
│              │  the JVM sees only Object/bound at runtime"   │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Generics → Heap Pollution → Reflection        │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** Why does `new T[10]` fail at compile time even though the compiler knows `T` — what would go wrong if it allowed it?
**Q2.** How does Jackson's `TypeReference<List<String>>` trick work to "circumvent" type erasure?
**Q3.** Why are raw types a dangerous legacy pattern even though they compile successfully?

