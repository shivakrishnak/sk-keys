---
id: CSF-035
title: Type Inference
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-034
used_by: CSF-037, JLG-010
related: CSF-036, CSF-064
tags: [type-inference, var, hindley-milner, local-variable, diamond-operator]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/csf/type-inference/
---

⚡ TL;DR - Type inference lets the compiler deduce types
from context, removing boilerplate annotations. Java 10+
`var` is local-type inference. Kotlin/Haskell use full
Hindley-Milner inference. Trade-off: less verbosity
vs reduced readability in complex expressions.

| #035 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-034 (Type Systems) | |
| **Used by:** | CSF-037 (Generics), JLG-010 (Java var) | |
| **Related:** | CSF-036 (Structural vs Nominal Typing), CSF-064 (Type Theory) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Pre-Java 10 Java code is famously verbose for type annotations:
`HashMap<String, List<Map<String, Integer>>> data = new HashMap<String, List<Map<String, Integer>>>();`
The type is written TWICE: on the left (declaration) and
on the right (constructor call). Any change to the type
requires changing both sides. The diamond operator `<>`
(Java 7) helped with generics: `HashMap<String, List<Map<String, Integer>>> data = new HashMap<>()`.
But the declaration side still required the full type.

**THE BREAKING POINT:**

When iterating collections or working with lambdas, the
verbosity becomes noise that obscures intent:
`for (Map.Entry<String, List<Integer>> entry : map.entrySet())`
vs what the developer means: "for each entry in this map."
The type annotation adds no information the compiler does
not already know - it just forces the developer to repeat it.
Languages like Haskell and ML had solved this problem
decades earlier with Hindley-Milner type inference: the
compiler deduces types from usage, eliminating the need
for most annotations.

**THE INVENTION MOMENT:**

Hindley-Milner type inference (Robin Milner, 1978) was
the theoretical foundation. Haskell (1990) implemented
full type inference. Java lagged due to backward compatibility
and design philosophy (explicit types as documentation).
Java 10 (2018) introduced `var` for local variable type
inference - a narrowly scoped version: only for local
variables with initializers. Kotlin (from JetBrains, 2011)
adopted pervasive type inference from the start, making
explicit type annotations rare in well-written Kotlin code.

---

### 📘 Textbook Definition

Type inference is the ability of a compiler or type checker
to automatically deduce the types of expressions without
explicit type annotations from the programmer. Given
`x = 42` in a statically typed language with type inference,
the compiler infers `x: Int` from the literal value `42`
without requiring `Int x = 42`. Type inference is a compiler
feature, not a runtime behavior - the program still has
a fixed static type; the programmer just does not have
to write it.

**Java `var` (Java 10+, JEP 286):** Local variable type
inference. `var x = new ArrayList<String>()` infers
`x: ArrayList<String>`. Works only for local variables
with an initializer. NOT for method parameters, return
types, fields, or `null` initializers.

**Hindley-Milner (HM) inference:** Full whole-program type
inference algorithm used in Haskell, OCaml, and Kotlin.
HM infers types for entire programs including function
signatures. In Haskell: `add a b = a + b` infers `add :: Num a => a -> a -> a` automatically.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Type inference: the compiler deduces the type, so you don't
have to write it. Less boilerplate, same static safety.

**One analogy:**

> Autocomplete on a search engine. You type "java" and
> the engine infers you likely mean "Java programming
> language" from context. You don't have to type the full
> query - the context fills in the gap.
>
> Type inference is autocomplete for types. You write
> `var x = new ArrayList<String>()` and the compiler fills
> in: `x: ArrayList<String>`. You don't have to say it -
> the context makes it obvious. The type is still there;
> you just don't have to repeat what is already known.

**One insight:**

`var` in Java does NOT make Java dynamically typed.
The type of `var x = 42` is `int`, fixed at compile time.
`x = "hello"` after that is still a compile error.
`var` is syntactic sugar for "compiler, write the type for me."
The resulting bytecode is identical to `int x = 42`.
`var` is a writing convenience, not a type system change.

---

### 🔩 First Principles Explanation

**HOW THE COMPILER INFERS:**

```
┌──────────────────────────────────────────────────────┐
│ Constraint-based inference (simplified):             │
│                                                      │
│ var x = 42;                                         │
│ // Constraint: x must be the type of literal 42     │
│ // Literal 42 in Java has type int                  │
│ // Therefore: x: int                                │
│                                                      │
│ var list = new ArrayList<String>();                  │
│ // Constraint: list must be the type returned by    │
│ //   new ArrayList<String>()                        │
│ // That type is ArrayList<String>                   │
│ // Therefore: list: ArrayList<String>               │
│                                                      │
│ Hindley-Milner (full inference):                    │
│ def identity(x) = x                                 │
│ // Constraint: identity returns the same type it receives│
│ // Result: identity :: forall T. T -> T (polymorphic)│
└──────────────────────────────────────────────────────┘
```

**JAVA `var` RULES:**

```
┌──────────────────────────────────────────────────────┐
│ VALID uses of var:                                   │
│   var i = 0;                       // int            │
│   var name = "Alice";              // String         │
│   var list = new ArrayList<String>(); // ArrayList<> │
│   var entry = map.entrySet().iterator().next();      │
│                                                      │
│ INVALID uses of var:                                 │
│   var x;          // ERROR: no initializer           │
│   var x = null;   // ERROR: cannot infer from null   │
│   var x = () -> x + 1; // ERROR: lambda target type  │
│                         // cannot be inferred        │
│   // Not allowed for: method params, return types,   │
│   //                  fields, catch parameters       │
└──────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

**Gain:** Reduced verbosity. Readability improvement for
long generic types. Less duplication (type written once,
not twice).

**Cost:** Reduced readability when the type is non-obvious
(`var result = process(input)` - what is `result`?).
IDE becomes required to understand types. Harder code
review without IDE (reading a diff where `var` is used
requires mental inference of the type).

---

### 🧪 Thought Experiment

**GOOD vs BAD `var` USAGE:**

```java
// GOOD: type is obvious from the right-hand side
var list = new ArrayList<String>();
var map = new HashMap<String, Integer>();
var name = user.getName(); // clearly a String

// BAD: type is not obvious - var hurts readability
var result = process(config);  // what is result? Object? String? DTO?
var x = get();                  // completely opaque
var item = items.stream()
    .filter(i -> i.isActive())
    .findFirst()
    .orElseThrow();  // var hides that this is of type Item
```

**THE LESSON:**

`var` should be used where the type is obvious from the
initializer expression. If you have to hover in your IDE
to understand what type `var` resolves to, explicit type
annotation improves the readability of the code.
The goal of type inference is to remove NOISE, not remove
INFORMATION. When the type is the information, write it.

---

### 🎯 Mental Model / Analogy

**THE PRONOUN ANALOGY:**

Type inference is like using pronouns in natural language.
"Alice walked to the store. She bought milk." We do not
repeat "Alice" in the second sentence - the context makes
the pronoun "She" unambiguous. Similarly, `var list = new
ArrayList<String>()` - we don't repeat `ArrayList<String>`
on both sides; the context makes the type obvious.

But if you say "It did the thing," the pronoun is unhelpful
because "it" could refer to anything. Similarly, `var x =
process()` is unhelpful if the return type of `process()`
is not obvious from context.

**MEMORY HOOK:**

"`var` = let compiler write the obvious type. Not dynamic
typing - the type is fixed at compile time, you just
don't type it. Use `var` when the type is obvious from
the expression. Write the type when it is the documentation."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Type inference means the computer can figure out what kind
of thing a variable holds without you having to say it.
Like, if you say "I have 5 apples," the computer knows
that 5 is a number without you having to say "I have the
number 5, which is an integer."

**Level 2 - Student:**
Java 10 `var`: instead of writing `ArrayList<String> names = new ArrayList<>()`,
you can write `var names = new ArrayList<String>()`.
The compiler sees the right-hand side (`new ArrayList<String>()`)
and infers the type of `names`. The resulting code is
exactly the same at runtime.

**Level 3 - Professional:**
`var` in lambda parameters (Java 11): `(@NotNull var x) -> x.toUpperCase()`.
Allows annotations on lambda parameters (not possible with
the inferred form `x -> x.toUpperCase()`). The diamond
operator `<>` is a related but older inference mechanism:
`new HashMap<>()` instead of `new HashMap<String, Integer>()` -
the type parameters are inferred from the declared variable type.

**Level 4 - Senior Engineer:**
Kotlin's pervasive type inference: `val list = listOf("a", "b")`
infers `List<String>`. `val map = mutableMapOf<String, Int>()`
infers `MutableMap<String, Int>`. Function return types are
inferred when defined as expression functions: `fun double(n: Int) = n * 2`
infers return type `Int`. Kotlin's inference is based on
Hindley-Milner extended for object-oriented features.
The trade-off: Kotlin code often has NO explicit type
annotations on local variables or expression functions,
relying entirely on inference. This is idiomatic Kotlin;
requiring explicit types everywhere is non-idiomatic.

**Level 5 - Expert:**
Hindley-Milner type inference algorithm complexity: HM runs
in near-linear time for most programs. Pathological cases
(deeply nested polymorphic functions) can cause exponential
blowup - Haskell's type checker can run for minutes on
carefully constructed programs that trigger this. Java
deliberately chose limited `var`-based inference (not HM)
to guarantee O(1) type inference for any single variable
declaration - a compile-time performance guarantee.
Kotlin's HM implementation includes heuristics and fallbacks
that ensure practical performance even for complex programs.
The Java Language Specification explicitly states that
`var` resolution is intentionally simple: the inferred
type is exactly the type of the initializer expression,
with no complex constraint solving.

---

### ⚙️ How It Works (Formal Basis)

**JAVA `var` RESOLUTION (SIMPLE ALGORITHM):**

```
┌──────────────────────────────────────────────────────┐
│  var x = <expression>;                               │
│  1. Evaluate the type of <expression>                │
│  2. x has that type                                  │
│  Done. No constraint solving.                        │
│                                                      │
│  Examples:                                           │
│  var x = 42;          // expression type: int        │
│  var x = 42L;         // expression type: long       │
│  var x = "hello";     // expression type: String     │
│  var x = List.of(1,2);// expression type: List<Integer>│
│                                                      │
│  The type IS the most specific type of the RHS.      │
│  var list = new ArrayList<String>();                 │
│  // type: ArrayList<String> (not List<String>!)      │
└──────────────────────────────────────────────────────┘
```

**IMPORTANT SUBTLETY:**

`var list = new ArrayList<String>()` infers `ArrayList<String>`,
not `List<String>`. The inferred type is SPECIFIC to the
concrete class, not the interface. If you later call
`list.ensureCapacity(100)` (an `ArrayList`-specific method),
it compiles fine. If you write `List<String> list = new ArrayList<String>()`,
`list.ensureCapacity(100)` is a compile error (not on the
`List` interface). This specificity is a subtle behavior
difference between `var` and explicit interface-typed declarations.

---

### 🔄 System Design Implications

**`VAR` IN CODE REVIEW:**

`var` reduces the information visible in a code review
diff. A reviewer reading `var result = service.process(input)`
cannot tell the type of `result` without IDE access.
Team conventions for `var` usage matter: some teams allow
`var` everywhere; others restrict it to obvious constructors.
Google's Java style guide (as of Java 10 adoption) recommends
`var` for local variables where the type is obvious from
context; explicit types for non-obvious return values.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: `var` Reduces vs Hides Info**

```java
// BAD: var hides important type information
var result = factory.build(config);
// What is result? A User? A Config? An Optional?
// Must look up factory.build() signature to understand.

// GOOD: var for obviously-typed constructions
var users = new ArrayList<User>();
var connection = dataSource.getConnection();
var entry = map.entrySet().iterator().next();
// Type is clear from the right-hand side.

// GOOD: explicit type when type IS the documentation
List<String> names = fetchActiveUserNames();
Optional<User> adminUser = findAdminUser();
// Explicit types document what the caller expects to get.
```

**Example 2 - Diamond Operator vs `var`**

```java
// PRE-JAVA-7: full generic parameters on both sides
Map<String, List<Integer>> map =
    new HashMap<String, List<Integer>>();  // verbose

// JAVA 7+: diamond operator - infer right side from left
Map<String, List<Integer>> map = new HashMap<>();  // better

// JAVA 10+: var - infer left side from right
var map = new HashMap<String, List<Integer>>();  // even less typing
// But: inferred type is HashMap<String,List<Integer>> (concrete!)
// vs Map<String,List<Integer>> (interface) with diamond operator.

// For local variables where interface type matters:
List<String> names = new ArrayList<>();  // prefer when interface matters
var names = new ArrayList<String>();     // prefer when concrete impl is fine
```

---

### ⚖️ Comparison Table

| Aspect | Java `var` | Kotlin val/var | Haskell / ML |
|---|---|---|---|
| Scope | Local variables only | Local vars + properties + return types | Full program |
| Algorithm | Simple: type = RHS type | Extended HM | Hindley-Milner |
| Method param inference | No | No (explicit required) | Yes (full) |
| Return type inference | No | Yes (expression functions) | Yes |
| Readability impact | Moderate | Low (idiomatic) | High (no annotations) |
| Explicit override | Yes, always | Yes, always | Rarely needed |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `var` makes Java dynamically typed | No. `var` is purely a compile-time feature. The inferred type is FIXED at the declaration. `var x = 42; x = "hello"` is still a compile error. The bytecode is identical to `int x = 42`. |
| `var` infers the interface type (e.g., `List`) | No. `var list = new ArrayList<String>()` infers `ArrayList<String>` (the concrete class), NOT `List<String>`. This is more specific than what explicit `List<String>` would give. Be aware: calling `ArrayList`-specific methods on a `var` local works - calling them on an explicitly-typed `List` does not. |
| Type inference means no types | No. Every `var` has a static type - the compiler knows it precisely. The programmer just doesn't write it. The type system is as strict as with explicit annotations. |
| `var` works for method parameters and return types in Java | No. Java's `var` is restricted to local variables with initializers. Method parameters (`void foo(var x)`) and return types (`var foo()`) are NOT allowed. Kotlin allows type inference for single-expression function return types but not for multi-statement functions. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: `var` Infers Unexpected Concrete Type**

**Symptom:** Code using `var` has unexpected method
accessibility. `ensureCapacity()` available on inferred
`ArrayList` local but not expected. Or: trying to replace
`ArrayList` with `LinkedList` requires changes to all
`var` usage that calls `ArrayList`-specific methods.

**Root Cause:** `var` infers the concrete type of the RHS,
not the interface type. `var list = new ArrayList<String>()`
infers `ArrayList<String>`, not `List<String>`.

**Fix:** When the interface type matters for flexibility
or Liskov substitution principle, use explicit interface
type: `List<String> list = new ArrayList<String>()`.
Use `var` when you do not need to restrict to the interface.

**Failure Mode 2: `var` Cannot Infer from Null or Ambiguous Expressions**

**Symptom:** `var x = null` compilation error: "cannot
infer type for local variable x". Or: `var x = condition
? 1 : "hello"` compilation error because the ternary
has incompatible types.

**Root Cause:** `var` requires an unambiguous type from
the initializer. `null` has no type. A ternary with
incompatible branches has multiple possible common types.

**Fix:** Provide explicit type: `String x = null;`.
For ternary with incompatible types: restructure the code
or cast: `var x = condition ? 1 : (Object) "hello"`.

---

**Security Note:**

Type inference does not affect security directly.
However, `var` with loose semantics can OBSCURE security-
relevant types. Example: `var token = getToken()` - is
`token` a raw `String`, a `JWT`, a `SecureToken` wrapper?
If using domain types to enforce security invariants
(a `SafeHtml` type that can only be created via sanitization,
preventing XSS), using `var` on a `SafeHtml` value is fine -
the security guarantee is in the type. But `var token = service.
getToken()` obscures whether the token is validated or raw.
Team convention: use explicit types for security-sensitive
values where the type name communicates the security property.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Type Systems` (CSF-034) - understand static vs dynamic
  typing before understanding type inference

**Builds On This (learn these next):**
- `Generics and Parametric Polymorphism` (CSF-037) - diamond
  operator inference is a subset of generic type inference

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ DEFINITION   │ Compiler deduces types from context;   │
│              │ programmer omits obvious annotations    │
├──────────────┼─────────────────────────────────────────┤
│ JAVA VAR     │ Java 10+ local variable type inference  │
│              │ var x = expr; // type = type of expr    │
│              │ NOT for: params, returns, fields, null  │
├──────────────┼─────────────────────────────────────────┤
│ KEY RULE     │ var infers CONCRETE type (ArrayList),   │
│              │ NOT interface type (List)               │
├──────────────┼─────────────────────────────────────────┤
│ DIAMOND OP   │ Map<K,V> m = new HashMap<>();           │
│              │ Infers generic params from left side    │
├──────────────┼─────────────────────────────────────────┤
│ KOTLIN       │ Pervasive inference via extended HM     │
│              │ val list = listOf("a") // List<String>  │
├──────────────┼─────────────────────────────────────────┤
│ NOT DYNAMIC  │ var is compile-time; type is fixed      │
│              │ Same bytecode as explicit annotation    │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-037 (Generics), CSF-064 (Type Theory)│
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `var` in Java (10+) infers the type from the initializer
   expression - the type is FIXED at compile time. `var` is
   NOT dynamic typing. `var x = 42; x = "hello"` is a
   compile error. The bytecode is identical to `int x = 42`.
2. `var list = new ArrayList<String>()` infers `ArrayList<String>`
   (concrete class), NOT `List<String>` (interface). This means
   `ArrayList`-specific methods are accessible. When you
   need the interface type for flexibility, write it explicitly.
3. `var` is a readability tool: use it when the type is
   obvious from the initializer (constructors, factory methods
   with clear names). Avoid it when the type is the documentation
   (security-sensitive values, return types of complex methods).

**Interview one-liner:**
"Type inference lets the compiler deduce types, reducing
annotation verbosity without sacrificing static safety.
Java 10 `var` is local-variable-only inference. Key detail:
`var` infers the concrete type (ArrayList), not the interface
(List). `var` is not dynamic typing - the type is fixed at
compile time, exactly as if you wrote it explicitly."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Type inference is the principle of "don't repeat information
the compiler can derive." This appears throughout software:
default values (don't specify what the system can infer),
content negotiation (don't specify format when the system
can negotiate), schema inference (don't write the schema
when the tool can detect it). In each case, the underlying
contract exists and is enforced - you just don't have to
state the obvious. The risk in each case is the same: the
"obvious" inference may surprise you when it doesn't match
your intent. Type inference surprises (`var` infers concrete,
not interface); default value surprises (`null` vs `0`);
schema inference surprises (`2023-01-01` inferred as `date`
vs `string`). Explicit beats implicit when the implicit
behavior is unexpected.

**Where else this pattern appears:**

- **Kotlin `data class`** - Kotlin infers `equals()`,
  `hashCode()`, `toString()`, `copy()` for data classes.
  You don't write them; the compiler generates them from
  the properties. This is type-level inference: the compiler
  infers the behavior contract from the type structure.
- **SQL `RETURNING` clause** - Some ORMs infer the return
  type of a query from the SELECT clause structure. JPA's
  `@Query` with a projection interface - the framework
  infers what columns to fetch from the interface methods.
  Type inference applied to database query construction.
- **JSON Schema inference tools** - Tools like `quicktype`
  infer type definitions (TypeScript interfaces, Java classes)
  from sample JSON. The "type inference" here is from
  data structure, not code context. Same principle: the
  tool deduces the type so the developer doesn't have to.

---

### 💡 The Surprising Truth

Java's `var` was controversial when proposed (JEP 286).
Java developers and language designers debated whether it
was appropriate for a language that had always emphasized
explicit type declarations. One key concern: readability
in code reviews and without IDE assistance. The JEP authors
conducted surveys and found that approximately 90% of `var`
usages in Java code would be on clearly-typed initializers
(constructors, factory methods with descriptive names),
where the type is unambiguously obvious. The 10% ambiguous
cases were where developers would naturally write explicit
types. The final design decision: allow `var` everywhere
(within local variables) and rely on code review discipline,
rather than restricting `var` to specific syntactic contexts.
The same debate had been settled a decade earlier in Kotlin,
which made pervasive type inference idiomatic from day one.
Java's caution and late adoption reflects its philosophy:
evolution over revolution, never breaking existing code idioms.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[APPLY]** Identify 5 uses of `var` in a Java codebase
   where the type is obvious from context (constructors,
   factory methods) and 3 uses where explicit type would
   be clearer (method return values with non-descriptive
   names). Refactor each category appropriately.

2. **[EXPLAIN]** Explain the difference in inferred type
   between `var list = new ArrayList<String>()` (infers
   `ArrayList<String>`) and `List<String> list = new ArrayList<>()`
   (explicitly `List<String>`). Show a case where the difference
   matters (calling `ensureCapacity()` which is `ArrayList`-only).

3. **[COMPARE]** Compare Java `var`, Kotlin's pervasive
   type inference, and Haskell's full HM inference.
   For each: what is inferred, what must be explicit,
   and what is the readability impact.

4. **[DIAGNOSE]** Given `var x = null;` compilation error,
   explain why `null` cannot be the initializer for `var`
   and provide 2 alternative ways to declare a nullable
   local variable.

5. **[EVALUATE]** A team is debating whether to use `var`
   pervasively (Kotlin-style) or conservatively (explicit
   types except for long generics). Present the engineering
   trade-offs for each position. Include: code review
   tooling, IDE dependency, onboarding of new team members,
   and maintainability.

---

### 🧠 Think About This Before We Continue

**Q1.** `var` can be used in a for-each loop:
`for (var item : items) { ... }`. What type does `item`
have if `items` is a `List<String>`? If `items` is a
`List<? extends CharSequence>`? What happens if `items`
is an array `String[]`? Does `var` always resolve to
the most specific possible type?

*Hint: `List<String>` -> `item: String`. `List<? extends CharSequence>`
-> `item: CharSequence` (the compiler infers the capture
type). `String[]` -> `item: String`. `var` resolves to the
element type of the iterable - which for wildcards is the
captured bound. In all cases `var` gives the EXACT element
type, not `Object`. The key: `var` never widens unnecessarily.
It infers the most specific type available from the expression.*

**Q2.** Kotlin allows `var` and `val` at the class property
level (fields), while Java does not allow `var` for fields.
Why might this design choice have been made for Java?
What would be the implication of allowing `var` on Java fields?

*Hint: Field types in Java are part of the class's binary API.
The binary signature of a field is its type. If `var field = something()`
inferred from the constructor body, the field type would
depend on what method returns - creating a coupling between
the field's signature and the method's return type. The
field signature is inspected by: reflection, serialization,
external class loaders, code generators. Allowing `var` on
fields would make the API contract non-obvious and harder
to inspect without running code. Kotlin's approach: property
types can be inferred but are captured at compile time and
are visible in the compiled .class metadata.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is Java's `var` and what are its limitations?"**

*Why they ask:* Tests modern Java knowledge (Java 10+).
Common at senior level.

*Strong answer includes:*
- `var` is local variable type inference (JEP 286, Java 10).
  The compiler infers the variable type from the initializer.
  `var x = new ArrayList<String>()` infers `ArrayList<String>`.
- Limitations: (1) Local variables only - not method parameters,
  return types, fields, or catch clauses. (2) Must have an
  initializer. (3) Cannot initialize with `null` (no type
  to infer from). (4) Cannot use with array initializers
  without `new` (`var arr = {1,2,3}` is invalid).
  (5) Infers concrete type, not interface type.
- `var` is NOT dynamic typing. The type is fixed at compile
  time. The bytecode is identical to explicit annotation.

**Q2: "What is the diamond operator `<>` in Java?
Is it the same as `var`?"**

*Why they ask:* Tests understanding of two related but
distinct type inference mechanisms.

*Strong answer includes:*
- Diamond operator (Java 7, JEP 208): `new HashMap<>()` -
  the `<>` tells the compiler to infer the generic type
  parameters of the constructor from the CONTEXT (the
  declared variable type). `Map<String, Integer> map = new HashMap<>()` -
  the `<>` on `HashMap` is inferred as `<String, Integer>` from
  the declared `Map<String, Integer>` on the left.
- `var` (Java 10): `var map = new HashMap<String, Integer>()` -
  the type of the variable is inferred from the expression
  on the right. The expression must contain explicit generic
  parameters (or they're inferred from the expression).
- Key difference: diamond operator infers generic type PARAMS
  of a constructor from the left-hand declared type.
  `var` infers the type of the VARIABLE from the right-hand expression.
  They infer in opposite directions.
