---
layout: default
title: "Normalization"
parent: "Database Fundamentals"
nav_order: 36
permalink: /databases/normalization/
id: DBF-036
category: Database Fundamentals
difficulty: ★★☆
depends_on: Foreign Key / Referential Integrity, Database Fundamentals
used_by: Denormalization, Schema Design, Query Planner
related: Denormalization, Foreign Key / Referential Integrity, Index Types
tags:
  - database
  - schema-design
  - data-modeling
  - intermediate
---

# DBF-036 — Normalization

⚡ TL;DR — Normalization organizes a relational database schema into forms (1NF–BCNF) that eliminate redundant data and update anomalies — every fact stored once, in the right table, with the right key.

| #431            | Category: Database Fundamentals                                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Foreign Key / Referential Integrity, Database Fundamentals        |                 |
| **Used by:**    | Denormalization, Schema Design, Query Planner                     |                 |
| **Related:**    | Denormalization, Foreign Key / Referential Integrity, Index Types |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce system stores order data in a single flat table:

```
orders: order_id, customer_name, customer_email, customer_city,
        product_name, product_price, quantity, order_date
```

Problems:

1. **Update anomaly:** Customer changes email → must update every row with that customer's orders. Miss one row → inconsistent data.
2. **Insert anomaly:** Can't add a new product until an order exists for it — product data lives in the orders table.
3. **Delete anomaly:** Delete the last order for a customer → lose all customer information.
4. **Redundancy:** Customer's city stored once per order, not once per customer. 100 orders = 100 copies of the same city.

**THE BREAKING POINT:**
Redundant storage leads to divergent data (the same fact stored differently in different places), making data integrity impossible to maintain through application logic alone.

**THE INVENTION MOMENT:**
"Store each fact exactly once, in the table where it belongs, referenced by key elsewhere."

---

### 📘 Textbook Definition

**Normalization** is the process of structuring a relational database schema to reduce data redundancy and improve data integrity by organizing data into multiple related tables according to normal forms. The major normal forms are: **1NF** (First Normal Form) — atomic column values, no repeating groups; **2NF** (Second Normal Form) — no partial dependencies on a composite primary key; **3NF** (Third Normal Form) — no transitive dependencies (non-key attributes depend only on the key); **BCNF** (Boyce-Codd Normal Form) — every determinant is a superkey; **4NF/5NF** — handle multi-valued dependencies and join dependencies (rare in practice). In practice, most schemas target 3NF or BCNF.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Normalization means storing each piece of data exactly once by decomposing tables so every non-key column depends only on the primary key — eliminating redundancy and update anomalies.

**One analogy:**

> A well-organized office filing system. You don't write the company address on every invoice — you have one "companies" file and reference it from each invoice. If the company moves, you update one record. Without normalization: you'd write the address on every invoice, and moving means updating 10,000 pieces of paper. Normalization is the discipline of "store each fact once, reference it from everywhere else."

**One insight:**
The goal of normalization is not to minimize disk space — it's to ensure that any update, insert, or delete operation can be performed without creating inconsistencies. Normalization makes it _structurally impossible_ to have the same fact stored differently in two places.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **1NF:** Every column contains atomic (indivisible) values; no repeating groups; rows are uniquely identifiable.
2. **2NF (requires composite PK):** Every non-key column depends on the _whole_ primary key, not just part of it.
3. **3NF:** Every non-key column depends directly on the primary key, not transitively through another non-key column.
4. **BCNF:** Every functional dependency `X → Y` has X as a superkey. (Stricter than 3NF in edge cases.)

**EXAMPLES:**

**Violates 1NF:**

```
customer_id | name   | phone_numbers
1           | Alice  | "555-1234, 555-5678"  ← not atomic
```

Fix: separate `customer_phones(customer_id, phone_number)` table.

**Violates 2NF:**

```
order_id | product_id | product_name | quantity  ← PK: (order_id, product_id)
1        | 101        | Laptop       | 2
```

`product_name` depends only on `product_id`, not the full composite key `(order_id, product_id)`.
Fix: move `product_name` to `products(product_id, product_name)`.

**Violates 3NF:**

```
employee_id | department_id | department_name  ← PK: employee_id
1           | 10            | Engineering
```

`department_name` depends on `department_id` (non-key), not directly on `employee_id`.
Fix: separate `departments(department_id, department_name)`.

**BCNF (stricter than 3NF):**
Only relevant when a table has multiple overlapping candidate keys — rare in practice.

**THE TRADE-OFFS:**
**Gain:** No redundancy → no update anomalies. Smaller tables → faster writes. Clear data relationships → easier schema evolution.
**Cost:** More tables → more JOINs for queries. JOIN-heavy queries can be slower than denormalized scans. OLAP workloads often intentionally denormalize for read performance.

---

### 🧪 Thought Experiment

**SETUP:**
Design a schema for a university: students enroll in courses taught by professors in specific rooms.

**UNNORMALIZED (single table):**

```
student_id | student_name | course_id | course_name | professor_id | professor_name | room_id | room_capacity
```

- Update anomaly: rename a course → update every enrollment row.
- Delete anomaly: last student drops a course → course info lost.
- Insert anomaly: can't add a course until a student enrolls.

**NORMALIZED TO 3NF:**

```
students(student_id, student_name, email)
professors(professor_id, professor_name, department)
rooms(room_id, building, capacity)
courses(course_id, course_name, professor_id FK, room_id FK)
enrollments(student_id FK, course_id FK, grade, enrolled_date)
             ↑ PK: (student_id, course_id)
```

- Rename a course: update 1 row in `courses`.
- Add a course before enrollment: insert into `courses` with no enrollments.
- Remove last enrollment: course data preserved in `courses`.

**THE INSIGHT:**
The normalized schema makes all three anomalies structurally impossible. The cost: a query like "show all students with their course names and professors" now requires 3–4 JOINs. This is the normalization/denormalization trade-off — correct by construction, or fast reads.

---

### 🧠 Mental Model / Analogy

> Normalization is like the principle of "single source of truth" in software engineering. In code, you don't copy-paste the same constant in 50 files — you define it once and reference it. If you need to change it, you change it in one place. Normalization applies the same principle to data: each fact (customer's city, product's price, professor's name) lives in exactly one table. All other tables reference it via foreign key, never duplicate it.

- "Defining a constant once" → normalized table (one row per entity)
- "Copy-pasting the constant" → storing the same fact in multiple rows
- "Changing the constant in 50 files" → update anomaly (must update all copies)
- "Foreign key reference" → the reference to the single source of truth

Where this analogy breaks down: unlike code constants, database normalization has formal mathematical definitions (normal forms) — it's not just good practice, it's a provably correct structural property.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Normalization is the practice of organizing a database so each piece of information is stored exactly once. Instead of writing a customer's address on every order, you store the address in a "customers" table and refer to it from each order. This prevents the problem of having the same information recorded differently in different places.

**Level 2 — How to use it (junior developer):**
Check your schema:

- **1NF:** Does every column contain a single value? (No arrays, no comma-separated lists in a column.)
- **2NF:** If you have a composite primary key, does every non-key column depend on ALL key columns?
- **3NF:** Does every non-key column depend ONLY on the primary key? (Not on another non-key column.)
  If violations exist: extract the dependent columns into a new table with their own primary key, and replace them with a foreign key reference.

**Level 3 — How it works (mid-level engineer):**
Formal definition: A relation R is in 3NF if for every functional dependency X → A in R, either X is a superkey, or A is a prime attribute (part of some candidate key). The practical test: start with a list of all functional dependencies (e.g., `customer_id → customer_name`, `product_id → product_price`). If any FD has a left-hand side that is not the full PK, that's a normalization violation. Decompose into tables where each table's PK is the LHS of its FDs. Use BCNF when there are overlapping candidate keys causing anomalies not caught by 3NF. In practice: follow the principle "every non-key attribute should be a fact about the key, the whole key, and nothing but the key" (Codd's mantra).

**Level 4 — Why it was designed this way (senior/staff):**
Normalization theory was developed by Edgar F. Codd (1970–1972) as a formalization of relational database design. The normal forms are progressively stronger constraints on functional dependencies — each form eliminates a class of update anomalies. The theory is mathematically provable: a schema in BCNF cannot have update anomalies caused by redundancy. However, normalization has a well-known limitation: it doesn't address all anomalies — 4NF addresses multi-valued dependencies, 5NF addresses join dependencies. In practice, most production schemas stop at 3NF/BCNF because 4NF/5NF violations are rare and their fixes introduce complex join structures. The ongoing tension: OLTP databases benefit from normalization (write performance, integrity); OLAP databases often deliberately denormalize (star schema, wide tables) to avoid JOIN cost at query time. This is why data warehouses (Snowflake, BigQuery) use denormalized star/snowflake schemas while OLTP databases (PostgreSQL, MySQL) use normalized schemas.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ NORMALIZATION: VIOLATION EXAMPLES                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 1NF VIOLATION:                                       │
│ orders: order_id, products="101,102,103"  ← not atomic│
│ Fix: order_items(order_id, product_id)               │
│                                                      │
│ 2NF VIOLATION (composite PK):                        │
│ order_items: (order_id, product_id), product_name   │
│   product_name depends only on product_id, not both  │
│ Fix: products(product_id, product_name)              │
│      order_items(order_id, product_id FK, quantity)  │
│                                                      │
│ 3NF VIOLATION (transitive dependency):               │
│ employees: emp_id, dept_id, dept_location            │
│   dept_location → dept_id → emp_id (transitive)     │
│ Fix: departments(dept_id, dept_name, dept_location)  │
│      employees(emp_id, dept_id FK, salary)           │
│                                                      │
│ RESULT: 3NF SCHEMA                                   │
│ • Update customer → 1 row, not N rows                │
│ • Update product price → 1 row                       │
│ • Delete order → no customer data lost               │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Identify entities and facts
→ List functional dependencies
→ [NORMALIZATION ← YOU ARE HERE: decompose to 3NF]
→ Create separate tables for each entity
→ Primary key per table; foreign keys for relationships
→ Result: no redundancy, no update anomalies
→ Queries JOIN tables as needed
```

**FAILURE PATH:**

```
Denormalized schema in production (customer address in orders)
→ Customer address change requires UPDATE on all orders
→ Partial update (application bug) → some rows have old address
→ Data inconsistency: same customer has two different cities
→ Reports and analytics produce wrong results
→ Fix requires schema migration and data deduplication
```

**WHAT CHANGES AT SCALE:**
At scale, normalized schemas in OLTP databases perform well for write-heavy workloads — each write touches fewer bytes, fewer indexes. But read-heavy OLAP queries joining 10+ normalized tables become slow. Solution: keep the OLTP source of truth normalized; create a separate denormalized data warehouse (star schema via ETL/CDC) for analytical queries. This "CQRS at the schema level" pattern lets you have both: write correctness (normalized OLTP) and read performance (denormalized warehouse).

---

### ⚖️ Comparison Table

| Normal Form | What It Eliminates                  | Test                            | When Violated                                  |
| ----------- | ----------------------------------- | ------------------------------- | ---------------------------------------------- |
| **1NF**     | Non-atomic values, repeating groups | All columns single-valued       | Arrays, CSV in column, repeating column groups |
| **2NF**     | Partial key dependency              | All non-key depend on whole PK  | Composite PK with non-key depending on part    |
| **3NF**     | Transitive dependency               | Non-key depend only on PK       | Non-key A → non-key B → PK                     |
| **BCNF**    | All determinant anomalies           | Every determinant is a superkey | Overlapping candidate keys (rare)              |

How to choose: Target 3NF for OLTP production schemas. BCNF when schema has multiple overlapping candidate keys. Accept denormalization deliberately for read-heavy OLAP access patterns with clear documentation.

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                  |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Normalization always improves performance | Normalization improves write performance and integrity; it can reduce read performance (requires JOINs). OLAP workloads often perform better with denormalization        |
| A normalized schema has no redundancy     | Normalization eliminates update-anomaly-causing redundancy; derived data (counts, sums) must still be stored separately or computed at query time — both have trade-offs |
| 5NF is always the goal                    | In practice, 3NF/BCNF is sufficient for almost all OLTP schemas; 4NF/5NF fixes theoretical multi-valued dependency anomalies that rarely occur in real-world data models |
| Normalization is only about disk space    | Normalization's primary goal is data integrity — eliminating update, insert, and delete anomalies. Disk space reduction is a byproduct, not the objective                |

---

### 🚨 Failure Modes & Diagnosis

**1. Update Anomaly from Denormalized Schema**

**Symptom:** Customer's address, product price, or other entity attribute appears in multiple rows with different values; data inconsistency in reports.

**Root Cause:** The schema stores entity attributes (customer.address, product.price) in rows of a related table (orders, order_items) instead of in a dedicated entity table referenced by foreign key.

**Diagnostic:**

```sql
-- Find customer address inconsistency
SELECT customer_id,
       COUNT(DISTINCT shipping_address) AS address_versions
FROM orders
GROUP BY customer_id
HAVING COUNT(DISTINCT shipping_address) > 1;
-- Any result here = update anomaly has occurred

-- Find product price inconsistency within same product
SELECT product_id,
       COUNT(DISTINCT unit_price) AS price_versions,
       MIN(unit_price) AS min_price,
       MAX(unit_price) AS max_price
FROM order_items
GROUP BY product_id
HAVING COUNT(DISTINCT unit_price) > 1;
```

**Fix:** Schema migration: create `customers(customer_id, address)` and `products(product_id, current_price)` tables. Migrate data. Add foreign keys. Data cleansing: choose authoritative value (most recent, most common) for existing inconsistencies.

**Prevention:** Enforce normalization at schema design review. Foreign key constraints prevent orphaned references but don't enforce normalization. Peer review schema changes for normalization violations.

---

**2. Insert Anomaly — Cannot Add Entity Without Related Data**

**Symptom:** Cannot create a new product in the database until an order exists for it (because product data is only stored in `order_items`).

**Root Cause:** Entity attributes stored in a relationship table rather than a dedicated entity table.

**Diagnostic:**

```sql
-- Check if product information can exist independently
-- If the only place product_name appears is order_items:
SELECT DISTINCT product_id, product_name FROM order_items;
-- If there's no separate "products" table → insert anomaly
\dt  -- list all tables; look for missing entity tables
```

**Fix:** Create entity tables (`products`, `customers`, `categories`) to give entities an independent existence. Populate from existing relationship table data.

**Prevention:** Schema design rule: every real-world entity (product, customer, employee) should have its own table. Relationship tables (orders, enrollments) connect entities via foreign keys.

---

**3. Query Performance Degraded by Over-Normalization**

**Symptom:** A reporting query joins 8 tables and takes 30 seconds; denormalizing some data would allow a 2-table query taking 0.5 seconds.

**Root Cause:** Strict normalization is correct for OLTP but can be suboptimal for analytical queries that aggregate across many entities.

**Diagnostic:**

```sql
-- Identify query join depth
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.name, p.name, SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
JOIN categories cat ON p.category_id = cat.id
GROUP BY c.name, p.name;
-- If planning time > 100ms or execution > 5s for typical data → consider denormalization
```

**Fix:** Create a denormalized view or materialized view for the analytical query. Or create a separate analytics table (populated via CDC/ETL) with pre-joined, pre-aggregated data.

**Prevention:** Recognize at design time which queries are OLTP (normalized is correct) and which are OLAP (consider materialized views or a data warehouse). Don't apply OLTP normalization rules to analytical query paths.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Foreign Key / Referential Integrity` — the mechanism that enforces normalized relationships
- `Transaction` — normalization affects how transactions are structured

**Builds On This (learn these next):**

- `Denormalization` — deliberate reversal of normalization for read performance
- `Index Types (B-Tree, Hash, Composite, Covering)` — normalized schemas create natural index opportunities on foreign keys
- `Schema Evolution` — normalized schemas are easier to evolve without breaking constraints

**Alternatives / Comparisons:**

- `Denormalization` — the deliberate trade-off of redundancy for read performance
- `Materialized View` — a middle ground: normalized source, denormalized materialized result

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 1NF          │ Atomic columns, no repeating groups       │
│ 2NF          │ No partial key dependency (composite PKs) │
│ 3NF          │ No transitive dependency (A→B→PK)         │
│ BCNF         │ Every determinant is a superkey           │
├──────────────┼───────────────────────────────────────────┤
│ TARGET       │ 3NF/BCNF for OLTP production schemas      │
├──────────────┼───────────────────────────────────────────┤
│ ANOMALIES    │ Update: change in N places                │
│ IT PREVENTS  │ Insert: can't add entity alone            │
│              │ Delete: lose entity data with last row    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Write correctness + integrity vs          │
│              │ read performance (JOINs)                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Store each fact exactly once —           │
│              │  every other reference uses a FK"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Denormalization → Foreign Key → Schema    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A — Pattern Identification) You're reviewing a schema for a healthcare system: `appointments(appt_id, patient_id, patient_name, patient_dob, doctor_id, doctor_name, doctor_specialty, room_id, room_floor, appt_date, diagnosis)`. List all normalization violations (1NF through 3NF), name which normal form each violates, and write the normalized schema.

**Q2.** (TYPE C — Design Trade-off) A product team argues: "We should store the user's subscription tier (FREE/PRO/ENTERPRISE) in every row of the `usage_events` table to avoid a join on every analytics query." Analyze this proposal: what normalization violation does it introduce, what specific anomaly will occur as the product evolves subscription tiers, and propose a design that gives both correct normalization AND fast analytics queries without the join overhead.
