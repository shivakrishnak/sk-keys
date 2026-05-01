---
layout: default
title: "Hinted Handoff"
parent: "Distributed Systems"
nav_order: 625
permalink: /distributed-systems/hinted-handoff/
number: "625"
category: Distributed Systems
difficulty: ★★★
depends_on: "Eventual Consistency, Anti-Entropy"
used_by: "Cassandra, DynamoDB, Voldemort, Riak"
tags: #advanced, #distributed, #replication, #repair, #availability
---

# 625 — Hinted Handoff

`#advanced` `#distributed` `#replication` `#repair` `#availability`

⚡ TL;DR — When a target replica is temporarily down, the **coordinator stores a "hint"** (the write) and **replays it to the replica when it recovers** — a write-path repair mechanism that maintains availability without sacrificing data durability.

| #625            | Category: Distributed Systems        | Difficulty: ★★★ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Eventual Consistency, Anti-Entropy   |                 |
| **Used by:**    | Cassandra, DynamoDB, Voldemort, Riak |                 |

---

### 📘 Textbook Definition

**Hinted handoff** is a write-side availability and repair mechanism in distributed databases: when a replica node is temporarily unavailable during a write, the coordinator (or another live node) stores the write as a **hint** — a temporary record that includes the target replica's node ID and the write data — and delivers that write to the target replica once it comes back online. This allows writes to succeed at quorum even when some replicas are down, while ensuring those replicas catch up when they recover. Three key components: (1) **Hint storage** — the coordinator stores hints locally (disk-backed, not in memory). (2) **Hint delivery** — when the target replica comes back up, the coordinator detects recovery (via gossip) and delivers pending hints. (3) **Hint expiry** — hints have a TTL (`max_hint_window_in_ms` in Cassandra, default 3 hours). If the node is down longer than TTL: hints expire and are discarded. Recovery then requires anti-entropy repair instead. Hinted handoff: fast repair for short outages; not a substitute for anti-entropy for longer outages.

---

### 🟢 Simple Definition (Easy)

You send a letter to your friend, but they're temporarily away. The mail carrier doesn't throw the letter away — they hold it and re-deliver it when your friend returns. "Hint" = the letter. "Coordinator" = the mail carrier that holds the letter. "Target replica recovering" = your friend coming home. BUT: if your friend is away for 3+ hours: the mail carrier can't hold letters indefinitely; they're eventually discarded. Your friend misses those letters — they need to call and ask for all missed correspondence (= anti-entropy repair).

---

### 🔵 Simple Definition (Elaborated)

Hinted handoff: optimized for short node downtime (restart, brief network blip). For Cassandra: a node restart for a rolling upgrade takes 2-5 minutes. During those 2-5 minutes: ~dozens of writes might target that node. Without hinted handoff: those writes silently succeed at quorum (2 of 3 replicas), but the restarting node misses them. With hinted handoff: coordinator stores those writes, delivers them immediately on restart. The restarting node: fully consistent within seconds of coming back up. No manual repair needed. For longer outages (> max_hint_window): hints expire → manual anti-entropy repair required.

---

### 🔩 First Principles Explanation

**Hint storage, delivery, expiry, and interaction with repair mechanisms:**

```
HINTED HANDOFF MECHANICS:

  SETUP:
    RF = 3. Write consistency = QUORUM. Needs 2 of 3 acks.
    Target replica: Node C is down (crash, maintenance restart).
    Nodes: A (coordinator), B, C (down).

  WRITE REQUEST (with hinted handoff):
    Client: WRITE user:alice = "Alice Smith" CONSISTENCY QUORUM.
    Coordinator (Node A): sends write to Node A (self), Node B, Node C.

    Node A: writes successfully. ACK.
    Node B: writes successfully. ACK.
    Node C: DOWN. No response.

    Quorum (2) met by A and B: write succeeds from client perspective.

    BUT: Coordinator (Node A) also STORES A HINT for Node C:
      Hint record:
        target_node: Node C (host ID: "abc-123")
        key: "user:alice"
        value: "Alice Smith"
        timestamp: 10:00:00.000
        created_at: 10:00:00.000
        expires_at: 10:00:00.000 + max_hint_window (3 hours) = 13:00:00.000

    Hint stored on: Node A's disk (in hints/ directory in Cassandra).
    Node A: now responsible for delivering this hint when Node C recovers.

  NODE C RECOVERY:
    Node C: comes back online at 10:15:00.
    Gossip: Node A detects Node C is alive.

    Hint delivery: Node A reads hint for Node C from hints/ directory.
    Node A: sends the write to Node C: user:alice = "Alice Smith" (timestamp 10:00:00).
    Node C: applies the write. Now consistent with A and B.
    Node A: deletes the delivered hint.

  MULTIPLE HINTS:
    Node C down for 10 minutes. 5000 writes targeted Node C. 5000 hints stored by coordinator(s).
    On recovery: all 5000 hints delivered rapidly. Node C: fully caught up in seconds.

  HINT STORAGE:
    Cassandra: hints stored in $CASSANDRA_DATA/hints/ directory.
    Format: sstable-like files. On disk, not memory. Survives coordinator crash.
    Per-target-node: separate hint directory (so hints for Node C don't mix with hints for Node D).

  HINT EXPIRY:
    max_hint_window_in_ms: default = 10800000 (3 hours).
    If Node C is down > 3 hours: hints expire and are deleted.
    Why delete: hints accumulate unboundedly if the target node never recovers.
    If hints fill disk: coordinator itself could fail (out of disk space).

    After hint expiry: Node C is missing all writes from the outage period.
    Recovery: requires anti-entropy repair (nodetool repair).

  cassandra.yaml:
    max_hint_window_in_ms: 10800000  # 3 hours.
    # Increase if nodes frequently down for > 3 hours but < extended outage.
    # Risk: hints disk space grows proportional to write rate × downtime window.

    hints_flush_period_in_ms: 10000  # Flush hints to disk every 10s.
    # Lower: hints survive coordinator crash more quickly. Higher: less I/O.

    max_hints_delivery_threads: 2    # Threads for delivering hints to recovered nodes.
    # More threads: faster hint delivery after recovery.
    # More CPU/network during delivery burst.

HINTED HANDOFF ARCHITECTURE (WHERE HINTS LIVE):

  COORDINATOR-STORES MODEL (Cassandra default):
    The coordinator that received the write stores the hint.
    Problem: coordinator may also crash → hints lost.
    Mitigation: hints are disk-backed (survive coordinator restart). Not memory.

  DISTRIBUTED HINTS MODEL (alternative):
    Store hints on multiple nodes (like a replicated hints queue).
    Higher durability: hints survive coordinator failure.
    More complex implementation.

  CASSANDRA IMPROVEMENT (Cassandra 3.x+):
    Improved hint delivery: parallelized per-node hint delivery.
    Hint tables: stored in system.hints system table (Cassandra 3.x).
    Batch hint delivery: delivers multiple hints in one streaming session (efficient for burst recovery).

INTERACTION WITH OTHER REPAIR MECHANISMS:

  WRITE PATH:
    Write → Coordinator → all target replicas.
    Replica down → store hint → deliver on recovery.
    (Hinted handoff)

  READ PATH:
    Read → Coordinator → multiple replicas.
    Divergence detected → repair stale replicas inline.
    (Read repair)

  BACKGROUND:
    Periodic scan → Merkle tree comparison → stream divergent ranges.
    (Anti-entropy / nodetool repair)

  COMPLEMENTARY ROLES:
    Hinted handoff: handles SHORT outages (< 3 hours). Writes are buffered and delivered.
    Read repair: handles ONLINE divergence on read path. Hot data kept consistent.
    Anti-entropy: handles LONG outages and COLD data. Full scan ensures all data consistent.

  TYPICAL SCENARIO (rolling restart):
    Node C restarted for maintenance. Down 3 minutes.
    Writes during downtime: handled by hinted handoff (coordinator stores hints).
    On restart: hints delivered instantly. Node C fully consistent.
    No manual repair needed for the 3-minute window.

SPECULATIVE WRITES AND HINTED HANDOFF:

  Some systems: use hinted handoff with speculative retry.
  If a replica doesn't respond within timeout: send write to EXTRA replica (speculation).
  Also store hint for original target.

  Benefit: lower write latency (don't wait for slow replica).
  Risk: extra write load during speculation.

  Cassandra: `write_request_timeout_in_ms` (default 2 seconds).
  Hint stored: after timeout, not immediately on first failure.

HINTED HANDOFF LIMITS:

  1. HINT DISK SPACE:
     Hints = all missed writes during downtime.
     High write rate + long downtime = large hint files.
     1 million writes/sec × 1 hour = 3.6 billion hint entries.
     At 100 bytes each: 360 GB of hints. Must limit via max_hint_window.

  2. HINT DELIVERY BURST:
     Node recovers after 3 hours (just before hint expiry).
     All hints delivered at once: burst of writes to recovering node.
     Recovering node: simultaneously receiving hints + serving new traffic.
     Can cause recovery overload. Mitigation: throttle hint delivery.

     hints_throttle_in_kb: 1024  # Cassandra: default 1 MB/s hint delivery rate.
     Slower hint delivery: recovering node not overwhelmed.

  3. COORDINATOR-SPECIFIC:
     If coordinator storing hints crashes BEFORE delivering them:
     Hints survive (disk-backed) and are delivered after coordinator restarts.
     If coordinator disk fails: hints for that node permanently lost.
     Anti-entropy repair: must cover this case.

  4. NOT A SUBSTITUTE FOR QUORUM:
     Hinted handoff happens AFTER quorum is met.
     Write fails quorum (> 1 replica down with RF=3, CL=QUORUM): write rejected.
     No hinted handoff in this case: error returned to client.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT hinted handoff:

- Node down for 5-minute maintenance restart
- All writes during that 5 minutes: succeed at quorum (2 of 3), but 3rd replica misses them
- Node recovers: must run full anti-entropy repair to catch up all missed writes
- Anti-entropy repair: expensive, time-consuming, requires manual scheduling

WITH hinted handoff:
→ Coordinator automatically stores missed writes during brief downtime
→ Node recovers: instantly receives all missed writes within seconds
→ No manual repair needed for brief outages (< max_hint_window)
→ Availability maintained without sacrificing eventual durability

---

### 🧠 Mental Model / Analogy

> A post office delivers mail to houses. House C is temporarily closed for renovation. The mail carrier doesn't discard the letters — they hold them at the post office and re-deliver when the house reopens. BUT: if the house is closed for more than 3 months, the post office can't keep all that mail indefinitely — they return to sender (hints expire). When that happens, the house owner must contact all senders and request all missed mail (anti-entropy repair).

"Letters" = writes targeted at a replica
"House C closed for renovation" = replica Node C temporarily down
"Mail carrier holds letters" = coordinator stores hints on disk
"Re-delivers when house reopens" = hint delivery on node recovery
"3-month limit" = max_hint_window_in_ms expiry
"Contact all senders for missed mail" = anti-entropy repair after hint expiry

---

### ⚙️ How It Works (Mechanism)

```
HINTED HANDOFF WRITE FLOW:

  1. Write request: client → coordinator.
  2. Coordinator: sends to all RF replicas.
  3. Target replica C: down. Timeout/connection refused.
  4. Quorum met by other replicas: ACK to client.
  5. Coordinator: stores hint on disk for Node C.
     { target: Node-C, key: K, value: V, ts: T, expires: T+3h }
  6. Coordinator: gossips. Detects Node C recovery.
  7. Coordinator: reads pending hints for Node C.
  8. Coordinator: sends hints to Node C (streaming).
  9. Node C: applies hints. Now consistent.
  10. Coordinator: deletes delivered hints.
```

---

### 🔄 How It Connects (Mini-Map)

```
Write Path (coordinator → replicas)
        │
        ▼ (replica unavailable → store hint)
Hinted Handoff ◄──── (you are here)
(write-path buffering for temporary unavailability)
        │
        ├── Anti-Entropy: for long outages (> hint TTL) — full background repair
        ├── Read Repair: for divergence detected on reads (complement on read path)
        └── Gossip Protocol: detects when target replica recovers → triggers delivery
```

---

### 💻 Code Example

```java
// Hint storage and delivery in a simplified distributed write coordinator:
public class HintedHandoffCoordinator {

    private final HintStore hintStore; // Disk-backed hint storage.
    private final GossipService gossip;
    private static final Duration HINT_TTL = Duration.ofHours(3);

    // Write to replicas; store hints for unreachable ones:
    public WriteResult write(String key, String value, List<Replica> replicas, int quorum) {
        int acked = 0;
        for (Replica replica : replicas) {
            try {
                replica.write(key, value, timeout);
                acked++;
            } catch (NodeUnavailableException e) {
                // Node is temporarily down: store a hint instead of failing:
                if (e.isTemporary()) {  // Temporary (connection refused) vs. permanent (decommissioned).
                    Hint hint = new Hint(replica.nodeId(), key, value,
                                        Instant.now(), Instant.now().plus(HINT_TTL));
                    hintStore.store(hint);
                    log.info("Stored hint for node {} key {}", replica.nodeId(), key);
                }
                // Don't count hint toward ack. Quorum must be met by real replicas.
            }
        }
        if (acked < quorum) throw new QuorumNotMetException("Only " + acked + " of " + quorum + " acks");
        return WriteResult.SUCCESS;
    }

    // Deliver hints when node recovers (triggered by gossip):
    public void onNodeRecovery(String nodeId) {
        List<Hint> pendingHints = hintStore.getPendingHints(nodeId);
        Replica recoveredNode = clusterTopology.getReplica(nodeId);

        for (Hint hint : pendingHints) {
            if (Instant.now().isAfter(hint.expiresAt())) {
                hintStore.deleteHint(hint.id());  // Expired: discard.
                log.warn("Hint expired for node {} key {}", nodeId, hint.key());
                continue;
            }
            try {
                recoveredNode.write(hint.key(), hint.value(), hint.timestamp());
                hintStore.deleteHint(hint.id());  // Delivered: delete.
            } catch (Exception e) {
                log.error("Hint delivery failed for {}: {}", nodeId, e.getMessage());
                // Retry later. Keep hint until expiry.
            }
        }
        log.info("Delivered {} hints to recovered node {}", pendingHints.size(), nodeId);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hinted handoff makes the write durable on the target replica | Hinted handoff makes the write durable on the COORDINATOR's disk (as a hint). The TARGET replica doesn't have the data until hint delivery. If the coordinator's disk fails before delivery: hint is lost and data is permanently missing on that replica. Anti-entropy repair is the safety net for that scenario. Hinted handoff: a best-effort mechanism for short outages, not a durability guarantee |
| Hinted handoff works for any length of outage                | Hints expire (default 3 hours in Cassandra). After expiry: hints discarded to prevent disk exhaustion. A node down for 4 hours: many hints already expired. Recovery requires anti-entropy repair for the expired window + hint delivery for the recent window. Set max_hint_window based on realistic expected downtime, not the maximum                                                                 |
| Hinted handoff counts toward quorum acknowledgment           | Never. Hinted handoff is triggered AFTER quorum is met. The hint represents a DEFERRED write. The client gets an ACK because quorum was met by live replicas. The hint ensures the down node catches up later — it is not part of the write's durability guarantee. If < quorum replicas are alive: write fails (no hints help)                                                                           |

---

### 🔥 Pitfalls in Production

**Hint disk space exhaustion causes coordinator failures:**

```
SCENARIO:
  Cassandra cluster. Write rate: 500,000 writes/sec.
  Node C: hardware failure. Expected to be down 4 hours (parts shipment delay).
  Each write: average 200 bytes.

  max_hint_window_in_ms: 10800000 (3 hours default).

  Hints generated: 500,000 writes/sec × 3,600 seconds/hour × 3 hours = 5,400,000,000 hints.
  Storage: 5.4 billion hints × 200 bytes = 1.08 TB of hint files.

  Coordinator Node A: only has 500 GB free disk space.

  RESULT:
    Hour 2: Node A disk fills up. Node A FAILS (out of disk space).
    Node A: can't write. Cassandra logs: "Aborting write to hints, disk full."
    Now: TWO nodes down (Node C hardware failure + Node A out of disk).
    With RF=3 and 2 nodes down: writes FAIL quorum. Cluster write-unavailable.
    CASCADE FAILURE caused by hint accumulation.

BAD: Default hint configuration on high-write-rate cluster:
  # max_hint_window_in_ms: 10800000  # 3 hours at 500k writes/sec = 1TB hints. Disk death.

FIX 1: Reduce max_hint_window aggressively for high-write-rate clusters:
  # Calculate max hint window based on disk capacity:
  # Available hint disk space: 50 GB (dedicated partition).
  # Write rate: 500k writes/sec. Average write size: 200 bytes.
  # Max window = 50GB / (500k × 200 bytes/sec) = 50,000,000,000 / 100,000,000 = 500 seconds (~8 minutes).
  max_hint_window_in_ms: 480000  # 8 minutes.
  # After 8 minutes of downtime: hints stop accumulating. Anti-entropy handles the rest.

FIX 2: Dedicate a separate disk partition for hints:
  hints_directory: /data/cassandra/hints  # Separate partition.
  # Prevents hint growth from filling main data disk.
  # Monitor hint partition separately.

FIX 3: Monitor hint accumulation proactively:
  # Metric: TotalHintsInProgress (JMX) → number of hints waiting for delivery.
  # Metric: Hints store size on disk.
  # ALERT: hint store > 10 GB → check if target node is down, expected recovery time.
  # ALERT: hint store growing > 1 GB/minute → emergency: lower max_hint_window or drain hints.

FIX 4: For planned maintenance (expected downtime > 8 minutes):
  # Use DataStax OpsCenter / nodetool pauseHandoff before taking node down.
  # Or: use nodetool drain on the node being taken down → writes route elsewhere cleanly.
  # After maintenance: nodetool resumeHandoff.
  # Run nodetool repair after bringing node back: catch up any missed writes beyond hint window.

HINT DELIVERY MONITORING:
  JMX: org.apache.cassandra.db:type=HintedHandoffManager
    ActiveDeliveries: hints being delivered right now.
    PausedDeliveries: delivery paused (node overloaded or manually paused).

  Cassandra logs on hint delivery:
    "Scheduled hints for delivery" → hint delivery started.
    "Delivered hints for endpoint ..." → delivery complete.

  Alert: HintedHandoffManager.ActiveDeliveries = 0 but TotalHintsInProgress > 0
    → hints accumulating but not being delivered → target node still down.
```

---

### 🔗 Related Keywords

- `Anti-Entropy` — long-term repair for nodes down beyond hint TTL or cold data
- `Read Repair` — read-path repair for detecting divergence during reads
- `Gossip Protocol` — node recovery detected via gossip → triggers hint delivery
- `Eventual Consistency` — the consistency model hinted handoff helps maintain
- `Quorum Writes` — writes succeed at quorum; hinted handoff is the cleanup mechanism

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Node temporarily down: coordinator stores │
│              │ a "hint" (the write) → delivers it when  │
│              │ node recovers. Fast recovery, no manual  │
│              │ repair needed for short outages.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Brief node unavailability: restarts,     │
│              │ maintenance (< max_hint_window = 3h)     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long outages (hints expire — use repair);│
│              │ high write rate with tiny disks          │
│              │ (hint accumulation → disk exhaustion)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Mail carrier holds letters while you're │
│              │  away, re-delivers when you're back."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Anti-Entropy → Read Repair → Gossip     │
│              │ Protocol → Cassandra nodetool repair     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Cassandra has max_hint_window_in_ms = 3 hours. Node C goes down at 9:00 AM and recovers at 11:50 AM (2 hours 50 minutes — just inside the 3-hour window). Hints are stored at the coordinator. Between 9:00 and 10:00 AM: coordinator Node A received most of the writes. But at 10:05 AM, coordinator Node A was also restarted (rolling restart) and Node B became the coordinator. Where are the hints for 10:05-11:50 AM stored? Are the hints for 9:00-10:05 AM still available? What does this mean for hint delivery completeness?

**Q2.** At 11:50 AM: Node C recovers. The hint store on the coordinator contains 2 million hints (2 hours 50 minutes × estimated write rate). Node C immediately begins receiving new live traffic. Now it must simultaneously: (1) receive and apply 2 million hints, and (2) handle new live writes. Describe two failure modes that can occur during this simultaneous load. How would you design hint delivery to prevent these failure modes while still completing hint delivery within a reasonable time window?
