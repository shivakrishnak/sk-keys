---
layout: default
title: "Clock Skew / Clock Drift"
parent: "Distributed Systems"
nav_order: 582
permalink: /distributed-systems/clock-skew-drift/
number: "0582"
category: Distributed Systems
difficulty: ★★☆
depends_on: Distributed Systems Fundamentals, NTP, Lamport Clock
used_by: Distributed Transactions, Event Ordering, Lease Management
related: Lamport Clock, Vector Clock, Linearizability, Spanner TrueTime
tags:
  - clock-skew
  - clock-drift
  - ntp
  - distributed-systems
  - intermediate
---

# 582 — Clock Skew / Clock Drift

⚡ TL;DR — Clock Skew is the difference in time between two clocks at a moment in time; Clock Drift is the rate at which a clock diverges from true time. In distributed systems, every machine has an independent hardware clock that drifts relative to real time, causing skew between nodes. This invalidates wall-clock-based event ordering, invalidates lease-based logic, and breaks distributed protocols that assume synchronized time. Solutions include NTP (reduces ms-level skew), GPS/atomic clocks (μs), and Google's TrueTime (uncertainty-bounded clock API).

| #582 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Distributed Systems Fundamentals, NTP, Lamport Clock | |
| **Used by:** | Distributed Transactions, Event Ordering, Lease Management | |
| **Related:** | Lamport Clock, Vector Clock, Linearizability, Spanner TrueTime | |

---

### 🔥 The Problem This Solves

**THE DISTRIBUTED CLOCK PROBLEM:**
Server A logs event at 10:00:00.001. Server B logs event at 10:00:00.000.
You sort events by timestamp: B then A. But A's event actually happened first — Server B's clock is 5ms behind Server A's (clock skew). Your entire event log is out of order. Worse: a distributed database uses wall-clock "write timestamp" for Last-Write-Wins conflict resolution. Server A writes x=5 at T=100ms. Server B writes x=7 at T=99ms (B's clock is 1ms behind). The database picks x=5 as the "newer" write — but the intention was the opposite, silently discarding x=7.

This is why you CANNOT use physical clocks alone for distributed event ordering, distributed locking, or conflict resolution. Understanding clock skew and drift is fundamental to understanding every distributed system's design.

---

### 📘 Textbook Definition

**Clock Drift** is the rate at which a clock's frequency deviates from true frequency, measured in parts per million (ppm). A typical quartz clock drifts at 10–100ppm — meaning it gains or loses 10–100 microseconds per second. Over an hour, this accumulates to 36–360ms of drift without re-synchronization.

**Clock Skew** is the absolute difference between two clocks at any given moment in real time. Skew = ∫ drift_difference dt. Two identically-drifting clocks can have significant skew if they started from different initial values or have brief rates of drift differential.

**NTP (Network Time Protocol):** compensates for skew by periodically syncing to time servers, achieving within-millisecond accuracy on LAN (typically 0.1–10ms on WAN). NTP uses a hierarchy of servers (stratum 0 = atomic clock, stratum 1 = NTP server directly connected to stratum 0, etc.).

**Monotonic clock vs wall clock:** OS provides two types — `CLOCK_REALTIME` (wall clock, can jump backward on NTP adjustment) and `CLOCK_MONOTONIC` (monotonic, always increases, but local to one machine and can't be compared across machines).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Clock drift = your machine's clock slowly becomes inaccurate; clock skew = the difference between two machines' clocks at the same moment.

**One analogy:**
> Two wristwatches set to the same time diverge over weeks. After a month, your watch says 3:00:05pm and your friend's says 2:59:55pm — a 10-second skew. Your watch drifted forward at 16 microseconds/second; your friend's drifted backward at 5 μs/s. In a distributed system, this same drift/skew happens at millisecond scale, and it invalidates any protocol assuming "Server A and Server B agree on what time it is."

---

### 🔩 First Principles Explanation

```
THE PHYSICS OF CLOCK DRIFT:

  Hardware clock: quartz crystal oscillator
  Frequency: ~32,768 Hz (32.768 kHz) for low-power clocks
              ~10 MHz for precision clocks
  
  Drift: temperature affects crystal oscillation frequency
    +/- 5°C → ~10ppm drift
    Typical server room: ±1°C → ~1ppm drift
    1ppm = 1 microsecond per second = 86ms per day
    Without NTP: days accumulate to seconds of skew
  
  NTP CORRECTION CYCLE:
    1. Client queries NTP servers (typically 4 servers)
    2. NTP measures Round-Trip Time (RTT) to each server
    3. NTP estimates one-way delay = RTT/2 (assumes symmetric path)
    4. NTP adjusts local clock by calculated offset
    5. Adjustment is gradual ("slewing") to avoid backward jumps: max 500ppm rate
    
    Problem 1: RTT asymmetry — network paths are not always symmetric
               If client→server = 5ms and server→client = 15ms (asymmetric)
               NTP assumes 10ms each way → 5ms error in time estimate
    
    Problem 2: Step vs slew — large corrections (> 128ms) cause "step" adjustment
               → clock jumps backward → CLOCK_REALTIME goes backward → bugs!
    
  NTP ACCURACY CHARACTERISTICS:
  Datacenter (LAN, GPS-synced stratum 1): ~0.1ms skew
  Single datacenter (NTP with several hops): ~1-5ms skew
  Cloud inter-region (WAN NTP): ~10-100ms skew
  Without NTP (isolated machine): seconds to minutes per day drift
```

---

### 🧪 Thought Experiment

**SCENARIO:** Distributed rate limiter using Redis with timestamp-based sliding window.

```
SETUP:
  Redis server in us-east-1 with NTP-synced clock
  API Gateway server in us-west-2 with its own NTP-synced clock
  API Gateway clock is 20ms ahead of Redis clock due to NTP skew

  Rate limit window: 1 second, max 100 requests

  At T=999ms (API Gateway clock), Gateway sends request 101 to rate limiter.
  Rate limiter (Redis clock T=979ms): window for T=979ms-T=1979ms checks count.
  Last window (T=-21ms to T=979ms): only 100 requests (limit hit at apparent T=979ms)
  Gateway clock says T=999ms → in a "new" 1s window → sends request.
  
  Redis: "Your window is 979ms–1979ms; I see 0 in this window → allow."
  Gateway: "My previous 100 requests are in window 979-1999ms → but Redis sees new window."
  
  Result: Extra requests allowed → rate limit partially defeated by 20ms clock skew.
  
  At scale: 20ms × 10,000 req/s = 200 requests that bypass the rate limit per second
  For a payment API: significant financial risk.

  Solution: Use Redis CLOCK (not client clock) for all window calculations
  OR: Use logical time (Lamport), not physical time for rate limiting windows
```

---

### 🧠 Mental Model / Analogy

> Clock skew in distributed systems is like baking a soufflé with multiple ovens. All ovens are set to 200°C but some run slightly hotter, some slightly cooler. If you rely on "the recipe says 45 minutes at 200°C" and all ovens finish simultaneously — you'll have uneven results. A good baker takes each oven's actual temperature into account. Distributed systems that rely on "all clocks show the same time" are the baker who ignores oven variation.
> 
> The fix: either synchronize ovens precisely (GPS/atomic clock), or use cooking-done signals (logical clocks, heartbeats) instead of timers.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Every server's clock drifts slightly. Over time, servers have different times (skew). Never sort distributed events by wall-clock timestamp alone — the "earlier" timestamp might be on a server with a faster clock. Use logical clocks (Lamport) for event ordering, or NTP to keep skew small enough to tolerate.

**Level 2:** NTP reduces but doesn't eliminate skew. Typical NTP accuracy in a well-managed datacenter: ±1–5ms. For most applications, this is fine. For high-frequency trading, real-time bidding, or systems where 1ms skew causes correctness issues: use GPS-disciplined clocks (μs accuracy) or hardware-assisted time synchronization (AWS Time Sync Service with Chrony: ±100μs; Google TrueTime: ±7ms bounded uncertainty).

**Level 3:** The most dangerous clock behavior: the NTP "step" correction (when a clock jumps backward). Code that assumes monotonic time fails: a 5-second lease that started at T=100 expires at T=105. If the clock jumps backward to T=103 after the lease expires: the lease appears still valid. Java's `System.currentTimeMillis()` uses wall clock → can jump backward. `System.nanoTime()` uses monotonic clock → never jumps backward, but only valid within a single JVM. For distributed lease management, always use monotonic time + explicit heartbeat, not wall clock alone.

**Level 4:** Google Spanner's TrueTime API addresses clock skew with bounded uncertainty: instead of returning a single timestamp, it returns an interval [earliest, latest] within which the true time is guaranteed to lie. The interval width (2ε) is bounded at ~7ms on Google's infrastructure. Spanner's "commit wait" protocol: after a transaction commits at timestamp T, Spanner waits until TrueTime.now().earliest > T before returning to the client. This guarantees any future transaction sees time > T, providing external consistency. This is the only production system that achieves linearizability + global serializability at planetary scale — made possible by bounded clock uncertainty, not perfect synchronization.

---

### ⚙️ How It Works (Mechanism)

```
MEASURING CLOCK SKEW (practical):

  TOOL: chronyc tracking
  System clock: 2024-01-15 10:00:00
  Reference Time: GPS stratum 1 server
  System time offset: +0.000234567 seconds   → 234μs skew
  Frequency error: +1.234 ppm                → drift rate
  RMS offset: 0.000421234 seconds             → sustained error
  
  AWS CLOCK SYNC SERVICE (using Chrony + Amazon Time Sync):
  Accuracy: < 100μs in the same region
  Uses local hardware clock signal, not NTP over internet
  
  CHECK SKEW BETWEEN TWO HOSTS:
  Host A: python3 -c "import time; print(time.time())"  → 1705310400.1234567
  Host B: python3 -c "import time; print(time.time())"  → 1705310400.1191234
  Difference: 43ms → clock skew between these two hosts
  
  JAVA: use System.nanoTime() for duration measurement (monotonic):
  long start = System.nanoTime();
  doWork();
  long elapsedNs = System.nanoTime() - start;  ← correct, monotonic
  
  WRONG: use System.currentTimeMillis() for duration (can jump backward):
  long start = System.currentTimeMillis();
  doWork();
  long elapsed = System.currentTimeMillis() - start;  ← can be NEGATIVE if NTP adjusts clock!
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
DISTRIBUTED LEASE WITH CLOCK SKEW PROTECTION:

  PROBLEM: Leader holds lease for 10 seconds. Follower detects leader failure
  and wants to start a new election only after lease has expired.
  
  NAIVE (buggy): Follower tracks wall-clock time of lease grant + 10 seconds.
  If follower's clock is 5s ahead: thinks lease expired 5s early → false election.
  
  CORRECT (heartbeat-based):
  1. Leader sends heartbeats every 1 second
  2. Follower tracks: "last heartbeat received at my monotonic clock time T"
  3. Election timeout: "if no heartbeat for 2× clock uncertainty (e.g., 10s worst case)"
  4. Uncertainty: local monotonic clock drift is bounded per machine → O(ms) per minute
  
  SPANNER-STYLE (if you have TrueTime):
  Lease granted at TT.now() = [T₁_earliest, T₁_latest]
  Lease duration = 10 seconds
  Lease expires at T = T₁_latest + 10 (conservative: use LATEST bound for grant)
  Follower waits until TT.now().earliest > T₁_latest + 10 before stealing lease
  → Even with bounded uncertainty, lease is always expired before follower acts
```

---

### 💻 Code Example

```java
// WRONG: using wall clock for distributed event ordering
@Service
public class EventOrderingWrong {
    public long generateEventTimestamp() {
        return System.currentTimeMillis(); // ← WRONG: can go backward, has skew across nodes
    }
    
    public boolean eventABeforeEventB(long tsA, long tsB) {
        return tsA < tsB; // ← WRONG: if nodes have different clocks, this is unreliable
    }
}

// CORRECT: monotonic clock for local duration, logical clock for ordering
@Service
public class EventOrderingCorrect {
    
    private final LamportClock lamportClock; // logical clock (previous keyword)
    
    // For distributed event ordering: use logical clocks
    public long generateLogicalTimestamp() {
        return lamportClock.tick().timestamp(); // logical, not physical time
    }
    
    // For local duration measurement: use monotonic clock
    public long measureOperationDurationNs(Runnable operation) {
        long startNs = System.nanoTime();   // monotonic, local-only, never goes backward
        operation.run();
        return System.nanoTime() - startNs; // always non-negative ✓
    }
    
    // For lease management: conservative approach assuming max NTP skew
    public Instant conservativeLeaseExpiry(Instant grantTime, Duration leaseDuration) {
        // Add NTP skew budget (assume worst-case 5ms skew between nodes)
        Duration ntpUncertainty = Duration.ofMillis(5);
        // Expire the lease slightly later to account for skew
        // (clock might be faster than actual by ntpUncertainty)
        return grantTime.plus(leaseDuration).plus(ntpUncertainty);
    }
}
```

---

### ⚖️ Comparison Table

| Synchronization Method | Accuracy | Cost | Use Case |
|---|---|---|---|
| **No sync (raw quartz)** | Seconds/day | Zero | Air-gapped single machines |
| **NTP (internet)** | 1–100ms | Minimal | General distributed systems |
| **NTP (datacenter LAN)** | 0.1–5ms | Minimal | Most cloud workloads |
| **PTP (IEEE 1588)** | 1–100μs | Hardware requirement | Financial, HFT |
| **GPS-disciplined oscillator** | 10–100ns | Expensive hardware | Telecom, specialized |
| **Google TrueTime** | ±3.5ms bound | Google infrastructure | Spanner, internal Google |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| NTP eliminates clock skew | NTP reduces skew to ±1–10ms on LAN. It does not eliminate it. Any protocol that requires exactly synchronized clocks (not just "approximately") must account for residual skew |
| `System.currentTimeMillis()` is safe for local durations | It uses CLOCK_REALTIME which can go backward on NTP adjustment. Use `System.nanoTime()` for local duration measurement |
| Clock skew only matters for databases | It affects distributed locks (lease expiry), rate limiters (window boundaries), authentication (JWT exp validation), log correlation, ordered event processing — nearly every distributed protocol |

---

### 🚨 Failure Modes & Diagnosis

**NTP Step Correction Causing Distributed Lock Bug**

```
Symptom:
After a maintenance window (NTP re-synchronization), some worker processes
report "lock already expired" and start competing for the same lock simultaneously.

Root Cause:
NTP "step" correction jumped clock backward by 500ms.
Lock expiry "time = acquired_at + lease_duration" was calculated using pre-step time.
After step, acquired_at is now in the future → lease appears expired → lock released.

Detection:
  journalctl -u ntpd | grep -E "step|offset" | tail -20
  sudo ntpq -p → review offset column
  dmesg | grep -i "time: clock jump"

Fix 1: Use monotonic clock for lease timers
  long leaseStartNs = System.nanoTime();
  boolean isExpired = (System.nanoTime() - leaseStartNs) > leaseNs;  ← nanoTime is monotonic

Fix 2: Use chrony in "makestep" limited mode:
  # /etc/chrony.conf — only allow backward step once at startup, then slew:
  makestep 1.0 3   ← allow step > 1s during first 3 clock updates, then slew only

Fix 3: Use TrueTime-aware lease protocol (wait for TT.now.earliest > expiry before re-acquiring)
```

---

### 🔗 Related Keywords

- `Lamport Clock` — logical clock that bypasses the physical clock skew problem
- `Vector Clock` — causal clock that also avoids dependency on physical time
- `Linearizability` — requires real-time ordering, making clock accuracy critical
- `Raft` — uses election timeouts that must account for clock skew between nodes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ DRIFT         │ Clock frequency deviation (ppm) — HW issue  │
│ SKEW          │ Difference between two clocks at a moment   │
├───────────────┼─────────────────────────────────────────────┤
│ NTP ACCURACY  │ LAN: ±0.1-5ms; WAN: ±10-100ms              │
├───────────────┼─────────────────────────────────────────────┤
│ DANGER        │ Wall clock can go BACKWARD (NTP step)       │
│               │ CLOCK_MONOTONIC safe for local duration     │
├───────────────┼─────────────────────────────────────────────┤
│ JAVA          │ System.nanoTime() = monotonic (duration OK) │
│               │ System.currentTimeMillis() = can jump back  │
├───────────────┼─────────────────────────────────────────────┤
│ SOLUTION      │ Logical clocks for ordering; tolerate skew  │
│               │ in protocols; TrueTime for bounded guaranty │
└───────────────┴─────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A Java service generates "unique" IDs using `System.currentTimeMillis() + random4digits`. During a deploy, NTP steps the server clock backward by 200ms. The ID generator starts producing IDs that are numerically lower than IDs generated before the step. A downstream consumer sorts IDs numerically, assuming monotonic increase. Identify: (1) how many IDs could be "duplicated" or out-of-order (given 50K req/s during the 200ms backward step), (2) how this affects downstream database inserts (primary key conflict), (3) how `System.nanoTime()` would or wouldn't fix this, and (4) design an ID generation scheme that is globally unique, monotonically increasing, and survives clock steps.
