---
id: DST-042
title: Paxos
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-027, DST-041
used_by: DST-046
related: DST-027, DST-029, DST-041, DST-046
tags:
  - distributed
  - consensus
  - paxos
  - agreement
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/distributed-systems/paxos/
---

⚡ TL;DR - Paxos is the foundational distributed consensus
algorithm that proves consensus is possible in an
asynchronous network with fail-stop (not Byzantine)
failures; it uses a two-phase protocol (Prepare/Promise
then Accept/Accepted) where a proposer wins if a
quorum of acceptors acknowledge each phase; understanding
Paxos is prerequisite to understanding why all practical
consensus algorithms (Raft, Zab, Viewstamped Replication)
look the way they do.

---

### 📋 Entry Metadata

| #042 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, Quorums, Raft | |
| **Used by:** | Leader Election, Google Chubby, Zookeeper | |
| **Related:** | Quorums, Linearizability, Raft, Leader Election | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Multiple nodes must agree on a single value (which node
is the leader, which transaction committed, which
configuration is active). If two nodes simultaneously
propose different values and both get accepted by
different subsets of nodes, you have no consistent
agreed value. Any subsequent decision based on this
value is potentially wrong. Paxos provides the first
formal proof that nodes CAN agree on a single value
in a network where messages may be delayed, reordered,
or lost - as long as nodes don't behave maliciously.

---

### 📘 Textbook Definition

**Paxos** is a consensus algorithm published by Leslie
Lamport in 1989 (circulated as a tech report) and
formally published in 2001. It solves the problem of
choosing a single value among multiple proposals in
a distributed system that may experience:
- Message loss
- Message delay
- Node failures (fail-stop, not Byzantine)

**Roles:**
- **Proposer:** Initiates the consensus process with
  a proposed value
- **Acceptor:** Votes on proposals; maintains state
  across phases
- **Learner:** Learns the decided value (read-only)

A single node can play multiple roles.

---

### ⏱️ Understand It in 30 Seconds

```
SINGLE PAXOS (choosing ONE value):

Phase 1a - PREPARE:
  Proposer sends Prepare(n) to all acceptors.
  n = proposal number (must be unique, increasing)

Phase 1b - PROMISE:
  Acceptor: if n > highest_seen_n:
    promise to reject proposals with n' < n
    reply with highest accepted (n, value) if any
  If quorum of acceptors promise:
    proposer moves to Phase 2

Phase 2a - ACCEPT:
  Proposer sends Accept(n, v) to all acceptors.
  v = highest_accepted_value from Phase 1b responses
    (if any), else proposer's own value

Phase 2b - ACCEPTED:
  Acceptor: if n >= highest_promised_n:
    accept the value, record (n, v)
    reply Accepted(n, v)

COMMIT:
  If quorum of acceptors send Accepted:
    value v is decided. Proposer notifies learners.
```

---

### 🔩 First Principles Explanation

**WHY TWO PHASES?**

Phase 1 (Prepare/Promise) serves two purposes:
1. Establishes that no prior rounds have already
   committed a value (or discovers what was committed)
2. Blocks other proposers with lower proposal numbers
   from interfering

Without Phase 1: two proposers with simultaneous
proposals could each get a quorum to accept different
values, violating the invariant that at most one
value is ever decided.

**THE KEY INVARIANT:**

```
"If a value v has been chosen (quorum accepted it),
 then every future Accept with a higher proposal
 number must propose v."

How enforced:
  Phase 1b: acceptors report the highest-numbered
  proposal they've accepted.
  If any acceptor in the Phase 1b quorum has accepted
  a value: the proposer MUST use that value in Phase 2.
  Otherwise: the proposer may use any value.

Why this works:
  If v was chosen with proposal n:
  At least a quorum of acceptors have (n, v).
  Any future proposer's Phase 1 quorum overlaps this.
  The overlapping acceptor reports (n, v).
  Future proposer must propose v.
  v remains the only possible value to commit.
```

**LIVENESS (THE DUELING PROPOSERS PROBLEM):**

```
Proposer A sends Prepare(1).
Quorum promises.
Proposer B sends Prepare(2) before A sends Accept.
Quorum promises to B (rejects A's n=1).
A sends Accept(1) - rejected.
A sends Prepare(3).
Quorum promises to A (rejects B's n=2).
B sends Accept(2) - rejected.
B sends Prepare(4).
...

This loop can continue indefinitely (liveness failure).
FIX: elect a distinguished proposer (leader).
Only one proposer at a time.
This insight leads directly to Multi-Paxos and Raft.
```

**MULTI-PAXOS:**

Single Paxos chooses one value. Multi-Paxos runs
Paxos for each slot in a log. Optimization: once a
leader is stable, Phase 1 runs once for the leader's
entire tenure. Each new log entry only needs Phase 2.
This is essentially what Raft implements with a
cleaner structure.

---

### 🧠 Mental Model / Analogy

> Paxos is like a vote on a contract amendment in a
> committee. Phase 1 (Prepare): a proposer asks
> members "will you accept my proposal if I make one?
> Tell me if you've already promised someone else."
> The proposer checks: has anyone already voted on
> an amendment? If yes, the proposer must propose that
> same amendment (cannot change what's already been
> committed). Phase 2 (Accept): proposer presents
> the amendment. Members vote. If a majority vote
> yes, the amendment passes. The key: members never
> go back on a promise, and proposers always continue
> an in-progress amendment rather than starting a
> new one. This prevents two different amendments from
> passing simultaneously.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A 2-round protocol to get a cluster of nodes to agree
on a single value. Round 1: proposer checks if anyone
has already committed anything. Round 2: proposer
asks nodes to accept a value. If a majority accept,
the value is committed.

**Level 2 - Why two rounds:**
Round 1 prevents two proposers from committing different
values simultaneously. By asking the cluster first,
a proposer discovers if a value was already committed
and must continue it. Without round 1, two proposers
could simultaneously get disjoint majorities to accept
different values.

**Level 3 - Proposal numbers:**
Each proposal has a unique, monotonically increasing
proposal number. A higher number supersedes a lower
one. This gives a total order to proposals and ensures
stale proposals don't interfere with newer ones. When
a new proposer starts, it must use a number higher
than any it has seen. This is how Paxos handles
concurrent proposers: the higher-numbered one wins.

**Level 4 - Multi-Paxos to Raft:**
Paxos chooses one value. Real systems need to agree
on a sequence of values (a log). Multi-Paxos runs
a separate Paxos instance per log slot. Optimization:
one leader runs Phase 1 for all future slots at once,
and only Phase 2 per entry. This is expensive to
implement correctly (leader changes are tricky).
Raft simplifies this by adding explicit leader
election, structured log, and term-based staleness
detection. Raft is essentially Multi-Paxos with
engineering constraints that make it implementable.

**Level 5 - FLP impossibility:**
The FLP impossibility theorem (Fischer, Lynch, Paterson,
1985) proves that in a purely asynchronous distributed
system, no deterministic consensus algorithm can
guarantee both safety (only one value decided) and
liveness (a value is always eventually decided) in
the presence of even one crash failure. Paxos handles
this by guaranteeing safety always; liveness is only
guaranteed if there is a stable leader (a practical
assumption in most systems). The leader election
itself may not terminate under adversarial scheduling,
but in practice it does.

---

### 💻 Code Example

**Basic Paxos Acceptor State**

```python
# BAD: Acceptor does not check proposal number
# (allows stale proposals to overwrite fresh ones)

class BadAcceptor:
    def __init__(self):
        self.accepted_value = None

    def prepare(self, n: int):
        return {"ok": True}  # Always promise (BUG)

    def accept(self, n: int, value) -> bool:
        self.accepted_value = value  # Always accept (BUG)
        return True
# Two proposers can commit different values
# to different subsets of acceptors.
```

```python
# GOOD: Correct Paxos acceptor with proposal tracking

from dataclasses import dataclass
from typing import Optional

@dataclass
class AcceptedProposal:
    proposal_n: int
    value: object

class PaxosAcceptor:
    def __init__(self):
        self.promised_n: int = -1          # Phase 1 promise
        self.accepted: Optional[AcceptedProposal] = None

    def prepare(self, n: int) -> dict:
        """Phase 1b: respond to Prepare(n)."""
        if n > self.promised_n:
            self.promised_n = n
            return {
                "ok": True,
                # Report previously accepted proposal (if any)
                # Proposer must use this value if present
                "accepted_n": (
                    self.accepted.proposal_n
                    if self.accepted else None
                ),
                "accepted_value": (
                    self.accepted.value
                    if self.accepted else None
                ),
            }
        else:
            # Reject: already promised to a higher-n proposer
            return {"ok": False, "highest_seen": self.promised_n}

    def accept(self, n: int, value: object) -> bool:
        """Phase 2b: respond to Accept(n, value)."""
        if n >= self.promised_n:
            # Accept and update state
            self.accepted = AcceptedProposal(
                proposal_n=n,
                value=value
            )
            # Do NOT update promised_n here:
            # A future Prepare with n+1 should still work
            return True
        else:
            # Reject: received Prepare with higher n after this
            return False

class PaxosProposer:
    def propose(
        self,
        n: int,
        my_value: object,
        acceptors: list
    ) -> Optional[object]:
        """Run one round of Paxos."""
        # Phase 1: Prepare
        quorum_size = len(acceptors) // 2 + 1
        promises = []
        for a in acceptors:
            response = a.prepare(n)
            if response["ok"]:
                promises.append(response)
            if len(promises) >= quorum_size:
                break

        if len(promises) < quorum_size:
            return None  # Phase 1 failed

        # If any promise contains an accepted value:
        # MUST use the value with the highest accepted_n
        highest = max(
            (p for p in promises if p["accepted_n"] is not None),
            key=lambda p: p["accepted_n"],
            default=None
        )
        value = highest["accepted_value"] if highest else my_value

        # Phase 2: Accept
        accepts = 0
        for a in acceptors:
            if a.accept(n, value):
                accepts += 1
            if accepts >= quorum_size:
                return value  # Consensus reached

        return None  # Phase 2 failed
```

---

### ⚖️ Comparison Table

| Property | Single Paxos | Multi-Paxos | Raft |
|---|---|---|---|
| **Purpose** | Choose one value | Replicated log | Replicated log |
| **Phases per write** | 2 | 1 (after leader established) | 1 (AppendEntries) |
| **Leader needed** | No (but improves liveness) | Yes (implicit) | Yes (explicit) |
| **Understandability** | Hard | Very hard | Designed for clarity |
| **Used in** | Academic, Chubby internals | Chubby, Zookeeper (Zab variant) | etcd, CockroachDB, TiKV |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Paxos requires all nodes to agree" | Paxos requires a quorum (majority). A value is decided when a majority of acceptors have accepted it, regardless of what minority nodes have done. |
| "Paxos is too slow for production" | Multi-Paxos in steady state (stable leader) is as fast as Raft - one round trip per log entry. The 2-round overhead only occurs during leader election or on first startup. |
| "Paxos guarantees liveness" | Paxos guarantees safety (no two different values committed). Liveness requires a stable leader. The dueling proposers scenario is a liveness failure, not a safety failure. |
| "Raft replaced Paxos" | Raft replaced Multi-Paxos as the preferred implementation-level algorithm. Paxos remains the theoretical foundation. Understanding Paxos makes Raft's design choices obvious rather than arbitrary. |

---

### 🚨 Failure Modes & Diagnosis

**Split Proposals (Liveness Failure)**

**Symptom:** Zookeeper or a Paxos-based system
keeps entering elections, never reaching a stable
state. Proposal rounds repeatedly fail.

**Root Cause:** Multiple nodes believe they should
be leader and are sending competing Prepare messages.
Each supersedes the other, preventing Phase 2 from
completing.

**Diagnosis:**
```bash
# Zookeeper: check leader election log:
grep "LEADING\|FOLLOWING\|LOOKING" zookeeper.log | tail -50
# If oscillating LOOKING/LEADING: election instability

# Paxos systems: check proposal round counters
# in metrics. If proposal_n is incrementing rapidly
# without commits: dueling proposers.
```

**Fix:** Ensure only one proposer is active. In
practice: fix the network partition or node failure
causing nodes to not receive leader heartbeats.
Increase election timeout to reduce false elections.

---

### 🔗 Related Keywords

**Prerequisites:** `Consistency` (DST-014),
`Read and Write Quorums` (DST-027),
`Raft Consensus Algorithm` (DST-041)

**Builds On This:** `Leader Election` (DST-046),
Zookeeper, Google Chubby, Google Spanner

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1a   │ Prepare(n) → Promise: tell me if you've   │
│            │ already accepted something                 │
│ PHASE 1b   │ Promise(n, prev_n, prev_v) or Reject      │
│ PHASE 2a   │ Accept(n, v) where v = previously accepted │
│            │ value (if any) or proposer's own value    │
│ PHASE 2b   │ Accepted or Reject                        │
├────────────┼────────────────────────────────────────────┤
│ KEY RULE   │ Proposer MUST continue prior committed     │
│            │ value (never propose a new one if old exist│
│ QUORUM     │ Majority of acceptors for both phases      │
├────────────┼────────────────────────────────────────────┤
│ GUARANTEES │ Safety: always. Liveness: with stable leade│
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Phase 1 discovers history, Phase 2 extends│
│            │  it - the invariant is: never lose a win." │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Paxos teaches the deepest lesson in distributed
systems: **agreement in an asynchronous system
requires discovering, not imposing**. A proposer
cannot simply declare its value the winner - it must
first check what others have already accepted and
potentially continue their work rather than its own.
This pattern appears everywhere: leader election
algorithms check which node has the most up-to-date
state before winning; distributed databases check
vector clocks before accepting writes; even human
consensus building works this way - you gather
existing positions before proposing a resolution.
The discipline of "discover before proposing" is
the core of any correct distributed agreement protocol.

---

### 💡 The Surprising Truth

Leslie Lamport submitted the Paxos paper in 1989
to TOCS (ACM Transactions on Computer Systems). The
reviewers found the paper's narrative style (Lamport
wrote it as a story about an ancient Greek parliament)
too unusual and unclear. The paper was rejected. It
circulated as a DEC SRC Technical Report until 2001
when Lamport re-submitted a "conventional" version
titled "Paxos Made Simple." In the interim, Google
independently discovered a similar algorithm for
Chubby (their distributed lock service) and engineers
had to figure out Paxos from the unpublished report.
Lamport later wrote: "The Paxos algorithm, when
presented in plain English, is very simple." The
irony: the "understandability" problem that Raft
tried to solve was in part caused by the 12-year
delay in Paxos's formal publication.

---

### ✅ Mastery Checklist

1. [TRACE] Walk through a single Paxos round with
   3 acceptors, starting from Prepare(5) and ending
   with a value committed. Include the case where
   acceptors have already promised to proposal n=3.
2. [EXPLAIN] Why does the proposer have to use the
   previously accepted value if one exists in Phase 1b
   responses? What goes wrong if it ignores it and
   proposes its own value?
3. [IDENTIFY] Describe the dueling proposers liveness
   failure and explain how Raft prevents it.
4. [COMPARE] List two properties that Raft adds to
   Multi-Paxos that make it easier to implement
   correctly, and explain why each property helps.
5. [APPLY] Paxos is used to implement a distributed
   lock. What does Phase 1 accomplish in terms of
   "who holds the lock"? What does Phase 2 accomplish?
