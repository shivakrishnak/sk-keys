---
layout: default
title: "Strangler Fig Pattern"
parent: "Software Architecture Patterns"
nav_order: 761
permalink: /software-architecture/strangler-fig-pattern/
number: "761"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Microservices, Anti-Corruption Layer, Bounded Context"
used_by: "Legacy modernization, Incremental migration, Risk-managed refactoring"
tags: #advanced, #architecture, #migration, #modernization, #risk-management
---

# 761 — Strangler Fig Pattern

`#advanced` `#architecture` `#migration` `#modernization` `#risk-management`

⚡ TL;DR — The **Strangler Fig Pattern** incrementally replaces a legacy system by routing specific functionality to a new system piece by piece — the new system "strangles" the old one gradually until the old is completely replaced, avoiding a risky big-bang rewrite.

| #761 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Microservices, Anti-Corruption Layer, Bounded Context | |
| **Used by:** | Legacy modernization, Incremental migration, Risk-managed refactoring | |

---

### 📘 Textbook Definition

**Strangler Fig Pattern** (Martin Fowler, 2004 — inspired by the strangler fig tree that grows around a host tree and eventually replaces it): an incremental migration strategy for replacing a legacy system in which new functionality is implemented in a new system while existing functionality is migrated piece by piece. A facade or proxy routes traffic: initially all to the legacy, gradually more to the new system, until the legacy handles zero traffic and can be decommissioned. Key characteristics: (1) no big-bang cutover; (2) old and new systems coexist during migration; (3) incremental risk (each migration step is small and reversible); (4) continuous delivery of value during migration (new features built in the new system). Used extensively in cloud migrations, monolith-to-microservices, legacy API modernization.

---

### 🟢 Simple Definition (Easy)

Renovating a house while living in it. Not: demolish the house, rebuild it, move back in (big-bang — no house for 6 months). Instead: renovate one room at a time. You move out of one room into another. Renovate it. Move back in. Move to the next room. After 2 years: entire house renovated, but you lived there the whole time. The old house "died" room by room, replaced piece by piece by the new house. You never had a "no house" period.

---

### 🔵 Simple Definition (Elaborated)

A 10-year-old Rails monolith. Business can't stop while you rewrite it from scratch (would take 2 years, high risk, scope creep). Strangler Fig: put an API gateway in front. Route `/payments/*` to the new Payment microservice. Old monolith still handles all other routes. Ship the Payment service. It works. Next: route `/orders/checkout` to the new Order service. Old monolith handles less. Eventually: 100% of routes route to new services. Monolith handles 0%. Decommission it. At every step: the system is live and delivering value.

---

### 🔩 First Principles Explanation

**Why big-bang rewrites fail and how Strangler Fig avoids the failure modes:**

```
THE BIG-BANG REWRITE PROBLEM:

  "Let's rewrite the legacy system from scratch."
  
  Failure modes (Joel Spolsky: "Things You Should Never Do"):
  
  1. REQUIREMENTS LOSS: The old system has 10 years of bug fixes and edge cases.
     Developers don't know why the code is the way it is. Edge cases re-introduced.
     
  2. MOVING TARGET: Business keeps adding features to OLD system during rewrite.
     New system must catch up to a target that keeps moving. Never complete.
     
  3. SCOPE CREEP: "Since we're rewriting, let's also modernize the data model,
     change the language, add microservices, and implement a new UI."
     2-year estimate → 5 years.
     
  4. RISK CONCENTRATION: Entire team works on new system. Zero value delivered.
     Until cutover: zero new features in production. Business suffers.
     
  5. CUTOVER PANIC: Big-bang cutover day. All-or-nothing. If it fails: revert.
     Revert to old system: months of bug fixes lost. Horror show.
     
THE STRANGLER FIG SOLUTION:

  Incremental steps. Each step:
  - Small, bounded, reversible.
  - Delivers real value immediately (new feature in new system).
  - Reduces legacy footprint.
  
  STRANGLER FIG ANATOMY:
  
    Phase 1: COEXIST
    
      Client Request
           │
           ▼
      [Facade/Proxy/API Gateway]
           │
           ├─── New capability → [New System]
           │
           └─── Everything else → [Legacy System]
           
    Phase 2: MIGRATE INCREMENTALLY
    
      Move one bounded context at a time:
      
      Step 1: Orders API → New Service. Monolith: still handles Payments, Catalog, etc.
      Step 2: Payments API → New Service. Monolith: still handles Catalog, Users.
      Step 3: Catalog API → New Service. Monolith: still handles Users.
      Step 4: Users API → New Service. Monolith: handles nothing.
      Step 5: Decommission monolith.
      
    Phase 3: STRANGLE
    
      Legacy handles 0% of traffic. Can be safely removed.
      
FACADE STRATEGIES:

  1. API GATEWAY: HTTP-level routing. Route by path prefix or header.
     No code change to clients; routing config change to shift traffic.
     Tool: nginx, AWS API Gateway, Kong, Traefik.
     
  2. STRANGLER FIG FACADE (application-level):
     An application proxy that delegates to either legacy or new.
     Can do data transformation at the boundary.
     
     class OrderFacade {
         Order getOrder(OrderId id) {
             if (featureFlags.isNewOrderServiceEnabled()) {
                 return newOrderService.get(id);     // new system
             } else {
                 return legacyAdapter.getOrder(id);  // legacy
             }
         }
     }
     
  3. DATABASE STRANGLER:
     Harder case: both systems share a database.
     
     Step 1: Keep shared database. New service reads/writes same tables.
     Step 2: Mirror writes (dual-write: write to both new service's DB AND legacy DB).
     Step 3: Migrate reads to new service's DB.
     Step 4: Stop writes to legacy DB.
     Step 5: Remove legacy DB dependency.
     
     This is the most complex strangling scenario (often needs Event Sourcing or CDC).
     
MIGRATION STRATEGIES FOR SHARED DATABASE:

  EXPAND-CONTRACT (parallel change):
  
    Expand: Add new columns/tables needed by new system (backwards compatible).
    Migrate: New system writes to new columns; legacy to old.
    Contract: Remove old columns when legacy is fully replaced.
    
  ANTI-CORRUPTION LAYER at DB boundary:
    New service has its own database.
    Migration job synchronizes data from legacy DB to new DB.
    New service reads its own DB; writes go to both during transition.
    
FEATURE FLAG CONTROLLED STRANGLING:

  Gradual traffic migration with feature flags:
  
  class PaymentRouter {
      PaymentResult process(PaymentRequest req) {
          double rolloutPercentage = featureFlags.get("NEW_PAYMENT_SERVICE_ROLLOUT");
          if (Math.random() < rolloutPercentage) {
              return newPaymentService.process(req);
          } else {
              return legacyPaymentProcessor.process(req);
          }
      }
  }
  
  Start: rollout = 0% (all legacy)
  Week 1: rollout = 5% (5% on new service, monitor)
  Week 2: rollout = 25%
  Week 4: rollout = 100% (all new service)
  Decommission: remove legacy code path.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Strangler Fig (big-bang rewrite):
- 18-month dark period: no new features, high risk, scope creep, all-or-nothing cutover
- Legacy knowledge lost in the rewrite; edge cases re-introduced

WITH Strangler Fig:
→ New features immediately in the new system; business value delivered throughout migration
→ Each step small, reversible — failure means one feature fails, not entire system rollback

---

### 🧠 Mental Model / Analogy

> The strangler fig tree (Ficus aurea). A fig seed germinates in the branches of a host tree. The fig grows AROUND the host, sending roots down to the soil. The host continues to live and provide structural support. Over decades: the fig's roots and trunk surround the host completely. Eventually: the host tree dies and rots away. The fig stands independently, having used the host for structural support during its own growth. At no point was the forest without a tree.

"Host tree" = legacy system (provides structure while new system grows)
"Strangler fig growing around it" = new system incrementally taking over capabilities
"Both trees coexist" = facade routes some traffic to new, some to legacy during migration
"Host rots away" = legacy decommissioned after new system handles all traffic

---

### ⚙️ How It Works (Mechanism)

```
STRANGLER FIG MIGRATION CHECKLIST:

  1. IDENTIFY: Map the legacy system's capabilities (what does it do?).
  2. PRIORITIZE: Which capability to migrate first? (new features > stable existing)
  3. FACADE: Put routing layer in front (API gateway, proxy, or facade class).
  4. IMPLEMENT: Build the capability in the new system.
  5. SHADOW: Run both in parallel — old handles traffic, new handles shadow traffic (log differences).
  6. ROUTE: Shift traffic (start with 5%, monitor, increase).
  7. VERIFY: New system handles capability correctly at 100%.
  8. REMOVE: Delete legacy code path for this capability.
  9. REPEAT: Next capability.
  10. DECOMMISSION: When legacy handles 0% of all capabilities.
```

---

### 🔄 How It Connects (Mini-Map)

```
Legacy monolith needing modernization (too big to rewrite at once)
        │
        ▼ (incremental migration via proxy/facade)
Strangler Fig Pattern ◄──── (you are here)
(new system grows around legacy; legacy strangled incrementally)
        │
        ├── Anti-Corruption Layer: needed at the boundary between new and legacy models
        ├── Feature Flags: enable gradual traffic migration per capability
        ├── Bounded Context: each bounded context is one migration unit
        └── Event-Driven Architecture: CDC/events enable data migration without shared DB
```

---

### 💻 Code Example

```java
// STRANGLER FIG FACADE — routes between legacy and new payment service:
@Component
public class PaymentFacade {
    private final LegacyPaymentProcessor legacy;
    private final NewPaymentService newService;
    private final FeatureFlags featureFlags;
    
    public PaymentResult process(PaymentRequest request) {
        if (featureFlags.isEnabled("NEW_PAYMENT_SERVICE", request.customerId())) {
            log.info("Routing payment {} to NEW service", request.paymentId());
            try {
                return newService.process(request);
            } catch (Exception e) {
                log.error("New service failed, falling back to legacy", e);
                metrics.increment("new_payment_fallback");
                return legacy.process(request);  // Fallback during migration
            }
        }
        log.info("Routing payment {} to LEGACY", request.paymentId());
        return legacy.process(request);
    }
}

// ────────────────────────────────────────────────────────────────────

// Feature flag: gradually increase rollout:
// Week 1: featureFlags.setRollout("NEW_PAYMENT_SERVICE", 5%)
// Week 2: featureFlags.setRollout("NEW_PAYMENT_SERVICE", 25%)
// Week 4: featureFlags.setRollout("NEW_PAYMENT_SERVICE", 100%)
// Week 5: Remove legacy code path. Remove feature flag. Decommission legacy.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strangler Fig always uses microservices | Strangler Fig is an incremental migration strategy, not a target architecture. You can strangle a monolith into another monolith (smaller, cleaner), into a modular monolith, or into microservices. The pattern is about the migration technique, not the destination architecture |
| The facade is temporary and should be removed quickly | The facade may become a permanent part of the architecture (as an API gateway, service mesh, or aggregation layer). For HTTP API facades: they often evolve into API gateways with routing, authentication, rate limiting — valuable in their own right. Don't rush to remove the facade just because migration is complete |
| Strangler Fig only applies to monolith → microservices | Strangler Fig applies to any legacy replacement: legacy mainframe → modern system, old REST API → GraphQL, old synchronous architecture → event-driven, legacy database → modern database. Whenever you need to replace something that can't be replaced all at once |

---

### 🔥 Pitfalls in Production

**Shared database preventing clean strangling:**

```
PROBLEM: Legacy monolith and new Order service both write to the same Orders table.
New service adds new features. Legacy processes have direct SQL on same tables.

SYMPTOM: Can't evolve new service's data model without breaking legacy.
         Can't remove legacy without data ownership confusion.

BAD (tight database coupling):
New Order Service → orders_db.orders (same table)
Legacy Monolith  → orders_db.orders (same table)

FIX - EXPAND-CONTRACT + OWNERSHIP TRANSFER:

Step 1 EXPAND: New service writes to orders table AND orders_v2 table (dual write).
               Legacy reads from orders. New service reads from orders_v2.
               
Step 2 SYNC: Sync job ensures orders and orders_v2 stay consistent.

Step 3 MIGRATE READS: Gradually shift read traffic to new service (which reads orders_v2).

Step 4 MIGRATE WRITES: New service is sole writer to orders_v2.
                       Legacy writes to orders (its own). New service ignores orders.
                       
Step 5 DECOMMISSION: Legacy removed. orders table removed.
                     New service owns orders_v2 exclusively (rename to orders).
```

---

### 🔗 Related Keywords

- `Anti-Corruption Layer` — used at the boundary between new system and legacy to protect the new model
- `Feature Flags` — enable gradual traffic routing from legacy to new system
- `Bounded Context` — natural migration unit: migrate one bounded context at a time
- `API Gateway` — common façade implementation for HTTP-based strangling
- `Event-Driven Architecture` — CDC (Change Data Capture) enables database strangling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Build new system around legacy; facade   │
│              │ routes traffic; legacy traffic shrinks   │
│              │ to zero; decommission when done.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Modernizing legacy system too large or   │
│              │ risky to rewrite at once; need continuous│
│              │ delivery during migration                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ System is small enough to rewrite safely │
│              │ in one iteration; no good seam to route  │
│              │ traffic (entire system is tightly coupled│
│              │ with no extractable pieces)              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fig tree grows around the host tree;    │
│              │  host provides support while fig matures;│
│              │  host dies away after fig is independent."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Anti-Corruption Layer → Feature Flags →  │
│              │ Bounded Context → API Gateway            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're strangling a legacy e-commerce monolith. The first service to extract is the Product Catalog. The monolith has a single relational database with tables: `products`, `orders`, `customers`, `inventory` — all with foreign keys between them. How do you isolate the Product Catalog without breaking the monolith's FK relationships? What steps do you take to migrate the data, and what temporary solutions (views, dual write, CDC) allow both systems to coexist?

**Q2.** A team estimates the Strangler Fig migration will take 3 years (60+ bounded contexts, shared database, complex legacy logic). During those 3 years: legacy system and new system coexist, facade handles routing, and new features are built in new system but bugs in legacy still need to be fixed. What are the organizational and technical costs of running two systems simultaneously? At what point does the migration cost exceed the cost of living with the legacy? How do you prevent "strangler fig fatigue"?
