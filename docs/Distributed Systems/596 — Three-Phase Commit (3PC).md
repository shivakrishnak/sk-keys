---
layout: default
title: "Three-Phase Commit (3PC)"
parent: "Distributed Systems"
nav_order: 596
permalink: /distributed-systems/three-phase-commit/
number: "0596"
category: Distributed Systems
difficulty: ★★★
depends_on: Two-Phase Commit, Distributed Systems, Consensus, Failure Modes
used_by: Distributed Databases, Saga Pattern
related: Two-Phase Commit, Paxos, Saga Pattern, Consensus, Distributed Locking
tags:
  - distributed
  - transactions
  - consistency
  - algorithm
  - deep-dive
---

# 596 — Three-Phase Commit (3PC)

⚡ TL;DR — Three-Phase Commit adds a "pre-commit" phase between 2PC's vote and commit phases, allowing participants to safely commit unilaterally if the coordinator crashes — dramatically reducing the blocking window, but remaining unsafe under network partitions.

| #596            | Category: Distributed Systems                                         | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Two-Phase Commit, Distributed Systems, Consensus, Failure Modes       |                 |
| **Used by:**    | Distributed Databases, Saga Pattern                                   |                 |
| **Related:**    | Two-Phase Commit, Paxos, Saga Pattern, Consensus, Distributed Locking |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (2PC's blocking problem):**
2PC coordinator crashes after Phase 1. All participants voted YES and are now
blocked indefinitely with locks held. Nobody can unilaterally proceed because
nobody knows whether the coordinator decided COMMIT or ABORT before crashing.

**THE INVENTION MOMENT:**
3PC adds a middle phase called "Pre-Commit" or "Prepared-to-Commit." Once a
participant receives PRE-COMMIT, it knows the coordinator received all YES votes
and decided to commit. If the coordinator then crashes, any participant can
safely commit unilaterally — because they know all other participants ALSO received
PRE-COMMIT (the coordinator only sends PRE-COMMIT after collecting all YES votes).
The blocking window is eliminated for crash-stop failures.

---

### 📘 Textbook Definition

**Three-Phase Commit (3PC)** extends 2PC with an additional phase to eliminate indefinite blocking. **Phase 1 (Can-Commit)**: coordinator sends `CAN-COMMIT?`; participants vote YES/NO. **Phase 2 (Pre-Commit)**: if all voted YES, coordinator sends `PRE-COMMIT`; participants acknowledge — this sends a "commit intent" signal. If any voted NO or timeout: coordinator sends `ABORT`. **Phase 3 (Do-Commit)**: coordinator sends `DO-COMMIT`; participants finalise. **Non-blocking property**: if a participant has received PRE-COMMIT when the coordinator crashes, it knows all others also voted YES and received PRE-COMMIT — it can safely commit unilaterally during recovery. **Limitation**: 3PC is not safe under network partitions. If a partition occurs during Phase 2, one partition might receive PRE-COMMIT and commit; the other might time out and abort. Split-brain is possible — a problem 2PC doesn't have (it blocks instead).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
3PC adds a "we're all ready to commit" broadcast before the final commit, letting participants safely proceed if the coordinator disappears.

**One analogy:**

> 3PC adds a "hold" step to the wedding ceremony: after everyone says "I do" (Pre-Commit), the officiant announces "marriage is about to be confirmed." Everyone now knows the decision is COMMIT. If the officiant then collapses, any witness can declare them married — everyone already knew the decision.
> But: if communication breaks down during the "hold" phase, one room might commit while another hears silence and aborts. The ceremony fails atomically in 2PC (everyone waits); in 3PC, it might result in a partial marriage.

**One insight:**
3PC trades one problem (blocking on coordinator crash) for another (split-brain on network partition). In data center environments where crash-stop is the dominant failure mode and network partitions are rare, 3PC is a reasonable trade-off. But in cloud environments where transient network partitions are common, 3PC can cause correctness violations — which is why it's rarely used in modern systems. Paxos-based distributed commit is preferred.

---

### 🔩 First Principles Explanation

**3PC PROTOCOL FLOW:**

```
Phase 1 — CAN-COMMIT:
  C ──CAN-COMMIT?──▶ P1, P2, P3
  P1, P2, P3 ──YES──▶ C

Phase 2 — PRE-COMMIT (the new phase):
  C ──PRE-COMMIT──▶ P1, P2, P3
  Each participant writes "pre-committed" to WAL
  P1, P2, P3 ──ACK──▶ C

Phase 3 — DO-COMMIT:
  C ──DO-COMMIT──▶ P1, P2, P3
  Each participant commits.
  P1, P2, P3 ──ACK──▶ C
```

**WHY PRE-COMMIT ENABLES NON-BLOCKING RECOVERY:**

```
Coordinator crashes after sending PRE-COMMIT to P1, P2, P3.
All three received PRE-COMMIT.

P1, P2, P3 know:
  "C sent PRE-COMMIT, which means C received all YES votes.
   C's ONLY option was COMMIT (all voted YES, so no ABORT possible).
   C crashed before sending DO-COMMIT but the decision was already COMMIT."

→ P1, P2, P3 can all commit unilaterally. Non-blocking. ✓

IF coordinator crashes after Phase 1 but before Phase 2:
  Participants voted YES but have NOT received PRE-COMMIT.
  Participants don't know if C sent PRE-COMMIT to ANYONE.
  → ABORT is safe: C hadn't broadcast "everyone said YES" yet.
  → Participants time out and ABORT unilaterally. Non-blocking. ✓
```

**THE PARTITION VULNERABILITY:**

```
Network partition occurs during Phase 2 (PRE-COMMIT sending):
  Left partition (P1, P2): received PRE-COMMIT → wait → commit unilaterally ✓
  Right partition (P3):    did NOT receive PRE-COMMIT → timeout → ABORT ✗

Result: P1 and P2 committed, P3 aborted.
        Transaction is NOT atomic. Data is inconsistent.

In 2PC this scenario: P3 blocks (holds locks, waits for coordinator).
                      Eventually coordinator is recovered or fixed.
                      P3 gets the decision from coordinator. Atomicity preserved.

3PC's trade: partition-safe atomicity (2PC) vs crash-safe non-blocking (3PC).
In modern cloud systems: partitions happen frequently → 3PC is dangerous.
```

---

### 🧪 Thought Experiment

**2PC vs 3PC vs PAXOS-COMMIT for coordinator HA:**

**Scenario:** E-commerce order: debit account on DB1, create order on DB2, reserve inventory on DB3. Coordinator is the order service.

**2PC:** If order service crashes after Phase 1, DB1/DB2/DB3 are blocked. Locks held. Other users cannot buy inventory. Time to recovery = minutes (service restart).

**3PC:** If order service crashes after Phase 2 (PRE-COMMIT), participants commit automatically. Non-blocking. But if the network partitions during Phase 2, some DBs commit and some abort. Customer is debited but no order created. Financial inconsistency.

**Paxos-Based Commit:** Coordinator is a Paxos group of 3 replicated instances. One coordinator dies → failover in 150ms via Paxos leader election. No blocking beyond 150ms. No partition split-brain (Paxos consensus guarantees atomicity). Used by Google Spanner, CockroachDB. Cost: 3× coordinator infrastructure.

**Real-world choice:** Most systems use Saga (no 2PC at all) or Paxos-based TM (for strong consistency), not 3PC. 3PC is theoretically interesting but rarely deployed.

---

### 🧠 Mental Model / Analogy

> 2PC is like a committee vote where everyone must wait for the chair's final announcement.
> Blocking if chair disappears.
>
> 3PC adds a "The chair is ABOUT TO announce PASS" broadcast. Now if the chair
> disappears, everyone can proceed on their own because they all know the announcement
> was PASS. But if the building's PA system fails during this broadcast — some
> rooms heard it and will proceed, others didn't and will cancel. 3PC solves the
> blocking problem by accepting the partition risk.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** 3PC adds a middle step to 2PC's prepare/commit dance. After everyone agrees to commit, the coordinator announces "we WILL commit" before the final commit. If the coordinator dies after that announcement, everyone already knows the outcome and can proceed.

**Level 2:** Phase 1 (vote) → Phase 2 (pre-commit: all know decision) → Phase 3 (commit). Pre-commit enables non-blocking recovery for crash failures. But network partitions during Phase 2 can cause split decisions — some participants commit, some abort. 3PC is safe only in crash-stop environments with no network partitions.

**Level 3:** The formal property: 3PC has "non-blocking" under crash failures but is unsafe under network partitions. This is a direct application of the FLP impossibility theorem and CAP theory: you cannot have both non-blocking and partition safety simultaneously in an asynchronous system with failures. Paxos solves this by using replicated coordinators — making coordinator crash a non-issue while preserving partition safety.

**Level 4:** 3PC's vulnerability during partitions is not a theoretical concern — it's a common production scenario. CloudWatch partition events, Kubernetes network policies, noisy VMs cause regular millisecond-to-second network disruptions. These disruptions arrive at exactly the wrong time with non-zero probability. This is why 3PC's non-blocking property is rarely worth its partition risk in modern cloud deployments. The only context where 3PC makes sense: a tightly-coupled, single-datacenter system with reliable hardware switches and no virtualisation — where partition frequency is negligible. These environments are increasingly rare.

---

### ⚙️ Standard Comparison: 2PC vs 3PC vs Saga:\*\*

| Aspect            | 2PC                      | 3PC                | Saga                    |
| ----------------- | ------------------------ | ------------------ | ----------------------- |
| Atomicity         | Atomic                   | Atomic\*           | Eventual (compensation) |
| Coordinator crash | Blocks indefinitely      | Non-blocking       | N/A                     |
| Network partition | Safe (blocks, not split) | Unsafe (may split) | N/A                     |
| Latency           | 2 RTT                    | 3 RTT              | 1 RTT per step          |
| Lock duration     | Full duration            | Full duration      | Per step                |
| Microservices fit | Poor                     | Poor               | Good                    |

---

### ⚠️ Common Misconceptions

| Misconception                 | Reality                                                                                                                              |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 3PC is always better than 2PC | 3PC is better for crash-stop failures; WORSE for network partitions (which are more common in cloud environments)                    |
| 3PC fully prevents blocking   | 3PC prevents blocking on coordinator crash. It can still block during Phase 2 network issues (between pre-commit and timeout expiry) |
| All modern databases use 3PC  | Almost no modern distributed database uses 3PC. They use 2PC with HA coordinator (Spanner, CockroachDB) or Saga (microservices)      |

---

### 🔗 Related Keywords

- `Two-Phase Commit (2PC)` — the predecessor; 3PC directly solves 2PC's blocking problem
- `Saga Pattern` — the alternative that avoids distributed transactions entirely
- `Paxos` — the preferred modern solution: replicated coordinator eliminates the coordinator SPOF
- `FLP Impossibility` — the theoretical result that bounds what 3PC can achieve (cannot solve both blocking AND partition safety)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  3PC = 2PC + PRE-COMMIT phase                            │
│  Phase 1: Vote (CAN-COMMIT?)                             │
│  Phase 2: Pre-commit (all know decision = COMMIT)        │
│  Phase 3: Do-commit (finalise)                           │
│  WIN: non-blocking if coordinator crashes (crash-stop)   │
│  LOSE: unsafe under network partitions (split decisions)  │
│  VERDICT: rarely used in production; Saga/Paxos preferred│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 3PC coordinator has sent PRE-COMMIT to participant P1 but the network fails before P2 and P3 receive PRE-COMMIT. The coordinator then crashes. The cluster has P1 (pre-committed), P2 (voted YES, waiting), P3 (voted YES, waiting). A recovery protocol allows participants to elect an acting coordinator. Should the acting coordinator commit or abort? Show how either choice can violate atomicity and explain what additional information the recovery protocol would need to make the correct decision.

**Q2.** Compare the failure taxonomy for 2PC vs 3PC: For both protocols, list all possible coordinator crash points, the state of participants at that moment, and whether the outcome is blocking, safe-abort, or split-brain. Then explain why Paxos-based distributed commit eliminates all blocking scenarios without introducing split-brain.
