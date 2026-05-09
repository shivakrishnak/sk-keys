---
layout: default
title: "Builder"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /design-patterns/builder/
id: DPT-009
category: Design Patterns
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-009 - Builder

⚡ TL;DR - Builder constructs complex objects step-by-step, separating configuration from creation so the same process can produce different representations.

| DPT-009 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Method Chaining, Immutability | |
| **Used by:** | Complex Object Construction, Test Data Builders, Query DSLs | |
| **Related:** | Factory Method, Abstract Factory, Prototype, Immutability | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An `HttpRequest` class has 12 fields: URL, method, headers, body, timeout, retries, auth token, proxy, certificate, compression, user agent, and cookies. The constructor becomes: `new HttpRequest(url, method, headers, body, timeout, retries, authToken, proxy, cert, compress, userAgent, cookies)`. Callers pass `null` for fields they don't use - but in what position? Mistake: swapping `timeout` (int) and `retries` (int) silently compiles and sends requests with wrong values. Adding a 13th field breaks every call site in the codebase.

**THE BREAKING POINT:**
This is called the "telescoping constructor" anti-pattern. To avoid the 12-arg monster, developers add convenience constructors: `HttpRequest(url, method)`, `HttpRequest(url, method, body)`, `HttpRequest(url, method, body, timeout)`, etc. With 12 fields, the combinations are combinatorial. The class becomes unmaintainable and callers still can't see what each `null` means - `new HttpRequest("http://api.com", "GET", null, null, 5000, 3, null, null, null, true, null, null)` is unreadable.

**THE INVENTION MOMENT:**
This is exactly why the Builder pattern was created. A fluent builder API makes each parameter self-documenting: `HttpRequest.builder().url("http://api.com").method("GET").timeout(5000).retries(3).compress(true).build()`. Only the needed fields are set. Parameter order doesn't matter. Adding a new optional field doesn't break any call site.

**EVOLUTION:**
The GoF Builder (1994) was a Director-driven pattern for parsing
complex documents (RTF, HTML). Joshua Bloch's "Effective Java"
(2001) popularised the telescoping-constructor variant as a solution
to nullable parameter hell. Project Lombok's `@Builder` (2009)
eliminated the boilerplate entirely. Java records (Java 16+) now
handle simple cases without any builder class. Today the pattern
lives on primarily in fluent DSL APIs, query builders, and
test fixture factories.

---

### 📘 Textbook Definition

The **Builder** pattern is a creational design pattern that separates the construction of a complex object from its representation. A `Builder` object accumulates configuration through a series of setter-like methods, and a final `build()` call creates the target object. This allows the same construction process to produce different representations, enforces immutability on the final object, and keeps construction code readable. The pattern is distinct from Abstract Factory in that it constructs one complex object step-by-step rather than a family of related objects in one call.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Build a complex object piece by piece, each step named, then finalise it in one call.

**One analogy:**
> Building a custom pizza by telling the chef: "Add tomato sauce. Add mozzarella. Add mushrooms. Add extra pepperoni. No olives. Done." Each instruction is named and optional. Contrast with: "Give me pizza number [3, 1, 1, 1, 0, 0, 1, 12]" - positional, unreadable, and error-prone.

**One insight:**
The Builder's deepest value is not convenience - it is the separation of *valid incomplete state* (the builder) from *complete valid state* (the built object). The `build()` method is the validation checkpoint that transforms a partially-configured builder into an immutable, valid object.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Complex objects have many optional parts with independent validity rules.
2. A partially-constructed object should not be usable - invalid state must be contained.
3. Callers must be able to specify only the parts they care about without knowing internal defaults.

**DERIVED DESIGN:**
Given invariant 1: each "part" is a separate setter-style method on the builder. Given invariant 2: the builder, not the target class, holds intermediate state. The target object is only created at `build()`, when all mandatory fields can be validated. Given invariant 3: the builder provides defaults for optional fields; only mandatory fields throw on `build()` if absent.

The fluent API (method chaining) emerges from each builder method returning `this`. This allows `builder.a().b().c()` rather than three separate statements - visually declarative. The returned builder is mutable during construction; the built object is immutable after construction.

**THE TRADE-OFFS:**
**Gain:** Readable construction of complex objects; immutable final objects; mandatory/optional distinction enforced at `build()`; no parameter-order bugs; easy to add optional fields without breaking callers.
**Cost:** Boilerplate - builder class mirrors all fields of the target class (Lombok `@Builder` or Java records mitigate this); two-class increase per domain object; if the domain object changes, the builder must change too; mutable builder is not thread-safe during construction (by design).

---

### 🧪 Thought Experiment

**SETUP:**
An email system must send emails with: mandatory `to` and `body`, optional `cc`, `bcc`, `subject`, `attachments`, `priority`, and `replyTo`. There are 128 possible combinations of optional fields.

**WHAT HAPPENS WITHOUT BUILDER:**
Either: 128 constructor overloads (absurd) - or one 8-argument constructor where every call has nulls: `new Email("alice@x.com", null, null, null, "Hello", null, null, "HIGH")`. Reviewers cannot tell which `null` maps to `bcc` and which to `replyTo`. A bug slips through: the wrong null position causes emails to send without subjects for two weeks.

**WHAT HAPPENS WITH BUILDER:**
`Email.builder().to("alice@x.com").body("Hello").priority(HIGH).build()`. Only three fields set; the other five default safely. A code review of this expression is instantly readable. Adding `replyTo` support later: add `replyTo(String)` to the builder - zero existing call sites break.

**THE INSIGHT:**
The Builder externalises "which configuration is required" and "which is optional" from the call site to the builder's `build()` method. The caller expresses intent (named fields) rather than position (argument index). Intent is readable; position is not.

---

### 🧠 Mental Model / Analogy

> Builder is like a custom sandwich order form. You check the boxes for what you want: bread type, proteins, vegetables, sauces, toasted or not. The form collects your choices. When you hand it to the cashier (`build()`), they assemble the sandwich - validating that you've chosen at least a bread type and one filling (mandatory). You never have to say "white bread, lettuce, no tomato, no onion, yes cheese, no..." in a fixed order.

- "Sandwich order form" → the Builder object (mutable collector)
- "Checking boxes" → calling `bread()`, `protein()`, `sauce()` methods
- "Handing form to cashier" → calling `build()`
- "Validation: must have bread" → mandatory field check in `build()`
- "Final assembled sandwich" → the immutable built object
- "Default: no sauce unless requested" → optional field default logic

Where this analogy breaks down: a sandwich order form allows inconsistent choices (no toppings). A well-designed `build()` method validates consistency - e.g., `attachment != null && subject == null → throw`.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Builder is a step-by-step recipe for creating complex objects. Instead of passing 15 ingredients all at once in a fixed order, you call one method per ingredient, in any order, and say "make it" when you're done. Each step is labelled, so anyone reading the code knows exactly what's happening.

**Level 2 - How to use it (junior developer):**
Create a nested static `Builder` class inside your target class. Mirror every field as a builder field. Each builder method sets that field and returns `this` (fluent). The `build()` method validates required fields and calls the target class's private constructor. In Java: use Project Lombok's `@Builder` annotation to generate all this automatically. For test data: create builder variants with sensible defaults per test domain (`UserBuilder.validUser()`) to reduce test boilerplate.

**Level 3 - How it works (mid-level engineer):**
The built object's constructor is private, forcing all creation through the builder - this ensures `build()` has always been called and validation has run. Thread safety: the builder is intended to be used by one thread assembling one object; sharing a partially-built builder across threads requires external synchronisation. The director variant of Builder (GoF original) separates "which steps to call in what order" into a Director class - useful when the same builder can produce different objects based on a recipe. Modern Java uses `record` types (Java 16+) with `with` copy-methods as an alternative for immutable objects with many fields.

**Level 4 - Why it was designed this way (senior/staff):**
The GoF Builder was designed to separate complex construction sequences from representations - primarily for parsers (build an AST node-by-node). The fluent-API flavour (popularised by Effective Java / Joshua Bloch) is a simplification focused on telescoping constructors. They share the name but slightly different intents. The deep insight: Builder is an application of the Separation of Concerns principle - the knowledge of "what constitutes a valid Email" is in one place (`Email.build()`) rather than scattered across every call site. This is the same principle that drives domain validation: centralise invariant enforcement. At scale, builders become domain-specific languages (e.g., SQL query builders, HTTP client builders, test fixture builders) that form a fluency layer over the underlying domain model.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  BUILDER PATTERN FLOW                       │
│                                             │
│  Client                                     │
│    ↓ calls                                  │
│  Email.builder()              ← creates     │
│     .to("alice@x.com")        ← sets field  │
│     .subject("Hello")         ← sets field  │
│     .body("Content...")       ← sets field  │
│     .priority(HIGH)           ← sets field  │
│     .build()                  ← validates + │
│                                  creates    │
│                ↓                            │
│         Email (immutable)                   │
│         { to, subject, body,                │
│           priority, cc=null... }            │
└─────────────────────────────────────────────┘
```

**Method chaining works because:**
Each method returns `this` (the same builder instance). The chain is just calling methods on the same object sequentially - the chain is syntactic sugar for separate statements. No new objects are created until `build()`.

**`build()` validation logic:**
```
build():
  if (to == null) throw IllegalStateException("to required")
  if (body == null) throw IllegalStateException("body required")
  if (attachment != null && subject == null)
    throw IllegalStateException("subject required with attachment")
  return new Email(this);  // private constructor
```

**Director variant (GoF original):**
A `Director` class encapsulates the sequence of builder calls. `Director.buildMarketingEmail(builder)` calls `builder.priority(LOW).unsubscribeLink(true).subject(template.subject())...`. The director knows the recipe; the builder knows how to set each field; the client uses the director without knowing the recipe.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client composes email configuration
  → Email.builder()          ← YOU ARE HERE
  → .to(), .subject(), .body() called
  → .build() validates all mandatory fields
  → private Email(...) called with builder state
  → Email object returned - immutable, valid
  → Client passes Email to EmailService.send(email)
```

**FAILURE PATH:**
```
build() called with missing mandatory field
  → IllegalStateException("to address required")
  → Called at construction time (not send time)
  → Bug caught close to the construction site
  → Stack trace points directly to the build() call
```

**WHAT CHANGES AT SCALE:**
In high-throughput systems (100,000+ objects/second), builder object allocation per email adds GC pressure. The pattern is reused via **object pools of builders** - the builder is reset and reused rather than discarded. Alternatively, records with compact constructors (Java 16+) eliminate the builder entirely for simple cases. In DSL scenarios (query builders, ORM criteria), lazy evaluation is added: the builder accumulates operations but defers execution to query time - the `build()` call produces an AST, not a result.

---

### 💻 Code Example

**Example 1 - BAD: Telescoping constructors:**
```java
// BAD: position-dependent, null-filled, unreadable
Email email = new Email(
    "alice@x.com",  // to
    null,           // cc - or is it bcc?
    null,           // bcc
    "Hello",        // subject
    "Content",      // body
    null,           // attachment
    "HIGH",         // priority
    null            // replyTo
);
```

**Example 2 - GOOD: Builder pattern (handwritten):**
```java
public final class Email {
    private final String to;
    private final String cc;       // optional
    private final String subject;  // optional
    private final String body;
    private final Priority priority;

    // Private - forces use of builder
    private Email(Builder b) {
        this.to       = b.to;
        this.cc       = b.cc;
        this.subject  = b.subject;
        this.body     = b.body;
        this.priority = b.priority;
    }

    public static Builder builder() { return new Builder(); }

    public static final class Builder {
        private String to;
        private String cc;
        private String subject;
        private String body;
        private Priority priority = Priority.NORMAL; // default

        public Builder to(String to) {
            this.to = to; return this;
        }
        public Builder cc(String cc) {
            this.cc = cc; return this;
        }
        public Builder subject(String s) {
            this.subject = s; return this;
        }
        public Builder body(String b) {
            this.body = b; return this;
        }
        public Builder priority(Priority p) {
            this.priority = p; return this;
        }

        public Email build() {
            // Validation - centralised, one place
            if (to == null || to.isBlank())
                throw new IllegalStateException(
                    "to is required");
            if (body == null || body.isBlank())
                throw new IllegalStateException(
                    "body is required");
            return new Email(this);
        }
    }
}

// Usage:
Email email = Email.builder()
    .to("alice@example.com")
    .subject("Hello")
    .body("Meeting at 3pm?")
    .cc("bob@example.com")
    .priority(Priority.HIGH)
    .build();
```

**Example 3 - BEST: Lombok @Builder (production shorthand):**
```java
@Builder(toBuilder = true)  // toBuilder enables copy-with
@Value                      // Lombok immutable fields
public class Email {
    @NonNull String to;     // Lombok @NonNull = mandatory
    String cc;              // optional - null by default
    String subject;
    @NonNull String body;
    @Builder.Default
    Priority priority = Priority.NORMAL;
}

// Usage:
Email e = Email.builder()
    .to("alice@example.com")
    .body("Hi!")
    .build();

// Copy-with (immutable update):
Email urgent = e.toBuilder()
    .priority(Priority.HIGH)
    .build();
```

**Example 4 - Test data builder (production pattern):**
```java
// Default builder with test-meaningful defaults:
public class EmailTestBuilder {
    private String to = "test@example.com";
    private String body = "Default test body";
    private Priority priority = Priority.NORMAL;

    public EmailTestBuilder withUrgentPriority() {
        this.priority = Priority.HIGH;
        return this;
    }

    public EmailTestBuilder to(String to) {
        this.to = to; return this;
    }

    public Email build() {
        return Email.builder()
            .to(to).body(body).priority(priority).build();
    }
}

// In tests - minimal setup, clear intent:
Email urgentEmail = new EmailTestBuilder()
    .withUrgentPriority()
    .build();
```

---

### ⚖️ Comparison Table

| Approach | Readability | Optional Fields | Immutability | Validation | Best For |
|---|---|---|---|---|---|
| **Builder** | Excellent | Explicit defaults | Easy (build()) | Centralised | Complex objects with many optional parts |
| Telescoping constructors | Poor (>4 args) | Null-filled | Easy | At constructor | Simple 2–3 field objects |
| JavaBean setters | Medium | Natural | Lost (mutable) | Scattered | Mutable objects, frameworks needing defaults |
| Record (Java 16+) | Good | Limited | Built-in | Compact constructor | Small immutable value objects |
| Factory Method | Good | Pre-defined sets | Depends | In factory | Polymorphic single-call creation |

How to choose: prefer Builder for objects with more than 4 fields and at least 2 optional fields. Use records (Java 16+) for small immutable value types with fewer than 5 fields. Use Lombok `@Builder` in production code to eliminate the boilerplate.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Builder always creates immutable objects | Builder can create mutable objects. The pattern just separates construction from use. Immutability is a common but separate choice made on the built object |
| GoF Builder and fluent-API Builder are the same | GoF Builder separates construction algorithm (Director) from representation (Builder). Bloch-style fluent Builder specifically addresses telescoping constructors. Same name, different emphasis |
| Builder is only for domain objects | Builders are widely used for: SQL query construction (Criteria API, jOOQ), HTTP client configuration (OkHttp, WebClient), test fixtures, command-line argument parsing, configuration DSLs |
| build() must return a new object every time | For pooled or cached objects, `build()` can return an existing instance from a cache. The pattern does not mandate creating new objects - it mandates that the built object passes through a validation gate |
| Builder makes code more readable only to the author | The self-documenting `.field(value)` syntax makes code readable to anyone. Studies of code readability consistently show named parameters (simulated by fluent builders) outperform positional parameters for objects with >3 fields |

---

### 🚨 Failure Modes & Diagnosis

**1. Builder Shared Across Threads Without Synchronisation**

**Symptom:** Intermittent `NullPointerException` or wrong field values in built objects during load testing, disappearing under single-thread conditions.

**Root Cause:** A builder instance was reused or shared between threads. Thread A sets `to`, Thread B sets `body`, both call `build()` - each gets a partially-configured object.

**Diagnostic:**
```bash
# Check if builder instances are stored in fields/shared state:
grep -n "Builder b = " src --include="*.java" -r \
  | grep -v "= .builder()"
# Field-stored builders are sharing risks - investigate each
```

**Fix:**
Builders must never be stored as instance/static fields or passed between threads. Create a new builder per object being constructed.

**Prevention:** Treat builders as local variables only. Code review rule: never assign a builder to a field.

---

**2. Mutable Object Exposed Before `build()` Completes**

**Symptom:** An object is accessed with incorrect state. `getTo()` returns null even though `to("...")` was called.

**Root Cause:** The builder's intermediate object (or the builder itself) was passed to another method before `build()` was called.

**Diagnostic:**
```java
// Add a "built" flag to detect premature use:
private boolean built = false;
public String getTo() {
    if (!built) throw new IllegalStateException(
        "Builder not yet built");
    return to;
}
```

**Fix:**
Make the target class's constructor package-private or private. The builder is the only entry point. Pass the *built* object, not the builder, to other methods.

**Prevention:** Never pass builder instances across method boundaries - only pass the `build()` result.

---

**3. Missing Mandatory Field Detected Too Late**

**Symptom:** `NullPointerException` inside `EmailService.send()` at `email.getTo().contains("@")` - 5 stack frames from the construction site.

**Root Cause:** Mandatory field validation is done in the consuming method rather than in `build()`. The object was allowed to exist in an invalid state.

**Diagnostic:**
```bash
# Check build() method for validation coverage:
grep -A 20 "public.*build()" src/Email.java
# If no null-checks before return: validation is missing
```

**Fix:**
Add all mandatory-field validation to `build()` before calling the private constructor. Use Lombok `@NonNull` to generate null-checks automatically.

**Prevention:** Design rule: a successfully-built object is ALWAYS valid. Any invariant violation must fail in `build()`, not in downstream consumers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Object-Oriented Programming (OOP)` - builder pattern uses classes, constructors, and method chaining
- `Immutability` - builders are typically used to create immutable objects; understanding why immutability matters drives correct use
- `Method Chaining` - the fluent API style relies on each method returning `this`; understanding this Java pattern prevents confusion

**Builds On This (learn these next):**
- `Fluent Interface` - Builder is the most common example of a Fluent Interface - a DSL-like API where methods chain to compose behaviour
- `Prototype` - when cloning an existing object with small modifications, Prototype + Builder's `toBuilder()` method provide efficient "copy-with" semantics
- `Test Data Builder` - a specialisation of Builder for test fixtures that provides domain-meaningful named constructors (`validUser()`, `expiredUser()`)

**Alternatives / Comparisons:**
- `Factory Method` - creates objects in one call, not step-by-step; use when the full configuration is known at creation time
- `Abstract Factory` - creates families of related objects in one call; use when multiple compatible objects must be created together
- `Java Records` - Java 16+ alternative for small immutable value objects; simpler than Builder but no step-by-step construction or defaults

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Step-by-step object construction with     │
│              │ named methods and final build() call      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Telescoping constructors with many        │
│ SOLVES       │ null positional args are unreadable       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ build() is the validation checkpoint -    │
│              │ no valid object exists before it runs     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object has 4+ fields with optional ones   │
│              │ and invalid partial states must be barred │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Object has 2–3 simple fields; use a       │
│              │ plain constructor or record instead       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Readable construction + immutability vs   │
│              │ boilerplate builder class per domain type │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Config the parts you want, build once,  │
│              │  get an immutable valid object."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Immutability → Fluent Interface →         │
│              │ Test Data Builder                         │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate the accumulation of configuration from the act of
construction. Let the consumer describe *what* is needed step by
step; enforce validity once at the moment of creation.

**Where else this pattern appears:**
- **SQL query builders (jOOQ, Criteria API):** `.select().from()
  .where().groupBy().build()` accumulates clauses independently
  of execution; the query is only validated and sent at `.fetch()`.
- **HTTP clients (OkHttp, WebClient):** Request configuration is
  built fluently; validation (required URL, method) happens when
  the request is dispatched.
- **Infrastructure as Code (Terraform):** A `resource` block
  declares fields step by step; the plan phase is the "build()"
  that validates and validates the complete configuration.

---

### 💡 The Surprising Truth

The Builder pattern and the Telescoping Constructor anti-pattern
are so closely linked that Joshua Bloch added Builder to Effective
Java specifically *because* Java lacked named parameters. Languages
with native named parameters (Python, Kotlin, Swift) rarely need
Builder for the telescoping-constructor problem - `Email(to="alice",
body="hi", priority=HIGH)` is already as readable as a builder.
Java's missing language feature became the pattern's primary
use case, making Builder one of the few GoF patterns whose
prevalence is a measure of a language limitation, not architecture.
---

### 🧠 Think About This Before We Continue

**Q1.** A `QueryBuilder` uses the Builder pattern to construct SQL queries: `.select("id", "name").from("users").where("age > 18").orderBy("name").limit(10).build()`. The `build()` method produces a `Query` object. At 50,000 requests/second, each request creates a new `QueryBuilder` and `Query`. Profile the allocation rate - estimate the bytes allocated per request and the GC pressure in a 2 GB heap JVM, then describe a structural change to the Builder that reduces allocation without changing the caller API.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** You are building a `HttpRequest` builder. A requirement says: if `authentication` is set to `OAUTH`, then `clientId` and `clientSecret` must also be set; if `authentication` is `BASIC`, only `username` and `password` are required. This is a conditional mandatory-field relationship. Design the `build()` validation logic for this, and then evaluate whether the standard Builder pattern is sufficient or whether a more specialised pattern (staged builder, type-safe builder) would enforce these constraints at compile time rather than runtime.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** Kotlin's data classes provide
`copy()`: `val urgent = email.copy(priority = HIGH)`. Java 16+
records provide compact constructors. Given these language
features, describe the remaining cases where the full Builder
pattern is still the superior choice over these alternatives,
and state where it becomes unnecessary overhead.

*Hint: Look at the Comparison Table — identify what Builder
provides that `copy()` and records cannot: validation on
`build()`, conditional field rules, and ordered construction
of complex multi-step objects.*
