---
layout: default
title: "Service Contract"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /microservices/service-contract/
id: MSV-059
category: Microservices
difficulty: ★★★
depends_on: Backward Compatibility, Consumer-Driven Contract Testing, API Gateway
used_by: Backward Compatibility, Versioning Strategy, Consumer-Driven Contract Testing
related: Backward Compatibility, Versioning Strategy, Consumer-Driven Contract Testing
tags:
  - microservices
  - api-design
  - contracts
  - design
  - deep-dive
status: complete
---

# MSV-059 - Service Contract

⚡ TL;DR - A service contract is the formal, explicit agreement between a service and its consumers, specifying the API shape, message formats, error codes, and behavioural guarantees - making it safe for consumers to depend on the service without being coupled to its implementation.

| #674            | Category: Microservices                                                       | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Backward Compatibility, Consumer-Driven Contract Testing, API Gateway         |                 |
| **Used by:**    | Backward Compatibility, Versioning Strategy, Consumer-Driven Contract Testing |                 |
| **Related:**    | Backward Compatibility, Versioning Strategy, Consumer-Driven Contract Testing |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Order Service calls Payment Service. Nobody wrote down what the Payment Service API looks like. Order Service was built by reading the Payment Service source code. Payment Service team refactors: renames `PaymentRequest.amount` to `PaymentRequest.totalAmount`. They don't think to notify the Order Service team - after all, they didn't change any "public API" (the service is internal). Order Service deploys on Friday. Saturday: all payments fail. `NullPointerException: amount is null`. Root cause: Payment Service changed its interface without telling consumers. No contract; no violation detection; outage.

**THE BREAKING POINT:**
In a distributed system, every service is implicitly a provider of an API and a consumer of other APIs. Without explicit contracts, any implementation change can silently break consumers. "Implicit contracts" (consumers read provider source code) don't scale across team boundaries.

**THE INVENTION MOMENT:**
Service contracts formalise what a service promises to its consumers. Contracts are explicit, versioned, tested, and owned. Breaking a contract requires explicit, coordinated versioning - not accidental field renames.


**EVOLUTION:**
The concept of service contracts formalised as microservices replaced monoliths. In a monolith, contracts were enforced by the type system (changing a method signature caused a compile error). In microservices, interface changes caused runtime errors visible only in production. OpenAPI Specification (formerly Swagger, 2011) provided a machine-readable format for REST API contracts. gRPC Protocol Buffers (2015) provided strongly-typed contracts with backward compatibility rules. Consumer-Driven Contract Testing (Pact, 2013) added consumer expectations. The discipline evolved from 'document the API and hope consumers read it' to 'formally define, version, and test the contract from both sides.'
---

### 📘 Textbook Definition

A **service contract** is the explicit, versioned specification of a service's external interface, defining: (1) the **request/response schema** (field names, types, constraints, required/optional); (2) the **error model** (error codes, error response shapes); (3) the **behavioural guarantees** (idempotency, ordering, consistency level); (4) the **non-functional guarantees** (SLA: latency, availability, throughput limits). The service contract is the binding agreement between provider and consumer - the provider commits to maintaining backward compatibility within a contract version; the consumer commits to not depending on undocumented implementation details. The contract may be expressed as: OpenAPI specification (REST), Protobuf/gRPC schema, AsyncAPI (events), or consumer-driven Pact contracts.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The written promise a service makes to its callers - this is what I'll accept, what I'll return, what I guarantee.

**One analogy:**

> A restaurant menu is a contract. The menu (contract) specifies what dishes are available (API endpoints), what ingredients are in each (request fields), what you'll get served (response fields), and prices (rate limits/SLA). If the kitchen changes a recipe, they update the menu - they don't silently serve you something different. The menu protects diners from kitchen surprises.

**One insight:**
A service contract separates the "what" (observable interface) from the "how" (implementation). Consumers depend on the "what". The service can freely change the "how" - internal refactoring, database changes, algorithm improvements - as long as the "what" is preserved.

---

### 🔩 First Principles Explanation

**WHAT A CONTRACT CONTAINS:**

| Element             | Description                | Example                                          |
| ------------------- | -------------------------- | ------------------------------------------------ |
| **Endpoint**        | Method + path              | `POST /v1/payments`                              |
| **Request schema**  | Fields, types, constraints | `amount: decimal, required; currency: string(3)` |
| **Response schema** | Success and error shapes   | `{paymentId, status, timestamp}`                 |
| **Error catalogue** | Error codes + meanings     | `INSUFFICIENT_FUNDS`, `INVALID_CURRENCY`         |
| **Idempotency**     | Can repeat safely?         | `POST` with `Idempotency-Key` header             |
| **SLA**             | Latency + availability     | P99 < 500ms; 99.9% uptime                        |
| **Rate limits**     | Max requests               | 1000 req/min per client                          |
| **Versioning**      | How versions are signalled | URL path `/v1/`, `/v2/`; header `Accept-Version` |

**CONTRACT TYPES:**

| Type               | Format         | Used For                             |
| ------------------ | -------------- | ------------------------------------ |
| **OpenAPI (REST)** | YAML/JSON      | REST HTTP APIs                       |
| **Protobuf**       | `.proto` file  | gRPC APIs                            |
| **AsyncAPI**       | YAML           | Event/message APIs (Kafka, RabbitMQ) |
| **Pact**           | JSON pact file | Consumer-driven contract testing     |
| **GraphQL schema** | `.graphql`     | GraphQL APIs                         |

**CONTRACT OWNERSHIP:**
Two models:

1. **Provider-owned contract** (traditional): Provider defines and publishes the contract. Consumers must adapt to it. Risk: provider makes changes without considering consumer impact.
2. **Consumer-driven contract** (Pact): Consumers define what they need. Provider must satisfy all consumer contracts. Ensures no breaking changes are made without awareness.

**THE TRADE-OFFS:**
**Gain:** Explicit dependency management; safe independent deployment; breaking changes detected before production; enables trunk-based development across team boundaries; living documentation (contract = spec).
**Cost:** Overhead of maintaining contracts (especially for many consumer teams); contract testing CI integration; versioning complexity; risk of over-specification (contract tests become too brittle, failing on irrelevant changes).

---

### 🧪 Thought Experiment

**SETUP:**
Payment Service publishes this contract: `POST /v1/payments` accepts `{amount, currency, orderId}`, returns `{paymentId, status}`.

Order Service tests against this contract. Tests pass. Payment Service is deployed.

**THE SURPRISE:**
Payment Service team decides to add response validation: they now return `{paymentId, status, processingFee, taxAmount, merchantReference}`. No fields removed or renamed. Order Service code ignores the new fields (they don't use them). Everything works.

Three months later, Payment Service team removes `processingFee` (unused by consumers, they assume). Order Service team had silently started using `processingFee` without updating the contract. `processingFee` removal breaks Order Service.

**THE LESSON:**
Contracts work bidirectionally. Consumer-driven contracts (Pact) solve this: the Order Service consumer contract would have declared its dependency on `processingFee`. When Payment Service tried to remove `processingFee`, the consumer contract test would have failed - catching the breaking change before deployment.

---

### 🧠 Mental Model / Analogy

> A service contract is like a legal API terms of service. When you sign up to use a payment processor's API (Stripe, PayPal): they publish a specification (the contract). You build to that specification. They promise not to change the specification in a backward-incompatible way within a major version. If they need to change, they release v2 and maintain v1 during a sunset period. Without this contract, every API update would risk breaking every integration. The contract enables confidence and independent development.

- "Legal terms of service" → service contract
- "Build to the specification" → consumer depends on contract
- "Backward-incompatible change = new major version" → versioning strategy
- "Maintain v1 during sunset period" → deprecation process
- "Confidence in independent development" → teams deploy independently

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A service contract is a written agreement between a service and its users: "I will accept requests in this format, and I will respond in this format, and I promise not to change it without warning." Like a menu: it says what you can order and what you'll get.

**Level 2 - OpenAPI specification (junior developer):**
Write an OpenAPI 3.0 spec for your REST API. Publish it to an internal API portal or as a `openapi.yaml` in your repository. Use it to generate server stubs and client SDKs. Tools: Swagger UI for documentation; openapi-generator for SDK generation; springdoc-openapi for auto-generation from Spring annotations.

**Level 3 - Contract testing in CI (mid-level engineer):**
Integrate consumer-driven contract testing (Pact) into CI. Consumers generate Pact files. Provider CI runs provider verification tests against Pact Broker before every deployment. `can-i-deploy` check prevents deployment if any consumer contract is violated. This makes the contract machine-enforced, not just documentation.

**Level 4 - Contract governance at scale (senior/staff):**
At large organisations with hundreds of services and thousands of consumer-provider pairs, contract governance becomes a platform capability: an internal API catalog (Backstage, Apicurio) hosts all service contracts; a contract compatibility service validates every proposed API change against all known consumers; breaking changes require explicit deprecation workflow (announcement → sunset period → removal); API versioning policy (SemVer: major = breaking, minor = additive) is enforced by tooling. Some organisations adopt a "design-first" approach: the OpenAPI spec is written before any code, reviewed by consumer teams, approved, and then code is generated from the spec. This inverts the common "code-first" approach where the spec is generated from existing code after the fact.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ Service Contract Lifecycle                              │
└─────────────────────────────────────────────────────────┘

Provider:
  Publish: openapi.yaml → API Catalog
  Implement: service matches spec
  CI: openapi-diff checks no breaking changes between versions

Consumer:
  Build: generates client from openapi.yaml
  Pact: writes consumer contract tests
  CI: generates pact file → uploads to Pact Broker

Provider CI:
  Pull: pact files from Pact Broker
  Test: provider verification (does provider satisfy all pacts?)
  Check: can-i-deploy (all consumer pacts passing?)
  Deploy: only if can-i-deploy says YES

Change Flow (breaking change):
  Provider: wants to rename field A → B
  → Run consumer pact verification → FAIL (consumers use A)
  → Option 1: coordinate with consumers; update all consumers first
  → Option 2: bump major version (v2 API); serve both v1 and v2
  → Provider: remove v1 after all consumers migrated
```

---

### 💻 Code Example

**OpenAPI 3.0 contract (payment-service.yaml):**

```yaml
openapi: 3.0.3
info:
  title: Payment Service API
  version: 1.3.0
paths:
  /v1/payments:
    post:
      summary: Process a payment
      operationId: processPayment
      parameters:
        - in: header
          name: Idempotency-Key
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PaymentRequest"
      responses:
        "201":
          description: Payment processed
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/PaymentResponse"
        "422":
          $ref: "#/components/responses/UnprocessableEntity"

components:
  schemas:
    PaymentRequest:
      type: object
      required: [amount, currency, orderId]
      properties:
        amount:
          type: number
          format: decimal
          minimum: 0.01
          example: 49.99
        currency:
          type: string
          pattern: "^[A-Z]{3}$"
          example: "USD"
        orderId:
          type: string
          format: uuid
    PaymentResponse:
      type: object
      properties:
        paymentId:
          type: string
          format: uuid
        status:
          type: string
          enum: [APPROVED, DECLINED, PENDING]
        processedAt:
          type: string
          format: date-time
  responses:
    UnprocessableEntity:
      description: Business rule violation
      content:
        application/json:
          schema:
            type: object
            properties:
              errorCode:
                type: string
                enum: [INSUFFICIENT_FUNDS, INVALID_CURRENCY, DUPLICATE_PAYMENT]
              message:
                type: string
```

**CI check: detect breaking changes (openapi-diff):**

```bash
# openapi-diff: compare current spec against main branch spec
docker run --rm \
  -v $(pwd):/specs \
  openapitools/openapi-diff:latest \
  /specs/openapi-main.yaml \
  /specs/openapi-branch.yaml \
  --fail-on-incompatible
# Exits non-zero if breaking changes detected → CI fails
```

---

### ⚖️ Comparison Table

| Contract Type              | Enforcement                   | Direction       | Best For                       |
| -------------------------- | ----------------------------- | --------------- | ------------------------------ |
| **OpenAPI spec**           | Documentation + CI diff check | Provider-driven | REST APIs; large consumer base |
| **Pact contract**          | Automated testing             | Consumer-driven | Internal microservice pairs    |
| **Protobuf schema**        | Compiler enforcement          | Provider-driven | gRPC, high-performance         |
| **AsyncAPI**               | Documentation                 | Provider-driven | Event streaming                |
| **Informal (no contract)** | None                          | -               | Avoid in production systems    |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                          |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| "We have Swagger docs - that's our contract"     | Swagger docs generated from code describe current behaviour; a contract is a commitment about future behaviour   |
| Contracts only matter for external APIs          | Internal service contracts are equally important; internal API breakage causes internal outages                  |
| Consumer-driven contracts are just about testing | They are primarily about explicit dependency declaration and change safety; testing is the enforcement mechanism |
| Contracts prevent all breaking changes           | Contracts prevent accidental breaking changes; intentional changes require versioning and coordination           |

---

### 🚨 Failure Modes & Diagnosis

**Provider Changes Contract Without Notice**

**Symptom:** Consumer starts receiving 422/500 errors after a provider deployment.

**Root Cause:** Provider changed request/response schema; no contract version bump; no consumer notification.

**Prevention:**

```bash
# In provider CI: fail if breaking changes vs previous version
openapi-diff main.yaml feature-branch.yaml --fail-on-incompatible
# Run Pact provider verification against all consumer pacts
```

---

### 🔗 Related Keywords

**Prerequisites:** `Backward Compatibility`, `Consumer-Driven Contract Testing`, `API Gateway`

**Builds On This:** `Backward Compatibility`, `Versioning Strategy`, `Consumer-Driven Contract Testing`

**Related Patterns:** `Versioning Strategy`, `API Gateway`, `Consumer-Driven Contract Testing`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Formal written agreement: what a service  │
│              │ accepts, returns, and guarantees          │
├──────────────┼───────────────────────────────────────────┤
│ FORMATS      │ OpenAPI (REST), Protobuf (gRPC),          │
│              │ AsyncAPI (events), Pact (consumer-driven) │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Breaking change = new major version       │
│              │ Additive change = backward compatible     │
├──────────────┼───────────────────────────────────────────┤
│ CI ENFORCE   │ openapi-diff + Pact can-i-deploy          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "What I promise; what you can depend on"  │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
A service contract is an explicit promise about what a service will provide and what it will not change without notice. Without an explicit contract, every change is potentially breaking and every breaking change is invisible until it causes a production failure. Making the contract explicit (in code, in tests, in documentation) makes the implicit dependency explicit - which is the first step to managing it.

**Where else this pattern appears:**
- **HTTP API contracts (OpenAPI):** An OpenAPI specification is a formal service contract for a REST API - explicit promises about endpoints, fields, and types.
- **Message schema contracts:** An Avro or Protobuf schema is a service contract for a message - explicit promises about fields, types, and backward compatibility rules.
- **Database schema as contract:** A database table schema is a service contract for data storage - explicit promises about columns, types, and constraints shared with dependent services.

---

### 💡 The Surprising Truth

The most counterintuitive finding about service contracts is that having no contract often feels better than having one. Without a contract, every change is possible and teams feel productive. With a contract, every breaking change is flagged and API evolution requires coordination. This slowdown is exactly the right signal: it reveals the cost of change that was always there, previously invisible (manifesting as production incidents instead of CI failures). Teams that 'move fast' without contracts defer the cost of API evolution to production, where it is 10x more expensive.
---

### 🧠 Think About This Before We Continue

**Q1.** Your team owns the Order Service (consumer) and the Payment Service (provider). The Payment Service team wants to add request validation: they'll now return `400` for `amount < 0.01` (previously they returned `200` with an error body). From a service contract perspective, is this a breaking change? Why? How should the Payment Service team handle this change to maintain contract integrity?

*Hint:* Think about what a contract means for a status code change: the Payment Service previously returned 200 with an error body for invalid amounts - this was the documented, contractual behavior. Changing to 400 for the same input is a breaking change for consumers that check for 200 status and parse the body for success/failure. Semantically, 400 is more correct HTTP. Contractually, it breaks consumers. The correct approach: version the API (v2 returns 400 for validation), maintain v1 with the old 200-for-everything behavior during migration, sunset v1 after all consumers migrate to v2.

**Q2.** You discover that 5 different services consume the Order Service API, but each team wrote their integration by reading the Order Service source code - no formal contract exists. Design a process to retroactively create a service contract for the Order Service. How do you discover what each consumer actually depends on? What format would you use, and how would you enforce the contract going forward?

*Hint:* Think about how to discover what each consumer actually uses: (1) ask each team (fastest, incomplete); (2) review each consumer's code (accurate, time-consuming); (3) add API access logging that records which fields are accessed in responses (most accurate, requires instrumentation); (4) have each consumer write a Pact contract based on their actual usage (most rigorous - produces a machine-verifiable contract). The Pact approach is the most valuable retroactively: each team's Pact contract becomes the ongoing enforceable specification for what Order Service must not break.

**Q3 (Design Trade-off):** You provide an internal service with 30 consumers. A business requirement forces a semantic change: `ACTIVE` now means 'customer is active and premium' (previously 'customer is active'). 15 consumers use `status=ACTIVE` in their business logic. Design the contract change management process.

*Hint:* Think about what 'semantic change without a field rename' means: changing what `ACTIVE` means is a silent breaking change - consumers checking `status=ACTIVE` will silently get different behavior without any code change on their part. The correct approach: add a new field `premium: boolean` for the new semantic, maintain `ACTIVE` with the original meaning for backward compatibility, deprecate the conflated meaning explicitly in the OpenAPI spec, and coordinate migration with the 15 affected teams with a defined sunset date.
