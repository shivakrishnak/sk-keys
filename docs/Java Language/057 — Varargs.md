---
layout: default
title: "Varargs"
parent: "Java Language"
nav_order: 57
permalink: /java-language/varargs/
number: "057"
category: Java Language
difficulty: ★☆☆
depends_on: Arrays, Method Signatures, Autoboxing
used_by: String.format, MessageFormat, Logging APIs
tags: #java #foundational #varargs #methods
---

# 057 — Varargs

`#java` `#foundational` `#varargs` `#methods`

⚡ TL;DR — Variable-argument methods (`type... name`) accept zero or more values of a type without the caller creating an array; the compiler creates the array automatically.

| #057 | Category: Java Language | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Arrays, Method Signatures, Autoboxing | |
| **Used by:** | String.format, MessageFormat, Logging APIs | |

---

### 📘 Textbook Definition

Varargs (variable-length argument lists) is a Java feature (since Java 5) that allows a method to accept zero or more arguments of a specified type via the `type... paramName` syntax. The compiler converts varargs calls into array creation at the call site; the method receives a standard array. A varargs parameter must be the **last** parameter in the method signature.

---

### 🟢 Simple Definition (Easy)

Varargs lets you call `log("Hello")`, `log("Hello", "World")`, or `log("a", "b", "c", "d")` with the same method signature `void log(String... messages)` — no method overloading needed.

---

### 🔵 Simple Definition (Elaborated)

Before varargs, you'd write `void log(String[] messages)` and callers would write `log(new String[]{"a","b"})`. With varargs, callers write `log("a","b")` and the compiler wraps it into an array automatically. The method sees a normal `String[]`. You can also pass an actual array directly.

---

### 🔩 First Principles Explanation

**What the compiler does:**
```
Call site:
  sum(1, 2, 3, 4)
  ↓ compiled to:
  sum(new int[]{1, 2, 3, 4})

Method declaration:
  int sum(int... numbers) { ... }
  ↓ compiled as:
  int sum(int[] numbers) { ... }

Zero args:
  sum()  →  sum(new int[0])  (empty array, NOT null)
```

---

### ❓ Why Does This Exist (Why Before What)

Before varargs, APIs like `printf`, `EnumSet.of`, `List.of` would need dozens of overloads for different argument counts. Varargs enables clean APIs like `String.format(String fmt, Object... args)` and `List.of(T... elements)` with a single method declaration.

---

### 🧠 Mental Model / Analogy

> Varargs is like a supermarket self-checkout with a "put any items here" conveyor belt. Whether you bring 1 item or 20, you just place them on the belt and the system counts them. Behind the scenes, everything ends up in a standard basket (array) — you just don't have to create the basket yourself.

---

### ⚙️ How It Works (Mechanism)

```
Rules:
  1. Must be the LAST parameter
     void method(String prefix, int... nums)  // ✓
     void method(int... nums, String prefix)  // COMPILE ERROR

  2. At most ONE varargs per method

  3. Call site creates a new array each time → heap allocation

  4. Can pass an existing array directly
     int[] arr = {1, 2, 3};
     sum(arr);   // passes array directly, no new array created

  5. Zero args → empty array, not null
     sum()  →  new int[0]

Overload resolution with varargs:
  Fixed-arity overloads are preferred over varargs
  void log(String msg) { ... }         // preferred
  void log(String... msgs) { ... }     // fallback
  log("hello")  →  picks fixed-arity version
```

---

### 🔄 How It Connects (Mini-Map)

```
[varargs method declaration]
       │ compiler converts to
       ▼
[array parameter + array creation at call site]
       │
       ├─► generic varargs → @SafeVarargs / heap pollution risk (#054)
       ├─► ambiguous overloads with varargs → compilation warnings
       └─► performance: new array per call → avoid in tight loops
```

---

### 💻 Code Example

```java
// 1. Basic varargs
static int sum(int... nums) {
    int total = 0;
    for (int n : nums) total += n;
    return total;
}
sum();           // 0   (empty array)
sum(1);          // 1
sum(1, 2, 3);    // 6
sum(new int[]{4, 5}); // 9 — pass array directly

// 2. Mixed params — varargs must be last
static String join(String separator, String... parts) {
    return String.join(separator, parts);
}
join(", ", "a", "b", "c");     // "a, b, c"
join("-");                      // "" (empty parts array)

// 3. Generic varargs — heap pollution warning
@SafeVarargs   // suppress when you're certain the varargs array isn't written to
static <T> List<T> listOf(T... items) {
    return Arrays.asList(items);  // safe: we only READ the array
}
List<String> names = listOf("Alice", "Bob");

// 4. Real JDK examples
String.format("Hello %s, you are %d", "Alice", 30);  // varargs Object...
List.of(1, 2, 3, 4, 5);                              // varargs T...
EnumSet.of(DayOfWeek.MONDAY, DayOfWeek.TUESDAY);     // varargs E...
System.out.printf("x=%d, y=%d%n", x, y);            // varargs Object...

// 5. Null pitfall
sum(null);   // passes null as the array → NullPointerException inside method
             // if the method tries to iterate over null
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Varargs creates a List | Creates an array (`T[]`), not a List |
| Zero varargs means null | Zero args = empty array `new T[0]` |
| Varargs has no performance cost | New array allocated per call — avoid in hot loops |
| `@SafeVarargs` makes it type-safe | It only suppresses the warning; you must ensure safety manually |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Heap pollution with generic varargs**
```java
static <T> void store(T... items) {
    Object[] storeArr = items;   // always allowed (array covariance)
    storeArr[0] = "oops";        // if T=Integer, this pollutes the heap
}
// Use @SafeVarargs only if you NEVER write to the varargs array
```

**Pitfall 2: Ambiguous overload resolution**
```java
void log(Object... args)   { System.out.println("varargs"); }
void log(Object   arg)     { System.out.println("single");  }
log("hello");  // prints "single" — fixed arity preferred
log((Object) null);        // ambiguous — compiler warns

// With String vs Object overloads, be explicit about which you want
```

**Pitfall 3: Performance in loops**
```java
for (int i = 0; i < 1_000_000; i++) {
    log("event", i);   // allocates new Object[]{i} every iteration!
}
// Fix: use a logger that takes fixed params, or log at TRACE level with guard
```

---

### 🔗 Related Keywords

- **Arrays** — varargs is syntactic sugar over arrays
- **Generics / Type Erasure (#053, #054)** — generic varargs cause heap pollution warnings
- **@SafeVarargs** — annotation to suppress heap pollution warning when safe
- **String.format / printf** — canonical varargs `Object...` usage in JDK
- **List.of** — uses `@SafeVarargs` varargs internally (Java 9+)

---

### 📌 Quick Reference Card

| #057 | Category: Java Language | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Arrays, Method Signatures, Autoboxing | |
| **Used by:** | String.format, MessageFormat, Logging APIs | |

---

### 🧠 Think About This Before We Continue

**Q1.** Why must a varargs parameter always be the last parameter in a method signature?
**Q2.** What is the difference between calling `sum(null)` and `sum()` for a method `int sum(int... nums)`?
**Q3.** When is it correct to annotate a generic varargs method with `@SafeVarargs`?

