---
id: MSV-001
title: What Are Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★☆☆
depends_on:
used_by: MSV-002, MSV-003, MSV-004, MSV-005
related: MSV-006, DST-001, SAP-001
tags:
  - microservices
  - foundational
  - mental-model
  - architecture
status: complete
version: 1
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 1
permalink: /msv/what-are-microservices/
---

# MSV-001 - What Are Microservices

⚡ **TL;DR —** An architectural style that structures an application as a collection of small, independently deployable services, each owning its data and communicating over a network.

| Field          | Value                              |
| -------------- | ---------------------------------- |
| **Depends on** | —                                  |
| **Used by**    | MSV-002, MSV-003, MSV-004, MSV-005 |
| **Related**    | MSV-006, DST-001, SAP-001          |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Large applications are built as a single deployable unit — the monolith. One codebase, one database, one deployment artifact. To change one feature, you check out the entire codebase, rebuild the entire system, and deploy the entire application. A bug in the payments module can take down the recommendation engine. Teams working on different features block each other's releases.

**THE BREAKING POINT:**
At some scale of organisational and technical complexity, the monolith becomes a deployment bottleneck. A 200-engineer team working on one codebase: merge conflicts are constant, CI pipelines take 40 minutes, one team's bad deployment takes down every feature, and the deployment cycle slows to monthly because coordination cost is too high.

**THE INVENTION MOMENT:**
The insight was that independent deployability requires physical separation. If two components must be deployed together, you cannot change one without risking the other. The solution: split the application into separate processes, each running independently, each ownable by one team, each deployable without touching the others.

**EVOLUTION:**
Amazon's move to service-oriented architecture (2002, mandated by Jeff Bezos) is an early reference implementation. The term "microservices" was popularised by Martin Fowler and James Lewis in 2014, synthesising emerging practices at Netflix, Amazon, and Spotify. Docker (2013) and Kubernetes (2014) made independent deployment operationally tractable. The discipline evolved from "split the monolith" to "design services around business capabilities with independent data ownership."

---

### 📘 Textbook Definition

**Microservices** is an architectural style in which a single application is composed of many small, independently deployable services. Each service:

- Runs in its own process
- Communicates with other services over lightweight mechanisms (HTTP, gRPC, messaging)
- Is built around a specific business capability
- Is independently deployable
- Can use different programming languages and data stores

---

### ⏱️ Understand It in 30 Seconds

**One line:** Small, independently deployable services that each own a business capability and its data.

> _Think of a restaurant: the kitchen, the bar, the front-of-house, and the billing desk are separate teams with separate tools and separate processes — but they collaborate to deliver one customer experience._

**One insight:** The primary benefit of microservices is not technical — it is organisational. Independent deployment enables independent teams.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Each service is independently deployable — deploying service A cannot require deploying service B.
2. Each service owns its data — no shared database between services.
3. Services communicate over a network — all interaction is explicit (no shared memory, no shared code).
4. Services are sized by business capability, not by technical layer.

**DERIVED DESIGN:**
These invariants derive from Conway's Law: "Any organisation that designs a system will produce a design whose structure is a copy of the organisation's communication structure." Microservices make this explicit: one team owns one service. If you want two teams to work independently, they need two independently deployable components.

**THE TRADE-OFFS:**

- **Gain:** Independent deployment, independent scaling, technology freedom per service, fault isolation, team autonomy.
- **Cost:** Network latency between services, distributed systems complexity (partial failure, eventual consistency), operational overhead (many services to monitor and deploy), data consistency challenges.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

- **Essential:** Network communication is real cost. Data ownership requires coordination. Independent deployment requires a deployment platform. These costs exist regardless of implementation.
- **Accidental:** Service-per-function granularity (too fine-grained), shared library coupling, synchronous communication everywhere. These are implementation choices that can be avoided.

---

### 🧪 Thought Experiment

**SETUP:** You have a shopping application: product catalogue, shopping cart, payments, and user accounts. All in one monolith, one database, one deployment.

**WHAT HAPPENS WITHOUT MICROSERVICES:**
Black Friday: the payment service needs 10x capacity. You must scale the entire monolith 10x — including the product catalogue that doesn't need scaling. The payments team adds a security patch that requires a deployment. The cart team's half-finished feature is accidentally included and breaks checkout for 30 minutes. The entire application goes down.

**WHAT HAPPENS WITH MICROSERVICES:**
Payment service scales to 10x independently. The payments team deploys their security patch without touching the cart service. The cart team deploys their feature on their own schedule. A crash in the product catalogue doesn't affect the payment flow.

**THE INSIGHT:**
Microservices are a solution to the problem of organisational scale. When one team can deploy without waiting for another team, each team moves at its own speed.

---

### 🧠 Mental Model / Analogy

> _Microservices are like a city of specialist shops, each independently owned, versus a department store where everything is under one roof._

- A specialist shoe shop = one microservice (focused, independently managed)
- A department store = monolith (everything together, coordinated management required)
- The high street = the network (shops communicate by sending customers to each other)
- Each shop's stock room = its own database (no shared warehouse)

Where this analogy breaks down: shops in a city don't need millisecond-level coordination; microservices often need sub-100ms communication, making network reliability critical in a way that physical shops don't experience.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of one big program that does everything, you build many small programs. Each small program does one specific job (like "handle payments" or "manage user accounts"). They talk to each other to get things done together.

**Level 2 - How to use it (junior developer):**
You structure your application so that each service (e.g., `OrderService`, `PaymentService`, `NotificationService`) is a separate deployable unit. Each service has its own codebase, runs as its own process (e.g., a Docker container), exposes an API (HTTP or gRPC), and has its own database. Teams deploy their service independently using a CI/CD pipeline.

**Level 3 - How it works (mid-level engineer):**
Each service registers with a service registry (or is discovered via Kubernetes DNS). Services communicate via HTTP/REST, gRPC, or async messages. Data consistency across services requires eventual consistency patterns (sagas, outbox pattern) because you cannot use a distributed transaction. API gateways route external traffic to the right service. Distributed tracing (OpenTelemetry) correlates requests across services.

**Level 4 - Why it was designed this way (senior/staff):**
The microservices architecture is a sociotechnical design pattern, not a purely technical one. It externalises the coupling that exists between business capabilities. In a monolith, a team can accidentally couple to another team's code (compile-time coupling). In microservices, all coupling is explicit and network-mediated. The design enables Conway's Law alignment: the architecture matches the org structure. The costs (network latency, distributed consistency) are real but accepted in exchange for team autonomy and independent deployment velocity.

**Expert Thinking Cues:**

- "If two services must be deployed together, they are one logical service in two physical parts — the split doesn't buy you the autonomy you think it does."
- "The database is the hardest part. Shared databases are monolith coupling disguised as microservices."
- "Microservices have a team-size prerequisite. Below ~5 engineers per service, the operational overhead exceeds the autonomy benefit."

---

### ⚙️ How It Works (Mechanism)

**SERVICE IDENTIFICATION:**
Services are discovered via service registry (Consul, Eureka) or Kubernetes DNS (every service gets a DNS name: `payment-service.default.svc.cluster.local`). The caller resolves the name to an IP, establishes a connection (HTTP, gRPC, TCP), and makes a request.

**DATA ISOLATION:**
Each service has its own database schema (or entire database instance). No service reads another service's database directly. Cross-service data queries require an API call or an event subscription.

**INTER-SERVICE COMMUNICATION:**

- **Synchronous:** HTTP/REST or gRPC — the caller blocks waiting for a response.
- **Asynchronous:** Message queues (Kafka, RabbitMQ) — the caller publishes an event and continues; the downstream service processes it independently.

**FAILURE ISOLATION:**
Circuit breakers (Resilience4j, Hystrix) prevent cascading failures. If `PaymentService` is down, a circuit breaker in `OrderService` stops sending requests to `PaymentService` and returns a fallback response, preventing `OrderService` from also going down.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Client
  |
  v
API Gateway (routing, auth, rate limit)
  |
  +---> OrderService <- YOU ARE HERE
  |         |
  |         +---> PaymentService (sync gRPC)
  |         |
  |         +---> NotificationService (async event)
  |
  +---> ProductService (independent)
```

**FAILURE PATH:**
PaymentService is slow (5s timeout). OrderService's circuit breaker opens after 5 failures. OrderService returns a "payment pending" response. An async retry job later attempts payment again. NotificationService is unaffected.

**WHAT CHANGES AT SCALE:**

- Service discovery becomes complex (hundreds of services, dynamic IPs).
- Distributed tracing becomes mandatory (correlating one user request across 15 service calls).
- API versioning becomes critical (many services evolve at different rates).
- Data consistency becomes the dominant engineering challenge.

---

### 💻 Code Example

**BAD — Direct database access across services:**

```java
// OrderService reaching into PaymentService's DB
@Repository
public class OrderRepository {
    // WRONG: OrderService must NEVER access
    // the payment_db directly
    @Autowired
    private PaymentJdbcTemplate paymentDb;

    public void createOrder(Order order) {
        // This couples OrderService to PaymentService
        // at the database level
        paymentDb.update(
            "INSERT INTO payments ...", ...);
    }
}
```

**GOOD — Communication via API:**

```java
// OrderService calls PaymentService via HTTP client
@Service
public class OrderService {

    private final PaymentServiceClient paymentClient;

    public OrderResult createOrder(OrderRequest req) {
        // PaymentService owns its own DB
        PaymentResult payment =
            paymentClient.initiatePayment(
                req.getAmount(),
                req.getCustomerId()
            );
        if (payment.isApproved()) {
            orderRepository.save(
                new Order(req, payment.getId())
            );
        }
        return OrderResult.of(payment);
    }
}
```

**How to test / verify correctness:**

```bash
# Verify services are independently deployable:
# Deploy OrderService without deploying PaymentService
kubectl set image deployment/order-service \
  order-service=order-service:v2

# PaymentService continues running unchanged:
kubectl get pods -l app=payment-service
# Expected: payment-service pods unchanged
```

---

### ⚖️ Comparison Table

| Characteristic             | Monolith                    | Microservices               | Modular Monolith |
| -------------------------- | --------------------------- | --------------------------- | ---------------- |
| **Deployment unit**        | One artifact                | One per service             | One artifact     |
| **Deployment risk**        | High (all changes together) | Low (one service)           | Medium           |
| **Team scalability**       | Poor (>50 engineers)        | Good                        | Good             |
| **Operational complexity** | Low                         | High                        | Low              |
| **Network latency**        | None (in-process)           | Real overhead               | None             |
| **Data consistency**       | Easy (one DB)               | Hard (distributed)          | Easy             |
| **Technology freedom**     | None                        | Full per service            | Limited          |
| **Best for**               | Small teams, simple domains | Large orgs, complex domains | Medium teams     |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                            |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| "Microservices are always faster"                 | They add network latency. In-process monolith calls are ~1µs; network calls are ~1ms+.                             |
| "Smaller = better (one service per function)"     | Too fine-grained means excessive inter-service coordination. Service size should match team size.                  |
| "Shared database is fine"                         | A shared database couples services at the most fundamental level — schema changes in one service break others.     |
| "We can microservice our way out of a bad design" | Microservices amplify existing architectural problems. A poorly designed domain produces poorly designed services. |
| "Microservices remove all coupling"               | They only externalise coupling. Network coupling, API coupling, and data coupling still exist.                     |

---

### 🚨 Failure Modes & Diagnosis

**1. Distributed monolith**

**Symptom:** Services must always be deployed together; a change in one service requires a change in another.

**Root Cause:** Tight coupling — shared database, shared library with business logic, or synchronous dependencies on request/response chains that span all services.

**Diagnostic:**

```bash
# Check deployment frequency correlation
git log --oneline --all | grep -E "(payment|order|cart)" \
  | head -50
# If payment, order, and cart always appear in the
# same deployments, they are a distributed monolith
```

**Fix:**
BAD: Services sharing a single database schema.
GOOD: Each service owns its schema; cross-service data queries use APIs or events.

**Prevention:** Enforce database-per-service from day one. Review PRs for cross-service database access.

---

**2. Cascading failure**

**Symptom:** When one service goes down, several dependent services also go down or become slow.

**Root Cause:** No circuit breakers or timeouts between services. Slow responses block threads in callers.

**Diagnostic:**

```bash
# Check if a slow downstream is blocking threads
curl -w "%{time_total}" http://order-service/health
# If order-service is slow but payment-service is
# the actual problem, look for thread pool exhaustion
```

**Fix:**
BAD: Calling downstream services with no timeout.
GOOD: All downstream calls have explicit timeouts and circuit breakers (Resilience4j `@CircuitBreaker`).

**Prevention:** Every service-to-service call must have a configured timeout and circuit breaker.

---

**3. Data consistency problems**

**Symptom:** Data in two services is inconsistent — an order shows "paid" in OrderService but "pending" in PaymentService after a failure.

**Root Cause:** Using distributed transactions that can fail partway through, or not implementing sagas/outbox patterns for cross-service workflows.

**Diagnostic:**

```sql
-- Check for orders with no corresponding payment
SELECT o.id FROM orders o
LEFT JOIN payments p ON p.order_id = o.id
WHERE p.id IS NULL AND o.status = 'PAID';
-- Non-empty result = data inconsistency
```

**Fix:**
BAD: Two-phase commit across service databases.
GOOD: Outbox pattern + saga choreography for eventual consistency.

**Prevention:** Never use distributed transactions. Design cross-service workflows to be eventually consistent.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `MSV-002 - Monolith vs Microservices` — understand the trade-off before committing
- `DST-001 - Distributed Systems` — microservices are distributed systems
- `SAP-001 - Service-Oriented Architecture` — the precursor pattern

**Builds On This (learn these next):**

- `MSV-006 - Service Discovery` — how services find each other
- `MSV-010 - API Gateway` — entry point for external traffic
- `MSV-004 - The Microservices Ecosystem Map` — the full set of concerns

**Alternatives / Comparisons:**

- `MSV-002 - Monolith vs Microservices` — when NOT to use microservices
- `MSV-005 - When NOT to Use Microservices` — constraints and prerequisites

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS    │ Small, independently deployable  │
│               │ services per business capability │
├──────────────────────────────────────────────────┤
│ PROBLEM       │ Monolith deployment bottleneck   │
│               │ at organisational scale          │
├──────────────────────────────────────────────────┤
│ KEY INSIGHT   │ Primary benefit is organisational│
│               │ (team autonomy), not technical   │
├──────────────────────────────────────────────────┤
│ USE WHEN      │ Multiple teams, complex domain,  │
│               │ independent scaling needs        │
├──────────────────────────────────────────────────┤
│ AVOID WHEN    │ Small team (<5 engineers),       │
│               │ simple domain, early-stage       │
├──────────────────────────────────────────────────┤
│ TRADE-OFF     │ Team autonomy vs distributed     │
│               │ systems complexity               │
├──────────────────────────────────────────────────┤
│ ONE-LINER     │ "One team, one service,          │
│               │ one database"                    │
├──────────────────────────────────────────────────┤
│ NEXT EXPLORE  │ MSV-002, MSV-005, MSV-006        │
└──────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Each service owns its data — no shared databases.
2. The benefit is organisational (team autonomy), not just technical.
3. Microservices solve deployment bottlenecks at scale, not a general-purpose improvement.

**Interview one-liner:** "Microservices enable independent deployment by making all coupling explicit and network-mediated — the key constraint is one service per team and one database per service."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any system that allows implicit coupling (shared memory, shared database, shared code) will accumulate coupling until it becomes a single deployable unit. Making coupling explicit (network calls, versioned APIs) forces the cost of coupling to be visible and paid at design time rather than deployment time.

**Where else this pattern appears:**

- **Unix philosophy:** "Do one thing and do it well" — small, composable tools communicating via pipes is the microservices principle applied to system utilities.
- **Bounded contexts (DDD):** Each bounded context is a logical service boundary — the DDD version of the same principle (encapsulate one model, communicate at the boundary).
- **Cellular architecture:** Large-scale systems partitioned into independent cells, each processing a subset of data independently — the same isolation principle applied to scale, not just deployment.

---

### 💡 The Surprising Truth

Microservices don't reduce total complexity — they redistribute it. A well-designed monolith is technically simpler than an equivalent microservices architecture (no network calls, no distributed consistency, no service discovery). What microservices reduce is _organisational_ complexity at scale: the coordination cost of 200 engineers working on one codebase. The technical complexity increases; the organisational coordination complexity decreases. Teams that adopt microservices with fewer than 20 engineers typically discover they've traded a manageable monolith problem for an unmanageable distributed systems problem.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Two services share a PostgreSQL database — different schemas, same server. The teams claim they are "loosely coupled because it's separate schemas." Is this microservices? What specifically is the coupling risk?

_Hint:_ Think about what happens when one service runs a schema migration that locks the table or increases server-level resource usage. The "separate schema" claim doesn't eliminate database-level resource contention or the operational coupling of "both services must tolerate this schema migration window."

**Q2 (System Interaction):** OrderService makes synchronous HTTP calls to PaymentService (99.9% uptime), InventoryService (99.9% uptime), and NotificationService (99.9% uptime) for each order. What is the composite availability of OrderService if all three calls must succeed?

_Hint:_ Calculate 0.999 _ 0.999 _ 0.999. Then ask: which of these three calls truly must be synchronous, and which could be async (fire-and-forget) to decouple the availability of OrderService from each downstream?

**Q3 (Design Trade-off):** You are the first engineer at a 4-person startup with a monolith. The CTO wants microservices because "Netflix uses them." Design the argument for or against, and describe the exact conditions that should trigger a reconsideration.

_Hint:_ Think about what the startup currently lacks (operational tooling, dedicated platform team, enough engineers per service). Identify the specific trigger events (team growth milestones, deployment frequency hitting a wall, scaling requirements diverging across features) that shift the cost-benefit analysis from "not yet" to "now."
