---
layout: default
title: "Domain Model"
parent: "Software Architecture Patterns"
nav_order: 736
permalink: /software-architecture/domain-model/
number: "736"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Object-Oriented Programming, Aggregate Root, Value Objects"
used_by: "Domain-Driven Design, Hibernate, JPA, Spring applications"
tags: #advanced, #architecture, #ddd, #domain, #oop
---

# 736 — Domain Model

`#advanced` `#architecture` `#ddd` `#domain` `#oop`

⚡ TL;DR — A **Domain Model** is an object-oriented representation of the business domain — entities, value objects, services, and relationships that capture domain logic directly in code, replacing procedural scripts with behavior-rich objects.

| #736            | Category: Software Architecture Patterns                   | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Aggregate Root, Value Objects |                 |
| **Used by:**    | Domain-Driven Design, Hibernate, JPA, Spring applications  |                 |

---

### 📘 Textbook Definition

The **Domain Model** pattern (Martin Fowler, "Patterns of Enterprise Application Architecture") creates an object model of the domain that incorporates both behavior and data. Unlike Transaction Script (which puts logic in procedures) or Active Record (which attaches behavior to database rows), the Domain Model creates a rich network of objects where each object knows its rules and responsibilities. A well-designed Domain Model: (1) **Speaks the Ubiquitous Language** — code uses the same terms as domain experts (Order, Customer, Invoice — not "record," "row," "data"). (2) **Encapsulates business rules** — an `Order` knows it can only be cancelled before shipping; the rule lives in `Order.cancel()`, not in an `OrderService`. (3) **Has behavior** — objects do things; they're not just data containers. (4) **Uses Value Objects** — immutable, equality-by-value objects for concepts like Money, Email, Address. In DDD: the Domain Model is the aggregate roots, entities, value objects, domain services, and domain events that collectively express the business domain in code. The opposite: **Anemic Domain Model** — objects have data but no behavior (anti-pattern per Fowler).

---

### 🟢 Simple Definition (Easy)

A chess game: the Domain Model is the chess pieces and rules in code. A `Bishop` knows it can only move diagonally. A `King` knows it can't move into check. The board enforces "you can't have two pieces on the same square." Rules live in the pieces, not in a separate "chess rules service" that knows everything about every piece. The model mirrors how a chess expert thinks about the game. Add a new rule for a variant chess: change the piece's behavior, not a central rules engine.

---

### 🔵 Simple Definition (Elaborated)

Two approaches to an e-commerce checkout: (1) Transaction Script: `CheckoutService.processCheckout()` — one big procedure that reads from the DB, applies 200 lines of if/else business rules, writes back. Test: mock the entire database. Change: touch this giant method. (2) Domain Model: `Cart.checkout()` — the cart knows if it can be checked out. `InventoryItem.reserve()` — the item knows how to reserve itself. `CreditCard.charge()` — the card knows how to charge. Each object has its own rules. Test each in isolation. Add a new rule to `CartItem`: only the CartItem class changes. The Domain Model: your code tells a story the business understands.

---

### 🔩 First Principles Explanation

**Ubiquitous language, encapsulated behavior, value objects, and domain services:**

```
DOMAIN MODEL CHARACTERISTICS:

  1. UBIQUITOUS LANGUAGE:

     BAD (technical naming, no domain meaning):
       UserDataRecord, UserDataProcessor, UserDataManager.
       "process()" — what does it process?

     GOOD (domain language):
       Customer, Order, Invoice.
       "customer.placeOrder()" — self-documenting.
       "invoice.markAsPaid(payment)" — business language.

  2. BEHAVIOR IN OBJECTS:

     ANEMIC (data only, behavior elsewhere):
       class Order {
           Long id;
           String status;         // Just data.
           BigDecimal total;
           List<OrderItem> items;
           // No methods. No rules. Just getters/setters.
       }
       // Business rules: in OrderService (100+ method procedure).

     RICH DOMAIN MODEL (behavior in object):
       class Order {
           private OrderId id;
           private OrderStatus status;
           private List<OrderItem> items;

           public void confirm(PaymentResult payment) {
               if (status != OrderStatus.PENDING) throw new InvalidStateException();
               if (!payment.isSuccessful()) throw new PaymentFailedException();
               this.status = OrderStatus.CONFIRMED;
               this.confirmedAt = Instant.now();
               register(new OrderConfirmedEvent(id, total()));
           }

           public void cancel(CancellationReason reason) {
               if (status == OrderStatus.SHIPPED) throw new OrderAlreadyShippedException();
               this.status = OrderStatus.CANCELLED;
               this.cancellationReason = reason;
               register(new OrderCancelledEvent(id, reason));
           }

           public Money total() {
               return items.stream().map(OrderItem::lineTotal)
                           .reduce(Money.ZERO, Money::add);
           }
       }
       // Business rules LIVE in the domain object. Service: just orchestrates.

  3. VALUE OBJECTS:

     Primitive Obsession (BAD):
       String email = "user@example.com";  // Just a String. No validation. No behavior.
       BigDecimal price = new BigDecimal("19.99");  // No currency. Can add USD + EUR.

     Value Objects (GOOD):
       Email email = Email.of("user@example.com");  // Validates format. Immutable.
       Money price = Money.of(new BigDecimal("19.99"), Currency.USD);  // Currency-aware.

       // Money with domain behavior:
       Money total = price.add(tax);  // Type-safe. Can't add USD to EUR.
       Money discounted = price.applyDiscount(Percentage.of(10));  // Domain operation.

  4. DOMAIN SERVICES (for operations that don't belong to a single object):

     When an operation involves multiple aggregates: use a Domain Service.

     // TransferService: spans two Account aggregates.
     public class MoneyTransferService {
         public void transfer(Account source, Account target, Money amount) {
             source.debit(amount);  // Account knows how to debit itself.
             target.credit(amount); // Account knows how to credit itself.
             // Transfer logic: orchestrates two accounts. Lives in domain service.
         }
     }

     RULE: Domain Service is in the domain layer. Uses domain objects. No infrastructure.
     NOT a service that wraps a repository (that's Application Service).

  5. DOMAIN EVENTS:

     Significant state changes: announce via domain events.

     // Order publishes event when confirmed:
     order.confirm(payment);
     // Internally: order.register(new OrderConfirmedEvent(id, customerId, total()));

     // Event handlers react (in separate contexts):
     OrderConfirmedEvent → EmailNotificationHandler → sends confirmation email
     OrderConfirmedEvent → LoyaltyPointsHandler → adds loyalty points
     OrderConfirmedEvent → AnalyticsHandler → records sale event

     Order: doesn't know about email, loyalty, or analytics. Decoupled via events.

DOMAIN MODEL vs TRANSACTION SCRIPT COMPARISON:

  Transaction Script (checkoutService.checkout(cartId)):
    1. Load cart from DB.
    2. Validate cart not empty.
    3. Calculate totals.
    4. Check inventory.
    5. Reserve inventory.
    6. Charge payment.
    7. Create order.
    8. Send confirmation.
    → 200-line procedure. All steps in one service method.

  Domain Model (cart.checkout(payment)):
    cart.checkout(payment):
      cart.validate()         → Cart knows if it's valid.
      items.forEach(i → i.reserve()) → Each item knows how to reserve.
      payment.charge(total()) → Payment knows how to charge.
      return Order.create(this) → Order knows how to create itself.

    → Each object responsible for its part. Coordinator just calls.

DOMAIN MODEL COMPLEXITY THRESHOLD:

  Simple CRUD: Domain Model overkill. Use Active Record or Transaction Script.

  Signs you need Domain Model:
    - Business rules are complex and spread across many services.
    - Rules interact: "10% discount if order > $100 AND customer is premium AND not a sale item."
    - Multiple concepts must stay consistent together (aggregates).
    - Domain experts and developers have communication gaps (Ubiquitous Language needed).
    - Business rules change frequently.

  Amazon, financial systems, healthcare: Domain Model appropriate.
  Blog post CRUD API: Domain Model is over-engineering.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Domain Model:

- Business rules scattered across Service classes, controllers, SQL stored procedures
- Rules duplicated: validation in API layer, service layer, database triggers — three versions of the same rule
- Domain expert and developer speak different languages: "process an order" vs. `UserDataProcessor.executeUserDataProcessingRoutine()`

WITH Domain Model:
→ Business rules in one place: the domain object that owns them
→ Ubiquitous Language: code reads like the business domain
→ Each object independently testable with its own rules

---

### 🧠 Mental Model / Analogy

> A hospital vs. a factory assembly line. Factory (Transaction Script): one assembly line (service method) does everything — each step hands off to the next. Hospital (Domain Model): each specialist knows their domain — cardiologist handles heart concerns, neurologist handles brain concerns, surgeon knows surgical rules. A patient (domain object) has their own medical history and knows their conditions. Doctors (domain services) coordinate specialists. Each specialist's knowledge encapsulated in their specialty, not all in one "HospitalAdministratorService."

"Specialists knowing their domain" = domain objects with encapsulated behavior
"Patient knowing their own medical history" = aggregate holding its own state
"Doctors coordinating specialists" = domain service orchestrating aggregates
"Factory assembly line" = Transaction Script (one big procedure)

---

### ⚙️ How It Works (Mechanism)

```
DOMAIN MODEL CALL FLOW:

  Application Service (thin orchestrator):
    Cart cart = cartRepo.findById(cartId);
    PaymentResult result = paymentGateway.charge(card, cart.total());
    Order order = cart.checkout(result);  // Domain model: Cart creates Order.
    orderRepo.save(order);               // Persist result.
    eventBus.publishAll(order.events()); // Publish domain events.

  Domain objects do the work:
    cart.checkout(result) → validates state, creates Order, registers event.
    Order.create(cart) → applies creation rules, initializes state.
    cart.total() → computes from items (business computation in model).
```

---

### 🔄 How It Connects (Mini-Map)

```
Object-Oriented Programming (encapsulation and behavior in objects)
        │
        ▼ (applied to business domain)
Domain Model ◄──── (you are here)
(entities, value objects, domain services, events — expressing domain in code)
        │
        ├── Aggregate Root: organizes domain model into consistency units
        ├── Value Objects: immutable objects for domain concepts (Money, Email)
        ├── Anemic Domain Model: the anti-pattern (data without behavior)
        └── Transaction Script: the simpler alternative for low-complexity domains
```

---

### 💻 Code Example

```java
// Rich Domain Model for a loan application:
public final class LoanApplication {
    private final ApplicationId id;
    private final CustomerId applicantId;
    private final Money requestedAmount;
    private ApplicationStatus status;
    private CreditScore creditScore;

    // Factory: domain-level creation with initial validation:
    public static LoanApplication submit(CustomerId applicantId, Money amount) {
        if (amount.isLessThan(Money.of(1000, USD)))
            throw new MinimumLoanAmountException("Minimum loan: $1,000");
        if (amount.isGreaterThan(Money.of(50000, USD)))
            throw new MaximumLoanAmountException("Maximum loan: $50,000");
        return new LoanApplication(ApplicationId.generate(), applicantId, amount);
    }

    // Domain operation with business rule:
    public void approve(CreditScore score, UnderwriterDecision decision) {
        if (status != PENDING_REVIEW)
            throw new InvalidStateException("Can only approve PENDING_REVIEW applications");
        if (score.value() < 650)
            throw new InsufficientCreditScoreException("Minimum credit score: 650");
        this.creditScore = score;
        this.status = APPROVED;
        // Domain event: notify interested contexts.
        register(new LoanApprovedEvent(id, applicantId, requestedAmount, score));
    }

    // Derived domain calculation:
    public Money monthlyPayment(InterestRate rate, int termMonths) {
        // Business formula lives here — not in a "LoanCalculatorService":
        double r = rate.monthly();
        double n = termMonths;
        double p = requestedAmount.amount().doubleValue();
        double payment = p * (r * Math.pow(1+r, n)) / (Math.pow(1+r, n) - 1);
        return Money.of(BigDecimal.valueOf(payment).setScale(2, HALF_UP), USD);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain Model is the same as the database schema | Domain Model reflects the business domain, not the storage structure. A domain `Money` value object maps to two columns (amount, currency). A domain `Address` maps to 5 columns. A domain `OrderItem` may span two tables. The mapping between domain model and database schema is the ORM's job. Designing domain model to match DB schema: Anemic Domain Model anti-pattern                                                                      |
| Domain Model requires DDD                       | Domain Model predates DDD (Fowler described it in 2002; Evans published DDD in 2003). DDD provides the methodology (Ubiquitous Language, Bounded Contexts, Aggregates) to build effective Domain Models. You can use Domain Model without full DDD. But DDD gives you the tools to build the right domain model for complex domains                                                                                                                 |
| Every application needs a Domain Model          | For simple CRUD applications: Transaction Script or Active Record may be more appropriate. Martin Fowler: "Domain Model suits complex business logic." Complexity threshold: if your service methods are mostly "load, validate a simple rule, save" — Transaction Script is sufficient and simpler. Domain Model: worthwhile when you have truly complex business rules, invariants across multiple objects, or frequently changing business logic |

---

### 🔥 Pitfalls in Production

**Anemic Domain Model masquerading as a Rich Domain Model:**

```
LOOKS LIKE Domain Model (has Order class with methods):

  class Order {
      private Long id;
      private String status;

      public void setStatus(String status) { this.status = status; }  // Just a setter.
      public String getStatus() { return this.status; }
      public void confirm() { this.status = "CONFIRMED"; }  // No rules. Just sets value.
  }

  class OrderService {
      public void confirmOrder(Long orderId) {
          Order order = orderRepo.findById(orderId);

          // Business rules: in the SERVICE, not in Order:
          if (!"PENDING".equals(order.getStatus())) {
              throw new InvalidStateException("Can only confirm PENDING orders");
          }
          if (order.getItems().isEmpty()) {
              throw new EmptyOrderException("Cannot confirm empty order");
          }
          PaymentResult result = paymentService.charge(order.getCustomerId(), order.getTotal());
          if (!result.isSuccessful()) {
              throw new PaymentFailedException();
          }

          order.confirm();  // Order.confirm(): just sets status. No logic.
          orderRepo.save(order);
      }
  }

  PROBLEM: Order has methods but no behavior. All rules in OrderService.
  This IS the Anemic Domain Model: objects are data containers with getter/setter methods.
  The "confirm()" method is just a setter with a name.

BAD: Order.confirm() has no domain knowledge:
  public void confirm() { this.status = "CONFIRMED"; }  // No validation. Just mutation.

FIX: Move rules INTO the Order object:
  public void confirm(PaymentResult payment) {
      // Domain rules LIVE here:
      if (status != OrderStatus.PENDING)
          throw new InvalidStateException("Can only confirm PENDING orders");
      if (items.isEmpty())
          throw new EmptyOrderException("Cannot confirm empty order");
      if (!payment.isSuccessful())
          throw new PaymentFailedException("Payment failed: " + payment.errorCode());

      // State transition:
      this.status = OrderStatus.CONFIRMED;
      this.confirmedAt = Instant.now();
      this.paymentReference = payment.reference();

      // Domain event:
      register(new OrderConfirmedEvent(id, customerId, total(), confirmedAt));
  }

  // OrderService now just coordinates — no business rules:
  public void confirmOrder(Long orderId) {
      Order order = orderRepo.findById(orderId);
      PaymentResult payment = paymentGateway.charge(order.customerId(), order.total());
      order.confirm(payment);  // Domain object does the work.
      orderRepo.save(order);
  }
  // OrderService: 5 lines. Order: has all rules. Testable without service.
```

---

### 🔗 Related Keywords

- `Anemic Domain Model` — the anti-pattern: domain objects as data bags with no behavior
- `Aggregate Root` — how domain objects are organized into consistency units
- `Value Objects` — immutable, equality-by-value domain concepts (Money, Email, Address)
- `Transaction Script` — the simpler alternative for low-complexity domains
- `Ubiquitous Language` — shared vocabulary between developers and domain experts

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Objects reflect business domain: behavior│
│              │ + data + rules encapsulated in the       │
│              │ objects that own them. Code speaks the   │
│              │ business language.                       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex domain; rules span multiple      │
│              │ concepts; rules change frequently;       │
│              │ DDD project; domain experts collaborate  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; few business rules;         │
│              │ small team; time pressure (Transaction   │
│              │ Script is simpler and faster to build)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Chess pieces know their own moves;     │
│              │  rules live in the pieces, not in       │
│              │  a central 'chess rules service'."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Aggregate Root → Value Objects →        │
│              │ Anemic Domain Model → Transaction        │
│              │ Script → DDD (Domain-Driven Design)      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a `Discount` rule: "Premium customers get 15% off orders over $200. Sale items don't qualify for discounts. Discount is capped at $50 maximum." Which object owns this rule: `Order`, `Customer`, `OrderItem`, or a `DiscountService`? Design the method signature(s) and explain how the objects collaborate to enforce this multi-object rule without creating coupling or moving it to a service.

**Q2.** A `BankAccount` domain object has a `withdraw(Money amount)` method. Concurrent requests: two simultaneous withdrawals of $800 from an account with $1,000. Both load the account (balance $1,000), both check: $1,000 ≥ $800 (pass), both deduct $800. Final balance: -$600. The domain model's invariant ("balance cannot go negative") was enforced by each instance's `withdraw()`, but the invariant was still violated. How does this concurrency problem relate to the aggregate root pattern? What mechanism prevents this race condition?
