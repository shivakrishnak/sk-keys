---
id: DST-023
title: "Clock Skew - Clock Drift"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-040, DST-041
used_by: DST-036, DST-038, DST-039
related: DST-040, DST-041, DST-038, DST-042
tags:
  - distributed
  - networking
  - intermediate
  - production
  - tradeoff
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /distributed-systems/clock-skew-drift/
---

# DST-008 - Clock Skew - Clock Drift

⚡ TL;DR - Clock skew is the instantaneous difference between two clocks; clock drift is the rate at which they diverge — both make physical timestamps unreliable for ordering events in distributed systems.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-040, DST-041                   |     |
| **Used by:**    | DST-036, DST-038, DST-039          |     |
| **Related:**    | DST-040, DST-041, DST-038, DST-042 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer uses `System.currentTimeMillis()` on two servers to timestamp events and determine which came first. Server A sends event at 10:00:00.005; Server B receives it at 10:00:00.002 (B's clock is 3ms behind). By timestamp comparison: B "received before A sent." This is physically impossible — but entirely plausible given normal clock differences between machines. The engineer debugs a causality violation that doesn't exist in reality.

**THE BREAKING POINT:**
As systems scale to hundreds of nodes across data centers, clock disagreement becomes unavoidable. A 50ms skew between servers in different AWS regions is normal. If your Last-Write-Wins policy uses wall-clock timestamps, a 50ms skew means writes from the "wrong" server silently win — regardless of actual write order. Financial systems lose transactions. Audit logs become untrustworthy. Rate limiters allow 2x the intended rate at window boundaries.

**THE INVENTION MOMENT:**
The solution is awareness: understand clock skew and drift as fundamental properties of distributed systems, and design accordingly. For precision: Network Time Protocol (NTP) synchronizes clocks to within ±1-10ms. For safety: Lamport and vector clocks eliminate physical time dependency entirely. For high-precision: Google's TrueTime API explicitly represents time as an uncertainty interval rather than a point.

**EVOLUTION:**
1958: Crystal oscillators become standard — inherently imprecise (ppm drift). 1985: NTP v1 published (David Mills). 1991: NTP v3 — internet-scale time synchronization. 2004: IEEE 1588 Precision Time Protocol — microsecond accuracy for LAN. 2012: Spanner TrueTime — GPS+atomic clock bounded uncertainty for global linearizability. 2014: Hybrid Logical Clocks (HLC) — combines physical+Lamport for bounded skew with causality.

---

### 📘 Textbook Definition

**Clock skew** is the instantaneous difference in time readings between two clocks at a given moment. **Clock drift** is the rate at which a clock deviates from true time over time, measured in parts per million (ppm). A crystal oscillator drifts at ~1-100 ppm; at 10 ppm, a clock drifts ~1ms per 100 seconds = ~0.86 seconds per day. NTP (Network Time Protocol) counters drift by periodically adjusting clocks to match reference servers, achieving ±1ms precision on LANs and ±10-50ms over the internet. **The key distributed systems implication**: you can never assume two machines have the same wall-clock time; any system that uses physical timestamps for ordering, conflict resolution, or lease expiry must account for the maximum expected skew between the clocks it compares.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Every machine's clock runs at a slightly different rate and shows a slightly different time — these differences are clock skew and drift, and they silently break timestamp-based ordering.

> Clock drift is like two wristwatches bought at the same store: they leave the factory showing the same time, but after a week, one is 30 seconds ahead. NTP is the watchmaker who periodically resets them — but between resets, they drift apart. Clock skew is the difference at any given moment; drift is how fast they diverge.

**One insight:** NTP doesn't eliminate clock skew — it bounds it. In a correctly configured system, clocks should agree within ±10ms. But ±10ms is enough to incorrectly order events that occur within the same 20ms window. Never use physical timestamps to order events at sub-100ms granularity in distributed systems.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Physical clocks are imprecise by physics:** Crystal oscillators have manufacturing variance. No two crystals oscillate at exactly the same frequency. This is irreducible.
2. **Network-based sync has bounded error:** NTP corrects drift periodically, but network round-trip time uncertainty limits accuracy. NTP precision = f(network_jitter, stratum_count).
3. **NTP can move clocks backward:** After a large drift correction, NTP may "step" the clock backward. Code using `System.currentTimeMillis()` may observe decreasing values.
4. **Monotonic clocks don't have this problem:** OS monotonic clocks (Java's `System.nanoTime()`, Python's `time.monotonic()`) never go backward — but they measure elapsed time, not wall-clock time.

**DERIVED DESIGN:**
Use wall-clock (`currentTimeMillis`) for: human-readable timestamps, log display, TTL expiry (where ±50ms error is acceptable). Use monotonic (`nanoTime`) for: measuring durations, performance benchmarks. Use logical clocks (Lamport, vector) for: event ordering, conflict resolution, distributed causality.

**THE TRADE-OFFS:**
**Gain:** Physical timestamps are intuitive, cheap, and require no coordination — appealing for simple systems.
**Cost:** In distributed settings, physical timestamp ordering is unreliable for sub-100ms event sequences. Silent correctness bugs in ordering and conflict resolution are the result.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** No distributed system can have perfectly synchronized clocks without global coordination — which itself is a distributed systems problem.
**Accidental:** Many systems use physical timestamps for event ordering despite the known risks, creating bugs that only appear under load when multiple nodes are active simultaneously.

---

### 🧪 Thought Experiment

**SETUP:** A distributed rate limiter uses wall-clock timestamps with a 1-second sliding window. Two API gateway servers (A and B) both limit a user to 10 requests/second. Server A's clock is 500ms ahead of Server B.

**WITHOUT SKEW AWARENESS:**
User sends 10 requests to Server A at T=1000ms through T=1009ms (A's clock). All pass (10 in window). At T=1005ms (B's clock) = T=1505ms (A's clock), user sends 10 requests to Server B. B's window is T=505ms–T=1505ms. B's counter shows 0 (no requests seen in B's window — A's requests were at T=1000ms by A's clock = T=500ms by B's clock, outside B's window). All 10 pass. User makes 20 requests in ~1 second, bypassing the 10 req/s limit.

**WITH SKEW AWARENESS:**
Shared rate limit counter in Redis (single source of truth). Requests from A and B both increment the same counter. Clock skew is irrelevant — the counter is the truth, not the timestamps.

**THE INSIGHT:** Clock skew turns any distributed time-window computation into a security or correctness risk. The solution is almost always: move the truth to a single counter, or use Lamport-style monotonic ordering.

---

### 🧠 Mental Model / Analogy

> Clock skew and drift are like running a race where each runner has their own stopwatch. Each runner starts their watch at "go," but some watches run fast, some slow. At the finish line, each runner reports a different time for the same events. The race happened objectively, but the recorded times are unreliable for placing runners within a few milliseconds of each other.

**Mapping:**

- **Each runner's stopwatch** → each server's wall clock
- **Watch running fast/slow** → clock drift
- **Different start times** → initial clock skew
- **Finish time disagreement** → ordering disagreement for nearly-simultaneous events
- **Official timekeepers with GPS** → TrueTime / PTP (authoritative time sources)

Where this analogy breaks down: runners know their watch is imprecise; software engineers often assume `System.currentTimeMillis()` is the objective truth.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Every computer has an internal clock, but they don't all run at exactly the same speed. After a while, one computer thinks it's 10:00:00.005 while another thinks it's 10:00:00.002. That 3ms difference (the skew) means they can disagree about which of two events happened first. NTP fixes this periodically, but never perfectly.

**Level 2 - How to use it (junior developer):**
Rules for avoiding clock skew bugs: (1) Never use physical timestamps to order events across services. (2) Use `System.nanoTime()` for measuring durations on one machine. (3) Use Lamport timestamps or database sequence numbers for cross-service event ordering. (4) Add a safety margin ≥ 2× expected max skew for any time-based lease or window computation.

**Level 3 - How it works (mid-level engineer):**
NTP synchronizes via a hierarchy: Stratum 0 (GPS/atomic) → Stratum 1 (primary) → Stratum 2 (secondary). NTP measures round-trip time to estimate one-way offset. After a large adjustment, NTP either "steps" (jumps) the clock or "slews" it (gradually adjusts at ≤500ppm rate). Java's `System.currentTimeMillis()` reflects the wall clock — it can go backward on step. `System.nanoTime()` is monotonic and unaffected by NTP. After a 3-minute NTP slew at 500ppm: clock adjusts by 3min × 60s × 0.5ms/s = 90ms.

**Level 4 - Why it was designed this way (senior/staff):**
The alternative to tolerating skew is global clock synchronization — which requires a globally-coordinated protocol (itself a distributed systems problem). Google's Spanner solves this with TrueTime: GPS receivers and atomic clocks at every datacenter, bounded uncertainty of ±7ms. Spanner's commit-wait protocol waits for the uncertainty interval to pass before returning, guaranteeing linearizability. This costs ~7ms per commit — the price of global temporal certainty. Most systems use NTP (free, ±50ms) and tolerate the residual imprecision by using logical clocks for ordering.

**Expert Thinking Cues:**

- "Are you using timestamps for LWW conflict resolution across nodes?" → Switch to Lamport timestamps or vector clocks.
- "Are you using time-based rate limiting across multiple API gateway instances?" → Use a shared counter (Redis), not per-node windows.
- "Are you computing lease durations with `System.currentTimeMillis()`?" → Add 2× max_skew safety margin.
- "Did your distributed tests fail intermittently?" → Look for physical timestamp comparisons across nodes.

---

### ⚙️ How It Works (Mechanism)

**Crystal oscillator physics:**

```
Nominal frequency: 32.768 kHz (quartz)
Manufacturing tolerance: ±100 ppm
1 ppm = 1 microsecond per second
100 ppm = 8.64 seconds per day drift (max)
Real-world server clocks: 1-10 ppm without sync
```

**NTP synchronization process:**

```
Client → Stratum 1: "What time is it?" at T1
Stratum 1 receives at T2, sends response at T3
Client receives at T4

Round-trip delay = (T4-T1) - (T3-T2)
Offset estimate  = ((T2-T1) + (T3-T4)) / 2
Adjustment applied: step (>128ms) or slew (≤128ms)
Achieved precision: ±1ms LAN, ±10-50ms internet
```

**Java clock types:**

```java
// Wall clock — can go BACKWARD after NTP step:
long wallMs = System.currentTimeMillis();

// Monotonic — NEVER goes backward (for durations):
long nanoTime = System.nanoTime();
// Safe for: duration = end - start (on same JVM)
// NOT safe for: comparing across JVMs / machines
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (NTP-synchronized distributed system):**

```
Server A                Server B
clock=10:00:00.005      clock=10:00:00.002
                              (3ms skew)
 │                        │
Event X (ts=005)     Event Y (ts=002)
 │                        │
 │                        │
Aggregator receives both
 │
 Sorts by timestamp:
 Y (002) BEFORE X (005)
             ← YOU ARE HERE
 But X actually happened before Y by causality!
 Physical timestamps gave WRONG ordering.
```

**FAILURE PATH:**
NTP step backward: Server A's clock jumps from 10:00:00.500 to 10:00:00.450 (50ms correction). Any event at 10:00:00.490 appears to occur AFTER 10:00:00.500 by the old clock but BEFORE the corrected clock's events. Distributed logs using wall-clock timestamps become causally inconsistent for 50ms during the correction window.

**WHAT CHANGES AT SCALE:**
At 1000 nodes: expected max skew between any two nodes is larger (more nodes = more chances for high-skew pairs). Cross-DC skew (AWS us-east-1 to eu-west-1) can be ±50ms. Monitoring: `chronyc tracking` shows current offset; alert if >10ms within a DC or >100ms cross-DC.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Distributed transactions (2PC, Saga) that use wall-clock timestamps for read timestamps may see stale data from the "future" (clock-skewed node). Linearizable systems must account for maximum skew in their read protocols. Spanner's commit-wait explicitly models this — commits wait until the latest possible time uncertainty has passed.

---

### 💻 Code Example

**BAD - Using wall-clock timestamps for distributed LWW:**

```java
// Dangerous: wall-clock LWW across distributed nodes
public class WallClockStore {
    private long timestamp;
    private String value;

    // NTP skew means ts comparison is unreliable
    public synchronized void write(
        String v, long ts
    ) {
        // Server A at ts=1000, Server B at ts=999
        // (B's clock 1ms behind)
        // B's write WINS even if B wrote AFTER A
        if (ts > timestamp) {
            this.value = v;
            this.timestamp = ts;
        }
    }
}
```

**GOOD - Use logical clock for ordering, wall-clock for display only:**

```java
public class SafeDistributedStore {
    // Lamport clock for ordering — no skew risk
    private final LamportClock lamport =
        new LamportClock("nodeId");
    private long logicalTs;
    private String value;

    // Logical timestamp from sender (via message)
    public synchronized void write(
        String v, long receivedLogicalTs
    ) {
        long ts = lamport.tickOnReceive(receivedLogicalTs);
        if (ts > logicalTs) {
            this.value = v;
            this.logicalTs = ts;
        }
    }

    // Duration measurement: use monotonic clock
    public long measureLatency(Runnable op) {
        long start = System.nanoTime(); // monotonic
        op.run();
        return System.nanoTime() - start; // safe
    }

    // Human display only: use wall clock
    public String getLastWriteTime() {
        // currentTimeMillis OK here — display only
        return new Date(System.currentTimeMillis())
            .toString();
    }
}
```

**How to test / verify correctness:**

```bash
# Check NTP sync status on a node:
chronyc tracking
# Key metrics:
# "System time": current offset from NTP (should be <10ms)
# "RMS offset": average recent offset
# "Frequency": drift rate in ppm

# Check all servers' clock offsets:
for host in server{1..10}; do
  echo -n "$host: "
  ssh $host "chronyc tracking | grep 'System time'"
done

# Alert if any offset > 10ms within DC:
# timedatectl status | grep "NTP synchronized"
```

---

### ⚖️ Comparison Table

| Mechanism            | Accuracy              | Requires        | Use Case               |
| :------------------- | :-------------------- | :-------------- | :--------------------- |
| NTP                  | ±1-50ms               | Network         | General servers        |
| PTP (IEEE 1588)      | ±1 microsecond        | Hardware PTP    | Finance, telecom       |
| GPS disciplined      | ±100ns                | GPS antenna     | Data center primary    |
| TrueTime (Spanner)   | ±7ms bounded interval | GPS+atomic      | Global linearizability |
| Lamport clock        | N/A (logical)         | Message passing | Event ordering         |
| Hybrid Logical Clock | Physical + logical    | NTP + Lamport   | Causality + timestamps |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                          |
| :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "NTP makes clocks perfectly synchronized"            | NTP bounds skew to ±1-50ms but does not eliminate it. For correctness within single-millisecond windows, NTP is insufficient.                                                    |
| "`System.currentTimeMillis()` is monotonic"          | False. On Linux (and Java), wall-clock time can decrease after an NTP step correction. Only `System.nanoTime()` is guaranteed monotonic.                                         |
| "Clock skew is only a few milliseconds — negligible" | At network speeds, 10ms = ~100km of lightspeed propagation. For LWW conflict resolution, database snapshots, or rate limiting, 10ms skew is substantial.                         |
| "Adding NTP to all servers solves clock skew"        | NTP reduces clock skew but doesn't eliminate it. For ordering events within a millisecond of each other, use logical clocks — which are insensitive to any amount of clock skew. |
| "PTP gives microsecond accuracy on any network"      | PTP achieves microsecond accuracy only with hardware timestamping support in NICs and switches. Software PTP on commodity hardware degrades to ~100 microsecond accuracy.        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: NTP Step Causes Timestamp Inversion**

**Symptom:** Distributed log shows events "going back in time." Event at 10:00:00.500 is followed by event at 10:00:00.450. Causality appears violated in logs.
**Root Cause:** NTP step correction applied to a server that was running 50ms fast. Wall-clock jumped backward 50ms. Any event logged after the step appears to occur "before" events logged just before the step.
**Diagnostic:**

```bash
# Check if NTP made a step correction recently:
grep "Time stepped" /var/log/chrony/measurements.log
# Or check system journal:
journalctl -u chronyd --since "1 hour ago" | grep -i step
# Verify NTP mode (step vs slew):
chronyc makestep  # force step; check if slew is configured
```

**Fix:**
BAD: Using wall-clock timestamps for distributed log ordering without monotonic clock awareness.
GOOD: Append Lamport timestamp OR use OS monotonic clock for duration measurements. Wall-clock timestamps are for display only.
**Prevention:** Configure NTP to prefer "slew" mode (gradual adjustment) over "step" to avoid backward jumps. For critical systems: use `CLOCK_MONOTONIC` (Linux), not `CLOCK_REALTIME`.

**Failure Mode 2: Rate Limiter Bypassed via Clock Skew**

**Symptom:** API rate limit (10 req/sec) is enforced per gateway node. Users exceed the limit by routing requests across multiple gateway instances. No error returned; limit silently bypassed.
**Root Cause:** Each gateway uses a local wall-clock sliding window. With >100ms skew between gateways, a user can submit up to 2× the limit before any window overlap triggers a block.
**Diagnostic:**

```bash
# Estimate exploitable requests = limit * (2 * max_skew_sec)
# max_skew 100ms = 0.1s → extra = 10 req/s * 0.1 * 2 = 2 req
# For limit=100/min = 1.67/s: extra = 1.67 * 0.2 = 0.33 req
# Acceptable for low limits; unacceptable for high
```

**Fix:**
BAD: Per-node sliding windows based on local wall-clock.
GOOD: Shared rate limit counter in Redis with atomic INCR. Time window boundaries based on a single authoritative clock (Redis server), not per-gateway wall clocks.
**Prevention:** Centralize rate limit state. Use Redis sorted sets with ZADD/ZCOUNT for sliding windows.

**Failure Mode 3: Security - Distributed Lease Expiry Race Condition**

**Symptom:** After a lease expires, two nodes briefly believe they hold the lease simultaneously. Split-brain ensues — both write to the same resource, causing data corruption.
**Root Cause:** Lease holder's clock runs 20ms slow. It believes lease expires at T+5000ms (actual T+4980ms). Coordinator's clock is accurate — it revokes the lease at T+5000ms and grants it to a new holder at T+5001ms. For 20ms, both nodes believe they hold valid leases.
**Diagnostic:**

```bash
# Check offset between lease holder and coordinator:
ssh lease-holder "chronyc tracking | grep 'System time'"
ssh coordinator  "chronyc tracking | grep 'System time'"
# If delta > lease_safety_margin: misconfigured
```

**Fix:**
BAD: Lease expiry without clock skew safety margin.
GOOD: `lease_duration > intended_duration + 2 * max_skew`. Additionally: use fencing tokens (DST-013) — monotonically increasing token per grant, storage rejects writes from holders with lower tokens.
**Prevention:** Never rely solely on clock-based lease expiry for exclusive access. Always add fencing tokens as a correctness backup.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-040 - Lamport Clock (the logical alternative to physical timestamps)
- DST-041 - Vector Clock (extends Lamport for concurrent event detection)

**Builds On This (learn these next):**

- DST-036 - Strong Consistency (TrueTime enables Spanner's global linearizability)
- DST-038 - Linearizability (requires bounding clock uncertainty for correctness proofs)
- DST-042 - Clock Skew Clock Drift (deep-dive: mechanisms, HLC, monotonic clocks)

**Alternatives / Comparisons:**

- DST-040 - Lamport Clock (eliminates physical time dependency entirely)
- DST-042 - Clock Skew Clock Drift (more advanced treatment of this topic)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Skew=instant clock difference; |
|                  | drift=rate of divergence (ppm) |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Physical timestamps are        |
|                  | unreliable for event ordering  |
+------------------+--------------------------------+
| KEY INSIGHT      | NTP bounds skew; it doesn't    |
|                  | eliminate it. Use logical clks |
+------------------+--------------------------------+
| USE WHEN         | Understanding why LWW, leases, |
|                  | & rate limits fail at scale    |
+------------------+--------------------------------+
| AVOID WHEN       | "currentTimeMillis for ordering"|
|                  | across distributed nodes       |
+------------------+--------------------------------+
| TRADE-OFF        | Physical timestamps (easy) vs  |
|                  | logical clocks (correct)       |
+------------------+--------------------------------+
| ONE-LINER        | Two server clocks differ by    |
|                  | ±50ms; never order by them     |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-040 Lamport Clock,         |
|                  | DST-042 Clock Skew (deep dive) |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Clock drift makes clocks diverge; NTP corrects periodically but leaves ±1-50ms skew.
2. `System.currentTimeMillis()` can go backward after NTP correction. `System.nanoTime()` is monotonic (use for durations, not ordering).
3. Never use physical timestamps for LWW conflict resolution or event ordering across distributed nodes — use Lamport/vector clocks instead.

**Interview one-liner:**
"Clock skew is the instantaneous difference between two machines' clocks; clock drift is the rate at which they diverge (±100 ppm without NTP). NTP bounds skew to ±1-50ms but can't eliminate it — meaning physical timestamps are unreliable for ordering distributed events within sub-100ms windows, requiring logical clocks (Lamport, vector) for correctness."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any system that assumes two independently-maintained counters (clocks, sequence numbers, IDs) agree without explicit coordination is fragile. The principle extends beyond clocks: independently-incremented counters in distributed systems will drift. The solution is always the same — either coordinate (NTP, vector clocks, shared state) or design for divergence (use logical clocks, idempotent operations, or explicit conflict resolution).

**Where else this pattern appears:**

- **Financial market timestamps:** Stock exchanges and trading systems use PTP (nanosecond precision) because microsecond timestamp disagreements between buyer and seller can determine trade priority. MiFID II regulation requires clock accuracy within 100 microseconds. "Clock skew" is a regulated risk in financial markets, not just an engineering concern.
- **Database read-your-writes consistency:** DynamoDB uses "session tokens" (essentially Lamport timestamps for each session) because waiting for NTP-synchronized clock agreement would add 50ms+ to every read. Logical session tokens solve the read-your-writes problem without any clock synchronization dependency.
- **Multi-region CDN cache invalidation:** CDN cache purge messages travel at speed-of-light across continents. A cache purge sent at T=0 may arrive at different PoPs at T+30ms and T+150ms. Purge ordering based on physical timestamps is unreliable — CDNs use version numbers (Lamport equivalents) to determine which purge instruction is the latest.

---

### 💡 The Surprising Truth

When Amazon engineers designed the Dynamo paper (2007), they explicitly chose NOT to use NTP-based wall-clock timestamps for Last-Write-Wins — even though Dynamo's AP design made eventual consistency necessary. The reason: they knew wall-clock LWW would produce silent, user-invisible data loss at Amazon's scale. Instead, Dynamo uses vector clocks (version vectors) to detect conflicts and return "siblings" to the client application. The "vector clock" section of the Dynamo paper was directly motivated by the authors' experience with clock skew bugs in earlier Amazon systems. The irony: DynamoDB (Dynamo's successor) later introduced wall-clock LWW as the default mode for simplicity — acknowledging that most applications prefer occasional silent data loss to mandatory conflict handling. Dynamo was principled; DynamoDB is pragmatic. Understanding clock skew is what allows engineers to make that trade-off consciously.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A distributed cache uses NTP-synchronized timestamps on each node for cache entry expiry (TTL). An item's TTL is 60 seconds. Node A's clock is 200ms ahead of Node B. What is the maximum error in expiry timing between nodes? Is this acceptable for a session token cache where expired tokens must not be accepted?
_Hint:_ Node A will expire the item 200ms early relative to Node B. For 60-second TTLs: 200ms/60,000ms = 0.3% error. For session tokens: is a 200ms window where one node accepts and another rejects the same token a security risk? Who wins — the node that accepts or the one that rejects?

**Q2 (D - Root Cause):** A distributed leaderboard uses `System.currentTimeMillis()` for scoring timestamps across 10 leaderboard servers. Players report that their scores sometimes appear "earlier" than scores they know occurred before theirs. What is the precise mechanism — and would switching to `System.nanoTime()` fix the problem?
_Hint:_ `nanoTime()` is monotonic within a JVM but NOT synchronized across JVMs. Two servers can have `nanoTime()` values that are entirely incomparable — they measure time since JVM start, not wall time. What is the correct tool for cross-server event ordering?

**Q3 (E - First Principles):** TrueTime (Spanner) represents time as an interval [earliest, latest] rather than a point. Commits wait until `now.earliest > commit_timestamp`. Why is the interval representation essential for global linearizability — and what would break if Spanner used a point timestamp (even from GPS) instead?
_Hint:_ A GPS timestamp has microsecond accuracy but still has bounded uncertainty (signal processing, atmospheric delay). If Spanner used a point timestamp from GPS and two commits on opposite sides of the Earth both got GPS timestamp T=1000, what would their causal ordering be? Can GPS accuracy alone guarantee two events in different datacenters are totally ordered without the commit-wait protocol?

