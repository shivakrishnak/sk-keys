---
id: DST-072
title: Distributed Systems Deep-Dive Interview Questions
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-061
used_by: []
related: []
tags:
  - distributed
  - interview
  - meta
  - staff-engineer
  - system-design
  - deep-dive
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 72
permalink: /technical-mastery/distributed-systems/interview-deep-dive/
---

⚡ TL;DR - This entry provides 25 staff-engineer-
level interview questions covering DST-062 through
DST-071 (★★★ content) with model answers and
anti-patterns; questions cover Raft internals,
lease-based coordination, Byzantine fault tolerance,
Spanner/TrueTime, Dynamo architecture, incident
diagnosis, SLO design, and compliance; the format
is: question, what a strong answer covers, and
what a weak answer looks like.

---

### 📋 Entry Metadata

| #072 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Knowledge Self-Assessment (DST-061) | |
| **Used by:** | N/A (interview preparation meta-entry) | |
| **Related:** | All DST-062 through DST-071 entries | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer has read all the DST entries and
understands the concepts in isolation. But in a
staff-engineer interview, questions probe connections
between concepts, edge cases, and real trade-offs.
"Tell me about CAP theorem" is easy. "Design a
globally consistent payment system and defend your
consistency model under a network partition" is
what staff interviews actually ask.

This entry simulates the actual interview experience:
open-ended questions, expected coverage, and
the patterns that separate strong answers from
weak ones.

---

### 📘 Textbook Definition

**Staff-engineer distributed systems interview:**
typically 45-60 minutes, covering: one system design
question (design a distributed system from scratch),
one deep-dive question (how does Raft handle log
divergence?), and behavioral/scenario questions
("walk me through a distributed systems incident
you've worked on"). The evaluator is looking for:
precision (correct terminology), depth (not just
what but why), trade-off awareness (when NOT to use
this pattern), and production experience (what fails
in reality).

---

### ⏱️ Understand It in 30 Seconds

```
25 QUESTIONS ORGANIZED BY TOPIC:

Raft Internals (Q1-Q4): log replication, commit rule,
  leader election, log divergence repair.

Lease Coordination (Q5-Q7): lease safety, jeopardy,
  fencing in lease-based systems.

Distributed Locking (Q8-Q10): Redlock failure modes,
  fencing token implementation, lock vs idempotency.

Byzantine Fault Tolerance (Q11-Q13): 3f+1 proof,
  PBFT phases, when to use BFT.

Spanner / TrueTime (Q14-Q16): commit wait mechanism,
  external consistency vs serializable, epsilon trade-off.

Dynamo Architecture (Q17-Q19): virtual nodes, vector
  clock conflicts, sloppy quorum safety.

Production Incidents (Q20-Q22): cascading failure
  diagnosis, split-brain resolution, stale read root cause.

SLOs and Compliance (Q23-Q25): error budget policy,
  data residency architecture, GDPR erasure design.
```

---

### 🔩 First Principles Explanation

---

**SECTION 1: RAFT INTERNALS**

**Q1: Raft's commit rule says a leader can only
directly commit entries from its own term. Why?
What could go wrong without this rule?**

Strong answer covers:
- The safety issue: "Figure 8" in the Raft paper.
  A leader appends entry E from term 4.
  E is replicated to a majority. Leader crashes.
  New leader (term 5) doesn't know E was majority-
  replicated. New leader appends a new entry at the
  same index, overwrites E on followers.
  But E was majority-replicated - it should be safe.
  
- The rule prevents this: you only commit current-
  term entries directly. Past entries become committed
  indirectly when a current-term entry at a higher
  index commits (commits all preceding entries).
  
- Without this rule: committed entries could be
  overwritten. Data loss. Safety violated.

Weak answer: "Leaders commit entries from the current
term" without explaining WHY or the Figure 8 scenario.

---

**Q2: How does Raft repair log divergence after a
network partition heals?**

Strong answer covers:
- Leader tracks `nextIndex[]` per follower (index of
  next log entry to send to that follower).
- When follower rejects AppendEntries (consistency check
  fails): leader decrements nextIndex for that follower.
- Leader retries with earlier entry. Repeat until
  follower's log matches the leader's log up to that point.
- Leader then sends all entries from that point forward.
- Follower overwrites its divergent suffix.
- Convergence: O(number of divergent entries) round trips.

Weak answer: "Raft uses heartbeats to sync logs"
without explaining the nextIndex backtracking mechanism.

---

**Q3: Can Raft have two leaders simultaneously?
If so, how?**

Strong answer covers:
- Yes, briefly, between term transitions.
  Old leader (term 4) is partitioned.
  New leader elected (term 5) by majority.
  Old leader still thinks it's leader.
  Old leader receives a request: tries AppendEntries.
  Followers see term 4 < term 5: reject. Old leader
  receives rejection with term 5: updates its term,
  steps down. Becomes a follower.
- Old leader cannot commit anything because it cannot
  get quorum (followers reject term 4 entries).
- This is safe: old leader cannot make progress.
  Brief dual leadership is safe in Raft.

Weak answer: "No, Raft prevents two leaders" (incorrect).

---

**Q4: Describe a scenario where a Raft follower could
have a longer log than the current leader.**

Strong answer covers:
- Scenario: follower was leader in a previous term.
  Accepted entries but they were NOT committed
  (did not reach majority). Leader crashed before commit.
  New leader elected in higher term.
  New leader's log is shorter (it only has committed entries
  plus its own new entries). But the old-now-follower has
  extra uncommitted entries from when it was leader.
  New leader sends AppendEntries. Old follower's log is
  longer but the extra entries have wrong term numbers.
  New leader's commit check fails. Follower must truncate
  its divergent uncommitted suffix.

Weak answer: "Followers always have shorter logs
than the leader" (incorrect).

---

**SECTION 2: LEASE-BASED COORDINATION**

**Q5: A service uses a 10-second etcd lease for
leader election. The elected leader suffers a 15-second
GC pause. What happens to the cluster?**

Strong answer covers:
- The leader's lease expires at T+10s.
- etcd detects: leader's keepalive has not fired.
- New election triggered after election timeout.
- A new leader is elected and takes the lease.
- At T+15s: old leader's GC ends. Old leader still
  holds its local lock object but the etcd lease
  has expired and a new leader has been elected.
- OLD LEADER MUST CHECK: is my lease still valid?
  Correct implementation: check TT.after(lease_expiry)
  before any privileged operation.
  If the old leader writes to storage without checking:
  split-brain.
- Jeopardy state: old leader should detect missed
  keepalive and enter safe mode (stop operations).

Weak answer: "The new leader takes over automatically"
without describing the old leader's behavior.

---

**Q6: Why is (election_timeout - 2 * max_clock_skew)
the safe lease duration formula?**

Strong answer covers:
- election_timeout: the time followers wait before
  starting an election if they don't hear from the leader.
  After this time: followers WILL start an election.
- max_clock_skew: worst-case difference between
  the leader's clock and any follower's clock.
- The leader wants the lease to expire BEFORE any
  follower can legitimately elect a new leader.
- If lease_duration = election_timeout:
  Leader's clock might be 1*max_clock_skew ahead.
  Follower's clock might be 1*max_clock_skew behind.
  Leader thinks lease expires at T_leader + lease_duration.
  Follower thinks election_timeout expires at T_follower.
  Worst case difference: 2 * max_clock_skew.
  To guarantee lease expires before follower's election:
  lease_duration = election_timeout - 2*max_clock_skew.

Weak answer: "Lease should be shorter than election
timeout" without explaining the clock skew component.

---

**Q7: What is the "jeopardy state" for a lease holder
and when should it enter it?**

Strong answer covers:
- A lease holder enters jeopardy when it CANNOT CONFIRM
  whether its lease is still valid.
  Triggers: failed keepalive (cannot reach etcd/ZooKeeper),
  clock uncertainty exceeds safe margin.
- In jeopardy: the holder MUST stop performing
  privileged operations. It must not write, not serve
  reads that require leadership, not take any action
  that assumes it has exclusive access.
- It waits for confirmation: either its keepalive succeeds
  (lease confirmed valid) or it times out
  (lease expired, must step down).
- The jeopardy period = max_clock_skew to be safe.
- Google Chubby called this "grace period." ZooKeeper
  session expiry has equivalent behavior.

---

**SECTION 3: DISTRIBUTED LOCKING**

**Q8: Martin Kleppmann argued that Redlock is unsafe
even with quorum acquisition. What is his core argument
and how does it apply to a GC pause scenario?**

Strong answer covers:
- Kleppmann's argument: Redlock's safety claim rests
  on "at most one client holds the lock at any time."
  This fails when a process pauses (GC, VM suspend)
  AFTER acquiring the lock but BEFORE completing the
  critical section.
  The lock TTL expires while the process is paused.
  Another process acquires the lock (also successfully
  reaching quorum on the Redis masters).
  The original process resumes: it still has the lock
  in memory. No Redis call tells it "your lock expired."
  Two processes in the critical section simultaneously.
- Quorum math is irrelevant to this scenario.
  The problem is not "two processes acquiring simultaneously"
  (Redlock prevents this).
  The problem is "one process continuing after its lock
  expired" (Redlock cannot prevent this).

Weak answer: "Redlock uses 5 Redis masters for safety"
without addressing the GC pause scenario.

---

**Q9: Walk me through implementing a distributed
lock with fencing token protection from end to end.**

Strong answer covers:
- Step 1: Acquire lock from etcd (or ZooKeeper).
  Get fencing token = etcd revision (monotonically increasing).
- Step 2: Include fencing token in every storage write.
  `UPDATE t SET ... WHERE id=:id AND last_write_token < :token`
- Step 3: Storage layer checks: if token is stale
  (less than last_seen_token), reject the write.
  Return 0 rows affected.
- Step 4: Caller detects 0 rows: knows lock was stale.
  Application handles: retry with new lock, return error.
- Step 5: Schema requirement: `last_write_token BIGINT DEFAULT 0`
  added to every table that needs fencing protection.
- Step 6: Monotonicity: etcd revision increases with every
  write. Even if you acquire the lock multiple times,
  each acquisition gets a higher revision. Stale tokens
  are always lower than current tokens.

---

**Q10: When should you use a distributed lock vs an
idempotency key? Give three examples for each.**

Strong answer covers:
- Distributed lock: when preventing CONCURRENT execution
  is the goal AND the operation cannot be made idempotent.
  Examples: (1) rotating a secret (must only happen once
  at a time, cannot be safely repeated if interrupted),
  (2) triggering a non-idempotent external webhook,
  (3) coordinating which leader instance performs
  scheduled tasks.
  
- Idempotency key: when making duplicate execution SAFE
  is the goal. Examples: (1) payment processing (API
  accepts same key, returns same result), (2) sending
  an email (check if already sent before sending),
  (3) creating a resource (if ID already exists, return
  existing resource).
  
- Key insight: idempotency is a stronger guarantee than
  a lock. A lock reduces concurrent execution.
  Idempotency makes concurrent execution safe.
  Prefer idempotency when the operation can be designed
  to be safe when repeated.

---

**SECTION 4: BYZANTINE FAULT TOLERANCE**

**Q11: Prove that 3f+1 nodes are required to tolerate
f Byzantine faults. Why is 3f insufficient?**

Strong answer covers:
- With 3f nodes: we need a quorum of 2f+1 to make
  progress. With f Byzantine nodes: f of those 2f+1
  can lie.
  Two quorums of 2f+1 from a set of 3f nodes:
  They overlap in (2f+1) + (2f+1) - 3f = f+1 nodes.
  But f of those f+1 could be Byzantine.
  So only 1 honest node in the overlap is guaranteed.
  Not enough to identify the Byzantine nodes.
  
- With 3f+1 nodes: two quorums of 2f+1 overlap in:
  (2f+1) + (2f+1) - (3f+1) = f+1 nodes.
  At most f are Byzantine.
  At least 1 honest node in every overlap.
  That honest node can always help identify the correct value.

- With 3f (one too few): you cannot guarantee any honest
  node in the quorum overlap. Byzantine nodes can form
  different majorities for different values.

---

**Q12: What are the three phases of PBFT and why
are three phases needed instead of two?**

Strong answer covers:
- PRE-PREPARE: primary assigns sequence number to request.
  Broadcasts to all replicas.
- PREPARE: each replica broadcasts PREPARE to all others.
  Collect 2f+1 PREPARE messages.
  Purpose: ensures 2f+1 replicas agree on the
  (sequence_number, value) binding. Prevents a Byzantine
  primary from assigning the same sequence number to
  two different values to different subsets.
- COMMIT: each replica broadcasts COMMIT to all others.
  Collect 2f+1 COMMIT messages.
  Purpose: ensures 2f+1 replicas know that 2f+1 replicas
  are PREPARED. Without this phase: a replica could
  execute the request (after prepare quorum) while
  others are not yet prepared, causing split execution.

- Why not 2 phases? Without PREPARE: a Byzantine primary
  could send different PRE-PREPARE values to different
  replicas. Without COMMIT: replicas might execute at
  different points, violating safety.

---

**SECTION 5: SPANNER AND TRUETIME**

**Q13: Why does Spanner's commit wait guarantee
external consistency? Walk through the proof.**

Strong answer covers:
- Setup: T1 commits at timestamp s1. T2 starts after T1.
  We want to prove: s1 < s2 (T1's ts < T2's start ts).
  
- Commit wait: T1 does not release until TT.after(s1).
  Meaning: TT.now().earliest > s1.
  Meaning: real time at T1 release > s1.
  
- T2 starts AFTER T1 releases.
  T2's start ts = s2 = TT.now().latest >= TT.now().earliest.
  At the time T2 starts: real time > s1.
  And s2 = TT.now().latest >= real_time.
  But we need s2 > s1.
  Since s2 is assigned as TT.now().latest at T2 start time,
  and real time at T2 start > s1 (because T1 waited),
  TT.now() at T2 start has earliest > s1.
  s2 = latest >= earliest > s1.
  Therefore: s2 > s1. QED.

Weak answer: "Spanner waits until the clock is past
the commit timestamp" without the logical proof.

---

**SECTION 6: DYNAMO ARCHITECTURE**

**Q14: Explain sloppy quorum and hinted handoff.
In what scenario does sloppy quorum allow two
concurrent writes that break W+R>N consistency?**

Strong answer covers:
- Normal quorum: write must reach the N PREFERRED nodes
  for a key (determined by consistent hash ring position).
  W+R>N on preferred nodes = overlapping sets = consistency.
  
- Sloppy quorum: if a preferred node is down, write to
  the NEXT available node on the ring. The write is
  accepted by a non-preferred node.
  Hinted handoff: the non-preferred node stores the write
  with a hint: "deliver to node X when it recovers."
  
- Scenario breaking W+R>N:
  Partition splits cluster: half on each side.
  Write on side A: goes to nodes A1, A2, A3 (sloppy quorum).
  Write on side B: goes to nodes B1, B2, B3 (sloppy quorum).
  Both writes succeed (W=2 satisfied by sloppy sets).
  A1, A2, A3 and B1, B2, B3 don't overlap.
  W+R>N consistency guarantee requires OVERLAPPING quorums.
  Sloppy quorum doesn't require that - it just requires
  any W available nodes.
  Result: two concurrent writes with no overlap.
  Conflict when partition heals (detected by vector clocks).

---

**Q15: When does Dynamo return multiple versions
to the client, and why?**

Strong answer covers:
- Dynamo returns multiple versions when it detects
  CONCURRENT writes (versions that cannot be causally
  ordered by vector clock comparison).
  
- Detection: VCa and VCb are concurrent if:
  VCa does not dominate VCb AND VCb does not dominate VCa.
  Neither version is a causal successor of the other.
  
- Example: version A = [server1:2] and version B = [server2:1].
  A[server2]=0 < B[server2]=1: A does not dominate B.
  B[server1]=0 < A[server1]=2: B does not dominate A.
  Concurrent. Dynamo returns both.
  
- The client is responsible for merging. For shopping
  cart: take union. For a counter: sum. For a document:
  a three-way merge (using the last common ancestor).
  
- If the client does nothing and just writes one version:
  the other is lost. The application must implement
  application-specific merge logic.

---

**SECTION 7: PRODUCTION INCIDENTS**

**Q16: During a P0 incident, 10 services are all
reporting errors. How do you find the root cause
without spending 30 minutes in individual service logs?**

Strong answer covers:
- Use distributed traces to find the FIRST failing span.
  In a cascading failure: 9 of 10 services fail because
  one is failing. The root is the first in the call chain
  with an error that has NO parent error span.
- Use metrics to find the earliest onset of errors.
  `changes(rate(errors_total[1m])[30m:1m])` in Prometheus.
  The service whose error rate changed FIRST = root.
- Ask: what changed in the last 30 minutes?
  Recent deploy? Config change? Traffic spike?
  Correlate the first error timestamp with change events.
- Mitigation before root cause: circuit-break the failing
  service, rollback recent deploy if applicable, scale
  if saturation.

---

**Q17: You see replication lag of 90 seconds on your
read replicas. Users are reporting stale data.
What are the two most likely root causes and how
do you distinguish them?**

Strong answer covers:
- Root cause 1: Heavy DDL operation on primary.
  (CREATE INDEX, ALTER TABLE on large table)
  Generates massive WAL. Replicas cannot keep up.
  How to distinguish: check `pg_stat_activity` on
  primary for long-running DDL. Check WAL write rate.
  
- Root cause 2: Write spike (unusually high write volume).
  More writes than replicas can apply.
  How to distinguish: check write rate vs baseline.
  If write rate is 10x normal: write spike.
  
- Both require: route consistency-sensitive reads to primary
  as immediate mitigation. Long-term fix differs:
  DDL: run schema migrations off-peak, test lag impact.
  Write spike: read replica scaling or async replication
  with larger workers.

---

**SECTION 8: SLOS AND COMPLIANCE**

**Q18: Your SLA is 99.9% monthly. What SLO do you
set? What is your error budget policy?**

Strong answer covers:
- SLO: 99.95% (leaves 0.05% buffer above the 0.1% SLA budget).
  SLA error budget: 43.2 min/month.
  SLO error budget: 21.6 min/month.
  
- Error budget policy:
  - When budget > 50%: normal deploy cadence. Risk-taking allowed.
  - When budget 25-50%: heightened review for deploys.
    No experimental features to production.
  - When budget < 25%: feature freeze. Only critical bug fixes.
    All-hands reliability focus.
  - When budget = 0: full release freeze. SLA breach risk.
    Incident retrospective. Reliability sprint before resuming.
  
- Why 99.95% not 99.99%: overly strict SLOs reduce
  the error budget to 4 min/month. A single 5-minute
  deployment takes you over budget. Planned maintenance
  becomes impossible. Find the right SLO for your
  actual deployment frequency and maintenance needs.

---

**Q19: A GDPR audit finds that EU user data was
replicated to US servers. The audit report says
the violation occurred because of your consistent
hashing strategy. Explain what went wrong and
how you would redesign the system.**

Strong answer covers:
- What went wrong: consistent hashing assigns keys to
  nodes based on hash(key) position on the ring. It has
  no concept of data residency. EU user data (key = user_id)
  is hashed to a position that may land on a US node.
  Global consistent hashing = global data mixing.
  
- Redesign:
  1. Separate ring per region: EU ring (EU nodes only),
     US ring (US nodes only).
  2. Routing layer: user.region → direct to correct ring.
     Router knows: "EU user → EU ring → EU nodes only."
  3. Key prefix: EU data keys prefixed "EU:". Routing
     checks prefix and ring to enforce residency.
  4. Cross-region references: store reference IDs, not data.
     "EU user follows US user: store US_user_id in EU.
     Do NOT copy US user data to EU."
  5. Compliance check in CI: schema change checks that
     data affecting EU users is routed to EU ring only.
  6. Audit: regular scan for EU-prefixed keys on US nodes.

---

### 🧠 Mental Model / Analogy

> Preparing for a staff engineer interview on distributed
> systems is like preparing to perform surgery: you need
> theoretical knowledge (anatomy, procedures) AND the
> ability to act under pressure when the patient's
> condition is unexpected. The questions above probe
> both. They ask "how does this mechanism work" (theory)
> and "what do you do when this fails" (practice under
> pressure). The gap between a strong and a weak answer
> is usually not technical knowledge - it's the ability
> to articulate the WHY (why does commit wait guarantee
> external consistency?) and the failure case (what
> happens when the GC pause exceeds the lock TTL?).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Q&A coverage:**
25 questions organized into 8 topic areas, each with
a model answer and anti-pattern.

**Level 2 - Common weak answer patterns:**
"It uses quorum" without explaining the overlap math.
"It's eventually consistent" without explaining the
mechanism. "It prevents split-brain" without explaining
how (or that it can't fully prevent it). Weak answers
lack the FAILURE SCENARIO and the WHY.

**Level 3 - Strong answer pattern:**
Every strong answer to a distributed systems question
covers: mechanism (how it works), failure case (when
it breaks), recovery (how you fix it), and trade-off
(what you give up to get this property).

**Level 4 - Connecting concepts:**
Staff interviewers often ask: "How does Raft's commit
rule relate to vector clocks?" The answer requires
understanding both and their shared purpose: causality
tracking for safe ordering of events. Concepts are
connected through the shared problems they solve.

**Level 5 - The evaluation framework:**
Interviewers evaluate: precision (right terms),
depth (not just what but why and when), trade-off
awareness (when not to use this), and production
credibility (what breaks in practice, how you
diagnosed it). Each of the 25 questions above tests
at least one of these dimensions.

---

### 💻 Code Example

```python
# Interview exercise: explain this code's invariant

import time
from threading import Lock, Thread

class DistributedKVClient:
    """
    Simple KV client with version-checked writes.
    Can you identify: what guarantee does this provide?
    What failure does it NOT protect against?
    """

    def __init__(self, etcd_client, db_conn):
        self.etcd = etcd_client
        self.db = db_conn

    def conditional_write(
        self, key: str, value: str, expected_version: int
    ) -> bool:
        """
        Write value only if current DB version
        equals expected_version.
        Returns True if write succeeded.
        """
        rows = self.db.execute(
            """
            UPDATE kv_store
            SET value = %s, version = version + 1
            WHERE key = %s AND version = %s
            """,
            (value, key, expected_version)
        )
        return rows.rowcount == 1

# INTERVIEW QUESTION:
# What distributed systems concept does this implement?
# (Answer: optimistic concurrency control / OCC)
# What failure does it prevent?
# (Answer: lost update under concurrent writes)
# What failure does it NOT prevent?
# (Answer: does not prevent phantom reads, does not
# handle distributed transactions spanning multiple keys,
# does not handle partition where two nodes independently
# accept writes to the same key with the same version)
```

---

### ⚖️ Comparison Table

| Question Type | Tests | Strong Signal | Weak Signal |
|---|---|---|---|
| "How does X work?" | Mechanism knowledge | Explains WHY, not just HOW; includes failure case | Describes API/interface only |
| "What happens when..." | Failure mode knowledge | Traces the exact failure path; names the invariant that's violated | "It fails gracefully" without specifics |
| "Design a system" | Trade-off reasoning | Names the consistency/availability choice and defends it | Names the right technology without defending the choice |
| "Why does X require N nodes?" | Mathematical reasoning | Provides the quorum overlap argument | States the number without proof |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Name-dropping (etcd, Raft, PBFT) impresses interviewers" | Names without explanation impress no one. "We use etcd" is nothing; "we use etcd because we need consistent leader election with Raft's safety guarantees, which PBFT would also provide but at 3x the node cost" is a strong answer. |
| "The interviewer wants the 'correct' answer" | Staff interviews probe understanding, not memorization. A wrong answer with good reasoning ("I would try X because of Y, though I'm not certain that handles Z") is stronger than a correct answer recited without understanding. |
| "Failure cases are negative - focus on the happy path" | Failure cases are what interviewers care about most. The happy path is assumed. The question is: what breaks and how do you handle it? |

---

### 🚨 Failure Modes & Diagnosis

**Not included** - this is a META entry (interview prep).
The failure modes are embedded in each Q&A answer above.

---

### 🔗 Related Keywords

All DST-062 through DST-071 entries.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STRONG ANSWER FORMULA:                                  │
│ Mechanism + Failure case + Recovery + Trade-off         │
├─────────────────────────────────────────────────────────┤
│ RAFT:    Commit rule (current term only) + Figure 8     │
│          nextIndex backtracking + brief dual leader ok  │
├─────────────────────────────────────────────────────────┤
│ LEASE:   (election_timeout - 2*clock_skew) formula     │
│          Jeopardy state on missed keepalive             │
├─────────────────────────────────────────────────────────┤
│ LOCKING: Redlock = efficiency, not safety               │
│          Fencing token = storage WHERE last_token < :t  │
├─────────────────────────────────────────────────────────┤
│ BFT:     3f+1 proof via quorum overlap argument        │
│          PBFT: pre-prepare/prepare/commit - all needed  │
├─────────────────────────────────────────────────────────┤
│ SPANNER: Commit wait proof: s2 > s1 via TT.after(s1)   │
├─────────────────────────────────────────────────────────┤
│ DYNAMO:  Sloppy quorum breaks W+R>N under partition    │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The pattern that separates strong from weak distributed
systems answers in interviews is the same pattern
that separates senior from junior engineers in
production: the ability to trace from symptom to root
cause through the system's invariants. "Split-brain
happened" is a symptom. "The election timeout was
shorter than the maximum network blip duration, so
a false election fired; the old leader had no
mechanism to detect its lease had expired; storage
had no fencing token to reject the stale write"
is the root cause chain. Every concept in DST has:
an invariant it maintains, a condition under which
that invariant breaks, and a recovery mechanism.
Knowing all three for each concept is the difference
between "I've read about it" and "I can use it."

---

### 💡 The Surprising Truth

In practice, interviewers at staff engineer level
are not testing whether you know that Raft uses
quorum or that BFT needs 3f+1. These facts are
easily looked up. They are testing whether you can
think through an unfamiliar scenario and arrive at
a reasonable conclusion. The most common interview
question format is "here's a scenario; what do you
do?" - not "what is the formula for X?" The way to
prepare is not memorization but deliberate practice:
take each concept, construct a novel failure scenario,
and work through the diagnosis and fix without
looking at the answer. The 25 questions above can
all be practiced this way: cover the model answer,
construct your own answer, then compare.

---

### ✅ Mastery Checklist

1. [ANSWER] Answer Q1 (Raft commit rule) without
   reading the model answer. Compare your answer.
   Did you cover: the Figure 8 scenario, the indirect
   commit mechanism, the safety violation without the rule?
2. [ANSWER] Answer Q8 (Redlock critique) without
   reading the model answer. Did you construct the
   GC pause timeline: acquire, pause, TTL expire,
   second acquire, resume, two holders?
3. [CONNECT] Without looking at the entry: connect
   Raft's commit rule to vector clock causality tracking.
   What shared problem do they both solve?
4. [PRACTICE] Find a friend or colleague and run
   through 5 questions from this entry as a mock
   interview. Ask them to give model answers. Ask
   yourself: did I get to the failure case?
5. [EXTEND] Write 5 additional questions not covered
   here, covering: conflict-free replicated data types
   (CRDTs), Hybrid Logical Clocks vs TrueTime, and
   chaos engineering methodology.
