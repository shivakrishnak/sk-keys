---
id: CSF-039
title: Pattern Matching
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-038, CSF-034
used_by: JLG-015, JLG-016
related: CSF-036, CSF-037
tags: [pattern-matching, instanceof, switch-expressions, sealed-interfaces, exhaustiveness]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/csf/pattern-matching/
---

⚡ TL;DR - Pattern matching tests values against shapes
and binds matched parts to variables in one step. Java
evolved: `instanceof` patterns (16), switch expressions
(14-21), sealed exhaustiveness (17), guards (21).
Eliminates cast chains and null checks.

| #039 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-038 (Algebraic Data Types), CSF-034 (Type Systems) | |
| **Used by:** | JLG-015 (Sealed Interfaces), JLG-016 (Switch Expressions) | |
| **Related:** | CSF-036 (Structural vs Nominal), CSF-037 (Generics) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Pre-Java 16 type-dispatch code is a chain of `instanceof`
checks followed by explicit casts:

```java
Object obj = getValue();
if (obj instanceof String) {
    String s = (String) obj;      // check, then cast - verbose
    System.out.println(s.length());
} else if (obj instanceof Integer) {
    Integer i = (Integer) obj;    // again
    System.out.println(i * 2);
} else if (obj instanceof List) {
    List<?> list = (List<?>) obj; // again
    System.out.println(list.size());
}
```

The check and cast are always paired - the `instanceof`
check proves the type, then the cast REPEATS that assertion.
This is a two-step operation that should be one.

**THE BREAKING POINT:**

Visitor pattern in Java (the traditional solution for
type dispatch) requires: an interface with a `visit` method
for each type, a `accept` method on each type, a visitor
implementation class per operation. 40-60 lines of
boilerplate for what in a pattern-matching language is
5 lines. Complex type hierarchies (AST nodes, domain models
with many subtypes) become maintenance nightmares with
traditional instanceof chains or visitor pattern.

**THE INVENTION MOMENT:**

Pattern matching in functional languages (ML, Haskell,
1970s-90s) was the natural way to work with ADTs: destructure
values, match on shape, bind sub-values to names, check
exhaustiveness. Scala brought this to the JVM (2003).
Java adopted it incrementally: `instanceof` pattern (Java 16),
switch expressions (Java 14-21), sealed interface exhaustiveness
(Java 17), record deconstruction patterns (Java 21 preview/21).
Each step removed a class of boilerplate from Java code.

---

### 📘 Textbook Definition

Pattern matching is a mechanism that tests an expression
against one or more patterns, and when a match is found:
(1) extracts (destructures) components of the matched
value and (2) binds them to named variables in scope
for the matching branch. A pattern is a structural
description of what a value should look like.

**Java pattern types (as of Java 21):**
Type pattern: `obj instanceof String s` - matches if obj
is a String, binds to `s`.
Guarded pattern: `case String s when s.length() > 5` -
additional boolean condition.
Record deconstruction: `case Point(int x, int y)` - destructures
a record's components.
Exhaustiveness: switch on sealed interface without default
is compiler-verified to cover all variants.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pattern matching is: test the shape + extract the parts +
bind names - in ONE operation, with compiler-verified completeness.

**One analogy:**

> A sorting machine at a shipping company. Each parcel
> comes in on the conveyor belt. The machine checks the
> shape: is it a flat envelope (PATTERN 1)? Route to rack A.
> Is it a small box under 2kg (PATTERN 2)? Route to rack B.
> Is it a large heavy box (PATTERN 3)? Route to rack C.
>
> Without pattern matching: you check the shape (instanceof),
> then pick it up again (cast), then route it. Pattern
> matching does it in one motion: detect shape, extract
> details, act on them.

**One insight:**

Java's `instanceof` pattern (`if (obj instanceof String s)`)
uses "flow scope" - `s` is in scope and typed as `String`
ONLY in the `if` body. In the `else` branch, `s` doesn't
exist. The compiler ensures you never use `s` where
the match might not have succeeded. This is why it's
called "pattern matching" and not just "better instanceof":
the binding is SCOPED to the match, not dangerously
available everywhere.

---

### 🔩 First Principles Explanation

**THE EVOLUTION IN JAVA:**

```
┌──────────────────────────────────────────────────────┐
│ JAVA 14-15: switch expressions (preview then standard)│
│   int result = switch (day) {                        │
│     case MONDAY -> 1;                                │
│     case TUESDAY -> 2;                               │
│     default -> 0;                                    │
│   };  // switch is an expression (yields a value)    │
│                                                      │
│ JAVA 16: instanceof type pattern                     │
│   if (obj instanceof String s) {   // match + bind   │
│     println(s.length());  // s is String here        │
│   }                                                  │
│                                                      │
│ JAVA 17: switch on types + sealed exhaustiveness     │
│   switch (shape) {  // shape: sealed Shape           │
│     case Circle c    -> area(c);                     │
│     case Rectangle r -> area(r);                     │
│     // No default - compiler verifies all covered    │
│   }                                                  │
│                                                      │
│ JAVA 21: guarded patterns + record deconstruction    │
│   case Circle c when c.radius() > 10 -> "large";    │
│   case Point(int x, int y) when x == y -> "diagonal";│
└──────────────────────────────────────────────────────┘
```

**EXHAUSTIVENESS:**

```
┌──────────────────────────────────────────────────────┐
│ sealed interface Expr permits Num, Add, Mul {}       │
│ record Num(int value) implements Expr {}             │
│ record Add(Expr left, Expr right) implements Expr {} │
│ record Mul(Expr left, Expr right) implements Expr {} │
│                                                      │
│ int eval(Expr e) {                                   │
│   return switch (e) {                               │
│     case Num n       -> n.value();                   │
│     case Add(var l, var r) -> eval(l) + eval(r);     │
│     case Mul(var l, var r) -> eval(l) * eval(r);     │
│     // No default - ALL Expr variants covered        │
│   };                                                 │
│ }                                                    │
│ // Adding 'record Sub(Expr left, Expr right)' to     │
│ // Expr -> compile error here: Sub not handled       │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**ELIMINATING THE VISITOR PATTERN:**

Traditional Visitor for evaluating expressions:

```java
// OLD: 50+ lines for a simple eval function
interface ExprVisitor<T> { T visitNum(Num n); T visitAdd(Add a); }
interface Expr { <T> T accept(ExprVisitor<T> v); }
class Num implements Expr {
    int value;
    <T> T accept(ExprVisitor<T> v) { return v.visitNum(this); }
}
class EvalVisitor implements ExprVisitor<Integer> {
    Integer visitNum(Num n) { return n.value; }
    Integer visitAdd(Add a) { return a.left.accept(this) + a.right.accept(this); }
}
// ...plus Add, Mul classes with accept methods
```

With pattern matching on sealed ADTs:

```java
// NEW: 5 lines for the same logic
int eval(Expr e) {
    return switch (e) {
        case Num n -> n.value();
        case Add(var l, var r) -> eval(l) + eval(r);
        case Mul(var l, var r) -> eval(l) * eval(r);
    };
}
```

**THE LESSON:**

The Visitor pattern was invented to work around the absence
of pattern matching in mainstream OOP languages. With
Java 21 sealed interfaces + pattern matching, the Visitor
pattern is obsolete for closed type hierarchies. The pattern
matching switch IS the visitor, with exhaustiveness checking,
in a fraction of the code.

---

### 🎯 Mental Model / Analogy

**THE SQL CASE ANALOGY:**

SQL's `CASE WHEN x > 0 THEN 'positive' WHEN x < 0 THEN 'negative' ELSE 'zero' END`
is pattern matching on a value: test each condition, execute
the matching branch, return a value. Java's switch expression
is the same idea applied to types and shapes, with
the compiler ensuring all shapes are covered.

**MEMORY HOOK:**

"Pattern matching = test shape + extract + bind in ONE step.
Java 16: `instanceof` pattern. Java 17: type patterns
in switch + sealed exhaustiveness. Java 21: guards (`when`)
+ record deconstruction. No default = compiler exhaustiveness.
Replaces instanceof-chain, cast dance, and Visitor pattern."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Pattern matching is like sorting laundry: you look at each
item (match), see if it's a shirt (pattern), then hang it
up (bind). If it's socks, you fold them. You check all
types of clothing; if you miss one, the machine tells you.

**Level 2 - Student:**
`if (obj instanceof String s)` - instead of checking
`instanceof`, then casting separately, you do both in
one step. `s` is a `String` and available in the if-body.
`switch (shape) { case Circle c -> ...}` - match on type,
bind to variable `c` in the arm.

**Level 3 - Professional:**
Java 21 guards: `case String s when s.length() > 5 -> "long"`.
Guards add a boolean condition to the pattern match.
Record deconstruction: `case Point(int x, int y) when x > 0 && y > 0 -> "quadrant 1"`.
Destructures the record's components directly in the pattern.
Nesting: `case AddExpr(Num n, var right) when n.value() == 0 -> simplify(right)` -
pattern match on the type, destructure, add a guard. All in one case.

**Level 4 - Senior Engineer:**
Exhaustiveness with generics and nested seals. A `sealed interface
Visitor<T>` that dispatches on subtypes using pattern matching
can replace the classic double-dispatch Visitor pattern entirely.
The compiler verifies that all subtypes of a sealed hierarchy
are handled. In an interpreter or compiler front-end where
all AST node types are sealed, every traversal function
(eval, typecheck, print, optimize) is a `switch` expression
over the AST type - no visitor interface boilerplate, no
accept methods, just the logic.

**Level 5 - Expert:**
Java's pattern matching design was influenced by the need
to preserve compatibility. Java's existing `switch` statement
was NOT changed. A new switch EXPRESSION was added (Java 14).
Pattern matching switch expressions use `->` arms (no fall-through),
not `:` (with fall-through). This was a deliberate choice
to avoid the classic `switch` fall-through bug. The `->` arms
are single-expression or `{}` blocks; `break` is not needed.
This means Java has TWO switch syntaxes: the classic
(statement, `:`, fall-through) and the modern (expression, `->`,
no fall-through). Both continue to work; they are not
interchangeable. New code should use `->` switch expressions.

---

### ⚙️ How It Works (Formal Basis)

**FLOW SCOPE IN `instanceof` PATTERNS:**

```
┌──────────────────────────────────────────────────────┐
│  if (obj instanceof String s && s.length() > 5) {   │
│      println(s); // s definitely String here         │
│  }                                                   │
│                                                      │
│  // s is in scope only where obj is definitely String│
│  // Compiler tracks definite assignment via flow:    │
│  // - After instanceof String s: s is String         │
│  // - In else branch: s is NOT in scope              │
│  // - Can use in AND (&&) condition: short-circuit   │
│  //   ensures second clause only evaluates if true   │
│  // - CANNOT use in OR (||) condition: short-circuit │
│  //   might not evaluate instanceof                  │
│                                                      │
│  if (!(obj instanceof String s) || s.length() < 5) {│
│  // ERROR: s not in scope here - condition may be    │
│  //        true without instanceof matching          │
│  }                                                   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 System Design Implications

**COMMAND PATTERN WITH SEALED INTERFACES:**

A command bus where commands are sealed:

```java
sealed interface Command permits CreateUser, DeleteUser, UpdateEmail {}
record CreateUser(String name, String email) implements Command {}
record DeleteUser(UUID userId) implements Command {}
record UpdateEmail(UUID userId, String newEmail) implements Command {}

// Pattern matching dispatch - no dispatch table, no if-chains
CommandResult dispatch(Command cmd) {
    return switch (cmd) {
        case CreateUser(var name, var email) ->
            userService.create(name, email);
        case DeleteUser(var id) ->
            userService.delete(id);
        case UpdateEmail(var id, var email) ->
            userService.updateEmail(id, email);
        // Add new command type -> compile error here until handled
    };
}
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: instanceof Chain vs Pattern Matching**

```java
// BAD: check-then-cast dance, no exhaustiveness
Object shape = getShape();
double area;
if (shape instanceof Circle) {
    Circle c = (Circle) shape;  // redundant cast
    area = Math.PI * c.radius() * c.radius();
} else if (shape instanceof Rectangle) {
    Rectangle r = (Rectangle) shape;  // redundant cast
    area = r.width() * r.height();
} else {
    area = 0; // silent fallthrough for unknown types
}

// GOOD: pattern matching switch with exhaustiveness
// (assuming Shape is sealed: permits Circle, Rectangle)
double area = switch (shape) {
    case Circle c    -> Math.PI * c.radius() * c.radius();
    case Rectangle r -> r.width() * r.height();
    // No default needed - compiler ensures all variants covered
};
```

**Example 2 - Guards and Record Deconstruction (Java 21)**

```java
// Guards: additional conditions after pattern
String describe(Object obj) {
    return switch (obj) {
        case Integer i when i < 0  -> "negative integer";
        case Integer i when i == 0 -> "zero";
        case Integer i             -> "positive: " + i;
        case String s when s.isEmpty() -> "empty string";
        case String s  -> "string: " + s;
        case null -> "null";
        default   -> "unknown: " + obj.getClass().getSimpleName();
    };
}

// Record deconstruction: destructure record components
record Point(int x, int y) {}
record Line(Point start, Point end) {}

String classifyLine(Line line) {
    return switch (line) {
        // Destructure: extract start and end points
        case Line(Point(int x1, int y1), Point(int x2, int y2))
                when x1 == x2 -> "vertical line";
        case Line(Point(int x1, int y1), Point(int x2, int y2))
                when y1 == y2 -> "horizontal line";
        case Line(Point(int x1, int y1), Point(int x2, int y2))
                -> "diagonal line";
    };
}
```

---

### ⚖️ Comparison Table

| Feature | Java 14-15 | Java 16 | Java 17 | Java 21 |
|---|---|---|---|---|
| Switch expression (-> arms) | Preview | Standard | Standard | Standard |
| `instanceof` type pattern | - | Standard | Standard | Standard |
| Type patterns in switch | - | - | Standard | Standard |
| Sealed exhaustiveness | - | - | Standard | Standard |
| Guarded patterns (`when`) | - | - | Preview | Standard |
| Record deconstruction | - | - | - | Standard |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java 16 `instanceof` pattern replaces all `instanceof` use | `instanceof` patterns work only when you want to use the value after the check. `if (collection instanceof Set)` to check type without using the Set's methods doesn't need a pattern. Pattern binding `instanceof Set<?> s` is useful when you'll use `s`. Both forms coexist. |
| A `default` case in a sealed switch is safe as a catch-all | Using `default` in a switch over a sealed type defeats exhaustiveness. If a new variant is added to the sealed interface, the compiler will NOT report an error - the default silently handles it (likely incorrectly). Always omit `default` on sealed interface switches to get compile-time safety. |
| Pattern matching in Java 21 is the same as in Haskell | Java's pattern matching is less powerful. Java 21 supports type patterns, guard conditions, and record deconstruction. Haskell supports nested patterns on any algebraic type, list patterns, as-patterns (`@`), wildcard `_`. Java patterns work only on sealed types (for exhaustiveness) or any Object (for type tests without exhaustiveness). |
| Switch expressions replaced switch statements | Both exist. Switch EXPRESSIONS use `->` arms and return a value; no fall-through. Switch STATEMENTS use `:` arms with potential fall-through; classic behavior unchanged. For new code, prefer switch expressions. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Partial Match / Missing Default on Non-Sealed Type**

**Symptom:** `switch (obj)` over a non-sealed type (e.g.,
`Object` or a non-sealed interface) without a `default`
case causes a compilation error: "the switch expression
does not cover all possible input values."

**Root Cause:** A switch expression over a non-sealed type
cannot be exhaustive (the compiler cannot know all possible
types). A `default` or `case null` is required.

**Fix:** Add `default -> throw new IllegalArgumentException("Unexpected: " + obj)`.
Or, better: seal the type hierarchy so the compiler can
verify exhaustiveness without a default.

**Failure Mode 2: Guard Order Dependency**

**Symptom:** A switch with multiple guards for the same
type produces unexpected results for some inputs.

**Root Cause:** Switch cases with guards on the same type
are evaluated in ORDER. The first matching case wins.

```java
// BAD: wrong order - "positive" case matches before the "zero" special case
switch (n) {
    case Integer i when i >= 0 -> "non-negative";  // matches 0 and positive
    case Integer i when i == 0 -> "zero";           // never reached for 0!
    ...
}
// GOOD: more specific cases first
switch (n) {
    case Integer i when i == 0  -> "zero";         // checked first
    case Integer i when i > 0   -> "positive";
    case Integer i              -> "negative";
}
```

---

**Security Note:**

Pattern matching improves security by eliminating unguarded
casts. Before Java 16, code patterns like `((AdminUser) user).getSecretKey()`
without prior `instanceof` check could throw `ClassCastException`
at unexpected paths - but worse, if the wrong type was passed
deliberately (injection), the error-handling path might
leak sensitive information. Pattern matching forces the
type check and the cast to be atomic; there is no window
between them for manipulation. Additionally, exhaustive
switches on sealed types ensure that security-relevant
code (e.g., permission checks) MUST handle every permission
type. Adding a new permission type without handling it
is a compile error, not a silent miss.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Algebraic Data Types` (CSF-038) - sealed interfaces
  are what make switch exhaustiveness possible; understanding
  ADTs is prerequisite for understanding what pattern matching is matching ON
- `Type Systems` (CSF-034) - pattern matching is a type-system
  feature; type patterns test and cast in one operation

**Builds On This (learn these next):**
- `Sealed Interfaces in Java` (JLG-015) - the Java-specific
  implementation of sum types used as pattern matching targets
- `Switch Expressions` (JLG-016) - the switch expression
  syntax that enables pattern matching in Java

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ INSTANCEOF   │ if (obj instanceof String s) {...}       │
│ PATTERN      │ Binds s as String in if-body. Java 16+  │
├──────────────┼─────────────────────────────────────────┤
│ SWITCH EXPR  │ switch (shape) { case Circle c -> ...;} │
│ TYPE PATTERN │ Binds c as Circle in arm. Java 17+      │
├──────────────┼─────────────────────────────────────────┤
│ GUARD        │ case String s when s.length() > 5       │
│              │ Extra boolean condition. Java 21+        │
├──────────────┼─────────────────────────────────────────┤
│ RECORD DECON │ case Point(int x, int y) -> ...         │
│              │ Destructures record fields. Java 21+     │
├──────────────┼─────────────────────────────────────────┤
│ EXHAUSTIVE   │ No default on sealed type = compiler    │
│              │ verifies all variants handled            │
│              │ Adding variant -> compile error          │
├──────────────┼─────────────────────────────────────────┤
│ NEVER DO     │ default on sealed type switch           │
│              │ Defeats exhaustiveness; silent miss      │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-038 (ADTs), JLG-015 (Sealed)        │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Pattern matching combines test + extract + bind in one
   step: `instanceof String s` tests that `obj` is a String
   AND binds it to `s` - no separate cast needed.
   `s` is scoped to where the match is guaranteed true.
2. Switch expressions on sealed interfaces are exhaustive:
   omit `default` so the compiler verifies all variants
   are handled. Adding a variant to the sealed interface
   produces compile errors at all unhandled switches.
   This is the feature - use it deliberately.
3. Guards (`when`) add boolean conditions to pattern arms:
   `case String s when s.length() > 5`. Order matters:
   the first matching case wins. Put more specific (narrower)
   guards before general ones.

**Interview one-liner:**
"Pattern matching in Java tests a value's shape, extracts
its parts, and binds them to variables in one step.
Java 16: `instanceof` type patterns. Java 17: type patterns
in switch expressions with sealed exhaustiveness. Java 21:
guards (`when`) and record deconstruction. The key: switch
on sealed types without `default` gives compile-time exhaustiveness
- adding a variant is a compile error until all handlers are updated."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Pattern matching is the principle of "inspect and use in one
step, not two." This eliminates "check then use" duplication
throughout software. SQL's `CASE WHEN` expressions do the
same: test a condition, produce a value, without separate
if-then-else. Regular expressions with capture groups do
the same: test a pattern AND capture matched subgroups in
one operation. JSON Schema `oneOf` does the same: validate
the type AND extract the fields defined for that type.
The deeper pattern: test-and-bind is always safer than
test-then-bind-separately because there is no window between
the test and the bind for the value to change.

**Where else this pattern appears:**

- **Rust's `match` expression** - Rust's `match` is the most
  complete pattern matching in mainstream systems languages.
  `match result { Ok(value) => use(value), Err(e) => handle(e) }`.
  Exhaustiveness is required for `match` - all variants
  must be handled. Rust's ownership model interacts with
  pattern matching: matching a value MOVES it out of the
  variable in some cases. Java's version is simpler (no
  ownership) but follows the same structure.
- **Kotlin `when` expression** - Kotlin's `when` is its
  equivalent: `when (shape) { is Circle -> ...; is Rectangle -> ... }`.
  Smart casts: after `is Circle`, Kotlin automatically casts
  the variable to `Circle` without explicit pattern binding.
  This is structural typing + pattern matching: "if it IS
  this type, treat it as this type." Similar to Java's
  `instanceof` pattern but without the explicit binding name.
- **TypeScript discriminated unions + narrowing** - TypeScript
  narrows types in `if` and `switch` branches based on
  type guards: `if (shape.kind === 'circle') { shape.radius ... }`.
  After the `kind === 'circle'` check, TypeScript NARROWS
  the type to `Circle` automatically. This is pattern matching
  via the type system without special syntax.

---

### 💡 The Surprising Truth

Java's switch statement has had fall-through behavior (execution
continues to the next case unless `break` is used) since
Java 1.0 (1995), based on C's switch. Fall-through is the
source of thousands of Java bugs: developers forget `break`,
the code continues executing the next case, producing
unexpected results. This was so well-known that it was
a required Java interview question: "What is switch fall-through?"
When Java added switch EXPRESSIONS (Java 14), the designers
had the opportunity to change this. They chose to add a
NEW syntax (`->` arrow cases) instead of changing the existing
syntax. `->` arms do NOT fall through; `break` is not needed.
The existing `:` syntax continues to fall through as before.
This means Java has two switch syntaxes with completely
different semantics. The backward-compatibility commitment
was so strong that rather than fix the old behavior,
Java added a new, better form. Developers learning Java
today encounter both forms and must understand that `->` (expression)
vs `:` (statement) behaves fundamentally differently.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[REFACTOR]** Take a method with 5 sequential `instanceof`
   checks followed by casts and refactor it to a switch
   expression with type patterns. Ensure the type hierarchy
   is sealed (if applicable) and remove the `default` case
   to get compiler exhaustiveness.

2. **[WRITE]** Write a method that evaluates a simple
   arithmetic expression tree where `Expr` is sealed
   (`Num`, `Add`, `Sub`, `Mul`, `Div` variants as records).
   Use record deconstruction patterns. Add a `Div by zero`
   check using a guard.

3. **[VERIFY]** Add a new variant to a sealed interface
   that is used in pattern matching switches in 3 different
   places in the codebase. Verify that the compiler reports
   errors at all 3 places. Fix all errors.

4. **[EXPLAIN]** Explain Java's flow scope for `instanceof`
   patterns: why `s` is in scope in the if-body but NOT
   in the else-body. Why `&&` works with patterns but
   `||` does not (for scoping). Give a code example of each.

5. **[EVALUATE]** Given an existing codebase that uses the
   Visitor pattern for processing a hierarchy of 6 AST node
   types, evaluate whether migrating to sealed interfaces
   + pattern matching is worthwhile. Identify the steps
   of the migration and any risks.

---

### 🧠 Think About This Before We Continue

**Q1.** A switch expression over a `sealed interface Shape permits
Circle, Rectangle` has no `default` case and is
exhaustive. A new deployment adds `Triangle implements Shape`
to the classpath without recompiling the class with the
switch expression. What happens at runtime when a `Triangle`
reaches the switch?

*Hint: This is the sealed hierarchy runtime violation.
At compile time, the switch was exhaustive. At runtime,
if a `Triangle` instance (from a new JAR added to the classpath
without recompiling the switch class) reaches the switch,
Java 17+ will throw `MatchException` (or `IncompatibleClassChangeError`
in older implementations). The sealed contract is verified
at compile time; adding a new implementing class from a
different JAR without recompiling the switch violates the
sealed contract. In practice: sealed hierarchies should
be in the same module/package as the consuming code; if
sealed types are part of a library API, all consumers
should be recompiled when the library changes the sealed hierarchy.*

**Q2.** Pattern matching in a `switch` expression evaluates
cases in ORDER. Given:
```java
switch (n) {
    case Integer i when i > 0  -> "positive";
    case Integer i when i > 10 -> "large positive";
    default -> "other";
}
```
For `n = 15`, what is the result? Why? How should the cases be ordered?

*Hint: `n = 15` matches the FIRST case `when i > 0` (15 > 0 is true).
Result: "positive". The second case (`when i > 10`) is
never reached for 15 because the first case already matched.
CORRECT ORDER: most specific (narrower) first:
`case Integer i when i > 10 -> "large positive"` (first),
then `case Integer i when i > 0 -> "positive"` (second).
This way, 15 matches "large positive"; 5 matches "positive".*

---

### 🎯 Interview Deep-Dive

**Q1: "What is pattern matching in Java? When was it introduced?"**

*Why they ask:* Tests modern Java knowledge. Common for
candidates claiming Java 11+ expertise.

*Strong answer includes:*
- Pattern matching is a mechanism that tests a value's shape,
  extracts components, and binds them to variables in one step.
- Java timeline: `instanceof` type patterns in Java 16
  (JEP 394). Type patterns in switch expressions + sealed
  exhaustiveness in Java 17 (JEP 441 preview, finalized 21).
  Guarded patterns (`when`) and record deconstruction patterns
  in Java 21 (JEP 441).
- `instanceof` pattern: `if (obj instanceof String s)` -
  tests type AND binds without separate cast. `s` is scoped
  to the if-body (flow scope).
- Switch pattern: `switch (shape) { case Circle c -> ... }` -
  dispatch on type + bind in one arm. On sealed types:
  exhaustiveness enforced by compiler.

**Q2: "What is exhaustiveness in switch expressions and why does it matter?"**

*Why they ask:* The core benefit of sealed types + pattern matching.
Tests design thinking.

*Strong answer includes:*
- Exhaustiveness: a switch expression on a sealed interface
  WITHOUT a `default` case must handle ALL permitted types.
  The compiler rejects the switch expression if any variant
  is unhandled.
- Why it matters: adding a new variant to the sealed interface
  produces compile errors at EVERY unhandled switch.
  The type system propagates the "you need to handle this new case"
  message through the entire codebase automatically.
- Without exhaustiveness (using `default`): a new variant is
  silently handled by the default case. If the default throws
  an exception, it's a runtime error. If the default returns
  a fallback value, it's a silent behavioral regression.
- Best practice: NEVER put `default` on a switch over a sealed
  type unless you genuinely want to ignore future variants.

**Q3: "Replace a traditional instanceof chain and Visitor pattern
with pattern matching. Show before and after."**

*Why they ask:* Tests practical refactoring ability.
Common in code review discussions.

*Strong answer includes:*
- Before (instanceof chain):
  ```java
  if (shape instanceof Circle) { ... (Circle) shape ... }
  else if (shape instanceof Rectangle) { ... (Rectangle) shape ... }
  else throw new IllegalStateException("Unknown: " + shape);
  ```
- After (switch expression, assuming sealed):
  ```java
  double area = switch (shape) {
      case Circle c    -> Math.PI * c.radius() * c.radius();
      case Rectangle r -> r.width() * r.height();
  };
  ```
- Visitor pattern before: requires `accept(Visitor)` on each
  type + visitor interface + visitor implementation. 40+ lines.
- Visitor pattern after: one switch expression, 5 lines.
  No boilerplate. No double dispatch. Exhaustiveness checked.
  Adding a shape type: compile error at the switch, not a
  silent visitor miss.
