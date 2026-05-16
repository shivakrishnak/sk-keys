---
id: JPH-022
title: CascadeType
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-013, JPH-017, JPH-018, JPH-019, JPH-021
used_by: JPH-027, JPH-037, JPH-039
related: JPH-029, JPH-052
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
nav_order: 22
permalink: /jpa-hibernate/cascadetype/
---

# JPH-022 - CascadeType

⚡ **TL;DR** - `CascadeType` controls which lifecycle
operations on a parent entity are automatically applied
to child entities. Never use `CascadeType.ALL` on
`@ManyToMany`. Be precise: use `PERSIST` + `MERGE` +
`orphanRemoval=true` instead of `ALL` on `@OneToMany`
when you need cascade delete.

| #022 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Entity Lifecycle, @OneToOne, @OneToMany/@ManyToOne, @ManyToMany, FetchType | |
| **Used by:** | N+1 Problem, @EntityGraph, Pessimistic Locking | |
| **Related:** | @Transactional with JPA, Dirty Checking and Flush Mode | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without cascade, saving an `Order` with new `OrderItem`s
requires two separate `em.persist()` calls:

```java
em.persist(order);
for (OrderItem item : order.getItems()) {
    em.persist(item);  // must do this manually
}
```

Forgetting to persist any child leaves it as a NEW entity
(not in the database) despite being referenced by the parent.
Deleting the order requires manually deleting each item first.

**THE BREAKING POINT:**
In a domain with deep object graphs (Order -> items ->
products -> attributes), every save operation requires
traversing the entire tree manually. Deleting a root
requires bottom-up deletion. The developer must track
every entity's lifecycle in application code.

**THE INVENTION MOMENT:**
`CascadeType.PERSIST` on `Order.items` means `em.persist(order)`
cascades to `em.persist(item)` for each item automatically.
`CascadeType.REMOVE` + `orphanRemoval=true` means deleting
or removing from the collection cascades to deletion.
The developer manages the lifecycle of the root; JPA manages
the rest.

---

### 📘 Textbook Definition

**`CascadeType`** is a JPA enum that controls which
`EntityManager` operations are cascaded from a parent
entity to its associated entities through a relationship.

The six cascade types:
- `PERSIST` - `em.persist(parent)` cascades to associated entities
- `MERGE` - `em.merge(parent)` cascades to associated entities
- `REMOVE` - `em.remove(parent)` cascades to associated entities
- `REFRESH` - `em.refresh(parent)` cascades to associated entities
- `DETACH` - `em.detach(parent)` cascades to associated entities
- `ALL` - shorthand for all five above

`orphanRemoval = true` is a separate attribute (not a
`CascadeType`): it deletes child entities that are removed
from the parent's collection, even without `em.remove(parent)`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `CascadeType` determines which JPA lifecycle
operations "flow through" an association from parent to child.

**One analogy:**
> A company (parent) and its employees (children). With
> `CascadeType.PERSIST`, registering the company automatically
> registers all employees. With `CascadeType.REMOVE`,
> dissolving the company automatically terminates all employees.
> Without cascade, dissolving the company leaves employees
> in legal limbo (orphan records / FK violations).

**One insight:** `CascadeType.ALL` includes `CascadeType.REMOVE`.
On `@ManyToMany`, `REMOVE` deletes the shared entities
(the Course entities all students share), not just the
join table rows. `CascadeType.ALL` on `@ManyToMany`
is a data-loss bug.

---

### 🔩 First Principles Explanation

**SIX CASCADE TYPES AND THEIR TRIGGERS:**

```
CascadeType.PERSIST  - triggered by em.persist(parent)
CascadeType.MERGE    - triggered by em.merge(parent)
CascadeType.REMOVE   - triggered by em.remove(parent)
CascadeType.REFRESH  - triggered by em.refresh(parent)
CascadeType.DETACH   - triggered by em.detach(parent)
CascadeType.ALL      - all of the above
```

**orphanRemoval vs CascadeType.REMOVE:**

```
CascadeType.REMOVE: fires when em.remove(parent) is called
  -> deletes all child entities
  -> triggered by parent deletion

orphanRemoval=true: fires when a child is removed from
  the parent's collection
  -> collection.remove(child) -> em.remove(child) at flush
  -> triggered by collection modification

Both can coexist (orphanRemoval=true + cascade=REMOVE):
  - em.remove(parent): all children deleted (REMOVE)
  - collection.remove(child): that child deleted (orphanRemoval)
```

**RECOMMENDED PATTERNS:**

```java
// Child entities with exclusive ownership (Order items):
@OneToMany(mappedBy = "order",
           cascade = {CascadeType.PERSIST,
                      CascadeType.MERGE},
           orphanRemoval = true,
           fetch = FetchType.LAZY)
private List<OrderItem> items;
// - PERSIST: new items saved with order
// - MERGE: updated items merged with order
// - orphanRemoval: removed items deleted
// - No REMOVE: don't want to delete items independently
//   (orphanRemoval handles collection-based deletion)

// Aggregate root with full lifecycle ownership:
@OneToOne(mappedBy = "user",
          cascade = CascadeType.ALL,
          orphanRemoval = true,
          fetch = FetchType.LAZY)
private UserProfile profile;
// ALL is safe here: profile has no meaning without user
// orphanRemoval: profile deleted if user.setProfile(null)
```

**CORE INVARIANTS:**
1. Cascade only flows in ONE direction: parent -> child
2. `CascadeType.ALL` = PERSIST + MERGE + REMOVE + REFRESH
   + DETACH (all five)
3. `orphanRemoval=true` implies `CascadeType.REMOVE` but
   also adds collection-based deletion
4. On `@ManyToMany`: NEVER use `REMOVE` or `ALL` - it
   deletes shared entities, not just join table rows
5. `CascadeType.PERSIST` is safe on all association types
6. Cascade does NOT control fetch type - those are orthogonal

---

### 🧪 Thought Experiment

**SCENARIO 1: No cascade, manually managed:**

```java
Order order = new Order();
OrderItem item1 = new OrderItem(3, 50.00);
OrderItem item2 = new OrderItem(1, 100.00);
order.addItem(item1);
order.addItem(item2);

em.persist(order);   // saves order
// item1 and item2 are still NEW (not persisted!)
// FK violation at commit: order_item.order_id is not null
// but item is not in the database
```

**SCENARIO 2: CascadeType.PERSIST:**

```java
@OneToMany(cascade = CascadeType.PERSIST, ...)
private List<OrderItem> items;

em.persist(order);   // cascades to item1, item2
// INSERT INTO orders ...
// INSERT INTO order_items ... (item1)
// INSERT INTO order_items ... (item2)
// All three entities saved in correct order
```

**SCENARIO 3: orphanRemoval:**

```java
@OneToMany(orphanRemoval = true, ...)
private List<OrderItem> items;

order.getItems().remove(item1);
// At flush: DELETE FROM order_items WHERE id = item1.id
// item1 is gone from DB because it was removed from collection
```

**THE INSIGHT:** Choose the minimum set of cascade types
that matches the lifecycle semantics. PERSIST and MERGE
are almost always safe. REMOVE requires careful analysis
of who "owns" the entity lifecycle.

---

### 🧠 Mental Model / Analogy

> Think of cascade types as HR policies in a company.
> - `PERSIST` = when a new department is created, its
>   initial employees are registered automatically
> - `MERGE` = when a department's data is updated, employee
>   updates are applied simultaneously
> - `REMOVE` = when a department is dissolved, its employees
>   are terminated
> - `orphanRemoval` = when an employee is removed from a
>   department's roster, they are immediately let go
>   (even if the department continues)
>
> Using `ALL` on a shared team (like a project team where
>   employees can be on multiple projects) is dangerous -
>   dissolving Project A terminates employees who are still
>   on Project B.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Cascade types control whether saving, deleting, or other
JPA operations on one entity automatically apply to related
entities. `PERSIST` is the most common: save the parent
and its new children are saved too.

**Level 2 - How to use it (junior developer):**
Use `cascade = {CascadeType.PERSIST, CascadeType.MERGE}`
on `@OneToMany` parent associations. Add `orphanRemoval=true`
when children should be deleted when removed from the
collection. Never use `cascade=ALL` on `@ManyToMany`.

**Level 3 - How it works (mid-level engineer):**
JPA intercepts `em.persist(parent)` and checks all
associations with `CascadeType.PERSIST`. For each child
entity in those associations, `em.persist(child)` is
called. This cascades recursively if the child also has
cascade associations. The cascade fires in the Java layer
before SQL generation.

**Level 4 - Why it was designed this way (senior/staff):**
Cascade types were designed for aggregate roots in DDD.
An `Order` aggregate root owns its `OrderItem` children.
`PERSIST` and `MERGE` on the Order's items mean the
aggregate can be saved as a unit. `orphanRemoval` enforces
the invariant that items cannot exist without an order -
removing from the collection is the only way to delete an item,
which is the correct way to model exclusive ownership.

**Level 5 - Mastery (distinguished engineer):**
Cascade semantics have a critical interaction with
`@ManyToMany` and shared entities. In DDD terms, entities
referenced via `@ManyToMany` are NOT owned by the parent
aggregate - they are separate aggregates referenced by
the association. Cascading REMOVE across a M:N association
violates the aggregate boundary. The correct DDD model:
cascade PERSIST/MERGE (to allow saving related entities
in the same transaction), but NEVER REMOVE on `@ManyToMany`.
Deleting associated entities (Course when a Student is
deleted) must be an explicit business operation, not an
implicit cascade.

---

### ⚙️ How It Works (Mechanism)

**CASCADE EXECUTION ORDER:**

```
em.persist(order)  where cascade=PERSIST on items
    |
    v
[ Hibernate intercepts persist() ]
    |  Find all associations with CascadeType.PERSIST
    v
[ For each OrderItem in order.items: ]
    |  em.persist(item)
    |  (recursive if item has cascade associations)
    v
[ At flush time: SQL generation in dependency order ]
    |  INSERT INTO orders ... (order must exist first)
    |  INSERT INTO order_items ... order_id=order.id
```

**orphanRemoval EXECUTION:**

```
order.getItems().remove(item1)
    |
    v
[ Hibernate tracks collection modification ]
    |  item1 removed from collection
    v
[ At flush time: ]
    |  check: item1 is no longer in any parent collection
    |  orphanRemoval=true -> schedule DELETE
    v
[ DELETE FROM order_items WHERE id = item1.id ]
```

**CROSS-TRANSACTION BEHAVIOR:**
Cascade fires only within the same transaction/session.
Calling `em.persist(detachedOrder)` where order has
`CascadeType.PERSIST` will cascade to the detached items
via `em.merge(item)` if item is detached. The cascade
adapts to the entity state.

---

### 🔄 The Complete Picture - End-to-End Flow

**CREATING AND SAVING AN AGGREGATE:**

```java
@Transactional
public Order createOrder(CreateOrderRequest req) {
    Order order = new Order(req.getCustomerId());

    req.getItems().forEach(itemReq -> {
        Product product = productRepo
            .findById(itemReq.getProductId())
            .orElseThrow();
        OrderItem item = new OrderItem(
            product, itemReq.getQty());
        order.addItem(item);
        // item.order = order; cascade=PERSIST ensures
        // item will be saved when order is saved
    });

    return orderRepo.save(order);
    // JPA:
    // INSERT INTO orders ...
    // N INSERT INTO order_items ... (one per item)
}
```

**REMOVING AN ITEM:**

```java
@Transactional
public void removeItem(Long orderId, Long itemId) {
    Order order = orderRepo.findById(orderId)
        .orElseThrow();
    order.getItems().removeIf(
        i -> i.getId().equals(itemId));
    // orphanRemoval=true:
    // DELETE FROM order_items WHERE id=itemId at flush
}
```

---

### 💻 Code Example

**Example 1 - Recommended cascade pattern for @OneToMany:**

```java
@Entity
public class Order {

    @OneToMany(
        mappedBy = "order",
        cascade = {CascadeType.PERSIST,
                   CascadeType.MERGE},
        orphanRemoval = true,
        fetch = FetchType.LAZY)
    private List<OrderItem> items = new ArrayList<>();

    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }

    public void removeItem(OrderItem item) {
        items.remove(item);
        item.setOrder(null);
    }
}
```

**Example 2 - BAD: CascadeType.ALL on @ManyToMany:**

```java
// BAD: cascade ALL on @ManyToMany
@ManyToMany(cascade = CascadeType.ALL)
@JoinTable(name = "student_courses", ...)
private Set<Course> courses;

// studentRepo.delete(student):
// -> cascade REMOVE to all Course entities
// -> DELETE FROM courses WHERE id IN (1,2,3...)
// -> Other students lose their courses!

// GOOD: only PERSIST and MERGE on @ManyToMany
@ManyToMany(cascade = {CascadeType.PERSIST,
                       CascadeType.MERGE})
@JoinTable(name = "student_courses", ...)
private Set<Course> courses;
// Deleting student only deletes join table rows
// Course entities are preserved for other students
```

**Example 3 - orphanRemoval vs CascadeType.REMOVE:**

```java
// orphanRemoval=true (WITHOUT cascade=REMOVE):
@OneToMany(mappedBy="order",
           orphanRemoval=true,
           cascade={CascadeType.PERSIST,
                    CascadeType.MERGE})
private List<OrderItem> items;

// Collection remove -> DELETE (via orphanRemoval)
order.removeItem(item);  // DELETE at flush

// Direct em.remove(order) -> does NOT cascade delete items
// Items remain as orphan rows -> FK violation!
// (no CascadeType.REMOVE, so no cascade on em.remove)

// To avoid: add CascadeType.REMOVE too, or always
// delete order by clearing its items first
```

**Example 4 - CascadeType.REFRESH for bulk refresh:**

```java
@OneToMany(mappedBy = "order",
           cascade = {CascadeType.PERSIST,
                      CascadeType.MERGE,
                      CascadeType.REFRESH},
           orphanRemoval = true)
private List<OrderItem> items;

// After a bulk JPQL UPDATE on order_items:
em.refresh(order);
// Cascades: em.refresh(item) for each item in items
// All items reloaded from DB, stale state evicted
```

---

### ⚖️ Comparison Table

| Cascade | Triggers on | Safe for @ManyToMany? | Use case |
|---|---|---|---|
| `PERSIST` | `em.persist(parent)` | Yes | Save new children with parent |
| `MERGE` | `em.merge(parent)` | Yes | Update detached children |
| `REMOVE` | `em.remove(parent)` | NO - deletes shared entities | Exclusive ownership only |
| `REFRESH` | `em.refresh(parent)` | Yes (rarely needed) | After bulk updates |
| `DETACH` | `em.detach(parent)` | Yes (rarely needed) | Batch processing |
| `ALL` | All of the above | NO | `@OneToOne`/`@OneToMany` exclusive ownership |
| `orphanRemoval` | Collection modification | N/A | Exclusive children that die with parent |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`orphanRemoval=true` and `CascadeType.REMOVE` are the same" | `CascadeType.REMOVE` fires only on `em.remove(parent)`. `orphanRemoval=true` ALSO fires when a child is removed from the parent's collection via `collection.remove(child)`. `orphanRemoval` is stricter. |
| "`CascadeType.ALL` is always safe for @OneToMany" | `ALL` includes `REMOVE`. If the child entities could ever be referenced by another parent (e.g., shared lookup entities), cascading `REMOVE` deletes them across the board. Only use `ALL` for exclusively-owned children. |
| "Cascade fires in SQL order (parent first, then children)" | Cascade fires at the Java EntityManager level, then Hibernate determines the SQL insertion order based on FK dependencies. The cascade happens before SQL generation. |
| "`CascadeType.MERGE` is needed for updating child entities" | If the child is already MANAGED (in the persistence context), dirty checking handles updates automatically at flush time - no explicit `merge` or `cascade=MERGE` needed. `cascade=MERGE` is needed only when the parent OR child is DETACHED and `em.merge(parent)` is called. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: TransientPropertyValueException (Missing PERSIST)**

**Symptom:** `org.hibernate.TransientPropertyValueException:
object references an unsaved transient instance - save
the transient instance before flushing`
**Root Cause:** A child entity is in NEW state (not yet
persisted) and is referenced by a MANAGED parent entity.
`CascadeType.PERSIST` is not configured, so JPA does not
automatically persist the child.
**Diagnostic:**

```
Stack trace: at flush time, Hibernate finds that entity
field X references a NEW (unsaved) entity Y.
-> Y must be persisted before the session flushes.
```

**Fix:** Either (1) add `CascadeType.PERSIST` to the
association, or (2) explicitly call `em.persist(child)`
before calling `em.persist(parent)` or before the flush.

---

**Failure Mode 2: Data Loss From CascadeType.REMOVE on @ManyToMany**

**Symptom:** Deleting a User entity also deletes Role
entities, causing other users to lose their roles.
`NoResultException` or missing data for other users.
**Root Cause:** `cascade = CascadeType.ALL` (or `REMOVE`)
on `@ManyToMany User.roles`. `em.remove(user)` cascades
`em.remove(role)` to all Role entities in `user.roles`.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# delete user:
# DELETE FROM user_roles WHERE user_id=1  (join table)
# DELETE FROM roles WHERE id=1            (entity deleted!)
# DELETE FROM roles WHERE id=2            (entity deleted!)
```

**Fix:** Change to `cascade = {CascadeType.PERSIST, CascadeType.MERGE}`.
Role entities should not be deleted when a user is deleted -
only the join table rows should be cleaned up (done
automatically by JPA when the user is removed).

---

**Failure Mode 3: Orphan Items Not Deleted (Missing orphanRemoval)**

**Symptom:** `order.getItems().remove(item)` does not
delete the item from the database. The item row remains
in `order_items` with the original `order_id`.
**Root Cause:** `orphanRemoval=false` (or not set). JPA
does not delete children when they are removed from the
collection without `orphanRemoval=true`.
**Fix:** Add `orphanRemoval=true` to the `@OneToMany`
annotation. Also ensure the owning side (`item.order`)
is set to null when removing (via the helper method).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-013 - Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)]] -
  cascade types map to lifecycle transitions
- [[JPH-018 - @OneToMany and @ManyToOne]] - primary
  association where PERSIST + MERGE + orphanRemoval is used
- [[JPH-019 - @ManyToMany]] - NEVER use REMOVE or ALL cascade

**Builds On This (learn these next):**
- [[JPH-027 - N+1 Problem (ORM Context)]] - cascade affects
  the number of SQL statements
- [[JPH-037 - EntityGraph (Solving N+1)]] - @EntityGraph
  is orthogonal to cascade; solves fetch, not lifecycle
- [[JPH-039 - Pessimistic Locking (LockModeType)]] -
  cascade and locking interact in concurrent scenarios

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PERSIST      │ Cascade em.persist(parent) to children   │
│ MERGE        │ Cascade em.merge(parent) to children     │
│ REMOVE       │ Cascade em.remove(parent) to children    │
│              │ NEVER on @ManyToMany                     │
│ ALL          │ All above - ONLY for exclusive children  │
├──────────────┼───────────────────────────────────────────┤
│ orphanRemoval│ Delete child when removed from collection │
│ =true        │ (separate from CascadeType.REMOVE)       │
├──────────────┼───────────────────────────────────────────┤
│ SAFE PATTERN │ @OneToMany: cascade={PERSIST, MERGE}     │
│              │ + orphanRemoval=true                      │
│              │ @ManyToMany: cascade={PERSIST, MERGE}    │
│              │ (NO REMOVE, NO ALL)                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cascade = lifecycle propagation. PERSIST │
│              │ + MERGE + orphanRemoval for @OneToMany.  │
│              │ NEVER cascade REMOVE on @ManyToMany."    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `CascadeType.REMOVE` on `@ManyToMany` deletes shared
   entities - not just join rows. NEVER use it.
2. `orphanRemoval=true` fires on collection.remove(child);
   `CascadeType.REMOVE` fires on em.remove(parent). They
   are different and often both needed.
3. The safe `@OneToMany` pattern: `cascade={PERSIST,MERGE}` +
   `orphanRemoval=true` (use ALL only for entities with
   no other parents)

**Interview one-liner:** `CascadeType` controls which JPA
lifecycle operations (`persist`, `merge`, `remove`, `refresh`,
`detach`) propagate from parent to child. For `@OneToMany`
exclusive children use `cascade={PERSIST,MERGE}` +
`orphanRemoval=true`. Never use `REMOVE` or `ALL` on
`@ManyToMany` - it deletes shared entities. `orphanRemoval`
differs from `CascadeType.REMOVE`: it fires on collection
removal, not only on parent deletion.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Aggregate boundaries
determine cascade scope. An aggregate root owns its
children exclusively: cascade PERSIST, MERGE, REMOVE,
and orphanRemoval are all appropriate for exclusively-owned
children (Order -> OrderItem). Shared entities (Course
enrolled by multiple Students) are separate aggregates:
cascade PERSIST/MERGE at most; NEVER cascade REMOVE across
aggregate boundaries. This is the core DDD aggregate
design pattern. The same principle applies in event
sourcing (events are exclusively owned by their aggregate;
cascading deletes of events when deleting a snapshot is
appropriate), microservices (a service deleting its own
aggregate's sub-resources is fine; deleting resources
owned by another service is not).

---

### 💡 The Surprising Truth

`CascadeType.REFRESH` is the most commonly forgotten cascade
type, yet it is critical after bulk JPQL operations. A
JPQL bulk UPDATE on child entities (e.g., `UPDATE OrderItem i
SET i.price = i.price * 1.1`) bypasses the persistence
context and leaves managed child entities with stale
field values. Without `cascade=REFRESH`, calling
`em.refresh(order)` only refreshes the Order entity -
not its items. With `cascade=REFRESH` on `Order.items`,
`em.refresh(order)` refreshes all items too. This is
the correct pattern after any bulk update that affects
child entities in a long-running session.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CHOOSE** the correct cascade set for three scenarios:
   (a) exclusively-owned `@OneToMany`, (b) `@ManyToMany`
   shared entities, (c) `@OneToOne` with shared lifecycle
2. **EXPLAIN** the difference between `orphanRemoval=true`
   and `CascadeType.REMOVE` with a concrete example
3. **FIX** a `TransientPropertyValueException` by identifying
   the missing `CascadeType.PERSIST` and adding it correctly
4. **DEBUG** data loss from `CascadeType.ALL` on `@ManyToMany`
   by reading SQL logs and identifying the entity deletion
5. **DESIGN** a cascade strategy for a `Customer` aggregate
   with `@OneToMany` `addresses`, `@OneToMany` `orders`,
   and `@ManyToMany` `roles` (each with different ownership
   semantics)

---

### 🎯 Interview Deep-Dive

**Q1: What is the danger of using CascadeType.ALL on a
@ManyToMany relationship?**
*Why they ask:* Very common production bug; tests cascade
depth understanding.
*Strong answer includes:*
- `ALL` includes `CascadeType.REMOVE`
- For `@ManyToMany`, the entities in the collection are
  SHARED - other parents reference them
- `em.remove(student)` with `cascade=ALL` calls
  `em.remove(course)` for each course in `student.courses`
- This deletes Course entities from the database, breaking
  all other students enrolled in those courses
- Fix: `cascade = {PERSIST, MERGE}` only; join table rows
  are managed implicitly

**Q2: What is the difference between orphanRemoval=true
and CascadeType.REMOVE?**
*Why they ask:* A subtle distinction that affects data
integrity; tests JPA lifecycle knowledge.
*Strong answer includes:*
- `CascadeType.REMOVE`: fires only when `em.remove(parent)`
  is explicitly called; cascades the remove operation to
  all child entities
- `orphanRemoval=true`: fires when a child is removed from
  the parent's collection (`collection.remove(child)`),
  even if `em.remove(parent)` is never called
- Both can coexist; `orphanRemoval` implies `REMOVE` behavior
  for collection-based removal
- Example: `order.getItems().remove(item)` with
  `orphanRemoval=true` -> DELETE item at flush (even if
  the order is NOT being deleted)

**Q3: What happens if you have CascadeType.PERSIST but
not CascadeType.MERGE and you try to update a detached
child entity?**
*Why they ask:* Tests understanding of entity states and
which cascade type handles which transition.
*Strong answer includes:*
- `CascadeType.PERSIST`: only fires on `em.persist()` for
  NEW entities; does not cascade merging DETACHED entities
- Without `CascadeType.MERGE`: when `em.merge(parent)` is
  called and parent has a DETACHED child, the merge does
  not cascade to the child
- The DETACHED child's changes are NOT applied to the
  persistence context
- Fix: add `CascadeType.MERGE` to ensure detached child
  updates are merged when the parent is merged
- With MANAGED children: no cascade needed for updates
  (dirty checking handles it)