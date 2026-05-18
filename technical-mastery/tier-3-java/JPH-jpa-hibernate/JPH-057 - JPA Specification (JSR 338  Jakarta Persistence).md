---
id: JPH-057
title: "JPA Specification (JSR 338 / Jakarta Persistence)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-001, JPH-006, JPH-011, JPH-014, JPH-060
used_by: []
related: JPH-001, JPH-060, JPH-058
tags:
  - java
  - jpa
  - database
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/jpa-hibernate/jpa-specification/
---

⚡ **TL;DR** - JPA (Jakarta Persistence API) is a standard
specification (not a library) defining how Java objects
map to relational databases. Currently at Jakarta
Persistence 3.1 (Spring Boot 3.x). Key packages:
`jakarta.persistence.*` (Spring Boot 3) vs `javax.persistence.*`
(Spring Boot 2 / JPA 2.2). Hibernate is the reference
implementation. The spec defines: `@Entity`, `EntityManager`,
JPQL, Criteria API, lifecycle callbacks. The spec does NOT
define: N+1 behavior, 2LC specifics, batch size,
`StatelessSession` - those are Hibernate extensions.

| #057            | Category: JPA & Hibernate                                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | JPA Overview, Entity Basics, Entity Lifecycle, JPQL, Hibernate 6 Migration |                 |
| **Used by:**    | -                                                                          |                 |
| **Related:**    | JPA Overview, Hibernate 6 Migration, Hibernate Internals                   |                 |

---

### 🔥 The Problem This Solves

**WHY A STANDARD MATTERS:**

```
Without JPA standard (2001-2006 Java ORM landscape):
  Team A uses Hibernate (HQL, Session API)
  Team B uses TopLink (EJBQL, EntityBean API)
  Team C uses JDO (JDOQL, PersistenceManager API)
  - Code is 100% vendor-specific: switch ORM = rewrite
  - JEE container integration inconsistent per ORM
  - Different lifecycle APIs: Session vs EntityManager
  - XML deployment descriptors differ

With JPA 1.0 (2006, JSR 220 part of EJB 3.0):
  All three ORMs implement EntityManager, @Entity, JPQL
  Code written to JPA standard: portable across ORMs
  Spring: one JpaTransactionManager for all providers
  "Program to the interface, not implementation" for ORM

Current (2024): Jakarta Persistence 3.1
  - Standardizes: EntityManager, JPQL, Criteria API,
    @Entity/associations
  - Hibernate 6.x: reference implementation
  - EclipseLink: JEE reference implementation
  - 95% of apps: Hibernate via Spring Boot
  - Portability remains theoretical benefit;
    practical value: stable, well-documented API
```

---

### 📘 Textbook Definition

**JPA (Jakarta Persistence API)** is a Java specification
(Jakarta EE) that defines the ORM programming model for
Java applications. Originally **Java Persistence API** under
`javax.persistence` package; renamed to **Jakarta Persistence**
under `jakarta.persistence` when Java EE transitioned to Jakarta EE.

**Version history:**

| Version                 | Year | Package               | Key additions                          | Spring Boot version |
| ----------------------- | ---- | --------------------- | -------------------------------------- | ------------------- |
| JPA 1.0 (JSR 220)       | 2006 | `javax.persistence`   | Core: @Entity, EntityManager, JPQL     | 1.x                 |
| JPA 2.0 (JSR 317)       | 2009 | `javax.persistence`   | Criteria API, metamodel, cache API     | 1.x-2.x             |
| JPA 2.1 (JSR 338)       | 2013 | `javax.persistence`   | Stored procedure, bulk ops, converters | 2.x                 |
| JPA 2.2                 | 2017 | `javax.persistence`   | Java 8 types, streaming                | 2.x                 |
| Jakarta Persistence 3.0 | 2020 | `jakarta.persistence` | Package rename from `javax`            | 3.x                 |
| Jakarta Persistence 3.1 | 2022 | `jakarta.persistence` | Math functions, UUID, numeric types    | 3.x                 |

**Key standard interfaces:**

| Interface                 | Location                        | Role                                  |
| ------------------------- | ------------------------------- | ------------------------------------- |
| `EntityManager`           | `jakarta.persistence`           | Persistence context operations        |
| `EntityManagerFactory`    | `jakarta.persistence`           | Create EntityManager; session factory |
| `Query` / `TypedQuery<T>` | `jakarta.persistence`           | JPQL/native query execution           |
| `CriteriaBuilder`         | `jakarta.persistence.criteria`  | Build Criteria queries                |
| `CriteriaQuery<T>`        | `jakarta.persistence.criteria`  | Criteria query structure              |
| `Metamodel`               | `jakarta.persistence.metamodel` | Static metamodel access               |

---

### ⏱️ Understand It in 30 Seconds

**One line:** JPA is the specification (the standard
API contract); Hibernate is the implementation. You write
code against JPA interfaces; Hibernate implements them.

**One analogy:**

> JPA is like JDBC. JDBC is a standard (interface +
> contract); MySQL driver, PostgreSQL driver, H2 are
> implementations. You write `Connection.prepareStatement(sql)`
> (JDBC interface); the PostgreSQL driver implements it.
> JPA is the ORM equivalent: you write `EntityManager.find()`
> (JPA interface); Hibernate implements it. Just as you
> rarely switch JDBC drivers, you rarely switch JPA providers.
> The value: consistent API regardless of which ORM is used;
> Spring, Quarkus, Jakarta EE containers all know how to
> integrate with "any JPA provider."

**One insight:** The most important practical implication
of the JPA spec for Spring Boot 3 developers is the package
rename. Anything that was `javax.persistence.X` in Spring Boot 2
is now `jakarta.persistence.X` in Spring Boot 3. This is
the #1 compilation error when migrating from Spring Boot 2 to 3.
The rename happened because Oracle transferred Java EE to the
Eclipse Foundation, which needed to rename the `javax.*` namespace
(Oracle retains the `javax.` trademark).

---

### 🔩 First Principles Explanation

**SPEC vs IMPLEMENTATION BOUNDARY:**

```
JPA Spec (jakarta.persistence.*) defines:
  @Entity, @Id, @GeneratedValue, @Column         -> entity
    mapping
  @ManyToOne, @OneToMany, @ManyToMany, @OneToOne ->
    association mapping
  EntityManager.find(), persist(), merge(),       ->
    lifecycle ops
    remove(), refresh()
  JPQL: SELECT e FROM Entity e WHERE ...          -> query
    language
  Criteria API: CriteriaQuery, CriteriaBuilder    ->
    type-safe queries
  @NamedQuery, @NamedNativeQuery                  -> named
    queries
  @EntityListeners, @PrePersist, @PostUpdate etc  ->
    lifecycle callbacks
  JPA Caching API: @Cacheable, @Cache             -> 2LC
    hints

Hibernate-specific extensions (org.hibernate.*):
  @BatchSize, @Fetch, @FetchMode                  -> fetch
    strategy
  @Cache region settings (EhCache, Hazelcast)     -> 2LC
    config
  Session.enableFilter(), @FilterDef, @Filter     -> SQL
    filters
  StatelessSession                                -> batch
    session
  hibernate.jdbc.batch_size                       ->
    batching config
  @Immutable                                      ->
    read-only entity
  @Formula                                        ->
    derived fields
  @Type, @CompositeType                           ->
    custom type system
  @TenantId                                       ->
    multi-tenancy (H6)
  HQL extensions (TREAT, table-valued functions)  ->
    extended query ops

RULE: prefer JPA standard annotations;
      use Hibernate-specific only when JPA provides no
        equivalent.
```

---

### 🧪 Thought Experiment

**THE javax -> jakarta MIGRATION IMPACT:**

```java
// Spring Boot 2.x code (JPA 2.2 / javax):
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.GeneratedValue;
import javax.persistence.ManyToOne;
import javax.persistence.Transient;
import javax.persistence.Column;

// Spring Boot 3.x code (Jakarta Persistence 3.x / jakarta):
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Transient;
import jakarta.persistence.Column;

// The annotations are IDENTICAL in name and semantics;
// ONLY the package changes.

// ALSO affected (not just JPA):
import javax.validation.constraints.NotNull;  // Spring Boot 2
import jakarta.validation.constraints.NotNull; // Spring Boot 3
// Bean Validation also migrated to jakarta.* namespace

// Build tools can help:
// OpenRewrite recipe: org.openrewrite.java.migrate.Jakarta
// IntelliJ: File -> Migrate to newer Spring -> Spring Boot 3
// Migration is mechanical; ~30 min for typical project
```

---

### 🧠 Mental Model / Analogy

> The JPA specification is like a building code. Building
> codes define: minimum ceiling height, required exits,
> load-bearing standards. Every contractor (ORM provider:
> Hibernate, EclipseLink) must comply with the building code.
> But each contractor has their own tools, techniques,
> and specializations beyond the minimum code (Hibernate's
> `StatelessSession`, EclipseLink's change tracking).
> The building code (JPA spec) ensures interoperability
> of the base: any JEE container, Spring, Quarkus can
> "inspect" any building (application) and understand
> the JPA layer because it conforms to code. Hibernate
> extensions are like premium finishes: beyond code, not
> portable, but often the right choice.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Spec vs implementation (anyone can understand):**
JPA is the standard (like JDBC for ORM). Hibernate is the
most popular implementation. You write `@Entity` (JPA);
Hibernate handles the SQL generation.

**Level 2 - Key spec annotations (junior developer):**

```java
// All from jakarta.persistence:
@Entity                // marks class as persistent
@Table(name="products")// maps to specific table
@Id                    // primary key
@GeneratedValue        // auto-generate PK
@Column(name="prod_name") // map to specific column
@ManyToOne             // many-to-one association
@OneToMany(cascade=CascadeType.ALL) // one-to-many
@Transient             // not persisted to DB
@NamedQuery(name="...", // static JPQL query
    query="SELECT e FROM Entity e")
@EntityListeners(AuditListener.class) // lifecycle callbacks
```

**Level 3 - What the spec guarantees (mid-level engineer):**
The spec guarantees portable behavior for: entity lifecycle
states (TRANSIENT, MANAGED, DETACHED, REMOVED), JPQL syntax
(all providers must support it), Criteria API structure,
cascade types, fetch types (LAZY/EAGER semantics), locking
modes (`LockModeType` values), and transaction integration.
The spec does NOT guarantee: performance of N+1 fetching,
default batch sizes, cache hit rates, or provider-specific
SQL generation behavior (ORDER BY may vary).

**Level 4 - EntityManager lifecycle (senior engineer):**

```java
// EntityManager is the JPA entry point (spec-defined)
// In Spring: injected as a scoped proxy (one per tx)
@PersistenceContext  // JPA spec injection
private EntityManager em;

// Core operations (all spec-defined):
em.persist(entity);          // transient -> managed (INSERT queued)
em.find(T.class, id);        // SELECT; result is managed
em.merge(detachedEntity);    // detached -> managed (UPDATE queued)
em.remove(managedEntity);    // managed -> removed (DELETE queued)
em.flush();                  // flush pending changes to DB
em.clear();                  // detach all; clear persistence context
em.refresh(managedEntity);
// reload from DB; discard pending changes
em.detach(managedEntity);    // managed -> detached (stops tracking)
em.contains(entity);         // is entity in managed state?
em.getLockMode(entity);      // current lock mode on entity
em.setProperty(key, value);  // hint to provider (batch size, etc.)
```

**Level 5 - JPA 3.1 additions (staff engineer):**
Jakarta Persistence 3.1 (2022) adds: math functions in JPQL
(`CEILING`, `FLOOR`, `ROUND`, `EXP`, `LN`, `POWER`, `SIGN`),
UUID support as a first-class type (`@Id` on UUID),
local/offset date/time in JPQL (`LOCAL DATE`, `LOCAL TIME`,
`LOCAL DATETIME`, `OFFSET TIME`, `OFFSET DATETIME`), and
`EXTRACT()` in JPQL (year, month, day extraction without
vendor-specific functions). Hibernate 6 implements JP 3.1.
Practical implication: Spring Boot 3.x developers can use
standard JPQL functions that previously required Hibernate-specific
expressions or native SQL.

---

### ⚙️ How It Works (Mechanism)

**PERSISTENCE.XML vs SPRING BOOT AUTO-CONFIGURATION:**

```xml
<!-- Traditional JPA: persistence.xml in META-INF/ -->
<persistence xmlns="https://jakarta.ee/xml/ns/persistence"
    version="3.0">
    <persistence-unit name="myApp"
        transaction-type="RESOURCE_LOCAL">
        <provider>
            org.hibernate.jpa.HibernatePersistenceProvider
        </provider>
        <class>com.example.Product</class>
        <properties>
            <property name="jakarta.persistence.jdbc.url"
                value="jdbc:postgresql://..."/>
            <property name="hibernate.hbm2ddl.auto"
                value="validate"/>
        </properties>
    </persistence-unit>
</persistence>
```

```properties
# Spring Boot: replaces persistence.xml
# Auto-configures EntityManagerFactory via
# LocalContainerEntityManagerFactoryBean
# No persistence.xml needed:
spring.datasource.url=jdbc:postgresql://...
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.properties.hibernate.jdbc.batch_size=50
# Spring Boot scans @Entity classes automatically
```

Spring Boot's `HibernateJpaAutoConfiguration` creates:

- `LocalContainerEntityManagerFactoryBean` (wraps Hibernate `SessionFactory`)
- `JpaTransactionManager` (implements both `PlatformTransactionManager`
  and JPA `EntityTransaction` semantics)

---

### 🔄 The Complete Picture - End-to-End Flow

**JPA PORTABILITY IN PRACTICE:**

```
Standard JPA code (compiles against jakarta.persistence.*):
  @Entity
  @Table(name = "products")
  public class Product {
      @Id @GeneratedValue
      private Long id;
      @Column(nullable = false)
      private String name;
  }

  interface ProductRepository
      extends JpaRepository<Product, Long> {}

This code compiles and runs against:
  - Hibernate 6.x (Spring Boot 3.x default)
  - EclipseLink (switch JPA provider in boot config)
  - DataNucleus (alternative JPA provider)

Switch JPA provider in Spring Boot:
spring.jpa.properties.jakarta.persistence.provider=
  org.eclipse.persistence.jpa.PersistenceProvider
<!-- Exclude Hibernate, add EclipseLink dependency -->

PRACTICAL REALITY: 99% of Spring Boot apps use Hibernate.
Portability benefits are theoretical. The real value of JPA
standard: stable, well-documented API that every Spring
developer knows; consistent behavior across Spring,
  Quarkus,
Jakarta EE; large ecosystem of tools, books, courses.
```

---

### 💻 Code Example

**Example 1 - JPA 3.1 new JPQL math functions:**

```java
// JPA 3.1 (Jakarta Persistence 3.1 / Hibernate 6+):
// Math functions now standard in JPQL (no native SQL needed)

// Round product price to 2 decimal places:
em.createQuery(
    "SELECT ROUND(p.price, 2) FROM Product p " +
    "WHERE p.active = true",
    BigDecimal.class).getResultList();

// Extract year from date (standard JPQL):
em.createQuery(
    "SELECT p FROM Order p " +
    "WHERE EXTRACT(YEAR FROM p.createdAt) = :year",
    Order.class)
    .setParameter("year", 2024)
    .getResultList();

// LOCAL DATE (current date in JPQL, standard in 3.1):
em.createQuery(
    "SELECT p FROM Subscription p " +
    "WHERE p.expiresAt < LOCAL DATE")
    .getResultList();
// Previously required: Hibernate-specific CURRENT_DATE
// or native SQL CURRENT_DATE
```

**Example 2 - UUID as @Id (JPA 3.1):**

```java
// JPA 3.1 / Hibernate 6+: UUID as first-class ID type
@Entity
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;    // UUID type, JPA 3.1 standard
    // Hibernate 6 maps to: uuid column type in PostgreSQL
    //                       binary(16) or varchar(36) in MySQL
    private String name;
}
// Previously: required Hibernate-specific @Type annotation
// Now: standard JPA
```

---

### ⚖️ Comparison Table

| Package               | JPA version | Spring Boot version | Hibernate version |
| --------------------- | ----------- | ------------------- | ----------------- |
| `javax.persistence`   | 1.0 - 2.2   | 1.x - 2.x           | 4.x - 5.x         |
| `jakarta.persistence` | 3.0 - 3.1+  | 3.x+                | 6.x+              |

**Key differences JPA 2.2 -> Jakarta 3.x:**

- Package: `javax.persistence` -> `jakarta.persistence`
- Bean Validation: `javax.validation` -> `jakarta.validation`
- Servlet API: `javax.servlet` -> `jakarta.servlet`
- CDI: `javax.inject` -> `jakarta.inject`

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "JPA and Hibernate are the same"                            | JPA is the specification (interfaces, annotations, contracts). Hibernate is an implementation. You can run JPA code with EclipseLink or DataNucleus instead of Hibernate. In practice: Hibernate is used in >95% of Spring applications, so the distinction is rarely relevant but important to understand conceptually. |
| "javax.persistence annotations still work in Spring Boot 3" | NO - Spring Boot 3 requires `jakarta.persistence.*`. Any code using `javax.persistence.*` will fail to compile against Spring Boot 3's classpath. This is the #1 compilation error in Spring Boot 2 -> 3 migrations. The fix is a mechanical import rename (OpenRewrite automates this).                                 |
| "The JPA spec defines N+1 behavior"                         | NO - the JPA spec defines `FetchType.LAZY` as an optimization HINT. The spec does not require lazy loading to be implemented as "load on first access." Hibernate happens to implement LAZY as a proxy that loads on first method call. The N+1 problem is a Hibernate implementation behavior, not a JPA spec behavior. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: javax vs jakarta Import Conflict**

**Symptom:** `ClassNotFoundException: javax.persistence.Entity`
or `NoClassDefFoundError` after upgrading Spring Boot.
Or: entity annotations are not recognized; `@Entity`
produces no error but entity is not mapped to a table.

**Root Cause:** Codebase has `import javax.persistence.Entity`
(Spring Boot 2 style) but classpath only has `jakarta.persistence.Entity`
(Spring Boot 3 style). The class loads but the annotation
is from a different package - treated as unknown annotation.

**Diagnosis:**

```bash
# Find all javax.persistence imports:
grep -r "javax.persistence" src/
# If found and Spring Boot version is 3.x: must migrate

# Also check:
grep -r "javax.validation" src/  # bean validation
grep -r "javax.servlet"   src/  # servlet API
```

**Fix:** Replace all `javax.persistence` -> `jakarta.persistence`.
OpenRewrite: `mvn rewrite:run -Drewrite.recipe=org.openrewrite.java.migrate.javax.JavaxPersistenceToJakartaPersistence`

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-001 - JPA Overview]] - practical JPA usage before
  understanding the spec formally
- [[JPH-006 - Entity Basics]] - `@Entity` annotation meaning
  and mapping conventions per spec

**Builds On This (learn these next):**

- [[JPH-060 - Hibernate 6 Migration]] - Jakarta Persistence 3
  migration from Spring Boot 2 to 3

**Related:**

- [[JPH-058 - Hibernate Internals]] - how Hibernate
  implements JPA spec interfaces
- [[JPH-001 - JPA Overview]] - practical application of
  JPA spec concepts

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ SPEC vs IMPL │ JPA = spec (jakarta.persistence.*)       │
│              │ Hibernate = implementation (reference)   │
├──────────────┼──────────────────────────────────────────┤
│ PACKAGE      │ Spring Boot 2: javax.persistence.*       │
│ SPLIT        │ Spring Boot 3: jakarta.persistence.*     │
│              │ Migration: mechanical import rename      │
├──────────────┼──────────────────────────────────────────┤
│ CURRENT VER  │ Jakarta Persistence 3.1 (Spring Boot 3.x)│
│              │ Hibernate 6.x as implementation          │
├──────────────┼──────────────────────────────────────────┤
│ 3.1 ADDS     │ Math functions, UUID @Id, LOCAL DATE,    │
│              │ EXTRACT() in JPQL - all standard now     │
├──────────────┼──────────────────────────────────────────┤
│ PORTABILITY  │ Standard code runs on Hibernate,         │
│              │ EclipseLink, DataNucleus (theoretical;   │
│              │ 99% of apps use Hibernate)               │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "JPA = ORM specification standard.       │
│              │ Spring Boot 3 uses jakarta.persistence.*.│
│              │ Hibernate is the reference impl."        │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. JPA = specification (interfaces); Hibernate = implementation;
   Spring Data JPA = Spring abstraction on top of JPA
2. Spring Boot 2 = `javax.persistence.*`; Spring Boot 3 = `jakarta.persistence.*`;
   #1 migration compilation error is this package rename
3. JPA 3.1 adds math functions, UUID `@Id`, `LOCAL DATE` to standard JPQL

**Interview one-liner:** JPA is the ORM specification (Jakarta Persistence API,
Jakarta EE standard) under `jakarta.persistence.*` in Spring Boot 3
(was `javax.persistence.*` in Spring Boot 2). Hibernate 6.x is the reference
implementation. The spec defines: `@Entity`, `EntityManager`, JPQL, Criteria API,
lifecycle annotations. Hibernate adds: `@BatchSize`, `StatelessSession`, `@Cache`,
`@Filter` - beyond the spec. Jakarta Persistence 3.1 adds math functions,
UUID primary keys, and temporal functions to standard JPQL.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Specifications (JSRs,
RFCs, W3C standards) separate the contract from the
implementation. This enables: (1) portable code (program
to the interface), (2) vendor competition (multiple
implementations of the same standard), (3) long-term stability
(specs evolve slowly; breaking the standard is a major event),
(4) tooling ecosystem (Spring, IDEs, testing frameworks
all know the JPA standard). The Java ecosystem has many
such specifications: JDBC, JMS, JAX-RS (REST), JAX-WS (SOAP),
Bean Validation, CDI, Servlet API. When you see `javax.*`
or `jakarta.*`: these are standard APIs, not library APIs.
Understanding which capabilities are "spec" (portable) vs
"provider extension" (vendor lock-in) is a key architectural
judgment in Java enterprise development.

---

### 💡 The Surprising Truth

The `javax` -> `jakarta` namespace rename was NOT about
technical necessity - it was about trademark rights. When
Oracle donated Java EE to the Eclipse Foundation in 2017,
Oracle retained the trademark on the `javax.*` namespace.
The Eclipse Foundation needed to rename the packages to
maintain control over their evolution. This is why the
transition was purely a package rename with no API changes
in Jakarta EE 9: `javax.persistence.Entity` -> `jakarta.persistence.Entity`
is identical in every way except the package name. The
rename broke source compatibility for millions of projects
but did not change any semantics. It remains one of the
most controversial decisions in Java EE history. The
practical lesson: trademarks on package namespaces matter;
when choosing dependency packages for a library you intend
to maintain long-term, ensure you control the namespace.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** the relationship between the JPA spec,
   Hibernate, Spring Data JPA, and Spring Boot
2. **IDENTIFY** which annotations/interfaces are JPA
   standard (`jakarta.persistence`) vs Hibernate-specific
   (`org.hibernate`)
3. **MIGRATE** a Spring Boot 2 project's `javax.persistence`
   imports to `jakarta.persistence` for Spring Boot 3
4. **LIST** the key additions in Jakarta Persistence 3.1
   (math functions, UUID, LOCAL DATE)
5. **EXPLAIN** why the `javax` -> `jakarta` rename happened
   (trademark, not technical reasons)

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between JPA, Hibernate,
and Spring Data JPA?**
_Why they ask:_ Tests clarity of the Java persistence stack.
_Strong answer includes:_

- JPA (Jakarta Persistence API): the SPECIFICATION - defines
  the interface contract. `@Entity`, `EntityManager`, JPQL are
  JPA concepts. Package: `jakarta.persistence.*`
- Hibernate: the IMPLEMENTATION of JPA. Provides the actual
  SQL generation, dirty checking, 2LC. Adds extensions beyond JPA:
  `@BatchSize`, `@Filter`, `StatelessSession`. Package: `org.hibernate.*`
- Spring Data JPA: SPRING ABSTRACTION on top of JPA. Provides
  repository interfaces (`JpaRepository`), auto-query generation from method
  names, `@Transactional` integration, pagination, specifications.
  Spring Data JPA uses Hibernate (by default) to implement JPA operations.
  Package: `org.springframework.data.jpa.*`
- Hierarchy: Spring Data JPA -> JPA (via Hibernate) -> JDBC -> DB

**Q2: A team member says "We should avoid Hibernate-specific
annotations and only use standard JPA annotations for portability."
Is this advice sound?**
_Why they ask:_ Tests pragmatic architecture judgment.
_Strong answer includes:_

- Partially sound; but overly rigid in practice
- Portability benefit: code compiles against any JPA provider
- Reality check: 99% of Spring apps use Hibernate; switching providers
  is extremely rare (complex migration, different behaviors)
- When Hibernate-specific annotations provide significant value
  (`@BatchSize` for N+1, `@Cache` for 2LC config, `@Immutable` for
  read-only entities), use them pragmatically
- Better principle: use JPA standard when JPA provides the feature;
  use Hibernate-specific when JPA has no equivalent or Hibernate's
  implementation is significantly better
- Document Hibernate-specific annotations in code comments so future
  maintainers understand the coupling
