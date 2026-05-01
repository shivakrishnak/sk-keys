---
layout: default
title: "Paxos"
parent: "Distributed Systems"
nav_order: 587
permalink: /distributed-systems/paxos/
number: "587"
category: Distributed Systems
difficulty: ★★★
depends_on: "Leader Election, Quorum"
used_by: "Google Chubby, Spanner, ZooKeeper (ZAB)"
tags: #advanced, #distributed, #consensus, #coordination, #theoretical
---

# 587 — Paxos

`#advanced` `#distributed` `#consensus` `#coordination` `#theoretical`

⚡ TL;DR — **Paxos** is the foundational consensus algorithm that proves a single value can be agreed upon by N distributed nodes despite failures — the theoretical bedrock underlying Google Chubby, Spanner, and distributed consensus systems.

| #587 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Leader Election, Quorum | |
| **Used by:** | Google Chubby, Spanner, ZooKeeper (ZAB) | |

---

### 📘 Textbook Definition

**Paxos** (Lamport, 1989 published 1998 — "The Part-Time Parliament") is a family of consensus protocols for reaching agreement on a single value among N processes where some processes may fail (crash-stop model). Single-Decree Paxos agrees on one value using two phases: **Phase 1 (Prepare/Promise)** — a proposer sends Prepare(n) to a quorum; acceptors promise not to accept proposals with ballot number < n and return any previously accepted value; **Phase 2 (Accept/Accepted)** — proposer sends Accept(n, v) to quorum; acceptors accept if no promise for higher n; once quorum accepts: value v is chosen. **Multi-Paxos** extends single-decree Paxos to an ordered log by stabilising a distinguished leader (eliminating Phase 1 for subsequent rounds). Safety: at most one value is chosen per slot (never two conflicting decisions). Liveness: not guaranteed (two proposers can live-lock by continuously out-bidding each other — FLP result). Practical systems add leader election to ensure progress. Variants: Cheap Paxos, Fast Paxos, Flexible Paxos, Byzantine Paxos. ZooKeeper's ZAB (ZooKeeper Atomic Broadcast) is a Paxos-like protocol. Google Spanner uses Paxos for per-shard replication.

---

### 🟢 Simple Definition (Easy)

Paxos: how N computers agree on ONE value even if some crash. The "proposer" tries to get its value accepted. It first sends "Prepare(n)" to get promises from a majority. Then sends "Accept(n, v)" — if a majority accept: the value is "chosen." The key insight: if any previous round almost chose value X, all future rounds must also choose X (no flip-flopping). Very hard to implement correctly (Leslie Lamport admitted even his colleagues struggled to understand the original paper).

---

### 🔵 Simple Definition (Elaborated)

Why Paxos is fundamental: it's the first proof that consensus is achievable in asynchronous distributed systems despite process failures (not network partitions — see FLP). The two-phase structure ensures that if any value was "almost chosen" (accepted by a quorum in Phase 2), subsequent proposers will learn about it and adopt it. The ballot number (n) is a "generation number" — higher n wins — preventing old proposals from interfering with new ones. Multi-Paxos reduces to a leader election + log append protocol: once a stable leader exists, Phase 1 is done once for the leader's term, and Phase 2 is repeated for each log slot. This is architecturally similar to Raft — but Raft makes the leader-first model explicit from the start.

---

### 🔩 First Principles Explanation

**Single-Decree Paxos — phase-by-phase:**

```
ROLES:
  Proposer: initiates the protocol, tries to get a value chosen.
  Acceptor: votes on proposals. Must be a majority to "choose" a value.
  Learner: learns the chosen value (may be separate from acceptors).
  
  In practice: each node plays all three roles.

PHASE 1a: PREPARE
  Proposer P selects ballot number n (must be globally unique and increasing).
  Sends Prepare(n) to all (or quorum of) acceptors.

PHASE 1b: PROMISE
  Acceptor A receives Prepare(n):
    If n > A.maxPromised: 
      A.maxPromised = n.
      Responds: Promise(n, acceptedBallot, acceptedValue)
        where acceptedBallot = last ballot A accepted (or null)
              acceptedValue  = last value A accepted (or null)
      EFFECT: A promises to never accept proposals with ballot < n.
    Else (n ≤ A.maxPromised):
      Ignores (or sends Nack).

PHASE 2a: ACCEPT
  Proposer P receives Promise from a QUORUM (majority) of acceptors:
    Let highestAccepted = max(acceptedBallot) from all promises.
    If any acceptor returned (acceptedBallot, acceptedValue):
      v = value associated with highest acceptedBallot.  ← MUST use this value!
      (Proposer cannot use its own value — another value may have been almost chosen.)
    Else (no acceptor has accepted anything):
      v = proposer's own proposed value.
      
  Sends Accept(n, v) to all (or quorum of) acceptors.

PHASE 2b: ACCEPTED
  Acceptor A receives Accept(n, v):
    If n ≥ A.maxPromised:
      A.acceptedBallot = n.
      A.acceptedValue = v.
      Responds: Accepted(n, v) to proposer and all learners.
    Else (n < A.maxPromised — a newer prepare was seen):
      Ignores (or sends Nack).

LEARNING:
  When a quorum of acceptors send Accepted(n, v) for the same n:
    VALUE v IS CHOSEN. Learners record v as the consensus decision.

SAFETY PROOF (why two different values can't be chosen):
  Suppose value X is chosen in ballot n1 (quorum Q1 all accepted X in ballot n1).
  Can value Y ≠ X be chosen in ballot n2 > n1?
  
  For Y to be chosen in n2: proposer must have gotten promises from quorum Q2.
  Q1 and Q2 must share ≥ 1 acceptor (both are majorities of N nodes).
  Shared acceptor A:
    A accepted X in ballot n1.
    A received Prepare(n2) and promised: "maxPromised = n2".
    A returned: Promise(n2, n1, X) ← told proposer about previously accepted value X.
    Proposer in n2 received A's promise with (n1, X) — highest accepted ballot.
    Proposer MUST set v = X (cannot use its own Y).
  Therefore: in ballot n2, proposer proposes X, not Y. 
  Y cannot be chosen. Safety maintained.

CONCRETE EXAMPLE (5 acceptors, 2 competing proposers):

  ROUND 1 — Proposer P1 tries to get value "red":
    P1: Prepare(1) → A1, A2, A3, A4, A5.
    All: Promise(1, null, null) — no previous accepted value.
    P1: Accept(1, "red") → A1, A2, A3, A4, A5.
    A1, A2, A3: Accepted(1, "red").  ← quorum (3 of 5)!
    Value "red" is CHOSEN.
    A4, A5: network delays, haven't received Accept yet.
    
  ROUND 2 — Competing Proposer P2 tries to get value "blue" (concurrent with Round 1):
    P2: Prepare(2) → A1, A2, A3, A4, A5.
    Responses:
      A1: "maxPromised was 1. n=2 > 1. Promise(2, ballot=1, value='red')"
      A2: "maxPromised was 1. n=2 > 1. Promise(2, ballot=1, value='red')"
      A3: "maxPromised was 1. n=2 > 1. Promise(2, ballot=1, value='red')"
      A4: "maxPromised was 1. n=2 > 1. Promise(2, null, null)" — hadn't accepted yet
      A5: "maxPromised was 1. n=2 > 1. Promise(2, null, null)" — hadn't accepted yet
      
    P2 receives promises from A1-A5 (quorum).
    HighestAccepted: ballot=1, value="red" (from A1, A2, A3).
    P2 MUST propose "red" (not "blue")!
    P2: Accept(2, "red") → all.
    All: Accepted(2, "red").
    Value "red" confirmed (same value, higher ballot).
    P2 wanted "blue" but consensus forces "red". Safety maintained.

LIVE-LOCK (why Paxos liveness is not guaranteed):
  P1: Prepare(1). Gets promises. About to send Accept(1, v1).
  P2: Prepare(2) (higher ballot). A1-A5 promise to P2. A1-A5's maxPromised = 2.
  P1: Accept(1, v1) → all. A1-A5: reject (maxPromised=2 > 1).
  P1: Prepare(3). Gets promises. About to send Accept(3, v1).
  P2: Prepare(4). A1-A5 maxPromised = 4.
  P1: Accept(3, v1) → rejected.
  P2: Accept(4, v2) → rejected.
  ... forever. Live-lock.
  
  Fix: only one proposer at a time (leader election). Multi-Paxos adds leader election.

MULTI-PAXOS:
  Extension: use Paxos for a sequence of log slots (slot 1, slot 2, ...).
  Optimization: stable leader completes Phase 1 ONCE for its term.
    Phase 1 with ballot n: "I'm leader for ALL future slots."
    All acceptors promise: "We won't accept < n for ANY slot."
    Leader then runs Phase 2 for each slot independently (no Phase 1 per slot).
    Result: single RTT per slot when leader is stable.
  
  Equivalent to Raft's normal operation (leader election + log append per entry).
  
  Phase 1 required again when: leader fails → new leader with higher ballot → Phase 1 for all uncommitted slots.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Paxos (no consensus algorithm):
- No theoretical proof that distributed consensus is possible
- No principled way to replicate state machine across nodes
- All distributed databases had ad-hoc replication with unknown safety guarantees

WITH Paxos:
→ Theoretical foundation: proved consensus possible despite crash-stop failures
→ Production systems: Google Chubby (distributed lock service) uses Paxos; Spanner uses Paxos per shard
→ Led to Raft: Paxos complexity motivated Raft's design (explicit understandability goal)

---

### 🧠 Mental Model / Analogy

> A land auction in medieval times. A bidder (proposer) first announces "I claim the right to bid — no one accept bids below mine (ballot n)" — notaries (acceptors) promise and reveal any previous bids they've endorsed. If no previous bid: bidder names their own price. Then bidder makes the formal offer (Accept). If a majority of notaries endorse it — the sale is closed. If a rival bidder appeared with a higher "right to bid" number: the original bidder's formal offer is void, must start again with a higher number.

"Right-to-bid number" = ballot/proposal number (n)
"Notaries promising: won't accept lower bids" = Phase 1 Promise (maxPromised)
"Notaries revealing previous endorsed bids" = returning accepted value in Promise
"Sale closed when majority endorse" = value chosen when quorum Accepted

---

### ⚙️ How It Works (Mechanism)

**Simplified Multi-Paxos implementation:**

```java
// Multi-Paxos acceptor state (per log slot):
public class PaxosAcceptor {
    // Per-slot state:
    private Map<Long, SlotState> slots = new ConcurrentHashMap<>();
    private volatile long globalMaxPromised = 0;  // For Phase 1 optimization
    
    static class SlotState {
        volatile long maxPromised = -1;   // Highest ballot promised
        volatile long acceptedBallot = -1; // Ballot of accepted value
        volatile Object acceptedValue = null; // Accepted value
    }
    
    // Phase 1b: handle Prepare(ballot, slot)
    public PromiseResponse prepare(long ballot, long slot) {
        SlotState state = slots.computeIfAbsent(slot, k -> new SlotState());
        synchronized (state) {
            if (ballot > state.maxPromised) {
                state.maxPromised = ballot;
                return new PromiseResponse(true, state.acceptedBallot, state.acceptedValue);
            }
            return new PromiseResponse(false, -1, null); // Nack
        }
    }
    
    // Phase 2b: handle Accept(ballot, slot, value)
    public boolean accept(long ballot, long slot, Object value) {
        SlotState state = slots.computeIfAbsent(slot, k -> new SlotState());
        synchronized (state) {
            if (ballot >= state.maxPromised) {
                state.maxPromised = ballot;
                state.acceptedBallot = ballot;
                state.acceptedValue = value;
                return true; // Accepted
            }
            return false; // Rejected
        }
    }
}

// Proposer (leader in Multi-Paxos runs Phase 1 once per term):
public class PaxosProposer {
    private final List<PaxosAcceptor> acceptors;
    private final int quorumSize;
    private volatile long currentBallot;
    
    // Phase 1 (run once per leadership term):
    public boolean becomeLeader(long ballot) throws Exception {
        this.currentBallot = ballot;
        List<PromiseResponse> promises = new ArrayList<>();
        
        for (PaxosAcceptor acceptor : acceptors) {
            PromiseResponse r = acceptor.prepare(ballot, Long.MAX_VALUE); // All future slots
            if (r.promised) promises.add(r);
        }
        return promises.size() >= quorumSize; // Phase 1 succeeded
    }
    
    // Phase 2 (per log slot, no Phase 1 needed if leader stable):
    public boolean proposeValue(long slot, Object value) throws Exception {
        // Check for previously accepted values (from Phase 1 responses):
        Object actualValue = getHighestAcceptedValue(slot, value);
        
        int accepts = 0;
        for (PaxosAcceptor acceptor : acceptors) {
            if (acceptor.accept(currentBallot, slot, actualValue)) {
                accepts++;
            }
        }
        if (accepts >= quorumSize) {
            notifyLearners(slot, actualValue);
            return true; // Value chosen
        }
        return false; // Phase 2 failed — restart with higher ballot
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Consensus (impossibility: FLP shows cannot guarantee liveness in async systems)
        │
        ▼
Paxos ◄──── (you are here)
(single-decree → Multi-Paxos → replicated log)
        │
        ├── Raft (designed as more understandable Paxos alternative)
        ├── ZooKeeper ZAB (Paxos-like: leader broadcasts ordered updates)
        └── Google Spanner (Paxos per shard for linearisable distributed SQL)
```

---

### 💻 Code Example

**Google Chubby pattern — Paxos for distributed lock service:**

```python
# Chubby (Google's distributed lock service) uses Paxos under the hood.
# Client-facing API: acquire/release named locks.
# Under the hood: Chubby runs a 5-node Paxos group.
# Each lock acquisition = Paxos consensus on lock state.

# Using etcd (Raft, but same conceptual API as Chubby) as a Paxos/Chubby analogy:
import etcd3
import uuid

class DistributedLock:
    """Mimics Chubby's distributed lock using etcd (Raft-based consensus)."""
    
    def __init__(self, etcd_client, lock_name: str, ttl: int = 30):
        self.client = etcd_client
        self.lock_name = f"/chubby/locks/{lock_name}"
        self.ttl = ttl
        self.lease = None
        self.lock_holder_id = str(uuid.uuid4())
    
    def acquire(self) -> bool:
        """Try to acquire lock. Returns True if acquired."""
        # Paxos-equivalent: consensus on who holds the lock.
        # etcd: atomic compare-and-swap on the key (backed by Raft consensus).
        self.lease = self.client.lease(self.ttl)
        
        # Atomic: only creates key if it doesn't exist (compare-and-create).
        # Under the hood: etcd Raft group agrees that this key was created.
        success, _ = self.client.transaction(
            compare=[self.client.transactions.create(self.lock_name) == 0],  # Key doesn't exist
            success=[self.client.transactions.put(self.lock_name, self.lock_holder_id, 
                                                   lease=self.lease)],
            failure=[]
        )
        return success
    
    def release(self):
        """Release the lock."""
        # Only release if we're the current holder (fencing: check lock_holder_id).
        self.client.transaction(
            compare=[self.client.transactions.value(self.lock_name) == self.lock_holder_id],
            success=[self.client.transactions.delete(self.lock_name)],
            failure=[]
        )
        if self.lease:
            self.lease.revoke()
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Paxos and Raft are fundamentally different algorithms | Multi-Paxos and Raft are architecturally equivalent: both use leader election + replicated log. The key difference is how they're specified and implemented. Raft explicitly defines leader election, log indices, terms, and the up-to-date check. Multi-Paxos leaves these as implementation details. This is why Raft implementations are more consistent and easier to verify |
| Paxos guarantees liveness (will always make progress) | Single-Decree Paxos does NOT guarantee liveness. Two proposers can repeatedly out-bid each other (live-lock) and no value is ever chosen. FLP Impossibility Theorem proves no deterministic consensus algorithm can guarantee both safety AND liveness in a fully asynchronous system. In practice: add leader election to ensure at most one proposer → progress is made |
| Paxos is only used in academic systems | Paxos (or variants) powers Google's most critical infrastructure: Chubby (distributed lock, used by BigTable, GFS, Spanner), Spanner (global distributed SQL database), Megastore, and more. AWS also uses Paxos variants. ZooKeeper's ZAB (Zookeeper Atomic Broadcast) is a Paxos-like protocol. The theoretical foundations are very much in production |
| The "ballot number" is the same as Raft's "term" | They're conceptually similar (both prevent old leaders from interfering) but have subtle differences. Raft's term is per-leader and resets on each new election. Paxos ballot numbers must be globally unique and increasing (proposers choose them, often using a formula like `server_id + (n × num_servers)`). Raft's term is implicit in every AppendEntries; Paxos's ballot must be explicitly tracked per slot in multi-Paxos |

---

### 🔥 Pitfalls in Production

**Paxos live-lock causing prolonged unavailability:**

```
PROBLEM: Two nodes simultaneously become leaders (network hiccup → old leader thought
         follower crashed; follower also thinks leader crashed → both restart election
         with competing proposals → live-lock → no consensus → system blocked).

SCENARIO:
  3-node cluster: L (leader), F1, F2.
  Network: brief partition {L} vs {F1, F2}.
  F1, F2: elect F1 as new leader (ballot=2). L not aware yet.
  Partition heals:
    L (ballot=1) resumes sending AppendEntries to F1, F2.
    F1 (ballot=2) rejects L's AppendEntries (ballot 1 < 2).
    F1 sends its own AppendEntries to L.
    L: sees ballot=2 > ballot=1. Steps down. F1 is leader.
  
  Correct Raft handles this gracefully (term number fencing).
  
  BUT: buggy Paxos implementation where two proposers continuously increment ballot:
    Proposer A: Prepare(100). Gets promises. About to Accept(100, v).
    Proposer B: Prepare(101). All acceptors: maxPromised=101.
    Proposer A: Accept(100, v) → rejected (maxPromised=101 > 100).
    Proposer A: Prepare(102). Gets promises. About to Accept(102, v).
    Proposer B: Accept(101, v') → rejected (maxPromised=102 > 101).
    ... indefinitely.

BAD: No leader election, two proposers retry immediately:
  while (true) {
      int ballot = getNextBallot();  // Increments ballot immediately after failure
      if (prepare(ballot) && accept(ballot, value)) break;
      // NO BACKOFF, NO LEADER ELECTION → both retry immediately → live-lock
  }

FIX: Leader election + exponential backoff + jitter:
  // Elect a stable leader (Raft-style): only one proposer active.
  // If proposer detects competing proposer (rejected due to higher ballot):
  //   1. Back off exponentially.
  //   2. Yield to the higher-ballot proposer (it may succeed).
  
  long retryDelay = 100; // ms
  while (true) {
      long ballot = getNextBallot();
      try {
          if (prepare(ballot) && accept(ballot, value)) break;
          // Rejected — someone has higher ballot. Wait + retry.
          Thread.sleep(retryDelay + (long)(Math.random() * retryDelay));
          retryDelay = Math.min(retryDelay * 2, 5000); // Exponential backoff, max 5s
      } catch (HigherBallotException e) {
          // Another proposer won. Let them finish; we become follower.
          becomeFollower(e.getHigherBallot());
          break;
      }
  }
```

---

### 🔗 Related Keywords

- `Raft` — modern understandable alternative to Multi-Paxos with explicit leader election and log replication
- `Leader Election` — required for Multi-Paxos to prevent live-lock (stable leader = progress guaranteed)
- `Quorum` — the majority intersection property that guarantees Paxos safety
- `FLP Impossibility` — proves liveness cannot be guaranteed in async systems (motivates why Paxos has live-lock)
- `ZooKeeper` — uses ZAB (Paxos-like atomic broadcast) for its replication

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Two-phase (Prepare/Promise + Accept/     │
│              │ Accepted): quorum intersection ensures   │
│              │ at most one value chosen                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need theoretical foundation for          │
│              │ distributed consensus; studying systems  │
│              │ like Chubby, Spanner, ZooKeeper          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Implementing from scratch — use Raft     │
│              │ or a library (etcd, ZooKeeper) instead   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The land auction: secure the right to   │
│              │  bid before naming the price."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Raft → ZooKeeper → FLP Impossibility →  │
│              │ Quorum → Leader Election                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In Single-Decree Paxos, a proposer P sends Prepare(5) to 5 acceptors. It receives: A1: Promise(5, ballot=3, value="X"), A2: Promise(5, ballot=2, value="Y"), A3: Promise(5, null, null), A4: Nack (maxPromised=6 already), A5: no response (crashed). Does P have a quorum? What value MUST P propose in Phase 2a? What does it mean that a competing proposer already did Prepare(6)?

**Q2.** Multi-Paxos with a stable leader looks almost identical to Raft. But there's a subtle difference in how they handle "holes" in the log. In Raft: the leader must apply log entries in strict index order; gaps are not allowed. In Multi-Paxos: different proposers can have "holes" in the log (some slots committed, others in-flight). How does a Multi-Paxos implementation handle a hole — a slot where the previous leader started a proposal but crashed before choosing a value?
