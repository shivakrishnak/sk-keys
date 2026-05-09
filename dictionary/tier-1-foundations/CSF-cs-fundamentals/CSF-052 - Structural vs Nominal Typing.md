---
id: CSF-052
title: Structural vs Nominal Typing
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - deep-dive
  - tradeoff
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /csf/structural-vs-nominal-typing/
---

# CSF-052 - Structural vs Nominal Typing

⚡ TL;DR - Nominal typing: types match by name (must declare); structural typing: types match by shape (if it has the right methods/fields, it qualifies). Both are static; they differ in what makes types compatible.

| CSF-052         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-012, CSF-038, CSF-051             |                 |
| **Used by:**    | CSF-069, CSF-076                      |                 |
| **Related:**    | CSF-012, CSF-038, CSF-051, CSF-069    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In pure nominal systems, you can't use a third-party class with
your interface even if it has all the right methods — it just
doesn't declare `implements YourInterface`. In pure structural
systems, you can accidentally use the wrong type if two types
happen to have the same shape but different semantics.

**THE BREAKING POINT:**
Java: a library `Point` class with `getX()` and `getY()` can't
be used as `Coordinate` interface without modifying it or wrapping it.
Python duck typing: `len(obj)` works for strings, lists, dicts
— any object with `__len__`. If two unrelated types accidentally
have the same methods, structural typing can accept the wrong one.

**THE INVENTION MOMENT:**
Simula/Java used nominal: types must explicitly declare their
hierarchy. ML/Haskell used structural-style: matching is by type
structure. Go made structural typing explicit in a nominally-typed
staticly-typed language: its interfaces are structural — any type
with the right methods satisfies the interface without declaration.

**EVOLUTION:**
TypeScript uses structural typing: two types are compatible if
they have the same shape, regardless of name. Go interfaces
are structural. Rust traits are nominal (must `impl Trait for Type`).
Modern languages often blend: TypeScript has nominal-like
brand patterns when structural gives too much flexibility.

---

### 📘 Textbook Definition

**Nominal typing** (or _nominative typing_): type compatibility
is determined by explicit name-based declarations. Two types
are compatible only if one is declared to extend or implement
the other. **Structural typing** (or _duck typing_ in static form):
type compatibility is determined by the actual structure (fields
and methods). Two types are compatible if they have the same shape,
regardless of their names or inheritance relationships.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Nominal: types match by declared name/hierarchy; structural: types match by having the same shape/methods.

**One analogy:**

> Nominal typing is a private club with a guest list: you must
> be on the list to enter. Structural typing is a dress code:
> if you're wearing the right outfit, you get in, regardless of
> your name. Both are enforced at the door (compile-time),
> but the criteria differ.

**One insight:**
Structural typing is more flexible (works with third-party types
not on your "list") but less precise (accidentally admits
unrelated types that happen to dress the same). Nominal typing
is more precise but requires declaring every relationship.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Nominal: subtype = declared subtype; must explicitly state `implements/extends`.
2. Structural: subtype = same shape; no declaration needed.
3. Both can be enforced at compile-time (static typing).
4. Structural allows ad-hoc polymorphism without modifying existing types.
5. Nominal allows intentional incompatibility despite identical shape.

**DERIVED DESIGN:**

- **Java** — nominal: must `implements Runnable`; two identical-shaped types are different
- **Go** — structural interfaces: `io.Reader` satisfied by anything with `Read([]byte) (int, error)`
- **TypeScript** — structural: `{name: string}` is compatible with `{name: string, age: number}` (subtype)
- **Rust** — nominal traits: must `impl Display for MyType`; same methods don't help without impl
- **Python** — duck typing: dynamic structural; no compile-time check
- **C# 9+ records** — structural equality but nominal type identity

**THE TRADE-OFFS:**
**Nominal:** Intentional; explicit; refactoring-safe; prevents accidental compatibility.
**Structural:** Flexible; works with third-party libraries; less boilerplate for adapters.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Types need a compatibility model.
**Accidental:** Java's inability to retroactively add interface declaration to third-party types;
TypeScript's need for "branded types" to simulate nominal when structural is too permissive.

---

### 🧪 Thought Experiment

**SETUP:**
You have `UserId` (a String) and `ProductId` (a String).
Both are semantically distinct but structurally identical.

**STRUCTURAL (TypeScript, problem):**

```typescript
type UserId = string;
type ProductId = string;
function deleteUser(id: UserId) { ... }
const productId: ProductId = "prod-123";
deleteUser(productId); // COMPILES! No error -- wrong type passed
```

**NOMINAL (branded type, TypeScript workaround):**

```typescript
type UserId = string & { readonly __brand: "UserId" };
type ProductId = string & { readonly __brand: "ProductId" };
function makeUserId(s: string): UserId {
  return s as UserId;
}
const productId = makeProductId("prod-123");
deleteUser(productId); // NOW a compile error!
```

**NOMINAL (Java, clean):**

```java
record UserId(String value) {}
record ProductId(String value) {}
void deleteUser(UserId id) { ... }
deleteUser(new ProductId("prod-123")); // compile error!
```

**THE INSIGHT:**
When types are semantically distinct even if structurally
identical, nominal typing is safer. Structural typing makes
Accidental compatibility a real risk.

---

### 🧠 Mental Model / Analogy

> Nominal typing is like having a passport: your identity is
> official, declared, and traceable. Structural typing is like
> a job skill test: if you can do the tasks, you qualify,
> regardless of your official credentials. For some roles
> ("can you write code?") the skill test is better. For
> others ("is this person a US citizen?") the passport is
> essential.

**Element mapping:**

- Passport = nominal type declaration (`implements Interface`)
- Skill test = structural type check (has the right methods)
- Official credentials = inheritance/impl declaration
- Anonymous skill match = structural compatibility

Where this analogy breaks down: type compatibility is checked
at compile time by a deterministic algorithm; passport checks
have human judgement.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Nominal: a type is what it says it is. Structural: a type is
what it does. Like identifying a person by their passport
(nominal) vs by their job skills (structural).

**Level 2 - How to use it (junior developer):**
In Java: all type compatibility is nominal; no surprise compatibility.
In TypeScript: structural compatibility is the default; use
"branded types" or `class` (not `interface`) when you need
nominal. In Go: write small interfaces; any type with the
right methods satisfies them without declaration.

**Level 3 - How it works (mid-level engineer):**
TypeScript structural subtyping: type `{name: string, age: number}`
is a subtype of `{name: string}` because it has all the fields
of the supertype (plus more). This is called _width subtyping_.
Functions are contravariant in parameters and covariant in
return types: `(Animal -> void) <: (Dog -> void)` because a
function that handles any animal can handle a Dog.

**Level 4 - Why it was designed this way (senior/staff):**
Go's structural interfaces were designed to enable composition
across independently-developed packages. `io.Reader` in the
standard library can be satisfied by any third-party code
without that code depending on the `io` package. This enables
a form of retroactive abstraction: you can write a function
that works with any existing type that happens to have the
right methods, without requiring those types to know about you.

**Expert Thinking Cues:**

- TypeScript `interface` is structural; `class` is nominal. Use class when accidental compatibility is a concern.
- When designing Go APIs: small interfaces (1-2 methods) are powerful structural contracts.
- When a bug is caused by the wrong type accepted: was structural typing too permissive?

---

### ⚙️ How It Works (Mechanism)

**TypeScript structural check:**

```typescript
interface Printable {
  print(): void;
}
class Dog {
  print() {
    console.log("Woof!");
  }
}
// Dog satisfies Printable structurally (no declaration)
const d: Printable = new Dog(); // OK!

// But also:
class SecurityToken {
  print() {
    return "secret";
  }
}
const t: Printable = new SecurityToken(); // OK structurally
// Even if semantically wrong!
```

**Go structural interfaces:**

```go
type Reader interface { Read(p []byte) (n int, err error) }
// os.File satisfies Reader (without declaring it)
var r Reader = os.Stdin // OK: os.File has Read method
// net.Conn also satisfies Reader
// bytes.Buffer also satisfies Reader
// All without any import dependency on "io"
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Go structural):**

```
func process(r io.Reader) { ... }  ← YOU ARE HERE
  -> compiler: does arg have Read([]byte) (int, error)?
     os.File: yes -> compatible (no import of io needed)
     bytes.Buffer: yes -> compatible
     MyCustomReader: yes -> compatible
     string: no -> compile error
```

**FAILURE PATH:**

- Accidental structural compatibility: wrong type accepted silently
- TypeScript: `{id: number}` accidentally compatible with `UserId = {id: number}` — use branded types
- Go: large interface (10+ methods) impossible to satisfy without explicit design

---

### ⚖️ Comparison Table

| Language   | Typing                                                    | Interface Satisfied By      | Safety Profile                    |
| ---------- | --------------------------------------------------------- | --------------------------- | --------------------------------- |
| Java       | Nominal                                                   | Explicit `implements`       | High: no accidental compatibility |
| Rust       | Nominal traits                                            | Explicit `impl Trait`       | High                              |
| Go         | Structural interfaces                                     | Any type with right methods | Flexible; small interfaces safe   |
| TypeScript | Structural                                                | Shape compatibility         | Risk of accidental compatibility  |
| Python     | Duck (dynamic structural)                                 | Runtime shape check         | Runtime errors                    |
| Scala      | Both (nominal classes, structural types with `{ def m }`) | Declared or structural      | Flexible                          |

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                              |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| "Structural = dynamic typing"            | TypeScript and Go use structural static typing; shapes checked at compile time                                       |
| "Nominal = always safer"                 | Both have trade-offs; nominal requires adapter boilerplate for third-party types                                     |
| "Go interfaces are like Java interfaces" | Go: structural (no declaration); Java: nominal (must declare `implements`)                                           |
| "TypeScript classes are nominal"         | TypeScript class instances have structural compatibility too (unlike Java); only private members add nominal flavour |
| "Duck typing is structural typing"       | Duck typing is usually dynamic (Python); structural typing is static (TypeScript, Go)                                |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Accidental Structural Compatibility**
**Symptom:** Function accepts wrong type silently; bug from semantic mismatch.
**Root Cause:** Structural types with same shape but different semantics.
**Fix:** Use branded/opaque types; or use nominal types (class in TS, struct in Go).

**Mode 2: Nominal Adapter Boilerplate**
**Symptom:** Wrapper class needed for every third-party type to satisfy interface.
**Root Cause:** Nominal typing can't retroactively adopt third-party types.
**Fix:** Consider whether structural typing is more appropriate for your use case.

**Mode 3: Go Large Interface Not Satisfied**
**Symptom:** Compile error: type X does not implement LargeInterface (missing methods).
**Root Cause:** Large interface makes structural satisfaction harder; too many methods.
**Fix:** Split into smaller interfaces; compose them where needed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-012 - Type Systems (Static vs Dynamic)]]
- [[CSF-038 - Interfaces vs Abstract Classes]]

**Builds On This (learn these next):**

- [[CSF-069 - Type System Design for Large Codebases]]
- [[CSF-076 - Type Theory (System F, HM Inference)]]

**Alternatives / Comparisons:**

- Duck typing (Python) = dynamic structural
- Branded types (TypeScript) = simulated nominal in structural system

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Nominal=compatible by name declaration;│
│                 Structural=compatible by shape/methods│
│ PROBLEM         Rigid nominal hierarchies vs accidental │
│ IT SOLVES       structural compatibility               │
│ KEY INSIGHT     Structural: flexible, third-party works;│
│                 Nominal: intentional, no accidents    │
│ USE WHEN        Nominal: domain types with same shape  │
│                 Structural: composing unrelated libs  │
│ AVOID WHEN      Large structural interfaces;           │
│                 structural for semantically distinct  │
│                 identically-shaped types              │
│ TRADE-OFF       Flexibility (structural) vs safety     │
│                 (nominal)                            │
│ ONE-LINER       Nominal=be named; Structural=look right│
│ NEXT EXPLORE    CSF-069, TypeScript branded types      │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Nominal typing: compatible by name declaration; structural typing: compatible by shape/methods.
2. Go interfaces are structural (no `implements` needed); Java interfaces are nominal (must declare).
3. Structural types risk accidental compatibility; use branded types when shape alone isn't enough.

**Interview one-liner:**
"Nominal typing requires explicit declaration of type relationships (Java `implements`); structural typing accepts any type with the right shape/methods without declaration (TypeScript, Go); both are static — they differ in what constitutes compatibility."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Choose structural typing when you want flexibility and
retrospective compatibility. Choose nominal typing when you
want to prevent accidental compatibility between semantically
distinct types. The same principle applies to: HTTP API versioning
(structural: same schema = compatible), database schema evolution
(structural: same columns = compatible), and microservice contracts.

**Where else this pattern appears:**

- **GraphQL** — structural: a query matches any type with the requested fields
- **JSON Schema validation** — structural: any JSON matching the schema is valid
- **Kubernetes API** — structural: spec-compatible objects are valid regardless of source

---

### 💡 The Surprising Truth

Java is nominally typed, but the JVM itself uses structural
typing internally. When the JVM verifies bytecode, it checks
that method calls have the right parameter shapes — regardless
of the class name. The JVM's `invokevirtual` instruction works
structurally: any class with the right method signature at the
right offset in its vtable will work, even if the class wasn't
known at compile time. Nominal type checking is a _compiler_
safety layer; the runtime is structurally based.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** In TypeScript, `interface A { x: number }` and
`interface B { x: number }` are compatible: you can assign
an `A` to a `B` variable. But in Java, two interfaces with
the same methods are incompatible unless one extends the other.
What would break in Java if it used structural typing?

_Hint:_ Consider two Java interfaces: `Closeable` and
`AutoCloseable` both have `close() throws Exception`. In
structural typing, any class with `close()` satisfies both.
Is this desirable?

**Q2 (Scale):** A large TypeScript codebase with structural
typing has 500 interfaces. A developer changes one interface
to add a required field. How many types does this potentially
break, and how does structural typing's "compatibility by shape"
make this analysis different from a nominal (Java) codebase?

_Hint:_ In TypeScript, any type that _used to_ satisfy the
interface now fails (missing the new field). How do you find
all types? Is `TypeScript strict null checks` relevant here?

**Q3 (Design Trade-off):** Rust uses nominal traits: you must
`impl Display for MyType` explicitly. Go uses structural interfaces:
any type with the right methods qualifies. Both are statically
typed systems. When would you choose Rust's nominal approach
over Go's structural approach for a new system, and why?

_Hint:_ Think about a security-sensitive context where accidental
interface satisfaction could be a security vulnerability.
