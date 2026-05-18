---
id: DST-063
title: Lease-Based Coordination
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-046, DST-049, DST-052
used_by: DST-066
related: DST-046, DST-047, DST-049, DST-062
tags:
  - distributed
  - leases
  - coordination
  - leader-lease
  - zookeeper
  - etcd
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 63
permalink: /technical-mastery/distributed-systems/lease-based-coordination/
---

⚡ TL;DR - A lease is a time-limited grant of a right
(leadership, resource ownership, cache authority)
that expires automatically if not renewed; leases
are fundamental to distributed coordination because
they provide a bounded guarantee without requiring
consensus on every operation; the key risk is clock
skew causing lease overlap (two holders believe the
lease is theirs simultaneously).

---

### 📋 Entry Metadata

| #063 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Leader Election, Distributed Locking, Hybrid Logical Clocks | |
| **Used by:** | Spanner and TrueTime | |
| **Related:** | Leader Election, Fencing Tokens, Distributed Locking, Raft Internals | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed database has one writer (leader).
The leader must process every operation through
consensus (AppendEntries + quorum acknowledge).
For read operations: the leader must also confirm
it is still the leader before serving reads (via
read-index procedure: send heartbeat, wait for quorum
confirm). Every read = a network round trip to
quorum. Throughput: limited by consensus latency.

Leases provide a shortcut: after winning an election,
the leader is granted a lease for duration D. During
the lease period, it KNOWS it is the leader without
asking anyone. Reads can be served directly. Write
throughput is unchanged; read throughput scales
with the node, not the consensus latency.

---

### 📘 Textbook Definition

A **lease** is a time-bounded exclusive right granted
by a lessor (typically a consensus system or a
primary server) to a lessee (a node). The lessee
holds the right until the lease expires or is
explicitly revoked.

**Key property:** The lessor guarantees that no
conflicting lease is granted until the current
lease expires. This creates a bounded window of
exclusivity that requires no communication to
maintain within the window.

**Types:**
- **Leader lease:** leader can serve reads without
  read-index during the lease period
- **Cache lease:** cache entry is valid for the
  lease duration; no validation needed
- **Lock lease:** distributed lock with automatic
  expiry if holder crashes

---

### ⏱️ Understand It in 30 Seconds

```
LEASE PROTOCOL:

GRANT:  At time T, leader wins election.
        Followers will not vote for anyone for
        min_election_timeout (e.g., 150ms).
        Leader's lease: valid from T to T+150ms.
        
SERVE:  During lease: leader serves reads directly.
        No heartbeat needed. Lease guarantees: no
        other leader can exist during [T, T+150ms].

RENEW:  Successful heartbeat at T+100ms resets
        followers' election timers.
        Leader's new lease: valid until T+250ms.

EXPIRE: If no renewal by T+150ms: lease expires.
        Leader stops serving reads.
        Followers may start new election.

RISK:   If leader's clock runs FAST:
        Leader believes lease ends at T+150ms.
        Follower's clock (running slow) hasn't ticked
        to T+100ms yet - they haven't started new
        election. But leader thinks lease expired
        100ms earlier than followers do.
        OR VICE VERSA: leader believes lease valid
        past when followers would start election.
        
        This is why: lease_duration < election_timeout -
          max_clock_skew
```

---

### 🔩 First Principles Explanation

**LEASE MATHEMATICS:**

```
SAFE LEASE DURATION:

Variables:
  T_election: election timeout (followers wait this
               long without heartbeat before election)
  ε:          maximum clock skew between any two nodes

SAFE LEASE:
  lease_duration ≤ T_election - ε

WHY:
  Scenario: Leader L granted lease at real time 0.
  Follower F's clock: εms ahead of L's clock.
  
  At real time T_election - ε:
    L's clock shows: T_election - ε (lease: valid)
    F's clock shows: T_election (timer expired!)
    F starts election → new leader possible.
    
  If L served read at T_election - ε:
    New leader M might have been elected.
    M may have accepted writes.
    L's read is now STALE (safety violation!).
  
  SAFE LEASE = T_election - ε:
    At L's clock time T_election - ε, F's clock
    shows T_election - ε + ε = T_election.
    F's timer expires exactly now.
    Before F starts election, L has ended the lease.
    No window of two simultaneous leaders.

EXAMPLE:
  T_election = 150ms
  ε = 10ms (max NTP skew)
  Safe lease: 140ms
  CockroachDB: uses 500ms election timeout,
               500ms max clock skew, lease = 0ms
               (must use read-index instead!)
  Spanner: uses TrueTime (7ms skew), longer lease OK.
```

**ETCD LEADER LEASE:**

```
etcd uses leases for both leader reads and
key-value object TTLs.

ETCD LEADER LEASE (READ OPTIMIZATION):
  After winning election (term T):
  1. Leader records election time.
  2. For duration = election_timeout - 2*max_clock_skew:
     Serve reads without round-trip to followers.
     (etcd actually uses read-index by default;
     lease-based reads are an optimization when
     clock skew is bounded)
  3. Reset timer on each successful heartbeat.

ETCD KV LEASE (TTL FOR KEYS):
  etcd supports attaching a lease (TTL) to any key.
  Key is automatically deleted when lease expires.
  Clients must renew the lease (KeepAlive RPC) to
  keep the key alive.
  
  Use case: service registration.
  Service registers itself with a 10-second lease.
  Service sends KeepAlive every 3 seconds.
  If service crashes: lease expires in 10 seconds.
  Other services detect deregistration.
```

**CHUBBY'S LEASE MODEL (Google):**

```
Google Chubby (internal lock service):
  Uses leases for two purposes:
  
1. MASTER LEASE:
   Paxos master (leader) is granted a lease.
   Clients can read from master without going through
   Paxos for reads. Master lease = read optimization.
   
2. SESSION LEASE:
   Clients hold session leases with Chubby.
   If client fails to renew lease: session expires.
   All locks held by the client are released.
   Other clients can acquire those locks.
   This is the "jeopardy" state: client in jeopardy
   of losing its lease.
   Client must stop operations and wait for grace period.
   
   GRACE PERIOD: When lease approaches expiry but
   Chubby is unreachable (network issue):
   Client enters grace period.
   Client MUST NOT use its locks during grace period
   (lease might have already expired on Chubby's side).
   If Chubby comes back and renews: client continues.
   If grace period expires: client terminates itself.
```

**ZooKeeper EPHEMERAL NODES AS LEASES:**

```python
# ZooKeeper: ephemeral nodes as implicit leases
# Ephemeral node exists only while session is active.
# Session maintained via heartbeat (ZK calls it "ping").
# If client disconnects and session expires (timeout):
# All ephemeral nodes created by that session are deleted.

import kazoo.client as kazoo

def register_service_with_lease(
    zk: kazoo.KazooClient,
    service_name: str,
    host: str,
    port: int
) -> str:
    """
    Register service using ephemeral node (implicit lease).
    Node exists as long as this client's session is alive.
    """
    path = f"/services/{service_name}/{host}:{port}"
    
    # EPHEMERAL: auto-deleted when session expires
    node_path = zk.create(
        path,
        value=f'{{"host":"{host}","port":{port}}}'.encode(),
        ephemeral=True,  # Lease = session lifetime
        makepath=True
    )
    # ZK sends ping every session_timeout/3 ms.
    # If application crashes: pings stop.
    # ZK detects: session_timeout passes.
    # ZK deletes ephemeral node.
    # Other services get watch event: service gone.
    return node_path

def watch_service(zk, service_name: str) -> None:
    """Monitor service registrations."""
    @zk.ChildrenWatch(f"/services/{service_name}")
    def watch_fn(children):
        print(f"Active instances: {children}")
        # Called when instances register or deregister.
        # Deregister happens when lease (session) expires.
```

---

### 🧠 Mental Model / Analogy

> A lease is like a library book checkout. The
> library (lessor) grants you exclusive use for 2 weeks
> (lease duration). During those 2 weeks: you have the
> book; no one else can have it; you don't need to call
> the library to confirm you still have it. The library
> trusts you do until the lease expires. If you don't
> return it at 2 weeks: you're charged (lease expired,
> lock released; another client can acquire it).
> Clock skew is like: your lease says "return by Friday
> 5pm." But your clock shows 4:50pm while the library's
> clock shows 5:05pm (they've already given it to
> someone else). You still think you have the book
> (lease is "valid" on your clock), but you don't.
> This is the lease safety hazard.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What a lease is:**
A time-limited exclusive right. "I own this resource
for the next T seconds; no one else can own it during
that window; I don't need to check with anyone during
the window."

**Level 2 - Why leases are useful:**
Reduces coordination overhead. Without leases: every
operation requires at least one round-trip to a
consensus system (etcd/Zookeeper). With leases:
after acquiring a lease, operations are local until
the lease expires. Significant throughput improvement.

**Level 3 - Clock skew is the fundamental risk:**
Leases depend on clocks. If node A's clock is faster
than expected, it may believe its lease has not
expired when it actually has. Two nodes can
simultaneously believe they hold a lease. The
safety margin (lease_duration < election_timeout - skew)
ensures this cannot happen.

**Level 4 - Jeopardy and grace periods:**
When a leaseholder cannot contact the lessor, it
enters jeopardy: it doesn't know if its lease has
been renewed or revoked. Safe behavior: stop using
the lease (stop serving reads, stop performing
privileged operations) until lease is either
renewed or known to have expired. This is the
Chubby "jeopardy" state.

**Level 5 - Spanner's TrueTime enables tighter leases:**
Spanner uses GPS and atomic clocks to bound clock
uncertainty to ±7ms. With ε=7ms, leases can be
much tighter: lease_duration = election_timeout - 14ms.
This enables Spanner's leader to serve reads without
consensus during the lease period, achieving
~millisecond read latency for single-row operations
at global scale.

---

### 💻 Code Example

**Lease with Clock Skew Safety**

```python
# BAD: Lease without clock skew safety margin
# (two nodes may simultaneously hold the lease)

import time

class BadLease:
    def __init__(self, duration_ms: float):
        self.duration_ms = duration_ms
        self.granted_at: float = time.time() * 1000

    def is_valid(self) -> bool:
        # BAD: No safety margin for clock skew
        elapsed = time.time() * 1000 - self.granted_at
        return elapsed < self.duration_ms
        # If our clock is fast: we might think
        # lease is valid after it has expired on the
        # lessor's clock. Race condition possible.
```

```python
# GOOD: Lease with clock skew safety margin

class SafeLease:
    def __init__(
        self,
        duration_ms: float,
        max_clock_skew_ms: float,
        safety_margin_multiplier: float = 2.0
    ):
        # Reduce effective duration by (safety_margin * skew)
        # to ensure no overlap with next possible grant:
        self.effective_duration_ms = (
            duration_ms
            - safety_margin_multiplier * max_clock_skew_ms
        )
        if self.effective_duration_ms <= 0:
            raise ValueError(
                f"Clock skew {max_clock_skew_ms}ms too high "
                f"for lease duration {duration_ms}ms. "
                f"Must have: duration > {safety_margin_multiplier}x skew."
            )
        self.granted_at_ms: float | None = None
        self.max_clock_skew_ms = max_clock_skew_ms

    def grant(self) -> None:
        self.granted_at_ms = time.time() * 1000

    def is_valid(self) -> bool:
        """Return True only if lease is safely within duration."""
        if self.granted_at_ms is None:
            return False
        elapsed = time.time() * 1000 - self.granted_at_ms
        return elapsed < self.effective_duration_ms

    def renew(self) -> None:
        """Renew lease. Only valid if currently held."""
        if not self.is_valid():
            raise LeaseExpiredError(
                "Cannot renew expired lease. Must re-acquire."
            )
        self.granted_at_ms = time.time() * 1000

    def time_remaining_ms(self) -> float:
        if self.granted_at_ms is None:
            return 0.0
        elapsed = time.time() * 1000 - self.granted_at_ms
        return max(0, self.effective_duration_ms - elapsed)

# Usage:
# election_timeout = 150ms, max_clock_skew = 10ms
# safe_lease = SafeLease(150, 10)  # effective = 130ms
```

---

### ⚖️ Comparison Table

| Approach | Coordination Cost | Safety | Clock Dependency | Use Case |
|---|---|---|---|---|
| **Lease-based reads** | None during lease | Requires bounded skew | Yes (critical) | Leader reads, cache validity |
| **Read-index reads** | 1 heartbeat per read | Always safe | No | Linearizable reads when skew unbounded |
| **Quorum reads** | Quorum round trip | Always safe | No | Maximum safety, high latency |
| **Optimistic reads** | None | Stale reads possible | No | Analytics, best-effort |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A lease guarantees exclusive access indefinitely" | A lease has a fixed duration and MUST be renewed. If the holder crashes or loses connectivity, the lease expires and another node can acquire it. The holder must stop operations before its lease expires if it cannot confirm renewal. |
| "Longer leases are safer" | Longer leases reduce coordination overhead but increase the window during which a stale holder thinks it has the lease. The optimal lease duration balances coordination cost against safety margin for clock skew. |
| "etcd leases and Raft leases are the same thing" | etcd uses leases in two contexts: (1) leader lease for read optimization (Raft internal), (2) key-value object leases (TTL on keys, exposed via API). These are different mechanisms with different semantics. |
| "Clock sync eliminates lease safety concerns" | Even with NTP, clock skew is bounded (typically ±100ms) but not zero. The lease must be designed with this bound in mind. Perfect clock sync (Spanner's TrueTime) reduces the safety margin needed, but the principle of accounting for skew still applies. |

---

### 🚨 Failure Modes & Diagnosis

**Lease Overlap Causing Split-Brain Read**

**Symptom:** A distributed key-value store returns
different values for the same key from two different
nodes simultaneously. Both nodes believe they are
the current leader. Reads from node A return value
"X"; reads from node B return value "Y" for the
same key.

**Root Cause:** Clock skew exceeded the safety margin
built into the leader lease. Node A's clock ran slow;
it believed its lease had not expired when node B
had already been elected as the new leader and
started serving reads.

**Diagnosis:**
```bash
# Check clock skew between nodes:
for host in node-a node-b node-c; do
    echo "=== $host ==="
    ssh $host "chronyc tracking | grep offset"
done
# Look for: "System time offset" > safety_margin_ms

# Check etcd leader changes:
etcdctl endpoint status --cluster -w table
# Two nodes showing as leader? Split-brain confirmed.

# Check NTP service:
timedatectl show --property=NTPSynchronized
# If "NTPSynchronized=no": clock sync broken

# CockroachDB: check clock offset:
cockroach debug zip /tmp/debug --certs-dir=certs
# In debug output: look for nodes with clockOffsetMs
# exceeding 400ms (CockroachDB's threshold before it
# refuses transactions)
```

**Fix:**
1. Fix NTP configuration; ensure NTP service is
   running on all nodes.
2. Reduce lease duration or increase safety margin
   in configuration.
3. Transition to read-index reads (no lease, no
   clock dependency) until clock sync is reliable.
4. Add monitoring alert: `clock_offset > 80ms`
   (should alert well before hitting safety threshold).

---

### 🔗 Related Keywords

**Prerequisites:** `Leader Election` (DST-046),
`Distributed Locking` (DST-049),
`Hybrid Logical Clocks` (DST-052)

**Builds On This:** `Spanner and TrueTime` (DST-066)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LEASE        │ Time-bounded exclusive right from lessor │
│ DURATION     │ MUST be < election_timeout - 2*clock_skew│
├──────────────┼─────────────────────────────────────────-┤
│ JEOPARDY     │ Can't contact lessor: STOP operations    │
│              │ Wait for lease expiry or confirmed renew │
├──────────────┼──────────────────────────────────────────┤
│ ETCD LEASES  │ (1) Leader read optimization             │
│              │ (2) Key TTL - attach lease to KV keys    │
├──────────────┼──────────────────────────────────────────┤
│ CLOCK SKEW   │ Root of all lease safety problems        │
│ MONITOR      │ Alert: clock_offset > 80ms               │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Lease: no coordination during window;   │
│              │  must end before clock skew causes race" │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Leases teach the most important time-related principle
in distributed systems: any correctness guarantee
that depends on time must account for the fact that
clocks are imperfect and distributed clocks can
disagree. A lease that says "valid for 150ms" is
only valid if you can prove that all other nodes'
clocks agree that 150ms has not passed. In practice,
this requires: known clock skew bounds (NTP monitoring),
safety margins (reduce effective duration by 2x skew),
and fallback behavior (jeopardy state). This principle
extends to: HTTP cache expiry (max-age must account
for client clock drift), JWT expiry (check server-side
clock, not client), distributed rate limiting (token
counts reset based on server time, not client time),
and scheduled jobs (don't trust client timestamps for
ordering). Whenever correctness depends on time: verify,
bound the skew, and build in a safety margin.

---

### 💡 The Surprising Truth

Google Chubby (the original distributed lock service
that inspired etcd and ZooKeeper) was designed with
leases as a first-class feature, and its designers
had to grapple with a subtle consequence: the "jeopardy"
state. When a Chubby client cannot contact Chubby
(network partition), it doesn't know if its lease
has expired or is still valid. Chubby's solution -
the grace period where the client MUST stop using
its locks - was initially controversial internally
because it required application developers to handle
the jeopardy state explicitly. The insight that
emerged: any lease-based system must provide a way
for clients to handle "I don't know if I have the
right anymore" gracefully. Applications that ignore
jeopardy and continue operating assuming they still
hold the lease are the source of the most subtle
and hard-to-reproduce distributed bugs.

---

### ✅ Mastery Checklist

1. [CALCULATE] Given election_timeout=300ms and
   max_clock_skew=50ms, what is the safe maximum
   lease duration? Why must it be strictly less than
   election_timeout - 2*skew?
2. [IMPLEMENT] Build a SafeLease class that grants,
   checks validity, and renews a lease with the
   correct safety margin. Include a test that
   verifies the lease expires before a simulated
   new election can start.
3. [EXPLAIN] What is the jeopardy state in Chubby?
   What must the application do when it enters
   jeopardy? What happens if it does not?
4. [COMPARE] For a read-heavy key-value store, when
   would you prefer lease-based reads over read-index
   reads? What are the prerequisites for lease reads
   to be safe?
5. [DESIGN] A distributed cache where each entry has
   a lease (TTL). How does the cache implement lease
   expiry, renewal, and behavior under lease expiry?
   What happens if the cache node crashes while
   holding a lease?
