---
id: SYD-005
title: The System Design Ecosystem Map
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-001, SYD-003
used_by: SYD-043, SYD-044, SYD-045, SYD-046
related: SYD-001, SYD-003, SYD-004
tags:
  - architecture
  - foundational
  - mental-model
  - pattern
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /syd/the-system-design-ecosystem-map/
---

# SYD-005 - The System Design Ecosystem Map

⚡ TL;DR - A structured vocabulary map of every major system design concept, component, and pattern - the reference topology of the discipline.

| SYD-005         | Category: System Design                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | SYD-001, SYD-003                          |                 |
| **Used by:**    | SYD-043, SYD-044, SYD-045, SYD-046       |                 |
| **Related:**    | SYD-001, SYD-003, SYD-004                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You know system design concepts individually: load balancing, caching, sharding, message queues. But you do not know how they relate to each other. When should caching be chosen over sharding? When does a message queue replace a synchronous API? Which concepts address latency vs which address throughput? Without a map, you navigate a maze of interconnected concepts by trial and error.

**THE BREAKING POINT:**
System design has hundreds of concepts spanning networking, databases, caching, distribution, reliability, and infrastructure. Without a mental map of how these concepts cluster and relate, studying feels like memorising disconnected facts. Applying them in practice means reaching for whatever pattern you last learned rather than the right pattern for the problem.

**THE INVENTION MOMENT:**
As system design became a teachable discipline, educators noticed that students who built a mental map of the concept space before diving into details learned faster and retained more. The ecosystem map is the "domain ontology" of system design - the structured vocabulary that enables reasoning about problems before knowing every solution.

**EVOLUTION:**
Early system design education was component-by-component. Resources like the System Design Primer and Grokking the System Design Interview began organising concepts into categories. Modern system design teaching starts with the map, then drills into specifics.

---

### 📘 Textbook Definition

The **System Design Ecosystem Map** is a structured categorisation of all major system design concepts into domains: compute, network, storage, reliability, scalability, observability, security, and data patterns. Each domain contains the components and patterns that address its core concerns. The map reveals the relationships between concepts - how caching and database replication both address read scalability through different mechanisms, or how circuit breakers and rate limiting both address reliability through different layers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The map tells you which bucket every system design concept belongs to and which other concepts it relates to.

**One analogy:**
> A field guide to birds. Not every bird has been seen, but the guide organises birds by family, habitat, and behaviour. When you spot a new bird, you do not catalogue it from scratch - you find the right family, note the distinguishing features, and relate it to birds you already know. The ecosystem map does this for system design concepts.

**One insight:**
Knowing the map means you can look at any system design problem, identify which domains are relevant, and systematically retrieve the candidate patterns - instead of hoping you remember the right pattern from memory.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every system design problem is a combination of concerns from a small number of fixed domains.
2. Concepts within a domain address the same concern through different mechanisms.
3. Trade-offs between concepts within a domain can be compared; trade-offs across domains require weighing different concerns.
4. No real system uses only one domain - all production systems span at least compute, storage, networking, and reliability.

**DERIVED DESIGN:**
The map clusters concepts by the concern they address. This clustering is derived from system architecture theory: every system must handle requests (compute), store state (storage), communicate (networking), and remain available (reliability). Advanced systems additionally handle traffic shaping (scalability), visibility (observability), and threat surfaces (security).

**THE TRADE-OFFS:**
**Gain:** Structured vocabulary enables systematic pattern selection rather than ad-hoc recall.
**Cost:** The map is an abstraction - real systems have concepts that span multiple domains and resist clean categorisation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Systems genuinely have multiple orthogonal concerns that must be addressed simultaneously.
**Accidental:** Over-elaborate taxonomies that split concepts into too-fine categories create maintenance overhead without improving reasoning.

---

### 🧪 Thought Experiment

**SETUP:**
Two engineers receive the prompt: "Design a system that shows a personalised home feed to users."

**WHAT HAPPENS WITHOUT THE MAP:**
Engineer A draws a database and an API. They add caching when the interviewer hints at performance. They add a queue when prompts for scalability. Their design is reactive - driven by prompts, not by a systematic scan of the problem space. They miss: CDN for static content, read replicas for feed queries, async fan-out for write-heavy updates.

**WHAT HAPPENS WITH THE MAP:**
Engineer B mentally scans the ecosystem: Compute (load balancer, app servers), Storage (database for user graph, object storage for media, cache for pre-computed feeds), Networking (CDN for media delivery, API gateway for auth), Reliability (replicas, health checks), Scalability (fan-out strategy, write sharding). They build a checklist from the map and address each domain explicitly. The result is a more complete design arrived at proactively.

**THE INSIGHT:**
The map is a checklist for problem space coverage. The engineer who uses it systematically produces more complete designs than the engineer who relies on memory.

---

### 🧠 Mental Model / Analogy

> The ecosystem map is like the periodic table for system design. The periodic table groups elements by properties (alkali metals, halogens, noble gases). Each group behaves predictably in reactions. A chemist uses the table to predict reactions and choose elements for a target formula. The ecosystem map groups system design concepts by the concern they address. A system designer uses the map to predict which patterns apply and choose the right tool for a given requirement.

**Mapping:**
- Periodic table → ecosystem map
- Element groups → concept domains (storage, compute, etc.)
- Element properties → concept trade-offs (latency, consistency, cost)
- Chemical reaction → system interaction between components
- Target formula → desired system behaviour (availability, latency SLO)

Where this analogy breaks down: elements have fixed properties; system design components interact in ways that depend heavily on the specific implementation and configuration of each component.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
System design has a lot of pieces. The ecosystem map groups them like a shopping list: storage stuff, networking stuff, reliability stuff, performance stuff. When you are designing a system, you go through each group and ask "do I need anything from this shelf?"

**Level 2 - How to use it (junior developer):**
When approaching a design problem, scan each domain: Do I need distributed storage (database, object storage, distributed cache)? What networking components (LB, CDN, API gateway, service mesh)? What reliability mechanisms (replication, failover, circuit breaker)? What scalability patterns (horizontal scaling, partitioning, async processing)? The map ensures you do not forget an entire category.

**Level 3 - How it works (mid-level engineer):**
The map reveals the *orthogonality* of system design concerns. Latency and availability are often addressed by different mechanisms: caching reduces latency; replication increases availability. Throughput and consistency are fundamentally in tension: higher throughput often requires relaxed consistency. Understanding which domain each requirement lives in prevents you from trying to solve availability with caching (wrong tool, wrong domain).

**Level 4 - Why it was designed this way (senior/staff):**
At senior level, the map is used for *failure domain analysis*. Every component lives in a domain; every domain has characteristic failure modes. Compute fails by overload or crash. Storage fails by corruption or exhaustion. Networking fails by partition or congestion. Reliability mechanisms themselves fail when they add coordination overhead. A senior engineer uses the map to ensure each domain has an explicit failure mode and a mitigation strategy, and to identify which domain is the weakest link in the system's reliability chain.

**Expert Thinking Cues:**
- "Which domain contains my single point of failure?"
- "I have covered compute and storage - have I thought about data consistency patterns?"
- "What is the reliability mechanism for each domain component?"
- "Which domain's concerns conflict most in this design?"

---

### ⚙️ How It Works (Mechanism)

```
SYSTEM DESIGN ECOSYSTEM MAP
════════════════════════════

DOMAIN 1: COMPUTE
  App Servers · API Gateway
  Load Balancer · Auto Scaling
  Serverless Functions

DOMAIN 2: STORAGE
  Relational DB (SQL)
  Document DB (NoSQL)
  Key-Value Store (Redis)
  Object Storage (S3)
  Column Store (Cassandra)
  Search Engine (Elasticsearch)

DOMAIN 3: CACHING                  ← YOU ARE HERE
  CDN · Reverse Proxy Cache
  In-Process Cache (Guava)
  Distributed Cache (Redis)
  Database Query Cache

DOMAIN 4: NETWORKING
  DNS · CDN · API Gateway
  Service Mesh · gRPC · REST
  WebSocket · SSE · Long Poll

DOMAIN 5: ASYNC & MESSAGING
  Message Queue (RabbitMQ)
  Pub/Sub (Kafka, SNS)
  Event Sourcing
  Job Queue · Cron

DOMAIN 6: RELIABILITY
  Replication · Failover
  Circuit Breaker
  Bulkhead · Retry + Backoff
  Health Checks · Chaos Eng

DOMAIN 7: SCALABILITY
  Horizontal Scaling · Sharding
  Partitioning · Rate Limiting
  Read Replicas · Fan-out

DOMAIN 8: OBSERVABILITY
  Metrics (Prometheus)
  Logging (ELK Stack)
  Tracing (Jaeger, Zipkin)
  Alerting (PagerDuty)

DOMAIN 9: SECURITY
  Auth (OAuth2/JWT)
  Encryption (TLS, at-rest)
  DDoS Protection · WAF
  Secrets Management
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
User Request
    │
[SECURITY] Auth + TLS
    │
[NETWORKING] DNS + CDN
    │
[COMPUTE] Load Balancer
    │         ← YOU ARE HERE
[COMPUTE] App Server
    │
[CACHING] Redis Cache
    │
[STORAGE] Database
    │
[ASYNC] Event Queue
    │
[COMPUTE] Worker
    │
[OBSERVABILITY] Metrics
```

**FAILURE PATH:**
Database overloaded → caching layer absorbs reads (Domain 3 saves Domain 2). App server crashes → load balancer routes around it (Domain 1 absorbs Domain 1). DB primary fails → replication promotes replica (Domain 6 saves Domain 2). Message queue allows workers to fall behind without losing messages (Domain 5 decouples Domain 1 and workers).

**WHAT CHANGES AT SCALE:**
At scale, each domain's mechanism must be distributed. A single cache node becomes a cluster. A single queue becomes a partitioned log. Each domain's failure mode probability increases as more nodes mean more opportunities for failure in that node type.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Distributed systems require explicit coordination within each domain: distributed locking in storage, consensus protocols in reliability, partition strategies in scalability. Each domain must be designed with the assumption that multiple instances of each component will run simultaneously.

---

### 💻 Code Example

```yaml
# Architecture checklist derived from the ecosystem map
# For: Social Media Feed System

compute:
  load_balancer: nginx   # horizontal, health-checked
  app_servers: 3+        # stateless, auto-scaled
  api_gateway: Kong      # rate limiting, auth

storage:
  primary_db: PostgreSQL # user graph, post metadata
  object_storage: S3     # photos, videos
  search: Elasticsearch  # post search, autocomplete

caching:
  cdn: CloudFront        # static assets, media
  distributed: Redis     # pre-computed feeds (TTL 1h)
  session: Redis         # user sessions (TTL 24h)

networking:
  protocol: REST + WebSocket
  cdn_enabled: true

async:
  message_queue: Kafka   # feed fan-out events
  job_queue: Celery      # email, push notifications

reliability:
  db_replication: true        # 1 primary, 2 replicas
  circuit_breaker: Resilience4j
  health_checks: /health endpoint on all services

scalability:
  partitioning: user_id % N shards
  read_replicas: 2
  rate_limiting: 100 req/sec/user

observability:
  metrics: Prometheus + Grafana
  logging: ELK stack
  tracing: Jaeger

security:
  auth: OAuth2 + JWT
  transport: TLS 1.3
  secrets: HashiCorp Vault
```

**How to test / verify correctness:**
- Coverage test: verify each domain has at least one component specified
- Gap analysis: identify any hardcoded single points of failure (single DB, single cache node)
- Load test: verify load balancer, cache, and DB each behave as expected under target req/sec

---

### ⚖️ Comparison Table

| Domain | Primary Concern | Key Components | Core Trade-off |
|---|---|---|---|
| **Compute** | Processing requests | LB, App Servers, Serverless | Latency vs cost |
| **Storage** | Persisting state | SQL, NoSQL, Object Storage | Consistency vs availability |
| **Caching** | Reducing latency | CDN, Redis, in-process | Freshness vs speed |
| **Networking** | Communication | DNS, CDN, Service Mesh | Coupling vs performance |
| **Async** | Decoupling producers/consumers | Kafka, RabbitMQ, Job Queens | Durability vs throughput |
| **Reliability** | Surviving failure | Replication, Circuit Breakers | Cost vs resilience |
| **Scalability** | Growing under load | Sharding, Partitioning | Complexity vs scale |
| **Observability** | Seeing what is happening | Metrics, Logs, Traces | Cost vs visibility |
| **Security** | Protecting the system | Auth, TLS, WAF | Friction vs safety |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Caching and replication both improve read performance" | True, but they address different failure modes - caching reduces load; replication improves availability. They are complementary, not interchangeable. |
| "Reliability is just adding redundancy" | Reliability includes failure detection, failover orchestration, and recovery procedures. Redundancy without detection is not reliability. |
| "Security is a domain to add at the end" | Security constraints (auth, encryption) affect every other domain's design choices. It must be addressed from the start. |
| "Observability is optional" | Without observability, you cannot diagnose production failures. Unobservable systems cannot be operated reliably. |
| "Async messaging replaces synchronous APIs" | Async decouples producers and consumers; synchronous APIs provide immediate feedback. They serve different requirements. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Domain Blindspot**
**Symptom:** System performs well on paper but critical domain is unaddressed (e.g., no observability, no async for long operations).
**Root Cause:** Design reviewed against component knowledge, not against a systematic domain checklist.
**Diagnostic:**
```bash
# Check for observability blindspot
curl http://service/health     # health endpoint?
curl http://service/metrics    # metrics endpoint?
# Check for async blindspot
grep -r "Thread.sleep\|@Scheduled" src/  # busy waits?
```
**Fix:** Conduct domain-by-domain design review using the ecosystem map as a checklist.
**Prevention:** Mandatory domain coverage review as part of design doc approval.

**Mode 2: Wrong Domain Tool**
**Symptom:** Availability problem solved with additional caching; still available issues after cache is added.
**Root Cause:** Confused domain - availability is a reliability concern (replication), not a caching concern.
**Diagnostic:**
```bash
# Check if database is single point of failure
psql -c "SELECT count(*) FROM pg_stat_replication;"
# 0 = no replicas = availability risk
```
**Fix:** Identify the correct domain for the problem, then apply the domain-appropriate mechanism.
**Prevention:** Before adding any component, name which domain concern it addresses and verify that concern is what is actually failing.

**Mode 3: Cascading Domain Failures**
**Symptom:** A caching failure causes a storage failure that causes a compute failure.
**Root Cause:** Domains are coupled without failure isolation - no bulkheads between domains.
**Diagnostic:**
```bash
# Chaos test: kill Redis (caching domain)
docker stop redis-node
# Observe: does the app degrade or crash?
# If crash: missing circuit breaker between cache and DB
```
**Fix:** Add circuit breakers between domain boundaries; implement graceful degradation per domain.
**Prevention:** Each domain must have explicit failure mode documentation and a defined degradation behaviour.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-001 - What Is System Design]] - The discipline the map describes
- [[SYD-003 - How to Approach Any System Design Problem]] - How to use the map in practice

**Builds On This (learn these next):**
- [[SYD-006 - Vertical Scaling]] - First concept in the scalability domain
- [[SYD-008 - Load Balancing]] - First concept in the compute domain
- [[SYD-015 - SLA SLO SLI]] - First concept in the reliability domain

**Alternatives / Comparisons:**
- [[SYD-002 - The System Design Interview Mental Model]] - Procedural complement to this structural map
- [[SYD-062 - Trade-off Navigation Framework]] - Advanced cross-domain trade-off reasoning

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Structured vocabulary map   ║
║               of system design domains    ║
╠══════════════════════════════════════════╣
║ PROBLEM       Concepts known in           ║
║ IT SOLVES     isolation, not in relation  ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   Every system spans multiple ║
║               domains; every domain has   ║
║               characteristic trade-offs   ║
╠══════════════════════════════════════════╣
║ USE WHEN      Starting any design;        ║
║               reviewing completeness;     ║
║               finding the right pattern   ║
╠══════════════════════════════════════════╣
║ AVOID WHEN    Over-applying taxonomy to   ║
║               simple, single-domain tools ║
╠══════════════════════════════════════════╣
║ TRADE-OFF     Structure vs flexibility;   ║
║               completeness vs simplicity  ║
╠══════════════════════════════════════════╣
║ ONE-LINER     9 domains: compute, storage,║
║               cache, network, async,      ║
║               reliability, scale, obs,    ║
║               security                    ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-006: Vertical Scaling   ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Every production system spans at least: compute, storage, networking, and reliability domains.
2. Concepts within a domain address the same concern differently; concepts across domains address different concerns - do not substitute one for the other.
3. Use the map as a completeness checklist: scan each domain and ask "have I addressed this concern in my design?"

**Interview one-liner:**
"I organise system design concepts into nine domains - compute, storage, caching, networking, async, reliability, scalability, observability, and security - and use each domain as a completeness check for any design."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Organise your knowledge before applying it. Domain maps - taxonomies, ontologies, reference architectures - do not just describe knowledge; they make knowledge *retrieval* tractable. An engineer who knows 100 patterns but cannot organise them applies fewer than an engineer who knows 50 patterns structured around a clear domain map.

**Where else this pattern appears:**
- **OWASP Top 10:** A map of the security domain's most critical concerns - enables systematic security review of any application.
- **12-Factor App:** A map of the operations domain for cloud-native applications - enables systematic operability review.
- **TOGAF ADM:** An enterprise architecture framework that maps business, application, data, and technology domains.

---

### 💡 The Surprising Truth

The nine domains of the ecosystem map did not arise from academic theory - they emerged empirically from post-mortem analysis of production failures. Companies noted that failures clustered in the same categories: compute (overload, crash), storage (corruption, exhaustion), network (partition, congestion), reliability (cascade failure). The domains map directly to the distribution of real production failures. Studying them in this order is not arbitrary - it is calibrated to where real systems break most often.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A system has robust compute, storage, and caching domains but no observability domain. An incident occurs. Describe what the on-call engineer's experience looks like, and what specific evidence they lack.
*Hint:* Think about what a structured incident response needs (metrics, logs, traces) and what decisions cannot be made without each type of signal - look into mean time to detect vs mean time to recover.

**Q2 (Scale):** At 1M DAU, your system uses all nine domains. At 1B DAU, which domain becomes the most expensive to operate, and which becomes the most complex to design?
*Hint:* Think separately about operational cost (storage dominates at scale) and engineering complexity (cross-domain consistency and distributed reliability mechanisms) - explore how each domain's cost and complexity scales non-linearly.

**Q3 (Design Trade-off):** Two systems have identical functionality. System A has strong isolation between domains (separate databases, separate caches per service). System B has shared infrastructure (one Redis, one PostgreSQL). How do failure blast radii, operational costs, and query patterns differ between them?
*Hint:* Look into the microservices vs monolith database debate, shared-nothing architecture, and the trade-off between isolation blast radius and infrastructure overhead.
