---
layout: default
title: "Test Fixtures"
parent: "Testing"
nav_order: 1151
permalink: /testing/test-fixtures/
number: "1151"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, Test Isolation
used_by: All Developers
related: Test Isolation, Test Data Management, BeforeEach, Builder Pattern, Object Mother
tags:
  - testing
  - fixtures
  - test-data
  - setup
---

# 1151 — Test Fixtures

⚡ TL;DR — A test fixture is the known, fixed state of the world a test needs to run: the objects, data, and environment set up before a test executes and torn down afterward.

| #1151           | Category: Testing                                                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, Test Isolation                                                        |                 |
| **Used by:**    | All Developers                                                                   |                 |
| **Related:**    | Test Isolation, Test Data Management, BeforeEach, Builder Pattern, Object Mother |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Each test method contains 20 lines of setup code (create user, create cart, add items, create discount). The same setup is copy-pasted across 30 test methods. A change to the `User` constructor requires editing 30 tests. The setup code dwarfs the actual test assertion. With test fixtures, the setup is defined once, reused everywhere, and tests read as "given this state, when this happens, then this result."

---

### 📘 Textbook Definition

A **test fixture** is the set of preconditions or state necessary for running a test. This includes: objects that must be created before the test can run, database records, file system state, mock configurations, and network state. In JUnit 5: `@BeforeEach` (run before each test), `@BeforeAll` (run once before all tests in a class), `@AfterEach` (teardown after each test), `@AfterAll` (teardown after all tests). In the broader sense, fixture also refers to the helpers and patterns used to build consistent test data (Object Mother, Test Data Builder, factory methods).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Fixtures = the setup your test needs to run + the teardown to clean up.

**One analogy:**

> A fixture is like the **chef's mise en place** (French: everything in its place): before cooking begins, every ingredient is prepped, measured, and in position. The cooking (the test) starts from a known, prepared state. Without mise en place, cooking is chaotic and inconsistent.

---

### 🔩 First Principles Explanation

JUNIT 5 FIXTURE LIFECYCLE:

```java
@TestInstance(PER_CLASS)  // default: PER_METHOD (new instance per test)
class CartServiceTest {

    private CartService service;
    private FakeProductRepository productRepo;

    @BeforeAll      // once before all tests — for expensive setup
    static void initDatabase() { /* start Testcontainers */ }

    @BeforeEach     // before each test — reset state
    void setup() {
        productRepo = new FakeProductRepository();
        service = new CartService(productRepo);
        // fresh service for each test — isolation guaranteed
    }

    @Test void addItem_incrementsCartSize() { /* ... */ }
    @Test void removeItem_decrementsCartSize() { /* ... */ }

    @AfterEach void cleanup() { /* clear any side effects */ }

    @AfterAll      // once after all tests
    static void shutdownDatabase() { /* stop Testcontainers */ }
}
```

TEST DATA BUILDER PATTERN (avoid object construction repetition):

```java
// Without builder: scattered, brittle
User user = new User("alice", "alice@example.com", "password123",
    UserRole.STANDARD, true, LocalDate.now(), null, "en-US");

// With builder: readable, default-filled, only override what matters
User user = UserBuilder.aUser()
    .withEmail("alice@example.com")
    .withRole(UserRole.PREMIUM)
    .build();
// Sensible defaults for all other fields

// Builder definition (Object Mother pattern):
class UserBuilder {
    private String name = "Test User";
    private String email = "test@example.com";
    private UserRole role = UserRole.STANDARD;
    private boolean active = true;

    public static UserBuilder aUser() { return new UserBuilder(); }
    public UserBuilder withEmail(String email) { this.email = email; return this; }
    public UserBuilder withRole(UserRole role) { this.role = role; return this; }
    public User build() { return new User(name, email, role, active); }
}
```

FIXTURE CATEGORIES:

```
1. Fresh fixture:  created fresh before each test (@BeforeEach)
   → Maximum isolation; preferred default

2. Shared fixture: created once for all tests in a class (@BeforeAll)
   → Good for expensive setup (DB containers); requires careful isolation

3. Persistent fixture: pre-existing in the DB/file system
   → Fragile: any change to pre-existing data breaks tests
   → Avoid for automated tests; use only for exploratory testing
```

---

### 🧪 Thought Experiment

FIXTURE BLOAT — THE ANTI-PATTERN:

```java
@BeforeEach
void setup() {
    // 40 lines of setup
    // Creates 5 users, 3 orders, 2 products, 1 discount, 1 cart, 1 customer...
    // Tests only use 2 of these objects

    // Problems:
    // 1. Hard to understand: which objects does THIS test need?
    // 2. Slow: creates objects that aren't used
    // 3. Brittle: change to any object model breaks all tests
}

// Solution: minimal fixture — create only what THIS test needs
// Use @BeforeEach for shared setup; inline extra setup in each test
```

---

### 🧠 Mental Model / Analogy

> A test fixture is the **stage setting before curtain rise**: the theater crew (setup) arranges the props, sets the lighting, positions the actors. The performance (test) happens in this arranged environment. After the performance, the crew strikes the set (teardown). Each performance starts with the same arranged stage — reproducibility guaranteed.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `@BeforeEach` runs before every test to set up what the test needs. `@AfterEach` cleans up after. They ensure each test starts fresh.

**Level 2:** Keep fixtures minimal: set up only what each test class actually needs. Use Test Data Builders to create objects with sensible defaults — only set the fields relevant to the specific test. For database integration tests: use `@Transactional` rollback as teardown (automatic) rather than `@AfterEach deleteAll()` (explicit).

**Level 3:** Fixture design patterns: (1) Object Mother (a factory class with named creation methods: `UserMother.aStandardUser()`, `UserMother.anAdminUser()`); (2) Test Data Builder (fluent builder); (3) Parameterized fixtures (`@MethodSource`, `@CsvSource` for data-driven tests). Fixture vs. factory: a fixture is the specific state for a test; a factory is a reusable helper for creating test objects. The most maintainable approach: Object Mother for common scenarios + Builder for customization.

**Level 4:** The relationship between fixture complexity and design quality: a test that requires 40 lines of setup is likely testing a class that does too many things. The fixture complexity mirrors the production code complexity — a Single Responsibility Principle (SRP) violation produces complex fixtures. The refactoring hint: when fixture setup is large, the class under test should be split. Each resulting class will have a small, focused fixture.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│               JUnit 5 LIFECYCLE METHODS                  │
├──────────────────────────────────────────────────────────┤
│  @BeforeAll ────────────────────────────────────────────→│
│  │ (once per class)                                      │
│  ↓                                                      │
│  @BeforeEach ──── [test 1] ──── @AfterEach              │
│  @BeforeEach ──── [test 2] ──── @AfterEach              │
│  @BeforeEach ──── [test 3] ──── @AfterEach              │
│  ↓                                                      │
│  @AfterAll ─────────────────────────────────────────────│
│  │ (once per class)                                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Test class for OrderService:

@BeforeAll:   start Testcontainers PostgreSQL (expensive, once)
@BeforeEach:  truncate tables, create base test data (cheap, per-test)
@Test:        each test creates additional specific data with builders
@AfterEach:   (nothing — BeforeEach truncation handles cleanup)
@AfterAll:    stop Testcontainers

Test method:
  // Only the specific additional setup for THIS test
  Order order = OrderBuilder.anOrder()
    .withStatus(PENDING)
    .withTotal(100.00)
    .build();
  repo.save(order);

  // Test: confirm order
  service.confirm(order.getId());
  assertThat(repo.findById(order.getId()).get().getStatus()).isEqualTo(CONFIRMED);
```

---

### 💻 Code Example

```java
// Object Mother pattern
class OrderMother {
    public static Order aPendingOrder() {
        return Order.builder()
            .id(UUID.randomUUID())
            .customerId(UUID.randomUUID())
            .status(OrderStatus.PENDING)
            .total(BigDecimal.valueOf(99.90))
            .createdAt(Instant.now())
            .build();
    }

    public static Order aConfirmedOrder() {
        return aPendingOrder().toBuilder().status(CONFIRMED).build();
    }
}

// Test Data Builder
class OrderBuilder {
    private OrderStatus status = PENDING;
    private BigDecimal total = BigDecimal.valueOf(50.0);
    private UUID customerId = UUID.randomUUID();

    public static OrderBuilder anOrder() { return new OrderBuilder(); }
    public OrderBuilder withStatus(OrderStatus s) { this.status = s; return this; }
    public OrderBuilder withTotal(double t) { this.total = BigDecimal.valueOf(t); return this; }
    public Order build() { return new Order(UUID.randomUUID(), customerId, status, total, Instant.now()); }
}

// In test:
@Test void cancelOrder_confirmedOrder_throws() {
    Order order = OrderBuilder.anOrder().withStatus(CONFIRMED).build();
    repo.save(order);
    assertThatThrownBy(() -> service.cancel(order.getId()))
        .isInstanceOf(InvalidOrderStateException.class);
}
```

---

### ⚖️ Comparison Table

| Pattern           | Purpose               | Trade-offs                                                 |
| ----------------- | --------------------- | ---------------------------------------------------------- |
| `@BeforeEach`     | Per-test setup        | Runs before every test — keep fast                         |
| `@BeforeAll`      | Per-class setup       | One-time — good for containers; requires careful isolation |
| Object Mother     | Named factory methods | Quick for common cases; can get large                      |
| Test Data Builder | Fluent customization  | Verbose to write; highly flexible                          |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| "More shared fixture = better (less duplication)"    | Shared fixture increases coupling between tests; prefer fresh fixtures per test                   |
| "Object Mother is just a utility class"              | Object Mother encodes domain knowledge (what makes a valid pending order); it's a design artifact |
| "Fixtures should create complete, realistic objects" | Fixtures should create MINIMAL objects — only the fields relevant to the test under test          |

---

### 🚨 Failure Modes & Diagnosis

**1. Tests Fail After Unrelated Changes**

Cause: Shared `@BeforeAll` fixture is modified; many tests depend on its exact state.
**Fix:** Prefer `@BeforeEach` (fresh per-test) over `@BeforeAll` for test data. Reserve `@BeforeAll` for infrastructure setup (containers, schemas).

**2. Fixture Uses Hardcoded IDs → Parallel Test Failures**

Cause: Multiple tests insert records with `id = 1` → duplicate key violation in parallel execution.
**Fix:** Use `UUID.randomUUID()` or auto-generated IDs in all test data builders.

---

### 🔗 Related Keywords

- **Prerequisites:** Unit Test, Test Isolation
- **Related:** Test Data Management, `@BeforeEach`, Object Mother, Builder Pattern, Testcontainers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Known state set up before a test and    │
│              │ cleaned up after                        │
├──────────────┼───────────────────────────────────────────┤
│ JUnit 5      │ @BeforeEach, @AfterEach, @BeforeAll,    │
│              │ @AfterAll                               │
├──────────────┼───────────────────────────────────────────┤
│ PATTERNS     │ Object Mother, Test Data Builder        │
├──────────────┼───────────────────────────────────────────┤
│ PRINCIPLE    │ Minimal fixture: create only what       │
│              │ THIS test actually needs                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Known state in, known state out"       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Object Mother pattern was coined by Peter Schuh and Stephanie Punke (ThoughtWorks, 2003). As a codebase grows, Object Mother classes can become bloated "God factories" with hundreds of creation methods. Describe: (1) how the Object Mother and Builder patterns complement each other (Object Mother for common named scenarios, Builder for per-test customization), (2) how to use Kotlin data class `copy()` as a lightweight builder alternative, and (3) the `@ParameterizedTest` + `@MethodSource` combination for driving multiple fixture variations through the same test logic — when does this replace a Builder and when is a Builder still cleaner?

**Q2.** Spring Boot's `@TestConfiguration` and `@Bean` allow creating fixture beans at the application context level (e.g., a `TestClock` fixed to a known instant, or a `TestEmailService` that captures sent emails). Compare this approach to: (1) `@MockBean` (Mockito-based), (2) a hand-written fake injected via constructor, (3) `@TestConfiguration` providing a test-scoped bean. For each: what is the test isolation guarantee, what is the Spring context caching behavior, and what happens when you mix `@MockBean` and `@TestConfiguration` in the same test class.
