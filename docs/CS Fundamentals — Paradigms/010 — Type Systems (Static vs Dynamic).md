---
layout: default
title: "Type Systems (Static vs Dynamic)"
parent: "CS Fundamentals — Paradigms"
nav_order: 10
permalink: /cs-fundamentals/type-systems-static-vs-dynamic/
number: "10"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Compiled vs Interpreted Languages, Variables, Imperative Programming
used_by: Strong vs Weak Typing, Metaprogramming, Type Inference, Generics
tags: #foundational, #intermediate, #pattern, #architecture
---

# 10 — Type Systems (Static vs Dynamic)

`#foundational` `#intermediate` `#pattern` `#architecture`

⚡ TL;DR — Static typing checks types at compile time; dynamic typing checks them at runtime — a fundamental trade-off between early error detection and flexibility.

| #10             | Category: CS Fundamentals — Paradigms                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Compiled vs Interpreted Languages, Variables, Imperative Programming |                 |
| **Used by:**    | Strong vs Weak Typing, Metaprogramming, Type Inference, Generics     |                 |

---

### 📘 Textbook Definition

A **type system** is a set of rules that a programming language uses to assign a _type_ to every expression and variable, and to verify that types are used consistently. In a **statically typed** language, type checking occurs at compile time — the compiler rejects programs where types are used incorrectly before any code runs. In a **dynamically typed** language, type checking occurs at runtime — type errors surface only when the offending code is actually executed. The type system determines what operations are legal on a value and provides guarantees about program correctness at a specific point in the development lifecycle.

---

### 🟢 Simple Definition (Easy)

In static typing, the programming language checks if you're using the right types of data _before_ running the program. In dynamic typing, it checks _while_ the program runs — so you might not discover a type error until you hit that line of code in production.

---

### 🔵 Simple Definition (Elaborated)

Every variable holds a value of a certain kind: a number, a string, an object. A type system defines those kinds and enforces that you don't mix them up unsafely. In Java (static), if you declare `int age = "thirty"`, the compiler refuses to compile it — you know about the error before shipping. In Python (dynamic), `age = "thirty"` is valid; only if you try `age + 1` at runtime will you get a `TypeError`. Static typing catches mistakes early but requires more upfront annotation. Dynamic typing allows faster prototyping but defers error detection to runtime — often to production.

---

### 🔩 First Principles Explanation

**The problem: machines have no inherent notion of "a name" vs "a salary".**

At the hardware level, every value is just bytes. Adding two numbers and adding a string to a number are both bit operations to the CPU. Nothing physically prevents you from treating a customer's name bytes as an integer and multiplying them. The result is nonsense.

**The constraint:** programs operate on data with semantic meaning. A system that allows arbitrary type mixing produces unpredictable, hard-to-debug behaviour.

**The insight:** attach a label (the _type_) to every piece of data, and enforce rules about which operations are legal on which labels.

**The question:** when should those rules be checked?

**Static typing — check before execution:**

```java
// Java: compiler enforces types
int age = 30;
String greeting = "hello";
int sum = age + greeting; // COMPILE ERROR: incompatible types
// Program never runs — error caught at compile time
```

**Dynamic typing — check during execution:**

```python
# Python: interpreter checks types as code runs
age = 30
greeting = "hello"
result = age + greeting  # TypeError raised at RUNTIME
# Works fine if this line never executes (e.g., in an untested branch)
```

**The trade-off:**

- Static: more work upfront (type annotations, generics), errors caught early, better IDE support, faster runtime.
- Dynamic: less ceremony, faster prototyping, errors surface later (runtime or in production).

Modern languages blur the line: TypeScript adds static typing to JavaScript; Kotlin has type inference; Python has type hints via `mypy`.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT a type system:

```c
// C allows this — type confusion is a security vulnerability
char buffer[8] = "hello";
int* ptr = (int*)buffer;   // treat string bytes as integer array
*ptr = 0x90909090;          // overwrite memory — undefined behaviour
// Buffer overflow / type confusion exploits work exactly this way
```

What breaks without it:

1. Data interpreted with the wrong type produces silent data corruption.
2. Security vulnerabilities (buffer overflows, type confusion attacks) become possible.
3. IDEs cannot autocomplete methods — they don't know what type a variable holds.
4. Refactoring is unsafe — renaming a field requires searching all usages manually.

WITH a static type system:
→ The compiler proves type consistency across the entire codebase before any code runs.
→ IDEs know the exact type of every variable — full autocomplete, refactoring, find-usages.
→ Refactoring is safe — the compiler flags every location that must change.
→ Performance: the compiler can allocate exact-size memory and avoid runtime type checks.

WITH a dynamic type system:
→ No type annotations required — faster to write exploratory or scripting code.
→ Duck typing: any object with the right methods works, regardless of declared type.
→ Runtime inspection and modification of types is natural.

---

### 🧠 Mental Model / Analogy

> Think of two post office systems. In System A (static), every package must be labelled with its contents category (Fragile / Electronics / Documents) before leaving the sender. Sorting staff refuse any unlabelled or mislabelled package. You know about problems before the package ships. In System B (dynamic), packages leave without labels. Sorting staff open and check each package when they handle it. Errors (a liquid bottle in a Documents bag) are discovered only when someone actually opens the box.

"Labelling before shipping" = compile-time type annotation
"Sorting staff refuse mislabelled packages" = compiler type error
"Checking when opened at destination" = runtime type error
"Category label" = declared type (e.g., `int`, `String`, `List<User>`)

System A catches problems earlier at the cost of more labelling work. System B is faster to ship but risks surprises at delivery.

---

### ⚙️ How It Works (Mechanism)

**Static Type Checking — compiler phase:**

```
┌──────────────────────────────────────────────────────┐
│              Java Compilation Pipeline               │
│                                                      │
│  Source.java                                         │
│      │                                               │
│      ▼                                               │
│  Parsing → AST (Abstract Syntax Tree)                │
│      │                                               │
│      ▼                                               │
│  Type Checker ← Symbol Table (variable → type map)  │
│      │  verifies: every expression has a valid type  │
│      │  rejects: incompatible assignments/calls      │
│      │                                               │
│      ▼                                               │
│  Bytecode Generator (only runs if type check passes) │
│      │                                               │
│      ▼                                               │
│  .class file (type information embedded in bytecode) │
└──────────────────────────────────────────────────────┘
```

**Dynamic Type Checking — interpreter at runtime:**

```
┌──────────────────────────────────────────────────────┐
│              Python Execution                        │
│                                                      │
│  Script.py                                           │
│      │                                               │
│      ▼                                               │
│  Bytecode compilation (no type checks)               │
│      │                                               │
│      ▼                                               │
│  Interpreter executes line by line                   │
│      │                                               │
│      ▼                                               │
│  Each operation: check types of operands at runtime  │
│      → if incompatible: raise TypeError              │
│      → if compatible: execute operation              │
└──────────────────────────────────────────────────────┘
```

**Type Inference — static typing without explicit annotations:**

```kotlin
// Kotlin: static typing with full inference — no annotations needed
val name = "Alice"   // inferred as String at compile time
val age  = 30        // inferred as Int

name + age  // COMPILE ERROR — String + Int — caught at compile time
            // without the programmer writing String/Int anywhere
```

---

### 🔄 How It Connects (Mini-Map)

```
Variables + Memory Model
        │
        ▼
Type Systems (Static vs Dynamic)  ◄── Compiled vs Interpreted
(you are here)
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
Strong vs Weak Typing               Type Inference (Kotlin, Haskell)
        │                                      │
        ▼                                      ▼
Metaprogramming / Reflection          Generics (Java, C#)
        │
        ▼
  TypeScript (static typing for JS)
```

---

### 💻 Code Example

**Example 1 — Static vs Dynamic error detection:**

```java
// Java (static): caught at compile time
public class Example {
    public static void main(String[] args) {
        int age = 30;
        // Compile error: incompatible types: String cannot be
        // converted to int
        age = "thirty"; // ← red underline in IDE before running
    }
}
```

```python
# Python (dynamic): only caught when this line executes
def calculate_retirement(age):
    return 65 - age   # TypeError if age is a string

calculate_retirement(30)       # works fine
calculate_retirement("thirty") # TypeError raised HERE at runtime
```

**Example 2 — Duck typing in Python (dynamic typing advantage):**

```python
# Works with ANY object that has a .speak() method
# No interface or base class required
def make_sound(animal):
    animal.speak()   # type checked at runtime

class Dog:
    def speak(self): print("Woof")

class Robot:
    def speak(self): print("Beep")

make_sound(Dog())    # → Woof
make_sound(Robot())  # → Beep  (no common type required)
```

**Example 3 — Gradual typing: TypeScript over JavaScript:**

```typescript
// TypeScript: adds static types to JavaScript
function greet(name: string): string {
  return "Hello, " + name;
}

greet("Alice"); // OK
greet(42); // Compile error: Argument of type 'number'
// is not assignable to parameter of type 'string'
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                 |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dynamic typing means no types                          | Every value in a dynamic language has a type — it is just not declared on the variable; Python integers are still integers                                              |
| Static typing always requires writing type annotations | Languages with type inference (Kotlin, Haskell, Rust) are statically typed but require few or no annotations — the compiler infers types                                |
| Dynamic typing is always less safe                     | A statically typed language with a weak type system (C) allows more dangerous implicit conversions than a dynamically typed language with a strong type system (Python) |
| TypeScript eliminates all JavaScript type errors       | TypeScript catches errors at compile time; type assertions (`as any`) and untyped third-party code can still introduce runtime type errors                              |
| Static typing is always slower to develop              | With modern IDEs, type inference, and autocompletion, statically typed code often develops faster due to IDE support and fewer debugging sessions                       |

---

### 🔥 Pitfalls in Production

**Trusting dynamic types from external input without validation**

```python
# BAD: assume JSON input has the expected type
def process_order(data: dict):
    total = data["quantity"] * data["price"]
    # If price arrives as "9.99" (string), TypeError at runtime

# GOOD: validate and coerce at the boundary
def process_order(data: dict):
    quantity = int(data["quantity"])    # explicit coercion
    price    = float(data["price"])     # with error handling
    total = quantity * price
```

Type errors from external JSON, CSV, or API data are a leading cause of production crashes in dynamically typed services.

---

**Overusing `Object` / `Any` in static languages to avoid typing**

```java
// BAD: loses all type safety — ClassCastException waiting to happen
Map<String, Object> config = loadConfig();
int timeout = (int) config.get("timeout"); // ClassCastException if it's Long

// GOOD: use typed config classes
@ConfigurationProperties(prefix = "app")
public class AppConfig {
    private int timeout;  // type-safe, validated at startup
    // getter...
}
```

---

**Missing `null` as a type-system failure**

```java
// BAD: null is not part of the type system — NullPointerException at runtime
String name = getUser().getName(); // getUser() returns null? NPE!

// GOOD: use Optional to make null explicit in the type system
Optional<User> user = userRepository.findById(id);
String name = user.map(User::getName).orElse("Unknown");
```

Null is the "billion-dollar mistake" (Hoare, 1965): a value of any type that bypasses all type checking.

---

### 🔗 Related Keywords

- `Compiled vs Interpreted Languages` — compiled languages typically have static type checking; interpreted languages are often dynamically typed
- `Strong vs Weak Typing` — orthogonal dimension: how strictly a language enforces type rules, regardless of when they are checked
- `Metaprogramming` — dynamic type systems enable richer runtime metaprogramming; static type systems constrain it
- `Generics` — Java/C# mechanism for writing type-safe code that works across multiple static types
- `Type Inference` — static typing without explicit annotations; used in Kotlin, Haskell, Rust
- `TypeScript` — adds a static type layer to JavaScript without changing its runtime behaviour
- `Null Safety` — Kotlin and Rust eliminate null from the type system by making Optional/Option types explicit
- `Duck Typing` — the dynamic typing style where type compatibility is determined by behaviour, not declaration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Static: types verified at compile time    │
│              │ Dynamic: types checked at runtime         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Static: large teams, long-lived codebases │
│              │ Dynamic: scripting, prototyping, DSLs     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Static: not "avoid" — choose based on     │
│              │ team size and maintenance horizon         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Static typing is a pre-flight checklist; │
│              │ dynamic typing is learning to fly by      │
│              │ crashing and recovering."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strong vs Weak Typing → Type Inference    │
│              │ → Generics → TypeScript → Null Safety     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kotlin is statically typed, yet a Kotlin function that calls a Java method returning `String` (without `@NotNull`) receives a value with type `String!` — the platform type. This platform type bypasses Kotlin's null safety. Describe the exact conditions under which a Kotlin application crashes with a NullPointerException despite using a statically typed, null-safe language, and what engineering practice prevents this at the integration boundary.

**Q2.** Python's `mypy` type checker and Java's compiler both perform static type analysis, yet a `mypy`-clean Python codebase can still raise `TypeError` at runtime in ways a Java codebase cannot. Identify two specific mechanisms in Python's runtime model that allow runtime type errors even after passing full static analysis, and explain why they do not exist in the JVM model.
