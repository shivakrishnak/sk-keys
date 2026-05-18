---
id: NET-046
title: "Load Balancing Algorithms"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-031
used_by: NET-055, NET-056
related: NET-031, NET-032, NET-055
tags:
  - networking
  - load-balancing
  - algorithms
  - round-robin
  - least-connections
  - consistent-hashing
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 46
permalink: /technical-mastery/net/load-balancing-algorithms/
---

**⚡ TL;DR** - Load balancing algorithms decide which
backend server handles each incoming request. Round-robin
works for uniform requests; least-connections handles
variable latency workloads; IP hash enables client
stickiness; consistent hashing (with virtual nodes) is
the standard for distributed caches and stateful sharding.
The wrong algorithm causes one backend to be 10x busier
than others while the rest idle. Understand the request
characteristics before choosing.

| #046 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Load Balancer Basics (NET-031) | |
| **Used by:** | Networking System Design Interview Patterns, HTTP Connection Management | |
| **Related:** | Load Balancer Basics, Reverse Proxy, Networking System Design | |

---

### 🔥 The Problem This Solves

A load balancer uses round-robin across 3 servers.
Server-1 handles quick API calls (5ms). Server-2 handles
file uploads (5s). Server-3 handles reports (30s).
Round-robin distributes requests equally, but Server-2
and Server-3 are overwhelmed while Server-1 is idle.
After 1 minute, Server-3 has a queue of thousands.
Least-connections would have seen Server-1's low
connection count and directed most traffic there. The
algorithm choice directly determines resource utilization.

---

### ⚙️ Algorithm 1: Round Robin

```
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A (cycle repeats)

Simple implementation:
  index = (request_count) % num_backends
  
Weighted Round Robin:
  Server A weight=3, Server B weight=1, Server C weight=1
  Sequence: A, A, A, B, A, A, A, C, A, A, A, B, ...
  
  # Nginx: upstream with weights
  upstream backend {
    server 10.0.0.1 weight=3;
    server 10.0.0.2 weight=1;
    server 10.0.0.3 weight=1;
  }

When to use:
  + Requests have similar duration (stateless API)
  + All servers have similar capacity
  + Simplest to configure and debug
  
When NOT to use:
  - Variable request duration (file uploads, reports)
  - Heterogeneous server capacity
  - Stateful sessions (each request goes to random server)
```

---

### ⚙️ Algorithm 2: Least Connections

```
New request → server with fewest active connections

Why it works:
  Server with fewer connections = likely finishing faster
  Or has more capacity available

Active connections: in-flight requests the server is processing

Implementation:
  for each new request:
    backend = min(active_connections for each healthy backend)
    route request to backend

Variant: Weighted Least Connections
  Adjusted connections = active_connections / weight
  Server with weight=2 appears to have half as many connections
  → gets twice as many new requests
  
When to use:
  + Variable request duration (file processing, ML inference)
  + Mixed workloads (fast reads + slow writes on same pool)
  + Reliable for long-lived connections (WebSocket, gRPC streaming)
  
When NOT to use:
  - Very short requests (< 1ms): overhead of counting > benefit
  - State-based routing needed
```

---

### ⚙️ Algorithm 3: IP Hash (Client Stickiness)

```
hash(client_ip) % num_backends → always same backend

Property: same client IP always goes to same server
Use: sessions stored in-process (not in Redis)

# Nginx:
upstream backend {
    ip_hash;
    server 10.0.0.1;
    server 10.0.0.2;
    server 10.0.0.3;
}

Problem: Adding/removing servers changes ALL mappings
  3 servers → 4 servers: ~75% of clients remap to new server
  Their sessions are on old server → data loss / reauth
  
Problem: IPv6 or NAT hiding many clients behind one IP
  Office NAT: 1000 employees → 1 public IP → all go to Server A
  Server A overwhelmed, B and C idle

Better alternative: Cookie-based sticky sessions
  Load balancer sets a cookie with the backend server ID
  Subsequent requests: route based on cookie
  → Works with NAT (IP doesn't matter)
  → Predictable: adding servers doesn't remap existing clients

When to use:
  + Server-side session without external session store
  + Legacy apps that cannot externalize state
  
Prefer: externalize session to Redis → stateless backends
        → any algorithm works, no stickiness needed
```

---

### ⚙️ Algorithm 4: Consistent Hashing

```
Problem: IP hash remaps clients when servers are added/removed
  N servers → N+1 servers: ~N/(N+1) clients remap (expensive!)

Consistent hashing solution:
  Hash space: 0 to 2^32-1 (ring of numbers)
  Place servers at positions on ring: hash(server_id)
  Route request: hash(key) → find next server clockwise on ring
  
  When adding server:
    New server takes ~1/(N+1) of one neighboring server's load
    All other servers: unchanged
    Only ~1/N of keys remap (vs ~N/(N+1) without it!)

Virtual nodes:
  Problem: servers cluster unevenly on ring
  Solution: each server has K virtual nodes
    Server A has: hash("A-1"), hash("A-2"), ..., hash("A-K")
    Server B has: hash("B-1"), hash("B-2"), ..., hash("B-K")
  Result: more even distribution even with small server count

  k = virtual nodes
  Standard: k = 100-200 per physical server
```

```python
# Simplified consistent hashing implementation
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=150):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}-{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}-{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, request_key):
        if not self.ring:
            return None
        h = self._hash(request_key)
        idx = bisect.bisect(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

# Usage:
ch = ConsistentHash(nodes=['cache1', 'cache2', 'cache3'])
ch.get_node('user:12345')   # → 'cache2' (consistent)
ch.get_node('user:12345')   # → 'cache2' (same every time)

# Add a server: only ~1/N requests remap
ch.add_node('cache4')
ch.get_node('user:12345')   # → might still be 'cache2'
```

**Used by: Redis Cluster, Cassandra, DynamoDB, Kafka partition assignment**

---

### ⚙️ Algorithm 5: Random with Two Choices

```
Power of Two Choices algorithm:
  1. Pick 2 servers at random
  2. Send request to the one with fewer active connections

This sounds too simple but the math is profound:
  Pure random: max load = O(log N / log log N) with N servers
  Two choices: max load = O(log log N) - exponentially better
  
In practice:
  With 100 servers and pure random:
    Expected max load: ~7x average
  With two choices:
    Expected max load: ~1.7x average
  
  This is used by:
  - Netflix Zuul
  - Envoy Proxy
  - Twitter Finagle

# Implementation
def two_choices(backends):
    a = random.choice(backends)
    b = random.choice(backends)
    return a if a.active_connections <= b.active_connections else b
```

---

### ⚙️ Wrong vs Right: Round-Robin for ML Inference

```
# BAD: round-robin for GPU inference backends
# ML inference: 50-500ms per request (highly variable)
# Some models: 50ms (small), some: 500ms (large models)

upstream ml_backend {
    server gpu1:8080;   # handles all model sizes
    server gpu2:8080;
    server gpu3:8080;
}
# Result: a slow 500ms large-model request occupies GPU for
# 10× longer than a fast 50ms small-model request
# Round-robin gives each GPU the same number of requests
# GPU with 3 slow requests: 1,500ms queue
# GPU with 3 fast requests: 150ms queue
# → Large variance in user response times

# GOOD: least connections for variable-latency backends
upstream ml_backend {
    least_conn;  # route to GPU with fewest in-flight requests
    server gpu1:8080;
    server gpu2:8080;
    server gpu3:8080;
}
# GPUs get new requests only when they free up
# Slow GPUs get fewer new requests automatically
# Fast GPUs get more requests (natural load leveling)
```

---

### ⚙️ Health Checks and Algorithm Interaction

```
Health check: LB periodically probes each backend
  Active health check: LB probes GET /health every 5s
  Passive health check: LB watches error rates per backend

When a backend is unhealthy:
  All algorithms must skip it
  Consistent hashing: remove node, keys remap to neighbors
  Round-robin: skip in rotation
  Least-connections: skip (never route to unhealthy)

Gradual removal (drain mode):
  Mark backend as "draining" - no new connections routed
  Wait for active connections to finish
  Then remove from pool
  
  # nginx:
  upstream backend {
    server 10.0.0.1;
    server 10.0.0.2 down;   # exclude from LB
    server 10.0.0.3 drain;  # no new connections, wait for finish
  }

Health check response best practice:
  GET /health → 200 OK if healthy
  GET /health → 503 Service Unavailable if degraded
  Check: database reachability, dependency health
  NOT: just return 200 unconditionally (blind health check)
```

---

### ⚙️ Diagnosing Load Imbalance

```bash
# Check connection counts per backend (nginx upstream)
# nginx.conf: add status module
# location /nginx_status { stub_status on; }
curl http://lb:8080/nginx_status

# Better: use prometheus nginx exporter
# nginx_upstream_peers_active{upstream="backend",server="10.0.0.1"}
# Compare active connections across peers

# Application-level: log which backend handled request
# X-Served-By: 10.0.0.2:8080  ← custom response header
# Aggregate in Kibana/Splunk by backend server

# Quick check: request counts per backend in last 5 min
grep "upstream_addr" /var/log/nginx/access.log \
  | grep "$(date -d '5 minutes ago' '+%H:%M')" \
  | awk '{print $N}' | sort | uniq -c | sort -rn
# N = position of upstream_addr in log format

# Imbalance ratio: max_load / avg_load
# > 2x = significant imbalance, investigate algorithm choice
```

---

### 📐 Consistent Hashing at Scale

```
N=3 servers, K=150 virtual nodes each → 450 ring positions
Adding server N+1:
  1/4 of existing keys remap (to new server's virtual nodes)
  3/4 remain on same servers
  → Cache miss rate spike: ~25% (acceptable, brief)

Redis Cluster: 16,384 hash slots
  Slot = CRC16(key) % 16,384
  Each master node owns a range of slots
  Adding node: rebalance by migrating slots
  Migration is live (MIGRATE command)

Kafka partitioning:
  hash(key) % num_partitions → producer selects partition
  Consumer group: each partition to one consumer
  Adding partitions: old keys may remap → ordering guarantees lost
  → Don't add partitions to existing topics with keyed producers!
  → Create new topic, migrate consumers
```

---

### 🧭 Decision Guide

```
Request characteristics → algorithm choice:

All requests same duration AND same server capacity?
  → Round-robin (simplest)

Variable duration requests?
  → Least connections

Need client stickiness AND can use cookies?
  → Cookie-based sticky sessions (not IP hash)

Distributing keys across cache servers?
  → Consistent hashing with virtual nodes

Many backends, want to avoid hot-spot under load?
  → Power of Two Choices

Interview answer for "how does consistent hashing work":
  "Place servers on a ring by hashing their IDs.
  Route each key to the next server clockwise.
  Adding/removing a server only remaps ~1/N keys
  (vs full remap with simple hash mod N).
  Virtual nodes (K per server) ensure even distribution.
  Used by Redis Cluster, Cassandra, DynamoDB."
```