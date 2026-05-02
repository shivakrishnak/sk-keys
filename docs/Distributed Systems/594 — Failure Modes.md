---
layout: default
title: "Failure Modes (Crash, Byzantine)"
parent: "Distributed Systems"
nav_order: 594
permalink: /distributed-systems/failure-modes/
number: "0594"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Systems Fundamentals, Consensus
used_by: Fault-tolerant system design, Blockchain, BFT protocols
related: Byzantine Fault Tolerance, FLP Impossibility, Raft, Paxos
tags:
  - failure-modes
  - crash-failure
  - byzantine
  - distributed-systems
  - advanced
---

# 594 — Failure Modes (Crash, Byzantine)

⚡ TL;DR — Distributed system failure modes form a hierarchy from benign to malicious: Crash-stop (node halts, never sends another message), Crash-recovery (node halts and may rejoin), Omission (node drops some messages), Timing (messages arrive too late), Byzantine (node behaves arbitrarily — may lie, send conflicting messages, or collude). Each mode requires stronger (and costlier) protocols to tolerate: Raft handles crash-stop; Byzantine Fault Tolerance (PBFT, Tendermint) handles Byzantine. Designing for the wrong failure model leaves dangerous gaps.

┌──────────────────────────────────────────────────────────────────────────┐
│ #594         │ Category: Distributed Systems      │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ Consensus, Distributed Systems      │                      │
│ Used by:     │ BFT protocols, Blockchain           │                      │
│ Related:     │ BFT, FLP Impossibility, Raft        │                      │
└──────────────────────────────────────────────────────────────────────────┘

---

### 🔥 The Problem This Solves

A network engineer designs a fault-tolerant system assuming nodes either work correctly or crash. The system is deployed. An attacker compromises one node and makes it send conflicting version numbers to different replicas — splitting the cluster's view of the data without a crash. The Raft-based consensus protocol has no defense against this: it assumes all messages are honest. Result: data corruption. Failure mode taxonomy exists to define WHICH failures you design for, and which protocols are needed.

---

### 📘 Textbook Definition

**Failure mode hierarchy (most to least benign):**

1. **Crash-stop (fail-stop):** Node halts permanently, sends no further messages. Other nodes detect via timeout. Easiest to handle: absence = failure.

2. **Crash-recovery:** Node halts, loses volatile state, but may restart. Raft handles this: crashed node rejoins and catches up via log replication. Persistent storage required.

3. **Omission failure:** Node is alive but drops some messages (send omission or receive omission). Network layer issues (packet loss, buffer overflow). Protocols handle via retries + ACKs.

4. **Timing failure:** Node sends messages but too slowly (violates timing assumptions). Heartbeat timeouts trigger spurious leader re-elections.

5. **Byzantine failure:** Node behaves arbitrarily — sends incorrect data, sends different data to different peers, selectively drops messages, colludes with other Byzantine nodes. Requires BFT protocols; needs 3f+1 nodes to tolerate f Byzantine failures.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The more arbitrarily a node can fail, the more expensive (more replicas, more message rounds) the protocol needed to tolerate it.

**Analogy:** Failure modes are like employee behavior categories: Crash-stop = employee quits without notice. Crash-recovery = employee temporarily passes out, wakes up, forgets short-term memory. Omission = employee forgets to relay some messages. Timing = employee delivers all messages but always late. Byzantine = employee actively sabotages — lies to some colleagues, tells different stories to management vs. colleagues.  Each category requires increasingly complex HR policies.

---

### 🔩 First Principles Explanation

```
FAILURE MODE TAXONOMY:

  CRASH-STOP:
  │ Node halts permanently. From others' perspective: stops responding.
  │ Detection: heartbeat timeout.
  │ Raft tolerance: 2f+1 nodes survive f crash-stops.
  │ Example: hardware failure, OOM kill.
  
  CRASH-RECOVERY:
  │ Node halts, state may be partially saved, node restarts.
  │ Raft: persistent state (currentTerm, votedFor, log) written to disk before responding.
  │ After restart: loads state, rejoins as follower, catches up.
  │ Example: server reboot, application crash + restart.
  
  OMISSION:
  │ Node is alive but loses messages (send or receive).
  │ From Raft's perspective: acts like a slow crash.
  │ TCP retransmits handle most network-level omissions.
  │ Example: network congestion causing packet drops.
  
  TIMING FAILURE:
  │ Messages eventually arrive but violate timing assumptions (heartbeat timeout).
  │ Effect on Raft: spurious elections (follower times out, triggers election).
  │ Tuning: election timeout must be >> network round-trip time.
  
  BYZANTINE:
  │ Node can do ANYTHING: send wrong checksums, lie about log entries, send
  │ different values to different peers simultaneously, vote twice.
  │ Raft CANNOT tolerate Byzantine nodes (a Byzantine node can vote twice,
  │ causing two "leaders" to be elected simultaneously).
  │ BFT requires 3f+1 nodes for f Byzantine failures:
  │   - f Byzantine nodes can send conflicting messages
  │   - We need 2f+1 honest nodes to outvote them
  │   - Total minimum: 3f+1
```

---

### 🧠 Mental Model / Analogy

> Failure modes as courtroom analogy: Crash-stop = witness dies before testifying (easy: dismiss). Crash-recovery = witness faints, revives with partial memory (handle gently). Omission = witness doesn't receive all question papers (resend). Timing = witness delivers testimony after the verdict (protocol must extend deadlines). Byzantine = witness actively lies and tells conflicting stories to judge vs. jury (require 2/3 majority agreement across all testimonies to convict — the Byzantine Generals Problem).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Failures spectrum: crash-stop (easy) → crash-recovery → omission → timing → Byzantine (hardest). Each requires stronger protocols. Most enterprise systems (Raft, ZooKeeper, Paxos) only handle crash-recovery. Blockchains (Tendermint, PBFT) handle Byzantine.

**Level 2:** The fundamental cost of BFT: 3f+1 nodes for f failures vs. 2f+1 for crash-only. For f=1: BFT needs 4 nodes, Raft needs 3. For f=2: BFT needs 7, Raft needs 5. Plus BFT requires more message rounds (PBFT = 3 phases: pre-prepare, prepare, commit). At f=1 with BFT: ~O(n²) messages vs O(n) for Raft. Massive performance difference.

**Level 3:** In practice, Byzantine failures in datacenter-internal systems are extremely rare (hardware ECC handles bit flip; software bugs crash rather than produce arbitrary output). Byzantine fault tolerance is reserved for: (a) blockchain/public consensus where participants don't trust each other, (b) safety-critical systems (aerospace, nuclear), (c) heterogeneous hardware/software environments where different vendor implementations might behave differently. For enterprise microservices: crash-recovery + crash-stop is sufficient.

**Level 4:** The "Byzantine army" has modern interpretations: (a) software bugs that cause non-crash incorrect behavior (memory corruption sending wrong values — rare but possible), (b) malicious insiders or compromised cloud nodes, (c) hardware faults producing incorrect-but-non-crashing behavior (cosmic rays, Rowhammer). For these, the formal BFT model is the only defense. Authenticated Byzantine agreement (using digital signatures) is cheaper: f+1 nodes need to sign a decision before it's accepted, reducing to 2f+1 nodes total (but requires PKI and signature verification overhead).

---

### ⚙️ How It Works (Mechanism)

```
PBFT (Practical Byzantine Fault Tolerance) — protocol for f Byzantine nodes in 3f+1 total:

  3 phases for a client request:
  
  1. PRE-PREPARE (Primary → Replicas):
     Primary assigns sequence number, broadcasts (SEQ=42, REQUEST=client_op, VIEW=3)
     
  2. PREPARE (Replicas → All):
     Each replica validates, broadcasts PREPARE(SEQ=42, DIGEST=hash(op), VIEW=3)
     Replica waits for 2f PREPARE messages matching its own → "prepared"
  
  3. COMMIT (All → All):
     Each "prepared" replica broadcasts COMMIT(SEQ=42, VIEW=3)
     Replica waits for 2f+1 COMMIT messages → "committed" → execute
  
  WHY 2f+1 COMMITS?
  n = 3f+1 nodes total. f can be Byzantine (lie).
  We need 2f+1 votes; f of those could be Byzantine.
  At least f+1 are honest → sufficient honest agreement to proceed.
  Any quorum of 2f+1 intersects by at least f+1 honest nodes.
  ∴ A committed decision was witnessed by at least f+1 honest nodes. ✓
  
  COMPLEXITY: O(n²) prepare messages per request. At n=100: 10,000 messages per op.
  Practical limit: ~100 nodes max before network overhead dominates.
```

---

### 💻 Code Example

```java
// Resilience4j: handling crash-recovery failure mode via circuit breaker
// (Byzantine failure handling is a protocol concern, not application-level)

@Service
public class InventoryService {

    // Circuit breaker handles crash/timing failures in dependent services
    // Opens after 50% failure rate over 10 calls → fallback behavior
    @CircuitBreaker(name = "inventoryService", fallbackMethod = "getInventoryFallback")
    @Retry(name = "inventoryService")
    @TimeLimiter(name = "inventoryService")
    public CompletableFuture<Integer> getInventory(String productId) {
        // This call may encounter crash-stop (remote service down),
        // timing failure (timeout), or omission (connection reset)
        return CompletableFuture.supplyAsync(() ->
            restTemplate.getForObject("/inventory/{id}", Integer.class, productId));
    }

    // Fallback for crash/timing failures: return cached/default value
    public CompletableFuture<Integer> getInventoryFallback(String productId, Exception e) {
        log.warn("Inventory service failure for {}: {}", productId, e.getMessage());
        // Degrade gracefully: return cached or conservative estimate
        return CompletableFuture.completedFuture(
            inventoryCache.getOrDefault(productId, 0));
    }
}

// For Byzantine fault handling in microservices (internal trust model):
// Add response validation — detect incorrect responses from compromised services
@Service
public class ValidatedServiceProxy {

    public InventoryResponse callWithValidation(String productId) {
        // Query multiple instances and compare responses (minority-vote approach)
        List<InventoryResponse> responses = instances.stream()
            .map(inst -> inst.getInventory(productId))
            .collect(Collectors.toList());
        
        // Return majority-agreed response (simplistic BFT for internal services)
        return responses.stream()
            .collect(Collectors.groupingBy(r -> r, Collectors.counting()))
            .entrySet().stream()
            .max(Map.Entry.comparingByValue())
            .map(Map.Entry::getKey)
            .orElseThrow(() -> new IllegalStateException("No majority response"));
    }
}
```

---

### ⚖️ Comparison Table

| Failure Mode | Protocol Needed | Replica Count (f=1) | Example |
|---|---|---|---|
| **Crash-stop** | Paxos/Raft | 3 nodes (2f+1) | Hardware failure |
| **Crash-recovery** | Raft + persistent log | 3 nodes (2f+1) | Server reboot |
| **Omission** | Raft + retries/timeouts | 3 nodes | Network packet loss |
| **Timing** | Raft + tuned timeouts | 3+ nodes | Network congestion |
| **Byzantine** | PBFT/Tendermint | 4 nodes (3f+1) | Compromised node |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ CRASH-STOP   │ Permanent halt. 2f+1 nodes (Raft)            │
│ CRASH-RECOV. │ Halt + restart. Raft with persistent log     │
│ OMISSION     │ Message loss. TCP retries, Raft handles       │
│ TIMING       │ Too slow. Tune heartbeat/election timeouts    │
│ BYZANTINE    │ Arbitrary/malicious. 3f+1 nodes (PBFT)       │
│ COST         │ BFT = O(n²) msgs + 1.5x more replicas       │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A financial messaging system needs to tolerate exactly 1 failure. The threat model includes: (a) random hardware failure, (b) software bug causing incorrect (non-crash) behavior, (c) insider threat compromising one node. (1) Which failure modes cover each threat? (2) If you design for crash-recovery only (Raft, 3 nodes), which threats remain unaddressed? (3) Designing for Byzantine (PBFT, 4 nodes) covers all three but at what cost? (4) A hybrid approach: use Raft for normal operation + cryptographic checksums on every replicated entry to detect Byzantine data corruption. Does this achieve Byzantine fault tolerance? What edge cases remain?
