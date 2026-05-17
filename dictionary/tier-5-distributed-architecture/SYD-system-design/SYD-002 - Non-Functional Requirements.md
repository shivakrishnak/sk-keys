---
id: SYD-002
title: Non-Functional Requirements
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: SYD-001
used_by: SYD-003, SYD-005, SYD-006, SYD-007, SYD-008
related: SYD-001, SYD-015, SYD-026
tags:
  - architecture
  - foundational
  - mental-model
  - reliability
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 2
permalink: /syd/non-functional-requirements/
---

# SYD-002 - Non-Functional Requirements

⚡ TL;DR - Non-functional requirements define how well a system
performs its job: the speed, reliability, and scale constraints
that architecture must satisfy before writing a single feature.

| #002 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | System Design | |
| **Used by:** | Availability, Latency vs Throughput, Vertical Scaling, Horizontal Scaling, Load Balancing | |
| **Related:** | System Design, SLA / SLO / SLI, Back-of-Envelope Estimation | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team receives a requirements document for a banking
application. It lists every feature: account creation,
fund transfers, transaction history, bill pay. The team
builds all of it in three months. On launch day, 50,000
users log in simultaneously. Response times climb to 30
seconds. Some transactions complete twice. Others fail
silently. The transaction history page returns data from
20 minutes ago. The bank receives regulatory inquiries
about data integrity.

None of these failures are bugs in the feature code. They
are consequences of requirements that were never written
down: how fast must responses be? How consistent must
transaction records be? What happens when the database
is unreachable? These are the requirements that got
skipped because no one had a name for them.

**THE BREAKING POINT:**
Feature requirements tell the system what to do. They say
nothing about how reliably, how quickly, or at what scale
to do it. A system that satisfies all its functional
requirements can still fail catastrophically if it never
defined its non-functional ones.

**THE INVENTION MOMENT:**
This is exactly why non-functional requirements (NFRs)
were formalized as a distinct category. They are the
measurable quality attributes that an architecture must
satisfy, independent of what the system does.

**EVOLUTION:**
Early software ran on single machines where performance
was largely a hardware question. As distributed systems
emerged in the 1990s, NFRs became architectural levers -
choices that could be traded off against each other.
The CAP theorem (2000) made explicit that availability
and consistency are competing NFRs in distributed systems.
DORA metrics (2014) added deployment frequency and
recovery time as measurable engineering NFRs.

---

### 📘 Textbook Definition

Non-functional requirements (NFRs) are system quality
attributes that constrain how a system behaves, as distinct
from what it does. They include measurable properties such
as availability (the percentage of time the system is
operational), latency (time to process a single request),
throughput (requests processed per unit time), durability
(guarantee that written data is not lost), scalability
(ability to handle growth), and security (resistance to
unauthorized access or data breach). NFRs are satisfied
through architectural decisions - component decomposition,
replication strategy, consistency model, and caching
layer - not through application code.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
NFRs define how fast, how reliable, and how big a system
must be - the constraints that determine its architecture.

**One analogy:**
> Building specifications beyond "it must have four walls
> and a roof." The NFRs are: it must withstand a 7.0
> earthquake, maintain 20°C indoors in -10°C weather,
> and be accessible to wheelchair users. These constraints
> determine materials, structural design, and layout -
> not what rooms the building has.

**One insight:**
NFRs are the most important inputs to an architecture
design, yet they are the most commonly omitted from
requirements documents. The reason is that they are
cross-cutting - they affect every component - and they
require engineering judgment to quantify, not just
product intuition.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every system has quality constraints, whether documented
   or not. Undocumented NFRs become production surprises.
2. Most NFRs trade off against each other: higher consistency
   reduces availability; lower latency requires more
   resources; broader scalability increases complexity.
3. NFRs must be measurable. "The system must be fast" is
   not an NFR. "The p99 response time must be < 300ms" is.

**DERIVED DESIGN:**
Given that NFRs trade off against each other, an architect
must:
- Rank NFRs by business priority (is availability more
  important than consistency for this specific system?)
- Convert qualitative statements into measurable targets
- Choose the architectural pattern that satisfies the
  highest-priority NFRs without violating any hard floors
  on the lower-priority ones

**THE TRADE-OFFS:**
**Gain:** Explicit NFRs mean architecture decisions are
justified against requirements, not just engineering taste.
**Cost:** Quantifying NFRs requires domain knowledge of
production behavior that new teams often lack.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The trade-offs between NFRs are real and
irreducible. No architecture simultaneously achieves
maximum availability, consistency, and performance at
zero cost.
**Accidental:** Most NFR failures in practice are not
because trade-offs are hard - they are because NFRs
were never written down, so no trade-off was ever made.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams build identical social networks. Team A writes
down NFRs: "99.9% availability, p99 latency < 500ms, data
readable within 5 seconds of write." Team B does not.

**WHAT HAPPENS WITHOUT NFRs (Team B):**
Team B ships features faster. At 100k users, queries are
slow. A DBA adds indexes. At 500k users, the database is
still the bottleneck. The DBA tries read replicas. Some
reads return stale data - users see posts disappear and
reappear. No one knows if this is a bug or acceptable
behavior because "acceptable behavior" was never defined.
At 2M users, Team B rewrites the data layer under load.

**WHAT HAPPENS WITH NFRs (Team A):**
Team A's "p99 < 500ms" requirement forces the choice of
read replicas at the design phase. The "data readable
within 5 seconds" requirement defines the acceptable
replication lag, so stale reads are a known trade-off, not
a mystery bug. When 2M users arrive, the architecture
has already been designed for it.

**THE INSIGHT:**
NFRs do not slow down development. They prevent rewrites.
The time spent defining them upfront is always less than
the time spent fixing the production failures they predict.

---

### 🧠 Mental Model / Analogy

> NFRs are the Service Level Agreement between the product
> and its users - written before the system exists. They
> are the contract the architecture must honor.

- "Availability SLA" → the percentage of time the system
  must be operational (e.g., 99.9% = 8.7h downtime/year)
- "Latency target" → the response time the user expects
  (e.g., p99 < 300ms for web requests)
- "Throughput target" → the request volume the system
  must handle (e.g., 10,000 requests/second at peak)
- "Durability target" → data loss tolerance
  (e.g., RPO = 0 for payments, RPO = 1 hour for analytics)
- "Scalability target" → growth the system must handle
  without redesign (e.g., 10x DAU growth in 6 months)

**Where this analogy breaks down:**
Unlike legal SLAs, NFRs are internal architectural targets.
Violating them causes technical debt and production
incidents, not lawsuits - which is why teams often
underinvest in them.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you design a system, you need to decide not just
what it does, but how fast, how reliable, and how big
it needs to be. These are the non-functional requirements.

**Level 2 - How to use it (junior developer):**
Before designing any system, write down answers to:
How many users? What response time is acceptable? What
happens if the database is down for 5 minutes? How much
data can we afford to lose? These answers become your
NFRs and they constrain every architectural decision.

**Level 3 - How it works (mid-level engineer):**
NFRs are operationalized through architectural patterns.
Availability is achieved through replication and failover.
Latency is achieved through caching and co-location.
Throughput is achieved through horizontal scaling and
sharding. Durability is achieved through synchronous
replication and write-ahead logging. Each pattern
carries a cost in complexity and resource usage.

**Level 4 - Why it was designed this way (senior/staff):**
NFRs expose fundamental trade-offs in distributed systems.
The CAP theorem formalizes the consistency vs. availability
trade-off. PACELC extends it to include latency. Strong
consistency requires coordination (latency cost). High
availability requires accepting eventual consistency
(correctness cost). The architecture that maximizes one
typically degrades another.

**Level 5 - Mastery (distinguished engineer):**
Expert engineers distinguish hard NFRs (system cannot
launch if violated) from soft NFRs (degradation is
acceptable under extreme load). Payment systems have hard
NFRs on consistency - no double charges under any failure
mode. Social feeds have soft NFRs on freshness - stale
data for 30 seconds is acceptable to avoid distributed
coordination overhead. The architecture that conflates
these two classes over-engineers soft NFRs and under-
engineers hard ones.

---

### ⚙️ How It Works (Mechanism)

The standard NFR categories and how they translate to
architectural decisions:

```
┌─────────────────────────────────────────────────┐
│ NFR TAXONOMY - ARCHITECTURAL IMPLICATIONS       │
├──────────────────┬──────────────────────────────┤
│ NFR              │ Architectural Lever           │
├──────────────────┼──────────────────────────────┤
│ Availability     │ Replication, failover, LB     │
│ Latency          │ Caching, co-location, CDN     │
│ Throughput       │ Horizontal scale, sharding    │
│ Durability       │ Sync replication, WAL, backup │
│ Consistency      │ Transactions, 2PC, RAFT       │
│ Scalability      │ Statelessness, partitioning   │
│ Security         │ Authz, encryption, audit log  │
│ Observability    │ Metrics, tracing, alerting    │
│ Maintainability  │ API boundaries, documentation │
└──────────────────┴──────────────────────────────┘
```

**Quantifying NFRs - the key skill:**

Each NFR must be expressed as a measurable target with
a defined measurement methodology:

```
AVAILABILITY:
  Target:  99.9% (8.7 hours downtime/year)
  Measure: (total_time - downtime) / total_time
  Alert:   Page if error rate > 1% for > 5 minutes

LATENCY:
  Target:  p50 < 100ms, p99 < 500ms, p999 < 2s
  Measure: HTTP response time histogram
  Alert:   Page if p99 > 500ms for > 3 minutes

THROUGHPUT:
  Target:  Handle 10,000 requests/second at peak
  Measure: Requests per second from load balancer
  Alert:   Page if throughput drops > 20% from baseline

DURABILITY:
  Target:  RPO = 0 (no committed writes lost)
           RTO = 30 minutes (restore within 30 min)
  Measure: Backup completion status + restore test
  Alert:   Page if last successful backup > 25h ago
```

**NFR conflict resolution:**
When NFRs conflict, the business priority determines which
wins. For a payment system: Durability > Consistency >
Availability > Latency. For a social feed: Availability
> Latency > Consistency > Durability. These priority
rankings must be written down explicitly because when
the system fails under load, the on-call engineer will
need to know which degraded mode is acceptable.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Business Requirements]
    → [Feature List (Functional)]
    → [NFR Extraction ← YOU ARE HERE]
    → [NFR Prioritization]
    → [Architecture Decisions]
    → [Component Design]
    → [Implementation]
    → [Monitoring (validates NFRs in prod)]
```

**FAILURE PATH:**
NFRs skipped → architecture without quality constraints
→ production incident → emergency NFR extraction from
incident data → retroactive architecture changes

**WHAT CHANGES AT SCALE:**
At 10x scale, latency NFRs force caching layers that
introduce consistency trade-offs. At 100x, throughput
NFRs drive sharding strategies that change query patterns.
At 1000x, availability NFRs require multi-region
deployment that introduces geo-distribution complexity.

---

### 💻 Code Example

NFRs themselves are not code, but they are documented
in a structured way that drives implementation decisions.

**Example 1 - BAD: NFRs expressed as vague aspirations**
```
# BAD: These are opinions, not requirements.
# Unmeasurable = unenforced = ignored.
- The system should be fast
- The system should be reliable
- The system should handle high traffic
- Data should not be lost
```

**Example 2 - GOOD: NFRs as measurable targets**
```yaml
# GOOD: Each NFR is measurable and traceable
# to an architectural decision.
nfrs:
  availability:
    target: 99.9%
    measurement: "uptime / total time, 30-day window"
    hard_floor: 99.0%
    owner: platform-team

  latency:
    p50_ms: 100
    p99_ms: 500
    p999_ms: 2000
    measurement: "HTTP response time histogram"
    scope: "read API endpoints"

  throughput:
    peak_rps: 10000
    sustained_rps: 5000
    measurement: "nginx access log rate"

  durability:
    rpo_minutes: 0
    rto_minutes: 30
    measurement: "backup completion + restore test"

  consistency:
    model: "read-your-writes within session"
    acceptable_lag_seconds: 5
    hard_requirement: "no double-charge on payment"
```

**Example 3 - Production: NFR as SLO with alert**
```yaml
# SLO-based alerting (Prometheus + AlertManager)
groups:
  - name: nfr-slos
    rules:
      - alert: AvailabilitySLOBreach
        expr: |
          (
            sum(rate(http_requests_total{
              status!~"5.."
            }[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) < 0.999
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "Availability below 99.9% SLO"

      - alert: LatencySLOBreach
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.5
        for: 3m
        labels:
          severity: page
```

---

### ⚖️ Comparison Table

| NFR Type | Primary Lever | Cost | Most Critical For |
|---|---|---|---|
| **Availability** | Replication + failover | Hardware, complexity | Customer-facing services |
| Latency | Caching, co-location | Memory, cost | User-facing reads |
| Throughput | Horizontal scale | Statelessness needed | High-volume ingestion |
| Durability | Sync replication, WAL | Write latency increase | Financial data |
| Consistency | Distributed transactions | Throughput reduction | Payment, inventory |
| Scalability | Sharding, statelessness | Design complexity | Hypergrowth products |

**How to choose:**
Map each NFR to the failure mode it prevents. Availability
prevents "system is down" incidents. Durability prevents
"data was lost" incidents. Choose the NFR level by asking:
what is the business cost of violating this for 1 hour?

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| NFRs are defined once and never revisited | NFRs must be re-evaluated as user volume and business criticality change |
| "We'll add reliability later" | Retrofitting availability and durability into a running system costs 5-10x more than designing for it upfront |
| High availability means zero downtime | 99.9% availability allows 8.7 hours of downtime per year. Zero downtime is 100% availability - often unnecessary and very expensive |
| NFRs are the platform team's concern | NFRs are defined by the business requirements and owned by the service team. Platform provides mechanisms; teams choose targets |
| Security is a separate concern from NFRs | Security is an NFR: "the system must resist SQL injection" is as much an NFR as "the system must respond in 300ms" |

---

### 🚨 Failure Modes & Diagnosis

**Missing Durability NFR**

**Symptom:**
A database failure causes data loss. The team discovers
they had no backup strategy because no one had written
down how much data loss was acceptable.

**Root Cause:**
RPO (Recovery Point Objective) was never defined. No one
owned the decision, so no one made it. The database
defaulted to async replication with no backups.

**Diagnostic Command:**
```bash
# Check backup freshness
aws s3 ls s3://backups/prod/ --recursive | \
  sort | tail -5

# Check replication lag (PostgreSQL)
psql -c "SELECT now() - pg_last_xact_replay_timestamp()
  AS replication_lag;"

# Check WAL archiving status
psql -c "SELECT archived_count, failed_count,
  last_archived_wal FROM pg_stat_archiver;"
```

**Fix:**
Define RPO immediately. For RPO=0, enable synchronous
replication. For RPO=1h, enable WAL archiving to S3 with
hourly snapshots. Test restore from backup monthly.

**Prevention:**
Add durability NFR to the service design template.
Require backup strategy documentation before production
launch.

---

**Inconsistent NFR Ownership**

**Symptom:**
The p99 latency SLO is breached in production. Three
teams claim it is not their component causing it. No
one owns the end-to-end latency NFR.

**Root Cause:**
The NFR was defined at the system level but not
decomposed into component-level budgets. Each component
team has a local SLO that sums to more than the system
budget allows.

**Diagnostic Command:**
```bash
# Trace request latency by component (Jaeger/Zipkin)
curl "http://jaeger:16686/api/traces?\
  service=api-gateway&limit=20" | \
  jq '.data[].spans[] | {op: .operationName,
      dur: .duration}'

# Check per-service latency contribution
kubectl exec -n monitoring prometheus-0 -- \
  promtool query instant \
  'histogram_quantile(0.99,
    rate(grpc_server_handling_seconds_bucket[5m]))
    by (grpc_service)'
```

**Fix:**
Define a latency budget per tier. If total budget is
500ms: frontend = 50ms, API = 100ms, service = 200ms,
database = 150ms. Each team owns their slice.

**Prevention:**
Decompose system-level NFRs into component-level budgets
at design time. Each service team owns their budget.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `System Design` - the discipline that NFRs feed into as
  primary design inputs

**Builds On This (learn these next):**
- `Availability` - the most critical NFR for customer-
  facing systems, with specific measurement methodology
- `SLA / SLO / SLI` - the operational framework for
  measuring and enforcing NFRs in production
- `Back-of-Envelope Estimation` - the technique for
  quantifying throughput and storage NFRs

**Alternatives / Comparisons:**
- `Functional Requirements` - what the system does vs.
  how well it does it; NFRs constrain all functional features

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Quality attributes a system must satisfy  │
│              │ independent of its feature set             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Systems built without NFRs fail under     │
│ SOLVES       │ load in ways nobody anticipated            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ NFRs conflict with each other. Picking    │
│              │ one (consistency) means sacrificing       │
│              │ another (availability or latency)         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every system design session, before any   │
│              │ component diagram is sketched              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never avoid - even disposable systems     │
│              │ need a "don't care" NFR definition        │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ "The system must be fast and reliable"    │
│              │ - not measurable, not an NFR              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Specificity (time to define) vs ambiguity │
│              │ (production surprises)                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Features tell you what to build.        │
│              │  NFRs tell you how well to build it."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Availability → SLA/SLO/SLI → Capacity    │
│              │ Planning                                  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. NFRs are measurable quality targets, not vague
   aspirations. "Fast" is not an NFR; "p99 < 300ms" is.
2. NFRs conflict. You cannot simultaneously maximize
   consistency, availability, and performance. Pick
   the priority order before the system exists.
3. Missing NFRs become production incidents. The cost
   of retroactive NFR satisfaction is always higher
   than proactive design.

**Interview one-liner:**
"Non-functional requirements are the measurable quality
attributes - availability, latency, throughput, durability
- that constrain every architectural decision. They matter
more than features because features can be added; retrofitting
availability into a running system is 10x more expensive."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every system has two requirement layers: what it does
and how well it does it. The second layer is harder to
write, easier to skip, and more expensive to retrofit.
This pattern appears in every engineering discipline:
a bridge's functional requirement is to span a gap;
its NFRs are load capacity, wind resistance, and design
life. Bridges are not designed without structural NFRs;
software systems routinely are.

**Where else this pattern appears:**
- **Database schema design** - the schema is the functional
  design; index strategy is the NFR satisfaction layer.
  Teams who skip index planning add them under production
  load, causing table locks and downtime.
- **API design** - the endpoint contract is functional;
  rate limits, timeouts, and backward compatibility
  guarantees are the NFR layer. Clients break when these
  are defined only after first production failure.
- **Machine learning systems** - model accuracy is
  functional; inference latency, model staleness, and
  fallback behavior are the NFRs. ML systems routinely
  launch without defining acceptable inference latency.

**Industry applications:**
- **Financial services** - payment systems have hard NFRs
  on consistency (no double charges), durability (no lost
  transactions), and availability (99.999% uptime).
  Missing any of these is a regulatory violation, not
  just a customer experience problem.
- **Healthcare** - EHR systems require NFRs on data
  integrity (no data corruption), audit trail completeness,
  and access control that are mandated by HIPAA. NFR
  violations create legal liability.

---

### 💡 The Surprising Truth

The most consequential NFR is usually the one left out of
the requirements document. In 2017, Amazon S3 experienced
a significant outage when a human error during routine
maintenance brought down a large portion of US-EAST-1.
The root cause was not missing availability infrastructure -
Amazon's availability engineering was world-class. The root
cause was a missing operational NFR: "the blast radius of
any single maintenance command must be bounded." The runbook
that allowed an engineer to remove a large block of servers
in a single command violated an implicit NFR that had never
been written down. The S3 post-mortem added tooling that
prevented any single command from removing more than a
bounded number of servers - the implicit NFR was finally made
explicit. The most dangerous missing NFR is the one everyone
assumes is handled somewhere else.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Given a business description of any service,
   extract the five most critical NFRs and express each
   as a measurable target with a monitoring methodology.
2. [DEBUG] Given an incident post-mortem, identify which
   NFR was violated, whether it was ever defined, and what
   architectural decision (or omission) caused the violation.
3. [DECIDE] For a social media feed vs a payment processing
   service, rank the same six NFRs in different priority
   orders and justify why the ranking differs.
4. [BUILD] Write an NFR document for a system you currently
   own. Define availability, latency (p50/p99), throughput,
   durability (RPO/RTO), and consistency model.
5. [EXTEND] Identify the implicit NFR that your current
   system violates under conditions that have not yet been
   hit in production. What load or failure scenario would
   expose it?

---

### 🧠 Think About This Before We Continue

**Q1.** A startup builds a photo-sharing app and defines
these NFRs: "99.9% availability, p99 < 500ms reads, no
data loss." Eighteen months later, the system is running
at 10x the designed load. Which of these three NFRs is
most likely to have been violated first, and what specific
component is the bottleneck?

*Hint: Think about which NFR requires the most hardware
resources to sustain as load grows. Latency degrades
gradually; availability degrades suddenly; durability
is usually unaffected by load until disk fills. Trace
which component first runs out of capacity.*

**Q2.** The CAP theorem says you can only guarantee two
of Consistency, Availability, and Partition Tolerance.
How does this theorem constrain which NFRs a distributed
system can simultaneously satisfy, and what does it mean
for a payment system designer choosing between strong
and eventual consistency?

*Hint: Think about what "consistency" means for a payment
system specifically (no double charges, no lost
transactions) versus what "availability" means (users
can always initiate payments). During a network partition,
which behavior does the business require?*

**Q3 (Hands-On):** Take a system you currently work on.
Write down its NFRs from memory - no documentation
allowed. Then check the actual documentation (if it exists).
What NFRs did you miss? What NFRs does the system have
that are unmeasured? Pick the most important missing
measurement and describe how you would add it.

*Hint: Start with: availability (do you have an SLO?),
latency (do you have p99 targets?), durability (do you
have a defined RPO?). Each missing one is a production
risk that is currently invisible.*

---

### 🎯 Interview Deep-Dive

**Q1: When you start designing a new system, how do you
determine what the non-functional requirements are?**
*Why they ask:* Tests whether the candidate has a
structured process for extracting NFRs or just wings it.
*Strong answer includes:*
- Ask about user-facing SLAs: what does the business
  promise users? (Response time, uptime)
- Ask about business criticality: what is the cost of
  1 hour of downtime? (Determines availability target)
- Ask about data importance: can data be replayed or
  is it lost forever? (Determines durability target)
- Ask about growth trajectory: how many users in 1 year?
  (Determines scalability requirements)

**Q2: Your team just had a production incident where the
database primary failed and 2 hours of user data was lost.
How would you retroactively define the durability NFR,
and what architectural change would you make?**
*Why they ask:* Tests incident-driven NFR learning and
architectural decision-making under production reality.
*Strong answer includes:*
- Define RPO from the incident: "2 hours of loss is
  unacceptable for user content; RPO = 0 is required"
- Enable synchronous replication to a standby with
  confirmation before acknowledging writes
- Add WAL archiving to S3 for point-in-time recovery
- Test recovery quarterly with a documented runbook

**Q3: How do you handle NFR conflicts? For example, a
payment service needs both 99.999% availability and
strong consistency for transactions.**
*Why they ask:* Tests depth of distributed systems
understanding and ability to navigate real trade-offs.
*Strong answer includes:*
- These NFRs conflict under network partition (CAP theorem)
- Resolve by defining behavior per scenario: during normal
  operation, achieve both; during partition, consistency
  wins over availability (payments queue, not process)
- Implement: synchronous replication for writes, circuit
  breaker to queue requests during partition, automatic
  retry with idempotency key after partition heals
- Define the acceptable degraded mode explicitly: users
  see "payment queued" during partition, not "payment failed"
