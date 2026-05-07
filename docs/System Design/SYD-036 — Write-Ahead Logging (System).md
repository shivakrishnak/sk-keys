---
layout: default
title: "Write-Ahead Logging (System)"
parent: "System Design"
nav_order: 36
permalink: /system-design/write-ahead-logging-system/
number: "SYD-036"
category: System Design
difficulty: ★★★
depends_on: Storage Systems, Durability, Leader-Follower Pattern
used_by: Databases, Message Queues, Recovery Systems
related: Leader-Follower Pattern, Event Sourcing, Append-Only Log
tags:
  - storage
  - durability
  - advanced
  - databases
  - recovery
---

# SYD-036 — Write-Ahead Logging (System)

⚡ TL;DR — Write-Ahead Logging records intended changes in an append-only log before mutating the main data structure. If the system crashes midway, the log can be replayed to recover consistent state.

| #716            | Category: System Design                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Storage Systems, Durability, Leader-Follower Pattern     |                 |
| **Used by:**    | Databases, Message Queues, Recovery Systems              |                 |
| **Related:**    | Leader-Follower Pattern, Event Sourcing, Append-Only Log |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
System crashes after changing memory or disk structures but before the change is fully durable. State becomes corrupted or ambiguous.

**SOLUTION:**
Log the intent first, then apply the change.

---

### 📘 Textbook Definition

**Write-Ahead Logging (WAL):** Durability technique in which updates are first written to a sequential log on stable storage before being applied to primary data structures, enabling crash recovery and replication.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Never update the database page before the recovery log says what you intended to do.

**One analogy:**

> Before moving money between envelopes, write the transaction in a ledger. If you get interrupted, the ledger tells you what still needs to be completed.

**One insight:**
Sequential append is cheap. Random repair without a log is expensive and unreliable.

---

### 🧠 Mental Model

```
1. append intent to log
2. fsync log
3. update in-memory / data files
4. later checkpoint data files

On crash:
  replay committed log entries
```

---

### 📶 Gradual Depth

**Level 1:** Save the recovery record before changing the main data.

**Level 2:** WAL gives crash recovery and enables replication from the log stream.

**Level 3:** Need log sequence numbers, checkpoints, flush ordering, and replay semantics.

**Level 4:** WAL is foundational because sequential disk writes outperform random writes and preserve a canonical mutation history.

---

### ⚙️ How It Works

```
Write path:
1. Client submits write
2. System creates log record with LSN
3. Append record to WAL
4. Flush WAL to durable storage
5. Acknowledge commit or apply to data pages

Recovery path:
1. Load last checkpoint
2. Scan WAL from checkpoint LSN
3. Redo committed operations
4. Undo incomplete work if needed
```

---

### 💻 Code Example

```python
class WALStore:
    def __init__(self):
        self.log = []
        self.state = {}

    def write(self, key, value):
        record = {"op": "set", "key": key, "value": value}
        self.log.append(record)  # write-ahead step
        self.state[key] = value  # apply after log append

    def recover(self):
        recovered = {}
        for record in self.log:
            if record["op"] == "set":
                recovered[record["key"]] = record["value"]
        self.state = recovered
```

---

### ⚖️ Comparison Table

| Approach                    | Crash recovery | Write cost         | Read complexity   |
| --------------------------- | -------------- | ------------------ | ----------------- |
| WAL                         | Strong         | Extra append/flush | Low               |
| Direct overwrite only       | Weak           | Lower initially    | Risky after crash |
| Full copy-on-write snapshot | Strong         | Higher             | Medium            |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                |
| -------------------------------------------- | ---------------------------------------------------------------------- |
| "WAL means data files are always up to date" | No. Data files may lag behind log position.                            |
| "Appending to log is enough"                 | Durability requires correct flush ordering, not just append in memory. |

---

### 🚨 Failure Modes

**Failure Mode 1: Acknowledge before log flush**

**Symptom:**
Client sees success, server crashes, write disappears.

**Prevention:**
Do not acknowledge committed writes before WAL durability policy is satisfied.

---

**Failure Mode 2: Unbounded log growth**

**Symptom:**
Replay time becomes huge and storage fills up.

**Prevention:**
Checkpoints, segment rotation, retention policy.

---

### 📌 Quick Reference

```
WAL:
  append first
  flush before claiming durability
  replay on crash
  checkpoint to bound recovery cost
```

---

### 🧠 Questions

**Q1.** When should a system acknowledge a write: after log append or after log fsync?

**Q2.** Why is WAL so useful for replication as well as recovery?
