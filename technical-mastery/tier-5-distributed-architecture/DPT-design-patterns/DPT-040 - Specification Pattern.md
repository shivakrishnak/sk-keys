---
id: DPT-040
title: Specification Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-027, DPT-039
used_by: DPT-064
related: DPT-027, DPT-039, DPT-079, DPT-074
tags:
  - pattern
  - domain-driven-design
  - advanced
  - business-rules
  - predicate
  - query-object
  - composable
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/design-patterns/specification/
---

⚡ TL;DR - Specification Pattern encapsulates a business
rule as a reusable, composable object with a single
`isSatisfiedBy(candidate)` method, allowing complex
filtering and validation logic to be named, combined
with AND/OR/NOT, and reused across the application
without scattering conditionals.

| #40 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-027, DPT-039 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-027, DPT-039, DPT-079, DPT-074 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce platform filters orders for different purposes.
Business rules are scattered across the codebase:

```java
// In the report service:
orders.stream()
    .filter(o -> o.status() == FULFILLED
        && o.total().compareTo(new BigDecimal("100")) >= 0
        && o.date().isAfter(startOfMonth))
    .collect(toList());

// In the notification service:
for (Order o : orders) {
    if (o.status() == FULFILLED
        && !o.emailSent()
        && o.customer().isOptedIntoEmails()) {
        sendEmail(o);
    }
}

// In the billing service:
if (order.status() == FULFILLED
    && order.total().compareTo(threshold) >= 0
    && !order.isTaxExempt()) {
    calculateTax(order);
}
```

**THE BREAKING POINT:**
Business rule "fulfilled order" (status == FULFILLED) is
duplicated in 3+ places. When the rule changes (add
"and not cancelled within 24 hours"): find and update
all instances. The filter lambda in the stream is
anonymous - no name, no unit test, no reuse.

**THE INVENTION MOMENT:**
Specification Pattern: encapsulate each business rule
as a named class. Compose complex rules using AND/OR/NOT
combinators. Use the same named specification everywhere.

```java
var fulfilled = new FulfilledOrderSpec();
var highValue  = new HighValueOrderSpec(new BigDecimal("100"));
var recentOrder = new RecentOrderSpec(startOfMonth);

var reportSpec = fulfilled.and(highValue).and(recentOrder);

orders.stream()
    .filter(reportSpec::isSatisfiedBy)
    .collect(toList());
```

Changing "fulfilled": update one class. Test each
specification independently. Compose specifications
to create new filtering logic.

**EVOLUTION:**
Spring Data JPA's `Specification<T>` (with `JpaSpecificationExecutor`)
directly implements this pattern for database queries.
`Criteria API` in JPA. Spring Batch `ItemReader` specifications.
Domain-Driven Design: Specifications are first-class
domain objects that encapsulate domain rules.

---

### 📘 Textbook Definition

The **Specification Pattern** is a Domain-Driven Design
pattern that encapsulates a business rule as a predicate
object with an `isSatisfiedBy(entity)` method. Each
specification represents one coherent business rule.
Specifications are combinable: a base `Specification`
interface provides `and()`, `or()`, `not()` methods
that return composite specifications. Complex rules
are built by composing simpler specifications. The
pattern, introduced by Eric Evans and Martin Fowler,
keeps domain logic in the domain layer (named, testable
specifications) rather than scattered in service methods,
query lambdas, or SQL strings.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Specification Pattern wraps a business rule (a condition)
in a named, reusable, composable object.

**One analogy:**
> A job posting has requirements. Each requirement is a
> Specification: `HasJavaDegree`, `Has5YearsExperience`,
> `LivesInCalifornia`. The job combines them:
> `HasJavaDegree.and(Has5YearsExperience).and(LivesInCalifornia)`.
> A candidate (entity) is checked: `spec.isSatisfiedBy(candidate)`.
> Adding "requires AWS certification": create `HasAWSCert`,
> add to composition. No changes to other rules.

**One insight:**
Specification Pattern makes business rules first-class
objects. Named, testable, composable. Contrast with
anonymous lambdas in streams: `filter(o -> o.status() == FULFILLED)`.
An anonymous lambda has no name, no test, no reuse.
`new FulfilledOrderSpec()` has a name, is testable in
isolation, and is reusable everywhere the rule applies.

---

### 🔩 First Principles Explanation

**CORE INTERFACE:**
```java
interface Specification<T> {
    boolean isSatisfiedBy(T candidate);

    default Specification<T> and(Specification<T> other) {
        return candidate ->
            this.isSatisfiedBy(candidate)
            && other.isSatisfiedBy(candidate);
    }

    default Specification<T> or(Specification<T> other) {
        return candidate ->
            this.isSatisfiedBy(candidate)
            || other.isSatisfiedBy(candidate);
    }

    default Specification<T> not() {
        return candidate -> !this.isSatisfiedBy(candidate);
    }
}
```

**COMPOSITE SPECIFICATIONS:**
- `and()`: logical AND of two specifications.
- `or()`: logical OR.
- `not()`: negation.
The resulting composite is itself a `Specification` -
infinitely composable.

**THREE USE CASES (Evans & Fowler):**
1. **Validation**: check if a domain object meets a rule.
2. **Selection (filtering)**: select objects satisfying a rule from a collection.
3. **Construction**: generate objects that satisfy a rule.

**SPRING DATA JPA SPECIFICATION:**
```java
// Spring Data JPA: translate Specification to SQL Predicate
interface OrderRepository extends JpaRepository<Order, Long>,
    JpaSpecificationExecutor<Order> {}

class OrderSpecs {
    static Specification<Order> isFulfilled() {
        return (root, query, cb) ->
            cb.equal(root.get("status"), OrderStatus.FULFILLED);
    }
    static Specification<Order> hasMinTotal(BigDecimal min) {
        return (root, query, cb) ->
            cb.greaterThanOrEqualTo(root.get("total"), min);
    }
}

// Query: SELECT * FROM orders WHERE status='FULFILLED' AND total >=
// 100
List<Order> result = repo.findAll(
    isFulfilled().and(hasMinTotal(new BigDecimal("100"))));
```

**TRADE-OFFS:**

**Gain:** Named, reusable, testable business rules.
Composable: complex rules from simple parts.
Avoids rule duplication across services and repositories.
Domain language expressed in code (specification names
= ubiquitous language).

**Cost:** Over-engineering for simple, one-time filtering.
If the rule is used only once and is not domain-significant:
a simple lambda is cleaner. JPA Specification: complex
specifications with joins can become verbose and hard
to read compared to JPQL.

---

### 🧪 Thought Experiment

**SETUP:**
Premium membership check: customer must have registered
>6 months ago AND has placed >10 orders AND has not
had a payment failure in the last 30 days.

**WITHOUT SPECIFICATION:**
Three conditions inline everywhere "premium" is checked:
`customer.registeredAt.isBefore(now.minusMonths(6))
&& customer.orderCount > 10 && !customer.hasRecentPaymentFailure()`.
Five places use this check. The rule changes (>3 months):
update all five places.

**WITH SPECIFICATION:**
```java
var premium = new OldEnoughSpec(6)
    .and(new FrequentCustomerSpec(10))
    .and(new NoRecentPaymentFailureSpec(30).not());

// All five places:
if (premium.isSatisfiedBy(customer)) { ... }
// Rule change: update OldEnoughSpec. Five places: UNCHANGED.
```

---

### 🧠 Mental Model / Analogy

> Specification Pattern is a set of LEGO BRICKS each
> representing one rule. Individual bricks:
> "status = FULFILLED", "total >= 100", "date is recent."
> Snap them together: and(), or(), not() are the connectors.
> Complex query = assembled structure of bricks.
> Each brick is named, reusable, and independently testable.
> Adding a new rule: new brick. Existing structure: unchanged.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Specification Pattern is a way to name your filter
conditions. Instead of writing `o.status == FULFILLED`
as an anonymous condition everywhere, you create a class
called `FulfilledOrderSpec` that contains that check.
You can then combine these named rules: "this AND that
AND NOT theOther."

**Level 2 - How to use it (junior developer):**
Create an interface `Specification<T>` with `isSatisfiedBy(T t)`.
Add `and()`, `or()`, `not()` default methods. Create one
class per business rule implementing `Specification<T>`.
Compose specifications using the combinator methods.
Use in `stream.filter(spec::isSatisfiedBy)` or in Spring
Data queries.

**Level 3 - How it works (mid-level engineer):**
Spring Data JPA's `Specification<T>` extends this concept
to JPA queries: the `isSatisfiedBy()` equivalent is
`toPredicate(Root<T>, CriteriaQuery<?>, CriteriaBuilder)`.
This translates the specification into a JPA `Predicate`
which becomes SQL. `JpaSpecificationExecutor.findAll(spec)`
takes a composed specification and generates the appropriate
SQL WHERE clause. The power: the same specification
class can be used for both in-memory filtering (in tests,
with domain objects) and SQL generation (in production,
with JPA). The specification is not aware of whether
it is being applied to objects or being translated to SQL.

**Level 4 - Why it was designed this way (senior/staff):**
Specification Pattern is a Domain-Driven Design tactical
pattern from Evans' "Domain-Driven Design" (2003). The
core DDD principle it addresses: domain logic should
live in the domain layer, not leaked into services,
repositories, or query string builders. A specification
is a domain object that expresses domain rules in domain
language. `new EligibleForPremiumUpgrade()` is more
domain-expressive than `customer.joinedAt.before(now.minusMonths(6))
&& customer.orders.size() > 10`. The specification
name IS the ubiquitous language. Domain experts can
review specification names and verify they match business
understanding. Anonymous lambdas cannot be verified
by domain experts.

**Level 5 - Mastery (distinguished engineer):**
Specification Pattern is the foundation for type-safe,
composable query builders - a middle ground between
JPQL strings (not type-safe) and Criteria API (verbose).
Libraries like QueryDSL and jOOQ implement Specification-style
composable predicates: `QOrder.order.status.eq(FULFILLED)
.and(QOrder.order.total.goe(new BigDecimal("100")))`.
This is Specification Pattern with type safety (generated
Q-classes from entity schema). At the architectural
level: Specification Pattern in a CQRS architecture
defines the query side's predicate objects. The query
side accepts Specification objects (not raw SQL parameters)
and translates them to queries. Specification objects
are domain objects that cross the CQRS boundary - they
live in a shared kernel between command and query sides.
This enables the query side to change its storage technology
(from SQL to Elasticsearch) without changing the Specification
API.

---

### ⚙️ How It Works (Mechanism)

```
Specification Composition
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ Simple specs:                                           │
│   FulfilledSpec:  o.status == FULFILLED                 │
│   HighValueSpec:  o.total >= 100                        │
│   RecentSpec:     o.date >= startOfMonth                │
│                                                         │
│ Composition (and()):                                    │
│   reportSpec = FulfilledSpec                            │
│               .and(HighValueSpec)                       │
│               .and(RecentSpec)                          │
│                                                         │
│ isSatisfiedBy(order):                                   │
│   → FulfilledSpec.isSatisfiedBy(order)  = true          │
│   → HighValueSpec.isSatisfiedBy(order)  = true          │
│   → RecentSpec.isSatisfiedBy(order)     = false         │
│   → overall: false (AND short-circuits)                 │
│                                                         │
│ or() and not() follow the same composable pattern       │
│                                                         │
│ Spring Data JPA: same composition creates SQL:          │
│   WHERE status='FULFILLED' AND total>=100 AND date>=?   │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Premium order report generation:

Business rule: fulfilled, high-value, recent orders

Domain specifications:
  Specification<Order> fulfilled = new
    FulfilledOrderSpec();
  Specification<Order> highValue  = new
    HighValueOrderSpec(100.00);
  Specification<Order> recent     = new
    RecentOrderSpec(30); // days

Composed:
  Specification<Order> premiumOrders =
      fulfilled.and(highValue).and(recent);

Service layer:
  List<Order> reportOrders =
    orderRepository.findAll(premiumOrders);
  // Spring Data JPA translates to:
  // SELECT * FROM orders
  // WHERE status='FULFILLED'
  //   AND total >= 100.0
  //   AND date >= (now - 30 days)

In-memory test (no DB needed):
  boolean isReport =
    premiumOrders.isSatisfiedBy(testOrder);
  // Tests specification logic without database
```

---

### 💻 Code Example

**Example 1 - Anonymous lambdas scattered (anti-pattern):**

```java
// BAD: business rule scattered as anonymous lambdas
// "fulfilled + high value" rule duplicated in 3 places

// ReportService:
orders.stream()
    .filter(o -> o.status() == FULFILLED
        && o.total().compareTo(new BigDecimal("100")) >= 0)
    .forEach(reportWriter::write);

// BillingService:
orders.stream()
    .filter(o -> o.status() == FULFILLED
        && o.total().compareTo(new BigDecimal("100")) >= 0)
    .forEach(invoiceService::generateInvoice);

// AuditService:
for (Order o : orders) {
    if (o.status() == FULFILLED
        && o.total().compareTo(new BigDecimal("100")) >= 0) {
        auditLog.record(o);
    }
}
// Rule changes: find and fix 3 places (and any forgotten ones)
```

**Example 2 - Specification Pattern:**

```java
// GOOD: named, composable, reusable specifications

// Core interface with default combinators
interface Specification<T> {
    boolean isSatisfiedBy(T candidate);

    default Specification<T> and(Specification<T> other) {
        return candidate ->
            this.isSatisfiedBy(candidate)
            && other.isSatisfiedBy(candidate);
    }

    default Specification<T> or(Specification<T> other) {
        return candidate ->
            this.isSatisfiedBy(candidate)
            || other.isSatisfiedBy(candidate);
    }

    default Specification<T> not() {
        return candidate -> !this.isSatisfiedBy(candidate);
    }
}

// Named specification classes (domain objects)
class FulfilledOrderSpec implements Specification<Order> {
    @Override
    public boolean isSatisfiedBy(Order order) {
        return order.status() == OrderStatus.FULFILLED;
    }
}

class HighValueOrderSpec implements Specification<Order> {
    private final BigDecimal threshold;

    HighValueOrderSpec(BigDecimal threshold) {
        this.threshold = threshold;
    }

    @Override
    public boolean isSatisfiedBy(Order order) {
        return order.total().compareTo(threshold) >= 0;
    }
}

// USAGE: compose named specifications
Specification<Order> premiumOrderSpec =
    new FulfilledOrderSpec()
        .and(new HighValueOrderSpec(new BigDecimal("100")));

// All services use the SAME specification:
orders.stream()
    .filter(premiumOrderSpec::isSatisfiedBy)
    .forEach(reportWriter::write);

orders.stream()
    .filter(premiumOrderSpec::isSatisfiedBy)
    .forEach(invoiceService::generateInvoice);

// Rule changes (threshold to 150): update HighValueOrderSpec only
```

**Example 3 - Spring Data JPA Specification:**

```java
// JPA Specification: same composable pattern for database queries

import org.springframework.data.jpa.domain.Specification;

public class OrderSpecs {

    public static Specification<Order> isFulfilled() {
        return (root, query, cb) ->
            cb.equal(root.get("status"), OrderStatus.FULFILLED);
    }

    public static Specification<Order> hasMinTotal(BigDecimal min) {
        return (root, query, cb) ->
            cb.greaterThanOrEqualTo(root.get("total"), min);
    }

    public static Specification<Order> placedAfter(LocalDate date) {
        return (root, query, cb) ->
            cb.greaterThanOrEqualTo(root.get("orderDate"), date);
    }
}

// Repository: extend JpaSpecificationExecutor
interface OrderRepository
    extends JpaRepository<Order, Long>,
            JpaSpecificationExecutor<Order> {}

// Service: compose and query
@Service
class OrderReportService {
    @Autowired OrderRepository repo;

    List<Order> getPremiumOrders(LocalDate since) {
        Specification<Order> spec = isFulfilled()
            .and(hasMinTotal(new BigDecimal("100")))
            .and(placedAfter(since));
        return repo.findAll(spec);
        // SQL: WHERE status='FULFILLED' AND total>=100 AND
        // order_date>=?
    }
}
```

**Example 4 - Unit testing specifications independently:**

```java
// Specifications are independently unit-testable (no DB needed)
class FulfilledOrderSpecTest {

    @Test
    void fulfilledOrder_satisfiesSpec() {
        FulfilledOrderSpec spec = new FulfilledOrderSpec();
        Order fulfilledOrder = Order.builder()
            .status(OrderStatus.FULFILLED)
            .build();

        assertTrue(spec.isSatisfiedBy(fulfilledOrder));
    }

    @Test
    void pendingOrder_doesNotSatisfySpec() {
        FulfilledOrderSpec spec = new FulfilledOrderSpec();
        Order pendingOrder = Order.builder()
            .status(OrderStatus.PENDING)
            .build();

        assertFalse(spec.isSatisfiedBy(pendingOrder));
    }
}

// Test composed specification
class PremiumOrderSpecTest {
    @Test
    void composedSpec_requiresAllConditions() {
        Specification<Order> premiumSpec =
            new FulfilledOrderSpec()
                .and(new HighValueOrderSpec(new BigDecimal("100")));

        Order highValueFulfilled = Order.builder()
            .status(OrderStatus.FULFILLED)
            .total(new BigDecimal("200"))
            .build();
        Order lowValueFulfilled = Order.builder()
            .status(OrderStatus.FULFILLED)
            .total(new BigDecimal("50"))
            .build();

        assertTrue(premiumSpec.isSatisfiedBy(highValueFulfilled));
        assertFalse(premiumSpec.isSatisfiedBy(lowValueFulfilled));
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Reusable | Named | Composable | Testable | Verbose |
|---|---|---|---|---|---|
| Inline lambda | No | No | No | No | No |
| Named lambda | Partial | Yes | No | No | No |
| **Specification** | Yes | Yes | Yes | Yes | Medium |
| Spring Data Spec | Yes | Yes | Yes | Yes | High (JPA) |
| QueryDSL | Yes | Partial | Yes | Yes | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Specification Pattern is only for queries | Specification Pattern is for ANY business rule: validation (`spec.isSatisfiedBy(entity)` returns boolean), selection (filtering collections), and construction (find objects satisfying the spec). Queries are one use case |
| It's over-engineering for simple filters | For a one-time, non-domain filter: yes, a lambda is cleaner. For domain rules that appear in multiple places and have business meaning: Specification Pattern prevents rule duplication and makes rules explicit. The test: does this condition have a business name? If yes: Specification |
| Spring Data Specification is the same as the domain Specification | Spring Data's `Specification<T>` interface has a different signature (`toPredicate`). It is designed for JPA query generation. A domain Specification (`isSatisfiedBy`) is for in-memory checking. They serve similar purposes but are different interfaces; ideally, a domain specification maps to a JPA specification for the persistence layer |
| Specifications must be class-based | A lambda or method reference IS a Specification (if the functional interface is `Specification<T>`). The benefit of class-based specs is naming and parameter encapsulation. For simple, one-parameter specs: `Specification<Order> isFulfilled = o -> o.status() == FULFILLED` is valid |

---

### 🚨 Failure Modes & Diagnosis

**JPA Specification with N+1 Issue**

**Symptom:**
`findAll(spec)` generates one query for the main entity
and N additional queries for associations. 1000 orders
= 1001 queries.

**Root Cause:**
A composed specification that accesses a lazy association
triggers N additional queries (N+1 problem).

**Diagnosis:**
Enable SQL logging: `spring.jpa.show-sql=true`.
Count SELECT statements for a single `findAll(spec)` call.

**Fix:**
```java
// Include a JOIN FETCH in the specification's query customization:
Specification<Order> withItems = (root, query, cb) -> {
    if (query.getResultType() == Long.class) {
        // Count query: no fetch join
        return cb.conjunction();
    }
    root.fetch("items", JoinType.LEFT); // Eager fetch for main query
    return cb.conjunction(); // no additional predicate
};

repo.findAll(isFulfilled().and(withItems));
// Single query: SELECT o.*, i.* FROM orders o LEFT JOIN items i
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Strategy` - DPT-027; each Specification is a Strategy
  for "how to evaluate a condition"
- `Dependency Injection` - DPT-039; specifications with
  configurable thresholds use DI for configuration

**Builds On This (learn these next):**
- `Repository Pattern` - DPT-079; Repository Pattern
  uses Specifications as query parameters
- `CQRS Pattern` - DPT-052; the query side of CQRS
  accepts Specifications to define which events/entities
  to return

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Named, composable business rule object: │
│              │ isSatisfiedBy(T), and(), or(), not()    │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Business rule appears in multiple places │
│              │ AND has domain significance (has a name) │
├──────────────┼──────────────────────────────────────────┤
│ SPRING DATA  │ Specification<T> + JpaSpecificationExecut│
│              │ Translates to SQL Predicate automatically│
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ One-time filter with no business meaning │
│              │ Use lambda instead                       │
├──────────────┼──────────────────────────────────────────┤
│ TEST VALUE   │ Each spec independently testable without │
│              │ Compose in tests; validates each rule    │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Anti-Patterns Overview → God Object      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Specification = a named, reusable, composable business
   rule. `isSatisfiedBy(entity)`. Compose with `and()`,
   `or()`, `not()`. Use when the rule appears in multiple
   places or has a domain name. Not needed for one-time
   anonymous filters.
2. Spring Data JPA's `Specification<T>` interface translates
   the same composition to SQL predicates. `isFulfilled().and(hasMinTotal(100))`
   generates `WHERE status='FULFILLED' AND total>=100`.
   Same composition, different execution (in-memory vs SQL).
3. Unit-test each specification independently (no database,
   no Spring context needed). Test composites. This is
   the pattern's testability payoff: named, independently
   testable business rules vs. untestable anonymous lambdas.

