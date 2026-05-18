---
id: CSF-034
title: "Type Systems (Static vs Dynamic)"
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-001, CSF-005
used_by: CSF-035, CSF-036, CSF-037, CSF-038
related: CSF-070, JLG-001
tags: [type-systems, static-typing, dynamic-typing, type-safety, type-checking]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/csf/type-systems-static-vs-dynamic/
---

⚡ TL;DR - Static typing catches type errors at compile
time (Java, Kotlin, TypeScript); dynamic typing defers
checks to runtime (Python, JavaScript). Java adds type
erasure at runtime and gradual typing paths via tools.

| #034 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-001 (Programming Paradigms), CSF-005 (Variables and Types) | |
| **Used by:** | CSF-035 (Type Inference), CSF-037 (Generics), CSF-038 (ADTs) | |
| **Related:** | CSF-070 (JIT vs AOT), JLG-001 (Java Language Basics) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Assembly code has no types: a register holds 64 bits.
Whether those bits represent an integer, a memory address,
a floating-point number, or a string pointer is entirely
up to the programmer. Calling a function with the wrong
argument type causes silent data corruption. Early FORTRAN
(1957) introduced type distinctions (INTEGER vs REAL) to
prevent the most common calculation errors. The problem
became acute as programs grew: calling a function with
string data where integer data is expected causes a crash
(best case) or silent wrong result (worst case). In a
100,000-line codebase, tracking all type contracts manually
is impossible.

**THE BREAKING POINT:**

JavaScript circa 2010: `'2' + 2 = '22'` (string concatenation),
`'2' - 2 = 0` (numeric subtraction), `null + 1 = 1`,
`undefined + 1 = NaN`, `[] + {} = '[object Object]'`,
`{} + [] = 0`. The absence of type checking means the
language will perform ANY operation on ANY value and try
to coerce it rather than reject it. At scale, these silent
coercions cause bugs that are nearly impossible to trace.
TypeScript was created specifically because large-scale
JavaScript development was unsafe without type annotations.

**THE INVENTION MOMENT:**

Type theory in programming languages developed through
the 1960s-1980s. The fundamental question: when should
we verify that operations are applied to compatible values?
Static typing: at compile time (before execution).
Dynamic typing: at runtime (during execution).
Gradual typing (Gilad Bracha, 2004, later TypeScript):
optionally annotate types where helpful, skip where not.
The insight: the choice is a trade-off between catching
errors early (static) and flexibility / rapid prototyping
(dynamic), not a correctness absolute.

---

### 📘 Textbook Definition

A type system is a set of rules that assigns a type to
each expression in a program and determines which operations
are valid on values of each type.

**Static typing:** Types are verified at compile time.
The compiler rejects programs where an operation is applied
to a value of an incompatible type. Examples: Java, Kotlin,
Scala, TypeScript, Rust, Go, Haskell.

**Dynamic typing:** Types are checked at runtime.
The runtime raises an error (TypeError, AttributeError)
when an operation is applied to an incompatible value.
Examples: Python, JavaScript, Ruby, PHP (loose typing).

**Strong vs weak typing** (orthogonal to static/dynamic):
**Strong:** type coercion between incompatible types is
rejected or requires explicit casting (Java, Python).
**Weak:** implicit coercion between incompatible types
is allowed (C: `int + float` implicitly; JavaScript: `'2'+2`).

Java is: **statically typed** + **strongly typed** +
type erasure at runtime (generics are compile-time only).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Static typing = compile-time type errors; dynamic typing
= runtime type errors. Strong typing = no implicit coercion;
weak typing = implicit coercion allowed.

**One analogy:**

> Static typing: a type-checked contract before the work
> begins. A building contractor reviews the blueprints
> and says "this wall cannot carry that load" before any
> concrete is poured. Errors discovered while the cost
> to fix is low.
>
> Dynamic typing: discover the problem during construction.
> You pour the concrete, the wall collapses. The problem
> is real, discovered at runtime. In software: the customer
> discovers the type error in production.

**One insight:**

Java's type system is static, but it has a runtime escape
hatch: casting. `(String) someObject` compiles fine but
throws `ClassCastException` at runtime if `someObject`
is not a `String`. Java's `instanceof` check before casting
is the manual version of the runtime type check that
dynamic languages do automatically. Java 16+ pattern
matching (`if (obj instanceof String s)`) eliminates the
unsafe cast entirely.

---

### 🔩 First Principles Explanation

**THE TYPE CHECKING SPECTRUM:**

```
┌──────────────────────────────────────────────────────┐
│ STATIC STRONG │ Java, Kotlin, Haskell, Rust           │
│  Checked at: compile time                            │
│  Coercion:   explicit cast required                  │
│  Errors:     caught before execution                 │
│                                                      │
│ STATIC WEAK   │ C, C++ (some implicit coercions)      │
│  Checked at: compile time (partial)                  │
│  Coercion:   some implicit (int/float arithmetic)    │
│                                                      │
│ DYNAMIC STRONG│ Python, Ruby                          │
│  Checked at: runtime                                 │
│  Coercion:   explicit; TypeError on mismatch         │
│  Example: Python `'a' + 1 -> TypeError`              │
│                                                      │
│ DYNAMIC WEAK  │ JavaScript, PHP (some contexts)       │
│  Checked at: runtime                                 │
│  Coercion:   implicit and pervasive                  │
│  Example: JS `'2' + 2 = '22'` (no error thrown)     │
└──────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

**Static typing gains:** IDE autocompletion, safe refactoring,
compile-time error detection, no runtime `TypeError`, self-
documenting code (types ARE documentation).

**Static typing costs:** Verbosity (type annotations),
less flexibility for metaprogramming, type system fights
(covariance/contravariance, wildcards), longer compile times.

**Dynamic typing gains:** Flexibility, faster prototyping,
less ceremony, easy duck typing (any object with the right
methods works regardless of type hierarchy).

**Dynamic typing costs:** Runtime type errors, no IDE
autocomplete on untyped values, harder refactoring
(rename a field - how do you find all callers across a
dynamically typed codebase?), bugs only caught in production.

---

### 🧪 Thought Experiment

**GRADUAL TYPING IN PRACTICE:**

TypeScript is JavaScript with optional type annotations.
A migration path:
1. Start with `any` everywhere (dynamic, zero type safety).
2. Add types to function signatures one by one (gradual).
3. Enable `strict: true` in `tsconfig.json` (strict static).

Python has a similar path via `mypy`: add type hints
(`def add(a: int, b: int) -> int`) and run `mypy` for
static checking without changing the runtime.

**THE LESSON:**

Static and dynamic typing are not binary opposites.
Gradual typing allows teams to incrementally add type
safety to existing codebases. TypeScript's adoption
at Microsoft, Google, and Airbnb showed that large teams
working on large JavaScript codebases could dramatically
reduce runtime type errors by adding type annotations
without a full rewrite.

---

### 🎯 Mental Model / Analogy

**CONTRACTS BEFORE VS DURING WORK:**

Think of types as contracts. Static typing checks all
contracts before anyone starts working (compile time).
If a contract is wrong, the project does not start.
Dynamic typing starts the work and checks contracts as
they are encountered at runtime. The first contract
violation stops the work (runtime error).

For long-running programs (web servers), a dynamic typing
runtime error may only occur for specific inputs or specific
code paths - which may not be encountered in testing,
only in production. Static typing catches ALL paths
before execution.

**MEMORY HOOK:**

"Static = compiler catches type errors. Dynamic = runtime
crashes on type errors. Strong = no implicit coercion.
Weak = silent coercions. Java: static + strong + type erasure.
Python: dynamic + strong. JavaScript: dynamic + weak."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Types tell the computer what kind of thing a variable
stores: numbers, words, true/false. Static typing: check
types before running. Dynamic typing: check types while running.

**Level 2 - Student:**
In Java (static): `int x = "hello"` is a compile error.
The compiler rejects it before the program runs. In Python
(dynamic): `x = 5; x = "hello"` is fine - `x` changes
type at runtime. An error only occurs if you do something
incompatible like `x + 5` after assigning the string.

**Level 3 - Professional:**
Java's type system at the JVM level: all generic type
parameters are erased at compile time (type erasure).
`List<String>` and `List<Integer>` are both just `List`
at runtime. `instanceof List<String>` is a compile error
because there is no `List<String>` at runtime. Casts to
parameterized types generate "unchecked cast" warnings.
This is a design trade-off: generic type erasure maintains
backward compatibility with pre-Java-5 code but means
generic type information is not available at runtime.

**Level 4 - Senior Engineer:**
Structural vs nominal typing (a separate but related concept):
Java is nominally typed - compatibility is determined by
declared type names. `class Duck implements Animal` - Duck
is an Animal because the declaration says so. TypeScript
is structurally typed - compatibility is determined by
shape (fields and methods). If `Duck` has a `quack()` method
and the interface requires a `quack()` method, `Duck` is
compatible - no explicit `implements` needed. This affects
API design: nominal typing requires explicit interface
declarations; structural typing is more flexible but less
intentional.

**Level 5 - Expert:**
Dependent types (Idris, Agda, Coq) push type checking
further: the type itself can depend on a VALUE. A type
like `Vector<n>` (a vector of exactly `n` elements) is
a dependent type. Adding two `Vector<3>` values produces
a `Vector<6>` - enforced at compile time. Standard Java
cannot express this. Refinement types (LiquidHaskell,
F*) allow types like `x: Int where x > 0` - the type
system verifies the constraint holds at compile time.
These are research-grade features but inform practical
thinking: the stronger the type system, the more invariants
that can be expressed and automatically verified, reducing
the need for runtime validation.

---

### ⚙️ How It Works (Formal Basis)

**JAVA TYPE ERASURE:**

```
┌──────────────────────────────────────────────────────┐
│ At compile time (Java source):                       │
│   List<String> names = new ArrayList<String>();      │
│   names.add("Alice");                                │
│   String s = names.get(0);  // no cast needed        │
│                                                      │
│ After erasure (bytecode equivalent):                 │
│   List names = new ArrayList();  // raw type         │
│   names.add("Alice");                                │
│   String s = (String) names.get(0);  // cast added   │
│                                                      │
│ The compiler inserts the cast; the type parameter    │
│ <String> disappears from the bytecode.               │
└──────────────────────────────────────────────────────┘
```

**INSTANCEOF PATTERN MATCHING (JAVA 16+):**

```java
// Old style: unsafe cast after instanceof check
if (obj instanceof String) {
    String s = (String) obj; // cast after check = verbose
    System.out.println(s.length());
}

// New style: pattern matching (Java 16+)
if (obj instanceof String s) {
    // s is already typed as String, no explicit cast
    System.out.println(s.length());
}
```

---

### 🔄 System Design Implications

**LANGUAGE CHOICE AND TYPE SYSTEM:**

The choice of static vs dynamic typing affects system
design at scale. Statically typed codebases are easier
to refactor (rename a class - the compiler finds all
call sites). IDE tooling is more reliable (autocomplete
works on typed variables). Dynamic codebases are faster
to write initially but accumulate type-related technical
debt as they grow.

Typical pattern: start with Python/JavaScript for rapid
prototyping; migrate to TypeScript/Kotlin as the codebase
stabilizes and the team grows. This is the path Twitter
(Scala), Dropbox (mypy for Python), and Airbnb (TypeScript)
took.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Unsafe Cast**

```java
// BAD: unchecked cast can throw ClassCastException at runtime
Object obj = getValue(); // returns Object
String s = (String) obj; // ClassCastException if obj is not String
System.out.println(s.toUpperCase()); // may never reach here

// GOOD: check type before cast (old style)
Object obj = getValue();
if (obj instanceof String) {
    String s = (String) obj; // safe after check
    System.out.println(s.toUpperCase());
}

// BETTER: Java 16+ pattern matching (eliminates separate cast)
Object obj = getValue();
if (obj instanceof String s) {
    System.out.println(s.toUpperCase()); // s is typed, no cast
}
```

**Example 2 - Dynamic Typing Pitfalls (Python example)**

```python
# BAD: function assumes int, silently produces wrong result with str
def double(x):
    return x * 2

print(double(5))      # 10 - correct
print(double("abc"))  # "abcabc" - wrong! no error, silent bug

# GOOD: add type hints + runtime check (or use mypy for static)
def double(x: int) -> int:
    if not isinstance(x, int):
        raise TypeError(f"Expected int, got {type(x).__name__}")
    return x * 2

# EVEN BETTER: use mypy to catch at development time
# $ mypy myfile.py
# myfile.py:5: error: Argument 1 to "double" has
#             incompatible type "str"; expected "int"
```

---

### ⚖️ Comparison Table

| Aspect | Static Typing (Java) | Dynamic Typing (Python) | Gradual (TypeScript) |
|---|---|---|---|
| When checked | Compile time | Runtime | Compile (typed) / Runtime (any) |
| Type errors | Caught before run | Crash at runtime | Caught for typed code |
| IDE support | Full autocomplete | Partial (inferred) | Full for typed code |
| Refactoring | Compiler finds all sites | Manual search | Compiler for typed code |
| Flexibility | Less (explicit types) | More (duck typing) | Configurable |
| Performance | Optimization at compile | Runtime type checks overhead | Compiled to JS (no runtime overhead) |
| Verbosity | Higher | Lower | Medium (type inference helps) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Static typing = more verbose | Modern static languages (Kotlin, Scala, Haskell) use type inference extensively. `val x = 42` - Kotlin infers `Int`. The verbosity of Java (pre-Java 10) was a Java design choice, not a property of static typing. Java 10+ `var` reduces this. |
| Dynamic typing = faster development | True for small scripts and prototypes. For large codebases (100K+ lines), the lack of type information dramatically slows refactoring, IDE assistance, and debugging. TypeScript's adoption was driven by large teams reporting that typed JavaScript was 2-5x faster to maintain. |
| Java's type system is always checked at runtime | Java uses type erasure for generics: `List<String>` at compile time becomes `List` (raw type) at runtime. Generic type parameters do not exist at runtime. `instanceof List<String>` is a compile error. Actual runtime type information is limited. |
| Strong typing prevents all type bugs | Strong typing prevents implicit coercions. It does not prevent incorrect logic or wrong type assumptions when values are stored as `Object` (pre-generics Java), `any` in TypeScript, or `dict` in Python where the key/value types are not checked. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: ClassCastException in Legacy Generic Code**

**Symptom:** `ClassCastException: class java.lang.Integer
cannot be cast to class java.lang.String` at a line that
does not appear to cast anything.

**Root Cause:** The compiler inserted an unchecked cast
at a point where generic type information was lost (a raw
type was used, or an `@SuppressWarnings("unchecked")` was
applied to silence a warning about an unsafe cast).

**Diagnosis:**

```java
// Find the raw type usage - where is the type parameter lost?
// Look for: List (raw), Map (raw), Class.cast(), @SuppressWarnings("unchecked")

// Enable unchecked cast warnings:
// javac -Xlint:unchecked MyClass.java
// Fix each warning - they indicate where type safety is lost.
```

**Failure Mode 2: JavaScript Silent Type Coercion Bug**

**Symptom:** User's form input is treated as a number
but produces unexpected results: `'5' + 3 = '53'` instead
of `8`.

**Root Cause:** JavaScript `+` operator with a string
operand performs concatenation, not addition. User input
from forms is always a string; not parsing it first leads
to silent concatenation.

**Fix:**

```javascript
// BAD: form input is string type - silent concatenation
const total = document.getElementById('amount').value + fee;
// '50' + 5 = '505' (wrong)

// GOOD: parse to number first
const total = parseFloat(document.getElementById('amount').value) + fee;
// 50.0 + 5 = 55.0 (correct)
```

---

**Security Note:**

Type confusion vulnerabilities occur in weakly-typed or
improperly typed systems when an attacker provides a value
of an unexpected type and the system processes it in an
unsafe context. Examples: SQL injection exploits the fact
that user input (string type) is concatenated into SQL
(code type) without proper escaping. The type system does
not distinguish "safe string" from "user-controlled string."
Using parameterized queries enforces the type distinction:
the parameter is a data value, never code. In Java: never
build SQL strings with `+` concatenation; always use
`PreparedStatement` or JPA parameterized queries. The type
system cannot prevent this automatically, but disciplined
use of types (e.g., a `SafeSQL` wrapper type that can only
be created via a safe builder) can enforce it at compile time.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Programming Paradigms` (CSF-001) - type systems are
  a design dimension orthogonal to paradigm choice
- `Variables and Types` (CSF-005) - foundational understanding
  of what types are before understanding type systems

**Builds On This (learn these next):**
- `Type Inference` (CSF-035) - how compilers deduce types
  without explicit annotations (reduces verbosity)
- `Generics and Parametric Polymorphism` (CSF-037) - Java's
  generic type system in depth, including type erasure

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ STATIC TYPING│ Errors at compile time (Java, Kotlin)  │
│              │ IDE autocomplete, safe refactoring      │
├──────────────┼─────────────────────────────────────────┤
│ DYNAMIC TYPING│ Errors at runtime (Python, JavaScript) │
│              │ Flexibility, duck typing, less ceremony │
├──────────────┼─────────────────────────────────────────┤
│ STRONG TYPING│ No implicit coercion (Java, Python)    │
│              │ `'a' + 1` = TypeError                   │
├──────────────┼─────────────────────────────────────────┤
│ WEAK TYPING  │ Implicit coercion (JavaScript)          │
│              │ `'2' + 2 = '22'`, `'2' - 2 = 0`        │
├──────────────┼─────────────────────────────────────────┤
│ JAVA         │ Static + strong + type erasure          │
│              │ Generics are compile-time only          │
│              │ instanceof pattern matching (Java 16+)  │
├──────────────┼─────────────────────────────────────────┤
│ GRADUAL      │ TypeScript, mypy (Python)               │
│              │ Add types incrementally to dynamic code │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-035 (Type Inference), CSF-037 (Generics)│
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Static typing catches type errors at compile time (Java);
   dynamic typing catches them at runtime (Python). Strong
   typing rejects incompatible type operations; weak typing
   silently coerces (JavaScript `'2' + 2 = '22'`).
2. Java's generics use type erasure: `List<String>` becomes
   `List` at runtime. Generic type information is not available
   at runtime; `instanceof List<String>` is a compile error.
   Casts to generic types generate unchecked cast warnings.
3. Static and dynamic typing are a trade-off: static catches
   errors early and enables better tooling; dynamic enables
   flexibility and faster prototyping. Gradual typing
   (TypeScript, mypy) combines both by making annotations optional.

**Interview one-liner:**
"Static typing checks types at compile time (Java, Kotlin);
dynamic typing checks at runtime (Python, JavaScript).
Strong typing rejects implicit coercions; weak typing allows
them. Java is static + strong. Key Java detail: type erasure
means generic parameters are compile-time only. Java 16+
pattern matching eliminates unsafe casts."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The choice between static and dynamic typing is a trade-off
between "fail early, fail loudly" (static) and "fail
at the point of contact, fail specifically" (dynamic).
This principle appears everywhere in engineering:
Input validation at API boundaries (fail early before
the data enters the system) vs defensive validation
throughout the system (fail when the data is used).
Database constraints (fail at insert time) vs application
validation only (fail at query time). The static/dynamic
debate is the same "when to check" question applied
to types. The modern consensus: validate at boundaries
(static typing for interfaces and APIs), be flexible
internally (type inference and inference for local variables).

**Where else this pattern appears:**

- **TypeScript in frontend** - TypeScript adds static typing
  to JavaScript. Any team that has maintained a large
  JavaScript codebase without TypeScript has experienced
  the dynamic typing pain: renaming a function requires
  global text search; adding a parameter to a function
  requires manually checking all call sites; `undefined`
  errors only appear in production. TypeScript catches all
  of these at compile time with zero runtime overhead.
- **mypy in Python** - Python type hints + mypy bring static
  type checking to Python. Dropbox (in 2019) reported that
  adding mypy to their Python codebase caught 10-15% of bugs
  before deployment. Many Python teams now run mypy in CI.
- **GraphQL schemas** - GraphQL's type system is a statically
  typed API contract. Clients know exactly what types
  the server returns; the GraphQL schema validator rejects
  malformed queries at development time. This is static
  typing applied to API design: schema = contract, validated
  before execution.

---

### 💡 The Surprising Truth

JavaScript was designed in 10 days by Brendan Eich at
Netscape in 1995. Its type coercion rules (`[] + {}`,
`null == undefined`, `NaN !== NaN`) were not carefully
designed - they were implementation artifacts of the
rushed development. These coercions became standardized
as part of the ECMAScript spec because changing them
would break the existing web. The result: decades of
confusing behavior that caused TypeScript to be invented.
TypeScript, built by Microsoft as a statically typed
superset of JavaScript, was released in 2012 - 17 years
after JavaScript was created. An entire category of language
(gradual typing) was invented essentially to fix the
type system of a language created in 10 days.
The lesson: type system design decisions made early
in a language's lifetime have decades-long consequences.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Given Java code with an unchecked cast
   warning (`@SuppressWarnings("unchecked")`), trace why
   the warning exists, what runtime error it might cause
   (`ClassCastException`), and refactor it to eliminate
   the unsafe cast using generics or pattern matching.

2. **[COMPARE]** For a new project, recommend static
   (TypeScript) or dynamic (Python) typing based on:
   team size, expected codebase size, rate of change,
   and whether the API is external-facing. Justify each
   factor.

3. **[IDENTIFY]** Given a Python codebase, add type hints
   to 3 functions and run `mypy`. Identify the type errors
   caught and explain which would have been runtime crashes
   in production.

4. **[EXPLAIN]** Explain Java type erasure to a junior
   developer: why `new List<String>()` exists but
   `new T()` (where T is a generic parameter) does not.
   Explain why `obj instanceof List<String>` is a compile
   error while `obj instanceof List` compiles fine.

5. **[DESIGN]** Design the type boundary for a method
   that accepts either a `User` or an `AdminUser`:
   using polymorphism (interface/abstract class), using
   generics, and using a sealed interface with pattern
   matching (Java 17+). Explain the trade-offs.

---

### 🧠 Think About This Before We Continue

**Q1.** A colleague says "Python is dynamically typed,
so it is not type safe." Is this true? What is the
difference between dynamic typing and type safety?
Give a Python example that IS type safe and one that
is NOT, despite both being in the same dynamically typed language.

*Hint: Dynamic typing means type checks happen at runtime.
Strong dynamic typing (Python) means those runtime checks
DO reject incompatible operations with a clear TypeError.
`'a' + 1` in Python raises `TypeError: can only concatenate
str (not "int") to str`. Python IS type safe - it just
checks at runtime, not compile time. Not type safe example:
storing mixed types in a dict without validation and using
them without checking - the type system does not help.
Contrast: JavaScript `'a' + 1 = 'a1'` (weak typing) is
genuinely unsafe: the coercion silently produces a wrong
result with no error. Python refuses; JavaScript silently coerces.*

**Q2.** Java's type erasure means `List<String>` and
`List<Integer>` are the same type at runtime. This is
sometimes called a "type system leak." What problems
does this cause in practice, and what patterns have
Java developers developed to work around it?

*Hint: Problems: (1) Cannot create generic arrays (`new T[]`).
(2) Cannot use instanceof with generic types.
(3) Cannot pass `Class<T>` to a factory method (the `T`
is unknown at runtime). Workarounds: (1) Pass `Class<T>
clazz` as a parameter to factory methods and use `clazz.
cast()`. (2) Use `TypeToken` (Guava) or `ParameterizedType`
to capture type information at runtime. (3) Use `Class<T>`
as a reification token. Kotlin reified type parameters
(inlined functions) solve this for specific cases.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is type erasure in Java? What are its practical
implications?"**

*Why they ask:* Core Java knowledge. Explains why generic
code sometimes behaves unexpectedly.

*Strong answer includes:*
- Java generics were added in Java 5 (2004) as a compile-
  time feature for backward compatibility with Java 4 code.
  At compile time, `List<String>` enforces string-only
  access. At runtime, the JVM only sees `List` (raw type).
  The type parameter `<String>` is erased.
- Practical implications: (1) `obj instanceof List<String>`
  is a compile error (no `List<String>` exists at runtime).
  (2) Casting to parameterized type (`(List<String>) obj`)
  generates "unchecked cast" warning. (3) Cannot create
  generic arrays: `new T[10]` does not compile.
  (4) Cannot use type parameters in instanceof or new expressions.
- Workaround: pass `Class<T>` to capture the runtime type:
  `<T> T create(Class<T> type) { return type.newInstance(); }`

**Q2: "What is the difference between strongly typed
and statically typed? Is Python strongly typed?"**

*Why they ask:* Tests precision of understanding. Many
developers confuse these dimensions.

*Strong answer includes:*
- Static/dynamic: WHEN type checking occurs.
  Static = compile time (Java). Dynamic = runtime (Python).
- Strong/weak: WHETHER implicit coercion is allowed.
  Strong = no implicit coercion (Python, Java).
  Weak = implicit coercion (JavaScript, C).
- Python is dynamically typed (checks at runtime) AND
  strongly typed (rejects implicit coercions with TypeError).
  `'a' + 1` in Python: `TypeError: can only concatenate str (not "int") to str`.
- JavaScript is dynamically AND weakly typed.
  `'a' + 1 = 'a1'` - silently coerces `1` to `'1'` and concatenates.
- Java is statically AND strongly typed.
  `int x = "hello"` is a compile error (static).
  `(String) 5` is a compile error (strong).

**Q3: "How would you approach migrating a Python service
to a more type-safe codebase without a full rewrite?"**

*Why they ask:* Practical type system migration knowledge.
Common in teams adopting TypeScript or mypy.

*Strong answer includes:*
- Add type hints incrementally: start with function signatures
  for public API methods.
- Add mypy to the project: `pip install mypy`.
  Run `mypy . --ignore-missing-imports` to get an initial baseline.
- Enable strict mode gradually: `--disallow-untyped-defs`
  (all functions must have type hints), `--strict` (full strictness).
- Add mypy to CI to prevent type regressions.
- Use `TypeVar` for generic functions, `Protocol` for
  structural typing (interface-like types), `Union` for
  multi-type parameters, `Optional[T]` for nullable values.
- Timeline: 3-6 months for a 50K-line service to reach
  fully typed with mypy strict. Prioritize: API boundaries
  first (most value for type safety at ingress/egress),
  then core business logic, then utilities.
