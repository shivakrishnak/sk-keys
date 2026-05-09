---
layout: default
title: "Strangler Fig"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /design-patterns/strangler-fig/
id: DPT-055
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - architecture
  - deep-dive
  - microservices
  - refactoring
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-055 - Strangler Fig

⚡ TL;DR - The Strangler Fig pattern incrementally replaces a legacy system by routing traffic to new code piece by piece until the old system is fully replaced - with zero big-bang rewrite.

| DPT-055 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Design Patterns, Strangler Fig Pattern, Microservices, Anti-Corruption Layer, Facade | |
| **Used by:** | Microservices, System Design, Legacy Migration, Refactoring | |
| **Related:** | Anti-Corruption Layer, Saga Pattern, Branch by Abstraction, Big Ball of Mud | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company has a 10-year-old monolith with 500k lines of code. The CTO wants to move to microservices. Two paths exist: (1) Big-bang rewrite - stop feature development for 18 months, rewrite everything, deploy the new system on a specific date. Risk: the new system has untested behaviour, the old system continued to grow during the rewrite, and the date slips. This approach has a well-documented failure rate. (2) Do nothing - the monolith continues to slow down the organisation until it is no longer tenable.

**THE BREAKING POINT:**
Every legacy migration faces the same dilemma: the old system is too risky to rewrite in one shot, but incremental transformation seems impossible because the codebase is tangled. "We can't refactor this while the plane is in flight."

**THE INVENTION MOMENT:**
Martin Fowler named the Strangler Fig pattern after the strangler fig tree, which grows around a host tree using it as a scaffold, eventually replacing it entirely. Applied to software: a new system grows around the legacy system, routing increasing traffic to the new code, until the legacy system is no longer needed and can be removed - incrementally, safely, with zero big-bang.

**EVOLUTION:**
Strangler Fig Pattern was coined by Martin Fowler in 2004,
inspired by the strangler fig tree that grows around a host tree
and eventually replaces it. It gained prominence with the
microservices movement (2014-2018) as the standard approach
to decomposing monolithic applications incrementally. Netflix,
Amazon, and Uber publicly documented their Strangler Fig
migrations. Sam Newman's "Building Microservices" (2015) and
"Monolith to Microservices" (2019) formalised the pattern with
detailed migration strategies. The Pattern is now considered
the safest known approach to legacy system modernisation in
production environments.

---

### 📘 Textbook Definition

The Strangler Fig pattern is an incremental modernisation strategy in which a new system is built alongside the existing legacy system. A routing layer (facade or proxy) intercepts all incoming requests. As specific features or modules are reimplemented in the new system, the route for those requests is changed to point to the new implementation. The legacy system continues to handle all other requests. The process continues until all routes are migrated and the legacy system can be decommissioned.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Replace a legacy system by rerouting one feature at a time to new code until nothing routes to the old system.

**One analogy:**
> The strangler fig tree (Ficus aurea) wraps its roots around a host tree, growing slowly upward using the host as a scaffold. Over years, the fig entirely encloses the host, which eventually decomposes - leaving only the successful fig. The fig never kills the host abruptly; it simply grows around it. Legacy migrations work the same way: build around the old system, until the old system is no longer needed.

**One insight:**
The key is the routing layer. Without a facade or proxy that can reroute requests dynamically, gradual migration is impossible - all traffic hits the same endpoint. The routing layer decouples "which system handles this request" from "who the client calls."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Both the old and new systems must coexist during migration - there is no "cutover" date; the transition is gradual.
2. A routing layer intercepts all requests and directs them to either the legacy or new system - clients see no change.
3. Migration proceeds feature by feature - each feature migrated reduces the routing to the legacy system until it is zero.

**DERIVED DESIGN:**
The routing layer is the core technology enabler. It can be: an API Gateway (AWS API Gateway, Kong, nginx) that routes by path prefix; an HTTP proxy (nginx `upstream` config); a feature-flag-controlled service facade; or a message router in event-driven systems. The routing layer must be centrally configurable so traffic can be shifted without redeployment.

The data migration strategy is the hardest part: if new and old features share data, they cannot simply coexist without a data synchronisation layer. Two approaches: (1) Dual-write - new system writes to both old and new data stores; (2) CDC - Change Data Capture syncs data between old and new stores. Until the old system is decommissioned, data must be consistent across both.

**THE TRADE-OFFS:**
**Gain:** Zero big-bang risk; continuous delivery during migration; each migrated feature is independently testable; easy rollback (revert routing).
**Cost:** Both systems run in parallel (operational overhead); data synchronisation complexity; routing layer is a new single point of failure.

---

### 🧪 Thought Experiment

**SETUP:**
A monolith handles user authentication, product catalogue, and order management. The team wants to extract order management as a microservice.

**WHAT HAPPENS with big-bang rewrite:**
Team estimates 6 months for the rewrite. 8 months in, the new order service handles basic cases but misses 15 edge cases that emerged from the monolith's behaviour. The monolith has received 200 bug fixes during the 8 months. The team cannot confidently cut over. Project extended by 4 months. Total: 12 months, still not production-ready.

**WHAT HAPPENS with Strangler Fig:**
Month 1: A routing proxy is set up. All traffic routes to the monolith. No user-visible change. Month 2: "Create order" endpoint migrated. Proxy routes POST /orders to new order service. Rollback takes 5 minutes (revert proxy config). Month 3: "List orders" migrated. Month 4: "Order details" migrated. Month 5: "Cancel order" migrated. Month 6: No routes remain to monolith order module. Monolith module deleted. Users were never disrupted.

**THE INSIGHT:**
Strangler Fig decomposes risk. Each migration step is independently reversible. No step risks the entire system. The accumulated improvements are identical - but achieved in smaller, safer, reviewable increments.

---

### 🧠 Mental Model / Analogy

> Think of replacing the floors in a house while still living in it. You replace one room at a time: the bathroom first (vacate it temporarily, replace it, move back in), then the kitchen, then the living room. You never vacate the entire house. At no point is there no floor. The Strangler Fig is that renovation - one room (feature) at a time, while the household (system) continues to function.

- "The old floor" → the legacy system
- "The new floor (one room)" → the new microservice for one feature
- "Vacating one room temporarily" → routing that feature's traffic to the new service
- "Full renovation complete" → all features migrated, legacy decommissioned
- "Living in it throughout" → system remains available to users throughout

Where this analogy breaks down: when renovating a house, each room is independent. In a legacy migration, features often share data - the "floor" of one room is connected to the adjacent room. Data coupling is the hardest problem the analogy underrepresents.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The Strangler Fig is a migration strategy where you replace a legacy system one piece at a time, not all at once. You redirect traffic to a new system piece by piece, until the old system has no traffic and can be turned off safely.

**Level 2 - How to use it (junior developer):**
Start by identifying the migration boundary: which feature or API path will you migrate first? It should be: (1) well-defined (clear inputs/outputs), (2) relatively isolated (minimal dependencies on other legacy features), and (3) high-value (moving it demonstrates value quickly). Then: create the routing layer (API Gateway, nginx, or an application-level facade), implement the feature in the new service, test it thoroughly, change the routing rule, monitor. If metrics are healthy, keep the new routing. If not, revert.

**Level 3 - How it works (mid-level engineer):**
Routing strategies: (1) **Path-based routing**: `/api/v2/orders` → new service, `/api/orders` → legacy (clients gradually migrated to v2). (2) **Traffic splitting**: 5% → new, 95% → legacy (canary deployment style - validate before full migration). (3) **User-cohort routing**: specific users (beta group) → new service, all others → legacy. Data consistency: during migration, the new service must read from the legacy data store or have a synchronised copy. Write strategies: dual-write (both stores updated) or CDC (legacy changes replicated to new store). The Anti-Corruption Layer (ACL) - an adapter between the legacy and new data models - prevents the legacy data model from leaking into the new service's design.

**Level 4 - Why it was designed this way (senior/staff):**
The Strangler Fig is ultimately a risk management pattern. It converts a single large deployment risk (big-bang rewrite) into N small deployment risks (one per migrated feature). Each small risk is reversible within minutes. The aggregated risk is far lower. At the organisational level, the Strangler Fig allows the new system's team to operate independently while the legacy team continues to maintain the old system. This is a critical organisational enabler for large organisations where a monolith is owned by multiple teams. The pattern also produces an incremental business case: each migrated feature is a demonstrable improvement, enabling continued investment justification. The final challenge is the long tail: the last 20% of the legacy system is typically the most complex, most entangled, and least understood. This is where the Strangler Fig project often slows or stalls. Addressing this requires explicit prioritisation of the hard cases, not just the easy wins.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  STRANGLER FIG MIGRATION PHASES                      │
│                                                      │
│  Phase 1: Routing Layer Added                        │
│                                                      │
│  Client → [Proxy/Gateway] → Legacy (100% traffic)   │
│                                                      │
│  Phase 2: First Feature Migrated                     │
│                                                      │
│  Client → [Proxy/Gateway]                            │
│            ├─ POST /orders → New Service             │
│            └─ * → Legacy                            │
│                                                      │
│  Phase 3: Incremental Migration (n features done)    │
│                                                      │
│  Client → [Proxy/Gateway]                            │
│            ├─ /orders/* → New Service               │
│            ├─ /products/* → New Service             │
│            └─ * → Legacy                            │
│                                                      │
│  Phase N: Legacy Decommissioned                      │
│                                                      │
│  Client → [Proxy/Gateway] → New System (100%)       │
│           (Legacy removed)                           │
└──────────────────────────────────────────────────────┘
```

**Setting up routing (nginx example):**

```nginx
# nginx.conf - Strangler Fig routing
upstream legacy { server legacy-app:8080; }
upstream orders_service { server orders:8081; }
upstream products_service { server products:8082; }

server {
    location /api/orders {
        # Migrated: route to new orders microservice
        proxy_pass http://orders_service;
    }
    location /api/products {
        # Migrated: route to new products microservice
        proxy_pass http://products_service;
    }
    location / {
        # Everything else: still legacy
        proxy_pass http://legacy;
    }
}
# Migration progress is visible in this config file.
# Rollback: comment out one location block.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client → POST /api/orders
  → API Gateway / Proxy [← YOU ARE HERE: routing decision]
  → Is /api/orders migrated?
    → YES: route to OrdersMicroservice
    → NO: route to Legacy

Client receives response
  → Transparently from new or legacy service
  → Client is unaware of which system handled it
```

**FAILURE PATH:**
```
New service has a bug after routing change
  → Error rate increases
  → Monitoring alert fires (5xx spike)
  → Revert routing rule in proxy
    (5-minute operation)
  → Traffic returns to legacy
  → Bug fixed in new service
  → Re-migrated when ready
```

**WHAT CHANGES AT SCALE:**
At 100 routes, the routing layer is a simple nginx config or API Gateway rule set. At 1,000 routes, it requires programmatic management (service mesh, API Gateway SDKs). At 10,000 endpoints, feature-flag-driven routing is necessary - each route is a feature flag, managed via a feature flag platform (LaunchDarkly, Unleash).

---

### 💻 Code Example

**Example 1 - Application-level facade (API facade pattern):**

```java
// API Facade that routes based on feature flag
@RestController
@RequestMapping("/api/orders")
public class OrdersFacadeController {
    private final LegacyOrderService legacy;
    private final NewOrdersClient newService;
    private final FeatureFlags flags;

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @RequestBody CreateOrderRequest req) {
        if (flags.isEnabled("new-orders-service",
                req.userId())) {
            // Route to new microservice
            return newService.createOrder(req);
        }
        // Route to legacy (inline call or HTTP)
        return legacy.createOrder(req);
    }
}
// Rollback: set feature flag to disabled (seconds)
// Canary: enable for 5% of users initially
```

**Example 2 - Data sync during migration:**

```java
// During migration: dual-write to both stores
// Ensures legacy and new service data stays in sync
@Service
public class DualWriteOrderRepository {
    private final LegacyOrderDao legacyDao;     // old DB
    private final NewOrderRepository newRepo;   // new DB

    @Transactional
    public Order save(Order order) {
        // Write to new store first
        newRepo.save(order);
        // Write to legacy store (may be different schema)
        legacyDao.insert(OrderMapper.toLegacy(order));
        return order;
    }
}
// Once migration complete: remove legacyDao.insert()
// Simplifies to just newRepo.save()
```

---

### ⚖️ Comparison Table

| Approach | Risk | Duration | User Impact | Rollback |
|---|---|---|---|---|
| **Strangler Fig** | Low | Months-years | None | Immediate (reroute) |
| Big-Bang Rewrite | Very High | 6-24 months | High on cutover | Very difficult |
| Branch by Abstraction | Low | Weeks-months | None | Easy |
| Lift and Shift | Low-Medium | Days-weeks | None | Easy |

How to choose: Strangler Fig is the default for large legacy systems where behaviour correctness is critical. Branch by Abstraction is better within a single codebase without external routing. Big-bang rewrite is almost never the right choice.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strangler Fig requires rewriting the whole system | The pattern is specifically designed to allow selective migration - only migrate features that provide value when migrated |
| The routing layer adds latency | An API Gateway or nginx proxy adds 1-5ms latency - negligible for most services, and no worse than the legacy system's existing overhead |
| Legacy data must be migrated first | Data migration is incremental too - new and legacy stores coexist with synchronisation during the migration period |
| Once migrated, a feature cannot revert to legacy | The routing layer makes reversion trivial - change the routing rule, the legacy code still exists until explicitly decommissioned |

---

### 🚨 Failure Modes & Diagnosis

**1. Data Divergence Between Legacy and New Service**

**Symptom:** Feature migrated to new service; users see different data depending on which system they hit (A/B or canary traffic split). Inconsistent order history.

**Root Cause:** Dual-write is not atomic. New service write succeeds, legacy write fails (or vice versa). Stores diverge.

**Diagnostic:**
```bash
# Compare record count in both stores:
psql -c "SELECT COUNT(*) FROM legacy.orders
  WHERE created_at > NOW() - INTERVAL '1 hour'"
psql -h new-db -c "SELECT COUNT(*) FROM orders
  WHERE created_at > NOW() - INTERVAL '1 hour'"
# Count difference > 0 = divergence
```

**Fix:** Use a CDC-based sync (Debezium) rather than dual-write for consistency. Or: make the legacy store the source of truth and sync to the new store - not the other way around.

**Prevention:** Never use dual-write without an idempotency check and divergence monitoring.

---

**2. Routing Layer Becomes a Single Point of Failure**

**Symptom:** Proxy/gateway crashes; all traffic (to both new and legacy) is disrupted - more total failure than pre-migration.

**Root Cause:** The routing layer was added as a single instance without high availability configuration.

**Diagnostic:**
```bash
# Check proxy health:
kubectl get pods -l app=api-gateway
# Restart count > 5 = unstable
kubectl describe pod api-gateway-xxx | grep Restart
```

**Fix:** Deploy the routing layer with multiple replicas and health checks. The routing layer must have higher availability SLA than either the legacy or new service.

**Prevention:** The routing layer must be highly available before any migration begins. Never start migration with a single-instance proxy.

---

**3. Migration Stalls at the Long Tail**

**Symptom:** 80% of features migrated but migration effort stalls - remaining 20% is complex and nobody wants to tackle it.

**Root Cause:** Legacy long-tail features are typically the most complex, least understood, and most tangled. They were migrated last because they were avoided first.

**Diagnostic:**
```bash
# Check route migration progress:
curl http://api-gateway/admin/routes \
  | jq '[.[] | select(.backend=="legacy")] | length'
# Monitor this number monthly - should decrease
```

**Fix:** Explicitly schedule the long-tail features as engineering investment, not as part of regular feature work. Create a dedicated migration team or allocate 20% of engineer time to migration exclusively.

**Prevention:** Track migration progress as a metric. Set a decommission date for the legacy system (with organizational commitment) to force completion of the long tail.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Anti-Corruption Layer` - the adapter pattern that prevents the legacy system's data model from corrupting the new system's design during migration
- `Facade` - the structural pattern underpinning the routing layer in the Strangler Fig; the facade hides which system is handling the request

**Builds On This (learn these next):**
- `Branch by Abstraction` - an alternative incremental migration approach used within a single codebase; complementary to Strangler Fig for components that cannot be extracted via an API boundary
- `Canary Deployment` - the traffic-splitting technique used in Strangler Fig to validate new service behaviour before full migration

**Alternatives / Comparisons:**
- `Big-Bang Rewrite` - the high-risk alternative that Strangler Fig replaces; rewrites are occasionally justified when the legacy codebase is not safely operable but carry high risk
- `Lift and Shift` - moving existing code to a new platform without rewriting; faster than Strangler Fig but does not address the underlying code quality problem

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Route traffic to new code incrementally  │
│              │ until legacy has no traffic left          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Legacy systems cannot be safely replaced  │
│ SOLVES       │ in one big-bang migration                 │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The routing layer is the core enabler -   │
│              │ without it, incremental migration is      │
│              │ impossible. Build it first.               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Replacing a legacy system that must       │
│              │ remain available throughout migration     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Legacy system is unsafe to run even       │
│              │ temporarily (security, compliance);       │
│              │ migration must be instantaneous           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Incremental safety + rollback vs.         │
│              │ operational complexity of running two     │
│              │ systems simultaneously                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Grow the new system around the old one - │
│              │  until the old one can be safely removed."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Anti-Corruption Layer → Branch by         │
│              │ Abstraction → Feature Flags → Canary      │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Migrate a legacy system by building the replacement alongside it,
routing traffic incrementally from old to new, and removing
the old system only after the new system has absorbed all
its traffic. Never perform a "big bang" cutover.

**Where else this pattern appears:**
- **Database schema migration (expand-contract):** Add new
  columns/tables (expand), migrate data to them, update code
  to use new structure, remove old structure (contract) --
  the Strangler Fig pattern applied to database evolution.
- **Infrastructure blue-green deployment:** New infrastructure
  is built ("green") while old continues running ("blue");
  traffic is shifted from blue to green incrementally.
- **Feature flag rollouts:** New feature code coexists with old
  code behind a flag; traffic is incrementally shifted to the
  new path; old code is removed when migration is complete.

---

### 💡 The Surprising Truth

Martin Fowler's original Strangler Fig article (2004) described
the pattern for migrating to a new website, not for
microservices decomposition. The microservices community adopted
it wholesale as a legacy decomposition strategy -- a perfectly
valid application, but one Fowler did not anticipate. The
irony: the original motivation (website migration) is now
considered the simpler use case. The microservices application
(migrating from a monolith to distributed services) is
significantly more complex because it involves not just routing
but also data migration, distributed transaction handling,
and service boundary definition -- problems invisible in
the original website migration scenario.
---

### 🧠 Think About This Before We Continue

**Q1.** A Strangler Fig migration is 70% complete (7 of 10 modules migrated). The new system is in production and healthy. The remaining 3 modules (authentication, billing, and admin) are deeply entangled with the legacy data model and share state with the 7 migrated modules. The CTO is considering stopping the migration at 70% and running both systems indefinitely. What is the engineering cost of stopping at 70% vs. completing the final 30%, and what criteria would you use to decide whether to proceed or plateau?

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A team uses the Strangler Fig to migrate a monolith to microservices. After 6 months, 5 services have been extracted successfully. A post-migration review shows that the routing layer (nginx) is handling 15,000 requests/second and has become the most critical component in the system - any change to it requires extensive testing. The routing layer has itself become a legacy bottleneck. Design the Strangler Fig for the routing layer itself: how would you incrementally replace the monolithic routing layer with a more distributed approach?



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A team is strangling a monolith's
`OrderManagement` module into a new `OrderService`. They use
an API gateway to route 5% of order creation traffic to
the new service. The new service uses a separate database.
After two weeks, they discover 15 orders are duplicated --
both the monolith and the new service processed the same
order IDs. Trace the root cause and describe the structural
changes needed before increasing traffic beyond 5%.

*Hint: The Failure Modes section covers data consistency during
migration. The duplicate ID issue arises from shared state
(the order ID sequence or database) being split -- the two
services need a coordination mechanism during the migration.*
