---
id: MSV-070
title: Service Contract
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-010, MSV-061
used_by: MSV-061, MSV-062, MSV-071
related: MSV-061, MSV-062, MSV-071, MSV-010, MSV-020, MSV-003
tags:
  - microservices
  - api
  - deep-dive
  - contracts
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/microservices/service-contract/
---

⚡ TL;DR - Service Contract: the formal, versioned
specification of a service's API - what it accepts,
what it returns, what errors it can produce, and
what behaviors it guarantees. For REST: OpenAPI
spec (swagger.yaml). For async: AsyncAPI spec or
SchemaRegistry (Avro/Protobuf). The contract is
the PROMISE a service makes to its consumers:
"If you call me this way, I will respond this way."
Breaking a contract (removing a field, changing
a type) without versioning: breaks all consumers.
Contract-first development: write the spec first,
implement second. Consumer-Driven Contracts (Pact):
consumers define the minimum they need.

| #070 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | API Gateway, Consumer-Driven Contract Testing | |
| **Used by:** | Consumer-Driven Contract Testing, Pact (Contract Testing), API Evolution Strategy | |
| **Related:** | Consumer-Driven Contract Testing, Pact (Contract Testing), API Evolution Strategy, API Gateway, Service Mesh, Domain-Driven Design | |

---

### 🔥 The Problem This Solves

**API CHANGES BREAK CONSUMERS UNEXPECTEDLY:**
Without a formal contract: a provider developer
renames a field (feels more descriptive), removes
an endpoint (seems unused), or changes a response
type (from string to integer). Consumers break
silently (nulls instead of values) or loudly
(deserialization exceptions). The provider team
didn't know anyone was using those fields. Service
contracts: make the interface explicit, versioned,
and communicated. Breaking changes require a new
contract version. Consumers know what version
they depend on.

---

### 📘 Textbook Definition

**Service Contract** (also called API Contract or
Interface Contract) is the formal specification
of a service's public interface: the set of
promises a service makes to its consumers about
what it accepts and what it returns. A service
contract specifies: (1) **Operations** - available
HTTP endpoints/methods or Kafka topics; (2)
**Request schema** - parameters, headers, body
structure and types; (3) **Response schema** -
status codes, body structure, fields, types; (4)
**Error handling** - error codes and their meanings;
(5) **Behavioral guarantees** - idempotency,
ordering, consistency guarantees; (6) **SLA** -
latency guarantees, availability SLOs.
Formal representations: OpenAPI/Swagger spec
(REST), gRPC proto files, AsyncAPI spec (Kafka/
event-driven), Avro/Protobuf schemas (data
contracts for messages). Contract-first development
("design-first"): write the contract before
implementing the service; enables parallel
consumer development. Consumer-Driven Contract
Testing (CDCT/Pact): consumers define a minimal
contract (what they need); providers verify
they fulfill it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Service contract: the formal specification of
what a service promises to accept and return.
Violating it = breaking change. Versioned contracts
allow evolution without breaking consumers.

**One analogy:**
> Service contract is like a restaurant menu.
> The menu (contract) specifies: what dishes are
> available (endpoints), what you order (request
> format), what you receive (response format), and
> the price (SLA). Changing the menu: valid (add
> new dish, change price). Removing a dish without
> notice: breaks customers who expected it (breaking
> change). Publishing a new menu version (v2):
> while keeping old menu available for existing
> customers (backward compatibility). Seasonal
> menu (v3): replaces the old one with advance
> notice (deprecation policy).

**One insight:**
Service contracts are fundamentally about TRUST
between teams. Provider teams want maximum freedom
to evolve their services. Consumer teams want
stability guarantees. The contract is the negotiated
boundary: provider promises to honor the contract;
consumer promises not to depend on undocumented
behavior. Without contracts: implicit assumptions
accumulate ("I know the provider returns users in
alpha order - I depend on that"). With contracts:
only documented behaviors are valid dependencies.

---

### 🔩 First Principles Explanation

**CONTRACT TYPES BY API STYLE:**

```
REST API CONTRACT (OpenAPI 3.0):
  openapi: "3.0.0"
  paths:
    /customers/{customerId}:
      get:
        description: Get customer by ID
        parameters: [{name: customerId, required: true}]
        responses:
          200:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Customer'
          404:
            $ref: '#/components/responses/NotFound'
  components:
    schemas:
      Customer:
        required: [customerId, name, email]
        properties:
          customerId: {type: string}
          name: {type: string}
          email: {type: string, format: email}
          # phone: optional, may be absent
  # This is the CONTRACT:
  # Required fields: customerId, name, email
  # Optional fields: phone
  # Breaking change: remove name or email
  # Non-breaking change: add new optional field

KAFKA EVENT CONTRACT (Avro schema):
  {
    "type": "record",
    "name": "OrderCreated",
    "namespace": "com.example.orders",
    "fields": [
      {"name": "orderId", "type": "string"},
      {"name": "customerId", "type": "string"},
      {"name": "totalAmount",
       "type": {"type": "bytes", "logicalType": "decimal",
                "precision": 10, "scale": 2}}
    ]
  }
  # Stored in Confluent Schema Registry
  # Version controlled; backward/forward compatibility
  # checked on publish

gRPC CONTRACT (Proto):
  syntax = "proto3";
  service OrderService {
    rpc GetOrder (GetOrderRequest)
      returns (Order);
    rpc CreateOrder (CreateOrderRequest)
      returns (CreateOrderResponse);
  }
  message Order {
    string order_id = 1;    // field tag 1
    string customer_id = 2; // field tag 2
    // Adding field 3: backward compatible
    // Removing field 2: backward incompatible
    //   (do NOT delete; mark deprecated instead)
  }
```

**BREAKING vs NON-BREAKING CHANGES:**

```
NON-BREAKING (safe for existing consumers):
+ Add a new optional request parameter
+ Add a new optional response field
+ Add a new endpoint
+ Return a more specific error code
  (consumer ignores it; existing handling still works)

BREAKING (requires contract version bump):
- Remove a response field consumers depend on
- Rename a response field
- Change response field type (string -> int)
- Change required request parameter to required
  with different validation
- Remove an endpoint
- Change HTTP method (POST -> PUT)
- Change URL structure (/orders/{id} -> /orders/v2/{id})
- Change response status code for existing behavior
```

---

### 🧪 Thought Experiment

**CONTRACT-FIRST vs CODE-FIRST DEVELOPMENT:**

```
SCENARIO: 3 teams building: order-service (producer),
customer-service (consumer), notification-service
  (consumer)

CODE-FIRST (no contract):
  Week 1: order-service team builds API
  Week 1: customer-service team: "waiting for API
          to be deployed to know what fields exist"
  Week 3: order-service deployed
  Week 3: customer-service team starts consuming
  Week 5: order-service renames "email" -> "emailAddr"
          (feels cleaner internally)
  Week 5: customer-service BREAKS
  Week 5: 2 teams: emergency coordination
  Total time: 5 weeks; 1 breaking incident

CONTRACT-FIRST:
  Day 1: All 3 teams agree on OpenAPI spec
         for order-service API
         (10 fields, required/optional defined)
  Day 1: customer-service team: generate client
         code from OpenAPI spec (OpenAPI codegen)
         Start implementing against mock server
  Day 1: notification-service: same
  Day 1: order-service: implement against the spec
  Week 2: all 3 services complete simultaneously
  Week 5: order-service wants to rename "email":
          OpenAPI spec is the contract
          Breaking change: requires version bump
          (new spec /api/v2/orders)
          OR: backward compat (keep both names,
          deprecate old over 2 releases)
          Consumer notified before change: no surprise
  
  Total time: 2 weeks; 0 breaking incidents
  Benefit: parallel development; formal change management
```

---

### 🧠 Mental Model / Analogy

> Service contract is like building codes in
> construction. When you build a house: you promise
> (contract) to follow specific standards (fire
> safety, structural integrity, electrical codes).
> Future owners depend on these standards being
> met. If the builder later "upgrades" by removing
> required fire exits (breaking change): violates
> the contract; others are harmed. Adding a new
> optional feature (bonus room): non-breaking change;
> existing occupants benefit without being harmed.
> The building code (OpenAPI spec) defines what
> the contract requires. Inspectors (contract tests,
> CI/CD gates) verify compliance.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A service contract is the documented agreement
between a service and its users: what the service
accepts, what it returns, and what it guarantees.
If the service changes in a way that breaks this
agreement: it's a breaking change and requires
careful management.

**Level 2 - OpenAPI basics (junior developer):**
OpenAPI 3.0: standard format for REST API contracts.
Spring Boot: `springdoc-openapi-starter-webmvc-ui`
(auto-generates from annotations). `@OpenAPIDefinition`,
`@Schema`, `@Operation`: document your endpoints.
Generate client SDKs: `openapi-generator-cli`
produces Java, TypeScript, Go clients from spec.
Publish spec: `/v3/api-docs` endpoint (JSON);
Swagger UI: `/swagger-ui.html`.

**Level 3 - Versioning strategies (mid-level):**
URL versioning (`/api/v1/`, `/api/v2/`): most
visible; easiest for routing. Header versioning
(`Accept: application/vnd.company.v2+json`):
cleaner URLs; harder to test in browser. Query
parameter (`?version=2`): simple; not RESTful.
Maintain old versions for deprecation period:
define how long (e.g., 2 major versions, or 6
months). Semantic versioning: MAJOR (breaking),
MINOR (non-breaking feature), PATCH (bug fix).
OpenAPI: include version in `info.version`.

**Level 4 - Schema Registry for async (senior):**
Confluent Schema Registry: stores Avro/JSON/Protobuf
schemas for Kafka topics. Compatibility levels:
`BACKWARD` (new schema can read old messages),
`FORWARD` (old schema can read new messages),
`FULL` (both directions). Enforced on producer:
producer must register schema before publishing.
Incompatible schema: rejected by Registry. This
is the contract enforcement for event-driven
microservices. `io.confluent:kafka-avro-serializer`:
seamlessly encodes schema ID with each message.

**Level 5 - Contract governance (principal):**
Contract governance at scale: 50 services, 200+
API endpoints, 100+ Kafka topics. Tools: Backstage
(Spotify's service catalog) with OpenAPI plugin:
centralized contract discovery; which services
provide which APIs; dependency graph. API change
management process: API changes require a PR
to the contract repo (OpenAPI spec), reviewed
by API governance team, consumers notified of
breaking changes. API deprecation automation:
count how many consumers use each endpoint
(via access logs or Pact Broker); automatically
determine when it's safe to remove. Contract
testing as CI gate: Pact broker verifies all
consumers before provider deploys.

---

### ⚙️ How It Works (Mechanism)

```yaml
# OpenAPI 3.0: complete service contract example
# customer-service-contract.yaml
openapi: "3.0.3"
info:
  title: Customer Service API
  version: "2.1.0"
  description: |
    Customer Service manages customer profiles.
    SLA: p99 < 100ms; availability 99.9%.
    Breaking changes: announced 30 days prior.
paths:
  /customers/{customerId}:
    get:
      summary: Get customer by ID
      operationId: getCustomer
      parameters:
      - name: customerId
        in: path
        required: true
        schema: {type: string}
      responses:
        '200':
          description: Customer found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '404':
          description: Customer not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error
components:
  schemas:
    Customer:
      type: object
      required: [customerId, name, email]
      # REQUIRED fields: contract-guaranteed
      # Consumer MAY depend on these
      properties:
        customerId:
          type: string
          description: Unique customer identifier
          example: cust-abc-123
        name:
          type: string
          description: Customer full name
          example: Alice Smith
        email:
          type: string
          format: email
          description: Customer primary email
          example: alice@example.com
        phone:
          type: string
          nullable: true
          description: |
            OPTIONAL. Not all customers have phone.
            Consumer must handle null.
          example: +1234567890
        # Breaking change: removing name or email
        # Non-breaking: adding new optional field
    ErrorResponse:
      type: object
      required: [errorCode, message]
      properties:
        errorCode: {type: string}
        message: {type: string}
        details: {type: string, nullable: true}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CONTRACT LIFECYCLE:

DESIGN PHASE:
  API review with consumers (1-hour meeting)
  Define: endpoints, required/optional fields, errors
  Write: OpenAPI spec (contract-first)
  Publish: to API gateway/developer portal
  Generate: client SDKs for consuming teams

DEVELOPMENT PHASE:
  Provider: implements against spec
  Consumers: develop against mock server
    (generated from OpenAPI spec)
  Pact tests: consumers publish contracts
  Provider verification: passes against spec

CHANGE MANAGEMENT:
  Non-breaking change (add field):
    Update spec (version: 2.1.1)
    No consumer notification required
    All existing consumers: still work
  Breaking change (remove field):
    Create new spec version (version: 3.0.0)
    New endpoint: /api/v3/customers/{id}
    Announce: 30-day deprecation of v2
    Consumers: migrate to v3 within 30 days
    CI gate: Pact broker verifies all consumers
             before v2 is removed

GOVERNANCE:
  API changes: PR to contract repo (openapi/)
  Review: API governance team (breaking changes)
  Merge: triggers consumer notification
  CI: validate spec syntax (openapi-spec-validator)
  CI: check Pact verification status before deploy
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: implicit vs formal contract**

```java
// BAD: implicit contract in code only
// Consumers must read source code to understand API
// No versioning; changes are invisible
@GetMapping("/customers/{id}")
public Customer getCustomer(@PathVariable String id) {
    Customer c = repo.findById(id).orElseThrow();
    return c; // Returns ALL fields (even internal ones)
    // consumer doesn't know which fields to depend on
    // Field removed tomorrow? Consumer breaks silently
}
// Breaking change invisible: no spec, no version,
// no notification. Just a code change.
```

```java
// GOOD: contract-first with OpenAPI annotations
@GetMapping("/api/v2/customers/{customerId}")
@Operation(summary = "Get customer by ID",
    description = "Returns customer profile. " +
        "Guaranteed fields: customerId, name, email. " +
        "Optional fields: phone (may be null).")
@ApiResponse(responseCode = "200",
    content = @Content(schema =
        @Schema(ref = "#/components/schemas/CustomerV2")))
@ApiResponse(responseCode = "404",
    description = "Customer not found")
public ResponseEntity<CustomerResponseV2> getCustomer(
        @PathVariable @Parameter(description =
            "Unique customer ID, format: cust-xxx-xxx")
        String customerId) {
    // Implementation against the contract spec
    // Spec is the source of truth, not the code
}
// OpenAPI spec auto-generated: serves as contract
// Version: /api/v2/ -> consumers know which version
// Breaking change: creates /api/v3/ with migration guide
// Non-breaking: add optional field to spec (no new version)
```

---

### ⚖️ Comparison Table

| Contract Type | Format | Tooling | Best For |
|---|---|---|---|
| **OpenAPI** | YAML/JSON | Swagger UI, codegen | REST APIs |
| **gRPC Proto** | .proto | Protobuf codegen | Binary protocols, internal |
| **Avro Schema** | JSON | Confluent Schema Registry | Kafka events |
| **AsyncAPI** | YAML | AsyncAPI Studio | Event-driven docs |
| **Pact** | JSON | Pact Broker | Consumer-driven verification |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The database schema IS the service contract | The database schema is an INTERNAL implementation detail of the service. The service contract is the PUBLIC API: HTTP endpoints, request/response schema, Kafka events. Exposing the DB schema as the API (e.g., via a direct DB-to-REST mapping with no abstraction) tightly couples consumers to internal implementation. When you change the DB schema (for performance): you break the API contract. Service contracts should be designed independently of the DB schema. |
| Adding a new required field is non-breaking | Adding a new REQUIRED field to a request is BREAKING: existing consumers don't send the new field; requests fail validation. Adding a new OPTIONAL field to a request: non-breaking (existing consumers don't send it; that's valid). Adding a new field to a RESPONSE: always non-breaking (existing consumers ignore unknown fields). Rule: never add required request fields to an existing API version; it always breaks consumers. |
| OpenAPI-generated documentation is sufficient as a contract | OpenAPI describes the schema (what fields exist and their types). It does NOT document: business semantics ("email must be unique in the system"), ordering guarantees ("orders returned in reverse chronological order - do not rely on this"), behavioral guarantees ("this endpoint is idempotent"), error semantics ("404 means account does not exist, not that it's deleted"). A contract requires both the schema AND the behavioral documentation. Pact contracts also capture consumer BEHAVIOR expectations, not just schema. |

---

### 🚨 Failure Modes & Diagnosis

**Field dependency on undocumented behavior causes production bug**

**Symptom:**
order-service feature release: orders being returned
in wrong order on the dashboard. Root cause: order-
service was relying on customer-service returning
customers in alphabetical order (by name). The
customer-service was returning them alphabetically
"by accident" (PostgreSQL scan order happened to
be alphabetical for historical data). New data:
inserted in different order. The order-service
developer assumed alphabetical order was guaranteed
(it was never documented).

**Root Cause:**
No formal service contract. order-service depended
on UNDOCUMENTED behavior. customer-service changed
internal data access pattern (for performance).
Behavior changed. order-service broke.

**Fix:**
1. Document in OpenAPI spec: response field ordering
   is NOT guaranteed; consumers must sort if needed.
2. If alphabetical order IS needed: add sort parameter
   to the contract (`?sort=name&order=asc`).
3. Add to contract governance: review process for
   any code change that affects response ordering.

---

### 🔗 Related Keywords

**Enforces contracts:**
- `Consumer-Driven Contract Testing` - consumers
  define minimal contracts; providers verify
- `Pact (Contract Testing)` - the tool for CDCT

**Evolution of contracts:**
- `API Evolution Strategy` - how contracts evolve
  over time without breaking consumers

**Foundation:**
- `API Gateway` - enforces contract at edge
  (validates requests against contract schema)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ TYPES        │ OpenAPI (REST), Proto (gRPC),            │
│              │ Avro/AsyncAPI (Kafka), Pact (CDCT)       │
├──────────────┼──────────────────────────────────────────┤
│ BREAKING     │ Remove field, rename field, change type, │
│              │ add required request param               │
├──────────────┼──────────────────────────────────────────┤
│ SAFE CHANGES │ Add optional response field, new endpoint│
│              │ Add optional request param               │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Formal promise: accept this, return that│
│              │  Breaking change: new version required"  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Service contract: formal spec (OpenAPI/Avro/Proto)
   of what a service promises. Breaking a contract
   (remove field, change type) requires a new
   version with consumer migration.
2. Breaking vs non-breaking: adding optional
   response fields = safe; removing/renaming fields
   = breaking; adding required request params = breaking.
3. Contract-first: write the OpenAPI spec before
   coding. Enables parallel development. Generates
   client SDKs and mock servers.

**Interview one-liner:**
"Service Contract: formal specification of a service's
API (OpenAPI for REST, Avro for Kafka, Proto for gRPC).
Defines: endpoints, required/optional fields, errors,
behavioral guarantees. Breaking change (remove field,
change type): requires new version (/api/v2/) with
deprecation period for consumers to migrate. Non-
breaking: add optional response fields. Contract-first
development: write OpenAPI spec before coding;
enables parallel development; generates client SDKs.
Enforced by: Consumer-Driven Contract Tests (Pact) and
CI gates that prevent deployment if contracts are violated."

---

### 💡 The Surprising Truth

The most violated service contract principle in
real-world microservices is not technical - it's
"Postel's Law" (Robustness Principle): "Be
conservative in what you send, liberal in what
you accept." Consumers should not break when
providers add NEW optional fields to responses
(be liberal in accepting). But many Java Jackson
configurations fail with `UnrecognizedPropertyException`
when encountering unknown fields:
```java
// BAD: strict deserialization breaks on new fields
@JsonIgnoreProperties(allowGetters = false)
// GOOD: tolerant to new fields
@JsonIgnoreProperties(ignoreUnknown = true)
```
Or globally: `ObjectMapper.configure(
DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES,
false)`. Setting this: makes all consumers
automatically backward-compatible with new response
fields from providers. Missing this setting:
every new non-breaking field addition by a provider
causes production failures in consumers.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **OPENAPI** Write a complete OpenAPI 3.0 spec
   for a customer-service API: GET /customers/{id}
   (with required/optional response fields and
   error responses), POST /customers (request
   schema validation), and define components/schemas
   for reuse.
2. **BREAKING CHANGES** Given 10 proposed API
   changes: classify each as breaking or non-
   breaking, explain why, and propose how to
   make breaking changes backward-compatible.
3. **VERSIONING** For a payment-service API with
   3 consumers: design the migration from v1 to
   v2 (breaking change: rename `amount` to
   `amountInCents`). How long do you maintain v1?
   How do you track when consumers have migrated?
4. **SCHEMA REGISTRY** Configure Confluent Schema
   Registry for an OrderCreated Kafka event:
   register the Avro schema, set compatibility to
   BACKWARD, try to register a breaking change
   (remove a field), observe the rejection.
5. **JACKSON** Configure Spring Boot Jackson
   `ObjectMapper` to be tolerant of unknown fields
   globally. Explain why this is important for
   consumer resilience to provider contract evolution.

---

### 🧠 Think About This Before We Continue

**Q1.** You have a customer-service API (v1) with
20 consumers. You need to change the `dateOfBirth`
field from a string ("YYYY-MM-DD") to a LocalDate
object (ISO-8601 JSON). This is a type change -
a breaking change. Design the complete migration:
what changes in the API spec, what the versioning
strategy is, how consumers are notified, and
what the timeline looks like.

**Q2.** A team wants to use Avro with Confluent
Schema Registry for Kafka events. They have an
OrderCreated event with 8 fields. In 3 months:
they need to add a `discountCode` field (nullable)
and remove an `internalTrackingId` field (only
used internally). Using the Schema Registry
compatibility rules: can both changes be done in
one schema version? In what order should they
be deployed? Why?

**Q3.** Your organization is creating a new "API
governance" process. Propose: (a) what OpenAPI
validation should happen in CI before a service
deployment, (b) what approval process is needed
for breaking changes, (c) how you track which
consumers use which API endpoints to know when
it's safe to remove deprecated endpoints, and
(d) how you enforce backward compatibility for
Kafka events via Schema Registry.