---
layout: default
title: "Log Replication"
parent: "Distributed Systems"
nav_order: 589
permalink: /distributed-systems/log-replication/
number: "589"
category: Distributed Systems
difficulty: ★★★
depends_on: "Raft, Replication Strategies"
used_by: "etcd, CockroachDB, Kafka, PostgreSQL WAL"
tags: #advanced, #distributed, #replication, #raft, #durability
---

# 589 — Log Replication

`#advanced` `#distributed` `#replication` `#raft` `#durability`

⚡ TL;DR — **Log Replication** is the mechanism where a leader appends ordered entries to a replicated log, commits them when a quorum ACKs, and all nodes apply the same sequence to reach identical state machine output.

| #589 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Raft, Replication Strategies | |
| **Used by:** | etcd, CockroachDB, Kafka, PostgreSQL WAL | |

---

### 📘 Textbook Definition

**Log Replication** is the core mechanism of replicated state machines: a leader receives commands from clients, appends them as entries to a persistent, ordered log, broadcasts AppendEntries RPCs to followers, and marks entries as "committed" once a quorum of nodes have durably stored them. Committed entries are then applied to each node's local state machine in log-index order, guaranteeing that all nodes execute the same sequence of commands and reach identical states. The replicated log provides: **durability** (entries survive node restarts via disk persistence), **ordering** (index is a total order), **consistency** (log matching property: equal (index, term) implies identical preceding log), and **fault tolerance** (committed entries survive up to ⌊N/2⌋ node failures). In Raft: the AppendEntries RPC carries (prevLogIndex, prevLogTerm) for consistency checks, ensuring follower logs are identical to leader's up to the insertion point before appending. In Apache Kafka: the log is the fundamental data structure — producers append records to a partition log; brokers replicate logs across ISR (In-Sync Replicas); consumers read committed records. PostgreSQL WAL (Write-Ahead Log): changes written to WAL before applying to data files; WAL shipped to standbys for streaming replication.

---

### 🟢 Simple Definition (Easy)

Log replication: the leader keeps an ordered list (the "log") of all operations. Every new operation is appended to the log. The leader sends the log entry to all followers. Once most followers have it: it's "committed" — applied to the actual data. Every node applies the same log entries in the same order → every node has the same data. The log is the single source of truth. If you know the log, you can reconstruct any node's state.

---

### 🔵 Simple Definition (Elaborated)

Why a log (and not just direct state replication)? With state replication: send current state snapshot to followers — expensive for large state. With log replication: send only what changed (delta). More efficient. Also: log gives you time-travel (replay from any point), compaction (snapshot at checkpoint + apply recent log), and auditability (every change recorded). The log is also the crash recovery mechanism: restart from last snapshot + replay log entries since snapshot → fully recovered state. Kafka took this concept further: the log IS the product (not just an internal mechanism). Consumers read from the log at their own pace — the log persists, consumers can rewind.

---

### 🔩 First Principles Explanation

**AppendEntries RPC and log consistency check:**

```
RAFT LOG REPLICATION PROTOCOL (detailed):

DATA STRUCTURES:
  Leader state:
    log[]: array of (index, term, command). Persisted to disk.
    nextIndex[follower]: next log index to send to this follower (optimistic: leader.lastLogIndex+1)
    matchIndex[follower]: highest log index known to be replicated to follower (committed-tracking)
    commitIndex: highest index known committed (acked by majority).
    lastApplied: highest index applied to state machine.
    
  Follower state:
    log[]: same structure. Persisted.
    commitIndex: updated from leader's AppendEntries.
    lastApplied: applied to state machine.

NORMAL OPERATION (leader has followers at same index):
  Client → Leader: "SET x = 10"
  
  Leader:
    entry = {index: nextIndex, term: currentTerm, command: SET_x_10}
    log.append(entry)
    Persist log to disk (fsync or equivalent).
    
    For each follower f:
      Send AppendEntries(
          term: currentTerm,          // Used for leader validity check
          leaderId: self,             // So followers can redirect clients
          prevLogIndex: nextIndex[f]-1, // Index of entry just before new entries
          prevLogTerm: log[nextIndex[f]-1].term, // Term of prevLogIndex entry
          entries: [entry],           // New entries to append (may be batch)
          leaderCommit: commitIndex   // Highest committed index (followers use this to apply)
      )
      
  Follower receives AppendEntries:
    CHECK 1: If term < currentTerm → reject (stale leader).
    CHECK 2: If log[prevLogIndex].term ≠ prevLogTerm → LOG INCONSISTENCY. Reject.
      (Follower doesn't have prevLogIndex entry, or has a different term there.)
    
    If both checks pass:
      If entries conflict with existing log entries (same index, different term):
        Delete conflicting entry and all following it.
      Append new entries.
      Persist to disk.
      Update commitIndex = min(leaderCommit, index of last new entry).
      Reply SUCCESS.
      
  Leader receives SUCCESS from follower f:
    matchIndex[f] = index of last sent entry.
    nextIndex[f] = matchIndex[f] + 1.
    
  Leader checks for new commit:
    For each index N > commitIndex:
      If log[N].term == currentTerm AND
         count(matchIndex[f] >= N for all followers) >= majority:
        commitIndex = N.
    
  Apply committed entries to state machine:
    While lastApplied < commitIndex:
      lastApplied++
      stateMachine.apply(log[lastApplied].command)

LOG INCONSISTENCY REPAIR (follower behind/diverged):

  SCENARIO: follower F1 missed 5 entries (was partitioned, now rejoined).
    Leader log: [1,2,3,4,5,6,7,8,9,10]  (index 10 = latest)
    F1 log:     [1,2,3,4,5]             (index 5 = last applied before partition)
    
  Leader: nextIndex[F1] = 6 (initially: leader.lastLogIndex + 1 = 11 — optimistic)
  
  Attempt 1: Leader → F1: AppendEntries(prevLogIndex=10, prevLogTerm=3, entries=[])
    F1: "I don't have index 10." REJECT.
    
  Leader: decrements nextIndex[F1] to 10.
  Attempt 2: AppendEntries(prevLogIndex=9, ...). F1: no index 9. REJECT.
  ...
  Attempt 6: AppendEntries(prevLogIndex=5, prevLogTerm=2, entries=[6,7,8,9,10]).
    F1: checks log[5].term == prevLogTerm (2). YES (F1 has entry 5 with term 2).
    F1: appends entries 6,7,8,9,10. SUCCESS.
    
  OPTIMIZATION (nextIndex binary search):
    Instead of decrementing one by one (O(n) round trips for large gaps):
    Followers include conflictIndex (index of first inconsistent entry) and conflictTerm in rejection.
    Leader can jump nextIndex directly to conflictIndex.
    Reduces catch-up from O(n) to O(log n) or O(1) in most cases.
    
  DIVERGED LOG (follower has entries not on leader):
    Scenario: F2 was briefly leader in term 2, accepted some entries, then was replaced by
              current leader in term 3.
    F2 log: [1,2,3, 4t2, 5t2] (indices 4 and 5 have term=2 entries from F2's brief leadership)
    Leader log: [1,2,3, 4t3, 5t3, 6t3] (term=3 entries for indices 4,5,6)
    
    Leader: AppendEntries(prevLogIndex=3, prevLogTerm=1, entries=[4t3, 5t3, 6t3]).
    F2: log[3].term == 1 (matches prevLogTerm). YES. Append entries.
    F2 overwrites its term=2 entries 4,5 with term=3 entries 4,5 from leader.
    
    WHY THIS IS SAFE: F2's term=2 entries at 4,5 were NEVER COMMITTED (they're from a brief 
    leadership that ended before majority ACKed). No client ever received a response for those
    entries. Safe to overwrite with the current leader's entries.
    
    CRITICAL SAFETY CHECK: committed entries (acked by majority) are NEVER overwritten.
    Leader election rule (up-to-date check) ensures new leader has all committed entries.
    Uncommitted entries on stale leaders are discarded.

KAFKA LOG REPLICATION:

  Kafka partition = ordered, immutable, append-only log.
  
  ISR (In-Sync Replicas): set of replicas "in sync" with leader.
    In-sync = replica's log is within replica.lag.time.max.ms of leader.
    Out-of-sync: replica removed from ISR (too far behind).
    
  Producer write (acks=all):
    Producer → Leader partition: produce record.
    Leader appends to log.
    Leader → all ISR replicas: replicate (synchronously waits for ISR ACKs).
    All ISR replicas: append to log. ACK leader.
    Leader → Producer: "Write successful."
    
  High Watermark (HW): highest offset committed to all ISR replicas.
    Consumers: can only read up to HW (no uncommitted reads).
    This ensures consumers only see records that won't be lost on leader failure.
    
  Log Retention:
    Time-based: delete segments older than log.retention.hours.
    Size-based: delete oldest segments when total size > log.retention.bytes.
    Compaction: keep only the latest value per key (like Raft snapshots).
    
  Log Segments:
    Each partition log divided into segments (default 1GB or 7 days).
    Active segment: being written to. Inactive: sealed (immutable).
    .log file: records. .index file: offset-to-position index. .timeindex: time-to-offset.
    
  Consumer reads from segment files directly (zero-copy via sendfile() syscall).

POSTGRESQL WAL STREAMING REPLICATION:
  
  WAL (Write-Ahead Log): every change written to WAL before data files.
  WAL record: contains enough info to re-apply the change (redo log).
  
  Streaming replication:
    Primary: flushes WAL to disk, sends WAL records to standbys via replication slot.
    Standby: receives WAL records, applies to its own data files.
    
  LSN (Log Sequence Number): byte offset in WAL stream.
    pg_current_wal_lsn(): current WAL write position on primary.
    pg_last_wal_receive_lsn(): position received by standby.
    pg_last_wal_replay_lsn(): position applied by standby.
    Replication lag = pg_current_wal_lsn() - pg_last_wal_replay_lsn().
    
  Synchronous replication: synchronous_standby_names = 'standby1'.
    Primary waits for standby1 to confirm WAL receipt before COMMIT returns.
    Same trade-off as synchronous database replication.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT log replication (only state snapshots):
- Replicate full state on every change: expensive for large state
- No ordered history: can't determine what changed and when
- Recovery requires full state transfer: slow startup after failure

WITH log replication:
→ Efficient delta replication: only send changes, not full state
→ Total order: all nodes apply same commands in same sequence → identical state
→ Crash recovery: replay log from checkpoint → recover to exact pre-crash state

---

### 🧠 Mental Model / Analogy

> A bank's transaction ledger shared between multiple branches. The head office (leader) records every transaction in order: "Entry 1001: deposit $50 to account A. Entry 1002: withdraw $30 from account B." Each branch (follower) receives the ledger entries and applies them to its local account balances. A branch's current balances = ledger entries 1 through N applied in order. New branch: receive full ledger, apply all entries. Missed entries: receive missing entries from head office, apply in order. Balances at all branches are IDENTICAL because everyone applies the SAME ledger in the SAME order.

"Head office recording transactions in ledger" = leader appending to log
"Branches applying ledger entries" = followers applying log entries to state machine
"Entry number in ledger" = log index
"Transaction committed once multiple branches confirm" = commit when quorum ACKs

---

### ⚙️ How It Works (Mechanism)

**etcd log replication monitoring:**

```bash
# Check etcd Raft log status:
$ etcdctl endpoint status --write-out=table
# Shows: raft_index (committed), raft_applied (applied to state machine).
# If raft_applied < raft_index: apply backlog (normal during heavy write load).

# Monitor etcd Raft metrics (Prometheus):
# etcd_server_proposals_committed_total: total proposals committed via Raft.
# etcd_server_proposals_pending: proposals waiting to commit.
# etcd_raft_status_apply_index: last applied log index.
# etcd_raft_status_commit_index: last committed log index.

# Check if follower is behind:
$ etcdctl endpoint status --cluster --write-out=json | \
    python3 -c "
import json, sys
nodes = json.load(sys.stdin)
for n in nodes:
    s = n['Status']
    print(f\"{n['Endpoint']}: raftIndex={s['raftIndex']}, raftApplied={s['raftApplied']}, isLeader={s['leader']==(s['header']['member_id'])}\")
"

# Trigger manual compaction (discard old log entries before snapshot):
$ REV=$(etcdctl endpoint status --write-out=json | python3 -c \
    "import json,sys; print(json.load(sys.stdin)[0]['Status']['header']['revision'])")
$ etcdctl compact $REV
$ etcdctl defrag
```

---

### 🔄 How It Connects (Mini-Map)

```
Raft (consensus: leader election + log replication + safety)
        │
        ▼
Log Replication ◄──── (you are here)
(append entries to log; commit when quorum ACKs; apply to state machine)
        │
        ├── State Machine Replication (what log replication achieves: identical state machines)
        ├── Replication Strategies (sync/async/quorum: log replication is quorum-synchronous)
        └── Kafka (log is the core data structure for distributed event streaming)
```

---

### 💻 Code Example

**Simplified replicated log implementation:**

```java
public class ReplicatedLog {
    
    private final List<LogEntry> log = new ArrayList<>();
    private volatile int commitIndex = -1;
    private volatile int lastApplied = -1;
    private final StateMachine stateMachine;
    private final List<Follower> followers;
    private final int quorum;
    
    @Getter @AllArgsConstructor
    public static class LogEntry {
        private final int index;
        private final int term;
        private final Command command;
    }
    
    // Leader: append a new entry and replicate to followers.
    public CompletableFuture<Result> appendEntry(Command command, int currentTerm) {
        // Step 1: Append to local log.
        LogEntry entry = new LogEntry(log.size(), currentTerm, command);
        log.add(entry);
        
        // Step 2: Replicate to all followers in parallel.
        CompletableFuture<Boolean>[] replicationFutures = followers.stream()
            .map(f -> replicateToFollower(f, entry))
            .toArray(CompletableFuture[]::new);
        
        // Step 3: Wait for quorum (majority) to ACK.
        return waitForQuorum(replicationFutures, entry.getIndex())
            .thenApply(committed -> {
                if (committed) {
                    commitIndex = entry.getIndex();
                    applyCommittedEntries(); // Step 4: Apply to state machine.
                    return Result.success();
                }
                return Result.failure("Quorum not reached");
            });
    }
    
    private CompletableFuture<Boolean> replicateToFollower(Follower follower, LogEntry entry) {
        int prevLogIndex = entry.getIndex() - 1;
        int prevLogTerm = prevLogIndex >= 0 ? log.get(prevLogIndex).getTerm() : -1;
        
        return follower.appendEntries(
            entry.getTerm(),    // current leader term
            prevLogIndex,       // consistency check index
            prevLogTerm,        // consistency check term
            List.of(entry),     // new entries
            commitIndex         // let follower know what's committed
        );
    }
    
    // Apply all committed but not-yet-applied entries to state machine:
    private void applyCommittedEntries() {
        while (lastApplied < commitIndex) {
            lastApplied++;
            stateMachine.apply(log.get(lastApplied).getCommand());
        }
    }
    
    // Follower: handle AppendEntries RPC.
    public AppendEntriesResponse onAppendEntries(int leaderTerm, int prevLogIndex,
                                                  int prevLogTerm, List<LogEntry> entries,
                                                  int leaderCommit) {
        // Consistency check:
        if (prevLogIndex >= 0 && (prevLogIndex >= log.size() || 
            log.get(prevLogIndex).getTerm() != prevLogTerm)) {
            // Log inconsistency — return conflict index for fast repair:
            int conflictIndex = Math.min(prevLogIndex, log.size() - 1);
            return AppendEntriesResponse.failure(conflictIndex);
        }
        
        // Delete conflicting entries and append:
        for (LogEntry entry : entries) {
            if (entry.getIndex() < log.size()) {
                if (log.get(entry.getIndex()).getTerm() != entry.getTerm()) {
                    // Conflict: truncate log from this point.
                    while (log.size() > entry.getIndex()) log.remove(log.size() - 1);
                }
            }
            if (entry.getIndex() >= log.size()) {
                log.add(entry);
            }
        }
        
        // Update commitIndex from leader:
        if (leaderCommit > commitIndex) {
            commitIndex = Math.min(leaderCommit, log.size() - 1);
            applyCommittedEntries();
        }
        
        return AppendEntriesResponse.success(log.size() - 1);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The log and the state machine are the same thing | They are separate. The log is the ordered sequence of commands (durable, append-only). The state machine is the current state after applying those commands (e.g., a key-value store, a SQL table). You can reconstruct the state machine from the log by replaying commands. You can checkpoint the state machine (snapshot) to avoid replaying the entire log from the beginning. Two different nodes can have identical state machines with different log histories if snapshots were taken at different points |
| Log replication is just database WAL | They are related but different in scope. Database WAL (Write-Ahead Log) is a durability mechanism for a single node: write to WAL before modifying data files, so you can recover after crash by replaying WAL. Log replication distributes this concept across N nodes: each node has a WAL, and the leader coordinates keeping all WALs in sync. Kafka and Raft use log replication as a distributed primitive; PostgreSQL WAL streaming replication is WAL + log replication combined |
| All entries in the log are committed | Only entries up to commitIndex are committed. Entries between commitIndex and log.lastIndex are "in-flight" — appended locally by the leader but not yet replicated to a quorum. These in-flight entries can be lost if the leader crashes. The leader never tells the client the write succeeded until the entry is committed (quorum ACKed). In-flight entries that were never committed will be cleaned up by the new leader's log repair mechanism |
| Kafka consumers always get consistent (latest) data | Kafka consumers can only read up to the High Watermark (HW) — the highest offset committed to all ISR replicas. Records written to the leader partition log but not yet replicated to all ISR replicas are "not visible" to consumers (offset > HW). This prevents consumers from reading data that could be lost on leader failure. After leader failover and log truncation, the HW advances — consumers continue from where they left off |

---

### 🔥 Pitfalls in Production

**Raft log growth causing slow follower catch-up on restart:**

```
PROBLEM: etcd follower restarts after 1 hour of downtime.
         During the hour: 1 million Raft log entries accumulated (no snapshot).
         Follower catch-up: must receive and apply 1 million entries → 15 minutes of unavailability
         for that node. If a second node fails during this window: cluster loses quorum.

BAD: Relying solely on log replication for follower catch-up (no snapshot):
  # etcd peer URL: follower rejoining cluster.
  # Leader sends 1M AppendEntries → follower applies 1M entries → slow recovery.
  
  # Problem exacerbated by:
  # 1. No snapshot configured (snapshotCount too high or disabled).
  # 2. Single-threaded application of log entries.
  # 3. Large entries (big values stored in etcd).
  
FIX: Configure snapshots + prefer snapshot-based sync for lagging followers:

  # etcd configuration (in /etc/etcd/etcd.conf):
  snapshot-count: 10000  # Snapshot every 10K committed entries
  
  # When follower is too far behind (nextIndex < snapshot index):
  # Leader sends InstallSnapshot RPC instead of AppendEntries.
  # Follower: apply snapshot → jump directly to snapshot's log index.
  # Then: replay only entries from snapshot index to current (much fewer).
  
  # Instead of: 1M entries → 15 min
  # Snapshot at 990K entries + 10K recent entries → 30 seconds catch-up.
  
  # Monitor: etcd_network_peer_sent_bytes_total — high rate = follower catching up.
  # If catch-up takes > half of election timeout: cluster at risk.
  # Set: --election-timeout = max(10ms, 10 * heartbeat-interval) with headroom.

FIX 2: Kafka ISR catch-up:
  # Kafka log compaction for catch-up of new consumers:
  # Set cleanup.policy=compact for topics with key-based state (not event streams).
  # New broker joining: receives compacted log (only latest value per key) → fast catch-up.
  # Producer throughput sustained during catch-up (existing ISR still satisfies quorum).
```

---

### 🔗 Related Keywords

- `Raft` — uses log replication as its core mechanism for replicated state machines
- `State Machine Replication` — what log replication achieves: identical deterministic state machines
- `Kafka` — log is the fundamental data structure; consumers read ordered log from any offset
- `Replication Strategies` — sync/async/quorum: log replication implements quorum-synchronous strategy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Leader appends to log; committed when     │
│              │ quorum ACKs; all nodes apply same        │
│              │ sequence → identical state machines      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Replicated state (etcd, Kafka, CockroachDB│
│              │ PostgreSQL streaming replication)         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple pub/sub without ordering needs;   │
│              │ eventual-consistent large datasets        │
│              │ (too many replicas = high log sync cost) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The ledger: all branches apply the same │
│              │  transactions in order → same balances." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ State Machine Replication → Raft →       │
│              │ Kafka → Replication Strategies → Quorum  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Raft leader has log: [1,2,3,4,5] (all committed, commitIndex=5). Follower F1 also has [1,2,3,4,5] (matchIndex=5). Leader appends entry 6 (not yet committed). Leader crashes. F1 becomes new leader. F1's log is [1,2,3,4,5]. Does F1 know about entry 6? Can entry 6 ever be committed? What does F1 do with any uncommitted entries that might be on other followers?

**Q2.** Kafka producer with acks=1 (only leader ACK required). Producer writes 1000 records to partition leader. Leader ACKs all 1000. Leader then crashes. The ISR replica only replicated 950 of 1000 records before the crash. The ISR replica is elected as new leader. Kafka truncates the replica's log to the High Watermark (950). What happens to records 951-1000? What should the producer do? How does Kafka's idempotent producer (enable.idempotence=true) help here?
