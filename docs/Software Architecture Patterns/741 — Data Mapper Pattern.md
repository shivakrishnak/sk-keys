---
layout: default
title: "Data Mapper Pattern"
parent: "Software Architecture Patterns"
nav_order: 741
permalink: /software-architecture/data-mapper-pattern/
number: "741"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Active Record Pattern, Repository Pattern, Domain Model"
used_by: "Hibernate, JPA, MyBatis, Spring Data, DDD"
tags: #advanced, #architecture, #patterns, #persistence, #orm
---

# 741 — Data Mapper Pattern

`#advanced` `#architecture` `#patterns` `#persistence` `#orm`

⚡ TL;DR — The **Data Mapper Pattern** separates the domain object from the database, using a mapper layer that moves data between them — keeping the domain model pure and independent of the persistence mechanism.

| #741            | Category: Software Architecture Patterns                | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Active Record Pattern, Repository Pattern, Domain Model |                 |
| **Used by:**    | Hibernate, JPA, MyBatis, Spring Data, DDD               |                 |

---

### 📘 Textbook Definition

The **Data Mapper** pattern (Martin Fowler, "Patterns of Enterprise Application Architecture") moves data between objects and a database while keeping them independent of each other and the mapper itself. Unlike Active Record (domain object knows its own persistence), Data Mapper creates a separate layer: (1) **Domain object**: pure business logic, no SQL, no persistence annotations. (2) **Mapper**: translates between domain object and database rows. (3) **Database**: storage, schema, queries — completely separate concern. The domain object does not depend on the database; the database does not depend on the domain object. The mapper bridges them. In modern Java: Hibernate/JPA is a Data Mapper framework — your `@Entity` class maps to the DB, but you can also implement pure Data Mapper by having a separate `JpaEntity` class and a `DomainMapper` that translates between domain objects and JPA entities.

---

### 🟢 Simple Definition (Easy)

A translator between two people who speak different languages. The domain model speaks "business language" (Order, Customer, Money). The database speaks "database language" (rows, columns, foreign keys, joins). Data Mapper: the translator in the middle. Each side can evolve independently — the business domain can reorganize without changing the database, and the database can be restructured without changing the domain model. The translator (mapper) handles all the conversion.

---

### 🔵 Simple Definition (Elaborated)

Two representations of the same data: (1) Domain Object `Order`: has an `OrderId`, a list of `OrderItem` value objects, a `Money` total, an `OrderStatus` enum — all rich domain concepts. (2) Database table `orders`: has `id`, `customer_id`, `total_amount`, `total_currency`, `status_code` — flat columns, no Java types. The Data Mapper converts between them: `toDomain(OrderJpaEntity)` → `Order`, `toJpaEntity(Order)` → `OrderJpaEntity`. Domain object: no `@Entity` annotation, no JPA dependency. Can be unit-tested without a database. Can be stored in a different database or event store tomorrow with only the mapper changing.

---

### 🔩 First Principles Explanation

**Pure Data Mapper implementation in Java (DDD-style):**

```
DATA MAPPER LAYERING:

  ┌─────────────────────────────────────────────────────────┐
  │  DOMAIN LAYER (pure Java, no persistence dependencies)  │
  │                                                          │
  │  class Order {                                           │
  │      private OrderId id;                                 │
  │      private CustomerId customerId;                      │
  │      private List<OrderItem> items;  // Value objects    │
  │      private Money total;            // Value object     │
  │      private OrderStatus status;     // Enum             │
  │      // Business methods: confirm(), cancel(), addItem() │
  │      // No @Entity, no @Table, no @Column                │
  │      // No dependency on JPA, JDBC, or any DB technology │
  │  }                                                       │
  └──────────────────────┬──────────────────────────────────┘
                         │  Data Mapper bridges the gap
  ┌──────────────────────▼──────────────────────────────────┐
  │  MAPPER LAYER (translation responsibility)               │
  │                                                          │
  │  class OrderMapper {                                     │
  │      Order toDomain(OrderJpaEntity entity,               │
  │                     List<OrderItemJpaEntity> items) {    │
  │          List<OrderItem> domainItems = items.stream()    │
  │              .map(i -> new OrderItem(                    │
  │                  ProductId.of(i.getProductId()),         │
  │                  Quantity.of(i.getQuantity()),           │
  │                  Money.of(i.getPrice(), i.getCurrency()) │
  │              )).toList();                                 │
  │                                                          │
  │          return new Order(                               │
  │              OrderId.of(entity.getId()),                 │
  │              CustomerId.of(entity.getCustomerId()),      │
  │              domainItems,                                │
  │              OrderStatus.fromCode(entity.getStatusCode())│
  │          );                                              │
  │      }                                                   │
  │                                                          │
  │      OrderJpaEntity toJpaEntity(Order order) {          │
  │          OrderJpaEntity entity = new OrderJpaEntity();   │
  │          entity.setId(order.id().value());               │
  │          entity.setCustomerId(order.customerId().value());│
  │          entity.setTotal(order.total().amount());        │
  │          entity.setCurrency(order.total().currency().name());│
  │          entity.setStatusCode(order.status().code());    │
  │          return entity;                                  │
  │      }                                                   │
  │  }                                                       │
  └──────────────────────┬──────────────────────────────────┘
                         │  Mapper works with JPA entities
  ┌──────────────────────▼──────────────────────────────────┐
  │  PERSISTENCE LAYER (JPA entities — persistence concerns) │
  │                                                          │
  │  @Entity @Table(name = "orders")                        │
  │  class OrderJpaEntity {                                  │
  │      @Id Long id;                                        │
  │      Long customerId;                                    │
  │      BigDecimal total;                                   │
  │      String currency;                                    │
  │      Integer statusCode;  // Different type from domain! │
  │      // JPA lifecycle callbacks, @Version for optimistic │
  │      // locking — infrastructure concerns, not domain.   │
  │  }                                                       │
  └─────────────────────────────────────────────────────────┘

DATA MAPPER IN REPOSITORY IMPLEMENTATION:

  interface OrderRepository {        // Domain interface (in domain layer)
      Order findById(OrderId id);
      void save(Order order);
  }

  class JpaOrderRepository implements OrderRepository {  // Infrastructure layer
      private final JpaOrderEntityRepository jpaRepo;   // Spring Data JPA repo
      private final OrderMapper mapper;

      @Override
      public Order findById(OrderId id) {
          OrderJpaEntity entity = jpaRepo.findById(id.value()).orElseThrow();
          List<OrderItemJpaEntity> items = jpaRepo.findItemsByOrderId(id.value());
          return mapper.toDomain(entity, items);         // Data Mapper converts.
      }

      @Override
      public void save(Order order) {
          OrderJpaEntity entity = mapper.toJpaEntity(order);
          jpaRepo.save(entity);
          List<OrderItemJpaEntity> itemEntities = mapper.toItemJpaEntities(order);
          jpaOrderItemRepo.saveAll(itemEntities);
      }
  }

  // Domain service uses repository — completely unaware of JPA or DB:
  class PlaceOrderService {
      void placeOrder(PlaceOrderCommand cmd) {
          Cart cart = cartRepo.findById(cmd.cartId());  // Returns domain Cart
          Order order = cart.checkout(cmd.payment());   // Domain operation
          orderRepo.save(order);                        // Data Mapper translates
          // order: pure domain object. Never saw @Entity, never knew about JPA.
      }
  }

ACTIVE RECORD vs DATA MAPPER COMPARISON:

  Active Record:
    Domain object ═══ Database row  (same class, tightly coupled)

    Benefits:
      - Less code (no mapper classes)
      - Simpler for CRUD
      - Framework support (Rails, Eloquent)

    Costs:
      - Domain structure constrained by DB schema
      - Domain object has JPA/ActiveRecord dependency
      - Hard to test domain logic without database
      - Domain can't freely use value objects (must map to columns)

  Data Mapper:
    Domain object ←→ [Mapper] ←→ Database row  (separated by mapper)

    Benefits:
      - Domain structure independent of DB schema
      - Domain is pure (no persistence imports)
      - Testable without database
      - DB can be refactored without touching domain
      - Supports complex mappings (domain ≠ DB structure)

    Costs:
      - More code (mapper classes, two object hierarchies)
      - More complexity
      - Manual mapper maintenance (or use frameworks like MapStruct)

HIBERNATE AS DATA MAPPER:

  Hibernate is a Data Mapper framework:
  - Your class: `Order` (with business logic, but @Entity annotation).
  - Hibernate: maps between your Java object and DB rows.
  - You call `session.save(order)` — Hibernate figures out the SQL.

  NOT pure Data Mapper because: @Entity annotation pollutes the domain class.
  CLOSEST to pure Data Mapper: separate JPA entity + domain class + mapper.

  Pragmatic approach (team decision):
  - Small team, simple domain: @Entity on domain class (Active Record hybrid).
  - Large team, complex domain, DDD: separate JPA entity and domain class.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Data Mapper (Active Record):

- Domain structure forced to match database schema
- Adding a new database column requires changing the domain object
- Domain object imports JPA; unit tests require database or complex mocking

WITH Data Mapper:
→ Domain structure reflects business, not database schema
→ Database schema can change without touching domain objects (only mapper changes)
→ Domain fully unit-testable: no database dependency in domain layer

---

### 🧠 Mental Model / Analogy

> A passport and a country's immigration record. You (domain object) have a passport with your identity, stamps, and personal information — in a format you control. Each country's immigration system (database) stores data about you in their own format — different fields, different structure. An immigration officer (Data Mapper) translates between your passport and the country's immigration records. You don't need to restructure yourself to enter each country. Each country's system can change its format without changing your passport.

"Your passport (your format)" = domain object (business structure)
"Country's immigration record (their format)" = database row (DB schema)
"Immigration officer (translator)" = Data Mapper
"You don't restructure for each country" = domain independent of DB

---

### ⚙️ How It Works (Mechanism)

```
DATA MAPPER: SAVE FLOW:

  Service calls: orderRepo.save(order)
      │
      ▼
  JpaOrderRepository.save(order)
      │
      ├─ mapper.toJpaEntity(order) → OrderJpaEntity (converted)
      └─ jpaRepo.save(jpaEntity)   → INSERT/UPDATE SQL executed

DATA MAPPER: LOAD FLOW:

  Service calls: orderRepo.findById(orderId)
      │
      ▼
  JpaOrderRepository.findById(orderId)
      │
      ├─ jpaRepo.findById(orderId.value()) → OrderJpaEntity (raw DB data)
      ├─ mapper.toDomain(jpaEntity)        → Order (converted to domain)
      └─ returns domain Order              ← Service receives pure domain object
```

---

### 🔄 How It Connects (Mini-Map)

```
Active Record (domain + persistence in one class — tightly coupled)
        │
        ▼ (separate persistence from domain via mapper)
Data Mapper Pattern ◄──── (you are here)
(domain object | mapper layer | persistence/DB entity — separated)
        │
        ├── Repository Pattern: Data Mapper is typically inside the Repository implementation
        ├── Domain Model: Data Mapper enables pure domain model (no persistence annotations)
        ├── ORM (Hibernate/JPA): the framework-level implementation of Data Mapper
        └── Value Objects: Data Mapper enables domain to use complex value objects (Money, Email)
```

---

### 💻 Code Example

```java
// Pure domain object — no JPA dependency:
public final class Product {
    private final ProductId id;
    private final String name;
    private final Money price;
    private final ProductStatus status;

    // Business method — no SQL, no annotation:
    public Product applyPriceIncrease(Percentage increase) {
        if (status == ProductStatus.DISCONTINUED)
            throw new DiscontinuedProductException(id);
        return new Product(id, name, price.applyIncrease(increase), status);
    }
}

// JPA entity — persistence concerns only:
@Entity @Table(name = "products")
class ProductJpaEntity {
    @Id Long id;
    String name;
    BigDecimal priceAmount;    // Money split into two columns:
    String priceCurrency;
    String statusCode;
}

// Data Mapper — translation layer:
@Component
class ProductMapper {
    Product toDomain(ProductJpaEntity e) {
        return new Product(
            ProductId.of(e.id),
            e.name,
            Money.of(e.priceAmount, Currency.getInstance(e.priceCurrency)),
            ProductStatus.fromCode(e.statusCode)
        );
    }

    ProductJpaEntity toJpaEntity(Product p) {
        ProductJpaEntity e = new ProductJpaEntity();
        e.id = p.id().value();
        e.name = p.name();
        e.priceAmount = p.price().amount();
        e.priceCurrency = p.price().currency().getCurrencyCode();
        e.statusCode = p.status().code();
        return e;
    }
}

// Repository uses mapper — domain has no persistence awareness:
@Repository
class JpaProductRepository implements ProductRepository {
    public Product findById(ProductId id) {
        return jpaRepo.findById(id.value())
                      .map(mapper::toDomain)
                      .orElseThrow(() -> new ProductNotFoundException(id));
    }
    public void save(Product product) {
        jpaRepo.save(mapper.toJpaEntity(product));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| JPA with @Entity IS the Data Mapper pattern     | JPA/Hibernate is a Data Mapper FRAMEWORK that automates the mapping. But putting @Entity on your domain class still creates coupling (domain imports JPA). Pure Data Mapper: domain class has zero persistence imports; a separate JPA entity class mirrors the DB; a mapper class translates between them. JPA on domain classes = compromise (less code, some coupling)  |
| Data Mapper is always better than Active Record | Depends on complexity and context. Data Mapper: significant extra code (mapper classes, two object hierarchies). For simple CRUD with aligned domain and DB structure, Active Record is simpler and faster. Data Mapper pays off when: domain structure differs from DB schema, domain must be tested without DB, or domain objects need to be stored in multiple backends |
| The mapper is the repository                    | Different responsibilities. Repository: domain interface for loading and saving domain objects. Data Mapper: the translation logic between domain objects and DB entities. In practice: the Repository IMPLEMENTATION contains or uses a Data Mapper. The domain sees only the Repository interface. The Data Mapper is an implementation detail inside the Repository     |

---

### 🔥 Pitfalls in Production

**Mapper leaking database concerns into the domain:**

```java
// BAD: Mapper introducing DB-specific identifiers into domain:
public Order toDomain(OrderJpaEntity entity) {
    Order order = new Order();
    order.setDatabaseId(entity.getId());       // BAD: domain now has "database ID"
    order.setVersion(entity.getVersion());     // BAD: Hibernate @Version in domain
    order.setCreatedAtTimestamp(entity.getCreatedAt()); // BAD: using SQL Timestamp type
    return order;
}

// BAD: Domain object exposes a method only needed by mapper:
class Order {
    Long getDatabaseId() { return this.databaseId; }  // Only mapper uses this. Leaks.
}

// FIX: Mapper uses domain's own identity; DB concerns stay in JPA entity:
public Order toDomain(OrderJpaEntity entity) {
    return new Order(
        OrderId.of(entity.getId()),          // Domain uses OrderId value object
        CustomerId.of(entity.getCustomerId()),
        OrderStatus.fromCode(entity.getStatusCode()),
        toOrderItems(entity.getItems())
    );
    // No DB version, no Timestamp type, no "database ID" — pure domain types.
}

// Version/optimistic locking: handle in JPA entity layer, not in domain:
@Entity class OrderJpaEntity {
    @Version Long version;  // Hibernate-specific — stays here, not in domain.
}
```

---

### 🔗 Related Keywords

- `Active Record Pattern` — the simpler alternative: domain object handles its own persistence
- `Repository Pattern` — the interface that hides Data Mapper implementation from the domain
- `Domain Model` — what Data Mapper enables: pure domain objects with no persistence coupling
- `Value Objects` — Data Mapper allows domain to use value objects that map to multiple columns
- `ORM (Object-Relational Mapping)` — Hibernate, JPA: framework implementation of Data Mapper

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Separate mapper translates between domain │
│              │ objects and DB rows. Domain: no DB        │
│              │ knowledge. DB: no domain knowledge.       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Domain structure differs from DB schema;  │
│              │ need to unit-test domain without DB;      │
│              │ DDD with rich domain model; complex       │
│              │ value objects spanning multiple columns   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD where Active Record suffices; │
│              │ small team; fast delivery priority;       │
│              │ domain and DB structures naturally align  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Passport and immigration records: each   │
│              │  has its own format; the officer          │
│              │  translates between them."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Repository Pattern → Active Record →      │
│              │ Domain Model → Value Objects              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Using Data Mapper: domain `Order` uses a `Money` value object (with `amount` BigDecimal and `currency` Currency fields). The JPA entity has `total_amount DECIMAL(10,2)` and `currency VARCHAR(3)` columns. The mapper converts between them. Now the business wants to support multi-currency orders where each `OrderItem` can have a different currency, with a `displayTotalInUsd` computed field. How does the Data Mapper pattern handle this growing complexity better than Active Record? Specifically: what changes in the domain, what changes in the mapper, and what might need to change in the DB schema?

**Q2.** A team uses pure Data Mapper (separate domain and JPA entity classes). They discover that Hibernate's `@Version` optimistic locking requires the version field to be on the JPA entity, but the domain needs to detect concurrent modification conflicts too. They propose adding a `version()` method to the domain object that returns the JPA entity's version. Is this an acceptable design? If not, how should optimistic locking concurrency conflicts be handled when the domain is kept pure (no JPA imports)?
