---
id: SYD-001
title: System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on:
used_by: SYD-002, SYD-003, SYD-005, SYD-006, SYD-007
related: SYD-002, SYD-078, SYD-079
tags:
  - architecture
  - foundational
  - mental-model
  - distributed
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 1
permalink: /syd/system-design/
---

# SYD-001 - System Design

⚡ TL;DR - System design is the discipline of decomposing a
real-world requirement into components, data flows, and
trade-offs that a team can build, operate, and evolve.

| #001 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | None | |
| **Used by:** | Non-Functional Requirements, Availability, Latency vs Throughput, Vertical Scaling, Horizontal Scaling | |
| **Related:** | Non-Functional Requirements, System Design Interview Framework, System Design Interview Preparation Guide | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a startup that receives a simple requirement: "Build an
app where users can share photos." Two engineers write code for
two days and deploy a single Node.js server with a SQLite
database on one laptop. It works perfectly for the first 20
users. Then the company is featured in TechCrunch. 10,000 users
sign up. The single server buckles under CPU load. The database
file corrupts under concurrent writes. All photos are lost. The
engineers had no mental framework to anticipate any of this -
they just wrote features.

**THE BREAKING POINT:**
Without a deliberate approach to system architecture, teams
discover requirements they missed only when those requirements
cause production failures. Performance, reliability, scalability,
and security are invisible until they are violated - usually
at the worst possible moment.

**THE INVENTION MOMENT:**
This is exactly why system design was formalized as a discipline.
It is the practice of thinking through architectural decisions
BEFORE writing code - decomposing requirements into components,
anticipating failure modes, and making explicit trade-offs.

**EVOLUTION:**
Early systems (1960s-1980s) ran on mainframes - a single
machine handled everything. As the internet scaled in the
1990s-2000s, single-machine limits forced engineers to
distribute work across multiple servers. Google, Amazon, and
Facebook published architecture papers (MapReduce, Dynamo, TAO)
that crystallized distributed system design into transferable
patterns. Today, system design interviews and books like
"Designing Data-Intensive Applications" (Kleppmann) have made
these once-tribal patterns accessible to every engineer.

---

### 📘 Textbook Definition

System design is the process of defining the architecture,
components, modules, interfaces, data flows, and operational
properties of a system to satisfy specified functional and
non-functional requirements. It translates business requirements
into technical blueprints by making explicit decisions about
decomposition, communication protocols, data models,
scalability strategies, and failure handling - each decision
carrying trade-offs between cost, performance, reliability,
and development complexity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Break a big problem into components that can each be built,
scaled, and fixed independently.

**One analogy:**
> Designing a building before pouring concrete. The architect
> doesn't just start stacking bricks - they think about load
> distribution, exits, plumbing, electricity, and what happens
> if one wall fails. System design is the architecture
> blueprint before engineers write a single line of code.

**One insight:**
The purpose of system design is not to produce the perfect
system - it is to make trade-offs explicit. Every design choice
gains something and loses something. The engineer who cannot
articulate what they are giving up does not actually understand
their design.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every system has functional requirements (what it does)
   and non-functional requirements (how well it does it).
2. No single machine can serve unlimited load - distribution
   becomes necessary at some scale.
3. Distributed systems introduce failure modes that single-
   machine systems do not have (partial failure, network
   partition, clock skew).

**DERIVED DESIGN:**
Given that load must eventually be distributed and distributed
systems fail in partial ways, a well-designed system must:
- Decompose into independently scalable services or components
- Define clear boundaries (APIs, queues, databases) between
  components so one can fail without cascading to all others
- Choose consistency or availability for each data operation
  based on business requirements (CAP theorem trade-off)
- Build observability in from the start - if you can't measure
  it, you can't know when it breaks

**THE TRADE-OFFS:**
**Gain:** Systems that anticipate failure modes survive them;
systems that plan for scale can grow without rewrites.
**Cost:** Upfront design time, increased architecture
complexity, cognitive overhead for every team member.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Distributing state correctly across machines is
fundamentally hard. Consistency, ordering, and failure handling
cannot be wished away - they are properties of physics and
network behavior, not implementation choices.
**Accidental:** Much complexity comes from premature
optimization, choosing the wrong abstraction layer, or
over-engineering for scale that never comes. Most startups
don't need Kafka on day one.

---

### 🧪 Thought Experiment

**SETUP:**
A social media company wants to store 100 million user
profiles. Each profile has a name, bio, avatar URL, and a
follow-graph. They have one PostgreSQL server.

**WHAT HAPPENS WITHOUT SYSTEM DESIGN:**
The team adds features for 18 months. At 500k users, queries
slow down. At 2 million users, the database becomes the
bottleneck for every request. At 5 million users, the single
server runs out of memory. A DBA adds indexes, which
temporarily helps but increases write latency. At 10 million
users, a storage disk fails and 6 hours of data is lost because
backups were never configured. The company issues a public
apology. The engineering team rewrites the system under
pressure, during peak traffic, with no safety net.

**WHAT HAPPENS WITH SYSTEM DESIGN:**
Before building, the team defines: 100M users, 1000 reads/sec
per server, need 99.9% availability, lose at most 1 hour of
data on failure. This drives: read replicas for the profile
service, object storage for avatars, a graph database for the
follow-graph, and automated nightly backups from day one.
When load grows, the pre-designed sharding strategy is
activated rather than rewriting under pressure.

**THE INSIGHT:**
System design converts unknown unknowns into known trade-offs.
The exact numbers don't have to be right - the act of reasoning
about scale surfaces architectural decisions that would
otherwise be made by accident.

---

### 🧠 Mental Model / Analogy

> System design is urban planning for software. A city planner
> doesn't design individual buildings - they design roads,
> water systems, power grids, and zoning rules. Each building
> follows rules that make the city work as a whole. When a
> water main breaks, it doesn't take down the electricity.
> When traffic surges downtown, the road grid absorbs it
> without paralysing the entire city.

- "Roads" → APIs and message queues (how components communicate)
- "Buildings" → services/components (what does the work)
- "Water system" → databases and storage (persistent state)
- "Power grid" → compute and scaling infrastructure
- "Zoning rules" → contracts (SLAs, schemas, rate limits)
- "Traffic surge" → load spikes requiring auto-scaling
- "Emergency services" → monitoring, alerting, on-call rotation

**Where this analogy breaks down:**
Unlike cities, software can be deployed in minutes - but this
speed tempts engineers to skip the planning phase entirely,
which is how unmaintainable monoliths are born.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
System design is the process of planning how software will
be built before building it. Like an architect drawing
blueprints before construction begins.

**Level 2 - How to use it (junior developer):**
When given a requirement, think: what data needs to be stored?
How many users will use this? What happens if one server goes
down? Sketch the components (frontend, backend, database) and
how they connect. Identify the most likely bottleneck.

**Level 3 - How it works (mid-level engineer):**
System design requires explicit decisions on: data model
(SQL vs NoSQL, normalized vs denormalized), communication
(sync REST vs async messaging), consistency requirements
(strong vs eventual), and fault tolerance (what fails, how
often, what is the acceptable data loss). Each decision
produces a component diagram, a data flow, and a failure
mode analysis.

**Level 4 - Why it was designed this way (senior/staff):**
The architectural patterns that dominate today - microservices,
event sourcing, CQRS, saga, circuit breaker - each emerged to
solve a specific failure mode at scale. Understanding which
problem each pattern solves prevents cargo-culting: adopting
microservices without the deployment infrastructure to support
them, or using eventual consistency where the business requires
immediate consistency (financial transactions).

**Level 5 - Mastery (distinguished engineer):**
Expert system designers think in feedback loops: the system
produces data (metrics, logs) that informs the next design
iteration. They recognize that most systems are under-designed
(missed NFRs cause production incidents) and over-engineered
(premature optimization adds complexity with no payoff).
The master skill is knowing which requirements to invest in
now versus defer - a function of current user volume,
failure history, and business growth trajectory.

---

### ⚙️ How It Works (Mechanism)

System design proceeds through a structured sequence of
decisions, each building on the previous:

```
┌─────────────────────────────────────────┐
│     SYSTEM DESIGN PROCESS               │
├─────────────────────────────────────────┤
│  1. CLARIFY REQUIREMENTS                │
│     Functional: what the system does    │
│     Non-functional: how well it does it │
│     Constraints: budget, timeline, team │
├─────────────────────────────────────────┤
│  2. ESTIMATE SCALE                      │
│     Users: DAU / MAU                   │
│     Traffic: reads/writes per second    │
│     Data: storage volume, growth rate   │
├─────────────────────────────────────────┤
│  3. HIGH-LEVEL DESIGN                   │
│     Components: what services exist     │
│     Data flow: how data moves           │
│     Data model: tables, documents, keys │
├─────────────────────────────────────────┤
│  4. DEEP DIVE CRITICAL COMPONENTS       │
│     Bottleneck identification           │
│     Scaling strategy (H/V scale)        │
│     Failure mode analysis               │
├─────────────────────────────────────────┤
│  5. OPERATIONAL DESIGN                  │
│     Monitoring: what to measure         │
│     Deployment: how to ship safely      │
│     Incident: how to diagnose failures  │
└─────────────────────────────────────────┘
```

**Step 1 - Clarify Requirements:**
Every system has two layers. Functional requirements define
WHAT the system does: "users can post photos", "search returns
results in < 200ms". Non-functional requirements define HOW
WELL it does it: "99.99% availability", "handles 1M concurrent
users", "data cannot be lost". The NFRs drive architectural
decisions far more than the functional requirements.

**Step 2 - Estimate Scale:**
Back-of-envelope math converts vague requirements into
concrete numbers. "1 billion users" means: 10M daily active,
500 requests/user/day, 5B requests/day, ~60K requests/second
peak. These numbers determine whether one server, ten servers,
or a distributed cluster is needed.

**Step 3 - High-Level Design:**
Sketch the major components and their connections. This is not
code - it is boxes and arrows. Focus on data flow: where does
data enter, how does it transform, where is it stored, how
is it served back to users.

**Step 4 - Deep Dive:**
Identify the component most likely to fail under load - the
bottleneck. For read-heavy systems, this is usually the
database. For write-heavy systems, it is often the queue or
ingestion layer. Apply the appropriate scaling pattern.

**Step 5 - Operational Design:**
A system that cannot be observed cannot be operated. Define
what metrics matter, what logs to produce, and what alerts
indicate failure. This is not an afterthought - it is a
design requirement.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Business Requirement]
    → [NFR Extraction]
    → [Scale Estimation]
    → [Component Design ← YOU ARE HERE]
    → [Data Model]
    → [Failure Mode Analysis]
    → [Operational Design]
    → [Implementable Blueprint]
```

**FAILURE PATH:**
Design skips NFR extraction → bottleneck found in production
→ emergency rewrite under load → data loss risk → incident

**WHAT CHANGES AT SCALE:**
At 10x scale, single-server designs break at the database
layer first. At 100x, the application tier requires horizontal
scaling and statelessness becomes mandatory. At 1000x, data
locality and geo-distribution become dominant concerns.

---

### 💻 Code Example

System design itself is not code - it is an architectural
process. However, good system design produces clear API
contracts. Below is an example of how a design decision
becomes an API boundary.

**Example 1 - BAD: No separation of concerns**
```python
# BAD: One function handles auth, business logic,
# DB write, and notification - impossible to scale
# or test independently
def post_photo(user_id, photo_bytes, caption):
    if not db.query("SELECT id FROM users WHERE id=?",
                    user_id):
        return 401
    img_url = compress_and_store(photo_bytes)
    photo_id = db.insert("photos", {
        "user_id": user_id,
        "url": img_url,
        "caption": caption
    })
    send_notification_to_followers(user_id, photo_id)
    return photo_id
```

**Example 2 - GOOD: Concerns separated by design**
```python
# GOOD: Each concern is a separate service.
# Auth service → Photo service → Notification queue.
# Each scales independently.

# Photo Service - receives pre-authenticated request
def post_photo(user_id: int,
               photo_url: str,  # pre-uploaded to object store
               caption: str) -> PhotoResponse:
    photo = photo_repo.create(user_id, photo_url, caption)
    # Publish event - notification service consumes async
    event_bus.publish("photo.created", {
        "photo_id": photo.id,
        "user_id": user_id
    })
    return PhotoResponse(photo_id=photo.id)
```

The design decision (separate services, async notification)
is visible in the code structure. This is what good system
design produces - architecture that guides implementation.

---

### ⚖️ Comparison Table

| Approach | Design Time | Runtime Surprise | Refactor Cost | Best For |
|---|---|---|---|---|
| **System Design First** | Days-weeks | Low | Low | Production systems |
| Ad-hoc coding | Hours | Very High | Very High | Throwaway prototypes |
| Framework defaults | Low | Medium | Medium | Standard CRUD apps |
| Architecture committee | Weeks-months | Very Low | Very Low | Critical infrastructure |

**How to choose:**
Apply system design proportionally to expected lifetime and
scale. A one-day hackathon prototype needs no formal design.
A system serving 1M users after 12 months needs deliberate
NFR analysis before the first line is written.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| System design is about choosing a tech stack | It is about choosing architectural properties (consistency level, scaling strategy, failure tolerance) - the tech stack is secondary |
| More complexity = better design | Complexity has cost: maintenance, debugging, onboarding. The best design is the simplest one that meets all NFRs |
| System design ends at deployment | Systems evolve. Design is an ongoing conversation between observed production behavior and architectural decisions |
| Only big companies need system design | Every system eventually hits a scale it was not designed for. The question is when, not if |
| You need to get the design perfect before coding | Designs are living documents. Iterative refinement based on production data is the norm, not the exception |

---

### 🚨 Failure Modes & Diagnosis

**Skipped NFR Analysis**

**Symptom:**
System degrades under load in ways no one anticipated.
Metrics that were never defined spike on dashboards that
were never built. On-call engineers have no playbook.

**Root Cause:**
The team only defined what the system does (functional
requirements) but not how well it must do it. Availability,
latency, and throughput requirements were never specified,
so no architectural decisions were made to satisfy them.

**Diagnostic Command:**
```bash
# After an incident, check if NFRs were ever defined:
# Look for SLO definitions in the runbook/docs
grep -r "availability\|SLO\|uptime\|latency" docs/ runbooks/

# Check if monitoring captures the right signals
curl https://metrics.internal/api/v1/query?query=\
  http_request_duration_seconds_p99
```

**Fix:**
Document NFRs retroactively from production data. Use
observed p99 latency as the SLO baseline. Add alerting
on the metrics that caused the incident.

**Prevention:**
Add "NFR Document" as a required deliverable before any
new service enters design review.

---

**Premature Optimization (Over-Engineering)**

**Symptom:**
The team spends 3 months building distributed infrastructure
for a system that currently has 100 users. The additional
complexity slows feature development by 40%.

**Root Cause:**
Scale assumptions were made without data. Engineers
optimized for a scale they imagined, not the scale they
measured. A distributed message queue was added "for when
we scale" before a single scale problem was observed.

**Diagnostic Command:**
```bash
# Check current actual load vs designed capacity
# If actual << designed, the system is over-engineered
kubectl top pods -n production
# Compare with what the system was designed to handle
cat infra/capacity-design.md
```

**Fix:**
Delete the distributed infrastructure. Replace with the
simplest thing that works at current scale. Add a ticket
to revisit when actual usage reaches 70% of capacity.

**Prevention:**
Require scale estimates to be grounded in measured data,
not projections. Defer distributed infrastructure until
a single-server architecture shows signs of strain.

---

**Missing Failure Mode Analysis**

**Symptom:**
One downstream dependency goes down and takes the entire
system with it. Cascading failure that a circuit breaker
or bulkhead would have contained.

**Root Cause:**
The system was designed assuming all dependencies are
available. No thought was given to what happens when
a database, external API, or cache is unreachable.

**Diagnostic Command:**
```bash
# Check if any circuit breaker is configured
grep -r "circuitBreaker\|hystrix\|resilience4j" src/

# Simulate dependency failure in staging
docker-compose stop postgres
# Observe: does the entire app crash, or does it
# degrade gracefully?
```

**Fix:**
Add circuit breakers at every external dependency call.
Define degraded behavior: "if recommendations service is
down, serve most popular items as fallback."

**Prevention:**
Require a failure mode analysis document for every
external dependency in the system design phase.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Non-Functional Requirements` - the inputs that drive every architectural decision
- `Availability` - the most commonly missed NFR before systems hit production

**Builds On This (learn these next):**
- `Vertical Scaling` - first scaling lever when a system grows
- `Horizontal Scaling` - the second scaling lever and its trade-offs
- `Load Balancing` - required once horizontal scaling is applied

**Alternatives / Comparisons:**
- `System Design Interview Framework` - structured approach for interview context
- `Software Architecture Patterns` - the pattern catalog that implements system design decisions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Blueprint for how components, data, and  │
│              │ trade-offs combine into a working system  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Systems built without design fail under  │
│ SOLVES       │ load in ways that are expensive to fix   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ NFRs (availability, latency, throughput) │
│              │ drive architecture more than features do  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any system expected to serve real users   │
│              │ or evolve beyond a 1-person prototype     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Throwaway prototypes, 24-hour hackathons, │
│              │ scripts with 1-day lifecycles             │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Designing for imagined scale without any  │
│              │ measured baseline (premature optimization) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Upfront clarity vs time-to-first-commit   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Design is the art of making trade-offs   │
│              │  before the system makes them for you."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ NFRs → Availability → Load Balancing      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. NFRs (availability, latency, throughput) determine
   architecture more than features do.
2. The best design is the simplest one that meets all NFRs -
   complexity has a real cost.
3. Systems always grow beyond their original design. The goal
   is to design for the next 2 years, not the next 20.

**Interview one-liner:**
"System design is the practice of making architectural
trade-offs explicit before building - defining what the
system must do, how well it must do it, and how it fails
gracefully when components break."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Requirements exist at two levels: functional (what it does)
and non-functional (how well it does it). This distinction
applies everywhere - a car's functional requirement is to
transport people; its NFRs are fuel efficiency, safety
rating, and reliability. Engineers who only think about
features consistently miss the NFRs that cause failures.

**Where else this pattern appears:**
- **Database schema design** - defining the schema is the
  design phase; adding indexes later is the optimization
  phase. Skipping schema design produces unmigrateable tables.
- **API design** - defining the contract before implementation
  enables parallel work and prevents breaking changes.
- **Team organization** - Conway's Law means system design
  and team design are inseparable. The architecture mirrors
  the communication structure of the team that builds it.

**Industry applications:**
- **Finance** - payment systems require upfront design of
  idempotency, atomicity, and audit trails. Retrofitting
  these into a running payment system is extremely costly.
- **Healthcare** - patient data systems require HIPAA
  compliance by design; adding encryption and access control
  after launch means rewriting every data access path.

---

### 💡 The Surprising Truth

The biggest architecture mistakes in industry history were
not caused by engineers who didn't know better - they were
caused by successful systems that outgrew their original
design. Twitter's "fail whale" era (2008-2010) was not a
failure of engineering talent; it was a success failure:
the system grew 10x faster than any design assumption
predicted. The lesson is not that you must design for
infinite scale. It is that the cost of redesigning a
running system under production load is 10-100x the cost
of getting the next growth horizon right before hitting it.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Describe to a non-engineer why a feature-only
   approach causes production failures, using a specific
   example of which NFR was missed and what it cost.
2. [DEBUG] Given a production incident description, identify
   which NFR was not met and what architectural decision
   (or absence of one) caused it.
3. [DECIDE] In a 45-minute design session, produce a complete
   high-level design for a URL shortener: components,
   data model, scale estimate, and top failure mode.
4. [BUILD] Document the NFRs for a system you currently
   work on. Identify any that are missing or unmeasured.
5. [EXTEND] Apply the system design process to a non-software
   domain (a physical supply chain, a hospital workflow)
   and identify the analogous trade-offs.

---

### 🧠 Think About This Before We Continue

**Q1.** A startup has built a social app with 50,000 daily
active users. The founding engineer says: "We don't need
system design - we'll scale when we need to." The company
gets Series A funding and user growth is projected to hit
5 million DAU within 12 months. What are the three most
critical architectural decisions they must make NOW, before
growth hits, and why does the order matter?

*Hint: Think about what breaks at 100x scale that is cheap
to fix at 1x but expensive at 100x. Consider the data model,
session storage, and database write path specifically.*

**Q2.** Two engineers design the same photo-sharing system.
Engineer A uses microservices with Kubernetes, Kafka, and
Redis. Engineer B uses a monolith with PostgreSQL. The
system needs to serve 10,000 users at launch. At what
user count does Engineer A's design become an advantage
rather than a liability, and what specific operational
capability creates that transition point?

*Hint: Think about the operational overhead of Kubernetes
at small scale (deployment complexity, debugging distributed
traces) versus at large scale (independent scaling, fault
isolation). The transition is not about user count alone.*

**Q3 (Hands-On):** Take any system you use daily (a search
engine, a ride-sharing app, an email client). Without
Googling, sketch a high-level component diagram with at
least 5 components. Identify: (a) the most likely single
point of failure, (b) the component that limits write
throughput, and (c) the NFR that is hardest to satisfy.
What does your sketch tell you about the trade-offs the
original designers made?

*Hint: Start with the user request and trace every hop
until data is returned. Each hop is a component. SPOF is
where one failure takes down the user experience entirely.*

---

### 🎯 Interview Deep-Dive

**Q1: Walk me through how you would approach designing a
system you have never built before.**
*Why they ask:* Tests whether the candidate has a
systematic process or just improvises. Most weak candidates
jump to technology choices immediately.
*Strong answer includes:*
- Start with clarifying functional requirements (what the
  system must do) and non-functional requirements (scale,
  latency, availability, durability)
- Produce a back-of-envelope estimate to size the problem
  before choosing components
- Sketch high-level components first, then drill into the
  bottleneck component in depth
- Explicitly state trade-offs made at each decision point

**Q2: Your team's monolithic application is experiencing
performance degradation at 500k daily users. Product
wants to keep shipping features. How do you approach the
architectural decision of whether to refactor or rebuild?**
*Why they ask:* Tests judgment under constraint - the
candidate must balance engineering idealism with product
reality.
*Strong answer includes:*
- Profile the system to identify the actual bottleneck
  (usually database or specific service) before deciding
- Apply the Strangler Fig pattern: extract the bottleneck
  component as a service first, not everything at once
- Cost of incremental extraction vs full rewrite:
  rewrites have a 70%+ abandonment rate; incremental
  wins more often
- Define the "done" state before starting: what metric
  proves the refactor succeeded?

**Q3: How do you ensure a system design accounts for
requirements that haven't been stated yet?**
*Why they ask:* Tests senior-level thinking about implicit
requirements and future-proofing without over-engineering.
*Strong answer includes:*
- Extract implicit NFRs from the business context: a
  payment system implicitly requires idempotency and
  audit trails even if the brief doesn't mention them
- Build observability in from day one - metrics and logs
  make unknown requirements visible when they emerge
  in production
- Design component boundaries to minimize blast radius:
  even if the internal design changes, stable API
  contracts protect the rest of the system
- Use Architecture Decision Records (ADRs) to document
  what was deferred and why - this surfaces when the
  deferral becomes a liability
