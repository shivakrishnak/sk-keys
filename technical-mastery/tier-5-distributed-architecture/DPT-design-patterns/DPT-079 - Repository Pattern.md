---
id: DPT-079
title: Repository Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-078
used_by: []
related: DPT-073, DPT-078, DPT-002, DPT-003
tags:
  - pattern
  - data-access
  - intermediate
  - persistence
  - testability
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 79
permalink: /technical-mastery/design-patterns/repository-pattern/
---

⚡ TL;DR - The Repository Pattern mediates between the
domain layer and the data mapping layer using a
collection-like interface for accessing domain objects.
The domain sees a repository as an in-memory collection;
the repository internally handles all database interaction.

| #79 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-078 | |
| **Used by:** | N/A | |
| **Related:** | DPT-073, DPT-078, DPT-002, DPT-003 | |

---

### 🔥 The Problem This Solves

**SQL LEAKING INTO BUSINESS LOGIC:**
An e-commerce `OrderService` that wants to load an order
containing all its items writes:
```java
String sql = "SELECT o.*, i.* FROM orders o " +
             "JOIN order_items i ON o.id = i.order_id " +
             "WHERE o.id = ? AND o.status = 'ACTIVE'";
```
This SQL is:
- Inside `OrderService` (the business layer)
- Tied to a specific database schema
- Unable to be unit-tested without a database
- Duplicated wherever orders are loaded

**THE CONSEQUENCE:**
Business logic is mixed with data access. Changing the
schema (renaming a column, changing a join) requires
finding and editing SQL in business classes. Testing
business rules requires a database to be running.

**REPOSITORY SOLUTION:**
`OrderService` calls `orderRepository.findActiveById(id)`.
The repository interface hides all SQL, ORM, schema
details. Business logic sees a collection. The repository
contains the data access complexity.

---

### 📘 Textbook Definition

The **Repository Pattern** (Martin Fowler, "Patterns of
Enterprise Application Architecture", 2002) is a data
access pattern:

> "Mediates between the domain and data mapping layers
> using a collection-like interface for accessing domain
> objects."

**Key characteristics:**
- The repository's interface is expressed in DOMAIN TERMS
  (`findActiveOrders`, `findByCustomer`) not database terms
  (`executeQuery`, `SELECT WHERE`).
- Internally, the repository translates domain queries
  into database operations (SQL, ORM queries, API calls).
- The domain layer (business logic, use cases) depends
  on the repository INTERFACE (abstraction), not the
  implementation (DIP - DPT-078).
- One repository per aggregate root (in DDD: the top-level
  domain entity for a consistency boundary).

**Repository vs DAO (Data Access Object):**
DAO focuses on database access (one DAO per table).
Repository focuses on the domain (one repository per
domain concept). A repository may use multiple DAOs
or ORM entities internally.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The repository pattern makes databases look like in-memory
collections to the business layer. Find by condition,
save, delete - no SQL visible outside the repository.

**One analogy:**
> A library's card catalog (or online catalog).
>
> You search: "all science fiction books published after 2010."
> The catalog returns books matching your query.
> You do not care: whether books are in the basement
> storage, in a partner library, or in a digital archive.
> The catalog's interface speaks your language (title,
> genre, author). The mechanism (where the books physically
> are) is hidden.
>
> Repository: your code speaks domain language (findByGenre,
> findByAuthorAndPublishYear). The repository translates
> to the storage mechanism (SQL, NoSQL, REST API, file system).
> The business layer never knows the difference.

---

### 🔩 First Principles Explanation

**THE COLLECTION METAPHOR:**
The repository interface models an in-memory collection:
`add(entity)`, `remove(entity)`, `findById(id)`,
`findByCondition(spec)`. From the caller's perspective:
it is as if all domain objects are in memory.
The repository's INTERNAL implementation performs the
actual database work.

This metaphor is powerful: unit tests can use an in-memory
repository (a `HashMap` behind the interface). The business
logic is tested at full speed without a database.
In production: the same interface is backed by real DB.

**DOMAIN LANGUAGE IN THE INTERFACE:**
Repository methods are named for business queries:
```
findActiveOrdersByCustomer(customerId)
findHighValueOrders(minimumAmount)
countPendingOrdersOlderThan(duration)
```
Not: `executeSelect(sql)` or `query("SELECT ... WHERE status=?")`.
The interface expresses WHAT the business needs.
The implementation decides HOW to get it.

**AGGREGATE ROOT PRINCIPLE:**
In Domain-Driven Design (DDD), repositories are defined
for AGGREGATE ROOTS only (the top-level entity that
controls a consistency boundary). Access to child entities
goes through the aggregate root's repository:
`orderRepository.findById(orderId)` returns the Order
WITH its items. You do not have a separate `OrderItemRepository`.
This enforces the aggregate's consistency boundary.

---

### 🧪 Thought Experiment

**THREE STORAGE BACKENDS, ONE BUSINESS RULE:**
Business rule: "An order is invalid if it has no items."
This rule should be testable WITHOUT any database.

**With Repository Pattern:**
```java
// Test with in-memory repository:
OrderRepository repo = new InMemoryOrderRepository();
Order order = new Order(); // no items
repo.save(order);
OrderService service = new OrderService(repo);
assertThrows(InvalidOrderException.class,
    () -> service.validate(order));
```
Test runs in < 1ms. No database. No mocking framework.

**Same test in production:** the same `OrderService` uses
a `JpaOrderRepository`. The business rule test does
not change. The infrastructure changes (real DB) do
not affect the test.

---

### 🧠 Mental Model / Analogy

> Repository = the "domain translator" model.
> A professional interpreter between two worlds.
>
> Domain world: "Give me all active orders for customer #42."
> Database world: "SELECT * FROM orders JOIN ... WHERE ..."
>
> The interpreter (repository) receives domain language,
> translates to database language, gets the result,
> translates back to domain objects.
>
> Neither the domain nor the database needs to know
> the other's language. The interpreter is the only
> bilingual entity.
>
> Changing the database (from SQL to NoSQL): replace
> the interpreter (a new implementation of the same interface).
> Domain code: unchanged (it still speaks domain language).

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Basic repository structure:**
A repository has: an interface in the domain layer,
and a concrete implementation in the infrastructure layer.
Methods are named in domain terms. The implementation
uses JPA, JDBC, NoSQL client, or HTTP client.

**Level 2 - Specification Pattern:**
For complex queries, the Repository can accept a
`Specification` object (a composable query predicate).
`findAll(new ActiveOrderSpec().and(new HighValueSpec()))`.
Spring Data JPA's `JpaSpecificationExecutor` implements this.
Avoids proliferating `findByX`, `findByXAndY` methods.

**Level 3 - Spring Data JPA as framework support:**
Spring Data JPA auto-generates repository implementations
from interface method names (`findByStatusAndCustomerId`).
This is a framework-level implementation of the Repository
Pattern - the framework generates the SQL translation.
Spring Data repositories ARE Repository Pattern compliant:
the interface is domain-focused; the framework handles
the mechanism. Custom `@Query` methods provide escape
hatches for complex queries the method name convention
cannot express.

---

### ⚙️ How It Works (Mechanism)

```
Repository Pattern Structure
┌─────────────────────────────────────────────────────────┐
│ DOMAIN LAYER (business logic):                         │
│   interface OrderRepository {                          │
│     Order findById(long id);                          │
│     List<Order> findByCustomer(long customerId);       │
│     List<Order> findActiveOrders();                    │
│     void save(Order order);                           │
│     void delete(long id);                             │
│   }                                                    │
│   OrderService uses OrderRepository (interface only)  │
│                                                        │
│ INFRASTRUCTURE LAYER (data access):                   │
│   JpaOrderRepository implements OrderRepository {     │
│     findById(id): JPA entityManager.find()           │
│     findByCustomer(id): JPQL query                   │
│     findActiveOrders(): Named query                   │
│     save(order): entityManager.persist/merge()        │
│     delete(id): entityManager.remove()               │
│   }                                                    │
│                                                        │
│ TESTING (unit tests):                                 │
│   InMemoryOrderRepository implements OrderRepository { │
│     findById(id): hashMap.get(id)                    │
│     save(order): hashMap.put(order.getId(), order)   │
│   }                                                    │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Repository Pattern implementation:**

```java
// DOMAIN LAYER - interface in business/domain package:
// com.example.domain.order

interface OrderRepository {
    Optional<Order> findById(long id);
    List<Order> findByCustomerId(long customerId);
    List<Order> findPendingOlderThan(Duration age);
    void save(Order order);
    void delete(long id);
}

class OrderService {
    private final OrderRepository orderRepo; // interface only

    OrderService(OrderRepository orderRepo) {
        this.orderRepo = orderRepo;
    }

    void cancelAbandonedOrders(Duration threshold) {
        // Domain language. No SQL. No JPA.
        List<Order> abandoned =
            orderRepo.findPendingOlderThan(threshold);
        abandoned.forEach(o -> {
            o.cancel();
            orderRepo.save(o);
        });
    }
}
```

```java
// INFRASTRUCTURE LAYER - JPA implementation:
// com.example.infrastructure.persistence

@Repository
class JpaOrderRepository implements OrderRepository {

    @PersistenceContext
    private EntityManager em;

    public Optional<Order> findById(long id) {
        return Optional.ofNullable(em.find(Order.class, id));
    }

    public List<Order> findByCustomerId(long customerId) {
        return em.createQuery(
            "SELECT o FROM Order o " +
            "WHERE o.customerId = :cid", Order.class)
            .setParameter("cid", customerId)
            .getResultList();
    }

    public List<Order> findPendingOlderThan(Duration age) {
        LocalDateTime cutoff = LocalDateTime.now().minus(age);
        return em.createQuery(
            "SELECT o FROM Order o " +
            "WHERE o.status = 'PENDING' " +
            "AND o.createdAt < :cutoff", Order.class)
            .setParameter("cutoff", cutoff)
            .getResultList();
    }

    public void save(Order order) {
        em.merge(order);
    }

    public void delete(long id) {
        Order o = em.find(Order.class, id);
        if (o != null) em.remove(o);
    }
}
```

```java
// UNIT TESTS - InMemory implementation:
class InMemoryOrderRepository implements OrderRepository {
    private final Map<Long, Order> store = new HashMap<>();

    public Optional<Order> findById(long id) {
        return Optional.ofNullable(store.get(id));
    }
    public List<Order> findByCustomerId(long customerId) {
        return store.values().stream()
            .filter(o -> o.getCustomerId() == customerId)
            .collect(Collectors.toList());
    }
    public List<Order> findPendingOlderThan(Duration age) {
        LocalDateTime cutoff = LocalDateTime.now().minus(age);
        return store.values().stream()
            .filter(o -> o.getStatus() == PENDING
                && o.getCreatedAt().isBefore(cutoff))
            .collect(Collectors.toList());
    }
    public void save(Order order) {
        store.put(order.getId(), order);
    }
    public void delete(long id) { store.remove(id); }
}

// Fast, zero-infrastructure unit test:
class OrderServiceTest {
    @Test
    void cancelAbandonedOrders_cancelsPendingOldOrders() {
        InMemoryOrderRepository repo =
            new InMemoryOrderRepository();
        // Setup: old pending order
        Order old = new Order(1L, PENDING,
            LocalDateTime.now().minusDays(8));
        repo.save(old);
        // Setup: recent pending order (should not be cancelled)
        Order recent = new Order(2L, PENDING,
            LocalDateTime.now().minusHours(1));
        repo.save(recent);

        OrderService svc = new OrderService(repo);
        svc.cancelAbandonedOrders(Duration.ofDays(7));

        assertEquals(CANCELLED, repo.findById(1L).get().getStatus());
        assertEquals(PENDING,   repo.findById(2L).get().getStatus());
    }
}
```

---

### 🔥 Failure Scenario

**THE N+1 QUERY PROBLEM IN REPOSITORIES:**
```java
// BAD: findByCustomerId loads orders but not items (lazy).
// For each order, accessing items triggers a separate SQL.
List<Order> orders = repo.findByCustomerId(customerId);
for (Order order : orders) {
    // EACH iteration: 1 SQL SELECT to load items.
    // 100 orders = 101 SQL queries.
    order.getItems().forEach(item -> process(item));
}
```
**Symptom**: Performance degrades linearly with data volume.
**Fix**: Add a `findByCustomerIdWithItems(id)` method that
uses a JOIN FETCH (eagerly loads items in one query):
```java
"SELECT o FROM Order o " +
"JOIN FETCH o.items " +
"WHERE o.customerId = :cid"
```
The repository interface hides the query complexity;
the business layer calls the right method for the use case.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Repository = DAO | DAO = thin wrapper around one database table/SQL. Repository = domain concept, may use multiple tables/DAOs, returns domain objects in domain language |
| Repository must use an ORM | Repositories can use JDBC, NoSQL drivers, in-memory maps, HTTP clients, or file system. The interface is database-agnostic; the implementation chooses the mechanism |
| Every entity needs a repository | Only aggregate roots need repositories (DDD). Child entities within an aggregate are accessed through the root's repository |
| Generic repository (CRUD only) is sufficient | For simple CRUD: a generic repository (`CrudRepository<T, ID>`) is fine. For complex queries and domain-specific behavior: extend with specific methods. Spring Data JPA's auto-generated queries and `@Query` annotations fill this gap |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Collection-like interface to domain     │
│              │ objects. Hides data access mechanism.  │
├──────────────┼──────────────────────────────────────────┤
│ INTERFACE    │ Domain terms. findByCustomer, saveOrder.│
│              │ Not: executeSQL, query(String).        │
├──────────────┼──────────────────────────────────────────┤
│ DDD RULE     │ One repository per aggregate root.     │
│              │ No direct child entity repositories.   │
├──────────────┼──────────────────────────────────────────┤
│ TEST VALUE   │ In-memory implementation = no DB unit  │
│              │ tests. Full speed, full isolation.     │
├──────────────┼──────────────────────────────────────────┤
│ N+1 RISK     │ Use JOIN FETCH methods for collection  │
│              │ traversal. Don't rely on lazy loading. │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-080: Reactor Pattern               │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Repository = a domain-language collection over your data.
   Business code calls `findActiveOrders()` not SQL.
   The repository translates. Business logic never
   knows whether storage is MySQL, MongoDB, or an in-memory map.
2. In-memory implementation = your unit test superpower.
   No database setup. No transaction management in tests.
   Millisecond test runs. Same business logic, different
   repository implementation.
3. N+1 is the most common repository failure. Accessing
   a collection on a lazy-loaded entity inside a loop
   triggers one query per entity. Fix: add a repository
   method with JOIN FETCH for collection traversal use cases.

