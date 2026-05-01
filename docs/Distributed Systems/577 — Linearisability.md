---
layout: default
title: "Linearisability"
parent: "Distributed Systems"
nav_order: 577
permalink: /distributed-systems/linearisability/
number: "577"
category: Distributed Systems
difficulty: ★★★
depends_on: "Strong Consistency, Consistency Models"
used_by: "Distributed Locks, etcd, ZooKeeper, Raft"
tags: #advanced, #distributed, #consistency, #correctness, #formal
---

# 577 — Linearisability

`#advanced` `#distributed` `#consistency` `#correctness` `#formal`

⚡ TL;DR — **Linearisability** is the gold standard of distributed consistency: every operation appears to execute **atomically at a single instant** in real-time between invocation and response, making the distributed system indistinguishable from a single correct machine.

| #577            | Category: Distributed Systems            | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Strong Consistency, Consistency Models   |                 |
| **Used by:**    | Distributed Locks, etcd, ZooKeeper, Raft |                 |

---

### 📘 Textbook Definition

**Linearisability** (Maurice Herlihy & Jeannette Wing, 1990) is a correctness condition for concurrent data objects that requires each operation to appear to take effect atomically at some single point in time (the **linearisation point**) that lies between the operation's invocation and its response. The history of all operations forms a total order consistent with real-time ordering: if operation A completes before operation B begins, then A appears before B in the linearisation order. Linearisability is a composable property: if each object in a system is linearisable, the system as a whole is linearisable. It is the strongest non-blocking consistency model and is equivalent to **strong consistency** or **atomic consistency** in distributed systems literature. In practice, achieving linearisability in a distributed system requires either (1) routing all operations through a single leader, (2) using a quorum protocol with W + R > N, or (3) implementing a consensus algorithm (Raft, Paxos). Linearisability is not the same as serialisability (ACID): serialisability applies to multi-operation transactions; linearisability applies to individual operations.

---

### 🟢 Simple Definition (Easy)

Linearisability: every operation on a distributed system takes effect at exactly one point in time, as if there were a single magical clock ticking globally. If Alice writes x=10 and the write "happens at" tick 42, any read that "happens at" tick 43 or later MUST return 10. No matter which server you talk to. The distributed system looks like one computer with one memory.

---

### 🔵 Simple Definition (Elaborated)

Linearisability is the key property that makes distributed systems "feel" like single machines to programmers. Without it: reading from server A might give x=10, reading from server B gives x=5 — same data, same moment. With linearisability: both servers agree on the same value at any given moment. The catch: ensuring this agreement requires servers to coordinate — if one server accepts a write, it must tell others before responding to any reads. More coordination = higher latency. That's the fundamental cost of linearisability: you pay in latency (coordination overhead) to get correct, simple programming semantics.

---

### 🔩 First Principles Explanation

**Formalising and testing linearisability with concrete histories:**

```
FORMAL DEFINITION WITH EXAMPLE:

  A history H of operations is linearisable if there exists a LEGAL SEQUENTIAL HISTORY S such that:
    1. S contains all completed operations from H.
    2. The real-time order of H is preserved: if op A completes before op B begins in H,
       then A appears before B in S.
    3. S satisfies the sequential specification of the object (e.g., register: read after write
       returns the written value).

  Example — LINEARISABLE HISTORY:
    Process P1: WRITE(x, 10) [invoked at T=1, response at T=3]
    Process P2: READ(x)       [invoked at T=2, response at T=4]
    Process P3: READ(x)       [invoked at T=5, response at T=6]

    P1's write covers time [1, 3].
    P2's read covers time [2, 4] — OVERLAPS with P1's write.
    P3's read covers time [5, 6] — AFTER P1's write completes.

    Legal linearisation: WRITE(x,10) at T=2 (within [1,3]), READ→10 at T=3, READ→10 at T=5.
    All reads after linearisation point of write return 10. ✓ LINEARISABLE.

  Example — NON-LINEARISABLE HISTORY:
    P1: WRITE(x, 10) [invoked at T=1, response at T=3] ← write COMPLETES at T=3
    P2: READ(x) [invoked at T=4, response at T=5] ← read starts AFTER write completes
    P2 returns: 5 (OLD VALUE)

    Real-time order: WRITE(x,10) completes BEFORE READ begins.
    Therefore: in any linearisation, WRITE must precede READ.
    But WRITE(x,10) preceding READ means READ must return 10.
    P2 returned 5 → VIOLATES linearisability. ✗ NON-LINEARISABLE.

    This is the classic "stale read from replica" bug. After a write completes,
    any subsequent read (on any node) must see the written value.

LINEARISABILITY VS SEQUENTIAL CONSISTENCY:

  Sequential Consistency (Lamport 1979):
    Operations may be re-ordered as long as:
    (a) within each process, program order preserved.
    (b) all processes agree on the SAME total order.

    Key difference: sequential consistency does NOT require the total order to
    respect real-time ordering between DIFFERENT processes.

  Example showing the difference:
    P1: WRITE(x, 1)      [completes at T=1]
    P2: WRITE(x, 2)      [completes at T=2]
    P3: READ(x) → 2      [at T=3]
    P4: READ(x) → 1      [at T=3]  ← same real time, different values

    LINEARISABILITY: VIOLATION. P3 reads 2 (x=2 at T=3), P4 reads 1 (x=1 at T=3).
                     In real time, x=2 was set at T=2 → after T=2, x must be 2 for all.
                     P4 reading 1 at T=3 violates real-time ordering.

    SEQUENTIAL CONSISTENCY: NOT necessarily a violation.
                     Could exist a legal sequential order where x=1 is seen by P4 before x=2.
                     As long as P4's program order is consistent: no violation.

  Sequential consistency: allowed in CPU memory models (x86 has TSO - Total Store Order).
  Linearisability: required for correct distributed algorithms (consensus, locks).

LINEARISABILITY AND THE CAP THEOREM:

  CAP's "C" = linearisability.
  During a network partition: some nodes cannot communicate.

  Maintaining linearisability under partition (CP system):
    Minority partition: MUST REFUSE OPERATIONS.
    Reason: if minority served reads/writes, it would diverge from majority.
    Diverged state → some reads return values not in the linearisation order → violation.

  Cost: CP systems like ZooKeeper return errors or timeouts on the minority side during partition.

  AP system (eventual consistency):
    Minority partition: continues to serve reads/writes.
    Data diverges from majority.
    After partition heals: conflict resolution (LWW, merge, CRDT).
    Linearisability: NOT achieved during partition period.
    "Eventually consistent" histories are not linearisable.

TESTING LINEARISABILITY: JEPSEN:

  Kyle Kingsbury (Jepsen) built a framework to test if distributed systems maintain linearisability.

  Method:
    1. Run concurrent operations from N clients.
    2. Record: operation type, arguments, start time, end time, result.
    3. Generate all possible linearisation orderings.
    4. Check if any ordering is consistent with: (a) real-time constraints, (b) sequential spec.
    5. If no valid linearisation found → system violates linearisability.

  Famous findings (simplified):
    Cassandra (2013): linearisability violated with QUORUM consistency + LWT (Lightweight Transactions).
    MongoDB (2013): data loss on primary failover (not linearisable).
    etcd 3.4+: passes linearisability tests consistently.

  This work fundamentally changed how the industry tests distributed databases.

IMPLEMENTATION PATTERNS:

  Pattern 1: SINGLE LEADER + ALL READS FROM LEADER (simplest):
    - All writes: to leader.
    - All reads: to leader (bypassing replicas entirely).
    - Leader is the linearisation point for every operation.
    - Cost: leader is a bottleneck; single point of failure (until new leader elected).

  Pattern 2: QUORUM (W + R > N):
    - Write quorum W: write must reach W nodes before ACK.
    - Read quorum R: read must contact R nodes, take latest version.
    - If W + R > N: at least 1 node is in both quorums → latest write always visible.
    - Linearisation point: write = when quorum ACKs. Read = when quorum is contacted.

  Pattern 3: RAFT CONSENSUS:
    - Leader handles all writes (committed = majority ACK).
    - Reads: either from leader directly (linearisable) or with ReadIndex protocol.
    - ReadIndex: leader records current commit index, sends heartbeat to confirm leadership,
      then serves read from state machine at that index → linearisable.

  Pattern 4: COMPARE-AND-SWAP (CAS) for lock-free linearisable operations:
    - Atomic CAS: if current_value == expected → set new_value, return true.
    - Single atomic operation at a single point in time.
    - Used for: distributed locks, leader election, atomic counters.
    - ZooKeeper: compare-and-set on znode version = linearisable CAS.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT linearisability:

- Two processes think they both hold a distributed lock simultaneously
- Leader election results in split-brain: two leaders simultaneously
- Sequence generators produce duplicate IDs (two nodes issued the same ID concurrently)

WITH linearisability:
→ Safe distributed algorithms: only one lock holder, only one leader, unique sequence IDs
→ Simple programming model: code reasons about distributed state as if it were a single machine
→ Composability: if every component is linearisable, the composed system is too

---

### 🧠 Mental Model / Analogy

> A post office with a single authoritative package status database. When a package is marked "delivered," that status immediately and atomically becomes the ground truth for ALL post office branches worldwide. If you call any branch after the "delivered" timestamp, every clerk answers with "delivered" — no branch can say "still in transit" after the delivery was recorded. The single database is the linearisation point. Distributed systems without linearisability: branches have local ledgers that sync overnight — a branch might still say "in transit" hours after delivery was recorded. With linearisability: every branch's answer reflects global reality at the moment you ask.

"Package status database" = the strongly consistent distributed store
"Delivered timestamp = ground truth for all branches" = linearisation point
"Branch still saying in transit after delivery" = stale read (non-linearisable)
"Single authoritative database" = the cost: one bottleneck, single point of coordination

---

### ⚙️ How It Works (Mechanism)

**Raft's ReadIndex protocol for linearisable reads:**

```
RAFT READINDEX PROTOCOL (prevents stale reads from leader):

Problem: A Raft leader might be a "stale leader" — network partition isolated it,
         and a new leader was elected elsewhere. Stale leader has older state.

Without ReadIndex: stale leader serves reads → returns stale data → non-linearisable.

ReadIndex protocol:
  1. Client sends read request to leader.
  2. Leader records current commit index (e.g., 500) as readIndex.
  3. Leader sends heartbeat to ALL followers.
  4. If majority ACK heartbeat → leader is confirmed as current leader.
     (If stale leader: majority won't respond — new leader is elsewhere.)
  5. Leader waits until its state machine has applied all entries up to readIndex.
  6. Leader serves read from state machine at readIndex → linearisable.

Lease-based reads (optimisation):
  1. After winning election, leader holds "lease" for duration = election timeout.
  2. During lease period: no new election can succeed (no other leader possible).
  3. Leader can serve reads without heartbeat during lease.
  4. More efficient: no heartbeat round-trip per read.
  5. Risk: if clock skews > election timeout, lease may expire without leader knowing.
```

---

### 🔄 How It Connects (Mini-Map)

```
Consistency Models (full spectrum)
        │
        ▼
Strong Consistency (practical term)
        │
        ▼
Linearisability ◄──── (you are here)
(formal correctness condition)
        │
        ├── Raft / Paxos (consensus protocols achieving linearisability)
        ├── ZooKeeper / etcd (linearisable key-value stores)
        └── Distributed Locks (correct only with linearisable backing store)
```

---

### 💻 Code Example

**Testing linearisability violation: concurrent reads after write:**

```java
// Demonstrating what a linearisability violation looks like in practice:
// (This is NOT correct code — it illustrates what a buggy system might do)

@Test
public void testLinearisability() throws InterruptedException {
    AtomicReference<Integer> valueFromNode1 = new AtomicReference<>();
    AtomicReference<Integer> valueFromNode2 = new AtomicReference<>();

    // WRITE to a distributed system (simulated):
    distributedStore.write("x", 10);  // write completes — returns success

    // BOTH reads happen AFTER the write completes:
    CountDownLatch latch = new CountDownLatch(2);

    Thread t1 = new Thread(() -> {
        valueFromNode1.set(distributedStore.readFromNode("x", "node-1"));
        latch.countDown();
    });

    Thread t2 = new Thread(() -> {
        valueFromNode2.set(distributedStore.readFromNode("x", "node-2"));
        latch.countDown();
    });

    t1.start();
    t2.start();
    latch.await();

    // LINEARISABILITY ASSERTION:
    // Both reads happen after the write completes.
    // Therefore BOTH must return 10 (the written value).
    // If either returns the old value (stale read) → LINEARISABILITY VIOLATION.

    assertThat(valueFromNode1.get())
        .as("Node 1 must see written value after write completes")
        .isEqualTo(10);

    assertThat(valueFromNode2.get())
        .as("Node 2 must see written value after write completes — linearisability check")
        .isEqualTo(10);

    // A non-linearisable system (e.g., async replica):
    // node-2 might return 5 (old value) if it's a stale replica.
    // This test would FAIL on such a system → linearisability violation detected.
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Linearisability and serialisability are the same         | Linearisability applies to SINGLE OPERATIONS and imposes real-time ordering. Serialisability (ACID) applies to TRANSACTIONS (multi-operation units) and only requires operations to appear in SOME serial order — not necessarily real-time order. A system can be serialisable without being linearisable (stale replica reads, sequential consistency). Strict serialisability = linearisable + serialisable — the strongest guarantee |
| Linearisability requires a single master database        | Linearisability can be achieved without a single master. Quorum protocols (W+R>N) achieve linearisability across multiple nodes. Raft with multiple followers is linearisable — there is a single leader but other nodes participate in consensus. The key is that ALL writes must be committed to a majority before being ACKed, and ALL reads must contact a quorum                                                                    |
| If a system says "strongly consistent" it's linearisable | "Strong consistency" is an informal term. Different systems define it differently. DynamoDB's "strongly consistent reads" provide linearisable reads for individual items but NOT across transactions. PostgreSQL with synchronous_commit=on is linearisable for single writes but NOT if you read from a replica. Always check what operations the system guarantees are linearisable                                                   |
| Linearisability means the system is always correct       | Linearisability is about the ordering of observable reads and writes. It does not guarantee absence of bugs, correct business logic, or atomicity across multiple objects. If you need atomicity across multiple keys (e.g., transfer money from account A to account B), you need transactions + linearisability — not just linearisability alone                                                                                       |

---

### 🔥 Pitfalls in Production

**Split-brain: two leaders both believe they are linearisable:**

```
PROBLEM: Network partition + Raft implementation bug → two leaders elected simultaneously.
         Both serve writes. State diverges. After partition heals: data loss during reconciliation.

  5-node Raft cluster: N1 (leader), N2, N3, N4, N5.
  Network partition splits cluster: {N1, N2} and {N3, N4, N5}.

  Correct behavior:
    {N1, N2}: minority (2 of 5) → cannot form quorum → N1 STEPS DOWN.
    {N3, N4, N5}: majority (3 of 5) → elects N3 as new leader.

  Bug scenario (incorrect Raft implementation / misconfigured cluster):
    N1 does not receive partition signal correctly.
    N1 continues accepting writes (believes it's still leader).
    N3 also elected as leader and accepts writes.

  Result: N1 accepts writes A, B, C. N3 accepts writes X, Y, Z.
          Both clusters respond "success" to clients.
          After partition heals: conflict. Raft MUST discard shorter log.
          If N1's log wins: X, Y, Z lost. If N3's log wins: A, B, C lost.
          Either way: "successful" writes were silently lost → LINEARISABILITY VIOLATION.

BAD: Custom Raft implementation without proper pre-vote protocol:
  // Before starting election: check if quorum is reachable:
  // WITHOUT pre-vote: a node with stale log might win election via split vote
  // PRE-VOTE PROTOCOL prevents this:
  //   Node asks majority: "Would you vote for me if I started an election?"
  //   Only starts election if majority says yes.
  //   This prevents stale leaders from winning unexpected elections.

FIX: Use battle-tested Raft implementations (etcd, CockroachDB) which implement:
  1. Pre-vote protocol (prevents stale leader elections)
  2. Leader leases (prevents two concurrent leaders via time-bounded guarantees)
  3. Linearisable reads via ReadIndex (prevents stale reads from leader)
  4. Epoch-based fencing: each term has an epoch; old leader commands rejected by higher-epoch followers.

  NEVER implement Raft from scratch for production. Use etcd's raft library or CockroachDB's.
```

---

### 🔗 Related Keywords

- `Strong Consistency` — linearisability applied in practice (the operational term)
- `Raft` — consensus protocol achieving linearisability via replicated log
- `Distributed Locks` — REQUIRE linearisable backing store (ZooKeeper, etcd)
- `Serializability` — transactions; related but different from linearisability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Every op appears atomic at one instant;   │
│              │ real-time order globally respected        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Distributed locks; leader election;       │
│              │ unique ID generation; config consensus    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-throughput analytics; feeds; any     │
│              │ data where brief staleness is acceptable  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Post office: after 'delivered' is logged,│
│              │  EVERY branch worldwide says 'delivered'."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Raft → etcd/ZooKeeper → Distributed Locks │
│              │ → Serializability → CAP Theorem           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed counter service uses 3 nodes with quorum writes (W=2) and quorum reads (R=2), N=3. Two clients simultaneously read the counter (value=10), both add 1, and both write back 11 with quorum. Is this counter implementation linearisable? What value does the counter end up with, and why? What additional primitive would you need to make the increment operation linearisable?

**Q2.** Jepsen tests have found linearisability violations in many distributed databases. A database vendor claims: "We use Raft, so we're linearisable." Under what specific conditions can a Raft-based system violate linearisability? Describe at least 3 scenarios where a correctly specified but imperfectly implemented (or misconfigured) Raft system could return stale reads or lose writes.
