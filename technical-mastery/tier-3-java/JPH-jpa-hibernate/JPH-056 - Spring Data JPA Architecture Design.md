---
id: JPH-056
title: Spring Data JPA Architecture Design
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-011, JPH-014, JPH-016, JPH-023, JPH-025, JPH-026, JPH-027, JPH-036, JPH-043, JPH-054
used_by: []
related: JPH-043, JPH-053, JPH-054, JPH-055, JPH-059
tags:
  - java
  - spring
  - jpa
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/jpa-hibernate/spring-data-jpa-architecture/
---

⚡ **TL;DR** - Spring Data JPA layer design: (1) Entity
classes NEVER leak outside the persistence layer -
return DTOs/projections from services. (2) Repository
interfaces: one per aggregate root, not per table.
(3) `@Transactional` belongs on the Service layer,
not the Repository layer. (4) `@Query` on repositories
for complex queries; JOOQ for analytics. (5) `findAll()`
without `Pageable` is almost always wrong in production
(unbounded result set). (6) Spring Data projections
(interfaces, class-based DTOs) eliminate N+1 in read
paths; use them by default for list endpoints.

| #056            | Category: JPA & Hibernate                                                                                                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Entity Lifecycle, JPQL, Spring Data JPA, Spring Data Repositories, @Transactional, N+1 Problem, Criteria API, Spring Data Specifications, JPA at Scale |                 |
| **Used by:**    | -                                                                                                                                                      |                 |
| **Related:**    | Spring Data Specifications, QueryDSL, JPA at Scale, ORM Selection, Spring Data JPA Decision                                                            |                 |

---

### 🔥 The Problem This Solves

**COMMON ARCHITECTURE ANTI-PATTERNS IN SPRING DATA JPA:**

```
Anti-pattern 1: Entity leaks to controller
  @GetMapping("/products")
  public List<Product> listProducts() { // ENTITY leaked
      return productRepo.findAll();     // NO pagination
  }
  Problems:
  - JSON serialization triggers lazy loading: N+1
  - Serializes all entity fields (including sensitive ones)
  - No pagination: 1M products = 1M JSON objects in
    response
  - Controller coupled to DB schema (Product change = API
    change)

Anti-pattern 2: @Transactional on every repository method
  @Repository
  @Transactional // Applied to repository, not service
  public class ProductRepository { ... }
  Problems:
  - Multiple repository calls in one service method =
    multiple transactions
  - No atomicity across multiple saves
  - "Save order + save inventory" in 2 separate
    transactions
    = inconsistent state if second fails

Anti-pattern 3: Business logic in repositories
  public interface ProductRepository {
      @Modifying @Query("UPDATE Product p SET p.price = " +
          "p.price * 0.9 WHERE p.categoryId = :catId")
      void applyDiscountToCategory(Long catId); //
        Business logic!
  }
  Problem: business rule (10% discount) buried in data
    layer;
  hard to test, version, or compose with other business
    rules

Anti-pattern 4: N+1 in service layer
  List<Order> orders = orderRepo.findAll();
  orders.forEach(o -> {
      // Lazy loading triggers 1 query per order:
      emailService.send(o.getCustomer().getEmail());
  });
```

---

### 📘 Textbook Definition

**Spring Data JPA architecture** refers to the structural
patterns for organizing Spring Data JPA repositories,
service layers, and transaction management in production
applications.

**Architectural layers:**

| Layer          | Responsibility                                         | Spring components                           |
| -------------- | ------------------------------------------------------ | ------------------------------------------- |
| Controller/API | HTTP boundary; input validation; DTO marshaling        | `@RestController`, `@RequestBody`, `@Valid` |
| Service        | Business logic; transaction management; orchestration  | `@Service`, `@Transactional`                |
| Repository     | Data access; query definition; NOT business logic      | `@Repository`, `JpaRepository`              |
| Entity         | Persistence state; domain invariants (no anemic model) | `@Entity`, domain methods                   |
| DTO/Projection | Data transfer; decouple persistence from API           | records, interfaces, class projections      |

**Golden rules:**

1. Entities don't cross the service boundary (return DTOs)
2. `@Transactional` on service methods, not repository methods
3. One repository per aggregate root
4. No business logic in repository `@Query` methods
5. Always paginate list endpoints (`Pageable`)

---

### ⏱️ Understand It in 30 Seconds

**One line:** Well-designed Spring Data JPA architecture:
entities stay in the service layer, DTOs cross boundaries,
transactions span service methods, repositories are thin
query interfaces.

**One analogy:**

> Spring Data JPA architecture is like a restaurant's
> kitchen pass (the counter between kitchen and dining room).
> The kitchen (persistence layer) uses raw ingredients
> (entities) to prepare meals. The dining room (API layer)
> receives plates (DTOs) - never the raw ingredients.
> Entities are the raw ingredients: they carry state,
> triggers (lifecycle events), and behavior. DTOs are
> the plated dishes: optimized for presentation,
> not raw manipulation. The pass (service layer) is
> the transformation point. Customers (clients) never
> handle raw ingredients directly.

**One insight:** The #1 architectural mistake in Spring
Data JPA applications is returning entities from controller
methods. This causes: (1) JSON serialization triggering
lazy loading (N+1 in the view layer), (2) over-exposing
entity fields, (3) tight coupling between API shape and
DB schema. The fix is always to return projections or DTOs.

---

### 🔩 First Principles Explanation

**TRANSACTION OWNERSHIP - SERVICE, NOT REPOSITORY:**

```java
// BAD: @Transactional on repository methods
@Repository
public class OrderRepository extends
    JpaRepository<Order, Long> {
    @Transactional // WRONG: one tx per method
    public Order save(Order o) { ... }
}

@Service
public class OrderService {
    public void placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.create(cmd);
        orderRepo.save(order);        // Tx 1
        inventoryRepo.decrement(cmd); // Tx 2 (separate!)
        paymentRepo.record(cmd);      // Tx 3 (separate!)
        // If paymentRepo.record() fails:
        // order was committed (Tx 1), inventory decremented (Tx 2)
        // DATA INCONSISTENCY
    }
}

// GOOD: @Transactional on service method
@Service
public class OrderService {
    @Transactional // Single tx wraps all operations
    public void placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.create(cmd);
        orderRepo.save(order);        // participates in service tx
        inventoryRepo.decrement(cmd); // same tx
        paymentRepo.record(cmd);      // same tx
        // If any fails: all rollback (atomicity)
    }
}
```

---

### 🧪 Thought Experiment

**DTO VS PROJECTION VS ENTITY - WHICH WHEN:**

```java
// Scenario 1: List endpoint - 100 products, need id + name + price
// only
// Use: Spring Data PROJECTION (interface-based) - no entity loading
// overhead
public interface ProductSummary {
    Long getId();
    String getName();
    BigDecimal getPrice();
}
@Query("SELECT p.id as id, p.name as name, " +
    "p.price as price FROM Product p")
Page<ProductSummary> findAllProjected(Pageable pageable);
// Returns Hibernate proxy implementing ProductSummary - no full
// entity

// Scenario 2: Edit form - need full product with all fields
// Use: Entity (full state needed; may be modified and saved)
Optional<Product> findById(Long id);

// Scenario 3: Dashboard - aggregated data from multiple tables
// Use: DTO constructor or JOOQ (no entity overhead)
@Query("SELECT new com.example.ProductDashboardDto" +
    "(p.id, p.name, COUNT(o.id), SUM(o.total)) " +
    "FROM Product p LEFT JOIN p.orders o " +
    "GROUP BY p.id, p.name")
List<ProductDashboardDto> getDashboardData();
// DTO projection: no entity tracking; no lazy loading
```

---

### 🧠 Mental Model / Analogy

> Spring Data JPA architectural layers are like a bank's
> departments. The vault (persistence layer) holds the
> actual assets (entities). Tellers (service layer) access
> the vault and process transactions. The teller window
> display (API layer) shows only what the customer needs
> (balance, last transaction) - not the full vault
> ledger (entity). Transactions (banking sense) are
> approved by the manager (service `@Transactional`),
> not by individual vault access calls (repository
> methods). The teller never takes a customer to the vault
> (entities never leave the service boundary).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Core rules (anyone can understand):**
(1) Return DTOs from services, not entities.
(2) Put `@Transactional` on service methods.
(3) Always add `Pageable` to list queries.

**Level 2 - Repository design (junior developer):**

```java
// One repository per aggregate root (not per table):
// ORDER is the aggregate root; ORDER_ITEM is part of ORDER aggregate
public interface OrderRepository
    extends JpaRepository<Order, Long> {
    // OrderItemRepository should NOT exist
    // Order items accessed via Order.getItems()
}

// Pageable always for list endpoints:
Page<Order> findByStatus(OrderStatus status, Pageable p);
// NEVER:
List<Order> findByStatus(OrderStatus status); // unbounded
```

**Level 3 - Projection design (mid-level engineer):**

```java
// Interface projection: auto-mapped by field name
public interface OrderListItem {
    Long getId();
    @Value("#{target.customer.name}")
    String getCustomerName();    // nested property
    BigDecimal getTotal();
    OrderStatus getStatus();
    LocalDateTime getCreatedAt();
}

// Repository:
Page<OrderListItem> findAll(Pageable pageable);
// No full Order entity loaded; no customer association traversal
// (SpringData resolves @Value expressions without lazy loading)
```

**Level 4 - Custom repository implementation (senior engineer):**

```java
// For complex queries: custom repository fragment pattern
public interface OrderRepositoryCustom {
    Page<OrderListItem> searchOrders(
        OrderSearchCriteria criteria, Pageable pageable);
}

// Implementation:
@RequiredArgsConstructor
public class OrderRepositoryCustomImpl
    implements OrderRepositoryCustom {

    private final JPAQueryFactory factory;

    @Override
    public Page<OrderListItem> searchOrders(
        OrderSearchCriteria c, Pageable p) {
        QOrder o = QOrder.order;
        BooleanBuilder pred = buildPredicate(c, o);
        // ... QueryDSL implementation
    }
}

// Main repository inherits both:
public interface OrderRepository
    extends JpaRepository<Order, Long>,
    OrderRepositoryCustom {
    // Standard + custom methods in one interface
}
```

**Level 5 - Aggregate root pattern (staff engineer):**
In Domain-Driven Design, repositories correspond to
AGGREGATE ROOTS. The aggregate root is the entry point
to a cluster of related entities. Rule: you only
repository-load aggregate roots; you access child entities
only through the root. For an `Order` aggregate:
`OrderRepository` exists; `OrderItemRepository` does NOT.
The `Order.addItem()` domain method handles item creation.
This enforces domain invariants (e.g., max 50 items per
order) at the aggregate level. Spring Data JPA supports
this via cascade operations and `@Transactional` on
service methods that load the root and delegate to domain
methods. The `spring-data-commons` `@DomainEvents` annotation
supports publishing domain events on aggregate save.

---

### ⚙️ How It Works (Mechanism)

**SPRING DATA JPA PROJECTION MECHANISM:**

```java
// Interface projection - Spring Data creates a proxy:
public interface ProductSummary {
    Long getId();
    String getName();
    BigDecimal getPrice();
}

// Spring Data generates:
// SELECT p.id, p.name, p.price FROM products p
// (ONLY the 3 requested columns; not SELECT p.*)
// Returns JDK proxy implementing ProductSummary
// No Product entity object created; no 1LC tracking

// Class-based DTO projection:
public record ProductSummaryDto(Long id, String name,
    BigDecimal price) {}
// Repository:
@Query("SELECT new com.example.ProductSummaryDto" +
    "(p.id, p.name, p.price) FROM Product p")
List<ProductSummaryDto> findAllAsDto();
// JPQL: SELECT p.id, p.name, p.price (only 3 columns)
// Instantiates DTO via constructor; no entity created
```

---

### 🔄 The Complete Picture - End-to-End Flow

**COMPLETE LAYERED ARCHITECTURE EXAMPLE:**

```java
// 1. ENTITY (domain state + invariants; never crosses service
// boundary)
@Entity
public class Order {
    @Id @GeneratedValue Long id;
    @ManyToOne @JoinColumn Customer customer;
    @OneToMany(cascade = ALL, orphanRemoval = true)
    List<OrderItem> items = new ArrayList<>();
    OrderStatus status = OrderStatus.PENDING;
    BigDecimal total = BigDecimal.ZERO;

    // Domain method: enforces invariant
    public void addItem(Product product, int qty) {
        if (items.size() >= 50)
            throw new OrderLimitExceeded();
        items.add(new OrderItem(product, qty));
        recalculateTotal();
    }
}

// 2. REPOSITORY (thin query interface)
public interface OrderRepository
    extends JpaRepository<Order, Long>,
    JpaSpecificationExecutor<Order> {
    @Query("SELECT new OrderListDto(o.id, o.total, " +
        "o.status, c.name) FROM Order o JOIN o.customer c")
    Page<OrderListDto> findAllAsDto(Pageable p);
}

// 3. SERVICE (@Transactional; business orchestration)
@Service @Transactional @RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepo;
    private final ProductRepository productRepo;

    public Order placeOrder(PlaceOrderCommand cmd) {
        Customer c = customerRepo.findById(
            cmd.getCustomerId()).orElseThrow();
        Order order = new Order(c);
        cmd.getItems().forEach(item -> {
            Product p = productRepo.findById(
                item.getProductId()).orElseThrow();
            order.addItem(p, item.getQuantity());
        });
        return orderRepo.save(order);
        // Returns entity within service boundary
    }

    @Transactional(readOnly = true)
    public Page<OrderListDto> listOrders(Pageable p) {
        return orderRepo.findAllAsDto(p);
        // Returns DTO - safe to expose to controller
    }
}

// 4. CONTROLLER (maps DTO to API response; no entities)
@RestController @RequiredArgsConstructor
public class OrderController {
    private final OrderService orderService;

    @GetMapping("/orders")
    public Page<OrderListDto> list(Pageable p) {
        return orderService.listOrders(p);
        // DTO page - no lazy loading risk
    }

    @PostMapping("/orders")
    public OrderCreatedResponse create(
        @Valid @RequestBody PlaceOrderCommand cmd) {
        Order order = orderService.placeOrder(cmd);
        return new OrderCreatedResponse(order.getId());
        // Only return ID; entity not serialized
    }
}
```

---

### 💻 Code Example

**Example 1 - Testing the layered architecture:**

```java
@SpringBootTest
class OrderServiceTest {
    @Autowired OrderService orderService;
    @Autowired OrderRepository orderRepo;

    @Test
    @Transactional
    void placeOrder_shouldBeAtomic() {
        // Given: valid command
        PlaceOrderCommand cmd = buildValidCommand();

        // When: order placed
        Order order = orderService.placeOrder(cmd);

        // Then: all changes persisted in one transaction
        Order saved = orderRepo.findById(order.getId())
            .orElseThrow();
        assertThat(saved.getStatus())
            .isEqualTo(OrderStatus.PENDING);
        assertThat(saved.getItems()).hasSize(
            cmd.getItems().size());
    }

    @Test
    void listOrders_shouldReturnDtosNotEntities() {
        // When: list orders via service
        Page<OrderListDto> page =
            orderService.listOrders(
                PageRequest.of(0, 10));

        // Then: returns DTOs (no entity class exposed)
        assertThat(page.getContent())
            .allSatisfy(dto ->
                assertThat(dto)
                    .isInstanceOf(OrderListDto.class));
    }
}
```

---

### ⚖️ Comparison Table

| Pattern                          | Anti-pattern                   | Better approach                         | Benefit                                     |
| -------------------------------- | ------------------------------ | --------------------------------------- | ------------------------------------------- |
| Entity in controller return type | `@GetMapping -> List<Product>` | Return `Page<ProductDto>` or projection | No lazy load, pagination, schema decoupling |
| `@Transactional` on repository   | `@Repository @Transactional`   | `@Transactional` on `@Service`          | Atomic multi-repo operations                |
| No pagination                    | `findAll()` in controller      | `findAll(Pageable)`                     | Bounded result set; no OOM                  |
| Business logic in `@Query`       | `@Query("UPDATE... * 0.9...")` | Domain method on entity                 | Testable, composable, version-safe          |
| `OrderItemRepository` exists     | One repo per DB table          | One repo per aggregate root             | Aggregate invariants enforced               |

---

### ⚠️ Common Misconceptions

| Misconception                                                             | Reality                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Spring Data repositories are transactional by default"                   | Spring Data JPA repository implementations DO add `@Transactional` to each individual method (like `save()`, `findById()`). But these are single-method transactions. When your service calls `orderRepo.save()` + `inventoryRepo.decrement()`, each runs in its own transaction unless the service method wraps them in one `@Transactional`. The service `@Transactional` ensures multi-repo operations are atomic. |
| "Interface projections always avoid N+1"                                  | Interface projections with `@Value("#{target.association.field}")` WILL trigger lazy loading to resolve the SpEL expression. The safe alternative is a JPQL-based DTO projection with a constructor expression that JOINs the association: `SELECT NEW dto(p.id, c.name) FROM Product p JOIN p.category c`. This avoids lazy loading entirely.                                                                        |
| "Returning entities from services is fine as long as the session is open" | Open-session-in-view (OSIV) pattern keeps the session open until the HTTP response is complete. This allows lazy loading during JSON serialization (no LazyInitializationException) but at the cost of uncontrolled N+1 in the view layer. Disable OSIV in production: `spring.jpa.open-in-view=false`. This forces you to eagerly load everything the controller needs, preventing hidden lazy loading.              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: LazyInitializationException in Controller**

**Symptom:** `LazyInitializationException: could not
initialize proxy - no Session` when accessing
`order.getCustomer().getName()` in the controller.

**Root Cause:** The `@Transactional` service method
returned an `Order` entity. After the method returned,
the transaction committed and the Hibernate session
closed. The controller tries to access a lazy association
on the now-detached entity - no session available.

**Diagnosis:**

```java
// Is OSIV on or off?
# spring.jpa.open-in-view=true (default) -> no LIZE, but N+1 risk
# spring.jpa.open-in-view=false -> LIZE forces you to load eagerly
```

**Fix A (preferred):** Return a DTO from the service:

```java
return new OrderResponseDto(
    order.getId(),
    order.getCustomer().getName(), // access inside tx
    order.getTotal());
```

**Fix B:** Use `@EntityGraph` or JOIN FETCH to eagerly
load `customer` within the service transaction.
Do NOT re-enable OSIV as a solution - it hides N+1.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-026 - @Transactional]] - transaction ownership in service layer
- [[JPH-023 - Spring Data Repositories]] - repository interface design
- [[JPH-027 - N+1 Problem]] - why entities in controllers cause N+1

**Builds On This (learn these next):**

- All JPH architecture entries synthesize here

**Related:**

- [[JPH-043 - Spring Data Specifications]] - advanced filtering
  within the service layer
- [[JPH-054 - JPA at Scale]] - architecture patterns at high traffic

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LAYER RULES  │ Controller: no entities; DTOs only       │
│              │ Service: @Transactional; business logic  │
│              │ Repository: queries only; no biz logic   │
│              │ Entity: domain state + invariants        │
├──────────────┼──────────────────────────────────────────┤
│ TRANSACTION  │ @Transactional on SERVICE methods        │
│ OWNER        │ NOT on repository interface              │
├──────────────┼──────────────────────────────────────────┤
│ LIST API     │ ALWAYS return Page<DTO>; never List<Entit│
│ RULE         │ ALWAYS accept Pageable parameter         │
├──────────────┼──────────────────────────────────────────┤
│ ENTITY SCOPE │ Entity objects: created/modified in servi│
│              │ Returned to controller: DTO/record only  │
├──────────────┼──────────────────────────────────────────┤
│ REPO DESIGN  │ One per aggregate root (not one per table│
├──────────────┼──────────────────────────────────────────┤
│ OSIV         │ spring.jpa.open-in-view=false            │
│              │ Forces proper DTO mapping; no hidden N+1 │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `@Transactional` on the SERVICE layer (not repository) - ensures
   multi-repository operations are atomic
2. NEVER return entities from controllers - return DTOs or projections
   to prevent N+1 from lazy loading during serialization
3. All list endpoints MUST accept `Pageable` - `findAll()` without
   pagination is an OOM risk in production

**Interview one-liner:** Spring Data JPA architecture: (1) `@Transactional`
belongs on service methods (not repositories) to ensure multi-repo atomicity,
(2) entities never cross the service boundary - return DTOs/projections,
(3) one repository per aggregate root with `Pageable` on all list queries,
(4) disable `spring.jpa.open-in-view=false` to enforce DTO mapping.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Boundary enforcement
(preventing internal representation from leaking through
API boundaries) is a fundamental principle of layered
architecture. The entity is an internal representation
optimized for persistence (with lifecycle tracking, lazy
loading, bidirectional associations). The DTO is an external
representation optimized for the API consumer (serializable,
versioned, schema-independent). Mixing them creates coupling:
every schema change breaks the API. This same principle
appears as: domain model vs view model separation in MVC;
internal message format vs external event format in Kafka;
internal service data vs OpenAPI spec shape. The rule is
always the same: internal representations stay inside;
external representations cross boundaries. The conversion
happens at the boundary layer.

---

### 💡 The Surprising Truth

`spring.jpa.open-in-view=true` (OSIV) is the default
in Spring Boot. This means: for EVERY HTTP request, a
Hibernate `EntityManager` is opened when the request
arrives and closed when the response is fully written.
The session spans the entire HTTP request-response cycle,
not just the `@Transactional` service method. This is
why `LazyInitializationException` rarely appears in
basic Spring Boot apps - OSIV silently enables lazy
loading everywhere. The problem: this allows and HIDES
N+1 queries happening during JSON serialization
(Jackson serializes `order.customer.name`; Hibernate
executes a SELECT). Spring Boot 3.x shows a warning
when OSIV is active: "Consider configuring
`spring.jpa.open-in-view=false`". Disabling OSIV forces
you to be explicit about what data you load in the service
layer, which is the architecturally correct behavior.
Teams that run with `open-in-view=false` have fewer
production N+1 incidents because the architecture forces
correct loading upfront.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** why `@Transactional` belongs on service
   methods and the concrete failure mode when it's on repositories
2. **DESIGN** a layered service with entity loading inside
   the transaction and DTO return to the controller
3. **USE** Spring Data interface projections or constructor
   projections to avoid loading full entity objects in list queries
4. **DISABLE** OSIV and fix the `LazyInitializationException`
   that results by loading data eagerly within the transaction
5. **FOLLOW** the aggregate root pattern with one repository
   per aggregate

---

### 🎯 Interview Deep-Dive

**Q1: Why is it a problem to put `@Transactional` on a
Spring Data JPA repository method instead of a service method?**
_Why they ask:_ Tests understanding of transaction scope.
_Strong answer includes:_

- Repository `@Transactional` creates a transaction per method call
- Service calling two repos: `orderRepo.save()` + `inventoryRepo.decrement()`
  = two separate transactions (no atomicity)
- If `inventoryRepo.decrement()` throws after `orderRepo.save()` commits:
  order saved, inventory not decremented - DATA INCONSISTENCY
- Fix: `@Transactional` on service method; both repo calls participate
  in one transaction; rollback on failure rolls back both
- Note: Spring Data's default `SimpleJpaRepository` already has
  `@Transactional` on its methods internally; when a service `@Transactional`
  is active, those inner transactions use PROPAGATION_REQUIRED and JOIN
  the outer transaction

**Q2: What happens if you return an entity from a service method
and then access a lazy association in the controller?**
_Why they ask:_ Tests understanding of session lifecycle.
_Strong answer includes:_

- `@Transactional` on service method closes the session on return
- Entity is now DETACHED (no associated Hibernate session)
- Controller accesses `entity.getAssociation()` (lazy proxy) -> triggers load
- Hibernate proxy: "No session available" -> LazyInitializationException
- With OSIV (`spring.jpa.open-in-view=true`): session kept open; lazy load succeeds
  but causes N+1 during serialization
- Correct fix: return DTO from service; access lazy association INSIDE the
  `@Transactional` method before returning
