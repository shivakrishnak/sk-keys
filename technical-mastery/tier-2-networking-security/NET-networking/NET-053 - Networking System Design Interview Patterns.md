---
id: NET-053
title: "Networking System Design Interview Patterns"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-034, NET-043, NET-046
used_by: NET-067
related: NET-034, NET-043, NET-046, NET-067
tags:
  - networking
  - system-design
  - interviews
  - architecture
  - patterns
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/net/networking-system-design-interview-patterns/
---

**⚡ TL;DR** - System design interviews always involve
networking decisions. The patterns: load balancing
strategy (why least-connections for long-lived, consistent
hashing for stateful), connection protocol (why WebSocket
for chat, SSE for notifications, gRPC for internal),
DNS strategy (why short TTL during migrations), and
latency budget allocation (split 200ms across service
chain). This entry gives you the decision frameworks for
each networking question that comes up in design rounds.

| #053 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Networking Quick Recall Card (NET-034), DNS Resolution Deep Dive (NET-043), Load Balancing Algorithms (NET-046) | |
| **Used by:** | Networking Deep-Dive Interview Questions (NET-067) | |
| **Related:** | Networking Quick Recall Card, DNS Resolution Deep Dive, Load Balancing Algorithms, Networking Deep-Dive Interview Questions | |

---

### 🔥 The Interview Problem

System design rounds inevitably ask: "How would you
handle 10 million users?" or "Design a real-time chat
system." Every answer requires networking decisions:
layer 4 vs layer 7 LB, HTTP vs WebSocket, global traffic
routing, connection state management. Without networking
patterns, you give vague answers. With them, you explain
specific trade-offs and numbers.

---

### 🧠 Core Framework: Network Decision Tree for System Design

```
Any system design → answer these networking questions:

1. PROTOCOL: What communication pattern does each component need?
   Request-response (HTTP/REST/gRPC) vs streaming (WebSocket/SSE)

2. LOAD BALANCING: What distribution strategy?
   Stateless: round-robin or least-connections
   Stateful: consistent hashing or sticky sessions

3. ROUTING: How does traffic reach the right region/AZ?
   Single region: DNS + LB
   Multi-region: anycast, GeoDNS, global LB

4. CONNECTION: Long-lived or short-lived?
   Long-lived: WebSocket, gRPC streaming → need session affinity
   Short-lived: REST → easy to scale horizontally

5. LATENCY: What is the budget?
   End-to-end budget → allocate to each hop
   Where is the bottleneck likely?
```

---

### ⚙️ Pattern 1 - Protocol Selection

```
Protocol decision matrix:

USE HTTP/REST when:
  - CRUD operations, single request-response
  - Public APIs (standard, client-compatible)
  - Cacheable responses (CDN, browser cache)
  - Fire-and-forget webhooks (receiver retries on own schedule)

USE gRPC when:
  - Internal microservices (controlled clients)
  - High-throughput, low-latency (protobuf = smaller payload)
  - Streaming needed (server streaming, bidirectional)
  - Strong contract enforcement needed (.proto schema)
  Trade-off: binary protocol (harder to debug without tooling)

USE WebSocket when:
  - Client needs SERVER-INITIATED events in real time
  - Bidirectional, low-latency: chat, gaming, live collaboration
  - Client needs to SEND data as well as receive
  Downside: stateful - can't redistribute to any server
  Need: sticky sessions (ip_hash or cookie-based) at LB

USE SSE (Server-Sent Events) when:
  - Server pushes events to client (one direction only)
  - Live feed, notifications, dashboards
  - Client doesn't need to send messages
  Upside: works over HTTP/2, CDN-friendly, automatic reconnect
  Downside: client-to-server still needs separate REST call

USE long polling when:
  - Legacy browser support needed
  - Infrastructure doesn't support WebSocket
  Trade-off: connection overhead, server resource waste

Interview answer:
  Chat: WebSocket (bidirectional, real-time, both parties send)
  Stock ticker: SSE (server pushes, client reads only)
  Internal services: gRPC (performance, schema enforcement)
  Public API: REST (compatibility, caching, tooling)
```

---

### ⚙️ Pattern 2 - Load Balancing Strategy

```
Load balancing decision tree:

STATELESS services (REST API, most web services):
  Algorithm: Least-connections (best distribution)
  Alternative: Round-robin if all instances identical
  Why not random? Uneven distribution on variable request times
  Why not consistent hashing? Only needed for state

STATEFUL connections (WebSocket, gRPC streams):
  Algorithm: Consistent hashing on connection ID or user ID
  Alternative: ip_hash (nginx), but problems with NAT
  Why? Connection must return to same backend
  Problem: hot spots if user distribution is uneven
  Fix: virtual nodes in consistent hash ring

LONG-LIVED DATABASE connections:
  Algorithm: Least-connections (not round-robin)
  Why? Slow queries hold connections; round-robin ignores this
  Round-robin: new connections pile onto a node with a slow query
  Least-connections: avoids nodes with many open connections

CACHING layer (Redis/Memcached):
  Algorithm: Consistent hashing
  Why? Each key must go to the same shard
  Change: adding a node moves minimum keys (not all)

Session affinity (sticky sessions):
  When: stateful backend (session data not externalized)
  How: AWSALB cookie, nginx upstream_hash module
  Problem: failure of one backend loses all its sessions
  Better solution: externalize session to Redis → become stateless
```

---

### ⚙️ Pattern 3 - Global Traffic Routing

```
Single region:
  DNS → ELB/ALB/NGINX → multiple AZs
  Simplest, no cross-region latency
  Failure mode: entire region outage

Active-active multi-region:
  GeoDNS routes users to nearest region
  Each region is fully capable
  Data: conflict resolution needed (write conflicts)
  Best for: read-heavy workloads, static content

Active-passive multi-region (failover):
  Primary handles all traffic
  Standby region ready but not serving
  DNS TTL: short (60s) for fast failover
  RTO: DNS TTL + LB health check
  Best for: write-heavy, consistency-critical

Anycast routing:
  Single IP, multiple PoP locations
  Network routes to nearest PoP (BGP routing)
  Used by: Cloudflare, Google (8.8.8.8), Akamai
  Best for: DNS, CDN, DDoS mitigation

Interview example - Design a CDN:
  1. GeoDNS returns nearest edge PoP
  2. PoP checks local cache
  3. Cache miss: origin pull via HTTP
  4. Serve from PoP, cache with appropriate TTL
  5. Origin: single authoritative source
  6. TLS: terminate at edge PoP (nearest, lowest latency)
```

---

### ⚙️ Pattern 4 - Latency Budget Allocation

```
Interview: "Design a system with 200ms P99 latency budget"

Step 1: Identify all hops in the request path
  User → CDN/Edge → LB → Web Server → App Server → DB
  DNS: 5ms (cached), TLS: 20ms (TLS 1.3)

Step 2: Allocate budget to each hop
  CDN/Edge:  20ms  (TLS termination, edge processing)
  Network:   10ms  (speed of light, same region)
  LB:        5ms   (minimal overhead)
  App:       80ms  (business logic, caching)
  DB:        50ms  (indexed queries only)
  Network:   10ms  (return path)
  Margin:    25ms  (buffer for P99 vs P50 variance)
  Total:     200ms

Step 3: Identify where optimization is needed
  If DB is 50ms: need indexed queries, connection pooling
  If App is 80ms: need caching layer (Redis)
  If network is 20ms: need co-location or CDN

Key insight for interviewers: P99 ≠ P50 × 1.5
  Tail latency is often 5-10x median
  Budget should account for: GC pauses, cold starts,
  network jitter, head-of-line blocking

Real numbers to know:
  Same datacenter RTT: < 1ms
  Same cloud region (cross-AZ): 1-3ms
  Cross-region (US → EU): 80-100ms
  HDD seek time: ~10ms
  SSD seek time: 0.1ms
  Database indexed query: 1-10ms (warm cache)
  Uncached DB query: 50-500ms (depends on data size)
```

---

### ⚙️ Pattern 5 - Scale Transition Points

```
1K users:
  Single server
  Vertical scaling
  No LB needed yet

10K users:
  LB + 2-3 app servers
  Externalize sessions to Redis
  Database read replica for heavy read queries

100K users:
  CDN for static assets (removes ~70% origin load)
  Database connection pooling (PgBouncer/HikariCP)
  Caching layer (Redis)
  Multiple LB instances (active-passive or active-active)

1M users:
  Regional deployment (multiple DCs)
  GeoDNS for routing
  Database sharding or read replicas per region
  Async processing (message queues for heavy work)
  Rate limiting and backpressure

10M+ users:
  Global anycast (Cloudflare-style)
  Consistent hashing for stateful components
  Service mesh for observability and policies
  Multi-tier caching (edge, regional, local)
  Database: horizontally sharded, specialized per workload

Key insight: each scale-up is triggered by a bottleneck
  Common order: DB connections → app servers → LB → DB itself
```

---

### ⚙️ Pattern 6 - Connection Architecture for Real-Time Systems

```
Chat system networking architecture:

Users connected via WebSocket to Chat Servers
Chat Servers publish to Message Broker (Kafka/Redis Pub/Sub)
Message Broker fans out to all Chat Servers with subscriber
Chat Servers deliver to connected WebSocket clients

Load balancing for WebSocket:
  Problem: WebSocket is stateful (user A connected to server 1)
  If message for user A arrives at server 2 → miss!
  Solution 1: sticky sessions (ip_hash nginx)
    - Pro: simple
    - Con: uneven distribution, failover loses connection
  Solution 2: all servers subscribe to all messages
    - Pro: any server can deliver to any client
    - Con: fan-out overhead at high user count
  Solution 3: presence service maps user → server
    - Pro: targeted delivery, scales better
    - Con: additional hop, consistency complexity

Notification system (simpler than chat):
  Push: APNs (Apple), FCM (Google) - they maintain connection
  Web push: SSE or WebSocket
  Email/SMS: async queue → third-party service
  Fan-out: write to queue, notification workers consume
  At 10M users: 10M concurrent SSE connections
    → Need specialized push infrastructure (not web servers)
    → ~64K simultaneous connections per server (file descriptor limit)
    → 10M / 64K = ~160 servers just for notification delivery
```

---

### 🧭 Decision Guide

```
Interview question to pattern mapping:

"Design a real-time messaging system"
→ WebSocket protocol, sticky LB, pub/sub backend

"Design a notification service"  
→ SSE or push notifications, fan-out queue, APN/FCM

"Design a URL shortener"
→ REST API, consistent hashing for redirect servers,
  Redis for hot URLs, CDN for static landing pages

"Design a video streaming service"
→ CDN for segments (HLS/DASH), adaptive bitrate,
  anycast for edge delivery, TCP (reliability) for
  progressive download vs UDP for live streaming

"Design a stock trading platform"
→ gRPC streaming for market data, WebSocket for UI,
  co-location for lowest latency, UDP for market data

"Design an API gateway"
→ L7 LB, rate limiting per user, TLS termination,
  connection pooling to upstream, circuit breakers

Common networking mistakes in system design:
  Ignoring latency budget: "just add more servers"
  Wrong protocol: HTTP polling instead of WebSocket for chat
  Missing LB considerations for stateful services
  Forgetting TLS overhead: ~20ms for 1-RTT handshake
  Not mentioning CDN for static assets (first optimization)
  No mention of connection pooling to DB

Strong answer signals:
  Specific numbers (RTT, connection counts, file descriptors)
  Trade-off acknowledgment (sticky sessions vs complexity)
  Scale transition points (when to add LB, CDN, etc.)
  Failure mode awareness (what breaks at scale)
```