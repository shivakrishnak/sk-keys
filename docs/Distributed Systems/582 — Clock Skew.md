---
layout: default
title: "Clock Skew"
parent: "Distributed Systems"
nav_order: 582
permalink: /distributed-systems/clock-skew/
number: "582"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Lamport Clock, Distributed Systems Fundamentals"
used_by: "Hybrid Logical Clock, TrueTime, Distributed Transactions"
tags: #intermediate, #distributed, #clocks, #time, #synchronization
---

# 582 — Clock Skew

`#intermediate` `#distributed` `#clocks` `#time` `#synchronization`

⚡ TL;DR — **Clock Skew** is the difference between the physical clocks of two nodes in a distributed system — a fundamental problem that makes wall-clock timestamps unreliable for ordering events across machines.

| #582            | Category: Distributed Systems                            | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Lamport Clock, Distributed Systems Fundamentals          |                 |
| **Used by:**    | Hybrid Logical Clock, TrueTime, Distributed Transactions |                 |

---

### 📘 Textbook Definition

**Clock Skew** is the difference in clock values between two nodes in a distributed system at any given moment. It arises because physical clocks are subject to hardware frequency variations (crystal oscillators drift 10–100 ppm), temperature effects, and NTP synchronization latency. NTP (Network Time Protocol) reduces clock skew to typically 1–50ms within a datacenter and 50–500ms across the internet, but cannot eliminate it entirely. Clock skew creates critical problems for distributed systems that rely on timestamps for ordering: two events on different nodes with the same "timestamp" may have occurred in different orders than the timestamps suggest; a node with a clock ahead by 200ms appears to generate events "in the future" relative to a slow-clock node. Solutions include: **logical clocks** (Lamport, Vector) which are skew-immune by design; **Hybrid Logical Clocks** (HLC) which combine physical and logical clocks; and **Google TrueTime**, which uses GPS + atomic clocks to bound skew to ε < 7ms, enabling globally consistent timestamps within a known uncertainty interval.

---

### 🟢 Simple Definition (Easy)

Clock skew: two computers show different times even though they're running simultaneously. Computer A says 14:30:00.100, Computer B says 14:30:00.350 at the exact same instant — a 250ms difference. This means "event timestamps" from A and B can't be trusted to tell which happened first. NTP tries to keep computers synchronized, but can only get to ~1-50ms accuracy in a datacenter — not good enough for many distributed systems.

---

### 🔵 Simple Definition (Elaborated)

Clock skew breaks assumptions in distributed systems. Example: database transaction commit order. Transaction T1 commits on Node A at 14:30:00.100. Transaction T2 commits on Node B at 14:30:00.050 (Node B's clock is 50ms behind). If you order by timestamp: T2 (050ms) appears before T1 (100ms). But in real wall-clock time, T2 committed AFTER T1. Causally wrong order. This is why databases like CockroachDB don't rely on OS timestamps directly — they use Hybrid Logical Clocks that guarantee monotonicity and causal correctness despite clock skew.

---

### 🔩 First Principles Explanation

**Clock skew sources, measurement, and mitigation strategies:**

```
SOURCES OF CLOCK SKEW:

1. CRYSTAL OSCILLATOR DRIFT:
   CPU clock crystal oscillates at ~32,768 Hz or higher.
   Accuracy: ±20–100 ppm (parts per million).

   Calculation:
     20 ppm drift = 20 microseconds per second.
     In 1 hour: 20 × 3600 = 72,000 μs = 72ms drift.
     Without NTP correction: two nodes can drift 72ms/hour relative to each other.

   TCXO (Temperature-Compensated Crystal Oscillator): ±1 ppm (better hardware).
   Atomic clock: ±0.0001 ppm (used by GPS and TrueTime).

2. NTP SYNCHRONISATION:
   NTP adjusts clock by comparing with stratum-1 servers (GPS or atomic reference).

   NTP accuracy tiers:
     Stratum 0 (GPS/atomic): ±1 nanosecond reference
     Stratum 1 (directly connected): ±1–50μs
     Stratum 2 (internal NTP servers): ±1–10ms
     Stratum 3 (most servers): ±10–100ms

   Measurement of NTP offset:
     t1: client sends request at time T1 (client clock)
     t2: server receives at T2 (server clock)
     t3: server responds at T3 (server clock)
     t4: client receives at T4 (client clock)

     Round-trip delay: δ = (T4 - T1) - (T3 - T2)
     Clock offset: θ = ((T2 - T1) + (T3 - T4)) / 2
     Assumes: network delay is symmetric (equal each way).
     Error: if asymmetric delay (different paths outbound/inbound): offset measurement wrong.

   In practice:
     LAN: ±0.1ms accuracy achievable with PTP (Precision Time Protocol).
     WAN (internet): ±10–100ms typical with NTP.
     AWS, GCP, Azure: dedicated NTP infrastructure → typically ±1–5ms.

3. LEAP SECONDS:
   Earth's rotation irregularities require periodic 1-second adjustments to UTC.
   NTP: "smears" leap seconds over 24 hours (±0.5 ppm during smear period).
   Linux: can insert leap second at midnight → clocks "pause" for 1 second.
   Impact: timestamps at midnight on leap second day may be duplicated or skipped.

   Google, AWS, Azure: use leap second smearing by default.
   Systems sensitive to timestamp ordering: must be aware of leap second handling policy.

CLOCK SKEW IMPACT ON DISTRIBUTED SYSTEMS:

1. LAST-WRITE-WINS WITH SKEWED CLOCKS:

   Cassandra LWW: highest timestamp wins.
   Node A: clock 200ms ahead. Writes value=5 at "T=14:30:00.200" (real time 14:30:00.000).
   Node B: accurate clock. Writes value=10 at T=14:30:00.100 (real time: actually after A's write).

   LWW compares timestamps: A's "200ms" > B's "100ms" → A's write wins → value=5.
   Reality: B's write happened AFTER A's write in real time.

   Data loss: B's write (value=10, the correct later value) is silently discarded.
   Root cause: 200ms clock skew on Node A caused incorrect ordering.

2. DISTRIBUTED TRANSACTION ORDERING (CockroachDB):

   Transaction T1 on Node A, T2 on Node B. Both trying to read same key.
   T1's commit timestamp: 14:30:00.100 (A's clock).
   T2's read timestamp: 14:30:00.050 (B's clock, 50ms behind).

   If B's node serves T2 from replica: may not have seen T1's commit (committed at 100ms).
   T2 reads stale data without realising T1 was "in the past" relative to B's clock.

   CockroachDB's solution: "uncertainty interval" = max expected clock skew (500ms default).
   When T2 reads a value timestamped in T2's uncertainty window, T2 may restart (retry).
   This prevents reading stale data due to clock skew.

3. DISTRIBUTED LOCKS WITH LEASE EXPIRY:

   Raft leader lease: "I hold the lease for 300ms (election timeout). No other leader possible."
   Lease start: T=14:30:00.000 on leader's clock. Expires: T=14:30:00.300.

   If leader's clock drifts 50ms FAST (runs ahead):
     Leader's real lease expired at real-time 14:29:59.950 (300ms of leader's FAST time = 250ms real time).
     Leader continues serving reads thinking it holds valid lease.
     Meanwhile: actual 300ms real time has passed → new leader could be elected.
     Two leaders simultaneously → split-brain → linearisability violation.

   Fix: etcd uses clock-skew-aware lease with safety margin.
        Subtract max_clock_skew from lease duration.
        Lease effective duration = config_lease - max_clock_skew.

GOOGLE TRUERIME:

  TrueTime is Google's global time API (used by Google Spanner).

  Components:
    GPS receivers: ±1 microsecond accuracy, but vulnerable to outages (indoor, jamming).
    Atomic clocks: ±0.1 ppm drift, less accurate but fault-tolerant (no RF signal needed).
    Redundancy: each datacenter has multiple GPS + atomic clocks. Cross-validates signals.

  API: TT.now() returns [earliest, latest] — an interval, not a point.
       If TT.now() = [14:30:00.100, 14:30:00.107], the true time is SOMEWHERE in this 7ms interval.
       ε (epsilon) = uncertainty bound. Spanner keeps ε < 7ms typically.

  Usage in Spanner commit protocol:
    1. Transaction prepared to commit.
    2. Spanner calls TT.now() → gets interval [t_earliest, t_latest].
    3. Assigns commit timestamp = t_latest (conservative: ensures no other committed
       transaction can have a later timestamp from a skewed clock).
    4. WAITS until TT.now().earliest > t_latest ("commit wait" = wait for ε to pass).
    5. After commit wait: CERTAIN that true time > commit timestamp everywhere.
    6. Responds to client.

  Result: globally consistent commit ordering. Any transaction that commits after T=14:30:00.107
          is GUARANTEED to see this transaction's writes (by TrueTime ordering).

  Cost: commit latency ≥ 2ε (at least 2 × 7ms = 14ms per transaction).
        This is the price of global consistent ordering in Spanner.

PRACTICAL CLOCK SKEW VALUES IN PRODUCTION:

  AWS, GCP, Azure: NTP infrastructure → typically ±1–5ms between instances.
  Multi-region: ±50–200ms between regions.
  CockroachDB default max_offset: 500ms (cluster aborts if node exceeds this).
  Spanner TrueTime ε: typically 3–7ms.

  NTP monitoring (Linux):
  $ chronyc tracking   → Shows RMS offset (e.g., "System time offset: 0.000123 seconds")
  $ timedatectl status → Shows NTP sync status and offset.

  Alert threshold: set alerts if NTP offset > 50ms. Investigate > 100ms.
  CockroachDB: $ cockroach debug check-store → validates clocks are within max_offset.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT understanding clock skew:

- Timestamp-based ordering silently wrong: wrong winner in LWW conflicts
- Distributed lock leases expire incorrectly: potential split-brain
- Developers trust system timestamps for event ordering across nodes — incorrect assumption

WITH clock skew awareness:
→ Use logical clocks (Lamport, Vector, HLC) instead of wall-clock for event ordering
→ Bound-based approaches (TrueTime): know the uncertainty and design around it
→ Correct lease durations: factor in max clock skew for safety margins

---

### 🧠 Mental Model / Analogy

> Two referees at opposite ends of a sports field, each with their own stopwatch, trying to coordinate simultaneous events. Even if both start their stopwatches at the same moment, by the end of the game the watches show slightly different elapsed times (crystal oscillator drift). One watch reads 90:00, the other 90:07. If you order events by stopwatch time, events at minute 89:55 on the slow watch might actually have occurred after events at 90:00 on the fast watch. NTP is like a central timekeeper periodically calling in corrections: "Slow down, you're 7 seconds ahead." But the correction itself takes time (the call), so the referees are never perfectly in sync.

"Two referees' stopwatches drifting apart" = clock skew between two nodes
"NTP correction call takes time" = NTP synchronization delay introduces its own uncertainty
"Order events by stopwatch time" = using physical timestamps for distributed event ordering
"Central timekeeper" = NTP server (stratum 1 or GPS)

---

### ⚙️ How It Works (Mechanism)

**Measuring clock skew and configuring NTP on Linux:**

```bash
# Check current NTP synchronization status and clock offset:
$ chronyc tracking
Reference ID    : 169.254.169.123 (169.254.169.123)   # AWS NTP server
Stratum         : 4
Ref time (UTC)  : Mon Oct 14 14:30:00.123456789 2024
System time     : 0.000041207 seconds fast of NTP time  # 41 microseconds ahead
RMS offset      : 0.000023456 seconds                  # Typical variation
Frequency       : -3.456 ppm                           # Crystal drift rate
Residual freq   : +0.001 ppm
Skew            : 0.123 ppm
Root delay      : 0.000456 seconds                     # Network delay to NTP server
Root dispersion : 0.000678 seconds                     # Worst-case dispersion

# Monitor NTP offset over time — alert if > 50ms:
$ chronyc tracking | grep "System time" | awk '{print $4}'
# → 0.000041207 seconds (good: 41 microseconds)

# AWS EC2: use Amazon Time Sync Service (PTP-based, ±1ms):
# In /etc/chrony.conf:
server 169.254.169.123 prefer iburst
# or for PTP:
server 169.254.169.123 prefer iburst minpoll 4 maxpoll 4

# Check if PTP hardware timestamping available (reduces to ±10μs):
$ ethtool -T eth0 | grep "hardware-transmit"
# hardware-transmit → PTP hardware support available.

# CockroachDB: check cluster clock skew:
$ cockroach debug check-store --host=localhost:26257 --certs-dir=certs
# Alerts if any node exceeds --max-offset (default 500ms).
```

---

### 🔄 How It Connects (Mini-Map)

```
Physical Clocks (drift, not globally synchronized)
        │ problem
        ▼
Clock Skew ◄──── (you are here)
(difference between node clocks; undermines timestamp ordering)
        │
        ├── Lamport Clock / Vector Clock (avoid problem by using logical clocks)
        ├── Hybrid Logical Clock (combines physical + logical for bounded skew)
        └── TrueTime (GPS+atomic clock bounded uncertainty; Spanner)
```

---

### 💻 Code Example

**Hybrid Logical Clock (HLC) — production solution for clock skew:**

```java
/**
 * Hybrid Logical Clock (HLC) - Kulkarni, Demirbas et al. 2014.
 * Combines wall clock (physical) with logical counter.
 * Guarantees: HLC >= physical time. Causality preserved. Skew bounded by NTP accuracy.
 * Used by: CockroachDB, YugabyteDB.
 */
public class HybridLogicalClock {

    // HLC = (wallTime, logicalCounter)
    // wallTime: milliseconds since epoch (from NTP-synced system clock)
    // logical: tie-breaker within same millisecond; advances on receive

    private volatile long wallTime = 0;
    private volatile int logical = 0;
    private final Object lock = new Object();

    /** Call before any local event or send. Returns HLC timestamp. */
    public long[] tick() {
        synchronized (lock) {
            long now = System.currentTimeMillis();
            if (now > wallTime) {
                wallTime = now;
                logical = 0;
            } else {
                logical++;  // Same millisecond: increment logical counter
            }
            return new long[]{wallTime, logical};
        }
    }

    /** Call on receiving a message. Returns updated HLC. */
    public long[] receive(long msgWallTime, int msgLogical) {
        synchronized (lock) {
            long now = System.currentTimeMillis();
            long newWall = Math.max(Math.max(wallTime, msgWallTime), now);

            if (newWall == wallTime && newWall == msgWallTime) {
                logical = Math.max(logical, msgLogical) + 1;
            } else if (newWall == wallTime) {
                logical = logical + 1;
            } else if (newWall == msgWallTime) {
                logical = msgLogical + 1;
            } else {
                logical = 0;  // now > both → reset logical
            }

            wallTime = newWall;
            return new long[]{wallTime, logical};
        }
    }

    // HLC guarantee: if A → B (causally), then HLC(A) < HLC(B) (lexicographically)
    // HLC is always ≥ physical clock → events have human-readable timestamps
    // HLC differs from physical clock by at most max NTP offset (~5ms in AWS)
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NTP makes clocks perfectly synchronized                      | NTP reduces skew to ~1–50ms in a datacenter, NOT zero. The synchronization correction itself depends on symmetric network latency (which is not always the case). Even with PTP (Precision Time Protocol) using hardware timestamping, skew can be ±10–100μs. For most applications 1ms skew is fine; for timestamp-ordered distributed transactions, even 1ms can matter                                      |
| Monotonically increasing timestamps are immune to clock skew | System clocks can go backwards after NTP correction. If NTP finds the clock is 200ms ahead, it gradually slows the clock ("slew rate" ≤ 500ppm) or can step it backwards. `System.currentTimeMillis()` can return a smaller value than a previous call during a backward correction. Use monotonic clocks (`System.nanoTime()`, `CLOCK_MONOTONIC`) for measuring elapsed time                                  |
| Clock skew only matters for global distributed systems       | Clock skew matters even within a single datacenter. AWS measured ±1–5ms skew between instances in the same availability zone. For database replication, distributed locks, and event ordering: even 5ms of skew can cause issues. Kafka's Exactly-Once Semantics and CockroachDB both have to account for intra-datacenter clock skew in their correctness proofs                                              |
| TrueTime eliminates clock skew                               | TrueTime bounds clock uncertainty to ε ≈ 7ms — it doesn't eliminate it. The key innovation is knowing the BOUNDS: TrueTime.now() returns [earliest, latest] instead of a single value. By waiting ε after a commit before returning to the client (commit wait), Spanner ensures any future transaction sees this transaction's writes. The uncertainty is not eliminated — it's accounted for in the protocol |

---

### 🔥 Pitfalls in Production

**NTP clock going backwards during correction — breaks monotonicity:**

```
PROBLEM: System.currentTimeMillis() returns smaller value after NTP backward correction.
         Code using timestamps for ordering gets confused: "time went backwards."

  Application: event ID generator using currentTimeMillis() as part of ID.
  Scheme: event_id = (timestamp_ms << 12) | sequence_within_ms

  At 14:30:00.200: event_id = (1728907800200 << 12) | 0 = some large number.
  NTP correction: clock steps back 50ms.
  At 14:30:00.180 (after backward step): event_id uses 1728907800180 << 12.

  New event_id < previous event_id → ID ordering violated!
  Database inserts with ID-based ordering: new events appear before old ones.

  Bug manifestation: "records appearing out of order in time-series data"
                     "duplicate IDs generated" (same timestamp reused after step-back)

BAD: Using System.currentTimeMillis() for monotonic IDs:
  long eventId = System.currentTimeMillis();  // can go backwards after NTP correction!

FIX 1: MONOTONIC CLOCK for elapsed time, wall clock for timestamps:
  // Java: System.nanoTime() = CLOCK_MONOTONIC (never goes backwards, not wall-clock)
  // Use nanoTime() for measuring durations and ordering within a process.
  // Use currentTimeMillis() for human-readable timestamps (accept rare non-monotonicity).

FIX 2: SNOWFLAKE ID GENERATOR (Twitter) — wall clock + sequence + node ID:
  public class SnowflakeIdGenerator {
      private long lastTimestamp = -1;
      private long sequence = 0;
      private final long nodeId;

      public synchronized long nextId() {
          long timestamp = System.currentTimeMillis();

          if (timestamp < lastTimestamp) {
              // Clock went backwards! Wait until we catch up, or throw exception:
              long waitMs = lastTimestamp - timestamp;
              if (waitMs > 5) throw new RuntimeException("Clock moved backwards " + waitMs + "ms");
              // For small skew: wait:
              try { Thread.sleep(waitMs); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
              timestamp = System.currentTimeMillis();
          }

          if (timestamp == lastTimestamp) {
              sequence = (sequence + 1) & 0xFFF;  // 12-bit sequence (4096/ms)
              if (sequence == 0) timestamp = waitNextMs(lastTimestamp);  // Wait for next ms
          } else {
              sequence = 0;
          }

          lastTimestamp = timestamp;
          return (timestamp << 22) | (nodeId << 12) | sequence;
      }
  }
```

---

### 🔗 Related Keywords

- `Lamport Clock` — logical clock immune to clock skew
- `Hybrid Logical Clock` — production solution: physical + logical, bounded skew
- `TrueTime` — GPS+atomic clock API with known uncertainty bound (Google Spanner)
- `Distributed Transactions` — commit ordering requires addressing clock skew

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Difference between node clocks (~1-50ms   │
│              │ in DC); makes wall-time ordering          │
│              │ unreliable across nodes                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Auditing timestamp-based ordering; sizing │
│              │ CockroachDB max_offset; Spanner commit    │
│              │ wait tuning                               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using wall-clock for distributed ordering │
│              │ (use logical/hybrid clocks instead)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two referees' stopwatches drift apart;   │
│              │  NTP corrects but never perfectly syncs." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hybrid Logical Clock → TrueTime →        │
│              │ Lamport Clock → Distributed Transactions  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** CockroachDB sets a default `max-offset` of 500ms between nodes. If a node's clock deviates more than 500ms, CockroachDB shuts it down. Why 500ms specifically? What would happen if CockroachDB allowed unlimited clock skew? Describe a concrete scenario where a 1-second clock skew between two nodes causes a transaction that should have been serialisable to instead produce incorrect results.

**Q2.** Google Spanner's "commit wait" forces each transaction to pause for at least 2ε (ε = TrueTime uncertainty, ~7ms) before returning to the client. This adds at least 14ms to every write transaction's latency. Explain precisely why this wait is necessary for external consistency. What specific concurrency anomaly would occur if Spanner skipped the commit wait? Provide a concrete example with two transactions T1 and T2 where skipping commit wait leads to a causal consistency violation.
