---
layout: default
title: "Adapter Pattern (Microservices)"
parent: "Microservices"
nav_order: 65
permalink: /microservices/adapter-pattern-microservices/
id: MSV-065
category: Microservices
difficulty: ★★★
depends_on: Sidecar Pattern (Microservices), Ambassador Pattern, Service Contract
used_by: Ambassador Pattern, Sidecar Pattern (Microservices), Backward Compatibility
related: Ambassador Pattern, Sidecar Pattern (Microservices), Backward Compatibility
tags:
  - microservices
  - patterns
  - integration
  - design
  - deep-dive
---

# MSV-065 — Adapter Pattern (Microservices)

⚡ TL;DR — The adapter pattern in microservices wraps an existing service with a new interface — translating between incompatible protocols, data formats, or API shapes — enabling integration without modifying the legacy service or requiring all consumers to understand its idiosyncrasies.

| #680            | Category: Microservices                                                     | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Sidecar Pattern (Microservices), Ambassador Pattern, Service Contract       |                 |
| **Used by:**    | Ambassador Pattern, Sidecar Pattern (Microservices), Backward Compatibility |                 |
| **Related:**    | Ambassador Pattern, Sidecar Pattern (Microservices), Backward Compatibility |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your organisation has a legacy Payment Service built in 2008. It speaks SOAP/XML over HTTP/1.0, requires HMAC authentication with a proprietary key format, and returns XML with deeply nested structures. Every new microservice that needs to call Payment Service must: implement a SOAP client, understand the HMAC key format, parse the legacy XML response, handle legacy error codes. Five teams do this. Five different SOAP client implementations. When the HMAC key format changes, five teams must update their integration. Nobody fully understands the legacy Payment Service protocol except one engineer who is retiring.

**THE BREAKING POINT:**
Integration with legacy systems (or external third-party APIs) leaks complexity into consuming services. Each consumer re-implements the same integration logic. Changes to the legacy system propagate to all consumers. The legacy system becomes a source of technical debt that metastasises across the fleet.

**THE INVENTION MOMENT:**
The adapter pattern wraps the legacy service in a new, clean interface that all consumers use. Consumers speak modern JSON/REST. The adapter translates to SOAP/XML internally. When the HMAC format changes, only the adapter is updated. When the adapter is updated, all consumers benefit without changes.

---

### 📘 Textbook Definition

The **adapter pattern** (in microservices, also called the "strangler fig" adapter, "anti-corruption layer," or "integration facade") is a structural pattern where a dedicated service or component translates between incompatible interfaces. It wraps an existing service (legacy, third-party, or mismatched protocol) with a new interface that conforms to the consumer's expectations. The adapter handles: **protocol translation** (SOAP → REST, Thrift → gRPC), **data format translation** (XML → JSON, legacy field names → canonical field names), **authentication adaptation** (proprietary auth → modern OAuth/JWT), and **error normalisation** (legacy error codes → standard HTTP status codes + domain error codes). The adapter is the only component that understands the wrapped service's interface; all consumers depend on the adapter's clean interface.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A translator service that converts your clean API calls into whatever the legacy system needs — so you never expose legacy complexity to consumers.

**One analogy:**

> A power outlet adapter. Your laptop has a USB-C charger (modern interface). The hotel room in France has a Type E socket (legacy interface). The adapter translates between the two. You don't modify your laptop charger (consumer); you don't re-wire the hotel's electrical system (legacy service). The adapter is a small, contained translation layer between them.

**One insight:**
The adapter is a containment strategy for complexity. Legacy systems have ugly interfaces — proprietary protocols, XML, weird auth, opaque error codes. The adapter absorbs all of that ugliness. New consumers see only clean, modern interfaces. When the legacy system changes, only the adapter changes.

---

### 🔩 First Principles Explanation

**ADAPTER PATTERNS IN MICROSERVICES — THREE FORMS:**

**Form 1: Protocol Adapter (Service Wrapper)**

```
Consumer (REST/JSON) → Adapter Service → Legacy (SOAP/XML)

Consumer calls: POST /api/v1/payments {"amount": 99.99}
Adapter:
  - Translates to SOAP envelope
  - Adds HMAC auth header
  - Calls: POST /LegacyPaymentService.svc with XML body
  - Receives XML response
  - Translates to: {"paymentId": "...", "status": "APPROVED"}
Consumer receives: clean JSON
```

**Form 2: Sidecar Adapter (In-Pod Translation)**

```
App calls → Adapter sidecar (localhost) → External service

Used when: app speaks one protocol; external service requires another
Example: app speaks HTTP/1.1; external service requires gRPC
Adapter sidecar: translates HTTP/1.1 to gRPC locally
(This is the adapter+sidecar combination — "ambassador adapter")
```

**Form 3: Anti-Corruption Layer (Domain Boundary)**

```
New Service (clean domain model) → ACL → Legacy Service (old domain)

The ACL translates not just protocol but also:
  - Concepts (legacy "CUST_ID" → domain "customerId")
  - Semantics (legacy "STAT_CD: 3" → domain "status: SHIPPED")
  - Cardinality (legacy returns array of codes → domain maps to enum)
```

**WHAT THE ADAPTER HANDLES:**

| Concern            | Adapter Role                                            |
| ------------------ | ------------------------------------------------------- |
| **Protocol**       | REST↔SOAP, HTTP↔gRPC, REST↔MQ                           |
| **Format**         | JSON↔XML, flat↔nested, arrays↔maps                      |
| **Authentication** | OAuth↔HMAC↔API key                                      |
| **Error codes**    | Legacy codes → HTTP status + domain errors              |
| **Field names**    | Legacy names → canonical domain names                   |
| **Units/types**    | Cents (int) → Dollars (decimal); epoch (long) → ISO8601 |
| **Versioning**     | Legacy v1 → consumer v2 (field migration)               |

**THE ANTI-CORRUPTION LAYER (Eric Evans, DDD):**
The ACL is the adapter's domain-model version. It prevents legacy domain concepts from leaking into the new service's domain model. Without ACL: `Customer.legacyStatus = "CUST_STAT_CD_03"` pollutes the new domain. With ACL: new domain has `Customer.status = CustomerStatus.ACTIVE`; the ACL translates `CUST_STAT_CD_03` → `ACTIVE` at the boundary.

**THE TRADE-OFFS:**
**Gain:** Legacy complexity contained; all consumers use clean interface; single update point for integration changes; enables incremental migration away from legacy; prevents domain model corruption.
**Cost:** Additional service to maintain; potential bottleneck (all consumers route through adapter); added latency; if adapter becomes a monolith absorbing too many concerns, it recreates the original problem; testing complexity (adapter + legacy + consumer integration).

---

### 🧪 Thought Experiment

**SETUP:**
Legacy Payment Service returns this XML:

```xml
<PMTRSLT>
  <RSLT_CD>00</RSLT_CD>
  <PMT_REF>12345</PMT_REF>
  <PROC_DT>20240115143022</PROC_DT>
</PMTRSLT>
```

**WITHOUT ADAPTER:**
Each consumer parses this XML, maps `RSLT_CD` values (`00=success, 01=insufficient_funds, 99=system_error`), parses `PROC_DT` as `yyyyMMddHHmmss`, maps `PMT_REF` to `paymentId`. Five consumers do this. When the legacy system adds `PROC_DT2` (with timezone), three consumers break. The other two somehow handle it correctly but differently.

**WITH ADAPTER:**
Adapter parses legacy XML internally. Adapter emits clean JSON:

```json
{
  "paymentId": "12345",
  "status": "APPROVED",
  "processedAt": "2024-01-15T14:30:22Z"
}
```

All five consumers get the same clean response. When `PROC_DT2` is added: adapter absorbs the change. Zero consumer updates required.

**THE LESSON:**
The adapter is a blast shield. All changes to the legacy system's interface are absorbed by the adapter. Consumers are permanently isolated from legacy interface evolution. The adapter is the only component that must understand the legacy system.

---

### 🧠 Mental Model / Analogy

> The adapter pattern is like a United Nations interpreter. The UN speaker (legacy service) speaks one language (SOAP/XML). The delegates (consumers) speak another language (REST/JSON). The interpreter (adapter) translates between them in real time. The speaker doesn't change their language; the delegates don't learn the speaker's language. The interpreter absorbs the complexity of both languages. If the speaker adds new vocabulary (new API field), only the interpreter needs to learn it — not all the delegates.

- "UN speaker" → legacy service
- "Delegates" → consumer services
- "Interpreter" → adapter service
- "Speaker's language" → legacy API (SOAP/XML/proprietary)
- "Delegates' language" → modern API (REST/JSON)
- "Interpreter absorbs vocabulary changes" → adapter absorbs legacy API changes

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An adapter service is like a universal remote control. Your TV (legacy service) only understands its own remote (proprietary protocol). The universal remote (adapter) translates your button presses (clean API calls) into the TV's language (legacy protocol). You don't need to know how the TV's remote works.

**Level 2 — Building a simple REST-to-legacy adapter (junior developer):**
Create a Spring Boot service with a REST controller. The controller accepts clean JSON requests. The service layer translates the request to the legacy format (SOAP, XML, proprietary). Calls the legacy system. Translates the response back to clean JSON. Returns clean JSON to the consumer. The adapter is a standalone microservice with its own deployment.

**Level 3 — Anti-Corruption Layer in DDD (mid-level engineer):**
In Domain-Driven Design, the ACL is a formal pattern for integration at a Bounded Context boundary. When two bounded contexts have different domain models, the ACL translates between them without allowing one model to corrupt the other. Implementation: a dedicated translation layer in code (not always a separate service) that maps legacy DTO → domain model, legacy exceptions → domain exceptions, legacy terminology → ubiquitous language. The ACL prevents "legacy model pollution" — the gradual contamination of a clean domain model with legacy field names, concepts, and status codes.

**Level 4 — Strangler Fig + Adapter (senior/staff):**
The adapter pattern is a key enabler of the strangler fig pattern (Martin Fowler) for legacy system migration. Phase 1: wrap the legacy system with an adapter; all consumers use the adapter. Phase 2: build the new system behind the same adapter interface; adapter routes some requests to the new system (canary). Phase 3: when the new system is ready, adapter routes all requests to it; legacy system decommissioned. The adapter's clean interface never changes; consumers are unaware that the underlying system was replaced. This is how large organisations incrementally replace legacy systems without big-bang rewrites — the adapter provides the stable interface for the transition.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ Adapter Service — Request Translation                   │
└─────────────────────────────────────────────────────────┘

Order Service:
  POST http://payment-adapter/v1/payments
  {"amount": 99.99, "currency": "USD", "orderId": "ORD-123"}
  Authorization: Bearer <JWT>

Payment Adapter (adapter service):
  1. Validate + extract JWT
  2. Translate to SOAP envelope:
     <PMTREQ>
       <AMT>9999</AMT>  ← convert decimal to cents
       <CCY>840</CCY>   ← convert ISO currency code to numeric
       <REF>ORD-123</REF>
     </PMTREQ>
  3. Compute HMAC-SHA256 signature with legacy key
  4. POST to http://legacy-payment-service:8080/PaymentService
  5. Receive XML response
  6. Translate XML → JSON domain model
  7. Map RSLT_CD: "00" → {status: "APPROVED"}
  8. Return: {"paymentId": "12345", "status": "APPROVED", "processedAt": "..."}

Order Service:
  Receives clean JSON; no knowledge of legacy system
```

---

### 💻 Code Example

**Spring Boot payment adapter service:**

```java
@RestController
@RequestMapping("/v1/payments")
public class PaymentAdapterController {

    private final LegacyPaymentClient legacyClient;
    private final PaymentTranslator translator;

    @PostMapping
    public ResponseEntity<PaymentResponse> processPayment(
            @RequestBody @Valid PaymentRequest request) {

        // Translate clean request → legacy format
        LegacyPaymentRequest legacyRequest =
            translator.toLegacy(request);

        // Call legacy SOAP service
        LegacyPaymentResponse legacyResponse =
            legacyClient.submitPayment(legacyRequest);

        // Translate legacy response → clean domain response
        PaymentResponse response =
            translator.fromLegacy(legacyResponse);

        return ResponseEntity.status(201).body(response);
    }
}

@Component
public class PaymentTranslator {

    public LegacyPaymentRequest toLegacy(PaymentRequest request) {
        return LegacyPaymentRequest.builder()
            .amt(toCents(request.getAmount()))      // decimal → cents
            .ccy(toCurrencyCode(request.getCurrency()))  // "USD" → 840
            .ref(request.getOrderId())
            .build();
    }

    public PaymentResponse fromLegacy(LegacyPaymentResponse legacy) {
        return PaymentResponse.builder()
            .paymentId(legacy.getPmtRef())
            .status(mapStatus(legacy.getRsltCd()))  // "00" → APPROVED
            .processedAt(parseDate(legacy.getProcDt())) // yyyyMMddHHmmss → ISO8601
            .build();
    }

    private PaymentStatus mapStatus(String rsltCd) {
        return switch (rsltCd) {
            case "00" -> PaymentStatus.APPROVED;
            case "01" -> throw new InsufficientFundsException();
            case "99" -> throw new PaymentSystemException();
            default   -> throw new UnknownPaymentStatusException(rsltCd);
        };
    }
}
```

**Sidecar adapter for protocol translation (gRPC↔REST):**

```yaml
# Envoy sidecar as adapter: app speaks REST, upstream requires gRPC
spec:
  containers:
    - name: order-service
      env:
        - name: INVENTORY_URL
          value: "http://localhost:9000" # local adapter port

    - name: grpc-adapter
      image: envoyproxy/envoy:v1.28
      # Configured: listener :9000 → transcodes REST to gRPC
      # Uses: envoy.filters.http.grpc_json_transcoder
      # App calls REST → Envoy transcodes to gRPC → Inventory Service
```

---

### ⚖️ Comparison Table

| Pattern                   | Purpose                        | Location             | Direction     | Scope                    |
| ------------------------- | ------------------------------ | -------------------- | ------------- | ------------------------ |
| **Adapter**               | Protocol/format translation    | Service or sidecar   | Any           | Integration boundary     |
| **Ambassador**            | Outbound connection management | Sidecar              | Outbound only | Any upstream             |
| **Sidecar**               | Cross-cutting concern          | Co-located container | Any           | Pod-level                |
| **API Gateway**           | Inbound routing/auth           | Edge                 | Inbound       | Fleet-wide               |
| **Anti-Corruption Layer** | Domain model protection        | Code layer           | Any           | Bounded context boundary |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                         |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Adapter = ambassador                             | Ambassador handles connection management (retries, TLS); adapter handles protocol/format translation; often combined, but distinct concerns     |
| Adapter is only for legacy systems               | Adapters are also useful for external third-party APIs, between microservices with incompatible domain models, and during API version migration |
| Adapter creates a single point of failure        | Adapter is a service; deploy with multiple replicas and circuit breakers; failure is contained to the integration point                         |
| Anti-corruption layer must be a separate service | ACL can be implemented as a translation layer in code within a service; doesn't require a separate deployment                                   |

---

### 🚨 Failure Modes & Diagnosis

**Adapter Becomes a God Service**

**Symptom:** The adapter absorbs too many translation responsibilities; it becomes a mini-monolith with 30 endpoints for 10 different legacy systems; it has its own database, its own cache, its own business logic.

**Root Cause:** No scope boundary defined for the adapter; teams keep adding integrations to the same service.

**Fix:** One adapter per legacy/external system (not one adapter for all). Keep adapters thin (translation only; no business logic). Use separate adapters for: payment-adapter, inventory-adapter, shipping-adapter.

---

**Data Loss in Translation**

**Symptom:** Consumer reports missing fields in response; traced to adapter not translating a new field the legacy system started returning.

**Root Cause:** Legacy system added a new field; adapter doesn't map it; field is silently dropped.

**Prevention:**

```java
// Log warning on unmapped fields
@JsonIgnoreProperties  // DON'T use this blindly
// Instead: log unknown fields for review
@JsonAnySetter
public void handleUnknown(String key, Object value) {
    log.warn("Unknown field from legacy: key={}, value={}", key, value);
    // Can choose to forward it as-is or drop it explicitly
}
```

---

### 🔗 Related Keywords

**Prerequisites:** `Sidecar Pattern (Microservices)`, `Ambassador Pattern`, `Service Contract`

**Builds On This:** `Ambassador Pattern`, `Sidecar Pattern (Microservices)`, `Backward Compatibility`

**Related Patterns:** `Ambassador Pattern`, `Anti-Corruption Layer`, `Strangler Fig Pattern`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Translation layer between incompatible    │
│              │ interfaces (protocol, format, domain)     │
├──────────────┼───────────────────────────────────────────┤
│ THREE FORMS  │ Service wrapper (REST→SOAP service)       │
│              │ Sidecar adapter (protocol translation)    │
│              │ Anti-corruption layer (domain boundary)   │
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFIT  │ Legacy complexity contained in one place; │
│              │ consumers see only clean interface        │
├──────────────┼───────────────────────────────────────────┤
│ STRANGLER    │ Adapter enables incremental legacy        │
│ FIG USE      │ replacement without consumer changes      │
├──────────────┼───────────────────────────────────────────┤
│ RELATION     │ Adapter (translation) ≠ Ambassador        │
│              │ (connection management)                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Legacy speaks its language inside;       │
│              │  everyone else sees your language"        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're building an adapter for a third-party shipping service. The shipping service API has 4 versions (v1–v4) all still in production (different clients use different versions). You need to support all 4 versions. How do you design the adapter? What does the internal model look like? How do you handle fields that exist in v4 but not v1? How do you handle error codes that changed meaning between versions?

**Q2.** Your adapter service translates REST→SOAP for a legacy payment system. The adapter processes 5,000 requests/second at peak. The legacy SOAP service becomes a bottleneck (max 3,000 req/sec capacity). The adapter can't batch requests (legacy system is request/response only). Describe the strategies available to reduce load on the legacy system while maintaining the adapter's clean interface to consumers. Which strategy would you choose and why?
