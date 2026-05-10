---
id: SAP-064
title: Active Record
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-065, SAP-040
used_by:
related: SAP-040, SAP-066, SAP-041
tags:
  - architecture
  - pattern
  - intermediate
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /software-architecture/active-record/
  - orm
  - database
---

# SAP-042 - Active Record

⚡ TL;DR - Active Record is a pattern where a domain object wraps a database row and knows how to load, save, and delete itself - the object and the table row are tightly coupled by design.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-065, SAP-040          |
| **Used by**    | -                         |
| **Related**    | SAP-040, SAP-066, SAP-041 |

---

### 🔥 The Problem This Solves

**THE PROBLEM:**
Building a small web application that manages data - a blog, a CMS, a user directory. You need to create, read, update, and delete records. Setting up a full repository pattern, domain model, and data mapper is heavy infrastructure for a straightforward requirement.

**THE SOLUTION:**
Active Record gives you domain objects that manage their own persistence. `User.find(id)` loads a user. `user.save()` persists it. `user.delete()` removes it. Simple, direct, productive - the object and its database row are the same concept.

**EVOLUTION:**
Martin Fowler named Active Record as a pattern in "Patterns of Enterprise Application Architecture" (2002), but David Heinemeier Hansson made it famous by building Ruby on Rails around it (2004) - the Rails `ActiveRecord::Base` class became the canonical implementation and a major factor in Rails' popularity. Django (2005) adopted a similar approach (though Django's ORM is sometimes called "Data Mapper" due to its query API). Laravel's Eloquent (2011) continued the trend in PHP. The pattern proved so productive for web applications that it remains the dominant pattern for web frameworks today, despite DDD practitioners' criticism.

---

### 📘 Textbook Definition

Active Record, defined by Martin Fowler in "Patterns of Enterprise Application Architecture" and popularized by Ruby on Rails, is a pattern where a class maps directly to a single database table, and an instance of the class maps to a single row. The class contains both the domain data and the logic for accessing the database - it includes methods to load objects from the database, save them, and delete them, alongside any domain logic that applies to the row's data. The object and the row are the same thing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A domain object that knows its own database row - it loads itself, saves itself, and deletes itself.

**One analogy:**

> A business card that knows how to file itself. When you receive a new card, it jumps into the appropriate folder (save). When you want someone's details, the folder slot hands you their card (find). When you want to remove a contact, the card removes itself from the folder (delete). The card IS the filing system entry - there's no separate filing clerk.

**One insight:**
Active Record trades architectural cleanliness (separation of domain and persistence) for developer productivity and simplicity. It's the right trade-off for applications where the data model IS the domain model.

---

### 🔩 First Principles Explanation

**STRUCTURAL PRINCIPLE:**

```
┌──────────────────────────────────────────────────────────┐
│              ACTIVE RECORD STRUCTURE                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  class User                                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │  DATA (maps to table columns):                  │    │
│  │    id, name, email, passwordHash, createdAt     │    │
│  │                                                 │    │
│  │  PERSISTENCE METHODS:                           │    │
│  │    User.find(id)     → SELECT WHERE id=?        │    │
│  │    User.findAll()    → SELECT *                 │    │
│  │    User.findBy(...)  → SELECT WHERE ...         │    │
│  │    user.save()       → INSERT or UPDATE         │    │
│  │    user.delete()     → DELETE WHERE id=?        │    │
│  │                                                 │    │
│  │  DOMAIN METHODS (optional, if needed):          │    │
│  │    user.authenticate(password)                  │    │
│  │    user.isActive()                              │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ONE class = ONE table = ONE row per instance            │
└──────────────────────────────────────────────────────────┘
```

**THE IMPEDANCE TRADE-OFF:**

```
┌──────────────────────────────────────────────────────────┐
│         ACTIVE RECORD vs DATA MAPPER TRADE-OFF           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Active Record:                                          │
│    Domain ← tightly coupled → Database schema            │
│    Pro: Simple, fast to develop                          │
│    Con: Domain changes require DB changes, vice versa    │
│    Con: Cannot test domain logic without a database      │
│                                                          │
│  Data Mapper (Repository pattern):                       │
│    Domain ← Mapper → Database schema                     │
│    Pro: Domain evolves independently from DB schema      │
│    Pro: Domain logic testable without database           │
│    Con: More code, more moving parts                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SMALL SCALE (where Active Record wins):**
A blog platform: `Post.find(id)`, `post.publish()`, `post.save()`. Building this with repositories, aggregates, and domain events would be over-engineering. Active Record lets you ship the feature in 30 minutes.

**LARGE SCALE (where Active Record loses):**
An e-commerce platform: `Order` needs to enforce complex rules about shipping eligibility, payment states, and refund policies. `Order.save()` needs to be called carefully to avoid saving invalid intermediate states. The database schema starts constraining the domain model design. Testing becomes impossible without a test database. The tight coupling that made it fast to build is now making it painful to change.

---

### 🧠 Mental Model / Analogy

> Active Record is the ORM equivalent of a spreadsheet. A spreadsheet is fast to build, directly maps to what you're representing (rows = records), and handles simple logic well. But as your "application" grows complex with shared rules, formulas that depend on other sheets, and multi-step operations, the spreadsheet becomes tangled and fragile. At that point, you need a proper database with a domain model - not more spreadsheet.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
A domain object that manages its own database row - you call `save()` on the object to persist it, `find()` to load it, `delete()` to remove it.

**Level 2 - How to use it (junior):**
In Spring with JPA, `@Entity` classes are partly Active Record-style (they map to tables), but Spring separates the persistence methods into repositories. Pure Active Record frameworks like Rails' ActiveRecord or Django ORM build the persistence methods directly into the class. For simple CRUD apps, this is fast and productive.

**Level 3 - Design limits (mid-level):**
The core limitation: because Active Record tightly couples the domain object to the database schema, you cannot change the domain object's design without also changing the database. This makes it hard to evolve the domain model as requirements grow. Business logic in Active Record is accessible (good) but is implicitly coupled to the database schema (bad). The pattern works well for data-centric applications; it struggles for logic-centric applications.

**Level 4 - Architectural context (senior/staff):**
In Java/Spring ecosystems, pure Active Record is rare - JPA's `@Entity` provides object-relational mapping but without the `find()/save()` methods on the object itself. Spring Data repositories provide a hybrid: the mapping is on the entity, the persistence methods are on the repository. This is closer to Data Mapper. Pure Active Record is most common in Rails (Ruby), Django (Python), and Laravel (PHP) - frameworks designed around rapid development of data-driven applications. For DDD or Clean Architecture in Java, the Data Mapper / Repository pattern is preferred because it allows the domain model to evolve independently from the persistence schema.

---

### ⚙️ How It Works (Mechanism)

**Rails-style Active Record (canonical implementation):**

```
┌──────────────────────────────────────────────────────────┐
│             ACTIVE RECORD MECHANICS                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  class User < ApplicationRecord                          │
│    # Automatically maps to 'users' table                 │
│    # Columns: id, name, email, created_at                │
│                                                          │
│    # Validations (called on save())                      │
│    validates :email, presence: true, uniqueness: true    │
│    validates :name, presence: true                       │
│                                                          │
│    # Domain methods (optional)                           │
│    def active?                                           │
│      !deactivated_at.nil?                                │
│    end                                                   │
│  end                                                     │
│                                                          │
│  Usage:                                                  │
│  user = User.new(name: "Alice", email: "a@b.com")       │
│  user.save!      → INSERT INTO users ...                 │
│  User.find(1)    → SELECT * WHERE id=1                   │
│  user.update!(name: "Bob") → UPDATE users SET ...        │
│  user.destroy    → DELETE FROM users WHERE id=?          │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**Spring JPA - hybrid Active Record/Data Mapper:**

```
┌──────────────────────────────────────────────────────────┐
│         JPA: CLOSER TO DATA MAPPER THAN ACTIVE RECORD    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  @Entity class User {                                    │
│    @Id UUID id;                                          │
│    String name;                                          │
│    // NO find/save/delete methods on the object          │
│    // Mapping annotations on the entity (Active Record)  │
│    // Persistence methods on repository (Data Mapper)    │
│  }                                                       │
│                                                          │
│  interface UserRepository extends JpaRepository {        │
│    // Persistence methods separate from domain object    │
│  }                                                       │
│                                                          │
│  → JPA is a HYBRID - mapping in entity, persistence     │
│    operations in a separate repository                   │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Active Record pattern - Java simulation:**

```java
// Active Record: object manages its own persistence
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue
    private Long id;
    private String name;
    private BigDecimal price;
    private boolean active;

    // Active Record: persistence methods on the object
    // (In Java with JPA, this requires the EntityManager)
    // Pure AR: the object knows how to save itself

    // Domain method - validates business rule
    public void discontinue() {
        if (!active) {
            throw new ProductAlreadyDiscontinuedException(id);
        }
        this.active = false;
    }

    public void updatePrice(BigDecimal newPrice) {
        if (newPrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidPriceException(newPrice);
        }
        this.price = newPrice;
    }

    // In Rails this would also include find()/save()/delete()
    // In JPA, those live in ProductRepository
}
```

**Django Active Record (Python - canonical AR):**

```python
# Django ORM - classic Active Record
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10,
                                 decimal_places=2)
    active = models.BooleanField(default=True)

    # Domain method on the Active Record object
    def discontinue(self):
        if not self.active:
            raise ValueError(
                f"Product {self.id} is already discontinued")
        self.active = False
        self.save()  # persistence method on same object

    @classmethod
    def active_products(cls):
        return cls.objects.filter(active=True)  # AR query

# Usage - object saves itself
product = Product.objects.get(pk=1)  # SELECT WHERE id=1
product.discontinue()                # UPDATE + business rule
```

---

### ⚖️ Comparison Table

| Pattern            | Persistence       | Domain Logic      | Coupling                   | Best For                       |
| ------------------ | ----------------- | ----------------- | -------------------------- | ------------------------------ |
| **Active Record**  | On the object     | On the object     | Tight (DB schema = domain) | Simple CRUD, rapid prototyping |
| Data Mapper        | Separate mapper   | In domain object  | Loose                      | Complex domains, testability   |
| Repository Pattern | Separate repo     | In domain object  | Loose                      | DDD, rich domain models        |
| Transaction Script | In service method | In service method | Medium                     | Simple operations              |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                           |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| JPA @Entity classes are Active Records      | JPA entities are closer to Data Mapper - they have ORM annotations but persistence operations are in repositories |
| Active Record is always an anti-pattern     | Active Record is appropriate for data-centric applications with simple business rules                             |
| Active Record can't have business logic     | Active Record CAN include domain methods - the pattern doesn't prohibit behavior                                  |
| Active Record and Anemic Model are the same | Anemic model = no behavior; Active Record can have behavior - they're independent concepts                        |

---

### 🚨 Failure Modes & Diagnosis

**Uncontrolled saves from anywhere**

**Symptom:** `product.save()` called from 15 different places. Changing what triggers a save is nearly impossible to track.

**Root Cause:** Active Record's persistence methods are on the object and accessible everywhere. No centralized save point.

**Fix:** Move to Repository pattern. Persistence methods in a repository limit where saves can originate. This is one of the key reasons DDD applications favor repositories over Active Record.

---

**Database schema change cascades to domain**

**Symptom:** Adding a column to the database requires changing the Active Record class. Renaming a database column requires changing all references in domain methods.

**Root Cause:** Active Record maps 1:1 to the database schema. Domain and schema are the same thing.

**Fix:** For complex domains, migrate to Data Mapper / Repository pattern. The domain model and database schema can then evolve independently with an explicit mapping layer between them.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Co-locate data and its persistence operations when the cost of the coupling is outweighed by the simplicity gain. For simple, data-centric operations, the object and the database row ARE the same concept - forcing a separation adds indirection without value.

**Where else this pattern appears:**

- **Configuration objects:** A settings object that reads from a file on instantiation and writes to the file on `save()` is Active Record for configuration. The object and the persistent store are tightly coupled, and that is appropriate for configuration.
- **File system APIs:** File objects in many languages combine data (file content) with persistence operations (`read()`, `write()`, `delete()`). The file object IS the file - the Active Record pattern applied to the file system.
- **Browser localStorage:** In single-page apps, a `UserPreferences` class that reads from localStorage on load and writes on change is Active Record for the browser's local storage.

---

### 💡 The Surprising Truth

GitHub was built on Ruby on Rails Active Record and processed millions of pull requests and code reviews for years before any significant architectural shift. Shopify runs on Rails Active Record and handles billions in transactions annually. Instagram's core was built on Django's Active Record-style ORM. These are not "simple apps" that happened to use Active Record by accident - they are proof that Active Record scales further than the DDD community acknowledges. The critical factor is not the pattern itself but the size of the team and the complexity of the BUSINESS RULES, not the scale of traffic. GitHub's git operations are simple CRUD from a business logic perspective - there is nothing to gain from a domain model.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-065 - Domain Model (understanding what a rich domain model provides helps clarify Active Record's trade-off: it combines the domain object and the persistence in one class at the cost of domain purity)
- SAP-040 - Repository Pattern (the alternative persistence approach; understanding Repository shows what Active Record has coupled together)

**Builds On This (learn these next):**

- SAP-066 - Data Mapper (the pattern that separates what Active Record combines; the migration path from Active Record to Data Mapper is a standard refactoring)
- SAP-041 - Transaction Script (Active Record objects often contain Transaction Script logic for complex operations; the two patterns frequently coexist)

**Alternatives / Comparisons:**

- SAP-040 - Repository Pattern (separates persistence concerns from domain objects; correct when domain object needs to be testable without database)
- SAP-066 - Data Mapper (Fowler's term for the mapper between domain and persistence layers; Hibernate implements this)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Object = database row, manages itself     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Simplicity via tight coupling to schema   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple CRUD, data-driven apps, rapid dev  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex domain, DDD, need to test without │
│              │ database, schema evolves independently     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Dev speed + simplicity vs flexibility     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The object IS the database row"          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Ruby on Rails application using Active Record has grown to handle complex financial calculations, multi-step approvals, and multi-table operations. The `Order` Active Record class has grown to 800 lines. What is the migration path from Active Record to a repository-based architecture, and what are the specific points of coupling you'd need to break?

_Hint:_ Research the "Strangler Fig" pattern applied to ORM migration - specifically the technique of introducing a parallel `OrderRepository` class that wraps the existing ActiveRecord model, calling `Order.find()` internally but exposing a clean interface. The 800-line model reveals which behaviors have leaked into the persistence class; those behaviors become candidates for extraction to a domain service or domain object. Research how Shopify migrated parts of their Rails monolith using this approach.

**Q2.** Django ORM and Rails ActiveRecord are enormously productive for startups and rapid prototyping. Many large, successful applications (GitHub, Shopify, Instagram) were built on Active Record. Does their success invalidate the case for Data Mapper / Repository patterns, or does it say something specific about when and how those applications evolved their architectures?

_Hint:_ Research how Shopify evolved beyond pure Active Record - specifically their "Modular Monolith" approach and the introduction of service objects and form objects to handle complex business logic that doesn't belong in the Active Record model. The insight: Active Record scales for I/O complexity (traffic, data volume) but not for business logic complexity. GitHub handles complex git operations, but git operations are well-defined algorithms, not complex business rules - the domain is simple, so Active Record is appropriate indefinitely.

**Q3.** A team using Rails Active Record needs to implement an `Order` that must enforce the invariant: "An order cannot be placed if any item is out of stock, and this check must be atomic." The check requires loading stock levels from a separate `inventory` table, which Active Record's callback system (`before_save`) can handle. But the `before_save` runs inside a database transaction, creating a potential deadlock if two orders try to reserve the same stock simultaneously. How do you implement the stock check correctly with Active Record?

_Hint:_ Research database-level locking in Active Record - specifically `Product.lock.find(id)` which issues a `SELECT ... FOR UPDATE` preventing concurrent modification. Also research the "Optimistic Locking" pattern (`lock_version` column) as an alternative that avoids locks but retries on conflict. This reveals that Active Record IS capable of handling concurrency correctly, but requires understanding the underlying database locking semantics rather than relying on Ruby-level callbacks.
