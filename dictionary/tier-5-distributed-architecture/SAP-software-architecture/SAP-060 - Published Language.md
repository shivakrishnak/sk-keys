---
id: SAP-080
title: Published Language
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-073, SAP-071
used_by: SAP-073
related: SAP-071, SAP-073
tags:
  - architecture
  - ddd
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 60
permalink: /software-architecture/published-language/
  - advanced
  - strategic
---

# SAP-074 - Published Language

⚡ TL;DR - A Published Language is a well-documented, versioned data exchange format that enables Bounded Contexts to communicate without sharing internal domain models - it is the lingua franca at context boundaries.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | SAP-073, SAP-071 |
| **Used by**    | SAP-073          |
| **Related**    | SAP-071, SAP-073 |

---

### 🔥 The Problem This Solves

**THE COMMON LANGUAGE PROBLEM:**
Two microservices need to exchange order data. Service A uses `Order.customerId: UUID`. Service B calls the same field `Order.clientId: String`. Without a common exchange format, every integration requires mapping code. As integrations multiply, the mapping logic becomes a maintenance nightmare.

**THE PUBLISHED LANGUAGE SOLUTION:**
Define a formal, shared exchange language: a documented schema with agreed names, types, and semantics. Both services translate their internal models to and from this language. The Published Language is the neutral ground - neither service's internal model, but a documented contract that both can implement against.

**EVOLUTION:**
Eric Evans introduced Published Language in "Domain-Driven Design" (2003) as the companion to Open Host Service - OHS defines the service interface, PL defines the exchange format. The concept predates DDD in EDI (Electronic Data Interchange) formats from the 1970s-80s. WSDL and XML Schema (2001) were the first formal PL tooling for web services. JSON Schema (2007) and OpenAPI (2011) replaced them for REST. Apache Avro and Protocol Buffers brought schema evolution capabilities. Confluent Schema Registry (2015) made Published Language for Kafka events a first-class infrastructure concern - every event's schema is versioned, stored, and enforced centrally.

---

### 📘 Textbook Definition

A Published Language, as described by Eric Evans in "Domain-Driven Design," is a well-documented shared language that can be used as a common medium of communication. When two Bounded Contexts use a Published Language to communicate, each translates its own domain model to and from the published format. Unlike a Shared Kernel (which shares actual code), a Published Language shares only a documented schema or protocol specification. The specification is published - that is, stable, accessible, and versioned - so that any team can implement it independently without requiring access to the other team's codebase.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A documented exchange format at context boundaries - neither side's internal model, but a stable common language both can implement.

**One analogy:**

> International trade uses standardized shipping container specifications and Incoterms (trade term definitions). German and Japanese companies with completely different internal logistics processes can trade because they share these published standards. Neither company exposes their internal systems - they both implement the published standard at the boundary.

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

Integration broken. Fix requires changing one service to match the other's format - creating coupling.

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

> Published Language is HTML/HTTP. Web servers and browsers are developed by thousands of companies with completely different internal architectures. They interoperate because they all implement the same published standards (HTTP/1.1 RFC, HTML spec). Neither Firefox's code nor Apache's code is the standard - the standard is a published document that both implement. This is exactly what Published Language does at domain boundaries.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
An agreed format for how two systems talk to each other - written down so both sides can implement it independently.

**Level 2 - How to define one (junior):**
Write an OpenAPI spec for your REST API, or Avro schemas for your Kafka events. Name fields clearly using business vocabulary. Document what each field means (not just the type). Register schemas in a schema registry (Confluent, AWS Glue). Version the schema (v1, v2).

**Level 3 - Schema evolution (mid-level):**
Schema evolution rules for backward compatibility: 1) Adding optional fields is backward compatible (old consumers ignore new fields). 2) Removing fields is breaking (consumers expecting the field will fail). 3) Renaming fields is breaking. 4) Changing field types is breaking. Managing evolution: use Avro's backward/forward compatibility settings in schema registry; support multiple versions with a deprecation window; use upcasters for event-sourced systems to translate old event versions.

**Level 4 - Industry standards (senior/staff):**
Many domains already have Published Languages: FHIR for healthcare data exchange, FIX protocol for financial trading, EDI/EDIFACT for logistics, JSON-LD for linked data. When an industry standard exists, use it - your system becomes interoperable with the ecosystem. When no standard exists, you create one for your organization. The creation of a Published Language is a governance activity: who owns it, who can propose changes, what's the approval process, what's the deprecation timeline? A Published Language without governance degrades into an undocumented internal API.

---

### ⚙️ How It Works (Mechanism)

**Published Language with Schema Registry:**

```
┌──────────────────────────────────────────────────────────┐
│      PUBLISHED LANGUAGE - KAFKA + SCHEMA REGISTRY       │
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
│         PUBLISHED LANGUAGE - FULL FLOW                   │
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
│  Both services INDEPENDENT - connected only via schema   │
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
| Published Language = internal domain model exposed | PL is a translation target, not the internal model - each side may need to translate                         |
| OpenAPI spec = Published Language                  | OpenAPI is a tool for expressing a PL; the PL is the business-meaningful schema, not just the technical spec |
| Published Language never changes                   | It evolves, but responsibly - with versioning, backward compatibility, and deprecation windows               |
| Only needed for external APIs                      | Published Language is valuable for internal service-to-service communication too                             |

---

### 🚨 Failure Modes & Diagnosis

**Schema Drift - producer and consumer out of sync**

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

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Systems that must exchange data long-term need a common language that is independent of either system's internal representation. The common language must be versioned, documented, and stable; it is the contract both sides depend on.

**Where else this pattern appears:**

- **Legal contract language:** Legal documents use a precise, formally defined vocabulary ("hereinafter," "consideration," "force majeure") that is independent of either party's internal terminology. Both parties translate their intent into this neutral legal language.
- **Musical notation:** Sheet music is a Published Language for music - a formal, agreed-upon notation that any trained musician (any system) can read and perform. The composer's internal mental model and the performer's interpretation are both separate from the notation.
- **GeoJSON/GPX formats:** Geographic data exchange formats define a Published Language for location data. Navigation apps, mapping services, and GPS devices all speak GeoJSON, regardless of their internal data structures.

---

### 💡 The Surprising Truth

The hardest part of a Published Language is NOT the initial design - it is versioning over time. A Published Language that can never be changed is often too rigid; one that changes frequently breaks all consumers. The practical solution is additive versioning: new fields can always be added (consumers ignore unknown fields), but no existing fields can be removed or renamed without a major version increment with deprecation period. This is the same evolution strategy used by JSON-LD, Protocol Buffers, and Avro - and it requires establishing the versioning rules BEFORE the first consumer integrates, not after breaking changes have already occurred.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-073 - Open Host Service (the OHS publishes a language; understanding OHS explains the context in which Published Language is defined and maintained)
- SAP-071 - Context Map (the Context Map shows which contexts are connected by Published Language relationships; understanding Context Map provides the strategic picture)

**Builds On This (learn these next):**

- SAP-073 - Open Host Service (complementary; OHS is the service boundary, Published Language is the exchange format; they are designed together)
- SAP-071 - Context Map (the Context Map shows where Published Language relationships exist; completing the strategic DDD picture)

**Alternatives / Comparisons:**

- SAP-072 - Shared Kernel (alternative exchange approach: share code rather than define a neutral language; lower translation overhead but higher coupling)
- Domain-specific schema languages (OpenAPI, Avro, Protobuf - tools for defining Published Language formally; not alternatives but implementation mechanisms)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Formal, documented, versioned exchange    │
│              │ schema at context boundaries              │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Neither side's internal model - neutral   │
│              │ schema both translate to/from             │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ OpenAPI, Avro, Protobuf, Schema Registry  │
├──────────────┼───────────────────────────────────────────┤
│ BREAKING CHG │ Requires version bump + deprecation plan  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The trade standard: neither side's       │
│              │  internal system - common at the border"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing the Published Language for an `OrderPlaced` event. The event needs to carry product information (product IDs, names, quantities). Should the Published Language include the full product name and description, or just the product ID? What are the implications of each choice for consumers who need to display order details to customers?

_Hint:_ Research the "fat event" vs "thin event" design choice - specifically the trade-off between self-contained events (include all data consumers might need - fat) and reference events (include only IDs, consumers look up data - thin). Fat events: consumers don't need extra API calls but the event payload grows and may contain stale data. Thin events: smaller payloads but consumers must call the product service to get names, creating a dependency. Research the "event-carried state transfer" pattern as a middle ground.

**Q2.** Your event's Published Language uses `totalAmountPence: long` (amount in pence/cents). A new requirement needs to support Japanese Yen (no fractional currency) and Kuwaiti Dinar (3 decimal places). The current schema only supports 2-decimal currencies. Designing a backward-compatible evolution of this schema - what changes, what stays, and how do you handle existing events with the old format?

_Hint:_ Research how financial message standards (ISO 20022, FIX Protocol) handle multi-currency amount representation - specifically the pattern of `{ amount: long, currencyCode: string, minorUnit: int }` where `minorUnit` specifies the number of decimal places for the currency (2 for USD/EUR, 0 for JPY, 3 for KWD). The evolution: add `currencyCode` and `minorUnit` fields alongside `totalAmountPence`. Old events default `currencyCode` to the original currency and `minorUnit` to 2. New events populate all three fields.

**Q3.** Three teams must share a Published Language for product catalog data. Team A owns the OHS and wants to use Avro (binary, schema-enforced). Team B prefers JSON (human-readable, widely supported). Team C wants Protobuf (performance-focused). The three teams cannot agree on the serialization format. How do you resolve this technical and political disagreement, and what principle should guide the choice?

_Hint:_ Research the "upstream/downstream" power dynamic in OHS - the team publishing the OHS (Team A) decides the Published Language format; consuming teams (Teams B and C) use ACLs to translate the Published Language into their preferred internal format. The OHS provider should choose the format that is best for their production needs (Avro with Schema Registry for event streaming makes sense). Consumers use ACLs - not to avoid the OHS, but to translate its format into their internal representation. Research Apache Kafka Connect's converters as infrastructure that performs this translation transparently.
