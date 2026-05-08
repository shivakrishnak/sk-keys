---
layout: default
title: "Data Integrity Constraints"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /databases/data-integrity-constraints/
id: DBF-013
category: Database Fundamentals
difficulty: ★★☆
depends_on: SQL, Relational Database, Schema Design Best Practices
used_by: Database Fundamentals, Spring Data JPA
related: ACID Transactions, Schema Design Best Practices, Foreign Key
tags:
  - database
  - intermediate
  - foundational
---

# DBF-013 - Data Integrity Constraints

⚡ TL;DR - Data integrity constraints are database-enforced rules (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, NOT NULL) that make invalid data structurally impossible to store.

| Field        | Value |
|--------------|-------|
| Depends on   | SQL, Relational Database, Schema Design Best Practices |
| Used by      | Database Fundamentals, Spring Data JPA |
| Related      | ACID Transactions, Schema Design Best Practices, Foreign Key |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** An e-commerce application has a validation rule in Java: "order amount must be positive." A junior developer writes a bulk import script that bypasses the application layer. Negative amounts enter the database. Financial reports are wrong. A refund process runs on negative amounts and credits accounts instead of debiting. The bug is not caught for three months.

**THE BREAKING POINT:** Every layer of an application - web API, batch jobs, admin scripts, ORM queries, raw SQL consoles - can write to the database. Application-level validation only protects one entry point. The database is the only system that sees every write, from every source.

**THE INVENTION MOMENT:** Codd's relational model (1970) defined constraints as part of the schema, not the application. The insight: rules about data belong with the data, not the code that happens to write it today.

---

### 📘 Textbook Definition

**Data integrity constraints** are declarative rules defined in the database schema that the DBMS enforces on every data modification (INSERT, UPDATE, DELETE), regardless of the source. The five standard constraint types are: **NOT NULL** (column must have a value), **UNIQUE** (column value must be distinct across all rows), **PRIMARY KEY** (NOT NULL + UNIQUE; uniquely identifies each row), **FOREIGN KEY** (column value must reference an existing row in another table), and **CHECK** (column value must satisfy a boolean expression). Constraints may be immediate (enforced per statement) or deferrable (enforced at transaction COMMIT).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Constraints are enforcement built into the database so that invalid data cannot be stored, no matter which application writes it.

> Imagine a bank's physical vault with mechanical locks that prevent withdrawals below zero. A teller, a manager, a wire transfer system, and an ATM all use the same vault. The lock - not each operator's training - is the guarantee.

**One insight:** Every validation rule that can be expressed as a constraint SHOULD be a constraint. Application-level validation is defense-in-depth but not the primary guarantee. The database constraint is.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Constraints are checked by the database engine on every write - not by the application, not by the ORM, not by the caller.
2. A violated constraint causes the statement to fail and roll back (statement-level). The transaction remains open.
3. Primary key = entity integrity (each row is uniquely identifiable).
4. Foreign key = referential integrity (relationships between tables are consistent - no orphaned rows).
5. CHECK and UNIQUE = domain integrity (values are valid within their defined domain).

**DERIVED DESIGN:**
- **Deferrable constraints:** INITIALLY DEFERRED (checked at COMMIT) or INITIALLY IMMEDIATE (checked at statement). Enables multi-step operations that temporarily violate constraints within a transaction.
- **Partial unique index (PostgreSQL):** Enforce uniqueness only on rows satisfying a condition - e.g., unique email only for non-deleted rows.
- **FK action clauses:** `ON DELETE CASCADE` (auto-delete children), `ON DELETE SET NULL` (null the FK), `ON DELETE RESTRICT` (prevent parent delete if children exist - default behavior).

**THE TRADE-OFFS:**

**Gain:** Correctness guaranteed at the data layer; impossible for any code path to bypass; documents business rules in the schema.

**Cost:** Constraints slow writes slightly (index maintenance for UNIQUE, FK lookup for FK, CHECK evaluation); bulk imports may need to disable constraints temporarily; deferrable constraints add complexity; foreign key constraints require indexes on FK columns or deletes become O(n).

---

### 🧪 Thought Experiment

**SETUP:** A `transactions` table has a `type` column that should only contain `DEBIT` or `CREDIT`. This rule is enforced in the Java service layer.

**WITHOUT CHECK CONSTRAINT:**
- A new developer writes an admin script using raw JDBC. They use the value `'TRANSFER'` for a new transaction type. No validation error. Data enters the database.
- Six months later, a downstream reporting query `WHERE type = 'CREDIT'` misses all `'TRANSFER'` rows. A $2M discrepancy in financial reports.

**WITH CHECK CONSTRAINT:**
```sql
CONSTRAINT chk_transactions_type
  CHECK (type IN ('DEBIT', 'CREDIT'))
```
The admin script fails with `ERROR: new row for relation "transactions" violates check constraint`. The developer must update the constraint (visible in source control) before adding a new type. The schema becomes self-documenting.

**THE INSIGHT:** The constraint enforces the business rule at every entry point - API, script, direct SQL, ORM - with no additional code.

---

### 🧠 Mental Model / Analogy

> Data integrity constraints are like the physical locks and gates in a hospital dispensary. The rule "only authorized personnel can dispense narcotics" is not just a policy in the employee handbook (application-level validation). It is a physical lock on the cabinet. No matter who approaches - nurse, doctor, janitor, visitor - the lock applies. The lock is the enforcement mechanism; the handbook is documentation.

- **Hospital dispensary cabinet** = database table
- **Physical lock** = database constraint
- **Employee handbook rule** = application-level validation
- **Authorized personnel** = valid data values
- **Unauthorized visitor** = invalid INSERT/UPDATE

Where this analogy breaks down: A physical lock is binary (open or locked). Database constraints can be deferred (temporarily unlocked for the duration of a transaction) - which is why deferrable constraints exist.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Database constraints are rules the database checks before saving any data. For example, "this field must have a value," or "this number must be positive." If the rule is broken, the save fails - automatically.

**Level 2 - How to use it (junior developer):**
Add `NOT NULL` to required columns. Add `UNIQUE` to columns like `email` that must be distinct. Define a `PRIMARY KEY`. Add `FOREIGN KEY (customer_id) REFERENCES customers(id)` to enforce relationships. Add `CHECK (amount > 0)` for domain rules. These are defined in `CREATE TABLE` or added with `ALTER TABLE ADD CONSTRAINT`.

**Level 3 - How it works (mid-level engineer):**
`PRIMARY KEY` creates a B-tree unique index automatically. `UNIQUE` creates a separate B-tree index. `FOREIGN KEY` checks the referenced table on INSERT/UPDATE; checks child table for orphans on DELETE/UPDATE of parent. `CHECK` evaluates the boolean expression inline in the executor for every modified row. `NOT NULL` is a bitmask check in the row header - essentially free. Deferrable constraints (PostgreSQL, Oracle) delay enforcement until `COMMIT`, enabling multi-step transactions that temporarily violate constraints.

**Level 4 - Why it was designed this way (senior/staff):**
The relational model's key contribution over file systems was the separation of integrity rules from application code. Codd defined three types of integrity: entity integrity (PK), referential integrity (FK), and domain integrity (CHECK). These are schema-level concerns, not application concerns - because the schema outlives any specific application. A database may be written to by ten different applications over its lifetime; the schema-level constraints are the only invariants that survive all of them. Deferrable constraints were introduced to handle the bootstrapping problem: when inserting two mutually referencing rows, one must be inserted first, temporarily violating the FK. Deferring to commit allows the transaction to complete both inserts before checking.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│       Constraint Check Order per Row        │
│                                             │
│  INSERT/UPDATE/DELETE statement received    │
│          │                                  │
│          ▼                                  │
│  1. NOT NULL check (per column, per row)    │
│          │                                  │
│          ▼                                  │
│  2. Data type check (type coercion)         │
│          │                                  │
│          ▼                                  │
│  3. CHECK constraint evaluation             │
│          │                                  │
│          ▼                                  │
│  4. UNIQUE / PK index lookup                │
│          │                                  │
│          ▼                                  │
│  5. FK lookup in referenced table           │
│          │                                  │
│  Any violation? → statement fails, rollback │
│  All pass?      → row written to heap       │
└─────────────────────────────────────────────┘
```

**FK ON DELETE actions:**
```
ON DELETE RESTRICT    Block delete if children exist (default)
ON DELETE CASCADE     Delete children automatically
ON DELETE SET NULL    Set FK column to NULL in children
ON DELETE NO ACTION   Like RESTRICT but deferrable
ON DELETE SET DEFAULT Set FK to column's DEFAULT value
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Application executes INSERT INTO orders
  │
  ▼
PostgreSQL executor processes row
  │
  ├── NOT NULL: order_id, customer_id, amount → pass
  │
  ├── CHECK: amount > 0 → 150.00 > 0 → pass
  │
  ├── UNIQUE: order_id unique index lookup → no conflict
  │
  └── FK: customer_id=42 exists in customers?
               ← YOU ARE HERE
              YES → pass
              NO  → ERROR: FK violation
  │
  ▼
Row written; indexes updated; constraint recorded
```

**FAILURE PATH:**
- **FK violation on INSERT:** Referenced row doesn't exist. `ERROR: insert or update on table "orders" violates foreign key constraint`.
- **UNIQUE violation:** Duplicate email insert. `ERROR: duplicate key value violates unique constraint "uq_customers_email"`.
- **NOT NULL violation:** NULL into required column. `ERROR: null value in column "name" of relation "customers" violates not-null constraint`.
- **CHECK violation:** Amount = -50. `ERROR: new row for relation "orders" violates check constraint "chk_orders_amount"`.

**WHAT CHANGES AT SCALE:**
- FK constraints slow bulk imports: each inserted row triggers a lookup in the referenced table. For large batch imports, temporarily disable FK checks (with caution; re-enable and validate before commit).
- In distributed databases (Vitess, CockroachDB), FK enforcement across shards requires cross-shard lookups - often disabled for performance, pushing enforcement to the application layer.
- Partial indexes (`CREATE UNIQUE INDEX ... WHERE deleted_at IS NULL`) maintain unique constraint semantics for soft-delete patterns.

---

### 💻 Code Example

**Complete table with all constraint types:**
```sql
CREATE TABLE orders (
  -- PRIMARY KEY: entity integrity
  id            BIGSERIAL PRIMARY KEY,

  -- NOT NULL: required fields
  customer_id   BIGINT      NOT NULL,
  order_date    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status        VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  amount        DECIMAL(12,2) NOT NULL,

  -- UNIQUE: business-level uniqueness
  reference_code VARCHAR(50) UNIQUE,

  -- CHECK: domain constraints
  CONSTRAINT chk_orders_amount
    CHECK (amount > 0),

  CONSTRAINT chk_orders_status
    CHECK (status IN ('PENDING','CONFIRMED',
                      'SHIPPED','DELIVERED','CANCELLED')),

  -- FOREIGN KEY: referential integrity
  CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id)
    REFERENCES customers(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

-- Index on FK column (performance for DELETE on customers)
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

**Deferrable FK constraint (for mutual references):**
```sql
-- Deferrable: check at COMMIT, not per-statement
ALTER TABLE employees
ADD CONSTRAINT fk_emp_manager
  FOREIGN KEY (manager_id) REFERENCES employees(id)
  DEFERRABLE INITIALLY DEFERRED;

-- Now you can insert the manager after the employee
-- within the same transaction:
BEGIN;
INSERT INTO employees(id, name, manager_id) VALUES (1,'CEO',2);
INSERT INTO employees(id, name, manager_id) VALUES (2,'VP',1);
COMMIT;  -- FK check happens here; both rows exist
```

**Partial unique index for soft delete:**
```sql
-- Allow multiple deleted records with same email
-- Only enforce uniqueness for active (non-deleted) rows
CREATE UNIQUE INDEX uq_customers_active_email
ON customers(email)
WHERE deleted_at IS NULL;
```

**Checking existing constraints:**
```sql
-- PostgreSQL: list all constraints on a table
SELECT conname, contype, pg_get_constraintdef(oid)
FROM   pg_constraint
WHERE  conrelid = 'orders'::regclass
ORDER  BY contype;

-- MySQL: show constraints
SELECT constraint_name, constraint_type
FROM   information_schema.table_constraints
WHERE  table_name = 'orders';
```

---

### ⚖️ Comparison Table

| Constraint | Enforces | Creates Index? | NULL Handling | When Checked |
|---|---|---|---|---|
| PRIMARY KEY | Uniqueness + NOT NULL | Yes (B-tree) | Not allowed | Per statement |
| UNIQUE | Uniqueness | Yes (B-tree) | NULLs not compared | Per statement |
| NOT NULL | Column has value | No | Prevents NULL | Per statement |
| FOREIGN KEY | Referential integrity | No (add manually!) | NULL FK = no check | Per statement (or deferred) |
| CHECK | Boolean expression | No | NULL passes CHECK | Per statement |

| FK Action | What Happens | When to Use |
|---|---|---|
| RESTRICT | Block parent delete | Default; safest |
| CASCADE | Auto-delete children | Parent owns children |
| SET NULL | Null the FK in children | Optional relationship |
| SET DEFAULT | Set FK to default | Rare; re-assign to default |
| NO ACTION | Like RESTRICT but deferrable | Complex transactions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "CHECK constraints prevent NULL values" | `CHECK (amount > 0)` does NOT prevent NULL. `NULL > 0` evaluates to UNKNOWN (not FALSE), so the constraint passes. Combine CHECK with NOT NULL if NULL should be invalid. |
| "UNIQUE constraint prevents all duplicates including NULL" | Most databases allow multiple NULL values in a UNIQUE column (NULL ≠ NULL). Use `NOT NULL` + `UNIQUE` together to prevent both NULL and duplicates. |
| "FK constraints are automatically indexed" | PostgreSQL, MySQL, and Oracle do NOT automatically create indexes on FK columns. Without the index, deleting a parent row requires a full scan of the child table. Always create the index explicitly. |
| "Constraints slow down reads" | Constraints are only checked on writes (INSERT/UPDATE/DELETE). Reads are unaffected. The B-tree indexes created for PK and UNIQUE constraints actually speed up reads. |
| "Disabling FK during bulk load is always safe" | Disabling FK constraints during a bulk load means the database will not verify referential integrity for imported rows. You must manually validate and re-enable - and if invalid data was imported, re-enabling will fail. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: FK Constraint Violation in Application**

**Symptom:** `ERROR: insert or update on table "order_items" violates foreign key constraint "fk_order_items_order"`. Application throws `DataIntegrityViolationException`.

**Root Cause:** Application tried to insert an `order_item` referencing a non-existent `order_id`, or the order was deleted after the item was read.

**Diagnostic:**
```sql
-- Verify the referenced order exists
SELECT id FROM orders WHERE id = 999;

-- Check FK constraint definition
SELECT pg_get_constraintdef(oid)
FROM   pg_constraint
WHERE  conname = 'fk_order_items_order';
```

**Fix:** Ensure the parent order is committed before inserting children. Use `ON DELETE CASCADE` if child rows should be deleted with the parent, or `ON DELETE RESTRICT` to prevent accidental orphan creation.

**Prevention:** Use database transactions to ensure parent rows are committed before inserting dependent children. Never assume a row exists - always verify in the transaction that creates dependencies.

---

**Mode 2: Bulk Import Fails Due to CHECK Constraint**

**Symptom:** `COPY` or batch INSERT fails: `ERROR: new row for relation "products" violates check constraint "chk_products_price"`.

**Root Cause:** Source data contains invalid values (negative prices, invalid status codes) that violate defined CHECK constraints.

**Diagnostic:**
```sql
-- Find the violating rows before import
SELECT * FROM staging.products
WHERE price <= 0 OR price IS NULL;

SELECT * FROM staging.products
WHERE status NOT IN ('ACTIVE','INACTIVE','DISCONTINUED');
```

**Fix:**
```sql
-- Clean the data before import
UPDATE staging.products
SET price = 0.01 WHERE price <= 0;

-- OR: import with constraint disabled (risky)
ALTER TABLE products DISABLE TRIGGER ALL;
-- ... import ...
ALTER TABLE products ENABLE TRIGGER ALL;
-- Run validation query to check for violations after
```

**Prevention:** Validate data against schema constraints in a staging table or with pre-flight SQL queries before loading into the production table.

---

**Mode 3: Unique Constraint Violation in Concurrent Inserts**

**Symptom:** Intermittent `ERROR: duplicate key value violates unique constraint "uq_customers_email"` in a concurrent API. Happens under load, not in testing.

**Root Cause:** Two concurrent requests check "does this email exist?" simultaneously, both find it doesn't, and both proceed to INSERT - creating a race condition (check-then-act pattern).

**Diagnostic:**
```sql
-- Find duplicate emails that somehow got in
SELECT email, COUNT(*) FROM customers
GROUP BY email HAVING COUNT(*) > 1;
```

**Fix:**
```sql
-- Use INSERT ... ON CONFLICT for idempotent upsert
INSERT INTO customers(email, full_name)
VALUES ('user@example.com', 'Jane Doe')
ON CONFLICT (email) DO NOTHING;
-- or: ON CONFLICT (email) DO UPDATE SET ...
```

**Prevention:** Rely on the UNIQUE constraint, not application-level "check first." Use `INSERT ... ON CONFLICT` (PostgreSQL) or `INSERT IGNORE` / `ON DUPLICATE KEY UPDATE` (MySQL) for concurrent-safe inserts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SQL - the DDL syntax for defining constraints
- Relational Database - the model constraints are built into
- Schema Design Best Practices - when and how to apply constraints as part of schema design

**Builds On This (learn these next):**
- ACID Transactions - how constraint checks interact with transaction isolation
- Query Optimization - how PK/UNIQUE indexes created by constraints affect query plans
- Spring Data JPA - how JPA maps entity annotations to database constraints

**Alternatives / Comparisons:**
- Application-level validation - defense in depth, but not a replacement for DB constraints
- Database Triggers - more powerful but more complex enforcement mechanism
- Foreign Key - the referential integrity mechanism in detail

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════╗
║ WHAT IT IS     DB-enforced schema rules     ║
║ PROBLEM SOLVED Invalid data from any source ║
║                bypassing application checks ║
║ KEY INSIGHT    Constraints fire on every    ║
║                write regardless of source   ║
║ USE WHEN       Any rule about data validity ║
║                that must hold universally   ║
║ AVOID WHEN     Bulk import: disable FK      ║
║                temporarily (validate after) ║
║ TRADE-OFF      Correctness vs write perf;  ║
║                DB-enforced vs app-enforced  ║
║ ONE-LINER      CHECK + NOT NULL together;  ║
║                always index FK columns      ║
║ NEXT EXPLORE   Deferrable constraints,      ║
║                partial indexes, ON CONFLICT ║
╚══════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(E - First Principles)** SQL's CHECK constraint evaluates to UNKNOWN (not FALSE) when any operand is NULL, causing the constraint to pass. This is intentional per the SQL standard. What are the implications for a constraint like `CHECK (discount_pct BETWEEN 0 AND 100)` on a nullable `discount_pct` column - and what is the correct way to enforce "either NULL or between 0 and 100"?

2. **(A - System Interaction)** A Spring Data JPA `@Entity` with `@Column(nullable = false)` and a database column with `NOT NULL`. The JPA validation fires before the SQL is sent to the database. If the JPA validation is removed (annotation deleted), does correctness change? Under what circumstances would the database constraint alone be insufficient?

3. **(C - Design Trade-off)** You have a `customers` table and an `orders` table with `FK orders.customer_id → customers.id ON DELETE CASCADE`. A product manager asks to add a "delete account" feature. Describe the complete cascade effect on dependent tables, how to audit what will be deleted before the deletion, and what alternative to CASCADE would give more control.
