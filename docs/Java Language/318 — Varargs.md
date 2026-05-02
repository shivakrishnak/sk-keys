---
layout: default
title: "Varargs"
parent: "Java Language"
nav_order: 318
permalink: /java-language/varargs/
number: "318"
category: Java Language
difficulty: ★★☆
depends_on: "Generics, Arrays, Method Overloading"
used_by: "String.format, Arrays.asList, printf, logging, Spring @Value"
tags: #java, #varargs, #arrays, #method-overloading, #heap-pollution
---

# 318 — Varargs

`#java` `#varargs` `#arrays` `#method-overloading` `#heap-pollution`

⚡ TL;DR — **Varargs** (`Type... args`) allow a method to accept zero or more arguments of a type; desugared to an array. Use `@SafeVarargs` with generics to suppress heap pollution warnings.

| #318 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Generics, Arrays, Method Overloading | |
| **Used by:** | String.format, Arrays.asList, printf, logging, Spring @Value | |

---

### 📘 Textbook Definition

**Varargs** (Variable-length argument lists, Java 5): a method parameter syntax (`Type... paramName`) that allows a method to accept zero or more arguments of the specified type. The compiler desugars the call site: it collects the arguments into an array and passes that array to the method. The varargs parameter must be the last parameter in the method signature. At the method body, `paramName` is an array (`Type[]`). Callers can pass individual values, an explicit array, or nothing. `@SafeVarargs`: annotation that suppresses unchecked warnings from generic varargs — the programmer asserts that the method body does not perform heap-polluting operations on the varargs array.

---

### 🟢 Simple Definition (Easy)

`void log(String message, Object... args)` — the `...` means "zero or more arguments of type Object." Call it as `log("Hello")`, `log("Hello {}", name)`, `log("Name {}, age {}", name, age)`. Behind the scenes: the compiler wraps the extra arguments in an `Object[]` and passes it to the method. The method body treats `args` as a regular array.

---

### 🔵 Simple Definition (Elaborated)

Before varargs: `String.format(String pattern, Object[] args)` — callers had to create an array manually: `String.format("%s=%s", new Object[]{key, value})`. With varargs: `String.format("%s=%s", key, value)` — cleaner. The feature is purely syntactic: the compiler creates the array at the call site. You can still pass an explicit array: `String.format("%s", myArray)` — the array IS the varargs array (no wrapping). One common pitfall: passing a single `Object[]` argument — the compiler treats it as the varargs array directly, which may not be your intent.

---

### 🔩 First Principles Explanation

**Varargs desugaring, overloading interaction, and @SafeVarargs:**

```
VARARGS DESUGARING:

  Source: method declaration:
  public void print(String label, int... values) {
      System.out.print(label + ": ");
      for (int v : values) System.out.print(v + " ");
  }
  
  Bytecode equivalent:
  public void print(String label, int[] values) { ... }
  
  Source: call sites:
  print("nums", 1, 2, 3)   → print("nums", new int[]{1, 2, 3})
  print("empty")            → print("empty", new int[0])  ← zero-length array
  print("arr", myArr)       → print("arr", myArr)          ← array passed directly
  
VARARGS WITH ARRAYS — AMBIGUITY:

  void method(Object... args) { ... }
  
  method("a", "b");         // args = new Object[]{"a", "b"}
  method(new Object[]{"a", "b"});  // args = {"a", "b"} (array IS the varargs)
  
  // GOTCHA:
  Object[] arr = {1, 2, 3};
  method(arr);              // args = {1, 2, 3} (array is unwrapped)
  method((Object) arr);     // args = {arr}     (array treated as single Object)
  // The cast to Object wraps the array as one element

OVERLOADING WITH VARARGS:

  void foo(int a, int b) { System.out.println("two ints"); }
  void foo(int... nums)  { System.out.println("varargs"); }
  
  foo(1, 2);    // "two ints" — exact match takes priority over varargs
  foo(1, 2, 3); // "varargs" — only varargs matches
  foo(1);       // "varargs" — only varargs matches
  
  // AMBIGUITY — avoid:
  void bar(int a, int... b) {}
  void bar(int... a) {}
  bar(1);  // COMPILE ERROR: ambiguous — both match

GENERIC VARARGS + HEAP POLLUTION:

  // WARNING: [unchecked] Possible heap pollution from parameterized vararg type
  @SafeVarargs  // suppress if method doesn't expose varargs array outside
  public static <T> List<T> listOf(T... elements) {
      return Arrays.asList(elements);  // SAFE: elements not stored/cast
  }
  
  // UNSAFE — NEVER do this:
  static <T> T[] toArray(T... args) {
      return args;  // UNSAFE: caller gets Object[] due to erasure, ClassCastException possible
  }
  String[] result = toArray("a", "b");  // ClassCastException: Object[] cannot be String[]
  
  // WHY: new T[]{...} with erasure → actually new Object[]{...}
  // Caller expects String[], gets Object[] → ClassCastException at assignment
  
  // RULE FOR @SafeVarargs: safe if:
  // 1. Method doesn't store anything into the varargs array
  // 2. Method doesn't expose the varargs array to untrusted code
  // Examples: Arrays.asList(T... a) — safe; toArray(T... a) — unsafe

COMMON VARARGS IN JDK:

  String.format(String format, Object... args)
  Arrays.asList(T... a)
  Collections.unmodifiableList(Collection<? extends T> c)  // not varargs
  List.of(E... elements)   // Java 9+: @SafeVarargs
  EnumSet.of(E first, E... rest)
  System.out.printf(String format, Object... args)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Varargs:
- `void log(String msg, Object[] args)` — caller must create array: `log("msg", new Object[]{a, b})`
- `printf`-style methods: verbose, error-prone array construction at every call site

WITH Varargs:
→ `void log(String msg, Object... args)` — caller writes `log("msg", a, b)`. Compiler handles array creation. Cleaner API, especially for utility methods with variable argument counts.

---

### 🧠 Mental Model / Analogy

> A restaurant that says "bring your whole table group" (varargs) vs. "fill out a form listing each person" (array parameter). Varargs: just walk in with 1, 5, or 10 people — the host groups you automatically (compiler creates the array). Array parameter: you must pre-list everyone on a reservation form (manual `new Object[]{...}`). The host's internal list (the array parameter in the method) is the same either way — only the arrival process differs.

"Walk in with any number of people" = calling varargs method with any count of args
"Host groups you automatically" = compiler creates `new T[]{arg1, arg2, ...}` at call site
"Fill out reservation form" = pre-Java 5 manual array creation
"Internal guest list" = the method's `args[]` parameter — identical in both cases

---

### ⚙️ How It Works (Mechanism)

```
BYTECODE VIEW (javap):

  Source:
  void print(int... values) { System.out.println(values.length); }
  print(1, 2, 3);
  
  Bytecode for call:
  iconst_3
  newarray int        ← creates new int[3]
  dup
  iconst_0
  iconst_1            ← values[0] = 1
  iastore
  dup
  iconst_1
  iconst_2            ← values[1] = 2
  iastore
  dup
  iconst_2
  iconst_3            ← values[2] = 3
  iastore
  invokevirtual print([I)  ← passes int[]
  
  // Zero-arg call: print() → compiler creates new int[0] (not null!)
```

---

### 🔄 How It Connects (Mini-Map)

```
Need methods with flexible argument counts
        │
        ▼
Varargs ◄──── (you are here)
(Type... args; desugared to Type[]; last param only; @SafeVarargs for generics)
        │
        ├── Generics: generic varargs T... triggers heap pollution warning
        ├── @SafeVarargs: annotation to assert safe use of generic varargs
        ├── Arrays: varargs is syntactic sugar over array creation
        └── Method Overloading: exact match preferred over varargs match
```

---

### 💻 Code Example

```java
// BASIC VARARGS:
static int sum(int... numbers) {
    int total = 0;
    for (int n : numbers) total += n;
    return total;
}
System.out.println(sum());           // 0
System.out.println(sum(1, 2, 3));    // 6
System.out.println(sum(1, 2, 3, 4, 5)); // 15

// PASSING AN ARRAY DIRECTLY:
int[] arr = {10, 20, 30};
System.out.println(sum(arr));       // 60 (array passed directly as varargs)

// MIXED PARAMS:
static String format(String template, Object... args) {
    return String.format(template, args);  // forward varargs to String.format
}

// SAFE GENERIC VARARGS:
@SafeVarargs
static <T> List<T> listOf(T... items) {
    return new ArrayList<>(Arrays.asList(items));  // safe: not exposing array
}
List<String> names = listOf("Alice", "Bob", "Carol");

// LOGGING PATTERN (avoid toString until needed):
void debug(String msg, Object... args) {
    if (logger.isDebugEnabled()) {
        logger.debug(msg, args);  // SLF4J: lazy format avoids toString() if DEBUG disabled
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `void foo(Object... args)` called with `null` produces an empty array | `foo(null)` sets `args = null` (not an empty array). The null is treated as the array itself, not as a missing argument. `foo((Object) null)` wraps null as a single element: `args = new Object[]{null}`. Always null-check varargs: `if (args == null) args = new Object[0]`. |
| `@SafeVarargs` makes generic varargs actually safe | `@SafeVarargs` only suppresses the warning — it doesn't make unsafe code safe. It's a programmer assertion that the code is safe. If you use `@SafeVarargs` on a method that exposes the varargs array or stores alien types into it, heap pollution still occurs. |
| `String.format(pattern, arr)` works as expected for Object[] | If `arr` is an `Object[]`, it's treated as the entire varargs array (the elements are the format args). If `arr` is a `String[]`, same thing. But if you intended the array itself to be one format arg, cast: `String.format("%s", (Object) arr)`. This is a common bug with format methods and arrays. |

---

### 🔥 Pitfalls in Production

**NullPointerException or ambiguity from null varargs:**

```java
// ANTI-PATTERN — not handling null varargs:
public void sendEmails(String subject, String... recipients) {
    for (String r : recipients) {  // NullPointerException if recipients is null!
        emailService.send(r, subject);
    }
}

// Called as:
sendEmails("Hello", null);  // recipients = null, NOT new String[]{null}!
// NullPointerException on for-each loop

// FIX — null guard in varargs methods:
public void sendEmails(String subject, String... recipients) {
    if (recipients == null || recipients.length == 0) return;
    for (String r : recipients) {
        if (r != null) emailService.send(r, subject);
    }
}

// FIX 2 — use List<String> instead of varargs for nullable collections:
public void sendEmails(String subject, List<String> recipients) {
    if (recipients == null) return;
    recipients.stream().filter(Objects::nonNull).forEach(r -> emailService.send(r, subject));
}
```

---

### 🔗 Related Keywords

- `Generics` — generic varargs `T...` creates heap pollution (erased to `Object[]`)
- `@SafeVarargs` — annotation to suppress heap pollution warning on safe generic varargs
- `Arrays.asList` — uses `@SafeVarargs` and varargs: `Arrays.asList("a", "b", "c")`
- `Method Overloading` — varargs overloads have lowest priority; exact matches preferred
- `SLF4J / Logback` — logger methods use varargs for lazy parameter formatting

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Type... args = zero or more args.        │
│              │ Compiler creates Type[] at call site.   │
│              │ Must be last parameter.                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Utility methods (sum, format, listOf);  │
│              │ flexible arity; DSL-style builders       │
├──────────────┼───────────────────────────────────────────┤
│ NULL TRAP    │ foo(null) → args = null, not empty[].   │
│              │ Always null-check varargs parameter.    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Walk in with any group size — host     │
│              │  writes the list automatically."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @SafeVarargs → Generics → Type Erasure → │
│              │ Method Overloading → Arrays.asList       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `Arrays.asList(T... a)` is annotated `@SafeVarargs`. It returns a `List<T>` backed by the array. If you call `Arrays.asList(1, 2, 3)` and then try to call `.add(4)` on the result, you get `UnsupportedOperationException`. Why? And how does this relate to the fact that the returned list is backed by the exact same array that was the varargs parameter?

**Q2.** `List.of(E... elements)` in Java 9 is also `@SafeVarargs` and returns an unmodifiable list. But `List.of()` (no args), `List.of(e1)`, and `List.of(e1, e2)` are separate overloads — not varargs. Why does the JDK provide these separate fixed-arity overloads in addition to the varargs version? What performance optimization does this enable?
