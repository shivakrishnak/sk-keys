---
id: DST-070
title: Global Distribution Strategy
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
  - architecture
  - bestpractice
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 70
permalink: /distributed-systems/global-distribution-strategy/
---

# DST-070 - Global Distribution Strategy

⚡ TL;DR - Global distribution strategy decides how to deploy across regions: active-active (full capacity everywhere, conflict risk), active-passive (one region hot, failover cold), or follow-the-sun (data sovereignty, lowest latency to user).

| DST-070         | Category: Distributed Systems               | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | DST-006, DST-008, DST-024, DST-033, DST-038 |                 |
| **Used by:**    | DST-066                                     |                 |
| **Related:**    | DST-006, DST-008, DST-033, DST-066, DST-072 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company deploys their application in one AWS region.
Users in Asia-Pacific experience 200ms latency. A
regional AWS outage takes the service fully down globally.
Compliance requires EU data to stay in the EU. Each
of these problems requires a different distribution
strategy; without explicit strategy, all three problems
co-exist.

**THE BREAKING POINT:**
A payments company deploys active-active across
us-east-1 and eu-west-1. A customer clicks "pay" in
the US. The request is processed. Before the response
arrives, another request from the EU processes the
same payment (replication lag: 80ms). Double charge.
No conflict resolution. Active-active for payments
requires explicit conflict handling or is the wrong
strategy.

**THE INVENTION MOMENT:**
Amazon Route 53 (2006): DNS-based geo-routing. AWS
Multi-Region design patterns (2012+). Google Spanner's
external consistency (2012): first database supporting
global active-active with strong consistency.

**EVOLUTION:**
Modern strategies: CockroachDB (2017) for global
active-active SQL. AWS Global Accelerator (2018) for
routing. Cloudflare Workers and Durable Objects (2021)
for edge-distributed state. The frontier: serverless
global distribution without region management.

---

### 📘 Textbook Definition

**Global distribution strategy** defines how an application
deployed across geographic regions handles: write routing
(which region accepts writes?), read routing (can reads
be served locally?), consistency (are all regions
synchronised?), failover (what happens when a region
fails?), and data sovereignty (can data cross borders?).
Strategies: **active-active** (all regions accept writes;
conflicts must be resolved), **active-passive** (one
region is primary; others are read replicas or standbys),
**follow-the-sun** (primary region rotates with business
hours), **sharding by region** (each user pinned to
their closest region).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Global distribution strategy decides which regions accept writes, how they stay in sync, and what happens when a region fails — the choice determines your consistency, latency, and conflict trade-offs.

**One analogy:**

> Global distribution strategy is like choosing how
> to run branches of a bank. Active-active: every branch
> accepts deposits and withdrawals, but needs to sync
> balances continuously. Active-passive: one main branch
> accepts all transactions; others are read-only ATMs;
> if main branch closes, pick one ATM to promote. Region
> sharding: each customer belongs to one branch; never
> uses another.

**One insight:**
Active-active is appealing because it has no single
point of failure. But it's the hardest strategy:
every write must be conflict-resolvable. Most businesses
don't need active-active; they need fast failover from
active-passive, which is simpler to implement and safer.

---

### 🔩 First Principles Explanation

**FOUR GLOBAL DISTRIBUTION PATTERNS:**

```
1. ACTIVE-PASSIVE (Single-Primary)
   Writes -> us-east-1 (primary)
   Reads  -> eu-west-1, ap-southeast-1 (replicas)
   Failover: promote eu-west-1 on us-east-1 failure
   Consistency: strong on primary; eventual on replicas
   Conflict risk: NONE (one write path)
   Latency: writes: US latency; EU writes: cross-region
   Use: financial systems, booking systems

2. ACTIVE-ACTIVE (Multi-Primary)
   Writes -> any region
   Reads  -> local region
   Replication: async (lag: ~80ms cross-continent)
   Conflict: possible (same record written in 2 regions)
   Conflict resolution: LWW, CRDT, or application-logic
   Consistency: eventual (unless Spanner/CockroachDB)
   Use: social media, CDN, user-generated content
   NOT for: financial transactions without explicit design

3. FOLLOW-THE-SUN
   Business hours US: us-east-1 is primary
   Business hours APAC: ap-southeast-1 is primary
   Rotation: DNS failover + primary promotion scheduled
   Use: B2B SaaS with regional business hours
   Complexity: scheduled promotion; state transfer

4. REGION SHARDING (Pinned Users)
   EU users -> eu-west-1 always
   US users -> us-east-1 always
   Data: never crosses region boundary
   Consistency: strong (no cross-region writes)
   Use: GDPR compliance; data residency requirements
   Limitation: user must always use same region
```

**FAILOVER STRATEGIES:**

```
RPO (Recovery Point Objective):
  Max acceptable data loss
  Active-passive async: RPO = replication lag (seconds)
  Active-passive sync: RPO = 0 (but: latency penalty)
  Active-active: RPO = 0 (if conflict-resolved correctly)

RTO (Recovery Time Objective):
  Max acceptable downtime
  DNS failover: 30-300s (TTL dependent)
  BGP anycast: <30s
  Route53 health-check: ~30s detection + TTL
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Multi-region systems must choose how to handle writes and conflicts; these choices are irreducible.
**Accidental:** Choosing active-active without designing conflict resolution (the hard part of active-active).

---

### 🧪 Thought Experiment

**SETUP:**
Design a global e-commerce platform.
Requirements: (a) EU users must see EU orders only
(GDPR), (b) checkout must not double-charge, (c)
product catalogue must be globally fast.

**APPLYING THE PATTERNS:**

```
Product catalogue:
  Write: once (admin team, US)
  Read: globally, high volume, stale-OK (1min)
  -> Active-passive + CDN caching
  -> Primary: us-east-1; CDN edges worldwide
  -> Latency: <50ms globally; no conflict risk

User orders (GDPR):
  EU orders must stay in EU
  -> Region sharding by user residency
  -> EU users always routed to eu-west-1
  -> US users always routed to us-east-1
  -> No cross-region data transfer

Payment/checkout:
  Cannot double-charge; requires strong consistency
  Write must be atomic
  -> Active-passive; writes to user's region only
  -> Idempotency key + linearizable write
  -> Failover: promote replica; RPO ~0 (sync replication)
```

**THE INSIGHT:**
Three domains; three different distribution patterns.
No single strategy works for all domains. The right
design maps each domain to the pattern that satisfies
its correctness and latency requirements.

---

### 🧠 Mental Model / Analogy

> Global distribution is like running a worldwide
> restaurant chain. Active-passive: only the Paris
> kitchen creates new recipes; all other branches
> follow Paris (replicas). Active-active: every branch
> can invent recipes, but must not serve contradictory
> dishes in the same day (conflict resolution). Region
> sharding: each customer is assigned one branch for
> life (data residency). Each model has a cost.

**Element mapping:**

- Restaurant branch = AWS region
- Recipe creation = write
- Recipe following = replication
- Same dish contradiction = write conflict
- Customer assignment = region sharding

Where this analogy breaks down: restaurant branches
can physically serve customers from any location; data
residency means data physically cannot cross borders.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Global distribution decides: Which regions take orders
(writes)? Who can read? What happens when one region
goes down? Different answers suit different businesses.

**Level 2 - How to use it (junior developer):**
When your service expands globally: start with
active-passive. Set up a primary region and one replica.
Configure Route53 health-check failover. Accept that
writes go to one region (slightly higher write latency
for remote users) until you have a specific reason to
change.

**Level 3 - How it works (mid-level engineer):**
Active-passive setup on AWS: primary RDS in us-east-1;
read replica in eu-west-1. Route53: latency routing
for reads (route to nearest). Health-check failover
for writes (if primary down, promote replica; update
DNS). RTO: ~2min (DNS propagation). RPO: replication
lag (typically seconds).

**Level 4 - Why it was designed this way (senior/staff):**
Google Spanner's external consistency makes active-active
with strong consistency possible globally. Mechanism:
2-phase commit across shards + TrueTime wait (7ms)
ensures no two concurrent transactions overlap across
regions. Cost: every cross-shard write takes 5-10ms.
For most use cases, active-passive + saga compensation
achieves similar correctness with lower operational
complexity. Spanner is appropriate when the business
requirement is truly global strong consistency.

**Expert Thinking Cues:**

- When someone says "we need active-active": ask "what is the conflict resolution strategy?"
- Active-passive is almost always simpler and safer for financial systems.
- GDPR/data residency forces region sharding regardless of performance preference.

---

### ⚙️ How It Works (Mechanism)

**Route53 active-passive failover:**

```hcl
# Terraform: Route53 active-passive
resource "aws_route53_record" "primary" {
  zone_id = var.zone_id
  name    = "api.example.com"
  type    = "A"
  set_identifier = "primary"

  failover_routing_policy {
    type = "PRIMARY"
  }

  health_check_id = aws_route53_health_check.primary.id
  records = [aws_lb.us_east.dns_name]
  ttl     = 30
}

resource "aws_route53_record" "secondary" {
  zone_id = var.zone_id
  name    = "api.example.com"
  type    = "A"
  set_identifier = "secondary"

  failover_routing_policy {
    type = "SECONDARY"
  }

  records = [aws_lb.eu_west.dns_name]
  ttl     = 30
  # No health check: always serves if primary is down
}
# RTO: health_check_interval(30s) + TTL(30s) = ~60s
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Global distribution decision flow:**

```
Requirements analysis:               <- YOU ARE HERE
  |
Data residency required?:
  |-> Yes: region sharding forced
  |-> No: continue
  |
Conflict tolerance:
  |-> Conflicts unacceptable (finance): active-passive
  |-> Conflicts resolvable (social): active-active
  |
Write latency requirement:
  |-> All users need low-write latency: active-active
  |-> Only reads need to be global: active-passive + CDN
  |
RTO/RPO requirement:
  |-> RTO < 60s: DNS failover (Route53)
  |-> RTO < 5s: BGP anycast or Global Accelerator
  |-> RPO = 0: sync replication (cost: latency)
  |
Document strategy in ADR
```

---

### ⚖️ Comparison Table

| Strategy        | Write Latency       | Conflict Risk | Failover   | Data Sovereignty | Complexity |
| --------------- | ------------------- | ------------- | ---------- | ---------------- | ---------- |
| Active-passive  | Low (local primary) | None          | Manual/DNS | Possible         | Low        |
| Active-active   | Low (any region)    | High          | Automatic  | Partial          | Very High  |
| Follow-the-sun  | Low (during hours)  | Low           | Scheduled  | Possible         | High       |
| Region sharding | Low (pinned)        | None          | Per-shard  | Yes              | Medium     |

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                         |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| "Active-active is always more available" | Active-active without conflict resolution can cause data corruption; active-passive with fast failover is safer |
| "Multi-region = active-active"           | Most multi-region systems are active-passive; active-active requires conflict resolution                        |
| "GDPR just means encrypt the data"       | GDPR requires data to physically remain in the EU; region sharding is the architectural response                |
| "DNS failover is instant"                | DNS has TTL; Route53 health check failover takes 30-120s                                                        |
| "Spanner solves active-active conflicts" | Spanner provides strong consistency; you still design your application logic around it                          |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Split-Brain in Active-Active**
**Symptom:** Same record updated in two regions during replication lag; both updates committed; conflict detected on sync.
**Fix:** Conflict resolution policy: LWW (last-write-wins) or CRDT or application-level merge; explicit design, not afterthought.

**Mode 2: DNS Failover Too Slow (Long TTL)**
**Symptom:** Primary region down; clients still routing to primary for 5 minutes.
**Root Cause:** DNS TTL was 300s; health-check detected failure in 30s but DNS cache keeps old entry.
**Fix:** Reduce TTL to 30s for failover records; accept slightly higher DNS query load.

**Mode 3: Write Starvation on Remote Region (Active-Passive)**
**Symptom:** EU users experience 180ms write latency (writes go to us-east-1 cross-region).
**Fix:** If EU write latency is unacceptable: promote EU to active-active for non-conflicting domains; keep US as primary for conflict-sensitive operations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-006 - CAP Theorem]]
- [[DST-008 - Consistency Models]]
- [[DST-033 - Multi-Region Deployment]]

**Builds On This (learn these next):**

- [[DST-066 - Distributed System Architecture Strategy]]
- [[DST-072 - Distributed Transaction Theory]]

**Alternatives / Comparisons:**

- CockroachDB geo-partitioning (region sharding at DB level)
- Cloudflare Durable Objects (edge-native global distribution)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Strategy for writes, reads, failover|
|                 and consistency across regions      |
| PROBLEM         Low write latency + strong consist  |
| IT SOLVES       + no conflicts is impossible to     |
|                 achieve simultaneously globally     |
| KEY INSIGHT     Active-active: highest complexity;  |
|                 active-passive: simplest + safer    |
| USE WHEN        Service crosses geographic regions  |
| AVOID           Active-active without explicit      |
|                 conflict resolution design          |
| TRADE-OFF       Write latency vs conflict safety    |
| ONE-LINER       Choose: one primary or all primaries|
| NEXT EXPLORE    DST-066, DST-072, CockroachDB geo  |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Active-passive: one primary write region; simple; safe; higher write latency for remote regions.
2. Active-active: all regions accept writes; fast globally; requires explicit conflict resolution; rarely simple.
3. Data residency (GDPR): forces region sharding regardless of latency or simplicity preferences.

**Interview one-liner:**
"Global distribution strategy chooses between active-active (all regions accept writes; conflict resolution required), active-passive (one primary; replicas for reads; safest for financial data), and region sharding (users pinned to their region; mandatory for data sovereignty) — the choice depends on conflict tolerance, latency requirements, and compliance."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Before choosing an availability pattern, determine the
conflict model. If conflicts cannot be tolerated: choose
a design with one write path (single-primary). If
conflicts are resolvable: multiple write paths are
possible. This applies beyond global distribution: to
database replica selection, cache write strategies,
and distributed queue processing.

**Where else this pattern appears:**

- **Database read/write splitting** — writes to primary; reads from replica; same trade-off as active-passive
- **CDN cache invalidation** — active-passive with CDN: origin is primary; edges are read-only replicas
- **Multi-datacenter Redis** — Redis Cluster with cross-DC replication faces same active-active conflict risk

---

### 💡 The Surprising Truth

GMail experienced a global outage in 2009 when Google
deployed a new feature to one region, which caused
that region to start rejecting requests from other
regions — triggering a cascade that briefly took Gmail
down globally. Their active-active architecture, designed
for maximum availability, became a liability when
cross-region rejection logic caused all regions to
reject each other simultaneously. The lesson: active-
active systems have complex failure modes that active-
passive systems do not; the "higher availability" claim
of active-active assumes failures are independent,
but a shared bug creates correlated failures across
all regions simultaneously.

---

### 🧠 Think About This Before We Continue

**Q1 (Design Trade-off):** A social media company
wants to implement active-active globally for their
post-creation API. A user can post from any region.
The like count on a post must eventually reflect all
likes, regardless of which region received each like.
Design the conflict resolution strategy for the like
counter across regions.

_Hint:_ Like counter is a monotonically increasing number.
This is a CRDT G-Counter: each region maintains its own
counter for that post; global count = sum of all region
counters. No conflict possible; CRDT merges automatically.
User ID set (who liked) is a G-Set CRDT. No coordination needed.

**Q2 (Scale):** AWS Global Accelerator routes traffic
to the nearest healthy region. Describe the failure
cascade when us-east-1 fails for a service using Global
Accelerator active-passive to eu-west-1. What is the
RTO and what are the risks during failover?

_Hint:_ Global Accelerator: health check detects failure
in ~30s; routes traffic to eu-west-1. RTO: ~30-60s.
Risks during failover: (1) replication lag -> recent
us-east-1 writes may not be on eu-west-1 (RPO); (2)
eu-west-1 may not have full capacity for global traffic
(scale-out lag); (3) sticky sessions broken.

**Q3 (System Interaction):** A fintech startup processes
payments in the US and EU. GDPR requires EU payment
data stays in the EU. US payments may not go to EU
servers. They want 99.99% SLA. Design the global
distribution strategy, including how US and EU services
can share authentication (a user might travel from
US to EU).

_Hint:_ Region sharding for payment data (forced by GDPR).
Auth tokens: user can authenticate in either region;
JWT is stateless (no data transfer); token validation
does not expose payment data across regions. Auth
service: active-active (JWTs are stateless; no conflict).
Payment service: strictly region-sharded. 99.99% SLA:
requires multi-AZ within each region minimum.
