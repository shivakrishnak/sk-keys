---
id: SAP-017
title: Entities
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-065, SAP-069
used_by: SAP-067
related: SAP-067, SAP-069
tags:
  - architecture
  - ddd
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /software-architecture/entities/
---

# SAP-043 - Entities

⚡ TL;DR - An Entity is a domain object with a unique identity that persists through time and state changes - two entities with the same attributes are still different objects if they have different identities.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | SAP-065, SAP-069 |
| **Used by**    | SAP-067          |
| **Related**    | SAP-067, SAP-069 |

---

### 🔥 The Problem This Solves

**THE IDENTITY PROBLEM:**
A system manages customer accounts. Two customers, "Alice Smith" at "123 Main St," are registered. Are they the same customer? They share identical data. But in the business domain, they could be two different people with the same name and address, or the same person registered twice. Without identity - a unique, persistent ID - there is no way to distinguish or track specific things over time.

**THE ENTITY SOLUTION:**
Assign unique identities. `Customer #12345` and `Customer #67890` are distinct customers forever, regardless of how their names, addresses, or statuses change. The identity is the anchor that ties together all the changes that happen to a thing over its lifetime.

**EVOLUTION:**
Eric Evans gave the Entity pattern its DDD-specific definition in "Domain-Driven Design" (2003): an object defined by its identity, not its attributes. The concept predates DDD - object databases (ObjectStore, Versant, 1990s) tracked object identity explicitly. JPA/Hibernate (2001+) operationalised the concept with the `@Id` annotation and identity map pattern - the persistence framework ensures that loading the same entity twice returns the same object instance. The key evolution was distinguishing Entities from Value Objects precisely: JPA entities always have an `@Id`, while Value Objects have no persistent identity. Kotlin and Java records made Value Objects practical, sharpening the entity/value object distinction in modern codebases.

---

### 📘 Textbook Definition

An Entity, as defined in Domain-Driven Design by Eric Evans, is a domain object that is fundamentally defined by its identity - a unique identifier that persists through time and across different representations. An Entity is distinguished from a Value Object by the fact that its identity matters: two Entities are different even if all their attributes are identical. Entities have a lifecycle - they are created, undergo state changes, and may be deleted. The defining characteristic is that the same conceptual "thing" can be tracked across those changes using its identity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A domain object with a persistent unique identity - it's tracked as the same thing even when its attributes change.

**One analogy:**

> A person. Alice Smith (born 1990, lives at 10 Oak Street) gets married: she's now Alice Jones (lives at 20 Pine Avenue). She is still the same person - identified by her passport number, not her name and address. Her identity is fixed; her attributes change. An Entity works the same way: Customer #12345 remains the same customer whether their address, email, or subscription status changes.

**One insight:**
Entities are "things that happen to" over time. Value Objects are "descriptions of" at a point in time. An order (Entity) can be placed, modified, shipped, and delivered - these are things that happen to it. A delivery address (Value Object) is a description - it doesn't change; you replace it with a new description.

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
│  1. Unique ID - assigned at creation, never changes      │
│     UUID, database sequence, domain-specific ID          │
│                                                          │
│  2. Equality by ID - not by attributes                   │
│     entity1.equals(entity2) ↔ entity1.id == entity2.id   │
│                                                          │
│  3. Mutable state - attributes change over lifetime      │
│     Customer's address changes; CustomerID doesn't       │
│                                                          │
│  4. Lifecycle - created, modified, possibly deleted      │
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

Is it still the same subscription? Yes - because it has the same SubscriptionId. The identity persists through all attribute changes.

**THE DUPLICATE TEST:**
Two `Order` objects with identical data: same customer, same items, same total, same address. Are they the same order? No - they are two separate orders placed at different times. The business treats them as distinct. Therefore, `Order` is an Entity.

Two `Money` objects: `Money(100, GBP)` and `Money(100, GBP)`. Are they the same? Yes, completely interchangeable. Therefore, `Money` is a Value Object.

---

### 🧠 Mental Model / Analogy

> Entities are the nouns that the business keeps track of in ledgers and databases: customers, orders, accounts, products, employees, contracts. Value Objects are the adjectives and measures that describe those nouns: the amount, the status, the address, the date, the percentage. Your business's most important concepts are almost always Entities - because they're what the business cares about tracking over time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
A thing with a unique ID that you track over time. Even if everything about it changes, it's still the same thing because it has the same ID.

**Level 2 - How to implement it (junior):**
Give each entity a unique ID (UUID or typed wrapper). Implement `equals()` and `hashCode()` based only on the ID. Make the ID immutable (assigned at construction, never changed). Put lifecycle-managing behavior on the entity (status transitions, state changes).

**Level 3 - Entity design (mid-level):**
Entity design choices: Where should the ID come from? Application-generated UUIDs (independent of database, can be created before persistence) vs database sequences (simpler but requires roundtrip to DB). Surrogate keys (UUID, database ID) vs natural keys (email address, account number). Natural keys seem convenient but change in the real world - a customer changes their email; using email as the entity ID is problematic.

**Level 4 - Aggregate scope (senior/staff):**
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
// Typed ID Value Object - prevents mixing up entity IDs
public record CustomerId(UUID value) {
    public static CustomerId generate() {
        return new CustomerId(UUID.randomUUID());
    }
    public static CustomerId of(UUID value) {
        return new CustomerId(value);
    }
}

// Entity - identity by ID, mutable state
public class Customer {
    private final CustomerId id;          // immutable identity
    private EmailAddress email;           // mutable attribute
    private CustomerName name;            // mutable attribute
    private CustomerStatus status;        // lifecycle state
    private PostalAddress address;        // mutable attribute

    // Factory - ensures valid initial state
    public static Customer register(
            CustomerName name, EmailAddress email) {
        return new Customer(
            CustomerId.generate(), name, email,
            CustomerStatus.ACTIVE);
    }

    // Entity operations - state transitions
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

    // ENTITY EQUALITY: by ID only - not attributes
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
| Identity           | Unique persistent ID  | None - equality by value | Unique persistent ID |
| Mutability         | Yes - state changes   | No - immutable           | Yes - state changes  |
| Equality           | By ID                 | By all attribute values  | By ID                |
| Repository         | Internal entities: no | No                       | Yes - one per root   |
| External reference | Via ID                | By value (embed or copy) | Via ID               |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                            |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every database row is an Entity           | Some rows represent Value Objects (address table rows, currency rows) - whether it's an Entity depends on domain semantics, not database structure |
| Entities must use database-generated IDs  | Application-generated UUIDs are often better - they allow ID assignment before persistence                                                         |
| Entity equals() should compare all fields | Entity equals() compares ONLY ID - two entities with the same ID and different attributes are the same entity in a different state                 |
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

### � Transferable Wisdom

**Reusable Engineering Principle:** When a thing must be tracked and distinguished from other things with identical attributes, assign it a stable, persistent identity that survives all attribute changes. The identity is the anchor for all historical records about that thing.

**Where else this pattern appears:**

- **National identity documents:** A passport number is an entity identity. Two people named "John Smith" born on the same day are different entities because they have different passport numbers. The passport number survives name changes, address changes, and nationality changes.
- **Git commits:** A commit SHA is an entity identity. Two commits with identical content are still different commits (different SHA) because they occur at different points in time and have different parents. The SHA is the immutable identity.
- **Social Security / National Insurance numbers:** Government-assigned persistent identities that survive name changes, address changes, and marital status changes. The number is the entity identity; the attributes are mutable but the identity is permanent.

---

### 💡 The Surprising Truth

The hardest entity design question is not "what is the identity?" but "at what point is something a DIFFERENT entity rather than the SAME entity that changed?" If a ship has every plank replaced over time, is it the same ship? (Ship of Theseus.) In software: if a company undergoes a merger and the resulting company has a new name, new headquarters, new officers, and new shareholders - is it the same `Company` entity or a new one? The answer determines whether you UPDATE the existing entity (same identity) or CREATE a new entity and ARCHIVE the old one. There is no universal rule - the business domain determines what counts as "same thing" versus "different thing," and getting this wrong causes data corruption that is expensive to diagnose years later.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-065 - Domain Model (entities are the core building blocks of domain models; understanding the domain model provides the context for why tracked, mutable domain objects with identity are the primary unit of design)
- SAP-069 - Value Objects (the complementary concept; understanding both entities and value objects together is how you decide whether a domain concept needs identity or can be defined by its value)

**Builds On This (learn these next):**

- SAP-067 - Aggregate Root (entities are organized into aggregates with one root entity; the aggregate root is the entity that other entities access only through)

**Alternatives / Comparisons:**

- SAP-069 - Value Objects (use when the concept is defined by its attributes and equality by value is correct; use an Entity when identity persists across attribute changes)

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

*Hint:* Research the "Temporal Pattern" and specifically Martin Fowler's "Temporal Patterns" article - which documents BiTemporal modeling (transaction time vs. valid time), Snapshot pattern (store entity state snapshots with timestamps), and the Event Sourcing approach (derive current state by replaying historical events). Also research the Hibernate Envers library which adds automatic audit table generation for entity history.

**Q2.** A `UserSession` object exists for the duration of a user's login session. It has a session ID, a user ID, expiry time, and device information. Is `UserSession` an Entity or a Value Object? Defend your answer using the criteria above, and describe what consequences your decision has for how you implement `equals()` and `hashCode()`.

*Hint:* Research the Entity criterion: does identity persist through attribute changes? A session's expiry time can be extended (refresh token) - the session is still the same session with the same session ID. Two sessions with identical user ID and device but different session IDs are DIFFERENT sessions (different concurrent logins). This means `UserSession` IS an entity: it has a stable identity (session ID), it changes over time (expiry refresh), and two otherwise identical sessions are distinct if their IDs differ. Therefore `equals()` and `hashCode()` should use only the session ID.

**Q3.** Your system models a `BankAccount` entity with an `accountNumber` (String) as the identity. A regulatory change requires that account numbers be re-issued in a new format (they now have a 2-letter country prefix). Existing accounts must migrate from old format to new format over 18 months. During migration, the SAME bank account has TWO different account numbers. How do you handle this entity identity crisis without breaking transaction history, customer records, or cross-system references?

*Hint:* Research the "Surrogate Key" pattern - specifically the concept of using an internal, system-generated UUID as the true entity identity, while the externally-visible account number is just an attribute that can change. The surrogate key (`accountId: UUID`) is the entity's true identity; the `accountNumber` is a human-readable alias that changes during migration. All internal references use the UUID; account number is only for display and customer-facing APIs. This is the standard database design pattern for exactly this problem.
