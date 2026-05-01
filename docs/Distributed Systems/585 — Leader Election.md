---
layout: default
title: "Leader Election"
parent: "Distributed Systems"
nav_order: 585
permalink: /distributed-systems/leader-election/
number: "585"
category: Distributed Systems
difficulty: ★★★
depends_on: "Strong Consistency, Distributed Locks"
used_by: "Raft, Paxos, ZooKeeper, Kubernetes"
tags: #advanced, #distributed, #consensus, #coordination, #fault-tolerance
---

# 585 — Leader Election

`#advanced` `#distributed` `#consensus` `#coordination` `#fault-tolerance`

⚡ TL;DR — **Leader Election** is the distributed algorithm for selecting exactly one node as the authoritative coordinator — the leader that serialises decisions, replicates state, and is automatically replaced if it fails.

| #585            | Category: Distributed Systems         | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | Strong Consistency, Distributed Locks |                 |
| **Used by:**    | Raft, Paxos, ZooKeeper, Kubernetes    |                 |

---

### 📘 Textbook Definition

**Leader Election** is a fundamental distributed coordination problem: given N processes that can communicate via message passing and may fail, select exactly one process as the **leader** such that (1) all non-faulty processes agree on the same leader, (2) the leader knows it is the leader, and (3) if the leader fails, a new leader is elected. Leader election provides the simplest path to strong consistency in distributed systems — all writes go through the single leader, which serialises them. It is a sub-problem of consensus and is implemented by: **Ring election** algorithms (LCR, Hirschberg-Sinclair — O(n log n) messages); **Bully algorithm** (highest process ID wins — simple but O(n²) messages); and **Quorum-based election** (Raft's vote-based election, Paxos, ZooKeeper's ZAB protocol). Modern production systems use Raft's election protocol: candidates request votes; a candidate becomes leader if it receives votes from a majority of nodes; terms prevent split-brain; heartbeats maintain leadership. ZooKeeper uses ephemeral znodes with sequence numbers for application-level leader election.

---

### 🟢 Simple Definition (Easy)

Leader election: among N computers, all must agree on exactly ONE leader. The leader makes the decisions so everyone agrees on the order of events. If the leader crashes: the remaining computers run an election to pick a new leader. Like choosing a team captain: everyone must agree on the same person, and if the captain leaves, a new one is chosen.

---

### 🔵 Simple Definition (Elaborated)

Why leader election is needed: without a leader, two nodes might simultaneously try to become the source of truth. In a 3-node cluster, Node A and Node B both think they should serve writes → split-brain → data diverges → disaster. Leader election ensures only ONE node can be the leader at any time (enforced via quorum: must get majority votes). Raft: a node becomes leader only if a MAJORITY of nodes vote for it. If the network splits into two groups: at most one group has a majority → at most one leader elected. Safety: never two leaders simultaneously.

---

### 🔩 First Principles Explanation

**Raft leader election algorithm with term numbers:**

```
RAFT LEADER ELECTION:

SETUP:
  N nodes: N1, N2, N3, N4, N5.
  Each node has: currentTerm (monotonically increasing), role (Follower/Candidate/Leader), votedFor.

NORMAL STATE:
  One node is Leader. All others are Followers.
  Leader sends HEARTBEAT (AppendEntries with empty entries) to all followers every ~100ms.
  Followers reset their election timeout on heartbeat receipt.
  Election timeout: random(150ms, 300ms). Randomness prevents simultaneous elections.

LEADER FAILURE → ELECTION TRIGGER:
  T=0: Leader (N1) crashes. N1 stops sending heartbeats.
  T=150-300ms: Followers' election timeouts expire (randomly staggered).
  First timeout (say N3 at T=180ms): N3 becomes CANDIDATE.

CANDIDATE BEHAVIOR:
  N3: increments currentTerm (e.g., 1 → 2).
  N3: votes for itself (votedFor = N3 in term 2).
  N3: sends RequestVote(term=2, candidateId=N3, lastLogIndex=X, lastLogTerm=Y) to all others.

VOTING RULES (each node grants at most 1 vote per term):
  Voter grants vote if ALL of:
    1. candidate's term ≥ voter's currentTerm.
    2. voter hasn't already voted in this term.
    3. candidate's log is AT LEAST AS UP-TO-DATE as voter's log.
       "At least as up-to-date": candidate's lastLogTerm > voter's, OR
                                  (equal lastLogTerm AND candidate's lastLogIndex ≥ voter's).

  Why log-up-to-date check?
    Ensures new leader has all previously committed entries.
    Prevents: stale node becoming leader and overwriting committed data.

  N2: term=2 > N2's term=1. N2 hasn't voted in term 2. N3's log up-to-date. GRANTS vote.
  N4: similar check → GRANTS vote.
  N5: receives request but N5's timeout expires first → N5 also becomes Candidate with term=2.
      N5 increments to term=2 and sends its own RequestVote.
      N3 already voted (for itself) in term 2 → DENIES vote to N5.

ELECTION RESULT:
  N3 receives votes: itself + N2 + N4 = 3 votes of 5 (majority = 3). BECOMES LEADER.
  N5 receives votes: itself + ? (others already voted for N3 or N5). Likely loses.

  If N5 wins a split vote: nobody wins majority → timeout → new election with term=3.
  Random timeouts ensure eventual convergence (one candidate gets majority before others start).

SPLIT VOTE RESOLUTION:
  If N3 and N5 both get 2 votes: no majority. Both timeout → new election term=3.
  Random(150-300ms) timers: extremely unlikely both expire at same time again.
  Probabilistically: one candidate starts election before the other → wins majority.

SPLIT-BRAIN PREVENTION:
  Quorum requirement: must get MAJORITY (N/2 + 1) votes.

  Network partition: {N1, N2} and {N3, N4, N5}.
  Partition A ({N1, N2}): minority = 2 of 5 nodes. Cannot form quorum. No leader elected.
  Partition B ({N3, N4, N5}): majority = 3 of 5 nodes. Can elect leader.

  Result: at most 1 leader (in the majority partition). Minority side: no leader → refuses writes.
  → No split-brain (two simultaneous leaders) possible with quorum-based election.

FENCING WITH TERM NUMBERS:
  Term = epoch identifier. Increases on every election.

  Old leader (N1) recovers after crash. Still thinks it's leader (term=1).
  Other nodes: already have term=2 (new leader N3).
  N1 sends AppendEntries(term=1) to followers.
  Follower: "term=1 < my currentTerm=2" → REJECTS. Replies: currentTerm=2.
  N1: receives term=2 > term=1. N1 reverts to FOLLOWER state. N1 accepts N3 as leader.

  Term number acts as "fencing token" — old leader's messages rejected by all followers.

ELECTION TIMEOUT TUNING:
  Too short timeout (e.g., 50ms):
    Frequent spurious elections due to brief network hiccups.
    Leader not failed, just slow heartbeat → unnecessary election → disrupts cluster.

  Too long timeout (e.g., 5 seconds):
    Slow failover: system unavailable for 5 seconds after leader failure.
    During election: reads blocked (no leader to serve linearisable reads).

  Typical values:
    etcd: heartbeat 100ms, election timeout 1000ms.
    CockroachDB: heartbeat 200ms, election timeout 2000ms.
    Kubernetes etcd: heartbeat 100ms, election timeout 1000ms (default).

  Rule of thumb: election timeout ≈ 10× heartbeat interval.
  Rationale: 10 missed heartbeats before declaring leader dead (reduces false positives).

ZOOKEEPER LEADER ELECTION (Application-Level):
  Pattern: services register ephemeral sequential znodes.
  /election/candidate-0000000001 (registered by Service A)
  /election/candidate-0000000002 (registered by Service B)
  /election/candidate-0000000003 (registered by Service C)

  Algorithm:
    Each service: watches the znode with sequence number ONE LESS than its own.
    Service A (lowest number 001): is the LEADER (no smaller znode).
    Service B: watches 001 (A's znode).
    Service C: watches 002 (B's znode).

  Leader A crashes: its ephemeral znode 001 is automatically deleted by ZooKeeper.
  Service B: receives notification (it was watching 001). Checks: am I now the smallest? YES.
  Service B: becomes new LEADER. No need to notify C (C watches B's znode 002, still exists).

  Properties: no "herd effect" (each node watches only one predecessor → O(1) notifications per event).
              ZooKeeper guarantees znode watches → notification delivered exactly once.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT leader election:

- Split-brain: two nodes simultaneously believe they are primary → data divergence
- Conflicting writes: two masters accept different writes → inconsistent state
- No coordination: each node independently decides → no global agreement

WITH leader election:
→ Single source of truth: all writes through one leader → total order of writes
→ Automatic failover: leader failure detected, new leader elected within seconds
→ Consistency: majority quorum ensures at most one leader ever

---

### 🧠 Mental Model / Analogy

> A medieval kingdom where the crown prince is determined by a vote of the council. A king reigns until death (failure). On death: council convenes, requires majority vote to crown a new king. If the kingdom is partitioned (war, no communication between regions): only the region with MAJORITY of council members can crown a new king. The minority region cannot crown anyone (no quorum). The crown has an "era number" (term): if the old king's ghost appears giving orders with the old era, the council immediately recognises the new era and ignores the ghost.

"King" = leader node (single source of truth)
"Council majority vote" = quorum-based election (majority of nodes)
"Era number on the crown" = term number (fencing token, rejects old leader's commands)
"Partitioned kingdom, only majority region crowns" = split-brain prevention via quorum

---

### ⚙️ How It Works (Mechanism)

**ZooKeeper-based leader election:**

```java
@Component
public class LeaderElectionService {

    private final CuratorFramework zkClient;
    private final LeaderLatch leaderLatch;

    public LeaderElectionService(CuratorFramework zkClient, String serviceName) {
        this.zkClient = zkClient;
        // LeaderLatch: Curator recipe for leader election using ZooKeeper ephemeral sequential znodes.
        this.leaderLatch = new LeaderLatch(zkClient, "/election/" + serviceName,
                                            InetAddress.getLocalHost().getHostName());
    }

    @PostConstruct
    public void start() throws Exception {
        leaderLatch.addListener(new LeaderLatchListener() {
            @Override
            public void isLeader() {
                // This instance is now the leader!
                log.info("Became leader. Starting leader-only tasks.");
                startLeaderTasks();
            }

            @Override
            public void notLeader() {
                // Lost leadership (failover, or started as follower).
                log.info("Not the leader. Stopping leader-only tasks.");
                stopLeaderTasks();
            }
        });
        leaderLatch.start();
        // Blocks until leadership acquired or times out:
        // leaderLatch.await(30, TimeUnit.SECONDS);
    }

    // Only call from leader-designated tasks:
    public boolean isLeader() {
        return leaderLatch.hasLeadership();
    }

    @Scheduled(fixedDelay = 5000)
    public void scheduledLeaderTask() {
        if (!isLeader()) return;  // Only leader runs this

        // Leader-only work: e.g., distribute partition assignments to workers,
        // run scheduled database cleanup, coordinate distributed workflow.
        distributeWork();
    }

    @PreDestroy
    public void stop() throws Exception {
        leaderLatch.close();  // Releases leadership (ephemeral znode deleted)
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Consensus (agreement problem)
        │
        ▼
Leader Election ◄──── (you are here)
(elect exactly one leader; sub-problem of consensus)
        │
        ├── Raft (implements leader election via vote + term numbers)
        ├── ZooKeeper (provides leader election primitives via ephemeral znodes)
        └── Distributed Locks (alternative coordination primitive — not leader-based)
```

---

### 💻 Code Example

**Raft election state machine (simplified):**

```java
public enum RaftRole { FOLLOWER, CANDIDATE, LEADER }

@Component
public class RaftNode {

    private volatile RaftRole role = RaftRole.FOLLOWER;
    private volatile int currentTerm = 0;
    private volatile String votedFor = null;  // node ID voted for in currentTerm
    private volatile String leaderId = null;

    private final String nodeId;
    private final Set<String> peerIds;
    private final ScheduledExecutorService scheduler;
    private ScheduledFuture<?> electionTimer;

    // Election timeout: random 150-300ms
    private void resetElectionTimer() {
        if (electionTimer != null) electionTimer.cancel(false);
        int timeout = 150 + (int)(Math.random() * 150);
        electionTimer = scheduler.schedule(this::startElection, timeout, TimeUnit.MILLISECONDS);
    }

    // Called when election timeout expires (no heartbeat received):
    private synchronized void startElection() {
        if (role == RaftRole.LEADER) return;

        role = RaftRole.CANDIDATE;
        currentTerm++;
        votedFor = nodeId;  // Vote for self
        int votesReceived = 1;

        log.info("[{}] Starting election for term {}", nodeId, currentTerm);

        // Send RequestVote to all peers:
        int finalTerm = currentTerm;
        for (String peer : peerIds) {
            boolean granted = sendRequestVote(peer, finalTerm, nodeId, getLastLogIndex(), getLastLogTerm());
            if (granted) votesReceived++;
        }

        int majority = (peerIds.size() + 1) / 2 + 1;
        if (votesReceived >= majority && role == RaftRole.CANDIDATE) {
            becomeLeader();
        } else {
            role = RaftRole.FOLLOWER;
            resetElectionTimer();
        }
    }

    private void becomeLeader() {
        role = RaftRole.LEADER;
        leaderId = nodeId;
        log.info("[{}] Became leader for term {}", nodeId, currentTerm);
        // Start sending heartbeats:
        scheduler.scheduleAtFixedRate(this::sendHeartbeats, 0, 100, TimeUnit.MILLISECONDS);
    }

    // On receiving RequestVote from a candidate:
    public synchronized VoteResponse onRequestVote(int candidateTerm, String candidateId,
                                                    int lastLogIndex, int lastLogTerm) {
        if (candidateTerm < currentTerm) return new VoteResponse(currentTerm, false);

        if (candidateTerm > currentTerm) {
            currentTerm = candidateTerm;
            role = RaftRole.FOLLOWER;
            votedFor = null;
        }

        boolean canVote = (votedFor == null || votedFor.equals(candidateId));
        boolean logUpToDate = (lastLogTerm > getLastLogTerm()) ||
                              (lastLogTerm == getLastLogTerm() && lastLogIndex >= getLastLogIndex());

        if (canVote && logUpToDate) {
            votedFor = candidateId;
            resetElectionTimer();
            return new VoteResponse(currentTerm, true);
        }
        return new VoteResponse(currentTerm, false);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Leader election means only one node is ever active               | Leader election means only one node LEADS (makes ordering decisions). Follower nodes are still ACTIVE — they serve reads (with various consistency levels), participate in replication, and monitor the leader. In Raft: followers can serve serialisable reads (slightly stale) while the leader handles strongly consistent reads and all writes                                                                                                                                                    |
| A new leader election is triggered immediately on leader failure | Election triggers after the election TIMEOUT expires (150-300ms typical). This delay is intentional: prevents spurious elections from brief network hiccups. The timeout is randomised to prevent all followers starting elections simultaneously. Result: ~150-300ms to detect failure + election time (~1 RTT for vote collection) = ~200-600ms total failover time                                                                                                                                 |
| The node with the most data always wins election                 | In Raft: the node whose log is most "up-to-date" (highest lastLogTerm, then highest lastLogIndex) can win the election. But "most data" is not the same as "up-to-date." A stale node that didn't receive recent replication might win if it has a higher process ID (in some implementations) — this is a bug. Raft explicitly requires the log up-to-date check to prevent stale nodes from winning                                                                                                 |
| Leader election and distributed locking are the same             | They are related but different primitives. Leader election: one node continuously holds the "leadership" role for an extended period; other nodes defer to it. Distributed lock: any node can acquire and release a lock for a short critical section; multiple different nodes may acquire it over time. ZooKeeper provides primitives for both. For long-running singletons (cron jobs, partition owners), use leader election. For short critical sections (check-then-act), use distributed locks |

---

### 🔥 Pitfalls in Production

**Stale leader serving reads after network partition heals:**

```
PROBLEM: Old leader isolated by partition, continues serving reads.
         New leader elected. Partition heals. Old leader re-joins.
         During overlap: old leader may briefly serve stale reads.

  5-node Raft cluster: N1=leader(term=1), N2, N3, N4, N5.
  Network partition: {N1} isolated from {N2, N3, N4, N5}.

  {N2,N3,N4,N5}: majority, elect N2 as leader (term=2).
  {N1}: isolated. N1 still believes it's leader (term=1).

  Client A: reads from N1 (stale reads! N1 has no new writes since partition).
  Client B: writes to N2 (new leader, committed entries).
  N1: returns stale data to Client A.

  This is a LINEARISABILITY VIOLATION if reads from N1 are supposed to be strongly consistent.

BAD: Serving reads from any node without leader confirmation:
  // Any node serves reads without checking if it's still the leader:
  public Value read(String key) {
      return localStateMachine.get(key);  // Returns local (potentially stale) state.
  }

FIX 1: READINDEX PROTOCOL (Raft — linearisable reads):
  // Before serving read, confirm still leader via heartbeat to majority:
  public Value linearisableRead(String key) {
      // 1. Record current commit index as readIndex.
      long readIndex = commitIndex.get();
      // 2. Send heartbeat to majority. If majority ACKs: still leader.
      if (!confirmLeadership()) {
          throw new NotLeaderException("Leadership lost");
      }
      // 3. Wait until state machine applied up to readIndex:
      waitForApplied(readIndex);
      // 4. Serve from local state machine.
      return localStateMachine.get(key);
  }

FIX 2: LEASE-BASED READS (bounded latency, slightly weaker):
  // After election, hold "lease" for duration = election_timeout - clock_skew_margin.
  // During lease: safe to serve reads (no other leader could have been elected).
  // Lease expiry: require re-confirmation (heartbeat).
  // etcd: implements lease-based reads for production read performance.

FIX 3: FORWARD READS TO KNOWN LEADER:
  // Non-leader nodes: reject read requests, return leaderHint = known leader address.
  // Client: retry at leader. Adds one RTT but guarantees linearisable reads.
```

---

### 🔗 Related Keywords

- `Raft` — consensus protocol with built-in leader election via terms and votes
- `Paxos` — another consensus protocol for leader election (more complex, older)
- `ZooKeeper` — provides leader election primitives via ephemeral sequential znodes
- `Split Brain` — the failure mode leader election prevents (two simultaneous leaders)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Select exactly one leader; majority       │
│              │ quorum prevents split-brain; terms fence  │
│              │ stale leaders                             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Replicated state machines; distributed    │
│              │ cron jobs; Kafka controller; DB primary   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Short critical sections (use distrib.    │
│              │ locks instead); extremely latency-        │
│              │ sensitive paths (failover = 200-600ms)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Council votes: majority crowns the king; │
│              │  old king's orders rejected by new era."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Raft → Paxos → ZooKeeper → Split Brain → │
│              │ Fencing and Epoch                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Raft's election safety requires that a new leader must have all committed log entries. This is enforced by the "log up-to-date" check during voting. Consider a scenario: 5-node cluster, leader fails after committing entry at index 100 on nodes N1, N2, N3 (majority). Nodes N4 and N5 only have index 99. Can N4 become the new leader? Why or why not? What would happen to committed entry 100 if N4 became leader?

**Q2.** Kubernetes uses etcd for leader election of its control plane components (kube-scheduler, kube-controller-manager). These components use etcd's lease mechanism rather than Raft directly. The lease is a key that a component must hold to be the active leader; it expires after a TTL (15 seconds by default). What happens if the current leader is alive but the lease expiry write (lease renewal) is delayed by more than 15 seconds due to a brief network issue? What is the trade-off between short lease TTL (fast failover) and long lease TTL (fewer false failovers)?
