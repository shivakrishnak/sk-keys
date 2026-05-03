---
layout: default
title: "Primitive Obsession"
parent: "Code Quality"
nav_order: 1117
permalink: /code-quality/primitive-obsession/
number: "1117"
category: Code Quality
difficulty: ★★★
depends_on: Code Smell, Data Clumps, Refactoring
used_by: Refactoring, Technical Debt, Code Review
related: Data Clumps, Code Smell, Feature Envy
tags:
  - antipattern
  - advanced
  - bestpractice
---

# 1117 — Primitive Obsession

⚡ TL;DR — Primitive obsession is a code smell where domain concepts are represented as primitive types (String, int, double) instead of dedicated value objects, causing validation to scatter and type safety to disappear.

| #1117 | Category: Code Quality | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Code Smell, Data Clumps, Refactoring | |
| **Used by:** | Refactoring, Technical Debt, Code Review | |
| **Related:** | Data Clumps, Code Smell, Feature Envy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An order system takes `int customerId` as a parameter. Later, a developer accidentally passes a `productId` where a `customerId` was expected (`int` and `int` are interchangeable at the type level). The compiler says nothing. The tests say nothing. In production, product IDs are used as customer IDs in 0.1% of orders — silent data corruption.

**THE BREAKING POINT:**
When domain concepts are represented as primitives, the type system provides no protection. Every piece of code that accepts an `int customerId` would equally accept an `int productId` — they're the same type. The developer must remember the distinction; the compiler forgets it.

**THE INVENTION MOMENT:**
This is exactly why **Primitive Obsession** is named: using primitives where domain types should exist is a failure to model the domain — and introducing dedicated types (even thin wrappers) restores the type safety and behaviour location that primitives cannot provide.

---

### 📘 Textbook Definition

**Primitive Obsession** is a code smell (Fowler, "Refactoring") describing the use of primitive data types (int, String, double, boolean) to represent domain concepts that warrant their own types. Common manifestations: **ID types** (`long customerId`, `long orderId` — both `long`, but different domains), **monetary values** (`double price` — floating-point precision bugs, no currency), **status codes** (`String status = "ACTIVE"` — no type safety, case-sensitive bugs), **validation-scattered types** (`String email` — validated differently in 10 places), **boolean flags** (`boolean isPaid, boolean isActive, boolean isDeleted, boolean isFraudulent` — a state machine hidden in four booleans). Refactoring: **Replace Primitive with Object** (introduce a class or record for the concept), **Replace Type Code with State/Strategy** (booleans/strings representing state → State pattern), **Replace Type Code with Subclasses** (int/string type codes → polymorphism). Java 21's sealed classes and record patterns enable expressive domain types with minimal boilerplate.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Using `String` for an email address when `EmailAddress` would prevent invalid emails at construction time.

**One analogy:**
> Primitive Obsession is like labelling boxes only with numbers instead of names. Box 1 = kitchen items, Box 2 = books, Box 3 = clothes. You can put anything in any box — the number doesn't restrict what goes in. If you accidentally put cooking utensils in Box 3 (the "clothes" box), you won't know until you unpack. Named boxes (custom types) enforce what can go inside. You can't put kitchen items in the `ClothesBox` because it only accepts `Clothing` objects.

**One insight:**
Primitive Obsession is a domain modelling failure. Every time you use `String email` instead of `EmailAddress`, you're choosing not to model a concept that your domain clearly has. The domain has email addresses; your type system doesn't — and this gap is filled by scattered validation code.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Distinct domain concepts should be represented by distinct types — even when the underlying representation is the same primitive.
2. Validation of a concept belongs in the type representing the concept — not scattered across all usages.
3. Type aliases (even thin wrappers) prevent a class of bugs that the compiler catches at zero cost and the developer never has to think about.

**DERIVED DESIGN:**
Since distinct domain concepts (`CustomerId`, `OrderId`) can share an underlying primitive representation (`long`) but must not be interchangeable, they require distinct types. A type that wraps a `long` and is named `CustomerId` cannot be passed where `OrderId` is expected — the compiler enforces the boundary. The validation for `EmailAddress` (RFC 5322 format) belongs in `EmailAddress`'s constructor — not in every service method that receives an email.

**THE TRADE-OFFS:**
Gain: Type safety (wrong ID types caught at compile time); validation centralised in type constructor; behaviour co-located with type; self-documenting APIs.
Cost: More classes; slight verbosity at call sites (`new CustomerId(42)` vs. `42`); serialisation/deserialisation may need configuration; legacy code may use primitives pervasively (migration cost).

---

### 🧪 Thought Experiment

**SETUP:**
`processPayment(long customerId, long orderId, double amount)` — all three parameters are primitives.

**BUG SCENARIO:**
Developer calls: `processPayment(orderId, customerId, amount)` — swaps the first two arguments.

**Without custom types:** Compiles. Tests (mock-based) pass. In production: order 12345 is charged to customer 67890's account. Data corruption.

**With `CustomerId(long)` and `OrderId(long)`:**
`processPayment(CustomerId customerId, OrderId orderId, Money amount)`
Calling `processPayment(orderId, customerId, amount)` → **compile error**: `OrderId` cannot be passed where `CustomerId` expected. Bug caught before running, at zero runtime cost.

**THE INSIGHT:**
The bug was logical but structurally impossible when domain types were used. The type system becomes a documentation system AND a bug prevention system.

---

### 🧠 Mental Model / Analogy

> Primitive Obsession is like writing a recipe that says "add 2 units of flour and 2 units of butter." Units prevent you from knowing if it's cups or tablespoons. If the unit is wrong, the recipe fails — but you don't know why until you taste it. Named types (`Cup`, `Tablespoon`) make "2 cups of flour and 2 tablespoons of butter" explicit. You can't accidentally add 2 tablespoons of flour where 2 cups were needed — the unit (type) carries the meaning.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** When you use plain numbers or text for specific concepts (customer IDs, email addresses, money amounts), you lose the ability for the computer to catch mixing them up. Introduce a specific type for each concept. `EmailAddress` can validate itself; `double` cannot.

**Level 2:** Key replacement patterns: `long customerId` → `record CustomerId(long value) {}` (simple wrapper, compile-time type safety). `String email` → `record EmailAddress(String value) { EmailAddress { if (!isValid(value)) throw... } }` (validates at construction). `double price` → `record Money(BigDecimal amount, Currency currency) {}` (precision + currency). `String status` → `enum OrderStatus { PENDING, PAID, SHIPPED, CANCELLED }` (exhaustive, type-safe).

**Level 3:** Java 16+ records provide value-class semantics with minimal boilerplate. A `record CustomerId(long value)` generates constructor, equals/hashCode, toString automatically. For IDs, sealed classes or type aliases prevent primitive interchangeability. For enums-as-strings: `"ACTIVE"` strings become `Status.ACTIVE` enums — refactoring support, exhaustive switch. For money: introducing `Money(amount, currency)` as a value object centralises: currency-safe arithmetic (`add`, `subtract`), formatting (`format(Locale)`), and validation (non-negative amounts).

**Level 4:** Primitive Obsession is a failure of the **Whole Value** pattern (Ward Cunningham): every domain value should be a first-class type. Languages differ in how well they support this: Java requires explicit class/record definitions; Kotlin adds inline classes (zero-overhead wrappers); Haskell's newtype is the canonical form. The deeper principle: **types are specifications**. A method that accepts `String email` specifies very little — any string is accepted. A method that accepts `EmailAddress email` specifies: this is a validated email address in RFC 5322 format. The method documents what it needs and the compiler enforces it. This moves validation upstream (to type construction time) and downstream concerns (email formatting, domain extraction) into a single, testable location.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────┐
│  PRIMITIVE OBSESSION → DOMAIN TYPE                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  BEFORE:                                           │
│  String email → any string accepted                │
│  Validation: if (!email.contains("@")) throw...    │
│  Occurs in: UserService.create(),                  │
│   NotificationService.send(),                      │
│   ReportService.email(),                           │
│   AuthService.register()                           │
│  Bug: one place forgets validation                 │
│                                                    │
│  AFTER:                                            │
│  record EmailAddress(String value) {               │
│    EmailAddress {  // compact constructor           │
│      if (!value.contains("@"))                     │
│          throw new InvalidEmailException(value);   │
│    }                                               │
│  }                                                 │
│  Validation: happens once, in EmailAddress         │
│  Invalid emails cannot exist as EmailAddress       │
│  All 4 methods receive EmailAddress —              │
│    guaranteed valid by type invariant              │
└────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer: createOrder(CustomerId, OrderId, Money)
  → Accidentally passes orderId as customerId
  → IDE: type error [← YOU ARE HERE: caught immediately]
  → Developer fixes parameter order
  → Bug: prevented at zero runtime cost
```

**FAILURE PATH:**
```
processPayment(long customerId, long orderId, double amount)
  → processPayment(orderId, customerId, 99.99)
  → Compiles, tests pass
  → Production: customer 5678 charged to account 1234
  → Silent data corruption for 48 hours
  → Root cause: primitives provide no type boundary
```

---

### 💻 Code Example

```java
// SMELL: Primitive obsession
void createOrder(long customerId, long productId, 
                 double price, String currency) {}

// REPLACED:
record CustomerId(long value) {}
record ProductId(long value) {}
record Money(BigDecimal amount, Currency currency) {
    Money {
        if (amount.compareTo(BigDecimal.ZERO) < 0)
            throw new IllegalArgumentException("Negative");
    }
}

void createOrder(CustomerId customerId, ProductId productId,
                 Money price) {}
// createOrder(productId, customerId, price) → compile error!

// String status → enum
// SMELL:
String status = "ACTIVE";
if (status.equals("active")) { ... } // case-sensitive bug

// REPLACED:
enum UserStatus { ACTIVE, INACTIVE, SUSPENDED, DELETED }
UserStatus status = UserStatus.ACTIVE;
// switch(status) { case ACTIVE -> ... } // exhaustive, type-safe
```

---

### ⚖️ Comparison Table

| Concept | Problem | Solution | Language Feature |
|---|---|---|---|
| ID confusion | `long userId == long orderId` type | `record UserId(long v)` | Java records |
| Invalid state | `String email` accepts garbage | `EmailAddress` validates | Constructor validation |
| Magic strings | `"ACTIVE"` vs `"active"` bugs | `enum Status { ACTIVE }` | Enums |
| **Primitive money** | `double price` precision loss | `Money(BigDecimal, Currency)` | Value object |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Wrapping primitives is over-engineering | A one-line `record CustomerId(long value)` prevents entire classes of bugs. The cost is minimal; the type safety is permanent. |
| Enums solve all type codes | String status fields should be enums; single-field value types (IDs, money) should be records/classes; complex state should be State pattern objects. Enums solve one category. |

---

### 🚨 Failure Modes & Diagnosis

**1. Record Wrapper Not Used Consistently**

**Symptom:** `CustomerId` class exists but some code still passes `long customerId` directly.

**Root Cause:** Inconsistent adoption; API boundary (REST deserialisation) injects raw primitives that bypass the type.

**Fix:** Ensure `@JsonCreator` / Jackson deserialisation creates `CustomerId` objects from JSON, not raw longs. Enforce consistently in code review: no `long` accepted where `CustomerId` is the domain type.

---

### 🔗 Related Keywords

**Prerequisites:** `Code Smell`, `Data Clumps` (related smell — multiple primitives for one concept)
**Builds On This:** `Refactoring`, `Value Objects`
**Alternatives / Comparisons:** `Data Clumps` — multiple primitives forming a group; Primitive Obsession — single primitive for a concept

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Using primitives (int, String) where      │
│              │ domain-specific types should exist        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Type system provides no protection: wrong │
│ SOLVES       │ ID types, invalid emails, precision loss  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ A named type is both documentation and    │
│              │ a compiler-enforced domain boundary       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Domain concept appears as a primitive in  │
│              │ 5+ method signatures                      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Truly generic utilities (sorting, parsing)│
│              │ that work on any string/int               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Type safety + validation locality vs.     │
│              │ more classes, serialisation plumbing      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Numbered boxes: no protection from       │
│              │  putting kitchen items in 'clothes'."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Clumps → Value Objects → Extract     │
│              │ Class                                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A REST API returns `{ "userId": 12345, "orderId": 67890 }` as JSON numbers. The Java backend receives them via Jackson and maps them to `long userId` and `long orderId`. Introduce `UserId` and `OrderId` records. How do you configure Jackson to deserialise `12345` into `UserId(12345)` transparently, and how do you configure the serialiser to emit `12345` (not `{"value": 12345}`)? What are the trade-offs of different approaches?

**Q2.** Kotlin's `value class` and Java's `record` are both used for Primitive Obsession refactoring, but they differ. Kotlin's `inline class` (JVM backend) compiles to the underlying primitive when possible, eliminating runtime boxing overhead. Java's `record` always boxes. For a high-frequency financial trading system processing 1 million orders/second, where order IDs are checked, compared, and hashed in every transaction: would you use records for `OrderId` type safety, or would the boxing overhead make this impractical? What evidence would you need to decide?

