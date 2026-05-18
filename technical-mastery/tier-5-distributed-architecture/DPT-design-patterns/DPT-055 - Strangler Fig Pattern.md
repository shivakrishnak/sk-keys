---
id: DPT-055
title: Strangler Fig Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005
used_by: DPT-064, DPT-065
related: DPT-052, DPT-054, DPT-058, DPT-059
tags:
  - pattern
  - architecture
  - advanced
  - migration
  - legacy
  - refactoring
  - incremental
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/design-patterns/strangler-fig/
---

⚡ TL;DR - The Strangler Fig Pattern migrates a legacy
system to a new architecture incrementally: new functionality
is built in the new system while old functionality is
gradually moved there, until the legacy system is
completely replaced with no big-bang cutover.

| #55 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-052, DPT-054, DPT-058, DPT-059 | |

---

### 🔥 The Problem This Solves

**THE MONOLITH DILEMMA:**
A 10-year-old Java EE monolith handles all business logic:
2 million lines of code, hundreds of modules, no unit
tests, deployed by the same process. The business needs
to move to microservices for independent scaling and
team autonomy. Options:

**Option A: Big Bang Rewrite**
Stop feature development for 18 months. Rewrite everything.
Deploy the new system. Throw away the old one.
Risk: massive cost and time. The new system may not
replicate all the subtle behaviors of the old one.
Business requirements change during the 18 months.
There is no rollback if the new system fails.

**Option B: Strangler Fig**
Build new functionality in the new system. Migrate old
functionality piece by piece. Both systems run in parallel.
Traffic is gradually shifted. Roll back any piece that
fails. Complete when the last piece is migrated.

**THE BOTANICAL ANALOGY (Martin Fowler, 2004):**
The strangler fig (Ficus watkinsiana) grows around a
host tree, eventually replacing it. The original tree
dies and rots away, leaving the fig tree as a hollow
trunk that supported itself on the old tree's structure.
The new system grows around the old system, using it
for support, until the old system is no longer needed.

---

### 📘 Textbook Definition

The **Strangler Fig Pattern** (coined by Martin Fowler)
is an approach to incrementally migrating a legacy system
to a new architecture. The migration proceeds via:

1. **Identify a seam**: find a piece of functionality
   that can be extracted independently.
2. **Build the replacement**: implement the functionality
   in the new system.
3. **Route traffic**: a facade (proxy, API gateway, or
   load balancer) routes requests for that functionality
   to the new system.
4. **Verify and stabilize**: monitor the new system
   handling the live traffic.
5. **Remove the legacy code**: once the new system is
   verified, remove the corresponding code from the
   legacy system.
6. **Repeat**: identify the next seam.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Strangler Fig = replace a legacy system by growing a
new system around it, piece by piece, until the old
one can be removed.

**One analogy:**
> Renovating a house while living in it. You don't
> demolish everything and camp outside for a year.
> You renovate one room at a time: move furniture to
> another room, renovate the room, move back, repeat.
> The house is always livable. The renovation is always
> in progress. Eventually: all rooms renovated,
> old fixtures gone, new house complete.

**One insight:**
The Strangler Fig transforms a high-risk big-bang
migration into a series of low-risk incremental changes.
Each piece migrated is verifiable and independently
roll-backable. The risk is bounded to the current piece
being migrated. The total migration risk is the sum
of N small risks, not one catastrophic big risk.

---

### 🔩 First Principles Explanation

**THE KEY MECHANISM: THE FACADE**
A routing facade sits in front of both systems. It
decides: "does this request go to the old system or
the new system?" Initially: all requests → old system.
As pieces are migrated: specific requests → new system.
Finally: all requests → new system. The facade is removed.

**FACADE OPTIONS:**
- API Gateway (Kong, AWS API Gateway): route by path,
  header, or query parameter.
- Nginx/HAProxy: route by URL path.
- Application-level BFF: a backend-for-frontend that
  calls either old or new service per capability.
- Feature flags: toggle routing at runtime.

**SEAM IDENTIFICATION:**
A "seam" is a piece of the legacy system that can be
extracted independently:
- Has a clear API boundary (called by a specific set
  of callers)
- Has manageable data dependencies (data can be
  migrated or shared)
- Has observable behavior (can be verified the new
  implementation matches)

**DATA MIGRATION CHALLENGE:**
The hardest part of Strangler Fig is usually data. The
new service needs its own data store. Options:
- Share the legacy database (synchronization concern)
- Replicate data from the legacy DB to the new DB
- Migrate data and use the new DB as the source of truth

---

### 🧪 Thought Experiment

**ORDER SYSTEM MIGRATION (6-month roadmap):**

**Month 1:** Build new Order Query Service (CQRS read side).
Route all dashboard queries to the new service.
Legacy still handles writes. Read queries: 30% migrated.

**Month 2:** Build new Order Search Service (Elasticsearch).
Route all search requests to the new service. Legacy
still handles writes and basic reads. Search: 100%
migrated.

**Month 3:** Build new Order Write Service.
Route new order creation to the new service.
Legacy still handles order updates. Writes: 30% migrated.

**Month 4-5:** Migrate remaining legacy write paths to
new service. Data migrated to new database. Legacy
handles zero new requests.

**Month 6:** Remove legacy order module from the monolith.
Decommission legacy database tables. Migration complete.

At no point: a big-bang cutover. At every point: rollback
possible by re-routing the facade.

---

### 🧠 Mental Model / Analogy

> Strangler Fig is "upgrade the ship while it sails."
> Naval ships require periodic overhauls (dry dock).
> Strangler Fig equivalent: replace one system at a time
> (propulsion, navigation, communication) while the ship
> is at sea. Each system is tested while the ship sails.
> When all systems are replaced: decommission the old ones.
> The ship never stopped sailing. The upgrade is continuous.
>
> Contrast with "dry dock rewrite": take the ship out
> of service for 18 months, refit completely, return
> to service. High risk. No revenue during refit.
> All problems discovered at launch.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Strangler Fig: migrate a legacy system step by step.
Build the new version of one piece. Route traffic to
the new piece. Verify it works. Remove the old piece.
Repeat until the legacy system is gone.

**Level 2 - The routing facade:**
The facade is the key enabler. Without a facade, switching
between old and new requires a cutover. With a facade:
routing is a configuration change. The facade is the
first thing to build when starting a Strangler Fig migration.

**Level 3 - Seam selection strategy:**
Start with the least risky seam (read-only functionality,
rarely changed, clear API). Build confidence in the
new system. Progress to higher-risk seams (writes,
complex business logic) after the team has practiced
the pattern.

**Level 4 - Data migration patterns:**
Three approaches:
1. **Shared DB (short term)**: new service reads/writes
   the legacy DB. No data migration required initially.
   Trade-off: tight coupling to legacy schema.
2. **DB synchronization**: CDC (Debezium) replicates
   changes from legacy DB to new DB. New service reads
   from new DB (eventually consistent copy).
3. **Swap**: new service writes to new DB, legacy DB
   is read-only. After verification: legacy DB decommissioned.

**Level 5 - Traffic management and feature flags:**
Advanced Strangler Fig uses traffic splitting at the
facade level: route 5% of traffic to the new system,
monitor error rates, route 100% when stable. Combined
with feature flags: individual users or tenants can
be in the new system before the full migration. This
is canary deployment at the system level.

---

### ⚙️ How It Works (Mechanism)

```
Strangler Fig Migration Progress
┌─────────────────────────────────────────────────────────┐
│ INITIAL STATE: All traffic → Legacy Monolith            │
│                                                         │
│   API Gateway → [Legacy Monolith]                       │
│                     /orders, /search, /payments, ...    │
│                                                         │
│ STEP 1: Migrate Search:                                 │
│   API Gateway → /search  → [New Search Service]         │
│              → (everything else) → [Legacy Monolith]   │
│                                                         │
│ STEP 2: Migrate Order Reads:                            │
│   API Gateway → /search  → [New Search Service]         │
│              → GET /orders* → [New Order Read Service]  │
│              → (everything else) → [Legacy Monolith]   │
│                                                         │
│ STEP 3: Migrate Order Writes:                           │
│   API Gateway → /search  → [New Search Service]         │
│              → GET /orders* → [New Order Read Service]  │
│              → POST/PUT /orders* → [New Order Write Svc]│
│              → (remaining) → [Legacy Monolith]          │
│                                                         │
│ FINAL STATE: Legacy decommissioned                      │
│   API Gateway → All traffic → [New Services]            │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - API Gateway routing facade (Nginx config):**

```nginx
# Nginx: Strangler Fig routing facade
# Route migrated functionality to new services
# Route everything else to legacy monolith

upstream legacy_monolith {
    server legacy.internal:8080;
}

upstream new_search_service {
    server search.internal:8080;
}

upstream new_order_service {
    server orders.internal:8080;
}

server {
    listen 80;

    # Step 1: Search migrated to new service
    location /api/orders/search {
        proxy_pass http://new_search_service;
    }

    # Step 2: Order reads migrated
    location ~ ^/api/orders/[^/]+$ {
        if ($request_method = GET) {
            proxy_pass http://new_order_service;
        }
        # Non-GET: still legacy
        proxy_pass http://legacy_monolith;
    }

    # Everything else: legacy monolith
    location / {
        proxy_pass http://legacy_monolith;
    }
}
```

**Example 2 - Application-level facade with feature flag:**

```java
// Application-level facade using feature flags for gradual rollout

@RestController
@RequestMapping("/api/orders")
class OrderFacadeController {

    @Autowired FeatureFlags featureFlags;
    @Autowired LegacyOrderClient legacyClient;  // old system
    @Autowired NewOrderService newOrderService;  // new system

    @GetMapping("/{id}")
    public OrderResponse getOrder(@PathVariable String id,
        Authentication auth) {

        // Feature flag: gradually migrate users to new service
        // e.g., 10% of requests, then 50%, then 100%
        if (featureFlags.isEnabled("new-order-service", auth)) {
            return newOrderService.getOrder(id);
        } else {
            return legacyClient.getOrder(id);
        }
    }

    @PostMapping
    public OrderResponse createOrder(@RequestBody OrderRequest req,
        Authentication auth) {

        if (featureFlags.isEnabled("new-order-creation", auth)) {
            return newOrderService.createOrder(req);
        } else {
            return legacyClient.createOrder(req);
        }
    }
}
// Flag 'new-order-service': enabled for 0% → 5% → 10% → 50% → 100%
// Rollback: set flag to 0% - instant return to legacy
```

---

### ⚖️ Comparison: Big Bang vs Strangler Fig

| Aspect | Big Bang Rewrite | Strangler Fig |
|---|---|---|
| Duration | Long (months/years) | Continuous (never fully "done") |
| Risk | Very high (all-or-nothing) | Low per step (bounded) |
| Rollback | None (no legacy) | Always (re-route via facade) |
| Business continuity | Disrupted | Continuous |
| Discovery of unknown requirements | All at end | Continuous per piece |
| Team learning | All at once | Incremental per piece |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strangler Fig is only for monolith-to-microservices | The pattern applies to any incremental system replacement: replacing a database, a service, a messaging system, a payment provider. Any system where big-bang replacement is too risky is a Strangler Fig candidate |
| The facade adds permanent overhead | The facade is temporary: removed when migration is complete. Some mature migrations replace the facade with direct service-to-service routing (or the facade becomes an API gateway that was always needed) |
| Strangler Fig is always better than a rewrite | For systems that are truly incapable of supporting a seam-based migration (e.g., deeply intertwined codebase with no identifiable seams), a bounded rewrite of the most painful module may be pragmatic. Strangler Fig requires identifiable seams |
| You can strangle any piece of functionality first | Start with low-risk, high-confidence pieces. Building the new system is the learning phase. Starting with the most complex, highest-risk module first builds risk into the beginning of the migration |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Incremental legacy replacement: one      │
│              │ seam at a time, always reversible        │
├──────────────┼──────────────────────────────────────────┤
│ FACADE       │ API Gateway or proxy routes to old or    │
│              │ new system per capability                │
├──────────────┼──────────────────────────────────────────┤
│ PROCESS      │ Identify seam → Build new → Route →      │
│              │ Verify → Remove legacy → Repeat         │
├──────────────┼──────────────────────────────────────────┤
│ VS BIG BANG  │ No big-bang risk; always reversible;     │
│              │ business continuity maintained           │
├──────────────┼──────────────────────────────────────────┤
│ HARDEST PART │ Data migration: shared DB → replicated   │
│              │ → migrated → legacy decommissioned       │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-056: Bulkhead Pattern                │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Strangler Fig: grow the new system around the old one,
   piece by piece. No big-bang. Build a routing facade
   first. Each migration step is independently reversible.
2. Seam first: identify the cleanest boundary in the
   legacy system. Migrate that seam first. The first
   migration teaches the team the pattern; subsequent
   ones go faster.
3. Data is the hard part. Three strategies: shared DB
   (coupling), CDC replication (eventual consistency),
   swap (new DB as primary). Plan the data strategy
   before each seam migration.

