---
id: ATH-008
title: "Session-Based Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-006, ATH-007
used_by: ATH-009, ATH-014, ATH-015, ATH-034
related: ATH-009, ATH-010, ATH-014
tags:
  - security
  - authentication
  - sessions
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/authentication/session-based-authentication/
---

⚡ **TL;DR** - Session-based authentication exchanges verified
credentials for a server-side session record and a client-side
session ID. The server is the source of truth: it stores who is
authenticated, for how long, and can immediately invalidate any
session. The trade-off against token-based auth is simplicity and
instant revocation at the cost of server state and horizontal
scaling complexity.

---

### 📊 Entry Metadata

| #008 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-006, ATH-007 | |
| **Used by:** | ATH-009, ATH-014, ATH-015, ATH-034 | |
| **Related:** | ATH-009 Cookies, ATH-010 Tokens, ATH-014 Remember Me | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

HTTP is stateless. Every request is independent. Without
sessions, the server forgets who you are between requests.
The only way to authenticate each request would be to
send the password with every HTTP call - massively
increasing the attack surface (more transmissions = more
chances for credential exposure).

Sessions solve this by trading a high-value credential
(password) for a low-value, opaque, short-lived token
(session ID) after the initial verification. The password
is used once; the session ID proves the successful login
for subsequent requests.

---

### 📘 Textbook Definition

Session-based authentication is a stateful mechanism where
the server maintains a session store that maps opaque session
identifiers to authenticated user state. After successful
credential verification, the server creates a session record
and issues the session ID to the client (typically as a cookie).
On each subsequent request, the client presents the session ID;
the server looks it up in the session store, retrieves the
user state, and makes the authorization decision. Session
validity is controlled server-side by expiry and explicit
invalidation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Log in once, get a numbered ticket; show the ticket on
every subsequent visit instead of re-proving your identity.

**One analogy:**
> A coat check at a restaurant. You hand in your coat (prove
> your identity with credentials), receive a numbered ticket
> (session ID). You show the ticket number to retrieve your
> coat (present session ID to continue the session). The
> restaurant staff match the ticket to your coat - you
> never need to describe the coat again.

**One insight:**
The session ID is like a numbered claim ticket - it has
value only because the server holds the corresponding
record. If the server's record expires or is deleted,
the ticket is worthless. This is why sessions enable
instant revocation: delete the server-side record, and
no existing session ID can authenticate.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│           Session-Based Authentication Flow            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  LOGIN:                                                │
│  Client  ──→  POST /login {email, password}            │
│  Server       Verify credentials                       │
│               Create session: {                        │
│                 id: "abc123...",    // random, opaque   │
│                 userId: 42,                            │
│                 roles: ["user"],                       │
│                 created: 1716048000,                   │
│                 expires: 1716134400  // 24h             │
│               }                                        │
│               Store in Redis: sessions:abc123 = {...}  │
│  Client  <──  Set-Cookie: SESSIONID=abc123; HttpOnly   │
│                                                        │
│  SUBSEQUENT REQUESTS:                                  │
│  Client  ──→  GET /api/profile                         │
│               Cookie: SESSIONID=abc123                 │
│  Server       Lookup: Redis GET sessions:abc123        │
│               Found + not expired → user=42            │
│               Proceed with authorized user             │
│                                                        │
│  LOGOUT:                                               │
│  Server       Redis DEL sessions:abc123                │
│               Clear-Cookie: SESSIONID                  │
│               → Session permanently invalidated        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

```mermaid
sequenceDiagram
    participant C as Client
    participant S as App Server
    participant R as Redis (session store)
    C->>S: POST /login (credentials)
    S->>S: Verify credentials
    S->>R: SET sessions:abc123 {userId:42} TTL 86400
    S-->>C: Set-Cookie: SESSIONID=abc123; HttpOnly; Secure
    C->>S: GET /profile (Cookie: SESSIONID=abc123)
    S->>R: GET sessions:abc123
    R-->>S: {userId:42, roles:[user]}
    S-->>C: Profile data
    C->>S: POST /logout
    S->>R: DEL sessions:abc123
    S-->>C: Clear-Cookie: SESSIONID
```

**Session store options:**

| Store | Use case | Trade-offs |
|---|---|---|
| In-memory (HashMap) | Single server, dev | Lost on restart; no horizontal scale |
| Redis | Production, multi-server | Fast, TTL support, shared across instances |
| Database | Persistent sessions | Slower; survives restart |
| Sticky sessions | Load-balanced apps | No shared store; single server per user |

---

### 💻 Code Examples

**Example - Spring Boot session management**

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        http
            .sessionManagement(session -> session
                // Prevent session fixation: regenerate
                // session ID on login
                .sessionFixation()
                    .migrateSession()
                // Limit concurrent sessions per user
                .maximumSessions(1)
                    .expiredUrl("/login?expired")
            );
        return http.build();
    }
}

// Redis-backed session store (Spring Session)
@Bean
public LettuceConnectionFactory connectionFactory() {
    return new LettuceConnectionFactory(
        new RedisStandaloneConfiguration("redis-host", 6379)
    );
}
```

**Example - FAILURE: session fixation**

```
Attack sequence:
  1. Attacker gets a valid but unauthenticated session ID:
     GET /login → server issues SESSIONID=xyz789 (pre-auth)

  2. Attacker tricks victim into using that session ID
     (via URL: https://app.com/login?jsessionid=xyz789
     or via Set-Cookie injection on HTTP)

  3. Victim logs in with SESSIONID=xyz789 (already set)

  4. Server authenticates victim but KEEPS session ID xyz789

  5. Attacker presents SESSIONID=xyz789 → fully authenticated
     as victim (without knowing victim's password)

Fix: ALWAYS issue a NEW session ID after successful login:
  // Spring Security does this automatically with
  // .sessionFixation().migrateSession() or .newSession()
  // Manual Java Servlet:
  session.invalidate(); // destroy old session
  HttpSession newSession = request.getSession(true); // new
  newSession.setAttribute("userId", userId);
```

---

### ⚠️ Common Failure Modes

**Sessions not invalidated on logout:**

```
Symptom: user logs out but can still access app using
the session ID from browser history.

Root cause: logout only clears the client-side cookie
but does not delete the server-side session record.

Fix: always delete the session record from the store on
logout. Client-side cookie clearing is insufficient.
```

**Session store single point of failure:**

```
Symptom: Redis outage → all users logged out simultaneously.

Fix:
  1. Redis Sentinel or Cluster for high availability
  2. Graceful degradation: on Redis failure, issue a
     short-lived signed JWT (fallback to stateless)
  3. Circuit breaker pattern around session store calls
```

---

### 📏 Decision Guide: Sessions vs Tokens

| Factor | Sessions (server-side) | Tokens (JWT, stateless) |
|---|---|---|
| **Instant revocation** | Yes - delete session | No - wait for expiry |
| **Horizontal scaling** | Needs shared session store | Stateless - any server |
| **Storage** | Server-side (Redis/DB) | Client-side (cookie/header) |
| **Expiry complexity** | Simple TTL in store | Must track short-lived tokens |
| **Best for** | Web apps, instant logout needed | APIs, microservices, mobile |

---

*Authentication category: ATH | Entry: ATH-008 | v5.0*