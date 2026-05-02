---
layout: default
title: "Log Replication"
parent: "Distributed Systems"
nav_order: 589
permalink: /distributed-systems/log-replication/
number: "0589"
category: Distributed Systems
difficulty: ★★★
depends_on: Raft, Leader Election, Distributed Consensus, Write-Ahead Log
used_by: etcd, CockroachDB, MySQL Replication, Kafka
related: Raft, State Machine Replication, Write-Ahead Log, Replication Strategies
tags:
  - log-replication
  - raft
  - consensus
  - distributed-systems
  - advanced
---

# 589 — Log Replication

⚡ TL;DR — Log Replication is the mechanism by which a distributed system maintains identical, ordered logs across multiple nodes by having the leader append entries to its own log and then replicate those entries to followers before confirming them as committed. It is the core mechanism in Raft, MySQL binlog replication, Kafka's log segment replication, and write-ahead logging (WAL). The log serves as the source of truth: any state can be derived by replaying the log from the beginning.

| #589 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Raft, Leader Election, Distributed Consensus, Write-Ahead Log | |
| **Used by:** | etcd, CockroachDB, MySQL Replication, Kafka | |
| **Related:** | Raft, State Machine Replication, Write-Ahead Log, Replication Strategies | |

---

### 🔥 The Problem This Solves

**WITHOUT LOG REPLICATION:**
A distributed database wants 3 copies of each write (for fault tolerance). Naïve approach: on each write, send the data to all 3 replicas and wait for all to ACK. Problems: (1) What if replica 2 received writes 1, 2, 4, 5 but missed 3 due to a network blip? How does it catch up? (2) Which write happened first? What's the "correct" order for applying them? (3) If the primary crashes mid-write, how do replicas know which writes to consider complete? Log replication solves all three: ALL writes go into a sequential, indexed, immutable log. Replicas catch up by requesting missing log entries by index. The primary confirms a write only after a majority of replicas have record in their logs. This log = a complete, ordered, recoverable history of all mutations.

---

### 📘 Textbook Definition

**Log Replication** is the process of maintaining identical ordered sequences of operations (a "replicated log") across multiple nodes. The log serves as the authoritative, append-only sequence of mutations; state is derived by applying log entries in order from the beginning (the state machine).

In Raft, log replication proceeds as:
1. Leader receives a client command (write)
2. Leader appends the command as a new entry in its log: (term, index, command)
3. Leader sends AppendEntries RPC to all followers, carrying the new entries
4. Followers append entries to their own logs (after verifying the prevLogIndex/prevLogTerm consistency check)
5. Leader commits (advances commitIndex) when a majority of nodes have the entry
6. Leader applies committed entry to its state machine, responds to client
7. In subsequent AppendEntries, followers learn the new commitIndex and apply accordingly

**Log consistency invariant:** If two log entries have the same index and term, they contain the same command, AND all prior entries are identical. This invariant is maintained by the prevLogIndex/prevLogTerm check in AppendEntries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Log replication = leader appends write to a sequential numbered log, replicates to followers, marks "committed" when majority have it.

**One analogy:**
> The flight recorder (black box) pattern. Every action is recorded, in order, to an append-only log. No action is "official" until it's replicated to the backup recorder (majority). If the primary recorder fails, the backup has the complete history and can be promoted. Replaying the log from start = derived state. This is exactly how Raft log replication (and MySQL binlog replication) work.

---

### 🔩 First Principles Explanation

```
LOG REPLICATION — ANATOMY:

  RAFT LOG STRUCTURE:
  ┌────────────┬────────────┬────────────┬────────────┬────────────┐
  │ Index: 1   │ Index: 2   │ Index: 3   │ Index: 4   │ Index: 5   │
  │ Term:  1   │ Term:  1   │ Term:  2   │ Term:  2   │ Term:  3   │
  │ SET x=1    │ SET y=2    │ SET z=3    │ DEL y      │ SET w=5    │
  └────────────┴────────────┴────────────┴────────────┴────────────┘
  ←───────────── committed (on majority) ────────────→ ← uncommitted
  
  commitIndex = 4 (entries 1-4 on majority of nodes, applied to state machine)
  lastLogIndex = 5 (latest entry, not yet confirmed on majority)
  
  APPEND ENTRIES RPC:
  {
    term: 3,                      // leader's current term
    leaderId: "node-1",           // so followers can redirect clients
    prevLogIndex: 4,              // index of entry before new entries
    prevLogTerm: 2,               // term of prevLogIndex entry
    entries: [(5, 3, "SET w=5")], // new entries to append
    leaderCommit: 4               // leader's commitIndex (tell followers what to apply)
  }
  
  FOLLOWER CONSISTENCY CHECK:
  "Does my log contain an entry at index=4 with term=2?"
  YES → append new entries → ACK success
  NO  → reply fail → leader BACKS UP (decrements nextIndex for this follower)
        and retries with earlier entries until follower is consistent
```

---

### 🧪 Thought Experiment

**SCENARIO:** A follower (N3) was network-partitioned for 10 seconds and missed 50 log entries. What happens when it reconnects?

```
N3's log: ends at index 100 (commitIndex 98)
Leader's log: ends at index 150 (commitIndex 148)

On reconnect, leader's next AppendEntries to N3:
  prevLogIndex=149, prevLogTerm=5, entries=[(150, 5, ...)]

N3 consistency check: "Do I have index=149 with term=5?"
  NO (N3 only has up to index=100) → Reply: {success: false}

Leader backs up: decrement nextIndex[N3] = 100
  prevLogIndex=99, prevLogTerm=4, entries=[(100,4,...),(101,4,...),...]

N3 consistency check: "Do I have index=99 with term=4?" YES ✓
N3 appends entries 100-150 all at once
N3 ACKs success

Leader advances nextIndex[N3] = 151
N3 is now fully caught up: log matches leader's ✓

Performance note: Leader may batch many entries in one AppendEntries
(configurable, up to 4MB in etcd). N3 catches up ~in 1 round trip for 50 entries.
```

---

### 🧠 Mental Model / Analogy

> Log replication is like a court reporter for a distributed trial.
> Every objection, ruling, and statement is entered into the official transcript (log) with a sequence number by the presiding judge (leader).
> Before a ruling is "final" (committed), it must appear in the transcripts of a majority of court reporters (followers).
> If the judge is replaced mid-trial (leader failure): the new judge reviews all transcripts, picks the most complete one as authoritative, and continues from where the prior judge left off. Any entries only the old judge had (not in majority's transcripts) are discarded — they were never "final."

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Log replication: leader writes command to its log (numbered entry), tells followers to append it, waits for majority to confirm, then marks it "committed." The log number (index) gives total ordering — every replica applies entries in order.

**Level 2:** The prevLogIndex/prevLogTerm consistency check is the heart of Raft's Log Matching property. Before appending new entries at position P, the leader verifies: "Does the follower's log have the SAME entry at position P-1 as I do?" Because the log is built incrementally with this check, by induction the logs agree on all entries from 0 to P-1. Any divergence is detected and the leader forces the follower to roll back to the last common entry (via nextIndex decrement) before re-sending.

**Level 3:** Log replication vs. state transfer: an alternative to replaying logs is transferring the entire state (snapshot). Raft supports both: for new members or nodes far behind, a full state snapshot (InstallSnapshot RPC) is more efficient than replaying thousands of old log entries. After installing the snapshot, the follower can continue with log replication from where the snapshot ends. etcd has compaction: periodically takes a snapshot, truncates old log entries (disk space management), and uses InstallSnapshot for catching up lagging nodes.

**Level 4:** MySQL binlog replication works on the same principle: the binlog is the authoritative log of all SQL DML operations. A replica connects, sends its current binlog position (file + offset), and the primary streams all subsequent events. The replica applies events in order (converting them into SQL and executing, or using row-based replication for direct row changes). Semi-synchronous replication = wait for at least one replica to ACK the binlog event before committing the transaction (analogous to Raft's majority commit but with f=1). Kafka topic partitions use a replicated log (the topic partition itself IS the log): leader broker holds the authoritative log, in-sync replicas (ISR) replicate it. A message is "committed" when all ISR replicas have it — stricter than Raft majority, but configurable (acks=all vs acks=1).

---

### ⚙️ How It Works (Mechanism)

```
RAFT APPENDENTRIES — HAPPY PATH AND ERROR PATH:

HAPPY PATH:
  Client → Leader(N1): SET config = "prod-v2"
  
  N1: appends (term=5, index=43, "SET config=prod-v2") to own log
  
  N1 → N2: AppendEntries(prevIdx=42, prevTerm=5, entries=[(43,5,...)])
  N1 → N3: AppendEntries(prevIdx=42, prevTerm=5, entries=[(43,5,...)])
  
  N2: has index=42 with term=5 ✓ → appends index=43 → ACK success
  N3: has index=42 with term=5 ✓ → appends index=43 → ACK success
  
  N1 receives ACKs from N2, N3 (3 of 3 → majority of cluster) → COMMIT index=43
  N1: applies "SET config=prod-v2" to state machine
  N1 → Client: OK ✓
  
  N1 → N2, N3 (next heartbeat): leaderCommit=43 → followers advance commitIndex=43 and apply

ERROR PATH (follower diverged):
  N3 missed entries 41, 42 (was partitioned). N3's log ends at index=40.
  
  N1 → N3: AppendEntries(prevIdx=42, prevTerm=5, ...) 
  N3: no entry at index=42 → ACK {success: false}
  
  N1: decrements nextIndex[N3] to 41
  N1 → N3: AppendEntries(prevIdx=40, prevTerm=4, entries=[(41,4,...),(42,5,...),(43,5,...)])
  N3: has index=40 with term=4 ✓ → appends 41,42,43 → ACK success
  N1: updates nextIndex[N3] = 44
  N3 is now fully synchronized ✓
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
KAFKA PARTITION LOG REPLICATION:

  Topic "orders", Partition 0, 3 replicas (leader=Broker1, ISR=[B1,B2,B3])
  
  Producer → Broker1: PRODUCE order_id=42, events=... (acks=all)
  
  Broker1 appends to local log segment:
    offset=1000, order_id=42, ...  ← written to disk
  
  Broker1 → Broker2: Fetch from offset=1000 (pull-based replication)
  Broker2 fetches offset 1000 → stores locally
  Broker2 → Broker1: FetchResponse including high watermark update
  
  Broker1 → Broker3: same flow
  
  When all ISR replicas (B1, B2, B3) have offset=1000:
  Broker1 advances High Watermark (HW) to 1000
  Broker1 → Producer: ProduceResponse(offset=1000) ← ACK ✓
  
  Consumer reads offset ≤ HW only (committed messages):
  Consumer → Broker1: Fetch(offset=1000) → gets order_id=42 ✓
  
  Messages at offset > HW: not yet on all ISR → not consumer-readable yet
  This is Kafka's "committed = all ISR have it" guarantee.
```

---

### 💻 Code Example

```java
// MySQL semi-synchronous replication (log replication with at-least-1 follower ACK)
// Configuration: equivalent to Raft's quorum write but with f=1 (1 replica must ACK)
@Configuration
public class DataSourceConfig {

    // Write to primary (synchronous binlog replication to at least 1 replica)
    @Bean
    @Primary
    public DataSource primaryDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://primary:3306/mydb");
        // Primary must be configured with: rpl_semi_sync_master_enabled=ON
        //   This ensures at least 1 replica ACKs the binlog event before COMMIT returns.
        //   Semi-sync commit → log replicated binlog to ≥1 replica → durable.
        config.addDataSourceProperty("sessionVariables",
            "rpl_semi_sync_master_timeout=10000");  // 10s timeout → falls back to async
        return new HikariDataSource(config);
    }

    // Read from replica (asynchronous log replication may lag)
    @Bean("readReplica")
    public DataSource replicaDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://replica:3306/mydb");
        // Replica is behind by up to semi_sync timeout duration
        // Use for read-heavy queries where slight staleness is acceptable
        return new HikariDataSource(config);
    }
}

// Service: route reads to replica, writes to primary
@Service
public class OrderService {

    @Transactional  // Write: goes to primary (binlog replicated semi-synchronously)
    public void createOrder(Order order) {
        orderRepository.save(order);  // goes to primary DataSource
        // write acknowledged only after at least 1 replica has the binlog event ✓
    }

    @Transactional(readOnly = true)  // Read: can use replica (may be slightly stale)
    public List<Order> getOrderHistory(String userId) {
        return orderRepository.findByUserId(userId);  // goes to replica DataSource
        // may be 0-100ms behind primary (replication lag)
    }
}
```

---

### ⚖️ Comparison Table

| System | Log Type | Commit Quorum | Replication Mode |
|---|---|---|---|
| **Raft (etcd)** | Raft log entries (index + term) | Majority (N/2+1) | Push (leader → followers) |
| **MySQL Binlog** | SQL events / Row changes | 1 replica (semi-sync) | Push (primary → replicas) |
| **Kafka** | Partition log segments (offsets) | All ISR replicas | Pull (replicas → leader) |
| **PostgreSQL WAL** | Write-Ahead Log records | 1+ standbys (synchronous_standby_names) | Push (primary → standbys) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Committed" means applied to state machine | "Committed" means on a majority of nodes (Raft commitIndex). "Applied" means executed on the state machine. These are separate states — a committed entry might not be applied immediately to all followers |
| Log replication is only for databases | Any replicated state machine uses log replication: Kafka (event log), ZooKeeper (config mutations), Kubernetes ETCD (cluster state mutations), even game servers (event sourcing for distributed game state) |
| Followers can serve reads immediately after log entry commits | Followers might still be applying earlier committed entries. The "applied index" might lag the "commit index." Safe follower reads require waiting until applied index ≥ the commit index of the entry you want to read |

---

### 🚨 Failure Modes & Diagnosis

**Replication Lag — Follower Falls Behind**

```
Symptom:
etcd follower is 1000 log entries behind the leader.
Reads from this follower return stale config data.

Root Cause:
1. Network congestion/slow link between leader and this follower
2. Disk I/O bottleneck on follower (slow fsync of AppendEntries)
3. CPU overload on follower (slow log application)
4. Compaction / snapshot install in progress on follower

Detection:
  etcdctl endpoint status --cluster
  → Look at "raftIndex" field: large difference from leader = lag
  Metric: etcd_server_proposals_committed_total - etcd_server_proposals_applied_total
  → Large gap: leader commits faster than follower applies

Fix:
1. Network: check bandwidth/latency between leader and follower
2. Disk: use SSDs for etcd data dir; tune fsync settings
3. Snapshot install: etcd handles automatically (InstallSnapshot RPC)
4. Monitoring: alert on raft_follower_lag > 500ms (or 100 entries)
```

---

### 🔗 Related Keywords

- `Raft` — the consensus algorithm that uses log replication as its core mechanism
- `State Machine Replication` — the higher-level pattern built on top of log replication
- `Write-Ahead Log (WAL)` — the local log abstraction that each node uses
- `Replication Strategies` — the broader category of database replication approaches

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Leader appends command to sequential log,   │
│               │ replicates to followers, commits on majority│
├───────────────┼─────────────────────────────────────────────┤
│ KEY INVARIANT │ If indexes + term match: logs identical up  │
│               │ to that point (Log Matching Property)       │
├───────────────┼─────────────────────────────────────────────┤
│ CONSISTENCY   │ prevLogIndex/prevLogTerm consistency check  │
│ CHECK         │ before AppendEntries → ensures no gaps     │
├───────────────┼─────────────────────────────────────────────┤
│ CATCH-UP      │ Leader backs up nextIndex until match found│
│               │ then bulk-sends missing entries             │
├───────────────┼─────────────────────────────────────────────┤
│ SYSTEMS       │ Raft, etcd, MySQL binlog, Kafka ISR, WAL   │
└───────────────┴─────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A CockroachDB range (Raft group) has 3 replicas: node-1 (leader), node-2, node-3. Node-2 is slow due to disk I/O issues — it consistently takes 200ms to ACK AppendEntries (vs 5ms for node-3). Write latency spikes to 200ms for all writes because Raft waits for majority (2 of 3) and both followers respond, but node-2 is always the bottleneck. The team considers removing node-2 from the Raft group and using only node-1 and node-3. Analyze: (1) what does the team lose by doing this? (2) Is "wait for the first majority ACK" optimization available — i.e., can Raft commit on node-1 + node-3 ACKs, ignoring the slow node-2? (3) What configuration change would reduce write latency while maintaining fault tolerance, and what new failure scenario does it introduce?
