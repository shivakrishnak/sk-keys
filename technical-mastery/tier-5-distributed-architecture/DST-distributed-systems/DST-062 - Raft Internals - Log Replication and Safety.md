---
id: DST-062
title: "Raft Internals - Log Replication and Safety"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-041, DST-058
used_by: DST-089
related: DST-041, DST-042, DST-046, DST-058
tags:
  - distributed
  - raft
  - consensus
  - log-replication
  - safety
  - leader-completeness
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 62
permalink: /technical-mastery/distributed-systems/raft-internals/
---

⚡ TL;DR - Raft's log replication works through
AppendEntries RPCs from leader to followers; the
Leader Completeness property guarantees that any
newly elected leader has all previously committed
entries; safety relies on the vote restriction
(candidates cannot win without an up-to-date log)
and the commit rule (entries only committed when
on a quorum's log in the current term).

---

### 📋 Entry Metadata

| #062 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Raft Consensus Algorithm, The Consensus Problem | |
| **Used by:** | Build KV Store Phase 3 | |
| **Related:** | Raft, Paxos, Leader Election, Consensus | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
DST-041 introduced Raft at a conceptual level.
But the safety proofs are where the hard problems
hide. What prevents two leaders from committing
conflicting entries? What if a leader commits an
entry from a previous term right before dying?
What is the "5.4.2 safety argument" in the Raft
paper and why was it added late in Raft's design?

Without understanding the internal mechanisms:
you can implement Raft but not debug it when it
breaks; you cannot identify subtle correctness
bugs; you cannot explain to a team WHY a specific
implementation decision is or is not safe.

---

### 📘 Textbook Definition

**Raft log replication** is the mechanism by which
a Raft leader distributes log entries to followers
and commits them once a quorum acknowledges.

**Raft safety** is enforced by two key rules:
1. **Election Restriction:** A candidate can only
   win an election if its log is at least as
   up-to-date as the majority of voters' logs.
2. **Commit Rule:** A leader only commits entries
   from its current term (not previous terms)
   directly. Previous-term entries become committed
   only indirectly, when a current-term entry is
   committed and its log position passes theirs.

---

### ⏱️ Understand It in 30 Seconds

```
RAFT LOG ENTRY: {index, term, command}
  index: position in log
  term:  when it was created (leader's term)
  command: the state machine command

APPEND ENTRIES RPC:
  Leader → Follower:
    prevLogIndex: last log entry before these
    prevLogTerm:  term of that entry
    entries[]:    new entries to append
    leaderCommit: highest committed index

FOLLOWER RULE:
  Accept AppendEntries only if:
    log[prevLogIndex].term == prevLogTerm
  (This is the "consistency check")

COMMIT RULE (key safety rule):
  Leader commits entry at index i when:
    quorum of servers have log[i] with CURRENT TERM
  (NOT from a previous term - critical!)

LEADER COMPLETENESS PROPERTY:
  If entry E is committed in term T,
  then every leader elected in terms > T
  has E in its log.
  (Guaranteed by vote restriction)
```

---

### 🔩 First Principles Explanation

**THE LOG MATCHING PROPERTY:**

```
If two logs have an entry at the same index
with the same term, they are identical up to
that index.

WHY: Leader never creates two entries with the
  same index in the same term. AppendEntries
  consistency check rejects entries if prevLogIndex/
  prevLogTerm doesn't match. Therefore logs can
  only diverge after the last matching entry.

DIVERGENT LOG EXAMPLE:
  Leader (Term 3): 1[T1] 2[T1] 3[T2] 4[T3] 5[T3]
  Follower A:      1[T1] 2[T1] 3[T2] 4[T3]
    (missing entry 5 - was offline)
  Follower B:      1[T1] 2[T1] 3[T2] 5[T2] 6[T2]
    (conflicting entries - was leader in T2)

  Leader sends AppendEntries to Follower B:
  Detects conflict at index 4 (B has T2, leader has T3)
  Leader decrements nextIndex until it finds
  a matching entry (index 3 matches).
  Then overwrites from index 4 onward.
  Follower B: 1[T1] 2[T1] 3[T2] 4[T3] 5[T3]
  (Follower B's conflicting entries are replaced)
```

**THE COMMIT RULE (Critical Safety Property):**

```
DANGEROUS SCENARIO (why the commit rule exists):

Term 2: S1 is leader.
  S1 appends entry E at index 3, term 2.
  S1 replicates to S2 only. S1 crashes.

Term 3: S5 is elected (has only index 1,2 in log).
  S5 appends entry F at index 3, term 3.
  S5 crashes immediately.

Term 4: S1 is re-elected (has entry E at index 3).
  S1 sees E (term 2) at index 3 on its log and S2's.
  That's a quorum!
  CAN S1 commit E (which was created in term 2)?

  NO! (This is the critical rule)
  WHY: S5 could be re-elected (has votes from S3, S4
  which have no conflicting entry at index 3).
  If S5 is elected, it would overwrite index 3 with F.
  If S1 already committed E at index 3 for clients:
  SAFETY VIOLATION - two different committed values.

THE FIX:
  Leaders only directly commit entries from THEIR CURRENT
    TERM.
  S1 (term 4) must append a new entry at index 4 in term 4.
  When that entry is committed (quorum in term 4):
  The log matching property ensures E is also implicitly
  committed (it's at index 3 on the quorum that confirmed
    term 4).
  Now S5 cannot be elected: any voter confirming index 4
  has E at index 3, so S5's log is not up-to-date.
```

**LEADER ELECTION SAFETY (Vote Restriction):**

```python
def should_grant_vote(
    candidate_last_log_index: int,
    candidate_last_log_term: int,
    my_last_log_index: int,
    my_last_log_term: int
) -> bool:
    """
    Vote for candidate only if their log is at least
    as up-to-date as mine.
    
    "Up-to-date" means:
    1. Higher last log term wins.
    2. If same last term: longer log wins.
    """
    if candidate_last_log_term > my_last_log_term:
        return True  # Candidate has newer term in log
    if candidate_last_log_term == my_last_log_term:
        return candidate_last_log_index >= my_last_log_index
    return False  # Candidate's log is behind mine

# WHY THIS ENSURES LEADER COMPLETENESS:
# Any committed entry E was on a quorum of servers.
# To win election, candidate needs votes from a quorum.
# Any two quorums overlap in at least one server.
# The overlapping server has E in its log.
# The overlapping server will NOT vote for a candidate
# whose log doesn't include E.
# Therefore: any elected leader has E.
```

**LINEARIZABLE READS IN RAFT:**

```
PROBLEM: A Raft leader can serve stale reads.

Scenario:
  Leader A (term 5) is partitioned from others.
  New leader B is elected (term 6).
  Leader B commits new writes.
  Client reads from Leader A: returns stale data.
  (A doesn't know it's no longer leader)

SOLUTION 1: Lease-based reads
  Leader sends heartbeat, records time T.
  For next election_timeout duration, no new leader
  can be elected (followers won't time out).
  Leader serves reads within this lease period
  without another round trip.
  RISK: Requires bounded clock skew.

SOLUTION 2: Read index (used by etcd)
  On each read request:
  1. Leader records its current commit index: readIndex
  2. Leader sends heartbeat to confirm it's still leader
     (ensures quorum is still following it)
  3. Wait until state machine apply index >= readIndex
  4. Serve read from state machine
  No additional write needed; linearizable read guaranteed.
  
SOLUTION 3: Always route reads through quorum
  Most conservative; highest latency.
  Reads treated like writes: go through AppendEntries.
```

---

### 🧠 Mental Model / Analogy

> Raft's commit rule for previous-term entries is
> like a new CEO (leader) who finds a signed contract
> (old entry) on their predecessor's desk. The contract
> was signed by two of the five board members (quorum).
> Can the new CEO execute it? Not safely - because a
> rival CEO might have been elected during the chaos
> and signed a different contract with those same two
> board members. The new CEO must first get all five
> board members to acknowledge that THEY are the CEO
> (new term commitment), and then the old contract is
> implicitly ratified by the log matching property.
> This is the "commit a new-term entry to indirectly
> commit old-term entries" rule.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Basic log replication:**
Leader appends to log. Sends to followers. When
quorum acknowledges: commit. Apply to state machine.
Tell followers to commit in next heartbeat.

**Level 2 - Log divergence and repair:**
Followers can have stale or conflicting log entries
(from previous failed leaders). Current leader repairs
divergence by finding the last matching entry and
overwriting everything after it. This is why Raft
can have followers with more entries than the leader
temporarily (they get overwritten).

**Level 3 - The critical commit rule:**
Leaders do not directly commit entries from previous
terms. This prevents a subtle safety violation where
a stale entry could appear committed and then be
overwritten by a newly elected leader with a
conflicting entry at the same index.

**Level 4 - Vote restriction implementation:**
The vote restriction is implemented in RequestVote RPC
handling: a server only votes for a candidate if the
candidate's last log entry is at least as up-to-date
as its own. "Up-to-date" means: higher last log term,
or same last log term and at least as long log.

**Level 5 - Linearizable reads without lease:**
Serving reads from a Raft leader without additional
coordination can return stale data (the leader might
be deposed and not know it). etcd's read index
approach (commit index check + heartbeat confirmation)
provides linearizable reads without writing to the
log for every read, enabling high-throughput read
workloads on Raft clusters.

---

### 💻 Code Example

**AppendEntries Consistency Check**

```python
# WRONG: Accepting entries without consistency check
# (can create divergent logs)

class BadRaftFollower:
    def append_entries(
        self,
        prev_log_index: int,
        prev_log_term: int,
        entries: list,
        leader_commit: int
    ) -> bool:
        # BAD: no consistency check
        # Append regardless of prev_log_index/term:
        for entry in entries:
            self.log.append(entry)  # May create divergence!
        return True
```

```python
# CORRECT: Raft AppendEntries with full consistency check

from dataclasses import dataclass
from typing import Optional

@dataclass
class LogEntry:
    index: int
    term: int
    command: str

class RaftFollower:
    def __init__(self):
        self.log: list[LogEntry] = []
        self.commit_index: int = 0
        self.current_term: int = 0

    def _last_log_index(self) -> int:
        return len(self.log)

    def _log_term(self, index: int) -> int:
        """Return term of entry at index (1-based)."""
        if index == 0:
            return 0
        if index <= len(self.log):
            return self.log[index - 1].term
        return -1  # Index doesn't exist

    def append_entries(
        self,
        term: int,
        leader_id: str,
        prev_log_index: int,
        prev_log_term: int,
        entries: list[LogEntry],
        leader_commit: int
    ) -> tuple[int, bool]:
        """
        AppendEntries RPC handler.
        Returns (current_term, success).
        """
        # Rule 1: Reply false if term < current_term
        if term < self.current_term:
            return (self.current_term, False)

        self.current_term = term

        # Rule 2: Reply false if log doesn't contain
        # entry at prevLogIndex with prevLogTerm
        if prev_log_index > 0:
            if prev_log_index > len(self.log):
                # We don't have prevLogIndex: reject
                return (self.current_term, False)
            if self._log_term(prev_log_index) != prev_log_term:
                # Term mismatch at prevLogIndex: reject
                return (self.current_term, False)

        # Rule 3: Delete conflicting entries and append new ones
        for entry in entries:
            existing_term = self._log_term(entry.index)
            if existing_term != 0 and existing_term != entry.term:
                # Conflict: truncate from this index onward
                self.log = self.log[:entry.index - 1]

            if entry.index > len(self.log):
                self.log.append(entry)
            # (If entry already exists with same term: skip)

        # Rule 4: Update commit index
        if leader_commit > self.commit_index:
            self.commit_index = min(
                leader_commit,
                self._last_log_index()
            )

        return (self.current_term, True)
```

---

### ⚖️ Comparison Table

| Property | Raft Mechanism | Why It Matters |
|---|---|---|
| **Leader election safety** | Vote restriction (up-to-date log required) | Ensures new leader has all committed entries |
| **Log matching** | prevLogIndex + prevLogTerm consistency check | Guarantees logs are identical up to match point |
| **Commit rule** | Only commit current-term entries directly | Prevents overwrite of old committed entries |
| **Linearizable reads** | Read index + heartbeat confirm | Reads reflect committed state; no stale reads |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A leader commits entries from any term once quorum acknowledges" | WRONG. This is the most common Raft misconception. A leader can only directly commit entries with its CURRENT TERM in the log. Old-term entries are committed INDIRECTLY when a new-term entry is committed that appears after them in the log. |
| "Reading from the leader is always linearizable" | WRONG. A partitioned leader may serve stale reads (doesn't know it's deposed). Linearizable reads require a read-index check (etcd's approach) or lease-based reads with bounded clock skew. |
| "Raft is simpler than Paxos to implement" | More understandable (Raft's design goal) is not the same as simpler. A correct Raft implementation requires: election restriction, log conflict resolution, commit rule for old terms, read-index for linearizable reads, snapshot support, membership changes. It is complex; just more comprehensible than Paxos. |
| "Leader failure always causes data loss" | No. Committed entries (on quorum) are never lost. The only entries that may be lost are uncommitted entries that were only on the leader before it failed. This is intentional and correct behavior. |

---

### 🚨 Failure Modes & Diagnosis

**Raft Cluster Serves Stale Reads**

**Symptom:** A key-value store backed by Raft is
returning old values even though writes completed
successfully. Different clients see different values
for the same key. The leader is "up" and accepting
writes.

**Root Cause:** Reads are served directly from the
leader's state machine without a read-index check.
After a brief partition and re-election, the old
leader (now follower) was still serving reads for
a short window when clients connected to it.

**Diagnosis:**
```bash
# etcd: check leadership status:
etcdctl endpoint status --cluster -w table
# Compare "RAFT INDEX" across nodes.
# If the node serving reads has lower RAFT INDEX
# than other nodes: it's lagging behind.

# Check if reading from a follower or lagging leader:
etcdctl endpoint status -w json | \
  python3 -c "
import json, sys
for ep in json.load(sys.stdin):
    m = ep['Status']
    print(f\"Leader: {m['leader']}, \
            Member: {m['header']['member_id']}, \
            RaftIndex: {m['raftIndex']}\")
"
# If leader ID != member's own ID: this is a follower.
# Do not serve reads from followers (in etcd's default config)

# Application: ensure reads use ConsistentRead=true
# (DynamoDB) or linearizable read option (etcd):
etcdctl get mykey --consistency=l  # linearizable
```

**Fix:** Use read-index based reads (etcd default for
linearizable reads). For custom Raft implementations:
implement the read-index procedure before serving
any client read.

---

### 🔗 Related Keywords

**Prerequisites:** `Raft Consensus Algorithm` (DST-041),
`The Consensus Problem` (DST-058)

**Builds On This:** `Build KV Store Phase 3` (DST-089)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LOG ENTRY    │ {index, term, command}                   │
│ COMMIT       │ Quorum ack'd in CURRENT TERM             │
│ OLD TERM     │ Committed indirectly via new-term entry  │
├──────────────┼─────────────────────────────────────────-┤
│ VOTE RULE    │ Vote only if candidate log >= own log    │
│              │ Compare: last term first, then length   │
├──────────────┼──────────────────────────────────────────┤
│ LINEARIZABLE │ Read-index: get commit, send heartbeat,  │
│ READS        │ wait for apply >= readIndex, serve read  │
├──────────────┼──────────────────────────────────────────┤
│ DIVERGENCE   │ Leader backtracks nextIndex per follower │
│ REPAIR       │ until prevLog match; overwrites rest     │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Safety: leaders only commit own-term   │
│              │  entries; old entries commit indirectly"│
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The Raft commit rule - only directly commit
current-term entries - is an example of a crucial
class of distributed systems design pattern: deferred
commitment of past state through present commitment.
Rather than directly committing past actions (which
can race with concurrent overwrite), commit a present
action that provably supersedes and includes the
past actions. This pattern appears in: Git (a commit
includes its parent's full history - supersedes all
prior commits), Kafka (a consumer committing offset N
implicitly commits all offsets < N), and database
WAL recovery (replay from the most recent checkpoint,
which includes all earlier committed transactions).
When you encounter "how do I safely commit something
from the past in a distributed system?", the answer
is usually: add a current-timestamp/current-term
action that includes and supersedes the past item.

---

### 💡 The Surprising Truth

The Raft commit rule for old-term entries was not in
the original Raft design. Diego Ongaro discovered
the bug during the formalization of Raft's safety
proof (the TLA+ spec), not during initial design or
implementation. The scenario - where an old-term
entry appears on a quorum but can still be overwritten
by a new leader - was a subtle correctness bug that
only appeared during formal verification. This is
why TLA+ and formal methods matter for distributed
protocols: human reasoning about rare concurrent
failure scenarios is unreliable. Many distributed
systems bugs in production (etcd's leader reads,
Kafka's replica assignment, CockroachDB's early
bugs) were found by formal methods, not by code
review or testing.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Why can't a Raft leader directly commit
   an entry from a previous term, even if quorum
   acknowledges it? Construct the safety violation
   scenario that would occur without the rule.
2. [TRACE] Given log states for 5 nodes where the
   new leader's log is shorter than two followers':
   which follower logs get truncated? Which get
   extended? Draw the before/after state.
3. [IMPLEMENT] Write the AppendEntries RPC handler
   (follower side) including prevLogIndex check,
   conflict detection, and leader_commit update.
4. [COMPARE] Read-index linearizable reads vs
   lease-based reads: what assumption does each
   make? When does each fail?
5. [PROVE] Using the vote restriction rule, explain
   why Leader Completeness holds: why any newly
   elected leader has all committed entries.
