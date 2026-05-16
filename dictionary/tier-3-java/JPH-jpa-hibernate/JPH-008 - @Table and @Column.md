---
id: JPH-008
title: "@Table and @Column"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★☆☆
depends_on: JPH-006, JPH-007
used_by: JPH-011, JPH-014
related: JPH-033, JPH-034
tags:
  - java
  - database
  - jpa
  - foundational
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /jpa-hibernate/table-column-annotations/
---

# JPH-008 - @Table and @Column

⚡ **TL;DR** - `@Table` overrides the database table name
and schema for an entity; `@Column` overrides the column
name, type constraints, and DDL options for individual
fields.

| #008 | Category: JPA & Hibernate | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | @Entity, @Id and @GeneratedValue | |
| **Used by:** | EntityManager, JPQL (Java Persistence Query Language) | |
| **Related:** | Native SQL Queries, Stored Procedure Mapping | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
JPA's default naming convention maps `ProductOrder` to a
table named `ProductOrder` (or `product_order` depending on
the naming strategy). If the pre-existing database uses
`tbl_ord` as the table name and `cust_id` as a column name,
you have an impedance mismatch: either rename the Java class
(losing semantic meaning) or rename the database column
(breaking existing queries and reports).

**THE BREAKING POINT:**
Enterprise applications are rarely greenfield. More often,
Java code is added on top of an existing database schema
designed years earlier by a DBA who used naming conventions
incompatible with JPA defaults. Without `@Table` and
`@Column`, the developer is forced into one of three bad
choices: rename the database, rename the class, or write a
custom naming strategy affecting every entity.

**THE INVENTION MOMENT:**
`@Table` and `@Column` provide per-entity, per-field overrides
that decouple Java naming (following Java conventions) from
database naming (following DBA or legacy conventions). They
also extend into DDL generation: `@Column(nullable=false,
length=200)` generates `VARCHAR(200) NOT NULL` in the schema,
providing schema-as-code for the fields that need constraints.

---

### 📘 Textbook Definition

**`@Table`** is a Jakarta Persistence annotation applied to
an `@Entity` class that specifies the primary database table
for the entity. Its attributes are `name` (table name),
`schema` (database schema), `catalog` (database catalog),
and `uniqueConstraints` (DDL-level unique constraints across
multiple columns).

**`@Column`** is applied to a field or property of an entity
and specifies the column mapping for that field. Its key
attributes are `name` (column name), `nullable`, `unique`,
`length` (for `VARCHAR`), `precision` and `scale` (for
`DECIMAL`), `insertable`, `updatable`, and `columnDefinition`
(raw DDL for the column type).

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@Table` maps the class to a table;
`@Column` maps each field to a column - both let you
override JPA's defaults.

**One analogy:**
> `@Table` is the street address of a building - it tells
> the mail carrier (JPA provider) where to deliver
> persistence operations. `@Column` is the apartment number
> - it routes the right field to the right column within
> the table. Without them, JPA guesses the address and
> apartment from the class and field names.

**One insight:** `@Table` and `@Column` serve two purposes:
(1) mapping - connecting Java names to database names;
(2) DDL generation - defining constraints that become
`CREATE TABLE` DDL when `ddl-auto=create`. Many teams use
them only for (1) mapping while managing schema separately
via Flyway/Liquibase.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Without `@Table`, the table name defaults to the entity
   class name (or the naming strategy's transformation of it)
2. Without `@Column`, the column name defaults to the field
   name (or the naming strategy's transformation)
3. `@Column` constraints (`nullable`, `length`, `precision`)
   affect DDL generation when `ddl-auto=create/update` - they
   do NOT enforce constraints in Java code (that is Bean
   Validation's job with `@NotNull`, `@Size`)
4. `@Table(uniqueConstraints)` generates DDL unique
   constraints; `@Column(unique=true)` generates a
   single-column unique index
5. `insertable=false, updatable=false` on a `@Column` makes
   it read-only from JPA's perspective - the column appears
   in SELECT but not INSERT or UPDATE

**DERIVED DESIGN:**
Two naming resolution layers exist independently:
- **Physical Naming Strategy**: transforms logical names
  (class, field) to physical names (table, column) via
  camelCase-to-snake_case or similar rules
- **`@Table`/`@Column` annotations**: explicit overrides
  that take precedence over any naming strategy

This means `@Column(name="customer_id")` overrides the naming
strategy for that specific field; unnamed fields still go
through the strategy.

**THE TRADE-OFFS:**
**Gain:** Precise control over database naming, DDL constraint
generation, and read-only column mappings.
**Cost:** Annotations clutter entity classes with database
concerns; schema changes require recompiling Java code.
Teams using Flyway typically use `@Column` only for mapping
(name), not for constraints (nullable, length), letting the
migration scripts own the DDL.

---

### 🧪 Thought Experiment

**SETUP:**
You join a team that inherited a legacy Oracle schema.
The `customers` table has columns `CUST_ID`, `CUST_EMAIL`,
`CUST_LAST_NM`. Java convention would name these
`customerId`, `email`, `lastName`.

**WITHOUT @Column:**
JPA maps `customerId` to `customerid` (or with snake_case
strategy, `customer_id`). Neither matches `CUST_ID`. Every
`find()` and `persist()` fails with `unknown column` errors.

**WITH @Column:**

```java
@Entity
@Table(name = "customers", schema = "sales")
public class Customer {

    @Id
    @Column(name = "CUST_ID")
    private Long id;

    @Column(name = "CUST_EMAIL",
            nullable = false, length = 320)
    private String email;

    @Column(name = "CUST_LAST_NM", length = 100)
    private String lastName;
}
```

Now `SELECT CUST_ID, CUST_EMAIL, CUST_LAST_NM FROM sales.customers`
is generated correctly. Java code uses clean names (`email`,
`lastName`) while mapping to legacy column names.

**THE INSIGHT:** `@Table`/`@Column` are the adapter layer
between JPA naming conventions and database reality. They let
Java code stay clean while mapping to any existing schema.

---

### 🧠 Mental Model / Analogy

> `@Table` is a language translator at an international
> conference. The Java speaker says "ProductOrder" (English);
> the DBA speaks "tbl_prd_ord" (legacy). `@Table` translates
> silently so both sides communicate without changing their
> natural language.
>
> `@Column` is a field-by-field translator that handles each
> attribute separately - "firstName" in Java becomes
> "FIRST_NM" in Oracle.

- "Language translator" - the mapping annotation
- "English speaker" - Java code using Java naming conventions
- "Legacy speaker" - database with DBA-defined names
- "Translation" - the `name=` attribute in the annotation
- "Neither changing their language" - no Java rename, no DB rename

Where this analogy breaks down: translators interpret meaning;
`@Table`/`@Column` are mechanical mappings - they do not
validate that the column types match the Java types. A
`String` field mapped to an `INT` column will fail at runtime.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@Table` renames the database table that an entity class
maps to. `@Column` renames the database column that a field
maps to, and can also set constraints like "this column
cannot be null."

**Level 2 - How to use it (junior developer):**
Add `@Table(name = "products")` above the class if the table
name differs from the class name. Add `@Column(name = "prod_name",
nullable = false, length = 200)` above a field to specify its
column name and DDL constraints. If the default mapping is
correct, omit both annotations.

**Level 3 - How it works (mid-level engineer):**
JPA resolves column names in two passes: first apply the
physical naming strategy (e.g. Spring Boot's
`SpringPhysicalNamingStrategy` converts camelCase to
snake_case), then check for `@Column(name=...)` overrides.
The explicit annotation always wins. During DDL generation
(`ddl-auto=create`), `@Column` attributes (`nullable`,
`length`, `precision`) become DDL constraint clauses.

**Level 4 - Why it was designed this way (senior/staff):**
JPA separates logical naming (what the entity/attribute is
called in Java) from physical naming (what the table/column
is called in the database). The `@Table`/`@Column` annotations
are the physical naming layer. The naming strategy is a
configuration-level default for the physical layer.
This two-layer design allows a team to establish a naming
convention via strategy (zero annotations needed for new
code following the convention) while still supporting
legacy column names via explicit overrides.

**Level 5 - Mastery (distinguished engineer):**
`@Column(insertable=false, updatable=false)` is the correct
pattern for formula columns, computed columns, or columns
managed by a database trigger. Without it, Hibernate includes
the column in INSERT/UPDATE SQL and the trigger or generated
column constraint fails. Combined with `@Formula` or
`@ColumnDefault`, it provides precise control over what
Hibernate reads vs. writes to each column.
`@Table(uniqueConstraints)` generates multi-column unique
indexes that cannot be expressed with `@Column(unique=true)`;
it is the only way to declare compound uniqueness constraints
via JPA annotations.

**Expert Thinking Cues:**
- Ask: "Is this `@Column` annotation for mapping (name) or
  for DDL (nullable/length)?" - teams using Flyway should
  strip DDL attributes and let migration scripts control schema
- Watch: `columnDefinition` is database-specific raw DDL;
  using it couples the entity class to a specific database
  vendor, losing portability
- Know: `@Column` constraints do NOT validate at the Java
  layer; `@NotNull`/`@Size` from Bean Validation (Jakarta
  Validation) is needed for application-layer validation

---

### ⚙️ How It Works (Mechanism)

**Name Resolution Order:**

```
┌───────────────────────────────────────────────┐
│          COLUMN NAME RESOLUTION ORDER          │
├───────────────────────────────────────────────┤
│ 1. @Column(name="explicit_name")              │
│    Highest priority - always used if present  │
│                                               │
│ 2. @AttributeOverride (inheritance/embedded)  │
│    Overrides mappings from superclass         │
│                                               │
│ 3. Physical Naming Strategy                   │
│    Default: Spring's camelCase -> snake_case  │
│    e.g. firstName -> first_name               │
│                                               │
│ 4. Implicit Naming Strategy                   │
│    Fallback: uses field name unchanged        │
└───────────────────────────────────────────────┘
```

**DDL Generation from @Column:**

```
@Column(nullable = false, length = 200)
private String email;

Generated DDL:
  email VARCHAR(200) NOT NULL

@Column(precision = 10, scale = 2)
private BigDecimal price;

Generated DDL:
  price DECIMAL(10,2)

@Column(columnDefinition =
    "TEXT DEFAULT 'unknown'")
private String notes;

Generated DDL (PostgreSQL):
  notes TEXT DEFAULT 'unknown'
```

**Read-Only Column Pattern:**

```
@Column(name = "created_at",
        insertable = false,
        updatable = false)
private LocalDateTime createdAt;
// Only appears in SELECT; database trigger
// or DEFAULT sets value on INSERT
```

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
`@Table` and `@Column` are compile-time metadata; they are
read once at `EntityManagerFactory` creation and immutable
afterwards. They are inherently thread-safe.

---

### 🔄 The Complete Picture - End-to-End Flow

**QUERY GENERATION FLOW:**

```
em.find(Product.class, 1L)
    |
    v
[ Hibernate metadata: entity=Product ]
    |  @Table(name="products", schema="inventory")
    v
[ Table: inventory.products ]
    |  @Column(name="prod_name") on field name
    v
[ Column: prod_name ]
    |  @Column(name="unit_price") on field price
    v
[ Generated SQL: ]
    SELECT p.id, p.prod_name, p.unit_price
    FROM inventory.products p
    WHERE p.id = ?
```

**FAILURE PATH:**
If `@Table(name="non_existent_table")` is used, queries fail
with `table or view does not exist` at runtime, not compile
time. If `@Column(name="wrong_col")` references a non-existent
column, the error is `Unknown column 'wrong_col'` on first
query execution. Neither error is caught until the code runs.

**WHAT CHANGES AT SCALE:**
`@Column` constraints (`nullable`, `unique`, `length`) only
affect DDL generation - not query performance. For performance
tuning at scale, database-side indexes defined in migration
scripts (Flyway) matter more than `@Column` annotations.
`@Table(indexes = {...})` generates DDL index creation but
is rarely used in teams with Flyway/Liquibase.

---

### 💻 Code Example

**Example 1 - BAD: ignoring naming mismatches:**

```java
// BAD: table is "tbl_products", field is "PROD_NM"
// Default JPA naming maps to "product" and "prod_nm"
@Entity
public class Product {
    @Id
    private Long id;
    // Maps to column "prod_nm" NOT "PROD_NM" (case varies by DB)
    // If table is "tbl_products" this entity never works
    private String prodNm;
}
```

**Example 2 - GOOD: explicit table and column mapping:**

```java
// GOOD: explicit names match legacy schema
@Entity
@Table(name = "tbl_products",
       schema = "catalog")
public class Product {

    @Id
    @Column(name = "PROD_ID")
    private Long id;

    @Column(name = "PROD_NM",
            nullable = false,
            length = 200)
    private String name;  // Java: clean name

    @Column(name = "UNIT_PRICE",
            precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "CREATED_TS",
            insertable = false,
            updatable = false)
    private LocalDateTime createdAt;
    // Database DEFAULT CURRENT_TIMESTAMP
}
```

**Example 3 - Multi-column unique constraint:**

```java
@Entity
@Table(
    name = "order_items",
    uniqueConstraints = {
        @UniqueConstraint(
            name = "uq_order_product",
            columnNames = {"order_id",
                           "product_id"})
    }
)
public class OrderItem {
    @Id
    @GeneratedValue(
        strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "order_id",
            nullable = false)
    private Long orderId;

    @Column(name = "product_id",
            nullable = false)
    private Long productId;
    // (order_id, product_id) pair is unique
}
```

**Example 4 - insertable/updatable=false for DB-managed cols:**

```java
@Entity
public class AuditedEntity {

    @Id
    private Long id;

    // Set once by DB DEFAULT, never updated
    @Column(name = "created_at",
            insertable = false,
            updatable = false)
    private LocalDateTime createdAt;

    // Updated by DB trigger, Hibernate reads only
    @Column(name = "updated_at",
            insertable = false,
            updatable = false)
    private LocalDateTime updatedAt;
}
```

---

### ⚖️ Comparison Table

| Attribute | Affects | DDL Generated | Runtime Enforcement |
|---|---|---|---|
| `@Column(name)` | Mapping | No | Yes (column name in SQL) |
| `@Column(nullable=false)` | DDL | `NOT NULL` | No (DB enforces) |
| `@Column(length=200)` | DDL | `VARCHAR(200)` | No |
| `@Column(unique=true)` | DDL | `UNIQUE INDEX` | No (DB enforces) |
| `@Column(insertable=false)` | Mapping | No | Yes (excluded from INSERT) |
| `@Table(uniqueConstraints)` | DDL | `UNIQUE (col1, col2)` | No (DB enforces) |
| `@Column(columnDefinition)` | DDL | Raw SQL fragment | No |

**Key distinction:** `@Column` constraints define the desired
schema state (for DDL generation); Bean Validation annotations
(`@NotNull`, `@Size`) enforce the same constraints in the
Java application layer. Both should be used in tandem.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`@Column(nullable=false)` throws an exception when you set null" | It only generates `NOT NULL` in DDL. Setting null on the Java field succeeds until the INSERT hits the database, which then throws a constraint violation. Use `@NotNull` (Bean Validation) for Java-layer validation. |
| "You need `@Column` on every field" | Without `@Column`, Hibernate maps the field to a column named after the field (via naming strategy). Only add `@Column` when you need to override the default - especially the name. |
| "`@Table` is only useful for renaming tables" | `@Table` also sets `schema`, `catalog`, `uniqueConstraints`, and `indexes`. For multi-schema databases, `schema` is essential for correctness. |
| "`@Column(columnDefinition)` is a good idea for cross-database apps" | `columnDefinition` takes raw SQL fragment specific to one database vendor (e.g. `"JSONB"` for PostgreSQL). Using it couples your entity to that vendor, breaking portability to other databases. |
| "Changing `@Column(name)` is safe to do in production" | Renaming the mapped column name changes every generated SQL query immediately. If the database column name has not been renamed (via migration), all queries break immediately after deployment. Always coordinate with a Flyway migration. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Wrong Column Name Mapping (Runtime)**

**Symptom:** `org.hibernate.HibernateException: Unknown column
'prod_name' in 'field list'` on application startup or first
query (depending on `ddl-auto`).
**Root Cause:** JPA applied the naming strategy (e.g.
`product_name`) but the database column is named `PROD_NM`.
Missing `@Column(name="PROD_NM")`.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Inspect generated SELECT/INSERT for wrong column names
# Compare against database schema with:
# DESCRIBE tbl_products;  -- MySQL
# \d tbl_products          -- PostgreSQL
```

**Fix:**

```java
// Add @Column with the correct database column name
@Column(name = "PROD_NM")
private String name;
```

**Prevention:** When mapping to legacy schemas, list all
column names explicitly with `@Column(name=...)` rather
than relying on naming conventions.

---

**Failure Mode 2: DDL Constraint Not Enforced in Java**

**Symptom:** Application successfully sets a `null` email
on a `Customer` entity; the insert succeeds in tests (using
an H2 in-memory database without strict constraint enforcement)
but fails in production (PostgreSQL with `NOT NULL`).
**Root Cause:** `@Column(nullable=false)` was used without
`@NotNull` Bean Validation; H2 in schema-creation mode
may not enforce `NOT NULL` the same way PostgreSQL does.
**Diagnostic:**

```bash
# Run integration test against real PostgreSQL
# or enable full schema validation:
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=true
# Validate the NOT NULL constraint in the actual schema
```

**Fix:**

```java
// Add Bean Validation for Java-layer enforcement
@Column(nullable = false, length = 320)
@NotNull  // Validates before hitting DB
@Email    // Additional format check
private String email;
```

**Prevention:** Use both `@Column(nullable=false)` (for DDL)
and `@NotNull` (for Java validation) together. Configure
integration tests to run against the same database vendor
as production.

---

**Failure Mode 3: Schema Change Breaking Existing Queries**

**Symptom:** After changing `@Column(name="prod_name")` to
`@Column(name="product_name")`, all SELECT/INSERT/UPDATE
queries fail with `Unknown column 'product_name'` - the
database column was not renamed.
**Root Cause:** Renaming the `@Column(name=...)` attribute
changes the SQL immediately. The database column still has
the old name.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Look for SELECT ... product_name ... 
# then verify DB column is still prod_name
```

**Fix:** Create a Flyway migration script to rename the
database column before (or simultaneously with) the
`@Column` change:

```sql
ALTER TABLE tbl_products
  RENAME COLUMN prod_name TO product_name;
```

**Prevention:** Treat `@Column(name=...)` changes as schema
changes requiring a coordinated migration script. Never
change column name mappings without a corresponding database
migration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-006 - @Entity]] - `@Table` annotates `@Entity`
  classes; cannot exist without `@Entity`
- [[JPH-007 - @Id and @GeneratedValue]] - `@Column` often
  used alongside `@Id` to specify the primary key column name

**Builds On This (learn these next):**
- [[JPH-011 - EntityManager]] - EntityManager generates SQL
  using the table and column names resolved by these annotations
- [[JPH-014 - JPQL (Java Persistence Query Language)]] -
  JPQL uses entity names and field names (not `@Column` names);
  understanding the distinction prevents confusion

**Alternatives / Comparisons:**
- [[JPH-033 - Native SQL Queries]] - when full control over
  SQL is needed, bypassing `@Table`/`@Column` mappings
- [[JPH-034 - Stored Procedure Mapping]] - stored procedures
  bypass column mapping entirely

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ @Table: maps entity to named DB table     │
│              │ @Column: maps field to named DB column    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Decouples Java naming from legacy DB      │
│ SOLVES       │ naming; provides DDL constraint generation │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ @Column constraints (nullable, length)    │
│              │ generate DDL - NOT Java validation.       │
│              │ Use @NotNull for Java validation           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Table/column name differs from Java name; │
│              │ need DDL constraints or multi-col unique  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Default naming matches DB; Flyway controls│
│              │ schema (skip nullable/length in @Column)  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ columnDefinition with DB-specific SQL;    │
│              │ changing @Column(name) without migration  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Precise mapping vs. clutter in entity     │
│              │ classes; annotations couple code to schema│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Table = building address; @Column =     │
│              │ apartment number inside the building"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ EntityManager -> JPQL -> Native SQL       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `@Column(nullable=false, length=200)` generates DDL
   constraints but does NOT validate in Java - add
   `@NotNull`/`@Size` for Java-layer enforcement
2. `@Column(insertable=false, updatable=false)` makes a
   field read-only - use for DB-managed columns (triggers,
   defaults, generated columns)
3. Changing `@Column(name=...)` is a schema change - always
   coordinate with a database migration script (Flyway)

**Interview one-liner:** `@Table` overrides the entity's
database table name and schema; `@Column` overrides a field's
column name and DDL constraints. The key nuance: `@Column`
constraints (nullable, length) only affect DDL generation -
they do not validate at the Java application layer.
Use Bean Validation annotations (`@NotNull`, `@Size`) for
application-layer enforcement.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Separate the logical
model (what things are called in the application) from the
physical model (what things are called in the storage layer).
Explicit mapping annotations are the translation layer
between the two. This principle applies in any system that
bridges two naming conventions: microservices with different
field names for the same concept, event schemas mapped to
domain objects, or external API models mapped to internal
representations.

**Where else this pattern appears:**
- **Jackson `@JsonProperty`** - same pattern: decouples Java
  field names from JSON key names; `@JsonProperty("user_id")`
  maps a Java `userId` field to `"user_id"` in JSON
- **Spring MVC `@RequestParam("first_name")`** - maps HTTP
  query parameters to Java method parameters with different
  names
- **MyBatis `@Result(column="cust_id", property="customerId")`** -
  explicit column-to-property mapping, identical concept

**Industry applications:**
- Legacy banking systems: Java microservices mapping to
  COBOL-era Oracle schemas with 8-character column name
  limits require extensive `@Column(name=...)` usage
- Multi-tenant SaaS: `@Table(schema = ...)` dynamically
  set via a Hibernate schema resolver, allowing one entity
  class to map to different schemas per tenant

---

### 💡 The Surprising Truth

`@Column(name)` in JPQL queries is invisible. JPQL
(`SELECT p.name FROM Product p`) uses the Java field name
(`name`), not the database column name (`PROD_NM`).
The JPA provider translates the JPQL field name to the
database column name using the `@Column(name)` mapping.
This means changing `@Column(name="PROD_NM")` to
`@Column(name="product_name")` has zero impact on JPQL
queries in Java code - but changes every generated SQL
statement. Developers who mix Native SQL queries with JPQL
must use the database column name in native SQL and the
Java field name in JPQL, which causes constant confusion
when the two differ.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the difference between `@Column(nullable=false)`
   (DDL constraint) and `@NotNull` (Bean Validation) and
   state exactly when each is enforced
2. **DEBUG** a production `NOT NULL constraint` violation that
   passes in unit tests by identifying the missing `@NotNull`
   Bean Validation annotation
3. **DECIDE** when to use `@Column(insertable=false, updatable=false)`,
   naming the three scenarios where it is appropriate:
   DB-generated columns, audit timestamps managed by triggers,
   and columns shared between two entity mappings
4. **BUILD** an entity class that maps to a legacy schema
   with 8-character column name conventions using explicit
   `@Column(name=...)` annotations while preserving clean
   Java field names
5. **EXTEND** `@Table(uniqueConstraints)` to enforce a
   compound unique constraint on (tenantId, externalId)
   and explain why `@Column(unique=true)` alone cannot
   express this constraint

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE C - Design Trade-off):** Your team uses Flyway
to manage all database schema changes. Should you include
`@Column(nullable=false, length=200)` DDL attributes in your
entities, or omit them and rely on Flyway migrations only?
What are the arguments for and against each approach?
*Hint: Consider schema as documentation, DRY principle
(constraints in two places), and what happens when the
Flyway migration and the `@Column` annotation disagree.*

**Q2 (TYPE D - Root Cause Trace):** A JPQL query
`SELECT c.email FROM Customer c WHERE c.id = :id` works
correctly. After renaming the Java field from `email` to
`emailAddress` and adding `@Column(name="email")`, the JPQL
query breaks. Trace exactly what happened and what the
developer needs to fix.
*Hint: JPQL uses Java field names; after renaming the field,
all JPQL queries using `c.email` must be updated to `c.emailAddress`.*

**Q3 (TYPE G - Hands-On):** Create an entity class that maps
to a table with the following constraints: (1) a compound
unique constraint on `(tenant_id, external_id)`, (2) a
`created_at` column that is managed by a database `DEFAULT
CURRENT_TIMESTAMP` and should never be included in INSERT
or UPDATE, (3) a `notes` field that maps to a PostgreSQL
`TEXT` column. Write the complete entity with all required
annotations and explain each annotation choice.

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between `@Column(nullable=false)`
and `@NotNull`? Which one would you use and when?**
*Why they ask:* Tests the distinction between persistence
constraints and application validation - a very common
interview question for Spring/JPA roles.
*Strong answer includes:*
- `@Column(nullable=false)`: DDL constraint, generates
  `NOT NULL` in `CREATE TABLE`, enforced by the database
  at INSERT/UPDATE time; no Java exception until DB is hit
- `@NotNull`: Bean Validation, enforced by the Java
  application before the SQL is executed; throws
  `ConstraintViolationException` in Java code
- Use both: `@Column(nullable=false)` ensures the schema
  is correct; `@NotNull` validates before hitting the DB
  and provides clear error messages in the application layer

**Q2: When would you use `@Column(insertable=false,
updatable=false)` and what problem does it solve?**
*Why they ask:* Tests knowledge of edge-case mapping needs -
database-managed columns, triggers, and shared foreign keys.
*Strong answer includes:*
- Used for columns managed by the database: `DEFAULT
  CURRENT_TIMESTAMP`, `GENERATED ALWAYS AS (...)`, or
  values set by INSERT triggers
- Also used when a join column is mapped twice (as a
  `@Column` and as a `@ManyToOne` join column) - one
  mapping must be `insertable=false, updatable=false`
- Without it, Hibernate includes the column in INSERT/UPDATE,
  conflicting with the database-managed default or generated value

**Q3: If you use JPQL and also Native SQL on the same entity,
what naming do you use for column references in each?**
*Why they ask:* Tests understanding of the fundamental
JPQL-vs-SQL distinction that confuses many developers.
*Strong answer includes:*
- JPQL: uses Java field names (e.g. `c.email`, `p.name`) -
  the JPA provider translates to database column names
- Native SQL: uses database column names (e.g. `c.CUST_EMAIL`,
  `p.PROD_NM`) - no JPA translation happens
- When `@Column(name="CUST_EMAIL")` is used, JPQL query
  uses `c.email` (Java field name) while a native SQL
  query must use `c.CUST_EMAIL` - using the wrong name
  in either context causes a silent mismatch or runtime error