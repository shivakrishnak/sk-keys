---
layout: default
title: "Published Language"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /software-architecture/published-language/
id: SAP-038
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Bounded Context, Open Host Service, Context Map, Domain Events
used_by: API design, Microservices, Event-driven architectures, DDD
related: Open Host Service, Bounded Context, Context Map, Schema Registry, API Versioning
tags:
  - architecture
  - ddd
  - pattern
  - deep-dive
  - advanced
  - strategic
---

# SAP-038 — Published Language

⚡ TL;DR — A Published Language is a well-documented, versioned data exchange format that enables Bounded Contexts to communicate without sharing internal domain models — it is the lingua franca at context boundaries.

---

### 📊 Entry Metadata

| #751            | Category: Software Architecture Patterns                                         | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Open Host Service, Context Map, Domain Events                   |                 |
| **Used by:**    | API design, Microservices, Event-driven architectures, DDD                       |                 |
| **Related:**    | Open Host Service, Bounded Context, Context Map, Schema Registry, API Versioning |                 |

---

### 🔥 The Problem This Solves

**THE COMMON LANGUAGE PROBLEM:**
Two microservices need to exchange order data. Service A uses `Order.customerId: UUID`. Service B calls the same field `Order.clientId: String`. Without a common exchange format, every integration requires mapping code. As integrations multiply, the mapping logic becomes a maintenance nightmare.

**THE PUBLISHED LANGUAGE SOLUTION:**
Define a formal, shared exchange language: a documented schema with agreed names, types, and semantics. Both services translate their internal models to and from this language. The Published Language is the neutral ground — neither service's internal model, but a documented contract that both can implement against.

---

### 📘 Textbook Definition

A Published Language, as described by Eric Evans in "Domain-Driven Design," is a well-documented shared language that can be used as a common medium of communication. When two Bounded Contexts use a Published Language to communicate, each translates its own domain model to and from the published format. Unlike a Shared Kernel (which shares actual code), a Published Language shares only a documented schema or protocol specification. The specification is published — that is, stable, accessible, and versioned — so that any team can implement it independently without requiring access to the other team's codebase.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A documented exchange format at context boundaries — neither side's internal model, but a stable common language both can implement.

**One analogy:**

> International trade uses standardized shipping container specifications and Incoterms (trade term definitions). German and Japanese companies with completely different internal logistics processes can trade because they share these published standards. Neither company exposes their internal systems — they both implement the published standard at the boundary.

**One insight:**
Published Language decouples the schema from the implementation. Two services can have completely different internal models as long as both can produce and consume the Published Language. This is the key to independent evolution: change your internal model freely as long as you maintain the Published Language contract.

---

### 🔩 First Principles Explanation

**PUBLISHED LANGUAGE PROPERTIES:**

```
┌──────────────────────────────────────────────────────────┐
│           PUBLISHED LANGUAGE PROPERTIES                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ✅ Documented:                                          │
│     Formal schema: OpenAPI, Avro, Protobuf, JSON Schema  │
│     Field meanings explained, not just field names       │
│                                                          │
│  ✅ Versioned:                                           │
│     Breaking changes → new version                       │
│     Both old and new versions supported during migration │
│                                                          │
│  ✅ Neutral:                                             │
│     Neither context's internal model directly            │
│     Translation on both sides if needed                  │
│                                                          │
│  ✅ Stable:                                              │
│     High bar for changes; consumers can rely on it       │
│     Deprecation policy for removing old elements         │
│                                                          │
│  ✅ Self-describing:                                     │
│     Schema registered in a schema registry               │
│     Consumer can validate received data against schema   │
└──────────────────────────────────────────────────────────┘
```

**PUBLISHED LANGUAGE EXAMPLES:**

```
┌──────────────────────────────────────────────────────────┐
│         PUBLISHED LANGUAGE IN PRACTICE                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  REST APIs:                                              │
│    OpenAPI 3.0 spec = Published Language                 │
│    JSON request/response schemas are the Published       │
│    Language of the HTTP API                              │
│                                                          │
│  Kafka events:                                           │
│    Avro schemas in Confluent Schema Registry             │
│    Each event topic has a published schema               │
│    Producers and consumers both use the schema           │
│                                                          │
│  gRPC:                                                   │
│    .proto files = Published Language                     │
│    Generated stubs implement the Published Language      │
│                                                          │
│  Industry standards:                                     │
│    FHIR (healthcare), FIX (finance), EDIFACT (trade)     │
│    Pre-existing industry Published Languages             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**WITHOUT PUBLISHED LANGUAGE:**
Order service sends to Billing service:

```json
{ "orderId": "abc-123", "amount": 99.99, "cur": "GBP" }
```

Billing service expects:

```json
{ "order_id": "abc-123", "total": 99.99, "currency": "GBP" }
```

Integration broken. Fix requires changing one service to match the other's format — creating coupling.

**WITH PUBLISHED LANGUAGE:**
Both teams agree on the Published Language schema:

```json
{
  "orderId": "string (UUID)",
  "totalAmount": "number (decimal, 2dp)",
  "currency": "string (ISO 4217 code)"
}
```

Order service translates its internal `Order.id` and `Order.total` to this schema. Billing service translates this schema to its internal `Invoice.orderReference` and `Invoice.amount`. Both work independently. Neither knows the other's internal field names.

---

### 🧠 Mental Model / Analogy

> Published Language is HTML/HTTP. Web servers and browsers are developed by thousands of companies with completely different internal architectures. They interoperate because they all implement the same published standards (HTTP/1.1 RFC, HTML spec). Neither Firefox's code nor Apache's code is the standard — the standard is a published document that both implement. This is exactly what Published Language does at domain boundaries.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
An agreed format for how two systems talk to each other — written down so both sides can implement it independently.

**Level 2 — How to define one (junior):**
Write an OpenAPI spec for your REST API, or Avro schemas for your Kafka events. Name fields clearly using business vocabulary. Document what each field means (not just the type). Register schemas in a schema registry (Confluent, AWS Glue). Version the schema (v1, v2).

**Level 3 — Schema evolution (mid-level):**
Schema evolution rules for backward compatibility: 1) Adding optional fields is backward compatible (old consumers ignore new fields). 2) Removing fields is breaking (consumers expecting the field will fail). 3) Renaming fields is breaking. 4) Changing field types is breaking. Managing evolution: use Avro's backward/forward compatibility settings in schema registry; support multiple versions with a deprecation window; use upcasters for event-sourced systems to translate old event versions.

**Level 4 — Industry standards (senior/staff):**
Many domains already have Published Languages: FHIR for healthcare data exchange, FIX protocol for financial trading, EDI/EDIFACT for logistics, JSON-LD for linked data. When an industry standard exists, use it — your system becomes interoperable with the ecosystem. When no standard exists, you create one for your organization. The creation of a Published Language is a governance activity: who owns it, who can propose changes, what's the approval process, what's the deprecation timeline? A Published Language without governance degrades into an undocumented internal API.

---

### ⚙️ How It Works (Mechanism)

**Published Language with Schema Registry:**

```
┌──────────────────────────────────────────────────────────┐
│      PUBLISHED LANGUAGE — KAFKA + SCHEMA REGISTRY       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Schema Registry:                                        │
│    Stores all registered schemas                         │
│    Each schema has ID + version                          │
│    Enforces compatibility rules                          │
│                                                          │
│  Producer (Order Service):                               │
│    1. Register OrderPlaced v1 Avro schema                │
│    2. Serialize event using schema (schema ID in header) │
│    3. Publish to topic: orders.order-placed              │
│                                                          │
│  Consumer (Billing Service):                             │
│    1. Receive message from topic                         │
│    2. Read schema ID from message header                 │
│    3. Fetch schema from registry                         │
│    4. Deserialize using schema                           │
│    5. Translate Published Language → internal model      │
│       via ACL or directly if Conformist                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│         PUBLISHED LANGUAGE — FULL FLOW                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Order Service                                           │
│    Internal: Order(id=OrderId, total=Money)              │
│         ↓ TRANSLATE TO Published Language               │
│    Published: { orderId: "...", totalAmount: 99.99,      │
│                  currency: "GBP" }                       │
│         ↓ SEND via REST or Kafka                         │
│                                                          │
│  ------ Schema Registry validates against schema ------  │
│                                                          │
│    Published: { orderId: "...", totalAmount: 99.99,      │
│                  currency: "GBP" }                       │
│         ↓ TRANSLATE FROM Published Language             │
│  Billing Service                                         │
│    Internal: Invoice(orderRef=String, amount=BigDecimal) │
│                                                          │
│  Both services INDEPENDENT — connected only via schema   │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Avro schema as Published Language:**

```json
// File: schemas/order-placed-v1.avsc
// Registered in Schema Registry
{
  "namespace": "com.acme.orders.events.v1",
  "type": "record",
  "name": "OrderPlaced",
  "doc": "Raised when a customer places an order",
  "fields": [
    {
      "name": "orderId",
      "type": "string",
      "doc": "UUID of the order"
    },
    {
      "name": "customerId",
      "type": "string",
      "doc": "UUID of the customer"
    },
    {
      "name": "totalAmountPence",
      "type": "long",
      "doc": "Total amount in smallest currency unit (pence)"
    },
    {
      "name": "currencyCode",
      "type": "string",
      "doc": "ISO 4217 currency code (e.g. GBP, USD)"
    },
    {
      "name": "placedAt",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "doc": "UTC timestamp when order was placed"
    }
  ]
}
```

**Producer using Published Language:**

```java
// Order service: translate internal model to Published Language
@Component
@RequiredArgsConstructor
public class OrderEventPublisher {

    private final KafkaTemplate<String, OrderPlaced>
        kafkaTemplate;
    private final SchemaRegistryClient schemaRegistry;

    // Translates domain event → Published Language event
    public void publish(OrderPlacedDomainEvent event) {
        // Map: domain types → Published Language types
        OrderPlaced publishedEvent = OrderPlaced.newBuilder()
            .setOrderId(event.orderId().value().toString())
            .setCustomerId(
                event.customerId().value().toString())
            .setTotalAmountPence(
                event.total().amountInMinorUnits())
            .setCurrencyCode(
                event.total().currency().isoCode())
            .setPlacedAt(
                event.placedAt().toEpochMilli())
            .build();

        kafkaTemplate.send("orders.order-placed",
                            publishedEvent.getOrderId(),
                            publishedEvent);
    }
}
```

---

### ⚖️ Comparison Table

| Approach               | Documentation       | Stability          | Independence | Best For                    |
| ---------------------- | ------------------- | ------------------ | ------------ | --------------------------- |
| **Published Language** | Formal schema       | High (governed)    | High         | Multi-consumer integration  |
| Shared Kernel          | Code (shared types) | High (coordinated) | Medium       | Closely collaborating teams |
| Ad-hoc JSON            | None / informal     | Low                | Low          | Small, stable integrations  |
| Direct RPC             | Interface code      | Medium             | Low          | Tight service coupling      |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                      |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Published Language = internal domain model exposed | PL is a translation target, not the internal model — each side may need to translate                         |
| OpenAPI spec = Published Language                  | OpenAPI is a tool for expressing a PL; the PL is the business-meaningful schema, not just the technical spec |
| Published Language never changes                   | It evolves, but responsibly — with versioning, backward compatibility, and deprecation windows               |
| Only needed for external APIs                      | Published Language is valuable for internal service-to-service communication too                             |

---

### 🚨 Failure Modes & Diagnosis

**Schema Drift — producer and consumer out of sync**

**Symptom:** Consumer fails to deserialize messages. Unknown fields cause errors. Required fields missing.

**Root Cause:** Producer changed the schema without updating the schema registry or notifying consumers.

**Fix:** Use schema registry with compatibility enforcement. Confluent Schema Registry compatibility modes: BACKWARD (new schema can read old data), FORWARD (old schema can read new data), FULL (both).

**Diagnostic:**

```bash
# Check schema compatibility before publishing new schema
curl -X POST \
  "http://schema-registry:8081/compatibility/subjects/\
  orders.order-placed-value/versions/latest" \
  -H "Content-Type: application/json" \
  -d '{"schema": "<new_schema_json>"}'
# Response: {"is_compatible": true/false}
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `Open Host Service` — OHS publishes a language
- `Bounded Context` — contexts use Published Language to communicate

**Related:**

- `Context Map` — shows Published Language relationships
- `Schema Registry` — tool for managing Published Language schemas
- `API Versioning` — the versioning practice for Published Languages

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Formal, documented, versioned exchange    │
│              │ schema at context boundaries              │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Neither side's internal model — neutral   │
│              │ schema both translate to/from             │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ OpenAPI, Avro, Protobuf, Schema Registry  │
├──────────────┼───────────────────────────────────────────┤
│ BREAKING CHG │ Requires version bump + deprecation plan  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The trade standard: neither side's       │
│              │  internal system — common at the border"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing the Published Language for an `OrderPlaced` event. The event needs to carry product information (product IDs, names, quantities). Should the Published Language include the full product name and description, or just the product ID? What are the implications of each choice for consumers who need to display order details to customers?

**Q2.** Your event's Published Language uses `totalAmountPence: long` (amount in pence/cents). A new requirement needs to support Japanese Yen (no fractional currency) and Kuwaiti Dinar (3 decimal places). The current schema only supports 2-decimal currencies. Designing a backward-compatible evolution of this schema — what changes, what stays, and how do you handle existing events with the old format?
