---
id: SYD-059
title: Event Sourcing
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-041, SYD-057
used_by: ""
related: SYD-041, SYD-057, SYD-058, SYD-033
tags:
  - architecture
  - event-sourcing
  - audit
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /syd/event-sourcing/
---

# SYD-059 - Event Sourcing

⚡ TL;DR - Event Sourcing stores ALL state changes as
an ordered, immutable sequence of events instead of
storing the current state. "What is the balance?" is
answered by replaying all events: Deposited(100),
Withdrew(30), Deposited(50) → balance = 120. The current
state is a derived view; the event log is the source of
truth. Benefits: complete audit history, ability to replay
events to rebuild state, time-travel (what was the state
on Tuesday?). Cost: complexity, eventual consistency,
and replaying many events can be slow (solved with snapshots).

| #059 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Write-Ahead Logging (System), Event-Driven Architecture | |
| **Related:** | Write-Ahead Logging, Event-Driven Architecture, CQRS, Database Internals | |

---

### 🔥 The Problem This Solves

A bank account system gets a complaint: "My $500 transfer
disappeared." The database shows the current balance but
not how it got there. The audit log has timestamps but
not the exact values at each step. Without event sourcing:
- No way to know the exact balance at any point in time
- If there was a bug in the transfer code: no way to
  identify which transactions were affected
- Cannot replay transactions to find the error

Banks, financial systems, and healthcare systems REQUIRE
a complete, tamper-evident history of every state change.
Event sourcing provides this as a first-class design.

---

### 📘 Textbook Definition

**Event Sourcing:** An architectural pattern where the
state of a domain object is not stored directly.
Instead, all state changes are stored as an ordered
sequence of events. The current state is derived by
replaying (folding) the event sequence.

**Event store:** An append-only log of domain events,
ordered by time. Events are never modified or deleted.
New events are appended at the end.

**Aggregate:** A cluster of related domain objects
treated as a single unit. In event sourcing, an aggregate
is loaded by replaying its event history. Its current
state = fold(initial_state, events).

**Snapshot:** A point-in-time capture of an aggregate's
state, used to speed up replay. Instead of replaying
all events from the beginning, replay events from
the most recent snapshot.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store every change as an event, not the current state.
Current state = replay of all events.

**One analogy:**
> A ledger-based accounting system:
> A bank does not store "balance = $120."
> It stores every transaction:
>   - Deposit $100
>   - Withdrawal $30
>   - Deposit $50
> The balance ($120) is derived by summing the ledger.
> The ledger is the source of truth; the balance is a
> derived view. You can always recalculate the balance.
> You can see what the balance was at any point in time.
> You can find who made which change and when.

**One insight:**
Traditional databases store a snapshot of current state.
Event sourcing stores the history that led to that state.
History answers questions that a snapshot cannot: "What
happened?", "When exactly did this change?", "What would
the state be if we undid that one transaction?"

---

### 🔩 First Principles Explanation

**EVENT STORE VS. TRADITIONAL DATABASE:**
```
TRADITIONAL DATABASE:
  Table: accounts
  | account_id | balance | updated_at         |
  | 123        | 120.00  | 2024-01-15 10:30  |
  
  After UPDATE balance = 120:
  Previous state is GONE. No history.

EVENT STORE:
  Table: events (append-only)
  | account_id | event_type | amount | occurred_at        |
  | 123        | Deposited  | 100.00 | 2024-01-01 09:00  |
  | 123        | Withdrew   |  30.00 | 2024-01-10 14:00  |
  | 123        | Deposited  |  50.00 | 2024-01-15 10:30  |
  
  Current balance = fold events:
    0 + 100 - 30 + 50 = 120
  
  Balance on 2024-01-05?
    Replay events up to 2024-01-05:
    0 + 100 = 100
  
  Who changed the balance on Jan 10?
    The Withdrew event with occurred_at = Jan 10.
```

**AGGREGATE LIFECYCLE:**
```
Loading an aggregate (from events):

def load_account(account_id, event_store):
    events = event_store.load(account_id)
    account = Account(id=account_id, balance=0)
    
    for event in events:
        account.apply(event)  # Replay each event
    
    return account  # Current state

Applying events:
def apply(self, event):
    if event.type == "Deposited":
        self.balance += event.amount
    elif event.type == "Withdrew":
        self.balance -= event.amount
    elif event.type == "AccountOpened":
        self.status = "active"
        self.owner = event.owner

Executing a command:
def withdraw(account, amount):
    if account.balance < amount:
        raise ValueError("Insufficient funds")
    
    event = WithdrewEvent(
        account_id=account.id,
        amount=amount,
        timestamp=now()
    )
    # Persist the event (append-only)
    event_store.append(event)
    # Update in-memory state
    account.apply(event)
    
    # Note: we store the EVENT, not the new balance
```

**SNAPSHOTS FOR PERFORMANCE:**
```
Problem: account has 10,000 transactions.
Replaying 10,000 events on every load = slow.

Solution: snapshot every N events (e.g., every 100).

Snapshot: {
    account_id: 123,
    balance: 8750.00,
    status: "active",
    snapshot_version: 100  # event position
}

Loading with snapshot:
  1. Load latest snapshot (balance=8750, version=100)
  2. Load events AFTER version 100 (events 101-10000)
  3. Replay only events 101-10000 (not 0-10000)
  4. Result: 9900 fewer events to replay

Snapshot frequency:
  High write volume: snapshot every 100-500 events
  Low write volume: snapshot less frequently
  
IMPORTANT: Snapshot is a cache of derived state.
Events are still the source of truth.
```

---

### 🧪 Thought Experiment

**AUDIT AND TIME-TRAVEL FOR A FINANCIAL SYSTEM**

Regulatory requirement: "Show me every state transition
for all accounts in Q3 2023."

**Traditional database:**
Current state only. Historical states lost on each UPDATE.
To comply: need a separate audit log table.
Audit log is written separately from the main update:
risk of inconsistency (update succeeds, audit log fails).
Reconstruction of state at a specific date: impossible
unless audit log was designed to capture every change
(it usually is not complete enough).

**Event sourcing:**
Every state change is an event in the event store.
Query: all events for all accounts between July 1 and
September 30, 2023 → trivial: filter by timestamp.
Reconstruct state of account 123 on July 15, 2023:
replay all events for account 123 up to July 15.
The audit log IS the data store - no divergence possible.
No separate audit log maintenance.

**Bug in calculation:**
On Dec 1, you discover a bug in interest calculation
from Nov 1-30. It incorrectly applied 3% instead of 2%.
With event sourcing:
- Identify all "InterestApplied" events in November
- Emit a correcting event: "InterestCorrected" with
  the delta amount
- No data was "wrong" - the events capture what actually
  happened (including the error); the correction is also
  an event. Complete auditability.

---

### 🧠 Mental Model / Analogy

> Event sourcing is like version control for data:
>
> Git does not store the current state of your files only.
> It stores every commit (every change) as an immutable
> record. The current state of your code is derived by
> applying all commits from the beginning.
> You can `git checkout <date>` to see the state at any
> point in time. You can see WHO changed WHAT and WHEN.
>
> Event sourcing is the same pattern applied to business
> data: every change is a commit (event). The current
> balance/state is the checkout of all commits.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of just storing what something IS right now, event
sourcing stores everything that HAPPENED. "The balance is
$120" is replaced by "Deposited $100, withdrew $30,
deposited $50." You always know the whole history.

**Level 2 - How to use it (junior developer):**
Create events for every state change (Deposited, Withdrew,
AccountOpened). Store events in an append-only table (event
store). Load an account by replaying its events. Use
snapshots to speed up loading for accounts with many events.

**Level 3 - How it works (mid-level engineer):**
Aggregate loads by replaying its event stream from the
event store. Commands validate business rules against
in-memory state, then append new events to the event store
(never update). The event store is append-only and
immutable. Snapshots are cached derived states used to
reduce replay overhead. CQRS complements event sourcing:
the event stream feeds projections that serve queries.

**Level 4 - Why it was designed this way (senior/staff):**
Event sourcing solves two distinct problems: auditability
and temporal queries. Auditability: the event log is tamper-
evident (append-only, immutable), making it the ideal audit
trail for regulated industries. Temporal queries: "what was
the state at T" requires only filtering events by timestamp.
The cost is load complexity: loading an aggregate by
replaying N events is O(N). Snapshots reduce this to O(N
- last_snapshot_position). Another cost: the event schema
is a public contract - changing an event type (renaming,
removing fields) breaks replay. Event schema evolution
requires upcasting (transform old events to new schema
on load). This makes event sourcing suitable for stable
domain models, not rapidly-changing schema contexts.

**Level 5 - Mastery (distinguished engineer):**
Greg Young's original formulation (2010) treats event
sourcing as primarily a persistence mechanism, not a
messaging mechanism. Events are facts about aggregates;
they are stored in an event store (e.g., EventStoreDB)
and optionally published to a message bus (Kafka) for
integration with other bounded contexts. The event store
is the source of truth; Kafka is the delivery mechanism.
Conflating these (using Kafka as both the event store and
the message bus) creates operational risk: Kafka's retention
policy may delete events before they are replayed (the
event log is not infinite by default). For true event
sourcing, the event store must retain ALL events indefinitely
(or with intentional archival). Netflix's distributed tracing
system (Zipkin) and payment systems at Monzo and Stripe
use event sourcing as their core persistence strategy.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ EVENT SOURCING FLOW                                 │
│                                                      │
│ WRITE PATH:                                         │
│   Client: withdraw $30 from account 123            │
│     │                                               │
│     ▼                                               │
│   Command Handler:                                 │
│     1. Load events for account 123 from store     │
│     2. Replay: build in-memory state (balance=100) │
│     3. Validate: balance >= 30? YES                │
│     4. Append event:                               │
│        {type: Withdrew, amount: 30,               │
│         timestamp: T, account_id: 123}            │
│     5. Publish to Kafka: Withdrew event           │
│     6. Return success (no return value from write) │
│                                                      │
│ READ PATH (via CQRS projection):                   │
│   Projection consumer reads Withdrew from Kafka   │
│   Updates read model: balance_view → 70           │
│   Query: GET /accounts/123/balance               │
│   → Read model returns 70 (eventually consistent) │
│                                                      │
│ SNAPSHOT FLOW:                                     │
│   Every 100 events:                               │
│     Save snapshot: {account_id: 123, balance: 70, │
│                     version: N}                   │
│   On next load:                                   │
│     Read snapshot (version N, balance=70)         │
│     Replay only events > version N                │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Event-sourced bank account**
```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime, timezone
import uuid

# ======= DOMAIN EVENTS =======

@dataclass(frozen=True)
class AccountOpened:
    event_id: str
    account_id: str
    owner: str
    timestamp: str

@dataclass(frozen=True)
class Deposited:
    event_id: str
    account_id: str
    amount: float
    timestamp: str

@dataclass(frozen=True)
class Withdrew:
    event_id: str
    account_id: str
    amount: float
    timestamp: str

# ======= AGGREGATE =======

class BankAccount:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance: float = 0.0
        self.status: str = "pending"
        self.owner: str = ""
        self._version: int = 0  # For optimistic locking
        self._pending_events: List = []

    def apply(self, event) -> None:
        """Apply event to update in-memory state."""
        if isinstance(event, AccountOpened):
            self.status = "active"
            self.owner = event.owner
        elif isinstance(event, Deposited):
            self.balance += event.amount
        elif isinstance(event, Withdrew):
            self.balance -= event.amount
        self._version += 1

    # ======= COMMAND HANDLERS =======

    def open_account(self, owner: str) -> None:
        event = AccountOpened(
            event_id=str(uuid.uuid4()),
            account_id=self.account_id,
            owner=owner,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self._pending_events.append(event)
        self.apply(event)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.status != "active":
            raise ValueError("Account not active")
        event = Deposited(
            event_id=str(uuid.uuid4()),
            account_id=self.account_id,
            amount=amount,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self._pending_events.append(event)
        self.apply(event)

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        event = Withdrew(
            event_id=str(uuid.uuid4()),
            account_id=self.account_id,
            amount=amount,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self._pending_events.append(event)
        self.apply(event)


# ======= EVENT STORE REPOSITORY =======

class AccountRepository:
    def __init__(self, event_store, snapshot_store):
        self.event_store = event_store
        self.snapshot_store = snapshot_store

    def load(self, account_id: str) -> BankAccount:
        account = BankAccount(account_id)

        # Load latest snapshot to reduce replay cost
        snapshot = self.snapshot_store.load(account_id)
        start_version = 0
        if snapshot:
            account.balance = snapshot["balance"]
            account.status = snapshot["status"]
            account.owner = snapshot["owner"]
            account._version = snapshot["version"]
            start_version = snapshot["version"]

        # Replay events AFTER the snapshot version
        events = self.event_store.load(
            account_id, after_version=start_version)
        for event in events:
            account.apply(event)

        return account

    def save(self, account: BankAccount) -> None:
        # Append pending events to the store
        self.event_store.append_all(
            account._pending_events,
            expected_version=account._version - len(
                account._pending_events)  # Optimistic lock
        )
        account._pending_events.clear()

        # Take snapshot every 100 events
        if account._version % 100 == 0:
            self.snapshot_store.save({
                "account_id": account.account_id,
                "balance": account.balance,
                "status": account.status,
                "owner": account.owner,
                "version": account._version
            })
```

**Example 2 - Mutable state (BAD for audit requirements)**
```python
# BAD: Overwrites state - no history retained
def withdraw_bad(account_id: str, amount: float):
    account = db.query(
        "SELECT * FROM accounts WHERE id = %s",
        [account_id])
    new_balance = account.balance - amount
    
    # History is LOST after this UPDATE
    # No way to know what the balance was before
    # No audit trail of who withdrew and when
    db.execute(
        "UPDATE accounts SET balance = %s WHERE id = %s",
        [new_balance, account_id])

# GOOD: Append event - state reconstructed from history
def withdraw_good(account_id: str, amount: float):
    repo = AccountRepository(event_store, snapshot_store)
    account = repo.load(account_id)  # Replay events
    account.withdraw(amount)          # Validate + create event
    repo.save(account)                # Append event to store
    # Complete history preserved.
    # Who withdrew what and when: in the event store.
```

---

### ⚖️ Comparison Table

| Aspect | Traditional Store | Event Sourcing |
|---|---|---|
| **Storage** | Current state only | All historical events |
| **Audit** | Separate audit log (risk of divergence) | Built-in (events are the data) |
| **Time-travel queries** | Not possible (unless audit log) | Trivial (replay to timestamp) |
| **Load performance** | O(1) | O(N events) - mitigated with snapshots |
| **Schema changes** | Easy (ALTER TABLE) | Hard (upcasting old events) |
| **Complexity** | Low | High |
| **Best for** | Simple CRUD, stable data | Finance, healthcare, any audit requirement |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Event sourcing is the same as event-driven architecture | EDA is about communication between services (producer publishes event, consumers react). Event sourcing is about persistence: storing all state changes as events. You can use EDA without event sourcing, and event sourcing without EDA. They complement each other when combined: CQRS + event sourcing uses EDA to propagate projections. |
| Events can be modified to fix bugs | Events are immutable facts: they record what happened. If a bug caused wrong calculations, the fix is to append a correcting event (not to modify the original event). Modifying events destroys the audit trail. The correcting event is itself part of the history. |
| Snapshots are required | Snapshots are a performance optimization, not a requirement. For aggregates with few events, replay from the beginning is fast (< 10ms for 100 events). Snapshots become necessary when aggregates have thousands of events (accounts with years of transaction history). Start without snapshots; add them when replay becomes measurably slow. |

---

### 🚨 Failure Modes & Diagnosis

**Event Stream Grows Unboundedly (Large Aggregates)**

**Symptom:**
Loading a specific account takes 5-10 seconds.
The account has 500,000+ events (a high-volume trading
account). Service timeouts on load. Memory pressure
during replay (loading all 500K events into memory).

**Root Cause:**
No snapshot strategy implemented. Every load replays
all events from the beginning. Large aggregates become
unusable over time.

**Fix - Snapshot strategy + stream segmentation:**
```python
SNAPSHOT_INTERVAL = 500  # Snapshot every 500 events

class AccountRepository:
    def load(self, account_id: str) -> BankAccount:
        account = BankAccount(account_id)
        snapshot = self.snapshot_store.load(account_id)
        start_version = 0

        if snapshot:
            account.balance = snapshot["balance"]
            account._version = snapshot["version"]
            start_version = snapshot["version"]
        else:
            # Large aggregate, no snapshot:
            # Load in batches to avoid memory pressure
            pass

        # Load events in batches (not all at once)
        batch_size = 1000
        version = start_version
        while True:
            events = self.event_store.load_batch(
                account_id,
                after_version=version,
                limit=batch_size
            )
            if not events:
                break
            for event in events:
                account.apply(event)
            version = account._version

            # Take snapshot at interval
            if account._version % SNAPSHOT_INTERVAL == 0:
                self.snapshot_store.save({
                    "account_id": account_id,
                    "balance": account.balance,
                    "version": account._version
                })

        return account

# Alternative: archive old events to cold storage
# Active events: last 1 year in hot event store (fast)
# Archived events: > 1 year in S3/cold store (slow)
# Load archived events only when historical query needed
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Write-Ahead Logging (System)` - WAL is database-level
  event sourcing; understanding WAL builds intuition
  for why append-only logs are powerful
- `Event-Driven Architecture` - event sourcing uses
  EDA to propagate events to projections

**Builds On This (learn these next):**
- `CQRS` - almost always combined with event sourcing;
  the event log feeds projections that serve queries
- `Database Internals` - understanding how traditional
  databases work illuminates why event sourcing is
  different and when each approach is appropriate

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Store events, not state. Current state =  │
│             │ replay of all events. Append-only log.    │
├─────────────┼──────────────────────────────────────────  │
│ EVENT STORE │ Append-only. Never update or delete.      │
│             │ Events ordered by version per aggregate.  │
├─────────────┼──────────────────────────────────────────  │
│ SNAPSHOT    │ Cache of state at version N.              │
│             │ Replay from snapshot, not from 0.        │
├─────────────┼──────────────────────────────────────────  │
│ AUDIT       │ Complete history by design. No extra log. │
│             │ Tamper-evident (append-only).             │
├─────────────┼──────────────────────────────────────────  │
│ TIME-TRAVEL │ Replay events up to timestamp T.         │
│             │ Answer: "What was the state at T?"       │
├─────────────┼──────────────────────────────────────────  │
│ COST        │ Schema changes: upcasting required.       │
│             │ Load: O(N) events (mitigated by snapshot).│
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Append-only event log. State = replay.  │
│             │  Snapshot for performance."              │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Circuit Breaker → Bulkhead Pattern       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. The event store is append-only and immutable. State is
   derived by replaying events. The event log is the source
   of truth; the current state in memory or in a projection
   is always derivable from the log.
2. Snapshots are a performance optimization: cache the
   aggregate state at version N, replay only events after
   version N. Without snapshots, load time grows linearly
   with the number of events per aggregate.
3. Events are immutable facts. To fix a bug: append a
   correcting event. Never modify or delete past events.
   This preserves the audit trail and ensures the history
   is a faithful record of what actually happened (including
   errors and their corrections).

**Interview one-liner:**
"Event sourcing: all state changes stored as immutable, append-only events in an
event store (never the derived state). Loading an aggregate = replaying its event
stream (fold events into state). Snapshots every N events reduce replay to O(N -
snapshot_position). Built-in audit trail: events are the data, not a separate log.
Time-travel: replay events up to timestamp T. Cost: schema changes require
upcasting old events; load is O(N) without snapshots. Almost always paired with
CQRS: event store as write model, projections as read model."
