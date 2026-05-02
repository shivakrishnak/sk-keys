---
layout: default
title: "Contract Test"
parent: "Testing"
nav_order: 1133
permalink: /testing/contract-test/
number: "1133"
category: Testing
difficulty: ★★★
depends_on: "Integration Test, Microservices, HTTP APIs"
used_by: "Consumer-Driven Contract Testing, Pact, Spring Cloud Contract, CI-CD pipelines"
tags: #testing, #contract-test, #pact, #consumer-driven, #microservices, #api-compatibility
---

# 1133 — Contract Test

`#testing` `#contract-test` `#pact` `#consumer-driven` `#microservices` `#api-compatibility`

⚡ TL;DR — A **contract test** verifies that a service's API (the "contract") matches what its consumers expect. In microservices, Service A (consumer) calls Service B (provider). Consumer-Driven Contract Testing (CDC): the consumer defines the contract (what it sends, what it expects back), the provider verifies it can fulfill that contract. Tools: **Pact** (polyglot) and **Spring Cloud Contract**. Prevents API breaking changes from reaching production without coordination.

| #1133           | Category: Testing                                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Integration Test, Microservices, HTTP APIs                                     |                 |
| **Used by:**    | Consumer-Driven Contract Testing, Pact, Spring Cloud Contract, CI-CD pipelines |                 |

---

### 📘 Textbook Definition

**Contract test**: an automated test that verifies the interface agreement (contract) between a service provider and its consumers. A contract specifies: for a given request/event from the consumer, what response/message does the provider return? Types: (1) **Consumer-Driven Contract Testing (CDC)**: the consumer writes the expected contract; the provider runs the contract to verify it can fulfill it. This inverts the traditional API-first approach — consumers define what they need, providers verify they provide it. (2) **Provider contract testing**: the provider publishes its contract (OpenAPI spec); consumers verify their code works with it. Tools: **Pact** (CDC, polyglot: Java, JavaScript, Python, Go), **Spring Cloud Contract** (CDC, Spring-native), **Pact Broker/PactFlow** (centralized contract sharing and verification). Contract tests solve the microservices integration testing problem: without them, you'd need all services running simultaneously for integration tests (slow, complex) OR rely on manual API change coordination (error-prone). With CDC: each service tests independently against the shared contract.

---

### 🟢 Simple Definition (Easy)

Microservices problem: Service A calls Service B's API. Service B's team changes the API response format (removes a field). Service A breaks in production. Nobody noticed because: the teams tested their services independently.

Contract test solution: Service A writes a test saying "I expect the response to have `{ orderId, status, total }`." This test is the CONTRACT. Service B's CI pipeline runs this contract against its own code. If Service B removes `total` → Service B's tests fail → the breaking change is caught BEFORE deployment. No manual coordination needed.

---

### 🔵 Simple Definition (Elaborated)

Contract testing sits between unit tests and E2E tests for microservices:

- **Unit test**: mock HTTP client → fast but doesn't test real network/serialization
- **Integration test (E2E)**: deploy all services → tests real interaction but is slow and complex
- **Contract test**: offline verification of the API contract — no real services running, but tests the actual contract (request/response shape, types, required fields)

**CDC Flow**:

1. Consumer team writes a Pact test: "when I send GET /orders/123, I expect `{id: 123, status: 'PAID', total: 99.99}`"
2. Pact generates a `.json` contract file from the consumer test
3. Contract is published to Pact Broker (shared repository for contracts)
4. Provider team's CI downloads the contract and runs it against the real provider service
5. Provider CI fails if the provider doesn't fulfill the contract
6. Pact Broker tracks which versions are compatible — "can Service A v1.2 deploy with Service B v3.4?"

---

### 🔩 First Principles Explanation

```java
// CONSUMER SIDE (Service A - Order Service calling Inventory Service)

@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "inventory-service")
class InventoryServicePactConsumerTest {

    // Define the contract: what request I send, what response I expect
    @Pact(consumer = "order-service")
    public V4Pact checkInventory(PactDslWithProvider builder) {
        return builder
            .given("product prod-123 exists with stock 50")  // provider state
            .uponReceiving("a request to check inventory for prod-123")
                .path("/inventory/prod-123")
                .method("GET")
                .headers(Map.of("Accept", "application/json"))
            .willRespondWith()
                .status(200)
                .headers(Map.of("Content-Type", "application/json"))
                .body(new PactDslJsonBody()
                    .stringType("productId")     ← must be a string (not specific value)
                    .integerType("availableStock")  ← must be an integer
                    .booleanType("inStock")
                    // Only fields the consumer ACTUALLY USES are included
                    // The provider can have more fields; we don't care about extras
                )
            .toPact(V4Pact.class);
    }

    @Test
    @PactTestFor(pactMethod = "checkInventory")
    void checkInventory_whenProductExists_returnsStockInfo(MockServer mockServer) {
        // Pact starts a mock server that returns the response we defined above
        InventoryClient client = new InventoryClient(mockServer.getUrl());

        // ACT: call our real InventoryClient with the mock server
        InventoryResponse response = client.checkStock("prod-123");

        // ASSERT: does our client correctly parse the response?
        assertThat(response.getProductId()).isNotNull();
        assertThat(response.getAvailableStock()).isGreaterThanOrEqualTo(0);
        assertThat(response.isInStock()).isNotNull();
    }

    // This test generates: target/pacts/order-service-inventory-service.json
    // That file is the CONTRACT
}
```

```java
// PROVIDER SIDE (Inventory Service - must fulfill the contract)

@Provider("inventory-service")
@PactBroker(url = "${pact.broker.url}")   // download contracts from Pact Broker
class InventoryServicePactProviderIT {

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void pactVerificationTestTemplate(PactVerificationContext context) {
        context.verifyInteraction();  // runs the contract against the real service
    }

    @BeforeEach
    void before(PactVerificationContext context) {
        // Start the real Inventory Service (Spring Boot)
        context.setTarget(new HttpTestTarget("localhost", 8081));
    }

    // Provider states: set up the data that the consumer's test requires
    @State("product prod-123 exists with stock 50")
    void setupProduct() {
        // Insert test data into the real database (Testcontainers PostgreSQL)
        productRepository.save(new Product("prod-123", "Widget", 50));
    }

    // If this test passes: Inventory Service can fulfill Order Service's contract
    // Pact Broker records: order-service@current + inventory-service@current = COMPATIBLE
}
```

```
PACT BROKER WORKFLOW:

  Consumer CI:
  1. Run consumer tests → generate .json contract file
  2. Publish contract to Pact Broker: pact publish target/pacts/

  Provider CI:
  3. mvn verify (or gradle test)
  4. Provider test downloads contracts from Pact Broker
  5. For each contract: sets up provider state → runs request → verifies response
  6. Reports result to Pact Broker: PASSED or FAILED

  Deployment gate (can-i-deploy):
  7. Before deploying ANY service: pact-broker can-i-deploy
     --pacticipant order-service --version 1.2.3 --to production
  8. Pact Broker checks: all contracts verified? → YES → allow deploy
                                                  → NO → block deploy

SPRING CLOUD CONTRACT (alternative to Pact, Spring-native):

  Provider writes contracts (Groovy/YAML DSL):
  // contracts/shouldReturnInventory.groovy
  Contract.make {
    request {
      method GET()
      url '/inventory/prod-123'
    }
    response {
      status 200
      body([productId: $(anyNonEmptyString()), availableStock: $(anyInteger())])
      headers { contentType(applicationJson()) }
    }
  }

  Maven plugin generates:
  - Provider test: verifies the real provider fulfills the contract
  - Consumer stub JAR: published to Maven Central/Nexus

  Consumer: downloads the stub JAR → runs against the stub in tests
  (no Pact Broker needed; stubs in Maven repo)
```

---

### ❓ Why Does This Exist (Why Before What)

In a microservices architecture with 20+ services, verifying that every service is compatible with every other service requires either: (1) deploying all services and running E2E tests — extremely complex, slow, and expensive; or (2) trusting that API changes are communicated and coordinated manually — error-prone and doesn't scale. Contract tests provide a middle path: each service independently verifies its contract compliance, and a shared contract broker tracks compatibility across versions. Teams can deploy independently while maintaining confidence that the contracts are upheld.

---

### 🧠 Mental Model / Analogy

> **Contract tests are like legal contracts between businesses**: Service A (consumer) and Service B (provider) agree to a contract: "Service B will always return `{productId, availableStock, inStock}` when I call GET /inventory/{id}." Service A can build its code against this contract, knowing it will be honored. If Service B violates the contract (removes `availableStock`), the contract is broken — the CI pipeline catches it. Without contracts, both parties just trust each other and hope — which works until someone changes the API without telling everyone.

---

### 🔄 How It Connects (Mini-Map)

```
Microservices need to verify inter-service API compatibility without deploying everything
        │
        ▼
Contract Test ◄── (you are here)
(CDC: consumer defines contract; provider verifies it can fulfill; Pact Broker tracks)
        │
        ├── Integration Test: contract tests ARE integration tests (special case)
        ├── Microservices: contract tests designed specifically for microservices architectures
        ├── HTTP APIs: most contracts are HTTP request/response pairs
        └── CI-CD Pipeline: can-i-deploy gate prevents deploying incompatible versions
```

---

### 💻 Code Example

```yaml
# Pact contract file (generated by consumer test: order-service-inventory-service.json)
{
  "consumer": { "name": "order-service" },
  "provider": { "name": "inventory-service" },
  "interactions":
    [
      {
        "description": "a request to check inventory for prod-123",
        "providerStates": [{ "name": "product prod-123 exists with stock 50" }],
        "request":
          {
            "method": "GET",
            "path": "/inventory/prod-123",
            "headers": { "Accept": "application/json" },
          },
        "response":
          {
            "status": 200,
            "headers": { "Content-Type": "application/json" },
            "body":
              {
                "productId": "some-string",
                "availableStock": 100,
                "inStock": true,
              },
            "matchingRules":
              {
                "body":
                  {
                    "$.productId": { "matchers": [{ "match": "type" }] },
                    "$.availableStock":
                      { "matchers": [{ "match": "integer" }] },
                    "$.inStock": { "matchers": [{ "match": "type" }] },
                  },
              },
          },
      },
    ],
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contract tests replace integration tests        | Contract tests verify API compatibility (shape, types, required fields). They don't test business logic, data correctness, or complex flows. You still need integration tests to verify that the provider service returns the RIGHT data for specific business scenarios, not just data of the right SHAPE. |
| The provider writes the contracts in CDC        | In Consumer-Driven Contract Testing, the CONSUMER writes the contracts based on what IT needs. The provider verifies it can fulfill consumer-defined contracts. This is intentional — it ensures the API is driven by actual consumer needs, not hypothetical provider assumptions.                         |
| All fields must match exactly in Pact contracts | Pact supports flexible matching: `type` matchers (value must be the same type, not the same value), `regex` matchers, `datetime` matchers, and more. You should use type matchers for IDs and values that change — the contract tests the SHAPE and TYPES, not the specific data values.                    |

---

### 🔗 Related Keywords

- `Integration Test` — contract tests are a specialized form of integration test
- `Microservices` — contract tests solve the multi-service compatibility problem
- `HTTP APIs` — most contracts describe HTTP request/response pairs
- `E2E Test` — the alternative to contract tests (but slower and more complex)
- `CI-CD Pipeline` — `can-i-deploy` gate uses contract verification results

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CDC FLOW:                                               │
│ 1. Consumer writes Pact test → generates contract.json │
│ 2. Publish to Pact Broker                               │
│ 3. Provider downloads + verifies contract               │
│ 4. can-i-deploy gate checks compatibility before deploy │
│                                                         │
│ TOOLS: Pact (polyglot) | Spring Cloud Contract (Java)  │
│                                                         │
│ WHAT IT TESTS: API shape, types, required fields        │
│ WHAT IT DOESN'T: business logic, data correctness      │
│                                                         │
│ CONSUMER writes contracts → PROVIDER verifies them     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Consumer-Driven Contract Testing gives consumers control over the provider's API evolution. But what if there are 50 consumers of a provider API, all defining their own contracts? The provider must satisfy ALL 50 contracts simultaneously. Adding a new required field to the response breaks nothing (additive). Removing a field used by one consumer breaks that consumer's contract. How does this asymmetry (additive changes are safe; removals are breaking) shape API versioning strategy in a CDC environment? What is the "expand and contract" pattern for evolving APIs under contract testing?

**Q2.** Pact works well for synchronous HTTP APIs but microservices also communicate via asynchronous messages (Kafka, RabbitMQ). Pact supports message contracts: the consumer defines the message structure it expects to consume; the provider verifies it publishes messages in that format. Compare synchronous (HTTP) vs asynchronous (event) contract testing: what additional challenges arise with events? (Consider: event schema evolution, consumer lag, event ordering, schema registries like Confluent Schema Registry vs Pact for Kafka.) When does schema registry replace Pact for event-based contracts?
