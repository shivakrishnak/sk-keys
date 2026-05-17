---
id: MSV-062
title: Pact (Contract Testing)
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-061, MSV-010
used_by: MSV-061
related: MSV-061, MSV-010, MSV-048, MSV-070, MSV-071, MSV-067
tags:
  - microservices
  - testing
  - deep-dive
  - contracts
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 62
permalink: /microservices/pact-contract-testing/
---

# MSV-062 - Pact (Contract Testing)

⚡ TL;DR - Pact is the open-source Consumer-Driven
Contract Testing framework (pact.io). Consumers
write tests using Pact's DSL, generating JSON
`.pact` files (contract artifacts). The Pact Broker
stores these contracts. Provider CI fetches and
verifies each contract against the running provider.
The `can-i-deploy` CLI command queries the Pact
Broker before deployment: "has this version been
verified by all required providers/consumers?" If
not: deploy blocked. Supports: HTTP/REST (Pact V3)
and async message contracts (Kafka, SNS, SQS)
via MessagePact. Available: Java (pact-jvm), JS,
Go, Ruby, .NET, Python, Swift.

| #062 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Consumer-Driven Contract Testing, Service Discovery | |
| **Used by:** | Consumer-Driven Contract Testing | |
| **Related:** | Consumer-Driven Contract Testing, Service Discovery, Event-Driven Microservices, Service Contract, API Evolution Strategy, Canary Deployment | |

---

### 🔥 The Problem This Solves

**CONSUMER-DRIVEN CONTRACT TESTING NEEDS A STANDARD:**
Without a framework: teams would implement their
own ad-hoc API compatibility tests. These would
have inconsistent formats, no centralized verification
history, no "can I deploy" query capability, and
no support for async message contracts. Pact:
provides the standard format (JSON pact files),
the broker (centralized contract registry with
verification history), the SDK (language bindings
for writing contracts), and the CLI tools (can-i-
deploy, pact-broker CLI). Everything needed to
implement CDCT in an organization.

---

### 📘 Textbook Definition

**Pact** is an open-source Consumer-Driven Contract
Testing tool and ecosystem consisting of:
(1) **Pact Libraries** - language-specific SDKs
(pact-jvm for Java/Kotlin, pact-js, pact-go, etc.)
for writing consumer tests (generates .pact JSON
files) and provider verification tests;
(2) **Pact Broker** - a web application/server that
stores pact files, records verification results,
shows consumer-provider relationship graphs, and
provides the deployment query API;
(3) **Pact CLI** - command-line tools including
`pact-broker can-i-deploy` for querying deployment
safety and `pact-broker publish` for uploading pacts;
(4) **PactFlow** - cloud-hosted Pact Broker with
additional enterprise features (can-i-deploy webhooks,
bi-directional contract testing for OpenAPI specs).
The Pact specification (V1-V4) defines the JSON
contract format. V3 adds message contracts (async);
V4 adds XML support and combined interaction types.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pact = the standard tool for Consumer-Driven Contract
Testing. Consumer writes a Pact test (generates
JSON contract). Provider runs the contract as a
test. Pact Broker tracks what was verified. Can-
i-deploy: "is it safe to deploy?"

**One analogy:**
> Pact is like a legal contract management system.
> A client (consumer) files a contract (pact file)
with the court (Pact Broker). The contractor
(provider) must verify their work meets the contract's
specifications (provider verification test). The
court records the verification result. Before
payment (deployment): the court confirms the
verification is complete and current (can-i-deploy).
The contract format is standardized (Pact spec V3).
Any lawyer (developer in any language) can write
and read contracts in this format.

**One insight:**
Pact's real value is the Pact Broker and can-i-
deploy, not just the test libraries. Without the
broker: each service team must manually share pact
files and track verification history. The broker
automatically answers: "If I deploy order-service
v2.1 to production, will it break anything?" This
is the automation of what teams previously did
manually (check with other teams) or not at all
(find out in production).

---

### 🔩 First Principles Explanation

**PACT ARCHITECTURE:**

```
  CONSUMER SIDE:              PROVIDER SIDE:
  
  Consumer test (Java)        Provider test (Java)
  | Pact DSL: define         | @PactBroker annotation
  |  interaction             | @State: set up data
  |  request + response      | Run: pact verify
  | Generates:               |
  |  order-service-          |
  |  customer-service.json   |
  |                          |
  v                          |
  Pact Broker <--------------+
  | Stores pact file         |
  | Records verification     |
  |                          v
  | can-i-deploy query        Provider CI
  v                            (verify all pacts)
  CI/CD gate
  
PACT BROKER DATA MODEL:
  Pacticipant: a service (consumer or provider)
  Pact: a contract between a consumer version
        and a provider
  Verification: a provider version's verification
                result for a specific pact
  Environment: production, staging, etc.
  Deployed version: which version is in which env
  
  can-i-deploy: answers
  "Has consumer@version's pact been verified
   by provider@(current-production-version)?"
```

**PACT FILE FORMAT (V3 JSON):**

```json
{
  "consumer": {"name": "order-service"},
  "provider": {"name": "customer-service"},
  "interactions": [
    {
      "description": "get customer for order",
      "providerStates": [
        {"name": "customer cust-001 exists"}
      ],
      "request": {
        "method": "GET",
        "path": "/customers/cust-001",
        "headers": {
          "Accept": "application/json"
        }
      },
      "response": {
        "status": 200,
        "matchingRules": {
          "body": {
            "$.customerId": {"matchers": [
              {"match": "type"}
            ]},
            "$.name": {"matchers": [
              {"match": "type"}
            ]},
            "$.email": {"matchers": [
              {"match": "type"}
            ]}
          }
        },
        "body": {
          "customerId": "cust-001",
          "name": "Alice Smith",
          "email": "alice@example.com"
        }
      }
    }
  ],
  "metadata": {
    "pactSpecification": {"version": "3.0.0"},
    "pact-jvm": {"version": "4.6.0"}
  }
}
```

---

### 🧪 Thought Experiment

**CAN-I-DEPLOY: DEPLOYMENT SAFETY NETWORK:**

```
SCENARIO: 3 services, release day, 2 need to deploy

  order-service v2.1 (consumer) - pact published
  customer-service v1.5 (provider) - verified pact
  notification-service v3.0 (consumer) - new pact published
  
  order-service v2.1 pact:
  - Verified by customer-service v1.5: YES
  - customer-service v1.5 is in production: YES
  can-i-deploy order-service v2.1 to production: YES
  
  notification-service v3.0 pact:
  - Verified by customer-service v1.5: NO
    (new pact; provider not yet re-verified)
  can-i-deploy notification-service v3.0: NO
  
  Result:
  order-service: deploys safely
  notification-service: blocked until
    customer-service verifies new pact
  
  customer-service CI: detects new pact from
    notification-service (via webhook)
  Runs verification: passes
  Records result in Pact Broker
  can-i-deploy notification-service: NOW YES
  notification-service: deploys
  
  Total time: 10-15 minutes (CI run time)
  Without Pact: would require email/Slack coordination
  or would deploy and hope for the best
```

---

### 🧠 Mental Model / Analogy

> Pact Broker is like a banking system for contracts.
> You can deposit contracts (publish pacts). You can
> check the account balance of verifications (has
> this contract been verified?). The bank (Pact
> Broker) keeps a complete transaction history
> (verification history). Before a large transfer
> (production deployment), the bank confirms funds
> are available (can-i-deploy). The bank supports
> multiple currencies (multiple programming languages
> via pact spec). And PactFlow is the premium banking
> account with extra features (webhooks, BI-directional
> contracts for OpenAPI).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Pact is a tool that lets services agree on "what
I need from you" contracts, then automatically
verify those contracts are not broken before
deployments. Like a spell-checker for API compatibility.

**Level 2 - Getting started (junior developer):**
Add `pact-jvm` dependency (Consumer DSL + Provider
Verifier). Write consumer test with `@ExtendWith
(PactConsumerTestExt.class)`. Define `@Pact`
interaction. Run test: generates target/pacts/*.json.
Publish to Pact Broker with `pact-broker publish`.
Provider: add `@PactBroker`, `@Provider`, write
`@State` setups, run `@TestTemplate` verification.

**Level 3 - Pact Broker operations (mid-level):**
Pact Broker environment tags: mark which version
is in which environment (`--tag production`).
Webhooks: configure broker to trigger provider
CI when new pact published. `can-i-deploy --to-
environment production`: uses environment-aware
query (requires `record-deployment` after each
deploy). Version selectors: `matchingBranch()`,
`deployedOrReleased()` - provider verifies only
relevant consumer versions.

**Level 4 - Message contracts (senior):**
Pact V3 `MessagePact`: consumer test defines
the Kafka/SQS message it expects to receive.
Provider test: generates the message and verifies
it matches. No Kafka broker needed in test: purely
in-memory message verification. Integrates with
Confluent Schema Registry: use Avro schemas in
Pact tests. `PactVerifyProvider` annotation with
`@PactVerifyMessage` for the message producer.

**Level 5 - PactFlow + Bi-directional (principal):**
PactFlow Bi-Directional Contract Testing: provider
uploads an OpenAPI spec instead of running Pact
verification tests. PactFlow: cross-checks consumer
Pact contracts against the OpenAPI spec automatically.
Benefit: no code change on provider side (works
with existing OpenAPI documentation). Limitation:
no provider state verification (only schema checking).
Use when: adopting Pact in a brownfield environment
where providers have OpenAPI specs but cannot add
Pact verification tests easily.

---

### ⚙️ How It Works (Mechanism)

```groovy
// PACT IN PRACTICE: build.gradle dependencies
dependencies {
    // Consumer test dependency
    testImplementation "au.com.dius.pact.consumer:
        junit5:4.6.0"
    // Provider verification dependency
    testImplementation "au.com.dius.pact.provider:
        junit5spring:4.6.0"
}
```

```java
// MESSAGE PACT: Kafka consumer contract
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(
    providerName = "order-event-publisher",
    providerType = ProviderType.ASYNCH
)
public class OrderEventConsumerTest {

    @Pact(consumer = "notification-service")
    public MessagePact createOrderCreatedPact(
            MessagePactBuilder builder) {
        return builder
            .given("order placed successfully")
            .expectsToReceive("order created event")
            .withContent(new PactDslJsonBody()
                .stringType("orderId")
                .stringType("customerId")
                .decimalType("totalAmount")
                .stringType("status", "CREATED")
                // Only fields notification-service uses:
                // customerId for looking up email
                // orderId for the notification subject
                // totalAmount for email content
            )
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "createOrderCreatedPact")
    void testOrderCreatedMessage(
            List<Message> messages) {
        Message msg = messages.get(0);
        // Pact: provides the message as bytes
        // notification-service deserializes and uses it
        OrderCreatedEvent event = objectMapper
            .readValue(msg.contentsAsString(),
                OrderCreatedEvent.class);
        assertThat(event.getOrderId()).isNotNull();
        assertThat(event.getCustomerId()).isNotNull();
        // Pact: generates target/pacts/*.json
    }
}

// PROVIDER MESSAGE VERIFICATION:
@Provider("order-event-publisher")
@PactBroker(host = "pact-broker.internal")
@SpringBootTest
public class OrderEventProviderTest {

    @TestTemplate
    @ExtendWith(
        PactVerificationInvocationContextProvider.class)
    void verifyPact(
            PactVerificationContext context) {
        context.verifyInteraction();
    }

    @PactVerifyProvider("order created event")
    public MessageAndMetadata generateOrderCreatedEvent() {
        // Provider: generate the actual Kafka message
        OrderCreatedEvent event = new OrderCreatedEvent(
            "ord-001", "cust-001",
            new BigDecimal("99.99"), "CREATED");
        return MessageAndMetadata.create(
            objectMapper.writeValueAsBytes(event));
        // Pact: verifies this message matches
        // notification-service's contract
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
PACT CI/CD INTEGRATION:

CONSUMER CI (order-service):
  1. Run consumer Pact tests
     -> target/pacts/order-service-customer-service.json
  2. Publish to Pact Broker:
     pact-broker publish target/pacts \
       --consumer-app-version 2.1.0 \
       --tag main
  3. Can-I-Deploy (before deploy to production):
     pact-broker can-i-deploy \
       --pacticipant order-service \
       --version 2.1.0 \
       --to-environment production
     Result: YES (or NO -> pipeline fails)
  4. Deploy order-service 2.1.0 to production
  5. Record deployment:
     pact-broker record-deployment \
       --pacticipant order-service \
       --version 2.1.0 \
       --environment production

PROVIDER CI (customer-service):
  Triggered by: new pact published (webhook) OR
                provider code change
  1. Fetch consumer pacts from Pact Broker
  2. Run provider verification tests
     (sets up provider state, replays interactions)
  3. Publish verification result:
     pact.verifier.publishResults=true
  4. can-i-deploy for provider:
     pact-broker can-i-deploy \
       --pacticipant customer-service \
       --version 1.5.0 \
       --to-environment production
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: exact values vs type matchers**

```java
// BAD: exact value matching - brittle contract
// Any test data change breaks the contract
body(new PactDslJsonBody()
    .stringValue("customerId", "cust-001")  // EXACT!
    .stringValue("name", "Alice Smith")     // EXACT!
    .stringValue("email",
        "alice@example.com")               // EXACT!
)
// Problem: if test data changes (different DB,
// different seed data), contract fails spuriously
// Not testing structure: testing specific values
```

```java
// GOOD: type matchers - tests structure, not values
body(new PactDslJsonBody()
    .stringType("customerId")  // any non-null string
    .stringType("name")        // any non-null string
    .stringType("email")       // any non-null string
    // emailFormat() matcher: verify it's email shape
    // but don't hardcode a specific email value
)
// Why: any valid test data passes the contract
// What is tested: the field EXISTS and is the right TYPE
// Provider can use any test customer: contract passes
```

---

### ⚖️ Comparison Table

| Pact Feature | Use Case | Alternative | Pact Advantage |
|---|---|---|---|
| **HTTP contract tests** | REST API compatibility | WireMock stubs | Consumer-driven; provider verifies |
| **Message contract tests** | Kafka event compatibility | Schema Registry | Tests consumer behavior, not just schema |
| **Pact Broker** | Contract registry | Shared git folder | Verification history, can-i-deploy |
| **PactFlow BiDi** | OpenAPI-based contracts | Manual review | No provider code changes needed |
| **can-i-deploy** | Deployment gate | Manual coordination | Automated, queryable, environment-aware |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Pact verifies that the provider API works correctly | Pact verifies that the provider satisfies consumer contracts (the minimum fields consumers need). It does NOT test provider business logic, error handling for non-contracted scenarios, or performance. Provider unit and integration tests cover that. Pact specifically covers: "does the provider's response include the fields consumers claim to need?" |
| Pact requires a running Kafka broker for message tests | Pact Message contracts are purely in-memory. Consumer test: defines the message shape; Pact generates a mock message. Provider test: generates the message and Pact verifies it matches the contract. No Kafka broker, no Docker, no real messaging infrastructure needed. This makes message contract tests as fast as unit tests. |
| If Pact tests pass, deployment is safe | Pact tests verify API contracts, not application correctness. A Pact test can pass while application logic is broken: e.g., the endpoint returns the right fields but wrong business logic (calculates wrong total). Pact is one layer of a defense-in-depth testing strategy: unit tests, Pact contracts, integration tests (limited), E2E tests (very limited). |

---

### 🚨 Failure Modes & Diagnosis

**Provider verification passes locally, fails in CI**

**Symptom:**
Provider developer runs `./mvnw test` locally:
Pact verification passes. CI pipeline: Pact
verification fails with "Provider state setup
failed: customer cust-001 not found". Same code,
different result.

**Root Cause (common: state setup not working in CI):**
1. Local: developer's PostgreSQL has test data.
   CI: starts with empty H2 or fresh PostgreSQL.
2. `@State("customer cust-001 exists")` setup method:
   uses `@Autowired` `CustomerRepository` - but
   the CI environment doesn't have the repository
   bean initialized correctly in the test context.
3. Or: the Pact Broker URL is different in CI
   (env variable `PACT_BROKER_URL` not set);
   Pact fetches no contracts; "0 pacts to verify";
   test PASSES vacuously (no tests = pass).

**Diagnosis:**
```bash
# Check Pact Broker URL in CI
echo $PACT_BROKER_URL

# Check how many pacts were fetched:
# Look for: "Verifying a pact between X and Y"
# If absent: no pacts fetched (broker URL wrong)

# Verbose Pact output:
-Dpact.verifier.publishResults=true
-Dpact.showStacktrace=true
```

**Fix:**
1. Set `PACT_BROKER_URL` env variable in CI.
2. Add `@Transactional` + `@Rollback` to state
   setup methods or use `@BeforeEach` data setup.
3. Add assertion: if 0 pacts verified: fail the
   build (not pass vacuously).

---

### 🔗 Related Keywords

**The concept:**
- `Consumer-Driven Contract Testing` - the methodology
  that Pact implements

**Related tooling:**
- `Service Contract` - formal service interface
  definition (Pact is one implementation)
- `API Evolution Strategy` - Pact enables safe
  API evolution by detecting breaking changes

**Testing context:**
- `Event-Driven Microservices` - Pact supports
  Kafka message contracts (async interactions)
- `Canary Deployment` - deploy confidently using
  Pact contract verification before canary release

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COMPONENTS   │ SDK (consumer+provider tests)             │
│              │ Pact Broker (storage + verification log)  │
│              │ can-i-deploy (deployment safety gate)     │
├──────────────┼───────────────────────────────────────────┤
│ LANGUAGES    │ Java (pact-jvm), JS, Go, Ruby, .NET, Python│
├──────────────┼───────────────────────────────────────────┤
│ ASYNC        │ MessagePact for Kafka/SQS/SNS             │
│              │ No broker needed in tests                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pact: SDK + Broker + can-i-deploy;        │
│              │  consumer-driven contract testing standard"│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Pact = SDK (write consumer/provider tests) +
   Pact Broker (store contracts + verification
   history) + can-i-deploy (deployment gate).
2. Consumer test: generates JSON pact file.
   Provider test: fetches pacts from broker,
   verifies each interaction.
3. Key CI pattern: publish pacts after consumer
   build; verify pacts in provider CI (webhook-
   triggered); can-i-deploy gates both pipelines.

**Interview one-liner:**
"Pact is the de-facto Consumer-Driven Contract
Testing framework: consumers write tests (pact-jvm
for Java) that generate JSON contract files; providers
fetch contracts from the Pact Broker and run
verification tests. can-i-deploy CLI queries the
broker before deployment: 'has this version been
verified by all required consumers/providers?'
Pact V3 supports MessagePact for Kafka events -
no real Kafka broker needed in tests. PactFlow
adds bi-directional contracts: providers upload
OpenAPI specs instead of running verification tests."

---

### 💡 The Surprising Truth

The most common Pact failure mode is not a test
failure - it's a VACUOUS PASS. When the Pact Broker
URL is misconfigured: the provider fetches 0 pacts,
runs 0 verification tests, and the build PASSES.
Developer sees: "All tests passed!" Provider deploys
and breaks consumers. Defense: configure your Pact
verification test to FAIL if 0 pacts were fetched:
```yaml
pact.verifier.failIfNoPactsFound=true
```
This single configuration line prevents the most
common Pact deployment failure mode. Without it:
a misconfigured Pact Broker URL silently disables
all contract testing, and no one notices until
a production incident.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **HTTP** Write a complete Pact consumer test
   (pact-jvm V4): define interaction with provider
   state, use type matchers, publish to broker.
   Write provider verification test: fetch from
   broker, set up state, verify.
2. **MESSAGE** Write a Pact MessagePact consumer
   test for a Kafka OrderCreated event. Write the
   provider message verification test. Run end-
   to-end: consumer publishes pact; provider verifies.
3. **BROKER** Deploy a self-hosted Pact Broker
   (Docker Compose). Configure consumer CI to
   publish pacts. Configure provider CI webhook
   (trigger on new pact). Configure can-i-deploy
   gates in both pipelines.
4. **DEBUGGING** Diagnose: provider verification
   passes locally but fails in CI. Walk through:
   Pact Broker URL, provider state setup, test
   data, Pact Broker connection in CI.
5. **PACTFLOW** Explain Bi-Directional Contract
   Testing: what it verifies, how it differs from
   standard Pact, when to use it (brownfield
   OpenAPI environments), limitations (no behavioral
   verification).

---

### 🧠 Think About This Before We Continue

**Q1.** You have a payment-service that consumes
events from order-service via Kafka. payment-service
needs: `orderId`, `customerId`, `amount`, `currency`.
You want to implement a Pact MessagePact. Write the
pseudo-code for both the consumer test (payment-service)
and the provider test (order-service). What is in
the generated pact file? How does the Pact Broker
know this verification result applies to the
current production version of order-service?

**Q2.** Your organization has 40 microservices.
Some are in Java (Spring Boot), some in Node.js,
one in Go. All need Pact. The Pact Broker is self-
hosted on Kubernetes. Describe your rollout strategy:
which services do you instrument first, how do
you handle the cross-language contracts (a Node.js
consumer, Java provider), and how do you ensure
can-i-deploy is respected in all 40 CI pipelines?

**Q3.** A developer argues: "We have comprehensive
integration tests in a shared staging environment.
We don't need Pact." Prepare a counter-argument:
what specific failure modes does the shared staging
approach have that Pact solves, and what is the
cost comparison (time, infrastructure, developer
productivity) between the two approaches?