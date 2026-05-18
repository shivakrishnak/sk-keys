---
id: DST-048
title: Split-Brain
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-015, DST-016, DST-041, DST-046, DST-047
used_by: []
related: DST-016, DST-027, DST-041, DST-046, DST-047, DST-049
tags:
  - distributed
  - split-brain
  - network-partition
  - consensus
  - data-integrity
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/distributed-systems/split-brain/
---

⚡ TL;DR - Split-brain occurs when a network partition
causes two or more segments of a distributed cluster
to each elect their own leader and accept writes
independently; it violates consistency guarantees
because the same data can be concurrently modified
in both partitions with no way to automatically
reconcile the conflicting versions.

---

### 📋 Entry Metadata

| #048 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, Availability, CAP Theorem, Raft, Leader Election, Fencing Token | |
| **Used by:** | N/A (root cause concept) | |
| **Related:** | CAP Theorem, Quorums, Raft, Leader Election, Fencing Token, Distributed Locking | |

---

### 🔥 The Problem This Solves

**WORLD WITH IT:**
```
CLUSTER: {A, B, C} (A=leader)
Network partition: A separated from B and C

Partition sub-cluster 1: {A}
  A still thinks it is leader (no heartbeats sent fail)
  A accepts writes: X=1 committed

Partition sub-cluster 2: {B, C}
  B and C can't reach A: start election
  B wins (quorum of 2): becomes leader
  B accepts writes: X=2 committed

Network heals:
  A: X=1 (one "committed" value)
  B: X=2 (another "committed" value)
  C: X=2 (followed B)
  PROBLEM: Two different committed values for X.
  Which is correct? No automatic answer.
```

Split-brain is the most dangerous consistency failure
in distributed databases. It happens when both
partitions believe they are authoritative and accept
independent writes. Correctly designed systems
prevent it; incorrectly configured systems experience
it silently with data corruption discovered hours
or days later.

---

### 📘 Textbook Definition

**Split-brain** is a failure mode in distributed
systems where a network partition causes a cluster
to divide into two or more sub-groups, each operating
independently and potentially accepting conflicting
updates to shared data.

The term comes from neurology: a "split-brain patient"
has had the corpus callosum severed, causing the two
hemispheres of the brain to operate independently.
In distributed systems, the network is the corpus
callosum.

**When it occurs:** A split-brain requires both a
network partition AND a failure to enforce quorum.
A correctly configured quorum-based system (like
Raft) prevents split-brain by refusing to elect
a leader in a sub-cluster that lacks a majority.

---

### ⏱️ Understand It in 30 Seconds

```
SAFE (Raft, 5 nodes, partition: {A,B} vs {C,D,E}):
  {A,B}: can't form quorum (2 of 5 = 40%)
    → no leader election → refuse writes
  {C,D,E}: forms quorum (3 of 5 = 60%)
    → elects leader → accepts writes
  Result: One side accepts writes (safe)

UNSAFE (no quorum, 2-node primary-replica):
  {Primary}: thinks it's primary → accepts writes
  {Replica}: thinks primary is down, promotes self
    → accepts writes
  Both sides accept writes → SPLIT-BRAIN

PREVENTION: Quorum-based decisions.
A minority cluster cannot elect a leader.
```

---

### 🔩 First Principles Explanation

**WHY QUORUM PREVENTS SPLIT-BRAIN:**

```
CLUSTER: 5 nodes
QUORUM: 3 (majority of 5)

Network partition: {A,B} | {C,D,E}

Election in {A,B}:
  A sends RequestVote to B.
  A needs 3 votes. Has 2. Cannot reach 3.
  A cannot become leader. {A,B} refuses writes.

Election in {C,D,E}:
  C sends RequestVote to D and E.
  C gets 3 votes (C, D, E). Quorum achieved.
  C becomes leader. {C,D,E} accepts writes.

WHY IT WORKS:
  A minority partition can never form a quorum.
  Only the majority partition can elect a leader.
  At most one partition has a leader at any time.
  (Two majority partitions are mathematically impossible.)
```

**SPLIT-BRAIN SCENARIOS IN PRACTICE:**

```
SCENARIO 1: MySQL with MHA (Master High Availability)
  Network partition: master isolated from replicas.
  MHA: detects master failure, promotes a replica.
  Master: not dead, just isolated - still takes writes.
  Result: two write-accepting nodes.
  Fix: STONITH (Shoot The Other Node In The Head)
    - Active fencing: forcibly power-off the isolated
      node before promoting the new primary.
    - Ensures only ONE node is primary at any time.

SCENARIO 2: Redis Sentinel (2-of-3 sentinel
  misconfiguration)
  Redis: {Primary P, Replica R1, Replica R2}
  Sentinel: {S1 near P, S2 near R1, S3 near R2}
  Network partition: P+S1 isolated from R1+R2+S2+S3
  S2+S3: quorum (2/3) → declare P down → promote R1
  S1: still reports P as up, P still accepts writes
  P and R1 both accept writes → SPLIT-BRAIN
  Fix: require sentinel quorum AND reduce promotion
    threshold below TTL of split detection.

SCENARIO 3: Database without fencing
  PostgreSQL streaming: primary isolated.
  pg_auto_failover or Patroni: promotes standby.
  Primary resumes, believes it is still primary.
  Both accept writes until DBA intervenes.
  Fix: Patroni uses Patroni epoch + DCS (etcd/ZK)
    to fence the old primary (revoke lease).
    Old primary cannot write: checks DCS, finds
    it no longer holds the leader key.
```

**DETECTING SPLIT-BRAIN:**

```
INDICATOR 1: Two nodes both report "I am primary"
  Monitor: check all cluster nodes for primary status
  Alert: if COUNT(nodes reporting primary) > 1

INDICATOR 2: Diverging write counters
  Monitor: compare write sequence numbers across nodes
  Alert: if primary-A and primary-B have different
    sequence numbers for the same position

INDICATOR 3: Data divergence
  Monitor: checksum-based comparison of critical tables
  Alert: if checksums diverge between nodes that
    should be identical (after partition heals)

INDICATOR 4: VIP (Virtual IP) bound to multiple nodes
  Monitor: ARP table for VIP address
  Alert: if VIP resolves to more than one MAC address
    in the same subnet (ARP conflict = split-brain)
```

---

### 🧠 Mental Model / Analogy

> Split-brain is like a company where the CEO's
> communication line goes down. The East Coast office
> can't reach headquarters. They decide to appoint
> their own CEO (the East Coast Regional VP) because
> they haven't heard from the real CEO in hours.
> Now there are two CEOs, both signing contracts,
> both hiring people, both spending budget. When the
> communication line is restored, there are contradictory
> decisions made by both. Which decisions are valid?
> How are the contradictions resolved? This is why
> real companies require that the board (quorum) must
> confirm any CEO appointment - the East Coast VP
> cannot appoint a CEO without board approval from
> a majority.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
When a network partition splits a cluster in two,
and both halves continue accepting writes, thinking
they are "in charge." When the partition heals, there
are conflicting writes with no clear winner.

**Level 2 - How quorum prevents it:**
Quorum-based systems require a majority vote to
elect a leader. A minority partition (less than half)
cannot form a majority, so it cannot elect a leader,
so it refuses writes. Only the majority partition
continues operating. This guarantees at most one
active leader.

**Level 3 - STONITH:**
Some high-availability systems prevent split-brain
through active node killing: if a node might be a
stale primary, kill it before promoting the new one.
"Shoot The Other Node In The Head" - use out-of-band
power management (IPMI, BMC) or cloud instance stop
APIs to terminate the potentially-split node. Extreme
but reliable.

**Level 4 - PostgreSQL Patroni:**
Patroni uses a Distributed Configuration Store (etcd,
ZooKeeper, or Consul) as the source of truth for
leadership. The primary holds a lease key. On suspected
failure: new candidate checks the DCS; if old primary's
lease has expired, acquires the key and promotes itself.
Old primary: on every write, it also checks DCS (reads
its own lease); if lease lost, refuses further writes
and gracefully demotes itself.

**Level 5 - Split-brain in Kubernetes:**
etcd (Raft-based) prevents split-brain at the API
server level. However, Kubernetes nodes themselves
can experience split-brain: if the kubelet on a node
loses connection to the control plane, it continues
running pods (correct behavior) but also triggers
node failure eviction of its own pods from the
scheduler's perspective. This can cause the same pod
to run on two nodes simultaneously (the "duplicate
pod" problem). StatefulSets are most vulnerable:
a stateful pod running twice means its storage may
be written by two instances. Kubernetes's mitigation:
PodDisruptionBudgets and StatefulSet ordinal ordering,
but these reduce probability, not impossibility.

---

### 💻 Code Example

**Detecting and Preventing Split-Brain**

```python
# BAD: Primary promotion without quorum check
# (split-brain possible)

class BadFailoverManager:
    def __init__(self, primary_host: str, replica_host: str):
        self.primary = primary_host
        self.replica = replica_host

    def check_and_failover(self) -> None:
        if not self._is_reachable(self.primary):
            # BUG: No quorum check. No fencing.
            # Just promote replica and hope for the best.
            self._promote_replica()

    def _promote_replica(self) -> None:
        # What if primary is NOT dead, just partitioned?
        # PRIMARY IS STILL RUNNING - NOW TWO PRIMARIES.
        execute_on(
            self.replica,
            "SELECT pg_promote();"
        )
```

```python
# GOOD: Failover with quorum check and fencing
# (using DCS like etcd as arbitrator)

import etcd3
import time

class SafeFailoverManager:
    def __init__(
        self,
        etcd_client,
        primary_host: str,
        replica_host: str,
        leader_key: str = "/db/leader",
        lease_ttl: int = 30
    ):
        self.etcd = etcd_client
        self.primary = primary_host
        self.replica = replica_host
        self.leader_key = leader_key
        self.ttl = lease_ttl

    def attempt_failover(self) -> bool:
        """
        Safely promote replica only after:
        1. Primary lease has expired in DCS (not just unreachable)
        2. This failover manager acquires the leader lease
        """
        # STEP 1: Wait for primary's lease to expire in DCS
        # (not just wait for TCP timeout - DCS is the authority)
        current_leader, _ = self.etcd.get(self.leader_key)
        if current_leader is not None:
            print(
                "Primary still holds DCS lease: "
                "not yet expired. Waiting."
            )
            return False  # Not safe yet

        # STEP 2: Acquire the leader lease atomically
        # (fencing: ensures we are THE designated new primary)
        new_lease = self.etcd.lease(self.ttl)
        success, _ = self.etcd.transaction(
            compare=[
                self.etcd.transactions.version(
                    self.leader_key
                ) == 0  # Key must not exist
            ],
            success=[
                self.etcd.transactions.put(
                    self.leader_key,
                    self.replica,
                    lease=new_lease
                )
            ],
            failure=[]
        )

        if not success:
            print("Another failover manager won the race.")
            return False

        # STEP 3: Now safe to promote (old primary's lease gone,
        # we hold the new lease)
        self._promote_replica()
        self._start_lease_renewal(new_lease)
        print(f"Promoted {self.replica} as new primary.")
        return True

    def _promote_replica(self) -> None:
        execute_on(self.replica, "SELECT pg_promote();")

    def _start_lease_renewal(self, lease) -> None:
        import threading
        def renew():
            while True:
                time.sleep(self.ttl // 3)
                lease.refresh()
        threading.Thread(target=renew, daemon=True).start()
```

---

### ⚖️ Comparison Table

| System | Split-Brain Prevention | Mechanism |
|---|---|---|
| **PostgreSQL + Patroni** | Yes | etcd/ZK lease + DCS check on every write |
| **MySQL + MHA** | Partial (without STONITH) | STONITH: kill old primary before promoting |
| **Redis Sentinel** | Yes (with correct quorum config) | Sentinel quorum: majority must agree on failover |
| **Kafka + ZooKeeper** | Yes | ZK leader election + epoch-based fencing |
| **etcd/Raft** | Yes (by design) | Quorum election: minority cannot elect leader |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Split-brain only happens when nodes crash" | Split-brain occurs on NETWORK PARTITIONS even when all nodes are healthy. A healthy isolated node is more dangerous than a crashed one: it actively accepts writes. A crashed node does nothing. |
| "Raft completely solves split-brain" | Raft prevents a minority partition from electing a leader. But a majority partition that experiences a partition within itself (due to misconfiguration or bugs) can still have issues. The Raft algorithm is correct; incorrect implementations can have bugs. |
| "Shorter heartbeat intervals prevent split-brain" | Shorter heartbeats detect failures faster but do not prevent split-brain. Split-brain requires that BOTH partitions believe they are the majority. The quorum check is what prevents it, not heartbeat frequency. |
| "Split-brain is always detected immediately" | Split-brain can persist for minutes or hours before data divergence is noticed. Monitoring must actively check that exactly one node claims to be the primary, not just that the primary is reachable. |

---

### 🚨 Failure Modes & Diagnosis

**PostgreSQL Split-Brain After Network Partition**

**Symptom:** Application writes succeed but data
seems inconsistent. Some writes appear, others don't.
pg_replication_slots shows unusual lag. Two connection
strings both report `SELECT pg_is_in_recovery() = false`.

**Diagnosis:**
```sql
-- Check BOTH nodes: if both report false, split-brain
-- On node1:
SELECT pg_is_in_recovery(), inet_server_addr();
-- false, 10.0.0.1

-- On node2:
SELECT pg_is_in_recovery(), inet_server_addr();
-- false, 10.0.0.2
-- BOTH PRIMARY: SPLIT-BRAIN CONFIRMED

-- Check transaction IDs to find divergence:
-- On node1:
SELECT pg_current_wal_lsn(), now();

-- On node2:
SELECT pg_current_wal_lsn(), now();
-- Compare LSNs: if different, both have accepted writes
```

**Immediate action:**
1. **STOP all writes immediately** to both nodes.
2. Determine which node has "canonical" data
   (typically: the node that received more authoritative
   writes, or the node that Patroni/DCS recognizes).
3. Point-in-time recovery (PITR): restore the losing
   node from the winning node, applying only the
   transactions that happened after the partition.
4. Post-mortem: audit what data was lost or corrupted.

---

### 🔗 Related Keywords

**Prerequisites:** `CAP Theorem` (DST-016),
`Raft Consensus Algorithm` (DST-041),
`Leader Election` (DST-046), `Fencing Token` (DST-047)

**Used to understand:** Patroni, MySQL MHA, DRBD,
Redis Sentinel, distributed database failover

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT       │ Two+ partitions each believe they're leader│
│ CAUSE      │ Network partition + missing quorum check   │
│ RESULT     │ Conflicting writes; data corruption       │
├────────────┼────────────────────────────────────────────┤
│ PREVENTION │ Quorum: minority cannot elect leader       │
│            │ STONITH: kill old primary before promoting │
│            │ DCS lease: primary checks DCS on writes   │
│            │ Fencing token: storage rejects stale writes│
├────────────┼────────────────────────────────────────────┤
│ DETECT     │ Check: how many nodes report as primary?  │
│            │ Alert if count > 1                        │
├────────────┼────────────────────────────────────────────┤
│ RECOVERY   │ Stop writes on BOTH nodes → compare LSN  │
│            │ Restore loser from winner + PITR          │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "A healthy isolated node is more dangerous │
│            │  than a crashed one: it silently writes." │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Split-brain is the cautionary tale of "just do
something" in distributed systems. A failover system
that promotes a replica when it can't reach the primary
feels safe: if the primary is down, someone should
take over. But "can't reach" is not the same as "is
down." The replica's inability to reach the primary
might be the replica's problem, not the primary's.
This is the distributed systems duality: every failure
detector can make both false positives (declare alive
as dead) and false negatives (declare dead as alive).
The only safe response to "I can't reach the other node"
is to check with a third party (DCS, quorum) rather
than act unilaterally. Systems that act unilaterally
on one-sided failure detection are vulnerable to
split-brain.

---

### 💡 The Surprising Truth

The "split-brain" problem famously caused a 14-hour
AWS outage in 2011 (EBS outage in US-EAST-1). The
EBS storage cluster used a primary/secondary
replication model for individual EBS volumes. A
network event caused some volume segments to partition.
Both sides of the partition believed they were the
primary. Both accepted writes. When the network
healed, the reconciliation logic couldn't handle
the scale of diverged state - essentially two versions
of thousands of volumes existed simultaneously. The
reconciliation logic itself caused a feedback loop
of re-mirroring requests that overloaded the network.
The fix required quarantining the diverged volumes
and manually reconciling. The lesson: at large scale,
split-brain recovery is often harder than prevention.
Design for prevention, not recovery.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Why quorum-based systems (Raft) cannot
   experience split-brain in a two-partition scenario
   (derive the mathematical argument).
2. [IDENTIFY] Name the three infrastructure-level
   mechanisms that prevent split-brain (quorum,
   fencing, STONITH) and explain what each prevents.
3. [DIAGNOSE] Given a PostgreSQL cluster where both
   nodes report `pg_is_in_recovery() = false`, write
   the SQL to confirm split-brain and identify which
   node has more recent writes.
4. [DESIGN] For a 5-node cluster, describe the
   minimum quorum size and the maximum number of
   concurrent node failures that can be safely tolerated.
5. [EXPLAIN] Why "I can't reach the primary" is an
   insufficient reason to promote a replica, and
   what additional check is required.
