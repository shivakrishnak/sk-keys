---
id: DST-085
title: CAP Theorem Formalization - Gilbert and Lynch 2002
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-001, DST-084
used_by: DST-086
related: DST-001, DST-079, DST-084, DST-086
tags:
  - distributed
  - cap-theorem
  - gilbert-lynch
  - consistency
  - availability
  - partition-tolerance
  - foundational-paper
  - formal-proof
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 85
permalink: /technical-mastery/distributed-systems/cap-formalization/
---

⚡ TL;DR - Brewer's CAP conjecture (2000) stated
informally that a distributed system cannot have
all three of: Consistency, Availability, and Partition
Tolerance; Gilbert and Lynch (2002) formalized and
proved this: their formal definitions are (C) atomic
consistency for all read/write operations, (A)
every request receives a response from a non-failing
node, (P) the network can drop any message; the
proof is short (~5 pages) and shows that during a
partition, any algorithm must either return an
error (sacrificing A) or risk returning stale data
(sacrificing C); this entry explains the formal
definitions, the proof structure, and why Brewer
himself later said the "2 of 3" framing is misleading.

---

### 📋 Entry Metadata

| #085 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAP Theorem intro (DST-001), FLP Impossibility (DST-084) | |
| **Used by:** | Consistency-Availability Spectrum (DST-086) | |
| **Related:** | CAP intro, FLP, CAP Trade-off Navigation (DST-079), Spectrum (DST-086) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT FORMALIZATION:**
Brewer's CAP conjecture (2000) was stated as an
informal observation. Engineers used it as a design
heuristic: "pick 2 of 3." But informal statements
invite misinterpretation. What exactly is "consistency"?
Is it linearizability? Sequential consistency? Read-
your-writes? What exactly is "availability"? Is a
slow response available? What exactly counts as a
partition?

Without formal definitions, the theorem could be
applied to any situation to justify any design.
"We chose eventual consistency because of CAP" -
but does CAP actually require eventual consistency?
Or does it only require sacrificing C during actual
partitions?

Gilbert and Lynch's 2002 formalization answers these
questions with mathematical precision.

---

### 📘 Textbook Definition

**CAP Theorem (Gilbert and Lynch, 2002 formal version):**
It is impossible for any distributed data store to
simultaneously guarantee the following three properties:

**Formal definitions:**

**Consistency (C):** equivalent to **atomic consistency**
(linearizability). In any execution, there must exist
a total order on all read and write operations that
is consistent with real-time ordering and such that
each read returns the value of the most recent write
in that total order.

**Availability (A):** every request received by a
non-failing node must result in a response. The
response must be non-error and contain data (not
just an acknowledgment). A service that returns
"503 Service Unavailable" does NOT satisfy A.

**Partition Tolerance (P):** the system continues
to operate correctly even if an arbitrary number
of messages between nodes are lost (but not delayed
indefinitely). A network partition = a subset of
nodes cannot communicate with another subset.

**The proof:** shows that during a network partition,
any algorithm that satisfies A must sacrifice C,
and any algorithm that satisfies C must sacrifice A.

---

### ⏱️ Understand It in 30 Seconds

```
THE FORMAL PROOF (sketch):

SETUP:
  Two nodes: N1 and N2.
  A partition: N1 and N2 cannot communicate.
  One value v, initially v0.
  
SCENARIO:
  A client writes v1 to N1.
  Another client reads from N2.
  
PARTITION MEANS:
  N1 cannot send the write (v1) to N2.
  N2 has no knowledge of v1.

CASE 1 (choose A over C):
  N2 must respond (Availability).
  N2 responds with v0 (its last known value).
  The first client writes v1 on N1.
  N2 has v0.
  Both clients "succeeded" but N2 has stale data.
  → CONSISTENCY VIOLATED.

CASE 2 (choose C over A):
  N2 must return current value.
  N2 cannot know current value (no communication with N1).
  N2 must return error or block.
  → AVAILABILITY VIOLATED (returns error, not data).

CASE 3 (choose C and A, sacrifice P):
  Only possible if we ASSUME no partition occurs.
  In a single-node system: C + A trivially.
  In a distributed system: partitions DO occur.
  → You CANNOT drop P in a real distributed system.

CONCLUSION:
  A + C requires no partition (impossible guarantee).
  P is mandatory → choose C or A during partitions.
```

---

### 🔩 First Principles Explanation

**THE FORMAL MODEL:**

```
ATOMIC CONSISTENCY (linearizability) in detail:
  Operation definitions:
    write(v): a client writes value v.
    read()  : a client reads the current value.
  
  Atomic consistency requires:
    Given a set of operations o1, o2, ..., on:
    There EXISTS a total order (sequential history)
    compatible with:
      1. Real-time constraint: if o1 completes before
         o2 begins (in wall-clock time), o1 precedes
         o2 in the total order.
      2. Correctness: each read returns the value
         written by the most recent preceding write
         in the total order.
  
  Intuition: all operations appear to execute
  instantaneously at some point during their
  actual duration (the "linearization point").
  
AVAILABILITY in detail:
  Every request received by a HEALTHY node must
  receive a response.
  
  Strict: a response must arrive within finite time.
  (The 2002 paper requires "eventually respond" -
  it does not give a bound. This is weak availability.
  Practical systems require bounded availability.)
  
  NOT: every request receives a CORRECT response.
  Availability is about liveness, not correctness.
  
PARTITION TOLERANCE in detail:
  The network is modeled as: can deliver or drop
  any message at any time.
  
  This is NOT: messages are delayed.
  This IS: messages are permanently lost.
  
  The proof uses this model to show that
  N1 and N2 can be arbitrarily isolated.
```

**THE PROOF (formal structure):**

```
Theorem: No algorithm A can provide atomic
consistency (C), availability (A), and partition
tolerance (P) simultaneously.

Proof by contradiction:
  Assume algorithm A satisfies C, A, and P.
  
  Setup:
    System: nodes G1 (contains N1) and G2 (contains N2).
    Partition: all messages between G1 and G2 are dropped.
    Initial state: v0 stored on all nodes.
  
  Step 1:
    Client C1 sends write(v1) to N1 (in G1).
    Since A is satisfied: N1 must respond successfully.
    (N1 cannot communicate with G2 due to partition.
    But N1 must still respond.)
    Result: write(v1) succeeds at N1.
    N2 still has v0 (partition blocks propagation).
  
  Step 2:
    Client C2 sends read() to N2 (in G2).
    Since A is satisfied: N2 must respond.
    N2 has v0 (cannot reach N1 for the latest write).
    
    Case A: N2 returns v0.
      This violates C: C claims reads see the most
      recent write. C1 wrote v1. C2 reads v0.
      The linearization point of read() must come
      after write(v1) (if C1's write completed, which it
        did).
      But read() returns the old value. CONTRADICTION with
        C.
    
    Case B: N2 returns v1.
      N2 cannot have v1 (partition blocks N1→N2).
      N2 cannot fabricate v1 (validity: decided values
      must be proposed values).
      This is impossible.
    
    Case C: N2 blocks (waits for N1).
      This violates A: N2 must respond to non-failing node.
      CONTRADICTION with A.
    
    Case D: N2 returns error.
      This violates A: A requires non-error response.
      CONTRADICTION with A.
    
  In all cases: A assumed but violated, or C assumed but
    violated.
  CONTRADICTION. Algorithm A satisfying all three does not
    exist.
  QED.
```

**BREWER'S RETROACTIVE CLARIFICATION (2012):**

```
In "CAP Twelve Years Later: How the Rules Have Changed"
(2012), Brewer noted the "2 of 3" framing is misleading.

CORRECTIONS:
  1. CAP only applies DURING a network partition.
     "Choosing between C and A" is only meaningful when
     P occurs. Outside of partitions: both C and A
     are achievable simultaneously.
  
  2. C and A are not binary.
     C is a spectrum: linearizability → sequential →
       causal → eventual.
     A is a spectrum: 100% response rate → 99.99%
       → 99% → "sometimes responds."
     You can have PARTIAL consistency and HIGH
       availability.
  
  3. "CA systems" don't exist in practice.
     Claiming a distributed system is "CA" means:
     it assumes no partitions will ever occur.
     In practice: partitions DO occur (hardware failure,
     network congestion, software bugs, maintenance).
     "CA" is only valid for single-node systems.
  
  4. Modern systems tune the trade-off.
     Cassandra: AP by default, tunable toward CP.
     DynamoDB: AP by default, CP for strong reads.
     MongoDB: CP by default (with majority write concern).
     Spanner: CP by TrueTime design.
     
  PRACTICAL REFRAMING:
    "When a partition occurs, I choose to:
     (a) Maintain consistency: refuse writes until healed.
     (b) Maintain availability: accept writes, resolve
       later."
    This is the actual design decision. Not "2 of 3" at
      build time.
```

**FLP VS CAP:**

```
COMMON CONFUSION: are FLP and CAP the same?

NO. They are different:

FLP (1985):
  Problem: CONSENSUS (all nodes agree on a value).
  Model: fully asynchronous (unbounded message delays).
  Sacrifice: liveness (termination). Safety is preserved.
  Escape: partial synchrony, randomization.

CAP (2002):
  Problem: READ/WRITE operations on a shared register.
  Model: partitioned network (messages can be dropped).
  Sacrifice: C (stale reads) or A (errors on partition).
  Escape: no escape; you must choose during partitions.

RELATIONSHIP:
  Both prove limits on distributed systems.
  FLP shows: you cannot guarantee consensus terminates.
  CAP shows: you cannot have both C and A during
    partitions.
  
  A consensus algorithm (Paxos, Raft) is CP:
    During partition: refuses requests (sacrifices A).
    Therefore satisfies C but not A.
    This is consistent with CAP: they chose C over A.
```

---

### 🧠 Mental Model / Analogy

> The CAP proof is like two bank branches during
> a communication blackout (partition). Branch A
> gets a deposit of $100 (write v1). Branch B
> gets a withdrawal request (read). If Branch B
> is available (A): it must respond without knowing
> about Branch A's deposit. It reports the old
> balance (violating C: stale read). If Branch B
> wants consistency (C): it must refuse the withdrawal
> until communication with Branch A is restored
> (violating A: returns error). The bank cannot
> simultaneously tell Branch B "respond immediately"
> (A) and "always have the latest balance" (C)
> when Branch A cannot be reached.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The informal version:**
Pick at most 2 of: C (everyone sees the same data),
A (everyone gets a response), P (survives network splits).

**Level 2 - The formal definition:**
C = linearizability. A = every non-failing node responds.
P = any messages can be dropped.

**Level 3 - The proof structure:**
Two nodes, one partition, one write, one read.
To satisfy A: N2 must respond. To satisfy C:
N2 must have the latest write. During a partition:
N2 cannot have it. Pick one.

**Level 4 - The nuance:**
CAP only applies DURING partitions. Between partitions
(normal operation): C and A can coexist. The "2 of 3"
framing misleads; the real choice is: during partitions,
do I sacrifice C or A?

**Level 5 - The spectrum beyond CAP:**
C and A are spectrums, not binaries. PACELC (DST-079)
models this: even without partitions, C costs latency.
The formal proof is important as a lower bound; the
practical model is PACELC and tunable consistency.

---

### 💻 Code Example

*See the proof-by-contradiction structured argument
in First Principles, and the FLP vs CAP comparison.*

---

### ⚖️ Comparison Table

| Property | Formal Definition | Example: Satisfies | Example: Violates |
|---|---|---|---|
| **Consistency (C)** | Linearizability | Single-node DB (always) | Cassandra with ONE consistency |
| **Availability (A)** | Non-failing node always responds | Cassandra (eventually) | Paxos during no-quorum |
| **Partition Tolerance (P)** | Continues despite message drops | Any distributed system | Single-node only |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "CAP means you must always sacrifice one property" | CAP means during a PARTITION you must sacrifice C or A. Without partitions: you can have both. Most systems are not partitioned most of the time. |
| "CA systems exist" | A "CA" distributed system assumes no partitions. In any distributed system over a real network, partitions will occur. "CA" is therefore only valid for single-node systems. |
| "C in CAP = eventual consistency" | C in CAP is specifically linearizability (atomic consistency). Eventual consistency is on the OPPOSITE end of the consistency spectrum from C in CAP. Conflating them causes serious design errors. |
| "Choosing AP means the system is eventually consistent" | AP means: during a partition, you choose to remain available and sacrifice linearizability. The consistency level you get from "A" depends on your replication and merge strategy. You could have causal consistency or read-your-writes consistency while still being "AP" under CAP. |

---

### 🚨 Failure Modes & Diagnosis

**Misapplying CAP: Calling a System "CA"**

**Symptom:** An architecture document describes a
MySQL primary with synchronous replicas as "CA"
(consistent and available). A network partition
occurs between the primary and replica. The system
enters a split-brain state. Both sides accept writes.

**Root Cause:** Calling MySQL "CA" was wrong. MySQL
is CP (primary/replica with synchronous replication
is CP: during partition, the replica waits for the
primary and blocks). However, if the configuration
was wrong (replica allowed writes independently),
the partition produced split-brain.

**Correct Classification:**
```
MySQL primary/replica:
  WITH synchronous replication:
    CP: replica blocks on partition.
    No split-brain. Data loss possible if primary
    fails before replication.
  
  WITH asynchronous replication:
    EFFECTIVELY AP: replica accepts reads (may be stale).
    Writes still go to primary. On primary failure:
    promote replica → possible data loss (replication lag).
  
  WITH dual-primary (wrong config):
    NEITHER C NOR A: split-brain possible.
    Both primaries accept writes.
    After partition heals: conflict.
    This violates C (inconsistency) and creates
    data corruption (not AP in the sense of CAP).

PREVENTION:
  Use GROUP REPLICATION or Orchestrator to enforce
  that only one primary is active.
  Or: use ProxySQL with write failover to enforce
  single primary at the proxy level.
```

---

### 🔗 Related Keywords

**Foundations:** `CAP Theorem intro` (DST-001),
`FLP Impossibility` (DST-084)

**Built upon:** `Consistency-Availability Spectrum` (DST-086)

**Navigation:** `CAP Trade-off in Practice` (DST-079)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CAP FORMAL DEFINITIONS                                  │
│ C = linearizability (reads see latest write)           │
│ A = non-failing nodes always respond                   │
│ P = any messages can be dropped                        │
├─────────────────────────────────────────────────────────┤
│ PROOF STRUCTURE                                         │
│ 2 nodes. Partition → N1 write, N2 read.               │
│ N2 cannot know latest value → C or A violated.        │
├─────────────────────────────────────────────────────────┤
│ NUANCE: CAP applies only DURING partitions             │
│ "2 of 3" framing is misleading (Brewer 2012)          │
│ C and A are spectrums, not binaries                   │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The formalization of CAP teaches that informal
conjectures become much more powerful when given
precise mathematical definitions. Brewer's informal
"pick 2 of 3" (2000) was correct in spirit but
ambiguous. Gilbert and Lynch's formal definitions
(2002) made the claim precise enough to prove
and to challenge. The formal proof also revealed
the nuance: CAP ONLY applies during partitions.
The informal version suggested a permanent three-
way trade-off; the formal version shows a conditional
two-way trade-off. This pattern - formalization
reveals nuance - is common in computer science.
The lesson for engineers: when working with informal
design principles, try to state them formally
enough that the conditions and exceptions become
visible.

---

### 💡 The Surprising Truth

Brewer's CAP conjecture (PODC 2000) was not a paper;
it was a conference keynote slide. He presented 3
properties informally, called it a conjecture, and
moved on. Gilbert and Lynch read the keynote abstract,
formalized the definitions, wrote a proof, and
published it in 2002 at ACM SIGACT News. The
"theorem" is therefore the work of Gilbert and Lynch,
not Brewer, despite often being called "Brewer's CAP
theorem." Brewer graciously acknowledged their proof
and said it "was stronger and more general than what
I had in mind." The conjecture → formalization →
proof path took 2 years and resulted in one of the
most-cited papers in distributed systems. The lesson:
informal intuitions from practitioners, when
formalized by theoreticians, often produce more
precise and more surprising results than the
original intuition contained.

---

### ✅ Mastery Checklist

1. [FORMAL] State the formal definitions of C, A,
   and P from Gilbert and Lynch 2002. In particular:
   what specific consistency model does C represent?
   (Not "consistent" but the specific formal name.)
2. [TRACE] Walk through the CAP proof sketch: two
   nodes, partition, write to N1, read from N2.
   For each of the 4 possible actions by N2 (return
   v0, return v1, block, return error), identify
   which property is violated.
3. [DISTINGUISH] Compare the proof structure of
   FLP (DST-084) and CAP (this entry). Both prove
   limits on distributed systems. What problem
   does each address? What model does each use?
   What property does each sacrifice?
4. [EVALUATE] A database vendor claims their system
   is "CA" (consistent AND available). Under what
   conditions is this claim valid? Under what
   conditions is it impossible?
5. [CONNECT] Brewer's 2012 note says C and A are
   spectrums. Give a concrete example of a system
   that is: (a) fully C and partially A, (b) fully
   A and partially C, and (c) somewhere in the
   middle of both spectrums.
