---
id: MSV-001
title: Monolith vs Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★☆☆
depends_on: DST-001, DST-002
used_by: MSV-002, MSV-005, MSV-036, MSV-085
related: MSV-004, MSV-031, MSV-090
tags:
  - microservices
  - architecture
  - foundational
  - tradeoff
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 1
permalink: /microservices/monolith-vs-microservices/
---

# MSV-001 - Monolith vs Microservices

⚡ TL;DR - A monolith ships everything as one deployable unit;
microservices split that unit into independent services, each
ownable, deployable, and scalable on its own.

| #001 | Category: Microservices | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | What Is a Distributed System, Why Distribution Is Hard | |
| **Used by:** | Microservices Architecture, Service Decomposition, Strangler Fig Pattern, Monolith to Microservices Migration | |
| **Related:** | Modular Monolith, Domain-Driven Design, Anti-Patterns in Microservices | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a 500-developer engineering org where every feature,
from checkout to email notification to fraud detection, lives
in one codebase. A junior engineer changes the tax calculation
function. To deploy that one change, the entire application must
be rebuilt, tested end-to-end, and redeployed. That process takes
four hours. Every team waits on every other team.

**THE BREAKING POINT:**
The checkout team is ready. The email team is blocked by a bug
in the fraud module. Nobody ships. The release manager runs a
Thursday-night deployment ceremony. A bug in payment rolls back
all twelve features that were bundled in. The organisation ships
twice a month and calls that "continuous delivery."

At 10x load during the holiday peak, you cannot scale just the
checkout service - you must replicate the entire application.
You pay for idle fraud-detection CPU just to serve more checkouts.

**THE INVENTION MOMENT:**
This is exactly why Microservices was created: to give each
business capability independent deployability, independent
scalability, and independent ownership - so teams can move at
their own pace without coupling to the whole system.

**EVOLUTION:**
Before microservices, Service-Oriented Architecture (SOA) tried
to solve team coupling with XML-based SOAP services and a central
Enterprise Service Bus - it helped but introduced its own
bottlenecks. Netflix and Amazon pioneered fine-grained microservices
around 2010-2012, publishing lessons that the industry adopted.
Today the pendulum swings back: many teams rediscover the Modular
Monolith as a simpler starting point before committing to
distributed complexity.

---

### 📘 Textbook Definition

A **monolith** is an application deployed as a single unit in which
all modules - UI, business logic, data access - share one codebase,
one build artifact, and one deployment process.

**Microservices** is an architectural style in which a system is
composed of small, independently deployable services, each
responsible for a single business capability, communicating over
well-defined network APIs (typically HTTP/REST or messaging).

The choice determines coupling topology: a monolith has in-process
coupling (fast, strongly typed), while microservices have network
coupling (slower, loosely typed, fault-tolerant by design).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A monolith is one big jar; microservices are many small jars
that call each other over the network.

**One analogy:**
> Think of a Swiss Army knife versus a toolbox. The Swiss Army
> knife (monolith) is compact and fast to grab, but when the
> blade breaks you replace the whole knife. The toolbox
> (microservices) lets you upgrade or swap just the screwdriver
> without touching anything else - but it takes more space and
> coordination to use.

**One insight:**
The real difference is not technical - it is organisational.
Microservices encode Conway's Law deliberately: each service
boundary maps to a team boundary, so teams can ship and own
their piece without waiting for others. The distributed
complexity is the cost of that autonomy.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every deployable unit has a deployment surface: the set of
   things that must change together to ship a feature.
2. Scaling is only possible at the granularity of the deployable
   unit - you cannot scale half a monolith.
3. Failure isolation is bounded by the process boundary: a crash
   in one module takes down everything in the same process.

**DERIVED DESIGN:**
Given those invariants, a monolith is the simplest possible
system - one deployable unit, one process, one scaling boundary.
That simplicity is a genuine advantage for small teams: no
network latency between calls, no distributed transactions, no
service discovery, no independent deployment pipelines.

Microservices decompose the deployable unit along business
capability lines. Each service gets its own process boundary,
which means: independent deployment (invariant 1), independent
scaling (invariant 2), and failure isolation (invariant 3). The
cost is that every cross-service call becomes a network call -
slower, fallible, and harder to reason about.

**THE TRADE-OFFS:**

| Dimension | Monolith | Microservices |
|---|---|---|
| Deployment | One artifact, whole-system deploy | Per-service, independent |
| Scaling | Replicate everything | Scale individual services |
| Inter-module calls | In-process (nanoseconds) | Network (milliseconds) |
| Data consistency | Single DB, ACID transactions | Distributed, eventual |
| Team autonomy | Low - shared codebase | High - independent repos |
| Operational complexity | Low | High |
| Testing | Simpler - one process | Harder - service contracts |

**Gain:** Team and deployment independence, per-service scaling,
fault isolation.
**Cost:** Network latency, distributed data consistency, massive
operational overhead (service mesh, distributed tracing, contract
testing, multi-repo CI/CD).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any system split across process boundaries will have
network latency, partial failure, and eventual consistency. These
cannot be engineered away - they are physics.
**Accidental:** Most of the tooling burden (service discovery
frameworks, distributed tracing stacks, contract testing suites)
exists because the ecosystem had to be built from scratch. A
mature platform (Kubernetes + Istio + OpenTelemetry) absorbs much
of this accidental complexity.

---

### 🧪 Thought Experiment

**SETUP:**
You have a three-developer startup with an e-commerce application:
user accounts, product catalog, and order processing. You build
it as a monolith. Three months later you have 10 developers and
a payments team joining.

**WHAT HAPPENS WITHOUT MICROSERVICES:**
The payments team commits code to the same repository. Their
payment library upgrade conflicts with the order module's version.
Both teams spend a week resolving dependency conflicts. The
payments team cannot deploy without the order team's sign-off.
A bug in the product catalog brings down checkout because they
share a database connection pool.

**WHAT HAPPENS WITH MICROSERVICES:**
The payments service lives in its own repository, ships its own
artifact, runs its own database. The payments team deploys
independently on Friday while the catalog team fixes a bug on
Monday. A catalog service outage is isolated - checkout keeps
working by serving cached data. Each team owns their service.

**THE INSIGHT:**
The monolith vs microservices decision is fundamentally a decision
about how you want to distribute cognitive load: across a shared
codebase (monolith) or across explicit network contracts
(microservices). Neither is universally better - the right choice
depends on team size, team structure, and scale requirements.

---

### 🧠 Mental Model / Analogy

> A monolith is a restaurant with one open kitchen: every chef
> sees and can affect every dish. Microservices is a food court:
> each stall is its own kitchen, staff, and menu - customers
> (the API gateway) route to the right stall.

- "One kitchen" - the monolith single codebase
- "Every chef sees every dish" - shared code and database
- "Food court" - microservices cluster
- "Each stall, own kitchen" - per-service deployment unit
- "Own staff" - independent team ownership
- "Own menu" - service-specific API contract
- "Customer routing" - API gateway or service mesh

Where this analogy breaks down: the food court analogy implies
physical separation, but microservices still share the same
network, and a misconfigured stall can spray 500 errors that
affect how the whole food court is perceived.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A monolith is one giant program. Microservices is many small
programs that talk to each other. Your startup likely started
as a monolith. Amazon and Netflix eventually split into thousands
of microservices because their teams got too big to coordinate.

**Level 2 - How to use it (junior developer):**
If your team has fewer than ~10-15 engineers and ships features
weekly, a well-structured monolith (good module boundaries,
clean packages) is almost always the right starting point.
Start with microservices only if you have clear team autonomy
requirements or wildly different scaling profiles (e.g., a
video transcoding service that needs 100x the compute of
everything else).

**Level 3 - How it works (mid-level engineer):**
The operational difference: a monolith has one CI/CD pipeline
producing one artifact deployed to n replicas behind a load
balancer. Microservices has one pipeline PER service, each
producing its own artifact, each deployed independently, each
with its own database. Cross-service calls become HTTP or
messaging. Data consistency moves from ACID transactions to
eventually consistent sagas.

**Level 4 - Why it was designed this way (senior/staff):**
Microservices emerged at companies where the bottleneck was team
coordination, not raw performance. Amazon's "two-pizza team" rule
preceded their service decomposition - the architecture followed
the org structure, not the reverse. The design insight is that
network boundaries enforce API contracts, which prevent the
hidden coupling that destroys maintainability in large monoliths.
The cost is significant: every call that was once a function
invocation becomes a network hop that can fail, timeout, or
produce unexpected latency.

**Level 5 - Mastery (distinguished engineer):**
The expert reads "we're migrating to microservices" as a
sociotechnical statement, not a technical one. The real
question is: does your organisation have the operational
maturity - platform teams, observability tooling, on-call
culture, contract discipline - to absorb the complexity tax?
A microservices architecture run by a team without that maturity
creates a "distributed monolith": all the operational cost of
distribution, none of the deployment independence. Staff
engineers recognise this antipattern before it is built.
The decision framework: "Can your team independently deploy,
scale, and on-call own each service?" If no for even one
service, you do not have microservices - you have a network
monolith.

---

### ⚙️ How It Works (Mechanism)

**MONOLITH RUNTIME MODEL:**

```
┌─────────────────────────────────────────┐
│            MONOLITH PROCESS             │
│  ┌──────────┐  ┌──────────┐            │
│  │  Users   │  │ Orders   │            │
│  │  Module  │  │ Module   │            │
│  └────┬─────┘  └────┬─────┘            │
│       │              │ in-process call  │
│  ┌────┴──────────────┴──────────────┐  │
│  │           Shared Database        │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
       Single JVM, single DB connection
       pool, single deployment artifact
```

Everything runs in one JVM (or process). Module-to-module calls
are direct method invocations - nanosecond latency. Transactions
span the full database via JDBC. A single `./gradlew build`
produces one runnable jar. Deploying a one-line bug fix rebuilds
and redeploys everything.

**MICROSERVICES RUNTIME MODEL:**

```
Client
  │
  ▼
┌─────────────────┐
│   API Gateway   │ ← single entry point
└──────┬──────────┘
       │  routes by path / domain
  ┌────┴────┐    ┌──────────────┐
  │  Users  │    │   Orders     │
  │ Service │    │   Service    │
  │  :8081  │    │    :8082     │
  └────┬────┘    └──────┬───────┘
       │                │
  ┌────┴───┐      ┌─────┴────┐
  │ Users  │      │  Orders  │
  │   DB   │      │    DB    │
  └────────┘      └──────────┘
       ^─────────────────^
       Network call (HTTP/gRPC/message)
       May fail, may timeout, may return
       stale data
```

Each service runs in its own process, has its own database,
and is deployed independently. Every cross-service interaction
is a network call - subject to latency (1-50ms typical), partial
failure, and versioning.

**DEPLOYMENT LIFECYCLE:**

Monolith:
```
1 change → 1 build → 1 artifact → 1 deploy (all modules)
Timeline: minutes to hours
Risk: one bad module can block entire release
```

Microservices:
```
1 change → 1 service build → 1 service deploy (that service only)
Timeline: minutes per service
Risk: service contract breaks can cause distributed failures
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (monolith):**
```
HTTP Request → Load Balancer → Monolith Process
  → Controller → Service → Repository → DB
  → Response (all in-process, ~10ms)
```

**NORMAL FLOW (microservices):**
```
HTTP Request → API Gateway → [route decision]
  → User Service (auth check, ~5ms)
  → Order Service (business logic, ~15ms)
    → Calls Inventory Service (stock check, ~10ms network)
    → Calls Notification Service (fire-and-forget, async)
  → Response (~30ms total - 3x slower due to network hops)
```

**FAILURE PATH (microservices):**
```
Inventory Service goes down
  → Order Service call times out (after 5s default)
  → Order Service returns 503 to API Gateway
  → User sees "checkout unavailable"
  WITHOUT a Circuit Breaker this repeats on every request,
  exhausting Order Service thread pool (cascade failure)
```

**WHAT CHANGES AT SCALE:**
At 10k RPS on a monolith, every module scales together - you
provision 20 instances of the whole jar even if only the
checkout endpoint is hot. At 10k RPS on microservices, you
scale only the Order Service to 20 instances while User Service
stays at 3. The network hop count grows too: at 1000 services,
a single user request may traverse 10+ services, each adding
latency. P99 latency degrades faster in microservices at scale
unless circuit breakers and caching are aggressive.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: calling another module**

```java
// BAD: monolith code pretending to be microservices
// Direct import couples OrderService to UserService code
import com.example.user.UserRepository;

@Service
public class OrderService {
    @Autowired
    private UserRepository userRepo; // shared DB access!

    public Order createOrder(String userId, Cart cart) {
        User user = userRepo.findById(userId); // direct DB call
        // ... creates order
    }
}
```

```java
// GOOD: microservices - OrderService calls UserService via HTTP
@Service
public class OrderService {
    private final UserServiceClient userClient;

    public Order createOrder(String userId, Cart cart) {
        // HTTP call - can fail, must handle
        UserDTO user = userClient.getUser(userId);
        // ... creates order in own DB
    }
}

// Feign client - declarative HTTP
@FeignClient(name = "user-service",
             url = "${services.user.url}")
public interface UserServiceClient {
    @GetMapping("/users/{id}")
    UserDTO getUser(@PathVariable String id);
}
```

The key difference: the BAD example shares a database and imports
internal classes. The GOOD example communicates only via a
declared API contract and handles the possibility of network
failure.

**Example 2 - Production pattern: health endpoint**

```java
// Every microservice MUST expose a health endpoint
// Spring Boot Actuator does this automatically:
// GET /actuator/health → {"status": "UP"}

// Custom health check - include dependency status:
@Component
public class DatabaseHealthIndicator
        implements HealthIndicator {

    @Override
    public Health health() {
        try {
            // ping DB with 1-second timeout
            jdbcTemplate.queryForObject(
                "SELECT 1", Integer.class);
            return Health.up().build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

**How to test / verify correctness:**
Test the service boundary in isolation: mock the HTTP client
and assert that `OrderService.createOrder()` handles 503
responses gracefully (returns fallback, does not throw). Use
WireMock to stub downstream services in integration tests.

---

### ⚖️ Comparison Table

| Architecture | Team Scale | Deploy Freq | Ops Overhead | Best For |
|---|---|---|---|---|
| **Monolith** | 1-15 devs | Weekly | Low | Early-stage, single team |
| Modular Monolith | 10-50 devs | Weekly | Low-medium | Growing team, shared DB OK |
| Microservices | 50+ devs | Daily/hourly | High | Large orgs, scale isolation |
| Serverless | Any | Continuous | Very low | Event-driven, spiky load |

**How to choose:** Start with a monolith (or modular monolith)
until you feel real pain from team coupling or scaling limits.
Migrate to microservices service-by-service (Strangler Fig)
when autonomous team deployment becomes a genuine blocker, not
before.

**Decision Tree:**
Team < 15 engineers? → Monolith
Team 15-50, modules clearly separable? → Modular Monolith
Team 50+, teams blocked on each other? → Microservices
Wildly different scaling profiles? → Extract that service first
No platform team / DevOps maturity? → Avoid Microservices yet

---

### 🔁 Flow / Lifecycle

```
Organization Growth Lifecycle:
─────────────────────────────

1. Startup (1-5 devs)
   └─ Single monolith, one DB, fast iteration

2. Growth (10-30 devs)
   └─ Monolith grows, modules emerge,
      deploy pain starts

3. Scaling Pain
   └─ "We can't deploy without breaking each other"
      → Identify first extraction candidate
      → Extract using Strangler Fig Pattern

4. First Microservice
   └─ One service extracted, owns its DB
      → Learn: deployment, observability, contracts

5. Steady State
   └─ N services, each team owns 1-3
      → Platform team emerges to manage shared infra

Failure Path:
   Skip steps 1-3 → Start at step 4
   → Distributed Monolith antipattern
   → All complexity, no benefit
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Microservices are always faster | Network hops add 1-50ms per call. A monolith in-process call is 1000x faster. Microservices enable independent scaling, not raw speed. |
| Microservices solve bad code | A microservice with bad internal design is still bad. Decomposition doesn't fix code quality. |
| Each service needs its own DB technology | Polyglot persistence is an option, not a requirement. Using the same DB technology across services is fine initially. |
| Microservices require containers | Microservices are a design style. They can run on VMs, bare metal, or PaaS. Containers are a popular deployment mechanism, not a requirement. |
| You should start with microservices for a new project | "Don't start with microservices" - Martin Fowler. Start monolith, extract when you feel the real pain. |
| Microservices eliminate coupling | They eliminate deploy-time coupling. Runtime coupling (one service waiting for another) can be just as bad if not designed carefully. |

---

### 🚨 Failure Modes & Diagnosis

**Distributed Monolith (the most dangerous failure)**

**Symptom:**
Services exist but cannot be deployed independently. Deploying
Service A requires deploying Service B and C simultaneously.
Teams coordinate "release trains" just like with a monolith.

**Root Cause:**
Services share a database schema. Service A reads tables owned
by Service B. Services call each other synchronously in ways
that create deploy-time ordering requirements.

**Diagnostic Command:**
```bash
# Find services sharing DB tables (check connection strings)
grep -r "jdbc:postgresql://shared-db" services/*/src/

# Find synchronous call graphs - trace a request
curl -H "X-Trace-Id: test" http://gateway/api/order/1
# Check logs across all services for that trace ID
```

**Fix:**
```yaml
# BAD: shared DB in docker-compose for all services
services:
  orders-service:
    environment:
      DB_URL: jdbc:postgresql://shared-db/app
  users-service:
    environment:
      DB_URL: jdbc:postgresql://shared-db/app  # same DB!

# GOOD: each service has its own DB
services:
  orders-service:
    environment:
      DB_URL: jdbc:postgresql://orders-db/orders
  users-service:
    environment:
      DB_URL: jdbc:postgresql://users-db/users
```

**Prevention:**
Enforce "database per service" as a hard rule at architecture
review. No service reads another service's tables - ever.

---

**Cascade Failure Without Circuit Breakers**

**Symptom:**
One slow service causes all calling services to exhaust their
thread pools. The entire system goes down when one service is
slow, not just the callers of that service.

**Root Cause:**
Synchronous HTTP calls without timeouts fill caller thread
pools. 100 threads each waiting 30 seconds = no capacity for
other requests.

**Diagnostic Command:**
```bash
# Check thread pool exhaustion
curl http://order-service:8080/actuator/metrics/ \
  executor.pool.size

# Check active HTTP connections
ss -s | grep ESTABLISHED
netstat -an | grep TIME_WAIT | wc -l
```

**Fix:**
Set aggressive timeouts and add circuit breakers (see MSV-044).
```yaml
# application.yml
resilience4j:
  circuitbreaker:
    instances:
      inventory-service:
        slidingWindowSize: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 10s
feign:
  client:
    config:
      inventory-service:
        connectTimeout: 1000
        readTimeout: 3000
```

**Prevention:**
Never call a downstream service without a timeout. Configure
circuit breakers from day one on all service-to-service calls.

---

**Data Inconsistency Without Saga**

**Symptom:**
Order created in Orders DB but payment charge failed. Customer
has an order confirmation but no payment taken. Database shows
order status "pending" forever.

**Root Cause:**
Cross-service operations were not implemented as compensating
transactions. A failure in Step 2 left Step 1's effects in place.

**Diagnostic Command:**
```bash
# Find orphaned orders (no matching payment)
psql orders_db -c "
  SELECT o.id, o.status, o.created_at
  FROM orders o
  LEFT JOIN payment_confirmations p
    ON p.order_id = o.id
  WHERE p.id IS NULL
    AND o.status = 'pending'
    AND o.created_at < NOW() - INTERVAL '10 minutes';"
```

**Fix:**
Implement the Saga pattern (see MSV-046) with compensating
transactions or event-driven choreography.

**Prevention:**
Any multi-service workflow involving money or critical state
must be modelled as a saga before implementation begins.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Is a Distributed System` - microservices are distributed
  systems; understand the fallacies first
- `HTTP and APIs` - all inter-service calls are HTTP or messaging;
  know the protocol before building on it

**Builds On This (learn these next):**
- `Microservices Architecture` - the structural patterns that
  make microservices work in practice
- `Service Decomposition` - how to find the right service boundaries
- `Strangler Fig Pattern` - how to migrate a monolith incrementally
- `Domain-Driven Design` - the conceptual toolkit for drawing
  service boundaries correctly
- `Circuit Breaker` - the first resilience pattern every
  microservices system needs

**Alternatives / Comparisons:**
- `Modular Monolith` - structured monolith with clear module
  boundaries; lower operational cost, team autonomy through
  code discipline rather than deployment independence
- `Serverless` - function-level decomposition; even finer
  granularity than microservices but with cold-start trade-offs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two deployment models: one-jar (monolith)  │
│              │ vs many-jars (microservices)               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Teams blocked on shared codebase; can't   │
│ SOLVES       │ scale or deploy independently              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The boundary is organisational, not just  │
│              │ technical - services = team boundaries     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Team > 15 devs; deploy coupling is real   │
│              │ pain; scaling profiles diverge             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small team; no platform maturity; early   │
│              │ product/market fit stage                   │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Distributed monolith: services sharing DB  │
│              │ or deployed together = worst of both worlds│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Team autonomy + scaling vs network         │
│              │ complexity + operational overhead          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Microservices buy team independence;      │
│              │  make sure you can afford the price tag"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Modular Monolith → Service Decomposition  │
│              │ → Domain-Driven Design                     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Microservices buy deployment independence at the cost of
   distributed system complexity - you must earn the right to
   use them.
2. The distributed monolith antipattern (services sharing a DB)
   gives you all the cost and none of the benefit.
3. Start with a (modular) monolith. Extract services when you
   feel real team coordination pain, not before.

**Interview one-liner:**
"A monolith is one deployable unit sharing a codebase and
database. Microservices decompose that into independently
deployable services each owning their data. The decision is
really about whether your organisation can absorb the
operational complexity - small teams almost always start
with a monolith first."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Coupling drives coordination cost. Every time two things must
change, deploy, or fail together, a human coordination event
is required. Architecture is the practice of putting coupling
where you can afford it and removing it where you cannot.

**Where else this pattern appears:**
- Database normalisation vs denormalisation - coupling query
  simplicity to write complexity; the same trade-off applies
- Git monorepo vs multi-repo - same team-autonomy tension as
  monolith vs microservices
- Microkernel vs monolithic OS kernels - the same isolation
  vs performance trade-off at the OS level

**Industry applications:**
- Financial services - often keep a monolith for the transaction
  core (strong consistency required) and extract microservices
  only for auxiliary services (notifications, reporting)
- E-commerce - checkout/payment as a separate service is almost
  universal because of its different scaling and compliance
  requirements; the product catalog often stays in a larger
  service or a modular monolith

---

### 💡 The Surprising Truth

Most engineers think Amazon Web Services was born microservices-
first. In fact, Amazon's early retail system was a tightly
coupled monolith. Jeff Bezos issued his "API mandate" in 2002
requiring all teams to expose functionality only through APIs -
not because microservices were the goal, but because the codebase
had become unmaintainable. The microservices architecture emerged
as a side effect of enforcing communication discipline between
teams. The lesson: the tooling (APIs, services) followed the
organisational rule, not the reverse.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Describe to a product manager why splitting
   the user service from the order service means their teams
   can ship independently, without using the word "microservice."
2. **DEBUG** Given a system where deploying Service A always
   requires deploying Service B, identify whether it is a
   shared-database problem, a synchronous call ordering problem,
   or a shared-library version problem.
3. **DECIDE** A 12-engineer startup asks whether to begin with
   microservices. Articulate the exact conditions that would
   change your answer from "no, start monolith" to "yes,
   extract this service now."
4. **BUILD** Convert a monolith UserModule that shares a DB
   with OrderModule into a separate UserService by defining
   the HTTP API contract, migrating the schema to a separate
   DB, and replacing direct calls with a Feign client.
5. **EXTEND** Apply the coupling-vs-autonomy reasoning to
   decide whether a data warehouse should use one schema
   (monolith) or separate schemas per business domain -
   identify the precise trade-offs.

---

### 🧠 Think About This Before We Continue

**Q1.** Your company has 200 engineers across 20 teams working
on a single Java monolith that deploys successfully twice a
week. A new VP of Engineering mandates a full migration to
microservices over 18 months. What is the single biggest risk
that could make the system MORE brittle after the migration
than before, and what architectural rule would you enforce from
day one to prevent it?
*Hint: Think about what "independent deployment" actually
requires at the data layer, not just the code layer.*

**Q2.** A notification service currently runs inside the
monolith. It is called by 15 other modules at peak load of
50k calls/minute. If extracted to a microservice, what happens
to the calling modules at 100k calls/minute when the notification
service takes 500ms to respond instead of the current 0.1ms
in-process? Trace through the thread pool mathematics.
*Hint: Consider a web server with a fixed thread pool of 200
threads and a 30-second default HTTP timeout.*

**Q3.** Take a monolith order management system and design its
first service extraction. Choose the service boundary, specify
its API contract (3-5 endpoints), define what data it owns, and
write one compensating transaction for a failure scenario.
What would you instrument first to know if the extraction
succeeded?
*Hint: Start from the scaling and team ownership dimensions,
not from the code structure.*

---

### 🎯 Interview Deep-Dive

**Q1: "When would you NOT migrate from a monolith to
microservices, even under management pressure?"**

*Why they ask:* Tests whether the candidate understands the
genuine trade-offs or is just following a trend.

*Strong answer includes:*
- Team size is small (< 15 engineers) - coordination cost
  is already low
- No platform team to handle service mesh, distributed
  tracing, or independent CI/CD pipelines
- Domain boundaries are not clear yet - premature decomposition
  creates wrong service boundaries that are expensive to fix
- Concrete risk: you end up with a distributed monolith

**Q2: "What is a distributed monolith and why is it worse
than either a true monolith or true microservices?"**

*Why they ask:* Separates engineers who understand the
principle from those who just split code into jars.

*Strong answer includes:*
- Definition: services that cannot be deployed independently
  due to shared DB schema, synchronous coupling, or shared
  library version lock
- Costs all three of: network latency, operational complexity,
  and distributed consistency
- Gains none of the benefits: still needs coordinated deploys,
  still has shared failure domains
- Recognition: you have microservices on paper but still run
  deployment ceremonies and coordinated release trains

**Q3: "Walk me through how you would extract your first service
from a monolith. What do you check first?"**

*Why they ask:* Tests practical migration experience, not just
theoretical knowledge.

*Strong answer includes:*
- Choose a service with a clear boundary and no shared tables
  (notifications, file processing are common first choices)
- Strangler Fig: keep old code running, route traffic to new
  service gradually, validate, then delete old code
- Data migration: create a separate DB, add a sync mechanism,
  cut over when the new DB is current
- Day-one observability: health endpoint, distributed tracing,
  alerts on error rate before flipping traffic

**Q4: "A service you own averages 20ms in staging but 250ms in
production at peak. How do you diagnose this?"**

*Why they ask:* Tests production debugging skills in a
distributed system context.

*Strong answer includes:*
- Distributed tracing (Jaeger/Zipkin/OpenTelemetry) to find
  which downstream call added the latency
- Check if 250ms correlates with cold cache, DB query plan
  changes, or GC pauses in the service itself
- Check if a downstream dependency introduced a timeout or
  retry loop adding latency amplification
- P99 vs P50 analysis - if P99 is 250ms but P50 is 20ms,
  suspect a slow DB query or external call affecting tail latency