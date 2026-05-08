---
id: DST-077
title: Distribution Necessity Assessment
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - dst
  - advanced
  - mental-model
  - bestpractice
status: draft
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 77
permalink: /dst/distribution-necessity-assessment/
---

# DST-077 - Distribution Necessity Assessment

⚡ TL;DR - Distribution necessity assessment is the structured process of determining whether a system genuinely needs to be distributed — most systems don't, and the cost of unnecessary distribution is significant; the answer to "should we distribute?" should always be evidence-based.

| DST-077 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DST-001, DST-002, DST-066, DST-076 | |
| **Used by:** | | |
| **Related:** | DST-001, DST-002, DST-066, DST-076 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams adopt microservices and distributed architectures
because Netflix uses them, because it looks impressive
on a CV, or because a conference talk made it sound
necessary. The result: 5-person teams with 30
microservices, spending 80% of engineering time on
infrastructure and distributed systems complexity,
instead of on product. The "monolith is a bad word"
culture causes premature distribution.

**THE BREAKING POINT:**
A startup's monolith serving 10,000 users works
perfectly. An engineer proposes migrating to microservices
"to prepare for scale." 6 months later: 15 microservices;
3 engineers spent on infrastructure; velocity dropped
70%; still 10,000 users. The distribution added cost
with no benefit. The monolith could have served
10x more users with zero distributed systems overhead.

**THE INVENTION MOMENT:**
Martin Fowler's "Monolith First" rule (2015): build
a monolith first; extract services only when you have
a specific reason. Sam Newman's "Building Microservices"
(2015): explicitly lists when microservices are NOT
appropriate. Martin Kleppmann's "DDIA" (2017): "don't
distribute unless you have to."

**EVOLUTION:**
The industry has moved through hype cycles: monolith
(pre-2010) → SOA (2005) → microservices (2012) →
"microservices considered harmful" backlash (2018) →
modular monolith renaissance (2020+). The current
consensus: distribute when specific triggers are met;
not by default.

---

### 📘 Textbook Definition

**Distribution necessity assessment** is the structured
evaluation of whether a system's requirements genuinely
need distribution. It evaluates four dimensions:
**Scale** (does traffic or data volume exceed a single
machine?), **Reliability** (does the system require
availability beyond a single machine?), **Autonomy**
(does the team structure require independent deployment?),
and **Compliance** (do data residency requirements
force geographic distribution?). Distribution is
justified only when at least one dimension cannot be
met by a non-distributed architecture.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Before distributing: prove that a single well-engineered machine cannot meet your requirements — if it can, distribution adds cost with no benefit.

**One analogy:**

> Distribution necessity assessment is like deciding
> whether to build a second factory. One factory can
> produce 10,000 units/month. Your orders are 1,000/month.
> Building a second factory doesn't double your output;
> it doubles your overhead with no throughput benefit.
> Build the second factory only when orders exceed
> 10,000 units/month — and not a day sooner.

**One insight:**
A well-optimised single Postgres instance can handle
100,000 TPS. A single application server can handle
50,000 concurrent requests. Most applications never
reach these numbers. The question is not "could we
distribute?" but "do we need to, and does the benefit
exceed the cost?"

---

### 🔩 First Principles Explanation

**FOUR DIMENSIONS OF DISTRIBUTION NECESSITY:**
```
1. SCALE
   Question: Can a single machine (vertical scale) meet
             the capacity requirement?

   Single machine capacity (2024 cloud hardware):
     AWS r8g.metal: 192 vCPUs, 1536 GB RAM, 25Gbps NIC
     Postgres single instance: 100,000 TPS (OLTP)
     Redis single instance: 1,000,000 ops/sec
     Node.js: 50,000+ req/sec (I/O bound)

   If traffic < 10% of single machine capacity:
     -> No scale justification for distribution
     -> Vertical scale is cheaper and simpler

   Triggers for horizontal scale:
     -> Peak traffic exceeds single machine
     -> Data volume exceeds single machine storage
     -> Compute is CPU-bound and unparallelisable per machine

2. RELIABILITY
   Question: Does the SLA require availability beyond
             a single machine MTBF?

   Single machine MTBF (cloud): ~10 years
   => ~99.999% availability (5.25 min downtime/year)

   Note: single machine 99.999% requires:
     fast automated restart (<30s);
     health checks; process manager

   Triggers for distribution for reliability:
     -> SLA requires >99.99% (planned maintenance too)
     -> Geographic redundancy required (region failure)
     -> Zero-downtime deployment required

3. TEAM AUTONOMY
   Question: Do team structure and deployment independence
             require separate services?

   Distribution justified if:
     -> Teams deploy independently without coordination
     -> Different scaling profiles per component
     -> Different technology choices per component
     -> Regulatory separation (billing team isolated from order team)

   NOT justified:
     -> Single team owns all code
     -> Deployments are coordinated anyway
     -> "We might grow the team"

4. COMPLIANCE / DATA RESIDENCY
   Question: Do legal requirements force geographic
             distribution?

   GDPR: EU data must stay in EU -> region separation forced
   HIPAA: Healthcare data residency -> not necessarily distributed
   PCI DSS: Cardholder data isolation -> may require service separation
```

**COST OF DISTRIBUTION:**
```
For a 5-engineer team:
  Kubernetes cluster:     1 engineer x 20% = 0.2 FTE
  Service mesh:           1 engineer x 10% = 0.1 FTE
  Distributed tracing:    1 engineer x 5%  = 0.05 FTE
  CI/CD per service:      5 services x 2%  = 0.10 FTE
  On-call complexity:     2x incidents     = 0.2 FTE
  Total overhead:         ~0.65 FTE
  vs. 5 FTEs = 13% of engineering on infrastructure

For a 5-engineer team with 30 microservices:
  Total overhead: 2.5+ FTEs = 50% of engineering
  Product velocity: halved
  User impact: zero (30 services for 10K users)
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Some systems genuinely require distribution (Google Search, Netflix, global banking).
**Accidental:** Distributing a system that doesn't need it, because distribution is fashionable.

---

### 🧪 Thought Experiment

**SETUP:**
A B2B SaaS startup has 500 enterprise customers,
5,000 daily active users, 1,000 API requests/second
peak, a 5-engineer team.

**DISTRIBUTION NECESSITY ASSESSMENT:**
```
Dimension 1: Scale
  1,000 req/sec = trivially handled by:
  - Single Node.js: 50x headroom
  - Single Postgres: 100x headroom
  Conclusion: NO scale justification

Dimension 2: Reliability
  SLA: 99.9% (8.76 hours downtime/year)
  Single machine + auto-restart achieves 99.95%
  Conclusion: NO reliability justification
  (if SLA was 99.99%: justify 2-node active-passive)

Dimension 3: Team autonomy
  5 engineers; all own all code; deploy together
  No regulatory separation required
  Conclusion: NO autonomy justification

Dimension 4: Compliance
  Enterprise customers in US and EU
  GDPR: EU customer data must stay in EU
  Conclusion: YES; EU data residency requires
    region-separated storage; NOT full microservices
    -> modular monolith + region-sharded DB is sufficient

ASSESSMENT RESULT:
  Distribution justified: NO (for microservices)
  Distribution justified: PARTIALLY (region-sharded DB for GDPR)
  Recommendation: modular monolith + Postgres (multi-AZ)
    + region-sharded DB for EU customer data
  Engineering overhead savings: 2.5 FTE vs microservices
```

---

### 🧠 Mental Model / Analogy

> Distribution necessity assessment is the "Yagni"
> principle applied to distributed systems. Yagni:
> "You Ain't Gonna Need It" — don't build features
> until you need them. Distribution yagni: don't distribute
> until you can demonstrate that a non-distributed
> architecture cannot meet the specific, measured
> requirement. Speculative distribution is technical debt
> that arrives immediately.

**Element mapping:**
- Yagni for features = don't build what you don't need
- Yagni for distribution = don't distribute what doesn't need distributing
- "We might need it" = premature distribution anti-pattern
- Measured requirement = proven trigger for distribution

Where this analogy breaks down: Yagni for features is
low-cost to reverse; distributing and then de-distributing
has high reversal cost — so assessment is even more critical.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before splitting your application into multiple
services, check: does it actually need to be split?
Most apps don't. A well-built single application is
simpler, cheaper, and faster to develop.

**Level 2 - How to use it (junior developer):**
Before proposing distribution: measure current utilisation.
If your DB is at 10% CPU and your app server is at
20% memory, you have 5-10x headroom. Distribution
doesn't help. Come back when you're at 70%+ utilisation
or when a specific reliability requirement can't be
met by a single-machine architecture.

**Level 3 - How it works (mid-level engineer):**
Modular monolith + vertical scale is often the right
architecture for teams < 50 engineers or systems
< 100,000 TPS. Extract services when: (1) a module
has a dramatically different scaling profile; (2) a
module needs a different SLA; (3) a module needs a
different technology; or (4) a team needs truly
independent deployment. These are specific triggers,
not general preferences.

**Level 4 - Why it was designed this way (senior/staff):**
Amazon (2002 Bezos API mandate), Netflix (2008+), and
Uber (2014+) all distributed because they measured
specific bottlenecks that single machines couldn't
meet. Amazon's monolith couldn't be deployed without
taking down unrelated services. Netflix's streaming
could not scale regionally on one machine. Uber's
driver-dispatch had different compute and latency
requirements than their billing. Each extracted services
for a specific, measured reason. The anti-pattern:
extract first, find the reason later.

**Expert Thinking Cues:**
- When someone proposes microservices: ask "what specific requirement cannot be met by a modular monolith?"
- Distribution is a cost that must earn its keep with a specific, measurable benefit.
- The monolith is not a failure state; it is the appropriate architecture for most systems at most scales.

---

### ⚙️ How It Works (Mechanism)

**Distribution necessity scorecard:**
```markdown
## Distribution Necessity Assessment

### Scale
- [ ] Peak traffic > 50% of single machine capacity?
- [ ] Data volume > single machine storage?
- [ ] CPU-bound computation requiring parallel machines?

### Reliability
- [ ] SLA requires >99.99% (beyond single machine MTBF)?
- [ ] Geographic redundancy required?
- [ ] Zero-downtime deployment required AND cannot achieve
      with rolling restart?

### Team Autonomy
- [ ] Multiple teams requiring truly independent deployment?
- [ ] Dramatically different scaling profiles per component?
- [ ] Regulatory separation required?

### Compliance
- [ ] Data residency requirements (GDPR etc.)?

### Scoring
0-1 YES: Strong recommendation against distribution
2 YES: Consider targeted distribution of specific bottleneck
3+ YES: Distribution is justified

### Current assessment: [0/4 YES]
### Recommendation: modular monolith + vertical scale
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Distribution decision flow:**
```
New system or refactor proposed:     <- YOU ARE HERE
  |
Measure current state (if existing):
  -> CPU utilisation (peak and average)
  -> Memory utilisation
  -> DB query time (p99)
  -> Deployment frequency and coupling
  |
Apply 4-dimension assessment:
  Scale -> Reliability -> Autonomy -> Compliance
  |
If 0-1 YES:
  -> Modular monolith + vertical scale
  -> Re-assess when triggers are hit
  |
If 2+ YES:
  -> Identify specific components to distribute
  -> Distribute only those components
  -> Keep rest as modular monolith
  |
Document decision:
  -> ADR with specific triggers met
  -> Review trigger: re-assess at 2x current scale
```

---

### ⚖️ Comparison Table

| Architecture | Complexity | Team Size Sweet Spot | Distribution Trigger |
|---|---|---|---|
| Monolith | Low | 1-10 engineers | None |
| Modular monolith | Low-Medium | 10-50 engineers | Team module ownership |
| Macroservices (3-5) | Medium | 20-100 engineers | Scale/reliability triggers |
| Microservices (10+) | High | 50+ engineers | All 4 triggers met |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Monolith = legacy = bad" | Monolith = appropriate architecture for specific scale and team size; not inherently bad |
| "Microservices = scalable" | Microservices enable independent scaling; they don't automatically make a system faster |
| "We should prepare for scale" | Premature optimisation; distribute when scale is measured, not predicted |
| "Netflix/Amazon use microservices" | Netflix/Amazon have specific requirements that justify microservices; most companies don't |
| "Microservices = one service per engineer" | Team size and service count are independent; one team can own multiple services or one large service |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Premature Microservices (Distributed Monolith)**
**Symptom:** 15 microservices all deployed together; distributed transactions everywhere; slow velocity.
**Root Cause:** Services are logically tightly coupled despite physical separation.
**Diagnostic:**
```bash
# Count cross-service synchronous calls in a single request
# If a single request touches >5 services: distributed monolith
grep -r 'RestTemplate\|WebClient\|feign' src/ | wc -l
```
**Fix:** Re-evaluate: merge highly coupled services; use asynchronous event-driven communication.

**Mode 2: Under-distribution (Single Point of Failure)**
**Symptom:** Single instance fails; full outage despite 99.99% SLA target.
**Root Cause:** Distribution assessment showed 0 triggers; no redundancy added.
**Fix:** Even without full distribution: multi-AZ deployment of monolith; auto-scaling group with minimum 2 instances.

**Mode 3: Wrong Trigger (Conway's Law Violation)**
**Symptom:** Teams distribute services along team boundaries; services share DB; performance worse than monolith.
**Root Cause:** Distributed by org chart, not by technical trigger; shared DB creates distributed monolith.
**Fix:** Services must be fully autonomous with their own DB; if they share a DB, merge them.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[DST-001 - What Is a Distributed System]]
- [[DST-002 - Why Distribution Is Hard]]
- [[DST-066 - Distributed System Architecture Strategy]]

**Builds On This (learn these next):**
- Modular monolith patterns
- Conway's Law

**Alternatives / Comparisons:**
- Vertical scaling (scale up before scaling out)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      4-dimension check: should this      |
|                 system actually be distributed?     |
| PROBLEM         Premature distribution: 50% of team |
| IT SOLVES       on infra; product velocity halved   |
| KEY INSIGHT     Single Postgres handles 100K TPS;   |
|                 most apps never need distribution   |
| USE WHEN        Before any new distributed system   |
|                 or microservices migration proposal |
| AVOID           "We might need scale" as justification|
| TRADE-OFF       Simplicity vs distribution benefits |
| ONE-LINER       Measure first; distribute when needed|
| NEXT EXPLORE    Modular monolith, vertical scaling  |
+-----------------------------------------------------+
```

**If you remember only 3 things:**
1. Four triggers for distribution: scale exceeds single machine, SLA requires multi-machine, team requires independent deployment, compliance forces geographic separation.
2. Most systems (< 100,000 TPS, < 50 engineers) are better served by a well-engineered modular monolith than by microservices.
3. Distribute specific bottlenecks, not the entire system; keep the rest as modular monolith until additional triggers are met.

**Interview one-liner:**
"Distribution necessity assessment evaluates four triggers: scale (exceeds single machine), reliability (SLA requires multi-instance), team autonomy (requires independent deployment), and compliance (data residency); distribution is justified only when a trigger is measured to be met — not as a default architecture choice."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Necessity is the only valid justification for complexity.
Every layer of complexity must earn its place by solving
a specific, measured problem. This applies to:
distribution (is it necessary?), abstractions (is this
layer necessary?), caching (is this cache necessary?),
microservices (is this separation necessary?). The
question is always "what specific problem does this
solve, and what is the evidence?"

**Where else this pattern appears:**
- **Caching** — add cache only when DB query is measured to be a bottleneck; not preemptively
- **Indexes** — add index only for measured slow queries; not on every column "just in case"
- **Abstraction layers** — add abstraction only when variation is measured to be needed; not speculatively

---

### 💡 The Surprising Truth

Stack Overflow, one of the world's top 100 websites
(serving 50M+ developers per month), ran on a single
primary SQL Server instance for most of its existence.
In 2016, Stack Overflow served 4,000+ requests per
second from a single SQL Server with 384GB RAM and
64 CPU cores. Their database had 40GB of working set
that fit in RAM; most queries returned in <1ms. No
distributed database; no microservices; no sharding.
The entire Stack Overflow application infrastructure
was 9 web servers, 4 SQL servers, and 3 tag engine
servers — a fraction of the complexity of a typical
startup with 10x fewer users using microservices.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Stack Overflow serves 50M
users/month from 9 web servers. A typical startup with
50,000 users/month has 30 microservices. Using back-of-
envelope math, estimate the ratio of infrastructure
complexity to users served for each. What does this
tell you about the relationship between distribution
and scale?

*Hint:* Stack Overflow: 9 servers / 50M users = 0.18 servers
per million users. Startup: 30 services / 0.05M users =
600 services per million users. Ratio: 3,300x more
complexity per user for the startup. Distribution does
not correlate with scale; it correlates with team
structure and specific technical requirements.

**Q2 (Design Trade-off):** A team is building a healthcare
platform. HIPAA requires cardholder data isolation.
GDPR requires EU patient data stays in EU. The team
has 8 engineers and 1,000 patients. Apply the 4-dimension
assessment: which dimensions justify distribution,
which don't, and what is the minimum architecture?

*Hint:* Scale: 1,000 patients = trivially single machine.
Reliability: healthcare SLA varies; but 99.9% achievable
with single multi-AZ. Autonomy: 8 engineers; modular
monolith is fine. Compliance: HIPAA isolation = service
boundary for billing (but modular monolith with logical
separation might suffice); GDPR EU residency = region-
sharded DB (forced). Minimum: modular monolith + EU DB
region separation. Not microservices.

**Q3 (Scale):** At what exact point should an e-commerce
platform that started as a modular monolith extract its
first service? Define the measurement criteria, the
specific trigger value, and which service to extract first.

*Hint:* Measurement: instrument monolith; identify hotspot
(CPU/memory/DB bottleneck). First trigger: DB CPU > 70%
sustained, OR specific module responsible for >80% of
DB queries. First extraction: the module causing the
bottleneck, not an arbitrary service. Extraction only
after measurement proves the trigger; never before.
