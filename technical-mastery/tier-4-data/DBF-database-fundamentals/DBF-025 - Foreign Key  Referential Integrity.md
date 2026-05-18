---
version: 2
layout: default
title: "Foreign Key  Referential Integrity"
parent: "Database Fundamentals"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/databases/foreign-key/
id: DBF-008
category: Database Fundamentals
difficulty: ★★☆
depends_on: Normalization, Transaction, ACID
used_by: Denormalization, Schema Evolution, ORM Patterns
related: Normalization, Constraint, Cascade
tags:
  - database
  - schema-design
  - data-integrity
  - intermediate
---

⚡ TL;DR - A foreign key is a column that must match a value in another table's primary key, enforced by the database - it's the mechanism that makes "this order must belong to a real customer" an invariant, not just a convention.

| #433            | Category: Database Fundamentals                 | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | Normalization, Transaction, ACID                |                 |
| **Used by:**    | Denormalization, Schema Evolution, ORM Patterns |                 |
| **Related:**    | Normalization, Constraint, Cascade              |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An application deletes a customer record. But the `orders` table still has 47 rows with that `customer_id`. Those orders now reference a non-existent customer - orphaned records. The application shows blank customer names on those orders. A JOIN on customer name breaks. A delete cascade that should have happened didn't. Without database-enforced referential integrity, the application must manually maintain these relationships - and it will fail eventually.

**THE BREAKING POINT:**
In a system with 20 tables and 50 foreign key relationships, enforcing all of them through application logic requires 50 "check this reference exists" queries on every write - and will still miss cases when data is inserted directly via SQL scripts, migrations, or administrative tools that bypass the application layer.

**THE INVENTION MOMENT:**
"Let the database enforce that every reference is valid - at the storage level, not the application level."

---

### 📘 Textbook Definition

A **foreign key** is a column (or group of columns) in one table that references the primary key (or unique key) of another table, establishing a parent-child relationship. **Referential integrity** is the guarantee that every foreign key value either (a) matches an existing primary key value in the referenced table, or (b) is NULL (if the column is nullable). The database enforces referential integrity through **foreign key constraints**: INSERT/UPDATE of a child row fails if the referenced parent row doesn't exist; DELETE/UPDATE of a parent row raises an error or triggers a cascade action if child rows exist. Foreign key constraints can be configured with actions on parent deletion: `CASCADE` (delete children), `SET NULL` (null the FK), `SET DEFAULT`, `RESTRICT` (error), `NO ACTION` (deferred error).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A foreign key constraint is the database's guarantee that every reference to another table points to something that actually exists - orphaned records are structurally impossible.

**One analogy:**

> A library's card catalog (foreign key: book catalog entry) always points to an actual physical book (primary key: book shelf location). The library rule: you can't have a catalog card for a book that doesn't exist. And if a book is removed from the shelf, its catalog card must be removed too (CASCADE) or flagged as "location unknown" (SET NULL). Referential integrity is that rule, enforced by the librarian (database), not the patron (application).

**One insight:**
Foreign keys are most controversial as a performance concern - checking the parent exists on every INSERT and checking no children exist on every DELETE adds overhead. But this overhead is almost always worth it: the cost of an orphaned-record data integrity bug in production is far higher than the cost of foreign key validation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A foreign key value must reference an existing primary key (or be NULL if nullable).
2. Cannot INSERT a child row if the parent doesn't exist.
3. Cannot DELETE a parent row if child rows reference it (unless CASCADE or SET NULL is configured).
4. Foreign key checks happen within the same transaction - checks are consistent.

**SYNTAX:**

```sql
-- Creating a foreign key inline:
CREATE TABLE orders (
    id          BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id)
                ON DELETE RESTRICT ON UPDATE CASCADE,
    amount      DECIMAL,
    created_at  TIMESTAMP
);

-- Adding to existing table:
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id)
    REFERENCES customers(id)
    ON DELETE CASCADE;
```

**ON DELETE ACTIONS:**
| Action | Behavior | Use When |
|---|---|---|
| `RESTRICT` | Error if any child exists | Default; safest |
| `NO ACTION` | Same as RESTRICT but deferred | Deferred constraint checking |
| `CASCADE` | Delete all child rows | Ownership (deleting user → delete their posts) |
| `SET NULL` | Set FK column to NULL | Optional associations (deleting author → keep post, null author) |
| `SET DEFAULT` | Set FK to default value | Rare; assign to default parent (e.g., "unassigned" category) |

**DEFERRABLE CONSTRAINTS (PostgreSQL):**

```sql
-- Check FK constraint at commit time, not at statement time
ADD CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
    REFERENCES customers(id) DEFERRABLE INITIALLY DEFERRED;

-- Useful for circular references or bulk reordering operations
BEGIN;
SET CONSTRAINTS fk_orders_customer DEFERRED;
-- ... operations that temporarily violate FK ...
COMMIT; -- FK checked here
```

**THE TRADE-OFFS:**

**Gain:** Structural integrity guarantee - orphaned records are impossible. Simplifies application code (no need to check parent existence). Enables ON DELETE CASCADE for clean data management.

**Cost:** Write overhead - INSERT checks parent exists; DELETE checks no children exist (both are indexed lookups, typically fast but not zero). FK columns must be indexed on the child side to avoid full table scans on parent DELETE. Distributed databases often don't support FKs across shards.

---

### 🧪 Thought Experiment

**SETUP:**
Table: `orders(id, customer_id FK → customers.id, amount)`. No foreign key. A bug in the customer deletion code deletes a customer without deleting their orders.

**WITHOUT FOREIGN KEY:**

- Customer #42 deleted from `customers`.
- `orders` still has 500 rows with `customer_id = 42`.
- `SELECT * FROM orders JOIN customers c ON orders.customer_id = c.id WHERE orders.id = 101` → returns empty (customer 42 doesn't exist, JOIN produces no rows). Application shows blank order.
- `SELECT COUNT(*) FROM orders` shows 500 orders for non-existent customers.
- Analytics: "revenue by customer" under-counts because these orders don't join to any customer.
- Fix requires identifying all orphaned rows, deciding what to do with them, running a migration.

**WITH FOREIGN KEY (ON DELETE RESTRICT):**

- Delete customer #42: `ERROR: update or delete on table "customers" violates foreign key constraint on table "orders"`.
- Application receives error, handles it: either forbid deletion ("customer has active orders") or trigger order archival first, then delete customer.
- No orphaned records ever possible.

**WITH FOREIGN KEY (ON DELETE CASCADE):**

- Delete customer #42: automatically deletes all 500 orders for that customer.
- Fine if orders are "owned" by the customer and have no independent existence.
- Dangerous if orders are billing records that should be retained for audit.

**THE INSIGHT:**
The right ON DELETE action is a business rule, not a technical one. "Delete customer" can mean: forbidden if orders exist (RESTRICT), archive customer only if no orders (application check), cascade delete all orders (CASCADE), or orphan orders into an "unassigned" bucket (SET NULL). The FK constraint enforces whatever that business rule is.

---

### 🧠 Mental Model / Analogy

> A foreign key constraint is like a government ID requirement on a contract. Every contract (child row) must reference a real person (parent row) with a valid ID number (primary key). The registry (database) verifies: "Does ID #42 exist?" on every new contract (INSERT). If ID #42 is cancelled (parent deleted), either all their contracts are voided (CASCADE) or the ID field is set to "unknown" (SET NULL) or the cancellation is blocked (RESTRICT). The registry, not the lawyer writing the contract, enforces this rule.

- "Contract" → child row (order)
- "Person with valid ID" → parent row (customer)
- "ID number" → primary key / foreign key value
- "Registry verification" → FK constraint check
- "ID cancelled, all contracts voided" → ON DELETE CASCADE
- "Lawyer" → application code (not trusted for integrity)

Where this analogy breaks down: unlike a government registry, a database FK constraint can be disabled temporarily (for bulk imports) and then re-enabled - though this creates a window of potential integrity violation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A foreign key is a column that must point to something real in another table. For example, every order must reference a real customer - you can't have an order for customer #999 if customer #999 doesn't exist. The database checks this automatically and refuses to create invalid references.

**Level 2 - How to use it (junior developer):**
Add `REFERENCES other_table(pk_column)` to a column definition. Choose ON DELETE action: RESTRICT (safe default), CASCADE (delete children with parent), SET NULL (clear FK when parent deleted). Always create an index on the FK column in the child table - without an index, parent DELETE causes a full table scan on the child table.

**Level 3 - How it works (mid-level engineer):**
FK enforcement is two operations:

1. **INSERT/UPDATE child:** Database checks: does `parent_pk = FK_value` exist in the parent table? Requires an index on parent's PK (always exists). Typically a single B+ Tree lookup - O(log n).
2. **DELETE/UPDATE parent:** Database checks: does any child have `FK_column = parent_pk_value`? Requires an index on the child's FK column. Without this index: full table scan on child. With index: O(log n) lookup. Always create `CREATE INDEX ON child(fk_column)` for every FK.

FK check happens within the current transaction's MVCC snapshot - consistent view, no locking (unless FOR UPDATE or serializable isolation).

**Level 4 - Why it was designed this way (senior/staff):**
Referential integrity enforcement is one of the most important correctness features relational databases offer. The decision to enforce it at the storage layer (not application layer) is fundamental to the relational model - E.F. Codd's original design explicitly includes referential integrity as a first-class concern. The controversy in modern distributed systems: foreign keys don't work across shards or across microservice boundaries. This is a genuine limitation - distributed transactions (2PC) are expensive, and FK checks across service boundaries require coupling. The pragmatic answer is: FK constraints within a service's database are essential; cross-service referential integrity must be handled through eventual consistency, compensating transactions, or acceptance of temporary inconsistency. Disabling FKs entirely to avoid this problem is throwing out correctness for the easy case to avoid complexity in the distributed case.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ FK ENFORCEMENT: INSERT + DELETE PATH                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ INSERT INTO orders (customer_id=42, amount=100):     │
│ 1. Check: SELECT 1 FROM customers WHERE id=42        │
│    (uses PK index on customers - O(log n))           │
│ 2. If exists → INSERT succeeds                       │
│ 3. If not exists → ERROR: FK violation               │
│                                                      │
│ DELETE FROM customers WHERE id=42:                   │
│ 1. Check: SELECT 1 FROM orders WHERE customer_id=42  │
│    (needs index on orders.customer_id!)              │
│ 2. ON DELETE RESTRICT: if any exist → ERROR          │
│ 3. ON DELETE CASCADE: DELETE FROM orders             │
│    WHERE customer_id=42 (recursively)                │
│ 4. ON DELETE SET NULL: UPDATE orders                 │
│    SET customer_id=NULL WHERE customer_id=42         │
│                                                      │
│ ⚠️  Without index on orders.customer_id:             │
│    Full table scan on every customer DELETE          │
│    100M orders → 100M rows scanned → seconds         │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
User requests account deletion
→ Application calls DELETE FROM customers WHERE id=42
→ [FOREIGN KEY ← YOU ARE HERE: database enforces]
→ DB checks: orders with customer_id=42? (indexed lookup)
→ ON DELETE RESTRICT: error → app handles gracefully
→ OR: app first moves orders to archive, then deletes
  customer
→ OR: CASCADE: orders deleted automatically with customer
```

**FAILURE PATH:**

```
FK constraint disabled for bulk import
→ Import inserts order_items with non-existent product_ids
→ FK constraint re-enabled (or never re-enabled if
  forgotten)
→ 50,000 orphaned order_items with invalid product
  references
→ Application JOIN shows broken product data
→ Silent data corruption in production
```

**WHAT CHANGES AT SCALE:**
At high write rates (100K+ inserts/second), FK check overhead per insert becomes significant. Strategies: (1) batch inserts that validate references in application before DB insert; (2) use deferrable constraints for bulk operations; (3) for microservices, accept that cross-service FKs are impossible - enforce consistency at the service boundary with compensating transactions. Distributed databases (Cassandra, DynamoDB) intentionally omit FK support - the application must enforce referential integrity or accept eventual consistency.

---

### ⚖️ Comparison Table

| On Delete Action | Parent Delete Behavior | Child State       | Use Case                             |
| ---------------- | ---------------------- | ----------------- | ------------------------------------ |
| **RESTRICT**     | Error - blocked        | Unchanged         | Default; prevent accidental deletion |
| **NO ACTION**    | Error at commit        | Unchanged         | Deferred constraint checking         |
| **CASCADE**      | Parent deleted         | Child deleted     | Ownership relationship               |
| **SET NULL**     | Parent deleted         | FK set to NULL    | Optional association                 |
| **SET DEFAULT**  | Parent deleted         | FK set to default | Reassign to default parent           |

How to choose: RESTRICT is the safest default - it forces explicit handling of child records before parent deletion. Use CASCADE only when children have no independent existence (posts, comments, attachments owned by a user). Use SET NULL for optional associations (author deleted → posts become authorless).

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                   |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FK constraints hurt performance significantly          | FK checks are single B+ Tree lookups - typically <1ms. Performance impact is only significant if the child table's FK column has no index (causing full table scans on parent DELETE)     |
| ORMs handle referential integrity without DB-level FKs | ORMs validate references at the application level, but direct SQL queries, migration scripts, and data imports bypass the ORM - only DB-level FKs provide universal enforcement           |
| ON DELETE CASCADE is always convenient                 | CASCADE can cause accidental mass deletion - deleting a root entity cascades to ALL descendants. In billing/audit systems, deleting a customer should NOT cascade to their invoices       |
| Foreign keys work across microservices                 | FKs only work within a single database instance - they cannot span service boundaries; cross-service referential integrity requires application-level enforcement or eventual consistency |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing Index on FK Column Causes Slow Parent DELETE**

**Symptom:** Deleting a user takes 30 seconds; slow query log shows the DELETE blocked by a full table scan on a child table.

**Root Cause:** No index on the FK column in the child table. The database must scan all rows of the child table to check if any reference the parent being deleted.

**Diagnostic:**

```sql
-- Find FK columns without indexes (PostgreSQL)
SELECT
  tc.table_name AS child_table,
  kcu.column_name AS fk_column,
  ccu.table_name AS parent_table,
  ccu.column_name AS parent_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index
    JOIN pg_attribute ON pg_attribute.attrelid = pg_index.indrelid
      AND pg_attribute.attnum = ANY(pg_index.indkey)
    JOIN pg_class ON pg_class.oid = pg_index.indrelid
    WHERE pg_class.relname = tc.table_name
      AND pg_attribute.attname = kcu.column_name
  );
```

**Fix:** `CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders(customer_id)` - creates the index without blocking reads/writes.

**Prevention:** Rule: every FK column must have an index. Include in schema review checklist. Automate detection with the above query in CI/CD database migration validation.

---

**2. Orphaned Records from Disabled FK During Bulk Import**

**Symptom:** After a bulk data migration, application shows foreign key errors when reading data; JOINs return empty results for records that should have matching parents.

**Root Cause:** FK constraints were disabled during import for performance; the import inserted child records with parent IDs that don't exist; FK constraints were re-enabled (or not) without validating existing data.

**Diagnostic:**

```sql
-- Find orphaned order_items (no matching order)
SELECT oi.id, oi.order_id
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.id IS NULL;

-- Find orphaned orders (no matching customer)
SELECT o.id, o.customer_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE c.id IS NULL;
```

**Fix:** For orphaned records: decide disposition - delete, reassign to a placeholder parent, or create the missing parent record. Then re-enable FK constraints: `ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_customer`.

**Prevention:** When disabling FKs for bulk import, always run orphan detection queries after import before re-enabling constraints. Better: use `SET CONSTRAINTS ALL DEFERRED` within a transaction instead of disabling - this defers FK checks to commit time while still detecting violations.

---

**3. Accidental Cascade Deletion**

**Symptom:** Deleting a parent record triggers unexpected deletion of thousands of child records; data loss discovered in production.

**Root Cause:** `ON DELETE CASCADE` was set on a relationship that should have been `RESTRICT`. Developer or admin deleted a parent record without realizing the cascade scope.

**Diagnostic:**

```sql
-- Check all CASCADE foreign keys in the schema
SELECT
  tc.table_name AS child_table,
  kcu.column_name AS fk_column,
  ccu.table_name AS parent_table,
  rc.delete_rule AS on_delete
FROM information_schema.referential_constraints rc
JOIN information_schema.table_constraints tc
  ON rc.constraint_name = tc.constraint_name
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
  ON rc.unique_constraint_name = ccu.constraint_name
WHERE rc.delete_rule = 'CASCADE'
ORDER BY child_table;
```

**Fix:** Restore deleted records from backup. Change `ON DELETE CASCADE` to `ON DELETE RESTRICT`: `ALTER TABLE orders DROP CONSTRAINT fk_customer; ALTER TABLE orders ADD CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT`.

**Prevention:** Audit all CASCADE FK relationships in the schema annually. In billing/audit systems, use RESTRICT for all financial records (orders, invoices, transactions) - these must never be automatically deleted by cascade.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Normalization` - FKs are the mechanism that links normalized tables
- `Transaction` - FK checks happen within transaction boundaries; deferrable FKs check at commit

**Builds On This (learn these next):**

- `Denormalization` - denormalized schemas may relax FK constraints for performance
- `Schema Evolution` - FK constraints complicate migrations (must drop before schema change)
- `ORM Patterns` - ORMs generate FK constraints; understanding them helps debug ORM behavior

**Alternatives / Comparisons:**

- `Normalization` - FKs are the implementation of normalized schema relationships
- `Constraint` (CHECK, UNIQUE, NOT NULL) - other database-enforced integrity mechanisms

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Column that must match a PK in another   │
│              │ table; database enforces validity        │
├──────────────┼──────────────────────────────────────────┤
│ ON DELETE    │ RESTRICT: error (safe default)           │
│ ACTIONS      │ CASCADE: delete children                 │
│              │ SET NULL: null the FK                    │
├──────────────┼──────────────────────────────────────────┤
│ CRITICAL     │ Always index the FK column in child table│
│              │ - unindexed FK = full scan on parent DEL │
├──────────────┼──────────────────────────────────────────┤
│ AVOID        │ CASCADE on billing/audit records         │
│              │ FK across microservice boundaries        │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Data integrity vs. write overhead;       │
│              │ FK enforcement vs. distributed scale     │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "The database, not the application,      │
│              │  guarantees every reference is real"     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Normalization → Schema Evolution → ORM   │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Trade-off) A microservices architecture has three services: `users-service` (owns `users` table), `orders-service` (owns `orders` table with `user_id` reference), `payments-service` (owns `payments` table with `order_id` reference). Database-level foreign keys cannot span service boundaries. Design three approaches to maintain referential integrity across services: (a) eventual consistency with orphan detection, (b) saga pattern with compensating transactions, (c) outbox pattern with event sourcing. Compare them on: consistency guarantee, failure handling complexity, and operational overhead.

**Q2.** (TYPE D - Failure Scenario) A production system has `ON DELETE CASCADE` from `accounts → orders → order_items → shipments`. A support engineer runs `DELETE FROM accounts WHERE status='trial' AND created_at < '2020-01-01'` to clean up old trial accounts. The query deletes 5,000 accounts. Due to the cascade, it also deletes 50,000 orders, 200,000 order_items, and 40,000 shipments. Some of those "trial" orders were converted to paid orders and have associated financial records. Describe the complete failure scenario, what should have prevented it, and how to recover without a full database restore.
