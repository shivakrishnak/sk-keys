---
id: DPT-009
title: Builder
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-007
used_by: DPT-040
related: DPT-007, DPT-008, DPT-010, DPT-039
tags:
  - pattern
  - creational
  - intermediate
  - java
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/design-patterns/builder/
---

⚡ TL;DR - Builder separates the construction of a complex
object from its representation, allowing the same construction
process to produce different representations - and in Java,
it solves the telescoping constructor problem.

| #9 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-007 | |
| **Used by:** | DPT-040 | |
| **Related:** | DPT-007, DPT-008, DPT-010, DPT-039 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `User` class has 12 fields: name (required), email
(required), age (optional), phone (optional), address
(optional), avatar (optional), bio (optional), role
(required), verified (optional), preferences (optional),
timezone (optional), locale (optional). Without Builder,
you get telescoping constructors:
`User(name, email)`, `User(name, email, age)`,
`User(name, email, age, phone)`, ..., ending in a
constructor that takes all 12 parameters.

**THE BREAKING POINT:**
The 12-parameter constructor is called as:
`new User("Alice", "alice@x.com", 0, null, null, null, null,
"ADMIN", false, null, "UTC", "en-US")`

Which parameter is age? Which is phone? What does 0 mean?
The null parameters are noise. When the parameter order
changes in a refactor, callsites break silently: the compiler
accepts the wrong argument positions if the types match.

**THE INVENTION MOMENT:**
GoF Builder separates construction from the product: a Director
controls the construction steps, a Builder accumulates them.
In Java practice, Josh Bloch (Effective Java, Item 2) fused
the Builder concept into an inner static class that serves
as both Builder and Director, producing the "fluent builder"
idiom that is now ubiquitous in Java libraries.

**EVOLUTION:**
GoF Builder was designed for cases where the same construction
process produces different output formats (an HTML document
builder and a Markdown document builder sharing a Director).
In Java practice, the inner static Builder (Bloch's variant)
dominates and is used primarily to solve the telescoping
constructor and optional parameter problems, less commonly
for multiple-representation purposes. Lombok's `@Builder`
generates the inner static builder automatically. Kotlin's
named arguments make this entire pattern unnecessary in Kotlin.

---

### 📘 Textbook Definition

The **Builder** pattern is a Creational design pattern that
separates the construction of a complex object (the Product)
from its representation. A Builder object receives
construction steps one at a time, accumulates state
representing the object being built, and produces the final
Product on demand via a `build()` call. A Director (optional
in the Bloch variant) orchestrates the construction sequence.
The caller can vary the final Product's representation by
using a different concrete Builder with the same Director,
or by calling different setter steps on the same Builder.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Builder assembles a complex object step-by-step, with a
final `build()` call producing the result - solving the
"12-argument constructor" problem.

**One analogy:**
> Ordering a custom PC: you configure it component by
> component - CPU, RAM, GPU, storage, peripherals. Each
> choice is a builder step. When you're done, "Place Order"
> (build()) creates the final PC. You cannot build an invalid
> machine mid-configuration because the build() is deferred
> until you say you're done.

**One insight:**
Builder's key power is DEFERRED CREATION: the object does
not exist until `build()` is called. This enables VALIDATION
at build time: check all required fields are set BEFORE
creating the object. Once built, the object can be immutable.
Builder enables immutable objects with many fields.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The product does not exist during construction - it is
   assembled in the Builder, not in the product's constructor.
2. `build()` is the single commit point: validation, defaults,
   and object creation happen here.
3. Builder is mutable by design; Product should be immutable
   by design - the Builder is discarded after build().

**DERIVED DESIGN:**
Four participants (GoF variant):
- **Product**: the complex object being built
- **AbstractBuilder**: interface declaring construction steps
- **ConcreteBuilder**: accumulates state, implements steps,
  provides build() to return the Product
- **Director**: (optional) orchestrates the step sequence
  using an AbstractBuilder

Two participants (Bloch/Java variant):
- **Product**: the outer class, typically immutable
- **Product.Builder**: inner static class, mutable, all
  setter methods return `this` for chaining, `build()`
  creates the immutable Product

**TRADE-OFFS:**

**Gain:** Readable construction (named steps vs positional
arguments). Deferred validation. Immutable products. Reusable
Builder instances (build the same config multiple times).

**Cost:** More classes. The inner Builder class duplicates
field declarations. For objects with 2-3 fields, Builder
is over-engineering; use a regular constructor.

**When Builder is wrong:**
Use Builder for objects with 4+ parameters where several
are optional and the constructor call is unreadable without
knowing the parameter names. For 2-3 parameters with obvious
names and all required, a regular constructor is clearer.

---

### 🧪 Thought Experiment

**SETUP:**
An HTTP request builder: a request needs a URL (required),
method (default GET), optional headers (Map), optional body,
optional timeout, optional authentication, optional retry
policy. Building a complete authenticated request with
retry looks like:

```
new Request(url, "POST", headers, body, 5000, auth,
  retryPolicy)
```

**WHAT HAPPENS WITHOUT BUILDER:**
Seven positional arguments. The second argument is the method
string - a typo like "PSOT" is not caught at compile time.
What is the 6th argument? auth? Timeout? The call is
unreadable without the IDE's parameter hints. Adding an
8th optional parameter (proxy settings) breaks every callsite.

**WHAT HAPPENS WITH BUILDER:**
```java
Request req = Request.builder()
    .url(url)
    .method("POST")
    .header("Content-Type", "application/json")
    .body(payload)
    .timeout(5000)
    .auth(credentials)
    .retryPolicy(RetryPolicy.threeAttempts())
    .build();
```

Each step is named. Adding proxy settings adds one `.proxy()`
step - zero impact on existing callsites.

**THE INSIGHT:**
Builder's fluent API is self-documenting. The construction
reads like a specification. Omitting optional fields is
natural - just don't call that step. The `build()` validates
that URL is present before creating the Request.

---

### 🧠 Mental Model / Analogy

> Builder is a construction CHECKLIST that produces a finished
> product when you check "Done." Each checkbox is a builder
> step. You fill in what you need, leave optional items
> unchecked, and when you sign off (build()), the foreman
> validates the checklist before delivering the finished item.

- "Checklist" = Builder accumulator
- "Each checkbox" = a setter method on Builder
- "Sign off / Done" = build()
- "Foreman validation" = validation in build()
- "Finished item" = the immutable Product
- "Required checkboxes" = required field validation in build()

**Where this analogy breaks down:**
A checklist allows completing items in any order. Builders
typically allow steps in any order too. But GoF Builder with
a Director enforces a SPECIFIC ORDER. The analogy holds for
Bloch-style fluent builders but not for Director-governed
construction where step sequence matters.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Builder lets you set up an object piece by piece with named
steps, then call `build()` at the end to get the final object.
It makes complex object construction readable and validates
required pieces before creating the object.

**Level 2 - How to use it (junior developer):**
Create a static inner class `Product.Builder`. Each optional
field gets a setter that returns `this` (for chaining).
Required fields go in the Builder's constructor. `build()`
validates required fields and calls `new Product(this)`.
The Product constructor takes the Builder as its single
argument and copies all fields.

**Level 3 - How it works (mid-level engineer):**
The Bloch Builder works by making the Product's constructor
PRIVATE and the Builder an inner class (so it can access
private fields). Builder accumulates mutable state; build()
creates the immutable Product and discards the Builder.
This achieves the "telescoping constructor" fix and enables
immutability without a 12-parameter constructor.

**Level 4 - Why it was designed this way (senior/staff):**
GoF Builder's Director was designed for MULTIPLE REPRESENTATIONS:
a `DocumentBuilder` with a `HtmlConcreteBuilder` and
`MarkdownConcreteBuilder` allows the same Director to produce
HTML and Markdown from the same construction steps. This is
rarely used in practice because format conversion is usually
handled differently (visitor, template, serializer). The GoF
and Bloch variants serve different problems. Expert engineers
distinguish them and apply each to the correct problem.

**Level 5 - Mastery (distinguished engineer):**
Builder composes with Factory Method in sophisticated
frameworks: a factory method returns a pre-configured Builder
for a specific context. `OkHttpClient.Builder` from Square's
OkHttp library is a production-grade fluent Builder with
a final `build()`. Kotlin DSL builders use lambda-with-receiver
syntax to achieve Builder semantics without a separate class:
`buildString { append("x"); append("y") }`. Java record
classes (Java 16+) reduce the need for Builders in simple
cases: `User.of(name, email).withAge(25)` using `with` copy
constructors - but these are limited to small numbers of
optional fields.

---

### ⚙️ How It Works (Mechanism)

```
Builder Mechanics (Bloch/Java variant)
┌──────────────────────────────────────────────────────┐
│  Product (immutable, private constructor)            │
│  - name: String    (required)                        │
│  - email: String   (required)                        │
│  - age: int        (optional, default 0)             │
│  - role: Role      (required)                        │
│                                                      │
│  static inner class Builder                          │
│  - name: String    ← required, set in constructor    │
│  - email: String   ← required, set in constructor    │
│  - age: int = 0    ← optional, default value         │
│  - role: Role      ← required, set in constructor    │
│                                                      │
│  Builder(name, email, role)   ← required fields      │
│  .age(int) → this             ← fluent chaining       │
│  .build()                                            │
│    validate: not null/empty                          │
│    return new Product(this)   ← the product created  │
│                                                      │
│  Product(Builder b)                                  │
│    this.name = b.name         ← copies all fields    │
│    this.email = b.email       ← from builder         │
│    this.age = b.age                                  │
│    this.role = b.role                                │
└──────────────────────────────────────────────────────┘
```

**Execution trace:**
1. Caller: `new User.Builder("Alice", "alice@x.com", ADMIN)`
2. Calls `.age(25)` → Builder.age = 25; returns same Builder
3. Calls `.build()` → validates name/email/role not null
4. `build()` calls `new User(this)` → Product created
5. Product constructor copies all fields from Builder
6. Immutable `User` object returned; Builder discarded
7. User's fields cannot change after build()

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Create Builder with required fields
  → Chain optional setter calls (any order)
  → Call build()
  → build() validates required fields
  → build() calls private Product constructor
  → Immutable Product returned
  → Builder discarded (single-use by convention)
```

**FAILURE PATH:**
```
build() called without required field set
  → IllegalStateException: "email is required"
  → Caught at build() time, not at use time
  → Clear error message with field name
```

**WHAT CHANGES AT SCALE:**
Builder itself has no scale concerns. Performance note:
Builder creates an intermediate object (the Builder itself)
before the final Product. In tight loops creating millions
of objects, the Builder allocation adds GC pressure. For
high-frequency simple objects, consider factory method or
direct constructor.

---

### 💻 Code Example

**Example 1 - Telescoping constructor (the problem):**

```java
// BAD: telescoping constructor - unreadable callsite
class User {
    User(String name, String email) { ... }
    User(String name, String email, int age) { ... }
    User(String name, String email, int age, String phone) { ... }
    // ... 8 more overloads, plus:
}

// Callsite: what is null? what is 0? parameter order unclear
User u = new User("Alice", "alice@x.com", 25,
    null, null, null, "ADMIN", false, null, "UTC", "en-US");
```

**Example 2 - Bloch Builder pattern:**

```java
// GOOD: Bloch-style inner static Builder
public final class User {
    private final String name;
    private final String email;
    private final int age;
    private final String role;
    private final String timezone;

    // Private constructor - only Builder creates User
    private User(Builder b) {
        this.name     = b.name;
        this.email    = b.email;
        this.age      = b.age;
        this.role     = b.role;
        this.timezone = b.timezone;
    }

    public static class Builder {
        // Required fields - set in Builder constructor
        private final String name;
        private final String email;
        private final String role;
        // Optional fields - defaults applied here
        private int age = 0;
        private String timezone = "UTC";

        public Builder(String name, String email, String role) {
            this.name  = name;
            this.email = email;
            this.role  = role;
        }

        public Builder age(int age) {
            this.age = age;
            return this; // fluent chaining
        }

        public Builder timezone(String tz) {
            this.timezone = tz;
            return this;
        }

        public User build() {
            // Validate required fields before creating
            if (name == null || name.isBlank())
                throw new IllegalStateException("name required");
            if (email == null || !email.contains("@"))
                throw new IllegalStateException(
                    "valid email required");
            return new User(this);
        }
    }
}

// Callsite: readable, self-documenting, extensible
User alice = new User.Builder("Alice", "alice@x.com", "ADMIN")
    .age(25)
    .timezone("America/New_York")
    .build();
```

**Example 3 - GoF Builder for multiple representations:**

```java
// GOOD: GoF variant - same steps, different representations
interface ReportBuilder {
    void addTitle(String title);
    void addSection(String heading, String body);
    void addTable(List<String[]> rows);
    Object build();
}

class HtmlReportBuilder implements ReportBuilder {
    private StringBuilder html = new StringBuilder();
    public void addTitle(String t) {
        html.append("<h1>").append(t).append("</h1>\n");
    }
    public void addSection(String h, String b) {
        html.append("<h2>").append(h).append("</h2>\n")
            .append("<p>").append(b).append("</p>\n");
    }
    public void addTable(List<String[]> rows) { /* HTML table */ }
    public String build() { return html.toString(); }
}

class PdfReportBuilder implements ReportBuilder {
    // Same steps, produces a PDF byte[] instead
    public byte[] build() { /* PDF bytes */ return null; }
}

// Director: same construction sequence, different output
class ReportDirector {
    static void buildQuarterlyReport(
            ReportBuilder builder, ReportData data) {
        builder.addTitle("Q" + data.quarter() + " Report");
        builder.addSection("Summary", data.summary());
        builder.addTable(data.metricsTable());
    }
}
```

**How to test/verify correctness:**
Test that required-field validation in `build()` throws with
a clear message when fields are missing. Test that optional
fields use defaults when not set. Test that the built Product
is immutable (no setters, all fields final). Test that
the same Builder can produce multiple products if needed.

---

### ⚖️ Comparison Table

| Approach                  | Readability | Immutability | Validation | Complexity |
| ------------------------- | ----------- | ------------ | ---------- | ---------- |
| **Builder (Bloch)**       | High        | Yes          | build()    | Medium     |
| Telescoping constructors  | Low         | Yes          | compile    | Low        |
| JavaBeans setters         | Medium      | No           | scattered  | Low        |
| Record (Java 16+)         | High        | Yes          | limited    | None       |
| Lombok @Builder           | High        | Yes          | build()    | None       |

**How to choose:**
- 2-3 all-required fields: regular constructor
- 2-3 fields some optional: Java record with compact constructor
- 4+ fields with optional mix: Builder (manual or Lombok)
- Multiple output representations: GoF Builder with Director
- Kotlin: named arguments; skip Builder entirely

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Builder and Factory Method solve the same problem | Factory Method decides WHICH type to create; Builder controls HOW to construct a complex object of a known type |
| You must always have a Director with Builder | The Director is optional - Bloch-style Builder in Java has no Director; the caller IS the director |
| Builder should validate each setter as it's called | Validation in build() is correct; validating in setters makes partial construction state invalid, breaking chaining |
| Builder must create the same type always | GoF Builder explicitly supports multiple representations - the same Director can produce HTML, PDF, or XML from one builder interface |
| Lombok @Builder is not the GoF Builder pattern | Lombok @Builder IS the Bloch variant with generated code; the intent and structure match - code generation does not change the pattern |

---

### 🚨 Failure Modes & Diagnosis

**Builder Reuse After build() - Shared Mutable State**

**Symptom:**
A test or batch job creates a `RequestBuilder`, calls
`build()` to produce `request1`, then modifies the same
builder for `request2`. The two requests share mutable
state from the builder, and modifying one builder field
retroactively changes request1's state if the builder
fields are not copied defensively in `build()`.

**Root Cause:**
The Product constructor copied a reference to a mutable
collection from the Builder (e.g., `this.headers = b.headers`)
instead of making a defensive copy.

**Diagnostic Signal:**
Modify a builder collection field AFTER calling build().
If the built product's state changes: defensive copy is missing.

**Fix:**
```java
// BAD: aliased reference from builder to product
public Request build() {
    return new Request(this); // product.headers = b.headers
}

// GOOD: defensive copy at build() time
public Request build() {
    this.headers = Collections.unmodifiableMap(
        new HashMap<>(this.headers) // copy, not alias
    );
    return new Request(this);
}
```

**Prevention:**
Rule: if Builder contains any mutable objects (List, Map,
arrays), create defensive copies in build() before passing
to the Product constructor. Mark builder fields as mutable
explicitly in code comments.

---

**Missing Required Field Validation - Null Product Fields**

**Symptom:**
A `User` built without the required `email` field produces
a User with `null` email. The null propagates through the
system until a NullPointerException occurs far from the
construction site - hard to diagnose.

**Root Cause:**
`build()` method does not validate required fields before
calling the Product constructor.

**Diagnostic Signal:**
Unit test: create a builder with only one required field set
and call build(). Expected: exception with a clear message.
Actual: a User with null fields returned, test passes.

**Fix:**
```java
// BAD: build() creates product without validation
public User build() {
    return new User(this); // null email possible
}

// GOOD: validate required fields before creating
public User build() {
    Objects.requireNonNull(email, "email is required");
    if (email.isBlank())
        throw new IllegalStateException("email cannot be blank");
    return new User(this);
}
```

**Prevention:**
Required fields should be set in the Builder's constructor
(they become compile-time-required), OR validated in build().
Prefer Builder constructor for required fields over runtime
validation when possible.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Factory Method` - simpler Creational pattern; understand
  single-step creation before multi-step Builder

**Builds On This (learn these next):**
- `Specification Pattern` - frequently combined with Builder;
  a Specification object is a good candidate for Builder
  construction when specifications have many optional criteria

**Alternatives / Comparisons:**
- `Factory Method` / `Abstract Factory` - one-step creation
  vs Builder's multi-step assembly; use Factory Method when
  there is no complex construction, Builder when there is
- `Prototype` - another Creational pattern; clones an existing
  object rather than building from scratch; sometimes combined
  with Builder for "copy and modify" scenarios

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Step-by-step construction of a complex   │
│              │ object, deferred to final build() call   │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Telescoping constructors with 5+ params; │
│ SOLVES       │ optional fields with no clear API        │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ build() = validation + creation commit;  │
│              │ Builder is mutable, Product is immutable │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ 4+ fields with optional parameters;      │
│              │ want readable, self-documenting callsites│
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ 2-3 required fields with no optionals;  │
│              │ Kotlin (use named arguments instead)     │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ No defensive copy in build() leaks       │
│              │ mutable state from Builder to Product    │
├──────────────┼──────────────────────────────────────────┤
│ MODERN EXPR. │ Lombok @Builder generates the inner      │
│              │ Builder class automatically              │
├──────────────┼──────────────────────────────────────────┤
│ TWO VARIANTS │ GoF: Director + multiple representations │
│              │ Bloch: fluent inner Builder in Java      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Prototype → Specification → DI Pattern   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `build()` is the commit point - validation and object
   creation happen here; object does not exist until build()
   is called
2. Builder should be mutable, Product should be immutable;
   defensive copy mutable collections from Builder to Product
3. The GoF Director variant (multiple representations from
   one construction process) and the Bloch variant
   (telescoping constructor fix) solve DIFFERENT problems;
   know which you're using

**Interview one-liner:**
"Builder separates complex object construction from its
representation, solving the telescoping constructor problem
in Java. The key is build()-time validation before the
immutable product is created. Lombok @Builder generates this
automatically; OkHttpClient.Builder and StringBuilder are
widely-used production examples."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Defer object creation to a validation gate. Any system where
creating an invalid object is worse than preventing its
creation benefits from a Builder: the object either passes
validation and is created correctly, or an exception is
thrown with a clear description of what is missing. No
partially-constructed invalid state can escape build().

**Where else this pattern appears:**
- **HTTP client builders** - OkHttp, Apache HttpClient,
  Java 11 HttpClient all use fluent builders; the full request
  is assembled before any network connection is made
- **SQL query builders** - JOOQ, Querydsl, Criteria API
  all use Builder to assemble SQL queries step-by-step;
  build() generates the SQL string
- **Configuration objects** - most production frameworks
  use Builder for complex configuration: Caffeine cache config,
  Resilience4j CircuitBreakerConfig, Kafka producer config
- **Protocol buffers** - Protobuf Java generated code uses
  a Builder for message construction; once `build()` is
  called the message is immutable

**Industry applications:**
- **Spring MockMvc** - test DSL is a complete fluent Builder:
  `MockMvcRequestBuilders.post("/api/users").content(json)
  .contentType(APPLICATION_JSON)` - the request is assembled
  via builder, performed by `mockMvc.perform(request)`
- **Avro/Parquet record creation** - Big Data frameworks use
  generated Builder classes for schema-validated record creation

---

### 💡 The Surprising Truth

`StringBuilder` is a Builder in disguise - though Java's
designers never named it as such. `new StringBuilder()`
creates the Builder, `append()` calls are the construction
steps, and `toString()` is the `build()` method that produces
the final immutable `String`. Java's `String` is immutable;
`StringBuilder` exists precisely because you need a mutable
intermediate state to assemble complex strings step-by-step
before committing to a final immutable result. Every Java
developer has used Builder hundreds of thousands of times
without recognising the pattern name. `StringBuilder` is
the simplest possible Builder implementation in the language.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Identify three different Builder implementations
   in the Java standard library or common libraries
   (StringBuilder, Java 11 HttpClient.Builder, Locale.Builder)
   and explain why each matches the Builder pattern definition
2. [DISTINGUISH] Explain the specific difference between the
   GoF Builder (with Director, multiple representations) and
   the Bloch Builder (inner static class, telescoping
   constructor fix) - and which applies to a given problem
3. [DEBUG] Given a Builder where modifying the builder after
   build() corrupts the built product's state, identify the
   missing defensive copy and implement the fix
4. [BUILD] Implement from memory a fluent Builder for a
   `DatabaseConfig` object with required fields (url, username,
   password) and optional fields (poolSize=10, timeout=30s,
   readOnly=false), with build() validation
5. [DECIDE] Given a class with 8 constructor parameters
   (3 required, 5 optional), explain why Builder is preferable
   to JavaBeans setters for this case - specifically the
   immutability and thread-safety arguments

---

### 🧠 Think About This Before We Continue

**Q1.** `StringBuilder.append(x).append(y).append(z)
.toString()` - where is the Director in this Builder usage?
If the Director is optional in the Bloch variant, what exactly
IS the Director in GoF Builder, and when would you use it?

*Hint: The caller (you) IS the director in the Bloch variant.
You sequence the append() calls. GoF Director is useful when
the SAME sequence of steps must be applied to DIFFERENT
builders (HtmlBuilder, MarkdownBuilder) to produce different
representations. The Director encodes the sequence; the Builder
encodes the rendering. When would you want the same sequence
to produce different outputs? Report generation is the canonical
example - the Director knows the report structure; the Builder
knows the format.*

**Q2.** Consider a Builder with 20 optional fields. The team
debates: should required fields be in the Builder's constructor
(forcing compile-time correctness) or validated in build()
(allowing all fields to be set via setter methods)?

Design a hybrid approach that gives compile-time safety for
required fields while keeping the fluent API clean. Consider:
what happens when the required field set changes?

*Hint: Builder(requiredA, requiredB) enforces compile-time
but breaks callsites when required fields change. Annotations
(@NotNull on setter methods) + build() validation are more
stable but lose compile-time errors. The hybrid: use Step
Builder pattern - the constructor returns an intermediate
"Phase1" object with only requiredA; once set, returns a
"Phase2" object with requiredB; only Phase2 has build(). This
is compile-time enforcement without breaking on required field
changes - but adds N intermediate classes.*

**Q3.** Kotlin named arguments make Builder unnecessary for
most cases. But a senior engineer insists on Builder even in
Kotlin. When is this insistence justified? What does Builder
provide that named arguments do not?

*Hint: Named arguments give readability but not: (1) deferred
construction - the object is created at the call site;
(2) build-time validation across multiple fields (e.g.,
endDate must be after startDate); (3) partial construction
and reuse - building the same base config with different
overrides; (4) a stable API when the underlying class
constructor parameters change. For complex domain objects
with cross-field validation, Builder adds value even in Kotlin.*

---

### 🎯 Interview Deep-Dive

**Q1: What problem does Builder solve that constructors
cannot? When should you NOT use Builder?**

*Why they ask:* Tests understanding of the design motivation,
not just the pattern name.

*Strong answer includes:*
- Constructors cannot name their parameters at the call site:
  `new User("Alice", null, 25, null, "ADMIN")` - which null?
- Constructors cannot cleanly express optional parameters
  without telescoping overloads
- Builders should NOT be used for: 2-3 clearly named required
  fields (constructor is cleaner), Kotlin (named args), simple
  value objects (Java records), or performance-critical tight
  loops (Builder allocation overhead)

**Q2: Why should the Product built by a Builder be
immutable? How does Builder enable immutability?**

*Why they ask:* Tests understanding of the immutability
relationship - a common interview follow-up.

*Strong answer includes:*
- Without Builder: to make an object with many fields
  immutable, the constructor needs all those fields at once -
  leading to a 12-parameter constructor call
- With Builder: mutable assembly happens in the Builder;
  `build()` creates the immutable product with all fields
  via a single private constructor call
- The product has `final` fields + private constructor =
  truly immutable; no setters needed post-construction
- Builder and immutability are natural partners: Builder IS
  the mechanism that makes many-field immutable objects practical

**Q3: How does Lombok @Builder relate to the GoF Builder
pattern? What does Lombok generate?**

*Why they ask:* Tests practical knowledge and ability to
connect annotation-driven code to underlying pattern structure.

*Strong answer includes:*
- Lombok generates: the inner static Builder class, all field
  setters returning `this`, `build()` that calls the private
  constructor, and optionally `toBuilder()` for copy builders
- The generated code IS Bloch-style Builder - Lombok is code
  generation for the pattern, not a replacement for it
- Limitations: Lombok @Builder does not generate required-field
  validation in build() - add a `@Builder.ObtainVia` or write
  build() manually for required-field checks
- In code reviews, look for `@Builder` without required-field
  validation: missing guards allow null products to escape

