---
layout: default
title: "ISR (In-Sync Replicas)"
parent: "Big Data & Streaming"
nav_order: 18
permalink: /big-data-streaming/isr-in-sync-replicas/
id: BIG-018
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Kafka, Kafka Topic / Partition / Offset
used_by: Kafka Replication, Producer Durability, Leader Election
related: Apache Kafka, Kafka Topic / Partition / Offset, Log Compaction
tags:
  - kafka-isr
  - replication
  - durability
  - leader-election
  - deep-dive
---

# BIG-018 — ISR (In-Sync Replicas)

⚡ TL;DR — **ISR (In-Sync Replicas)** is the set of Kafka partition replicas that are **fully caught up** with the partition leader (within `replica.lag.time.max.ms`, default 30s); producers with `acks=all` wait for ALL ISR members to acknowledge a write — guaranteeing no data loss as long as at least one ISR member survives; replicas falling behind are removed from ISR, and the leader only commits messages that all ISR replicas have acknowledged.

| #543            | Category: Big Data & Streaming                                 | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, Kafka Topic / Partition / Offset                 |                 |
| **Used by:**    | Kafka Replication, Producer Durability, Leader Election        |                 |
| **Related:**    | Apache Kafka, Kafka Topic / Partition / Offset, Log Compaction |                 |

---

### 🔥 The Problem This Solves

**DURABILITY WITHOUT WAITING FOR SLOW REPLICAS:**
With `acks=all`, you want to wait for enough replicas to confirm a write for durability. But if one replica is slow (garbage collection pause, network issue), waiting for it would add seconds of latency to every write. ISR solves this: only replicas that are keeping up with the leader are in the ISR. `acks=all` waits only for ISR members — if a replica falls behind and leaves the ISR, writes proceed without waiting for it. If it recovers, it catches up and re-joins the ISR.

---

### 📘 Textbook Definition

**ISR (In-Sync Replicas)**: the dynamic set of partition replicas that have fully replicated the leader's log. A replica is considered in-sync if it has fetched all messages from the leader within `replica.lag.time.max.ms` (default: 30 seconds).

**High Watermark (HW)**: the offset up to which all ISR replicas have acknowledged. Consumers can only read up to the high watermark — data above HW is "uncommitted" (replicated to some but not all ISR members).

**Leader Epoch**: a monotonically increasing counter that changes with each leader election. Used to detect stale replicas after failover and prevent "zombie" leaders from overwriting valid data.

**`min.insync.replicas`**: minimum number of ISR replicas that must acknowledge a write for it to succeed (with `acks=all`). If ISR size drops below this threshold: the broker rejects writes with `NotEnoughReplicasException` — preventing silent data loss.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ISR = set of replicas fully caught up with leader; `acks=all` waits for all ISR members; `min.insync.replicas=2` + `replication.factor=3` = tolerate 1 broker failure without data loss.

**One analogy:**

> A choir (Kafka partition). The conductor (leader) sets the tempo. "In-sync" singers (ISR) are those who can keep up. If a singer falls behind (replica lag), they're asked to step back (removed from ISR). For a note to be "officially performed" (`acks=all`): all in-sync singers must have sung it. If one singer is on a bathroom break (ISR shrinks): the remaining ISR still performs. If fewer than `min.insync.replicas` singers remain: the performance is halted (writes rejected) — better to pause than perform incorrectly.

**One insight:**
`replication.factor=3, min.insync.replicas=2` is the most important Kafka durability configuration. Three replicas: always 1 broker can be down without affecting writes. The ISR guarantees: any message acknowledged by the leader is on at least 2 servers. Even if the leader crashes immediately after acknowledging: the data is on the standby (ISR follower) and won't be lost. This is the standard production configuration for critical topics.

---

### 🔩 First Principles Explanation

**REPLICATION FLOW:**

```
Partition "orders-P0" configuration:
  replication.factor=3
  min.insync.replicas=2

Broker assignment:
  Leader: Broker 1 (handles reads and writes from producers/consumers)
  Follower: Broker 2 (replicates from leader)
  Follower: Broker 3 (replicates from leader)

ISR = [Broker1, Broker2, Broker3]  (all 3 initially in-sync)

WRITE FLOW (acks=all):
  1. Producer → Broker1 (leader): write message M at offset 100
  2. Broker1: appends M to local log
  3. Broker2: fetch request to Broker1 → pulls M → appends locally → ACK to Broker1
  4. Broker3: fetch request to Broker1 → pulls M → appends locally → ACK to Broker1
  5. Broker1: all ISR replicas have M → move High Watermark to 101
     → send ACK to Producer (acks=all satisfied)

  Consumer read: only up to High Watermark (101-1 = 100)
  Message M is now "committed" — safe to consume

  Timeline:
  T=0ms: Producer writes M
  T=5ms: Broker2 fetches and replicates M
  T=6ms: Broker3 fetches and replicates M
  T=7ms: HW advances → Producer ACK sent
  → Total write latency with acks=all: ~7ms (vs ~1ms for acks=1)
```

**ISR SHRINKS AND GROWS:**

```
Scenario: Broker3 experiences a 60-second GC pause

T=0: Broker3 last fetched at offset 500 (all 3 in ISR)
T=30s: Broker3 hasn't fetched for 30s > replica.lag.time.max.ms (default 30s)
  → Broker1 (leader): removes Broker3 from ISR
  → ISR = [Broker1, Broker2]  (size=2, which meets min.insync.replicas=2)
  → Writes continue with acks=all, but now only wait for Broker2

T=60s: Broker3 GC completes, starts fetching again from offset 501
  → Broker3 catches up to current offset (500→600)
  → Once caught up: Broker1 adds Broker3 back to ISR
  → ISR = [Broker1, Broker2, Broker3]

What if Broker2 also fails during the GC pause?
  → ISR = [Broker1] only (size=1, below min.insync.replicas=2)
  → Writes fail with NotEnoughReplicasException
  → Producers: must handle this exception and retry
  → This is intentional: better to reject writes than risk data loss

What if min.insync.replicas=1 (unsafe)?
  → Single ISR member can acknowledge writes
  → If that broker crashes: data in-flight is lost
  → Never use min.insync.replicas=1 for critical data
```

**UNCLEAN LEADER ELECTION:**

```
Scenario: Leader (Broker1) crashes permanently
  ISR at time of crash: [Broker1] only (Broker2 and Broker3 are behind by 100 messages)

  unclean.leader.election.enable=false (default, recommended):
    → No non-ISR replica can become leader
    → Topic partition is OFFLINE until an ISR member is available
    → If Broker1 is unrecoverable: manual intervention required
    → Prevents data loss but causes availability loss

  unclean.leader.election.enable=true (NOT recommended):
    → Any follower (even one behind by 100 messages) can become leader
    → New leader has offsets up to offset X (missing last 100 messages)
    → Consumers who already read messages up to offset X+100:
      those messages are now "unwritten" (data loss)
    → May also cause offset confusion
    → Only use when availability is more critical than consistency

Best practice:
  replication.factor=3
  min.insync.replicas=2
  unclean.leader.election.enable=false

  → Tolerate 1 broker failure: ISR=[Broker1,Broker2,Broker3] → Broker1 fails
    → ISR=[Broker2,Broker3] (size=2 = min.insync.replicas)
    → Broker2 or Broker3 elected leader (one of them IS in ISR)
    → No data loss, no unavailability
```

**CONFIGURATION REFERENCE:**

```yaml
# Server config (broker level):
default.replication.factor=3            # replicate each partition to 3 brokers
min.insync.replicas=2                   # require 2 ISR acks for acks=all
unclean.leader.election.enable=false    # safety: no stale leader
replica.lag.time.max.ms=30000           # ISR membership window (30s)

# Topic-level override (overrides broker defaults for this topic):
kafka-topics.sh --create \
  --topic critical-payments \
  --replication-factor 3 \
  --partitions 6 \
  --config min.insync.replicas=2 \
  --config unclean.leader.election.enable=false

# Producer config:
acks=all                     # wait for all ISR
enable.idempotence=true      # deduplicate retries
max.in.flight.requests.per.connection=5  # 5 unconfirmed (safe with idempotence)
retries=2147483647           # retry indefinitely on transient errors
delivery.timeout.ms=120000   # give up after 2 minutes total
```

---

### 🧪 Thought Experiment

**HIGH WATERMARK AND CONSUMER VISIBILITY:**

Producer writes messages M100, M101, M102 to the leader.

- Leader: has M100, M101, M102
- Broker2 (ISR follower): has M100, M101 (hasn't replicated M102 yet)
- Broker3 (ISR follower): has M100 (behind by 2)

High Watermark = min(replicated offset across all ISR) = 100 (Broker3's position).

Consumer: can only read up to offset 100. Cannot read M101, M102 yet.

Why? If the leader crashes now and Broker3 becomes leader, Broker3 doesn't have M101, M102. If a consumer had already read M101 (before HW), it would have "read" data that doesn't exist on the new leader — inconsistency.

Solution: High Watermark guarantees all ISR replicas have the data before consumers can read it. This adds some latency (consumer sees HW, not the latest offset) but ensures consistency across leader failover.

---

### 🧠 Mental Model / Analogy

> ISR is like a multi-city backup system for a bank ledger. The master copy (leader) is in New York. Backup copies are in Chicago and Los Angeles (followers). "In-sync" means the backup is up-to-date (checked in within the last 30 seconds). A transaction is only "confirmed" (`acks=all`) when both Chicago AND Los Angeles have confirmed they have a copy (High Watermark advances). If Los Angeles goes offline for maintenance (removed from ISR): New York + Chicago still confirm transactions. But if Chicago also goes offline (ISR size < min.insync.replicas): New York refuses new transactions — better to pause than create records that might be lost.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** ISR = replicas fully caught up with leader. `acks=all`: wait for all ISR to confirm → no data loss. `min.insync.replicas=2`: reject writes if fewer than 2 ISR → safety over availability. Standard: `replication.factor=3, min.insync.replicas=2`.

**Level 2:** High Watermark: consumers only see committed messages (acknowledged by all ISR). When a replica lags > `replica.lag.time.max.ms` (30s): removed from ISR. After catching up: re-added. `unclean.leader.election.enable=false`: no stale follower can become leader (prevents data loss but may cause unavailability).

**Level 3:** ISR maintenance: broker controller tracks ISR changes. On ISR shrink/grow: controller updates ZooKeeper/KRaft and notifies all brokers. Leader epoch: monotonically increasing counter per leader election. Used to detect "zombie" followers that try to replicate from a stale leader. On recovery: follower truncates log to last known HW before re-joining ISR to ensure log consistency.

**Level 4:** The ISR design is a form of **quorum-based replication** (similar to Raft's commit rule), but with a dynamic quorum (ISR size changes). Unlike Raft (static majority quorum), Kafka's ISR quorum is "all members that are caught up." This means: with 3 replicas, ISR might shrink to 1 (if 2 are slow) and `acks=all` would only require 1 ACK — violating the durability goal. `min.insync.replicas` is the safety floor that prevents ISR from shrinking too far. In practice, set `min.insync.replicas = floor(replication.factor/2) + 1` for majority quorum.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ KAFKA REPLICATION — PARTITION "orders-P0"            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Producer (acks=all)                                 │
│       ↓ write                                        │
│  [Leader: Broker1] offset=100 → move HW to 101 ←─┐ │
│       ↑                                            │ │
│  Broker2 (ISR): fetch → replicates → ACK ──────────┤ │
│  Broker3 (ISR): fetch → replicates → ACK ──────────┘ │
│                                                      │
│  Consumer: reads up to High Watermark only (101)     │
│  [ISR ← YOU ARE HERE: dynamic quorum for durability] │
│                                                      │
│  If Broker3 lags > 30s: ISR=[Broker1,Broker2]       │
│  min.insync.replicas=2 still satisfied → writes ok   │
│  If Broker2 also lags: ISR=[Broker1] < 2 → REJECT   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Write with acks=all, min.insync.replicas=2, replication.factor=3:

1. Producer → Broker1 (leader): write order event M at offset 100
2. Broker1: appends M to local segment file (offset 100)
3. Broker2 (follower): fetch request → Broker1 sends M → Broker2 appends
4. Broker3 (follower): fetch request → Broker1 sends M → Broker3 appends
5. High Watermark: all 3 ISR have offset 100 → HW advances to 101
6. Broker1 → Producer: ACK (acks=all satisfied)

Consumer can now read offset 100.

Broker3 GC pause (60s):
1. Broker3 stops fetching for 30s
2. Broker1: removes Broker3 from ISR → ISR=[Broker1,Broker2]
3. Producer write M101: Broker2 replicates → HW moves to 102 (2 ISR = min)
4. Broker3 recovers: fetches from offset 100, catches up to 101
5. Broker1: adds Broker3 back to ISR → ISR=[Broker1,Broker2,Broker3]

Broker1 crashes:
1. Controller: detects Broker1 failure (ZooKeeper/KRaft session expires)
2. ISR at time of crash: [Broker1,Broker2,Broker3]
3. Controller: elects Broker2 (first in ISR list) as new leader
4. Broker2: starts serving reads and writes for partition 0
5. Broker3: now follows Broker2
6. No data loss: Broker2 had all committed messages (was in ISR)
```

---

### ⚖️ Comparison Table

| Config                    | Durability                     | Availability                 | Use Case                   |
| ------------------------- | ------------------------------ | ---------------------------- | -------------------------- |
| acks=0                    | None (fire & forget)           | Maximum                      | Metrics, logging (loss OK) |
| acks=1                    | Leader ack only                | High                         | Moderate importance        |
| acks=all, min.isr=1       | Weak (same as acks=1 if ISR=1) | High                         | Don't use                  |
| acks=all, min.isr=2, rf=3 | Strong (standard)              | Good (survives 1 failure)    | Financial, critical data   |
| acks=all, min.isr=3, rf=3 | Strongest                      | Lower (any failure = reject) | Extreme durability         |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                       |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "replication.factor=3 guarantees no data loss"           | Without `acks=all + min.insync.replicas=2`, replication is async. With `acks=1`: leader acks before replicas have the data. Leader crash between ack and replication = data loss despite RF=3 |
| "min.insync.replicas means ISR must always be that size" | `min.insync.replicas` is only checked when a producer writes with `acks=all`. It doesn't prevent the ISR from shrinking below that threshold — it rejects WRITES if ISR is below threshold    |
| "unclean.leader.election=true is safe"                   | Unclean leader election allows a lagging replica (not in ISR) to become leader. Messages that were on the old leader but not replicated to the new leader are permanently lost                |

---

### 🚨 Failure Modes & Diagnosis

**1. NotEnoughReplicasException — Writes Rejected**

**Symptom:** Kafka producers start failing with `org.apache.kafka.common.errors.NotEnoughReplicasException: The size of the current ISR Set(1) is insufficient to satisfy the min.isr requirement of 2 for partition orders-0`. Orders stop flowing.

**Root Cause:** Two brokers in the ISR went offline (maintenance, network partition, failure). ISR shrunk to 1 broker, which is below `min.insync.replicas=2`.

**Diagnosis:**

```bash
kafka-topics.sh --describe --topic orders --bootstrap-server kafka:9092
# Shows: ISR: 1 (only one broker in ISR)
kafka-broker-api-versions.sh --bootstrap-server kafka:9092
# Check which brokers are responsive
```

**Immediate action:** Restore the failed brokers. If planned maintenance: use rolling restarts (one broker at a time, ensure it re-joins ISR before stopping the next).

**Mitigation:** `unclean.leader.election.enable=true` (last resort — risks data loss). Or temporarily reduce `min.insync.replicas=1` (also risks data loss) to restore availability.

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Kafka Topic / Partition / Offset
**Builds On This:** Kafka Replication, Producer Durability
**Related:** Apache Kafka, Kafka Topic / Partition / Offset, Log Compaction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ISR         │ Replicas fully caught up (within lag.ms)  │
│ HIGH WATER  │ Max committed offset (all ISR have it)    │
│ acks=all    │ Wait for ALL ISR to confirm                │
│ min.isr=2   │ Reject writes if ISR < 2 (safety floor)  │
│ RF=3,min=2  │ Standard: survive 1 broker failure        │
│ LAG WINDOW  │ replica.lag.time.max.ms=30000 (default)   │
│ UNCLEAN     │ =false: prevent stale leader data loss    │
│ CONSUMER    │ Reads up to HW only (committed data)      │
│ DIAGNOSE    │ kafka-topics.sh --describe → ISR field    │
│ ONE-LINER   │ "ISR = caught-up replicas; acks=all waits │
│             │  for all; min.isr=2 prevents silent loss" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain the relationship between ISR, High Watermark, and consumer visibility. Why can consumers only read up to the High Watermark and not the latest offset on the leader?

**Q2.** (TYPE C — Production) A Kafka cluster has `replication.factor=3` and `min.insync.replicas=2`. During a rolling restart, you take down Broker2 (maintenance), and Broker3 unexpectedly crashes. Describe what happens to producer writes, consumer reads, and the ISR, and how you restore normal operation.
