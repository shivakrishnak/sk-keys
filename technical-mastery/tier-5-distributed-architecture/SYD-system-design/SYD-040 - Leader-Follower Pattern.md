---
id: SYD-040
title: Leader-Follower Pattern
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-019, SYD-039
used_by: ""
related: SYD-011, SYD-019, SYD-039, SYD-062
tags:
  - architecture
  - distributed-systems
  - coordination
  - consensus
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/syd/leader-follower-pattern/
---

⚡ TL;DR - The leader-follower (primary-replica) pattern
designates one node as the leader (primary) that
makes decisions, coordinates writes, or performs the
single-threaded work; other nodes are followers
(replicas) that replicate the leader's state and can
take over if the leader fails. It is the foundational
pattern for database replication, Kafka partition
leaders, consensus protocols (Raft), and distributed
job schedulers. The key challenge is leader election:
safely promoting a follower to leader without causing
split-brain (two nodes both believing they are the leader).

| #040 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Redundancy and Failover, Distributed Locks | |
| **Used by:** | (Saga Pattern) | |
| **Related:** | Database Replication, Redundancy and Failover, Distributed Locks, Saga Pattern | |

---

### 🔥 The Problem This Solves

**DISTRIBUTED COORDINATION PROBLEM:**
A Kafka cluster has 3 brokers: B1, B2, B3. Partition
0 has data that must be written to exactly one broker
(the leader) and replicated to others. Without a
designated leader:
- All 3 brokers might accept writes independently →
  divergent state (split-brain)
- Reads from any broker return different data →
  consistency violation
- No single authority to know "what is the next offset?"

**THE SPLIT-BRAIN SCENARIO:**
In a 3-node database cluster, the network briefly
partitions: B1 can see B2 but not B3. B3 can see
neither B1 nor B2. B1 and B3 both think the other
is dead. BOTH promote themselves to leader. Both
accept writes. Network heals: B1 and B3 have
different data. Data is corrupted.

The leader-follower pattern with proper election
(requiring quorum) prevents split-brain: a node
can only become leader if it has votes from a
majority (2 of 3 nodes). In the partition above,
only B1/B2 have a majority → only one leader possible.

---

### 📘 Textbook Definition

**Leader-follower pattern:** A distributed systems
design where one node (leader/primary) has a
distinguished role: it is the authoritative source
for writes, decisions, or coordination for a given
resource. Other nodes (followers/replicas/secondaries)
replicate the leader's state and handle reads (in
some configurations). When the leader fails, one
of the followers is elected as the new leader through
a leader election protocol.

**Split-brain:** The failure condition where two nodes
simultaneously believe they are the leader. This causes
data divergence and must be prevented. Prevention:
quorum-based elections (requires majority vote),
fencing tokens (STONITH: "Shoot The Other Node In
The Head" - forcing a suspected old leader to stop).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One node is the boss (leader). Others are assistants
(followers). If the boss disappears, the team elects
a new boss. Only one boss at a time.

**One analogy:**
> A restaurant with a head chef (leader) and sous-chefs
> (followers):
> - Head chef decides the menu and plating standards
>   (authoritative decisions)
> - Sous-chefs execute and learn the recipes (replicate)
> - If the head chef calls in sick (leader fails):
>   sous-chefs vote to promote the most senior one
>   (leader election via seniority = most up-to-date log)
> - Two head chefs simultaneously = kitchen chaos
>   (split-brain)

**One insight:**
The leader-follower pattern is a specialization of
consensus: the entire cluster agrees on who is the
leader. Without consensus, you get split-brain. Raft
and Paxos are consensus algorithms that implement
safe leader election as their primary mechanism.
Understanding leader-follower is understanding why
consensus matters.

---

### 🔩 First Principles Explanation

**LEADER ELECTION MECHANISMS:**

**1. Lease-based (distributed lock approach):**
```
Every N seconds, leader renews a lease (Redis TTL).
If leader fails to renew, lease expires.
Followers detect lease expiry → start election.
First follower to acquire lease = new leader.

Simple but has fencing problem:
  Old leader had lease, was paused (GC)
  Lease expired, new leader elected
  Old leader resumes → two leaders briefly
  
Mitigation: fencing token (lease version number)
  Old leader's actions rejected by followers
  because their lease version is older.
```

**2. Quorum-based election (Raft/Paxos):**
```
Raft leader election:
  1. Follower detects no heartbeat from leader
     (election timeout: randomized 150-300ms)
  2. Follower increments term, votes for itself,
     sends RequestVote to other nodes
  3. Other nodes grant vote if:
     - They haven't voted in this term AND
     - Candidate's log is at least as up-to-date
  4. Candidate receives votes from majority →
     becomes leader for this term
  5. New leader sends heartbeats to all followers

Term number is the fencing token:
  Old leader (term 4) tries to write to followers
  Followers already in term 5 → reject term 4 writes
  Old leader cannot corrupt state
```

**3. ZooKeeper ephemeral sequential nodes:**
```
All candidates create ephemeral sequential nodes:
  /leader/candidate-0000000001 (node 1)
  /leader/candidate-0000000002 (node 2)
  /leader/candidate-0000000003 (node 3)

Leader = lowest-numbered node holder
Followers watch the node just below them:
  node2 watches node1's deletion
  node3 watches node2's deletion

If node1 dies: its ephemeral node is auto-deleted
node2 detects deletion → becomes leader (now lowest)

Benefits:
  No thundering herd (each watches only its predecessor)
  Built-in fencing (leader lease is ephemeral node)
  No duplicate leader possible (ZooKeeper guarantees)
```

**FOLLOWER READ STALENESS:**
```
Leader handles all writes.
Followers replicate: may lag behind leader.

If reads from followers: stale data possible.
  Leader write: stock=0 (out of stock)
  Follower read (replication lag 1 second): stock=5
  Customer buys the item based on stale follower read
  → Inventory oversell

Options:
  Read-your-writes: read from leader for your own writes
  Eventual consistency: acceptable lag for non-critical
    reads
  Sync replication: followers ACK write before leader
    responds
    (stronger consistency, higher latency)
  Semi-sync: at least 1 follower must ACK (MySQL semi-sync)
```

---

### 🧪 Thought Experiment

**SCENARIO: Kafka partition leadership**

A Kafka topic has 10 partitions, each with a leader
broker and 2 follower brokers. All 3 brokers run on
different servers. Broker B1 hosts the leader for
partitions 0, 3, 6. The server running B1 crashes.

**What happens (Kafka's leader election):**
1. Kafka controller (a broker elected via ZooKeeper)
   detects B1 is down (heartbeat missing for 30s)
2. Controller selects a new leader for each affected
   partition from the ISR (In-Sync Replicas - followers
   that are fully caught up)
3. For partition 0: ISR = [B2, B3]. Controller
   elects B2 as new leader.
4. All producers/consumers are notified of new leader
5. Producers retry → automatically connect to B2
6. Total election time: typically 10-30 seconds

**What if B2 also crashes simultaneously?**
If ISR for partition 0 = [B3] and B3 is elected.
If ISR = [] (all ISR members are down):
  - Kafka can elect an "unclean leader" (a follower
    that was not in ISR → may be missing recent messages)
    `unclean.leader.election.enable=true` (default: false)
  - Or wait for an ISR member to recover (availability
    tradeoff: partition is unavailable until ISR member recovers)

**The CAP tradeoff in practice:**
  `unclean.leader.election=true`: availability (partition
  stays open), consistency (may lose recent messages).
  `unclean.leader.election=false`: consistency (no
  data loss), availability (partition unavailable if
  all ISR members are down).

---

### 🧠 Mental Model / Analogy

> Leader-follower is like the electoral college:
>
> Leader = elected president (one decision-maker)
> Followers = congress members (replicate policy)
> Election = campaign + votes (> 50% = majority)
> Term = presidential term (numbered, increasing)
> Old president can't override new one
>   (fencing: term number rejects old-term actions)
> If president disappears mid-term:
>   Speaker of the House becomes president
>   (follower with highest seniority / most up-to-date)
>
> Two presidents simultaneously = constitutional crisis
> (split-brain). Prevented by: quorum election + term
> fencing.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
One server is the "master" (leader). Others are "slaves"
(followers). The master accepts writes; slaves copy
them. If the master fails, one slave becomes the new
master.

**Level 2 - How to use it (junior developer):**
In most databases and message brokers, this is
transparent. PostgreSQL: primary + hot standby.
MySQL: master + replicas. Kafka: partition leaders
+ replicas. You configure it; the system manages
election. Key config: synchronous replication (strong
consistency) vs asynchronous (higher availability,
possible data loss).

**Level 3 - How it works (mid-level engineer):**
Leader election requires a quorum to avoid split-brain.
In a 3-node cluster: requires 2 votes. In a 5-node
cluster: requires 3 votes. This is why distributed
clusters use odd numbers (3, 5, 7 nodes): ties
cannot occur. The election algorithm (Raft, Paxos,
ZAB) ensures only one leader per term.

**Level 4 - Why it was designed this way (senior/staff):**
The leader bottleneck is the known limitation: all
writes must go through the leader. This limits write
throughput to what one node can handle. Multi-master
replication (any node accepts writes, eventual consistency)
exists but is significantly more complex (conflict
resolution needed). Leader-follower is the correct
tradeoff when writes must be ordered: payment systems,
financial ledgers, order processing. Multi-master is
acceptable for non-conflicting operations: shopping
carts (CRDTs), analytics events.

**Level 5 - Mastery (distinguished engineer):**
The Raft paper (Ongaro & Ousterhout 2014) was published
specifically to make consensus more understandable
than Paxos. The key insight: Raft serializes all
decisions through a single leader per term, making
correctness reasoning straightforward. The leader
has the complete log up to the current term. All
decisions are linearizable (appear as if executed
by a single sequential process). This is how etcd
(Kubernetes' control plane store) and CockroachDB
achieve strong consistency without a traditional
RDBMS. The practical design question: how many nodes?
3 nodes: tolerate 1 failure. 5 nodes: tolerate 2
failures. Cost: `(N-1)/2` nodes are "wasted" maintaining
quorum. 3 nodes is the sweet spot for most deployments.

---

### ⚙️ How It Works (Mechanism)

**Raft leader election state machine:**

```
┌────────────────────────────────────────────────────────┐
│ RAFT LEADER ELECTION                                  │
│                                                        │
│  All nodes start as FOLLOWER                          │
│                                                        │
│  FOLLOWER:                                            │
│    Receives heartbeats from leader                    │
│    If no heartbeat for election_timeout:              │
│      → Become CANDIDATE                              │
│                                                        │
│  CANDIDATE:                                           │
│    Increment current_term                             │
│    Vote for self                                      │
│    Send RequestVote{term, last_log_index,             │
│                     last_log_term} to all             │
│    If receives majority votes → become LEADER         │
│    If receives heartbeat from valid leader            │
│      → revert to FOLLOWER                            │
│    If election timeout → start new election           │
│                                                        │
│  LEADER:                                              │
│    Send heartbeats to all followers every 50ms        │
│    Handle all client writes                           │
│    Replicate log entries to followers                 │
│    Commit when majority acknowledge receipt           │
│                                                        │
│ Term number increases each election.                  │
│ Nodes reject messages from old terms.                 │
│ → Split-brain prevention                              │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Simple leader election with Redis**
```python
import redis
import uuid
import time
import threading

r = redis.Redis(host="redis", port=6379)

class LeaderElection:
    """
    Leader election using Redis distributed lock.
    Simple version: suitable for single-node Redis
    (not production-grade; use etcd or Zookeeper
     for production consensus).
    """

    def __init__(self, service_name: str, ttl: int = 15):
        self.service_name = service_name
        self.lock_key = f"leader:{service_name}"
        self.node_id = str(uuid.uuid4())
        self.ttl = ttl
        self.is_leader = False
        self._heartbeat_thread = None

    def try_become_leader(self) -> bool:
        """Attempt to acquire leadership."""
        result = r.set(
            self.lock_key,
            self.node_id,
            nx=True,   # only if not exists
            ex=self.ttl
        )
        if result:
            self.is_leader = True
            self._start_heartbeat()
        return bool(result)

    def _start_heartbeat(self):
        """Extend TTL while we are the leader."""
        def heartbeat():
            while self.is_leader:
                # Renew leadership lease every TTL/3 seconds
                current = r.get(self.lock_key)
                if current == self.node_id.encode():
                    r.expire(self.lock_key, self.ttl)
                else:
                    # Lost leadership (shouldn't happen
                    # but handle gracefully)
                    self.is_leader = False
                    break
                time.sleep(self.ttl // 3)

        self._heartbeat_thread = threading.Thread(
            target=heartbeat, daemon=True)
        self._heartbeat_thread.start()

    def resign(self):
        """Voluntarily release leadership."""
        # Only release if we own the lock
        script = r.register_script("""
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
        """)
        script(keys=[self.lock_key], args=[self.node_id])
        self.is_leader = False

# Usage: distributed cron job
election = LeaderElection("payment-processor")

def run_payment_job():
    if election.try_become_leader():
        print(f"I am the leader: {election.node_id}")
        try:
            process_outstanding_payments()
        finally:
            # Keep leadership for next run unless resigning
            pass
    else:
        print("Not the leader; skipping this run")
```

**Example 2 - Detecting leader failures and failover**
```python
class ServiceMonitor:
    """
    Monitor a leader and trigger failover if it fails.
    In production: use etcd watch or ZooKeeper watcher.
    """

    def __init__(self, service_name: str):
        self.lock_key = f"leader:{service_name}"
        self.election = LeaderElection(service_name)

    def watch_for_leadership(self):
        """
        Follower watches for leader failure.
        When lock disappears: attempt to become new leader.
        """
        while True:
            leader_id = r.get(self.lock_key)

            if leader_id is None:
                # Leader expired or crashed
                print("Leader gone. Attempting election...")
                if self.election.try_become_leader():
                    print("I am the new leader!")
                    on_leader_elected()
                    return
                else:
                    print("Lost election. Still a follower.")

            elif leader_id.decode() == self.election.node_id:
                # We are the current leader
                return

            # Check every 2 seconds for leader change
            time.sleep(2)
```

**Example 3 - Kafka partition leader election (config)**
```java
// Kafka producer: automatically routes to partition leader
// No manual leader tracking needed

Properties props = new Properties();
props.put("bootstrap.servers",
    "broker1:9092,broker2:9092,broker3:9092");
props.put("key.serializer",
    "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer",
    "org.apache.kafka.common.serialization.StringSerializer");

// Durability: require all ISR replicas to acknowledge
// Strong consistency: no data loss on leader failover
props.put("acks", "all");

// Retry on transient errors (leader election in progress)
props.put("retries", 3);
props.put("retry.backoff.ms", 100);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// Kafka handles leader election transparently:
// If partition leader fails during send:
//   1. Producer gets LEADER_NOT_AVAILABLE error
//   2. Producer retries (with retry config above)
//   3. Kafka controller elects new leader (< 30s)
//   4. Producer metadata refresh → connects to new leader
//   5. Message delivered to new leader

// With acks=all: only ACKs after all ISR replicas
// have the message. Safe against leader failure.
producer.send(new ProducerRecord<>("orders", key, value));
```

---

### ⚖️ Comparison Table

| Approach | Split-Brain Risk | Election Speed | Consistency | Use Case |
|---|---|---|---|---|
| **Redis lease** | Medium (single node SPOF) | Fast (< 1s) | Weak | Simple job coordination |
| **Redis Redlock** | Low (quorum) | Fast (< 1s) | Medium | Distributed coordination |
| **ZooKeeper** | None (ZAB consensus) | Medium (1-5s) | Strong | Production leader election (Kafka) |
| **etcd (Raft)** | None (Raft consensus) | Fast (< 1s) | Strong | Kubernetes, production systems |
| **Raft in-process** | None (by construction) | Very fast (ms) | Strong | Embedded consensus (CockroachDB) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Two nodes are enough for a cluster | A 2-node cluster cannot achieve quorum on a partition (neither node can get 2/2 votes from the other). Minimum for fault tolerance: 3 nodes (can lose 1; still have quorum of 2). |
| The leader is a single point of failure | The leader is the single point for writes, but not a single point of failure. When the leader fails, a new leader is elected from followers. The election time (seconds to minutes) is the "failover time" - not permanent unavailability. |
| Followers can accept writes for better throughput | In standard leader-follower: followers do not accept writes (would cause split-brain). Multi-master replication allows writes on multiple nodes but requires complex conflict resolution. Do not confuse the two models. |

---

### 🚨 Failure Modes & Diagnosis

**Split-Brain After Network Partition**

**Symptom:**
A 3-node Kubernetes cluster: masters M1, M2, M3.
Network partition: M1 cannot reach M2/M3. M1 still
believes it is the leader (its lease has not expired yet).
M2 and M3 hold a new election and elect M2 as leader.
Both M1 and M2 accept writes for a brief period.

**Root Cause:**
The election algorithm allowed a new leader before
the old leader's lease expired. Old leader is still
running and does not know it lost leadership.

**Diagnosis in etcd:**
```bash
# Check etcd leader election status
etcdctl endpoint status \
  --endpoints=https://etcd1:2379,\
              https://etcd2:2379,\
              https://etcd3:2379 \
  -w table

# Output: IS LEADER column
# Only one node should show true
# If two nodes show "IS LEADER": split-brain

# Check current term (should be same for all healthy nodes)
etcdctl endpoint status \
  --endpoints=... | grep "Raft Term"
# Diverging terms = network partition issue
```

**Fix:**
Raft prevents split-brain by design: a node with an
old term cannot be accepted as leader by nodes with
a newer term. When the partition heals, M1 receives
M2's heartbeat with term T+1 > M1's term T. M1
immediately steps down to follower. Data written to
M1 during the partition may be lost if it was not
replicated to a majority (this is a known tradeoff:
partition writes on the minority side are rolled back).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Redundancy and Failover` - leader-follower is
  the primary mechanism for database failover
- `Distributed Locks` - leader election is implemented
  via distributed locks in simpler systems

**Builds On This (learn these next):**
- `Saga Pattern` - uses leader-follower for exactly-once
  saga execution coordination

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ One leader: authoritative for writes/   │
│               │ decisions. Followers: replicate + ready │
│               │ for failover.                           │
├───────────────┼─────────────────────────────────────────┤
│ ELECTION      │ Quorum (majority vote). Term = fencing. │
│               │ Only one leader per term possible.      │
├───────────────┼─────────────────────────────────────────┤
│ SPLIT-BRAIN   │ Two leaders = data corruption.          │
│               │ Prevented by: quorum + term fencing.    │
├───────────────┼─────────────────────────────────────────┤
│ CLUSTER SIZE  │ 3 nodes: 1 failure tolerated (quorum=2) │
│               │ 5 nodes: 2 failures tolerated (q=3)     │
│               │ Always use odd numbers!                 │
├───────────────┼─────────────────────────────────────────┤
│ SYSTEMS       │ Kafka: ZooKeeper/KRaft for election     │
│               │ PostgreSQL: Patroni for HA              │
│               │ Kubernetes: etcd (Raft) for control plan│
├───────────────┼─────────────────────────────────────────┤
│ FOLLOWER READS│ May be stale (replication lag).         │
│               │ Sync replication = consistent but slower│
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "One boss per term. Quorum for election.│
│               │  Term number rejects old-boss commands."│
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Write-Ahead Logging → Data Partitioning │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Leader handles all writes; followers replicate.
   On leader failure: quorum election (majority vote)
   picks a new leader. Quorum prevents split-brain.
2. Use odd cluster sizes (3, 5, 7). A 3-node cluster
   can tolerate 1 failure; a 5-node cluster can
   tolerate 2 failures.
3. Term number (Raft) or epoch number is the fencing
   token: old leader's writes are rejected by followers
   that have moved to a higher term. This is the
   mechanism that prevents split-brain writes.

**Interview one-liner:**
"The leader-follower pattern designates one node as the authoritative
source for writes. Followers replicate the leader's state and stand
ready for failover. The critical challenge is leader election: when
the leader fails, a new leader must be elected without allowing two
leaders simultaneously (split-brain). Raft solves this with quorum
elections (requires majority votes) and term-based fencing (nodes
reject messages from old terms). Practical note: use odd cluster sizes
(3, 5, 7) so quorum is always achievable. A 3-node cluster tolerates 1
failure; 5 nodes tolerates 2. Follower reads may return stale data
(replication lag). For strong consistency: read from leader or use
synchronous replication (at least 1 follower must ACK before write
is committed)."
