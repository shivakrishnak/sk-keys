---
layout: default
title: "Mocking"
parent: "Testing"
nav_order: 1144
permalink: /testing/mocking/
number: "1144"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, Dependency Injection, Interfaces
used_by: Developers, TDD Practitioners
related: Stubbing, Faking, Spying, Mockito, Test Double, Dependency Injection
tags:
  - testing
  - mocking
  - test-doubles
  - unit-testing
---

# 1144 — Mocking

⚡ TL;DR — A mock is a test double that replaces a real dependency, verifies that specific interactions (method calls) occur, and controls what values the dependency returns — enabling unit tests to run without real databases, APIs, or external services.

| #1144           | Category: Testing                                                    | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, Dependency Injection, Interfaces                          |                 |
| **Used by:**    | Developers, TDD Practitioners                                        |                 |
| **Related:**    | Stubbing, Faking, Spying, Mockito, Test Double, Dependency Injection |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A `PaymentService` calls `StripePaymentGateway.charge(card, amount)`. To unit test `PaymentService`, you need: (1) a real Stripe API key, (2) internet access, (3) a real test card number, (4) Stripe's test server to be up. Every unit test makes a real network call. Tests are: slow (500ms+ per test), flaky (network failures), expensive (API call limits), and non-deterministic (real service behavior can change). Without mocking, unit tests are actually integration tests, and the line between them disappears.

THE ISOLATION PRINCIPLE:
A unit test tests ONE unit in isolation. When `PaymentService.charge()` is tested with a real `StripeGateway`, you're simultaneously testing: PaymentService logic + network code + HTTP client + Stripe API behavior. When the test fails, is it the PaymentService logic or the Stripe API that's wrong? Mocking isolates the unit.

### 📘 Textbook Definition

A **mock** is a test double (a replacement for a real object in tests) that: (1) can be programmed to **return specific values** when specific methods are called (stubbing), (2) **records all interactions** (method calls, arguments, call order), (3) **verifies** at the end of the test that expected interactions actually occurred. Mocks answer: "Did my code call the right methods on its dependencies, with the right arguments, the right number of times?" Mocking frameworks (Mockito for Java, Jest mocks for JavaScript, unittest.mock for Python) generate mock objects at runtime using reflection/proxies.

### ⏱️ Understand It in 30 Seconds

**One line:**
Mock = fake dependency that records interactions and returns scripted responses.

**One analogy:**

> Testing a pilot in a flight simulator: the simulator is a mock of the real aircraft. It returns realistic responses to inputs (stubbing), and the instructor can verify the pilot performed the right sequence of actions (verification). The test doesn't require a real plane, real fuel, or real passengers.

### 🔩 First Principles Explanation

TEST DOUBLE TAXONOMY (Gerard Meszaros):

```
Dummy:  passed but never used (filling parameter lists)
Stub:   returns pre-programmed responses; no interaction verification
Fake:   working implementation but unsuitable for production (in-memory DB)
Mock:   pre-programmed + verifies interactions occurred
Spy:    wraps real object; records calls to a real implementation
```

MOCKITO EXAMPLE — complete mock lifecycle:

```java
// ARRANGE: create mock and program its behavior (stubbing)
PaymentGateway gateway = mock(PaymentGateway.class);
when(gateway.charge(any(Card.class), eq(100.0)))
    .thenReturn(new PaymentResult("txn-123", SUCCESS));

// ACT: call the code under test
PaymentService service = new PaymentService(gateway);
Receipt receipt = service.processPayment(testCard, 100.0);

// ASSERT: verify the result
assertThat(receipt.getTransactionId()).isEqualTo("txn-123");

// VERIFY: confirm interactions happened correctly
verify(gateway).charge(testCard, 100.0);          // called exactly once
verify(gateway, never()).refund(any(), anyDouble()); // refund NOT called
verifyNoMoreInteractions(gateway);                 // no other calls
```

WHEN TO MOCK:

```
✓ Mock: external services (Stripe, Twilio, S3)
✓ Mock: database repositories (for service-layer unit tests)
✓ Mock: time sources (Clock) — for deterministic time-based logic
✓ Mock: email senders, notification services
✗ Don't mock: value objects, simple utilities (no external state)
✗ Don't mock: the class under test itself
✗ Don't mock: simple collaborators with no external dependencies
   (over-mocking makes tests fragile: test knows too much about implementation)
```

### 🧪 Thought Experiment

OVER-MOCKING — THE FRAGILE TEST PROBLEM:

```java
// Service code:
public Order createOrder(Cart cart) {
    validateCart(cart);                        // private method
    Order order = orderRepository.save(new Order(cart));
    emailService.sendConfirmation(order);
    inventoryService.reserveItems(cart.getItems());
    return order;
}

// Over-mocked test (mocks every internal collaborator):
@Test
void createOrder() {
    when(orderRepository.save(any())).thenReturn(savedOrder);
    when(emailService.sendConfirmation(any())).thenReturn(true);
    when(inventoryService.reserveItems(any())).thenReturn(true);

    service.createOrder(cart);

    verify(orderRepository).save(any());
    verify(emailService).sendConfirmation(savedOrder);
    verify(inventoryService).reserveItems(cart.getItems());
}

// This test is a carbon copy of the implementation.
// If you refactor (rename a method, change order), test breaks.
// Test verifies structure, not behavior.
// → Mock only external dependencies; use real objects for internal collaborators.
```

### 🧠 Mental Model / Analogy

> A mock is like a **contract-enforcing test actor**: you hire an actor to play "the Stripe API" in your test. You hand them a script ("when asked to charge $100, say success"). After the scene, you check the actor's notes to verify they received the right cues from the code under test ("was charge() called exactly once with $100?"). The goal is to isolate the code under test from real external complexity.

### 📶 Gradual Depth — Four Levels

**Level 1:** A mock is a fake version of a dependency (like a fake Stripe API) that your code uses in tests. You control what it returns, and you can check what your code called on it.

**Level 2:** Use Mockito in Spring Boot tests: `@MockBean` replaces the real bean with a mock in the Spring context. `when(...).thenReturn(...)` programs the response. `verify(...)` checks interactions. Key rule: mock external dependencies (repositories, external APIs, email services), not domain objects.

**Level 3:** Mock vs Stub distinction in practice: if your test only calls `when().thenReturn()` without any `verify()`, you're using the mock as a stub (you don't care about interactions, only return values). If your test has `verify()`, you're using mock behavior (you care that specific interactions occurred). This distinction matters: over-verification (verifying every method call) creates tests that are too tied to implementation details — refactoring breaks tests without changing behavior.

**Level 4:** The London School vs. Detroit School TDD debate: London School (mockist) uses mocks extensively — every collaborator is mocked to achieve complete isolation; tests verify interaction between objects. Detroit School (classicist) prefers real objects where possible — over-mocking creates tests that know too much about implementation. The classicist concern: "if you mock the order repository, you're testing that your code calls the repository correctly, not that the repository actually works." The consensus: mock at architectural boundaries (service → database, service → external API), use real objects within the same architectural layer.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│               MOCKITO INTERNALS                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  mock(PaymentGateway.class)                             │
│  → ByteBuddy/cglib generates a subclass at runtime      │
│  → All methods override → delegate to MockHandler       │
│                                                          │
│  when(gateway.charge(any(), eq(100.0)))                 │
│  → Records "when charge called with these args"         │
│  → .thenReturn() binds the response                     │
│                                                          │
│  Production code: gateway.charge(card, 100.0)           │
│  → MockHandler intercepts call                          │
│  → Finds matching stub → returns PaymentResult("txn-123")│
│  → Records interaction (args, count)                    │
│                                                          │
│  verify(gateway).charge(testCard, 100.0)                │
│  → Checks recorded interactions                         │
│  → Exactly 1 call with these args → PASS               │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

```
Feature: PaymentService sends email confirmation after successful payment

Unit test (with mocking):
  1. Mock: PaymentGateway → returns success
  2. Mock: EmailService → records calls
  3. Mock: AuditLogger → records calls

  4. Call: service.processPayment(card, 100.0)

  5. Assert: receipt is non-null and has transaction ID
  6. Verify: gateway.charge(card, 100.0) called once
  7. Verify: emailService.sendConfirmation(receipt) called once
  8. Verify: auditLogger.log() called once with "PAYMENT_SUCCESS"

Result: PaymentService logic is tested in complete isolation
  → No network calls
  → Runs in < 10ms
  → Deterministic (no real external state)

Integration test (separate, without mocking):
  → Uses Testcontainers (real DB)
  → Uses WireMock (mock Stripe HTTP server)
  → Tests PaymentService + Repository interaction
```

### 💻 Code Example

```java
// Spring Boot test with @MockBean
@ExtendWith(MockitoExtension.class)
class PaymentServiceTest {

    @Mock
    private PaymentGateway gateway;
    @Mock
    private EmailService emailService;
    @InjectMocks  // injects mocks into PaymentService constructor
    private PaymentService service;

    @Test
    void processPayment_success_sendsConfirmationEmail() {
        // ARRANGE
        Card card = new Card("4111111111111111", "12/25", "123");
        PaymentResult gatewayResult = new PaymentResult("txn-456", SUCCESS);
        when(gateway.charge(card, 50.0)).thenReturn(gatewayResult);

        // ACT
        Receipt receipt = service.processPayment(card, 50.0);

        // ASSERT outcome
        assertThat(receipt.getTransactionId()).isEqualTo("txn-456");

        // VERIFY interactions
        verify(gateway).charge(card, 50.0);
        verify(emailService).sendConfirmation(eq(card.getHolderEmail()), argThat(r ->
            r.getTransactionId().equals("txn-456")));
    }

    @Test
    void processPayment_gatewayDeclines_throwsPaymentException() {
        when(gateway.charge(any(), anyDouble()))
            .thenThrow(new GatewayException("Card declined"));

        assertThatThrownBy(() -> service.processPayment(testCard, 100.0))
            .isInstanceOf(PaymentException.class)
            .hasMessage("Payment failed: Card declined");

        verifyNoInteractions(emailService);  // email should NOT be sent on failure
    }
}
```

### ⚖️ Comparison Table

| Test Double | Returns Values       | Verifies Calls | Real Logic       |
| ----------- | -------------------- | -------------- | ---------------- |
| Dummy       | No (null/empty)      | No             | No               |
| Stub        | Yes (programmed)     | No             | No               |
| **Mock**    | Yes (programmed)     | **Yes**        | No               |
| Spy         | Real (or programmed) | Yes            | **Yes**          |
| Fake        | Real (lightweight)   | No             | Yes (simplified) |

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                    |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| "Mock = stub"                              | Mocks verify interactions; stubs only return values. Mockito can do both.                                  |
| "Always mock all dependencies"             | Over-mocking creates brittle tests tied to implementation; mock at boundaries only                         |
| "If I mock everything, tests are fast"     | True, but tests may pass when code is wrong (mock hides real interaction issues)                           |
| "Mocks make integration tests unnecessary" | Mocks confirm your code calls dependencies correctly; integration tests confirm the real dependencies work |

### 🚨 Failure Modes & Diagnosis

**1. Tests Pass But Feature Is Broken in Production**

Cause: Mock was set up incorrectly (wrong return type, wrong behavior) so tests verify against a fantasy version of the dependency.
Fix: Supplement unit tests with integration tests against real (or WireMock) dependencies. Use contract tests (Pact) to verify mock matches real API behavior.

**2. Every Refactoring Breaks 20 Tests**

Cause: Tests over-verify every internal interaction; mock `verify()` on private collaborators.
Fix: Verify observable behavior (outputs, returned values) not internal interactions. Remove `verify()` calls that aren't testing meaningful contract obligations.

### 🔗 Related Keywords

- **Prerequisites:** Unit Test, Dependency Injection, Interfaces
- **Builds on:** Stubbing, Spying, Faking, Mockito, WireMock
- **Related:** Test Isolation, Test Doubles, TDD, Contract Testing

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Replace real dependency with scripted    │
│              │ fake that records interactions           │
├──────────────┼───────────────────────────────────────────┤
│ WHEN         │ External services, databases, time,      │
│              │ anything slow/non-deterministic          │
├──────────────┼───────────────────────────────────────────┤
│ JAVA TOOL    │ Mockito: @Mock, when(), verify()         │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ Mock at boundaries (external deps);      │
│              │ don't mock what you own                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fake the dependency; verify the call"   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Mockito's `@InjectMocks` uses either constructor injection, setter injection, or field injection (in that priority order) to inject mocks. Field injection (`@InjectMocks` with no constructor) is convenient for tests but has a hidden danger: it will silently succeed even if there's no matching field, meaning the real object (not mock) is used. Describe: (1) why constructor injection is preferred in both production code AND tests, (2) how to verify that Mockito actually injected your mock (not a real object), and (3) the `strictMocks()` extension and why Mockito introduced it (catches unused stubs and unnecessary stubbing).

**Q2.** The "mock only what you own" rule from Growing Object-Oriented Software (Freeman & Pryce): don't mock types you don't own (third-party libraries, frameworks). The reason: if the third-party API changes behavior, your mock still returns the old behavior — tests pass but code is broken. Compare: (1) mocking `HttpClient` directly vs. wrapping it in your own `HttpGateway` interface (then mocking the interface you own); (2) how Pact contract tests address this gap (verify that your mock's behavior matches the real API); (3) when Testcontainers is better than mocking (when you need to verify actual SQL, actual Redis behavior, not just that the method was called).
