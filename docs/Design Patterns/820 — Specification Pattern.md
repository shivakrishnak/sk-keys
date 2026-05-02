---
layout: default
title: "Specification Pattern"
parent: "Design Patterns"
nav_order: 820
permalink: /design-patterns/specification-pattern/
number: "820"
category: Design Patterns
difficulty: ★★★
depends_on: "Interpreter Pattern, Composite Pattern, Spring Data JPA, Domain-Driven Design"
used_by: "Complex domain queries, business rule encapsulation, Spring Data Specification, validation"
tags: #advanced, #design-patterns, #ddd, #spring-data, #jpa, #domain-rules, #composable
---

# 820 — Specification Pattern

`#advanced` `#design-patterns` `#ddd` `#spring-data` `#jpa` `#domain-rules` `#composable`

⚡ TL;DR — **Specification Pattern** encapsulates a business rule as a reusable, composable object with `isSatisfiedBy(T candidate)` — combine rules with `and()`, `or()`, `not()` to build complex queries without scattering logic across the codebase.

| #820            | Category: Design Patterns                                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Interpreter Pattern, Composite Pattern, Spring Data JPA, Domain-Driven Design              |                 |
| **Used by:**    | Complex domain queries, business rule encapsulation, Spring Data Specification, validation |                 |

---

### 📘 Textbook Definition

**Specification Pattern** (Eric Evans and Martin Fowler, "Specifications", 1997 white paper; Evans, "Domain-Driven Design", 2003, pp. 226–233): a Domain-Driven Design tactical pattern that encapsulates a business rule (a predicate over a domain object) in a standalone, reusable specification object. Interface: `boolean isSatisfiedBy(T candidate)`. Composite specifications: `AndSpecification`, `OrSpecification`, `NotSpecification` allow boolean composition. In Spring: `org.springframework.data.jpa.domain.Specification<T>` provides a JPA Criteria API integration — specifications translate to `javax.persistence.criteria.Predicate` objects for dynamic database queries. Key benefits: reusability (same specification used in validation, querying, filtering), readability (named business rules), composability (combine without inheritance), testability (each specification unit-tested in isolation).

---

### 🟢 Simple Definition (Easy)

`CustomerIsActive`: checks if a customer is active. `CustomerIsPremium`: checks if a customer is premium. `OrderValueExceedsThreshold`: checks if order total > threshold. Compose: `CustomerIsActive.and(CustomerIsPremium)` → premium active customers. Reuse the same specifications in: filter a list in memory, build a JPA query, validate a business rule. One named specification object per business rule: readable, testable, composable.

---

### 🔵 Simple Definition (Elaborated)

Without Specification Pattern: business rule logic scattered across services — `customerRepository.findByStatusAndPremiumAndAgeGreaterThan(ACTIVE, true, 18)` in one service, `customers.stream().filter(c -> c.isActive() && c.isPremium() && c.getAge() > 18)` in another. Same rule, two implementations that can drift. With Specification Pattern: `new ActiveCustomerSpec().and(new PremiumCustomerSpec()).and(new AgeAboveSpec(18))`. Used in the repository (JPA), in a service (in-memory filter), in a validator (can this customer place an order?). Single definition, three use sites.

---

### 🔩 First Principles Explanation

**Complete Specification Pattern with Spring Data JPA integration:**

```
GENERIC SPECIFICATION INTERFACE:

  public interface Specification<T> {
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

  // Terminal specifications (reusable business rules):

  public class ActiveCustomerSpec implements Specification<Customer> {
      @Override
      public boolean isSatisfiedBy(Customer customer) {
          return customer.getStatus() == CustomerStatus.ACTIVE;
      }
  }

  public class PremiumCustomerSpec implements Specification<Customer> {
      @Override
      public boolean isSatisfiedBy(Customer customer) {
          return customer.isPremium();
      }
  }

  public class AgeAboveSpec implements Specification<Customer> {
      private final int minimumAge;

      public AgeAboveSpec(int minimumAge) {
          this.minimumAge = minimumAge;
      }

      @Override
      public boolean isSatisfiedBy(Customer customer) {
          return customer.getAge() > minimumAge;
      }
  }

  // Composite usage:
  Specification<Customer> eligibleForPremiumOffer =
      new ActiveCustomerSpec()
          .and(new PremiumCustomerSpec())
          .and(new AgeAboveSpec(18));

  // In-memory filtering:
  List<Customer> eligible = customers.stream()
      .filter(eligibleForPremiumOffer::isSatisfiedBy)
      .collect(toList());

  // Domain validation:
  if (!eligibleForPremiumOffer.isSatisfiedBy(customer)) {
      throw new CustomerNotEligibleException("Customer does not meet premium offer criteria");
  }

SPRING DATA JPA SPECIFICATION:

  // Spring's org.springframework.data.jpa.domain.Specification<T>
  // translates to JPA Criteria API (generates SQL WHERE clauses)

  // Repository:
  public interface CustomerRepository
      extends JpaRepository<Customer, Long>,
              JpaSpecificationExecutor<Customer> {}   // enables findAll(Specification<Customer>)

  // JPA Specifications (generates SQL predicates):
  public class CustomerSpecs {

      public static Specification<Customer> isActive() {
          return (root, query, criteriaBuilder) ->
              criteriaBuilder.equal(root.get("status"), CustomerStatus.ACTIVE);
      }

      public static Specification<Customer> isPremium() {
          return (root, query, criteriaBuilder) ->
              criteriaBuilder.isTrue(root.get("premium"));
      }

      public static Specification<Customer> ageAbove(int minimumAge) {
          return (root, query, criteriaBuilder) ->
              criteriaBuilder.greaterThan(root.get("age"), minimumAge);
      }

      public static Specification<Customer> registeredAfter(LocalDate date) {
          return (root, query, criteriaBuilder) ->
              criteriaBuilder.greaterThan(root.get("registrationDate"), date);
      }
  }

  // Compose specifications (Spring's Specification supports and()/or()/not()):
  Specification<Customer> spec = CustomerSpecs.isActive()
      .and(CustomerSpecs.isPremium())
      .and(CustomerSpecs.ageAbove(18));

  // Execute as single SQL query:
  List<Customer> results = customerRepository.findAll(spec);
  // Generated SQL (approximately):
  // SELECT * FROM customers
  // WHERE status = 'ACTIVE'
  //   AND premium = true
  //   AND age > 18;

  // Dynamic query composition (from filter request):
  public List<Customer> search(CustomerSearchRequest req) {
      Specification<Customer> spec = Specification.where(null);  // Always-true base

      if (req.getActiveOnly()) spec = spec.and(CustomerSpecs.isActive());
      if (req.getPremiumOnly()) spec = spec.and(CustomerSpecs.isPremium());
      if (req.getMinAge() != null) spec = spec.and(CustomerSpecs.ageAbove(req.getMinAge()));
      if (req.getRegisteredAfter() != null)
          spec = spec.and(CustomerSpecs.registeredAfter(req.getRegisteredAfter()));

      return customerRepository.findAll(spec);
  }
  // Result: composable dynamic query without if-else on query strings.
  // Adding a new filter: add one new static spec method + one new if block. No query rewrite.

DOMAIN VALIDATION REUSE:

  // Same spec used for validation AND querying:

  @Service @RequiredArgsConstructor
  public class OfferService {
      private final CustomerRepository customerRepo;

      // IN-MEMORY (validation):
      public void validateEligibility(Customer customer) {
          Specification<Customer> eligible = CustomerSpecs.isActive()
              .and(CustomerSpecs.isPremium());
          if (!eligible.isSatisfiedBy(customer)) {
              throw new CustomerNotEligibleException(customer.getId());
          }
      }

      // JPA QUERY (batch query):
      public List<Customer> findEligibleCustomers() {
          return customerRepo.findAll(
              CustomerSpecs.isActive().and(CustomerSpecs.isPremium()));
      }
  }
  // Single specification definition; used in both validation and database query.
  // Business rule cannot drift between the two use sites.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Specification:

- Business rules scattered: service methods, query method names, WHERE clauses, stream filters — multiple places, can drift and become inconsistent
- Adding a new filter: modify query method signature, modify JPQL, modify stream filter — in sync
- Rules not named, not reusable, not testable in isolation

WITH Specification:
→ Each business rule: one named, reusable, testable specification class. Compose with `and()`, `or()`, `not()`. Use in queries, validation, and in-memory filtering from one definition.

---

### 🧠 Mental Model / Analogy

> A hiring process with reusable screening criteria. Each criterion is a card: "Has Java experience", "Has 3+ years experience", "Location in EU", "Available for full-time". Each card: checks one specific rule against a candidate (`isSatisfiedBy(candidate)`). Compose criteria: "Has Java AND 3+ years AND Available" for a senior Java role. "Has Java OR Python AND EU" for a different role. Mix and match any criteria cards into any combination. Add a new criterion: one new card, no existing cards change. Same criteria cards used in: initial screening (in-memory), database search, contract validation.

"Each criterion card" = one Specification class (single, named business rule)
"`isSatisfiedBy(candidate)`" = method checking if the candidate meets this one criterion
"Has Java AND 3+ years AND Available" = `JavaSpec().and(SeniorSpec()).and(AvailableSpec())`
"Mix and match any combination" = composability via `and()`, `or()`, `not()`
"Same cards for screening and DB search" = same Specification used in-memory AND in JPA query
"Add a new criterion: one new card" = new class, no changes to other specs

---

### ⚙️ How It Works (Mechanism)

```
SPECIFICATION PATTERN STRUCTURE:

  Specification<T>           (interface)
  ├── isSatisfiedBy(T) → boolean
  ├── and(Specification<T>) → Specification<T>   (AndSpec wrapper)
  ├── or(Specification<T>)  → Specification<T>   (OrSpec wrapper)
  └── not()                 → Specification<T>   (NotSpec wrapper)

  Concrete Implementations (Terminal):
  ActiveCustomerSpec, PremiumCustomerSpec, AgeAboveSpec, ...

  Composition creates anonymous Composite specifications:
  active.and(premium) = AnonymousSpec: active.isSatisfiedBy(c) && premium.isSatisfiedBy(c)

  SPRING DATA JPA INTEGRATION:

  Specification<T>       (Spring interface: (Root, CriteriaQuery, CriteriaBuilder) → Predicate)
  Predicate              (JPA: SQL WHERE clause fragment)
  CriteriaBuilder        (JPA: builds predicates: equal, greaterThan, like, etc.)
  Root<T>                (JPA: from clause — access entity fields)

  Spring's Specification.and(other):
  return (root, query, cb) → cb.and(this.toPredicate(root, query, cb),
                                    other.toPredicate(root, query, cb));
  // cb.and() → SQL AND clause combining both predicates
```

---

### 🔄 How It Connects (Mini-Map)

```
Business rules need to be: reusable, composable, testable, named
        │
        ▼
Specification Pattern ◄──── (you are here)
(isSatisfiedBy(); and()/or()/not(); Spring Data JPA integration)
        │
        ├── Composite Pattern: CompositeSpecification (and/or/not) IS a Composite Pattern
        ├── Interpreter Pattern: Specification = simple Interpreter (one grammar rule per spec)
        ├── Spring Data JPA Specification: production implementation of this pattern
        └── Domain-Driven Design: Specifications express domain rules in the domain layer
```

---

### 💻 Code Example

(See First Principles — complete Java Specification interface with default `and()`/`or()`/`not()`, terminal specs for Customer, Spring Data JPA integration with `CustomerSpecs`, and dynamic query composition from a search request.)

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spring Data's Specification is the Specification Pattern | Spring's `org.springframework.data.jpa.domain.Specification<T>` implements the pattern specifically for JPA Criteria API (database queries). Evans/Fowler's original pattern is for in-memory `isSatisfiedBy(T)` checks. They serve related but different purposes: in-memory validation vs. SQL generation. You need both: one for domain validation (in-memory), one for JPA queries (Criteria API). They can coexist and ideally share the same named specification concept (even if implemented differently). |
| Specification Pattern replaces Query by Example or JPQL  | They solve the same problem differently. Specification Pattern: composable, named, reusable, testable. JPQL/Query by Example: simpler for static queries, hard to compose dynamically. Query methods (`findByStatusAndPremium`): compile-time safe but inflexible. Use Specification when you need: dynamic composition of multiple filters at runtime based on user input. Use JPQL for simple, static queries.                                                                                                  |
| All business rules should be Specifications              | Specification Pattern shines when: (1) the same rule is used in multiple contexts (validate + query + filter), (2) rules are dynamically composed, (3) rules are complex enough to warrant naming. Simple, one-time rules: `if (order.getTotal() > 0)` — don't wrap in a Specification. Apply the pattern where it provides value: shared, named business rules used in multiple contexts.                                                                                                                        |

---

### 🔥 Pitfalls in Production

**N+1 query problem with in-memory Specification replacing JPA query:**

```java
// ANTI-PATTERN — using in-memory Specification for large datasets:

@Service
public class CustomerService {
    private final CustomerRepository repo;

    public List<Customer> findEligibleForOffer() {
        Specification<Customer> spec = new ActiveCustomerSpec()
            .and(new PremiumCustomerSpec())
            .and(new AgeAboveSpec(18));

        // WRONG: loading ALL customers to memory, then filtering:
        List<Customer> all = repo.findAll();  // SELECT * FROM customers → potentially 1M rows!
        return all.stream()
            .filter(spec::isSatisfiedBy)
            .collect(toList());
        // Problem: loads 1,000,000 rows into memory to filter to 10,000 eligible customers.
        // Heap: 1M Customer objects → GC pressure, possible OOM.
    }
}

// FIX — use JPA Specification for database-level filtering:
@Service
public class CustomerService {
    private final CustomerRepository repo;  // extends JpaSpecificationExecutor

    public List<Customer> findEligibleForOffer() {
        // JPA Specification: filters IN DATABASE — only 10,000 rows returned:
        Specification<Customer> spec = CustomerSpecs.isActive()
            .and(CustomerSpecs.isPremium())
            .and(CustomerSpecs.ageAbove(18));

        return repo.findAll(spec);
        // Generated SQL: SELECT * FROM customers WHERE status='ACTIVE' AND premium=true AND age>18
        // Returns only matching rows. Zero OOM risk.
    }

    // For large result sets: use pagination:
    public Page<Customer> findEligibleForOfferPaged(Pageable pageable) {
        Specification<Customer> spec = CustomerSpecs.isActive()
            .and(CustomerSpecs.isPremium())
            .and(CustomerSpecs.ageAbove(18));
        return repo.findAll(spec, pageable);
    }
}

// RULE:
// In-memory Specification (isSatisfiedBy): use for domain validation on single objects.
// JPA Specification (toPredicate): use for querying collections from the database.
// Never load a large collection to filter in memory when a JPA query would work.
```

---

### 🔗 Related Keywords

- `Composite Pattern` — `AndSpecification`, `OrSpecification` are Composite Pattern structures
- `Interpreter Pattern` — each Specification is a simple interpretation of one grammar rule
- `Spring Data JPA` — `JpaSpecificationExecutor` enables Specification-based database queries
- `Domain-Driven Design` — Specifications express domain rules in the domain model layer
- `CriteriaBuilder (JPA)` — the API used by Spring's Specification to generate SQL predicates

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Encapsulate one business rule as a named  │
│              │ Specification; compose with and/or/not;  │
│              │ reuse for query, filter, validation.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Same rule in multiple contexts; dynamic  │
│              │ query composition from filters; complex  │
│              │ domain rules that need names + tests     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple, one-time filter; static query    │
│              │ (use JPQL); small dataset always loaded  │
│              │ in memory; over-engineering CRUD         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hiring criteria cards: one card per rule,│
│              │  combine any way. Same cards for CV     │
│              │  screening and database search."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Composite Pattern → Interpreter Pattern → │
│              │ Spring Data JPA → DDD → Rule Engine       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Data JPA's `Specification` uses the JPA Criteria API internally, which generates a `Predicate` object that becomes a SQL WHERE clause fragment. The Criteria API is type-unsafe (uses string field names like `root.get("status")`). Hibernate's Metamodel Generator generates a type-safe `Customer_` metamodel class that provides `Customer_.status` (a `SingularAttribute`). How does using the JPA static metamodel (`Customer_` class) improve Specification type safety, and what is the tradeoff in terms of build configuration and developer ergonomics?

**Q2.** The Specification Pattern (isSatisfiedBy) and the JPA Criteria API Specification serve the same conceptual role but are implemented differently. In a large codebase, you often need the same business rule in both forms: `isActive()` as an in-memory check for domain validation AND `isActive()` as a JPA Criteria predicate for database queries. How would you design a Specification abstraction that provides both forms from a single class definition, avoiding duplication while keeping the domain layer free of JPA dependencies (Hexagonal Architecture / Ports and Adapters)?
