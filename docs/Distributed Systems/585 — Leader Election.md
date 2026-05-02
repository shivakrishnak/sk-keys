---
layout: default
title: "Leader Election"
parent: "Distributed Systems"
nav_order: 585
permalink: /distributed-systems/leader-election/
number: "0585"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Systems, Consensus, Quorum, Failure Modes, Networking
used_by: Raft, Paxos, Distributed Locking, Log Replication, State Machine Replication
related: Raft, Paxos, Split Brain, Quorum, Fencing / Epoch
tags:
  - distributed
  - reliability
  - algorithm
  - deep-dive
  - pattern
---

# 585 — Leader Election

⚡ TL;DR — Leader election is the process by which a distributed cluster of nodes autonomously selects one node to act as the authoritative coordinator, ensuring all clients interact with a consistent single source of truth even as nodes fail and recover.

| #585            | Category: Distributed Systems                                                | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Systems, Consensus, Quorum, Failure Modes, Networking            |                 |
| **Used by:**    | Raft, Paxos, Distributed Locking, Log Replication, State Machine Replication |                 |
| **Related:**    | Raft, Paxos, Split Brain, Quorum, Fencing / Epoch                            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A 5-node database cluster. All 5 nodes accept writes. Client A sends `SET x=1`
to Node 1. Client B sends `SET x=2` to Node 3 simultaneously. Both nodes accept
their write. No node knows what the other accepted. The cluster has two different
"current" values for x — it has forked into inconsistent state. Without a single
designated coordinator, a distributed system cannot serve strongly-consistent writes.

**THE BREAKING POINT:**
Every consistent distributed system needs ONE node (at any given time) to make
the authoritative decision when multiple clients request conflicting operations.
But hard-coding a "master" node is fragile — if it crashes, everything stops.
A self-healing system must be able to elect a NEW leader automatically.

**THE INVENTION MOMENT:**
Leader election algorithms solve the "which node is the authority?" question
dynamically. They guarantee: (1) eventually exactly ONE node believes itself leader,
(2) a failed leader is detected and replaced, (3) the election itself is safe
even when multiple nodes suspect leadership is vacant simultaneously.

---

### 📘 Textbook Definition

**Leader Election** is a distributed coordination problem where N processes must agree that exactly one process is the designated leader at any given time, with the property that if the leader fails, a new election completes and exactly one new leader is elected. Formal safety properties: **Safety** — at most one leader at any time (no split-brain); **Liveness** — if the current leader fails and a quorum of nodes is reachable, a new leader is eventually elected. Common algorithms: Bully Algorithm (elect highest-ID node), Raft Election (randomised timeouts + vote majority), ZooKeeper's ZAB (ZooKeeper Atomic Broadcast), etcd/Raft, and Paxos Phase 1. Leader election typically requires achieving a quorum (majority) of votes to guarantee safety under network partitions (CAP theorem: elect leader or stay available, not both).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Leader election is how a cluster picks one node to be "in charge" — and automatically picks a new one when the current leader goes offline.

**One analogy:**

> Leader election is like choosing a spokesperson in a room where the lights keep going out. When the current spokesperson's voice goes silent (timeout), everyone starts talking at once, but the group eventually agrees on exactly one new voice to listen to. The key rule: wait for a majority to confirm the choice before the new spokesperson starts giving directives — this prevents two people thinking they're simultaneously the spokesperson.

**One insight:**
The most dangerous moment in leader election is the gap between the old leader becoming unreachable and the new leader being confirmed. During this window, some nodes may still be executing the old leader's commands while others have moved on. This is why leader election uses **epochs** (term numbers): any command from a lower epoch is rejected, preventing a recovered old leader from issuing stale commands.

---

### 🔩 First Principles Explanation

**THE SPLIT-BRAIN PROBLEM:**

```
5-node cluster: N1 N2 N3 | N4 N5  (network partition)

Left partition:  N1, N2, N3 — elect N1 as new leader (3/5 quorum ✓)
Right partition: N4, N5 — cannot form quorum (2/5 < majority) ✗
  → N4, N5 must NOT elect a leader (stay read-only or reject writes)

WHY MAJORITY?
  If left = 3 and right = 2 (out of 5):
    Left CAN form majority: safely elect
    Right CANNOT form majority: safely cannot elect
    GUARANTEE: at most one partition can form a quorum at a time
               → at most one leader at any time → no split-brain

  If we allowed any 2 nodes to elect a leader:
    LEFT elects N1, RIGHT elects N4 → TWO leaders → split-brain
```

**RAFT ELECTION (simplified):**

```
State machine:
  FOLLOWER → (timeout, no heartbeat) → CANDIDATE
  CANDIDATE → (wins majority votes) → LEADER
  CANDIDATE → (sees higher term or other leader) → FOLLOWER
  LEADER → (network partition or higher term) → FOLLOWER

Election:
  1. Follower times out (randomised 150-300ms — reduces simultaneous elections)
  2. Increments term number (epoch), votes for self, sends RequestVote to all
  3. Each node votes YES if:
     - It hasn't voted in this term yet, AND
     - Candidate's log is at least as up-to-date as voter's log
  4. Candidate wins if it receives votes from majority (N/2 + 1)
  5. Winner broadcasts leader status; all other candidates become followers

KEY SAFETY INSIGHT: log completeness check in step 3 ensures the new leader
  has all committed entries from previous terms — no data loss on leader change.
```

**TERM / EPOCH NUMBER:**

```
Term 1: N1 is leader.
N1 crashes. Timeout fires.
Term 2: N3 wins election, becomes leader.
N1 recovers with outdated state (still thinks term=1).
N3 sends messages with term=2.
N1 sees term=2 > its term=1 → immediately steps down to follower.
N1 will not issue commands as "leader" → no split-brain.

RULE: Any message with higher term number immediately demotes the receiver to follower.
```

**BULLY ALGORITHM:**

```
Node with highest ID always wins.
Election triggered by any node noticing unresponsive leader:
  1. Initiating node A sends ELECTION to all nodes with higher ID
  2. If no higher-ID node responds within timeout → A declares itself leader
  3. If higher-ID node B responds: B takes over election process, repeats
  4. Eventual winner broadcasts "I AM LEADER" to all

Weakness: highest-ID node always wins → may not be the most up-to-date node
          (fine for simple coordination, NOT for replicated log safety)
```

---

### 🧪 Thought Experiment

**SETUP:** 3-node Raft cluster: N1 (leader), N2, N3. All healthy.

**SCENARIO — Network Partition:**
N1 gets partitioned from N2, N3 (N1 can still talk to clients on its side).

- N1: still thinks it's leader. Accepts client writes. Tries to replicate — can't reach N2 or N3. Log entries NOT committed (no majority). What should N1 do?
- N2 and N3: N1's heartbeats stop. Election timeout fires (say N2 first). N2 increments term, sends RequestVote to N3. N3 votes YES. N2 wins (2/3 quorum). N2 is elected as new leader with higher term.
- N1 recovers (partition heals): N1 receives a message with term > its own. N1 steps down to follower immediately. N1's un-committed log entries from "fake" leadership are discarded and overwritten by N2's log.

**WHAT THIS PROVES:**
The randomised timeout ensures N2 fires before N3 (reducing tie elections). The term number ensures the recovered old leader (N1) never acts as leader again in its outdated term. Any client writes that N1 accepted but didn't commit are LOST — this is correct: clients should retry via the new leader.

**IMPLICATIONS FOR CLIENT DESIGN:**
Clients must not assume a "yes" from the leader means the write is committed until the leader confirms majority replication. Raft only acknowledges a write to the client after it's committed on a majority — so this scenario results in N1 never responding to those clients (they retry), not in silent data loss.

---

### 🧠 Mental Model / Analogy

> Leader election is like an Olympic relay race succession plan.
> The current runner (leader) must signal the next runner before handing off the baton.
> If the current runner collapses (crashes), the team has a rule: the runner with
> the highest runner number (most complete race knowledge) takes over rather than
> any runner. The baton number (epoch/term) increments on each handoff — any runner
> who received an old baton number automatically stands down.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Leader election is a cluster's automatic "promotion" mechanism: when the current boss (leader) goes offline, the remaining nodes hold a vote, and the winner becomes the new boss. The vote requires more than half the nodes to agree.

**Level 2:** Election safety requires a majority quorum: the winning candidate must get `floor(N/2) + 1` votes. This prevents two different partitions from simultaneously electing a leader (split-brain). The election is triggered by a timeout — when a follower doesn't hear from the leader within a window, it starts an election. Randomised timeouts reduce simultaneous elections.

**Level 3:** The elected leader gets a term/epoch number. All subsequent commands carry this term. A node that receives a message with a higher term than it knows immediately steps down to follower. This epoch mechanism prevents a recovered stale leader from issuing commands — it sees the new higher term and immediately defers. The elected leader's log must be at least as up-to-date as any majority member's log (safety invariant) — Raft enforces this via a log completeness check in the vote grant condition.

**Level 4:** Leader election is a special case of consensus: nodes must agree on identity (which node is leader) rather than on a value. This is why you can reduce leader election to multi-Paxos or Raft consensus. The optimal election timeout range (150-300ms in Raft) is a trade-off: too short → spurious elections under network jitter; too long → slow recovery after genuine leader failure. In production, randomised election timeouts prevent "election livelock" — where multiple candidates keep cancelling each other's elections. Leader stickiness (preferring to re-elect the current leader when healthy) reduces disruptions in stable systems. Raft's Pre-Vote extension prevents unnecessary term increments from partitioned nodes trying to start unnecessary elections.

---

### ⚙️ How It Works (Mechanism)

**Raft Election State Machine:**

```
┌──────────────────────────────────────────────────────────┐
│       FOLLOWER                                           │
│  - Receives AppendEntries (heartbeats) from leader       │
│  - Resets election timeout on each heartbeat             │
│  - If timeout expires → become CANDIDATE                 │
│                  ↓ timeout                               │
│       CANDIDATE                                          │
│  - Increment currentTerm                                 │
│  - Vote for self                                         │
│  - Send RequestVote(term, lastLogIndex, lastLogTerm)     │
│  - If majority vote YES → become LEADER                  │
│  - If receive AppendEntries/higher term → FOLLOWER       │
│  - If timeout again (no majority) → retry with term+1    │
│                  ↓ majority votes                        │
│       LEADER                                             │
│  - Send AppendEntries heartbeats to all followers        │
│  - Process client requests, replicate log entries        │
│  - If receive message with term > currentTerm → FOLLOWER │
└──────────────────────────────────────────────────────────┘
```

**ZooKeeper-based Leader Election (practical pattern):**

```java
// ZooKeeper election via ephemeral sequential znodes:
// 1. Each candidate creates /election/candidate-XXXXXXXXXX (sequential)
// 2. Each node reads /election/ children, sorted by sequence number
// 3. If your znode is the smallest: YOU ARE LEADER
// 4. If not: watch the znode just before yours for deletion
// 5. If watched znode is deleted: re-check if you're now smallest → repeat

// Result: exactly one leader at a time, automatic re-election on failure,
// no "write storm" (each node watches only one other znode — not all)
```

---

### ⚖️ Comparison Table

| Algorithm     | Safety (No Split-Brain) | Liveness             | Elects Best Node          | Complexity     |
| ------------- | ----------------------- | -------------------- | ------------------------- | -------------- |
| Bully         | If network reliable     | Yes                  | Highest ID (not best log) | O(N²) messages |
| Raft Election | Yes (quorum)            | Yes (random timeout) | Most up-to-date log       | O(N) messages  |
| ZooKeeper ZAB | Yes (quorum)            | Yes                  | FIFO order                | O(N) messages  |
| Paxos Phase 1 | Yes (quorum)            | With randomisation   | Any proposer              | O(N) messages  |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                      |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Leader election guarantees instant leader change | Election takes at least one round-trip timeout + vote exchange. Production systems should expect 150-500ms of unavailability during election |
| Any node can win an election                     | Safety-sensitive elections (Raft) only allow a node to win if its log is at least as complete as any voter's log — prevents data rollback    |
| Split-brain is prevented by leader heartbeats    | Heartbeats detect failure but cannot prevent split-brain — only quorum-based voting prevents two simultaneous leaders                        |
| The first node to timeout becomes leader         | Multiple nodes may timeout simultaneously; votes settle this; randomised timeouts make simultaneous elections rare                           |

---

### 🚨 Failure Modes & Diagnosis

**Frequent Re-elections (Election Storms)**

**Symptom:** Cluster logs show rapid succession of term increments; leaders hold
positions for <1s before new elections; write throughput drops to near zero.

Causes: Network jitter repeatedly exceeds election timeout; election timeout
too short for the network latency in the environment.

**Fix:** Increase election timeout to 3-5× the 99th-percentile heartbeat RTT.
Enable leader stickiness (prefer re-electing current leader when healthy).

Diagnosis:

```bash
# Raft/etcd election events:
journalctl -u etcd | grep -E "election|term|leader"
# Look for: rapid term increment messages vs. expected low frequency
```

---

**Vote Split (No Leader Elected)**

**Symptom:** Cluster enters repeated election cycles; no node achieves majority.

Cause: Even number of nodes (N=4) with 2-2 vote splits, or randomisation is
insufficient and multiple candidacies fire simultaneously.

**Fix:** Use odd number of nodes (3, 5, 7) to ensure a majority is achievable
with fewer tie scenarios. Raft's randomised timeout handles this; in practice
with odd N, splits are rare.

---

### 🔗 Related Keywords

- `Raft` — consensus protocol that uses leader election as a fundamental mechanism
- `Paxos` — Phase 1 of Paxos is a leader election (proposer establishment) step
- `Split Brain` — the failure mode that leader election with quorum prevents
- `Fencing / Epoch` — the mechanism that prevents recovered stale leaders from causing split-brain
- `Quorum` — the majority requirement that gives leader election its safety guarantee

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  LEADER ELECTION                                         │
│  Safety: at most ONE leader at any time (quorum)         │
│  Liveness: new leader elected if majority reachable      │
│  Term/Epoch: increments each election; old terms rejected│
│  Trigger: follower timeout (no heartbeat)               │
│  Win condition: majority vote AND most up-to-date log    │
│  Prevent: split-brain requires MAJORITY quorum (N/2+1)  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 5-node Raft cluster loses nodes N4 and N5 simultaneously (network failure,
not crash — they can still talk to each other). N1 is the current leader with term=3.
What happens on the N1-N2-N3 side? What happens on the N4-N5 side? If N4 and N5
both timeout and N4 tries to elect itself, will it succeed? Why? When the partition
heals and N4 (term=4 from its failed election attempt) reconnects, what happens to N1?

**Q2.** A database cluster needs leader election with the additional property that
the elected leader always has the most complete write-ahead log. Standard Bully
algorithm elects the highest process ID, which may not have the most complete log.
Modify the Bully algorithm to ensure log completeness as the election criterion.
Describe the exact vote comparison logic and explain what happens if two candidates
have logs of equal length but different last-applied terms.
