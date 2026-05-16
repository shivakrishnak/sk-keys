---
id: JPH-010
title: JPA Interview Preparation Guide
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-001, JPH-002, JPH-003, JPH-004, JPH-005
used_by: JPH-011, JPH-012, JPH-013, JPH-014
related: JPH-015, JPH-016, JPH-029
tags:
  - java
  - database
  - jpa
  - interview
  - guide
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /jpa-hibernate/jpa-interview-preparation-guide/
---

# JPH-010 - JPA Interview Preparation Guide

⚡ **TL;DR** - A synthesis of the most frequently asked
JPA/Hibernate interview questions, organised by difficulty
tier and topic cluster. Use this to audit gaps and
prioritise study depth.

| #010            | Category: JPA & Hibernate                                                          | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | ORM Mismatch, What is ORM, JPA vs JDBC, Hibernate as JPA Impl, JPA Ecosystem Map   |                 |
| **Used by:**    | EntityManager, Persistence Context, Entity Lifecycle, JPQL                         |                 |
| **Related:**    | CrudRepository vs JpaRepository, Spring Data JPA Auto-configuration, JDBC Template |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
JPA interview preparation without a guide means studying
topics in arbitrary order - memorising annotations without
understanding mechanics, or understanding one fetch strategy
without knowing how it interacts with the persistence
context. Interviewers at senior level test depth of
understanding, not breadth of annotation knowledge.

**THE BREAKING POINT:**
JPA has 61+ concepts in this dictionary alone. Without a
prioritised map, candidates spend days on `@Table` and
`@Column` while missing N+1 queries (top 3 asked question)
or transaction propagation (tested at every senior role).

**THE INVENTION MOMENT:**
This guide organises JPH concepts by (1) interview frequency,
(2) knowledge dependency order, and (3) depth required per
seniority level. It maps each topic to the type of question
asked and the specific trap interviewers set.

---

### 📘 Textbook Definition

A **JPA interview preparation guide** is a structured
study map for Jakarta Persistence API concepts, organised
by frequency of appearance in technical interviews, depth
of expected answer per seniority level, and conceptual
dependencies (what you must understand before what).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Know these topics in this order, at this depth,
and you will pass JPA questions at junior through staff level.

**One analogy:**

> Preparing for JPA interviews without a guide is like
> packing for a trip without knowing the destination.
> This guide is the itinerary: what to pack (topics),
> in what order (dependency chain), and what level of
> detail to prepare (junior vs. senior depth).

**One insight:** The single most asked JPA question at
mid-level and above is the N+1 problem. Every other topic
is secondary in frequency. If you know only one thing
deeply, know N+1.

---

### 🔩 First Principles Explanation

**THE JPA INTERVIEW TOPIC HIERARCHY:**

JPA interview questions cluster into five zones:

```
Zone 1 - Fundamentals (asked at ALL levels)
  ORM concept, @Entity requirements, @Id strategies,
  persistence context, entity states

Zone 2 - Querying (asked at mid-level+)
  JPQL, Criteria API, N+1 detection and fix,
  @Query in Spring Data, projections

Zone 3 - Relationships (asked at mid-level+)
  @OneToMany, @ManyToOne, cascade types, orphanRemoval,
  fetch strategies (LAZY vs EAGER), bidirectional sync

Zone 4 - Transactions (asked at senior level)
  @Transactional propagation, rollback rules,
  optimistic vs. pessimistic locking, @Version

Zone 5 - Performance (asked at senior/staff level)
  Second-level cache, batch inserts, connection pool,
  Hibernate statistics, query plan cache
```

**SENIORITY DEPTH MAP:**

| Level  | Expected depth                                      | Traps                                                           |
| ------ | --------------------------------------------------- | --------------------------------------------------------------- |
| Junior | Can describe concept + basic usage                  | Confusing @Transient with Java `transient`                      |
| Mid    | Can trace mechanism + failure modes                 | LAZY vs EAGER in practice, N+1                                  |
| Senior | Can compare trade-offs + diagnose production issues | Transaction propagation, optimistic lock conflict               |
| Staff  | Can design persistence architecture                 | Cache invalidation, multi-datasource, schema migration strategy |

---

### 🧪 Thought Experiment

**THE INTERVIEW SIMULATION:**
You are asked: "Explain the N+1 problem in JPA."

**JUNIOR answer (insufficient at mid-level+):**
"It's when you load a list and each item triggers an extra
query."

**MID-LEVEL answer (passes mid-level):**
"N+1 occurs with `@OneToMany(fetch=LAZY)` when iterating
through N parent entities and each child access triggers a
separate SELECT. You detect it with Hibernate statistics or
`spring.jpa.show-sql=true`. You fix it with `JOIN FETCH`
in JPQL or `@EntityGraph`."

**SENIOR answer (distinguishes senior candidates):**
"N+1 is a symptom, not the root cause. The root cause is
mismatched fetch strategy for the query's access pattern.
`JOIN FETCH` fixes N+1 but creates a Cartesian product
problem when joining multiple collections simultaneously.
`@EntityGraph` fixes N+1 per use case without changing
the entity's default fetch type. For reporting queries,
use projections (DTOs via `@Query`) to avoid loading
entities at all - this eliminates both N+1 and dirty
checking overhead."

**THE INSIGHT:** Depth of the N+1 answer signals the
candidate's actual production experience more reliably
than any other single question.

---

### 🧠 Mental Model / Analogy

> Preparing for JPA interviews is like training for
> a decathlon rather than a sprint. You need minimum
> competence in every event, but the order to train
> and the depth per event matters:
>
> 1. Fundamentals (sprinting) - everyone's tested on these
> 2. Querying/N+1 (javelin) - mid-level gateway question
> 3. Transactions (pole vault) - senior-level discriminator
> 4. Performance tuning (10,000m) - staff-level depth

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Topic Map (start here):**
Study in this order: ORM concept -> @Entity -> @Id ->
EntityManager -> Entity lifecycle -> @OneToMany/@ManyToOne ->
LAZY vs EAGER -> N+1 detection/fix -> @Transactional ->
Spring Data JPA -> second-level cache.

**Level 2 - Question Frequency (junior preparation):**
Most asked by frequency:

1. What is the N+1 problem? How do you fix it?
2. Difference between `persist()`, `merge()`, `detach()`
3. LAZY vs EAGER fetch - when to use each?
4. What is the persistence context / first-level cache?
5. `@OneToMany(mappedBy=...)` vs `@JoinColumn` - what is the difference?

**Level 3 - Mechanism Depth (mid-level preparation):**
For each of the top 5, explain:

- What Hibernate does internally
- What SQL is generated
- What breaks and why
- How to diagnose from logs

**Level 4 - Design Trade-offs (senior preparation):**
For each topic, know:

- When the default choice is wrong
- Three real production failure modes
- Alternatives and their trade-offs
- How the choice interacts with transactions and caching

**Level 5 - Architecture Decisions (staff preparation):**
Be able to answer:

- How would you design the persistence layer for
  a 100-table schema in a microservices architecture?
- How do you handle schema migration with zero downtime?
- What caching strategy would you apply across a
  cluster of 10 application nodes?
- How do you prevent N+1 in a Spring Data JPA repository
  layer used by 20 service classes?

---

### ⚙️ How It Works (Mechanism)

**INTERVIEW TOPIC DEPENDENCY GRAPH:**

```
JPH-001 ORM Mismatch
  |
  v
JPH-002 What is ORM <- core, learn first
  |
  v
JPH-003 JPA vs JDBC <- context
  |
  v
JPH-004 Hibernate as JPA Implementation
  |
  +---> JPH-006 @Entity
  |         |
  |         +---> JPH-007 @Id
  |         |       |---> JPH-008 @Table/@Column
  |         |
  |         +---> JPH-011 EntityManager
  |                   |
  |                   +---> JPH-012 Persistence Context
  |                   |---> JPH-013 Entity Lifecycle
  |
  +---> JPH-014 JPQL
  |         |
  |         +---> JPH-020 N+1 Problem  <-- KEY
  |         |---> JPH-021 JOIN FETCH
  |         |---> JPH-023 @EntityGraph
  |
  +---> JPH-017 @OneToMany / @ManyToOne
            |
            +---> JPH-018 Cascade Types
            |---> JPH-019 Fetch LAZY/EAGER
            |---> JPH-024 Bidirectional Sync
            |
            +---> JPH-029 @Transactional
                      |
                      +---> JPH-038 Optimistic Lock
                      |---> JPH-039 Pessimistic Lock
                      |
                      +---> JPH-043 Second-Level Cache
```

---

### 🔄 The Complete Picture - End-to-End Flow

**STUDY PLAN - 2 WEEKS:**

```
Week 1 - Foundations
  Day 1-2: JPH-001 to JPH-005 (ORM, JPA overview)
  Day 3-4: JPH-006 to JPH-009 (@Entity, @Id, @Column, Config)
  Day 5-6: JPH-011 to JPH-013 (EntityManager, PersistenceCtx)
  Day 7:   JPH-014 (JPQL), practice queries

Week 2 - Depth
  Day 8-9: JPH-017 to JPH-019 (relationships, fetch)
  Day 10:  JPH-020 to JPH-023 (N+1, fixes)
  Day 11:  JPH-029, JPH-038-039 (@Transactional, locking)
  Day 12:  JPH-015 to JPH-016 (Spring Data JPA)
  Day 13:  JPH-043 to JPH-045 (caching)
  Day 14:  Mock interview questions (review this guide)
```

**TOP 15 INTERVIEW QUESTIONS BY FREQUENCY:**

| #   | Question                                                          | Depth Required | JPH Entry |
| --- | ----------------------------------------------------------------- | -------------- | --------- |
| 1   | What is the N+1 problem? How to fix it?                           | Senior         | JPH-020   |
| 2   | LAZY vs EAGER fetch - trade-offs?                                 | Mid            | JPH-019   |
| 3   | `persist()` vs `merge()` vs `save()` differences?                 | Mid            | JPH-011   |
| 4   | What is the persistence context / first-level cache?              | Mid            | JPH-012   |
| 5   | `@OneToMany(mappedBy=)` vs `@JoinColumn`?                         | Mid            | JPH-017   |
| 6   | How does dirty checking work?                                     | Senior         | JPH-012   |
| 7   | When would you use native SQL over JPQL?                          | Mid            | JPH-033   |
| 8   | Explain `@Transactional` propagation types                        | Senior         | JPH-029   |
| 9   | Optimistic vs pessimistic locking?                                | Senior         | JPH-038   |
| 10  | What is `CascadeType.ALL` and when is it dangerous?               | Senior         | JPH-018   |
| 11  | How does Spring Data's `save()` decide persist vs merge?          | Mid            | JPH-016   |
| 12  | What is the difference between `@Repository` and `JpaRepository`? | Junior         | JPH-016   |
| 13  | How would you tune JPA for bulk inserts?                          | Senior         | JPH-009   |
| 14  | What is the second-level cache in Hibernate?                      | Senior         | JPH-043   |
| 15  | How do you prevent LazyInitializationException?                   | Mid            | JPH-019   |

---

### 💻 Code Example

**Pattern 1 - N+1 Detection and Fix (most asked):**

```java
// BAD: N+1 - 1 SELECT for orders + N SELECTs
//            for each order's items
List<Order> orders =
    em.createQuery("SELECT o FROM Order o",
                   Order.class)
      .getResultList();

for (Order o : orders) {
    // Each call triggers a new SELECT
    o.getItems().size();
}

// GOOD: JOIN FETCH eliminates N+1
List<Order> orders =
    em.createQuery(
        "SELECT DISTINCT o FROM Order o " +
        "LEFT JOIN FETCH o.items",
        Order.class)
      .getResultList();
// 1 SELECT with JOIN - items loaded upfront
```

**Pattern 2 - Entity State Transitions:**

```java
// NEW -> MANAGED
Product p = new Product("Widget");
em.persist(p);  // p is now MANAGED; id assigned

// MANAGED -> DETACHED
em.detach(p);   // p is now DETACHED; changes ignored

// DETACHED -> MANAGED (merge returns new managed copy)
Product managed = em.merge(p);
// p is STILL detached; managed is the tracked copy

// MANAGED -> REMOVED
em.remove(managed); // DELETE queued at flush
```

**Pattern 3 - @Transactional trap (tested at senior level):**

```java
// BAD: calling @Transactional method within same bean
@Service
public class OrderService {

    @Transactional
    public void processOrder(Long id) {
        // Calls self - Spring proxy NOT invoked
        // @Transactional on createInvoice is IGNORED
        createInvoice(id);  // no new transaction!
    }

    @Transactional(
        propagation = Propagation.REQUIRES_NEW)
    public void createInvoice(Long id) {
        // Expects a NEW transaction
        // Gets processOrder's transaction instead
    }
}

// GOOD: inject a separate bean or use
// ApplicationContext self-injection
@Service
public class OrderService {
    @Autowired
    private InvoiceService invoiceService;

    @Transactional
    public void processOrder(Long id) {
        // Spring proxy IS invoked - new transaction
        invoiceService.createInvoice(id);
    }
}
```

---

### ⚖️ Comparison Table

**Answer Quality by Question and Level:**

| Question          | Junior answer                     | Senior answer                                                                                                                                                                            |
| ----------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| N+1 problem       | "Load list, N child queries fire" | "Symptom of fetch mismatch; fix with JOIN FETCH or @EntityGraph; Cartesian product danger with multiple collections; use projections for reporting"                                      |
| LAZY vs EAGER     | "LAZY = load on demand"           | "LAZY is default for collections, EAGER is default for @ManyToOne; EAGER can cause N+1 with JPQL without JOIN; OSIV determines LAZY accessibility outside transaction"                   |
| dirty checking    | "JPA auto-saves changes"          | "Hibernate takes a snapshot at load; at flush, field-by-field comparison via bytecode enhancement or reflection; snapshot memory doubles with large result sets"                         |
| first-level cache | "Session-level cache"             | "Identity map within EntityManager session; `find()` uses it; JPQL bypasses it; detach() removes entity from it; clear() empties it; critical for preventing duplicate entity instances" |

---

### ⚠️ Common Misconceptions

| Misconception                                                        | Reality                                                                                                                                                                                                                        |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "EAGER fetch is safer because you avoid LazyInitializationException" | EAGER on collections causes Cartesian products with JPQL (unless JOIN FETCH is used), leading to N+1 at the query level. LAZY with explicit fetch strategies is almost always the correct design.                              |
| "`CascadeType.ALL` is the safe default"                              | `CascadeType.ALL` includes `REMOVE`, which cascades deletes. An unintended cascade delete can wipe child records. Use specific cascade types (`PERSIST`, `MERGE`) unless full cascade including delete is explicitly required. |
| "Spring Data's `repository.save()` always does an INSERT"            | `save()` calls `isNew()` - if the entity has a null/0 ID it calls `persist()` (INSERT); if non-null it calls `merge()` (SELECT + potential UPDATE). For entities with pre-assigned UUIDs, every `save()` triggers a SELECT.    |
| "`@Transactional` on a private method works in Spring"               | Spring's `@Transactional` is implemented via a proxy subclass; private methods are not overriddable and the proxy cannot intercept them. The `@Transactional` annotation on a private method is silently ignored.              |
| "The second-level cache always improves performance"                 | The second-level cache improves read performance for frequently accessed, rarely changing entities. For frequently written entities, cache invalidation overhead and stale read risk can make performance worse than no cache. |

---

### 🚨 Failure Modes & Diagnosis

**Interview-Critical Failure Modes to Know:**

**Failure Mode 1: LazyInitializationException**

```
org.hibernate.LazyInitializationException:
failed to lazily initialize a collection of role:
com.example.Order.items: could not initialize
proxy - no Session
```

Root cause: accessing a `LAZY` collection after the session
is closed (outside `@Transactional` scope or with OSIV
disabled). Fix: `JOIN FETCH` in the query, `@EntityGraph`,
or `@Transactional` on the caller.

**Failure Mode 2: TransactionRequiredException**

```
javax.persistence.TransactionRequiredException:
No transactional EntityManager available
```

Root cause: calling `em.persist()` / `em.merge()` outside a
transaction. Fix: add `@Transactional` to the method or use
Spring Data repository which handles transactions.

**Failure Mode 3: OptimisticLockException**

```
org.hibernate.StaleObjectStateException:
Row was updated or deleted by another transaction
(or unsaved-value mapping was incorrect)
```

Root cause: Two concurrent transactions read the same entity;
one commits first; the second's `@Version` check fails.
Fix: retry the transaction, or merge the conflicting changes
at the application layer.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-001 - The Object-Relational Mismatch Problem]] -
  why JPA exists at all
- [[JPH-002 - What is ORM (Object-Relational Mapping)]] -
  ORM fundamentals
- [[JPH-004 - Hibernate as JPA Implementation]] -
  the engine behind every JPA feature

**Builds On This (learn these next):**

- [[JPH-011 - EntityManager]] - the core API; must know
  deeply for all senior JPA questions
- [[JPH-012 - Persistence Context]] - the mechanism behind
  dirty checking and identity map
- [[JPH-020 - N+1 Problem]] - the #1 interview question

**Alternatives / Comparisons:**

- [[JPH-015 - CrudRepository and JpaRepository]] - Spring
  Data JPA interview questions are the most asked practical
  questions in Spring Boot roles
- [[JPH-029 - @Transactional]] - transaction questions
  are the top discriminator between junior and senior

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOP 5 INTERVIEW QUESTIONS                                │
├──────────────────────────────────────────────────────────┤
│ 1. N+1 problem: cause, detection, fix (JOIN FETCH /     │
│    @EntityGraph), Cartesian product danger              │
│                                                          │
│ 2. LAZY vs EAGER: defaults, OSIV, LazyInitException,    │
│    when each causes problems                            │
│                                                          │
│ 3. persist() vs merge() vs save(): state transitions,   │
│    what SQL each generates, Spring Data isNew()         │
│                                                          │
│ 4. Persistence context: identity map, dirty checking,   │
│    flush modes, session scope                           │
│                                                          │
│ 5. @Transactional: propagation types, self-invocation  │
│    trap, rollback rules, checked exception gotcha       │
└──────────────────────────────────────────────────────────┘
```

**Study priority order (if time is limited):**

1. N+1 + JOIN FETCH + @EntityGraph (JPH-020, JPH-021, JPH-023)
2. EntityManager + Persistence Context (JPH-011, JPH-012)
3. @OneToMany/@ManyToOne + fetch (JPH-017, JPH-019)
4. @Transactional + propagation (JPH-029)
5. Spring Data save() / isNew() (JPH-016)

**Interview one-liner:** The most discriminating JPA interview
question is N+1: junior candidates describe it, mid-level
candidates fix it with JOIN FETCH, senior candidates explain
the Cartesian product trade-off, and staff candidates
design a repository layer that prevents it by default
using projections and EntityGraph specifications.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Deep interview preparation
is not memorisation - it is building a connected mental model
where each concept links to its mechanism, failure modes,
and trade-offs. The candidate who can trace a LazyInitializationException
from HTTP request through the Spring proxy, through the
Hibernate session lifecycle, to the missing transaction
boundary - and then explain three ways to fix it with
different trade-offs - demonstrates production experience
that cannot be faked by memorising definitions.

**The meta-skill being tested:** Every JPA interview
question at senior level tests the same underlying ability:
can you reason about what SQL is generated, what the database
does, how the session state affects the outcome, and what
breaks under concurrent load? The annotation is the surface;
the session lifecycle is the substance.

---

### 💡 The Surprising Truth

The single question that most reliably separates senior JPA
candidates from mid-level is not N+1 (most people know it)
but the self-invocation `@Transactional` trap: calling an
`@Transactional` method from within the same bean bypasses
the Spring proxy and silently ignores the transaction
annotation. Fewer than 30% of mid-level candidates who
pass the N+1 question can explain this correctly. If you
understand proxy-based AOP interception and why self-calls
bypass it, you demonstrate a depth of Spring internals that
interviewers value highly.

---

### ✅ Mastery Checklist

**You are interview-ready at senior level when you can:**

1. **EXPLAIN** the N+1 problem, trace the SQL it generates,
   and describe three fixes (JOIN FETCH, @EntityGraph, DTO
   projection) with the trade-off of each
2. **TRACE** the lifecycle of a `@Transactional` method call
   through a Spring proxy including what happens on checked
   exception, unchecked exception, and normal return
3. **DESCRIBE** the persistence context identity map,
   dirty checking mechanism, and how `clear()` and
   `detach()` affect memory and behaviour
4. **COMPARE** optimistic locking (`@Version`) and
   pessimistic locking (`PESSIMISTIC_WRITE`) and state
   three scenarios where each is the correct choice
5. **DESIGN** a Spring Data JPA repository layer that
   prevents N+1 by default using projections and
   `@EntityGraph` specifications

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE A - Fundamentals):** Why does calling an
`@Transactional` method from within the same Spring
bean not start a transaction? Trace the mechanism from
`@Autowired` injection through proxy creation to method
invocation. What two approaches fix this?

**Q2 (TYPE C - Design Trade-off):** You are building a
REST API where a `GET /orders/{id}` endpoint needs to
return an order with its 10 items. Compare three
implementation approaches: (1) return an `@Entity` with
`@OneToMany(fetch=EAGER)`, (2) return an `@Entity` with
`@OneToMany(fetch=LAZY)` and an `@EntityGraph`, (3) use a
DTO projection via `@Query`. For each, state the SQL generated,
the risk of N+1, and the trade-off.

**Q3 (TYPE D - Root Cause):** A developer reports that
in a production system, an `Order` entity's `items`
collection is sometimes empty even though items exist in
the database. The code uses `LAZY` fetch. The bug does not
reproduce in tests. Trace the three most likely root causes
and the diagnostic steps for each.

---

### 🎯 Interview Deep-Dive

**Q1: What is the N+1 problem and how do you solve it?**
_Why they ask:_ #1 most asked JPA question - tests practical
ORM experience more than any other single topic.
_Strong answer:_
"N+1 occurs when loading N parent entities and accessing
their `LAZY`-loaded collections generates N additional
SELECT queries - 1 for the parent list and N for each
child collection. Detection: `spring.jpa.show-sql=true`
or Hibernate statistics. Fix options: (1) `JOIN FETCH`
in JPQL eliminates the N queries but creates a Cartesian
product when joining multiple collections; use `DISTINCT`
or `@QueryHints(PASS_DISTINCT_THROUGH=false)`. (2)
`@EntityGraph` solves N+1 per use case without changing
the entity's default fetch type. (3) DTO projections via
`@Query` - loads only needed fields, eliminates N+1 and
dirty checking overhead. Best choice depends on use case:
@EntityGraph for entity-returning endpoints,
DTO projection for reporting/read-heavy queries."

**Q2: Explain the persistence context. What is the first-level
cache and how does it affect your code?**
_Why they ask:_ Tests understanding of the core JPA mechanism
most candidates confuse with the second-level cache.
_Strong answer:_
"The persistence context is an identity map maintained by
the EntityManager for the duration of a session. Every
entity loaded within the same session is cached by its
`@Id`. `em.find(Product.class, 1L)` hits the DB on first
call; the second call within the same session returns the
cached instance without a DB round trip. Dirty checking
uses the same snapshot: at flush, Hibernate compares each
managed entity field against its loaded snapshot and issues
UPDATE only for changed fields. The first-level cache is
always on, cannot be disabled, and is scoped to the
EntityManager instance. Implications: (1) in a long
transaction processing thousands of entities, calling
`em.clear()` periodically prevents OutOfMemoryError from
snapshot accumulation; (2) JPQL queries bypass the
first-level cache and always hit the DB, but their results
are stored in it, potentially returning stale data if
the same entity was modified in the same session."

**Q3: What is the `@Transactional` self-invocation trap
and how do you fix it?**
_Why they ask:_ Discriminates senior from mid-level candidates;
requires understanding of Spring AOP proxy mechanism.
_Strong answer:_
"Spring's `@Transactional` is implemented via a proxy.
When a bean is `@Autowired`, you receive a proxy, not the
real bean. Calling an `@Transactional` method through the
proxy triggers the transaction interceptor. But calling a
method from within the same bean uses `this` (the real
object, not the proxy), bypassing the interceptor entirely.
The `@Transactional` annotation is silently ignored.
Fix options: (1) extract the inner method to a separate
Spring bean and inject it (preferred - improves separation
of concerns); (2) inject `ApplicationContext` and get
a reference to the current bean's proxy;
(3) use `AopContext.currentProxy()` (requires
`@EnableAspectJAutoProxy(exposeProxy=true)` - coupling to
Spring internals, avoid this).
The correct fix is always option 1."
