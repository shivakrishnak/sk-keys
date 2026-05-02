---
layout: default
title: "Hinted Handoff"
parent: "Distributed Systems"
nav_order: 625
permalink: /distributed-systems/hinted-handoff/
number: "0625"
category: Distributed Systems
difficulty: ★★☆
depends_on: Quorum, Replication Strategies, Read Repair
used_by: Cassandra, DynamoDB, Riak, ScyllaDB
related: Anti-Entropy, Read Repair, Quorum, Gossip Protocol, Eventual Consistency
tags:
  - distributed
  - consistency
  - repair
  - availability
  - intermediate
---

# 625 — Hinted Handoff

⚡ TL;DR — Hinted handoff is a write-side availability mechanism where, if a target replica is temporarily unavailable, the coordinator stores the write as a "hint" and delivers it to the target when it recovers — allowing the cluster to accept writes at full quorum even when one replica is briefly down, without permanently losing the write.

| #625 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Quorum, Replication Strategies, Read Repair | |
| **Used by:** | Cassandra, DynamoDB, Riak, ScyllaDB | |
| **Related:** | Anti-Entropy, Read Repair, Gossip Protocol, Quorum, Eventual Consistency | |

### 🔥 The Problem This Solves

**THE TEMPORARY DOWNTIME PROBLEM:**
In a 3-replica database cluster, a target replica goes down for 10 minutes (garbage collection pause, brief network blip, rolling restart). With strict quorum writes (W=ALL), you'd have to reject all writes during that 10 minutes — unacceptable for production. With W=QUORUM=2, writes succeed to the 2 available replicas. But now Replica 3 is permanently missing those 10 minutes of writes. When it comes back, those writes are lost — unless something saved them.

**HINTED HANDOFF:**
The coordinator (the node that received the client's write request) saves the write locally as a "hint" addressed to the unavailable Replica 3. When Replica 3 comes back (detected via gossip), the coordinator delivers the queued hints. Replica 3 catches up on the missed writes. The cluster looks like Replica 3 was never absent.

---

### 📘 Textbook Definition

**Hinted Handoff** is a write-side repair mechanism in distributed databases where, when a write cannot be delivered to its target replica (due to the replica being down or unreachable), the write coordinator stores the write as a "hint" (a record of the pending write + its target). When the target replica recovers, the coordinator detects recovery (via gossip) and delivers (replays) all stored hints. **Key properties**: (1) **Hint TTL**: hints are stored for a limited time (e.g., 3 hours in Cassandra, configurable). If the target doesn't recover within the TTL, hints expire and are discarded — the target permanently misses those writes (anti-entropy must recover them). (2) **write_request_timeout**: coordinators only create hints for nodes detected as down within the write timeout; nodes that are up but slow don't trigger hints. (3) The receiving coordinator acts as a "proxy" storage for the downed node's incoming writes. **Used in**: Cassandra (`hints` system table), Amazon Dynamo (original paper), Riak, ScyllaDB.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When a replica is temporarily down, the coordinator stores the write as a "hint" and delivers it when the replica recovers — letting the cluster stay available and eventually consistent without losing recent writes.

**One analogy:**
> You need to deliver a package to Apartment 3B, but the resident isn't home. Instead of returning the package (rejecting the write), the building superintendent (coordinator) holds the package (hint). When the resident returns and checks in (gossip recovery detection), the superintendent delivers the package. The resident catches up on everything they missed. But if the package sits unclaimed for 3 hours (hint TTL), the delivery service shreds it (hint expires) — the resident must reconcile with the main inventory separately (anti-entropy).

**One insight:**
Hinted handoff is a "write buffer for temporarily-unavailable nodes." Its critical limitation is the hint TTL: if a node is down for longer than the hint TTL, hints expire and the write is lost from the hinted perspective. Anti-entropy (nodetool repair) is the fallback for every scenario where hints expire before delivery.

---

### 🔩 First Principles Explanation

**HINTED HANDOFF FLOW:**
```
Setup: RF=3 (Replicas: A, B, C)
Coordinator receives write for key K → must write to A, B, C.

Normal write (all nodes up):
  Coordinator → A: WRITE K=v1 ✓
  Coordinator → B: WRITE K=v1 ✓
  Coordinator → C: WRITE K=v1 ✓
  Quorum achieved. Done.

Hinted handoff (Node C is down):
  Coordinator → A: WRITE K=v1 ✓
  Coordinator → B: WRITE K=v1 ✓
  Coordinator → C: WRITE K=v1 ✗ (timeout, node down)
  
  Coordinator detects C is down via gossip.
  Coordinator stores hint locally:
    {
      target: "Node C",
      key: K,
      value: v1,
      timestamp: T1,
      expires_at: T1 + hint_window (3 hours)
    }
  
  Quorum achieved (A + B = 2 of 3). Write returns success to client.
  
  Node C recovers at T1 + 30 minutes:
    Gossip propagates: "Node C is UP" to all nodes.
    Coordinator (and any other node storing hints for C) detects C is up.
    Coordinator replays hints to C:
      C receives: WRITE K=v1 (with original timestamp T1)
    C now has K=v1. Cluster fully converged.

Node C down for 4 hours (> hint TTL of 3 hours):
  All hints expire after 3 hours.
  C comes back: K is missing on C.
  Read repair: if K is later read with R=QUORUM, C's absence is detected.
    If C is included in read, digest mismatch → repair C.
    If C is NOT included (other nodes answer quorum), C stays stale.
  Anti-entropy: nodetool repair will eventually find and repair K on C.
```

**CASSANDRA HINTED HANDOFF CONFIGURATION:**
```yaml
# cassandra.yaml — key hinted handoff settings

# Enable hinted handoff (default: true)
hinted_handoff_enabled: true

# Maximum time to store hints for a down node
# (node must recover within this window for hints to be delivered)
max_hint_window_in_ms: 10800000  # 3 hours (default)

# Throttle hint delivery to recovering nodes (KB/s per thread)
# Too fast: overwhelms a recovering node; too slow: recovery takes longer
hinted_handoff_throttle_in_kb: 1024  # 1MB/s (default)

# Maximum number of hints written per second (across the cluster)
# Prevents hints from overwhelming the coordinator's disk
max_hints_delivery_threads: 2  # 2 threads sending hints concurrently

# Where hints are stored on coordinator:
# $CASSANDRA_DATA_DIR/hints/{target_node_id}/*.hints
```

**HINT EXPIRY AND ANTI-ENTROPY INTERACTION:**
```
Timeline of correct failure recovery:

T=0:    Node C goes down.
T=0..3h: Coordinator stores hints for Node C (up to hint window).
T=3h:   hint window expires. New writes are NOT hinted to C anymore.
         Old hints (T=0..3h) are still stored for delivery.

T=0..10d: gc_grace_seconds window (default 10 days).
         Any delete tombstones created during C's absence are still on A, B.
         Anti-entropy must run BEFORE T+10d to propagate tombstones to C.

T=4h:    Node C comes back.
         Hints from T=0..3h → delivered to C. C receives 3 hours of writes.
         But: writes from T=3h..4h are NOT hinted.
         C is still missing 1 hour of writes (T=3h to T=4h).
         
T=4h+:  Read repair (probabilistic): reads that happen to hit C detect stale data.
T=next repair: nodetool repair / anti-entropy fills the remaining gap.

Key insight: hinted handoff covers ONLY hint_window.
Beyond hint_window: anti-entropy is the only guaranteed recovery.
```

---

### 🧪 Thought Experiment

**THE INTERACTION BETWEEN QUORUM AND HINTED HANDOFF:**

With RF=3, W=QUORUM=2, hint_window=3 hours:
- 3 nodes: A, B, C
- C is down. Coordinator is A.
- Client writes K=v1: A writes to itself ✓, B ✓, stores hint for C.
- After 2 hours, client writes K=v2: A writes to itself ✓, B ✓, stores hint for C.
- After 4 hours (> hint window): client writes K=v3: A ✓, B ✓, NO hint for C.
- C comes back at hour 5.

What does C have? After hint delivery: K=v1, K=v2.
C is missing K=v3. C serves stale K=v2 if hit by R=1 reads.
Anti-entropy must run to deliver K=v3 to C.

This is exactly the "hint window gap" you must close with anti-entropy.

---

### 🧠 Mental Model / Analogy

> Hinted handoff is like an email "out of office" with message forwarding. When Node C is down (out of office), a proxy (coordinator) stores all incoming messages (writes/hints) and delivers them when C returns. But the forwarding service only keeps messages for 3 hours (hint TTL). If C is out for 4 hours: messages from hours 0–3 are forwarded when C returns; messages from hour 3–4 were never stored. C is missing the last hour. The post office (anti-entropy) handles the overflow — it will eventually compare C's mailbox with others and fill in whatever the forwarding service missed.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Hinted handoff lets writes succeed when one replica is down by having the coordinator save the write and deliver it when the node recovers. The hint has a TTL (3 hours in Cassandra) — if the node is down longer, hints expire and anti-entropy must fill the gap.

**Level 2:** Hints are stored in Cassandra's `system.hints` table (pre-4.0) or in hint files on coordinator nodes (4.x). Hint delivery is throttled to prevent overwhelming a recovering node. `hinted_handoff_enabled: true` is the default; disabling it makes long node outages much harder to recover from. Hints are per-write, per-target-node. A coordinator stores hints for any of its replicas that are down.

**Level 3:** Hinted handoff interacts critically with gc_grace_seconds. If Node C is down for > gc_grace_seconds (10 days default): tombstones (deletes) from A and B are GC'd before C returns. When C comes back: hints contain original mutations but tombstones are gone. Deletes that occurred during C's absence will NOT be delivered (tombstones GC'd) → zombie rows on C. Rule: never let a node be down for > gc_grace_seconds without running anti-entropy on the full ring immediately on recovery. Cassandra 4.x introduced "global hints service" — hints are node-independent and more resilient to coordinator failure.

**Level 4:** Hinted handoff in the context of CAP theorem: it's part of the "A" side of choosing AP. By storing hints and accepting writes during replica unavailability, the cluster maintains availability. This sacrifices immediate consistency (C is diverged) but allows recovery to full consistency later (eventual consistency via hints + anti-entropy). In a CP system (etcd/ZooKeeper-like), writes are rejected if quorum is not met — no hinted handoff concept. The failure mode unique to hinted handoff: "hint bomb" — a node is down for 2 hours, accumulating millions of hints. When it recovers, hint delivery generates massive write I/O on the recovering node, potentially causing cascading overload (the recovering node can't catch up before becoming overloaded again). Mitigation: `hinted_handoff_throttle_in_kb` + observe recovery I/O before removing the node from rotation.

---

### ⚙️ How It Works (Mechanism)

**Monitoring Hinted Handoff in Production:**
```bash
# Check hint counts per target node (Cassandra):
nodetool tpstats | grep -i hint

# Check hints directory size:
du -sh /var/lib/cassandra/hints/

# How many hints are queued for each target node:
nodetool statushandoff

# Watch hint delivery rate (should increase when down node recovers):
nodetool tpstats | grep HintedHandoff

# Health indicators:
# Hints directory > 1GB: a node has been down for a while.
# HintedHandoffStage pending > 0 for hours: hint delivery is stuck.
# Hints present but statushandoff shows 0: hints for already-recovered nodes (stale).

# Disable hint delivery temporarily during controlled outage:
nodetool pausehandoff

# Re-enable hint delivery:
nodetool resumehandoff

# After a long node outage (> hint window): run anti-entropy immediately:
nodetool repair -pr -seq keyspace table
```

**ScyllaDB Hinted Handoff Enhancement:**
```
ScyllaDB improves Cassandra's hinted handoff with per-shard hint queues:
  - Each CPU core (shard) maintains its own hint queue for each target node.
  - Parallel hint delivery: all shards deliver hints concurrently on recovery.
  - Faster catch-up: recovering node receives hints from all CPU cores simultaneously.
  - Per-shard hint files: no global lock contention on hint writes/reads.

Delivery throttle:
  scylla.yaml:
    hints_directory: /var/lib/scylla/hints
    max_hint_window_in_ms: 10800000   # 3 hours
    hinted_handoff_throttle_in_kb: 10240  # 10MB/s (ScyllaDB handles more I/O)
```

---

### ⚖️ Comparison Table

| Repair Mechanism | When It Fires | What It Covers | TTL / Scope |
|---|---|---|---|
| Hinted Handoff | Write time (target node down) | Writes during node downtime (within hint window) | Hint TTL (3h default) |
| Read Repair | Read time (digest mismatch) | Specific read keys (hot data) | Per-read (probabilistic) |
| Anti-Entropy | Background schedule | ALL keys unconditionally | Full partition scan |
| W=ALL Quorum | Every write (prevents divergence) | Prevents all divergence | No recovery needed |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Hinted handoff means a node can be down indefinitely without data loss | Hints expire after the hint window (3 hours by default). After that, writes are no longer hinted. Anti-entropy is needed to repair the remaining gap |
| Hints are delivered "immediately" when the node recovers | Hint delivery is throttled (default 1MB/s per thread). For a node that was down for 3 hours with 1000 writes/sec, hint backlog = ~10.8 million writes. Delivery at 1MB/s may take hours |
| Disabling hinted handoff makes the cluster more available | Disabling hinted handoff means a crashed node will have permanently missed writes until manually repaired. It reduces recovery quality, not write availability (writes still succeed at quorum) |

---

### 🚨 Failure Modes & Diagnosis

**"Hint Bomb" — Recovering Node Overwhelmed by Hints**

Symptom: Node C was down for 2.5 hours (within hint window). On recovery,
nodetool tpstats shows HintedHandoffStage: 2,000,000 pending.
Node C's CPU at 100%, I/O at saturation. Read latency on Node C spikes to 5s.
After 10 minutes of hint delivery, Node C throws OOM errors and crashes again.
Cycle repeats: C recovers → hint bomb → C crashes → repeat.

Cause: During the 2.5-hour outage, the cluster was writing at 300K writes/sec.
2.5h × 300K/s = 2.7 billion hints stored. At hint delivery rate of 1MB/s
(~1000 mutations/sec), estimated delivery time = 2.7 million seconds. Meanwhile,
Node C is also serving live traffic and running compaction. Total overload.

Fix: 
1. Pause hint delivery: `nodetool pausehandoff`
2. Allow Node C to stabilize (compaction catches up, live traffic normalizes).
3. Throttle hint delivery more aggressively:
   ALTER SYSTEM SET hinted_handoff_throttle_in_kb = 256;  (0.25MB/s)
4. Resume handoff: `nodetool resumehandoff`
5. Monitor: set alert on HintedHandoffStage pending > 100K.

Prevention:
- If hint backlog is expected to be very large: decommission the node,
  bootstrap a replacement, which streams data from other replicas
  (faster than hint delivery for large datasets).
- Set max_hint_window_in_ms lower (1 hour) to bound hint accumulation.
  Accept: nodes down > 1 hour require anti-entropy vs. hint delivery.

---

### 🔗 Related Keywords

- `Anti-Entropy` — the safety net for writes not covered by hints (expired TTL)
- `Read Repair` — fix divergence detected during reads
- `Quorum` — the consistency level that works with hinted handoff
- `Gossip Protocol` — how coordinators learn that a downed node has recovered
- `Eventual Consistency` — the model that hinted handoff helps achieve

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  HINTED HANDOFF                                          │
│  Purpose: don't lose writes when a replica is briefly   │
│           down — store them and deliver on recovery      │
│  Storage: coordinator stores hints for downed replica   │
│  TTL: hint_window (default 3 hours in Cassandra)        │
│  Delivery: throttled replay on recovery (gossip detects)│
│  Limitation: only covers downtime within hint window    │
│  Beyond window: anti-entropy (nodetool repair) needed   │
│  Risk: hint bomb on recovery of high-load nodes         │
│  Config: hinted_handoff_throttle_in_kb (Cassandra)      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Cassandra node was down for exactly 4 hours. The hint window is 3 hours. After recovery, what specific category of writes is delivered by hinted handoff, and what specific category remains missing? Draw a timeline showing: hint-covered writes, hint-expired writes, which consistency mechanism handles each category, and the risk window for stale reads on the recovered node.

**Q2.** DynamoDB's hinted handoff is internal and operator-invisible. When a DynamoDB partition is unavailable for a write (behind the scenes), the write is queued and later delivered. As an application developer using DynamoDB, what observable behaviors should you watch for that indicate hinted handoff is delivering "catch-up" writes to your application, and how should your application be designed to handle a burst of stale-then-fresh reads on the same keys?
