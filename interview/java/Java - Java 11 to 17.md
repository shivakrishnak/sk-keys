---
layout: default
title: "Java - Java 11 to 17"
parent: "Java"
grand_parent: "Interview Mastery"
nav_order: 5
permalink: /interview/java/java-11-to-17/
topic: Java
subtopic: Java 11 to 17
keywords:
  - Records
  - Sealed Classes
  - Pattern Matching
  - Text Blocks
  - Switch Expressions
difficulty_range: mixed
status: in-progress
version: 2
---

# Records

**TL;DR** - Records are immutable data carriers that auto-generate equals, hashCode, toString, and accessors from a concise declaration, eliminating hundreds of lines of boilerplate for simple value objects.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
A simple data class holding three fields required 60+ lines: private final fields, constructor, getters, equals(), hashCode(), toString(). Every team had its own template or relied on Lombok. When a field was added, developers forgot to update equals or toString, causing subtle bugs in collections and logging.

**THE BREAKING POINT:**
A HashMap lookup fails silently because a developer added a new field to a data class but forgot to regenerate equals/hashCode. The object is in the map but can never be found. This bug class is so common it has a name: the "forgotten equals update."

**THE INVENTION MOMENT:**
"This is exactly why records were created."

**EVOLUTION:**
Manual POJO boilerplate -> IDE generation (still manual maintenance) -> Lombok `@Data`/`@Value` (annotation processor dependency) -> Records (Java 14 preview, Java 16 final). Records are a language feature, not a library - the compiler guarantees correctness.

---

### Textbook Definition

A record is a restricted class that acts as a transparent carrier for an immutable tuple of values. The compiler automatically generates: a canonical constructor, private final fields, accessor methods (same name as fields, no `get` prefix), `equals()` and `hashCode()` based on all components, and `toString()` showing all components. Records are final (cannot be extended), cannot declare instance fields beyond the record components, and can implement interfaces.

---

### Understand It in 30 Seconds

**One line:**
Records turn `class Point { int x; int y; ... 50 lines ... }` into `record Point(int x, int y) {}`.

**One analogy:**

> A record is like a shipping label. It holds data (address, weight, tracking number) and two labels with the same data are considered identical. You don't subclass a shipping label - you just read the data off it.

**One insight:**
Records are not just shorter syntax - they make a semantic commitment: "this class is defined entirely by its data." The compiler enforces this by generating equals/hashCode from all components, making records safe for use as HashMap keys, in Sets, and in pattern matching without any manual maintenance.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Records are implicitly final - no subclassing
2. All components are private final - immutable by construction
3. equals/hashCode use ALL components - no field can be omitted
4. No instance fields beyond components allowed
5. Can have static fields, static methods, instance methods, and implement interfaces

**DERIVED DESIGN:**
Because records are defined by their components, they are ideal targets for pattern matching (`instanceof` pattern, switch pattern). The compiler knows the structure at compile time, enabling destructuring.

**THE TRADE-OFFS:**
**Gain:** Zero boilerplate for data carriers, guaranteed correct equals/hashCode, pattern matching support
**Cost:** Cannot extend other classes, no mutable fields, no field-level customization of equals

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Value objects need equals/hashCode/toString - this is inherent.
**Accidental:** Writing 60 lines of boilerplate for 3 fields is purely accidental complexity that records eliminate.

---

### Mental Model / Analogy

> A record is a named tuple with type safety. Just as a mathematical point (3, 4) is defined entirely by its coordinates, a `record Point(int x, int y)` is defined entirely by its components. Two points with the same coordinates are equal, period.

- "Named tuple" -> record declaration
- "Coordinates" -> record components
- "Equal if same coordinates" -> generated equals/hashCode

Where this analogy breaks down: Records can have methods and implement interfaces, which tuples in most languages cannot.

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A record is a shortcut for creating a simple class that just holds data. Instead of writing dozens of lines of code, you write one line and Java fills in the rest automatically.

**Level 2 - How to use it (junior developer):**

```java
// One line replaces ~60 lines of boilerplate
record Point(int x, int y) {}

Point p = new Point(3, 4);
System.out.println(p.x());     // 3 (accessor)
System.out.println(p);         // Point[x=3, y=4]
System.out.println(p.equals(
    new Point(3, 4)));         // true

// With custom validation
record Range(int min, int max) {
    Range {  // compact constructor
        if (min > max) throw new
            IllegalArgumentException(
                "min > max");
    }
}

// With methods
record Money(BigDecimal amount, String currency) {
    Money add(Money other) {
        if (!currency.equals(other.currency))
            throw new IllegalArgumentException(
                "Currency mismatch");
        return new Money(
            amount.add(other.amount), currency);
    }
}
```

**Level 3 - How it works (mid-level engineer):**

The compiler generates bytecode equivalent to a final class with:

- Private final fields for each component
- A canonical constructor assigning all components
- Accessor methods (no `get` prefix: `x()` not `getX()`)
- `equals()` using `Objects.equals()` on each component
- `hashCode()` using `Objects.hash()` on all components
- `toString()` returning `ClassName[comp1=val1, comp2=val2]`

Records use `invokedynamic` for equals/hashCode/toString generation (similar to lambdas), so the JVM can optimize the generated methods.

The compact constructor validates and normalizes but does not assign fields - assignment happens automatically after the compact constructor body executes.

**Level 4 - Mastery (senior/staff+ engineer):**

Records are the foundation for algebraic data types in Java when combined with sealed classes. `sealed interface Shape permits Circle, Rectangle` with `record Circle(double radius) implements Shape` and `record Rectangle(double w, double h) implements Shape` creates a closed type hierarchy that exhaustive pattern matching can verify at compile time.

Records work naturally with serialization (they use the canonical constructor for deserialization, avoiding the security issues of traditional Java serialization). They are ideal for DTOs, events, messages, and any immutable value object. However, records with mutable component types (e.g., `record Container(List<String> items)`) are not truly immutable - the list can be modified. Use `List.copyOf()` in the compact constructor for defensive copying.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

```
  Source: record Point(int x, int y) {}

  Compiler generates:
  +-- final class Point extends Record
  |   +-- private final int x
  |   +-- private final int y
  |   +-- Point(int x, int y)  [constructor]
  |   +-- int x()              [accessor]
  |   +-- int y()              [accessor]
  |   +-- boolean equals(Object o)
  |   +-- int hashCode()
  |   +-- String toString()
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Traditional data class:**

```java
public final class Point {
    private final int x;
    private final int y;
    public Point(int x, int y) {
        this.x = x; this.y = y;
    }
    public int getX() { return x; }
    public int getY() { return y; }
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point p)) return false;
        return x == p.x && y == p.y;
    }
    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
    @Override
    public String toString() {
        return "Point[x=" + x + ", y=" + y + "]";
    }
}
```

**GOOD - Record:**

```java
record Point(int x, int y) {}
// That's it. All the above is generated.
```

**GOOD - Record with validation and methods:**

```java
record Email(String address) {
    Email {
        if (!address.contains("@"))
            throw new IllegalArgumentException(
                "Invalid email: " + address);
        address = address.toLowerCase().trim();
    }

    String domain() {
        return address.substring(
            address.indexOf('@') + 1);
    }
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Records auto-generate constructor, accessors, equals, hashCode, toString from components
2. Records are final and immutable - no subclassing, no mutable fields
3. Use compact constructor `Record { ... }` for validation without explicit assignment

**Interview one-liner:**
"Records are immutable data carriers that generate equals/hashCode/toString from their components, eliminating boilerplate while making the semantic commitment that the class is defined entirely by its data."

---

### The Surprising Truth

Records use `invokedynamic` for their equals, hashCode, and toString methods rather than generating fixed bytecode. This means the JVM can optimize these methods differently at runtime based on the actual usage patterns. In benchmarks, record equals/hashCode can be faster than hand-written implementations because the JVM can inline and optimize the generated code path.

---

### Interview Deep-Dive

**Q1: When would you NOT use a record? What are the limitations?**

_Why they ask:_ Tests understanding of records beyond the happy path.

_Strong answer:_

Don't use records when:

1. **You need mutability:** Records components are final. If the object's state must change, use a regular class.
2. **You need inheritance:** Records are final and extend `Record`. They cannot extend other classes.
3. **You need to customize equals to exclude fields:** Record equals uses ALL components. You cannot exclude a field from equality.
4. **JPA/Hibernate entities:** Entities need a no-arg constructor, mutable state, and proxy support (non-final). Records satisfy none of these.
5. **Builder pattern:** Records don't support builders natively. For objects with many optional fields, a regular class with builder is better.

Records CAN:

- Implement interfaces
- Have static fields, static methods, and instance methods
- Have compact constructors for validation
- Be local (declared inside a method)
- Be serialized (they use canonical constructor, which is more secure)

---

**Q2: How do records interact with pattern matching?**

_Why they ask:_ Tests knowledge of modern Java features working together.

_Strong answer:_

Records are ideal pattern matching targets because their components are known at compile time:

```java
sealed interface Shape permits Circle, Rect {}
record Circle(double r) implements Shape {}
record Rect(double w, double h) implements Shape {}

// Pattern matching with records (Java 21)
double area(Shape s) {
    return switch (s) {
        case Circle(var r) -> Math.PI * r * r;
        case Rect(var w, var h) -> w * h;
    };
    // Exhaustive - compiler verifies all
    // subtypes are covered
}

// Nested deconstruction
record Line(Point start, Point end) {}
record Point(int x, int y) {}

// Deconstruct both levels at once
if (line instanceof
        Line(Point(var x1, var y1),
             Point(var x2, var y2))) {
    double len = Math.sqrt(
        Math.pow(x2-x1, 2) +
        Math.pow(y2-y1, 2));
}
```

This combination of sealed interfaces + records + pattern matching gives Java algebraic data types similar to Kotlin's `sealed class` or Rust's `enum`.

---

**Q3: What is the compact constructor and how does it differ from a canonical constructor?**

_Why they ask:_ Tests understanding of record construction semantics.

_Strong answer:_

The **canonical constructor** is the full constructor with explicit parameter list and assignment:

```java
record Range(int min, int max) {
    Range(int min, int max) {
        if (min > max)
            throw new IllegalArgumentException();
        this.min = min;
        this.max = max;
    }
}
```

The **compact constructor** omits parameters and assignment - they happen automatically after the body:

```java
record Range(int min, int max) {
    Range {
        // Validation and normalization only
        if (min > max)
            throw new IllegalArgumentException();
        // You can reassign parameter variables
        // for normalization:
        // min = Math.abs(min);
        // this.min = min; happens automatically
    }
}
```

Key differences:

- Compact: no parameter list, no `this.x = x` assignments (auto-generated after body)
- Compact: can reassign parameter variables for normalization (e.g., `address = address.trim()`)
- Canonical: full control, explicit assignments required
- Compact is preferred for simple validation/normalization

---

**Q4: How should you handle mutable components in records?**

_Why they ask:_ Tests awareness of shallow immutability.

_Strong answer:_

Records make fields `final` but if a component is a mutable type (List, Map, Date), the contents can still be modified:

```java
// DANGER: mutable component
record Team(String name, List<String> members) {}

Team t = new Team("Dev", new ArrayList<>(
    List.of("Alice", "Bob")));
t.members().add("Mallory"); // mutated!
```

Fix with defensive copy in compact constructor:

```java
record Team(String name, List<String> members) {
    Team {
        members = List.copyOf(members);
        // Now truly immutable
    }
}

Team t = new Team("Dev",
    List.of("Alice", "Bob"));
t.members().add("X"); // throws
// UnsupportedOperationException
```

Rules:

- Primitive components: naturally immutable
- String, Integer, etc.: naturally immutable
- Collections: use `List.copyOf()`, `Map.copyOf()`, `Set.copyOf()`
- Custom objects: use immutable types or defensive copy
- Date/Calendar: use `java.time` classes instead (immutable)

---

**Q5: How do records compare to Lombok's @Value? When would you still use Lombok?**

_Why they ask:_ Tests practical migration knowledge.

_Strong answer:_

| Feature          | Record                         | Lombok @Value                  |
| ---------------- | ------------------------------ | ------------------------------ |
| Language level   | Built-in (Java 16+)            | Library (annotation processor) |
| Inheritance      | Cannot extend classes          | Can extend classes             |
| Builder          | Not built-in                   | `@Builder` support             |
| Selective equals | All components always          | `@EqualsAndHashCode.Exclude`   |
| Accessor naming  | `x()` (no prefix)              | `getX()`                       |
| Serialization    | Secure (canonical constructor) | Standard (unsafe)              |

**Still use Lombok when:**

- Stuck on Java < 16
- Need `@Builder` for many-field objects
- Need to exclude fields from equals
- Need to extend a base class
- Need mutable fields with `@Data`

**Migrate to records when:**

- Simple immutable value objects
- DTOs, events, messages
- Pattern matching targets
- No inheritance or builder needed

In a new Java 16+ project, records should be the default for value objects. Use Lombok only for cases records cannot handle.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Records. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Sealed Classes

**TL;DR** - Sealed classes restrict which classes can extend them, giving the compiler exhaustive knowledge of a type hierarchy for pattern matching and enabling true algebraic data types in Java.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
A class is either `final` (no subclasses) or open (any class anywhere can extend it). There is no middle ground. When you write `if (shape instanceof Circle)`, the compiler cannot warn you about missing cases because it does not know all possible subtypes. Adding a new subtype silently breaks existing switch/if-else chains.

**THE BREAKING POINT:**
A payment processing system uses `abstract class PaymentMethod` with `CreditCard`, `BankTransfer`, and `Wallet` subclasses. A new developer adds `Crypto extends PaymentMethod` in a different module. The settlement code's if-else chain does not handle crypto payments. Funds are accepted but never settled. The bug runs for a week before discovery.

**THE INVENTION MOMENT:**
"This is exactly why sealed classes were created."

**EVOLUTION:**
Final classes (no extension) and open classes (unlimited extension) since Java 1.0 -> Sealed classes (Java 15 preview, Java 17 final) -> Exhaustive pattern matching with sealed types (Java 21).

---

### Textbook Definition

A sealed class or interface declares a fixed set of permitted subtypes using the `permits` clause. Only the permitted classes can extend or implement the sealed type. The compiler knows all possible subtypes at compile time, enabling exhaustive switch expressions and pattern matching without a default branch.

---

### Understand It in 30 Seconds

**One line:**
Sealed classes tell the compiler "these are the ONLY subtypes" - no surprises, no missing cases.

**One analogy:**

> A sealed class is like a members-only club with a fixed roster. The bouncer (compiler) has the complete list. No one can sneak in. When you need to check who's inside, you know you've checked everyone.

**One insight:**
Sealed classes solve the "expression problem" for Java. Before sealed classes, adding a new subtype was easy (just extend) but adding a new operation was hard (must find all switch/if-else chains). Sealed classes make both safe: the compiler tells you when a switch is not exhaustive after adding a new permitted subtype.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Permitted subtypes are declared in the `permits` clause (or inferred if in the same file)
2. Permitted subtypes must directly extend the sealed type
3. Each permitted subtype must be `final`, `sealed`, or `non-sealed`
4. The compiler has complete knowledge of the type hierarchy

**DERIVED DESIGN:**
Combined with records and pattern matching, sealed classes create algebraic data types (sum types). `sealed interface Result permits Success, Failure` with `record Success(T value) implements Result` is Java's equivalent of Rust's `enum Result<T, E>`.

**THE TRADE-OFFS:**
**Gain:** Compile-time exhaustiveness checking, safe type hierarchies, enables pattern matching
**Cost:** Less extensibility (by design), all subtypes must be known at compile time

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Sometimes a type hierarchy is genuinely closed - there are exactly N variants and no more.
**Accidental:** The requirement that permitted subtypes be in the same module/package is a limitation of Java's compilation model.

---

### Mental Model / Analogy

> Sealed classes are like an enum on steroids. An enum has fixed constants with no data variation. A sealed class has fixed subtypes where each can carry different data. `enum Color { RED, GREEN, BLUE }` becomes `sealed interface Shape permits Circle, Rectangle, Triangle` where each variant has its own fields.

- "Enum constants" -> permitted subtypes
- "Fixed set" -> sealed constraint
- "Each constant can vary" -> records with different components

Where this analogy breaks down: Unlike enums, sealed subtypes can have their own methods, constructors, and even be sealed themselves (creating a hierarchy).

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A sealed class says "only these specific classes are allowed to be my children." This lets the compiler check that you have handled every possible type.

**Level 2 - How to use it (junior developer):**

```java
sealed interface Shape
    permits Circle, Rectangle, Triangle {}

record Circle(double radius)
    implements Shape {}
record Rectangle(double width, double height)
    implements Shape {}
record Triangle(double a, double b, double c)
    implements Shape {}

// Compiler ensures all cases are covered
double area(Shape s) {
    return switch (s) {
        case Circle c -> Math.PI * c.radius()
                         * c.radius();
        case Rectangle r -> r.width()
                            * r.height();
        case Triangle t -> {
            double p = (t.a()+t.b()+t.c()) / 2;
            yield Math.sqrt(p * (p-t.a())
                * (p-t.b()) * (p-t.c()));
        }
        // No default needed - exhaustive!
    };
}
```

**Level 3 - How it works (mid-level engineer):**

Each permitted subtype must declare one of three modifiers:

- `final` or `record`: this branch ends here
- `sealed`: this branch has its own fixed subtypes
- `non-sealed`: this branch is open for extension (escape hatch)

```java
sealed interface Animal permits Dog, Cat, Fish {}
final class Dog implements Animal {}
sealed class Cat implements Animal
    permits HouseCat, WildCat {}
non-sealed class Fish implements Animal {}
// Anyone can extend Fish
```

The `permits` clause can be omitted if all subtypes are in the same source file - the compiler infers them.

**Level 4 - Mastery (senior/staff+ engineer):**

Sealed classes + records create discriminated unions (sum types) that enable functional programming patterns in Java:

```java
// Result type (like Rust's Result<T, E>)
sealed interface Result<T>
    permits Success, Failure {}
record Success<T>(T value)
    implements Result<T> {}
record Failure<T>(String error, Exception cause)
    implements Result<T> {}

// Usage with exhaustive matching
Result<User> result = findUser(id);
String msg = switch (result) {
    case Success<User>(var user) ->
        "Found: " + user.name();
    case Failure<User>(var err, var cause) ->
        "Error: " + err;
};
```

This pattern eliminates the need for checked exceptions in many cases and is superior to Optional when you need to carry error information. It is the foundation for functional error handling in Java.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

```
  sealed interface Shape permits A, B, C
       |
  Compiler records permitted subtypes
  in the class file (PermittedSubclasses attr)
       |
  switch(shape) {
    case A -> ...
    case B -> ...
    // Missing C?
  }
       |
  Compiler ERROR: switch not exhaustive
  "Shape permits Circle, Rectangle, Triangle
   but only Circle, Rectangle are covered"
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**GOOD - Domain modeling with sealed types:**

```java
sealed interface PaymentResult
    permits Approved, Declined, PendingReview {}

record Approved(String txnId, BigDecimal amount)
    implements PaymentResult {}
record Declined(String reason, String code)
    implements PaymentResult {}
record PendingReview(String txnId,
    String reviewReason)
    implements PaymentResult {}

// Every handler must cover all cases
String processResult(PaymentResult result) {
    return switch (result) {
        case Approved a ->
            "Payment " + a.txnId()
            + " approved for " + a.amount();
        case Declined d ->
            "Declined: " + d.reason();
        case PendingReview p ->
            "Under review: "
            + p.reviewReason();
    };
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `sealed` + `permits` declares all allowed subtypes - compiler knows the full set
2. Subtypes must be `final`, `sealed`, or `non-sealed`
3. Enables exhaustive switch/pattern matching without default

**Interview one-liner:**
"Sealed classes declare a closed set of permitted subtypes, giving the compiler exhaustive type knowledge for pattern matching and preventing unauthorized extension of controlled type hierarchies."

---

### The Surprising Truth

Sealed classes make the `Visitor` design pattern nearly obsolete. The Visitor pattern exists because Java lacked exhaustive type matching - you needed double dispatch to safely handle all subtypes. With sealed classes and pattern matching switches, you get compile-time exhaustiveness checking directly, making the Visitor's ceremony unnecessary.

---

### Interview Deep-Dive

**Q1: How do sealed classes compare to enums? When would you use each?**

_Why they ask:_ Tests understanding of type modeling choices.

_Strong answer:_

**Enums:** Fixed set of singleton constants. Each constant is the same type. Can have fields and methods, but all constants share the same structure. Use for finite, uniform values (days, statuses, directions).

**Sealed classes:** Fixed set of subtypes. Each subtype can have different structure (different fields, different behavior). Use for finite, non-uniform variants (shapes with different dimensions, results with different payloads).

```java
// Enum: same structure for all
enum Status { ACTIVE, INACTIVE, SUSPENDED }

// Sealed: different structure per variant
sealed interface Event permits
    OrderCreated, OrderShipped, OrderCancelled {}
record OrderCreated(String orderId,
    List<Item> items) implements Event {}
record OrderShipped(String orderId,
    String trackingNo) implements Event {}
record OrderCancelled(String orderId,
    String reason) implements Event {}
```

Rule of thumb: if every variant carries the same data (or no data), use enum. If variants carry different data, use sealed interface + records.

---

**Q2: What does `non-sealed` mean and when would you use it?**

_Why they ask:_ Tests understanding of the escape hatch mechanism.

_Strong answer:_

`non-sealed` reopens a branch of a sealed hierarchy for unrestricted extension. It's an escape hatch when some parts of the hierarchy should be closed but one branch needs flexibility:

```java
sealed interface Logger permits
    FileLogger, ConsoleLogger, CustomLogger {}

final class FileLogger implements Logger {}
final class ConsoleLogger implements Logger {}
non-sealed class CustomLogger implements Logger {}
// Third parties can extend CustomLogger
class SlackLogger extends CustomLogger {}
class DatadogLogger extends CustomLogger {}
```

The trade-off: the compiler can no longer guarantee exhaustiveness for `CustomLogger` subtypes. A switch with `case CustomLogger` covers all custom subtypes as one branch, but you lose type-specific handling.

Use `non-sealed` when:

- You want most of the hierarchy closed but one extension point
- Framework code where users must provide implementations
- Migration path from open to sealed (gradually seal branches)

---

**Q3: How do sealed classes help with serialization safety?**

_Why they ask:_ Tests security and architecture awareness.

_Strong answer:_

Traditional Java serialization has a well-known vulnerability: a malicious payload can instantiate any class on the classpath by manipulating the serialized stream. Sealed classes mitigate this because:

1. The set of permitted subtypes is known at compile time and recorded in the class file
2. Deserialization can verify that the incoming type is in the permitted set
3. Combined with records (which use canonical constructors for deserialization), there are no hidden `readObject()` hooks

```java
sealed interface Command permits
    CreateUser, DeleteUser, UpdateUser {}
record CreateUser(String name, String email)
    implements Command {}
// ...

// Deserializer knows: only CreateUser,
// DeleteUser, UpdateUser are valid
// Any other type in the stream is rejected
```

This is especially valuable for message-driven architectures where commands/events are serialized across service boundaries. The sealed type acts as a schema that both serialization and pattern matching can enforce.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Sealed Classes. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Pattern Matching

**TL;DR** - Pattern matching lets you test a value's type and extract its components in one step, replacing verbose instanceof checks and casts with concise, safe, and exhaustive expressions.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Testing types required a three-step dance: (1) `instanceof` check, (2) explicit cast, (3) variable assignment. This was verbose, error-prone (wrong cast type), and the compiler could not verify exhaustiveness.

**THE BREAKING POINT:**
A 200-line method with 15 `instanceof` checks, each followed by a cast. A developer changes one cast to the wrong type. The code compiles (casts are unchecked at compile time). It crashes in production with `ClassCastException` on edge case #12.

**THE INVENTION MOMENT:**
"This is exactly why pattern matching was created."

**EVOLUTION:**
`instanceof` + cast (Java 1.0) -> `instanceof` pattern matching (Java 14 preview, Java 16 final) -> switch pattern matching (Java 17 preview, Java 21 final) -> record pattern deconstruction (Java 21) -> primitive patterns (future).

---

### Textbook Definition

Pattern matching is a language feature that combines a type test with a variable binding in a single operation. Instead of writing `if (obj instanceof String) { String s = (String) obj; }`, you write `if (obj instanceof String s)`. Switch pattern matching extends this to switch expressions, enabling type-based branching with exhaustiveness checking when used with sealed types.

---

### Understand It in 30 Seconds

**One line:**
Pattern matching combines "is it this type?" and "give me the value" into one safe expression.

**One analogy:**

> Traditional instanceof is like checking someone's ID, writing down their name, then using the name. Pattern matching is like a smart scanner that checks the ID and gives you the name in one beep.

**One insight:**
Pattern matching is not just syntactic sugar for instanceof + cast. In switch expressions with sealed types, the compiler verifies exhaustiveness - if you add a new permitted subtype, every switch that doesn't handle it becomes a compile error. This turns runtime `ClassCastException` into compile-time errors.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. A pattern binds a variable only when the match succeeds (flow scoping)
2. The pattern variable is in scope where the compiler can prove the match succeeded
3. Switch patterns support guards (`case String s when s.length() > 10`)
4. With sealed types, switch patterns are exhaustive - no default needed

**DERIVED DESIGN:**
Record patterns enable deconstruction: `case Point(int x, int y)` both matches the type AND extracts the components. Nested patterns enable deep deconstruction: `case Line(Point(var x1, var y1), Point(var x2, var y2))`.

**THE TRADE-OFFS:**
**Gain:** Less code, safer (no explicit casts), exhaustive checking with sealed types
**Cost:** New syntax to learn, flow scoping can be subtle, null handling in switches requires explicit case

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Pattern matching lets you check what type something is and use it as that type in one step, instead of checking first and converting separately.

**Level 2 - How to use it (junior developer):**

```java
// Before: instanceof + cast (3 steps)
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}

// After: pattern matching (1 step)
if (obj instanceof String s) {
    System.out.println(s.length());
}

// Switch pattern matching (Java 21)
String describe(Object obj) {
    return switch (obj) {
        case Integer i -> "int: " + i;
        case String s -> "str: " + s;
        case null -> "null";
        default -> "other: " + obj;
    };
}
```

**Level 3 - How it works (mid-level engineer):**

Flow scoping means the pattern variable is only in scope where the compiler can guarantee the match succeeded:

```java
// Variable 's' is in scope in the true branch
if (obj instanceof String s) {
    // s is in scope here
}
// s is NOT in scope here

// Also works with && (short-circuit)
if (obj instanceof String s && s.length() > 5) {
    // s is in scope - guaranteed String
}

// Does NOT work with || (can't guarantee)
// if (obj instanceof String s
//     || s.length() > 5) // ERROR
```

**Level 4 - Mastery (senior/staff+ engineer):**

Guarded patterns allow additional conditions:

```java
return switch (shape) {
    case Circle c when c.radius() > 100 ->
        "large circle";
    case Circle c -> "small circle";
    case Rectangle r when r.width() == r.height()
        -> "square";
    case Rectangle r -> "rectangle";
    case Triangle t -> "triangle";
};
```

Pattern dominance: the compiler checks that more specific patterns come before more general ones. `case Circle c` after `case Shape s` is unreachable and causes a compile error.

Record patterns with nested deconstruction enable deep matching without temporary variables:

```java
sealed interface Expr permits Num, Add, Mul {}
record Num(int value) implements Expr {}
record Add(Expr left, Expr right)
    implements Expr {}
record Mul(Expr left, Expr right)
    implements Expr {}

int eval(Expr expr) {
    return switch (expr) {
        case Num(var v) -> v;
        case Add(var l, var r) ->
            eval(l) + eval(r);
        case Mul(var l, var r) ->
            eval(l) * eval(r);
    };
}
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Traditional instanceof chain:**

```java
double area(Object shape) {
    if (shape instanceof Circle) {
        Circle c = (Circle) shape;
        return Math.PI * c.radius() * c.radius();
    } else if (shape instanceof Rectangle) {
        Rectangle r = (Rectangle) shape;
        return r.width() * r.height();
    }
    throw new IllegalArgumentException(
        "Unknown shape");
}
```

**GOOD - Pattern matching switch:**

```java
double area(Shape shape) {
    return switch (shape) {
        case Circle(var r) -> Math.PI * r * r;
        case Rectangle(var w, var h) -> w * h;
        case Triangle(var a, var b, var c) -> {
            double p = (a + b + c) / 2;
            yield Math.sqrt(
                p*(p-a)*(p-b)*(p-c));
        }
    };
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `instanceof String s` combines type check + cast + variable binding in one step
2. Switch patterns with sealed types are exhaustive - no default needed
3. Record patterns deconstruct: `case Point(var x, var y)` extracts components

**Interview one-liner:**
"Pattern matching unifies type testing and extraction into a single expression, and combined with sealed types, enables exhaustive, compile-time-verified type-based branching."

---

### The Surprising Truth

Null handling in pattern matching switches is explicit and deliberate. Before Java 21, a switch on a reference type would throw `NullPointerException` on null input. With pattern matching switches, you can add `case null ->` as an explicit branch. This makes null handling visible and intentional rather than a runtime surprise.

---

### Interview Deep-Dive

**Q1: How does pattern matching in switches differ from traditional switch statements?**

_Why they ask:_ Tests understanding of the evolution and new capabilities.

_Strong answer:_

Traditional switch: matches only on constants (int, String, enum). Falls through by default. Statements only (pre-Java 14).

Pattern matching switch:

1. Matches on types, not just constants
2. Binds variables in the matched branch
3. Supports guards (`when` clause)
4. Exhaustive with sealed types (no default needed)
5. Expression form returns values
6. No fall-through in arrow syntax

```java
// Traditional: constant matching
switch (status) {
    case "ACTIVE": handle(); break;
    case "INACTIVE": disable(); break;
    default: throw new IllegalStateException();
}

// Pattern matching: type + guard matching
return switch (event) {
    case OrderCreated o when o.items().isEmpty()
        -> handleEmpty(o);
    case OrderCreated o
        -> handleOrder(o);
    case OrderCancelled c
        -> handleCancel(c);
    case null
        -> handleNull();
};
```

---

**Q2: Explain flow scoping for pattern variables. Where is the variable in scope?**

_Why they ask:_ Tests understanding of a subtle and unique feature.

_Strong answer:_

The pattern variable is in scope wherever the compiler can prove the pattern matched:

```java
// In scope in true branch
if (x instanceof String s) {
    // s in scope
}

// In scope after negated check
// (compiler knows x is NOT String)
if (!(x instanceof String s)) {
    return; // x is not String, s not in scope
}
// s IS in scope here (x must be String
// to reach this point)

// Works with && (both sides must be true)
if (x instanceof String s && s.length() > 0) {
    // s in scope
}

// DOES NOT work with || (only one side
// needs to be true - can't guarantee match)
// if (x instanceof String s || s.isEmpty())
// COMPILE ERROR
```

In switch expressions, the pattern variable is scoped to that case's arrow expression or block. It is not visible in other cases.

This scoping is purely a compiler analysis - no runtime checks. The variable binding is erased at bytecode level, just like a normal local variable after a cast.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Pattern Matching. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Text Blocks

**TL;DR** - Text blocks provide multi-line string literals with automatic indentation management, eliminating escape character hell for JSON, SQL, HTML, and other embedded text.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Embedding multi-line strings (JSON, SQL, HTML) in Java code required string concatenation with `+`, explicit `\n` for newlines, and escaped quotes `\"` everywhere. A 10-line JSON template became 20 lines of unreadable Java concatenation.

**THE BREAKING POINT:**
A developer writes a SQL query as a concatenated string. They miss a space before `WHERE`, creating `...table_nameWHERE...`. The query fails in production. The concatenation mess made the missing space invisible in code review.

**THE INVENTION MOMENT:**
"This is exactly why text blocks were created."

**EVOLUTION:**
String concatenation with `+` and `\n` -> `String.format()` -> `StringBuilder` -> Text blocks (Java 13 preview, Java 15 final).

---

### Textbook Definition

A text block is a multi-line string literal delimited by triple double-quotes (`"""`). It begins on the line after the opening delimiter and ends at the closing delimiter. The compiler strips common leading whitespace (incidental indentation), normalizes line terminators to `\n`, and allows embedded double quotes without escaping.

---

### Understand It in 30 Seconds

**One line:**
Text blocks let you write multi-line strings exactly as they should appear, no escapes needed.

**One analogy:**

> Traditional strings are like dictating a letter over the phone: "new line, quote, backslash n." Text blocks are like handwriting the letter directly - what you see is what you get.

**One insight:**
The closing `"""` position matters - it determines how much leading whitespace is stripped. Moving the closing delimiter left or right adjusts the indentation of the entire block. This is the single most important rule for text blocks.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of writing strings with `\n` and `\"` everywhere, you write the text exactly how it should look, between triple quotes.

**Level 2 - How to use it (junior developer):**

```java
// Before: escape hell
String json = "{\n" +
    "  \"name\": \"Alice\",\n" +
    "  \"age\": 30\n" +
    "}";

// After: text block
String json = """
        {
          "name": "Alice",
          "age": 30
        }
        """;
// Result is identical
```

**Level 3 - How it works (mid-level engineer):**

The compiler processes text blocks in three steps:

1. **Line terminator normalization:** All line endings become `\n`
2. **Incidental whitespace removal:** Common leading whitespace is stripped (determined by the leftmost content line or the closing `"""` position)
3. **Escape processing:** `\n`, `\t`, `\"` still work; new escape `\` at end of line continues the line (no newline)

```java
// Indentation control via """ position
String a = """
        Hello
        World
        """;
// "Hello\nWorld\n" (8 spaces stripped)

String b = """
        Hello
        World
""";
// "        Hello\n        World\n"
// (0 spaces stripped - """ at column 0)
```

**Level 4 - Mastery (senior/staff+ engineer):**

Text blocks combined with `String.formatted()` (Java 15) or `String.format()` create powerful template patterns:

```java
String sql = """
    SELECT %s FROM %s
    WHERE status = '%s'
    ORDER BY created_at DESC
    LIMIT %d
    """.formatted(columns, table,
        status, limit);
```

For security-sensitive use (SQL, HTML), text blocks should be used with parameterized queries or template engines, not string interpolation, to prevent injection attacks. The readability of text blocks can mask the danger of string interpolation with user input.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Concatenation for SQL:**

```java
String query = "SELECT u.name, u.email " +
    "FROM users u " +
    "JOIN orders o ON u.id = o.user_id " +
    "WHERE o.status = ? " +
    "AND o.created_at > ? " +
    "ORDER BY o.created_at DESC";
```

**GOOD - Text block:**

```java
String query = """
    SELECT u.name, u.email
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE o.status = ?
    AND o.created_at > ?
    ORDER BY o.created_at DESC
    """;
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Triple quotes `"""` on their own line, content starts next line
2. Closing `"""` position controls indentation stripping
3. No need to escape `"` inside text blocks (only `"""` needs escaping)

**Interview one-liner:**
"Text blocks are multi-line string literals delimited by triple quotes that auto-strip incidental indentation and normalize line endings, replacing escape-heavy string concatenation for SQL, JSON, and HTML."

---

### The Surprising Truth

Text blocks support two new escape sequences: `\s` (a space that prevents trailing whitespace stripping) and `\` at end of line (line continuation - suppresses the newline). The `\` continuation means you can write long single-line strings across multiple source lines without inserting unwanted newlines.

---

### Interview Deep-Dive

**Q1: How does incidental whitespace stripping work? What determines how much whitespace is removed?**

_Why they ask:_ Tests understanding of the most confusing text block feature.

_Strong answer:_

The compiler determines "incidental" whitespace by finding the minimum indentation across all non-blank content lines AND the closing `"""` line. That minimum is stripped from every line.

```java
// 8 spaces before each line, 8 before """
String a = """
        line1
        line2
        """;
// min indent = 8 -> strip 8
// Result: "line1\nline2\n"

// 8 spaces before lines, 4 before """
String b = """
        line1
        line2
    """;
// min indent = 4 (""" position wins)
// Result: "    line1\n    line2\n"

// Mixed indentation
String c = """
        line1
            line2
        """;
// min indent = 8 -> strip 8
// Result: "line1\n    line2\n"
// (line2 retains 4 extra spaces)
```

Practical rule: position the closing `"""` at the column where you want the left margin of the text to be.

---

**Q2: Can text blocks be used with `String.format()` or `formatted()`? What are the security implications?**

_Why they ask:_ Tests practical usage and security awareness.

_Strong answer:_

Yes, text blocks work with both:

```java
String html = """
    <div class="%s">
        <h1>%s</h1>
        <p>%s</p>
    </div>
    """.formatted(cssClass, title, body);
```

**Security warning:** If `title` or `body` come from user input, this is an XSS vulnerability. Text blocks make string interpolation look clean and natural, which can mask injection risks.

Rules:

- SQL: always use parameterized queries (`?` placeholders), never string interpolation
- HTML: use template engines (Thymeleaf, Freemarker) that auto-escape
- JSON: use Jackson/Gson for serialization, not text block templates
- Test data, logging, documentation: text block formatting is safe

```java
// DANGEROUS: SQL injection possible
String sql = """
    SELECT * FROM users WHERE name = '%s'
    """.formatted(userInput);

// SAFE: parameterized query
String sql = """
    SELECT * FROM users WHERE name = ?
    """;
stmt.setString(1, userInput);
```

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Text Blocks. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Switch Expressions

**TL;DR** - Switch expressions return values, use arrow syntax to prevent fall-through, and support pattern matching, making switch a powerful expression instead of a bug-prone statement.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Traditional switch statements have three notorious problems: (1) fall-through by default (missing `break` causes silent bugs), (2) cannot return values (must use mutable variable), (3) limited to constants (no type matching). These made switch a source of bugs rather than clarity.

**THE BREAKING POINT:**
A developer adds a new enum constant but forgets to add a `case` in the switch statement. No compiler warning. The code falls through to `default`, which silently returns a wrong value. The bug persists for months because the wrong value is plausible.

**THE INVENTION MOMENT:**
"This is exactly why switch expressions were created."

**EVOLUTION:**
Switch statements with fall-through (Java 1.0) -> switch expressions with arrow syntax (Java 12 preview, Java 14 final) -> switch pattern matching (Java 17 preview, Java 21 final).

---

### Textbook Definition

A switch expression evaluates to a value, uses arrow (`->`) syntax to prevent fall-through, and the compiler enforces exhaustiveness. Combined with pattern matching (Java 21), it supports type-based branching, guards, null handling, and record deconstruction.

---

### Understand It in 30 Seconds

**One line:**
Switch expressions return a value, prevent fall-through, and the compiler ensures you handle every case.

**One analogy:**

> Old switch is like a waterslide - once you enter a case, you slide through all remaining cases unless you explicitly jump off (break). New switch expressions are like elevator buttons - you press one floor, go there, and stop.

**One insight:**
The arrow syntax (`->`) is not just cosmetic. It fundamentally changes the semantics: no fall-through, expression-based (returns a value), and the compiler enforces that every possible value is handled. Missing a case with arrow syntax is a compile error, not a runtime mystery.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Switch expressions let you pick a result based on a value, like a lookup table that always gives you an answer. The compiler makes sure you haven't forgotten any options.

**Level 2 - How to use it (junior developer):**

```java
// Old switch statement (bug-prone)
String label;
switch (day) {
    case MONDAY:
    case TUESDAY:
        label = "early week"; // fall-through!
        break;
    case WEDNESDAY:
        label = "midweek";
        break;
    default:
        label = "other";
}

// New switch expression (safe)
String label = switch (day) {
    case MONDAY, TUESDAY -> "early week";
    case WEDNESDAY -> "midweek";
    case THURSDAY, FRIDAY -> "late week";
    case SATURDAY, SUNDAY -> "weekend";
};
// Exhaustive - compiler checks all enum values
```

**Level 3 - How it works (mid-level engineer):**

Switch expressions support two syntaxes:

- Arrow (`->`) - no fall-through, expression result
- Colon (`:`) - traditional syntax but with `yield` for returning values

```java
// Arrow syntax (preferred)
int result = switch (x) {
    case 1 -> 10;
    case 2 -> 20;
    default -> 0;
};

// Block with yield for complex logic
int result = switch (x) {
    case 1 -> {
        log("case 1");
        yield 10;
    }
    case 2 -> 20;
    default -> 0;
};
```

**Level 4 - Mastery (senior/staff+ engineer):**

Combined with sealed types and pattern matching, switch expressions become Java's primary control flow mechanism for type-safe branching:

```java
sealed interface Expr permits Num, BinOp {}
record Num(int val) implements Expr {}
record BinOp(Expr l, String op, Expr r)
    implements Expr {}

int eval(Expr e) {
    return switch (e) {
        case Num(var v) -> v;
        case BinOp(var l, var op, var r)
            when op.equals("+") ->
                eval(l) + eval(r);
        case BinOp(var l, var op, var r)
            when op.equals("*") ->
                eval(l) * eval(r);
        case BinOp b ->
            throw new UnsupportedOperationException(
                "Unknown op: " + b.op());
    };
}
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Fall-through bug in traditional switch:**

```java
// Missing break causes fall-through!
int days;
switch (month) {
    case FEBRUARY:
        days = 28;
        // MISSING BREAK - falls through!
    case APRIL: case JUNE:
        days = 30;
        break;
    default:
        days = 31;
}
// FEBRUARY silently gets 30!
```

**GOOD - Switch expression:**

```java
int days = switch (month) {
    case FEBRUARY -> 28;
    case APRIL, JUNE, SEPTEMBER,
         NOVEMBER -> 30;
    default -> 31;
};
// No fall-through possible
// Compiler error if non-exhaustive
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Arrow syntax (`->`) prevents fall-through and returns values
2. Compiler enforces exhaustiveness - missing cases are compile errors
3. `yield` returns a value from a block in switch expressions

**Interview one-liner:**
"Switch expressions use arrow syntax to eliminate fall-through bugs, return values directly, and the compiler enforces exhaustiveness, making switch a safe, expression-based control flow mechanism."

---

### The Surprising Truth

You can mix arrow and colon syntax in the same file but not in the same switch. However, the Java language team deliberately designed switch expressions to make the old colon syntax feel uncomfortable - the new arrow syntax is so much cleaner that teams naturally migrate. Java 21's pattern matching switches only support arrow syntax, making the migration path inevitable.

---

### Interview Deep-Dive

**Q1: What is the difference between `yield` and `return` in switch expressions?**

_Why they ask:_ Tests understanding of expression semantics vs method semantics.

_Strong answer:_

`yield` produces the value of a switch expression branch. `return` exits the entire method:

```java
int compute(int x) {
    int result = switch (x) {
        case 1 -> {
            log("computing");
            yield 10; // switch gets value 10
        }
        case 2 -> {
            return -1; // METHOD returns -1
            // switch expression is abandoned
        }
        default -> 0;
    };
    return result; // only reached for case 1
}
```

`yield` is only valid inside a switch expression block. In arrow syntax without a block (`case 1 -> 10`), the value is implicitly yielded - no `yield` keyword needed. `yield` is needed only inside `-> { ... }` blocks.

---

**Q2: How does exhaustiveness checking work with enums vs sealed types vs other types?**

_Why they ask:_ Tests understanding of when default is required.

_Strong answer:_

- **Enums:** Compiler knows all constants. If every constant has a case, no default needed. If a new constant is added and the switch is not updated, it becomes a compile error.

- **Sealed types:** Compiler knows all permitted subtypes. Same exhaustiveness rules as enums. Adding a new permitted subtype without updating switches causes compile errors everywhere.

- **Primitives/String/other:** Cannot be exhaustive without `default`. The compiler cannot enumerate all possible ints or Strings, so `default` is always required.

```java
// Exhaustive: enum
String r = switch (season) {
    case SPRING -> "bloom";
    case SUMMER -> "sun";
    case FALL -> "leaves";
    case WINTER -> "snow";
}; // no default needed

// Exhaustive: sealed type
String r = switch (shape) {
    case Circle c -> "circle";
    case Rectangle r -> "rect";
}; // no default needed (if sealed)

// NOT exhaustive: String
String r = switch (input) {
    case "yes" -> "confirmed";
    case "no" -> "denied";
    default -> "unknown"; // REQUIRED
};
```

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Switch Expressions. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

