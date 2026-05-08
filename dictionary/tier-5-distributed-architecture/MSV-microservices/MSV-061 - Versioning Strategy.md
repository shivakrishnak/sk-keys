---
layout: default
title: "Versioning Strategy"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /microservices/versioning-strategy/
id: MSV-061
category: Microservices
difficulty: ★★★
depends_on: Backward Compatibility, Service Contract, API Gateway
used_by: Backward Compatibility, Service Contract, Zero-Downtime Deployment
related: Backward Compatibility, Service Contract, Consumer-Driven Contract Testing
tags:
  - microservices
  - api-design
  - versioning
  - design
  - deep-dive
---

# MSV-061 - Versioning Strategy

⚡ TL;DR - API versioning strategy defines how a service signals and manages breaking API changes - URI versioning (`/v2/`), header versioning (`Accept-Version: v2`), media type versioning, or semantic versioning - allowing old consumers to continue working while new consumers use updated interfaces.

| #676            | Category: Microservices                                                    | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Backward Compatibility, Service Contract, API Gateway                      |                 |
| **Used by:**    | Backward Compatibility, Service Contract, Zero-Downtime Deployment         |                 |
| **Related:**    | Backward Compatibility, Service Contract, Consumer-Driven Contract Testing |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Payment Service deploys a new API. The field `amount` is now renamed to `totalAmount`. All consumers break simultaneously. Team response: "Everyone must update within this weekend's deployment window." Four teams work over the weekend to update their services. One team misses the deadline. Monday: 25% of payment flows are broken. Root cause: no versioning strategy; breaking change to a shared API with no migration period.

**THE BREAKING POINT:**
Distributed systems require that consumers be independently deployable. This means a provider must be able to release breaking changes without requiring all consumers to update simultaneously. Versioning strategies provide the mechanism: run multiple API versions concurrently; consumers migrate at their own pace; old version is sunset after a defined period.

**THE INVENTION MOMENT:**
API versioning decouples the release timeline between providers and consumers. The provider can release v2 while continuing to serve v1. Consumers migrate to v2 at their own pace. v1 is sunset only after all consumers have migrated. Independent deployability is preserved.

---

### 📘 Textbook Definition

An **API versioning strategy** is the mechanism by which a service signals and manages changes to its external interface over time. Versioning enables coexistence of multiple API versions, allowing: (a) breaking changes to be introduced in new versions without affecting existing consumers; (b) consumers to migrate at their own pace; (c) providers to sunset old versions after a defined deprecation period. Common strategies include: **URI versioning** (`/api/v1/`, `/api/v2/`), **Header versioning** (`Accept-Version: v2`), **Media type versioning** (`Accept: application/vnd.myapi.v2+json`), and **Semantic versioning** (SemVer: `MAJOR.MINOR.PATCH` with MAJOR indicating breaking changes).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Signal which version of the API you're using so old and new consumers can coexist.

**One analogy:**

> Software versioning is like building codes. When a new building code (API v2) is released, existing buildings (consumers) don't need to be torn down and rebuilt immediately. New buildings must comply with the new code. Existing buildings are grandfathered under the old code (v1 served). After a sunset period, the old code version is retired - existing buildings must comply or be demolished (consumers must migrate or be decommissioned).

**One insight:**
Versioning is the admission that you will need to make breaking changes, and the strategy for doing so without coordination chaos. The "no versioning" approach implies either: no breaking changes ever (impossible long-term) or coordinated simultaneous updates (a distributed monolith).

---

### 🔩 First Principles Explanation

**VERSIONING MECHANISMS:**

**1. URI Path Versioning (most common):**

```
GET /api/v1/orders
GET /api/v2/orders
```

- Pros: explicit, easy to see in logs/metrics, easy to proxy/route in API gateway
- Cons: "URI should identify resource, not version of resource" (REST purists); multiple URIs for same resource
- Best for: public APIs; large breaking changes; long co-existence periods

**2. Header Versioning:**

```
GET /api/orders
Accept-Version: v2
# or
X-API-Version: 2
```

- Pros: clean URIs; cacheable per-version
- Cons: less visible; requires custom header support in clients; harder to test in browser
- Best for: internal APIs where headers are controlled; minor version distinctions

**3. Media Type Versioning (Content Negotiation):**

```
GET /api/orders
Accept: application/vnd.mycompany.order.v2+json
```

- Pros: RESTful; leverages HTTP content negotiation
- Cons: verbose; complex to implement and maintain; clients must know media types
- Best for: technically pure REST APIs; rarely used in practice

**4. Query Parameter Versioning:**

```
GET /api/orders?version=2
```

- Pros: simple; visible in URLs
- Cons: not RESTful; version in cache key; often considered a shortcut
- Best for: prototyping; not recommended for production APIs

**SEMANTIC VERSIONING (SemVer) for API contracts:**

```
MAJOR.MINOR.PATCH
  MAJOR: breaking change (increment forces consumers to update)
  MINOR: backward-compatible addition (new feature; optional)
  PATCH: backward-compatible bug fix (no API change)

Examples:
  v1.0.0 → v1.1.0: added optional field (consumers can ignore)
  v1.1.0 → v1.1.1: fixed response latency bug (no API change)
  v1.1.1 → v2.0.0: renamed field (breaking; consumers must migrate)
```

**THE VERSIONING LIFECYCLE:**

```
1. v1 released: serves all consumers

2. Breaking change needed:
   → Implement v2 endpoint (or full v2 API)
   → v1 continues to serve existing consumers
   → Announce: "v1 deprecated; sunset date: 90 days"

3. Migration period:
   → Consumers migrate to v2 at their pace
   → Monitor: which consumers still hit v1?
   → Assist: provide migration guide, client library updates

4. Sunset:
   → All consumers confirmed migrated (or decommissioned)
   → v1 shutdown
   → Remove v1 code

Tooling: API Gateway tracks version usage per consumer
```

**THE TRADE-OFFS:**
**Gain:** Independent deployability; graceful migration periods; consumer autonomy; provider can evolve API without blocking consumers.
**Cost:** Must maintain multiple versions simultaneously (code + infrastructure cost); migration coordination still required (just less urgent); risk of consumers never migrating ("zombie consumers"); version sprawl if not governed.

---

### 🧪 Thought Experiment

**SETUP:**
You use URI versioning. You have `/v1/payments` and `/v2/payments`. The API gateway routes `/v1` to the v1 handler and `/v2` to the v2 handler. Both are in the same Payment Service deployment.

**THE SCALING PROBLEM:**
After 2 years, you have `/v1/payments`, `/v2/payments`, and `/v3/payments`. Each version has slightly different logic. The code has three parallel handler implementations, sharing some logic but diverging at the edges. A bug fix must be applied to all three versions. Your v1 sunset plan never happened - 2 consumers still hit v1 (one was decommissioned but nobody updated the API gateway config).

**THE LESSON:**
Versioning requires active lifecycle management. Without it, versions accumulate. Solutions: (a) set hard sunset dates and enforce them (not soft "please migrate"); (b) sunset monitoring: API gateway emits `api_calls_by_version` metric; alert when v1 drops to 0; (c) limit concurrent versions: maximum 2 versions at any time; new version requires sunset of oldest.

---

### 🧠 Mental Model / Analogy

> API versioning is like maintaining highway lanes during construction. The old highway (v1) stays open while the new highway (v2) is built in parallel. Drivers (consumers) are directed to the new highway via signage (deprecation notices, migration guides). The old highway remains open during the transition. Once all drivers have switched to the new highway (consumers migrated), the old highway is closed (v1 sunset) and the land is repurposed.

- "Old highway" → v1 API
- "New highway" → v2 API
- "Parallel construction" → v2 built alongside v1
- "Signage directing drivers" → deprecation notices
- "Highway closed" → v1 sunset

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you need to change an API in a way that would break old users, you create a new version (`/v2/`) instead of changing the existing one. Old users keep using v1. New users use v2. After enough time, v1 is retired when everyone has switched.

**Level 2 - URI versioning in Spring Boot (junior developer):**
Create separate controllers for each API version: `@RequestMapping("/api/v1/payments")` and `@RequestMapping("/api/v2/payments")`. Share service layer logic where possible; version-specific logic in controllers. Or: single controller with version routing. Alternatively, use API gateway routing: API gateway routes `/v1/*` to service-v1 deployment, `/v2/*` to service-v2 deployment.

**Level 3 - Version routing patterns (mid-level engineer):**
Three implementation approaches: (1) **Multiple controllers** (same service): v1 and v2 handlers in same codebase; share service layer; version-specific serialisation. (2) **API gateway routing** (separate services): gateway routes `/v1` to old service version, `/v2` to new service version; clean separation; more infrastructure. (3) **Request transformation** (gateway-level): API gateway translates v1 requests to v2 format before forwarding to service; service only implements v2; v1 compatibility handled at gateway. Approach (3) is often cleanest for long-running APIs - one service implementation, version adapter at gateway.

**Level 4 - Event versioning (senior/staff):**
Event versioning (Kafka, EventBridge) is harder than HTTP API versioning because events are stored and replayed. You can't just "point consumers at v2" - consumers may replay v1 events from months ago. Solutions: (a) **Event schema registry** (Confluent, AWS Glue): track schema versions; consumers declare which version they read; compatibility mode enforced. (b) **Upcasting**: event handler that transforms old events to new format on read (not on write) - storage stays unchanged. (c) **Dual events**: producer emits both v1 and v2 events on separate topics; consumers subscribe to their version; when all consumers on v2, stop emitting v1 events. (d) **Event versioning header**: embed `schema-version: 2` in Kafka message header; consumer dispatcher routes to correct handler.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ API Gateway Version Routing + Sunset Monitoring         │
└─────────────────────────────────────────────────────────┘

API Gateway:
  /api/v1/payments → Payment Service v1 handler
  /api/v2/payments → Payment Service v2 handler

  Metrics emitted per request:
    api_calls{version="v1", consumer="order-service"} ++
    api_calls{version="v2", consumer="checkout-service"} ++

Deprecation HTTP header (RFC 8594):
  Response to v1 calls:
    Deprecation: Tue, 11 Mar 2025 23:59:59 GMT
    Sunset: Thu, 11 Jun 2025 23:59:59 GMT
    Link: </api/v2/payments>; rel="successor-version"

Sunset monitoring (Grafana):
  ALERT: api_calls{version="v1"} > 0 after sunset date
    → Someone is still calling v1 after sunset!
    → Action: investigate consumer; block or redirect

Sunset enforcement:
  On sunset date: API gateway returns 410 Gone for v1 calls
  Response body: {"error": "API v1 deprecated. Use /v2. Docs: https://..."}
```

---

### 💻 Code Example

**Spring Boot URI versioning:**

```java
@RestController
@RequestMapping("/api/v1/payments")
public class PaymentControllerV1 {

    @PostMapping
    public ResponseEntity<PaymentResponseV1> createPayment(
            @RequestBody PaymentRequestV1 request) {
        // v1 logic: uses 'amount' field
        PaymentResponseV1 response = paymentService.processV1(request);
        return ResponseEntity.status(201)
            .header("Deprecation", "Sun, 01 Jun 2025 00:00:00 GMT")
            .header("Sunset", "Sun, 31 Aug 2025 00:00:00 GMT")
            .body(response);
    }
}

@RestController
@RequestMapping("/api/v2/payments")
public class PaymentControllerV2 {

    @PostMapping
    public ResponseEntity<PaymentResponseV2> createPayment(
            @RequestBody PaymentRequestV2 request) {
        // v2 logic: uses 'totalAmount' + 'currency' fields
        PaymentResponseV2 response = paymentService.processV2(request);
        return ResponseEntity.status(201).body(response);
    }
}
```

**API Gateway route config (Nginx/Ingress):**

```yaml
# Route v1 to old handler; v2 to new handler (same service)
- path: /api/v1/
  pathType: Prefix
  backend:
    service:
      name: payment-service
      port: 8080
  # Custom header injected for routing
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /api/v1/$1

- path: /api/v2/
  pathType: Prefix
  backend:
    service:
      name: payment-service
      port: 8080
```

**Kafka event schema versioning with header:**

```java
// Producer: embed version in header
ProducerRecord<String, byte[]> record = new ProducerRecord<>(
    "order-events", key, avroBytes);
record.headers().add("schema-version", "2".getBytes());
producer.send(record);

// Consumer: dispatch to correct handler
@KafkaListener(topics = "order-events")
public void consume(ConsumerRecord<String, byte[]> record) {
    String version = new String(record.headers()
        .lastHeader("schema-version").value());
    switch (version) {
        case "1" -> handleV1(record.value());
        case "2" -> handleV2(record.value());
        default  -> log.warn("Unknown schema version: {}", version);
    }
}
```

---

### ⚖️ Comparison Table

| Strategy                             | Visibility | REST Purity | Caching | Client Complexity  |
| ------------------------------------ | ---------- | ----------- | ------- | ------------------ |
| **URI Path** (`/v2/`)                | High       | Low         | Easy    | Low                |
| **Header** (`X-API-Version`)         | Low        | High        | Medium  | Medium             |
| **Media Type** (`Accept: vnd.+json`) | Low        | Very High   | Easy    | High               |
| **Query Param** (`?v=2`)             | High       | Low         | Medium  | Low                |
| **No versioning**                    | N/A        | N/A         | N/A     | None (until break) |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                  |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Versioning means you can always make breaking changes | Versioning manages breaking changes; minimising them is still the goal                                   |
| Header versioning is more RESTful                     | There's no consensus; URI versioning is more practical for most teams                                    |
| Version 1 can stay forever                            | Zombie versions accumulate cost; active lifecycle management is required                                 |
| Versioning solves all compatibility problems          | Database migrations, event schema evolution, and inter-service protocol changes need separate strategies |

---

### 🚨 Failure Modes & Diagnosis

**Version Sprawl - Too Many Live Versions**

**Symptom:** Service maintains v1, v2, v3 simultaneously; bug fixes must be applied to all three; increasing maintenance burden.

**Root Cause:** No sunset enforcement; consumers never migrated; versions accumulated.

**Fix:** Set maximum concurrent versions policy (2); alert on v1 calls 30 days before sunset; block v1 at API gateway on sunset date.

---

### 🔗 Related Keywords

**Prerequisites:** `Backward Compatibility`, `Service Contract`, `API Gateway`

**Builds On This:** `Backward Compatibility`, `Service Contract`, `Zero-Downtime Deployment`

**Related Patterns:** `Consumer-Driven Contract Testing`, `Deprecation Pattern`, `API Gateway`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ How breaking API changes are signalled    │
│              │ and managed across consumer migrations    │
├──────────────┼───────────────────────────────────────────┤
│ COMMON       │ URI path (/v1/, /v2/) - most practical    │
│ STRATEGY     │                                          │
├──────────────┼───────────────────────────────────────────┤
│ LIFECYCLE    │ Release v2 → deprecate v1 → migrate →    │
│              │ sunset v1 → remove                       │
├──────────────┼───────────────────────────────────────────┤
│ SUNSET HDR   │ Deprecation + Sunset + Link headers       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Old and new run together; old retires    │
│              │  after everyone moves"                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You maintain a public API with 200 external consumers. You need to remove a field `legacyId` from the response (it's been meaningless for 2 years; no consumer should need it). You can't contact all 200 consumers. Design a versioning and sunset strategy, including: (a) the sunset timeline; (b) how you detect which consumers still use `legacyId`; (c) how you enforce the sunset if some consumers don't migrate.

**Q2.** Your team debates: URI versioning vs header versioning. Advocate for URI versioning. Now advocate for header versioning. Which would you choose for: (a) a public REST API with external third-party consumers; (b) an internal gRPC service used by 5 internal services?
