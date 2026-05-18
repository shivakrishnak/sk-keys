---
id: DST-070
title: Production Incident Simulation
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-069
used_by: []
related: DST-007, DST-033, DST-055, DST-056, DST-069
tags:
  - distributed
  - production
  - incident-simulation
  - case-study
  - meta
  - diagnosis
  - cascading-failure
  - split-brain
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/distributed-systems/production-incident-simulation/
---

⚡ TL;DR - This entry walks through three simulated
production incidents to practice the DST-069
diagnosis framework; Incident 1: cascading failure
from DB connection pool exhaustion (root cause: slow
query holding connections); Incident 2: split-brain
after network partition (root cause: two leaders
accepting writes to the same key range); Incident 3:
data inconsistency from stale replica reads after a
deploy (root cause: read replicas lagging on heavy
index rebuild); each incident follows the full arc
from alert to root cause to fix.

---

### 📋 Entry Metadata

| #070 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Production Diagnosis Toolkit | |
| **Used by:** | N/A (simulation/learning entry) | |
| **Related:** | Cascading Failures, Circuit Breakers, Observability, Production Diagnosis | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers read about cascading failures, split-brain,
and stale reads in theory. On-call is the first time
they apply this knowledge under time pressure, at
2 AM, with a real outage affecting real users. Mistakes
are made because the knowledge was theoretical, not
practiced. Structured incident simulations convert
theoretical knowledge into muscle memory.

This entry is a simulation - work through each
incident as if you are the on-call engineer.
Read the alert and symptoms, formulate a diagnosis,
then read the walkthrough. Repeat until the
framework is reflexive.

---

### 📘 Textbook Definition

**Incident simulation (game day):** a practice exercise
where engineers work through a realistic failure
scenario to test their diagnosis skills, runbooks,
and tooling without real production impact.

This entry uses three real-world failure archetypes:
1. Cascading failure from DB pool exhaustion
2. Split-brain from network partition
3. Stale read from replica lag after deploy

Each incident is parameterized with realistic metrics,
log excerpts, and trace patterns.

---

### ⏱️ Understand It in 30 Seconds

```
THREE INCIDENTS:

INCIDENT 1: CASCADING FAILURE
  Alert: order-service P99 > 5000ms, errors 12%.
  Root: slow DB query on orders table after deploy.
  Pattern: slow dep → connections held → pool
    exhausted → errors cascade to upstream services.
  Fix: rollback deploy; add index; connection timeout.

INCIDENT 2: SPLIT-BRAIN
  Alert: data-inconsistency alert fires.
  Root: network partition → two Raft leaders
    accepted writes to overlapping key ranges.
  Pattern: partition → dual leader → conflicting writes.
  Fix: fencing + STONITH; force one leader to step down.

INCIDENT 3: STALE READS AFTER DEPLOY
  Alert: users report seeing "old" data after writing.
  Root: heavy index rebuild on primary during deploy →
    replica lag spikes to 90+ seconds → reads from
    replica return stale data.
  Pattern: schema change → replica lag → stale reads.
  Fix: route reads to primary during schema migrations;
    monitor replication lag.
```

---

### 🔩 First Principles Explanation

---

**INCIDENT 1: CASCADING FAILURE FROM DB POOL EXHAUSTION**

**ALERT (02:37 AM):**
```
PagerDuty: order-service P99 > 5000ms [CRITICAL]
PagerDuty: order-service error rate > 10% [CRITICAL]
```

**STEP 1 - ORIENT: What changed in the last 30 min?**
```bash
kubectl rollout history deployment --all-namespaces | \
  grep -v "<none>"
# Output:
# NAMESPACE  NAME             REVISION  STATUS
# prod       order-service    14        complete
# prod       order-service    13        complete
# (deployed revision 14 at 02:24 AM - 13 minutes ago)
```

Hypothesis: deploy caused this.

**STEP 2 - CLASSIFY SYMPTOM:**
P99 spike + error rate up. This is Error Rate + Latency.
Check if errors are "connection" or "timeout" type.

```bash
grep "ERROR" /var/log/order-service/app.log | \
  grep -E "2:3[0-9]:" | head -20
# 02:37:14 ERROR: HikariPool-1 - Connection is not
#   available, request timed out after 30000ms.
# 02:37:14 ERROR: HikariPool-1 - Connection is not
#   available, request timed out after 30000ms.
```

Connection pool exhaustion. All 50 pool connections
are in use. New requests wait 30 seconds then fail.

**STEP 3 - TRACES: What is holding connections?**
```
Jaeger: order-service request trace
  [order-service] POST /api/orders         8421ms
    [order-service → db] INSERT orders      8390ms  ← SLOW
    [order-service → inventory] PUT ...       12ms
  
  Span detail: db INSERT orders - 8390ms
  SQL: INSERT INTO orders (...) ON CONFLICT UPDATE ...
  Execution plan: SEQUENTIAL SCAN on orders (n=2.1M rows)
```

Sequential scan on insert. After the deploy, the query
plan changed. The deploy added a new column to orders
table. The INSERT now triggers an update on a column
that lacks an index. Seq scan on 2.1M rows = 8 seconds.

**STEP 4 - ROOT CAUSE:**
```
Deploy at 02:24 added column `shipping_zone` to orders.
The INSERT ... ON CONFLICT UPDATE shipping_zone
triggers a table scan to find conflicting rows.
The conflict check was always there but with 2.1M
rows accumulating, the seq scan is now 8 seconds.
Previously: 0.2M rows → 0.3s → not noticed.
After growth: 2.1M rows → 8s → connection pool fills.
```

**MITIGATION:**
```bash
# 1. Rollback deploy (fastest mitigation):
kubectl rollout undo deployment/order-service -n prod

# 2. Monitor: P99 should drop within 5 minutes of rollback.
watch -n5 'curl -s http://prometheus:9090/api/v1/query \
  --data-urlencode "query=histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket
  {service=\"order-service\"}[1m]))" | jq ".data"'

# 3. Add index (permanent fix, next deploy):
CREATE INDEX CONCURRENTLY idx_orders_shipping_zone
  ON orders(shipping_zone);
```

---

**INCIDENT 2: SPLIT-BRAIN FROM NETWORK PARTITION**

**ALERT (11:14 PM):**
```
PagerDuty: data-consistency-check FAILED [CRITICAL]
  "Account balance read from service-A != service-B"
PagerDuty: raft-cluster dual-leader detected [CRITICAL]
```

**STEP 1 - ORIENT: What changed in the last 30 min?**
```bash
kubectl get events --sort-by=.lastTimestamp -n prod | \
  grep -E "Network|Node"
# 23:08: Node node-3 NetworkNotReady
# 23:09: Node node-3 NetworkReady
```

Network blip on node-3 at 23:08. But it recovered.

**STEP 2 - CLASSIFY SYMPTOM:**
Data inconsistency + dual-leader alert. This is
split-brain pattern.

**STEP 3 - TOPOLOGY CHECK: Is there a dual leader?**
```bash
etcdctl endpoint status --write-out=table \
  --endpoints=node1:2379,node2:2379,node3:2379
# +------------+---------+--------+---------+-----------+
# |  ENDPOINT  |   ID    |VERSION | DB SIZE |  LEADER   |
# +------------+---------+--------+---------+-----------+
# | node1:2379 | abc123  |  3.5.1 |  22 MB  | node1:2379|  ← leader
# | node2:2379 | def456  |  3.5.1 |  22 MB  | node1:2379|
# | node3:2379 | ghi789  |  3.5.1 |  22 MB  | node3:2379|  ← also
# leader?
# +------------+---------+--------+---------+-----------+
```

node-3 believes it is the leader. node-1 also
believes it is the leader. During the network blip:
node-3 was isolated from node-1 and node-2. node-3
initiated a new election (didn't receive heartbeat),
elected itself. When the network recovered: two
leaders. Both accepted writes.

**STEP 4 - DAMAGE ASSESSMENT:**
```bash
# Find all writes during the split-brain window:
# (23:08 to 23:14 - 6 minute window)
etcdctl get / --prefix --write-out=json \
  --rev=REVISION_AT_23:08 | \
  jq '.kvs[] | select(.mod_revision > MOD_REV_THRESHOLD)'
# Returns: all keys modified during the split-brain.
# Check for keys modified on node-1 AND node-3.
# Conflicting keys = data loss or inconsistency.
```

**MITIGATION:**
```bash
# 1. Force node-3 to step down:
etcdctl move-leader node1_id \
  --endpoints=node3:2379
# node-3 steps down. node-1 becomes sole leader.

# 2. Verify single leader:
etcdctl endpoint status --write-out=table
# All nodes should report same leader.

# 3. Audit inconsistent keys:
# Compare account balances from node-1 history
# vs node-3 history during the window.
# For each conflicting key: use application-level
# resolution (e.g., max balance, or reconstruct
# from transaction log).

# 4. Long-term fix: Raft leader lease + fencing.
# Ensure node-3 does not accept writes after
# its lease expires on partition.
# etcd already has this; check:
# --election-timeout vs --heartbeat-interval
# election_timeout must be > 10x heartbeat_interval
# to prevent false elections on transient blips.
```

---

**INCIDENT 3: STALE READS AFTER DEPLOY**

**ALERT (3:15 PM, business hours):**
```
PagerDuty: user-reported data inconsistency [HIGH]
  "Users updating profile see old data on next read"
  Engineering: writes succeed (200 OK), reads return
    previous values.
```

**STEP 1 - ORIENT: What changed recently?**
```bash
kubectl rollout history deployment/user-service -n prod
# REVISION 22 at 15:03 PM: "add full-text search index
#   on user profiles"
```

Schema migration in revision 22 added a full-text
index on the profiles table.

**STEP 2 - CLASSIFY SYMPTOM:**
Successful writes but stale reads. Classic stale read
pattern: replica lag.

**STEP 3 - CHECK REPLICATION LAG:**
```bash
# PostgreSQL replication lag:
psql -h primary -c "
  SELECT
    client_addr,
    state,
    sent_lsn - write_lsn AS write_lag,
    sent_lsn - flush_lsn AS flush_lag,
    sent_lsn - replay_lsn AS replay_lag,
    write_lag,
    flush_lag,
    replay_lag
  FROM pg_stat_replication;
"
# Output:
# client_addr | state  | replay_lag
# 10.0.0.12   | streaming | 00:01:34.218
# 10.0.0.13   | streaming | 00:01:28.441
```

Replicas are 90+ seconds behind. Any read from a
replica will see data that is at least 90 seconds old.
Since the full-text index creation on profiles table
is running on the primary: heavy WAL generation.
Replicas cannot keep up with the WAL flood.

**ROOT CAUSE:**
```
CREATE INDEX CONCURRENTLY idx_profiles_fulltext
  ON profiles USING GIN(to_tsvector('english', bio));

This command on the primary:
  Scans entire profiles table (100M rows).
  Builds GIN index.
  Generates massive WAL volume.
  
Replicas apply WAL sequentially.
The WAL flood from the index build overwhelmed
the replica apply capacity.
Replica lag = 90+ seconds.
User writes to primary. User reads from replica.
Replica lag > user action time → stale read.
```

**MITIGATION:**
```bash
# 1. Route user reads to PRIMARY immediately:
# In application load balancer or DB connection pool:
# Remove read replicas from read pool until lag < 5s.

# Application-level (Spring/HikariCP):
# data-source.hikari.read-only=false
# (disable read-only routing to force primary reads)

# 2. Monitor lag recovery:
watch -n5 'psql -h primary -c "
  SELECT client_addr,
    extract(epoch from replay_lag)::int AS lag_seconds
  FROM pg_stat_replication;"'

# 3. Long-term: run schema migrations off-peak.
# And test replication lag impact in staging first.
# Index creation on large tables generates WAL proportional
# to table size. Always test:
#   CREATE INDEX CONCURRENTLY ... -- in staging
# Measure: how much WAL, how much replica lag.
```

---

### 🧠 Mental Model / Analogy

> Think of each incident as a medical case study.
> The alert is the symptom (fever, chest pain).
> The classification step is triage (is this cardiac
> or respiratory?). The trace is the physical exam
> (which organ is involved?). The log is the
> diagnostic test (what exactly is wrong?). The
> topology check is the imaging (is there a structural
> problem - network partition, dual leader?). And
> mitigation is treatment - stop the bleeding first,
> understand the cause second. Practicing on simulated
> cases builds the pattern recognition that makes
> real incidents resolve faster.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Pattern recognition:**
The three incidents illustrate three patterns:
slow dependency, dual leader, and stale reads.
Each pattern has a distinct fingerprint in metrics.

**Level 2 - The cascade amplifier:**
In Incident 1, the root cause (slow query) was not
new - the query existed before. The blast radius
grew because connection pool exhaustion turned a
latency issue into an error rate crisis. The cascade
was the amplifier: a slow service became a failing
service once the pool filled.

**Level 3 - Raft partitions need election tuning:**
Incident 2 happened because the election timeout
was too short for the network blip duration. The
blip was 1 second; the election timeout was also
~1 second. Increasing election timeout to 5-10x
the expected blip duration prevents false elections.

**Level 4 - Schema changes have infrastructure consequences:**
Incident 3 shows that a DDL operation (CREATE INDEX)
is not isolated to the database. It generates WAL
that overwhelms replicas, causing application-visible
inconsistency. Engineers must understand the
infrastructure ripple effects of database operations.

**Level 5 - Mitigation first, always:**
In all three incidents: the correct action is
mitigation before root cause. Rollback the deploy
(Incident 1). Force step-down on the extra leader
(Incident 2). Route reads to primary (Incident 3).
Root cause analysis happens after the blast radius
is contained.

---

### 💻 Code Example

**Chaos Test: Simulate Slow DB Query**

```python
# Fault injection to reproduce Incident 1 (slow DB query)
# Use Toxiproxy to inject latency on the DB connection.

# Toxiproxy: lightweight TCP proxy for fault injection.
# Docs: https://github.com/shopify/toxiproxy

import requests

TOXIPROXY_URL = "http://localhost:8474"

def create_db_proxy(
    upstream_host: str = "db:5432",
    proxy_port: int = 5433
) -> str:
    """Create a proxy in front of the database."""
    resp = requests.post(
        f"{TOXIPROXY_URL}/proxies",
        json={
            "name": "db-proxy",
            "listen": f"0.0.0.0:{proxy_port}",
            "upstream": upstream_host,
            "enabled": True
        }
    )
    resp.raise_for_status()
    return f"localhost:{proxy_port}"


def inject_latency(latency_ms: int = 8000):
    """Inject latency to simulate slow query scenario."""
    resp = requests.post(
        f"{TOXIPROXY_URL}/proxies/db-proxy/toxics",
        json={
            "name": "slow-query",
            "type": "latency",
            "attributes": {"latency": latency_ms},
            "toxicity": 1.0  # 100% of connections
        }
    )
    resp.raise_for_status()
    print(f"Injected {latency_ms}ms latency on DB connections")


def remove_latency():
    """Remove the injected latency."""
    requests.delete(
        f"{TOXIPROXY_URL}/proxies/db-proxy/toxics/slow-query"
    )
    print("Removed DB latency injection")


# To reproduce Incident 1:
# 1. Create the proxy:
proxy_addr = create_db_proxy()
# 2. Configure your app to connect to proxy_addr
#    instead of db:5432
# 3. Inject 8-second latency:
inject_latency(8000)
# 4. Send requests to order-service
# 5. Observe: connection pool fills up (50 connections,
#    each held for 8 seconds = ~6 req/second before exhaustion)
# 6. Observe: requests start timing out with
#    "HikariPool Connection not available" errors
# 7. Remove the fault:
remove_latency()
# 8. Observe: system recovers
```

---

### ⚖️ Comparison Table

| Incident | Alert Fingerprint | Root Cause Pattern | Mitigation | Permanent Fix |
|---|---|---|---|---|
| **#1 Cascading failure** | P99 spike + connection pool exhaustion errors | Slow dep held connections until pool saturated | Rollback deploy | Add index; add query timeout |
| **#2 Split-brain** | Dual-leader alert + data inconsistency | Network blip triggered false election; two leaders accepted writes | Force step-down on extra leader | Increase election timeout; add fencing |
| **#3 Stale reads** | Write success + stale read; after schema migration | Heavy DDL on primary flooded WAL; replicas lagged 90s | Route reads to primary | Schema changes off-peak; monitor WAL during migrations |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Rollback always fixes the problem" | Rollback removes the change that introduced the problem. But the problem may persist (e.g., data inconsistency from split-brain writes). Rollback is the mitigation; data repair is a separate step. |
| "Connection pool exhaustion = add more connections" | The pool is exhausted because existing connections are held too long (by slow queries or locked transactions). Adding connections overloads the database further. Fix the slow query; the pool will free up. |
| "Replication lag is always a database problem" | Heavy DDL operations (adding indexes, altering columns on large tables) generate WAL proportional to the operation size. The lag can be caused by application-triggered operations, not DB infrastructure failure. Always check if a schema migration is in progress when you see replica lag. |
| "After the network partition heals, Raft auto-resolves split-brain" | Raft is designed to prevent split-brain (leader uniqueness is guaranteed by the algorithm). But edge cases exist: a stale leader may not have received the new term election result if its network was partially restored. Always verify leader count after a partition heals. |

---

### 🚨 Failure Modes & Diagnosis

**Slow Recovery After Connection Pool Exhaustion**

**Symptom:** After rolling back the bad deploy, the
service continues to report errors. Error rate is
decreasing but P99 is still high. Recovery is slow.

**Root Cause:** The connection pool is still full.
Even after rollback, the in-flight requests that
were waiting for connections are still queued.
They hold the pool slots until they timeout or succeed.
The 30-second HikariCP timeout means recovery takes
up to 30 seconds per queued request.

**Diagnosis:**
```java
// Check current pool state via Spring Actuator:
// GET http://service:8080/actuator/metrics/hikaricp.connections
// hikaricp.connections.active (should be near 0 after recovery)
// hikaricp.connections.pending (requests waiting for conn)
// hikaricp.connections.timeout (# of timeouts since start)

// In JVM logs:
// tail -100 /var/log/app/app.log | grep HikariPool
// Look for: connection acquired, connection returned.
// If acquired >> returned: leak or long-held connections.
```

**Fix:** After rollback: if recovery is slow, restart
the service (drops all connections, starts fresh pool).
This is acceptable because the bad code is gone.
Monitor: P99 should drop to baseline within 60 seconds
of restart. If not: the slow query may still be in
the codebase (check if rollback was successful).

---

### 🔗 Related Keywords

**Prerequisites:** `Production Diagnosis Toolkit` (DST-069)

**Related:** `Cascading Failures` (DST-007),
`Circuit Breakers` (DST-033),
`Observability` (DST-055)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ INCIDENT 1 │ CASCADING FAILURE                         │
│ Root: slow query → pool exhaustion → cascade         │
│ Fix: rollback + add index                            │
├─────────────────────────────────────────────────────────┤
│ INCIDENT 2 │ SPLIT-BRAIN                               │
│ Root: partition → false election → dual leader       │
│ Fix: force step-down + increase election timeout     │
├─────────────────────────────────────────────────────────┤
│ INCIDENT 3 │ STALE READS FROM REPLICA LAG             │
│ Root: heavy DDL → WAL flood → replica lagging 90s   │
│ Fix: route reads to primary + off-peak migrations   │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Each of these three incidents shares a common meta-
pattern: a localized event (slow query, network blip,
schema change) had consequences that extended far
beyond its origin. The slow query affected the
connection pool, which affected all service requests.
The network blip triggered a false election, which
caused data inconsistency in an unrelated data store.
The index build affected replication lag, which
affected user-facing reads. This is the nature of
distributed systems: there is no true isolation.
Every component is coupled to every other component
through shared resources (connection pools, network,
WAL replication). The skill of a distributed systems
engineer is understanding these coupling paths in
advance and designing circuit breakers, timeouts,
and fallbacks at each coupling boundary. The incidents
above could all have been less severe if: (1) query
timeouts were enforced so slow queries didn't hold
pool slots, (2) election timeout was tuned to prevent
false elections, (3) reads were automatically routed
to primary when replica lag exceeded a threshold.
Each lesson is a design decision that should be
made proactively, not reactively.

---

### 💡 The Surprising Truth

In practice, most production incidents are not new
failures - they are old failures whose conditions
were finally met. The slow query in Incident 1 was
always slow on large tables; the table just wasn't
large enough to cause problems until this deploy.
The Raft election timeout was always borderline
for the network blip duration; the blip just happened
to fall inside the window. The replica lag from
heavy DDL was always possible; this was just the
first time a large enough table had an index added.
This is why post-mortems ask: "why did this happen
NOW?" not just "why did this happen?" The "why now"
question reveals the threshold that was crossed:
table size, traffic level, timing. Understanding
thresholds helps you prevent the next incident by
monitoring for approaches to those thresholds.
Anomaly detection on "table growth rate approaching
slow-query threshold" or "election timeout approaching
expected max blip duration" can prevent the incident
entirely.

---

### ✅ Mastery Checklist

1. [SIMULATE] Run Incident 1 in a local environment
   using Toxiproxy to inject 8-second DB latency.
   Watch the connection pool fill up. Then remove
   the latency and observe recovery. How long does
   recovery take?
2. [CONFIGURE] Set your Raft/etcd cluster's election
   timeout to 5x the maximum expected network blip
   duration. What is the trade-off? How does this
   affect leader election speed under a real failure?
3. [MONITOR] Add a replication lag alert to your
   monitoring: alert if replica lag > 30 seconds.
   What is the correct threshold for your workload?
   What is the mitigation if the alert fires?
4. [DESIGN] A service that reads from a read replica
   for performance. Add an automatic fallback: if
   replica lag > 10s, route reads to primary. How
   do you implement this in the connection pool
   or load balancer?
5. [PRACTICE] Using the DST-069 framework, work
   through all three incidents without reading the
   walkthrough first. Record your diagnosis steps.
   Then compare with the walkthrough. Where did
   your path diverge? What would you do differently?
