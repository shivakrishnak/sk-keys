---
layout: default
title: "Type Systems (Static vs Dynamic)"
parent: "CS Fundamentals — Paradigms"
nav_order: 10
permalink: /cs-fundamentals/type-systems/
number: "0010"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Variables, Functions, Compiled vs Interpreted Languages
used_by: Strong vs Weak Typing, Java Language, TypeScript
related: Strong vs Weak Typing, Compiled vs Interpreted Languages, Type Inference
tags:
  - intermediate
  - foundational
  - mental-model
  - java
  - typescript
  - first-principles
---

# 010 — Type Systems (Static vs Dynamic)

⚡ TL;DR — A type system defines what kinds of data exist and when type errors are caught: statically at compile time (Java, TypeScript) or dynamically at runtime (Python, JavaScript).

| #010 | Category: CS Fundamentals — Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Variables, Functions, Compiled vs Interpreted Languages | |
| **Used by:** | Strong vs Weak Typing, Java Language, TypeScript | |
| **Related:** | Strong vs Weak Typing, Compiled vs Interpreted Languages, Type Inference | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In early machine code, a word in memory was just bits. You could
add two bits representing "a number" and "a text character"
— the CPU wouldn't object. The result would be meaningless garbage.
As programs grew, a function expecting a number might receive
a customer name. The program would continue silently, computing
nonsense until a crash or, worse, outputting wrong financial data.

**THE BREAKING POINT:**
Without types, every operation on every piece of data is
potentially wrong — and the programmer must manually track what
kind of data every variable holds. At scale, this is impossible.
A 100,000-line codebase where anyone can pass any data to any
function makes correctness analysis infeasible.

**THE INVENTION MOMENT:**
This is exactly why type systems were created. By attaching a
type to every value, the language can verify that operations
are meaningful: you can add two integers, but not an integer
and a string (unless the language explicitly defines that
operation). The debate between static and dynamic typing is
about WHEN this verification happens — and who pays the cost.

---

### 📘 Textbook Definition

A type system is a set of rules that associates a type (integer,
string, list, function) with every expression in a program and
constrains which operations can be applied to values of each type.
In a statically typed system (Java, C, TypeScript, Kotlin), types
are assigned to variables at compile time and type errors are
detected before execution. In a dynamically typed system (Python,
JavaScript, Ruby), types are associated with values at runtime
and type errors are detected only when the mismatched operation
is actually executed. Type inference (Kotlin, Haskell, modern
Java with `var`) allows static typing without explicit type
annotations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Static types: compiler catches type errors before you run the code. Dynamic types: errors appear at runtime.

**One analogy:**

> Static typing is like airport baggage rules declared upfront:
> "Only 23kg bags allowed." Overweight bags are caught at
> check-in — before the plane loads. Dynamic typing is like
> loading the plane first and discovering the overweight bag
> mid-flight. Both enforce limits; timing is the difference.

**One insight:**
Static types move errors from runtime to compile time — they're
bugs you catch for free, in your IDE, before deployment. The
cost is that you must declare types explicitly (or rely on type
inference). Dynamic types offer flexibility and speed of
prototyping at the cost of discovering type errors later and
harder to trace.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every value has a type — a category that determines which
   operations are valid on it. Even dynamically typed languages
   have types; they're just checked at runtime.
2. A type system's job is to prevent type errors — operations
   applied to values of the wrong type. The question is WHEN:
   before execution (static) or during (dynamic).
3. There is a fundamental tension between expressiveness and
   safety: a more restrictive type system catches more bugs but
   rejects more valid programs.

**DERIVED DESIGN:**
**Static typing:**
The compiler assigns types to every expression. Before generating
machine code, it checks every operation: "you're adding `int + String`
— that's invalid." This requires every variable's type to be
knowable at compile time — either explicitly annotated or
inferred. Result: a type-correct program is guaranteed not to
fail with a type error at runtime.

**Dynamic typing:**
Types are stored with values at runtime. `x = 42` stores the
integer value 42 along with a tag "int". When `x + "hello"` is
evaluated, Python checks at that moment: "can int + str?"
— and raises `TypeError`. Result: programs can be shorter
(no declarations), but type errors only appear when the code path
is executed.

**THE TRADE-OFFS:**
Static: Catches bugs early; IDE tooling (autocomplete, refactoring);
performance (types known to JIT); requires declarations
or inference; can be too restrictive.
Dynamic: Rapid prototyping; duck typing flexibility; shorter code;
type errors only at runtime; harder to maintain at scale.

---

### 🧪 Thought Experiment

**SETUP:**
A function `calculateTax(income)` is called in a codebase by
50 different callers. In one place, a developer passes a string
`"50000"` (from a form input) instead of the integer `50000`.

**WHAT HAPPENS IN DYNAMICALLY TYPED PYTHON:**
The code runs. `calculateTax("50000")` might succeed if the
function uses string multiplication internally (e.g., `"50000" * 0.20`
raises `TypeError`) — but only when that code path executes.
If the function is rarely called (quarterly report), the bug
lives undetected for months. When it fires, the stack trace
points to the middle of `calculateTax`, not the 50 callers.
Finding the wrong caller requires investigation.

**WHAT HAPPENS IN STATICALLY TYPED JAVA:**

```java
double calculateTax(double income) { ... }
calculateTax("50000");  // COMPILE ERROR: String not a double
```

The IDE shows a red underline at the call site immediately.
The error is caught before the code compiles, at the exact
location of the mistake, in the file of the developer who made
the error.

**THE INSIGHT:**
Static typing shifts the debugging cost from "runtime investigation"
to "compile-time red squiggle." For large codebases with many
callers, the static version's benefit compounds with scale.

---

### 🧠 Mental Model / Analogy

> Static typing is a strict recipe: "add 200g of sugar (type:
> weight)." The kitchen scale checks before you add anything —
> if you try to add "a handful" (wrong type), it refuses before
> baking begins. Dynamic typing is tasting as you go — the
> wrong ingredient (type error) is only discovered when the
> cake tastes wrong (runtime crash).

- "The kitchen scale checking before baking" → compile-time type check
- "Tasting as you go" → runtime type check
- "A handful vs. grams" → string vs. number type mismatch
- "The recipe" → function signature / type annotation
- "The cake tasting wrong" → runtime TypeError

Where this analogy breaks down: in real cooking, a scale
can't check all incompatibilities (wrong flavour combination);
type systems CAN check arbitrary compatibility constraints
through dependent types and contracts.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A type system is the language's way of keeping track of what
kind of data is in each variable — number, text, date, etc.
Static means the language checks this before you run the code
(like proofreading). Dynamic means it checks as the code runs
(like performing live and discovering a mistake mid-show).

**Level 2 — How to use it (junior developer):**
In Java, every variable has a declared type: `int count = 0;`
`String name = "";`. The compiler enforces this. In Python,
you just write `count = 0` — no declaration needed. Python 3.5+
adds optional type hints (`count: int = 0`) for tooling but
doesn't enforce them at runtime. TypeScript is JavaScript with
static types — you get compile-time checking but the output is
still JavaScript.

**Level 3 — How it works (mid-level engineer):**
Static type checkers perform type inference: they propagate
type information through expressions. `int x = 5; double y = x + 2.0`
— the compiler infers `x + 2.0` is `double` because `int +
double → double`. Modern languages (Kotlin, Scala, TypeScript)
infer types from assignment: `val x = "hello"` infers `x: String`.
Dynamic typed runtimes (CPython) store a type tag in every
object's header — `type(42)` reads the tag. Python's `isinstance`
checks the tag; type mismatch raises `TypeError`.

**Level 4 — Why it was designed this way (senior/staff):**
The type system design space is a fundamental trade-off in
language design. Hindley-Milner type inference (Haskell, ML,
Scala) provides full type inference with no type annotations,
unlike Java's partial inference. Gradual typing (TypeScript,
Python type hints) allows opting in incrementally — you annotate
what matters most and leave the rest dynamic. Dependent types
(Idris, Coq) allow types that depend on values (`Vector<n>` where
`n` is a runtime integer) — proving program correctness at the
type level. Java's generics are a deliberate compromise: they
provide static type safety but are erased at runtime (type
erasure), which is why `List<String>.class` is just `List.class`.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│       STATIC vs DYNAMIC TYPE CHECKING            │
├──────────────────────────────────────────────────┤
│                                                  │
│  STATIC (Java):                                  │
│  Source → [Compiler type check] → Bytecode       │
│            ↓ ERROR FOUND HERE                    │
│   "String cannot be applied to int parameter"    │
│                                                  │
│  DYNAMIC (Python):                               │
│  Source → [Interpreter runs line by line]        │
│            ↓ ERROR FOUND HERE (at runtime)       │
│   TypeError: unsupported operand type(s)         │
│   for +: 'int' and 'str'                         │
│                                                  │
│  GRADUAL (TypeScript):                           │
│  Source → [tsc type check] → JavaScript output   │
│            ↓ ERROR FOUND HERE (at build time)    │
│   Argument of type 'string' is not assignable    │
│   to parameter of type 'number'                  │
│   (Runtime JS has NO type checking)              │
└──────────────────────────────────────────────────┘
```

**Java type erasure (important detail):**
Java's generic types exist only at compile time. `List<String>`
becomes `List` in bytecode. At runtime, `instanceof List<String>`
is illegal — only `instanceof List` is valid. This is why you
can't write `new T[]` in a generic class — `T` is unknown at
runtime. Type erasure was a backwards-compatibility decision
(Java 1.4 code had to work with Java 5 generics).

**Python type checking:**
Every CPython object has `ob_type` — a pointer to its
type object. `type(42)` returns `<class 'int'>`. Operations
like `+` dispatch through the type's `__add__` method — if it
returns `NotImplemented`, Python tries the right-hand operand's
`__radd__`. If both return `NotImplemented`, Python raises `TypeError`.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (Static — Java):

```
[Developer writes: processAge(getUserName())]
  → [Compiler: getUserName() returns String]
  → [Compiler: processAge expects int]
  → [Type error ← YOU ARE HERE]
  → [Compile fails with error at the call site]
  → [Developer fixes before runtime]
```

FAILURE PATH (Dynamic — Python at runtime):
[processAge(getUserName())] calls with string "Alice"
→ [processAge runs: age * 2]
→ [TypeError: can't multiply sequence by non-int]
→ [Stack trace points to processAge internals]
→ [Developer must trace back to callsite]

**WHAT CHANGES AT SCALE:**
At 10x codebase size, static typing's benefit compounds — refactoring
a function's signature shows every affected caller immediately.
At 100x, TypeScript over JavaScript prevents entire classes of
production bugs. At 1000x (platform engineering), type correctness
across service boundaries requires API contracts — gRPC's Protobuf
or OpenAPI schemas provide cross-service static typing.

---

### 💻 Code Example

**Example 1 — Static vs dynamic: type error discovery:**

```java
// Java (static): compile-time error
public class PayrollService {
    public double computePay(double hoursWorked) {
        return hoursWorked * HOURLY_RATE;
    }
}

// This line fails at COMPILE TIME:
service.computePay("forty");  // Error: String not a double
```

```python
# Python (dynamic): runtime error
def compute_pay(hours_worked):
    return hours_worked * HOURLY_RATE

# This runs until this line is executed, THEN fails:
compute_pay("forty")  # TypeError: can't multiply str by float
# If this path is only exercised in a monthly report, bug
# may survive in production for weeks
```

**Example 2 — TypeScript gradual typing:**

```typescript
// BAD: any type — defeats static typing
function processUser(user: any) {
  console.log(user.nmae); // typo: 'nmae' not caught
}

// GOOD: explicit interface — typo caught at compile time
interface User {
  name: string;
  age: number;
}
function processUser(user: User) {
  console.log(user.nmae); // ERROR: Property 'nmae' does
  // not exist on type 'User'
}
```

**Example 3 — Type inference in Java (var):**

```java
// Before Java 10: explicit type required
HashMap<String, List<Integer>> scores =
    new HashMap<String, List<Integer>>();

// Java 10+ var: type inferred from right-hand side
var scores = new HashMap<String, List<Integer>>();
// Type is still HashMap<String, List<Integer>> — static,
// just without repetitive declaration
```

---

### ⚖️ Comparison Table

| Dimension          | Static (Java, TS)            | Dynamic (Python, JS)       | Gradual (TS, Python hints) |
| ------------------ | ---------------------------- | -------------------------- | -------------------------- |
| Type errors caught | Compile time                 | Runtime                    | Compile time (opt-in)      |
| Verbosity          | Higher                       | Lower                      | Configurable               |
| IDE tooling        | Excellent                    | Limited                    | Good with hints            |
| Refactoring safety | High                         | Low                        | Medium                     |
| **Best For**       | Large teams, long-lived code | Rapid prototyping, scripts | Migration, flexibility     |

How to choose: Use static typing for systems that must be
maintained long-term by large teams. Use dynamic typing for
scripts, rapid prototyping, and small codebases. Use gradual
typing (TypeScript) to add safety incrementally to existing
dynamic codebases.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                             |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| Python has no types                              | Python has types on every value; it's dynamically typed, meaning type CHECKING happens at runtime, not that types don't exist       |
| Static typing requires more code                 | Modern type inference (Kotlin `val`, TypeScript, Scala `val`) means static types often require no more syntax than dynamic types    |
| TypeScript is fully statically typed at runtime  | TypeScript types are erased during compilation to JavaScript — at runtime, TypeScript code is JavaScript with no type checks        |
| Java's generics provide full runtime type safety | Java generics are erased at runtime — `List<String>` becomes `List`; casting errors are only caught if explicit casts are attempted |

---

### 🚨 Failure Modes & Diagnosis

**1. Runtime Type Error in Dynamically Typed Code**

**Symptom:**
`TypeError: unsupported operand type(s)` or `AttributeError:
'NoneType' object has no attribute 'x'` in production; error
only appears for specific user inputs.

**Root Cause:**
A code path receives an unexpected type — a string where a
number was expected, or None where an object was expected.
Dynamic typing deferred this check to execution.

**Diagnostic:**

```bash
# Python: add type hints and use mypy for static analysis
pip install mypy
mypy app/service.py --ignore-missing-imports
# Shows type errors before runtime, like a static type checker

# Add runtime type guard for external data (API inputs)
from pydantic import BaseModel
class OrderInput(BaseModel):
    amount: float  # validates and converts on input
```

**Fix:**

```python
# BAD: assumes input is the right type
def process_order(amount):
    return amount * TAX_RATE  # TypeError if amount is a string

# GOOD: validate and convert at the boundary
def process_order(amount: float) -> float:
    if not isinstance(amount, (int, float)):
        raise TypeError(f"Expected number, got {type(amount)}")
    return float(amount) * TAX_RATE
```

**Prevention:** Validate all external inputs at system boundaries;
use Pydantic/dataclasses in Python, Zod in TypeScript.

**2. Type Erasure Causes ClassCastException (Java)**

**Symptom:**
`ClassCastException: class java.lang.String cannot be cast to
class java.lang.Integer` at runtime, inside generic code.

**Root Cause:**
An unchecked cast in generic code wasn't caught at compile time
because type erasure removed the generic type information.

**Diagnostic:**

```bash
# Compile with -Xlint:unchecked to expose unsafe casts
javac -Xlint:unchecked MyClass.java
# Shows warnings at lines where unchecked casts occur
```

**Fix:**

```java
// BAD: heap pollution — mixing raw and generic types
List list = new ArrayList();          // raw type
list.add("hello");
List<Integer> ints = (List<Integer>) list; // no warning!
int val = ints.get(0); // ClassCastException at runtime

// GOOD: use typed collections consistently
List<String> strings = new ArrayList<>();
strings.add("hello");
// List<Integer> ints = strings; // COMPILE ERROR — caught early
```

**Prevention:** Never use raw generic types; enable all compiler
warnings; use `@SuppressWarnings("unchecked")` sparingly and
document why.

**3. TypeScript `any` Defeats Type Safety**

**Symptom:**
TypeScript code compiles cleanly but throws runtime errors
that TypeScript should have caught; `any` type is widespread.

**Root Cause:**
`any` disables type checking — it's the "escape hatch" that
removes all guarantees.

**Diagnostic:**

```bash
# tsconfig.json: enable strict mode
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true  // errors on implicit 'any'
  }
}
npx tsc --noEmit  # type-check without emitting JS
```

**Fix:**

```typescript
// BAD: any defeats type checking
function processData(data: any) {
  return data.nmae.toUpperCase(); // typo not caught
}

// GOOD: specific type with interface
interface UserData {
  name: string;
  age: number;
}
function processData(data: UserData) {
  return data.nmae.toUpperCase(); // ERROR: 'nmae' not in UserData
}
```

**Prevention:** Enable `strict: true` in tsconfig; treat `any` as
a code smell requiring justification; use `unknown` instead of
`any` when type is genuinely unknown.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Variables` — types describe what a variable can hold
- `Functions` — parameter and return types are the function's contract
- `Compiled vs Interpreted Languages` — static typing is often associated with compilation

**Builds On This (learn these next):**

- `Strong vs Weak Typing` — a related but distinct dimension of type system design
- `TypeScript` — gradual typing for JavaScript
- `Generics` — parameterised types that extend static type systems

**Alternatives / Comparisons:**

- `Strong vs Weak Typing` — orthogonal axis: how strictly the language enforces types
- `Type Inference` — automatic static type deduction without explicit annotations
- `Dependent Types` — types that depend on values — the extreme of static typing

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ Rules associating types with values and │
│ │ when type errors are caught │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ Operations on wrong-type data produce │
│ SOLVES │ garbage or crashes; type system prevents │
│ │ this class of errors │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ Static ≠ verbose; dynamic ≠ typeless. │
│ │ The difference is WHEN errors are caught │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ Static: large teams, long-lived, complex │
│ │ Dynamic: scripts, prototyping, small teams│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ `any` in TypeScript defeats static typing;│
│ │ raw types in Java defeat generics safety │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ Static: early error detection + tooling │
│ │ vs. Dynamic: flexibility + less ceremony │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "Airport baggage check: static catches │
│ │ overweight at check-in, dynamic mid- │
│ │ flight." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strong vs Weak Typing → TypeScript │
│ │ → Type Inference → Generics │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Java's generics use type erasure — `List<String>` becomes
`List` at runtime. Python's type hints are also erased at runtime
(not enforced). Both languages are considered "statically typed"
or "supporting static typing." Define the precise criterion that
distinguishes whether a language's type system provides a
meaningful safety guarantee — and evaluate both Java generics
and Python type hints against that criterion.

**Q2.** A TypeScript function accepts `unknown` as its parameter
type. A Python function has no type annotation. Both can receive
any value. Trace the exact steps a developer must take in each
language to safely use the parameter's value — and explain why
`unknown` in TypeScript provides stronger guarantees than no
annotation in Python, even though both "accept anything."
