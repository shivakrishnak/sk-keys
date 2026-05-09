---
id: DST-031
title: Fencing Epoch
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-022, DST-030
used_by: DST-023
related: DST-030, DST-022, DST-029
tags:
  - distributed
  - reliability
  - algorithm
  - deep-dive
  - pattern
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /distributed-systems/fencing-epoch-concept/
---

# DST-031 - Fencing Epoch

⚡ TL;DR - An epoch (also called term, generation, or era) is a monotonically increasing integer that identifies a distinct period of distributed system leadership; every consensus protocol uses epochs to discard stale messages, detect leadership changes, and ensure no action from a previous epoch can be accepted in a new one.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-022, DST-030          |     |
| **Used by:**    | DST-023                   |     |
| **Related:**    | DST-030, DST-022, DST-029 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed cluster has a leader that crashes. A new leader is elected. The old leader recovers (it wasn't actually dead — just slow). Now two leaders exist, both sending messages to followers. Followers receive AppendEntries from both. Which one do they obey? Without a mechanism to distinguish "messages from the current leader" from "messages from a stale former leader," the followers have no way to decide. If they obey both, they corrupt state. If they obey neither, the system stalls.

**THE BREAKING POINT:**
Network partitions, GC pauses, and process restarts all cause transient "leader disappearance." In each case: the missing leader may return after a new leader has been elected. Its messages look syntactically identical to the new leader's messages. The only distinguishing property is WHEN authority was granted. An epoch number encodes this: "I was the leader during epoch N. If you're in epoch M > N, ignore everything I say."

**THE INVENTION MOMENT:**
The epoch concept appeared in Lamport's Paxos (1989) as the ballot number — a monotonically increasing number for each leadership attempt. Raft (2013) formalized it as the "term" — explicitly used to discard stale messages and detect leadership changes. Every consensus protocol since uses an epoch-like mechanism because it's the minimal representation of "this message belongs to leadership period N."

**EVOLUTION:**
1989: Paxos ballot number. 1992: Viewstamped Replication (VR) "view number." 2007: ZooKeeper epoch (high 32 bits of zxid). 2013: Raft term. 2015: Kafka consumer group generation. 2017: Kubernetes leader lease resourceVersion. 2019: etcd lease revision. The epoch concept is now embedded in every consensus protocol, coordination primitive, and distributed lock manager.

---

### 📘 Textbook Definition

An **epoch** (synonyms: term, generation, view, ballot, era) in a distributed system is a monotonically increasing integer assigned to a distinct period of cluster leadership or authority. Epochs have three key properties: (1) **Monotonicity:** each new epoch is strictly greater than all previous epochs. (2) **Authority binding:** all actions authorized during epoch N are invalid in epoch N+1. A message from epoch N received during epoch M > N is stale and must be discarded. (3) **Conflict detection:** any node receiving a message with epoch > currentEpoch knows it has missed a leadership change and must update its state. The epoch is issued by the consensus protocol (Raft, Paxos, ZAB) during leader election — no new epoch can be issued without a quorum agreeing to it. The fencing token (DST-030) is the storage-layer application of the epoch: the epoch IS the fencing token, used to reject writes from nodes operating in outdated epochs.

---

### ⏱️ Understand It in 30 Seconds

**One line:** An epoch is a timestamp for leadership — a monotone counter that lets every node instantly tell "is this message from the current leader or an old one?"

> Epochs are like the generation number on a software release. If you receive a security patch for v3.1 from a source claiming to be the vendor, but the current version is v5.0: you don't apply it. The generation number (epoch) tells you the patch is stale without reading its contents.

**One insight:** Epochs solve the "stale message" problem with zero coordination. Every node independently applies the same rule: "if message.epoch < currentEpoch: discard." No network round-trip needed. No consensus required to reject a stale message. The epoch comparison IS the validation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Monotone generation:** epoch(new_leader) > epoch(any_previous_leader). Guaranteed by the consensus protocol that assigns epochs (requires quorum agreement on the new epoch value).
2. **Epoch binding:** all authority is scoped to an epoch. A node in epoch N cannot legitimately exercise authority in epoch N+1.
3. **Higher epoch wins:** upon receiving any message with epoch > currentEpoch, a node must immediately update its epoch and reevaluate its role. This is the "step down" rule in Raft: any node that sees a higher term must step down to follower.
4. **Epoch 0 is invalid:** no legitimate authority is ever assigned epoch 0. New clusters start at epoch 1 (or term 1 in Raft). This allows the "compare to 0" pattern as a sentinel for "no known epoch."

**DERIVED DESIGN:**
Epoch numbers flow through every message in a consensus protocol. Every AppendEntries RPC, every RequestVote, every heartbeat carries the sender's current epoch. Recipients check: "is this epoch >= my current epoch?" If yes: accept and process. If no: reject and return the current epoch to the sender.

**THE TRADE-OFFS:**
**Gain:** O(1) stale message detection. Zero network coordination required to reject old epochs. Clear audit trail (what epoch was each action taken in?).
**Cost:** Epoch storage and comparison overhead (negligible). Leader election must increment epoch atomically with quorum agreement. Epoch number space can wrap (very rare — 64-bit epoch numbers won't wrap in practice).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any distributed system where leadership can change must have some mechanism to detect stale authority. Epoch numbers are the minimal such mechanism — a single integer comparison.
**Accidental:** Different names (term, ballot, generation, view, revision) are used across protocols. The concept is identical; the naming is accidental complexity from independent invention.

---

### 🧪 Thought Experiment

**SETUP:** 3-node Raft cluster: N1 (leader, term=3), N2, N3. N1 experiences a 60-second GC pause. After 30 seconds: N2 and N3 detect N1's heartbeat timeout. N2 wins election (now leader, term=4).

**WITHOUT EPOCH COMPARISON:**
N1's GC pause ends. N1 resumes. N1 sends AppendEntries to N2 and N3 (still with its own entries, term=3). N2 receives an AppendEntries from N1. N2 is now the leader — but how does it know this AppendEntries is from a stale leader? It can't — the message looks legitimate. N2 might apply the stale entries or get confused about leadership.

**WITH EPOCH (TERM) COMPARISON:**
N1's GC pause ends. N1 sends AppendEntries (term=3). N2 receives it. N2's currentTerm=4. Check: `3 < 4 → reject`. N2 returns its currentTerm=4. N1 receives the response with term=4 > 3. N1 immediately: `currentTerm=4, role=FOLLOWER, leader=N2`. N1 steps down. All of this happens in one message exchange, without a quorum vote.

**THE INSIGHT:** The epoch (term) is a self-correcting mechanism. Stale leaders don't need to be told to step down by a coordinator — they discover their own staleness the moment they receive a rejection with a higher epoch. The distributed system heals itself through the epoch comparison without any additional coordination.

---

### 🧠 Mental Model / Analogy

> An epoch is like a security clearance generation. When a new administration takes office, all clearances from the previous administration are revoked and reissued with new generation numbers. Any request with a clearance from generation N is automatically rejected in generation N+1. Agents don't need to be individually notified — they discover their clearance is revoked the first time they try to use it and it's rejected.

**Mapping:**

- **Security clearance generation** → epoch number
- **New administration taking office** → new leader election
- **Agent trying to use old clearance** → stale leader sending message with old term
- **Automatic rejection** → `if message.term < currentTerm: reject`
- **Agent discovering clearance is revoked** → stale leader stepping down upon receiving higher term

Where this analogy breaks down: security clearances require an explicit revocation database. Epoch comparison is purely mathematical — no database needed, just a monotone integer comparison.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An epoch is a version number for "who's the boss." Every time a new leader is elected, the epoch number goes up by one. Any message with an old epoch number is ignored. If a server wakes up after a crash and has an old epoch, it discovers it immediately and steps down.

**Level 2 - How to use it (junior developer):**
When building on Raft/etcd-based systems: the revision or term is the epoch. Pass it through all your operations. When your operation is rejected with a higher term: it means a new leader was elected while you were operating. Retry the operation from scratch (read the current state first, then write with a new request). Never retry with the same epoch — always re-read current state first.

**Level 3 - How it works (mid-level engineer):**
In Raft: `currentTerm` is the epoch. Persisted on disk on every update (must survive crashes). On every incoming message: `if message.term > currentTerm: currentTerm = message.term; role = FOLLOWER`. On every outgoing message: include `currentTerm`. On leader election: candidate increments `currentTerm` before sending RequestVote. If elected: becomes leader for `currentTerm`. If it sees a response with higher term: steps down. The term (epoch) is the most frequently written value in a Raft node — persisted before every vote, before every log append, before every message send.

**Level 4 - Why it was designed this way (senior/staff):**
Epochs are the distributed systems equivalent of sequence numbers in TCP/IP — they solve the stale delivery problem. In TCP: a segment from a previous connection with the same port pair must be discarded if it arrives late (ISN solves this). In distributed systems: a message from a previous leadership period must be discarded. The epoch number is the distributed equivalent of the TCP ISN (Initial Sequence Number) for leadership. The key design insight in Raft is that the term serves TRIPLE DUTY: (1) stale message detection (discard message if term < currentTerm), (2) authority proof (current leader's messages carry current term), (3) leadership change detection (seeing a higher term means you're stale). This three-in-one role of a single monotone integer is why terms are the simplest possible mechanism for distributed consensus correctness.

**Expert Thinking Cues:**

- "Raft election storm — many candidates, no winner" → All candidates increment term on election, triggering another election. Randomized election timeouts prevent this — but check if any node's `currentTerm` is extremely high (millions) indicating many failed elections.
- "Kafka consumer group keeps rebalancing" → Each rebalance increments the group generation (epoch). If a consumer repeatedly fails its heartbeat (slow processing), it keeps triggering rebalances. Fix: increase `max.poll.interval.ms` or reduce processing per poll batch.
- "etcd cluster shows extremely high revision number" → Every write to etcd increments the global revision (epoch-like). Millions of revisions = millions of writes since last compaction. Enable auto-compaction: `--auto-compaction-mode=periodic --auto-compaction-retention=1h`.
- "ZooKeeper zxid high epoch" → High 32 bits of zxid = epoch. If epoch is high (> 100), ZooKeeper has had many leader elections. Check stability of ZK leader.

---

### ⚙️ How It Works (Mechanism)

**Epoch lifecycle in Raft (term):**

```
Node state: {currentTerm, role, votedFor}
             all persisted to disk (durability)

Normal flow (N1 is leader, term=5):
  N1 → sends heartbeat {term=5} to N2, N3
  N2: currentTerm=5, 5 >= 5 → accept heartbeat
  N3: currentTerm=5, 5 >= 5 → accept heartbeat

Leader failure + election:
  N1 crashes. N2 times out (150-300ms random).
  N2: currentTerm=5 → 6 (increment for election)
  N2: sends RequestVote {term=6, candidateId=N2}
  N3: 6 > currentTerm(5) → update to 6, vote for N2
  N2: quorum reached → N2 is leader for term=6

N1 recovers:
  N1: currentTerm=5. Sends AppendEntries {term=5}
  N2: term=5 < currentTerm(6) → REJECT
      responds: {success=false, term=6}
  N1: 6 > currentTerm(5) →
      currentTerm=6, role=FOLLOWER, leader=N2
      N1 is self-corrected via epoch comparison
```

**Epoch implementations across systems:**

```
System          | Epoch name      | Bits | Monotone guarantee
----------------|-----------------|------|--------------------
Raft            | term            | 64   | Quorum vote
ZooKeeper       | epoch (zxid hi) | 32   | ZAB election
Kafka consumer  | generation      | 32   | Group coordinator
etcd            | revision        | 64   | Raft log index
Kubernetes      | resourceVersion | 64   | etcd revision
Paxos           | ballot number   | 64   | Phase 1 quorum
HDFS NN HA      | epoch           | 64   | ZK-based lock
Cassandra gossip| generation      | 32   | Node boot count
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (epoch across a full leader election cycle):**

```
Cluster: N1(leader,t=3), N2(follower,t=3), N3(follower,t=3)

N1 crashes (GC, hardware fault, etc.)

N2: heartbeat timeout → starts election
    currentTerm: 3 → 4 (increment)
    sends RequestVote(term=4) to N3

N3: 4 > currentTerm(3) →
    currentTerm=4, voteGranted=true

N2: quorum (N2+N3 votes) → N2 becomes leader(t=4)
    ← YOU ARE HERE: new epoch=4

N2 sends heartbeat(term=4) to N3
N3: 4 >= currentTerm(4) → accepts, resets timer

N1 recovers, sends heartbeat(term=3) to N2:
N2: 3 < currentTerm(4) → REJECT, reply term=4
N1: 4 > 3 → STEP DOWN to follower, term=4

All nodes: currentTerm=4, N2 is leader. Consistent.
```

**FAILURE PATH (epoch number exhaustion - extremely rare):**
A 32-bit epoch in a system with very frequent leader elections (e.g., `election_timeout=1ms` in a testing environment) can wrap around to 0. Term 0 is the "no authority" sentinel — receiving it would cause all stale-detection logic to break (0 < everything). Fix: use 64-bit epoch numbers. Raft implementations (etcd, CockroachDB) use 64-bit terms — won't wrap for billions of years at realistic election rates.

**WHAT CHANGES AT SCALE:**
Multi-Raft (CockroachDB): each range has its own independent Raft group with its own term. A node can simultaneously be a leader in term=47 for range 1 and a follower in term=12 for range 2. Term comparison is always LOCAL to the Raft group — terms are not globally comparable across groups.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multi-leader setups (geo-distributed primary-secondary): epochs apply PER REGION. A region can have its own epoch progression independent of other regions. Cross-region epoch comparison only matters for global operations (2PC coordinators, global locks). Each region's leader may be in a different epoch without that being a conflict.

---

### 💻 Code Example

**BAD - No epoch tracking (stale message processing):**

```java
// No term/epoch checking → stale leader messages processed
public class UnsafeRaftNode {
    private String leaderId;

    // Accepts ANY AppendEntries regardless of source epoch
    public void handleAppendEntries(AppendEntries ae) {
        // No epoch check: stale leader messages are processed
        // as if they were from the current leader!
        this.leaderId = ae.getLeaderId();
        log.append(ae.getEntries());  // BUG: stale entries appended
        // Result: follower applies old leader's entries AFTER
        // a new leader has already committed different entries.
        // Log divergence ensues.
    }
}
```

**GOOD - Epoch (term) comparison at every message boundary:**

```java
// Every message checks sender's term against currentTerm
// Implements the core epoch comparison invariant
public class SafeRaftNode {
    private long currentTerm;  // PERSISTED to disk
    private RaftRole role;     // LEADER, FOLLOWER, CANDIDATE
    private String votedFor;   // PERSISTED per term (one vote/term)

    // Called for every incoming AppendEntries RPC
    public AppendEntriesResponse handleAppendEntries(
        AppendEntries ae) {
        // RULE 1: reject if sender's term is stale
        if (ae.getTerm() < currentTerm) {
            // Sender is operating in an old epoch
            // Return current term so sender can step down
            return AppendEntriesResponse.failure(currentTerm);
        }

        // RULE 2: if sender has higher term → update epoch
        // This node may have missed a leadership change
        if (ae.getTerm() > currentTerm) {
            // Persist to disk BEFORE changing state
            persist(currentTerm = ae.getTerm(), votedFor = null);
            role = FOLLOWER;  // Can't be leader in unknown epoch
        }

        // Now in correct epoch: process the AppendEntries
        resetElectionTimer();  // Valid leader heartbeat received
        return processLogEntries(ae);
    }

    // Called for every incoming RequestVote RPC
    public VoteResponse handleRequestVote(RequestVote rv) {
        // Higher term candidate: update to their epoch first
        if (rv.getTerm() > currentTerm) {
            persist(currentTerm = rv.getTerm(), votedFor = null);
            role = FOLLOWER;
        }

        // Same stale term: reject (we're in a higher epoch)
        if (rv.getTerm() < currentTerm) {
            return VoteResponse.denied(currentTerm);
        }

        // Same term: check if we already voted this term
        // (one vote per epoch enforces election safety)
        if (votedFor != null && !votedFor.equals(rv.getCandidateId())) {
            return VoteResponse.denied(currentTerm);  // Already voted
        }

        // Check log completeness (candidate must have all committed
        // entries — ensures new leader knows all committed state)
        if (!candidateLogIsUpToDate(rv)) {
            return VoteResponse.denied(currentTerm);
        }

        // Grant vote: persist votedFor before responding
        persist(votedFor = rv.getCandidateId());
        return VoteResponse.granted(currentTerm);
    }
}
```

**How to test / verify correctness:**

```bash
# Monitor Raft term stability in etcd:
# High term = many elections = instability
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=json | \
  jq '.[].Status.raftTerm'
# Expected: low, stable number
# Alert if term increases more than once per hour

# Monitor Kafka consumer group generation (epoch):
kafka-consumer-groups.sh \
  --bootstrap-server $KAFKA_BROKERS \
  --describe --group my-consumer-group | \
  grep GENERATION
# High/rapidly increasing generation = frequent rebalances
# Fix: increase max.poll.interval.ms

# ZooKeeper epoch (from zxid):
# zxid = (epoch << 32) | counter
# Extract epoch: zxid >> 32
echo "obase=16; 1234567890" | bc  # convert zxid to hex
# High 8 hex digits = epoch
```

---

### ⚖️ Comparison Table

| System         | Epoch name      | Scope          | Increment trigger     | Persisted   |
| :------------- | :-------------- | :------------- | :-------------------- | :---------- |
| Raft           | term            | Raft group     | Leader election       | Yes (disk)  |
| ZooKeeper      | epoch (in zxid) | ZK cluster     | ZAB leader election   | Yes (disk)  |
| Paxos          | ballot number   | Paxos instance | Prepare phase         | Yes (disk)  |
| Kafka consumer | generation      | Consumer group | Group rebalance       | Coordinator |
| etcd           | revision        | Cluster        | Every write           | Yes (WAL)   |
| Kubernetes     | resourceVersion | Per-resource   | Every resource update | etcd        |
| Cassandra      | generation      | Node           | Node restart          | Yes (disk)  |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                                                                                                                   |
| :--------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Epoch and term are different things"          | Raft calls it "term." Paxos calls it "ballot." ZooKeeper calls it "epoch." VR calls it "view." They are all the same concept: monotonically increasing leadership period identifier. The term "epoch" is used generically; each protocol has its own name.                                                                |
| "Higher epoch always means more correct data"  | Higher epoch means more RECENT authority, not necessarily more complete data. A new leader in a higher epoch may have fewer log entries than a follower with more log entries. Raft's leader election ensures the new leader has all COMMITTED entries — but it may not have all entries (some may be uncommitted).       |
| "Epoch rollover is a theoretical concern"      | For 32-bit epochs in systems with frequent elections (test environments, buggy code): yes, rollover is possible. Production systems use 64-bit epoch numbers. But 32-bit Kafka consumer `generation` could theoretically rollover after 4 billion rebalances — not practically concerning but the code should handle it.  |
| "A node can increment the epoch independently" | Epoch increment requires quorum agreement. A single node cannot unilaterally declare itself in a new epoch. It can TRY to start a new election (incrementing its local term), but the new term is only "real" if the node wins a quorum vote. Failed elections increment local terms but don't commit the epoch globally. |
| "Epoch comparison is only for leader election" | Epoch comparison is used in EVERY message type: AppendEntries, RequestVote, heartbeats, InstallSnapshot. Any message received with a stale epoch is rejected. This pervasive checking is what makes epoch-based stale detection robust.                                                                                   |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Election Storm (Rapid Epoch Increment)**

**Symptom:** etcd or Raft cluster's term number increases rapidly (thousands of terms in minutes). Write throughput drops to zero. Metrics show constant leader elections. No writes are committed.
**Root Cause:** All nodes time out simultaneously (clock skew or synchronized election timeouts), all start elections at the same time, nobody wins. Each failed election increments the term. With each increment: all candidates step down, wait, then start another election simultaneously.
**Diagnostic:**

```bash
# Check Raft term increment rate in etcd:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=json | \
  jq '.[].Status.raftTerm'
# Run every 5 seconds — if term increases each run:
# election storm in progress

# Check election timeout configuration:
grep "heartbeat-interval\|election-timeout" \
  /etc/etcd/etcd.conf
# election-timeout should be 10x heartbeat-interval
# Default: heartbeat=100ms, election=1000ms
```

**Fix:**
BAD: All nodes have identical `election_timeout=150ms` (synchronized elections).
GOOD: Raft specifies election timeout is RANDOM within [T, 2T]. etcd default: 1000-2000ms randomized. Verify randomization is active: check etcd source or config for `election-timeout`. If using custom Raft: `timeout = baseTimeout + random(0, baseTimeout)`.
**Prevention:** Never configure fixed (non-random) election timeouts in Raft. Monitor `etcd_server_leader_changes_seen_total` Prometheus metric — alert if > 1 per 5 minutes.

**Failure Mode 2: Epoch Skew After Partial Network Partition**

**Symptom:** After healing a network partition: one node has term=100, others have term=5. The high-term node cannot win an election (its log is far behind), but keeps triggering elections (it starts elections because it sees no leader). Other nodes keep stepping down when they see term=100. The cluster can't elect a stable leader.
**Root Cause:** The partitioned node couldn't win any elections but kept incrementing its term. Its term is now so high that any other node that receives a message from it steps down to follower — including the current leader. A new election starts, the high-term node can't win (log is stale), another node becomes leader at term=101, then the high-term node sends another message at term=102... loop.
**Diagnostic:**

```bash
# Check term of all etcd nodes:
for ep in $ETCD_EP1 $ETCD_EP2 $ETCD_EP3; do
  ETCDCTL_API=3 etcdctl --endpoints=$ep \
    endpoint status --write-out=json | \
    jq '.[].Status.raftTerm'
done
# If one node has term >> others: pre-vote problem
# etcd fix: enable --pre-vote (nodes check if they
# can win before incrementing term)
```

**Fix:**
BAD: Standard Raft allows any candidate to increment term and trigger elections — enabling term inflation in isolated nodes.
GOOD: Enable Pre-Vote (Raft extension): before incrementing term and starting a real election, a node sends a PreVote to check if it would win. If not (log is stale, or other nodes have a leader): the node doesn't increment its term. etcd supports `--pre-vote` flag. This prevents term inflation during partitions.
**Prevention:** Enable Pre-Vote in all Raft implementations for production clusters. This is the standard fix for the "disruptive server" problem described in Raft's extended paper section 4.2.3.

**Failure Mode 3: Security - Epoch Injection via Unauthenticated Raft Peer API**

**Symptom:** An attacker sends a RequestVote message with an extremely high term (e.g., term=2^62) to all cluster nodes via the Raft peer port (2380 for etcd). All nodes receive the message, update their currentTerm to 2^62, and step down to followers. The cluster can't elect a new leader for the next 2^62 terms (practically forever) because no legitimate leader can claim a higher term.
**Root Cause:** Raft peer communication is not authenticated. The attacker can send syntactically valid Raft messages with crafted term numbers. The Raft rule "update to higher term on any message" becomes a vulnerability.
**Diagnostic:**

```bash
# Check if etcd peer port requires mTLS:
curl -k https://etcd-peer:2380/members 2>&1
# If returns data without cert error: peer port is insecure

# Check peer TLS config:
ps aux | grep etcd | grep -E "peer-cert-file|peer-client-cert-auth"
# Must show: --peer-client-cert-auth=true
# AND: --peer-cert-file=... --peer-key-file=... --peer-trusted-ca-file=...
```

**Fix:**
BAD: `etcd --peer-urls=http://0.0.0.0:2380` (plain HTTP for peer traffic).
GOOD: Enable peer mTLS: `etcd --peer-cert-file=/etc/etcd/peer.crt --peer-key-file=/etc/etcd/peer.key --peer-client-cert-auth=true --peer-trusted-ca-file=/etc/etcd/ca.crt`. With peer mTLS: any message without a valid peer certificate is rejected before the Raft layer even sees it.
**Prevention:** Always configure peer mTLS for etcd in production. The peer port (2380) must be firewalled to only allow other etcd cluster members. Apply the same controls as for the client port (2379). Audit peer port exposure in Kubernetes control plane deployments.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-022 - Leader Election (epochs are assigned during leader election — understanding election is required)
- DST-030 - Fencing / Epoch (the storage-level application of epochs to reject stale writes)

**Builds On This (learn these next):**

- DST-023 - Raft (Raft's "term" is the epoch concept fully implemented with persistence, comparison, and election rules)

**Alternatives / Comparisons:**

- DST-030 - Fencing / Epoch (epoch used specifically for storage-level write fencing)
- DST-029 - Split Brain (epochs/terms are the mechanism that prevents split brain in consensus protocols)
- DST-022 - Leader Election (the process that produces and validates epoch numbers)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Monotone leadership-period ID  |
|                  | (term, ballot, generation)     |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Stale messages from old leaders|
|                  | processed as if current        |
+------------------+--------------------------------+
| KEY INSIGHT      | message.epoch < currentEpoch   |
|                  | → discard (no coordination)    |
+------------------+--------------------------------+
| USE WHEN         | Any consensus or leader-based  |
|                  | distributed protocol           |
+------------------+--------------------------------+
| AVOID WHEN       | 32-bit epoch + rapid elections |
|                  | (rollover risk: use 64-bit)    |
+------------------+--------------------------------+
| TRADE-OFF        | Perfect stale detection vs.    |
|                  | persistent storage per epoch   |
+------------------+--------------------------------+
| ONE-LINER        | Stale message detection via    |
|                  | one integer comparison         |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-030 Fencing/Epoch,         |
|                  | DST-023 Raft                   |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Epoch = monotonically increasing leadership period ID. Every consensus protocol has one: Raft term, Paxos ballot, ZooKeeper epoch, Kafka generation. Different name, same concept.
2. The core rule: `if message.epoch < currentEpoch: reject`. Zero coordination needed. One integer comparison.
3. Epoch increment requires quorum. A node can't unilaterally start a new epoch — it needs a quorum vote to legitimize its new epoch claim.

**Interview one-liner:**
"An epoch (term, generation, ballot) is a monotonically increasing integer assigned per leadership period. Every message in a consensus protocol carries the sender's epoch. Recipients discard messages with `epoch < currentEpoch` and step down when they see `epoch > currentEpoch`. This eliminates stale message processing with zero coordination — a single integer comparison is all that's needed to detect whether a message is from a current or past leader."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Version everything with a monotone counter. When authority, capability, or state can be superseded, embed a monotone epoch in every assertion of that authority. Recipients reject assertions with outdated epochs automatically. This eliminates the need for explicit "you are superseded" notifications — supersession is discovered implicitly upon the first interaction after the epoch changes. Apply this pattern whenever an actor needs to detect that its authority has been revoked without requiring a coordinated notification.

**Where else this pattern appears:**

- **TCP Initial Sequence Number (ISN):** Each TCP connection uses a random ISN to ensure segments from a previous connection on the same port pair are rejected. If a stale segment arrives from connection epoch N with sequence number S: the receiving TCP stack checks if S falls within the current connection's receive window. If not (old ISN): reject. The ISN is the epoch for TCP connection identity — it distinguishes "this connection's segments" from "a previous connection's segments."
- **OAuth2 token versioning:** When a user changes their password, all existing OAuth2 access tokens are invalidated. This is implemented with a secret version or generation number embedded in the token (or in the token's validation lookup). Any token from generation N is rejected when the user's current generation is N+1. The generation number IS the epoch for the user's authentication state.
- **Database schema version (migration framework):** Flyway/Liquibase assigns a monotone version number to each database migration. Code that expects schema version N cannot run against schema version N-1 (the migration hasn't run) or N+1 (the schema has changed). The schema version is an epoch for the database structure — code from one epoch cannot safely operate on a schema from a different epoch. This is why blue-green deployments must be backward-compatible: the new code (epoch N+1) must work with schema epoch N until the migration completes.

---

### 💡 The Surprising Truth

Raft terms — the most widely deployed epoch mechanism in distributed systems today — are stored on disk with every vote, every log append, and every leadership change. In a production etcd cluster running in Kubernetes, the term is written to the WAL (Write-Ahead Log) with every Raft operation. On a busy Kubernetes cluster processing 1000 API calls per second: the etcd term is durably persisted (via fsync) to disk thousands of times per second — not because the term changes (it rarely does), but because every log entry includes the current term, and every log entry is durably persisted. The surprising truth: the epoch number (a single integer representing "who is currently in charge") is arguably the most-written piece of data in a Kubernetes cluster. Yet it almost never changes its VALUE — the term may stay at, say, 42 for months at a time. The overhead of durably persisting it thousands of times per second is the unavoidable cost of ensuring that after any crash, every node can atomically determine "what epoch were we in?" from a single disk read.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** In Raft, a node must persist `currentTerm` and `votedFor` to disk BEFORE responding to any RPC. If these aren't persisted before responding: what specific failure scenario occurs? Consider: a candidate C1 receives votes from nodes N1 and N2, becomes leader in term=7. N1 crashes before persisting its `votedFor=C1`. N1 restarts. Another candidate C2 requests a vote for term=7. Can N1 vote for C2? What does this break?
_Hint:_ N1 didn't persist `votedFor=C1` before crashing. After restart: N1 has no record of voting in term=7. C2 requests vote for term=7. N1 checks: "Did I vote in term=7?" — no record. N1 may vote for C2. Now both C1 and C2 may have won a quorum vote for term=7. Two leaders for term=7. Raft's safety invariant violated. This is why Raft requires fsync of `currentTerm` and `votedFor` before responding — it's not optional optimization.

**Q2 (C - Design Trade-off):** Kafka consumer group "generation" (epoch) increments on every rebalance. A consumer group with 50 consumers and a 5-minute processing loop: each `max.poll.interval.ms` violation (slow processing) triggers a rebalance, incrementing the generation. Each rebalance pauses ALL 50 consumers for the duration of the rebalance (coordinator protocol). For a system with 1000 partitions and 50 consumers: estimate the throughput loss from one rebalance event and propose a configuration or architectural change to reduce rebalance frequency.
_Hint:_ Rebalance pause ≈ 3 × `session.timeout.ms` (30 seconds default). 50 consumers × 30 seconds stopped = 1500 consumer-seconds of lost throughput. With 1000 partitions: 30 seconds × 1000 partitions of unprocessed records. Configuration fix: `max.poll.interval.ms` increase, batch size reduction. Architectural fix: Kafka Streams with incremental cooperative rebalancing (COOPERATIVE_STICKY). What is the epoch/generation number implication of cooperative rebalancing vs. eager rebalancing?

**Q3 (A - System Interaction):** etcd stores Kubernetes resource versions as its revision counter (a global epoch for the etcd state machine). When a Kubernetes controller uses `List + Watch` to track Pod changes: the initial `List` returns a `resourceVersion`. The controller then starts a `Watch` from that `resourceVersion`. If the controller crashes and restarts: it re-reads `resourceVersion` from its cache and resumes the Watch. If the `resourceVersion` is too old (older than etcd's compaction window): the Watch fails with "compacted" error. What is the correct recovery strategy, and how does the epoch (resourceVersion) concept determine the correct behavior?
_Hint:_ When Watch fails with "compacted": the controller must re-do a full `List` (getting a fresh resourceVersion) and rebuild its cache from scratch. The old `resourceVersion` is from a compacted epoch — etcd no longer has the event history from that point. This is the "epoch compaction" problem: epochs from before compaction are gone. The controller must reconcile its FULL current state against the API server's state, then start a fresh Watch. Controllers that don't handle this correctly miss events that occurred during their downtime.

