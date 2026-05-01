---
layout: default
title: "Strangler Fig Pattern"
parent: "Microservices"
nav_order: 634
permalink: /microservices/strangler-fig-pattern/
number: "634"
category: Microservices
difficulty: ★★★
depends_on: "Monolith vs Microservices, Anti-Corruption Layer, Service Decomposition"
used_by: "Service Decomposition, Modular Monolith"
tags: #advanced, #architecture, #microservices, #pattern
---

# 634 — Strangler Fig Pattern

`#advanced` `#architecture` `#microservices` `#pattern`

⚡ TL;DR — The **Strangler Fig Pattern** is an incremental migration strategy: new microservices are built alongside an existing monolith, gradually taking over functionality piece by piece via a proxy/façade. The monolith is "strangled" until it can be decommissioned without a big-bang rewrite.

| #634            | Category: Microservices                                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Monolith vs Microservices, Anti-Corruption Layer, Service Decomposition |                 |
| **Used by:**    | Service Decomposition, Modular Monolith                                 |                 |

---

### 📘 Textbook Definition

The **Strangler Fig Pattern** (Martin Fowler, 2004) is a software migration technique for incrementally replacing a legacy system by building the new system alongside the old one, gradually routing functionality from the old to the new, until the old system can be decommissioned. Named after the Strangler Fig tree that grows around a host tree and eventually replaces it. The pattern requires a **Façade** (typically an API Gateway, reverse proxy, or feature flag mechanism) that intercepts all requests and routes them either to the legacy system or to the new services based on which functionality has been migrated. Migration proceeds in small, reversible steps: identify a well-bounded piece of functionality → extract it as a new service → test the new service in parallel → route traffic to the new service → remove the functionality from the legacy system → repeat. An Anti-Corruption Layer bridges the data and model differences between the legacy system and the new service during the transition period.

---

### 🟢 Simple Definition (Easy)

The Strangler Fig Pattern means: instead of rewriting everything at once, you build the new system piece by piece next to the old one. A proxy decides which parts go to the new system and which still go to the old one. When everything is migrated, you shut down the old system.

---

### 🔵 Simple Definition (Elaborated)

Rewriting an entire monolith at once (the "big bang" rewrite) is extremely risky: it takes months or years, the new system has no production track record, and teams must maintain two systems in parallel anyway. The Strangler Fig approach reduces risk by making migration incremental: extract the "Customer Profile" feature as a new service this month, redirect all Customer Profile requests to the new service, confirm it works in production, then move on to the next feature. At every step, you can roll back by redirecting traffic back to the old system. The monolith shrinks gradually until it handles nothing and can be switched off.

---

### 🔩 First Principles Explanation

**The four phases of Strangler Fig migration:**

```
PHASE 1: FAÇADE INSTALLATION
  All traffic still goes to monolith.
  Install a proxy/API Gateway in front of the monolith.
  No behaviour change — this is purely infrastructure.

  [Client] → [Proxy (pass-through)] → [Monolith]
  Risk: minimal. Roll-back: remove proxy.

PHASE 2: NEW SERVICE CREATION (SHADOW MODE)
  Build the new service alongside the monolith.
  Optionally: shadow traffic (send duplicate requests to new service, discard response).
  Compare new service output with monolith output to verify correctness.

  [Client] → [Proxy] → [Monolith] (response served to client)
                   ↘ → [New Service] (shadow: response discarded, just for testing)

PHASE 3: TRAFFIC MIGRATION
  Route a subset of traffic to the new service.
  Canary: 1% → new service, 99% → monolith.
  Monitor error rates, latency, correctness.
  Gradually increase: 10% → 50% → 100%.

  [Client] → [Proxy] → 99% → [Monolith]
                   → 1%  → [New Service]

PHASE 4: MONOLITH DECOMMISSION (for this feature)
  100% traffic routed to new service.
  Remove corresponding code from monolith (don't leave dead code).
  Proxy routing rule updated/removed.
  Repeat for next feature.

  [Client] → [Proxy] → [New Service]  (monolith feature removed)
```

**Data migration during Strangler Fig:**

```
THE DATA PROBLEM:
  Monolith and new service need access to the SAME data during transition.
  You cannot do a one-time data migration if the monolith is still writing.

APPROACH 1: NEW SERVICE READS FROM MONOLITH DATABASE (via ACL)
  New service doesn't have its own DB yet.
  It reads from (and writes to) the monolith's DB via an Anti-Corruption Layer.
  Risk: new service is still coupled to legacy schema.
  When migration complete: extract the data to new service's DB, add sync.

APPROACH 2: DUAL WRITE (both old and new service write to both DBs)
  During migration: monolith writes to legacy DB + new service's DB.
  New service reads from its own DB.
  After migration: monolith stops writing to new DB; new service is sole writer.
  Risk: dual write consistency, data drift.

APPROACH 3: EVENT-DRIVEN SYNC (CDC)
  Change Data Capture (Debezium) captures all writes from monolith DB.
  Publishes events to Kafka.
  New service consumes and syncs its own DB.
  Eventually consistent during transition.

  [Monolith] → [Legacy DB] → [Debezium CDC] → [Kafka] → [New Service] → [New DB]
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Strangler Fig (big bang rewrite):

What breaks without it:

1. High risk: the entire system is replaced at once — one mistake affects all functionality.
2. Long development cycle with no production feedback — new system is built for months without real-world validation.
3. Teams must maintain both old and new systems with no incremental progress.
4. The new system cannot leverage lessons from running the old system in production.

WITH Strangler Fig:
→ Incremental risk: each extraction is small, reversible, and validated in production.
→ New services have production track record before the monolith is fully replaced.
→ Business can continue using the working monolith while migration proceeds.
→ Priority: extract the pieces that need independent scaling first (e.g., checkout during peak season).

---

### 🧠 Mental Model / Analogy

> The Strangler Fig tree (Ficus aurea) sends roots down from its branches, wrapping around a host tree. Over decades, the fig's roots thicken and merge, gradually replacing the host tree's structure. When the host tree eventually dies, the fig has grown its own full structure and stands independently. The host tree is gone, but you never had a moment where neither the old nor the new tree was providing support. Software migration via Strangler Fig mirrors this: new services wrap the legacy system, gradually taking over functionality. The legacy system continues operating throughout — there is no "dark period" where nothing works.

"Host tree" = legacy monolith (provides all functionality today)
"Strangler fig roots" = new microservices being built alongside
"Fig wrapping around host" = proxy routing some traffic to new services
"Host tree dying" = monolith features being decommissioned one by one
"Fig standing independently" = fully migrated microservices architecture, monolith gone

---

### ⚙️ How It Works (Mechanism)

**Feature flag routing — code-level Strangler Fig:**

```java
// At the Facade/Proxy level (or at the application level):
@RestController
class OrderController {

    @Autowired OldOrderService oldOrderService;       // monolith service
    @Autowired NewOrderService newOrderService;       // new microservice client
    @Autowired FeatureFlagService featureFlags;

    @PostMapping("/api/orders")
    public OrderResponse createOrder(@RequestBody CreateOrderRequest req) {
        if (featureFlags.isEnabled("new-order-service", req.getCustomerId())) {
            // Route to new microservice (gradually increasing %):
            return newOrderService.createOrder(req);
        } else {
            // Route to legacy monolith service:
            return oldOrderService.createOrder(req);
        }
    }
}
// Feature flag allows:
// - 1% of customers routed to new service (canary)
// - Specific test customers always routed to new service
// - Instant rollback: disable flag if new service has issues
```

---

### 🔄 How It Connects (Mini-Map)

```
Monolith vs Microservices
        │
        ▼
Strangler Fig Pattern  ◄──── (you are here)
(incremental monolith → microservices migration)
        │
        ├── Anti-Corruption Layer → bridges data/model between old and new
        ├── Feature Flags         → controls traffic routing during migration
        ├── Canary Deployment     → validates new service with subset of traffic
        ├── API Gateway           → the Façade that routes old vs new traffic
        └── Service Decomposition → identifies which capabilities to extract first
```

---

### 💻 Code Example

**Nginx proxy routing — Strangler Fig at the network layer:**

```nginx
# Nginx proxy: routes /api/orders/... to new service, everything else to monolith

upstream monolith {
    server monolith:8080;
}

upstream order_service {
    server order-service:8081;
}

server {
    listen 80;

    # Migrated: Order API now handled by new service
    location /api/orders {
        proxy_pass http://order_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Migrated: Customer API now handled by new service
    location /api/customers {
        proxy_pass http://customer_service;
    }

    # Not yet migrated: everything else still goes to monolith
    location / {
        proxy_pass http://monolith;
    }
}
# As each service is extracted:
# 1. Add the new service upstream block
# 2. Add the new location block
# 3. When 100% stable: remove the monolith from the Nginx config for that path
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                    |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The Strangler Fig Pattern requires a microservices architecture | The new system can also be a modular monolith, a different monolith, or any other architecture. The pattern is about incremental replacement, not about the destination architecture                                                                                                                       |
| The migration is done when the monolith is turned off           | The migration is done for each extracted feature when 100% of traffic is routed to the new service and the feature is removed from the monolith. The monolith is not turned off until ALL features are migrated — which could take years                                                                   |
| You must extract features from the monolith in a specific order | Extract based on business priority and technical feasibility. Start with features that are: (1) independently useful, (2) have stable, well-defined APIs, and (3) have the most to gain from independent scaling or deployment                                                                             |
| The Strangler Fig is always the right migration strategy        | For very small monoliths (<50KLOC), a careful big-bang rewrite with thorough testing may be faster. For systems with no existing API surface (batch jobs, background workers), different migration patterns apply. Strangler Fig works best for request-response systems with an identifiable Façade point |

---

### 🔥 Pitfalls in Production

**Data consistency during dual-write phase**

```
SYMPTOM: Customer profile updated in new CustomerService,
         but monolith's checkout page still shows old data
         because it reads from the legacy DB (not yet migrated).

ROOT CAUSE: dual-write setup where both services update data independently.

SCENARIO:
  User updates email: [New CustomerService] → writes to new_customers.email
  Checkout reads:     [Monolith]           → reads from legacy.CUST_EMAIL (old)
  User gets checkout confirmation to old email!

MITIGATION STRATEGIES:
  1. Sync legacy DB from new service (new = source of truth, CDC back to legacy)
  2. Monolith reads customer data via new CustomerService API (ACL)
  3. New service reads from legacy DB during transition (ACL, not ideal)
  4. Tight migration timeline: minimize the dual-write window

KEY PRINCIPLE: Define ONE source of truth per data entity, per migration phase.
  During transition: old = truth (new service reads from old)
  After cutover: new = truth (old system reads from new via ACL or is decommissioned)
```

---

### 🔗 Related Keywords

- `Monolith vs Microservices` — the Strangler Fig bridges the gap between the two architectures
- `Anti-Corruption Layer` — translates between the legacy system's model and the new service's model during migration
- `Feature Flags (Microservices)` — enables controlled traffic routing between old and new systems
- `Canary Deployment` — validates new services with a subset of production traffic during migration
- `Service Decomposition` — identifies what to extract and in what order

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PHASES       │ 1. Install Facade (proxy)                 │
│              │ 2. Build new service (shadow mode)        │
│              │ 3. Route 1% → 100% to new service        │
│              │ 4. Remove feature from monolith           │
│              │ Repeat per feature                        │
├──────────────┼───────────────────────────────────────────┤
│ ROUTING      │ API Gateway, Nginx, Feature Flags         │
├──────────────┼───────────────────────────────────────────┤
│ DATA         │ ACL reads from legacy DB, CDC sync,       │
│              │ or dual-write with one source of truth    │
├──────────────┼───────────────────────────────────────────┤
│ VS BIG-BANG  │ Lower risk, reversible, prod-validated    │
│              │ each step                                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Strangler Fig requires a "Façade" that intercepts all traffic. In a web application, this is typically an API Gateway or reverse proxy. But what about background jobs, scheduled tasks, and batch processes in the monolith? Describe the migration strategy for a nightly batch job (e.g., "generate invoices for all orders placed today") that is being extracted to a new `InvoicingService`. There is no HTTP Façade for batch jobs — how do you handle the transition? Describe the "parallel run" approach where both the old and new batch jobs run simultaneously and their outputs are compared before the old one is disabled.

**Q2.** During the Strangler Fig migration, there is a period when the same data entity (e.g., "Customer") is being written to by both the monolith and the new CustomerService — dual writes. Describe Change Data Capture (Debezium) as the synchronisation mechanism: what is the "transaction outbox pattern" that prevents data loss during the sync? If the monolith writes to the legacy DB and Debezium publishes events to Kafka, but the Kafka consumer (new service) is temporarily down, what happens to the events — are they lost or replayed? And what is the acceptable lag for sync in a near-real-time profile update scenario?
