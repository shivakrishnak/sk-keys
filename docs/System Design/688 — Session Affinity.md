---
layout: default
title: "Session Affinity"
parent: "System Design"
nav_order: 688
permalink: /system-design/session-affinity/
number: "688"
category: System Design
difficulty: ★★☆
depends_on: "Load Balancing, Sticky Sessions"
used_by: "Horizontal Scaling"
tags: #intermediate, #distributed, #networking, #architecture, #pattern
---

# 688 — Session Affinity

`#intermediate` `#distributed` `#networking` `#architecture` `#pattern`

⚡ TL;DR — **Session Affinity** is the principle that a client's requests should reach the same server during a session; Sticky Sessions is one implementation — but external session stores remove the need entirely.

| #688 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Sticky Sessions | |
| **Used by:** | Horizontal Scaling | |

---

### 📘 Textbook Definition

**Session Affinity** is the architectural property that requests from the same client session are consistently directed to the same backend server or service instance. It is an umbrella concept that encompasses multiple implementation strategies: cookie-based persistence (Sticky Sessions), IP-hash routing, URL-based routing, application-level routing (e.g., user ID sharding), and consistent hashing by session token. Session Affinity exists on a spectrum: from hard affinity (requests MUST go to one server — all others return errors) to soft affinity (prefer same server, but can fall back to any server if needed, with re-authentication). Modern cloud-native architectures prefer eliminating session affinity requirements entirely by externalising session state to shared stores (Redis, Memcached, database), making all application instances stateless and freely interchangeable.

---

### 🟢 Simple Definition (Easy)

Session Affinity means "keep sending this user's requests to the same server." Sticky Sessions is one way to achieve it (the load balancer routes by cookie). But the better long-term approach is externalising session state so any server can handle any user — making session affinity unnecessary.

---

### 🔵 Simple Definition (Elaborated)

Session Affinity is the WHY. Sticky Sessions is one HOW. Other HOWs: consistent hashing by user ID, application-level routing to shards, JWT tokens (no server-side state needed). The goal is ensuring request continuity for stateful interactions. Architecturally: reduce your dependence on session affinity over time. Move session state out of servers and into shared stores. When all servers share state, session affinity is no longer needed — and you gain true horizontal scalability.

---

### 🔩 First Principles Explanation

**Session Affinity requirements and the statefulness spectrum:**

```
STATEFULNESS SPECTRUM (and affinity requirements):

  FULLY STATELESS (no session affinity needed):
    - REST API with JWT: token carries all state
    - GraphQL API: state in database, stateless compute
    - Static asset servers: HTML/CSS/JS, all identical
    
    All servers: identical, interchangeable.
    Load balancer: use any algorithm freely.
    Horizontal scaling: perfectly linear.
    
  SOFT SESSION AFFINITY (prefer same server, can re-initialize):
    - In-memory computation cache (CDN edge, computation results)
      Same server: cache hit → fast response
      Different server: cache miss → recompute → still works, just slower
      
    - Connection pools to specific shards (database routing):
      Same server: reuse existing DB connection pool
      Different server: create new pool → works, with connection overhead
      
    - Not using session affinity: safe but suboptimal (performance)
    - Using session affinity: performance optimization only
    
  HARD SESSION AFFINITY (broken without same server):
    - In-process HTTP sessions: Java HttpSession, PHP $_SESSION
      Without same server: "session not found" → authentication failure
      REQUIRES affinity to function at all
      
    - Long-lived WebSocket connections (stateful protocol):
      WebSocket connection established to Server A.
      Server A maintains connection state (user, subscription topics).
      All WebSocket messages for this client: MUST go to Server A.
      Different server: connection doesn't exist → error.
      
    - Conversational AI / multi-turn chat servers:
      Conversation context held in server memory.
      Different server: no context → broken conversation.
      
REMOVING HARD SESSION AFFINITY:

  Pattern 1: EXTERNALISE SESSION STATE
    Java: Spring Session + Redis
    @EnableRedisHttpSession  // sessions stored in Redis, not server RAM
    // Result: any server reads any session from Redis
    // Session affinity: no longer required
    
  Pattern 2: CLIENT-SIDE STATE (JWT, stateless tokens)
    JWT payload: { userId: 42, roles: ["admin"], exp: 1730000000 }
    Signed with server secret → tamper-proof
    Any server: verify signature → extract state → proceed
    No server-side storage → truly stateless
    
  Pattern 3: WEBSOCKET BACKPLANE (for WebSocket affinity)
    Redis Pub/Sub or Apache Kafka:
    Client → WebSocket → Server A → publishes to Redis channel
    Server B/C also subscribed → can relay messages to their clients
    
    // Socket.IO with Redis Adapter:
    const { createAdapter } = require("@socket.io/redis-adapter");
    const pubClient = createClient({ url: "redis://redis:6379" });
    const subClient = pubClient.duplicate();
    io.adapter(createAdapter(pubClient, subClient));
    // Now: any server can receive/publish messages for any client
    // WebSocket session affinity: no longer required for message routing
```

**Affinity by application routing vs load balancer routing:**

```
APPLICATION-LEVEL AFFINITY (sharding by user ID):
  Not a load balancer feature — baked into application routing.
  
  Example: multi-tenant SaaS, each tenant has a dedicated shard:
    tenantId "acme-corp" → always to Shard 3 (data isolation)
    tenantId "globex" → always to Shard 7
    
  Router service: routes based on tenant registry (database lookup).
  This is NOT sticky sessions — it's logical routing by business rule.
  
  Advantage: can be maintained across server restarts, deploys
  Disadvantage: hot tenant problem (one large tenant overloads shard)
  
LOAD BALANCER AFFINITY (sticky sessions):
  Transparent to application — LB handles routing.
  Session → Server mapping: stored in LB's memory.
  Application: unaware of which instance it's on.
  Problem: LB restart → all session bindings lost → everyone re-logs in.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Session Affinity (stateful app with server-side sessions):
- Requests from same user → different servers → broken session state
- User experience: random logouts, lost state, broken flows

WITH Session Affinity:
→ Session continuity preserved for stateful applications
→ Acts as a bridge while migrating to stateless architecture
→ Soft affinity: performance optimisation for cache-warm servers

---

### 🧠 Mental Model / Analogy

> A conversation with a new person at a company who doesn't have access to the shared CRM (customer records). You must speak to the SAME person every time, because only they remember your previous conversations. But if that company implements a shared CRM (shared session store), any employee can look up your history and help you — no need to always find the same person. Session Affinity = same person required. External session store = any employee can help.

"Same person" = same server instance
"Person's memory" = server-side session state
"Shared CRM" = external session store (Redis)
"Any employee can help" = stateless application servers

---

### ⚙️ How It Works (Mechanism)

**AWS ALB session affinity target group configuration:**

```yaml
# CloudFormation: ALB Target Group with session affinity
TargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Protocol: HTTP
    Port: 8080
    TargetType: instance
    TargetGroupAttributes:
      # Enable cookie-based stickiness:
      - Key: stickiness.enabled
        Value: "true"
      # ALB-generated cookie (AWSALB):
      - Key: stickiness.type
        Value: lb_cookie
      # Cookie duration: 1 day (matches application session TTL):
      - Key: stickiness.lb_cookie.duration_seconds
        Value: "86400"
      # Alternative: application-based cookie (reads app session cookie):
      # - Key: stickiness.type
      #   Value: app_cookie
      # - Key: stickiness.app_cookie.cookie_name
      #   Value: JSESSIONID
      # - Key: stickiness.app_cookie.duration_seconds
      #   Value: "3600"
```

---

### 🔄 How It Connects (Mini-Map)

```
Stateful HTTP Application
(server-side session state)
        │
        ▼ (requires affinity)
Session Affinity ◄──── (you are here)
(the principle: same server for same session)
        │
        ├── Sticky Sessions (load balancer implementation)
        ├── IP Hash (simpler but less reliable implementation)
        ├── Consistent Hashing by Session ID (scalable implementation)
        │
        ▼ (eliminating the need for affinity)
External Session Store (Redis/Memcached)
→ Stateless Servers
→ Horizontal Scaling (fully linear, no session constraints)
```

---

### 💻 Code Example

**Spring Session with Redis — removing session affinity requirement:**

```java
// Before: server-side sessions (requires sticky sessions)
@GetMapping("/profile")
public UserProfile getProfile(HttpSession session) {
    // session stored in THIS server's memory
    Long userId = (Long) session.getAttribute("userId");
    return userService.findById(userId);
}
// Problem: different server → no "userId" in its session memory

// After: Spring Session with Redis (no sticky sessions needed)
@Configuration
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 3600)
public class SessionConfig {
    // All HttpSession operations now use Redis transparently
    // session.setAttribute() → Redis SET
    // session.getAttribute() → Redis GET
    // Any server can access any session
}

@GetMapping("/profile")
public UserProfile getProfile(HttpSession session) {
    // session is now backed by Redis — any server has access
    Long userId = (Long) session.getAttribute("userId");
    return userService.findById(userId);
}
// Result: sticky sessions no longer required
//         any instance can handle any user's request
//         horizontal scaling: unlimited

// application.properties:
// spring.data.redis.host=redis.internal
// spring.data.redis.port=6379
// spring.session.store-type=redis
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Session Affinity and Sticky Sessions are the same thing | Sticky Sessions is one implementation of Session Affinity. Others include IP-hash routing, consistent hashing by session token, application-level sharding by user ID, and client-side state (JWT). Session Affinity is the principle; Sticky Sessions is a specific mechanism |
| All distributed applications need session affinity | Only applications with server-side state require it. REST/JSON APIs with JWT, GraphQL APIs, and static content servers are stateless and work fine without any session affinity |
| Removing session affinity always requires Redis | Redis is the most common external session store, but alternatives include: Memcached, database-backed sessions (slower), client-side JWT tokens (no external store needed), cookie-stored encrypted sessions (limited size) |
| Session affinity prevents horizontal scaling | Sticky sessions ENABLE horizontal scaling for stateful apps that would otherwise break. The real ceiling is uneven load (one server accumulates more sessions than others). Removing session affinity entirely (via external store) provides the most scalable architecture |

---

### 🔥 Pitfalls in Production

**Session loss during rolling deployments with sticky sessions:**

```
PROBLEM:
  Rolling deployment: replace servers one at a time.
  Load balancer: 4 servers (A, B, C, D)
  Server A: 1,500 active sessions
  
  Deployment starts: Server A taken out of rotation.
  Session affinity bindings for Server A: all immediately invalid.
  1,500 users: next request → LB routes to B/C/D → session not found.
  1,500 users: forced logout (HttpSession.getAttribute returns null → NPE)
  
  User impact: all active users on Server A simultaneously logged out.
  With 4 servers: 25% of users logged out per server replacement.
  
MITIGATION 1: Session drain (graceful)
  1. Remove Server A from rotation (no new sessions routed there).
  2. Set drain timeout: 30 minutes (match session TTL).
  3. Existing session requests: still route to Server A during drain.
  4. After 30 minutes: all sessions either expired or completed.
  5. Now terminate Server A — no active sessions → no forced logouts.
  
  Trade-off: deployment takes hours (30-min drain × 4 servers = 2 hours).
  
MITIGATION 2: External session store (Redis) — the proper fix
  Sessions in Redis: survive Server A termination.
  Server A is terminated → sessions remain in Redis.
  Requests: LB routes to B/C/D → they read sessions from Redis.
  No forced logouts. Rolling deployment takes minutes, not hours.
  
  Implementation time: typically 1-3 sprints.
  ROI: eliminates all session-related production incidents.
```

---

### 🔗 Related Keywords

- `Sticky Sessions` — the most common load-balancer implementation of session affinity
- `Load Balancing` — load balancers implement session affinity features
- `Consistent Hashing (Load Balancing)` — can implement session affinity via hash(session_id) → server
- `Horizontal Scaling` — session affinity limits horizontal scaling effectiveness
- `JWT (JSON Web Tokens)` — stateless alternative that eliminates session affinity requirements

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Route same-session requests to same       │
│              │ server — OR eliminate via shared store    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Legacy stateful apps; WebSocket routing;  │
│              │ soft affinity for performance (cache warm)│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Elastic scaling critical; blue-green/     │
│              │ rolling deploys; cloud-native greenfield  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Sticky sessions are a workaround;        │
│              │  external session store is the cure."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sticky Sessions → Redis Session Store     │
│              │ → Horizontal Scaling                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A multiplayer game server uses WebSocket connections to maintain player state (position, health, inventory) in server memory. 10,000 active players, 5 game servers, each managing 2,000 players via WebSocket sticky sessions. A server upgrade is needed (new features + bug fixes). Describe a zero-downtime WebSocket migration strategy that moves players from the old server to the new server without disconnecting them or losing their game state. What are the key protocol and state transfer challenges?

**Q2.** You have a microservices architecture where Service A (user-facing, session-managed, uses sticky sessions) calls Service B (internal, stateless) and Service C (internal, uses server-local computation cache — soft affinity preferred). Draw the session affinity topology: which service-to-service calls benefit from affinity, which are harmed by enforced affinity, and which should be completely unconstrained. Explain how Kong API Gateway or AWS ALB would be configured to enforce or bypass affinity at each hop.
