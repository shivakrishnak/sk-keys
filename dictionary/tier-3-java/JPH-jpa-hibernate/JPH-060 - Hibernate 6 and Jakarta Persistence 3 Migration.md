---
id: JPH-060
title: Hibernate 6 and Jakarta Persistence 3 Migration
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-001, JPH-006, JPH-011, JPH-014, JPH-026, JPH-057
used_by: []
related: JPH-057, JPH-058, JPH-051
tags:
  - java
  - jpa
  - hibernate
  - migration
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 60
permalink: /jpa-hibernate/hibernate-6-and-jakarta-persistence-3-migration/
---

# JPH-060 - Hibernate 6 and Jakarta Persistence 3 Migration

⚡ **TL;DR** - Spring Boot 3.x upgrades from Hibernate 5 to
Hibernate 6 and from JPA 2.2 (`javax.persistence`) to Jakarta
Persistence 3.x (`jakarta.persistence`). The three migration
breaking points: (1) package rename: `javax.persistence.*` ->
`jakarta.persistence.*` (mechanical, all imports), (2) Hibernate 6
type system overhaul (`@Type`, `@TypeDef` removed; use `@JavaType`,
`@JdbcType`, `@CompositeType`), (3) Hibernate 6 new query model
(SQM replaces old query plan cache; some legacy HQL syntax deprecated).
Automated with OpenRewrite. Typical migration: 1-3 days for a
mid-size Spring Boot 2 app.

| #060 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JPA Overview, Entity Basics, EntityManager, JPQL, Persistence Context, JPA Spec | |
| **Used by:** | - | |
| **Related:** | JPA Spec, Hibernate Internals, Converters | |

---

### 🔥 The Problem This Solves

**WHY THIS MIGRATION IS NEEDED:**

```
Spring Boot 2.x (Hibernate 5 / javax.persistence):
  Spring Boot 2.7 (last 2.x): EOL November 2023
  No security patches after EOL
  Jakarta EE 8 = javax.* namespace
  Hibernate 5: old query engine (Antlr2), old type system
  Java 8 minimum

Spring Boot 3.x (Hibernate 6 / jakarta.persistence):
  Requires Java 17 minimum
  Jakarta EE 10 = jakarta.* namespace
  Hibernate 6: new SQM query engine (Antlr4), improved type system
  Active security maintenance through 2025+
  New features: UUID @Id, virtual threads (Spring Boot 3.2+),
  native GraalVM support

The migration is MANDATORY for teams that need:
  - Long-term security support
  - Java 17+ features (records, sealed classes, text blocks)
  - GraalVM native image compilation
  - Jakarta EE 10 ecosystem compatibility
  - Spring Security 6, Spring Batch 5, Spring Authorization Server

Staying on Spring Boot 2.x: viable short-term but compounds
migration cost every quarter (more changes to migrate at once).
```

---

### 📘 Textbook Definition

**Hibernate 6 Migration** refers to the upgrade from Hibernate
ORM 5.x (Spring Boot 2.x) to Hibernate ORM 6.x (Spring Boot 3.x)
with the concurrent Jakarta Persistence 3.x adoption. This is
part of the broader Jakarta EE namespace migration from `javax.*`
to `jakarta.*`.

**Key versions in the migration path:**

| Spring Boot | JPA spec | Hibernate | Package | Java minimum |
|---|---|---|---|---|
| 2.5.x - 2.7.x | JPA 2.2 | 5.6.x | `javax.persistence` | 8 |
| 3.0.x | Jakarta 3.0 | 6.1.x | `jakarta.persistence` | 17 |
| 3.1.x | Jakarta 3.1 | 6.2.x | `jakarta.persistence` | 17 |
| 3.2.x | Jakarta 3.1 | 6.4.x | `jakarta.persistence` | 17 |

**Three categories of changes:**

| Category | Scope | Example |
|---|---|---|
| Package rename | All `javax.*` imports | `javax.persistence.Entity` -> `jakarta.persistence.Entity` |
| Hibernate type system | `@Type`, `@TypeDef` APIs | `@Type(type="json")` -> `@JdbcTypeCode(SqlTypes.JSON)` |
| Query/SQL changes | Some HQL/JPQL changes | Deprecated implicit join syntax removed |

---

### ⏱️ Understand It in 30 Seconds

**One line:** Spring Boot 3 = Hibernate 6 + `jakarta.persistence.*` (not `javax.`).
Three things break: import packages, `@Type` annotations, some HQL syntax.

**One analogy:**
> This migration is like moving from one city to another with the same
> job. Your skills (Java, JPA, Hibernate) are identical. But your
> address changes (`javax` -> `jakarta`), your workplace layout changed
> (Hibernate 6 type system), and some local roads are different (HQL
> syntax changes). Most of your daily routine is identical. A few
> weeks of adjustment. After that: new city is better (Java 17, better
> performance, active maintenance). The worst approach: stay in the old
> city until it shuts down, then scramble. The best approach: migrate
> deliberately while the old city still works.

---

### 🔩 First Principles Explanation

**THE THREE BREAKING CHANGES IN DETAIL:**

```
BREAKING CHANGE 1: Package rename (most widespread)
  Scope: ALL Java files with JPA annotations/interfaces

  Renamed namespaces (complete list for JPA):
    javax.persistence.* -> jakarta.persistence.*
    javax.validation.*  -> jakarta.validation.*
    javax.servlet.*     -> jakarta.servlet.*
    javax.transaction.* -> jakarta.transaction.*
    javax.annotation.*  -> jakarta.annotation.*
    javax.inject.*      -> jakarta.inject.*

  Impact: every @Entity class, @Repository, @Service
  using these annotations needs import updated.
  Automated: OpenRewrite handles all of these.

BREAKING CHANGE 2: Hibernate 6 type system overhaul
  Scope: custom types, JSON columns, UUID columns

  Hibernate 5 (deprecated in H6, removed):
    @Type(type = "json")  // custom UserType
    @TypeDef(name="json", typeClass=JsonType.class)
    // io.hypersistence:hypersistence-utils-hibernate-55

  Hibernate 6 equivalents:
    // For JSON:
    @JdbcTypeCode(SqlTypes.JSON)   // column is JSON type
    private Map<String, Object> metadata;
    // Still works with hypersistence-utils-hibernate-60

    // For UUID:
    @JdbcTypeCode(SqlTypes.CHAR)  // store as varchar(36)
    private UUID externalId;
    // Default: UUID stored as binary in MySQL, uuid in PG

    // For custom types: implement UserType<T> (H6 interface)
    // H5: UserType (un-typed); H6: UserType<T> (typed)

BREAKING CHANGE 3: HQL/JPQL query changes
  Scope: less common; affects advanced HQL usage

  Removed: implicit join path from SELECT without FROM entry
    H5 (worked): SELECT e.department.name FROM Employee e
    H6 (works):  SELECT d.name FROM Employee e JOIN e.department d
    // Explicit join required in some cases

  Changed: some aggregate function syntax
  New: FILTER clause for conditional aggregation
  New: TREAT operator (was available but now standardized)
  Removed: legacy Hibernate-specific syntax not in JPA spec
```

---

### 🧪 Thought Experiment

**THE MIGRATION ORDER MATTERS:**

```
Wrong migration order (common mistake):
  1. Update pom.xml: spring-boot 2.7 -> 3.0
  2. Compile -> 500 errors (all javax.persistence.* not found)
  3. Panic: "Everything is broken"

Right migration order:
  1. First: upgrade Java 8 -> Java 17 (separate PR)
     Test: run all tests, deploy, confirm stable
  2. Then: upgrade Spring Boot 2.7.x -> 2.7.latest
     Apply any security patches
  3. Then: run OpenRewrite migration recipe
     Fixes: imports, @Type annotations, Spring XML configs
  4. Then: upgrade pom.xml boot version 2.7 -> 3.0
     Fix remaining compilation errors (from OpenRewrite misses)
  5. Run all tests; fix failures
  6. Deploy to staging; verify behavior

Each step is independently releasable.
The javax -> jakarta rename is ~95% automated by OpenRewrite.
The Hibernate type system changes (5%) require manual review.
```

---

### 🧠 Mental Model / Analogy

> Think of Hibernate 6 as a new engine model in the same car
> chassis. The steering wheel (JPA API: `@Entity`, `EntityManager`)
> looks and works the same. The gear shift (`@Transactional`,
> `@Query`) is in the same place. But the engine internals
> (query engine: SQM replaces old AST; type system rewritten)
> are completely different under the hood. You don't need to
> relearn driving (JPA fundamentals unchanged). But a few
> components around the engine changed: the type adapters
> (`@Type` -> `@JdbcTypeCode`), some under-hood wiring
> (`javax.*` package labels -> `jakarta.*` labels). The
> package rename is like replacing the car's badge from one
> marque to another: different logo, same car.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What changes and what doesn't (anyone):**
The import statements change: `javax.persistence.Entity` ->
`jakarta.persistence.Entity`. Everything else - `@Entity`,
`@Id`, `@Transactional`, Spring repositories - works exactly
the same. Automated tool fixes the imports.

**Level 2 - Dependency changes (junior):**
```xml
<!-- pom.xml Spring Boot 2 -> 3 -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <!-- Change this: -->
    <version>3.2.0</version>
</parent>

<!-- Requires Java 17: -->
<properties>
    <java.version>17</java.version>
</properties>

<!-- If using Hibernate Types (JSON etc.): -->
<!-- Spring Boot 2: -->
<dependency>
    <groupId>io.hypersistence</groupId>
    <artifactId>hypersistence-utils-hibernate-55</artifactId>
</dependency>

<!-- Spring Boot 3 (Hibernate 6): -->
<dependency>
    <groupId>io.hypersistence</groupId>
    <artifactId>hypersistence-utils-hibernate-60</artifactId>
</dependency>
<!-- Note: artifact ID contains Hibernate version -->
```

**Level 3 - Type system migration (mid):**
```java
// Spring Boot 2 / Hibernate 5: @Type for custom types
@Entity
public class Product {
    @Type(type = "json")  // REMOVED in H6
    @Column(columnDefinition = "json")
    private Map<String, Object> metadata;

    @Type(type = "uuid-char")  // REMOVED in H6
    private UUID externalRef;
}

// Spring Boot 3 / Hibernate 6: @JdbcTypeCode
@Entity
public class Product {
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "json")
    private Map<String, Object> metadata;

    @JdbcTypeCode(SqlTypes.CHAR)  // varchar(36) storage
    private UUID externalRef;
    // OR: just use UUID - Hibernate 6 maps natively
    // PostgreSQL: uuid type; MySQL: binary(16) or varchar(36)
}
```

**Level 4 - Custom UserType migration (senior):**
```java
// Hibernate 5 UserType (un-typed, raw):
public class MoneyUserType implements UserType {
    @Override
    public int[] sqlTypes() { return new int[]{Types.BIGINT}; }

    @Override
    public Class returnedClass() { return Money.class; }

    @Override
    public Object nullSafeGet(ResultSet rs,
        String[] names, SessionImplementor s,
        Object owner) throws SQLException {
        long cents = rs.getLong(names[0]);
        return Money.ofCents(cents);
    }

    @Override
    public void nullSafeSet(PreparedStatement st,
        Object value, int index, SessionImplementor s)
        throws SQLException {
        st.setLong(index,
            ((Money) value).toCents());
    }
    // + ~10 more methods (equals, hashCode, assemble...)
}

// Hibernate 6 UserType<T> (typed, fewer methods):
public class MoneyUserType implements UserType<Money> {
    @Override
    public int getSqlType() { return Types.BIGINT; }

    @Override
    public Class<Money> returnedClass() { return Money.class; }

    @Override
    public Money nullSafeGet(ResultSet rs,
        int position, SharedSessionContractImplementor s,
        Object owner) throws SQLException {
        long cents = rs.getLong(position);
        return Money.ofCents(cents);
    }

    @Override
    public void nullSafeSet(PreparedStatement st,
        Money value, int index,
        SharedSessionContractImplementor s)
        throws SQLException {
        st.setLong(index, value.toCents());
    }
    // + equals, hashCode (type-safe now)
}
```

**Level 5 - OpenRewrite automation (staff):**
```xml
<!-- pom.xml: add OpenRewrite plugin for automated migration -->
<plugin>
    <groupId>org.openrewrite.maven</groupId>
    <artifactId>rewrite-maven-plugin</artifactId>
    <version>5.20.0</version>
    <configuration>
        <activeRecipes>
            <recipe>
                org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_2
            </recipe>
        </activeRecipes>
    </configuration>
    <dependencies>
        <dependency>
            <groupId>org.openrewrite.recipe</groupId>
            <artifactId>rewrite-spring</artifactId>
            <version>5.7.0</version>
        </dependency>
    </dependencies>
</plugin>
```

```bash
# Run migration:
mvn rewrite:run
# Handles:
#   javax.persistence -> jakarta.persistence (all files)
#   javax.validation -> jakarta.validation
#   javax.servlet -> jakarta.servlet
#   Spring Boot 2 -> 3 config properties renames
#   Some Hibernate 5 -> 6 annotation changes
# Generates a diff; review before committing
```

---

### ⚙️ How It Works (Mechanism)

**HIBERNATE 6 QUERY ENGINE (SQM):**

```
Hibernate 5 query pipeline:
  HQL string -> HQL AST (Antlr2)
               -> SQL via HibernateEntityPersister
               -> plan cached as QueryPlanKey

Hibernate 6 query pipeline:
  HQL string -> SQM tree (Semantic Query Model, Antlr4)
               -> SQL AST (new internal representation)
               -> SQL string via SqmTranslator
               -> plan cached in QueryPlanCache

Benefits of SQM in H6:
  - Better type inference in queries
  - More accurate JPQL/HQL compliance
  - Supports: FILTER clause, improved TREAT,
    lateral subqueries, better pagination SQL
  - Cleaner error messages for invalid HQL

Breaking changes from H5 -> H6 SQM:
  - Some implicit join paths now require explicit JOIN
  - Some legacy HQL-only syntax removed
  - Query plan cache key changed: warm-up needed post deploy
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL MIGRATION CHECKLIST:**

```
Pre-migration:
  [ ] Java 17 upgrade complete and deployed
  [ ] Spring Boot 2.7.latest running in production
  [ ] All tests passing
  [ ] Baseline metrics captured (response times, DB query counts)

Step 1 - Automated migration:
  [ ] Add OpenRewrite plugin to pom.xml
  [ ] Run: mvn rewrite:run
  [ ] Review diff (OpenRewrite changes)
  [ ] Commit OpenRewrite changes

Step 2 - Manual fixes:
  [ ] Update Spring Boot version in pom.xml: 2.7 -> 3.2
  [ ] Update hypersistence-utils: hibernate-55 -> hibernate-60
  [ ] Fix @Type -> @JdbcTypeCode for JSON columns
  [ ] Fix custom UserType classes (implement UserType<T>)
  [ ] Fix @TypeDef annotations (remove; use @JdbcTypeCode)
  [ ] Review and fix HQL queries (if implicit join warnings)
  [ ] Update spring.jpa.* property renames (if any)

Step 3 - Test and validate:
  [ ] Run full test suite; fix failures
  [ ] Run integration tests (Testcontainers)
  [ ] Check N+1 behavior (H6 may change lazy loading behavior)
  [ ] Verify JSON column read/write (common breakage point)
  [ ] Verify UUID storage (binary vs varchar may change)

Step 4 - Deploy:
  [ ] Deploy to staging; run smoke tests
  [ ] Monitor: error rates, slow queries, connection pool
  [ ] Compare metrics to baseline
  [ ] Deploy to production with rollback plan ready
```

---

### 💻 Code Example

**Most common JSON column migration:**

```java
// BEFORE (Spring Boot 2 / Hibernate 5):
import org.hibernate.annotations.Type;
import org.hibernate.annotations.TypeDef;

@Entity
@TypeDef(name = "json",
    typeClass = JsonBinaryType.class)
public class Product {
    @Id @GeneratedValue
    private Long id;

    @Type(type = "json")
    @Column(columnDefinition = "jsonb")
    private Map<String, Object> attributes;
}

// AFTER (Spring Boot 3 / Hibernate 6):
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
public class Product {
    @Id @GeneratedValue
    private Long id;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private Map<String, Object> attributes;
    // No @TypeDef needed; Hibernate 6 handles JSON natively
    // For complex types: still use hypersistence-utils-hibernate-60
}
```

---

### ⚖️ Comparison Table

| Feature | Hibernate 5 / Spring Boot 2 | Hibernate 6 / Spring Boot 3 |
|---|---|---|
| Package | `javax.persistence` | `jakarta.persistence` |
| Java minimum | 8 | 17 |
| Custom types | `@Type(type="...")` + `@TypeDef` | `@JdbcTypeCode(SqlTypes.X)` |
| JSON support | Via `hypersistence-utils-hibernate-55` | Native + `hypersistence-utils-hibernate-60` |
| UUID support | `@Type(type="uuid-char")` | Native `UUID` type |
| Query engine | Antlr2-based HQL AST | SQM (Antlr4-based) |
| UserType API | `UserType` (untyped) | `UserType<T>` (typed) |
| PostgreSQL | `@Type(type="array")` for arrays | `@JdbcTypeCode(SqlTypes.ARRAY)` |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The migration is just changing import statements" | Import rename is the largest change by volume, but the Hibernate 6 type system changes and some HQL changes require manual attention. A project using `@Type(type="json")` extensively will need every such annotation changed with correct semantics, not just imports. |
| "OpenRewrite handles everything" | OpenRewrite handles ~90% (imports, config property renames, some boot-specific changes). The Hibernate 5 `@Type` -> `@JdbcTypeCode` migration requires per-case judgment (what SQL type to use, how UUID should be stored). Custom `UserType` implementations require manual rewrite. |
| "Hibernate 6 changes lazy loading behavior" | Partially true - Hibernate 6 changed how some associations are loaded (particularly for batching). In some cases, queries that loaded correctly in H5 may produce different SQL in H6. This should be validated by comparing SQL logs before and after migration. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: JSON Column Returns null After Migration**

**Symptom:** After Spring Boot 3 migration, entity fields
annotated with `@JdbcTypeCode(SqlTypes.JSON)` return `null`
when read from PostgreSQL `jsonb` columns, even though data
exists in the DB. No exception thrown.
**Root Cause:** The `@Column(columnDefinition = "jsonb")` is
needed to tell Hibernate the exact PostgreSQL type. Without it,
Hibernate may not correctly map between the `JsonB` JDBC type
and the Java `Map`. Additionally: the Jackson ObjectMapper used
by Hibernate's JSON type handling may not be able to deserialize
to the target generic type (e.g., `Map<String, CustomObject>`).
**Diagnosis:**
```sql
-- Verify data exists in DB:
SELECT id, attributes FROM product WHERE id=1;
-- Check columnDefinition matches actual DB type
```
```java
// Fix: explicit column definition:
@JdbcTypeCode(SqlTypes.JSON)
@Column(columnDefinition = "jsonb")  // required for PG jsonb
private Map<String, Object> attributes;

// For complex generic types: consider @Convert instead:
@Convert(converter = JsonAttributeConverter.class)
private Map<String, Object> attributes;
// AttributeConverter<Map<String,Object>, String> is explicit
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-057 - JPA Specification]] - the javax vs jakarta
  package naming and version history context
- [[JPH-051 - Converter and AttributeConverter]] - alternative
  to @Type annotations for custom type mapping

**Builds On This (learn these next):**
- [[JPH-058 - Hibernate Internals]] - new internals in Hibernate 6
  (SQM query engine details)

**Related:**
- [[JPH-001 - JPA Overview]] - JPA fundamentals unchanged across versions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ IMPORT RENAME  │ javax.persistence.* ->                  │
│                │ jakarta.persistence.*                   │
│                │ (all javax.* in JEE affected)           │
├────────────────┼─────────────────────────────────────────┤
│ TYPE SYSTEM    │ @Type(type="json") ->                   │
│                │ @JdbcTypeCode(SqlTypes.JSON)            │
│                │ @TypeDef removed entirely               │
├────────────────┼─────────────────────────────────────────┤
│ AUTOMATION     │ OpenRewrite: mvn rewrite:run            │
│                │ Handles: imports, config, some types    │
├────────────────┼─────────────────────────────────────────┤
│ JAVA MIN       │ Java 17 required for Spring Boot 3.x    │
├────────────────┼─────────────────────────────────────────┤
│ VALIDATE       │ Compare SQL logs before/after migration │
│                │ Check N+1 behavior, JSON columns, UUIDs │
├────────────────┼─────────────────────────────────────────┤
│ ONE-LINER      │ "Spring Boot 3 = Hibernate 6 +          │
│                │ jakarta.persistence. Three breaks:      │
│                │ imports, @Type, some HQL. ~90%          │
│                │ automated by OpenRewrite."              │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Package: `javax.persistence.*` (Spring Boot 2) -> `jakarta.persistence.*` (Spring Boot 3); automated
2. Type system: `@Type(type="json")` -> `@JdbcTypeCode(SqlTypes.JSON)` (manual); `@TypeDef` removed
3. Use OpenRewrite (`mvn rewrite:run`) to automate ~90%; manually fix custom types and UserType classes

**Interview one-liner:** Spring Boot 3 upgrade requires Hibernate 6 and Jakarta Persistence 3.
Three changes: (1) package rename - all `javax.persistence.*` becomes `jakarta.persistence.*` (OpenRewrite automates this);
(2) Hibernate 6 type system - `@Type`/`@TypeDef` removed, replaced by `@JdbcTypeCode(SqlTypes.X)`;
(3) some HQL syntax changes (implicit joins tightened). Requires Java 17 minimum.
OpenRewrite handles ~90%; custom `UserType` implementations need manual rewrite from untyped to typed `UserType<T>`.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Namespace migrations (package
renames, API renames) are a recurring pattern in software
ecosystems when organizational control changes hands: Java EE
(`javax.*`) -> Jakarta EE (`jakarta.*`), Python 2 -> Python 3
(`print` statement -> function), Angular 1 -> Angular 2+
(complete rewrite). The pattern for managing them is the same:
(1) automate what can be automated (OpenRewrite, 2to3 tools),
(2) manually review the 5-10% that can't be automated (type
system changes, behavior changes), (3) do it in phases not all
at once (Java 17 first, then Spring Boot 3), (4) validate
behavior not just compilation (SQL logs, integration tests).
The worst strategy: delay until the old version is EOL, then
migrate under security pressure. The best strategy: migrate
on your schedule when both versions are supported.

---

### 💡 The Surprising Truth

The Hibernate 6 type system rewrite was triggered by a single
design flaw in Hibernate 5's `UserType` interface: it used
raw types (`Object`) instead of generics, forcing casts
everywhere and making type errors runtime-only (not compile-time).
The H6 `UserType<T>` interface is the fix. But because
`UserType` was used by hundreds of third-party libraries
(Hypersistence Utils, Spring Data, custom types), the change
broke the entire custom type ecosystem, requiring every library
to release a "hibernate-60" artifact. This is why the
`hypersistence-utils-hibernate-55` -> `hypersistence-utils-hibernate-60`
artifact rename exists. The takeaway: a foundational interface
using raw types instead of generics creates a type-erasure
compatibility cliff that requires a major version bump to fix.
Generics in interfaces are not just style; they determine
how deeply breaking a future API cleanup must be.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **LIST** the three categories of breaking changes in
   Spring Boot 2 -> 3 migration (imports, type system, HQL)
2. **FIX** a `@Type(type="json")` annotation for Spring Boot 3
3. **RUN** an OpenRewrite migration and explain what it covers
4. **REWRITE** a Hibernate 5 `UserType` to Hibernate 6 `UserType<T>`
5. **SEQUENCE** the migration steps (Java 17 first, then Spring Boot 3)
6. **EXPLAIN** why `javax.*` was renamed to `jakarta.*`
   (trademark, not technical reasons)

---

### 🎯 Interview Deep-Dive

**Q1: Your team needs to upgrade from Spring Boot 2.7 to
Spring Boot 3.2. What is your migration plan and what
are the main risks?**
*Why they ask:* Tests migration planning and knowledge of actual
breaking changes.
*Strong answer includes:*
- Pre-requisite: upgrade to Java 17 FIRST (separate PR, validate)
- Phase 1: run OpenRewrite (`mvn rewrite:run`) to automate ~90% of changes
  (import renames, property renames, some annotation migrations)
- Phase 2: manually fix what OpenRewrite misses:
  - `@Type` -> `@JdbcTypeCode(SqlTypes.X)` for JSON, UUID, custom types
  - `@TypeDef` annotations: remove entirely
  - Custom `UserType` implementations: rewrite to `UserType<T>`
  - Update hypersistence-utils: `-hibernate-55` -> `-hibernate-60`
- Phase 3: run all tests; fix HQL query failures (implicit join syntax)
- Phase 4: deploy to staging; compare SQL logs to baseline (N+1 checks)
- Risks: JSON column mapping failures (silent null returns), UUID storage
  format changes (binary vs varchar), HQL syntax regressions,
  third-party library compatibility (need Hibernate 6 compatible versions)

**Q2: A colleague updated the Spring Boot version to 3.0 but
all entity fields annotated with `@Type(type="json")` are
now returning null. How would you diagnose and fix this?**
*Why they ask:* Tests practical H5->H6 migration knowledge.
*Strong answer includes:*
- Root cause: `@Type(type="json")` is a Hibernate 5 API, removed in H6
- Fix: replace with `@JdbcTypeCode(SqlTypes.JSON)`
- Ensure `@Column(columnDefinition = "jsonb")` is present for PostgreSQL
  (Hibernate 6 needs to know the exact DB column type for JSON handling)
- If using complex generic types: consider `@Convert` with explicit
  `AttributeConverter<T, String>` for more predictable behavior
- Run test: save entity with JSON field, reload, verify fields non-null
- Check: if still null - verify Jackson is on classpath (Hibernate 6
  JSON support uses Jackson for serialization; it's auto-detected)
