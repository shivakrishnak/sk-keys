---
layout: default
title: "Pact (Contract Testing)"
parent: "Microservices"
nav_order: 663
permalink: /microservices/pact-contract-testing/
number: "663"
category: Microservices
difficulty: ★★★
depends_on: "Consumer-Driven Contract Testing, CI-CD Pipeline"
used_by: "Service Contract, Backward Compatibility"
tags: #advanced, #microservices, #testing, #distributed, #architecture
---

# 663 — Pact (Contract Testing)

`#advanced` `#microservices` `#testing` `#distributed` `#architecture`

⚡ TL;DR — **Pact** is the open-source framework that implements Consumer-Driven Contract Testing. Consumers write tests that generate JSON pact files (contracts); providers verify these contracts in their CI pipeline. The **Pact Broker** stores and manages contracts across versions. `can-i-deploy` checks prevent deploying services that would break their consumers.

| #663            | Category: Microservices                          | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Consumer-Driven Contract Testing, CI-CD Pipeline |                 |
| **Used by:**    | Service Contract, Backward Compatibility         |                 |

---

### 📘 Textbook Definition

**Pact** is an open-source consumer-driven contract testing framework (created by Beth Skurrie et al., originally Ruby/2013, now supports Java, JavaScript, Python, Go, .NET, and more) that enables API consumers to define contracts and providers to verify them — without requiring both services to be deployed simultaneously. Core components: **Pact Consumer Library** — DSL for writing consumer tests that generate `.json` pact files describing expected interactions; **Pact Provider Library** — runs provider verification tests by replaying pact interactions against the real provider implementation; **Pact Broker** — a server (self-hosted or PactFlow SaaS) that stores contracts, tracks which provider versions have verified which consumer contracts, provides webhooks (trigger provider CI when consumer publishes new pact), and implements the `can-i-deploy` query ("is it safe to deploy service X version Y to environment Z?"). Pact supports both HTTP/REST contracts and messaging (Kafka, SQS) contracts. The `can-i-deploy` tool queries the Broker's compatibility matrix and fails CI if deploying a service would break any consumer.

---

### 🟢 Simple Definition (Easy)

Pact is the tool that makes Consumer-Driven Contract Testing practical. Consumers write tests using the Pact library → these tests automatically generate contract files. Those files are uploaded to the Pact Broker. When providers change their code, their CI downloads consumer contracts from the Broker and runs them against the new code. If any contract breaks: CI fails. No deployment until contracts are satisfied.

---

### 🔵 Simple Definition (Elaborated)

`OrderService` (consumer) has Pact tests: "I call `GET /customers/123` and I expect `{id, name, tier}`." These tests pass locally and generate `OrderService-CustomerService.json`. This file is published to the Pact Broker. `CustomerService` developer makes a change, runs CI. CI fetches `OrderService-CustomerService.json` from the Broker and verifies: does the changed `CustomerService` still return `{id, name, tier}` for `GET /customers/123`? If yes → CI passes, can deploy. If no (e.g., `name` renamed to `fullName`) → CI fails. `CustomerService` cannot deploy until `OrderService` updates its contract or `CustomerService` maintains backward compatibility.

---

### 🔩 First Principles Explanation

**Pact matching rules — flexible contract verification:**

```
EXACT MATCHING (default without rules):
  Consumer expects: {"name": "Alice Smith", "tier": "GOLD"}
  Provider returns: {"name": "Alice Smith", "tier": "GOLD"}
  → PASS

  Problem: test data coupling. Consumer's test knows the exact provider test data.
  Brittle: provider changes test data → contract fails (false negative)

MATCHING RULES (flexible matching — recommended):

  TYPE MATCHING:
  Consumer expects type String for "name" (any string value):
  "matchingRules": {"body": {"$.name": {"matchers": [{"match": "type"}]}}}
  Provider returns: {"name": "Bob Jones"} → PASS (type matches: string)
  Provider returns: {"name": 12345} → FAIL (type mismatch: number ≠ string)

  REGEX MATCHING:
  Consumer expects "tier" to match BRONZE|SILVER|GOLD:
  "matchingRules": {"body": {"$.tier": {"matchers": [{"match": "regex", "regex": "BRONZE|SILVER|GOLD"}]}}}
  Provider returns: {"tier": "SILVER"} → PASS
  Provider returns: {"tier": "PLATINUM"} → FAIL

  INTEGER MATCHING:
  "matchingRules": {"body": {"$.count": {"matchers": [{"match": "integer"}]}}}
  Provider returns: {"count": 42} → PASS
  Provider returns: {"count": "42"} → FAIL (string ≠ integer)

  ARRAY CONTAINS MATCHING:
  Consumer expects items array to contain at least one element of a specific type.
  Doesn't mandate exact length.
  Useful when provider returns dynamic-length lists.

BEST PRACTICE:
  Use type/regex matching (not exact value matching) for all fields in Pact contracts.
  Exact matching = brittle; type matching = resilient.
```

**Provider states — setting up test data for verification:**

```java
// Provider state declarations in CustomerService verification:
@State("customer cust-123 exists and is GOLD tier")
void setupGoldCustomer() {
    customerRepository.deleteAll();  // clean state
    customerRepository.save(new Customer(
        "cust-123", "Alice Smith", CustomerTier.GOLD, "alice@example.com"
    ));
}

@State("no customers exist")
void setupEmptyCustomers() {
    customerRepository.deleteAll();
}

@State("customer cust-DELETED is deleted")
void setupDeletedCustomer() {
    customerRepository.deleteAll();
    // Customer doesn't exist → 404 expected by consumer
}

// WHY PROVIDER STATES MATTER:
// Consumer pact says: "given customer cust-123 exists, GET /customers/cust-123 → 200"
// Without provider state setup: cust-123 might not exist in test DB → 404 returned → FAIL
// Provider state handler: ensures data exists before interaction is verified
// Allows provider to use its real DB (embedded H2 or TestContainers PostgreSQL)
```

**Pact Broker — the coordination layer:**

```
PACT BROKER CAPABILITIES:

1. CONTRACT STORAGE:
   Published contracts are versioned by consumer version (git SHA or semver).
   URL: /pacts/provider/CustomerService/consumer/OrderService/latest
   UI: visual matrix of consumer/provider compatibility

2. COMPATIBILITY MATRIX:
   Rows: consumer versions
   Columns: provider versions
   Cells: verification result (PASS/FAIL/PENDING) + date

   Example:
   OrderService v1.2.3 × CustomerService v2.0.0 → VERIFIED ✅
   OrderService v1.2.3 × CustomerService v2.1.0 → FAILED ❌ (name field missing)
   OrderService v1.3.0 × CustomerService v2.1.0 → VERIFIED ✅ (after consumer updated)

3. CAN-I-DEPLOY:
   Query: "Can I deploy OrderService v1.2.3 to production?"
   Logic: Is there a compatible verification for the provider versions
          currently deployed in the production environment?
   Returns: YES → deploy allowed; NO → deploy blocked

4. WEBHOOKS:
   Consumer publishes new pact → Broker fires webhook → triggers CustomerService CI
   Provider doesn't need to poll for new contracts; automatically notified.

5. PENDING PACTS:
   New consumer (AnalyticsService) publishes pact against CustomerService.
   CustomerService CI picks up this pact for the first time.
   Without pending: CustomerService CI FAILS immediately (new unverified pact)
   With pending pacts enabled: new unverified pacts don't FAIL provider CI.
   Provider can verify at its own pace; pact becomes "non-pending" once verified.
   Prevents new consumers from blocking provider deployments.
```

**Pact for messaging (Kafka/async events):**

```java
// Consumer (InventoryService) — defines expected event format from OrderService:
@Pact(provider = "OrderService", consumer = "InventoryService")
MessagePact orderPlacedEventPact(MessagePactBuilder builder) {
    return builder
        .given("an order is placed")
        .expectsToReceive("an OrderPlaced event")
        .withContent(new PactDslJsonBody()
            .stringType("eventType", "OrderPlaced")
            .stringType("orderId")
            .stringType("customerId")
            .stringType("productId")
            .numberType("quantity")
            .decimalType("totalAmount"))
        .toPact();
}

@Test
@PactTestFor(pactMethod = "orderPlacedEventPact", providerType = ProviderType.ASYNCH)
void shouldHandleOrderPlacedEvent(List<Message> messages) {
    // InventoryService processes the event defined in the pact:
    OrderPlacedEvent event = objectMapper.readValue(
        messages.get(0).getContents().valueAsString(), OrderPlacedEvent.class
    );
    inventoryEventHandler.handle(event);
    verify(inventoryService).reserve(event.getProductId(), event.getQuantity());
}

// Provider (OrderService) — verifies it publishes events matching the pact:
@Provider("OrderService")
@PactFolder("target/pacts")
class OrderServiceMessagingPactTest {
    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verifyPact(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @State("an order is placed")
    @PactVerifyProvider("an OrderPlaced event")
    String generateOrderPlacedEvent() {
        OrderPlacedEvent event = new OrderPlacedEvent(
            "OrderPlaced", "ord-123", "cust-456", "prod-789", 2, new BigDecimal("49.99")
        );
        return objectMapper.writeValueAsString(event);
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

Before Pact, teams ran integration test environments with all services deployed. These environments were slow to provision, frequently broken, and required coordination between teams to use. Pact provides the benefits of integration testing (cross-service contract verification) with the speed and isolation of unit testing. It operationalizes the "you can deploy independently if your contracts are satisfied" principle of microservices.

---

### 🧠 Mental Model / Analogy

> Pact is like a formalized exchange of "I need X from you" notes between teams. `OrderService` team writes: "I need you to return `{id, name, tier}` when I call `GET /customers/{id}`." They put this in a shared folder (Pact Broker). When `CustomerService` team changes their code, they automatically check the shared folder and verify their new code still delivers everything on the "need" notes. `can-i-deploy` is the gatekeeper: "before you ship your changes, check every team that depends on you has confirmed your new version works for them."

---

### ⚙️ How It Works (Mechanism)

**Complete Pact workflow in a single CI/CD pipeline:**

```
┌─────────────────────────────────────────────────────┐
│  CONSUMER CI (OrderService)                         │
│                                                     │
│  1. Run unit tests (including Pact consumer tests)  │
│  2. Pact consumer tests → generate pact JSON files  │
│  3. Publish pacts to Pact Broker (with git SHA)     │
│  4. can-i-deploy?                                   │
│     → Check Broker: has CustomerService verified    │
│       the latest OrderService pact?                 │
│     → If YES: proceed to deploy                     │
│     → If NO: WAIT (or FAIL) — provider hasn't       │
│              verified new contract yet              │
│  5. Deploy OrderService to environment              │
│  6. Record deployment in Broker:                    │
│     pact-broker record-deployment \                 │
│       --environment production \                    │
│       --pacticipant OrderService \                  │
│       --version <git-sha>                           │
└─────────────────────────────────────────────────────┘

             Pact Broker webhook fires ↓

┌─────────────────────────────────────────────────────┐
│  PROVIDER CI (CustomerService)                      │
│                                                     │
│  (Triggered by: pact published OR own code change)  │
│  1. Run unit tests                                  │
│  2. Run Pact provider verification:                 │
│     → Fetch all consumer pacts from Broker          │
│     → For each pact: setup provider state           │
│     → Replay consumer interactions against          │
│        running CustomerService                      │
│     → Report PASS/FAIL to Broker                    │
│  3. If ALL pacts pass: can-i-deploy?                │
│     → Check Broker: compatible with prod consumers? │
│  4. Deploy CustomerService                          │
│  5. Record deployment in Broker                     │
└─────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
Consumer-Driven Contract Testing
(the pattern)
        │
        ▼
Pact (Contract Testing)  ◄──── (you are here)
(the framework implementing the pattern)
        │
        ├── Pact Broker → stores + manages contracts + can-i-deploy
        ├── CI-CD Pipeline → where consumer tests + provider verification run
        └── Service Contract → what Pact verifies
```

---

### 💻 Code Example

**Maven POM configuration for Pact:**

```xml
<dependency>
    <groupId>au.com.dius.pact.consumer</groupId>
    <artifactId>junit5</artifactId>
    <version>4.6.7</version>
    <scope>test</scope>
</dependency>

<plugin>
    <groupId>au.com.dius.pact.provider</groupId>
    <artifactId>maven</artifactId>
    <version>4.6.7</version>
    <configuration>
        <serviceProviders>
            <serviceProvider>
                <name>CustomerService</name>
                <protocol>http</protocol>
                <host>localhost</host>
                <port>8080</port>
                <path>/</path>
                <pactBrokerUrl>https://pact-broker.internal</pactBrokerUrl>
                <pactBrokerToken>${env.PACT_BROKER_TOKEN}</pactBrokerToken>
            </serviceProvider>
        </serviceProviders>
        <projectVersion>${git.commit.id}</projectVersion>
        <publishVerificationResults>true</publishVerificationResults>
    </configuration>
</plugin>
```

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pact tests are slow because they need real services running   | Consumer tests run against a Pact mock server (no real service needed — milliseconds). Provider verification runs against the real provider in isolation (no other services needed). Both are fast unit-test speed                                                                                |
| Pact Broker requires PactFlow (paid)                          | The Pact Broker is open-source and self-hostable (Docker image available). PactFlow is a commercial hosted version with additional features (RBAC, teams, secrets management). Self-hosted Pact Broker is sufficient for most organisations                                                       |
| Pact tests need to cover every field in the provider response | Consumer tests should declare ONLY the fields the consumer actually uses. If `OrderService` only reads `id`, `name`, and `tier` from the customer response, the pact should only declare those three fields — not the full customer object. This is the "be lenient in what you accept" principle |
| Pact replaces OpenAPI/Swagger documentation                   | Pact contracts represent what consumers actually use (subset of API). OpenAPI describes the full API surface for discoverability and human documentation. Both have value and are complementary                                                                                                   |

---

### 🔥 Pitfalls in Production

**Pact tests not run in CI, or bypassed by teams:**

```
SCENARIO:
  Pact tests exist for OrderService-CustomerService contract.
  CustomerService team under deadline pressure.
  CI is "slow" — team merges directly to main, bypassing CI.
  CustomerService deployed with breaking change (renamed field).
  OrderService: production failures start immediately after deployment.
  Post-mortem: Pact tests WOULD have caught this, but CI was bypassed.

PREVENTION:
  1. Branch protection rules: require CI to pass before merge (GitHub/GitLab settings)
  2. can-i-deploy gate in deployment pipeline (not just CI):
     Deployment scripts: always call `pact-broker can-i-deploy` before deploy
     Cannot bypass via git operations — checked at deployment time
  3. Make Pact tests fast (< 5 seconds) — slow tests tempt bypassing
  4. Team culture: contract tests are production safety nets, not optional ceremony

PACT TEST EXECUTION TIME OPTIMIZATION:
  - Consumer tests: mock server → < 100ms per test
  - Provider verification: use TestContainers for DB (parallel startup) → < 30s total
  - Caching: cache provider state between pact interactions where safe
  - Parallel verification: multiple consumer pacts verified in parallel
```

---

### 🔗 Related Keywords

- `Consumer-Driven Contract Testing` — the pattern that Pact implements
- `CI-CD Pipeline` — where Pact tests execute and can-i-deploy gates deployments
- `Service Contract` — the formal API agreement that Pact verifies
- `Backward Compatibility` — maintaining backward compatibility ensures Pact contracts continue to pass

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PACT CONSUMER│ Write test → PactDsl DSL → pact.json      │
│ PACT PROVIDER│ Fetch pact.json → verify interactions     │
│ PACT BROKER  │ Store contracts + track verifications     │
├──────────────┼───────────────────────────────────────────┤
│ can-i-deploy │ Safe to deploy? (checks broker matrix)    │
│ MATCHING     │ Use type/regex matching (not exact values) │
├──────────────┼───────────────────────────────────────────┤
│ SUPPORTS     │ HTTP REST + Messaging (Kafka, SQS)         │
│ LANGUAGES    │ Java, JS/TS, Python, Go, Ruby, .NET        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your organisation has 30 microservices with Pact contracts between them. The Pact Broker shows a compatibility matrix of 30 × 30 = 900 potential relationships. On average, each service has 5 consumers. You push a change to `UserService` (consumed by 15 services). The provider verification job takes 45 seconds per consumer contract. Sequential execution: 11 minutes to verify all 15 consumer contracts. How would you architect the provider verification job to run all 15 verifications in parallel in your CI/CD pipeline? What are the constraints (test data isolation, database state) that make parallelisation complex?

**Q2.** Your consumer-driven contract tests use exact value matching (not type matching) because an early developer didn't know about matching rules. Your provider verification fails whenever the provider changes test data. The team treats these as "noise" and re-runs CI until it passes. How do you migrate 200 existing pact interactions from exact matching to type matching without breaking the tests? Is there a Pact tool or migration path? What is the rollout strategy: fix all at once or service-by-service?
