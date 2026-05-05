---
layout: default
title: "Leader-Follower Pattern"
parent: "System Design"
nav_order: 715
permalink: /system-design/leader-follower-pattern/
number: "0715"
category: System Design
difficulty: ★★★
depends_on: Replication, Distributed Coordination, Failover
used_by: Databases, Consensus Systems, Replicated Services
related: Active-Passive, Distributed Locks, Write-Ahead Logging
tags:
  - replication
  - architecture
  - distributed-systems
  - advanced
  - failover
---

# 715 — Leader-Follower Pattern

⚡ TL;DR — One node becomes the leader and coordinates writes or decisions. Other nodes follow by replicating the leader’s state. This simplifies consistency and ordering, but introduces failover and leader-election complexity.

| #715            | Category: System Design                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Replication, Distributed Coordination, Failover        |                 |
| **Used by:**    | Databases, Consensus Systems, Replicated Services      |                 |
| **Related:**    | Active-Passive, Distributed Locks, Write-Ahead Logging |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Multiple replicas need one authoritative source for write ordering and state transitions.

**SOLUTION:**
Elect one leader to serialize changes, then replicate to followers.

---

### 📘 Textbook Definition

**Leader-Follower Pattern:** Replication and coordination pattern where a designated leader node accepts writes or makes coordination decisions and follower nodes copy or apply those decisions to stay consistent.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One node decides. Others copy.

**One analogy:**

> An orchestra conductor sets tempo and timing. The musicians follow the conductor so the performance stays synchronized.

**One insight:**
It is easier to keep one ordered log than many competing writers.

---

### 🧠 Mental Model

```
Leader:
  accepts writes
  assigns order
  replicates log

Followers:
  receive updates
  apply in order
  may serve reads
```

---

### 📶 Gradual Depth

**Level 1:** One machine is primary. Others are replicas.

**Level 2:** All writes go to leader. Followers catch up asynchronously or synchronously.

**Level 3:** Need leader election, replication lag handling, split-brain protection, and failover routing.

**Level 4:** This pattern underpins relational replication, Raft-like systems, metadata managers, and coordination services because it gives a single source of ordering.

---

### ⚙️ How It Works

```
1. Cluster elects leader
2. Clients send writes to leader
3. Leader appends operation to log
4. Followers replicate and apply log entries
5. On leader failure:
     elect new leader
     redirect clients

Trade-offs:
- simpler write consistency
- write throughput bottleneck at leader
- lag or stale reads on followers
```

---

### 💻 Code Example

```python
class Node:
    def __init__(self, node_id, role="follower"):
        self.node_id = node_id
        self.role = role
        self.log = []

    def append(self, command):
        if self.role != "leader":
            raise ValueError("writes must go to leader")
        self.log.append(command)
        return len(self.log)


leader = Node("n1", role="leader")
follower = Node("n2")

index = leader.append({"op": "create_user", "id": 42})
follower.log = leader.log.copy()
```

---

### ⚖️ Comparison Table

| Pattern                 | Write path           | Complexity | Best fit                    |
| ----------------------- | -------------------- | ---------- | --------------------------- |
| Leader-follower         | Single leader        | Medium     | Ordered writes              |
| Active-active           | Multiple writers     | High       | Regional write availability |
| Shared-nothing sharding | Per-partition leader | High       | Horizontal scale            |

---

### ⚠️ Common Misconceptions

| Misconception                       | Reality                                               |
| ----------------------------------- | ----------------------------------------------------- |
| "Followers are always identical"    | Replication lag means followers may be stale.         |
| "Leader-follower means no downtime" | Leader failure still requires detection and failover. |

---

### 🚨 Failure Modes

**Failure Mode 1: Split brain**

**Symptom:**
Two nodes both accept writes as leader.

**Prevention:**
Quorum election, fencing, and strict write routing.

---

**Failure Mode 2: Read-after-write inconsistency**

**Symptom:**
Client writes to leader then reads stale data from follower.

**Prevention:**
Read from leader, stickiness, or minimum replication acknowledgment.

---

### 📌 Quick Reference

```
Leader-follower:
  One writer, many replicas
  Great for ordering and simpler consistency
  Costs: failover complexity and leader bottleneck
```

---

### 🧠 Questions

**Q1.** When should followers be allowed to serve reads?

**Q2.** How do you stop stale leaders from continuing to write after failover?
