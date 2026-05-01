---
layout: default
title: "Active Record Pattern"
parent: "Software Architecture Patterns"
nav_order: 740
permalink: /software-architecture/active-record-pattern/
number: "740"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Domain Model, Repository Pattern, Transaction Script"
used_by: "Ruby on Rails, Laravel Eloquent, ActiveJDBC"
tags: #intermediate, #architecture, #patterns, #orm, #persistence
---

# 740 — Active Record Pattern

`#intermediate` `#architecture` `#patterns` `#orm` `#persistence`

⚡ TL;DR — The **Active Record Pattern** wraps a database row in an object that knows how to save, find, and update itself — combining domain logic and persistence concern in one class, trading domain isolation for simplicity.

| #740            | Category: Software Architecture Patterns                  | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Domain Model, Repository Pattern, Transaction Script      |                 |
| **Used by:**    | Ruby on Rails, ActiveRecord, Laravel Eloquent, ActiveJDBC |                 |

---

### 📘 Textbook Definition

The **Active Record** pattern (Martin Fowler, "Patterns of Enterprise Application Architecture") creates an object that wraps a row in a database table, encapsulates the database access, and adds domain logic on that data. The object: (1) **Knows how to persist itself**: `user.save()`, `user.delete()`, `User.find(id)` — the object is both the domain object AND the data access object. (2) **Matches the database schema**: Active Record object structure maps directly to a database table (one field per column). (3) **Includes some domain behavior**: validation, computed properties, associations — but typically simpler than a full Domain Model. Active Record occupies the middle ground: richer than pure Transaction Script (the object has behavior), simpler than full Domain Model (no separation of persistence from domain). Popular in web frameworks: Ruby on Rails `ApplicationRecord`, Laravel `Eloquent`, Python Django ORM, ActiveJDBC. Criticized in enterprise DDD: the persistence coupling (object structure forced to match DB schema) violates domain model purity.

---

### 🟢 Simple Definition (Easy)

A person who manages their own appointments. Domain Model (separated concerns): a Patient object and a separate PatientRepository object that handles saving/loading. Active Record: a Patient who knows how to save themselves to the hospital's database — `patient.save()`, `patient.delete()`, `Patient.findByDoctorId(123)`. The patient IS the record. Good for simple cases. Gets awkward when the patient's real-world structure (domain) differs from the hospital's filing system (database schema).

---

### 🔵 Simple Definition (Elaborated)

Ruby on Rails: `class User < ApplicationRecord`. That's it. `User.find(id)`, `user.save()`, `user.update(name: "Alice")`, `user.destroy()` — the User object handles all database operations. Add validations: `validates :email, presence: true, uniqueness: true`. Add associations: `has_many :orders`. Add methods: `def premium? = subscription_type == 'premium'`. The User object is both the data AND the behavior AND the persistence. Ideal for Rails CRUD apps. In Java enterprise: DDD practitioners avoid Active Record in the domain layer because the domain object shouldn't care about SQL or JPA annotations.

---

### 🔩 First Principles Explanation

**Active Record in Java (JPA entities with behavior) vs. pure Domain Model:**

```
ACTIVE RECORD CHARACTERISTICS:

  1. OBJECT = DATABASE ROW:
     One object → one table row. Object fields → table columns.

     Active Record User:
     ┌──────────────────┬──────────────────────────────────────────────┐
     │  Java Object     │  Database Table                              │
     ├──────────────────┼──────────────────────────────────────────────┤
     │  id (Long)       │  id BIGINT PRIMARY KEY                       │
     │  email (String)  │  email VARCHAR(255)                          │
     │  name (String)   │  name VARCHAR(255)                           │
     │  status (String) │  status VARCHAR(50)                          │
     └──────────────────┴──────────────────────────────────────────────┘

     Strong coupling between domain and database. Change DB schema: change object.
     Change object structure: might break DB.

  2. SELF-SAVING METHODS:

     // Pure Active Record (Ruby Rails style):
     user = User.new(email: "user@example.com", name: "Alice")
     user.save!   // saves to DB immediately

     User.find(1)              // SELECT * FROM users WHERE id = 1
     User.where(status: 'active') // SELECT * FROM users WHERE status = 'active'

     // Java with JPA — not quite Active Record but similar when Entity has behavior:
     @Entity
     class User {
         @Id Long id;
         String email;
         UserStatus status;

         // Active Record adds behavior directly to the entity:
         public void activate() {
             if (status != PENDING) throw new IllegalStateException("Not pending");
             this.status = ACTIVE;
         }

         // But in Java, saving still requires EntityManager/Repository:
         // user.activate(); userRepo.save(user);
         // True Active Record would be: user.activate() saves itself.
     }

  3. VALIDATION IN OBJECT:

     Rails: validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }

     Java (Bean Validation on JPA entity):
     @Entity class User {
         @NotNull @Email String email;
         @NotBlank String name;
         @Size(min = 8) String passwordHash;
     }

     Validation: in the record object. Domain logic mixed with persistence annotations.

  4. ASSOCIATIONS:

     Rails:
       class Order < ApplicationRecord
         belongs_to :customer       # FK: customer_id column
         has_many :order_items      # FK: order_id in order_items table
         has_many :products, through: :order_items
       end

     JPA:
       @Entity class Order {
           @ManyToOne @JoinColumn(name = "customer_id") Customer customer;
           @OneToMany(mappedBy = "order") List<OrderItem> items;
       }

ACTIVE RECORD vs DOMAIN MODEL + REPOSITORY:

  Feature                    | Active Record          | Domain Model + Repository
  ─────────────────────────────────────────────────────────────────────────────
  Domain structure           | = DB schema structure  | Independent of DB schema
  Save/load                  | Object does it itself  | Repository does it
  Business logic             | In the record          | In the domain object
  Test domain without DB     | Hard (tight coupling)  | Easy (inject mock repo)
  Complex domain structure   | Hard (must match DB)   | Full flexibility
  Simple CRUD                | Ideal                  | Overkill
  Aggregate spanning tables  | Awkward                | Natural
  DDD Bounded Context        | Not supported          | Fully supported
  ─────────────────────────────────────────────────────────────────────────────

  WHEN ACTIVE RECORD WINS:
    - Simple CRUD application (blog, content management, admin panels).
    - Domain structure and DB structure align naturally.
    - Small team, fast delivery.
    - Framework support is strong (Rails, Laravel, Django).
    - Complex query capabilities needed from domain layer.

  WHEN DOMAIN MODEL + REPOSITORY WINS:
    - Domain structure differs from storage structure.
    - Need to test domain logic independently of database.
    - Multiple storage backends (DB + cache + event store).
    - Complex aggregates spanning multiple tables.
    - Rich domain behavior with many interacting rules.

JAVA JPA ENTITIES — Active Record OR Domain Model?

  Java JPA Entity: not pure Active Record (must call repository.save(entity)).
  But if: entity has @Entity + business behavior + validation → hybrid.

  Common Java hybrid:
    @Entity
    @Table(name = "orders")
    public class Order {
        @Id @GeneratedValue Long id;
        @Enumerated OrderStatus status;
        @OneToMany List<OrderItem> items;

        // Business behavior (Rich Domain Model part):
        public void confirm(PaymentResult payment) { ... }
        public void cancel(CancellationReason reason) { ... }

        // Persistence annotations (Active Record influence):
        // The class KNOWS its table structure via @Table/@Column.
        // Domain structure forced to match DB structure (Active Record constraint).
    }

  PURE DOMAIN MODEL approach (Spring + JPA with mapping):
    @Entity @Table(name = "orders") class OrderJpaEntity { ... }  // Persistence: separate class
    class Order { ... }                                            // Domain: pure, no annotations
    class OrderJpaMapper { Order toDomain(OrderJpaEntity e) {...} } // Mapper between them

  Tradeoff: two classes per domain concept vs. coupling domain to persistence annotations.
  Pure Domain Model: more flexible. Active Record hybrid: less code, pragmatic.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Active Record (Transaction Script + raw SQL):

- Duplicate SQL in every service method: `INSERT INTO users...` repeated everywhere
- No object to attach validation and association behavior

WITH Active Record:
→ Object knows how to persist itself: centralize DB operations
→ Framework handles associations and cascades automatically
→ Developer productivity: `User.find(id)` vs. raw JDBC or repeated repository code

---

### 🧠 Mental Model / Analogy

> A self-filing document vs. a file clerk. Domain Model + Repository: the document (domain object) knows its content and rules; the file clerk (repository) handles all filing, finding, and archiving. Active Record: the document itself knows where it's filed, can file itself, find related documents, and update its own record. Simpler for a small office with few documents. Breaks down when the document structure doesn't match the filing system, or when you need to reorganize the filing system without changing the document.

"Self-filing document" = Active Record object that saves itself
"The file clerk" = Repository pattern (separate concern)
"Document knows its own rules" = business logic in the record
"Structure must match filing system" = DB schema coupling constraint

---

### ⚙️ How It Works (Mechanism)

```
ACTIVE RECORD FLOW (Ruby on Rails example):

  Order.create(customer_id: 1, total: 99.99)
      │
      ├── Runs before_validation callbacks
      ├── Validates: presence, uniqueness, etc.
      ├── Runs before_save callbacks
      ├── Executes: INSERT INTO orders (customer_id, total) VALUES (1, 99.99)
      ├── Sets id from DB auto-increment
      └── Runs after_save callbacks

  order.update(status: "CONFIRMED")
      │
      └── Executes: UPDATE orders SET status = 'CONFIRMED' WHERE id = ?
```

---

### 🔄 How It Connects (Mini-Map)

```
Transaction Script (no domain object, pure procedure)
        │
        ▼ (more structure, persistence in object)
Active Record Pattern ◄──── (you are here)
(domain object + persistence; DB schema coupling; framework-driven)
        │
        ▼ (separate domain from persistence)
Domain Model + Repository Pattern
(pure domain object; independent persistence via Repository; DDD-ready)
```

---

### 💻 Code Example

```java
// Java quasi-Active Record with JPA (hybrid approach):
@Entity
@Table(name = "subscriptions")
public class Subscription {
    @Id @GeneratedValue Long id;
    @Column(nullable = false) String customerId;
    @Enumerated(EnumType.STRING) SubscriptionStatus status;
    @Column(nullable = false) LocalDate startDate;
    LocalDate endDate;

    // Business behavior in the record (Active Record style):
    public void cancel() {
        if (status == SubscriptionStatus.CANCELLED)
            throw new IllegalStateException("Already cancelled");
        this.status = SubscriptionStatus.CANCELLED;
        this.endDate = LocalDate.now();
    }

    public boolean isActive() {
        return status == SubscriptionStatus.ACTIVE
               && (endDate == null || LocalDate.now().isBefore(endDate));
    }

    // Rails would be: subscription.save! — Java still needs:
    // subscriptionRepo.save(subscription) — not pure Active Record
}

// Usage (service is thin — Active Record does the work):
Subscription sub = subscriptionRepo.findById(id).orElseThrow();
sub.cancel();               // Object applies rules.
subscriptionRepo.save(sub); // Save (Java step; Rails: sub.save! inside cancel())
```

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| JPA @Entity is Active Record                   | Not exactly. Pure Active Record objects save and load themselves (`user.save()`, `User.find(id)`). JPA entities require a repository or EntityManager. JPA entities are closer to a hybrid — they have the schema coupling of Active Record (fields match columns) but still need external persistence coordination. True Active Record: the object manages its own persistence. JPA: the ORM manages persistence on your behalf |
| Active Record cannot have business logic       | Active Record CAN and SHOULD have validation and domain behavior. The difference from Domain Model: Active Record's structure is constrained by the database schema (coupling). Domain Model: structure is designed for the domain, then mapped to DB by a separate layer                                                                                                                                                        |
| Active Record is always an anti-pattern in DDD | It's a tradeoff, not always wrong. In simple microservices where domain structure and DB structure align, Active Record reduces boilerplate significantly. The DDD criticism: Active Record couples the domain to the persistence layer, limiting domain model evolution. For simple domains, this coupling may be an acceptable trade-off                                                                                       |

---

### 🔥 Pitfalls in Production

**N+1 query problem from Active Record associations:**

```java
// BAD: Iterating customers and loading orders for each — N+1 queries:
List<Customer> customers = customerRepo.findAll(); // 1 query: SELECT * FROM customers
for (Customer c : customers) {
    List<Order> orders = c.getOrders(); // 1 query per customer: SELECT * FROM orders WHERE customer_id = ?
    // 100 customers = 101 queries. Active Record lazy association = N+1.
    System.out.println(c.getName() + ": " + orders.size() + " orders");
}

// FIX: Eager loading (join fetch) — 1 query with JOIN:
@Query("SELECT c FROM Customer c JOIN FETCH c.orders")
List<Customer> findAllWithOrders();
// OR in Rails: Customer.includes(:orders).all
// 1 query: SELECT customers.*, orders.* FROM customers LEFT JOIN orders...
```

---

### 🔗 Related Keywords

- `Domain Model` — richer alternative: separates persistence from domain logic
- `Repository Pattern` — the opposite approach: separate object for persistence concerns
- `Transaction Script` — simpler alternative: procedural, no domain object at all
- `Data Mapper Pattern` — pattern that maps between domain objects and DB (separates them cleanly)
- `ORM (Object-Relational Mapping)` — framework support for Active Record and Data Mapper patterns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Domain object knows its own persistence;  │
│              │ structure mirrors DB schema. Object =     │
│              │ row + behavior + DB access combined.      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple CRUD; domain structure matches DB; │
│              │ rapid development; Rails/Laravel/Django   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex domain logic; domain structure    │
│              │ differs from DB schema; need to test      │
│              │ domain without DB; DDD/Rich Domain Model  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Self-filing document: knows where it     │
│              │  lives and can file itself — simple       │
│              │  for a small office, awkward at scale."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Repository Pattern → Data Mapper →        │
│              │ Domain Model → Domain Model + Repository  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Rails application uses Active Record (`ApplicationRecord`) for all models. The `Order` model's structure exactly matches the `orders` table. Business requirement: "Permanently archive completed orders to a separate archive database after 1 year." The archive database has a different schema (denormalized, no foreign keys). How does Active Record's coupling between domain structure and DB schema create a problem here? What pattern would you use instead if this requirement were known from the start?

**Q2.** In Java with Spring + JPA, an architect debates two approaches: (A) Put business logic directly in `@Entity` classes — validates, transitions status, computes derived values. (B) Keep `@Entity` classes as pure data holders, put logic in service classes. Approach A is "Active Record hybrid." Approach B is "Anemic Domain Model." Is there a third option that is neither Active Record coupling NOR Anemic Domain Model? Describe it (hint: think about what separates the domain from the persistence layer).
