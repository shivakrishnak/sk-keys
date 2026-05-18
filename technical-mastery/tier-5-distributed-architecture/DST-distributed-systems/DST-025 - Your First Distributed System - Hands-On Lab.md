---
id: DST-025
title: "Your First Distributed System - Hands-On Lab"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-001, DST-008, DST-011, DST-018, DST-019
used_by: []
related: DST-012, DST-016, DST-021, DST-022
tags:
  - distributed
  - lab
  - meta
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/distributed-systems/hands-on-lab/
---

⚡ TL;DR - A structured sequence of hands-on exercises
that build a multi-node distributed system from scratch,
deliberately introducing and observing the failures
described in L0-L1 theory: network partitions, replication
lag, stale reads, and split-brain; learning through
controlled failure is the only way to internalize
distributed systems concepts.

---

### 📋 Entry Metadata

| #025 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Meta Entry:** | Hands-on lab synthesizing DST-001 through DST-023 | |
| **Prerequisites:** | Read DST-001 through DST-023 before starting | |
| **Estimated Time:** | 4-6 hours for full lab completion | |

---

### 🔥 Why This Lab Exists

Reading about distributed systems is necessary but not
sufficient. The mental model for why network partitions,
replication lag, and consistency trade-offs matter only
solidifies when you have personally observed them fail in
a controlled environment. This lab is designed to:

1. Build a functional 3-node distributed key-value store
2. Observe replication in real time
3. Inject failures and watch the system respond
4. Experience CP vs AP behavior firsthand
5. Implement idempotency and test it under retries

Every concept in DST-001 through DST-023 has a corresponding
lab exercise. After this lab, the theoretical content has
a concrete mental anchor.

---

### 🔧 Lab Environment Setup

**Prerequisites:**
- Docker Desktop installed
- Python 3.10+ (or Java 17+ for Java developers)
- curl or HTTPie
- Basic terminal proficiency

**Start the lab environment:**

```bash
# Clone the reference implementation:
git clone https://github.com/distributed-systems-lab/dst-lab
cd dst-lab

# Start 3-node cluster with Docker Compose:
docker compose up -d

# Verify nodes are running:
docker ps
# Should show: node-1, node-2, node-3, lb-proxy

# Check cluster health:
curl http://localhost:8001/health  # node-1
curl http://localhost:8002/health  # node-2
curl http://localhost:8003/health  # node-3
```

**Cluster architecture:**

```
┌────────────────────────────────────────────────────────┐
│  CLIENT                                                │
│      │                                                 │
│  LOAD BALANCER (port 8000)                             │
│      ├── node-1 (port 8001) [leader initially]        │
│      ├── node-2 (port 8002) [follower]                │
│      └── node-3 (port 8003) [follower]                │
│                                                        │
│  Single-leader replication: writes → node-1           │
│  Reads from any node (may see replication lag)        │
│  Consistent hashing for shard routing                 │
└────────────────────────────────────────────────────────┘
```

---

### 🧪 Exercise 1 - Basic Write/Read (15 min)

**Objective:** Observe single-leader replication in action.

```bash
# Write a value to the cluster (routed to leader):
curl -X PUT http://localhost:8000/keys/user:1 \
  -H "Content-Type: application/json" \
  -d '{"value": "Alice", "idempotency_key": "put-001"}'

# Read from load balancer (any node):
curl http://localhost:8000/keys/user:1

# Read directly from each node:
curl http://localhost:8001/keys/user:1  # leader: latest
curl http://localhost:8002/keys/user:1  # follower: check
curl http://localhost:8003/keys/user:1  # follower: check
```

**What to observe:**
- All three nodes should return "Alice" (replication is fast)
- The load balancer header `X-Served-By` shows which node
  served each read

**What to modify:**
- Write 10 values in rapid succession
- Read immediately from followers
- Observe if any reads return stale data

---

### 🧪 Exercise 2 - Observing Replication Lag (30 min)

**Objective:** Make replication lag visible.

```bash
# Enable artificial replication delay on followers:
curl -X POST http://localhost:8002/debug/set-replication-delay \
  -d '{"delay_ms": 500}'

curl -X POST http://localhost:8003/debug/set-replication-delay \
  -d '{"delay_ms": 500}'

# Write a value:
curl -X PUT http://localhost:8001/keys/counter:1 \
  -d '{"value": "100"}'

# Immediately read from each node:
echo "Leader (node-1):"; curl -s http://localhost:8001/keys/counter:1
echo "Follower (
    node-2):"; curl -s http://localhost:8002/keys/counter:1
echo "Follower (
    node-3):"; curl -s http://localhost:8003/keys/counter:1
```

**Expected output:**
```
Leader (node-1):   {"value": "100", "version": 1}
Follower (node-2): {"value": null, "error": "key not
  found"}
Follower (node-3): {"value": null, "error": "key not
  found"}
```

Wait 600ms, repeat reads. Now all three return "100".

**The lesson:** This is replication lag. A user who wrote
the value and immediately reads it back would see "not found"
if their read hit a follower. This motivates read-your-writes
consistency (DST-014).

**Cleanup:**
```bash
# Remove artificial delay:
curl -X POST http://localhost:8002/debug/set-replication-delay \
  -d '{"delay_ms": 0}'
curl -X POST http://localhost:8003/debug/set-replication-delay \
  -d '{"delay_ms": 0}'
```

---

### 🧪 Exercise 3 - Network Partition (45 min)

**Objective:** Force a partition and observe CP vs AP behavior.

**Part A - CP mode (system default):**

```bash
# The cluster is in CP mode by default:
# minority partition rejects writes

# Simulate network partition (isolate node-3 from leader):
docker network disconnect dst-lab_cluster node-3

# Verify: node-3 can no longer reach node-1/node-2
docker exec node-3 curl http://node-1:8001/health
# Expected: connection timeout

# Write to the cluster via load balancer:
curl -X PUT http://localhost:8000/keys/test:partition \
  -d '{"value": "during-partition"}'
# Expected: 200 OK (node-1 and node-2 form majority)

# Read from node-3 (partitioned minority):
curl http://localhost:8003/keys/test:partition
# Expected: 503 or stale data depending on CP vs AP mode
# In CP mode: 503 Service Unavailable
# (node-3 knows it is isolated, refuses to serve)
```

**Reconnect and observe recovery:**
```bash
docker network connect dst-lab_cluster node-3

# Wait 5 seconds for resync
sleep 5

# Read from node-3:
curl http://localhost:8003/keys/test:partition
# Expected: {"value": "during-partition"}
# node-3 has synced from the leader
```

**Part B - Switch to AP mode:**

```bash
curl -X POST http://localhost:8000/admin/set-mode \
  -d '{"mode": "AP"}'

# Repeat the partition:
docker network disconnect dst-lab_cluster node-3

# Write during partition:
curl -X PUT http://localhost:8000/keys/test:ap \
  -d '{"value": "during-ap-partition"}'

# Write to node-3 directly (AP mode: accepts writes):
curl -X PUT http://localhost:8003/keys/test:ap \
  -d '{"value": "from-partitioned-node"}'

# Reconnect:
docker network connect dst-lab_cluster node-3

# Observe conflict resolution:
sleep 2
curl http://localhost:8001/keys/test:ap
curl http://localhost:8003/keys/test:ap
# In AP mode: last-write-wins by timestamp
# One value survives, the other is discarded
```

**The lesson:** CP mode keeps data correct but makes
the minority partition unavailable. AP mode keeps all
nodes serving requests but may create conflicting writes
that must be resolved. This is the CAP theorem (DST-016)
experienced firsthand.

---

### 🧪 Exercise 4 - Leader Failover (30 min)

**Objective:** Observe automatic leader election.

```bash
# Check which node is currently leader:
curl http://localhost:8000/admin/status
# {"leader": "node-1", "followers": ["node-2", "node-3"]}

# Kill the leader:
docker stop node-1

# Watch leader election in logs:
docker logs node-2 --follow &
# You should see: "Heartbeat timeout for node-1"
#                 "Starting leader election..."
#                 "Won election with term 2"
#                 "I am the new leader"

# Write to the cluster (should succeed with new leader):
sleep 2  # Wait for election to complete (~1-2 seconds)
curl -X PUT http://localhost:8000/keys/post-failover \
  -d '{"value": "new-leader-write"}'

# Check new cluster status:
curl http://localhost:8000/admin/status
# {"leader": "node-2", "followers": ["node-3"]}
```

**Measure failover time:**
```bash
# Send requests in a loop and count errors:
for i in $(seq 1 50); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      http://localhost:8000/keys/probe 2>/dev/null)
    echo "$i: $STATUS"
    sleep 0.2
done
# Count 503 responses = approximate failover window
```

**Restart node-1 and observe recovery:**
```bash
docker start node-1
sleep 5
curl http://localhost:8000/admin/status
# node-1 should rejoin as a follower, not reclaim leader
```

---

### 🧪 Exercise 5 - Idempotency Under Retries (30 min)

**Objective:** Observe double-execution without idempotency,
then implement it.

**Part A - Non-idempotent operation:**

```bash
# Create a counter:
curl -X PUT http://localhost:8000/keys/counter \
  -d '{"value": 0}'

# Increment without idempotency (simulated retry):
curl -X POST http://localhost:8000/counters/counter/increment
curl -X POST http://localhost:8000/counters/counter/increment
# (simulating a retry because first response was lost)

# Check counter:
curl http://localhost:8000/keys/counter
# {"value": 2}  ← WRONG: should be 1
```

**Part B - Idempotent operation:**

```bash
# Reset counter:
curl -X PUT http://localhost:8000/keys/counter \
  -d '{"value": 0}'

# Increment with idempotency key (same key = same operation):
IDEM_KEY=$(uuidgen)

curl -X POST http://localhost:8000/counters/counter/increment \
  -H "Idempotency-Key: $IDEM_KEY"

# "Retry" with same idempotency key:
curl -X POST http://localhost:8000/counters/counter/increment \
  -H "Idempotency-Key: $IDEM_KEY"

# Check counter:
curl http://localhost:8000/keys/counter
# {"value": 1}  ← CORRECT: idempotency prevented double-increment
```

**Inspect the idempotency store:**
```bash
curl http://localhost:8000/debug/idempotency-keys
# Shows all stored keys and their cached results
```

---

### 🧪 Exercise 6 - Chaos Experiment (60 min)

**Objective:** Validate fault tolerance assumptions.

```bash
# Install toxiproxy for network chaos:
docker compose -f docker-compose-chaos.yml up -d

# Scenario 1: Add 100ms latency to all inter-node traffic
toxiproxy-cli toxic add node1-node2 -t latency -a latency=100

# Measure impact on write latency:
time curl -X PUT http://localhost:8000/keys/chaos:1 \
  -d '{"value": "test"}'
# Expected: ~200ms (100ms to replicate synchronously)

# Scenario 2: Add packet loss (5%)
toxiproxy-cli toxic add inter-cluster \
  -t bandwidth -a rate=50  # 50KB/s limit

# Watch replication lag grow under limited bandwidth:
watch -n 1 'curl -s http://localhost:8000/admin/replication-lag'

# Scenario 3: Kill-9 the leader (unclean shutdown)
docker kill -s 9 node-1  # SIGKILL, no graceful shutdown
# Observe: does the cluster elect a new leader?
# Is any data lost? Check leader's final writes vs new leader.
```

---

### 📊 Worksheet - Record Your Observations

During each exercise, record:

| Exercise | Observation | Matches Theory? | Surprise? |
|---|---|---|---|
| Ex1: Basic reads | Node consistency? | | |
| Ex2: Replication lag | Stale read window? | | |
| Ex3: CP mode partition | Minority behavior? | | |
| Ex3: AP mode conflict | Winning value? | | |
| Ex4: Leader election | Failover time (ms)? | | |
| Ex5: Idempotency | Counter value? | | |
| Ex6: Chaos | Data loss? | | |

**Key questions after completing:**
1. How long was the stale read window in Exercise 2?
   Does this match your read consistency expectations?
2. In Exercise 3 AP mode, which write won the conflict?
   Was the winner deterministic?
3. In Exercise 4, what was the failover time?
   Is it acceptable for your production SLA?
4. What surprised you most?

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ EXERCISE MAP:                                           │
│ Ex1: Replication basics (DST-012, DST-017)              │
│ Ex2: Replication lag (DST-026)                          │
│ Ex3: Network partition + CAP (DST-010, DST-016)         │
│ Ex4: Leader failover (DST-046, DST-017)                 │
│ Ex5: Idempotency (DST-018)                              │
│ Ex6: Chaos engineering (DST-011)                        │
├─────────────────────────────────────────────────────────┤
│ LEARNING PRINCIPLE:                                     │
│ "Every concept in distributed systems that surprised    │
│  you in a lab would have surprised you in production.  │
│  Prefer the lab."                                       │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The most valuable outcome of this lab is not the specific
exercises - it is the habit of deliberately injecting
failures. In production systems, failures happen
unexpectedly. The only teams that handle them well are
the ones that have previously created the same failure
in a controlled environment, measured the system's
response, and verified that the response matches their
design intent. Chaos engineering is not about breaking
things - it is about discovering, before production does,
whether your fault tolerance design is correct.

The lab exercises map directly to chaos engineering
practices used by Netflix (Chaos Monkey), Amazon (GameDays),
and Google (DiRT - Disaster Recovery Testing). Building
this habit early in your career is the most important
professional investment you can make in distributed
systems engineering.

---

### ✅ Completion Criteria

**You have completed the lab when you can:**
1. Explain WHY stale reads happened in Exercise 2 and
   what code change would prevent them.
2. Describe the exact sequence of events during leader
   election in Exercise 4, in terms of DST-020 heartbeat
   concepts.
3. Show the idempotency key storage contents from Exercise 5
   and explain why the counter did not double-increment.
4. Identify one assumption you made about distributed
   system behavior that the lab disproved.
5. Propose one chaos experiment not in this lab that
   would test another aspect of the system's fault
   tolerance.
