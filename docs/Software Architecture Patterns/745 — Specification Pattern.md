---
layout: default
title: "Specification Pattern"
parent: "Software Architecture Patterns"
nav_order: 745
permalink: /software-architecture/specification-pattern/
number: "745"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Domain Model, Value Objects, Repository Pattern"
used_by: "DDD, Spring Data Specifications, Query building, Validation"
tags: #advanced, #architecture, #ddd, #patterns, #query
---

# 745 — Specification Pattern

`#advanced` `#architecture` `#ddd` `#patterns` `#query`

⚡ TL;DR — The **Specification Pattern** encapsulates a business rule as a reusable, composable object that can be used for validation, filtering, and querying — decoupling business rules from the code that applies them.

| #745            | Category: Software Architecture Patterns                    | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Domain Model, Value Objects, Repository Pattern             |                 |
| **Used by:**    | DDD, Spring Data Specifications, Query building, Validation |                 |

---

### 📘 Textbook Definition

The **Specification Pattern** (Eric Evans, "Domain-Driven Design"; Martin Fowler & Eric Evans, "Specifications") models a business rule as a predicate — an object that answers "does this candidate satisfy this criterion?" A specification: (1) **Encapsulates a rule**: `PremiumCustomerSpecification.isSatisfiedBy(customer)` returns `true` if customer is premium. (2) **Composable**: specifications combine using `and()`, `or()`, `not()` — building complex rules from simple ones without if/else chains. (3) **Reusable across contexts**: the same `ActiveOrderSpecification` used in validation, filtering, and querying. (4) **Names the rule**: `EligibleForDiscountSpecification` is self-documenting in a way that anonymous lambda predicates are not. The classic use cases: (A) Validation — "does this object satisfy this business rule?" (B) In-memory filtering — filter a collection by specification. (C) Query generation — translate specification into a database query (SQL/JPA Criteria).

---

### 🟢 Simple Definition (Easy)

A job posting requirements checklist vs. an interviewer who memorizes requirements. Without specification: each interviewer must remember all job requirements and apply them manually — duplicate logic, inconsistent application. With specification: the requirements are captured in a `JobRequirementsSpec` object. Any interviewer (service, batch job, API) uses the same spec to check any candidate. Change the requirements: change the spec object once. Everyone automatically uses the updated requirements.

---

### 🔵 Simple Definition (Elaborated)

Business rule: "A customer is eligible for premium discount if: (1) they are a premium member AND (2) they have placed at least 5 orders in the last 12 months AND (3) they are not in arrears." Without specification: this triple condition duplicated in `OrderService.applyDiscount()`, `ReportingService.identifyPremiumUsers()`, and `BatchJob.sendDiscountEmails()`. With specification: `PremiumDiscountEligibilitySpec` encapsulates all three conditions. All three callers use the same spec. Change the threshold from 5 to 10 orders: one change. Test the rule in isolation: just test the spec with mocked customers.

---

### 🔩 First Principles Explanation

**Specification interfaces, composition, and repository integration:**

```
BASIC SPECIFICATION INTERFACE:

  // Generic specification interface:
  interface Specification<T> {
      boolean isSatisfiedBy(T candidate);

      // Composition operators:
      default Specification<T> and(Specification<T> other) {
          return candidate -> this.isSatisfiedBy(candidate) && other.isSatisfiedBy(candidate);
      }

      default Specification<T> or(Specification<T> other) {
          return candidate -> this.isSatisfiedBy(candidate) || other.isSatisfiedBy(candidate);
      }

      default Specification<T> not() {
          return candidate -> !this.isSatisfiedBy(candidate);
      }
  }

CONCRETE SPECIFICATIONS:

  class PremiumCustomerSpec implements Specification<Customer> {
      @Override
      public boolean isSatisfiedBy(Customer customer) {
          return customer.membershipType() == MembershipType.PREMIUM;
      }
  }

  class MinimumOrderCountSpec implements Specification<Customer> {
      private final int minimumOrders;
      private final Period period;
      private final OrderRepository orderRepo;

      MinimumOrderCountSpec(int minimumOrders, Period period, OrderRepository orderRepo) {
          this.minimumOrders = minimumOrders;
          this.period = period;
          this.orderRepo = orderRepo;
      }

      @Override
      public boolean isSatisfiedBy(Customer customer) {
          LocalDate since = LocalDate.now().minus(period);
          long orderCount = orderRepo.countByCustomerSince(customer.id(), since);
          return orderCount >= minimumOrders;
      }
  }

  class NotInArrearsSpec implements Specification<Customer> {
      @Override
      public boolean isSatisfiedBy(Customer customer) {
          return customer.balance().isGreaterThanOrEqual(Money.zero(USD));
      }
  }

COMPOSITION — BUILDING COMPLEX RULES FROM SIMPLE SPECS:

  // Each spec is simple. Composition creates the complex rule:
  Specification<Customer> premiumDiscountEligible =
      new PremiumCustomerSpec()
          .and(new MinimumOrderCountSpec(5, Period.ofYears(1), orderRepo))
          .and(new NotInArrearsSpec());

  // Usage in service:
  customers.stream()
           .filter(premiumDiscountEligible::isSatisfiedBy)
           .forEach(discountService::applyPremiumDiscount);

  // Usage in validation:
  if (!premiumDiscountEligible.isSatisfiedBy(customer)) {
      throw new NotEligibleForDiscountException(customer.id());
  }

  // Same spec: validation, filtering, batch processing — one definition.

USE CASE 1: VALIDATION (is this object valid for this operation?):

  class OrderFulfillmentSpec implements Specification<Order> {
      boolean isSatisfiedBy(Order order) {
          return order.status() == OrderStatus.CONFIRMED
              && order.items().stream().allMatch(item -> item.inventoryStatus() == IN_STOCK)
              && order.shippingAddress() != null;
      }
  }

  // Validation:
  OrderFulfillmentSpec spec = new OrderFulfillmentSpec();
  if (!spec.isSatisfiedBy(order)) throw new OrderNotFulfillableException(order.id());

USE CASE 2: IN-MEMORY FILTERING (filter a collection):

  List<Product> eligibleForPromotion = products.stream()
      .filter(new ActiveProductSpec()
              .and(new StockAboveThresholdSpec(10))
              .and(new NoActiveDiscountSpec())::isSatisfiedBy)
      .toList();

USE CASE 3: QUERY GENERATION (Spring Data JPA Specifications):

  // Spring Data Specification interface integrates with JPA Criteria API:
  interface Specification<T> {
      Predicate toPredicate(Root<T> root, CriteriaQuery<?> query, CriteriaBuilder builder);
  }

  class PremiumCustomerSpecification implements Specification<CustomerJpaEntity> {
      @Override
      public Predicate toPredicate(Root<CustomerJpaEntity> root,
                                   CriteriaQuery<?> query,
                                   CriteriaBuilder cb) {
          return cb.equal(root.get("membershipType"), "PREMIUM");
      }
  }

  class MinOrderCountSpecification implements Specification<CustomerJpaEntity> {
      private final int minOrders;
      MinOrderCountSpecification(int minOrders) { this.minOrders = minOrders; }

      @Override
      public Predicate toPredicate(Root<CustomerJpaEntity> root,
                                   CriteriaQuery<?> query,
                                   CriteriaBuilder cb) {
          // Subquery: count orders per customer:
          Subquery<Long> subquery = query.subquery(Long.class);
          Root<OrderJpaEntity> orderRoot = subquery.from(OrderJpaEntity.class);
          subquery.select(cb.count(orderRoot))
                  .where(cb.equal(orderRoot.get("customerId"), root.get("id")));
          return cb.greaterThanOrEqualTo(subquery, (long) minOrders);
      }
  }

  // Spring Data: combine and query:
  Specification<CustomerJpaEntity> spec =
      new PremiumCustomerSpecification()
          .and(new MinOrderCountSpecification(5));

  List<CustomerJpaEntity> results = customerJpaRepo.findAll(spec);
  // Spring Data generates: SELECT * FROM customers WHERE membership_type = 'PREMIUM'
  //   AND (SELECT COUNT(*) FROM orders WHERE customer_id = customers.id) >= 5

  // Repository method signature:
  interface CustomerJpaRepo extends JpaRepository<CustomerJpaEntity, Long>,
                                     JpaSpecificationExecutor<CustomerJpaEntity> {}

SPECIFICATION AS A NAMED DOMAIN CONCEPT:

  Instead of scattered predicates:
    customers.stream().filter(c -> c.membership() == PREMIUM
        && c.orderCount() >= 5
        && !c.isInArrears())     // Anonymous predicate — no name.

  Named specification:
    PremiumDiscountEligibilitySpecification eligibility = new PremiumDiscountEligibilitySpecification();
    customers.stream().filter(eligibility::isSatisfiedBy)  // Named! Self-documenting.

  // Name captures INTENT: "eligible for premium discount" is meaningful.
  // The logic might change; the name stays the same.
  // Domain experts can review: "Show me PremiumDiscountEligibilitySpecification" — readable.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Specification:

- Business rule "eligible for premium discount" scattered: validation in service, filter in reporting, query in batch job — three copies of the same conditional logic
- Rule changes: update 3+ places; easily miss one

WITH Specification:
→ One place: `PremiumDiscountEligibilitySpec` — the single source of truth
→ Composable: complex rules built from simple specs, no deep nesting
→ Testable in isolation: just test `spec.isSatisfiedBy(customer)` with mocked data

---

### 🧠 Mental Model / Analogy

> A Lego brick set vs. a hardcoded sculpture. Without specifications: business rules embedded in code — like a sculpture that's permanently fixed. Change the rule: chip away and rebuild part of the sculpture. With specifications: Lego bricks — each brick is one rule. Snap them together for complex rules. Disassemble and reassemble easily. `and()`, `or()`, `not()`: the connectors. The same brick reused in different structures.

"Lego bricks (individual rules)" = simple specification objects
"Snap together for complex rules" = .and(), .or(), .not() composition
"Reuse same brick in different structures" = same spec in validation, filtering, querying
"Hardcoded sculpture" = complex if/else chains embedded in service methods

---

### ⚙️ How It Works (Mechanism)

```
SPECIFICATION EVALUATION FLOW:

  PremiumDiscountEligibilitySpec
  = PremiumCustomerSpec.and(MinOrderCountSpec(5, 1 year)).and(NotInArrearsSpec)

  spec.isSatisfiedBy(customer):
      ├─ PremiumCustomerSpec.isSatisfiedBy(customer)?   → customer.membership == PREMIUM
      │   TRUE →
      ├─ MinOrderCountSpec.isSatisfiedBy(customer)?     → orderRepo.countByCustomerSince(...) >= 5
      │   TRUE →
      └─ NotInArrearsSpec.isSatisfiedBy(customer)?      → customer.balance >= 0
          TRUE → isSatisfiedBy: TRUE (eligible)
          FALSE → isSatisfiedBy: FALSE (not eligible — in arrears)
```

---

### 🔄 How It Connects (Mini-Map)

```
Business Rule (validation, filtering, querying logic)
        │
        ▼ (encapsulated as reusable object)
Specification Pattern ◄──── (you are here)
(isSatisfiedBy(); composable via and/or/not; reusable across contexts)
        │
        ├── Domain Model: specs express domain rules using domain language
        ├── Repository Pattern: specs translate to queries (Spring Data Specs)
        ├── Value Objects: specs often test against value objects (Money, Status)
        └── Strategy Pattern: specs are a form of strategy (pluggable predicate)
```

---

### 💻 Code Example

```java
// Composable specifications for product eligibility:
interface Specification<T> {
    boolean isSatisfiedBy(T candidate);

    default Specification<T> and(Specification<T> other) {
        return candidate -> this.isSatisfiedBy(candidate) && other.isSatisfiedBy(candidate);
    }
    default Specification<T> or(Specification<T> other) {
        return candidate -> this.isSatisfiedBy(candidate) || other.isSatisfiedBy(candidate);
    }
    default Specification<T> not() {
        return candidate -> !this.isSatisfiedBy(candidate);
    }
}

// Simple, focused specifications:
class ActiveProductSpec implements Specification<Product> {
    public boolean isSatisfiedBy(Product p) { return p.status() == ProductStatus.ACTIVE; }
}

class SufficientStockSpec implements Specification<Product> {
    private final int minimumStock;
    SufficientStockSpec(int min) { this.minimumStock = min; }
    public boolean isSatisfiedBy(Product p) { return p.stockLevel() >= minimumStock; }
}

class NotDiscontinuedSpec implements Specification<Product> {
    public boolean isSatisfiedBy(Product p) { return p.discontinuedAt() == null; }
}

// Usage: compose for complex rule — named, reusable, testable:
Specification<Product> shippableProduct =
    new ActiveProductSpec()
        .and(new SufficientStockSpec(1))
        .and(new NotDiscontinuedSpec());

// Validation:
cart.items().forEach(item -> {
    if (!shippableProduct.isSatisfiedBy(item.product()))
        throw new ProductNotShippableException(item.product().id());
});

// Filtering:
List<Product> readyToShip = products.stream()
    .filter(shippableProduct::isSatisfiedBy).toList();
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Specification Pattern is just a fancy Predicate             | Specification adds: (1) a domain-meaningful name that captures business intent (`EligibleForCreditSpec` vs. anonymous lambda), (2) composability with named `and()`, `or()`, `not()`, (3) ability to translate to queries (Spring Data), and (4) reusability across validation, filtering, and querying contexts. Java `Predicate<T>` does composition but without business meaning or query translation |
| Specifications always need to query the database            | No. Simple specifications are pure: `PremiumCustomerSpec` checks a field on the object — no DB query. Complex specifications might need data: `MinOrderCountSpec` queries the order count. Design them for the appropriate source: in-memory check vs. DB query. For DB-level filtering: Spring Data `JpaSpecificationExecutor` translates to SQL                                                        |
| Specification Pattern replaces the Repository query methods | Complementary. Simple queries: named repository methods (`findByStatus(status)`) are cleaner. Dynamic queries with multiple optional criteria: Specification is better (`findAll(spec)`). Don't replace all repository methods with Specifications — only where the combination of criteria needs to be dynamic or the rule is complex enough to deserve a name                                          |

---

### 🔥 Pitfalls in Production

**Specification checks object but doesn't reflect actual database state:**

```java
// BAD: In-memory spec passes, but DB query would fail (stale data):
class SufficientInventorySpec implements Specification<Product> {
    boolean isSatisfiedBy(Product product) {
        return product.stockLevel() > 0;  // Checks in-memory loaded object.
    }
}

// Issue: Product loaded 5 minutes ago. Stock was 1. Meanwhile: another user purchased.
// In-memory: stockLevel = 1 → spec passes → place order → DB update fails (stock = 0).
// The spec gave false guarantee: checked object state, not actual current state.

// FIX for critical checks: spec should reflect real-time data, or check at DB level:
class SufficientInventorySpec implements Specification<Product> {
    private final InventoryRepository inventoryRepo;

    boolean isSatisfiedBy(Product product) {
        // Query current state from DB (not from loaded object):
        return inventoryRepo.getAvailableStock(product.id()) > 0;
    }
}

// OR: Use optimistic locking + check at reservation time (DB-level constraint).
// Spec as pre-check; DB constraint as the enforcement guarantee.
```

---

### 🔗 Related Keywords

- `Domain Model` — specifications express domain business rules using domain language
- `Repository Pattern` — specifications translate to DB queries (Spring Data JPA Specifications)
- `Value Objects` — specifications often evaluate value object attributes
- `Strategy Pattern` — specifications are a form of pluggable strategy (predicate as strategy)
- `CQRS Pattern` — specifications useful on the query side for dynamic filtering

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Business rule as composable, reusable     │
│              │ object: isSatisfiedBy(candidate).         │
│              │ One definition: validation, filter, query │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Same rule used in multiple places;        │
│              │ complex conditional logic needs naming;   │
│              │ dynamic queries with optional criteria    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple, single-use predicates (just use   │
│              │ lambda); pure DB queries better as        │
│              │ named repository methods                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Lego bricks for business rules:          │
│              │  snap together, reuse anywhere, and       │
│              │  change one brick to change the logic."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain Model → Repository Pattern →       │
│              │ Value Objects → Strategy Pattern          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `ShippableOrderSpec` checks: order is CONFIRMED, all items are in stock, delivery address is valid, and no fraud flag. You use this spec in three places: the `FulfillOrderService.fulfill()` validation, the `ShippingBatchJob.findOrdersToShip()` filter, and the `FulfillmentDashboard.getShippableCount()` query. The batch job and dashboard query millions of orders — loading them all into memory to run the in-memory spec is not feasible. How does this performance constraint affect spec design? What two different implementations of `ShippableOrderSpec` might you create, and how do you ensure they stay consistent?

**Q2.** You have `PremiumEligibilitySpec` (is customer premium?), `MinPurchaseSpec` (has minimum purchase history?), and `ActiveStatusSpec` (is account active?). A new business rule: "A customer is eligible for the annual bonus if they meet premium eligibility AND have an active status, OR if they've been a customer for more than 10 years." Write the specification composition using `and()`, `or()`, `not()`. Then consider: what if the rule changes monthly based on marketing campaigns? Should the rule composition be hardcoded in the specification objects, or should it be configurable? Design a solution.
