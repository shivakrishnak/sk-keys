---
version: 1
layout: default
title: "Consistency (DB)"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /databases/consistency-db/
id: DBF-018
category: Database Fundamentals
difficulty: ★☆☆
depends_on: ACID, Transaction, Constraints
used_by: Foreign Key, Normalization, ORM Patterns
related: Atomicity, Isolation, CAP Theorem
tags:
  - database
  - transactions
  - reliability
  - foundational
---

# DBF-018 - Consistency (DB)

⚡ TL;DR - Consistency in ACID means every transaction moves the database from one valid state to another, never leaving it with violated constraints or broken rules.

| #413            | Category: Database Fundamentals          | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | ACID, Transaction, Constraints           |                 |
| **Used by:**    | Foreign Key, Normalization, ORM Patterns |                 |
| **Related:**    | Atomicity, Isolation, CAP Theorem        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An order system allows inserting an `OrderItem` row with a `product_id` that references a product that was deleted five minutes ago. Now the order line item points to nothing - a dangling reference. Reports break, shipping logic crashes, customer service can't look up what the customer ordered. The database has become a collection of inconsistent lies masquerading as data.

**THE BREAKING POINT:**
At scale, applications make mistakes. Code has bugs. Data is imported from external systems. If the database doesn't enforce its own rules, "garbage in" doesn't just stay at the entry point - it propagates through every downstream query, report, and API. Cleaning up inconsistent data is orders of magnitude harder than preventing it.

**THE INVENTION MOMENT:**
"This is exactly why database Consistency was created."

---

### 📘 Textbook Definition

**Consistency** (in the ACID sense) is the guarantee that a transaction can only bring the database from one valid state to another valid state, as defined by all declared integrity constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK). Any transaction that would violate a constraint is rejected - the database refuses the commit and rolls back the transaction. Note: ACID Consistency is distinct from CAP Theorem Consistency. In CAP, "consistency" means all nodes see the same data simultaneously; in ACID, it means constraint rules are always enforced.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Consistency means the database never accepts data that breaks its own rules.

**One analogy:**

> A spreadsheet with data validation rules - if you try to enter a date in a "Phone Number" column, the spreadsheet rejects it. The spreadsheet's rules are always enforced. You can't sneak invalid data past the validation. Database Consistency is that same enforcement, but for referential integrity, uniqueness, and domain rules, applied to every write.

**One insight:**
ACID Consistency is the only ACID property that isn't implemented purely by the database engine - it's a shared responsibility. The database enforces structural rules (constraints), but application-level rules (e.g., "account balance must never go negative") must be explicitly expressed as CHECK constraints or enforced in application code plus the atomicity/isolation guarantees.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The database has a set of declared integrity rules (schema constraints).
2. Every committed state of the database must satisfy all integrity rules.
3. Any transaction that would leave the database in a state violating those rules must be rejected.

**DERIVED DESIGN:**
Consistency is the simplest of the four ACID properties to implement - the database engine checks declared constraints at commit time (or at write time for immediate constraints). If any constraint fails, the transaction is aborted.

Three categories of constraints enforce Consistency:

- **Entity integrity**: PRIMARY KEY (unique, non-null row identifier)
- **Referential integrity**: FOREIGN KEY (child row's reference must match an existing parent row)
- **Domain integrity**: UNIQUE, NOT NULL, CHECK (column-level value rules)

The subtlety: Consistency is defined by what you declare. A database with no constraints can accept any data and is "consistent" by definition - consistently unconstrained. The value of Consistency scales with how precisely you model your integrity rules in the schema.

**THE TRADE-OFFS:**
**Gain:** The database becomes a self-validating system - invalid data is rejected at the boundary, not discovered days later in a failed report.
**Cost:** Strict foreign key enforcement adds overhead on every INSERT/UPDATE/DELETE (the engine must verify referenced rows exist). Some applications disable foreign keys for bulk imports, then re-enable - risking inconsistency if they skip validation.

---

### 🧪 Thought Experiment

**SETUP:**
A `users` table and an `orders` table. `orders.user_id` has a FOREIGN KEY referencing `users.id`. A bug in the user deletion service deletes a user without first deleting their orders.

**WHAT HAPPENS WITHOUT CONSISTENCY (no FK constraint):**

- User 42 is deleted from `users`.
- 15 orders with `user_id = 42` remain in `orders`.
- Dashboard query: `SELECT o.* FROM orders o JOIN users u ON o.user_id = u.id` - returns 0 rows for deleted user's orders (silently wrong).
- Accounting report: processes only JOINed orders, misses 15 orphaned orders. Revenue figures are wrong. Nobody knows why.

**WHAT HAPPENS WITH CONSISTENCY (FK constraint active):**

- `DELETE FROM users WHERE id = 42` is attempted.
- Database detects 15 orders referencing user 42.
- DELETE is rejected: `ERROR: update or delete on table "users" violates foreign key constraint`.
- The bug in the deletion service is caught immediately, not 3 months later in an audit.

**THE INSIGHT:**
Consistency turns silent data corruption into loud, immediate errors. A constraint violation that crashes a deployment is infinitely preferable to orphaned data silently corrupting reports for months.

---

### 🧠 Mental Model / Analogy

> Consistency is like building code enforcement for a city. Before any construction is approved, inspectors verify it meets all codes: electrical, structural, fire safety. If a building would violate code, the permit is denied before construction starts - not after the building collapses. The database's schema constraints are the building codes.

- "Building permit application" → database transaction attempting a write
- "Building codes" → schema constraints (PK, FK, UNIQUE, CHECK)
- "Inspector" → database constraint enforcement at commit time
- "Denied permit" → `ROLLBACK` with constraint violation error
- "Approved construction" → committed transaction leaving valid state

Where this analogy breaks down: database constraint checking is automatic and instant; building inspections take days. Also, unlike building codes, database constraints can be temporarily deferred within a transaction.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Consistency means the database only accepts data that follows its rules. If you try to add a row that breaks a rule - like referencing a record that doesn't exist - the database refuses it.

**Level 2 - How to use it (junior developer):**
Define PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, and CHECK constraints in your `CREATE TABLE` statements. The database enforces them automatically. When a violation occurs, the INSERT/UPDATE/DELETE throws an exception (`ConstraintViolationException` in JPA, `SQLException` in JDBC) - catch it and handle it.

**Level 3 - How it works (mid-level engineer):**
Constraints can be IMMEDIATE (checked on each statement) or DEFERRED (checked at commit time). PostgreSQL supports `SET CONSTRAINTS DEFERRED` within a transaction - useful for temporarily-invalid intermediate states, like inserting two rows that reference each other. CHECK constraints are evaluated per-row; FOREIGN KEY constraints require an index lookup on the referenced table. Cascading actions (`ON DELETE CASCADE`, `ON UPDATE CASCADE`) extend consistency maintenance automatically.

**Level 4 - Why it was designed this way (senior/staff):**
ACID Consistency is the only property that's partly delegated to the application. The database engine enforces declared constraints, but it can't enforce undeclared business rules. The classic example: an account balance can never go negative - this requires either a CHECK constraint (`CHECK (balance >= 0)`) or application-level enforcement inside a transaction. Teams that don't use CHECK constraints for business invariants end up with "application-layer consistency" - enforced inconsistently, bypassed by direct SQL queries, and violated during migrations. The strongest databases use as many constraints as possible to make the database a true source of truth, not just a data dump.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ CONSISTENCY ENFORCEMENT                      │
├──────────────────────────────────────────────┤
│                                              │
│  INSERT INTO orders (user_id, total)         │
│    VALUES (999, 100.00)                      │
│                                              │
│  Constraint checks (immediate):              │
│    ├── NOT NULL: user_id not null ✅          │
│    ├── NOT NULL: total not null ✅            │
│    ├── FK: SELECT 1 FROM users               │
│    │       WHERE id = 999                    │
│    │       → no row found ❌                  │
│    └── REJECT: constraint violation          │
│         → ROLLBACK transaction               │
│                                              │
│  Constraint types:                           │
│  ┌────────────────┬────────────────────────┐ │
│  │ PRIMARY KEY    │ unique + not null       │ │
│  │ FOREIGN KEY    │ references must exist   │ │
│  │ UNIQUE         │ no duplicate values     │ │
│  │ NOT NULL       │ column always has value │ │
│  │ CHECK          │ custom boolean rule     │ │
│  └────────────────┴────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
App writes data → BEGIN → SQL INSERT/UPDATE/DELETE
→ [CONSISTENCY ← YOU ARE HERE: constraint checks]
→ All constraints pass → COMMIT → Valid state persisted
```

**FAILURE PATH:**

```
Constraint violated (FK, UNIQUE, CHECK, NOT NULL)
→ Database throws ConstraintViolationException
→ Transaction rolled back → App catches exception
→ App returns validation error to user
```

**WHAT CHANGES AT SCALE:**
Under heavy write loads, foreign key enforcement becomes a hotspot - every INSERT to an orders table requires a read on the users index to verify the FK reference. Disabling foreign keys for bulk imports and re-enabling after is a common pattern, but it requires the application to guarantee data integrity during the window without FK checks. Some teams move FK enforcement to application code and drop DB-level FKs entirely - trading safety for write throughput, which is generally inadvisable.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                        |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ACID Consistency is the same as CAP Consistency        | Completely different: ACID Consistency = constraint enforcement; CAP Consistency = all replicas see same data simultaneously                                                                   |
| The database automatically enforces all business rules | The database only enforces declared constraints; application-level rules (negative balance, duplicate orders) must be explicitly declared as CHECK constraints or enforced in application code |
| Disabling foreign keys for performance is safe         | It's safe only if you guarantee no inconsistent data is written during the disabled window - any inconsistency committed will silently corrupt referential integrity                           |
| Consistency is always enforced immediately             | PostgreSQL supports DEFERRABLE constraints - CHECK and FK can be deferred to commit time, allowing temporarily invalid states within a transaction                                             |

---

### 🚨 Failure Modes & Diagnosis

**1. Silent Orphaned Data from Missing Foreign Keys**

**Symptom:** JOIN queries return fewer rows than expected; data discrepancies between tables; reports show wrong totals.

**Root Cause:** No FOREIGN KEY constraint declared; application code that was supposed to maintain referential integrity had a bug; data now exists in child table referencing deleted parent rows.

**Diagnostic:**

```sql
-- Find orphaned order items (no matching order)
SELECT oi.*
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.id IS NULL;

-- PostgreSQL: count orphaned records
SELECT COUNT(*) FROM order_items oi
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.id = oi.order_id
);
```

**Fix:** Add missing FOREIGN KEY constraints. Clean orphaned data first (requires business decision on what to do with orphans). Then add the constraint.

**Prevention:** Always declare FOREIGN KEY constraints at schema design time. Review ERD before any table creation migration.

---

**2. CHECK Constraint Not Preventing Invalid Business State**

**Symptom:** Negative account balances in production; inventory counts below zero; prices at $0.00 for paid products.

**Root Cause:** Business invariants enforced only in application code, not as CHECK constraints. A bug, script, or direct SQL query bypassed the application layer.

**Diagnostic:**

```sql
-- Find violated business invariants
SELECT id, balance FROM accounts WHERE balance < 0;
SELECT id, stock_count FROM products WHERE stock_count < 0;

-- See existing check constraints
SELECT conname, consrc
FROM pg_constraint
WHERE contype = 'c'
  AND conrelid = 'accounts'::regclass;
```

**Fix:**

```sql
-- Add CHECK constraint to prevent future violations
ALTER TABLE accounts
  ADD CONSTRAINT chk_balance_non_negative
  CHECK (balance >= 0);

-- Fix existing violations first (business decision)
-- Then add constraint
```

**Prevention:** For every "this value must always be X" business rule, add a CHECK constraint. Don't rely on application code alone - code paths can be bypassed.

---

**3. UNIQUE Constraint Race Condition**

**Symptom:** Duplicate rows exist despite a UNIQUE constraint; two requests submitted near-simultaneously both insert the same data.

**Root Cause:** Application code checked for existence, found none, then inserted - but between the check and the insert, another thread inserted the same row. The "check-then-act" pattern is not atomic.

**Diagnostic:**

```sql
-- Find duplicates
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Fix:**

```sql
-- Use INSERT ... ON CONFLICT (upsert) instead of check-then-insert
INSERT INTO users (email, name)
VALUES ('alice@example.com', 'Alice')
ON CONFLICT (email) DO NOTHING;
-- OR:
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;
```

**Prevention:** Never use "SELECT then INSERT" for uniqueness checks. Use database-level UNIQUE constraints and handle `ConstraintViolationException` in application code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ACID` - Consistency is the "C"; understand the full four-property model
- `Transaction` - consistency is enforced at transaction boundaries

**Builds On This (learn these next):**

- `Foreign Key / Referential Integrity` - the primary mechanism for cross-table consistency
- `Normalization` - the process of designing schemas that express consistency rules efficiently
- `Isolation Levels` - the "I" in ACID that prevents concurrency from breaking consistency

**Alternatives / Comparisons:**

- `CAP Theorem Consistency` - completely different concept despite the same word; distributed systems trade-off
- `Eventual Consistency` - the BASE model's alternative: data will become consistent eventually, not immediately

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Every transaction leaves the database     │
│              │ in a valid state per declared constraints │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Invalid/orphaned data silently corrupts   │
│ SOLVES       │ reports, logic, downstream systems        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Only declared constraints are enforced -  │
│              │ undeclared business rules are not checked │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always - declare every constraint the     │
│              │ data model requires (FK, UNIQUE, CHECK)   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Bulk imports may need deferred/disabled   │
│              │ FK checks - re-enable and validate after  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Data integrity vs FK enforcement overhead │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Garbage in, garbage out - unless the DB  │
│              │  refuses the garbage at the gate"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Foreign Keys → Normalization → Isolation  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Trade-off) A team decides to remove all FOREIGN KEY constraints from their production database schema because FK checks are slowing writes by 15%. They will enforce referential integrity in application code only. Under what three specific operational scenarios will this decision guarantee data corruption even if the application code is perfectly written?

**Q2.** (TYPE F - Comparison Depth) ACID Consistency and CAP Theorem Consistency both use the word "consistency" but mean completely different things. Describe a distributed database operation (spanning two nodes, two tables) that satisfies ACID Consistency but violates CAP Consistency - and describe the reverse: an operation that satisfies CAP Consistency but violates ACID Consistency.
