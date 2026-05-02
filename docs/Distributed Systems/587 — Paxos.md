---
layout: default
title: "Paxos"
parent: "Distributed Systems"
nav_order: 587
permalink: /distributed-systems/paxos/
number: "0587"
category: Distributed Systems
difficulty: ★★★
depends_on: Leader Election, Quorum, Consensus, Distributed Systems, Failure Modes
used_by: Raft, Distributed Locking, State Machine Replication, Google Chubby
related: Raft, Multi-Paxos, Zab, Consensus, Quorum
tags:
  - distributed
  - consensus
  - algorithm
  - deep-dive
  - reliability
---

# 587 — Paxos

⚡ TL;DR — Paxos is the theoretical foundation of all practical consensus algorithms: a two-phase protocol (Prepare + Accept) that guarantees a cluster of nodes agrees on a single value even when messages are delayed and nodes fail, as long as a majority survives.

| #587            | Category: Distributed Systems                                          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Leader Election, Quorum, Consensus, Distributed Systems, Failure Modes |                 |
| **Used by:**    | Raft, Distributed Locking, State Machine Replication, Google Chubby    |                 |
| **Related:**    | Raft, Multi-Paxos, Zab, Consensus, Quorum                              |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The Two Generals Problem proves you cannot get exactly-once guaranteed agreement over an unreliable network. Yet real distributed systems (databases, coordination services) need to agree on things — the value of a configuration parameter, the identity of a leader, the next transaction to commit. Without a proven algorithm, every team invents their own solution. Some are subtly wrong. A database that uses a flawed consensus algorithm might allow two nodes to simultaneously believe they are the primary — leading to data corruption.

**THE INVENTION MOMENT:**
Leslie Lamport published "The Part-Time Parliament" in 1998 (originally written in 1989) establishing the first provably correct consensus algorithm for asynchronous networks with node failures. Paxos became the standard reference for distributed consensus. It is NOT a practical blueprint (Multi-Paxos fills that gap) but the theoretical foundation upon which all practical consensus algorithms are built and proved correct.

---

### 📘 Textbook Definition

**Paxos** is a consensus protocol operating in an asynchronous network model (no timing guarantees) with crash-stop failures. It assigns roles to processes: **Proposers** (propose values), **Acceptors** (vote on values), and **Learners** (learn the agreed value). Single-decree Paxos reaches agreement on ONE value in two phases. **Phase 1 (Prepare)**: a proposer chooses a proposal number `n`, sends `Prepare(n)` to a quorum of acceptors; each acceptor promises not to accept proposals < n and returns the highest-numbered proposal it has already accepted. **Phase 2 (Accept)**: the proposer sends `Accept(n, v)` to a quorum, where `v` is the value of the highest-numbered prior accepted proposal (if any); each acceptor accepts if it has made no promise for a higher numbered proposal. A value is **chosen** when a quorum of acceptors accept it. **Multi-Paxos** runs Paxos repeatedly for each slot in a log, with an elected leader skipping Phase 1 for subsequent slots.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Paxos is the two-step protocol that proves distributed consensus is possible: first ask "what have others already agreed to?", then propose a value that doesn't contradict it.

**One analogy:**

> Paxos is like passing a motion in a committee with a multi-round voting system.
> Round 1: A member says "I'm proposing motion #5 — is anyone currently committed to a higher-numbered motion?" Any member who already voted on motion #4 reports what they voted for. Round 2: The proposer collects these reports, and if someone already voted for a specific value, must adopt that value; otherwise proposes their own. The motion passes when a majority votes yes.

**One insight:**
Paxos Phase 1 is about preventing the proposer from choosing a value that conflicts with something already agreed. The critical invariant: if any value V was previously "chosen" (accepted by a quorum), then any newly proposed value must be V. Phase 2 enforces this: if any acceptor reports a prior accepted value, the proposer MUST adopt it. This invariant is what makes Paxos safe under concurrent proposers.

---

### 🔩 First Principles Explanation

**PHASE 1 — PREPARE:**

```
Proposer P selects proposal number n (must be globally unique, monotonically increasing).
P sends: Prepare(n) to ALL acceptors (or a quorum).

Each Acceptor A responds:
  if n > max_prepare_n_seen:
    update max_prepare_n_seen = n
    promise: "I will not accept any proposal with number < n"
    return (promise=true, accepted_n, accepted_v)
      where accepted_n = highest proposal number A has accepted (or null)
            accepted_v = corresponding value (or null)
  else:
    return (promise=false)  ← proposer must retry with higher n
```

**PHASE 2 — ACCEPT:**

```
Proposer receives Phase 1 responses from a quorum Q:

Choose value v:
  if any acceptor in Q returned (accepted_n, accepted_v):
    v = accepted_v with highest accepted_n
    (MUST adopt the already-accepted value — the KEY safety rule)
  else:
    v = proposer's own preferred value (no prior accepted value)

P sends: Accept(n, v) to ALL acceptors.

Each Acceptor A:
  if n >= max_prepare_n_seen:
    accept(n, v)
    update max_accepted = (n, v)
    notify Learners
  else:
    reject (another proposer eclipsed this one)
```

**WHY THIS IS SAFE:**

```
Invariant: if value V was chosen (accepted by quorum Q),
  then any future Phase 1 quorum Q' must include at least one
  member of Q (quorum intersection). That member returns accepted_v=V.
  The proposer MUST adopt V. → V is the only value that can be chosen.

The overlap guarantee (quorum ∩ quorum ≠ ∅ for majority):
  |Q1| + |Q2| > N (majority + majority) → must share at least one node.

This is THE fundamental safety argument for Paxos.
```

**MULTI-PAXOS OPTIMISATION:**

```
Single-decree Paxos: agrees on ONE value (one slot in the log).

Multi-Paxos optimisation: elect a stable leader (via Phase 1).
Leader can skip Phase 1 for subsequent slots (Phase 2 only).
This gives a persistent leader that acts like a Raft leader.
Multi-Paxos = Raft in terms of practical behavior (different derivation).

Slot-by-slot:
  Slot 1: [Phase 1 + Phase 2] → agree on value v1
  Slot 2: [Phase 2 only, leader known] → agree on value v2
  Slot n: [Phase 2 only] → agree on value vN
```

---

### 🧪 Thought Experiment

**DUELLING PROPOSERS — LIVELOCK:**

```
Proposer P1 sends Prepare(n=1) → quorum promises.
Proposer P2 sends Prepare(n=2) → quorum promises, eclipsing P1.
P1 sends Accept(n=1) → ALL acceptors reject (promised n≥2, not n=1).
P1 retries: Prepare(n=3) → quorum promises, eclipsing P2.
P2 sends Accept(n=2) → ALL acceptors reject (promised n≥3, not n=2).
P2 retries: Prepare(n=4)...
→ Neither proposer ever completes Phase 2.

This is Paxos LIVELOCK (not deadlock — progress is being made, but never finishing).
```

**THE SOLUTION:**
Multi-Paxos solves livelock by electing ONE stable proposer (leader). Only the leader sends proposals. No duelling proposers means no livelock. This is exactly the motivation for Raft's strong leader design.

**THE THEORETICAL CAVEAT:**
FLP Impossibility (Fischer, Lynch, Paterson, 1985) proves no deterministic consensus algorithm can guarantee progress in an asynchronous system with even one crash-stop failure. Paxos handles this by: (1) guaranteeing SAFETY always; (2) guaranteeing LIVENESS only with timing assumptions (eventually, a stable leader with message delivery). The environment must eventually be "nice enough" for progress.

---

### 🧠 Mental Model / Analogy

> Paxos Phase 1 is like claiming a "reservation number" at a notary's office.
> The higher your number, the more recent your reservation. Everyone with a lower
> number must wait. Phase 2 is like presenting your documents — but you must adopt
> any documents that were ALREADY submitted (to prevent conflicting decisions).
>
> If two people race to submit higher reservation numbers, neither ever gets to
> present documents (livelock). The solution: designate one person as the notary's
> preferred client (stable leader) who doesn't need to queue.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Paxos is the mathematical proof that distributed systems CAN agree on a value despite node failures. It uses a two-round voting protocol with unique vote numbers to prevent conflicting decisions.

**Level 2:** Phase 1 establishes "authority" with a unique proposal number: acceptors promise not to accept older proposals. Phase 2 proposes a value — but must use the most recently accepted value from any acceptor (to avoid contradicting a previous agreement). Agreement is reached when a majority accepts.

**Level 3:** The safety invariant: any two quorums overlap by at least one acceptor. An acceptor in the overlap will report any prior accepted value, forcing the new proposer to adopt it. This prevents two different values ever being chosen for the same slot. Liveness is NOT guaranteed in asynchronous systems (FLP impossibility) — Multi-Paxos solves this with stable leader election.

**Level 4:** Paxos's power is its minimal assumptions: asynchronous network (no delivery timeout), crash-stop failures, majority quorum. It tolerates message duplication, reordering, and loss — only not Byzantine failures. Production implementations (Google Chubby, Spanner) all implement Multi-Paxos variants with: Phase 1 amortised across log slots via stable leader; noop entries to commit prior unconfirmed entries on leader change; log compaction; and Epoch/Lease mechanisms to avoid round-trips on reads. Engineering reality: Paxos papers describe the algorithm, not the implementation. Engineers have found Paxos "underspecified" for real systems — which directly motivated Raft's design as a complete specification of the replicated log state machine.

---

### ⚙️ How It Works (Mechanism)

**Single-Decree Paxos Pseudocode:**

```python
# Proposer:
def propose(preferred_value, n, acceptors):
    # Phase 1: Prepare
    promises = []
    for a in quorum(acceptors):
        resp = a.prepare(n)
        if resp.promise:
            promises.append(resp)

    if len(promises) < quorum_size(acceptors):
        raise Exception("No quorum — retry with higher n")

    # Choose value: must use highest-accepted if any:
    highest = max(promises, key=lambda r: r.accepted_n or -1)
    v = highest.accepted_v if highest.accepted_v else preferred_value

    # Phase 2: Accept
    accepts = []
    for a in quorum(acceptors):
        resp = a.accept(n, v)
        if resp.accepted:
            accepts.append(resp)

    if len(accepts) >= quorum_size(acceptors):
        return v  # CHOSEN!

# Acceptor:
class Acceptor:
    max_prepare_n = 0
    accepted_n = None
    accepted_v = None

    def prepare(self, n):
        if n > self.max_prepare_n:
            self.max_prepare_n = n
            return Promise(True, self.accepted_n, self.accepted_v)
        return Promise(False, None, None)

    def accept(self, n, v):
        if n >= self.max_prepare_n:
            self.accepted_n = n
            self.accepted_v = v
            return Accepted(True)
        return Accepted(False)
```

---

### ⚖️ Comparison Table

| Property          | Single-Decree Paxos      | Multi-Paxos             | Raft                            |
| ----------------- | ------------------------ | ----------------------- | ------------------------------- |
| Scope             | One value per run        | Sequential log slots    | Sequential log                  |
| Leader            | Any proposer             | Stable leader (elected) | Stable leader (elected)         |
| Phase 1 per slot  | Yes                      | Only on first           | Only on first (term)            |
| Livelock risk     | Yes (duelling proposers) | No (stable leader)      | No                              |
| Completeness      | Safety only              | Safety + practical      | Safety + practical + membership |
| Understandability | Low                      | Medium                  | High                            |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                           |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Paxos guarantees liveness (progress)          | FLP impossibility: no consensus algorithm guarantees progress in a purely asynchronous system. Paxos only guarantees liveness under eventual synchrony            |
| Paxos and Multi-Paxos are the same            | Single-decree Paxos agrees on one value. Multi-Paxos uses a leader to agree on an ordered log efficiently                                                         |
| Raft replaced Paxos                           | Raft is a re-derivation of Multi-Paxos with complete specification; they're equivalent in power but Raft is easier to implement correctly                         |
| Two different values can be chosen with Paxos | The quorum intersection invariant mathematically prevents this — if implemented correctly, Paxos never allows two different values to be chosen for the same slot |

---

### 🚨 Failure Modes & Diagnosis

**Proposal Livelock (Duelling Proposers)**

**Symptom:** Cluster oscillates between proposers with incrementing proposal numbers;
no progress is made for seconds; logs show rapid Prepare/Reject cycles.

**Root Cause:** Multiple simultaneous proposers competing; no stable leader.

**Fix:** Implement leader election on top of Paxos (Multi-Paxos). Only the elected
leader sends Accept messages. Randomised backoff for proposers in election phase.

---

**Value Loss After Leader Change**

**Symptom:** A value V was "accepted" by some acceptors but not chosen (no quorum);
new leader takes over; V is not present in the new leader's proposals.

Cause: Phase 1 must include the "no-op" commit protocol — the new leader runs
Phase 1 for each uncommitted slot, discovers any accepted values, and must
re-propose them to commit or replace them. Without this, "almost-chosen" values
may be silently dropped.

**Fix:** On leader change, run Phase 1 for all slots with no confirmed commit and
re-propose whatever was accepted (or a noop if nothing was accepted).

---

### 🔗 Related Keywords

- `Raft` — the most widely implemented successor to Multi-Paxos; same theory, clearer design
- `Quorum` — the majority intersection property that makes Paxos safe
- `Leader Election` — Multi-Paxos Phase 1 stably elects a proposer as leader
- `FLP Impossibility` — the theoretical result that bounds what Paxos (and all consensus) can achieve

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  PAXOS — Two phases for one agreed value                 │
│  Phase 1 (Prepare): claim unique n, get quorum promises  │
│  Phase 2 (Accept): propose value v, get quorum accepts   │
│  Value rule: must adopt highest accepted_v from Phase 1  │
│  Safety: quorum intersection guarantees single value     │
│  Liveness: NOT guaranteed (needs stable leader fix)      │
│  Multi-Paxos: stable leader → Phase 1 amortised          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Walk through a Paxos Phase 1 and Phase 2 execution with 5 acceptors (A1-A5) and 2 concurrent proposers P1 (n=1, prefers value "X") and P2 (n=2, prefers value "Y"). P1 gets promises from A1, A2, A3. P2 sends Prepare(n=2) and gets promises from A3, A4, A5 (A3 switches its promise to n=2). Now P1 sends Accept(n=1, "X"): which acceptors accept? P2 sends Accept(n=2, "Y"): which accept? What is the final outcome, and does Paxos allow two values to be chosen simultaneously?

**Q2.** Google Spanner uses Multi-Paxos for its replicated transaction log. A Paxos leader in Spanner's US-East datacenter crashes. A new leader must be elected from US-East, US-West, or EU replicas. The election requires Phase 1 to "fence" the old leader. Explain: (1) why Phase 1 is needed even when a new leader is elected (what problem does it prevent?); (2) what the new leader must do for uncommitted log slots from the old leader's tenure; (3) how Spanner's use of TrueTime (bounded physical time) can allow some of these steps to be skipped for read-only transactions.
