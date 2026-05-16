---
id: JPH-013
title: "Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-012
used_by: JPH-014, JPH-017, JPH-018, JPH-029
related: JPH-038, JPH-043
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
nav_order: 13
permalink: /jpa-hibernate/entity-lifecycle/
---

# JPH-013 - Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)

⚡ **TL;DR** - Every JPA entity instance is in one of four
states: NEW (not yet persisted), MANAGED (tracked by the
session), DETACHED (outside the session), or REMOVED
(scheduled for delete). Understanding which state an entity
is in determines what JPA does with it.

| #013 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | EntityManager, Persistence Context | |
| **Used by:** | JPQL, Relationship Mapping (@OneToMany/@ManyToOne), Cascade Types, @Transactional | |
| **Related:** | Optimistic Locking (@Version), Second-Level Cache | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In JDBC, every object interaction with the database is
explicit: you write an INSERT for new rows, UPDATE for
modified rows, DELETE for removed rows. There is no automatic
tracking. You must remember which objects are "in the DB,"
which are "new and need inserting," and which are "modified
and need updating." Miss one state transition and you have
silent data loss or duplicate inserts.

**THE BREAKING POINT:**
In a service layer that creates objects in one method, passes
them to another for modification, and then a third method
persists them, tracking the object state manually is fragile.
When objects are serialised to JSON, passed over HTTP,
deserialised, and then saved to the database, they have
lost their database connection. Calling the wrong JPA
operation on a disconnected object causes either a duplicate
insert or an EntityExistsException.

**THE INVENTION MOMENT:**
JPA formalises entity state into a well-defined lifecycle
with explicit transitions. Understanding which state an
entity is in - and which operation causes which transition -
eliminates the "which method do I call?" confusion.
The state machine IS the API contract.

---

### 📘 Textbook Definition

The JPA entity lifecycle defines four states for any entity
class instance:

**NEW (Transient):** A Java object instance created with
`new`. Not associated with any persistence context.
Not in the database. The `@Id` field is typically null or 0.
JPA does not track it.

**MANAGED (Persistent):** Associated with an active
persistence context. Every field change is tracked by
dirty checking. At flush time, Hibernate generates SQL to
synchronise with the database. An entity becomes MANAGED
via `em.persist()` (for new), `em.find()` (for existing),
`em.merge()` return value, or a JPQL query result.

**DETACHED:** Previously MANAGED but now outside any
persistence context. Has a valid `@Id` (exists or existed
in the database). Changes to a detached entity are NOT
tracked. Becomes detached when the session closes,
`em.detach()` is called, or `em.clear()` is called.

**REMOVED:** Scheduled for deletion. Was MANAGED;
`em.remove()` was called. At flush time, Hibernate generates
a DELETE. Still has its `@Id`. The deletion is only
executed at flush; the entity remains in the persistence
context as REMOVED until the flush executes.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Four states - NEW (created), MANAGED (tracked),
DETACHED (disconnected), REMOVED (delete queued) - and the
transitions between them are the EntityManager's API.

**One analogy:**
> Think of entity lifecycle like employment:
> - NEW: a job candidate (not yet hired, no employee ID)
> - MANAGED: a current employee (active, tracked, changes visible)
> - DETACHED: a former employee (has an ID, exists in records,
>   but no longer tracked day-to-day)
> - REMOVED: an employee who has submitted resignation (still
>   has access until last day / flush)

**One insight:** The most dangerous transition is
NEW -> DETACHED (a partially constructed entity that
was never persisted). Calling `em.merge()` on it will
try to update a non-existent DB row (or insert a duplicate).
Always know which state an entity is in before passing
it to the persistence layer.

---

### 🔩 First Principles Explanation

**STATE MACHINE DIAGRAM:**

```
         new Entity()
              |
              v
           [NEW]
              |
    em.persist(e)  <------- em.merge(detached)
              |                   returns new MANAGED
              v                   (detached stays DETACHED)
         [MANAGED]
         /    |    \
        /     |     \
em.detach() close   em.remove()
       /   session    \
      v                v
 [DETACHED]        [REMOVED]
      |                |
      |         flush() / commit()
      |                |
 em.merge(e)      [entity deleted
 (SELECT + copy)   from DB]
      |
      v
 NEW MANAGED COPY
```

**TRANSITION TABLE:**

| From | Operation | To | SQL |
|---|---|---|---|
| NEW | `em.persist(e)` | MANAGED | INSERT (at flush) |
| MANAGED | `em.detach(e)` | DETACHED | None |
| MANAGED | session close | DETACHED | None |
| MANAGED | `em.remove(e)` | REMOVED | DELETE (at flush) |
| MANAGED | field change | MANAGED | UPDATE (at flush) |
| DETACHED | `em.merge(e)` | MANAGED (new copy returned) | SELECT + UPDATE |
| REMOVED | none (via flush) | (gone) | DELETE |
| ANY | `em.find()` for ID | MANAGED (if found) | SELECT (or cache hit) |

**CORE INVARIANTS:**
1. Only MANAGED entities are dirty-checked and flushed
2. Calling `em.persist()` on a MANAGED entity is a no-op
3. Calling `em.persist()` on a DETACHED entity throws
   `EntityExistsException`
4. `em.merge()` always returns a NEW managed copy; the
   input detached entity STAYS detached
5. `em.remove()` must be called on a MANAGED entity;
   calling it on a detached entity throws
   `IllegalArgumentException`

---

### 🧪 Thought Experiment

**SCENARIO: REST API update flow**

A common pattern:
1. GET /products/1 -> loads entity, serialises to JSON,
   entity session closes -> entity DETACHED
2. Client modifies JSON, sends PUT /products/1
3. Spring deserialises JSON to a `Product` object with id=1

**What state is this `Product`?**
It was NEVER loaded from the database by this new request.
It was constructed by the deserialiser with the `@Id` field set.
It is a NEW entity object that LOOKS like a detached entity.

**If you call `em.persist()` on it:**
Hibernate sees non-null `@Id` and may throw
`EntityExistsException` or try to INSERT with a duplicate key.

**If you call `em.merge()` on it:**
Hibernate does a SELECT to check if the entity exists,
then generates an UPDATE if it does (correct behaviour).
This is why Spring Data's `save()` is designed to call
`merge()` when the ID is non-null - the object may be
a detached entity from a previous session OR a freshly
constructed DTO-like object. `merge()` handles both.

**THE INSIGHT:** In a REST API context, incoming request
body objects are ALWAYS in NEW state (they were constructed
by the deserialiser), even if they have an `@Id`. Always
use `merge()` (or Spring Data's `save()`) for update operations
in REST APIs. Never use `persist()` on an object from a
request body with a non-null ID.

---

### 🧠 Mental Model / Analogy

> Entity lifecycle = library book lifecycle:
> - NEW: a book someone brought to donate (no library ID yet)
> - MANAGED: a catalogued book on the shelf (ID assigned,
>   status tracked, checked out = "modified", returned = clean)
> - DETACHED: a book on loan (ID exists, not in library's
>   daily tracking; the library doesn't know what you've
>   done to it)
> - REMOVED: a book flagged for disposal (still on shelf
>   until end of day / flush, then removed)

- "Cataloguing" - `em.persist()` transitions NEW to MANAGED
- "Checking out" - `em.detach()` or session close
- "Returning and re-cataloguing" - `em.merge()`
- "Flagging for disposal" - `em.remove()`
- "End of day processing" - `flush()/commit()`

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you create a JPA entity with `new`, JPA doesn't know
about it. After `em.persist()`, JPA tracks it. After the
session closes, JPA stops tracking it. After `em.remove()`,
it's scheduled for deletion. Four states, four behaviours.

**Level 2 - How to use it (junior developer):**
In Spring Data JPA:
- `repository.save(entity)` when `id` is null = persist
- `repository.save(entity)` when `id` is non-null = merge
- `repository.delete(entity)` = remove
- `repository.findById(id)` = find (returns MANAGED)
Spring Data manages transitions automatically. Directly
using `EntityManager` requires knowing the state explicitly.

**Level 3 - How it works (mid-level engineer):**
The persistence context maintains a registry of MANAGED
entities. `em.contains(entity)` checks if an entity is
MANAGED. The dirty checker only processes MANAGED entities
at flush time. DETACHED entities carry their last-known
state in their fields but have no connection to the session.
`em.merge()` creates a copy in the session from the detached
entity's field values.

**Level 4 - Why it was designed this way (senior/staff):**
The DETACHED state exists specifically for the "conversation"
pattern: load an entity in one request, display it to a
user, let the user modify it, then save in a second request.
Between requests, the entity travels as a serialised object
(DETACHED). The `merge()` operation was designed to
re-attach and persist the detached state. However, modern
REST API design avoids this pattern: it sends changes as DTOs,
not re-attaches entity objects, because DTOs are simpler,
testable, and do not carry JPA-specific state constraints.

**Level 5 - Mastery (distinguished engineer):**
The REMOVED state is often misunderstood. After
`em.remove(entity)`, the entity is REMOVED but not yet
deleted from the database. It remains in the persistence
context as REMOVED. If cascade DELETE is configured on a
relationship, the cascaded entities are also transitioned
to REMOVED (not immediately deleted). At flush, all REMOVED
entities generate DELETE statements in reverse FK order
(children before parents to avoid FK violations). This
ordering is automatic in JPA but can fail when
`CascadeType.REMOVE` is used with `orphanRemoval=true` and
the cascade chain creates a cycle or an incomplete tree.

---

### ⚙️ How It Works (Mechanism)

**EntityManager Lifecycle Operations:**

```
┌──────────────────────────────────────────────┐
│        ENTITY STATE TRANSITIONS              │
├──────────────────────────────────────────────┤
│                                              │
│  [new Product()]                             │
│       |                                      │
│       | new = NEW state                      │
│       v                                      │
│  [NEW / Transient]                           │
│       |                                      │
│       | em.persist(p) or cascade PERSIST     │
│       v                                      │
│  [MANAGED] <-- em.find() / JPQL result       │
│       |    <-- em.merge() return value       │
│       |                                      │
│  +----|----+                                 │
│  |         |                                 │
│  | em.detach() / session close               │
│  v         | em.remove()                     │
│ [DETACHED] v                                 │
│  |      [REMOVED]                            │
│  |         |                                 │
│  | em.merge() -> new MANAGED copy            │
│  v         | flush / commit                  │
│ [NEW MANAGED COPY]                           │
│             v                                │
│         [DB row deleted]                     │
└──────────────────────────────────────────────┘
```

**Lifecycle Callbacks:**
JPA provides annotations for entity lifecycle events:

| Annotation | Trigger | Common Use |
|---|---|---|
| `@PrePersist` | Before INSERT | Set `createdAt` timestamp |
| `@PostPersist` | After INSERT | Send creation event |
| `@PreUpdate` | Before UPDATE | Set `updatedAt` timestamp |
| `@PostUpdate` | After UPDATE | Audit logging |
| `@PreRemove` | Before DELETE | Soft delete logic |
| `@PostRemove` | After DELETE | Cleanup side effects |
| `@PostLoad` | After SELECT / refresh | Decrypt fields |

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
Entity state is per-EntityManager (per-session, per-thread
in Spring). Two threads loading the same entity have two
separate MANAGED instances. There is no shared entity state
across sessions. Concurrent modifications to the same entity
are handled at the database level by transaction isolation
and optionally by optimistic locking (`@Version`).

---

### 🔄 The Complete Picture - End-to-End Flow

**REST API UPDATE FLOW:**

```
PUT /products/1 { "price": 29.99 }
    |
    v
[ Controller: @RequestBody Product p ]
    |  p is a new Java object, id=1, price=29.99
    |  p.state = NEW (constructed by Jackson)
    v
[ Service: productRepo.save(p) ]
    |  save() calls isNew(): id=1, non-null -> MERGE
    v
[ em.merge(p) ]
    |  SELECT * FROM products WHERE id=1
    |  (existing row found)
    |  State of p: still NEW
    |  managed = new MANAGED copy with p's fields
    v
[ managed.price = 29.99 confirmed ]
    |  dirty check at flush: price changed
    v
[ UPDATE products SET price=29.99 WHERE id=1 ]
    |
    v
[ Transaction commits ]
    |
    v
[ managed entity becomes DETACHED ]
    |  returned from save() as the managed copy
    v
[ Controller serialises returned Product to JSON ]
```

**FAILURE PATH:**
If `em.remove()` is called on a DETACHED entity (not in
the persistence context), it throws
`IllegalArgumentException: Removing a detached instance`.
Fix: call `em.merge()` first to get a MANAGED copy, then
call `em.remove()` on that.

---

### 💻 Code Example

**Example 1 - Full lifecycle walkthrough:**

```java
@Transactional
public void fullLifecycle() {

    // 1. NEW state
    Product p = new Product("Widget", 19.99);
    // p is NOT in any persistence context

    // 2. NEW -> MANAGED
    em.persist(p);
    // p is MANAGED; id assigned by sequence

    // 3. MANAGED: change tracked
    p.setPrice(29.99);
    // dirty - will generate UPDATE at flush

    // 4. MANAGED -> DETACHED
    em.detach(p);
    p.setName("Super Widget"); // NOT tracked!

    // 5. DETACHED -> new MANAGED copy via merge()
    Product managed = em.merge(p);
    // managed IS tracked; p is still DETACHED
    // managed.name = "Super Widget" (copied from p)
    // But p.price change to 29.99 was already flushed

    // 6. MANAGED -> REMOVED
    em.remove(managed);
    // DELETE queued; managed is REMOVED state

    // 7. flush/commit: DELETE executes
}
```

**Example 2 - @PrePersist for audit timestamps:**

```java
@Entity
public class Order {

    @Id
    @GeneratedValue(
        strategy = GenerationType.IDENTITY)
    private Long id;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private String status;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
    // No need to manually set timestamps
}
```

**Example 3 - Correct update via merge() in REST:**

```java
@PutMapping("/products/{id}")
@Transactional
public Product update(
        @PathVariable Long id,
        @RequestBody ProductDto dto) {

    // dto is NOT an entity; it's a plain DTO
    // Load entity (MANAGED) by ID
    Product managed = em.find(Product.class, id);
    if (managed == null) {
        throw new ProductNotFoundException(id);
    }

    // Apply changes to the MANAGED entity
    managed.setPrice(dto.getPrice());
    managed.setName(dto.getName());
    // dirty checking generates UPDATE at flush

    return managed;
    // No explicit save() needed -
    // dirty checking handles the UPDATE
}
```

---

### ⚖️ Comparison Table

| State | In Persistence Context | Tracked | SQL on change | `@Id` Present |
|---|---|---|---|---|
| **NEW** | No | No | No | No (or 0) |
| **MANAGED** | Yes | Yes | UPDATE at flush | Yes (after persist) |
| **DETACHED** | No | No | No | Yes |
| **REMOVED** | Yes | No (deleted) | DELETE at flush | Yes |

**Key distinction:** DETACHED vs. NEW both have no tracking,
but DETACHED entities have a valid `@Id` (they existed in
the DB). NEW entities have no `@Id`. This is how Spring
Data's `isNew()` check distinguishes them:
null/0 ID = NEW = call `persist()`; non-null ID = treat as
DETACHED = call `merge()`.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "I need to call `em.save()` to persist changes to a MANAGED entity" | There is no `em.save()`. MANAGED entities are automatically dirty-checked at flush. Just modify the field and let flush handle the UPDATE. This is the essence of dirty checking. |
| "`em.persist()` works on any entity object, including detached ones" | `em.persist()` on a DETACHED entity throws `EntityExistsException`. Use `em.merge()` for detached entities. |
| "After `em.remove()`, the entity is deleted from the database" | `em.remove()` transitions to REMOVED state. The DELETE SQL is only sent at flush. Until flush, the row still exists in the database. |
| "`em.merge()` updates the entity I passed in" | `em.merge()` returns a NEW managed copy. The input entity remains DETACHED. All subsequent modifications must be made on the returned managed copy. |
| "Entity state is shared across sessions" | Each `EntityManager` has its own persistence context. The same entity in two different sessions is two different Java objects in two independent MANAGED states. Changes in one session do not affect the other until committed and the other refreshes. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Calling persist() on a Detached Entity**

**Symptom:**
```
javax.persistence.EntityExistsException:
detached entity passed to persist: com.example.Product
```
**Root Cause:** An entity with a non-null `@Id` was passed
to `em.persist()`. The entity was previously managed (has
an `@Id`) but is now detached.
**Diagnostic:**

```bash
# Check the entity's @Id at the point of persist() call
# If non-null, the entity is detached or a DTO
```

**Fix:**

```java
// BAD: persist on a detached entity
em.persist(detachedProduct); // throws

// GOOD: merge to re-attach, OR find the managed copy
Product managed = em.merge(detachedProduct);
// OR:
Product managed = em.find(
    Product.class, detachedProduct.getId());
managed.setPrice(detachedProduct.getPrice());
```

**Prevention:** Never call `em.persist()` on an object
from outside the current session (REST request body,
cached object, DTO with ID). Use `em.merge()` or the
find-and-update pattern.

---

**Failure Mode 2: Modifying Detached Entity Without Noticing**

**Symptom:** Changes to an entity persist in some code paths
but not others; the behaviour depends on whether the method
is `@Transactional`.
**Root Cause:** The entity is MANAGED inside a `@Transactional`
context and DETACHED outside it. Code that modifies it
outside a transaction has no dirty checking, so changes
are silently lost.
**Diagnostic:**

```bash
# Add logging to @PreUpdate to detect when UPDATE fires
@PreUpdate
protected void onUpdate() {
    log.info("Updating entity: {}", this.id);
}
# If this log does not appear when expected,
# the entity is DETACHED when modified
```

**Fix:** Ensure modifications happen within a `@Transactional`
context. Use `@Transactional` on the service method or
the repository method that wraps the modification.

---

**Failure Mode 3: Remove Called on Detached Entity**

**Symptom:**
```
java.lang.IllegalArgumentException:
Removing a detached instance com.example.Order#42
```
**Root Cause:** `em.remove()` was called on an entity that
is DETACHED (not in the current persistence context).
**Diagnostic:**

```bash
# Check if em.contains(entity) returns false before remove
boolean isManaged = em.contains(order);
// false -> entity is DETACHED
```

**Fix:**

```java
// Correct pattern: merge to get managed copy, then remove
Order managed = em.merge(detachedOrder);
em.remove(managed);

// OR: find the entity in the current session
Order managed = em.find(
    Order.class, detachedOrder.getId());
if (managed != null) em.remove(managed);
```

**Prevention:** Refactor entity removal to load the entity
by ID within the same transaction, rather than passing
a detached entity across method boundaries.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-011 - EntityManager]] - lifecycle transitions are
  EntityManager operations; understand EntityManager first
- [[JPH-012 - Persistence Context]] - the persistence
  context determines which state (MANAGED vs DETACHED)
  an entity is in

**Builds On This (learn these next):**
- [[JPH-014 - JPQL (Java Persistence Query Language)]] -
  JPQL results are MANAGED entities (loaded into the
  persistence context)
- [[JPH-017 - @OneToMany and @ManyToOne]] - relationships
  affect lifecycle transitions via cascade
- [[JPH-018 - Cascade Types (ALL, PERSIST, MERGE, REMOVE)]] -
  cascade propagates lifecycle transitions to related entities
- [[JPH-029 - @Transactional]] - `@Transactional` scope
  determines when entities transition from MANAGED to DETACHED

**Alternatives / Comparisons:**
- [[JPH-038 - Optimistic Locking (@Version)]] - handles
  concurrent MANAGED -> flush conflicts
- [[JPH-043 - Second-Level Cache (@Cache, @Cacheable)]] -
  second-level cache stores serialised entity state for
  entities that are currently DETACHED

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STATE SUMMARY                                            │
├──────────────┬───────────────────────────────────────────┤
│ NEW          │ Created with new, no @Id, not tracked     │
│ MANAGED      │ In persistence context, tracked, SQL auto │
│ DETACHED     │ Has @Id, no tracking, changes ignored     │
│ REMOVED      │ DELETE queued, not yet executed           │
├──────────────┼───────────────────────────────────────────┤
│ KEY TRAPS    │ persist() on DETACHED -> exception        │
│              │ merge() -> use RETURN VALUE, not input    │
│              │ remove() needs MANAGED entity first       │
├──────────────┼───────────────────────────────────────────┤
│ REST API     │ Request body @RequestBody = NEW (not      │
│ RULE         │ DETACHED) - always use merge()/save()    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Know the state before you call the op:  │
│              │ persist=NEW, merge=DETACHED, find=any"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cascade Types -> @Transactional -> @Version│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. MANAGED = tracked; DETACHED = not tracked. Changes to
   DETACHED entities are silently ignored at flush
2. `merge()` returns a NEW managed copy; always use the
   return value - NOT the input object
3. In a REST API, `@RequestBody` entities are always NEW,
   not DETACHED - even if they have an `@Id`

**Interview one-liner:** JPA entity lifecycle has four states:
NEW (not tracked, no id), MANAGED (tracked by session, dirty
check on flush), DETACHED (has id, not tracked), REMOVED
(delete queued). Key traps: `persist()` on DETACHED throws
`EntityExistsException`; `merge()` returns a new MANAGED
copy (the input stays DETACHED); `remove()` requires a
MANAGED entity.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Explicit state machines
make hidden state bugs visible. Every object in a stateful
system has a lifecycle - but without explicit state modelling,
that lifecycle is implicit and error-prone. JPA's entity
lifecycle is the persistence-layer equivalent of a finite
state machine: each state has defined valid transitions and
the operations that trigger them. Systems that model state
explicitly - entity lifecycle, order status, payment state -
have fewer "impossible" bugs than systems where state is
tracked via boolean flags.

**Where else this pattern appears:**
- **Order management systems** - an order's state (PENDING,
  CONFIRMED, SHIPPED, DELIVERED, CANCELLED) follows an
  explicit state machine; trying to ship a CANCELLED order
  is equivalent to calling `persist()` on a REMOVED entity
- **Spring Batch Job lifecycle** - `STARTING`, `STARTED`,
  `STOPPING`, `STOPPED`, `FAILED`, `COMPLETED` are explicit
  states with defined transitions and callbacks - the same
  lifecycle callback pattern as JPA's `@PrePersist` etc.

---

### 💡 The Surprising Truth

The JPA DETACHED state was originally designed for the
"conversation" pattern: a user edits data across multiple
HTTP requests, and the entity "travels" between requests
in DETACHED state. The JPA spec even has `@PersistenceContext(type=EXTENDED)`
for extended persistence contexts that span multiple
transactions, keeping entities MANAGED across HTTP requests.
However, this pattern creates serious problems in stateless
web applications (entity state leaked via thread-local
across requests, connection pool exhaustion from long-lived
sessions). Modern Spring Boot applications default to
transaction-scoped persistence contexts and use DTOs for
multi-step workflows. The DETACHED state exists in the
spec for a use case that modern best practice has largely
abandoned.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DRAW** the entity lifecycle state diagram from memory
   with all four states, all transitions, and the operation
   that triggers each transition
2. **IDENTIFY** the state of an entity at any point in a
   code example: is it NEW, MANAGED, DETACHED, or REMOVED?
3. **DEBUG** an `EntityExistsException: detached entity
   passed to persist` by identifying the object came from
   outside the current session and replacing `persist()`
   with `merge()`
4. **EXPLAIN** why `merge()` returns a new object and
   why using the input object after `merge()` is an antipattern
5. **APPLY** `@PrePersist` and `@PreUpdate` callbacks to
   automatically set `createdAt` and `updatedAt` timestamps
   without manual code in every service method

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE D - Root Cause Trace):** A developer loads an
entity in `MethodA()` (non-transactional), passes it to
`MethodB()` (also non-transactional), which modifies a field,
and then calls `MethodC()` which is `@Transactional` and
calls `repository.save(entity)`. Is the modification from
`MethodB()` persisted? Why or why not? What is the entity's
state at each method boundary?
*Hint: Without `@Transactional` on MethodA, the entity is
loaded but the session immediately closes. The entity is
DETACHED before MethodB is called. MethodB modifies a
DETACHED entity. MethodC calls save() which calls merge()
on the DETACHED entity - so YES, the modification IS
persisted, because merge() copies the detached state.*

**Q2 (TYPE C - Design Trade-off):** Compare two approaches
for a REST API PUT endpoint: (1) Accept `@RequestBody Product`
and call `repository.save(product)` directly. (2) Accept
`@RequestBody ProductUpdateDto`, load the entity with
`findById()`, apply the DTO's fields to the managed entity.
Which is safer and why? What security risks does approach (1) introduce?
*Hint: Approach 1 is a "mass assignment" vulnerability -
the client can send any field including sensitive ones
(isAdmin, price, discount). Approach 2 explicitly maps
only allowed fields from the DTO to the entity.*

**Q3 (TYPE A - Fundamentals):** An entity is in REMOVED
state. What happens if `em.persist(entity)` is called on
it before flush? What does the JPA spec say?
*Hint: The JPA spec says calling persist() on a REMOVED entity
reactivates it (transitions back to MANAGED and cancels the
DELETE). This is an edge case that is easy to overlook -
a REMOVED entity can be "un-removed" by calling persist() before flush.*

---

### 🎯 Interview Deep-Dive

**Q1: Describe the four entity lifecycle states and the
operations that transition between them.**
*Why they ask:* Tests foundational JPA knowledge; this
is a standard screening question for all JPA roles.
*Strong answer includes:*
- NEW: created with `new`, no persistence context, no
  `@Id`; transition to MANAGED via `em.persist()`
- MANAGED: in persistence context, dirty checked;
  transitions to DETACHED via session close/`em.detach()`,
  to REMOVED via `em.remove()`
- DETACHED: has `@Id`, no tracking; transition to new
  MANAGED copy via `em.merge()` (return value)
- REMOVED: DELETE queued at flush; no further operations
  (except `em.persist()` to un-remove, which is a spec
  edge case)

**Q2: Why does `em.merge()` return a new object instead
of modifying the entity you passed in?**
*Why they ask:* Tests deep understanding of the merge
contract - a common source of bugs.
*Strong answer includes:*
- `merge()` must work when the detached entity has an ID
  that may or may not exist in the current persistence
  context; it needs to either locate or load the managed
  copy
- The input entity might be used in other code paths after
  merge; if `merge()` mutated it in-place, those code paths
  would unexpectedly hold a managed reference
- The spec defines merge as "copy state from detached to
  managed"; the "managed" is either an existing MANAGED
  copy in the context or a newly loaded one; the input
  is the source of state, not the output

**Q3: In a REST controller, a `@RequestBody Product` has
an id=42. Is this entity NEW or DETACHED?**
*Why they ask:* Tests practical understanding of entity
state in web application contexts - a common interview trap.
*Strong answer includes:*
- It is NEW - it was constructed by the Jackson deserialiser
  with `new Product()` and field assignments; it has never
  been loaded from a database by this JPA session
- A DETACHED entity would have been previously MANAGED in
  some session; this object was never in any session
- However, JPA treats it like a detached entity for `merge()`
  purposes: `merge()` checks if the ID exists in the DB
  and generates a SELECT + UPDATE if it does
- The distinction matters for `persist()`: calling
  `persist()` on this "fake detached" object may throw
  `EntityExistsException` if the DB already has a row
  with id=42
- Best practice: never pass `@RequestBody` entity objects
  to `em.persist()`; always use `merge()` or Spring Data's
  `save()` for REST-based updates