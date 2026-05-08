---
layout: default
title: "Rich Domain Model"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /software-architecture/rich-domain-model/
id: SAP-025
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Domain Model, Anemic Domain Model, Value Objects, Aggregate Root
used_by: DDD, Clean Architecture, Hexagonal Architecture, Event Sourcing
related: Domain Model, Anemic Domain Model, Aggregate Root, Domain Events, Value Objects
tags:
  - architecture
  - ddd
  - pattern
  - deep-dive
  - advanced
---

# SAP-025 — Rich Domain Model

⚡ TL;DR — A Rich Domain Model is a domain model where objects encapsulate both state and behavior: they enforce their own invariants, use the language of the business, and are the authoritative home for all business logic concerning that object.

---

### 📊 Entry Metadata

| #738            | Category: Software Architecture Patterns                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Domain Model, Anemic Domain Model, Value Objects, Aggregate Root                |                 |
| **Used by:**    | DDD, Clean Architecture, Hexagonal Architecture, Event Sourcing                 |                 |
| **Related:**    | Domain Model, Anemic Domain Model, Aggregate Root, Domain Events, Value Objects |                 |

---

### 🔥 The Problem This Solves

**THE PROBLEM:**
As business logic grows more complex, it scatters across service classes if domain objects have no behavior. The same rule ends up duplicated in multiple places with subtle variations. When business rules change, you must hunt through all services to find every copy of the rule.

**THE SOLUTION:**
Make domain objects the single authoritative home for the logic that governs them. When an `Loan` object is the only place that knows whether a loan can be approved, when an `Order` is the only place that enforces shipping eligibility, the business rules are concentrated, visible, and testable without infrastructure.

---

### 📘 Textbook Definition

A Rich Domain Model is the concrete expression of the Domain Model pattern, where domain classes contain not only the data that represents the domain entity but also the methods that implement the business behaviors and enforce the business invariants of that entity. Rich domain model classes actively guard their own state, raise domain events when significant things happen, and use the vocabulary of the domain (ubiquitous language) in their method and property names. This contrasts with the Anemic Domain Model, where domain classes contain only data.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Domain objects that refuse to be put into invalid states — they know their own rules.

**One analogy:**

> A vending machine is a rich domain model. It knows: it won't dispense if payment is insufficient; it won't accept a denomination it doesn't recognize; it will return change automatically; it tracks its own inventory and signals when items are sold out. The machine doesn't need an external service to validate every operation — the logic is built into the machine itself.

**One insight:**
Rich domain model = objects that say "no" when asked to do something invalid, and do so using the same words the business uses.

---

### 🔩 First Principles Explanation

**CHARACTERISTICS OF A RICH DOMAIN MODEL:**

```
┌──────────────────────────────────────────────────────────┐
│           RICH DOMAIN MODEL CHARACTERISTICS              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Behavior via methods (not setter chains)             │
│     order.approve()   NOT order.setStatus(APPROVED)      │
│                                                          │
│  2. Invariant enforcement                                │
│     loan.approve() throws if credit score < threshold    │
│     — you can NEVER approve a loan below the threshold   │
│                                                          │
│  3. Factory methods for valid construction               │
│     Order.place(customer, items) — validates at birth    │
│     — you CANNOT create an empty order                   │
│                                                          │
│  4. Value Objects for descriptive concepts               │
│     Money, EmailAddress, DateRange instead of            │
│     BigDecimal, String, Date                             │
│                                                          │
│  5. Domain Events for significant state transitions      │
│     order.cancel() → raises OrderCancelledEvent          │
│                                                          │
│  6. No public setters — state changes through methods    │
│     private setters or package-private for ORM          │
└──────────────────────────────────────────────────────────┘
```

**INVARIANT PROTECTION:**

```
┌──────────────────────────────────────────────────────────┐
│              INVARIANT PROTECTION LEVELS                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  At construction (factory method or constructor):        │
│    Product.create(name, price)                           │
│    → price must be > 0 (enforced at creation)            │
│    → name must not be null/blank (enforced at creation)  │
│    Product is ALWAYS valid after construction            │
│                                                          │
│  At state transitions (operation methods):               │
│    product.markAsSoldOut()                               │
│    → can only mark sold-out if currently active          │
│    → raises ProductSoldOutEvent                          │
│                                                          │
│  At aggregate boundaries:                                │
│    order.addItem(product, qty)                           │
│    → cannot add item to a shipped order                  │
│    → recalculates total automatically                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE COMPARISON:**

**Task:** Apply a 10% discount to an order if the customer is a premium member and the order total exceeds £100.

**Anemic approach:**

```java
// In OrderDiscountService (scattered rule):
if (customer.getMembershipTier()
        .equals(MembershipTier.PREMIUM) &&
    order.getTotal().compareTo(new BigDecimal("100")) > 0) {
    order.setDiscountPercentage(new BigDecimal("10"));
    order.setDiscountedTotal(
        order.getTotal().multiply(new BigDecimal("0.9")));
}
// 3 months later, same check in OrderCheckoutService, slightly different
```

**Rich domain approach:**

```java
// In Order:
public void applyPremiumDiscount(Customer customer) {
    if (!customer.isPremiumMember()) {
        throw new NotEligibleForPremiumDiscountException();
    }
    if (total().isLessThanOrEqualTo(Money.of(100, GBP))) {
        throw new OrderTotalBelowDiscountThresholdException();
    }
    this.discount = Discount.percentage(10);
    // Domain event raised — discount applied
    events.add(new PremiumDiscountAppliedEvent(id, discount));
}
```

**The key difference:** The rule is in one place. The test is on `Order`, not on `OrderDiscountService`. The logic cannot be bypassed.

---

### 🧠 Mental Model / Analogy

> A rich domain model is like a smart contract in the legal sense: the terms are encoded into the contract itself. You can't sign a contract on behalf of a minor — the contract validates the signatories. You can't change a signed contract's terms unilaterally — the contract enforces immutability of agreed terms. The rules travel with the contract, not with the lawyers who manage it.

Where this breaks down: Smart contracts are immutable once deployed; domain models are code and can change. The analogy is about rule encapsulation, not immutability.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
Business objects that know and enforce their own rules. You can't put them into an invalid state — they'll refuse and tell you why.

**Level 2 — How to build it (junior):**
Replace setters with intention-revealing methods. Add guard clauses at the start of each method. Use factory methods instead of public constructors. Add value objects for concepts like money or email. Test by calling methods on the domain object directly — no service mocking needed.

**Level 3 — How to design it (mid-level):**
Design the API of the domain object to match the ubiquitous language. Ask: "What can you do with this thing, according to the business?" The answers become the methods. Ask: "What makes this thing invalid?" The answers become the guard clauses. Ask: "What significant things happen to this thing?" The answers become domain events. Design is driven by behaviour, not by database tables.

**Level 4 — Trade-offs and limits (senior/staff):**
Rich domain models require significant upfront design investment and close collaboration with domain experts. They're harder to map to relational databases (impedance mismatch — private fields, no setters, value object types). ORM configuration becomes more complex. Serialization frameworks that require no-arg constructors + setters may fight the rich model design. Solutions: use reflection-based ORMs with explicit field access, builder patterns for construction, or separate persistence models with mappers. The richness of the domain model is worth this complexity only when the business logic is genuinely complex.

---

### ⚙️ How It Works (Mechanism)

**Building blocks of a rich domain model:**

```
┌──────────────────────────────────────────────────────────┐
│        RICH DOMAIN MODEL BUILDING BLOCKS                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  AGGREGATES — consistency boundaries                     │
│    Order aggregates: OrderItems, DeliveryAddress         │
│    Invariant: order total is always consistent with items│
│                                                          │
│  VALUE OBJECTS — descriptive, immutable                  │
│    Money, EmailAddress, PostalCode, DateRange            │
│    Equality by value, not identity                       │
│                                                          │
│  DOMAIN EVENTS — something significant happened          │
│    OrderShippedEvent, LoanApprovedEvent                  │
│    Raised by aggregate, consumed by event handlers       │
│                                                          │
│  DOMAIN SERVICES — logic that spans aggregates           │
│    TransferService: coordinates two Account aggregates   │
│    NOT: OrderStatusService (status belongs on Order)     │
│                                                          │
│  SPECIFICATIONS — reusable business rules                │
│    CanBeCancelledSpec.isSatisfiedBy(order)               │
│    Encapsulates complex eligibility checks               │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│          RICH DOMAIN MODEL — LAYERS OF RICHNESS          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  LAYER 1 — Basic behavior (no setters):                  │
│    order.addItem() / order.cancel() / order.ship()       │
│                                                          │
│  LAYER 2 — Invariant enforcement (guard clauses):        │
│    cancel() throws CannotCancelShippedOrderException     │
│                                                          │
│  LAYER 3 — Value objects (type safety):                  │
│    Order uses Money, not BigDecimal                      │
│    Order uses CustomerId, not UUID                       │
│                                                          │
│  LAYER 4 — Domain events (side-effect notification):     │
│    cancel() → adds OrderCancelledEvent to events list    │
│    Repository commit publishes events                    │
│                                                          │
│  LAYER 5 — Aggregate design (consistency boundaries):    │
│    Order aggregate owns all OrderItem consistency        │
│    One repository per aggregate root                     │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**A fully rich domain model — Loan aggregate:**

```java
public class Loan {
    private final LoanId id;
    private final CustomerId customerId;
    private final Money principal;
    private LoanStatus status;
    private CreditScore approvedAtScore;
    private final List<DomainEvent> events = new ArrayList<>();

    // Factory method — validates on creation
    public static Loan apply(CustomerId customerId,
                              Money principal) {
        Objects.requireNonNull(customerId);
        if (principal.isLessThanOrEqualTo(Money.ZERO)) {
            throw new InvalidLoanAmountException(principal);
        }
        if (principal.isGreaterThan(Money.of(100_000, GBP))) {
            throw new LoanExceedsMaximumException(principal);
        }
        return new Loan(LoanId.generate(),
                         customerId, principal,
                         LoanStatus.PENDING);
    }

    // Behavior with domain rule enforcement
    public void approve(CreditScore score) {
        if (status != LoanStatus.PENDING) {
            throw new LoanAlreadyProcessedException(id,status);
        }
        if (score.isBelow(CreditScore.MINIMUM_FOR_APPROVAL)) {
            throw new InsufficientCreditScoreException(
                id, score);
        }
        this.status = LoanStatus.APPROVED;
        this.approvedAtScore = score;
        events.add(new LoanApprovedEvent(id, customerId,
                                          principal, score));
    }

    public void reject(String reason) {
        if (status != LoanStatus.PENDING) {
            throw new LoanAlreadyProcessedException(id,status);
        }
        this.status = LoanStatus.REJECTED;
        events.add(new LoanRejectedEvent(id, customerId,
                                          reason));
    }

    public void disburse() {
        if (status != LoanStatus.APPROVED) {
            throw new CannotDisburseUnapprovedLoan(id, status);
        }
        this.status = LoanStatus.DISBURSED;
        events.add(new LoanDisbursedEvent(id, customerId,
                                           principal));
    }

    // Read-only — no mutation
    public Money principal() { return principal; }
    public LoanStatus status() { return status; }

    // Collected domain events for publishing after commit
    public List<DomainEvent> domainEvents() {
        return Collections.unmodifiableList(events);
    }
    public void clearEvents() { events.clear(); }
}
```

**Testing the rich domain model — no mocks needed:**

```java
@Test
void approve_rejects_loan_with_insufficient_credit_score() {
    Loan loan = Loan.apply(customerId, Money.of(5000, GBP));
    CreditScore poorScore = CreditScore.of(450);

    assertThatThrownBy(() -> loan.approve(poorScore))
        .isInstanceOf(InsufficientCreditScoreException.class);
    assertThat(loan.status()).isEqualTo(LoanStatus.PENDING);
    assertThat(loan.domainEvents()).isEmpty();
}

@Test
void approved_loan_raises_LoanApprovedEvent() {
    Loan loan = Loan.apply(customerId, Money.of(5000, GBP));
    CreditScore goodScore = CreditScore.of(750);

    loan.approve(goodScore);

    assertThat(loan.status()).isEqualTo(LoanStatus.APPROVED);
    assertThat(loan.domainEvents())
        .hasSize(1)
        .first().isInstanceOf(LoanApprovedEvent.class);
}
```

---

### ⚖️ Comparison Table

| Aspect                  | Rich Domain Model            | Anemic Domain Model                   |
| ----------------------- | ---------------------------- | ------------------------------------- |
| Business logic location | In domain objects            | In service classes                    |
| Invariant enforcement   | Object refuses invalid state | Service must check manually           |
| Testability             | Test domain object directly  | Test service with mocks               |
| Rule duplication risk   | Low — one canonical place    | High — same rule in multiple services |
| ORM compatibility       | Requires configuration       | Easy — plain beans                    |
| Design cost             | High                         | Low                                   |

---

### ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Rich domain model = bloated objects | Rich means behavior-rich, not responsibility-bloated — each class stays focused                                 |
| Requires DDD to implement           | Rich models are a general OO principle; DDD provides useful vocabulary and patterns                             |
| Hard to persist with JPA            | JPA field access mode, protected setters, and Hibernate's constructor bypass mechanisms all support rich models |
| Service layer disappears            | Service layer coordinates use cases and infrastructure; domain layer owns business rules — both exist           |

---

### 🚨 Failure Modes & Diagnosis

**God Object: Too Much Richness in One Class**

**Symptom:** Domain object grows to 1000+ lines. It imports service interfaces, repositories, or infrastructure types. Everything is a method on one mega-object.

**Root Cause:** Over-application of the pattern — rich model does not mean one class owns everything. Domain services handle cross-aggregate behavior. Aggregates have clear boundaries.

**Fix:** Extract domain services for cross-aggregate operations. Split large aggregates on bounded context boundaries.

---

**Bypassing Rich Model via Reflection or Setters**

**Symptom:** Direct field access or setter calls from outside the domain in tests or migrations. Invariants silently broken.

**Root Cause:** Test setup bypassing the public API, or data migration scripts using direct field manipulation.

**Fix:** Test factory helpers that use the domain object's own creation methods. Migration scripts treated as first-class concern that go through the domain API.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Domain Model` — the concept this implements
- `Anemic Domain Model` — the anti-pattern this replaces

**Builds On This:**

- `Aggregate Root` — how to define consistency boundaries in a rich model
- `Domain Events` — raised by rich model objects
- `Value Objects` — used within rich domain models

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Domain objects with data + behavior + rules│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Objects refuse invalid states themselves  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex business domain with real rules   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD, no meaningful business logic │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Design investment vs scattered logic risk  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Objects that know and enforce their       │
│              │  own rules"                                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your `Order` aggregate has grown to include 15 methods and references to `Customer`, `Product`, `Inventory`, and `Payment` domain objects. It's becoming difficult to understand and test. How do you decide which behaviors belong on `Order` itself versus in a domain service, and what rule helps you make that distinction?

**Q2.** You need to import legacy data from an old system that doesn't conform to your rich domain model's invariants (for example, some historical orders have a `null` customer). How do you handle this in a system where your domain model strictly enforces that an order always has a customer?
