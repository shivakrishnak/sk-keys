---
layout: default
title: "Pact (Contract Testing)"
parent: "Testing"
nav_order: 1159
permalink: /testing/pact-contract-testing/
number: "1159"
category: Testing
difficulty: ★★★
depends_on: Contract Test, Integration Test, Microservices
used_by: Microservices Teams, API Teams
related: Contract Test, WireMock, Consumer-Driven Contracts, Pact Broker, Test Diamond
tags:
  - testing
  - pact
  - contract-testing
  - microservices
---

# 1159 — Pact (Contract Testing)

⚡ TL;DR — Pact is a consumer-driven contract testing framework: the API consumer writes a test defining what it expects from the provider; Pact generates a contract file (pact); the provider verifies its API fulfills the contract — enabling independent deployment of services with confidence.

| #1159           | Category: Testing                                                             | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Contract Test, Integration Test, Microservices                                |                 |
| **Used by:**    | Microservices Teams, API Teams                                                |                 |
| **Related:**    | Contract Test, WireMock, Consumer-Driven Contracts, Pact Broker, Test Diamond |                 |

### 🔥 The Problem This Solves

MICROSERVICES INTEGRATION HELL:
Service A consumes Service B's API. When Service B changes its response schema (renames a field, removes a field, changes a type), Service A breaks. Without contract tests, this is discovered: (1) in E2E tests (slow, expensive, hard to diagnose), or (2) in production (catastrophic). With manual contracts (OpenAPI spec): the spec can drift from the real implementation; the spec doesn't verify that Service A's consumption code matches what Service B provides.

CONSUMER-DRIVEN = CONSUMER IN CONTROL:
Standard API-first (provider-driven): provider publishes spec → consumers adapt. Risks: provider changes spec without knowing which consumers rely on which fields. Consumer-driven (Pact): consumers publish what they NEED → provider verifies it satisfies all consumers before deploying. If a provider change would break a consumer's pact, the provider's CI fails — before deployment.

### 📘 Textbook Definition

**Pact** is a consumer-driven contract testing framework. The **consumer** writes a Pact test that: (1) defines the HTTP interaction it expects (request/response), (2) runs the test against a Pact mock server (which verifies the consumer code can handle the response), (3) generates a **pact file** (JSON) describing the contract. The **provider** downloads the pact file and runs a **provider verification test** — verifying that its real API fulfills every interaction in the pact. The **Pact Broker** is a service that stores and distributes pact files between consumer and provider CI pipelines. The `can-i-deploy` tool checks if it's safe to deploy a version based on verified contracts.

### ⏱️ Understand It in 30 Seconds

**One line:**
Pact = consumer writes what it needs, provider proves it delivers — without direct communication.

**One analogy:**

> Pact is a **supplier agreement** process: the restaurant (consumer) tells the food supplier (provider) exactly what quality and specification they need ("10kg free-range eggs, grade A"). The supplier verifies they can supply that specification before accepting the order. If the supplier changes their egg source, they verify the new source still meets the restaurant's spec before delivering. No surprises on delivery day.

### 🔩 First Principles Explanation

PACT WORKFLOW:

```
1. CONSUMER SIDE (Order Service):

   @ExtendWith(PactConsumerTestExt.class)
   class OrderServicePactConsumerTest {

     @Pact(consumer = "order-service", provider = "payment-service")
     RequestResponsePact createPact(PactDslWithProvider builder) {
       return builder
         .given("payment service is available")
         .uponReceiving("a charge request")
           .method("POST").path("/charges")
           .headers(Map.of("Content-Type", "application/json"))
           .body(new PactDslJsonBody()
               .numberType("amount")       // any number
               .stringType("currency")     // any string
               .stringType("token"))
         .willRespondWith()
           .status(201)
           .body(new PactDslJsonBody()
               .stringType("chargeId")     // any string
               .stringMatcher("status", "succeeded|failed"))
         .toPact();
     }

     @Test
     @PactTestFor(pactMethod = "createPact")
     void chargePayment_shouldHandleResponse(MockServer mockServer) {
       // MockServer is a Pact-controlled server, returns the defined response
       PaymentClient client = new PaymentClient(mockServer.getUrl());
       ChargeResult result = client.charge(50.00, "USD", "tok_test");

       // Verify consumer CAN handle the response format
       assertThat(result.getChargeId()).isNotNull();
       assertThat(result.getStatus()).isIn("succeeded", "failed");
     }
   }

   → Generates: pact/order-service-payment-service.json
   → Uploaded to Pact Broker

2. PROVIDER SIDE (Payment Service):

   @SpringBootTest(webEnvironment = RANDOM_PORT)
   @Provider("payment-service")
   @PactBroker(url = "${PACT_BROKER_URL}")
   class PaymentServicePactProviderTest {

     @TestTemplate
     @ExtendWith(PactVerificationInvocationContextProvider.class)
     void verifyPact(PactVerificationContext context) {
       context.verifyInteraction();
     }

     @State("payment service is available")
     void paymentServiceAvailable() {
       // Set up test state — no special setup needed
     }
   }

   → Downloads pact from Pact Broker
   → Runs each interaction against real Spring Boot app
   → If real response matches pact → PASS → safe to deploy
```

THE "CAN I DEPLOY" CHECK:

```bash
# Before deploying payment-service v2.0:
pact-broker can-i-deploy \
  --pacticipant payment-service \
  --version 2.0.0 \
  --to-environment production

# Output:
# ✅ payment-service v2.0.0 is verified against order-service v1.5.0 (consumer)
# ✅ payment-service v2.0.0 is verified against checkout-service v2.1.0 (consumer)
# RESULT: can-i-deploy = YES

# If payment-service v2.0 changed chargeId field → chargeId2:
# ❌ order-service v1.5.0 pact specifies chargeId — NOT satisfied by v2.0
# RESULT: can-i-deploy = NO
```

### 🧪 Thought Experiment

THE FIELD RENAME BUG — PACT CATCHES IT:

```
Payment Service developer renames field: "chargeId" → "transactionId"
(In a non-Pact world: this silently breaks all consumers)

With Pact:
  1. Order Service consumer test: expects field "chargeId"
     pact file: { "chargeId": { "match": "type", "example": "ch_123" } }

  2. Payment Service provider verification:
     Real response: { "transactionId": "ch_123" }
     Pact expects: "chargeId" field
     → PROVIDER VERIFICATION FAILS in Payment Service CI

  3. Developer sees: "Order Service pact requires 'chargeId' field — not found"
     Options: (a) revert rename, (b) talk to Order Service team about migration

  4. If transitional: Payment Service returns BOTH fields for a version:
     { "chargeId": "ch_123", "transactionId": "ch_123" }  // backward compatible
     → Pact: PASS
     → Order Service can deploy new code using "transactionId" first
     → Then Payment Service removes "chargeId"
     → Order Service pact updated to expect "transactionId"

  Result: coordinated, safe API evolution without integration incidents
```

### 🧠 Mental Model / Analogy

> Pact is a **living contract repository**: consumers deposit their requirements, providers make withdrawals (verify they can fulfill them). The Pact Broker is the contract vault — any time a provider wants to deploy, they check the vault to ensure they're not breaking any deposited requirements. Deposits (consumer pacts) drive provider requirements; the provider can never claim ignorance of consumer needs.

### 📶 Gradual Depth — Four Levels

**Level 1:** Consumer writes: "I expect Service B to return a JSON with field X." Provider tests: "My API actually returns field X." If provider changes field X, its test fails before deployment. No integration incidents.

**Level 2:** Consumer Pact test: define interaction with `PactDslJsonBody` (flexible: `stringType` matches any string, `numberType` matches any number — not brittle like exact values). Generate pact file. Publish to Pact Broker. Provider test: `@PactBroker` downloads pacts, `@TestTemplate` runs each interaction, `@State` sets up test data for each scenario.

**Level 3:** Provider states: each pact interaction can specify a state ("given order 123 exists"). The provider must implement `@State("order 123 exists")` — a setup method that creates the required test data. This ensures the provider test creates the correct preconditions for each interaction being verified. Consumer version tagging: tag consumer versions by environment (`main`, `staging`, `production`). Provider uses `from-environment=production` to only verify against pacts from currently deployed consumers.

**Level 4:** Pact in enterprise context: 20 services with 50 consumer-provider pairs. Pact Broker's network graph shows all contracts and verification status. Webhook configuration: when a consumer publishes a new pact, the Pact Broker triggers a CI job on the provider automatically — continuous contract verification without manual coordination. The `can-i-deploy` check in every deployment pipeline is the key enforcement mechanism — no service deploys to production if it breaks any consumer's pact. Pact for messaging/events: beyond HTTP, Pact supports message contracts (Kafka, SNS) — consumer defines what event format it expects, producer verifies its events match.

### 💻 Code Example

```java
// Consumer test: generates pact file
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "product-service")
class ProductServicePactConsumerTest {

    @Pact(consumer = "order-service")
    RequestResponsePact getProductPact(PactDslWithProvider builder) {
        return builder
            .given("product p123 exists")
            .uponReceiving("get product p123")
                .method("GET").path("/products/p123")
            .willRespondWith()
                .status(200)
                .headers(Map.of("Content-Type", "application/json"))
                .body(new PactDslJsonBody()
                    .stringType("productId", "p123")
                    .stringType("name")
                    .decimalType("price")
                    .booleanType("available"))
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "getProductPact")
    void getProduct_canParseResponse(MockServer mockServer) {
        ProductClient client = new ProductClient(mockServer.getUrl());
        Product product = client.getProduct("p123");

        assertThat(product.getProductId()).isNotNull();
        assertThat(product.getPrice()).isPositive();
    }
}
```

```java
// Provider test: verifies against consumer pact
@SpringBootTest(webEnvironment = RANDOM_PORT)
@Provider("product-service")
@PactBroker(url = "${PACT_BROKER_URL}", tags = {"main"})
class ProductServicePactProviderTest {

    @LocalServerPort
    int port;

    @BeforeEach
    void setupTarget(PactVerificationContext context) {
        context.setTarget(new HttpTestTarget("localhost", port));
    }

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verifyPact(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @State("product p123 exists")
    void productExists() {
        productRepository.save(new Product("p123", "Widget", 9.99, true));
    }
}
```

### ⚖️ Comparison Table

|                           | Integration Test (Testcontainers) | Pact Contract Test             | E2E Test           |
| ------------------------- | --------------------------------- | ------------------------------ | ------------------ |
| What it tests             | Service internal behavior         | Service API contract           | Full user journey  |
| Requires running provider | No (Pact mock server)             | No (consumer) / Yes (provider) | Yes (all services) |
| Speed                     | Medium                            | Fast (consumer)                | Slow               |
| Catches schema drift      | ✗                                 | ✓                              | ✓ (eventually)     |
| Feedback loop             | Minutes                           | Minutes (per service)          | Hours              |

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                    |
| ------------------------------------------------------ | -------------------------------------------------------------------------- |
| "Pact replaces integration tests"                      | Pact verifies the contract; integration tests verify behavior; both needed |
| "Provider-driven contracts (OpenAPI) is equivalent"    | OpenAPI spec can drift; Pact verification runs against the real API        |
| "Pact requires both services to change simultaneously" | Pact enables independent deployment; `can-i-deploy` ensures safety         |

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROLES        │ Consumer: defines needs; Provider:        │
│              │ verifies it delivers                     │
├──────────────┼───────────────────────────────────────────┤
│ FLOW         │ Consumer test → pact JSON → Pact Broker  │
│              │ → Provider downloads → verifies → deploy │
├──────────────┼───────────────────────────────────────────┤
│ SAFETY GATE  │ can-i-deploy: check before every deploy  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Consumer declares needs; provider must  │
│              │  prove it satisfies them before deploy"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Pact uses "type matching" (`stringType`, `numberType`) rather than value matching (`equalTo("ch_123")`) in consumer pacts. Explain why type matching is better for contracts: (a) value matching creates brittle pacts (test data becomes part of the contract), (b) type matching expresses what the consumer ACTUALLY cares about (field exists and has correct type), (c) when value matching IS appropriate (enum values, status codes, specific string formats). Describe the `PactDslJsonBody` matchers for: regex validation, datetime format, array min/max length, and nested object matching.

**Q2.** Pact for events (Kafka/SNS): a Producer publishes an `OrderPlaced` event; a Consumer (notification service) subscribes and sends emails. Describe: (1) how Pact message contract tests work differently from HTTP contract tests (no request/response — just a message body), (2) the `@MessagePact` annotation and how the consumer test verifies it can parse the message, (3) how the producer test verifies its published message matches the consumer's pact, (4) the schema evolution challenge — if producer adds a new field, how does Pact ensure backward compatibility (old consumers still parse new messages), and (5) how this compares to Confluent Schema Registry (Avro schema compatibility).
