---
id: DST-009
title: Failure Modes
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-022, DST-046
used_by: DST-015, DST-017
related: DST-046, DST-047, DST-015, DST-022
tags:
  - distributed
  - reliability
  - foundational
  - algorithm
  - deep-dive
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /distributed-systems/failure-modes/
---

# DST-014 - Failure Modes

⚡ TL;DR - Distributed system failure modes form a hierarchy from benign to malicious: crash-stop, crash-recovery, omission, timing, and Byzantine — each requiring progressively stronger and more expensive protocols to tolerate, making the choice of failure model the most consequential design decision in distributed systems.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-022, DST-046                   |     |
| **Used by:**    | DST-015, DST-017                   |     |
| **Related:**    | DST-046, DST-047, DST-015, DST-022 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team designs a distributed payment system. They assume: "if a node fails, it just stops sending messages." They build using Raft (which handles crash-stop failures). In production: a corrupt network card starts sending malformed (but syntactically valid) vote messages. The system doesn't just stop — it elects the wrong leader. Different nodes see different leaders. The system continues processing payments, each half accepting conflicting transactions. Raft doesn't handle this — it was designed for crash failures, not Byzantine ones.

**THE BREAKING POINT:**
Without a taxonomy of failure modes, every system implicitly assumes the best case (crash-stop) while potentially encountering the worst case (Byzantine). The cost of being wrong: crash-stop protocols (Raft, Paxos) provide no safety guarantees against Byzantine nodes. Designing for crash-stop when Byzantine is possible leaves a security hole that no amount of application-layer validation can fully close.

**THE INVENTION MOMENT:**
Lamport, Shostak, and Pease's "Byzantine Generals Problem" (1982) formally established the failure taxonomy: nodes can fail by crashing, by omitting messages, or by sending arbitrary (Byzantine) messages. They proved: Byzantine fault tolerance requires 3f+1 nodes (not 2f+1) to tolerate f failures, because Byzantine nodes can collude. This result made explicit what systems designers implicitly chose: the failure model determines the minimum system requirements.

**EVOLUTION:**
1978: Lamport introduces fail-stop model for reliable systems. 1982: Byzantine Generals Problem — Byzantine fault taxonomy established. 1985: Fischer, Lynch, Paterson (FLP) — impossibility result for consensus in async systems (applies to all failure models above crash-stop). 1999: PBFT (Practical Byzantine Fault Tolerance) — first efficient BFT protocol. 2008: Bitcoin's Proof of Work — Byzantine fault tolerance at internet scale. 2013: Tendermint — BFT consensus for blockchain. 2020s: Most cloud databases use crash-recovery models (Raft); blockchain uses Byzantine models (PBFT, PoW, PoS).

---

### 📘 Textbook Definition

A **failure mode** (or fault model) in distributed systems defines how a component can deviate from its specified behavior. The standard taxonomy (from weakest to strongest assumption about failures): (1) **Crash-stop (fail-stop):** a node fails by halting permanently. It sends no further messages. Other nodes may or may not detect the crash. (2) **Crash-recovery:** a node crashes but may later restart with its persistent state intact. Transient failures. (3) **Omission:** a node drops some messages (send or receive) but doesn't send incorrect messages. (4) **Timing:** a node sends correct messages but may violate timing constraints (e.g., a heartbeat arrives late). (5) **Byzantine (arbitrary):** a node may behave in any way — crash, send incorrect messages, send different messages to different nodes, collude with other Byzantine nodes. The **critical design rule:** the failure model chosen determines the required protocol. Raft/Paxos tolerate crash-recovery failures (2f+1 nodes for f failures). PBFT/Tendermint tolerate Byzantine failures (3f+1 nodes for f failures). Designing for a weaker failure model than what the system actually experiences leads to correctness violations.

---

### ⏱️ Understand It in 30 Seconds

**One line:** How a node can "fail" determines how many nodes you need and what algorithm you use — Byzantine failures require 3f+1 nodes and much more complex protocols than crash failures (2f+1 nodes).

> Failure modes are like adversary levels in a game. Crash-stop is "the player puts down the controller" — they stop participating. Byzantine is "the player actively cheats" — they send fake messages to confuse other players. The rules (protocol) for a fair game (crash-stop) completely break down against a cheating player (Byzantine). You need fundamentally different rules.

**One insight:** The failure taxonomy is not a spectrum — Byzantine is not just "worse crash-stop." It's a categorically different threat model. Crash-stop failures are detectable (silence = failure). Byzantine failures are undetectable (the failed node still sends messages — just wrong ones). This single difference changes required node counts from 2f+1 to 3f+1.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Hierarchy:** crash-stop ⊂ crash-recovery ⊂ omission ⊂ timing ⊂ Byzantine. A protocol that tolerates Byzantine failures also tolerates all weaker failures. A protocol that only tolerates crash-stop fails against omission, timing, or Byzantine.
2. **Detectability:** crash-stop failures are detectable via timeout (silence). Byzantine failures are undetectable — the faulty node continues sending messages, some of which may be correct.
3. **Node count requirement:** f failures, crash-stop: 2f+1 nodes. f failures, Byzantine: 3f+1 nodes. The extra f nodes are needed to outvote Byzantine nodes that may collude.
4. **Message complexity:** crash-stop protocols: O(n) messages. BFT protocols: O(n²) messages (each node must confirm with all others that they received the same message). This is why Byzantine protocols are rare in standard distributed databases.

**DERIVED DESIGN:**
For most cloud infrastructure: crash-recovery (Raft/Paxos) is sufficient — hardware and software failures produce crashes, not Byzantine behavior. For blockchain (untrusted participants) and safety-critical systems (adversarial environment): Byzantine fault tolerance is required.

**THE TRADE-OFFS:**
**Gain (stronger failure model):** correctness guaranteed even against adversarial behavior.
**Cost:** 3f+1 vs 2f+1 nodes (50% more hardware). O(n²) message complexity vs. O(n). Much higher implementation complexity.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The number of required nodes (2f+1 vs 3f+1) is mathematically proven. You cannot build a Byzantine-tolerant system with fewer than 3f+1 nodes.
**Accidental:** Different BFT protocols (PBFT, Tendermint, HotStuff) have different message complexities (O(n²) vs. O(n) with modern optimizations). The choice of protocol is accidental; the node count requirement is essential.

---

### 🧪 Thought Experiment

**SETUP:** 3-node cluster (f=1, crash-stop tolerant). Each node holds a bank balance. Protocol: majority quorum for writes.

**CRASH-STOP FAILURE:** N3 crashes. N1 and N2 still form a quorum. Write "balance=100" succeeds on N1 and N2. N3 recovers, replays log, gets balance=100. Correct.

**BYZANTINE FAILURE (N3 sends wrong votes):** N3 doesn't crash — it's corrupted. Write request arrives. N3 sends conflicting messages: tells N1 "I voted YES" and tells N2 "I voted NO." N1 counts: N1+N3=YES → thinks quorum achieved, commits balance=100. N2 counts: N2 alone=YES (N3 said NO to N2) → doesn't achieve quorum, doesn't commit. Result: N1 committed balance=100, N2 did not. Data divergence from Byzantine node — and a 3-node cluster using Raft has NO defense against this.

**THE INSIGHT:** With 3 nodes (f=1 Byzantine): you need 3(1)+1=4 nodes. The 4th node ensures you can always find a quorum that excludes the Byzantine node. With 3 nodes and 1 Byzantine: the Byzantine node can always be in any quorum of size 2 — it can disrupt both possible quorums.

---

### 🧠 Mental Model / Analogy

> Failure modes are like types of witnesses in a courtroom. A crash-stop witness simply doesn't show up — easy to handle (majority without them). A crash-recovery witness is late but eventually arrives with their original testimony. An omission witness shows up but refuses to answer some questions. A Byzantine witness actively lies — gives different testimony to the judge and jury, forges documents, and coordinates with other bad witnesses. The rules of evidence (protocol) sufficient for an absent witness are completely inadequate for a lying one.

**Mapping:**

- **Absent witness** → crash-stop failure (silent)
- **Late witness** → crash-recovery (eventual return)
- **Selectively silent witness** → omission failure (drops some messages)
- **Lying, coordinating witness** → Byzantine failure (arbitrary messages, possible collusion)
- **Rules of evidence** → consensus protocol (Raft for crash-stop, PBFT for Byzantine)

Where this analogy breaks down: in courts, liars can sometimes be caught through cross-examination. In distributed systems, Byzantine nodes can collude perfectly and there's no way to "cross-examine" them — only to outnumber them with honest nodes.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
In a distributed system, a server can fail in different ways: (1) it might just stop (crash), (2) it might restart and come back, (3) it might randomly drop messages, or (4) it might go rogue and send wrong or conflicting information on purpose. Each type of failure needs a different solution. The nastiest kind (Byzantine) requires much more complex and expensive protocols.

**Level 2 - How to use it (junior developer):**
When choosing between etcd, Kafka, ZooKeeper, or a blockchain for coordination: understand what failure model you're in. Most cloud infrastructure → crash-recovery model → Raft/Paxos (etcd, Kafka KRaft) is sufficient. Financial blockchain (untrusted participants) → Byzantine model → use a BFT protocol (Tendermint, Hyperledger) or Proof of Work/Stake.

**Level 3 - How it works (mid-level engineer):**
The asynchronous network (the real-world network model) means timing failures are ALWAYS possible — messages can be delayed arbitrarily. This is why consensus protocols must be designed for the asynchronous timing model: assume messages can be delayed, not just dropped. Raft's leader heartbeat timeout assumes: "if no heartbeat for election_timeout, leader has failed." This is safe only if Byzantine failures don't happen — a Byzantine leader could send heartbeats from two different IPs to two different follower groups, causing a split-brain that Raft can't defend against. Understanding your failure model determines whether Raft's assumption is valid.

**Level 4 - Why it was designed this way (senior/staff):**
The failure model is the core assumption of every distributed systems correctness proof. FLP impossibility (Fischer, Lynch, Paterson, 1985) proves: in an asynchronous network with even one crash-stop failure possibility, no deterministic algorithm can achieve consensus. Raft and Paxos "solve" this by using timeouts (partial synchrony assumption) — they assume the network is eventually synchronous. PBFT assumes partial synchrony too, but for Byzantine failures requires 3f+1. The model choice is: what failure mode do you assume, and what synchrony assumption do you make? The answer determines everything: node count, message complexity, algorithm choice, and the safety/liveness trade-offs.

**Expert Thinking Cues:**

- "Our Raft cluster acted weirdly after a network card firmware bug" → Network card bug → corrupted but syntactically valid packets → Byzantine failure. Raft has no defense. Fix: add application-layer MAC or TLS for all inter-node communication (TLS catches bit-level corruption).
- "Is the blockchain Byzantine-fault-tolerant?" → Depends on the consensus mechanism. Proof of Work: Byzantine-tolerant up to 50% malicious hash power. PBFT: up to 33% malicious nodes. Proof of Stake (Ethereum): up to 33% malicious stake.
- "Our database uses 2PC with 3 nodes — is that Byzantine-safe?" → No. 2PC is a crash-recovery protocol. A Byzantine coordinator in 2PC can tell different participants different things (commit to some, abort to others), causing inconsistency.
- "Why does AWS Aurora use 4 of 6 quorum for writes?" → 6 nodes: allows 2 complete AZ failures (crash-stop) AND normal reads from 3 of 6. The 4-of-6 write quorum means even with 2 node failures: still have 4 nodes for writes. This is crash-recovery model, not Byzantine.

---

### ⚙️ How It Works (Mechanism)

**Failure mode detection:**

```
Failure Mode    | How detected        | How to tolerate
----------------|---------------------|---------------------
Crash-stop      | Silence / timeout   | Timeout + re-election
Crash-recovery  | Rejoin with log gap | Snapshot + log replay
Omission        | Missing ACKs/msgs   | Retransmit + timeout
Timing          | Deadline exceeded   | Partial synchrony,
                |                     | bounded delays
Byzantine       | Conflicting msgs    | BFT protocol, 3f+1
                | or UNDETECTABLE     | cryptographic signing

Key insight: Byzantine is often SILENT:
  Normal: N1 sends msg to N2, N3. Both get same message.
  Byzantine: N1 sends msg=X to N2, msg=Y to N3.
    N2 and N3 see "correct" messages from N1.
    Neither knows N1 is Byzantine without comparing notes.
    PBFT's "prepare" phase: all nodes broadcast to each other
    → each node collects 2f+1 matching "prepare" messages
    → if Byzantine node sent different msgs: < 2f+1 match
    → Byzantine node can't forge a quorum's agreement
```

**Node count requirements (mathematical basis):**

```
Crash-stop (Raft/Paxos):
  Need: n > 2f (so f+1 quorum excludes all f failures)
  n = 2f+1 is minimum:
    f failures → f+1 correct nodes remain
    Quorum = f+1 → always achievable from correct nodes

Byzantine (PBFT):
  Need: n > 3f (so f+1 good nodes dominate any quorum)
  n = 3f+1 is minimum:
    f Byzantine nodes (may be in any quorum of 2f+1)
    2f+1 quorum MUST have ≥ f+1 honest nodes
    (2f+1 from 3f+1 total: at most f can be Byzantine)
    → f+1 honest nodes always outvote f Byzantine

Why 3f+1 and not 2f+1 for Byzantine?
  With 2f+1 nodes and f Byzantine:
    Quorum = f+1. Byzantine nodes = f.
    f Byzantine nodes CAN be all in the quorum.
    They can agree amongst themselves on wrong value.
    Honest quorum members can't distinguish.
    Safety violated.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CRASH-STOP FLOW (Raft handles it):**

```
N1(leader), N2, N3. N1 crashes.

N2: heartbeat timeout → election → wins (N2+N3 quorum)
N2 becomes leader. N3 follows.
← YOU ARE HERE: crash-stop handled correctly by Raft
No data loss (committed entries replicated to N2,N3 before crash)
```

**BYZANTINE FLOW (Raft DOES NOT handle it):**

```
N1(Byzantine leader). N2, N3 honest followers.

Client sends: PUT x=100
N1 → AppendEntries(x=100) to N2
N1 → AppendEntries(x=200) to N3 (DIFFERENT VALUE!)

N2: ACK (has x=100 in log)
N3: ACK (has x=200 in log)

N1: "I have 2 ACKs (quorum achieved!)" → replies success
    N1 commits both to different followers.

N2.x=100, N3.x=200. Cluster diverged.
Raft has no mechanism to detect N1 sent different values.
← YOU ARE HERE: Byzantine failure — SYSTEM BROKEN
```

**WHAT CHANGES AT SCALE:**
Byzantine fault tolerance cost scales quadratically: O(n²) message complexity in PBFT. At n=100 BFT nodes: 10,000 messages per consensus round. This is why blockchain BFT variants (HotStuff, Tendermint) optimize message complexity. HotStuff achieves O(n) messages per round — practical for up to ~200 validators.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
In a crash-stop model: network partitions are the hardest case (CAP theorem). In a Byzantine model: network partitions + Byzantine behavior simultaneously is the hardest case (impossible to solve without threshold signatures or other cryptographic primitives). The assumption that "only 1/3 of nodes are Byzantine" relies on honest-majority — violated if an adversary can compromise > 1/3 of nodes.

---

### 💻 Code Example

**BAD - Application ignores Byzantine failure mode:**

```java
// 3-node voting system assuming crash-stop only
// VULNERABLE to Byzantine voter sending conflicting votes
public class UnsafeConsensus {
    private int yesVotes = 0;
    private final int quorum = 2; // 2 of 3

    // Accepts any vote message without authentication
    // A Byzantine node can send "YES" to some nodes
    // and "NO" to others — causing divergent commits
    public boolean collectVote(String nodeId, boolean vote) {
        if (vote) yesVotes++;
        if (yesVotes >= quorum) {
            // Commit — but did all quorum members REALLY vote yes?
            // A Byzantine node might have sent NO to another node
            // that's running the same collection
            return commit();  // May diverge across nodes!
        }
        return false;
    }
}
```

**GOOD - Application uses TLS to prevent message forgery (minimal BFT defense):**

```java
// For crash-recovery model (no Byzantine): mTLS prevents
// unauthorized nodes from sending messages.
// For Byzantine model: use PBFT or add message signing.
@Configuration
public class SecureRaftConfig {
    // mTLS: prevents rogue nodes from injecting messages
    // Does NOT protect against compromised legitimate nodes
    // (those are Byzantine: they HAVE valid certs)
    @Bean
    public SslContext raftPeerSslContext() throws Exception {
        return SslContextBuilder.forServer(
            new File("/etc/raft/peer.crt"),
            new File("/etc/raft/peer.key")
        )
        .trustManager(new File("/etc/raft/ca.crt"))
        .clientAuth(ClientAuth.REQUIRE)
        .build();
    }
}

// For Byzantine-tolerant application:
// Use BFT library (e.g., BFT-SMART, Tendermint client)
// or implement threshold signatures for vote verification
public class ByzantineTolerantVoting {
    private static final int TOTAL_NODES = 4; // 3f+1 for f=1
    private static final int QUORUM = 3;      // 2f+1 = 3
    // Honest quorum from 4 nodes:
    // Even if 1 Byzantine node votes differently per target:
    // 3 honest nodes' votes form consistent quorum

    // Each vote carries a cryptographic signature
    // Multiple nodes cross-verify: "did we all receive
    // the same vote from N1?" via prepare phase
    public void handlePrepare(PrepareMessage msg) {
        // Verify signature (prevents forged votes)
        if (!msg.verifySignature(publicKeys.get(msg.getSenderId()))) {
            log.warn("Invalid signature from {}", msg.getSenderId());
            return; // Byzantine node forging message detected
        }
        // Broadcast to other nodes to cross-check
        // (PBFT prepare step: node broadcasts to all)
        broadcastPrepareAck(msg);
    }
}
```

**How to test / verify correctness:**

```bash
# Test crash-stop tolerance (Raft):
# Kill one node, verify writes still succeed:
docker stop etcd-node1
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_EP2,$ETCD_EP3 \
  put test-key test-value
# Should succeed (2 of 3 nodes = quorum)

# Test Byzantine behavior detection:
# Use Jepsen (https://jepsen.io) to inject Byzantine failures:
# Jepsen can inject network partitions, message corruption,
# and timing violations. It does NOT test Byzantine faults
# (by design — crash-stop testing only).
# For Byzantine testing: use formal verification tools
# (TLA+, Ivy) or BFT testbeds.

# Check if your system uses TLS (minimum protection):
openssl s_client -connect etcd-node:2380 \
  -cert /etc/etcd/peer.crt \
  -key /etc/etcd/peer.key \
  -CAfile /etc/etcd/ca.crt 2>&1 | grep "Verify return code"
# Expected: "Verify return code: 0 (ok)"
```

---

### ⚖️ Comparison Table

| Failure mode   | Detectability              | Nodes for f failures | Protocol         | Example                        |
| :------------- | :------------------------- | :------------------- | :--------------- | :----------------------------- |
| Crash-stop     | Easy (silence)             | 2f+1                 | Raft, Paxos      | Server OOM, kernel panic       |
| Crash-recovery | Easy (silence then rejoin) | 2f+1 + persistence   | Raft + WAL       | Restart after power loss       |
| Omission       | Medium (missing ACKs)      | 2f+1 + retransmit    | Raft (handles)   | NIC queue drop, firewall       |
| Timing         | Hard (delay not drop)      | 2f+1 + partial sync  | Raft (timeouts)  | GC pause, network congestion   |
| Byzantine      | Undetectable               | 3f+1 + crypto        | PBFT, Tendermint | Compromised node, hardware bug |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                         |
| :---------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Raft handles Byzantine failures"               | Raft explicitly assumes crash-recovery failure model. Byzantine behavior (sending different messages to different nodes) breaks Raft's safety. PBFT, Tendermint, or HotStuff are needed for Byzantine tolerance.                                                                                                                |
| "Byzantine failures only happen in blockchains" | Byzantine failures occur anywhere a node can malfunction while continuing to send messages: hardware memory corruption, kernel bugs, NIC firmware bugs, software bugs causing incorrect state transitions. TLS between nodes mitigates some but not all Byzantine scenarios.                                                    |
| "3f+1 nodes is always the minimum for BFT"      | 3f+1 is the minimum for AUTHENTICATED message (with digital signatures). Without authentication: 5f+1 nodes are required (Lamport's original result). Modern BFT protocols universally use digital signatures to achieve 3f+1.                                                                                                  |
| "Crash-stop and fail-stop are the same"         | Fail-stop is a STRONGER assumption: the node stops AND other nodes are guaranteed to detect the stop (via a reliable failure detector). Crash-stop doesn't guarantee detection. Real systems use timeouts which may incorrectly suspect a live node (false positive) — this is why failure detectors are imperfect in practice. |
| "Omission failures are always handled by Raft"  | Raft handles complete omission (dropped messages) via retransmission and timeouts. But partial omission (node drops messages to some peers but not others) can create a "partial partition" — Raft's leader may still receive heartbeats from enough nodes to maintain leadership while being partitioned from some followers.  |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Hardware-Level Byzantine via Memory Corruption**

**Symptom:** One node in a Raft cluster starts producing incorrect checksum values for stored data. Other nodes receive replication data and accept it (Raft doesn't verify application-layer checksums by default). The corrupted data is committed to the cluster. Corruption spreads to all replicas.
**Root Cause:** ECC memory failure or disk sector corruption causes the node to read/send corrupted data — still valid bytes, just wrong content. This is Byzantine at the data layer even though Raft's message framing is correct. Raft has no mechanism to detect that the replicated data content is wrong.
**Diagnostic:**

```bash
# Check hardware ECC errors:
edac-util --status  # Linux ECC memory errors
# If showing single-bit or multi-bit errors: ECC failure

# Check disk health:
smartctl -a /dev/sda | grep -E "Reallocated|Pending|Uncorrectable"
# Non-zero Reallocated/Pending sectors = storage corruption risk

# Application-layer checksum verification:
# etcd uses CRC32 for WAL entries:
etcdutl check --data-dir /var/lib/etcd
# CRC mismatch = data corruption detected
```

**Fix:**
BAD: Relying solely on Raft's message-level integrity (CRC of the Raft message frame).
GOOD: Add application-layer content hashing: each log entry includes SHA-256 of the payload. All replicas verify the hash after applying. Mismatch → alert and remove node from cluster. Use ECC memory in production hardware (mandatory for consensus node hardware).
**Prevention:** Hardware requirements for Raft nodes: ECC memory (critical), redundant power, enterprise SSD with end-to-end data integrity (T10 DIF). Annual "chaos day" where disks are tested for silent data corruption.

**Failure Mode 2: Timing Failure via GC-Induced False Leader Suspicion**

**Symptom:** A Raft leader experiences a 2-second GC pause. Followers declare the leader dead (election timeout = 1 second). New leader elected. Old leader resumes, discovers it's been replaced (higher term). Steps down. Frequent leader elections from GC pauses cause write stalls every few minutes.
**Root Cause:** GC stop-the-world pause > election timeout. The GC pause is a timing failure: the leader is not crashed (crash-stop), it just can't send messages on time. Raft correctly handles this (elects new leader) but frequent occurrences cause availability issues.
**Diagnostic:**

```bash
# Check JVM GC pause durations:
java -Xlog:gc*:file=gc.log:time,uptime
grep "Pause Full\|Pause Young" gc.log | \
  awk '{print $NF}' | sort -n | tail -10
# If any pause > election_timeout_ms: will cause leader rotation

# Check etcd leader changes:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_ENDPOINTS \
  endpoint status --write-out=table
# Or: Prometheus: etcd_server_leader_changes_seen_total
# If > 1 per hour: investigate GC pauses or network issues
```

**Fix:**
BAD: JVM with CMS/G1GC as etcd node (long GC pauses).
GOOD: Use Go-based etcd (no JVM GC). If Java Raft node: use ZGC or Shenandoah (< 10ms pauses). Or: increase election timeout to 10× P99 GC pause. ZGC configuration: `java -XX:+UseZGC -Xmx4g`.
**Prevention:** P99 GC pause < 1/10 of election timeout. Monitor GC pause histogram. Kubernetes etcd: always use official Go-based etcd, not JVM reimplementations.

**Failure Mode 3: Security - Byzantine Attack via Compromised Peer Node**

**Symptom:** An attacker gains root access to one etcd node. They modify the etcd binary to send conflicting values to different followers during specific time windows — targeting financial transaction records. The cluster appears healthy. Writes appear to succeed. But specific keys have different values on different nodes.
**Root Cause:** One compromised node (Byzantine behavior) in a 3-node cluster. Raft provides no defense against a Byzantine leader. If the compromised node becomes leader: it can commit different values to different followers by sending conflicting AppendEntries.
**Diagnostic:**

```bash
# Detect Byzantine data divergence:
# Compare data hashes across all etcd nodes:
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_EP1 \
  endpoint hashkv 0 --write-out=json | jq '.[].HashKV.hash'
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_EP2 \
  endpoint hashkv 0 --write-out=json | jq '.[].HashKV.hash'
ETCDCTL_API=3 etcdctl --endpoints=$ETCD_EP3 \
  endpoint hashkv 0 --write-out=json | jq '.[].HashKV.hash'
# If hashes differ at the same revision: Byzantine divergence
# (or bug — investigate both)
```

**Fix:**
BAD: Relying on Raft alone for security against compromised nodes.
GOOD: (1) Container isolation + SELinux/AppArmor on etcd nodes. (2) Read-only container root filesystem (etcd only writes to data dir). (3) Host-based IDS (OSSEC, Falco) detecting binary modification. (4) For truly Byzantine-threat environments: migrate to BFT protocol (Hyperledger Fabric for permissioned chains). (5) Network-level monitoring: unusual inter-node traffic patterns.
**Prevention:** Treat etcd nodes as security-critical infrastructure. Same controls as HSMs: hardware attestation, immutable OS (CoreOS), zero-trust network access. Kubernetes: control plane node isolation with separate VPCs/subnets.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-022 - CAP Theorem (failure models and the CAP theorem are tightly coupled — partitions are a specific failure mode)
- DST-046 - Raft (Raft is the most widely deployed crash-recovery protocol — understand what it handles before what it doesn't)

**Builds On This (learn these next):**

- DST-015 - Two-Phase Commit (2PC assumes crash-recovery model — coordinator crash is the critical failure case)
- DST-017 - Three-Phase Commit (3PC improves 2PC's crash handling in crash-recovery model)

**Alternatives / Comparisons:**

- DST-046 - Raft (crash-recovery solution)
- DST-047 - Paxos (crash-recovery solution, same failure model as Raft)
- DST-015 - Two-Phase Commit (crash-recovery atomic commitment protocol)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Taxonomy of how nodes deviate  |
|                  | from correct behavior          |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Protocol/node-count mismatch   |
|                  | with actual failure behavior   |
+------------------+--------------------------------+
| KEY INSIGHT      | Byzantine ≠ "worse crash" —    |
|                  | it's an undetectable adversary |
|                  | requiring 3f+1 nodes, not 2f+1 |
+------------------+--------------------------------+
| USE WHEN         | Choosing consensus protocol or |
|                  | determining node count         |
+------------------+--------------------------------+
| AVOID WHEN       | N/A — always apply failure     |
|                  | model analysis before design   |
+------------------+--------------------------------+
| TRADE-OFF        | Byzantine tolerance: 3f+1 and  |
|                  | O(n²) messages vs 2f+1 O(n)    |
+------------------+--------------------------------+
| ONE-LINER        | Crash: silent → 2f+1 nodes.    |
|                  | Byzantine: deceptive → 3f+1    |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-015 Two-Phase Commit,      |
|                  | DST-046 Raft                   |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Crash-stop: node halts permanently (2f+1 nodes, Raft/Paxos). Byzantine: node sends wrong messages (3f+1 nodes, PBFT/Tendermint). Choosing the wrong model = correctness violation.
2. Byzantine failures are often undetectable — the faulty node still sends messages, just wrong ones. You need cryptographic signing or BFT protocols to detect them.
3. Hardware bugs (memory corruption, NIC firmware) can cause Byzantine behavior in systems designed for crash-stop only. mTLS prevents unauthorized injection but not compromised-legitimate-node Byzantine behavior.

**Interview one-liner:**
"Distributed failure modes range from crash-stop (node halts) through crash-recovery, omission, timing, to Byzantine (arbitrary behavior). The critical design choice: crash-stop requires 2f+1 nodes and crash-recovery protocols (Raft, Paxos). Byzantine requires 3f+1 nodes and BFT protocols (PBFT, Tendermint) because Byzantine nodes can collude within any quorum of size 2f+1. Raft provides zero protection against Byzantine failures — using Raft where Byzantine behavior is possible is a correctness violation."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Name your threat model explicitly before choosing your defense. Every system has an implicit failure model — either the designer chose it, or it was chosen by default (usually optimistic/crash-stop). Making the failure model explicit forces three questions: (1) What failure modes am I actually protecting against? (2) Does my protocol handle those modes? (3) What failure modes am I NOT protecting against, and what is the acceptable risk? Implicit failure models lead to systems that fail in unexpected ways; explicit ones fail only in anticipated ways.

**Where else this pattern appears:**

- **RAID levels and disk failure modes:** RAID 1 (mirroring) handles crash-stop disk failure (disk stops responding). RAID 5 handles 1 disk crash-stop. But "silent data corruption" (disk reads wrong data without error) is Byzantine — the disk returns data but it's wrong. RAID 6 adds another parity disk for double crash-stop protection but still doesn't detect silent corruption. ZFS/BTRFS checksums every block (application-layer integrity) — this is the storage equivalent of adding cryptographic signatures to handle Byzantine disk failures. Same taxonomy: crash-stop → RAID, Byzantine → checksums.
- **Network security models (zero-trust):** Traditional perimeter security assumes: "internal network = trusted, external = untrusted" — a crash-stop-like model (outsiders are excluded, insiders are trusted). Zero-trust security assumes: "any node can be compromised" — a Byzantine model (any device can be an adversary). Zero-trust requires: multi-factor authentication, device attestation, encrypted communication between all internal services (same as BFT requiring cryptographic signing for all messages). The architectural shift from perimeter to zero-trust IS the shift from crash-stop to Byzantine failure model.
- **Software testing strategy:** Unit tests assume crash-stop bugs (function throws exception or returns wrong value — detected). Fuzz testing exposes Byzantine bugs (unexpected input causes function to silently return wrong value — not throwing, just wrong). Property-based testing and formal verification address Byzantine correctness — the function must be correct for ALL inputs, not just the tested ones. The failure mode taxonomy maps: unit testing → crash-stop, property-based → Byzantine.

---

### 💡 The Surprising Truth

The Byzantine Generals Problem (1982) was solved theoretically decades before being solved in practice. Lamport, Shostak, and Pease proved Byzantine fault tolerance is achievable with 3f+1 nodes in 1982. But the first PRACTICAL Byzantine fault-tolerant system — Castro and Liskov's PBFT — wasn't published until 1999, and wasn't widely deployed until blockchain emerged around 2010. The 17-year gap between theoretical proof and practical deployment reveals a profound truth about Byzantine fault tolerance: it was too expensive to be worth implementing in normal infrastructure. PBFT requires O(n²) messages — 10 nodes × 10 nodes = 100 messages per consensus round. At f=1 (3f+1=4 nodes), Byzantine consensus requires 4 nodes and 16 messages per round. At f=33 (3f+1=100 nodes), it requires 10,000 messages per round — unusable at scale. Bitcoin's Proof of Work solved Byzantine consensus at internet scale (millions of nodes) not by reducing messages but by making Byzantine behavior ECONOMICALLY irrational (it costs more to attack than to participate honestly). The surprising truth: the mathematically optimal solution to Byzantine fault tolerance (PBFT, 3f+1 nodes) was replaced in practice by an economically optimal solution (PoW, making attacks unprofitable) — distributed systems mathematics yielded to economics.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** The FLP impossibility theorem proves that in a fully asynchronous network with even one possible crash-stop failure, no deterministic algorithm can guarantee consensus termination. Raft "violates" FLP by using timeouts (partial synchrony assumption). If your network is genuinely asynchronous (unbounded message delays, no clock), what happens to Raft's correctness? Does it become UNSAFE (violates safety invariant) or LIVE (stops making progress)? Explain using the definition of Raft's safety invariant.
_Hint:_ Raft's safety invariant: "if an entry is committed in term T, it will be present in the logs of all future leaders." This invariant doesn't depend on timing — it depends only on quorum intersection. Raft's SAFETY holds even in fully asynchronous networks. Raft's LIVENESS (eventually elects a leader, eventually commits) requires bounded message delays (partial synchrony). Without bounded delays: leaders keep timing out, elections keep failing, no progress. Safe but not live. FLP says: you can have safety OR liveness, not both, in truly async networks. Raft chooses: safety always, liveness under partial synchrony. What does this mean for a Raft cluster experiencing a network congestion event that delays messages for 60 seconds?

**Q2 (C - Design Trade-off):** You are designing a distributed payment processing system. Payments involve: (1) deduct from sender account, (2) credit receiver account. You must choose between Raft (crash-recovery, 2f+1 nodes) and PBFT (Byzantine, 3f+1 nodes). What is the threat model that would justify PBFT over Raft for payment processing? Under what conditions is Raft sufficient, and under what conditions does Byzantine fault tolerance become necessary?
_Hint:_ Raft is sufficient if: all nodes are operated by the same organization (or trusted organizations), hardware integrity is maintained (ECC memory, storage integrity), and the attack surface is external (not from within the cluster). PBFT is necessary if: nodes are operated by different organizations with conflicting interests (multi-bank consortium), insider threat is assumed (a compromised employee could modify a node's behavior), or hardware attacks are part of the threat model. For a single-bank internal payment system: Raft is sufficient. For a multi-bank DLT (distributed ledger technology): PBFT or threshold signatures are necessary.

**Q3 (D - Root Cause):** A 5-node etcd cluster experiences a mysterious intermittent failure: every few days, one node's data diverges from the others for about 30 seconds, then re-syncs. During the divergence window: reads from that node return stale data. No errors in logs. The node's hardware is healthy (ECC shows no errors). The network shows no drops. What failure mode is this, and what are the 3 most likely root causes given that crash-stop and Byzantine are ruled out by the symptoms?
_Hint:_ The node continues operating (not crash-stop). No hardware errors. The data diverges and then RE-SYNCS (not permanent corruption = not Byzantine in the pure sense). This pattern (diverge + resync) suggests: (A) timing failure — the node gets temporarily "behind" in applying committed entries (apply backlog). The node's commitIndex advances but appliedIndex lags. Reads from this node return from the state machine at appliedIndex, not commitIndex. (B) GC pause in a JVM-based client library connecting to this etcd node — the client library's lease renewal fails, and the client reconnects to a different node (returning different data). (C) etcd read from a follower with non-linearizable reads (no ReadIndex check) — the follower's in-memory data lags the leader's committed state.

