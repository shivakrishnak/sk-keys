---
id: DST-060
title: "Build a Distributed Key-Value Store - Phase 1"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-011, DST-012, DST-016
used_by: DST-073, DST-089
related: DST-011, DST-012, DST-016, DST-041
tags:
  - distributed
  - key-value-store
  - lab
  - consistent-hashing
  - replication
  - hands-on
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/distributed-systems/build-kv-store-phase1/
---

⚡ TL;DR - Phase 1 of a 3-phase distributed KV store
lab: build a single-node in-memory KV store, add
consistent hashing to partition keys across multiple
nodes, implement basic replication for fault tolerance;
by the end you have a runnable 3-node cluster that
handles put/get with data distributed and replicated.

---

### 📋 Entry Metadata

| #060 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Sharding and Partitioning, Replication, Consistent Hashing | |
| **Used by:** | Build KV Store Phase 2, Build KV Store Phase 3 | |
| **Related:** | Sharding, Replication, Consistent Hashing, Raft | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Reading about distributed systems is not the same
as building one. You can read about consistent
hashing, replication, and fault tolerance for hours
without truly understanding why each design decision
was made, what the failure modes are, and why the
papers describe the algorithms the way they do.

Phase 1 builds the foundation: a working distributed
KV store from scratch. The goal is not production-
ready code - it is code that works correctly enough
to illuminate the fundamental challenges and design
choices that every real distributed KV store faces.

---

### 📘 What We Build in Phase 1

**Phase 1 targets:**
1. Single-node in-memory KV store with HTTP API
2. Consistent hashing to partition keys across nodes
3. Basic replication (write to N replicas, read from 1)

**Phase 2** (DST-073) adds: gossip-based failure
detection, vector clocks for conflict resolution,
anti-entropy reconciliation.

**Phase 3** (DST-089) adds: Raft consensus for
leader election, linearizable reads, production
hardening.

---

### ⏱️ Understand It in 30 Seconds

```
PHASE 1 ARCHITECTURE:

  Client
    |
    v
  Node A (port 8001)  Node B (port 8002)  Node C (port
    8003)
    |                    |                    |
  Consistent Hash Ring (keys partitioned by hash)
    |
  Replication: write to primary + 1 replica

GET "user:123":
  1. Client sends to Node A
  2. Node A hashes "user:123" → belongs to Node B
  3. Node A forwards to Node B
  4. Node B returns value

PUT "user:123" = "{name:Alice}":
  1. Client sends to Node A
  2. Node A hashes "user:123" → primary = Node B
  3. Node A forwards to Node B (primary)
  4. Node B writes + replicates to Node C (1 replica)
  5. Node B returns success when N=2 writes confirmed
```

---

### 🔩 Step-by-Step Build

**STEP 1: Single-Node KV Store**

```python
# kv_node.py - Single-node KV store with HTTP API

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import sys
from urllib.parse import urlparse, parse_qs

class KVStore:
    """Thread-safe in-memory key-value store."""

    def __init__(self):
        self._store: dict[str, str] = {}
        self._lock = threading.RWLock() if hasattr(
            threading, 'RWLock'
        ) else threading.Lock()

    def get(self, key: str) -> str | None:
        with self._lock:
            return self._store.get(key)

    def put(self, key: str, value: str) -> None:
        with self._lock:
            self._store[key] = value

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._store.keys())


class KVHandler(BaseHTTPRequestHandler):
    """HTTP handler for KV operations."""

    def __init__(self, kv_store: KVStore, *args, **kwargs):
        self.kv = kv_store
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/kv/"):
            key = parsed.path[4:]
            value = self.kv.get(key)
            if value is not None:
                self._respond(200, {"key": key, "value": value})
            else:
                self._respond(404, {"error": "key not found"})
        else:
            self._respond(404, {"error": "unknown path"})

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/kv/"):
            key = parsed.path[4:]
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            self.kv.put(key, data["value"])
            self._respond(200, {"status": "ok"})
        else:
            self._respond(404, {"error": "unknown path"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/kv/"):
            key = parsed.path[4:]
            deleted = self.kv.delete(key)
            status = 200 if deleted else 404
            self._respond(status, {"deleted": deleted})

    def _respond(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Silence default access log
```

**STEP 2: Consistent Hashing Ring**

```python
# consistent_hash.py - Consistent hashing ring

import hashlib
import bisect

class ConsistentHashRing:
    """
    Consistent hash ring for key-to-node mapping.
    Uses virtual nodes (vnodes) for even distribution.
    """

    def __init__(
        self,
        nodes: list[str],
        vnodes_per_node: int = 150
    ):
        self.vnodes_per_node = vnodes_per_node
        self._ring: dict[int, str] = {}   # hash → node
        self._sorted_keys: list[int] = []  # sorted hashes
        for node in nodes:
            self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(
            hashlib.md5(key.encode()).hexdigest(), 16
        )

    def add_node(self, node: str) -> None:
        """Add a node with its virtual replicas."""
        for i in range(self.vnodes_per_node):
            vnode_key = f"{node}:vnode:{i}"
            h = self._hash(vnode_key)
            self._ring[h] = node
            bisect.insort(self._sorted_keys, h)

    def remove_node(self, node: str) -> None:
        """Remove a node and its virtual replicas."""
        for i in range(self.vnodes_per_node):
            vnode_key = f"{node}:vnode:{i}"
            h = self._hash(vnode_key)
            if h in self._ring:
                del self._ring[h]
                self._sorted_keys.remove(h)

    def get_node(self, key: str) -> str:
        """Get the primary node for a key."""
        if not self._ring:
            raise ValueError("No nodes in ring")
        h = self._hash(key)
        idx = bisect.bisect(self._sorted_keys, h)
        if idx == len(self._sorted_keys):
            idx = 0  # Wrap around
        return self._ring[self._sorted_keys[idx]]

    def get_nodes(self, key: str, n: int) -> list[str]:
        """
        Get n distinct nodes for a key.
        First is primary; rest are replicas.
        """
        if not self._ring:
            raise ValueError("No nodes in ring")
        h = self._hash(key)
        idx = bisect.bisect(self._sorted_keys, h)
        nodes = []
        seen = set()
        for i in range(len(self._sorted_keys)):
            pos = (idx + i) % len(self._sorted_keys)
            node = self._ring[self._sorted_keys[pos]]
            if node not in seen:
                nodes.append(node)
                seen.add(node)
            if len(nodes) == n:
                break
        return nodes

# Test distribution:
ring = ConsistentHashRing(
    ["node-1:8001", "node-2:8002", "node-3:8003"]
)
distribution = {"node-1:8001": 0,
                "node-2:8002": 0,
                "node-3:8003": 0}
for i in range(10000):
    node = ring.get_node(f"key:{i}")
    distribution[node] += 1

print("Key distribution:")
for node, count in distribution.items():
    print(f"  {node}: {count} keys ({count/100:.1f}%)")
# Should be roughly: 33% / 33% / 33%
# Without vnodes: very uneven. With 150 vnodes: ~33% each
```

**STEP 3: Distributed Node with Routing and Replication**

```python
# distributed_kv_node.py - Full distributed node

import httpx
from functools import partial

class DistributedKVNode:
    """
    A distributed KV store node that:
    1. Routes requests to the correct primary node
    2. Replicates writes to N nodes
    3. Forwards reads to primary if not local
    """

    def __init__(
        self,
        node_id: str,
        all_nodes: list[str],
        replication_factor: int = 2
    ):
        self.node_id = node_id
        self.local_store = KVStore()
        self.ring = ConsistentHashRing(all_nodes)
        self.all_nodes = all_nodes
        self.replication_factor = replication_factor

    def _is_local(self, key: str) -> bool:
        """True if this node is the primary for key."""
        return self.ring.get_node(key) == self.node_id

    def _get_replicas(self, key: str) -> list[str]:
        """Get all nodes responsible for key."""
        return self.ring.get_nodes(
            key, self.replication_factor
        )

    def get(self, key: str) -> str | None:
        """Get value. Route to primary if not local."""
        if self._is_local(key):
            return self.local_store.get(key)

        # Forward to primary node:
        primary = self.ring.get_node(key)
        try:
            response = httpx.get(
                f"http://{primary}/kv/{key}",
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()["value"]
            return None
        except httpx.RequestError:
            # Primary unreachable: try replicas
            for replica in self._get_replicas(key)[1:]:
                try:
                    response = httpx.get(
                        f"http://{replica}/kv/{key}",
                        timeout=2.0
                    )
                    if response.status_code == 200:
                        return response.json()["value"]
                except httpx.RequestError:
                    continue
            return None  # All replicas unreachable

    def put(self, key: str, value: str) -> bool:
        """
        Write to all replicas. Returns True if at least
        W=replication_factor writes succeed.
        """
        replicas = self._get_replicas(key)
        successes = 0

        for node in replicas:
            if node == self.node_id:
                # Local write:
                self.local_store.put(key, value)
                successes += 1
            else:
                # Remote write (replication):
                try:
                    response = httpx.put(
                        f"http://{node}/kv/{key}",
                        json={"value": value},
                        timeout=2.0
                    )
                    if response.status_code == 200:
                        successes += 1
                except httpx.RequestError:
                    pass  # Replica unavailable

        # Return True if quorum writes succeeded:
        required = (self.replication_factor // 2) + 1
        return successes >= required
```

---

### 🧠 Mental Model / Analogy

> Phase 1 is like building a small post office
> network. Step 1: one post office that sorts and
> stores letters. Step 2: three post offices; when
> a letter arrives, a consistent rule (hash of address)
> determines which office handles it. A letter for
> "Alice Street" always goes to Office B, not randomly.
> Step 3: each post office sends a copy to a backup
> office - if Office B burns down, its backup can
> still deliver Alice's letters. This is: partitioning
> (different keys to different offices) + replication
> (copies for fault tolerance). The hash ring is the
> "sorting rule" that every office agrees on.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What we're building:**
A distributed key-value store where data is spread
across multiple nodes and each key has N copies.
The goal: one node can fail without losing data.

**Level 2 - Why consistent hashing:**
Random distribution would require a lookup table
(which node has which key). Consistent hashing
provides a formula: hash the key, find the position
on the ring, the next node clockwise is the primary.
Any node can independently compute where any key
lives - no coordination required.

**Level 3 - Replication factor and write quorum:**
With replication_factor=2, each key lives on 2 nodes.
A write succeeds if at least W=1 node confirms.
But: if W=1 and the primary returns success before
replicating to the second node, and then crashes,
the data is on 0 nodes. Better: W=2 (both must
confirm) or use async replication with an WAL.
Phase 1 uses synchronous replication (W=N) for
simplicity.

**Level 4 - What Phase 1 does NOT handle:**
Node failure detection (how does the ring know
a node is down?), conflict resolution (what if
two nodes have different values for the same key
after a partition?), rebalancing when a node is
added. These are Phase 2 and 3 additions. Phase 1
is deliberately minimal.

**Level 5 - How this maps to DynamoDB:**
Amazon DynamoDB uses consistent hashing for
partitioning (though on virtual partitions managed
by the control plane, not a simple ring). It uses
a replication factor of 3 (data lives on 3 storage
nodes). Write quorum W=2, read quorum R=2, giving
eventual consistency with W+R > N (strongly consistent
when W+R > replica count). Phase 1's design mirrors
this core structure.

---

### 💻 Code Example

**Running a 3-Node Cluster (Integration Test)**

```python
# test_cluster.py - Test Phase 1 KV cluster

import subprocess
import time
import httpx
import pytest

def start_cluster():
    """Start 3 KV nodes as subprocesses."""
    nodes = []
    for port in [8001, 8002, 8003]:
        proc = subprocess.Popen(
            ["python3", "kv_node.py",
             "--port", str(port),
             "--peers", "localhost:8001",
                        "localhost:8002",
                        "localhost:8003"],
            stdout=subprocess.PIPE
        )
        nodes.append(proc)
    time.sleep(1)  # Let nodes start
    return nodes

def stop_cluster(nodes):
    for node in nodes:
        node.terminate()

@pytest.fixture(scope="module")
def cluster():
    nodes = start_cluster()
    yield nodes
    stop_cluster(nodes)

def test_basic_put_get(cluster):
    """Writes to any node should be readable from any node."""
    # Write to node 1:
    r = httpx.put(
        "http://localhost:8001/kv/user:alice",
        json={"value": '{"name":"Alice"}'}
    )
    assert r.status_code == 200

    # Read from node 3 (may be on a different node):
    r = httpx.get("http://localhost:8003/kv/user:alice")
    assert r.status_code == 200
    assert r.json()["value"] == '{"name":"Alice"}'

def test_node_failure_tolerance(cluster):
    """Data readable after primary node dies."""
    # Write to node 1:
    httpx.put(
        "http://localhost:8001/kv/critical:data",
        json={"value": "must-survive"}
    )

    # Kill the primary for this key:
    primary = get_primary_node("critical:data")
    kill_node(cluster, primary)
    time.sleep(0.5)

    # Read from a different node:
    for port in [8001, 8002, 8003]:
        if port != primary:
            r = httpx.get(
                f"http://localhost:{port}/kv/critical:data"
            )
            if r.status_code == 200:
                assert r.json()["value"] == "must-survive"
                return

    pytest.fail("Data lost after primary failure")

def test_consistent_hash_distribution(cluster):
    """Keys should be roughly evenly distributed."""
    # Write 1000 keys:
    for i in range(1000):
        httpx.put(
            f"http://localhost:8001/kv/key:{i}",
            json={"value": f"value:{i}"}
        )

    # Check distribution:
    counts = {}
    for port in [8001, 8002, 8003]:
        r = httpx.get(f"http://localhost:{port}/kv/_keys")
        keys = r.json()["keys"]
        counts[port] = len(keys)

    # Each node should have roughly 33% of 1000 keys:
    # (with replication_factor=2: up to 66% including replicas)
    for port, count in counts.items():
        assert 200 < count < 800, (
            f"Node {port} has {count} keys: "
            f"expected 200-800 for balanced distribution"
        )
```

---

### ⚖️ Comparison Table

| Feature | Phase 1 (This) | Phase 2 | Phase 3 |
|---|---|---|---|
| **Partitioning** | Consistent hashing | + Rebalancing | + Raft-managed |
| **Replication** | Synchronous, all replicas | + Async + anti-entropy | + Raft log |
| **Failure detection** | None | Gossip protocol | Raft heartbeat |
| **Consistency** | Eventual | Causal (vector clocks) | Linearizable |
| **Conflict resolution** | Last-write-wins | Vector clock merge | Raft: no conflict |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Consistent hashing is complicated" | The algorithm is ~30 lines of Python. The concept (virtual nodes on a ring) is more complex than the code. Virtual nodes are the key insight - without them, distribution is severely uneven. |
| "Phase 1 is already a real distributed database" | Phase 1 has no failure detection (it doesn't know when a node goes down), no conflict resolution (two concurrent writes to the same key on different nodes may produce split-brain), and no durability (data is in-memory only). It is a learning exercise, not production software. |
| "Synchronous replication is always better" | Synchronous replication (Phase 1) provides stronger durability at the cost of latency: every write waits for all replicas to confirm. Asynchronous replication (Phase 2+) is faster but risks losing writes if the primary fails before replication completes. |
| "Consistent hashing eliminates hot spots" | Virtual nodes reduce hot spots significantly but do not eliminate them. A key that is written by millions of users per second (celebrity tweet, trending product) is a hot spot regardless of partitioning strategy. These require application-level caching or fan-out strategies. |

---

### 🚨 Failure Modes & Diagnosis

**Uneven Key Distribution Despite Consistent Hashing**

**Symptom:** After adding 10,000 keys, one node holds
60% of keys and another holds 15%. Requests to the
first node are slow; the other two are idle.

**Root Cause:** Too few virtual nodes per physical
node. With the default Python hash and <50 vnodes
per node, statistical variance creates highly uneven
distribution.

**Diagnosis:**
```python
def analyze_distribution(ring: ConsistentHashRing,
                          num_keys: int = 10000) -> None:
    counts: dict[str, int] = {
        node: 0 for node in set(ring._ring.values())
    }
    for i in range(num_keys):
        node = ring.get_node(f"key:{i}")
        counts[node] += 1

    total = sum(counts.values())
    print(f"Distribution across {total} keys:")
    for node, count in sorted(counts.items()):
        pct = count / total * 100
        bar = "=" * int(pct / 2)
        print(f"  {node}: {count:5d} ({pct:5.1f}%) {bar}")

    # Ideal: (100 / num_nodes)% per node
    # If any node deviates by >20%: increase vnodes

# Fix: increase vnodes_per_node:
# ring = ConsistentHashRing(nodes, vnodes_per_node=150)
# With 150 vnodes: typically within 5% of ideal distribution
```

**Fix:** Increase `vnodes_per_node` from 10 to 150.
This increases memory usage proportionally (150x more
ring entries) but gives near-uniform distribution.
Production systems (Cassandra: 256 vnodes per node
by default) use high vnode counts.

---

### 🔗 Related Keywords

**Prerequisites:** `Sharding and Partitioning`
(DST-011), `Replication` (DST-012),
`Consistent Hashing` (DST-016)

**Builds On This:** `Build KV Store Phase 2` (DST-073),
`Build KV Store Phase 3` (DST-089)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1    │ Single node → 3-node cluster              │
│ BUILDING   │ HTTP API + Consistent Hash + Replication  │
├────────────┼────────────────────────────────────────────┤
│ CONSISTENT │ hash(key) → position on ring              │
│ HASHING    │ 150 vnodes/node for even distribution     │
│            │ get_nodes(key, N) → primary + N-1 replicas│
├────────────┼────────────────────────────────────────────┤
│ REPLICATION│ Write to all replicas synchronously       │
│            │ Read from primary; fallback to replica    │
├────────────┼────────────────────────────────────────────┤
│ PHASE 1    │ No failure detection, no conflict resolve  │
│ LIMITS     │ In-memory only (no durability)            │
│ NEXT       │ Phase 2: gossip + vector clocks           │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Consistent hashing + replication:        │
│            │  partition the data, copy for safety."   │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Building a distributed KV store from scratch exposes
a lesson that reading about it cannot: every design
decision creates a new problem that requires another
design decision. Adding consistent hashing raises
the question of how many virtual nodes? Adding
replication raises the question of synchronous vs
asynchronous? Adding fault tolerance raises the
question of how to detect failure? Each feature you
add reveals the next layer of complexity. This
is the essential nature of distributed systems
engineering: there is no free lunch. Every property
you want (availability, consistency, durability,
performance) has a cost in terms of complexity,
coordination, or latency. Building the system makes
this concrete and memorable in a way that no amount
of reading can achieve.

---

### 💡 The Surprising Truth

Amazon DynamoDB, one of the most reliable distributed
databases in the world, has its architectural roots
in a simple insight described in the Amazon Dynamo
paper (2007): consistent hashing + vector clocks +
gossip-based failure detection. The paper describes
exactly what Phase 1, 2, and 3 of this lab builds -
in rough form. The production DynamoDB is, of course,
far more sophisticated. But the fundamental algorithm
you implement in this lab is the same one powering
a database that serves trillions of requests per day.
Building it yourself is the most direct way to
understand why those design choices were made and
what problems they solve.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Build the single-node KV store with
   GET, PUT, DELETE via HTTP. Write unit tests for
   the thread-safe KVStore class.
2. [IMPLEMENT] Build the ConsistentHashRing. Verify
   uniform distribution with 150 vnodes by testing
   10,000 keys and checking no node has >45% or
   <20% of keys.
3. [IMPLEMENT] Add replication: when a key is written,
   write it to get_nodes(key, 2). Verify with a test
   that data is readable after killing the primary.
4. [OBSERVE] Write to node 1 with a key that hashes
   to node 3. Add logging to trace the routing.
   Verify the PUT reaches node 3 and is readable from
   node 2 (via replication).
5. [EXTEND] Add a /kv/_keys endpoint to each node
   that returns all keys stored locally. Write a test
   that verifies distribution is within 20% of ideal
   after 10,000 writes.
