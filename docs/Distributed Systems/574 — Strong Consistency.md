---
layout: default
title: "Strong Consistency"
parent: "Distributed Systems"
nav_order: 574
permalink: /distributed-systems/strong-consistency/
number: "574"
category: Distributed Systems
difficulty: ★★★
depends_on: "Consistency Models, Linearisability"
used_by: "Distributed Locks, ZooKeeper, etcd"
tags: #advanced, #distributed, #consistency, #linearisability, #replication
---

# 574 — Strong Consistency

`#advanced` `#distributed` `#consistency` `#linearisability` `#replication`

⚡ TL;DR — **Strong Consistency** (linearisability) guarantees every read returns the most recently committed write — as if the distributed system were a single machine with a single shared memory, regardless of which node handles the request.

| #574            | Category: Distributed Systems       | Difficulty: ★★★ |
| :-------------- | :---------------------------------- | :-------------- |
| **Depends on:** | Consistency Models, Linearisability |                 |
| **Used by:**    | Distributed Locks, ZooKeeper, etcd  |                 |

---

### 📘 Textbook Definition

**Strong Consistency**, formally called **linearisability**, is a consistency model guaranteeing that every operation on a distributed system appears to execute atomically at a single point in time between its invocation and response, and these points form a total order consistent with real-time ordering. A read operation on a strongly consistent system always returns the value of the most recently completed write. In practice, strong consistency is implemented via: (1) **single-leader routing** — all reads and writes go through a single leader, ensuring a single source of truth; (2) **synchronous quorum** — a majority of replicas must acknowledge a write before it is considered committed, and reads must also contact a quorum; or (3) **consensus protocols** (Raft, Paxos) which elect a leader and maintain a consistent replicated log. Strong consistency sacrifices availability and latency in exchange for the simplest programming model — application code can treat the distributed system as a single computer.

---

### 🟢 Simple Definition (Easy)

Strong consistency: "No matter which database server you ask, you always get the most up-to-date answer." If Alice writes x=10, Bob reads x immediately after on a different server, he gets 10 — never an older value. Achieved by making every server coordinate before answering. Slower than eventually consistent systems, but no surprises.

---

### 🔵 Simple Definition (Elaborated)

Strong consistency enables simple application code. Example: distributed counter (number of available seats on a flight). Without strong consistency: Server A says 2 seats remain, Server B also says 2 seats remain. Two users simultaneously book the last 2 seats on different servers → both succeed → 4 seats sold from 2 remaining — overbooking! With strong consistency: all booking operations go through a single leader or quorum. Second booking sees 1 seat remaining (first is already committed) → correct. Or: the leader coordinates and only one succeeds while the other fails with "0 seats remaining."

---

### 🔩 First Principles Explanation

**Implementing strong consistency: single-leader vs quorum:**

```
SINGLE-LEADER IMPLEMENTATION:

  Architecture: all writes AND reads go to the leader (primary).

  Client 1: writes x=10 → leader persists, replicates (async) → ACKs client 1.
  Client 2: reads x → goes to LEADER (not replica) → returns 10 (always fresh).

  Guarantee: since all reads/writes go through one node, it's equivalent to a single computer.

  Problem: leader is a bottleneck. Leader failure = system unavailable until new leader elected.

  PostgreSQL implementation:
    - primary_conninfo in recovery.conf: applications write to primary
    - For strong reads: connect to primary. For weaker reads: replica.
    - hot_standby = on: allows reads from replica (but reads may be stale — NOT strong consistency)

  QUORUM-BASED IMPLEMENTATION:

  Quorum: minimum number of nodes that must agree for an operation to succeed.
  N = total replicas, W = write quorum, R = read quorum.

  Strong consistency requirement: W + R > N

  Example: N=3, W=2, R=2. W+R=4 > 3=N → strong consistency guaranteed.

  WHY this works:
    Write quorum (W=2): write must succeed on at least 2 of 3 nodes.
    Read quorum (R=2): read must contact at least 2 of 3 nodes.
    Overlap: at least 1 node is in BOTH the write quorum and read quorum.
    That overlapping node has the latest write.
    Therefore: a quorum read ALWAYS includes at least 1 node with the latest write.

  Cassandra QUORUM example:
    Replication factor RF=3 (3 copies of each row).
    QUORUM = RF/2 + 1 = 2 (floor of 3/2 + 1).

    Write: send to 3 nodes, wait for 2 to ACK → write committed.
    Read: send to 3 nodes, wait for 2 to respond, take latest version.

    Node 1: x=10 (latest)  ─── quorum read contacts nodes 1+2 ───► returns x=10 ✓
    Node 2: x=10 (latest)
    Node 3: x=5 (stale)    (not contacted in this read)

    Node 1: x=10 (latest)
    Node 2: x=5 (stale)    ─── quorum read contacts nodes 2+3 ───► returns x=10 ✓
    Node 3: x=10 (latest)

    IMPOSSIBLE: read quorum (2 nodes) always overlaps with write quorum (2 nodes)
                Therefore: always at least one node with the latest write is contacted.

WRITE PATH (RAFT CONSENSUS):

  Raft is the most widely used protocol for strongly consistent distributed systems.

  Leader: receives client write.
  Leader → Followers: AppendEntries RPC (replicate log entry).

  Client: WRITE x=10 → Leader
  Leader: appends to local log (log index=42, term=3, value=x=10)
  Leader → Follower1: AppendEntries(index=42, term=3, x=10) → ACK
  Leader → Follower2: AppendEntries(index=42, term=3, x=10) → ACK

  Once majority (leader + 1 follower) acknowledge → entry is "committed".
  Leader: updates commit index = 42. Responds to client: x=10 written ✓.

  READ PATH (linearisable reads in Raft):

  Option 1: LEADER READS ONLY.
    Client reads always go to leader. Leader has latest committed state.
    Strongly consistent. But: leader bottleneck.

  Option 2: READ INDEX.
    Leader: record current commit index (e.g., 42) as the read index.
    Leader: send heartbeat to majority → confirm still leader (prevents stale leader reads).
    Once confirmed: serve read from local state machine. Return result.
    Slightly more expensive than follower reads but maintains linearisability.

  Option 3: LEASE-BASED READS.
    After winning election: leader holds a "lease" for a bounded time period.
    During lease: leader knows it's the only valid leader → can serve reads without heartbeat.
    Lease expires after election timeout (e.g., 150-300ms).
    Caveat: requires tightly synchronized clocks. If clock skew > lease timeout → reads may be stale.

LATENCY IMPACT:

  Single-region (same datacenter):
    Leader write: ~1ms (local write + intra-DC replication)
    Quorum read: ~2ms (contact N nodes, wait for R responses)

  Multi-region (US + EU + APAC):
    US → EU RTT: ~80ms
    US → APAC RTT: ~180ms

    Raft leader in US, followers in EU and APAC:
    Write: leader → EU (80ms) + leader → APAC (180ms).
    Wait for MAJORITY: leader (0ms) + EU (80ms) = quorum of 2.
    APAC's 180ms NOT in critical path (majority is already reached at 2/3 nodes).
    Write latency: ~80ms (limited by EU RTT, not APAC RTT).

    Google Spanner with TrueTime: ~5-10ms for global writes by using GPS-synchronized
    clocks instead of traditional consensus rounds.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT strong consistency:

- Race conditions in critical sections: two nodes believe they are the leader simultaneously
- Financial anomalies: two withdrawals both succeed because both saw the balance as sufficient
- Distributed locks that don't work: lock acquired on node A while node B thinks no lock exists

WITH strong consistency:
→ Single source of truth: code can treat the distributed system as a single computer
→ Correct distributed algorithms: leader election, distributed locking, sequence number generation
→ Safety for critical data: account balances, inventory counts, configuration state

---

### 🧠 Mental Model / Analogy

> A single judge making all ruling decisions in a courtroom, with all lawyers required to submit motions to and receive answers from only that judge. No matter how many lawyers are in the room (replicas), every ruling goes through the single judge who has the complete, up-to-date case record. Strong consistency: every read/write passes through the judge. No lawyer (client) can get conflicting information from different sources. The trade-off: the judge is a bottleneck — the busier the court, the longer each lawyer waits. If the judge is sick (leader failure), the court must pause until a replacement judge is appointed (leader election).

"Single judge with complete case record" = strongly consistent leader with latest state
"All motions must go to the judge" = all reads/writes routed to leader
"Judge is a bottleneck" = single leader limits write throughput
"Replacing a sick judge" = Raft/Paxos leader election on failure

---

### ⚙️ How It Works (Mechanism)

**ZooKeeper: strongly consistent distributed configuration store:**

```java
// ZooKeeper provides linearisable reads/writes for configuration and coordination:
// Raft-like ZAB (ZooKeeper Atomic Broadcast) protocol ensures strong consistency.

@Component
public class DistributedConfigService {

    private final CuratorFramework zkClient;
    private static final String CONFIG_PATH = "/service/config/feature-flag";

    // Strongly consistent write (goes through ZK leader):
    public void setFeatureFlag(boolean enabled) throws Exception {
        byte[] data = String.valueOf(enabled).getBytes();

        if (zkClient.checkExists().forPath(CONFIG_PATH) == null) {
            zkClient.create()
                .creatingParentsIfNeeded()
                .withMode(CreateMode.PERSISTENT)
                .forPath(CONFIG_PATH, data);
        } else {
            zkClient.setData().forPath(CONFIG_PATH, data);
        }

        // After this returns: majority of ZK nodes have the new value.
        // ANY ZK node queried next will return the updated value.
        // → Linearisability guaranteed by ZAB protocol.
    }

    // Strongly consistent read (sync() ensures we see latest committed value):
    public boolean getFeatureFlag() throws Exception {
        // sync() forces ZK to contact the leader before serving this read:
        // Without sync(): read from local follower cache → may be slightly stale
        // With sync(): ZK waits for follower to be caught up to leader → linearisable
        zkClient.sync().forPath(CONFIG_PATH);

        byte[] data = zkClient.getData().forPath(CONFIG_PATH);
        return Boolean.parseBoolean(new String(data));
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Consistency Models (spectrum of all models)
        │
        ▼
Strong Consistency ◄──── (you are here)
(linearisability: strongest model)
        │
        ├── Linearisability (formal definition)
        ├── Raft / Paxos (consensus protocols that implement it)
        └── Distributed Locks (application of strong consistency)
```

---

### 💻 Code Example

**etcd: strongly consistent key-value store (used in Kubernetes):**

```go
package main

import (
    "context"
    "fmt"
    "time"

    clientv3 "go.etcd.io/etcd/client/v3"
)

// etcd uses Raft consensus → all operations are linearisable by default.

func main() {
    cli, _ := clientv3.New(clientv3.Config{
        Endpoints:   []string{"etcd1:2379", "etcd2:2379", "etcd3:2379"},
        DialTimeout: 5 * time.Second,
    })
    defer cli.Close()

    ctx := context.Background()

    // STRONGLY CONSISTENT WRITE:
    // Raft replicates this to a majority before returning.
    _, err := cli.Put(ctx, "/leader-lock", "node-A")
    if err != nil {
        panic(err)
    }

    // STRONGLY CONSISTENT READ:
    // etcd defaults to linearisable reads — contacts leader to confirm latest value.
    resp, _ := cli.Get(ctx, "/leader-lock")
    fmt.Printf("Value: %s\n", resp.Kvs[0].Value)  // Always "node-A" — linearisable.

    // SERIALISABLE READ (weaker, faster — may be slightly stale):
    // clientv3.WithSerializable() allows reading from follower cache:
    resp, _ = cli.Get(ctx, "/leader-lock", clientv3.WithSerializable())
    fmt.Printf("Serialisable read: %s\n", resp.Kvs[0].Value)  // May lag slightly.

    // ATOMIC COMPARE-AND-SWAP (CAS) for leader election:
    // If /leader-lock == "" then set it to "node-A"
    // Strongly consistent: only one concurrent caller can win this CAS.
    txn := cli.Txn(ctx)
    txnResp, _ := txn.
        If(clientv3.Compare(clientv3.Version("/leader-lock"), "=", 0)).
        Then(clientv3.OpPut("/leader-lock", "node-A")).
        Else(clientv3.OpGet("/leader-lock")).
        Commit()

    if txnResp.Succeeded {
        fmt.Println("Won leader election!")  // Node A is now leader.
    } else {
        fmt.Printf("Lost election. Current leader: %s\n", txnResp.Responses[0].GetResponseRange().Kvs[0].Value)
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Strong consistency means no downtime                        | Strong consistency means coordinated reads and writes, but it does NOT prevent failures. During a network partition, a strongly consistent system will REFUSE to serve requests on the minority partition (to avoid inconsistency). This means reduced availability during failures — the opposite of always-on. ZooKeeper: loses availability during partition to maintain consistency                            |
| Reading from any replica gives you strong consistency       | Reading from a replica without synchronisation gives you at-best monotonic reads or read-your-writes — NOT linearisability. To read with strong consistency from a replica, the system must confirm the replica is caught up (e.g., etcd's sync() call, DynamoDB's ConsistentRead=true) — this adds latency equivalent to contacting the leader                                                                    |
| Strong consistency solves all race conditions               | Strong consistency covers read-write and write-write conflicts on shared data. It does NOT automatically solve application-level race conditions. Example: read balance (100) → compute new balance (100-50=50) → write (50). Between read and write, another process also read 100 and is writing 50. Result: lost update. Solution: Compare-And-Swap (CAS) or database transactions, not just strong consistency |
| Strong consistency is always required for financial systems | Many financial systems deliberately use eventual consistency for certain operations (e.g., viewing transaction history, balance after close-of-business). Strong consistency is required only for operations where double-spending or lost updates would occur — typically write operations on account balances. Read operations showing yesterday's balance to a user can safely be eventual                      |

---

### 🔥 Pitfalls in Production

**Stale reads from replica masquerading as "strongly consistent":**

```
PROBLEM: Application configured to use read replicas "for performance"
         → reads from replica after write → stale data → application logic errors.

  Kubernetes cluster uses etcd as the state store.
  Application code reads Pod status from etcd follower (serialisable read):

  Step 1: Leader writes: Pod "api-pod-1" status = TERMINATING (at Raft index 1000)
  Step 2: Application reads: GET /pods/api-pod-1 → follower at index 990 (lagging)
  Step 3: Follower returns: status = RUNNING (stale by 10 log entries)
  Step 4: Application: "pod is running, send it traffic!" → sends traffic to terminating pod.

  This exact bug caused production issues in early Kubernetes versions.

BAD: Serialisable read from follower for status check:
  // etcd client — serialisable = read from follower cache:
  resp, _ := cli.Get(ctx, "/registry/pods/default/api-pod-1",
      clientv3.WithSerializable())  // MAY BE STALE

FIX: Linearisable read (default in etcd) ensures freshness:
  // etcd default: linearisable — contacts leader to confirm current read index:
  resp, _ := cli.Get(ctx, "/registry/pods/default/api-pod-1")
  // ^^^ No WithSerializable() → contacts leader → guaranteed latest value.

  // Performance optimization: use serialisable ONLY for reads where
  // staleness is acceptable (e.g., displaying list of pods to human operator):
  // Kubelet status updates: LINEARISABLE (critical path — pod lifecycle)
  // kubectl get pods display: SERIALISABLE acceptable (human reading, slight lag ok)
```

---

### 🔗 Related Keywords

- `Linearisability` — the formal definition of strong consistency (every op appears atomic at a single instant)
- `Raft` — consensus protocol implementing strong consistency via replicated log
- `Distributed Locks` — require strong consistency to prevent two nodes thinking both hold the lock
- `Eventual Consistency` — the opposite end of the spectrum; weaker but higher availability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Every read returns the most recent write; │
│              │ distributed system = single computer view │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Distributed locks; leader election;       │
│              │ financial balances; config state          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-throughput reads where slight        │
│              │ staleness is acceptable (analytics, feeds)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One judge, every ruling final — no stale │
│              │  verdicts, but you must wait your turn."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Linearisability → Raft → ZooKeeper/etcd  │
│              │ → Distributed Locks → Quorum              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed rate limiter needs to enforce "maximum 100 requests per second per user." It's deployed across 3 nodes. The counter for user Alice is stored with replication factor 3. If the rate limiter uses eventual consistency for the counter reads and writes, what attack could a user exploit? What minimum quorum (W and R) with N=3 ensures no user can exceed 100 requests/second even when sending requests to different nodes simultaneously?

**Q2.** Google Spanner claims to provide "externally consistent" transactions globally. External consistency is stronger than linearisability — it applies across multiple operations (transactions) not just single reads/writes. How does Spanner use TrueTime (GPS + atomic clock synchronized timestamps with an uncertainty bound ε) to achieve external consistency? Specifically: why does Spanner's commit protocol wait for the uncertainty interval ε before returning a commit response to the client?
