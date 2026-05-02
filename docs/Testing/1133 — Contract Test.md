---
layout: default
title: "Contract Test"
parent: "Testing"
nav_order: 1133
permalink: /testing/contract-test/
number: "1133"
category: Testing
difficulty: ★★★
depends_on: Integration Test, HTTP and APIs, Microservices
used_by: Microservices, Consumer-Driven Contract Testing, CI-CD
related: Pact, Spring Cloud Contract, CDC Testing, Consumer, Provider
tags:
  - testing
  - microservices
  - contracts
  - pact
---

# 1133 — Contract Test

⚡ TL;DR — A contract test verifies that a service (provider) honours the API expectations of its consumers, without deploying both together — enabling microservices teams to deploy independently with confidence.

| #1133           | Category: Testing                                            | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Integration Test, HTTP and APIs, Microservices               |                 |
| **Used by:**    | Microservices, Consumer-Driven Contract Testing, CI-CD       |                 |
| **Related:**    | Pact, Spring Cloud Contract, CDC Testing, Consumer, Provider |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Microservice A (consumer) calls Microservice B (provider). Team B updates B's response schema — removes the `email` field because they don't need it anymore. Team B's unit and integration tests all pass. Team A's unit tests mock B's response — they still pass. The bug is only discovered when both services are deployed together in staging and A's JSON deserialisation fails. Now both teams are blocked, debugging cross-service compatibility in a shared environment.

THE BREAKING POINT:
At 10 microservices, the interaction matrix is 45 pairs. A shared staging environment can't test all 45 interactions reliably. E2E tests are too slow and fragile. The solution: each consumer defines its expectations (contract) in a portable format; the provider verifies it meets all consumers' contracts before deploying. Neither team needs the other deployed.

THE INVENTION MOMENT:
Consumer-Driven Contract Testing (Beth Skurrie, 2011 at REA Group) and the Pact framework (2014) formalised the pattern: consumer generates a pact file (expectations), provider verifies against the pact file. Teams can deploy independently with confidence that contracts are honoured.

---

### 📘 Textbook Definition

A **contract test** (specifically **Consumer-Driven Contract test**) is a testing methodology for distributed systems where: (1) the **consumer** (calling service) writes a test that records its expectations of a **provider** (called service) as a **contract** (Pact file, Spring Cloud Contract stub); (2) the **provider** runs the consumer's contract against its real implementation, verifying it meets all consumers' expectations without deploying the consumer.

**Consumer-Driven** means consumers specify what they need, not what the provider offers. The provider may return more fields than the consumer needs — as long as it returns at least what consumers require. This prevents breaking changes while allowing additive changes (adding new fields).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Contract test = consumer writes its expectations as a test; provider proves it meets those expectations — no shared environment needed.

**One analogy:**

> A supplier contract in business: the buyer specifies exactly what they need (dimensions, tolerances, delivery schedule). The supplier doesn't need the buyer present to verify they can meet the spec — they test their product against the spec. If the product passes the spec, the supplier can ship independently.

**One insight:**
Pact specifically tests that the consumer can parse what the provider actually returns — not that the provider's full API works. Pact tests are narrower than E2E tests (which verify full user flows) but catch the specific class of bugs that cause consumer parse failures.

---

### 🔩 First Principles Explanation

PACT WORKFLOW:

```
CONSUMER SIDE (Service A tests):
  1. Consumer test: mock the provider using Pact mock server
     → consumer sends request to mock server
     → mock server returns Pact-configured response
     → consumer code parses response → assertions pass
  2. Pact records the interaction: {request, response} → pact.json
  3. Pact file published to Pact Broker (shared registry)

PROVIDER SIDE (Service B CI):
  1. Provider verifies:
     → Load pact.json for Service A from Pact Broker
     → Replay recorded request against real Service B
     → Compare actual response to pact's expected response
     → PASS: B returns what A needs
     → FAIL: B's response breaks A's contract
  2. Record verification result in Pact Broker

CAN I DEPLOY? (Pact Broker):
  → Service A: all providers verified my contract? YES → deploy
  → Service B: all consumers' contracts verified? YES → deploy
  → No: deployment blocked
```

MATCHING RULES (key feature):
Contract test with flexible matching (not exact values):

```json
{
  "matchingRules": {
    "$.body.userId": { "match": "type" }, // any string
    "$.body.email": { "match": "regex", "regex": "^\\S+@\\S+$" },
    "$.body.amount": { "match": "decimal" } // any decimal number
  }
}
```

This prevents brittle tests that fail when the provider returns different but valid values.

THE TRADE-OFFS:
Gain: Teams deploy independently; catches interface breaking changes before staging; documents API expectations explicitly.
Cost: Requires Pact Broker infrastructure; test setup complexity; contracts are limited to request/response matching (not business logic); teams must share and update contracts.

---

### 🧪 Thought Experiment

BREAKING CHANGE DETECTION:

```
Current contract (from consumer A's pact file):
  GET /users/123 → {userId: "123", email: "...", plan: "premium"}

Provider B's team removes 'plan' field (not in their DB anymore):
  GET /users/123 → {userId: "123", email: "..."}

Without contract test:
  → B's tests: all pass (B doesn't test what A needs)
  → A's unit tests: all pass (mock returns plan field)
  → In staging: A fails to deserialize, NullPointerException on plan
  → Both teams blocked for hours

With contract test:
  → B runs pact verification
  → Pact replays A's request, compares actual response
  → FAIL: 'plan' field missing from provider response
  → B's CI fails BEFORE B deploys → caught by B's team
  → B either: keeps 'plan', coordinates deprecation, or contacts A
```

---

### 🧠 Mental Model / Analogy

> Contract testing is like a restaurant **order slip system**. The waiter (consumer) writes exactly what the customer ordered on the slip (contract). The kitchen (provider) must verify they can fulfil any slip before the restaurant opens. The kitchen tests: "can we make order X from slip X?" — without needing the actual customer present. If the kitchen can fulfil every possible slip from every waiter, they can open with confidence.

> Pact Broker is the slip archive: all historical order slips are stored, and the kitchen must verify against all of them.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Contract tests check that when Service A calls Service B, B returns exactly what A expects. This lets teams work independently — B doesn't need A running to verify compatibility.

**Level 2:** Use Pact (pact-jvm for Java). Consumer writes `@PactTestFor` test → generates pact.json. Provider runs `@Provider` test that loads pact.json. Publish to Pact Broker (hosted: pactflow.io, self-hosted). Use `can-i-deploy` CLI before each deployment. Matching rules: use `PactDslJsonBody` for flexible matching (not exact values).

**Level 3:** Pact specification v3 adds message contracts (Kafka/async). Provider states: before replaying the request, provider sets up specific state (e.g., "user 123 exists with premium plan"). State is communicated via `@State` annotation + a state change endpoint. Provider test calls the state handler before replaying each interaction. This decouples provider's test data setup from consumer's contract.

**Level 4:** Consumer-Driven Contracts are about **collaborative API design**, not just testing. The consumer's pact file is a negotiation: "this is what I need — can you provide it?" When a consumer adds a new field expectation, the provider team sees this via the Pact Broker. The conversation happens around contract changes, not production incidents. The Pact Broker's "can-i-deploy" endpoint implements a compatibility matrix: for any pair (consumer version, provider version), it checks all interaction verifications. This enables the branching strategy: main → main compatibility is verified; feature branches are checked against main before merge.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│                  PACT VERIFICATION FLOW                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  CONSUMER (Service A CI):                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  @PactTestFor: mock server at localhost:8080      │   │
│  │  Consumer code → HTTP GET /users/123              │   │
│  │  Mock server → returns pact-configured response   │   │
│  │  Consumer parses response → assertions pass        │   │
│  │  → Generates: service-a-service-b.json (pact)     │   │
│  │  → Publishes to Pact Broker                        │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼ (pact file)                  │
│  PACT BROKER: pactflow.io / self-hosted                  │
│                          │                              │
│                          ▼                              │
│  PROVIDER (Service B CI):                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  @Provider: starts real Service B on random port  │   │
│  │  Loads pact file from Broker                      │   │
│  │  For each interaction in pact:                    │   │
│  │    → Run @State setup                             │   │
│  │    → Replay request against real Service B        │   │
│  │    → Compare actual response to pact expected     │   │
│  │    → PASS / FAIL                                  │   │
│  │  → Records result in Pact Broker                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  CAN I DEPLOY? (before each deployment):                │
│    pact-broker can-i-deploy --pacticipant ServiceB      │
│    --version 1.2.3 --to-environment production          │
│    → PASS: all consumers verified → deploy safely       │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
1. Consumer test (UserServiceConsumerTest.java):
   @Pact(consumer="UserService", provider="AuthService")
   RequestResponsePact getUserPact(PactDslWithProvider builder) {
       return builder.given("user 123 exists")
           .uponReceiving("GET user 123")
           .path("/users/123").method("GET")
           .willRespondWith().status(200)
           .body(new PactDslJsonBody()
               .stringType("userId")
               .stringType("email")
               .booleanType("active"))
           .toPact();
   }

2. Pact file generated: user-service-auth-service.json
3. Published to PactFlow with git commit SHA as version

4. Provider test (AuthServiceProviderTest.java):
   @Provider("AuthService") @PactBroker
   class AuthServiceContractTest {
       @TestTarget public final HttpTarget target = new HttpTarget(port);

       @State("user 123 exists")
       void userExists() { testUserRepository.save(testUser("123")); }
   }

5. Provider verifies: GET /users/123 response matches pact
6. can-i-deploy passes for both services → deploy
```

---

### 💻 Code Example

```java
// CONSUMER SIDE
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "UserService", port = "8080")
class UserClientContractTest {

    @Pact(consumer = "OrderService")
    public RequestResponsePact getUserPact(PactDslWithProvider builder) {
        return builder
            .given("user alice exists and is active")
            .uponReceiving("request for user alice")
                .path("/users/alice").method("GET")
            .willRespondWith()
                .status(200)
                .body(new PactDslJsonBody()
                    .stringType("userId", "alice")       // type-based matching
                    .stringMatcher("email", ".*@.*", "alice@example.com")
                    .booleanType("active", true)
                    .decimalType("creditLimit", 500.0))
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "getUserPact")
    void getUser_activeUser_parsedCorrectly(MockServer mockServer) {
        UserClient client = new UserClient("http://localhost:" + mockServer.getPort());
        User user = client.getUser("alice");

        assertThat(user.getUserId()).isNotBlank();
        assertThat(user.getEmail()).contains("@");
        assertThat(user.isActive()).isTrue();
    }
}

// PROVIDER SIDE
@Provider("UserService")
@PactBroker(url = "${PACT_BROKER_URL}", authentication = @PactBrokerAuth(token = "${PACT_TOKEN}"))
@SpringBootTest(webEnvironment = RANDOM_PORT)
class UserServiceProviderTest {

    @LocalServerPort int port;

    @BeforeEach
    void setUp(PactVerificationContext context) {
        context.setTarget(new HttpTestTarget("localhost", port));
    }

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verifyPact(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @State("user alice exists and is active")
    void userAliceExists() {
        userRepository.save(User.builder()
            .userId("alice").email("alice@example.com").active(true)
            .creditLimit(new BigDecimal("500.00")).build());
    }
}
```

---

### ⚖️ Comparison Table

| Test Type        | Tests What                  | Environment         | Speed   | Coupling    |
| ---------------- | --------------------------- | ------------------- | ------- | ----------- |
| Unit test        | Business logic              | None (mocks)        | <100ms  | None        |
| Contract test    | API interface compatibility | Provider only       | 1–10s   | Pact Broker |
| Integration test | Real DB/service behavior    | Docker              | 5–30s   | Docker      |
| E2E test         | Full user flow              | Full stack deployed | Minutes | Full stack  |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                           |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| "Contract tests replace E2E tests"             | They complement; contract tests verify interface; E2E tests verify business flows                 |
| "Pact tests all edge cases of the provider"    | Pact only tests what the consumer uses; not the provider's full API surface                       |
| "Provider breaking its own contract is caught" | Only if consumers test for that behavior; new provider features not consumed won't be in any pact |
| "Contract tests are only for HTTP"             | Pact v3/v4 supports async messaging (Kafka, SQS) contracts too                                    |

---

### 🚨 Failure Modes & Diagnosis

**1. Pact Verification Fails After Provider Refactor**

Symptom: Provider CI fails with "body mismatch: field X not found".

Diagnosis: Provider removed/renamed a field that a consumer's contract expects. Check Pact Broker for which consumers depend on the field.

Resolution: Either keep the field (backward compatibility), add to provider response, or negotiate contract change with consumer team.

**2. Provider States Not Set Up Correctly**

Symptom: Pact verification returns 404 for resources that should exist.

Root Cause: `@State` handler doesn't create the test data correctly, or test is using wrong database.

Fix: Add logging in state handler, verify state setup creates expected data before request replay.

---

### 🔗 Related Keywords

- **Prerequisites:** Integration Test, HTTP and APIs, Microservices
- **Builds on:** Pact (Contract Testing), Spring Cloud Contract, Pact Broker
- **Alternatives:** E2E Test (higher fidelity, slower), Integration Test (requires both services)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Consumer writes expectations; provider   │
│              │ verifies it meets them — no shared env   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Consumer-Driven: consumer specifies what  │
│              │ it needs; provider proves it delivers it  │
├──────────────┼───────────────────────────────────────────┤
│ TOOL         │ Pact (pact-jvm) + Pact Broker / PactFlow │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Independent deployment vs Pact Broker    │
│              │ infrastructure + contract maintenance    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Consumer's expectations, provider       │
│              │  verified — deploy independently"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pact → Pact Broker → Spring Cloud Contract│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Pact's consumer test runs against a Pact mock server — which means the consumer test never touches the real provider. The contract (pact file) records what the consumer sent and what it expected to receive. The provider verification replays the exact request and compares the actual response. But what if the consumer sends a request with a body that contains fields the provider doesn't care about, or the provider's response headers include new headers the consumer didn't expect? Describe Pact's content-type negotiation and response body matching in detail: what happens to unexpected response fields (they are ignored by default — additive changes are safe), what happens to unexpected request fields (provider receives them — safe), and how `PactDslJsonBody.minArrayLike()` prevents brittleness in array responses.

**Q2.** Spring Cloud Contract takes the opposite approach from Pact: the **provider** defines contracts (in Groovy DSL or YAML), and the framework generates both provider verification tests AND consumer stubs (WireMock mappings). The consumer uses the generated WireMock stub to test against. This is "Provider-Driven Contract Testing". Compare the two approaches: (a) In CDC (Consumer-Driven, Pact): who discovers breaking changes first? (b) In Provider-Driven (Spring Cloud Contract): what prevents provider teams from writing contracts that their consumers don't actually use? (c) For a mature microservices ecosystem with 50 services, which approach scales better and why? Provide a specific scenario where each approach is superior.
