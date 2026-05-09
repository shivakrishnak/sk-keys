---
id: SAP-021
title: Repository Pattern
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-023, SAP-020, SAP-043
used_by: SAP-022
related: SAP-022, SAP-029, SAP-023
tags:
  - architecture
  - pattern
  - intermediate
  - database
  - bestpractice
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /software-architecture/repository-pattern/
---

# SAP-021 - Repository Pattern

⚡ TL;DR - The Repository Pattern provides a collection-like interface for accessing domain objects, hiding all persistence details from the domain layer.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-023, SAP-020, SAP-043 |
| **Used by**    | SAP-022                   |
| **Related**    | SAP-022, SAP-029, SAP-023 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your service classes are full of SQL strings, JDBC calls, and JPA criteria queries. Business logic methods alternate between domain rule checks and `entityManager.createQuery("FROM Order o WHERE o.status = :status")`. When you want to test whether an order discount is correctly calculated, your test must spin up a real database. When the DBA decides to change the table name, you grep through service files looking for SQL strings. When a new developer asks "how do I load orders?", the answer is "well, in `OrderService.java` there's this one way, but in `DashboardService.java` there's a different way, and in `ReportService.java`..."

**THE BREAKING POINT:**
Three service classes query the same `orders` table three different ways. When an index is added, only one query benefits because the other two use different column filters. There is no single place to go to understand how orders are persisted and loaded.

**THE INVENTION MOMENT:**
This is exactly why the Repository Pattern was created - to provide a single, well-defined collection-like interface that centralises all persistence logic for a given domain object, hiding the database completely from the rest of the application.

**EVOLUTION:**
Martin Fowler documented the Repository Pattern in "Patterns of Enterprise Application Architecture" (2002), defining it as an in-memory collection-like interface for accessing domain objects. The pattern existed informally in DAO (Data Access Object) form before that, but the key distinction is ownership: in a DAO the interface is defined by the data access layer, while in a Repository the interface is defined by the domain. Spring Data (2011 onwards) made the pattern accessible to millions of Java developers through its `JpaRepository` interface, though Spring Data's flavour blurs the domain-ownership boundary by coupling repository interfaces to JPA specifics.

---

### 📘 Textbook Definition

The Repository Pattern, documented by Martin Fowler in "Patterns of Enterprise Application Architecture" (2002) and formalized in Domain-Driven Design by Eric Evans, is a structural pattern that mediates between the domain model and the data access layer using a collection-like interface. A Repository provides methods for querying and persisting domain objects - `findById`, `findAll`, `save`, `delete` - while completely encapsulating the underlying storage technology (SQL, NoSQL, in-memory). Business logic interacts with repositories as if they were in-memory collections of domain objects.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A repository is a pretend in-memory collection that secretly talks to the database.

**One analogy:**

> A library's card catalogue (the repository) lets you ask "give me all books by Tolkien" without knowing which warehouse shelf holds them, how the shelves are organised, or whether the book is checked out. The catalogue presents a simple query interface. The actual retrieval process is completely hidden behind it.

**One insight:**
The repository contract is defined in domain language, not database language. You call `orderRepository.findPendingOrdersForCustomer(customerId)`, not `jdbcTemplate.query("SELECT * FROM orders WHERE customer_id = ? AND status = 'PENDING'", ...)`. The domain never knows that SQL exists.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The repository interface is defined in the domain package - it speaks domain language.
2. The repository implementation is in the infrastructure package - it speaks database language.
3. The domain interacts with the repository interface; it never imports the implementation.

**DERIVED DESIGN:**
The repository creates a clean boundary between two fundamentally different worlds:

- **Domain world:** objects, methods, invariants, business rules
- **Database world:** tables, rows, joins, transactions, indexes

Without a repository, these worlds intermingle. With a repository, there's a defined translation layer:

```
┌──────────────────────────────────────────────────────────┐
│              REPOSITORY PATTERN OVERVIEW                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Domain Layer                   Infrastructure Layer     │
│                                                          │
│  OrderService                   JpaOrderRepository       │
│  calls:                         implements:              │
│  orderRepo.findById(id)  →→→→   SELECT * FROM orders     │
│                                 WHERE id = ?             │
│                                 + map rows to Order obj  │
│                                                          │
│  orderRepo.save(order)   →→→→   INSERT or UPDATE         │
│                                 (ORM handles it)         │
│                                                          │
│  [Domain sees collections]   [Infra sees SQL/ORM]        │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Domain tests use an in-memory repository - zero database needed. Swapping databases (PostgreSQL → MongoDB) requires only a new implementation, not domain changes. All queries for a given entity are centralised in one class.
**Cost:** Repository interfaces can become "query dumping grounds" - over time accumulating dozens of very specific query methods that expose internal database details (`findByStatusAndRegionAndDateBetween`). This is the N+1 repository query problem. Repositories also add an abstraction layer that can hide performance issues.

---

### 🧪 Thought Experiment

**SETUP:**
You're testing a business rule: "An order cannot be placed if the customer already has 3 pending orders."

**WHAT HAPPENS WITHOUT REPOSITORY PATTERN:**
`OrderService.placeOrder()` contains: `List<Order> pending = em.createQuery("SELECT o FROM Order o WHERE o.customerId = :cid AND o.status = 'PENDING'").setParameter("cid", customerId).getResultList();`. Your test must start PostgreSQL, insert test data, and run the full JPA stack. Test takes 3 seconds. When the rule changes to "5 pending orders," you search for the magic string `'PENDING'` in service code.

**WHAT HAPPENS WITH REPOSITORY PATTERN:**
`OrderService.placeOrder()` calls `orderRepository.countPendingOrders(customerId)`. In tests, `InMemoryOrderRepository.countPendingOrders()` returns whatever you configured. Test takes 2 milliseconds. The actual SQL lives in `JpaOrderRepository.countPendingOrders()` - one place to change, one place to optimize.

**THE INSIGHT:**
The repository is the translation between two languages: domain language (what the business needs) and infrastructure language (how storage works). When this translation has one place to live, both languages stay clean.

---

### 🧠 Mental Model / Analogy

> Think of a vending machine. From the outside, you see a simple interface: press the button for "B3" and get the item. The internal mechanism - coils, coin validation, drop sensors - is completely hidden. You don't know whether items are sorted by column or by row. You don't know the restocking schedule. You interact with a simple, predictable interface; the machine handles the rest.

- "Button interface" → Repository interface (domain-language methods)
- "Coin slot, coils, drop sensor" → Repository implementation (ORM, SQL, indexes)
- "You pressing B3" → Domain service calling `findById()`
- "Factory restocking" → Infrastructure team tuning SQL queries
- "All machines have the same panel" → One interface, multiple implementations (JPA, MongoDB, in-memory)

Where this analogy breaks down: A vending machine's interface is fixed by the manufacturer. A repository's interface is designed by you - it should be discovered from domain use cases, not pre-defined.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A repository is a helper that fetches and saves objects for you, hiding all the database complexity. You say "get me order 42" and it handles everything else.

**Level 2 - How to use it (junior developer):**
Define an interface `OrderRepository` in your domain package with methods like `findById(OrderId)`, `findByCustomerId(CustomerId)`, `save(Order)`. Create an implementation `JpaOrderRepository` in the infrastructure package. Inject `OrderRepository` (the interface) into your service using dependency injection. In tests, inject `InMemoryOrderRepository` instead.

**Level 3 - How it works (mid-level engineer):**
The repository typically uses a Data Mapper to convert between domain objects and persistence entities. `Order` (domain) and `OrderEntity` (JPA annotated) may be different classes. The repository implementation loads an `OrderEntity` from JPA, maps it to an `Order` domain object, and returns it. On save, it maps `Order` back to `OrderEntity` and persists. This separation prevents JPA annotations (persistence concerns) from leaking into domain objects. Spring Data's `JpaRepository` provides basic implementations - but be careful not to expose `JpaRepository` in the domain; wrap it.

**Level 4 - Why it was designed this way (senior/staff):**
Evans' key insight in DDD was that repositories should be defined per aggregate root, not per database table. A repository for `Order` aggregate returns complete `Order` objects including `OrderItem` children - the domain consumer never needs to join manually. The domain treats the repository as an infinite in-memory collection; the ORM handles the illusion. In practice, the most insidious failure mode is designing repositories by imitating database tables (one repository per table) instead of by aggregate boundaries - leading to repositories that expose database structure rather than domain concepts.

---

### ⚙️ How It Works (Mechanism)

**Loading an aggregate via repository:**

1. **Service calls repository interface:** `Order order = orderRepository.findById(orderId);`
2. **JPA implementation executes query:** `SELECT * FROM orders WHERE id = ?` + joins for order items.
3. **ORM returns entity objects:** `OrderEntity` + `List<OrderItemEntity>`.
4. **Data Mapper converts to domain:** `OrderMapper.toDomain(entity)` → `Order` with `List<OrderItem>`.
5. **Domain object returned:** Service receives a complete `Order` with no knowledge of SQL.

**Saving an aggregate:**

1. **Service modifies domain object:** `order.addItem(item)`.
2. **Service calls save:** `orderRepository.save(order)`.
3. **Mapper converts to entity:** `OrderMapper.toEntity(order)`.
4. **JPA persists:** `entityManager.merge(entity)` - ORM generates INSERT/UPDATE.

```
┌──────────────────────────────────────────────────────────┐
│           REPOSITORY LOAD/SAVE CYCLE                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  LOAD:                                                   │
│  Service → orderRepo.findById(42)                        │
│          → [JPA implementation]                          │
│          → SELECT * FROM orders WHERE id=42              │
│          → JOIN order_items ON order_id=42               │
│          → Map rows to Order domain object               │
│          ← Order returned to service                     │
│                                                          │
│  SAVE:                                                   │
│  Service modifies order → orderRepo.save(order)          │
│          → [JPA implementation]                          │
│          → Map Order → OrderEntity                       │
│          → em.merge(entity)                              │
│          → ORM generates UPDATE + INSERT as needed       │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
POST /orders/{id}/items (AddItemToOrderCommand)
  → Controller (parse request)
  → OrderApplicationService.addItem(cmd)
  → orderRepository.findById(cmd.orderId())  ← YOU ARE HERE
  → [JPA] SELECT + JOIN → OrderEntity → Order
  → order.addItem(item) [domain rule]
  → orderRepository.save(order)
  → [JPA] UPDATE + INSERT → PostgreSQL
  → HTTP 200 OK
```

**FAILURE PATH:**

```
orderRepository.findById(unknownId) returns Optional.empty()
  → Service throws OrderNotFoundException
  → Controller maps to HTTP 404

Database connection fails
  → JPA throws DataAccessException
  → Service propagates (or wraps)
  → Controller returns HTTP 503
```

**WHAT CHANGES AT SCALE:**
At scale, repositories become performance hotspots. Repositories may need `findWithLock()` variants for concurrent modifications, batch insert methods for bulk operations, and streaming APIs (`Stream<Order>`) for large result sets. CQRS extends this by having separate read repositories (projections, denormalised views) alongside write repositories.

---

### 💻 Code Example

**Example 1 - Wrong: SQL in service layer:**

```java
// BAD - database concern in domain/service layer
@Service
public class OrderService {
    @Autowired
    private JdbcTemplate jdbc;  // direct DB dependency

    public Order getOrder(Long id) {
        // SQL in business logic class
        return jdbc.queryForObject(
            "SELECT * FROM orders WHERE id = ?",
            (rs, rowNum) -> mapRow(rs),
            id
        );
    }
}
```

**Example 2 - Right: repository interface and implementation:**

```java
// Domain layer - interface in domain package
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    List<Order> findPendingByCustomer(CustomerId cid);
    void save(Order order);
    void delete(OrderId id);
}

// Infrastructure layer - JPA implementation
@Repository
@RequiredArgsConstructor
public class JpaOrderRepository
        implements OrderRepository {
    private final OrderJpaRepository jpa;  // Spring Data
    private final OrderMapper mapper;

    @Override
    public Optional<Order> findById(OrderId id) {
        return jpa.findById(id.value())
                  .map(mapper::toDomain);
    }

    @Override
    public void save(Order order) {
        OrderEntity entity = mapper.toEntity(order);
        jpa.save(entity);
    }

    @Override
    public List<Order> findPendingByCustomer(
            CustomerId cid) {
        return jpa.findByCustomerIdAndStatus(
            cid.value(), OrderStatus.PENDING
        ).stream().map(mapper::toDomain).toList();
    }
}
```

**Example 3 - In-memory repository for tests:**

```java
// Test adapter - zero database required
class InMemoryOrderRepository
        implements OrderRepository {
    private final Map<OrderId, Order> store =
        new HashMap<>();

    @Override
    public Optional<Order> findById(OrderId id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public void save(Order order) {
        store.put(order.id(), order);
    }

    @Override
    public List<Order> findPendingByCustomer(
            CustomerId cid) {
        return store.values().stream()
            .filter(o -> o.customerId().equals(cid)
                && o.status() == PENDING)
            .toList();
    }
}
```

---

### ⚖️ Comparison Table

| Pattern                  | Abstraction level | Domain awareness     | Best For                    |
| ------------------------ | ----------------- | -------------------- | --------------------------- |
| **Repository**           | High              | Domain objects       | DDD aggregates; testability |
| DAO (Data Access Object) | Medium            | Tables/rows          | Data-centric apps           |
| Active Record            | Low               | Object=Table row     | Simple CRUD; Ruby on Rails  |
| Data Mapper              | Low (utility)     | Translates both ways | Separating ORM from domain  |

**How to choose:** Use Repository when practising DDD - it maps naturally to aggregate roots. Use DAO for simpler data-centric applications where the domain model closely mirrors the database schema. Avoid Active Record when you need to test domain logic independently.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                        |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Spring Data's JpaRepository IS a Repository       | JpaRepository is a DAO - it returns entities, not domain objects. Wrap it to create a true Repository          |
| Repositories should have one method per SQL query | Repositories should have methods named in domain language - the SQL is an implementation detail                |
| Repository per database table                     | Repository per aggregate root (DDD) - one repository may join multiple tables to load one aggregate            |
| Repositories should be thin                       | Repositories may contain complex mapping, caching, retry logic - the service just sees a simple interface      |
| Every domain object needs a repository            | Only aggregate roots need repositories - child entities are loaded through their parent aggregate's repository |

---

### 🚨 Failure Modes & Diagnosis

**Generic Repository anti-pattern (query explosion)**

**Symptom:** Repository interface grows to 40+ methods: `findByStatusAndCreatedAfterAndCustomerIdIn(...)`. Service code is full of complex predicate combinations.

**Root Cause:** Repository designed as a general-purpose query engine instead of a domain capability interface.

**Diagnostic Command / Tool:**

```bash
# Count repository methods
grep -c "findBy\|List\|Optional" \
  src/main/java/**/repository/*.java | sort -rn
```

**Fix:** Use Specification Pattern or Criteria API for dynamic queries. Keep repository methods at a domain-meaningful level of abstraction.

**Prevention:** Each repository method should correspond to a named domain concept: "findOverdueOrders" not "findByDueDateBeforeAndStatus."

---

**N+1 query (loading child entities separately)**

**Symptom:** Loading 100 orders issues 101 queries (1 for orders + 100 for each order's items). Response time grows linearly with result set size.

**Root Cause:** Lazy loading without fetch strategy - the repository returns `Order` objects that trigger database queries when `order.getItems()` is accessed.

**Diagnostic Command / Tool:**

```bash
# Enable SQL logging to see N+1 pattern
# application.properties:
spring.jpa.show-sql=true
logging.level.org.hibernate.SQL=DEBUG
# Watch for repetitive SELECT * FROM order_items
```

**Fix:** Use `@EntityGraph` or JOIN FETCH in repository queries to load children eagerly when needed.

**Prevention:** Review repository queries under realistic data volumes. Any query returning a collection of aggregates should explicitly define fetch strategy.

---

**Repository accessing child entities directly**

**Symptom:** An `OrderItemRepository` exists alongside `OrderRepository`. Service code loads items independently without going through the `Order` aggregate.

**Root Cause:** Developer needs an `OrderItem` and creates a new repository for convenience, bypassing the aggregate boundary.

**Diagnostic Command / Tool:**

```bash
# Repositories for non-aggregate-root entities
ls src/main/java/**/repository/ \
  | grep -v Order\.java | grep Repository
```

**Fix:** In DDD, only aggregate roots have repositories. Access `OrderItem` through `OrderRepository.findById(orderId).getItems()`.

**Prevention:** Define aggregate boundaries before creating repositories. Each repository should correspond to one aggregate root.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Providing a collection-like interface to a storage mechanism hides persistence complexity from consumers and enables independent substitution of the storage implementation. The consumer thinks in domain objects; the repository translates to storage primitives.

**Where else this pattern appears:**

- **File system abstraction layers:** AWS S3, Azure Blob Storage, and local disk all provide the same key-value object storage interface - applications that use `StorageRepository.save(key, bytes)` can switch storage backends without changing application code.
- **Secret management:** AWS Secrets Manager, HashiCorp Vault, and environment variables all provide `SecretRepository.get(name)` semantics - the application asks for a secret by name without knowing where it is stored.
- **Feature flags:** LaunchDarkly, Unleash, and config files all provide `FeatureFlagRepository.isEnabled(flag)` semantics - the application logic is decoupled from the flag storage and evaluation mechanism.

---

### 💡 The Surprising Truth

Spring Data's `JpaRepository<Entity, Id>` is NOT a clean Repository Pattern implementation in the DDD sense - it exposes database concepts (entity class, primary key type) in the interface signature, which means the domain must know it is being persisted with JPA. A proper DDD repository interface is defined in the domain layer without any JPA import: `OrderRepository.findById(OrderId)` returns a domain `Order`, not a JPA entity. Spring Data is a pragmatic infrastructure tool, not an architectural pattern implementation.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-023 - Domain Model (repositories return domain objects; you need a domain model before the repository has anything to return)
- SAP-020 - Ports and Adapters (Repository is a specific application of a driven port to database persistence; the domain defines the interface)
- SAP-043 - SOLID Principles (specifically the Dependency Inversion Principle; services depend on repository interfaces, not JPA implementations)

**Builds On This (learn these next):**

- SAP-022 - Unit of Work Pattern (coordinates multiple repository operations in a single atomic transaction)

**Alternatives / Comparisons:**

- SAP-029 - Data Mapper (a related but simpler pattern; maps between domain objects and database rows without the collection-like interface)
- Active Record - domain objects manage their own persistence; simpler but couples domain to the database technology

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Collection-like interface hiding all      │
│              │ database access behind domain methods     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ SQL scattered through service code;       │
│ SOLVES       │ untestable domain logic                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Interface defined in domain language;     │
│              │ SQL lives entirely in the implementation  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ DDD aggregates; domain logic to test      │
│              │ without database; infrastructure changes  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple scripts; prototype; 1-to-1 table   │
│              │ CRUD where Active Record is simpler       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Testability + infrastructure independence │
│              │ vs extra mapping code and files           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ask for objects in domain language;      │
│              │  let the repo worry about the SQL"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Unit of Work → Aggregate Root → CQRS     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service method calls `orderRepository.findById(orderId)` and then `customerRepository.findById(customerId)` to validate a business rule: "Premium customers can place orders even when their credit limit is exceeded." Each call hits the database. In a high-traffic system processing 5,000 orders/minute, what performance implications does this have, and how does the Repository Pattern structure affect your options for optimising this without changing the domain logic?

*Hint:* Research the "N+1 query problem" and how second-level caching in JPA/Hibernate can be applied at the repository implementation level without the domain service knowing about it. Also research the "specification pattern" - how a domain-defined specification object can be passed to the repository to enable the repository to use a JOIN query instead of two separate lookups, keeping SQL in the repository while letting the domain express the predicate.

**Q2.** A DDD system has a `Shipment` aggregate that contains a collection of `Packages`, and each `Package` contains a collection of `Items`. The query "find all shipments containing items with SKU X" requires a deep join through three nested levels. The domain rule is "shipments are the aggregate root - Packages and Items have no independent lifecycle." How do you design the repository interface to support this query without exposing the join structure to the domain, and what are the performance implications of your choice?

*Hint:* Research the "Specification Pattern" (from Evans' DDD) applied to repositories - specifically how `ShipmentRepository.findByItemSku(SKU sku)` encapsulates the three-level join in the repository implementation while expressing the query in domain language. Compare with the CQRS approach: for queries that require complex joins, bypass the domain model entirely and use a separate read model (a denormalised query table) populated by a projector.

**Q3.** A Spring Data `JpaRepository<OrderEntity, Long>` is used directly in domain services. A senior engineer argues this violates the Repository Pattern because the domain now imports `javax.persistence.Entity`. The team asks: is there a pragmatic middle ground between "pure DDD repositories" and "Spring Data convenience"? How do you evaluate this trade-off for a team of 8 developers on a 3-year-old codebase?

*Hint:* Research the concept of "pragmatic DDD" and specifically Martin Fowler's point that patterns are tools, not rules. Look at how Spring Data projections (interfaces that extend `JpaRepository` but return domain-specific types) can be used as a bridge - the domain layer depends on the projection interface, not the JPA entity class, reducing but not eliminating the coupling.
