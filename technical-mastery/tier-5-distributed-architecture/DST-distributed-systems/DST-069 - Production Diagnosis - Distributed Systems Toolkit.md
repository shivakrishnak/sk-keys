---
id: DST-069
title: Production Diagnosis - Distributed Systems Toolkit
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-055, DST-056
used_by: []
related: DST-007, DST-033, DST-055, DST-056
tags:
  - distributed
  - production
  - diagnosis
  - incident-response
  - debugging
  - observability
  - runbook
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 69
permalink: /technical-mastery/distributed-systems/production-diagnosis-toolkit/
---

⚡ TL;DR - The distributed systems production
diagnosis framework follows a strict order: metrics
first (which symptom - error rate, latency P99, or
saturation), then traces (which service in the call
chain), then logs (which error at which timestamp),
then topology (which nodes/partitions are involved);
common patterns are: network partition - split-brain,
overloaded dependency - connection pool exhaustion,
slow downstream - cascading latency, clock skew -
ordering anomalies; and the most productive first
question is always "what changed in the last 30
minutes?"

---

### 📋 Entry Metadata

| #069 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Observability, Performance Tuning | |
| **Used by:** | N/A (operational runbook) | |
| **Related:** | Cascading Failures, Circuit Breakers, Observability, Performance Tuning | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Alert fires at 2 AM. P99 latency went from 50ms
to 8,000ms. Engineers scatter: one checks the
database, one checks the cache, one checks recent
deploys, one opens the dashboards and cannot
determine causality from 50 overlapping time series.
Thirty minutes of parallel investigation with no
coordination. Someone finds the cause by luck.
The wrong service was restarted twice. The incident
lasted 2 hours because there was no shared framework
for narrowing from "something is wrong" to "exactly
this component failed in exactly this way."

**THE INSIGHT:**
Distributed systems failures follow a small set of
patterns. A structured diagnosis framework narrows
the search space systematically. Most incidents
are resolved faster by spending 2 minutes orienting
(what changed? what symptom?) than by immediately
diving into individual service logs.

---

### 📘 Textbook Definition

**Production diagnosis** for distributed systems is
the systematic process of identifying the root cause
of a distributed system failure by: (1) characterizing
the symptom class from metrics, (2) isolating the
component using distributed traces, (3) confirming
with logs, (4) understanding topology (partitions,
replication lag, leader state).

This entry is a practical runbook - a tool for
use during actual incidents.

---

### ⏱️ Understand It in 30 Seconds

```
DIAGNOSIS FLOWCHART:

1. ORIENT: What changed in the last 30 minutes?
   Deploy? Config change? Traffic spike? Holiday?
   → Most outages are correlated with a recent change.

2. CLASSIFY SYMPTOM:
   a. Error rate up → service/dep failure
   b. Latency P99 up (errors normal) → slow dep
   c. Saturation (CPU/mem/connections) → resource limit
   d. Data inconsistency → split-brain or replication lag

3. FIND THE BOUNDARY (where does the error originate?):
   Use distributed traces: find the FIRST service in
   the call chain that returns an error.
   That service is the root. Work inward from there.

4. CONFIRM WITH LOGS:
   At the root service: find the first error at
   the incident start time. What is the error?
   Stack trace? Timeout? Connection refused?
   ResourceExhaustedException?

5. TOPOLOGY CHECK (if step 4 is unclear):
   Is the cluster partitioned? (Check replication lag,
   leader state, network connectivity between nodes).
   Is there clock skew? (NTP drift could cause ordering
     issues).

6. ACT: mitigate first, understand later.
   Mitigation = reduce blast radius + stop bleeding.
   Root cause analysis = after the incident.
```

---

### 🔩 First Principles Explanation

**THE FOUR SYMPTOM CLASSES AND THEIR PATTERNS:**

**CLASS 1: ERROR RATE SPIKE**

```
SYMPTOM: HTTP 5xx errors or exception rate spiking.

DECISION TREE:

Is the error rate in ONE service or ALL services?
  ALL services → infrastructure issue (network,
    LB, DNS, cloud provider) or shared dependency (DB,
      cache).
  ONE service → that service has a specific issue.

If ONE service:
  Is the error message: "connection refused" or timeout?
    → That service cannot reach one of ITS dependencies.
    → Check: what does that service depend on?
    → Check that dependency for errors.
  
  Is the error message: "too many connections" or pool
    exhaustion?
    → Connection pool saturation.
    → Check: max_pool_size vs current connections.
    → Check: are all connections in use? Are they idle?
    → Likely: a slow upstream is holding connections open.

  Is the error message: OOM, GC overhead limit?
    → Memory exhaustion.
    → Check: heap usage, GC pause duration, memory leak.
    → Short-term: restart instance.
    → Long-term: find leak.

COMMANDS:
  # Error rate by service (Prometheus):
  rate(http_requests_total{status=~"5.."}[5m])
  / rate(http_requests_total[5m])
  
  # Top error endpoints:
  topk(10, rate(http_requests_total{status=~"5.."}[5m]))
    by (service, endpoint)
```

**CLASS 2: LATENCY SPIKE (P99)**

```
SYMPTOM: P99 latency up. Errors normal or small.

DECISION TREE:

Check: is latency up for ALL requests or just SOME?
  ALL → bottleneck in a shared path (DB, cache, shared
    network path).
  SOME → specific endpoint or operation type affected.

Is there a slow dependency (DB, cache, external API)?
  Use traces: find calls that contribute most to latency.
  The LONGEST span in the trace = the bottleneck.

Is it a queue backup?
  Check: queue depth for job queues or message queues.
  If queue depth growing: consumers too slow or too few.

Is it GC pauses in JVM?
  Check GC logs: stop-the-world pause duration.
  Check: G1GC vs ZGC (ZGC has sub-1ms pauses).

Is it thread pool saturation?
  Check: thread pool queue depth.
  Check: how many threads are waiting vs running.
  Waiting threads = upstream is slow.

COMMANDS:
  # P99 latency by service (Prometheus):
  histogram_quantile(0.99,
    rate(http_request_duration_seconds_bucket[5m]))
  by (le, service)
  
  # Check JVM GC pauses:
  grep "GC pause" /var/log/app/gc.log | \
    awk '{print $NF}' | sort -rn | head -20
  
  # Thread pool state (Actuator):
  curl http://service:8080/actuator/metrics/\
    executor.pool.size
  curl http://service:8080/actuator/metrics/\
    executor.queued
```

**CLASS 3: SATURATION**

```
SYMPTOM: CPU high, memory high, connections exhausted,
  disk I/O maxed. Operations queuing.

DECISION TREE:

CPU saturation:
  Is it GC? (Java) → check GC logs, heap pressure.
  Is it compression or serialization? → check for
    unnecessary work (logging too much, serializing
    large objects on hot path).
  Is it a busy loop? → check for runaway threads.
  
Connection saturation (DB):
  How many connections are open vs max?
    SHOW STATUS WHERE Variable_name = 'Threads_connected';
  How many are active (not sleeping)?
    SHOW PROCESSLIST;
  Sleeping connections = idle in pool.
  Active for >5s = slow query holding connection.
    SHOW FULL PROCESSLIST;

Memory saturation:
  Is heap growing monotonically? → memory leak.
  Is heap spiky? → large object allocation (check
    for large result sets, big JSON payloads).
  On JVM: enable -XX:+HeapDumpOnOutOfMemoryError
    to capture heap at OOM.

Disk I/O saturation:
  Is it write-heavy? → check for excessive logging,
    WAL write amplification (DB).
  Is it read-heavy? → check cache hit rate
    (if misses high: cold cache or working set > RAM).

COMMANDS:
  # CPU usage per process:
  top -p $(pgrep java) -H
  
  # Disk I/O by process:
  iotop -p $(pgrep java)
  
  # Connection count (PostgreSQL):
  SELECT count(*), state FROM pg_stat_activity
  GROUP BY state;
  
  # Long-running queries (PostgreSQL):
  SELECT pid, age(clock_timestamp(), query_start),
    usename, query
  FROM pg_stat_activity
  WHERE query != '<IDLE>'
    AND query_start < NOW() - INTERVAL '5 minutes'
  ORDER BY query_start;
```

**CLASS 4: DATA INCONSISTENCY / SPLIT-BRAIN**

```
SYMPTOM: Two services report different values for
  the same entity. Data written appears to be lost.
  Timestamp anomalies (events out of order).

DECISION TREE:

Multiple readers reporting different values?
  Check: are they reading from different replicas?
  Check: what is the replication lag?
    SHOW SLAVE STATUS\G  -- MySQL
    SELECT ... FROM pg_replication_slots;  -- Postgres
  If replication lag > 0: reads from replica = stale.
  Fix: route consistency-critical reads to primary.

Is the split-brain: two leaders?
  Check etcd/ZooKeeper: is there more than one leader?
  Check Raft logs: are there two different nodes claiming
    leadership for the same term?
  Split-brain = critical. Both nodes accept writes.
  Resolution: fencing + compare-and-swap to detect
    and halt the node with the lower lease.

Is it a clock skew issue?
  Events from two services look out of order in logs?
  Check: NTP sync status on each node.
    ntpq -p
    timedatectl status
  If clock difference > 100ms: ordering is unreliable.
  Use logical clocks (HLC, vector clocks) instead of
    wall clocks for event ordering.
  
COMMANDS:
  # Replication lag (Postgres):
  SELECT now() - pg_last_xact_replay_timestamp()
  AS replication_delay;
  
  # etcd leader:
  etcdctl endpoint status --write-out=table
  
  # NTP sync:
  ntpq -p
  timedatectl show --property=NTPSynchronized
  chronyc tracking | grep "System time"
```

**THE UNIVERSAL FIRST STEP:**

```bash
# ALWAYS START HERE: what changed in the last 30 min?

# Recent deployments (Git):
git log --oneline --after="30 minutes ago" --all

# Recent k8s deployments:
kubectl rollout history deployment --all-namespaces | \
  grep -v "<none>"

# Recent config changes (Consul, etcd):
etcdctl get / --prefix --write-out=json | \
  jq '.kvs[] | select(.mod_revision > THRESHOLD)'

# Recent autoscaling events:
kubectl get events --sort-by='.lastTimestamp' | \
  grep -E "Scal|Deploy|Error" | tail -20

# Traffic anomalies:
rate(http_requests_total[5m]) vs 24h ago same time
# Any spike in traffic? Unusual bot traffic?
```

---

### 🧠 Mental Model / Analogy

> Diagnosing a distributed system incident is like
> an ER triage: start with vitals (metrics = heart
> rate, blood pressure), not with detailed organ
> examination (logs for specific services). Vitals
> tell you the class of problem: cardiac, respiratory,
> trauma. Once you know the class, you narrow to
> the organ (trace: which service). Then you examine
> that organ specifically (logs: what error, when).
> An ER doctor who skips vitals and goes directly
> to detailed organ examination misses the forest
> for the trees. Similarly, an engineer who opens
> individual service logs before checking metrics
> may be looking at the wrong service for 30 minutes.
> Triage first. Narrow. Then examine.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The framework:**
Four symptom classes (error rate, latency, saturation,
inconsistency). For each: a decision tree. Always
start by asking "what changed?"

**Level 2 - Traces are the bridge:**
Metrics tell you WHAT is broken. Traces tell you
WHERE in the call chain. The first failing span
in a distributed trace is usually the root cause.
Everything after it fails because of cascade.

**Level 3 - Replication lag is the first thing to check for inconsistency:**
Stale reads from replicas are the most common cause
of apparent data inconsistency. Check replication
lag before concluding split-brain. Lag is normal
and expected; split-brain is a crisis.

**Level 4 - Connection pool exhaustion is a symptom, not a cause:**
"Too many connections" means a downstream is slow
and holding connections. Fix the slow downstream,
not the connection count. Increasing max_pool_size
temporarily, but the real fix is the upstream cause.

**Level 5 - The blast radius principle:**
Before deep investigation, mitigate: enable circuit
breakers, reduce traffic to the affected service,
increase replica count. Mitigate reduces the blast
radius while diagnosis proceeds. Never let
investigation block mitigation.

---

### 💻 Code Example

**Automated Incident Pre-Check Script**

```python
#!/usr/bin/env python3
"""
Distributed Systems Incident Pre-Check
Run at the START of any incident investigation.
Outputs a triage summary in < 60 seconds.
"""

import subprocess
import json
from datetime import datetime, timedelta, timezone

PROMETHEUS_URL = "http://prometheus:9090"
KUBECTL = "kubectl"

def prom_query(query: str) -> list:
    """Run an instant Prometheus query."""
    import urllib.request
    import urllib.parse
    url = (
        f"{PROMETHEUS_URL}/api/v1/query"
        f"?query={urllib.parse.quote(query)}"
    )
    with urllib.request.urlopen(url, timeout=5) as r:
        data = json.loads(r.read())
    return data.get("data", {}).get("result", [])


def check_error_rates():
    print("\n=== ERROR RATES (last 5m) ===")
    results = prom_query(
        "topk(5, "
        "rate(http_requests_total{status=~'5..'}[5m])"
        " / rate(http_requests_total[5m])) by (service)"
    )
    for r in results:
        svc = r["metric"].get("service", "unknown")
        val = float(r["value"][1])
        if val > 0.01:  # > 1% error rate
            print(f"  ALERT {svc}: {val*100:.1f}% error rate")
        else:
            print(f"  OK    {svc}: {val*100:.2f}% error rate")


def check_p99_latency():
    print("\n=== P99 LATENCY (last 5m) ===")
    results = prom_query(
        "topk(5, histogram_quantile(0.99, "
        "rate(http_request_duration_seconds_bucket[5m]))"
        ") by (service)"
    )
    for r in results:
        svc = r["metric"].get("service", "unknown")
        val = float(r["value"][1]) * 1000  # to ms
        flag = "ALERT" if val > 1000 else "OK   "
        print(f"  {flag} {svc}: P99={val:.0f}ms")


def check_recent_deployments():
    print("\n=== RECENT DEPLOYMENTS (last 30m) ===")
    try:
        result = subprocess.run(
            [KUBECTL, "get", "events",
             "--all-namespaces",
             "--sort-by=.lastTimestamp",
             "-o", "json"],
            capture_output=True, text=True, timeout=10
        )
        events = json.loads(result.stdout)
        cutoff = datetime.now(timezone.utc) - timedelta(
            minutes=30
        )
        for item in events.get("items", []):
            reason = item.get("reason", "")
            if reason in ("Pulled", "Created", "Started",
                          "ScalingReplicaSet"):
                msg = item.get("message", "")
                ts_str = item.get("lastTimestamp", "")
                print(f"  {ts_str[:19]} {reason}: {msg[:60]}")
    except Exception as e:
        print(f"  Could not fetch events: {e}")


def check_replication_lag():
    print("\n=== REPLICATION LAG ===")
    results = prom_query(
        "pg_replication_lag_seconds"
    )
    for r in results:
        instance = r["metric"].get("instance", "unknown")
        lag = float(r["value"][1])
        flag = "ALERT" if lag > 10 else "OK   "
        print(f"  {flag} {instance}: lag={lag:.1f}s")


if __name__ == "__main__":
    print(f"Incident triage: {datetime.now().isoformat()}")
    check_recent_deployments()
    check_error_rates()
    check_p99_latency()
    check_replication_lag()
    print("\n=== NEXT STEPS ===")
    print("1. Check traces for first failing service")
    print("2. Check logs at that service for first error")
    print("3. Mitigate (circuit break / rollback) then dig deeper")
```

---

### ⚖️ Comparison Table

| Symptom Class | Primary Tool | Key Metric | Common Pattern | First Fix |
|---|---|---|---|---|
| **Error rate spike** | Metrics + traces | HTTP 5xx rate per service | Dependency down or connection pool exhausted | Circuit-break failing dep |
| **Latency P99 spike** | Traces (find longest span) | P99 latency by service | Slow downstream, GC pause, thread pool full | Add capacity or reduce fanout |
| **Saturation** | Metrics + system tools | CPU%, heap%, connections/max | Traffic spike, memory leak, slow query | Scale out or shed load |
| **Data inconsistency** | Replication metrics + DB | Replication lag, leader count | Stale replica reads, split-brain | Route reads to primary |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Check logs first" | Logs are step 3, not step 1. Metrics first (what class of problem), then traces (which service), then logs (what specific error). Jumping to logs for the wrong service wastes time. |
| "Restart the service if it's slow" | Restart removes symptoms (clears connection pools, resets state) but doesn't fix the root cause. After restart: the service may recover briefly, then degrade again. Fix the dependency first. |
| "Increasing connection pool size fixes connection exhaustion" | Connection exhaustion means all connections are in use. Increasing pool size increases memory usage and adds more connections to an already overloaded database. The real fix: find what is holding connections open (slow query, slow upstream), and fix that. |
| "Only one person should diagnose during an incident" | Incident command structure: one commander (coordinates), one scribe (timeline), investigators (parallel paths, reported back to commander). Silent individual heroics = duplicated effort, missed communication. |

---

### 🚨 Failure Modes & Diagnosis

**False Positive: Cascade Masking the Root Cause**

**Symptom:** Traces show 10 services all failing.
Every service team says "it's not us." No consensus.
Incident drags on.

**Root Cause:** In a cascading failure, EVERY service
downstream of the root failure appears to fail.
Teams see their service failing and investigate their
service (which is fine). The root is the FIRST service
to fail, not the loudest.

**Diagnosis:**
```bash
# Find the root in traces:
# Look at the span tree. The root cause is the span
# with an error that has NO parent span with an error.

# In Jaeger:
# Search for trace_id from the first user-reported error.
# Open the trace. Look for the first RED span.
# That service is the root cause.

# In Prometheus (heuristic):
# Which service error rate went up FIRST?
changes(
  rate(http_requests_total{status=~"5.."}[1m])[30m:1m]
) > 0
# The service with the earliest change onset = root cause.

# Timeline reconstruction from logs:
# Collect first error timestamp per service:
grep "ERROR" /var/log/service-A/app.log | \
  head -1 | awk '{print $1, $2, "service-A"}'
grep "ERROR" /var/log/service-B/app.log | \
  head -1 | awk '{print $1, $2, "service-B"}'
# Sort by time: earliest error = root cause service.
```

---

### 🔗 Related Keywords

**Prerequisites:** `Observability in Distributed Systems`
(DST-055), `Distributed Systems Performance Tuning`
(DST-056)

**Related:** `Cascading Failures` (DST-007),
`Circuit Breakers` (DST-033)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: ORIENT   │ What changed in the last 30 min?     │
│ STEP 2: CLASSIFY │ Error / Latency / Saturation /       │
│                  │ Inconsistency                        │
│ STEP 3: TRACES   │ Find FIRST failing span in call chain│
│ STEP 4: LOGS     │ Find first error at that service     │
│ STEP 5: TOPOLOGY │ Partition? Replication lag? Skew?   │
│ STEP 6: MITIGATE │ Circuit break / rollback / scale    │
├──────────────────┼──────────────────────────────────────┤
│ COMMON PATTERNS  │ Latency spike → slow dep/GC pause   │
│                  │ Errors → dep down/pool exhausted    │
│                  │ Stale data → replication lag        │
│                  │ Split-brain → two leaders           │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The diagnosis framework described here applies beyond
distributed systems incidents. Any complex system
failure benefits from: (1) classify the symptom
before investigating the cause, (2) use the highest-
level signal (metrics) to narrow to the component
before using the low-level signal (logs), (3) always
ask "what changed?" before assuming something failed
without provocation. These principles transfer to:
debugging production code (check deploy log before
logs), investigating performance regressions (check
what changed in the build before profiling), and
analyzing A/B test results (check if there was a
confounding factor before concluding significance).
The meta-skill is: resist the urge to immediately
examine the lowest level (log lines, stack traces)
and instead zoom out to find the smallest scope that
contains the entire problem, then zoom in.

---

### 💡 The Surprising Truth

In a survey of distributed systems incidents at large
tech companies, more than 70% of major outages were
traceable to a change (deploy, config change, traffic
spike, cron job) within the preceding hour. The most
impactful single step in incident diagnosis is not
a technical tool - it is asking "what changed?"
before touching any monitoring system. This is why
SRE incident playbooks universally start with this
question. The implication for system design: every
change must be traceable, tagged, and visible in
monitoring dashboards alongside operational metrics.
When a P99 latency graph shows a spike at 14:37,
you should be able to see a deploy annotation at
14:35 on the same graph without opening a separate
system. This is why tools like Grafana annotations,
Datadog change tracking, and deployment markers
exist - they are not optional niceties but critical
diagnostic tools that reduce mean time to resolution.

---

### ✅ Mastery Checklist

1. [APPLY] Given an alert: "service-B P99 > 2000ms".
   Walk through the full 6-step triage framework.
   Which Prometheus queries run first? What are you
   looking for in traces? In logs?
2. [DISTINGUISH] A colleague says: "The database has
   too many connections; I increased the pool size."
   What question should you ask to find the actual
   root cause? Why is increasing pool size usually
   the wrong fix?
3. [COMMAND] Design an incident command structure
   for a 5-person on-call team responding to a
   P0 incident. What roles? What communication
   channel? What cadence for status updates?
4. [IMPLEMENT] Add a "what changed recently" query
   to your incident pre-check script. It should
   show: recent deployments, config changes, and
   traffic anomalies compared to the same time 24h ago.
5. [IDENTIFY] How do you distinguish a cascading
   failure (where 10 services fail because 1 failed)
   from a correlated failure (where 10 services fail
   due to a shared infrastructure problem)? What
   is the key diagnostic difference?
