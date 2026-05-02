---
layout: default
title: "Consumer-Driven Contract Testing"
parent: "Microservices"
nav_order: 662
permalink: /microservices/consumer-driven-contract-testing/
number: "662"
category: Microservices
difficulty: ★★★
depends_on: "API Gateway, Service Contract"
used_by: "Pact (Contract Testing), CI-CD Pipeline"
tags: #advanced, #microservices, #testing, #distributed, #architecture
---

# 662 — Consumer-Driven Contract Testing

`#advanced` `#microservices` `#testing` `#distributed` `#architecture`

⚡ TL;DR — **Consumer-Driven Contract Testing** is a testing pattern where API **consumers** (calling services) define the contract (expected request/response format) and share it with the **provider** (called service). The provider runs the consumer's contract as part of its CI pipeline. Breaks are caught before deployment — not in integration environments. **Pact** is the dominant framework.

| #662            | Category: Microservices                 | Difficulty: ★★★ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | API Gateway, Service Contract           |                 |
| **Used by:**    | Pact (Contract Testing), CI-CD Pipeline |                 |

---

### 📘 Textbook Definition

**Consumer-Driven Contract Testing** (CDCT) is a microservices testing technique introduced by Ian Robinson (ThoughtWorks, 2006) where API contracts are defined by the **consumer** (the service that calls another service's API), not the provider. Each consumer defines a **contract**: "I call endpoint X with request Y and expect response Z." The consumer generates this contract (in Pact's case: a `.json` pact file) as a side effect of running its own unit tests. The provider then retrieves these consumer contracts and runs them against its actual implementation in its own CI pipeline. If a provider change would break any consumer's contract, the provider CI fails — before deployment. Benefits: catches breaking API changes in CI, not in staging/production; providers know exactly which fields consumers actually use (consumers define only what they need — not the full schema); enables independent deployment of services as long as contracts are satisfied (**can-i-deploy** check). Alternative to: end-to-end integration tests (which are slow, flaky, require all services running), and strict provider-defined API versioning (which constrains the provider unnecessarily).

---

### 🟢 Simple Definition (Easy)

Service A calls Service B's API. Consumer-Driven Contract Testing: Service A writes a test that says "I expect this response when I call this endpoint." That test generates a contract file. Service B's CI pipeline reads that contract and verifies its implementation satisfies it. If Service B changes its API in a way that would break Service A — Service B's CI fails before deployment. Breaking changes are caught instantly, not in production.

---

### 🔵 Simple Definition (Elaborated)

Without CDCT: `OrderService` calls `CustomerService` API. `CustomerService` renames `name` to `fullName` in a refactor. Both services have unit tests (passing). Both have integration tests (but integration environment isn't updated). `CustomerService` is deployed to production. `OrderService` starts failing — `customer.getName()` returns `null`. Incident at 3am. With CDCT: `OrderService`'s Pact consumer test defines "I expect a `name` field." The generated contract is shared with `CustomerService`. When `CustomerService`'s CI runs provider verification against this contract: FAIL. The rename is caught before deployment. `CustomerService` either keeps `name` alongside `fullName` (additive) or coordinates a versioned migration.

---

### 🔩 First Principles Explanation

**The integration testing problem in microservices:**

```
TRADITIONAL INTEGRATION TEST PYRAMID:
  Unit Tests (fast, isolated) → Service Tests → Integration Tests (slow, fragile)

INTEGRATION TEST PROBLEMS IN MICROSERVICES:
  1. All services must be deployed and running simultaneously
     5 services → 5 containers → startup time: 30-120 seconds per test run

  2. Flakiness: any service restart, network glitch, or data issue fails ALL tests
     False failure rate: 20-30% in large systems → "just re-run it" culture

  3. Environment drift: integration environment ≠ production configuration
     Tests pass in integration → fail in production (environment-specific bugs)

  4. Slow feedback loop: broken contract not detected until integration test run
     Code merged → integration test scheduled → runs 30 min later → fail
     Developer has context-switched away → costly to debug

  5. No isolation: you don't know WHICH service's change broke the test

CDCT SOLUTION:
  Consumer test: fast unit test (mocked provider) → generates contract file
  Provider verification: fast test (replays consumer requests against real provider)
  No running infrastructure needed for either test
  Feedback: immediate (within same CI pipeline that introduced the change)
  Isolation: when provider CI fails on consumer contract → exactly which consumer fails
```

**How Pact contracts are structured:**

```json
{
  "consumer": {"name": "OrderService"},
  "provider": {"name": "CustomerService"},
  "interactions": [
    {
      "description": "Get customer for order placement",
      "request": {
        "method": "GET",
        "path": "/api/v1/customers/cust-123",
        "headers": {"Authorization": "Bearer token123"}
      },
      "response": {
        "status": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {
          "id": "cust-123",
          "name": "Alice Smith",     ← OrderService needs this field
          "tier": "GOLD"             ← OrderService needs this for discount
          // NOTE: OrderService does NOT declare "email" or "address"
          // because it doesn't use them — contract is minimal
        },
        "matchingRules": {
          "body": {
            "$.id": {"matchers": [{"match": "type"}]},       // match type: string
            "$.name": {"matchers": [{"match": "type"}]},     // match type: string
            "$.tier": {"matchers": [{"match": "regex", "regex": "BRONZE|SILVER|GOLD"}]}
          }
        }
      }
    }
  ]
}
```

**Consumer-side test (Pact Java) — generates the contract:**

```java
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "CustomerService", port = "8080")
class OrderServiceCustomerClientPactTest {

    @Pact(consumer = "OrderService")
    RequestResponsePact getCustomerForOrderPact(PactDslWithProvider builder) {
        return builder
            .given("customer cust-123 exists")
            .uponReceiving("get customer for order placement")
                .method("GET")
                .path("/api/v1/customers/cust-123")
                .headers(Map.of("Authorization", "Bearer token123"))
            .willRespondWith()
                .status(200)
                .headers(Map.of("Content-Type", "application/json"))
                .body(new PactDslJsonBody()
                    .stringType("id", "cust-123")
                    .stringType("name", "Alice Smith")
                    .stringMatcher("tier", "BRONZE|SILVER|GOLD", "GOLD"))
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "getCustomerForOrderPact")
    void shouldReturnCustomerForOrderPlacement(MockServer mockServer) {
        // This test runs against a mock server that enforces the pact contract.
        // The pact file is generated as a side effect of this test passing.
        CustomerClient client = new CustomerClient(mockServer.getUrl());
        CustomerDTO customer = client.getCustomer("cust-123");

        assertThat(customer.getName()).isNotBlank();
        assertThat(customer.getTier()).isIn("BRONZE", "SILVER", "GOLD");
    }
}
// Output: target/pacts/OrderService-CustomerService.json (the contract file)
```

**Provider-side verification (CustomerService CI) — verifies contract:**

```java
@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Provider("CustomerService")
@PactBroker(url = "https://pact-broker.internal")  // fetch contracts from Pact Broker
class CustomerServicePactVerificationTest {

    @LocalServerPort
    private int port;

    @BeforeEach
    void setUp(PactVerificationContext context) {
        context.setTarget(new HttpTestTarget("localhost", port));
    }

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verifyPact(PactVerificationContext context) {
        context.verifyInteraction();  // replays each consumer interaction against real service
    }

    @State("customer cust-123 exists")  // setup test data for this provider state
    void setupCustomerExists() {
        customerRepository.save(new Customer("cust-123", "Alice Smith", CustomerTier.GOLD));
    }
}
// If CustomerService renames "name" to "fullName":
// → verification fails: expected "name" field missing in response
// → CI fails: CustomerService cannot be deployed until contract is satisfied
```

---

### ❓ Why Does This Exist (Why Before What)

Microservices are deployed independently, but their APIs are interdependent. Provider-side API versioning alone (SemVer, URL versioning) tells consumers "a new version exists" but doesn't tell providers "which consumers would break if I change X." CDCT inverts this: consumers explicitly declare what they need, providers know exactly what they must preserve. The test pyramid has a "gap" between unit tests (isolated, fast) and integration tests (cross-service, slow). CDCT fills this gap: fast, isolated, yet cross-service contract verification.

---

### 🧠 Mental Model / Analogy

> Consumer-Driven Contract Testing is like a plug-and-socket electrical standard. The consumer (device) defines the plug shape it requires (3-pin UK, 2-pin EU). The provider (wall socket) must conform to this shape — not define its own. If the provider wants to change the socket shape, it must first check: do any existing devices (consumers) have a contract for the current shape? Only when all contracts are satisfied (or migrated) can the socket shape change. Compare to provider-driven contracts (API documentation): the provider defines the socket, and consumers must adapt. Provider-driven contracts often don't catch breaking changes until deployment.

---

### ⚙️ How It Works (Mechanism)

**CI/CD pipeline integration with Pact Broker:**

```
CONSUMER CI PIPELINE (OrderService):
  1. Run consumer tests (includes Pact consumer tests)
  2. Pact consumer tests generate pact files → target/pacts/
  3. Publish pacts to Pact Broker:
     ./pactflow publish target/pacts/ \
       --broker-base-url https://pact-broker.internal \
       --consumer-app-version $GIT_COMMIT_HASH \
       --branch main
  4. can-i-deploy check:
     pactflow can-i-deploy --pacticipant OrderService \
       --version $GIT_COMMIT_HASH --to-environment production
     → FAIL if CustomerService hasn't verified latest OrderService contract yet
  5. If PASS: deploy OrderService to production

PROVIDER CI PIPELINE (CustomerService):
  1. Run unit tests
  2. Run Pact provider verification (fetches all consumer contracts from Broker):
     → Verifies OrderService-CustomerService contract
     → Verifies PaymentService-CustomerService contract
     → Verifies ReportingService-CustomerService contract
  3. If ALL verifications pass:
     pactflow publish-provider-contracts \
       --broker-base-url https://pact-broker.internal \
       --provider CustomerService \
       --provider-app-version $GIT_COMMIT_HASH \
       --branch main
  4. can-i-deploy check → confirms all consumers are compatible
  5. If PASS: deploy CustomerService to production

PACT BROKER:
  Stores: all pact contracts by consumer + provider + version
  Tracks: which provider versions have verified which consumer contracts
  API: can-i-deploy checks (are all dependencies satisfied?)
  Webhooks: trigger provider CI when new consumer pact is published
```

---

### 🔄 How It Connects (Mini-Map)

```
API Gateway / Service Contract
(service API as interface)
        │
        ▼
Consumer-Driven Contract Testing  ◄──── (you are here)
(verify API contracts automatically in CI)
        │
        ├── Pact (Contract Testing) → the framework that implements this pattern
        ├── CI-CD Pipeline → where contract tests run
        └── Service Contract → what CDCT verifies
```

---

### 💻 Code Example

**can-i-deploy check in GitHub Actions:**

{% raw %}
```yaml
# .github/workflows/deploy.yml (OrderService):
- name: Publish Pact contracts
  run: |
    ./mvnw pact:publish \
      -Dpact.broker.url=https://pact-broker.internal \
      -Dpact.consumer.version=${{ github.sha }} \
      -Dpact.tag=${{ github.ref_name }}

- name: Can I Deploy?
  run: |
    docker run --rm pactfoundation/pact-cli:latest \
      broker can-i-deploy \
      --broker-base-url https://pact-broker.internal \
      --pacticipant OrderService \
      --version ${{ github.sha }} \
      --to-environment production
  # Fails if CustomerService hasn't verified the latest OrderService contract
  # Prevents deploying OrderService if its API dependencies aren't satisfied
```
{% endraw %}

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contract tests replace integration tests                       | CDCT tests API contracts (request/response shape). Integration tests verify business flows across services (e.g., "placing an order end-to-end"). Both have value. CDCT reduces the need for large-scale integration test suites but doesn't eliminate integration testing entirely |
| The provider defines the contract                              | In CDCT, consumers define contracts. Providers verify them. This is the inversion — and the key insight. Provider-defined contracts (Swagger/OpenAPI) describe the full API but don't tell you what specific fields consumers actually depend on                                    |
| Contract testing requires both services running simultaneously | No — that's the key advantage. Consumer tests run against a mock provider (no running service needed). Provider verification replays stored contracts against the real provider in isolation. No coordination required                                                              |
| If all contract tests pass, services are compatible            | Contract tests verify the API shape. They don't test behaviour, business logic, latency, or load handling. A provider can satisfy all contracts and still have production issues                                                                                                    |

---

### 🔥 Pitfalls in Production

**Stale contracts — consumer test covers only happy paths:**

```
SCENARIO:
  OrderService Pact consumer test: only covers HTTP 200 (success path)
  Contract does NOT include: HTTP 404 (customer not found), HTTP 503 (timeout)

  CustomerService changes error response:
  Old: 404 with body {"error": "not found"}
  New: 404 with body {"code": "CUSTOMER_NOT_FOUND", "message": "..."}

  OrderService code: CustomerNotFoundException catches response.body.error == "not found"
  After CustomerService deploys: 404 body changed.
  OrderService: exception handling broken, NPE in production.
  Contract tests: still passing (only happy path covered).

PREVENTION:
  Write consumer tests for ALL interactions the consumer handles:
  - Success paths (200, 201)
  - Client error paths (400, 404, 409)
  - Service unavailable (503) — if consumer has specific error handling

  // Test 404 path:
  @Pact(consumer = "OrderService")
  RequestResponsePact getCustomerNotFoundPact(PactDslWithProvider builder) {
      return builder
          .given("customer cust-NONEXISTENT does not exist")
          .uponReceiving("get non-existent customer")
          .method("GET").path("/api/v1/customers/cust-NONEXISTENT")
          .willRespondWith()
          .status(404)
          .body(new PactDslJsonBody()
              .stringType("code")     ← consumer tests the field it reads from 404
              .stringType("message"))
          .toPact();
  }
```

---

### 🔗 Related Keywords

- `Pact (Contract Testing)` — the framework that implements consumer-driven contract testing
- `Service Contract` — the API contract that CDCT verifies
- `CI-CD Pipeline` — where contract tests are executed and can-i-deploy checks run
- `API Gateway` — the integration point that contract testing protects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHO DEFINES  │ Consumer defines the contract              │
│ WHO VERIFIES │ Provider verifies against consumer contract│
│ WHEN         │ In CI pipeline (not integration environment)│
├──────────────┼───────────────────────────────────────────┤
│ PACT FLOW    │ Consumer test → pact.json → Pact Broker    │
│              │ → Provider CI fetches + verifies           │
├──────────────┼───────────────────────────────────────────┤
│ can-i-deploy │ Are all my dependencies verified?          │
│              │ Only deploy when YES                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your system has 20 microservices. `UserService` is consumed by 12 of those services. Each consumer has a Pact contract with `UserService`. The `UserService` team wants to add a new required field `phoneNumber` (NOT NULL) to the `POST /users` endpoint. Before making this change, they run provider verification: 8 of 12 consumer contracts pass, 4 fail (those 4 consumers don't send `phoneNumber`). How do you manage this migration? Describe the step-by-step process ensuring zero production incidents, including how you handle the 4 failing consumers in terms of deployment ordering and backward compatibility.

**Q2.** Consumer-Driven Contract Testing works well for synchronous REST/HTTP APIs. How would you adapt the contract testing concept for asynchronous event-based communication? Specifically: `OrderService` publishes `OrderPlaced` events to Kafka. `InventoryService` and `NotificationService` consume these events. How do you write a "consumer contract" for event consumers? What does the contract test look like? What does the provider (publisher) verification look like? Does Pact support messaging contracts, and what are the limitations?
