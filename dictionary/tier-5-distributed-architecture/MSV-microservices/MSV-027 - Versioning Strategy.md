---
id: MSV-027
title: Versioning Strategy
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-026, MSV-029, MSV-012
used_by: MSV-071, MSV-070
related: MSV-026, MSV-029, MSV-071, MSV-070, MSV-061
tags:
  - microservices
  - api
  - intermediate
  - versioning
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /microservices/versioning-strategy/
---

# MSV-027 - Versioning Strategy

⚡ TL;DR - Versioning Strategy defines how a service
exposes multiple API versions simultaneously so that
consumers can migrate at their own pace when breaking
changes are required. The three main approaches are:
URL versioning (/v1/, /v2/), Header versioning
(Accept: application/vnd.api+json;version=2), and
Query param (?version=2). URL versioning is the most
widely adopted in REST microservices.

| #027 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Backward Compatibility, Contract-First API Design, API Gateway | |
| **Used by:** | API Evolution Strategy, Service Contract | |
| **Related:** | Backward Compatibility, Contract-First API Design, API Evolution Strategy, Service Contract, Consumer-Driven Contract Testing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Payment Service must change its API. The change is not
backward compatible: the `amount` field type changes
from cents (integer) to dollars (decimal). 15 consuming
services call this API. Without versioning: either
(a) force all 15 consumers to deploy simultaneously
(coordinated deployment, violates independence), or
(b) maintain separate service instances for old and
new API (operational nightmare - two services to deploy,
monitor, scale), or (c) embed if-else version branching
in the service code (unmaintainable technical debt).

**THE INVENTION MOMENT:**
Versioning Strategy solves this with a formal contract:
the service exposes v1 AND v2 simultaneously from the
same deployment. Old consumers call /v1/payments. New
consumers call /v2/payments. Old consumers migrate to
v2 on their own schedule. When all consumers have
migrated, v1 is deprecated and retired.

---

### 📘 Textbook Definition

**API Versioning Strategy** is the approach used to
identify and route client requests to the appropriate
version of a service's API, enabling multiple versions
to coexist simultaneously. The strategy governs: how
version identity is communicated (URL, header, parameter),
how long old versions remain supported (deprecation
policy), and how consumers are guided through migration.
Common approaches: (1) URL path versioning - /v1/endpoint,
/v2/endpoint; (2) Accept header versioning - `Accept:
application/vnd.company.v2+json`; (3) Custom header -
`X-API-Version: 2`; (4) Query parameter - `?version=2`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Versioning strategy is how you publish multiple versions
of your API so old and new consumers can both work
until everyone migrates.

**One analogy:**
> A building with multiple elevator shafts: Shaft 1
> (v1 API) takes passengers to floors 1-20. Shaft 2
> (v2 API) takes passengers to all floors with a faster
> motor. Both shafts run simultaneously. Old tenants
> continue using Shaft 1 until they choose to switch.
> Eventually Shaft 1 is decommissioned when no tenants
> use it. The building never needs to close while the
> transition happens.

**One insight:**
Versioning is the escape hatch for breaking changes.
The goal is to never NEED it by designing APIs to evolve
backward-compatibly (additive only). But when a true
breaking change is unavoidable, versioning makes it safe.
Most APIs that need v2, v3, v4 had design problems in v1.

---

### 🔩 First Principles Explanation

**FOUR VERSIONING APPROACHES:**

```
URL PATH VERSIONING (most common in REST):
  /api/v1/payments/{id}
  /api/v2/payments/{id}

  Pros:
    - Explicit: URL tells consumer exactly what they get
    - Easy to test in browser/curl
    - Cache-friendly (different URLs are different resources)
    - API Gateway routing: trivial (path prefix match)
  Cons:
    - Violates REST purity (version is not a resource property)
    - URL changes require consumer code changes
    - Can't version individual fields, only whole endpoints

  Industry adoption: ~85% of REST APIs (Stripe, GitHub,
  Twilio, AWS, etc. all use URL versioning)

HEADER VERSIONING (REST-pure approach):
  GET /payments/123
  Accept: application/vnd.company.payment.v2+json

  Pros:
    - URL remains stable
    - Correct REST semantics (same resource, different representation)
    - Fine-grained: can version individual resource types
  Cons:
    - Not testable in browser
    - Harder to cache (vary on Accept header)
    - More complex API Gateway routing rules
    - Consumers often forget the header (silent v1 fallback)

  Industry adoption: ~10% (GitHub Enterprise, some
  Netflix internal APIs)

QUERY PARAMETER VERSIONING:
  GET /payments/123?version=2
  GET /payments/123?v=2

  Pros: URL-based, easy to add without path change
  Cons: Cache-unfriendly, easy to omit, not idiomatic REST
  Industry: ~5% (some Google APIs)

GRPC / PROTOBUF VERSIONING:
  package company.payment.v1;
  package company.payment.v2;

  Separate package namespaces per version
  Server can register multiple service handlers
  Protobuf backward compatibility: preferred over versioning
```

**VERSION LIFECYCLE:**

```
STATES: current -> deprecated -> sunset (retired)

Version Support Policy example (Stripe model):
  - New version: current, fully supported
  - Breaking change needed: new version released,
    old version -> deprecated
  - Deprecation period: 12 months minimum
  - Sunset date: announced, set in response header:
    Deprecation: true
    Sunset: Sat, 31 Dec 2025 23:59:59 GMT
  - After sunset: v1 returns 410 Gone or redirects to v2
  - Consumer migration: tracked via analytics
    (still receiving v1 requests? identify that consumer)
```

---

### 🧪 Thought Experiment

**VERSIONING GRANULARITY - WHERE TO APPLY:**

```
Option A: Version the whole service
  http://payment-service/v1/ vs /v2/
  Pros: simple, clear boundary
  Cons: consumers calling ONE endpoint forced to upgrade
        all usage to access new endpoints

Option B: Version at endpoint level
  GET /v1/payments/{id} vs /v2/payments/{id}
  POST /payments (unchanged - no version needed)
  Pros: minimal disruption (only affected endpoints versioned)
  Cons: mixed version landscape confusing consumers

Option C: Version via content negotiation
  Same URL, different Accept headers
  Pros: cleanest REST model
  Cons: operational complexity

INDUSTRY RECOMMENDATION:
  URL versioning at API prefix level:
  /api/v1/... vs /api/v2/...
  Route at API Gateway:
    /api/v1/* -> payment-service:v1
    /api/v2/* -> payment-service:v2
  (same service binary with conditional logic,
   or separate deployment per version for isolation)
```

---

### 🧠 Mental Model / Analogy

> API versioning is like maintaining multiple product
> lines (iPhone 14 vs iPhone 15). Apple sells both
> simultaneously. iPhone 14 users get security updates
> (non-breaking patches) but don't get iPhone 15
> features. After 2-3 years, iPhone 14 is end-of-life
> (sunset). Apple doesn't force iPhone 14 users to buy
> iPhone 15 immediately; the transition is user-paced.
> But Apple DOES end support eventually - indefinite
> support is not sustainable. API versioning works
> identically: maintain, deprecate, sunset.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Versioning lets you offer a new version of your API while
keeping the old version running. Old users keep using v1.
New users use v2. You turn off v1 after enough time.

**Level 2 - How to use it (junior developer):**
In Spring Boot: add `/v1` and `/v2` path prefixes to
your controllers. Add `@Deprecated` annotation to v1
controllers. Implement the same operation in both
controllers (or delegate from v1 to v2 with translation).

**Level 3 - How it works (mid-level engineer):**
In a Spring Boot API Gateway (or Spring WebFlux with
routing): route /v1/* to the v1 controller, /v2/* to v2.
Deprecation: add a response header `Deprecation: true`
and `Sunset: <date>` to all v1 responses. Monitor v1
call volume via metrics (metric tag: api_version="v1").
Send deprecation emails when volume drops to zero for
a consumer.

**Level 4 - Why it was designed this way (senior/staff):**
Version strategy decisions should align with consumer
type. Public APIs (Stripe, Twilio): long deprecation
windows (12-24 months) because consumers have limited
ability to respond quickly. Internal microservices:
shorter windows (3-6 months) because teams can coordinate.
Schema versioning (Kafka Avro): different rules - Avro
schema evolution (add fields with defaults) is preferred
over topic versioning. Versioning adds operational cost;
use it only when backward compatibility is truly impossible.

**Level 5 - Mastery (distinguished engineer):**
The "semantic versioning for APIs" problem: adding an
optional field is a patch (safe), adding a new endpoint
is a minor (safe), making a breaking change is a major
(requires new version). But this mapping is imperfect:
a behavioural change (changing sort order, changing
default page size) may be syntactically a patch but
semantically a breaking change. Consumer-driven contract
tests bridge this gap: they encode consumer expectations
(including behaviour) as executable tests. A CI check
that runs all consumer contract tests against a new
version catches semantic breaking changes before deployment.

---

### ⚙️ How It Works (Mechanism)

**SPRING BOOT URL VERSIONING IMPLEMENTATION:**

```java
// V1 Controller (deprecated)
@RestController
@RequestMapping("/api/v1/payments")
@Deprecated
public class PaymentControllerV1 {

    private final PaymentControllerV2 v2Controller;

    @GetMapping("/{id}")
    public ResponseEntity<PaymentResponseV1> getPayment(
            @PathVariable Long id,
            HttpServletResponse response) {
        // Add deprecation headers
        response.setHeader(
            "Deprecation", "true");
        response.setHeader(
            "Sunset", "Sat, 31 Dec 2025 23:59:59 GMT");
        response.setHeader(
            "Link", "/api/v2/payments/" + id
            + "; rel=\"successor-version\"");

        // Delegate to v2 + transform response
        PaymentResponseV2 v2 =
            v2Controller.getPayment(id).getBody();
        return ResponseEntity.ok(
            PaymentResponseV1.from(v2));
    }
}

// V2 Controller (current)
@RestController
@RequestMapping("/api/v2/payments")
public class PaymentControllerV2 {

    @GetMapping("/{id}")
    public ResponseEntity<PaymentResponseV2> getPayment(
            @PathVariable Long id) {
        // ... implementation
    }
}
```

**VERSIONING IN OPENAPI SPEC:**

```yaml
openapi: '3.0.3'
info:
  title: Payment API
  version: '2.0'  # current API version
  description: |
    ## Versioning Policy
    This API supports the following versions:
    - **v2** (current): Use `/api/v2/`
    - **v1** (deprecated, sunset 2025-12-31): `/api/v1/`
paths:
  /api/v2/payments/{id}:
    get:
      operationId: getPaymentV2
      summary: Get payment by ID
      # ...
  /api/v1/payments/{id}:
    get:
      operationId: getPaymentV1
      deprecated: true  # OpenAPI deprecated flag
      summary: "[DEPRECATED] Get payment - use v2"
      description: |
        DEPRECATED: Use /api/v2/payments/{id} instead.
        This endpoint will be retired on 2025-12-31.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**VERSION MIGRATION WORKFLOW:**

```
1. IDENTIFY: Breaking change required in Payment API
   Cannot be made backward compatible

2. DESIGN: New v2 API contract
   - OpenAPI spec for v2 created
   - Consumer-driven contract tests updated for v2
   - Consumer teams notified: v2 coming, migration guide

3. IMPLEMENT: Both versions in same service
   /api/v1/payments - old implementation (unchanged)
   /api/v2/payments - new implementation
   v1 controller adds Deprecation + Sunset headers

4. RELEASE: v2 available, v1 still active
   Consumers can test v2 in staging
   No forced migration

5. MONITOR: Track v1 call volume per consumer
   Metric: http_requests_total{api_version="v1",
           consumer="order-service"}
   Dashboard shows migration progress

6. COMMUNICATE: Email consuming teams with v1 call volume
   "Order-service is still calling v1 (1200 req/day).
    Migration deadline: 2025-12-31."

7. SUNSET: After deadline, v1 returns 410 Gone
   Response body: {"error": "API v1 is retired.
    Please use /api/v2. Migration guide: <link>"}

8. RETIRE: Remove v1 code 6 months after sunset
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: no versioning for breaking change**

```java
// BAD: in-place breaking change, no versioning
@RestController
@RequestMapping("/api/payments")
public class PaymentController {
    // v1.0: returns {amount: 1000} (cents)
    // v2.0: returns {totalAmount: 10.00} (dollars)
    // All consumers calling /api/payments NOW break
    // No migration path, no deprecation window
    @GetMapping("/{id}")
    public PaymentResponse getPayment(@PathVariable Long id) {
        // This change immediately breaks all consumers
        return new PaymentResponse(payment.getTotalAmount());
    }
}
```

```java
// GOOD: URL versioning gives consumers migration window
// v1 kept, v2 added, deprecation headers signal migration
@RestController
@RequestMapping("/api/v1/payments")
public class PaymentControllerV1 {
    @GetMapping("/{id}")
    public ResponseEntity<PaymentResponseV1> getPayment(
            @PathVariable Long id,
            HttpServletResponse res) {
        res.addHeader("Deprecation", "true");
        res.addHeader("Sunset", "Sat, 31 Dec 2025 23:59:59 GMT");
        return ResponseEntity.ok(/* v1 response with amount cents */);
    }
}

@RestController
@RequestMapping("/api/v2/payments")
public class PaymentControllerV2 {
    @GetMapping("/{id}")
    public ResponseEntity<PaymentResponseV2> getPayment(
            @PathVariable Long id) {
        return ResponseEntity.ok(
            /* v2 response with totalAmount dollars */);
    }
}
// Old consumers: keep calling /api/v1, still works
// New consumers: call /api/v2, get new format
```

---

### ⚖️ Comparison Table

| Strategy | Pros | Cons | Best For |
|---|---|---|---|
| **URL versioning** | Explicit, cacheable, easy to test | URL changes, REST purity | REST APIs (most cases) |
| **Header versioning** | URL stable, REST-pure | Not browser-testable, complex routing | Hypermedia APIs |
| **Query param** | Easy to add | Cache-unfriendly, easy to omit | Legacy APIs only |
| **Content-Type** | Fine-grained | Complex Accept negotiation | Media-type rich APIs |
| **No versioning** | No overhead | Breaking changes require coordinated deploy | Private internal APIs with rapid consumer cycles |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More versions = more flexible | More versions = more maintenance burden. Each active version must be deployed, monitored, and secured. Many teams run v1-v5 simultaneously, paying 5x the operational cost. The real goal is to design APIs that rarely need new versions. |
| Version the service, not the API | Services are versioned by deployment (container image tag). APIs are versioned by the interface contract. These are independent: Payment Service v2.1.3 (deployment) can serve both /api/v1 and /api/v2 (API versions) from the same binary. |
| Never remove old API versions | Indefinite support is not viable. Old API versions must be maintained (security patches, bug fixes) indefinitely. Stripe maintains compatibility for many years but has an explicit end-of-life process. Without a sunset policy, technical debt accumulates. |

---

### 🚨 Failure Modes & Diagnosis

**v1 API still receiving traffic after sunset date**

**Symptom:**
Payment v1 was sunset 30 days ago. 3 services are still
calling it. The team decommissioned v1 code. Those
3 services are receiving 410 Gone responses. Error
rates spike in Order Service, Reporting Service, and
Notification Service.

**Root Cause:**
Incomplete consumer inventory. Team tracked consumers
that were known via service mesh telemetry. 3 services
used a shared HTTP client library that had the v1 URL
cached in config - not tracked in the service mesh
dashboard because they called from a batch job (not
real-time traffic, invisible to monitoring).

**Diagnostic:**
```bash
# Check who called v1 in the last 30 days
# (before decommission - in log storage)
grep '/api/v1/' /var/log/access.log | \
  awk '{print $1}' | sort | uniq -c
# Reveals: order-service-batch, reporting-job,
# notification-scheduler

# Or via API Gateway metrics
kubectl exec -it prometheus-pod -- \
  promtool query instant \
  'sum by (consumer) (http_requests_total{path=~"/api/v1/.*"})'
# Shows consumers that called v1 in the window
```

**Permanent Fix:**
1. Re-add v1 temporarily (rollback), extend sunset by 3 months
2. Implement mandatory consumer registration: consumers
   must declare version usage in service catalog
3. Add Sunset response header 6 months before sunset date
4. Set up alerting: "v1 API called after sunset - PagerDuty"
5. Test sunset: canary the 410 response before full cutover

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Backward Compatibility` - versioning is the mechanism
  for when backward compatibility is not possible
- `Contract-First API Design` - good contracts reduce the
  need for versioning

**Builds on this:**
- `API Evolution Strategy` - the end-to-end process for
  managing API lifecycle including versioning
- `Service Contract` - the formal contract that includes
  the versioning commitment

**Enforcement:**
- `Consumer-Driven Contract Testing` - validates that
  version changes don't break consumers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ URL VERSION  │ /api/v1/resource (old, deprecated)       │
│              │ /api/v2/resource (current)               │
├──────────────┼───────────────────────────────────────────┤
│ DEPRECATED   │ Header: Deprecation: true                │
│ HEADERS      │ Header: Sunset: <RFC 7231 date>          │
├──────────────┼───────────────────────────────────────────┤
│ LIFECYCLE    │ current -> deprecated -> sunset (410)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "URL versioning for breaking changes;     │
│              │  Deprecation header + 12-month window"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Evolution Strategy → Consumer Tests  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. URL versioning is the industry standard for REST APIs:
   /api/v1/ (old) coexists with /api/v2/ (new).
2. Deprecation headers tell consumers: `Deprecation: true`
   and `Sunset: <date>` in every v1 response.
3. Monitor consumer migration via API call metrics by version
   tag - don't retire v1 while any consumer is still calling it.

**Interview one-liner:**
"API versioning allows breaking changes without coordinated
deployment. URL versioning (/api/v1/, /api/v2/) is the
de-facto standard. v1 and v2 coexist in the same service
binary. Deprecation is signalled via `Deprecation: true`
and `Sunset` response headers. Migration tracked by metrics;
v1 retired after all consumers migrate. The goal is to
never need versioning by designing for backward compatibility,
but versioning is the safety net when that's impossible."

---

### 💡 The Surprising Truth

The companies with the most stable APIs (Stripe, Twilio,
AWS S3) rarely bump major versions. Stripe's original
API is still supported 15 years later. How? They combined
two strategies: (1) every API change is reviewed for
backward compatibility before release (internal tooling
flags potential breaking changes), and (2) when a breaking
change is essential, the new version is introduced as a
new endpoint alongside the old one (not just a new version
prefix). The lesson: versioning strategy is the last resort.
The primary investment should be in API design quality
that avoids breaking changes in the first place.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** URL versioning in Spring Boot with v1 and
   v2 controllers, where v1 delegates to v2 with a translation
   layer and adds deprecation response headers.
2. **MONITOR** Set up a Prometheus metric tagged with
   `api_version` and a Grafana dashboard showing per-consumer,
   per-version call volume to track migration progress.
3. **POLICY** Define a versioning policy: when a major version
   is required, minimum deprecation window, sunset process,
   and consumer notification procedure.
4. **DETECT** Implement openapi-diff in CI that fails the
   build when a change to the OpenAPI spec is detected as
   backward-incompatible, before it reaches consumers.
5. **SUNSETIFY** Implement the sunset process: add 410
   response with migration guide, implement graceful
   degradation for consumers that ignore the Sunset header.

---

### 🧠 Think About This Before We Continue

**Q1.** You have Payment Service with 20 consumers. You
need to make a breaking change to the core payment resource.
Design the complete versioning and migration strategy:
what do you implement, how do you communicate, how do you
track migration, and how do you determine when it's safe
to retire v1?

**Q2.** Your team argues for header versioning instead of
URL versioning because "it's more RESTful and keeps URLs
stable". Make the argument for URL versioning. What are
the operational, developer experience, and tooling reasons
that make URL versioning preferable for most teams?

**Q3.** Kafka message schema versioning is different from
REST API versioning. You have a Kafka topic with 3
consumers. You need to add a required field to the message
schema. REST APIs use URL versioning; what is the Kafka
equivalent, and what patterns (Avro schema evolution,
topic versioning, dual-write) do you use?