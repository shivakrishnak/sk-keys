---
layout: default
title: "Backward Compatibility"
parent: "Microservices"
nav_order: 675
permalink: /microservices/backward-compatibility/
number: "675"
category: Microservices
difficulty: ★★★
depends_on: "Service Contract, Versioning Strategy"
used_by: "Pact (Contract Testing), API Gateway"
tags: #advanced, #microservices, #distributed, #architecture, #reliability
---

# 675 — Backward Compatibility

`#advanced` `#microservices` `#distributed` `#architecture` `#reliability`

⚡ TL;DR — **Backward Compatibility** means a new version of a service can be used by clients written against the old version without those clients needing to change. In microservices: a consumer calling Order Service v1 endpoints must continue to work when Order Service is updated to v2. Breaking backward compatibility causes downstream failures with no code change on the consumer's side.

| #675            | Category: Microservices               | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | Service Contract, Versioning Strategy |                 |
| **Used by:**    | Pact (Contract Testing), API Gateway  |                 |

---

### 📘 Textbook Definition

**Backward Compatibility** (also: backwards compatibility or downward compatibility) is the property of a system, API, or data format where a newer version continues to work correctly with clients, consumers, and data formats designed for an older version. In distributed systems and microservices, backward compatibility is critical because consumers cannot be updated atomically with providers — they are independently deployable services with independent release cycles. **Postel's Law** (Robustness Principle): "Be conservative in what you send, liberal in what you accept." A backward-compatible change to a REST API: adding an optional field to a response, adding a new optional request parameter, adding a new endpoint. A backward-incompatible (breaking) change: removing a field from a response, changing a field's type, making a previously optional request field required, changing status code semantics. In binary serialization formats (Protocol Buffers): backward compatibility is maintained by: never reusing field numbers, never removing required fields, always adding new fields as optional. In Apache Avro: the Schema Registry enforces that new schema versions are compatible with previous versions before they can be registered.

---

### 🟢 Simple Definition (Easy)

Backward compatible = old callers still work after you update. If you add a new field to your API response: old callers ignore it (they don't know about it). Safe. If you remove a field: old callers expecting it → fail. Not backward compatible. Rule of thumb: you can ADD to APIs freely. You cannot REMOVE or CHANGE without breaking callers.

---

### 🔵 Simple Definition (Elaborated)

Payment Service calls Order Service: expects `{orderId, status, totalAmount}`. You update Order Service to rename `totalAmount` to `total`. Payment Service: `response.getTotalAmount()` → null (field gone). Payment calculation wrong. Breaking change. Payment Service had zero code change. You broke them. Backward compatible version: keep `totalAmount` AND add `total`. Both fields present. Old callers use `totalAmount` (still there). New callers use `total`. Both work simultaneously. Eventually: when all callers are updated, deprecate `totalAmount`.

---

### 🔩 First Principles Explanation

**Classification: what changes are backward compatible vs breaking:**

```
REST API CHANGES:

BACKWARD COMPATIBLE (safe to deploy any time):
  ✅ Add a new optional field to response body
     Old clients: use tolerant reader pattern, ignore unknown fields
  ✅ Add a new optional request parameter (with a sensible default)
     Old clients: don't send it → default value applies
  ✅ Add a new endpoint
     Old clients: don't call it
  ✅ Add a new enum VALUE to a response field
     ⚠️ EXCEPTION: old clients with strict enum parsing WILL fail
        "Tolerant reader" clients (Jackson with FAIL_ON_UNKNOWN_PROPERTIES=false) are safe
        Strict clients: break
  ✅ Relax validation rules (accept more input)
     Old clients: their valid inputs still valid

BREAKING CHANGES (require version bump, deprecation, migration):
  ❌ Remove a response field
     Old clients: expect it, NPE or incorrect behavior
  ❌ Rename a response field
     Old clients: expect old name, new name is "unknown" (NPE or ignored)
  ❌ Change a field's type (string → int, decimal → string)
     Old clients: type mismatch exception
  ❌ Make an optional request field required
     Old clients: don't send it → 400 Bad Request
  ❌ Change endpoint URL or HTTP method
     Old clients: 404 Not Found
  ❌ Change error response format
     Old clients: error handling code breaks
  ❌ Change status code semantics (200 → 201 for create, or 404 behavior)
  ❌ Remove an endpoint
     Old clients: 404 Not Found

PROTOBUF SPECIFIC:
  ✅ Add a new field with a new field number (ignored by old clients)
  ✅ Add a new RPC method (ignored by old clients who don't call it)
  ❌ Change a field's type (even with same field number)
  ❌ Reuse a field number (even after deleting the old field)
     → binary incompatibility with old messages using that number
  ❌ Change a field from optional to required
     proto3 note: all fields are optional in proto3 (required is removed)
                  proto3 was designed to be more backward-compatible than proto2
```

**Jackson configuration: tolerant reader for REST clients:**

```java
// PROVIDER SIDE: configure serialization to not fail on unknown/extra fields:
@Bean
ObjectMapper objectMapper() {
    return new ObjectMapper()
        .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false)
        // PROVIDER: do NOT include null fields in response (reduces payload size)
        .setSerializationInclusion(JsonInclude.Include.NON_NULL)
        .registerModule(new JavaTimeModule());
}

// CONSUMER SIDE: tolerant reader — ignore fields we don't know about:
// (This is THE key configuration for backward compatibility on the consumer side)
@Bean
ObjectMapper objectMapper() {
    return new ObjectMapper()
        // CRITICAL for backward compat: unknown fields in response → ignore (don't fail)
        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
        // Enum values we don't recognize → null (don't fail):
        .configure(DeserializationFeature.READ_UNKNOWN_ENUM_VALUES_AS_NULL, true)
        // Missing fields → use default (null/0/false) rather than failing:
        .configure(DeserializationFeature.FAIL_ON_NULL_FOR_PRIMITIVES, false)
        .registerModule(new JavaTimeModule());
}
// With these settings: consumer can handle API additions without code changes
// This is "tolerant reader" — the consumer is lenient about what it accepts
```

**Dual-write strategy: maintaining backward compatibility during field migration:**

```java
// SCENARIO: Renaming "totalAmount" to "total" in Order response
// STEP 1: Add "total" alongside "totalAmount" (both present in response)

@Data
@Builder
public class OrderResponse {
    private String orderId;
    private String customerId;
    private OrderStatus status;

    @Deprecated  // Mark as deprecated to signal migration needed
    private BigDecimal totalAmount;  // OLD field: kept for backward compat

    private BigDecimal total;        // NEW field: consumers should switch to this

    // Both fields contain the same value during transition period
}

@Service
class OrderResponseMapper {
    OrderResponse toResponse(Order order) {
        BigDecimal amount = order.getTotalAmount();
        return OrderResponse.builder()
            .orderId(order.getId().toString())
            .customerId(order.getCustomerId().toString())
            .status(order.getStatus())
            .totalAmount(amount)  // backward compat: old consumers still work
            .total(amount)        // new field: new consumers use this
            .build();
    }
}

// Response JSON during transition:
// {
//   "orderId": "550e8400-...",
//   "customerId": "customer-123",
//   "status": "CONFIRMED",
//   "totalAmount": 149.99,    ← old consumers use this
//   "total": 149.99           ← new consumers use this
// }

// STEP 2: After all consumers updated to use "total":
// Deprecation notice: set "Sunset" header on old field
// STEP 3: Remove "totalAmount" from response DTO
```

**Avro Schema Registry — enforced backward compatibility for Kafka events:**

```java
// Avro schema v1 (UserRegisteredEvent):
// {
//   "type": "record", "name": "UserRegisteredEvent",
//   "fields": [
//     {"name": "userId", "type": "string"},
//     {"name": "email", "type": "string"},
//     {"name": "registeredAt", "type": "long", "logicalType": "timestamp-millis"}
//   ]
// }

// Avro schema v2 (adding optional "referralCode" field):
// {
//   "type": "record", "name": "UserRegisteredEvent",
//   "fields": [
//     {"name": "userId", "type": "string"},
//     {"name": "email", "type": "string"},
//     {"name": "registeredAt", "type": "long", "logicalType": "timestamp-millis"},
//     {"name": "referralCode", "type": ["null", "string"], "default": null}
//     ^^ BACKWARD COMPATIBLE: new field with null default
//     Old consumers reading v2 messages: ignore referralCode
//     New consumers reading v1 messages: referralCode = null (default)
//   ]
// }

// Confluent Schema Registry enforces compatibility before registration:
// curl -X POST http://schema-registry:8081/subjects/user-registered-value/versions \
//   -H "Content-Type: application/vnd.schemaregistry.v1+json" \
//   -d '{"schema": "...", "schemaType": "AVRO"}'
// → If new schema breaks backward compat: HTTP 409 Conflict
//   "Schema being registered is incompatible with an earlier schema"
// This prevents incompatible schema changes from reaching Kafka producers
```

---

### ❓ Why Does This Exist (Why Before What)

In a monolith, all code is deployed together — breaking changes are caught at compile time and deployed atomically. In microservices, services have independent deployment cycles and different teams. Service A can't force Service B to update simultaneously. If Service A breaks its API, Service B fails at runtime — during Service A's deployment. Backward compatibility is the constraint that allows independent deployability to work safely.

---

### 🧠 Mental Model / Analogy

> Backward compatibility is like publishing a book and promising: "everything in Chapter 3 will always be there." Readers (consumers) cite your Chapter 3. If you publish a new edition, you can ADD new chapters (new features). You can ADD more content to Chapter 3. But if you remove a section from Chapter 3, everyone who cited it has a broken reference. The Expand-Contract pattern is: publish a new edition with the old section AND the new section → when all readers update their citations → remove the old section in the next edition.

---

### ⚙️ How It Works (Mechanism)

**Versioning policy enforcement with deprecation headers:**

```java
// REST controller: support both v1 and v2 simultaneously
@RestController
@RequestMapping("/api")
class OrderController {

    @GetMapping("/v1/orders/{orderId}")
    @Deprecated
    ResponseEntity<OrderResponseV1> getOrderV1(@PathVariable String orderId) {
        Order order = orderService.getOrder(UUID.fromString(orderId));
        return ResponseEntity.ok()
            .header("Deprecation", "true")
            .header("Sunset", "Sat, 31 Dec 2025 23:59:59 GMT")
            .header("Link", "</api/v2/orders/" + orderId + ">; rel=\"successor-version\"")
            .body(orderMapperV1.toV1Response(order));
            // V1 response: uses "totalAmount" field (old name)
    }

    @GetMapping("/v2/orders/{orderId}")
    ResponseEntity<OrderResponseV2> getOrderV2(@PathVariable String orderId) {
        Order order = orderService.getOrder(UUID.fromString(orderId));
        return ResponseEntity.ok()
            .body(orderMapperV2.toV2Response(order));
            // V2 response: uses "total" field (new name), adds "itemCount"
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Service Contract
(defines what fields/endpoints are promised)
        │
        ▼
Backward Compatibility  ◄──── (you are here)
(the constraint: old consumers must still work)
        │
        ├── Versioning Strategy → how to manage breaking changes over time
        ├── Pact (Contract Testing) → verifies backward compat with each consumer
        └── API Gateway → routes v1/v2 to allow version transition period
```

---

### 💻 Code Example

**Automated backward compatibility check for Protobuf schemas in CI:**

```bash
# buf tool: lint and breaking change detection for .proto files
# buf.yaml:
# version: v1
# breaking:
#   use:
#     - FILE  # Check backward compat at FILE level (not WIRE_JSON level)

# In CI pipeline (on every PR):
buf breaking --against '.git#branch=main'
# Checks: does this PR introduce any breaking changes to .proto files vs main?
# Breaking changes detected:
#   --
#   proto/order/v1/order.proto:12:3:Field "1" with name "order_id" on message "Order" changed
#   type from "string" to "int64".
#   --
# Exit code 1 → CI fails → breaking change blocked from merging
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Adding a new enum value is always backward compatible        | Only if consumers use tolerant enum parsing. Jackson's `READ_UNKNOWN_ENUM_VALUES_AS_NULL` is needed. Strict enum parsers (generated code without this config) fail on unknown values. Always document whether your enum is "open" (more values may be added) or "closed" (exhaustive)           |
| If I version my API (v1, v2), backward compat doesn't matter | Versioning helps manage breaking changes, but during the transition both versions run simultaneously. The provider must maintain both. Backward compat within a version still matters: you can't break v1 by changing what v1 returns                                                           |
| Backward compatible means forward compatible                 | Backward compat: new server works with old clients. Forward compat: old server works with new clients. These are different. A client sending a new optional field to an old server that rejects unknown fields → forward incompatibility. Proto3 and tolerant-reader REST are designed for both |
| Protobuf is automatically backward compatible                | Proto3 makes backward compat easier (all fields optional, unknown fields ignored). But you can still break: reusing field numbers, changing field types, removing fields that producers write. The `.proto` file is still a contract                                                            |

---

### 🔥 Pitfalls in Production

**Silent data corruption from "backward compatible" type changes:**

```
SCENARIO:
  Order total previously stored as: "totalAmount": 149.99 (JSON number/float)
  Developer changes: store as string for "precision": "totalAmount": "149.99"

  This is considered "backward compatible" because:
    "Old consumers still get a totalAmount field" ✓

  REALITY:
    Old consumers deserialize to double/BigDecimal from JSON number
    New response sends totalAmount as JSON string "149.99"
    Jackson (strict): NumberFormatException — expected NUMBER but got STRING
    Jackson (lenient): deserializes "149.99" string as... nothing (ignored)
    Payment calculation: totalAmount = null → NullPointerException → 500

  TYPE CHANGE IS ALWAYS BREAKING — even if both represent "the same value."
  JSON number vs JSON string are different types. Consumers have type-specific parsing.

CORRECT FIX:
  Keep "totalAmount": 149.99 (float) — backward compat maintained
  Add new field "totalAmountStr": "149.99" (string) — for high-precision consumers
  Document: "totalAmount is float representation; use totalAmountStr for exact decimal"

  OR: use consistent representation from day one:
  - Never use float/double for money. Always use string or integer (cents).
  - "totalAmountCents": 14999 (integer cents) — no precision issues, type is clear
```

---

### 🔗 Related Keywords

- `Service Contract` — defines the formal API surface that backward compat protects
- `Versioning Strategy` — how breaking changes are managed (v1, v2 endpoints)
- `Pact (Contract Testing)` — verifies that the provider satisfies consumer contracts
- `API Gateway` — mediates version routing, can enforce deprecation policies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SAFE CHANGES │ Add optional fields, add endpoints,       │
│              │ relax validation, add enum values*        │
│ BREAKING     │ Remove/rename fields, change types,       │
│              │ make optional required, change URLs       │
├──────────────┼───────────────────────────────────────────┤
│ JACKSON CFG  │ FAIL_ON_UNKNOWN_PROPERTIES=false (consumer)│
│              │ READ_UNKNOWN_ENUM_VALUES_AS_NULL (consumer)│
├──────────────┼───────────────────────────────────────────┤
│ MIGRATION    │ Dual-write (old + new field) during trans  │
│              │ Deprecation: Deprecation + Sunset headers  │
│ * CAUTION    │ Enum values: safe only with tolerant reader│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer argues: "We use Avro with the Schema Registry set to BACKWARD compatibility mode, so we can never break our consumers." Is this statement accurate? Describe a scenario where a schema change passes the Schema Registry's BACKWARD compatibility check but still breaks a consumer at runtime. What does BACKWARD compatibility mode in Avro actually guarantee, and what does it NOT guarantee?

**Q2.** Your team is migrating a field from `decimal` (e.g., `"price": 29.99` as a JSON float) to a string representation (e.g., `"price": "29.99"` as a JSON string) to avoid floating-point precision errors. Consumers include: iOS app, Android app, 3 internal microservices, and a legacy Java batch job. Design the migration plan: what do you expose during the transition, what Jackson/Codable configurations are needed on consumer side, and what is the minimum transition period before the old float format can be removed? How do you verify all consumers have migrated?
