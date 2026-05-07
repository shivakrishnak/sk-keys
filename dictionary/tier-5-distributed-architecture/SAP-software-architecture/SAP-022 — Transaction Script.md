---
layout: default
title: "Transaction Script"
parent: "Software Architecture Patterns"
nav_order: 22
permalink: /software-architecture/transaction-script/
number: "SAP-022"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Service Layer, Database Transactions, Stored Procedures
used_by: Simple CRUD APIs, ETL processes, Scripts, Legacy systems
related: Service Layer, Domain Model, Active Record, Anemic Domain Model
tags:
  - architecture
  - pattern
  - intermediate
  - database
---

# SAP-022 — Transaction Script

⚡ TL;DR — A Transaction Script is a pattern where each business transaction is implemented as a single procedure that directly manipulates the database — simple, linear, easy for CRUD but unscalable for complex domains.

---

### 📊 Entry Metadata

| #740            | Category: Software Architecture Patterns                        | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Service Layer, Database Transactions, Stored Procedures         |                 |
| **Used by:**    | Simple CRUD APIs, ETL processes, Scripts, Legacy systems        |                 |
| **Related:**    | Service Layer, Domain Model, Active Record, Anemic Domain Model |                 |

---

### 🔥 The Problem This Solves

**WHEN IT'S THE RIGHT TOOL:**
Not every application has complex business logic. An application that manages a catalog of products, processes orders with standard rules, or runs nightly data imports doesn't need a rich domain model with aggregates and domain events. For these scenarios, the Transaction Script provides the simplest working solution — a procedure per business operation, no more.

**THE CORE INSIGHT:**
Simplicity is a virtue. Transaction Script embraces the fact that for many applications, the "business logic" IS the database operations — create this row, update that field, query these records. Making it complicated with domain models would be over-engineering.

---

### 📘 Textbook Definition

Transaction Script, defined by Martin Fowler in "Patterns of Enterprise Application Architecture," is a pattern that organizes business logic as a series of transactions where each transaction is a script (procedure or method) that contains all the logic for one business operation. The script fetches data from the database, processes it, and stores results back to the database, all within a single transaction. There is no separate domain model — the data manipulation IS the business logic.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One method per business operation; each method does all the database work for that operation.

**One analogy:**

> A recipe card. You want to make pasta? There's one recipe card for pasta. It tells you everything — get the ingredients, boil water, cook pasta, drain, serve. It's completely self-contained and sequential. There's no abstract "food preparation framework" — it's a direct procedure. Transaction Script is the recipe card approach to business operations.

**One insight:**
Transaction Script is not inherently bad — it is appropriately simple for simple problems. The question is: at what complexity point does Transaction Script become harder to maintain than a domain model? The answer is usually "when the same business rule appears in multiple scripts."

---

### 🔩 First Principles Explanation

**THE PATTERN:**

```
┌──────────────────────────────────────────────────────────┐
│              TRANSACTION SCRIPT STRUCTURE                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  One method = one business transaction:                  │
│                                                          │
│  registerCustomer(name, email, password):                │
│    1. Validate email format (input check)                │
│    2. Check email uniqueness (DB query)                  │
│    3. Hash password (computation)                        │
│    4. INSERT INTO customers (name, email, hash)          │
│    5. INSERT INTO welcome_emails_queue (customerId)      │
│    6. COMMIT                                             │
│    7. Return new customer ID                             │
│                                                          │
│  That's it. No domain model. No aggregates. No events.  │
│  Just a procedure that does what it needs to do.         │
└──────────────────────────────────────────────────────────┘
```

**WHEN IT SCALES POORLY:**

```
┌──────────────────────────────────────────────────────────┐
│        WHERE TRANSACTION SCRIPT BREAKS DOWN              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Script 1: placeOrder()                                  │
│    → checks product availability (SQL)                   │
│    → checks customer credit limit (SQL + calc)           │
│    → creates order (SQL)                                 │
│                                                          │
│  Script 2: addItemToExistingOrder()                      │
│    → checks product availability (SQL) ← DUPLICATE      │
│    → checks order is not shipped (SQL)                   │
│    → checks total won't exceed credit (SQL + calc)       │
│       ← SLIGHTLY DIFFERENT credit check!                 │
│                                                          │
│  Script 3: processReorder()                              │
│    → checks availability (SQL) ← TRIPLICATE             │
│    → different credit check again ← BUG SOURCE          │
│                                                          │
│  Duplicate logic + slight variations = bugs              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE TIPPING POINT:**
A Transaction Script works well for a blog: `createPost()`, `editPost()`, `deletePost()`, `publishPost()` — each is a simple SQL operation with no meaningful rules between them.

The Transaction Script breaks for a bank: `transfer()` needs to know the same "can this account be debited?" rule that `withdraw()`, `processPayment()`, `processRefund()`, and `applyFee()` all also need. Each script duplicates or slightly varies this rule. When the rule changes (new overdraft policy), how many scripts do you update?

**THE INSIGHT:**
Transaction Script is a good default for CRUD. Upgrade to Domain Model when you notice the same business rule appearing in multiple scripts.

---

### 🧠 Mental Model / Analogy

> Transaction Script is like a cooking recipe book where each recipe is completely self-contained. It doesn't reference abstract "cooking techniques" — it says "heat oil in a pan" every time, even if 10 recipes say the same thing. This is fine for a small recipe book. For a professional kitchen with 500 recipes, you want shared technique references ("basic roux," "standard bechamel") so changes propagate everywhere. The domain model is that professional kitchen handbook.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
One method per business operation that does all the database work from start to finish. Simple and direct.

**Level 2 — How to use it (junior):**
Create a service class with one method per business operation. Each method opens a transaction, does the SQL work, and commits. Use prepared statements. Keep methods focused on one operation. Extract helper functions for repeated SQL patterns.

**Level 3 — Trade-offs (mid-level):**
Transaction Script is proportionate for simple domains. The cost is duplication of business rules across scripts as the domain grows. The refactoring path is: identify the most frequently duplicated logic → extract to domain model classes → gradually move logic out of scripts into the model.

**Level 4 — Design decision (senior/staff):**
In a microservices architecture, individual services often start as Transaction Scripts (simple enough to justify it). As a service evolves and its domain logic grows, it graduates to a domain model approach within that service. Transaction Script is not an all-or-nothing choice for the whole system — different services can use different patterns based on their domain complexity. CQRS read models are often implemented as Transaction Scripts (optimized SQL queries) even in systems where the write side uses a rich domain model.

---

### ⚙️ How It Works (Mechanism)

**Transaction Script as SQL-first procedure:**

```
┌──────────────────────────────────────────────────────────┐
│            TRANSACTION SCRIPT — EXECUTION FLOW          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  BEGIN TRANSACTION                                       │
│     │                                                    │
│     ├─ Input validation (not DB — pure computation)      │
│     ├─ Query 1: fetch required data from DB              │
│     ├─ Business check: if condition → throw error        │
│     ├─ Query 2: fetch more data if needed                │
│     ├─ Computation: calculate derived values             │
│     ├─ Write 1: INSERT / UPDATE / DELETE                 │
│     ├─ Write 2: INSERT into related table                │
│     └─ Return result                                     │
│  COMMIT                                                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**Common variations of Transaction Script:**

```
┌──────────────────────────────────────────────────────────┐
│           TRANSACTION SCRIPT VARIATIONS                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Direct SQL (raw JDBC, raw queries):                  │
│     Method contains SQL strings directly                 │
│     Simplest possible implementation                     │
│                                                          │
│  2. Service + Repository (most common in Java):          │
│     Service method = transaction script                  │
│     Repository handles SQL abstraction                   │
│     This is "Transaction Script with Repository"         │
│                                                          │
│  3. Stored Procedures:                                   │
│     Script lives in the database as a procedure          │
│     Application calls: CALL process_payment(?)          │
│     Strong coupling to database; hard to test            │
│                                                          │
│  4. ETL/Batch scripts:                                   │
│     processNightlyBatch() reads rows, transforms, writes │
│     Canonical Transaction Script use case                │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Transaction Script — simple registration:**

```java
@Service
@RequiredArgsConstructor
public class CustomerRegistrationScript {

    private final JdbcTemplate jdbc;
    private final PasswordEncoder encoder;

    @Transactional
    public UUID registerCustomer(String name,
                                  String email,
                                  String password) {
        // Input validation
        if (!email.contains("@")) {
            throw new InvalidEmailException(email);
        }
        if (password.length() < 8) {
            throw new WeakPasswordException();
        }

        // Business check via SQL
        boolean exists = jdbc.queryForObject(
            "SELECT COUNT(*) > 0 FROM customers " +
            "WHERE email = ?",
            Boolean.class, email);
        if (exists) {
            throw new EmailAlreadyExistsException(email);
        }

        // Write operation
        UUID id = UUID.randomUUID();
        jdbc.update(
            "INSERT INTO customers(id, name, email, " +
            "password_hash, created_at) " +
            "VALUES (?, ?, ?, ?, ?)",
            id, name, email,
            encoder.encode(password),
            Instant.now());

        // Side effect
        jdbc.update(
            "INSERT INTO email_queue(type, recipient, " +
            "created_at) VALUES (?, ?, ?)",
            "WELCOME", email, Instant.now());

        return id;
    }
}
```

**When to upgrade to domain model — spotting duplication:**

```java
// placeOrder() — credit check rule
if (customer.creditBalance < order.total) { ... }

// addItemToOrder() — SAME credit check, slightly different
if (customer.creditBalance < order.total + item.price) { ... }

// processReorder() — credit check again, DIFFERENT threshold
if (customer.creditBalance - 100 < order.total) { ... }

// SIGNAL: extract "canAfford(amount)" method to Customer
// This is the domain model emerging naturally from the scripts
```

---

### ⚖️ Comparison Table

| Pattern                      | Logic Location        | Object Model     | Complexity            | Best For                  |
| ---------------------------- | --------------------- | ---------------- | --------------------- | ------------------------- |
| **Transaction Script**       | In procedures         | None (or anemic) | Low                   | Simple CRUD, ETL, scripts |
| Service Layer + Domain Model | Domain objects        | Rich             | High                  | Complex domains           |
| Active Record                | In entity + procedure | Partial          | Medium                | Simple ORM CRUD           |
| Stored Procedures            | In database           | None             | Low (app) / High (DB) | Database-driven logic     |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                            |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Transaction Script is always wrong               | It's appropriate for simple domains — wrong for complex ones                                                       |
| You must choose one pattern for the whole system | Different services or modules can use different patterns                                                           |
| Transaction Script = bad architecture            | Transaction Script is a legitimate pattern; using it when domain complexity warrants a richer model is the mistake |
| Moving to domain model requires full rewrite     | Scripts can be incrementally refactored by extracting shared logic into domain objects                             |

---

### 🚨 Failure Modes & Diagnosis

**Logic Divergence — same rule, different scripts**

**Symptom:** A business rule exists in 5 different service methods with slightly different implementations. Bugs are fixed in some but not all.

**Root Cause:** Transaction Script approach applied to a complex domain where shared rules are needed.

**Diagnostic Check:**

```bash
# Find duplicate patterns across service classes
# Look for repeated SQL patterns or repeated conditionals
grep -rn "credit_limit\|insufficient_funds\|overdraft" \
  src/main/java/ --include="*.java"
# Multiple occurrences = logic that belongs in a domain object
```

**Fix:** Extract the shared logic into a domain object method. All scripts call the method.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Service Layer` — the typical packaging structure for Transaction Scripts

**Builds On This:**

- `Domain Model` — the pattern to graduate to as domain complexity grows
- `Repository Pattern` — commonly used with Transaction Script to abstract SQL

**Alternatives:**

- `Domain Model` — richer, appropriate for complex business rules
- `Active Record` — middle ground: objects manage their own SQL

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One method = one transaction with all SQL │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Simplest solution for simple problems     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple CRUD, ETL, no shared business rules│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Business rules appear in 3+ scripts       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplicity vs rule duplication at scale   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The recipe card approach — complete,     │
│              │  self-contained, one operation"           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a Transaction Script system that has grown to 25 service methods, and you've noticed the same "eligibility check" logic appearing in 7 of them with minor variations. You want to refactor toward a domain model but can't stop development for a big rewrite. What is the smallest, safest first step that moves toward a richer model without breaking existing functionality?

**Q2.** The read side of a CQRS system uses complex optimized SQL queries — JOINs, aggregations, denormalized projections. Would you classify this as a Transaction Script? Does it matter? What does this reveal about Transaction Script as a pattern for read-heavy operations?
