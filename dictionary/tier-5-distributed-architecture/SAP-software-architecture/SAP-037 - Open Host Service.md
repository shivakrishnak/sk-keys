---
id: SAP-037
title: Open Host Service
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-035, SAP-034
used_by: SAP-035, SAP-038
related: SAP-034, SAP-035, SAP-038
tags:
  - architecture
  - ddd
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 37
permalink: /software-architecture/open-host-service/
  - advanced
  - strategic
---

# SAP-037 - Open Host Service

⚡ TL;DR - An Open Host Service defines a formal, stable protocol through which a Bounded Context exposes its services to multiple consumers - rather than customizing for each, it publishes a well-documented interface that all consumers integrate against.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-035, SAP-034          |
| **Used by**    | SAP-035, SAP-038          |
| **Related**    | SAP-034, SAP-035, SAP-038 |

---

### 🔥 The Problem This Solves

**THE MANY-CONSUMERS PROBLEM:**
An `Inventory` service has 6 downstream consumers: Order Management, Shipping, Procurement, Analytics, Mobile App, and a third-party marketplace. Each wants to integrate differently. Without a standard protocol, the Inventory team would need to understand and accommodate 6 different integration models - an unsustainable burden.

**THE OPEN HOST SERVICE SOLUTION:**
The Inventory service defines one formal, stable, well-documented integration protocol. All consumers integrate against this protocol. The Inventory team owns and maintains the protocol. Consumers adapt to it (or use an ACL to translate). The host service doesn't know or care about each consumer's internal model.

**EVOLUTION:**
Eric Evans introduced Open Host Service in "Domain-Driven Design" (2003) as the pattern for a team that wants to serve many consumers without being customised for each. The original concept was protocol-level. REST API design practices (2005+) and OpenAPI/Swagger (2011) operationalised OHS with formal specification tooling - a well-documented REST API with OpenAPI spec IS an Open Host Service. GraphQL (2015) took the pattern further: consumers specify exactly what fields they need, reducing the need for ACLs on the consumer side. Today, OHS is the standard for any "platform API" that must serve diverse consumers.

---

### 📘 Textbook Definition

An Open Host Service, as defined by Eric Evans in "Domain-Driven Design," is a protocol that gives access to a Bounded Context as a set of services. The protocol is open, meaning well-documented and accessible to anyone who needs to integrate. The hosting Bounded Context defines the protocol in its own terms. Downstream clients either adapt to the Open Host Service protocol directly (Conformist) or use an Anti-Corruption Layer to translate it into their own model. The Open Host Service is often paired with a Published Language - a well-documented exchange format that makes the protocol self-describing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A published, stable API that a service provides to multiple consumers - the service defines the interface, consumers adapt to it.

**One analogy:**

> A power outlet standard. The country's electrical authority defines the outlet standard (Open Host Service). All device manufacturers (consumers) build plugs that fit that standard - or buy adapters (ACL). The electrical authority doesn't customize outlets for every device brand. The standard is published, stable, and everyone integrates against it.

**One insight:**
Open Host Service is about the upstream service taking responsibility for a clean, documented, stable integration point. This is the responsible version of "you depend on us" - instead of being an unmaintained internal API that breaks consumers, you publish and maintain a real interface contract.

---

### 🔩 First Principles Explanation

**OPEN HOST SERVICE COMPONENTS:**

```
┌──────────────────────────────────────────────────────────┐
│          OPEN HOST SERVICE COMPONENTS                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Interface Definition:                                │
│     OpenAPI spec, gRPC proto, AsyncAPI, GraphQL schema   │
│     Describes available operations and data shapes       │
│                                                          │
│  2. Published Language:                                  │
│     Well-documented schema for exchange data             │
│     Versioned - consumers know exactly what to expect    │
│     Examples: JSON-LD, Avro schema, Protobuf             │
│                                                          │
│  3. Versioning Contract:                                 │
│     Semantic versioning for breaking changes             │
│     Deprecation policy (how long old versions supported) │
│     Changelog documenting all changes                    │
│                                                          │
│  4. Stability Guarantee:                                 │
│     The host service commits to backward compatibility   │
│     within a major version                               │
│     Breaking changes require major version bump          │
└──────────────────────────────────────────────────────────┘
```

**OHS vs CUSTOMER/SUPPLIER:**

```
┌──────────────────────────────────────────────────────────┐
│      OHS vs CUSTOMER/SUPPLIER COMPARISON                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Customer/Supplier:                                      │
│    Upstream accommodates specific Downstream needs       │
│    Bilateral negotiation (1:1 relationship)              │
│    Works well for 1-3 downstream consumers               │
│                                                          │
│  Open Host Service:                                      │
│    Upstream publishes one protocol for ALL consumers     │
│    Unilateral - host defines, consumers adapt            │
│    Works well for many (3+) downstream consumers         │
│    The "platform" or "API" model                         │
│                                                          │
│  Example:                                                │
│    Stripe is an Open Host Service                        │
│    → Stripe defines the API                              │
│    → Millions of companies integrate                     │
│    → If your model doesn't fit, you use an ACL           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE INVENTORY SERVICE EXAMPLE:**
Inventory service needs to support 6 consumers. Compare:

**Without OHS (Customer/Supplier × 6):**
Inventory team is in 6 separate conversations about integration. Each consumer has special requirements. The Inventory codebase has 6 different integration paths. Any internal change must be checked against all 6 consumers.

**With OHS:**
Inventory publishes OpenAPI 3.0 spec: `GET /stock/{productId}`, `POST /stock/reserve`, `POST /stock/release`. All consumers integrate against this spec. Adding a 7th consumer costs the Inventory team nothing. The Inventory team evolves internally as long as the API contract is maintained.

---

### 🧠 Mental Model / Analogy

> An Open Host Service is how successful platform companies operate. Stripe, Twilio, GitHub - they all define a clean, documented, versioned API. They don't customize for each customer. Customers use the API or wrap it in an adapter. The platform company maintains the API and is responsible for its stability. This is Open Host Service thinking applied to internal microservices.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
A published API that a service maintains for all its consumers. The service defines the API once, everyone uses it, and the service is responsible for keeping it stable.

**Level 2 - How to implement (junior):**
Write an OpenAPI specification for your service's integration points. Version the API (v1, v2). Document request/response schemas. Implement the API. All consumers use the published spec. When you need to change the API, increment the version and support both versions during a deprecation window.

**Level 3 - Design principles (mid-level):**
OHS API design principles: expose domain operations, not internal implementation details (e.g., `POST /reservations` not `POST /inventory-line-items/update-reserved-count`). Use event publishing (Kafka, RabbitMQ) for the push model alongside REST/gRPC for pull. Document explicitly what is guaranteed stable versus what might change. The Published Language (schema) is part of the OHS - it defines the vocabulary of the exchange.

**Level 4 - Platform engineering (senior/staff):**
At scale, Open Host Services are the building blocks of internal platform engineering. Platform teams own their services as products with consumers as their customers. SLOs for the API, backwards compatibility guarantees, SDK generation from OpenAPI specs - these are all OHS concepts. The key governance question is: who can change the OHS, and what's the process? Typically: breaking changes require major version bumps, consumer notification, and deprecation periods. Non-breaking additions are backward compatible and don't require consumer action. This discipline is what separates a reliable internal platform from an undocumented internal API that breaks consumers unexpectedly.

---

### ⚙️ How It Works (Mechanism)

**OHS with Published Language:**

```
┌──────────────────────────────────────────────────────────┐
│         OPEN HOST SERVICE - EVENT PUBLISHING             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Inventory Service (Open Host Service):                  │
│                                                          │
│  REST API (synchronous):                                 │
│    GET  /v1/stock/{productId}                            │
│    POST /v1/stock/reserve                                │
│    POST /v1/stock/release                                │
│    (Published as OpenAPI 3.0 spec)                       │
│                                                          │
│  Event Stream (asynchronous):                            │
│    Topic: inventory.stock-level-changed                  │
│    Topic: inventory.stock-reserved                       │
│    Topic: inventory.stock-depleted                       │
│    (Published as AsyncAPI spec with Avro schemas)        │
│                                                          │
│  Consumers:                                              │
│    Order Mgmt → REST API for reservation                 │
│    Analytics  → Event stream for metrics                 │
│    Mobile App → REST API for display                     │
│    Each integrates against the Published Language        │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│         OHS IN THE CONTEXT MAP                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [Inventory Service]                                     │
│    Published Language: OpenAPI + Avro schemas            │
│    Open Host Service: REST API + Kafka events            │
│         │                                                │
│         ├── Order Management (with ACL)                  │
│         │   (translates Inventory model to domain model) │
│         │                                                │
│         ├── Shipping (Conformist)                        │
│         │   (adopts Inventory model as-is)               │
│         │                                                │
│         ├── Analytics (Conformist)                       │
│         │   (consumes events directly)                   │
│         │                                                │
│         └── Third-party Marketplace (with their ACL)     │
│             (they translate on their side)               │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Open Host Service - REST API with versioning:**

```java
// OHS - versioned controller exposing domain operations
@RestController
@RequestMapping("/v1/stock")
@Tag(name = "Inventory", description = "Inventory OHS v1")
public class InventoryOpenHostController {

    private final InventoryApplicationService inventorySvc;

    @GetMapping("/{productId}")
    @Operation(summary = "Get current stock level")
    public ResponseEntity<StockLevelResponse> getStockLevel(
            @PathVariable String productId) {
        StockLevel level = inventorySvc
            .getStockLevel(ProductId.of(productId));

        // Response DTO = Published Language
        return ResponseEntity.ok(
            StockLevelResponse.from(level));
    }

    @PostMapping("/reserve")
    @Operation(summary = "Reserve stock for an order")
    public ResponseEntity<ReservationResponse> reserve(
            @RequestBody @Valid ReserveStockRequest request) {
        Reservation reservation = inventorySvc.reserve(
            ProductId.of(request.productId()),
            Quantity.of(request.quantity()),
            OrderId.of(request.orderId()));

        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(ReservationResponse.from(reservation));
    }
}

// Published Language DTO - the exchange format
// Part of the OHS contract - stable, versioned
public record StockLevelResponse(
    String productId,
    int availableQuantity,
    int reservedQuantity,
    String warehouseCode,
    Instant lastUpdated
) {
    public static StockLevelResponse from(StockLevel level) {
        return new StockLevelResponse(
            level.productId().value().toString(),
            level.available().value(),
            level.reserved().value(),
            level.warehouseCode(),
            level.lastUpdated()
        );
    }
}
```

**Event publishing as part of OHS:**

```java
// Domain event published to Kafka - part of the OHS contract
// Schema registered in Schema Registry (Avro/JSON Schema)
public record StockDepletedEvent(
    @JsonProperty("productId") String productId,
    @JsonProperty("warehouseCode") String warehouseCode,
    @JsonProperty("lastAvailableAt") Instant lastAvailableAt,
    @JsonProperty("eventId") String eventId,
    @JsonProperty("eventVersion") int eventVersion  // = 1
) implements PublishedEvent {
    // Avro schema version: 1
    // Topic: inventory.stock-depleted
    // Consumers subscribe to this Published Language
}
```

---

### ⚖️ Comparison Table

| Pattern               | Direction             | # Consumers | Stability              | Effort                  |
| --------------------- | --------------------- | ----------- | ---------------------- | ----------------------- |
| **Open Host Service** | Upstream publishes    | Many        | High (stable contract) | High (spec, versioning) |
| Customer/Supplier     | Bilateral negotiation | Few (1-3)   | Medium (negotiated)    | Medium                  |
| Conformist            | Downstream adopts     | N/A         | As upstream            | Low                     |
| Separate Ways         | None                  | N/A         | N/A                    | None                    |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                         |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Every REST API is an Open Host Service | OHS requires a formal, documented, stable protocol - an ad-hoc internal API without these properties is not OHS |
| OHS eliminates the need for ACLs       | Consumers often still need ACLs to translate the OHS protocol into their own domain model                       |
| OHS means you never change the API     | OHS means you change it responsibly - with versioning, deprecation periods, and consumer communication          |
| Published Language is always JSON      | Published Language is any agreed-upon schema - JSON, Avro, Protobuf, GraphQL schema                             |

---

### 🚨 Failure Modes & Diagnosis

**Undocumented "Open Host Service"**

**Symptom:** Many consumers depend on your service but there's no OpenAPI spec, no schema registry, no version number. Consumers discover the API by reading your code or asking your team.

**Root Cause:** Internal API masquerading as OHS without the stability and documentation commitments.

**Fix:** Invest in proper OHS documentation: OpenAPI/AsyncAPI specs, schema registry, versioning policy, deprecation policy. Treat consumers as customers.

---

**Breaking Change without Version Bump**

**Symptom:** Service changes a field name in the response. Three consuming services break in production.

**Root Cause:** Breaking change to OHS protocol without versioning or consumer notification.

**Fix:** Semantic versioning: any field removal, rename, or type change is a BREAKING CHANGE requiring a major version bump. Support both versions during deprecation period.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When one system must serve many consumers with different needs, publish ONE stable protocol optimized for integration rather than customizing separately for each consumer. The protocol absorbs consumer diversity; the implementation doesn't.

**Where else this pattern appears:**

- **Electrical power outlets:** Each country defines one standard power outlet format (its Open Host Service). Every appliance manufacturer adapts their device to the standard (or uses a travel adapter = ACL). The power grid doesn't customise its output per device.
- **Public transit schedules:** A train network publishes one unified GTFS (General Transit Feed Specification) data feed. All navigation apps (Google Maps, Citymapper, Transit) integrate against this standard. The transit authority doesn't produce custom feeds per app.
- **Banking SWIFT messages:** SWIFT defines the Published Language for international bank transfers. All banks implement SWIFT. No bank builds custom bilateral protocols for each correspondent bank - one standard serves all.

---

### 💡 The Surprising Truth

Open Host Service and Anti-Corruption Layer are complementary, not opposing patterns - but from different perspectives. The UPSTREAM team implements an OHS so consumers can integrate easily. The DOWNSTREAM team implements an ACL to protect their domain from the upstream's model. In a well-designed system, both exist simultaneously: the upstream publishes an OHS with a Published Language, AND the downstream wraps it with an ACL that translates the Published Language into their domain model. The ACL exists even for a well-designed OHS because the downstream domain has different concepts than the upstream - translation is always needed at bounded context boundaries.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-035 - Context Map (OHS is one of the relationship patterns on a Context Map; understanding Context Map shows when OHS is the right pattern versus Shared Kernel, Conformist, or Separate Ways)
- SAP-034 - Anti-Corruption Layer (the consumer-side companion to OHS; understanding ACL from the consumer perspective completes the picture of how OHS relationships work in practice)

**Builds On This (learn these next):**

- SAP-038 - Published Language (the schema and contract that the OHS publishes; OHS defines the service boundary, Published Language defines the exchange format)
- SAP-035 - Context Map (after understanding OHS, the Context Map shows where OHS relationships appear in the full architecture)

**Alternatives / Comparisons:**

- SAP-034 - Anti-Corruption Layer (complementary from the consumer side; ACL translates the OHS's Published Language into the consumer's domain model)
- SAP-036 - Shared Kernel (alternative integration approach; shares code instead of publishing a service protocol; lower latency but higher coupling)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Formal, stable published API for multiple │
│              │ consumers; upstream defines the protocol  │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Document it, version it, maintain it      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many consumers; upstream controls API     │
├──────────────┼───────────────────────────────────────────┤
│ REQUIRES     │ OpenAPI/AsyncAPI spec, versioning policy  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The power outlet standard: publish once, │
│              │  all consumers plug in and adapt"         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Inventory service's Open Host Service REST API is consumed by 8 services. You need to change the response format for `GET /v1/stock/{productId}` - the `quantity` field needs to become a nested object `{ available: int, reserved: int }` instead of a single integer. This is a breaking change. Design the complete migration strategy: how do you introduce v2, support both v1 and v2, notify consumers, and eventually deprecate v1?

_Hint:_ Research URL path versioning (`/v1/` vs `/v2/`) versus header-based versioning (`Accept: application/vnd.inventory.v2+json`). The standard approach: implement `/v2/stock/{productId}` alongside existing `/v1/`, notify all 8 consumers, give a deprecation period (e.g., 3 months), then remove `/v1/`. Research how Stripe's API versioning strategy handles this: they preserve old behavior per API key version, so consumers never break until they explicitly upgrade.

**Q2.** An Open Host Service typically means the upstream team defines the integration contract. But what about API design quality? If the OHS has a poorly designed Published Language (verbose, confusing field names, inconsistent formats), should consumers just use ACLs to hide the poor design? Or should they push back on the OHS provider to improve the design? What's the governance process for improving OHS quality?

_Hint:_ Research the "Customer/Supplier" relationship pattern from Evans's DDD - specifically the governance model where downstream teams are customers with influence over the upstream team's (supplier's) API roadmap. The question reveals a political dimension of Context Map patterns: Conformist relationships occur when downstream has no influence; Customer/Supplier occurs when downstream teams can negotiate API improvements. The ACL should be a temporary solution while the OHS improves, not a permanent acceptance of poor design.

**Q3.** Your platform team publishes an OHS for authentication (`AuthService`). All 15 application services depend on it. When `AuthService` is down, all 15 services cannot authenticate new requests. The OHS has created a single point of failure. How do you design the OHS and its consumers to maintain some level of operation when the OHS is temporarily unavailable?

_Hint:_ Research the "Circuit Breaker" pattern (from Microservices patterns) applied to OHS consumer resilience - specifically how a consumer that caches authentication decisions for a configurable TTL can serve requests from cache during `AuthService` outages. Research JWT tokens as a Published Language for authentication that embeds expiry and claims, enabling consumers to validate tokens locally without calling `AuthService` for every request. This converts a synchronous OHS dependency into a stateless validation operation.
