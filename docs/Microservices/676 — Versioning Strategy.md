---
layout: default
title: "Versioning Strategy"
parent: "Microservices"
nav_order: 676
permalink: /microservices/versioning-strategy/
number: "676"
category: Microservices
difficulty: ★★★
depends_on: "Backward Compatibility, API Gateway"
used_by: "Feature Flags, Service Contract"
tags: #advanced, #microservices, #distributed, #architecture, #devops
---

# 676 — Versioning Strategy

`#advanced` `#microservices` `#distributed` `#architecture` `#devops`

⚡ TL;DR — **Versioning Strategy** is how a service manages multiple API versions simultaneously to allow consumers to migrate at their own pace. Common approaches: URL versioning (`/v1/`, `/v2/`), header versioning (`Accept: application/vnd.service.v2+json`), and query param versioning (`?version=2`). URL versioning is the most widely used in microservices due to discoverability and routing simplicity.

| #676            | Category: Microservices             | Difficulty: ★★★ |
| :-------------- | :---------------------------------- | :-------------- |
| **Depends on:** | Backward Compatibility, API Gateway |                 |
| **Used by:**    | Feature Flags, Service Contract     |                 |

---

### 📘 Textbook Definition

**API Versioning Strategy** is the practice of managing multiple concurrent versions of a service's public API to enable backward-incompatible changes without forcing all consumers to update simultaneously. There are four primary strategies: (1) **URL Path Versioning**: embed the version in the URL path (`/api/v1/orders`, `/api/v2/orders`) — explicit, easy to route, easy to document; (2) **HTTP Header Versioning**: version specified in request/response headers (`Accept: application/vnd.company.orders-v2+json`) — clean URLs, but less discoverable; (3) **Query Parameter Versioning**: version as URL query parameter (`/api/orders?version=2`) — simple but pollutes query space; (4) **Semantic Versioning with Content Negotiation**: MIME type encodes version. Semantic Versioning (SemVer: MAJOR.MINOR.PATCH) provides a contract for versioning rules: MAJOR increment for breaking changes; MINOR increment for backward-compatible additions; PATCH increment for backward-compatible bug fixes. In practice, only MAJOR versions are surfaced to consumers in REST API URLs — MINOR and PATCH changes are transparent. The version lifecycle: GA (Generally Available) → Deprecated → Sunset (removed). Deprecation must include: written notice, migration guide, timeline, and Sunset date communicated via HTTP headers.

---

### 🟢 Simple Definition (Easy)

Versioning strategy = how you handle breaking API changes without forcing all users to update at once. You keep the old version running (`/v1/`) and add the new version (`/v2/`). Consumers switch to v2 on their timeline. When all consumers have switched, you remove v1. The strategy defines: how to signal versions, how long to run both, how to communicate deprecation, and when to remove the old version.

---

### 🔵 Simple Definition (Elaborated)

Order Service v1: `GET /api/v1/orders/{id}` → returns `{totalAmount: 149.99}`. New version changes to `{total: 149.99}` (breaking change). Strategy: keep `/v1/` alive, launch `/v2/` alongside. All 15 consumers of v1 are notified: "v1 will be removed December 31, 2025." Consumers migrate at their own pace. API Gateway routes `/v1/` and `/v2/` to the same order-service pods (the service handles both). On Jan 1, 2026: `/v1/` removed. Any consumer that didn't migrate: gets 404. Well-communicated, enforced deadline.

---

### 🔩 First Principles Explanation

**URL versioning in Spring Boot — single service handles multiple versions:**

```java
// Single service, multiple version controllers:
// Approach 1: Separate controllers per version (clean separation)

@RestController
@RequestMapping("/api/v1/orders")
class OrderControllerV1 {
    @Autowired private OrderService orderService;
    @Autowired private OrderMapperV1 mapper;

    @GetMapping("/{orderId}")
    ResponseEntity<OrderResponseV1> getOrder(@PathVariable UUID orderId) {
        Order order = orderService.getOrder(orderId);
        return ResponseEntity.ok()
            .header("Deprecation", "true")
            .header("Sunset", "Sat, 31 Dec 2025 23:59:59 GMT")
            .header("Link", "</api/v2/orders/" + orderId + ">; rel=\"successor-version\"")
            .body(mapper.toV1(order));
    }
}

@RestController
@RequestMapping("/api/v2/orders")
class OrderControllerV2 {
    @Autowired private OrderService orderService;
    @Autowired private OrderMapperV2 mapper;

    @GetMapping("/{orderId}")
    ResponseEntity<OrderResponseV2> getOrder(@PathVariable UUID orderId) {
        Order order = orderService.getOrder(orderId);
        return ResponseEntity.ok()
            .body(mapper.toV2(order));
    }
}

// V1 Response DTO: "totalAmount" field (old name)
@Data @Builder
class OrderResponseV1 {
    private UUID orderId;
    private UUID customerId;
    private String status;
    private BigDecimal totalAmount;  // old field name
}

// V2 Response DTO: "total" field (new name) + additional fields
@Data @Builder
class OrderResponseV2 {
    private UUID orderId;
    private UUID customerId;
    private String status;
    private BigDecimal total;          // new field name
    private int itemCount;             // new field added in v2
    private String shippingAddress;    // new field added in v2
}
```

**API Gateway routing for versioned services:**

```yaml
# Kong API Gateway — route v1 and v2 to the same upstream service:
# (The service handles both versions internally)
_format_version: "3.0"

services:
  - name: order-service
    url: http://order-service.svc.cluster.local:8080
    routes:
      - name: orders-v1
        paths:
          - /api/v1/orders
        methods: [GET, POST, PUT, DELETE]
        # Optional: add response header to all v1 responses:
        response-transformer:
          add:
            headers:
              - "Deprecation: true"
              - "Sunset: Sat, 31 Dec 2025 23:59:59 GMT"
      - name: orders-v2
        paths:
          - /api/v2/orders
        methods: [GET, POST, PUT, DELETE]

# Alternative: route v1 to old service image, v2 to new service image
# (useful when v2 is a complete rewrite, not an extension)
services:
  - name: order-service-v1
    url: http://order-service-v1.svc.cluster.local:8080
    routes:
      - name: orders-v1
        paths: [/api/v1/orders]
  - name: order-service-v2
    url: http://order-service-v2.svc.cluster.local:8080
    routes:
      - name: orders-v2
        paths: [/api/v2/orders]
```

**Header versioning approach:**

```java
// Header versioning: version in Accept header (REST best practice per Roy Fielding)
// Trade-off: cleaner URLs, but less discoverable, harder to test in browser

@RestController
@RequestMapping("/api/orders")
class OrderControllerHeaderVersioned {

    // GET with Accept: application/vnd.company.order.v1+json
    @GetMapping(value = "/{orderId}",
                produces = "application/vnd.company.order.v1+json")
    ResponseEntity<OrderResponseV1> getOrderV1(@PathVariable UUID orderId) {
        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType("application/vnd.company.order.v1+json"))
            .header("Deprecation", "true")
            .body(mapToV1(orderService.getOrder(orderId)));
    }

    // GET with Accept: application/vnd.company.order.v2+json
    @GetMapping(value = "/{orderId}",
                produces = "application/vnd.company.order.v2+json")
    ResponseEntity<OrderResponseV2> getOrderV2(@PathVariable UUID orderId) {
        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType("application/vnd.company.order.v2+json"))
            .body(mapToV2(orderService.getOrder(orderId)));
    }

    // Default: accept application/json → latest stable version
    @GetMapping(value = "/{orderId}",
                produces = MediaType.APPLICATION_JSON_VALUE)
    ResponseEntity<OrderResponseV2> getOrderDefault(@PathVariable UUID orderId) {
        // Default to current stable version
        return getOrderV2(orderId);
    }
}
```

**SemVer-based versioning for a service — internal vs external:**

```
RULE: Only MAJOR versions are public API versions (v1, v2, v3)
      MINOR and PATCH are internal implementation details

Example versioning lifecycle:
  1.0.0: initial release → /api/v1/ (public)
  1.1.0: add optional response field → /api/v1/ unchanged (backward compat, no new URL)
  1.2.0: add new endpoint → /api/v1/orders/batch (backward compat, new endpoint added)
  1.9.0: last v1 minor release
  2.0.0: BREAKING CHANGE (rename field) → /api/v2/ (new public version)
         /api/v1/ stays operational (deprecation period begins)
  2.0.0: Deprecation notice: "v1 EOL: 2025-12-31"
  2.1.0: add features to v2 only
  3.0.0: another breaking change → /api/v3/ added
         /api/v1/ removed (sunset date reached)
         /api/v2/ remains operational

GOVERNANCE:
  - Deprecation period: minimum 6 months for internal services, 12 months for external APIs
  - Sunset HTTP header: machine-readable deprecation signal
  - Migration guide: required before announcing deprecation
  - Consumer registry: know which consumers use which version
    (use API Gateway analytics or log parsing to identify v1 callers)
```

**Event versioning — Kafka topics:**

```
STRATEGY 1: Topic per version (clean isolation, but proliferates topics)
  order-placed.v1  → consumers using v1 Avro schema
  order-placed.v2  → consumers using v2 Avro schema
  Producer: publishes to BOTH topics during transition
  Consumers: each consumer subscribes to the version they're on
  After all consumers on v2: stop publishing to order-placed.v1

STRATEGY 2: Schema Registry with backward compat (single topic)
  Topic: order-placed
  v1 schema registered → consumers read v1
  v2 schema registered (backward compat: new optional field) → consumers transparently
    handle v2 events if using schema evolution:
    - New field: null for old events that don't have it
    - Old consumers: ignore new field (schema evolution built in)
  Schema Registry enforces: no breaking schema changes can be registered

STRATEGY 3: Envelope versioning
  Event payload includes version field:
    {"schemaVersion": "2", "orderId": "...", "newField": "..."}
  Consumer: switch on schemaVersion to determine parsing logic
  Disadvantage: manual version routing in every consumer
```

---

### ❓ Why Does This Exist (Why Before What)

Without a versioning strategy, the only options when breaking an API are: (1) update all consumers simultaneously (impossible in large orgs with many teams), (2) never break the API (severely limits evolution), (3) break the API and let consumers fail (unacceptable in production). Versioning strategy is the engineering process that enables the fourth option: break the API intentionally but safely, with notice, migration support, and time.

---

### 🧠 Mental Model / Analogy

> API versioning is like maintaining multiple editions of a software textbook. When you publish the 2nd Edition (v2) with restructured chapters (breaking change), you don't recall all copies of the 1st Edition. Libraries keep both editions. Students using the 1st Edition still have a valid book. New courses adopt the 2nd Edition. The 1st Edition is "deprecated" (not recommended for new students) but still available. Eventually, when no new library requests the 1st Edition, you stop printing it (sunset). Readers who depended on it get stranded only if they ignored the "1st Edition going out of print on this date" notice.

---

### ⚙️ How It Works (Mechanism)

**Consumer registry — knowing who uses what version:**

```bash
# API Gateway analytics: identify v1 callers before deprecating v1
# Kong: query request logs to find services still calling /api/v1/

kubectl exec -n kong deploy/kong-gateway -- \
  curl -s http://localhost:8001/routes/orders-v1/service/plugins/http-log/logs \
  | jq '[.[] | {consumer: .consumer.id, path: .request.url}] | group_by(.consumer)[] | {consumer: .[0].consumer, count: length}'

# Output:
# {"consumer": "inventory-service", "count": 14820}
# {"consumer": "payment-service", "count": 8891}
# → These two services still use v1. Cannot remove v1 until both migrate.

# Alternative: structured logging in the service itself:
@GetMapping("/v1/orders/{orderId}")
ResponseEntity<OrderResponseV1> getOrderV1(HttpServletRequest request, ...) {
    String callerService = request.getHeader("X-Service-Name");
    log.warn("Deprecated v1 API called by service={}, path={}", callerService, request.getRequestURI());
    // Structured log → aggregate in Grafana/Kibana → dashboard of v1 callers
    return ...;
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Backward Compatibility           API Gateway
(defines what changes are safe)  (routes traffic to version handlers)
        │                                │
        └──────────┬────────────────────┘
                   ▼
        Versioning Strategy  ◄──── (you are here)
        (manages v1/v2 lifecycle)
                   │
        ┌──────────┴──────────────┐
        ▼                         ▼
Service Contract             Feature Flags
(OpenAPI per version)        (feature flags can replace minor versions)
```

---

### 💻 Code Example

**Deprecation monitor — alert when consumer uses deprecated endpoint:**

```java
// Spring AOP: add deprecation warning headers to all v1 responses
@Aspect
@Component
class DeprecationHeaderAspect {

    @AfterReturning(
        pointcut = "execution(* com.example.order.controller.v1..*(..))",
        returning = "result"
    )
    void addDeprecationHeaders(JoinPoint joinPoint, Object result) {
        if (result instanceof ResponseEntity<?> response) {
            HttpServletResponse httpResponse =
                ((ServletRequestAttributes) RequestContextHolder.currentRequestAttributes())
                    .getResponse();
            httpResponse.setHeader("Deprecation", "true");
            httpResponse.setHeader("Sunset", "Sat, 31 Dec 2025 23:59:59 GMT");
            httpResponse.setHeader("Link",
                "<https://docs.example.com/api/migration-v1-to-v2>; rel=\"deprecation\"");
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                                                                                                               |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Semantic versioning means exposing all three numbers in the API URL | Only MAJOR versions are typically exposed in URLs (v1, v2). MINOR and PATCH changes are backward-compatible by definition and don't require URL changes. `GET /api/v1.2.3/orders` is an antipattern                                   |
| URL versioning pollutes the API with meaningless numbers            | URL versioning is preferred because: routes are explicit, easily visible in logs, directly navigable in browsers, and trivial to cache. The "clean URL" argument for header versioning trades discoverability for marginal aesthetics |
| You need to version every endpoint when you make a breaking change  | Only the changed endpoints need a new version. Unchanged endpoints can remain at v1. Consumers of unchanged endpoints don't need to update. Only consumers of the changed endpoint need to migrate to v2                              |
| Version parity: v1 and v2 should be the same codebase               | In practice, v1 and v2 may diverge significantly over time. As long as v1 consumers are migrating, it's acceptable for v1 to be a stable snapshot (potentially a separate service or deployment) and v2 to evolve                     |

---

### 🔥 Pitfalls in Production

**No consumer registry — sunset date surprise:**

```
SCENARIO:
  API versioning policy: v1 deprecated, sunset 6 months from now.
  Team confident: "We know our main consumers — they're already on v2."

  Sunset date: v1 removed from production.

  Immediately after removal:
  - Partner company's integration: 404 (they used v1 but were never identified)
  - Legacy batch job (runs monthly): 404 (doesn't show up in last 30 days of traffic)
  - Mobile app v3.2.1 (still deployed on 12% of devices): 404

  Root cause: No consumer registry. Assumptions replaced data.

PREVENTION:
  1. Build consumer registry BEFORE announcing deprecation:
     - API Gateway access logs: last 90 days of traffic → identify all callers
     - Mobile app: version analytics → what % of active users on what app version
     - Partner integrations: explicit registration (require header X-Client-Id)

  2. Deprecation announcement to specific consumers, not just documentation:
     - Email each identified team/partner with: migration guide + deadline + POC
     - Track acknowledgement

  3. Soft sunset testing:
     1 week before sunset: return 410 Gone for 1% of v1 traffic
     Monitor: any consumer that spikes errors → proactively reach out
     Ramp 410 to 100% over 1 week if no issues

  4. Emergency rollback plan:
     After sunset: keep v1 route in API Gateway but return 410 (not 404)
     "This endpoint was removed on DATE. Migration guide: <URL>"
     Monitor for 30 days after sunset → if critical consumer identified → temporarily re-enable
```

---

### 🔗 Related Keywords

- `Backward Compatibility` — the property versioning strategy is designed to preserve
- `API Gateway` — the routing layer that serves multiple API versions simultaneously
- `Service Contract` — the OpenAPI spec maintained per version
- `Feature Flags` — alternative to minor API versions for toggling behavior

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ APPROACHES   │ URL (/v1/, /v2/) — most common            │
│              │ Header (Accept: vnd.company.v2+json)       │
│              │ Query param (?version=2) — least preferred │
├──────────────┼───────────────────────────────────────────┤
│ SEMVER RULE  │ MAJOR = breaking → new URL version        │
│              │ MINOR = non-breaking → same URL version   │
│              │ PATCH = bugfix → same URL version         │
├──────────────┼───────────────────────────────────────────┤
│ LIFECYCLE    │ GA → Deprecated → Sunset (removed)        │
│ HEADERS      │ Deprecation: true, Sunset: <date>         │
│              │ Link: <migration-url>; rel="deprecation"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has been running v1 and v2 of the Order API for 8 months. The team wants to release v3 (another breaking change). v1 still has 2 remaining consumers that haven't migrated. v2 has 8 consumers, all current. Policy: maximum 2 concurrent major versions per service. Can you release v3 if v1 isn't fully sunset? Design the negotiation and escalation process you would follow, including technical mechanisms to enforce migration deadlines.

**Q2.** You have an event-driven service that publishes to a Kafka topic `order-events`. Two consumers: Consumer A uses v1 Avro schema, Consumer B recently migrated to v2 Avro schema. The v2 schema adds a new field (non-breaking per Avro BACKWARD compat rules). But your producer publishes to a single topic, and the Schema Registry uses subject `order-events-value`. A new developer proposes: "Let's register a v3 Avro schema that removes a field (the old `legacyStatus` field nobody uses anymore)." What happens to Consumer A, Consumer B, and new consumers if this v3 schema is registered? What Schema Registry compatibility mode prevents this from being registered?
