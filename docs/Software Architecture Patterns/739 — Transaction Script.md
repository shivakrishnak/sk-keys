---
layout: default
title: "Transaction Script"
parent: "Software Architecture Patterns"
nav_order: 739
permalink: /software-architecture/transaction-script/
number: "739"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Service Layer, Repository Pattern"
used_by: "CRUD applications, simple business logic, stored procedures"
tags: #intermediate, #architecture, #patterns, #procedural
---

# 739 — Transaction Script

`#intermediate` `#architecture` `#patterns` `#procedural`

⚡ TL;DR — A **Transaction Script** organizes business logic as a single procedure per use case — all steps (validation, domain logic, persistence) in one sequential script, matching the simplicity of CRUD applications where a Rich Domain Model would be over-engineering.

| #739            | Category: Software Architecture Patterns                    | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Service Layer, Repository Pattern                           |                 |
| **Used by:**    | CRUD applications, simple business logic, stored procedures |                 |

---

### 📘 Textbook Definition

The **Transaction Script** pattern (Martin Fowler, "Patterns of Enterprise Application Architecture") organizes all business logic as procedures: one procedure per system transaction (user action or batch process). Each Transaction Script is a self-contained procedure that validates inputs, applies business rules, accesses the database, and returns a result. It maps directly to one "transaction" in the user's mental model: "register customer," "place order," "cancel subscription." Transaction Script: (1) **Explicit and readable**: every step visible in one method. (2) **No indirection**: no object graph to traverse; no method dispatch. (3) **Works well for simple logic**: when each transaction has few, self-contained rules. (4) **Becomes unwieldy for complex logic**: when rules multiply and interact across transactions. Transaction Script is NOT an anti-pattern: it's a valid, explicit choice for simple domains. It becomes a problem only when forced into complex domains where Domain Model would be more maintainable.

---

### 🟢 Simple Definition (Easy)

A recipe card vs. a cookbook with cooking techniques. Transaction Script: a recipe card for every dish ("How to make spaghetti bolognese": step 1, step 2, step 3...). Simple, self-contained, works great. Domain Model: a cookbook that teaches techniques that combine to make any dish. Better when you have 500 dishes with shared techniques. For 5 dishes: the recipe card is simpler and faster. Transaction Script is the recipe card — perfect for simple use cases, awkward when you have 100 interacting rules.

---

### 🔵 Simple Definition (Elaborated)

A Spring service method that: (1) validates the input DTO, (2) queries the database to check preconditions, (3) computes a result, (4) saves to the database, (5) returns a response. No separate domain model objects with behavior. No aggregate roots. The service method IS the business logic. For a "register user" use case with two rules (email unique, password strong enough): Transaction Script is 20 lines, clear, testable. Domain Model: 3+ classes (User, Email VO, Password VO), overkill for 2 rules. Transaction Script wins here.

---

### 🔩 First Principles Explanation

**When to use Transaction Script, when to switch to Domain Model:**

```
TRANSACTION SCRIPT STRUCTURE:

  One method = one use case:

    class UserRegistrationScript {
        UserResponse register(RegisterRequest request) {
            // 1. VALIDATE INPUT:
            if (request.email() == null || !request.email().contains("@")) {
                throw new ValidationException("Invalid email");
            }
            if (request.password().length() < 8) {
                throw new ValidationException("Password too short");
            }

            // 2. CHECK BUSINESS PRECONDITIONS (query):
            if (userRepo.existsByEmail(request.email())) {
                throw new DuplicateEmailException("Email already registered");
            }

            // 3. APPLY BUSINESS LOGIC (compute):
            String hashedPassword = passwordHasher.hash(request.password());
            LocalDateTime now = LocalDateTime.now();

            // 4. PERSIST:
            User user = new User();         // User is just a data holder (DTO-like)
            user.setEmail(request.email());
            user.setPasswordHash(hashedPassword);
            user.setStatus("PENDING_VERIFICATION");
            user.setCreatedAt(now);
            User saved = userRepo.save(user);

            // 5. SIDE EFFECTS (email, etc.):
            emailService.sendVerificationEmail(request.email(), saved.getId());

            // 6. RETURN:
            return new UserResponse(saved.getId(), saved.getEmail());
        }
    }

  Every step visible. No object graph. No method dispatch. Readable as prose.

TRANSACTION SCRIPT vs DOMAIN MODEL — Decision Framework:

  Transaction Script is appropriate when:
    - ≤ 3 business rules per transaction.
    - Rules are independent (don't share logic between transactions).
    - Simple validation + DB operation pattern.
    - Prototyping or tight deadlines.
    - Simple CRUD (content management, configuration, catalog administration).
    - No complex invariants spanning multiple objects.

  Domain Model is appropriate when:
    - Business rules are complex (many conditions, interactions between concepts).
    - Rules are shared across multiple transactions.
    - Need to maintain invariants across multiple related objects.
    - Domain experts need to be involved in code review.
    - Rules change frequently and must be tested independently.

  CONTINUUM — the real world:

  Pure CRUD          Transaction Script          Domain Model
  (no rules)         (a few rules, explicit)     (complex, encapsulated)
      │                       │                         │
  blog posts          user registration          banking system
  file management     order placement             insurance rules
  address book        appointment booking         healthcare workflows

TRANSACTION SCRIPT GROWTH PROBLEM:

  Starts clean (year 1):
    placeOrder() — 30 lines, clear logic.

  Complex after business growth (year 3):
    placeOrder() — 200 lines:
      - Premium customers: 10% discount on orders over $100.
      - Flash sale items: no discount.
      - Loyalty points: 1 point per $1 spent. 2x on Tuesdays. 3x on birthdays.
      - Inventory: check, reserve, and handle out-of-stock.
      - Shipping: calculate based on weight, destination, and carrier.
      - Tax: compute per item based on category and destination.
      - Payment: retry logic with 3 gateway fallbacks.
      - Fraud check: if amount > $500 and new account.

  Same rules duplicated in processGiftOrder() and processSubscriptionOrder().

  Signal: it's time to extract a Domain Model.

COMMON TRANSACTION SCRIPT ORGANIZATION:

  Option 1: One class per use case (Command Pattern style):
    RegisterUserScript.execute(cmd)
    PlaceOrderScript.execute(cmd)

  Option 2: One class per domain area with multiple methods:
    UserService: register(), activate(), deactivate(), updateProfile()
    OrderService: place(), cancel(), ship(), refund()

  Option 3: Stored Procedures (database-level Transaction Script):
    PROCEDURE sp_place_order (@userId, @cartId, @paymentToken)
    -- All steps in SQL. Validation, computation, insert, return.

  All three are Transaction Script: what differs is where the script lives.

HELPER REUSE WITHIN TRANSACTION SCRIPTS:

  Scripts can share helpers — but helpers should be pure functions, not domain objects:

    class DiscountCalculator {               // Helper (not a domain object)
        BigDecimal calculate(BigDecimal total, CustomerType type, boolean isSale) {
            if (isSale) return BigDecimal.ZERO;                          // No discount on sale
            if (type == PREMIUM && total.compareTo(new BigDecimal(100)) > 0) {
                return total.multiply(new BigDecimal("0.10"));           // 10% for premium
            }
            return BigDecimal.ZERO;
        }
    }

    // Used in multiple scripts:
    placeOrder()    → discountCalc.calculate(total, customer.type(), item.isSale())
    reorderScript() → discountCalc.calculate(total, customer.type(), item.isSale())

  When helpers start to have state + behavior → you're building a Domain Model.
  That's fine: Transaction Script naturally evolves into Domain Model as complexity grows.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Transaction Script (forcing Domain Model for simple CRUD):

- 5 classes to implement "register a user" — overkill for 2 validation rules
- Developers spend time building aggregate roots and value objects instead of shipping

WITH Transaction Script:
→ Simple use cases stay simple: one method, all steps visible
→ Fast to build, easy to read and debug
→ Evolves naturally to Domain Model when complexity warrants

---

### 🧠 Mental Model / Analogy

> A TV remote control vs. a universal home automation system. Transaction Script: the TV remote — each button does one thing, all steps visible (press 5 → go to channel 5). Simple, direct, perfect for the job. Domain Model: a home automation system with scenes, rules, and objects that know their own behavior. Perfect for complex homes. For a single TV: the remote is the right tool. Transaction Script matches the remote: one operation per button, all steps explicit, no indirection.

"One button per action" = one script method per use case
"All steps visible" = no method dispatch or object graph
"Too simple for home automation" = Transaction Script for complex domain
"Remote is perfect for the job" = right tool for simple domains

---

### ⚙️ How It Works (Mechanism)

```
TRANSACTION SCRIPT FLOW (single method, linear):

  execute(input)
       │
       ├── Validate input
       ├── Query DB (check preconditions)
       ├── Compute business result
       ├── Update DB
       ├── Side effects (email, notifications)
       └── Return result

  All steps sequential in one method. No object graph traversal. No polymorphism.
```

---

### 🔄 How It Connects (Mini-Map)

```
CRUD / Simple Use Case (few rules, procedural flow)
        │
        ▼
Transaction Script ◄──── (you are here)
(one method per use case; all steps explicit; no domain model)
        │
        ├── Domain Model: richer alternative for complex domains
        ├── Service Layer: Transaction Script often IS the service layer (combined)
        ├── Repository Pattern: Transaction Script uses repos for DB access
        └── Active Record: middle ground — objects with both data and some behavior
```

---

### 💻 Code Example

```java
// Transaction Script for subscription cancellation:
@Service @Transactional
class CancelSubscriptionScript {

    SubscriptionCancelledResponse execute(CancelSubscriptionCommand cmd) {
        // 1. Load data:
        Subscription sub = subRepo.findById(cmd.subscriptionId())
                                  .orElseThrow(SubscriptionNotFoundException::new);
        Customer customer = customerRepo.findById(sub.getCustomerId())
                                        .orElseThrow(CustomerNotFoundException::new);

        // 2. Validate preconditions:
        if (!"ACTIVE".equals(sub.getStatus())) {
            throw new InvalidSubscriptionStateException(
                "Cannot cancel " + sub.getStatus() + " subscription");
        }

        // 3. Business rule — calculate prorated refund:
        long daysRemaining = ChronoUnit.DAYS.between(
            LocalDate.now(), sub.getBillingPeriodEnd());
        long totalDays = ChronoUnit.DAYS.between(
            sub.getBillingPeriodStart(), sub.getBillingPeriodEnd());
        BigDecimal refundAmount = sub.getMonthlyRate()
            .multiply(BigDecimal.valueOf(daysRemaining))
            .divide(BigDecimal.valueOf(totalDays), 2, HALF_UP);

        // 4. Apply state changes:
        sub.setStatus("CANCELLED");
        sub.setCancelledAt(LocalDateTime.now());
        sub.setCancellationReason(cmd.reason());
        subRepo.save(sub);

        // 5. Process refund if applicable:
        if (refundAmount.compareTo(BigDecimal.ZERO) > 0) {
            paymentService.refund(customer.getPaymentMethodId(), refundAmount);
        }

        // 6. Side effects:
        emailService.sendCancellationConfirmation(customer.getEmail(), sub.getId());
        analyticsService.trackCancellation(sub.getId(), cmd.reason());

        return new SubscriptionCancelledResponse(sub.getId(), refundAmount);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                              |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Transaction Script is always an anti-pattern          | No. For simple use cases and CRUD applications, Transaction Script is the appropriate choice. Domain Model has significant overhead (value objects, aggregates, events). For a "create blog post" use case with 1 validation rule, Transaction Script is the right tool              |
| Transaction Script is the same as Anemic Domain Model | Different. Anemic Domain Model: you're TRYING to build OOP/Domain Model but accidentally make your objects data-only bags. Transaction Script: you're CONSCIOUSLY choosing a procedural approach without pretending to use OOP domain objects. Intention is the difference           |
| Transaction Script doesn't scale                      | It scales fine when use cases remain simple. The problem is that it doesn't COMPOSE well: when business rules become complex and shared across scripts, you end up duplicating logic. The trigger to switch to Domain Model is when scripts start sharing non-trivial business rules |

---

### 🔥 Pitfalls in Production

**Scripts grow into unmanageable god methods:**

```java
// BAD: Transaction Script that grew to 150 lines — now unmaintainable:
void processOrder(Long userId, Long cartId, String paymentToken, String couponCode) {
    // 150 lines mixing: validation, discount calculation, inventory, payment,
    // fraud check, loyalty points, shipping cost, tax, order creation,
    // email confirmation, push notification, analytics event...
    // Everything in one method. Impossible to test individual rules.
    // Changing discount logic: touch this 150-line method.
}

// FIX option 1: Extract helper methods (still Transaction Script, more organized):
void processOrder(Long userId, Long cartId, String paymentToken, String couponCode) {
    Cart cart = loadAndValidateCart(cartId, userId);
    Discount discount = calculateDiscount(cart, userId, couponCode);
    Money total = calculateTotal(cart, discount);
    verifyFraud(userId, total);
    Payment payment = chargePayment(paymentToken, total);
    Order order = createAndSaveOrder(cart, payment, discount);
    updateInventory(cart);
    publishOrderConfirmation(order);
}
// Each extracted method is focused. processOrder: readable high-level flow.

// FIX option 2: If rules are complex enough, migrate to Domain Model:
void processOrder(Long userId, Long cartId, String paymentToken, String couponCode) {
    Cart cart = cartRepo.findById(cartId).orElseThrow();
    Coupon coupon = couponCode != null ? couponRepo.findByCode(couponCode).orElseThrow() : null;
    PaymentResult payment = paymentGateway.authorize(paymentToken, cart.total(coupon));
    Order order = cart.checkout(payment, coupon); // Domain model handles all the rules.
    orderRepo.save(order);
}
```

---

### 🔗 Related Keywords

- `Domain Model` — richer alternative for complex domains where Transaction Script becomes unwieldy
- `Service Layer` — Transaction Script methods are often the implementation of service layer methods
- `Repository Pattern` — Transaction Scripts use repositories for all database access
- `Active Record Pattern` — middle ground: domain objects with some behavior, tied to persistence
- `Anemic Domain Model` — different: accidentally building OOP objects with no behavior

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ One method per use case; all steps        │
│              │ explicit and sequential; no domain model. │
│              │ Valid choice for simple domains.          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple CRUD; few business rules; tight    │
│              │ deadline; rules don't repeat across       │
│              │ transactions; prototyping                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex rules that interact; shared logic │
│              │ across transactions; rules change often;  │
│              │ multiple objects must stay consistent     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "TV remote: one button per action, all   │
│              │  steps visible — perfect for a TV, not   │
│              │  for a smart home."                      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain Model → Service Layer →           │
│              │ Active Record Pattern → CQRS             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a Transaction Script `processPayroll(employeeId, payPeriod)` that is 100 lines: calculates gross pay, deductions (tax, health, 401k), net pay, generates paystub, updates employee YTD totals, and records a transaction. The payroll rules for tax and 401k apply to other scripts too (`processBonus()` and `processTerminationPayout()`). You're now duplicating 30 lines of deduction calculation across 3 scripts. At what exact point do you extract a Domain Model, and what would it look like?

**Q2.** A developer writes `registerUser()` as a Transaction Script: validate email, hash password, save user, send welcome email — all in one `@Transactional` method. The `emailService.sendWelcomeEmail()` call at the end succeeds (email sent), but then the database transaction rolls back due to an error in `userRepo.save()`. The email was already sent but the user wasn't created. How do you fix this ordering problem while keeping the Transaction Script pattern? What trade-offs do you accept?
