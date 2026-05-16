---
id: JPH-032
title: "JPA Auditing (@CreatedDate, @LastModifiedDate)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-011, JPH-012, JPH-013, JPH-026
used_by: JPH-049, JPH-054
related: JPH-041, JPH-051
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /jpa-hibernate/jpa-auditing-createddate-lastmodifieddate/
---

# JPH-032 - JPA Auditing (@CreatedDate, @LastModifiedDate)

⚡ **TL;DR** - Spring Data JPA auditing auto-populates
`createdAt`, `updatedAt`, `createdBy`, and `updatedBy`
fields on `@Entity` classes without manual service code.
Enable with `@EnableJpaAuditing` + `@EntityListeners(AuditingEntityListener.class)` + annotations on fields.
For who (user) auditing: implement `AuditorAware<T>`.
Never set these fields manually in application code.

| #032            | Category: JPA & Hibernate                                                     | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Entity, EntityManager, Persistence Context, Entity Lifecycle, @Transactional |                 |
| **Used by:**    | Hibernate Envers, JPA at Scale                                                |                 |
| **Related:**    | @Embedded/@Embeddable, @Converter/AttributeConverter                          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every service method that creates or updates an entity
must manually set `createdAt = LocalDateTime.now()` and
`updatedAt = LocalDateTime.now()`. If a developer forgets
to set `updatedAt` in one service method, the field is
never updated. There is no centralized enforcement.
Adding audit fields to 50 entities requires touching 50
entity classes and every service method that persists them.

**THE INVISIBLE BUG:**
`updatedAt` column shows `null` for records created by
a new batch import service - because the import service
developer didn't know about the audit field convention
and never set it. Data integrity is broken; support teams
cannot trace when records were created or last modified.

**THE SOLUTION:**
Spring Data's auditing infrastructure hooks into
Hibernate's entity lifecycle (`@PrePersist`, `@PreUpdate`
events) and automatically sets `@CreatedDate`, `@LastModifiedDate`,
`@CreatedBy`, and `@LastModifiedBy` fields before INSERT
and before UPDATE. Application code never needs to touch
these fields. They are always correct regardless of which
service method or batch job touches the entity.

---

### 📘 Textbook Definition

**JPA Auditing** (Spring Data JPA feature) automatically
populates designated fields on `@Entity` classes when
entities are created or modified. Uses JPA entity
lifecycle callbacks (`@PrePersist`, `@PreUpdate`) under
the hood via `AuditingEntityListener`.

**Key annotations:**

- `@CreatedDate`: populated on initial `persist()`; never updated again
- `@LastModifiedDate`: populated on `persist()` and every `merge()`/flush with dirty entity
- `@CreatedBy`: populated on `persist()`; captures auditor from `AuditorAware`
- `@LastModifiedBy`: populated on every modification; captures current auditor
- `@EntityListeners(AuditingEntityListener.class)`: registers the Spring Data listener
- `@EnableJpaAuditing`: Spring Boot configuration annotation (on `@Configuration` class)

**`AuditorAware<T>`**: interface you implement to provide
the current user identity for `@CreatedBy`/`@LastModifiedBy`.
Spring calls `getCurrentAuditor()` at each persist/update event.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Spring Data JPA auditing auto-fills
`createdAt`/`updatedAt`/`createdBy`/`updatedBy` on
every entity save/update without any manual code.

**One analogy:**

> JPA auditing is like an automatic timestamp stamp
> machine at a government office. Every document that
> passes through the machine gets stamped with the
> date and clerk ID without anyone explicitly asking
> for it. No document can leave without the timestamp.
> Application code (the clerk) never touches the stamp -
> it's applied automatically by the machine (auditing
> infrastructure).

**One insight:** JPA auditing uses JPA lifecycle
callbacks internally, which means it works for ALL
entry points that touch the entity - service methods,
batch jobs, event handlers - without requiring changes
to those callers. Adding audit fields to an existing
entity is a one-time change to the entity class only.

---

### 🔩 First Principles Explanation

**REQUIRED SETUP COMPONENTS:**

```
1. @EnableJpaAuditing on @Configuration class
   -> Registers AuditingEntityListener as a Spring bean
   -> Enables AuditorAware bean detection

2. @EntityListeners(AuditingEntityListener.class) on entity
   -> Registers the listener for JPA lifecycle events
   -> When Hibernate calls @PrePersist: listener sets
      @CreatedDate and @CreatedBy
   -> When Hibernate calls @PreUpdate: listener sets
      @LastModifiedDate and @LastModifiedBy

3. @CreatedDate, @LastModifiedDate on fields
   -> Supported types: LocalDateTime, LocalDate,
      ZonedDateTime, Instant, Date, Long (epoch millis)

4. AuditorAware<UserId> bean (for @CreatedBy/@LastModifiedBy)
   -> Spring calls getCurrentAuditor() on every event
   -> Return Optional.of(currentUser) from SecurityContext
```

**WHAT HAPPENS AT THE JPA LEVEL:**

```
em.persist(product):
  -> Hibernate fires @PrePersist on product
  -> AuditingEntityListener.touchForCreate(product)
     -> Sets @CreatedDate = now()
     -> Sets @LastModifiedDate = now()
     -> Sets @CreatedBy = auditorAware.getCurrentAuditor()
     -> Sets @LastModifiedBy = auditorAware.getCurrentAuditor()

em.flush() with dirty product:
  -> Hibernate fires @PreUpdate on product
  -> AuditingEntityListener.touchForUpdate(product)
     -> @CreatedDate: NOT changed (skip @CreatedDate on update)
     -> Sets @LastModifiedDate = now()
     -> @CreatedBy: NOT changed
     -> Sets @LastModifiedBy = auditorAware.getCurrentAuditor()
```

---

### 🧪 Thought Experiment

**THE @CreatedDate IMMUTABILITY GUARANTEE:**

```java
@CreatedDate
@Column(updatable = false)  // IMPORTANT: prevents UPDATE
private LocalDateTime createdAt;
```

**WITHOUT `updatable = false`:** If the entity is
ever merged (even without changes to `createdAt`),
Hibernate generates an UPDATE for ALL columns (including
`created_at`). The value would still be the original
value (AuditingEntityListener doesn't change it on
update), but the column is included in the UPDATE SQL,
which is a minor inefficiency and a risk if someone
manually overrides the field.

**WITH `updatable = false`:** Hibernate generates UPDATE
statements that explicitly exclude the `created_at`
column. This is the declarative guarantee: the column
CAN NEVER be changed by Hibernate after the initial INSERT.
This is the correct pattern for all `@CreatedDate` fields.

---

### 🧠 Mental Model / Analogy

> JPA auditing is like Git commit metadata. You never
> manually set the commit timestamp and author - Git
> records them automatically when you commit. `@CreatedDate`
> is the first commit timestamp (never changes). `@LastModifiedDate`
> is the latest commit timestamp (updated on every commit).
> `@CreatedBy` / `@LastModifiedBy` are the Git author/
> committer - populated from the current authenticated
> identity at commit time.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
JPA auditing automatically records WHEN an entity was
created and last changed, and WHO made the change.
You annotate fields with `@CreatedDate`, `@LastModifiedDate`,
etc., and Spring Data fills them in automatically.

**Level 2 - How to use it (junior developer):**

1. Add `@EnableJpaAuditing` to your `@SpringBootApplication`
   or a `@Configuration` class.
2. Add `@EntityListeners(AuditingEntityListener.class)` to your entity.
3. Annotate fields with `@CreatedDate`, `@LastModifiedDate`.
4. For user auditing: implement `AuditorAware<String>` to return the current username.

**Level 3 - How it works (mid-level engineer):**
`@EnableJpaAuditing` activates `AuditingEntityListener` which
registers on JPA's `@PrePersist` and `@PreUpdate` lifecycle
callbacks. On each event, it reads the `AuditorAware` bean
(if configured) and sets the annotated fields via reflection.
`@CreatedDate` is only set on `@PrePersist`; `@LastModifiedDate`
is set on both.

**Level 4 - Advanced patterns (senior/staff):**
Use a `@MappedSuperclass` `Auditable` base class to share
audit fields across all entities without repeating
`@EntityListeners` on each. Add `@Column(updatable = false)`
to `@CreatedDate` field to prevent accidental overwrite.
For multi-tenant systems: `AuditorAware` returns both
tenant ID and user ID; use a composite auditor type.
`@EnableJpaAuditing(auditorAwareRef = "myAuditorBean")`
for explicit bean reference when multiple beans exist.

**Level 5 - Architecture (distinguished engineer):**
Spring Data JPA auditing is limited to single-database
INSERT/UPDATE events. For distributed systems where the
same entity may be modified by multiple services (event
sourcing, CQRS), richer audit trails require a dedicated
audit log table or event store. Hibernate Envers (JPH-049)
provides full entity history tracking: every version of
every entity, not just current `createdAt`/`updatedAt`.
For compliance requirements (SOX, GDPR), Envers is more
appropriate than Spring Data auditing, which only captures
the current state's timestamps and user, not the full
change history.

---

### ⚙️ How It Works (Mechanism)

**SPRING DATA AUDITING EXECUTION FLOW:**

```java
// 1. Configuration class:
@Configuration
@EnableJpaAuditing
public class JpaConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(
            SecurityContextHolder.getContext()
                .getAuthentication())
            .map(Authentication::getName);
    }
}

// 2. Base auditing class (reuse across entities):
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseAuditEntity {

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(updatable = false)
    private String createdBy;

    @LastModifiedBy
    @Column
    private String updatedBy;

    // getters only - no setters to prevent manual override
}

// 3. Entity extends base:
@Entity
@Table(name = "products")
public class Product extends BaseAuditEntity {
    @Id @GeneratedValue
    private Long id;
    private String name;
    // Business fields only; audit fields inherited
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL LIFECYCLE WITH AUDITING:**

```java
// Service: no audit field management needed
@Service
@Transactional
public class ProductService {

    public Product createProduct(String name) {
        Product p = new Product();
        p.setName(name);
        productRepo.save(p);
        // createdAt: set by AuditingEntityListener at PrePersist
        // updatedAt: same
        // createdBy: "john" (from SecurityContext)
        // updatedBy: "john"
        return p;
    }

    public Product updatePrice(Long id, BigDecimal price) {
        Product p = productRepo.findById(id).orElseThrow();
        p.setPrice(price);
        // flush at method end:
        // updatedAt: set to now() by AuditingEntityListener at PreUpdate
        // updatedBy: current user from SecurityContext
        // createdAt: NOT changed (@Column(updatable=false))
        // createdBy: NOT changed
        return p;
    }
}

// Resulting SQL for update:
// UPDATE products SET name=?, price=?, updated_at=?,
// updated_by=? WHERE id=?
// (created_at, created_by excluded due to updatable=false)
```

---

### 💻 Code Example

**Example 1 - BAD: manual audit field management:**

```java
// BAD: manual - error-prone, repeated, easy to forget
@Transactional
public Product createProduct(ProductDto dto) {
    Product p = new Product();
    p.setName(dto.getName());
    p.setCreatedAt(LocalDateTime.now()); // manual
    p.setUpdatedAt(LocalDateTime.now()); // manual
    // What about createdBy? Forgot it!
    return productRepo.save(p);
}

// GOOD: use Spring Data JPA Auditing
// Entity extends BaseAuditEntity; no manual set needed
@Transactional
public Product createProduct(ProductDto dto) {
    Product p = new Product();
    p.setName(dto.getName());
    return productRepo.save(p);
    // createdAt, updatedAt, createdBy, updatedBy
    // all set automatically
}
```

**Example 2 - JPA Auditing with Instant (timezone-safe):**

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseAuditEntity {

    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt; // UTC timestamp; no TZ ambiguity

    @LastModifiedDate
    @Column
    private Instant updatedAt;

    // Instant stored as TIMESTAMP WITH TIMEZONE in PostgreSQL
    // Avoids LocalDateTime DST/timezone ambiguity in global apps
}
```

**Example 3 - AuditorAware for async/batch contexts:**

```java
@Component
public class SpringSecurityAuditorAware
        implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        // HTTP request context: get from Spring Security
        Authentication auth = SecurityContextHolder
            .getContext().getAuthentication();

        if (auth != null && auth.isAuthenticated()
            && !"anonymousUser".equals(
                auth.getPrincipal())) {
            return Optional.of(auth.getName());
        }
        // Batch job / scheduled context: no auth
        return Optional.of("system");  // fallback
    }
}
```

---

### ⚖️ Comparison Table

| Feature          | JPA Auditing (Spring Data)    | Hibernate Envers (JPH-049)      |
| ---------------- | ----------------------------- | ------------------------------- |
| Captures         | Current timestamps + user     | Full history of every version   |
| Storage          | In entity columns             | Separate audit table (\_AUD)    |
| Setup complexity | Simple (4 annotations)        | Moderate (@Audited on entity)   |
| Query history?   | No                            | Yes (find entity at revision N) |
| Use for          | Standard operational metadata | Compliance, undo, forensics     |

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                                                    |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`@EnableJpaAuditing` can be on any class"                                 | Technically yes, but if placed on a `@SpringBootTest` configuration, it applies only to tests. Best practice: place it on the main `@SpringBootApplication` class or a dedicated `@Configuration`.                                                         |
| "`@CreatedDate` is automatically immutable"                                | Without `@Column(updatable = false)`, Hibernate includes `created_at` in UPDATE statements. The value doesn't change (the listener doesn't touch it on updates) but it generates unnecessary SQL. Always add `updatable = false` to `@CreatedDate` fields. |
| "JPA Auditing works in `@Scheduled` methods"                               | The `AuditorAware` implementation must handle cases where there is no `SecurityContext` (scheduled tasks, async methods, batch jobs). Return `Optional.of("system")` or the job name as a fallback. Without a fallback, `@CreatedBy` may be `null`.        |
| "`@MappedSuperclass` handles `@EntityListeners` inheritance automatically" | `@EntityListeners` on a `@MappedSuperclass` IS inherited by subclass entities (JPA spec). However, this is a subtle JPA spec behavior. Explicitly adding `@EntityListeners` on the concrete entity is safer and more visible.                              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: @CreatedDate is null After Save**

**Symptom:** Entity is saved but `createdAt` field is
`null` in the database.
**Root Cause (most common):** `@EnableJpaAuditing` is
missing or placed on a test configuration that is not
active in production. Alternatively, `@EntityListeners(AuditingEntityListener.class)` is missing from the entity class.
**Diagnosis:**

```java
// Check @Configuration classes for @EnableJpaAuditing
// Check entity class for @EntityListeners
// Add debug: implement AuditingEntityListener and log touchForCreate
```

**Fix:** Add `@EnableJpaAuditing` to main application
config; add `@EntityListeners(AuditingEntityListener.class)`
to entity or base class.

---

**Failure Mode 2: @CreatedBy Returns null (No AuditorAware)**

**Symptom:** `created_by` column is always `null` even
though users are authenticated.
**Root Cause:** No `AuditorAware` bean configured, OR
the `AuditorAware` bean returns `Optional.empty()`.
**Fix:** Implement `AuditorAware<String>` bean and register
it. Ensure it handles unauthenticated contexts (batch,
system) with a fallback value.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-013 - Entity Lifecycle]] - auditing hooks use
  `@PrePersist` and `@PreUpdate` lifecycle callbacks
- [[JPH-026 - @Transactional]] - audit fields are set
  within the transaction boundary

**Builds On This (learn these next):**

- [[JPH-049 - Hibernate Envers]] - for full entity
  revision history beyond timestamps

**Related:**

- [[JPH-041 - @Embedded and @Embeddable]] - audit fields
  are often extracted into a reusable `@Embeddable`
  `AuditInfo` value object
- [[JPH-051 - @Converter and AttributeConverter]] -
  custom type converters for audit field types

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SETUP        │ @EnableJpaAuditing on @Configuration     │
│              │ @EntityListeners(AuditingEntityListener) │
│              │   on entity or @MappedSuperclass         │
├──────────────┼───────────────────────────────────────────┤
│ ANNOTATIONS  │ @CreatedDate, @LastModifiedDate,         │
│              │ @CreatedBy, @LastModifiedBy               │
├──────────────┼───────────────────────────────────────────┤
│ IMMUTABLE    │ @Column(updatable=false) on @CreatedDate │
│ CREATED_AT   │ and @CreatedBy to prevent accidental write│
├──────────────┼───────────────────────────────────────────┤
│ WHO AUDITING │ Implement AuditorAware<T> bean           │
│              │ Return current user from SecurityContext  │
│              │ + fallback "system" for batch/async       │
├──────────────┼───────────────────────────────────────────┤
│ BASE CLASS   │ @MappedSuperclass with all 4 audit fields │
│              │ Extend from all audited entities          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Spring Data JPA auditing auto-fills     │
│              │ createdAt/updatedAt/by via @PrePersist/  │
│              │ @PreUpdate. Enable: @EnableJpaAuditing +  │
│              │ @EntityListeners + field annotations."   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Requires three components: `@EnableJpaAuditing` config,
   `@EntityListeners(AuditingEntityListener.class)` on entity,
   and annotations on fields
2. Always add `@Column(updatable = false)` to `@CreatedDate`
   and `@CreatedBy` to make them truly immutable
3. Implement `AuditorAware<T>` for user auditing; provide
   a fallback for batch/async contexts with no SecurityContext

**Interview one-liner:** Spring Data JPA auditing auto-
populates `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`,
and `@LastModifiedBy` via JPA lifecycle callbacks
(`@PrePersist`/`@PreUpdate`). Enabled by `@EnableJpaAuditing`

- `@EntityListeners(AuditingEntityListener.class)`.
  Implement `AuditorAware` for user tracking. Always mark
  `@CreatedDate` with `@Column(updatable = false)`.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Audit metadata
(created/updated timestamps and users) should be
infrastructure concerns, not application concerns. Any
code path that creates or modifies data should get audit
metadata automatically without explicit code in each
path. This principle - infrastructure responsibility for
cross-cutting concerns - is AOP in practice. JPA auditing
is an AOP application: the advice (set audit fields)
fires on specific join points (persist/update events)
without any modification to the advised code (service
methods). The same principle applies to: request logging
middleware, security authentication, rate limiting,
distributed tracing context propagation - all enforced
at the infrastructure layer, invisible to business logic.

**Where else this pattern appears:**

- **MongoDB** - Spring Data MongoDB auditing: same
  `@EnableMongoAuditing` + `@CreatedDate` annotations;
  identical concept
- **ActiveRecord (Rails)** - `created_at` and `updated_at`
  columns added automatically; Rails fills them in on
  every save without developer code
- **Django** - `auto_now_add=True` for created,
  `auto_now=True` for updated on `DateTimeField`
- **Hibernate Envers** - extends auditing to full
  entity history, not just current timestamps

---

### 💡 The Surprising Truth

Spring Data JPA auditing does NOT work with bulk UPDATE
queries. When you run `@Modifying @Query("UPDATE Product p SET p.price = ...")`,
Hibernate executes the SQL directly without loading
entities into the persistence context and without firing
`@PreUpdate` lifecycle callbacks. The `AuditingEntityListener`
never runs. After a bulk update, the `updated_at` and
`updated_by` columns of affected rows remain unchanged.
This is consistent with Hibernate's behavior for all
entity lifecycle callbacks on bulk DML. For bulk operations
that must capture audit metadata: include `SET updated_at = CURRENT_TIMESTAMP, updated_by = :user` directly in the
bulk query SQL. This is an important exception to the
"Spring auditing handles everything" assumption.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **SET UP** complete JPA auditing with `@MappedSuperclass`,
   `@EnableJpaAuditing`, and `AuditorAware`
2. **EXPLAIN** why `@Column(updatable = false)` is needed
   on `@CreatedDate` and how to verify it works
3. **HANDLE** the edge case where `AuditorAware` is called
   in a batch/scheduled context with no authenticated user
4. **DIAGNOSE** why `@CreatedDate` is null after save
   (check `@EnableJpaAuditing` + `@EntityListeners` setup)
5. **EXPLAIN** why bulk UPDATE queries bypass JPA auditing
   and describe the workaround

---

### 🎯 Interview Deep-Dive

**Q1: How does Spring Data JPA auditing work under the hood?**
_Why they ask:_ Tests JPA lifecycle callback knowledge
and Spring Data internals.
_Strong answer includes:_

- `@EnableJpaAuditing` registers `AuditingEntityListener`
  as a Spring-managed JPA entity listener
- `@EntityListeners(AuditingEntityListener.class)` on the
  entity links the listener to JPA's `@PrePersist` and
  `@PreUpdate` lifecycle callbacks
- When Hibernate fires `@PrePersist` on entity persist:
  listener sets `@CreatedDate`, `@LastModifiedDate`,
  `@CreatedBy`, `@LastModifiedBy` via reflection
- When Hibernate fires `@PreUpdate` on dirty entity flush:
  listener updates only `@LastModifiedDate` and
  `@LastModifiedBy` (leaves `@CreatedDate`/`@CreatedBy` unchanged)
- AuditorAware.getCurrentAuditor() called at each event
  to get current user

**Q2: Does JPA auditing work with bulk UPDATE queries?
If not, how do you ensure audit fields are updated?**
_Why they ask:_ Tests understanding of JPA lifecycle
callbacks and bulk DML interaction.
_Strong answer includes:_

- NO - bulk UPDATE (`@Modifying @Query(...)`) executes SQL
  directly; JPA lifecycle callbacks (`@PreUpdate`) are
  NOT fired
- `AuditingEntityListener` is never invoked for bulk DML
- `updated_at` and `updated_by` columns remain stale
  after bulk UPDATE
- Fix: include audit columns explicitly in the bulk query:
  `UPDATE products SET price=:p, updated_at=NOW(),
updated_by=:user WHERE category=:cat`
- This also applies to Hibernate Envers - bulk DML
  operations are not tracked in audit tables
