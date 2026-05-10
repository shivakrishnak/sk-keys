---
layout: default
title: "Monolith vs Microservices"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 11
permalink: /microservices/monolith-vs-microservices/
id: MSV-011
category: Microservices
difficulty: ★☆☆
depends_on: HTTP & APIs, Deployment, Distributed Systems
used_by: Service Decomposition, API Gateway, Service Discovery
related: Modular Monolith, Service Mesh, Domain-Driven Design
tags:
  - microservices
  - architecture
  - distributed
  - foundational
  - pattern
status: complete
version: 2
---

# MSV-011 - Monolith vs Microservices

⚡ TL;DR - A monolith bundles all functionality into one deployable unit; microservices split it into independently deployable services that communicate over a network.

| #626 | Category: Microservices | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | HTTP & APIs, Deployment, Distributed Systems | |
| **Used by:** | Service Decomposition, API Gateway, Service Discovery | |
| **Related:** | Modular Monolith, Service Mesh, Domain-Driven Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a 200-developer team all working inside a single Java codebase. Every feature-payments, notifications, user management, inventory-lives in the same process. To release a one-line bug fix in payments, you must rebuild, retest, and redeploy the entire application. A bad deployment takes down every feature at once. The search team can't choose a different database optimised for text; they must use whatever the billing team locked in five years ago. Scaling the checkout service during Black Friday means scaling every other service too, wasting enormous compute.

**THE BREAKING POINT:**
Teams block each other. Build pipelines take 45 minutes. A memory leak in the recommendation engine crashes the checkout page. Deployments become so risky that the team only releases on Friday nights, making things worse.

**THE INVENTION MOMENT:**
This is exactly why the Microservices architectural style was created - to allow large organisations to deploy individual capabilities independently, scale them separately, and let teams own their own services end-to-end.


**EVOLUTION:**
The Monolith vs Microservices debate emerged as Amazon's "two-pizza team" philosophy (2002) and Netflix's open-sourcing of microservices infrastructure (2013-2015) made microservices culturally dominant. The movement peaked around 2014-2016 when Netflix, Uber, and Airbnb case studies made microservices appear universally beneficial. DHH's "Majestic Monolith" post (2016) marked the rebalancing: practitioners began documenting operational complexity costs that success stories had omitted. The discipline now recognises the decision is context-dependent: team size, deployment frequency, scaling requirements, and organisational structure together determine which architecture is correct.

**EVOLUTION:**
The Monolith vs Microservices debate emerged as Amazon's "two-pizza team" philosophy (2002) and Netflix's open-sourcing of microservices infrastructure (2013-2015) made microservices culturally dominant. The movement peaked around 2014-2016 when Netflix, Uber, and Airbnb case studies made microservices appear universally beneficial. DHH's "Majestic Monolith" post (2016) marked the rebalancing: practitioners began documenting operational complexity costs that success stories had omitted. The discipline now recognises the decision is context-dependent: team size, deployment frequency, scaling requirements, and organisational structure together determine which architecture is correct.
---

### 📘 Textbook Definition

A **monolith** is an application where all components are deployed and run as a single process, sharing memory and libraries directly. **Microservices** is an architectural style where an application is structured as a collection of small, autonomous services, each responsible for a bounded capability, communicating over lightweight protocols (typically HTTP/REST or messaging). Each microservice is independently deployable, scalable, and replaceable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A monolith is one big program; microservices are many small programs that talk to each other.

**One analogy:**
> A monolith is like a Swiss Army knife - everything in one tool. If the scissors break, the whole knife is out of service. Microservices are like a kitchen drawer full of specialist tools - the broken scissors don't affect the can opener, and you can replace just the scissors.

**One insight:**
Microservices solve an *organisational* problem as much as a technical one. Conway's Law states that system architecture mirrors the communication structure of the organisation that builds it. Small autonomous teams need small autonomous services.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A monolith has a single deployment unit - you release everything or nothing.
2. Microservices have independent deployment units - each service releases on its own schedule.
3. Microservices communicate over a network boundary, introducing latency and failure modes that in-process calls don't have.

**DERIVED DESIGN:**
Because services now communicate over a network, you gain deployment independence but pay with network complexity. Each service owns its data store (no shared database), enforcing isolation. This means cross-service queries require API calls or event streams rather than SQL JOINs. The network becomes the integration fabric.

**THE TRADE-OFFS:**
**Gain:** Independent deployability, independent scalability, technology heterogeneity, team autonomy, fault isolation.
**Cost:** Network latency, distributed tracing complexity, eventual consistency challenges, operational overhead (dozens of services to monitor), harder local development.

---

### 🧪 Thought Experiment

**SETUP:**
You have two features: user authentication and order history. In a monolith both are functions in the same codebase. In microservices they are two separate services.

**WHAT HAPPENS WITHOUT MICROSERVICES:**
A new hire introduces a null pointer in the order history code. During peak hour the shared JVM heap fills up. The JVM crashes. Users cannot log in. Authentication and order history fail together even though authentication code is perfectly fine.

**WHAT HAPPENS WITH MICROSERVICES:**
The order history service crashes. Its pod is restarted by Kubernetes within seconds. During those seconds the authentication service - a completely separate process - continues serving login requests unaffected. The blast radius is contained to one service.

**THE INSIGHT:**
Fault isolation is the most underrated benefit of microservices. Independent deployability makes the headline; fault isolation saves you at 2am.

---

### 🧠 Mental Model / Analogy

> Think of a monolith as a single large office building where every department shares the same HVAC, power grid, and entry door. If power fails, everyone is affected. Microservices are separate buildings connected by phone lines - each manages its own utilities, and one building's fire doesn't evacuate the others.

- "Shared building utilities" → shared process, heap, and libraries in a monolith
- "Phone lines between buildings" → HTTP, gRPC, or message queues between services
- "One building loses power" → one microservice crashes
- "Other buildings stay open" → fault isolation across services

Where this analogy breaks down: in real buildings, calling across buildings is slower than walking across the hall - in microservices the network latency is real and must be designed around, unlike in-process calls in a monolith.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A monolith is one big application. Microservices are many small applications that work together. Both approaches build the same product, but they divide the work differently.

**Level 2 - How to use it (junior developer):**
Start with a monolith - it is simpler to develop, test, and deploy. Move to microservices when team size, release frequency, or scaling requirements make the monolith painful. Split along business capabilities (orders, payments, notifications), not technical layers. Each service exposes an HTTP/REST or gRPC API.

**Level 3 - How it works (mid-level engineer):**
Each microservice runs as an independent OS process (or container). Services discover each other via a service registry (Consul, Eureka) or DNS. Inter-service calls cross a real network, so you need timeouts, retries, and circuit breakers. Each service owns its own database to avoid coupling. Distributed tracing (Jaeger, Zipkin) correlates logs across services using a shared Correlation ID header.

**Level 4 - Why it was designed this way (senior/staff):**
Microservices grew from SOA lessons at Amazon and Netflix in the mid-2000s. The key insight was Conway's Law: if you want autonomous teams, give them autonomous services. The two-pizza-team rule (a team fed by two pizzas owns one service) defines the right granularity. The hardest unsolved problems remain: distributed transactions (solved with Saga or two-phase commit, each with severe trade-offs) and local development (mitigated by Docker Compose or service stubs).

---

### ⚙️ How It Works (Mechanism)

**Monolith deployment:**

```
┌─────────────────────────────────────┐
│         Monolith Process            │
│  ┌─────────┐ ┌──────────┐           │
│  │  Auth   │ │  Orders  │           │
│  └─────────┘ └──────────┘           │
│  ┌─────────┐ ┌──────────┐           │
│  │Payments │ │Inventory │           │
│  └─────────┘ └──────────┘           │
│       Single shared DB              │
└─────────────────────────────────────┘
        One JAR / one deploy
```

All modules live in the same JVM heap. Method calls are in-memory (nanoseconds). One fat JAR gets deployed.

**Microservices deployment:**

```
┌──────────┐   HTTP    ┌──────────┐
│  Auth    │ ────────► │  Orders  │
│  :8081   │           │  :8082   │
└──────────┘           └──────────┘
     │                      │
  Auth DB              Orders DB
┌──────────┐   Event   ┌──────────┐
│Payments  │ ────────► │Inventory │
│  :8083   │  (Kafka)  │  :8084   │
└──────────┘           └──────────┘
```

Each service is its own deployable artifact (Docker image). Communication is over the network. Each service has its own database schema (maybe a different database engine entirely).

**Call path comparison:**

| Aspect | Monolith | Microservices |
|---|---|---|
| Call latency | ~50 ns (in-process) | 1–50 ms (network) |
| Failure scope | Whole app | One service |
| Deploy unit | One JAR | Per-service image |
| Scale unit | Whole app | Per service |
| Data access | Shared DB | Per-service DB |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (monolith):**
Browser → Load Balancer → Single App Process → In-Memory Module Calls → Shared DB → Response

**NORMAL FLOW (microservices):**
Browser → API Gateway → Auth Service → (JWT validated) → Order Service
← YOU ARE HERE → Order DB → Response via Gateway

**FAILURE PATH (microservices):**
Order Service crashes → API Gateway receives 503 → Circuit breaker opens → Fallback response ("orders temporarily unavailable") → Auth, Payments continue unaffected → Kubernetes restarts Order Service pod

**WHAT CHANGES AT SCALE:**
At 10x load, a monolith requires you to provision 10x instances of the entire application even if only the search module is hot. With microservices, only the search service scales. At 1000x, network overhead and inter-service serialisation (JSON encoding/decoding) become measurable - teams switch to binary protocols (Protobuf/gRPC) and introduce caching layers per service.

---

### 💻 Code Example

**Example 1 - BAD: Tight coupling inside a monolith leaking across modules:**

```java
// BAD: OrderService directly calls UserRepository
// - creates hidden coupling between modules
@Service
public class OrderService {
    @Autowired
    private UserRepository userRepo; // owns another module's data!

    public Order placeOrder(long userId, Cart cart) {
        User user = userRepo.findById(userId); // cross-module DB call
        // ...
    }
}
```

**Example 2 - GOOD: Service boundary enforced via HTTP API:**

```java
// GOOD: OrderService calls UserService over HTTP
// - boundary enforced, independently deployable
@Service
public class OrderService {
    private final UserServiceClient userClient;

    public Order placeOrder(long userId, Cart cart) {
        UserDto user = userClient.getUser(userId); // HTTP call
        // circuit breaker wraps this call
        // ...
    }
}

@FeignClient(name = "user-service", url = "${user.service.url}")
public interface UserServiceClient {
    @GetMapping("/users/{id}")
    UserDto getUser(@PathVariable long id);
}
```

**Example 3 - Production: Independent Docker deployment:**

```yaml
# docker-compose.yml - local dev simulation
services:
  order-service:
    image: myapp/order-service:1.4.2
    ports: ["8082:8080"]
    environment:
      USER_SERVICE_URL: http://user-service:8080
  user-service:
    image: myapp/user-service:2.1.0
    ports: ["8081:8080"]
  # Each service has its own DB
  orders-db:
    image: postgres:16
  users-db:
    image: postgres:16
```

---

### ⚖️ Comparison Table

| Architecture | Deployment | Operational Complexity | Best For |
|---|---|---|---|
| **Monolith** | Single unit | Low | Small teams, early-stage products |
| Modular Monolith | Single unit | Low-Medium | Medium teams, clear domain boundaries |
| Microservices | Per-service | High | Large teams, high scale, independent releases |
| Serverless Functions | Per-function | Medium | Event-driven, spiky workloads |

How to choose: start with a monolith until deployment independence or team scale demands the switch - microservices add real operational cost that is not worth it below ~50 engineers.

---

### 🔁 Flow / Lifecycle

```
┌────────────────────────────────────────────────┐
│         Migration Path (Monolith → MSvc)       │
├────────────────────────────────────────────────┤
│ 1. Identify bounded contexts in monolith        │
│ 2. Introduce module boundaries (no cross-calls) │
│ 3. Extract highest-value service first          │
│    (Strangler Fig pattern)                      │
│ 4. Route traffic via API Gateway                │
│ 5. Migrate data ownership per service           │
│ 6. Repeat until monolith is empty               │
│ 7. Decommission monolith                        │
└────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Microservices are always better than monoliths | A monolith is simpler and faster to build for small teams; microservices add enormous operational overhead |
| Each microservice needs its own team | Team ownership is important, but one team can own multiple small services initially |
| Splitting by technical layer (frontend/backend/DB) creates microservices | True microservices split by business capability, not technical layer |
| Microservices eliminate all coupling | They shift coupling from code to network contracts and data schemas - it is not eliminated, just moved |
| You can just split a monolith's database too | Database decomposition is the hardest part of microservices migration and typically requires application-level joins |

---

### 🚨 Failure Modes & Diagnosis

**1. Distributed Monolith**

**Symptom:** Services are separate deployables but cannot be deployed independently - deploying Service A always requires deploying Service B simultaneously.

**Root Cause:** Shared database schema or shared library that encodes inter-service contracts; services coupled at the data layer even though they are separate processes.

**Diagnostic:**
```bash
# Check if multiple services read/write the same DB table
grep -r "orders" services/*/src --include="*.java" | \
  grep "repository\|jdbc" | grep -v "order-service"
```

**Fix:**
```yaml
# BAD: two services use same 'orders' schema
order-service: datasource: jdbc:postgres/shared_db
reporting-service: datasource: jdbc:postgres/shared_db

# GOOD: each service owns its schema or DB
order-service: datasource: jdbc:postgres/orders_db
reporting-service: datasource: jdbc:postgres/reporting_db
```

**Prevention:** Enforce the "database per service" rule from day one; use separate schema namespaces at minimum.

**2. Chatty Services (N+1 Network Pattern)**

**Symptom:** API response latency is several seconds even though each service individually responds in milliseconds.

**Root Cause:** Service A calls Service B, which calls Service C, which calls Service D - all sequentially for a single user request. Network round-trips add up.

**Diagnostic:**
```bash
# Use distributed trace to see call depth
kubectl logs -n observability jaeger-query | grep "operationName"
# or check Jaeger UI for deep call chains
```

**Fix:**
```java
// BAD: sequential calls - 3 × 50ms = 150ms
UserDto user = userClient.getUser(id);         // 50ms
OrderDto order = orderClient.getOrder(id);     // 50ms
PaymentDto pay = paymentClient.getPayment(id); // 50ms

// GOOD: parallel calls using CompletableFuture
CompletableFuture<UserDto> user =
    CompletableFuture.supplyAsync(() -> userClient.getUser(id));
CompletableFuture<OrderDto> order =
    CompletableFuture.supplyAsync(() -> orderClient.getOrder(id));
CompletableFuture.allOf(user, order).join(); // ~50ms total
```

**Prevention:** Model your service interaction graph; prefer event-driven async over request chains deeper than 2 hops.

**3. No Service Versioning**

**Symptom:** Deploying a new version of a service breaks all calling services immediately.

**Root Cause:** Breaking API change was pushed without versioning; no backward compatibility maintained.

**Diagnostic:**
```bash
# Check if consumer services start failing after deployment
kubectl get events --field-selector reason=BackOff -n production
```

**Fix:**
```java
// BAD: rename field immediately breaks consumers
// v1: { "userId": 123 } → v2: { "id": 123 }  ← breaking!

// GOOD: add new field; keep old field; deprecate via header
// v2: { "userId": 123, "id": 123 }  ← both present = non-breaking
@RequestMapping("/v2/users")
public UserDto getUser(...) { ... }
```

**Prevention:** Use semantic versioning for APIs; maintain backward compatibility for at least one major version cycle.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HTTP & APIs` - services communicate primarily over HTTP; REST contract design is foundational
- `Distributed Systems` - microservices inherit all distributed systems problems (latency, partial failure, network partitions)
- `Containers` - the standard packaging format for microservices is Docker containers

**Builds On This (learn these next):**
- `Service Decomposition` - the methodology for deciding how to split a monolith into services
- `API Gateway (Microservices)` - the entry point that routes external requests to the right service
- `Service Discovery` - how services find each other's network addresses at runtime

**Alternatives / Comparisons:**
- `Modular Monolith` - an intermediate step: strong module boundaries but single deployment; lower operational cost than full microservices
- `Serverless` - takes service granularity to its extreme (per-function deployment) with managed infrastructure

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two opposing architectural styles for     │
│              │ structuring applications                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Monoliths can't scale teams or services   │
│ SOLVES       │ independently at large organisational size│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Microservices solve an organisational     │
│              │ problem (team autonomy) as much as a      │
│              │ technical one                             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple teams need independent deploy    │
│              │ cadences or vastly different scale needs  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small team (< 10 devs) or early-stage    │
│              │ product with undefined domain boundaries  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Team autonomy vs operational complexity   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Start with a monolith; earn your         │
│              │  microservices."                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Service Decomposition → API Gateway →     │
│              │ Service Discovery                         │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Architecture should reflect organisational structure (Conway's Law). The best architecture for a given team is the one that maps service boundaries to team boundaries. A monolith is correct when one team can own all of it; microservices are correct when independent teams need independent deployment pipelines. The architectural pattern is a consequence of the team structure, not the cause of it.

**Where else this pattern appears:**
- **Database design:** A single team owning all tables is fine with a monolithic schema. Multiple teams sharing a schema without ownership boundaries creates the shared database anti-pattern - the coupling problem is the same whether code is a monolith or microservices.
- **Deployment pipelines:** A monolith deploys as one unit, which is fine when all code is always in a consistent state. Multiple services need independent pipelines - which are overhead unless teams truly need to deploy on different cadences.
- **API contracts:** A monolith can use internal method calls with no contract. Microservices force all inter-domain communication to explicit API contracts, which is valuable only when different teams own the calling and called code and need to evolve independently.

---

### 💡 The Surprising Truth

The companies most associated with microservices success - Netflix, Amazon, Uber - all started with monoliths and migrated to microservices only after reaching scales where the monolith became the bottleneck. Netflix launched in 2007 as a Java monolith. Uber's early architecture was a Python monolith. Amazon's legendary two-pizza team structure emerged after years of operating as a monolith. The microservices architecture was not the reason these companies scaled - it was the result of scaling. Engineers who adopt microservices to scale before they have a scale problem are solving a future problem with a solution that creates present problems.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Architecture should reflect organisational structure (Conway's Law). The best architecture for a given team is the one that maps service boundaries to team boundaries. A monolith is correct when one team can own all of it; microservices are correct when independent teams need independent deployment pipelines. The architectural pattern is a consequence of the team structure, not the cause of it.

**Where else this pattern appears:**
- **Database design:** A single team owning all tables is fine with a monolithic schema. Multiple teams sharing a schema without ownership boundaries creates the shared database anti-pattern - the coupling problem is the same whether code is a monolith or microservices.
- **Deployment pipelines:** A monolith deploys as one unit, which is fine when all code is always in a consistent state. Multiple services need independent pipelines - which are overhead unless teams truly need to deploy on different cadences.
- **API contracts:** A monolith can use internal method calls with no contract. Microservices force all inter-domain communication to explicit API contracts, which is valuable only when different teams own the calling and called code and need to evolve independently.

---

### 💡 The Surprising Truth

The companies most associated with microservices success - Netflix, Amazon, Uber - all started with monoliths and migrated to microservices only after reaching scales where the monolith became the bottleneck. Netflix launched in 2007 as a Java monolith. Uber's early architecture was a Python monolith. Amazon's legendary two-pizza team structure emerged after years of operating as a monolith. The microservices architecture was not the reason these companies scaled - it was the result of scaling. Engineers who adopt microservices to scale before they have a scale problem are solving a future problem with a solution that creates present problems.
---

### 🧠 Think About This Before We Continue

**Q1.** Your startup has 8 engineers and is building a food-delivery app. A senior engineer proposes starting with microservices to "avoid technical debt." You have a monolith prototype that works. What are the concrete costs of adopting microservices at this stage, and what specific conditions in the future would make that switch worthwhile?

*Hint:* Think about what microservices concretely cost at 8 engineers: each service needs its own deployment pipeline, monitoring dashboards, health checks, service discovery registration, and on-call runbook. At 8 engineers, this overhead is borne by the same people writing features. Explore what specific conditions (independent scaling need, genuinely different deployment cadences, separate team ownership) would justify that overhead, and whether any of those conditions apply to a food-delivery startup at this stage.

*Hint:* Think about what microservices concretely cost at 8 engineers: each service needs its own deployment pipeline, monitoring dashboards, health checks, service discovery registration, and on-call runbook. At 8 engineers, this overhead is borne by the same people writing features. Explore what specific conditions (independent scaling need, genuinely different deployment cadences, separate team ownership) would justify that overhead, and whether any of those conditions apply to a food-delivery startup at this stage.

**Q2.** A company migrated from a monolith to 40 microservices two years ago. Deployments are now faster per service, but overall system reliability has dropped - they have more partial outages than before. Identify the distributed systems failure modes most likely responsible, and describe what architectural patterns would restore the reliability they had with the monolith.

*Hint:* Think about which distributed systems failure modes cause reliability regression that a monolith doesn't have: cascading failures (one slow service causes thread pool exhaustion in callers), network partition timeouts (previously fast in-process calls now have milliseconds of network latency and can fail), and deployment instability (40 services = 40x the deployment surface area). Explore which specific resilience patterns (circuit breakers for cascading failure, bulkheads for thread pool isolation, chaos engineering to find latent failure modes) address each root cause.

**Q3 (Design Trade-off):** Your team extracted 3 services from the monolith 6 months ago, only to discover the boundaries are wrong: the 3 services change together 80% of the time and cannot be deployed independently without careful sequencing. Designing a path forward: should you merge the 3 services back into one (closer to the original monolith), redraw boundaries and re-extract, or add an orchestration layer to manage the sequencing? What data would you gather before deciding, and how would you avoid the same mistake in the redraw?

*Hint:* Think about what "wrong boundaries" means technically: services that change together belong in the same service. Explore whether merging the 3 back into a correctly-bounded single service (still smaller than the original monolith) is simpler than adding orchestration to manage their sequencing. Consider what the correct decomposition looks like for these 3 domains and whether the error was decomposing by technical layer rather than by business capability.

*Hint:* Think about which distributed systems failure modes cause reliability regression that a monolith doesn't have: cascading failures (one slow service causes thread pool exhaustion in callers), network partition timeouts (previously fast in-process calls now have milliseconds of network latency and can fail), and deployment instability (40 services = 40x the deployment surface area). Explore which specific resilience patterns (circuit breakers for cascading failure, bulkheads for thread pool isolation, chaos engineering to find latent failure modes) address each root cause.

**Q3 (Design Trade-off):** Your team extracted 3 services from the monolith 6 months ago, only to discover the boundaries are wrong: the 3 services change together 80% of the time and cannot be deployed independently without careful sequencing. Designing a path forward: should you merge the 3 services back into one (closer to the original monolith), redraw boundaries and re-extract, or add an orchestration layer to manage the sequencing? What data would you gather before deciding, and how would you avoid the same mistake in the redraw?

*Hint:* Think about what "wrong boundaries" means technically: services that change together belong in the same service. Explore whether merging the 3 back into a correctly-bounded single service (still smaller than the original monolith) is simpler than adding orchestration to manage their sequencing. Consider what the correct decomposition looks like for these 3 domains and whether the error was decomposing by technical layer rather than by business capability.
