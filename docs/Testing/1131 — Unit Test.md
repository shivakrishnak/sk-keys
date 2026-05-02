---
layout: default
title: "Unit Test"
parent: "Testing"
nav_order: 1131
permalink: /testing/unit-test/
number: "1131"
category: Testing
difficulty: ★☆☆
depends_on: "Java Language, OOP"
used_by: "Integration Test, TDD, JUnit, Mockito"
tags: #testing, #unit-test, #tdd, #junit, #isolation, #fast-feedback
---

# 1131 — Unit Test

`#testing` `#unit-test` `#tdd` `#junit` `#isolation` `#fast-feedback`

⚡ TL;DR — A **unit test** verifies a single unit of code (a method, class, or small component) in isolation from its dependencies. Dependencies are replaced with test doubles (mocks/stubs). Unit tests are fast (milliseconds), numerous (hundreds in a project), and run on every code change. They give the fastest feedback cycle and form the base of the testing pyramid: many unit tests → fewer integration tests → even fewer E2E tests.

| #1131           | Category: Testing                     | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | Java Language, OOP                    |                 |
| **Used by:**    | Integration Test, TDD, JUnit, Mockito |                 |

---

### 📘 Textbook Definition

**Unit test**: an automated test that verifies the behavior of a small, isolated unit of code — typically a single class or method — with all external dependencies replaced by test doubles (mocks, stubs, fakes, spies). Characteristics: (1) **Fast**: run in milliseconds (no I/O, no network, no database); (2) **Isolated**: the unit under test has no real external dependencies — every collaborator is substituted; (3) **Deterministic**: same input → same output, always, on any machine; (4) **Independent**: each test is self-contained, with no shared state between tests; (5) **Readable**: the test describes the expected behavior in code — it's both a verification and a specification. In Java: JUnit 5 as the test framework, Mockito for mocking. F.I.R.S.T principles: Fast, Independent, Repeatable, Self-validating, Timely. Testing pyramid: unit tests form the large base (most tests), because they're cheap to write and fast to run. Goal: test every business rule, algorithm, and conditional in isolation to pinpoint exactly what broke when a test fails.

---

### 🟢 Simple Definition (Easy)

A unit test checks one small piece of your code — like testing that a single method returns the right answer. No database, no network, no Spring context. Just: "if I call `calculateTax(100.0)`, does it return `10.0`?" Fast (runs in 1ms), cheap to write, runs thousands of times per day. When a unit test fails, you know exactly which method has a bug — no detective work needed.

---

### 🔵 Simple Definition (Elaborated)

Unit tests verify your code's logic by testing units in isolation:

- **What's a "unit"**: typically one class or one method. In practice, a small cluster of closely related classes that form a logical unit (e.g., a service class + its supporting value objects).
- **Isolation**: if `OrderService` depends on `OrderRepository` (a database interface), you mock the repository. The test verifies `OrderService`'s logic without needing a real database.
- **Test doubles**: mocks (verify interactions), stubs (return pre-configured responses), fakes (lightweight implementations — in-memory repo), spies (partial mocks: real object with some methods overridden).

**Why isolation matters**: without isolation, a test failure could be caused by the unit under test OR by any dependency. Isolated tests pinpoint the exact source of the failure. This is why the "unit" in unit test means "testable in isolation" — not "one line of code."

---

### 🔩 First Principles Explanation

```java
// UNIT TEST ANATOMY (JUnit 5 + Mockito)

// Unit under test:
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final EmailService emailService;

    public OrderService(OrderRepository repo, PaymentGateway payment, EmailService email) {
        this.orderRepository = repo;
        this.paymentGateway = payment;
        this.emailService = email;
    }

    public Order placeOrder(Cart cart, PaymentInfo payment) {
        if (cart.isEmpty()) {
            throw new IllegalArgumentException("Cart cannot be empty");
        }

        Order order = Order.from(cart);
        PaymentResult result = paymentGateway.charge(payment, order.getTotal());

        if (!result.isSuccess()) {
            throw new PaymentException("Payment failed: " + result.getError());
        }

        order.markAsPaid();
        orderRepository.save(order);
        emailService.sendConfirmation(order);

        return order;
    }
}

// UNIT TEST:
@ExtendWith(MockitoExtension.class)   // JUnit 5 Mockito integration
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;    // mock dependency

    @Mock
    private PaymentGateway paymentGateway;      // mock dependency

    @Mock
    private EmailService emailService;          // mock dependency

    @InjectMocks
    private OrderService orderService;          // unit under test (dependencies injected)

    // GIVEN-WHEN-THEN (AAA: Arrange-Act-Assert) pattern

    @Test
    @DisplayName("should place order successfully when payment succeeds")
    void placeOrder_success() {
        // ARRANGE (Given)
        Cart cart = CartBuilder.aCart().withItem("Widget", 99.99).build();
        PaymentInfo payment = new PaymentInfo("4242-4242-4242-4242");

        // Configure mock behavior (stub)
        when(paymentGateway.charge(payment, 99.99))
            .thenReturn(PaymentResult.success("txn-123"));

        // ACT (When)
        Order result = orderService.placeOrder(cart, payment);

        // ASSERT (Then)
        assertThat(result.getStatus()).isEqualTo(OrderStatus.PAID);
        assertThat(result.getTotal()).isEqualTo(99.99);

        // VERIFY interactions (mock assertions)
        verify(orderRepository).save(result);           // was save() called?
        verify(emailService).sendConfirmation(result);  // was email sent?
    }

    @Test
    @DisplayName("should throw IllegalArgumentException when cart is empty")
    void placeOrder_emptyCart_throwsException() {
        // ARRANGE
        Cart emptyCart = Cart.empty();
        PaymentInfo payment = new PaymentInfo("4242-4242-4242-4242");

        // ACT + ASSERT
        assertThatThrownBy(() -> orderService.placeOrder(emptyCart, payment))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("Cart cannot be empty");

        // VERIFY no interactions with payment or email (early exit)
        verifyNoInteractions(paymentGateway, emailService);
    }

    @Test
    @DisplayName("should throw PaymentException when payment fails")
    void placeOrder_paymentFails_throwsException() {
        // ARRANGE
        Cart cart = CartBuilder.aCart().withItem("Widget", 99.99).build();
        PaymentInfo payment = new PaymentInfo("invalid-card");

        when(paymentGateway.charge(payment, 99.99))
            .thenReturn(PaymentResult.failure("Insufficient funds"));

        // ACT + ASSERT
        assertThatThrownBy(() -> orderService.placeOrder(cart, payment))
            .isInstanceOf(PaymentException.class)
            .hasMessageContaining("Insufficient funds");

        // Order should NOT be saved if payment fails
        verify(orderRepository, never()).save(any());
    }

    @Test
    @DisplayName("should not send email if order save fails")
    void placeOrder_saveFails_noEmail() {
        // ARRANGE
        Cart cart = CartBuilder.aCart().withItem("Widget", 99.99).build();
        PaymentInfo payment = new PaymentInfo("4242");

        when(paymentGateway.charge(any(), anyDouble()))
            .thenReturn(PaymentResult.success("txn-456"));
        doThrow(new RuntimeException("DB down"))
            .when(orderRepository).save(any());

        // ACT + ASSERT
        assertThatThrownBy(() -> orderService.placeOrder(cart, payment))
            .isInstanceOf(RuntimeException.class);

        verifyNoInteractions(emailService);
    }
}
```

```
TESTING PYRAMID:

       /\
      /  \
     / E2E \      ← Few (slow: full browser, full stack, minutes)
    /────────\
   /Integration\  ← Some (moderate: Spring context, DB, seconds)
  /──────────────\
 /    Unit Tests   \ ← MANY (fast: no I/O, milliseconds)
/────────────────────\

Rule of thumb: 70% unit / 20% integration / 10% E2E (varies by project)

FAST FEEDBACK CYCLE:
  Code change → mvn test → unit tests run (< 30 seconds) → immediate feedback
  vs
  Code change → mvn verify → full suite (30 minutes) → slow feedback

F.I.R.S.T PRINCIPLES:
  Fast        → run in milliseconds; 1000 tests in < 1 minute
  Independent → no shared state between tests; each test is self-contained
  Repeatable  → same result every run (no randomness, no time dependencies)
  Self-validating → pass/fail automatically; no human inspection needed
  Timely      → written before or with the code (TDD); not after
```

---

### ❓ Why Does This Exist (Why Before What)

Code without automated tests is difficult to change safely — every refactoring risks introducing bugs that may go undetected until production. Unit tests create a safety net: change the implementation → run unit tests → immediate feedback if behavior changed unexpectedly. They also act as executable documentation: a well-named unit test describes the expected behavior of a method better than comments. The speed of unit tests (milliseconds each) makes them practical to run on every code change, providing the tightest feedback loop possible.

---

### 🧠 Mental Model / Analogy

> **Unit tests are like circuit testing in electronics**: when assembling a complex circuit board (software system), you test each individual component (resistor, capacitor, IC chip) in isolation before assembling the board. If a capacitor fails its test, you know exactly which component is faulty — not "somewhere on the board." Integrating untested components and then testing the whole board makes fault diagnosis exponentially harder. Unit tests are the component-level tests; integration tests are the board-level tests.

---

### 🔄 How It Connects (Mini-Map)

```
Need fast, isolated verification of individual logic units
        │
        ▼
Unit Test ◄── (you are here)
(fast, isolated, deterministic; mocks replace dependencies)
        │
        ├── Integration Test: tests units working together (with real dependencies)
        ├── TDD: write unit tests FIRST; let them drive the implementation
        ├── Mockito: the mocking framework used to isolate units
        └── CI-CD Pipeline: unit tests run on every commit (fast gate)
```

---

### 💻 Code Example

```java
// Pure unit test: no mocks needed (no dependencies)
class TaxCalculatorTest {

    private TaxCalculator calculator = new TaxCalculator();

    @ParameterizedTest
    @CsvSource({
        "100.0, US, 10.0",
        "100.0, EU, 20.0",
        "100.0, UK, 17.5",
        "0.0, US, 0.0"
    })
    @DisplayName("should calculate correct tax for each region")
    void calculateTax(double amount, String region, double expectedTax) {
        double tax = calculator.calculate(amount, region);

        assertThat(tax)
            .as("Tax for %s in %s", amount, region)
            .isCloseTo(expectedTax, within(0.001));
    }

    @Test
    void calculateTax_negativeAmount_throwsException() {
        assertThatThrownBy(() -> calculator.calculate(-1.0, "US"))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 100% code coverage means the code is fully tested              | Coverage measures which lines were EXECUTED, not which behaviors were VERIFIED. You can have 100% coverage with tests that have no assertions. Coverage is a useful metric for finding untested code, but it's not a quality metric. A focused test suite with 80% meaningful coverage > 100% coverage with shallow tests.      |
| Unit tests should test every method, including getters/setters | Test behaviors, not implementations. Simple getters/setters generated by Lombok have no logic — testing them adds noise with no value. Test: business rules, conditional logic, error cases, boundary conditions. Don't test: getters, setters, constructors that just assign fields.                                           |
| Mocking is always the right approach for unit tests            | For pure functions (no I/O, no side effects), no mocking is needed. Over-mocking leads to tests that verify the implementation (how it's done) rather than the behavior (what it does) — making refactoring break tests unnecessarily. Use mocks only when a real collaborator is slow, non-deterministic, or has side effects. |

---

### 🔗 Related Keywords

- `Integration Test` — tests multiple units together with real dependencies
- `TDD` (Test-Driven Development) — write unit tests before implementation
- `Mockito` — the Java mocking framework used in unit tests
- `JUnit 5` — the Java test framework for writing and running unit tests
- `Testing Pyramid` — unit tests form the base (most tests, fastest)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ UNIT TEST CHARACTERISTICS:                              │
│ • Fast: milliseconds (no I/O, no DB, no network)       │
│ • Isolated: dependencies replaced with mocks           │
│ • Deterministic: same result every run                 │
│ • Independent: no shared state between tests           │
│                                                         │
│ STRUCTURE: Arrange-Act-Assert (Given-When-Then)         │
│ TOOLS (Java): JUnit 5 + Mockito + AssertJ              │
│ RUN: mvn test (surefire: *Test.java files)             │
│                                                         │
│ TEST THESE: business rules, conditions, error cases    │
│ SKIP THESE: getters, setters, trivial constructors     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The "should I mock or not mock?" debate is central to unit testing philosophy. The London School (mockist) TDD advocates mocking all collaborators to achieve pure isolation. The Detroit School (classicist) TDD uses real objects wherever possible, only mocking at the boundary (I/O, external systems). A test that mocks the `OrderRepository` tests `OrderService` in isolation but also tests the `OrderService`-`OrderRepository` integration implicitly through mock expectations. When you refactor — splitting `OrderService` into `OrderCreationService` and `OrderPaymentService` — mockist tests break even if behavior is unchanged. Detroit-style tests survive refactoring. What are the trade-offs? Which approach do you use for: (a) a service class with 5 collaborators, (b) a pure domain model class, (c) a class with a database dependency?

**Q2.** Unit tests are fast when they test pure logic. But many Java enterprise classes are not pure — `@Service` beans have Spring annotations, `@Transactional` methods, `@Cacheable` annotations, etc. Testing `OrderService` without Spring context means Spring AOP (`@Transactional`, `@Cacheable`) doesn't apply — the test is testing the "raw" class, not the "Spring-enhanced" version. Is this a problem? What behaviors can only be tested with a Spring context (integration test)? Where do you draw the line between what unit tests verify vs what integration tests verify in a Spring Boot application?
