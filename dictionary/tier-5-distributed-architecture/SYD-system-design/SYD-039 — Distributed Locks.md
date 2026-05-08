---
layout: default
title: "Distributed Locks"
parent: "System Design"
nav_order: 39
permalink: /system-design/distributed-locks/
id: SYD-039
category: System Design
difficulty: ★★★
depends_on: Distributed Systems, Consensus, Failure Detection
used_by: Leader Election, Job Scheduling, Critical Sections
related: Leader-Follower Pattern, Idempotency Key, Coordination Services
tags:
  - distributed-systems
  - locking
  - coordination
  - advanced
  - reliability
---

# SYD-039 — Distributed Locks

⚡ TL;DR — A distributed lock ensures only one node in a cluster performs a critical action at a time. It is much harder than a local mutex because networks partition, clocks drift, and processes can die while holding the lock.

| #714            | Category: System Design                                         | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Systems, Consensus, Failure Detection               |                 |
| **Used by:**    | Leader Election, Job Scheduling, Critical Sections              |                 |
| **Related:**    | Leader-Follower Pattern, Idempotency Key, Coordination Services |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Ten workers all try to run the same monthly billing job. Without coordination, customers are charged ten times.

**SOLUTION:**
Use a shared lock so only one worker enters the critical section.

---

### 📘 Textbook Definition

**Distributed Lock:** Coordination primitive used across multiple processes or nodes to grant exclusive access to a shared resource or operation in a distributed system.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Like a mutex, but the contenders are machines, not threads.

**One analogy:**

> A shared equipment room in an office with a single physical key. Whoever holds the key may enter; everyone else must wait. If the key holder disappears, someone must decide when to safely reclaim the key.

**One insight:**
The hard part is not acquisition. The hard part is safe expiration and failure handling.

---

### 🧠 Mental Model

```
Local lock:
  same process, shared memory, clear ownership

Distributed lock:
  different machines, unreliable network,
  uncertain process liveness, clock drift
```

---

### 📶 Gradual Depth

**Level 1:** Only one worker should do the job.

**Level 2:** Acquire lock from shared store, do work, release lock.

**Level 3:** Use leases with expiration, fencing tokens, and heartbeats. Never rely only on a boolean lock flag.

**Level 4:** Many systems do better by avoiding locks: idempotent tasks, partition ownership, or transactional uniqueness constraints.

---

### ⚙️ How It Works

```
Basic lease lock:
1. Worker writes lock_key if absent
2. Lock value contains owner + expiry
3. Worker renews before expiry
4. On completion, worker releases if still owner

Failure hazards:
- Worker pauses, lease expires, another worker acquires
- Old worker resumes and still writes
- Network partition makes two workers believe they own lock

Mitigation:
- fencing token: monotonically increasing lock version
- downstream systems reject stale token holders
```

---

### 💻 Code Example

```python
import time
import uuid


class LeaseLock:
    def __init__(self):
        self.record = None

    def try_acquire(self, ttl_seconds=10):
        owner = str(uuid.uuid4())
        now = time.time()
        if self.record is None or self.record["expires_at"] <= now:
            self.record = {"owner": owner, "expires_at": now + ttl_seconds}
            return owner
        return None

    def release(self, owner):
        if self.record and self.record["owner"] == owner:
            self.record = None
```

---

### ⚖️ Comparison Table

| Approach                        | Exclusivity        | Failure safety | Operational cost |
| ------------------------------- | ------------------ | -------------- | ---------------- |
| Local mutex                     | Process-local only | High           | Low              |
| Redis-style lease               | Medium             | Medium         | Medium           |
| Consensus lock (ZooKeeper/etcd) | High               | Higher         | Higher           |
| No lock, idempotent design      | Often enough       | Often best     | Medium           |

---

### ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------ |
| "A lock key in Redis is enough"    | Not for correctness-critical workflows without lease and fencing design. |
| "Lock acquired means work is safe" | Only if downstream actions can reject stale owners.                      |

---

### 🚨 Failure Modes

**Failure Mode 1: Split-brain lock ownership**

**Symptom:**
Two workers both think they hold the lock and both run the job.

**Prevention:**
Leases, fencing tokens, consensus systems, idempotent side effects.

---

**Failure Mode 2: Stuck lock**

**Symptom:**
Worker crashes and lock never clears.

**Prevention:**
Expiration-based lease instead of manual release only.

---

### 📌 Quick Reference

```
Distributed lock:
  Use when exclusive execution is truly required
  Prefer leases over permanent locks
  Add fencing for correctness-critical operations
  If possible, redesign to avoid needing locks
```

---

### 🧠 Questions

**Q1.** When is a database uniqueness constraint better than a distributed lock?

**Q2.** If the lock holder pauses for a GC stop-the-world event, what breaks?
