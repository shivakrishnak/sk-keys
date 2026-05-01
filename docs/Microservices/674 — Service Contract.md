---
layout: default
title: "Service Contract"
parent: "Microservices"
nav_order: 674
permalink: /microservices/service-contract/
number: "674"
category: Microservices
difficulty: ★★★
depends_on: "API Gateway, Consumer-Driven Contract Testing"
used_by: "Backward Compatibility, Pact (Contract Testing)"
tags: #advanced, #microservices, #distributed, #architecture, #testing
---

# 674 — Service Contract

`#advanced` `#microservices` `#distributed` `#architecture` `#testing`

⚡ TL;DR — A **Service Contract** is the formal agreement between a provider service and its consumers: what endpoints exist, what request/response shapes are expected, what error codes are returned. It's the API surface published as a specification (OpenAPI, AsyncAPI, Protobuf IDL). Breaking a contract = breaking all consumers who depend on it.

| #674            | Category: Microservices                         | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | API Gateway, Consumer-Driven Contract Testing   |                 |
| **Used by:**    | Backward Compatibility, Pact (Contract Testing) |                 |

---

### 📘 Textbook Definition

A **Service Contract** (also known as an API Contract) is a formal specification that defines the observable interface of a service: the set of operations it provides, the data structures it accepts and returns, the error conditions it signals, and the behavioral guarantees (SLA, ordering, idempotency) it upholds. In REST APIs, the contract is typically expressed as an **OpenAPI (Swagger) specification**. In gRPC services, as a **Protocol Buffers (`.proto`) IDL file**. In event-driven systems, as an **AsyncAPI specification** or Avro/Protobuf schema registered in a Schema Registry. The key property of a service contract: it is an independent artifact, separate from the implementation — it can be validated, versioned, tested, and published without touching the service code. **Consumer-Driven Contracts** (CDC) is the practice where consumers specify what they need from a provider (their "consumer contract"), and the provider verifies that its implementation satisfies all registered consumer contracts — using tools like Pact. This inverts the traditional model where the provider decides the contract and consumers adapt.

---

### 🟢 Simple Definition (Easy)

A service contract is the official promise a service makes to its callers: "I will accept requests in this exact format, and return responses in this exact format." Break the promise (change the format) without notice → everyone who calls you breaks. The contract is the API specification document (OpenAPI YAML/JSON). It's the source of truth for what the API does, independent of the code.

---

### 🔵 Simple Definition (Elaborated)

Order Service publishes its contract: `GET /orders/{id}` returns `{orderId, customerId, status, totalAmount, items}`. Inventory Service, Payment Service, and Notification Service all call this endpoint and expect these fields. If Order Service renames `totalAmount` to `total` without communicating → all three consumers break at runtime. With a contract (OpenAPI spec): the change is detected before deployment (contract diff), consumers are notified, and they update their code before the breaking change ships. Consumer-Driven Contracts go further: each consumer specifies exactly which fields they need, and the provider CI pipeline validates against all consumer contracts before every deployment.

---

### 🔩 First Principles Explanation

**OpenAPI specification — the REST service contract:**

```yaml
# order-service/src/main/resources/api-spec/openapi.yaml
openapi: 3.0.3
info:
  title: Order Service API
  version: 2.1.0
  description: |
    Service contract for Order Service.
    Breaking changes require major version bump and deprecation notice.
paths:
  /orders/{orderId}:
    get:
      operationId: getOrder
      summary: Get order by ID
      parameters:
        - name: orderId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        "200":
          description: Order found
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/OrderResponse"
        "404":
          description: Order not found
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "401":
          description: Unauthorized (missing or invalid JWT)

components:
  schemas:
    OrderResponse:
      type: object
      required: [orderId, customerId, status, totalAmount, createdAt]
      properties:
        orderId:
          type: string
          format: uuid
          example: "550e8400-e29b-41d4-a716-446655440000"
        customerId:
          type: string
          format: uuid
        status:
          type: string
          enum: [PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED]
        totalAmount:
          type: number
          format: decimal
          description: Total order amount in USD
        # NEVER remove a field from here without a major version bump
        # NEVER change a field's type without a major version bump
        # CAN add new optional fields (backward compatible)
        createdAt:
          type: string
          format: date-time
```

**Contract-first development: generate code from spec:**

```bash
# Generate Spring Boot server stubs from OpenAPI spec:
# (build.gradle.kts)
plugins {
    id("org.openapi.generator") version "7.2.0"
}

openApiGenerate {
    generatorName.set("spring")
    inputSpec.set("$rootDir/src/main/resources/api-spec/openapi.yaml")
    outputDir.set("$buildDir/generated-sources/openapi")
    apiPackage.set("com.example.order.api.generated")
    modelPackage.set("com.example.order.model.generated")
    configOptions.set(mapOf(
        "interfaceOnly" to "true",        // generate interface, implement manually
        "useSpringBoot3" to "true",
        "useBeanValidation" to "true"     // @Valid annotations from spec constraints
    ))
}

// Result: generated OrderApi interface that your controller implements
// If you change the code to add a field not in the spec:
//   → spec-to-code drift: contract is stale
// If you change the spec to add a field not in the code:
//   → compilation error → spec is always the source of truth

// Generate client stubs for consumers:
// → Inventory Service uses generated OrderServiceClient
// → If Order Service changes its spec → regenerate → compilation errors in consumers
//    BEFORE runtime surprises
```

**Protocol Buffers contract (gRPC services):**

```protobuf
// order-service/src/main/proto/order.proto
syntax = "proto3";
package com.example.order;
option java_package = "com.example.order.grpc";

// Field numbers are the contract: NEVER change a field number (breaks binary compat)
// Field names can change (proto uses numbers for serialization, not names)
message Order {
  string order_id = 1;       // field number 1 = orderId
  string customer_id = 2;    // field number 2 = customerId
  OrderStatus status = 3;
  double total_amount = 4;
  google.protobuf.Timestamp created_at = 5;
  // Can add new fields with NEW numbers:
  repeated string item_ids = 6;  // backward compatible: old clients ignore field 6
  // NEVER: reuse field number of a deleted field (binary incompatibility)
}

enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;  // proto3: always have 0 value
  PENDING = 1;
  CONFIRMED = 2;
  SHIPPED = 3;
  DELIVERED = 4;
  CANCELLED = 5;
}

service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc CreateOrder (CreateOrderRequest) returns (Order);
  rpc ListOrders (ListOrdersRequest) returns (stream Order);  // server-side streaming
}
```

**Consumer-Driven Contract Testing with Pact:**

```java
// CONSUMER SIDE (InventoryService tests — defines what it needs from OrderService):
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "order-service")
class OrderServicePactConsumerTest {

    @Pact(consumer = "inventory-service")
    RequestResponsePact createOrderPact(PactDslWithProvider builder) {
        return builder
            .given("order 550e8400 exists and is CONFIRMED")
            .uponReceiving("GET /orders/550e8400 from inventory-service")
                .path("/orders/550e8400-e29b-41d4-a716-446655440000")
                .method("GET")
            .willRespondWith()
                .status(200)
                .body(new PactDslJsonBody()
                    .stringType("orderId")
                    .stringType("customerId")
                    .stringMatcher("status", "CONFIRMED|SHIPPED|DELIVERED", "CONFIRMED")
                    // InventoryService ONLY cares about: orderId, customerId, status
                    // It does NOT require: totalAmount, createdAt
                    // → consumer contract is minimal (tolerant reader pattern)
                )
            .toPact();
    }

    @Test
    @PactTestFor(pactMethod = "createOrderPact")
    void inventoryServiceCanReadOrderStatus(MockServer mockServer) {
        OrderServiceClient client = new OrderServiceClient(mockServer.getUrl());
        Order order = client.getOrder("550e8400-e29b-41d4-a716-446655440000");
        assertThat(order.getStatus()).isEqualTo("CONFIRMED");
    }
}
// Pact saves this consumer contract to: pact-files/inventory-service-order-service.json
// Uploaded to Pact Broker (shared contract registry)
```

```java
// PROVIDER SIDE (OrderService verifies it satisfies all consumer contracts):
@Provider("order-service")
@PactBroker(url = "https://pact-broker.company.com")
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class OrderServicePactProviderTest {

    @LocalServerPort int port;

    @BeforeEach
    void setUp(PactVerificationContext context) {
        context.setTarget(new HttpTestTarget("localhost", port));
    }

    @State("order 550e8400 exists and is CONFIRMED")
    void orderExistsAndIsConfirmed() {
        // Set up test data in H2:
        orderRepository.save(Order.builder()
            .orderId("550e8400-e29b-41d4-a716-446655440000")
            .customerId("customer-123")
            .status(OrderStatus.CONFIRMED)
            .totalAmount(new BigDecimal("149.99"))
            .build());
    }

    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void pactVerificationTestTemplate(PactVerificationContext context) {
        context.verifyInteraction();
    }
}
// This runs in OrderService CI pipeline:
// Downloads all consumer contracts from Pact Broker
// Verifies OrderService satisfies each one
// If OrderService renames "status" → "orderStatus":
//   → inventory-service pact fails: expected field "status" not present
//   → CI pipeline FAILS → breaking change caught BEFORE production
```

---

### ❓ Why Does This Exist (Why Before What)

In a distributed system, services call each other through network boundaries. Unlike a monolith (where a refactor fails at compile time), microservices fail at runtime when contracts break. A renamed field in Order Service causes Inventory Service to fail at runtime — potentially hours or days after deployment. Service contracts formalise the API surface, enable static analysis of breaking changes, and allow consumer-side testing to catch breakage before production.

---

### 🧠 Mental Model / Analogy

> A service contract is like a restaurant's published menu. The menu is the contract between the kitchen and the customers. A customer orders "Chicken Caesar Salad" expecting it to have chicken, romaine, croutons, and caesar dressing. If the kitchen removes croutons without updating the menu, customers complain. If the menu is updated (contract changed), customers know before ordering. Consumer-Driven Contracts are like customers saying: "I only care that there's chicken and dressing — I don't care about croutons." The kitchen validates: "We can always provide chicken and dressing — crouton changes don't break any customer."

---

### ⚙️ How It Works (Mechanism)

**Contract versioning strategy:**

```
URL versioning (simple, most common):
  /api/v1/orders/{id}  ← v1 contract (never changed)
  /api/v2/orders/{id}  ← v2 contract (new fields added)
  Run both simultaneously during transition
  Deprecate v1 after all consumers migrated to v2
  Set Sunset header: "Sunset: Sat, 31 Dec 2025 23:59:59 GMT"

Header versioning:
  GET /api/orders/{id}
  Accept: application/vnd.order-service.v2+json
  Less visible to developers but cleaner URLs

RULE: Major version bump ONLY for BREAKING changes:
  Breaking: removing a field, changing a field type, changing required field to error
  Non-breaking (same version): adding optional fields, adding new enum values (Postel's Law)
```

---

### 🔄 How It Connects (Mini-Map)

```
API Gateway
(routes requests to versioned service contracts)
        │
        ▼
Service Contract  ◄──── (you are here)
(formal API specification: OpenAPI/Proto/AsyncAPI)
        │
        ├── Consumer-Driven Contract Testing → consumers define what they need
        ├── Backward Compatibility → contract rules that prevent breakage
        └── Pact (Contract Testing) → tool that enforces consumer contracts
```

---

### 💻 Code Example

**Automated breaking change detection in CI:**

```bash
# Using openapi-diff to detect breaking changes between versions:
# In CI pipeline (before merging PR):

# Compare current branch spec vs main branch spec:
docker run --rm \
  -v $(pwd):/workspace \
  openapitools/openapi-diff:latest \
  /workspace/main/openapi.yaml \
  /workspace/feature-branch/openapi.yaml \
  --fail-on-incompatible    # Exit code 1 if breaking changes detected

# Breaking changes detected → CI fails:
# Changes in GET /orders/{orderId}:
#   - Response 200 Body
#     - Missing property: `totalAmount` (BREAKING)
#     - New property: `total` (NON-BREAKING if totalAmount still present)
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The implementation is the contract                        | The OpenAPI spec (or .proto file) is the contract, not the implementation. The implementation may have bugs. The spec is what consumers depend on for their code generation, mock servers, and test expectations                                                                         |
| Adding fields to a response is always backward compatible | Adding fields is backward compatible ONLY if consumers use a tolerant reader (ignore unknown fields). Strict JSON parsers that fail on unknown fields will break. Always document this assumption. For strongly-typed gRPC clients: adding proto fields IS safe (ignored by old clients) |
| Service contract testing is just integration testing      | Integration tests test the full stack against a real environment. Contract tests test that the provider satisfies the consumer's expectations in isolation — fast, cheap, runnable in CI without a full environment                                                                      |
| Consumer-Driven Contracts require Pact                    | CDC is a pattern; Pact is one tool. Spring Cloud Contract is another. The pattern: consumers express needs → provider verifies → both sides use the contract as the test oracle                                                                                                          |

---

### 🔥 Pitfalls in Production

**Implicit contracts — the unmapped fields that consumers depend on:**

```
SCENARIO:
  Order Service response has an undocumented field: "internalNotes" (debug info).
  It appears in all responses because the JPA entity is serialized directly.
  Notification Service developer notices it and uses it for customer communication.

  6 months later: Order Service removes direct entity serialization,
  uses a proper DTO. "internalNotes" disappears from responses.

  Notification Service: NullPointerException — field "internalNotes" is null.

  Root cause: the implicit contract (implementation leaked through API).
  The field was never in the OpenAPI spec (never intended for consumers).
  But it was used as if it were part of the contract.

PREVENTION:
  1. NEVER serialize JPA entities directly as API responses
     Always use DTOs (Response objects) that exactly match the OpenAPI spec

  2. OpenAPI spec validation (strict):
     Response body must exactly match spec — no extra fields allowed
     Use springdoc-openapi with response validation enabled

  3. Contract review process:
     Any new field added to a response DTO → OpenAPI spec must be updated first
     PR template: "Did you update the OpenAPI spec for API changes?"

  4. Periodic spec-implementation sync check:
     CI job: regenerate DTOs from spec, compare with committed DTOs
     Drift detected → build fails
```

---

### 🔗 Related Keywords

- `API Gateway` — routes requests to the versioned service; enforces contract at the boundary
- `Consumer-Driven Contract Testing` — pattern for deriving contracts from consumer needs
- `Backward Compatibility` — the property a contract must maintain across versions
- `Pact (Contract Testing)` — the primary tool for CDC in the JVM/Node.js ecosystem

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMATS      │ REST: OpenAPI YAML/JSON                   │
│              │ gRPC: Protocol Buffers .proto             │
│              │ Events: AsyncAPI + Avro/JSON Schema       │
├──────────────┼───────────────────────────────────────────┤
│ BREAKING     │ Remove field, change type, rename field   │
│ NON-BREAKING │ Add optional field, add enum value        │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ openapi-diff (breaking change detection)  │
│              │ Pact (consumer-driven contract testing)   │
│              │ Spectral (OpenAPI linting)                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 3 consumers of Order Service (Inventory, Payment, Notification). Using Pact, each has registered a consumer contract specifying different fields they need. Order Service v2 adds a new required request parameter: `?includeItems=true` is now required (returns 400 without it). Inventory and Payment already send this parameter. Notification does not. The Pact broker shows: Inventory ✅, Payment ✅, Notification ❌. Can you deploy Order Service v2? What is the correct process before you can deploy?

**Q2.** Your team practices "contract-first" development using OpenAPI. A new developer writes code first, then updates the OpenAPI spec to match. The spec reviewer approves. Tests pass. Production works. Why is this still considered a problem, even if no immediate breakage occurs? What specific class of bugs does it introduce, and how does "spec-first" tooling (like OpenAPI Generator with `interfaceOnly: true`) prevent them?
