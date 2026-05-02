---
layout: default
title: "Heartbeat"
parent: "Distributed Systems"
nav_order: 601
permalink: /distributed-systems/heartbeat/
number: "0601"
category: Distributed Systems
difficulty: ★★☆
depends_on: Gossip Protocol, Failure Detection, Timeouts
used_by: Leader Election, Raft, Paxos, Service Mesh, Kubernetes
related: Gossip Protocol, Phi Accrual Detector, Circuit Breaker, Health Check
tags:
  - distributed
  - reliability
  - failure-detection
  - pattern
---

# 601 — Heartbeat

⚡ TL;DR — A heartbeat is a periodic signal sent from a node to prove it's alive; the absence of heartbeats within a timeout window is interpreted as failure, triggering automated recovery.

| #601            | Category: Distributed Systems                                        | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Gossip Protocol, Failure Detection, Timeouts                         |                 |
| **Used by:**    | Leader Election, Raft, Paxos, Service Mesh, Kubernetes               |                 |
| **Related:**    | Gossip Protocol, Phi Accrual Detector, Circuit Breaker, Health Check |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed system has no way to distinguish between a node that is alive-but-silent and a node that has crashed. If a follower node in a Raft cluster stops responding (due to crash or partition), the leader has no mechanism to detect the failure and trigger re-election. The cluster deadlocks: the leader holds resources, the followers wait, and progress halts until a human intervenes.

**THE INVENTION MOMENT:**
The heartbeat pattern is borrowed from hardware: early mainframes sent periodic clock signals to verify component liveness. A periodic "I'm alive" message gives the monitoring system a failure signal with bounded detection latency: `max_detection_time = heartbeat_interval + timeout_threshold`. No heartbeat = failure declared.

---

### 📘 Textbook Definition

A **heartbeat** is a periodic message (or signal) sent by a node to its peers or to a monitoring process to assert that the node is alive and functioning. If no heartbeat is received within a configurable **timeout window**, the monitored node is declared failed and remediation begins (leader re-election, replica promotion, container restart). **Parameters:** interval (how often to send), timeout (how long silence triggers failure). **Variants:** (1) **Push heartbeat** — node actively sends to monitor; (2) **Pull heartbeat** (health check polling) — monitor actively queries node; (3) **Lease-based** — node holds a lease that must be renewed; expiry triggers failure; (4) **Gossip-based** — heartbeat state is gossiped across cluster (Cassandra, SWIM). The fundamental trade-off: **faster detection** (short interval) vs. **false positive reduction** (longer interval + more tolerance).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every `T` seconds, a node shouts "I'm alive!" — if the monitor doesn't hear it for `N × T` seconds, it declares the node dead and triggers recovery.

**One analogy:**

> A heartbeat is like a diver's "OK" hand signal to their dive buddy every 30 seconds. If the buddy doesn't get the signal after 90 seconds (3 missed signals), they assume something is wrong and surface to investigate. The signal interval (30s) and tolerance (miss 3) are the heartbeat parameters.

**One insight:**
The timeout must be calibrated to be larger than the 99th-percentile round-trip time, but small enough that failures are detected quickly enough for SLA compliance. Setting it too tight causes cascading false positives (healthy nodes declared dead during GC pauses or network jitter), triggering leader re-elections that themselves cause latency spikes — a self-reinforcing failure loop.

---

### 🔩 First Principles Explanation

**RAFT HEARTBEAT (LEADER → FOLLOWERS):**

```
Leader sends AppendEntries RPC with empty entries (heartbeat) every 150ms.
Follower receives heartbeat → resets election_timeout.

If election_timeout expires (randomised 150ms–300ms) without heartbeat:
  Follower transitions to CANDIDATE
  Increments currentTerm
  Votes for self
  Sends RequestVote RPC to all other nodes

This is how Raft detects leader failure:
  Leader alive → constant heartbeats → followers reset timeout → no election
  Leader dead → no heartbeats → one follower times out → starts election
  New leader elected within 1-2 election timeouts (300–600ms)

Key: heartbeat interval < election timeout/2 (to prevent false positives)
```

**KUBERNETES LIVENESS PROBE (HTTP HEARTBEAT):**

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15 # wait before first probe
  periodSeconds: 10 # probe every 10 seconds
  failureThreshold: 3 # 3 consecutive failures → kill + restart pod
  timeoutSeconds: 1 # each probe must respond within 1 second


# Detection latency: 10s × 3 = 30 seconds worst case
# False positive prevention: 3 failures required, not 1
# Kubernetes is the "monitor"; pod is the "sender" (pull heartbeat)
```

**TCP KEEPALIVE (OS-LEVEL HEARTBEAT):**

```
After TCP_KEEPIDLE seconds of idle connection:
  OS sends TCP keepalive probe (1-byte packet)
  If no ACK within TCP_KEEPINTVL seconds: probe again
  After TCP_KEEPCNT failed probes: declare connection dead → ECONNRESET

Linux defaults: IDLE=7200s, INTERVAL=75s, COUNT=9 → ~2.25 hours to detect dead TCP
For distributed systems: reduce IDLE to 60-120s for faster detection
```

---

### 🧪 Thought Experiment

**THE SPLIT BRAIN HEARTBEAT PROBLEM:**

Cluster: 1 leader + 2 followers. Network partition: leader isolated, followers can see each other.

- Leader: no heartbeats reach followers → followers timeout → new leader elected.
- Original leader: can't reach followers → BUT still thinks it's leader (it never crashed).
- Two leaders: each serving reads/writes to their partition.

When partition heals:

- Raft: original leader sees higher term from new leader → immediately reverts to follower.
- Naive heartbeat without terms: both leaders try to merge state → CONFLICT.

**Lesson:** Heartbeat alone is insufficient for leader uniqueness. Heartbeat must be paired with a monotonic term/epoch counter so that when partitions heal, the cluster can deterministically identify which "leader" is stale (lower term). This is a core Raft design insight.

---

### 🧠 Mental Model / Analogy

> A heartbeat is like a check-in call to your team when working remotely. If you don't hear from a team member for 3 days (timeout), you assume they've gone AWOL and reassign their tasks. The interval (daily check-in) and threshold (3 missed) are tunable parameters. Miss once: tolerated. Miss three in a row: declared absent.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A node sends a periodic "I'm alive" message. If the monitor doesn't receive it within a timeout, the node is declared dead and recovery starts.

**Level 2:** Push vs. pull heartbeat. Timeout = interval × failure_threshold. Raft uses leader heartbeats to suppress follower elections. Kubernetes uses HTTP liveness probes. Key parameter: interval/timeout ratio prevents false positives from GC pauses.

**Level 3:** Phi accrual detector (Cassandra): adaptive timeout based on inter-arrival time distribution — if the network is slow today, the threshold auto-adjusts. SWIM protocol: combines failure detection with membership updates in one gossip message, with indirect probing (ask a third node to ping the suspect) to distinguish crash from congestion.

**Level 4:** Heartbeat design tension — fast detection vs. false positive suppression. Practical tuning: timeout = max(mean_RTT + 4σ, minimum_useful_detection_latency). For crash detection: heartbeat sufficient. For Byzantine detection: cryptographically signed heartbeats (the sender must prove identity; otherwise a malicious node can forge heartbeats for dead nodes). For partial failures (node alive but slow): combine heartbeat with SLI metrics (latency p99, error rate) — a node that's alive but degraded should trigger graceful degradation, not restart.

---

### ⚙️ How It Works (Mechanism)

**Heartbeat Manager:**

```java
public class HeartbeatMonitor {
    private final Map<String, Long> lastHeartbeat = new ConcurrentHashMap<>();
    private static final long TIMEOUT_MS = 10_000; // 10 seconds

    // Called when heartbeat received from nodeId
    public void recordHeartbeat(String nodeId) {
        lastHeartbeat.put(nodeId, System.currentTimeMillis());
    }

    // Called on a schedule to check for dead nodes
    public List<String> detectFailedNodes() {
        long now = System.currentTimeMillis();
        return lastHeartbeat.entrySet().stream()
            .filter(e -> now - e.getValue() > TIMEOUT_MS)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism           | Detection Latency    | False Positive Risk     | Overhead | Used In         |
| ------------------- | -------------------- | ----------------------- | -------- | --------------- |
| Simple timeout      | interval × threshold | High (fixed threshold)  | Low      | Basic systems   |
| Phi accrual         | Adaptive             | Low (adapts to network) | Medium   | Cassandra       |
| SWIM indirect probe | 1-2 rounds           | Very Low                | Low      | Consul, etcd    |
| TCP keepalive       | Minutes (OS default) | Low                     | Very Low | TCP connections |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                    |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| One missed heartbeat means the node is dead  | Best practice: require `failureThreshold` (2-3) consecutive misses to reduce false positives                                                                                               |
| Short heartbeat interval means fast recovery | Short interval increases CPU + network load; fast recovery requires tuning interval AND timeout ratio together                                                                             |
| Heartbeat proves the node is healthy         | Heartbeat only proves the node is alive and able to send TCP packets. A "healthy" heartbeat can come from an OOM-deadlocked process that was given CPU just long enough to send the packet |

---

### 🚨 Failure Modes & Diagnosis

**Cascading False-Positive Failure Declaration**

**Symptom:** During high GC pauses or network congestion, multiple healthy nodes are
declared dead simultaneously; cluster triggers mass re-elections and restarts;
latency spikes to seconds; cascading downtime despite nodes being alive.

Cause: heartbeat timeout is too tight relative to GC pause duration or p99 RTT.

**Fix:** Tune timeout = 2-3× p99 RTT. Use phi accrual (adaptive threshold) instead of
fixed timeout. Add `failureThreshold=3` to Kubernetes probes. Add GC pause
monitoring; alert if GC pause > heartbeat_interval × 0.5 to catch mis-tuning early.

---

### 🔗 Related Keywords

- `Gossip Protocol` — distributes heartbeat state across cluster using epidemic propagation
- `Circuit Breaker` — acts on repeated failures detected by heartbeat equiv. at service call level
- `Raft` — uses AppendEntries as leader heartbeat to suppress follower elections
- `Leader Election` — triggered when heartbeat timeout fires with no active leader

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  HEARTBEAT: periodic "I'm alive" signal                  │
│  Push: sender initiates (Raft leader → followers)        │
│  Pull: monitor polls (Kubernetes liveness probe)         │
│  Detection latency = interval × failureThreshold         │
│  Timeout must exceed p99 RTT to avoid false positives    │
│  Phi accrual: adaptive threshold → fewer false positives │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes pod serves HTTP traffic with a liveness probe: `periodSeconds=5`, `failureThreshold=3`, `timeoutSeconds=1`. A rare but reproducible bug causes the pod to stop responding to `/healthz` for 12 seconds before recovering. Will Kubernetes kill the pod? Show your calculation. What is the minimum `failureThreshold` that prevents an automatic restart in this scenario?

**Q2.** Raft requires `heartbeat_interval < election_timeout`. A production cluster uses heartbeat=150ms, election_timeout=300–600ms (randomized). A network partition isolates the leader for exactly 200ms then recovers. Trace through what happens: does a new leader get elected? What if the partition lasts 350ms? What observable effect does this have on client requests during the partition and during recovery?
