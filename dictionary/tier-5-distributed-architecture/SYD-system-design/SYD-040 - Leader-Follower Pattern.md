---
id: SYD-040
title: Leader-Follower Pattern
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-039, SYD-019
used_by: SYD-041, SYD-023
related: SYD-039, SYD-019, SYD-021
tags:
  - distributed
  - reliability
  - architecture
  - pattern
  - deep-dive
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 40
permalink: /syd/leader-follower-pattern/
---

# SYD-040 - Leader-Follower Pattern

⚡ TL;DR - One node (leader) handles all writes and coordinates state; followers replicate and handle reads - providing consistency, failover, and read scalability with a clear authority hierarchy.

| SYD-040         | Category: System Design        | Difficulty: ★★★ |
| :-------------- | :----------------------------- | :-------------- |
| **Depends on:** | SYD-039, SYD-019               |                 |
| **Used by:**    | SYD-041, SYD-023               |                 |
| **Related:**    | SYD-039, SYD-019, SYD-021     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a multi-node system where every node can accept writes, two nodes can accept conflicting updates simultaneously. Node A sets `user.email = alice@new.com`; Node B simultaneously sets `user.email = alice@old.com`. Both writes succeed locally. Now the nodes disagree. Which one wins? How do you reconcile without data loss?

**THE BREAKING POINT:**
Multi-master writes require conflict resolution - which is provably complex and application-specific. Most data has natural write semantics where "last write wins" or "all writes are ordered" is the correct expectation. Multi-master violates both.

**THE INVENTION MOMENT:**
Designate one node as the single authority for writes. All writes flow through the leader, which assigns a global order. Followers receive the ordered write log and apply it. Consistency is preserved because order is established at the source.

**EVOLUTION:**
Leader-follower (also called primary-replica or master-slave) appears in virtually every database: MySQL binlog replication, PostgreSQL streaming replication, Redis Sentinel, MongoDB replica sets, Kafka partition leadership. The pattern evolved beyond databases to coordination services (ZooKeeper), distributed job schedulers, and microservice shard coordination.

---

### 📘 Textbook Definition

The **Leader-Follower pattern** is a distributed systems topology where one node (the leader) is the authoritative source for writes and state changes. Follower nodes replicate leader state and serve read requests. On leader failure, a new leader is elected from the followers via a consensus protocol. The pattern trades multi-writer flexibility for consistency and clear write authority.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One boss who decides everything; assistants who copy and serve reads.

**One analogy:**

> A leader-follower cluster is like a head chef and line cooks. The head chef (leader) decides the recipes and directs changes. Line cooks (followers) execute and replicate the techniques. If the head chef is absent, the most senior line cook steps up.

**One insight:**
The leader is a throughput bottleneck for writes. The follower adds read throughput. This trade-off is why read-heavy workloads (10:1 read:write ratio) benefit most from this pattern.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. All writes must have a globally consistent order to prevent conflicts.
2. One authoritative writer per partition enforces ordering.
3. Followers are eventually consistent copies, not authorities.
4. Leader failure must be detectable and recoverable without data loss.

**DERIVED DESIGN:**
Leader accepts writes, appends to a replication log, sends log to followers. Followers apply log in order. Reads can be served by any node (with replication lag caveat). On leader failure: followers detect (heartbeat timeout), elect a new leader (Raft/Paxos/semi-sync), promote it.

**THE TRADE-OFFS:**
**Gain:** Strong write consistency, clear conflict avoidance, read scalability.
**Cost:** Leader is write bottleneck; follower reads may be stale (replication lag); leader election during failover causes a brief write unavailability window.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** You need one authority per partition to order writes. Order cannot emerge from voting on every write.
**Accidental:** Election algorithms, semi-sync replication, split-brain prevention with fencing.

---

### 🧪 Thought Experiment

**SETUP:** A financial ledger service runs on 3 nodes. Transfers must not be duplicated or lost.

**WHAT HAPPENS WITHOUT LEADER-FOLLOWER (all nodes accept writes):**
A transfer is sent to Node 1 and Node 2 simultaneously (load balancer round-robin). Both write the debit independently. Result: the account is debited twice. Alternatively, Node 1 and Node 3 accept conflicting balance updates at the same millisecond. No single truth exists.

**WHAT HAPPENS WITH LEADER-FOLLOWER:**
All transfers go to the leader. The leader appends to WAL, applies locally, streams to followers. Followers are read-only mirrors. Transfer arrives once, is applied once, is replicated to followers in order. Followers serve balance reads (possibly with small lag).

**THE INSIGHT:**
Write coordination is expensive precisely because you must establish a global order. A single leader is the cheapest way to establish order - one node decides, everyone follows. The cost is that leader becomes the bottleneck.

---

### 🧠 Mental Model / Analogy

> A leader-follower cluster is like a master key generator and locksmiths. The master (leader) cuts all original keys. The locksmiths (followers) duplicate every key cut by the master and serve customers who need copies. If the master retires, the most senior locksmith takes over as the new master.

- **Master key generator** = leader (accepts writes)
- **Key cutting** = write operation
- **Duplication log** = replication stream
- **Locksmiths** = followers (serve reads)
- **Senior locksmith promoted** = leader election on failure
- **Time to get duplicate key** = replication lag

Where this analogy breaks down: key duplication is instantaneous; replication has latency, so followers may temporarily serve stale data.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
In a team, the manager (leader) makes all decisions. Assistants (followers) copy those decisions and can answer questions about the company's state. If the manager leaves, an assistant gets promoted.

**Level 2 - How to use it (junior developer):**
Connect your writes to the primary DB endpoint; connect reads to replica endpoints. Monitor replication lag - reads from a replica may be seconds behind the leader. For strong consistency (must read your own write), route reads to the leader too.

**Level 3 - How it works (mid-level engineer):**
Leader writes to its WAL (Write-Ahead Log). The WAL is streamed to followers (physical/logical). Followers apply WAL in order. Replication lag = leader WAL position - follower applied position. Failover: heartbeat timeout triggers election; candidate with most up-to-date log wins in Raft. Fencing: old leader fenced (STONITH or lease expiry) to prevent split-brain.

**Level 4 - Why it was designed this way (senior/staff):**
The CAP theorem: leader-follower is a CP design (consistency + partition tolerance). During network partition separating leader from followers, writes block at the leader rather than split into two conflicting write streams. Semi-synchronous replication provides a middle ground: leader waits for at least one follower to acknowledge before responding - preventing data loss on failover at the cost of write latency. Synchronous replication (all followers must ACK) maximizes durability but tanks write throughput.

**Expert Thinking Cues:**
- Ask: "What is your acceptable replication lag SLA for reads? Zero? 100ms?"
- Ask: "How long is the leader election window, and what is the write impact?"
- Red flag: routing all reads to leader - defeats the read scalability benefit
- Red flag: no fencing - old leader can accept writes after election

---

### ⚙️ How It Works (Mechanism)

**Write path:**
```
Client -> Leader
Leader: 1. Write to WAL
        2. Apply to local state
        3. Send WAL entry to followers
        4. ACK client (async or semi-sync)
Followers: Apply WAL entry in order
```

**Read path:**
```
Client -> Any follower (or leader for strong consistency)
Follower: Return local state (may have replication lag)
Leader: Return guaranteed up-to-date state
```

**Failover path:**
```
Leader stops sending heartbeats
Followers: timeout elapsed -> start election
Candidate with highest log index: REQUEST_VOTE
  -> Majority grants vote -> becomes new leader
  -> Fences old leader (prevents split-brain)
New leader: announces leadership, continues WAL
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Client sends write]
         |
         v
[Leader receives write]  <- YOU ARE HERE
         |
         v
[WAL entry created, state applied]
         |
         v
[Replication stream to followers]
         |
         v
[Followers apply in order]
         |
         v
[Read from follower (lag possible)]
```

**FAILURE PATH:**
```
[Leader stops heartbeating]
         |
[Follower heartbeat timeout]
         |
[Election: Raft/Paxos vote]
         |
[New leader elected]
         |
[Writes resume (brief gap)]
         |
[Old leader fenced on recovery]
```

**WHAT CHANGES AT SCALE:**
With many read replicas, replication fan-out network cost grows. Use replication chains (follower-of-follower) or a replication bus. Write throughput is bounded by single-leader capacity - shard to add write throughput (multiple leader-follower groups, each owning a partition).

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Split-brain: a network partition can make followers think the leader is dead before the leader thinks it is dead. Two nodes both elect themselves leader. Prevent via: fencing tokens, STONITH (Shoot The Other Node In The Head), distributed lock on leadership token.

---

### 💻 Code Example

**BAD - writing to a replica:**
```python
# BAD: writing to replica = read-only error or stale write
import psycopg2

# Replica connection string (read-only)
conn = psycopg2.connect(
    "host=replica.db.internal dbname=app"
)
cur = conn.cursor()
cur.execute(
    "UPDATE accounts SET balance = 900 WHERE id = 1"
)  # Fails or silently applies to stale replica
```

**GOOD - write to leader, read from replica:**
```python
import psycopg2

def get_connections():
    leader = psycopg2.connect(
        "host=leader.db.internal dbname=app"
    )
    replica = psycopg2.connect(
        "host=replica.db.internal dbname=app"
    )
    return leader, replica

def transfer(leader_conn, from_id, to_id, amount):
    # All writes go to leader
    with leader_conn.cursor() as cur:
        cur.execute("""
            UPDATE accounts SET balance = balance - %s
            WHERE id = %s
        """, (amount, from_id))
        cur.execute("""
            UPDATE accounts SET balance = balance + %s
            WHERE id = %s
        """, (amount, to_id))
        leader_conn.commit()

def get_balance(replica_conn, account_id):
    # Reads from replica (may have small lag)
    with replica_conn.cursor() as cur:
        cur.execute(
            "SELECT balance FROM accounts WHERE id=%s",
            (account_id,)
        )
        return cur.fetchone()[0]
```

**How to test / verify correctness:**
- Write to leader, immediately read from replica - assert that lag is within acceptable window.
- Kill leader, assert election completes and new leader accepts writes within SLA timeout.
- Double-write same data to leader and directly to replica - assert replica rejects direct write.

---

### ⚖️ Comparison Table

| Topology              | Writes     | Reads        | Consistency | Failover       |
| --------------------- | ---------- | ------------ | ----------- | -------------- |
| Single leader         | Leader only | Leader/replicas | Strong    | Manual/auto    |
| Multi-leader          | Any node   | Any node     | Eventual    | No failover needed |
| Leaderless (Dynamo)   | Any node   | Quorum       | Tunable     | No election    |
| Synchronous replica   | Leader     | Leader/replicas | Strongest | Slower writes  |
| Async replica         | Leader     | Leader/replicas | Weaker    | Potential data loss |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Followers are always consistent with leader" | Followers have replication lag. A read from a follower may return data that is seconds behind the leader. For "read your own write" guarantees, route reads to the leader. |
| "More replicas = faster reads" | Adding replicas adds read capacity but also adds replication network fan-out cost from the leader. Beyond ~5 replicas, use replication chains. |
| "Leader election is instantaneous" | Leader election typically takes seconds (ZooKeeper ~2-5s, etcd ~1-3s). Writes are blocked during this window. Design for this gap. |
| "Followers can accept writes if I want" | Writing to a follower bypasses replication ordering. The write will be overwritten when the leader's stream arrives, or will conflict. |
| "Multi-leader is always better for write performance" | Multi-leader requires conflict resolution logic that is application-specific and notoriously hard. Single-leader is almost always the right starting point. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Split-brain (two leaders)**

**Symptom:** Two nodes both accept writes; data diverges; one overwrites the other after partition heals.

**Root Cause:** Network partition: followers timed out and elected new leader before old leader knew it was isolated.

**Diagnostic:**
```bash
# PostgreSQL: check timeline IDs
psql -c "SELECT pg_current_wal_lsn();" -h leader
psql -c "SELECT pg_last_wal_receive_lsn();" -h replica
# Diverging values = split-brain risk
```

**Fix:** Implement fencing: old leader must be unable to accept writes after election. Use lease-based leadership with renewal requirement.

**Prevention:** Configure `synchronous_standby_names` for critical writes; use STONITH if possible.

---

**Failure Mode 2: Replication lag causing stale reads**

**Symptom:** User updates profile, immediately refreshes page, sees old data.

**Root Cause:** Read routed to follower that has not yet applied the write from leader.

**Diagnostic:**
```sql
-- PostgreSQL: measure replication lag
SELECT client_addr,
       pg_wal_lsn_diff(
           pg_current_wal_lsn(),
           sent_lsn
       ) AS lag_bytes
FROM pg_stat_replication;
```

**Fix:** Route reads to leader for "read your own writes" scenarios. Or use monotonic reads (always read from same follower).

**Prevention:** Monitor and alert on replication lag > acceptable threshold (e.g., > 500ms).

---

**Failure Mode 3: Leader election timeout causes write outage**

**Symptom:** Writes fail with "no leader available" for 10-30 seconds after leader crash.

**Root Cause:** Heartbeat timeout too long; election algorithm too conservative.

**Diagnostic:**
```bash
# Check cluster leadership status
redis-cli -h sentinel01 SENTINEL masters
# Or for etcd
etcdctl endpoint status --write-out=table
```

**Fix:** Tune heartbeat interval and election timeout. Set `election_timeout = 3 * heartbeat_interval`.

**Prevention:** Test failover scenario regularly; measure actual election time in staging.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-019 - Redundancy Failover]] - foundational concept for leader recovery
- [[SYD-039 - Distributed Locks]] - leader election uses distributed lock semantics

**Builds On This (learn these next):**
- [[SYD-041 - Write-Ahead Logging (System)]] - WAL is the replication mechanism inside leader-follower
- [[SYD-023 - Geo-Replication]] - leader-follower topology extended across regions

**Alternatives / Comparisons:**
- [[SYD-021 - Active-Passive]] - similar concept at the service/deployment level
- [[SYD-019 - Redundancy Failover]] - the general pattern; leader-follower is a specific implementation

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ One authoritative write node;    │
│              │ N read-only follower replicas    │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Multi-writer conflicts in        │
│ IT SOLVES    │ distributed systems              │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Ordering writes at one point     │
│              │ eliminates conflicts cheaply     │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Read-heavy workload; need        │
│              │ strong write consistency         │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Write-heavy workload needing     │
│              │ horizontal write scale           │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Write throughput bounded by      │
│              │ single leader capacity           │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Leader orders all writes;       │
│              │ followers replicate in order."   │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-041 Write-Ahead Logging      │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. All writes go to the leader; followers serve reads with possible lag.
2. Leader election takes seconds - design your write path to handle this.
3. Prevent split-brain: fence the old leader before promoting the new one.

**Interview one-liner:** "Leader-follower gives you consistent writes by routing them all through one authority, and read scale by letting followers serve reads - at the cost of write throughput being bounded by one node."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When ordering is critical, funnel through a single sequencer. Multiple sequencers require synchronization that is more expensive than the sequencer itself. Use sharding to multiply throughput by multiplying sequencers, not by removing them.

**Where else this pattern appears:**
- **Kafka partitions:** Each partition has a leader broker. Producers write to the leader; followers replicate. Consumer groups read from leader or replica.
- **Service mesh sidecar coordination:** Envoy proxies sync config from a single Pilot (control plane leader).
- **Git branching:** The main branch is the "leader" - all changes flow through PR merge, creating an ordered history.

---

### 💡 The Surprising Truth

Most database drivers transparently implement write-to-leader, read-from-replica routing - but many developers don't realize they're opted out by default. In PostgreSQL, read queries on a replica require explicitly connecting to the replica endpoint. If your app always connects to the primary, you gain zero read scale from adding replicas. You must explicitly route reads away from the leader to benefit from the pattern.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A PostgreSQL leader-follower cluster has 3 replicas. The leader is in us-east-1, replicas in us-east-1, eu-west-1, and ap-southeast-1. A write occurs on the leader. 100ms later, a user in Asia reads from the ap-southeast-1 replica. Assuming async replication, what is the replication lag, and what happens if the user immediately reads their own write?

*Hint:* Trace the replication path across regions (leader WAL -> network -> follower apply), estimate propagation latency, and explore the "read-your-own-writes" consistency model and how session affinity or leader reads solve it.

**Q2 (Scale):** Your MySQL leader handles 50K writes/sec at 70% CPU. You add 10 read replicas. Write throughput does not improve. CPU still 70%. Why, and what must you do to scale write throughput?

*Hint:* Leader-follower adds read capacity, not write capacity. Adding replicas actually adds replication fan-out CPU cost to the leader. To scale writes, you need to shard (multiple independent leader-follower groups, each owning a key range).

**Q3 (Design Trade-off):** A fintech requires zero data loss on leader failure. Semi-synchronous replication (leader waits for one follower ACK before responding) adds 5ms average write latency. Your current write p99 is 8ms. Should you enable semi-sync? What are the tail latency implications?

*Hint:* Evaluate the impact on p99 write latency (8ms + 5ms = 13ms minimum, but network jitter means p99 could be much higher). Then look at how semi-sync "swithces to async" under follower failure and what that means for your zero-loss guarantee.
