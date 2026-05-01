---
layout: default
title: "Service Layer"
parent: "Software Architecture Patterns"
nav_order: 738
permalink: /software-architecture/service-layer/
number: "738"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Domain Model, Repository Pattern, Transaction Script"
used_by: "Spring Service, Application Services, REST APIs, CQRS"
tags: #intermediate, #architecture, #layers, #spring, #ddd
---

# 738 — Service Layer

`#intermediate` `#architecture` `#layers` `#spring` `#ddd`

⚡ TL;DR — The **Service Layer** defines an application's boundary and its set of available operations, coordinating the domain model to execute business use cases — it's the entry point to the domain, not the home of business logic.

| #738            | Category: Software Architecture Patterns              | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Domain Model, Repository Pattern, Transaction Script  |                 |
| **Used by:**    | Spring Service, Application Services, REST APIs, CQRS |                 |

---

### 📘 Textbook Definition

The **Service Layer** pattern (Martin Fowler, "Patterns of Enterprise Application Architecture") defines an application's boundary with a layer of services that establishes a set of available operations and coordinates the application's response in each operation. A Service Layer: (1) **Defines use cases**: each service method corresponds to one use-case (e.g., `placeOrder()`, `cancelOrder()`, `upgradeCustomer()`). (2) **Coordinates domain objects**: calls domain model methods, repositories, and domain services to fulfill the use case. (3) **Manages transactions**: demarcates transaction boundaries at the service method level. (4) **Does NOT contain business logic**: business rules belong in domain objects. The Service Layer is a thin orchestrator. In DDD terminology, the Service Layer corresponds to the **Application Layer**: application-specific orchestration (load aggregate, execute domain operation, save, publish events). The difference from Domain Service: Application Service orchestrates; Domain Service is part of the domain (contains domain logic, speaks domain language).

---

### 🟢 Simple Definition (Easy)

A restaurant analogy: the service layer is the waiter. The waiter doesn't cook (domain logic stays in the kitchen), doesn't store food (repository does that), doesn't own the table (the controller handles HTTP). The waiter coordinates: takes your order (receives the request), goes to the kitchen (calls domain model), picks up the food (gets the result), brings it to the table (returns the response), and handles the payment (manages the transaction). One waiter per use case. The kitchen (domain model) does the actual cooking.

---

### 🔵 Simple Definition (Elaborated)

In a Spring Boot application, `@Service` classes are the Service Layer. `OrderService.placeOrder()`: (1) Loads the `Customer` and `Cart` from repositories. (2) Calls `cart.checkout(payment)` — domain logic in the domain model. (3) Saves the resulting `Order` via `OrderRepository`. (4) Publishes `OrderPlacedEvent` via `EventBus`. (5) `@Transactional` annotation: the whole method is one database transaction. The Service Layer doesn't know how cart checkout works — that's `Cart`'s job. It just coordinates: get things, call the operation, save, publish. One service method = one use case. Simple and testable.

---

### 🔩 First Principles Explanation

**Application Service vs. Domain Service vs. Infrastructure Service:**

```
WHAT BELONGS WHERE:

  APPLICATION SERVICE (Service Layer):
    - Orchestrates a USE CASE.
    - Loads domain objects from repositories.
    - Calls domain object methods (business logic in domain objects).
    - Saves changes via repositories.
    - Publishes domain events to event bus.
    - Manages transaction boundaries.
    - Converts DTOs ↔ domain objects.

    EXAMPLE:
      @Service @Transactional
      class PlaceOrderService {

          OrderId placeOrder(PlaceOrderCommand cmd) {
              // 1. Load domain objects:
              Customer customer = customerRepo.findById(cmd.customerId())
                                             .orElseThrow(CustomerNotFoundException::new);
              Cart cart = cartRepo.findById(cmd.cartId())
                                  .orElseThrow(CartNotFoundException::new);

              // 2. Execute domain operation (logic in domain model):
              Order order = cart.checkout(customer, cmd.paymentMethod());

              // 3. Persist result:
              orderRepo.save(order);

              // 4. Publish domain events:
              eventBus.publishAll(order.domainEvents());

              // 5. Return result to caller (as primitive, not domain object):
              return order.id();
          }
      }

    NOTICE:
      - No business rules in this class.
      - "Can the cart be checked out?" → Cart knows.
      - "What makes a valid order?" → Order knows.
      - This service: just coordinates and handles infrastructure concerns.

  DOMAIN SERVICE:
    - Contains domain logic that doesn't belong to one entity.
    - Part of the domain layer (inside the domain, not outside it).
    - Speaks the domain language.
    - Has no infrastructure dependencies (no repos, no email, no HTTP).

    EXAMPLE:
      class ShippingCostCalculator {  // Domain Service
          Money calculate(Address from, Address to, Weight weight) {
              // Domain logic: shipping cost formula.
              // Pure function. No side effects. No infrastructure.
          }
      }

      class PricingService {  // Domain Service
          Money applyDiscounts(Order order, Customer customer, List<Coupon> coupons) {
              // Domain logic: pricing rules span Order + Customer + Coupons.
              // This logic doesn't belong to any single entity.
          }
      }

  INFRASTRUCTURE SERVICE:
    - Adapter to infrastructure (email, SMS, S3, external APIs).
    - Implements domain interface (EmailPort) with infrastructure (SendGridEmailAdapter).
    - Service Layer depends on interface; infrastructure implements it.

    EXAMPLE:
      interface NotificationPort { void send(Notification n); }      // Domain interface
      class SendGridNotificationAdapter implements NotificationPort { // Infrastructure
          // Calls SendGrid API. Infrastructure detail.
      }

SERVICE LAYER THICKNESS:

  THIN Service Layer (with Rich Domain Model):

    @Transactional
    void cancelOrder(OrderId orderId, CancellationReason reason) {
        Order order = orderRepo.findById(orderId).orElseThrow();
        order.cancel(reason);      // Domain object does the work.
        orderRepo.save(order);     // Save.
        // Domain events published by event listener on save.
    }
    // 4 lines. Zero business logic. All in domain model.

  FAT Service Layer (with Anemic Domain Model):

    @Transactional
    void cancelOrder(Long orderId, String reason) {
        Order order = orderRepo.findById(orderId).orElseThrow();

        // Business rules here because Order is anemic:
        if (!"CONFIRMED".equals(order.getStatus()) && !"PENDING".equals(order.getStatus())) {
            throw new InvalidStateException("Can only cancel CONFIRMED or PENDING orders");
        }
        if (order.getShipments().stream().anyMatch(s -> s.getStatus().equals("SHIPPED"))) {
            throw new AlreadyShippedException("Order has shipped items");
        }
        if (order.getCreatedAt().isBefore(LocalDateTime.now().minusDays(30))) {
            throw new CancellationWindowExpiredException("30-day cancellation window expired");
        }

        // Direct mutations via setters:
        order.setStatus("CANCELLED");
        order.setCancelledAt(LocalDateTime.now());
        order.setCancellationReason(reason);

        // Calculate refund:
        BigDecimal refund = order.getItems().stream()
            .filter(i -> !"SHIPPED".equals(i.getStatus()))
            .map(i -> i.getPrice().multiply(BigDecimal.valueOf(i.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        // Create refund record:
        Refund r = new Refund();
        r.setOrderId(orderId);
        r.setAmount(refund);
        r.setReason(reason);
        r.setCreatedAt(LocalDateTime.now());
        refundRepo.save(r);

        orderRepo.save(order);

        // Send notifications:
        emailService.sendCancellationEmail(order.getCustomerId(), orderId, reason);
    }
    // 40+ lines. Full of business rules. Service Layer is too fat.

  RULE: Service Layer thickness is inversely proportional to the richness of the Domain Model.

TRANSACTION MANAGEMENT:

  Service Layer owns transaction boundaries.

  @Transactional                         // Transaction starts here.
  void transferFunds(AccountId from, AccountId to, Money amount) {
      Account source = accountRepo.findById(from).orElseThrow();
      Account target = accountRepo.findById(to).orElseThrow();

      source.debit(amount);              // Domain operation.
      target.credit(amount);             // Domain operation.

      accountRepo.save(source);          // Both saves: same transaction.
      accountRepo.save(target);
                                         // Transaction commits or rolls back both.
  }

  @Transactional(readOnly = true)       // Read-only transaction for queries.
  CustomerProfile getProfile(CustomerId id) { ... }

  IMPORTANT: @Transactional on Repository layer (not Service layer): anti-pattern.
  Fine-grained transactions: lose the ability to make multiple operations atomic.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Service Layer:

- Controller classes contain business logic and transaction management
- Business logic duplicated when same use case is called from REST API, message queue, batch job
- Transaction boundaries unclear: partial updates possible

WITH Service Layer:
→ Single entry point per use case: REST, queue, batch all call the same service method
→ Transaction boundary clear: `@Transactional` on service method
→ Controller stays thin: just HTTP concerns; service handles domain orchestration

---

### 🧠 Mental Model / Analogy

> An airport operations center vs. a flight simulator. Service Layer is the operations center: it coordinates — assigns gates, notifies passengers, tracks arrivals and departures, coordinates ground crew. It doesn't fly the plane (that's the pilot/domain model), doesn't store passenger data (that's the database/repository), doesn't make the runway (that's infrastructure). It's the thin coordination layer between the outside world (flight requests) and all the specialized parts. One operations coordinator per incoming flight (one service method per use case).

"Operations coordinator" = Service Layer method
"Doesn't fly the plane" = doesn't contain domain logic
"Assigns gates, notifies, tracks" = orchestrates repositories and domain events
"One per incoming flight" = one method per use case

---

### ⚙️ How It Works (Mechanism)

```
REQUEST FLOW THROUGH SERVICE LAYER:

  HTTP Request
      │
      ▼
  Controller (HTTP concerns only: parse request, return response)
      │
      ▼ (calls with domain command/DTO)
  Service Layer (@Transactional — orchestrates use case)
      │
      ├─ Load via Repository (find by ID, query)
      ├─ Call Domain Object method (business logic happens in domain)
      ├─ Save via Repository
      └─ Publish Domain Events
      │
      ▼ (returns result DTO or ID, never domain object to controller)
  Controller (converts to HTTP response)
      │
      ▼
  HTTP Response
```

---

### 🔄 How It Connects (Mini-Map)

```
Controller / REST API (HTTP request)
        │
        ▼ (delegates to)
Service Layer ◄──── (you are here)
(orchestrates use case: load, call domain, save, publish)
        │
        ├── Repository Pattern: loads and saves domain objects
        ├── Domain Model: where business logic actually lives
        ├── Domain Events: published after use-case completion
        └── Transaction Script: alternative when domain model is not used
```

---

### 💻 Code Example

```java
// Command object (input DTO):
record RegisterCustomerCommand(String email, String name, String passwordHash) {}

// Application Service (Service Layer) — thin orchestrator:
@Service
@Transactional
public class CustomerRegistrationService {

    private final CustomerRepository customerRepo;
    private final NotificationPort notificationPort; // Infrastructure interface

    // Use-case method: one command → one operation:
    public CustomerId register(RegisterCustomerCommand cmd) {
        // 1. Validate uniqueness (query — not domain logic):
        if (customerRepo.existsByEmail(cmd.email())) {
            throw new DuplicateEmailException(cmd.email());
        }

        // 2. Create domain object (factory method holds creation rules):
        Customer customer = Customer.register(
            Email.of(cmd.email()),
            Name.of(cmd.name()),
            HashedPassword.of(cmd.passwordHash())
        );

        // 3. Persist:
        customerRepo.save(customer);

        // 4. Publish domain events (notification, analytics, etc.):
        customer.domainEvents().forEach(event -> {
            if (event instanceof CustomerRegisteredEvent e) {
                notificationPort.sendWelcomeEmail(e.email(), e.name());
            }
        });

        // 5. Return primitive ID (never return domain object from service):
        return customer.id();
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Service Layer is where business logic lives          | No. Service Layer is where orchestration lives. Business logic belongs in domain objects (Domain Model) or domain services. If your service methods are more than 10-15 lines with business rules, the domain model is probably anemic                                                                                                                                                                                   |
| Every operation needs a Service Layer method         | Not necessarily. Simple read operations (get customer by ID) may go directly from controller to repository. The Service Layer is most valuable for write operations with domain logic, transactions, and event publishing. Adding a service method for every simple query creates unnecessary boilerplate                                                                                                                |
| Domain Service = Application Service (Service Layer) | Different. Application Service (Service Layer): in the application layer; orchestrates use cases; depends on repositories, event bus, external services. Domain Service: in the domain layer; contains domain logic that doesn't belong to one entity; no infrastructure dependencies; speaks domain language. Fowler: "Domain Model contains both domain objects and domain services. Application Service coordinates." |

---

### 🔥 Pitfalls in Production

**Service Layer becomes the domain — violates its own purpose:**

```java
// BAD: Service Layer doing domain work (not just orchestrating):
@Transactional
void applyPromotion(Long orderId, String promoCode) {
    Order order = orderRepo.findById(orderId).orElseThrow();
    Promotion promo = promoRepo.findByCode(promoCode).orElseThrow();

    // Business logic in service layer (should be in domain objects):
    if (order.getTotal().compareTo(promo.getMinimumOrderAmount()) < 0) {
        throw new PromotionMinimumNotMetException();
    }
    if (!promo.getApplicableCategories().isEmpty()) {
        boolean anyItemQualifies = order.getItems().stream()
            .anyMatch(i -> promo.getApplicableCategories().contains(i.getCategory()));
        if (!anyItemQualifies) throw new PromotionNotApplicableException();
    }
    if (order.getAppliedPromotions().contains(promoCode)) {
        throw new PromotionAlreadyAppliedException();
    }

    BigDecimal discount = order.getTotal().multiply(promo.getDiscountPercentage());
    order.setDiscountAmount(order.getDiscountAmount().add(discount));
    order.getAppliedPromotions().add(promoCode);
    orderRepo.save(order);
}
// SERVICE is a god class with domain knowledge. TEST: requires full Spring context.

// FIX: Move rules to domain objects:
@Transactional
void applyPromotion(Long orderId, String promoCode) {
    Order order = orderRepo.findById(orderId).orElseThrow();
    Promotion promo = promoRepo.findByCode(promoCode).orElseThrow();
    order.applyPromotion(promo);   // Domain object applies its own rules.
    orderRepo.save(order);
}
// SERVICE: 4 lines. Order.applyPromotion(): all rules, fully unit-testable.
```

---

### 🔗 Related Keywords

- `Domain Model` — where business logic lives; Service Layer orchestrates domain objects
- `Repository Pattern` — Service Layer uses repos to load and save domain objects
- `Transaction Script` — alternative: put procedural logic in service (less OOP, simpler for CRUD)
- `CQRS Pattern` — Command handlers are application services; query side bypasses domain model
- `Domain Events` — published from Service Layer after domain operations complete

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Thin orchestrator at domain boundary:    │
│              │ load, call domain, save, publish events. │
│              │ No business logic here.                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple entry points to same use case;  │
│              │ need transaction boundaries; coordinating│
│              │ multiple domain objects or repositories  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD with no domain logic (go     │
│              │ directly to repo); avoid putting domain  │
│              │ rules here (belongs in domain model)     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The waiter doesn't cook; the waiter     │
│              │  coordinates kitchen, tables, and        │
│              │  payment into one seamless use case."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain Model → Repository Pattern →      │
│              │ Transaction Script → CQRS → DDD          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In a layered architecture: Controller → Service → Repository. A developer adds `@Transactional` to the `save()` method in `OrderRepository`. Another developer adds `@Transactional` on `OrderService.placeOrder()` which calls `orderRepo.save()`, `inventoryRepo.save()`, and `eventBus.publish()`. What happens with Spring's default `REQUIRED` propagation? Is the repository-level `@Transactional` redundant, harmful, or necessary in this setup? What if `placeOrder()` were NOT `@Transactional`?

**Q2.** A microservices architect argues: "In a microservice, the Service Layer should call external service APIs directly — `inventoryServiceClient.reserve(itemId, qty)` and `paymentServiceClient.charge(cardId, amount)` inside the order service's `PlaceOrderService.placeOrder()`. This is just orchestration, so it belongs in the Service Layer." Is this appropriate? What problem arises when the payment call fails after inventory was reserved? What pattern addresses this, and how does it change the responsibilities of the Service Layer?
