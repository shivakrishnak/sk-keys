---
id: CSF-036
title: Structural vs Nominal Typing
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-034, CSF-015
used_by: CSF-037, CSF-038
related: CSF-035, CSF-064
tags: [structural-typing, nominal-typing, duck-typing, type-compatibility, typescript]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/csf/structural-vs-nominal-typing/
---

⚡ TL;DR - Nominal typing (Java): types compatible only
if explicitly declared related. Structural typing (Go,
TypeScript): types compatible if they have the same
shape. Java approximates structural typing with interfaces
and sealed types.

| #036 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-034 (Type Systems), CSF-015 (Polymorphism) | |
| **Used by:** | CSF-037 (Generics), CSF-038 (ADTs) | |
| **Related:** | CSF-035 (Type Inference), CSF-064 (Type Theory) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Imagine two independently developed libraries. Library A
defines `interface Flyable { void fly(); }`. Library B
defines `class Eagle { public void fly() {...} }`.
`Eagle` from Library B can fly - it has the `fly()` method.
But in a nominally-typed system (Java), `Eagle` is NOT
a `Flyable` unless Library B explicitly declares
`class Eagle implements Flyable`. If Library B's developer
did not know about Library A's `Flyable` interface, they
cannot declare the relationship retroactively without
modifying Library B.

**THE BREAKING POINT:**

In large ecosystems with many libraries, nominal typing
creates coordination friction: for types from different
libraries to be compatible, either they must have been
designed with that compatibility in mind, or you need
adapter wrappers. Working with JSON/maps/DTOs from external
APIs is painful nominally: you have to map the external
data to your own types explicitly, even if the structure
is identical. Python's duck typing sidesteps this: any
object with the right methods works, regardless of declared
type hierarchy.

**THE INVENTION MOMENT:**

Duck typing (informally named after "if it walks like
a duck and quacks like a duck, then it must be a duck")
was the dynamic typing approach to structural compatibility.
TypeScript (2012) formalized it as STATIC structural typing:
TypeScript's type checker verifies shape compatibility at
compile time without requiring explicit interface declarations.
Go (2012) independently introduced implicit interface
implementation: if a type has the methods of an interface,
it implements the interface - no `implements` keyword.
These formalizations brought the flexibility of duck typing
to statically checked systems.

---

### 📘 Textbook Definition

**Nominal typing** (name-based): Two types are compatible
if and only if they are declared to be compatible through
explicit inheritance or interface declaration. Types are
identified by NAME. Java, C++, C# use nominal typing.
`class B extends A` or `class B implements InterfaceA`
is required; having the same structure is insufficient.

**Structural typing** (shape-based): Two types are compatible
if they have the same structure (same fields and methods
with compatible types). Types are identified by STRUCTURE.
TypeScript, Go, Haskell type classes use structural or
structural-like typing.

**Duck typing:** The dynamic typing equivalent of structural
typing - at runtime, if an object has the right methods,
it is compatible. No type declarations needed. Python, Ruby.

Java approximates structural typing through explicit interfaces
(a class implements an interface to declare shape compatibility)
and, in Java 17+, sealed interfaces with pattern matching
(which give exhaustive structural analysis of a type hierarchy).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Nominal typing: "I am what I declare to be." Structural
typing: "I am what I look like." If it has the right
methods and fields, it's compatible - no declaration needed.

**One analogy:**

> Nominal: a passport. You are a citizen of France because
> your passport says "Republic of France." Even if you
> speak French, live in France, and have all the attributes
> of a French citizen - without the declaration in the
> document, you are not recognized as a French citizen.
>
> Structural: a job description. "Must be able to write
> code, design systems, and communicate with stakeholders."
> Anyone who CAN do those things qualifies, regardless of
> what their CV title says. If you have the skills (structure),
> you match the role.

**One insight:**

Go is nominally-defined but structurally-assigned.
In Go, you define an interface: `type Stringer interface { String() string }`.
Any type that has a `String() string` method implements
`Stringer` - no `implements Stringer` needed. This is
Go's structural typing: the interface is defined nominally,
but satisfaction is checked structurally. Java requires
the declaration (`implements Stringer`). This single
difference dramatically affects how library interoperability
works.

---

### 🔩 First Principles Explanation

**THE COMPATIBILITY QUESTION:**

Both systems answer: "Can value of type A be used where
type B is expected?"

```
┌──────────────────────────────────────────────────────┐
│ NOMINAL (Java):                                      │
│   Can Eagle be used as Flyable?                      │
│   Check: does Eagle declare "implements Flyable"?    │
│   NO -> incompatible, even if Eagle has fly() method │
│                                                      │
│ STRUCTURAL (TypeScript):                             │
│   Can EagleType be used as FlyableType?              │
│   Check: does EagleType have all properties/methods  │
│           required by FlyableType?                   │
│   YES (if fly() matches) -> compatible               │
│   No declaration needed.                             │
└──────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

**Nominal gains:** Explicit, intentional relationships.
The developer declares "this class IS-A that interface" -
it is a design decision, not an accident. Two classes with
the same methods are NOT compatible unless explicitly
related - this prevents unintended coupling between
types that happen to share method signatures.

**Nominal costs:** Requires upfront coordination. Cannot
make a third-party class implement your interface without
modifying its source. Verbose (must write `implements` for
every interface). Adapter pattern overhead.

**Structural gains:** Flexibility. Third-party types
automatically satisfy interfaces they structurally match.
No upfront coordination needed. Natural fit for data
transformation (JSON/maps) and protocol-agnostic code.

**Structural costs:** Accidental compatibility. Two types
with the same structure but different semantics (`User` and
`Product` both having `id: string` and `name: string`)
are considered compatible, which may not be intended.
A change in one type accidentally changes compatibility
with others.

---

### 🧪 Thought Experiment

**ACCIDENTAL COMPATIBILITY IN STRUCTURAL TYPING:**

```typescript
// TypeScript - structural typing
interface User { id: string; name: string; }
interface Product { id: string; name: string; }

function displayUser(user: User) {
    console.log(`User: ${user.name}`);
}

const product: Product = { id: "p1", name: "Widget" };
displayUser(product);  // COMPILES in TypeScript!
// User and Product are structurally identical ->
// they are compatible -> displayUser accepts a Product.
// This is accidental compatibility - structurally fine,
// semantically wrong.
```

**THE LESSON:**

In structural typing, identical structure = compatibility.
This is powerful when you WANT it (any object with the
right shape works for a function). It can cause bugs
when types with different semantics happen to share the
same structure. Java's nominal typing would reject this:
`Product` does not `implements User`, so they are not
compatible - even if their fields are identical.
For domain modeling where semantic correctness matters,
nominal typing provides an extra safety layer.

---

### 🎯 Mental Model / Analogy

**THE ELECTRICAL OUTLET ANALOGY:**

Nominal: a specific outlet for a specific plug type.
A USB-C plug only works in a USB-C outlet, even if physically
it would fit in a similar-shaped port. The compatibility
is declared and enforced by design standard.

Structural: a universal adapter. If the physical shape
fits and the voltage/current requirements match, the device
works, regardless of which country or standard the outlet
was designed for.

**MEMORY HOOK:**

"Nominal = by name/declaration. Structural = by shape.
Java = nominal (must declare `implements`). TypeScript = structural
(shape match is enough). Go = structurally-satisfied interfaces.
Duck typing = runtime structural check (Python)."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Nominal typing: you are what your ID card says. Structural
typing: you are what you can do. A bird without a "bird"
ID card would fail nominal typing, but if it can fly and
sing, structural typing accepts it as a bird.

**Level 2 - Student:**
In Java (nominal), to make `Eagle` work as `Flyable`,
you MUST write `class Eagle implements Flyable`. In TypeScript
(structural), if `Eagle` has a `fly()` method with the
right signature, it is automatically compatible with any
`Flyable` type - no declaration needed.

**Level 3 - Professional:**
TypeScript's structural typing enables "duck typing at
compile time." A common pattern: instead of creating an
interface class hierarchy for every third-party API response,
define an interface for what you need and rely on structural
compatibility. Any object with the right shape satisfies
the interface. This dramatically reduces boilerplate for
JSON API responses and data transfer objects.

**Level 4 - Senior Engineer:**
Java sealed interfaces (Java 17+) bring a form of structural
analysis to Java's nominal system. `sealed interface Shape
permits Circle, Rectangle, Triangle` explicitly enumerates
all valid subtypes. Combined with `instanceof` pattern
matching in a `switch` expression, the compiler verifies
EXHAUSTIVENESS: all cases covered. This is a nominally-
declared type hierarchy with structural analysis (switch
expressions must handle all declared shapes). The compiler
gives an error if a new shape is added but not handled
in switch expressions.

**Level 5 - Expert:**
TypeScript's excess property checking is a notable quirk
of structural typing. When assigning an OBJECT LITERAL
directly to a typed variable, TypeScript performs excess
property checking: extra properties not in the interface
cause a compile error. But when assigning a VARIABLE with
an object type, excess properties are allowed (pure structural
compatibility). This is a pragmatic heuristic: object literals
likely indicate a typo (wrote `colour` instead of `color`);
variables represent data from external sources where extra
properties are expected. It is not type theory - it is
practical UX for a structural type system.

---

### ⚙️ How It Works (Formal Basis)

**TYPE COMPATIBILITY CHECK:**

```
┌──────────────────────────────────────────────────────┐
│ NOMINAL (Java):                                      │
│   isCompatible(A, B):                                │
│     return A == B                                    │
│         || A extends B (via class hierarchy)         │
│         || A implements B (via interface list)       │
│   -> Linear check on declared hierarchy              │
│                                                      │
│ STRUCTURAL (TypeScript):                             │
│   isCompatible(A, B):                                │
│     return all properties of B exist in A           │
│         AND each property type is compatible        │
│   -> Recursive shape comparison                      │
│   Excess properties in A: allowed (not extra-checking)│
│   Missing properties in A: rejected                  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 System Design Implications

**JAVA INTERFACES AS STRUCTURAL APPROXIMATION:**

Java achieves a form of structural typing through interfaces:
define an interface for the shape you need; any class that
implements it satisfies the contract. The limitation:
the class must be aware of your interface and declare it.
Third-party classes cannot satisfy your interface without
wrappers (Adapter pattern). This is why Java heavily uses
the Adapter pattern for third-party integration where Go
or TypeScript would just use structural compatibility directly.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Nominal vs Structural in TypeScript**

```typescript
// NOMINAL-STYLE (Java thinking in TypeScript):
// Bad: forcing explicit inheritance for compatibility
class HttpUser {
    constructor(public id: string, public name: string) {}
}
class GraphQLUser extends HttpUser {} // forced hierarchy
// Coupling two data sources via inheritance - wrong design

// STRUCTURAL (idiomatic TypeScript):
// Good: define an interface for what you need
interface HasName { name: string; }

function greet(entity: HasName) {
    console.log(`Hello, ${entity.name}`);
}

// ALL of these are compatible - no declarations needed:
const httpUser = { id: "u1", name: "Alice", email: "a@b.com" };
const dbRow = { name: "Bob", createdAt: new Date() };
const apiResp = { name: "Charlie", status: "active", score: 99 };

greet(httpUser);  // compatible: has 'name'
greet(dbRow);     // compatible: has 'name'
greet(apiResp);   // compatible: has 'name'
// No class hierarchy needed. Any object with 'name' works.
```

**Example 2 - Java Sealed Interfaces for Exhaustive Type Handling**

```java
// Java 17+: sealed interface + pattern matching
// Nominal declaration, exhaustiveness enforced structurally
sealed interface Shape permits Circle, Rectangle, Triangle {}

record Circle(double radius) implements Shape {}
record Rectangle(double width, double height) implements Shape {}
record Triangle(double base, double height) implements Shape {}

// Compiler enforces ALL cases are handled:
double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t -> 0.5 * t.base() * t.height();
        // NO default needed - compiler verifies all permits are covered
        // If Triangle is added to permits but not to switch -> compile error
    };
}
```

---

### ⚖️ Comparison Table

| Aspect | Nominal (Java) | Structural (TypeScript) | Implicit (Go) |
|---|---|---|---|
| Compatibility determined by | Declared hierarchy | Shape match | Method set match |
| Third-party compatibility | Requires adapter | Automatic if shape matches | Automatic if methods match |
| Accidental compatibility | Not possible | Possible (same shape, different semantics) | Possible (same methods, different semantics) |
| Refactoring safety | High (compiler tracks relationships) | Medium (shape changes ripple) | Medium |
| Verbosity | High (`implements`, `extends`) | Low (no declaration needed) | Low (no `implements`) |
| Design intent clarity | High (explicit decisions) | Lower (implicit) | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java has no structural typing | Java approximates structural typing through interfaces. If you define an interface that captures the structure you need, and classes implement it, you achieve structural-like flexibility. The limitation is the declaration requirement - third-party classes cannot retroactively implement your interface without modification. |
| Structural typing is always better for flexibility | Structural typing enables accidental compatibility: two unrelated types with the same shape are compatible. In domain-driven design, `User` and `Product` might both have `id: string, name: string` but should NEVER be used interchangeably. Nominal typing prevents this accidental substitution. For domain models, nominal is safer. |
| TypeScript is fully structural | TypeScript performs excess property checks on object literals (not purely structural). When assigning an object literal directly, extra properties cause a compile error - even though purely structural typing would allow them. This is a pragmatic exception to pure structural compatibility. |
| Go interfaces require an `implements` keyword | Go has NO `implements` keyword. Interface satisfaction in Go is purely implicit: if your type has all the methods of an interface, it implements the interface. This is Go's structural implementation of interfaces. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: TypeScript Accidental Compatibility**

**Symptom:** A function accepting `UserDTO` accidentally
accepts a `ProductDTO` at compile time (both have `id` and
`name` properties). A product is displayed in the user UI.

**Root Cause:** TypeScript's structural typing: both types
have the same shape. The compiler cannot distinguish between
semantically different types that happen to share structure.

**Fix:** Use branded/nominal types in TypeScript for
domain types that must not be accidentally compatible:

```typescript
// Branded types - prevent accidental compatibility
type UserId = string & { readonly __brand: "UserId" };
type ProductId = string & { readonly __brand: "ProductId" };

function getUser(id: UserId): User {...}
const productId = "p1" as ProductId;
getUser(productId);  // Compile error: ProductId is not UserId
```

**Failure Mode 2: Java Adapter Pattern Overhead**

**Symptom:** Third-party library's `Event` class cannot be
used with your `Message` interface even though it has all
required methods.

**Root Cause:** Java nominal typing - `Event` does not
declare `implements Message`.

**Fix:** Adapter wrapper - create a wrapper class that
implements your interface and delegates to `Event`:

```java
// Adapter: wraps third-party Event to satisfy Message interface
class EventAdapter implements Message {
    private final Event delegate;
    EventAdapter(Event event) { this.delegate = event; }
    @Override public String getPayload() {
        return delegate.getData(); // delegate to third-party
    }
}
```

---

**Security Note:**

Structural typing can create security issues if type identity
is used as an authorization check. Example (TypeScript):
`function adminAction(user: AdminUser)` - if `AdminUser`
is just `{ role: "admin", id: string }`, any object with
`role: "admin"` and `id` satisfies the type - including
user-controlled input. NEVER rely on TypeScript structural
type compatibility for authorization. Always verify authorization
at runtime against the database/identity provider, not
against TypeScript types (which are compile-time only
and erased at runtime). TypeScript types are a development
tool, not a runtime security boundary.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Type Systems` (CSF-034) - static/dynamic, strong/weak
  typing must be understood before structural/nominal distinction
- `Polymorphism` (CSF-015) - structural typing enables
  a form of polymorphism without explicit hierarchy

**Builds On This (learn these next):**
- `Generics` (CSF-037) - generic type constraints interact
  with both structural and nominal type systems
- `Algebraic Data Types` (CSF-038) - sealed interfaces
  in Java bring structural exhaustiveness to nominal types

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ NOMINAL      │ Compatible by NAME/declaration          │
│              │ Java: must declare `implements`         │
│              │ Explicit, intentional relationships     │
├──────────────┼─────────────────────────────────────────┤
│ STRUCTURAL   │ Compatible by SHAPE (same methods/fields)│
│              │ TypeScript: shape match = compatible    │
│              │ Flexible; risk of accidental compat.   │
├──────────────┼─────────────────────────────────────────┤
│ GO           │ Implicit interface satisfaction         │
│              │ Have the methods? You implement it.     │
│              │ No `implements` keyword needed          │
├──────────────┼─────────────────────────────────────────┤
│ JAVA SEALED  │ Nominal declaration + structural check  │
│              │ sealed interface + permits              │
│              │ Pattern matching exhaustiveness          │
├──────────────┼─────────────────────────────────────────┤
│ TRADE-OFF    │ Nominal: safe for domain types           │
│              │ Structural: flexible for data transfer  │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-037 (Generics), CSF-038 (ADTs)      │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Nominal typing (Java): compatible if explicitly declared
   related (`implements`, `extends`). Two classes with
   identical methods are NOT compatible unless declared so.
   Safe for domain types; prevents accidental substitution.
2. Structural typing (TypeScript, Go): compatible if shapes
   match. Any object with the right methods/fields qualifies.
   Flexible for data transfer and protocol-agnostic code;
   risk of accidental compatibility between unrelated domain types.
3. Java approximates structural typing through interfaces.
   Java sealed interfaces (Java 17+) enable exhaustiveness
   analysis over a nominal type hierarchy - the compiler
   verifies that all `permits` types are handled in switch expressions.

**Interview one-liner:**
"Nominal typing (Java): compatible only if explicitly
declared. Structural typing (TypeScript, Go): compatible
if shapes match. Java uses nominal typing - `implements`
is mandatory - which prevents accidental type substitution
but requires adapters for third-party types. Go and TypeScript
use implicit/structural compatibility - flexible but
can cause accidental coupling between semantically different
types that share the same structure."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The structural vs nominal debate maps directly to the
tension between "contracts by convention" and "contracts
by declaration." This appears in many engineering decisions:
REST API response compatibility (structural: if the JSON
has the right fields, it works; nominal: if the Content-Type
matches the expected schema). Database schema evolution
(structural: if the columns exist, queries work; nominal:
explicit schema versioning). Protocol compatibility
(structural: if the packet format matches; nominal: explicit
protocol version negotiation). When designing APIs and
data contracts: use nominal (explicit versioning) for
breaking changes; use structural (shape compatibility)
for backward-compatible extensions.

**Where else this pattern appears:**

- **CSV/JSON data processing** - When processing JSON
  from external APIs, you work structurally: "extract the
  fields I need from this object." The API returns an object
  with 50 fields; you need 3. You don't check the type name
  of the JSON object - you extract by field name. This is
  structural compatibility in practice, used every day in
  data processing regardless of language type system.
- **Database ORMs** - ORM column mapping is structural:
  if the class has a field matching the column name (and
  type), the ORM maps it. The class does not need to
  declare itself as "this table's entity" in most modern
  ORMs beyond a basic `@Entity` annotation. Spring Data JPA's
  projections are structural: define an interface with
  getters matching column names; Spring generates the mapping.
- **Go's `io.Reader` / `io.Writer`** - Go's standard library
  uses implicit interfaces. `io.Reader` is `Read(p []byte) (n int, err error)`.
  Any type implementing that method signature works as an
  `io.Reader`. Files, network connections, in-memory buffers,
  compression streams - all compatible without declaring
  `implements io.Reader`. This is structural typing enabling
  the entire Go ecosystem to be composable without coordination.

---

### 💡 The Surprising Truth

TypeScript is not the only statically-typed language with
structural typing. The Go language specification explicitly
describes Go's interface system as structural: "A type
implements any interface comprising any subset of its
methods." This was a deliberate design choice at Google
that came from the Go designers' frustration with Java's
interface system: when building large systems at Google,
they frequently encountered situations where a type from
one package needed to satisfy an interface from another
package, requiring explicit declarations and coupling.
Go's structural interfaces eliminated this: the interface
and the implementing type are decoupled at the source level.
Two teams can evolve their types independently; compatibility
emerges from structure, not from shared interface declarations.
This design decision influenced Rust's trait system,
Swift's protocols, and TypeScript's type checker - all of
which use structural or structural-like compatibility checks.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Given a Java class `Eagle` with a `fly()`
   method and an interface `Flyable` with a `fly()` method,
   explain why `Eagle` is NOT a `Flyable` in Java without
   an explicit `implements Flyable` declaration. Contrast
   with how Go and TypeScript would handle the same situation.

2. **[DEMONSTRATE]** In TypeScript, create two interfaces
   `User` and `Product` that are structurally identical.
   Write a function that accepts `User` and call it with
   a `Product`. Show that TypeScript accepts the call.
   Then use branded types to prevent this accidental compatibility.

3. **[APPLY]** Given a Java service that wraps a third-party
   `HttpResponse` class (no source modification possible)
   to satisfy an internal `ApiResponse` interface,
   implement the Adapter pattern to bridge nominal incompatibility.

4. **[DESIGN]** Using Java 17+ sealed interfaces and pattern
   matching, model a payment processing result that can be
   `Success`, `Failure`, or `Pending`. Write a switch expression
   that handles all cases exhaustively. Add a new `Cancelled`
   case and show the compile error that requires updating
   all switches.

5. **[EVALUATE]** A team is building a data pipeline that
   processes records from 5 different external APIs with
   similar but not identical JSON structures. Evaluate:
   should the pipeline use structural typing (TypeScript/Python)
   or nominal typing (Java with explicit DTOs)? Justify
   the choice based on: type safety, maintainability,
   and evolution of the external API schemas.

---

### 🧠 Think About This Before We Continue

**Q1.** In TypeScript, the following compiles:
`interface A { x: number }; interface B { x: number; y: string }`.
`function f(a: A) {}; const b: B = {x:1, y:"s"}; f(b)`.
B has an extra property `y` but is compatible with A.
Now try: `f({ x: 1, y: "s" })` - an inline object literal
with the same shape as B. Does this compile? Why or why not?

*Hint: `f(b)` compiles because TypeScript's structural typing
allows B (which is a superset of A's shape) to be used
where A is expected. `f({ x: 1, y: "s" })` triggers TypeScript's
excess property checking: when an OBJECT LITERAL is assigned
directly to a type, TypeScript rejects extra properties
(`y` is not in A). This is a TypeScript pragmatic exception
to pure structural typing - object literals are checked
more strictly than variables to catch likely typos.*

**Q2.** Go's interface system is structural. Java's is nominal.
Both are statically typed. Which approach is better for
a large organization building dozens of microservices
that communicate via a shared service mesh?

*Hint: Large organization with microservices. Arguments
for Go structural: teams can evolve types independently;
a new service can satisfy existing interfaces without
coordination; less coordination overhead across teams.
Arguments for Java nominal: explicit interface declarations
make API contracts visible and intentional; accidental
structural compatibility across microservices is prevented;
contract versioning is cleaner (declare `implements V2Api`
for the new contract). Real-world answer: both work.
gRPC's Protobuf uses field numbers (structural compatibility:
if field numbers match, message is compatible across versions).
This is structural typing at the IDL level, regardless
of whether the implementation is Java or Go.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between structural and nominal
typing? Which does Java use?"**

*Why they ask:* Advanced type systems knowledge. Tests
whether the candidate understands the type system deeply.

*Strong answer includes:*
- Nominal: compatibility by declaration. Types are compatible
  if explicitly linked via `extends`/`implements`. Java.
  `Eagle` is `Flyable` only if `class Eagle implements Flyable`.
- Structural: compatibility by shape. Types are compatible
  if they have the same fields and methods. TypeScript, Go.
  If `Eagle` has `fly()`, it satisfies any type requiring `fly()`.
- Java uses nominal. This means: explicit interface declarations
  are required; third-party classes need adapter wrappers to
  satisfy your interfaces; accidental compatibility between
  semantically different types is prevented.
- Java sealed interfaces (17+) bring structural EXHAUSTIVENESS
  analysis to the nominal system: the compiler knows all
  subtypes of a sealed interface and enforces that switch
  expressions handle all cases.

**Q2: "In Go, there is no `implements` keyword. How does
Go's interface system work, and what are its advantages?"**

*Why they ask:* Tests polyglot type system knowledge.
Common in polyglot shops (Java + Go services).

*Strong answer includes:*
- Go: if a type has all the methods defined in an interface,
  it implements that interface implicitly. No `implements`
  declaration needed.
- Example: `io.Reader` interface has one method: `Read(p []byte) (n int, err error)`.
  Any type with that method signature implements `io.Reader`.
  The standard library never says "os.File implements io.Reader" -
  it just does, by virtue of having the `Read` method.
- Advantages: (1) Decoupled design - interface and implementation
  in different packages with no dependency on each other.
  (2) Retroactive compatibility - add a method to an existing
  type and it automatically satisfies any matching interface.
  (3) Smaller interfaces by convention (Go prefers single-method
  interfaces: `io.Reader`, `io.Writer`, `fmt.Stringer`).
- Contrast with Java: adding a method to a class does not
  automatically make it satisfy any interface. You must
  explicitly declare `implements`.
