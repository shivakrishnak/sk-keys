---
layout: default
title: "API Contract Testing (Pact / Karate)"
parent: "Testing"
nav_order: 52
permalink: /testing/api-contract-testing/
number: "TST-052"
category: Testing
difficulty: ★★★
depends_on: Testing, HTTP & APIs, Microservices
used_by: CI-CD, Microservices
related: Karate Framework (API Testing), Consumer-Driven Contracts, Integration Testing
tags:
  - testing
  - api
  - microservices
  - advanced
  - pattern
---

# TST-052 — API Contract Testing (Pact / Karate)

⚡ **TL;DR —** Contract testing verifies that a service consumer and its provider agree on an API shape, catching breaking changes before they reach production.

| Field | Value |
|---|---|
| **Depends on** | Testing, HTTP & APIs, Microservices |
| **Used by** | CI-CD, Microservices |
| **Related** | Karate Framework (API Testing), Consumer-Driven Contracts, Integration Testing |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a microservices architecture, Team A owns `order-service` (consumer) and Team B owns `inventory-service` (provider). Team B renames a JSON field from `stockCount` to `availableQty`. They run their own tests — all green. Team A's service is never told. Production breaks silently at 2 a.m.

**THE BREAKING POINT:**
Integration test suites running both services together become the last safety net. But they are slow (minutes to spin up), expensive to maintain, brittle against data state, and owned by nobody. Teams start shipping slower just to coordinate manual API reviews.

**THE INVENTION MOMENT:**
Consumer-Driven Contract testing flips the model: the consumer defines the contract (what it needs), publishes it to a shared broker, and the provider verifies against it independently. Breaking changes are detected the moment the provider's pipeline runs — no shared environment needed.

---

### 📘 Textbook Definition

**API contract testing** is a testing technique that verifies the interface agreement between a service consumer and a service provider by recording the consumer's expectations as a formal contract and running those expectations against the provider in isolation. **Pact** implements consumer-driven contracts via a JSON pact file and a Pact Broker. **Karate** provides a BDD DSL for API functional and schema-validation tests that enforce structural contracts.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Consumer writes what it expects; provider proves it can deliver; the broker tracks who can deploy with whom.

> Contract testing is like a legal agreement between departments: accounting says "I need invoices in this exact format," and the billing team signs off that they will always produce that format.

**One insight:** Contract tests replace a shared integration environment with two independent fast-running unit-speed checks — one on the consumer side and one on the provider side — each deployable and verifiable without the other service running.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The consumer owns its expectations — it defines the minimal contract it needs.
2. The provider must satisfy every consumer contract that depends on it.
3. Contracts are versioned and stored externally so history is auditable.
4. `can-i-deploy` must pass before either service ships to production.

**DERIVED DESIGN:**
In Pact, consumer tests run against a mock provider, recording interactions as JSON. The pact file is published to a Pact Broker. The provider downloads the pact and replays each interaction against its real implementation. The broker computes a compatibility matrix.

**THE TRADE-OFFS:**
**Gain:** Decoupled team pipelines; instant breaking-change detection; no shared environment required; linear scaling with service count.
**Cost:** Initial tooling investment (broker setup, library integration); contracts must be kept current; not a substitute for end-to-end smoke tests.

---

### 🧪 Thought Experiment

**SETUP:** `payment-service` calls `user-service` to fetch `{ id, email, tier }`. You have 40 microservices. Team structure: 8 squads, each owning 5 services.

**WHAT HAPPENS WITHOUT CONTRACT TESTING:**
A squad renames `tier` to `subscriptionLevel` in `user-service`. Their unit tests pass. An integration environment runs weekly. `payment-service` silently receives `undefined` for tier and applies the wrong pricing logic. The regression surfaces in production after five days.

**WHAT HAPPENS WITH PACT:**
`payment-service` has a consumer pact specifying `{ id, email, tier }`. The moment `user-service` removes `tier` from its response, the provider verification step in their CI pipeline fails with: `Expected 'tier' in response body but was absent`. The PR is blocked. No integration environment needed.

**THE INSIGHT:**
Contract testing moves the integration feedback loop from a shared staging environment (slow, shared, stateful) to independent CI pipelines (fast, isolated, deterministic).

---

### 🧠 Mental Model / Analogy

> A Pact contract is like a USB-C specification: the phone manufacturer (consumer) publishes the exact pin layout it requires, and every charger maker (provider) must prove compliance before selling — neither party needs the other's product in hand during the test.

**Mapping:**
- USB-C specification document → pact JSON file
- Phone manufacturer's requirements → consumer test expectations
- Charger maker's compliance test → provider verification run
- USB-IF certification body → Pact Broker (stores and gates deployments)
- `can-i-deploy` check → certification lookup before market release

Where this analogy breaks down: USB-C is a hardware standard with a single governing body; in Pact each consumer team writes its own contract, so contracts can diverge or overlap across multiple consumers of one provider.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Two services agree on a written contract: "I will call you with this request, and you will reply with this response." Both teams test against the contract independently, so neither can accidentally break the other's integration.

**Level 2 — How to use it (junior developer):**
In JavaScript, install `@pact-foundation/pact`. Write a consumer test that uses `new PactV3()` to define expected interactions, then call your real consumer code against the mock. Run the test — a pact JSON file is generated. Publish it to a Pact Broker. Ask your provider team to add verification to their CI.

**Level 3 — How it works (mid-level engineer):**
The Pact library starts a local mock server during consumer tests. Your consumer code hits that mock. The library records each interaction (request matchers + expected response body + status). On the provider side, Pact replays each recorded request against the real provider, verifies the response matches the expected structure using matchers (not exact values), and reports pass/fail per interaction.

**Level 4 — Why it was designed this way (senior/staff):**
Traditional integration tests are brittle because they depend on data state and service availability. Pact uses *matchers* (type matchers, regex, arrays of minimum size) rather than exact values, so contracts survive normal data changes while still catching structural breaks. The Pact Broker's `can-i-deploy` command queries a compatibility matrix across all deployed versions — this is the key mechanism that makes independent deployment safe in a polyglot microservices fleet.

---

### ⚙️ How It Works (Mechanism)

```
CONSUMER SIDE                BROKER              PROVIDER SIDE
─────────────                ──────              ─────────────
Consumer test runs           Pact Broker         Provider CI runs
  │                              │                    │
  ▼                              │                    │
Mock Provider Server             │                    │
records interactions             │                    │
  │                              │                    │
  ▼                              │                    │
pact.json generated              │                    │
  │                              │                    │
  └──── publish ────────────────►│                    │
                                 │◄─── download ──────┘
                                 │                    │
                                 │          Provider verifies
                                 │          real impl vs pact
                                 │                    │
                             can-i-deploy?       pass / fail
```

**Pact matchers (not exact values):**
- `like(value)` — match type, not exact value
- `eachLike(item)` — array with at least one item matching structure
- `regex(pattern, value)` — field matches regex

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Consumer team pushes code
  │
  ▼
Consumer Pact test runs  ◄── YOU ARE HERE
  │ (mock provider records interactions)
  ▼
pact.json published to Pact Broker
  │
  ▼
Provider team pushes code
  │
  ▼
Provider verification fetches pact
  │ (replays requests against real service)
  ▼
All interactions pass
  │
  ▼
Broker marks version: VERIFIED ✅
  │
  ▼
can-i-deploy: PASS → both services deploy
```

**FAILURE PATH:**
Provider renames a field → verification fails → `can-i-deploy` returns `NO` for provider version → provider deployment is blocked → provider team is notified with exact failing interaction.

**WHAT CHANGES AT SCALE:**
With 50+ services, use Pact Broker webhooks to trigger provider verification immediately on pact publish, rather than waiting for the next provider CI cycle. Enable Pactflow's bi-directional contract testing to support OpenAPI specs as provider-side contracts without modifying provider tests.

---

### 💻 Code Example

**BAD — Integration test with shared environment:**
```javascript
// ❌ Tests couple both services; brittle data state
describe('order-service integration', () => {
  it('fetches user tier', async () => {
    // Requires inventory-service to be running
    const res = await fetch(
      'http://inventory-service:8080/users/42'
    );
    const data = await res.json();
    expect(data.tier).toBe('gold');
  });
});
```

**GOOD — Pact consumer test (JavaScript):**
```javascript
// ✅ Consumer defines contract against mock provider
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
const { like } = MatchersV3;

const provider = new PactV3({
  consumer: 'order-service',
  provider: 'user-service',
  dir: './pacts',
});

it('receives user tier from user-service', async () => {
  await provider
    .given('user 42 exists')
    .uponReceiving('a request for user 42')
    .withRequest({ method: 'GET', path: '/users/42' })
    .willRespondWith({
      status: 200,
      body: like({
        id: 42,
        email: 'bob@example.com',
        tier: 'gold',
      }),
    })
    .executeTest(async (mockServer) => {
      const res = await fetch(
        `${mockServer.url}/users/42`
      );
      const data = await res.json();
      expect(data.tier).toBe('gold');
    });
});
```

**GOOD — Provider verification (Java / Spring):**
```java
// ✅ Provider verifies pact from broker
@Provider("user-service")
@PactBroker(url = "https://broker.example.com")
@ExtendWith(PactVerificationInvocationContextProvider.class)
class UserServicePactVerificationTest {

  @TestTarget
  public final MockMvcTarget target = new MockMvcTarget();

  @BeforeEach
  void setUp(PactVerificationContext ctx) {
    target.setControllers(new UserController());
    ctx.setTarget(target);
  }
}
```

**Karate — schema validation contract test:**
```gherkin
# ✅ Karate enforces response schema
Feature: User API contract

Scenario: GET /users/42 returns expected schema
  Given url 'http://user-service/users/42'
  When method GET
  Then status 200
  And match response == { id: '#number',
    email: '#string', tier: '#string' }
```

---

### ⚖️ Comparison Table

| Dimension | Pact | Karate | Integration Test |
|---|---|---|---|
| **Contract owner** | Consumer-driven | Usually provider-defined | Neither — shared |
| **Environment needed** | None (mock) | Real service required | Full stack required |
| **Breaking change detection** | Immediate in CI | On test run | On test run |
| **`can-i-deploy` gate** | Yes (broker) | No built-in | No |
| **Multi-language** | Yes (8 langs) | JVM-focused | Any |
| **Schema matchers** | Yes (type/regex) | Yes (`#number`, regex) | Manual assertions |
| **Setup cost** | Medium (broker) | Low (DSL only) | Low setup, high ops |
| **Best for** | Microservice APIs | REST functional tests | Legacy monolith seams |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Contract tests replace integration tests" | They replace the need for a shared running environment for structural checks, but a smoke test in staging still validates wiring, auth, and infra. |
| "The provider writes the contract" | In consumer-driven contract testing the consumer writes the contract. The provider's job is to verify it. If the provider defines the spec, it is schema testing, not contract testing. |
| "Pact tests both sides at once" | Consumer and provider tests run independently in separate pipelines. The broker is the coordination point, not a shared test environment. |
| "Pact verifies business logic" | Pact verifies structural compatibility only: fields exist, types match, status codes match. Business rule validation belongs in unit and integration tests. |
| "One pact covers all consumers" | Each consumer team publishes its own pact. A provider may have 10 pacts from 10 consumers, each specifying only the fields that consumer needs. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 — Pact verification fails after provider refactor**
**Symptom:** `Expected 'stockCount' in response body but received 'availableQty'`.
**Root Cause:** Provider renamed a field without checking consumer contracts first.
**Diagnostic:**
```bash
# Check which consumer pacts depend on the old field
pact-broker can-i-deploy \
  --pacticipant user-service \
  --version 2.1.0 \
  --broker-base-url https://broker.example.com
```
**Fix:** Either keep the old field name (additive, not breaking) or coordinate consumer migration and deploy atomically using Pact's `pending pacts` feature.
**Prevention:** Run provider verification on every consumer pact change via broker webhooks.

**Mode 2 — Pacts go stale (consumer evolves, pact not updated)**
**Symptom:** `can-i-deploy` passes but production breaks because consumers added new required fields not in the pact.
**Root Cause:** Consumer code changed but the pact test was not updated to reflect the new expectation.
**Diagnostic:**
```bash
# Compare pact version to consumer deploy version in broker
pact-broker list-latest-pact-versions \
  --broker-base-url https://broker.example.com
```
**Fix:** Treat pact updates as mandatory in the same PR as consumer code changes. Add a CI check that pact files are committed after test run.
**Prevention:** Generate pacts in CI and fail the build if pact files differ from committed versions.

**Mode 3 — Karate schema drift goes undetected**
**Symptom:** Provider adds a new required field; Karate test passes because it only validates existing fields.
**Root Cause:** Karate's `match response contains` is lenient by default — extra fields pass. If a required new field is absent in production callers, they fail silently.
**Diagnostic:**
```bash
# Karate fuzzy match vs strict match
# match response == { ... }  # strict — fails on extra fields
# match response contains { ... }  # lenient — misses removals
```
**Fix:** Use strict `==` matching for required response shape; use `contains` only for optional extension fields.
**Prevention:** Review Karate match operator in all contract scenarios during PR.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Testing — testing pyramid and where contract tests sit (between unit and integration)
- HTTP & APIs — REST/JSON conventions that contracts encode
- Microservices — why independent deployability makes contract testing necessary

**Builds On This (learn these next):**
- CI-CD — integrating Pact `can-i-deploy` as a mandatory pipeline gate
- Consumer-Driven Contracts — the design principle Pact implements
- Integration Testing — when a shared environment is still warranted alongside contracts

**Alternatives / Comparisons:**
- Karate Framework (API Testing) — BDD DSL for API tests with schema assertions
- Spring Cloud Contract — provider-driven contracts for JVM ecosystems
- OpenAPI / JSON Schema — static schema validation without live verification

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS    Consumer-owned API shape agreement │
│ PROBLEM       Silent breaking changes across     │
│               service boundaries                 │
│ KEY INSIGHT   Consumer writes contract; provider │
│               verifies — no shared env needed    │
│ USE WHEN      Microservices with independent     │
│               deployment pipelines               │
│ AVOID WHEN    Monolith internal module calls     │
│ TRADE-OFF     Setup cost vs integration env ops  │
│ ONE-LINER     Catch field renames before prod    │
│ NEXT EXPLORE  Pact Broker, can-i-deploy, Karate  │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** You have 30 microservices and 60 pacts in your broker. A provider has 12 consumers. When the provider needs to change its response schema for a performance reason, how do you coordinate migration without blocking all 12 consumer teams simultaneously?

2. **(Scale)** Your organisation grows to 200 services. Pact verification for one provider now takes 45 minutes because it must replay 800 consumer interactions. What architectural or tooling strategies reduce this without relaxing the safety guarantee?

3. **(Design Trade-off)** Pact consumer-driven contracts put the contract ownership in the consumer's hands. What happens when the provider disagrees with a consumer's contract (e.g., the consumer expects a field the provider considers an implementation detail)? How should teams resolve this conflict, and what process governs it?
