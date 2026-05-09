---
id: SAP-025
title: Rich Domain Model
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-023, SAP-024
used_by: SAP-030
related: SAP-023, SAP-030
tags:
  - architecture
  - ddd
  - pattern
  - advanced
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /software-architecture/rich-domain-model/
---

# SAP-025 - Rich Domain Model

⚡ TL;DR - A Rich Domain Model is a domain model where objects encapsulate both state and behavior: they enforce their own invariants, use the language of the business, and are the authoritative home for all business logic concerning that object.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | SAP-023, SAP-024 |
| **Used by**    | SAP-030          |
| **Related**    | SAP-023, SAP-030 |

---

### 🔥 The Problem This Solves

**THE PROBLEM:**
As business logic grows more complex, it scatters across service classes if domain objects have no behavior. The same rule ends up duplicated in multiple places with subtle variations. When business rules change, you must hunt through all services to find every copy of the rule.

**THE SOLUTION:**
Make domain objects the single authoritative home for the logic that governs them. When an `Loan` object is the only place that knows whether a loan can be approved, when an `Order` is the only place that enforces shipping eligibility, the business rules are concentrated, visible, and testable without infrastructure.

**EVOLUTION:**
Eric Evans's "Domain-Driven Design" (2003) made the Rich Domain Model the gold standard for complex business domains, providing an entire methodology (aggregates, repositories, domain events, bounded contexts) for building them. Allen Holub's "Tell Don't Ask" principle and Robert Martin's SOLID principles provided the design rules for individual rich domain objects. The pattern faced its most significant practical challenge with JPA/Hibernate, which requires mutable entities with no-arg constructors - a direct conflict with "always valid" rich domain objects. Kotlin records and Java 16+ records have partially resolved this by providing immutable value objects with less boilerplate.

---

### 📘 Textbook Definition

A Rich Domain Model is the concrete expression of the Domain Model pattern, where domain classes contain not only the data that represents the domain entity but also the methods that implement the business behaviors and enforce the business invariants of that entity. Rich domain model classes actively guard their own state, raise domain events when significant things happen, and use the vocabulary of the domain (ubiquitous language) in their method and property names. This contrasts with the Anemic Domain Model, where domain classes contain only data.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Domain objects that refuse to be put into invalid states - they know their own rules.

**One analogy:**

> A vending machine is a rich domain model. It knows: it won't dispense if payment is insufficient; it won't accept a denomination it doesn't recognize; it will return change automatically; it tracks its own inventory and signals when items are sold out. The machine doesn't need an external service to validate every operation - the logic is built into the machine itself.

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
│     - you can NEVER approve a loan below the threshold   │
│                                                          │
│  3. Factory methods for valid construction               │
│     Order.place(customer, items) - validates at birth    │
│     - you CANNOT create an empty order                   │
│                                                          │
│  4. Value Objects for descriptive concepts               │
│     Money, EmailAddress, DateRange instead of            │
│     BigDecimal, String, Date                             │
│                                                          │
│  5. Domain Events for significant state transitions      │
│     order.cancel() → raises OrderCancelledEvent          │
│                                                          │
│  6. No public setters - state changes through methods    │
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
    // Domain event raised - discount applied
    events.add(new PremiumDiscountAppliedEvent(id, discount));
}
```

**The key difference:** The rule is in one place. The test is on `Order`, not on `OrderDiscountService`. The logic cannot be bypassed.

---

### 🧠 Mental Model / Analogy

> A rich domain model is like a smart contract in the legal sense: the terms are encoded into the contract itself. You can't sign a contract on behalf of a minor - the contract validates the signatories. You can't change a signed contract's terms unilaterally - the contract enforces immutability of agreed terms. The rules travel with the contract, not with the lawyers who manage it.

Where this breaks down: Smart contracts are immutable once deployed; domain models are code and can change. The analogy is about rule encapsulation, not immutability.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Business objects that know and enforce their own rules. You can't put them into an invalid state - they'll refuse and tell you why.

**Level 2 - How to build it (junior):**
Replace setters with intention-revealing methods. Add guard clauses at the start of each method. Use factory methods instead of public constructors. Add value objects for concepts like money or email. Test by calling methods on the domain object directly - no service mocking needed.

**Level 3 - How to design it (mid-level):**
Design the API of the domain object to match the ubiquitous language. Ask: "What can you do with this thing, according to the business?" The answers become the methods. Ask: "What makes this thing invalid?" The answers become the guard clauses. Ask: "What significant things happen to this thing?" The answers become domain events. Design is driven by behaviour, not by database tables.

**Level 4 - Trade-offs and limits (senior/staff):**
Rich domain models require significant upfront design investment and close collaboration with domain experts. They're harder to map to relational databases (impedance mismatch - private fields, no setters, value object types). ORM configuration becomes more complex. Serialization frameworks that require no-arg constructors + setters may fight the rich model design. Solutions: use reflection-based ORMs with explicit field access, builder patterns for construction, or separate persistence models with mappers. The richness of the domain model is worth this complexity only when the business logic is genuinely complex.

---

### ⚙️ How It Works (Mechanism)

**Building blocks of a rich domain model:**

```
┌──────────────────────────────────────────────────────────┐
│        RICH DOMAIN MODEL BUILDING BLOCKS                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  AGGREGATES - consistency boundaries                     │
│    Order aggregates: OrderItems, DeliveryAddress         │
│    Invariant: order total is always consistent with items│
│                                                          │
│  VALUE OBJECTS - descriptive, immutable                  │
│    Money, EmailAddress, PostalCode, DateRange            │
│    Equality by value, not identity                       │
│                                                          │
│  DOMAIN EVENTS - something significant happened          │
│    OrderShippedEvent, LoanApprovedEvent                  │
│    Raised by aggregate, consumed by event handlers       │
│                                                          │
│  DOMAIN SERVICES - logic that spans aggregates           │
│    TransferService: coordinates two Account aggregates   │
│    NOT: OrderStatusService (status belongs on Order)     │
│                                                          │
│  SPECIFICATIONS - reusable business rules                │
│    CanBeCancelledSpec.isSatisfiedBy(order)               │
│    Encapsulates complex eligibility checks               │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│          RICH DOMAIN MODEL - LAYERS OF RICHNESS          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  LAYER 1 - Basic behavior (no setters):                  │
│    order.addItem() / order.cancel() / order.ship()       │
│                                                          │
│  LAYER 2 - Invariant enforcement (guard clauses):        │
│    cancel() throws CannotCancelShippedOrderException     │
│                                                          │
│  LAYER 3 - Value objects (type safety):                  │
│    Order uses Money, not BigDecimal                      │
│    Order uses CustomerId, not UUID                       │
│                                                          │
│  LAYER 4 - Domain events (side-effect notification):     │
│    cancel() → adds OrderCancelledEvent to events list    │
│    Repository commit publishes events                    │
│                                                          │
│  LAYER 5 - Aggregate design (consistency boundaries):    │
│    Order aggregate owns all OrderItem consistency        │
│    One repository per aggregate root                     │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**A fully rich domain model - Loan aggregate:**

```java
public class Loan {
    private final LoanId id;
    private final CustomerId customerId;
    private final Money principal;
    private LoanStatus status;
    private CreditScore approvedAtScore;
    private final List<DomainEvent> events = new ArrayList<>();

    // Factory method - validates on creation
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

    // Read-only - no mutation
    public Money principal() { return principal; }
    public LoanStatus status() { return status; }

    // Collected domain events for publishing after commit
    public List<DomainEvent> domainEvents() {
        return Collections.unmodifiableList(events);
    }
    public void clearEvents() { events.clear(); }
}
```

**Testing the rich domain model - no mocks needed:**

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
| Rule duplication risk   | Low - one canonical place    | High - same rule in multiple services |
| ORM compatibility       | Requires configuration       | Easy - plain beans                    |
| Design cost             | High                         | Low                                   |

---

### ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Rich domain model = bloated objects | Rich means behavior-rich, not responsibility-bloated - each class stays focused                                 |
| Requires DDD to implement           | Rich models are a general OO principle; DDD provides useful vocabulary and patterns                             |
| Hard to persist with JPA            | JPA field access mode, protected setters, and Hibernate's constructor bypass mechanisms all support rich models |
| Service layer disappears            | Service layer coordinates use cases and infrastructure; domain layer owns business rules - both exist           |

---

### 🚨 Failure Modes & Diagnosis

**God Object: Too Much Richness in One Class**

**Symptom:** Domain object grows to 1000+ lines. It imports service interfaces, repositories, or infrastructure types. Everything is a method on one mega-object.

**Root Cause:** Over-application of the pattern - rich model does not mean one class owns everything. Domain services handle cross-aggregate behavior. Aggregates have clear boundaries.

**Fix:** Extract domain services for cross-aggregate operations. Split large aggregates on bounded context boundaries.

---

**Bypassing Rich Model via Reflection or Setters**

**Symptom:** Direct field access or setter calls from outside the domain in tests or migrations. Invariants silently broken.

**Root Cause:** Test setup bypassing the public API, or data migration scripts using direct field manipulation.

**Fix:** Test factory helpers that use the domain object's own creation methods. Migration scripts treated as first-class concern that go through the domain API.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Objects that guard their own invariants remove the burden of invariant enforcement from every caller. The object is the single point of truth for what is valid. This encapsulation principle scales from individual objects to systems.

**Where else this pattern appears:**
- **Vending machines:** the machine enforces all its own rules (insufficient funds, unknown denomination, out of stock) internally; no external system needs to validate each operation before triggering it.
- **Type systems:** a strong type system is a rich domain model at the language level - a `NonEmptyString` type enforces the invariant "this string is never empty" at compile time without any caller needing to check.
- **Electrical safety standards:** a circuit breaker enforces the "maximum current" invariant internally and trips itself; no external monitoring system needs to detect overcurrent and then command the breaker.

---

### 💡 The Surprising Truth

Rich domain models are the hardest design to persist with most ORMs. JPA/Hibernate requires mutable entities with public or package-private setters and a no-arg constructor - exactly the design that a Rich Domain Model forbids (no public setters, always-valid construction only). The practical result is that teams using JPA with DDD must choose between: (1) using JPA entity classes AS domain objects (compromising invariant enforcement), (2) maintaining separate JPA entity classes and domain objects (mapping overhead), or (3) using a different persistence mechanism (e.g., R2DBC with manual mapping, or Document stores). This ORM impedance mismatch is the most underestimated practical challenge in DDD adoption.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-023 - Domain Model (the foundational concept; Rich Domain Model is the concrete expression of the Domain Model pattern)
- SAP-024 - Anemic Domain Model (the anti-pattern; understanding what a Rich Domain Model replaces reveals why the investment is worthwhile)

**Builds On This (learn these next):**
- SAP-030 - Aggregate Root (how to define consistency boundaries in a system of rich domain objects; aggregates are the organizing principle for rich models)

**Alternatives / Comparisons:**
- SAP-024 - Anemic Domain Model (correct for simple CRUD with no meaningful business rules; the trade-off is explicit)
- Transaction Script - procedural alternative; correct for simple workflows with no need for an object model

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

*Hint:* Research Evans' rule for Domain Services: behavior that naturally belongs to no single entity or value object should live in a Domain Service. Specifically, if the behavior requires data from MULTIPLE aggregates (Order + Inventory + Customer) it does not naturally belong on any one of them. The test: "If I delete this method from Order and put it in a service, does Order still make sense?" If yes, the service is correct.

**Q2.** You need to import legacy data from an old system that doesn't conform to your rich domain model's invariants (for example, some historical orders have a `null` customer). How do you handle this in a system where your domain model strictly enforces that an order always has a customer?

*Hint:* Research the "Anti-Corruption Layer" pattern (SAP-034) and specifically the technique of using a separate "import" aggregate or "migration" bounded context that accepts legacy data without invariant enforcement, then transforms it into valid domain events that the main bounded context can consume. Also look at database migration strategies that accept legacy nulls during import but enforce NOT NULL constraints after cleanup.

**Q3.** A Rich Domain Model enforces the "always valid" principle: a domain object must never be in an invalid state. But during a multi-step business process (a loan application with 5 stages), the `LoanApplication` object transitions through partially-complete states that would fail a "fully valid" check. How do you design an `LoanApplication` that enforces appropriate invariants at each stage without introducing a god-object with 50 validity conditions?

*Hint:* Research the "State Pattern" applied to Domain objects and specifically the concept of "stage-specific invariants" - a `LoanApplication` in `DRAFT` state has different valid invariants than one in `SUBMITTED` or `APPROVED` state. Look at how Evans treats this with separate domain concepts per stage (DraftApplication, SubmittedApplication, ApprovedApplication) versus a single entity with a state machine.
