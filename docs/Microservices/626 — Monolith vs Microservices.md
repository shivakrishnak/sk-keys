---
layout: default
title: "Monolith vs Microservices"
parent: "Microservices"
nav_order: 626
permalink: /microservices/monolith-vs-microservices/
number: "626"
category: Microservices
difficulty: ★☆☆
depends_on: "Service Decomposition, Bounded Context"
used_by: "Modular Monolith, Strangler Fig Pattern, Service Discovery"
tags: #foundational, #architecture, #microservices, #distributed
---

# 626 — Monolith vs Microservices

`#foundational` `#architecture` `#microservices` `#distributed`

⚡ TL;DR — A **monolith** deploys all features in one unit; **microservices** decompose the system into independently deployable services. Monoliths are simpler to develop and test; microservices enable independent scaling and deployment but introduce distributed systems complexity.

| #626            | Category: Microservices                                    | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Service Decomposition, Bounded Context                     |                 |
| **Used by:**    | Modular Monolith, Strangler Fig Pattern, Service Discovery |                 |

---

### 📘 Textbook Definition

A **monolithic architecture** packages all application components — UI, business logic, data access — into a single deployable unit. The entire application is built, tested, and deployed as one artefact. A **microservices architecture** decomposes the system into small, independently deployable services, each owning its own data store and communicating over the network (HTTP/REST, gRPC, or messaging). Microservices are bounded by business capability (Domain-Driven Design's Bounded Context), deployed independently, and can be scaled individually. The trade-off: monoliths have lower operational complexity (one deployment, in-process calls, shared memory) but high coupling; microservices have lower coupling and independent scalability but require distributed systems tooling: service discovery, circuit breakers, distributed tracing, contract testing, and eventual consistency.

---

### 🟢 Simple Definition (Easy)

A monolith is one big application doing everything together. Microservices split that into many small, independent services — each doing one job. Monolith = easier to start; microservices = easier to scale one piece without touching the rest.

---

### 🔵 Simple Definition (Elaborated)

Imagine a restaurant. A monolith is one chef who cooks everything, takes orders, handles payments, and cleans up — fast and simple for a small café, but one sick chef shuts everything down. Microservices is a full restaurant team: one chef per cuisine, a separate waiter, a cashier, a cleaner — each can be replaced or doubled without stopping the others. But they need coordination (service discovery, communication protocols), and a mistake in communication between the cashier and chef (distributed failure) requires extra tooling to handle. The right choice depends on team size, traffic, and how independently different parts of the system need to evolve.

---

### 🔩 First Principles Explanation

**Comparison of key properties:**

```
PROPERTY              │ MONOLITH                     │ MICROSERVICES
──────────────────────┼──────────────────────────────┼──────────────────────────────
Deployment unit       │ One artefact (WAR/JAR/container)│ N independent containers
Communication         │ In-process method calls      │ Network calls (HTTP, gRPC, MQ)
Data store            │ Shared database              │ Database per service
Scalability           │ Scale entire application     │ Scale individual services
Failure isolation     │ One bug can crash everything │ Failure limited to one service
Team autonomy         │ All teams share one codebase │ Each team owns their service
Operational complexity│ Low (one deployment)         │ High (N services + infra)
Testing               │ Easier (in-process, no mocks)│ Harder (contract testing needed)
Development start     │ Fast (no infra setup)        │ Slow (service mesh, tracing...)
Latency               │ In-process: microseconds     │ Network: milliseconds + retries
Data consistency      │ ACID transactions             │ Eventual consistency (Saga)
```

**Three deployment models:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. MONOLITH                                                     │
│   [UI + Business Logic + Data Access] → [Single Database]      │
│   Deployed as one JVM process or container                      │
│   All teams commit to one repo, one build, one deploy          │
│                                                                 │
│ 2. MODULAR MONOLITH (Majestic Monolith)                        │
│   [Module A | Module B | Module C] → [Single Database]         │
│   One deployment unit but internally divided by domain         │
│   Enforced module boundaries (Java modules, packages)          │
│   Easier path to microservices if needed                        │
│                                                                 │
│ 3. MICROSERVICES                                                │
│   [Service A]─HTTP─[Service B]─MQ─[Service C]                 │
│   [DB-A]         [DB-B]         [DB-C]                         │
│   Each independently deployed, scaled, and versioned           │
│   API Gateway as single entry point for clients                │
└─────────────────────────────────────────────────────────────────┘
```

**When microservices do NOT help:**

```
Anti-patterns for premature microservices:
1. TEAM TOO SMALL: fewer than 3–5 teams → microservices add overhead with no benefit
2. DOMAIN NOT UNDERSTOOD: splitting before understanding boundaries creates wrong splits
   → "distributed monolith": services so tightly coupled they deploy together anyway
3. NO CI/CD PIPELINE: microservices require automated deployment per service
4. NO OBSERVABILITY: distributed tracing and logging are essential, not optional
5. SHARED DATABASE: multiple services using one DB = distributed monolith's worst form

Heuristic: start with a monolith (or modular monolith).
Extract services when: a team owns a clear domain, independent scaling is needed,
or deployment coupling is causing release friction.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT microservices (pure monolith at scale):

What breaks without it:

1. Scaling: must scale the entire application even if only the payment module is under load.
2. Deployment: one small change requires deploying the entire application — high risk.
3. Team autonomy: all teams coordinate on one codebase — merge conflicts, release coordination overhead.
4. Technology lock-in: entire system must use the same language, framework, database.

WITH microservices:
→ Payment service scales independently during Black Friday without scaling the user profile service.
→ Teams deploy their service independently — no cross-team release coordination.
→ A failure in the recommendation service does not affect the checkout service (failure isolation).
→ Each service can choose the best technology for its domain (polyglot persistence).

---

### 🧠 Mental Model / Analogy

> A monolith is a Swiss Army knife — everything in one compact tool. Perfect for everyday tasks, simple to carry. Microservices is a full toolbox — each tool is specialised, replaceable, and the best tool for its job. But you need a bigger bag, and if you drop the bag (infrastructure failure), you need to reassemble. Neither is universally better — the Swiss Army knife is ideal for camping; the full toolbox is essential for a professional workshop.

"Swiss Army knife" = monolith (one unit, all features, simple)
"Full toolbox" = microservices (specialised, independent, complex infra)
"Camping" = early-stage startup, small team
"Professional workshop" = large org, multiple teams, independent scale requirements

---

### ⚙️ How It Works (Mechanism)

**Distributed monolith — the worst of both worlds:**

```
WRONG: microservices in name only
  OrderService ──────────────────────────► UserService
       │ (synchronous HTTP REQUIRED)       (shared DB!)
       │ If UserService is down:
       │ OrderService FAILS → not failure isolated
       │ Both services deploy together (shared schema)
       ▼
  PaymentService
       │ (calls UserService too)
       ▼ (same shared database!)
  [Single Postgres DB]  ← ALL services share one DB
                        ← Schema changes require all services to redeploy
                        ← ACID transactions across "services" = just a monolith over HTTP
RESULT: network overhead of microservices + coupling of monolith
```

---

### 🔄 How It Connects (Mini-Map)

```
Monolith vs Microservices  ◄──── (you are here)
(fundamental architectural choice)
        │
        ├── Modular Monolith    → middle ground: one deploy, module boundaries
        ├── Strangler Fig Pattern → migration path from monolith to microservices
        ├── Service Decomposition → how to split the monolith
        ├── Bounded Context     → DDD principle for service boundaries
        ├── Service Discovery   → microservices infra: how services find each other
        └── API Gateway         → single entry point for microservices clients
```

---

### 💻 Code Example

**Modular monolith with enforced boundaries (Java modules):**

```java
// module-info.java for the orders module — enforces boundaries
module com.example.orders {
    requires com.example.products; // declares dependency explicitly
    exports com.example.orders.api; // only API package is public
    // com.example.orders.internal is NOT exported → other modules can't access it
}

// Cross-module call: OrderService calls ProductService via its public API
// (not a network call — still in-process, but bounded like microservices)
@Service
class OrderService {
    @Autowired ProductCatalogApi productApi; // public API of products module

    public Order createOrder(OrderRequest req) {
        Product product = productApi.findById(req.getProductId()); // in-process call
        return new Order(product, req.getQuantity());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                              |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Microservices always means better performance | Microservices introduce network latency for every inter-service call (milliseconds instead of microseconds). Performance is typically WORSE for individual requests unless the benefit of independent scaling outweighs the overhead |
| Microservices require separate teams          | Microservices are most valuable when aligned with team ownership (Conway's Law). A single team maintaining 20 microservices gets operational complexity with no autonomy benefit                                                     |
| A monolith cannot scale                       | Monoliths can be horizontally scaled (multiple instances behind a load balancer). They just cannot scale individual components independently — but for many workloads, that is not required                                          |
| Microservices solve organisational problems   | Microservices amplify existing team structures. A poorly-organised team will create a poorly-organised microservices system. Team structure and ownership boundaries must be designed first                                          |

---

### 🔥 Pitfalls in Production

**Chatty microservices — network amplification**

```
CHATTY PATTERN (N calls to render one page):
  User → API Gateway → OrderService
                         → UserService (get user name)    +1 call
                         → ProductService (per order item) +N calls
                         → InventoryService (per item)    +N calls
  For a 20-item order: 1 + 1 + 20 + 20 = 42 network calls
  At 2ms each: 84ms of network overhead (just for one page render)

BETTER: API Gateway aggregation or Backend-for-Frontend (BFF)
  User → BFF → (single enriched query per downstream service)
  BFF assembles the response, microservices expose efficient bulk APIs
```

---

### 🔗 Related Keywords

- `Modular Monolith` — the middle ground between monolith and microservices
- `Service Decomposition` — the strategies for splitting a monolith into services
- `Bounded Context` — the DDD principle that defines service boundaries
- `Strangler Fig Pattern` — the incremental migration from monolith to microservices
- `API Gateway (Microservices)` — the single entry point that the microservices architecture requires

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│             │ MONOLITH           │ MICROSERVICES          │
├─────────────┼────────────────────┼────────────────────────┤
│ Deploy      │ One artefact       │ N independent services │
│ Comms       │ In-process         │ Network (HTTP/MQ)      │
│ Data        │ Shared DB          │ DB per service         │
│ Scaling     │ Whole app          │ Per service            │
│ Complexity  │ Low (start)        │ High (distributed)     │
├─────────────┴────────────────────┴────────────────────────┤
│ RULE: Start monolith → extract service when:             │
│   team owns domain + independent scaling needed          │
│   + you have CI/CD + observability in place              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Conway's Law states that "organisations design systems that mirror their own communication structure." Explain how this applies to the monolith vs microservices decision: if an organisation has 3 teams all working on one codebase, what architectural form will naturally emerge? And conversely, if you force microservices onto a single team, what coordination overhead emerges? Describe the "Inverse Conway Manoeuvre" — restructuring teams first to drive the desired architecture, rather than restructuring architecture to force team separation.

**Q2.** A "distributed monolith" combines the worst of both worlds. Define the two key signatures of a distributed monolith: (1) synchronous coupling — service A cannot function if service B is unavailable, and (2) deployment coupling — services must be deployed in a specific order or simultaneously. For each signature, describe what design decision caused it (synchronous HTTP without circuit breaker, shared database schema) and what architectural change would fix each one (async messaging + circuit breaker; database per service + data replication).
