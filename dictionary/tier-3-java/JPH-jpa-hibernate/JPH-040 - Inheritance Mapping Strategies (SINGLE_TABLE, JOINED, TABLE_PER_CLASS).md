---
id: JPH-040
title: "Inheritance Mapping Strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-007, JPH-008, JPH-011, JPH-014, JPH-021, JPH-022
used_by: JPH-041, JPH-054, JPH-056, JPH-058
related: JPH-028, JPH-036, JPH-041
tags:
  - java
  - jpa
  - database
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 40
permalink: /jpa-hibernate/inheritance-mapping/
---

# JPH-040 - Inheritance Mapping Strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS)

⚡ **TL;DR** - JPA has three strategies for mapping an
inheritance hierarchy to relational tables:
`SINGLE_TABLE` (all subclasses in one table, nullable
columns for subtype fields - fastest queries, bad NULL
constraints), `JOINED` (parent + child tables joined
on primary key - normalized, slower queries via JOIN),
`TABLE_PER_CLASS` (each subclass is a complete table -
no JOINs for subtype queries, but polymorphic queries
require UNION ALL). Default recommendation: `JOINED`
for most cases; `SINGLE_TABLE` for performance-critical
hierarchies with few fields; avoid `TABLE_PER_CLASS`.

| #040            | Category: JPA & Hibernate                                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Entity, @Id, @Table/@Column, EntityManager, JPQL, @OneToMany, @ManyToOne                  |                 |
| **Used by:**    | @Embedded and @Embeddable, JPA at Scale, Spring Data JPA Architecture, Hibernate Internals |                 |
| **Related:**    | HQL, Criteria API, @Embedded                                                               |                 |

---

### 🔥 The Problem This Solves

**THE OBJECT-RELATIONAL IMPEDANCE FOR INHERITANCE:**
Java's object model supports inheritance naturally:

```java
abstract class Payment { Long id; BigDecimal amount; }
class CreditCardPayment extends Payment { String cardNumber; }
class BankTransferPayment extends Payment { String iban; }
```

Relational databases have no concept of inheritance.
The problem: how do you store these three classes in
a relational schema while supporting:

1. Polymorphic queries: `SELECT * FROM Payment` returns
   both credit card and bank transfer payments
2. Type-specific queries: `SELECT * FROM CreditCardPayment`
3. Referential integrity from other tables to `Payment`

Three strategies solve this differently with different
trade-offs on normalization, query performance, and
constraint enforcement.

---

### 📘 Textbook Definition

**JPA Inheritance Strategies** define how class hierarchies
are mapped to database tables:

**SINGLE_TABLE (default if `@Inheritance` omitted on parent):**
All classes in hierarchy stored in one table. A discriminator
column indicates the subtype. Subtype-specific columns
are nullable for rows of other subtypes.

**JOINED:**
Each class in the hierarchy has its own table. The subclass
table has a foreign key to the parent table's primary key.
Loading a subclass entity requires a JOIN between parent
and child tables.

**TABLE_PER_CLASS:**
Each concrete subclass has a complete table with all fields
(parent + own). Abstract parent class has no table.
Polymorphic queries require a UNION ALL across all
subclass tables.

**@MappedSuperclass (NOT an inheritance strategy):**
Parent class fields are mapped into each subclass table.
No polymorphic queries possible - parent class is not
an entity. Common for shared `@Id`, `@CreatedDate`,
`@Version` fields across unrelated entities.

---

### ⏱️ Understand It in 30 Seconds

**One line:** JPA inheritance maps class hierarchies to
SQL tables using one of three strategies - one table
(fast, nullable columns), joined tables (normalized,
JOINs), or one table per class (no joins for subtypes,
UNION ALL for polymorphic).

**One analogy:**

> A company directory has employees with different roles:
> Engineer, Manager, Intern. Three ways to store this:
>
> SINGLE_TABLE: one spreadsheet "Employees" with a
> "role" column. Engineers have blank "managedTeam" cells.
> Fast to query; lots of nulls.
>
> JOINED: "Employees" table (shared fields) + "Engineers"
> table (engineer-specific fields). Get an engineer:
> JOIN both tables. Normalized; slower.
>
> TABLE_PER_CLASS: separate "Engineers" spreadsheet,
> "Managers" spreadsheet, "Interns" spreadsheet, each
> with all fields. Fast per-type; "all employees" requires
> combining all sheets.

---

### 🔩 First Principles Explanation

**SINGLE_TABLE SCHEMA:**

```sql
CREATE TABLE payments (
  id         BIGINT PRIMARY KEY,
  dtype      VARCHAR(31) NOT NULL,  -- discriminator
  amount     DECIMAL(10,2) NOT NULL,
  -- CreditCardPayment columns (nullable for other types):
  card_number VARCHAR(16),
  card_expiry DATE,
  -- BankTransferPayment columns (nullable for cc payments):
  iban       VARCHAR(34),
  bic        VARCHAR(11)
);
-- Nullability cannot be enforced on subtype columns
-- card_number NULLABLE even for CreditCardPayment!
```

**JOINED SCHEMA:**

```sql
CREATE TABLE payments (      -- parent table
  id     BIGINT PRIMARY KEY,
  dtype  VARCHAR(31) NOT NULL,
  amount DECIMAL(10,2) NOT NULL
);
CREATE TABLE credit_card_payments (
  id          BIGINT PRIMARY KEY
              REFERENCES payments(id),  -- FK to parent
  card_number VARCHAR(16) NOT NULL,
  card_expiry DATE NOT NULL
);
CREATE TABLE bank_transfer_payments (
  id   BIGINT PRIMARY KEY
       REFERENCES payments(id),  -- FK to parent
  iban VARCHAR(34) NOT NULL,     -- can be NOT NULL!
  bic  VARCHAR(11)
);
```

**TABLE_PER_CLASS SCHEMA:**

```sql
CREATE TABLE credit_card_payments (
  id          BIGINT PRIMARY KEY,
  amount      DECIMAL(10,2) NOT NULL,  -- parent field repeated
  card_number VARCHAR(16) NOT NULL,
  card_expiry DATE NOT NULL
);
CREATE TABLE bank_transfer_payments (
  id     BIGINT PRIMARY KEY,
  amount DECIMAL(10,2) NOT NULL,  -- parent field repeated
  iban   VARCHAR(34) NOT NULL,
  bic    VARCHAR(11)
);
-- No payments table. FK from "orders.payment_id" to
-- which table? Both! Cannot use FK constraint.
```

---

### 🧪 Thought Experiment

**POLYMORPHIC QUERY SQL COMPARISON:**

```sql
-- SINGLE_TABLE: polymorphic query
SELECT * FROM payments;
-- 1 table scan; discriminator column filters if needed
-- Fast. All fields in one row.

-- JOINED: polymorphic query
SELECT p.id, p.amount, p.dtype,
       cc.card_number, cc.card_expiry,
       bt.iban, bt.bic
FROM payments p
LEFT JOIN credit_card_payments cc ON cc.id = p.id
LEFT JOIN bank_transfer_payments bt ON bt.id = p.id;
-- 2 LEFT JOINs for 2 subtypes; N LEFT JOINs for N subtypes
-- More expensive; index on FK usually helps

-- TABLE_PER_CLASS: polymorphic query
SELECT id, amount, NULL as card_number, NULL as iban
  FROM payments  -- doesn't exist!
UNION ALL
SELECT id, amount, card_number, NULL as iban
  FROM credit_card_payments
UNION ALL
SELECT id, amount, NULL as card_number, iban
  FROM bank_transfer_payments;
-- UNION ALL across all tables; N scans; no index optimization
-- Slowest for polymorphic; no FK constraints possible
```

---

### 🧠 Mental Model / Analogy

> Think of these as three filing systems for documents
> that share some properties but have type-specific fields:
>
> SINGLE_TABLE = one giant filing cabinet. Every document
> is in the same drawer. Fast to retrieve all documents.
> But every document has empty slots for fields that don't
> apply to its type. The more types, the more empty slots.
>
> JOINED = separate sections for each document type,
> plus a master index at the front (parent table). To get
> a document, look up the master index first (parent),
> then go to the right section (child join). Normalized;
> extra lookup each time.
>
> TABLE_PER_CLASS = completely separate filing cabinets.
> To find ALL documents: open every cabinet and combine.
> Fast if you only look in one cabinet. Slow for "all
> documents" view.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you have a class hierarchy in Java (parent + children)
and need to save them to a database, JPA needs to decide
how to structure the tables. The three strategies offer
different trade-offs between simplicity and database normalization.

**Level 2 - Which to use (junior developer):**
Default choice: `JOINED` - normalized schema, proper
NOT NULL constraints, good for most cases. Use `SINGLE_TABLE`
only if performance benchmarks show JOINs are too slow.
Avoid `TABLE_PER_CLASS` - it has no FK constraint support
and UNION ALL polymorphic queries.

**Level 3 - JPA configuration (mid-level engineer):**

```java
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
@DiscriminatorColumn(name = "dtype",
    discriminatorType = DiscriminatorType.STRING)
public abstract class Payment { ... }

@Entity
@DiscriminatorValue("CC")
public class CreditCardPayment extends Payment { ... }
```

**Level 4 - Performance implications (senior engineer):**
SINGLE_TABLE: single table scan for all queries; discriminator
column must be indexed for subtype queries; no JOINs
but sparse columns (NULLs). Better for deep hierarchies
where subtype queries dominate.
JOINED: parent+child JOIN on every load; `@OneToMany` on
parent entity that polymorphically includes children
triggers LEFT JOINs per subtype; performance degrades
with many subtypes (N LEFT JOINs). Better for wide
entities with distinct subtype fields requiring NOT NULL.

**Level 5 - @MappedSuperclass vs SINGLE_TABLE (staff engineer):**
`@MappedSuperclass` is NOT an inheritance strategy - the
parent class is not an entity, has no table, and cannot
be used in polymorphic queries or as a relationship target.
It's a column-sharing mechanism. `SINGLE_TABLE` with the
parent as an abstract entity DOES support polymorphic queries
(`SELECT p FROM Payment p`). When polymorphism is needed:
use `@Inheritance`. When only sharing columns with no
polymorphism: use `@MappedSuperclass`. Never use `@MappedSuperclass`
where you need to query "all payments".

---

### ⚙️ How It Works (Mechanism)

**SINGLE_TABLE IMPLEMENTATION:**

```java
@Entity
@Table(name = "payments")
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "dtype",
    discriminatorType = DiscriminatorType.STRING,
    length = 31)
public abstract class Payment {
    @Id @GeneratedValue
    private Long id;
    private BigDecimal amount;
    // discriminator field NOT mapped in Java
}

@Entity
@DiscriminatorValue("CREDIT_CARD")
public class CreditCardPayment extends Payment {
    private String cardNumber;  // nullable in DB!
    private LocalDate cardExpiry;
}

@Entity
@DiscriminatorValue("BANK_TRANSFER")
public class BankTransferPayment extends Payment {
    private String iban;   // nullable in DB!
    private String bic;
}
```

**JOINED IMPLEMENTATION:**

```java
@Entity
@Table(name = "payments")
@Inheritance(strategy = InheritanceType.JOINED)
@DiscriminatorColumn(name = "dtype")
public abstract class Payment {
    @Id @GeneratedValue
    private Long id;
    private BigDecimal amount;
}

@Entity
@Table(name = "credit_card_payments")
@PrimaryKeyJoinColumn(name = "payment_id")
@DiscriminatorValue("CREDIT_CARD")
public class CreditCardPayment extends Payment {
    @Column(nullable = false)  // CAN enforce NOT NULL!
    private String cardNumber;
    @Column(nullable = false)
    private LocalDate cardExpiry;
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CHOOSING A STRATEGY - DECISION TREE:**

```
┌─────────────────────────────────────────────────┐
│ Do you need polymorphic queries?                │
│ ("Find all Payments regardless of type")        │
└──────────────────────┬──────────────────────────┘
                       │ YES
                       ▼
┌─────────────────────────────────────────────────┐
│ Does any subtype have required (NOT NULL) fields?│
└──────────────────────┬──────────────────────────┘
          NO           │ YES
          │            ▼
          │    ┌───────────────────────────────────┐
          │    │ How many subtypes (now + future)? │
          │    └──────────────┬────────────────────┘
          │        ≤5 subtypes│  >5 subtypes
          │                   │    (likely)
          │                   ▼           ▼
          │              JOINED      JOINED still
          │             strategy     (consider sharding
          │           (normalized)   by subtype table)
          ▼
  SINGLE_TABLE
  (performance:
   no JOINs;
   accept NULLs)
```

---

### 💻 Code Example

**Example 1 - BAD: TABLE_PER_CLASS with FK from another entity:**

```java
// BAD: TABLE_PER_CLASS breaks FK constraints
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
public abstract class Payment { ... }

@Entity
public class Order {
    @ManyToOne
    @JoinColumn(name = "payment_id")
    private Payment payment;
    // payment_id column cannot have a DB FK constraint
    // - which table does it reference? Both!
    // Hibernate works; DB FK integrity: broken.
    // Orphaned payment IDs undetectable at DB level.
}

// GOOD: JOINED with proper FK
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Payment { ... }
// payments table has payment_id; FK from orders.payment_id
// -> payments.id works correctly
```

**Example 2 - SINGLE_TABLE performance query:**

```java
// SINGLE_TABLE: type-specific query is fast
List<CreditCardPayment> ccPayments = em
    .createQuery("FROM CreditCardPayment p",
                 CreditCardPayment.class)
    .getResultList();
// SQL: SELECT * FROM payments WHERE dtype='CREDIT_CARD'
// Index on (dtype) makes this fast

// JOINED: type-specific query requires JOIN
// SQL: SELECT p.*, cc.* FROM payments p
//      INNER JOIN credit_card_payments cc ON cc.id=p.id
// Index on pk makes this reasonably fast, but extra join
```

---

### ⚖️ Comparison Table

| Feature              | SINGLE_TABLE                     | JOINED                     | TABLE_PER_CLASS      |
| -------------------- | -------------------------------- | -------------------------- | -------------------- |
| Tables               | 1                                | 1 per class                | 1 per concrete class |
| Discriminator        | Required                         | Optional (can use FK type) | None                 |
| Polymorphic query    | Single scan                      | LEFT JOIN per subtype      | UNION ALL            |
| Subtype query        | WHERE dtype=?                    | INNER JOIN                 | Single scan          |
| NOT NULL constraints | Not on subtype fields            | Yes                        | Yes                  |
| FK references        | Yes (to parent table)            | Yes (to parent table)      | No (which table?)    |
| Recommended for      | Performance-critical, few fields | Most cases                 | Avoid                |

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "@MappedSuperclass and @Inheritance(SINGLE_TABLE) are interchangeable" | `@MappedSuperclass` = parent class is NOT an entity, no table, no polymorphic queries. `SINGLE_TABLE` parent = IS an entity, has a table (shared), supports polymorphic queries. Completely different.                    |
| "JOINED strategy doesn't need a discriminator column"                  | JOINED works without a discriminator column (Hibernate infers the type from which child table has a matching row). However, some JPA providers require it. Adding one is a best practice for clarity and query debugging. |
| "TABLE_PER_CLASS is good for query performance"                        | It is ONLY good for subtype-specific queries. Polymorphic queries (`FROM Payment`) require UNION ALL across all tables - no index optimization, full scans. This is typically worse than JOINED.                          |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Nullable Constraint Violations (SINGLE_TABLE)**

**Symptom:** A `CreditCardPayment` is saved without
`cardNumber`, but no exception is thrown - despite
`@Column(nullable=false)` on the field.
**Root Cause:** In `SINGLE_TABLE`, Hibernate ignores
`@Column(nullable=false)` on subtype fields because
the column IS nullable for other subtypes.
**Diagnosis:** Check the DDL: `card_number` column
will be `VARCHAR NULL` despite the `nullable=false` annotation.
**Fix:** Switch to `JOINED` strategy if NOT NULL constraints
are required. In `SINGLE_TABLE`, use `@Check` constraint:

```java
@Table(name = "payments", indexes = {...},
       uniqueConstraints = {...})
@org.hibernate.annotations.Check(
    constraints = "dtype!='CREDIT_CARD' OR " +
                  "(card_number IS NOT NULL)")
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-006 - @Entity]] - entity basics before inheritance
- [[JPH-021 - @OneToMany]] - parent entity relationships
  interact with inheritance strategy

**Builds On This (learn these next):**

- [[JPH-041 - @Embedded and @Embeddable]] - alternative
  to inheritance for value types

**Related:**

- [[JPH-028 - HQL]] - polymorphic queries work through
  JPQL/HQL using parent entity names
- [[JPH-036 - Criteria API]] - Criteria queries on
  parent type automatically include all subtypes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SINGLE_TABLE │ One table; discriminator col; fast queries│
│              │ nullable subtype cols; no NOT NULL enfmt  │
│ JOINED       │ Parent + child tables; FK join; normalized│
│              │ NOT NULL possible; N JOINs for N subtypes │
│ TABLE_PER_CL │ Complete tables per concrete class        │
│              │ UNION ALL for polymorphic; no FK possible │
├──────────────┼───────────────────────────────────────────┤
│ MAPPED_SUPER │ NOT inheritance; just shared columns;     │
│              │ no polymorphic queries; no entity table   │
├──────────────┼───────────────────────────────────────────┤
│ DEFAULT CHOICE│ JOINED for most; SINGLE_TABLE for perf  │
│ AVOID        │ TABLE_PER_CLASS                           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "3 strategies: 1 table (fast/nullable),  │
│              │ joined tables (normalized/FK), per-class  │
│              │ (avoid - UNION ALL, no FK). Use JOINED." │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `SINGLE_TABLE` = one table, discriminator column, fastest
   queries but cannot enforce NOT NULL on subtype fields
2. `JOINED` = parent + child tables joined on PK/FK,
   normalized, supports NOT NULL, recommended default
3. `TABLE_PER_CLASS` = avoid - polymorphic queries use
   UNION ALL and FK constraints are impossible

**Interview one-liner:** JPA has three inheritance strategies:
`SINGLE_TABLE` (one table with discriminator, fast but nullable
subtype columns), `JOINED` (parent+child tables with FK,
normalized, supports NOT NULL), and `TABLE_PER_CLASS`
(separate tables per concrete class, no FK constraints
possible, UNION ALL for polymorphic queries). `JOINED` is
the recommended default. `@MappedSuperclass` is not an
inheritance strategy - it's a column-sharing mechanism
with no polymorphic query support.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Object-Relational
Impedance Mismatch - the gap between object-oriented and
relational models - is fundamental and cannot be perfectly
solved. Inheritance is one instance of this gap. Each
inheritance mapping strategy trades some OO property
(type safety, encapsulation) for some relational property
(normalization, constraint enforcement, query efficiency).
There is no free lunch: the strategy that is best for
polymorphic queries is worst for constraint enforcement
(SINGLE_TABLE). The strategy best for constraints is
worst for polymorphic query performance (TABLE_PER_CLASS).
Choose the strategy that best matches your PRIMARY query
patterns. This same trade-off appears in: NoSQL vs SQL
(data model flexibility vs schema enforcement), graph DB
vs relational DB (relationship traversal vs set operations),
document store vs key-value (rich queries vs throughput).

**Where else this pattern appears:**

- **ActiveRecord (Rails)** - provides the same three
  strategies (STI for SINGLE_TABLE, class_table_inheritance
  gem for JOINED)
- **SQLAlchemy (Python)** - `__mapper_args__ = {'polymorphic_on': ...}`
  with same single-table vs joined trade-offs
- **TypeORM (Node.js/TypeScript)** - `@ChildEntity()` decorator
  maps to JOINED strategy; `@TableInheritance` for SINGLE_TABLE

---

### 💡 The Surprising Truth

The JPA specification says `SINGLE_TABLE` is the DEFAULT
inheritance strategy when `@Inheritance` is omitted.
Many developers inadvertently use SINGLE_TABLE without
realizing it, simply by extending one entity from another
without adding `@Inheritance(strategy = InheritanceType.JOINED)`.
This means large, complex entity hierarchies accumulate
in single tables with hundreds of nullable columns, causing
performance issues with wide table scans and losing all
database-level constraint enforcement. The "default" is
arguably the wrong choice for most production schemas.
Always explicitly declare `@Inheritance(strategy=...)` on
the parent entity - never rely on the default.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **IMPLEMENT** a `JOINED` inheritance hierarchy and
   explain the generated DDL (parent + child tables + FK)
2. **EXPLAIN** why `SINGLE_TABLE` cannot enforce NOT NULL
   on subtype fields, and provide a workaround
3. **WRITE** the SQL that Hibernate generates for a
   polymorphic query under each strategy
4. **DISTINGUISH** between `@Inheritance(SINGLE_TABLE)`,
   `@Inheritance(JOINED)`, and `@MappedSuperclass`
5. **CHOOSE** the correct strategy given: hierarchy depth,
   subtype field NOT NULL requirements, primary query patterns

---

### 🎯 Interview Deep-Dive

**Q1: What are the three JPA inheritance strategies and
what are their trade-offs?**
_Why they ask:_ Common design question; reveals ORM depth.
_Strong answer includes:_

- SINGLE_TABLE: one table, discriminator column, fastest
  queries (no JOINs), cannot enforce NOT NULL on subtype fields
- JOINED: parent+child tables with FK, normalized, NOT NULL
  possible, N JOINs for N subtypes on polymorphic queries
- TABLE_PER_CLASS: one complete table per concrete class,
  no FK constraints possible, UNION ALL for polymorphic
- Recommendation: JOINED by default; SINGLE_TABLE for
  performance-critical with accepted nullable columns; avoid TABLE_PER_CLASS

**Q2: What is the difference between @Inheritance(SINGLE_TABLE)
and @MappedSuperclass?**
_Why they ask:_ Tests precision - many candidates confuse these.
_Strong answer includes:_

- `@MappedSuperclass`: parent class is NOT an entity; has NO table;
  cannot be queried polymorphically; cannot be FK target
- `@Inheritance(SINGLE_TABLE)`: parent class IS an entity; HAS a table;
  SUPPORTS polymorphic queries (`FROM Payment`); CAN be FK target
- Use `@MappedSuperclass` for: shared fields (id, createdAt, version)
  across unrelated entities; no polymorphism needed
- Use `@Inheritance` for: actual class hierarchy where you need
  polymorphic queries or FK references to the parent type
