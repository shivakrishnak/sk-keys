---
layout: default
title: "Test Diamond"
parent: "Testing"
nav_order: 1149
permalink: /testing/test-diamond/
number: "1149"
category: Testing
difficulty: ★★★
depends_on: Test Pyramid, Integration Test, Contract Test
used_by: Microservices Teams, API-First Teams
related: Test Pyramid, Test Honeycomb, Contract Test, API Testing, Microservices
tags:
  - testing
  - strategy
  - microservices
  - test-diamond
---

# 1149 — Test Diamond

⚡ TL;DR — The Test Diamond is an alternative to the Test Pyramid for API-centric and microservices architectures: fewer unit tests, a large middle layer of service/integration tests (especially contract tests), and few E2E tests — reflecting that the primary value and risk is in service interactions, not internal logic.

| #1149           | Category: Testing                                                       | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Test Pyramid, Integration Test, Contract Test                           |                 |
| **Used by:**    | Microservices Teams, API-First Teams                                    |                 |
| **Related:**    | Test Pyramid, Test Honeycomb, Contract Test, API Testing, Microservices |                 |

### 🔥 The Problem This Solves

MISMATCH BETWEEN PYRAMID AND MICROSERVICES:
The classic Test Pyramid assumes a monolith with rich domain logic — most bugs are in the logic, so unit tests are most valuable. In a microservices architecture, each service is often thin (CRUD over a database, or orchestrator of downstream services). The domain logic is minimal; the risk is in service interactions: "Does Service A's API contract match what Service B expects? Does the schema migration break consumers?"

THE PYRAMID APPLIED WRONG:
A team with 10 microservices, each with 80% unit test coverage. Their incident report: "Service B was updated, response schema changed. Service A didn't know. Broke in production." Unit tests on both sides passed — the interface mismatch was never tested.

THE DIAMOND INSIGHT:
For microservices, service interaction testing (contract tests, service-level integration tests) is more valuable than unit testing each service's internal logic. The diamond shape puts the widest layer at service/contract tests, not unit tests.

### 📘 Textbook Definition

The **Test Diamond** (also associated with the "testing honeycomb" by Spotify) is a testing strategy where: (1) **Unit tests** (bottom) are the fewest — used only where complex domain logic exists; (2) **Service/Integration tests** (middle — widest) are the most numerous — test the service in isolation with its real dependencies (DB, cache) and contract tests; (3) **E2E tests** (top) are the fewest — just enough to verify critical user journeys end-to-end. The diamond recognises that in API-centric architectures, the integration layer carries the most risk.

### ⏱️ Understand It in 30 Seconds

**One line:**
Test Diamond = most tests at the service interaction layer, fewer unit + fewer E2E.

**One analogy:**

> In microservices, the risk is at the **junctions** (service boundaries) — like road intersections are where most accidents happen. The test diamond puts the most test coverage at the junctions (contract tests, service tests), fewer tests on individual road segments (unit tests), and fewer tests on full-city routes (E2E).

### 🔩 First Principles Explanation

THE PYRAMID VS DIAMOND — WHEN TO USE EACH:

```
PYRAMID suits:
  ✓ Monolith with rich domain logic (pricing, rules, algorithms)
  ✓ When most bugs are in business logic
  ✓ When services are stable, interfaces don't change often

DIAMOND suits:
  ✓ Microservices with thin domain logic
  ✓ When most bugs are at service boundaries (schema drift, API changes)
  ✓ When services evolve independently and must maintain backward compatibility
  ✓ API-first teams where the contract IS the product
```

DIAMOND SHAPE:

```
      ★★
    [E2E]
  ──────────                     ~5 tests
      ★★★★★★★★★★
  [Service/Contract/API Tests]   ~100 tests (widest layer)
  ────────────────────────────
      ★★★★
    [Unit Tests]
  ──────────────                 ~20 tests (only for complex logic)
```

SERVICE TEST (fits the widest diamond layer):

```
What a service test covers:
  ✓ HTTP request → controller → service → repository → database (Testcontainers)
  ✓ Request serialization / deserialization
  ✓ Database schema correctness
  ✓ Error handling (what HTTP status for various error conditions)
  ✓ Contract: does the response match what consumers expect?

What it does NOT cover:
  ✗ Multi-service user journeys (that's E2E)
  ✗ Individual method logic (that's unit, if needed)
```

CONTRACT TESTS IN THE DIAMOND:

```
Service A (consumer) expects:
  GET /api/orders/{id}
  Response: { "orderId": "...", "status": "CONFIRMED", "total": 99.90 }

Service B (provider) has contract test:
  Verify: GET /api/orders/{id} returns schema matching consumer expectation
  Tools: Pact (consumer-driven contract testing)

Result: if Service B changes its response schema, contract test fails immediately
  → Integration bug caught before deployment, not in production
```

### 🧪 Thought Experiment

THE MICROSERVICES BUG THAT UNIT TESTS CAN'T CATCH:

```
Service A (Order Service):
  Sends: { "amount": 99.90, "currency": "USD" }

Service B (Payment Service):
  Reads: { "totalAmount": 99.90 }  ← different field name!

Both services have 100% unit test coverage.
Neither service notices the mismatch.
E2E test: payment always fails, but it's hard to diagnose.
Contract test (diamond middle layer): would catch this immediately.
  Consumer (Service A) defines: "I will send field 'amount'"
  Provider (Service B) verifies: "I read field 'amount'" ← fails immediately
```

### 🧠 Mental Model / Analogy

> The Test Diamond is an **API-first testing philosophy**: your service's primary identity is its API contract, not its internal code. Testing the internal code (unit tests) without testing the contract is like proofreading the internal company memo without ever checking what was said to customers. The widest test layer covers what matters most: "does our service honor its public contract?"

### 📶 Gradual Depth — Four Levels

**Level 1:** In microservices, the most important tests verify that services talk to each other correctly. Unit tests matter less when logic is thin; service/contract tests matter more.

**Level 2:** Implementation for a Spring Boot microservice: unit tests with Mockito for any complex calculations; service tests with `@SpringBootTest` + Testcontainers + MockMvc for the HTTP layer + DB; contract tests with Pact for each consumer-provider pair; minimal Playwright/Selenium E2E for critical journeys.

**Level 3:** Pact contract testing workflow: consumer writes a Pact test (what it expects from the provider), publishes the pact to a Pact Broker, provider downloads the pact and verifies its API fulfills the consumer's expectations. If the provider changes its API in a way that breaks consumers, the provider's contract verification fails before deployment. This decouples consumer and provider deployment cycles — services can be deployed independently as long as contract tests pass.

**Level 4:** The diamond is not the final word — it's a model for a specific context. The "testing honeycomb" (Spotify 2018) makes a similar case. The underlying principle both share: test distribution should match risk distribution. In microservices, risk lives at boundaries; in monoliths, risk lives in logic. Advanced teams model their test distribution empirically: track where production bugs were found, what test level would have caught them, and adjust the distribution accordingly. The test strategy is a living document, not a one-time decision.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│                   TEST DIAMOND SHAPE                     │
├──────────────────────────────────────────────────────────┤
│                     ▲                                    │
│                    /E\                                   │
│                   / 2E\   Top: few E2E tests             │
│                  /─────\                                 │
│                 /Service\                                │
│                /Contract \/──── Middle: widest           │
│               /API Tests──\     (service + contract)    │
│              /─────────────\                             │
│             / Unit (complex \  Bottom: few unit tests    │
│            /   logic only)   \ (only where logic exists) │
│           /───────────────────\                          │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

```
Order Service: thin CRUD microservice

Unit tests (5 tests — only for non-trivial logic):
  ✓ Tax calculation logic
  ✓ Discount eligibility check

Service tests (30 tests — the diamond's wide layer):
  ✓ POST /orders → creates order in PostgreSQL (Testcontainers)
  ✓ GET /orders/{id} → returns correct JSON schema
  ✓ PUT /orders/{id}/cancel → validates state machine transitions
  ✓ All HTTP status codes (200, 201, 400, 404, 409)

Contract tests (10 tests — part of wide layer):
  ✓ Pact: order response matches Payment Service consumer pact
  ✓ Pact: order events match Notification Service consumer pact

E2E tests (2 tests — top of diamond):
  ✓ Complete order flow (place → pay → confirm email)
  ✓ Order cancellation flow

Total test suite: 47 tests, CI time: ~3 minutes
Risk coverage: service contract, DB schema, HTTP layer, critical flows
```

### 💻 Code Example

```java
// Service test (widest diamond layer): real Spring context + Testcontainers
@SpringBootTest(webEnvironment = RANDOM_PORT)
@Testcontainers
class OrderControllerServiceTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createOrder_returnsCreatedWithCorrectSchema() {
        OrderRequest request = new OrderRequest("product-123", 2, "alice@test.com");
        ResponseEntity<OrderResponse> response = restTemplate.postForEntity(
            "/orders", request, OrderResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(CREATED);
        assertThat(response.getBody().getOrderId()).isNotNull();
        assertThat(response.getBody().getStatus()).isEqualTo("PENDING");
        assertThat(response.getBody().getTotal()).isPositive();
    }
}
```

```java
// Consumer-driven contract test (Pact — part of wide layer)
@ExtendWith(PactConsumerTestExt.class)
class PaymentServiceConsumerPactTest {

    @Pact(consumer = "payment-service", provider = "order-service")
    RequestResponsePact createPact(PactDslWithProvider builder) {
        return builder
            .given("order 123 exists")
            .uponReceiving("GET order 123")
                .path("/orders/123").method("GET")
            .willRespondWith()
                .status(200)
                .body(new PactDslJsonBody()
                    .stringType("orderId")
                    .decimalType("total")
                    .stringMatcher("status", "PENDING|CONFIRMED|CANCELLED"))
            .toPact();
    }
}
```

### ⚖️ Comparison Table

|                    | Test Pyramid         | Test Diamond (Honeycomb)           |
| ------------------ | -------------------- | ---------------------------------- |
| Widest layer       | Unit tests           | Service/integration/contract tests |
| Use case           | Domain-rich monolith | Microservices, API-centric         |
| Primary risk       | Logic bugs           | Interface/contract bugs            |
| Unit test role     | Central              | Supporting (where logic exists)    |
| Contract test role | Optional             | Central                            |

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                     |
| --------------------------------------- | ------------------------------------------------------------------------------------------- |
| "Diamond replaces pyramid everywhere"   | Diamond suits microservices; pyramid suits logic-rich systems; match to your risk profile   |
| "Unit tests are unimportant in diamond" | They're fewer, but still important for complex logic; don't skip them where logic exists    |
| "E2E tests verify contract too"         | E2E tests verify user journeys; contract tests verify API schemas — different failure modes |

### 🚨 Failure Modes & Diagnosis

**1. No Contract Tests → Silent Service Incompatibility**

Symptom: Service B deployed, breaks Service A — only discovered in production or E2E tests.
Fix: Add Pact consumer-driven contract tests between every service pair that communicates.

**2. Service Tests Too Slow (Full Spring Context + DB for Each Test)**

Cause: Each test class starts a new Spring context.
Fix: Use `@SpringBootTest` with shared application context; share Testcontainers containers via static lifecycle.

### 🔗 Related Keywords

- **Prerequisites:** Test Pyramid, Integration Test, Contract Test
- **Related:** Test Honeycomb, Pact, Consumer-Driven Contract Testing, Microservices Testing

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SHAPE        │ Wide middle (service/contract), narrow   │
│              │ bottom (unit) and top (E2E)              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Microservices, thin services, API-centric│
├──────────────┼───────────────────────────────────────────┤
│ KEY TESTS    │ Service tests (full HTTP→DB) + Pact      │
│              │ contract tests                           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "In microservices, the contract is the   │
│              │  product — test it most thoroughly"      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The "consumer-driven contract testing" model (Pact) means the consumer defines what they need from the provider, and the provider verifies it satisfies those needs. This creates a dependency: the provider can't change its API without checking all consumer pacts. Compare this to: (1) provider-driven contracts (provider publishes an OpenAPI spec, consumers adapt), and (2) schema registry for Kafka events (producer publishes Avro schema, consumers register compatibility). When is consumer-driven preferable, and when is provider-driven or schema registry more appropriate? Relate to: tight vs. loose coupling, number of consumers, rate of API change.

**Q2.** A microservices platform has 20 services and 50 consumer-provider pairs. Running all Pact contract verifications adds 15 minutes to CI. Describe: (1) how Pact Broker's "can I deploy" feature enables selective verification (only run contract tests for changed services), (2) how webhook triggers work (consumer change → trigger provider verification automatically), (3) the tradeoff between "verify all pacts on every build" (maximum safety) vs. "verify only affected pacts" (faster CI), and (4) what happens when a provider deploys without running contract tests and subsequently breaks a consumer — the incident timeline and detection lag.
