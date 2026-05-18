---
id: DST-034
title: Failure Detector
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-011, DST-020
used_by: DST-035, DST-036, DST-046
related: DST-011, DST-020, DST-035, DST-036
tags:
  - distributed
  - fault-tolerance
  - detection
  - operational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/distributed-systems/failure-detector/
---

⚡ TL;DR - A failure detector is a component that
monitors other nodes and classifies them as suspected-
dead or alive; no failure detector can be both complete
(always detects real failures) and accurate (never
suspects live nodes) in asynchronous systems, so
practical systems use probabilistic detectors like
Phi Accrual that express suspicion as a probability
rather than a binary alive/dead classification.

---

### 📋 Entry Metadata

| #034 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Fault Tolerance, Heartbeat and Health Check | |
| **Used by:** | Retry Logic, Circuit Breaker, Leader Election | |
| **Related:** | Fault Tolerance, Heartbeat and Health Check, Retry Logic, Circuit Breaker | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A cluster has 10 nodes. One node is slow (GC pause,
CPU-bound) but not crashed. The cluster's heartbeat
monitor uses a fixed 5-second timeout. The slow node
misses 3 heartbeats during a 15-second GC pause.
The monitor marks the node as DEAD and triggers failover:
evicts it from the cluster, reassigns its work to other
nodes, and starts a replacement. 15 seconds later, the
GC pause ends. The "dead" node reconnects - it is a
healthy node that was temporarily slow.

Now there is a split-brain: the original node thinks
it is still in the cluster. The cluster thinks it is
out. The replacement node has taken over its work.
The original node is still processing (incorrectly).
This is a false positive failure detection - one of
the most dangerous failure modes in distributed systems.

**THE INSIGHT:**
Failure detection is fundamentally about distinguishing
"slow" from "dead" in an asynchronous network. This
is provably impossible to do with certainty. Practical
failure detectors manage the uncertainty explicitly:
use adaptive timeouts, probabilistic suspicion scores,
or "suspected" (not "dead") classifications that allow
false positives to be corrected.

---

### 📘 Textbook Definition

A **failure detector** is a distributed abstraction
that monitors processes and outputs, for each monitored
process, one of two values:
- **Suspected:** the detector believes the process has
  failed (may be wrong - false positive)
- **Not Suspected (Alive):** the detector believes the
  process is running (may miss real failures - false negative)

**Two key properties (Chandra-Toueg, 1996):**
- **Completeness:** every crashed process is eventually
  permanently suspected by all correct processes
- **Accuracy:** no correct (live) process is ever
  suspected

**The FLP impossibility result** (Fischer-Lynch-Paterson,
1985) and Chandra-Toueg showed: in an asynchronous
system (no bounds on message delays), no failure
detector can be both complete and accurate. Practical
systems choose between:
- **Strong completeness, weak accuracy** (some false positives)
- **Weak completeness, strong accuracy** (may miss failures)

---

### ⏱️ Understand It in 30 Seconds

**The fundamental dilemma:**
```
You are waiting for a heartbeat from node B.
The heartbeat is 5 seconds late.

POSSIBILITIES:
  1. Node B has crashed           → declare dead (correct)
  2. Node B is in a GC pause      → declare alive (correct)
  3. Network is temporarily slow  → declare alive (correct)
  4. Node B is partitioned but alive → ??? (no way to know)

WITH FIXED TIMEOUT (5s):
  After 5s: declare DEAD
  If it was case 2/3/4: FALSE POSITIVE (wrong decision)
  If it was case 1: TRUE POSITIVE (correct decision)

WITH PHI ACCRUAL (adaptive):
  After 5s: φ=2 (weak suspicion: 1% chance of failure)
  After 10s: φ=5 (moderate: 0.7% per second getting worse)
  After 20s: φ=8 (strong suspicion: act now)
  → Act when probability crosses threshold, not a fixed
    time
```

---

### 🔩 First Principles Explanation

**WHY FIXED TIMEOUTS FAIL:**

Heartbeat intervals are designed for normal operating
conditions. In production, abnormal conditions are
common:
- JVM GC "stop the world" pauses: 100ms to 10+ seconds
- CPU throttling in cloud environments: variable
- Network congestion: variable RTT, packet loss
- Load spikes: heartbeat threads starved of CPU

Fixed timeouts cannot account for these variations.
Too short: false positives. Too long: slow detection
of real failures (cluster unavailable for too long).

**THE ACCURACY-COMPLETENESS TRADE-OFF:**

```
CONSERVATIVE (long timeout):
  + Rarely falsely suspect live nodes (high accuracy)
  - Slow to detect real failures (low completeness)
  Use when: false positives are expensive
            (e.g., leader re-election is disruptive)

AGGRESSIVE (short timeout):
  + Fast failure detection (high completeness)
  - Many false positives under load (low accuracy)
  Use when: false negatives are expensive
            (e.g., stuck transaction locks everything)

ADAPTIVE (Phi Accrual, SWIM):
  + Adapts to observed network conditions
  + Expresses suspicion as probability not binary
  Use when: both matter, or workload is variable
```

**PHI ACCRUAL DETECTOR:**

Tracks the distribution of arrival times of heartbeats
(mean and variance). When a heartbeat is late, it
computes a "phi" value representing the probability
that the current arrival delay is not due to normal
variance:

```
φ = -log₁₀(1 - Φ((t_now - t_last) / σ))

Where:
  t_now: current time
  t_last: time of last heartbeat
  σ: standard deviation of recent heartbeat intervals
  Φ: cumulative distribution function of normal
    distribution

Higher φ = higher confidence of failure
φ=1: ~10% chance of failure per second
φ=8: ~99.9999%+ confidence of failure
φ=10: act on this (Cassandra default threshold)
```

This adapts automatically: on a loaded system with
high heartbeat variance, φ grows more slowly (more
tolerance). On a healthy network, φ grows faster
(tighter detection).

---

### 🧠 Mental Model / Analogy

> A failure detector is like a doctor monitoring a
> patient's pulse. A fixed-timeout doctor says "if
> I don't feel a pulse for 5 seconds, the patient
> is dead." An adaptive doctor says "this patient's
> resting pulse averages 60bpm with 5bpm variance.
> If I haven't felt a pulse for 3 seconds (2x their
> normal interval), I'm 50% confident something is
> wrong. If it's 10 seconds (10x their normal), I'm
> 99.99% confident." The adaptive approach is less
> likely to misdiagnose a slow pulse as death.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A failure detector watches other nodes via heartbeats.
If a node stops sending heartbeats, the detector suspects
it has failed. The challenge: the network might be slow,
not the node. Simple timeout detectors confuse slow
nodes with dead nodes. Better detectors use statistics
to express how confident they are.

**Level 2 - Where it is used:**
Cassandra uses the Phi Accrual failure detector.
ZooKeeper uses session timeouts (configurable, not
adaptive). Kubernetes uses configurable liveness probe
timeouts (not adaptive). Akka cluster uses an adaptive
failure detector based on arrival time statistics.
Consul uses a combination of gossip (for membership)
and health checks (for service readiness).

**Level 3 - SWIM protocol:**
SWIM (Scalable Weakly-consistent Infection-style Process
group Membership protocol) is an alternative to
heartbeat-based failure detection. Instead of each
node monitoring all others directly (O(N) traffic),
SWIM uses random probing: each node randomly selects
one other node to ping each round. If the ping fails,
it asks K random other nodes to try (indirect probe).
Only if all fail: suspect the target. This is O(1)
message cost per node per round and scales to large
clusters. Used by HashiCorp Consul and similar systems.

**Level 4 - The timeout parameter as an SLO:**
The failure detection timeout is not a technical parameter
- it is an SLO definition. "We can tolerate a node
being dead for up to T seconds before taking corrective
action." T must account for:
- Maximum expected GC pause (90th percentile)
- Maximum expected network RTT spike (99.9th percentile)
- Acceptable time-to-detect failure (business requirement)

These three constraints may conflict. If maximum GC
pause is 2 seconds but acceptable time-to-detect is
1 second: you must either eliminate long GC pauses
(use G1GC, tune heap), or accept occasional false
positives.

**Level 5 - The role in consensus:**
Failure detectors are a core component of Raft and
Paxos. A Raft leader must be detected as failed by
followers before they can start an election. If the
failure detector has high false positive rates, followers
start unnecessary elections, causing performance
degradation and availability blips. Raft papers recommend
tuning the election timeout to be significantly larger
than the 99.9th percentile RTT - typically 150-300ms
for LAN, higher for WAN. This is the heartbeat_interval
and election_timeout parameters in etcd.

---

### ⚙️ Mechanism - Phi Accrual in Detail

```
SLIDING WINDOW of heartbeat arrival times:
  [t1, t2, t3, ..., tn] (last N heartbeat arrivals)

STATISTICS:
  mean (μ) = average inter-arrival time
  variance (σ²) = variance of inter-arrival times

ON EACH CHECK (no heartbeat received yet):
  elapsed = now - last_heartbeat_arrival
  z = (elapsed - μ) / σ  (standard deviations late)
  φ = -log₁₀(1 - CDF_normal(z))

INTERPRETATION:
  φ < 1:  normal variation; no suspicion
  φ = 1:  10% probability of failure
  φ = 8:  ~99.999% confidence of failure
  φ ≥ threshold (e.g., 10): SUSPECT node

ADAPTIVE BEHAVIOR:
  High network jitter → high σ → φ grows slowly
  (more tolerance for delays on congested networks)
  Low jitter → low σ → φ grows quickly
  (tight detection on stable networks)
```

---

### 💻 Code Example

**Fixed Timeout vs Adaptive Failure Detector**

```python
# BAD: fixed timeout failure detector
# False positives during GC pauses or network hiccups

import time

class FixedTimeoutDetector:
    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout = timeout_seconds
        self.last_heartbeat: dict[str, float] = {}

    def heartbeat(self, node_id: str) -> None:
        self.last_heartbeat[node_id] = time.monotonic()

    def is_alive(self, node_id: str) -> bool:
        last = self.last_heartbeat.get(node_id, 0)
        elapsed = time.monotonic() - last
        # BUG: 5s GC pause = node marked dead (false positive)
        return elapsed < self.timeout
```

```python
# GOOD: Phi Accrual failure detector (adaptive)
import math
import collections
import time
from statistics import mean, stdev

class PhiAccrualDetector:
    """
    Adaptive failure detector based on arrival time statistics.
    Phi value represents suspicion strength (higher = more suspected).
    """

    def __init__(
        self,
        threshold: float = 8.0,
        window_size: int = 200,
        min_std_dev: float = 0.1
    ):
        self.threshold = threshold  # phi to declare suspect
        self.window_size = window_size
        self.min_std_dev = min_std_dev  # Avoid zero variance

        # Sliding window of inter-arrival times per node
        self._arrivals: dict[
            str, collections.deque
        ] = {}
        self._last_arrival: dict[str, float] = {}

    def heartbeat(self, node_id: str) -> None:
        """Record a heartbeat arrival."""
        now = time.monotonic()
        if node_id in self._last_arrival:
            interval = now - self._last_arrival[node_id]
            if node_id not in self._arrivals:
                self._arrivals[node_id] = collections.deque(
                    maxlen=self.window_size
                )
            self._arrivals[node_id].append(interval)
        self._last_arrival[node_id] = now

    def phi(self, node_id: str) -> float:
        """
        Compute phi (suspicion level) for a node.
        Higher phi = stronger suspicion of failure.
        """
        if (
            node_id not in self._last_arrival or
            node_id not in self._arrivals or
            len(self._arrivals[node_id]) < 2
        ):
            return 0.0

        intervals = list(self._arrivals[node_id])
        mu = mean(intervals)
        sigma = max(stdev(intervals), self.min_std_dev)

        elapsed = time.monotonic() - self._last_arrival[node_id]

        # Standard deviations above mean:
        z = (elapsed - mu) / sigma
        # Phi: -log10(P(delay >= elapsed)):
        # Using normal approximation:
        p_later = 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
        if p_later == 0:
            return float("inf")
        return -math.log10(p_later)

    def is_suspected(self, node_id: str) -> bool:
        """True if phi exceeds threshold."""
        return self.phi(node_id) >= self.threshold

# Usage:
detector = PhiAccrualDetector(threshold=8.0)

# Normal heartbeats (every 1s with ±100ms jitter):
for _ in range(100):
    time.sleep(1.0 + (random.random() - 0.5) * 0.2)
    detector.heartbeat("node-1")

print(f"phi during normal: {detector.phi('node-1'):.2f}")
# → ~0.1 (not suspected)

# Simulate failure (no heartbeat for 8s):
time.sleep(8)
print(f"phi after 8s silence: {detector.phi('node-1'):.2f}")
# → ~8-10+ (suspected)
```

---

### ⚖️ Comparison Table

| Detector Type | Accuracy | Completeness | Scale | Used In |
|---|---|---|---|---|
| **Fixed timeout** | Low (false positives) | High (if timeout short) | O(N) messages | Simple systems |
| **Phi Accrual** | High (adaptive) | High (adapts to load) | O(N) messages | Cassandra, Akka |
| **SWIM** | Good | Good | O(1) per node | Consul, Serf |
| **Session timeout** | Medium | Medium (fixed) | O(N) | ZooKeeper |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A failure detector can distinguish slow from crashed" | Provably impossible in asynchronous systems (FLP impossibility). Failure detectors always have a trade-off between false positives and false negatives. |
| "Shorter timeout = better failure detection" | Shorter timeout = faster detection of real failures AND more false positives. The correct timeout depends on your GC pause profile, network RTT distribution, and how disruptive false positives are. |
| "Phi Accrual eliminates false positives" | No - it reduces false positives by adapting to observed network conditions. Under novel conditions (e.g., first-time GC pause longer than historical), phi will still cross the threshold. |
| "Failure detection is solved" | Every distributed system team tunes heartbeat timeouts repeatedly. It is an operational parameter that must match the actual performance profile of the deployment environment. |

---

### 🚨 Failure Modes & Diagnosis

**False Positive Causing Unnecessary Failover**

**Symptom:** A node is repeatedly removed and rejoined
to the cluster. Logs show: "Node X suspected," followed
by "Node X joined." Cluster performance is degraded
from constant rebalancing.

**Root Cause:** Failure detector timeout is shorter
than the node's GC pause duration. Every GC pause
triggers a false positive suspicion.

**Diagnosis:**
```bash
# Check GC pause times vs heartbeat timeout:
# (Java / JVM)
jstat -gcutil <pid> 500 20
# Column FGCT: Full GC time in seconds cumulative
# Column YGC/FGC: count of young/full GCs

# Check JVM GC logs for stop-the-world pauses:
java -Xlog:gc*=info:file=gc.log -jar app.jar
grep "Pause" gc.log | awk '{print $NF}' | sort -n | tail -5

# If P99 GC pause > heartbeat_interval * 2: tune detector
# Fix options:
#   1. Increase heartbeat timeout (accept slower detection)
#   2. Tune JVM GC (G1GC, ZGC for shorter pauses)
#   3. Increase phi threshold (reduce sensitivity)
```

**Fix:**
```yaml
# Cassandra: phi_convict_threshold (default 8)
# Increase for high-GC environments:
phi_convict_threshold: 12

# etcd: heartbeat and election timeout
# (election_timeout should be >> heartbeat_interval)
heartbeat-interval: 100     # ms
election-timeout: 1000      # ms (10x heartbeat)

# Kubernetes liveness probe: adjust failure threshold
livenessProbe:
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 6  # Allow 60s before restart
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Fault Tolerance` (DST-011)
- `Heartbeat and Health Check` (DST-020)

**Builds On This:**
- `Retry Logic with Exponential Backoff` (DST-035)
- `Circuit Breaker` (DST-036)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ GOAL       │ Distinguish dead nodes from slow nodes     │
│ PROBLEM    │ Impossible with certainty (async networks) │
├────────────┼────────────────────────────────────────────┤
│ FIXED      │ Simple; false positives on GC/load        │
│ PHI ACCRUAL│ Adaptive; calibrates to arrival variance  │
│ SWIM       │ O(1) per node; for large clusters         │
├────────────┼────────────────────────────────────────────┤
│ PHI        │ Low phi = alive; high phi ≥ 8 = suspect   │
│ THRESHOLD  │ Default 8-10; increase for GC-heavy apps  │
├────────────┼────────────────────────────────────────────┤
│ TUNE FOR   │ Timeout > P99.9 GC pause × 2              │
│            │ Election timeout >> heartbeat interval     │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Slow ≠ dead; good detectors adapt to     │
│            │  the gap between normal and failure."     │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The failure detection problem is a specific instance
of a general monitoring principle: distinguishing signal
from noise. In any monitoring system - health checks,
error rate monitors, latency SLO alerts - you face the
same trade-off between sensitivity (catch real problems
fast) and specificity (don't alert on noise). Every
monitoring threshold is a failure detector with
completeness and accuracy properties. The Phi Accrual
insight - express confidence as a probability derived
from historical statistics rather than a fixed binary
threshold - is universally applicable. Anomaly detection
systems, SLO burn rate alerts, and capacity alerts
all benefit from this statistical framing.

---

### 💡 The Surprising Truth

The Amazon DynamoDB team discovered that failure
detectors in cloud environments have a specific pathology:
"correlated timeouts." When an availability zone is
overloaded, many services simultaneously see timeouts.
A simple failure detector would mark all of them
"dead" simultaneously, triggering massive failover
that further overloads the surviving zone - a failure
amplification cascade. Modern failure detectors (AWS
and GCP internal implementations) include "cluster-level
awareness": if many nodes are suspected simultaneously,
reduce the sensitivity (raise the threshold). One dead
node is likely a real failure. Fifty simultaneously
suspected nodes is likely a network event. This is
the "correlated failure" heuristic that separates
cloud-native failure detectors from simple Phi Accrual.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Write a PhiAccrualDetector that maintains
   a sliding window of arrival times and computes phi.
   Test with simulated heartbeats at 1s intervals,
   then simulate a 10-second pause.
2. [TUNE] Given a service with P99 GC pause of 3 seconds
   and current heartbeat timeout of 2 seconds, calculate
   the minimum safe timeout and recommend the phi threshold.
3. [COMPARE] For a 1000-node cluster, compare the
   message overhead of O(N) direct heartbeat vs SWIM
   O(1) random probe. Determine at what N SWIM becomes
   clearly preferable.
4. [DIAGNOSE] Logs show "node suspected" / "node joined"
   repeating every 30 seconds on the same node. Identify
   the root cause and the three possible fixes.
5. [EXPLAIN] Why the FLP impossibility result means
   every failure detector must choose between accuracy
   and completeness, and how this manifests in production
   systems you have worked with.
