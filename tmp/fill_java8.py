#!/usr/bin/env python3
"""Fill [TODO] sections for Java - Java 8 Features.md (6 keywords)."""
import re

FILE = "interview/java/Java - Java 8 Features.md"

KEYWORDS = [
    "Lambda Expressions", "Streams API", "Optional",
    "Functional Interfaces", "Method References",
    "Default Methods",
]

LEVEL5 = {
    "Lambda Expressions": (
        "Lambda expressions are Java's implementation of closures - "
        "the same concept as JavaScript arrow functions, Python "
        "lambdas, C# delegates, and Rust closures. The expert "
        "insight is that lambdas are not syntactic sugar for "
        "anonymous inner classes: they compile to `invokedynamic` "
        "bytecode, which defers the implementation strategy to the "
        "JVM. The JVM can then choose to generate a class at "
        "runtime, reuse a singleton for non-capturing lambdas, or "
        "even inline the function body entirely. This is why "
        "lambdas are generally faster than anonymous classes - no "
        "`.class` file, no constructor, potentially no allocation. "
        "At extreme scale, lambda capture semantics matter: "
        "capturing a large object keeps the entire object alive "
        "(GC retention), while capturing a mutable variable "
        "requires boxing (performance penalty). If redesigning "
        "today, you would add syntax for multi-line lambdas with "
        "early return (currently `return` exits the lambda, not "
        "the enclosing method) and support for checked exceptions "
        "in functional interfaces.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this lambda capturing state?\" - non-capturing "
        "lambdas are singletons (zero allocation)\n"
        "- \"Could this be a method reference?\" - prefer "
        "`String::toLowerCase` over `s -> s.toLowerCase()`\n"
        "- \"Is the functional interface correct?\" - wrong "
        "interface choice causes confusing compiler errors"
    ),
    "Streams API": (
        "Streams embody the fundamental programming paradigm shift "
        "from imperative to declarative data processing. The same "
        "pattern appears in SQL (declarative query), LINQ (.NET), "
        "RxJava (reactive streams), and Apache Spark (distributed "
        "data pipelines). The expert insight is that streams are "
        "lazy pipelines: no computation happens until a terminal "
        "operation triggers pull-based evaluation. This enables "
        "short-circuiting (`findFirst`, `anyMatch`), fusion "
        "(merging map+filter into one pass), and parallelism "
        "(splitting via `Spliterator`). At extreme scale, "
        "`parallelStream()` uses the common ForkJoinPool, which "
        "means a slow stream operation blocks ALL parallel streams "
        "in the JVM. Production systems must use custom "
        "ForkJoinPool instances. If redesigning today, you would "
        "add `Stream.gather()` (preview in Java 22) for "
        "user-defined intermediate operations and fix the "
        "checked-exception problem that makes streams unusable "
        "with IO-throwing functions.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Will this stream be consumed once?\" - streams are "
        "single-use; accidental reuse throws "
        "`IllegalStateException`\n"
        "- \"Is parallel faster here?\" - only for CPU-bound work "
        "on large datasets (>10K elements). IO-bound or small "
        "collections are slower parallel\n"
        "- \"Am I mutating state in stream operations?\" - "
        "stateful lambdas in parallel streams cause race conditions"
    ),
    "Optional": (
        "Optional is Java's implementation of the Maybe/Option "
        "monad found in Haskell (`Maybe`), Rust (`Option<T>`), "
        "Scala (`Option[T]`), and Swift (`Optional<T>`). The "
        "cross-domain insight: Optional encodes the concept of "
        "'absence' in the type system, forcing the caller to "
        "handle the no-value case explicitly rather than ignoring "
        "it. This is the same pattern as null-safe navigation in "
        "Kotlin (`?.`), nullable reference types in C# 8+, and "
        "Result types for error handling. At extreme scale, "
        "Optional's limitation is boxing: `Optional<Integer>` "
        "double-boxes the value (Optional object wrapping Integer "
        "object wrapping int). `OptionalInt`/`OptionalLong` exist "
        "for primitives but don't compose with the generic stream "
        "API. If redesigning today, Valhalla value types would make "
        "Optional zero-cost (stack-allocated, no header).\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this a field or a return type?\" - Optional is for "
        "return types, never for fields, parameters, or "
        "collections\n"
        "- \"Am I using `get()` without `isPresent()`?\" - if "
        "yes, use `orElse`/`orElseThrow`/`map` instead\n"
        "- \"Is the default value expensive?\" - use `orElseGet("
        "supplier)` not `orElse(expensiveCall())` to avoid eager "
        "evaluation"
    ),
    "Functional Interfaces": (
        "Functional interfaces are Java's bridge between "
        "object-oriented and functional paradigms. The same "
        "concept appears as protocols with single methods in "
        "Swift, traits with one abstract method in Rust, and "
        "single-abstract-method (SAM) types in Kotlin/Scala. The "
        "expert insight is that `@FunctionalInterface` is a "
        "compile-time constraint, not a runtime feature - it tells "
        "the compiler to reject an interface if it has more than "
        "one abstract method. The four core functional interfaces "
        "(`Function`, `Predicate`, `Consumer`, `Supplier`) form a "
        "complete algebra: any data transformation can be expressed "
        "as a composition of these primitives plus their "
        "bi-variants. At extreme scale, functional interfaces "
        "enable the strategy pattern without class proliferation: "
        "instead of N strategy classes, you pass N lambdas. If "
        "redesigning today, you would add built-in support for "
        "checked exceptions (`ThrowingFunction<T, R, E>`) to avoid "
        "the pervasive try-catch-wrap pattern in stream operations.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Which of the four core types fits?\" - "
        "Function (T->R), Predicate (T->bool), Consumer (T->void), "
        "Supplier (()->T)\n"
        "- \"Should I create a custom functional interface?\" - "
        "only when the four core types don't express the intent "
        "clearly enough\n"
        "- \"Can I compose these?\" - use `.andThen()`, "
        "`.compose()`, `.and()`, `.or()`, `.negate()` for pipeline "
        "composition"
    ),
    "Method References": (
        "Method references are syntactic shorthand for lambdas that "
        "simply delegate to an existing method. The same concept "
        "exists in C# (method groups), Kotlin (callable "
        "references `::method`), and Python (first-class "
        "functions). The expert insight: method references are not "
        "just shorter - they often produce more efficient bytecode "
        "because the JVM can directly bind the call site to the "
        "target method via `invokedynamic`, skipping the lambda "
        "proxy entirely. There are four kinds: static "
        "(`Integer::parseInt`), bound instance "
        "(`myStr::toLowerCase`), unbound instance "
        "(`String::length`), and constructor (`ArrayList::new`). "
        "At extreme scale, method references compose better than "
        "lambdas for pipeline readability: "
        "`.map(String::trim).filter(Predicate.not(String::isEmpty))` "
        "reads like a specification. If redesigning today, you "
        "would fix the limitation that method references cannot "
        "express partial application (`Integer::compare` cannot "
        "be partially applied to fix one argument).\n\n"
        "**Expert thinking cues:**\n"
        "- \"Which of the 4 forms is this?\" - static, bound "
        "instance, unbound instance, or constructor\n"
        "- \"Does this lambda just call a single method?\" - if "
        "yes, replace with method reference for clarity\n"
        "- \"Is the method overloaded?\" - overloaded methods can "
        "cause ambiguous method reference errors at compile time"
    ),
    "Default Methods": (
        "Default methods solved Java's interface evolution problem "
        "- the same problem addressed by extension methods in C#, "
        "traits in Rust/Scala, and protocol extensions in Swift. "
        "The expert insight: default methods enabled the entire "
        "Streams API to be added to `Collection` (via "
        "`stream()`, `parallelStream()`, `forEach()`) without "
        "breaking the millions of existing `Collection` "
        "implementations. This is the 'expression problem' "
        "solution for Java: adding new operations to existing "
        "types without modifying them. At extreme scale, default "
        "methods create the diamond problem when a class implements "
        "two interfaces with the same default method signature - "
        "Java resolves this by requiring the class to override and "
        "explicitly choose. If redesigning today, you might prefer "
        "Kotlin-style interface delegation or Rust traits with "
        "explicit impl blocks to avoid the ambiguity entirely.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this behavior or contract?\" - default methods "
        "should provide convenience behavior, not core contract\n"
        "- \"Could two interfaces conflict?\" - check for diamond "
        "inheritance and override explicitly\n"
        "- \"Should this be an abstract class instead?\" - if you "
        "need state (fields), yes. Default methods cannot access "
        "instance state."
    ),
}

QUICKREF = {
    "Lambda Expressions": (
        "**WHAT IT IS:** Anonymous function that implements a "
        "functional interface via concise syntax\n"
        "**PROBLEM IT SOLVES:** Eliminates verbose anonymous inner "
        "class boilerplate for single-method callbacks\n"
        "**KEY INSIGHT:** Compiled to `invokedynamic`, not inner "
        "classes - faster, no `.class` files, zero allocation for "
        "non-capturing lambdas\n"
        "**USE WHEN:** Callbacks, event handlers, comparators, "
        "stream operations, strategy pattern\n"
        "**AVOID WHEN:** Logic exceeds 3 lines - extract to a named "
        "method and use method reference\n"
        "**ANTI-PATTERN:** Capturing mutable state in parallel "
        "stream lambdas - causes race conditions\n"
        "**TRADE-OFF:** Conciseness and composability vs reduced "
        "debuggability (anonymous stack frames)\n"
        "**ONE-LINER:** \"Behavior as a value - pass functions like "
        "data, compose like pipelines\""
    ),
    "Streams API": (
        "**WHAT IT IS:** Lazy, declarative pipeline for "
        "transforming and aggregating collections\n"
        "**PROBLEM IT SOLVES:** Replaces imperative loops with "
        "composable filter-map-reduce chains\n"
        "**KEY INSIGHT:** Lazy evaluation - nothing executes until "
        "a terminal operation triggers pull-through\n"
        "**USE WHEN:** Collection transformations, aggregations, "
        "filtering, grouping, parallel processing\n"
        "**AVOID WHEN:** Simple iteration with side effects, small "
        "collections (<100 elements), or when readability suffers\n"
        "**ANTI-PATTERN:** Using `parallelStream()` without "
        "measuring - it uses the common ForkJoinPool and can "
        "starve other tasks\n"
        "**TRADE-OFF:** Declarative clarity and potential "
        "parallelism vs debugging difficulty and "
        "single-use constraint\n"
        "**ONE-LINER:** \"Declarative data pipeline - lazy, "
        "composable, parallelizable, single-use\""
    ),
    "Optional": (
        "**WHAT IT IS:** Container that either holds a non-null "
        "value or is explicitly empty\n"
        "**PROBLEM IT SOLVES:** Makes absence explicit in the type "
        "system, replacing null-check chains\n"
        "**KEY INSIGHT:** Forces callers to handle the no-value "
        "case - NPEs become compile-time type errors\n"
        "**USE WHEN:** Method return types where absence is a valid "
        "outcome (e.g., findById)\n"
        "**AVOID WHEN:** Fields, method parameters, collections, "
        "or performance-critical inner loops\n"
        "**ANTI-PATTERN:** `optional.get()` without `isPresent()` "
        "check - defeats the entire purpose\n"
        "**TRADE-OFF:** Null safety and self-documenting API vs "
        "object allocation overhead and verbose chaining\n"
        "**ONE-LINER:** \"Type-safe null - makes absence visible, "
        "forces handling, eliminates NPE\""
    ),
    "Functional Interfaces": (
        "**WHAT IT IS:** Interface with exactly one abstract method "
        "- the lambda target type\n"
        "**PROBLEM IT SOLVES:** Provides the type system bridge "
        "between OOP interfaces and lambda expressions\n"
        "**KEY INSIGHT:** Four core types cover most use cases: "
        "Function (T->R), Predicate (T->bool), Consumer (T->void), "
        "Supplier (()->T)\n"
        "**USE WHEN:** Defining lambda-compatible APIs, strategy "
        "pattern, callback contracts\n"
        "**AVOID WHEN:** Interface needs multiple abstract methods "
        "- use a regular interface\n"
        "**ANTI-PATTERN:** Creating custom functional interfaces "
        "when `Function`/`Predicate`/`Consumer`/`Supplier` already "
        "fit\n"
        "**TRADE-OFF:** Lambda compatibility and composability vs "
        "less descriptive than named interface methods\n"
        "**ONE-LINER:** \"One abstract method = lambda target - "
        "Function, Predicate, Consumer, Supplier\""
    ),
    "Method References": (
        "**WHAT IT IS:** Shorthand for a lambda that delegates to "
        "an existing method (`Class::method`)\n"
        "**PROBLEM IT SOLVES:** Eliminates trivial pass-through "
        "lambdas that just call one method\n"
        "**KEY INSIGHT:** Four kinds: static, bound instance, "
        "unbound instance, and constructor references\n"
        "**USE WHEN:** Lambda body is a single method call with "
        "matching parameters\n"
        "**AVOID WHEN:** Need to transform arguments, add logic, "
        "or the method is overloaded (ambiguity)\n"
        "**ANTI-PATTERN:** Writing `x -> x.toString()` instead of "
        "`Object::toString` - less readable, less optimizable\n"
        "**TRADE-OFF:** Readability and potential JVM optimization "
        "vs less explicit about parameter flow\n"
        "**ONE-LINER:** \"Point to the method, skip the lambda - "
        "`Class::method` replaces `x -> Class.method(x)`\""
    ),
    "Default Methods": (
        "**WHAT IT IS:** Interface method with a body - provides "
        "default implementation that classes can override\n"
        "**PROBLEM IT SOLVES:** Evolve interfaces without breaking "
        "all existing implementations\n"
        "**KEY INSIGHT:** Enabled the entire Streams API to be "
        "added to `Collection` without breaking existing code\n"
        "**USE WHEN:** Adding new methods to published interfaces, "
        "providing convenience overloads\n"
        "**AVOID WHEN:** Method requires instance state (fields) - "
        "use abstract class instead\n"
        "**ANTI-PATTERN:** Using default methods to simulate "
        "multiple inheritance of state - interfaces have no fields\n"
        "**TRADE-OFF:** Interface evolution without breakage vs "
        "diamond problem and blurred abstract class boundary\n"
        "**ONE-LINER:** \"Interface evolution - add methods to "
        "interfaces without breaking implementations\""
    ),
}

COMPARISON = {
    "Lambda Expressions": (
        "| Aspect | Lambda | Anonymous Class | "
        "Method Reference |\n"
        "|--------|--------|----------------|"
        "-----------------|\n"
        "| Syntax | `x -> x + 1` | `new Fn() { ... }` | "
        "`Math::abs` |\n"
        "| Compiled to | `invokedynamic` | Inner class file | "
        "`invokedynamic` |\n"
        "| `this` refers to | Enclosing class | Anonymous class | "
        "Enclosing class |\n"
        "| Can have state | No (captures only) | Yes (fields) | "
        "No |\n"
        "| Performance | Best (no class) | Worst (class load) | "
        "Best |"
    ),
    "Streams API": (
        "| Aspect | Stream | For-each Loop | "
        "Iterator |\n"
        "|--------|--------|--------------|"
        "---------|\n"
        "| Style | Declarative | Imperative | Imperative |\n"
        "| Lazy | Yes | No | Yes |\n"
        "| Parallel | Built-in | Manual | No |\n"
        "| Reusable | No (single-use) | Yes | No |\n"
        "| Side effects | Discouraged | Normal | Normal |\n"
        "| Debugging | Harder | Easy | Easy |"
    ),
    "Optional": (
        "| Aspect | Optional | Null | "
        "Kotlin Nullable (`T?`) |\n"
        "|--------|----------|------|"
        "----------------------|\n"
        "| Type safety | Compile-time | None | "
        "Compile-time |\n"
        "| Memory | Object allocation | Zero | Zero |\n"
        "| Chaining | `map`/`flatMap` | Nested ifs | "
        "`?.` operator |\n"
        "| Absence visible | In signature | No | "
        "In signature |\n"
        "| Serializable | No | N/A | N/A |"
    ),
    "Functional Interfaces": (
        "| Interface | Signature | Use Case | "
        "Example |\n"
        "|-----------|-----------|----------|"
        "--------|\n"
        "| `Function<T,R>` | `T -> R` | Transform | "
        "`String::length` |\n"
        "| `Predicate<T>` | `T -> boolean` | Filter | "
        "`String::isEmpty` |\n"
        "| `Consumer<T>` | `T -> void` | Side effect | "
        "`System.out::println` |\n"
        "| `Supplier<T>` | `() -> T` | Factory | "
        "`ArrayList::new` |\n"
        "| `UnaryOperator<T>` | `T -> T` | Same-type transform | "
        "`String::trim` |\n"
        "| `BiFunction<T,U,R>` | `(T,U) -> R` | Two-arg "
        "transform | `String::concat` |"
    ),
    "Method References": (
        "| Kind | Syntax | Lambda Equivalent | "
        "Example |\n"
        "|------|--------|-------------------|"
        "--------|\n"
        "| Static | `Class::staticMethod` | "
        "`x -> Class.staticMethod(x)` | `Integer::parseInt` |\n"
        "| Bound instance | `obj::method` | "
        "`() -> obj.method()` | `str::length` |\n"
        "| Unbound instance | `Class::method` | "
        "`x -> x.method()` | `String::toLowerCase` |\n"
        "| Constructor | `Class::new` | "
        "`() -> new Class()` | `ArrayList::new` |"
    ),
    "Default Methods": (
        "| Aspect | Default Method | Abstract Method | "
        "Static Method |\n"
        "|--------|---------------|----------------|"
        "--------------|\n"
        "| Has body | Yes | No | Yes |\n"
        "| Override | Optional | Required | Cannot |\n"
        "| Access instance | Via `this` | N/A | No |\n"
        "| Inheritance | Diamond possible | Single abstract | "
        "No inheritance |\n"
        "| Purpose | Evolution/convenience | Contract | "
        "Utility |"
    ),
}

MISCONCEPTIONS = {
    "Lambda Expressions": [
        ("Lambdas are syntactic sugar for anonymous inner classes",
         "Lambdas use `invokedynamic` bytecode, not inner classes. "
         "No `.class` file is generated. `this` refers to the "
         "enclosing class, not the lambda. Performance is better."),
        ("Lambdas can modify local variables",
         "Captured local variables must be effectively final. "
         "Lambdas capture values, not variable bindings. Use "
         "`AtomicInteger` or a one-element array for mutation."),
        ("All lambdas cause object allocation",
         "Non-capturing lambdas (no external variables) are "
         "typically cached as singletons by the JVM - zero "
         "allocation after first call."),
        ("Longer lambdas are fine if they work",
         "Lambdas over 3 lines harm readability. Extract to a "
         "named method and use a method reference. The lambda body "
         "should express intent, not implementation."),
    ],
    "Streams API": [
        ("Streams are always faster than loops",
         "For small collections (<100 elements) or simple "
         "operations, for-loops are faster due to less "
         "overhead. Streams add object creation and method "
         "call layers."),
        ("`parallelStream()` always improves performance",
         "Parallel streams use the common ForkJoinPool. For "
         "IO-bound work, small data, or ordered operations, "
         "parallel is slower. Measure before parallelizing."),
        ("Streams can be reused",
         "A stream can only be consumed once. Calling a terminal "
         "operation twice throws `IllegalStateException`. Create "
         "a new stream from the source for each use."),
        ("Stream operations execute immediately",
         "Intermediate operations (`map`, `filter`) are lazy - "
         "they build a pipeline. Nothing executes until a terminal "
         "operation (`collect`, `forEach`) triggers evaluation."),
    ],
    "Optional": [
        ("`Optional.get()` is safe to call",
         "`get()` throws `NoSuchElementException` if empty. "
         "Use `orElse()`, `orElseGet()`, or `orElseThrow()` "
         "instead. `get()` without `isPresent()` defeats the "
         "purpose."),
        ("Optional should be used for method parameters",
         "Optional is designed for return types only. For "
         "parameters, use method overloading or `@Nullable`. "
         "Optional parameters add unnecessary wrapping."),
        ("Optional prevents all NPEs",
         "You can still get NPE if: you pass null to "
         "`Optional.of()` (use `ofNullable`), call `get()` on "
         "empty, or store null in a field that should be Optional."),
        ("Optional has negligible overhead",
         "Each `Optional.of()` creates an object on the heap. "
         "In tight loops, this adds GC pressure. Use "
         "`OptionalInt`/`OptionalLong` for primitives."),
    ],
    "Functional Interfaces": [
        ("@FunctionalInterface is required for lambda use",
         "The annotation is optional - any interface with one "
         "abstract method works with lambdas. `@FunctionalInterface` "
         "just adds compile-time validation."),
        ("Functional interfaces can only have one method",
         "They have one *abstract* method. They can have multiple "
         "`default` methods, `static` methods, and methods inherited "
         "from `Object` (`equals`, `hashCode`, `toString`)."),
        ("You should always create custom functional interfaces",
         "Java provides 43 built-in functional interfaces in "
         "`java.util.function`. Custom ones are only needed when "
         "none fit or when the name adds domain clarity."),
        ("BiFunction covers all two-argument cases",
         "`BiFunction<T,U,R>` only handles two inputs. For more "
         "arguments, create a custom interface or use currying: "
         "`Function<A, Function<B, Function<C, R>>>`."),
    ],
    "Method References": [
        ("Method references are always clearer than lambdas",
         "For complex scenarios like overloaded methods or when "
         "parameter mapping is non-obvious, a lambda with named "
         "parameters is clearer. Use method references for simple "
         "delegations."),
        ("Method references create new objects each time",
         "Like non-capturing lambdas, method references to static "
         "methods are typically cached as singletons by the JVM."),
        ("`obj::method` and `Class::method` are the same",
         "Bound (`obj::method`) captures the specific instance. "
         "Unbound (`Class::method`) takes the instance as the "
         "first parameter. Different signatures and behaviors."),
        ("Constructor references only work with no-arg constructors",
         "Constructor references adapt to the functional interface's "
         "parameter list. `Function<String, Integer>` matches "
         "`Integer::new` (the `Integer(String)` constructor)."),
    ],
    "Default Methods": [
        ("Default methods make interfaces same as abstract classes",
         "Interfaces still cannot have instance fields, "
         "constructors, or non-public methods (until Java 9 "
         "private methods). Abstract classes support all of these."),
        ("Default methods always win over superclass methods",
         "Class methods always win over default methods "
         "(\"class wins\" rule). A class's concrete or abstract "
         "method takes precedence over any interface default."),
        ("Diamond inheritance is always a compile error",
         "Java only errors if the class doesn't override the "
         "conflicting default method. The class can resolve by "
         "overriding and calling `InterfaceName.super.method()`."),
        ("Default methods should contain complex logic",
         "Default methods should provide simple convenience "
         "implementations. Complex logic belongs in abstract "
         "classes or helper classes where state management and "
         "testing are simpler."),
    ],
}

FAILURES = {
    "Lambda Expressions": """**Failure Mode 1: Effectively final violation**
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
**Prevention:** Create utility `ThrowingFunction` wrappers or use libraries like Vavr for checked-exception-safe functional types.""",

    "Streams API": """**Failure Mode 1: IllegalStateException - stream already consumed**
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
grep -n 'parallelStream\\|parallel()' MyClass.java
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
**Prevention:** Use custom ForkJoinPool for IO-bound parallel streams. Keep common pool for CPU-bound work only.""",

    "Optional": """**Failure Mode 1: NoSuchElementException from get()**
**Symptom:** `NoSuchElementException: No value present` from `Optional.get()`.
**Root Cause:** Calling `get()` without checking `isPresent()` - the anti-pattern Optional was designed to prevent.
**Diagnostic:**

```
grep -n '\\.get()' MyClass.java
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
grep -n 'Optional\\.of(' MyClass.java
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
grep -n '\\.orElse(' MyClass.java
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
**Prevention:** Use `orElseGet(supplier)` when the default value is expensive or has side effects. `orElse()` is only safe for constants.""",

    "Functional Interfaces": """**Failure Mode 1: Ambiguous lambda target type**
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
**Prevention:** Create `ThrowingFunction`/`ThrowingConsumer` wrappers for exception-prone functional code.""",

    "Method References": """**Failure Mode 1: Ambiguous method reference for overloaded methods**
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
**Prevention:** Never create bound method references from nullable variables. Null-check first.""",

    "Default Methods": """**Failure Mode 1: Diamond inheritance conflict**
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
**Prevention:** Adding methods to published interfaces: always use `default`. Never add abstract methods to `@FunctionalInterface`.""",
}

RELATED = {
    "Lambda Expressions": """**Prerequisites (understand these first):**

- Functional Interfaces - lambdas must target a functional interface type
- Anonymous inner classes - the verbose predecessor that lambdas replace

**Builds on this (learn these next):**

- Streams API - lambdas enable the entire stream pipeline
- Method References - concise alternative when lambda just delegates

**Alternatives / Comparisons:**

- Anonymous inner classes - when you need `this` scoping or multiple methods
- Method references - when lambda body is a single method call""",

    "Streams API": """**Prerequisites (understand these first):**

- Lambda Expressions - streams require lambdas for all operations
- Collections Framework - streams operate on collections and arrays

**Builds on this (learn these next):**

- Collectors API - advanced grouping, partitioning, and reduction
- Parallel streams and ForkJoinPool - concurrent data processing

**Alternatives / Comparisons:**

- For-each loops - simpler for side-effect-heavy or small operations
- RxJava/Reactor - push-based reactive streams with backpressure""",

    "Optional": """**Prerequisites (understand these first):**

- Null references and NPE - the problem Optional solves
- Generics - Optional is a generic container type

**Builds on this (learn these next):**

- Stream operations returning Optional - `findFirst()`, `reduce()`
- Monadic chaining with `map`/`flatMap` - composing Optional pipelines

**Alternatives / Comparisons:**

- Kotlin nullable types (`T?`) - compiler-enforced null safety without wrapping
- `@Nullable` annotations - lightweight null documentation for static analysis""",

    "Functional Interfaces": """**Prerequisites (understand these first):**

- Interfaces and abstract classes - functional interfaces extend the interface concept
- Generics - core functional interfaces are generic (`Function<T,R>`)

**Builds on this (learn these next):**

- Lambda Expressions - the primary syntax for implementing functional interfaces
- Composition methods - `andThen()`, `compose()`, `and()`, `or()`, `negate()`

**Alternatives / Comparisons:**

- Strategy pattern with classes - when you need state or multiple methods
- Kotlin SAM conversions - automatic functional interface adaptation""",

    "Method References": """**Prerequisites (understand these first):**

- Lambda Expressions - method references are shorthand for lambdas
- Functional Interfaces - method references must match a functional interface

**Builds on this (learn these next):**

- Streams API - method references make stream pipelines more readable
- Constructor references - `Class::new` for factory patterns

**Alternatives / Comparisons:**

- Explicit lambdas - when parameter transformation is needed
- Reflection (`Method.invoke`) - when method is determined at runtime""",

    "Default Methods": """**Prerequisites (understand these first):**

- Interfaces - default methods extend the traditional interface concept
- Inheritance and polymorphism - understanding method resolution order

**Builds on this (learn these next):**

- Interface evolution patterns - adding methods to published APIs
- Private interface methods (Java 9) - extracting common default method logic

**Alternatives / Comparisons:**

- Abstract classes - when you need fields, constructors, or complex state
- Kotlin extension functions - adding methods without modifying the type""",
}


def apply_all(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # Level 5
    level5_old = (
        "[TODO: Cross-domain pattern recognition. "
        "Expert heuristics.\n"
        " What would you change if redesigning today?\n"
        " How does this compose at extreme scale?]"
    )
    for kw in KEYWORDS:
        if level5_old in content and kw in LEVEL5:
            content = content.replace(level5_old, LEVEL5[kw], 1)
            changes += 1

    # Quick Reference Card
    qr_old = (
        "**WHAT IT IS:** [TODO]\n"
        "**PROBLEM IT SOLVES:** [TODO]\n"
        "**KEY INSIGHT:** [TODO]\n"
        "**USE WHEN:** [TODO]\n"
        "**AVOID WHEN:** [TODO]\n"
        "**ANTI-PATTERN:** [TODO]\n"
        "**TRADE-OFF:** [TODO]\n"
        "**ONE-LINER:** [TODO]"
    )
    for kw in KEYWORDS:
        if qr_old in content and kw in QUICKREF:
            content = content.replace(qr_old, QUICKREF[kw], 1)
            changes += 1

    # Comparison Table
    for kw in KEYWORDS:
        ct_old = (
            f"[TODO: Include if 2+ named alternatives exist "
            f"for {kw}. Otherwise remove this section.]"
        )
        if ct_old in content and kw in COMPARISON:
            content = content.replace(ct_old, COMPARISON[kw], 1)
            changes += 1

    # Misconceptions (regex for whitespace variations)
    mc_pat = re.compile(
        r'\| 1\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 2\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 3\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 4\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|'
    )
    for kw in KEYWORDS:
        if kw in MISCONCEPTIONS:
            m = mc_pat.search(content)
            if m:
                rows = MISCONCEPTIONS[kw]
                replacement = "\n".join(
                    f"| {i+1} | {mis} | {real} |"
                    for i, (mis, real) in enumerate(rows)
                )
                content = content[:m.start()] + replacement + \
                    content[m.end():]
                changes += 1

    # Failure Modes (no blank line before code fence)
    fm_pat = re.compile(
        r'\*\*Failure Mode 1: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 2: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 3: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]'
    )
    for kw in KEYWORDS:
        if kw in FAILURES:
            m = fm_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    FAILURES[kw] + content[m.end():]
                changes += 1

    # Related Keywords
    rk_pat = re.compile(
        r'\*\*Prerequisites \(understand these first\):\*\*\n\n?'
        r'- \[TODO\] - \[why needed\]\n'
        r'- \[TODO\] - \[why needed\]\n'
        r'\n?'
        r'\*\*Builds on this \(learn these next\):\*\*\n\n?'
        r'- \[TODO\] - \[what it adds\]\n'
        r'- \[TODO\] - \[what it adds\]\n'
        r'\n?'
        r'\*\*Alternatives / Comparisons:\*\*\n\n?'
        r'- \[TODO\] - \[when to prefer it\]\n'
        r'- \[TODO\] - \[when to prefer it\]'
    )
    for kw in KEYWORDS:
        if kw in RELATED:
            m = rk_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    RELATED[kw] + content[m.end():]
                changes += 1

    with open(filepath, 'w', encoding='utf-8',
              newline='\n') as f:
        f.write(content)

    remaining = content.count('[TODO')
    print(f"Applied {changes} replacements")
    print(f"Remaining TODOs: {remaining}")


apply_all(FILE)
