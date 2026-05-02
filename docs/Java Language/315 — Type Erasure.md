---
layout: default
title: "Type Erasure"
parent: "Java Language"
nav_order: 315
permalink: /java-language/type-erasure/
number: "315"
category: Java Language
difficulty: ★★★
depends_on: "Generics, JVM Bytecode, Reflection"
used_on: "Generic collections, Spring framework internals, serialization, Reflection API"
tags: #java, #generics, #type-erasure, #jvm, #bytecode, #runtime
---

# 315 — Type Erasure

`#java` `#generics` `#type-erasure` `#jvm` `#bytecode` `#runtime`

⚡ TL;DR — **Type Erasure** removes all generic type parameters at compile time: `List<String>` becomes `List` in bytecode. Generic safety exists only at compile time; the JVM never knows `T`.

| #315            | Category: Java Language                                                        | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Generics, JVM Bytecode, Reflection                                             |                 |
| **Used on:**    | Generic collections, Spring framework internals, serialization, Reflection API |                 |

---

### 📘 Textbook Definition

**Type Erasure** is the Java compiler's mechanism for implementing generics: all type parameters are removed ("erased") during compilation, replaced by their erasure (either `Object` for unbounded type parameters, or the leftmost bound for bounded type parameters). The resulting bytecode is identical to what a pre-Java 5 compiler would produce for the equivalent raw-type code. Consequence: at runtime, `List<String>` and `List<Integer>` are both just `List.class`; no generic type information is preserved. The compiler inserts necessary casts and generates bridge methods to maintain polymorphism. This design was chosen for backward compatibility with pre-Java 5 bytecode and JVMs.

---

### 🟢 Simple Definition (Easy)

Java's generics are a compile-time illusion. `List<String>` in your source code: the compiler uses it to check your types. But in the compiled `.class` file: it becomes just `List`. The JVM never sees `<String>`. This means: you can't ask "is this a `List<String>` at runtime?" — the JVM only knows it's a `List`. Generics are erased — type safety exists only during compilation.

---

### 🔵 Simple Definition (Elaborated)

Java 5 added generics. But the JVM (bytecode format) wasn't redesigned — it still uses raw types. The solution: generics are a compile-time feature only. The compiler checks your generic types, then strips them before producing bytecode. At runtime, `Box<String>` and `Box<Integer>` are both `Box`. This backward-compatible approach let existing JVMs and libraries work unchanged. The cost: you can't do things that require generic type information at runtime (`instanceof List<String>`, `new T()`, `T.class`). C#/.NET took the opposite approach — reified generics — but this required a new CLR.

---

### 🔩 First Principles Explanation

**What the compiler does: erasure rules and bridge methods:**

```
ERASURE RULES:

  1. Unbounded type parameter (T) → replaced by Object:
     Box<T>         compiles to    Box            (raw type)
     T get()        compiles to    Object get()
     void set(T v)  compiles to    void set(Object v)

  2. Bounded type parameter (T extends Comparable<T>) → replaced by leftmost bound:
     <T extends Comparable<T>> T max(T a, T b)
     compiles to:  Comparable max(Comparable a, Comparable b)

  3. Multiple bounds (<T extends Serializable & Comparable<T>>) → leftmost bound (Serializable)

  4. Wildcard (? extends Number) → erased to Number (the bound)
     Wildcard (?) → erased to Object

SOURCE vs BYTECODE:

  Source:
  public class Stack<T> {
      private List<T> elements = new ArrayList<>();
      public void push(T item) { elements.add(item); }
      public T pop() { return elements.remove(elements.size() - 1); }
  }

  After erasure (equivalent bytecode):
  public class Stack {
      private List elements = new ArrayList();       // T erased to Object
      public void push(Object item) { elements.add(item); }
      public Object pop() { return elements.remove(elements.size() - 1); }
      // Compiler inserts cast at use site: (T) pop()
  }

BRIDGE METHODS (preserving polymorphism after erasure):

  Source:
  interface Comparable<T> { int compareTo(T other); }

  class MyString implements Comparable<MyString> {
      @Override
      public int compareTo(MyString other) {
          return this.value.compareTo(other.value);
      }
  }

  Problem: after erasure, Comparable becomes compareTo(Object), but MyString has compareTo(MyString).
  The signatures don't match → polymorphism breaks.

  Compiler-generated bridge method (synthetic):
  public int compareTo(Object other) {        // matches erased interface method
      return this.compareTo((MyString) other); // delegates to typed method
  }

  javap -verbose MyString.class shows:
  compareTo(MyString): flags: ACC_PUBLIC
  compareTo(Object):   flags: ACC_PUBLIC, ACC_BRIDGE, ACC_SYNTHETIC

TYPE ERASURE + UNCHECKED WARNINGS:

  @SuppressWarnings("unchecked") suppresses warnings from unchecked casts.
  These casts exist because erasure loses type info that the compiler used to know.

  Example — Jackson deserialization:
  List<User> users = objectMapper.readValue(json, List.class);
  // compiler: "unchecked assignment: List to List<User>"
  // risk: if JSON contains non-User objects, ClassCastException at point of use

  FIX — TypeReference preserves generic type info for Jackson:
  List<User> users = objectMapper.readValue(json, new TypeReference<List<User>>(){});
  // TypeReference subclass: superclass generic type info survives erasure (see below)

PRESERVING GENERIC TYPE INFO AT RUNTIME:

  Java does NOT erase type info from class/field/method SIGNATURES — only from instance usage.

  Field declaration:  List<String> myField;
  getClass().getDeclaredField("myField").getGenericType()
  → ParameterizedType: java.util.List<java.lang.String>  ← type info preserved!

  Superclass generic type (TypeReference trick):
  class TypeRef<T> {}
  class UserListRef extends TypeRef<List<User>> {}  // superclass type preserved!

  UserListRef ref = new UserListRef();
  ((ParameterizedType) ref.getClass().getGenericSuperclass())
      .getActualTypeArguments()[0]  // → List<User>

  Spring's ResolvableType:
  ResolvableType.forClass(UserService.class)
      .getInterfaces()[0].getGeneric(0)  // resolves T in implemented generic interface
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Type Erasure (alternative: reified generics like C#):

- Would require JVM bytecode changes for every generics use
- All existing pre-Java 5 `.class` files and libraries: incompatible with new JVM
- New JVM required for existing `.jar` libraries to work with generics

WITH Type Erasure:
→ All pre-Java 5 `.class` files work unchanged with Java 5 JVM. `java.util.Collections` library didn't need to be recompiled. Backward compatibility preserved at the cost of runtime type information.

---

### 🧠 Mental Model / Analogy

> A shipping warehouse that erases package labels before putting them on trucks. When packages arrive (compile time), they're labeled "Glass: handle carefully" or "Electronics: dry only" — the warehouse system checks these labels and handles them correctly. But when loaded onto trucks (bytecode), all labels are stripped — every box just says "Contents: Object." The trucks (JVM) don't know what's inside. If you try to check "is this box labeled Glass?" at the truck depot (runtime instanceof check on generic type), you can't — the label was erased. But the warehouse (compiler) already verified everything was packed correctly before labels were stripped.

"Package labels (Glass, Electronics)" = generic type parameters (`<String>`, `<Integer>`)
"Warehouse checks labels" = compiler enforces generic type safety at compile time
"Labels stripped before trucks" = type erasure: `List<String>` → `List` in bytecode
"Trucks: all boxes are 'Contents: Object'" = JVM sees only raw types
"Can't check label at truck depot" = can't do `instanceof List<String>` at runtime
"Warehouse verified everything correctly" = trust the compile-time checks

---

### ⚙️ How It Works (Mechanism)

```
COMPILATION PIPELINE:

  Source code with generics
        │ javac: type checking
        ▼
  AST with full generic type information
        │ javac: erasure phase
        ▼
  Bytecode: raw types + inserted casts + bridge methods
        │
        ▼
  JVM: executes bytecode, no generic type awareness

RUNTIME REFLECTION — what survives erasure:

  Survives: class/field/method declaration signatures (from .class file metadata)
  Erased:   local variable types, instance/cast expressions

  // Survives:
  class Service<T extends Repository> {}
  Service.class.getTypeParameters()[0].getBounds()  // → Repository

  // Erased:
  void method() {
      List<String> list = new ArrayList<>();  // local variable: type erased
      // list's type is ONLY known to compiler, not stored in bytecode
  }
```

---

### 🔄 How It Connects (Mini-Map)

```
Java Generics added in Java 5 (backward compatible)
        │
        ▼
Type Erasure ◄──── (you are here)
(generic type params removed at compile time; JVM sees raw types)
        │
        ├── Generics: type erasure is the implementation mechanism for Java generics
        ├── Bridge Methods: compiler generates to preserve polymorphism after erasure
        ├── Reflection: getGenericType() / getGenericSuperclass() survive erasure
        └── Spring ResolvableType: framework tool to navigate surviving type info
```

---

### 💻 Code Example

```java
// WHAT SURVIVES ERASURE — field generic type:
class Container<T> {
    private List<T> items;  // generic type in FIELD DECLARATION survives!
}

Field field = Container.class.getDeclaredField("items");
System.out.println(field.getGenericType());
// → java.util.List<T>  (T is the class type parameter)

// JACKSON TypeReference — preserves List<User> via superclass trick:
List<User> users = objectMapper.readValue(json,
    new TypeReference<List<User>>() {}  // anonymous subclass — generic supertype preserved
);

// SPRING ResolvableType:
class OrderHandler implements EventHandler<OrderEvent> {}

ResolvableType type = ResolvableType.forClass(OrderHandler.class);
ResolvableType eventType = type.getInterfaces()[0].getGeneric(0);
System.out.println(eventType);  // → OrderEvent

// TYPE TOKENS — passing Class<T> to preserve type:
public <T> T deserialize(String json, Class<T> type) {
    return objectMapper.readValue(json, type);  // use Class<T> as type token
}
User u = deserialize(json, User.class);  // type safe: Class<User> is a runtime value

// WHAT DOESN'T WORK — erased at runtime:
// if (list instanceof List<String>) { }  // COMPILE ERROR
// T t = new T();                          // COMPILE ERROR
// Class<T> clazz = T.class;              // COMPILE ERROR
```

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Type erasure means ALL generic information is lost at runtime | Generic type information in class, field, and method DECLARATIONS is preserved in `.class` file metadata (Signature attribute). `getGenericType()`, `getGenericSuperclass()`, `getGenericInterfaces()` return full generic type info. Only instance-level usage (local variables, cast expressions) is erased.                     |
| C# generics are "better" than Java generics unconditionally   | C#'s reified generics allow `new T()`, `typeof(T)`, and `T[]` — more powerful. But reification requires all generic code to exist in every compiled version (increases binary size, requires more JIT compilation). Java's erasure compiles once to one bytecode version — simpler compilation model. Each approach has tradeoffs. |
| Type erasure is a bug or design flaw                          | It was a deliberate choice for backward compatibility. All existing Java libraries and bytecode remained compatible with Java 5 generics without recompilation. The cost (no runtime generic types) was considered acceptable given the benefit (universal compatibility).                                                         |

---

### 🔥 Pitfalls in Production

**Unchecked cast causes ClassCastException far from the problematic code:**

```java
// ANTI-PATTERN — raw type cast hides type mismatch:

// Service returns raw List:
public List getData(String type) {
    if ("users".equals(type)) return userRepository.findAll();
    if ("orders".equals(type)) return orderRepository.findAll();
    return Collections.emptyList();
}

// Caller — unchecked cast:
@SuppressWarnings("unchecked")
List<User> users = (List<User>) dataService.getData("orders");  // WRONG: orders!
// No exception here — the cast "succeeds" because List<User> erases to List
// ClassCastException thrown when iterating:
for (User u : users) {  // CRASH here: Order cannot be cast to User
    System.out.println(u.getName());
}
// The bug is 10+ lines from the actual mistake (the wrong getData call).

// FIX — typed service methods, no raw types:
public List<User> getUsers() { return userRepository.findAll(); }
public List<Order> getOrders() { return orderRepository.findAll(); }
// Compiler enforces correct types; no casts needed.

// Or type-safe generic factory:
public <T> List<T> getAll(Class<T> type) {
    return repository.findAll(type);  // JPA typed query
}
List<User> users = getAll(User.class);  // safe: Class<T> as type token
```

---

### 🔗 Related Keywords

- `Generics` — type erasure is the implementation mechanism for Java's generic type system
- `Bridge Methods` — compiler-generated synthetic methods to preserve polymorphism after erasure
- `Reflection` — `getGenericType()` reads surviving generic type info from class metadata
- `Spring ResolvableType` — Spring's abstraction for navigating generic type information
- `Heap Pollution` — consequence of mixing raw types and generics due to erasure

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Generic type params stripped at compile  │
│              │ time. JVM sees only raw types.           │
│              │ Casts inserted; bridge methods generated.│
├──────────────┼───────────────────────────────────────────┤
│ ERASED       │ Local variable generic types;            │
│              │ instanceof on generic type;              │
│              │ new T(); T.class; T[] creation           │
├──────────────┼───────────────────────────────────────────┤
│ SURVIVES     │ Class/field/method DECLARATION generic   │
│              │ types (Signature attribute in .class)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Labels checked at packing (compile),   │
│              │  stripped before truck (bytecode).       │
│              │  JVM just sees 'Object inside.'"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Generics → Bounded Wildcards →            │
│              │ Bridge Methods → Reflection → ResolvableType│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Gson and Jackson both need to deserialize JSON into generic types like `List<User>`. They solve the type erasure problem differently: Jackson uses `TypeReference<T>` (anonymous subclass captures superclass generic type), while Gson uses `TypeToken<T>`. Both exploit the fact that superclass generic type info survives erasure in `.class` metadata. Can you explain exactly WHY `new TypeReference<List<User>>(){}` captures `List<User>` at runtime — what JVM mechanism preserves this?

**Q2.** Java 17+ has `@SafeVarargs` and `@SuppressWarnings("unchecked")` to handle specific erasure-related warnings. But heap pollution (mixing raw types and parameterized types) can cause `ClassCastException` in code that never explicitly casts. Can you construct an example where a `ClassCastException` is thrown in a method that has no explicit cast in its source code — caused purely by type erasure and unchecked additions to a raw list?
