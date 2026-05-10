---
layout: default
title: "Pact (Contract Testing)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /microservices/pact-contract-testing/
id: MSV-062
category: Microservices
difficulty: ★★★
depends_on: Consumer-Driven Contract Testing, Testing, CI-CD
used_by: Backward Compatibility, Service Contract, Versioning Strategy
related: Consumer-Driven Contract Testing, OpenAPI, Schema Registry
tags:
  - microservices
  - testing
  - contracts
  - tooling
  - deep-dive
status: complete
version: 1
---

# MSV-048 - Pact (Contract Testing)

⚡ TL;DR - Pact is the leading Consumer-Driven Contract Testing framework; it generates contract files from consumer tests, shares them via Pact Broker, and verifies providers against them in CI/CD.

| #663            | Category: Microservices                                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Consumer-Driven Contract Testing, Testing, CI-CD              |                 |
| **Used by:**    | Backward Compatibility, Service Contract, Versioning Strategy |                 |
| **Related:**    | Consumer-Driven Contract Testing, OpenAPI, Schema Registry    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your team understands Consumer-Driven Contract Testing conceptually, but implementing it from scratch means: building a mock server library, defining a contract DSL, writing a contract file format, building a broker to share contracts, writing a verification test runner, and integrating all of it with CI/CD. This is weeks of platform work before any team gets value.

**THE BREAKING POINT:**
Good ideas without implementation tooling don't get adopted. Teams revert to the path of least resistance: integration environments, manual testing coordination, and slow feedback cycles.

**THE INVENTION MOMENT:**
Pact was built to make Consumer-Driven Contract Testing practical - providing the DSL, mock server, contract format (pact file), Pact Broker, verification runner, and CI/CD integration as a ready-made ecosystem.


**EVOLUTION:**
Pact was created at DiUS (Australia) in 2013 as an open-source implementation of Consumer-Driven Contract Testing for REST APIs. Initially Java and Ruby only, the framework expanded to JavaScript, Python, Go, PHP, and Scala by 2016. PactFlow (commercial Pact Broker as a service) launched in 2019. Pact messaging (async/event contracts) and bi-directional contract testing (comparing OpenAPI specs against consumer contracts) were added in 2020-2022. The discipline evolved from 'REST contract testing only' to 'contract testing for any protocol or message format including Kafka events.'
---

### 📘 Textbook Definition

**Pact** is an open-source Consumer-Driven Contract Testing framework that: (1) provides a testing DSL for consumers to define expected interactions with providers; (2) generates JSON _pact files_ (contracts) from consumer tests; (3) provides a _Pact Broker_ for publishing, sharing, and querying contract versions; (4) provides a provider verification runner that replays consumer interactions against the real provider; (5) provides a `can-i-deploy` tool to query whether a particular version combination is safe to deploy. Pact supports multiple protocols: HTTP/REST, gRPC, GraphQL, and async messaging (Kafka, RabbitMQ).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pact is the tool that makes Consumer-Driven Contract Testing work in practice - consumer tests generate JSON contracts; providers verify them automatically in CI.

**One analogy:**

> Pact is to service contract testing what JUnit is to unit testing. JUnit didn't invent the concept of testing individual methods; it made it practical by providing the framework, annotations, assertions, and test runner. Pact didn't invent consumer-driven contracts; it made them practical by providing the DSL, file format, broker, and runner.

**One insight:**
The Pact Broker is what makes the ecosystem work at scale: it's the shared registry where consumer contracts and provider verification results are stored and queried. Without it, contracts are just local files that never get to the provider.

---

### 🔩 First Principles Explanation

**THE PACT WORKFLOW - COMPONENT BY COMPONENT:**

**1. Consumer Test (generates the contract):**

```java
// Consumer writes this test
// It defines expected interactions AND generates order-product.pact.json
@Pact(consumer = "OrderService", provider = "ProductService")
public RequestResponsePact pact(PactDslWithProvider builder) {
  return builder
    .given("product-123-exists")
    .uponReceiving("get product details")
      .method("GET").path("/products/123")
    .willRespondWith()
      .status(200)
      .body(body -> body.decimalType("price", 9.99))
    .toPact();
}
```

**2. Pact File (the contract - JSON):**

```json
{
  "consumer": { "name": "OrderService" },
  "provider": { "name": "ProductService" },
  "interactions": [
    {
      "description": "get product details",
      "providerState": "product-123-exists",
      "request": { "method": "GET", "path": "/products/123" },
      "response": {
        "status": 200,
        "body": { "price": 9.99 },
        "matchingRules": {
          "body": {
            "$.price": { "matchers": [{ "match": "decimal" }] }
          }
        }
      }
    }
  ]
}
```

**3. Pact Broker:**

- Stores all pact files by (consumer, provider, consumer version)
- Stores provider verification results
- Answers: "Is consumer v1.2.3 compatible with provider v2.0.0?"
- Provides webhook triggers (e.g. trigger provider CI when new pact published)
- PactFlow (commercial) adds bi-directional contracts and advanced features

**4. Provider Verification:**

```java
// Provider runs this in CI
@Provider("ProductService")
@PactBroker(url = "https://pact.mycompany.com")
class ProductServicePactVerificationTest {
  // Pact framework replays each consumer's interactions
  // against the real Product Service
  // Verifies responses match consumer expectations
}
```

**5. can-i-deploy:**

```bash
pact-broker can-i-deploy \
  --pacticipant OrderService \
  --version 1.2.3 \
  --to-environment production
# Queries broker: has OrderService/1.2.3 been verified
# against the ProductService version currently in production?
# YES → exit 0 (safe to deploy)
# NO → exit 1 (block deployment)
```

**PACT MATCHING RULES:**

| Matcher       | Meaning                           | Example                    |
| ------------- | --------------------------------- | -------------------------- |
| `equalTo`     | Exact value match                 | `"status": "ACTIVE"`       |
| `like`        | Type match; value irrelevant      | `"name": <any string>`     |
| `eachLike`    | Array; each item matches template | `"items": [<any object>]`  |
| `regex`       | Regex match                       | `"id": /[a-z0-9-]+/`       |
| `integer`     | Must be integer                   | `"qty": <any int>`         |
| `decimal`     | Must be decimal                   | `"price": <any float>`     |
| `iso8601Date` | Must be ISO date                  | `"created": <date string>` |

**THE TRADE-OFFS:**
**Gain:** Ready-made ecosystem with cross-language support (Java, JS, Python, Go, Ruby, .NET); Pact Broker as centralised contract registry; `can-i-deploy` enables safe independent deployment; strong OSS community.
**Cost:** Learning curve; Pact Broker infrastructure to operate (or PactFlow subscription); provider state setup complexity; test suite must stay in sync with actual consumer usage.

---

### 🧪 Thought Experiment

**SETUP:**
Order Service (Java) and Shipping Service (Node.js) both consume Product Service (Java Spring Boot). Pact is deployed with a Pact Broker.

**SCENARIO: Product Service team wants to deploy a new version that changes the response structure.**

**WITHOUT PACT:**
Product team deploys. Order Service team finds breakage in staging. Shipping Service team finds breakage in production (staging didn't have their scenario). Three teams coordinate a hotfix over a weekend.

**WITH PACT:**
Product team runs provider verification before deployment. Pact Broker reports:

- Order Service pact: FAIL (field renamed)
- Shipping Service pact: PASS (doesn't use that field)
- `can-i-deploy` returns: exit 1, deployment blocked

Product team sees exactly which consumer is affected and why. They fix the API to be backward compatible, re-run provider verification - all pacts pass. `can-i-deploy` returns: exit 0. Safe deployment. Zero production incidents.

**THE INSIGHT:**
Pact gives the Product team _instant, actionable feedback_ about which consumer their change breaks - without needing those consumers running. The feedback loop shrinks from "days after deployment to production" to "minutes before merging to main."

---

### 🧠 Mental Model / Analogy

> Think of Pact as a multi-way simultaneous unit test harness for API contracts. Each consumer's pact is like a unit test for the provider - but written by the consumer, not the provider. The Pact Broker is the test registry. Provider verification is "running all consumer-written unit tests against your code." `can-i-deploy` is "checking all unit tests pass before deploying."

The analogy extends: just as you wouldn't deploy code without passing unit tests, you shouldn't deploy a service without passing all consumer contracts.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Pact is a tool where API consumers write tests specifying what they need from an API. These tests generate a file (the contract). The API provider's tests automatically check the contract. If the provider would break the contract, deployment is blocked.

**Level 2 - How to use it (junior developer):**
Consumer side: add `pact-jvm-consumer` (Java) or `@pact-foundation/pact` (Node.js) dependency; write a pact test using the builder DSL; run it to generate a pact file; publish the pact file to the Pact Broker with `pact-broker publish`. Provider side: add `pact-jvm-provider` dependency; write a verification test with `@Provider` and `@PactBroker` annotations; add `@State` setup methods for each provider state; run in CI. Add `can-i-deploy` to your CI/CD pipeline before deployment.

**Level 3 - How to operate Pact at scale (mid-level engineer):**
Pact Broker tagging: tag pact versions with branch name and environment (`main`, `staging`, `production`). Provider verifies against "all pacts from consumers currently deployed to production." Webhook integration: when a new pact is published by a consumer, Pact Broker triggers the provider's CI pipeline automatically - no manual coordination. Matrix view: the Pact Broker shows a compatibility matrix of all consumer/provider version combinations and their verification status - essential for understanding deployment safety at scale. Pending pacts: new consumer pacts start as "pending" - they don't fail provider CI immediately, giving providers time to implement. Work-in-progress pacts allow consumer-first development.

**Level 4 - Advanced patterns (senior/staff):**
Bi-directional contract testing (PactFlow feature): provider publishes an OpenAPI spec; consumer pacts are verified against the spec without running the real provider. This decouples provider verification from deployment timing. Provider-driven contracts for internal APIs with single consumers: sometimes the provider knows exactly what a consumer needs; in this case, provider-driven is acceptable and simpler. Cross-language Pact (Rust core): modern Pact implementations share a common Rust core - the matching engine is identical across Java, JS, Python, Go, .NET, ensuring cross-language compatibility. At-scale message Pact (Kafka): consumer defines expected message schema; provider publishes a test message and verifies it matches the pact - without requiring Kafka running.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│              Pact Ecosystem - Full Pipeline              │
└─────────────────────────────────────────────────────────┘

CONSUMER CI PIPELINE (Order Service):
  1. Run Pact consumer tests
     → Mock server handles requests
     → Tests pass/fail based on mock responses
     → Generates: order-service-product-service.pact.json
  2. Publish pact to Pact Broker:
     pact-broker publish \
       --pact-dir target/pacts \
       --consumer-app-version $GIT_SHA \
       --tag main
  3. can-i-deploy (before deploying Order Service):
     pact-broker can-i-deploy \
       --pacticipant OrderService \
       --version $GIT_SHA \
       --to-environment production

PACT BROKER:
  - Stores pact files by version
  - Stores verification results
  - Triggers webhooks on new pact
  - Answers can-i-deploy queries

PROVIDER CI PIPELINE (Product Service):
  [Triggered by new pact OR by code change]
  1. Run provider verification tests:
     - Fetch all consumer pacts from broker
     - Start real Product Service
     - For each interaction:
       * Set up provider state
       * Replay consumer request
       * Verify response matches contract
  2. Publish verification results to Pact Broker
  3. can-i-deploy (before deploying Product Service):
     pact-broker can-i-deploy \
       --pacticipant ProductService \
       --version $GIT_SHA \
       --to-environment production
```

---

### 🔄 The Complete Picture - Full Setup

**INFRASTRUCTURE:**

```yaml
# docker-compose.yml - Pact Broker (self-hosted)
pact-broker:
  image: pactfoundation/pact-broker:latest
  environment:
    PACT_BROKER_DATABASE_URL: postgres://...
    PACT_BROKER_BASE_URL: https://pact.mycompany.com
  ports:
    - "9292:9292"

postgres:
  image: postgres:14
  environment:
    POSTGRES_DB: pact_broker
```

**CONSUMER PIPELINE (.github/workflows):**

```yaml
- name: Run Pact tests
  run: mvn test -Dtest=*Pact*
- name: Publish pacts
  run: |
    pact-broker publish target/pacts \
      --consumer-app-version $GITHUB_SHA \
      --tag $GITHUB_REF_NAME \
      --broker-base-url $PACT_BROKER_URL
- name: Can I Deploy?
  run: |
    pact-broker can-i-deploy \
      --pacticipant OrderService \
      --version $GITHUB_SHA \
      --to-environment production
```

---

### 💻 Code Example

**Full working example - Node.js consumer (Order Service):**

```javascript
const { Pact, Matchers } = require("@pact-foundation/pact");
const { like, decimal } = Matchers;

const provider = new Pact({
  consumer: "OrderService",
  provider: "ProductService",
  port: 4000,
  dir: path.resolve(process.cwd(), "pacts"),
});

describe("Product Service Pact", () => {
  before(() => provider.setup());
  after(() => provider.finalize());

  describe("GET /products/:id", () => {
    before(async () => {
      await provider.addInteraction({
        state: "product-123-exists",
        uponReceiving: "a request for product 123",
        withRequest: {
          method: "GET",
          path: "/products/123",
        },
        willRespondWith: {
          status: 200,
          headers: { "Content-Type": "application/json" },
          body: {
            id: like("123"), // type: string
            name: like("Widget"), // type: string
            price: decimal(9.99), // type: decimal
          },
        },
      });
    });

    it("returns product details", async () => {
      const client = new ProductApiClient("http://localhost:4000");
      const product = await client.getProduct("123");

      expect(product.price).toBeDefined();
      expect(typeof product.price).toBe("number");
    });
  });
});
```

**Kafka message Pact (async):**

```java
@Pact(consumer = "ShippingService",
      provider = "OrderService")
public MessagePact createMessagePact(
    MessagePactBuilder builder) {
  return builder
    .given("order placed")
    .expectsToReceive("an OrderPlaced event")
    .withContent(body -> {
      body.stringType("orderId", "order-123");
      body.stringType("customerId", "cust-456");
      body.decimalType("amount", 99.99);
    })
    .toPact();
}
```

---

### ⚖️ Comparison Table

| Tool                   | Type              | Protocol Support           | Broker Needed     | Maturity |
| ---------------------- | ----------------- | -------------------------- | ----------------- | -------- |
| **Pact**               | CDCT              | HTTP, gRPC, Kafka, GraphQL | Yes (Pact Broker) | High     |
| Spring Cloud Contract  | Provider-driven   | HTTP, Messaging            | No                | High     |
| Postman Contract Tests | Provider-driven   | HTTP                       | No                | Medium   |
| OpenAPI Diff           | Schema comparison | HTTP                       | No                | Medium   |
| Dredd                  | Provider testing  | HTTP                       | No                | Medium   |

**How to choose:** Use **Pact** for consumer-driven contract testing across multiple teams. Use **Spring Cloud Contract** when the provider defines the contract and all consumers are Java. Use **OpenAPI Diff** for simple schema drift detection without full CDCT.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Pact tests are just integration tests with a mock | Pact tests generate a formal contract file; the mock is generated from the contract, not the other way around |
| Pact can replace all integration testing          | Pact tests contracts; business flow integration tests are still needed for end-to-end confidence              |
| The Pact Broker is optional                       | Without the broker, contracts are local files; the provider never sees them; CDCT doesn't work at scale       |
| `can-i-deploy` is optional                        | It's the mechanism that prevents unsafe deployments; skipping it defeats the purpose                          |
| Pact only supports REST                           | Pact supports REST, gRPC, GraphQL, Kafka, RabbitMQ, SNS                                                       |

---

### 🚨 Failure Modes & Diagnosis

**Provider State Not Found**

**Symptom:** Provider verification fails with `Provider state 'product-123-exists' not found`.

**Root Cause:** Consumer pact specifies a provider state that doesn't have a corresponding `@State` method in the provider verification test.

**Fix:**

```java
// Add missing @State handler in provider test
@State("product-123-exists")
void setupProduct123() {
  productRepository.save(
    new Product("123", "Widget", 9.99));
}
```

**Prevention:** Every new pact interaction that has a `given` clause must have a corresponding provider state handler. Review new pact interactions during provider team code review.

---

**Pact Broker Unreachable During CI**

**Symptom:** Consumer CI fails when publishing pacts; provider CI fails when fetching pacts; `can-i-deploy` fails.

**Root Cause:** Pact Broker down or misconfigured CI credentials.

**Diagnostic Command:**

```bash
# Test broker connectivity
curl -H "Authorization: Bearer $PACT_BROKER_TOKEN" \
  $PACT_BROKER_URL/pacts

# Verify credentials
pact-broker describe-version \
  --pacticipant OrderService \
  --latest \
  --broker-base-url $PACT_BROKER_URL \
  --broker-token $PACT_BROKER_TOKEN
```

**Fix:** Restore Pact Broker; fix credentials. Use PactFlow (SaaS) to eliminate broker infrastructure management.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Consumer-Driven Contract Testing` - the concept Pact implements
- `Testing` - the broader test strategy context
- `CI-CD` - where Pact fits into the deployment pipeline

**Builds On This (learn these next):**

- `Backward Compatibility` - what Pact contracts enforce
- `Service Contract` - Pact contracts are a form of service contract
- `Versioning Strategy` - Pact's version tagging enables safe version management

**Alternatives / Comparisons:**

- `Consumer-Driven Contract Testing` - the broader concept
- `OpenAPI / Swagger` - provider-defined API spec; less flexible for CDCT but widely used
- `Spring Cloud Contract` - alternative framework, provider-defined contracts

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ CDCT framework: consumer tests generate   │
│              │ JSON contracts; Pact Broker shares them;  │
│              │ providers verify against them in CI       │
├──────────────┼───────────────────────────────────────────┤
│ KEY TOOLS    │ pact-jvm, @pact-foundation/pact,          │
│              │ Pact Broker (self-host) / PactFlow (SaaS) │
├──────────────┼───────────────────────────────────────────┤
│ CI FLOW      │ Consumer test → pact file → publish →    │
│              │ provider verify → can-i-deploy → deploy  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple teams consuming shared APIs;     │
│              │ frequent independent deployments          │
├──────────────┼───────────────────────────────────────────┤
│ PROTOCOLS    │ REST, gRPC, GraphQL, Kafka, RabbitMQ      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Consumer tests → contract file →         │
│              │  provider must honour it"                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pact Broker → can-i-deploy →             │
│              │ Backward Compatibility                   │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Pact makes consumer dependencies explicit, versioned, and testable. Before Pact, what each consumer needed from a provider was implicit (reading source code) or separately documented (OpenAPI specs that diverged from reality). Pact makes the consumer's actual usage the test case, providing a continuously verified contract between every consumer-provider pair. The same principle applies to dependency management: actual used dependencies are more accurate than declared dependencies.

**Where else this pattern appears:**
- **OpenAPI specifications:** OpenAPI is provider-driven (the provider says what it returns). Pact is consumer-driven (each consumer says what it uses). Both describe the same API from different perspectives.
- **GraphQL schemas:** A GraphQL query is a consumer-driven contract - the consumer specifies exactly what fields it needs. The schema type system verifies the provider can fulfill all queries.
- **Feature flags:** A feature flag dependency (flag X must exist with boolean type) is the same pattern as a Pact field contract - consumer declares what it depends on.

---

### 💡 The Surprising Truth

Pact's most counterintuitive failure mode is test pollution from overly specific matchers. A consumer that uses `equalTo('John')` instead of `type(String)` in their Pact contract will cause provider verification to fail every time test data changes - even if the contract is still satisfied. The correct practice is to use type matchers (`type`, `eachLike`, `regex`) rather than exact value matchers. Teams that don't learn this lesson spend significant time debugging failing Pact tests caused by overly specific test data, not real API compatibility issues.
---

### 🧠 Think About This Before We Continue

**Q1.** Your team has three services: Order Service (Java), Shipping Service (Node.js), and Notification Service (Python) - all consuming Product Service (Java). Describe the complete Pact setup: what tools/libraries each team uses, where the Pact Broker lives, how the CI pipelines are wired, and what happens when Order Service adds a new field to their product pact that Product Service doesn't yet return.

*Hint:* Think about what 'Order Service adds a new field to their product pact' means for the CI pipeline: Order Service publishes updated pact to Pact Broker → Product Service CI runs pact verification → Product Service fails verification (it doesn't yet return the new field) → 'can-i-deploy' check fails for Order Service (its pact is not verified against the current production Product Service). Explore whether 'pending pacts' (Order Service's new pact is marked pending, doesn't block Product Service deployment, but does block Order Service deployment until Product Service has verified it) is the correct tool for managing this contract evolution.

**Q2.** The Product Service team wants to deprecate the `categoryId` field in their response (moving it to a separate Category Service). Three consumer pacts currently include `categoryId`. Using Pact matchers and the Pact Broker, design a migration strategy that: (a) allows Product Service to deploy without `categoryId` before consumers have updated, and (b) ensures consumers don't break. Describe each step in the deployment sequence.

*Hint:* Think about what the migration sequence must be: consumers must remove their dependency before the provider removes the field. Deployment order: (1) identify all consumer pacts referencing `categoryId`; (2) each consumer team updates their code and pact to use Category Service instead; (3) consumers deploy without `categoryId` in their pact; (4) Pact Broker shows zero consumer pacts reference `categoryId`; (5) Product Service removes `categoryId` from its response and deploys. The Pact Broker's 'can-i-deploy' check at step 5 confirms no consumer pact references the removed field before the deploy is allowed.

**Q3 (Design Trade-off):** 15 consumer services publish contracts for 5 provider services. After 6 months you have 200 historical pact versions in the Pact Broker. Provider CI pipelines verify all 200 versions, slowing CI significantly. Design the Pact Broker maintenance strategy that keeps CI fast without losing the protection CDCT provides.

*Hint:* Think about which pact versions actually need verification: the version currently deployed in production (always), the version being deployed now (always), and the latest version on each consumer's main branch (for catching issues before production). Explore whether Pact Broker's 'consumer version selectors' (verify only 'deployedOrReleased' + 'mainBranch' + 'matchingBranch' rather than all historical versions) eliminate the need to verify 200 versions, and what the minimum set of versions is that maintains the contractual safety guarantee.
