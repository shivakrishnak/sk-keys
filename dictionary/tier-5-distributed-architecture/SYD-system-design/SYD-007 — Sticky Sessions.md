---
layout: default
title: "Sticky Sessions"
parent: "System Design"
nav_order: 7
permalink: /system-design/sticky-sessions/
number: "SYD-007"
category: System Design
difficulty: ★★☆
depends_on: Load Balancing, Session Management, Stateless Design
used_by: Web Applications, Ecommerce, Session-Heavy Services
related: Session Affinity, Load Balancing, Distributed Sessions
tags:
  - session
  - load-balancing
  - state-management
  - intermediate
---

# SYD-007 — Sticky Sessions

⚡ TL;DR — A load balancing technique that routes all requests from a single client to the same backend server throughout their session—simplifies session management by avoiding data sync, but reduces scalability.

| #687            | Category: System Design                                  | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Session Management                       |                 |
| **Used by:**    | Web Applications, Shopping Carts, User Sessions          |                 |
| **Related:**    | Session Affinity, Distributed Sessions, Stateless Design |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
User logs in. Load balancer sends request to Server 1. Server 1 stores session data locally: `sessions[user_id] = {"logged_in": true, "cart": [...]}`. Request 2 from same user goes to Server 2 (load balancer doesn't care). Server 2 has no idea user is logged in—session data is on Server 1. Login fails.

**THE BREAKING POINT:**
With horizontal scaling, requests from the same user can land on different servers. Without shared session storage, each server is clueless about previous requests.

**THE INVENTION MOMENT:**
"This is why sticky sessions were created—pin each user to one server so their session data stays local."

---

### 📘 Textbook Definition

Sticky sessions (also called session affinity or session persistence) is a load balancing feature where all requests from a specific client are routed to the same backend server throughout their session. Typically implemented by tracking the client's IP address, a cookie, or a URL parameter and ensuring the load balancer's routing algorithm always returns the same server for that identifier. Simplifies session management but creates a single point of failure for that client and reduces flexibility in scaling.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Always route a user to the same server for their entire session—their session data stays local, no syncing needed.

**One analogy:**

> A bank customer has an account with Teller 1. When they arrive, they always go to Teller 1 (not random tellers). Teller 1 knows their balance, account history, preferences. If Teller 1 is busy, the customer waits (doesn't go to another teller). Sticky sessions = always your assigned teller.

**One insight:**
Sticky sessions are a workaround for having local session storage. The better solution is to move sessions to shared storage (Redis, database) so any server can handle any request.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A user/client must be identifiable (by IP, cookie, or session ID)
2. The load balancer must remember which server that client used previously
3. The same server must remain available (if it fails, session is lost)

**DERIVED DESIGN:**
The load balancer receives a request. It checks: is this client in my "stickiness map"? If yes, route to the mapped server. If no, pick a server (round-robin), store the mapping `{client_id → server}`, route to it. Future requests from same client check the map and route to the same server. If that server fails, the client's mapping is removed; next request picks a new server (session lost, client must re-login).

**THE TRADE-OFFS:**
**Gain:** Simplicity. No need for distributed session storage. Each server can keep sessions in memory (fast). No cross-server communication. Works for legacy applications.

**Cost:** Reduces scalability. If a server is pinned to 100 clients, removing that server breaks all 100. New servers added don't receive traffic from existing clients (until they re-login or session expires). Single point of failure per client: if their server crashes, session dies.

---

### 🧪 Thought Experiment

**SETUP:**
3 web servers. User logs in, session created with `{"user_id": 123, "logged_in": true}`. User makes 5 requests over 10 minutes.

**WITHOUT STICKY SESSIONS:**
Request 1 → Server 1 (session created locally)
Request 2 → Server 2 (no session! login failed)
Request 3 → Server 3 (no session! login failed)
User gets kicked out. Nightmare.

**WITH STICKY SESSIONS:**
Request 1 → Server 1 (session created, client pinned to Server 1)
Request 2 → Server 1 (routed to same server, session retrieved)
Request 3 → Server 1 (routed to same server, session retrieved)
Request 4 → Server 1 (routed to same server)
Request 5 → Server 1 (routed to same server)
All requests work. User stays logged in throughout their session.

**THE INSIGHT:**
Sticky sessions are a quick fix for local session storage, but they create scalability friction.

---

### 🧠 Mental Model / Analogy

> A hair salon books clients with specific stylists. Client books with Stylist A. Future appointments automatically go to Stylist A (sticky). Stylist A knows their hair history, preferences, color. If Stylist A leaves, the salon loses that client relationship. With non-sticky (clients can see any available stylist), new stylists quickly understand client preferences (if kept in a shared database).

- "Client" → user/session
- "Stylist A" → backend server
- "Hair history in Stylist A's notes" → session data in local memory
- "Shared database of client info" → distributed session store
- "Lost relationship if stylist leaves" → session lost if server fails

**Where this analogy breaks down:** Users don't actually care which server handles their request; hair clients do care about their stylist. But the scalability problem is the same.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
After a user logs in, all their future requests go to the same server. That server remembers them. If they go to a different server, they'd have to log in again.

**Level 2 — How to use it (junior developer):**
Enable sticky sessions in your load balancer config. NGINX: `ip_hash;` or `hash $cookie_jsessionid;`. AWS ELB: enable "Stickiness" in target group, set duration (e.g., 1 hour). Users will notice they stay logged in. Monitor that clients don't evenly distribute (sticky sessions cause imbalance).

**Level 3 — How it works (mid-level engineer):**
The load balancer maintains a table: `{client_identifier → server}`. Client ID is usually the client's IP address (IP hash) or a session cookie set on first request. When a request arrives, LB looks up the client ID in the table. If found, routes to that server. If not found, uses standard algorithm (round-robin) and creates a new entry. The table expires entries when sessions time out (e.g., 1 hour). If a backend server is marked down, its entries are removed (sessions lost).

**Level 4 — Why it was designed this way (senior/staff):**
Sticky sessions are a legacy pattern from early web, when storing sessions in a database was expensive or didn't exist. Modern practice is to move sessions to external storage (Redis, Memcached) and use stateless servers. But sticky sessions persist because (1) they're simple to enable, (2) some applications were built on them and are hard to refactor, (3) they have lower latency than distributed sessions (no network overhead). They're acceptable for small/medium systems.

---

### ⚙️ How It Works (Mechanism)

Sticky sessions operation:

```
LB State: stickiness_table = {}

Request 1: User logs in from IP 203.0.113.5
  ↓
  IP not in stickiness_table
  → Pick Server 1 (round-robin)
  → stickiness_table[203.0.113.5] = Server 1
  → Send request to Server 1

Server 1:
  Create session: sessions[123] = {"user_id": 123, "logged_in": true}
  Set cookie: "JSESSIONID=abc123; Path=/"
  Response to client

Request 2: Same client (203.0.113.5), cookie = abc123
  ↓
  IP in stickiness_table
  → stickiness_table[203.0.113.5] = Server 1
  → Send request to Server 1

Server 1:
  Look up session by JSESSIONID
  Found: sessions[123]
  Request processed with user context

Request 3: Different client (198.51.100.1) arrives
  ↓
  IP not in table
  → Pick Server 2 (round-robin)
  → stickiness_table[198.51.100.1] = Server 2
  → Send to Server 2
```

**In Happy Path:**
Client makes 5 requests. All route to Server 1. Session data stays consistent. User experience: seamless.

**When Something Goes Wrong:**
Server 1 crashes. Request arrives from client (203.0.113.5). LB tries to route to Server 1 (from stickiness table). Server 1 down. LB removes entry from table. Next request picks Server 2. Session is lost (not on Server 2). Client must re-login.

---

### 🔄 The Complete Picture — End-to-End Flow

```
User Action (login)
    ↓
Request to Load Balancer
    ↓
STICKY SESSIONS LOOKUP (YOU ARE HERE)
Check: is this client pinned to a server?
    ├─ YES: Route to that server
    └─ NO: Pick new server, pin client to it
    ↓
Request to backend server
    ↓
Server processes, creates session (local or shared)
    ↓
Response + cookie to client
    ↓
Client stores cookie

User Action (next request, same session)
    ↓
Request + cookie to Load Balancer
    ↓
LB: client is pinned to Server X
    ↓
Route to Server X
    ↓
Server X looks up session by cookie
    ↓
Session found, request processed

Server Failure Path:
    Server X crashes
    → LB detects (health check)
    → Remove from pool
    → Remove stickiness entries for clients on X
    → Next request from those clients: re-pin to new server
    → Session lost, clients see "login expired"
```

**WHAT CHANGES AT SCALE:**
At 1000 concurrent users with sticky sessions, 500 might pin to Server 1, 500 to Server 2. Very uneven. When you add Server 3, it gets no traffic (sticky clients stay with 1 and 2). Only new logins go to Server 3. At scale, sticky sessions are unacceptable—you need distributed sessions.

---

### 💻 Code Example

Sticky sessions are configured at load balancer level, not application code:

**Example 1 — NGINX Sticky Sessions:**

```nginx
upstream backend {
    # IP-based stickiness
    ip_hash;

    server app-1.internal:5000;
    server app-2.internal:5000;
    server app-3.internal:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

Requests from same IP always go to same server.

**Example 2 — AWS ELB Sticky Sessions:**

```terraform
resource "aws_lb_target_group" "app" {
    name = "app-tg"
    port = 5000
    protocol = "HTTP"

    # Enable stickiness
    stickiness {
        enabled = true
        type = "lb_cookie"  # Or "app_cookie"
        cookie_duration = 86400  # 1 day
    }
}
```

ELB automatically sets a cookie and routes based on it.

**Example 3 — Application Code (Session Storage):**

```python
from flask import Flask, session, request
from flask_session import Session
import secrets

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # Local to server
Session(app)

@app.route('/login', methods=['POST'])
def login():
    user_id = request.json['user_id']
    session['user_id'] = user_id
    session['logged_in'] = True
    # Session stored locally on this server
    # Depends on sticky sessions to find this server again
    return {'status': 'ok'}

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'not logged in'}, 401
    return {'user_id': user_id}
```

Works only if load balancer is sticky. Without stickiness, /profile request might go to different server (session not found).

---

### ⚖️ Comparison Table

| Session Approach        | Scalability                            | Speed                      | Complexity | Best For                               |
| ----------------------- | -------------------------------------- | -------------------------- | ---------- | -------------------------------------- |
| **Sticky Sessions**     | Poor (imbalance, single-point failure) | High (local memory)        | Low        | Small systems, legacy apps             |
| **Distributed (Redis)** | Excellent (servers interchangeable)    | Medium (network roundtrip) | Medium     | Production systems, horizontal scaling |
| **Database Sessions**   | Good                                   | Slow (disk I/O)            | Medium     | Persistent, queryable sessions         |
| **Stateless (JWT)**     | Excellent                              | High (no server state)     | Low        | APIs, microservices, serverless        |

**How to choose:** Use stateless (JWT) for new APIs. Use distributed sessions (Redis) for web apps needing server-side state. Sticky sessions only for legacy systems or small deployments.

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                  |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| "Sticky sessions eliminate scalability issues"          | No. They cause uneven load distribution and reduce flexibility. They're a bandage, not a solution.       |
| "Sticky sessions are free"                              | They reduce the ability to add/remove servers. New servers don't get traffic from existing clients.      |
| "Sticky sessions are transparent to the application"    | The application must store sessions locally (in memory). Won't work if app doesn't have session storage. |
| "If a server crashes, clients can fail over to another" | No. Session data is lost. Client must re-login. Defeats HA benefits of horizontal scaling.               |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Imbalanced Load Distribution**

**Symptom:**
3 servers with sticky sessions. After a day: Server 1 has 40 pinned users, Server 2 has 38, Server 3 has 5. Server 3 is mostly idle. Later, Server 1 has 150 users (80%), others 50 (10% each). Severe imbalance.

**Root Cause:**
Sticky sessions pin users to servers based on order of login. If most users login during a specific time when Server 1 is up, it gets pinned most users. As users accumulate, imbalance gets worse.

**Diagnostic Command:**

```bash
# Check stickiness table size on LB
cat /proc/sys/net/nf_conntrack_max  # Linux conntrack table
netstat -an | grep ESTABLISHED | wc -l

# Check request distribution per server
tail -f /var/log/nginx/access.log | \
  awk '{print $9}' | sort | uniq -c
# If one server >> others: imbalance
```

**Fix:**
Bad approach: Accept imbalance and overload Server 1.
Good approach: (1) Use distributed sessions so any server can handle any user. (2) Periodically drain and re-pin users (force re-login during low-traffic). (3) Use weighted sticky sessions (prefer less-loaded servers for new users).

**Prevention:**
Avoid sticky sessions. Use distributed session storage (Redis). If forced to use sticky: monitor server load per stickiness table size. Alert if > 20% imbalance.

---

**Failure Mode 2: Server Failure Breaks Pinned Sessions**

**Symptom:**
Server 1 crashes (hardware failure). 50 users pinned to Server 1 lose their session. They see "login expired" or "session not found". Must re-login. Bad user experience.

**Root Cause:**
Session data is local to Server 1. When Server 1 dies, sessions die. No replication.

**Diagnostic Command:**

```bash
# Check if session data exists on backup
ssh server-1-backup
ls /tmp/sessions/  # Empty if Server 1 crashed

# Check LB stickiness table
grep "server-1" /var/log/lb.log | tail -20
# All entries for Server 1 will be removed on failover
```

**Fix:**
Bad approach: Accept session loss.
Good approach: (1) Replicate sessions to backup server (expensive). (2) Store sessions in shared store (Redis). (3) Accept session loss but make re-login fast (no delays).

**Prevention:**
Assume server failure. Use distributed sessions. Don't rely on sticky sessions for persistence.

---

**Failure Mode 3: Client IP Changes (Mobile Roaming)**

**Symptom:**
Mobile user on WiFi gets pinned to Server 1. They switch to cellular (IP changes from 192.168.1.100 to 203.0.113.200). LB sees new IP, un-pins them. Next request goes to Server 2. Session lost (not on Server 2). User sees "login expired."

**Root Cause:**
Sticky sessions use client IP as identifier. When IP changes, identity changes. Client is re-routed, session left behind on Server 1.

**Diagnostic Command:**

```bash
# Check client IP in sticky table
grep "203.0.113.200" /var/log/lb_sticky.log
# If missing: user was never pinned (or IP changed)

# Check if user's session cookie exists elsewhere
ssh server-1
grep -r "session_id_xyz" /tmp/sessions/
```

**Fix:**
Bad approach: Ignore and accept session loss on IP change.
Good approach: (1) Use session cookie as sticky key (not IP). (2) Use distributed sessions so IP change doesn't matter. (3) Implement session migration (when user's IP changes, migrate their session).

**Prevention:**
Use session cookie stickiness (not IP hash). Clients carry their session ID; doesn't depend on IP.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Load Balancing` — the context where stickiness is configured
- `Session Management` — what stickiness is managing

**Builds On This (learn these next):**

- `Distributed Sessions` — better alternative using external storage
- `Session Affinity` — synonym/related concept
- `Stateless Design` — the architectural ideal that avoids this problem

**Alternatives / Comparisons:**

- `Distributed Sessions (Redis)` — better scalability
- `Stateless (JWT)` — no sessions at all
- `Session Affinity` — synonym for sticky sessions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Route all requests from a user to    │
│              │ same server, keep session local      │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Without stickiness, requests can     │
│ SOLVES       │ go to different servers; session    │
│              │ data not found                       │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Works but doesn't scale; creates    │
│              │ imbalance and single-point failure  │
│              │ per client                           │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Small system, legacy app, session   │
│              │ data too expensive to move           │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Building for scale; sessions need   │
│              │ to survive server failure; cloud    │
│              │ environment with auto-scaling       │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Simple, fast] vs [imbalance, low   │
│              │ resilience, inflexible]             │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Pin users to servers; simple but   │
│              │ scales poorly."                      │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Sessions → Stateless    │
│              │ Design → Session Affinity            │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A user logs in from home (IP = 203.0.113.5, pinned to Server 1). They switch to mobile (new IP = 198.51.100.1). Load balancer sees new IP, pins them to Server 2. But their session is on Server 1. What happens when they try to fetch their user profile—is session lost, or can Server 2 find it?

**Q2.** You're using sticky sessions with IP-based stickiness. A corporate proxy/NAT sits in front—100 employees go through the same proxy IP. The LB sees them all as the same client (same IP), pins all 100 to Server 1. Server 1 becomes 100x overloaded. How can this disaster be prevented?
