---
layout: default
title: "API Contract Testing"
parent: "HTTP & APIs"
nav_order: 247
permalink: /http-apis/api-contract-testing/
number: "0247"
category: HTTP & APIs
difficulty: ★★★
depends_on: REST, OpenAPI/Swagger, Testing
used_by: CI/CD Pipelines, Microservices Integration, API Design
related: OpenAPI/Swagger, API Mocking, Consumer-Driven Contract Testing, Pact
tags:
  - api
  - contract-testing
  - pact
  - consumer-driven
  - integration
  - advanced
---

# 247 — API Contract Testing

⚡ TL;DR — API contract testing verifies that a service's API implementation matches an agreed-upon contract (specification), catching breaking changes before they reach production; **consumer-driven contract testing** (via tools like Pact) inverts this by having consumer teams define their expectations, which are then verified against the provider's actual implementation — preventing the provider from silently breaking consumers.

┌──────────────────────────────────────────────────────────────────────────┐
│ #247 │ Category: HTTP & APIs │ Difficulty: ★★★ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ REST, OpenAPI/Swagger, Testing │ │
│ Used by: │ CI/CD, Microservices, API Design │ │
│ Related: │ OpenAPI/Swagger, API Mocking, │ │
│ │ Consumer-Driven Contracts, Pact │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Backend team changes user service: renames `user_name` to `name`. Passes all unit
tests. Passes all integration tests on the backend. Deploys to production. Three
consumer services (frontend, mobile App, partner API) now crash with JSON parse errors.
Incident raised. Rollback. Post-mortem. The field rename was a non-breaking change to
the backend team's perspective and a catastrophic breaking change to every consumer.
Without contract testing: the provider has no visibility into which consumers depend
on which fields, and consumers have no automated way to verify the provider didn't
change their expected behavior.

**THE INVENTION MOMENT:**
Consumer-driven contract testing emerged from the microservices world where dozens of
independent services communicate via APIs. Test Pyramid: unit tests are fast but can't
catch integration issues; E2E tests are slow and brittle. Contract tests fill the gap:
fast, isolated, yet catch cross-service breaking changes. Pact (2013, REA Group
Australia) pioneered consumer-driven contracts by having consumers generate "pact files"
(expected interactions) which the provider then verifies without needing the consumer
to be running.

---

### 📘 Textbook Definition

**API Contract Testing** is a testing approach that verifies a service adheres to an
API contract — an agreed-upon description of the API's interface. Two variants exist:
(1) **Provider-driven (spec-based)**: validate the provider's implementation against
an OpenAPI specification using tools like Dredd or Schemathesis. (2)
**Consumer-driven contract testing (CDCT)**: consumers define their interaction
expectations in "pact files"; the provider verifies it can satisfy all consumer
expectations independently, without requiring consumer services to be running.
The **Pact Broker** (or PactFlow) stores and distributes pact files between teams.
CDCT gives providers visibility into consumer dependencies, enabling safe evolution
("Can I deploy? Yes — consumer contract tests all pass").

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Contract testing catches API breaking changes before production by verifying both
sides of an integration agree on the same API shape — independently, without deploying all services together.

**One analogy:**

> Contract testing is like a landlord-tenant rental agreement.
> The tenant (consumer) specifies what they need: "working kitchen, hot water,
> heating." The landlord (provider) signs the contract and must maintain those
> guarantees. Any changes to the property (API) that break the contract
> (remove the kitchen) require renegotiation (contract update) before deployment.
> Testing verifies the contract is still honored — not the entire property, just the agreed-upon terms.

**One insight:**
Consumer-driven contracts solve the "who's responsible for keeping integrations working?"
question by making expectations EXPLICIT and VERSIONED. The consumer owns their
requirements; the provider owns the verification. Visibility flows to the provider:
they see exactly which consumers depend on which fields.

---

### 🔩 First Principles Explanation

**TWO TYPES OF CONTRACT TESTING:**

```
PROVIDER-DRIVEN (SPEC-BASED):
  Source of truth: OpenAPI spec
  Test: does provider implementation match the spec?
  Tools: Dredd, Schemathesis, REST Assured spec validation

  Flow:
  1. OpenAPI spec defines expected responses
  2. Dredd sends test requests to running provider
  3. Validates actual response against spec schema
  4. Fail if: missing required fields, wrong types, undocumented status codes

  Limitation: spec may not reflect what consumers actually use.
  Provider may remove a field consumers depend on — spec is silent about consumers.

CONSUMER-DRIVEN CONTRACT TESTING (CDCT):
  Source of truth: consumer's pact file (generated from consumer tests)
  Test: can provider satisfy every consumer's specific expectations?
  Tools: Pact, Spring Cloud Contract

  Flow:
  Consumer side:
  1. Consumer writes test: "When I call GET /users/1, I expect {id: 1, name: 'Alice'}"
  2. Pact library: runs consumer test against mock server
  3. Mock server records the interaction → pact.json
  4. Pact.json published to Pact Broker

  Provider side:
  5. Provider CI: fetches pact.json from Pact Broker
  6. Pact verifier: replays consumer's requests against REAL running provider
  7. Validates responses match consumer's expectations
  8. If pass: "can-i-deploy" check authorized → deploy

  Key: consumer and provider NEVER need to run simultaneously.
       Consumer tests against a mock. Provider verifies against the pact file.
```

**PACT FILE STRUCTURE:**

```json
{
  "consumer": { "name": "frontend-app" },
  "provider": { "name": "user-service" },
  "interactions": [
    {
      "description": "Get user by ID request",
      "request": {
        "method": "GET",
        "path": "/users/1"
      },
      "response": {
        "status": 200,
        "body": {
          "id": 1,
          "name": "Alice"
        },
        "matchingRules": {
          "body": {
            "$.id": { "matchers": [{ "match": "type" }] },
            "$.name": { "matchers": [{ "match": "type" }] }
          }
        }
      }
    }
  ]
}
```

---

### 🧪 Thought Experiment

**SCENARIO:** Provider renames field `user_name` → `name`.

```
WITHOUT CONTRACT TESTING:
  Provider: changes user_name → name in UserDto
  All provider unit tests: PASS (they reference 'name')
  Deploy to production
  Consumer A (frontend-app): crashes — JSON parsing expects user_name
  Consumer B (mobile-app): crashes — same reason
  Consumer C (partner): crashes — same reason
  3 separate incidents

WITH PACT CONTRACT TESTING:
  Consumer A has pact: expects field 'user_name' in response
  Consumer B has pact: expects field 'user_name' in response

  Provider CI after changing user_name → name:
  1. Fetch pact files from Pact Broker
  2. Replay Consumer A's interaction against provider
  3. Provider response: {"id":1, "name":"Alice"} (uses 'name')
  4. Consumer A pact expects: {"user_name": ...} (string type check)
  5. FAIL: 'user_name' not present in response
  6. Build fails. Deploy blocked.
  7. Provider team knows exactly: Consumer A depends on 'user_name' field
  8. Provider: notifies Consumer A to update their pact first
  9. Consumer A: updates code + pact to use 'name' → publishes new pact
  10. Provider: re-runs verification → PASS → deploys safely
```

---

### 🧠 Mental Model / Analogy

> Consumer-driven contract testing is like a builder's punch list.
> Before a contractor (provider) hands over the building (API), each tenant (consumer)
> gives their own punch list: "light switches must work, kitchen sink must drain,
> heat must reach 70°F." The contractor verifies EACH tenant's punch list independently.
> If any item fails, the contractor can't hand over keys (deploy).
> The punch list is written by the tenant — they define what "working" means to them.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Contract testing checks that when two services talk to each other, they both agree on
what the conversation looks like. If one service changes its API, contract tests catch
the mismatch before it causes a production outage.

**Level 2 — How to use it (junior developer):**
With Pact JVM: write a consumer test that mocks the provider using `PactProviderRule`.
Run test → generates `target/pacts/consumer-provider.json`. Publish this file to
Pact Broker. On provider side: add `@Provider("user-service")` test with `@PactBroker`
annotation → Pact runs all consumer pacts against your provider. Add `can-i-deploy`
to CI pipeline before deployment.

**Level 3 — How it works (mid-level engineer):**
Pact consumer tests define interactions: request shape + response matchers (type-based
rather than exact-value). Type matchers (matching rules) make pacts resilient to normal
data variation — consumer says "I need `id` to be an integer and `name` to be a string"
not "I need id=1 and name=Alice." Provider state callbacks set up database state
(`"User 1 exists"`) before each interaction replay. Pact Broker manages pact versioning:
each consumer version publishes a pact; provider CI fetches "pacts for latest consumer
versions." `can-i-deploy` CLI queries Pact Broker: "do all consumers that could be in
production have verified pacts against this provider version?" — prevents unsafe deployments.

**Level 4 — Why it was designed this way (senior/staff):**
Consumer-driven contracts solve the fundamental asymmetry in microservices API evolution:
providers know what they offer; consumers know what they actually use (which is often
a subset). Traditional spec-based testing validates completeness from the provider's
perspective but can't prevent removing fields consumers depend on. CDCT makes consumer
dependencies EXPLICIT as versioned artifacts. The trade-off: CDCT requires investment —
consumer teams must write and maintain pact tests; Pact Broker infrastructure required;
provider state callbacks add complexity. For internal microservices: CDCT is the gold
standard. For public APIs: OpenAPI spec + schema property validation (Schemathesis
stateful testing) may be more practical. Spring Cloud Contract is an alternative for
Spring-native teams: DSL-based contracts that generate both consumer stubs and provider
tests from the same contract file, avoiding the pact file format.

---

### ⚙️ How It Works (Mechanism)

```
PACT JVM FLOW — Spring Boot Services:

CONSUMER SIDE:
  @ExtendWith(PactConsumerTestExt.class)
  class UserClientPactTest {
      @Pact(provider = "user-service", consumer = "frontend-app")
      RequestResponsePact createPact(PactDslWithProvider builder) {
          return builder
              .given("User 1 exists")  // provider state
              .uponReceiving("GET user by ID")
              .path("/api/v1/users/1")
              .method("GET")
              .willRespondWith()
              .status(200)
              .body(LambdaDsl.newJsonBody(body -> {
                  body.numberType("id");    // type matcher: any integer
                  body.stringType("name"); // type matcher: any string
                  body.stringType("email");
              }).build())
              .toPact();
      }
      // Run test → generates pact file
  }

PROVIDER SIDE (verification):
  @Provider("user-service")
  @PactBroker(url = "https://pact-broker.company.com")
  @SpringBootTest(webEnvironment = RANDOM_PORT)
  class UserProviderPactTest {
      @State("User 1 exists")
      void setupUserExists() {
          userRepository.save(new User(1L, "Alice", "alice@example.com"));
      }
      // Pact verifier replays all consumer interactions against this running instance
  }

CAN-I-DEPLOY in CI:
  pact-broker can-i-deploy \
    --pacticipant user-service \
    --version ${GIT_COMMIT} \
    --to-environment production
  # Exits 0 (safe to deploy) or 1 (blocked — consumer contract failing)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
CONSUMER:           PACT BROKER:           PROVIDER:

Write pact test     ←─── pact.json ──────→  Fetch pacts
(mock interactions)       published          for all consumers

pact.json file      ←─ version tracking ──  Verify pacts
generated locally         (who verified      against live
                          what version)      provider

Can-I-Deploy?       ←─ query matrix ─────→ Can-I-Deploy?
Before deployment:        (all consumer      Before provider
consumer CI asks          verifications)     CI asks
broker for safety                            broker for safety
```

---

### 💻 Code Example

```java
// CONSUMER test with Pact JVM 4.x
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "user-service", port = "8080")
class UserServicePactTest {

    @Pact(consumer = "frontend-app")
    public RequestResponsePact getUserPact(PactDslWithProvider builder) {
        return builder
            .given("user with id 100 exists")
            .uponReceiving("a request for user 100")
                .path("/api/v1/users/100")
                .method("GET")
                .headers(Map.of("Accept", "application/json"))
            .willRespondWith()
                .status(200)
                .headers(Map.of("Content-Type", "application/json"))
                .body(LambdaDsl.newJsonBody(body -> {
                    body.numberType("id", 100);
                    body.stringType("name", "Alice");
                    body.stringType("email", "alice@example.com");
                }).build())
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "getUserPact")
    void testGetUser(MockServer mockServer) {
        UserClient client = new UserClient(mockServer.getUrl());
        UserDto user = client.getUserById(100L);

        assertThat(user).isNotNull();
        assertThat(user.getId()).isEqualTo(100L);
        assertThat(user.getName()).isEqualTo("Alice");
        // Pact file generated to target/pacts/frontend-app-user-service.json
    }
}

// PROVIDER verification test
@Provider("user-service")
@PactBroker(url = "${PACT_BROKER_URL}")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class UserServiceProviderPactTest {

    @LocalServerPort
    private int port;

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp(PactVerificationContext context) {
        context.setTarget(new HttpTestTarget("localhost", port));
    }

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verifyPacts(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @State("user with id 100 exists")
    void setupUserExists() {
        userRepository.saveAndFlush(new User(100L, "Alice", "alice@example.com"));
    }

    @State("user with id 100 exists", action = StateChangeAction.TEARDOWN)
    void teardownUser() {
        userRepository.deleteById(100L);
    }
}
```

---

### ⚖️ Comparison Table

| Approach                            | Who Defines Contract | Speed  | Detects Consumer Breaking Changes | Infrastructure      |
| ----------------------------------- | -------------------- | ------ | --------------------------------- | ------------------- |
| **Consumer-Driven (Pact)**          | Consumer             | Fast   | ✅ Yes                            | Pact Broker needed  |
| **Spec-Based (Dredd/Schemathesis)** | Provider (via spec)  | Medium | ❌ No                             | None needed         |
| **E2E Integration Tests**           | Both (implicit)      | Slow   | ✅ Partially                      | All services needed |
| **Spring Cloud Contract**           | Both (DSL)           | Fast   | ✅ Yes                            | Spring-only         |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                         |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contract tests replace integration tests      | They complement: contract tests verify interface shape; integration tests verify behavior. Both needed                                                                          |
| The consumer controls the provider's behavior | Consumer defines EXPECTATIONS (what they read), not the provider's full behavior. Provider can add fields/endpoints freely — contract tests only check what consumers specified |
| Exact value matching is more robust           | Type matchers are safer: "I need a string, not exactly 'Alice'." Exact values make pacts brittle to normal data changes                                                         |
| Only needed for public APIs                   | Most valuable for internal microservices: where provider and consumer teams are separate and deploy independently                                                               |

---

### 🚨 Failure Modes & Diagnosis

**Pact Verification Fails Despite No Breaking Change**

Symptom:
Provider CI fails Pact verification. Provider team insists they made no breaking changes.
Consumer pact specified exact response body, not type matchers.

Root Cause:
Consumer pact uses exact value matching (`"name": "Alice"`) instead of type matchers.
Provider's test database has `"name": "Bob"` → mismatch.

Diagnostic:

```bash
# Read the pact verification output:
# Expected: {"name": "Alice"}
# Actual:   {"name": "Bob"}
# Message: "Expected 'Bob' to equal 'Alice'"

# Fix: use type matcher in consumer pact:
# body.stringType("name")   ← any string, not "Alice" specifically
# body.numberType("id")     ← any integer, not a specific value
```

---

### 🔗 Related Keywords

- `OpenAPI/Swagger` — spec-based contract for API documentation and validation
- `API Mocking` — consumer uses mock provider during consumer pact tests
- `Pact` — the dominant consumer-driven contract testing tool
- `CI/CD` — contract tests gate deployments via can-i-deploy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Test verifying both sides of an API      │
│              │ integration agree on the same interface  │
├──────────────┼───────────────────────────────────────────┤
│ TWO TYPES    │ Spec-based: provider vs OpenAPI spec      │
│              │ Consumer-driven: provider vs consumer pacts│
├──────────────┼───────────────────────────────────────────┤
│ PACT TOOL    │ Consumer → pact.json → Pact Broker        │
│              │ Provider fetches → verifies → can-i-deploy│
├──────────────┼───────────────────────────────────────────┤
│ KEY PRACTICE │ Use type matchers, not exact values       │
│              │ Provider states set up test data          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Catch breaking changes before deploy"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Mocking → OpenAPI/Swagger → CI/CD    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You're the platform engineer at a company with 40 microservices where 12 teams
independently deploy providers and consumers. Breaking APIs in production is a monthly
occurrence causing incidents. Your manager wants E2E regression tests covering all
integrations. Your tech lead recommends consumer-driven contract testing with Pact instead.
Make the case for or against each approach, identify the adoption blockers for CDCT
in an existing 40-service landscape, and propose a realistic phased adoption strategy.
