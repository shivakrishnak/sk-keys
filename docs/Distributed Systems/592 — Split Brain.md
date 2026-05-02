---
layout: default
title: "Split Brain"
parent: "Distributed Systems"
nav_order: 592
permalink: /distributed-systems/split-brain/
number: "0592"
category: Distributed Systems
difficulty: ★★★
depends_on: Quorum, Leader Election, Network Partitions, CAP Theorem, Replication Strategies
used_by: Fencing / Epoch, Distributed Locking, STONITH, Raft
related: Quorum, Fencing / Epoch, CAP Theorem, Leader Election, Raft
tags:
  - distributed
  - reliability
  - architecture
  - deep-dive
  - antipattern
---

# 592 — Split Brain

⚡ TL;DR — Split brain occurs when a network partition causes two or more nodes to simultaneously believe they are the authoritative leader or primary, resulting in divergent writes, data corruption, and conflicting state that is difficult or impossible to automatically resolve.

| #592            | Category: Distributed Systems                                                    | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Quorum, Leader Election, Network Partitions, CAP Theorem, Replication Strategies |                 |
| **Used by:**    | Fencing / Epoch, Distributed Locking, STONITH, Raft                              |                 |
| **Related:**    | Quorum, Fencing / Epoch, CAP Theorem, Leader Election, Raft                      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two-node database cluster. Primary (DB1) and standby (DB2). Network between them fails for 30 seconds. DB2's health check to DB1 fails. DB2's monitoring system promotes DB2 to primary (to maintain availability). DB1 is still running — it never crashed. It just couldn't reach DB2. DB1 continues accepting writes from its clients. DB2 also accepts writes from clients that have failed over to it. For 30 seconds: two primaries, two different write streams, two diverging databases. Neither node knows about the other's writes. When the network heals: 30 seconds of conflicting transactions that must somehow be reconciled — but for financial data, bank transfers, inventory counts, "reconciliation" may be impossible.

**THE INVENTION MOMENT:**
Split brain prevention is why consensus-based systems (Raft, Paxos) were built. By requiring a QUORUM (majority) to proceed, they make it mathematically impossible for two partitions to simultaneously act as primary — only the majority partition can.

---

### 📘 Textbook Definition

**Split Brain** is a distributed systems failure mode where two or more nodes, isolated from each other by a network partition, each assume primary/leader status and independently accept conflicting operations. Neither node is "wrong" from its own perspective — each follows its failover logic correctly. Split brain violates the **Safety** property of consensus: at most one leader per term. Recovery from split brain requires determining which partition's state is authoritative, discarding the other's changes, and manually or automatically merging divergence — a process that is often destructive for financial or transactional data. Prevention via quorum consensus is strongly preferred over post-hoc recovery.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Split brain is when a network glitch convinces two servers they're both in charge — and both start writing conflicting data before anyone knows.

**One analogy:**

> Split brain is like a marriage where both spouses are traveling and lose contact. Each assumes the other has died. Each remarries. When they reconnect, both are legally married to a different person AND their original spouse. There's no clean resolution — someone's marriage is invalid and must be unilaterally annulled. In databases, "which data survives" is the same agonising question.

**One insight:**
Split brain is a CAP theorem manifestation: between Consistency (one leader, no split brain) and Availability (keep serving even during partition), the system chose Availability. The solution isn't a better algorithm — it's accepting that during a network partition, you must choose one: go to read-only (CP) or accept potential split brain (AP). Consensus-based systems (Raft) choose CP: the minority partition stops accepting writes. The majority partition remains available.

---

### 🔩 First Principles Explanation

**HOW SPLIT BRAIN HAPPENS:**

```
Normal:           DB1 (primary) ←heartbeat→ DB2 (standby)
                  Both agree DB1 is primary.

Network partition:
                  DB1 × × × × × × × DB2
                  DB2 cannot reach DB1.

DB2's monitoring: "Primary is down! Promote myself."
DB2 becomes primary. Clients fail over to DB2.

DB1: still running perfectly, still primary.
DB1's monitoring: "Strange — DB2 isn't replicating. Oh well, still running."

Result: BOTH DB1 and DB2 accept writes. SPLIT BRAIN.
```

**SPLIT BRAIN IN DATABASES:**

```
DB1 state (after 30s of partition):
  Account A: balance=500 (two withdrawals processed)

DB2 state (after 30s of partition):
  Account A: balance=900 (deposit processed)

Actual initial balance: 1000
DB1's writes: -300, -200 → 500
DB2's writes: +100 → 1100 → after detecting DB1 -300... unclear

Merge conflict: which balance is "correct"?
  Cannot be both — money was double-spent or double-deposited.
  Data must be manually audited.
```

**PREVENTION STRATEGIES:**

```
1. QUORUM CONSENSUS (Raft/Paxos):
   Require majority agreement before accepting writes.
   Minority partition: writes rejected → no split brain possible.
   Cost: minority partition goes read-only during network failure.

2. FENCING TOKENS (Distributed Lock):
   Each "primary" granted a monotonically increasing epoch token.
   Writes to shared resource include epoch token.
   Storage layer rejects writes with lower epoch than highest seen.
   Old primary's writes are rejected by storage even if it doesn't know it's been replaced.

3. STONITH (Shoot The Other Node In The Head):
   On detecting potential split brain, IMMEDIATELY power-off the other node
   via out-of-band management (IPMI, AWS EC2 Stop API, etc.) before proceeding.
   Brutal but effective: only ONE node can physically operate.
   Used in Pacemaker/Corosync HA clusters for databases like Oracle RAC.

4. ARBITRATOR / WITNESS:
   A third node (witness) that cannot hold data but CAN vote.
   2-node cluster + 1 witness = 3 nodes → majority quorum = 2.
   Witness breaks ties in 1-1 partition. No data doubles but quorum possible.
```

---

### 🧪 Thought Experiment

**REDIS REDLOCK AND SPLIT BRAIN:**
Redis Sentinel watches a primary Redis and promotes a replica if primary is unreachable.
A strict partition: Primary (R1) isolated from Sentinel and Replica (R2, R3).
Sentinel concludes R1 is down; promotes R2 as primary.
R1 is still running, still serving reads, accepting new keys (if clients can still reach it).
R2 starts accepting new keys.

When partition heals: Sentinel reconnects R1 as a replica of R2. R1's "newer" keys
are LOST — R1 gets the data from R2, overwriting any R1-only writes.

Any client that cached "I wrote key K to R1" might later find key K missing (it's gone —
R1 was demoted and its data wiped during catch-up from R2).

**LESSON:** Redis Sentinel does NOT prevent split brain — it prioritises availability.
Clients must accept replication lag + potential data loss. For strongly-consistent
Redis use cases: either use Raft-based Redis alternatives (like RedisRaft or Redis Cluster
with WAIT commands) or accept the trade-off.

---

### 🧠 Mental Model / Analogy

> Split brain is the distributed systems version of an organisation where the CEO
> goes on a remote expedition with no communication. The board appoints a new CEO.
> The original CEO returns from the expedition still making decisions as CEO.
> Two people are now signing contracts and making commitments in the company's name.
>
> The only safe solutions: (1) require board quorum approval for any major decision
> (the CEO can't act alone — quorum consensus); (2) lock the CEO's card access
> before appointing the new one (STONITH); (3) make all contracts include a
> "valid only if CEO ID matches latest board-approved ID" clause (fencing tokens).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Split brain is when two servers both think they're the boss. They both accept changes that conflict. When they reconnect, their data is in an inconsistent state that's hard to fix.

**Level 2:** Split brain happens during network partitions when a failover system promotes a standby to primary without verifying the original primary is truly dead. The solution is either quorum consensus (majority must agree before proceeding) or fencing (ensure old primary's writes are rejected by storage before new primary starts).

**Level 3:** Quorum prevents split brain by construction: only the partition with N/2+1 nodes can form a quorum. Fencing prevents split brain operationally: even if an old primary is running, its writes are cryptographically rejected by the storage layer (epoch token check). STONITH is the hardware-level alternative: physically power off the other node to guarantee mutual exclusion. All three approaches accept that the minority/old-primary side becomes unavailable — the trade-off for safety.

**Level 4:** Split brain detection and recovery in production systems: write divergence from split brain leaves tombstones in changelog that can be parsed to identify conflicting writes. For AP databases (Cassandra, DynamoDB), split brain is an accepted operational state resolved via last-write-wins (LWW) or CRDT merge at partition heal time. For CP databases (etcd, CockroachDB), split brain is prevented unconditionally by refusing minority-partition writes. The engineering choice between CP and AP is a business decision: financial data → CP; social media "likes" → AP acceptable. Hybrid approaches (per-operation consistency levels) complicate the analysis but allow per-key/per-table trade-offs.

---

### ⚙️ How It Works (Mechanism)

**Fencing Token Implementation:**

```
Fence token = monotonically increasing integer awarded with each lock grant.

Lock service: ZooKeeper, etcd, Consul
  1. Primary requests lock → receives token N=47
  2. Primary writes data to storage, includes: {epoch: 47, data: ...}
  3. Storage records highest_seen_epoch = 47

Network partition: New primary (secondary) takes over
  4. New primary requests lock → receives token N=48
  5. New primary writes: {epoch: 48, data: ...}
  6. Storage updates: highest_seen_epoch = 48

Old primary reconnects (still holding its old lock, epoch=47)
  7. Old primary tries to write: {epoch: 47, data: ...}
  8. Storage checks: 47 < 48 → REJECT: epoch too old!

Result: Old primary's writes are silently rejected.
        Never serves stale data. No split brain.
```

**STONITH via AWS API (self-fencing):**

```bash
#!/bin/bash
# Run on node B when it suspects node A is down:
# Before taking over as primary, force-stop node A:

INSTANCE_ID="i-0abc123def456" # node A's EC2 ID

# Stop instance A via AWS API (out-of-band, not network-dependent):
aws ec2 stop-instances --instance-ids $INSTANCE_ID

# Wait for confirmation:
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID

echo "Node A confirmed stopped. Safe to proceed as new primary."
# Only NOW promote this node to primary.
```

---

### ⚖️ Comparison Table

| Prevention Method       | Guarantees Safety?     | Availability During Partition                            | Complexity   | Use Case                                              |
| ----------------------- | ---------------------- | -------------------------------------------------------- | ------------ | ----------------------------------------------------- |
| Quorum Consensus (Raft) | Yes (mathematical)     | Majority partition available                             | High         | Consensus stores (etcd, CockroachDB)                  |
| Fencing Tokens          | Yes (storage-enforced) | Both partitions available; old primary's writes rejected | Medium       | Distributed locks, lease-based systems                |
| STONITH                 | Yes (physical)         | Surviving node only                                      | Low (brutal) | HA database clusters (PostgreSQL Patroni, Oracle RAC) |
| Arbitrator/Witness      | Yes                    | Majority partition available                             | Medium       | 2+1 small clusters                                    |
| No prevention (AP)      | No                     | Both partitions available                                | Zero         | Cassandra, DynamoDB with LWW                          |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| A healthy heartbeat prevents split brain       | Heartbeats only detect loss; they don't prevent both sides from acting independently after loss                                  |
| Split brain only happens in large clusters     | Split brain is most common in 2-node clusters with no quorum mechanism — any even-node cluster without an arbiter is susceptible |
| Data from the old primary can always be merged | For financial transactions, conflicting writes often cannot be automatically merged — human reconciliation is required           |
| Raft guarantees no data loss ever              | Raft guarantees no loss of COMMITTED entries. Un-committed entries on a partitioned leader ARE lost when the partition heals     |

---

### 🚨 Failure Modes & Diagnosis

**Silent Split Brain (Both Nodes Think They're Primary)**

Detection is the primary challenge — split brain often goes undetected.

Symptom: Two nodes serving writes simultaneously; data divergence silently accumulates;
only detected at partition heal or during a CHECKSUM comparison.

Detection:

```bash
# On both nodes, check if each thinks it's primary:
# PostgreSQL Patroni:
patronictl -c /etc/patroni.yml list
# If two nodes both show "Leader": SPLIT BRAIN CONFIRMED

# MySQL:
SHOW VARIABLES LIKE 'super_read_only';
# If both primaries have super_read_only=OFF: SPLIT BRAIN

# Immediate action: force-stop the node with LOWER epoch/LSN:
patronictl -c /etc/patroni.yml failover --master <OLD_PRIMARY> --force
```

---

### 🔗 Related Keywords

- `Quorum` — the mathematical prevention mechanism; majority quorum makes split brain impossible
- `Fencing / Epoch` — the operational mechanism that rejects stale primary's writes at the storage layer
- `Leader Election` — the process that must be done safely to avoid electing two leaders simultaneously
- `CAP Theorem` — the theoretical framing: CP systems prevent split brain; AP systems accept it

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  SPLIT BRAIN: two nodes both acting as primary           │
│  CAUSE: network partition + failover without quorum       │
│  EFFECT: conflicting writes, unresolvable divergence      │
│  PREVENT:                                                 │
│    Quorum consensus → only majority partition acts        │
│    Fencing tokens   → old primary's writes rejected      │
│    STONITH          → physically stop old primary first  │
│  DETECT: both nodes showing as primary in cluster status  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 2-node PostgreSQL cluster (DB1 primary, DB2 standby) with Patroni encounters a network partition. Patroni detects DB1 is unreachable from DB2's side. DB2's Patroni agent wants to promote DB2, but a quorum check requires a third node (DCS like etcd). The etcd cluster (3 nodes) is also split: etcd1+etcd2 on the DB2 side, etcd3 on the DB1 side. Trace through the exact set of checks Patroni performs, who gets the DCS lock, and whether split brain is prevented.

**Q2.** Your team argues that adding a STONITH device to your 2-node cluster "solves split brain." A dissenting engineer says "STONITH can itself cause both nodes to shoot each other." Explain the fencing race condition where both nodes receive the partition event simultaneously and both initiate STONITH against each other, and describe the protocol enhancement (randomised delays + leadership confirmation) that prevents mutual assured destruction.
