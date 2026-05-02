---
layout: default
title: "Varargs"
parent: "Java Language"
nav_order: 318
permalink: /java-language/varargs/
number: "0318"
category: Java Language
difficulty: ★★☆
depends_on: Generics, Type Erasure, Arrays
used_by: Stream API, Method References, Functional Interfaces
related: Generics, Method References, Autoboxing / Unboxing
tags:
  - java
  - varargs
  - syntax
  - intermediate
  - tradeoff
---

# 0318 — Varargs

⚡ TL;DR — Varargs (`Type... args`) lets a method accept any number of arguments of a type, transparently packing them into an array — eliminating overload explosion while hiding array syntax from callers.

| #0318 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Generics, Type Erasure, Arrays | |
| **Used by:** | Stream API, Method References, Functional Interfaces | |
| **Related:** | Generics, Method References, Autoboxing / Unboxing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Java 5, to write a method that accepted a variable number of arguments you had to overload it for each count — `log(String msg)`, `log(String msg, Object arg1)`, `log(String msg, Object arg1, Object arg2)`, etc. — or accept an explicit array: `log(String msg, Object[] args)`. The overload approach explodes combinatorially. The array approach pollutes every callsite with `new Object[] { ... }` construction noise. `String.format()` would require the caller to write `format("%s %s", new Object[]{"hello", "world"})` — clumsy and error-prone.

**THE BREAKING POINT:**
The Java logging and formatting APIs needed to accept an arbitrary number of arguments. Every formatting call wrote noise: `logger.log(Level.INFO, "Order {0} placed by {1}", new Object[]{orderId, userId})`. On a codebase with 10,000 log statements, that is 10,000 `new Object[]` allocations in syntax with zero semantic value.

**THE INVENTION MOMENT:**
This is exactly why **Varargs** were created — to let the compiler handle the array packaging automatically, so callers write `log("Order {} placed by {}", orderId, userId)` naturally.

---

### 📘 Textbook Definition

**Varargs** (variable-arity methods) are a Java feature introduced in Java 5 that allows declaring a method with the last parameter as `Type... paramName`, which accepts zero or more arguments of that type. The compiler packages all matching arguments into an array at the call site. Inside the method body, `paramName` is an ordinary array. If the caller explicitly passes an array of the correct type, no wrapping occurs — the array is passed directly. Varargs methods can be overloaded, but are matched last in overload resolution to avoid ambiguity with more specific signatures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Varargs lets you pass any number of arguments to a method without creating an array explicitly.

**One analogy:**
> A restaurant buffet takes any number of items on your plate. You don't hand the cashier a tray and say "here is my array of items" — you just pile them on. The cashier internally counts what you took. Varargs is the same: you pass arguments naturally; the method receives them as an array internally.

**One insight:**
Varargs is 100% syntactic sugar — `log("msg", a, b, c)` compiles to exactly the same bytecode as `log("msg", new Object[]{a, b, c})`. The value is purely in call-site readability and eliminating the visual noise of `new Object[]{}` at every callsite that uses a variable-number API.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Varargs parameter must be the last parameter in a method signature.
2. At the call site, the compiler implicitly creates `new T[]{ args... }` unless the caller passes an explicit array of type `T[]`.
3. Inside the method, the varargs parameter behaves exactly as a `T[]` array — null-safe iteration, length access, etc.

**DERIVED DESIGN:**
Given invariant 2, there is no performance magic in varargs — every call that does not pass an explicit array allocates a new array object on the heap. This means varargs on hot paths generates garbage. For `String.format("...", a, b)`, an `Object[]` of length 2 is heap-allocated per call. High-frequency APIs like loggers mitigate this with the isEnabled check pattern before varargs expansion.

**Overload resolution order:** The compiler resolves overloads as:
1. Methods without varargs that are applicable
2. Methods with varargs, as a last resort

This means `log(String s)` is preferred over `log(String... args)` when called with a single String argument.

```
┌────────────────────────────────────────────────┐
│         Varargs Compilation Path               │
│                                                │
│  Source:  format("%s %s", first, last)         │
│      ↓ javac                                   │
│  Bytecode: format("%s %s",                     │
│              new Object[]{first, last})        │
│                                                │
│  Source:  format("%s", arr)  // arr is String[]│
│      ↓ javac                                   │
│  Bytecode: format("%s", arr) // no wrapping!   │
│  (direct array pass — no new array created)    │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Clean call-site syntax for variable-argument methods; eliminates overload explosion; integrates naturally with arrays (no double-wrapping).
**Cost:** Heap allocation per call unless an explicit array is passed; heap pollution warning with generic varargs; last-parameter restriction limits flexibility; overload resolution surprises when mixing varargs and non-varargs signatures.

---

### 🧪 Thought Experiment

**SETUP:**
A method called 10,000 times per second that logs structured events with varying numbers of context fields.

**WHAT HAPPENS WITHOUT VARARGS (explicit array):**
```java
// Caller (10,000 times/second):
logger.log("Order created",
    new Object[]{orderId, userId, amount});
// Each call: new Object[3] allocated
// GC processes ~10,000 Object[] per second
```

**WHAT HAPPENS WITH VARARGS:**
```java
// Caller (same 10,000 times/second):
logger.log("Order created", orderId, userId, amount);
// Compile: new Object[]{orderId, userId, amount}
// Runtime: IDENTICAL allocation — same GC pressure
```

**THE INSIGHT:**
Varargs does not change the performance characteristics — it changes only the call-site syntax. The array allocation is identical. The real gains are readability and maintainability (no `new Object[]{}` noise), not throughput. Developers who believe varargs APIs are faster than array APIs are mistaken.

---

### 🧠 Mental Model / Analogy

> Varargs is like a phone contact that accepts "any number of email addresses." You type `add(alice@a.com, bob@b.com, carol@c.com)` in the UI. Behind the scenes, the system builds a list `[alice, bob, carol]` and stores it. You never see the list construction — you just separate addresses with commas like you naturally would.

- "Typing multiple emails with commas" → calling with multiple args.
- "System building a list behind the scenes" → compiler inserting `new T[]{}` at call site.
- "Contact stored as list internally" → method body receives a `T[]` array.

Where this analogy breaks down: You can pass an existing contact list directly (explicit array), and the system won't re-list it. Varargs also accepts an explicit array directly without re-wrapping — an important optimization path.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
With varargs you can call a method with as many arguments as you like: `add(1, 2, 3)` or `add(1, 2, 3, 4, 5)`. The method sees them all. Without varargs, the programmer has to create an array: `add(new int[]{1, 2, 3})`.

**Level 2 — How to use it (junior developer):**
Declare the last parameter with `...`: `void log(String msg, Object... args)`. Inside the method, use `args` as an array. At call sites, just pass comma-separated values. Do not add `new Object[]{}` — the compiler does it. Pass `null` to get a `null` args array (not zero-length). To pass an explicit array, pass it directly — no wrapping.

**Level 3 — How it works (mid-level engineer):**
The compiler applies varargs packing only when the last argument at the call site is not already an array of the varargs component type. When passing a `String[]` to a `String... args` method, the array passes directly. The method signature in bytecode is just `(String[])` — varargs is not encoded in bytecode operand types, only in method metadata flags (`ACC_VARARGS`). This is visible in `javap` output.

**Level 4 — Why it was designed this way (senior/staff):**
The "last parameter only" rule exists to prevent ambiguity in overload resolution — if two varargs parameters were allowed, the compiler couldn't determine which arguments belong to which vararg group. The `@SafeVarargs` annotation was added in Java 7 to suppress the heap pollution warning for methods that provably don't expose the varargs array outside the method. The annotation is a contract on the method author, not a compiler-verified guarantee — a known weakness. Java 9 added `@SafeVarargs` support on private and final methods.

---

### ⚙️ How It Works (Mechanism)

**Declaration and bytecode:**
```java
// Source:
void print(String... values) {
    for (String v : values) System.out.println(v);
}
```
After compilation, `javap -v MyClass.class` shows:
- Signature: `([Ljava/lang/String;)V` — plain String array
- Access flags include `ACC_VARARGS` — marks it as varargs for reflection

**Array allocation by the compiler:**
```java
// Source call:
print("a", "b", "c");

// Compiled to:
print(new String[]{"a", "b", "c"});
```

**Direct array pass (no double-wrap):**
```java
String[] arr = {"x", "y"};
print(arr);          // passed directly, no new array
print(arr, "z");     // ERROR: String[] is Object, not String — ambiguous
```

**Overload resolution priority:**
```java
void foo(String s) { System.out.println("single"); }
void foo(String... s) { System.out.println("varargs"); }

foo("hello"); // prints "single" — non-varargs wins
foo("a", "b"); // prints "varargs"
foo();         // prints "varargs"
```

**Generic varargs warning:**
```java
// Compiler warning: "unchecked or unsafe operations"
static <T> void unsafe(T... args) {
    // T is erased to Object — args is actually Object[]
    // Exposing it creates heap pollution
}

// Suppress when safe (method doesn't expose the array):
@SafeVarargs
static <T> List<T> listOf(T... args) {
    return Collections.unmodifiableList(
        Arrays.asList(args)
    );
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[Caller: format("Hello %s %s", first, last)]
    → [Compiler: packs to new Object[]{first, last}]
    → [Call: format("Hello %s %s", Object[])]  ← YOU ARE HERE
    → [Method body: iterates args array]
    → [Returns formatted string]
```

**FAILURE PATH:**
```
[Caller passes null: format("msg", null)]
    → [Compiler: null passed as the array itself]
    → [args == null inside method]
    → [NullPointerException on args.length or iteration]
    → [Fix: use explicit new Object[]{null} or check null]
```

**WHAT CHANGES AT SCALE:**
At high-frequency call sites (logging frameworks, tracing), every varargs call allocates a new array. SLF4J's two-argument overloads `logger.debug(String, Object, Object)` exist specifically to avoid the varargs array allocation for the common 1–2 argument case. Log4j 2 also uses this pattern. At 1M log calls/second with 3+ args, varargs-caused GC pressure is measurable.

---

### 💻 Code Example

Example 1 — Basic varargs method:
```java
// Declare: last parameter uses ...
int sum(int... numbers) {
    int total = 0;
    for (int n : numbers) total += n;
    return total;
}

sum(1, 2, 3);          // returns 6
sum(10, 20);           // returns 30
sum();                 // returns 0 — zero-arg allowed
```

Example 2 — Varargs with other parameters:
```java
// Must be LAST parameter
String format(String template, Object... args) {
    return String.format(template, args);
}

format("Hello, %s!", "World");
format("%d + %d = %d", 1, 2, 3);
```

Example 3 — null trap and fix:
```java
void printAll(String... items) {
    if (items == null) { // null passed as the array
        System.out.println("null");
        return;
    }
    Arrays.stream(items).forEach(System.out::println);
}

printAll((String) null);     // single null element
// [null] printed — null cast to String, wrapped in array

printAll((String[]) null);   // array itself is null
// "null" printed — items == null triggers null check

printAll(null);
// Warning: ambiguous — null could be String or String[]
// Use explicit cast to clarify
```

Example 4 — @SafeVarargs (correct use):
```java
// BAD: no @SafeVarargs — compiler warns
static <T> List<T> combine(List<T>... lists) {
    // Exposes the lists[] array via Arrays.asList —
    // NOT safe (heap pollution)
    List<T> result = new ArrayList<>();
    for (List<T> l : lists) result.addAll(l);
    return result;
}

// GOOD: @SafeVarargs when array is not exposed
@SafeVarargs
static <T> List<T> combine(List<T>... lists) {
    // lists[] is not exposed outside this method
    List<T> result = new ArrayList<>();
    for (List<T> l : lists) result.addAll(l);
    return result;
}
```

---

### ⚖️ Comparison Table

| Approach | Call Syntax | Allocation | Type Safety | Best For |
|---|---|---|---|---|
| **Varargs** | `m(a, b, c)` | New array per call | Good (generic: warning) | General variable-arg APIs |
| Explicit Array | `m(new T[]{a,b,c})` | New array per call | Full | Performance-critical paths |
| List parameter | `m(List.of(a,b,c))` | List wrapper | Full | When collection needed downstream |
| Overloads (1-4 args) | `m(a)`, `m(a,b)`, ... | None | Full | Hot-path performance (SLF4J style) |

How to choose: Use varargs for readability when call frequency is moderate. Use overloads for 1–3 common argument counts when the method is on a hot path (logging, tracing). Use explicit arrays or `List` when the collection needs to be reused or iterated multiple times.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Varargs avoids array allocation and is faster | Varargs and explicit array pass generate identical bytecode. The array is always allocated. There is no performance benefit to varargs — only syntax benefit |
| You can have varargs as any parameter, not just last | Varargs must be the LAST parameter. `void m(String... a, int b)` is a compile error |
| Passing null to varargs always gives a null element | `null` is ambiguous — it can be interpreted as a null array (args == null) or a null element (args = [null]). Always cast: `method((String) null)` for null element, `method((String[]) null)` for null array |
| `@SafeVarargs` makes generic varargs type-safe | `@SafeVarargs` suppresses the compiler warning but does NOT make the operation safe. It is a contract that the developer asserts the method doesn't expose the varargs array. If the array IS exposed, heap pollution still occurs |
| A varargs method with 0 args is called with neither args nor array | Zero-arg calls pass an empty array (`new T[]{}`), not null. `args.length == 0` is the correct check for no arguments |

---

### 🚨 Failure Modes & Diagnosis

**Heap Pollution via Generic Varargs Exposure**

**Symptom:**
`ClassCastException` thrown at a site far removed from the call that injected the wrong type. Difficult to trace.

**Root Cause:**
A generic varargs method stored or returned the varargs array. Because generics erase to `Object[]` at runtime, the array can hold any type. Accessing it as `T[]` later produces a `ClassCastException`.

**Diagnostic:**
```bash
# Compiler warning: "unchecked or unsafe operations"
javac -Xlint:unchecked *.java | grep "varargs"
# Any method with generic varargs (T...) without
# @SafeVarargs is a potential heap pollution site
```

**Fix:**
```java
// BAD: exposes the varargs array
@SafeVarargs  // WRONG: shouldn't suppress — it IS unsafe
static <T> T[] toArray(T... elements) {
    return elements; // returning erased Object[] as T[]
}
String[] s = toArray("a", "b"); // WORKS
Object[] o = toArray("a", 42);  // WORKS (heap polluted!)
String first = s[0]; // ClassCastException later!

// GOOD: copy to typed array or use List
static <T> List<T> toList(T... elements) {
    return new ArrayList<>(Arrays.asList(elements));
}
```

**Prevention:** Never return or store the varargs array directly from a generic method. Copy into a typed structure first.

---

**NullPointerException from Unguarded null Array**

**Symptom:**
`NullPointerException` on the first line that accesses the varargs parameter inside the method body.

**Root Cause:**
Caller explicitly passed `null` as the array argument (not as an element). `args == null` rather than `args.length == 0`.

**Diagnostic:**
```bash
# Add null guard at method start:
Objects.requireNonNull(args, "args must not be null");
# Or permissive:
if (args == null) args = new T[0];
```

**Fix:**
```java
// BAD: no null check
void log(Object... args) {
    Arrays.stream(args).forEach(System.out::println);
    // NPE when args is null
}

// GOOD: explicit null guard
void log(Object... args) {
    if (args == null || args.length == 0) return;
    Arrays.stream(args).forEach(System.out::println);
}
```

**Prevention:** Always add a null guard at the start of varargs methods that will be called from external code.

---

**Overloading Ambiguity with Varargs**

**Symptom:**
Compiler error "ambiguous method call" or unexpected overload selected when calling a varargs method.

**Root Cause:**
Multiple applicable methods when the varargs version should be a last resort but another candidate also matches.

**Diagnostic:**
```bash
javac -verbose MyClass.java 2>&1 | grep "ambiguous"
# Shows which two methods conflict
```

**Fix:**
```java
// Ambiguous: which overload for single String arg?
void process(String s) { System.out.println("S"); }
void process(String... ss) { System.out.println("VA"); }

process("x");  // "S" — non-varargs wins (correct)
process("x", "y");  // "VA" — only varargs works

// Ambiguous with subtype:
void process(Object o) { }
void process(String... ss) { }
process("x");  // uses Object overload, not varargs
```

**Prevention:** Avoid overloading varargs methods with methods accepting a single argument of the component type or its supertype — the resolution order is surprising.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Arrays` — varargs parameters are arrays inside the method body; understanding arrays is prerequisite
- `Generics` — generic varargs (`T... args`) interacts with generics and causes heap pollution warnings
- `Type Erasure` — generic varargs are erased to `Object[]`, creating the heap pollution risk explained in failure modes

**Builds On This (learn these next):**
- `Method References` — varargs methods can be referenced with method references, but the array-wrapping semantics matter
- `Stream API` — `Stream.of(T... values)` and similar factory methods use varargs; understanding varargs explains their allocation characteristics

**Alternatives / Comparisons:**
- `Method References` — an alternative to varargs for passing multiple operations
- `Autoboxing / Unboxing` — autoboxing interacts with varargs when primitive arrays are passed to `Object...` methods

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Type... syntax making last param accept   │
│              │ zero or more arguments as an array        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Before varargs, variable-arg methods      │
│ SOLVES       │ required overloads or explicit new T[]{}  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Varargs is pure syntax sugar — compile    │
│              │ result is identical to explicit array     │
│              │ pass. No performance benefit over arrays. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ APIs where callers need to pass 0–N args  │
│              │ of the same type, for readability         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Hot paths (log/trace at 1M+/sec) — use   │
│              │ overloads for 1-3 args instead            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Clean call syntax vs heap allocation per  │
│              │ call; generic varargs adds heap pollution  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Any number of args, one array inside"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Method References → Functional Interfaces │
│              │ → Lambda Expressions                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** SLF4J provides both `logger.debug(String format, Object arg)` and `logger.debug(String format, Object... arguments)`. At 10 million log calls per second (a high-frequency trading service), all with exactly two arguments, trace the allocation and GC impact of using the varargs overload versus the two-argument overload. Calculate the approximate bytes of garbage produced per second in each case, and explain why SLF4J maintains both signatures despite the code duplication.

**Q2.** A method `@SafeVarargs static <T> Optional<T> first(T... items)` is annotated as safe. A second developer later modifies it to store `items` in a field for later retrieval: `this.lastItems = items`. Trace exactly why the `@SafeVarargs` annotation is now incorrect, what specific sequence of operations would trigger a `ClassCastException`, and why the compiler cannot detect this violation at compile time even with `-Xlint:unchecked`.

