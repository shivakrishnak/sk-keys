---
layout: default
title: "Clock Skew / Clock Drift"
parent: "Distributed Systems"
nav_order: 582
permalink: /distributed-systems/clock-skew-clock-drift/
number: "0582"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Systems, Lamport Clock, Networking, Operating Systems
used_by: Lamport Clock, Vector Clock, Distributed Locking, Fencing / Epoch
related: Lamport Clock, NTP, Fencing / Epoch, Distributed Locking, TrueTime
tags:
  - distributed
  - networking
  - reliability
  - deep-dive
  - production
---

# 582 — Clock Skew / Clock Drift

⚡ TL;DR — Clock skew is the instantaneous difference in time between two clocks; clock drift is the rate at which that difference grows — and both are unavoidable in distributed systems, making wall-clock timestamps unreliable for ordering events.

| #582            | Category: Distributed Systems                                      | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Systems, Lamport Clock, Networking, Operating Systems  |                 |
| **Used by:**    | Lamport Clock, Vector Clock, Distributed Locking, Fencing / Epoch  |                 |
| **Related:**    | Lamport Clock, NTP, Fencing / Epoch, Distributed Locking, TrueTime |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed database decides "latest write wins" by comparing wall-clock timestamps from each server. Server A writes record R at `10:00:00.005` (its local clock). Server B writes the same record at `10:00:00.001` (its local clock). The system picks Server B's write as "later" and discards A's. But Server B's clock is 10ms behind Server A's — in physical reality, A's write came after B's. A customer's most recent address update is silently discarded. They receive deliveries to their old address for months before anyone notices.

**THE BREAKING POINT:**
Every computer's hardware clock drifts at a different rate — typically 10–200 ppm (parts per million), which means 10–200ms per second of drift. Over an hour without re-synchronisation a clock can be seconds off. NTP re-synchronises clocks periodically but introduces its own problems: a step correction can make a clock JUMP BACKWARD — causing `now < last_event_time`, breaking any system that assumes monotonically increasing timestamps.

**THE INVENTION MOMENT:**
This is why logical clocks (Lamport, vector) were invented — to provide ordering guarantees without trusting physical time. And it's why systems like Google Spanner invented TrueTime: GPS-atomic-clock-backed infrastructure that can guarantee clock accuracy within ±7ms with explicit uncertainty bounds, letting the database wait out the uncertainty window before committing.

---

### 📘 Textbook Definition

**Clock Skew** is the instantaneous difference between the time reported by two clocks at the same physical moment: `skew = clock_A(t) - clock_B(t)`. **Clock Drift** is the relative rate at which a clock's frequency deviates from a reference standard, measured in parts per million (ppm). A 100 ppm drift causes a 100ms/1000s ≈ 8.64s/day of skew accumulation. NTP (Network Time Protocol) corrects drift and skew by periodically slewing the clock (gradually speeding up or slowing down) or, for large errors, stepping it. **Clock Monotonicity** separates the clock into two views: wall-clock time (synchronised, may jump) and monotonic time (never goes backward, unsuitable for comparing across machines). Distributed systems safety requires assuming worst-case bounds on skew and designing algorithms that remain correct within those bounds.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every clock in a distributed system is slightly wrong, and "slightly wrong" is enough to corrupt any system that trusts timestamps for ordering.

**One analogy:**

> Imagine 100 referees each timing a 100m race with their own stopwatch. Even if everyone starts at the same signal, by the end of the race some watches show 9.87s and others show 9.85s — all watches drifted differently. If you pick the winner by whose stopwatch shows the earliest time, you'll sometimes pick the wrong runner. Now imagine the stakes are distributed database commits rather than a race result.

**One insight:**
The truly dangerous property of clock skew is that it's invisible from inside any single machine. A server with a drifted clock doesn't know it's wrong — it just reports its own time. Only comparison with an external reference reveals the error. This is why distributed systems must either use logical clocks (which side-step the problem) or assume bounded skew and build in explicit wait windows (as Spanner does).

---

### 🔩 First Principles Explanation

**TYPES OF CLOCK ERROR:**

```
┌──────────────────────────────────────────────────────────┐
│            Clock Error Taxonomy                          │
├──────────────────┬───────────────────────────────────────┤
│ Clock drift      │ Crystal oscillator runs at slightly   │
│                  │ off frequency (±100 ppm typical)      │
│                  │ Causes: temperature, age, vibration   │
├──────────────────┼───────────────────────────────────────┤
│ Clock skew       │ Instantaneous offset between two      │
│                  │ clocks at same real-world moment      │
│                  │ Accumulates from drift over time      │
├──────────────────┼───────────────────────────────────────┤
│ NTP step         │ Large backward/forward jump to correct│
│                  │ accumulated skew (dangerous for       │
│                  │ systems assuming monotonic time)      │
├──────────────────┼───────────────────────────────────────┤
│ NTP slew         │ Gradual speed-up/slow-down to correct │
│                  │ small skew without backward jump      │
│                  │ (safe but slow — max ±500ppm adjust.) │
├──────────────────┼───────────────────────────────────────┤
│ Network delay    │ NTP synchronisation accuracy limited  │
│                  │ by round-trip time uncertainty        │
│                  │ ~1ms LAN, ~50ms WAN                   │
└──────────────────┴───────────────────────────────────────┘
```

**PRACTICAL SKEW BOUNDS:**

- LAN with NTP: ±1ms typical, ±10ms worst case
- WAN with NTP: ±50ms typical, ±500ms worst case
- GPS-disciplined (PTP/TrueTime): ±100μs to ±7ms
- No synchronisation: unbounded

**THE MONOTONIC CLOCK SPLIT (Java/Linux):**

```java
// Wall-clock time — synchronised, may go backward:
System.currentTimeMillis()  //  can jump on NTP correction
Instant.now()               //  same — wall clock

// Monotonic time — never backward, but NOT comparable across machines:
System.nanoTime()           //  monotonically increasing, local only
ProcessHandle.current().info().startInstant()  // internal reference

// Rule: Use monotonic for measuring ELAPSED TIME on one machine
//       Use wall clock for timestamps in distributed contexts
//       NEVER compare System.nanoTime() across different JVMs
```

**GOOGLE SPANNER'S TRUETIME SOLUTION:**

```
TrueTime reports time as an interval: [earliest, latest]
where the true time is guaranteed to be within this interval.

TrueTime.now() → TT.Interval{earliest=T-ε, latest=T+ε}
where ε ≤ 7ms (bounded by GPS/atomic clock infrastructure + network)

Spanner uses "commit wait":
  1. Assign commit timestamp s = TT.now().latest
  2. Wait until TT.now().earliest > s  (wait out the uncertainty)
  3. Now: all clocks in the world have passed s → globally ordered

Cost: ≤7ms commit latency to buy external consistency (linearizability)
      without logical clocks or coordination protocols
```

---

### 🧪 Thought Experiment

**SETUP:**
A distributed lock implemented with timestamps: "whoever holds a lock with a later
timestamp wins." Server A holds lock with timestamp T=100. A suffers a GC pause
for 15ms. During the pause, the lock expires. Server B acquires the lock with
timestamp T=105. Server A resumes, clock shows T=98 (NTP backward correction
during pause). A thinks it still holds the lock. A writes to the locked resource.
B also writes to the locked resource. CORRUPTION.

**THIS IS THE CLOCK SKEW + GC PAUSE PROBLEM:**
Kyle Kingsbury (Jepsen) documented this exact failure mode in Redis Redlock.
Even with NTP, GC pauses + clock corrections create windows where two nodes
believe they hold the same lock simultaneously.

**THE SOLUTION — FENCING TOKENS:**
Instead of trusting timestamps, issue a monotonically-increasing fencing token
when a lock is granted. Each write to the protected resource includes the token.
The resource rejects any write with a token lower than the highest seen.
Server A's stale token (100) is rejected because B's write already used token 105.
Physical time is completely eliminated from the correctness argument.

---

### 🧠 Mental Model / Analogy

> Clock skew in distributed systems is like trying to coordinate a global
> relay race using participants' own phones as timers. Some phones' batteries
> are nearly dead and the system is throttling CPU (slower clock). Some
> phones just synced to a time server. Some haven't synced in days. The
> only safe strategy: don't use the phone timers to determine race order —
> use a baton hand-off sequence number (the fencing token) instead.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Every computer's clock drifts and may be set to a slightly different time than every other computer. In distributed systems, you can't trust one server's clock to correctly judge whether an event on another server happened before or after.

**Level 2:** Clock drift causes skew that accumulates over time. NTP corrects it — but NTP corrections can jump clocks backward. Safe practice: use wall-clock time for human-readable logs, but use logical clocks (Lamport/vector) or fencing tokens for correctness-critical ordering in distributed algorithms.

**Level 3:** The two failure modes to guard against: (1) skew-based false ordering — system believes event A (ts=100, server behind) came before event B (ts=99, server ahead) when physically A came after B; (2) NTP step backward — a monotonic invariant is violated, breaks any system that assumes `now > last_event`. Use `CLOCK_MONOTONIC` for elapsed-time measurement on a single host; use external coordination (Paxos/Raft/fencing tokens) for distributed ordering.

**Level 4:** Google Spanner's TrueTime is the only production system to exploit bounded physical clock uncertainty to achieve external consistency without logical clocks. By explicitly modelling time as an interval `[T-ε, T+ε]` and committing-wait until the interval passes, Spanner serialises transactions globally with physical time. This is safe because the GPS+atomic clock infrastructure guarantees ε ≤ 7ms. All other databases (CockroachDB, YugabyteDB) use hybrid logical clocks to achieve similar ordering semantics without GPS hardware, accepting a slightly wider uncertainty window by combining physical and logical components.

---

### ⚙️ How It Works (Mechanism)

**Measuring Skew (Linux/NTP):**

```bash
# Check NTP synchronisation status:
timedatectl status
# Look for: "NTP synchronized: yes" and "System clock synchronized: yes"

# Check offset/drift tracked by chronyd:
chronyc tracking
# Key fields:
#   System time offset: current skew vs NTP server
#   RMS offset: recent average skew
#   Frequency error: drift rate in ppm

# Check node-to-node skew (rough):
ssh server-b "date +%s%N" && date +%s%N
# Compare nanosecond timestamps — difference is approximate skew
```

**Safe Timestamp Pattern in Java:**

```java
// SAFE: wall clock for log correlation, monotonic for measurement
public class SafeClock {
    private final long referenceWall = System.currentTimeMillis();
    private final long referenceNano = System.nanoTime();

    // Locally monotonic wall-clock estimate (never backward on this JVM)
    public long monotonicMillis() {
        long elapsed = (System.nanoTime() - referenceNano) / 1_000_000;
        return referenceWall + elapsed;
    }
}
```

---

### ⚖️ Comparison Table

| Approach                | Ordering Guarantee   | Clock Dependency | Latency          | Use Case                          |
| ----------------------- | -------------------- | ---------------- | ---------------- | --------------------------------- |
| Wall clock (raw)        | None (unreliable)    | Physical clock   | Zero             | Human logs only                   |
| Logical clock (Lamport) | Causal (partial)     | None             | Zero             | Total order without physical time |
| Vector clock            | Causal (exact)       | None             | Zero             | Concurrency detection             |
| Fencing token           | Sequential           | None             | Zero             | Distributed locks, leases         |
| TrueTime (Spanner)      | External consistency | GPS/atomic clock | ≤7ms commit wait | Global transactions               |
| HLC                     | Causal + physical    | NTP              | Zero extra       | CockroachDB, YugabyteDB           |

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                       |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| NTP makes clocks identical                             | NTP corrects clocks to within ±1–50ms depending on network latency — far from identical                       |
| Monotonic clocks prevent ordering bugs across machines | Monotonic clocks are per-process — they cannot be compared across different machines                          |
| High-precision hardware eliminates the problem         | Even atomic clocks drift and have bounded uncertainty; Spanner models this explicitly with TrueTime           |
| Cloud VMs have more reliable clocks than bare metal    | VMs are worse — hypervisor interrupts cause clock stalls; AWS/GCP compensate with PTP but uncertainty remains |

---

### 🚨 Failure Modes & Diagnosis

**Backward Time Jump Breaks Application Logic**

Symptom: Application logs show timestamp going from 10:00:05.000 to 10:00:04.987;
"created_at > updated_at" database constraints violated; scheduled jobs fire twice.

Cause: NTP step correction backward to sync with time server.

Fix: Use `CLOCK_MONOTONIC` (Java: `System.nanoTime()`) for all elapsed time
measurements. For database timestamps, use `clock_timestamp()` with awareness it
can drift; for sequencing, use a logical counter or Postgres' `txid_current()`.

Diagnosis:

```bash
# Check for time jumps in recent system logs:
journalctl -u chronyd | grep -E "stepped|offset"
dmesg | grep "time set"
```

---

### 🔗 Related Keywords

- `Lamport Clock` — logical clock designed specifically to bypass physical clock unreliability
- `Fencing / Epoch` — token-based solution that replaces timestamp-based distributed lock safety
- `Distributed Locking` — application-level pattern severely affected by clock skew
- `Vector Clock` — another logical clock approach that avoids physical time entirely

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  SKEW:    offset between two clocks at same real moment  │
│  DRIFT:   rate of offset accumulation (ppm)              │
│  NTP:     corrects to ±1ms LAN, ±50ms WAN — can go BACK  │
│  SAFE:    use logical clocks for ordering (no physical t) │
│  SAFE:    use fencing tokens for distributed locks        │
│  UNSAFE:  wall-clock timestamp as distributed lock token  │
│  SPANNER: TrueTime — bounded ε, commit-wait → safe       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed cache uses Redis with `SET NX` to implement distributed locking.
The lock's expiry is set to 10 seconds to prevent deadlock. A client holds the lock
and enters a GC pause for 12 seconds. During the pause, the lock expires and another
client acquires it. When the first client resumes, what check must it perform before
writing to the protected resource, and why is checking Redis "do I still hold the lock?"
insufficient for safety? What mechanism provides an ironclad safety guarantee?

**Q2.** Google Spanner uses TrueTime's `[T-ε, T+ε]` uncertainty window and commit-wait
to achieve external consistency. If ε = 7ms, calculate the minimum commit latency
Spanner must add per transaction. Now design a simplified "poor man's TrueTime":
using only NTP (±50ms uncertainty), what commit-wait duration would you need, and
is this latency acceptable for a transactional database used for e-commerce checkout?
