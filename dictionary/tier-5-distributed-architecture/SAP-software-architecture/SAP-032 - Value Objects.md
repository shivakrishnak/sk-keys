---
id: SAP-032
title: Value Objects
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-023, SAP-043
used_by: SAP-030
related: SAP-030, SAP-033
tags:
  - architecture
  - ddd
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /software-architecture/value-objects/
  - deep-dive
  - advanced
---

# SAP-032 - Value Objects

⚡ TL;DR - A Value Object is a domain concept defined entirely by its attributes - it has no identity, is immutable, and two value objects with the same attributes are equal regardless of which instance they are.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | SAP-023, SAP-043 |
| **Used by**    | SAP-030          |
| **Related**    | SAP-030, SAP-033 |

---

### 🔥 The Problem This Solves

**THE PRIMITIVE OBSESSION PROBLEM:**
A financial system uses `BigDecimal` for money and `String` for currency codes. A method signature is `transfer(BigDecimal amount, String currency, String fromAccount, String toAccount)`. You can accidentally call it as `transfer(amount, fromAccount, currency, toAccount)` - the types are wrong, the compiler doesn't catch it, and money moves to the wrong account. Worse: what does `amount.subtract(fee)` return when `amount` is in GBP and `fee` is in USD?

**THE VALUE OBJECT SOLUTION:**
Replace primitives with domain-typed Value Objects: `Money(amount, currency)` and `AccountId`. The method becomes `transfer(Money amount, AccountId from, AccountId to)`. You can't accidentally swap a `String` and an `AccountId`. `Money.subtract(fee)` checks that both are in the same currency and throws if they're not. The business rules travel with the type.

**EVOLUTION:**
Martin Fowler documented Value Object as a pattern in "Patterns of Enterprise Application Architecture" (2002), but the concept predates that - it was part of SmallTalk's OOP culture and was deeply embedded in Evans's DDD (2003) as one of the three fundamental building blocks (Entities, Value Objects, Services). The pattern was theoretically sound but practically painful in Java, requiring manual implementation of `equals()`, `hashCode()`, and `copy()`. Kotlin's `data class` (2016) made Value Objects practical with one line of code. Java 16's `record` keyword (2021) finally provided a standard Java solution. Today, Value Objects are also the foundation of TypeScript's type-safe patterns, where wrapping primitives in branded types provides compile-time safety at zero runtime cost.

---

### 📘 Textbook Definition

A Value Object, as defined in Domain-Driven Design by Eric Evans, is a domain object that represents a descriptive aspect of the domain with no conceptual identity. Value Objects describe things - the color of a paint, the address on a letter, the amount on a check. Two Value Objects with the same attributes are considered equal and interchangeable. Value Objects are always immutable: once created with a set of attributes, they cannot change. Any "modification" creates a new Value Object with the new values. Value Objects are the building blocks of domain models - they replace primitive types with rich, validated, domain-meaningful types.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A domain concept whose identity IS its value - two £100 notes are interchangeable; a specific customer account is not.

**One analogy:**

> A £50 note. Two £50 notes are completely equal - it doesn't matter which specific physical note you have, only the value matters. You can exchange one for another without any concern. Compare to a passport: two passports are NOT equal just because they have the same name - each is a unique document with a specific identity. The £50 note is a Value Object; the passport is an Entity.

**One insight:**
Value Objects eliminate an entire class of bugs by encoding business rules into types. `Money` can refuse to subtract USD from GBP. `EmailAddress` can validate format on construction. `DateRange` can ensure start is before end. These validations run at the type level, not scattered across services.

---

### 🔩 First Principles Explanation

**VALUE OBJECT vs ENTITY:**

```
┌──────────────────────────────────────────────────────────┐
│           VALUE OBJECT vs ENTITY                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Entity: identity matters                                │
│    Customer #12345 and Customer #67890 are DIFFERENT     │
│    even if they have the same name and email             │
│    Mutable: Customer's email can change                  │
│    Equality: by ID                                       │
│                                                          │
│  Value Object: value matters, not identity               │
│    Money(100, GBP) == Money(100, GBP)  ← equal          │
│    Money(100, GBP) != Money(100, USD)  ← not equal      │
│    Immutable: you don't change a Money, you create new   │
│    Equality: by all attribute values                     │
│                                                          │
│  Test: "Would it matter if I swapped this for another    │
│  instance with the same attributes?"                     │
│    YES → Value Object                                    │
│    NO  → Entity (it has a specific identity)             │
└──────────────────────────────────────────────────────────┘
```

**TYPICAL VALUE OBJECTS:**

```
┌──────────────────────────────────────────────────────────┐
│             COMMON VALUE OBJECT EXAMPLES                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Money         - amount + currency (not just BigDecimal) │
│  EmailAddress  - valid email string (not just String)    │
│  PostalAddress - street, city, zip, country              │
│  DateRange     - start + end, start < end enforced       │
│  PhoneNumber   - validated format + country code         │
│  Percentage    - 0-100 range enforced, not just BigDecim │
│  Coordinates   - lat/long pair, range validated          │
│  Version       - semantic version with comparison logic  │
│  OrderId       - UUID wrapper (typed ID vs plain UUID)   │
│  CustomerId    - UUID wrapper (prevents ID type mix-up)  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE TYPE SAFETY TEST:**

```java
// WITHOUT Value Objects - all UUID references are interchangeable
void transfer(UUID fromAccount,
              UUID toAccount,
              BigDecimal amount,
              String currency) { ... }

// Easy to accidentally swap parameters - compiler can't help you:
transfer(toAccountId, fromAccountId, amount, currency);
// Money flows BACKWARDS. No compiler error.
```

```java
// WITH Value Objects - types prevent invalid combinations
void transfer(AccountId from,
              AccountId to,
              Money amount) { ... }

// Cannot swap from/to - both are AccountId, semantically same
// But Money(amount, currency) prevents currency errors:
Money gbpAmount = Money.of(100, Currency.GBP);
Money usdFee    = Money.of(5,   Currency.USD);
gbpAmount.subtract(usdFee);  // throws CurrencyMismatchEx
// Currency math errors caught at runtime (not in prod data)
```

**THE IMMUTABILITY TEST:**

```java
// Immutable Value Object - operations create new instances:
Money price = Money.of(100, Currency.GBP);
Money discounted = price.multiply(0.9);  // new instance
// price still == Money(100, GBP) - unchanged
// discounted == Money(90, GBP)
```

---

### 🧠 Mental Model / Analogy

> Value Objects are the difference between a photocopy and an original document. A photocopy is defined entirely by what it contains - two identical photocopies are the same thing. You don't care which specific photocopy you have, only that the content is correct. An original document (Entity) has intrinsic identity - "this original contract, signed on this date, with this serial number" - even if two contracts have identical text.

When designing domain types: ask yourself "do I care which specific instance this is?" If yes → Entity. If no, and only the content matters → Value Object.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
A type that represents a concept defined by its values. Two `Money` values with the same amount and currency are identical and interchangeable. No ID needed.

**Level 2 - How to build it (junior):**

1. Make all fields `final`. 2. No setters. 3. Override `equals()` and `hashCode()` to compare by all fields. 4. Validate invariants in the constructor (throw if invalid). 5. Any "modification" method returns a new instance. 6. Consider implementing as Java `record` (Java 16+).

**Level 3 - Design decisions (mid-level):**
Value Objects eliminate Primitive Obsession - the anti-pattern of using primitives (`String`, `int`, `BigDecimal`) for everything. A `CustomerId` (wrapping UUID) and an `OrderId` (also wrapping UUID) cannot be accidentally swapped - even though both are UUIDs at the primitive level, they're different types at the domain level. This prevents a class of bugs that are completely invisible to the compiler with raw primitives.

**Level 4 - Advanced patterns (senior/staff):**
Value Objects can contain business behavior: `DateRange.overlaps(other)`, `Money.convertTo(Currency, ExchangeRate)`, `Percentage.applyTo(Money)`. This behavior is pure - no side effects, no dependencies on external state. Pure behavior is trivially testable and highly composable. In functional programming, Value Objects align with the algebraic data type (ADT) concept. In Event Sourcing, all data within events should be Value Objects - they're serialized, stored, and replayed; mutability would cause state management nightmares. The "stringly-typed" anti-pattern (using String for every domain concept) is eliminated entirely by consistent Value Object usage.

---

### ⚙️ How It Works (Mechanism)

**Java `record` as Value Object (Java 16+):**

```
┌──────────────────────────────────────────────────────────┐
│          VALUE OBJECT IMPLEMENTATION OPTIONS             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Java record (Java 16+):                                 │
│    record Money(BigDecimal amount, Currency currency) {} │
│    → auto-generates equals/hashCode/toString             │
│    → immutable by design (final fields)                  │
│    → compact syntax                                      │
│                                                          │
│  Traditional class:                                      │
│    - final fields                                        │
│    - no setters                                          │
│    - custom equals/hashCode                              │
│    - validation in constructor                           │
│    - creation methods return new instances               │
│                                                          │
│  JPA mapping:                                            │
│    @Embeddable annotation on Value Object                │
│    @Embedded in the Entity that contains it              │
│    Value object columns embedded in entity's table       │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**Value Objects in a rich domain model:**

```
┌──────────────────────────────────────────────────────────┐
│          VALUE OBJECTS IN AGGREGATE CONTEXT              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Order (Entity / Aggregate Root)                         │
│  ├── id: OrderId           ← Value Object (typed UUID)   │
│  ├── customerId: CustomerId ← Value Object (typed UUID)  │
│  ├── items: List<OrderItem>                              │
│  │    └── OrderItem (Entity)                             │
│  │         ├── productId: ProductId  ← Value Object      │
│  │         ├── quantity: Quantity    ← Value Object      │
│  │         └── unitPrice: Money      ← Value Object      │
│  ├── total: Money          ← Value Object                │
│  ├── deliveryAddress: PostalAddress ← Value Object       │
│  └── status: OrderStatus  ← Enum (special Value Object)  │
│                                                          │
│  Primitives used: NONE in domain layer                   │
│  All concepts have domain-meaningful types               │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Money Value Object - full implementation:**

```java
// Value Object using Java record
public record Money(BigDecimal amount, Currency currency) {

    // Validation in compact constructor
    public Money {
        Objects.requireNonNull(amount, "amount required");
        Objects.requireNonNull(currency, "currency required");
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new NegativeMoneyException(amount);
        }
        // Canonical scale: always 2 decimal places
        amount = amount.setScale(2, RoundingMode.HALF_EVEN);
    }

    public static Money of(long amount, Currency currency) {
        return new Money(BigDecimal.valueOf(amount), currency);
    }

    public static Money ZERO(Currency currency) {
        return new Money(BigDecimal.ZERO, currency);
    }

    // Arithmetic creates new instances (immutable)
    public Money add(Money other) {
        requireSameCurrency(other);
        return new Money(
            amount.add(other.amount), currency);
    }

    public Money subtract(Money other) {
        requireSameCurrency(other);
        BigDecimal result = amount.subtract(other.amount);
        if (result.compareTo(BigDecimal.ZERO) < 0) {
            throw new NegativeMoneyException(result);
        }
        return new Money(result, currency);
    }

    public Money multiply(double factor) {
        return new Money(
            amount.multiply(BigDecimal.valueOf(factor))
                  .setScale(2, RoundingMode.HALF_EVEN),
            currency);
    }

    public boolean isGreaterThan(Money other) {
        requireSameCurrency(other);
        return amount.compareTo(other.amount) > 0;
    }

    private void requireSameCurrency(Money other) {
        if (!currency.equals(other.currency)) {
            throw new CurrencyMismatchException(
                currency, other.currency);
        }
    }
    // equals/hashCode/toString provided by record
}

// Typed ID Value Objects - prevents ID type mixing
public record OrderId(UUID value) {
    public static OrderId generate() {
        return new OrderId(UUID.randomUUID());
    }
    public static OrderId of(String value) {
        return new OrderId(UUID.fromString(value));
    }
}

public record CustomerId(UUID value) {
    public static CustomerId of(String value) {
        return new CustomerId(UUID.fromString(value));
    }
}

// Now: transfer(OrderId, CustomerId) cannot be swapped
// - different types, compiler enforces correctness
```

**DateRange Value Object with behavior:**

```java
public record DateRange(LocalDate start, LocalDate end) {

    public DateRange {
        Objects.requireNonNull(start);
        Objects.requireNonNull(end);
        if (end.isBefore(start)) {
            throw new InvalidDateRangeException(start, end);
        }
    }

    public boolean overlaps(DateRange other) {
        return !end.isBefore(other.start) &&
               !start.isAfter(other.end);
    }

    public long daysInRange() {
        return ChronoUnit.DAYS.between(start, end);
    }

    public boolean contains(LocalDate date) {
        return !date.isBefore(start) &&
               !date.isAfter(end);
    }

    public DateRange extendBy(int days) {
        return new DateRange(start, end.plusDays(days));
    }
}
```

---

### ⚖️ Comparison Table

| Aspect      | Value Object             | Entity                  | Primitive (String/int/UUID)    |
| ----------- | ------------------------ | ----------------------- | ------------------------------ |
| Identity    | None - equality by value | Has unique ID           | None                           |
| Mutability  | Immutable                | Mutable (state changes) | Mutable (primitive)            |
| Equality    | All fields equal         | ID equals               | Reference/value equals         |
| Validation  | In constructor           | In operation methods    | None - caller's responsibility |
| Type safety | High - named types       | High                    | Low - string is a string       |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Value Objects are just DTOs                 | DTOs transfer data; Value Objects are domain concepts with behavior and validation - fundamentally different |
| Value Objects can't have behavior           | Value Objects SHOULD have behavior - that's their power (Money.add, DateRange.overlaps)                      |
| Primitive wrappers (OrderId) are overkill   | Typed IDs prevent an entire class of runtime bugs; they have essentially zero performance cost               |
| Value Objects require deep copy to "change" | You don't change a Value Object - you create a new one. This is by design.                                   |

---

### 🚨 Failure Modes & Diagnosis

**Primitive Obsession - missed Value Object opportunities**

**Symptom:** Methods take `String email`, `BigDecimal amount`, `String currency`, `String status`. Email validation scattered across multiple service classes. Currency arithmetic errors.

**Root Cause:** Failing to model domain concepts as Value Objects.

**Diagnostic Check:**

```bash
# Find methods with too many String/BigDecimal/UUID parameters
# These are candidates for Value Object extraction
grep -rn "String\|BigDecimal\|UUID" \
  src/main/java/ --include="*.java" | \
  grep "public.*String.*String.*String" | head -20
```

**Fix:** Extract Value Objects for domain concepts. Start with the concepts that appear most frequently as method parameters or that have validation logic scattered across services.

---

**Mutable Value Object - equality breaks**

**Symptom:** Value object equality fails unexpectedly. Value object stored in a `HashSet` can't be retrieved after modification. Cache invalidation bugs.

**Root Cause:** Value Object has setters or mutable fields, violating the immutability requirement.

**Fix:** Make all fields `final`. Remove setters. Use Java `record` to enforce immutability at the language level.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Replace primitive types with domain-typed wrappers wherever business constraints apply to the primitive. The wrapper is the single place where those constraints are enforced, making invalid states unrepresentable.

**Where else this pattern appears:**
- **Newtypes in Rust/Haskell:** The newtype pattern wraps a primitive in a typed struct to prevent accidental misuse. A `Kilometers(f64)` and `Miles(f64)` are different types despite wrapping the same primitive - the compiler prevents passing Miles where Kilometers is expected. This is Value Object at the type system level.
- **SQL column constraints:** A `CHECK (price >= 0)` constraint wraps the `DECIMAL` type with a business rule. The database enforces the constraint regardless of which application writes to the column - the constraint travels with the data, not with the application code.
- **CSS color values:** A CSS `color` is not a string - it is a value with rules about valid formats (hex, rgb, hsl) and specific equality semantics (\`#FF0000\` and \`rgb(255, 0, 0)\` represent the same color). Value Object applied to styling.

---

### 💡 The Surprising Truth

Value Objects are more frequently the correct modeling choice than Entities, but developers default to Entities because ORMs make entities easier to persist. In a well-modeled domain, Value Objects should significantly outnumber Entities. A `Customer` entity has attributes that are Value Objects: `EmailAddress`, `PhoneNumber`, `PostalAddress`, `Money` (balance), `CustomerTier`. The `Order` entity's attributes are Value Objects: `OrderDate`, `Money` (total), `ShippingAddress`, `OrderStatus`. The entity is the rare thing that needs identity; most domain concepts are defined by their value. When a codebase has 20 entities and 5 value objects, it almost certainly has primitive obsession.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-023 - Domain Model (value objects are the building blocks of domain models; understanding domain models provides the context for why typed domain values matter)
- SAP-043 - SOLID Principles (value object immutability follows from Single Responsibility and Open/Closed principles; understanding SOLID explains why value objects should not have setters)

**Builds On This (learn these next):**
- SAP-030 - Aggregate Root (aggregate roots use value objects as typed attributes for their internal state; value objects appear throughout aggregate design)
- SAP-033 - Entities (the complementary concept; understanding both value objects and entities together defines when identity matters and when it does not)

**Alternatives / Comparisons:**
- SAP-033 - Entities (the contrast; use an entity when identity matters and the object is tracked over time; use a value object when the concept is defined purely by its attributes)
- Primitive types (always-available alternative; correct for truly primitive values with no business constraints; wrong when constraints or operations are needed)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Domain concept defined by its value,      │
│              │ no identity, immutable                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Equality by all attributes, not by ref    │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS       │ Immutable - operations return new instance │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Money, Address, DateRange, ID wrappers    │
├──────────────┼───────────────────────────────────────────┤
│ JAVA TOOL    │ record (Java 16+) is ideal for VO         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A £50 note: its value IS its identity"   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `PostalAddress` Value Object has five fields: `street`, `city`, `postcode`, `county`, `country`. An `Order` has a `deliveryAddress: PostalAddress`. A customer moves and updates their address. Should the `Order`'s delivery address change automatically? What does this tell you about the relationship between the `Customer`'s address (which might change) and the `Order`'s delivery address (which is the address at the time of order placement)?

*Hint:* Research the difference between a "snapshot" value and a "reference" value - specifically: the Order's delivery address is a snapshot of the address AT THE TIME OF ORDER PLACEMENT, not a reference to the Customer's current address. This is exactly why the delivery address should be a Value Object (immutable snapshot) stored on the Order, not a foreign key reference to the Customer's current address. This is also why value objects should be embedded in the owning entity's table (JPA `@Embedded`) rather than normalized into a separate address table with a foreign key.

**Q2.** You have a `Quantity` Value Object that wraps an integer. Two quantities can only be added if they have the same unit (kilograms, litres, pieces). This sounds like a Value Object with type-checking behavior. But what happens when you need to convert between units - `Quantity(2, LITRES).toMillilitres()` should return `Quantity(2000, MILLILITRES)`. Does this conversion method belong on the Value Object, or on a domain service? What is the design principle that guides this decision?

*Hint:* Research Evans's rule for Domain Services versus Value Object methods: behavior belongs on the Value Object if it uses only the object's own data and produces a result of the same or related type. `toMillilitres()` uses only the quantity's own data (value + unit) and returns a related `Quantity` - it belongs on the Value Object. A Domain Service would be needed if the conversion required external data (e.g., a currency exchange rate that must be looked up) or if the operation involved multiple distinct domain concepts.

**Q3.** You are building a financial trading system where a `Price` value object wraps a `BigDecimal`. The system processes millions of prices per second. Java `BigDecimal` uses heap allocation and creates garbage, causing GC pressure at scale. A primitive `long` (storing price as integer cents) would be 10x faster but loses the type safety of `Price`. How do you design `Price` as a Value Object that provides type safety without heap allocation?

*Hint:* Research Java's Project Valhalla "value types" (inline classes) - specifically the motivation that value objects currently require heap allocation in Java but value types will allow stack allocation. Also research the current workaround: using a primitive-backed value object where the `long` is stored as a field but all operations go through the `Price` wrapper, then using the JVM JIT's scalar replacement optimization to eliminate the object allocation in tight loops. This reveals a known limitation of Value Objects in Java that Project Valhalla is designed to fix.
