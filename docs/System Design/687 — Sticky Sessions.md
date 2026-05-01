---
layout: default
title: "Sticky Sessions"
parent: "System Design"
nav_order: 687
permalink: /system-design/sticky-sessions/
number: "687"
category: System Design
difficulty: ★★☆
depends_on: "Load Balancing, Round Robin, Session Affinity"
used_by: "Session Affinity"
tags: #intermediate, #distributed, #networking, #architecture, #pattern
---

# 687 — Sticky Sessions

`#intermediate` `#distributed` `#networking` `#architecture` `#pattern`

⚡ TL;DR — **Sticky Sessions** (session persistence) ensures all requests from the same user/session are routed to the same backend server, preserving server-side session state across multiple HTTP requests.

| #687 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Round Robin, Session Affinity | |
| **Used by:** | Session Affinity | |

---

### 📘 Textbook Definition

**Sticky Sessions** (also called session persistence, session affinity, or server affinity) is a load balancing feature where the load balancer routes all HTTP requests from a specific client session to the same backend server throughout the session's lifetime. The load balancer tracks session-to-server bindings using session identifiers embedded in: cookies (cookie-based stickiness, most common), source IP addresses, URL parameters, or SSL session IDs. Sticky sessions are necessary when application state is stored in-process (server memory) rather than in a shared external store — the application server holds session data (authentication state, shopping cart, workflow progress) that is not replicated to other instances. The binding is stored in the load balancer's persistence table and respected for subsequent requests until: the session expires, the server fails, or an administrative change removes the binding.

---

### 🟢 Simple Definition (Easy)

Sticky Sessions mean "once you're assigned to Server A, all your requests keep going to Server A." It's like being assigned to a specific checkout lane at a supermarket and having to use the same lane for every item in your cart. Needed when Server A holds your session data in its own memory (so only Server A knows who you are).

---

### 🔵 Simple Definition (Elaborated)

User logs in → load balancer routes to Server A → Server A creates session (stores user info in memory at `sessions["abc123"]`). Next request: user sends `Cookie: JSESSIONID=abc123`. Without Sticky Sessions: load balancer might send this to Server B → Server B has no `sessions["abc123"]` → user gets "Session not found" → forced re-login. With Sticky Sessions: load balancer reads the cookie, finds "abc123 → Server A" in its persistence table, routes to Server A → Server A finds the session → user stays logged in.

---

### 🔩 First Principles Explanation

**The problem Sticky Sessions solves — stateful HTTP:**

```
STATELESS HTTP DESIGN (ideal for horizontal scaling):
  HTTP is stateless by design: each request is independent.
  User state lives in external storage: database, Redis.
  
  Request 1: POST /login → authenticated → JWT token returned
  Request 2: GET /dashboard → sends JWT → any server can verify JWT
  Request 3: GET /profile → any server reads from shared database
  
  Load balancer: distributes freely — any server handles any request.
  Horizontal scaling: add servers → automatically handles more traffic.
  Server failure: requests rerouted → new server handles them fine.
  
STATEFUL HTTP APPLICATION (the problem):
  Server-side session: HttpSession (Java EE), $_SESSION (PHP),
  request.session (Express.js)
  
  Session data lives IN MEMORY on the specific server:
  Server A RAM: { "session_abc123": { "userId": 42, "cart": [...] } }
  Server B RAM: { }  ← no knowledge of session_abc123
  
  Without Sticky Sessions:
  Request 1 → Server A → creates session_abc123 in Server A's memory
  Request 2 → Server B → "session_abc123 not found" → 401 Unauthorized
  
  User experience: random logouts, lost shopping carts, broken workflows.

STICKY SESSIONS: bind session to server, solve the symptoms

  Load balancer persistence table:
  { "session_abc123": "server-a:8080" }
  { "session_xyz789": "server-b:8080" }
  { "session_qrs456": "server-a:8080" }
  
  Cookie: JSESSIONID=abc123 → LB table lookup → Server A
  Cookie: JSESSIONID=xyz789 → LB table lookup → Server B
  
  Server A handles 2 sessions, Server B handles 1 session.
  (Load imbalance is accepted to preserve session affinity)

COOKIE-BASED STICKINESS (most reliable):
  First request: load balancer sets a cookie with the server binding:
    Set-Cookie: AWSELB=server-a-id; Path=/; HttpOnly
    (or AWSALB, BIGipServer, NginxRoute, etc.)
  
  Subsequent requests: browser sends cookie → LB reads → routes to server-a
  
  Advantages: works even if client IP changes (mobile, NAT)
  Disadvantages: requires cookie support in client; adds cookie to response

IP HASH STICKINESS (simpler):
  server_binding = hash(client_ip) % num_servers
  
  Advantages: no cookie needed; stateless load balancer
  Disadvantages: NAT (many users behind one IP → hot server),
                IPv6 addresses harder to predict,
                VPN changes route user to different server mid-session
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Sticky Sessions (stateful application without shared session store):
- Requests from same user routed to different servers → sessions lost
- Users randomly logged out, shopping carts emptied, workflows broken
- Horizontal scaling impossible — adding servers breaks existing users

WITH Sticky Sessions:
→ Server-side session state preserved across requests
→ Horizontal scaling viable for legacy stateful applications
→ Incremental migration path: sticky now → shared session store later

---

### 🧠 Mental Model / Analogy

> A hospital where patients see different doctors on each visit, but their medical records are stored only by their personal doctor (not in a shared system). If the patient sees any doctor other than their own, the doctor has no history. The hospital's receptionist (load balancer) keeps a card: "Patient Smith → always route to Dr. A." Sticky sessions are the receptionist's routing card. The real fix: move records to a shared hospital database so any doctor can treat any patient.

"Receptionist's routing card" = load balancer session persistence table
"Patient → Doctor mapping" = session → server binding
"Medical records in doctor's office only" = session state in server RAM
"Shared hospital database" = external session store (Redis)

---

### ⚙️ How It Works (Mechanism)

**AWS ALB cookie-based sticky sessions:**

```
FLOW:
  1. First request arrives at ALB with no stickiness cookie.
  2. ALB routes to Server A (by chosen algorithm: round-robin, etc.).
  3. Server A responds with app session cookie: JSESSIONID=abc123
  4. ALB adds its own stickiness cookie: AWSALB=HASH_server-a (Secure; HttpOnly)
  5. Browser now has two cookies: JSESSIONID + AWSALB

  Subsequent requests:
  6. Browser sends: Cookie: JSESSIONID=abc123; AWSALB=HASH_server-a
  7. ALB reads AWSALB cookie → decodes → routes to Server A (ignoring RR turn)
  8. Server A processes request using session abc123 from its memory

FAILURE SCENARIO:
  Server A crashes → ALB detects failure → removes from pool
  Next request: AWSALB points to dead server → no longer in pool
  ALB: falls back to routing algorithm → sends to Server B
  Server B: no session abc123 → user must log in again
  
  This is unavoidable with server-side session state.
  Mitigation: session replication to nearest neighbour (Tomcat clustering),
              or external session store (Redis) + sticky sessions as optimisation.
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP (stateless protocol)
        │
        ▼ (stateful apps add server-side sessions)
Session State Problem
(session data in server RAM, not shared)
        │
        ▼ (two solutions)
Sticky Sessions ◄──── (you are here)     External Session Store
(bind session to server)                  (Redis, Memcached)
(quick fix, adds complexity)             (proper fix, enables stateless design)
        │
        ▼
Session Affinity (broader concept)
```

---

### 💻 Code Example

**nginx sticky sessions with cookie module:**

```nginx
# nginx (requires nginx-sticky-module-ng or nginx plus)
upstream api_backend {
    # Cookie-based sticky sessions:
    sticky cookie srv_id expires=1h domain=.example.com path=/ httponly;
    
    server backend1:8080;
    server backend2:8080;
    server backend3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# HAProxy: cookie-based persistence
backend app_servers
    balance roundrobin
    cookie SRV_ID insert indirect nocache httponly secure
    server app1 10.0.0.1:8080 check cookie app1
    server app2 10.0.0.2:8080 check cookie app2
    server app3 10.0.0.3:8080 check cookie app3
    # First response: Set-Cookie: SRV_ID=app1 (by HAProxy)
    # Subsequent: HAProxy reads SRV_ID → routes to app1
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Sticky Sessions are needed for all load-balanced applications | Only needed for applications with server-side session state. Stateless applications (JWT auth, API servers, microservices) don't need sticky sessions — any server can handle any request |
| Sticky Sessions solve the horizontal scaling problem | They enable horizontal scaling for stateful apps, but they also limit it: if one server has disproportionately many active sessions, load is uneven. They're a workaround, not a true solution — the real solution is an external session store |
| IP-hash sticky sessions always route the same client to the same server | IP-hash fails when clients are behind NAT (thousands of users share one IP → all routed to same server) or when clients use VPNs or mobile networks (IP changes during session → routed to wrong server) |
| Sticky Sessions prevent data loss on server failure | Server failure always means session loss when using server-side sessions. Sticky Sessions don't replicate session data; they just maintain affinity for healthy servers. For HA, use session replication or external session stores |

---

### 🔥 Pitfalls in Production

**Sticky sessions + auto scaling = hotspot problem:**

```
PROBLEM:
  9 AM: 10 backend servers, 10,000 users with sticky sessions evenly distributed.
  Each server: 1,000 sticky sessions.
  
  11 AM: traffic spike → Auto Scaler adds 5 more servers (now 15 total).
  New servers: 0 sticky sessions (no one is bound to them yet).
  Existing 10 servers: still have their 1,000 sessions each.
  
  New requests from NEW users: round-robin across all 15 servers.
  New users: most go to 5 new servers (they're free in round-robin).
  Existing users: still bound to their original 10 servers.
  
  Effective load:
    Original 10 servers: 1,000 old sessions + some new users
    New 5 servers: only new users (no sessions yet)
  
  RESULT: load does NOT distribute evenly across 15 servers.
  The 10 original servers are still handling most of the load.
  Auto scaling didn't help existing users — only new users hit new servers.
  
FIX:
  OPTION 1 (Best): Migrate to shared session store (Redis).
    Spring Session + Redis:
    @EnableRedisHttpSession
    // Session data stored in Redis, not server RAM
    // Any server can handle any user's request
    // Sticky sessions no longer needed
    // Auto scaling: new server immediately handles all sessions
  
  OPTION 2 (Migration path): Session replication.
    Tomcat cluster: replicate session data across all nodes.
    Expensive (network + memory per replication),
    but allows removing sticky sessions requirement.
  
  OPTION 3 (Temporary relief): Session drain during scale-in.
    Before decommissioning a server:
    - Remove from load balancer (no new sessions)
    - Wait for existing session TTL to expire (e.g., 30 minutes)
    - Then terminate server
    // Graceful: sessions expire naturally, no forced logout
```

---

### 🔗 Related Keywords

- `Load Balancing` — sticky sessions are a load balancer feature
- `Session Affinity` — the broader concept; sticky sessions is the implementation mechanism
- `Round Robin` — sticky sessions override round-robin when a session binding exists
- `Consistent Hashing (Load Balancing)` — alternative to cookie-based stickiness; hash(session_id) → server
- `Horizontal Scaling` — sticky sessions enable scaling but also limit its effectiveness

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Bind user session to one server (cookie   │
│              │ or IP-hash) to preserve server-side state │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Legacy stateful apps with server-side     │
│              │ sessions; can't refactor to shared store  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Stateless apps (JWT); when elastic auto-  │
│              │ scaling is critical; high availability    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Always route the patient back to their   │
│              │  own doctor — because records aren't      │
│              │  in the shared hospital system yet."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Session Affinity → External Session Store │
│              │ → Horizontal Scaling                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your e-commerce application uses sticky sessions with 6 backend servers. Server 3 handles 2,400 active sessions (40% of all 6,000 sessions) because it was the only server available during a traffic spike when many users first logged in. The other 5 servers each handle ~720 sessions. Server 3's CPU is at 85%; other servers at 25%. You cannot migrate to an external session store this sprint. What are your options to rebalance load without forcing users to log out, and what are the trade-offs of each approach?

**Q2.** An application uses cookie-based sticky sessions with a 30-minute session TTL. A security penetration test reveals that the stickiness cookie (`AWSALB=server-a-hash`) is exposed without the `Secure` flag. An attacker who can perform a man-in-the-middle attack on HTTP traffic could steal this cookie. Beyond adding the `Secure` flag, identify two other architectural improvements that would make the session routing infrastructure more secure, explaining exactly what attack each one prevents.
