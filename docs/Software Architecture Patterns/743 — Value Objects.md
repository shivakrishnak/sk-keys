---
layout: default
title: "Value Objects"
parent: "Software Architecture Patterns"
nav_order: 743
permalink: /software-architecture/value-objects/
number: "743"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Domain Model, Object-Oriented Programming"
used_by: "DDD, Aggregate Root, Domain Events, Data Mapper Pattern"
tags: #intermediate, #architecture, #ddd, #immutability, #domain
---

# 743 — Value Objects

`#intermediate` `#architecture` `#ddd` `#immutability` `#domain`

⚡ TL;DR — **Value Objects** are immutable objects whose identity is determined entirely by their attributes — not by reference or ID — making them safe to share, copy freely, and use to express domain concepts like Money, Email, and Address with built-in validation and behavior.

| #743            | Category: Software Architecture Patterns                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Domain Model, Object-Oriented Programming               |                 |
| **Used by:**    | DDD, Aggregate Root, Domain Events, Data Mapper Pattern |                 |

---

### 📘 Textbook Definition

**Value Objects** (Eric Evans, "Domain-Driven Design") are objects that describe characteristics or measure things, where equality is based on all attributes rather than identity. Key properties: (1) **No identity**: two `Money(100, USD)` objects are equal regardless of whether they're the same object in memory — unlike entities where `orderId == 1` is a distinct order from `orderId == 2`. (2) **Immutability**: value objects do not change after creation. Operations return new objects: `money.add(tax)` returns a new `Money`, not modifying the original. (3) **Self-validating**: a `Money` value object validates: amount is non-negative, currency is recognized. An `Email` validates format. Invalid state: impossible to construct. (4) **Side-effect-free functions**: all operations on value objects return new values; they never mutate external state. (5) **Replace by value**: freely shareable and copyable without side effects. Contrast with **Entities**: entities have identity (`Order #1001` is different from `Order #1002`); their equality is by ID; they change over time (mutable state transitions).

---

### 🟢 Simple Definition (Easy)

A $20 bill vs. a serial number. The $20 bill: it IS $20 (the value defines it). It doesn't matter WHICH $20 bill you hold — all $20 bills are equal. You can exchange one for another freely. If you burn one and print a new one, nothing changes in your wallet's value. An Order ID (entity): it matters WHICH order — Order #1001 and Order #1002 are different orders even if they have the same amount. Value Objects: equality by value. Entities: equality by identity.

---

### 🔵 Simple Definition (Elaborated)

Primitive obsession: `String email`, `BigDecimal price`, `String currency`. Problems: email might be "not an email." Price might be negative. Adding USD and EUR amounts accidentally. Value Objects solve this: `Email email = Email.of("user@example.com")` — validates on creation, throws if invalid. `Money price = Money.of(new BigDecimal("29.99"), USD)` — validates non-negative, carries its currency. `price.add(tax)` — type-safe, returns new Money. `price.compareTo(budget)` — same-currency comparison enforced. `email.domain()` — domain behavior on the type. Value Objects replace primitives with types that validate themselves and carry their own behavior.

---

### 🔩 First Principles Explanation

**Primitive Obsession problem → Value Objects solution:**

```
PRIMITIVE OBSESSION (the problem):

  Method signature:
    boolean bookFlight(String customerId, String flightId,
                       String departureDate, String returnDate,
                       BigDecimal price, String currency,
                       int seats, String seatClass) { ... }

  Problems:
    - String departureDate: could be "2024-13-45" (invalid), "tomorrow", or empty.
    - BigDecimal price: could be negative.
    - String currency: could be "XYZ" (non-existent currency).
    - bookFlight(customerId, flightId, ...): args in wrong order? Compiler won't catch.
    - No validation until somewhere deep in business logic.
    - Rules about dates, prices, currencies: scattered across service methods.

VALUE OBJECTS (the solution):

  boolean bookFlight(CustomerId customerId, FlightId flightId,
                     FlightDate departureDate, FlightDate returnDate,
                     Money price, SeatCount seats, SeatClass seatClass) { ... }

  // CustomerId: validates UUID format on creation.
  // FlightDate: validates date is in the future. Cannot be "tomorrow".
  // Money: validates positive, knows its currency. Can't add USD + EUR.
  // SeatClass: enum — only ECONOMY, BUSINESS, FIRST allowed.
  // All invalid states: impossible to CONSTRUCT. Validation at system boundary.

IMPLEMENTING A VALUE OBJECT (Java):

  public final class Money {
      private final BigDecimal amount;
      private final Currency currency;

      // Private constructor:
      private Money(BigDecimal amount, Currency currency) {
          // Validation in constructor — can't create invalid Money:
          if (amount == null) throw new IllegalArgumentException("Amount cannot be null");
          if (amount.compareTo(BigDecimal.ZERO) < 0)
              throw new IllegalArgumentException("Amount cannot be negative: " + amount);
          if (currency == null) throw new IllegalArgumentException("Currency cannot be null");

          this.amount = amount.setScale(2, RoundingMode.HALF_UP); // Normalize
          this.currency = currency;
      }

      // Factory method (preferred over public constructor):
      public static Money of(BigDecimal amount, Currency currency) {
          return new Money(amount, currency);
      }

      public static Money of(String amount, String currencyCode) {
          return new Money(new BigDecimal(amount), Currency.getInstance(currencyCode));
      }

      public static Money zero(Currency currency) {
          return new Money(BigDecimal.ZERO, currency);
      }

      // IMMUTABLE operations — return NEW Money, never mutate:
      public Money add(Money other) {
          if (!this.currency.equals(other.currency))
              throw new CurrencyMismatchException(this.currency, other.currency);
          return new Money(this.amount.add(other.amount), this.currency);
      }

      public Money subtract(Money other) {
          if (!this.currency.equals(other.currency))
              throw new CurrencyMismatchException(this.currency, other.currency);
          BigDecimal result = this.amount.subtract(other.amount);
          if (result.compareTo(BigDecimal.ZERO) < 0)
              throw new InsufficientFundsException(this, other);
          return new Money(result, this.currency);
      }

      public Money multiply(int factor) {
          if (factor < 0) throw new IllegalArgumentException("Factor cannot be negative");
          return new Money(this.amount.multiply(BigDecimal.valueOf(factor)), this.currency);
      }

      public Money applyDiscount(Percentage discount) {
          BigDecimal discountAmount = this.amount.multiply(discount.asFraction());
          return new Money(this.amount.subtract(discountAmount), this.currency);
      }

      public boolean isGreaterThan(Money other) {
          requireSameCurrency(other);
          return this.amount.compareTo(other.amount) > 0;
      }

      // EQUALITY BY VALUE (not by reference):
      @Override
      public boolean equals(Object obj) {
          if (this == obj) return true;
          if (!(obj instanceof Money other)) return false;
          return this.amount.equals(other.amount) && this.currency.equals(other.currency);
      }

      @Override
      public int hashCode() {
          return Objects.hash(amount, currency);
      }

      @Override
      public String toString() {
          return currency.getSymbol() + amount.toPlainString();
      }

      // Accessors (no setters — immutable):
      public BigDecimal amount() { return amount; }
      public Currency currency() { return currency; }
  }

  // Usage — type safety and built-in behavior:
  Money price = Money.of("29.99", "USD");
  Money tax = Money.of("2.40", "USD");
  Money total = price.add(tax);                    // Returns new Money: $32.39
  Money discounted = total.applyDiscount(Percentage.of(10)); // $29.15

  // Type system prevents mistakes:
  Money euros = Money.of("29.99", "EUR");
  price.add(euros);  // Throws CurrencyMismatchException — caught at runtime (or use compiler)

VALUE OBJECTS IN JAVA RECORDS:

  Java 16+ records: excellent for value objects:

  public record Email(String value) {
      public Email {  // Compact constructor — runs validation:
          if (value == null || value.isBlank()) throw new IllegalArgumentException("Email empty");
          if (!EMAIL_PATTERN.matcher(value).matches())
              throw new InvalidEmailException(value);
          value = value.toLowerCase().trim();  // Normalize
      }

      public String domain() { return value.substring(value.indexOf('@') + 1); }
      public String localPart() { return value.substring(0, value.indexOf('@')); }
  }

  // Records: immutable by default, equals/hashCode by value, toString built-in.
  Email a = new Email("User@Example.COM");
  Email b = new Email("user@example.com");
  a.equals(b);  // TRUE — equality by value (both normalized to user@example.com)

ENTITY vs VALUE OBJECT — how to decide:

  Question: "Do two instances with the same attributes represent the same 'thing'?"

  Address:
    Alice's billing address: "123 Main St, NYC, 10001"
    Bob's billing address:   "123 Main St, NYC, 10001"
    Same address? → Yes, if they're at the same physical location.
    → Value Object (equality by attributes).

  BUT: if you need to track each address's history separately (Bob moved; Alice didn't):
    Bob's address ID #5 vs Alice's address ID #5.
    → Entity (needs identity to distinguish histories).

  The domain decides, not the attributes alone.

  Typical Value Objects: Money, Email, PhoneNumber, Address (when no history needed),
  GPS coordinates, DateRange, URL, IP address, Weight, Temperature.

  Typical Entities: Order, Customer, Product, Account, Invoice, Employee.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Value Objects (Primitive Obsession):

- `String email` validated in controller, service, AND repository — three copies of the same rule
- `BigDecimal price` can accidentally become negative — no type-level protection
- Adding `BigDecimal usdPrice + BigDecimal eurPrice` — silent bug, no currency check

WITH Value Objects:
→ Validation at construction: can never have an invalid `Email` or negative `Money`
→ Domain behavior on the type: `email.domain()`, `money.add(other)`, `dateRange.overlaps(other)`
→ Type safety: compiler prevents passing `CustomerId` where `ProductId` expected

---

### 🧠 Mental Model / Analogy

> Physical quantities vs. objects with names. "3 kilometers" and "3 kilometers" are always equal — it doesn't matter which ruler measured them. But "John Smith (SSN 123-45-6789)" and "John Smith (SSN 234-56-7890)" are different people, even though the names are the same. Value Objects: like "3 kilometers" — equality by attributes, freely interchangeable. Entities: like people — identity matters, not just attributes. A Money value object is "3 kilometers"; an Order entity is "John Smith."

"3 kilometers = 3 kilometers (any ruler)" = value object equality by value
"SSN distinguishes two John Smiths" = entity identity
"Can freely exchange any ruler measuring 3km" = freely copy/share value objects
"Immutable: 3km is always 3km" = value objects don't mutate

---

### ⚙️ How It Works (Mechanism)

```
VALUE OBJECT USAGE:

  // Primitive obsession version:
  String email = "user@example.com";   // Any string. No validation.
  void sendEmail(String to, String body) { /* hope "to" is valid */ }

  // Value Object version:
  Email email = Email.of("user@example.com");  // Validates on creation.
  void sendEmail(Email to, EmailBody body) {    // Type-safe. Compiler enforces.
      // "to" is ALWAYS a valid email. No null check. No format check.
  }

IMMUTABILITY GUARANTEE:

  Money balance = Money.of("100.00", "USD");
  Money fee = Money.of("1.50", "USD");

  Money newBalance = balance.subtract(fee);  // Returns NEW Money.
  // balance: still $100.00 (unchanged)
  // newBalance: $98.50 (new object)
  // Thread-safe: immutable objects can be shared across threads.
```

---

### 🔄 How It Connects (Mini-Map)

```
Primitive types (String, int, BigDecimal — no domain meaning)
        │
        ▼ (wrap with domain meaning and validation)
Value Objects ◄──── (you are here)
(immutable, equality by value, self-validating, domain behavior)
        │
        ├── Domain Model: value objects are building blocks of rich domain models
        ├── Aggregate Root: aggregates use value objects for their fields
        ├── Data Mapper: maps value objects to/from multiple DB columns
        └── Domain Events: value objects in event payloads (Money, Email, Address)
```

---

### 💻 Code Example

```java
// Value object with builder for complex construction:
public final class PhysicalAddress {
    private final String streetLine1;
    private final String streetLine2; // nullable
    private final String city;
    private final String stateOrProvince;
    private final PostalCode postalCode;
    private final CountryCode country;

    private PhysicalAddress(String streetLine1, String streetLine2, String city,
                            String stateOrProvince, PostalCode postalCode, CountryCode country) {
        this.streetLine1 = Objects.requireNonNull(streetLine1, "streetLine1");
        this.streetLine2 = streetLine2; // nullable OK
        this.city = Objects.requireNonNull(city, "city");
        this.stateOrProvince = Objects.requireNonNull(stateOrProvince, "stateOrProvince");
        this.postalCode = Objects.requireNonNull(postalCode, "postalCode");
        this.country = Objects.requireNonNull(country, "country");
    }

    // Domain behavior:
    public boolean isInternational(CountryCode homeCountry) {
        return !this.country.equals(homeCountry);
    }

    public String formatted() {
        StringBuilder sb = new StringBuilder(streetLine1);
        if (streetLine2 != null) sb.append(", ").append(streetLine2);
        sb.append(", ").append(city).append(", ").append(stateOrProvince);
        sb.append(" ").append(postalCode.value()).append(", ").append(country.name());
        return sb.toString();
    }

    // Equality by all attributes:
    @Override
    public boolean equals(Object o) {
        if (!(o instanceof PhysicalAddress a)) return false;
        return Objects.equals(streetLine1, a.streetLine1)
            && Objects.equals(streetLine2, a.streetLine2)
            && Objects.equals(city, a.city)
            && Objects.equals(stateOrProvince, a.stateOrProvince)
            && Objects.equals(postalCode, a.postalCode)
            && Objects.equals(country, a.country);
    }

    @Override
    public int hashCode() {
        return Objects.hash(streetLine1, streetLine2, city, stateOrProvince, postalCode, country);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Value Objects are just DTOs                       | No. DTOs are dumb data bags for transferring data between layers. Value Objects are domain concepts with validation, domain behavior (methods), and equality semantics. A DTO `MoneyDto` has fields and getters. A Value Object `Money` validates on construction, provides `add()`, `subtract()`, `applyDiscount()`, enforces same-currency operations, and defines equality by value                          |
| Immutability makes Value Objects expensive to use | Modern JVMs are highly optimized for short-lived objects. Value objects are typically small and short-lived. The JVM's escape analysis often avoids heap allocation entirely for value objects that don't escape a method. Java 21+ Project Valhalla: primitive classes designed specifically for value semantics. The clarity and safety of immutable value objects far outweigh any minor allocation overhead |
| An Address needs an ID, so it should be an Entity | Only if your domain requires tracking specific address instances over time (e.g., "this particular address record was updated"). If you only care about what the address IS (the data values), not which database row represents it, it's a Value Object. Many real-world systems use Address as both: a value object for calculation/comparison, but stored with an ID for database reference                  |

---

### 🔥 Pitfalls in Production

**Mutable value object breaks equality contract:**

```java
// BAD: Mutable Value Object — equality breaks, sharing unsafe:
class DateRange {
    private LocalDate start;
    private LocalDate end;

    // Setter allows mutation AFTER creation:
    public void setStart(LocalDate start) { this.start = start; }
    public void setEnd(LocalDate end) { this.end = end; }

    // Equality check: but the object can change after being put in a Set or HashMap!
    @Override public boolean equals(Object o) { ... }
    @Override public int hashCode() { return Objects.hash(start, end); }
}

DateRange range = new DateRange(LocalDate.of(2024, 1, 1), LocalDate.of(2024, 12, 31));
Set<DateRange> set = new HashSet<>();
set.add(range);                // hashCode: based on start=Jan1, end=Dec31

range.setStart(LocalDate.of(2024, 6, 1));  // MUTATED after insertion!
set.contains(range);  // FALSE — hashCode changed, but object is in the bucket for old hash.
// Object lost in the Set. Silent data corruption.

// FIX: Make all fields final. No setters. Return new object for modifications:
public final class DateRange {
    private final LocalDate start;
    private final LocalDate end;

    public DateRange(LocalDate start, LocalDate end) {
        if (end.isBefore(start)) throw new IllegalArgumentException("end before start");
        this.start = start; this.end = end;
    }

    public DateRange extendBy(int days) {  // Returns new DateRange
        return new DateRange(this.start, this.end.plusDays(days));
    }

    public boolean overlaps(DateRange other) {
        return !this.end.isBefore(other.start) && !other.end.isBefore(this.start);
    }
}
```

---

### 🔗 Related Keywords

- `Domain Model` — value objects are first-class building blocks of rich domain models
- `Entities` — the counterpart: equality by identity, mutable state, have IDs
- `Aggregate Root` — aggregates use value objects for all their non-identity attributes
- `Primitive Obsession` — the anti-pattern that value objects solve
- `Immutability` — the key property enabling value objects to be safely shared

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Immutable objects with equality by value. │
│              │ Validate at construction. Carry domain   │
│              │ behavior. Replace raw primitives.        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Domain concepts with no identity: Money,  │
│              │ Email, Address, DateRange, GPS coord;     │
│              │ where two instances with same values = same│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Concept needs identity tracking over time │
│              │ (use Entity instead); concept needs to    │
│              │ mutate (use Entity); domain doesn't need  │
│              │ the abstraction (YAGNI)                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "$20 is $20 regardless of which bill:     │
│              │  equality by value, freely copyable,      │
│              │  and it knows its own denomination."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain Model → Aggregate Root →           │
│              │ Entities → Primitive Obsession → DDD      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `Quantity` value object represents product quantities: `Quantity(int value)` validates `value >= 0`. You model a cart item as having a `Quantity`. A user tries to add -5 units via the API. With primitive `int qty`: the API controller might catch it, or it might not, and the invalid value could propagate to the database. With `Quantity`: where does validation happen, and what's the benefit when validation must also happen in an event-driven system where the same `Quantity` is deserialized from a Kafka message? Trace the exact flow in both cases.

**Q2.** You model `Money` as a value object. Order totals are `Money`. A `Money` subtraction method throws `InsufficientFundsException` if result would be negative. Your domain expert says: "Orders can have credit balances (negative totals) in special cases — returns and refunds." Do you: (A) change `Money.subtract()` to allow negative results, (B) create a separate `SignedMoney` value object that allows negatives, or (C) remove the negativity validation from Money and validate at the aggregate level? What does this design decision tell you about the domain model?
