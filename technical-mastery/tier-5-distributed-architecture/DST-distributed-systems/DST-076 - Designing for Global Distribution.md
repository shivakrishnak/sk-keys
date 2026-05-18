---
id: DST-076
title: Designing for Global Distribution
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-011, DST-013, DST-059
used_on: []
related: DST-011, DST-013, DST-059, DST-066, DST-071, DST-078
tags:
  - distributed
  - global
  - multi-region
  - latency
  - data-locality
  - replication
  - architecture
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 76
permalink: /technical-mastery/distributed-systems/global-distribution/
---

⚡ TL;DR - Global distribution requires solving
three inter-dependent problems: latency (data must
be close to users), consistency (writes in one region
must propagate to others safely), and data residency
(regulations may prevent data from crossing borders);
the design space is: active-passive (one write region,
others read), active-active (writes everywhere,
conflict resolution required), or geo-partitioned
(each user's data lives in their home region, no
cross-region conflicts); most systems start with
active-passive and evolve to geo-partitioned as
regulatory and latency requirements tighten.

---

### 📋 Entry Metadata

| #076 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Consistent Hashing, MVCC, Consistency Levels | |
| **Used by:** | N/A (architectural pattern) | |
| **Related:** | Consistent Hashing, Consistency Levels, Spanner, Compliance and SLAs, Multi-Region Consistency | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A software company launches globally. They have one
US datacenter. A user in Tokyo gets 200ms latency
on every request (round-trip to US). They add a
Tokyo datacenter as a replica. Now Tokyo reads are
fast. But writes still go to the US (strong consistency:
replicate to all, single primary). Tokyo users have
fast reads, slow writes (submit order form: 300ms
round-trip to US + replication time).

Naively making Tokyo a write-accepting region creates
split-brain: both US and Tokyo accept writes for the
same user's account. Conflicting orders.

Global distribution requires intentional architecture:
choose the consistency model, data locality strategy,
and conflict resolution approach BEFORE adding regions.

---

### 📘 Textbook Definition

**Global distribution** in distributed systems:
the design of a system where data and computation
are physically located in multiple geographic regions
to reduce latency for users and increase availability.

**Three global distribution patterns:**

1. **Active-Passive (Primary-Replica):**
   One region accepts writes (primary). Others
   replicate (read-only replicas). Writes route to
   primary. Reads route to the nearest replica.

2. **Active-Active (Multi-Master):**
   Multiple regions accept writes. Conflict resolution
   required (LWW, CRDT, OCC). Higher availability.
   Higher complexity.

3. **Geo-Partitioned:**
   Each user's data is assigned to a "home region"
   and stays there. No cross-region data movement.
   Satisfies data residency. No conflicts (data isolated).
   Limitation: cross-region queries are slow or impossible.

---

### ⏱️ Understand It in 30 Seconds

```
CHOOSING YOUR GLOBAL DISTRIBUTION MODEL:

Q1: Do users need to write from multiple regions?
  No → Active-Passive (simple, strong consistency possible)
  Yes → Active-Active or Geo-Partitioned

Q2: Is data residency (GDPR etc.) required?
  Yes → Geo-Partitioned (user's data never leaves home
    region)
  No → Active-Active or Active-Passive with global
    replication

Q3: Can you tolerate conflicts from concurrent writes?
  No → Geo-Partitioned (no cross-region writes to same
    data)
  Yes → Active-Active (with CRDT or LWW conflict
    resolution)

LATENCY MATH:
  Speed of light: ~200ms round-trip US-Asia Pacific.
  With Active-Passive (writes to US from Tokyo):
    Write latency: 200ms (network) + processing = ~250ms.
  With Geo-Partitioned (writes to Tokyo region):
    Write latency: < 10ms.
  
  For a 100ms write latency target: Active-Passive
  with Tokyo primary is the only viable option.
```

---

### 🔩 First Principles Explanation

**ACTIVE-PASSIVE ARCHITECTURE:**

```
TOPOLOGY:
  us-east-1 (PRIMARY): accepts reads + writes.
  eu-west-1 (REPLICA): accepts reads; forwards writes to
    primary.
  ap-northeast-1 (REPLICA): same.

WRITE PATH:
  Tokyo user submits order.
  Request → ap-northeast-1 API servers.
  API servers → write to us-east-1 primary DB.
  (Synchronous write: 200ms round-trip)
  Primary replicates to ap-northeast-1 replica.
  (Async or synchronous: adds replication lag)
  API returns success to Tokyo user.

READ PATH:
  Tokyo user reads their order history.
  Request → ap-northeast-1 API servers.
  API servers → read from ap-northeast-1 replica.
  (Read: < 5ms local)
  User gets fast read.

FAILOVER:
  If us-east-1 primary fails:
    Promote eu-west-1 or ap-northeast-1 to primary.
    Update DNS to route writes to new primary.
    Resume writes (with possible replication lag gap).
    Replication lag = potential data loss window.
    RPO (Recovery Point Objective) = replication lag.

TRADE-OFFS:
  PRO: Strong consistency for reads (from primary).
    Simple conflict model (no conflicts; single writer).
  CON: Write latency for non-primary region users.
    Single primary = single point of write scalability.
    Failover takes time (minutes for DNS propagation).
```

**ACTIVE-ACTIVE ARCHITECTURE:**

```
TOPOLOGY:
  us-east-1: accepts reads + writes.
  eu-west-1: accepts reads + writes.
  ap-northeast-1: accepts reads + writes.

WRITE PATH:
  Tokyo user submits order → ap-northeast-1 accepts write.
  ap-northeast-1 replicates to other regions
    asynchronously.
  User gets fast write (< 10ms).

READ PATH:
  Tokyo user reads order → ap-northeast-1 returns it.
  Fast read (< 10ms).

CONFLICT SCENARIO:
  User A is in Tokyo. They update their profile
  from a mobile app AND from a web browser simultaneously.
  Mobile → ap-northeast-1: name = "Alice M."
  Web → eu-west-1 (VPN): name = "Alice Mayer"
  Both writes succeed locally (< 10ms each).
  Replication: both versions arrive at all nodes.
  CONFLICT: same key, different values, concurrent.

CONFLICT RESOLUTION OPTIONS:
  LWW (Last-Write-Wins): use timestamp.
    Cassandra default. Simplest. Risk: clock skew loses
      data.
  
  CRDT: for specific data types.
    G-Counter: sum across regions (no conflict).
    OR-Set: union (no conflict).
    LWW-Register: last write wins (per CRDT rules).
  
  OCC: return conflict to client.
    Client resolves. Only for low-frequency conflicts.
    
  Operation Transform (OT): for text collaboration.
    Google Docs approach. Transforms concurrent edits
    so they are compatible when applied in any order.
  
PRODUCTION ACTIVE-ACTIVE:
  Cassandra: LWW by default (simple, risk of data loss).
  Dynamo: vector clocks + client-side merge.
  CockroachDB: active-active with serializable
    isolation using HLC timestamps.
  Google Spanner: active-active with TrueTime for
    external consistency (single global ordering).
```

**GEO-PARTITIONED ARCHITECTURE:**

```
TOPOLOGY:
  Each user is assigned a "home region" at signup:
    EU users → eu-west-1 cluster.
    US users → us-east-1 cluster.
    APAC users → ap-northeast-1 cluster.

WRITE PATH:
  Tokyo user → ap-northeast-1 only.
    No cross-region write. No conflict.
    < 5ms write latency.

READ PATH:
  Tokyo user → reads from ap-northeast-1 only.
    < 5ms read latency.

DATA RESIDENCY:
  EU user data NEVER leaves eu-west-1.
  GDPR compliant by construction.

CROSS-REGION QUERIES:
  "Show me all orders from US users AND EU users in 2024."
  PROBLEM: EU data is in eu-west-1, US data is in
    us-east-1.
  To answer: query both clusters. Join in application.
  LATENCY: high (cross-region network).
  ALTERNATIVE: pre-aggregate into a global analytics
    cluster with anonymized/pseudonymized data
    (GDPR allows analytics on anonymized data).

USER MOVES REGION:
  EU user moves to US.
  Data migration: copy EU data to US cluster.
  Delete from EU cluster.
  Reassign home region to US.
  COMPLEXITY: migrations require careful execution.

COMPANIES USING THIS:
  Stripe: geo-partitioned by customer.
  Notion: home region per workspace.
  AWS DynamoDB Global Tables: regional item tables
    with cross-region replication but per-region writes
    for low-latency.
```

**LATENCY BUDGET FOR GLOBAL SYSTEMS:**

```
RULE: Each user request has a latency budget.
  Budget = target P99 latency - local processing time.
  Remainder = available for network round-trips.

EXAMPLE:
  SLO: 200ms P99 for checkout.
  Local processing: 50ms.
  Available for network: 150ms.
  
  Speed of light (one-way): ~65ms US to EU.
  Round-trip: ~130ms.
  Available - round-trip: 150ms - 130ms = 20ms margin.
  
  With Active-Passive (US primary, EU user):
    Write route: EU → US (130ms) + processing (50ms) =
      180ms.
    Still within 200ms budget? YES (barely).
    But: add queuing, jitter, retry: often exceeds 200ms.
    
  Solution: active-active or geo-partitioned.
  Or: increase the write SLO (300ms is acceptable for
    checkout?).

NETWORK DISTANCES (approximate round-trip):
  US East - EU West:  130ms
  US East - APAC:     300ms
  EU West - APAC:     280ms
  US East - US West:   70ms
  US East - Brazil:   160ms
```

---

### 🧠 Mental Model / Analogy

> Global distribution is like choosing a restaurant
> franchise model. Active-Passive: one central kitchen
> (primary), regional delivery points (replicas).
> Food is always fresh from the central kitchen.
> But delivery to far regions takes time (write latency).
> Active-Active: multiple kitchens, each serving
> their region directly. Fast service everywhere.
> But if two kitchens prepare the same dish differently
> (conflict), you need a recipe reconciliation process.
> Geo-Partitioned: each kitchen only serves its local
> region. No delivery, no conflicts. But you can't
> combine orders from different regions.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The core trade-off:**
Close data = low latency. But synchronizing close
data across regions = consistency challenges.
More regions = more coordination cost.

**Level 2 - Active-passive is the safe default:**
One primary, multiple replicas. Writes are slow for
far users (route to primary). Reads are fast. No
conflicts. Good starting point for most systems.

**Level 3 - Active-active unlocks write performance globally:**
At the cost of conflict resolution complexity. Works
well for data types with natural merge semantics
(CRDTs, LWW for non-critical fields). Avoid for
financial or inventory data where conflicts are
unacceptable.

**Level 4 - Geo-partitioned solves both latency and compliance:**
When data residency is required AND write latency
matters, geo-partitioned is the right architecture.
The trade-off: cross-region queries require special
handling. Analytics must use a separate global
pipeline.

**Level 5 - The hard part is migration:**
Most systems start as single-region, become active-
passive, and evolve toward geo-partitioned over years.
Each migration is a large engineering project. The
design choice at the beginning constrains the options
years later. Choosing the wrong model at the start
creates technical debt that costs millions to unwind.
Design for the global architecture you'll need in
3 years, not just today.

---

### 💻 Code Example

**Geo-Partitioned Request Router**

```python
# Router: directs requests to the correct region
# based on user's home_region.

from functools import lru_cache
from enum import Enum

class Region(str, Enum):
    US_EAST = "us-east-1"
    EU_WEST = "eu-west-1"
    AP_NORTHEAST = "ap-northeast-1"

# Region to cluster endpoint mapping:
REGION_ENDPOINTS = {
    Region.US_EAST:     "https://db-us-east.internal",
    Region.EU_WEST:     "https://db-eu-west.internal",
    Region.AP_NORTHEAST: "https://db-ap-ne.internal",
}

def get_user_region(user_id: str) -> Region:
    """
    Look up the user's home region from a fast
    key-value store (e.g., Redis or in-memory cache).
    This lookup must be fast and in the local region.
    """
    # In practice: cache user_id→region in Redis
    # with long TTL (24h). Invalidate on region change.
    region_str = user_region_cache.get(user_id)
    if not region_str:
        # Fallback: look up from the global user index
        # (a lightweight service that only stores
        # user_id → home_region mappings)
        region_str = global_user_index.get_region(user_id)
        user_region_cache.set(user_id, region_str, ttl=86400)
    return Region(region_str)


def get_db_for_user(user_id: str):
    """
    Returns the database connection for the user's
    home region. Data for this user only lives there.
    """
    region = get_user_region(user_id)
    endpoint = REGION_ENDPOINTS[region]
    return get_db_connection(endpoint)


# Usage in API handler:
def get_user_orders(user_id: str, limit: int = 20):
    db = get_db_for_user(user_id)
    # This query runs locally in the user's home region.
    # < 5ms latency.
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id = %s "
        "ORDER BY created_at DESC LIMIT %s",
        (user_id, limit)
    )
    return orders

# CROSS-REGION QUERY (analytics):
def get_all_orders_for_date(date: str):
    """
    Fetch orders from all regions for a date.
    WARNING: this is slow (cross-region network calls).
    For production: pre-aggregate into a global
    analytics store (BigQuery, Redshift) via CDC.
    """
    results = []
    for region in Region:
        db = get_db_connection(REGION_ENDPOINTS[region])
        region_orders = db.execute(
            "SELECT * FROM orders WHERE DATE(created_at) = %s",
            (date,)
        )
        results.extend(region_orders)
    # Merge and sort:
    results.sort(key=lambda o: o["created_at"])
    return results
    # In production: run this in the background, cache result.
```

---

### ⚖️ Comparison Table

| Architecture | Write Latency | Read Latency | Conflicts | Data Residency | Best For |
|---|---|---|---|---|---|
| **Active-Passive** | High for non-primary regions | Low (read from nearest replica) | None | Possible with replication config | Simple systems, strong consistency |
| **Active-Active** | Low (write to nearest region) | Low | Must resolve | Harder (data moves between regions) | High availability, eventually consistent |
| **Geo-Partitioned** | Low (write to home region) | Low | None (data isolated) | Native compliance | GDPR use cases, financial services |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Active-Active means all regions are always consistent" | Active-Active means all regions accept writes. Consistency depends on the replication and conflict resolution strategy. Most active-active systems are eventually consistent. Strong consistency across regions requires expensive coordination (e.g., Spanner). |
| "Geo-partitioned is less available than active-active" | Geo-partitioned is more available for single-user operations (data is local). It's less available for cross-region queries. The trade-off: if your SLA is per-user, geo-partitioned is excellent. |
| "You can add multi-region later" | Adding multi-region to a single-region system requires: schema changes (add region sharding key), data migration, routing changes, and conflict resolution design. Retrofitting is expensive. Design for the topology you'll need in 3 years. |
| "CDN solves global distribution" | CDN solves global read latency for static content and cacheable API responses. It does not solve write latency, data residency for mutable data, or database query distribution. CDN is a complement, not a substitute, for multi-region database architecture. |

---

### 🚨 Failure Modes & Diagnosis

**Region Failover Creates Data Loss (Active-Passive)**

**Symptom:** After failover from us-east-1 to eu-west-1,
some recent orders are missing. Users report orders
they placed successfully are not in their history.

**Root Cause:** Asynchronous replication between
us-east-1 and eu-west-1. At the time of failover,
eu-west-1 was 45 seconds behind us-east-1. All
transactions in that 45-second window were lost.
The RPO (Recovery Point Objective) was not 0 - but
the team assumed it was.

**Diagnosis:**
```sql
-- After failover: compare the new primary's last event
-- time with the failed primary's last event time.
-- (If you have event sourcing or CDC):
SELECT MAX(created_at) FROM orders;
-- On new primary (eu-west-1): 2024-01-15 14:37:32
-- On original primary (us-east-1 in log backup):
--   2024-01-15 14:38:17
-- Gap: 45 seconds. All orders in that window = lost.

-- PREVENTION:
-- Measure replication lag BEFORE failing over:
SELECT NOW() - pg_last_xact_replay_timestamp()
  AS replication_delay
FROM (-- on replica) pg_stat_replication;
-- If lag > acceptable RPO: delay failover, or accept
-- data loss, or use synchronous replication (higher
-- write latency but zero lag).
```

**Fix:** Use synchronous replication for the failover
replica (accept higher write latency). Or: implement
a binlog-based recovery process that replays missed
transactions from the failed primary's WAL log
(requires that WAL is still accessible after failure).

---

### 🔗 Related Keywords

**Prerequisites:** `Consistent Hashing` (DST-011),
`MVCC` (DST-013),
`Consistency Levels` (DST-059)

**Related:** `Spanner and TrueTime` (DST-066),
`Compliance and SLAs` (DST-071),
`Multi-Region Consistency Strategy` (DST-078)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ACTIVE-PASSIVE  │ One write region, low complexity      │
│                 │ Write latency for remote users        │
│ ACTIVE-ACTIVE   │ All regions write, conflicts possible │
│                 │ Low write latency everywhere          │
│ GEO-PARTITIONED │ User data stays in home region        │
│                 │ No conflicts; GDPR compliant          │
├─────────────────────────────────────────────────────────┤
│ LATENCY RULE    │ US-EU: ~130ms RT / US-APAC: ~300ms RT │
│ NETWORK BUDGET  │ Target P99 - local processing         │
│                 │ = available for cross-region hops     │
├─────────────────────────────────────────────────────────┤
│ DESIGN EARLY    │ Retrofitting multi-region is          │
│                 │ expensive. Design for 3-year horizon. │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The decision between active-passive, active-active,
and geo-partitioned is not a technical choice but
a product choice with technical implications. It
is driven by: who are your users (geographic
distribution), what do they do (read-heavy vs write-
heavy), what are your legal obligations (data
residency), and what is your availability SLA
(is 2-minute failover acceptable?). The technical
architecture follows from the answers to these
product questions. Engineers who jump directly to
"we need active-active globally" without answering
these questions often build a more complex system
than they need, with all the operational costs of
conflict resolution and cross-region coordination
for a product that could have been served by a
simpler active-passive model with a well-placed
primary region.

---

### 💡 The Surprising Truth

The speed of light is the fundamental constraint
on global distribution. Light travels approximately
200km per millisecond in a fiber optic cable.
The physical distance between New York and Tokyo
is approximately 10,800km. The minimum round-trip
time via the shortest fiber path (not the actual
path) is 10,800 / 200 * 2 = 108ms. The actual
measured RTT is typically 165-200ms due to fiber
routing (cables don't go in straight lines), routing
equipment latency, and queuing. No software design
can improve on the speed of light. The only way
to serve a Tokyo user with sub-10ms write latency
is to have a write-accepting database server in
or near Tokyo. This is not a software engineering
problem; it is a physics problem with a real estate
solution: put servers in the right geographic
locations.

---

### ✅ Mastery Checklist

1. [CHOOSE] For a fintech app with EU and US users:
   GDPR requires EU data to stay in EU. Writes must
   be < 50ms globally. Which global distribution
   model? Justify.
2. [CALCULATE] A user in Sydney wants to submit a
   form that requires a write to a Sydney-nearest
   database. The app is currently Active-Passive with
   the primary in us-east-1. What is the minimum
   write latency achievable? Is this below 200ms?
3. [DESIGN] An Active-Active system with US and EU
   regions. A user updates their email simultaneously
   from two devices (one in each region). Both writes
   succeed. How does the system detect and resolve
   this conflict? What model do you use?
4. [MIGRATE] Describe the steps to migrate a single-
   region Active-Passive system (US primary, EU replica)
   to a Geo-Partitioned system where EU users' data
   lives only in eu-west-1.
5. [AUDIT] Review your current system. Which global
   distribution model does it use (or should it use
   if currently single-region)? What is the expected
   write latency for a user in the region farthest
   from the primary?
