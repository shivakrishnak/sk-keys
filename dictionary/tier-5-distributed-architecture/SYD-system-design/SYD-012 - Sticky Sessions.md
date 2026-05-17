---
id: SYD-012
title: Sticky Sessions
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008
used_by: SYD-013
related: SYD-008, SYD-009, SYD-011, SYD-013
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
nav_order: 12
permalink: /syd/sticky-sessions/
---

# SYD-012 - Sticky Sessions

⚡ TL;DR - Sticky sessions (session persistence) route
all requests from the same client to the same backend
server, enabling stateful applications to work behind
a load balancer without externalizing session state.
It is a workaround, not a solution.

| #012 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing | |
| **Used by:** | Session Affinity | |
| **Related:** | Load Balancing, Round Robin, Consistent Hashing, Session Affinity | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An application stores user session data in-process
(HashMap in JVM heap). The team horizontally scales
to 4 servers behind a round-robin load balancer.
A user logs in on Server A, session is stored in A's
memory. The next request goes to Server B (round-robin).
Server B has no session data. User is logged out. The
team must either (a) refactor the entire session storage
to use Redis, which takes weeks, or (b) route each
user to the same server they logged in on, which takes
one config change.

**THE BREAKING POINT:**
The correct long-term solution is to externalize session
state so any server can handle any request. But not
every team has the time or resources to refactor
immediately. Sticky sessions are the emergency lever:
change one load balancer config, and stateful
applications work behind horizontal scaling right now.

**THE INVENTION MOMENT:**
Load balancer vendors (F5, Cisco) added session
persistence as a feature in the late 1990s when
enterprises needed to horizontally scale web applications
that were not designed for stateless operation.
The mechanism: set a cookie with the server identifier,
read that cookie on subsequent requests, route to the
identified server. Simple, effective, dangerous.

---

### 📘 Textbook Definition

Sticky sessions (also called session persistence or
session affinity) is a load balancer feature that
routes all requests from the same client to the same
backend server for the duration of a session. The
load balancer identifies the client via a cookie,
source IP, or request header. On the first request
from a client, the LB selects a backend and records
the binding. On subsequent requests, the LB reads
the identifier and routes to the same backend.
Sticky sessions enable stateful applications (storing
session data in-process) to function correctly behind
a horizontal load balancer. They do not eliminate the
SPOF: if the bound server fails, the session is lost.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A user's requests always go to the same server,
even though there are many servers behind the load
balancer.

**One analogy:**
> A hotel guest who is always checked in to Room 12
> when they stay at this hotel, so their belongings
> are always in the same room. If Room 12 is being
> renovated (server is down), the guest must move
> all their belongings to a new room - they lose
> their room-specific state.

**One insight:**
Sticky sessions solve the symptom (requests hitting
stateless servers with in-process state) without
fixing the root cause (state stored in-process).
The correct fix is externalizing session state. Sticky
sessions are valid as a short-term bridge but become
a liability if they persist as a permanent solution.

---

### 🔩 First Principles Explanation

**MECHANISM:**
1. Client sends first request. LB selects Backend A.
2. LB (or Backend A) sets a cookie:
   `Set-Cookie: SERVERID=backend-a; Path=/`
3. Client sends all subsequent requests with that cookie.
4. LB reads the cookie, routes to Backend A.
5. This continues until: the session expires, the
   cookie is cleared, or Backend A fails.

**IMPLEMENTATION METHODS:**
- **LB-injected cookie:** Load balancer inserts the
  cookie without application awareness. Application
  is not modified. Transparent to developers.
- **Application-generated cookie:** Application sets
  a session cookie that the LB reads to determine
  routing. Requires LB to know which cookie name
  to inspect.
- **Source IP hashing:** `hash(client_IP) % N` always
  routes the same IP to the same server. Simple,
  but clients behind NAT (many users sharing one IP)
  create hot servers.

**THE FUNDAMENTAL WEAKNESS:**
Sticky sessions do not solve session loss on server
failure. When Backend A fails, all sessions bound
to it are lost. The client must start a new session
on a different server. For some applications (shopping
cart), this means lost data. For others (stateless
data), it means re-login.

**THE TRADE-OFFS:**
**Gain:** Stateful applications work correctly with
horizontal scaling. Zero application code changes.
One load balancer config change.
**Cost:** Uneven load distribution (users with long
sessions exhaust one server while others are idle).
SPOF risk remains (server failure = session loss).
Harder to auto-scale (removing a server with active
sessions requires draining first or accepting session
loss). Masks the architectural problem.

---

### 🧪 Thought Experiment

**SCENARIO: Black Friday with sticky sessions**

Normal traffic: 1,000 users evenly distributed
across 4 servers (250 per server). Sessions last
~5 minutes.

Black Friday: 10,000 users arrive. Auto-scaling
adds 6 new servers (10 total). 

Problem: New servers have 0 sessions. Existing
4 servers still have their existing 1,000 sessions.
For the next 5 minutes while sessions expire,
existing sessions cannot move to new servers.
The 4 original servers handle 1,000 old sessions
+ their share of 9,000 new sessions.
New servers only get new sessions.
Original servers are overloaded. New servers idle.

**THE INSIGHT:**
Sticky sessions prevent traffic rebalancing. Auto-
scaling adds capacity, but that capacity cannot be
utilized by existing sessions. For short-lived
sessions, the mismatch resolves within one session
TTL. For long sessions (hours), the imbalance
persists. This is a real production problem during
traffic spikes.

---

### 🧠 Mental Model / Analogy

> Sticky sessions are like assigning specific seats
> at a conference to specific attendees. Each attendee
> always sits in their assigned seat. The problem:
> some seats (servers) get more complex attendees
> than others, and if a seat's row is removed, those
> attendees lose their spot with no way to recover
> their notes (session data).

**The better pattern:**
Give everyone a locker number (session ID) and let
them sit anywhere. The locker holds their stuff.
Any seat works. This is stateless + external session
storage.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A "remember me" feature in the load balancer: once
you're assigned to Server A, your requests always
go to Server A.

**Level 2 - How to use it (junior developer):**
In AWS ALB: enable "Stickiness" on the target group.
Set the cookie duration. The ALB automatically manages
the `AWSALB` cookie on each client.

**Level 3 - How it works (mid-level engineer):**
The LB inserts or reads a persistence cookie. On
arrival of a new session, the LB picks a backend
(via normal algorithm), encodes the backend identifier
in the cookie, and sets the cookie in the response.
On subsequent requests, the LB decodes the cookie
and routes directly to the identified backend,
bypassing the normal load balancing algorithm.

**Level 4 - Why it was designed this way (senior/staff):**
LB-injected cookies are preferred over source-IP
hashing because IP-based stickiness breaks in several
cases: clients behind carrier-grade NAT (CGN) may
share an IP, concentrating traffic; mobile clients
frequently change IPs as they move between networks
(WiFi → cellular), losing their session assignment.
Cookie-based stickiness is more reliable because
the cookie travels with the client regardless of
network changes.

**Level 5 - Mastery (distinguished engineer):**
Sticky sessions are an architectural smell. If a
system requires sticky sessions for correctness,
it has in-process state that should be externalized.
The correct architecture decision framework:
(1) Can this state be stored in Redis/DynamoDB? Yes
→ fix it now. (2) Can this state be computed on
each request (idempotent)? Yes → fix it now.
(3) Is this inherited legacy code with no path to
refactoring? → use sticky sessions as a bridge with
a clear date to remove it. Sticky sessions as a
permanent solution are a scaling time bomb.

---

### ⚙️ How It Works (Mechanism)

**Cookie-based sticky session flow:**

```
┌──────────────────────────────────────────────────────┐
│ FIRST REQUEST (no cookie)                            │
│                                                      │
│  Client → [Load Balancer]                            │
│               │ No SERVERID cookie found             │
│               │ Apply normal algorithm (round-robin) │
│               ↓                                      │
│           [Backend B] ← selected                     │
│               │ Response                             │
│               ↓                                      │
│  [Load Balancer] → Set-Cookie: SERVERID=backend-b   │
│               ↓                                      │
│  Client receives response + cookie                   │
│                                                      │
│ ALL SUBSEQUENT REQUESTS                              │
│                                                      │
│  Client → [Load Balancer]                            │
│               │ Cookie: SERVERID=backend-b           │
│               │ Route directly to Backend B          │
│               ↓                                      │
│           [Backend B] ← forced                       │
│               │ Response                             │
│               ↓                                      │
│  Client receives response                            │
└──────────────────────────────────────────────────────┘
```

**Load imbalance visualization:**

```
┌──────────────────────────────────────────────────────┐
│ LOAD DISTRIBUTION PROBLEM                            │
│                                                      │
│ 10 users, 3 servers, sticky sessions                 │
│ By chance: A=6 users, B=3 users, C=1 user           │
│                                                      │
│ Each user has a 30-minute session.                   │
│ CPU: A=60%, B=30%, C=10%                            │
│                                                      │
│ New request arrives from new user:                   │
│ LB uses round-robin for new sessions: goes to C.    │
│ C is now at 20%. A still at 60%.                    │
│                                                      │
│ vs. STATELESS (no sticky, Redis sessions):           │
│ Any server handles any request.                      │
│ Load balancer distributes based on algorithm.        │
│ CPU: A=33%, B=33%, C=33%. Perfect.                  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - AWS ALB: Enable sticky sessions**
```bash
# Enable sticky sessions on a target group
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --attributes \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=lb_cookie \
    Key=stickiness.lb_cookie.duration_seconds,Value=86400

# Verify
aws elbv2 describe-target-group-attributes \
  --target-group-arn arn:aws:... \
  --query 'Attributes[?starts_with(Key, `stickiness`)]'
# Output:
# stickiness.enabled: true
# stickiness.type: lb_cookie
# stickiness.lb_cookie.duration_seconds: 86400
```

**Example 2 - nginx: IP hash (simple sticky sessions)**
```nginx
# BAD: Source IP hashing - breaks with NAT, mobile clients
upstream backend {
    ip_hash;
    server 10.0.1.1:8080;
    server 10.0.1.2:8080;
    server 10.0.1.3:8080;
}

# GOOD: Cookie-based sticky sessions (nginx Plus)
# Or use application-level session storage instead
upstream backend {
    # Prefer this: least_conn + external session store
    least_conn;
    server 10.0.1.1:8080;
    server 10.0.1.2:8080;
    server 10.0.1.3:8080;
}

# Even better: Spring Session with Redis (no sticky needed)
# spring.session.store-type=redis
```

**Example 3 - Correct path: Replace sticky with Redis**
```java
// BAD: In-process session → requires sticky sessions
@Component
public class SessionService {
    // Dies when server restarts. Requires sticky sessions.
    private final Map<String, UserSession> sessions
        = new ConcurrentHashMap<>();

    public UserSession getSession(String sessionId) {
        return sessions.get(sessionId);
    }

    public void setSession(String id, UserSession s) {
        sessions.put(id, s);
    }
}

// GOOD: Redis session → sticky sessions NOT needed
// Any server can handle any request
@Component
public class SessionService {
    private final RedisTemplate<String, UserSession> redis;
    private static final Duration SESSION_TTL =
        Duration.ofHours(24);

    public UserSession getSession(String sessionId) {
        return redis.opsForValue()
            .get("session:" + sessionId);
    }

    public void setSession(String id, UserSession s) {
        redis.opsForValue()
            .set("session:" + id, s, SESSION_TTL);
    }
}
// Now: remove sticky sessions from load balancer.
// Any server serves any request. True horizontal scale.
```

---

### ⚖️ Comparison Table

| Approach | Session Safety on Server Fail | Load Distribution | Code Change Required | Scales? |
|---|---|---|---|---|
| **Sticky Sessions** | Session lost | Uneven | None | Poorly |
| **Redis Sessions** | Session survives | Even (any algorithm) | Yes (moderate) | Yes |
| **JWT (stateless tokens)** | N/A (no server state) | Even | Yes (moderate) | Yes (best) |
| **Database sessions** | Session survives | Even | Yes (simple) | Limited by DB |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Sticky sessions solve high availability | They do not. If the bound server fails, the session is lost regardless of how many other servers are available. Only external session storage survives server failure. |
| Sticky sessions are always a bad practice | They are pragmatic for legacy applications with no path to externalized state, or short-term during a stateful-to-stateless migration. The problem is using them permanently. |
| Cookie-based sticky sessions are the same as authentication cookies | They are different. The SERVERID/AWSALB cookie is for routing only. It is set by the load balancer, not the application. The application's session/auth cookie is separate. |

---

### 🚨 Failure Modes & Diagnosis

**Session Loss on Server Failure**

**Symptom:**
Server B crashes at 2 PM. Users whose sessions were
on Server B are suddenly logged out. 15% of active
users lose their sessions simultaneously. Support
ticket spike.

**Root Cause:**
Sessions stored in Server B's in-process memory.
Sticky sessions routed all of B's users to B. When
B fails, session data is gone. Load balancer routes
B's traffic to A and C, but those servers have no
session data for B's users.

**Diagnostic:**
```bash
# AWS ALB: check unhealthy target + traffic shift
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:... \
  --query 'TargetHealthDescriptions[*].{
    Target:Target.Id,State:TargetHealth.State,
    Reason:TargetHealth.Reason}'
# Shows: backend-b unhealthy, reason: connection error

# CloudWatch: correlate 5xx errors with B's failure time
# Look for: spike in 5xx + failed-auth errors immediately
# after backend-b goes unhealthy
```

**Fix (immediate):** None - sessions are lost, users
must re-authenticate. This is the fundamental weakness
of sticky sessions.

**Fix (permanent):** Migrate session storage to Redis.
Remove sticky sessions from LB config. Sessions survive
any individual server failure.

**Prevention:**
Never use sticky sessions for sessions containing
data that must not be lost on server failure. Sticky
sessions are only acceptable for easily-reproducible
state (easily re-computed or low-stakes).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - sticky sessions is a load balancer
  configuration; understand LB fundamentals first

**Builds On This (learn these next):**
- `Session Affinity` - the broader concept; sticky
  sessions is one implementation of session affinity

**Alternatives / Comparisons:**
- `Consistent Hashing` - for cache affinity (a different
  use case for routing-based-on-client-identifier)
- Externalized session storage (Redis) - the correct
  long-term alternative to sticky sessions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Load balancer routes same client to same  │
│              │ backend server every time (via cookie)    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Stateful apps with in-process sessions    │
│ SOLVES       │ break on round-robin routing              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Workaround, not a fix. The root cause     │
│              │ (in-process state) remains. Server fails  │
│              │ = sessions lost regardless.               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Short-term: legacy app can't be refactored│
│              │ immediately; as a migration bridge        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Permanent solution; high availability     │
│              │ is critical; auto-scaling needed          │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Using as a permanent substitute for       │
│              │ externalized session storage              │
├──────────────┼───────────────────────────────────────────┤
│ IMPLEMENTATION│ Cookie: AWSALB (ALB), SERVERID (nginx)   │
│              │ Duration: match session TTL               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Sticky sessions let a stateful app work  │
│              │  with horizontal scaling - until the      │
│              │  server fails and all sessions are lost." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Session Affinity → Auto Scaling           │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Routes same client to same server - enables in-process
   session state to work behind a load balancer.
2. Session lost on server failure - sticky sessions
   provide no fault tolerance.
3. Workaround, not a fix - the correct solution is
   externalizing state to Redis or a database.

**Interview one-liner:**
"Sticky sessions route all requests from a client to
the same backend server using a cookie. They allow
stateful applications with in-process session storage
to work behind a horizontal load balancer. The critical
weakness: if the server fails, all its sessions are
lost. Sticky sessions are a short-term workaround;
the proper solution is to externalize session state
to Redis so any server can handle any request."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Technical debt accumulated by choosing the "fast but
wrong" solution accumulates interest. Sticky sessions
are fast to configure (one checkbox) but wrong at
scale (uneven load, SPOF, auto-scaling problems).
When you accept this debt, set a concrete expiry date
(a ticket, a sprint, a quarter) to pay it back.
Debt without a payback plan grows until it causes
an incident.

**Where else this pattern applies:**
- **Database connection pools**: applications sometimes
  use "connection affinity" (always use the same
  connection for the same user context) to work with
  databases that have per-connection state. The right
  fix is usually stateless queries with application-level
  state management.
- **File system state**: applications that write
  temporary files to local disk and then read them
  on the next request require "server affinity" (the
  same problem). The fix is writing to S3 or shared
  NFS, not sticky sessions.

---

### 🎯 Interview Deep-Dive

**Q1: An interviewer shows you a web app that requires
sticky sessions. What questions would you ask, and
what is the path to removing the sticky session
dependency?**
*Why they ask:* Tests architectural improvement
thinking.
*Strong answer includes:*
- Why do you need sticky sessions? (What state is
  stored in-process?)
- What is the session data? (Auth tokens? Shopping
  cart? Uploaded file path?)
- For auth/session tokens: migrate to Redis session
  store (Spring Session, express-session with Redis)
- For uploaded files: move to S3/GCS before processing
- For in-progress computation state: consider if this
  can be async (kick off job, return job ID, client
  polls for result) → removes session requirement
- Path: spike Redis integration → test → remove sticky
  sessions → verify → monitor for issues → done

**Q2: What is the difference between sticky sessions
and session affinity?**
*Why they ask:* Tests terminology precision.
*Strong answer includes:*
- Session affinity is the general concept: routing
  requests from the same client to the same server.
- Sticky sessions is one implementation of session
  affinity using HTTP cookies.
- Other implementations: IP hash (source IP → same
  server), URL parameter (session ID in URL → same
  server), consistent hashing on session ID.
- "Sticky sessions" specifically implies the LB
  manages a cookie. "Session affinity" is broader.
