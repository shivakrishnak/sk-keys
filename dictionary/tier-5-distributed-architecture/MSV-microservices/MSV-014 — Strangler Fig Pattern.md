---
layout: default
title: "Strangler Fig Pattern"
parent: "Microservices"
nav_order: 14
permalink: /microservices/strangler-fig-pattern/
number: "MSV-014"
category: Microservices
difficulty: ★★★
depends_on: Anti-Corruption Layer, Service Decomposition, Modular Monolith
used_by: Service Decomposition, Bounded Context, Canary Deployment
related: Anti-Corruption Layer, Modular Monolith, Blue-Green Deployment
tags:
  - microservices
  - architecture
  - pattern
  - deep-dive
  - distributed
---

# MSV-014 — Strangler Fig Pattern

⚡ TL;DR — The Strangler Fig Pattern migrates a legacy system to a new architecture by incrementally routing requests to new services while the old system continues running, until the legacy is fully replaced.

| #634 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Anti-Corruption Layer, Service Decomposition, Modular Monolith | |
| **Used by:** | Service Decomposition, Bounded Context, Canary Deployment | |
| **Related:** | Anti-Corruption Layer, Modular Monolith, Blue-Green Deployment | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A large e-commerce company runs a 15-year-old PHP monolith handling $50M/month in transactions. Management wants to migrate to microservices. The conventional approach: build the complete new system in parallel over 18 months, then switch over in a "big bang" cutover during a maintenance window. The engineering team spends 18 months building. The cutover night arrives. Half the integrations don't work as expected. Payment processing breaks. The team rolls back at 3am. The new system is never deployed. The monolith continues for another decade.

**THE BREAKING POINT:**
"Big bang" rewrites almost always fail. The old system accumulated 15 years of undocumented edge cases, bug fixes, and business rules. The new system, built in isolation, misses them all. There is no safe way to test a complete rewrite under production load without actually using it in production.

**THE INVENTION MOMENT:**
This is exactly why the Strangler Fig Pattern was created — to incrementally route production traffic from the old system to the new system, one feature at a time, so the migration is continuously tested in production and can be reversed at any step.

---

### 📘 Textbook Definition

The **Strangler Fig Pattern** (named by Martin Fowler after the strangler fig tree that grows around and eventually replaces its host) is an application modernisation technique in which a new system is built around the edges of an existing system. A routing layer (proxy or API gateway) intercepts requests: initially all traffic goes to the legacy system; gradually, specific request types are routed to new services as they are built and validated. The legacy system is progressively "strangled" until it handles no more traffic and can be decommissioned.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Replace an old system piece by piece while it's still running — never stop-and-replace all at once.

**One analogy:**
> A strangler fig tree seeds in the canopy of a host tree, grows roots down, and eventually wraps around the host's trunk. The host tree lives on until the fig has grown strong enough to support the canopy alone — then the host quietly dies inside. Your new microservices are the fig. The legacy monolith is the host. The process takes time but the forest never stops growing.

**One insight:**
The strangler pattern makes the migration continuously verifiable. Each new service handles real production traffic from day one. Bugs are caught incrementally. There is no "big bang" risk because you can always send traffic back to the legacy for any individual feature that breaks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. At every point during the migration, the system serves production traffic — there is no downtime window.
2. Each extraction reduces the scope of the legacy system. The legacy never grows during the migration.
3. Any individual extraction can be reversed (rolled back) without affecting other extracted services.

**DERIVED DESIGN:**
Given Invariant 1 and 3, a routing layer must sit in front of both old and new systems. This router can direct each type of request to either system independently. The router is the implementation mechanism: typically an API Gateway, an nginx proxy with routing rules, or an application-level feature flag.

A standard migration sequence for one feature:
1. Build the new service (dark mode — 0% traffic)
2. Route a small percentage of traffic to the new service (shadow mode or canary)
3. Monitor new service behaviour vs legacy behaviour
4. If matching: increase percentage to 100%
5. Remove legacy code path for that feature
6. Repeat for the next feature

**THE TRADE-OFFS:**
**Gain:** Production-validated migration, reversible at every step, legacy continues providing value throughout, no downtime.
**Cost:** Dual system maintenance during migration (must maintain both old and new code), data synchronisation complexity, migration takes longer than a rewrite, routing layer is a single point of failure.

---

### 🧪 Thought Experiment

**SETUP:**
You have a monolith serving product catalog and checkout. You want to extract the catalog into a microservice. You have no downtime budget.

**WITHOUT STRANGLER FIG:**
Build new catalog service. Schedule a 4am maintenance window. Redirect all traffic to new service. Hope it works. It doesn't. Customers see blank product pages during promotion. Emergency rollback at 5am. Six months of work discarded.

**WITH STRANGLER FIG:**
1. Deploy new Catalog service alongside monolith (no traffic yet).
2. Add routing rule at API Gateway: `GET /products/**` → 5% to new Catalog service.
3. Monitor: new service has correct response rate, correct latency.
4. Ramp to 50%, 90%, 100% over two weeks.
5. Remove `GET /products/**` handler from the monolith.
6. Next: start extracting Checkout.

At every step: a one-config rollback returns all traffic to the monolith.

**THE INSIGHT:**
The Strangler Fig pattern turns a high-risk big-bang migration into a series of low-risk incremental experiments. Each step is production-tested and independently reversible.

---

### 🧠 Mental Model / Analogy

> Imagine renewing the plumbing in a house while people are still living in it. You don't cut off all water supply, install new pipes over three months, then reconnect. Instead, you run new pipes alongside old pipes, redirect one tap at a time, test each tap, then eventually cap the old pipes. The Strangler Fig Pattern is exactly this pipe-by-pipe approach for software systems.

- "Living in the house" → zero-downtime production system
- "Old pipes" → legacy monolith handling requests
- "New pipes" → new microservices
- "Redirecting one tap at a time" → routing one API endpoint/feature to the new service
- "Capping old pipes" → removing the legacy implementation after successful migration

Where this analogy breaks down: plumbing is purely sequential (one pipe at a time). The Strangler Fig can extract multiple features in parallel, as long as they don't share data or have tightly coupled dependencies.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The Strangler Fig Pattern is a way to replace an old computer system with a new one, one piece at a time, while both systems run simultaneously, until the old one is no longer needed and can be switched off.

**Level 2 — How to use it (junior developer):**
Start by identifying the feature with the fewest dependencies in the legacy system. Build a new service for it. Deploy a proxy or gateway that routes `0%` of traffic for that feature to the new service. Gradually increase the percentage while monitoring for errors. When 100% of traffic uses the new service without errors, delete the legacy code for that feature. Repeat.

**Level 3 — How it works (mid-level engineer):**
The routing layer is typically an API Gateway (Kong, AWS API Gateway, Nginx, Spring Cloud Gateway) with weighted routing rules. For each migrated endpoint: `route /api/products/* 10% → new-catalog-service, 90% → legacy-monolith`. Request logging in both systems enables comparison. Anti-Corruption Layers translate between the new service's clean domain model and the legacy data format. Data synchronisation during migration: write to both systems (dual write) or use change data capture (CDC) from the legacy database to the new service's database.

**Level 4 — Why it was designed this way (senior/staff):**
Fowler coined the pattern in 2004 and named it after his observation of strangler fig trees in Australia. The deeper insight is that all successful large-scale system migrations happen incrementally — Amazon's migration from monolith to microservices took over a decade, service by service. The pattern's power comes from continuous production testing: you learn far more about the new system's behaviour under real traffic than under load tests. The hardest part in practice is not the routing — it is the data model migration. The new service needs its own database, but the legacy database is the system of record. Change Data Capture (Debezium) or event-sourcing from the legacy system solves this without dual writes.

---

### ⚙️ How It Works (Mechanism)

**Migration stages:**

```
┌──────────────────────────────────────────────┐
│    Strangler Fig — Migration Stages          │
├──────────────────────────────────────────────┤
│ Stage 1: New service deployed (0% traffic)   │
│                                              │
│  Client → Gateway → 100% → [Monolith]        │
│                        0% → [New Service]    │
├──────────────────────────────────────────────┤
│ Stage 2: Canary (5-10% traffic)              │
│                                              │
│  Client → Gateway → 90% → [Monolith]         │
│                       10% → [New Service]    │
│  Monitor: errors, latency, business metrics  │
├──────────────────────────────────────────────┤
│ Stage 3: Full migration (100% traffic)       │
│                                              │
│  Client → Gateway → 0% → [Monolith]          │
│                    100% → [New Service]      │
│  Monolith code path still exists (rollback)  │
├──────────────────────────────────────────────┤
│ Stage 4: Legacy code deleted                 │
│                                              │
│  Client → Gateway → 100% → [New Service]     │
│  Monolith no longer handles this feature     │
└──────────────────────────────────────────────┘
```

**API Gateway routing rule (Spring Cloud Gateway):**

```yaml
# Route catalog requests: 95% legacy, 5% new service
spring:
  cloud:
    gateway:
      routes:
        - id: catalog-canary
          uri: http://new-catalog-service
          predicates:
            - Path=/api/products/**
            - Weight=catalog-group, 5
        - id: catalog-legacy
          uri: http://legacy-monolith
          predicates:
            - Path=/api/products/**
            - Weight=catalog-group, 95
```

**Data synchronisation with dual write:**

```java
// During migration: write to both systems
@Service
public class ProductService {
    private final NewCatalogRepository newRepo;
    private final LegacyCatalogClient legacyClient;

    @Transactional
    public void createProduct(CreateProductCommand cmd) {
        // Write to new system first (authoritative)
        Product product = newRepo.save(Product.from(cmd));
        // Sync to legacy (until legacy receives no reads)
        try {
            legacyClient.createProduct(
                LegacyProductDto.from(product)
            );
        } catch (Exception e) {
            // Log but do not fail — legacy is secondary
            log.warn("Legacy sync failed for {}", product.getId());
        }
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
Client Request → API Gateway / Proxy ← YOU ARE HERE → Routing Rule (% split) → New Service (% A) or Legacy Monolith (% B) → Response → Client

**FAILURE PATH:**
New service returns errors above threshold → Circuit breaker in gateway trips → 100% traffic reverts to legacy monolith → Alert fires → Team investigates → Fix deployed → Circuit breaker resets → Traffic ramps back up to new service

**WHAT CHANGES AT SCALE:**
At 10x traffic, maintaining dual-write synchronisation to legacy becomes a performance bottleneck — the legacy system was never designed for the new write volume. Solution: switch to change data capture (Debezium reading the legacy WAL) rather than dual writes. At 1000x, the monolith itself may not handle the load — use the Strangler Fig to extract the hottest features first, regardless of migration order preferences.

---

### 💻 Code Example

**Example 1 — Feature flag routing within a monolith (initial step):**

```java
// Before external routing: use feature flag to select
// new-style or legacy path within the monolith
@GetMapping("/products/{id}")
public ProductResponse getProduct(@PathVariable String id) {
    if (featureFlags.isEnabled("new-catalog-service", userId())) {
        // New path — calls new catalog service internally
        return newCatalogService.getProduct(id);
    }
    // Legacy path
    return legacyCatalogService.getProduct(id);
}
```

**Example 2 — Anti-corruption layer during migration:**

```java
// ACL translates legacy product to new domain types
// Enables new service to read legacy data during transition
@Component
public class LegacyCatalogAcl {
    public CatalogProduct translate(LegacyProductRecord r) {
        return CatalogProduct.builder()
            .id(ProductId.of(r.getPROD_ID()))
            .name(r.getPROD_NM())
            .price(Money.of(r.getPRICE_AMT(), "USD"))
            .category(Category.fromCode(r.getCATEGORY_CD()))
            .build();
    }
}
```

**Example 3 — Verify new and legacy return identical responses:**

```java
// Shadow mode test: call both, compare, alert on difference
@Component
public class ShadowModeProductController {
    public ProductResponse getProduct(String id) {
        ProductResponse legacy = legacyClient.getProduct(id);
        try {
            ProductResponse newSvc = newCatalogClient.getProduct(id);
            if (!newSvc.equals(legacy)) {
                metrics.increment("shadow.response.mismatch",
                    "product", id);
            }
        } catch (Exception e) {
            metrics.increment("shadow.call.error");
        }
        return legacy; // legacy is authoritative during shadow
    }
}
```

---

### ⚖️ Comparison Table

| Migration Strategy | Risk | Downtime | Duration | Reversibility |
|---|---|---|---|---|
| **Strangler Fig** | Low | None | Long | High at each step |
| Big Bang Rewrite | Very High | Yes (cutover) | Medium | None |
| Modular Monolith Refactor | Low | None | Medium | High |
| Parallel Run | Low | None | Long | High |
| Database-first Migration | Medium | None | Long | Medium |

How to choose: always prefer Strangler Fig over big-bang rewrite for production systems; use big-bang only when the legacy system cannot safely run alongside the new system (rare).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strangler Fig means you always end up with microservices | The pattern is about incremental migration — you could end up with a single new well-designed monolith replacing the legacy one |
| Data migration is straightforward with this pattern | Data migration is the hardest part — dual writes, CDC, and schema evolution require careful planning and are typically the migration bottleneck |
| You must extract features in dependency order | You can extract independent features in any order; you only need to respect dependency order when extracting tightly coupled features |
| The routing layer adds significant latency | A well-configured proxy or gateway adds 0.5–2ms — negligible compared to the latency of the services themselves |
| Once a feature is in the new service, the legacy code can be deleted immediately | Wait at least 1-2 weeks with 100% traffic to the new service before deleting legacy code; rollback windows should be respected |

---

### 🚨 Failure Modes & Diagnosis

**1. Data Inconsistency Between Legacy and New Service**

**Symptom:** A product shows different prices in legacy and new service. Customers using the new route see a lower price that isn't valid.

**Root Cause:** Dual write was implemented, but write failures to the legacy system were silently swallowed. The two systems diverged.

**Diagnostic:**
```bash
# Compare counts between legacy DB and new service DB
psql legacy_db -c "SELECT COUNT(*) FROM products"
psql new_catalog_db -c "SELECT COUNT(*) FROM products"
# Spot check individual records
curl http://legacy/products/123
curl http://new-catalog/products/123
```

**Fix:** Implement a reconciliation job that periodically compares key fields between systems and alerts on divergence. If diverged: reprocess CDC events to bring new system back in sync.

**Prevention:** Make legacy the system of record during dual write; treat failures to sync the new system as non-fatal but alertable; run daily reconciliation jobs.

**2. Routing Layer as Single Point of Failure**

**Symptom:** API Gateway crashes. All traffic — both legacy and new service — is unavailable simultaneously.

**Root Cause:** The routing layer was not built with high availability. A single gateway process without multiple replicas.

**Diagnostic:**
```bash
# Check gateway process health
kubectl get pods -n gateway
# Check for single-replica deployment
kubectl describe deployment api-gateway -n gateway | grep Replicas
```

**Fix:** Deploy the gateway with minimum 3 replicas across multiple availability zones. Use a Kubernetes PodDisruptionBudget to prevent all replicas being updated simultaneously.

**Prevention:** The routing layer is critical infrastructure — design it for higher availability than the services it routes to.

**3. Migration Stalls — Legacy Never Gets Smaller**

**Symptom:** Strangler Fig started 18 months ago. Three services have been extracted. The monolith still has 90% of the original code. The team is adding features to both old and new pathways.

**Root Cause:** Migration was not treated as a first-class engineering priority. Features continue to be added to the legacy path alongside extraction work.

**Diagnostic:**
```bash
# Track migration progress
git log --oneline --since="1 year ago" -- legacy-monolith/ | wc -l
git log --oneline --since="1 year ago" -- services/ | wc -l
# High legacy commit count = migration not prioritised
```

**Fix:** Implement a "feature freeze" on the legacy system — no new development in the monolith, only bug fixes. All new features go in new services. Set a concrete decommission date for the monolith with executive commitment.

**Prevention:** Make migration progress a tracked OKR. Assign 20–30% of team velocity explicitly to migration work in every sprint.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Anti-Corruption Layer` — the ACL is the translation mechanism that allows new services to read legacy data without adopting the legacy model
- `Service Decomposition` — determines which features to extract first and how to define the new service boundaries
- `API Gateway (Microservices)` — the routing layer that enables traffic splitting between legacy and new services

**Builds On This (learn these next):**
- `Canary Deployment (Microservices)` — the gradual traffic shifting used within each Strangler Fig extraction step
- `Database per Service` — the data isolation pattern that accompanies successful service extraction
- `Feature Flags (Microservices)` — an alternative routing mechanism for Strangler Fig within a monolith before external routing

**Alternatives / Comparisons:**
- `Big Bang Rewrite` — the alternative rejected by the Strangler Fig pattern: complete replacement in one step — high risk, no rollback
- `Modular Monolith` — an intermediate step where the monolith is restructured internally before service extraction begins

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Incremental legacy-to-microservices       │
│              │ migration using traffic routing to grow   │
│              │ new services while legacy shrinks         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Big-bang rewrites fail — too much risk,   │
│ SOLVES       │ too many untested edge cases, no rollback │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every extraction step is tested in        │
│              │ production. Failures are small and        │
│              │ reversible, not catastrophic              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Migrating a running production legacy     │
│              │ system that cannot be taken offline       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Greenfield system with no legacy — just   │
│              │ build the new architecture directly       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Low risk + reversibility vs dual system   │
│              │ maintenance cost during migration         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Never replace — grow around."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary Deployment → Feature Flags →       │
│              │ Database per Service                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are extracting the "Orders" service from a monolith using the Strangler Fig pattern. The Orders feature reads customer data from the monolith's `customers` table. Your new Orders service has its own database, but needs customer information. You have three options: (A) call the monolith's `/customers` API, (B) dual-write customer data to the new Orders DB, (C) use Change Data Capture from the monolith's DB. Walk through the failure scenarios for each approach under high load, and identify which is safest for zero-downtime migration.

**Q2.** Six months into a Strangler Fig migration, your team discovers that the newly extracted Inventory service has a subtle difference in low-stock calculation logic compared to the monolith. Both are in production handling real traffic. Shadow mode tests reveal the difference affects 0.3% of requests. Describe the exact steps to diagnose which implementation matches the actual business requirement, safely align both systems, and prevent similar divergence in the remaining migration steps.

