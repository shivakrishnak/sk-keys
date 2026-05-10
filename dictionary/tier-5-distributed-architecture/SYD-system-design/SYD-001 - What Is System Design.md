---
id: SYD-001
title: What Is System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on:
used_by: SYD-015, SYD-035, SYD-016, SYD-017
related: SYD-015, SYD-017
tags:
  - architecture
  - foundational
  - mental-model
  - first-principles
status: complete
version: 2
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 1
permalink: /syd/what-is-system-design/
---

# SYD-001 - What Is System Design

⚡ TL;DR - System design is the process of defining how software components work together to meet functional and non-functional requirements at scale.

| SYD-001         | Category: System Design   | Difficulty: ★☆☆ |
| :-------------- | :------------------------ | :-------------- |
| **Depends on:** |                           |                 |
| **Used by:**    | SYD-015, SYD-035, SYD-016 |                 |
| **Related:**    | SYD-015, SYD-017          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You write code that works on your laptop. Then 10 users join. It slows down. 100 users - it crashes. 10,000 users - it is unreachable. Nobody told you there was a discipline for thinking about this kind of problem before you build.

**THE BREAKING POINT:**
Any individual piece of code can be correct and still be wrong at scale. A function that returns in 1ms when called once may take 10 seconds when called by 50,000 threads simultaneously. Code correctness is necessary but not sufficient for building real systems.

**THE INVENTION MOMENT:**
Engineers at early internet companies discovered that building systems others had never built forced them to think ahead. How will this database handle 1 million rows? What happens when one server fails? How do writes and reads stay consistent across data centres? These repeated questions crystallised into a discipline - System Design.

**EVOLUTION:**
System design began as informal lore passed between senior engineers. The 2000s brought Google's Bigtable, MapReduce, Chubby - papers that documented solved hard problems. The 2010s turned it into a structured interview skill. Today system design is a first-class engineering discipline with its own vocabulary, patterns, and trade-off frameworks.

---

### 📘 Textbook Definition

**System design** is the process of defining the architecture, components, modules, interfaces, and data flows of a system so it satisfies a given set of functional requirements (what the system does) and non-functional requirements (how well it does it - availability, latency, throughput, consistency, fault tolerance). It operates above the code level: it is about what to build and how to connect the parts, not the implementation details of each part.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
System design asks: "Given these requirements, what components, connections, and trade-offs create the right system?"

**One analogy:**
> Designing a city, not a building. A building is a single program. A city is many buildings with roads (networks), utilities (databases), emergency services (failover), and zoning rules (architecture constraints) - all of which must work together, grow over time, and keep functioning when pieces fail.

**One insight:**
Every system design decision is a trade-off. There is no perfect design - only designs that are right or wrong for a given requirement set and constraint set.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every system has finite resources - CPU, memory, disk, bandwidth, money.
2. Every system has requests that must be processed within acceptable output constraints.
3. Components fail - hardware faults, software bugs, and network partitions are guaranteed over time.
4. Requirements change - a design that ignores future growth poisons the upgrade path.
5. Consistency, availability, and partition tolerance cannot all be maximised simultaneously.

**DERIVED DESIGN:**
From these invariants, system design derives: (1) how to distribute load so resources are not exhausted, (2) how to replicate data so single failures do not cause data loss, (3) how to draw boundaries around components so they can be changed independently, (4) how to make the system observable so failure is detectable.

**THE TRADE-OFFS:**
**Gain:** A designed system is predictable, operable, and scalable within known parameters.
**Cost:** Design requires upfront thought, may introduce coordination overhead, and can over-engineer simple problems.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The real complexity of distributing computation, maintaining consistency under network partitions, and handling failure. This cannot be eliminated.
**Accidental:** Poorly chosen technologies, premature abstractions, over-engineering for scale that never arrives. Good system design minimises this.

---

### 🧪 Thought Experiment

**SETUP:**
You build a note-taking app. It works perfectly. Then a viral post sends 1 million users to your site in one hour.

**WHAT HAPPENS WITHOUT SYSTEM DESIGN:**
The single database server CPU maxes out at 100 concurrent users. Writes queue. Reads timeout. The app returns errors. You had not designed for load - no caching, no read replicas, no connection pool limits, no queue to absorb spikes.

**WHAT HAPPENS WITH SYSTEM DESIGN:**
Before building, you asked: What are the read/write ratios? What is the peak load estimate? What does failure look like? You added a cache for read-heavy note viewing. You added a message queue for async write processing. You deployed multiple app servers behind a load balancer. When the spike hits, cache absorbs 90% of reads and the queue buffers writes.

**THE INSIGHT:**
System design is pre-emptive failure engineering. Its value is invisible when things go right and catastrophic when it is absent.

---

### 🧠 Mental Model / Analogy

> System design is like designing a factory assembly line. You know what goes in (raw materials / user requests) and what comes out (finished product / HTTP responses). The design determines: how many workers (servers), how big the storage room (database), how to handle breakdowns (failover), and how fast the conveyor belt can move (throughput).

**Mapping:**
- Raw materials → user requests
- Workers → application servers
- Storage room → database and storage layer
- Conveyor belt → network and message queues
- Factory manager → load balancer and orchestrator
- Warehouse → cache layer

Where this analogy breaks down: factories produce identical items at predictable rates; software systems handle unpredictable bursts of highly varied requests with complex interdependencies.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
System design is figuring out how to build something big enough for lots of people to use at the same time without it falling over. Like designing a bridge - you do not just build it and hope. You plan how heavy it needs to be, how many cars can cross at once, and what happens in a storm.

**Level 2 - How to use it (junior developer):**
When starting a new feature or a new service, system design means answering: What data does this need to store and how will it grow? How many requests per second will hit this endpoint? What other services does this call, and what happens if they are slow or down? These questions shape your database choice, API design, caching strategy, and error handling.

**Level 3 - How it works (mid-level engineer):**
System design is applied constraints satisfaction. You receive functional requirements (user can post a photo, friends can view it) and non-functional requirements (99.9% uptime, <300ms latency, 10M users). You decompose into components: upload service, storage service, CDN, feed aggregation service, notification service. You model data flows, identify bottlenecks, apply appropriate patterns, and document trade-offs.

**Level 4 - Why it was designed this way (senior/staff):**
System design is the art of managing complexity through abstraction boundaries, failure domains, and explicit trade-offs. Senior designers think in terms of: What are the failure modes and how does failure propagate? What SLO am I committing to and which architectural decisions are load-bearing for that commitment? How does this design evolve as the team grows from 5 to 50 engineers? Which decision here is hardest to undo in 12 months?

**Expert Thinking Cues:**
- "What is the read/write ratio, and does it change over time?"
- "Where is the single point of failure, and is that acceptable?"
- "What does this look like at 10x current scale?"
- "Which decision here is hardest to undo in 12 months?"

---

### ⚙️ How It Works (Mechanism)

A system design process translates requirements into a blueprint:

```
Requirements
  │
  ├── Functional: What the system does
  │     (user login, upload photo, send email)
  │
  └── Non-functional: How well it does it
        (latency, availability, durability, scale)
          │
          ▼
  Capacity Estimation
  (requests/sec, data volume, storage growth)
          │
          ▼
  Component Decomposition
  (services, databases, caches, queues, CDNs)
          │
          ▼
  Data Flow Design
  (how data moves between components)
          │
          ▼
  Trade-off Analysis
  (consistency vs availability,
   latency vs cost)
          │
          ▼
  Architecture Diagram  ← YOU ARE HERE
  (the deliverable)
```

**System design considers three layers simultaneously:**

| Layer | Questions |
|---|---|
| **Compute** | How many servers? How to distribute load? |
| **Storage** | What database type? How to partition? Replication? |
| **Network** | How do components talk? Sync or async? |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client Request
    │
    ▼
DNS Resolution
    │
    ▼
Load Balancer  ← YOU ARE HERE
    │
    ├─── App Server 1
    ├─── App Server 2
    └─── App Server 3
              │
    ┌─────────┴──────────┐
    ▼                    ▼
 Cache              Database
 (Redis)            (Primary)
                        │
                   DB Replica
                   (Read replica)
```

**FAILURE PATH:**
A single app server crashes. The load balancer detects the failure via health check and stops routing to that server. Other servers absorb traffic. Auto-scaling adds a new server. If the database primary fails, the replica is promoted. There is brief write downtime during promotion.

**WHAT CHANGES AT SCALE:**
At 10x scale, cache hit ratio becomes critical - each cache miss hits the database. Connection pooling becomes necessary. The load balancer itself becomes a bottleneck. Monitoring gaps acceptable at low scale become incident sources.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Every component that holds state becomes a contention point under concurrent access. System design explicitly locates these contention points and applies solutions: optimistic locking, consistent hashing, partitioning - each with its own trade-off profile.

---

### 💻 Code Example

System design is not expressed in a single file, but the decisions it produces govern code structure:

```java
// BAD: No system design thinking - monolithic, brittle
@RestController
public class UserController {

    @Autowired
    private JdbcTemplate db;

    @GetMapping("/user/{id}")
    public User getUser(@PathVariable Long id) {
        // Direct DB call on every request - no caching
        // Blocks thread waiting for DB - no async
        // Single point of failure - no fallback
        return db.queryForObject(
            "SELECT * FROM users WHERE id = ?",
            new Object[]{id}, User.class);
    }
}
```

```java
// GOOD: System design applied - layered with resilience
@RestController
public class UserController {
    @Autowired private UserService userService;

    @GetMapping("/user/{id}")
    public Mono<User> getUser(@PathVariable Long id) {
        // Non-blocking; service layer handles cache+fallback
        return userService.getUser(id);
    }
}

@Service
public class UserService {
    @Autowired private UserRepository repo;
    @Autowired private RedisTemplate<Long, User> cache;

    public Mono<User> getUser(Long id) {
        // Cache-aside pattern (system design decision)
        User cached = cache.opsForValue().get(id);
        if (cached != null) return Mono.just(cached);

        return repo.findById(id)
            .doOnNext(u -> cache.opsForValue()
                .set(id, u, Duration.ofMinutes(10)))
            .switchIfEmpty(Mono.error(
                new UserNotFoundException(id)));
    }
}
```

**How to test / verify correctness:**
- Load test with k6: confirm cache hit rate > 80% at steady state
- Chaos test: kill one app server; verify traffic re-routes within 30 seconds
- Measure DB connection count under peak - confirm it stays below pool limit

---

### ⚖️ Comparison Table

| Approach | Scale Ceiling | Complexity | Build Time | Failure Recovery |
|---|---|---|---|---|
| **Monolith, single DB** | ~1K req/s | Low | Fast | Manual, slow |
| **Monolith + cache + LB** | ~10K req/s | Medium | Medium | Semi-automatic |
| **Microservices + distributed DB** | ~1M req/s | High | Slow | Automatic if designed |
| **Hyperscale with custom sharding** | Unlimited | Very High | Very Slow | Automatic + runbooks |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "System design is only for big companies" | Every system serving users has non-functional requirements. The scale differs, not the discipline. |
| "You design once, then build" | Design is iterative. You design, discover assumptions are wrong, redesign, build incrementally. |
| "More components always means better design" | Complexity is a liability. Add components only when they solve a concrete, measured problem. |
| "System design is about choosing tech stacks" | Tech choices are downstream decisions. Architecture comes first. |
| "A perfect design exists" | Every design optimises for certain constraints and sacrifices others. There is no universal optimum. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Design for Today, Break Tomorrow**
**Symptom:** System works at launch but degrades sharply at 5x growth with no clear upgrade path.
**Root Cause:** Designed for current load without explicit scale assumptions.
**Diagnostic:**
```bash
# Find slow queries signalling growth pressure
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 12345;
# Check table size growth rate
SELECT pg_size_pretty(pg_total_relation_size('orders'));
```
**Fix:** Identify and instrument bottleneck components. Add read replicas and caching iteratively.
**Prevention:** During design, write down scale assumptions explicitly.

**Mode 2: Over-Engineering for Scale That Never Comes**
**Symptom:** System is slow to build, hard to debug, and most added complexity is never exercised.
**Root Cause:** Designing for 10M users when the product has 500 users and unvalidated product-market fit.
**Diagnostic:**
```bash
# Measure actual traffic - is the complex infra even used?
grep "requests" /var/log/nginx/access.log | wc -l
```
**Fix:** Strip back to the simplest architecture handling current load plus next 12 months.
**Prevention:** Design in explicit stages with clear trigger conditions for each upgrade.

**Mode 3: Missing Non-Functional Requirements**
**Symptom:** System is functionally correct but cannot be operated - no monitoring, mystery outages.
**Root Cause:** Design only covered functional requirements. NFRs were not specified.
**Diagnostic:**
```bash
# Check if basic health endpoints exist
curl -f http://service/health || echo "No health endpoint"
# Check if metrics are exported
curl http://service/metrics | grep -c "http_requests_total"
```
**Fix:** Retrofit observability: structured logging, metrics, distributed tracing, health endpoints.
**Prevention:** Non-functional requirements checklist at design phase start.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-016 - Estimation and Back-of-Envelope Thinking]] - You need to estimate before you can design
- [[DST-001 - Distributed Systems Foundations]] - System design is usually distributed system design

**Builds On This (learn these next):**
- [[SYD-015 - The System Design Interview Mental Model]] - How to structure a design session
- [[SYD-035 - How to Approach Any System Design Problem]] - Step-by-step methodology
- [[SYD-017 - The System Design Ecosystem Map]] - The full vocabulary map

**Alternatives / Comparisons:**
- [[SYD-011 - Horizontal Scaling]] - One of the core design decisions
- [[SYD-018 - Load Balancing]] - Core mechanism for distributing load

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Discipline of designing     ║
║               systems at scale            ║
╠══════════════════════════════════════════╣
║ PROBLEM       Code correctness does not   ║
║ IT SOLVES     equal system correctness    ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   Every design is a trade-off ║
║               optimised for a context     ║
╠══════════════════════════════════════════╣
║ USE WHEN      Building systems that must  ║
║               scale, survive failure,     ║
║               or serve multiple teams     ║
╠══════════════════════════════════════════╣
║ AVOID WHEN    Prototype or internal tool  ║
║               with minimal users          ║
╠══════════════════════════════════════════╣
║ TRADE-OFF     Robustness vs complexity;   ║
║               future-proof vs over-built  ║
╠══════════════════════════════════════════╣
║ ONE-LINER     Define components, flows,   ║
║               and trade-offs before code  ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-035: Design approach    ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. System design separates *what to build* from *how to code it* - it operates at the architecture level.
2. Non-functional requirements (latency, availability, scale) are as important as functional ones.
3. Every design decision is a trade-off - explicitly name what you are gaining and sacrificing.

**Interview one-liner:**
"System design is the process of defining architecture, components, and trade-offs so a system meets both functional and non-functional requirements at the required scale."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Define constraints before solutions. You cannot design the right system without knowing what "right" means for this context. Constraints make good decisions possible and prevent scope creep.

**Where else this pattern appears:**
- **Database schema design:** Define access patterns before choosing schema - otherwise you optimise for writing, not reading.
- **API design:** Define consumer needs before defining endpoints - API-first design prevents retrofitting.
- **Infrastructure sizing:** Define traffic profiles before choosing instance types - prevents both under- and over-provisioning.

---

### 💡 The Surprising Truth

Most system design failures are not caused by wrong technology choices - they are caused by implicit, unwritten assumptions. A team that assumes their database can handle 10,000 connections when the actual limit is 100 will build a catastrophically wrong system while writing perfectly correct code. The most dangerous phrase in system design is "it should be fine" without a number attached.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** If computing resources were infinite and free, what would system design still need to solve?
*Hint:* Think about what constraints remain even when cost and capacity disappear - consider consistency, coordination, and failure modes in a world with unlimited servers.

**Q2 (Scale):** A social network adds a "react to post" feature. The feature works fine in development. At 10M users it unexpectedly causes the "view post" feature to become slow. Why might two seemingly unrelated features interact at scale?
*Hint:* Look into shared resources and hot paths - what database tables or cache keys are accessed by both features and how contention manifests.

**Q3 (Design Trade-off):** You must choose between a design requiring 2 weeks to build that handles 10x current load, and one requiring 6 weeks that handles 1000x load. The product has not yet found product-market fit. How do you decide?
*Hint:* Explore the concept of reversibility and the cost of not shipping vs the cost of a future redesign - look into evolutionary architecture and the YAGNI principle.
