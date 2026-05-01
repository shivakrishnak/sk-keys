---
layout: default
title: "Anemic Domain Model"
parent: "Software Architecture Patterns"
nav_order: 737
permalink: /software-architecture/anemic-domain-model/
number: "737"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Domain Model, Object-Oriented Programming"
used_by: "Transaction Script, Spring Service layer"
tags: #intermediate, #architecture, #antipattern, #ddd, #oop
---

# 737 — Anemic Domain Model

`#intermediate` `#architecture` `#antipattern` `#ddd` `#oop`

⚡ TL;DR — An **Anemic Domain Model** is an OOP anti-pattern where domain objects are pure data containers (getters/setters only) and all business logic lives in separate Service classes — violating encapsulation and the object-oriented principle of behavior + data together.

| #737            | Category: Software Architecture Patterns  | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | Domain Model, Object-Oriented Programming |                 |
| **Used by:**    | Transaction Script, Spring Service layer  |                 |

---

### 📘 Textbook Definition

The **Anemic Domain Model** (Martin Fowler's "Patterns of Enterprise Application Architecture," 2002) describes domain objects that contain only data — fields with getter and setter methods — while all domain logic (validation, computation, state transitions, business rules) lives in external Service classes. Fowler called it "fundamentally contrary to the basic idea of object-oriented design, which is to combine data and process together." The hallmarks: (1) Domain objects are plain data-transfer objects (DTOs) with only `get*` and `set*` methods. (2) Service classes are massive: 200–500 line "procedure gods" with deep knowledge of multiple domain objects' internal structure. (3) Services directly mutate domain objects via setters instead of asking the object to do something. (4) Ubiquitous Language is absent: code says `processor.executeUserDataModificationRoutine()`, not `customer.upgradeToPreimum()`. The anti-pattern arises from applying OOP class syntax but procedural thinking: classes as struct/record containers, procedures as services.

---

### 🟢 Simple Definition (Easy)

A filing cabinet vs. a bank teller. Anemic Domain Model: the bank account is just a filing cabinet that holds numbers. The bank teller (Service class) does everything — opens the cabinet, reads the balance, applies rules, updates the balance, closes the cabinet. The cabinet has no say. Millions of "teller" classes all need to know the cabinet's internal structure. Change the cabinet format: update every teller. Better: a bank account that knows its own rules — "I won't let you overdraw me." The account (domain object) has behavior. The teller (service) just asks: "please withdraw $100."

---

### 🔵 Simple Definition (Elaborated)

A Java Spring application using JPA entities: `User.java` has `id`, `email`, `password`, `premiumUntil`, `accountStatus` — plus 20 getters and setters. No business logic. `UserService.java`: 600 lines — `activateAccount()`, `deactivateAccount()`, `upgradeToPremium()`, `applyDiscount()`, `calculateLoyaltyPoints()` — all directly calling `user.setStatus("ACTIVE")`, `user.setPremiumUntil(date)`, `user.setLoyaltyPoints(points)`. The service knows: how to compute loyalty points, which statuses can transition to which, when premium expires. Anemic Domain Model: domain objects as passive data bags, services as god-procedures. Every service must know every domain object's internal structure to do its job.

---

### 🔩 First Principles Explanation

**Why it arises, what it costs, how to recognize it:**

```
ANEMIC vs RICH — same feature, two styles:

  Feature: "A customer upgrades to Premium. Apply 10% loyalty bonus to existing balance.
            Premium expires 1 year from today. Cannot upgrade if account is suspended."

  ANEMIC DOMAIN MODEL (data in object, logic in service):

    class Customer {                           // Pure data bag:
        private Long id;
        private String status;                  // "ACTIVE", "SUSPENDED", "PREMIUM"
        private BigDecimal loyaltyBalance;
        private LocalDate premiumExpiresAt;

        // 20 getters and setters. No logic. No validation.
        public void setStatus(String s) { this.status = s; }
        public String getStatus() { return this.status; }
        public void setLoyaltyBalance(BigDecimal b) { this.loyaltyBalance = b; }
        public BigDecimal getLoyaltyBalance() { return this.loyaltyBalance; }
        public void setPremiumExpiresAt(LocalDate d) { this.premiumExpiresAt = d; }
        // ... 16 more getters/setters
    }

    class CustomerService {
        public void upgradeToPremium(Long customerId) {
            Customer c = customerRepo.findById(customerId)
                                     .orElseThrow(CustomerNotFoundException::new);

            // Business rules in SERVICE, not in Customer:
            if ("SUSPENDED".equals(c.getStatus())) {
                throw new InvalidOperationException("Cannot upgrade suspended account");
            }
            if ("PREMIUM".equals(c.getStatus())) {
                throw new InvalidOperationException("Already premium");
            }

            // Direct mutation via setters — service manipulates internal state:
            BigDecimal bonus = c.getLoyaltyBalance().multiply(new BigDecimal("0.10"));
            c.setLoyaltyBalance(c.getLoyaltyBalance().add(bonus));
            c.setStatus("PREMIUM");
            c.setPremiumExpiresAt(LocalDate.now().plusYears(1));

            customerRepo.save(c);
        }
    }

  PROBLEMS:
    1. DUPLICATED RULES: If CustomerControllerTests, CustomerBatchProcessor,
       CustomerApiHandler all need to upgrade customers: they duplicate the check.
       Or they all call the service, which helps; but the service grows to 800 lines.

    2. INVALID STATE POSSIBLE: CustomerRepo.save(customer) with manually set status:
       customer.setStatus("PREMIUM");        // Valid state.
       customer.setPremiumExpiresAt(null);   // Invalid! Premium without expiry.
       // But Customer class can't prevent this. It just accepts the setter call.

    3. SERVICES MUST KNOW INTERNALS: CustomerService needs to know:
       - Status is stored as a String ("ACTIVE", "SUSPENDED", "PREMIUM").
       - Loyalty balance is a BigDecimal (not Money, not LoyaltyPoints).
       - Premium expiry is a LocalDate (not Instant, not ZonedDateTime).
       Customer's internal representation leaks into every service that uses it.

    4. REFACTORING RIPPLE: Change `status` from String to enum CustomerStatus?
       Update every service that calls customer.setStatus("ACTIVE").

  RICH DOMAIN MODEL (logic in object):

    class Customer {
        private CustomerId id;
        private CustomerStatus status;             // Enum: ACTIVE, SUSPENDED, PREMIUM.
        private LoyaltyBalance loyaltyBalance;     // Value object.
        private LocalDate premiumExpiresAt;

        public void upgradeToPremium() {           // Rules LIVE here:
            if (status == SUSPENDED) throw new SuspendedAccountException();
            if (status == PREMIUM) throw new AlreadyPremiumException();

            this.loyaltyBalance = loyaltyBalance.applyBonus(Percentage.TEN);  // VOs do math.
            this.status = PREMIUM;
            this.premiumExpiresAt = LocalDate.now().plusYears(1);

            register(new CustomerUpgradedEvent(id, premiumExpiresAt)); // Domain event.
        }

        public boolean isSuspended() { return status == SUSPENDED; }
        public boolean isPremium() { return status == PREMIUM; }
    }

    class CustomerService {
        public void upgradeToPremium(Long customerId) {
            Customer customer = customerRepo.findById(customerId)...;
            customer.upgradeToPremium();  // 1 line. Rules in object.
            customerRepo.save(customer);
        }
    }

  BENEFITS:
    1. Rules in ONE place: Customer.upgradeToPremium() is the single source of truth.
    2. Invalid state impossible: Customer controls all its state transitions.
    3. Services don't need internals: just call the method; don't care how it works.
    4. Refactoring local: change status internal representation → only Customer changes.

ANEMIC DOMAIN MODEL RECOGNITION CHECKLIST:

  ☐ Domain classes have mostly get/set methods with no behavior.
  ☐ Service class method names include the domain class name:
      "activateUser()", "processOrder()", "updateAccount()" — in a Service, not in the domain object.
  ☐ Service methods load domain object, call getters to read state, call setters to mutate it.
  ☐ "Cannot do X if status is Y" rules live in services, not in domain objects.
  ☐ Domain experts can't read the domain object code to understand the rules.
  ☐ Multiple service classes have duplicated validation logic.

WHEN ANEMIC DOMAIN MODEL IS ACCEPTABLE:

  NOT everything needs a Rich Domain Model:

  Simple CRUD (Blog post content management):
    Post.title = req.title; post.body = req.body; postRepo.save(post);
    → No complex rules. Transaction Script or Active Record is fine.

  Query models (CQRS read side):
    OrderSummary: just a data bag for displaying order history. No behavior needed.
    → DTOs and read models: intentionally anemic.

  API Request/Response objects:
    CreateOrderRequest, OrderResponse — just data transfer. Anemic by design.

  External DTOs:
    Data received from external APIs or legacy systems: anemic structs are appropriate.

  Rule: Anemic Domain Model is a problem only when it represents the CORE DOMAIN.
  DTOs, view models, query objects, API contracts: intentionally anemic is fine.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT understanding Anemic Domain Model:

- Build "OOP" systems but apply procedural thinking inside classes
- Business rules duplicated across dozens of service classes
- "Object-Oriented" codebase that behaves like C functions with structs

WITH recognizing Anemic Domain Model:
→ Identify when your domain objects need behavior, not just data
→ Move rules back into the domain objects that own them
→ Reduce service class complexity dramatically

---

### 🧠 Mental Model / Analogy

> A marionette puppet vs. a person. Anemic Domain Model: the Customer class is a marionette — it has arms (fields) and legs (methods), but it can't move on its own. The puppeteer (CustomerService) must pull every string to make it do anything. The puppeteer must know exactly where each string is attached. 100 puppeteers all pulling strings on the same puppet — any puppeteer can put the puppet in an invalid position. Rich Domain Model: a person who can act on their own — "I won't do that; it violates my rules." The service asks; the person decides.

"Marionette (no will of its own)" = Anemic Domain Model
"Puppeteers (know all the strings)" = Service classes with all the logic
"Person who can act and refuse" = Rich Domain Model
"Invalid puppet positions" = invalid object state via setters

---

### ⚙️ How It Works (Mechanism)

```
ANEMIC DOMAIN MODEL FLOW:

  Controller → Service.method(data)
                  │
                  ├─ repo.findById(id) → Entity (data bag)
                  ├─ entity.getX() / entity.getY()  — read internal state
                  ├─ apply business rules in SERVICE
                  ├─ entity.setX(newValue)           — mutate via setters
                  └─ repo.save(entity)

RICH DOMAIN MODEL FLOW:

  Controller → Service.method(data)
                  │
                  ├─ repo.findById(id) → DomainObject (behavior + data)
                  ├─ domainObject.doBusinessOperation(params)
                  │      └─ object applies its own rules and transitions
                  └─ repo.save(domainObject)
```

---

### 🔄 How It Connects (Mini-Map)

```
Object-Oriented Programming (encapsulation principle violated by anemic model)
        │
        ▼
Anemic Domain Model ◄──── (you are here)
(data-only domain objects; all logic in service classes; anti-pattern)
        │
        ├── Domain Model: the rich alternative (behavior in objects)
        ├── Transaction Script: intentionally procedural (different pattern, not OOP anti-pattern)
        ├── Active Record: middle ground (data + some behavior, tied to persistence)
        └── DTOs: legitimately anemic (designed as pure data transfer, not domain models)
```

---

### 💻 Code Example

```java
// ANEMIC (anti-pattern) — spot the problems:
class BankAccount {
    private String accountId;
    private BigDecimal balance;
    private String status; // "ACTIVE", "FROZEN", "CLOSED"

    // Pure data bag — just getters/setters:
    public BigDecimal getBalance() { return balance; }
    public void setBalance(BigDecimal b) { this.balance = b; }  // DANGER: direct mutation
    public String getStatus() { return status; }
    public void setStatus(String s) { this.status = s; }       // No validation
}

class BankAccountService {
    void withdraw(String accountId, BigDecimal amount) {
        BankAccount acc = repo.findById(accountId).orElseThrow();

        // Business rules in SERVICE, not in account:
        if ("FROZEN".equals(acc.getStatus())) throw new AccountFrozenException();
        if ("CLOSED".equals(acc.getStatus())) throw new AccountClosedException();
        if (acc.getBalance().compareTo(amount) < 0) throw new InsufficientFundsException();

        acc.setBalance(acc.getBalance().subtract(amount)); // Direct mutation via setter
        repo.save(acc);
    }
}

// ─────────────────────────────────────────────────────

// RICH DOMAIN MODEL — rules in the object that owns them:
class BankAccount {
    private AccountId id;
    private Money balance;
    private AccountStatus status; // enum

    public void withdraw(Money amount) {  // Rules live here:
        if (status == FROZEN) throw new AccountFrozenException(id);
        if (status == CLOSED) throw new AccountClosedException(id);
        if (balance.isLessThan(amount)) throw new InsufficientFundsException(id, balance, amount);

        this.balance = balance.subtract(amount);
        register(new WithdrawalRecordedEvent(id, amount, balance)); // audit trail
    }
}

class BankAccountService {
    void withdraw(AccountId id, Money amount) {
        BankAccount account = repo.findById(id).orElseThrow();
        account.withdraw(amount); // ONE line; rules in account
        repo.save(account);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Anemic Domain Model is fine because we use services       | The problem isn't that services exist — it's that services contain all domain logic and domain objects are passive. With Rich Domain Model you still have services: they orchestrate. The domain object encapsulates its own rules. Both patterns use services; the difference is WHERE the business rules live                                                                                                                     |
| DTOs and read models are Anemic Domain Models             | No. DTOs are intentionally data-only and that's correct design. The Anemic Domain Model anti-pattern is specifically when the DOMAIN LAYER (core entities, aggregates) are data-only bags. DTOs, view models, API request/response objects, CQRS read models: legitimately anemic by design                                                                                                                                         |
| Anemic Domain Model is actually fine because it's simpler | For simple CRUD: yes, simpler patterns (Transaction Script, Active Record) are appropriate. Anemic Domain Model is the anti-pattern specifically in contexts where you used OOP but stripped it of its benefits. If you're building truly complex domain logic, Anemic Domain Model leads to God Service classes with hundreds of lines of business rules, duplication across services, and inability to express the domain in code |

---

### 🔥 Pitfalls in Production

**God Service class emerges from Anemic Domain Model:**

```java
// BAD: OrderService grown to 800 lines because Order is anemic:
class OrderService {
    // All these methods manipulate Order's internal state via setters:
    public void createOrder(OrderRequest req) { ... }
    public void confirmOrder(Long id) { ... }
    public void cancelOrder(Long id, String reason) { ... }
    public void shipOrder(Long id, TrackingInfo tracking) { ... }
    public void deliverOrder(Long id) { ... }
    public void refundOrder(Long id, RefundReason reason) { ... }
    public void applyDiscount(Long id, DiscountCode code) { ... }
    public void addItem(Long id, ProductId productId, int qty) { ... }
    public void removeItem(Long id, Long itemId) { ... }
    public void recalculateTotal(Long id) { ... }
    public void validateOrder(Long id) { ... }
    // ... 30 more methods, all reading Order getters and calling Order setters.
    // This class has 800 lines and knows everything about everything.
}

// FIX: Each method becomes a domain operation on Order itself.
// OrderService: thin orchestrator. Order: encapsulates own rules.
class Order {
    public void confirm(PaymentResult payment) { /* rules here */ }
    public void cancel(CancellationReason reason) { /* rules here */ }
    public void ship(TrackingInfo tracking) { /* rules here */ }
    public void addItem(Product product, Quantity qty) { /* rules here */ }
    public Money total() { /* calculation here */ }
}
// OrderService: each method is 3-5 lines (load, call, save).
```

---

### 🔗 Related Keywords

- `Domain Model` — the rich alternative: behavior encapsulated in domain objects
- `Transaction Script` — procedural pattern: explicit and intentional, not a disguised OOP anti-pattern
- `Active Record Pattern` — middle-ground: domain object knows its own persistence
- `Value Objects` — naturally rich (behavior-heavy, immutable) domain concepts
- `Object-Oriented Programming` — principle violated by Anemic Domain Model: combine data and behavior

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Domain objects have only data; all logic  │
│              │ in service classes. Anti-pattern: OOP    │
│              │ syntax with procedural thinking.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ (Anti-pattern — avoid for core domain)   │
│              │ DTOs, read models, view objects:          │
│              │ intentionally anemic is OK               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Always avoid for core domain classes.    │
│              │ Signs: 500-line service classes, rules   │
│              │ duplicated across services               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Marionette puppet with 100 puppeteers:  │
│              │  every puppeteer must know every string; │
│              │  the puppet can't refuse."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain Model → Rich Domain Model →       │
│              │ Aggregate Root → Value Objects           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team says: "We have domain objects but they have methods, so we have a Rich Domain Model." You look at their `OrderItem` class and see: `getProductId()`, `getQuantity()`, `getPrice()`, `setQuantity(int q)`, `setPrice(BigDecimal p)`, and two non-trivial methods: `getLineTotal()` (returns `quantity * price`) and `validate()` (returns `true` if quantity > 0 and price > 0). The `OrderService` has `addItemToOrder()`, `removeItemFromOrder()`, and `updateItemQuantity()` — each loading the order, calling setters on items, and saving. Is this a Rich Domain Model or Anemic Domain Model? Justify using the "behavior vs. data" criterion.

**Q2.** You're migrating from an Anemic Domain Model to a Rich Domain Model. The `CustomerService.activateAccount()` method is 40 lines: it validates preconditions, sets status, creates a welcome notification record, updates a loyalty tier, and increments a metrics counter. When moving logic into `Customer.activate()`, you wonder: does ALL of this move into the domain object? Where do notification creation and metrics incrementing belong in the domain model? What's the rule for deciding what goes in the domain object vs. what stays as infrastructure concern?
