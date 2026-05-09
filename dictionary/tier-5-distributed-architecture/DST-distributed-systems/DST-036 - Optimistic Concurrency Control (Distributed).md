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