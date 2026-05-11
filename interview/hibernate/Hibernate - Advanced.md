---
layout: default
title: "Hibernate - Advanced"
parent: "Hibernate"
grand_parent: "Interview Mastery"
nav_order: 4
permalink: /interview/hibernate/advanced/
topic: Hibernate
subtopic: Advanced
keywords:
  - Optimistic vs Pessimistic Locking
  - JPA Inheritance Mapping
  - JPQL vs Criteria API vs Native Queries
  - Schema Migration
difficulty_range: mixed
status: in-progress
version: 2
---

**Keywords covered in this file:**

- [Optimistic vs Pessimistic Locking](#optimistic-vs-pessimistic-locking)
- [JPA Inheritance Mapping](#jpa-inheritance-mapping)
- [JPQL vs Criteria API vs Native Queries](#jpql-vs-criteria-api-vs-native-queries)
- [Schema Migration](#schema-migration)

# Optimistic vs Pessimistic Locking

**TL;DR** - Optimistic locking uses version checks to detect conflicts at commit time; pessimistic locking acquires database locks upfront to prevent conflicts entirely - each trades throughput for safety.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT LOCKING:**
Two users view the same product page. Both see "stock: 10." User A buys 3 (stock should be 7). User B buys 5 (stock should be 5). Both read stock=10, subtract independently, and write back. Final stock: either 7 or 5, depending on who writes last. Two purchases deducted from 10, but only one deduction was applied. This is the **lost update** problem.

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### ⚙️ How It Works

```
OPTIMISTIC (version-based, conflict detected late):
  User A: READ product (version=1, stock=10)
  User B: READ product (version=1, stock=10)
  User A: UPDATE stock=7 WHERE version=1
          -> SUCCESS, version becomes 2
  User B: UPDATE stock=5 WHERE version=1
          -> FAIL (version is now 2)
          -> OptimisticLockException thrown

PESSIMISTIC (DB lock, conflict prevented early):
  User A: SELECT ... FOR UPDATE (acquires row lock)
  User B: SELECT ... FOR UPDATE (BLOCKS, waiting)
  User A: UPDATE stock=7, COMMIT (releases lock)
  User B: (unblocked) reads stock=7, UPDATE stock=2
```

---

### Comparison

| Aspect                 | Optimistic                      | Pessimistic                 |
| ---------------------- | ------------------------------- | --------------------------- |
| Mechanism              | Version column check            | Database row lock           |
| When conflict detected | At commit time                  | At read time (blocks)       |
| Throughput             | High (no locks held)            | Lower (locks block readers) |
| Conflict rate          | Good for LOW conflict           | Good for HIGH conflict      |
| Deadlock risk          | None                            | Yes (if multiple locks)     |
| Stale data             | Possible between read and write | No (lock held)              |
| JPA annotation         | `@Version`                      | `@Lock(PESSIMISTIC_WRITE)`  |

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 💻 Code Example

```java
// OPTIMISTIC LOCKING
@Entity
public class Product {
    @Id
    private Long id;
    private String name;
    private int stock;

    @Version  // JPA manages this automatically
    private int version;
}

// JPA auto-generates:
// UPDATE product SET stock=?, version=version+1
// WHERE id=? AND version=?
// If 0 rows updated -> OptimisticLockException

// Handling the exception
@Service
public class OrderService {
    @Retryable(
        value = OptimisticLockException.class,
        maxAttempts = 3)
    @Transactional
    public void purchaseProduct(
            Long productId, int quantity) {
        Product p = productRepo
            .findById(productId).orElseThrow();
        p.setStock(p.getStock() - quantity);
        productRepo.save(p);
        // If version conflict -> retry
    }
}

// PESSIMISTIC LOCKING
public interface ProductRepository
        extends JpaRepository<Product, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p "
        + "WHERE p.id = :id")
    Optional<Product> findByIdForUpdate(
        @Param("id") Long id);
}

@Transactional
public void purchaseProduct(
        Long productId, int quantity) {
    Product p = productRepo
        .findByIdForUpdate(productId)
        .orElseThrow();
    // Row is locked - no one else can modify
    p.setStock(p.getStock() - quantity);
    // Lock released at commit
}
```

---

### Decision Framework

```
Low conflict (< 5% of writes conflict):
  -> Optimistic locking (better throughput)

High conflict (> 20% of writes conflict):
  -> Pessimistic locking (fewer retries)

Financial transactions (must not lose updates):
  -> Pessimistic locking (stronger guarantee)

Read-heavy workload (99% reads):
  -> Optimistic locking (no lock contention)

Short transactions (< 100ms):
  -> Either works fine

Long transactions (seconds to minutes):
  -> Optimistic (don't hold DB locks that long)
```

---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Optimistic = `@Version` field, detect conflict at write time, retry on failure
2. Pessimistic = `SELECT FOR UPDATE`, block other writers, prevent conflict
3. Default to optimistic; switch to pessimistic only for high-conflict, short-lived transactions

**Interview one-liner:**
"I default to optimistic locking with @Version for most use cases because it provides better throughput - I switch to pessimistic locking with SELECT FOR UPDATE only when conflict rates are high and transactions are short, like inventory deductions during flash sales."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: A flash sale has 1000 users buying the same product simultaneously. Which locking strategy do you use and why?**

_Why they ask:_ Tests ability to reason about concurrency under extreme conditions.

**Answer:**
Pessimistic locking for the critical inventory deduction step. With 1000 concurrent buyers on the same product, optimistic locking would cause massive retry storms - 999 out of 1000 requests fail on first attempt, then 998 fail on retry, etc. This creates exponential database load.

With pessimistic locking: `SELECT ... FOR UPDATE` serializes access. Each buyer waits briefly, then reads the correct current stock and deducts. Total throughput is lower per second, but total success rate is much higher with zero wasted work.

Optimization: Use an atomic SQL update instead of read-then-write: `UPDATE product SET stock = stock - :qty WHERE id = :id AND stock >= :qty`. This is effectively pessimistic (row lock during UPDATE) but avoids the explicit SELECT FOR UPDATE round-trip.

**Q2: Your application throws OptimisticLockException frequently in production. How do you diagnose and fix it?**

_Why they ask:_ Tests real production debugging experience.

**Answer:**

1. **Identify the entity and frequency.** Log the entity type, ID, and stack trace. High frequency on a single entity = hot spot.

2. **Check for unnecessary writes.** If Hibernate's dirty checking triggers an update even when nothing changed (e.g., a setter called with the same value), the version increments unnecessarily. Use `@DynamicUpdate` to only update changed columns.

3. **Check transaction scope.** Long transactions increase the window for conflicts. Shorten the transaction: move read operations outside the transaction, do the write in a minimal transaction.

4. **Add retry logic.** For legitimate conflicts, use Spring Retry with `@Retryable(OptimisticLockException.class, maxAttempts = 3, backoff = @Backoff(delay = 100))`.

5. **Consider switching to pessimistic for hot entities.** If one entity gets 90% of the conflicts, use `PESSIMISTIC_WRITE` for that specific query.

---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Optimistic vs Pessimistic Locking. Otherwise remove this section.]

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# JPA Inheritance Mapping

**TL;DR** - JPA offers three strategies to map class hierarchies to database tables: Single Table (one table, discriminator column), Joined (one table per class, JOINs), and Table Per Class (one table per concrete class, UNION).

---

### 🔥 The Problem This Solves

Your domain has a `Payment` base class with `CreditCardPayment`, `BankTransferPayment`, and `CryptoPayment` subclasses. How do you store this in a relational database that has no concept of inheritance?

---

### Three Strategies

```
SINGLE TABLE (default, fastest queries):
+----+------+---------+--------+--------+------+
| id | type | amount  | card_no| iban   | addr |
+----+------+---------+--------+--------+------+
| 1  | CC   | 100.00  | 4111.. | NULL   | NULL |
| 2  | BT   | 250.00  | NULL   | DE89.. | NULL |
| 3  | CR   | 50.00   | NULL   | NULL   | 0x.. |
+----+------+---------+--------+--------+------+
  One table, NULL columns for non-applicable fields

JOINED (normalized, slower queries):
[payment]            [credit_card_payment]
+----+--------+      +----+---------+
| id | amount |      | id | card_no |
+----+--------+      +----+---------+
| 1  | 100.00 |      | 1  | 4111..  |
| 2  | 250.00 |
                     [bank_transfer_payment]
                     +----+--------+
                     | id | iban   |
                     +----+--------+
                     | 2  | DE89.. |
  JOIN required to load any entity

TABLE PER CLASS (no JOINs, no shared table):
[credit_card_payment]  [bank_transfer_payment]
+----+--------+------+ +----+--------+------+
| id | amount | card | | id | amount | iban |
+----+--------+------+ +----+--------+------+
| 1  | 100.00 | 4111 | | 2  | 250.00 | DE89 |
  UNION ALL needed for polymorphic queries
```

---

### Comparison

| Aspect              | Single Table                     | Joined               | Table Per Class  |
| ------------------- | -------------------------------- | -------------------- | ---------------- |
| Query speed         | Fastest (no JOINs)               | Slower (JOINs)       | Slow (UNION ALL) |
| Null columns        | Yes (many)                       | No                   | No               |
| Normalization       | Poor                             | Good                 | Good             |
| Schema evolution    | Easy (add column)                | Moderate (add table) | Hard             |
| Polymorphic query   | Fast                             | Moderate             | Slow             |
| NOT NULL constraint | Can't enforce on subclass fields | Can enforce          | Can enforce      |

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 💻 Code Example

```java
// SINGLE TABLE (recommended default)
@Entity
@Inheritance(strategy = SINGLE_TABLE)
@DiscriminatorColumn(name = "payment_type")
public abstract class Payment {
    @Id @GeneratedValue
    private Long id;
    private BigDecimal amount;
}

@Entity
@DiscriminatorValue("CC")
public class CreditCardPayment extends Payment {
    private String cardNumber;
    private String expiryDate;
}

@Entity
@DiscriminatorValue("BT")
public class BankTransferPayment extends Payment {
    private String iban;
    private String bic;
}

// JOINED
@Entity
@Inheritance(strategy = JOINED)
public abstract class Payment {
    @Id @GeneratedValue
    private Long id;
    private BigDecimal amount;
}
// Subclasses get their own tables with FK to payment

// TABLE PER CLASS
@Entity
@Inheritance(strategy = TABLE_PER_CLASS)
public abstract class Payment {
    @Id @GeneratedValue(strategy = TABLE)
    private Long id;  // Can't use IDENTITY
    private BigDecimal amount;
}
```

---

### Decision Framework

```
Few subclasses (2-5), query by base class often:
  -> SINGLE_TABLE (fastest, simplest)

Many subclass-specific fields, data integrity needed:
  -> JOINED (normalized, NOT NULL works)

Rarely query by base class, subclasses are independent:
  -> TABLE_PER_CLASS (avoid, usually worst option)

Default recommendation:
  -> SINGLE_TABLE unless you have a strong reason not to
```

---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. SINGLE_TABLE is the default and usually best - one table with discriminator column
2. JOINED normalizes but adds JOINs for every query on the base type
3. TABLE_PER_CLASS is almost never the right choice (UNION ALL is slow, can't use IDENTITY)

**Interview one-liner:**
"I default to SINGLE_TABLE inheritance for simplicity and performance, accepting NULL columns as the trade-off - I only switch to JOINED when I have many subclass-specific columns that need NOT NULL constraints and polymorphic queries are infrequent."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for JPA Inheritance Mapping. Otherwise remove this section.]

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# JPQL vs Criteria API vs Native Queries

**TL;DR** - JPQL is HQL-like object-oriented queries, Criteria API builds type-safe queries programmatically, and native SQL gives full database-specific control - choose based on query complexity and dynamism.

---

### Comparison

| Aspect          | JPQL                   | Criteria API              | Native SQL            |
| --------------- | ---------------------- | ------------------------- | --------------------- |
| Syntax          | String-based, SQL-like | Java API, builder pattern | Raw SQL string        |
| Type safety     | No (strings)           | Yes (metamodel)           | No                    |
| Dynamic queries | Messy concatenation    | Clean builder pattern     | Messy concatenation   |
| DB portability  | Yes (JPA abstracts)    | Yes                       | No (DB-specific)      |
| Complex queries | Good for simple/medium | Good for dynamic filters  | Best for complex      |
| Learning curve  | Low (SQL-like)         | High (verbose API)        | Low (if you know SQL) |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
[TODO: Concrete pain scenario. 2-4 sentences.]

**THE BREAKING POINT:**
[TODO: Specific failure. 1-2 sentences.]

**THE INVENTION MOMENT:**
"This is exactly why JPQL vs Criteria API vs Native Queries was created."

**EVOLUTION:**
[TODO: predecessor -> current form -> future.]

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 💻 Code Example

```java
// JPQL: Simple, readable, best for static queries
@Query("SELECT o FROM Order o "
    + "WHERE o.status = :status "
    + "AND o.createdAt > :since")
List<Order> findByStatusSince(
    @Param("status") String status,
    @Param("since") LocalDateTime since);

// CRITERIA API: Type-safe, best for dynamic queries
public List<Order> findOrders(OrderFilter filter) {
    CriteriaBuilder cb =
        em.getCriteriaBuilder();
    CriteriaQuery<Order> cq =
        cb.createQuery(Order.class);
    Root<Order> root = cq.from(Order.class);

    List<Predicate> predicates = new ArrayList<>();
    if (filter.getStatus() != null) {
        predicates.add(cb.equal(
            root.get("status"),
            filter.getStatus()));
    }
    if (filter.getMinAmount() != null) {
        predicates.add(cb.greaterThan(
            root.get("amount"),
            filter.getMinAmount()));
    }
    cq.where(predicates.toArray(new Predicate[0]));
    return em.createQuery(cq).getResultList();
}

// NATIVE SQL: Full DB power, best for complex/specific
@Query(value = "SELECT * FROM orders o "
    + "WHERE o.status = :status "
    + "AND o.created_at > NOW() - INTERVAL '7 days' "
    + "ORDER BY o.amount DESC "
    + "LIMIT 100",
    nativeQuery = true)
List<Order> findRecentHighValue(
    @Param("status") String status);
```

---

### Decision Guide

```
Static query, few parameters:
  -> JPQL (simple, readable)

Dynamic query with optional filters:
  -> Criteria API (type-safe, no string concat)
  -> Or: Spring Data Specifications

Complex query with DB-specific features:
  -> Native SQL (window functions, CTEs, hints)

Reporting/analytics:
  -> Native SQL (performance matters most)
```

---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. JPQL for simple static queries, Criteria API for dynamic filter queries, Native SQL for complex/DB-specific
2. Never concatenate user input into JPQL or native queries - always use parameters (`:paramName`)
3. Spring Data Specifications wraps Criteria API for cleaner dynamic queries

**Interview one-liner:**
"I use JPQL for simple static queries, Criteria API or Spring Data Specifications for dynamic filter-based queries, and native SQL only for complex DB-specific operations like window functions - always with parameterized queries for security."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for JPQL vs Criteria API vs Native Queries. Otherwise remove this section.]

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Schema Migration (Flyway / Liquibase)

**TL;DR** - Schema migration tools version-control your database schema changes, applying them in order across all environments - Flyway uses SQL scripts, Liquibase uses XML/YAML/JSON changesets.

---

### 🔥 The Problem This Solves

Without schema migration: developer A adds a column locally, developer B doesn't know. Production schema drifts from staging. Deploying requires a manual SQL script run by a DBA. Rolling back a bad migration means writing reverse SQL by hand. Nobody knows what schema version production is on.

---

### Flyway vs Liquibase

| Aspect           | Flyway                 | Liquibase             |
| ---------------- | ---------------------- | --------------------- |
| Migration format | SQL scripts            | XML/YAML/JSON/SQL     |
| Philosophy       | Convention-over-config | Flexible, explicit    |
| Rollback         | Manual (write undo)    | Auto-generated (some) |
| Diff tool        | No                     | Yes (compare DBs)     |
| Learning curve   | Very low               | Moderate              |
| Spring Boot      | Auto-configured        | Auto-configured       |
| Best for         | Most projects          | Complex multi-DB      |

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example (Flyway)

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- V2__add_phone_to_users.sql
ALTER TABLE users
    ADD COLUMN phone VARCHAR(20);

-- V3__create_orders_table.sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING'
);
```

```yaml
# application.yml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
```

**Naming convention:** `V{version}__{description}.sql`

- `V1__create_users.sql` - versioned migration
- `R__seed_data.sql` - repeatable migration

---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Flyway: SQL-based, convention-driven, simplest for most Spring Boot projects
2. Never modify an already-applied migration - create a new one
3. Spring Boot auto-runs migrations on startup - just drop SQL files in `db/migration`

**Interview one-liner:**
"I use Flyway for database schema versioning - SQL migration scripts named V1\_\_description.sql run automatically on Spring Boot startup, ensuring every environment has the same schema without manual intervention."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Schema Migration (Flyway / Liquibase). Otherwise remove this section.]

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

