---
layout: default
title: "Entities"
parent: "Software Architecture Patterns"
nav_order: 746
permalink: /software-architecture/entities/
number: "0746"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Domain Model, Value Objects, Aggregate Root
used_by: DDD, Rich Domain Model, JPA, Repository Pattern
related: Value Objects, Aggregate Root, Domain Model, Identity Map
tags:
  - architecture
  - ddd
  - pattern
  - intermediate
---

# 746 — Entities

⚡ TL;DR — An Entity is a domain object with a unique identity that persists through time and state changes — two entities with the same attributes are still different objects if they have different identities.

---

### 📊 Entry Metadata

| #746            | Category: Software Architecture Patterns                  | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Domain Model, Value Objects, Aggregate Root               |                 |
| **Used by:**    | DDD, Rich Domain Model, JPA, Repository Pattern           |                 |
| **Related:**    | Value Objects, Aggregate Root, Domain Model, Identity Map |                 |

---

### 🔥 The Problem This Solves

**THE IDENTITY PROBLEM:**
A system manages customer accounts. Two customers, "Alice Smith" at "123 Main St," are registered. Are they the same customer? They share identical data. But in the business domain, they could be two different people with the same name and address, or the same person registered twice. Without identity — a unique, persistent ID — there is no way to distinguish or track specific things over time.

**THE ENTITY SOLUTION:**
Assign unique identities. `Customer #12345` and `Customer #67890` are distinct customers forever, regardless of how their names, addresses, or statuses change. The identity is the anchor that ties together all the changes that happen to a thing over its lifetime.

---

### 📘 Textbook Definition

An Entity, as defined in Domain-Driven Design by Eric Evans, is a domain object that is fundamentally defined by its identity — a unique identifier that persists through time and across different representations. An Entity is distinguished from a Value Object by the fact that its identity matters: two Entities are different even if all their attributes are identical. Entities have a lifecycle — they are created, undergo state changes, and may be deleted. The defining characteristic is that the same conceptual "thing" can be tracked across those changes using its identity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A domain object with a persistent unique identity — it's tracked as the same thing even when its attributes change.

**One analogy:**

> A person. Alice Smith (born 1990, lives at 10 Oak Street) gets married: she's now Alice Jones (lives at 20 Pine Avenue). She is still the same person — identified by her passport number, not her name and address. Her identity is fixed; her attributes change. An Entity works the same way: Customer #12345 remains the same customer whether their address, email, or subscription status changes.

**One insight:**
Entities are "things that happen to" over time. Value Objects are "descriptions of" at a point in time. An order (Entity) can be placed, modified, shipped, and delivered — these are things that happen to it. A delivery address (Value Object) is a description — it doesn't change; you replace it with a new description.

---

### 🔩 First Principles Explanation

**ENTITY vs VALUE OBJECT DECISION:**

```
┌──────────────────────────────────────────────────────────┐
│          ENTITY vs VALUE OBJECT DECISION TREE            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Question 1: Does this thing have a lifecycle?           │
│    (is created, changes over time, maybe deleted)        │
│    YES → probably an Entity                              │
│    NO  → probably a Value Object                         │
│                                                          │
│  Question 2: Does identity matter independent of         │
│              attributes?                                 │
│    YES → Entity (two copies with same data ≠ same thing) │
│    NO  → Value Object (two copies with same data = same) │
│                                                          │
│  Question 3: Does it need to be tracked as "the same     │
│              thing" across time and state changes?       │
│    YES → Entity                                          │
│    NO  → Value Object                                    │
│                                                          │
│  Example decisions:                                      │
│    Customer    → Entity (has lifecycle, tracked)         │
│    Order       → Entity (placed, shipped, delivered)     │
│    Money       → Value Object (£100 is £100)             │
│    Address     → Value Object (describes a location)     │
│    OrderItem   → Entity (within aggregate, tracked)      │
│    DiscountPct → Value Object (just a number)            │
└──────────────────────────────────────────────────────────┘
```

**ENTITY CHARACTERISTICS:**

```
┌──────────────────────────────────────────────────────────┐
│              ENTITY CHARACTERISTICS                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Unique ID — assigned at creation, never changes      │
│     UUID, database sequence, domain-specific ID          │
│                                                          │
│  2. Equality by ID — not by attributes                   │
│     entity1.equals(entity2) ↔ entity1.id == entity2.id   │
│                                                          │
│  3. Mutable state — attributes change over lifetime      │
│     Customer's address changes; CustomerID doesn't       │
│                                                          │
│  4. Lifecycle — created, modified, possibly deleted      │
│     Order: OPEN → SUBMITTED → PAID → SHIPPED → DELIVERED │
│                                                          │
│  5. Can be referenced by ID from other aggregates        │
│     Order holds CustomerId (not the Customer object)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE SHIP OF THESEUS TEST:**
A `Subscription` entity is created for Customer #12345. Over 2 years: the price changes, the plan changes, the payment method changes, the renewal date changes. Every attribute is different from the day it was created.

Is it still the same subscription? Yes — because it has the same SubscriptionId. The identity persists through all attribute changes.

**THE DUPLICATE TEST:**
Two `Order` objects with identical data: same customer, same items, same total, same address. Are they the same order? No — they are two separate orders placed at different times. The business treats them as distinct. Therefore, `Order` is an Entity.

Two `Money` objects: `Money(100, GBP)` and `Money(100, GBP)`. Are they the same? Yes, completely interchangeable. Therefore, `Money` is a Value Object.

---

### 🧠 Mental Model / Analogy

> Entities are the nouns that the business keeps track of in ledgers and databases: customers, orders, accounts, products, employees, contracts. Value Objects are the adjectives and measures that describe those nouns: the amount, the status, the address, the date, the percentage. Your business's most important concepts are almost always Entities — because they're what the business cares about tracking over time.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
A thing with a unique ID that you track over time. Even if everything about it changes, it's still the same thing because it has the same ID.

**Level 2 — How to implement it (junior):**
Give each entity a unique ID (UUID or typed wrapper). Implement `equals()` and `hashCode()` based only on the ID. Make the ID immutable (assigned at construction, never changed). Put lifecycle-managing behavior on the entity (status transitions, state changes).

**Level 3 — Entity design (mid-level):**
Entity design choices: Where should the ID come from? Application-generated UUIDs (independent of database, can be created before persistence) vs database sequences (simpler but requires roundtrip to DB). Surrogate keys (UUID, database ID) vs natural keys (email address, account number). Natural keys seem convenient but change in the real world — a customer changes their email; using email as the entity ID is problematic.

**Level 4 — Aggregate scope (senior/staff):**
In DDD, Entities fall into two categories: Aggregate Roots (with their own Repository, referenced by ID from outside) and internal Entities (within the aggregate boundary, accessible only through the root). The key design question for internal entities: does the outside world need to reference this specific entity directly, or is it always accessed through its aggregate root? If outside code needs to reference an `OrderItem` directly, it may need to become an Aggregate Root. If it's always accessed through `Order`, it stays an internal entity.

---

### ⚙️ How It Works (Mechanism)

**Entity ID strategies:**

```
┌──────────────────────────────────────────────────────────┐
│               ENTITY ID STRATEGIES                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  UUID (application-generated):                           │
│    + Created before persistence (can use ID in events)   │
│    + No DB roundtrip to get ID                           │
│    - Non-sequential (random index fragmentation)         │
│    - Long strings in URLs                                │
│                                                          │
│  Database sequence/auto-increment:                       │
│    + Sequential (efficient DB index)                     │
│    + Short IDs                                           │
│    - Must persist to get ID                              │
│    - Sequential IDs reveal business volume (security)    │
│                                                          │
│  Typed ID wrappers (recommended):                        │
│    record OrderId(UUID value) {}                         │
│    record CustomerId(UUID value) {}                      │
│    → Cannot mix up OrderId with CustomerId at compile    │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**Entity lifecycle in a typical DDD system:**

```
┌──────────────────────────────────────────────────────────┐
│              ENTITY LIFECYCLE MANAGEMENT                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Creation:                                               │
│    Order.place(customerId, items)                        │
│    → new OrderId(UUID.randomUUID()) assigned             │
│    → status: OPEN                                        │
│    → persisted via Repository                            │
│                                                          │
│  State transitions:                                      │
│    order.submit() → SUBMITTED                            │
│    order.pay()    → PAID                                 │
│    order.ship()   → SHIPPED                              │
│    order.deliver()→ DELIVERED                            │
│    Each transition: same OrderId, new state              │
│                                                          │
│  Reference from outside:                                 │
│    Shipment entity holds OrderId (not Order object)      │
│    → avoids cross-aggregate object references            │
│                                                          │
│  Deletion (soft delete common for audit trail):          │
│    order.cancel() → CANCELLED (state change, not delete) │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Entity base pattern with typed ID:**

```java
// Typed ID Value Object — prevents mixing up entity IDs
public record CustomerId(UUID value) {
    public static CustomerId generate() {
        return new CustomerId(UUID.randomUUID());
    }
    public static CustomerId of(UUID value) {
        return new CustomerId(value);
    }
}

// Entity — identity by ID, mutable state
public class Customer {
    private final CustomerId id;          // immutable identity
    private EmailAddress email;           // mutable attribute
    private CustomerName name;            // mutable attribute
    private CustomerStatus status;        // lifecycle state
    private PostalAddress address;        // mutable attribute

    // Factory — ensures valid initial state
    public static Customer register(
            CustomerName name, EmailAddress email) {
        return new Customer(
            CustomerId.generate(), name, email,
            CustomerStatus.ACTIVE);
    }

    // Entity operations — state transitions
    public void updateEmail(EmailAddress newEmail) {
        if (status == CustomerStatus.SUSPENDED) {
            throw new SuspendedCustomerException(id);
        }
        this.email = newEmail;
    }

    public void updateAddress(PostalAddress newAddress) {
        // address change doesn't affect other invariants
        this.address = Objects.requireNonNull(newAddress);
    }

    public void suspend(String reason) {
        if (status == CustomerStatus.SUSPENDED) {
            throw new AlreadySuspendedException(id);
        }
        this.status = CustomerStatus.SUSPENDED;
    }

    // ENTITY EQUALITY: by ID only — not attributes
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Customer c)) return false;
        return id.equals(c.id);  // ONLY ID compared
    }

    @Override
    public int hashCode() {
        return id.hashCode();  // ONLY ID hashed
    }

    public CustomerId id() { return id; }
    public EmailAddress email() { return email; }
}
```

---

### ⚖️ Comparison Table

| Aspect             | Entity                | Value Object             | Aggregate Root       |
| ------------------ | --------------------- | ------------------------ | -------------------- |
| Identity           | Unique persistent ID  | None — equality by value | Unique persistent ID |
| Mutability         | Yes — state changes   | No — immutable           | Yes — state changes  |
| Equality           | By ID                 | By all attribute values  | By ID                |
| Repository         | Internal entities: no | No                       | Yes — one per root   |
| External reference | Via ID                | By value (embed or copy) | Via ID               |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                            |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every database row is an Entity           | Some rows represent Value Objects (address table rows, currency rows) — whether it's an Entity depends on domain semantics, not database structure |
| Entities must use database-generated IDs  | Application-generated UUIDs are often better — they allow ID assignment before persistence                                                         |
| Entity equals() should compare all fields | Entity equals() compares ONLY ID — two entities with the same ID and different attributes are the same entity in a different state                 |
| All domain objects with IDs are Entities  | An ID might be used for lookup convenience but the object may still be a Value Object semantically                                                 |

---

### 🚨 Failure Modes & Diagnosis

**Entity equality by all attributes (wrong)**

**Symptom:** Entity `equals()` compares all fields. After updating an entity and putting it back in a Set, it appears as a new entry. Event deduplication breaks because same entity with different state is treated as different.

**Root Cause:** `equals()`/`hashCode()` implemented using all fields instead of ID only.

**Fix:**

```java
// Correct entity equality:
@Override
public boolean equals(Object o) {
    if (!(o instanceof Order order)) return false;
    return id.equals(order.id);  // ID only
}
@Override
public int hashCode() { return id.hashCode(); }
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `Domain Model` — entities are the core building blocks

**Compare With:**

- `Value Objects` — the contrast concept; understanding both is essential

**Builds On This:**

- `Aggregate Root` — entities are organized into aggregates with one root
- `Repository Pattern` — loads and saves entities (specifically aggregate roots)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Domain object with persistent unique ID  │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Equality by ID, not by attributes         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Tracked over time; identity matters       │
├──────────────┼───────────────────────────────────────────┤
│ vs VO        │ VO: equality by value; Entity: by ID      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Same passport number = same person,      │
│              │  regardless of address or name"           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `Product` entity in an e-commerce system has a name, description, price, and SKU. An admin changes the price. Is it still the same product? Of course. But an analyst wants to know: "What was the price of this product 6 months ago?" The product's current state doesn't hold that history. How do you handle entity state history without losing the entity's current state, and what patterns exist for this problem?

**Q2.** A `UserSession` object exists for the duration of a user's login session. It has a session ID, a user ID, expiry time, and device information. Is `UserSession` an Entity or a Value Object? Defend your answer using the criteria above, and describe what consequences your decision has for how you implement `equals()` and `hashCode()`.
