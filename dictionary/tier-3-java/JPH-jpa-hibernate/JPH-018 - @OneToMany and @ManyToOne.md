---
id: JPH-018
title: "@OneToMany and @ManyToOne"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-008, JPH-013, JPH-017
used_by: JPH-019, JPH-021, JPH-022, JPH-027, JPH-037
related: JPH-020, JPH-040
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
nav_order: 18
permalink: /jpa-hibernate/onetomany-manytoone/
---

# JPH-018 - @OneToMany and @ManyToOne

⚡ **TL;DR** - `@ManyToOne` is on the "many" side and holds
the FK column. `@OneToMany` is on the "one" side and uses
`mappedBy`. Always map the FK via `@ManyToOne`; avoid
unidirectional `@OneToMany` (generates a join table or
an extra UPDATE statement for the FK).

| #018 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | @Entity, @Id, @Table/@Column, Entity Lifecycle, @OneToOne | |
| **Used by:** | @ManyToMany, FetchType, CascadeType, N+1 Problem, @EntityGraph | |
| **Related:** | @JoinColumn and @JoinTable, Inheritance Mapping | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without `@OneToMany`/`@ManyToOne`, loading an `Order` and
its `OrderItem` records requires two separate queries:
one for the order and one for `SELECT * FROM order_items
WHERE order_id = ?`. The developer manually constructs
the `Order.items` list. Updating an item price requires
knowing the order ID, calling the item DAO separately,
and ensuring both transactions are coordinated. Cascading
a delete (delete order -> delete items) is manual.

**THE BREAKING POINT:**
When every aggregate root (Order, Customer, Product,
Category) has 3-5 one-to-many child collections, the DAO
layer becomes 500 lines of boilerplate: load parent,
load children, stitch together, handle nulls. Any new
child type requires the same 50-line cycle.

**THE INVENTION MOMENT:**
`@OneToMany(mappedBy="order")` on `Order.items` tells JPA
the whole relationship in one line. `order.getItems()`
navigates the association. `order.getItems().add(item)` and
`em.persist(order)` with cascade handles the insert.
JPA generates the correct SQL JOIN or child query and
manages the FK values.

---

### 📘 Textbook Definition

**`@ManyToOne`** maps the "many" side of a one-to-many
relationship. The annotated field holds a reference to
the "one" side entity. The underlying table column is a
foreign key pointing to the "one" side's primary key.

**`@OneToMany`** maps the "one" side. The annotated field
is a collection of "many" side entities. It is almost
always the inverse side (`mappedBy` required) pointing
to the `@ManyToOne` field on the child entity.

A bidirectional pair: the "many" side entity has
`@ManyToOne` (owning side, has FK), and the "one" side
entity has `@OneToMany(mappedBy="...")` (inverse side).

---

### ⏱️ Understand It in 30 Seconds

**One line:** An `Order` has many `OrderItem`s.
`@ManyToOne` is on `OrderItem` (the many side, with FK);
`@OneToMany(mappedBy="order")` is on `Order` (the one side).

**One analogy:**
> Think of a folder and its files. Each file belongs to
> one folder (`@ManyToOne` on File). Each folder contains
> many files (`@OneToMany` on Folder). The folder does not
> store file references in itself - the files store which
> folder they belong to (FK column on File, not Folder).

**One insight:** Unidirectional `@OneToMany` (without a
matching `@ManyToOne` and using `mappedBy`) generates a
join table or causes Hibernate to issue a separate UPDATE
statement for the FK. Always prefer bidirectional mapping
with `@ManyToOne` on the child.

---

### 🔩 First Principles Explanation

**DATABASE SCHEMA:**

```
orders table:        order_items table:
id | total           id | order_id | qty | price
1  | 150.00          1  | 1        | 2   | 50.00
2  | 75.00           2  | 1        | 1   | 50.00
                     3  | 2        | 3   | 25.00

FK: order_items.order_id -> orders.id
```

**ENTITY MAPPING:**

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private BigDecimal total;

    // Inverse side: mappedBy = field name in OrderItem
    @OneToMany(mappedBy = "order",
               cascade = CascadeType.ALL,
               orphanRemoval = true,
               fetch = FetchType.LAZY)
    private List<OrderItem> items = new ArrayList<>();

    // Sync helper
    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }
    public void removeItem(OrderItem item) {
        items.remove(item);
        item.setOrder(null);
    }
}

@Entity
@Table(name = "order_items")
public class OrderItem {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private int qty;
    private BigDecimal price;

    // Owning side: FK column is here
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id",
                nullable = false)
    private Order order;
}
```

**CORE INVARIANTS:**
1. `@ManyToOne` is ALWAYS the owning side - it holds the FK
2. `@OneToMany(mappedBy=...)` is ALWAYS the inverse side
3. Cascade is set on the parent (`Order`), not the child
4. Always set both sides for in-memory consistency;
   only the `@ManyToOne` side is written to the DB
5. Default fetch for `@ManyToOne` is EAGER (bad) - always
   override with `fetch=LAZY`
6. Default fetch for `@OneToMany` is LAZY (good default)
7. `orphanRemoval=true` on `@OneToMany` deletes child
   records when removed from the collection

---

### 🧪 Thought Experiment

**UNIDIRECTIONAL @OneToMany (WITHOUT mappedBy):**

```java
// BAD design: unidirectional @OneToMany
@Entity
public class Order {
    @OneToMany  // no mappedBy!
    @JoinColumn(name = "order_id")
    private List<OrderItem> items;
}
// No @ManyToOne on OrderItem
```

**WHAT HAPPENS:**
1. `order.getItems().add(item)` -> Hibernate does:
   - INSERT INTO order_items (qty, price) VALUES (?, ?)
     -> item inserted with order_id = NULL
   - UPDATE order_items SET order_id = ? WHERE id = ?
     -> FK updated in a second statement
2. Every add/remove triggers this extra UPDATE
3. For 100 items added: 100 INSERTs + 100 UPDATEs

**VS BIDIRECTIONAL (with mappedBy and @ManyToOne):**
1. `order.addItem(item)` -> item.order = order is set
2. Hibernate: INSERT INTO order_items (qty, price,
   order_id) VALUES (?, ?, ?) -> FK set in INSERT directly
3. For 100 items: 100 INSERTs, no extra UPDATEs

**THE INSIGHT:** Always use bidirectional
`@OneToMany`/`@ManyToOne` with `mappedBy`. The extra UPDATE
in unidirectional is a performance penalty and a source
of confusion.

---

### 🧠 Mental Model / Analogy

> Think of `@OneToMany`/`@ManyToOne` as a building (Order)
> and its apartments (OrderItems). Each apartment stores
> its building address (FK column `order_id` on the
> apartment record). The building has a tenant list
> (`@OneToMany` collection) but the list is derived from
> who has the building's address in their record.
>
> When you add a tenant (add to the collection), you must
> also update their apartment record with the building
> address (set the `@ManyToOne` field). If you only add
> to the building's tenant list (inverse side), the
> apartment record has no address - the change is ignored
> by JPA.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An `Order` has many `OrderItem`s. `@OneToMany` on Order,
`@ManyToOne` on OrderItem. The FK column is in the
OrderItem table.

**Level 2 - How to use it (junior developer):**
Add `@OneToMany(mappedBy="order", cascade=ALL)` to `Order.items`.
Add `@ManyToOne @JoinColumn(name="order_id")` to
`OrderItem.order`. Use helper methods to set both sides.

**Level 3 - How it works (mid-level engineer):**
Hibernate loads the collection via a secondary SELECT:
`SELECT * FROM order_items WHERE order_id = ?`. This fires
when `order.getItems()` is first called (LAZY).
With `cascade=ALL`, saving the Order also persists all
new OrderItems. With `orphanRemoval=true`, removing an
item from the collection deletes it from the database.

**Level 4 - Why it was designed this way (senior/staff):**
The `mappedBy` inverse side is a performance and correctness
decision. If both sides could write the FK, saving an
`Order` with items would produce two UPDATE statements for
the FK column - ambiguous and wasteful. By designating
`@ManyToOne` as the single FK writer, Hibernate has one
source of truth. The `@OneToMany(mappedBy)` side is a
purely navigational convenience - it does not generate
any additional SQL beyond the child collection query.

**Level 5 - Mastery (distinguished engineer):**
`@OneToMany` collections are the primary source of N+1
problems. Loading 100 orders and accessing `order.getItems()`
on each triggers 100 separate child collection queries
(1 + 100 = 101 total). The fix is JOIN FETCH in JPQL or
`@EntityGraph`. However, JOIN FETCH with `@OneToMany`
returns a Cartesian product in SQL (order rows multiplied
by item rows), requiring `DISTINCT` or `Set` instead of
`List` to deduplicate. Large collections (10,000+ children
per parent) should use pagination on the child query, not
`@OneToMany` at all - use a dedicated repository query with
`WHERE order_id = ? LIMIT ?` instead.

---

### ⚙️ How It Works (Mechanism)

**SQL GENERATED FOR LAZY COLLECTION LOAD:**

```sql
-- Initial: load Order
SELECT o.id, o.total FROM orders o WHERE o.id = ?

-- When order.getItems() is accessed:
SELECT oi.id, oi.qty, oi.price, oi.order_id
FROM order_items oi
WHERE oi.order_id = ?
```

**SQL GENERATED FOR CASCADE PERSIST:**

```sql
-- order.addItem(item); em.persist(order);
INSERT INTO orders (total) VALUES (?)
-- (order.id assigned)
INSERT INTO order_items (qty, price, order_id)
VALUES (?, ?, ?)  -- order_id set from order.id
```

**SQL GENERATED FOR orphanRemoval:**

```sql
-- order.removeItem(item);
-- At flush time:
DELETE FROM order_items WHERE id = ?
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CREATING AN ORDER WITH ITEMS:**

```java
@Transactional
public Order createOrder(OrderRequest req) {
    Order order = new Order();
    order.setTotal(req.getTotal());

    for (ItemRequest item : req.getItems()) {
        OrderItem oi = new OrderItem();
        oi.setQty(item.getQty());
        oi.setPrice(item.getPrice());
        order.addItem(oi); // sets oi.order = order
    }

    return orderRepo.save(order);
    // INSERT orders; N INSERT order_items with order_id set
}
```

**REMOVING AN ITEM:**

```java
@Transactional
public void removeItem(Long orderId, Long itemId) {
    Order order = orderRepo.findById(orderId)
        .orElseThrow();
    order.getItems().removeIf(i -> i.getId().equals(itemId));
    // orphanRemoval=true -> DELETE order_items WHERE id=?
    // at flush (end of transaction)
}
```

**FAILURE PATH:**
Calling `order.getItems()` outside a transaction with
LAZY fetch -> `LazyInitializationException: could not
initialize proxy - no Session`. The persistence context
has been closed; the collection cannot be loaded.

---

### 💻 Code Example

**Example 1 - Correct bidirectional mapping:**

```java
@Entity
public class Category {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private String name;

    @OneToMany(mappedBy = "category",
               cascade = CascadeType.ALL,
               orphanRemoval = true,
               fetch = FetchType.LAZY)
    private List<Product> products = new ArrayList<>();

    public void addProduct(Product p) {
        products.add(p);
        p.setCategory(this);  // sync owning side
    }
}

@Entity
public class Product {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id",
                nullable = false)
    private Category category;
}
```

**Example 2 - BAD: setting only the inverse side:**

```java
// BAD: product.category_id will be NULL
Category cat = categoryRepo.findById(1L).get();
Product p = new Product("Widget");
cat.getProducts().add(p);  // inverse side only!
productRepo.save(p);
// product.category_id = NULL (owning side not set)

// GOOD: set owning side, or use helper method
cat.addProduct(p);  // sets p.category = cat
productRepo.save(p);
// product.category_id = 1 (correct)
```

**Example 3 - N+1 diagnosis and fix with JOIN FETCH:**

```java
// BAD: N+1 - 1 + N child collection queries
List<Order> orders = orderRepo.findAll();
orders.forEach(o -> process(o.getItems())); // N queries

// GOOD: JOIN FETCH loads items in one query
@Query("SELECT DISTINCT o FROM Order o " +
       "LEFT JOIN FETCH o.items " +
       "WHERE o.status = :s")
List<Order> findByStatusWithItems(
    @Param("s") String s);
// DISTINCT is needed to deduplicate the Cartesian
// product rows from the JOIN
```

**Example 4 - @BatchSize to reduce N+1 without JOIN FETCH:**

```java
// Alternative: @BatchSize(size=25) batch loads collections
@Entity
public class Order {
    @OneToMany(mappedBy = "order",
               fetch = FetchType.LAZY)
    @org.hibernate.annotations.BatchSize(size = 25)
    private List<OrderItem> items;
}
// Hibernate issues: SELECT ... WHERE order_id IN (1,2,...25)
// 4 queries for 100 orders instead of 100 queries
```

---

### ⚖️ Comparison Table

| Design | FK Location | Extra UPDATE | JOIN TABLE | Use case |
|---|---|---|---|---|
| Bidirectional `@ManyToOne`/`@OneToMany(mappedBy)` | Child table | No | No | Standard pattern (always prefer) |
| Unidirectional `@OneToMany` (no `@ManyToOne`) | Child table via `@JoinColumn` | Yes (extra UPDATE) | No | Avoid; use bidirectional instead |
| Unidirectional `@OneToMany` (no `@JoinColumn`) | Join table | No | Yes | Avoid; use `@ManyToMany` or bidirectional |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The @OneToMany parent controls the FK" | The `@ManyToOne` child holds the FK column. The `@OneToMany` parent has `mappedBy` and is the INVERSE side - it does NOT write the FK. |
| "@ManyToOne default fetch is LAZY" | `@ManyToOne` default is EAGER. Every `em.find(OrderItem.class, 1L)` triggers a JOIN to load the parent Order. Always override with `fetch=LAZY`. |
| "JOIN FETCH with @OneToMany is always safe" | JOIN FETCH with `@OneToMany` produces a Cartesian product in SQL. Without `DISTINCT` or using a `Set` result, the parent entity appears multiple times in the result list (once per child row). |
| "orphanRemoval=true and CascadeType.REMOVE are the same" | `CascadeType.REMOVE` cascades `em.remove(order)` to all items. `orphanRemoval=true` additionally deletes items removed from the collection, even without `em.remove(order)`. `orphanRemoval` is stricter. |
| "Infinite JSON serialization is a JPA problem" | Infinite recursion in JSON (`Order -> items -> order -> items...`) is a serialization problem, not a JPA problem. Fix with `@JsonManagedReference`/`@JsonBackReference` or `@JsonIgnore`, not by changing the JPA mapping. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: LazyInitializationException on Collection**

**Symptom:** `org.hibernate.LazyInitializationException:
failed to lazily initialize a collection of role:
Order.items - could not initialize proxy - no Session`
**Root Cause:** `order.getItems()` accessed after the
transaction and persistence context have closed. The LAZY
collection proxy has no session to load from.
**Diagnostic:**

```bash
# Stacktrace: LazyInitializationException from controller/view
# -> persistence context was closed before access
spring.jpa.open-in-view=false
# Disabling OEIV surface the problem earlier (good practice)
```

**Fix:** Either (1) load the collection within the service
transaction using JOIN FETCH or `@EntityGraph`, or (2)
convert to DTO before returning from the service layer.
**Prevention:** Set `spring.jpa.open-in-view=false`.
Never return managed entities from service methods to
the web layer - use DTOs.

---

**Failure Mode 2: Duplicate Parent Rows from JOIN FETCH**

**Symptom:** Query returns 5 `Order` objects but the list
contains 15 entries - each order appears 3 times (it has
3 items each).
**Root Cause:** JOIN FETCH on `@OneToMany` produces SQL
Cartesian product. Without DISTINCT, each parent row
is returned once per child row.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# SELECT o.id, oi.id ... FROM orders o
# INNER JOIN order_items oi ON o.id = oi.order_id
# Result: 15 rows for 5 orders with 3 items each
```

**Fix:**

```java
@Query("SELECT DISTINCT o FROM Order o " +
       "LEFT JOIN FETCH o.items")
List<Order> findAllWithItems();
// DISTINCT in JPQL deduplicates at Hibernate level
// (not added to SQL; Hibernate deduplicates in memory)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-006 - @Entity]] - entities needed for associations
- [[JPH-007 - @Id and @GeneratedValue]] - PK for FK targets
- [[JPH-017 - @OneToOne]] - same owning/inverse concept

**Builds On This (learn these next):**
- [[JPH-019 - @ManyToMany]] - extends to M:N with join table
- [[JPH-021 - FetchType (LAZY vs EAGER)]] - fetch strategy
  for collections and references
- [[JPH-022 - CascadeType]] - cascade and orphanRemoval
  deep dive
- [[JPH-027 - N+1 Problem (ORM Context)]] - primary source
  of N+1 is `@OneToMany` collections

**Alternatives / Comparisons:**
- [[JPH-020 - @JoinColumn and @JoinTable]] - FK column
  customization for associations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ @ManyToOne   │ On the CHILD (many side). Has the FK.    │
│              │ Owning side. Default fetch: EAGER (bad)  │
│              │ -> always set fetch=LAZY                 │
├──────────────┼───────────────────────────────────────────┤
│ @OneToMany   │ On the PARENT (one side). Uses mappedBy. │
│              │ Inverse side. Default fetch: LAZY (good) │
├──────────────┼───────────────────────────────────────────┤
│ SAVE RULE    │ Set BOTH sides; use helper method.       │
│              │ Only @ManyToOne (owning) writes FK to DB │
├──────────────┼───────────────────────────────────────────┤
│ CASCADE      │ Set on @OneToMany parent (ALL or PERSIST)│
│              │ orphanRemoval=true for exclusive children │
├──────────────┼───────────────────────────────────────────┤
│ TRAPS        │ N+1 (fix: JOIN FETCH + DISTINCT);        │
│              │ LazyInit (fix: eager load in service);  │
│              │ Cartesian product (DISTINCT in JPQL)     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@ManyToOne is owning (FK); @OneToMany   │
│              │ is inverse (mappedBy). Always set both.  │
│              │ Always fetch=LAZY on @ManyToOne."        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `@ManyToOne` owns the FK column - only it writes to the
   database; always use `fetch=LAZY` on `@ManyToOne`
2. `@OneToMany(mappedBy=...)` is the inverse side - changes
   here are ignored by JPA; always use bidirectional with
   `@ManyToOne` on the child
3. JOIN FETCH with `@OneToMany` produces Cartesian product;
   always use `DISTINCT` in JPQL or a `Set` result type

**Interview one-liner:** `@ManyToOne` is on the child entity
and holds the FK column (owning side). `@OneToMany(mappedBy=...)`
is on the parent entity (inverse side, no FK). Default fetch
for `@ManyToOne` is EAGER - always override to LAZY.
Unidirectional `@OneToMany` generates extra UPDATE statements -
always use bidirectional. JOIN FETCH on `@OneToMany` needs
`DISTINCT` to eliminate Cartesian product rows.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** In any parent-child
relationship, the FK lives in the child table (the "many"
side). This is a fundamental relational database normalization
rule (3NF). JPA's `@ManyToOne` on the child reflects this
directly: the annotation is on the entity that holds the
FK column. The `@OneToMany` on the parent is the
DERIVED view of the relationship, not the source. This
principle applies everywhere: a blog post (parent) has
comments (children) where each comment stores `post_id`;
a shopping cart (parent) has items (children) where each
item stores `cart_id`.

**Where else this pattern appears:**
- **REST API design** - the child resource URL embeds the
  parent ID: `/orders/{orderId}/items` mirrors the FK
  `order_id` in the items table
- **Event sourcing** - events are the "many" children;
  the aggregate root is the "one" parent; events store
  the aggregate ID (FK equivalent)
- **Microservice composition** - the "many" service stores
  the foreign key reference to the "one" service's entity ID

---

### 💡 The Surprising Truth

Hibernate's `@BatchSize` annotation is often overlooked but
solves N+1 for `@OneToMany` collections without the
complexity of JOIN FETCH and Cartesian products.
`@BatchSize(size=25)` on a `@OneToMany` field causes
Hibernate to load collections using `WHERE order_id IN (?, ?, ...25 values)`.
Loading 100 orders with `@BatchSize(25)` results in
1 ORDER query + 4 collection queries (batch of 25 each)
= 5 total queries, instead of 101. This is significantly
simpler than JOIN FETCH for read-heavy list endpoints
that don't need all children loaded simultaneously.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DRAW** the database schema from the entity code and
   correctly identify which table has the FK column
2. **FIX** a bug where `product.category_id` is null
   after save by identifying the missing `@ManyToOne` side
3. **DIAGNOSE** N+1 from a `@OneToMany` collection by
   reading SQL logs and counting queries
4. **APPLY** JOIN FETCH with DISTINCT to eliminate N+1
   on a `@OneToMany` collection
5. **CHOOSE** between JOIN FETCH, `@BatchSize`, and
   `@EntityGraph` for three different collection loading
   scenarios and justify each

---

### 🎯 Interview Deep-Dive

**Q1: Which side of @OneToMany/@ManyToOne holds the FK
column, and why does it matter for persistence?**
*Why they ask:* Core JPA knowledge; tests whether the
candidate understands the owning/inverse distinction.
*Strong answer includes:*
- `@ManyToOne` (child) holds the FK column (owning side)
- Changes to the `@OneToMany` (inverse) field are IGNORED
  by JPA - only `@ManyToOne` writes the FK to the database
- Consequence: must always set the `@ManyToOne` field;
  setting only the `@OneToMany` list results in null FK
- Helper methods on the parent entity that set both sides
  atomically are the standard solution

**Q2: Why is the default fetch type on @ManyToOne dangerous
and what should you always do?**
*Why they ask:* Tests awareness of the most common JPA
performance anti-pattern in production code.
*Strong answer includes:*
- `@ManyToOne` default is EAGER - every `em.find(OrderItem)`
  also loads the parent Order via JOIN
- In a list query (`SELECT i FROM OrderItem i`), EAGER
  `@ManyToOne` adds a JOIN for every parent in the result
- With multiple EAGER `@ManyToOne` fields, each query
  adds multiple JOINs; in extreme cases Hibernate cannot
  execute the query due to JOIN complexity
- Always: `@ManyToOne(fetch=LAZY)` - load the parent only
  when `item.getOrder()` is explicitly called

**Q3: What happens when you use JOIN FETCH on a @OneToMany
collection without DISTINCT?**
*Why they ask:* Tests understanding of SQL JOIN semantics
vs JPA result list expectations.
*Strong answer includes:*
- JOIN FETCH produces a SQL JOIN: ORDER rows are repeated
  for each ORDER_ITEM row (Cartesian product)
- 5 orders with 3 items each = 15 result rows
- Without `DISTINCT`, the JPA result list contains 15
  `Order` objects (5 unique + 10 duplicates)
- Fix: add `DISTINCT` to JPQL (`SELECT DISTINCT o FROM Order`)
- Hibernate processes `DISTINCT` at the in-memory level
  (deduplicates by entity identity) rather than adding
  SQL DISTINCT (which would break the join result)
- Alternative: use `Set<OrderItem>` instead of `List<OrderItem>`
  for the collection - `Set` identity deduplicates automatically