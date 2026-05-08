---
layout: default
title: "Session Affinity"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /system-design/session-affinity/
id: SYD-013
category: System Design
difficulty: ★★☆
depends_on: Load Balancing, Sticky Sessions, Session Management
used_by: Web Applications, Distributed Systems
related: Sticky Sessions, Load Balancing, Session Management
tags:
  - session
  - load-balancing
  - state-management
  - intermediate
---

# SYD-013 — Session Affinity

⚡ TL;DR — A load balancing technique that ensures requests related to the same session go to the same backend server—essentially synonymous with sticky sessions but emphasizes the intent of maintaining session continuity rather than just routing persistence.

| #688            | Category: System Design                                   | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Session Management                        |                 |
| **Used by:**    | Web Applications, Distributed Systems                     |                 |
| **Related:**    | Sticky Sessions, Load Balancing, Session State Management |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user interacts with a system across multiple requests. Their session (login state, shopping cart, preferences) is stored on the backend server that handled their first request. If later requests go to different servers, those servers don't have access to the session data, causing user state to be lost or corrupted.

**THE BREAKING POINT:**
In a distributed system with multiple backends, a user's session is fragmented if requests are arbitrarily routed. Without session affinity, the illusion of a continuous user session breaks down.

**THE INVENTION MOMENT:**
"This is why session affinity was created—guarantee that a user's related requests stay together on one server, preserving session coherency."

---

### 📘 Textbook Definition

Session affinity (also called session persistence or sticky sessions) is a load balancing mechanism that ensures all requests from a specific user/session are routed to the same backend server. Implemented by tracking a session identifier (cookie, URL parameter, or client IP) and using it as the routing key in the load balancer. Maintains session locality (all session data on one server) at the cost of reduced scalability and resilience.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Send all requests from one user session to the same server—preserves their session context without cross-server synchronization.

**One analogy:**

> A patient sees the same doctor throughout their treatment. The doctor knows their history, symptoms, prior tests. If the patient had to see a different doctor each visit, the new doctor would be clueless—no history, no context. Session affinity = same doctor throughout.

**One insight:**
Session affinity is a tradeoff: easy implementation vs. poor scalability. For systems that can use stateless design or shared session stores, it's unnecessary. For legacy monoliths, it's pragmatic.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Sessions are user-specific state that persists across requests
2. Sessions must be accessible to the server handling each request
3. Without affinity, synchronizing sessions across servers is expensive

**DERIVED DESIGN:**
The load balancer recognizes when requests belong to the same session (via session cookie, client ID, etc.). It routes all such requests to the same backend server. The backend stores session state locally (in memory, file system, or local cache). Subsequent requests from the same session find their state without network overhead.

**THE TRADE-OFFS:**
**Gain:** Simplicity—no need to implement distributed session storage, no inter-server communication, fast session lookup (local).

**Cost:** Server becomes stateful—can't easily replace or scale it. New servers added don't receive traffic from existing sessions (only new logins). Single server failure breaks all its pinned sessions.

---

### 🧪 Thought Experiment

**SETUP:**
Two backend servers. One user makes three requests within a session: login, view profile, logout.

**WITHOUT SESSION AFFINITY:**
Request 1 (login) → Server A → Session created locally: `sessions[user_123] = {logged_in: true}`
Request 2 (view profile) → Server B → Server B looks up `sessions[user_123]` locally—not found. User sees "not logged in."
Request 3 (logout) → Server A → Works (Server A has the session).
Incoherent behavior. User confused.

**WITH SESSION AFFINITY:**
Request 1 (login) → Server A → Session created locally
Request 2 (view profile) → Server A (routed via affinity) → Session found, profile displayed
Request 3 (logout) → Server A (routed via affinity) → Session found, logged out
Consistent behavior. User never notices session was local to one server.

**THE INSIGHT:**
Session affinity hides the complexity of distributed systems from the application and user—but at a scalability cost.

---

### 🧠 Mental Model / Analogy

> A gym assigns each member a locker. Member uses the same locker every visit (affinity). Gym staff don't need to replicate member's stuff to every locker—it's always in the same place. If a new gym location opens, existing members don't automatically use it (have to transfer). With non-affinity (member can use any locker), staff must ensure member's belongings are in every locker (expensive).

- "Member" → user/session
- "Locker" → backend server
- "Member's stuff" → session state
- "New gym location" → new server added to cluster
- "Staff replicating belongings" → distributed session storage

**Where this analogy breaks down:** Users don't actually care which server they hit; gym members do care about their locker. The trade-off is the same.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A user logs into a website. The website remembers which computer is handling their requests and keeps sending their requests to that same computer. That computer remembers the user is logged in.

**Level 2 — How to use it (junior developer):**
Enable session affinity in your load balancer. Configure it to use a session cookie as the affinity key (better than IP—survives IP changes). Users will stay logged in across requests. Be aware: if that server crashes, users must re-login.

**Level 3 — How it works (mid-level engineer):**
When a user logs in, they're assigned a Session ID (unique token, stored in a cookie). The load balancer extracts this Session ID from cookies and uses it as a hash key to map to a server. All requests with that Session ID route to the same server. The backend server stores session data in memory or local cache, indexed by Session ID. Lookup is O(1). When sessions expire (timeout), the mapping is removed.

**Level 4 — Why it was designed this way (senior/staff):**
Session affinity is a pragmatic solution from the era before distributed caching. Originally, storing sessions in a database was slow; storing them in memory on the server that created them was fast. Modern practice moved sessions to Redis or other distributed stores, making affinity unnecessary. But affinity persists in older systems and is still useful in certain scenarios (small systems, low-cost deployments, where the overhead of distributed sessions isn't justified).

---

### ⚙️ How It Works (Mechanism)

Session affinity operation:

```
User logs in (Request 1)
  ↓
Load Balancer picks Server A (round-robin or least-conn)
  ↓
Server A: Create session
  sessions = {"user_456": {logged_in: true, role: "admin"}}
  Set cookie: "SESSIONID=xyz789"
  ↓
Response sent to client with Set-Cookie header

User makes Request 2 (includes SESSIONID=xyz789)
  ↓
Load Balancer extracts: hash("xyz789") % num_servers
  → Maps to Server A
  ↓
Server A: Look up sessions["user_456"]
  → Found {logged_in: true, role: "admin"}
  → Request processed with user context
  ↓
Response sent

New request from new user (Request 3)
  ↓
Load Balancer: No Session ID in cookies (new user)
  → Pick Server B (round-robin)
  → New session created on Server B
```

**In Happy Path:**
User logs in, continues using app, all requests go to same server, session persists consistently.

**When Something Goes Wrong:**
Server A crashes. User's request arrives at LB. LB tries Server A, fails (health check). LB picks Server B. Server B has no session for this user. User sees "login expired."

---

### 🔄 The Complete Picture — End-to-End Flow

```
User Request with Session Cookie
    ↓
LOAD BALANCER: EXTRACT SESSION ID
(YOU ARE HERE)
    ↓
Hash: server_id = hash(session_id) % num_servers
    ↓
Route request to that server
    ↓
Server retrieves session data from local store
    ↓
Request processed in session context
    ↓
Response sent to client

Session Lifecycle:
    Create: First login request → Session created on assigned server
    ↓
    Maintain: All subsequent requests → Route via affinity to same server
    ↓
    Expire: Timeout OR logout → Session deleted from server

Failure Path:
    Server fails (containing sessions for N users)
    ↓
    Health check detects failure
    ↓
    Next request from affected users → Server not found
    ↓
    Re-route to different server → Session lost (not replicated)
    ↓
    User sees "Session expired" → Must re-login
```

**WHAT CHANGES AT SCALE:**
At 1000 concurrent users, 500 might be on Server 1, 500 on Server 2. Load is somewhat balanced. Add Server 3—it gets only new logins. Server 3 slowly fills with sessions. If you need to upgrade Server 1, you can't (500 active sessions will be lost). Inflexible.

---

### ⚖️ Comparison Table

| Approach                 | Session Locality     | Scalability      | Resilience             | Complexity  | Best For                   |
| ------------------------ | -------------------- | ---------------- | ---------------------- | ----------- | -------------------------- |
| **Session Affinity**     | One server           | Poor (imbalance) | Poor (loss on failure) | Low         | Small systems, legacy apps |
| **Distributed Sessions** | Shared store (Redis) | Excellent        | Excellent (replicated) | Medium      | Production, HA-required    |
| **Stateless (JWT)**      | No server state      | Excellent        | N/A (no state)         | Low         | APIs, microservices        |
| **Database Sessions**    | Shared DB            | Good             | Good (persistent)      | Medium-High | Durable, queryable state   |

**How to choose:** Affinity for small deployments or when refactoring is not feasible. Distributed sessions for production systems. Stateless for APIs.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                             |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| "Session affinity guarantees session persistence" | No. If the server crashes, the session is lost. Affinity is for routing, not persistence.           |
| "Session affinity is the same as sticky sessions" | Essentially yes, but sticky sessions emphasize the mechanism; affinity emphasizes the intent.       |
| "All users should use session affinity"           | No. For stateless applications or APIs, affinity is unnecessary and harmful to scalability.         |
| "Session affinity eliminates the need for HA"     | No. A single server failure still breaks all its sessions. Proper HA requires distributed sessions. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Server Failure Causes Session Loss**

**Symptom:**
Server 1 crashes. 100 users pinned to Server 1 lose their session. They see "not logged in" or "session expired." Angry support tickets.

**Root Cause:**
Session affinity doesn't replicate data. It just routes. If the server is gone, sessions are gone.

**Diagnostic Command:**

```bash
# Check which sessions were on Server 1
curl -s http://server-1/admin/sessions | wc -l
# (If server is down, curl fails—confirms sessions lost)

# Check if any replicas exist
curl -s http://server-2/admin/sessions | grep "session_from_server_1"
# (Empty if no replication)
```

**Fix:**
Bad approach: Accept session loss.
Good approach: (1) Replicate sessions to a backup server. (2) Move sessions to Redis/shared store. (3) Implement session replication with synchronous writes.

**Prevention:**
Design for session durability. Use distributed session stores. Or accept transient session loss and build fast re-login (seconds, not minutes).

---

**Failure Mode 2: Cascading Failure Under Load**

**Symptom:**
Server 1 has 200 pinned sessions. It becomes slow (garbage collection, resource contention). Requests back up. Timeouts increase. Users retry, adding more load to Server 1. It becomes slower. Cascading.

**Root Cause:**
Affinity means Server 1 can't shed load to other servers (users are pinned). It's stuck with its load, no matter how slow it becomes.

**Diagnostic Command:**

```bash
# Check response time per server
tail -f /var/log/app.log | awk '{print $1, $10}' | sort | uniq -c
# If Server 1 >> others: bottleneck

# Check pinned session count
grep "server-1" /var/log/lb_affinity.log | wc -l
# If high: many users stuck on slow server
```

**Fix:**
Bad approach: Accept cascading and hope it recovers.
Good approach: (1) Move to load-adaptive routing (least-connections, not affinity). (2) Implement circuit breaker—stop sending requests to slow server. (3) Drain sessions gracefully—move them to another server if current one is slow.

**Prevention:**
Monitor response time per server. If one server > 2x slower than others, investigate. Don't rely on affinity for all state—use hybrid: affinity for cache, distributed for critical state.

---

**Failure Mode 3: Imbalanced Session Distribution**

**Symptom:**
Over time, sessions accumulate unevenly. Server 1: 300 sessions, Server 2: 50, Server 3: 20. Server 1 is overloaded; Servers 2–3 are idle.

**Root Cause:**
Affinity maps new sessions to servers based on when they login. If most users login during business hours when Server 1 is up, it gets most sessions. Imbalance grows over time.

**Diagnostic Command:**

```bash
# Check session count per server
for server in servers; do
    echo -n "$server: "
    curl -s "http://$server/admin/session_count"
done

# If one server >> others: imbalance
```

**Fix:**
Bad approach: Accept imbalance.
Good approach: (1) Use load-based routing (least-connections), not affinity. (2) Periodically drain sessions from overloaded servers. (3) Use weighted affinity (prefer less-loaded servers for new sessions).

**Prevention:**
Monitor session count per server. Alert if > 30% variance. Migrate sessions proactively from overloaded servers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Load Balancing` — the infrastructure implementing affinity
- `Session Management` — what affinity manages

**Builds On This (learn these next):**

- `Distributed Sessions` — better approach using shared storage
- `Sticky Sessions` — synonym/related mechanism
- `Session Replication` — ensuring session durability across servers

**Alternatives / Comparisons:**

- `Sticky Sessions` — often used synonymously
- `Distributed Sessions` — more scalable alternative
- `Stateless Design` — eliminates the need for session affinity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Route all requests from one user to  │
│              │ same server via session identifier   │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Requests to different servers lose   │
│ SOLVES       │ session context; user state broken   │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Simple routing guarantee, not data   │
│              │ persistence; server failure = lost   │
│              │ sessions                             │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Small deployment, legacy app, quick  │
│              │ implementation needed                │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Need resilience, auto-scaling,       │
│              │ building for scale, or IP changes    │
│              │ common (mobile)                      │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Simple routing] vs [poor HA,        │
│              │ session loss on failure]             │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Send user's requests to same        │
│              │ server; simple but fragile."         │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Sticky Sessions → Distributed        │
│              │ Sessions → Stateless Design          │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Session affinity uses a session cookie as the affinity key. But the cookie is created on the server that handles the first request. What happens if the user's first request to a load balancer coincides with that server being overloaded—should the LB override affinity and send to a less-loaded server, risking session fragmentation?

**Q2.** A distributed system needs session affinity (routing) AND session durability (persistence). Affinity alone doesn't replicate data. How would you combine affinity with session replication to achieve both? What's the overhead?
