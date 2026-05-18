---
id: SYD-008
title: Load Balancing
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-007
used_by: SYD-009, SYD-010, SYD-011, SYD-012, SYD-013
related: SYD-007, SYD-009, SYD-010, SYD-011, SYD-012, SYD-013, SYD-019
tags:
  - architecture
  - networking
  - performance
  - distributed-systems
  - infrastructure
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/syd/load-balancing/
---

⚡ TL;DR - A load balancer distributes incoming requests
across a pool of backend servers, enabling horizontal
scaling, eliminating the server-tier SPOF, and providing
health-based routing to keep traffic away from failing
nodes.

| #008 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Horizontal Scaling | |
| **Used by:** | Round Robin, Least Connections, Consistent Hashing, Sticky Sessions, Session Affinity | |
| **Related:** | Horizontal Scaling, Round Robin, Least Connections, Consistent Hashing, Sticky Sessions, Redundancy and Failover | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You horizontally scale to 5 API servers. Clients need
to know which server to contact. You put all 5 IPs
in DNS. Client-side "load balancing" via DNS round-robin.
Problems: DNS TTL means clients cache the old IP for
minutes after a server fails. Some clients always hit
Server A, others always hit Server B - no rebalancing.
If Server C runs out of memory and gets slow, clients
keep hitting it anyway. No way to do zero-downtime
deploys (you can't safely remove a server from DNS
mid-traffic). The "horizontal scaling" is effectively
broken.

**THE BREAKING POINT:**
Without a dedicated load balancer, horizontal scaling
provides no real benefit: no health routing, no
graceful server removal, no dynamic traffic adjustment.
You have multiple servers but they function as poorly-
coordinated independent servers, not as a unified
high-capacity pool.

**THE INVENTION MOMENT:**
The first load balancers were hardware appliances
(Cisco LocalDirector in 1994, F5 BIG-IP in 1997).
They were dedicated network devices positioned in
front of server pools. As software-defined networking
evolved, software load balancers (HAProxy 2001, nginx
1.0 in 2004) replaced dedicated hardware. Cloud load
balancers (AWS ELB, 2009) made load balancing a
managed service requiring no infrastructure management.

**EVOLUTION:**
Layer 4 (TCP) load balancers → Layer 7 (HTTP) load
balancers → Application load balancers with content-
based routing → Service mesh sidecar proxies (Envoy,
Istio) that implement load balancing as an embedded
per-service component. Each generation added
intelligence: from "distribute packets" to "route
based on URL path and health signals."

---

### 📘 Textbook Definition

A load balancer is a networking component (hardware or
software) that distributes incoming network traffic
across a pool of backend servers according to a routing
algorithm. It operates at Layer 4 (TCP/UDP) for
connection-level balancing or Layer 7 (HTTP/HTTPS)
for request-level balancing with content awareness.
Core responsibilities: traffic distribution, health
monitoring (removing unhealthy backends from rotation),
SSL termination, connection management, and optional
request transformation. The load balancer is the entry
point for all client traffic and is itself a potential
single point of failure requiring its own HA design.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A load balancer sits in front of multiple servers and
directs each incoming request to whichever server should
handle it, based on a routing policy.

**One analogy:**
> An airport check-in counter manager who watches how
> long each agent's queue is and directs each arriving
> passenger to the shortest queue. If an agent is sick
> and goes home, the manager stops directing passengers
> to that desk. When a new agent opens a desk, the
> manager starts sending passengers there immediately.

**One insight:**
The load balancer does not just distribute load - it
is the component that enables everything else about
horizontal scaling to work correctly: zero-downtime
deploys, health-based routing, autoscaling. Without
a load balancer, horizontal scaling is little more
than having multiple servers that clients accidentally
hit at random.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. All client traffic enters through the load balancer.
   Clients know only the load balancer's address, not
   individual server addresses.
2. The load balancer continuously monitors backend
   health and only routes to healthy backends.
3. The load balancer is itself a potential SPOF and
   requires its own redundancy (active-passive pair
   or active-active with anycast).
4. The algorithm used to distribute requests determines
   which server gets each request - different algorithms
   optimize for different goals.

**LAYER 4 vs LAYER 7:**
- **L4 (TCP):** Routes based on IP address and TCP port.
  Cannot inspect request content. Very fast (no HTTP
  parsing). Used for non-HTTP protocols or when
  maximum performance is required.
- **L7 (HTTP):** Routes based on HTTP headers, URL path,
  cookies, query parameters. Can do content-based routing:
  "/api/v2/*" → new servers, "/api/v1/*" → old servers.
  Can terminate SSL. Can modify headers. More CPU
  overhead than L4.

**THE TRADE-OFFS:**

**Gain:** Single entry point that enables health routing,
zero-downtime deploys, autoscaling integration, SSL
termination, connection pooling.

**Cost:** Additional network hop (~0.5ms in same DC);
load balancer itself can become a bottleneck at extreme
request rates; operational complexity of configuring
and monitoring the load balancer itself.

---

### 🧪 Thought Experiment

**SCENARIO: Rolling deployment with and without a load balancer**

**Without a load balancer:**
To deploy v2 of your application to 5 servers without
downtime, you must update DNS A-records and hope clients
pick up the change quickly. Some clients will still
have old DNS cached. Some clients will hit v1 servers,
some v2. Mixed versions in production with no way to
control the split.

**With a load balancer:**
1. Remove Server A from the load balancer pool (LB stops
   sending new requests to Server A; in-flight requests
   complete)
2. Deploy v2 to Server A
3. Health check passes for Server A with v2
4. Add Server A back to pool
5. Repeat for Servers B, C, D, E

Result: Zero client-visible downtime. At any moment,
requests go only to fully-healthy servers running
a known version. The version split is perfectly
controlled.

**THE INSIGHT:**
The load balancer is not just a performance component -
it is the operational control plane for the server pool.
The ability to drain, replace, and add servers without
interrupting clients is what makes horizontal scaling
operationally tractable.

---

### 🧠 Mental Model / Analogy

> A load balancer is like a smart traffic cop at an
> intersection who knows which lanes are congested,
> which are blocked, and which have just opened.
> The cop (LB) directs each car (request) to the
> best available lane (server) at that moment.
> Without the traffic cop, cars would just pile
> into the first lane they see.

**Load balancing algorithm analogies:**
- Round Robin → taking turns: Car 1 → Lane A,
  Car 2 → Lane B, Car 3 → Lane C, repeat.
- Least Connections → shortest queue: cop looks
  at all lanes and sends next car to emptiest lane.
- IP Hash → preferred lane by driver's home zip code:
  cars from zip code 90210 always use Lane B (sticky).
- Random → random: cop throws a dart and picks a lane.

**Where this analogy breaks down:**
Unlike a traffic cop, the load balancer health-checks
backends proactively (not reactively). It knows a server
is degraded before clients notice, and stops routing
to it before clients get errors.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A "traffic director" that sits in front of multiple
servers and decides which server should handle each
request. It keeps all servers busy and avoids sending
requests to broken servers.

**Level 2 - How to use it (junior developer):**
In AWS, create an Application Load Balancer (ALB),
register your EC2 instances as targets, and configure
a health check (HTTP GET /health → 200 OK). The ALB
automatically routes traffic to healthy instances
and stops routing to instances that fail health checks.

**Level 3 - How it works (mid-level engineer):**
The load balancer maintains a connection pool to each
backend. For each incoming request, it selects a
backend according to the algorithm (round-robin, least
connections, etc.), forwards the request, and relays
the response. Health checks run in parallel on a
configurable interval. When a backend fails N consecutive
health checks, it is removed from the routing pool.

**Level 4 - Why it was designed this way (senior/staff):**
The load balancer must balance three competing concerns:
(1) fairness - distribute load evenly; (2) locality
- sometimes you want the same client to hit the same
backend (sticky sessions); (3) health - never route
to an unhealthy backend. These three goals conflict:
round-robin is fair but ignores server capacity
differences; least-connections routes to the lowest-
load server but ignores latency variance; consistent
hashing ensures locality but can create hot spots.
Real production load balancers let you tune these
trade-offs through algorithm selection and configuration.

**Level 5 - Mastery (distinguished engineer):**
The load balancer is one of the most latency-sensitive
components in the critical path of every request.
The "thundering herd" and "connection storm" patterns
can cause load balancers to amplify failures: a brief
backend slowdown causes connection queue buildup,
which causes load balancer memory exhaustion, which
cascades to all backends being marked unhealthy.
Circuit breaking at the load balancer level (cutting
off requests to a backend that is responding slowly,
not just one that is completely down) is the key
defense. This is why service meshes (Envoy, Linkerd)
with outlier detection are replacing traditional load
balancers for microservice architectures.

---

### ⚙️ How It Works (Mechanism)

**Architecture overview:**

```
┌──────────────────────────────────────────────────┐
│ LOAD BALANCER ARCHITECTURE                       │
│                                                  │
│  Clients                                         │
│    │                                             │
│    ▼                                             │
│  [VIP / DNS]  → single IP seen by clients        │
│    │                                             │
│    ▼                                             │
│  [Load Balancer] ← health checks all backends   │
│    │                                             │
│    ├─→ [Backend A: HEALTHY] ──→ response         │
│    ├─→ [Backend B: HEALTHY] ──→ response         │
│    ├─→ [Backend C: DEGRADED - removed from pool] │
│    └─→ [Backend D: HEALTHY] ──→ response         │
│                                                  │
│  Backends connect to:                            │
│    [Shared DB]                                   │
│    [Redis Cache]                                 │
└──────────────────────────────────────────────────┘
```

**Health check lifecycle:**

```
┌──────────────────────────────────────────────────┐
│ HEALTH CHECK STATE MACHINE                       │
│                                                  │
│  [HEALTHY]                                       │
│     │ health check fails N times                 │
│     ▼                                            │
│  [UNHEALTHY] ← removed from LB pool             │
│     │ health check passes M times                │
│     ▼                                            │
│  [HEALTHY] ← added back to LB pool              │
│                                                  │
│ AWS ALB defaults: N=2 fails, M=2 passes          │
│ Interval: 30s, Timeout: 5s                       │
│ Max time to remove bad server: 35s               │
└──────────────────────────────────────────────────┘
```

**Load balancing algorithms (comparative):**

```
Arrival: Request R1 R2 R3 R4 R5 R6

Round-Robin:
  A: R1, R4    B: R2, R5    C: R3, R6
  Simple. Even distribution. Ignores server load.

Least-Connections:
  A: R1(1 conn)  → R4 goes where connections lowest
  B: R2(1 conn)  → at R4: A=1, B=1, C=0 → C gets R4
  C: R3(1 conn)
  Tracks real load. Better for long-lived connections.

IP-Hash:
  hash(client_ip) % N = server index
  Same client always hits same server.
  Useful for session stickiness. Bad if one IP is busy.

Weighted Round-Robin:
  A: weight=3  B: weight=2  C: weight=1
  A: R1,R2,R3  B: R4,R5    C: R6 (per 6 requests)
  Handles servers of different capacity.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL REQUEST FLOW (L7 ALB):**
```
[Client sends HTTPS request]
  → [DNS resolves to LB Virtual IP]
  → [LB terminates TLS] (SSL offload)
  → [LB inspects HTTP headers/path]
  → [LB applies routing rule]
     (e.g., /api/* → target group A)
  → [LB selects backend via algorithm]
     (round-robin: next in rotation)
  → [LB forwards request to Backend A]
  → [Backend A processes, returns response]
  → [LB relays response to client]
Total added latency: ~0.5ms (same datacenter)
```

**BACKEND FAILURE DETECTION:**
```
[Backend B health check fails]
  → [Wait for N consecutive failures] (typically 2-3)
  → [LB marks Backend B UNHEALTHY]
  → [LB stops routing new requests to Backend B]
  → [In-flight requests to Backend B complete or timeout]
  → [Auto-scaling: new instance launched to replace B]
  → [New instance passes health check]
  → [LB adds new instance to rotation]
```

**SCALE AT DIFFERENT SIZES:**
- 10 backends: single load balancer is fine
- 100 backends: consider load balancer connection limits
  (AWS ALB handles 100,000+ req/s, no concern here)
- 10,000 backends: load balancer itself may need to
  be horizontally scaled or use anycast routing

---

### 💻 Code Example

**Example 1 - nginx: Basic load balancer config**
```nginx
# BAD: No health checks, no keepalive, no algorithm choice
upstream backend {
    server 10.0.1.1;
    server 10.0.1.2;
    server 10.0.1.3;
}

# GOOD: Health checks, keepalive, and explicit algorithm
upstream backend {
    least_conn;  # distribute to least-busy server
    server 10.0.1.1 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.1.2 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.1.3 weight=1 max_fails=3 fail_timeout=30s;
    keepalive 32;  # 32 idle connections to each backend
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
        proxy_next_upstream error timeout
                            http_502 http_503 http_504;
    }
}
```

**Example 2 - AWS ALB: Register targets and health check**
```bash
# Create target group with health check
aws elbv2 create-target-group \
  --name my-app-tg \
  --protocol HTTP \
  --port 8080 \
  --vpc-id vpc-12345678 \
  --health-check-path /health \
  --health-check-interval-seconds 10 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --health-check-timeout-seconds 5

# Register instances
aws elbv2 register-targets \
  --target-group-arn arn:aws:... \
  --targets Id=i-1234567890abcdef0 \
            Id=i-abcdef1234567890 \
            Id=i-0987654321abcdef

# Graceful deregister before deploy (drain connections)
aws elbv2 deregister-targets \
  --target-group-arn arn:aws:... \
  --targets Id=i-1234567890abcdef0
# Then wait for draining (deregistration delay: 30s)
sleep 35
# Now safe to deploy to this instance
```

**Example 3 - Spring Boot: Rolling deploy via LB drain**
```bash
# GOOD: Shell script for zero-downtime rolling deploy
# Assumes AWS ALB + auto-scaling group
INSTANCES=$(aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names my-app-asg \
  --query 'AutoScalingGroups[0].Instances[*].InstanceId' \
  --output text)

for INSTANCE_ID in $INSTANCES; do
  echo "Deploying to $INSTANCE_ID..."

  # 1. Detach from LB (graceful drain)
  aws autoscaling detach-load-balancer-target-groups \
    --auto-scaling-group-name my-app-asg \
    --target-group-arns arn:aws:...
  sleep 35  # wait for deregistration delay

  # 2. Deploy new artifact via SSM or SSH
  aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["cd /app && ./deploy.sh"]'

  # 3. Wait for health check to pass
  aws elb wait target-in-service \
    --load-balancer-name my-alb ...

  # 4. Re-attach to LB
  aws autoscaling attach-load-balancer-target-groups \
    --auto-scaling-group-name my-app-asg \
    --target-group-arns arn:aws:...

  echo "Done with $INSTANCE_ID"
done
```

---

### ⚖️ Comparison Table

| Type | Layer | Content-Aware | SSL Termination | Overhead | Use Case |
|---|---|---|---|---|---|
| L4 (TCP) | Transport | No | No | Minimal | Non-HTTP, max perf |
| L7 (HTTP) | Application | Yes | Yes | Low | Web APIs, microservices |
| DNS-based | None | No | No | None (client-side) | Geographic routing |
| Service Mesh | Application | Yes | mTLS | Medium | Microservice-to-microservice |

**Which to use:**
- HTTP APIs → AWS ALB / nginx / HAProxy (L7)
- Non-HTTP services → AWS NLB / HAProxy (L4)
- Microservices internal traffic → Envoy sidecar
  (service mesh); adds circuit breaking + retries
- Multi-region traffic → Route 53 latency-based
  routing + regional ALBs

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Load balancer eliminates all SPOFs | The load balancer itself is a SPOF. Production deployments use active-passive or active-active LB pairs with a virtual IP (VIP) that floats between them. |
| Health check passing = server is healthy | Health checks test a specific endpoint (/health). A server can pass the health check while being severely degraded for specific request types (e.g., database query deadlock). Deep health checks that probe actual functionality are more reliable. |
| Load balancing is only about distributing load | It also enables zero-downtime deploys, auto-healing (replace failed instances), SSL offload, connection pooling, request logging, and traffic shaping. The "balancing" is often the least important function. |
| More backends always = better | Adding backends does not help if the bottleneck is the shared database, Redis, or network. Profile the actual bottleneck before adding servers. |

---

### 🚨 Failure Modes & Diagnosis

**Connection Draining Failure During Deploy**

**Symptom:**
During a rolling deploy, some users receive HTTP 502
errors for ~5 seconds when each server is being
replaced. Support receives complaints about brief
errors during business hours.

**Root Cause:**
Instances are being removed from the load balancer
pool and immediately restarted, without waiting for
the deregistration delay to complete. In-flight
requests are killed mid-processing.

**Diagnostic:**
```bash
# Check if deregistration delay is configured
aws elbv2 describe-target-group-attributes \
  --target-group-arn arn:aws:... \
  --query 'Attributes[?Key==`deregistration_delay.timeout_seconds`]'
# Should be 30-60 seconds

# Check ALB access logs for 502s during deploys
# Correlate timestamps with deploy timeline
aws s3 cp s3://my-alb-logs/AWSLogs/.../access.log.gz .
gunzip access.log.gz
grep ' 502 ' access.log | tail -100
```

**Fix:**
Add a pre-stop hook in Kubernetes or a deregistration
wait in your deploy script:
```yaml
# Kubernetes: graceful shutdown with pre-stop hook
lifecycle:
  preStop:
    exec:
      command: ["/bin/sleep", "10"]
terminationGracePeriodSeconds: 30
```

**Prevention:**
Configure deregistration delay ≥ your application's
longest request timeout. Verify the deploy script
waits for this delay before killing the process.

---

**Load Balancer as Bottleneck Under Spike Traffic**

**Symptom:**
During a marketing campaign, traffic spikes 50x.
Backend servers are healthy and underutilized at 20%
CPU, but response times degrade to 10+ seconds.
Load balancer CPU is at 95%.

**Root Cause:**
The load balancer (a single EC2-based nginx instance)
cannot forward packets at 50x traffic. Backend servers
are fine, but the load balancer is the bottleneck.

**Diagnostic:**
```bash
# Check load balancer instance CPU
top -b -n 1 | grep nginx
# If near 100%: load balancer is the bottleneck

# Check active connections (nginx)
nginx -s status  # or
curl localhost/nginx_status
# Active connections: should be < 50k for most hardware
```

**Fix:**
For AWS: switch from self-managed nginx to AWS ALB
(autoscales automatically). For self-managed: use
anycast VIP with multiple LB nodes behind it,
or use DNS-based GSLB.

**Prevention:**
Never put a self-managed single-instance load balancer
on the critical path of production traffic without
its own HA design.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Horizontal Scaling` - load balancing is the required
  companion to horizontal scaling; without it, horizontal
  scaling does not function correctly

**Builds On This (learn these next):**
- `Round Robin` - the simplest LB algorithm; start here
- `Least Connections` - the most common production
  algorithm for variable-cost requests
- `Consistent Hashing` - the algorithm for distributing
  cache or shard-aware requests
- `Sticky Sessions` - how to handle sessions when
  the application has unavoidable server-local state

**Alternatives / Comparisons:**
- `DNS Load Balancing` - client-side, no health routing,
  simpler but much less capable
- `Service Mesh` - load balancing as a distributed
  sidecar; adds circuit breaking and observability

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Routes incoming requests across a pool   │
│              │ of backends using an algorithm +         │
│              │ health state                             │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Enables horizontal scaling to work:      │
│ SOLVES       │ distributes load, removes unhealthy      │
│              │ backends, enables zero-downtime deploys  │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ LB is not just for load distribution -   │
│              │ health routing and draining are equally  │
│              │ critical for production reliability      │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Any horizontally scaled service with 2+  │
│              │ backend instances                        │
├──────────────┼──────────────────────────────────────────┤
│ AVOID        │ Never skip HA for the LB itself;         │
│              │ never deploy without deregistration delay│
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Using DNS round-robin as a load balancer │
│              │ (no health checking, stale cache, no     │
│              │ draining)                                │
├──────────────┼──────────────────────────────────────────┤
│ ALGORITHMS   │ Round Robin: simple, even, stateless     │
│              │ Least Connections: best for variable cost│
│              │ IP Hash: client affinity (sticky)        │
│              │ Weighted: handles unequal capacity       │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Without a load balancer, horizontal     │
│              │  scaling is just having multiple servers │
│              │  that clients hit by accident."          │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Round Robin → Least Connections →        │
│              │ Consistent Hashing → Sticky Sessions     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Health routing is the most important function - the
   load balancer continuously checks backend health and
   removes failing servers from rotation automatically.
2. The LB itself is a SPOF - every production deployment
   needs a redundant load balancer pair.
3. Connection draining is required for zero-downtime
   deploys - always wait for deregistration delay before
   stopping a server.

**Interview one-liner:**
"A load balancer sits in front of backend servers and
routes each request to a server according to an algorithm
(round-robin, least connections, etc.) while continuously
health-checking backends and removing unhealthy ones
from rotation. It enables horizontal scaling, zero-
downtime deploys, and auto-healing. The LB is itself
a potential SPOF and requires its own HA design."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every component that sits in the critical path of
all requests must be designed for its own high
availability. A load balancer that is itself a SPOF
is worse than no load balancer - it gives the false
impression of resilience while adding a new failure
point. Apply this principle everywhere: "we added X
to improve Y, but X itself can now fail and take
down Y worse than before."

**Where else this pattern appears:**
- **DNS servers** - the naming system is itself
  horizontally scaled (multiple authoritative servers
  plus anycast for root servers) to avoid a global DNS
  SPOF.
- **Message queue brokers** - Kafka brokers are load-
  balanced at the partition level; each partition has
  a leader (the "load balancer" equivalent) that all
  producers/consumers connect to.
- **Database connection pooling** - PgBouncer is a
  load balancer for database connections: it sits in
  front of PostgreSQL and distributes connections,
  enabling more application connections than the DB
  can natively handle.
- **Kubernetes Service** - a Service is a virtual IP
  (VIP) that load balances across healthy pod instances
  using kube-proxy rules in iptables/ipvs.

**Industry applications:**
- **AWS ALB** - serves billions of requests per day
  across millions of customer applications. Auto-scales
  its own capacity to handle traffic spikes. Provides
  routing rules, SSL offload, WAF integration, and
  access logging as managed features.
- **Cloudflare** - distributes 50+ million HTTP
  requests/second using anycast routing: all 300+
  datacenters share the same IP addresses, and BGP
  routing directs each client to the nearest datacenter.
  This is global-scale load balancing at the network
  layer.

---

### 💡 The Surprising Truth

Netflix's "Chaos Monkey" was initially built to
specifically target load balancers. When Netflix
moved to AWS in 2008, their engineers discovered that
their AWS load balancers (before the current generation
of ALBs) were single points of failure. Chaos Monkey
would randomly terminate load balancer instances in
production. The engineering team had to make the LB
layer resilient to survive Chaos Monkey testing. This
forced the habit of designing every component - even
infrastructure components - for failure. The lesson
Chaos Monkey teaches is that assuming infrastructure
reliability without testing it is an illusion. Load
balancers fail. The only question is whether you
designed for that case before it happened.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Describe why a load balancer is required
   for horizontal scaling to work correctly, going
   beyond "it distributes load" to explain health
   routing and deploy draining.
2. [DESIGN] Given an API service scaling from 1 to
   10 servers, describe the complete load balancer
   setup: algorithm choice, health check config,
   deregistration delay, and LB HA.
3. [DEBUG] Given 502 errors during a rolling deploy,
   trace the failure to missing deregistration delay
   and describe the fix.
4. [DECIDE] Given two workloads - (a) short API calls
   ~5ms each, (b) file upload requests up to 30s each -
   explain which load balancing algorithm is appropriate
   for each and why.
5. [OPERATE] Describe how to safely drain a server
   from a load balancer pool before a deploy without
   any client-visible errors.

---

### 🧠 Think About This Before We Continue

**Q1.** Your load balancer health check hits /health
and gets 200 OK from all 5 backend servers. But users
are still experiencing errors on 20% of requests.
All errors are database connection timeouts. The
health check passes, but the service is clearly
degraded. What design change to the health check
would catch this problem?

*Hint: The health check should verify actual
functionality - including database connectivity -
not just that the process is running and listening.*

**Q2.** You have 3 backend servers. Server A handles
short requests averaging 10ms. Server B and C handle
similar load. You configure round-robin load balancing.
After a few hours, you notice Server A has 5x as many
active connections as B and C despite similar request
rates. Why, and what algorithm would fix this?

*Hint: Round-robin distributes requests evenly,
but if some requests are slow (long-running jobs,
file uploads), the server handling them accumulates
more active connections. Think about which algorithm
looks at the connection count directly.*

**Q3 (Hands-On):** Set up nginx locally as a load
balancer in front of two instances of a simple HTTP
server (can be two Python http.server instances on
different ports). Configure round-robin. Send 20
requests and observe distribution. Then stop one
backend and observe nginx's behavior (does it retry?
does it fail fast?). Configure health checks. Now
stopping one backend should result in all traffic
going to the remaining server within seconds.

*Hint: nginx upstream fail_timeout and max_fails
control health detection. With active health checks
(nginx Plus or custom), detection is faster than with
passive detection (based on response errors).*

---

### 🎯 Interview Deep-Dive

**Q1: How would you design the load balancing layer
for a system handling 1 million requests per second?**
*Why they ask:* Tests understanding of load balancer
scalability limits.
*Strong answer includes:*
- A single load balancer at this scale is itself a
  bottleneck; must horizontally scale the LB tier
- Use anycast routing (all LB nodes share the same
  IP; BGP routes each packet to the nearest/cheapest
  node) for active-active, not just active-passive
- AWS ALB can handle this natively (auto-scales);
  for self-managed, use L4 ECMP (equal-cost multi-path)
  routing at the network switch level before L7 LBs
- Track and optimize connection setup time: at 1M
  RPS, even a 1ms overhead per request is 1,000
  CPU-seconds/second wasted just on connection setup

**Q2: What is the difference between an Application
Load Balancer (L7) and a Network Load Balancer (L4)?
When would you choose each?**
*Why they ask:* Tests practical knowledge of
infrastructure options.
*Strong answer includes:*
- L4 (NLB): routes on IP/port, ultra-low latency
  (<1ms), preserves source IP, handles TCP/UDP
  (not just HTTP), no HTTP inspection. Use for:
  non-HTTP protocols, gaming, IoT, strict latency
  requirements, preserving client IP for compliance.
- L7 (ALB): routes on HTTP content (path, headers,
  host), terminates SSL, can add/modify headers,
  content-based routing, supports gRPC, WebSockets.
  Use for: HTTP/HTTPS APIs, content-based routing,
  SSL offload, WAF integration. 95% of web services.

**Q3: A backend server is responding to health checks
with 200 OK but its p99 latency is 5x normal. Your
load balancer has no circuit breaking. Describe what
happens to the system and how you would prevent it.**
*Why they ask:* Tests depth of understanding of
load balancer failure modes and advanced features.
*Strong answer includes:*
- Without circuit breaking: LB continues to route
  to the slow server. Its connection queue grows.
  Other requests waiting in the LB queue for that
  server also slow down. The slow server becomes
  a "gravitational well" that degrades overall p99.
- Prevention option 1: Least-connections algorithm
  naturally sends fewer requests to the slow server
  (its connection count is high). Not perfect but
  better than round-robin.
- Prevention option 2: Outlier detection (Envoy,
  Istio): if server response time is 2x the average,
  eject it from the pool temporarily even if health
  check passes.
- Prevention option 3: Timeout + retry at the LB:
  if backend does not respond within X ms, time out
  and retry on a different backend.
