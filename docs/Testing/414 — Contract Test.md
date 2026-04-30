---
layout: default
title: "Contract Test"
parent: "Testing"
nav_order: 414
permalink: /testing/contract-test/
number: "414"
category: Testing
difficulty: ★★★
depends_on: Integration Test, Consumer-Driven Contracts
used_by: Microservices, CI/CD, API Versioning
tags: #testing #advanced #microservices #contracts
---

# 414 — Contract Test

`#testing` `#advanced` `#microservices` `#contracts`

⚡ TL;DR — A test that verifies a service's API matches the expectations of its consumers — catching integration breaks without deploying both services together.

| #414 | Category: Testing | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Integration Test, Consumer-Driven Contracts | |
| **Used by:** | Microservices, CI/CD, API Versioning | |

---

### 📘 Textbook Definition

A Contract Test verifies that a service (provider) fulfills the expectations defined by its consumers. In Consumer-Driven Contract Testing (CDCT), each consumer defines the subset of the provider's API it depends on as a "contract" (Pact file). The provider runs these contracts as tests in its own pipeline — catching breaking changes before deployment, without needing both services running simultaneously.

---

### 🟢 Simple Definition (Easy)

Contract tests ensure **Service A's API still matches what Service B expects** — catching integration breaks automatically, without spinning up both services at the same time.

---

### 🔵 Simple Definition (Elaborated)

In microservices, E2E tests require all services running together — slow and brittle. Contract tests split this: the consumer defines what it needs (the contract), and the provider verifies it can satisfy that contract independently. When the provider changes its API, contract tests fail immediately in CI — long before any E2E test or deployment would catch it.

---

### 🔩 First Principles Explanation

**The core problem:**
Service A calls Service B. Service B changes its response structure. Service A breaks in production because nobody tested the integration point directly.

**The insight:**
> "Consumer-driven: let the consumer codify exactly what it needs. Provider verifies it delivers exactly that — independently, in its own pipeline."

```
Consumer (Order Service) defines:
  "When I call GET /users/1, I expect { id: 1, email: String }"

Provider (User Service) verifies:
  "My GET /users/1 endpoint returns { id: 1, email: String }"
  → Contract passes → safe to deploy

Provider changes email → name:
  → Contract fails in User Service pipeline
  → Order Service is notified before any deployment
```

---

### ❓ Why Does This Exist (Why Before What)

Without contract tests, API breaking changes are discovered only in E2E tests or production. With contract tests, the provider's pipeline fails the moment a breaking change is introduced — no E2E environment needed, no services started together, fast feedback.

---

### 🧠 Mental Model / Analogy

> Contract tests are like a written rental agreement. The tenant (consumer) specifies exactly what the apartment (provider) must include — working heating, internet. The landlord (provider) can renovate the apartment however they like, as long as the contract terms are still met. If they remove the heating, the contract fails before the tenant moves in.

---

### ⚙️ How It Works (Mechanism)

```
Pact (Consumer-Driven Contract Testing) workflow:

  1. Consumer writes interaction test:
     "When I call GET /users/1, the provider returns { id:1, email:'...' }"
     → Pact library records this as a Pact file (JSON contract)
     → Consumer test uses a mock provider server (no real Service B needed)

  2. Pact file published to Pact Broker (centralized contract registry)

  3. Provider verifies the Pact:
     "Can I satisfy all consumer contracts for my current code?"
     → Pact replays the consumer's expected requests against the real provider
     → If provider response matches contract → PASS
     → If not → FAIL → pipeline blocked

  4. Pact Broker tracks which versions are compatible:
     "Can I deploy Consumer v1.2 with Provider v2.1?"
```

---

### 🔄 How It Connects (Mini-Map)

```
[Consumer writes interaction]
       ↓
[Pact file generated + published]
       ↓
[Provider verifies Pact in its pipeline]
       ↓ PASS                ↓ FAIL
[Can-I-Deploy: YES]    [Provider pipeline blocked]
       ↓
[Deploy independently]
```

---

### 💻 Code Example

```java
// Consumer side — Order Service (Java + Pact)
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "UserService")
class OrderServiceContractTest {

    @Pact(consumer = "OrderService")
    public RequestResponsePact getUserPact(PactDslWithProvider builder) {
        return builder
            .given("user 1 exists")
            .uponReceiving("a request for user 1")
                .path("/users/1")
                .method("GET")
            .willRespondWith()
                .status(200)
                .body(new PactDslJsonBody()
                    .integerType("id", 1)
                    .stringType("email", "alice@example.com")
                    // Note: ONLY fields OrderService needs — not the full user object
                )
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "getUserPact")
    void orderServiceCanFetchUser(MockServer mockServer) {
        // Act: call the mock provider (no real UserService needed)
        User user = new UserClient(mockServer.getUrl()).getUser(1);

        // Assert: consumer can process the response
        assertThat(user.getId()).isEqualTo(1);
        assertThat(user.getEmail()).isNotEmpty();
    }
}

// Provider side — User Service verifies the Pact
@Provider("UserService")
@PactBroker(url = "https://pact-broker.internal")
@SpringBootTest(webEnvironment = RANDOM_PORT)
class UserServicePactVerificationTest {

    @TestTarget
    public final Target target = new SpringBootHttpTarget();

    @State("user 1 exists")
    void setupUserExists() {
        // Ensure user 1 is in the test database
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Contract tests = API documentation tests | Contract tests test live behavior, not documented specs |
| Provider defines the contract | Consumer-driven: consumers define what THEY need |
| Contract tests replace E2E tests | They complement — contract tests catch API breaks; E2E tests confirm user flows |
| Only REST APIs need contract tests | gRPC, GraphQL, and message-based APIs also benefit from contract tests |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Provider-Driven Contracts**
Team writes contracts from the provider's perspective — misses what consumers actually use.
Fix: always consumer-driven; providers verify consumer-defined contracts, not their own.

**Pitfall 2: Overly Strict Consumer Contracts**
Consumer asserts on every field — provider can't add new fields without breaking contracts.
Fix: use flexible matching (`stringType`, `integerType`) not exact values; only assert on fields the consumer uses.

**Pitfall 3: Pact Broker Not Used**
Teams share Pact files via git — versioning and compatibility tracking becomes unmanageable.
Fix: use a Pact Broker (or PactFlow); it tracks which consumer/provider version combinations are compatible.

---

### 🔗 Related Keywords

- **Integration Test** — contract tests are a specialized form targeting service-to-service boundaries
- **Pact** — the most widely used consumer-driven contract testing framework
- **Consumer-Driven Contracts** — the principle: consumers define what they need
- **Microservices** — the architecture where contract tests provide the most value
- **E2E Test** — contract tests reduce the need for brittle E2E tests

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Consumer defines what it needs; provider      │
│              │ verifies it can deliver — independently       │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Microservices with multiple teams; API changes │
│              │ that could break consumers                    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Monoliths with in-process calls (no API boundary)│
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Consumer owns the contract; provider verifies │
│              │  it — no shared environment needed"           │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Pact --> Pact Broker --> Consumer-Driven CDCs  │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** Why is consumer-driven contract testing more effective than provider-defined contract testing?  
**Q2.** How does the "can-i-deploy" check in Pact Broker prevent breaking deployments?  
**Q3.** What happens to existing contracts when a provider adds a new field to its response?

