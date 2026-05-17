---
id: MSV-036
title: Strangler Fig Pattern
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-035, MSV-085, MSV-002
used_by: MSV-085, MSV-074
related: MSV-035, MSV-085, MSV-074, MSV-086, MSV-087, MSV-088
tags:
  - microservices
  - pattern
  - deep-dive
  - migration
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /microservices/strangler-fig-pattern/
---

# MSV-036 - Strangler Fig Pattern

⚡ TL;DR - Strangler Fig Pattern is a migration strategy
for incrementally replacing a legacy system with new
microservices. Named after a tropical tree that grows
around an existing tree and eventually replaces it.
Traffic is gradually redirected from legacy to new
service. At any time: rollback is possible (revert
traffic). When all traffic is on new services: legacy
is retired. The pattern makes large-scale migration
incremental, reversible, and low-risk.

| #036 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Anti-Corruption Layer, Monolith to Microservices Migration, Microservices Architecture | |
| **Used by:** | Monolith to Microservices Migration, Adapter Pattern in Microservices | |
| **Related:** | Anti-Corruption Layer, Monolith to Microservices Migration, Adapter Pattern in Microservices, On-Premises to Cloud Migration, Technology Migration Strategy, Re-platforming vs Re-architecting | |

---

### 🔥 The Problem This Solves

**THE BIG BANG REWRITE FAILURE:**
A company decides to rewrite their 10-year-old monolith
as microservices. "The Big Bang": shut down the monolith,
build 15 new services from scratch, go live on a single
day. 18 months of development. Launch day: critical
bug in order processing service. No rollback: the
monolith has been decommissioned. Entire company is
down. The rewrite took 18 months and the new system
has 40% of the features. This failure mode is so common
that "the Big Bang rewrite" is considered an anti-pattern.

Strangler Fig Pattern solves this: never stop the
monolith. Incrementally move capabilities to new services.
Traffic gradually redirects. At every point: if something
goes wrong, redirect traffic back to the monolith. When
100% of traffic is on new services: monolith is empty
and can be retired.

---

### 📘 Textbook Definition

**Strangler Fig Pattern** (Martin Fowler, 2004) is a
migration strategy where new functionality is built
next to legacy functionality, and traffic is gradually
redirected from legacy to new. Named after the Strangler
Fig tree that grows around an existing tree, using it
as support, and eventually replaces it. Key characteristics:
(1) Incremental: migrate one capability at a time.
(2) Reversible: traffic can be redirected back to
legacy. (3) Co-existence: legacy and new system run
simultaneously during migration. (4) Facade: a proxy/
gateway routes traffic between legacy and new.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Strangler Fig: build new services alongside the old
system, gradually move traffic to new, retire old when
all traffic has moved.

**One analogy:**
> Renovating a house while still living in it. You
> renovate one room at a time: build the new kitchen,
> move cooking to the new kitchen, demolish the old
> kitchen. Continue room by room. You never have a day
> without a place to sleep or eat. At the end: every
> room is renovated, the house still works throughout.
> Big Bang rewrite = tearing down the entire house,
> living in a tent for 18 months, then moving back in.

**One insight:**
The Strangler Fig Pattern's power is that it converts
a high-risk, irreversible change into a series of
low-risk, reversible changes. Each step: one feature
moves, traffic is redirected. If it fails: undo the
traffic redirect. The risk at any point = risk of one
feature, not risk of the entire system. This is why
Strangler Fig is the default recommendation for
legacy migration, not Big Bang rewrite.

---

### 🔩 First Principles Explanation

**THREE PHASES OF STRANGLER FIG:**

```
PHASE 1 - TRANSFORM (build alongside):
  New service built with same functionality as one
  monolith capability. New service tested.
  Monolith continues to handle all traffic.

PHASE 2 - CO-EXISTENCE (redirect traffic):
  Proxy/API Gateway: route X% of traffic to new service.
  Start with 5% (canary), increase to 50%, then 100%.
  Monitor: errors, latency, business metrics.
  Both systems handle traffic simultaneously.
  Rollback = change routing back to 0%.

PHASE 3 - ELIMINATE (retire legacy):
  100% traffic on new service. Legacy code for
  this feature is no longer called.
  Monitor for 30 days: no regressions.
  Remove legacy code path.
  
REPEAT: next feature/capability.
```

**ROUTING STRATEGIES:**

```
STRATEGY 1 - API GATEWAY ROUTING:
  Client -> API Gateway -> [rule] -> Legacy OR New
  Rule: path-based, header-based, user-based, percentage
  
  Example (Kong/nginx):
  /api/v1/orders -> legacy (100%)
  /api/v2/orders -> new order-service (100%)
  /api/orders    -> 10% new, 90% legacy (canary)

STRATEGY 2 - REQUEST MIRRORING:
  Client -> Proxy
  Proxy -> Legacy (primary, response returned to client)
  Proxy -> New service (shadow, response discarded)
  Compare responses: catch discrepancies before switch
  Used to validate new service without user impact

STRATEGY 3 - FEATURE FLAG ROUTING:
  if (featureFlag.enabled("new-order-service", userId))
      newOrderService.create(request);
  else
      legacyMonolith.createOrder(request);
  
  Gradual rollout: 1% -> 10% -> 100% by user percentage

STRATEGY 4 - DATA MIGRATION ROUTING:
  New users: new service
  Existing users: legacy until data migrated
  Migration: per-user background job
  When user's data migrated: route to new service
```

---

### 🧪 Thought Experiment

**STRANGLER FIG WITH SHARED DATABASE:**

```
PROBLEM:
  Legacy monolith: PostgreSQL database (shared)
  New order-service: must access same customer data
  
  Options:
  A) New service reads legacy DB directly
     Risk: tight coupling; DB schema changes break service
     Anti-pattern: violates Database per Service
  
  B) New service calls legacy API for customer data
     Risk: still depends on legacy; not truly independent
     Acceptable during transition only
  
  C) Anti-Corruption Layer: new service has its own DB
     Sync from legacy DB via CDC (Change Data Capture)
     New service reads from its own read model
     Risk: eventual consistency during transition
     Preferred: data isolation achieved during migration

STRANGLER FIG WITH DATABASE MIGRATION:
  Phase 1: New service + ACL calling legacy
           (temporary coupling, acknowledged)
  Phase 2: New service DB created; dual-write (legacy
           writes to both DBs via Outbox Pattern)
  Phase 3: New service reads from its own DB;
           legacy reads from legacy DB
  Phase 4: Stop legacy write to legacy DB column/table;
           New service is source of truth
  Phase 5: Remove legacy code path entirely
```

---

### 🧠 Mental Model / Analogy

> Strangler Fig is like a river diversion. The old
> river (monolith) carries all the water (traffic). You
> dig a new channel alongside it (new service). At first:
> a small gate diverts 5% of the water to the new channel
> (canary). The new channel is validated. Gate opens
> to 50%, then 100%. The old river dries up. The old
> channel is filled in (legacy retired). At every
> step: if the new channel has problems, close the gate.
> Water returns to old channel. Users (fish) never have
> a bad experience.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Strangler Fig means: build the new thing next to the
old thing, move a little traffic at a time, remove
the old thing when no traffic goes there. You never
have to stop everything and rebuild from scratch.

**Level 2 - How to use it (junior developer):**
In Spring Boot: add a feature flag. `if (featureFlags
.enabled("new-order-service")) -> call new service;
else -> call legacy`. Gradually increase percentage.
Monitor errors and business metrics after each increase.

**Level 3 - How it works (mid-level engineer):**
In Kubernetes + Istio: use traffic weighting.
`VirtualService` splits traffic by percentage between
old and new deployment. Start: 5% to new, 95% to old.
Monitor: Istio metrics (error rate, latency). Increase
weighting weekly. Feature flags for user-specific routing:
use LaunchDarkly or Unleash to target specific user
segments (beta users, internal users) to new service first.

**Level 4 - Why it was designed this way (senior/staff):**
Strangler Fig forces a discipline: the new service must
match the legacy contract exactly for the duration of
co-existence. This is where Contract-First and ACL matter:
the new service must pass all existing consumer tests.
If the legacy service's behavior is undocumented: this
is where the migration becomes difficult. The Strangler
Fig forces documentation: what does the legacy service
actually do? This "archaeology" is often the most
valuable part of the migration - it reveals implicit
behaviors that would have caused bugs in a Big Bang
rewrite.

**Level 5 - Mastery (distinguished engineer):**
Strangler Fig at data layer: the hardest part is data.
When the new service has its own database, data
consistency during the transition window is the core
challenge. CDC (Change Data Capture) via Debezium:
legacy DB changes are published as events. New service
consumes events and maintains a read replica of needed
legacy data. When ready to write: dual-write pattern
(new service writes to own DB; Outbox pattern publishes
change events to keep legacy in sync). This two-phase
data migration ensures neither service loses data during
transition. The data migration completion event triggers
the final traffic cutover.

---

### ⚙️ How It Works (Mechanism)

**ISTIO TRAFFIC WEIGHTING FOR STRANGLER FIG:**

```yaml
# VirtualService: route 10% to new, 90% to legacy
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: order-service
spec:
  http:
    - route:
        - destination:
            host: order-service-new  # new microservice
            port:
              number: 8080
          weight: 10  # 10% of traffic
        - destination:
            host: order-service-legacy  # legacy monolith
            port:
              number: 8080
          weight: 90  # 90% of traffic
---
# As confidence grows: update weights
# week 1: 10/90, week 2: 25/75, week 3: 50/50
# week 4: 75/25, week 5: 100/0
```

**FEATURE FLAG ROUTING (Spring Boot):**

```java
@Service
public class OrderRoutingService {

    private final FeatureFlagClient featureFlags;
    private final NewOrderService newOrderService;
    private final LegacyOrderClient legacyOrderClient;

    public OrderId createOrder(
            CustomerId customerId, List<CartItem> items,
            String userId) {
        // Gradually roll out to users by percentage
        if (featureFlags.isEnabled(
                "new-order-service", userId)) {
            // Route to new microservice
            return newOrderService.placeOrder(
                customerId, items);
        } else {
            // Route to legacy monolith
            return legacyOrderClient.createOrder(
                customerId, items);
        }
    }
}
// Flag starts at 0% (no users see new service)
// Gradually increase: 1%, 5%, 25%, 50%, 100%
// Monitor each step before increasing
```

---

### 🔄 The Complete Picture - End-to-End Flow

**STRANGLER FIG MIGRATION PLAN:**

```
LEGACY MONOLITH: handles Orders, Payments, Customers,
Inventory all in one codebase/DB

PHASE 1 - MIGRATION FACADE:
  Add API Gateway in front of monolith
  All requests still go to monolith
  Gateway provides routing capability
  Duration: 2 weeks

PHASE 2 - EXTRACT ORDER SERVICE:
  Build order-service (new) with full order capability
  Route 0% to new service (shadow testing only)
  Mirror requests: both services called, responses compared
  Duration: 4 weeks
  Success: response parity achieved

PHASE 3 - CANARY ROLLOUT:
  Route 5% to order-service
  Monitor: error rate, latency, order data consistency
  Increase: 5% -> 25% -> 50% -> 100%
  Duration: 4 weeks
  Rollback available at all times

PHASE 4 - LEGACY CLEANUP:
  0% traffic to legacy order code
  Monitor for 30 days: no regression
  Remove order code from monolith
  Update monolith DB: drop order tables (after backup)
  Duration: 2 weeks

REPEAT: next capability (Payments, then Inventory)
Total migration: 12-18 months for large monolith
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Big Bang vs Strangler Fig**

```java
// BAD: Big Bang approach - rewrite everything at once
// Plan: "Shut down monolith on Dec 31, new services live Jan 1"
// Reality:
// - New order-service has 60% of monolith's behavior
// - 40% of edge cases not discovered until go-live
// - No rollback possible (monolith decommissioned)
// - Full outage on Jan 1
// - 6 months of hotfixes
// This is the 'Big Bang rewrite anti-pattern'
```

```java
// GOOD: Strangler Fig - incremental, reversible
@Component
public class OrderFacade {

    @Value("${feature.new-order-service.percentage:0}")
    private int newServicePercentage;

    private final NewOrderService newService;
    private final LegacyMonolithClient legacyClient;
    private final MeterRegistry metrics;

    public Order createOrder(OrderRequest request) {
        boolean useNew = isEnabledForRequest(request);

        metrics.counter("order.routing",
            "destination", useNew ? "new" : "legacy").increment();

        if (useNew) {
            try {
                return newService.placeOrder(request);
            } catch (Exception e) {
                // Fallback to legacy on new service failure
                metrics.counter("order.routing.fallback").increment();
                log.error("New service failed, falling back", e);
                return legacyClient.createOrder(request);
            }
        }
        return legacyClient.createOrder(request);
    }

    private boolean isEnabledForRequest(OrderRequest req) {
        int hash = Math.abs(
            req.getUserId().hashCode() % 100);
        return hash < newServicePercentage;
    }
}
// Increase newServicePercentage via config/feature flag
// Rollback: set percentage to 0
```

---

### ⚖️ Comparison Table

| Approach | Risk | Rollback | Duration | Recommended |
|---|---|---|---|
| **Big Bang rewrite** | Very High | None | 18-36 months | Never |
| **Strangler Fig** | Low per step | Always possible | 12-24 months | Yes |
| **Branch by abstraction** | Medium | Partial | 6-18 months | Yes (internal refactor) |
| **Parallel run** | Low | Always | Long | Yes (validation) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strangler Fig requires microservices | Strangler Fig is a general migration pattern. It can migrate a monolith to microservices, migrate between cloud providers, or replace any legacy component. The core principle (build next to, redirect traffic, retire) is universal. |
| The facade/proxy is a long-term component | The facade (API Gateway, routing layer) is a migration artefact. It should be retired when migration is complete. Teams that keep the facade permanently create a new layer of complexity. |
| You must migrate entire features atomically | Strangler Fig supports sub-feature migration. "Reading orders" can migrate before "writing orders". Each migration step should be the smallest unit that can be independently tested and rolled back. |

---

### 🚨 Failure Modes & Diagnosis

**Data consistency issues during traffic split**

**Symptom:**
50% of traffic is on new order-service, 50% on legacy.
Customers who placed orders on legacy can't see them
in the mobile app (which routes to new order-service).
Orders created on new service occasionally show
incorrect total (different tax calculation than legacy).

**Root Cause:**
1. Data isolation: new service uses its own DB. Orders
   created in legacy are NOT replicated to new service DB.
   New service can't find them.
2. Business logic parity: tax calculation in new service
   differs slightly from legacy (different rounding mode).

**Diagnostic:**
```bash
# Check data gap
kubectl exec -it new-order-service-pod -- psql -c \
  'SELECT COUNT(*) FROM orders WHERE created_at > NOW()-1d'
# Compare with legacy order count for same window
# Significant difference = replication not working

# Check tax calculation discrepancy
# Shadow mode: run both, compare results
diff <(curl .../legacy/orders/123/total) \
     <(curl .../new-service/orders/123/total)
```

**Fix:**
1. Data gap: implement CDC from legacy DB to new service
   DB. All legacy orders replicated to new service.
2. Tax parity: run in shadow mode first (both calculate,
   compare, don't switch until parity achieved).
3. Routing consistency: hash by userId - user always
   goes to same system. Not 50/50 per request.
   `userId hash % 100 < threshold` -> consistent routing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Anti-Corruption Layer` - ACL is how the new service
  integrates with the legacy during co-existence
- `Monolith to Microservices Migration` - Strangler Fig
  is the primary pattern for this migration

**Applied In:**
- `Monolith to Microservices Migration` - the end-to-end
  migration guide uses Strangler Fig as the core pattern
- `Adapter Pattern in Microservices` - the routing
  facade is implemented as an adapter

**Related Migration Patterns:**
- `On-Premises to Cloud Migration` - Strangler Fig
  used for cloud migration too
- `Technology Migration Strategy` - Strangler Fig is
  one of several technology migration strategies
- `Re-platforming vs Re-architecting` - Strangler Fig
  is used for both

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PHASES       │ 1. Build new alongside legacy           │
│              │ 2. Route traffic % to new (canary)     │
│              │ 3. 100% on new; retire legacy           │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Response parity before traffic split    │
│              │ Data consistency during split           │
│              │ Consistent routing (hash, not random)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build next to, redirect traffic,        │
│              │  retire legacy - incremental migration" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Monolith to Microservices Migration     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Strangler Fig = incremental migration: build new
   alongside old, redirect traffic %, retire old. Never
   shut down the old system before the new is proven.
2. Routing: use consistent hashing (same user always
   goes to same system) not random (prevents split-brain).
3. Data consistency is the hardest part: CDC from legacy
   DB to new service DB during the co-existence window.

**Interview one-liner:**
"Strangler Fig Pattern migrates a legacy system incrementally:
build new services alongside the legacy, route traffic
gradually (5% -> 25% -> 100%) using API Gateway weight
or feature flags, monitor at each step, rollback if
needed. Key challenges: response parity (shadow mode
before split), data consistency (CDC replication during
co-existence), and consistent routing (hash by userId).
The alternative - Big Bang rewrite - is considered an
anti-pattern due to high risk and no rollback."

---

### 💡 The Surprising Truth

The most surprising aspect of Strangler Fig migrations:
the migration process often reveals that the monolith
was doing many undocumented things. When building
the new order-service to replace the monolith's order
code, teams discover: the monolith sends emails in
some obscure code path; there's a scheduled job that
cleaned up partial orders; there's a webhook to a
partner system that nobody documented. These discoveries
happen in the shadow testing phase (both systems run,
responses are compared). Shadow mode is not just a
testing technique - it's a legacy archaeology tool.
Every difference found in shadow mode is an undocumented
behavior that the Big Bang rewrite would have silently
dropped. Strangler Fig makes these discoveries safe
(the legacy is still running) rather than catastrophic
(the legacy is gone and the new service is broken).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **PLAN** Design a Strangler Fig migration plan for
   a specific monolith feature: identify phases, routing
   strategy, data migration approach, rollback procedure.
2. **IMPLEMENT** Build an OrderFacade that routes traffic
   by user percentage between legacy and new service,
   with fallback and metrics.
3. **MONITOR** Define the metrics and dashboards needed
   to validate each step of the traffic shift: error rate,
   latency p99, business metrics (order success rate).
4. **DATA** Design the data migration strategy for the
   co-existence window: CDC, dual-write, or read replica.
5. **SHADOW** Implement shadow mode: both services called,
   responses compared, discrepancies logged (not failed).

---

### 🧠 Think About This Before We Continue

**Q1.** You're migrating a shopping cart feature from
a legacy monolith to a new cart-service. The cart data
is stored in the monolith's PostgreSQL database. The
new cart-service uses Redis for cart storage. Design
the Strangler Fig migration plan specifically addressing:
how do carts created before the migration work in
the new service? How do you handle the transition window?

**Q2.** Shadow mode reveals that the new order-service's
tax calculation produces results that differ from the
legacy's by $0.01 on 0.3% of orders (due to different
rounding). The legacy has been in production for 10 years;
customers may have expectations. How do you resolve
this discrepancy? Does the new service match legacy
(wrong algorithm), or does it use the correct algorithm
(potentially breaking customer expectations)?

**Q3.** The Strangler Fig migration has been running for
6 months. 90% of traffic is on new services. But the
remaining 10% (old users, complex edge cases) has been
"stuck" on the legacy for 3 months. The team wants to
force 100% migration. What are the risks, and what
steps should be taken before forcing the final cutover?