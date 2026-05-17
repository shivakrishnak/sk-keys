---
id: SYD-013
title: Session Affinity
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008, SYD-012
used_by: ""
related: SYD-008, SYD-011, SYD-012, SYD-014
tags:
  - architecture
  - networking
  - stateful-design
  - load-balancing
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /syd/session-affinity/
---

# SYD-013 - Session Affinity

⚡ TL;DR - Session affinity is the general concept of
routing requests from the same client to the same
backend server. Sticky sessions (cookie-based) is
one implementation. Understanding when affinity is
legitimately needed vs when it is masking bad design
is the key engineering judgment.

| #013 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Sticky Sessions | |
| **Used by:** | (none - builds on SYD-012) | |
| **Related:** | Load Balancing, Consistent Hashing, Sticky Sessions, Auto Scaling | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A stateful real-time application (WebSocket server,
video call session) must maintain an open connection
between a specific client and a specific server for
the duration of the session. The load balancer's
round-robin algorithm would route the first WebSocket
upgrade request to Server A, then the next message
from the same client to Server B. Server B has no
active connection. The WebSocket dies.

**THE POINT:**
Some workloads genuinely require client-to-server
affinity, not because of in-process state that should
be externalized, but because the protocol itself
requires a persistent connection to the same server
(WebSocket, long-polling, gRPC streaming). Session
affinity for these cases is architecturally correct,
not a workaround.

**DISTINGUISHING LEGITIMATE vs WORKAROUND AFFINITY:**
- **Legitimate:** WebSocket/SSE connections (protocol
  requires persistent connection to same server);
  GPU-accelerated sessions (GPU context is server-local);
  local in-memory computation caches where re-warming
  is expensive and data changes slowly.
- **Workaround:** HTTP session data stored in-process;
  in-memory counters or aggregations; uploaded files
  on local disk.

---

### 📘 Textbook Definition

Session affinity (also called client affinity, server
affinity, or persistence) is the property of a routing
system that routes requests from a specific client
or session to a specific backend server consistently
across multiple requests. Session affinity can be
implemented via cookies (sticky sessions), source IP
hashing, URL parameters, consistent hashing on a
session identifier, or transport-layer connection
persistence. Unlike sticky sessions (which specifically
refers to cookie-based LB persistence), session affinity
describes the desired behavior rather than the
implementation mechanism.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Session affinity means a client consistently reaches
the same server, by whatever mechanism achieves that.

**One analogy:**
> A doctor's appointment system where you always see
> your assigned GP (your "regular doctor"), not
> whoever happens to be available. The mechanism
> might be an appointment book (cookie), your patient
> record linking to a GP (consistent hashing), or
> simply calling your GP's direct line (persistent
> connection).

**One insight:**
Session affinity is the requirement. Sticky sessions,
consistent hashing on session ID, and persistent
connections are all implementations. Understanding
the requirement lets you choose the right implementation
for the constraint.

---

### 🔩 First Principles Explanation

**WHEN SESSION AFFINITY IS ARCHITECTURALLY REQUIRED:**

```
┌─────────────────────────────────────────────────────┐
│ LEGITIMATE AFFINITY REQUIREMENTS                    │
│                                                     │
│ WebSocket / SSE                                     │
│   Client opens persistent TCP connection.           │
│   Server holds connection state (subscriber list,   │
│   message buffer). Protocol breaks if routed        │
│   to different server mid-connection.               │
│   Solution: route upgrade request to stable server  │
│   via LB hash; maintain connection for session      │
│   lifetime.                                         │
│                                                     │
│ GPU/ML Inference Sessions                           │
│   GPU model is loaded into VRAM. Re-loading costs   │
│   2-10 seconds. Routing to same GPU server avoids   │
│   reload on every inference request.                │
│   Solution: consistent hashing on user/model ID.   │
│                                                     │
│ Local Cache Warming                                 │
│   Application has expensive in-memory precomputed   │
│   state (e.g., recommendation model loaded for a   │
│   tenant). Routing same tenant to same server       │
│   avoids re-loading the model on every request.     │
│   Solution: consistent hashing on tenant ID.        │
└─────────────────────────────────────────────────────┘
```

**IMPLEMENTATION METHODS COMPARISON:**

```
┌─────────────────────────────────────────────────────┐
│ IMPLEMENTATION  │ MECHANISM  │ FAILURE BEHAVIOR     │
├─────────────────┼────────────┼──────────────────────┤
│ Cookie (sticky) │ LB inserts │ Session lost on       │
│                 │ cookie     │ server failure        │
├─────────────────┼────────────┼──────────────────────┤
│ Source IP hash  │ hash(IP)%N │ Changes when client   │
│                 │            │ IP changes (mobile)   │
├─────────────────┼────────────┼──────────────────────┤
│ Consistent hash │ hash(key)  │ ~1/N affected on      │
│ on session ID   │ → ring     │ node change           │
├─────────────────┼────────────┼──────────────────────┤
│ Persistent TCP  │ Protocol   │ Reconnect to any      │
│ connection      │ level      │ server on failure     │
└─────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Protocol compliance for connection-oriented
workloads; local state reuse for expensive-to-reload
data; reduced coordination overhead for request
processing that benefits from server-local context.
**Cost:** Uneven load distribution; harder auto-scaling
(must drain affined sessions before removing server);
session loss on server failure (for cookie/IP-hash
implementations); more complex routing logic.

---

### 🧠 Mental Model / Analogy

> Session affinity is like customer segmentation at
> a bank. High-value customers are always routed to
> their assigned relationship manager (affinity).
> Regular transactions go to any available teller
> (no affinity). The distinction is made at the
> routing layer based on customer tier.

The key judgment: is routing to a specific server
(1) required by the protocol/architecture, or
(2) a compensation for stateful design that should
be fixed? Answer that correctly and the implementation
choice follows.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Making sure a user's requests always go to the same
server, using one of several techniques to identify
"this user should go to server B."

**Level 2 - How to use it (junior developer):**
In Kubernetes: use `sessionAffinity: ClientIP` in
the Service spec. In AWS ALB: enable stickiness on
the target group. In nginx upstream: use `ip_hash`
or `least_conn` + consistent hash module.

**Level 3 - How it works (mid-level engineer):**
The routing layer maintains a mapping from client
identifier (cookie value, IP, session ID) to backend.
For cookie-based: the map is encoded in the cookie
(stateless LB). For IP-hash: the mapping is computed
from the hash each time. For consistent hashing: the
ring serves as the mapping structure.

**Level 4 - Why it was designed this way (senior/staff):**
The choice between sticky sessions and consistent
hashing on session ID matters for resilience.
Cookie-based: simple, but the cookie ties a client
to one specific server. If that server disappears,
the LB cannot gracefully reroute (the cookie names
a dead server). Consistent hashing: the ring maps
session ID to the "nearest" server, so if a server
is removed, the session ID maps to the next server
(graceful failover). For systems requiring session
affinity, consistent hashing is more resilient than
simple cookie-based sticky sessions.

**Level 5 - Mastery (distinguished engineer):**
The WebSocket routing problem at scale is non-trivial.
A WebSocket connection is long-lived (minutes to hours).
As the server pool changes (auto-scaling events),
existing connections must stay on their current server
(mid-connection rerouting is impossible). New connections
should go to the least-loaded server. This requires
maintaining both stable affinity (for existing
connections) and load-aware routing (for new connections)
simultaneously. Solutions: consistent hashing for
initial connection assignment, then persistent connection
to that server for the lifetime of the WebSocket.
Connection state replication across servers (via Redis
pub/sub or similar) enables transparent failover even
for WebSocket connections when the server goes down.

---

### ⚙️ How It Works (Mechanism)

**Kubernetes service affinity:**

```yaml
# GOOD: Session affinity for WebSocket/stateful service
apiVersion: v1
kind: Service
metadata:
  name: websocket-service
spec:
  selector:
    app: websocket-server
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

**WebSocket routing with consistent hashing (nginx):**
```nginx
# GOOD: Consistent hashing on session ID for WS
upstream websocket_backend {
    hash $cookie_session_id consistent;
    server ws1.internal:8080;
    server ws2.internal:8080;
    server ws3.internal:8080;
    keepalive 100;
}

server {
    listen 80;
    location /ws {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
    }
}
```

---

### 💻 Code Example

**Example 1 - WebSocket with affinity: correct vs wrong**
```java
// BAD: WebSocket server stores connection state locally
// with round-robin LB → sessions die on rerouting
@Component
public class ChatServer {
    // Local - dies when LB routes to different server
    private final Map<String, WebSocketSession>
        activeSessions = new ConcurrentHashMap<>();

    @OnOpen
    public void onOpen(Session session) {
        activeSessions.put(session.getId(), session);
    }

    public void broadcast(String roomId, String msg) {
        // WRONG: Only clients on THIS server get message
        // Clients on other servers don't exist here
        activeSessions.values().stream()
            .filter(s -> s.getRoom().equals(roomId))
            .forEach(s -> s.sendText(msg));
    }
}

// GOOD: Session affinity + cross-server pub/sub
// LB: consistent hash on room_id (all room members
// go to same server). Pub/sub handles cross-server.
@Component
public class ChatServer {
    private final Map<String, WebSocketSession>
        localSessions = new ConcurrentHashMap<>();
    private final RedisTemplate<String, String> redis;

    @OnOpen
    public void onOpen(Session session) {
        localSessions.put(session.getId(), session);
        // Subscribe to room events for this connection
        redis.opsForList().rightPush(
            "room:" + session.getRoomId(),
            session.getServerId()
        );
    }

    public void broadcast(String roomId, String msg) {
        // Publish to Redis: all servers subscribed
        // to this room will receive and forward to
        // their local WebSocket connections
        redis.convertAndSend("room:" + roomId, msg);
    }
}
```

**Example 2 - Graceful reconnect after server failure**
```javascript
// Client-side WebSocket with reconnect logic
// Handles server failure gracefully even with affinity
class ResilientWebSocket {
    constructor(url) {
        this.url = url;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);
        this.ws.onclose = (event) => {
            if (!event.wasClean) {
                // Server failure: reconnect after delay
                // Load balancer will route to healthy server
                // New server may not have our session:
                // must re-authenticate
                setTimeout(() => {
                    this.reconnectDelay = Math.min(
                        this.reconnectDelay * 2,
                        this.maxReconnectDelay
                    );
                    this.connect();
                    this.authenticate(); // re-auth needed
                }, this.reconnectDelay);
            }
        };
    }
}
```

---

### ⚖️ Comparison Table

| Scenario | Affinity Needed? | Best Implementation |
|---|---|---|
| HTTP API (stateless) | No - remove if present | None; round-robin |
| In-process HTTP session | No - fix the root cause | Redis sessions |
| WebSocket connections | Yes - protocol requires it | Consistent hash on room/user ID |
| ML inference (GPU) | Yes - re-load cost | Consistent hash on model/user ID |
| Tenant-specific local cache | Maybe - measure re-warm cost | Consistent hash on tenant ID |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Session affinity and sticky sessions are synonyms | Sticky sessions is a specific LB implementation (cookie-based). Session affinity is the general requirement that can be met by cookies, IP hash, consistent hashing, or protocol-level persistent connections. |
| Session affinity always causes uneven load | Consistent hashing-based affinity distributes load relatively evenly (each server gets ~1/N of sessions). Cookie-based stickiness can cause hot servers if sessions are long-lived and traffic is bursty. |
| You must choose between affinity and high availability | With consistent hashing on session ID, server failures cause ~1/N of sessions to reroute to different servers, which is graceful. Sticky sessions are the "all-or-nothing" failure mode version. |

---

### 🚨 Failure Modes & Diagnosis

**Auto-Scaling Race Condition**

**Symptom:**
During a traffic spike, auto-scaling adds 4 new servers.
But all new connections continue routing to existing
servers (due to IP hash not redistributing). New
servers sit idle. Existing servers remain overloaded.

**Root Cause:**
IP hash is computed as `hash(client_IP) % N`. Adding
servers increases N, but for most client IPs, the
hash still resolves to one of the original N servers.
New servers only receive traffic from client IPs
that newly hash to them - a small fraction.

**Diagnostic:**
```bash
# Check per-server request rate vs total
# AWS ALB: RequestCountPerTarget metric
# High variance = IP hash causing hot servers
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCountPerTarget \
  --dimensions Name=TargetGroup,Value=... \
  --period 60 --statistics Sum ...
# If some targets have 3x others: hot server problem
```

**Fix:**
Replace IP hash with consistent hashing on session ID.
Or (better) remove affinity entirely by externalizing
session state and using least-connections.

**Prevention:**
Benchmark auto-scaling behavior before production.
Specifically test: add a new server and verify it
receives proportional traffic within 60 seconds.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - session affinity is a routing
  property of load balancers
- `Sticky Sessions` - the most common implementation;
  understand it before the broader concept

**Builds On This (learn these next):**
- `Auto Scaling` - session affinity complicates
  auto-scaling; understand the interaction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Routing requests from the same client     │
│              │ to the same server, by any mechanism      │
├──────────────┼───────────────────────────────────────────┤
│ KEY QUESTION │ Is this affinity REQUIRED by the protocol │
│              │ (WebSocket, GPU context) or masking bad   │
│              │ design (in-process sessions)?             │
├──────────────┼───────────────────────────────────────────┤
│ LEGITIMATE   │ WebSocket connections; GPU inference;     │
│ USE CASES    │ expensive-to-reload local caches          │
├──────────────┼───────────────────────────────────────────┤
│ WORKAROUND   │ In-process session storage for HTTP APIs; │
│ USE CASES    │ local file uploads; in-process counters   │
├──────────────┼───────────────────────────────────────────┤
│ BETTER IMPL  │ Consistent hash on session ID >           │
│              │ cookie sticky > IP hash                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Session affinity: route same client to   │
│              │  same server. Required for WebSockets.    │
│              │  A workaround for HTTP session state."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Auto Scaling → SLA/SLO/SLI               │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Session affinity is the requirement; sticky sessions
   (cookies), IP hash, consistent hashing are implementations.
2. Legitimate for connection-oriented protocols (WebSocket);
   a workaround for in-process HTTP session state.
3. Consistent hash on session ID is more resilient than
   cookie-based sticky sessions on server failure.

**Interview one-liner:**
"Session affinity routes requests from the same client
to the same backend server. It is legitimately required
for connection-oriented protocols like WebSocket. For
HTTP sessions, it is usually a workaround for in-process
state that should be externalized. The implementation
choices - cookie, IP hash, consistent hash - have
different failure characteristics, with consistent
hashing being most resilient."
