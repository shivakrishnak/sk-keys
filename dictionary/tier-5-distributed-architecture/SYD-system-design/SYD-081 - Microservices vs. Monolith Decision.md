---
id: SYD-081
title: "Microservices vs. Monolith Decision"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-001, SYD-002
used_by: ""
related: SYD-001, SYD-002, SYD-080, SYD-004, SYD-016
tags:
  - architecture
  - microservices
  - monolith
  - decision
  - trade-offs
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 81
permalink: /syd/microservices-vs-monolith-decision/
---

# SYD-081 - Microservices vs. Monolith Decision

⚡ TL;DR - Microservices vs. monolith is a trade-off
decision, not a technical superiority question.
Monolith wins on: simplicity, ease of development,
consistency, operational overhead. Microservices wins
on: independent deployability, independent scalability,
team autonomy, polyglot tech stack. The common mistake:
starting with microservices before the domain is
understood. Martin Fowler's rule: "Start with a monolith,
extract to microservices when you have clear service
boundaries and a scaling reason." Most systems < 50
engineers and < 10M DAU have no technical reason to
prefer microservices over a well-architected monolith.
Microservices solve organizational scaling problems
more than they solve technical scaling problems.

| #081 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | System Design Process, Scalability Fundamentals | |
| **Related:** | System Design Process, Scalability Fundamentals, Technology Selection Framework, High Availability Design, API Gateway Pattern | |

---

### 🔥 The Problem This Solves

Startup with 10 engineers ships a monolith. It works
well. The team hits product-market fit, grows to 50
engineers, and wants to move to microservices "to scale."
They split the monolith into 20 services. Now: inter-
service network calls where functions were called before.
Distributed transactions where database transactions
were. Separate deployments for each service. Kubernetes
for orchestration. A dedicated platform team. Six months
to get back to the feature velocity they had with the
monolith. Was the migration worth it? Sometimes yes.
Often no. The decision framework clarifies when.

---

### 📘 Textbook Definition

**Monolith:** A single deployable unit containing all
application functionality. All modules share the same
process, memory space, and database. A call from the
order module to the user module is a function call.
"Modular monolith" = well-structured monolith with
clear module boundaries but still deployed as one unit.

**Microservices:** An architectural style where the
application is structured as a collection of small,
independently deployable services. Each service runs
in its own process and communicates over a network
(HTTP/REST or message queues). Each service owns its
data (separate database per service).

**Service boundary:** The line that separates two
services. Good service boundaries align with business
domains (Bounded Contexts in Domain-Driven Design).
Poor service boundaries lead to chatty services
(many inter-service calls for a single business
operation) and distributed transactions.

**Bounded Context:** A Domain-Driven Design concept.
A bounded context is a region of the domain model
with a clear, consistent language and set of rules.
Good microservice candidates: each bounded context
could be a service. Orders, Payments, Inventory,
Users - each has its own language and rules.

**Distributed monolith:** The worst of both worlds:
many services that are tightly coupled - they must
be deployed together and share a database. Has the
operational overhead of microservices without the
independence benefits.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Monolith: simple, consistent, one deployment. Right for
most teams. Microservices: independent deployability and
scale per service. Right when you have clear service
boundaries and a reason to scale services independently.

**One analogy:**
> A restaurant (monolith) vs. a food court (microservices):
>
> Restaurant (monolith): one menu, one kitchen, one
> dining room. Coordination is easy: the chef, waiters,
> and cashier all share the same space. Communication
> is a shout across the room. Everything is consistent:
> same health inspection, same payment system, same
> opening hours.
>
> Food court (microservices): separate stalls, each
> independently owned and operated. A sushi stall can
> stay open later than the pizza stall. One stall can
> be renovated without closing the others. But:
> you need a common payment system (API gateway),
> shared seating is a coordination problem, and a
> customer wanting sushi AND pizza has to visit two
> stalls (distributed transaction).
>
> Right choice: one restaurant until you need different
> operating hours for different food types. Then: food court.

**One insight:**
The key insight, from Sam Newman (author of "Building
Microservices"): microservices are an optimization for
organizational scale, not primarily for technical scale.
A monolith can be vertically scaled (bigger server) and
read-scaled (read replicas) to handle significant traffic.
The moment microservices become clearly superior is when
you have 10+ teams deploying code to the same codebase:
they block each other, merge conflicts are constant,
deployment coordination is expensive. Microservices let
each team own, deploy, and scale their service independently.
The technical benefits (polyglot, per-service scaling)
are real but secondary.

---

### 🔩 First Principles Explanation

**WHEN MONOLITH IS BETTER:**
```
1. Early stage / unknown domain
   Domain model not yet understood.
   Service boundaries require domain expertise to draw.
   Wrong boundaries → distributed monolith: tightly
   coupled services that must deploy together.
   
   Symptom of wrong boundary: changing feature X
   requires deploying services A, B, C in sequence.
   This is not microservices. It's a worse monolith.
   
   Rule: Do not split until you understand the domain
   well enough to draw good service boundaries.
   Bad boundaries are worse than a monolith.

2. Small team (< 10 engineers)
   Microservices require a platform team to maintain
   Kubernetes, service mesh, CI/CD pipelines per service,
   distributed tracing, centralized logging.
   
   For a 5-person startup: this overhead consumes 1-2
   engineers' time that would otherwise ship features.
   
   A monolith with good internal structure (clear modules,
   dependency injection, clean interfaces) can be split
   later when the team and domain are ready.

3. Consistency-critical operations
   Monolith: update order, deduct inventory, charge
   payment = single database transaction. Atomic. Simple.
   
   Microservices: each service has its own DB.
   Update order → send message → deduct inventory →
   send message → charge payment.
   Any step can fail. Requires saga pattern or 2PC.
   Both are significantly more complex than a transaction.
   
   If the core operation requires consistency across
   multiple data entities: monolith simplifies this.
   Extract payment as a separate service only if payment
   logic is complex enough to warrant it, not just because
   it "should be a microservice."

4. Latency-sensitive internal calls
   Monolith: module A calls module B → function call
   (nanoseconds).
   Microservices: service A calls service B → network
   call (milliseconds, serialization overhead).
   
   For a request that chains 5 internal calls:
   Monolith: ~1ms total.
   Microservices: 5 × 5ms = 25ms minimum (network only).
   At p99, with retry on timeout: potentially 200ms+.
   
   If the critical path requires many internal calls,
   microservices add measurable latency to user requests.
```

**WHEN MICROSERVICES ARE BETTER:**
```
1. Organizational scale (10+ teams)
   Multiple teams deploying to the same codebase:
   - Merge conflicts: teams step on each other.
   - Deploy coordination: "who is deploying when?"
   - Blast radius: one team's bad deploy breaks all teams.
   
   Microservices: each team owns one or more services.
   Deploys independently. Owns the deployment pipeline.
   A bad deploy affects only that service.
   
   This is the primary use case for microservices.
   Organizations before this scale: lower ROI on micro.

2. Independent scaling requirements
   User service: 100 QPS (most users logged in once).
   Recommendation service: 10,000 QPS (every page load).
   Search service: 1,000 QPS.
   
   Monolith: scale the entire application to meet
   the recommendation service's 10K QPS requirement.
   100x over-provisioned for the user service.
   
   Microservices: scale recommendation service to 20
   instances. User service: 1 instance. Search: 5.
   Cost savings: significant. Right-sized per service.

3. Different technology requirements per service
   ML model serving: Python (scikit-learn, PyTorch).
   Core API: Java (mature ecosystem, team expertise).
   Real-time messaging: Go (goroutines, low memory).
   
   Monolith: one language. Cannot use Python for ML
   and Java for everything else in the same process.
   
   Microservices: polyglot. Each service uses the right
   tool for its workload.

4. Different reliability requirements
   User authentication: 99.99% availability (affects all users).
   Recommendation engine: 99.9% acceptable (degrade gracefully).
   Admin panel: 99.5% acceptable (low traffic, internal).
   
   Monolith: one availability target for everything.
   Must meet the highest requirement for all components.
   
   Microservices: right-size availability per service.
   Recommendation failure → show popular items (fallback).
   Does not affect auth service uptime.

5. Compliance isolation
   Payment Card Industry (PCI DSS): payment data must
   be isolated in a separate environment with specific
   security controls.
   
   Monolith: entire application must be PCI compliant
   (expensive: audit covers all code, all servers).
   
   Microservices: isolate payment service in a PCI
   compliant environment. All other services are out
   of PCI scope. Audit covers only the payment service.
   This alone often justifies extracting a payment service.
```

**DECISION FRAMEWORK:**
```
SHOULD YOU MIGRATE FROM MONOLITH TO MICROSERVICES?

Ask these questions:

Q1: Is deployment speed blocked by team size?
  Less than 10 engineers → NO (monolith is fine).
  10-50 engineers → MAYBE (depends on domain complexity).
  50+ engineers → YES (microservices likely beneficial).

Q2: Do you have clear, stable service boundaries?
  Domain not fully understood → NO (wait, risk distributed monolith).
  Boundaries clear, DDD bounded contexts identified → YES.

Q3: Do you have different scaling requirements per service?
  All services scale proportionally → NO (monolith can scale).
  Critical difference (100x) in QPS per component → YES.

Q4: Do you have compliance or security isolation requirements?
  Yes (PCI, HIPAA) → YES for the regulated component.

Q5: Do you have a platform team to support microservices?
  No → DO NOT migrate yet (ops overhead will kill velocity).
  Yes → Proceed if other conditions met.

ANSWER PATTERN:
  All NO → Stay with monolith. Optimize it internally.
  Q1 YES + Q2 YES → Extract carefully with DDD.
  Q3 YES for specific service → Extract that service only.
  Q4 YES → Extract compliance-sensitive service.

The goal is not "migrate everything."
The goal is "extract services where there is a clear reason."
A hybrid (monolith + a few extracted services) is often
the right architecture for a 50-100 person engineering org.
```

---

### 🧪 Thought Experiment

**The E-Commerce Migration**

Year 1: 5 engineers, Django monolith.
Modules: Users, Products, Orders, Payments, Inventory.
All in one codebase. Single PostgreSQL. Works perfectly.
200K users. 10K orders/day.

Year 3: 40 engineers, 5 feature teams.
Monolith problems emerging:
- Team A's deploy breaks Team B's feature (shared code).
- Large deploy window (60 min) → coordination overhead.
- Inventory team wants to use Go for concurrent stock
  updates; monolith is Python only.
- Payment must be PCI-isolated.

Right migration strategy:
  Step 1: Extract Payment service first. Isolated.
          PCI compliant. Team is 3 engineers.
  Step 2: Extract Inventory service. Go language.
          Independent scaling (flash sales).
  Step 3: Extract User service. Stable interface.
          Little domain change expected.
  Remaining: Orders + Products = still in monolith.
  These are tightly coupled. Extract together only
  if there is a specific team ownership reason.

Wrong migration strategy:
  "Let's convert everything to 50 microservices at once."
  Result: 6 months of engineering time, no new features.
  Distributed monolith created (services tightly coupled).
  Rollback to monolith. Start over.

Lesson: extract incrementally, only with clear reasons.
Not all at once. Not because microservices are "better."

---

### 🧠 Mental Model / Analogy

> Monolith vs. microservices is like a general
> contractor (GC) vs. a specialist subcontractor model:
>
> General contractor (monolith): one entity manages
> all construction. Plumbing, electrical, framing:
> all coordinated by one team. Communication is easy.
> Accountability is clear. For a house: perfect.
>
> Subcontractors (microservices): separate plumbing
> company, electrical company, framing company.
> Each specializes. Each works independently.
> Needed for a skyscraper: no single company has the
> capacity or expertise to do everything.
> But: coordination overhead is high (project manager,
> scheduling, interfaces between trades).
>
> Right choice: GC for a house (monolith for a small
> product). Subcontractors for a skyscraper (microservices
> for a large, complex, multi-team product).
> Hiring 20 subcontractors to build a house is
> expensive and slow.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A monolith is one application. A microservices architecture
is many small applications. The monolith is simpler to
build and operate. Microservices allow teams to work
independently and scale individual pieces. Most small
companies start with a monolith and extract services
as they grow.

**Level 2 - How to use it (junior developer):**
Start with a monolith. Structure it well: clear modules,
no circular dependencies, clean interfaces between modules.
When a module needs to scale independently, when a team
needs to own it independently, or when compliance requires
isolation: extract it as a service. Do not extract everything
at once. Partial migration (monolith + a few services)
is a valid long-term architecture.

**Level 3 - How it works (mid-level engineer):**
Monolith: function calls between modules. Shared
database. Single deployment. Benefits: consistency
(ACID transactions across modules), no network overhead,
simple operations. Costs: any change requires re-deploying
the entire application; one team's slow deploy blocks
others; cannot scale individual features independently.
Microservices: network calls between services. Separate
database per service. Independent deployments. Benefits:
team autonomy, independent scaling, polyglot, fault
isolation. Costs: distributed transactions (saga, 2PC),
network latency, operational complexity (Kubernetes,
service mesh, distributed tracing).

**Level 4 - Why it was designed this way (senior/staff):**
The microservices movement (2012-2015) emerged at companies
like Amazon and Netflix that had hit the organizational
scale limits of monoliths. Amazon's "two-pizza team"
rule (a team should be small enough to be fed by two
pizzas) naturally mapped to microservices: small teams
own small services. At Amazon's scale (100K+ engineers),
the coordination cost of a single codebase is catastrophic.
Microservices reduce coordination: each team's interface
to other teams is the service API, not shared code.
The mistake many companies made: copy the Netflix/Amazon
architecture without having Netflix/Amazon's organizational
scale. For a 20-person startup, the operational overhead
of microservices is not justified by the organizational
benefits.

**Level 5 - Mastery (distinguished engineer):**
The most sophisticated view of this decision: the
monolith vs. microservices question is often a proxy
for the underlying modularity question. A codebase
with good internal modularity (clear boundaries,
dependency injection, clean interfaces) can be extracted
to microservices with relatively low friction when the
organizational or technical need arises. A codebase
with poor modularity (circular dependencies, shared
state everywhere, no separation of concerns) cannot be
cleanly extracted regardless of how much effort is
invested. The prerequisite for microservices is a
well-structured monolith. Building microservices from
a poorly structured monolith produces a poorly structured
distributed system - a distributed monolith - which is
strictly worse than the original. Distinguished engineers
invest in modularity before considering whether to
distribute.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ MONOLITH ARCHITECTURE                              │
│                                                      │
│ [Single Process: API + Business Logic]             │
│   Users Module                                    │
│   Orders Module  → [Shared DB: all tables]        │
│   Payment Module                                  │
│   Inventory Module                               │
│                                                      │
│ Benefits:                                          │
│   - Function calls (nanoseconds)                 │
│   - ACID transactions across modules             │
│   - One deployment, one pipeline                 │
│   - Simple distributed tracing (not needed)      │
│                                                      │
│ MICROSERVICES ARCHITECTURE                         │
│                                                      │
│ [Users Service] ←→ [API Gateway] ←→ [Client]     │
│      |DB1                                          │
│                                                      │
│ [Orders Service] ←→ [Message Bus (Kafka)]         │
│      |DB2                                          │
│                                                      │
│ [Payment Service] → [External Payment API]        │
│      |DB3  (PCI isolated)                         │
│                                                      │
│ [Inventory Service] ← [Orders Service events]    │
│      |DB4  (Go service, high write QPS)          │
│                                                      │
│ Benefits:                                          │
│   - Independent deploys (Teams A,B,C deploy alone)│
│   - Independent scaling (Inventory: 20 replicas) │
│   - Polyglot (Payment: Python, Inventory: Go)    │
│   - Fault isolation (Search down ≠ Orders down)  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Modular monolith (right way to start)**
```python
# GOOD: modular monolith structure
# Clear module boundaries. Easy to extract later.

# users/service.py
class UserService:
    """
    Users bounded context.
    All user-related business logic lives here.
    Other modules call through this interface only.
    No other module accesses UserRepository directly.
    """
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository
    
    def get_user(self, user_id: int) -> User:
        return self._repo.get_by_id(user_id)
    
    def create_user(self, email: str,
                    name: str) -> User:
        if self._repo.exists_by_email(email):
            raise DuplicateEmailError(email)
        return self._repo.create(email=email, name=name)

# orders/service.py
class OrderService:
    """
    Orders bounded context.
    Depends on UserService and InventoryService interfaces.
    Does NOT directly query the users or inventory table.
    """
    def __init__(self,
                 order_repository: OrderRepository,
                 user_service: UserService,
                 inventory_service: InventoryService,
                 payment_service: PaymentService):
        self._repo = order_repository
        self._users = user_service
        self._inventory = inventory_service
        self._payment = payment_service
    
    def place_order(self, user_id: int,
                    items: list[OrderItem]) -> Order:
        # Validate user exists
        user = self._users.get_user(user_id)
        
        # Reserve inventory
        reservation = self._inventory.reserve(items)
        
        # Process payment (within same DB transaction)
        with self._repo.transaction():
            order = self._repo.create(
                user_id=user_id, items=items)
            self._payment.charge(
                user_id=user_id,
                amount=order.total,
                order_id=order.id)
        
        return order

# When to extract to microservices:
# 1. UserService is called by 5 other teams' code?
#    Extract to a service when there is a team ownership
#    reason. Until then: the interface is the boundary.
# 2. InventoryService needs to be Go?
#    Extract when the language boundary is reached.
# 3. PaymentService needs PCI isolation?
#    Extract immediately.
#
# The module interfaces above are the future service
# interfaces. Extracting is a matter of replacing
# Python function calls with HTTP calls to the same
# interface. Low friction if done right.
```

**Example 2 - Distributed transaction cost (anti-pattern)**
```python
# WHY transactions are hard in microservices

# MONOLITH: place_order is one ACID transaction.
# All or nothing: if payment fails, order is rolled back.
# Inventory is not reserved. Clean.

def place_order_monolith(user_id, items):
    with db.transaction():
        order = create_order(user_id, items)
        reserve_inventory(items)      # same DB
        charge_payment(user_id, order.total)  # same DB
        return order
    # If any step raises: entire transaction rolled back.

# MICROSERVICES: saga pattern required.
# Compensating transactions for rollback.
# Much more complex.

class PlaceOrderSaga:
    """
    Saga for placing an order across 3 services.
    Each step has a compensating transaction.
    """
    
    async def execute(self, user_id: int,
                      items: list) -> Order:
        order = None
        inventory_reserved = False
        payment_charged = False
        
        try:
            # Step 1: Create order
            order = await order_service.create(
                user_id, items)
            
            # Step 2: Reserve inventory
            reservation = await inventory_service.reserve(
                items)
            inventory_reserved = True
            
            # Step 3: Charge payment
            charge = await payment_service.charge(
                user_id, order.total, order.id)
            payment_charged = True
            
            # Step 4: Confirm order
            await order_service.confirm(order.id)
            return order
            
        except PaymentFailedError:
            # Compensate: release inventory
            if inventory_reserved:
                await inventory_service.release(
                    reservation.id)
            # Compensate: cancel order
            if order:
                await order_service.cancel(order.id)
            raise
        
        except Exception as e:
            # Compensate all applied steps
            if payment_charged:
                await payment_service.refund(charge.id)
            if inventory_reserved:
                await inventory_service.release(
                    reservation.id)
            if order:
                await order_service.cancel(order.id)
            raise

# The saga is correct but:
# 1. 3× more code than the monolith version.
# 2. Each step is a network call (failure possible).
# 3. Compensating transactions can fail too.
# 4. Requires idempotency in all services.
# 5. Requires a saga orchestrator or choreography logic.
# This complexity is WORTH IT when services have genuine
# independence reasons. It is NOT worth it if the only
# reason was "microservices are trendy."
```

---

### ⚖️ Comparison Table

| Dimension | Monolith | Microservices |
|---|---|---|
| **Development speed** | Fast (early stage) | Slower (overhead) |
| **Operational complexity** | Low (one service) | High (K8s, mesh, tracing) |
| **Transactions** | ACID (simple) | Saga / 2PC (complex) |
| **Scaling** | Scale entire app | Scale per service |
| **Team independence** | Low (shared codebase) | High (owns service) |
| **Deployment** | One pipeline | One per service |
| **Debugging** | Simple (one process) | Hard (distributed traces) |
| **Right for** | < 50 engineers, early stage | 50+ engineers, stable domain |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Microservices are more scalable than monoliths | A well-designed monolith can handle millions of users. Stack Overflow runs on a monolith (as of 2024) and handles billions of pageviews per month on a handful of servers. Shopify ran a Rails monolith for years. GitHub's core is still a monolith. The claim "microservices are more scalable" conflates scalability (handling more load) with the organizational benefits of microservices (team independence). A monolith can be scaled vertically and with read replicas to handle enormous traffic. Microservices solve organizational scaling more than technical scaling. |
| Each microservice should have its own database | Database per service is a principle of microservices, not a rule. For small teams with 5-10 services, sharing a database with strong module-level access control (each service only reads/writes its own tables) is simpler and avoids distributed transaction complexity. Extract to separate databases only when services have genuinely different scaling requirements for their data stores, or when isolation is required for security/compliance. Don't separate databases prematurely and then fight distributed transaction problems unnecessarily. |
| Migrating to microservices means migrating everything | A hybrid architecture - monolith with a few extracted services - is often the right long-term architecture for mid-size organizations. Extract services when there is a clear reason (compliance, independent scaling, team ownership, different language). Leave the rest in the monolith. Amazon started with a monolith and extracted services incrementally over years. The goal is not a fully microservices architecture: the goal is the right architecture for each component. |

---

### 🚨 Failure Modes & Diagnosis

**Distributed Monolith: Microservices Without Independence**

**Symptom:**
"We migrated to microservices six months ago. Now:
deploying service A requires deploying B and C first.
Any change to the Order schema breaks the Inventory
service and the Notification service. We have more
incidents than before and half the deployment velocity."

**Root Cause:**
Services are tightly coupled: they share a database,
or they make synchronous calls to each other in a
chain, or they depend on shared library versions that
must be updated in sync. This is a distributed monolith:
the operational complexity of microservices without the
independence benefit.

**Diagnosis:**
```
Smell 1: Deploying one service requires deploying others.
  Cause: synchronous dependency chain (A calls B calls C).
         Any change to C's interface breaks A and B.
  Fix: introduce an event/async interface. A publishes
       an event. B and C consume it independently.
       No direct synchronous coupling.

Smell 2: Services share a database.
  Cause: Order service reads the inventory table directly.
         A schema change to inventory breaks Orders.
  Fix: Inventory service exposes an API.
       Order service calls Inventory API only.
       Inventory owns its schema. Orders never directly
       access inventory tables.

Smell 3: Shared library must be updated in sync.
  Cause: "proto-shared" library with DTOs used by all
         services. New field in OrderDTO: must update
         all services that use it simultaneously.
  Fix: API contracts (Protobuf, OpenAPI) with backward
       compatibility. New fields are optional. Old clients
       ignore unknown fields. Independent evolution.

Diagnostic command:
  Draw a dependency graph (who calls whom).
  If the graph has cycles: distributed monolith.
  If most services call one central service:
  that central service is the new monolith bottleneck.
  If deploying one service requires N others: coupled.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `System Design Process` - the broader design process
  in which this architecture decision is made
- `Scalability Fundamentals` - understanding scale
  characteristics that drive this decision

**Builds On This (learn these next):**
- `Technology Selection Framework` - general framework
  for architectural decisions; this entry is a specific
  application of that framework
- `High Availability Design` - microservices change
  how high availability is designed (per-service SLA)
- `API Gateway Pattern` - the API gateway is a critical
  component in any microservices architecture

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MONOLITH    │ < 10 engineers. Domain unclear.           │
│ WINS        │ Consistency critical. No platform team.   │
├─────────────┼──────────────────────────────────────────  │
│ MICROSERVICES│ 50+ engineers. Team independence needed. │
│ WINS        │ Independent scaling. Compliance isolation. │
│             │ Different tech per service.              │
├─────────────┼──────────────────────────────────────────  │
│ HYBRID      │ Monolith + 2-3 extracted services.       │
│ (COMMON)    │ Extract: payment (PCI), ML model,        │
│             │ high-write service. Keep rest in mono.   │
├─────────────┼──────────────────────────────────────────  │
│ DANGER      │ Distributed monolith: micro ops cost,    │
│             │ no independence benefit.                 │
│             │ Caused by: poor service boundaries.     │
├─────────────┼──────────────────────────────────────────  │
│ RULE        │ "Start monolith. Extract when you have  │
│             │  a clear reason." - Martin Fowler       │
├─────────────┼──────────────────────────────────────────  │
│ PREREQUISITE│ Well-structured monolith first.         │
│             │ Good module boundaries = easy extract.   │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Microservices solve organizational     │
│             │  scaling, not just technical scaling."  │
├─────────────┼──────────────────────────────────────────  │
│ END         │ SYD category complete: 81/81 entries.    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Start with a modular monolith. Structure it with clear
   module boundaries and clean interfaces. This is a
   prerequisite for future microservices extraction:
   a poorly structured monolith produces a poorly
   structured distributed system (distributed monolith).
   Good modules → easy extraction. Bad modules →
   impossible extraction without a full rewrite.
2. Extract services when there is a specific reason:
   (a) compliance isolation (PCI DSS, HIPAA);
   (b) team ownership (a team of 5 should own one service);
   (c) independent scaling (10x QPS difference per component);
   (d) different language/runtime requirements.
   Do NOT extract because "microservices are better."
3. The distributed monolith is the worst outcome: microservices
   operational complexity without the independence benefits.
   It happens when services are tightly coupled (shared database,
   synchronous call chains, shared schema). Prevent it by
   designing service boundaries with DDD bounded contexts
   and ensuring each service can deploy independently.

**Interview one-liner:**
"Monolith wins: < 50 engineers, unclear domain, consistency-critical ops, no platform
team. Microservices wins: 50+ engineers needing team independence, per-service scaling
requirements, compliance isolation (PCI/HIPAA), polyglot tech requirements. Start
with modular monolith (clean module interfaces); extract incrementally with clear
reasons. Hybrid (monolith + extracted payment/ML service) is often right for mid-size
orgs. Danger: distributed monolith - services tightly coupled (shared DB, sync call
chains) = micro ops cost with no independence benefit. Prevent with DDD bounded
contexts. Core insight: microservices solve organizational scaling, not just technical."
