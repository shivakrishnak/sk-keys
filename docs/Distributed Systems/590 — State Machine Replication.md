---
layout: default
title: "State Machine Replication"
parent: "Distributed Systems"
nav_order: 590
permalink: /distributed-systems/state-machine-replication/
number: "590"
category: Distributed Systems
difficulty: ★★★
depends_on: "Log Replication, Total Order Broadcast"
used_by: "Raft, Paxos, etcd, Distributed Databases"
tags: #advanced, #distributed, #consensus, #replication, #correctness
---

# 590 — State Machine Replication

`#advanced` `#distributed` `#consensus` `#replication` `#correctness`

⚡ TL;DR — **State Machine Replication (SMR)** is the theorem that any deterministic state machine replicated across N nodes — given they execute the same commands in the same order — produces identical state, making the cluster a fault-tolerant single logical system.

| #590 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Log Replication, Total Order Broadcast | |
| **Used by:** | Raft, Paxos, etcd, Distributed Databases | |

---

### 📘 Textbook Definition

**State Machine Replication (SMR)** is the foundational approach to building fault-tolerant distributed systems, formalised by Lamport (1978) and popularised by Schneider (1990 — "Implementing Fault-Tolerant Services Using the State Machine Approach"). The approach rests on two properties: (1) **Determinism**: the state machine transitions are deterministic — given the same input state and command, the output state is always identical (no randomness, no time-based behavior, no side effects); (2) **Total Order**: all replicas execute the same sequence of commands in the same order. If both properties hold: all replicas starting from the same initial state will reach exactly the same state after any sequence of commands. SMR requires solving **Total Order Broadcast** (also called Atomic Broadcast) — delivering the same messages to all nodes in the same order, which is equivalent in difficulty to Consensus. In practice: Raft's replicated log is a Total Order Broadcast implementation; once a command is committed (log entry applied), all nodes execute it in log-index order. SMR is the theoretical justification for why systems like etcd, ZooKeeper, CockroachDB, and Spanner work correctly as fault-tolerant services.

---

### 🟢 Simple Definition (Easy)

State Machine Replication: if you have N computers all running the same program (state machine), and they all execute the same instructions in the same order, they all end up with the same data. That's it. The "replicated log" (Raft, Paxos) is just a way to ensure all computers agree on the same sequence of instructions. Once they agree: they independently execute them → identical state everywhere. The system is fault-tolerant because: lose 1 computer → remaining computers have identical state → any one of them can take over.

---

### 🔵 Simple Definition (Elaborated)

The insight: "replicated state" is hard to synchronise (what if two updates conflict?). But "replicated operations on a deterministic state machine" is easy — just ensure everyone applies the same operations in the same order. A deterministic state machine: same input always produces same output (no random(), no System.currentTimeMillis(), no external state). Total order: everyone applies operation #1 first, then #2, then #3 (never #2 before #1 on any node). Result: every node has identical state. This is why Raft/Paxos replicate a LOG (ordered sequence of operations) rather than replicating state directly.

---

### 🔩 First Principles Explanation

**SMR correctness, determinism requirements, and total order broadcast:**

```
STATE MACHINE FORMALISM:

  State machine M:
    S = set of all possible states (e.g., all possible key-value stores)
    Σ = set of possible commands (e.g., SET_x_10, DELETE_y, INCREMENT_z)
    δ: S × Σ → S (transition function: state + command → new state)
    s0 = initial state (same on all replicas, e.g., empty key-value store)
    
  Determinism requirement:
    ∀ s ∈ S, ∀ c ∈ Σ: δ(s, c) is a single, unique result.
    Same state + same command → ALWAYS same new state.
    
  Total order requirement:
    ∀ replicas R1, R2: if R1 applies commands [c1, c2, c3, ..., cn]
                        and R2 applies commands [c1, c2, c3, ..., cn]
                        in the SAME ORDER: δ^n(s0) is identical on both.

WHY ORDER MATTERS (non-commutativity):

  Commands:
    c1: SET x = 10
    c2: SET x = x * 2
    c3: DELETE x
    
  Order [c1, c2, c3]: s0 → {x=10} → {x=20} → {} = empty store.
  Order [c2, c1, c3]: s0 (x undefined) → c2 fails or x=0 → {x=10} → {} = empty store? Different!
  Order [c3, c1, c2]: s0 → {} (delete noop) → {x=10} → {x=20} ≠ empty store!
  
  Commands are NOT commutative in general.
  Must apply in SAME ORDER on all replicas.

TOTAL ORDER BROADCAST (TOB) = CONSENSUS:

  TOB definition:
    All correct nodes deliver the same set of messages.
    All correct nodes deliver messages in the same order.
    
  TOB is equivalent to Consensus:
    Given TOB: can implement consensus (broadcast proposed value; first delivered = chosen).
    Given Consensus: can implement TOB (agree on (message, sequence_number) for each position).
    
  Raft = TOB implementation:
    Leader assigns sequence number (log index) to each command.
    Commits when quorum ACKs.
    All replicas apply in index order.
    ∴ Raft implements TOB → implements SMR → fault-tolerant state machine.

DETERMINISM REQUIREMENTS (what breaks SMR):

  SAFE (deterministic) operations:
    PUT key=value, GET key, DELETE key — pure key-value operations.
    SQL INSERT, UPDATE with explicit values — deterministic.
    Arithmetic on existing values — deterministic.
    
  UNSAFE (non-deterministic) operations:
    CURRENT_TIMESTAMP / NOW() — different nodes may call at different wall-clock times.
    RANDOM() / UUID() — different values on different nodes.
    OS-level randomness — different.
    Reading external state (HTTP call, file read) — different result on each node.
    
  HOW TO HANDLE NON-DETERMINISM IN SMR:
  
    Option 1: COMPUTE ONCE, REPLICATE RESULT.
      Client generates UUID before sending command.
      Command: INSERT INTO orders (id, ...) VALUES ('550e8400-...', ...).
      UUID is IN the command — same on all replicas.
      Leader does not generate UUID. All replicas insert the same UUID.
      
    Option 2: LEADER GENERATES, REPLICATES.
      Leader generates timestamp/UUID when creating log entry.
      Log entry contains: {index: 5, term: 3, command: INSERT, generated_uuid: '550e...', 
                           generated_ts: 1699283456789}.
      Followers: use generated_uuid and generated_ts from log entry, NOT from their own clocks.
      
      PostgreSQL logical replication: captures row values (not SQL text) to ensure determinism.
      "Row-based replication" vs "statement-based replication".
      Statement: "INSERT INTO t VALUES (NOW())" — different timestamps on each replica!
      Row: "INSERT INTO t VALUES ('2024-01-15 10:30:00.123')" — same value on all.
      
    Option 3: DISALLOW in protocol.
      ZooKeeper: ephemeral nodes tied to session. Session expiry triggers deletion.
      ZooKeeper handles expiry deterministically (not by wall-clock on each node).
      
  REAL BUGS from non-determinism:
    MySQL statement-based replication + stored procedure with RAND() → different replica states.
    Cassandra LWT (lightweight transactions) + client retries without idempotency → duplicate writes.
    Redis Cluster: MULTI/EXEC transaction with RANDOMKEY → different keys selected on each shard.

SMR + SNAPSHOTS (log compaction):

  Problem: log grows unboundedly → slow recovery after restart.
  
  Snapshot approach:
    1. At log index N: take snapshot of full state machine state.
       Snapshot = serialised state_machine.getState() at the point after applying entry N.
    2. Discard log entries 1..N.
    3. Keep snapshot + log[N+1..current].
    
  Recovery from snapshot + log:
    Load snapshot (restores state machine to state at index N).
    Apply log entries N+1 through latest committed.
    State machine: identical to having applied entries 1 through latest from scratch.
    
  Invariant: δ^(snapshot.index+k)(s0) = δ^k(snapshot.state)
    Applying k entries to snapshot state = applying snapshot.index+k entries from initial state.
    
  Raft InstallSnapshot RPC:
    Leader: if nextIndex[f] < snapshot.index → send snapshot to follower (too far behind for log).
    Follower: receives snapshot, installs as state machine state, updates log/commitIndex.
    
  Checkpoint frequency:
    Too frequent: serialisation overhead (snapshot = GB for large state).
    Too infrequent: slow recovery (must replay many log entries).
    etcd default: every 10,000 committed entries.
    CockroachDB: Raft-group-level snapshots triggered when replica is > 8MB behind leader.

BYZANTINE vs CRASH-STOP FAULT TOLERANCE:

  SMR as described tolerates CRASH-STOP failures:
    Nodes fail by stopping. They don't send incorrect/malicious messages.
    N nodes: can tolerate f = ⌊(N-1)/2⌋ failures. N=5: f=2.
    
  Byzantine fault tolerance (BFT): nodes may send INCORRECT messages (buggy or malicious).
    Requires N ≥ 3f + 1 nodes to tolerate f Byzantine failures.
    N=5 tolerates only f=1 Byzantine failure (5 ≥ 3*1 + 1 = 4). Less efficient.
    Algorithms: PBFT (Practical Byzantine Fault Tolerance), Tendermint (blockchain).
    
  Why crash-stop is enough for most systems:
    Internal distributed systems (datacenter): buggy code crashes, doesn't send wrong data.
    External (blockchain): untrusted nodes — BFT required.
    
  Kubernetes (etcd): crash-stop. No Byzantine nodes. etcd uses Raft (crash-stop tolerant).
  Bitcoin: Byzantine. All nodes untrusted. Proof-of-Work as BFT-equivalent.

EXAMPLE: IMPLEMENTING A FAULT-TOLERANT KV STORE VIA SMR:

  Architecture:
    5 Raft nodes. Each node: (log, state machine = HashMap<String, String>).
    State machine transitions: PUT(k,v) → put k in map; GET(k) → return map.get(k); DELETE(k).
    
  Client write (SET x=10):
    → Leader: creates log entry {idx=42, term=3, cmd=PUT("x","10")}.
    → Replicates to 4 followers (waits for 3 ACKs = majority of 5).
    → commitIndex = 42. Applies to state machine: hashMap.put("x", "10").
    → Responds to client: "SET x=10 OK".
    
  All 5 nodes: apply entry 42 = PUT("x","10").
  All 5 nodes: hashMap.get("x") == "10". Identical state.
  
  Client read (GET x) — linearisable:
    → Leader: ReadIndex protocol (confirm still leader via heartbeat to majority).
    → Waits for appliedIndex >= readIndex.
    → Returns hashMap.get("x") = "10".
    
  Node 3 crashes. System has 4 nodes.
    Quorum: 3 of 5 (or 3 of 4 remaining? Still 3 of 5 original — quorum doesn't change).
    Writes: still go to leader, replicated to 2 remaining followers = 3 total = quorum. OK.
    
  Node 4 crashes. System has 3 nodes.
    Quorum: still 3 of 5. System can still write (3 nodes have entry).
    
  Node 5 crashes. System has 2 nodes.
    Quorum: needs 3, has 2. SYSTEM STOPS ACCEPTING WRITES. Returns error.
    Correctness: better to stop than return inconsistent data.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT SMR (ad-hoc replication):
- Inconsistent replicas: different nodes have different state due to unsynchronised updates
- No theoretical guarantee: impossible to reason about correctness
- Split-brain: two nodes diverge independently, reconciliation undefined

WITH SMR:
→ Formal correctness: if deterministic + total order → all nodes identical (proven theorem)
→ Fault tolerance: any quorum of nodes can serve any request (identical state)
→ Design guide: tells engineers exactly what they need to ensure: determinism + ordered log

---

### 🧠 Mental Model / Analogy

> A symphony orchestra performing a piece from a shared score. Every musician (replica) starts from the same initial position (rest). The conductor (leader/log) calls out each note in sequence (total order). Every musician plays the same notes in the same order (determinism). Result: every musician's part produces the same symphony. If 2 musicians can't hear (node failure): remaining musicians still play the same symphony. A musician who rejoined late: plays from where they were (log replay from last checkpoint) → catches up to the same position.

"Musicians playing from shared score" = replicas applying same log entries
"Conductor calling notes in sequence" = leader assigning total order to commands
"Same symphony = same state" = determinism of state machine transitions
"Musician replaying missed notes" = follower catching up via log replay

---

### ⚙️ How It Works (Mechanism)

**ZooKeeper as SMR example:**

```bash
# ZooKeeper is an SMR-based distributed coordination service.
# State machine: a hierarchical namespace (znodes) with reads/writes/watches.
# Backed by ZAB (ZooKeeper Atomic Broadcast) — a Paxos-like TOB protocol.

# All ZooKeeper writes go through the leader (TOB):
$ zkCli.sh -server zk1:2181

# Write (SET operation on state machine):
[zk: zk1:2181(CONNECTED)] create /config/feature-flag "enabled"
Created /config/feature-flag
# ZAB: leader replicates to quorum → all ZK nodes have /config/feature-flag="enabled".

# Read (from any node — all have identical state):
[zk: zk2:2181(CONNECTED)] get /config/feature-flag
enabled
# cZxid = 0x14  ← ZAB transaction ID (equivalent to Raft log index)
# ctime = ...
# mZxid = 0x14  ← last-modified ZAB txn ID
# dataVersion = 0

# Watch (deterministic: ZK guarantees all clients see watches in zxid order):
[zk: zk1:2181(CONNECTED)] get -w /config/feature-flag
# If another client updates: ALL clients with watches on this node are notified.
# Notification order is deterministic (ZAB total order).

# ZAB transaction ID (zxid) = epoch (32 bits) + counter (32 bits).
# epoch: ZAB leader's term (like Raft term).
# counter: monotonically increasing within epoch.
# Analogous to Raft: (term, log_index).

# Check ZAB leader status:
$ echo stat | nc zk1 2181 | grep Mode
Mode: leader
$ echo stat | nc zk2 2181 | grep Mode
Mode: follower
```

---

### 🔄 How It Connects (Mini-Map)

```
Total Order Broadcast (deliver same messages in same order)
        │  (equivalent to)
        ▼
Consensus (agree on one value per slot)
        │  (implements)
        ▼
State Machine Replication ◄──── (you are here)
(determinism + total order → identical state on all nodes)
        │
        ├── Log Replication (the practical mechanism: Raft/ZAB logs implement TOB)
        ├── Raft / Paxos (consensus algorithms that enable SMR)
        └── etcd / ZooKeeper (production systems built as SMR-based coordination services)
```

---

### 💻 Code Example

**Deterministic state machine for SMR (avoiding non-determinism pitfalls):**

```java
// CORRECT: Deterministic state machine for SMR.
// All commands must be deterministic — same input → same output on any replica.

public class DeterministicKVStateMachine {
    
    private final Map<String, String> store = new HashMap<>();
    
    // CORRECT: All values come from the command (generated by client or leader BEFORE replication).
    public void apply(LogEntry entry) {
        switch (entry.getCommandType()) {
            case PUT:
                PutCommand put = (PutCommand) entry.getCommand();
                store.put(put.getKey(), put.getValue()); // Deterministic: value in command.
                break;
                
            case PUT_IF_ABSENT:
                PutIfAbsentCommand cond = (PutIfAbsentCommand) entry.getCommand();
                // version number from command (not generated here):
                store.putIfAbsent(cond.getKey(), cond.getValue());
                break;
                
            case DELETE:
                store.remove(((DeleteCommand) entry.getCommand()).getKey());
                break;
                
            // WRONG: Do NOT do this:
            // case PUT_WITH_TIMESTAMP:
            //     store.put(key, System.currentTimeMillis() + ":" + value);
            //     // System.currentTimeMillis() differs on each replica → NOT deterministic!
                
            // CORRECT version: timestamp must be in the command:
            case PUT_WITH_TIMESTAMP:
                PutWithTimestampCommand ts = (PutWithTimestampCommand) entry.getCommand();
                // ts.getTimestamp() was set by the LEADER when creating the log entry.
                // All replicas use the SAME timestamp from the log entry.
                store.put(ts.getKey(), ts.getTimestamp() + ":" + ts.getValue());
                break;
        }
    }
    
    // LEADER ONLY: command creation with non-deterministic values resolved here (not in apply).
    public LogEntry createCommand(ClientRequest request) {
        switch (request.getType()) {
            case PUT_WITH_TIMESTAMP:
                // Leader generates timestamp ONCE. Embeds in log entry.
                // Followers use this timestamp from log → deterministic.
                return new LogEntry(new PutWithTimestampCommand(
                    request.getKey(),
                    request.getValue(),
                    System.currentTimeMillis() // Generated once by leader, NOT by each follower.
                ));
            case PUT_WITH_UUID:
                return new LogEntry(new PutCommand(
                    request.getKey(),
                    UUID.randomUUID().toString() // Leader generates UUID. Followers use same.
                ));
            default:
                return new LogEntry(request.toCommand());
        }
    }
    
    // Snapshot: take a point-in-time snapshot of the state machine.
    public byte[] takeSnapshot() {
        return serialize(store); // Full state serialised to bytes.
    }
    
    // Restore from snapshot:
    public void restoreSnapshot(byte[] snapshotData) {
        store.clear();
        store.putAll(deserialize(snapshotData));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SMR requires all nodes to be online simultaneously | SMR requires a quorum (majority) to commit entries, but individual nodes can be offline. Offline nodes miss committed entries. When they rejoin: they receive missed entries (via log replication) or a snapshot + recent entries (if they missed too much). After catching up: their state is identical to the rest of the cluster. SMR tolerates ⌊N/2⌋ simultaneous node failures without losing availability |
| SMR guarantees consistency even with non-deterministic state machines | SMR guarantees consistency ONLY for deterministic state machines. Non-determinism (random(), clock calls) produces divergent states even with identical log entries. This is a common implementation bug: SQL stored procedures with NOW() in statement-based replication produce replica divergence. Always use row-based replication (MySQL), WAL-level replication (PostgreSQL), or embed generated values in the log entry (Raft/ZooKeeper) |
| SMR and primary-backup replication are the same | Different approaches. SMR: every replica independently applies all commands and maintains identical active state. Primary-backup: only primary executes commands; backup receives state deltas. In SMR: any node can become the new primary immediately (same state). In primary-backup: backup must receive state transfer from primary before serving. SMR is more complex (all replicas maintain full state) but provides faster failover |
| Total Order Broadcast is easier than Consensus | They are equivalent in difficulty (proven). Any TOB implementation solves Consensus and vice versa. FLP Impossibility applies to both. In practice: Raft and Paxos solve both simultaneously — the replicated log is a TOB implementation, and each log slot is a Consensus instance. Systems that claim TOB without solving Consensus (e.g., simple ordering via sequence numbers) are not safe under network partitions |

---

### 🔥 Pitfalls in Production

**Non-deterministic state machine causing replica divergence:**

```
PROBLEM: Production etcd cluster: node 3 starts returning different values than nodes 1 and 2
         for the same key. Investigation: a custom etcd plugin was modifying values using 
         time.Now() during the apply phase (in the state machine, not in the log entry creation).
         time.Now() differs by nanoseconds on each node → different values applied → divergence.
         
  Node 1 applies entry 500: PUT /config/version = fmt.Sprintf("%s-%d", value, time.Now().UnixNano())
  Node 1 result: /config/version = "v1.2-1699283456789012300"
  Node 3 applies entry 500: PUT /config/version = fmt.Sprintf("%s-%d", value, time.Now().UnixNano())
  Node 3 result: /config/version = "v1.2-1699283456789015100"  ← 2800ns difference!
  
  Different values for same key on different nodes = SMR violation.
  Kubernetes reads from etcd: different nodes return different version strings.
  Helm chart deployments: version mismatch → Helm thinks chart is "modified" → spurious upgrades.

BAD: Non-deterministic value generation in apply():
  func (sm *StateMachine) Apply(entry *raftpb.Entry) {
      var cmd Command
      proto.Unmarshal(entry.Data, &cmd)
      if cmd.Type == "PUT_WITH_VERSION" {
          // BUG: time.Now() called during apply → different on each replica!
          versionedValue := fmt.Sprintf("%s-%d", cmd.Value, time.Now().UnixNano())
          sm.store[cmd.Key] = versionedValue
      }
  }

FIX: Generate non-deterministic values in command creation (leader only), embed in log entry:
  // At command creation time (LEADER, before replication):
  func (leader *RaftLeader) CreatePutCommand(key, value string) Command {
      return Command{
          Type:      "PUT_WITH_VERSION",
          Key:       key,
          Value:     value,
          Timestamp: time.Now().UnixNano(), // Generated ONCE by leader, embedded in log entry.
          RequestID: uuid.New().String(),   // For idempotency.
      }
  }
  
  // In apply() — uses value from log entry (identical on all replicas):
  func (sm *StateMachine) Apply(entry *raftpb.Entry) {
      var cmd Command
      proto.Unmarshal(entry.Data, &cmd)
      if cmd.Type == "PUT_WITH_VERSION" {
          // Uses cmd.Timestamp — set by leader, same on all replicas.
          versionedValue := fmt.Sprintf("%s-%d", cmd.Value, cmd.Timestamp)
          sm.store[cmd.Key] = versionedValue
          // Now: ALL replicas produce identical versionedValue. SMR maintained.
      }
  }
  
  // Detection: periodic hash comparison between replicas.
  // ZooKeeper: computes a hash of the namespace state, alerts if hashes diverge.
  // etcd: compare key-value hashes between nodes during health checks.
```

---

### 🔗 Related Keywords

- `Log Replication` — the practical mechanism implementing Total Order Broadcast for SMR
- `Raft` — consensus algorithm that provides the Total Order Broadcast needed for SMR
- `Total Order and Partial Order` — SMR requires total order on commands; partial order is insufficient
- `Consensus` — equivalent to Total Order Broadcast; solving one solves the other

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Deterministic SM + same commands in same  │
│              │ order → all replicas reach identical state│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fault-tolerant services: config stores,  │
│              │ lock services, distributed DBs — anything │
│              │ requiring strong consistency + HA         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ State machine has inherent non-determinism│
│              │ (CRDT-based or eventually consistent      │
│              │ systems: use different replication model) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Orchestra: same score, same order →      │
│              │  same symphony on every musician."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Log Replication → Raft → Total Order      │
│              │ Broadcast → Quorum → Consensus            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are building an SMR-based distributed cache using Raft. A client requests "GET x" — should this be a read command that goes through the Raft log (becomes a log entry, replicated to quorum, then applied)? What would be the performance impact? What alternative does Raft's ReadIndex protocol provide, and what safety guarantee does it maintain without adding a log entry?

**Q2.** A state machine implements a counter: `INCREMENT(key)` adds 1, `GET(key)` returns current value. This seems deterministic — INCREMENT always adds exactly 1. However, two clients simultaneously issue `INCREMENT(x)`. Both reach the leader. The leader assigns log indices 100 and 101. Both are committed. After applying: counter = initial + 2. Is this correct SMR behavior? Now consider: what if the state machine was "increment by a random amount between 1-10"? How would you fix this to maintain SMR correctness?
