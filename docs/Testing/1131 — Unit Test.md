---
layout: default
title: "Unit Test"
parent: "Testing"
nav_order: 1131
permalink: /testing/unit-test/
number: "1131"
category: Testing
difficulty: ★☆☆
depends_on: Functions, Classes, Methods
used_by: TDD, Test Pyramid, CI-CD
related: Integration Test, Mocking, Assertions, Test Coverage
tags:
  - testing
  - fundamentals
  - tdd
  - quality
---

# 1131 — Unit Test

⚡ TL;DR — A unit test verifies a single function or class in isolation, with dependencies replaced by mocks or stubs, running in milliseconds with no external systems.

| #1131           | Category: Testing                                    | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Functions, Classes, Methods                          |                 |
| **Used by:**    | TDD, Test Pyramid, CI-CD                             |                 |
| **Related:**    | Integration Test, Mocking, Assertions, Test Coverage |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You change a single calculation method in a 50,000-line codebase. To verify it works, you deploy to staging, run the full application, manually navigate to the feature, and check the result. This takes 20 minutes. You find a bug, fix it, repeat. Each change requires 20 minutes of feedback. Developers avoid changing code because the feedback loop is too slow. The codebase calculates.

THE BREAKING POINT:
To refactor with confidence, you need feedback in seconds — before deployment, before integration, before the browser. Unit tests make each function independently verifiable: you call it directly with controlled inputs, assert the output, and get a result in 10ms. Change a function → run its tests → pass/fail in 50ms. Refactor freely, verify instantly.

THE INVENTION MOMENT:
Kent Beck's SUnit (Smalltalk, 1994) and its Java port JUnit (1997) formalised the unit test pattern: Arrange (set up), Act (execute), Assert (verify). The framework pattern — test runner discovers test classes, isolates each test, reports pass/fail — became the model for every modern testing framework.

### 📘 Textbook Definition

A **unit test** is an automated test that verifies the behaviour of a single **unit** of code — typically a function, method, or class — in isolation from its dependencies. "Isolation" means external dependencies (databases, HTTP services, file systems, time) are replaced with **test doubles** (mocks, stubs, fakes). A unit test must be **FAST** (<100ms), **Isolated** (no shared state between tests), **Repeatable** (same result regardless of environment), **Self-checking** (pass/fail without human judgment), and **Timely** (written at development time). These properties are sometimes summarised as **FIRST** principles.

### ⏱️ Understand It in 30 Seconds

**One line:**
Unit test = call a function with known inputs → assert the output matches expectation, with no databases or network involved.

**One analogy:**

> Testing each component of a car separately before assembly: test the engine on a bench (not in the car), test the brakes on a rig, test the electronics in isolation. Unit tests are bench tests for code. Integration tests are assembly tests. End-to-end tests are test drives.

**One insight:**
A unit test that requires a running database is not a unit test — it's an integration test wearing unit test clothes. The key word is "isolation." Speed (< 100ms) is the indicator: if it's slow, something external is involved.

### 🔩 First Principles Explanation

UNIT TEST STRUCTURE (Arrange-Act-Assert):

```java
// ARRANGE: set up inputs and dependencies
User user = new User("alice", "alice@example.com");
PricingService pricing = mock(PricingService.class);
when(pricing.getDiscount(user)).thenReturn(0.10); // 10% discount

OrderService orderService = new OrderService(pricing);

// ACT: call the unit under test
double price = orderService.calculatePrice(user, 100.0);

// ASSERT: verify the output
assertEquals(90.0, price, 0.001);
verify(pricing).getDiscount(user); // verify interaction
```

WHAT MAKES A GOOD UNIT:

- One logical concept per test (not "test all of OrderService")
- Test the contract (input → expected output), not the implementation
- Boundary cases: null input, empty list, zero, max value, negative
- One reason to fail: if test breaks, exactly one thing is wrong

THE TRADE-OFFS:
Gain: Millisecond feedback; safe refactoring; tests as documentation.
Cost: Mocking can hide integration bugs; over-mocking leads to tests that pass but production breaks; maintaining tests as code evolves has cost.

### 🧪 Thought Experiment

WHAT IS THE "UNIT"?

```
Option A (too small): test each line individually
  → Tests are fragile, test implementation not behavior
  → Any internal refactor breaks tests

Option B (right size): test each public method
  → Tests verify behavior, not implementation
  → Internal refactors don't break tests if behavior unchanged

Option C (too large): test entire service class with real DB
  → Slow (seconds), not a unit test
  → Failures could be caused by DB, network, data state

Rule: unit = the smallest piece of code with testable behavior
Usually: one public method; sometimes: one class
Never: crosses a process boundary
```

### 🧠 Mental Model / Analogy

> A unit test is a spec sheet: "this function, given input X, should produce output Y." When you write the function, you implement the spec. When you refactor, you verify you still meet the spec. The test IS the spec, expressed as executable code.

> The mock/stub is a stand-in actor: if your function needs a database, the test uses a "mock database" that returns predetermined answers — like filming a scene with a stand-in instead of the real VIP.

### 📶 Gradual Depth — Four Levels

**Level 1:** A unit test automatically checks that a small piece of code (a function) produces the right answer. You write a test once; it runs thousands of times, instantly, every time you make a change.

**Level 2:** Use JUnit 5 + Mockito. Follow AAA (Arrange-Act-Assert). Mock external dependencies. Keep tests FIRST. Aim for one assertion per test concept. Name tests: `methodName_scenarioDescription_expectedResult()`.

**Level 3:** Tests should verify behavior not implementation. Avoid `@InjectMocks` with complex dependency chains — prefer constructor injection for easier mocking. Use `@ParameterizedTest` for boundary value analysis. Test naming conventions affect discoverability: `given_when_then` vs `should_when`. Coverage metric: aim for behavior coverage (all branches), not line coverage.

**Level 4:** The "unit" definition is contentious: "London school" (sociable unit tests) mocks all collaborators; "Chicago school" (classical unit tests) only mocks infrastructure (DB, HTTP) and allows real collaborators. The right boundary: mock at architectural boundaries (IO, network, time), not at every class boundary. This produces tests that are fast (no IO) but also resilient to refactoring (you can change internal class structure without breaking tests).

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│               UNIT TEST EXECUTION FLOW               │
├──────────────────────────────────────────────────────┤
│  JUnit 5 discovers @Test methods via classpath scan  │
│  For each @Test:                                     │
│    1. @BeforeEach → setup                           │
│    2. Execute test method                            │
│    3. Assertions checked (AssertJ, JUnit assertions) │
│    4. @AfterEach → teardown                         │
│    5. Report PASS / FAIL / ERROR                    │
│                                                      │
│  Test isolation: new instance per @Test (JUnit 5)   │
│  Parallel execution: @Execution(CONCURRENT)         │
│                                                      │
│  Mockito: generates dynamic proxy implementing      │
│  the interface; intercepts method calls;             │
│  returns configured stubs or records invocations    │
└──────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

TDD CYCLE (Red-Green-Refactor):

```
1. RED: Write failing test first
   @Test
   void calculateDiscount_premiumUser_returns20Percent() {
       var user = new User(UserType.PREMIUM);
       var service = new DiscountService();
       assertEquals(0.20, service.calculate(user));  // FAILS (method not implemented)
   }

2. GREEN: Write minimum code to make test pass
   public double calculate(User user) {
       return user.isPremium() ? 0.20 : 0.0;
   }
   // Test PASSES

3. REFACTOR: Improve code without breaking test
   public double calculate(User user) {
       return USER_TYPE_DISCOUNTS.getOrDefault(user.getType(), 0.0);
   }
   // Test still PASSES (behavior unchanged)
```

### 💻 Code Example

```java
// Production class
@Service
public class OrderPricingService {
    private final DiscountRepository discountRepo;
    private final TaxCalculator taxCalc;

    public OrderPricingService(DiscountRepository discountRepo,
                               TaxCalculator taxCalc) {
        this.discountRepo = discountRepo;
        this.taxCalc = taxCalc;
    }

    public BigDecimal calculateTotal(Order order) {
        BigDecimal discount = discountRepo.getDiscount(order.getUserId());
        BigDecimal subtotal = order.getSubtotal().multiply(
            BigDecimal.ONE.subtract(discount));
        return taxCalc.applyTax(subtotal, order.getRegion());
    }
}

// Unit test (JUnit 5 + Mockito)
@ExtendWith(MockitoExtension.class)
class OrderPricingServiceTest {

    @Mock DiscountRepository discountRepo;
    @Mock TaxCalculator taxCalc;
    @InjectMocks OrderPricingService sut;  // system under test

    @Test
    void calculateTotal_withDiscount_appliesDiscountBeforeTax() {
        // Arrange
        Order order = Order.builder()
            .userId("user1").subtotal(new BigDecimal("100.00"))
            .region("US").build();
        when(discountRepo.getDiscount("user1")).thenReturn(new BigDecimal("0.10"));
        when(taxCalc.applyTax(new BigDecimal("90.00"), "US"))
            .thenReturn(new BigDecimal("96.30"));

        // Act
        BigDecimal total = sut.calculateTotal(order);

        // Assert
        assertThat(total).isEqualByComparingTo("96.30");
        verify(taxCalc).applyTax(new BigDecimal("90.00"), "US");
    }

    @Test
    void calculateTotal_noDiscount_fullPricePlusTax() {
        Order order = Order.builder()
            .userId("new-user").subtotal(new BigDecimal("50.00"))
            .region("EU").build();
        when(discountRepo.getDiscount("new-user")).thenReturn(BigDecimal.ZERO);
        when(taxCalc.applyTax(new BigDecimal("50.00"), "EU"))
            .thenReturn(new BigDecimal("60.00"));

        assertThat(sut.calculateTotal(order)).isEqualByComparingTo("60.00");
    }
}
```

### ⚖️ Comparison Table

| Test Type   | Scope              | Speed    | Dependencies    | Confidence            |
| ----------- | ------------------ | -------- | --------------- | --------------------- |
| **Unit**    | One function/class | <100ms   | Mocked          | Low–medium (isolated) |
| Integration | Multiple layers    | 1–30s    | Real DB/service | High (real behavior)  |
| E2E         | Full user flow     | 10s–5min | Full stack      | Very high (reality)   |
| Contract    | Service boundary   | 1–10s    | Pact framework  | Medium (API contract) |

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| "100% coverage = no bugs"              | Coverage measures lines executed, not all behaviors tested; you can have 100% coverage with wrong assertions             |
| "More mocking = better isolation"      | Over-mocking produces tests that verify mock behavior, not real behavior; mock at architectural boundaries only          |
| "Unit tests are slow to write"         | TDD discipline: tests as fast as possible; the slow part is writing code without clear requirements (TDD forces clarity) |
| "Unit tests replace integration tests" | Unit tests verify units in isolation; integration tests verify units working together; both are required                 |

### 🚨 Failure Modes & Diagnosis

**1. Test Passes Locally, Fails in CI**

Cause: Test depends on system state (time, locale, file system, random seed, test order).
Fix: Use `@MockBean Clock`, fixed seeds, `@TempDir`, `@TestMethodOrder(OrderAnnotation.class)` with independent tests.

**2. Tests Break on Every Refactor**

Cause: Tests verify internal implementation details (private method calls, field values via reflection).
Fix: Only test public API. Use `verify()` sparingly — only for critical side effects (email sent, payment charged).

### 🔗 Related Keywords

- **Prerequisites:** Functions, Classes, Methods, Assertions
- **Builds on:** Mocking, Stubbing, TDD, Test Pyramid
- **Alternatives:** Integration Test (real dependencies), Contract Test (API boundaries)

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automated test of one unit (function/    │
│              │ class) in isolation from dependencies    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Fast feedback (ms) enables safe          │
│              │ refactoring and living documentation     │
├──────────────┼───────────────────────────────────────────┤
│ STRUCTURE    │ Arrange → Act → Assert (AAA)             │
├──────────────┼───────────────────────────────────────────┤
│ PROPERTIES   │ FIRST: Fast, Isolated, Repeatable,       │
│              │ Self-checking, Timely                    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Isolation = speed; but real integration  │
│              │ bugs only caught by integration tests    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Input X → output Y, no DB, in 10ms"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Integration Test → TDD → Test Pyramid    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** JUnit 5's `@ExtendWith(MockitoExtension.class)` creates a new test instance per test method (lifecycle `PER_METHOD`). If you change to `@TestInstance(PER_CLASS)`, the same instance is shared across all test methods — meaning mocks are shared too. Describe the exact bug that would occur in the `OrderPricingServiceTest` above if `PER_CLASS` lifecycle was used without calling `Mockito.reset()` between tests, and explain why the second test might pass or fail depending on execution order.

**Q2.** The "Test Doubles" taxonomy (Meszaros, 2007) distinguishes: Dummy (passed but never used), Fake (working implementation, e.g., in-memory DB), Stub (returns predetermined values), Spy (records calls, partial mock), Mock (pre-programmed with expectations). Mockito's `mock()` creates a Mock; `spy()` creates a Spy. For the `OrderPricingService` above: if `TaxCalculator` is a Spy wrapping a real implementation, and the real `applyTax` makes an HTTP call to a tax API — describe the specific failure mode in CI (no network), how you would detect it in a test run, and why the London school would say this is the wrong boundary to mock at.
