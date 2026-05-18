---
id: DST-077
title: Distributed Systems Migration Strategy
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-004, DST-035
used_by: []
related: DST-004, DST-035, DST-053, DST-076
tags:
  - distributed
  - migration
  - strangler-fig
  - live-migration
  - dual-write
  - cutover
  - zero-downtime
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 77
permalink: /technical-mastery/distributed-systems/migration-strategy/
---

⚡ TL;DR - Migrating a live distributed system
(database, storage engine, consistency model, or
topology) without downtime requires: dual-write
(write to both old and new simultaneously), backfill
(copy existing data from old to new), verification
(compare old vs new for correctness), and traffic
cutover (shift reads then writes); the most dangerous
migration step is cutover; the key invariant is that
the new system must be strictly ahead of the old
system at all times during dual-write; rollback
requires maintaining the old system for at least
24 hours after full cutover.

---

### 📋 Entry Metadata

| #077 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Discovery, Data Versioning | |
| **Used by:** | N/A (operational pattern) | |
| **Related:** | Service Discovery, Data Versioning, Event Sourcing, Global Distribution | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company needs to migrate from MySQL to Cassandra
for a high-throughput notifications table. The naive
approach: schedule 4 hours of downtime. Announce
to users. Stop writes. Export MySQL data. Import
to Cassandra. Update the application. Restart.
Hope everything works.

Problems: 4 hours of downtime destroys user trust.
The import may fail at 3.9 hours leaving the team
with no database. The application may have untested
bugs against Cassandra that only appear with real
data. There's no easy rollback if Cassandra performs
worse.

Live migration (zero-downtime) is more complex to
design but eliminates all of these risks. The cost:
running two systems simultaneously for weeks.
The benefit: instant rollback at any phase, no
downtime, production validation before cutover.

---

### 📘 Textbook Definition

**Live migration** (also: online migration, zero-
downtime migration): the process of moving data or
workload from one system to another while the system
continues to serve production traffic.

**Phases:**
1. **Dual-write:** New system receives all writes that old
   system receives. Old system is still the source of truth.
2. **Backfill:** Historical data copied from old to new.
   At completion: new system has all data.
3. **Verification:** Read from both; compare results.
   Identify divergence.
4. **Cutover:** Shift reads to new system. Validate.
   Shift writes to new system. Validate.
5. **Decommission:** Remove old system after confidence period.

---

### ⏱️ Understand It in 30 Seconds

```
LIVE MIGRATION PATTERN (DUAL-WRITE):

Phase 1: DUAL-WRITE begins
  Write → Old system (source of truth) + New system.
  Read → Old system only.
  State: both systems receiving writes.
         New system may lag (backfill not done yet).

Phase 2: BACKFILL
  Background job: copy all rows from Old to New.
  As backfill runs: new writes go to both (phase 1 covers
    new data).
  At completion: New has all historical + all new data.

Phase 3: VERIFICATION
  Shadow reads: for a % of requests, read from BOTH.
  Compare results. If they differ: log the divergence.
  Investigation + fix. Repeat until divergence rate = 0%.

Phase 4: CUTOVER READS
  Shift reads from Old to New.
  Monitor: latency, error rate. If issues: rollback (reads
    → Old).

Phase 5: CUTOVER WRITES
  Stop writing to Old. Write to New only.
  Old is now read-only. Monitor New carefully.
  If issues: turn Old back on (dual-write), fix, retry.

Phase 6: DECOMMISSION
  After 24-48 hours of stable operation on New:
  Decommission Old.
  
INVARIANT: During dual-write, New >= Old (version-wise).
If New falls behind: reads from New are stale.
Fix: pause cutover, let New catch up via backfill.
```

---

### 🔩 First Principles Explanation

**THE DUAL-WRITE CONSISTENCY CHALLENGE:**

```
PROBLEM: Writing to two systems is not atomic.
  Write to Old: succeeds.
  Write to New: fails (transient error).
  Result: Old and New diverge. New has stale data.

NAIVE DUAL-WRITE (WRONG):
  def write(data):
      old_db.write(data)  # Primary
      new_db.write(data)  # Best-effort; ignore errors
  
  Risk: new_db silently falls behind. You won't know
  until verification catches it (or after cutover).

SAFER DUAL-WRITE:
  def write(data):
      old_db.write(data)   # Must succeed (primary)
      try:
          new_db.write(data)  # Best-effort
      except Exception as e:
          # LOG AND TRACK the failure:
          divergence_counter.increment()
          divergence_log.write(key=data.id, error=str(e))
          # Do NOT raise - user request should not fail
          # because of migration infra.
      
  # Background repair: periodically re-sync divergent keys
  # by reading from Old and writing to New.

WRITE ORDERING GUARANTEE:
  Critical: New must process writes in the same order as
    Old.
  If writes are unordered: New can end up with wrong final
    state.
  
  Example:
    Write A: name="Alice" (version=1)
    Write B: name="Alice M." (version=2)
    
    Old DB: processed A then B. Final: "Alice M."
      (correct).
    New DB: processed B before A (due to retry timing).
    Final: "Alice" (WRONG - older value won due to OCC
      check).
    
  Fix: use a monotonic version or timestamp in writes.
  New DB: only apply write if incoming_version >
    stored_version.
```

**THE STRANGLER FIG PATTERN:**

```
ORIGIN: "The Strangler Fig" (Martin Fowler, 2004).
Named after the tropical plant that grows around
an existing tree, gradually replacing it.

APPROACH FOR MICROSERVICE MIGRATION:
  Old: monolith serves all requests.
  New: microservice handles a subset of requests.
  
  Step 1: Route 0% of requests to new service.
  Step 2: Route 1% to new service; 99% to old.
  Step 3: Monitor new service. If stable: increase to 10%.
  Step 4: Continue until 100% routed to new service.
  Step 5: Decommission old monolith endpoint.

WHY THIS WORKS FOR DISTRIBUTED SYSTEMS:
  The strangler fig approach applies to:
  - Migrating from monolith to microservices.
  - Migrating from MySQL to Cassandra (route a %
    of reads to Cassandra for verification before
    full cutover).
  - Migrating from one queue system to another
    (publish to both; consume from new; verify).
    
KEY: You can always revert by reducing the % routed
to the new system back to 0%.
```

**CUTOVER STRATEGY:**

```python
# Feature flag controlled cutover (safe, reversible)

from enum import Enum
import random

class MigrationPhase(Enum):
    OLD_ONLY = "old_only"
    DUAL_WRITE = "dual_write"
    SHADOW_READ = "shadow_read"
    NEW_READS_PERCENT = "new_reads_pct"
    NEW_ONLY = "new_only"

class MigrationConfig:
    """
    Migration state stored in a feature flag service
    (e.g., LaunchDarkly, ConfigCat, or Redis).
    Can be changed without deploying code.
    """
    phase: MigrationPhase = MigrationPhase.OLD_ONLY
    new_read_percent: float = 0.0  # 0.0 to 1.0

class DataAccessLayer:
    def __init__(self, old_db, new_db, config: MigrationConfig):
        self.old_db = old_db
        self.new_db = new_db
        self.config = config

    def write(self, key: str, value: str):
        # Always write to old (primary during migration):
        self.old_db.write(key, value)
        
        if self.config.phase in (
            MigrationPhase.DUAL_WRITE,
            MigrationPhase.SHADOW_READ,
            MigrationPhase.NEW_READS_PERCENT
        ):
            # Dual-write to new (best-effort):
            try:
                self.new_db.write(key, value)
            except Exception as e:
                self.track_divergence(key, "write_failed", e)

    def read(self, key: str) -> str:
        phase = self.config.phase

        if phase == MigrationPhase.OLD_ONLY:
            return self.old_db.read(key)

        if phase == MigrationPhase.SHADOW_READ:
            # Read from old (primary). Also read from new.
            # Compare. Track divergence. Return old result.
            old_val = self.old_db.read(key)
            try:
                new_val = self.new_db.read(key)
                if old_val != new_val:
                    self.track_divergence(key, "read_mismatch",
                                         {"old": old_val,
                                          "new": new_val})
            except Exception:
                pass
            return old_val  # Always return old

        if phase == MigrationPhase.NEW_READS_PERCENT:
            # Gradually shift reads to new system:
            if random.random() < self.config.new_read_percent:
                try:
                    return self.new_db.read(key)
                except Exception:
                    return self.old_db.read(key)  # Fallback
            return self.old_db.read(key)

        if phase == MigrationPhase.NEW_ONLY:
            return self.new_db.read(key)

    def track_divergence(self, key, reason, detail):
        metrics.increment("migration.divergence",
                          tags={"reason": reason})
        log.warning("Migration divergence",
                    key=key, reason=reason, detail=detail)
```

**BACKFILL STRATEGY:**

```python
# Backfill: copy all historical data from old to new.
# Must handle: ordering, idempotency, rate limiting.

def backfill_table(
    old_db, new_db,
    table: str,
    batch_size: int = 1000,
    checkpoint_key: str = "migration:backfill:last_id"
):
    """
    Backfill data from old_db to new_db.
    Uses checkpoint to resume after interruption.
    """
    last_id = redis_client.get(checkpoint_key) or 0

    while True:
        # Fetch batch from old:
        rows = old_db.execute(
            f"SELECT * FROM {table} WHERE id > %s "
            "ORDER BY id LIMIT %s",
            (last_id, batch_size)
        )

        if not rows:
            print("Backfill complete.")
            break

        # Upsert to new (idempotent: skip if newer version exists):
        for row in rows:
            new_db.upsert(
                table, row,
                condition="version < :version"
                # Only apply if new row has higher version
            )

        last_id = rows[-1]["id"]
        # Save checkpoint:
        redis_client.set(checkpoint_key, last_id)
        print(f"Backfilled up to id={last_id}")

        # Rate limit: avoid overwhelming new DB:
        time.sleep(0.1)
```

---

### 🧠 Mental Model / Analogy

> Live migration is like repaving a highway while
> traffic is still flowing. You can't close the
> highway (zero downtime). Instead:
> (1) Build a new lane alongside the old one.
> (2) Route a few cars to the new lane and see if
>     it handles traffic correctly (shadow reads).
> (3) Gradually shift more cars (read percentage).
> (4) Once all cars use the new lane:
>     close the old lane (decommission).
> The key: the new lane must be fully ready before
> any car is forced to use it. You need a clear
> on-ramp and off-ramp (rollback) at every stage.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The phases:**
Dual-write, backfill, verify, cutover reads, cutover
writes, decommission. Never skip phases.

**Level 2 - Dual-write is the dangerous phase:**
Running two systems simultaneously doubles operational
complexity. Every incident must be triage for two
systems. Keep this phase as short as possible.

**Level 3 - Shadow reads reveal divergence:**
Before cutting over reads, shadow-read both systems
for every request (read both, return old result,
compare silently). Fix all divergence before cutover.
A 0.001% divergence rate at migration scale = thousands
of incorrect reads after cutover.

**Level 4 - Rollback must be designed:**
At every phase: what is the rollback action?
Phase 4 (read cutover): shift reads back to old.
Phase 5 (write cutover): re-enable dual-write.
Rollback must be a config change, not a code deploy.

**Level 5 - Data model changes are hardest:**
Migrating between identical schemas is straightforward.
Migrating from a relational model to a wide-column
model (MySQL to Cassandra) requires: a data model
mapping layer, handling of joins (which don't exist
in Cassandra), and query rewrites. The schema
migration must happen before or in parallel with
the data migration.

---

### 💻 Code Example

*See the DataAccessLayer and backfill_table examples
in First Principles above.*

---

### ⚖️ Comparison Table

| Migration Strategy | Downtime | Rollback | Risk | Complexity |
|---|---|---|---|---|
| **Big bang (stop, migrate, start)** | Hours | Manual restore from backup | High | Low |
| **Dual-write + backfill** | Zero | Instant (config flag) | Medium | High |
| **Strangler fig (% routing)** | Zero | Instant (route 0% to new) | Low | Medium |
| **Event sourcing replay** | Zero | Easy (replay to old state) | Low | Very high |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Dual-write means both systems are equally correct" | During dual-write, the old system is the source of truth. The new system receives writes best-effort and may lag. Reads still come from the old system until shadow-read verification is complete. |
| "Shadow reads are optional" | Shadow reads are the most critical verification step. Without them, you cannot know if the new system produces correct results before you've already switched users to it. Always run shadow reads for a meaningful period before cutting over. |
| "Backfill is a one-time job" | Backfill must be idempotent and restartable (save checkpoints). It must also handle data written DURING the backfill (which is covered by dual-write). The backfill and dual-write phases overlap. |
| "After cutover, immediately decommission the old system" | Keep the old system in read-only mode for at least 24-48 hours after full cutover. This is the rollback window. During this period: any problem discovered can be mitigated by re-enabling reads or writes to the old system. |

---

### 🚨 Failure Modes & Diagnosis

**Write Divergence During Dual-Write**

**Symptom:** Shadow reads report 0.5% divergence
rate between old and new. The new system has wrong
values for ~500 keys per million reads.

**Root Cause:** The dual-write to the new system is
failing silently for a small percentage of writes.
The backfill covered historical data but is not
covering the live stream gap. Retries are not
being used for the new system writes.

**Diagnosis:**
```bash
# Check divergence tracker:
redis-cli GET migration:divergence:count
# → 12,453 in last hour (1% of writes failing)

# Check what errors are causing failures:
grep "divergence" /var/log/app/migration.log | \
  awk '{print $5}' | sort | uniq -c | sort -rn
# → 11,203: ConnectionPoolTimeout
# → 1,250: WriteTimeout

# ROOT CAUSE: New DB connection pool exhausted.
# New DB has max_connections=50. Dual-write + backfill
# job is using all 50 connections. Live writes time out.

# Fix:
# 1. Increase new DB connection pool to 100.
# 2. Throttle backfill job (reduce batch size, increase sleep).
# 3. Add retry to the dual-write path:
#    new_db.write(key, value, retries=3, backoff=0.1)
# 4. Add a divergence repair job: reads divergent keys
#    from the divergence log, re-syncs them from old to new.
```

---

### 🔗 Related Keywords

**Prerequisites:** `Service Discovery` (DST-004),
`Data Versioning` (DST-035)

**Related:** `Event Sourcing` (DST-053),
`Global Distribution` (DST-076)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LIVE MIGRATION PHASES                                   │
│ 1. DUAL-WRITE: write to both; read from old            │
│ 2. BACKFILL: copy historical data to new               │
│ 3. SHADOW READ: read both; compare; fix divergence     │
│ 4. CUTOVER READS: shift reads to new                   │
│ 5. CUTOVER WRITES: stop writing to old                 │
│ 6. DECOMMISSION: remove old after 24-48h               │
├─────────────────────────────────────────────────────────┤
│ INVARIANTS                                              │
│ Old = source of truth during dual-write               │
│ New >= Old (version) at all times                     │
│ Rollback = config flag, not code deploy               │
│ Shadow read divergence = 0% before cutover            │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The live migration pattern is an instance of a more
general principle: never make irreversible changes
to a production system without a tested rollback
path. The phases of live migration (dual-write,
verify, cut over) are an implementation of "change
incrementally and verify at each step." This principle
applies to: schema migrations (add nullable columns
first, migrate data, then add constraints), feature
rollouts (canary releases, A/B testing), infrastructure
changes (add new load balancer in parallel, shift
traffic, remove old LB), and architectural refactoring
(extract microservice via strangler fig, not big-bang
rewrite). The common thread: run old and new in
parallel; verify the new is correct; then switch
over; preserve the ability to roll back.

---

### 💡 The Surprising Truth

One of the most overlooked aspects of live migration
is the "decommission" phase. Teams successfully
migrate to the new system and then keep the old
system running "just in case" for months or years.
The old system continues to consume memory, CPU,
storage, and engineer attention. It accumulates
bugs and security vulnerabilities because it's not
being developed. Decommission should be planned
as a formal project phase with a target date, not
left as an open-ended task. The decommission date
should be set BEFORE the migration begins. At Stripe,
the decommission of old database systems is formally
tracked with a "kill date" and an assigned owner.
When the kill date arrives: decommission happens,
barring an extraordinary exception. This discipline
prevents the accumulation of legacy systems that
drain engineer productivity.

---

### ✅ Mastery Checklist

1. [DESIGN] You need to migrate a PostgreSQL users table
   to Cassandra (different data model). Describe the
   dual-write phase. How do you handle JOINs that
   PostgreSQL supports but Cassandra does not?
2. [IMPLEMENT] Write a shadow read comparison function
   that reads from both systems, compares the results,
   and logs divergence with key, old_value, new_value,
   and timestamp. How do you handle None vs null vs
   empty string differences?
3. [PLAN] Design a rollback strategy for Phase 5
   (write cutover). At what point would you trigger
   the rollback? What is the maximum acceptable
   divergence rate before rollback?
4. [IDENTIFY] A live migration has been in dual-write
   phase for 3 months. The divergence rate is 0.1%.
   The team keeps finding new edge cases. How do
   you unblock the migration? What decision criteria
   determine when 0.1% divergence is acceptable?
5. [OPERATE] After full cutover to the new system,
   a P2 incident is reported: 0.01% of reads return
   incorrect data. The old system is still running
   (read-only). Should you roll back? What is the
   decision framework?
