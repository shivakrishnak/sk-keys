---
id: ATH-054
title: "Distributed Session Management"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-008, ATH-015, ATH-047, ATH-053
used_by: ATH-056, ATH-057
related: ATH-008, ATH-053, ATH-057
tags:
  - security
  - authentication
  - session-management
  - distributed-systems
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/authentication/distributed-session-management/
---

⚡ **TL;DR** - In a single-server app, sessions are in memory.
In distributed systems (multiple app instances, multiple regions),
sessions must be externalized to a shared store. Redis is the
standard: fast, supports TTL-based expiry, atomic operations for
race conditions, and pub/sub for session invalidation events.
JWT-based "stateless sessions" avoid the shared store but cannot
be revoked before expiry - a tradeoff every architect must
consciously choose. Production systems often use both: JWT
access tokens (short TTL, stateless) + opaque refresh tokens
(Redis-backed, fully revocable).

---

### 📊 Entry Metadata

| #054 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-008 Session-Based Auth, ATH-015 Logout, ATH-047 Distributed Auth, ATH-053 Auth Server | |
| **Used by:** | ATH-056, ATH-057 | |
| **Related:** | ATH-008 Session-Based, ATH-053 Auth Server, ATH-057 IdP Design | |

---

### 📘 Textbook Definition

Distributed session management solves the fundamental problem
of session state in horizontally scaled applications: if user
session data is stored in-process on one server, and a load
balancer routes the next request to a different server, the
session is not found. Solutions: sticky sessions (route all
requests from a client to the same server - brittle), centralized
session store (all servers read/write to a shared Redis or
database), JWT-based stateless sessions (session state in the
token, no shared store, but cannot be revoked), or hybrid
(JWT access tokens + server-side refresh token tracking for
revocation). The centralized store approach adds network
latency per request (~1-3ms Redis) but enables instant session
revocation.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Distributed Session Strategies                 │
├──────────────────────┬─────────────────────────────────┤
│  Strategy            │ Trade-offs                      │
├──────────────────────┼─────────────────────────────────┤
│  In-memory (local)   │ Fast, no infra                  │
│  (NOT distributed)   │ Breaks with multiple instances  │
├──────────────────────┼─────────────────────────────────┤
│  Sticky sessions     │ Works with multiple instances   │
│  (load balancer)     │ Single point of failure         │
│                      │ No scale-in without session loss│
├──────────────────────┼─────────────────────────────────┤
│  Redis session store │ Fully distributed               │
│                      │ +1-3ms per request (Redis RTT)  │
│                      │ Full revocation capability      │
│                      │ TTL expiry + pub/sub invalidation│
├──────────────────────┼─────────────────────────────────┤
│  JWT (stateless)     │ Zero store - no Redis needed    │
│                      │ Cannot revoke before expiry     │
│                      │ Use short TTL (5-15 min max)    │
├──────────────────────┼─────────────────────────────────┤
│  JWT + Redis         │ Access token: JWT (short TTL)   │
│  hybrid (best)       │ Refresh token: Redis (long TTL) │
│                      │ Revocation: delete refresh token│
│                      │ Access tokens invalid after exp │
└──────────────────────┴─────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Session with Redis for distributed sessions**

```java
// Spring Session: transparent session management with Redis
// All session data stored in Redis - any instance handles it
@Configuration
@EnableRedisHttpSession(
    // Session timeout: 30 minutes of inactivity
    maxInactiveIntervalInSeconds = 1800,
    // Redis key namespace
    redisNamespace = "spring:session"
)
public class HttpSessionConfig {

    @Bean
    public LettuceConnectionFactory connectionFactory() {
        // Redis Sentinel for HA session store
        RedisSentinelConfiguration sentinelConfig =
            new RedisSentinelConfiguration()
                .master("mymaster")
                .sentinel("sentinel1", 26379)
                .sentinel("sentinel2", 26379);
        return new LettuceConnectionFactory(sentinelConfig);
    }
}

// Instant session invalidation (on logout or compromise):
@Service
public class SessionRevocationService {

    @Autowired
    private FindByIndexNameSessionRepository<
        ? extends Session> sessionRepository;

    public void revokeAllSessionsForUser(String userId) {
        // Finds and deletes ALL sessions for this user
        // Works across all running app instances
        Map<String, ? extends Session> sessions =
            sessionRepository.findByPrincipalName(userId);
        sessions.forEach((id, session) ->
            sessionRepository.deleteById(id));
        // Within milliseconds: any request with old
        // session cookie gets 401 Unauthorized
    }
}
```

---

*Authentication category: ATH | Entry: ATH-054 | v5.0*