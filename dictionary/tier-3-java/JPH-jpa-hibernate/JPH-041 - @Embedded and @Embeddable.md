---
id: JPH-041
title: "@Embedded and @Embeddable"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-008, JPH-011, JPH-040
used_by: JPH-042, JPH-051, JPH-054, JPH-056
related: JPH-040, JPH-042, JPH-051
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 41
permalink: /jpa-hibernate/embedded-embeddable/
---

# JPH-041 - @Embedded and @Embeddable

⚡ **TL;DR** - `@Embeddable` marks a value object class
whose fields are stored as columns in the owning entity's
table (no separate table). `@Embedded` on an entity field
references the embeddable. Group cohesive fields (Address:
street, city, zip) into a reusable value object without
creating a separate table or relationship. If an embedded
object is null, all its columns are stored as NULL. Use
`@AttributeOverride` to rename columns when embedding the
same class multiple times.

| #041 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | @Entity, @Id, @Table/@Column, EntityManager, Inheritance Mapping | |
| **Used by:** | @ElementCollection, @Converter, JPA at Scale, Spring Data JPA Architecture | |
| **Related:** | Inheritance Mapping, @ElementCollection, @Converter | |

---

### 🔥 The Problem This Solves

**WITHOUT @Embeddable: FIELD EXPLOSION:**

```java
@Entity
public class Customer {
    @Id Long id;
    String name;
    // Billing address:
    String billingStreet;
    String billingCity;
    String billingZip;
    String billingCountry;
    // Shipping address:
    String shippingStreet;
    String shippingCity;
    String shippingZip;
    String shippingCountry;
    // Contact info:
    String email;
    String phoneCountryCode;
    String phoneNumber;
    // 13 fields; Address logic duplicated across entities
}
// Problem: Address logic (validation, formatting) scattered
// across all entities; no reusability; no cohesion
```

**WITH @Embeddable:**

```java
@Embeddable
public class Address {
    private String street;
    private String city;
    private String zip;
    private String country;
    // Validation, formatting methods here - reusable
}

@Entity
public class Customer {
    @Id Long id;
    String name;
    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name="street",
            column=@Column(name="billing_street")),
        // ...
    })
    private Address billingAddress;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name="street",
            column=@Column(name="shipping_street")),
        // ...
    })
    private Address shippingAddress;
}
// Same single "customers" table; no extra JOIN;
// Address is a reusable, cohesive value object
```

---

### 📘 Textbook Definition

**@Embeddable** marks a class as an embeddable value type.
An embeddable class:
- Has NO `@Id` field (it has no independent identity)
- Is stored as columns in the OWNING entity's table (no separate table)
- Can be reused in multiple entities via `@Embedded`
- Can contain: basic fields, relationships to other entities,
  other embeddables, but NOT `@OneToMany` (use `@ElementCollection`)

**@Embedded** marks an entity field whose type is `@Embeddable`.
Hibernate maps the embeddable's fields to columns in the
enclosing entity's table.

**@AttributeOverride** renames the columns of an embedded class -
required when embedding the same `@Embeddable` type more than
once in the same entity (duplicate column names would occur otherwise).

**Lifecycle:** Embeddable objects share their owning entity's
lifecycle - no separate persist/merge/delete operations needed.
Saving the owning entity saves the embeddable data.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@Embeddable` groups related columns into
a Java value object - the columns stay in the parent
table, but the Java code has structure and reusability.

**One analogy:**
> A database row for a customer has 20 columns: name,
> 4 address columns, 4 phone columns, etc. In Java,
> instead of 20 flat fields on the Customer class, you
> group them: `Address` class, `Phone` class. The database
> table doesn't change - still 20 columns. But Java code
> has `customer.getBillingAddress().getCity()` instead of
> `customer.getBillingCity()`. Pure Java code organization;
> no DB change.

**One insight:** `@Embeddable` is the JPA implementation
of the Domain-Driven Design (DDD) "Value Object" pattern.
A value object is defined by its fields (not by identity),
is immutable, and is embedded in an aggregate root (entity).
DDD practitioners use `@Embeddable` for: Money (amount +
currency), Address, DateRange, PhoneNumber, GeoCoordinate.

---

### 🔩 First Principles Explanation

**SAME TABLE - DIFFERENT JAVA STRUCTURE:**

```
Database table: customers
  id | name | billing_street | billing_city | billing_zip |
     | shipping_street | shipping_city | shipping_zip

Java Entity:
  Customer
    id: Long
    name: String
    billingAddress: Address     <-- @Embedded
      street: String            <-- -> billing_street
      city: String              <-- -> billing_city
      zip: String               <-- -> billing_zip
    shippingAddress: Address    <-- @Embedded
      street: String            <-- -> shipping_street
      city: String              <-- -> shipping_city
      zip: String               <-- -> shipping_zip

No JOIN. Same table. Java grouping only.
```

**NULL EMBEDDABLE:**

```java
customer.setBillingAddress(null);
repo.save(customer);
// SQL: UPDATE customers SET billing_street=NULL,
//        billing_city=NULL, billing_zip=NULL WHERE id=?
// All embedded columns are set to NULL

customer = repo.findById(id).orElseThrow();
customer.getBillingAddress();
// Returns NULL if all embedded columns are NULL
// NOT an empty Address object with null fields
// Check for null before accessing nested fields!
```

---

### 🧪 Thought Experiment

**MONEY VALUE OBJECT - DDD PATTERN:**

```java
// Without @Embeddable: Money spread across columns
public class Product {
    private BigDecimal price;       // column: price
    private String currency;        // column: currency
    // price.multiply(1.2) - caller must pair these manually
    // What if price is set but currency is not? Invalid state
}

// With @Embeddable: Money as a cohesive value object
@Embeddable
public class Money {
    @Column(name = "price_amount",
            precision = 19, scale = 4)
    private BigDecimal amount;

    @Column(name = "price_currency", length = 3)
    @Enumerated(EnumType.STRING)
    private Currency currency;

    // Business logic lives here:
    public Money add(Money other) {
        if (!this.currency.equals(other.currency))
            throw new CurrencyMismatchException();
        return new Money(
            this.amount.add(other.amount),
            this.currency);
    }

    public Money applyTax(BigDecimal taxRate) {
        return new Money(
            this.amount.multiply(BigDecimal.ONE.add(taxRate)),
            this.currency);
    }
}

@Entity
public class Product {
    @Embedded
    private Money price;
    // product.getPrice().add(shipping) - cohesive
    // product.getPrice().applyTax(rate) - reusable
}
```

---

### 🧠 Mental Model / Analogy

> Think of `@Embeddable` like a labeled section in a
> filing cabinet drawer. The drawer is the database table.
> A section label "Billing Address" doesn't create a new
> drawer - it just organizes 4 physical folders already
> in the same drawer. Similarly, `Address` as an embeddable
> doesn't create a new database table; it creates a named
> grouping of 4 columns that already exist in the entity's
> table. The label (Java class) makes the code organized;
> the drawer (table) is unchanged.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@Embeddable` lets you group related fields (like address fields)
into a separate Java class, while still storing them in
the same database table. Better Java code organization
without changing the database structure.

**Level 2 - How to use it (junior developer):**
1. Create a class with `@Embeddable` and the grouped fields
2. Add an `@Embedded` field in your entity pointing to the
   embeddable class
3. Use `@AttributeOverride` when embedding the same class
   twice (to avoid duplicate column names)
4. The embeddable class has no `@Id`

**Level 3 - How it works (mid-level engineer):**
Hibernate reads the `@Embeddable` class's fields and maps
them to columns in the owning entity's table, prefixing
with `@AttributeOverride` names if specified. The embedded
object has no database identity. Loading the entity loads
all embedded columns. Null embeddable = all columns NULL.
Cannot be lazily loaded (it's part of the same row).

**Level 4 - DDD Value Objects (senior engineer):**
`@Embeddable` enables DDD Value Objects - objects defined
by their attributes (not identity), immutable, and self-
validating. Implement embeddables as immutable: `final`
fields, constructor-only initialization, no setters.
Mark as `@Embeddable` immutable with `@Immutable`
(Hibernate annotation). Use for: Money, Address, Period,
GeoPoint, PhoneNumber, EmailAddress. Business logic lives
in the value object, not scattered in service layer.

**Level 5 - Embeddable in Embeddable (staff engineer):**
`@Embeddable` classes can contain other `@Embeddable`
classes (nested embedding). The SQL result is still a
flat set of columns in the root entity's table. For complex
hierarchies, this produces wide rows. Alternative for
very deep nesting: consider separating to a `@OneToOne`
relationship with its own table (normalized, but JOIN cost).
Another edge case: `@Embeddable` inside a `@ElementCollection`
stores the embeddable's columns in the collection table
(not the entity table) - used for `List<Address>` or
`Set<Money>` scenarios (see JPH-042).

---

### ⚙️ How It Works (Mechanism)

**ATTRIBUTE OVERRIDE FOR REUSE:**

```java
@Embeddable
public class Address {
    // Default column names: street, city, zip, country
    private String street;
    private String city;
    private String zip;
    private String country;
}

@Entity
@Table(name = "customers")
public class Customer {
    @Id @GeneratedValue
    private Long id;
    private String name;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street",
            column = @Column(name = "billing_street")),
        @AttributeOverride(name = "city",
            column = @Column(name = "billing_city")),
        @AttributeOverride(name = "zip",
            column = @Column(name = "billing_zip")),
        @AttributeOverride(name = "country",
            column = @Column(name = "billing_country"))
    })
    private Address billingAddress;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street",
            column = @Column(name = "shipping_street")),
        @AttributeOverride(name = "city",
            column = @Column(name = "shipping_city")),
        @AttributeOverride(name = "zip",
            column = @Column(name = "shipping_zip")),
        @AttributeOverride(name = "country",
            column = @Column(name = "shipping_country"))
    })
    private Address shippingAddress;
}
// DDL:
// CREATE TABLE customers (
//   id BIGINT PK, name VARCHAR,
//   billing_street VARCHAR, billing_city VARCHAR,
//   billing_zip VARCHAR, billing_country VARCHAR,
//   shipping_street VARCHAR, shipping_city VARCHAR,
//   shipping_zip VARCHAR, shipping_country VARCHAR
// )
```

---

### 🔄 The Complete Picture - End-to-End Flow

**IMMUTABLE VALUE OBJECT PATTERN:**

```java
@Embeddable
public final class Money {  // final = immutable intent
    @Column(nullable = false,
            precision = 19, scale = 4)
    private final BigDecimal amount;

    @Column(nullable = false, length = 3)
    @Enumerated(EnumType.STRING)
    private final Currency currency;

    // JPA requires no-arg constructor (can be protected)
    protected Money() {
        this.amount = BigDecimal.ZERO;
        this.currency = Currency.USD;
    }

    public Money(BigDecimal amount, Currency currency) {
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException(
                "Amount cannot be negative");
        }
        this.amount = amount;
        this.currency = currency;
    }

    public Money add(Money other) {
        validateSameCurrency(other);
        return new Money(amount.add(other.amount), currency);
    }

    private void validateSameCurrency(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new CurrencyMismatchException(
                this.currency + " vs " + other.currency);
        }
    }
    // Getters only; no setters
}

@Entity
public class Order {
    @Id @GeneratedValue Long id;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name="amount",
            column=@Column(name="subtotal_amount")),
        @AttributeOverride(name="currency",
            column=@Column(name="subtotal_currency"))
    })
    private Money subtotal;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name="amount",
            column=@Column(name="total_amount")),
        @AttributeOverride(name="currency",
            column=@Column(name="total_currency"))
    })
    private Money total;
}
```

---

### 💻 Code Example

**Example 1 - BAD: checking null-safety incorrectly:**

```java
// BAD: assuming non-null embeddable
Customer c = repo.findById(id).orElseThrow();
String city = c.getBillingAddress().getCity();
// NullPointerException if billingAddress is null!
// (all billing columns NULL in DB -> null embeddable)

// GOOD: null check before accessing embeddable
String city = Optional.ofNullable(c.getBillingAddress())
    .map(Address::getCity)
    .orElse("Not provided");
```

**Example 2 - Querying embeddable fields in JPQL:**

```java
// Embeddable fields accessible via dot notation in JPQL:
List<Customer> customers = em.createQuery(
    "FROM Customer c WHERE c.billingAddress.city = :city",
    Customer.class)
    .setParameter("city", "New York")
    .getResultList();
// SQL: SELECT ... FROM customers
//      WHERE billing_city = 'New York'
// JPA knows 'billingAddress.city' -> 'billing_city' column
```

---

### ⚖️ Comparison Table

| Approach | Separate Table? | Identity? | Reusable? | NULL handling | Best for |
|---|---|---|---|---|---|
| `@Embeddable` | No | No (@Id) | Yes (with @AttributeOverride) | All columns NULL | Value objects, grouped fields |
| `@OneToOne` | Yes | Yes | Yes | FK is NULL | Complex owned entities with own lifecycle |
| Flat fields | No | N/A | No | Per-field NULL | Simple, non-reused column groups |
| `@MappedSuperclass` | No | Via subclass | Via inheritance | Per-field | Shared columns across entities |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "@Embeddable creates a separate table" | `@Embeddable` NEVER creates its own table. Its fields are always stored in the owning entity's table as regular columns. For a separate table with its own primary key, use `@Entity` with `@OneToOne`. |
| "I can use @OneToMany inside an @Embeddable" | `@OneToMany` is NOT supported inside `@Embeddable` directly. Use `@ElementCollection` with an `@Embeddable` type as the element for collection-of-value-objects scenarios (see JPH-042). |
| "Embeddable objects need an @Id field" | Embeddables explicitly MUST NOT have `@Id`. They derive identity from the owning entity. Adding `@Id` to an `@Embeddable` class will cause a mapping error. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: NullPointerException on Embeddable Access**

**Symptom:** `NullPointerException: Cannot invoke
"Address.getCity()" because "customer.billingAddress" is null`
after loading an entity from the database.
**Root Cause:** If all columns in the embedded group are NULL
in the database, Hibernate returns `null` for the embeddable
reference (not an empty Address with all null fields).
**Fix:**
1. Use null checks: `Optional.ofNullable(c.getBillingAddress())`
2. Initialize in the entity: `private Address billingAddress = new Address()`
   (empty object with null fields; Hibernate will save nulls
   but return the empty object on load if all cols are null - this
   depends on Hibernate version and config)
3. Add `@NotNull` to the embedded field to enforce non-null
   at the application level

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-006 - @Entity]] - embeddable belongs to an entity
- [[JPH-040 - Inheritance Mapping]] - @MappedSuperclass
  is a similar but different concept

**Builds On This (learn these next):**
- [[JPH-042 - @ElementCollection]] - extends embeddable
  to support collections of value objects

**Related:**
- [[JPH-051 - @Converter]] - attribute converters can
  convert Java types to/from DB types; alternative for
  simple type mappings
- [[JPH-040 - Inheritance Mapping]] - @MappedSuperclass
  for shared columns via inheritance vs @Embedded

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ @Embeddable  │ On the VALUE OBJECT class                 │
│ @Embedded    │ On the ENTITY FIELD (the embeddable)      │
├──────────────┼───────────────────────────────────────────┤
│ TABLE        │ Same table as owning entity; no separate  │
│ NO @Id       │ No identity; no lifecycle management      │
├──────────────┼───────────────────────────────────────────┤
│ REUSE        │ @AttributeOverride for column renaming    │
│              │ Required when embedding same class 2x     │
├──────────────┼───────────────────────────────────────────┤
│ NULL         │ null embeddable -> all columns NULL in DB │
│              │ All NULL in DB -> null embeddable on load  │
├──────────────┼───────────────────────────────────────────┤
│ QUERY        │ JPQL dot-notation: c.billingAddress.city  │
│ COLLECTIONS  │ Use @ElementCollection for List<Address>  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Embeddable = value object stored as     │
│              │ columns in parent entity's table; no JOIN;│
│              │ reuse with @AttributeOverride."           │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `@Embeddable` stores fields in the SAME table as the
   owning entity - no separate table, no JOIN required
2. All embedded columns NULL in DB means the Java
   reference is null - always null-check embeddable fields
3. Embedding the same type twice requires `@AttributeOverride`
   to rename the duplicate column names

**Interview one-liner:** `@Embeddable` maps a value object's
fields as columns in the owning entity's table. No separate
table, no `@Id`, no JOIN. Use for DDD value objects (Address,
Money, Period) to group cohesive fields with business logic.
Embed the same type multiple times with `@AttributeOverride`
to rename columns. Null embeddable = all columns NULL in DB.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Value Objects (DDD)
are a pattern for representing domain concepts that have
no independent identity and are defined entirely by their
attributes. They enforce invariants at construction time
(e.g., `Money` ensures positive amount, valid currency),
are immutable, and are reusable. The pattern generalizes
beyond JPA: in any data model, grouping cohesive fields
into typed value objects improves: (1) validation - invariants
enforced at object creation, (2) reusability - same Address
type across Customer, Supplier, Order, (3) business logic
encapsulation - Money.add() not scattered in services,
(4) readability - `order.getTotal().applyTax(rate)` vs
`new Money(order.getTotalAmount() * rate, order.getCurrency())`.

**Where else this pattern appears:**
- **Kotlin data classes** - natural value objects; JPA
  uses `data class` with protected no-arg constructor
- **Python dataclasses / NamedTuple** - value objects;
  SQLAlchemy uses `@dataclass` + `composite` for embeddables
- **TypeScript types/interfaces** - structural typing;
  embeddable-like patterns in TypeORM using `@Column(() => Address)`
- **Protobuf nested messages** - same concept; nested
  message type embedded in parent message

---

### 💡 The Surprising Truth

JPA's `@Embeddable` objects are required to have a no-argument
constructor (either public or protected), even if you want
the object to be immutable with only constructor-based
initialization. This is a JPA spec requirement for proxy
creation and entity instantiation. The workaround for
immutable embeddables: provide a `protected` no-arg
constructor that initializes to default values (or throws
an exception with a clear message), and use the public
constructor for actual instantiation. Kotlin's `data class`
requires special handling: you must add `@NoArgsConstructor`
(via plugin) or `protected constructor()` explicitly.
This is a leaky abstraction - the JPA requirement for
no-arg constructors bleeds through into value objects
that would naturally have no such constructor.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** an immutable `Money` value object using
   `@Embeddable` with proper no-arg constructor workaround
2. **CONFIGURE** `@AttributeOverride` to embed the same
   `Address` class twice in an entity for billing and shipping
3. **EXPLAIN** the NULL behavior: all columns NULL in DB
   returns null Java reference
4. **WRITE** a JPQL query that filters on an embedded field
5. **DISTINGUISH** between `@Embeddable`, `@MappedSuperclass`,
   and `@OneToOne` and recommend the right approach for given requirements

---

### 🎯 Interview Deep-Dive

**Q1: What is @Embeddable and how does it differ from @Entity?**
*Why they ask:* Tests understanding of value types vs entities.
*Strong answer includes:*
- `@Embeddable`: value type; no `@Id`; no own table; stored
  in owning entity's table; no independent lifecycle
- `@Entity`: has `@Id`; has own table; has independent lifecycle
  (persist, find, merge, remove); can be target of FK relationships
- Use `@Embeddable` for: value objects (Address, Money, Period)
  where identity doesn't matter; concept defined by its attributes
- Use `@Entity` for: objects with identity and independent lifecycle

**Q2: What happens when an @Embeddable field is set to null
on an entity?**
*Why they ask:* Tests operational knowledge.
*Strong answer includes:*
- All columns of the embedded object are set to NULL in the database
- When loaded: if ALL columns are NULL, Hibernate returns null
  for the embeddable reference (not an empty object)
- Safe access pattern: null-check before accessing nested fields
- Prevention: initialize embeddable to empty object in entity;
  or add `@NotNull` at application level to prevent null saves