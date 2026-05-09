# ALWAYS use pwsh to execute this script:
# pwsh -ExecutionPolicy Bypass -File tmp\write_dst018_020_031_034_036.ps1

Set-Location "c:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-5-distributed-architecture\DST-distributed-systems"

# ─── DST-018 - Hybrid Logical Clocks (HLC) ────────────────────────────────
$dst018 = @'
---
id: DST-018
title: Hybrid Logical Clocks (HLC)
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-015, DST-016, DST-017
used_by: DST-019, DST-021
related: DST-015, DST-016, DST-017
tags:
  - distributed
  - clocks
  - causality
  - deep-dive
  - advanced
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /distributed-systems/hybrid-logical-clocks/
---

# DST-018 - Hybrid Logical Clocks (HLC)

⚡ **TL;DR** — HLC merges wall-clock time with logical time so events carry
real timestamps while still preserving causal ordering, without requiring
global clock synchronization.

| Relationship    | IDs                                     |         |
| --------------- | --------------------------------------- | ------- |
| **Depends on:** | DST-015, DST-016, DST-017               |         |
| **Used by:**    | DST-019, DST-021                        |         |
| **Related:**    | DST-015, DST-016, DST-017               |         |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Lamport clocks (DST-015) give causal ordering but lose wall-clock
meaning — you cannot tell if event A happened before or after noon.
Physical clocks give real time but diverge by milliseconds across
nodes, so you cannot safely use them to order concurrent events.

**THE BREAKING POINT:**
Spanner (Google, 2012) needs globally-ordered reads with real
timestamps. If clock drift causes a stale read to appear "newer"
than it is, the database returns wrong data. Neither pure logical
clocks nor raw NTP clocks are sufficient alone.

**THE INVENTION MOMENT:**
Kulkarni et al. (2014) published HLC: encode both a physical
component `l` (max known wall time) and a logical counter `c` into
a single 64-bit timestamp. Update rules keep `l` as close to true
wall time as possible while `c` breaks ties and preserves causality.

**EVOLUTION:**
HLC is now embedded in CockroachDB, YugabyteDB, and FoundationDB
transaction layers. TrueTime (Spanner) uses GPS+atomic hardware
to bound uncertainty; HLC trades hardware for a software
approximation that works with commodity NTP.

---

### 📘 Textbook Definition

A **Hybrid Logical Clock (HLC)** is a timestamp scheme for
distributed systems that combines a physical clock component and a
logical counter. Each node maintains `(l, c)` where `l` is the
largest physical time the node has observed and `c` is a counter
that increments only when `l` does not advance. HLC timestamps are
comparable: `(l1,c1) < (l2,c2)` iff `l1 < l2`, or `l1 == l2` and
`c1 < c2`. They guarantee that if event A causally precedes B then
`hlc(A) < hlc(B)`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** HLC = Lamport clock + wall clock, packed into one
timestamp that is both causal and human-readable.

> Like a receipt printer that always shows the correct date AND
> stamps sequential numbers when two receipts print in the same
> second - you know both WHEN and in what ORDER.

**One insight:** HLC solves the either/or dilemma: use NTP and
risk causality violations, or use Lamport and lose real time.
HLC gives you both, bounded by max clock skew.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Causality: if A -> B (A happened-before B) then
   `hlc(A) < hlc(B)`.
2. Closeness: `|l - physicalClock| <= maxSkew` at all times.
3. Uniqueness: no two events at the same node share the same HLC.
4. Monotonicity: HLC never goes backward on a single node.

**DERIVED DESIGN:**
Each node tracks `(l, c)`. On local event or NTP tick: if
`physicalClock > l`, set `l = physicalClock`, `c = 0`.
On send: piggyback `(l, c)`. On receive `(l', c')`:
`l_new = max(l, l', physicalClock)`; if `l_new == l == l'`,
`c = max(c, c') + 1`; if `l_new == l`, `c++`; else `c = 0`.

**THE TRADE-OFFS:**
**Gain:** Events carry meaningful wall timestamps; causal ordering
maintained without GPS hardware; 64-bit timestamp fits standard
integer fields.
**Cost:** HLC timestamps are only correct up to `maxSkew` (usually
250 ms to 1 s). Queries spanning that window risk anomalies.
Clock jumps (NTP step adjustments) can briefly break the closeness
invariant.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Encoding two dimensions (physical + logical) into
one comparable value is inherently the challenge.
**Accidental:** Choosing bit widths for `l` vs `c` within 64 bits;
handling NTP leap seconds and step corrections gracefully.

---

### 🧪 Thought Experiment

**SETUP:** Two database nodes A and B. Node A's NTP clock is 200 ms
ahead of B's. A transaction writes to A then sends a message to B.

**WHAT HAPPENS WITHOUT HLC:**
Using raw NTP: B's timestamp for its reply is earlier than A's
write timestamp. The database sees the reply as happening "before"
the write — causality violation; a read-your-writes guarantee
breaks.
Using pure Lamport: B can order the events correctly, but a human
inspecting the log sees timestamps like `42, 43, 44` instead of
real times, making audit and debugging impossible.

**WHAT HAPPENS WITH HLC:**
A sends `(l=1000200, c=0)`. B receives it, sees its own physical
clock at `1000000`, so sets `l=1000200, c=1`. B's response carries
`(1000200, 1)`. The causality chain `A -> B` is preserved AND both
timestamps are within 200 ms of real wall time.

**THE INSIGHT:** HLC uses the physical component as a "fast path"
that is almost always enough. The logical counter fires only when
physical time stalls — which happens rarely in practice.

---

### 🧠 Mental Model / Analogy

> Imagine a courtroom clock that shows the real time of day, but
> when two witnesses speak simultaneously, the bailiff adds a
> suffix: "10:30:00.000-A", "10:30:00.000-B". Real time gives
> context; the suffix breaks ties without losing the timestamp.

Element mapping:
- Real time of day = physical component `l`
- Bailiff's suffix = logical counter `c`
- Speaking simultaneously = concurrent events with same `l`
- Hearing another witness first = receiving a message (updates `l`)

Where this analogy breaks down: real courtrooms have one clock;
HLC must work with many clocks that are slightly wrong and that
each node can only read locally.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Every message in the system carries a timestamp that looks like a
real clock time AND guarantees that earlier events always have
smaller timestamps — even if the clocks on different computers are
slightly out of sync.

**Level 2 - How to use it (junior developer):**
Replace `System.currentTimeMillis()` with `hlc.tick()` on sends
and `hlc.update(receivedTimestamp)` on receives. Store the 64-bit
HLC value in your event log. Use it for ordering and conflict
resolution instead of raw wall time.

**Level 3 - How it works (mid-level engineer):**
HLC maintains `(l, c)` per node. `l` is updated to
`max(l, physicalClock, l_received)` on every event. `c` increments
only when `l` does not change, resetting to 0 on each `l` advance.
The 64-bit encoding: upper 48 bits = `l` in milliseconds, lower
16 bits = `c` (max 65535 concurrent events per millisecond per node).

**Level 4 - Why it was designed this way (senior/staff):**
TrueTime (Spanner) uses atomic clocks to bound uncertainty to <7 ms.
That requires expensive hardware per datacenter. HLC offers a
software approximation: bound uncertainty by `maxSkew` (typically
NTP accuracy ~250 ms). The key insight is that in practice, most
events are separated by more than `maxSkew`, so `l` advances
normally and `c` stays at 0. The logical counter is an escape
hatch for bursts of concurrent events — it costs nothing when not
needed.

**Expert Thinking Cues:**
- "What is my NTP `maxSkew` budget and have I set HLC bounds
  accordingly?"
- "Am I handling NTP step corrections (forward or backward jumps)?"
- "What happens if `c` overflows 16 bits during a burst?"

---

### ⚙️ How It Works (Mechanism)

```
On LOCAL EVENT or SEND:
  l_new = max(l, physicalClock())
  if l_new == l: c = c + 1
  else: l = l_new; c = 0
  timestamp = (l, c)

On RECEIVE(l', c'):
  l_new = max(l, l', physicalClock())
  if l_new == l AND l_new == l': c = max(c, c') + 1
  elif l_new == l:                c = c + 1
  elif l_new == l':               c = c' + 1
  else:                           c = 0
  l = l_new
```

**64-bit encoding:**
```
| 48 bits (l, milliseconds epoch) | 16 bits (c) |
```
Allows `l` up to year 10889 and up to 65535 concurrent events
per millisecond per node.

**Comparison semantics:**
```java
// (l1,c1) < (l2,c2)
boolean before(long hlc1, long hlc2) {
    long l1 = hlc1 >>> 16, c1 = hlc1 & 0xFFFF;
    long l2 = hlc2 >>> 16, c2 = hlc2 & 0xFFFF;
    return l1 < l2 || (l1 == l2 && c1 < c2);
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Node A                   Node B
  |                        |
  |-- local event -------> |
  |   hlc.tick()           |
  |   ts=(1000200,0)       |
  |                        |
  |-- send msg ----------> |
  |   payload + ts         |
  |                        |   <- YOU ARE HERE
  |                        |-- hlc.update(1000200,0)
  |                        |   physClock=1000000
  |                        |   l_new=1000200, c=1
  |                        |   ts=(1000200,1)
  |                        |
  |                        |-- local write
  |                        |   ts=(1000200,2)
```

**FAILURE PATH:**
NTP step correction jumps clock back 500 ms on Node B. If `l`
at B was `T`, now `physicalClock < l`. HLC detects this: since
`max(l, physicalClock, l') = l` (unchanged), it simply increments
`c`. The closeness invariant `|l - physicalClock| <= maxSkew` is
temporarily violated. Recovery: when `physicalClock` catches up
past `l` again, `l` advances and `c` resets.

**WHAT CHANGES AT SCALE:**
At high throughput (> 65535 events/ms per node), `c` overflows.
Production systems add overflow detection and either reject or
stall for 1 ms. CockroachDB uses a 10-bit logical counter and
wider physical bits to avoid this in practice.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
HLC does NOT replace a consensus protocol. Two nodes can still
see `hlc(A) < hlc(B)` even if A and B are concurrent (not
causally related). HLC is a best-effort causality tracker; Raft
or Paxos is required for decisions requiring strict agreement.

---

### 💻 Code Example

```java
// BAD: using raw wall clock for distributed event ordering
public long timestamp() {
    // Causality violation possible under clock skew
    return System.currentTimeMillis();
}

// GOOD: HLC implementation
public class HybridLogicalClock {
    private long l = 0; // physical component (ms)
    private long c = 0; // logical counter

    // Call on local event or before sending
    public synchronized long tick() {
        long pt = System.currentTimeMillis();
        long lNew = Math.max(l, pt);
        if (lNew == l) { c++; } else { l = lNew; c = 0; }
        return encode(l, c);
    }

    // Call on message receive
    public synchronized long update(long received) {
        long lR = received >>> 16;
        long cR = received & 0xFFFFL;
        long pt = System.currentTimeMillis();
        long lNew = Math.max(Math.max(l, lR), pt);
        if (lNew == l && lNew == lR) {
            c = Math.max(c, cR) + 1;
        } else if (lNew == l) {
            c++;
        } else if (lNew == lR) {
            c = cR + 1;
        } else {
            c = 0;
        }
        l = lNew;
        return encode(l, c);
    }

    private long encode(long l, long c) {
        if (c > 0xFFFFL) throw new RuntimeException(
            "HLC counter overflow");
        return (l << 16) | (c & 0xFFFFL);
    }

    public static boolean happenedBefore(long a, long b) {
        long lA = a >>> 16, cA = a & 0xFFFFL;
        long lB = b >>> 16, cB = b & 0xFFFFL;
        return lA < lB || (lA == lB && cA < cB);
    }
}
```

**How to test / verify correctness:**
```java
HybridLogicalClock hlc = new HybridLogicalClock();
long ts1 = hlc.tick();
long ts2 = hlc.tick();
assert HybridLogicalClock.happenedBefore(ts1, ts2);

// Simulate receiving a message from a node 500ms ahead
long remoteTs = ((System.currentTimeMillis() + 500L) << 16) | 3L;
long ts3 = hlc.update(remoteTs);
assert HybridLogicalClock.happenedBefore(remoteTs, ts3);
```

---

### ⚖️ Comparison Table

| Property              | Lamport Clock  | Vector Clock  | HLC            | TrueTime      |
| --------------------- | -------------- | ------------- | -------------- | ------------- |
| Causal ordering       | Yes            | Yes (exact)   | Yes (bounded)  | Yes (bounded) |
| Wall-clock readable   | No             | No            | Yes            | Yes           |
| Space per timestamp   | 1 integer      | N integers    | 1 integer      | 2 integers    |
| Hardware required     | None           | None          | None           | GPS + atomic  |
| Skew tolerance        | Unlimited      | Unlimited     | <= maxSkew     | < 7 ms        |
| Counter overflow risk | No             | No            | Yes (16-bit)   | No            |
| Used in production    | Rare           | Some DBs      | CockroachDB    | Spanner       |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "HLC gives exact real timestamps" | HLC gives timestamps within `maxSkew` of real time; the physical component is the max OBSERVED time, not the current clock |
| "HLC replaces consensus protocols" | HLC orders events within a node or along causal chains; it cannot decide global ordering for concurrent events — Raft/Paxos is still needed |
| "Higher HLC = more recent in wall time" | Two events with the same `l` are ordered by `c` — the one with higher `c` may have happened a millisecond BEFORE a lower-`c` event on another node |
| "NTP clock drift breaks HLC" | HLC is designed for drift; it breaks only on large step corrections (forward or backward) that exceed `maxSkew`, which NTP bounds to a few hundred ms |
| "You can safely use HLC timestamps as primary keys" | You can, but you must handle duplicate `l` values via `c` and allow for clock leap gaps in the key space |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Counter overflow**

**Symptom:** `RuntimeException: HLC counter overflow` under high
write throughput.
**Root Cause:** More than 65535 events per millisecond on a single
node exhaust the 16-bit logical counter.
**Diagnostic:**
```bash
# Check event rate per ms
grep "hlc.tick" app.log | awk -F'ms=' '{print $2}' \
  | sort | uniq -c | sort -rn | head
```
**Fix:**
```java
// BAD: fixed 16-bit counter
private long c = 0; // overflows at 65535/ms

// GOOD: detect and stall for 1ms
if (c > 0xFFFFL) {
    Thread.sleep(1);
    l = System.currentTimeMillis();
    c = 0;
}
```
**Prevention:** Size the counter for peak burst rate; add
monitoring on `c > threshold` (e.g. > 60000).

---

**Failure Mode 2: NTP step correction breaks closeness**

**Symptom:** HLC timestamps suddenly jump backward relative to
wall time; recent events appear older than they are.
**Root Cause:** NTP applies a step correction (abrupt clock jump)
rather than slewing (gradual adjustment). If the jump is larger
than `maxSkew`, the closeness invariant breaks temporarily.
**Diagnostic:**
```bash
# Detect NTP step events in system log
grep "ntpd\|chronyd" /var/log/syslog | grep "step\|offset"
```
**Fix:** Configure NTP to use only slew mode (`tinker panic 0;
tinker step 0` in ntpd.conf) or use `chrony` with `makestep`
limits to prevent large backward jumps.
**Prevention:** Use a bounded-skew service (PTP/IEEE 1588) in
high-precision environments; set alerts when NTP offset > 100 ms.

---

**Failure Mode 3: Stale HLC causing causal anomaly (security)**

**Symptom:** A replay attack sends an old event with a past HLC
timestamp; the receiver accepts it as "new" because HLC does not
authenticate timestamps.
**Root Cause:** HLC timestamps are not signed; an attacker can
replay an old message with its original timestamp and the
receiver's HLC update will simply not advance (since received
`l` < current `l`), making the replayed event appear causally
before current events.
**Fix:** Sign message payloads including HLC timestamps with HMAC
or a session key. Validate timestamp is within an acceptable
window (e.g. +/- 2 * maxSkew) before processing.
**Prevention:** Always combine HLC with message authentication;
treat timestamps as metadata, not as proof of freshness.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-015 - Lamport Clock (logical time foundation)
- DST-016 - Vector Clock (causal tracking with N-node vectors)
- DST-017 - Clock Skew / Clock Drift (physical clock problem HLC solves)

**Builds On This (learn these next):**
- DST-019 - Total Order / Partial Order (ordering implications)
- DST-021 - Happened-Before (causal relation HLC preserves)
- DST-028 - Quorum (distributed reads that rely on timestamp ordering)

**Alternatives / Comparisons:**
- Lamport Clock: causal only, no wall time
- Vector Clock: exact causality, O(N) space
- TrueTime: hardware-bounded uncertainty, requires GPS/atomic clocks

---

### 📌 Quick Reference Card

```
+-------------------------------------------------+
| WHAT IT IS    | Clock combining wall time + logic|
| PROBLEM SOLVES| Causality with human timestamps  |
| KEY INSIGHT   | l tracks max seen time; c breaks |
|               | ties without losing wall clock   |
| USE WHEN      | Need causal ordering AND readable|
|               | timestamps without GPS hardware  |
| AVOID WHEN    | NTP maxSkew > 1s or burst rate   |
|               | > 65K events/ms/node             |
| TRADE-OFF     | Bounded wall accuracy vs exact   |
|               | causality of vector clocks       |
| ONE-LINER     | Lamport + NTP packed in 64 bits  |
| NEXT EXPLORE  | DST-019 Total Order Broadcast    |
+-------------------------------------------------+
```

**If you remember only 3 things:**
1. HLC = `(max_seen_physical_time, logical_counter)` in 64 bits.
2. Causal ordering is preserved; wall timestamps are within
   `maxSkew` of real time — not exact.
3. The counter fires only when the physical component stalls;
   under normal load it stays at 0.

**Interview one-liner:** "HLC gives you Lamport clock causality
guarantees and wall-clock readability in a single 64-bit value,
at the cost of exact physical accuracy bounded by NTP skew."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When two properties seem
mutually exclusive (causal ordering vs. real timestamps), look for
a composite representation that gives you both within a bounded
approximation. Pure solutions are elegant; hybrid solutions are
practical.

**Where else this pattern appears:**
- **Database versioning:** MVCC uses a combination of transaction
  ID (logical) and commit timestamp (physical) — same hybrid idea.
- **Log aggregation:** Structured logs carry both `timestamp` (wall)
  and `sequence` (logical) so they can be sorted causally even when
  clocks diverge across log shippers.
- **Network protocols:** TCP sequence numbers are logical; combined
  with OS timestamps they allow both ordering and latency measurement.

---

### 💡 The Surprising Truth

HLC timestamps can appear to run FASTER than wall time. Because `l`
is defined as `max(l, physicalClock, l_received)`, a message from a
node whose clock is 200 ms ahead will push your local `l` forward
by 200 ms instantly. Your next local event then carries a timestamp
that is 200 ms "in the future" from your own clock's perspective.
In CockroachDB, this is called "clock offset" and is bounded by a
configurable `max-offset` (default 500 ms); exceeding it causes the
node to self-terminate rather than violate consistency guarantees.

---

### 🧠 Think About This Before We Continue

**Question A (System Interaction):** If Node A's physical clock
is 300 ms ahead of Node B's, and the system's configured `maxSkew`
is 250 ms, what happens when A sends a message to B?
*Hint:* Look at the update rule for `l_new` on receive and
consider whether the closeness invariant holds for B after the
update.

**Question B (Scale):** CockroachDB uses a 10-bit logical counter
instead of 16 bits. What does this trade off, and at what write
rate does overflow become a real risk?
*Hint:* Calculate events per millisecond at the overflow boundary,
then compare to a typical write-heavy OLTP workload.

**Question C (Design Trade-off):** Why does Google Spanner use
GPS-synchronized atomic clocks (TrueTime) instead of HLC, even
though HLC requires no special hardware?
*Hint:* Think about the difference between a bounded-uncertainty
commit wait and an approximation-based timestamp in the context
of globally distributed serializable reads.
'@

$f018 = Join-Path $base "DST-018 - Hybrid Logical Clocks (HLC).md"
[System.IO.File]::WriteAllText(
    (Resolve-Path ".").Path + "\" + $f018,
    $dst018,
    [System.Text.UTF8Encoding]::new($false))
Write-Host "Written DST-018: $((Get-Content $f018 -Encoding UTF8).Count) lines"

# ─── DST-020 - Total Order Broadcast ──────────────────────────────────────
$dst020 = @'
---
id: DST-020
title: Total Order Broadcast
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-019, DST-015, DST-022
used_by: DST-023, DST-024, DST-027
related: DST-019, DST-021, DST-023
tags:
  - distributed
  - consensus
  - ordering
  - deep-dive
  - advanced
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /distributed-systems/total-order-broadcast/
---

# DST-020 - Total Order Broadcast

⚡ **TL;DR** — Total Order Broadcast (TOB) guarantees every correct
node delivers every message in exactly the same order — the practical
mechanism that turns ordering theory into distributed agreement.

| Relationship    | IDs                                     |         |
| --------------- | --------------------------------------- | ------- |
| **Depends on:** | DST-019, DST-015, DST-022               |         |
| **Used by:**    | DST-023, DST-024, DST-027               |         |
| **Related:**    | DST-019, DST-021, DST-023               |         |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a distributed system, nodes broadcast messages independently.
Node A delivers `[M1, M2]`; Node B delivers `[M2, M1]`. Both are
valid partial orders — but if M1 and M2 are "debit account" and
"credit account" operations, the different orderings produce
different final balances. There is no agreement protocol, so state
diverges silently.

**THE BREAKING POINT:**
Database replication without TOB: a primary fails during a write;
two replicas independently become primary; each processes a
different backlog order; state machines diverge permanently. The
system appears healthy but returns different answers per replica.

**THE INVENTION MOMENT:**
Lamport (1978) showed in "Time, Clocks, and Ordering" that a
totally ordered sequence of messages is equivalent to a distributed
state machine. If you can build TOB, you can replicate ANY
deterministic service. This insight is the theoretical foundation
of Raft, Paxos, and ZooKeeper.

**EVOLUTION:**
Modern consensus algorithms (Raft DST-023, Multi-Paxos DST-024)
implement TOB internally. Kafka topic partitions deliver TOB within
a partition. ZooKeeper's ZAB protocol is a TOB implementation used
to coordinate distributed metadata.

---

### 📘 Textbook Definition

**Total Order Broadcast** (also called Atomic Broadcast) is a
communication primitive that satisfies three properties:
1. **Validity:** if a correct node broadcasts M, all correct nodes
   eventually deliver M.
2. **Uniform Agreement:** if any correct node delivers M, all
   correct nodes deliver M.
3. **Total Order:** if nodes p and q both deliver M1 and M2, they
   deliver them in the same order.
TOB is equivalent to consensus: any system that solves one can
solve the other with constant overhead.

---

### ⏱️ Understand It in 30 Seconds

**One line:** TOB ensures every node sees the same message sequence
— the building block of any replicated state machine.

> Like a national TV broadcast schedule: every household watching
> the same channel sees the same programs in the same order, even
> though each household has its own TV.

**One insight:** TOB is NOT about speed — it's about agreement.
A slow TOB that delivers messages days late still guarantees
eventual consistency. A fast non-TOB system can deliver messages
in microseconds and still diverge.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every message M delivered by any correct node is eventually
   delivered by all correct nodes (Validity + Agreement).
2. All correct nodes deliver messages in the same sequence
   (Total Order).
3. No node delivers a message more than once (No Duplication).
4. Only broadcast messages are delivered (No Creation).

**DERIVED DESIGN:**
To implement TOB you need a sequencer — something that assigns
global sequence numbers. Options: (a) centralized sequencer
(single point of failure), (b) consensus round to agree on the
next message in the sequence (Paxos/Raft), (c) commutative
operations that avoid needing a total order (CRDTs, but this
gives up TOB).

**THE TRADE-OFFS:**
**Gain:** Replicated state machines are trivially correct;
once you have TOB, any deterministic service can be replicated.
**Cost:** TOB requires at least one consensus round per message;
this adds 1-2 RTTs of latency; throughput is bounded by
consensus leader bandwidth; under network partition, TOB halts
(choosing consistency over availability per CAP).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Agreeing on an order requires communication between
nodes — you cannot get consensus for free.
**Accidental:** Leader election, log truncation, membership
changes, and snapshot management are implementation concerns,
not theoretical requirements of TOB itself.

---

### 🧪 Thought Experiment

**SETUP:** Three replicas of a bank account. Initial balance: $100.
Two clients simultaneously send "debit $60" (M1) and "credit $40"
(M2).

**WHAT HAPPENS WITHOUT TOB:**
Replica 1 processes M1 then M2: $100 - $60 + $40 = $80. OK.
Replica 2 processes M2 then M1: $100 + $40 - $60 = $80. OK.
BUT: if the debit had an "insufficient funds" check, replica 1
would allow the debit (balance was $100), replica 2 might also
allow it — but if M1 came first on R1 and M2 first on R2, the
check fires differently. Results diverge silently.

**WHAT HAPPENS WITH TOB:**
All replicas agree: M1 is sequence 1, M2 is sequence 2.
All apply M1 first: balance $40; M2 makes it $80. Consistent.
The "insufficient funds" check fires identically on all replicas.

**THE INSIGHT:** TOB makes distributed state machines as simple as
single-node state machines. The complexity is paid once in the
broadcast protocol, not repeatedly in every application.

---

### 🧠 Mental Model / Analogy

> Think of TOB as a newspaper printing press: all copies of
> today's paper are identical regardless of which city the reader
> is in. The "press" is the consensus protocol — it determines
> which articles appear and in what order. Readers (replicas)
> simply read the paper in page order.

Element mapping:
- Newspaper = the totally ordered message log
- Printing press = the consensus protocol (Raft/Paxos)
- Readers = replicas applying the log
- Article submission = client request (broadcast)
- Page number = sequence number

Where this analogy breaks down: newspapers are printed centrally;
TOB must function without a permanent single point of control,
and must tolerate the "press" (leader) crashing and being replaced.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Imagine a group chat where a special rule guarantees everyone sees
every message in exactly the same order. TOB is that guarantee
for distributed systems — every server gets every update, in the
same order, no matter what.

**Level 2 - How to use it (junior developer):**
Use a Kafka topic (single partition) or ZooKeeper znodes to get
TOB semantics in practice. Write events to the topic; all
consumers read the same sequence. Do not rely on timestamps alone
— use offsets (sequence numbers) for ordering.

**Level 3 - How it works (mid-level engineer):**
TOB is implemented via a replicated log. A leader receives a
client request, assigns it sequence N, replicates the entry to a
quorum of followers (Raft AppendEntries RPC), waits for quorum
acknowledgement, then commits. The leader broadcasts the commit;
all nodes apply sequence N. Non-leaders redirect clients to the
leader. On leader failure, Raft elects a new leader that already
has the committed prefix — ensuring no message is lost.

**Level 4 - Why it was designed this way (senior/staff):**
TOB and consensus are equivalent (Chandra-Toueg, 1996). TOB
requires agreement on a sequence; consensus requires agreement on
a single value; each reduces to the other in O(1) messages. This
equivalence is why FLP Impossibility (DST-060) applies to TOB:
in an asynchronous system with one crash fault, no deterministic
algorithm can guarantee TOB termination. Practical systems
(Raft, Paxos) escape FLP by using timeouts (partial synchrony
assumption) — they do not guarantee liveness in fully
asynchronous networks, only in those that are "eventually
synchronous."

**Expert Thinking Cues:**
- "Is this use case actually requiring TOB or can CRDTs suffice?"
- "What is my leader bandwidth ceiling — that bounds TOB throughput."
- "Am I distinguishing between delivering and committing? TOB
  guarantees delivery order, not application idempotency."

---

### ⚙️ How It Works (Mechanism)

```
Client  Leader        Follower1  Follower2
  |        |               |          |
  |--req-->|               |          |
  |        |--AppendLog N->|          |
  |        |--AppendLog N------------>|
  |        |<---ACK--------|          |
  |        |<---ACK--------------------|
  |        | (quorum met)              |
  |        |--Commit N---->|          |
  |        |--Commit N---------------->|
  |<--ok---|               |          |
  |        | all deliver N in order    |
```

**Failure: Leader crash after replication but before commit**

```
Leader crashes mid-flight:
  - Followers have entry N but it's not committed
  - New leader elected from quorum (has entry N)
  - New leader re-commits N (Raft: re-sends commit)
  - Clients that got no response retry -> idempotency required
```

---

### 💻 Code Example

```java
// BAD: broadcasting without ordering guarantee
// Each node independently publishes; order may differ
pubSubClient.publish("orders", orderEvent);
// Replica A might process order1 before order2
// Replica B might process order2 before order1

// GOOD: using Kafka single partition for TOB semantics
// Producer with explicit key -> same partition -> TOB
ProducerRecord<String, String> record =
    new ProducerRecord<>(
        "orders",  // topic
        "account-123",  // key => same partition always
        orderEvent.toJson());
producer.send(record).get(); // sync: confirms TOB sequence N

// Consumer: process in offset order (TOB guaranteed by Kafka)
ConsumerRecords<String, String> records =
    consumer.poll(Duration.ofMillis(100));
// Records are in total order for this partition
for (ConsumerRecord<String, String> r : records) {
    stateMachine.apply(r.offset(), r.value());
}
```

**How to test / verify correctness:**
```java
// Send N concurrent messages, verify all consumers see same order
List<String> node1Order = new ArrayList<>();
List<String> node2Order = new ArrayList<>();
// ... subscribe both consumers ...
// After all messages delivered:
assert node1Order.equals(node2Order) :
    "TOB violation: nodes see different orders";
```

---

### ⚖️ Comparison Table

| Property              | Best-Effort Bcast | Reliable Bcast | Causal Bcast | TOB (Atomic) |
| --------------------- | ----------------- | -------------- | ------------ | ------------ |
| All nodes get all msgs| No                | Yes            | Yes          | Yes          |
| Message order         | None              | None           | Causal only  | Same total   |
| Consensus required    | No                | No             | No           | Yes          |
| Latency               | Lowest            | Low            | Low          | Highest      |
| FLP applies           | No                | No             | No           | Yes          |
| Use case              | UDP multicast     | Log replication| Social feeds | State machine|

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "TOB means messages arrive at the same wall time" | TOB is about delivery ORDER only; the actual delivery times can differ significantly across nodes |
| "Kafka guarantees TOB across all partitions" | Kafka provides TOB only WITHIN a single partition; cross-partition ordering requires additional coordination |
| "TOB requires a leader forever" | Leader-based TOB (Raft) can tolerate leader failures; the new leader continues from the last committed sequence |
| "TOB is just reliable broadcast" | Reliable broadcast guarantees all-or-nothing delivery; TOB adds the stronger property that all nodes agree on ORDER |
| "Any eventually consistent system uses TOB" | Eventual consistency systems (DynamoDB default) deliberately avoid TOB to gain availability; they trade order for uptime |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Leader bottleneck at scale**

**Symptom:** Write latency climbs linearly with write throughput;
leader CPU/network near saturation.
**Root Cause:** TOB forces all writes through the leader; the
leader's network bandwidth is the global write ceiling.
**Diagnostic:**
```bash
# Kafka: check leader partition load
kafka-topics.sh --describe --topic orders \
  | grep Leader
# Check broker network throughput
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
  --topic-list orders | python -m json.tool
```
**Fix:** Partition by key so multiple leaders handle disjoint key
spaces; use multi-Paxos pipeline to batch commits.
**Prevention:** Capacity plan for peak write throughput including
replication factor overhead (typically 3x raw write).

---

**Failure Mode 2: Split-brain under network partition**

**Symptom:** Two nodes both believe they are leader and deliver
conflicting sequences.
**Root Cause:** Network partition isolates a stale leader that
has not yet stepped down; new leader elected; both accept writes
for a period.
**Diagnostic:**
```bash
# ZooKeeper: check leader status
echo stat | nc zk-host 2181 | grep Mode
# Should be "leader" on exactly one node
```
**Fix:** Raft's term mechanism prevents this: a node with a
lower term rejects all operations from old leader. Ensure quorum
size > N/2.
**Prevention:** Configure appropriate `electionTimeout` (> network
RTT * 3); use fencing tokens (DST-030) for external resource
access.

---

**Failure Mode 3: Stale reads from non-leader replicas**

**Symptom:** Clients reading from a follower see data behind
committed sequence.
**Root Cause:** Follower has not yet received the latest committed
entry from leader; reads return stale state.
**Diagnostic:**
```bash
# Kafka consumer lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-group | grep LAG
```
**Fix:** Route all reads through the leader (linearizable reads)
OR use read-your-writes tokens: client tracks the last committed
sequence and waits for follower to catch up before reading.
**Prevention:** Design read paths to tolerate bounded staleness;
document the `maxLag` SLA; alert when consumer lag > threshold.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-019 - Total Order / Partial Order (the ordering theory)
- DST-015 - Lamport Clock (sequence number foundation)
- DST-022 - Leader Election (TOB requires leader selection)

**Builds On This (learn these next):**
- DST-023 - Raft (most widely implemented TOB algorithm)
- DST-024 - Paxos (theoretical TOB foundation)
- DST-027 - State Machine Replication (what TOB enables)

**Alternatives / Comparisons:**
- CRDTs (DST-061): avoid TOB by using commutative operations
- Causal Broadcast: weaker than TOB, sufficient for some use cases
- Reliable Broadcast: no ordering, but all-or-nothing delivery

---

### 📌 Quick Reference Card

```
+-------------------------------------------------+
| WHAT IT IS    | Protocol: all nodes same msg order|
| PROBLEM SOLVES| State divergence across replicas  |
| KEY INSIGHT   | TOB = consensus; solve one = both  |
| USE WHEN      | Replicated state machines,         |
|               | financial ledgers, config stores   |
| AVOID WHEN    | High availability > consistency;   |
|               | operations are commutative (CRDT)  |
| TRADE-OFF     | Strong consistency vs availability |
|               | (halts under partition: CAP-C)     |
| ONE-LINER     | Every node, every message, one order|
| NEXT EXPLORE  | DST-023 Raft (TOB implementation)  |
+-------------------------------------------------+
```

**If you remember only 3 things:**
1. TOB = every correct node delivers every message in the SAME
   order — the replicated state machine foundation.
2. TOB is equivalent to consensus: Raft and Paxos ARE TOB
   implementations.
3. TOB halts under partition (CAP-C); use CRDTs or eventual
   consistency if availability must be preserved.

**Interview one-liner:** "Total Order Broadcast guarantees all
replicas process the same message sequence, making replicated
state machines trivially consistent — it's the primitive that
Raft and Paxos implement under the hood."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When you need multiple
actors to reach identical state without central coordination,
find the primitive that makes their inputs equivalent — ordering
events into a shared sequence is one universal way to do this.

**Where else this pattern appears:**
- **Database replication:** Primary-replica MySQL uses binlog
  (a TOB sequence); replicas apply identical operations in order.
- **Distributed ledgers:** Blockchain ordering is TOB where
  "leaders" rotate (miners/validators) each block round.
- **Kubernetes controllers:** etcd (ZooKeeper-style) provides
  TOB for all cluster state changes; controllers watch the same
  ordered event stream.

---

### 💡 The Surprising Truth

Total Order Broadcast and consensus are provably equivalent —
not just similar. If you have an algorithm that solves consensus
(agreeing on one value), you can build TOB from it in O(1)
rounds per message. And if you have TOB, you can solve consensus
in one broadcast. This means every database that claims
"strong consistency" is running some form of consensus internally,
even if it never uses the word. When engineers debate "do we need
Paxos?" they are actually debating "do we need total ordering?"
— which is the same question.

---

### 🧠 Think About This Before We Continue

**Question A (System Interaction):** Kafka provides TOB within
a partition but NOT across partitions. If a banking application
requires TOB across all account events, what architectural options
exist to achieve this while maintaining high throughput?
*Hint:* Consider what "partition key" guarantees and what
additional coordination would be needed for cross-partition
ordering.

**Question B (Scale):** At 1 million messages per second, a
single TOB leader becomes a bottleneck. How do systems like
CockroachDB (which claims both strong consistency and high
throughput) deal with this?
*Hint:* Research "range-based sharding" and per-range Raft groups
— each range has its own TOB instance.

**Question C (Design Trade-off):** Your team proposes using TOB
for a social media "like" counter. What is wrong with this
approach and what alternative ordering primitive would be more
appropriate?
*Hint:* Consider whether "like" operations are order-sensitive
and which distributed data structure handles commutative,
associative operations without needing TOB.
'@

$f020 = Join-Path $base "DST-020 - Total Order Broadcast.md"
[System.IO.File]::WriteAllText(
    (Resolve-Path ".").Path + "\" + $f020,
    $dst020,
    [System.Text.UTF8Encoding]::new($false))
Write-Host "Written DST-020: $((Get-Content $f020 -Encoding UTF8).Count) lines"

# ─── DST-031 - Network Partition ──────────────────────────────────────────
$dst031 = @'
---
id: DST-031
title: Network Partition
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-006, DST-004, DST-030
used_by: DST-032, DST-029, DST-006
related: DST-006, DST-029, DST-030
tags:
  - distributed
  - networking
  - reliability
  - foundational
  - intermediate
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /distributed-systems/network-partition/
---

# DST-031 - Network Partition

⚡ **TL;DR** — A network partition is when a network failure splits
nodes into groups that cannot communicate, forcing every distributed
system to choose between consistency and availability.

| Relationship    | IDs                                     |         |
| --------------- | --------------------------------------- | ------- |
| **Depends on:** | DST-006, DST-004, DST-030               |         |
| **Used by:**    | DST-032, DST-029, DST-006               |         |
| **Related:**    | DST-006, DST-029, DST-030               |         |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers assume the network is always up. They design systems
without considering what happens when nodes cannot reach each
other. On the day a switch fails, both sides of the partition
continue accepting writes independently. When connectivity
restores, data conflicts must be resolved — often by human
intervention or data loss.

**THE BREAKING POINT:**
In a 2009 outage, a routing misconfiguration split an e-commerce
database cluster. Both halves continued accepting orders. When
the partition healed, the inventory numbers were wrong on both
sides. The system had no partition-handling logic because the
engineers assumed the network was reliable.

**THE INVENTION MOMENT:**
Brewer's CAP Theorem (2000) formalized what practitioners already
knew: network partitions will happen in any real system; the only
choice is what to sacrifice during one. This crystallized
partition-handling from "edge case" to "core design concern."

**EVOLUTION:**
Modern cloud providers experience partitions regularly at the
availability-zone and region level. AWS, GCP, and Azure design
their services explicitly around partition tolerance. Chaos
engineering tools (Chaos Monkey, Gremlin) deliberately induce
partitions to verify that systems behave correctly.

---

### 📘 Textbook Definition

A **network partition** is a failure condition in which a set of
nodes in a distributed system splits into two or more disjoint
groups, where nodes within each group can communicate with each
other but nodes across groups cannot. The failure is transient
(links eventually recover) but its duration is unpredictable.
Partitions can result from: physical cable failures, router/switch
crashes, misconfigured firewall rules, asymmetric routing, or
cloud provider infrastructure events.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A network split that forces your system to choose —
stop accepting requests, or risk inconsistency.

> Like a ship with two radio rooms that lose contact mid-voyage.
> Each room can talk to the crew on its side. If both rooms keep
> issuing orders independently, the ship's crew might row in
> opposite directions.

**One insight:** Partitions are not optional in real networks.
Every distributed system must declare upfront: "during a
partition, I will prefer consistency (stop)" or "I will prefer
availability (continue, accept divergence)."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A network partition is undetectable from a timeout alone:
   a slow node and an unreachable node look identical.
2. During a partition, each side has a consistent LOCAL view but
   an INCOMPLETE global view.
3. A system cannot distinguish "the other side is slow" from
   "the other side is dead" without a global oracle — which
   itself would require network connectivity.

**DERIVED DESIGN:**
Design choices during a partition:
- **CP (Consistency + Partition Tolerance):** reject requests
  unless a quorum of nodes is reachable (ZooKeeper, etcd, HBase).
- **AP (Availability + Partition Tolerance):** continue serving
  requests from each partition independently; reconcile after
  healing (Cassandra, DynamoDB, CouchDB).
- **CA (Consistency + Availability):** impossible under partition
  (this is the point of CAP Theorem).

**THE TRADE-OFFS:**
**Gain (AP):** system stays up during partition; no user-facing
errors; revenue continues.
**Cost (AP):** data may diverge; conflict resolution required on
healing; risk of "split brain" (DST-029).
**Gain (CP):** no data conflicts; consistency invariants hold.
**Cost (CP):** service is unavailable during partition; timeouts
return errors to users.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** you MUST handle partitions — the network will
eventually fail.
**Accidental:** choosing the RIGHT partition-handling strategy
for your business requirements (e.g. a payment system needs CP;
a social feed can be AP).

---

### 🧪 Thought Experiment

**SETUP:** A 3-node database cluster with a quorum-based write
policy (2 of 3 nodes must acknowledge). A network split isolates
Node 3 from Nodes 1 and 2.

**WHAT HAPPENS WITHOUT PARTITION HANDLING:**
Node 3, still believing it is the primary, continues accepting
writes. Nodes 1 and 2 also continue accepting writes via their
local majority quorum. When the partition heals, both sides have
diverging committed data. There is no correct merge strategy —
data loss is unavoidable.

**WHAT HAPPENS WITH PARTITION HANDLING (CP):**
Node 3 detects it cannot reach a quorum. It stops accepting
writes and returns errors to clients. Nodes 1+2 form a quorum
and continue. When the partition heals, Node 3 fetches the diff
and rejoins. No data was lost or duplicated.

**THE INSIGHT:** The worst partition outcome is not "service is
down" — it is "service appears up but silently corrupts data."
Explicit partition handling trades visible errors for hidden
corruption.

---

### 🧠 Mental Model / Analogy

> Think of a partition as a snowstorm that cuts off a remote
> village. The village (isolated node) still has its own town
> hall and can make local decisions. The capital (rest of cluster)
> also continues governing. When roads reopen, both sides have
> passed laws — some may conflict.

Element mapping:
- Village = isolated partition
- Capital = majority partition
- Laws = writes/commits
- Road reopening = partition healing
- Conflicting laws = data divergence requiring reconciliation

Where this analogy breaks down: a village knows it is isolated
(no roads visible). A network node cannot always tell if it is
isolated or if the others are simply slow — it must use timeouts
and quorums as a proxy for reachability.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Imagine your team splits into two rooms and the intercom breaks.
Each room keeps working, makes decisions, and moves forward.
When you reconnect, some decisions contradict each other. That
is a network partition — two parts of a system working without
knowing what the other is doing.

**Level 2 - How to use it (junior developer):**
Design your service with explicit partition handling:
- Use circuit breakers (DST-042) to fail fast when peers
  are unreachable.
- Use idempotent operations (DST-045) so retries on healing
  are safe.
- Decide CP vs AP upfront and encode it in your SLA/README.

**Level 3 - How it works (mid-level engineer):**
Partitions are detected via heartbeat (DST-041) timeouts. When a
node stops receiving heartbeats from peers, it suspects partition.
It checks quorum: can it reach a majority? If yes, it may be
safe to continue (minority is isolated). If no (it IS the
minority), it must stop or accept that it will diverge. Fencing
tokens (DST-030) prevent the isolated minority from writing to
shared storage even if it incorrectly believes it is the leader.

**Level 4 - Why it was designed this way (senior/staff):**
The detection/handling asymmetry is fundamental. A node cannot
distinguish "slow peer" from "partitioned peer" — this is the
core challenge Lamport identified: messages take unbounded time in
an asynchronous system. Practical systems use timeouts (partial
synchrony assumption) and accept that a live node may be treated
as failed. This creates a safety/liveness tension: tighten the
timeout and you risk false partition detection (reducing
availability); loosen it and real partitions go undetected longer
(extending inconsistency windows).

**Expert Thinking Cues:**
- "What is the blast radius if we get a false positive partition
  detection?"
- "Do our fencing tokens cover ALL paths to shared storage
  during a partition?"
- "Is our partition healing merge strategy documented and tested?"

---

### ⚙️ How It Works (Mechanism)

```
Normal:            |  During Partition:
                   |
Node1 -- Node2     |  Node1 -- Node2     Node3
   \    /          |     |         (isolated)
   Node3           |     |
                   |  Node1+2: quorum (2/3) - continue
                   |  Node3: no quorum - reject writes
```

**Healing sequence:**
```
1. Partition heals (link restored)
2. Isolated node detects connectivity
3. Isolated node sends sync request to majority
4. Majority sends diff since partition start
5. Isolated node applies diff, increments epoch
6. Fencing token updated; isolated node rejoins
```

**Asymmetric partition (hardest case):**
```
Node1 -> Node2 (OK)   Node2 -> Node1 (BROKEN)
```
Node1 thinks Node2 is down; Node2 is fine but cannot reach
Node1. Both may believe they are the "surviving" side.
Solution: require ACK from receiver; treat asymmetric link as
full partition.

---

### 💻 Code Example

```java
// BAD: no partition handling — writes both sides silently
@Transactional
public void transferFunds(String from, String to, BigDecimal amt) {
    // If we are the partitioned minority:
    // This write commits locally but diverges from majority
    accountRepo.debit(from, amt);
    accountRepo.credit(to, amt);
}

// GOOD: quorum check before critical write
public void transferFunds(String from, String to, BigDecimal amt)
    throws PartitionException {
    // Verify we can reach a quorum before mutating state
    if (!clusterHealth.hasQuorum()) {
        throw new PartitionException(
            "Cannot reach majority; refusing write to " +
            "prevent split-brain divergence");
    }
    accountRepo.debit(from, amt);
    accountRepo.credit(to, amt);
}

// Quorum check implementation
public class ClusterHealth {
    private final List<String> peerUrls;
    private final int quorumSize;

    public boolean hasQuorum() {
        long reachable = peerUrls.stream()
            .filter(this::isReachable)
            .count() + 1; // +1 for self
        return reachable >= quorumSize;
    }

    private boolean isReachable(String url) {
        try {
            HttpResponse<String> resp = httpClient.send(
                HttpRequest.newBuilder()
                    .uri(URI.create(url + "/health"))
                    .timeout(Duration.ofMillis(500))
                    .build(),
                HttpResponse.BodyHandlers.ofString());
            return resp.statusCode() == 200;
        } catch (Exception e) {
            return false;
        }
    }
}
```

**How to test / verify correctness:**
```bash
# Use tc (Linux traffic control) to simulate partition
# Block traffic between node1 and node3
sudo tc qdisc add dev eth0 root netem loss 100%
# Verify node1 rejects writes when quorum lost
curl -X POST http://node1/transfer -d '{"from":"A","to":"B"}'
# Expected: 503 PartitionException
# Heal partition
sudo tc qdisc del dev eth0 root
# Verify node1 rejoins and data is consistent
```

---

### ⚖️ Comparison Table

| Scenario           | CP System (etcd/ZK) | AP System (Cassandra) |
| ------------------ | ------------------- | --------------------- |
| During partition   | Minority side: 503  | All nodes: 200 (write)|
| After healing      | Auto-rejoin, no loss| Conflict resolution   |
| Data consistency   | Always consistent   | Eventually consistent |
| User experience    | Visible errors      | Invisible divergence  |
| Right for          | Config, finance, locks | Feeds, caches, counters|
| Recovery effort    | Automatic (quorum)  | Application-level merge|

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Partitions only happen in WANs" | Partitions happen in LANs too — a bad NIC, a misconfigured switch, or a noisy neighbor can isolate a single rack in a datacenter |
| "A 99.9% network gives you no partitions" | 99.9% uptime = ~8.7 hours down/year; a single datacenter switch failure can partition hundreds of nodes simultaneously |
| "Detecting a partition is straightforward" | You CANNOT distinguish a partitioned peer from a slow peer without a timeout; every partition detector has a false-positive rate |
| "AP systems lose data during partitions" | AP systems do not lose data — they accept divergent writes on both sides and merge later. Loss depends on the merge strategy |
| "CP means always consistent" | CP means consistent during a partition; before and after, consistency depends on the application's use of the CP system |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Silent split-brain under AP**

**Symptom:** After partition heals, inventory counts or account
balances are wrong; no errors were logged during the partition.
**Root Cause:** Both sides of the partition accepted writes to the
same key; last-write-wins (LWW) discarded one side's updates.
**Diagnostic:**
```bash
# Cassandra: check for repair gaps
nodetool status  # look for DN (Down/Normal) nodes
nodetool repair --full keyspace table
# Compare row counts across DCs after repair
cqlsh -e "SELECT COUNT(*) FROM keyspace.table" node1
cqlsh -e "SELECT COUNT(*) FROM keyspace.table" node3
```
**Fix:** Use vector-clock versioning with application-level
conflict resolution; avoid LWW for non-idempotent operations.
**Prevention:** Design writes to be idempotent and commutative
wherever possible; use CRDTs for counters and sets.

---

**Failure Mode 2: Phantom leader (fencing failure)**

**Symptom:** Two nodes believe they are primary; both write to
shared storage (database, S3, NFS); data is overwritten.
**Root Cause:** Leader election elected a new leader but the old
leader was not properly fenced; it continued writing.
**Diagnostic:**
```bash
# Check for multiple primary indicators
grep "became primary" /var/log/db/*.log | grep -v "stepping down"
# Should see exactly one "became primary" without a matching
# "stepping down" before it
```
**Fix:** Implement fencing tokens (DST-030): each new leader
gets a monotonically increasing token; shared storage rejects
writes with stale tokens.
**Prevention:** Never rely solely on heartbeat absence to detect
old leaders; always use a fencing mechanism with shared storage.

---

**Failure Mode 3: Partition induced by misconfigured firewall**

**Symptom:** Intermittent cluster splits with no hardware failure;
pattern correlates with deployment of new firewall rules.
**Root Cause:** A firewall rule blocks the internal gossip/heartbeat
port between specific node IP ranges; nodes timeout each other.
**Diagnostic:**
```bash
# Test inter-node connectivity on cluster port
nc -zv node3-ip 2380   # etcd peer port
# Or use nmap for a batch check
nmap -p 2380,2379 10.0.0.0/24
```
**Fix:** Add explicit ALLOW rules for cluster communication ports
between all node IPs; use security groups (AWS) or NSGs (Azure)
scoped to cluster CIDR.
**Prevention:** Include inter-node connectivity tests in your
deployment runbook; automate validation with a cluster health
check script post-deploy.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-006 - CAP Theorem (formal framework for partition trade-offs)
- DST-004 - Fallacies of Distributed Computing (network is reliable)
- DST-041 - Heartbeat (partition detection mechanism)

**Builds On This (learn these next):**
- DST-029 - Split Brain (what happens when partition goes unhandled)
- DST-030 - Fencing / Epoch (how to safely handle partition healing)
- DST-032 - Failure Modes (broader taxonomy of distributed failures)

**Alternatives / Comparisons:**
- Node failure: node crashes entirely; partition means node lives
  but link fails — a harder problem to detect
- High latency: often indistinguishable from partition; timeout
  tuning is shared concern

---

### 📌 Quick Reference Card

```
+-------------------------------------------------+
| WHAT IT IS    | Network split: nodes can't talk  |
| PROBLEM SOLVES| Forces explicit consistency choice|
| KEY INSIGHT   | Slow peer = partitioned peer;     |
|               | indistinguishable without timeout  |
| USE WHEN      | Designing any distributed system  |
|               | (always must plan for it)         |
| AVOID WHEN    | N/A - partitions happen regardless|
| TRADE-OFF     | CP: safe but unavailable           |
|               | AP: available but may diverge     |
| ONE-LINER     | Network fails; you pick C or A    |
| NEXT EXPLORE  | DST-029 Split Brain, DST-006 CAP  |
+-------------------------------------------------+
```

**If you remember only 3 things:**
1. Partitions WILL happen; design for them, not around them.
2. You cannot tell a slow node from a partitioned one — timeouts
   are your only signal, and they create false positives.
3. CP = errors during partition; AP = divergence during partition;
   choose based on your business requirement.

**Interview one-liner:** "A network partition splits the cluster
into groups that cannot communicate; the system must then choose
between rejecting requests (CP) or accepting divergent writes (AP),
which is exactly what CAP Theorem formalizes."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When two parties lose
communication, each must have a pre-agreed protocol for what to
do independently. Systems without a partition protocol fail in the
worst possible way — silently.

**Where else this pattern appears:**
- **Multi-datacenter deployments:** an inter-DC link failure
  creates a classic partition; every DC must have a pre-agreed
  behavior (accept reads only, fail writes, etc.).
- **Microservice API gateways:** a partition between gateway and
  upstream service requires fallback logic (cached response,
  circuit breaker) pre-coded, not improvised.
- **IoT edge devices:** a sensor loses connectivity to cloud;
  it must buffer locally and merge on reconnect — same partition
  healing logic as a database cluster.

---

### 💡 The Surprising Truth

Network partitions in real clouds are far more common than most
engineers expect. Amazon's internal post-mortems have documented
partitions caused by: DNS misconfiguration, BGP route flap,
physical fiber cuts, NIC driver bugs, and even software bugs in
the hypervisor network stack. The mean time between partition
events in a large AWS region is measured in DAYS, not years.
This is why AWS designs every major service (DynamoDB, S3, SQS)
as AP with explicit conflict resolution — not because they cannot
build CP systems, but because the partition rate makes CP systems
too frequently unavailable for most customer workloads.

---

### 🧠 Think About This Before We Continue

**Question A (System Interaction):** A 5-node cluster uses
majority quorum (3 of 5). A partition splits it 3 + 2. Both
sides attempt to elect a leader. What happens, and why is
quorum size > N/2 critical to this outcome?
*Hint:* Trace through the election protocol on each side and
consider what "quorum" means for the minority partition.

**Question B (Scale):** At 1,000 nodes, the probability of at
least one node being unreachable approaches certainty at any given
moment. How do systems like Cassandra remain available despite
constant "partial partitions"?
*Hint:* Research how replication factor and consistency level
(ONE, QUORUM, ALL) interact to tolerate partial node failures.

**Question C (Design Trade-off):** A fintech startup says "we
will handle partitions by queueing writes on the client side and
replaying them after healing." What are the hidden risks of this
approach that are not apparent at first glance?
*Hint:* Consider ordering, idempotency, and the case where the
"healing" never comes within the client's session lifetime.
'@

$f031 = Join-Path $base "DST-031 - Network Partition.md"
[System.IO.File]::WriteAllText(
    (Resolve-Path ".").Path + "\" + $f031,
    $dst031,
    [System.Text.UTF8Encoding]::new($false))
Write-Host "Written DST-031: $((Get-Content $f031 -Encoding UTF8).Count) lines"

# ─── DST-034 - XA Transactions ────────────────────────────────────────────
$dst034 = @'
---
id: DST-034
title: XA Transactions
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-033, DST-013, DST-032
used_by: DST-035, DST-037
related: DST-033, DST-035, DST-049
tags:
  - distributed
  - transactions
  - database
  - deep-dive
  - advanced
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 34
permalink: /distributed-systems/xa-transactions/
---

# DST-034 - XA Transactions

⚡ **TL;DR** — XA is the industry-standard interface for Two-Phase
Commit across heterogeneous resource managers (databases, queues,
message brokers), allowing atomic commits spanning multiple systems.

| Relationship    | IDs                                     |         |
| --------------- | --------------------------------------- | ------- |
| **Depends on:** | DST-033, DST-013, DST-032               |         |
| **Used by:**    | DST-035, DST-037                        |         |
| **Related:**    | DST-033, DST-035, DST-049               |         |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A bank transfer spans a PostgreSQL database (debit) and a message
queue (send notification). Without coordination, the debit commits
but the broker crashes before the message is enqueued. Or the
message is sent but the DB rollback leaves the account credited.
Each system has ACID locally, but the cross-system operation is
not atomic.

**THE BREAKING POINT:**
1990s enterprise Java applications connected to databases,
message brokers, and ERP systems simultaneously. Every vendor
had their own proprietary transaction API. Each application had
to hand-code retry and rollback logic for every combination of
resource types — a combinatorial maintenance nightmare.

**THE INVENTION MOMENT:**
The X/Open Consortium (1991) published the XA specification:
a common C interface (`xa_start`, `xa_end`, `xa_prepare`,
`xa_commit`, `xa_rollback`) that any transaction-capable resource
manager could implement. The Transaction Manager (TM) could then
coordinate 2PC across any combination of XA-compliant resources.

**EVOLUTION:**
XA was standardized into Java via JTA (Java Transaction API,
JSR-907). Frameworks like Atomikos, Bitronix, and Narayana
implement the Transaction Manager role. Spring's `@Transactional`
annotation can delegate to a JTA TM for cross-resource atomicity.
Modern microservices architectures largely replace XA with the
Saga pattern (DST-049) due to XA's performance and coupling costs.

---

### 📘 Textbook Definition

**XA** (eXtended Architecture) is the X/Open distributed
transaction processing (DTP) specification. It defines the
interface between a Transaction Manager (TM) and Resource Managers
(RMs — databases, message brokers, JMS providers). XA implements
Two-Phase Commit (DST-033): Phase 1 (`xa_prepare`) asks all RMs
to log and lock their changes; Phase 2 (`xa_commit` or
`xa_rollback`) finalizes atomically. The TM is the coordinator;
the TM log (transaction log) is the source of truth for in-doubt
transactions on crash recovery.

---

### ⏱️ Understand It in 30 Seconds

**One line:** XA is the standard plug for connecting any database
or broker into a coordinated two-phase commit.

> Like a universal power adapter: regardless of which "socket"
> (database vendor) you plug into, the XA standard ensures the
> Transaction Manager can speak the same protocol to all of them.

**One insight:** XA solves the VENDOR HETEROGENEITY problem of
distributed transactions — not the fundamental performance or
availability limits of 2PC. Choosing XA still means choosing 2PC
trade-offs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A Transaction ID (XID) globally identifies a distributed
   transaction across all participating resource managers.
2. `xa_prepare` is a promise: the RM has written its changes to
   durable storage and will not lose them if asked to commit.
3. Once the TM writes "commit" to its log, it will retry forever
   until all RMs acknowledge — the atomic commit point.
4. The TM log is the single source of truth; losing it means
   in-doubt transactions must be resolved manually.

**DERIVED DESIGN:**
Components: Application (starts/ends transaction), TM (coordinates
2PC, owns the log), RM (database or broker, implements xa_*
interface). The TM assigns XIDs; passes them to each RM via
`xa_start`. After application work: TM calls `xa_prepare` on each
RM; on all-OK calls `xa_commit` on each; on any FAIL calls
`xa_rollback` on all.

**THE TRADE-OFFS:**
**Gain:** True atomicity across heterogeneous resources with no
application-level retry logic; compatible with standard JDBC/JTA
frameworks; crash recovery is handled by TM log replay.
**Cost:** Each `xa_prepare` holds locks until `xa_commit` — latency
is 2+ RTTs per transaction; TM is a new SPOF; all RMs must be
reachable at commit time (partition = blocked transactions);
debugging in-doubt transactions requires vendor-specific tools.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Coordinating atomicity across two independent
systems requires at least two communication rounds — you cannot
avoid this.
**Accidental:** The `xa_*` C interface, JTA boilerplate,
JNDI datasource configuration, and TM-specific recovery tools
are accidental complexity added by the specification's age.

---

### 🧪 Thought Experiment

**SETUP:** A flight booking system writes to a reservation DB and
charges a payment processor. Both are XA-capable.

**WHAT HAPPENS WITHOUT XA:**
Two separate JDBC connections, two `commit()` calls. Reservation
commits; payment processor crashes before commit. Booking confirmed
but payment not charged. Or payment charged but DB crashes before
reservation saved. Customer has a receipt but no seat.

**WHAT HAPPENS WITH XA:**
TM starts XA transaction, XID shared with DB and payment
processor. Application performs DB insert + payment charge. TM
calls `xa_prepare` on both: DB locks the row, payment processor
holds the auth token. TM writes "commit" to its log. TM calls
`xa_commit` on both. If payment processor crashes AFTER prepare
but BEFORE commit, TM retries on recovery — the payment processor
will find the prepared transaction in its own log and commit it.
Either both commit or neither does.

**THE INSIGHT:** The power of XA is the prepare phase creating
a durable promise. Once all RMs have prepared, the transaction
WILL commit — even across crashes — because the TM retries.

---

### 🧠 Mental Model / Analogy

> XA is like a wedding officiant (Transaction Manager) overseeing
> two parties (Resource Managers). Phase 1: "Do you, Database, take
> this transaction?" — both say "I do" and sign a pre-nuptial
> contract (xa_prepare). Phase 2: officiant declares the marriage
> complete (xa_commit). If one party faints after signing (crash
> after prepare), the officiant can still complete the ceremony
> when they recover.

Element mapping:
- Wedding officiant = Transaction Manager (TM)
- Parties = Resource Managers (database, broker)
- "I do" + pre-nuptial signing = xa_prepare (durable promise)
- Marriage declaration = xa_commit
- Marriage register = TM log
- Fainting = crash after prepare

Where this analogy breaks down: a wedding can have one party
absent and still proceed legally in some contexts; XA requires
ALL parties to prepare before ANY commit.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
XA is a way to make sure that when your application updates two
different systems at once (a database AND a message queue, for
example), either BOTH updates succeed or NEITHER does — even if
one of the systems crashes in the middle.

**Level 2 - How to use it (junior developer):**
In Spring Boot with JTA: add an XA-capable connection pool
(e.g. Atomikos), configure JTA transaction manager, use
`@Transactional` as normal. Spring handles xa_start/prepare/
commit transparently. Key config:
```yaml
spring.jta.atomikos.datasource.xa-data-source-class-name:
  com.mysql.cj.jdbc.MysqlXADataSource
```

**Level 3 - How it works (mid-level engineer):**
When `@Transactional` method starts: JTA TM calls `xa_start(XID)`
on each enlisted RM (DB connection pool, JMS connection). When
method completes: TM calls `xa_end(XID)` then `xa_prepare(XID)`
on each RM sequentially. On all-OK: TM writes commit record to
its transaction log (fsync), then calls `xa_commit(XID)` on each.
If TM crashes after log write, on restart it reads the log and
retries `xa_commit` on all in-doubt RMs. If any RM fails to
prepare, TM calls `xa_rollback(XID)` on all prepared RMs.

**Level 4 - Why it was designed this way (senior/staff):**
The critical design choice is the TM log (write-ahead log for
commit records). Without it, a TM crash after prepare but before
commit leaves RMs in-doubt forever — they hold locks and cannot
unilaterally decide. The TM log solves this: it is the
authoritative record of the commit decision. However, this makes
the TM log a SPOF: if it is corrupted or lost, in-doubt
transactions become zombies requiring DBA intervention. Modern
XA TMs use replicated logs (e.g. Narayana with shared NFS or
database-backed logs) to mitigate this.

**Expert Thinking Cues:**
- "What is my TM's SPOF story — is its log replicated?"
- "How long will locks be held if one RM is slow to prepare?"
- "Have I tested TM crash-recovery in my staging environment?"

---

### ⚙️ How It Works (Mechanism)

```
Application         TM (Coordinator)     DB (RM1)   Broker (RM2)
    |                    |                  |             |
    |--beginTx()-------->|                  |             |
    |                    |--xa_start(XID)-->|             |
    |                    |--xa_start(XID)-------------->  |
    |--dbInsert()------->|                  |             |
    |--brokerSend()----->|                  |             |
    |--commit()--------->|                  |             |
    |                    |--xa_end(XID)---->|             |
    |                    |--xa_prepare(XID)->|             |
    |                    |<--PREPARED--------|             |
    |                    |--xa_prepare(XID)-------------> |
    |                    |<--PREPARED--------------------- |
    |                    |--[WRITE COMMIT LOG]--fsync      |
    |                    |--xa_commit(XID)->|             |
    |                    |--xa_commit(XID)-------------->  |
    |<--success----------|                  |             |
```

**Crash recovery (TM crashes after COMMIT LOG write):**
```
TM restarts:
  1. Read transaction log -> find committed XID
  2. Call xa_commit(XID) on each RM
  3. RMs either commit (if prepared) or respond XAER_NOTA
     (already committed -> idempotent)
  4. Mark transaction complete in log
```

---

### 💻 Code Example

```java
// BAD: two separate commits -- not atomic
@Service
public class OrderService {
    public void placeOrder(Order order) {
        // If broker crashes between these two commits:
        // order saved but notification never sent
        orderRepo.save(order);          // commit 1
        notificationBroker.send(order); // commit 2
    }
}

// GOOD: XA transaction across DB and JMS broker
@Service
public class OrderService {
    // JtaTransactionManager + XA DataSource + XA JMS configured
    // in application context (Atomikos or Narayana)

    @Transactional // Uses JTA -- coordinates XA across both RMs
    public void placeOrder(Order order) {
        // Both operations in same XA transaction (XID)
        orderRepo.save(order);
        notificationQueue.send(
            session.createObjectMessage(order));
        // On method return: TM xa_prepare both, then xa_commit
        // If anything fails: TM xa_rollback both
    }
}
```

**Spring Boot JTA configuration (Atomikos):**
```yaml
spring:
  jta:
    atomikos:
      datasource:
        unique-resource-name: orderDb
        xa-data-source-class-name:
          org.postgresql.xa.PGXADataSource
        xa-properties:
          serverName: localhost
          portNumber: 5432
          databaseName: orders
      connectionfactory:
        unique-resource-name: notificationQueue
        xa-connection-factory-class-name:
          org.apache.activemq.ActiveMQXAConnectionFactory
```

**How to test / verify correctness:**
```java
@Test
public void testXaRollbackOnBrokerFailure() {
    // Arrange: broker configured to throw after xa_prepare
    brokerRM.setFailOnPrepare(true);

    // Act: attempt order placement
    assertThrows(TransactionSystemException.class,
        () -> orderService.placeOrder(testOrder));

    // Assert: DB should be rolled back
    assertFalse(orderRepo.existsById(testOrder.getId()));
}
```

---

### ⚖️ Comparison Table

| Property             | Local Transaction | XA / JTA       | Saga (DST-049)   |
| -------------------- | ----------------- | --------------- | ---------------- |
| Atomicity scope      | Single RM         | Multiple RMs    | Multiple services|
| Coupling             | None              | Tight (2PC)     | Loose (async)    |
| Latency overhead     | None              | 2+ RTTs         | Multiple RTTs    |
| Lock duration        | Short             | Longer (prepare)| None             |
| Failure handling     | Automatic rollback| TM log recovery | Compensating txns|
| Partition tolerance  | High              | Low (blocks)    | High             |
| Complexity           | Low               | Medium          | High (app logic) |
| Right for            | Single DB         | Same-DC RMs     | Microservices    |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "XA gives you distributed ACID for free" | XA gives atomicity across RMs; isolation is per-RM (global snapshot isolation is not provided); durability depends on TM log integrity |
| "Spring @Transactional always uses XA" | By default, Spring uses the local DataSourceTransactionManager (one DB only); XA requires explicit JTA configuration with an XA-capable TM |
| "XA transactions can span microservices" | XA requires the TM to have direct access to all RM connections; it cannot cross process or network boundaries to external services |
| "XA is obsolete" | XA is still widely used in enterprise Java (banking, telecom, ERP) wherever heterogeneous resources need atomic coordination; it is less common in cloud-native microservices |
| "A crashed RM during xa_prepare causes data loss" | A crash during PREPARE causes a rollback (no data committed yet); data loss risk is only if the TM log is lost after a commit decision |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: In-doubt transactions locking database rows**

**Symptom:** Application queries hang; DB shows long-running
transactions holding row locks; TM log shows "prepared" entries
that never complete.
**Root Cause:** TM crashed after xa_prepare but before xa_commit;
on restart, TM log was not replayed; RMs still hold prepared state.
**Diagnostic:**
```sql
-- PostgreSQL: find prepared XA transactions
SELECT gid, prepared, owner, database
FROM pg_prepared_xacts;

-- MySQL: find in-doubt XA transactions
XA RECOVER;
```
**Fix:** Identify the XID from TM logs; manually commit or
rollback:
```sql
-- PostgreSQL
COMMIT PREPARED 'xid-value';
-- or
ROLLBACK PREPARED 'xid-value';
```
**Prevention:** Configure TM log replication; set `xa_prepare`
timeout so RMs rollback automatically after a bounded wait.

---

**Failure Mode 2: Performance degradation under XA**

**Symptom:** Transaction throughput drops 3-5x after enabling XA;
DB CPU high; many blocked connections.
**Root Cause:** XA doubles the number of roundtrips (prepare +
commit phases) and extends lock hold time across the network RTT
between TM and RMs.
**Diagnostic:**
```bash
# Check transaction rate vs latency
# Prometheus JVM metrics (Atomikos exports these):
atomikos_transaction_duration_seconds_bucket
# Or DB level
SHOW STATUS LIKE 'Innodb_row_lock_waits'; # MySQL
```
**Fix:** Batch operations to reduce XA transaction count; consider
Saga pattern for long-running or high-throughput flows; use XA
only for short, critical transactions (payments, inventory
decrements).
**Prevention:** Benchmark XA vs local transactions in your
specific environment before committing to the architecture.

---

**Failure Mode 3: TM as single point of failure**

**Symptom:** All transactions fail when TM node goes down; no
failover occurs; on TM restart, recovery is slow.
**Root Cause:** TM is deployed as a single instance without
replication or HA; its transaction log is on local disk.
**Diagnostic:**
```bash
# Atomikos: check TM log location and replication
ls -la /var/lib/atomikos/
# Should be on shared or replicated storage
df -h /var/lib/atomikos/
```
**Fix:** Deploy TM in HA mode (Narayana + shared DB log, or
Atomikos Extreme Transactions with active-passive failover);
ensure TM log is on replicated storage.
**Prevention:** Treat the TM as a critical infrastructure
component; apply the same HA treatment as your primary database.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-033 - Two-Phase Commit (2PC) (the algorithm XA implements)
- DST-013 - Serializability (the consistency guarantee XA targets)
- DST-032 - Failure Modes (what XA must recover from)

**Builds On This (learn these next):**
- DST-035 - Three-Phase Commit (3PC) (non-blocking alternative)
- DST-049 - Saga Pattern (modern alternative for microservices)
- DST-037 - Distributed Locking (often used alongside XA)

**Alternatives / Comparisons:**
- Saga pattern (DST-049): no 2PC, higher availability, more
  application complexity for compensation
- Outbox pattern (DST-057): solves DB + broker atomicity without XA
  via a transactional outbox table

---

### 📌 Quick Reference Card

```
+-------------------------------------------------+
| WHAT IT IS    | Standard API for 2PC across RMs  |
| PROBLEM SOLVES| Atomic commits across DB+broker  |
| KEY INSIGHT   | xa_prepare = durable promise;    |
|               | TM log = commit source of truth  |
| USE WHEN      | Must atomically coordinate 2 RMs  |
|               | in same DC; JTA/JEE environment  |
| AVOID WHEN    | Microservices across networks;   |
|               | high throughput; long transactions|
| TRADE-OFF     | Atomicity vs latency + coupling  |
| ONE-LINER     | Standard plug for 2PC across any |
|               | XA-compliant DB or broker        |
| NEXT EXPLORE  | DST-049 Saga (modern alternative)|
+-------------------------------------------------+
```

**If you remember only 3 things:**
1. XA = standard interface for 2PC across heterogeneous systems;
   the TM coordinates `xa_prepare` then `xa_commit` on all RMs.
2. The TM log is the atomic commit point; losing it causes in-doubt
   transactions that require manual DBA resolution.
3. XA is correct but expensive; prefer Saga or Outbox pattern for
   microservices or high-throughput scenarios.

**Interview one-liner:** "XA implements 2PC across heterogeneous
resource managers via a standard xa_prepare/xa_commit interface;
the Transaction Manager's write-ahead log is the atomic commit
point, enabling crash recovery without data loss."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** A durable, replicated log that
records a decision BEFORE acting on it is the universal pattern
for atomic, recoverable operations. The TM log in XA, the WAL in
Postgres, and the Raft log in distributed consensus all share this
invariant: write intent first, execute second.

**Where else this pattern appears:**
- **Database WAL:** PostgreSQL writes the intended change to its
  WAL before applying it; crash recovery replays the WAL.
- **Kafka producer idempotency:** Kafka assigns producer IDs and
  sequence numbers (a mini-log) to detect and deduplicate retried
  writes — same "log before action" principle.
- **Distributed saga log:** an explicit saga log records
  compensation actions upfront; on failure, the orchestrator
  replays the log to undo steps in reverse order.

---

### 💡 The Surprising Truth

XA transactions were designed in 1991 when a "distributed system"
meant multiple databases in the same server room connected by a
LAN. The spec assumes tight coupling and low latency between TM
and RMs. When developers try to use XA across AWS regions or
between microservices in different Kubernetes clusters, they
encounter the mismatch: XA requires the TM to hold an open
connection to every RM during the entire prepare phase, which
across a WAN means holding locks for hundreds of milliseconds.
This is why cloud-native architectures moved to Saga — not
because Saga is simpler (it is much harder to implement correctly),
but because XA's coupling model is physically incompatible with
the internet's latency profile.

---

### 🧠 Think About This Before We Continue

**Question A (System Interaction):** If the Transaction Manager
crashes AFTER writing "commit" to its log but BEFORE calling
`xa_commit` on Resource Manager 2, what exactly happens on TM
restart, and why does this not violate atomicity?
*Hint:* Trace the TM recovery procedure: what does it read from
the log, and what does it call on the in-doubt RMs?

**Question B (Scale):** Your service processes 10,000 orders per
second. Each order requires an XA transaction across a DB and a
message broker. Estimate the minimum additional latency per
transaction from XA, and determine at what throughput XA becomes
the bottleneck.
*Hint:* Consider 2 RTTs of 5 ms each (same DC) plus lock hold
time; then model queuing theory as concurrency approaches the
RM connection limit.

**Question C (Design Trade-off):** The Outbox Pattern (DST-057)
claims to solve the same "DB + broker atomicity" problem as XA
without using 2PC. Compare the failure modes of each approach:
when does Outbox win, and when does XA win?
*Hint:* Consider at-least-once vs exactly-once delivery, broker
availability requirements, and the cost of idempotent consumers.
'@

$f034 = Join-Path $base "DST-034 - XA Transactions.md"
[System.IO.File]::WriteAllText(
    (Resolve-Path ".").Path + "\" + $f034,
    $dst034,
    [System.Text.UTF8Encoding]::new($false))
Write-Host "Written DST-034: $((Get-Content $f034 -Encoding UTF8).Count) lines"

# ─── DST-036 - Optimistic Concurrency Control (Distributed) ───────────────
$dst036 = @'
---
id: DST-036
title: Optimistic Concurrency Control (Distributed)
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-033, DST-034, DST-013
used_by: DST-037, DST-055
related: DST-037, DST-033, DST-013
tags:
  - distributed
  - concurrency
  - transactions
  - deep-dive
  - advanced
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /distributed-systems/optimistic-concurrency-control/
---

# DST-036 - Optimistic Concurrency Control (Distributed)

⚡ **TL;DR** — Optimistic Concurrency Control (OCC) lets transactions
run without locks, then validates at commit time that no conflict
occurred — maximizing throughput when conflicts are rare.

| Relationship    | IDs                                     |         |
| --------------- | --------------------------------------- | ------- |
| **Depends on:** | DST-033, DST-034, DST-013               |         |
| **Used by:**    | DST-037, DST-055                        |         |
| **Related:**    | DST-037, DST-033, DST-013               |         |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Pessimistic locking (2PL) acquires locks on every read and holds
them until commit. In a distributed system, this means lock
requests cross the network: high latency, lock contention under
load, and deadlocks when two transactions wait for each other.
Systems with mostly-read workloads spend more time managing locks
than doing useful work.

**THE BREAKING POINT:**
A read-heavy catalog service uses distributed read locks. Each
product page view acquires a shared lock on the product record.
At 10,000 concurrent users, all lock requests queue behind each
other. A single slow lock-holder blocks thousands of readers.
Throughput collapses under load — the opposite of what was needed.

**THE INVENTION MOMENT:**
Kung & Robinson (1981) proposed OCC: "assume no conflict, validate
later." Transactions read freely, track what they read (read set)
and what they wrote (write set), then at commit time atomically
validate that no concurrent transaction modified their read set.
If clean: commit. If conflict: abort and retry.

**EVOLUTION:**
OCC is the foundation of MVCC (Multi-Version Concurrency Control)
used in PostgreSQL, MySQL InnoDB, and CockroachDB. Google Spanner
uses a distributed OCC variant with TrueTime timestamps for global
snapshot reads. DynamoDB uses conditional writes (a form of OCC:
`ConditionExpression: attribute_not_exists(id)`) for atomic updates.

---

### 📘 Textbook Definition

**Optimistic Concurrency Control (OCC)** is a concurrency control
scheme for databases and distributed systems in which transactions
execute without acquiring locks, then undergo a validation phase
at commit time. OCC has three phases:
1. **Read Phase:** Transaction reads data and buffers all writes
   locally; records its read set (all data read).
2. **Validation Phase:** Atomically checks that no committed
   transaction has modified the read set since the read phase
   began.
3. **Write Phase:** If validation passes, writes are applied;
   if it fails, the transaction aborts and retries.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Read freely, write locally, check for conflicts only
at commit — fast when conflicts are rare, retry when they occur.

> Like submitting a visa application assuming you will be approved.
> You fill out the form based on your current situation (read phase),
> submit (validation), and if your situation changed mid-review
> (conflict), you resubmit with updated details (retry).

**One insight:** OCC makes the optimistic bet that conflicts are
rare. If that bet is wrong (high contention workload), OCC
degrades to a retry storm. Choosing OCC vs pessimistic locking is
a judgment call about your contention profile.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. No locks held during the read phase; no other transaction is
   blocked by this transaction's reads.
2. The validation phase is atomic (often implemented as a single
   CAS or a short critical section) to prevent TOCTOU races.
3. If validation fails, ALL writes of this transaction are
   discarded; the transaction restarts from scratch.
4. The read set defines the "world view" of the transaction;
   any change to it invalidates the view.

**DERIVED DESIGN:**
Each data item carries a version number (or timestamp). On read:
record `(item, version)` in read set. On commit: for each item
in read set, atomically verify current version == recorded version.
If all match: increment version of each written item and apply
writes. If any mismatch: abort. This "version check + write" must
be atomic; in distributed systems, this is done via 2PC or a
single-shard CAS.

**THE TRADE-OFFS:**
**Gain:** Zero lock contention during reads; high throughput for
read-heavy, low-contention workloads; no deadlocks possible; no
lock manager SPOF.
**Cost:** Wasted work on conflict (entire transaction retries);
high-contention workloads cause retry storms; fairness not
guaranteed (a transaction can starve if it always loses validation);
implementing distributed validation atomically is complex.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Detecting write-write and read-write conflicts
without holding locks requires comparing version snapshots — this
is inherent.
**Accidental:** Version number storage, timestamp resolution
(OCC with physical clocks vs logical clocks), and retry backoff
strategy are implementation choices.

---

### 🧪 Thought Experiment

**SETUP:** Two users simultaneously update the same product's
stock quantity. Current quantity: 10. User A wants to buy 3.
User B wants to buy 8. Database uses OCC.

**WHAT HAPPENS WITHOUT OCC (raw read-modify-write):**
A reads 10, B reads 10. A writes 7 (10-3). B writes 2 (10-8).
Final: 2. Correct: -1 (should have rejected one purchase).
No conflict detection: inventory goes negative silently.

**WHAT HAPPENS WITH OCC:**
A reads quantity=10, version=5. B reads quantity=10, version=5.
A's read set: `{quantity: version=5}`. B's read set: same.
A validates: version still 5? YES. A writes quantity=7,
version becomes 6.
B validates: version still 5? NO (it's now 6). B ABORTS.
B retries: reads quantity=7, version=6. Validates, writes
quantity=-1. DB rejects as invalid (business rule check).
Purchase correctly denied.

**THE INSIGHT:** OCC did not prevent the conflict — it detected
it at commit time and ensured only one transaction succeeded.
The other retried with fresh data, at which point the business
rule correctly blocked the oversale.

---

### 🧠 Mental Model / Analogy

> Think of OCC like editing a shared Google Doc in offline mode.
> You make all your edits locally (read phase). When you reconnect
> (validation), Google Docs checks if anyone else edited the same
> paragraphs. If no conflicts: your changes merge in. If conflicts:
> you see the conflict markers and must re-edit (retry).

Element mapping:
- Offline editing = read phase (no locks, local changes)
- Reconnecting = validation phase (compare with current state)
- Conflict markers = validation failure (read set mismatch)
- Re-editing and resyncing = abort and retry

Where this analogy breaks down: Google Docs uses a CRDT-like
approach that merges edits rather than aborting; OCC strictly
aborts on conflict — no automatic merge.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Imagine checking out a library book by noting its shelf position,
going home to read and take notes, then returning to file your
notes. When you return, the librarian checks if anyone moved the
book since you noted its position. If yes, your notes might be
wrong — start over. If no — file your notes. No one was blocked
while you worked.

**Level 2 - How to use it (junior developer):**
OCC in practice: use `@Version` in JPA to get optimistic locking.
The DB column stores a version number; Hibernate checks it on
UPDATE and throws `OptimisticLockException` if it changed.
```java
@Entity
public class Product {
    @Version long version; // OCC version field
    int stock;
}
```
For DynamoDB: use `ConditionExpression` on writes.

**Level 3 - How it works (mid-level engineer):**
PostgreSQL's MVCC is OCC-based. Each row has `xmin` (creator
transaction ID) and `xmax` (deleter transaction ID). A read
transaction gets a snapshot of committed `xmin` values at start.
On write: create a new row version; old version is retained for
other readers. On commit: check if any row in the read set was
modified by a concurrent committed transaction. If yes: abort
(serializable isolation level enforces this via SSI — Serializable
Snapshot Isolation).

**Level 4 - Why it was designed this way (senior/staff):**
Distributed OCC requires atomic validation across multiple shards.
Spanner solves this with TrueTime: each transaction gets a commit
timestamp `T_commit` guaranteed to be after all reads. Spanner
waits `T_commit - now` seconds (commit wait) to ensure no future
read can observe a state before `T_commit`. This elegantly converts
the distributed validation problem into a time-domain problem.
CockroachDB uses HLC timestamps (DST-018) to approximate this
without GPS hardware. The insight: distributed OCC validation
reduces to "did any read-set item change between my read timestamp
and my commit timestamp?" — which is a temporal question, not a
lock question.

**Expert Thinking Cues:**
- "What is my expected conflict rate — below 5% favors OCC; above
  20% favors pessimistic locking."
- "How do I bound retry latency for high-priority transactions?"
- "Is my validation phase truly atomic, or is there a TOCTOU gap?"

---

### ⚙️ How It Works (Mechanism)

```
Transaction T1 (OCC):
  Read Phase:
    read(item_A, v=5) -> add to read_set
    read(item_B, v=3) -> add to read_set
    write item_A = new_value -> buffer locally

  Validation Phase (atomic):
    check item_A.version == 5? YES
    check item_B.version == 3? YES
    All OK -> proceed to write phase

  Write Phase:
    write item_A = new_value, version -> 6
    COMMIT

If concurrent T2 modifies item_A (version -> 6) before T1 validates:
  T1 Validation:
    check item_A.version == 5? NO (it's 6)
    ABORT -> T1 retries from scratch
```

**Distributed OCC validation (multi-shard):**
```
Coordinator:
  1. Send validate(read_set) to each shard
  2. All shards: check versions atomically
  3. All shards respond OK?
     YES -> coordinator sends commit to each shard
     NO  -> coordinator sends abort to each shard
```
This is 2PC (DST-033) applied to the validation + commit step.

---

### 💻 Code Example

```java
// BAD: read-modify-write without version check (lost update)
@Transactional
public void deductStock(Long productId, int qty) {
    Product p = productRepo.findById(productId).get();
    p.setStock(p.getStock() - qty); // RACE: another tx may have
    productRepo.save(p);            // changed stock since read
}

// GOOD: OCC with @Version (JPA optimistic locking)
@Entity
public class Product {
    @Id Long id;
    int stock;
    @Version long version; // incremented on every update
}

@Transactional
public void deductStock(Long productId, int qty) {
    Product p = productRepo.findById(productId).get();
    if (p.getStock() < qty) {
        throw new InsufficientStockException();
    }
    p.setStock(p.getStock() - qty);
    // Hibernate: UPDATE product SET stock=?, version=version+1
    //   WHERE id=? AND version=<original_version>
    // If 0 rows updated: throws OptimisticLockException
    productRepo.save(p);
}

// Retry wrapper for OCC
@Retryable(
    value = OptimisticLockingFailureException.class,
    maxAttempts = 3,
    backoff = @Backoff(delay = 50, multiplier = 2))
public void deductStockWithRetry(Long id, int qty) {
    deductStock(id, qty);
}
```

**DynamoDB OCC via conditional write:**
```java
// BAD: unconditional put -- overwrites concurrent writes
table.putItem(item);

// GOOD: conditional expression ensures version matches
UpdateItemRequest request = UpdateItemRequest.builder()
    .tableName("Products")
    .key(Map.of("id", AttributeValue.fromS(productId)))
    .updateExpression(
        "SET stock = :newStock, version = :newVersion")
    .conditionExpression("version = :expectedVersion")
    .expressionAttributeValues(Map.of(
        ":newStock",       numericValue(newStock),
        ":newVersion",     numericValue(currentVersion + 1),
        ":expectedVersion",numericValue(currentVersion)))
    .build();
// Throws ConditionalCheckFailedException on conflict
```

**How to test / verify correctness:**
```java
@Test
public void testOccPreventsLostUpdate() throws Exception {
    // Load same entity in two concurrent transactions
    Product p1 = productRepo.findById(1L).get();
    Product p2 = productRepo.findById(1L).get();

    p1.setStock(7); // T1 deducts 3 from 10
    productRepo.save(p1); // T1 commits -> version 6

    p2.setStock(2); // T2 deducts 8 from stale 10
    assertThrows(OptimisticLockingFailureException.class,
        () -> productRepo.save(p2)); // T2 should abort
}
```

---

### ⚖️ Comparison Table

| Property           | Pessimistic (2PL)   | Optimistic (OCC)    | MVCC (Postgres) |
| ------------------ | ------------------- | ------------------- | --------------- |
| Lock on read       | Yes (shared lock)   | No                  | No (snapshot)   |
| Lock on write      | Yes (exclusive)     | At commit only      | Row-version only|
| Deadlock possible  | Yes                 | No                  | No              |
| Wasted work        | None (blocked)      | Full retry on abort | Partial (SSI)   |
| Best for           | High contention     | Low contention      | Read-heavy OLTP |
| Throughput (reads) | Low (lock overhead) | High                | High            |
| Fairness           | FIFO wait queue     | Not guaranteed      | MVCC snapshots  |
| Implementation     | Lock manager        | Version columns      | Row versioning  |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "OCC never blocks" | The validation phase IS a brief critical section; at high concurrency, many transactions validating simultaneously can create contention at the version check step |
| "OCC is always faster than locking" | OCC is faster only when conflict rate is low; under high contention, repeated aborts and retries consume more CPU than blocking once would |
| "Optimistic locking means no ACID guarantees" | OCC can provide full serializable isolation (PostgreSQL SSI); it trades lock-based blocking for abort-based conflict resolution — both can be fully ACID |
| "@Version in JPA is sufficient for distributed OCC" | JPA @Version works for single-database OCC; for multi-shard or cross-service OCC, you need distributed validation and 2PC or equivalent |
| "OCC prevents all lost updates" | OCC prevents lost updates for items in the read set; if you update an item you did NOT read (write-only path), the version check may not catch conflicts |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Retry storm under high contention**

**Symptom:** CPU spikes; DB shows high abort rates; transaction
latency climbs; application logs filled with
`OptimisticLockingFailureException`.
**Root Cause:** Conflict rate exceeds ~20%; most transactions
abort and retry; each retry may conflict again — cascade of retries.
**Diagnostic:**
```sql
-- PostgreSQL: check conflict and rollback rates
SELECT xact_rollback, xact_commit,
       xact_rollback::float/(xact_commit+xact_rollback) as abort_rate
FROM pg_stat_database WHERE datname = 'mydb';
-- If abort_rate > 0.15: OCC contention too high
```
**Fix:** Switch to pessimistic locking for high-contention entities;
or partition the hot record into smaller units (e.g. per-warehouse
stock instead of global stock); add exponential backoff with jitter
on retry.
**Prevention:** Profile conflict rate per entity type; apply OCC
only where conflict rate < 10-15%.

---

**Failure Mode 2: Starvation of long-running transactions**

**Symptom:** Some transactions never commit; they repeatedly abort
after long read phases; high-priority short transactions always win.
**Root Cause:** OCC has no fairness guarantee; a short transaction
that conflicts with a long one will always win (commits faster);
the long transaction restarts and faces the same opponent.
**Diagnostic:**
```bash
# Application metrics: track per-transaction retry count
# Alert if any transaction exceeds 5 retries
grep "OptimisticLockException" app.log \
  | awk '{print $3}' | sort | uniq -c | sort -rn
```
**Fix:** After N failed retries, escalate to pessimistic locking
for that transaction; or use priority queues to sequence
conflicting transactions.
**Prevention:** Set a max-retry count with fallback; expose retry
count as a metric; alert on p99 retry count > 3.

---

**Failure Mode 3: Read set not tracked correctly (silent lost update)**

**Symptom:** Data inconsistencies under concurrent load; no
exceptions logged; inconsistent aggregate values (wrong totals,
negative counts).
**Root Cause:** Developer read an entity but the version field
was not included in the WHERE clause of the UPDATE; OCC validation
was silently bypassed.
**Diagnostic:**
```sql
-- Check if UPDATE has version check in WHERE clause
-- BAD (no OCC validation):
UPDATE product SET stock = 7 WHERE id = 1;
-- GOOD (OCC validated):
UPDATE product SET stock = 7, version = 6
  WHERE id = 1 AND version = 5;
```
**Fix:** Use ORM-level OCC (`@Version`) rather than manual SQL;
write integration tests that verify concurrent updates produce
exactly one success and one `OptimisticLockException`.
**Prevention:** Code review checklist item: every entity with
concurrent write risk must have a `@Version` field or equivalent.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- DST-013 - Serializability (isolation level OCC can provide)
- DST-033 - Two-Phase Commit (OCC validation phase uses 2PC)
- DST-034 - XA Transactions (pessimistic alternative for comparison)

**Builds On This (learn these next):**
- DST-037 - Distributed Locking (compare with pessimistic approach)
- DST-055 - CQRS (OCC enables high-throughput write paths)
- DST-056 - Event Sourcing (append-only writes avoid OCC conflicts)

**Alternatives / Comparisons:**
- Pessimistic locking / 2PL: better under high contention; blocks
  rather than aborts
- MVCC: OCC variant that retains old versions for readers; used in
  PostgreSQL, MySQL InnoDB
- CRDTs (DST-061): avoid conflict entirely via commutative ops

---

### 📌 Quick Reference Card

```
+-------------------------------------------------+
| WHAT IT IS    | Lock-free txn with commit validate|
| PROBLEM SOLVES| Lock contention in read-heavy DBs |
| KEY INSIGHT   | Conflicts are rare; validate at  |
|               | commit; abort+retry if conflict  |
| USE WHEN      | Read-heavy; conflict rate < 15%; |
|               | deadlock avoidance required      |
| AVOID WHEN    | High contention; long transactions|
|               | fairness required                 |
| TRADE-OFF     | Throughput vs wasted work on abort|
| ONE-LINER     | Assume no conflict; verify at end |
| NEXT EXPLORE  | DST-037 Distributed Locking      |
+-------------------------------------------------+
```

**If you remember only 3 things:**
1. OCC = read freely, buffer writes locally, validate at commit;
   abort and retry if any read-set item changed.
2. OCC wins on low-contention reads; pessimistic locking wins on
   high-contention writes — profile before choosing.
3. Distributed OCC validation is 2PC in disguise: the same
   latency/availability trade-offs apply.

**Interview one-liner:** "OCC eliminates lock contention by
deferring conflict detection to commit time via version checks —
maximizing throughput for read-heavy workloads at the cost of
wasted work and retries when conflicts occur."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When a bad outcome is rare,
optimistic execution followed by validation is more efficient than
defensive blocking. Measure conflict rate; choose optimism only
when failures are the exception, not the rule.

**Where else this pattern appears:**
- **Git version control:** `git push` is optimistic — you work
  locally, then push; if the remote changed (conflict), you must
  `git pull --rebase` and retry (same OCC pattern).
- **HTTP ETags:** GET returns `ETag: "v5"`; PUT includes
  `If-Match: "v5"`; server rejects with 412 if resource changed —
  web-scale OCC without a lock.
- **Kubernetes resource versions:** `kubectl apply` includes
  `resourceVersion` in the object; the API server rejects the
  write if the version changed — OCC for cluster state.

---

### 💡 The Surprising Truth

OCC was invented before NoSQL, before the cloud, and before
distributed databases — yet it underpins modern distributed
systems more deeply than most engineers realize. PostgreSQL's
SSI (Serializable Snapshot Isolation), introduced in version 9.1,
is a sophisticated OCC variant that provides full serializability
with no explicit locking, detecting even anti-dependency conflicts
(read-write cycles) that classic OCC misses. The research paper
behind SSI ("Serializable Isolation for Snapshot Databases,"
Cahill et al., 2008) showed that a pure OCC approach can match
2PL's correctness guarantees at near-MVCC performance, finally
making the "lock-free serializable database" practical. Most
engineers think OCC is a weaker, less correct approach to locking
— but at the serializable isolation level, it is equally correct
and usually faster.

---

### 🧠 Think About This Before We Continue

**Question A (System Interaction):** PostgreSQL's SSI catches
read-write anti-dependencies that classic OCC (version check only)
misses. Construct an example of a serialization anomaly that
classic OCC would not detect but SSI would, and explain why.
*Hint:* Look up the "write skew" anomaly and trace through what
happens with two transactions that each read non-overlapping rows
and write to each other's read set.

**Question B (Scale):** Amazon DynamoDB uses conditional writes
(a form of OCC) as its primary consistency mechanism. Under a
flash sale with 10,000 concurrent users competing for the last
item, what happens to DynamoDB throughput, and how would you
architect around this?
*Hint:* Consider partition key design, optimistic retry budgets,
and pre-warming inventory into a cache with pessimistic deduction.

**Question C (Design Trade-off):** Your team is choosing between
OCC and Saga (DST-049) for a multi-step order process that spans
inventory, payment, and shipping services. For each approach,
identify the key failure scenario that is harder to handle, and
which you would choose for a high-stakes financial workflow.
*Hint:* Compare what happens when step 3 of 4 fails, and how
each approach recovers: OCC via abort/retry vs Saga via
compensation.
'@

$f036 = Join-Path $base "DST-036 - Optimistic Concurrency Control (Distributed).md"
[System.IO.File]::WriteAllText(
    (Resolve-Path ".").Path + "\" + $f036,
    $dst036,
    [System.Text.UTF8Encoding]::new($false))
Write-Host "Written DST-036: $((Get-Content $f036 -Encoding UTF8).Count) lines"

Write-Host ""
Write-Host "=== All 5 DST gap entries written ==="
$bytes018 = [IO.File]::ReadAllBytes($f018)
Write-Host "DST-018 BOM: $($bytes018[0]),$($bytes018[1]),$($bytes018[2]) (must NOT be 239,187,191)"
$bytes020 = [IO.File]::ReadAllBytes($f020)
Write-Host "DST-020 BOM: $($bytes020[0]),$($bytes020[1]),$($bytes020[2]) (must NOT be 239,187,191)"
$bytes031 = [IO.File]::ReadAllBytes($f031)
Write-Host "DST-031 BOM: $($bytes031[0]),$($bytes031[1]),$($bytes031[2]) (must NOT be 239,187,191)"
$bytes034 = [IO.File]::ReadAllBytes($f034)
Write-Host "DST-034 BOM: $($bytes034[0]),$($bytes034[1]),$($bytes034[2]) (must NOT be 239,187,191)"
$bytes036 = [IO.File]::ReadAllBytes($f036)
Write-Host "DST-036 BOM: $($bytes036[0]),$($bytes036[1]),$($bytes036[2]) (must NOT be 239,187,191)"
