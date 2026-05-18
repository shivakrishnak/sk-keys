---
id: DST-066
title: Spanner and TrueTime
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-013, DST-016, DST-059
used_by: []
related: DST-013, DST-016, DST-052, DST-059
tags:
  - distributed
  - spanner
  - truetime
  - google
  - external-consistency
  - global-transactions
  - clocks
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 66
permalink: /technical-mastery/distributed-systems/spanner-and-truetime/
---

⚡ TL;DR - Google Spanner achieves externally
consistent global transactions using TrueTime, a
GPS+atomic-clock API that exposes clock uncertainty
as an interval [earliest, latest] rather than a
point; a transaction's commit timestamp is chosen
after TT.now().latest, and the transaction waits
(commit wait) until TT.now().earliest > commit_ts
before releasing, guaranteeing that any later
transaction's start is always after the commit;
epsilon (average uncertainty) is 7ms.

---

### 📋 Entry Metadata

| #066 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | MVCC, Clock Synchronization, Consistency Levels | |
| **Used by:** | N/A (Google internal + Cloud Spanner) | |
| **Related:** | Hybrid Logical Clocks, MVCC, Consistency at Every Level | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Traditional distributed databases face a dilemma:
- Strict serializability (linearizability) requires
  a single coordination point, which limits throughput
  and introduces a single point of failure.
- Partitioned databases (Dynamo, Cassandra) sacrifice
  consistency for availability.
- Paxos-based systems provide consistency but are
  bound to a single region for latency reasons.

No system before Spanner could provide:
- Globally distributed reads and writes
- Externally consistent (strict serializable) transactions
- Horizontal scalability across regions

The fundamental problem: to order transactions globally,
you need a global clock. But clock synchronization
(NTP) has milliseconds of uncertainty. How do you
make ordering decisions when you don't know precisely
what time it is?

**THE INSIGHT:** Don't pretend the clock is accurate.
Expose the uncertainty. Wait it out.

---

### 📘 Textbook Definition

**Spanner** (Google, 2012): a globally distributed
database system that provides externally consistent
distributed transactions at global scale. It is
the production database behind Google's advertising,
payment, and internal systems, and is available as
Google Cloud Spanner.

**TrueTime API:** a time service that exposes clock
uncertainty explicitly:

```
TT.now()   → TTinterval: [earliest, latest]
TT.after(t) → bool: "is t definitely in the past?"
TT.before(t) → bool: "is t definitely in the future?"
```

Where:
- `earliest` = lower bound on actual current time
- `latest` = upper bound on actual current time
- `epsilon` = (latest - earliest) / 2 (average ~7ms)

**External consistency:** if transaction T1 commits
before T2 begins, then T1's commit timestamp < T2's
commit timestamp. This is the same as strict
serializability or linearizability for transactions.

---

### ⏱️ Understand It in 30 Seconds

```
THE TRUETIME COMMIT PROTOCOL:

1. Begin transaction: s_start = TT.now().latest
   (pessimistic: assume the latest possible start time)

2. Execute transaction: read data at s_start,
   apply writes to pending state.

3. Assign commit timestamp:
   s_commit = max(s_start, paxos_leader_max_ts + 1)
   s_commit must be > any previously assigned ts.

4. COMMIT WAIT:
   while TT.now().earliest <= s_commit:
       wait()  # Wait until s_commit is in the past
   
   WHY: ensures s_commit is now DEFINITELY in the past.
   Any new transaction starting now will see
   TT.now() with earliest > s_commit.
   Therefore: new transaction's start > s_commit.
   Therefore: T1 commit < T2 start (external consistency).

5. Apply writes. Transaction is visible.

COST: ~14ms average wait (2 * epsilon, epsilon ~= 7ms)
HARDWARE: GPS receivers + atomic clocks in every
  Google data center.
  GPS satellites = stratum 1 time source.
  Atomic clocks = local fallback if GPS interrupted.
  Combined: epsilon < 7ms on average.
```

---

### 🔩 First Principles Explanation

**WHY CLOCK UNCERTAINTY MATTERS:**

```
SCENARIO WITHOUT TRUETIME:
  Data center A (US-East): T1 commits at 12:00:00.000
  Data center B (US-West): T2 begins at 12:00:00.003
  
  Real time difference: 3ms.
  T1 committed before T2 started.
  
  PROBLEM: NTP accuracy is ~100ms to 1ms between
  data centers. If B's clock is 5ms behind A's:
  B sees T2.start = 11:59:59.998
  A sees T1.commit = 12:00:00.000
  
  B's clock says T2 started BEFORE T1 committed.
  But actually T2 started AFTER T1 committed.
  
  With Spanner's serializable MVCC: if T2 reads at
  T2.start and T1.commit > T2.start (in A's clock):
  T2 sees STALE DATA. T1's writes are not yet visible.
  
  External consistency violated: T1 committed before
  T2 started, but T2 cannot see T1's writes.
  
TRUETIME SOLUTION:
  Expose uncertainty. Use [earliest, latest] interval.
  Wait until the entire universe agrees: T1's
  commit timestamp is in the past, even accounting
  for the worst-case clock error.
```

**THE COMMIT WAIT MECHANISM IN DETAIL:**

```
T1 commit timeline:
  TT.now() at commit time = [t-ε, t+ε]
  Assign commit ts = t+ε  (latest possible time)
  
  Wait until TT.now().earliest > t+ε
  This means: real time is definitely > t+ε
  
  So: TrueTime has guaranteed that the real commit
  time is some value in [t-ε, t+ε], and we've
  WAITED until even the earliest possible real time
  is past t+ε.
  
  Result: any future transaction that calls
  TT.now() will get earliest >= t+ε.
  Its start ts will be >= t+ε > T1's commit ts.
  
  T1 is guaranteed to be ordered before T2.
  This is external consistency.

COST:
  Average wait = epsilon = ~7ms.
  Worst case = 2*epsilon = ~14ms per transaction commit.
  For read-heavy workloads: stale reads can specify
  a timestamp in the past (no commit wait needed).
  For read-write transactions: pay the commit wait.
```

**SPANNER ARCHITECTURE:**

```
SPANNER HIERARCHY:
  Zone → Universe → Spanner
  
  Universe: all Spanner deployments globally.
  Zone: smallest unit of deployment (one data center).
    - Zone master (assigns tablet locations)
    - Span servers (store and serve data)
    - Location proxy (clients find tablet servers)
  
  Each zone has TrueTime hardware:
    TT Daemon: per-machine process that talks to
    GPS and atomic clock masters in the zone.
    Tracks epsilon (uncertainty bound).
    Advertises current [earliest, latest].
  
TABLET:
  A shard of row space.
  Stored in Colossus (Google's distributed filesystem).
  Each tablet is replicated via Paxos across 5 zones.
  Leader = Paxos leader for that tablet.
  
TRANSACTION EXECUTION:
  Client → finds tablet leaders for the rows it touches.
  
  Read-Only Transaction:
    Chooses a read timestamp = TT.now().latest
    Reads at that timestamp from any Paxos replica.
    No locks. No coordinator.
    Stale reads allowed (choose past timestamp).
    
  Read-Write Transaction:
    Wound-wait deadlock prevention (priority by age).
    Client coordinator manages 2PC across tablet leaders.
    Each shard leader participates in Paxos for its shard.
    Commit wait applied at coordinator.
```

**F1 MIGRATION (2012):**

```
Google migrated Google Ads from MySQL sharding to
Spanner via F1 (a SQL layer on top of Spanner).
  
Before: MySQL shards, manual resharding, downtime.
After: Spanner with F1, automated rebalancing,
  no downtime, external consistency.
  
F1 PERFORMANCE:
  Latency: ~5ms for reads, ~10-25ms for commits
  (commit wait adds ~7ms).
  Throughput: millions of transactions per second
  globally (2012 numbers; much higher today).
```

---

### 🧠 Mental Model / Analogy

> TrueTime is like a train schedule that admits
> uncertainty. Instead of "Train A arrives at 3:00 PM,"
> TrueTime says "Train A arrives between 2:57 PM
> and 3:03 PM." If you need to guarantee that your
> passenger makes Train B (which departs at 3:05 PM),
> you wait at the platform until 3:03 PM (the latest
> possible arrival of Train A). Once 3:03 passes,
> you are certain Train A has arrived, regardless
> of whether the station clock is slightly off.
> You've "committed" to the fact that Train A is done.
> Any new passenger arriving after 3:03 is guaranteed
> to see Train A as having already arrived.
> Commit wait = waiting until 3:03 before declaring
> "Train A has arrived" to the world.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The core idea:**
Spanner is a global database that can do transactions
across multiple continents. It uses a special time
service (TrueTime) to order those transactions
correctly without a centralized coordinator.

**Level 2 - Clock uncertainty is the problem:**
Clocks in different data centers are not perfectly
synchronized. NTP can drift by milliseconds. If
you assign timestamps to transactions using a drifting
clock, you can't guarantee the timestamps reflect
real causal order. TrueTime measures this drift and
exposes it.

**Level 3 - Commit wait is the solution:**
A transaction waits before becoming visible until
TrueTime confirms that the commit timestamp is
definitely in the past (even accounting for clock
uncertainty). This ensures that any future transaction's
start time is after this commit time, everywhere.

**Level 4 - This enables external consistency:**
External consistency = strict serializability = if T1
committed before T2 started, T1's ts < T2's ts.
Commit wait ensures this by construction. Spanner
is the only distributed database to provide this
guarantee at global scale.

**Level 5 - Trade-offs and when to use Spanner:**
Commit wait costs ~7ms per transaction. This is
acceptable for Google Ads but may be high for
ultra-low-latency systems. Read-only transactions
are cheap (no commit wait, can use any replica).
Use Spanner when: you need ACID transactions across
multiple shards, you need external consistency,
and you can tolerate ~10-25ms commit latency.
Not suitable for: sub-millisecond latency workloads,
pure caching, write-heavy workloads where 7ms per
commit is unacceptable.

---

### 💻 Code Example

**Simulating Commit Wait with TrueTime Semantics**

```python
# BAD: Using wall clock time for distributed transactions
import time

class BadDistributedDB:
    def commit_transaction(self, writes: dict):
        # Assign timestamp using local wall clock:
        commit_ts = time.time_ns()
        
        # IMMEDIATELY apply writes:
        self._apply_writes(writes, commit_ts)
        
        return commit_ts
        # PROBLEM: If clock is off by 5ms, and another
        # data center's transaction starts at the real
        # time we just committed, their start timestamp
        # (from their clock) may be LESS than our
        # commit_ts. External consistency violated.
```

```python
# GOOD: TrueTime-inspired commit with uncertainty window

import time
import threading
from dataclasses import dataclass

@dataclass
class TTInterval:
    earliest: float  # seconds since epoch
    latest: float

class TrueTimeClock:
    """
    Simplified TrueTime simulation.
    In production: backed by GPS + atomic clocks.
    epsilon = uncertainty half-width in seconds.
    """
    def __init__(self, epsilon_seconds: float = 0.007):
        self.epsilon = epsilon_seconds

    def now(self) -> TTInterval:
        wall = time.time()
        return TTInterval(
            earliest=wall - self.epsilon,
            latest=wall + self.epsilon
        )

    def after(self, t: float) -> bool:
        """Returns True if t is DEFINITELY in the past."""
        return self.now().earliest > t

    def before(self, t: float) -> bool:
        """Returns True if t is DEFINITELY in the future."""
        return self.now().latest < t


class SpannerLikeTransaction:
    def __init__(self, tt: TrueTimeClock):
        self.tt = tt
        self._data: dict = {}
        self._committed_at: dict = {}  # ts -> {writes}

    def commit(self, writes: dict) -> float:
        """
        Commit transaction with TrueTime commit wait.
        Returns the commit timestamp.
        """
        # 1. Choose commit timestamp = latest possible now
        interval = self.tt.now()
        commit_ts = interval.latest

        # Commit timestamp must also be > any previously
        # assigned timestamp (monotonicity):
        if self._committed_at:
            last_ts = max(self._committed_at.keys())
            commit_ts = max(commit_ts, last_ts + 0.000001)

        # 2. COMMIT WAIT: block until commit_ts is
        #    DEFINITELY in the past:
        while not self.tt.after(commit_ts):
            # Average wait = epsilon ~ 7ms
            # This is the "wait out the uncertainty"
            time.sleep(0.001)

        # 3. Now it is safe to apply writes.
        #    Any future transaction calling TT.now()
        #    will see earliest > commit_ts.
        self._committed_at[commit_ts] = writes
        for k, v in writes.items():
            self._data[k] = (v, commit_ts)

        return commit_ts  # ~7ms after commit started

    def read_at(self, key: str, timestamp: float):
        """
        Read the value of key as of a given timestamp.
        Returns the most recent value with ts <= timestamp.
        """
        best_val, best_ts = None, -1
        for ts, writes in self._committed_at.items():
            if ts <= timestamp and ts > best_ts:
                if key in writes:
                    best_val = writes[key]
                    best_ts = ts
        return best_val

# External consistency test:
tt = TrueTimeClock(epsilon_seconds=0.007)
db = SpannerLikeTransaction(tt)

# T1: commits "x=1"
ts1 = db.commit({"x": 1})
print(f"T1 committed at {ts1:.6f}")

# T2: starts AFTER T1 committed
time.sleep(0.001)  # Simulates T2 starting after T1
t2_start = tt.now().latest  # Pessimistic start time

# T2 reads: must see T1's write
val = db.read_at("x", t2_start)
assert val == 1, f"External consistency violated: saw {val}"
print(f"T2 reads x={val} (correct: T1 committed before T2)")
```

---

### ⚖️ Comparison Table

| System | Consistency | Latency | Multi-Region | Notes |
|---|---|---|---|---|
| **MySQL / PostgreSQL** | Serializable | Sub-ms (single region) | No | Single-host or manual sharding |
| **CockroachDB** | Serializable | 5-20ms | Yes | Hybrid Logical Clocks; no GPS hardware |
| **YugabyteDB** | Serializable | 5-20ms | Yes | HLC-based; inspired by Spanner |
| **Google Spanner** | External consistency (strict serializable) | 10-25ms commits | Yes | GPS + atomic clock hardware required |
| **Cassandra** | Eventual | Sub-ms | Yes | No transactions; tunable consistency |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Spanner uses NTP for TrueTime" | NTP is used as a fallback but is not the primary source. Google's data centers use GPS receivers and atomic clocks as stratum 1 sources. This reduces epsilon to ~7ms, far better than NTP's 100ms+ variance across the internet. |
| "Commit wait makes Spanner slow" | Commit wait adds ~7ms per read-write transaction. For OLTP workloads with mostly reads, read-only transactions (which use stale reads and have no commit wait) are very fast. The 7ms cost only applies to the commit path. |
| "External consistency is the same as serializable" | They are different: serializable means there exists some serial order. Externally consistent (strictly serializable) means the serial order matches real time: if T1 committed in real time before T2 started in real time, T1 is ordered before T2. Serializable without external consistency can reorder T1 and T2 in the serial history. |
| "You need GPS hardware to use Spanner" | Google Cloud Spanner provides TrueTime as a managed service. You do not need GPS hardware. Cloud Spanner users get external consistency without managing hardware; Google's data centers handle TrueTime internally. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Reads in Cross-Region Reads**

**Symptom:** After a write commits in region A, a
read from region B returns the old value. The write
succeeded (got commit timestamp). But the read
(immediately after) sees the pre-write state.

**Root Cause:** The read was issued with a stale
read timestamp. In Spanner, read-only transactions
can specify a "read exact staleness" (e.g., read as
of 10 seconds ago) for lower latency. If the
application used a stale read timestamp that predates
the write, it correctly returns the old value.

**Diagnosis:**
```sql
-- Cloud Spanner: check read staleness setting
-- in your client library configuration.
-- Default for read-only transactions:
-- "strong reads" = reads at current timestamp (latest).
-- "stale reads" = reads at a past timestamp.

-- In Java client:
-- ReadContext ctx = client.singleUseReadOnlyTransaction(
--     TimestampBound.ofExactStaleness(10, TimeUnit.SECONDS)
-- );  -- This reads 10 seconds in the past!

-- For consistent cross-region reads:
-- Use strong reads (default) or bound staleness
-- with a very small window (e.g., 1-2 seconds).

-- Check: what timestamp is your read using?
-- If timestamp < commit_ts of your write:
-- the stale read is correct (not a bug).
-- Fix: use strong reads for consistency-critical paths.
```

**Fix:** Use strong reads (no staleness bound) for
consistency-critical operations. Use stale reads
only for analytics, caches, or other scenarios where
slightly old data is acceptable.

---

### 🔗 Related Keywords

**Prerequisites:** `MVCC` (DST-013),
`Clock Synchronization` (DST-016),
`Distributed Consistency Explained at Every Level` (DST-059)

**Related:** `Hybrid Logical Clocks` (DST-052)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ TRUETIME    │ TT.now() → [earliest, latest]             │
│ API         │ epsilon ~ 7ms (GPS + atomic clock)        │
├─────────────┼─────────────────────────────────────────--┤
│ COMMIT WAIT │ Wait until TT.after(commit_ts)           │
│             │ = real time definitely past commit_ts    │
│             │ Cost: ~7ms average per RW transaction    │
├─────────────┼───────────────────────────────────────────┤
│ EXTERNAL    │ T1 committed before T2 started           │
│ CONSISTENCY │ → T1.commit_ts < T2.start_ts            │
│             │ = strict serializability                │
├─────────────┼───────────────────────────────────────────┤
│ HARDWARE    │ GPS receivers + atomic clocks per zone  │
│             │ TT daemon per machine                   │
├─────────────┼───────────────────────────────────────────┤
│ ONE-LINER   │ "Spanner: wait out clock uncertainty    │
│             │  to achieve global external consistency"│
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Spanner's design embodies the principle of making
implicit assumptions explicit. Every distributed
system that uses timestamps implicitly assumes that
clocks are accurate. Spanner instead asks: how
inaccurate is the clock, precisely? And designs
the protocol around the uncertainty bound. This
pattern - acknowledging and quantifying uncertainty
rather than ignoring it - appears throughout
distributed systems: quorum protocols acknowledge
that some nodes may be slow (wait for f+1 of N,
not all N); circuit breakers acknowledge that
some fraction of requests will be slow (track
failure rate, not individual failures); SLOs
acknowledge that not every request can succeed
(99.9% target, not 100%). The Spanner team's insight
was that "unknown clock error" is worse than
"known bounded clock error." By investing in GPS
hardware, they bounded epsilon to 7ms and could
design a precise, correct protocol. Unknown
uncertainty would require assuming infinite error,
making global consistency impossible.

---

### 💡 The Surprising Truth

The Spanner paper (Corbett et al., OSDI 2012)
describes TrueTime as providing epsilon < 10ms in
practice, with an average of 4ms. This was
achievable because Google installed GPS receivers
AND atomic clocks in every data center. Why both?
GPS signals can be jammed or disrupted (this has
happened). Atomic clocks (cesium or rubidium) are
the fallback: they drift slowly (~1 microsecond
per second) and bridge the gap during GPS outages.
The combination means epsilon rarely exceeds 7ms
even during GPS disruptions. This hardware investment
(GPS + atomic clocks per data center) is why public
cloud providers cannot simply copy Spanner exactly.
CockroachDB and YugabyteDB use Hybrid Logical Clocks
(HLC) as a software approximation, which provides
serializability (not strict serializability) without
GPS hardware, at the cost of slightly weaker
guarantees: they must consult a Paxos quorum for
reads (to ensure they've seen all committed data)
rather than using TrueTime's bounded wait.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Walk through TrueTime's commit wait.
   Why is waiting until TT.after(commit_ts) sufficient
   to guarantee external consistency? What would
   happen if we skipped the wait?
2. [CONTRAST] External consistency vs serializable:
   give a concrete example where a serializable
   (but not externally consistent) system produces
   a result that violates real-time ordering.
3. [DESIGN] A global e-commerce platform needs
   globally consistent inventory deduction. Should
   it use Google Cloud Spanner or CockroachDB?
   What are the key trade-offs (latency, cost,
   consistency guarantees, operational complexity)?
4. [CALCULATE] If epsilon = 7ms, what is the
   minimum additional latency added by commit wait?
   What is the maximum? How does this compare to
   a typical network round trip within a region?
5. [CRITIQUE] A team argues: "We can achieve external
   consistency with NTP by using commit wait with a
   much larger epsilon (e.g., 200ms)." Is this
   correct? What are the drawbacks?
