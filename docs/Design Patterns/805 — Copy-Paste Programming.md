---
layout: default
title: "Copy-Paste Programming"
parent: "Design Patterns"
nav_order: 805
permalink: /design-patterns/copy-paste-programming/
number: "805"
category: Design Patterns
difficulty: ★★☆
depends_on: "Anti-Patterns Overview, DRY Principle, Refactoring"
used_by: "Code review, refactoring planning, code quality analysis"
tags: #intermediate, #anti-patterns, #design-patterns, #dry, #duplication, #refactoring
---

# 805 — Copy-Paste Programming

`#intermediate` `#anti-patterns` `#design-patterns` `#dry` `#duplication` `#refactoring`

⚡ TL;DR — **Copy-Paste Programming** is duplicating logic instead of abstracting it — violating DRY (Don't Repeat Yourself) — so every bug must be fixed in 5 places and every behavior change requires touching 10 files.

| #805            | Category: Design Patterns                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Anti-Patterns Overview, DRY Principle, Refactoring       |                 |
| **Used by:**    | Code review, refactoring planning, code quality analysis |                 |

---

### 📘 Textbook Definition

**Copy-Paste Programming** (identified in "Code Complete" by McConnell, 2004; "Clean Code" by Martin, 2008): the practice of duplicating code blocks — by copy-pasting — rather than abstracting the shared logic into a reusable function, class, or library. Violates the DRY principle (Don't Repeat Yourself, Hunt and Thomas "The Pragmatic Programmer", 1999): "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." Consequences: bug in duplicated logic requires the same fix in every copy; behavior change requires finding every copy; copies drift over time (some get patched, others don't) — producing inconsistent behavior across the system; code review complexity increases; test coverage degrades (only some copies are tested).

---

### 🟢 Simple Definition (Easy)

Validate email in 5 different places: `if (!email.contains("@") || email.length() < 5) { throw... }` — exact same logic, copied 5 times. A bug is found: email validation should also check for a dot after the `@`. Fix it in 1 place. Deploy. 4 other copies still have the bug. Users hit the bug. Developer searches for all copies. Finds 3 more. Fixes them. Deploys. Misses the 5th. Bug is now fixed in 4 of 5 places. Copy-Paste Programming: one bug, five fixes needed.

---

### 🔵 Simple Definition (Elaborated)

A payment service, order service, and subscription service all have this logic:

- Validate user has a valid payment method
- Check account has sufficient credit
- Apply tax based on user's region
- Calculate discount based on customer tier

All three services have a copy of this logic, written by three different developers at different times. Version 1: no tax rounding. Version 2: rounds to 2 decimal places. Version 3: rounds to 4 decimal places. Tax calculation returns different results depending on which service you use. The discrepancy is discovered in an audit 2 years later. Copy-Paste Programming: three copies, three variants, one real business rule.

---

### 🔩 First Principles Explanation

**The DRY violation spectrum and refactoring approaches:**

```
DRY VIOLATION SPECTRUM (from minor to severe):

  LEVEL 1 — MINOR: Repeated utility snippets (low risk)

  // 3 places: null-safe string length check
  if (str != null && !str.isEmpty()) { ... }

  // Fix: extract to utility or use Objects.requireNonNullElse + String methods
  // Modern Java: StringUtils.hasText(str) (Spring)

  LEVEL 2 — MODERATE: Repeated business validation (medium risk)

  // In UserController:
  if (email == null || !email.matches("[^@]+@[^@]+\\.[^@]+")) {
      throw new ValidationException("Invalid email");
  }

  // In CustomerService:
  if (email == null || !email.matches("[^@]+@[^@]+\\.[^@]+")) {
      throw new IllegalArgumentException("Email format invalid");
  }

  // In SignupService:
  if (email == null || !email.matches("[^@]+@[^@]+\\.[^@]+")) {
      throw new BadRequestException("Bad email");
  }

  // 3 different exception types, 3 copies of the regex.
  // Regex update: 3 places. Different exceptions confuse callers.

  // FIX — Extract Method to shared utility or domain object:
  @Value  // Lombok value object
  public class Email {
      private final String value;

      public Email(String raw) {
          if (raw == null || !raw.matches("[^@]+@[^@]+\\.[^@]+")) {
              throw new InvalidEmailException(raw);
          }
          this.value = raw.toLowerCase().trim();
      }
  }
  // One class, one regex, one exception type. Validate at construction = validate everywhere.

  LEVEL 3 — SEVERE: Duplicated business logic with divergence (high risk)

  // TaxCalculator in OrderService:
  BigDecimal calculateTax(BigDecimal amount, String region) {
      BigDecimal rate = TAX_RATES.get(region);
      return amount.multiply(rate).setScale(2, HALF_UP);
  }

  // TaxCalculator in SubscriptionService (copied 6 months later):
  BigDecimal computeTax(BigDecimal subtotal, String countryCode) {
      BigDecimal rate = TAX_RATES.get(countryCode);
      if (rate == null) rate = DEFAULT_RATE;   // added: handles null
      return subtotal.multiply(rate).setScale(4, HALF_UP);  // different scale!
  }

  // Differences:
  // - method name (calculateTax vs. computeTax)
  // - parameter name (region vs. countryCode) — same concept
  // - null handling: OrderService throws NPE; SubscriptionService uses default
  // - scale: 2 decimal places vs. 4 decimal places
  // - tax law change (rate update): must be made in BOTH places

  // FIX: single TaxService in a shared module
  @Service
  public class TaxService {
      public BigDecimal calculateTax(BigDecimal amount, String regionCode) {
          BigDecimal rate = Optional.ofNullable(TAX_RATES.get(regionCode))
              .orElse(DEFAULT_TAX_RATE);
          return amount.multiply(rate).setScale(4, HALF_UP);
      }
  }
  // OrderService and SubscriptionService both @Autowired TaxService.
  // One implementation. One test suite. One change point.

  LEVEL 4 — CRITICAL: Duplicated entire layers

  // Microservices team: each service copies the auth middleware,
  //                     the pagination logic, the error response builder
  // 8 services, 8 copies, 8 diverged implementations

  // FIX: shared library (Maven/Gradle module) for cross-cutting concerns
  // auth, pagination, error formatting: in shared-lib/
  // Each service: dependency on shared-lib.

DETECTING COPY-PASTE CODE:

  1. IDE: Refactor → Find Duplicates (IntelliJ IDEA)
  2. PMD: Copy-Paste Detector (CPD)
     mvn pmd:cpd
     # Reports duplicated code blocks > N tokens
  3. SonarQube: "Duplicated Lines" metric (target < 3%)
  4. Smell: bug in feature A, same bug found in feature B = copy-paste indicator
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT DRY (copy-paste approach):

- Faster for the first copy — no abstraction design needed
- Works immediately; feels productive

WITH DRY (abstracted approach):
→ One change propagates everywhere. One bug fix fixes all instances. One test covers all uses. Behavior is consistent across the system.

---

### 🧠 Mental Model / Analogy

> A franchise restaurant chain where each location cooks its own version of the "signature burger" from memory — no shared recipe card. Some add more salt; others skip the pickle; one location has the patty thickness wrong. Customer who orders the same burger in New York and Los Angeles gets different burgers. Corporate HQ issues a recall for contaminated lettuce: must call all 500 locations separately. With a standardized, shared recipe distributed from HQ: one recipe change, 500 locations updated simultaneously. Copy-Paste Programming = 500 kitchens, 500 recipes, no central recipe card.

"Each location cooks from memory" = each service copy-pastes validation/calculation logic
"Different salt, no pickle, wrong thickness" = diverged copies: different exception types, different rounding, different null handling
"Contaminated lettuce recall: call 500 locations" = fixing one bug in 500 copies
"Standardized recipe from HQ" = shared abstraction (shared library, TaxService, Email value object)
"One recipe change → 500 locations updated" = fix in one place → all callers updated

---

### ⚙️ How It Works (Mechanism)

```
REFACTORING MOVES FOR COPY-PASTE CODE:

  Extract Method:
  // Multiple methods share a 10-line block → extract to private method
  // Effect: single definition, called from multiple sites

  Extract Class:
  // Multiple classes share a cluster of related methods/fields
  // → extract to a new class with a clear responsibility

  Extract Module/Library:
  // Multiple services share logic
  // → shared library (Maven module / Gradle subproject)
  // Published as artifact; declared as dependency

  Value Object:
  // Validation + representation of a domain concept repeated everywhere
  // → Email, Money, TaxRegion value objects
  // Validate at construction; reuse everywhere

  Template Method Pattern:
  // Multiple algorithms share the same structure but differ in steps
  // → abstract base class with template method;
  //    subclasses override steps that differ

  Strategy Pattern:
  // Multiple algorithms differ in implementation but share an interface
  // → Strategy interface + concrete implementations
  //    Switch strategy at configuration time, not copy-paste time
```

---

### 🔄 How It Connects (Mini-Map)

```
Duplicated logic in multiple places → divergence → bug fixed in one, not all → inconsistency
        │
        ▼
Copy-Paste Programming ◄──── (you are here)
(DRY violation; one truth in many copies; multi-point maintenance burden)
        │
        ├── DRY Principle: the principle violated
        ├── Refactoring: Extract Method, Extract Class are the primary cures
        ├── Technical Debt: every copy is future maintenance debt
        └── Magic Numbers: often copy-pasted together with the logic containing them
```

---

### 💻 Code Example

```java
// BEFORE — copy-pasted pagination logic in 5 different service methods:

// In OrderService:
public PagedResult<Order> getOrders(int page, int size) {
    if (page < 0) page = 0;
    if (size <= 0 || size > 100) size = 20;
    PageRequest req = PageRequest.of(page, size, Sort.by("createdAt").descending());
    Page<Order> p = orderRepo.findAll(req);
    return new PagedResult<>(p.getContent(), p.getTotalElements(), page, size);
}

// In ProductService (copy-pasted from OrderService, 6 months later):
public PagedResult<Product> getProducts(int page, int size) {
    if (page < 0) page = 0;
    if (size <= 0 || size > 100) size = 20;
    PageRequest req = PageRequest.of(page, size, Sort.by("createdAt").descending());
    Page<Product> p = productRepo.findAll(req);
    return new PagedResult<>(p.getContent(), p.getTotalElements(), page, size);
}

// In CustomerService (copy-pasted, max size changed to 50 — drift!):
public PagedResult<Customer> getCustomers(int page, int size) {
    if (page < 0) page = 0;
    if (size <= 0 || size > 50) size = 20;  // Different max! Drift.
    PageRequest req = PageRequest.of(page, size, Sort.by("createdAt").descending());
    Page<Customer> c = customerRepo.findAll(req);
    return new PagedResult<>(c.getContent(), c.getTotalElements(), page, size);
}
// 5 copies. 3 have max=100; 2 have max=50. Inconsistent API behavior.

// AFTER — extracted shared pagination utility:
@Component
public class PaginationUtils {
    private static final int DEFAULT_PAGE_SIZE = 20;
    private static final int MAX_PAGE_SIZE = 100;

    public PageRequest validatedPageRequest(int page, int size, Sort sort) {
        int validPage = Math.max(0, page);
        int validSize = (size <= 0 || size > MAX_PAGE_SIZE) ? DEFAULT_PAGE_SIZE : size;
        return PageRequest.of(validPage, validSize, sort);
    }

    public <T> PagedResult<T> toPagedResult(Page<T> page, int requestedPage, int requestedSize) {
        return new PagedResult<>(page.getContent(), page.getTotalElements(),
                                  requestedPage, requestedSize);
    }
}

// In OrderService (now delegates to shared utility):
@Service @RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepo;
    private final PaginationUtils pagination;

    public PagedResult<Order> getOrders(int page, int size) {
        PageRequest req = pagination.validatedPageRequest(page, size,
                                Sort.by("createdAt").descending());
        return pagination.toPagedResult(orderRepo.findAll(req), page, size);
    }
}
// ProductService, CustomerService: same pattern, same max size, consistent behavior.
// Change DEFAULT_PAGE_SIZE or MAX_PAGE_SIZE: one place. Consistent everywhere.
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A little copy-paste is fine for "simple" things   | The problem is not the first copy — it's the second, third, and the maintenance trajectory. The exact logic that seems "simple enough to copy" today becomes the logic that diverges, gets partially updated, and produces subtle production bugs 18 months later. The DRY principle applies proportionally to: how often the code changes AND how many copies exist. If it will never change AND there's only one copy: acceptable. If it changes quarterly AND has 5 copies: always abstract.           |
| DRY means never having similar-looking code       | DRY is about knowledge, not text. Two methods that happen to have a similar structure but represent genuinely different domain concepts should NOT be merged into a single abstraction just to avoid textual duplication. "Wrong abstraction" (forcing unrelated concepts into one function) is worse than duplication. The WET (Write Everything Twice) guideline: duplicate once, abstract on the third occurrence — by then you understand the true shape of the abstraction.                          |
| Shared libraries always solve copy-paste problems | Shared libraries introduce coupling: all consumers upgrade together, or pin different versions, leading to split dependency management. For microservices: shared domain logic in a library creates tight coupling between independently deployable services. The solution per team/service boundary context: sometimes duplication across microservice boundaries is acceptable to maintain service autonomy. Apply DRY strictly within a bounded context; evaluate carefully across service boundaries. |

---

### 🔥 Pitfalls in Production

**Security vulnerability fixed in one copy, not propagated to others:**

```java
// ANTI-PATTERN — security validation copy-pasted and partially fixed:

// UserController.java (fixed first — SQL injection via parameterized query):
public User getUser(String userId) {
    return jdbcTemplate.queryForObject(
        "SELECT * FROM users WHERE id = ?",   // ✓ parameterized
        new Object[]{userId}, userMapper);
}

// AdminController.java (copy-pasted old version — NOT updated with fix):
public User getAdminUser(String userId) {
    return jdbcTemplate.queryForObject(
        "SELECT * FROM users WHERE id = '" + userId + "'",  // ✗ SQL injection!
        userMapper);
}

// LegacyApiController.java (3rd copy — also NOT updated):
public User getLegacyUser(String userId) {
    String sql = "SELECT * FROM users WHERE id = '" + userId + "'";  // ✗ SQL injection!
    return jdbcTemplate.queryForObject(sql, userMapper);
}

// Security audit found:
// - UserController: fixed (parameterized query)
// - AdminController: SQL injection vulnerability (OWASP A03: Injection)
// - LegacyApiController: SQL injection vulnerability
//
// Fix in one → forgot the copies → two live SQL injection endpoints.
// This is exactly OWASP A03 (Injection) risk created by Copy-Paste Programming.

// CORRECT APPROACH: single UserRepository:
@Repository
interface UserRepository extends JpaRepository<User, String> {
    // JPA always uses parameterized queries — SQL injection not possible
    Optional<User> findById(String userId);
}
// All three controllers inject UserRepository. One implementation. Zero SQL injection risk.
```

---

### 🔗 Related Keywords

- `DRY Principle` — the principle violated: Every piece of knowledge must have one authoritative representation
- `Refactoring` — Extract Method, Extract Class, Extract Module are the direct remediation moves
- `Technical Debt` — every copy is future debt: each subsequent change costs 5× more than a single abstracted change
- `Magic Numbers Anti-Pattern` — magic numbers are often copy-pasted together with the logic that contains them
- `Template Method Pattern` — a pattern for sharing algorithm structure while allowing variable steps

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Duplicating logic instead of abstracting. │
│              │ One bug: fix in 5 places. One change:     │
│              │ touch 10 files. Copies drift over time.  │
├──────────────┼───────────────────────────────────────────┤
│ DETECT WITH  │ PMD CPD; SonarQube duplicated lines;     │
│              │ "same bug found twice" pattern;           │
│              │ IntelliJ "Find Duplicates"                │
├──────────────┼───────────────────────────────────────────┤
│ FIX WITH     │ Extract Method → Extract Class →         │
│              │ Shared library for cross-service logic;  │
│              │ Value Objects for domain concept validation│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "500 franchise kitchens, 500 recipes,    │
│              │  no central recipe card: contaminated    │
│              │  lettuce → call all 500 locations."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DRY Principle → Extract Method →         │
│              │ Value Object → Template Method → PMD CPD  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The WET principle ("Write Everything Twice" or "We Enjoy Typing") is a pragmatic complement to DRY: accept the first duplication, look for the second, abstract on the third occurrence — because by the third occurrence you understand the true shape of the abstraction. Abstracting too early (after the first copy) often produces a "wrong abstraction" that forces unrelated things into one function, creating coupling that's worse than the duplication. How do you decide when duplication has crossed the threshold for abstraction? What signals indicate that the abstraction shape is now clear enough to extract safely?

**Q2.** In microservices architecture, each service is supposed to be independently deployable — which means shared libraries create deployment coupling. If `shared-lib v1.2` introduces a breaking change, ALL services using it must upgrade together — defeating independent deployability. Some teams duplicate code deliberately across services to maintain service autonomy ("acceptable duplication at service boundaries"). How do you apply DRY pragmatically in a microservices context? What categories of code should NEVER be duplicated across services (e.g., security logic) and what categories are acceptable to duplicate (e.g., simple DTOs)?
