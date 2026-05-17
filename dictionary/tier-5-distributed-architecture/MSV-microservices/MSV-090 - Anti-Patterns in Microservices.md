---
id: MSV-090
title: Anti-Patterns in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-003, MSV-010, MSV-020, MSV-030
used_by: MSV-001
related: MSV-001, MSV-003, MSV-010, MSV-020, MSV-025, MSV-030, MSV-080, MSV-085, MSV-088, MSV-089
tags:
  - microservices
  - antipattern
  - deep-dive
  - architecture
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 90
permalink: /microservices/anti-patterns-in-microservices/
---

# MSV-090 - Anti-Patterns in Microservices

⚡ TL;DR - Anti-Patterns in Microservices:
common architectural and organizational
mistakes that create systems MORE complex
than the monolith they replaced. Top 5:
(1) Distributed Monolith: microservices with
tightly coupled deployments and shared databases
(worst of both worlds); (2) Nano-services: too
fine-grained services (1-2 functions each)
with excessive network overhead; (3) Chatty
Services: services making dozens of synchronous
calls per request (latency amplification);
(4) Shared Database: multiple services reading/
writing the same tables (DB as integration layer);
(5) No Observability: microservices deployed
without distributed tracing, structured logging,
or metrics (invisible failures). Each anti-pattern:
has specific symptoms, root causes, and remediation
strategies. A senior engineer's core skill:
recognizing and preventing these before they
become production crises.

| #090 | Category: Microservices | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, Domain-Driven Design, API Gateway, Service Discovery, Database Per Service |
| **Used by:** | What are Microservices | |
| **Related:** | What are Microservices, Domain-Driven Design, API Gateway, Service Discovery, Circuit Breaker Pattern, Database Per Service, Conway's Law in Microservices, Monolith to Microservices Migration, Re-platforming vs Re-architecting, Proof of Concept in Architecture | |

---

### 🔥 The Problem This Solves

**MICROSERVICES ADOPTION WITHOUT THE BENEFITS:**
Org spent 18 months migrating from monolith
to 30 microservices. Results: deployment time
increased (more services to coordinate), incident
MTTR increased ("which service is the problem?"),
cost increased (30 services + 30 databases +
30 pipelines), and developer velocity decreased
("I need to understand 5 services to make one
change"). This is the common outcome of
microservices adoption without understanding
the anti-patterns that transfer monolith
problems into a distributed context.

---

### 📘 Textbook Definition

**Anti-Patterns in Microservices** are recurring
mistakes in microservices architecture that
result in systems that combine the complexity
of distributed systems with the coupling
problems of monoliths.

**The 10 Most Dangerous Anti-Patterns:**

**1. Distributed Monolith**
Services: multiple. Deployments: synchronized
("must deploy all 5 services together").
Databases: shared. Dependencies: tightly
coupled. Benefit of microservices: none.
Complexity: maximum. AKA: a monolith with
network hops.

**2. Nano-services (Over-decomposition)**
Services: too small (1 function per service;
sendEmail-service, validateAddress-service).
Problem: excessive orchestration overhead,
network latency for trivial operations,
deployment overhead per service, cognitive
overload for engineers.

**3. Chatty Services**
Service A: makes 20 synchronous calls to
other services to fulfill one request.
Latency: amplified (each hop adds 5-50ms;
20 hops = 100-1000ms added latency). Failure
probability: compounded (if each service
has 99.9% uptime, 20 in sequence = 98% uptime).

**4. Shared Database (Database Coupling)**
Multiple services: read/write the same database
tables. Schema change in Table X: breaks
3 services simultaneously. No team can
change their data model without coordinating
with other teams. Violates: Database Per
Service pattern.

**5. No Observability**
Microservices deployed without: distributed
tracing (which service caused the error?),
structured logging (searchable across services),
metrics (what is each service's error rate
and latency?). Incident response: distributed
blindness.

**6. Missing Circuit Breaker**
Service A: calls Service B synchronously.
No circuit breaker. Service B: slows down.
Service A: threads blocked waiting for B.
Service A: crashes (thread pool exhaustion).
Cascade: entire system unavailable. Bulkhead
and circuit breaker: the minimum for any
callee relationship.

**7. Too Many Microservices**
Team of 5 engineers owns 15 microservices.
Each engineer: responsible for 3 services.
Documentation: outdated. Oncall: chaotic.
Security patches: delayed. Cognitive load:
critical. The anti-pattern: decomposed
beyond team capacity.

**8. Service Sprawl without Governance**
New services: created freely without approval.
Service count: 100+ in 2 years. No decommission
process. "Ghost services" (no owner). Security
debt: accumulating. Service catalog: missing
or outdated. No one knows all the services.

**9. Synchronous Coupling for Long Operations**
Order placed -> payment processed -> inventory
updated -> email sent. All: synchronous REST
calls. Payment takes 2 seconds: order placement
takes 2+ seconds. Email delivery: blocks
order response. Long operations: should be
asynchronous (event-driven).

**10. Premature Microservices**
Team of 5 engineers: starts with 10
microservices from day 1 (no monolith phase).
Day 1: unclear domain boundaries. Services:
wrong boundaries (discovered in month 6
when all business logic crosses service
boundaries). Re-design: expensive. "Monolith
first" or "modular monolith first": lets
boundaries emerge before making them service
boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Top 5 microservices anti-patterns: Distributed
Monolith, Nano-services, Chatty Services,
Shared Database, No Observability. Each:
has specific symptoms and fixes.

**One analogy:**
> Microservices anti-patterns are like over-
> managing employees in a flat organization.
> The benefit of microservices (like the benefit
> of autonomous employees): independent decision-
> making (independent deployment). Distributed
> Monolith: hiring autonomous employees but
> requiring committee approval for every
> decision (no independence gained). Nano-services:
> hiring one employee per task ("send email"
> employee, "validate address" employee) -
> excessive overhead. Chatty Services: employee
> who asks 20 colleagues before making any
> decision (paralysis). Shared Database: all
> employees using one whiteboard (can't change
> your section without others seeing and being
> affected). No Observability: autonomous employees
> working in dark rooms (no visibility into
> what they're doing).

**One insight:**
The "Distributed Monolith" is the most dangerous
anti-pattern because it combines the worst
of both worlds: the operational complexity
of distributed systems (network failures,
latency, distributed tracing) WITH the tight
coupling of a monolith (coordinated deployments,
shared databases, inter-service implicit
dependencies). The monolith: at least fails
fast (one process). The Distributed Monolith:
fails slowly and invisibly (failures propagate
through the network). Recognizing a Distributed
Monolith: if ANY change requires coordinating
>= 2 service deployments > 30% of the time:
you have a Distributed Monolith.

---

### 🔩 First Principles Explanation

**ANTI-PATTERN 1: DISTRIBUTED MONOLITH - DIAGNOSIS**

```
Diagnostic questions:
  1. How often do you deploy more than 1 service
     at the same time? (% of deployments)
     > 30%: Distributed Monolith signal
     
  2. Do services share a database?
     Same DB server? Same schema? Yes: Distributed Monolith
     
  3. Can a service be upgraded independently
     without coordinating with other service owners?
     No: Distributed Monolith
     
  4. Do you have an explicit "release train"
     (all services deployed together on Thursdays)?
     Yes: Distributed Monolith

Root causes:
  Conway's Law violation: team structure doesn't
  align with service boundaries
  Shared DB: the most common root cause
    (teams couple to the DB schema)
  Wrong domain decomposition: boundaries
  don't follow natural domain boundaries

Fix:
  Address team structure (Inverse Conway)
  Extract service-specific data to service-specific DB
  Define API contracts between services
  CDC tests: verify no silent coupling
```

**ANTI-PATTERN 3: CHATTY SERVICES - LATENCY MATH**

```
CHATTY SERVICES LATENCY AMPLIFICATION:

Scenario: order-service creates an order
  Synchronous calls made:
    1. user-service: get user (5ms)
    2. address-service: validate address (8ms)
    3. inventory-service: check stock x3 items
       (15ms each = 45ms if sequential)
    4. pricing-service: get prices x3 items
       (10ms each = 30ms if sequential)
    5. tax-service: calculate tax (7ms)
    6. coupon-service: validate coupon (6ms)
    7. payment-service: charge payment (150ms)
    8. inventory-service: reserve stock x3 (15ms)
    9. notification-service: send confirmation (20ms)
    
  SEQUENTIAL execution:
    Total: 5+8+45+30+7+6+150+45+20 = 316ms
    (before any of order-service's own logic)
    
  PARALLEL where possible:
    User + address: in parallel (5ms + 8ms = 8ms)
    Inventory + pricing: in parallel
      (45ms + 30ms = 45ms; longest wins)
    Remaining sequential: still > 200ms
    
  BETTER: async where possible
    Payment: synchronous (must complete before confirming)
    Notification: async (fire and forget via Kafka)
    Inventory reservation: async after payment succeeds
    Result: total = 5+8+45+30+7+6+150 = 251ms
    But: notification + reservation: no longer blocking
    User-visible latency: ~250ms (acceptable)
    vs 316ms synchronous chain (too high)
```

---

### 🧪 Thought Experiment

**THE SHARED DATABASE FAILURE: LIVE SCHEMA CHANGE**

```
Scenario:
  order-service: needs to rename column
  'user_id' to 'customer_id' in orders table
  (business: "customers" not "users" in orders)
  
  Orders table: shared with:
    report-service (SELECT user_id FROM orders)
    analytics-service (JOIN on user_id)
    customer-service (UPDATE orders SET user_id...)
    
Effect of schema change:
  order-service: deploys with new column name
  report-service: FAILS (column user_id not found)
  analytics-service: FAILS
  customer-service: FAILS
  3 services: simultaneously broken
  Emergency: rollback order-service
  Root cause: shared DB as integration layer
  
Fix (requires weeks of work):
  Step 1: Add 'customer_id' column (additive)
  Step 2: Dual-write: old + new column
  Step 3: Update all consumers to use customer_id
  Step 4: Stop writing to user_id
  Step 5: Remove user_id (weeks later)
  
Lesson: Database Per Service avoids all this.
  Each service: owns its schema
  Renames: purely internal to the owning service
  Other services: never query your DB directly
```

---

### 🧠 Mental Model / Analogy

> Microservices anti-patterns are like traffic
> engineering mistakes. Distributed Monolith:
> new roads but same traffic light cycle
> ("all roads change together"). Nano-services:
> building a separate road for every car type
> (cars, bikes, trucks, scooters all have
> dedicated roads - excessive infrastructure).
> Chatty Services: every car: must stop at
> 20 toll booths before reaching the destination
> (each synchronous call = a toll booth).
> Shared Database: all roads merging into one
> intersection (bottleneck and cascading failure
> when the intersection fails). No Observability:
> traffic cameras that record but don't transmit
> to traffic control (incidents: invisible until
> gridlock).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Microservices anti-patterns: common mistakes
that make microservices MORE complex than the
monolith they replaced. The biggest: deploying
microservices but still requiring all of them
to deploy together (distributed monolith).

**Level 2 - Nano-services recognition (junior developer):**
Nano-service smell: if a service has < 3 API
endpoints, no database, and is only called
by one other service: it's probably too small.
Merge it with the caller. Rule of thumb:
one service should be cohesive enough to
have a meaningful API contract AND small
enough for one team to understand and own.

**Level 3 - Chatty services detection (mid-level):**
Chatty services metric: "fan-out factor" per
request. If one user-visible request causes
> 10 inter-service calls: chatty service smell.
Fix strategies: (1) aggregation pattern
(API Gateway aggregates multiple service
calls into one); (2) denormalization (store
data locally to avoid lookups); (3) async
(non-critical calls: move to async events);
(4) caching (cache repeated lookups).

**Level 4 - Service Mesh + Circuit Breaker for anti-patterns (senior):**
Service Mesh (Istio) + Resilience4j: essential
infrastructure to prevent cascading failures
(anti-pattern 6). Without circuit breaker:
chatty services amplify failures (one service
slows down -> all callers queue -> all callers
exhaust thread pools). Circuit breaker: isolates
the failure (open circuit = fast fail; callers:
not blocked). Service Mesh: adds observability
(which service is slow?) and retry logic.
These are not optional for production
microservices; they are the minimum viable
resilience layer.

**Level 5 - Anti-pattern detection at architecture review (principal):**
Senior engineers detect anti-patterns in
architecture reviews before they reach production.
Red flags in a service design proposal:
(1) "service calls service B before returning"
(chatty + coupling); (2) "we'll use the shared
user database" (shared DB); (3) "we need to
deploy both services together" (distributed
monolith); (4) "this service just wraps one
function" (nano-service); (5) "we'll add
monitoring later" (no observability). Each
red flag: has a standard remediation. The
goal: catch these in review, not in production.

---

### ⚙️ How It Works (Mechanism)

```
ANTI-PATTERN DETECTION CHECKLIST:

Distributed Monolith:
  [ ] % of deployments requiring > 1 service
      deployed simultaneously
      Threshold: > 30% = Distributed Monolith
  [ ] Do services share a database?
  [ ] Is there a weekly "release train"?

Nano-services:
  [ ] Any service with < 3 API endpoints
      AND no DB AND only 1 caller?
      -> Candidate for merging
  [ ] Per-function services?
      (send-email-service, validate-address-service)
      -> Nano-service anti-pattern

Chatty Services:
  [ ] Count: inter-service calls per user request
      > 10: chatty service smell
  [ ] Distributed traces: sequential call chain
      > 5 hops: review for parallelization
  [ ] p99 latency >> p50 latency?
      (network amplification pattern)

Shared Database:
  [ ] Can service B's schema change break
      service A without A's team knowing?
      Yes: shared DB
  [ ] Multiple services: same DB connection string?
      -> Shared DB

No Observability:
  [ ] Can you trace a user request across
      services via a single trace ID? No?
      -> Missing distributed tracing
  [ ] Are logs searchable across services? No?
      -> Missing centralized logging
  [ ] Error rate + latency per service: visible
      in one dashboard? No? -> Missing metrics
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
MICROSERVICES HEALTH SCORECARD:

SCORE 1 (Healthy): Independent deployments
  - Each service: deploys without other services
  - Deployment frequency: multiple times/week
  - Rollback: per service (5 minutes)
  - Database: per service (no sharing)

SCORE 2 (Chatty): Fix with async or caching
  - Identify: > 10 calls/request in traces
  - Fix: async events for non-critical calls
  - Cache: reference data lookups
  - Aggregate: API Gateway for client efficiency

SCORE 3 (Shared DB): Critical fix
  - Symptom: DB schema change requires
    coordinating multiple teams
  - Fix: Database Per Service migration
  - Timeline: 3-6 months per service

SCORE 4 (Distributed Monolith): Urgent
  - Symptoms: release trains, coordinated deploys
  - Fix: Inverse Conway Maneuver
          + Database Per Service
  - Timeline: 6-12 months

SCORE 5 (No Observability): Immediate
  - Any production microservice without
    distributed tracing = production blindness
  - Fix: Micrometer Tracing + ELK or Datadog
  - Timeline: 2-4 weeks per service
    (using Spring Boot auto-config)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Shared DB vs API contract**

```java
// BAD: order-service directly reads user table
// (shared database anti-pattern)

@Repository
public interface DirectUserRepository
        extends JpaRepository<User, Long> {
    // ORDER-SERVICE accesses USERS table directly
    // user-service: has no idea order-service
    // depends on this table structure
    // If user-service changes User schema:
    // order-service breaks silently
    // No API contract; no versioning
    // Schema change: breaks 3 services simultaneously
    Optional<User> findByIdAndActiveTrue(
        Long userId);
}

@Service
public class OrderService {
    // Reaches into users table directly
    // This is the worst coupling: DB-level
    private final DirectUserRepository userRepo;
    
    public Order createOrder(CreateOrderRequest req) {
        User user = userRepo
            .findByIdAndActiveTrue(req.getUserId())
            .orElseThrow();
        // Tightly coupled to User schema
        // If user-service adds soft-delete and
        // removes 'active' column: this breaks
        return new Order(user.getId(), ...);
    }
}
```

```java
// GOOD: order-service calls user-service via API
// (Database Per Service; API contract)

@FeignClient(name = "user-service")
public interface UserClient {
    // API contract: only what order-service needs
    // NOT the full User entity
    // user-service: can change User schema
    // internally (name -> firstName + lastName)
    // API: stable (still returns CustomerSummary)
    @GetMapping("/api/v1/customers/{id}")
    CustomerSummary getCustomer(
        @PathVariable Long id);
}

// CustomerSummary: minimal DTO for order context
public record CustomerSummary(
    Long id,
    String displayName,
    String email,
    boolean active  // computed by user-service
) {}

@Service
public class OrderService {
    private final UserClient userClient;
    
    @CircuitBreaker(name = "user-service")
    public Order createOrder(CreateOrderRequest req) {
        // Calls API: not DB
        // Circuit breaker: if user-service slow,
        // doesn't block order-service threads
        CustomerSummary customer = userClient
            .getCustomer(req.getCustomerId());
        if (!customer.active()) {
            throw new InactiveCustomerException();
        }
        return new Order(customer.id(), ...);
    }
}
// user-service: can refactor User schema
// CustomerSummary API: stable (semantic versioning)
// order-service: never breaks on user-service
// internal changes
```

---

### ⚖️ Comparison Table

| Anti-Pattern | Symptom | Root Cause | Fix |
|---|---|---|---|
| **Distributed Monolith** | Coordinated deployments, release train | Wrong team boundaries, shared DB | Inverse Conway + DB per service |
| **Nano-services** | 1-2 function services, excessive network | Over-decomposition, premature extraction | Merge with related service |
| **Chatty Services** | > 10 inter-service calls/request, high p99 | Synchronous coupling, wrong decomposition | Async events, caching, aggregation |
| **Shared Database** | Schema change breaks multiple services | DB as integration layer | Database Per Service + API contract |
| **No Observability** | Unknown incident cause, slow MTTR | Treated as optional, not day-1 concern | Distributed tracing + metrics from day 1 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Microservices always deliver better scalability and velocity than monoliths | Microservices deliver better scalability and velocity ONLY when implemented correctly (proper domain decomposition, team alignment, observability, circuit breakers, database per service). Poorly implemented microservices (distributed monolith, shared databases, no observability) deliver WORSE scalability and velocity than a well-structured monolith. The choice is not monolith vs microservices; it's well-structured architecture vs poorly-structured architecture. |
| Adding more services makes the system more resilient | More services = more failure points (if service count doubles, probability of at least one service failing = higher). Microservices deliver resilience through: (1) circuit breakers (failures don't cascade), (2) bulkheads (failures don't exhaust shared resources), (3) independent failure domains (payment fails; catalog still works). Without these patterns: more services = lower overall system availability. |
| The Distributed Monolith problem is solvable by adding more microservices | Distributed Monolith is a COUPLING problem, not a granularity problem. Adding more services to a Distributed Monolith: adds more coupling points and more network complexity, making it worse. The fix: address the coupling (wrong domain boundaries, shared database). This requires FEWER, better-bounded services, not MORE services. |

---

### 🚨 Failure Modes & Diagnosis

**Cascading failure from missing circuit breaker (anti-pattern 6)**

**Symptom:**
Monday morning: inventory-service is slow
(DB query optimization deployed; caused 10-second
query times). Within 3 minutes: order-service
is also completely down. Within 5 minutes:
the entire system is unresponsive. 100% of
customer-facing requests: fail. But the
original issue: only inventory-service.

**Root Cause:**
order-service: makes synchronous calls to
inventory-service (no circuit breaker). When
inventory-service slows to 10 seconds: order-
service threads block waiting for inventory
response. Thread pool: exhausted in 3 minutes
(200 threads; 10s calls; backlog fills). New
order requests: rejected (no free threads).
Upstream services: cascade. One slow service
= entire system down.

**Diagnosis:**
```
Distributed trace analysis:
  All failed requests: show thread-wait
  span on inventory-service call
  Span duration: 10s (inventory timeout)
  Thread pool metric:
    order-service: http-thread-pool-active = 200
    (pool size = 200; all threads: waiting)
  Root cause: inventory-service slow query
  Amplifier: no circuit breaker on inventory calls
  
  Timeline:
    10:02: inventory-service slow query deployed
    10:03: order-service thread pool fills
    10:05: order-service unresponsive
    10:07: payment-service (calls order-service)
           also unresponsive
    10:09: entire checkout flow: down
```

**Fix:**
```java
// Short term: add circuit breaker IMMEDIATELY
@CircuitBreaker(
    name = "inventoryService",
    fallbackMethod = "getInventoryFallback")
@Bulkhead(
    name = "inventoryService",
    // Max 10 concurrent calls; rest: fast-fail
    type = Bulkhead.Type.SEMAPHORE)
@Retry(name = "inventoryService")
public InventoryStatus checkInventory(
        String sku) {
    return inventoryClient.check(sku);
}

private InventoryStatus getInventoryFallback(
        String sku, Exception e) {
    // Fallback: assume in-stock (or show
    // "limited availability" message)
    // Order: placed; inventory verified async
    return InventoryStatus.assumeAvailable(sku);
}

// Long term: set thread pool TIMEOUT
// If inventory doesn't respond in 500ms:
// fast-fail (don't wait 10 seconds)
// resilience4j:
//   circuitbreaker.inventoryService
//     .timeout.duration: 500ms
```

---

### 🔗 Related Keywords

**Anti-pattern context:**
- `What are Microservices` - understanding
  the goals clarifies what the anti-patterns
  violate
- `Conway's Law in Microservices` - Distributed
  Monolith root cause: wrong team structure
- `Monolith to Microservices Migration` -
  migration without care creates anti-patterns

**Technical solutions:**
- `Circuit Breaker Pattern` - prevents cascading
  failure (anti-pattern 6)
- `Database Per Service` - prevents shared
  database (anti-pattern 4)

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| TOP 5 ANTI-PATTERNS:                            |
| 1 Distributed Monolith -> Inverse Conway        |
| 2 Nano-services -> merge; right-size            |
| 3 Chatty Services -> async; cache; aggregate    |
| 4 Shared DB -> API contract; DB per service     |
| 5 No Observability -> tracing from day 1        |
+--------------+----------------------------------+
| SIGNAL (1)   | > 30% coordinated deploys       |
| SIGNAL (3)   | > 10 inter-service calls/req    |
| SIGNAL (4)   | schema change breaks > 1 service|
| SIGNAL (5)   | "which service failed?" unknown  |
+--------------+----------------------------------+
| ONE-LINER    | "Microservices anti-patterns    |
|              |  create distributed monoliths.  |
|              |  Measure. Detect early. Fix."   |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Distributed Monolith = microservices with
   all the coupling of a monolith. Signal: > 30%
   of deployments coordinate multiple services.
   Fix: Inverse Conway Maneuver + Database Per
   Service.
2. Circuit Breaker: mandatory for ALL synchronous
   inter-service calls. Without it: one slow
   service cascades to entire system down.
   Resilience4j: `@CircuitBreaker` + `@Bulkhead`.
3. Observability: day-1 requirement, not
   afterthought. Distributed tracing (trace ID
   across services) + structured logging +
   metrics per service = the minimum to operate
   microservices in production.

**Interview one-liner:**
"Anti-Patterns in Microservices: common architectural
mistakes. Top 5: (1) Distributed Monolith - services
are tightly coupled (shared DB, coordinated deploys)
= microservices complexity without independence
benefit; (2) Nano-services - too fine-grained (1-2
functions per service); (3) Chatty Services - > 10
synchronous inter-service calls per request = latency
amplification + cascading failures; (4) Shared Database
- multiple services own the same tables = schema
coupling; (5) No Observability - missing distributed
tracing, structured logging, metrics = production
blindness. Detection: deployment coordination rate,
inter-service call count per request, distributed
tracing coverage. Each has specific remediations."

---

### 💡 The Surprising Truth

The most dangerous microservices anti-pattern
isn't the Distributed Monolith or shared
databases - it's organizational overconfidence.
Teams that read the microservices success
stories (Netflix, Amazon) assume the patterns
will work the same way for a 20-person team
as for a 10,000-engineer organization. Netflix
has: thousands of engineers, years of tooling
development, Hystrix (circuit breaker library
they wrote), Atlas (metrics system they
built), and a culture of experimentation.
Your team: has Spring Boot, Kubernetes, and
6 months to deliver. The anti-patterns occur
when teams adopt microservices for the prestige
("we use microservices like Netflix!") without
the prerequisites (observability, circuit
breakers, team alignment). The honest question
before any microservices decision: "Do we
have the operational maturity to run distributed
systems? Or will we create a distributed
monolith?" The organizations that ask this
question before adopting microservices: avoid
most of the anti-patterns.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DETECT** Given a microservices architecture
   diagram and deployment history (which services
   deploy together): identify which of the 10
   anti-patterns are present. For each: cite
   specific evidence from the diagram/data.
2. **DISTRIBUTED MONOLITH FIX** For a system
   with 8 services sharing 2 databases and 60%
   coordinated deployments: design the 12-month
   remediation plan. What is the order of
   database extraction? What team restructuring
   is needed? What success metric confirms
   the anti-pattern is resolved?
3. **CIRCUIT BREAKER** For a chatty service
   making 15 synchronous calls: identify which
   calls should be async (event-driven), which
   should be cached, and which require circuit
   breakers. Implement the most critical circuit
   breaker with Resilience4j.
4. **OBSERVABILITY MINIMUM** Define the minimum
   observability stack for a 10-service
   microservices system: what tracing,
   logging, and metrics tools? What specific
   dashboards and alerts are required to
   detect the most common anti-patterns?
5. **ARCHITECTURE REVIEW** Design the architecture
   review process for new microservice proposals:
   what anti-pattern red flags do you check
   for? What questions do you ask the proposing
   team? What are your gate criteria (approve
   vs require rework)?

---

### 🧠 Think About This Before We Continue

**Q1.** Your organization has 40 microservices.
A new architecture review reveals: 12 services
share a single "transactions" database. 8 services
always deploy together (the "core services"
release train). 15 services have no distributed
tracing. You have 3 engineering teams and 12
months. Prioritize: which anti-patterns do
you address first? In what order? What's your
criteria for prioritization (business risk,
engineering effort, cascading dependencies)?

**Q2.** Your company is growing: 5 engineers
today, 50 engineers in 18 months (due to
funding). You're starting with a monolith.
Knowing the microservices anti-patterns: design
the architecture strategy for the growth phase.
At what point does decomposition to microservices
become necessary? How do you build the monolith
to minimize future anti-patterns (modular
monolith first)? What organizational structure
changes (Conway's Law) must happen before
service extraction?

**Q3.** A senior engineer joins your team.
In their first week: they find that two
microservices are sharing a database table
(legacy: "it was easier at the time"). The
engineers who built this are no longer at
the company. The services: have been in
production for 3 years; stable; no incidents.
"If it ain't broke, don't fix it." What
is your recommendation: fix the anti-pattern
or leave it? What specific risks justify
the cost of fixing it? What risks of fixing
it must be planned for?