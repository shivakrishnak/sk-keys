---
layout: default
title: "Tell Don't Ask"
parent: "Software Architecture Patterns"
nav_order: 759
permalink: /software-architecture/tell-dont-ask/
number: "759"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Law of Demeter, Cohesion and Coupling, Object-Oriented Programming"
used_by: "OOP design, Domain Model, Code review, Refactoring"
tags: #intermediate, #architecture, #oop, #coupling, #domain-model
---

# 759 — Tell Don't Ask

`#intermediate` `#architecture` `#oop` `#coupling` `#domain-model`

⚡ TL;DR — **Tell Don't Ask (TDA)** says objects should be TOLD to do something, not ASKED for their data so the caller can make decisions — keeping behavior and the data it operates on together in the same object, enforcing encapsulation and high cohesion.

| #759            | Category: Software Architecture Patterns                           | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Law of Demeter, Cohesion and Coupling, Object-Oriented Programming |                 |
| **Used by:**    | OOP design, Domain Model, Code review, Refactoring                 |                 |

---

### 📘 Textbook Definition

**Tell Don't Ask (TDA)** (Alec Sharp, 1997; popularized by Martin Fowler): a principle of object-oriented design stating that, instead of querying an object for its state and making decisions based on that state OUTSIDE the object, you should tell the object to make the decision and act on it itself. TDA is a direct consequence of encapsulation: if an object owns data, it should also own the behavior that operates on that data. Violation of TDA: extracting data from object A, computing something, and calling back into A based on the result — the logic lives outside the object that has the data. TDA pushes that logic INTO the object that has the data, making the object responsible for its own decisions. This leads to richer domain models (domain logic in domain objects) and anemic domain models as the anti-pattern.

---

### 🟢 Simple Definition (Easy)

A thermostat. Tell (TDA): you say "Set temperature to 22°C." The thermostat decides when to turn on/off the heater, when it's reached temperature, how fast to change. You don't constantly check the temperature yourself and manually flip the heater switch. Ask (anti-TDA): you check the current temperature every minute, decide yourself if the heater should be on or off, then flip the switch. You have to know all the thermostat's logic. The thermostat is just a data container.

---

### 🔵 Simple Definition (Elaborated)

Anemic domain model (anti-TDA): `Order` is a data class with getters/setters. `OrderService` gets `order.getStatus()`, checks `if status == PENDING`, then calls `order.setStatus(CONFIRMED)`, and computes shipping cost from `order.getTotal()`. The ORDER class has no behavior — all behavior lives in the service. Rich domain model (TDA): `order.confirm(payment)` — the Order object handles its own state transition, validates it's in the right state, fires the domain event. The service just says "confirm this order." It doesn't know HOW; the order does.

---

### 🔩 First Principles Explanation

**Anemic vs. rich domain model — the TDA divide:**

```
THE ANTI-PATTERN: ASK

  // ASK pattern (procedural thinking in OO):
  class OrderService {
      void confirmOrder(Order order, Payment payment) {
          // ASKING for state:
          if (order.getStatus() != OrderStatus.PENDING) {
              throw new InvalidStateException("Order is not pending");
          }
          if (payment.getAmount().compareTo(order.getTotal()) < 0) {
              throw new InsufficientPaymentException();
          }
          if (order.getItems().isEmpty()) {
              throw new EmptyOrderException();
          }

          // MAKING DECISIONS outside the object:
          order.setStatus(OrderStatus.CONFIRMED);
          order.setConfirmedAt(Instant.now());
          order.setPaymentReference(payment.getReference());

          // ACTING on Order's data externally:
          eventBus.publish(new OrderConfirmedEvent(order.getId(), order.getTotal()));
      }
  }

  Problems:
    1. Business rules scattered in service — not in Order object.
    2. Order has no behavior. It's a data bag with setters.
    3. 5 different services call order.getStatus() + different logic: duplicated rules.
    4. ORDER cannot protect its own invariants — status can be set to anything from outside.

THE PATTERN: TELL

  // TELL pattern (OO encapsulation):
  class Order {
      void confirm(Payment payment) {
          // Order OWNS its own validation and state transition:
          if (this.status != OrderStatus.PENDING)
              throw new InvalidStateException("Cannot confirm a " + status + " order");
          if (payment.amount().isLessThan(this.total))
              throw new InsufficientPaymentException(payment.amount(), this.total);
          if (this.items.isEmpty())
              throw new EmptyOrderException();

          // Order makes its OWN decisions:
          this.status = OrderStatus.CONFIRMED;
          this.confirmedAt = Instant.now();
          this.paymentReference = payment.reference();

          // Order fires its OWN events:
          this.events.add(new OrderConfirmedEvent(this.id, this.total));
      }
  }

  class OrderService {
      void confirmOrder(OrderId id, Payment payment) {
          Order order = orderRepository.findById(id).orElseThrow();
          order.confirm(payment);  // TELL the order to confirm itself. Done.
          orderRepository.save(order);
          eventBus.publishAll(order.domainEvents());
      }
  }

  Benefits:
    1. Business rules in Order — where the data lives. High cohesion.
    2. Order protects its own invariants — no external setter abuse.
    3. Confirmation logic in ONE place — no duplication across services.
    4. Service is a thin orchestrator: find → tell → save → publish.

WHERE TDA APPLIES (and where it doesn't):

  APPLIES: Domain model (aggregates, entities, value objects).
    The rich domain model is the TDA goal for domain objects.

  BORDERLINE: Service layer.
    Services orchestrate — they often need to check conditions before calling.
    But they should not re-implement domain logic that belongs in the domain object.

  DOESN'T APPLY (and shouldn't be forced):
    Data Transfer Objects (DTOs): pure data, no behavior expected.
    Query models (CQRS read side): flat projections, no domain logic.
    Configuration objects: properties, no behavior.
    Report generation: reading state is the point.

  WARNING — over-applying TDA:

    // DON'T force TDA on simple value access:
    boolean isEligibleForDiscount = customer.checkAndComputeEligibility(order);
    // vs.
    boolean isEligible = customer.isPremium() && order.total().isGreaterThan(MIN_ORDER);

    // The second might be cleaner when the condition is simple and the decision
    // BELONGS to the caller (e.g., a policy object, not the domain object).

    TDA is a GUIDELINE, not a law. Apply it where domain behavior belongs in the domain object.

ANEMIC DOMAIN MODEL (TDA anti-pattern):

  Recognized by:
    - Domain objects: getters + setters, no business methods
    - Service classes: ALL business logic, calling getters + setters on domain objects
    - Domain objects: easy to serialize/deserialize (just data)
    - Business rule change: must find service code, not domain code

  Martin Fowler calls it "anemic domain model" — objects that LOOK like OO
  (have classes, inheritance, etc.) but ARE NOT OO in the behavioral sense.
  Result: procedural programming with class names.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Tell Don't Ask (Anemic Model):

- Domain logic scattered across 5 services — each re-implements variations of the same rule
- `Order.setStatus()` called from anywhere — invariants unenforceable

WITH Tell Don't Ask:
→ `order.confirm(payment)` — one method, all rules in one place
→ Order enforces its own invariants — impossible to call with invalid state

---

### 🧠 Mental Model / Analogy

> A bank teller vs. a self-service ATM with an expert system. ASK: You ask the teller "What's my balance?" Then you do mental math, decide if you can afford a transaction, tell the teller "debit $500." Then ask "What's my new balance?" — You are doing the bank's logic externally, using the teller as a data retrieval system. TELL: You say "transfer $500 to account X." The bank system checks balance, applies the transfer rules, updates state, sends notification. You don't know how — you told it what you want. The bank does the rest.

"Bank doing its own logic" = Tell (object owns its behavior)
"You doing the bank's math externally" = Ask (logic outside the object)
"Teller as data retrieval system" = anemic domain model (pure data bag)
"Transfer command" = tell-style method that encapsulates all logic

---

### ⚙️ How It Works (Mechanism)

```
TDA TRANSFORMATION:

  BEFORE (Ask):                        AFTER (Tell):
  if (user.getStatus() == ACTIVE) {    user.deactivate(reason);
    user.setStatus(INACTIVE);          // User checks own state,
    user.setDeactivatedAt(now());      // updates fields,
    user.setDeactivationReason(r);     // fires event internally
    eventBus.publish(event);
  }

  TRANSFORMATION STEPS:
  1. Find: "caller gets state from object, makes decision, calls setters."
  2. Create: new method on the object: deactivate(reason)
  3. Move: validation + state change logic INTO the method
  4. Replace: all caller code with the new method call
  5. Remove: setters if they're no longer needed externally
```

---

### 🔄 How It Connects (Mini-Map)

```
Anemic Domain Model (data bags + service with all behavior)
        │
        ▼ (move behavior to objects)
Tell Don't Ask ◄──── (you are here)
(tell objects to act; don't extract their data to act externally)
        │
        ├── Law of Demeter: LoD = don't navigate strangers; TDA = don't extract data to decide
        ├── Domain Model (DDD): TDA produces rich domain models with behavior
        ├── Command-Query Separation: TDA commands (tell) vs. queries (ask read state)
        └── Encapsulation: TDA enforces encapsulation — data and behavior together
```

---

### 💻 Code Example

```java
// ASK (anemic model — anti-pattern):
class SubscriptionService {
    void renewSubscription(Subscription sub) {
        if (sub.getStatus() == EXPIRED &&
            sub.getExpiresAt().isBefore(Instant.now().plus(30, DAYS))) {
            sub.setStatus(ACTIVE);
            sub.setExpiresAt(Instant.now().plus(365, DAYS));
            sub.setRenewedAt(Instant.now());
            sub.setRenewalCount(sub.getRenewalCount() + 1);
            emailService.sendRenewalConfirmation(sub.getUserId(), sub.getExpiresAt());
        }
        // Business logic lives HERE, not in Subscription. Setters expose internals.
    }
}

// ────────────────────────────────────────────────────────────────────

// TELL (rich domain model):
class Subscription {  // Domain aggregate owns its behavior:
    void renew() {
        if (this.status != EXPIRED)
            throw new CannotRenewException("Only expired subscriptions can be renewed");

        // Object makes its OWN state decisions:
        this.status = ACTIVE;
        this.expiresAt = Instant.now().plus(365, DAYS);
        this.renewedAt = Instant.now();
        this.renewalCount++;

        // Records domain event internally:
        this.events.add(new SubscriptionRenewedEvent(this.userId, this.expiresAt));
    }
}

class SubscriptionService {
    void renewSubscription(SubscriptionId id) {
        Subscription sub = repo.findById(id).orElseThrow();
        sub.renew();       // TELL — one line. Service is a thin orchestrator.
        repo.save(sub);
        eventBus.publishAll(sub.domainEvents());
    }
}
// Business rule for renewal: ONE place (Subscription.renew()). No setters exposed.
```

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tell Don't Ask means never use getters | TDA applies to BEHAVIORAL decisions: don't get state to make a decision that belongs in the object. Getters for display, reporting, serialization, or cross-boundary data transfer are fine. The key test: "Am I getting this data to make a decision that should be the object's responsibility?" If yes: TDA applies. If the data is read for display or external use: getters are fine |
| TDA means all services should be empty | Service classes are legitimate orchestrators. They coordinate between aggregates, call repositories, publish events. TDA means services should not contain DOMAIN LOGIC that operates on a single aggregate's data. Cross-aggregate orchestration belongs in services. Single-aggregate behavior belongs in the aggregate                                                                 |
| TDA conflicts with CQRS                | CQRS and TDA serve different purposes. CQRS separates write models (commands/tell) from read models (queries/ask-read-only). The WRITE side should use TDA — tell commands to aggregates that own behavior. The READ side is purely about reading — getting data for display. No conflict: TDA applies to the write side, not the read projections                                        |

---

### 🔥 Pitfalls in Production

**Feature envy service — symptom of TDA violation:**

```java
// ANTI-PATTERN: Service with "feature envy" — uses Loan's data more than its own:
class LoanService {
    void applyLatePenalty(Loan loan) {
        if (loan.getDueDate().isBefore(LocalDate.now()) &&
            loan.getStatus() == LoanStatus.OUTSTANDING &&
            loan.getOutstandingAmount().isGreaterThan(Money.ZERO)) {

            Money penalty = loan.getOutstandingAmount()
                               .multiply(loan.getInterestRate())
                               .multiply(BigDecimal.valueOf(0.05));

            loan.setOutstandingAmount(loan.getOutstandingAmount().add(penalty));
            loan.setPenaltyAppliedAt(LocalDate.now());
            loan.setPenaltyCount(loan.getPenaltyCount() + 1);
        }
    }
    // "Feature envy": LoanService is obsessed with Loan's data.
    // Sign: this method belongs ON Loan.
}

// FIX: Move to Loan (the object that has all the data):
class Loan {
    void applyLatePenalty(LocalDate today) {
        if (!today.isAfter(this.dueDate)) return;  // not late
        if (this.status != LoanStatus.OUTSTANDING) return;
        if (this.outstandingAmount.isZero()) return;

        Money penalty = this.outstandingAmount.multiply(this.interestRate).multiply(FIVE_PERCENT);
        this.outstandingAmount = this.outstandingAmount.add(penalty);
        this.penaltyAppliedAt = today;
        this.penaltyCount++;
        this.events.add(new LatePenaltyAppliedEvent(this.id, penalty));
    }
}
// LoanService: loan.applyLatePenalty(LocalDate.now()); — one line. Done.
```

---

### 🔗 Related Keywords

- `Law of Demeter` — closely related: LoD = don't navigate strangers; TDA = don't externalize object's logic
- `Anemic Domain Model` — the anti-pattern that TDA prevents (data bags with no behavior)
- `Domain Model` — TDA produces rich domain models where aggregates own their logic
- `Command-Query Separation` — TDA commands (tell objects to act) and CQS (tell vs. ask read)
- `Encapsulation` — TDA is the behavioral consequence of encapsulation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Objects should be TOLD to do something,   │
│              │ not ASKED for data so caller decides.     │
│              │ Behavior belongs with the data it uses.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service code extracts object state to make│
│              │ decisions and call setters — move that    │
│              │ logic into the domain object              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Reading data for display/serialization;  │
│              │ CQRS read side; simple config access;    │
│              │ DTOs — don't force behavior onto them    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tell the bank to transfer $500 — don't   │
│              │  ask for balance, calculate yourself,     │
│              │  then call setBalance()."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Anemic Domain Model → Domain Model →      │
│              │ Law of Demeter → Command-Query Separation │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `User` aggregate has: `status`, `lastLoginAt`, `failedLoginCount`. The current `AuthService` checks: `if (user.getStatus() == ACTIVE && user.getFailedLoginCount() < 5)` then calls `user.setLastLoginAt(now)`, `user.setFailedLoginCount(0)`. Apply Tell Don't Ask: what method should you add to `User`? What does `user.login(credentials)` return? What events does it fire internally? What happens when you move this logic into `User` and someone argues that `User` "shouldn't know about authentication"?

**Q2.** A CQRS system: write side uses TDA (aggregates with rich behavior, tell-style commands). Read side uses projections — DTOs with only getters, no behavior, data returned from queries. Is the read side violating TDA by being an "anemic" data bag? How do you reconcile TDA on the write side with the intentionally anemic read side? Does CQRS actually REQUIRE some degree of "ask" on the read side?
