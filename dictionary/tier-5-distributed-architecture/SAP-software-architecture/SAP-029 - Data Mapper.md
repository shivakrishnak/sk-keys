---
id: SAP-029
title: Data Mapper
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-021, SAP-023
used_by: SAP-021, SAP-022
related: SAP-021, SAP-028
tags:
  - architecture
  - pattern
  - deep-dive
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /software-architecture/data-mapper/
  - orm
  - advanced
---

# SAP-029 - Data Mapper

⚡ TL;DR - Data Mapper is a pattern that separates the in-memory domain model from the database schema by introducing a mapper layer that translates between them - the domain object knows nothing about persistence.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | SAP-021, SAP-023 |
| **Used by**    | SAP-021, SAP-022 |
| **Related**    | SAP-021, SAP-028 |

---

### 🔥 The Problem This Solves

**THE PROBLEM WITH TIGHT COUPLING:**
Active Record couples domain objects to the database schema - change the schema, change the object; change the object, change the schema. Domain logic can't be tested without a database. The object can't be structured differently from the table.

**THE DATA MAPPER SOLUTION:**
Introduce a layer between the domain model and the database. The domain model is designed around business concepts. The database schema is designed around storage efficiency. A Mapper translates between the two. Each side can evolve independently.

**THE REAL PAYOFF:**
You can test domain logic with no database. You can change the database schema without touching domain code. You can use multiple storage backends. You can model domain concepts that don't map 1:1 to tables.

---

### 📘 Textbook Definition

The Data Mapper pattern, defined by Martin Fowler in "Patterns of Enterprise Application Architecture," is a layer that transfers data between the in-memory objects (domain model) and the database, while keeping them independent of each other and of the mapper itself. The Data Mapper is the intermediary - it knows about both the domain object structure and the database schema, but neither the domain object nor the database knows about the other. Domain objects have no SQL, no database connection, and no persistence methods. The mapper handles all translation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A translator layer between your domain model and your database - each side is ignorant of the other.

**One analogy:**

> An interpreter at a diplomatic meeting. The French diplomat speaks French; the Japanese diplomat speaks Japanese. Neither needs to learn the other's language - the interpreter translates. If the French diplomat changes their argument, the interpreter adapts the translation without the Japanese diplomat's representation changing. If the Japanese translation conventions change, the French diplomat is unaffected. The interpreter is the Data Mapper; the diplomats are the domain model and the database.

**One insight:**
The Data Mapper allows your domain to be designed around business truth rather than database convenience. A `Money` value object, a `DateRange` with business methods, a `Status` enum - these can all exist in the domain model even if the database stores them differently (as separate columns, as integer codes, etc.).

---

### 🔩 First Principles Explanation

**THE TRANSLATION RESPONSIBILITY:**

```
┌──────────────────────────────────────────────────────────┐
│          DATA MAPPER TRANSLATION EXAMPLES                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Domain Object:          Database Schema:                │
│  Money(amount, currency) → amount DECIMAL, currency CHAR │
│  OrderStatus.SHIPPED     → status VARCHAR "SHIPPED"      │
│  PostalAddress(...)      → street, city, zip columns     │
│  Set<Tag>                → tags JOIN table               │
│  DomainEvent list        → not stored (transient)        │
│                                                          │
│  Mapper handles ALL these translations:                  │
│  domain → DB: extract fields from objects, build SQL     │
│  DB → domain: read ResultSet, construct objects          │
└──────────────────────────────────────────────────────────┘
```

**DATA MAPPER vs ACTIVE RECORD:**

```
┌──────────────────────────────────────────────────────────┐
│         KNOWLEDGE DISTRIBUTION COMPARISON                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ACTIVE RECORD:                                          │
│  Domain Object knows: data + SQL + save/find/delete      │
│  Database knows: schema                                  │
│  Result: tight coupling, fast to build, hard to decouple │
│                                                          │
│  DATA MAPPER:                                            │
│  Domain Object knows: data + business behavior           │
│  Mapper knows: domain structure + database structure     │
│  Database knows: schema                                  │
│  Result: loose coupling, more code, independent evolution│
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE TEST OF INDEPENDENCE:**
Can you test your domain object without a database?

Active Record: No - `user.save()` needs a database connection.

Data Mapper: Yes - `user = new User(...)`, call methods, assert state, no SQL touched.

**THE TEST OF EVOLUTION:**
Can your database schema and domain model change independently?

Active Record: No - they're the same thing.

Data Mapper: Yes - add a column to the database, update the mapper, domain object unchanged. Rename a domain property, update the mapper, database schema unchanged.

---

### 🧠 Mental Model / Analogy

> Data Mapper is like the adapter cable between your laptop and a projector. The laptop outputs video in one format (your domain model). The projector accepts input in another format (the database schema). The adapter cable (mapper) translates between them. The laptop doesn't know what projector is connected. The projector doesn't know what laptop it's connected to. Swap the projector (different database) - just change the adapter. Upgrade the laptop (change domain model) - just update the adapter.

Where this breaks down: unlike a cable, the Data Mapper contains actual translation logic, not just physical conversion. Complex domain concepts require sophisticated mapping code.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
A translator between your business objects and your database. The business objects don't know about the database; the database doesn't know about the business objects. A separate class handles the translation.

**Level 2 - How to use it (junior):**
In Spring with JPA, Hibernate IS the Data Mapper - it translates your `@Entity` annotated classes to database tables. The `@Column`, `@Embedded`, `@OneToMany` annotations tell the mapper how to perform the translation. Spring Data Repositories wrap Hibernate to provide the persistence API. You rarely write a mapper from scratch; you configure an ORM to act as one.

**Level 3 - How it works (mid-level):**
Hibernate's Data Mapper implementation involves three key mechanisms: 1) **Identity Map** - a cache ensuring each database row is represented by at most one in-memory object per session; 2) **Lazy Loading** - associations are loaded on demand, not eagerly, to avoid loading more data than needed; 3) **Dirty Checking** - at flush time, Hibernate compares current object state to the loaded snapshot and generates UPDATE SQL for changed properties. These mechanisms make the mapper transparent - domain code calls methods on objects, the mapper handles when and how those changes reach the database.

**Level 4 - Advanced mapping (senior/staff):**
The hardest mapping challenge is the Object-Relational Impedance Mismatch: objects have inheritance, polymorphism, and complex associations; relational tables have foreign keys, normalized rows, and no inheritance. JPA's inheritance mapping strategies (SINGLE_TABLE, TABLE_PER_CLASS, JOINED) are Data Mapper solutions to this mismatch. Value objects map to `@Embedded` or `@Embeddable`. Aggregate boundaries are enforced by controlling cascade settings. When ORM-based mapping becomes too constraining (e.g., event-sourced aggregates that don't fit table-per-state storage), you implement custom mappers that handle serialization/deserialization to document or event stores.

---

### ⚙️ How It Works (Mechanism)

**JPA as Data Mapper - translation annotations:**

```
┌──────────────────────────────────────────────────────────┐
│         JPA DATA MAPPER ANNOTATION EXAMPLES              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Domain concept → JPA mapping annotation:                │
│                                                          │
│  Value Object (Money):                                   │
│    @Embedded Money price;                                │
│    @Embeddable class Money {                             │
│      @Column(name="price_amount") BigDecimal amount;     │
│      @Column(name="price_currency") String currency;     │
│    }                                                     │
│                                                          │
│  Enum as string:                                         │
│    @Enumerated(EnumType.STRING)                          │
│    OrderStatus status;                                   │
│                                                          │
│  Collection mapping:                                     │
│    @OneToMany(mappedBy="order",                          │
│               cascade=CascadeType.ALL,                   │
│               orphanRemoval=true)                        │
│    List<OrderItem> items;                                │
│                                                          │
│  Custom type converter:                                  │
│    @Convert(converter=MoneyConverter.class)              │
│    Money totalAmount;                                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│           DATA MAPPER - END-TO-END FLOW                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Repository.findById(id)                                 │
│       ↓                                                  │
│  Hibernate executes: SELECT * FROM orders WHERE id=?     │
│       ↓                                                  │
│  Data Mapper (Hibernate):                                │
│    ResultSet → constructs Order object                   │
│    Maps columns to fields (via annotations)              │
│    Creates Money value objects from amount+currency cols │
│    Creates OrderStatus enum from VARCHAR column          │
│    Lazy-loads OrderItems (separate SELECT on access)     │
│    Stores snapshot for dirty checking                    │
│       ↓                                                  │
│  Returns: Order domain object (no SQL knowledge)         │
│                                                          │
│  order.ship(details)  ← pure domain logic, no SQL        │
│                                                          │
│  @Transactional commit:                                  │
│  Data Mapper compares current state to snapshot          │
│  Generates: UPDATE orders SET status=?, shipped_at=?     │
│  WHERE id=? AND version=? (optimistic lock)              │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Manual Data Mapper (no ORM) - explicit translation:**

```java
// Domain object - pure, no persistence knowledge
public class Order {
    private final OrderId id;
    private final CustomerId customerId;
    private Money total;
    private OrderStatus status;

    // Business methods - no SQL
    public void ship(ShippingDetails details) {
        if (status != OrderStatus.PAID) {
            throw new CannotShipUnpaidOrderException(id);
        }
        this.status = OrderStatus.SHIPPED;
    }
    // Getters for mapper access (package-private ideally)
}

// Data Mapper - knows both domain structure and DB schema
@Repository
public class JdbcOrderMapper implements OrderRepository {

    private final JdbcTemplate jdbc;

    @Override
    public Optional<Order> findById(OrderId id) {
        return jdbc.query(
            "SELECT o.id, o.customer_id, o.total_amount, " +
            "o.total_currency, o.status " +
            "FROM orders o WHERE o.id = ?",
            this::mapRowToOrder,
            id.value()
        ).stream().findFirst();
    }

    @Override
    public void save(Order order) {
        jdbc.update(
            "INSERT INTO orders(id, customer_id, " +
            "total_amount, total_currency, status) " +
            "VALUES (?,?,?,?,?) " +
            "ON CONFLICT (id) DO UPDATE SET " +
            "total_amount=?, total_currency=?, status=?",
            order.id().value(),
            order.customerId().value(),
            order.total().amount(),
            order.total().currency().code(),
            order.status().name(),
            // update params (ON CONFLICT):
            order.total().amount(),
            order.total().currency().code(),
            order.status().name()
        );
    }

    // Translation: ResultSet row → Order domain object
    private Order mapRowToOrder(ResultSet rs, int row)
            throws SQLException {
        return Order.reconstitute(
            OrderId.of(rs.getString("id")),
            CustomerId.of(rs.getString("customer_id")),
            Money.of(
                rs.getBigDecimal("total_amount"),
                Currency.of(rs.getString("total_currency"))
            ),
            OrderStatus.valueOf(rs.getString("status"))
        );
    }
}
```

**JPA-based Data Mapper - ORM handles the translation:**

```java
// JPA Entity - ORM annotations tell JPA how to map
@Entity
@Table(name = "orders")
@Access(AccessType.FIELD)  // access fields, not getters
public class Order {

    @Id
    @Column(name = "id")
    private UUID id;

    @Column(name = "customer_id")
    private UUID customerId;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name="amount",
            column=@Column(name="total_amount")),
        @AttributeOverride(name="currency",
            column=@Column(name="total_currency"))
    })
    private Money total;  // Value Object embedded in row

    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private OrderStatus status;

    // Rich domain behavior - no SQL here
    public void ship(ShippingDetails details) {
        if (status != OrderStatus.PAID) {
            throw new CannotShipUnpaidOrderException(
                OrderId.of(id));
        }
        this.status = OrderStatus.SHIPPED;
    }

    // Protected no-arg constructor for JPA (reflection)
    protected Order() {}
}
```

---

### ⚖️ Comparison Table

| Aspect             | Data Mapper                       | Active Record             |
| ------------------ | --------------------------------- | ------------------------- |
| Domain/DB coupling | Loose - mapper separates them     | Tight - domain IS the row |
| Testability        | High - domain testable without DB | Low - save/find need DB   |
| Schema evolution   | Independent of domain model       | Coupled to domain model   |
| Complexity         | Higher - mapper layer needed      | Lower - all in one class  |
| ORM example        | Hibernate/JPA                     | Rails ActiveRecord        |
| Best for           | Complex domains, DDD, clean arch  | Simple CRUD, rapid dev    |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                               |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| JPA @Entity classes ARE Active Records          | JPA is Data Mapper - the mapping is in the Entity, but the persistence operations are in the EntityManager/Repository |
| Data Mapper requires writing SQL manually       | ORMs like Hibernate implement Data Mapper - you configure the mapping, the ORM generates SQL                          |
| Data Mapper eliminates the impedance mismatch   | It manages the mismatch; the structural differences between OO and relational models remain                           |
| Data Mapper is always better than Active Record | For simple CRUD apps, Active Record is more productive and proportionate                                              |

---

### 🚨 Failure Modes & Diagnosis

**N+1 Query Problem**

**Symptom:** Loading 100 orders generates 101 SQL queries (1 for orders + 1 per order for items). Database is overwhelmed. Response times are slow.

**Root Cause:** Lazy loading in the Data Mapper. Collection associations loaded on-demand for each entity individually.

**Diagnostic Command:**

```bash
# Enable SQL logging in Spring Boot to see query count
# application.properties:
# spring.jpa.show-sql=true
# logging.level.org.hibernate.SQL=DEBUG
# logging.level.org.hibernate.type.descriptor.sql=TRACE

# Then check logs for repeated SELECT patterns:
grep "select.*from.*order_items" app.log | wc -l
# If count = N+1 for N orders loaded, you have the problem
```

**Fix:** Use `@EntityGraph` or JOIN FETCH queries to load associations in a single query. Or use projections that load only needed data.

**Prevention:** Test with realistic data volumes. N+1 is invisible with 1–5 test records but catastrophic with production data volumes.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** When two subsystems with different concerns must share data, a dedicated translation layer between them protects each subsystem from the other's changes. The translator is the only place that knows about both systems.

**Where else this pattern appears:**
- **API DTOs:** A REST API DTO (Data Transfer Object) is a Data Mapper at the HTTP boundary - it translates between the domain model (with its invariants) and the JSON representation (with its serialization constraints). The DTO is the mapper; the domain object never knows about JSON.
- **Database migration tools:** Tools like Flyway and Liquibase are Data Mappers in reverse - they translate schema changes (migrations) into the database's SQL dialect. The migration knows about both the schema version and the SQL syntax; the application knows neither.
- **Protocol Buffers / Avro:** Schema-first serialization frameworks generate mapper code that translates between language-native types and the wire format. The generated mapper is the Data Mapper at the messaging boundary.

---

### 💡 The Surprising Truth

Hibernate, often called a "Data Mapper" implementation, actually violates the Data Mapper pattern's core principle: domain objects must not know about persistence. Hibernate's `@Entity`, `@Column`, and `@OneToMany` annotations are persistence annotations placed directly on the domain object - the domain object now knows about the database schema, the table name, and the relationship mapping strategy. A pure Data Mapper would use separate mapping configuration files (Hibernate's old `hbm.xml` format was closer) or a programmatic mapping API, keeping the domain object annotation-free. Many teams using JPA/Hibernate believe they are implementing Data Mapper, but they are actually implementing a hybrid that sits between Active Record (objects annotated with persistence metadata) and true Data Mapper.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-021 - Repository Pattern (the interface that sits in front of the Data Mapper; understanding Repository explains the separation: Repository defines WHAT operations are available, Data Mapper defines HOW they are implemented)
- SAP-023 - Domain Model (Data Mapper exists to decouple the domain model from persistence; understanding what a domain model is and why it should know nothing about SQL is the motivation for Data Mapper)

**Builds On This (learn these next):**
- SAP-021 - Repository Pattern (repositories use Data Mapper internally; learning Repository shows the full persistence pattern stack)
- SAP-022 - Unit of Work Pattern (coordinates multiple Data Mapper operations into a single atomic transaction; Hibernate's Session is an implementation of both Data Mapper and Unit of Work)

**Alternatives / Comparisons:**
- SAP-028 - Active Record (simpler; domain object manages its own persistence; correct for data-centric apps; wrong for complex domains)
- SAP-021 - Repository Pattern (complementary; Repository is the interface, Data Mapper is the implementation; not alternatives but collaborators)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Translator between domain model and DB    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Domain objects know nothing about DB      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex domains, independent DB evolution │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD - Active Record is faster     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Independence + testability vs complexity  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Diplomat's interpreter: each side speaks │
│              │  its own language"                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're building an event-sourced system where the state of an `Account` aggregate is derived by replaying a sequence of events stored in an event store (not a traditional relational table). How do you implement Data Mapper for this storage model? The "mapper" can't do a simple row-to-object translation anymore - it must replay events to reconstruct the object. What does this mapper look like?

*Hint:* Research the "Aggregate Repository" pattern in event-sourced systems - specifically how the repository's `findById()` method calls `EventStore.getEventsFor(aggregateId)`, then passes those events to `Account.rehydrate(events)` which replays them. The "Data Mapper" becomes an event replayer - it maps from a sequence of events to the current aggregate state. This is the core implementation pattern in frameworks like Axon Framework (Java) and EventStoreDB.

**Q2.** Hibernate's Data Mapper requires domain objects to have a no-arg constructor (for object reconstruction from database rows). But your rich domain model uses factory methods to enforce invariants at construction time - `Order.place(customerId, items)` which validates that items is not empty. The no-arg constructor allows constructing an invalid Order. How do you satisfy Hibernate's requirement without breaking the domain model's construction invariants?

*Hint:* Research Hibernate's ability to use package-private or protected no-arg constructors (not public) - specifically that Hibernate uses reflection to bypass access modifiers when reconstructing objects from the database. A `protected Order() {}` constructor is accessible to Hibernate (via reflection) but not accessible to application code (which must use the factory method). This is the standard DDD/JPA solution. Also research JPA's `@PersistenceConstructor` annotation and Kotlin's `@NoArg` plugin.

**Q3.** You have a `Product` domain object with 50 fields, but 90% of queries only need 5 fields (name, price, SKU, stock level, category). Loading all 50 fields every time wastes memory and database bandwidth. How do you implement partial loading with Data Mapper while maintaining the invariant that a fully-loaded `Product` object is always valid?

*Hint:* Research JPA's "projection" feature - specifically `@Query` with DTO constructor expressions (JPQL) and Spring Data's interface-based projections. The key insight: projections are NOT domain objects - they are read-only views that bypass the domain model entirely. This is the CQRS insight applied to the persistence layer: for reads, you don't need a full domain object with all its invariants - you need data in the right shape for the query. Only writes need the full domain object.
