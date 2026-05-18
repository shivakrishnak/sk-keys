---
id: SYD-007
title: Horizontal Scaling
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: SYD-006
used_by: SYD-008, SYD-014
related: SYD-006, SYD-008, SYD-014, SYD-019
tags:
  - architecture
  - foundational
  - performance
  - mental-model
  - distributed-systems
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/syd/horizontal-scaling/
---

⚡ TL;DR - Horizontal scaling means adding more servers
to share load - the path to near-unlimited capacity,
at the cost of distributed systems complexity.

| #007 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Vertical Scaling | |
| **Used by:** | Load Balancing, Auto Scaling | |
| **Related:** | Vertical Scaling, Load Balancing, Auto Scaling, Redundancy and Failover | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your API server handles 500 requests/second on one
machine. Traffic grows to 5,000 req/s. Vertical scaling
to the largest available instance gets you to 2,000 req/s
before hitting the hardware ceiling. You are stuck at
2,000 req/s with no further options. The system is
permanently capacity-constrained.

**THE BREAKING POINT:**
Every single server has an absolute capacity ceiling.
At large enough scale, that ceiling is always insufficient.
To grow beyond the ceiling of any single machine, you
must distribute work across many machines. This is the
fundamental problem horizontal scaling solves.

**THE INVENTION MOMENT:**
Horizontal scaling emerged as a practical architecture
when commodity servers became cheap enough that running
10 small servers cost less than one large server with
equivalent aggregate capacity. Google and Amazon
pioneered the "commodity hardware at scale" approach
in the early 2000s. This made horizontal scaling the
default architecture for internet-scale services.

**EVOLUTION:**
Before cloud computing, horizontal scaling required
buying racks of servers, complex networking, and custom
load balancing hardware (physical F5 appliances). This
made it accessible only to large organizations with
infrastructure teams. Cloud computing democratized
horizontal scaling: an auto-scaling group on AWS can
add a new server in 60 seconds and remove it when
no longer needed. Today, any team can build a
horizontally scaled system without owning hardware.

---

### 📘 Textbook Definition

Horizontal scaling (scale out) is the practice of
increasing system capacity by adding more machines
(nodes) to a resource pool rather than upgrading the
capabilities of existing machines. Work is distributed
across nodes, typically by a load balancer or
coordination service. Horizontal scaling is theoretically
unbounded (limited only by cost and coordination
overhead) and eliminates single points of failure.
However, it introduces distributed systems complexity:
state coordination, network partitions, consensus
protocols, and data consistency challenges that do not
exist in single-server architectures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Horizontal scaling means adding more servers to share
the load, rather than making one server bigger.

**One analogy:**
> Hiring more cashiers at a checkout line instead of
> making one cashier faster. Each new cashier handles
> their own customers. The maximum throughput scales
> with the number of cashiers. But now you need a
> queue manager to assign customers to cashiers -
> that is the load balancer.

**One insight:**
Horizontal scaling is the only scaling strategy without
a hard ceiling. But "no ceiling" comes at the cost of
having to solve the hardest problems in computer
science: distributed state, network partitions, and
eventual consistency.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each additional server adds approximately the same
   capacity (near-linear scaling) for stateless workloads.
2. State cannot be stored on individual servers if
   any server can handle any request - state must be
   externalized (database, Redis, etc.).
3. A load balancer is required to distribute requests
   to the server pool.
4. Coordination overhead grows with the number of nodes
   for stateful or coordinated workloads.

**DERIVED DESIGN:**
Given the statelessness requirement:
- Store session state in external systems (Redis,
  DynamoDB, database) not in-process
- Store local caches and re-warm them on startup, or
  accept temporary cold-cache performance degradation
  when nodes are replaced
- Design requests to be idempotent where possible -
  any node handling a retry must produce the same result

**THE TRADE-OFFS:**

**Gain:** No hard ceiling; eliminates SPOF; instances
can be replaced without downtime; can use spot/preemptible
instances for cost savings.

**Cost:** Statelessness requirement; distributed state
management; need for load balancer; network latency
between components; more complex observability.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The fundamental constraint is that
distributed state is genuinely harder than local state.
Coordination overhead is real. Network partitions
happen. These are not implementation details - they are
inherent to distribution.

**Accidental:** Session stickiness workarounds (sticky
sessions) are accidental complexity added to paper
over a stateful application design that was not built
for horizontal scale.

---

### 🧪 Thought Experiment

**SETUP:**
An online store has one API server and one database.
Both are maximally vertically scaled. Black Friday brings
a 10x traffic spike. What changes when you horizontally
scale the API tier?

**BEFORE:**
- API server: 1 server handles all 100 req/s
- Database: 1 server handles all queries
- Failure: either server down = full outage

**AFTER (API tier horizontally scaled to 10 servers):**
- Load balancer distributes 1,000 req/s across 10
  servers, each handling 100 req/s
- Database: unchanged - now the bottleneck
- Failure: 1 of 10 servers failing = 10% less capacity,
  not a full outage

**THE INSIGHT:**
Horizontal scaling at one tier moves the bottleneck
to the next tier. You scaled the API layer. Now the
database is the bottleneck. Scaling a system end-to-end
often requires horizontal scaling at every tier: API,
cache, database (read replicas or sharding), message
queue. Each tier adds its own complexity.

---

### 🧠 Mental Model / Analogy

> Horizontal scaling is like a highway adding lanes.
> One lane handles a fixed number of cars per minute.
> Three lanes handle 3x as many cars. Ten lanes handle
> 10x as many. The highway's capacity scales with
> the number of lanes - theoretically without limit.
> But the on-ramp (load balancer) becomes the new
> potential bottleneck, and all lanes need to connect
> to the same destinations (shared database, shared
> storage).

- "Adding lanes" → adding server instances
- "On-ramp" → load balancer
- "Cars" → requests
- "Highway exit" → shared backend (database)
- "Traffic jam at exit" → database bottleneck

**Where this analogy breaks down:**
Unlike highway lanes, servers can process requests
in parallel across multiple steps - a request can
take varying amounts of work, unlike car travel time
which is mostly fixed. Also, servers fail and recover
in ways that lanes do not.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of buying a bigger, more powerful single server,
you add more servers and split the work among them.
Like opening more checkout lanes at a supermarket
instead of training one super-fast cashier.

**Level 2 - How to use it (junior developer):**
Configure your application to be stateless (no local
session storage). Put a load balancer in front of
multiple identical server instances. When CPU hits
70%, add another server. Critically: move session state
to Redis, and move uploaded files to S3, so any server
can handle any request.

**Level 3 - How it works (mid-level engineer):**
For stateless HTTP services, horizontal scaling is
near-linear: 5 servers can handle ~5x the load of 1.
The load balancer adds a network hop (~0.5ms in the
same datacenter, negligible). The real work is
externalizing state: sessions to Redis, file storage
to object stores, configuration to environment
variables or config servers.

**Level 4 - Why it was designed this way (senior/staff):**
The architecture requirement for statelessness is not
arbitrary - it ensures that the load balancer can
route any request to any server without that server
needing request-specific prior state. This enables
zero-downtime deployments (replace servers one at a
time), auto-healing (replace failed servers without
data loss), and auto-scaling (add/remove servers based
on demand without state migration).

**Level 5 - Mastery (distinguished engineer):**
Horizontal scaling's complexity is not in the API
layer - making that stateless is tractable. The hard
problems are: (1) horizontally scaling the database
tier (sharding, distributed transactions, consistency
models); (2) distributed cache invalidation (what
happens when 100 servers each have a stale local cache?);
(3) distributed rate limiting (how do you limit a user
to 1,000 requests/hour when requests are spread across
100 servers?); (4) distributed tracing when a single
request touches 20 servers. Most of system design
interview difficulty comes from these second-order
horizontal scaling problems.

---

### ⚙️ How It Works (Mechanism)

**The horizontal scaling architecture:**

```
┌───────────────────────────────────────────────┐
│ BEFORE (vertical only)                        │
│                                               │
│   Client → [Single Big Server]                │
│                                               │
│   Capacity: 1x. SPOF.                        │
└───────────────────────────────────────────────┘

┌───────────────────────────────────────────────┐
│ AFTER (horizontal scale)                      │
│                                               │
│   Client                                      │
│     → [Load Balancer]                         │
│          → [Server A]   ─┐                   │
│          → [Server B]    ├─→ [Shared DB]      │
│          → [Server C]    ├─→ [Redis Cache]    │
│          → [Server D]   ─┘                   │
│                                               │
│   Capacity: 4x. No SPOF at server tier.      │
└───────────────────────────────────────────────┘
```

**Stateless requirement - what must be externalized:**

```
┌─────────────────────────────────────────────────┐
│ LOCAL STATE (blocks horizontal scaling)         │
│   Session data stored in-process (memory)       │
│   Uploaded files on local filesystem            │
│   Scheduled jobs on one specific server         │
│   WebSocket connections with server affinity    │
│   In-process caches (Caffeine, Guava)           │
├─────────────────────────────────────────────────┤
│ EXTERNAL STATE (enables horizontal scaling)     │
│   Sessions → Redis / DynamoDB / Memcached       │
│   Files → S3 / GCS / Azure Blob                 │
│   Jobs → distributed scheduler (Quartz cluster, │
│           Celery, AWS EventBridge)              │
│   WebSockets → sticky sessions or external      │
│                connection registry              │
│   Caches → Redis cluster or re-warm on start   │
└─────────────────────────────────────────────────┘
```

**How capacity scales:**

```
┌─────────────────────────────────────────────────┐
│ SCALING CURVE (stateless workload)              │
│                                                 │
│ Throughput                                      │
│   ^                                             │
│   │                         ╭── ideal (linear)  │
│   │                   ╭─────╯                   │
│   │              ╭────╯                         │
│   │        ╭─────╯ actual (coordination         │
│   │  ╭─────╯        overhead grows slightly)    │
│ ──┼──╯──────────────────────────►               │
│       1    2    4    8   Servers                 │
│                                                 │
│ Stateless workloads approach linear scaling.    │
│ Stateful workloads see coordination overhead.   │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (adding a server to the pool):**
```
[Traffic spike detected]
  → [Auto-scaling trigger fires] (CPU > 70% for 5 min)
  → [New server instance launched from AMI/container]
  → [Health check passes] (GET /health → 200 OK)
  → [Load balancer adds instance to rotation]
  → [Traffic distributed to N+1 servers]
  → [CPU drops back below threshold]
```

**FAILURE PATH (server removed from pool):**
```
[Server A health check fails 3 times]
  → [Load balancer removes Server A from rotation]
  → [In-flight requests to Server A: connection errors]
  → [Client retries hit Server B or C] (if idempotent)
  → [Auto-healing: new Server D launched to replace A]
  → [No user-visible outage if retry logic is correct]
```

**WHAT CHANGES AT SCALE:**
- At 10 servers: load balancer is a potential SPOF
  (solution: redundant LB in active-passive or
  active-active configuration)
- At 100 servers: server startup time matters - slow
  AMI initialization causes delayed scaling response
  (solution: pre-warm instances, baked AMIs, containers)
- At 1000 servers: coordination becomes expensive -
  distributed locking, centralized config, and log
  aggregation become serious engineering concerns

---

### 💻 Code Example

**Example 1 - The statelessness refactor**
```java
// BAD: Session stored in-memory (blocks horizontal scale)
// If Server B gets the next request, the session is gone
@RestController
public class CartController {
    // Stored per-process: dies with the server
    private final Map<String, List<Item>> sessions
        = new ConcurrentHashMap<>();

    @PostMapping("/cart/add")
    public void addItem(
        @RequestHeader("Session-Id") String sessionId,
        @RequestBody Item item) {
        sessions
            .computeIfAbsent(sessionId, k -> new ArrayList<>())
            .add(item);
    }
}

// GOOD: Session stored in Redis (any server can serve it)
@RestController
public class CartController {
    private final RedisTemplate<String, List<Item>> redis;

    @PostMapping("/cart/add")
    public void addItem(
        @RequestHeader("Session-Id") String sessionId,
        @RequestBody Item item) {
        String key = "cart:" + sessionId;
        List<Item> cart = redis.opsForValue().get(key);
        if (cart == null) cart = new ArrayList<>();
        cart.add(item);
        // 30-minute TTL, survives server replacement
        redis.opsForValue().set(key, cart, 30, MINUTES);
    }
}
```

**Example 2 - Health check for load balancer**
```java
// GOOD: Health endpoint that checks all dependencies
// Load balancer uses this to decide if server can
// receive traffic. Must be fast (< 100ms).
@RestController
public class HealthController {

    private final DataSource dataSource;
    private final RedisTemplate<?, ?> redis;

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> status = new HashMap<>();
        boolean healthy = true;

        // Check DB connectivity
        try (Connection c = dataSource.getConnection()) {
            c.createStatement().execute("SELECT 1");
            status.put("db", "UP");
        } catch (Exception e) {
            status.put("db", "DOWN: " + e.getMessage());
            healthy = false;
        }

        // Check Redis
        try {
            redis.getConnectionFactory()
                 .getConnection().ping();
            status.put("cache", "UP");
        } catch (Exception e) {
            status.put("cache", "DOWN");
            // Degraded but not completely down
        }

        return ResponseEntity
            .status(healthy ? 200 : 503)
            .body(status);
    }
}
```

**Example 3 - Distributed rate limiting**
```java
// BAD: In-process counter (wrong with horizontal scale)
// Each server has its own counter: user can make
// N requests to EACH of 10 servers = 10x the limit
public class RateLimiter {
    private final Map<String, AtomicInteger> counts
        = new ConcurrentHashMap<>();

    public boolean allow(String userId) {
        return counts
            .computeIfAbsent(userId, k -> new AtomicInteger())
            .incrementAndGet() <= 100; // per minute
    }
}

// GOOD: Redis-based distributed counter
// Shared across all servers: enforces limit globally
public class DistributedRateLimiter {
    private final StringRedisTemplate redis;

    public boolean allow(String userId) {
        String key = "rate:" + userId + ":"
            + Instant.now().getEpochSecond() / 60;
        Long count = redis.opsForValue()
            .increment(key);
        if (count == 1) {
            // Set expiry on first increment
            redis.expire(key, 2, TimeUnit.MINUTES);
        }
        return count <= 100;
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Vertical Scaling | Horizontal Scaling |
|---|---|---|
| Capacity ceiling | Hardware limit (~TB RAM) | Near-unlimited |
| Application changes | None required | Statelessness required |
| Cost model | Superlinear | Linear |
| SPOF | Remains | Eliminated at server tier |
| State management | Local (simple) | External (complex) |
| Deployment | Restart/resize | Rolling, zero-downtime |
| Best for | Databases, quick fixes | Stateless services at scale |

**How to choose:**
Horizontal scaling is the standard choice for API
servers, web servers, and any stateless compute layer.
Vertical scaling remains competitive for databases
and stateful services where the coordination cost of
distribution outweighs the benefit of horizontal scale.
Most production systems combine both.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Just add more servers" is easy | Stateful applications require significant refactoring to externalize state before horizontal scaling works correctly |
| Horizontal scaling eliminates all SPOFs | It eliminates the server-tier SPOF but creates new potential SPOFs: load balancer, shared database, Redis cluster, shared network switch |
| Horizontal = always cheaper than vertical | For small scale (2-3 servers), the operational overhead of load balancers and distributed state often makes it more expensive than one larger server |
| Container = automatically horizontally scalable | Containers are easy to replicate, but if the containerized app stores state locally, horizontal scaling still breaks correctness |

---

### 🚨 Failure Modes & Diagnosis

**State Corruption from Horizontal Scaling a Stateful App**

**Symptom:**
After scaling from 1 to 3 API servers, users randomly
lose their shopping cart contents. About 2/3 of requests
cause cart to appear empty. Support tickets spike.

**Root Cause:**
Session state was stored in the JVM heap of individual
servers. The load balancer distributes requests across
all 3 servers. When Server A handled login and stored
the cart, the next request went to Server B (no cart).

**Diagnosis:**
```bash
# Simulate: send 10 requests, see which server responds
# (requires server to identify itself in response header)
for i in $(seq 1 10); do
  curl -s -o /dev/null -D - https://app.example.com/ \
    | grep X-Served-By
done
# If responses show different servers: stateless check
# needed before scaling

# Check if sessions are being lost
# Enable session debug logging in Spring Boot:
# logging.level.org.springframework.session=DEBUG
# Then look for: "Cannot retrieve session with id: XYZ"
```

**Fix:**
```yaml
# Spring Boot: switch to Redis session storage
# application.yml
spring:
  session:
    store-type: redis
  data:
    redis:
      host: redis.internal
      port: 6379
```

**Prevention:**
Before horizontal scaling, run load tests with multiple
instances and verify session-dependent flows complete
correctly across server boundaries. A single integration
test that adds to cart, switches to a different server,
and reads cart verifies this.

---

**The Thundering Herd After Scale-In**

**Symptom:**
Traffic drops overnight. Auto-scaling removes 8 of 10
servers (scale-in). At 8 AM, traffic returns to peak.
All 2 remaining servers overload before new servers
spin up. Several minutes of errors.

**Root Cause:**
Scale-in happened too aggressively. New server startup
time (including health checks, warmup) is 90 seconds.
Traffic spike outruns the scale-out response time.

**Diagnostic:**
```bash
# Check auto-scaling activity log (AWS)
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name my-app-asg \
  --max-items 50 \
  --query 'Activities[*].{Status:StatusCode,
    Time:StartTime, Cause:Cause}' \
  --output table
# Look for: rapid scale-in at 2 AM, then
# scale-out failures at 8 AM
```

**Fix:**
Configure scale-in protection during known traffic
buildup windows. Set minimum instance count based on
baseline traffic, not zero. Use scheduled scaling
for predictable traffic patterns:
```bash
# AWS: pre-scale before morning traffic ramp
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name my-app-asg \
  --scheduled-action-name pre-morning-scale \
  --recurrence "0 7 * * 1-5" \
  --min-size 5 \
  --desired-capacity 8
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Vertical Scaling` - the alternative approach;
  understanding why vertical has a ceiling motivates
  the need for horizontal scaling

**Builds On This (learn these next):**
- `Load Balancing` - required companion to horizontal
  scaling; distributes requests across the server pool
- `Auto Scaling` - automating the add/remove of
  horizontal scale based on demand metrics

**Alternatives / Comparisons:**
- `Vertical Scaling` - simpler; right for stateful
  services; complementary rather than exclusive

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Adding more servers to share load,       │
│              │ instead of making one server bigger      │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Bypassing the single-server hardware     │
│ SOLVES       │ ceiling; eliminating the server-tier SPOF│
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Works only if the application is         │
│              │ stateless - state must be externalized   │
│              │ to a shared store (Redis, DB)            │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Need unlimited scale; stateless services;│
│              │ availability requirements demand SPOF    │
│              │ elimination; at vertical scale ceiling   │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Small scale (1-2 servers); cost of       │
│              │ distributed state > benefit of scale;    │
│              │ application has irreducible local state  │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Horizontally scaling a stateful app      │
│              │ (leads to split-brain, lost sessions)    │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Near-unlimited scale vs. statelessness   │
│              │ requirement + distributed complexity     │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Scale out for stateless tiers; the cost │
│              │  is externalizing state, which you need  │
│              │  for reliability anyway."                │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Load Balancing → Auto Scaling →          │
│              │ Consistent Hashing                       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. No hardware ceiling - horizontal scaling can grow
   to any capacity, bounded only by cost.
2. Statelessness is the price - every server must be
   able to handle any request; local state breaks this.
3. New SPOFs emerge - you eliminated the server SPOF
   but the load balancer and shared state store are now
   potential SPOFs requiring their own HA design.

**Interview one-liner:**
"Horizontal scaling means adding more servers to share
load. It has no hard ceiling but requires statelessness:
any server must be able to handle any request, so all
persistent state must live in an external shared store
like Redis or a database. The load balancer is the
required companion that distributes requests across
the server pool."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Distribution is the mechanism for escaping single-
machine limits, but distribution always adds coordination
overhead. The fundamental question is: for this
particular problem, does the gain from distribution
(unlimited scale, fault tolerance) exceed the cost
of coordination (complexity, latency, consistency
challenges)?

**Where else this pattern appears:**
- **Database sharding** - horizontal scaling applied
  to the data tier: split data across multiple database
  servers instead of making one bigger.
- **Microservices** - horizontal scaling applied to
  the application tier: split the application into
  independent services that scale independently.
- **CDN** - horizontal scaling applied to content
  delivery: many edge servers instead of one central
  server; requests go to the geographically nearest node.
- **MapReduce/Spark** - horizontal scaling applied
  to data processing: split a large computation across
  many worker nodes in parallel.

**Industry applications:**
- **Google's web index** - petabytes of data distributed
  across thousands of commodity servers, each holding
  a shard of the index. No single server could hold
  the whole index; horizontal scaling is the only option.
- **Netflix** - 100+ microservices, each horizontally
  scaled independently based on demand. During peak
  viewing (8-10 PM), the video streaming service scales
  to thousands of instances. At 4 AM, it scales back.
- **Payment processors** - horizontally scaled API
  tiers with distributed rate limiting, idempotency
  keys, and centralized distributed locks to prevent
  double-processing of the same transaction across
  multiple servers.

---

### 💡 The Surprising Truth

The first cloud-scale internet services (Google, Amazon)
did not use horizontal scaling because it was a better
architecture - they used it because their traffic
was growing so fast that even the most expensive server
available could not keep up. They effectively had no
choice. The stateless design principles, shared-nothing
architecture, and externalized state patterns that are
now taught as best practices were engineering solutions
to an economic and physical necessity. The lesson: the
best architectural patterns often emerge not from
upfront design but from solving the problems that
appear as scale forces your hand. You learn what
"good architecture" means when you have no choice
but to get it right.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Describe to a non-technical stakeholder
   why adding more servers requires the application
   to be stateless, using a concrete example they
   will understand.
2. [DEBUG] Given a horizontally scaled application
   where users randomly lose session data, diagnose
   the root cause and describe the fix.
3. [DESIGN] Take a Spring Boot application that stores
   sessions in-process and describe the minimum changes
   needed to make it correctly horizontally scalable.
4. [DECIDE] Given a system with 3 components (API
   server, database, cache), explain which components
   are candidates for horizontal scaling and which
   should be vertically scaled first, and why.
5. [OPERATE] Explain how to configure an auto-scaling
   group to avoid the scale-in/thundering-herd failure
   mode described in the failure modes section.

---

### 🧠 Think About This Before We Continue

**Q1.** A social media platform needs to handle file
uploads. Currently, uploaded files are stored on the
local filesystem of the API server. When they horizontally
scale to 5 servers, users report that uploaded photos
randomly appear or disappear. What is happening and
how would you redesign this to work correctly with
horizontal scaling?

*Hint: Think about which server stores the file versus
which server handles the view request. They are not
always the same server. The fix requires externalizing
file storage to a shared location.*

**Q2.** A startup starts with 1 API server and 1
database. They plan to horizontally scale the API
tier to 10 servers next quarter. What hidden assumption
about the database might cause a problem at 10x API
scale, even though the database itself was not changed?

*Hint: Think about database connection pools. Each
server opens connections to the database. 1 server
might have 50 connections. 10 servers have 500.
What happens when the database's max_connections
setting is 200?*

**Q3 (Hands-On):** Take a simple Spring Boot REST
application that stores some state in-memory (a counter,
a list, a map). Run it twice on different ports locally.
Send requests alternating between the two ports.
Observe that the state is split between the two instances.
Now refactor it to use Redis for shared state. Run both
instances again, alternate requests, and verify the
state is consistent across both.

*Hint: This exercise makes the statelessness requirement
viscerally concrete. The split-brain behavior on the
first run is something you need to feel before you
deeply understand why stateless design is non-optional.*

---

### 🎯 Interview Deep-Dive

**Q1: Walk me through how you'd design a URL shortener
to handle 10 billion shortening operations per day.**
*Why they ask:* Tests horizontal scaling thinking at
every tier (API, cache, database).
*Strong answer includes:*
- API tier: stateless, horizontally scalable (any
  server handles any request)
- Cache tier: Redis cluster for frequent URL lookups
  (80% cache hit rate expected)
- Database tier: sharded by short code prefix or
  consistent hash of short code; read replicas for
  heavy read load
- ID generation: distributed ID generator (Snowflake
  or similar) to avoid sequential ID contention across
  database shards

**Q2: A new engineer proposes: "Let's just horizontally
scale the database the same way we horizontally scaled
the API tier." What would you tell them?**
*Why they ask:* Tests understanding of why databases
are harder to horizontally scale than stateless services.
*Strong answer includes:*
- Databases are stateful: data must be split (sharding)
  or replicated, both of which add complexity
- Sharding requires deciding how to split data (by
  user ID, by region, etc.) - wrong choice leads to
  hot shards
- Cross-shard queries become expensive or impossible
- Transactions across shards require distributed
  transaction protocols (2PC) which are slow and
  complex
- Most systems vertically scale the primary database
  and horizontally scale via read replicas long before
  sharding, because sharding is an expensive last resort

**Q3: How does horizontal scaling interact with
distributed caching?**
*Why they ask:* Tests second-order effects of horizontal
scaling decisions.
*Strong answer includes:*
- In-process cache (Caffeine/Guava): effective per-server,
  but 10 servers have 10 independent caches, potentially
  holding stale data if one is updated. Cache invalidation
  becomes a broadcast problem.
- Distributed cache (Redis): single shared cache, all
  servers read the same data. Correct, but adds network
  RTT to every cache read.
- The right choice depends on read-to-write ratio and
  tolerable staleness: mostly-read data with acceptable
  staleness → per-server cache; requires strict
  consistency → distributed cache.
