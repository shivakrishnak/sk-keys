---
layout: default
title: "DRY Principle"
parent: "Software Architecture Patterns"
nav_order: 751
permalink: /software-architecture/dry-principle/
number: "751"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "SOLID Principles, Cohesion and Coupling, Refactoring"
used_by: "Code quality, Refactoring, Design Patterns, Clean Code"
tags: #intermediate, #architecture, #principles, #clean-code, #refactoring
---

# 751 — DRY Principle

`#intermediate` `#architecture` `#principles` `#clean-code` `#refactoring`

⚡ TL;DR — **DRY (Don't Repeat Yourself)** states that every piece of knowledge should have a single, authoritative representation in the system — preventing the "same logic in multiple places" problem where a rule change requires hunting and updating every copy.

| #751            | Category: Software Architecture Patterns               | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | SOLID Principles, Cohesion and Coupling, Refactoring   |                 |
| **Used by:**    | Code quality, Refactoring, Design Patterns, Clean Code |                 |

---

### 📘 Textbook Definition

**DRY — Don't Repeat Yourself** (Andrew Hunt & Dave Thomas, "The Pragmatic Programmer," 1999): "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." DRY is not about avoiding duplicate code — it's about avoiding duplicate KNOWLEDGE. The distinction: (1) **Knowledge duplication**: the same business rule, algorithm, or domain concept expressed in multiple places. Change the rule: must find and update every copy. (2) **Code duplication**: similar-looking code that represents DIFFERENT knowledge (same structure, different intent). Extracting this into shared code: wrong — it couples unrelated concepts. The DRY violation to address: when a business rule change requires editing multiple files. Accidental code similarity: do NOT extract just because code looks similar.

---

### 🟢 Simple Definition (Easy)

A law vs. multiple people interpreting it. DRY: the law exists once in the legal code. Everyone references the same source. Change the law: one change, everyone automatically follows the new version. Anti-DRY: the law is written in 20 different employee handbooks, each with slight variations. Change the law: find all 20 handbooks. Miss one: that company still follows the old law.

---

### 🔵 Simple Definition (Elaborated)

A discount rule: "Premium customers get 10% off orders over $100." This rule written in: `OrderService.placeOrder()`, `ReportingService.generateReport()`, `BatchJob.processDiscounts()`, and `API.applyDiscount()`. Business says: "Change it to 15%." Four files to find and update. Miss one: that code path applies the wrong discount. DRY: extract `PremiumDiscountPolicy.calculate()` — one implementation. Reference it from all four. Change: one file. All four paths automatically updated. The RULE exists once.

---

### 🔩 First Principles Explanation

**What DRY actually means vs. common misunderstandings:**

```
DRY IS ABOUT KNOWLEDGE, NOT LINES OF CODE:

  WRONG application of DRY (structure similarity, not knowledge):

    // Order validation:
    if (order.customerId() == null) throw new ValidationException("customerId required");
    if (order.items().isEmpty())    throw new ValidationException("items required");

    // User validation:
    if (user.email() == null)       throw new ValidationException("email required");
    if (user.name().isBlank())      throw new ValidationException("name required");

    // These LOOK similar. Should you extract a common validateNotNull(field, name) helper?

    ONLY IF: the validation rule is the same knowledge (same business rule).

    If order validation rules and user validation rules evolve independently:
      Extracting them couples them. Change user validation: might break order validation.
      The similar structure is COINCIDENTAL, not shared knowledge.

  CORRECT application of DRY (knowledge duplication):

    // Premium discount rule written THREE times:

    // In OrderService:
    if (customer.isPremium() && order.total().isGreaterThan(Money.of(100, USD))) {
        BigDecimal discount = order.total().amount().multiply(new BigDecimal("0.10"));
        // apply discount...
    }

    // In ReportingService:
    boolean isDiscountEligible = customer.isPremium()
        && order.getTotal().compareTo(100.0) > 0;
    double discountAmount = isDiscountEligible ? order.getTotal() * 0.10 : 0;

    // In BatchDiscountJob:
    if (customerTier.equals("PREMIUM") && orderTotal > 100.00) {
        discount = orderTotal * 0.1;
    }

    // THREE representations of ONE rule. Each uses different types, different thresholds,
    // different variable names. Business change: THREE places to update.
    // One is a String comparison ("PREMIUM"), one is a boolean method, one compares a double.

    DRY FIX — the KNOWLEDGE in one place:

    class PremiumDiscountPolicy {
        private static final Money MINIMUM_ORDER = Money.of(100, USD);
        private static final Percentage DISCOUNT_RATE = Percentage.of(10);

        boolean isEligible(Customer customer, Order order) {
            return customer.isPremium() && order.total().isGreaterThan(MINIMUM_ORDER);
        }

        Money calculateDiscount(Order order) {
            return order.total().applyDiscount(DISCOUNT_RATE);
        }
    }

    // Now: OrderService, ReportingService, BatchJob all use PremiumDiscountPolicy.
    // Business change to 15%: PremiumDiscountPolicy.DISCOUNT_RATE = Percentage.of(15).
    // ONE change. Done.

TYPES OF DRY VIOLATIONS:

  1. DUPLICATED CODE (most visible):
     Same or similar code blocks in multiple methods/classes.
     Fix: extract to a shared method or class.

  2. DUPLICATED LOGIC:
     Same business rule re-implemented multiple times (sometimes in different styles).
     Fix: extract to a domain object, policy, or specification.

  3. DUPLICATED KNOWLEDGE IN SCHEMA + CODE:
     Database: column CHECK constraint validates email format.
     Java: @Email annotation validates email format.
     API: regex validates email format.
     Three representations of ONE rule: "what is a valid email?"
     If the rule changes: three places to update.
     Fix: define email validation once (domain object Email) and rely on it.

  4. DOCUMENTATION THAT REPEATS CODE:
     // This method adds two numbers:
     int add(int a, int b) { return a + b; }
     The comment repeats what the code says. Comment will get out of sync.
     Fix: write code that speaks for itself. Comment WHY, not WHAT.

WRY THE MISUNDERSTOOD TWIN:

  WRY = "Write it Right, then Yes, DRY" — informal reminder:
  First: make it work. Second: make it right. THEN: deduplicate.

  Two pieces of similar code? Don't rush to extract:
  - Are they really the same KNOWLEDGE? Or just similar STRUCTURE?
  - Do they change for the same reason? (SRP question)
  - Would extracting couple them unnecessarily?

  Rule of Three (Ron Jeffries):
    Write it once: just write it.
    Write it twice: note the similarity.
    Write it three times: NOW extract.

  Premature deduplication: coupling things that should stay separate.

THE OPPOSITE OF DRY:

  WET = "Write Everything Twice" / "We Enjoy Typing"

  WET system characteristics:
    - Bug found in 1 place: must search for copies in 5 other places.
    - Discount rate changed: grep for "0.10" and hope you found them all.
    - Copy-paste developer: "I'll just copy this and change one line."
    - Tests break after "simple" change: hidden assumptions in multiple places.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT DRY (WET codebase):

- Business rule change: grep codebase, hope you found all copies, change each, miss one in production
- Bug found: fixed in one place but exists in 4 copies — other 3 still in production

WITH DRY:
→ Business rule in one place: change once, applies everywhere
→ Bug fixed once: no copies to hunt
→ Knowledge has a clear owner: "where is the premium discount rule?" — one answer

---

### 🧠 Mental Model / Analogy

> A master clock vs. 100 clocks set individually. DRY: one master clock (atomic reference). All clocks sync to it. Daylight saving time: master clock changes, all 100 update automatically. WET: 100 independently set clocks. Daylight saving time: manually update all 100. Miss three: three clocks now wrong. The KNOWLEDGE of "what time it is" lives in one master source.

"Master clock" = single authoritative source of a business rule
"All clocks sync to it" = all code references the same definition
"100 independently set clocks" = business rule duplicated in 100 places
"Miss three on DST" = update rule in 97 places, 3 still have old version

---

### ⚙️ How It Works (Mechanism)

```
DRY EXTRACTION PATTERN:

  BEFORE (rule in 3 places):
    OrderService.java:      if (amount > 1000) applyFraudCheck();
    PaymentService.java:    if (payment.amount > 1000.0) flagForReview();
    BatchAuditJob.java:     if (transaction.getAmount().compareTo(1000) > 0) addToAudit();

  IDENTIFY: Same business rule — "amounts over $1000 trigger fraud/audit."

  EXTRACT:
    class FraudThreshold {
        private static final Money THRESHOLD = Money.of(1000, USD);
        static boolean exceeds(Money amount) { return amount.isGreaterThan(THRESHOLD); }
    }

  AFTER (rule in 1 place):
    OrderService:   if (FraudThreshold.exceeds(order.total())) applyFraudCheck();
    PaymentService: if (FraudThreshold.exceeds(payment.amount())) flagForReview();
    BatchAuditJob:  if (FraudThreshold.exceeds(txn.amount())) addToAudit();

  Rule change ($1000 → $2000): change FraudThreshold.THRESHOLD. Done.
```

---

### 🔄 How It Connects (Mini-Map)

```
Duplicate Business Rule (knowledge scattered across codebase)
        │
        ▼ (extract to single representation)
DRY Principle ◄──── (you are here)
(single authoritative representation of each piece of knowledge)
        │
        ├── SOLID SRP: when one class changes for two reasons, that's a DRY violation
        ├── Specification Pattern: captures a business rule once as a reusable spec
        ├── Refactoring: extracting duplicated knowledge is a refactoring operation
        └── YAGNI: tension — don't abstract prematurely (DRY vs. YAGNI)
```

---

### 💻 Code Example

```java
// DRY VIOLATION — same validation logic in 3 places:
class OrderController {
    void create(OrderRequest req) {
        if (req.quantity() <= 0 || req.quantity() > 100)
            throw new ValidationException("Quantity must be 1-100");
    }
}

class OrderImportService {
    void importOrders(List<OrderRequest> orders) {
        orders.forEach(req -> {
            if (req.quantity() <= 0 || req.quantity() > 100)
                throw new ValidationException("Quantity must be 1-100");
        });
    }
}

class OrderReactivationService {
    void reactivate(OrderRequest req) {
        if (req.quantity() <= 0 || req.quantity() > 100)
            throw new ValidationException("Quantity must be 1-100");
    }
}
// Business changes max quantity to 500: find and update ALL 3.

// ────────────────────────────────────────────────────────────────────

// DRY FIX — single representation of "valid order quantity":
public record Quantity(int value) {
    public Quantity {  // Compact constructor validates:
        if (value <= 0 || value > 100)
            throw new InvalidQuantityException("Quantity must be 1-100, got: " + value);
    }
}

// All three classes use Quantity — validation happens ONCE at construction:
class OrderController {
    void create(OrderRequest req) {
        Quantity qty = new Quantity(req.quantity()); // Validates here. No copy.
    }
}
// Change max to 500: only Quantity record changes. All three callers updated automatically.
```

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DRY means "no duplicate code"               | DRY means "no duplicate KNOWLEDGE." Duplicate code is a symptom; duplicate knowledge is the disease. Two similar-looking code blocks that represent different business rules should NOT be extracted just because they look similar — that would couple different knowledge. Test: "do these change for the same reason?" If yes: extract. If no: leave separate |
| DRY means extract every common 3-line block | Over-DRY creates accidental coupling. The "Rule of Three" prevents premature extraction: write it once (fine), write it twice (note similarity), write it three times (extract). Extracting after only seeing two occurrences: might couple unrelated things based on accidental similarity                                                                      |
| DRY only applies to code                    | DRY applies to: database schema (constraints vs. code validation), documentation (comments vs. code), configuration (hardcoded values vs. centralized config), and even tests (test setup duplicated across 50 test methods). DRY is a principle about knowledge representation, not just code lines                                                             |

---

### 🔥 Pitfalls in Production

**Over-DRY creating wrong abstraction:**

```java
// OVER-DRY: Extract "similar looking" code that represents DIFFERENT knowledge:
// Customer address update:
void updateCustomerAddress(CustomerId id, Address newAddr) { repo.updateAddress(id, newAddr); }
// Order delivery address update:
void updateOrderDeliveryAddress(OrderId id, Address newAddr) { repo.updateAddress(id, newAddr); }

// Developer sees similar code, "DRYs" it:
void updateAddress(Long entityId, String entityType, Address addr) {
    if ("CUSTOMER".equals(entityType)) customerRepo.updateAddress(entityId, addr);
    else if ("ORDER".equals(entityType))  orderRepo.updateAddress(entityId, addr);
}
// NOW: the "DRY" version has Control Coupling (entityType flag).
// Adding new entity: modify this shared method (OCP violated).
// The original code was similar by coincidence — different tables, different rules, different history.

// BETTER: Keep them separate. The similarity was coincidental, not shared knowledge.
void updateCustomerAddress(CustomerId id, Address addr) { /* customer-specific rules */ }
void updateDeliveryAddress(OrderId id, Address addr) { /* order-specific rules */ }
// Separate methods evolve independently. No accidental coupling.
```

---

### 🔗 Related Keywords

- `YAGNI` — tension with DRY: don't abstract prematurely; YAGNI says don't add what you don't need yet
- `KISS Principle` — DRY extraction should not add complexity; keep the extraction simple
- `Specification Pattern` — one way to apply DRY to business rules (one spec = one rule)
- `Refactoring` — extracting duplicated knowledge is a core refactoring technique
- `Technical Debt` — WET (duplicated knowledge) is technical debt: future change cost

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Every piece of KNOWLEDGE: single,          │
│              │ authoritative representation. Not about   │
│              │ duplicate code — about duplicate meaning.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Same business rule in multiple places;    │
│              │ changing one thing requires updating 3+   │
│              │ files; bug fixed in 1 place, exists in 4  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Code looks similar but represents         │
│              │ different knowledge (coincidental);       │
│              │ Rule of Three: wait for 3rd occurrence    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Master clock: change daylight saving in  │
│              │  one place; all 100 clocks update. No     │
│              │  hunting for copies."                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ YAGNI → KISS Principle →                  │
│              │ Specification Pattern → Refactoring       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two microservices both have validation: "order amount must be between $1 and $10,000." Service A (Order Service) enforces it in Java. Service B (Payment Service) enforces it in its own validation. Is this a DRY violation? Should you extract a shared library with the validation rule? What are the trade-offs of shared library coupling in a microservices context vs. the consistency risk of two independent copies of the rule?

**Q2.** A developer extracts "common" test setup code into a shared `TestFixtures.setupOrder()` method used by 50 tests. Two months later, a new feature requires changing some tests to use a slightly different order setup, but they can't easily change `TestFixtures.setupOrder()` without breaking 48 other tests. Is this a good application of DRY? What principle — often cited as a counterargument to DRY in tests — suggests test code should tolerate more duplication than production code? Explain why.
