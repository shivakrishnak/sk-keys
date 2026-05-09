---
layout: default
title: "Specification Pattern"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 40
permalink: /design-patterns/specification-pattern/
id: DPT-040
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - deep-dive
  - architecture
  - java
  - bestpractice
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-040 - Specification Pattern

⚡ TL;DR - Specification encapsulates a business rule as a reusable, combinable object so rules can be composed, reused, and tested independently of the objects they govern.

| DPT-040 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Predicate, Domain-Driven Design (DDD) | |
| **Used by:** | Domain-Driven Design, Query Building, Business Rules Engine, Filtering | |
| **Related:** | Strategy, Decorator, Composite, Chain of Responsibility, Predicate | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce `ProductCatalog` needs to filter products by: (1) in-stock, (2) price < $50, (3) rated > 4 stars, (4) free-shipping-eligible. The code has `if (product.inStock() && product.price() < 50 && product.rating() > 4 && product.freeShipping())`. The rule is embedded in the query code. Business analysts can't read it. Testing requires creating products that satisfy every combination. Reusing "in-stock AND price < $50" in another feature means copy-pasting the condition.

**THE BREAKING POINT:**
With 15 business rules and 7 query scenarios, the combinations explode. Rules are duplicated across service methods. Changing "eligible for free shipping" requires hunting all places the rule is encoded. A new rule (membership discount eligibility) must be added to all existing if-chains. The logic is not composable - it's scattered.

**THE INVENTION MOMENT:**
This is exactly why the Specification pattern was created. Each rule is an object: `InStockSpec`, `PriceBelowSpec(50)`, `HighRatedSpec(4)`. They combine: `inStock.and(priceBelowFifty).and(highRated)`. The composed specification is passed to a repository, a filter, or a query builder. Rules are named, reusable, and composable.

**EVOLUTION:**
Specification Pattern was formalised by Eric Evans and Martin
Fowler (1997) as part of Domain-Driven Design vocabulary.
Java's `Predicate<T>` interface (Java 8) is a single-method
Specification -- `and()`, `or()`, and `negate()` provide
the composition operators. JPA Specification (Spring Data)
extended the pattern to database queries: `Specification<T>`
composes into a JPA `CriteriaQuery`. The pattern gained
popularity in DDD-influenced codebases where business rules
must be composable, testable, and expressible in domain language.
QueryDSL and jOOQ provide specification-like composable query APIs.

---

### 📘 Textbook Definition

The **Specification** pattern encapsulates a business rule in a reusable object with a single `isSatisfiedBy(candidate)` method that returns boolean. Specifications can be combined using logical operations: `and(other)` (conjunction), `or(other)` (disjunction), and `not()` (negation), producing composite specifications. In Domain-Driven Design (Evans, 2003), Specification is used to encapsulate selection criteria that can be passed to repositories as queries, used to validate domain objects, or applied as predicates in collections.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A named, reusable, composable business rule object - rather than an inline if-statement.

**One analogy:**
> Ingredient filters in a recipe app. Instead of hardcoding "vegetarian AND gluten-free AND under 30 minutes," you have three independent filter buttons. Each is a Specification. You can combine them freely: just vegetarian, or vegetarian AND gluten-free, or gluten-free OR under 30 minutes. The filters are named, composable, and reusable across the whole app.

**One insight:**
Specification's power is that business rules become first-class objects. They can be named after domain language (`EligibleForFreeShippingSpec`), stored, measured (how many products match?), combined (eligibility for discount bundle = spec1.and(spec2)), and documented - none of which is possible when rules are anonymous boolean expressions in if-statements.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A business rule is a predicate on a domain object - it returns true or false.
2. Rules should be reusable across different contexts.
3. Complex rules are composed from simpler rules.

**DERIVED DESIGN:**
Given invariants 1+2: create an interface `Specification<T>` with `boolean isSatisfiedBy(T candidate)`. Each rule is a class implementing this interface. Given invariant 3: implement `and()`, `or()`, `not()` as default methods or base class methods that return composite specifications internally wrapping two specifications with logical operations.

```
AndSpecification: isSatisfiedBy(x) = left.isSatisfiedBy(x) && right.isSatisfiedBy(x)
OrSpecification:  isSatisfiedBy(x) = left.isSatisfiedBy(x) || right.isSatisfiedBy(x)
NotSpecification: isSatisfiedBy(x) = !inner.isSatisfiedBy(x)
```

**THE TRADE-OFFS:**
**Gain:** Rules are named domain objects; reusable across features; composable; testable in isolation; readable business language in code.
**Cost:** More classes than inline conditions; composing to SQL queries requires additional adapter (repository must translate Specification to criteria); over-specification of simple one-location rules adds boilerplate without benefit.

---

### 🧪 Thought Experiment

**SETUP:**
Find all products eligible for a "summer sale" bundle: in-stock, price < $30, rated > 3.5, not already on sale.

**WITHOUT SPECIFICATION:**
```java
products.stream()
  .filter(p -> p.inStock()
    && p.price().compareTo(BigDecimal.valueOf(30)) < 0
    && p.rating() > 3.5
    && !p.onSale())
  .collect(toList());
```
New requirement: also show products to a marketing dashboard. Copy-paste the filter. Change "price < $30" to "price < $25" for the dashboard - one copy updated, one not. Divergence.

**WITH SPECIFICATION:**
```java
Specification<Product> summerSaleEligible =
    new InStockSpec()
      .and(new PriceBelowSpec(30))
      .and(new MinRatingSpec(3.5))
      .and(new NotSpec(new OnSaleSpec()));

// Reuse in catalog:
catalog.findBy(summerSaleEligible);
// Reuse in dashboard (different price):
dashboard.findBy(new PriceBelowSpec(25).and(summerSaleEligible));
```

**THE INSIGHT:**
Specifications can be composed differently for different contexts using the same atomic rules. Changing `InStockSpec` to handle backorder changes it everywhere. Rules are defined once and reused everywhere.

---

### 🧠 Mental Model / Analogy

> Specification is like a set of coloured LEGO bricks. Each brick is a rule (`InStockBrick`, `PriceBrick`). You connect bricks to form larger structures (composite specifications). You can build any shape from the same bricks in different combinations. Individual bricks can be tested, named, and reused in any project. The composition mechanism (LEGO stud) is `and()`, `or()`, `not()`.

- "Individual LEGO brick" → atomic Specification (InStockSpec)
- "LEGO stud connection" → `and()` / `or()` composition operators
- "Complex LEGO structure" → composite Specification (bundled rules)
- "Testing a single brick" → unit test for one Specification
- "Same bricks in different models" → reuse across features

Where this analogy breaks down: LEGO bricks have physical constraints on connection. Specifications have no such constraint - any specification can compose with any other, even if the combination is semantically meaningless. The developer is responsible for composing meaningful rules.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Specification is a named rule object. Instead of writing `if (price < 50)` everywhere, you create a `PriceBelowFifty` object that knows how to answer "does this product meet the rule?" You can combine rules: "this AND that AND NOT that."

**Level 2 - How to use it (junior developer):**
Create `interface Specification<T> { boolean isSatisfiedBy(T t); }`. Add default methods `and(Specification<T> other)` and `or(Specification<T> other)` returning composite specs. Implement atomic rule classes. Use: `new InStockSpec().and(new PriceBelowSpec(50)).isSatisfiedBy(product)`. For repository queries in Spring, extend Specification to implement Spring Data JPA's `Specification<T>` interface which translates to Criteria API predicates.

**Level 3 - How it works (mid-level engineer):**
Spring Data JPA's `JpaSpecificationExecutor` accepts `Specification<T>` objects and translates them to `CriteriaQuery` predicates. The JPA Specification interface `toPredicate(Root<T>, CriteriaQuery<?>, CriteriaBuilder)` returns a JPA `Predicate`. Composite specifications use `cb.and()` / `cb.or()`. This approach translates business-domain specifications directly to SQL -- an `InStockSpec.toPredicate()` generates `WHERE stock > 0`. Complex filtering becomes a combinable query API without raw JPQL. Spring Data Specifications can be stateless singletons: `INSTANCE = new InStockSpec()` - thread-safe because `toPredicate` takes the builder as parameter.

**Level 4 - Why it was designed this way (senior/staff):**
Eric Evans described Specification in "Domain-Driven Design" (2003) as a pattern for expressing selection criteria in domain language. The key DDD insight: selection criteria are domain concepts (EligibilitySpec, RiskSpec) that belong in the domain model, not in the query layer. A specification like `IsPremiumCustomer` encodes domain expertise (membership duration criteria, purchase history thresholds) that would otherwise live in SQL WHERE clauses invisible to the domain model. At scale, Specification-to-SQL translation becomes a DSL problem: complex combinations of specifications representing different customer segments, product eligibility rules, or fraud detection criteria can be stored as data (serialised spec trees) and evaluated dynamically - the foundation of configurable business rules engines (Drools, Easy Rules).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  SPECIFICATION - COMPOSITION TREE                    │
│                                                      │
│  Spec: InStock AND Price<50 AND NOT OnSale           │
│                                                      │
│            AndSpec                                   │
│           /       \                                  │
│        AndSpec    NotSpec                            │
│        /  \          \                               │
│  InStock  Price<50  OnSale                           │
│                                                      │
│  isSatisfiedBy(product):                             │
│    = InStock.isSatisfiedBy(p)                        │
│      && Price<50.isSatisfiedBy(p)                    │
│      && NOT OnSale.isSatisfiedBy(p)                  │
└──────────────────────────────────────────────────────┘
```

**Composition operators (abstract base class):**
```java
public abstract class AbstractSpec<T>
    implements Specification<T> {

    public AbstractSpec<T> and(Specification<T> other) {
        return new AndSpec<>(this, other);
    }
    public AbstractSpec<T> or(Specification<T> other) {
        return new OrSpec<>(this, other);
    }
    public AbstractSpec<T> not() {
        return new NotSpec<>(this);
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Spring Data JPA):**
```
HTTP GET /products?filter=summer-sale
  → ProductController.findSummerSale()
  → Specification<Product> spec =
      new InStockSpec()
        .and(new PriceBelowSpec(30))
              ← YOU ARE HERE (spec built)
  → productRepo.findAll(spec)
  → JPA translates spec to CriteriaQuery
  → SQL: WHERE stock > 0 AND price < 30
  → returns matching products
  → HTTP 200 with product list
```

**FAILURE PATH:**
```
Specification returns null predicate on invalid input
  → JPA Criteria API throws NullPointerException
  → Or: incorrect predicate yields full table scan
Fix: validate spec inputs; use cb.isTrue(cb.literal(true))
     for no-op specs rather than null
```

**WHAT CHANGES AT SCALE:**
At millions of products, each `isSatisfiedBy()` call in-memory is expensive. Translate Specifications to database predicates (JPA Criteria, QueryDSL) to push filtering to the DB index layer. For very complex or dynamic rule combinations, consider Drools or a dedicated rules engine that compiles specifications into optimised execution plans.

---

### 💻 Code Example

**Example 1 - Pure Specification (in-memory):**
```java
// Interface with composition methods
public interface Specification<T> {
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

// Atomic specifications
public class InStockSpec implements Specification<Product> {
    @Override
    public boolean isSatisfiedBy(Product p) {
        return p.stockQuantity() > 0;
    }
}

public class PriceBelowSpec implements Specification<Product> {
    private final BigDecimal threshold;

    public PriceBelowSpec(double threshold) {
        this.threshold = BigDecimal.valueOf(threshold);
    }

    @Override
    public boolean isSatisfiedBy(Product p) {
        return p.price().compareTo(threshold) < 0;
    }
}

// Usage: composable, named rule
Specification<Product> summerDeal =
    new InStockSpec()
      .and(new PriceBelowSpec(30.0))
      .and(new MinRatingSpec(4.0));

List<Product> deals = products.stream()
    .filter(summerDeal::isSatisfiedBy)
    .collect(toList());
```

**Example 2 - Spring Data JPA Specification:**
```java
// Translates to SQL via JPA Criteria API
public class InStockJpaSpec
    implements org.springframework.data.jpa.domain.Specification<Product> {

    @Override
    public Predicate toPredicate(Root<Product> root,
        CriteriaQuery<?> query, CriteriaBuilder cb) {
        return cb.greaterThan(root.get("stockQuantity"), 0);
    }
}

public class PriceBelowJpaSpec
    implements org.springframework.data.jpa.domain.Specification<Product> {
    private final BigDecimal max;

    @Override
    public Predicate toPredicate(Root<Product> root,
        CriteriaQuery<?> query, CriteriaBuilder cb) {
        return cb.lessThan(root.get("price"), max);
    }
}

// Repository:
public interface ProductRepository
    extends JpaRepository<Product, Long>,
            JpaSpecificationExecutor<Product> {}

// Compose and pass to repository:
Specification<Product> spec = where(new InStockJpaSpec())
    .and(new PriceBelowJpaSpec(BigDecimal.valueOf(30)));

List<Product> products = productRepo.findAll(spec);
// SQL: SELECT * FROM products WHERE stock > 0 AND price < 30
```

---

### ⚖️ Comparison Table

| Approach | Reusability | Composability | SQL Translation | Best For |
|---|---|---|---|---|
| **Specification** | High | Composable | Via JPA Criteria | Complex, reusable domain rules |
| Inline `Predicate<T>` | Low (anonymous) | Limited | No | Simple one-off filtering |
| @Query JPQL | Medium (named) | Low | Yes | Simple queries, no composition |
| Criteria API | Low | Manual | Yes | Complex SQL without domain layer |
| QueryDSL | Medium | Type-safe | Yes | Type-safe query composition |

How to choose: use Specification when business rules are domain concepts that recur across features. Use `@Query` or QueryDSL for complex queries focused on performance. Use inline `Predicate` for simple, single-use filtering.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Specification is only for database queries | Specification works on any collection or domain validation. It works in-memory, with repositories, and as validation rules |
| Specification replaces all predicates | Simple, one-line, single-use predicates don't need a Specification class. Apply Specification when rules have domain names, are reused, or are composed |
| Java 8 Predicate<T> is the same as Specification | `Predicate<T>` has `and`, `or`, `negate` but carries no domain semantics or SQL translation. Specification adds domain meaning and optional DB translation |
| Specification violates encapsulation | Done correctly, Specifications query public accessors. If a Specification requires private access, refactor the domain object to expose the appropriate query method |
| Composition always builds an object tree in memory | Lambda-based Specifications (default interface methods returning lambdas) don't build a tree - they compose method calls. JPA Specifications build a CriteriaBuilder tree for SQL generation |

---

### 🚨 Failure Modes & Diagnosis

**1. N+1 Queries with In-Memory Specifications**

**Symptom:** Filtering 10,000 products with a Specification takes 60 seconds. Each specification check triggers lazy-loading of related entities.

**Root Cause:** `InStockSpec.isSatisfiedBy(p)` calls `p.getWarehouseItems().size()` which lazy-loads a collection per product - 10,000 queries.

**Diagnostic:**
```bash
# Enable Hibernate SQL logging
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
# Count SQL statements executed during spec evaluation
```

**Fix:**
Translate the specification to a JPA query with explicit `JOIN FETCH` or a SQL predicate. For complex in-memory specs, load data using a projection (DTO) with required fields pre-fetched.

**Prevention:** Specifications accessing lazy-loaded associations must be translated to DB predicates or data must be fetched eagerly.

---

**2. Specification Permissiveness - No-Op Spec Selects All**

**Symptom:** A "premium customers only" endpoint returns all customers. The specification is silently no-op.

**Root Cause:** A conditional Specification: `if (premiumEnabled) return premiumSpec; else return null` - null passed to `findAll(spec)` results in "no restriction" in Spring Data JPA.

**Diagnostic:**
```bash
# Spring Data JPA with null Specification = no WHERE clause
# Check generated SQL:
spring.jpa.show-sql=true
# If no WHERE clause: spec returned null
```

**Fix:**
```java
// Specification.where(null) also returns no restriction
// GOOD: return a Specification that always returns true
// for "no filter" case:
Specification<Customer> noRestriction =
    (root, query, cb) -> cb.isTrue(cb.literal(true));
// or use Optional<Specification<T>> to make nullability explicit
```

**Prevention:** Always return a valid Specification from factory methods. Use `Optional<Specification<T>>` to force callers to handle the absent case.

---

**3. Specification Composition Order - Short-Circuit Missed**

**Symptom:** Specifications that call expensive external services (API calls) are always called even when the candidate could be rejected cheaply.

**Root Cause:** Composition order matters: `expensiveSpec.and(cheapSpec)` calls `expensive` first; `cheapSpec.and(expensiveSpec)` evaluates `cheap` first and short-circuits on false.

**Diagnostic:**
```bash
# Add logging to each spec's isSatisfiedBy:
log.debug("Evaluating ExpensiveSpec for {}", candidate);
# If ExpensiveSpec logs appear for candidates that
# are obviously failing cheapSpec: order is wrong
```

**Fix:**
```java
// Ensure cheap specs evaluate first
Specification<Customer> spec =
    new InAccountGoodStandingSpec() // cheap: DB check
      .and(new FraudDetectionSpec()); // expensive: API call
// InAccountGoodStanding checked first;
// FraudDetection only if account is in good standing
```

**Prevention:** Order specifications from cheapest to most expensive. Document the execution order assumptions in composite specifications.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Predicate` - a Specification is a named, domain-meaningful Predicate; `java.util.function.Predicate<T>` is the functional primitive that Specification builds upon
- `Composite Pattern` - `AndSpec`, `OrSpec`, `NotSpec` are Composite objects that combine two child Specifications
- `Domain-Driven Design (DDD)` - Specification was formalised by Eric Evans as a DDD tactical pattern for selection criteria

**Builds On This (learn these next):**
- `Spring Data JPA Specification` - the framework implementation that translates domain Specifications into JPA Criteria API predicates
- `Business Rules Engine (Drools)` - Specification taken to its extreme: configurable, externalised rules stored and updated without code changes
- `QueryDSL` - type-safe JPA query building that complements Specification for complex database queries

**Alternatives / Comparisons:**
- `Strategy` - both encapsulate logic; Specification is a boolean predicate; Strategy is an algorithm that produces a result
- `Chain of Responsibility` - also processes items through a chain; Specification combines rules statically; Chain processes dynamically with possible early exit
- `Criteria API` - the database-level alternative; powerful but not domain-language-readable; Specification adds domain semantics on top

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Named, composable business rule object    │
│              │ (predicate) for selecting domain objects  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Business rules scattered as inline        │
│ SOLVES       │ conditions; not reusable or composable    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ and() / or() / not() turn rules into      │
│              │ first-class combinable domain objects     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Rules are domain concepts; reused across  │
│              │ features; or need to translate to SQL     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple single-use filter; use inline      │
│              │ Predicate instead                         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Domain-readable composable rules vs       │
│              │ more classes and SQL translation effort   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Name your rules; combine them freely."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring Data Specification →               │
│              │ Domain Events → Business Rules Engine     │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Encapsulate a business rule as a named, composable predicate.
Business rules become first-class objects: testable in isolation,
combinable into complex rules, and readable in domain language.

**Where else this pattern appears:**
- **Search engine query syntax:** Boolean operators AND, OR,
  NOT in search queries compose specification objects at the
  query language level -- `Specification` semantics in the
  search engine's query parser.
- **Firewall rules (iptables):** Each firewall rule is a
  specification (port=80 AND protocol=TCP AND source=192.168.x.x);
  chains compose rules into ordered policies.
- **Database query predicates (WHERE clauses):** SQL's `WHERE
  age > 18 AND (country = 'US' OR premium = true)` is a
  composed specification -- each predicate is a Specification
  unit; AND/OR are the composition operators.

---

### 💡 The Surprising Truth

Java's `Predicate<T>` interface, used millions of times daily
in stream operations, is a stripped-down Specification pattern.
`predicate.and(otherPredicate)` is Specification composition;
`predicate.negate()` is NOT; `predicate.or(other)` is OR.
The only difference from the full Specification pattern is
that `Predicate<T>` lacks meaningful naming (a predicate
is anonymous unless you assign it to a named variable).
When a team writes `Predicate<User> isPremium = u ->
u.hasPremiumSubscription()` and composes it, they are
implementing the Specification pattern -- just with Java's
built-in functional interface rather than an explicit class.
---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce recommendation engine uses Specification to build product eligibility rules dynamically from user-configurable criteria stored in a database (e.g., segment: "premium users → price under $200 AND rating > 4.5"). Each request loads the user's segment specification and evaluates it against 500,000 products in memory. Calculate the approximate evaluation time assuming each `isSatisfiedBy()` takes 1 μs. Describe two architectural changes that would bring this under 50 ms without simplifying the specification model.

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A `ComplianceSpecification` combines: `ActiveAccountSpec.and(KYCVerifiedSpec).and(NotHighRiskCountrySpec)`. The `NotHighRiskCountrySpec` calls an external compliance API that takes 200 ms. In a 100-request/second load test, this specification is evaluated for every API request. Calculate the throughput impact. Describe a caching strategy applied at the Specification level (not the API level) that reduces API calls by 95% while maintaining correctness, and identify the one data consistency risk this caching introduces.



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A Spring Data application uses
`Specification<Product>` to build dynamic search queries.
A requirement says: specifications must be cached by their
composition key so that identical queries reuse the cached
JPA Criteria object. Design the caching strategy and describe
the equality/hashCode requirements for Specification objects
to make caching reliable.

*Hint: The Failure Modes section addresses specification
testability. The caching problem requires Specification objects
to correctly implement value equality -- which lambdas do NOT
provide by default. This is the key obstacle to cache-based
Specification reuse.*
