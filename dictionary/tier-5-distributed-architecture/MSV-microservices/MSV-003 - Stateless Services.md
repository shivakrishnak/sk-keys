---
id: MSV-003
title: Stateless Services
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★☆☆
depends_on: MSV-001, MSV-002
used_by: MSV-014, MSV-023, MSV-068, MSV-069
related: MSV-004, MSV-012, MSV-083
tags:
  - microservices
  - architecture
  - foundational
  - scalability
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 3
permalink: /microservices/stateless-services/
---

# MSV-003 - Stateless Services

⚡ TL;DR - A stateless service stores no user session state
in memory; any instance can handle any request, making the
service trivially horizontally scalable.

| #003 | Category: Microservices | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Microservices Architecture | |
| **Used by:** | Load Balancing in Microservices, Blue-Green Deployment, Zero-Downtime Deployment, Graceful Shutdown | |
| **Related:** | Modular Monolith, API Gateway, Distributed Caching in Microservices | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have an e-commerce service. When a user logs in, the server
stores their session in memory: cart contents, auth token,
preferences. This works fine with one server. Then traffic
spikes - you add a second server. But User A's session is
on Server 1. When the load balancer routes their next request
to Server 2, they are logged out. Their cart is gone.

**THE BREAKING POINT:**
Your load balancer must implement "sticky sessions" - pinning
each user to one server permanently. Now you cannot take
Server 1 down for maintenance or deployment without logging
out half your users. You cannot scale down Server 1 under
low traffic. You cannot do rolling deploys. Every server is
carrying irreplaceable state, making it effectively unmovable.

**THE INVENTION MOMENT:**
This is exactly why stateless services were embraced as the
foundational principle of cloud-native microservices: remove
all in-process session state so that any instance is identical
and interchangeable, enabling scale-out, rolling deploys, and
crash recovery without data loss.

**EVOLUTION:**
Early web applications were almost universally stateful
(server-side session storage was the default in Struts,
JSF, and early Spring MVC). The 12-Factor App methodology
(Heroku, 2011) codified statelessness as Factor VI. JWT tokens
(2015 RFC) provided a portable, server-side-sessionless auth
mechanism that made stateless REST APIs practical.

---

### 📘 Textbook Definition

A **stateless service** is a service instance that holds no
durable, per-user session state between requests. All state
required to process a request must either be included in the
request itself (JWT token, request payload), retrieved from
an external store (database, cache), or reconstructed from
other services. Any instance of the service can handle any
request without prior knowledge of that client's history.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Stateless means every request is self-contained - no server
remembers the previous request.

**One analogy:**
> A vending machine is stateless: it doesn't remember who
> used it last. You insert your coins, make your selection,
> and get your item - each transaction is independent. A
> barista taking your "usual" order is stateful: they remember
> you. The vending machine can be replaced with another
> identical vending machine with no disruption.

**One insight:**
Stateless services trade server memory for external storage
access. Instead of O(1) in-memory lookup ("is this session
valid?"), you do a JWT validation (CPU, no I/O) or a cache
lookup (milliseconds, but external). The payoff is that you
can kill and restart any instance without losing data.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Any request must contain all information needed to process
   it, or that information must be retrievable from a shared
   external store accessible to all instances.
2. When an instance crashes or is replaced, no user request
   should fail because state was lost.
3. The load balancer must be able to route any request to
   any healthy instance without affinity constraints.

**DERIVED DESIGN:**
From invariant 1: authentication state moves to self-contained
JWT tokens (signed by the server, verified by the service
without a DB call) or to a shared cache (Redis). Shopping
cart state moves to the database. Pagination cursors move
to the request (offset/cursor-based pagination).
From invariant 2: instances become interchangeable cattle,
not pets. You can replace them at any time.
From invariant 3: load balancers use round-robin or
least-connections with no sticky sessions.

**THE TRADE-OFFS:**
**Gain:** Horizontal scaling without data loss, zero-downtime
rolling deploys, automatic crash recovery, simplified
load balancing.
**Cost:** Every request carries more data (larger tokens),
every state access hits an external store (latency), external
state store becomes a new failure point.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** State must live somewhere - moving it out of
the service does not eliminate it, just centralises it.
Managing the external state store (Redis HA, DB replicas)
is essential complexity.
**Accidental:** JWT validation overhead, cache round-trips,
and cache warm-up problems are accidental - better tooling
(local JWT caching, efficient serialisation) reduces them.

---

### 🧪 Thought Experiment

**SETUP:**
You have a service with 3 instances behind a load balancer.
Instance 2 stores User X's session in memory (logged in,
cart has 3 items). You deploy a new version requiring a
restart of Instance 2.

**WHAT HAPPENS WITH STATEFUL SERVICE:**
Instance 2 restarts, losing User X's session. Load balancer
routes User X's next request to Instance 2 (post-restart) -
the user is logged out. Their cart is empty. If sticky sessions
are configured, all users on Instance 2 lose their session
simultaneously during the deploy.

**WHAT HAPPENS WITH STATELESS SERVICE:**
Instance 2 restarts. User X's cart is in the database. Their
auth token is a JWT they hold in their browser cookie. Load
balancer routes their next request to Instance 1 or 3 - service
reads cart from DB, validates JWT locally, continues the
session transparently. The restart is invisible to the user.

**THE INSIGHT:**
Statelessness decouples the user experience lifecycle from
the server instance lifecycle. Users outlive server instances.
Server instances become temporary workers, not relationship
holders.

---

### 🧠 Mental Model / Analogy

> A stateless service is like a toll booth that accepts only
> exact change (self-contained tokens). The booth operator
> (service instance) doesn't need to remember you. You present
> your pre-paid card (JWT), the booth validates it and opens.
> If one booth closes, you go to the next one - same card,
> same result.

- "Pre-paid card" - JWT token containing identity and claims
- "Toll booth operator" - service instance
- "Card validation" - JWT signature verification (stateless)
- "Opening the gate" - authorised response
- "Booth closes" - service instance restarts
- "Go to next booth" - load balancer routes to another instance

Where this analogy breaks down: a real toll booth does not
need to look up your balance against a shared database.
Stateless services often still make DB calls per request
for state that cannot be embedded in the token.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A stateless service doesn't remember anything between requests.
Each request must bring everything the server needs. Like a
website with no login - every page is independent.

**Level 2 - How to use it (junior developer):**
Avoid storing anything in instance variables that is
per-user or per-session. Store user session data in JWT
tokens (for auth claims) or Redis (for mutable session
state like cart contents). Never use `HttpSession` in
Spring Boot if you need more than one instance.

**Level 3 - How it works (mid-level engineer):**
Stateless auth with JWT: the token contains user ID,
roles, and expiry. The service verifies the signature
using a shared secret (symmetric HMAC) or public key
(asymmetric RSA/EC). No database lookup needed. Stateless
pagination: pass an offset or cursor in the request rather
than storing "user is on page 4" in server memory.

**Level 4 - Why it was designed this way (senior/staff):**
The 12-Factor App principle VI ("Processes") states:
"Twelve-factor processes are stateless and share-nothing."
The architectural motivation was the elastic cloud: you
need to be able to add or remove instances in seconds based
on load. Any instance carrying unique state cannot be
removed without data loss. Statelessness is what makes
auto-scaling possible.

**Level 5 - Mastery (distinguished engineer):**
True statelessness is a spectrum, not a binary. Even a
"stateless" service has local caches (in-memory LRU for
JIT-compiled code, class loading state). The engineering
decision is which state is safe to lose (local cache -
worst case a cache miss, regenerated) vs which state must
be durable (user cart - must not be lost). Staff engineers
design the state tiering: ephemeral (instance memory),
shared-volatile (Redis), and durable (DB), and understand
the consistency and latency implications of each tier.

---

### ⚙️ How It Works (Mechanism)

**STATEFUL vs STATELESS REQUEST FLOW:**

```
STATEFUL:
─────────
Request → LB (sticky) → Instance 2 (owns session 42)
  → Session 42 found in memory → process → respond
  BUG: If LB routes to Instance 1, session 42 = NOT FOUND

STATELESS:
──────────
Request + JWT → LB (any instance) → Instance 1
  → Validate JWT signature locally (no DB)
  → Load user data from DB if needed
  → Process → respond
  OK: Any instance handles any request
```

**JWT TOKEN ANATOMY:**

```
Header.Payload.Signature

Header:  {"alg":"RS256","typ":"JWT"}
Payload: {
  "sub": "user-123",      ← user identity
  "roles": ["CUSTOMER"],  ← claims
  "exp": 1716000000       ← expiry (epoch seconds)
}
Signature: RSA-SHA256(header+payload, private_key)

Service validation:
  1. Decode header + payload (base64)
  2. Verify signature with public key (no DB call)
  3. Check exp > now()
  4. Trust claims if valid
```

**EXTERNAL STATE TIERING:**

```
┌─────────────────────────────────────────┐
│  Request (JWT + payload)                │
│  - auth claims    - request parameters  │
│  - API key        - idempotency key     │
└────────────────────┬────────────────────┘
                     │ missing state?
         ┌───────────┼───────────┐
         ▼           ▼           ▼
   Redis Cache    Session DB    Config
   (volatile)     (durable)     Store
   - rate limit   - cart        - feature
   - temp tokens  - preferences   flags
   TTL: seconds   TTL: weeks    TTL: hours
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Client (holds JWT in cookie/header)
  │
  ▼
Load Balancer (round-robin, no stickiness)
  │ routes to any healthy instance
  ▼
Service Instance A  ← YOU ARE HERE
  │ 1. Extract JWT from Authorization header
  │ 2. Verify JWT signature (local, no I/O)
  │ 3. Check JWT expiry
  │ 4. Load required state from Redis/DB
  │ 5. Process business logic
  │ 6. Return response
  ▼
Client receives response
```

**FAILURE PATH:**

```
Service Instance A crashes mid-processing
  → Load balancer detects failed health check
  → Removes Instance A from rotation
  → Client retries (idempotent GET) → routes to Instance B
  → Instance B processes from scratch using JWT + DB
  → No data loss (state is in DB, not Instance A)
```

**WHAT CHANGES AT SCALE:**
At 100 instances, the load balancer distributes load with no
affinity constraints. Auto-scaling adds/removes instances in
seconds based on CPU/RPS metrics. At 10,000 RPS, JWT validation
overhead (RSA verify: ~1ms per request) becomes measurable -
a local in-memory cache of validated token hashes reduces this
to a hash lookup.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: session state in Spring Boot**

```java
// BAD: storing session state in HttpSession (server memory)
@RestController
public class CartController {

    @GetMapping("/cart")
    public Cart getCart(HttpSession session) {
        // BREAKS with multiple instances!
        return (Cart) session.getAttribute("cart");
    }

    @PostMapping("/cart/items")
    public void addItem(HttpSession session,
                        @RequestBody Item item) {
        Cart cart = (Cart) session.getAttribute("cart");
        cart.add(item);
        session.setAttribute("cart", cart); // in-memory!
    }
}
```

```java
// GOOD: state in DB, identity from JWT
@RestController
@RequiredArgsConstructor
public class CartController {

    private final CartRepository cartRepo;

    @GetMapping("/cart")
    public Cart getCart(
            @AuthenticationPrincipal JwtUser user) {
        // user.getId() extracted from JWT - no DB lookup
        return cartRepo.findByUserId(user.getId());
    }

    @PostMapping("/cart/items")
    public void addItem(
            @AuthenticationPrincipal JwtUser user,
            @RequestBody Item item) {
        Cart cart = cartRepo.findByUserId(user.getId());
        cart.add(item);
        cartRepo.save(cart); // state in DB - any instance
    }
}
```

**Example 2 - Production: JWT validation with caching**

```java
// JWT validation is ~1ms (RSA). At 1000 RPS = 1000ms/s
// of CPU just on validation. Cache recently validated tokens:
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    // Caffeine cache: validated token hash → user claims
    // Max 10000 entries, expire after 1 minute
    private final Cache<String, Claims> tokenCache =
        Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(1, TimeUnit.MINUTES)
            .build();

    @Override
    protected void doFilterInternal(
            HttpServletRequest req,
            HttpServletResponse res,
            FilterChain chain) {
        String token = extractToken(req);
        Claims claims = tokenCache.get(
            token,
            t -> jwtParser.parseClaimsJws(t).getBody()
        );
        // Set security context from cached claims
        SecurityContextHolder.getContext()
            .setAuthentication(toAuth(claims));
        chain.doFilter(req, res);
    }
}
```

**How to test / verify correctness:**
Test statelessness by running two service instances and
making alternating requests to each via a load balancer.
Verify that a request to Instance 2 succeeds after state
was created in Instance 1 with no sticky sessions. Use
`curl -c cookies.txt` and `curl -b cookies.txt` to simulate
a browser session across instances.

---

### ⚖️ Comparison Table

| State Strategy | Scalability | Latency | Complexity | Best For |
|---|---|---|---|---|
| **In-memory session (stateful)** | None (sticky sessions) | ~0ms | Low | Single instance, dev env |
| JWT token (stateless) | Unlimited | ~1ms (validation) | Medium | Auth claims, roles |
| Redis session (external) | High | ~1-5ms (cache hit) | Medium | Mutable session data |
| Database state | High | ~5-50ms | Low | Durable user state |
| Event sourcing | High | Variable | High | Audit trail, replay |

**How to choose:** Use JWT for immutable auth claims (avoid DB
on every request). Use Redis for mutable per-user state that
needs sub-second TTL management (shopping cart, temp tokens).
Use the database for durable state (order history, preferences).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Stateless means no state at all | State exists - it's moved to an external store (DB, cache). Stateless means no instance-local state. |
| JWT is always stateless | A JWT blocklist (for logout/revocation) re-introduces server-side state. Truly stateless JWT cannot be revoked before expiry. |
| Stateless services need no caching | They often need MORE caching (Redis for session state, token validation cache) because every request hits external stores. |
| Spring Boot is stateless by default | Not with HttpSession enabled. `spring.session.store-type=redis` must be configured explicitly for multi-instance deployments. |

---

### 🚨 Failure Modes & Diagnosis

**Sticky sessions creeping in**

**Symptom:**
Rolling deploy causes ~50% of users to experience 401 errors
or empty carts for one minute during the deploy.

**Root Cause:**
Load balancer has sticky sessions enabled. When the sticky
instance is restarted, all its users lose their in-memory
session data before being re-routed to healthy instances.

**Diagnostic Command:**
```bash
# Check Kubernetes service sessionAffinity
kubectl get service order-service -o yaml \
  | grep -A3 "sessionAffinity"

# Should be: sessionAffinity: None
# BAD:       sessionAffinity: ClientIP

# Check if Nginx has ip_hash (sticky)
grep -r "ip_hash" /etc/nginx/
```

**Fix:**
```yaml
# Kubernetes service - disable sticky sessions
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  sessionAffinity: None  # stateless - any pod handles any req
  selector:
    app: order-service
```

Move all session state to Redis and enable
`spring.session.store-type=redis`.

**Prevention:**
Add architecture conformance test: any service deployment
must pass a "sticky session disabled" check in CI.

---

**JWT token too large - header size exceeded**

**Symptom:**
Some requests return HTTP 431 (Request Header Fields Too Large)
or Nginx `client_max_header_size` errors. Users with many
roles or permissions are affected more than others.

**Root Cause:**
JWT payload has grown to include the user's full permission
list (hundreds of permissions), making the token 8-20KB.
Default Nginx header limit is 8KB.

**Diagnostic Command:**
```bash
# Check JWT size in production
echo "Bearer $TOKEN" | awk '{print length($2)}' # bytes

# Decode JWT payload (no verification)
echo "$JWT" | cut -d. -f2 | base64 -d | jq . | wc -c
```

**Fix:**
```java
// BAD: embed all permissions in JWT
Map<String, Object> claims = Map.of(
    "sub", user.getId(),
    "permissions", user.getAllPermissions()  // 500 items!
);

// GOOD: embed only roles, look up fine-grained permissions
// in a permission service cache on first use
Map<String, Object> claims = Map.of(
    "sub", user.getId(),
    "roles", user.getRoles()  // 2-5 roles max
);
// Permissions cached in Redis keyed by userId:
// redis GET perm:user-123 → ["ORDER_READ","ORDER_WRITE"]
```

**Prevention:**
Set a hard limit on JWT payload size in your token minting
service. Alert when average token size exceeds 1KB.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Monolith vs Microservices` - understanding WHY stateless
  services are necessary in a distributed deployment model
- `HTTP and APIs` - HTTP is the protocol over which stateless
  services communicate; understanding request/response is
  foundational

**Builds On This (learn these next):**
- `Load Balancing in Microservices` - statelessness is what
  makes pure load balancing (no sticky sessions) possible
- `Blue-Green Deployment` - requires stateless services to
  cut traffic between environments without user disruption
- `Distributed Caching in Microservices` - where the state
  that was removed from the service must now live

**Alternatives / Comparisons:**
- `Stateful services (sticky session)` - simpler to build,
  impossible to scale horizontally without data loss
- `Event Sourcing` - an alternative state model where state
  is derived from events rather than stored directly

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Service instance that holds no per-user   │
│              │ state in memory between requests          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Sticky sessions that prevent scaling,     │
│ SOLVES       │ rolling deploys, and auto-recovery        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ State is NOT eliminated - it moves to     │
│              │ JWT tokens, Redis, or the database        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any service that must run as more than    │
│              │ one instance (almost always)              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-instance dev tools, CLI scripts,  │
│              │ single-user batch processors              │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ HttpSession with in-memory store behind   │
│              │ a load balancer - users lose session      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Horizontal scale + rolling deploys vs     │
│              │ external state store round-trip latency   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Kill any instance, lose no user data -   │
│              │  that's what stateless buys you"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JWT Token → Redis Session Store           │
│              │ → Load Balancing in Microservices         │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Stateless does not mean no state - it means no
   instance-local state. State moves to JWT, Redis, or DB.
2. Sticky sessions are the enemy of horizontal scaling and
   rolling deploys. Diagnose and eliminate them.
3. JWT tokens must be bounded in size and must contain only
   roles/identity - not large permission lists.

**Interview one-liner:**
"A stateless service holds no per-user session in memory.
Any instance handles any request. Auth state moves to JWT
tokens (self-validating, no DB), mutable session state moves
to Redis, and durable state stays in the DB. This is what
makes auto-scaling and zero-downtime deploys possible."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Shared mutable state is the root of coordination complexity.
Remove it from the hot path and you remove the need to
coordinate between instances. This principle applies at
every level: thread-safe code (immutable objects), distributed
systems (stateless services), and functional programming
(pure functions).

**Where else this pattern appears:**
- HTTP itself is a stateless protocol - each request carries
  all necessary context; cookies are the "external state store"
- RESTful API design - each request is self-descriptive;
  no server-side conversation state
- Kubernetes pods - designed to be replaceable cattle;
  any pod handles any request

**Industry applications:**
- Financial services APIs - stateless REST APIs with JWT for
  auth, Redis for rate limiting counters, DB for account state
- Global CDNs - stateless edge servers handle any request
  for any user; user data lives in origin DB

---

### 💡 The Surprising Truth

The JWT standard (RFC 7519) was designed to be cryptographically
verifiable without a database lookup, yet the most common JWT
implementation mistake is storing a JWT ID (jti) in a database
and looking it up on every request to check revocation - making
the "stateless" token as stateful as a session ID. Truly
stateless JWTs cannot be revoked before they expire, which is
why most production systems choose short expiry (15 minutes)
with a refresh token strategy, rather than long-lived JWTs
that can never be invalidated.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Explain to a junior engineer why `HttpSession`
   breaks with two service instances and what concrete change
   (Redis session store + Spring Session) fixes it.
2. **DEBUG** Given a production incident where 40% of users
   experience login failures during a rolling deploy, identify
   whether the root cause is sticky sessions, JWT expiry during
   deploy, or a Redis connection pool issue.
3. **DECIDE** A service needs to track "has the user seen
   this onboarding tutorial." Should this state be in the JWT
   token, Redis, or the database? Justify based on mutability,
   TTL, and size constraints.
4. **BUILD** Migrate a Spring Boot application from HttpSession
   to Redis-backed session using `spring-session-data-redis`,
   including configuration for session serialization and TTL.
5. **EXTEND** Apply statelessness reasoning to a WebSocket
   service (which maintains a persistent connection per user).
   Is it stateless? What happens when you restart the instance?
   How would you design it to be crash-resilient?

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service issues JWTs with a 24-hour expiry.
A security incident means all tokens issued in the last 12 hours
must be invalidated immediately. Without a token blocklist
(which adds state), how do you handle this? What are the
operational trade-offs of each approach (rotate signing key,
maintain a blocklist, reduce token TTL)?
*Hint: Consider the trade-off between the stateless ideal
and operational security requirements.*

**Q2.** You have a stateless order service running 10 instances.
A database migration adds a new required column to the orders
table. During the migration window (30 minutes), old service
instances cannot write the new column and new instances
require it. How do you deploy this migration without downtime,
given that the service is stateless but the database is not?
*Hint: Think about expand-contract (parallel change) pattern
at the schema level.*

**Q3.** Design the state architecture for a multiplayer
real-time game backend where 1000 concurrent users each
maintain a game session with 50KB of state. Your goal is
stateless services that auto-scale. Where does each type
of state live, what is the latency budget per request, and
what happens when a Redis instance fails mid-game?
*Hint: Distinguish between state that must survive a server
crash (durable) and state that can be reconstructed (volatile).*

---

### 🎯 Interview Deep-Dive

**Q1: "What does it mean for a service to be stateless,
and why does it matter for scaling?"**

*Why they ask:* Tests foundational cloud-native knowledge
before discussing Kubernetes auto-scaling.

*Strong answer includes:*
- No per-user in-memory session: any instance handles any request
- Makes round-robin load balancing correct (no sticky sessions)
- Enables rolling deploys: instance can be killed mid-session
  without data loss
- Enables auto-scaling: spin up 20 instances on traffic spike,
  kill 18 when it drops - no user impact

**Q2: "How does JWT provide stateless authentication?
What are its limitations?"**

*Why they ask:* Tests understanding of auth mechanism behind
stateless services.

*Strong answer includes:*
- JWT: signed token containing user identity and claims;
  service verifies signature with public key locally - no DB
- Limitation 1: cannot revoke before expiry - once issued,
  valid until `exp` (use short TTL + refresh tokens)
- Limitation 2: payload grows with claims - keep tokens small,
  look up permissions separately
- Limitation 3: signing key rotation requires all tokens
  to be re-issued or dual-key validation during transition

**Q3: "Describe a production bug caused by a service not
being truly stateless. How did you discover it and fix it?"**

*Why they ask:* Tests real-world experience with a common
microservices failure mode.

*Strong answer includes:*
- Common pattern: in-memory cache with no expiry seeded at
  startup; instance A has fresh data, instance B has stale
  data, load balancer alternates users between them producing
  inconsistent behavior
- Discovery: users report "sometimes my settings save,
  sometimes they don't" - a non-deterministic bug; distributed
  tracing shows alternating responses from two instances
- Fix: move to Redis with explicit TTL; add `Cache-Control:
  no-store` on endpoints where staleness is unacceptable