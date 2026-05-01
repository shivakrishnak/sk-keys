---
layout: default
title: "Leader-Follower Pattern"
parent: "System Design"
nav_order: 715
permalink: /system-design/leader-follower/
number: "715"
category: System Design
difficulty: ★★★
depends_on: "Distributed Locks, Active-Passive"
used_on: "Write-Ahead Logging (System), Database Replication, Raft"
tags: #advanced, #distributed, #consistency, #reliability, #consensus
---

# 715 — Leader-Follower Pattern

`#advanced` `#distributed` `#consistency` `#reliability` `#consensus`

⚡ TL;DR — **Leader-Follower Pattern** assigns one node as the authoritative leader for coordinating writes/decisions, while follower nodes replicate state from the leader — ensuring consistency while allowing read scale-out through followers.

| #715            | Category: System Design                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Locks, Active-Passive                        |                 |
| **Used on:**    | Write-Ahead Logging (System), Database Replication, Raft |                 |

---

### 📘 Textbook Definition

**Leader-Follower** (also called Master-Replica, Primary-Replica, or Single-Leader Replication) is a distributed systems pattern where one node (the leader/primary) is designated as the authoritative source for write operations, while one or more follower nodes (replicas) maintain copies of the leader's state by consuming its replication log. All writes go through the leader, which ensures serialisability of operations. Followers serve read requests (distributing read load) and provide fault tolerance (any follower can be promoted to leader on leader failure). Leader election (determining which node becomes the new leader after failure) is implemented via consensus algorithms (Raft, Paxos, ZooKeeper ZAB) or distributed locks. Leader-Follower is the default architecture for PostgreSQL, MySQL, Redis Sentinel, Kafka partition leaders, and many distributed databases.

---

### 🟢 Simple Definition (Easy)

Leader-Follower: one node is the boss (leader) — all changes go through the boss. Other nodes (followers) copy everything the boss does. If anyone wants to read data: they can ask any follower (boss has many helpers). If the boss goes down: elect a new boss from the helpers. No two bosses at the same time — that causes conflicts.

---

### 🔵 Simple Definition (Elaborated)

PostgreSQL primary-replica setup: One primary (leader) accepts all writes. Three replicas (followers) receive a stream of WAL (Write-Ahead Log) records from the primary and replay them — staying in sync. Application: writes to primary, reads can go to any replica. If primary goes down: one replica is promoted to primary (leader election via Patroni). New primary starts accepting writes. Other replicas re-attach to new primary. Service restored, typically within 30-60 seconds. This is the architecture behind most relational database HA (High Availability) setups.

---

### 🔩 First Principles Explanation

**Leader-follower replication modes and failure handling:**

```
REPLICATION MODES:

  1. SYNCHRONOUS REPLICATION:
     Leader: receives write → writes locally → waits for ACK from all followers → returns to client.

     Request: INSERT INTO orders (id, amount) VALUES (1, 100)
     Leader: writes to WAL
     Leader: sends WAL record to all followers
     Followers: apply WAL record, send ACK
     Leader: only then returns "OK" to client

     Durability: guaranteed — data on N+1 nodes before client gets success.
     Availability: if any follower is slow/down → ALL writes block.
     Latency: max follower latency added to every write.
     Use: financial systems where data loss is unacceptable.

  2. ASYNCHRONOUS REPLICATION:
     Leader: receives write → writes locally → returns to client → sends WAL to followers.

     Durability: data may be on leader only when client gets success.
     If leader crashes before WAL reaches followers: COMMITTED DATA LOST (follower is behind).
     Availability: follower lag doesn't block writes. Leader proceeds immediately.
     Latency: no follower roundtrip added.
     Use: social media (losing one tweet is acceptable), read-heavy workloads.

  3. SEMI-SYNCHRONOUS (MySQL default):
     Leader: waits for ACK from AT LEAST ONE follower (not all).
     At least one follower always has the latest data.
     If that follower is promoted: no data loss.
     Availability: only ONE follower's latency affects writes (not all).
     Good balance: one follower guarantees durability; others can be async.

LEADER ELECTION (what happens when leader fails):

  SCENARIO: Leader crashes. 3 followers remain.

  WITHOUT CONSENSUS:
    Network partition: followers can't reach leader.
    Followers can't tell: "leader crashed" vs "network partition — leader still alive"
    Two followers: "leader is dead → I'm the new leader!"
    SPLIT BRAIN: two leaders both accepting writes → divergent state → data corruption.

  WITH CONSENSUS (Raft algorithm simplified):
    1. Follower detects: no heartbeat from leader for election_timeout (150-300ms).
    2. Follower: increments term, becomes CANDIDATE, votes for itself.
    3. Candidate: sends RequestVote to all other followers.
    4. Followers: vote for candidate if they haven't voted this term AND
                  candidate's log is at least as up-to-date.
    5. If candidate receives majority votes (N/2+1): becomes LEADER.
    6. New leader: sends heartbeats immediately (suppress other elections).
    7. Old leader (if alive): sees higher term → steps down → becomes follower.

    SAFETY: majority (quorum) ensures only one leader per term.
    N=3 nodes: need 2 votes. Leader crashes → 2 remaining → elect new leader.
    N=4 nodes: need 3 votes. Two nodes down → can't form quorum → no election.

    Recommendation: odd number of nodes (3, 5, 7) for easy majority.

REPLICATION LAG (key problem in async replication):

  SCENARIO: User writes a tweet, then reads their own tweet.

  Request 1: POST /tweets → goes to leader → written at T=100ms
  Request 2: GET /tweets/mine → goes to read replica → data only up to T=50ms
  Result: User's own tweet is missing (read-your-writes violation!)

  SOLUTIONS:

  A. Read-your-writes consistency:
     After write: route subsequent reads to leader (for 1-2 seconds).
     OR: route reads for items the user modified to leader always.

  B. Monotonic reads:
     User always reads from the SAME follower replica.
     Same follower: data only moves forward in time (never backwards).
     Different follower per request: user might see tweet, then not see it, then see it again.
     Solution: sticky routing (same user → same replica) using consistent hashing.

  C. Accept eventual consistency (simplest, often OK):
     "Your tweet will appear within 30 seconds."
     Most social media platforms do this.

KAFKA PARTITION LEADERSHIP (leader-follower in message queues):

  Kafka topic partitioned into N partitions.
  Each partition: 1 leader broker + M follower brokers.

  Write (producer): always goes to partition leader.
  Read (consumer): goes to partition leader (by default; Kafka 2.4+ allows follower reads).

  Leader fails: ZooKeeper triggers leader election.
  New leader: chosen from in-sync replicas (ISR — followers fully caught up).
  Out-of-sync replica: cannot be elected leader (would cause data loss).

  ISR (In-Sync Replicas):
    replica.lag.time.max.ms = 10000  // follower must send heartbeat within 10 seconds
    Follower behind > 10 seconds: removed from ISR.
    Only ISR members eligible for leader election.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Leader-Follower:

- Multi-leader writes: conflicts when two leaders accept concurrent writes to same key
- No ordering: can't guarantee consistent write order → divergent state
- No read scale-out: single node handles all reads and writes

WITH Leader-Follower:
→ Write consistency: single writer (leader) ensures total order of writes
→ Read scale-out: followers serve reads → 5 followers = 5× read throughput
→ High availability: follower promotion on leader failure → automatic failover

---

### 🧠 Mental Model / Analogy

> An orchestra conductor (leader) keeps all musicians (followers) in sync. Only the conductor decides tempo and dynamics — musicians follow. If a musician plays a wrong note (out of sync), the conductor corrects them. If the conductor collapses, the first violinist (most senior musician / most up-to-date follower) takes over as interim conductor. No two conductors simultaneously — that causes cacophony (split brain).

"Orchestra conductor" = leader node (single authoritative source for writes)
"Musicians following conductor" = follower nodes (replicate leader's state)
"Only conductor decides tempo" = only leader accepts writes (prevents conflicts)
"First violinist takes over" = leader election (most up-to-date follower promoted)
"Two conductors = cacophony" = split brain (two leaders → divergent state → data corruption)

---

### ⚙️ How It Works (Mechanism)

**PostgreSQL primary-replica with Patroni (production HA):**

```yaml
# Patroni configuration (patroni.yml):
scope: my-postgres-cluster
name: node1

restapi:
  listen: 0.0.0.0:8008
  connect_address: node1:8008

etcd:
  hosts: etcd1:2379,etcd2:2379,etcd3:2379 # consensus storage for leader election

bootstrap:
  dcs:
    ttl: 30 # leader lease TTL (seconds)
    loop_wait: 10 # how often Patroni checks
    retry_timeout: 10
    maximum_lag_on_failover: 1048576 # don't promote follower > 1MB behind
    synchronous_mode: false # set true for sync replication

  pg_hba:
    - host replication replicator 0.0.0.0/0 md5 # allow replication connections

postgresql:
  listen: 0.0.0.0:5432
  connect_address: node1:5432
  data_dir: /var/lib/postgresql/data

  parameters:
    wal_level: replica # enables WAL streaming
    hot_standby: "on" # followers can serve reads
    max_wal_senders: 10 # max parallel replication streams
    synchronous_commit: "remote_apply" # semi-sync: wait for at least 1 follower
```

**Application: routing writes to leader, reads to followers:**

```java
@Configuration
public class DataSourceRouter extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        // Read-only transactions → follower replica:
        if (TransactionSynchronizationManager.isCurrentTransactionReadOnly()) {
            return "follower"; // round-robin across replicas in production
        }
        return "leader";  // all writes to leader (primary)
    }
}

// Service layer:
@Service
public class ProductService {

    @Transactional(readOnly = true)  // → routes to follower replica
    public List<Product> getProducts() {
        return productRepository.findAll();
    }

    @Transactional  // → routes to leader (writes)
    public Product createProduct(Product product) {
        return productRepository.save(product);
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Distributed Systems (consistency requirement)
        │
        ▼
Leader-Follower Pattern ◄──── (you are here)
(single leader for writes, followers for reads)
        │
        ├── Write-Ahead Logging (mechanism for replication)
        ├── Raft / Paxos (leader election consensus algorithm)
        └── Active-Passive (leader-follower at infrastructure level)
```

---

### 💻 Code Example

**Leader election via Redis distributed lock:**

```java
@Component
public class LeaderElection {

    @Autowired private RedissonClient redissonClient;
    private volatile boolean isLeader = false;

    @Scheduled(fixedDelay = 5000)  // check every 5 seconds
    public void electLeader() {
        RLock leaderLock = redissonClient.getLock("service:leader");

        // Try to acquire/renew leadership:
        boolean acquired = leaderLock.tryLock();  // TTL via Redisson watchdog

        if (acquired && !isLeader) {
            isLeader = true;
            log.info("This instance is now the LEADER");
            onLeadershipGained();
        } else if (!acquired && isLeader) {
            isLeader = false;
            log.info("Leadership lost — becoming FOLLOWER");
            onLeadershipLost();
        }
    }

    private void onLeadershipGained() {
        // Start leader-only tasks: cron jobs, partition leadership, coordination
    }

    private void onLeadershipLost() {
        // Stop leader-only tasks: become a passive follower
    }

    public boolean isLeader() {
        return isLeader;
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Leader-follower means only the leader can be read from | Followers are typically used for reads (this is the entire point of having followers for scale). Only writes must go to the leader. The trade-off is replication lag — reads from followers may be slightly behind. For consistency-sensitive reads (read-your-writes), route to leader                                                                  |
| Leader election is instantaneous                       | Leader election takes time: election timeout (150-300ms) + vote round trips + leader announcement + followers reconfiguring. PostgreSQL/Patroni failover: typically 30-60 seconds. Kafka leader election: typically 10-30 seconds. Plan for this downtime window in SLAs and use health checks to route traffic away during election                     |
| Multi-leader is always better than single-leader       | Multi-leader (multiple nodes accept writes) eliminates the leader as a bottleneck but introduces conflict resolution complexity. Concurrent writes to the same key by two leaders create conflicts that must be resolved (last-write-wins, CRDTs, application-level merge). Single-leader avoids this at the cost of write throughput ceiling            |
| Automatic failover is risk-free                        | Automatic failover without quorum protection can cause split-brain. Two network-partitioned groups each elect a leader → two leaders accepting writes → divergent state → corruption on network heal. Production systems need fencing (STONITH — Shoot The Other Node In The Head) to ensure the old leader cannot accept writes before the new one does |

---

### 🔥 Pitfalls in Production

**Split-brain after network partition:**

```
PROBLEM: Network partition causes two leaders

  Setup: 3-node Kafka cluster (broker1, broker2, broker3)
  Normal: broker1 = leader for partition 0

  Network partition:
    broker1 isolated from broker2, broker3
    broker2 + broker3 can reach each other

  broker2, broker3: "We can't see broker1 → it's dead → elect new leader"
  → broker2 elected as new leader for partition 0

  broker1: "I can't see broker2, broker3 → they might be dead → I'm still leader"
  → broker1 still accepts producer writes!

  SPLIT BRAIN: both broker1 and broker2 accept writes as "leader"

  Producer writes to broker1: offset 100, 101, 102 (divergent)
  Producer writes to broker2: offset 100, 101, 102 (different messages)

  On partition heal: Kafka must choose one leader's log → other's writes DISCARDED.

  PROTECTION (Kafka's approach):
    Epoch-based fencing:
    - Each election increments the leader epoch.
    - Old leader: receives write with lower epoch → REJECTS (knows it's been superseded)
    - Only current epoch's leader can write.

  PROTECTION (general):
    min.insync.replicas = 2  (Kafka: require at least 2 replicas to be in sync)
    acks = all              (producer: wait for all ISR replicas to acknowledge)

    With 3 brokers and min.insync.replicas=2:
    Network partition (1 broker isolated): isolated broker can't form quorum of 2
    → isolated broker rejects writes → no split brain
    → partition side with 2 brokers: forms quorum → correct leader elected
```

---

### 🔗 Related Keywords

- `Write-Ahead Logging (System)` — mechanism by which leader replicates state to followers
- `Distributed Locks` — simple leader election implementation for single-node coordination
- `Raft` — consensus algorithm for safe leader election in distributed systems
- `Active-Passive` — infrastructure-level analogy to leader-follower at the database layer
- `Database Replication` — practical implementation of leader-follower for relational databases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Single leader accepts writes; followers   │
│              │ replicate and serve reads                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Relational DB HA; Kafka partitions;       │
│              │ cron job deduplication across fleet       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Auto-failover without quorum protection;  │
│              │ async replication for financial data      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Orchestra conductor — only one leads;    │
│              │  musicians follow; first violinist steps  │
│              │  up if conductor collapses."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Raft → Write-Ahead Logging                │
│              │ → Database Replication                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A PostgreSQL cluster has 1 primary and 2 replicas using asynchronous replication. The primary is at LSN (Log Sequence Number) 1000. Replica A is at LSN 990. Replica B is at LSN 1000 (fully caught up). The primary crashes suddenly. Which replica should be promoted to leader, and why? What happens to the 10 WAL records that Replica A is missing? A user had just committed a transaction at LSN 995 — is their data guaranteed to survive this failover? How would your answer change with synchronous replication?

**Q2.** You're designing a distributed cron job system where one of N service instances should execute a scheduled task. Using Redis as the coordination mechanism: (a) design the leader election protocol using Redis TTL-based locks; (b) what happens if the elected leader's Redis connection drops mid-task (it still holds the lock in Redis's view but can't communicate)? (c) how do you prevent the situation where no node executes the task (all nodes fail to acquire the lock simultaneously due to a Redis outage)?
