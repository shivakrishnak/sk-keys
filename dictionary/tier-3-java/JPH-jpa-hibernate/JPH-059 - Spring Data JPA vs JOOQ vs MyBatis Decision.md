---
id: JPH-059
title: Spring Data JPA vs JOOQ vs MyBatis Decision
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-001, JPH-014, JPH-016, JPH-023, JPH-025, JPH-050, JPH-053, JPH-055
used_by: []
related: JPH-050, JPH-053, JPH-055, JPH-054
tags:
  - java
  - jpa
  - architecture
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /jpa-hibernate/spring-data-jpa-vs-jooq-vs-mybatis-decision/
---

# JPH-059 - Spring Data JPA vs JOOQ vs MyBatis Decision

⚡ **TL;DR** - Framework choice: Spring Data JPA for CRUD-heavy
domain-model code (standard entities, associations, lifecycle);
JOOQ for complex SQL, type-safe query building, advanced DB
features (window functions, CTEs, lateral joins); MyBatis when
your team has SQL expertise and needs full SQL control with
lightweight mapping. In practice: Spring Data JPA is the default
for Spring Boot microservices. JOOQ is the go-to upgrade when
JPA's query model becomes a liability (reporting, analytics, bulk ops).
MyBatis is used when JOOQ's code generation is impractical.
Mixing is valid: Spring Data JPA for entities, JOOQ for reports.

| #059 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JPA Overview, JPQL, Criteria API, Native Queries, Named Queries, Hibernate vs MyBatis vs JOOQ, QueryDSL, ORM Selection Framework | |
| **Used by:** | - | |
| **Related:** | Hibernate vs MyBatis vs JOOQ, QueryDSL, ORM Selection Framework, JPA at Scale | |

---

### 🔥 The Problem This Solves

**WHY THIS DECISION MATTERS:**

```
Wrong tool choice symptoms:

Spring Data JPA used for everything:
  "Write me a report: top 10 products by revenue last
   quarter, with year-over-year % change, grouped by
   category, filtered by region."
  -> 50-line JPQL + multiple @NamedQueries + manual
     BigDecimal math in Java + multiple queries joined
     in application code
  -> Could be 8-line SQL with window functions + 1 JOOQ call
  -> N+1 loading of associations not needed for report
  -> ORM cognitive overhead for a pure SQL task

MyBatis used for everything:
  "Save this Order with 10 OrderItem children."
  -> Write INSERT for Order, write foreach INSERT for items
  -> Handle transaction manually
  -> Write UPDATE to detect changes
  -> 200 lines of XML mappers for what JPA does in 20 lines

JOOQ used for everything:
  "Implement CQRS with an aggregate root."
  -> JOOQ has no identity map, no lifecycle management
  -> Every "update" is manual SELECT + UPDATE
  -> No cascade, no dirty checking, no first-level cache
  -> JOOQ is not an ORM; using it as one is anti-pattern

Decision framework: match tool to query type, not "one ORM
to rule them all."
```

---

### 📘 Textbook Definition

**Spring Data JPA**: Spring abstraction layer over JPA
(Hibernate). Provides: repository interfaces, method-name
query derivation, `@Query` for JPQL/native, pagination,
auditing, specifications. Manages entity lifecycle.

**JOOQ (Java Object Oriented Querying)**: Type-safe SQL
builder library. Generates Java classes from DB schema
(code generation). Builds SQL programmatically using
fluent API. No entity lifecycle or identity map.
SQL-first approach.

**MyBatis**: SQL mapping framework. Write SQL in XML
or annotations; MyBatis handles result mapping to Java
objects. No ORM magic: no dirty checking, no lazy loading,
no entity lifecycle. Manual SQL = full SQL control.

| Axis | Spring Data JPA | JOOQ | MyBatis |
|---|---|---|---|
| Approach | ORM (object-first) | SQL DSL (SQL-first, typed) | SQL mapping (SQL-first, plain) |
| Query language | JPQL / Criteria API / native | Java fluent SQL API | Raw SQL in XML / annotations |
| Schema awareness | From `@Entity` annotations | Code-generated from DB schema | Manual result maps |
| Dirty checking | Yes (automatic) | No | No |
| Lazy loading | Yes (Hibernate proxies) | No | No |
| Associations | Mapped (`@ManyToOne`, etc.) | Manual joins | Manual joins |
| 2LC / 1LC | Yes | No | No (3rd party only) |
| Best at | CRUD, domain model, lifecycle | Complex SQL, reporting, bulk ops | Stored proc, full SQL control |
| Main cost | Complex queries become awkward | Code generation step needed | No ORM benefits; verbose for CRUD |

---

### ⏱️ Understand It in 30 Seconds

**One line:** Spring Data JPA = "manage my entities and generate SQL";
JOOQ = "I'll write the SQL but in type-safe Java";
MyBatis = "I'll write the SQL in XML/annotations, you map results."

**One analogy:**
> Spring Data JPA is like a hotel: everything is managed for you
> (room service, housekeeping = entity lifecycle). JOOQ is like
> a well-equipped Airbnb: you cook your own meals but the kitchen
> is professional grade (type-safe, schema-aware SQL builder).
> MyBatis is like camping: you bring your own tent and food (raw SQL),
> but you have full control over what you eat (exactly how the DB
> is queried). Most enterprises need the hotel for most things
> (CRUD entities) and rent the Airbnb occasionally (complex reports).
> Camping is for specialists with specific requirements.

---

### 🔩 First Principles Explanation

**WHAT EACH TOOL OPTIMIZES:**

```
Spring Data JPA optimizes for:
  - Entity lifecycle management (persist/merge/remove)
  - Association navigation (entity.getOrders())
  - Repository pattern (findByNameAndActive(name, true))
  - Pagination (Pageable)
  - Auditing (@CreatedBy, @LastModifiedDate)
  - Transaction-scoped identity map (1LC)
  Assumes: domain model with OO associations,
  standard CRUD + moderate query complexity

JOOQ optimizes for:
  - SQL expressiveness (window functions, CTEs, lateral joins)
  - Type safety (compile-time column/table name checks)
  - DB-specific features (PostgreSQL arrays, JSON operators)
  - Dynamic query building (add WHERE clauses at runtime safely)
  - Batch operations (INSERT ... VALUES (row1),(row2)...)
  - Reporting / analytics queries
  Assumes: SQL is the primary query language, queries are complex

MyBatis optimizes for:
  - Full SQL control (existing SQL investment)
  - Simple result mapping (pojo, Map<String,Object>)
  - Stored procedure / function calls
  - Teams with strong SQL/DBA background
  - Brownfield: existing SQL to migrate
  Assumes: developers write all SQL; ORM abstractions not desired
```

---

### 🧪 Thought Experiment

**THE REPORTING QUERY ACID TEST:**

```
Requirement:
  "Monthly active users per plan tier, with % change
   from previous month, ordered by tier."

Spring Data JPA solution:
  - No clean JPQL for LAG() window function
  - Must: write native SQL query OR do in Java (bad)
  - Native SQL loses type safety and portability

JOOQ solution:
  DSLContext dsl = ...;
  Result<?> result = dsl
    .select(
      USERS.PLAN_TIER,
      DSL.count().as("current_month"),
      DSL.lag(DSL.count())
         .over(DSL.partitionBy(USERS.PLAN_TIER)
                   .orderBy(DSL.trunc(USERS.CREATED_AT,
                              DatePart.MONTH)))
         .as("prev_month")
    )
    .from(USERS)
    .where(USERS.ACTIVE.isTrue())
    .groupBy(USERS.PLAN_TIER,
        DSL.trunc(USERS.CREATED_AT, DatePart.MONTH))
    .orderBy(USERS.PLAN_TIER)
    .fetch();
  // LAG() window function: idiomatic, type-safe, DB-specific

MyBatis solution:
  <!-- XML mapper: write the same SQL but as string -->
  <select id="monthlyActivePct" resultType="Map">
    SELECT plan_tier,
           COUNT(*) AS current_month,
           LAG(COUNT(*)) OVER (
               PARTITION BY plan_tier
               ORDER BY DATE_TRUNC('month', created_at)
           ) AS prev_month
    FROM users WHERE active = true
    GROUP BY plan_tier, DATE_TRUNC('month', created_at)
    ORDER BY plan_tier
  </select>
  // Works but no type safety; errors at runtime

Verdict: JOOQ wins for SQL-heavy analytics.
         Spring Data JPA wins for entity CRUD.
```

---

### 🧠 Mental Model / Analogy

> Think of SQL complexity as altitude. At low altitude
> (simple CRUD: find by ID, save, delete), any aircraft
> flies fine. Spring Data JPA is a commercial airliner:
> efficient, well-serviced, handles low-altitude routes with
> minimal pilot input. At high altitude (complex SQL: window
> functions, CTEs, lateral joins), small aircraft struggle
> and the airliner hits turbulence (awkward native SQL,
> lost type safety). JOOQ is a private jet: designed for
> any altitude, requires a trained pilot (schema code-gen,
> DSL learning curve), but handles complex routes elegantly.
> MyBatis is a helicopter: extremely maneuverable (full SQL
> control), but you manually handle everything. The right
> fleet uses multiple aircraft based on mission. Most
> Spring applications fly at low altitude most of the time
> - airliner (JPA) is the right default; rent the private
> jet (JOOQ) when the route demands it.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - When to use which (anyone can understand):**
Spring Data JPA: default for standard CRUD Spring Boot apps.
JOOQ: when queries get complex (reports, analytics).
MyBatis: when your team wants full SQL control.
Mixing: allowed and common in large apps.

**Level 2 - Code comparison (junior developer):**
```java
// Same query: "find active users by plan tier"

// Spring Data JPA (repository method derivation):
List<User> findByActiveTrueAndPlanTier(PlanTier tier);
// Hibernate generates: SELECT * FROM users
//   WHERE active=true AND plan_tier=?

// JOOQ (type-safe SQL builder):
dsl.selectFrom(USERS)
   .where(USERS.ACTIVE.isTrue()
      .and(USERS.PLAN_TIER.eq(tier.name())))
   .fetchInto(UserDTO.class);

// MyBatis (XML mapper):
// <select id="findByTier" resultType="UserDTO">
//   SELECT * FROM users
//   WHERE active=true AND plan_tier=#{tier}
// </select>
```

**Level 3 - Transaction integration (mid):**
All three integrate with Spring `@Transactional`.
Spring Data JPA: Hibernate manages connection within tx.
JOOQ: `DSLContext` uses Spring-managed `DataSource`; respects
`@Transactional` context automatically when configured with
`SpringTransactionProvider`.
MyBatis: `SqlSession` integrates with Spring transaction via
`SqlSessionTemplate`; uses same JDBC connection as Hibernate
if both are in same `@Transactional` context.

**Level 4 - Mixing Spring Data JPA + JOOQ (senior):**
```java
// Pattern: JPA for writes/CRUD, JOOQ for reads/reports
@Service
public class OrderReportService {
    @Autowired
    private OrderRepository jpaRepo;   // Spring Data JPA
    @Autowired
    private DSLContext dsl;            // JOOQ

    @Transactional  // same transaction for both
    public ReportDTO processAndReport(Long orderId) {
        // Write with JPA (entity lifecycle):
        Order order = jpaRepo.findById(orderId)
            .orElseThrow();
        order.setStatus(PROCESSED);
        jpaRepo.save(order);

        // Report with JOOQ (complex aggregation):
        return dsl.select(
                ORDERS.PRODUCT_ID,
                DSL.sum(ORDERS.AMOUNT))
            .from(ORDERS)
            .where(ORDERS.CUSTOMER_ID
                .eq(order.getCustomerId()))
            .groupBy(ORDERS.PRODUCT_ID)
            .fetchOneInto(ReportDTO.class);
    }
}
// Both use the same DataSource and @Transactional connection
```

**Level 5 - JOOQ code generation and maintenance (staff):**
```xml
<!-- pom.xml: JOOQ code generation plugin -->
<plugin>
  <groupId>org.jooq</groupId>
  <artifactId>jooq-codegen-maven</artifactId>
  <executions>
    <execution>
      <phase>generate-sources</phase>
      <goals><goal>generate</goal></goals>
      <configuration>
        <jdbc>
          <url>${db.url}</url>
          <user>${db.user}</user>
        </jdbc>
        <generator>
          <database>
            <name>org.jooq.meta.postgres.PostgresDatabase</name>
            <includes>.*</includes>
            <inputSchema>public</inputSchema>
          </database>
          <target>
            <packageName>com.example.generated.jooq</packageName>
          </target>
        </generator>
      </configuration>
    </execution>
  </executions>
</plugin>
<!-- Runs at build time; generates: Tables.java, Records.java,
     Keys.java, Routines.java from actual DB schema.
     Requires: DB available at build time (or Testcontainers).
     Maintenance: schema change -> regenerate -> compile errors
     show you all affected queries at compile time. -->
```

---

### ⚙️ How It Works (Mechanism)

**DECISION TREE:**

```
Start: choosing data access layer
│
├─ Does the domain have rich associations
│  and entity lifecycle matters (persist,
│  merge, cascade, dirty checking)?
│    YES -> Spring Data JPA (Hibernate)
│    NO  -> continue
│
├─ Are queries complex: window functions,
│  CTEs, lateral joins, complex aggregations,
│  DB-specific features?
│    YES -> JOOQ
│    NO  -> continue
│
├─ Does the team have strong SQL expertise
│  and want full SQL control? Or is this a
│  brownfield migration from JDBC/stored procs?
│    YES -> MyBatis
│    NO  -> Spring Data JPA (simpler, more convention)
│
├─ Are both CRUD entity management AND complex
│  SQL reporting needed in the same service?
│    YES -> Mix: Spring Data JPA + JOOQ
│           Both work in same @Transactional context
│    NO  -> Single tool per above branches

Common combinations:
  Microservice CRUD API: Spring Data JPA only
  Reporting service: JOOQ only
  Large monolith: Spring Data JPA + JOOQ for reports
  Legacy brownfield: MyBatis (existing SQL investment)
  New greenfield: Spring Data JPA + JOOQ for analytics
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ARCHITECTURE IN PRACTICE:**

```
E-commerce backend - 3 services, 3 different needs:

OrderService (entity lifecycle, CRUD):
  @Entity Order, @Entity OrderItem
  OrderRepository extends JpaRepository
  Spring Data JPA: persist, find, cascade, optimistic lock
  -> Hibernate manages INSERT/UPDATE/DELETE

AnalyticsService (complex SQL, reporting):
  No entities. DSLContext with JOOQ.
  SELECT product_id,
         SUM(quantity) OVER (PARTITION BY region) as total,
         LAG(SUM(quantity)) OVER (...) as prev_period
  FROM order_items
  JOOQ: type-safe, compile-time column names, window functions

LegacyIntegrationService (brownfield, stored procs):
  Existing DB with 50 stored procedures.
  MyBatis XML mappers call stored procs directly.
  No ORM needed: CALL proc_get_orders(#{customerId})

Shared: same DataSource, same @Transactional manager.
  Spring Boot autoconfigures all three with same connection pool.
```

---

### 💻 Code Example

**Migrating a complex query from JPA native to JOOQ:**

```java
// BAD: Spring Data JPA native SQL (loses type safety)
@Repository
public interface OrderRepo extends JpaRepository<Order, Long> {
    @Query(nativeQuery = true, value =
        "SELECT p.category, " +
        "  SUM(oi.quantity * oi.price) AS revenue, " +
        "  RANK() OVER (ORDER BY SUM(oi.quantity * oi.price) " +
        "    DESC) AS rank " +
        "FROM order_items oi " +
        "JOIN products p ON oi.product_id = p.id " +
        "WHERE oi.created_at > :since " +
        "GROUP BY p.category")
    List<Object[]> getRevenueByCategory(
        @Param("since") LocalDate since);
    // Returns Object[] - no type safety at all
    // Column rename in DB -> no compile error -> runtime NPE
    // Can't compose dynamically
}

// GOOD: JOOQ (type-safe, composable, readable)
@Repository
@RequiredArgsConstructor
public class OrderJooqRepository {
    private final DSLContext dsl;

    public List<RevenueByCategoryDTO> getRevenueByCategory(
            LocalDate since) {
        return dsl
            .select(
                PRODUCTS.CATEGORY,
                DSL.sum(
                    ORDER_ITEMS.QUANTITY
                        .mul(ORDER_ITEMS.PRICE)
                ).as("revenue"),
                DSL.rank()
                   .over(DSL.orderBy(
                       DSL.sum(ORDER_ITEMS.QUANTITY
                           .mul(ORDER_ITEMS.PRICE))
                           .desc()))
                   .as("rank")
            )
            .from(ORDER_ITEMS)
            .join(PRODUCTS)
                .on(ORDER_ITEMS.PRODUCT_ID.eq(PRODUCTS.ID))
            .where(ORDER_ITEMS.CREATED_AT.gt(since))
            .groupBy(PRODUCTS.CATEGORY)
            .fetchInto(RevenueByCategoryDTO.class);
        // Column rename -> compile error immediately
        // Composable: add .and(condition) dynamically
    }
}
```

---

### ⚖️ Comparison Table

| Criterion | Spring Data JPA | JOOQ | MyBatis |
|---|---|---|---|
| Query complexity | Low-medium | Any | Any |
| Entity lifecycle | Full (dirty check, cascade) | None | None |
| Type safety | JPQL is string-based | Compile-time (generated) | SQL strings only |
| DB-specific features | Via native SQL | Full support (generated) | Full SQL support |
| Learning curve | Medium | Medium + code-gen setup | Low (just SQL) |
| Code generation | No | Required | No |
| Bulk operations | Via JPQL (limited) | Excellent | Excellent |
| Dynamic queries | Criteria API / Specifications | Natural (fluent builder) | Dynamic SQL tags |
| Spring Boot auto-config | Native | Spring Boot starter | Spring Boot starter |
| Stored procedures | Via native query | Full support | Full support |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JOOQ replaces Spring Data JPA" | NO - JOOQ is not an ORM. It has no entity lifecycle, dirty checking, or identity map. JOOQ excels at SQL building; Spring Data JPA excels at entity management. They solve different problems and are commonly combined in the same application. |
| "MyBatis is legacy/bad" | Misconception. MyBatis is excellent for brownfield codebases with existing SQL investment, stored procedure-heavy databases, or teams with SQL expertise who don't want ORM abstraction. Many high-scale Chinese tech companies (Alibaba, Baidu) use MyBatis at enormous scale. It's not legacy - it's a deliberate design choice for SQL-first teams. |
| "You must choose one and use it for everything" | No requirement. Spring Boot supports Spring Data JPA + JOOQ in the same project on the same DataSource within the same @Transactional boundary. The mix pattern (JPA for CRUD entities, JOOQ for reporting) is widely used in production at scale. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: JOOQ DSLContext Ignores Spring Transaction**

**Symptom:** JOOQ write operations in a `@Transactional` method
are committed immediately, not rolled back when the transaction
rolls back. Mixed JPA+JOOQ code: JPA operations roll back but
JOOQ operations do not.
**Root Cause:** JOOQ's `DSLContext` was configured with a plain
`DataSource` directly instead of a Spring-transaction-aware
`DataSource`. JOOQ opened its own JDBC connection, bypassing
Spring's transaction synchronization.
**Diagnosis:**
```java
// Check JOOQ configuration:
// BAD: JOOQ uses its own connection (not tx-aware):
@Bean
public DSLContext dslContext(DataSource ds) {
    return DSL.using(ds, SQLDialect.POSTGRES);
    // WRONG: JOOQ opens new connection bypassing Spring tx
}

// GOOD: Spring-transaction-aware JOOQ:
@Bean
public DSLContext dslContext(DataSource ds) {
    return DSL.using(
        new DataSourceConnectionProvider(
            new TransactionAwareDataSourceProxy(ds)),
        new DefaultConfiguration()
            .set(SQLDialect.POSTGRES)
            .set(new SpringTransactionProvider(
                platformTransactionManager))
    );
}
// Or: use Spring Boot JOOQ autoconfiguration
// (spring-boot-starter-jooq) which configures this correctly
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-001 - JPA Overview]] - foundational JPA before comparing
- [[JPH-023 - JPQL Queries]] - JPA query model
- [[JPH-016 - Repository Pattern]] - Spring Data JPA foundation

**Builds On This (learn these next):**
- [[JPH-055 - ORM Selection Framework]] - formal decision
  framework extending this comparison

**Related:**
- [[JPH-050 - Hibernate vs MyBatis vs JOOQ]] - feature comparison
- [[JPH-053 - QueryDSL with JPA]] - type-safe JPA alternative
  (compare with JOOQ approach)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SPRING DATA JPA │ Use for: entity CRUD, lifecycle,       │
│                 │ associations, audit, pagination.        │
│                 │ Avoid for: complex SQL, analytics.      │
├─────────────────┼─────────────────────────────────────────┤
│ JOOQ            │ Use for: complex SQL, window functions, │
│                 │ type-safe queries, DB-specific features.│
│                 │ Avoid for: entity lifecycle management. │
├─────────────────┼─────────────────────────────────────────┤
│ MYBATIS         │ Use for: stored procs, full SQL control,│
│                 │ brownfield, SQL-first teams.            │
│                 │ Avoid for: complex domain models.       │
├─────────────────┼─────────────────────────────────────────┤
│ MIXING          │ Spring Data JPA + JOOQ in same project: │
│                 │ both use same @Transactional context.   │
│                 │ Common in large apps.                   │
├─────────────────┼─────────────────────────────────────────┤
│ ONE-LINER       │ "JPA = entity management;               │
│                 │ JOOQ = type-safe SQL building;          │
│                 │ MyBatis = SQL mapping. Mix as needed."  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Spring Data JPA = ORM (entity lifecycle); JOOQ = SQL DSL; MyBatis = SQL mapping
2. JOOQ is not an ORM - no dirty checking, no entity lifecycle; they complement JPA, not replace it
3. Mixing Spring Data JPA + JOOQ in one Spring Boot app is idiomatic for CRUD + reporting

**Interview one-liner:** Spring Data JPA (via Hibernate) manages entity lifecycle - `@Entity`,
dirty checking, cascade, associations. Use it for CRUD-heavy domain models. JOOQ is a type-safe
SQL builder (code-generated from schema) for complex SQL: window functions, CTEs, analytics -
no ORM lifecycle. MyBatis is SQL mapping for teams who want full SQL control. The pragmatic
choice for a Spring Boot microservice with complex reporting: Spring Data JPA for entities +
JOOQ for reports, sharing the same `@Transactional` context.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The best tool is matched
to the task, not applied uniformly across all tasks. This
applies beyond ORM choices: REST vs gRPC vs GraphQL per
API use case; Redis vs PostgreSQL per data access pattern;
synchronous vs async per latency requirement. "Use X for
everything" is an anti-pattern in engineering. The engineering
judgment is: identify the dimensions that matter (query
complexity, entity lifecycle need, type safety requirement,
team SQL expertise), find the tool that best matches on the
key dimensions, and accept its limitations in areas that
don't matter for this context. The worst anti-pattern:
choosing one tool for political reasons ("we standardize on
JPA") and then fighting against its limitations in every
use case where it's the wrong fit.

---

### 💡 The Surprising Truth

JOOQ's license model is a significant operational consideration
often overlooked: JOOQ is free for open-source databases
(PostgreSQL, MySQL, H2) but PAID for commercial databases
(Oracle, SQL Server, DB2). A team on Oracle evaluating JOOQ
for "just reporting queries" needs a commercial JOOQ license.
This asymmetry means: JOOQ is ubiquitous in PostgreSQL/MySQL
Spring Boot shops but rarely seen in Oracle enterprise shops
(where MyBatis or Spring Data JPA native queries are preferred
due to licensing). Before recommending JOOQ in an enterprise
context: verify the target database license tier. This is
a real architecture decision driver that doesn't appear in
technical comparisons.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the fundamental difference between an ORM
   (entity lifecycle) and a SQL builder (JOOQ) in one paragraph
2. **IDENTIFY** which tool is wrong for a given use case
   (e.g., "complex analytics" with Spring Data JPA native SQL)
3. **CONFIGURE** JOOQ and Spring Data JPA to share the same
   `@Transactional` context in a Spring Boot app
4. **WRITE** a JOOQ query with window functions and explain
   why the equivalent JPQL version is impossible or awkward
5. **JUSTIFY** using MyBatis over JOOQ in a specific scenario
   (Oracle + commercial licensing, stored procedure heavy)

---

### 🎯 Interview Deep-Dive

**Q1: When would you choose JOOQ over Spring Data JPA?
Describe a concrete scenario.**
*Why they ask:* Tests whether candidate can go beyond "JOOQ is type-safe"
to explain the actual use case boundaries.
*Strong answer includes:*
- Spring Data JPA scenario: CRUD entities, simple queries,
  entity associations, domain model with lifecycle
- JOOQ scenario: complex SQL required - window functions (`LAG`, `RANK`,
  `ROW_NUMBER`), CTEs, complex multi-table aggregations, DB-specific
  features (PostgreSQL arrays, JSON operators), dynamic SQL with many
  optional conditions
- Concrete example: reporting service that generates monthly revenue by
  product category with % change from prior month - requires `LAG()`
  window function; Spring Data JPA has no JPQL equivalent; would require
  native SQL losing type safety; JOOQ handles it idiomatically with
  compile-time column names
- Operational note: JOOQ requires code-gen from DB schema at build time;
  adds CI/CD complexity; requires DB access at build

**Q2: Can Spring Data JPA and JOOQ be used in the same
Spring Boot application? If so, how do you ensure they
participate in the same transaction?**
*Why they ask:* Tests integration architecture knowledge.
*Strong answer includes:*
- YES - both can use the same `DataSource` and Spring transaction manager
- Spring Boot: use `spring-boot-starter-data-jpa` + `spring-boot-starter-jooq`
- Spring Boot auto-configures JOOQ with `TransactionAwareDataSourceProxy` when
  `spring-boot-starter-jooq` is on classpath - JOOQ automatically joins the
  Spring transaction
- Both JPA operations and JOOQ operations in the same `@Transactional` method
  use the same JDBC connection; commit/rollback affects both
- Common pattern: `OrderRepository` (JPA) for writes; `OrderJooqRepository`
  (JOOQ `DSLContext`) for complex read queries; both in same `@Transactional` service
- Caveat: Hibernate 1LC and JOOQ are independent - JOOQ reads won't hit Hibernate's
  identity map; if you JOOQ-update a row and then JPA-load it, the 1LC may return
  the stale Hibernate snapshot unless you call `em.refresh()` or `em.clear()`
