---
layout: default
title: "Monolith to Microservices Migration"
parent: "Microservices"
nav_order: 1
permalink: /microservices/monolith-to-microservices-migration/
number: "MSV-001"
category: Microservices
difficulty: ★★★
depends_on: Monolith vs Microservices, Strangler Fig Pattern, Domain-Driven Design (DDD), Bounded Context, Service Decomposition
used_by: Technology Migration Strategy, Re-platforming vs Re-architecting
related: Strangler Fig Pattern, Modular Monolith, Service Decomposition, Anti-Corruption Layer, Bounded Context
tags:
  - microservices
  - architecture
  - advanced
  - pattern
  - distributed
  - bestpractice
---

# MSV-001 — Monolith to Microservices Migration

⚡ TL;DR — Migrating a monolith to microservices requires strangling the monolith service-by-service, driven by domain boundaries, not technical convenience.

| #2280 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Strangler Fig Pattern, Domain-Driven Design (DDD), Bounded Context, Service Decomposition | |
| **Used by:** | Technology Migration Strategy, Re-platforming vs Re-architecting | |
| **Related:** | Strangler Fig Pattern, Modular Monolith, Service Decomposition, Anti-Corruption Layer, Bounded Context | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company has a 10-year-old monolithic Java application. Deployments take 45 minutes and must be coordinated across 12 teams. Scaling the Payment module requires scaling the entire application (including the Reports module which needs no scaling). A bug in the Shipping module caused an unrelated User Authentication outage — the entire process crashed. Leadership decides: "We need microservices." The engineering team rewrites everything simultaneously. Two years and $8M later, the microservices system is still not in production. The original monolith has continued accumulating technical debt.

**THE BREAKING POINT:**
Big-bang rewrites of monolithic systems fail at a near-100% rate for large codebases. The rewrite never fully catches up with the monolith's ongoing feature development; the original system continues accumulating logic; teams lose institutional knowledge about edge cases; and the "new" system goes live with half the battle-tested logic of the original.

**THE INVENTION MOMENT:**
Monolith-to-microservices migration patterns emerged to provide incremental, risk-managed strategies: extract services one domain at a time, run old and new systems in parallel, route traffic progressively to the new service. The monolith shrinks gradually; the risk of any single extraction is bounded; value is delivered continuously.

---

### 📘 Textbook Definition

**Monolith to Microservices Migration** is an incremental architectural transformation strategy in which a monolithic application is decomposed into microservices over time — typically applying the **Strangler Fig Pattern**: new functionality is built as standalone services, existing functionality is extracted service-by-service behind a routing proxy or API facade, until the monolith contains no significant business logic and can be decommissioned. The migration is guided by **Domain-Driven Design (DDD)** bounded context identification to ensure each extracted service aligns with a coherent business capability.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Wrap the monolith in a proxy, extract one domain at a time, and reroute traffic incrementally until the monolith is empty.

**One analogy:**
> Renovating a house while living in it. You don't demolish the house and live in a tent for two years while rebuilding. You renovate one room at a time — kitchen first, then bathrooms, then bedrooms — living in the finished rooms while the next is being renovated. The old house keeps you warm throughout. Monolith-to-microservices migration is exactly this: the monolith keeps your business running while you extract rooms (services) one at a time.

**One insight:**
The most dangerous mistake in monolith migration is not technical — it is choosing extraction order based on technical convenience ("this module is self-contained") rather than business value and domain separation. Extract where pain is highest and domain boundaries are clearest.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Never rewrite everything simultaneously — incremental extraction limits risk to one domain at a time.
2. Domain boundaries, not code structure, determine extraction order and service boundaries.
3. The monolith and new services must coexist and interoperate during migration — no flag day.
4. Data is the hardest migration problem — services need their own databases, not a shared monolith DB.
5. Each extraction must deliver independent deployability before moving to the next.

**DERIVED DESIGN:**
From invariant 2: identify Bounded Contexts using Event Storming or domain analysis. The Payment domain is a better extraction candidate than "the module with the fewest dependencies" because domain clarity predicts service stability.

From invariant 4: the **Strangler Fig** antipattern failure mode is extracting logic but leaving data in the shared monolith database. The service is not truly independent if it reads/writes the monolith's `payments` table. Database decomposition follows or accompanies logic extraction — using the **Database per Service** pattern.

**THE TRADE-OFFS:**
**Gain:** Incremental risk; continuous delivery of business value; earlier production validation; preserves institutional knowledge.
**Cost:** Running monolith + microservices simultaneously increases operational complexity; data synchronisation between monolith and extracted services is complex; extended migration period (months to years); requires disciplined DDD-based decomposition planning.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce monolith with 500k LOC. Modules: Catalog, Cart, Orders, Payments, Shipping, Users, Reports. The Payments module processes $50M/day and needs PCI-DSS isolation. The Reports module is an internal tool with 5 users.

**WHAT HAPPENS with Big-Bang Rewrite:**
Team starts full rewrite. 18 months later: Payments, Cart, and Orders are in the new system. Reports, Catalog, and Shipping are 40% done. The monolith is still in production with all traffic. The rewrite diverged from the monolith 9 months ago — 900 bug fixes applied to the monolith were not ported. Go-live date: unknown.

**WHAT HAPPENS with Strangler Fig Migration:**
Week 1: Deploy routing proxy (API Gateway / Nginx) in front of monolith. Week 4: Extract **Payments** service (highest business value, clearest domain, regulatory need). Route `/payments/*` to new service. Monolith still handles everything else. Week 12: Extract **Users** service (clear domain, widely used by other services). Week 20: Extract **Shipping**. Reports never extracted — not worth the migration cost for 5 users. Monolith decommissioned after Reports is retired.

**THE INSIGHT:**
Not every module deserves to become a microservice. Apply the Strangler Fig where domain value and isolation requirements justify the cost. Leave stable, low-value modules in the monolith (or migrate to a modular monolith) rather than paying migration costs with no return.

---

### 🧠 Mental Model / Analogy

> Think of the monolith migration like replacing a ship's engine while at sea. You can't stop the ship (take the monolith offline) and do a full refit. Instead, you install a new engine compartment alongside the old one, gradually route power demand to the new engine, and eventually shut down the old one — all while the ship keeps sailing.

- "Ship" → running production system
- "Old engine" → monolith
- "New engine compartment" → extracted microservice
- "Routing power demand" → Strangler Fig API routing
- "Same passengers/cargo" → same requests, same business logic
- "Sailing during refit" → non-stop production availability

Where this analogy breaks down: engine replacement is a physical parallel process. In software migration, data synchronisation between monolith and extracted services is a distributed systems problem with potential consistency challenges that have no physical analogy.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Moving from a monolith to microservices is like converting a big open-plan factory floor into separate specialist workshops. You don't close the factory and rebuild it — you isolate one production line at a time, move it to its own workshop, and when all lines are moved, you decommission the old floor.

**Level 2 — How to use it (junior developer):**
Step 1: Map your monolith's domains (Payment, Orders, etc.). Step 2: Deploy a routing proxy in front of the monolith (no behaviour change yet). Step 3: Extract the highest-priority domain as a standalone service. Step 4: Route requests for that domain to the new service via the proxy. Step 5: Decommission the monolith code for that domain. Step 6: Repeat steps 3–5 for the next domain. Migration done when the proxy routes nothing to the monolith.

**Level 3 — How it works (mid-level engineer):**
The **Strangler Fig** proxy (API Gateway/Nginx) is the key enabler. It inspects incoming requests and routes to either the monolith or a new service based on path/header. During migration, the new service and monolith may handle the same domain — **feature flags** control the routing percentage (10% → 50% → 100% canary rollout). For data migration: the new service initially calls back to the monolith's data API (Anti-Corruption Layer) to avoid re-implementing all data access logic immediately. Over time, the service's own database is populated via **Change Data Capture (CDC)** from the monolith's database, until the monolith's data for that domain is fully migrated.

**Level 4 — Why it was designed this way (senior/staff):**
The Strangler Fig migration is a directional architectural bet. The organisation is betting that the long-term benefits (independent scalability, independent deployability, team autonomy) justify the sustained migration cost. The key design decision is **what to never extract**: not every module deserves microservice separation. The 80/20 rule often applies — 80% of the business value from microservices comes from extracting 20% of the monolith (the high-churn, high-scale, high-isolation-need domains). A **Modular Monolith** is sometimes the right end state — not a microservices fleet. The discipline is in resisting "microservices for its own sake" and applying extraction only where isolation need is real.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  STRANGLER FIG MIGRATION PHASES                        │
│                                                        │
│  PHASE 1 — Proxy in front, all traffic to monolith:   │
│  Client → [Proxy] → [Monolith]                        │
│                                                        │
│  PHASE 2 — Extract service, route one domain:         │
│  Client → [Proxy] → /payments → [Payment SVC]  NEW    │
│                   → everything else → [Monolith]       │
│                                                        │
│  PHASE 3 — Extract next domain:                       │
│  Client → [Proxy] → /payments → [Payment SVC]         │
│                   → /users    → [User SVC]      NEW   │
│                   → everything else → [Monolith]       │
│                                                        │
│  PHASE N — Full extraction, monolith decommissioned:  │
│  Client → [Proxy] → /payments → [Payment SVC]         │
│                   → /users    → [User SVC]             │
│                   → /orders   → [Order SVC]            │
│                   (no monolith routes remain)          │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Day 1: API Gateway deployed in front of monolith
  → All routes → Monolith (no change in behaviour)
    [← YOU ARE HERE: proxy installed, system unchanged]

Month 3: Payment service extracted
  → POST /payments/* → Payment Microservice
  → Everything else → Monolith
  → Payment service DB seeded via CDC from monolith DB

Month 9: User service extracted
  → /users/* → User Microservice
  → /payments/* → Payment Microservice
  → Remainder → Monolith (Catalog, Orders, Shipping)

Month 18: All high-value domains extracted
  → Monolith serves only Reports (5 internal users)
  → Decision: retire Reports or leave as-is
```

**FAILURE PATH:**
```
Data synchronisation failure:
  → Payment service reads from its own DB (extracted)
  → Monolith Orders module still reads from shared DB
  → Order data references payment IDs no longer in monolith DB
  → Referential integrity violation → orders fail
  [Fix: implement Anti-Corruption Layer in Orders module
   to call Payment Service API instead of DB directly]
```

**WHAT CHANGES AT SCALE:**
At 5 developers: monolith is fine, no migration needed. At 50 developers: modular monolith or 5–10 microservices. At 200 developers: 20–50 microservices aligned with team topology. The extraction cadence (1–2 services/quarter) is sustainable; faster creates integration debt.

---

### 💻 Code Example

**Example 1 — Anti-Corruption Layer (ACL) during migration:**

```java
// During migration: Orders module still in monolith
// but Payments service has been extracted.
// BAD: Orders module reads payment data from DB directly
@Repository
public class OrderRepository {
    // Direct DB call to payments table — breaks as soon
    // as payment DB is migrated to Payment Service's DB
    @Query("SELECT * FROM payments WHERE order_id = :id")
    Payment getPaymentForOrder(Long id);
}

// GOOD: Anti-Corruption Layer — Orders calls Payment API
@Component
public class PaymentServiceACL {
    // Insulates Orders module from Payment Service's
    // internal representation and data store
    public Payment getPaymentForOrder(Long orderId) {
        return paymentServiceClient
            .get("/payments?orderId=" + orderId)
            .bodyToMono(Payment.class)
            .block();
    }
}
```

**Example 2 — Strangler Fig routing with Nginx:**

```nginx
# Strangler Fig proxy configuration
upstream monolith {
    server monolith-app:8080;
}
upstream payment_service {
    server payment-svc:8080;
}
upstream user_service {
    server user-svc:8080;
}

server {
    listen 80;

    # Phase 2: route payments to new service
    location /api/v1/payments/ {
        proxy_pass http://payment_service;
    }

    # Phase 3: route users to new service
    location /api/v1/users/ {
        proxy_pass http://user_service;
    }

    # All other traffic still goes to monolith
    location / {
        proxy_pass http://monolith;
    }
}
```

---

### ⚖️ Comparison Table

| Strategy | Risk | Speed | Best When |
|---|---|---|---|
| **Strangler Fig (incremental)** | Low | Slow (months–years) | Production system that must stay live |
| **Big-Bang Rewrite** | Very high | Fast (in theory) | Never recommended for complex systems |
| **Modular Monolith (intermediate)** | Low | Medium | First step before potential microservices extraction |
| **Parallel Run** | Medium | Medium | Validating new service parity before routing cutover |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All modules should become microservices | Extract only where isolation need is real (scale, team autonomy, security boundary). Low-churn, stable modules may be better left in the monolith |
| Database migration happens automatically | Data separation is the hardest part. Each service needs its own database — this requires explicit CDC migration, data ownership clarity, and deduplication strategies |
| The monolith must be fully decommissioned | Some organisations productively run a "skeleton monolith" for stable, low-value domains indefinitely. The goal is strategic isolation, not total elimination |
| Microservices are faster to develop than the monolith | Microservices have higher operational overhead and distributed-systems complexity. Development speed advantage applies only per-team per-domain, once the architecture is stable |

---

### 🚨 Failure Modes & Diagnosis

**1. Distributed Monolith — No Independence Gained**

**Symptom:** "Microservices" deployed but: deployments still require coordinating all teams simultaneously. A change to Order Service always requires a synchronized Payment Service change. Shared database still connects them.

**Root Cause:** Services were split by technical layer (controller/service/repository) rather than by domain. Or services share a database, defeating the purpose. When services are not independently deployable, you have a distributed monolith.

**Diagnostic:**
```bash
# Count cross-service deployments:
git log --oneline --all | grep -c "deploy"
# If multiple services always deployed together: distributed monolith
# Check for shared database schemas:
psql -c "\dt" | grep -c "schema"
# If one schema used by multiple services: shared DB anti-pattern
```

**Fix:** Re-decompose along DDD bounded context boundaries. Introduce ACL to decouple shared data. Configure each service's own database schema.

**Prevention:** Enforce the "independently deployable" definition as a migration acceptance criterion. A service is not "migrated" until it can be deployed without coordinating other services.

---

**2. Data Synchronisation Lag — Business Logic Errors**

**Symptom:** Customer reports: "My order shows as unpaid but I was charged." Payment Service and Order Service have inconsistent views of payment status.

**Root Cause:** CDC pipeline from monolith DB to Payment Service DB has processing lag. Order Service reads the monolith DB (stale); Payment Service reads its own DB (current). During the migration window, both sources are active simultaneously.

**Diagnostic:**
```bash
# Check CDC pipeline lag:
kafka-consumer-groups --bootstrap-server kafka:9092 \
  --describe --group cdc-payment-group
# Large lag on payment_events topic = synchronisation delay
```

**Fix:** Order Service reads payment status from Payment Service API — not database. Add anti-corruption layer. Eventual consistency is acceptable; stale reads from wrong source are not.

**Prevention:** Define the "source of truth" per domain before migration. After extracting a service, all consumers must read from the service's API, never the legacy shared database directly.

---

**3. Feature Freeze — Monolith Migration Consumes All Capacity**

**Symptom:** No new product features have shipped in 6 months. All engineering capacity consumed by migration work.

**Root Cause:** Migration was executed as a dedicated project consuming all engineering resources, rather than being threaded through normal feature development.

**Diagnostic:**
```bash
# Check feature vs. migration commit ratio:
git log --oneline --since="6 months ago" \
  | grep -c "feat:\|fix:"
git log --oneline --since="6 months ago" \
  | grep -c "migration:\|refactor:"
# If migration >> feature: capacity imbalance
```

**Fix:** Apply the 20% rule: no more than 20% of sprint capacity on migration work. Extract services opportunistically when touching a domain for a feature, not as a standalone project.

**Prevention:** Embed migration work in feature tickets. "Add User registration feature" also includes "extract User Service from monolith" as a subtask. Business features and migration progress together.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Strangler Fig Pattern` — the primary pattern for incremental monolith extraction; understanding the Strangler Fig's proxy-and-reroute mechanism is required to execute a safe migration
- `Domain-Driven Design (DDD)` — the analytical framework for identifying correct service boundaries; migrations without DDD analysis lead to distributed monoliths

**Builds On This (learn these next):**
- `Database per Service` — the data isolation pattern required after logical service extraction; without it, services remain coupled through a shared database
- `Anti-Corruption Layer` — the integration pattern for insulating extracted services from the monolith's data model during the migration period

**Alternatives / Comparisons:**
- `Modular Monolith` — a less invasive alternative: improve the monolith's internal modularity without full microservice extraction; appropriate when the organisation lacks the operational maturity for microservices
- `Re-platforming vs Re-architecting` — the strategic decision of whether to migrate the monolith to a cloud platform as-is (re-platform) vs. decompose it as microservices (re-architect)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Incremental decomposition of a monolith   │
│              │ into microservices via Strangler Fig       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Monolith deployment coupling; inability    │
│ SOLVES       │ to scale individual domains; team          │
│              │ coordination bottleneck                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Extract one domain at a time; never        │
│              │ rewrite everything simultaneously          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Monolith scaling pain; team autonomy need; │
│              │ regulatory isolation requirements          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small teams (<10 engineers); early-stage   │
│              │ products; unclear domain boundaries        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lower risk, continuous delivery vs.        │
│              │ extended migration timeline, dual-system   │
│              │ operational complexity                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Strangle the monolith one domain at a     │
│              │  time; never rewrite, always reroute."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strangler Fig → Database per Service →     │
│              │ Anti-Corruption Layer → Event Sourcing     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A company has a 15-year-old monolith where the Payment, Inventory, and Notification domains are tightly coupled with shared transactional boundaries — a payment commit also updates inventory and triggers notifications in one database transaction. Design an extraction strategy that preserves transactional correctness across these three domains as they are separated into microservices, specifying the consistency model and the data synchronisation approach.

**Q2.** Your team is 12 months into a monolith-to-microservices migration. 6 services have been extracted. The monolith still owns 70% of the business logic. A new CTO arrives and asks: "Should we continue, pause and stabilise, or consider a Modular Monolith as the end state instead?" What decision framework would you apply, what metrics would you present, and what recommendation would you make?

**Q3.** During Monolith-to-Microservices migration, the team discovers that the shared monolith database is the integration backbone for 30 internal modules — direct SQL JOINs across tables that will belong to different services. Evaluate three strategies for managing this transition (Anti-Corruption Layer with API calls, CDC-based data replication, and shared-read database with write isolation) against the dimensions of operational complexity, consistency guarantees, and migration reversibility.

