---
version: 2
layout: default
title: "Java 17 Features (Records, Sealed, Pattern Matching)"
parent: "Java Language"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/java/java-17-features/
id: JLG-032
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Java Language, Java 8 to Java 17 Migration Guide
used_by: Spring Core, Java Language, Testing
related: Kotlin Data Class, Scala Case Class, Switch Expression
tags:
  - java
  - jvm
  - intermediate
  - foundational
---

⚡ **TL;DR -** Java 17's headline features - records, sealed classes, and pattern matching for `instanceof` - eliminate the three most persistent sources of boilerplate and unsafe type-switching in Java codebases.

| | |
|---|---|
| **Depends on** | Java Language, Java 8 to Java 17 Migration Guide |
| **Used by** | Spring Core, Java Language, Testing |
| **Related** | Kotlin Data Class, Scala Case Class, Switch Expression |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A simple data class in Java 8 requires a constructor, two getters, `equals()`, `hashCode()`, and `toString()` - typically 40–60 lines of code to represent two fields. Worse, this boilerplate code drifts: a developer adds a field, forgets to update `equals()`, and introduces a subtle bug that only surfaces in tests months later.

**THE BREAKING POINT:** You read Kotlin code with `data class Point(val x: Int, val y: Int)` - one line, all boilerplate generated correctly and automatically. You look at your Java codebase and see 50 identical, brittle data-class definitions. Or you maintain a type-switch using raw `instanceof` followed by explicit casts - three separate operations, with no compiler guarantee you handled all cases.

**THE INVENTION MOMENT:** Project Amber delivered three interlocking features: **records** eliminate data-class boilerplate; **sealed classes** constrain type hierarchies so the compiler knows all subtypes; **pattern matching for `instanceof`** collapses the check-and-cast into a single expression. Together they enable algebraic data types - a foundational FP concept - in idiomatic Java.

---

### 📘 Textbook Definition

**Records** (final in Java 16, available in Java 17) are immutable data carrier classes declared with a compact syntax; the compiler auto-generates constructor, accessors, `equals`, `hashCode`, and `toString` from the record components. **Sealed classes** (final in Java 17) restrict which classes can extend or implement a type, enabling exhaustive type analysis by the compiler. **Pattern matching for `instanceof`** (final in Java 16) combines the type test and cast into one expression: `if (obj instanceof String s) { ... }` - `s` is bound only when the check succeeds.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Records = auto-boilerplate; Sealed = closed hierarchy; Pattern matching = check+cast in one step.

> Records are like a mint that stamps coins to a fixed design. Sealed classes are like a law declaring the only legal currency denominations. Pattern matching is a vending machine that accepts a coin and knows exactly what denomination it is without you manually measuring it.

**One insight:** These three features are most powerful together: a sealed interface with record implementations gives you exhaustive, type-safe, boilerplate-free algebraic data types - the backbone of robust domain modelling.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A record's components are `final`; the record itself is implicitly `final` - no subclassing.
2. A record's auto-generated `equals` and `hashCode` use all components; you cannot accidentally skip one.
3. A sealed class/interface lists every permitted subtype at compile time via the `permits` clause.
4. Pattern matching binds the variable only in the scope where the type check is true - no unsafe cast possible.
5. Sealed hierarchies + switch expressions produce compiler errors (not warnings) for unhandled cases.

**DERIVED DESIGN:**
- Records enforce immutability and correct value semantics automatically.
- Sealed classes enable *exhaustive switch* expressions - the compiler rejects missing branches.
- Compact record constructors allow validation without writing `this.x = x; this.y = y;` explicitly.
- Record components are accessible via methods named after the component (not `getX()`, just `x()`).

**THE TRADE-OFFS:**

**Gain:** Dramatically reduced boilerplate, compiler-enforced exhaustiveness, less surface area for bugs.

**Cost:** Records are immutable and final - unsuitable for JPA entities (which need mutable, extensible classes) or DTOs requiring field-by-field patching. Sealed hierarchies require all permitted subtypes to be in the same compilation unit (same package or same file).

---

### 🧪 Thought Experiment

**SETUP:** You model a payment result as three possibilities: `Success(transactionId)`, `Failure(errorCode, message)`, and `Pending(referenceId)`.

**WHAT HAPPENS WITHOUT JAVA 17 FEATURES:** You define an interface `PaymentResult` and three classes, each with 40 lines of boilerplate. Your switch over the result uses `instanceof` checks in an `if-else if` chain. A new `Frozen(reason)` case is added. Nobody updates the switch. A `ClassCastException` appears in production six months later.

**WHAT HAPPENS WITH JAVA 17 FEATURES:** You declare a sealed interface with three record implementations. A switch expression over the result is exhaustive - adding `Frozen` without updating the switch is a **compile error**. Total declaration code: 8 lines. The compiler is your safety net.

**THE INSIGHT:** Sealed classes transform a runtime failure mode (unhandled type) into a compile-time error. Pattern matching transforms a three-step operation (check, cast, use) into one expression. The result is a system where the type hierarchy itself encodes correctness constraints.

---

### 🧠 Mental Model / Analogy

> Records are pre-stamped forms with no blank fields. Sealed classes are a closed union - like a traffic light that can only be Red, Yellow, or Green. Pattern matching is a security scanner that identifies the person and grants access in a single step.

- **Pre-stamped form (record)** → components are fixed; filling in all fields is mandatory; copying is exact
- **Closed union (sealed)** → you know every possible value at compile time
- **Security scanner (pattern matching)** → identifies type AND binds variable in one atomic step
- **Compiler exhaustiveness check** → the security system alerts you if a new badge type (subtype) appears without a registered handler

Where this analogy breaks down: sealed classes only close the hierarchy within their compilation unit - external libraries can still be added as permitted subtypes if the `permits` clause names them explicitly.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Records let you write `record Point(int x, int y) {}` instead of 50 lines of boilerplate. Sealed classes let you say "this type can ONLY be one of these specific things." Pattern matching lets you check if something is a type AND use it as that type in one line - no more redundant cast.

**Level 2 - How to use it (junior developer):**
Use records for DTOs, API response objects, and value objects. Use sealed interfaces for result types (success/failure/pending) and command objects. Use `instanceof` pattern matching everywhere you previously wrote `if (x instanceof Foo) { Foo f = (Foo) x; }` - replace all three lines with `if (x instanceof Foo f)`.

**Level 3 - How it works (mid-level engineer):**
Records compile to a final class with private final fields, a canonical constructor, and synthesised `equals/hashCode/toString`. You can add instance methods, implement interfaces, and define a compact constructor (no parameter list) for validation. Sealed classes add a `PermittedSubclasses` class file attribute listing direct subtypes - the compiler reads this to verify switch exhaustiveness. Pattern matching is desugared by the compiler into a type check + local variable binding, with the binding's scope limited to the true branch.

**Level 4 - Why it was designed this way (senior/staff):**
Records, sealed classes, and pattern matching are the Java surface of Project Amber's push toward algebraic data types (sum types and product types). Sum types (sealed + records) model domains where a value is exactly one of a fixed set of alternatives - the core of domain-driven design and functional programming. The compiler's exhaustiveness enforcement eliminates the `default` branch anti-pattern where unhandled new cases fail silently. This mirrors Haskell's `data` types and Scala's `sealed trait` + `case class` pattern - but designed for Java's object-oriented, runtime-flexible ecosystem.

---

### ⚙️ How It Works (Mechanism)

```
  record Point(int x, int y) {}
  ─────────────────────────────────────
  Compiler generates:
    final class Point {
      private final int x;
      private final int y;
      public Point(int x, int y) { ... }
      public int x()    { return x; }
      public int y()    { return y; }
      public boolean equals(Object o) { ... }
      public int hashCode()           { ... }
      public String toString()        { ... }
    }

  sealed interface Shape
    permits Circle, Rectangle {}
  ─────────────────────────────────────
  Class file: PermittedSubclasses attr
  → [Circle, Rectangle]
  Compiler rejects any other subtype
  Switch must cover Circle + Rectangle
  OR include default

  if (shape instanceof Circle c) { ... }
  ─────────────────────────────────────
  Desugars to:
    if (shape instanceof Circle) {
      Circle c = (Circle) shape;
      // c in scope only here
    }
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  Domain: Model a payment result
    │
    ▼
  Declare sealed interface       ← YOU ARE HERE
  sealed interface PaymentResult
    permits Success, Failure, Pending {}

  Declare record variants
    record Success(String txId) {}
    record Failure(int code, String msg) {}
    record Pending(String refId) {}
    │
    ▼
  Switch expression - exhaustive
  String display = switch (result) {
    case Success s  -> "OK: " + s.txId();
    case Failure f  -> "ERR: " + f.msg();
    case Pending p  -> "WAIT: " + p.refId();
    // no default needed - sealed is exhaustive
  };
    │
    ▼
  Compiler verifies all cases covered
  Adding new permitted type without
  updating switch = COMPILE ERROR
```

**FAILURE PATH:**
- Adding a `permits` type without updating all switches → compile error (correct behaviour).
- Using a record as a JPA `@Entity` → runtime error (`Entity` requires a no-arg constructor and mutable state).
- Compact constructor that throws → constructor throws at `new`, propagating to caller.

**WHAT CHANGES AT SCALE:**
Records used as API response types flow through serialisation frameworks. Jackson 2.12+ and Spring Boot 3.x natively support records. Older Jackson requires `@JsonProperty` or constructor-based deserialisation config. At scale, ensure your serialisation framework is record-aware before adopting records in DTOs.

---

### 💻 Code Example

```java
// BAD - verbose, drift-prone data class
public class Money {
    private final long amount;
    private final String currency;
    public Money(long amount, String currency) {
        this.amount   = amount;
        this.currency = currency;
    }
    public long getAmount()     { return amount; }
    public String getCurrency() { return currency; }
    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money m)) return false;
        return amount == m.amount
            && currency.equals(m.currency);
    }
    @Override public int hashCode() {
        return Objects.hash(amount, currency);
    }
    @Override public String toString() {
        return "Money[amount=" + amount
            + ", currency=" + currency + "]";
    }
}
```

```java
// GOOD - record replaces all of the above
public record Money(long amount, String currency) {
    // Compact constructor for validation
    public Money {
        if (amount < 0)
            throw new IllegalArgumentException(
                "amount must be non-negative");
        Objects.requireNonNull(currency,
            "currency must not be null");
    }
}

// Usage - accessors are component names (no get)
Money price = new Money(999L, "GBP");
System.out.println(price.amount());   // 999
System.out.println(price.currency()); // GBP
System.out.println(price);
// Money[amount=999, currency=GBP]
```

```java
// Sealed interface + records = algebraic type
public sealed interface PaymentResult
    permits PaymentResult.Success,
            PaymentResult.Failure,
            PaymentResult.Pending {

    record Success(String transactionId)
        implements PaymentResult {}

    record Failure(int errorCode, String message)
        implements PaymentResult {}

    record Pending(String referenceId)
        implements PaymentResult {}
}

// Pattern matching switch - exhaustive
String display = switch (result) {
    case PaymentResult.Success s ->
        "Paid: " + s.transactionId();
    case PaymentResult.Failure f ->
        "Failed(" + f.errorCode() + "): "
        + f.message();
    case PaymentResult.Pending p ->
        "Pending ref: " + p.referenceId();
    // No default - compiler verifies exhaustiveness
};
```

```java
// BAD - old instanceof pattern (Java 8 style)
if (shape instanceof Circle) {
    Circle c = (Circle) shape;  // redundant cast
    area = Math.PI * c.radius() * c.radius();
} else if (shape instanceof Rectangle) {
    Rectangle r = (Rectangle) shape;
    area = r.width() * r.height();
}

// GOOD - pattern matching (Java 17)
if (shape instanceof Circle c) {
    area = Math.PI * c.radius() * c.radius();
} else if (shape instanceof Rectangle r) {
    area = r.width() * r.height();
}
```

---

### ⚖️ Comparison Table

| Feature | Java 17 | Kotlin | Scala |
|---|---|---|---|
| Data class | `record Point(int x, int y){}` | `data class Point(val x: Int, val y: Int)` | `case class Point(x: Int, y: Int)` |
| Closed hierarchy | `sealed interface` + `permits` | `sealed class` (same file) | `sealed trait` (same file) |
| Pattern matching | `instanceof Foo f` (Java 16+) | `when (x) { is Foo -> ... }` | `match (x) { case Foo f => ... }` |
| Exhaustiveness | switch expression (Java 21 enhanced) | `when` expression | `match` expression |
| Mutable records | Not supported (records are final) | `var` fields in data class | Mutable fields possible |
| JPA compatibility | No (use regular class) | No (`data class` also incompatible) | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Records are like JavaBeans" | Records are immutable value objects. JavaBeans are mutable with `get`/`set` methods. Records have no setters and cannot be subclassed. |
| "Sealed classes prevent all extensions" | Sealed classes only restrict *direct* subclasses. They must be listed in `permits` and reside in the same package (or explicitly named). |
| "Pattern matching removes the need for explicit casts" | Pattern matching binds a variable of the narrower type; it eliminates the *separate* cast line. You still need the check - you just do both at once. |
| "Records work as JPA entities" | JPA requires a no-arg constructor and mutable state for dirty tracking. Records have neither. Use regular classes for entities. |
| "Sealed means only one instance can exist" | Sealed is about restricting subtype definitions, not instance counts. It has nothing to do with the Singleton pattern. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Record used as JPA `@Entity`**
**Symptom:** `HibernateException: No default constructor for entity` at startup, or `IllegalArgumentException: CGLIB proxying failed` for lazy loading.

**Root Cause:** JPA/Hibernate requires a no-arg constructor and mutable state. Records are `final` and have no no-arg constructor by default.

**Diagnostic:**
```bash
# Maven build output on Spring Boot 3 + record entity
[ERROR] HibernateException: No default constructor
        for entity: com.example.Order

# Stacktrace shows Hibernate trying to instantiate
# the record via default constructor reflection
```
**Fix:** Use a regular class for `@Entity`. Use records only for DTOs or value objects passed between layers - never for the persistence layer.

**Prevention:** Add an ArchUnit rule that forbids `@Entity`-annotated records in your test suite.

**Mode 2: Switch over sealed type is not exhaustive**
**Symptom:** `java.lang.MatchException: No match found` at runtime (Java 21+) or silent fall-through when a new subtype is added.

**Root Cause:** Switch statement (not expression) or switch expression with a `default` branch masks the missing case when a new permitted subtype is added.

**Diagnostic:**
```bash
javac -Xlint:all PaymentService.java
# Warning: switch may not be exhaustive
# (only shown in Java 21+ with pattern switches)
```
**Fix:**
```java
// BAD - default hides missing cases
String msg = switch (result) {
    case Success s  -> "ok";
    default         -> "other"; // masks Failure/Pending
};

// GOOD - no default, compiler enforces
String msg = switch (result) {
    case Success s  -> "ok";
    case Failure f  -> "error";
    case Pending p  -> "waiting";
};
```
**Prevention:** Never use `default` in a switch over a sealed type. Let the compiler do the exhaustiveness work.

**Mode 3: Jackson cannot deserialise a record**
**Symptom:** `InvalidDefinitionException: No suitable constructor found for type [record class]` when deserialising JSON into a record.

**Root Cause:** Jackson versions before 2.12 do not understand the canonical constructor of records.

**Diagnostic:**
```bash
# Check Jackson version
mvn dependency:tree | grep "jackson-databind"
# If < 2.12.0, records not natively supported
```
**Fix:** Upgrade to Jackson 2.12+ and add `jackson-module-parameter-names` to preserve constructor parameter names (required for records when not using `@JsonProperty`).

**Prevention:** Verify Jackson version compatibility in your library upgrade checklist before adopting records in API request/response types.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Java Language - class, interface, and inheritance fundamentals
- Java 8 to Java 17 Migration Guide - getting to Java 17 first

**Builds On This (learn these next):**
- Switch Expression - pattern matching in switch (enhanced further in Java 21)
- Spring Core - Spring Boot 3 native record support for `@ConfigurationProperties`
- Testing - records simplify test fixtures and value assertions

**Alternatives / Comparisons:**
- Kotlin Data Class - single-line data class with optional mutability; `copy()` method
- Scala Case Class - sealed trait + case class = Scala's ADT; more powerful pattern matching
- Lombok `@Value` - generates immutable class on Java 8; redundant on Java 17+

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS   Records, Sealed, Pattern Match (17) │
│ PROBLEM SOLVED Boilerplate, unsafe casts, gaps   │
│ KEY INSIGHT  Sealed+Record = compile-safe ADTs   │
│ USE WHEN     DTOs, result types, domain models   │
│ AVOID WHEN   JPA entities, mutable state needed  │
│ TRADE-OFF    Immutability vs ORM compatibility   │
│ ONE-LINER    record=value; sealed=closed; PM=safe│
│ NEXT EXPLORE Switch Expression, Spring Records   │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(C - Design Trade-off)** Records are immutable and final, making them ideal for value objects. But your team uses Hibernate for persistence and needs mutable entities. How would you structure a domain model that uses records at the service/API layer while keeping mutable JPA entities at the persistence layer - and where is the boundary?

2. **(E - First Principles)** A sealed interface's `permits` clause forces all subtypes to be known at compile time. How does this property enable the compiler to guarantee switch exhaustiveness - and why can a switch over a *non-sealed* interface never be statically exhaustive?

3. **(A - System Interaction)** Your team adds a new `PaymentResult.Cancelled` record to a sealed interface that is used in 12 microservices. Which services will fail to compile, which will fail at runtime, and which will behave silently incorrectly - depending on how each handles the switch?
