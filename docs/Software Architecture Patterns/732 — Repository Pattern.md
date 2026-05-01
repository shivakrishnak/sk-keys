---
layout: default
title: "Repository Pattern"
parent: "Software Architecture Patterns"
nav_order: 732
permalink: /software-architecture/repository-pattern/
number: "732"
category: Software Architecture Patterns
difficulty: ★★
depends_on: "Layered Architecture, Hexagonal Architecture, Domain Model"
used_by: "Spring Data JPA, Entity Framework, Hibernate, Ruby on Rails ActiveRecord"
tags: #intermediate, #architecture, #data-access, #abstraction, #persistence
---

# 732 — Repository Pattern

`#intermediate` `#architecture` `#data-access` `#abstraction` `#persistence`

⚡ TL;DR — The **Repository pattern** provides a **collection-like abstraction** over data access — the domain layer works with repositories as if they are in-memory collections, unaware of SQL, ORM, or any specific persistence technology.

| #732            | Category: Software Architecture Patterns                                 | Difficulty: ★★ |
| :-------------- | :----------------------------------------------------------------------- | :------------- |
| **Depends on:** | Layered Architecture, Hexagonal Architecture, Domain Model               |                |
| **Used by:**    | Spring Data JPA, Entity Framework, Hibernate, Ruby on Rails ActiveRecord |                |

---

### 📘 Textbook Definition

The **Repository pattern**, described by Eric Evans in "Domain-Driven Design" (2003), provides a layer of abstraction between the domain layer and the data access layer by presenting a **collection-like interface** for accessing domain objects. A repository's job: encapsulate the logic required to access data sources, so the domain layer works with domain objects directly without caring whether they come from a SQL database, a NoSQL store, a file, or an in-memory cache. The repository interface is defined in the domain layer (it specifies what operations the domain needs). The implementation is in the infrastructure layer (it uses JPA, JDBC, MongoDB driver, etc.). Key principle: **repositories work with aggregate roots** — you find or save an entire aggregate through its repository. You don't have a repository for every table; you have one per aggregate root. Benefits: testability (swap in-memory repository for tests), loose coupling (domain doesn't depend on infrastructure), single responsibility (data access in one place per aggregate). The Generic Repository anti-pattern: one `IRepository<T>` for all entities — too broad, leaks data access concerns, loses the collection-like semantics of a true repository.

---

### 🟢 Simple Definition (Easy)

A library catalog: when you want a book, you tell the librarian "find me a book about distributed systems." You don't go into the stacks yourself. The librarian knows where books are stored (database, archive, digital shelf). The catalog is the repository — you ask it for books, it returns books. You don't care if the book came from shelf A, the basement archive, or a digital copy. The catalog abstracts the storage. Change the storage system: only the librarian's procedure changes. You still ask the same way.

---

### 🔵 Simple Definition (Elaborated)

Without Repository pattern: `OrderService` directly uses `EntityManager.createQuery("SELECT o FROM Order o WHERE o.customerId = ?1")`. Problem: JPA-specific code in the service. To test: need a running database. To switch to MongoDB: rewrite the service. With Repository: `OrderService` calls `orderRepository.findByCustomerId(customerId)`. The JPA implementation is behind the interface. Test: use an `InMemoryOrderRepository` that just stores orders in a `HashMap`. Production: use `JpaOrderRepository`. The service is identical in both cases. The repository is the boundary between the domain world and the persistence world.

---

### 🔩 First Principles Explanation

**Interface design, aggregate root principle, Spring Data, and testing:**

```
REPOSITORY INTERFACE (domain layer — no JPA imports):

  // Defined IN the domain package. Domain dictates what it needs.
  // This is the "driven port" in hexagonal architecture terminology.
  public interface OrderRepository {
      Optional<Order> findById(OrderId id);
      List<Order> findByCustomerId(CustomerId customerId);
      List<Order> findByStatus(OrderStatus status);
      Order save(Order order);
      void delete(OrderId id);
      // Note: NO pagination objects, NO Specification<T>, NO JPA-specific types.
      // Only domain types (OrderId, CustomerId, OrderStatus — all domain objects).
  }

REPOSITORY IMPLEMENTATION (infrastructure layer — JPA details here):

  @Repository
  public class JpaOrderRepository implements OrderRepository {
      private final SpringDataOrderRepository jpa;  // Spring Data JPA interface.

      @Override
      public Optional<Order> findById(OrderId id) {
          return jpa.findById(id.value())           // JPA: UUID/Long.
                    .map(OrderMapper::toDomain);    // JPA entity → domain entity.
      }

      @Override
      public List<Order> findByCustomerId(CustomerId customerId) {
          return jpa.findByCustomerId(customerId.value())
                    .stream()
                    .map(OrderMapper::toDomain)
                    .collect(Collectors.toList());
      }

      @Override
      public Order save(Order order) {
          OrderJpaEntity entity = OrderMapper.toJpaEntity(order);
          OrderJpaEntity saved = jpa.save(entity);
          return OrderMapper.toDomain(saved);
      }
  }

AGGREGATE ROOT PRINCIPLE:

  Repository: one per aggregate root. NOT one per table.

  Order aggregate:
    Order (aggregate root)
    ├── OrderItem (child entity — part of Order aggregate)
    └── ShippingAddress (value object — part of Order aggregate)

  Correct: OrderRepository (for the Order aggregate root).
  WRONG: OrderItemRepository, ShippingAddressRepository (these are not aggregate roots).

  OrderItem: accessed through Order, never directly.
    // Correct:
    Order order = orderRepository.findById(orderId).orElseThrow();
    OrderItem item = order.findItem(itemId);  // Through aggregate.

    // WRONG:
    orderItemRepository.findById(itemId);  // Bypasses aggregate root. WRONG.

  Why aggregate root matters:
    Order aggregate: has invariants.
    "Total items in an order ≤ 50" is an Order-level rule.
    If you fetch/modify OrderItem directly (bypassing Order),
    you might violate this invariant without Order's knowledge.
    Repository enforces: always go through the aggregate root.

SPRING DATA JPA (repository as framework):

  Spring Data: auto-generates repository implementations from interface method names.

  public interface SpringDataOrderRepository extends JpaRepository<OrderJpaEntity, UUID> {
      List<OrderJpaEntity> findByCustomerId(UUID customerId);  // Auto-generated SQL.
      List<OrderJpaEntity> findByStatusAndCreatedAtAfter(String status, Instant after);

      @Query("SELECT o FROM OrderJpaEntity o WHERE o.total > :minTotal")
      List<OrderJpaEntity> findExpensiveOrders(@Param("minTotal") BigDecimal minTotal);
  }

  IMPORTANT DISTINCTION:
    SpringDataOrderRepository: the JPA-specific interface (infrastructure layer).
    OrderRepository: the domain interface (domain layer).
    JpaOrderRepository: wraps SpringDataOrderRepository to implement OrderRepository.

  Many teams: inject SpringDataOrderRepository directly into service classes.
  This is pragmatic but leaks JPA types into the service.
  Acceptable for simple apps; use the wrapper for clean domain separation.

IN-MEMORY REPOSITORY (for tests):

  public class InMemoryOrderRepository implements OrderRepository {
      private final Map<OrderId, Order> store = new HashMap<>();

      @Override
      public Optional<Order> findById(OrderId id) {
          return Optional.ofNullable(store.get(id));
      }

      @Override
      public List<Order> findByCustomerId(CustomerId customerId) {
          return store.values().stream()
              .filter(o -> o.customerId().equals(customerId))
              .collect(Collectors.toList());
      }

      @Override
      public Order save(Order order) {
          store.put(order.id(), order);
          return order;
      }

      @Override
      public void delete(OrderId id) {
          store.remove(id);
      }
  }

  // Test:
  @Test
  void shouldReturnOrdersForCustomer() {
      OrderRepository repo = new InMemoryOrderRepository();
      Order order = Order.create(CustomerId.of("c-1"), items);
      repo.save(order);

      List<Order> found = repo.findByCustomerId(CustomerId.of("c-1"));
      assertEquals(1, found.size());
      // No Spring context. No database. Test runs in < 10ms.
  }

THE GENERIC REPOSITORY ANTI-PATTERN:

  BAD: IRepository<T> that provides CRUD for any T:

    public interface IRepository<T, ID> {
        Optional<T> findById(ID id);
        List<T> findAll();
        T save(T entity);
        void delete(ID id);
    }

    public class GenericJpaRepository<T, ID> implements IRepository<T, ID> {
        // Generic JPA implementation for any entity type.
    }

    // Usage:
    IRepository<Order, UUID> orderRepo;
    IRepository<OrderItem, UUID> itemRepo;  // But OrderItem shouldn't have a repo!

  PROBLEMS:
    - `findAll()` on orders: no pagination, returns ALL orders. DB killer.
    - Encourages `OrderItem` repository (violates aggregate root principle).
    - No domain-specific queries: `findByCustomerId` → must use `findAll()` and filter in memory.
    - Repository loses its "collection-like API with domain semantics" meaning.

  RIGHT: Specific repositories with domain-meaningful methods:
    Optional<Order> findById(OrderId id)         ← domain type, not UUID
    List<Order> findByCustomerId(CustomerId id)  ← domain query
    // No findAll(). No generic T. No OrderItem repository.

SPECIFICATION PATTERN (for complex queries):

  When: many different filter combinations. Don't want 30 repository methods.

  public interface OrderSpecification {
      Predicate toPredicate(Root<OrderJpaEntity> root, CriteriaQuery<?> query, CriteriaBuilder cb);
  }

  // Repository:
  List<Order> findAll(OrderSpecification spec);

  // Usage:
  Specification spec = new OrdersByCustomer(customerId)
      .and(new OrdersAfterDate(afterDate))
      .and(new OrdersAboveTotal(minTotal));

  orderRepository.findAll(spec);
  // Composable, no explosion of repository methods.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Repository pattern:

- Service classes contain SQL strings or JPA queries — tied to persistence technology
- Testing services: requires a database (slow, environment-specific)
- Switch from MySQL to MongoDB: rewrite every service that touches data

WITH Repository pattern:
→ Domain services work with domain objects; persistence technology hidden behind interface
→ Test with in-memory repository: fast, no infrastructure required
→ Switch persistence technology: only change the repository implementation

---

### 🧠 Mental Model / Analogy

> A librarian (repository) for a collection of books (domain objects). You (service) tell the librarian "find me all books by Author X" — you don't care if they're on shelf 3, in digital storage, or in off-site archives. The librarian abstracts where books live. The catalog interface (repository interface) defines what you can ask for. The storage system (JPA, MongoDB) is the librarian's private knowledge. Replace the off-site archive with a digital system: the librarian's lookup changes, but you still ask the same questions.

"You asking for books" = service calling repository methods
"Librarian" = repository implementation
"Catalog interface" = repository interface (defined by domain)
"Where books live" = JPA/MongoDB/Redis (hidden implementation detail)

---

### ⚙️ How It Works (Mechanism)

```
REPOSITORY CALL FLOW:

  Service: orderRepository.findByCustomerId(customerId)
         ↓ (interface call)
  JpaOrderRepository.findByCustomerId(customerId):
    1. Convert CustomerId (domain type) → UUID (JPA type)
    2. jpa.findByCustomerId(uuid) → List<OrderJpaEntity>
    3. Map each OrderJpaEntity → Order (domain entity) via OrderMapper
    4. Return List<Order>
  Service: receives List<Order> (domain objects, no JPA types)
```

---

### 🔄 How It Connects (Mini-Map)

```
Domain Model (aggregate roots that repositories manage)
        │
        ▼ (abstract data access for domain objects)
Repository Pattern ◄──── (you are here)
(interface in domain; implementation in infrastructure)
        │
        ├── Hexagonal Architecture: repository is a "driven port" (secondary adapter)
        ├── Unit of Work Pattern: coordinates transactions across multiple repositories
        └── Specification Pattern: composable query objects for complex filtering
```

---

### 💻 Code Example

```java
// Clean repository: domain interface + JPA implementation:

// DOMAIN LAYER (no persistence imports):
public interface ProductRepository {
    Optional<Product> findById(ProductId id);
    List<Product> findByCategoryAndInStock(Category category);  // Domain-meaningful query.
    Product save(Product product);
    // No findAll(). No deleteAll(). Only operations the domain actually needs.
}

// INFRASTRUCTURE LAYER:
@Repository
public class JpaProductRepository implements ProductRepository {
    private final JpaProductStore store;

    @Override
    public Optional<Product> findById(ProductId id) {
        return store.findById(id.value()).map(ProductMapper::toDomain);
    }

    @Override
    public List<Product> findByCategoryAndInStock(Category category) {
        return store.findByCategoryAndStockGreaterThan(category.name(), 0)
                    .stream().map(ProductMapper::toDomain).toList();
    }

    @Override
    public Product save(Product product) {
        return ProductMapper.toDomain(store.save(ProductMapper.toJpa(product)));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Repository pattern is just a DAO (Data Access Object) | DAO: low-level data access, often maps to database tables, works with raw data/entities. Repository: higher-level, domain-centric, works with aggregate roots, presents collection-like semantics. DAO might have `updateStatusColumn(id, status)`. Repository would have `save(order)` (the whole aggregate). Repository is more DDD-aligned; DAO is more data-centric                                                              |
| Spring Data's JpaRepository IS the Repository pattern | Spring Data's JpaRepository is an infrastructure detail. It extends CrudRepository and PagingAndSortingRepository — providing generic CRUD. The Repository pattern's repository interface is domain-defined, returns domain types, has only domain-meaningful methods. Inject JpaRepository directly into services: pragmatic, but leaks infrastructure types. True DDD Repository: wrap JpaRepository in a domain-defined interface |
| You need a repository for every entity                | Repositories are for aggregate roots only. An aggregate root: the entity that is the "entry point" for an aggregate. Child entities (OrderItem, Address) are accessed through the aggregate root's repository. Creating a repository for every entity: bypasses aggregate boundaries, allows invariant violations, creates unnecessary infrastructure code                                                                           |

---

### 🔥 Pitfalls in Production

**N+1 query problem — repository loads aggregates one at a time in a loop:**

```
SCENARIO: Show a page of orders (20 orders) with customer names.

  OrderRepository:
    List<Order> findRecentOrders(int page, int size);
    // Returns 20 Order objects. Each Order has a customerId.

  Service (BUGGY):
  public List<OrderSummaryDTO> getRecentOrdersPage(int page, int size) {
      List<Order> orders = orderRepository.findRecentOrders(page, size);  // 1 query.

      List<OrderSummaryDTO> result = new ArrayList<>();
      for (Order order : orders) {
          // BUG: fetching customer for each order individually:
          Customer customer = customerRepository.findById(order.customerId()).orElseThrow();
          // ^ 1 query per order. 20 orders = 20 queries here.
          result.add(new OrderSummaryDTO(order.id(), customer.name(), order.total()));
      }
      return result;
  }

  TOTAL QUERIES: 1 (orders) + 20 (customers) = 21 queries for 20 results.
  N+1 query problem. At 1000 requests/second: 21,000 DB queries/sec. DB overwhelmed.

BAD: Loading related aggregates individually in a loop:
  for (Order order : orders) {
      customerRepository.findById(order.customerId());  // 1 query per order. N+1.
  }

FIX 1: Add a batch-loading method to the repository:
  // OrderRepository: add a method for this specific query pattern:
  List<OrderWithCustomerDTO> findRecentOrdersWithCustomer(int page, int size);

  // Implementation: single JOIN query:
  @Query("SELECT new OrderWithCustomerDTO(o.id, c.name, o.total) " +
         "FROM Order o JOIN Customer c ON o.customerId = c.id " +
         "ORDER BY o.createdAt DESC LIMIT :size OFFSET :offset")
  List<OrderWithCustomerDTO> findRecentOrdersWithCustomer(...);
  // 1 query. 21x improvement.

FIX 2: Use DataLoader / batch loading for the common pattern:
  // Load all customer IDs first, then batch fetch:
  List<Order> orders = orderRepository.findRecentOrders(page, size);
  Set<CustomerId> customerIds = orders.stream().map(Order::customerId).collect(toSet());
  Map<CustomerId, Customer> customers = customerRepository.findByIds(customerIds);  // 1 batch query.
  // Map orders to DTOs using the fetched customer map.

  // CustomerRepository: add batch method:
  Map<CustomerId, Customer> findByIds(Set<CustomerId> ids);
  // Implementation: SELECT WHERE id IN (...) — single query regardless of set size.

FIX 3: For reads, consider bypassing aggregate repositories and using direct SQL projections:
  // QueryHandler (read path — not going through domain repositories):
  @Query("SELECT o.id, c.name, o.total FROM orders o JOIN customers c ON o.customer_id = c.id " +
         "ORDER BY o.created_at DESC LIMIT ? OFFSET ?")
  List<OrderSummaryDTO> getOrdersPage(int page, int size);
  // Pure read. No domain loading. No N+1. Fast.
  // Appropriate in CQRS read path where domain rules aren't needed.
```

---

### 🔗 Related Keywords

- `Unit of Work Pattern` — coordinates multiple repository operations into a single transaction
- `Aggregate Root` — the DDD concept that determines what has a repository
- `Hexagonal Architecture` — repository is the "driven port" for data access
- `Specification Pattern` — composable query objects for complex repository filtering
- `Domain Model` — the domain entities and aggregates that repositories manage

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Collection-like interface for domain      │
│              │ objects. Domain says what it needs        │
│              │ (interface). Infrastructure says how      │
│              │ (implementation). One per aggregate root. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Domain needs to be decoupled from DB;    │
│              │ testability important; DDD project;      │
│              │ multiple data sources possible           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD app; Spring Data JPA covers  │
│              │ needs directly; no domain complexity     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Librarian: you ask for books by title  │
│              │  or author; you don't enter the stacks."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Unit of Work → Aggregate Root → Domain  │
│              │ Model → Specification Pattern → DDD      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your `OrderRepository` interface has `findById(OrderId)` and `findByCustomerId(CustomerId)`. A new performance requirement: "The order list page must return 50 orders with customer names and total item counts in under 50ms." This requires a JOIN query across 3 tables. Where does this query go? In the `OrderRepository`? A separate `OrderReadRepository`? A query object? Design the solution and explain how it interacts with CQRS principles.

**Q2.** An `Order` aggregate contains `OrderItems`. You have `OrderRepository`. A business operation: "Cancel all orders that contain a specific discontinued product SKU." This requires finding all `OrderItem`s with a given SKU, getting their parent `Order`s, and cancelling those orders. Write the solution using only `OrderRepository` (no `OrderItemRepository`). What query method do you add to `OrderRepository`? Is there a risk of loading too many orders at once? How do you handle pagination for this bulk operation?
