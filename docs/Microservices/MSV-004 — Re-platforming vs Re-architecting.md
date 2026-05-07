---
layout: default
title: "Re-platforming vs Re-architecting"
parent: "Microservices"
nav_order: 4
permalink: /microservices/re-platforming-vs-re-architecting/
number: "MSV-004"
category: Microservices
difficulty: ★★★
depends_on: On-Premises to Cloud Migration, Technology Migration Strategy, Containers, Twelve-Factor App
used_by: Technology Migration Strategy, Monolith to Microservices Migration
related: On-Premises to Cloud Migration, Technology Migration Strategy, Twelve-Factor App, Strangler Fig Pattern
tags:
  - architecture
  - advanced
  - microservices
  - cloud
  - tradeoff
  - pattern
---

# MSV-004 — Re-platforming vs Re-architecting

⚡ TL;DR — Re-platforming optimises an existing application for cloud managed services with minimal code change; Re-architecting redesigns it as cloud-native from the ground up.

| #2283 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | On-Premises to Cloud Migration, Technology Migration Strategy, Containers, Twelve-Factor App | |
| **Used by:** | Technology Migration Strategy, Monolith to Microservices Migration | |
| **Related:** | On-Premises to Cloud Migration, Technology Migration Strategy, Twelve-Factor App, Strangler Fig Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A senior architect faces a decision: an application currently runs on a self-managed Tomcat server with a self-managed MySQL database. Moving to AWS. Option A: swap Tomcat for ECS Fargate, swap MySQL for RDS — minor operational changes, application code largely unchanged. Option B: break the application into microservices, adopt SQS for async messaging, redesign the database into per-service schemas, containerise everything. Same business requirement, radically different effort, risk, and business value. Without a framework for choosing, teams default to either "modernise everything" (over-engineering) or "change nothing" (missing cloud value).

**THE BREAKING POINT:**
Defaulting to re-architecting everything wastes engineering capacity on redesigns that deliver marginal incremental value. Defaulting to re-platforming everything leaves architectural debt in place, preventing teams from achieving the scale, velocity, and resilience that cloud-native architectures enable. The decision matters enormously per application.

**THE INVENTION MOMENT:**
AWS's migration framework (and subsequent adaptations) formalised the distinction: **Re-platforming** = cloud-optimised operational improvements with minimal code change ("lift-tinker-and-shift"). **Re-architecting** = redesign fundamentals for cloud-native patterns, accepting higher upfront cost for long-term architectural value.

---

### 📘 Textbook Definition

**Re-platforming** (Replatform, "Lift-Tinker-and-Shift") is a migration strategy that moves an application to the cloud while making targeted optimisations for managed cloud services — replacing self-managed components with managed equivalents (self-managed DB → RDS, self-managed app server → ECS/App Service, on-prem message queue → SQS/Service Bus) — without changing the application's fundamental architecture or code.

**Re-architecting** (Refactor) is a migration strategy that redesigns the application's architecture to be cloud-native, applying patterns such as microservices decomposition, event-driven architecture, serverless functions, or containerised 12-Factor Apps. Re-architecting requires significant code changes and architectural redesign.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Re-platform: swap the engine without changing the car. Re-architect: design a new car from the ground up.

**One analogy:**
> Upgrading a kitchen. Re-platforming: replace the gas hob with an induction hob, the old fridge with a smart fridge — the kitchen layout unchanged, just better appliances. Re-architecting: tear out walls, reconfigure the entire space, install an island counter, open-plan layout — a fundamentally different kitchen. Both are improvements; the choice depends on where you live and what you cook.

**One insight:**
The choice between re-platforming and re-architecting is primarily a business ROI decision, not a technical preference. Re-platform when the operational improvement (reduced management overhead, SLA improvement) justifies the effort. Re-architect when the scaling, velocity, or resilience requirements are fundamentally unachievable with the current architecture.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Re-platforming preserves the application's domain logic and data model unchanged.
2. Re-architecting changes at least one of: data model, communication model (sync→async), or deployment model (monolith→microservices).
3. Re-platforming delivers operational benefit; re-architecting delivers both operational and architectural benefit.
4. Re-architecting scope is always larger, riskier, and more expensive than re-platforming for the same application.
5. Neither option is universally correct — the right choice is per-application based on business value vs. migration cost.

**DERIVED DESIGN:**
From invariants 3 and 4: use re-platforming as the default strategy for applications where the primary goal is cloud migration (cost reduction, managed services). Reserve re-architecting for applications where architectural change enables new business capabilities (scalability, team autonomy, compliance) that re-platforming cannot deliver.

Decision test: "If we re-platform this application, can we meet the next 3 years of business requirements?" If yes → re-platform. If no → re-architect.

**THE TRADE-OFFS:**
**Re-platform: Gain:** Lower risk, faster migration, immediate operational benefit (managed patches, HA, backups), reduced code change.
**Re-platform: Cost:** Architectural debt remains; scaling ceiling remains; future re-architecture more costly when eventually required.
**Re-architect: Gain:** Cloud-native scalability; team autonomy (microservices); long-term operational excellence; 12-Factor compliance.
**Re-architect: Cost:** Higher upfront cost (6–18 months); significant risk; requires DDD analysis; creates distributed systems complexity.

---

### 🧪 Thought Experiment

**SETUP:**
Two applications: (A) internal HR system used by 200 employees, 10 requests/minute, no scaling requirements. (B) Customer checkout system used by 1M customers, peak 50,000 requests/minute on Black Friday, with PCI compliance requirements.

**WHAT HAPPENS — HR system re-architectured:**
Team spends 12 months decomposing the HR system into 8 microservices. Kubernetes cluster deployed. Event-driven messaging with Kafka. Total cost: $800K. Business benefit: HR system works identically as before, but is now 10× more complex to operate. 200 employees notice no difference.

**WHAT HAPPENS — HR system re-platformed:**
Self-managed Tomcat + MySQL → ECS Fargate + RDS. 6 weeks. Cost: $30K. Result: same application, zero management overhead for OS, patches, or DB backups. Cost saving: $80K/year in operational time. Business benefit: high.

**WHAT HAPPENS — Checkout system re-architected:**
Payment, Cart, Inventory separated into independent microservices. Each scales independently. Black Friday: Payment scales to 200 pods; Cart to 150. No single-service failures cascade. PCI scope isolated to Payment service only. Team deploys independently.

**THE INSIGHT:**
Re-platform the HR system (operational improvement at low cost). Re-architect the checkout system (architectural capability at justified cost). The application's scaling requirement and failure cost determine which applies.

---

### 🧠 Mental Model / Analogy

> Think of a fleet of company vehicles. Re-platforming is replacing petrol with hybrid engines — same chassis, same purpose, more efficient. Re-architecting is replacing the car fleet with motorcycles and vans — better suited to specific roles, fundamentally different capability, requires driver retraining.

- "Petrol → hybrid" → re-platform (better efficiency, same shape)
- "Cars → motorcycles + vans" → re-architect (different form factor, different capability)
- "Driver retraining" → team skill development for microservices / cloud-native
- "Fleet assessment: which vehicles need what?" → per-application migration strategy

Where this analogy breaks down: vehicle replacement is a cost decision with no code dependency. Re-architecting an application creates integration dependencies with other systems that must also adapt — a cascade of changes not present in vehicle fleets.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Re-platforming means moving your application to the cloud with small improvements — like upgrading from a car's engine without changing the car. Re-architecting means redesigning the entire car — new structure, new engine, new capabilities. Re-platforming is faster and safer; re-architecting delivers more powerful long-term results but takes much longer and costs more.

**Level 2 — How to use it (junior developer):**
For re-platforming: identify self-managed components replaceable with managed equivalents. Self-managed MySQL → RDS MySQL (same engine, no app code change). Self-managed Redis → ElastiCache (same client library). Self-managed Tomcat → ECS Fargate (same WAR deployment, containerised). For re-architecting: conduct DDD analysis. Identify bounded contexts. Separate domain logic into individual services. Redesign database per service. Introduce event-driven communication where appropriate.

**Level 3 — How it works (mid-level engineer):**
Re-platform decision checklist: (1) Can the application's runtime be containerised with no code changes? (2) Can self-managed databases be replaced with managed equivalents without schema changes? (3) Can self-managed caches/queues be replaced with PaaS equivalents using the same client API? If all three: re-platform is viable. Re-architect decision checklist: (1) Does the application need to scale specific components independently? (2) Does the deployment coupling between modules block team velocity? (3) Does the failure blast radius need to be reduced? (4) Does compliance require isolation (e.g., PCI scope reduction)? If any answer is yes → re-architect candidate.

**Level 4 — Why it was designed this way (senior/staff):**
The re-platform vs. re-architect decision is fundamentally about **where the cost is paid**: re-platforming pays later (architectural debt accumulates; future re-architect is more expensive when the system is larger), re-architecting pays now (high upfront cost delivers architectural ROI compounding over time). The optimal strategy minimises total cost of ownership over a 5–10 year horizon. For stable, low-churn systems, re-platforming's lower upfront cost is never "repaid" because re-architecting never becomes necessary. For high-growth, high-churn systems, early re-architecting prevents exponentially increasing re-architect cost as the system grows.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  RE-PLATFORM vs RE-ARCHITECT — DECISION FLOW           │
│                                                        │
│  Does the application need:                            │
│  ├─ Independent scaling of components? ── Yes          │
│  ├─ Independent team deployment? ──────── Yes  →  RE-  │
│  ├─ Compliance isolation? ─────────────── Yes  ARCH-   │
│  └─ Reduced blast radius? ─────────────── Yes  ITECT   │
│                                                        │
│  All No? → RE-PLATFORM:                                │
│  Self-managed DB    → Managed DB (RDS, CloudSQL)       │
│  Self-managed cache → Managed cache (ElastiCache)      │
│  VM-based app       → Container (ECS/App Service)      │
│  Self-managed queue → Managed queue (SQS/Service Bus)  │
│                                                        │
│  Re-platform effort: weeks                             │
│  Re-architect effort: months to years                  │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Re-platform):**
```
Current: Tomcat on EC2 + self-managed MySQL on EC2
  → Containerise app: create Dockerfile (no code change)
    [← YOU ARE HERE: re-platform begins]
  → Deploy to ECS Fargate (managed container runtime)
  → Migrate DB: AWS DMS replicates to RDS MySQL
  → Update connection string: MySQL endpoint → RDS endpoint
  → Test: functional parity confirmed
  → DNS cutover → Decommission old EC2 instances
Result: same application, zero OS/DB management overhead
```

**FAILURE PATH (Re-architect prematurely):**
```
HR system chosen for re-architect (low value, low scale)
  → 8 microservices designed
  → 4 months into development: service mesh needed
  → 6 months: distributed tracing required
  → 8 months: data consistency issues across services
  → 12 months: still not in production
  → Cost: 10× original estimate
  → Original HR system still running, no users migrated
[This is the re-architect anti-pattern for wrong workloads]
```

**WHAT CHANGES AT SCALE:**
At 50 apps: re-platform decisions dominate (faster value). At 200 apps: re-architect reserved for top 20% highest value/scale. At 1,000+ apps: re-platform is the default; re-architect requires business case justification.

---

### 💻 Code Example

**Example 1 — Re-platform: containerise + managed DB:**

```dockerfile
# Re-platform: containerise existing app, no code change
FROM eclipse-temurin:11-jre
COPY target/hr-system.war /app/app.war
# Same WAR as on-premises — no code modifications
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.war"]
```

```yaml
# Re-platform: RDS replaces self-managed MySQL
# Application connection string update only:
spring:
  datasource:
    # Before: jdbc:mysql://on-prem-server:3306/hrdb
    # After: RDS endpoint (same MySQL driver, same schema)
    url: jdbc:mysql://hrdb.cluster-xxx.rds.amazonaws.com:\
         3306/hrdb
    # No application code changes required
```

**Example 2 — Re-architect: microservice decomposition:**

```java
// BAD (monolith - re-platform this): all in one service
@Service
public class HRService {
    void processPayroll() { /* ... */ }
    void manageLeave() { /* ... */ }
    void handleRecruitment() { /* ... */ }
    void generateReports() { /* ... */ }
}

// GOOD (re-architect - for checkout system with scale need):
// Separate services: PaymentService, CartService,
//                    InventoryService, NotificationService
// Each: own database, own deployment, own scaling policy
@SpringBootApplication
public class PaymentServiceApplication {
    // Only payment domain logic — independent deployable
    // Independent DB: payment_schema in PostgreSQL
    // Async communication: publishes PaymentCompleted event
}
```

---

### ⚖️ Comparison Table

| Dimension | Re-platform | Re-architect |
|---|---|---|
| **Code changes** | Minimal (config, connection strings) | Significant (new services, new architecture) |
| **Migration time** | Weeks to 3 months | 6–18 months |
| **Risk** | Low | High |
| **Operational benefit** | High (managed services) | Very high (cloud-native) |
| **Scaling benefit** | Moderate (vertical + managed scaling) | High (independent horizontal scaling) |
| **Team velocity benefit** | Low | High (independent deployability) |
| **Best for** | Stable, low-churn systems | High-growth, high-scale, complex-domain systems |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Re-architecting is always better | Re-architecting is better for the right applications. For stable, low-scale applications, the re-architect cost exceeds the lifetime operational benefit |
| Re-platforming is "giving up" | Re-platforming is a deliberate, strategic choice. It delivers real operational value (managed services, HA, automated backups) with minimal risk |
| You can only choose one approach per migration programme | A portfolio migration applies multiple strategies: some apps rehosted, some replatformed, some re-architected, some retired. The 6Rs coexist |
| Re-architect and re-platform are mutually exclusive phases | For some applications, re-platforming is the first step: containerise and get onto managed services, then re-architect into microservices 12–18 months later when the domain is better understood |

---

### 🚨 Failure Modes & Diagnosis

**1. Re-architecting for the Wrong Reasons**

**Symptom:** Microservices migration completed for an internal tool with 50 users. 5 services deployed on Kubernetes. Team spends 40% of time managing service mesh, distributed tracing setup, and Kubernetes cluster updates. No business benefit gained.

**Root Cause:** Re-architect decision driven by technology enthusiasm rather than business requirement analysis.

**Diagnostic:**
```bash
# Calculate re-architect ROI for this workload:
echo "Concurrent users: 50"
echo "Scaling requirement: NO"
echo "Team deployment frequency: monthly"
echo "Team size: 2 engineers"
# If all metrics are low: re-architect unjustified
```

**Fix:** Recognise the decision was wrong. Consolidate microservices back into a modular monolith. Decommission Kubernetes for this workload. Apply re-platform (ECS + RDS) instead.

**Prevention:** Apply business value scoring before re-architect decisions. Require explicit justification for each microservice: "we need independent scaling of X" or "team Y cannot deploy independently without separating Z."

---

**2. Re-platform Becomes Re-architect Mid-Stream**

**Symptom:** "Simple" re-platform of Tomcat to ECS evolves to include redesigning the session management, splitting a monolithic config into 12-Factor env vars, and reimplementing caching. Timeline triples.

**Root Cause:** Re-platform scope not strictly bounded. Every "small improvement" is added to the migration.

**Diagnostic:**
```bash
# Count PRs touching application logic vs config:
git log --oneline --since="migration-start" \
  | grep -v "config:\|infra:\|ci:" | wc -l
# High count of non-config changes = scope creep
```

**Fix:** Freeze re-platform scope: only infrastructure replacements (container, managed services). Any application logic changes are separate tickets, separate sprint, post-migration.

**Prevention:** Define re-platform acceptance criterion: "no changes to application source files." Any source file change is re-architect scope, not re-platform.

---

**3. Database Re-platform Fails Schema Compatibility**

**Symptom:** Application connects to RDS but errors with colum-not-found or syntax errors. Self-managed MySQL 5.7 → RDS MySQL 8.0 introduced breaking changes.

**Root Cause:** Database engine version change during re-platform introduced incompatibilities in SQL syntax, collation, or storage engine behaviour.

**Diagnostic:**
```bash
# Run AWS Schema Conversion Tool:
aws dms create-replication-task \
  --migration-type full-load \
  --table-mappings file://mapping.json \
  --replication-task-settings file://settings.json
# Review conversion report for incompatibilities
```

**Fix:** Use AWS SCT to identify and resolve schema incompatibilities before cutover. Test application against the target RDS version in a staging environment for 2 weeks before production migration.

**Prevention:** Never change DB engine version as part of a re-platform. Database engine version upgrades are a separate, subsequent step after the re-platform is stable.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `On-Premises to Cloud Migration` — the broader migration programme within which re-platform and re-architect decisions are made per application
- `Twelve-Factor App` — the design methodology that defines cloud-native re-architected applications; understanding 12-Factor principles is required to assess re-architect suitability

**Builds On This (learn these next):**
- `Monolith to Microservices Migration` — the re-architect path applied to monolithic applications; builds on the re-architect decision with a specific execution strategy
- `Technology Migration Strategy` — the programme-level framework that orchestrates many individual re-platform and re-architect decisions into a coherent migration wave plan

**Alternatives / Comparisons:**
- `Rehost (Lift-and-Shift)` — the most minimal migration strategy: move VMs as-is with no optimisation; less effort than re-platform but no cloud benefit gained
- `Modular Monolith` — an intermediate architecture between re-platform (unchanged monolith) and re-architect (microservices); improves internal modularity without full decomposition

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two cloud migration strategies: swap       │
│              │ components (re-platform) vs. redesign     │
│              │ architecture (re-architect)               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Choosing wrong migration depth: over-     │
│ SOLVES       │ engineering or under-delivering per app   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Business requirement drives the choice:   │
│              │ re-platform if next 3 years are achievable│
│              │ on same architecture; re-architect if not │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Re-platform: stable, low-scale, low-churn │
│              │ Re-architect: high-scale, high-velocity,  │
│              │ team autonomy or compliance required      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Re-architect: when scale/velocity need    │
│              │ doesn't justify the cost and risk        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Re-platform: low risk, fast, operational  │
│              │ improvement only. Re-architect: high risk,│
│              │ slow, architectural + operational benefit │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Re-platform: better engine, same car.    │
│              │  Re-architect: entirely new vehicle."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strangler Fig → 12-Factor App →           │
│              │ Monolith to Microservices → FinOps        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An application has been re-platformed to AWS ECS + RDS. The product team now wants to add real-time features (WebSocket connections to 500k concurrent users) and personalisation (ML inference per request). The current monolithic architecture cannot meet these requirements. Describe the re-architect strategy: which components require decomposition, what the new service boundaries are, and how you'd execute the re-architect without taking the re-platformed application offline during the transition.

**Q2.** A company has re-platformed 80 applications over 18 months. The cloud bill is 40% lower than on-premises costs. A new architecture review reveals that 20 of those 80 applications are now scaling bottlenecks — they need independent component scaling that re-platforming didn't enable. Evaluate the decision: should those 20 apps now be re-architected (making the earlier re-platform a "wasted" step), or is there a path that builds incrementally on the re-platform investment?

**Q3.** Re-architecting into microservices creates distributed systems complexity: network failures, eventual consistency, distributed tracing overhead. For a team of 5 engineers migrating a medium-complexity e-commerce application, at what team size / transaction volume / deployment frequency threshold does the re-architect trade-off become positive (benefits exceed costs), and what metrics would you track to validate that threshold was correctly identified?

