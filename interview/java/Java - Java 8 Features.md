---
layout: default
title: "Java - Java 8 Features"
parent: "Java"
grand_parent: "Interview Mastery"
nav_order: 4
permalink: /interview/java/java-8-features/
topic: Java
subtopic: Java 8 Features
keywords:
  - Lambda Expressions
  - Streams API
  - Optional
  - Functional Interfaces
  - Method References
  - Default Methods
difficulty_range: mixed
status: in-progress
version: 3
---

**Keywords covered in this file:**

- [Lambda Expressions](#lambda-expressions)
- [Streams API](#streams-api)
- [Optional](#optional)
- [Functional Interfaces](#functional-interfaces)
- [Method References](#method-references)
- [Default Methods](#default-methods)

# Lambda Expressions

**TL;DR** - Lambdas let you pass behaviour as data - a function becomes a value you can store, pass, and compose, eliminating thousands of lines of anonymous inner class boilerplate.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Java 8, every callback required a full anonymous inner class. Sorting a list by name meant writing 5 lines of `new Comparator<String>() { @Override public int compare(...)  { ... } }` for what is logically a one-liner. Event handlers, thread tasks, and collection operations all drowned in ceremony. Developers wrote more boilerplate than logic.

**THE BREAKING POINT:**
Functional programming languages showed that passing behavior as arguments makes code dramatically shorter and more composable. Java developers were leaving for Scala, Groovy, and Kotlin because basic operations like filter-map-reduce required absurd verbosity in Java.

**THE INVENTION MOMENT:**
"This is exactly why lambda expressions were created."

**EVOLUTION:**
Anonymous inner classes (Java 1.1) -> lambda expressions and functional interfaces (Java 8) -> `var` in lambda parameters (Java 11) -> pattern matching in future versions. The JVM added `invokedynamic` (Java 7) specifically to enable efficient lambda implementation.
---

### 📘 Textbook Definition

A lambda expression is an anonymous function that can be assigned to a variable, passed as an argument, or returned from a method. In Java, lambdas implement functional interfaces (interfaces with exactly one abstract method) and are compiled to `invokedynamic` bytecode instructions rather than inner class files.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
A lambda is a block of code you can pass around like a variable.

**One analogy:**

> Think of a lambda like a sticky note with instructions. Instead of hiring a full-time employee (anonymous inner class) to do one task, you hand someone a sticky note saying "sort by last name." The note is the behavior, detached from any class.

**One insight:**
Lambdas did not add new capability to Java - anything a lambda does, an anonymous class could do. What they added was readability and composability. Code that was 8 lines became 1, and that 1 line could be chained with other lambdas to build pipelines.
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A lambda must target a functional interface (exactly one abstract method)
2. The lambda's parameter types and return type must match the interface's abstract method signature
3. Lambdas capture effectively final variables from enclosing scope (closure semantics)
4. Lambdas are not syntactic sugar for anonymous classes - they use `invokedynamic` for better performance

**DERIVED DESIGN:**
Because lambdas target functional interfaces, Java 8 introduced `@FunctionalInterface` annotation for compile-time validation. The `java.util.function` package provides 43 standard functional interfaces (`Function`, `Predicate`, `Consumer`, `Supplier`, etc.) so you rarely need custom ones.

**THE TRADE-OFFS:**
**Gain:** Dramatic reduction in boilerplate, composability, enables Streams API, better readability
**Cost:** Debugging stack traces are harder (lambda frames show as `lambda$main$0`), cannot use non-effectively-final local variables, learning curve for developers from OOP-only backgrounds

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Passing behavior as data is fundamental to functional programming - some mechanism is needed.
**Accidental:** The restriction to functional interfaces exists because Java chose to retrofit lambdas onto its existing type system rather than adding true function types. Languages like Kotlin have `(A) -> B` as a first-class type.
---

### 🧠 Mental Model / Analogy

> A lambda is like a recipe card. An anonymous inner class is like a full cookbook with one recipe. Both achieve the same meal, but one fits in your pocket. You can hand the recipe card to any chef (method) who knows how to read recipe cards (functional interface).

- "Recipe card" -> lambda expression
- "Cookbook" -> anonymous inner class
- "Chef" -> method accepting a functional interface
- "Recipe format" -> functional interface (contract the lambda must fulfill)

Where this analogy breaks down: Unlike recipe cards, lambdas can capture values from their surrounding environment (closures), which recipes don't do.
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A lambda is a short way to write a small piece of code that you want to pass to another method. Instead of creating a whole class just to define one action, you write the action directly.

**Level 2 - How to use it (junior developer):**

```java
// Before Java 8 - anonymous inner class
Collections.sort(names, new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.compareTo(b);
    }
});

// Java 8 lambda
Collections.sort(names, (a, b) -> a.compareTo(b));

// Even shorter with method reference
names.sort(String::compareTo);
```

Lambda syntax: `(parameters) -> expression` or `(parameters) -> { statements; }`. Type inference handles parameter types in most cases.

**Level 3 - How it works (mid-level engineer):**
Lambdas are compiled using `invokedynamic` bytecode. The first time a lambda callsite is reached, the JVM calls a bootstrap method (`LambdaMetafactory.metafactory`) which generates a class at runtime implementing the target functional interface. Subsequent invocations reuse the generated class. This is faster than anonymous inner classes because: (1) no `.class` file is generated at compile time, (2) the JVM can optimize the generated class, (3) non-capturing lambdas can be implemented as singletons.

Lambdas capture variables from their enclosing scope, but only if they are effectively final. This restriction exists because the captured value is copied into the lambda's closure - if the original variable changed after capture, the lambda would have a stale copy, leading to confusing bugs.

**Level 4 - Why it was designed this way (senior/staff+):**
The design team (led by Brian Goetz) chose to retrofit lambdas onto existing functional interfaces rather than adding function types for backward compatibility. This means `Runnable`, `Callable`, `Comparator` all became lambda targets without any code changes. The `invokedynamic` approach was chosen over inner class generation because it gives the JVM freedom to optimize: today it generates a class via `Unsafe.defineAnonymousClass`, but future JVMs could inline the lambda body directly.

The effectively-final restriction is a deliberate design choice, not a JVM limitation. Mutable closures (as in JavaScript) lead to subtle concurrency bugs. By requiring effective finality, Java pushes developers toward functional purity and makes lambdas safe for parallel streams.


**Level 5 - Distinguished (expert thinking):**
Lambda expressions are Java's implementation of closures - the same concept as JavaScript arrow functions, Python lambdas, C# delegates, and Rust closures. The expert insight is that lambdas are not syntactic sugar for anonymous inner classes: they compile to `invokedynamic` bytecode, which defers the implementation strategy to the JVM. The JVM can then choose to generate a class at runtime, reuse a singleton for non-capturing lambdas, or even inline the function body entirely. This is why lambdas are generally faster than anonymous classes - no `.class` file, no constructor, potentially no allocation. At extreme scale, lambda capture semantics matter: capturing a large object keeps the entire object alive (GC retention), while capturing a mutable variable requires boxing (performance penalty). If redesigning today, you would add syntax for multi-line lambdas with early return (currently `return` exits the lambda, not the enclosing method) and support for checked exceptions in functional interfaces.

**Expert thinking cues:**
- "Is this lambda capturing state?" - non-capturing lambdas are singletons (zero allocation)
- "Could this be a method reference?" - prefer `String::toLowerCase` over `s -> s.toLowerCase()`
- "Is the functional interface correct?" - wrong interface choice causes confusing compiler errors
---

### How It Works (Mechanism)

1. **Compile time:** `javac` desugars the lambda body into a synthetic private method in the enclosing class. The lambda callsite becomes an `invokedynamic` instruction pointing to `LambdaMetafactory`.

2. **First invocation:** The JVM invokes the bootstrap method. `LambdaMetafactory.metafactory()` dynamically generates a class implementing the target functional interface. For non-capturing lambdas, it creates a singleton instance. For capturing lambdas, it creates a class with fields for captured values.

3. **Subsequent invocations:** The `CallSite` returned by the bootstrap method is cached. Non-capturing lambdas return the same singleton. Capturing lambdas instantiate the generated class with current captured values.

4. **JIT optimization:** The JIT compiler can inline lambda bodies, eliminate the generated class entirely, and optimize the whole pipeline as if the code was written inline.

```
Source:  list.forEach(x -> System.out.println(x))
           |
Compile: invokedynamic #accept()
           |
Bootstrap: LambdaMetafactory generates
           Consumer implementation
           |
Runtime: Generated class delegates to
         synthetic method lambda$main$0
```
---

### The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
  Source code        javac            Class file
  (a,b) -> a+b  --> desugar to   --> invokedynamic
                    lambda$0(a,b)     bootstrap ref
                         |
    <- YOU ARE HERE       |
                         v
                  JVM first call
                         |
                  LambdaMetafactory
                  generates impl class
                         |
                  CallSite cached
                         |
                  Subsequent calls
                  reuse CallSite
                         |
                  JIT inlines everything
```

**FAILURE PATH:**
- Targeting a non-functional interface (>1 abstract method): compile error
- Capturing a mutable local variable: compile error ("must be effectively final")
- Serializing a lambda without `(Serializable & TargetInterface)` cast: `NotSerializableException`
- Lambda in a hot loop creating closures: GC pressure from captured variable boxing

**WHAT CHANGES AT SCALE:**
In high-throughput systems, non-capturing lambdas are preferred because they are singletons (zero allocation). Capturing lambdas create a new object per invocation. In tight loops processing millions of events, this difference matters for GC pressure. Profile with `-XX:+PrintCompilation` to verify lambda inlining.

---

### 💻 Code Example

**BAD - Anonymous inner class for simple behavior:**

```java
// 7 lines for a one-line operation
button.addActionListener(
    new ActionListener() {
        @Override
        public void actionPerformed(ActionEvent e) {
            System.out.println("Clicked!");
        }
    }
);
```

**GOOD - Lambda expression:**

```java
// 1 line, same behavior
button.addActionListener(
    e -> System.out.println("Clicked!")
);
```

**GOOD - Composing lambdas for complex behavior:**

```java
Predicate<Employee> senior =
    e -> e.getYearsOfExp() > 5;
Predicate<Employee> highPerf =
    e -> e.getRating() >= 4.5;
Function<Employee, String> toName =
    Employee::getName;

List<String> result = employees.stream()
    .filter(senior.and(highPerf))
    .map(toName)
    .sorted()
    .collect(Collectors.toList());
```

**How to test / verify correctness:**

```java
@Test
void lambdaCapturesEffectivelyFinal() {
    int multiplier = 3; // effectively final
    Function<Integer, Integer> fn =
        x -> x * multiplier;
    assertEquals(15, fn.apply(5));
    // multiplier = 4; // uncommenting = error
}
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** Anonymous function that implements a functional interface via concise syntax
**PROBLEM IT SOLVES:** Eliminates verbose anonymous inner class boilerplate for single-method callbacks
**KEY INSIGHT:** Compiled to `invokedynamic`, not inner classes - faster, no `.class` files, zero allocation for non-capturing lambdas
**USE WHEN:** Callbacks, event handlers, comparators, stream operations, strategy pattern
**AVOID WHEN:** Logic exceeds 3 lines - extract to a named method and use method reference
**ANTI-PATTERN:** Capturing mutable state in parallel stream lambdas - causes race conditions
**TRADE-OFF:** Conciseness and composability vs reduced debuggability (anonymous stack frames)
**ONE-LINER:** "Behavior as a value - pass functions like data, compose like pipelines"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**
1. Lambdas target functional interfaces (one abstract method)
2. Captured variables must be effectively final
3. Lambdas use `invokedynamic`, not inner classes - they are faster

**Interview one-liner:**
"A lambda is an anonymous function targeting a functional interface, compiled via invokedynamic for performance, that captures only effectively final variables to ensure thread safety."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Non-capturing lambdas (those that don't reference any variables from the enclosing scope) are implemented as singletons by the JVM - the same object instance is reused across every invocation. This means `list.forEach(System.out::println)` in a loop allocates zero objects after the first call, making lambdas cheaper than the anonymous inner classes they replaced.
---

### ⚖️ Comparison Table

| Aspect | Lambda | Anonymous Class | Method Reference |
|--------|--------|----------------|-----------------|
| Syntax | `x -> x + 1` | `new Fn() { ... }` | `Math::abs` |
| Compiled to | `invokedynamic` | Inner class file | `invokedynamic` |
| `this` refers to | Enclosing class | Anonymous class | Enclosing class |
| Can have state | No (captures only) | Yes (fields) | No |
| Performance | Best (no class) | Worst (class load) | Best |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Lambdas are syntactic sugar for anonymous inner classes | Lambdas use `invokedynamic` bytecode, not inner classes. No `.class` file is generated. `this` refers to the enclosing class, not the lambda. Performance is better. |
| 2 | Lambdas can modify local variables | Captured local variables must be effectively final. Lambdas capture values, not variable bindings. Use `AtomicInteger` or a one-element array for mutation. |
| 3 | All lambdas cause object allocation | Non-capturing lambdas (no external variables) are typically cached as singletons by the JVM - zero allocation after first call. |
| 4 | Longer lambdas are fine if they work | Lambdas over 3 lines harm readability. Extract to a named method and use a method reference. The lambda body should express intent, not implementation. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Effectively final violation**
**Symptom:** Compile error: "local variables referenced from a lambda expression must be final or effectively final."
**Root Cause:** Attempting to modify a local variable inside a lambda.
**Diagnostic:**

```
# Compiler error points to the variable
javac MyClass.java 2>&1 | grep "effectively final"
```

**Fix:**
```java
// BAD: modifying local variable
int count = 0;
list.forEach(x -> count++); // won't compile

// GOOD: use AtomicInteger
AtomicInteger count = new AtomicInteger(0);
list.forEach(x -> count.incrementAndGet());
// Or better: list.stream().count()
```
**Prevention:** Use stream reductions (`count()`, `reduce()`, `collect()`) instead of mutation.

**Failure Mode 2: Confusing `this` reference**
**Symptom:** `this.field` inside lambda refers to the enclosing class, not the "lambda object" (which doesn't exist).
**Root Cause:** Unlike anonymous classes, lambdas don't have their own `this`. Developers from JavaScript/Python expect lambda-scoped `this`.
**Diagnostic:**

```
# Add debug logging
System.out.println(this.getClass().getName());
# Inside lambda: prints enclosing class name
```

**Fix:**
```java
// In anonymous class: this = anonymous class
// In lambda: this = enclosing class
// If you NEED anonymous class this:
Runnable r = new Runnable() {
    public void run() { /* this = Runnable */ }
};
```
**Prevention:** Remember: lambda `this` = enclosing class. If you need a separate `this`, use an anonymous class.

**Failure Mode 3: Checked exception in lambda**
**Symptom:** Compile error when lambda throws a checked exception that the functional interface doesn't declare.
**Root Cause:** Built-in functional interfaces (`Function`, `Consumer`) don't declare checked exceptions.
**Diagnostic:**

```
# Compiler shows: "unhandled exception type IOException"
javac MyClass.java 2>&1 | grep "unhandled exception"
```

**Fix:**
```java
// BAD: checked exception in stream
list.stream().map(path -> {
    return Files.readString(path); // IOException!
});

// GOOD: wrap in unchecked exception
list.stream().map(path -> {
    try { return Files.readString(path); }
    catch (IOException e) {
        throw new UncheckedIOException(e);
    }
});
```
**Prevention:** Create utility `ThrowingFunction` wrappers or use libraries like Vavr for checked-exception-safe functional types.
---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between a lambda expression and an anonymous inner class?**

*Why they ask:* Tests whether you understand lambdas beyond syntax sugar.

*Strong answer:*

They differ in five key ways:

1. **Compilation:** Anonymous inner classes generate a separate `.class` file at compile time (e.g., `MyClass$1.class`). Lambdas use `invokedynamic` and the class is generated at runtime by `LambdaMetafactory`.

2. **Performance:** Non-capturing lambdas are singletons - zero allocation after first call. Anonymous classes create a new object every time.

3. **`this` keyword:** Inside an anonymous class, `this` refers to the anonymous class instance. Inside a lambda, `this` refers to the enclosing class instance.

4. **Scope:** Anonymous classes can shadow variables from the enclosing scope. Lambdas cannot - a lambda parameter cannot have the same name as a local variable in the enclosing scope.

5. **State:** Anonymous classes can have fields, constructors, and multiple methods. Lambdas have no state and implement exactly one method.

```java
class Demo {
    Runnable anonymousClass = new Runnable() {
        @Override
        public void run() {
            // 'this' = the Runnable instance
            System.out.println(this.getClass());
        }
    };

    Runnable lambda = () -> {
        // 'this' = the Demo instance
        System.out.println(this.getClass());
    };
}
```

---

**Q2: Why must variables captured by lambdas be effectively final? What happens if you try to mutate them?**

*Why they ask:* Tests understanding of closure semantics and concurrency safety.

*Strong answer:*

When a lambda captures a local variable, it copies the variable's value into the lambda's closure. If you could mutate the original variable after capture, the lambda would hold a stale copy, creating a confusing disconnect between what the developer sees and what the lambda uses.

More critically, lambdas are designed to work safely with parallel streams. If captured variables were mutable, two threads could race on the same variable. By enforcing effective finality, Java makes lambdas safe for concurrent execution by construction.

```java
int count = 0;
// COMPILE ERROR: count must be effectively final
list.forEach(item -> count++);

// Workaround 1: Use AtomicInteger
AtomicInteger count2 = new AtomicInteger(0);
list.forEach(item -> count2.incrementAndGet());

// Workaround 2: Use stream reduction
long count3 = list.stream()
    .filter(item -> item.isActive())
    .count();
// Workaround 2 is preferred - no mutation needed
```

The rule is "effectively final" - the variable doesn't need the `final` keyword, it just must never be reassigned after initialization. This was a pragmatic design choice: requiring explicit `final` would have made existing code incompatible with lambdas.

---

**Q3: Explain how `invokedynamic` enables lambda expressions. Why not just compile to inner classes?**

*Why they ask:* Tests deep understanding of JVM internals and performance.

*Strong answer:*

`invokedynamic` (added in Java 7, used for lambdas in Java 8) decouples the lambda's callsite from its implementation strategy. Here's how it works:

1. **At compile time:** `javac` emits an `invokedynamic` instruction at each lambda callsite. The lambda body is desugared into a private static method (e.g., `lambda$main$0`) in the same class. No inner class file is generated.

2. **At first invocation:** The JVM calls the bootstrap method `LambdaMetafactory.metafactory()`. This generates a lightweight class at runtime that implements the target functional interface and delegates to the desugared method.

3. **The `CallSite` is cached:** Subsequent invocations skip the bootstrap entirely and reuse the generated class.

Why not inner classes? Three reasons:

- **Disk footprint:** An application with 500 lambdas would generate 500 `.class` files. With `invokedynamic`, zero extra files are generated.
- **Startup time:** Loading 500 inner classes requires 500 classloading operations. `invokedynamic` defers class generation to first use.
- **Future optimization:** The `invokedynamic` approach is an indirection layer. Today's JVM generates classes, but future JVMs could inline the lambda body directly, use `MethodHandle` chains, or apply other optimizations - all without changing the bytecode.

This is why Brian Goetz calls `invokedynamic` a "stable binary interface" - the bytecode format is fixed, but the implementation strategy can evolve independently.

---

**Q4: What are the main functional interfaces in `java.util.function`? When do you use each?**

*Why they ask:* Tests practical working knowledge of the functional API.

*Strong answer:*

The four pillars of `java.util.function`:

| Interface | Signature | Use Case |
|-----------|-----------|----------|
| `Function<T,R>` | `T -> R` | Transform a value |
| `Predicate<T>` | `T -> boolean` | Test a condition |
| `Consumer<T>` | `T -> void` | Perform side effect |
| `Supplier<T>` | `() -> T` | Lazy value production |

Key variants:
- `BiFunction<T,U,R>`, `BiPredicate<T,U>`, `BiConsumer<T,U>` - two-argument versions
- `UnaryOperator<T>` extends `Function<T,T>` - same input/output type
- `BinaryOperator<T>` extends `BiFunction<T,T,T>` - reduction operations
- Primitive specializations: `IntFunction`, `LongSupplier`, `DoublePredicate` - avoid autoboxing

```java
// Function: transform
Function<String, Integer> len = String::length;

// Predicate: filter
Predicate<String> notEmpty = s -> !s.isEmpty();

// Consumer: side effect
Consumer<String> print = System.out::println;

// Supplier: lazy creation
Supplier<List<String>> listFactory =
    ArrayList::new;

// Composition
Function<String, String> pipeline =
    String::trim
        .andThen(String::toLowerCase)
        .andThen(s -> s.replaceAll("\\s+", "-"));
```

The primitive specializations (`IntFunction`, `ToIntFunction`, `IntUnaryOperator`, etc.) exist to avoid autoboxing overhead. In a hot path processing millions of values, `IntStream.map(IntUnaryOperator)` is significantly faster than `Stream<Integer>.map(Function<Integer,Integer>)` because it avoids boxing every integer.

---

**Q5: What is a method reference and how does it relate to lambdas?**

*Why they ask:* Tests understanding of the four types and when each applies.

*Strong answer:*

A method reference is a shorthand for a lambda that simply calls an existing method. There are four types:

1. **Static method reference:** `ClassName::staticMethod`
   - Lambda equivalent: `(args) -> ClassName.staticMethod(args)`
   - Example: `Integer::parseInt` is `s -> Integer.parseInt(s)`

2. **Instance method of a particular object:** `instance::method`
   - Lambda equivalent: `(args) -> instance.method(args)`
   - Example: `System.out::println` is `x -> System.out.println(x)`

3. **Instance method of an arbitrary object of a particular type:** `ClassName::instanceMethod`
   - Lambda equivalent: `(obj, args) -> obj.instanceMethod(args)`
   - Example: `String::toLowerCase` is `s -> s.toLowerCase()`

4. **Constructor reference:** `ClassName::new`
   - Lambda equivalent: `(args) -> new ClassName(args)`
   - Example: `ArrayList::new` is `() -> new ArrayList<>()`

The tricky one is type 3. `String::compareToIgnoreCase` can be used as a `Comparator<String>` because the first parameter becomes the receiver: `(a, b) -> a.compareToIgnoreCase(b)`.

```java
// Type 1: Static
Function<String, Integer> parse =
    Integer::parseInt;

// Type 2: Bound instance
PrintStream out = System.out;
Consumer<String> print = out::println;

// Type 3: Unbound instance
Function<String, String> upper =
    String::toUpperCase;

// Type 4: Constructor
Supplier<List<String>> factory =
    ArrayList::new;

// Type 3 as Comparator (two-arg)
Comparator<String> comp =
    String::compareToIgnoreCase;
```

Method references are preferred over lambdas when the lambda simply delegates to an existing method with no additional logic. They are more readable and communicate intent: `Employee::getName` immediately tells the reader "extract the name," whereas `e -> e.getName()` requires reading the body.

---

**Q6: How do default methods in interfaces work? What problem do they solve and what conflicts can arise?**

*Why they ask:* Tests understanding of interface evolution and the diamond problem.

*Strong answer:*

Default methods allow interfaces to provide a method implementation using the `default` keyword. They were introduced to solve the **interface evolution problem**: adding a new method to an existing interface (like `Collection.stream()`) would break every class implementing that interface.

```java
public interface Collection<E> {
    // existing abstract methods...

    // Added in Java 8 - doesn't break existing
    // implementations
    default Stream<E> stream() {
        return StreamSupport.stream(
            spliterator(), false);
    }
}
```

**Conflict resolution rules (the diamond problem):**

1. **Class wins over interface:** If a class defines the same method, the class method takes precedence over any default method.

2. **Sub-interface wins over super-interface:** If `InterfaceB extends InterfaceA` and both define the same default method, `InterfaceB`'s version wins.

3. **Explicit resolution required:** If a class implements two unrelated interfaces with the same default method, the compiler forces you to override and explicitly choose.

```java
interface A {
    default void hello() {
        System.out.println("A");
    }
}
interface B {
    default void hello() {
        System.out.println("B");
    }
}
// Must resolve conflict explicitly
class C implements A, B {
    @Override
    public void hello() {
        A.super.hello(); // explicit choice
    }
}
```

Default methods do NOT make interfaces equivalent to abstract classes. Interfaces still cannot have constructors, mutable instance fields, or private state (until Java 9 added private methods). Default methods are for behavior that can be expressed purely in terms of the interface's abstract methods.

---

**Q7: Can you explain variable capture in lambdas vs local/anonymous classes with a code example showing the differences?**

*Why they ask:* Tests nuanced understanding of scoping rules.

*Strong answer:*

Three key differences in variable capture:

1. **Effectively final requirement:**
   Both lambdas and anonymous classes require captured local variables to be effectively final. But lambdas enforce this more strictly - you cannot even shadow a local variable name:

```java
int x = 10;

// Anonymous class: can shadow x
new Runnable() {
    int x = 20; // shadows outer x - OK
    public void run() {
        System.out.println(x); // 20
    }
};

// Lambda: CANNOT shadow x
// Runnable r = () -> {
//     int x = 20; // COMPILE ERROR
// };
```

2. **`this` reference:**
   In an anonymous class, `this` refers to the anonymous instance, so it captures an implicit reference to itself. In a lambda, `this` refers to the enclosing class, so it captures a reference to the enclosing instance.

3. **Memory implications:**
   Anonymous inner classes always capture a reference to the enclosing instance (even if they don't use it), which can prevent garbage collection. Non-capturing lambdas are singletons and hold no references at all.

```java
class Outer {
    void method() {
        String name = "test";

        // Anonymous class: captures
        // 'this' (Outer) + 'name'
        Runnable anon = new Runnable() {
            public void run() {
                System.out.println(name);
                // 'this' = this Runnable
                // Outer.this = the Outer
            }
        };

        // Lambda: captures only 'name'
        // (unless 'this' is used)
        Runnable lambda = () -> {
            System.out.println(name);
            // 'this' = the Outer instance
        };
    }
}
```

The practical implication: in Android or UI frameworks where listeners are registered, lambda-based listeners that don't reference `this` are lighter weight than anonymous class listeners, reducing the risk of memory leaks.
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Functional Interfaces - lambdas must target a functional interface type
- Anonymous inner classes - the verbose predecessor that lambdas replace

**Builds on this (learn these next):**

- Streams API - lambdas enable the entire stream pipeline
- Method References - concise alternative when lambda just delegates

**Alternatives / Comparisons:**

- Anonymous inner classes - when you need `this` scoping or multiple methods
- Method references - when lambda body is a single method call


---

---

# Streams API

**TL;DR** - Streams provide a declarative pipeline for transforming collections - filter, map, reduce in a chain - replacing imperative loops with composable, parallelizable operations.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Processing a collection meant writing nested for-loops with mutable accumulators, temporary lists, and index tracking. Filtering, transforming, and aggregating required 15-20 lines of imperative code for what is logically a three-step pipeline. The code was hard to read, hard to parallelize, and easy to get wrong.

**THE BREAKING POINT:**
When you need to filter employees by department, map to their salaries, remove nulls, sort, and sum - that is a five-step pipeline. With loops, it becomes 25 lines of mutable state. One off-by-one error in the index, one forgotten null check, and you have a production bug.

**THE INVENTION MOMENT:**
"This is exactly why the Streams API was created."

**EVOLUTION:**
External iteration (for-each loops) -> internal iteration (Streams, Java 8) -> `toList()` collector shortcut (Java 16) -> gatherers API for custom intermediate operations (Java 22+).
---

### 📘 Textbook Definition

A Stream is a sequence of elements supporting sequential and parallel aggregate operations. Streams are lazy - intermediate operations build a pipeline that executes only when a terminal operation is invoked. Streams do not store data; they pull elements from a source (collection, array, generator) and push them through a pipeline of transformations.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
Streams are assembly lines for data: source in, transformations in the middle, result out.

**One analogy:**

> A stream is like a factory assembly line. Raw materials (collection elements) enter one end. Each station (intermediate operation) modifies or filters them. The product comes off the end (terminal operation). The line doesn't run until someone orders output.

**One insight:**
Streams are lazy by design. Calling `.filter().map().sorted()` builds a pipeline but processes zero elements. Only when you call `.collect()` or `.forEach()` does a single pass through the data begin. This means short-circuiting operations like `.findFirst()` can stop early without processing the entire collection.
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A stream pipeline has one source, zero or more intermediate operations, and one terminal operation
2. Intermediate operations are lazy - they return a new stream and do nothing until terminal
3. Streams are consumed once - after a terminal operation, the stream cannot be reused
4. Streams do not mutate the underlying data source

**DERIVED DESIGN:**
Laziness enables fusion: the JVM combines multiple intermediate operations into a single pass. `filter().map().filter()` does not create three intermediate collections - it creates one composite function applied element by element. This is why streams often outperform manual loops despite appearing higher-level.

**THE TRADE-OFFS:**
**Gain:** Declarative, composable, parallelizable, short-circuit-able
**Cost:** Single-use, debugging is harder (no breakpoints between stages), slight overhead for simple operations, parallel streams need careful thread-safety

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The pipeline model (source -> transform -> collect) is fundamental to data processing.
**Accidental:** The inability to reuse a stream is a design choice for simplicity, not a mathematical necessity.
---

### 🧠 Mental Model / Analogy

> A stream is a water pipe system. The reservoir (data source) holds water, but nothing flows until you open the faucet (terminal operation). Filters and valves (intermediate operations) are installed along the pipe but don't do anything until water flows. You can't reverse the flow or run water through the same pipe twice.

- "Reservoir" -> data source (collection, array, generator)
- "Pipe sections" -> intermediate operations (filter, map, sorted)
- "Faucet" -> terminal operation (collect, forEach, reduce)
- "Water flowing" -> elements being processed

Where this analogy breaks down: Unlike water, stream elements can be transformed (mapped) as they flow - a string element can become an integer element mid-pipeline.
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Streams let you describe what you want to do with a list of things (filter the red ones, count them) without writing step-by-step loop instructions.

**Level 2 - How to use it (junior developer):**

```java
// Filter, transform, collect
List<String> names = employees.stream()
    .filter(e -> e.getSalary() > 50000)
    .map(Employee::getName)
    .sorted()
    .collect(Collectors.toList());

// Reduce to single value
int total = numbers.stream()
    .reduce(0, Integer::sum);

// Check conditions
boolean anyOver100k = employees.stream()
    .anyMatch(e -> e.getSalary() > 100000);
```

**Level 3 - How it works (mid-level engineer):**
Streams use internal iteration. When you call `stream()`, a `Spliterator` is created over the source. Intermediate operations (`filter`, `map`, `sorted`) wrap each other as `AbstractPipeline` nodes. When the terminal operation fires, the pipeline calls `Spliterator.forEachRemaining()` and pushes each element through the composed function chain.

Stateless operations (filter, map, flatMap) process each element independently. Stateful operations (sorted, distinct, limit) must see multiple elements before producing output, which limits parallelization.

**Level 4 - Why it was designed this way (senior/staff+):**
The `Spliterator` interface is the key abstraction enabling parallelism. It supports `trySplit()` which divides the data source in half recursively, allowing the ForkJoinPool to process each half independently. The `characteristics()` method (ORDERED, SIZED, SORTED, DISTINCT) lets the pipeline skip unnecessary work - for example, calling `.sorted()` on an already-sorted source is a no-op if the spliterator declares SORTED.

The Collector API (`Collector<T,A,R>`) is deliberately designed for parallel reduction: `supplier()` creates a mutable container, `accumulator()` adds elements, `combiner()` merges partial results from parallel sub-tasks. This three-method pattern mirrors the MapReduce paradigm.


**Level 5 - Distinguished (expert thinking):**
Streams embody the fundamental programming paradigm shift from imperative to declarative data processing. The same pattern appears in SQL (declarative query), LINQ (.NET), RxJava (reactive streams), and Apache Spark (distributed data pipelines). The expert insight is that streams are lazy pipelines: no computation happens until a terminal operation triggers pull-based evaluation. This enables short-circuiting (`findFirst`, `anyMatch`), fusion (merging map+filter into one pass), and parallelism (splitting via `Spliterator`). At extreme scale, `parallelStream()` uses the common ForkJoinPool, which means a slow stream operation blocks ALL parallel streams in the JVM. Production systems must use custom ForkJoinPool instances. If redesigning today, you would add `Stream.gather()` (preview in Java 22) for user-defined intermediate operations and fix the checked-exception problem that makes streams unusable with IO-throwing functions.

**Expert thinking cues:**
- "Will this stream be consumed once?" - streams are single-use; accidental reuse throws `IllegalStateException`
- "Is parallel faster here?" - only for CPU-bound work on large datasets (>10K elements). IO-bound or small collections are slower parallel
- "Am I mutating state in stream operations?" - stateful lambdas in parallel streams cause race conditions
---

### How It Works (Mechanism)

```
  source.stream()
       |
  .filter(predicate)   [lazy - wraps pipeline]
       |
  .map(function)        [lazy - wraps pipeline]
       |
  .collect(collector)   [TERMINAL - triggers]
       |
       v
  Spliterator pulls elements one by one
  Each element flows through:
    predicate.test() -> true?
      -> function.apply()
        -> collector.accumulator().accept()
  Until Spliterator exhausted
       |
  collector.finisher() -> result
```

Key operations categorized:

| Type | Operations | Lazy? |
|------|------------|-------|
| Stateless intermediate | filter, map, flatMap, peek | Yes |
| Stateful intermediate | sorted, distinct, limit, skip | Yes |
| Short-circuit terminal | findFirst, findAny, anyMatch | No |
| Non-short-circuit terminal | collect, forEach, reduce, count | No |
---

### The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
  Collection          Stream Pipeline
  [A, B, C, D]  -->  .filter(x -> ...)
                     .map(x -> ...)
                     .collect(toList())
       |                    |
  <- YOU ARE HERE           v
                     Terminal triggers
                     Spliterator walks
                     source element by
                     element through
                     composed pipeline
                            |
                     Result: [B', D']
```

**FAILURE PATH:**
- Using a stream after terminal operation: `IllegalStateException: stream has already been operated upon`
- Parallel stream with non-thread-safe collector: data corruption or `ArrayIndexOutOfBoundsException`
- Modifying source during stream operation: `ConcurrentModificationException`
- `flatMap` with null return: `NullPointerException`

**WHAT CHANGES AT SCALE:**
Parallel streams use the common ForkJoinPool (default threads = CPU cores - 1). If your parallel stream does I/O, it blocks a ForkJoinPool thread, starving other parallel operations across the entire JVM. For I/O-bound work, use a custom ForkJoinPool or CompletableFuture instead of parallel streams.

---

### 💻 Code Example

**BAD - Imperative loop with mutable state:**

```java
List<String> result = new ArrayList<>();
for (Employee e : employees) {
    if (e.getDepartment().equals("Engineering")) {
        if (e.getSalary() > 80000) {
            result.add(e.getName().toUpperCase());
        }
    }
}
Collections.sort(result);
```

**GOOD - Stream pipeline:**

```java
List<String> result = employees.stream()
    .filter(e -> "Engineering"
        .equals(e.getDepartment()))
    .filter(e -> e.getSalary() > 80000)
    .map(Employee::getName)
    .map(String::toUpperCase)
    .sorted()
    .toList(); // Java 16+
```

**GOOD - Complex aggregation:**

```java
Map<String, DoubleSummaryStatistics> stats =
    employees.stream()
        .collect(Collectors.groupingBy(
            Employee::getDepartment,
            Collectors.summarizingDouble(
                Employee::getSalary)));
// stats.get("Engineering").getAverage()
// stats.get("Engineering").getMax()
```

**How to test / verify correctness:**

```java
@Test
void streamProducesCorrectResult() {
    List<Employee> input = List.of(
        new Employee("Alice", "Eng", 90000),
        new Employee("Bob", "HR", 70000),
        new Employee("Carol", "Eng", 85000));

    List<String> result = input.stream()
        .filter(e -> "Eng"
            .equals(e.getDepartment()))
        .map(Employee::getName)
        .sorted()
        .toList();

    assertEquals(List.of("Alice", "Carol"),
        result);
}
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** Lazy, declarative pipeline for transforming and aggregating collections
**PROBLEM IT SOLVES:** Replaces imperative loops with composable filter-map-reduce chains
**KEY INSIGHT:** Lazy evaluation - nothing executes until a terminal operation triggers pull-through
**USE WHEN:** Collection transformations, aggregations, filtering, grouping, parallel processing
**AVOID WHEN:** Simple iteration with side effects, small collections (<100 elements), or when readability suffers
**ANTI-PATTERN:** Using `parallelStream()` without measuring - it uses the common ForkJoinPool and can starve other tasks
**TRADE-OFF:** Declarative clarity and potential parallelism vs debugging difficulty and single-use constraint
**ONE-LINER:** "Declarative data pipeline - lazy, composable, parallelizable, single-use"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**
1. Streams are lazy - nothing executes until terminal operation
2. Streams are single-use - consumed after terminal operation
3. Parallel streams use ForkJoinPool - don't use for I/O

**Interview one-liner:**
"Streams provide a lazy, composable pipeline for aggregate operations over data sources, enabling declarative data processing with optional parallelism through Spliterator-based decomposition."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

`stream().count()` on an `ArrayList` does not iterate through the elements at all. Since `ArrayList`'s Spliterator declares the SIZED characteristic, the stream pipeline can simply call `list.size()` and return it directly. The JVM skips the entire pipeline for known-size sources with no intermediate operations that change the count.
---

### ⚖️ Comparison Table

| Aspect | Stream | For-each Loop | Iterator |
|--------|--------|--------------|---------|
| Style | Declarative | Imperative | Imperative |
| Lazy | Yes | No | Yes |
| Parallel | Built-in | Manual | No |
| Reusable | No (single-use) | Yes | No |
| Side effects | Discouraged | Normal | Normal |
| Debugging | Harder | Easy | Easy |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Streams are always faster than loops | For small collections (<100 elements) or simple operations, for-loops are faster due to less overhead. Streams add object creation and method call layers. |
| 2 | `parallelStream()` always improves performance | Parallel streams use the common ForkJoinPool. For IO-bound work, small data, or ordered operations, parallel is slower. Measure before parallelizing. |
| 3 | Streams can be reused | A stream can only be consumed once. Calling a terminal operation twice throws `IllegalStateException`. Create a new stream from the source for each use. |
| 4 | Stream operations execute immediately | Intermediate operations (`map`, `filter`) are lazy - they build a pipeline. Nothing executes until a terminal operation (`collect`, `forEach`) triggers evaluation. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: IllegalStateException - stream already consumed**
**Symptom:** `IllegalStateException: stream has already been operated upon or closed`.
**Root Cause:** Calling two terminal operations on the same stream, or storing a stream in a variable and reusing it.
**Diagnostic:**

```
# Search for stream stored in variable and reused
grep -n 'stream()' MyClass.java
# Check if same variable is used in two terminals
```

**Fix:**
```java
// BAD: reusing stream
Stream<String> s = list.stream().filter(x -> !x.isEmpty());
long count = s.count();
List<String> result = s.collect(toList()); // ISE!

// GOOD: create new stream each time
long count = list.stream().filter(x -> !x.isEmpty()).count();
List<String> result = list.stream()
    .filter(x -> !x.isEmpty()).collect(toList());
```
**Prevention:** Never store streams in variables. Chain from source to terminal in one expression.

**Failure Mode 2: Side effects in parallel stream**
**Symptom:** Intermittent wrong results, data corruption, or `ArrayIndexOutOfBoundsException` in parallel stream.
**Root Cause:** Lambda modifies shared mutable state (e.g., adding to a non-thread-safe list).
**Diagnostic:**

```
# Search for mutation inside stream lambdas
grep -n 'parallelStream\|parallel()' MyClass.java
# Check for .add(), .put(), ++, = inside forEach
```

**Fix:**
```java
// BAD: mutating shared state
List<String> results = new ArrayList<>();
data.parallelStream()
    .map(String::toUpperCase)
    .forEach(results::add); // race!

// GOOD: use collect()
List<String> results = data.parallelStream()
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```
**Prevention:** Never mutate shared state in stream lambdas. Use `collect()` for aggregation.

**Failure Mode 3: Common ForkJoinPool starvation**
**Symptom:** All `parallelStream()` operations in the JVM slow down when one has a blocking call.
**Root Cause:** `parallelStream()` uses the shared `ForkJoinPool.commonPool()`. A blocking lambda (DB/IO) occupies all threads.
**Diagnostic:**

```
jstack <pid> | grep "ForkJoinPool.commonPool"
# All threads blocked in IO = starvation
```

**Fix:**
```java
// BAD: blocking IO in common pool
data.parallelStream()
    .map(id -> db.findById(id)) // blocks!
    .collect(toList());

// GOOD: custom ForkJoinPool
ForkJoinPool pool = new ForkJoinPool(4);
pool.submit(() ->
    data.parallelStream()
        .map(id -> db.findById(id))
        .collect(toList())
).get();
```
**Prevention:** Use custom ForkJoinPool for IO-bound parallel streams. Keep common pool for CPU-bound work only.
---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between intermediate and terminal operations? Give examples of each type.**

*Why they ask:* Tests foundational understanding of the stream lifecycle.

*Strong answer:*

**Intermediate operations** return a new Stream and are lazy - they execute nothing until a terminal operation is invoked. They build a pipeline:
- Stateless: `filter()`, `map()`, `flatMap()`, `peek()` - each element processed independently
- Stateful: `sorted()`, `distinct()`, `limit()`, `skip()` - must see multiple elements

**Terminal operations** consume the stream and produce a result or side effect. They trigger the pipeline:
- Reduction: `collect()`, `reduce()`, `count()`, `min()`, `max()`
- Search: `findFirst()`, `findAny()`, `anyMatch()`, `allMatch()`
- Side effect: `forEach()`

Key distinction: after a terminal operation, the stream is consumed. Calling any operation on it throws `IllegalStateException`.

```java
Stream<String> s = list.stream()
    .filter(x -> x.length() > 3) // intermediate
    .map(String::toUpperCase);    // intermediate
// Nothing has executed yet

List<String> result =
    s.collect(Collectors.toList()); // terminal
// NOW all elements are processed

// s.count(); // IllegalStateException!
```

Short-circuiting terminals (`findFirst`, `anyMatch`, `limit`) can avoid processing all elements. `sorted()` is the most expensive intermediate operation because it must buffer all elements before producing output.

---

**Q2: When should you use parallel streams, and when should you avoid them?**

*Why they ask:* Tests production experience and performance intuition.

*Strong answer:*

**Use parallel streams when ALL of these are true:**
1. Large data set (>10,000 elements is a rough threshold)
2. CPU-bound operations (computation, not I/O)
3. Source supports efficient splitting (ArrayList, arrays - yes; LinkedList, HashSet - poor)
4. No shared mutable state
5. Order doesn't matter (or you accept the ordering overhead)

**Avoid parallel streams when:**
1. **I/O-bound work:** Parallel streams use the common ForkJoinPool. Blocking I/O starves the pool, affecting all parallel streams in the JVM.
2. **Small data sets:** Thread coordination overhead exceeds computation savings.
3. **LinkedList or Iterator source:** Cannot be split efficiently.
4. **Ordered operations required:** `forEachOrdered()` eliminates parallelism benefits.
5. **Non-thread-safe accumulators:** Using `ArrayList::add` as a downstream collector in parallel = data corruption.

```java
// GOOD: CPU-bound, large array, no shared state
double avg = largeArray.parallelStream()
    .mapToDouble(this::expensiveComputation)
    .average()
    .orElse(0);

// BAD: I/O in parallel stream
list.parallelStream()
    .forEach(item -> {
        httpClient.send(item); // blocks FJP
    });

// BETTER: Use CompletableFuture for I/O
List<CompletableFuture<Void>> futures =
    list.stream()
        .map(item -> CompletableFuture
            .runAsync(
                () -> httpClient.send(item),
                ioExecutor))
        .toList();
CompletableFuture.allOf(
    futures.toArray(new CompletableFuture[0]))
    .join();
```

You can use a custom ForkJoinPool to isolate parallel streams:
```java
ForkJoinPool custom =
    new ForkJoinPool(4);
List<String> result = custom.submit(
    () -> list.parallelStream()
        .filter(...)
        .collect(toList())
).get();
```

---

**Q3: Explain `flatMap`. When do you use it instead of `map`?**

*Why they ask:* Tests understanding of one-to-many transformations.

*Strong answer:*

`map` transforms each element 1:1. `flatMap` transforms each element into zero or more elements and flattens the results into a single stream.

Use `flatMap` when each element maps to a collection/stream:

```java
// map: Stream<List<String>>  (NOT what we want)
Stream<List<String>> nested =
    orders.stream()
        .map(Order::getLineItems);

// flatMap: Stream<String>  (flattened)
Stream<String> flat =
    orders.stream()
        .flatMap(order ->
            order.getLineItems().stream());
```

Common use cases:
1. **One-to-many:** Each order has multiple items
2. **Optional unwrapping:** `Stream<Optional<T>>` -> `Stream<T>`
3. **Nested structures:** Flatten a list of lists

```java
// Flatten list of lists
List<List<Integer>> nested =
    List.of(List.of(1,2), List.of(3,4));
List<Integer> flat = nested.stream()
    .flatMap(Collection::stream)
    .toList(); // [1, 2, 3, 4]

// Filter out empty Optionals (Java 9+)
Stream<String> values =
    optionals.stream()
        .flatMap(Optional::stream);

// Word frequency from lines of text
Map<String, Long> freq =
    lines.stream()
        .flatMap(line ->
            Arrays.stream(line.split("\\s+")))
        .collect(Collectors.groupingBy(
            Function.identity(),
            Collectors.counting()));
```

**Performance note:** Each `flatMap` call creates a new stream per element. For very hot paths, consider restructuring to avoid `flatMap` if profiling shows it as a bottleneck.

---

**Q4: What are Collectors and how do `groupingBy`, `partitioningBy`, and `toMap` differ?**

*Why they ask:* Tests practical data aggregation skills.

*Strong answer:*

Collectors define how to accumulate stream elements into a result container. They have three components: supplier (create container), accumulator (add element), combiner (merge parallel results).

**`groupingBy`** - Groups elements into a `Map<K, List<V>>` by a classifier function:

```java
Map<String, List<Employee>> byDept =
    employees.stream()
        .collect(Collectors.groupingBy(
            Employee::getDepartment));

// With downstream collector
Map<String, Double> avgSalary =
    employees.stream()
        .collect(Collectors.groupingBy(
            Employee::getDepartment,
            Collectors.averagingDouble(
                Employee::getSalary)));
```

**`partitioningBy`** - Special case: splits into exactly two groups (true/false):

```java
Map<Boolean, List<Employee>> partitioned =
    employees.stream()
        .collect(Collectors.partitioningBy(
            e -> e.getSalary() > 100000));
List<Employee> highEarners =
    partitioned.get(true);
```

**`toMap`** - Creates a `Map<K, V>` with explicit key/value extractors:

```java
Map<Integer, String> idToName =
    employees.stream()
        .collect(Collectors.toMap(
            Employee::getId,
            Employee::getName));

// Handle duplicate keys
Map<String, Employee> byName =
    employees.stream()
        .collect(Collectors.toMap(
            Employee::getName,
            Function.identity(),
            (existing, dup) -> existing));
```

Key differences: `groupingBy` always produces `Map<K, List<V>>` (or downstream-reduced). `partitioningBy` always produces `Map<Boolean, List<V>>`. `toMap` produces `Map<K, V>` where each key maps to one value (duplicate keys throw `IllegalStateException` unless a merge function is provided).

---

**Q5: How do you handle exceptions inside stream operations?**

*Why they ask:* Tests real-world production experience with streams.

*Strong answer:*

Stream operations accept functional interfaces that don't declare checked exceptions. This is a deliberate design choice - checked exceptions would break the composability of lambdas. Here are the patterns:

**Pattern 1: Wrap in unchecked exception**

```java
// Helper method
static <T, R> Function<T, R> unchecked(
        ThrowingFunction<T, R> f) {
    return t -> {
        try { return f.apply(t); }
        catch (Exception e) {
            throw new RuntimeException(e);
        }
    };
}

@FunctionalInterface
interface ThrowingFunction<T, R> {
    R apply(T t) throws Exception;
}

// Usage
List<URL> urls = strings.stream()
    .map(unchecked(URL::new))
    .toList();
```

**Pattern 2: Collect successes and failures separately**

```java
Map<Boolean, List<String>> results =
    strings.stream()
        .collect(Collectors.partitioningBy(
            s -> {
                try {
                    new URL(s); return true;
                } catch (Exception e) {
                    return false;
                }
            }));
```

**Pattern 3: Use Either/Try monad (libraries like Vavr)**

```java
List<Try<URL>> attempts = strings.stream()
    .map(s -> Try.of(() -> new URL(s)))
    .toList();
List<URL> successes = attempts.stream()
    .filter(Try::isSuccess)
    .map(Try::get)
    .toList();
```

The anti-pattern is catching the exception inside the lambda and silently swallowing it. Always make failure handling explicit.
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Lambda Expressions - streams require lambdas for all operations
- Collections Framework - streams operate on collections and arrays

**Builds on this (learn these next):**

- Collectors API - advanced grouping, partitioning, and reduction
- Parallel streams and ForkJoinPool - concurrent data processing

**Alternatives / Comparisons:**

- For-each loops - simpler for side-effect-heavy or small operations
- RxJava/Reactor - push-based reactive streams with backpressure


---

---

# Optional

**TL;DR** - Optional is a container that explicitly represents the presence or absence of a value, eliminating null pointer exceptions by forcing the caller to handle the "missing" case.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Methods return `null` to mean "no result found." The caller forgets to check, chains a method call on the null return, and gets a `NullPointerException` at 3 AM in production. Tony Hoare called null his "billion-dollar mistake." Every Java codebase has hundreds of defensive `if (x != null)` checks scattered through the code.

**THE BREAKING POINT:**
`NullPointerException` is consistently the #1 exception in Java production systems. The problem is not null itself - it is that null is invisible in the type system. A method signature `Employee findById(int id)` gives no indication that it might return nothing.

**THE INVENTION MOMENT:**
"This is exactly why Optional was created."

**EVOLUTION:**
Null checks everywhere (pre-Java 8) -> `Optional<T>` as return type (Java 8) -> `Optional.ifPresentOrElse()` and `Optional.stream()` (Java 9) -> improved `Optional` pattern matching (future Java versions).
---

### 📘 Textbook Definition

`Optional<T>` is a container object that may or may not contain a non-null value. It provides methods to explicitly handle both cases (`isPresent`, `ifPresent`, `orElse`, `map`, `flatMap`) and is designed to be used as a method return type to indicate that a result may be absent.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
Optional wraps a value that might not exist, forcing you to handle the missing case explicitly.

**One analogy:**

> Optional is like a gift box that might be empty. Instead of handing someone a present that could be a box of nothing (null), you hand them a clearly labeled box that says "MIGHT BE EMPTY - CHECK FIRST." They must open it consciously.

**One insight:**
Optional does not prevent null - it makes absence visible in the type system. When a method returns `Optional<Employee>`, the caller knows immediately that the result might not exist. When it returns `Employee`, the caller can assume it always exists. The type system communicates intent.
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An Optional is either empty or contains exactly one non-null value
2. `Optional.of(null)` throws `NullPointerException` - use `Optional.ofNullable()` for possibly-null values
3. Optional is a value-based class - never use `==`, never use as a field, never serialize it

**DERIVED DESIGN:**
Optional supports `map()` and `flatMap()` to chain transformations without explicit presence checks. This enables a functional style: `findUser(id).map(User::getEmail).orElse("unknown")` instead of nested null checks.

**THE TRADE-OFFS:**
**Gain:** NullPointerException prevention, self-documenting APIs, composable with streams and lambdas
**Cost:** Object allocation overhead, should not be used for fields or method parameters, learning curve

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The concept of "maybe a value" is fundamental - every language has it (Haskell's Maybe, Rust's Option, Kotlin's nullable types).
**Accidental:** Java's Optional is a library solution, not a language feature. It cannot be used in generics (no `Optional<int>`), and there is nothing preventing someone from passing `null` where an Optional is expected.
---

### 🧠 Mental Model / Analogy

> Optional is like a safe deposit box with a glass window. You can see whether there is something inside without opening it (`isPresent`). If there is something, you can take it out (`get`), transform it while it stays inside (`map`), or provide a default if it's empty (`orElse`).

- "Glass window" -> `isPresent()`, `isEmpty()`
- "Opening the box" -> `get()` (throws if empty)
- "Transform while inside" -> `map()`, `flatMap()`
- "Default if empty" -> `orElse()`, `orElseGet()`

Where this analogy breaks down: Unlike a physical box, Optional is immutable - you cannot put something in or take something out. Each operation returns a new Optional.
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Optional is a wrapper that says "this value might not exist." Instead of getting a surprise error when you try to use a missing value, Optional makes you handle that possibility upfront.

**Level 2 - How to use it (junior developer):**

```java
// Creating Optionals
Optional<String> present =
    Optional.of("hello");
Optional<String> empty =
    Optional.empty();
Optional<String> maybe =
    Optional.ofNullable(possiblyNull);

// Using Optionals
String value = maybe.orElse("default");
String computed = maybe
    .orElseGet(() -> expensiveDefault());
maybe.ifPresent(v ->
    System.out.println(v));
```

**Level 3 - How it works (mid-level engineer):**

Optional is a simple wrapper class with a private `value` field. `Optional.empty()` returns a shared singleton instance. `Optional.of(value)` checks for null and wraps the value.

The real power is in chaining:

```java
// Instead of nested null checks:
String city = null;
if (user != null) {
    Address addr = user.getAddress();
    if (addr != null) {
        city = addr.getCity();
    }
}

// Optional chain:
String city = Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown");
```

`map` applies a function if the value is present and wraps the result in a new Optional. If the value is absent, it returns `Optional.empty()` without calling the function. `flatMap` is used when the function itself returns an Optional, avoiding `Optional<Optional<T>>` nesting.

**Level 4 - Why it was designed this way (senior/staff+):**

Optional was deliberately designed with restrictions:

1. **Not serializable:** Prevents use as a persistent field - it is a return type signal, not a storage type.
2. **Value-based class:** The JVM may cache and reuse instances. Using `==` or synchronizing on Optional is undefined behavior.
3. **No `Optional<int>`:** Separate `OptionalInt`, `OptionalDouble`, `OptionalLong` exist to avoid boxing. This is an artifact of type erasure.

The Java team (Brian Goetz) explicitly stated Optional is meant for return types only. Using it as a method parameter forces callers to wrap values unnecessarily. Using it as a field wastes 16 bytes of object header per field.


**Level 5 - Distinguished (expert thinking):**
Optional is Java's implementation of the Maybe/Option monad found in Haskell (`Maybe`), Rust (`Option<T>`), Scala (`Option[T]`), and Swift (`Optional<T>`). The cross-domain insight: Optional encodes the concept of 'absence' in the type system, forcing the caller to handle the no-value case explicitly rather than ignoring it. This is the same pattern as null-safe navigation in Kotlin (`?.`), nullable reference types in C# 8+, and Result types for error handling. At extreme scale, Optional's limitation is boxing: `Optional<Integer>` double-boxes the value (Optional object wrapping Integer object wrapping int). `OptionalInt`/`OptionalLong` exist for primitives but don't compose with the generic stream API. If redesigning today, Valhalla value types would make Optional zero-cost (stack-allocated, no header).

**Expert thinking cues:**
- "Is this a field or a return type?" - Optional is for return types, never for fields, parameters, or collections
- "Am I using `get()` without `isPresent()`?" - if yes, use `orElse`/`orElseThrow`/`map` instead
- "Is the default value expensive?" - use `orElseGet(supplier)` not `orElse(expensiveCall())` to avoid eager evaluation
---

### How It Works (Mechanism)

```
  Optional.of("hello")
       |
  Wraps value in Optional instance
  (null check - throws NPE if null)
       |
  .map(String::toUpperCase)
       |
  Value present?
    YES -> apply function, wrap result
    NO  -> return Optional.empty()
       |
  .orElse("default")
       |
  Value present?
    YES -> return unwrapped value
    NO  -> return "default"
```
---

### The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
  Repository.findById(42)
       |
  Returns Optional<User>
       |
  <- YOU ARE HERE
       |
  .map(User::getProfile)
       |
  .map(Profile::getAvatar)
       |
  .orElse(DEFAULT_AVATAR)
       |
  Result: avatar URL or default
```

**FAILURE PATH:**
- Calling `.get()` on empty Optional: `NoSuchElementException`
- Using `Optional.of(null)`: `NullPointerException` at creation
- Chaining without `flatMap` when function returns Optional: `Optional<Optional<T>>` - compile error

**WHAT CHANGES AT SCALE:**
In hot paths processing millions of values, Optional creates an extra object allocation per call. For performance-critical inner loops, consider returning null with `@Nullable` annotation instead. For API boundaries and service layers, Optional is the right choice - clarity outweighs micro-optimization.

---

### 💻 Code Example

**BAD - Null checks everywhere:**

```java
public String getUserCity(Long userId) {
    User user = userRepo.findById(userId);
    if (user != null) {
        Address address = user.getAddress();
        if (address != null) {
            return address.getCity();
        }
    }
    return "Unknown";
}
```

**GOOD - Optional chain:**

```java
public String getUserCity(Long userId) {
    return userRepo.findById(userId)
        .map(User::getAddress)
        .map(Address::getCity)
        .orElse("Unknown");
}
```

**BAD - Using Optional wrong:**

```java
// Anti-pattern 1: Optional as parameter
void process(Optional<String> name) { }

// Anti-pattern 2: Optional as field
class User {
    Optional<String> middleName; // NO
}

// Anti-pattern 3: isPresent + get
if (opt.isPresent()) {
    return opt.get(); // just use orElse
}
```

**GOOD - Proper Optional patterns:**

```java
// ifPresentOrElse (Java 9+)
userOpt.ifPresentOrElse(
    user -> greet(user),
    () -> log.warn("User not found"));

// or() - lazy fallback Optional (Java 9+)
Optional<User> user = localCache
    .find(id)
    .or(() -> remoteService.find(id))
    .or(() -> Optional.of(GUEST_USER));

// stream() - integrate with streams (Java 9+)
List<String> names = userIds.stream()
    .map(repo::findById)
    .flatMap(Optional::stream)
    .map(User::getName)
    .toList();
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** Container that either holds a non-null value or is explicitly empty
**PROBLEM IT SOLVES:** Makes absence explicit in the type system, replacing null-check chains
**KEY INSIGHT:** Forces callers to handle the no-value case - NPEs become compile-time type errors
**USE WHEN:** Method return types where absence is a valid outcome (e.g., findById)
**AVOID WHEN:** Fields, method parameters, collections, or performance-critical inner loops
**ANTI-PATTERN:** `optional.get()` without `isPresent()` check - defeats the entire purpose
**TRADE-OFF:** Null safety and self-documenting API vs object allocation overhead and verbose chaining
**ONE-LINER:** "Type-safe null - makes absence visible, forces handling, eliminates NPE"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**
1. Optional is for return types only - never fields, parameters, or serialization
2. Use `map`/`flatMap`/`orElse` chains instead of `isPresent()`+`get()`
3. `Optional.of(null)` throws NPE - use `ofNullable()` for uncertain values

**Interview one-liner:**
"Optional is a type-level signal that a value may be absent, replacing null returns with a composable container that forces explicit handling of the missing case."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

In performance-critical code, Optional is slower than null checks because it allocates a heap object. But JVM escape analysis can often eliminate the allocation entirely if the Optional never leaves the method scope. In JMH benchmarks with JIT-compiled code, `Optional.ofNullable(x).map(f).orElse(default)` compiles down to the same machine code as `x != null ? f(x) : default`. The abstraction cost is zero after JIT optimization.
---

### ⚖️ Comparison Table

| Aspect | Optional | Null | Kotlin Nullable (`T?`) |
|--------|----------|------|----------------------|
| Type safety | Compile-time | None | Compile-time |
| Memory | Object allocation | Zero | Zero |
| Chaining | `map`/`flatMap` | Nested ifs | `?.` operator |
| Absence visible | In signature | No | In signature |
| Serializable | No | N/A | N/A |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | `Optional.get()` is safe to call | `get()` throws `NoSuchElementException` if empty. Use `orElse()`, `orElseGet()`, or `orElseThrow()` instead. `get()` without `isPresent()` defeats the purpose. |
| 2 | Optional should be used for method parameters | Optional is designed for return types only. For parameters, use method overloading or `@Nullable`. Optional parameters add unnecessary wrapping. |
| 3 | Optional prevents all NPEs | You can still get NPE if: you pass null to `Optional.of()` (use `ofNullable`), call `get()` on empty, or store null in a field that should be Optional. |
| 4 | Optional has negligible overhead | Each `Optional.of()` creates an object on the heap. In tight loops, this adds GC pressure. Use `OptionalInt`/`OptionalLong` for primitives. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: NoSuchElementException from get()**
**Symptom:** `NoSuchElementException: No value present` from `Optional.get()`.
**Root Cause:** Calling `get()` without checking `isPresent()` - the anti-pattern Optional was designed to prevent.
**Diagnostic:**

```
grep -n '\.get()' MyClass.java
# Check for Optional.get() calls without guards
```

**Fix:**
```java
// BAD: unsafe get
String name = findUser(id).get(); // throws!

// GOOD: provide default or throw with context
String name = findUser(id)
    .orElseThrow(() -> new UserNotFoundException(id));
```
**Prevention:** Ban `Optional.get()` via code review or linting rules. Use `orElse`/`orElseThrow`/`map`.

**Failure Mode 2: NullPointerException from Optional.of(null)**
**Symptom:** `NullPointerException` at `Optional.of()` call site.
**Root Cause:** Using `Optional.of(value)` when value can be null. `of()` requires non-null.
**Diagnostic:**

```
grep -n 'Optional\.of(' MyClass.java
# Check if argument can be null at runtime
```

**Fix:**
```java
// BAD: of() with nullable value
Optional<User> user = Optional.of(repo.find(id));
// Throws NPE if find returns null!

// GOOD: use ofNullable
Optional<User> user = Optional.ofNullable(
    repo.find(id));
```
**Prevention:** Use `Optional.ofNullable()` for values that might be null. Reserve `Optional.of()` for known non-null values.

**Failure Mode 3: Eager evaluation with orElse()**
**Symptom:** Expensive fallback method called even when Optional has a value.
**Root Cause:** `orElse(expensiveCall())` evaluates the argument eagerly, regardless of Optional state.
**Diagnostic:**

```
grep -n '\.orElse(' MyClass.java
# Check if argument has side effects or is expensive
```

**Fix:**
```java
// BAD: eager evaluation - DB called always
User u = findCached(id)
    .orElse(findFromDb(id)); // always calls DB!

// GOOD: lazy evaluation - DB called only if empty
User u = findCached(id)
    .orElseGet(() -> findFromDb(id));
```
**Prevention:** Use `orElseGet(supplier)` when the default value is expensive or has side effects. `orElse()` is only safe for constants.
---

### 🎯 Interview Deep-Dive

**Q1: What are the anti-patterns when using Optional, and why does Java's design specifically discourage them?**

*Why they ask:* Tests whether you use Optional correctly in production code.

*Strong answer:*

The three main anti-patterns and why:

1. **Optional as a method parameter:** Forces every caller to wrap their value in `Optional.ofNullable()` before calling. The method should accept the raw type and handle null internally. Parameters are inputs, not signals about presence.

2. **Optional as a class field:** Each Optional adds 16 bytes of object header overhead. More importantly, Optional is not serializable, so it breaks JPA entities, JSON serialization, and any persistence framework. Use `@Nullable` for fields.

3. **`isPresent()` + `get()` pattern:** This is just a null check with extra steps. It defeats the purpose of Optional, which is to use functional composition (`map`, `flatMap`, `orElse`).

```java
// Anti-pattern: Optional.get() without check
String name = findUser(id).get(); // NPE danger

// Anti-pattern: isPresent + get
Optional<User> opt = findUser(id);
if (opt.isPresent()) {
    return opt.get().getName(); // WHY?
}
return "Unknown";

// Correct: functional chain
return findUser(id)
    .map(User::getName)
    .orElse("Unknown");
```

Brian Goetz (Java language architect) has explicitly said: "Optional is intended to provide a limited mechanism for library method return types where there is a clear need to represent 'no result.'" It was never intended as a general-purpose Maybe type.

---

**Q2: Explain the difference between `map` and `flatMap` on Optional with a practical example.**

*Why they ask:* Tests understanding of monadic composition.

*Strong answer:*

`map` applies a function to the value inside the Optional. If the function returns a plain value, the result is wrapped in a new Optional:
- `Optional<T>.map(T -> R)` returns `Optional<R>`

`flatMap` applies a function that itself returns an Optional, and "flattens" the result to avoid double wrapping:
- `Optional<T>.flatMap(T -> Optional<R>)` returns `Optional<R>`

Without `flatMap`, you would get `Optional<Optional<R>>`.

```java
// map - function returns plain value
Optional<String> name =
    findUser(id).map(User::getName);
// Optional<String> - correct

// map - function returns Optional
Optional<Optional<Address>> nested =
    findUser(id).map(User::findAddress);
// Optional<Optional<Address>> - WRONG!

// flatMap - function returns Optional
Optional<Address> address =
    findUser(id).flatMap(User::findAddress);
// Optional<Address> - correct

// Real-world chain
String city = findUser(id)
    .flatMap(User::findAddress)  // Optional
    .flatMap(Address::findCity)  // Optional
    .map(City::getName)          // plain String
    .orElse("Unknown");
```

Rule of thumb: use `map` when your function returns a plain value, use `flatMap` when your function returns `Optional`. This is the same pattern as `Stream.map` vs `Stream.flatMap`.

---

**Q3: How does Optional compare to Kotlin's nullable types (`String?`) and Rust's `Option<T>`?**

*Why they ask:* Tests breadth of understanding and language design trade-offs.

*Strong answer:*

| Aspect | Java Optional | Kotlin `?` | Rust `Option<T>` |
|--------|---------------|-------------|-------------------|
| Level | Library class | Language feature | Language enum |
| Null safety | Runtime only | Compile-time | Compile-time |
| Cost | Object allocation | Zero cost | Zero cost |
| Nesting | Possible | Not possible | Possible |
| Pattern matching | No (future) | No (uses `?.`) | Yes (`match`) |

**Java Optional** is a retrofit solution. It does not eliminate null from the language - you can still have `null` Optional references. It is a convention, not a guarantee.

**Kotlin's approach** is superior for everyday use: the compiler tracks nullability through the type system. `String?` means nullable, `String` means never-null, and the compiler enforces this at compile time. The `?.` safe-call operator chains naturally without wrapping.

**Rust's `Option<T>`** is the gold standard. There is no null in Rust. `Option<T>` is `Some(T) | None`, and `match` forces exhaustive handling. The compiler makes it impossible to use a value without checking for `None` first.

Java's Optional is the weakest of the three because it is a library type bolted onto a language that still has null. But within Java's constraints, it is the best tool available. The combination of Optional return types + `@Nullable`/`@NonNull` annotations + static analysis tools (NullAway, SpotBugs) gets close to Kotlin-level safety.

---

**Q4: How do `orElse`, `orElseGet`, and `orElseThrow` differ, and when does the choice matter?**

*Why they ask:* Tests understanding of lazy evaluation and performance implications.

*Strong answer:*

```java
// orElse - always evaluates the default
String a = opt.orElse(computeDefault());

// orElseGet - evaluates only if empty
String b = opt.orElseGet(
    () -> computeDefault());

// orElseThrow - throws if empty
String c = opt.orElseThrow(
    () -> new NotFoundException(id));
```

The critical difference between `orElse` and `orElseGet`:

`orElse(value)` evaluates its argument eagerly, even if the Optional has a value. If the default is expensive (database query, HTTP call, object creation), this wastes resources:

```java
// BAD: DB query runs even when user exists
User user = findUser(id)
    .orElse(createDefaultUser()); // always runs

// GOOD: DB query only if user not found
User user = findUser(id)
    .orElseGet(() -> createDefaultUser());
```

Even worse, `orElse` with a side-effecting default can cause bugs:

```java
// BUG: creates a default user in DB even
// when the real user exists!
User user = findUser(id)
    .orElse(userRepo.save(
        new User("default")));
```

Rule: use `orElse` only with cheap, pre-computed constants. Use `orElseGet` for everything else.

---

**Q5: Can you use Optional with primitive types? What are the performance implications?**

*Why they ask:* Tests awareness of boxing overhead.

*Strong answer:*

`Optional<T>` cannot hold primitives directly due to type erasure. `Optional<int>` is invalid. Java provides three primitive specializations:

```java
OptionalInt    optInt    = OptionalInt.of(42);
OptionalLong   optLong   = OptionalLong.of(100L);
OptionalDouble optDouble = OptionalDouble.of(3.14);
```

These avoid autoboxing overhead. The difference matters in hot paths:

```java
// BAD: boxes every int into Integer
Optional<Integer> sum = numbers.stream()
    .reduce(Integer::sum);

// GOOD: no boxing
OptionalInt sum = numbers.stream()
    .mapToInt(Integer::intValue)
    .reduce(Integer::sum);
```

However, primitive Optionals are limited: they don't have `map`, `flatMap`, or `filter`. They only support `ifPresent`, `orElse`, `orElseGet`, `orElseThrow`, and `getAsInt`/`getAsLong`/`getAsDouble`.

This is another area where Java's type system shows its age. Kotlin's `Int?` handles nullable primitives without any of this ceremony, and Project Valhalla's value types will eventually allow `Optional<int>` in Java.
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Null references and NPE - the problem Optional solves
- Generics - Optional is a generic container type

**Builds on this (learn these next):**

- Stream operations returning Optional - `findFirst()`, `reduce()`
- Monadic chaining with `map`/`flatMap` - composing Optional pipelines

**Alternatives / Comparisons:**

- Kotlin nullable types (`T?`) - compiler-enforced null safety without wrapping
- `@Nullable` annotations - lightweight null documentation for static analysis


---

---

# Functional Interfaces

**TL;DR** - A functional interface has exactly one abstract method, making it a target for lambda expressions - the bridge between Java's object-oriented type system and functional programming.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before functional interfaces were formalized, Java had no standard way to represent "a piece of behavior" as a type. You could create interfaces with one method (like `Runnable`, `Comparator`), but there was no convention, no type safety guarantee, and no standard library of reusable behavior types.

**THE BREAKING POINT:**
Lambda expressions needed a target type. The language team needed a way to say "this interface can receive a lambda" without adding function types to Java. The answer: formalize the pattern of single-method interfaces that Java developers had been using for 20 years.

**THE INVENTION MOMENT:**
"This is exactly why the functional interface concept and `@FunctionalInterface` annotation were created."

**EVOLUTION:**
Single-method interfaces (Java 1.0, e.g., `Runnable`) -> `@FunctionalInterface` annotation and `java.util.function` package (Java 8) -> 43 standard functional interfaces covering all common patterns.
---

### 📘 Textbook Definition

A functional interface is any interface that has exactly one abstract method (SAM - Single Abstract Method). It may have any number of default methods and static methods. The `@FunctionalInterface` annotation is optional but provides compile-time validation that the interface maintains its single-abstract-method contract.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
A functional interface is an interface with exactly one abstract method - the contract a lambda must fulfill.

**One analogy:**

> A functional interface is like a power outlet. The outlet defines the shape (one abstract method signature). Any plug that matches the shape (lambda with matching parameters and return type) fits. The `@FunctionalInterface` annotation is a label on the outlet saying "only one plug shape accepted here."

**One insight:**
Every lambda in Java has a type, and that type is always a functional interface. When you write `(x) -> x + 1`, the compiler infers which functional interface it targets from context. The same lambda text can be a `Function<Integer,Integer>`, an `IntUnaryOperator`, or a custom interface - it depends on the assignment target.
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Exactly one abstract method (not counting `Object` methods like `toString`, `equals`, `hashCode`)
2. Can have any number of default and static methods
3. `@FunctionalInterface` is optional but recommended - it prevents accidental addition of a second abstract method

**DERIVED DESIGN:**
The `java.util.function` package provides 43 standard functional interfaces organized around four archetypes: `Function<T,R>` (transform), `Predicate<T>` (test), `Consumer<T>` (consume), `Supplier<T>` (produce). Primitive specializations (`IntFunction`, `ToLongFunction`, etc.) avoid autoboxing.

**THE TRADE-OFFS:**
**Gain:** Type safety for lambdas, reusable behavior types, composability via default methods (`and`, `or`, `compose`, `andThen`)
**Cost:** 43 interfaces is a lot to remember, primitive specializations add complexity, no support for checked exceptions in standard interfaces

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** A type system needs some mechanism to assign types to function values.
**Accidental:** Having 43 separate interfaces instead of true function types (`(T) -> R`) is an artifact of Java's type erasure. Kotlin, Scala, and other JVM languages have function types as first-class citizens.
---

### 🧠 Mental Model / Analogy

> Functional interfaces are like job descriptions that specify exactly one responsibility. "Someone who can compare two things" (Comparator), "someone who can test a condition" (Predicate), "someone who can transform a value" (Function). A lambda is the anonymous worker who fulfills that one job.

- "Job description" -> functional interface
- "One responsibility" -> single abstract method
- "Anonymous worker" -> lambda expression
- "Job agency" -> `java.util.function` package

Where this analogy breaks down: A job description can change. A functional interface cannot have its abstract method changed without breaking all existing lambdas targeting it.
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A functional interface is a special kind of interface that defines exactly one action. Because there is only one thing to do, Java can figure out what your lambda is supposed to implement.

**Level 2 - How to use it (junior developer):**

```java
// Standard functional interfaces
Function<String, Integer> length =
    String::length;
Predicate<String> nonEmpty =
    s -> !s.isEmpty();
Consumer<String> printer =
    System.out::println;
Supplier<List<String>> factory =
    ArrayList::new;

// Custom functional interface
@FunctionalInterface
interface Validator<T> {
    boolean validate(T item);
}

Validator<String> emailCheck =
    s -> s.contains("@");
```

**Level 3 - How it works (mid-level engineer):**

The compiler determines the target functional interface from context (target typing):

```java
// Same lambda, different target types
Comparator<String> comp =
    (a, b) -> a.length() - b.length();
ToIntBiFunction<String, String> func =
    (a, b) -> a.length() - b.length();
// Both valid - compiler infers target
```

Default methods on functional interfaces enable composition:

```java
Predicate<String> notEmpty =
    s -> !s.isEmpty();
Predicate<String> notTooLong =
    s -> s.length() < 100;

// Compose with and/or/negate
Predicate<String> valid =
    notEmpty.and(notTooLong);

Function<String, String> pipeline =
    String::trim
        .andThen(String::toLowerCase)
        .andThen(s -> s.replace(" ", "-"));
```

**Level 4 - Why it was designed this way (senior/staff+):**

The SAM type approach was chosen over true function types for backward compatibility. Every existing single-method interface in the JDK (`Runnable`, `Callable`, `Comparator`, `ActionListener`, etc.) automatically became a lambda target without any code changes. This was a massive win: millions of existing APIs became lambda-compatible overnight.

The alternative (adding function types like `(String) -> int`) would have required new syntax, new type system rules, and would not have been compatible with existing APIs. The tradeoff is verbosity: `Function<String, Integer>` vs `String -> int`. Kotlin made the other choice and has true function types.


**Level 5 - Distinguished (expert thinking):**
Functional interfaces are Java's bridge between object-oriented and functional paradigms. The same concept appears as protocols with single methods in Swift, traits with one abstract method in Rust, and single-abstract-method (SAM) types in Kotlin/Scala. The expert insight is that `@FunctionalInterface` is a compile-time constraint, not a runtime feature - it tells the compiler to reject an interface if it has more than one abstract method. The four core functional interfaces (`Function`, `Predicate`, `Consumer`, `Supplier`) form a complete algebra: any data transformation can be expressed as a composition of these primitives plus their bi-variants. At extreme scale, functional interfaces enable the strategy pattern without class proliferation: instead of N strategy classes, you pass N lambdas. If redesigning today, you would add built-in support for checked exceptions (`ThrowingFunction<T, R, E>`) to avoid the pervasive try-catch-wrap pattern in stream operations.

**Expert thinking cues:**
- "Which of the four core types fits?" - Function (T->R), Predicate (T->bool), Consumer (T->void), Supplier (()->T)
- "Should I create a custom functional interface?" - only when the four core types don't express the intent clearly enough
- "Can I compose these?" - use `.andThen()`, `.compose()`, `.and()`, `.or()`, `.negate()` for pipeline composition
---

### How It Works (Mechanism)

```
  @FunctionalInterface
  interface Converter<F, T> {
      T convert(F from);
  }
       |
  Compiler verifies: exactly 1 abstract method
       |
  Lambda assigned:
  Converter<String,Integer> c =
      Integer::parseInt;
       |
  Compiler matches lambda signature
  (String) -> Integer
  to abstract method
  Integer convert(String from)
       |
  invokedynamic generates implementation
```
---

### The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
  Define @FunctionalInterface
       |
  <- YOU ARE HERE
       |
  Assign lambda or method reference
       |
  Compiler type-checks against SAM
       |
  invokedynamic at callsite
       |
  LambdaMetafactory generates impl
       |
  Method invocation
```

**FAILURE PATH:**
- Adding a second abstract method to `@FunctionalInterface`: compile error
- Lambda signature mismatch with SAM: compile error ("incompatible types")
- Ambiguous target type (multiple overloads match): compile error ("ambiguous method call")

**WHAT CHANGES AT SCALE:**
In library design, functional interfaces are the public API for behavior injection. Choose standard `java.util.function` types whenever possible. Custom functional interfaces add API surface that users must learn. Only create custom ones when the standard 43 don't fit or when you need a more descriptive name (e.g., `Validator<T>` is clearer than `Predicate<T>` in a validation context).

---

### 💻 Code Example

**BAD - Creating unnecessary custom functional interfaces:**

```java
// Don't do this - Predicate already exists
@FunctionalInterface
interface StringChecker {
    boolean check(String s);
}

// Don't do this - Function already exists
@FunctionalInterface
interface Transformer<T, R> {
    R transform(T input);
}
```

**GOOD - Using standard functional interfaces:**

```java
// Use Predicate for boolean checks
Predicate<String> valid =
    s -> s != null && s.length() > 3;

// Use Function for transformations
Function<String, String> normalize =
    String::trim;

// Custom only when it adds clarity
@FunctionalInterface
interface RetryPolicy {
    Duration getDelay(int attemptNumber);
}
// Better than Function<Integer,Duration>
// because the name communicates intent
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** Interface with exactly one abstract method - the lambda target type
**PROBLEM IT SOLVES:** Provides the type system bridge between OOP interfaces and lambda expressions
**KEY INSIGHT:** Four core types cover most use cases: Function (T->R), Predicate (T->bool), Consumer (T->void), Supplier (()->T)
**USE WHEN:** Defining lambda-compatible APIs, strategy pattern, callback contracts
**AVOID WHEN:** Interface needs multiple abstract methods - use a regular interface
**ANTI-PATTERN:** Creating custom functional interfaces when `Function`/`Predicate`/`Consumer`/`Supplier` already fit
**TRADE-OFF:** Lambda compatibility and composability vs less descriptive than named interface methods
**ONE-LINER:** "One abstract method = lambda target - Function, Predicate, Consumer, Supplier"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**
1. Exactly one abstract method (SAM) - default/static methods don't count
2. Four pillars: Function, Predicate, Consumer, Supplier
3. `@FunctionalInterface` is optional but prevents accidental breaking

**Interview one-liner:**
"A functional interface has exactly one abstract method, serving as the target type for lambda expressions, with `java.util.function` providing 43 standard interfaces covering the four archetypes: transform, test, consume, and produce."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

`Comparator<T>` has two abstract methods: `compare(T, T)` and `equals(Object)`. Yet it is a valid `@FunctionalInterface`. Why? Because `equals` is inherited from `Object` and is excluded from the SAM count. Any abstract method that overrides a public `Object` method does not count toward the single-abstract-method requirement.
---

### ⚖️ Comparison Table

| Interface | Signature | Use Case | Example |
|-----------|-----------|----------|--------|
| `Function<T,R>` | `T -> R` | Transform | `String::length` |
| `Predicate<T>` | `T -> boolean` | Filter | `String::isEmpty` |
| `Consumer<T>` | `T -> void` | Side effect | `System.out::println` |
| `Supplier<T>` | `() -> T` | Factory | `ArrayList::new` |
| `UnaryOperator<T>` | `T -> T` | Same-type transform | `String::trim` |
| `BiFunction<T,U,R>` | `(T,U) -> R` | Two-arg transform | `String::concat` |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | @FunctionalInterface is required for lambda use | The annotation is optional - any interface with one abstract method works with lambdas. `@FunctionalInterface` just adds compile-time validation. |
| 2 | Functional interfaces can only have one method | They have one *abstract* method. They can have multiple `default` methods, `static` methods, and methods inherited from `Object` (`equals`, `hashCode`, `toString`). |
| 3 | You should always create custom functional interfaces | Java provides 43 built-in functional interfaces in `java.util.function`. Custom ones are only needed when none fit or when the name adds domain clarity. |
| 4 | BiFunction covers all two-argument cases | `BiFunction<T,U,R>` only handles two inputs. For more arguments, create a custom interface or use currying: `Function<A, Function<B, Function<C, R>>>`. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Ambiguous lambda target type**
**Symptom:** Compile error: "reference to method is ambiguous" when passing a lambda.
**Root Cause:** Multiple overloaded methods accept different functional interfaces that are compatible with the same lambda.
**Diagnostic:**

```
javac MyClass.java 2>&1 | grep "ambiguous"
# Shows which methods conflict
```

**Fix:**
```java
// BAD: ambiguous overload
void process(Function<String, Integer> f) {}
void process(ToIntFunction<String> f) {}
process(s -> s.length()); // ambiguous!

// GOOD: cast to resolve
process((Function<String, Integer>) s -> s.length());
// Or: remove overload ambiguity
```
**Prevention:** Avoid overloading methods with different functional interface types that have compatible signatures.

**Failure Mode 2: Missing @FunctionalInterface on API interface**
**Symptom:** Someone adds a second abstract method to your interface, breaking all lambda call sites.
**Root Cause:** Without `@FunctionalInterface`, the compiler doesn't enforce the single-abstract-method rule.
**Diagnostic:**

```
javap MyInterface.class | grep "abstract"
# Count abstract methods - must be exactly 1
```

**Fix:**
```java
// BAD: no annotation protection
interface Converter<T, R> {
    R convert(T input);
    // Someone adds: R convertAll(List<T> inputs);
    // All lambdas now fail to compile!
}

// GOOD: annotated
@FunctionalInterface
interface Converter<T, R> {
    R convert(T input);
}
```
**Prevention:** Always annotate functional interfaces with `@FunctionalInterface`.

**Failure Mode 3: Checked exception incompatibility**
**Symptom:** Cannot use lambda with `Function<T,R>` when the operation throws a checked exception.
**Root Cause:** `Function.apply()` does not declare any checked exceptions. The lambda cannot throw one.
**Diagnostic:**

```
javac MyClass.java 2>&1 | grep "unreported exception"
```

**Fix:**
```java
// BAD: Function can't throw IOException
Function<Path, String> reader =
    p -> Files.readString(p); // won't compile!

// GOOD: custom functional interface
@FunctionalInterface
interface ThrowingFunction<T, R> {
    R apply(T t) throws Exception;
}
```
**Prevention:** Create `ThrowingFunction`/`ThrowingConsumer` wrappers for exception-prone functional code.
---

### 🎯 Interview Deep-Dive

**Q1: Name the four core functional interfaces in java.util.function and explain when you would create a custom one instead.**

*Why they ask:* Tests practical knowledge of the standard library.

*Strong answer:*

The four core archetypes:
1. `Function<T,R>` - takes T, returns R: `T -> R`. Use for transformation.
2. `Predicate<T>` - takes T, returns boolean: `T -> boolean`. Use for filtering.
3. `Consumer<T>` - takes T, returns void: `T -> void`. Use for side effects.
4. `Supplier<T>` - takes nothing, returns T: `() -> T`. Use for lazy creation.

Create a custom functional interface when:
- The name communicates domain intent better than the generic name (e.g., `RetryPolicy` vs `Function<Integer,Duration>`)
- You need to throw checked exceptions (standard interfaces don't)
- You want to add useful default methods for composition
- The interface is part of your public API and you want stronger typing

```java
@FunctionalInterface
interface EventHandler<E extends Event> {
    void handle(E event) throws EventException;

    default EventHandler<E> andThen(
            EventHandler<E> next) {
        return event -> {
            this.handle(event);
            next.handle(event);
        };
    }
}
```

---

**Q2: How does `@FunctionalInterface` work at compile time? What happens if you violate the contract?**

*Why they ask:* Tests understanding of annotation processing.

*Strong answer:*

`@FunctionalInterface` is a compile-time marker annotation (retention = RUNTIME, but its primary use is compile-time). The compiler checks:

1. The annotated type must be an interface (not a class or enum)
2. The interface must have exactly one abstract method
3. Methods overriding `Object` public methods (`equals`, `hashCode`, `toString`) don't count

Violations produce compile errors:
```java
@FunctionalInterface
interface Bad {
    void method1();
    void method2(); // ERROR: not functional
}

@FunctionalInterface
class NotInterface { // ERROR: not an interface
    void method();
}
```

Without the annotation, an interface with one abstract method is still a valid lambda target. The annotation is documentation + protection against accidental changes:

```java
// Without annotation: works as lambda target
// but someone might add a second method later
interface Fragile {
    void process();
}

// With annotation: compiler prevents adding
// a second abstract method
@FunctionalInterface
interface Safe {
    void process();
}
```

---

**Q3: Explain the difference between `Function.compose` and `Function.andThen` with examples.**

*Why they ask:* Tests understanding of function composition order.

*Strong answer:*

Both chain two functions together but in different order:

- `f.andThen(g)` = apply f first, then g: `g(f(x))`
- `f.compose(g)` = apply g first, then f: `f(g(x))`

```java
Function<String, String> trim =
    String::trim;
Function<String, String> upper =
    String::toUpperCase;

// andThen: trim first, then uppercase
Function<String, String> pipeline1 =
    trim.andThen(upper);
pipeline1.apply("  hello  ");
// trim -> "hello" -> upper -> "HELLO"

// compose: uppercase first, then trim
Function<String, String> pipeline2 =
    trim.compose(upper);
pipeline2.apply("  hello  ");
// upper -> "  HELLO  " -> trim -> "HELLO"
```

`andThen` reads left-to-right (natural pipeline order) and is generally preferred. `compose` reads right-to-left (mathematical function composition notation).

`Predicate` has `and()`, `or()`, and `negate()` for boolean composition:
```java
Predicate<String> valid = notNull
    .and(notEmpty)
    .and(maxLength(100));
```

`Consumer` has `andThen()` for chaining side effects:
```java
Consumer<User> process = validate
    .andThen(save)
    .andThen(notify);
```
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Interfaces and abstract classes - functional interfaces extend the interface concept
- Generics - core functional interfaces are generic (`Function<T,R>`)

**Builds on this (learn these next):**

- Lambda Expressions - the primary syntax for implementing functional interfaces
- Composition methods - `andThen()`, `compose()`, `and()`, `or()`, `negate()`

**Alternatives / Comparisons:**

- Strategy pattern with classes - when you need state or multiple methods
- Kotlin SAM conversions - automatic functional interface adaptation


---

---

# Method References

**TL;DR** - Method references are shorthand lambdas that point directly to an existing method, making code more readable when the lambda simply delegates to a named method.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Even with lambdas, you often write `x -> someMethod(x)` - a lambda whose only job is to call an existing method. This is one level of indirection that adds noise. When every stream operation wraps a named method in a lambda, the code obscures rather than reveals intent.

**THE BREAKING POINT:**
`.map(x -> x.toString())`, `.filter(x -> isValid(x))`, `.forEach(x -> process(x))` - these lambdas add no logic. They are pure delegation with extra syntax.

**THE INVENTION MOMENT:**
"This is exactly why method references were created."

**EVOLUTION:**
Anonymous classes (Java 1.1) -> lambda expressions (Java 8) -> method references (Java 8, same release). Method references are not a separate feature - they are a syntactic shorthand for lambdas that delegate to a single method.
---

### 📘 Textbook Definition

A method reference is a compact syntax for a lambda expression that calls an existing method. The `::` operator separates the target (class or instance) from the method name. There are four kinds: static method references, bound instance method references, unbound instance method references, and constructor references.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
Method references replace `x -> method(x)` with `Class::method` for cleaner code.

**One analogy:**

> If a lambda is a handwritten note saying "call this method," a method reference is a direct phone number. Both reach the same person, but the phone number is shorter and less error-prone.

**One insight:**
Method references are preferred over lambdas when the lambda simply delegates to a single method without additional logic. They communicate intent more clearly: `Employee::getName` says "extract the name" while `e -> e.getName()` says "given e, call getName on e" - same result, but the method reference is more declarative.
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A method reference targets an existing named method
2. The referenced method's signature must be compatible with the target functional interface
3. Method references are compiled identically to equivalent lambdas (same `invokedynamic` mechanism)

**DERIVED DESIGN:**
Four kinds exist because methods can be static or instance, and instance methods can be bound (specific object) or unbound (any object of the type). Constructor references (`ClassName::new`) treat constructors as factory methods.

**THE TRADE-OFFS:**
**Gain:** More concise, more readable, communicates intent (what method, not how to call it)
**Cost:** Four kinds can be confusing initially, especially unbound instance references

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Referencing existing methods by name is natural in any language with first-class functions.
**Accidental:** The four-kind taxonomy exists because Java distinguishes static from instance methods and has no unified function type.
---

### 🧠 Mental Model / Analogy

> A lambda is like giving someone verbal directions: "Go to the store, find the milk, pick it up." A method reference is like saying: "Go to Store::getMilk." Same destination, fewer words.

- "Verbal directions" -> lambda expression
- "Named destination" -> method reference
- "::" -> the "at" symbol connecting target to method

Where this analogy breaks down: Method references can be unbound (not attached to a specific store), which directions cannot be.
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of writing a mini-function that just calls another function, you point directly to the function you want to call using `::`.

**Level 2 - How to use it (junior developer):**

```java
// Instead of: x -> System.out.println(x)
Consumer<String> print =
    System.out::println;

// Instead of: s -> Integer.parseInt(s)
Function<String, Integer> parse =
    Integer::parseInt;

// Instead of: s -> s.toUpperCase()
Function<String, String> upper =
    String::toUpperCase;

// Instead of: () -> new ArrayList<>()
Supplier<List<String>> factory =
    ArrayList::new;
```

**Level 3 - How it works (mid-level engineer):**

The four kinds, with lambda equivalents:

| Kind | Syntax | Lambda Equivalent |
|------|--------|-------------------|
| Static | `Class::static` | `(args) -> Class.static(args)` |
| Bound instance | `obj::method` | `(args) -> obj.method(args)` |
| Unbound instance | `Class::method` | `(obj, args) -> obj.method(args)` |
| Constructor | `Class::new` | `(args) -> new Class(args)` |

The tricky part is unbound instance references. `String::toLowerCase` as a `Function<String, String>` means "given any String, call its toLowerCase method." The first parameter becomes the receiver:

```java
// Unbound: first arg becomes 'this'
BiFunction<String, String, Boolean> eq =
    String::equalsIgnoreCase;
// Equivalent: (a, b) -> a.equalsIgnoreCase(b)
```

**Level 4 - Why it was designed this way (senior/staff+):**

Method references are compiled to the exact same `invokedynamic` bytecode as their equivalent lambdas. There is zero performance difference. The value is purely readability and intent communication.

The unbound instance reference is the most powerful kind: it enables point-free programming in Java. `stream.map(String::trim).map(String::toLowerCase)` reads as a sequence of transformations without any mention of variables. This style is common in functional languages and is one of the key readability improvements Java 8 brought.


**Level 5 - Distinguished (expert thinking):**
Method references are syntactic shorthand for lambdas that simply delegate to an existing method. The same concept exists in C# (method groups), Kotlin (callable references `::method`), and Python (first-class functions). The expert insight: method references are not just shorter - they often produce more efficient bytecode because the JVM can directly bind the call site to the target method via `invokedynamic`, skipping the lambda proxy entirely. There are four kinds: static (`Integer::parseInt`), bound instance (`myStr::toLowerCase`), unbound instance (`String::length`), and constructor (`ArrayList::new`). At extreme scale, method references compose better than lambdas for pipeline readability: `.map(String::trim).filter(Predicate.not(String::isEmpty))` reads like a specification. If redesigning today, you would fix the limitation that method references cannot express partial application (`Integer::compare` cannot be partially applied to fix one argument).

**Expert thinking cues:**
- "Which of the 4 forms is this?" - static, bound instance, unbound instance, or constructor
- "Does this lambda just call a single method?" - if yes, replace with method reference for clarity
- "Is the method overloaded?" - overloaded methods can cause ambiguous method reference errors at compile time
---

### How It Works (Mechanism)

```
  employees.stream()
    .map(Employee::getName)
       |
  Compiler resolves Employee::getName
  to instance method getName() on Employee
       |
  Target type: Function<Employee, String>
  SAM: String apply(Employee e)
       |
  Desugared to lambda:
  (Employee e) -> e.getName()
       |
  invokedynamic + LambdaMetafactory
  (identical to lambda compilation)
```
---

### The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
  Source: Employee::getName
       |
  <- YOU ARE HERE
       |
  Compiler infers target type
  from context (map expects Function)
       |
  Validates signature compatibility
  getName(): String matches
  Function<Employee, String>
       |
  Compiles to invokedynamic
  (same as equivalent lambda)
```

**FAILURE PATH:**
- Ambiguous method reference (overloaded methods): compile error
- Wrong number of parameters: compile error ("incompatible types")
- Referencing a non-existent method: compile error

**WHAT CHANGES AT SCALE:**
Method references are preferred in codebases with style guides that emphasize readability. In complex pipelines, mixing method references and lambdas strategically improves clarity: use method references for simple delegation, lambdas for inline logic.

---

### 💻 Code Example

**BAD - Unnecessary lambdas wrapping method calls:**

```java
list.stream()
    .filter(s -> Objects.nonNull(s))
    .map(s -> s.trim())
    .map(s -> s.toLowerCase())
    .forEach(s -> System.out.println(s));
```

**GOOD - Method references for cleaner code:**

```java
list.stream()
    .filter(Objects::nonNull)
    .map(String::trim)
    .map(String::toLowerCase)
    .forEach(System.out::println);
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** Shorthand for a lambda that delegates to an existing method (`Class::method`)
**PROBLEM IT SOLVES:** Eliminates trivial pass-through lambdas that just call one method
**KEY INSIGHT:** Four kinds: static, bound instance, unbound instance, and constructor references
**USE WHEN:** Lambda body is a single method call with matching parameters
**AVOID WHEN:** Need to transform arguments, add logic, or the method is overloaded (ambiguity)
**ANTI-PATTERN:** Writing `x -> x.toString()` instead of `Object::toString` - less readable, less optimizable
**TRADE-OFF:** Readability and potential JVM optimization vs less explicit about parameter flow
**ONE-LINER:** "Point to the method, skip the lambda - `Class::method` replaces `x -> Class.method(x)`"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**
1. Four kinds: static, bound instance, unbound instance, constructor
2. Same bytecode as equivalent lambda - zero performance difference
3. Use when lambda simply delegates to an existing method

**Interview one-liner:**
"Method references are shorthand lambdas using `::` that point to existing methods, compiled identically via invokedynamic, preferred when a lambda's only job is delegating to a named method."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Constructor references can target array constructors: `int[]::new` is a valid `IntFunction<int[]>`. This is used internally by `stream.toArray(int[]::new)` to create arrays of the right size without reflection. The compiler translates `int[]::new` to `(size) -> new int[size]`.
---

### ⚖️ Comparison Table

| Kind | Syntax | Lambda Equivalent | Example |
|------|--------|-------------------|--------|
| Static | `Class::staticMethod` | `x -> Class.staticMethod(x)` | `Integer::parseInt` |
| Bound instance | `obj::method` | `() -> obj.method()` | `str::length` |
| Unbound instance | `Class::method` | `x -> x.method()` | `String::toLowerCase` |
| Constructor | `Class::new` | `() -> new Class()` | `ArrayList::new` |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Method references are always clearer than lambdas | For complex scenarios like overloaded methods or when parameter mapping is non-obvious, a lambda with named parameters is clearer. Use method references for simple delegations. |
| 2 | Method references create new objects each time | Like non-capturing lambdas, method references to static methods are typically cached as singletons by the JVM. |
| 3 | `obj::method` and `Class::method` are the same | Bound (`obj::method`) captures the specific instance. Unbound (`Class::method`) takes the instance as the first parameter. Different signatures and behaviors. |
| 4 | Constructor references only work with no-arg constructors | Constructor references adapt to the functional interface's parameter list. `Function<String, Integer>` matches `Integer::new` (the `Integer(String)` constructor). |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Ambiguous method reference for overloaded methods**
**Symptom:** Compile error: "reference to method is ambiguous" when using `ClassName::methodName`.
**Root Cause:** The referenced method is overloaded and the compiler cannot determine which overload matches the functional interface.
**Diagnostic:**

```
javac MyClass.java 2>&1 | grep "ambiguous"
```

**Fix:**
```java
// BAD: String.valueOf is overloaded (Object, char[], int, ...)
list.stream().map(String::valueOf); // ambiguous!

// GOOD: use explicit lambda
list.stream().map(x -> String.valueOf(x));
// Or cast: map((Function<Object,String>) String::valueOf)
```
**Prevention:** Fall back to explicit lambdas for overloaded methods. Avoid overloading API methods intended for method references.

**Failure Mode 2: Capturing stale reference in bound method reference**
**Symptom:** Method reference uses old object state because it was bound at creation time.
**Root Cause:** Bound method reference (`obj::method`) captures the object reference at binding time. If `obj` is reassigned, the reference still points to the old object.
**Diagnostic:**

```
# Check if the object variable is reassigned
# after the method reference is created
grep -n '::' MyClass.java
```

**Fix:**
```java
// BAD: stale binding
Formatter fmt = new Formatter("v1");
Function<String, String> f = fmt::format;
fmt = new Formatter("v2");
f.apply("x"); // still uses v1 Formatter!

// GOOD: use lambda for late binding
Function<String, String> f =
    x -> currentFormatter.format(x);
```
**Prevention:** Use lambdas instead of bound method references when the target object may change.

**Failure Mode 3: NullPointerException from null receiver**
**Symptom:** NPE when calling a bound method reference where the captured instance is null.
**Root Cause:** `null::method` is captured; NPE occurs at invocation time, not binding time.
**Diagnostic:**

```
# Check for nullable variables used in ::
grep -n '::' MyClass.java
# Verify the variable is non-null at binding point
```

**Fix:**
```java
// BAD: potentially null receiver
String s = map.get("key"); // might be null
Function<Integer, String> f = s::substring;
f.apply(0); // NPE!

// GOOD: null-check first
Function<Integer, String> f =
    Optional.ofNullable(map.get("key"))
        .map(str -> (Function<Integer, String>)
            str::substring)
        .orElse(i -> "default");
```
**Prevention:** Never create bound method references from nullable variables. Null-check first.
---

### 🎯 Interview Deep-Dive

**Q1: Explain the four types of method references with examples. Which one is most commonly misunderstood?**

*Why they ask:* Tests complete understanding of all method reference types.

*Strong answer:*

1. **Static:** `Integer::parseInt` - calls a static method. Lambda: `s -> Integer.parseInt(s)`.

2. **Bound instance:** `System.out::println` - calls a method on a specific object. Lambda: `x -> System.out.println(x)`. The object (`System.out`) is captured at the time the reference is created.

3. **Unbound instance:** `String::length` - calls a method on whatever object is passed as the first argument. Lambda: `s -> s.length()`. The first parameter becomes the receiver.

4. **Constructor:** `ArrayList::new` - invokes a constructor. Lambda: `() -> new ArrayList<>()` or `(capacity) -> new ArrayList<>(capacity)` depending on context.

The most misunderstood is **unbound instance references**, especially with two-parameter methods:

```java
// String::compareToIgnoreCase as Comparator
// This works because Comparator.compare(T, T)
// maps to: (a, b) -> a.compareToIgnoreCase(b)
// First arg becomes 'this', second becomes
// the method parameter

TreeSet<String> set = new TreeSet<>(
    String::compareToIgnoreCase);
```

The confusion arises because the same method reference can be both:
- `Function<String, String>` when used as unbound: `String::toUpperCase`
- Bound to a specific instance: `"hello"::toUpperCase` (becomes `Supplier<String>`)

---

**Q2: When should you prefer a lambda over a method reference?**

*Why they ask:* Tests judgment about code readability.

*Strong answer:*

Prefer lambdas when:

1. **Additional logic is needed:** `x -> x.getName().toUpperCase()` cannot be a single method reference.

2. **Method reference is ambiguous:** When a class has overloaded methods, the method reference may be unclear to the reader.

3. **The lambda is more readable:** Sometimes explicit parameters improve understanding:
   ```java
   // Unclear what the arguments mean
   map.merge(key, 1, Integer::sum);
   // Clearer with lambda
   map.merge(key, 1,
       (existing, newVal) -> existing + newVal);
   ```

4. **Casting is required for disambiguation:**
   ```java
   // Ambiguous - which overload?
   // stream.map(String::valueOf)
   // Clearer with lambda:
   stream.map(x -> String.valueOf(x));
   ```

The general rule: if the method reference reads naturally (like `Employee::getName`, `Objects::nonNull`), use it. If you have to pause to understand what it does, use a lambda.
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Lambda Expressions - method references are shorthand for lambdas
- Functional Interfaces - method references must match a functional interface

**Builds on this (learn these next):**

- Streams API - method references make stream pipelines more readable
- Constructor references - `Class::new` for factory patterns

**Alternatives / Comparisons:**

- Explicit lambdas - when parameter transformation is needed
- Reflection (`Method.invoke`) - when method is determined at runtime


---

---

# Default Methods

**TL;DR** - Default methods let interfaces provide implementation, solving the interface evolution problem by adding new methods without breaking existing implementations.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Java 8, adding a method to an interface broke every class implementing it. The `Collection` interface needed a `stream()` method, but adding it would force every custom collection implementation (thousands of third-party libraries) to implement `stream()` or fail to compile. Interfaces were frozen the moment they were published.

**THE BREAKING POINT:**
Java 8 needed to add `stream()`, `forEach()`, `spliterator()`, and `removeIf()` to the `Collection` interface. Without default methods, this would have been impossible without breaking backward compatibility for the entire Java ecosystem.

**THE INVENTION MOMENT:**
"This is exactly why default methods were created."

**EVOLUTION:**
Interfaces with only abstract methods (pre-Java 8) -> default methods for interface evolution (Java 8) -> private methods in interfaces for code reuse within defaults (Java 9).
---

### 📘 Textbook Definition

A default method is a method in an interface that has a body, declared with the `default` keyword. It provides a default implementation that classes inheriting the interface can use without overriding. Classes can always override default methods to provide specialized behavior.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
Default methods add behavior to interfaces without breaking existing implementations.

**One analogy:**

> Default methods are like a new menu item at a restaurant franchise. The headquarters (interface) adds "veggie burger" with a standard recipe (default implementation). Individual restaurants (implementing classes) can use the standard recipe or create their own version. No restaurant is forced to close for renovation.

**One insight:**
Default methods were created for library evolution, not multiple inheritance of behavior. They enable API designers to add methods to interfaces after publication. The fact that they also enable a form of multiple inheritance is a secondary effect, not the primary purpose.
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Default methods have a body, declared with the `default` keyword
2. Classes can override default methods
3. If a class inherits conflicting default methods from two interfaces, it must explicitly resolve the conflict

**DERIVED DESIGN:**
The conflict resolution rules follow a clear precedence: (1) class always wins over interface, (2) more specific interface wins over less specific, (3) if ambiguous, the class must override and choose explicitly.

**THE TRADE-OFFS:**
**Gain:** Interface evolution without breaking changes, optional method implementations, shared behavior across unrelated classes
**Cost:** Diamond problem complexity, can blur the line between interfaces and abstract classes, harder to reason about behavior origin

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Library evolution requires some mechanism to add methods to published contracts.
**Accidental:** The diamond problem resolution rules are complex because Java chose to allow default methods from multiple interfaces rather than restricting to single inheritance of defaults.
---

### 🧠 Mental Model / Analogy

> Think of an interface as a contract, and default methods as suggested clauses. "You must implement deposit() and withdraw() (abstract methods). If you don't specify how to calculate interest, here's a standard formula (default method). You can always write your own formula."

- "Must implement" -> abstract methods
- "Here's a standard formula" -> default method
- "Write your own" -> override the default

Where this analogy breaks down: In real contracts, conflicting clauses void the contract. In Java, the compiler forces you to explicitly choose which default to use.
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Default methods let interfaces include pre-written methods so that classes don't have to write them if the default behavior is fine.

**Level 2 - How to use it (junior developer):**

```java
interface Greeter {
    String name();

    // Default method - optional to override
    default String greet() {
        return "Hello, " + name() + "!";
    }
}

class SimpleGreeter implements Greeter {
    public String name() { return "World"; }
    // greet() inherited from interface
}

class FormalGreeter implements Greeter {
    public String name() { return "Sir"; }

    @Override
    public String greet() {
        return "Good day, " + name() + ".";
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Default methods are compiled as regular methods in the interface's `.class` file. The JVM's method resolution order determines which implementation to invoke:

1. Look for the method in the class itself
2. Look in the class's superclass chain
3. Look in the implemented interfaces (most specific wins)

Java 9 added private methods in interfaces, enabling default methods to share helper logic:

```java
interface Logging {
    default void logInfo(String msg) {
        log("INFO", msg);
    }
    default void logError(String msg) {
        log("ERROR", msg);
    }
    // Java 9: private helper method
    private void log(String level, String msg) {
        System.out.printf("[%s] %s%n",
            level, msg);
    }
}
```

**Level 4 - Why it was designed this way (senior/staff+):**

Default methods are the pragmatic solution to the "interface evolution problem." The alternatives were: (1) never add methods to interfaces (too restrictive), (2) break backward compatibility (unacceptable for Java), (3) add extension methods like C# (considered but rejected as too complex). Default methods were the minimum viable feature that solved the core problem.

The key design constraint: default methods must be expressible purely in terms of the interface's other methods. They cannot access instance state (no fields in interfaces). This keeps them fundamentally different from abstract class methods and prevents them from becoming a back door to multiple state inheritance.


**Level 5 - Distinguished (expert thinking):**
Default methods solved Java's interface evolution problem - the same problem addressed by extension methods in C#, traits in Rust/Scala, and protocol extensions in Swift. The expert insight: default methods enabled the entire Streams API to be added to `Collection` (via `stream()`, `parallelStream()`, `forEach()`) without breaking the millions of existing `Collection` implementations. This is the 'expression problem' solution for Java: adding new operations to existing types without modifying them. At extreme scale, default methods create the diamond problem when a class implements two interfaces with the same default method signature - Java resolves this by requiring the class to override and explicitly choose. If redesigning today, you might prefer Kotlin-style interface delegation or Rust traits with explicit impl blocks to avoid the ambiguity entirely.

**Expert thinking cues:**
- "Is this behavior or contract?" - default methods should provide convenience behavior, not core contract
- "Could two interfaces conflict?" - check for diamond inheritance and override explicitly
- "Should this be an abstract class instead?" - if you need state (fields), yes. Default methods cannot access instance state.
---

### How It Works (Mechanism)

```
  interface Collection<E> {
      default Stream<E> stream() {
          return StreamSupport.stream(
              spliterator(), false);
      }
  }
       |
  MyList implements Collection<E>
  (does not override stream())
       |
  myList.stream() called
       |
  JVM checks: MyList.stream()? NO
  JVM checks: superclass? NO
  JVM checks: Collection.stream()? YES
       |
  Invokes default implementation
```
---

### The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
  Interface publishes default method
       |
  <- YOU ARE HERE
       |
  Existing classes inherit default
  without recompilation
       |
  New classes can override if needed
       |
  Method resolution at runtime
  checks class -> superclass -> interface
```

**FAILURE PATH:**
- Two unrelated interfaces with same default method: compile error in implementing class (must override)
- Default method calls abstract method that implementation forgot to implement: `AbstractMethodError` at runtime (rare, usually caught at compile time)
- Assumption that default method has access to implementation state: it does not - interfaces have no instance fields

**WHAT CHANGES AT SCALE:**
In large codebases, default methods can create "action at a distance" bugs. A library updates an interface with a new default method. Your class inherits it silently. If the default behavior doesn't match your class's invariants, you have a bug that no compiler warning catches. This is why `@implSpec` Javadoc tag exists: document what assumptions a default method makes.

---

### 💻 Code Example

**GOOD - Interface evolution without breaking changes:**

```java
// Java 7: original interface
interface Sortable<T> {
    int compareTo(T other);
}

// Java 8+: add default without breaking
interface Sortable<T> {
    int compareTo(T other);

    default boolean isGreaterThan(T other) {
        return compareTo(other) > 0;
    }

    default boolean isLessThan(T other) {
        return compareTo(other) < 0;
    }
}
// All existing Sortable implementations
// gain isGreaterThan/isLessThan for free
```

**GOOD - Diamond problem resolution:**

```java
interface A {
    default void hello() {
        System.out.println("A");
    }
}
interface B extends A {
    default void hello() {
        System.out.println("B");
    }
}
// B is more specific than A -> B wins
class C implements A, B {
    // hello() resolves to B automatically
}

interface D {
    default void hello() {
        System.out.println("D");
    }
}
// A and D are unrelated -> must resolve
class E implements A, D {
    @Override
    public void hello() {
        A.super.hello(); // explicit choice
    }
}
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** Interface method with a body - provides default implementation that classes can override
**PROBLEM IT SOLVES:** Evolve interfaces without breaking all existing implementations
**KEY INSIGHT:** Enabled the entire Streams API to be added to `Collection` without breaking existing code
**USE WHEN:** Adding new methods to published interfaces, providing convenience overloads
**AVOID WHEN:** Method requires instance state (fields) - use abstract class instead
**ANTI-PATTERN:** Using default methods to simulate multiple inheritance of state - interfaces have no fields
**TRADE-OFF:** Interface evolution without breakage vs diamond problem and blurred abstract class boundary
**ONE-LINER:** "Interface evolution - add methods to interfaces without breaking implementations"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**
1. Default methods solve interface evolution - add methods without breaking implementors
2. Resolution: class wins > sub-interface wins > must resolve conflicts explicitly
3. Interfaces still have no instance fields - defaults cannot access implementation state

**Interview one-liner:**
"Default methods allow interfaces to provide implementations, enabling API evolution without breaking existing classes, with conflict resolution following class-over-interface precedence."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Default methods can be called explicitly using `InterfaceName.super.methodName()` syntax, but only from a class that directly implements that interface. This means a class can implement two interfaces with conflicting defaults and use both implementations within its override method - composing behavior from multiple sources in a controlled way.
---

### ⚖️ Comparison Table

| Aspect | Default Method | Abstract Method | Static Method |
|--------|---------------|----------------|--------------|
| Has body | Yes | No | Yes |
| Override | Optional | Required | Cannot |
| Access instance | Via `this` | N/A | No |
| Inheritance | Diamond possible | Single abstract | No inheritance |
| Purpose | Evolution/convenience | Contract | Utility |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Default methods make interfaces same as abstract classes | Interfaces still cannot have instance fields, constructors, or non-public methods (until Java 9 private methods). Abstract classes support all of these. |
| 2 | Default methods always win over superclass methods | Class methods always win over default methods ("class wins" rule). A class's concrete or abstract method takes precedence over any interface default. |
| 3 | Diamond inheritance is always a compile error | Java only errors if the class doesn't override the conflicting default method. The class can resolve by overriding and calling `InterfaceName.super.method()`. |
| 4 | Default methods should contain complex logic | Default methods should provide simple convenience implementations. Complex logic belongs in abstract classes or helper classes where state management and testing are simpler. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Diamond inheritance conflict**
**Symptom:** Compile error: "class inherits unrelated defaults for method() from types InterfaceA and InterfaceB."
**Root Cause:** Class implements two interfaces that both define the same default method with different implementations.
**Diagnostic:**

```
javac MyClass.java 2>&1 | grep "inherits unrelated"
```

**Fix:**
```java
// BAD: diamond conflict
interface A { default void log() { /*...*/ } }
interface B { default void log() { /*...*/ } }
class C implements A, B {} // won't compile!

// GOOD: override and resolve
class C implements A, B {
    @Override
    public void log() {
        A.super.log(); // explicit choice
    }
}
```
**Prevention:** When implementing multiple interfaces, check for default method conflicts. Override and delegate explicitly.

**Failure Mode 2: Default method silently overridden by superclass**
**Symptom:** Default method implementation is not called; superclass method runs instead.
**Root Cause:** Java's "class wins" rule - a concrete method in any superclass takes precedence over any interface default.
**Diagnostic:**

```
# Check class hierarchy for same method name
javap -p MySuperclass.class | grep methodName
```

**Fix:**
```java
// Superclass has: void sort() { /* old impl */ }
// Interface has: default void sort() { /* new */ }
// Class extends Super implements Interface
// Super.sort() wins silently!

// GOOD: override explicitly if interface default is wanted
@Override
public void sort() {
    MyInterface.super.sort(); // use interface version
}
```
**Prevention:** When adding default methods, audit implementors' class hierarchies for conflicting methods.

**Failure Mode 3: Accidental functional interface breakage**
**Symptom:** Adding a default method to an interface works, but adding an abstract method breaks all lambda call sites.
**Root Cause:** Developers confuse default methods (safe to add) with abstract methods (break existing implementations and lambdas).
**Diagnostic:**

```
javac ConsumerCode.java 2>&1 | grep "abstract"
# Shows "is not a functional interface" errors
```

**Fix:**
```java
// BAD: adding abstract method to functional interface
@FunctionalInterface
interface Handler<T> {
    void handle(T t);
    String describe(); // breaks all lambdas!
}

// GOOD: add as default
@FunctionalInterface
interface Handler<T> {
    void handle(T t);
    default String describe() { return "handler"; }
}
```
**Prevention:** Adding methods to published interfaces: always use `default`. Never add abstract methods to `@FunctionalInterface`.
---

### 🎯 Interview Deep-Dive

**Q1: How does the JVM resolve default method conflicts? Walk through the resolution algorithm.**

*Why they ask:* Tests understanding of the diamond problem in Java.

*Strong answer:*

The resolution follows three rules in order:

1. **Class always wins:** If a class or its superclass defines the method (even if abstract), that takes precedence over any interface default.

2. **Most specific sub-interface wins:** If `B extends A` and both define the same default method, `B`'s version wins because it is more specific.

3. **Explicit resolution required:** If two unrelated interfaces define the same default method and a class implements both, the class must override the method and explicitly choose.

```java
interface A {
    default String hello() { return "A"; }
}
interface B extends A {
    default String hello() { return "B"; }
}
interface C {
    default String hello() { return "C"; }
}

class D implements B, C {
    // Rule 2: B is more specific than A
    // But B and C are unrelated -> Rule 3
    // MUST override:
    @Override
    public String hello() {
        return B.super.hello(); // "B"
    }
}

class E extends D implements A {
    // Rule 1: D.hello() exists -> class wins
    // Inherits D's override of hello()
}
```

The `super` syntax `InterfaceName.super.method()` is the only way to call a specific interface's default from an overriding method. This is Java's controlled solution to the diamond problem.

---

**Q2: What is the difference between default methods in interfaces and methods in abstract classes? When would you choose one over the other?**

*Why they ask:* Tests architectural judgment.

*Strong answer:*

| Feature | Default Method | Abstract Class |
|---------|---------------|----------------|
| State | No instance fields | Instance fields |
| Constructor | None | Yes |
| Access modifiers | Public only (+ private in Java 9) | All modifiers |
| Inheritance | Multiple interfaces | Single class |
| `this` | Refers to implementing class | Refers to the class |

**Choose interface with defaults when:**
- Multiple unrelated classes need the behavior
- The behavior can be expressed without instance state
- You want to add behavior to an existing API without breaking changes
- Classes already extend another class

**Choose abstract class when:**
- You need shared mutable state (fields)
- You need constructors for initialization
- You need non-public methods (protected, package-private)
- The implementations share a fundamental "is-a" relationship

```java
// Interface: behavior without state
interface Cacheable {
    String getCacheKey();
    default Duration getTTL() {
        return Duration.ofMinutes(5);
    }
}

// Abstract class: shared state + template
abstract class AbstractRepository<T> {
    protected final DataSource ds;
    protected AbstractRepository(DataSource ds) {
        this.ds = ds;
    }
    protected abstract String tableName();
    public List<T> findAll() {
        return query("SELECT * FROM "
            + tableName());
    }
}
```

The general guidance: prefer interfaces with default methods for mix-in behavior, abstract classes for shared state and template patterns.
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Interfaces - default methods extend the traditional interface concept
- Inheritance and polymorphism - understanding method resolution order

**Builds on this (learn these next):**

- Interface evolution patterns - adding methods to published APIs
- Private interface methods (Java 9) - extracting common default method logic

**Alternatives / Comparisons:**

- Abstract classes - when you need fields, constructors, or complex state
- Kotlin extension functions - adding methods without modifying the type
