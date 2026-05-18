---
id: SYD-003
title: Availability
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: SYD-002
used_by: SYD-015, SYD-019, SYD-020, SYD-021, SYD-022
related: SYD-002, SYD-004, SYD-015, SYD-019
tags:
  - reliability
  - foundational
  - architecture
  - distributed
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 3
permalink: /technical-mastery/syd/availability/
---

⚡ TL;DR - Availability is the percentage of time a system
is operational and reachable, and it is achieved by
eliminating single points of failure through replication.

| #003 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Non-Functional Requirements | |
| **Used by:** | SLA / SLO / SLI, Redundancy and Failover, Active-Active, Active-Passive, Disaster Recovery | |
| **Related:** | Non-Functional Requirements, Single Point of Failure, SLA / SLO / SLI, Redundancy and Failover | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a bank that runs its core transaction system on
a single server. On a Tuesday afternoon, a power supply
unit in that server fails. The entire bank is offline.
ATMs stop working. Point-of-sale terminals decline cards.
Wire transfers queue and miss same-day processing windows.
Customers cannot access their accounts. The bank loses
millions of dollars per hour and faces regulatory scrutiny.
One hardware component - costing $150 - brought down a
system serving millions of people.

**THE BREAKING POINT:**
Any system running on a single component inherits that
component's failure probability. Modern servers have
Mean Time Between Failures (MTBF) measured in years -
but with enough servers, one fails every week. Without
a strategy for surviving component failures, the system's
availability is bounded by the least reliable component.

**THE INVENTION MOMENT:**
This is exactly why availability is a first-class design
concern. High availability (HA) means designing systems
so that individual component failures do not cause
system-wide outages.

**EVOLUTION:**
Early systems achieved availability through better hardware
(redundant power supplies, RAID storage). As internet
scale arrived in the 2000s, hardware reliability was
outpaced by the sheer number of components that could
fail. Google's Borg (2003) and Amazon's Dynamo (2007)
pioneered software-level availability: designing systems
to assume hardware fails constantly and routing around it
automatically. The "nines" vocabulary (99.9%, 99.99%)
became industry standard in SLA negotiation by 2010.

---

### 📘 Textbook Definition

Availability is the proportion of time a system is in a
functional, operational state, expressed as a percentage
over a measurement window. It is calculated as:

  Availability = Uptime / (Uptime + Downtime)

For a system with components in series (each must work
for the system to work), availability is the product of
individual availabilities. For a system with components
in parallel (any one can work), availability is
1 - (product of individual unavailabilities). High
availability is achieved by eliminating single points
of failure through redundancy, automated failover, and
health-check-based traffic routing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The percentage of time your system is usable - achieved
by having backups ready when primary components fail.

**One analogy:**
> The redundant power supply in a data center server.
> When one PSU fails, the second takes over without
> interruption. Users never notice. Availability is
> the practice of building that "second PSU" into
> every critical component of a distributed system.

**One insight:**
Availability is not about preventing failures - hardware
fails, networks partition, software has bugs. Availability
is about surviving failures without user-visible impact.
The question is not "will this fail?" but "when this
fails, what happens to users?"

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every component has a non-zero failure probability.
   A system is only as available as its failure handling
   allows, not as available as its hardware promises.
2. Components in series reduce availability (each is
   a potential point of failure). Components in parallel
   increase availability (redundancy).
3. Availability of 100% is theoretically impossible for
   distributed systems because network partitions are
   an inescapable physical reality (CAP theorem).

**DERIVED DESIGN:**
Given that failures are certain, a high-availability
system must:
- Remove every single point of failure (SPOF)
- Detect failures automatically (health checks)
- Route traffic away from failed components automatically
  (load balancer, DNS failover)
- Recover failed components without manual intervention
  (auto-scaling, self-healing)

**THE TRADE-OFFS:**

**Gain:** User-visible uptime, reduced incident frequency,
business continuity during component failures.

**Cost:** More hardware (redundant components), operational
complexity (failover testing), potential consistency
cost (two replicas may have different state).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Detecting that a component has failed and
routing around it requires real-time health information
that takes measurable time to propagate - there will
always be a brief window during failover when some
requests fail.

**Accidental:** Many systems have avoidable SPOFs -
a single load balancer, a single DNS server, a single
database primary with no replica. These are design
oversights, not physics constraints.

---

### 🧪 Thought Experiment

**SETUP:**
A web application has one server, one database, and one
load balancer. Each has 99.9% monthly availability.

**WHAT HAPPENS WITHOUT HIGH AVAILABILITY DESIGN:**
Three components in series:
Availability = 0.999 × 0.999 × 0.999 = 99.7%
That is 21.9 hours of downtime per year. In a single
month, one component will fail and take the whole system
down for roughly 43 minutes.

**WHAT HAPPENS WITH HA DESIGN:**
Two servers behind a load balancer, each 99.9% available:
Server pair availability = 1 - (0.001 × 0.001) = 99.9999%
Database with synchronous replica: 99.9999%
Load balancers in active-active pair: 99.9999%
Combined: 99.9997% ≈ 15 minutes downtime per year.

**THE INSIGHT:**
Redundancy at each layer multiplies availability. The
math is simple but the design implication is profound:
a 3-component system can move from 99.7% to 99.9997%
availability purely through architectural choices,
without better hardware.

---

### 🧠 Mental Model / Analogy

> Availability is like electrical grid resilience.
> A single power line from the plant to your house means
> one tree fall takes out your power. A grid with multiple
> routing paths means the power company can route around
> the downed line and you never lose electricity. High
> availability is building a grid, not a single line.

- "Power plant" → primary data source (database, API)
- "Routing paths" → replicas, load balancers, failover
- "Circuit breaker" → automated failover mechanism
- "Power restored" → component recovery and re-join
- "Downed line" → failed server, network partition
- "Blackout area" → users affected during failover window

**Where this analogy breaks down:**
Electrical grids route power without data consistency
concerns. Distributed systems must ensure that replicas
serving traffic have consistent data - otherwise routing
around a failure can serve stale or incorrect data.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Availability means the system is working when users need
it. 99.9% means it is down for less than 9 hours per year.
Achieving it means having backups that automatically take
over when something breaks.

**Level 2 - How to use it (junior developer):**
To increase availability: add redundant instances of
every critical component, use a load balancer to
distribute traffic, and configure health checks so failed
instances are removed from the rotation automatically.
Avoid single servers, single databases, and any component
without a standby.

**Level 3 - How it works (mid-level engineer):**
High availability is achieved through: (1) redundancy -
multiple copies of each component; (2) health monitoring -
continuous health checks on each component; (3) automated
failover - traffic redirected from failed to healthy
components within a defined time window; (4) data
replication - state synchronized across redundant
components so failover does not lose committed writes.

**Level 4 - Why it was designed this way (senior/staff):**
The design of HA systems is dominated by the failure
detection and failover latency. A health check interval
of 10 seconds means a failed component serves errors
for up to 10 seconds before traffic is rerouted. This
creates a trade-off: frequent health checks reduce
detection latency but increase load on healthy components.
False positive detection (flagging a slow but not failed
component) causes unnecessary failovers. Most HA systems
use a combination: shallow health checks at high
frequency for fast detection, deep health checks at low
frequency for validation.

**Level 5 - Mastery (distinguished engineer):**
True availability engineering means understanding the
difference between infrastructure-level availability
(is the server responding to pings?) and application-
level availability (are users successfully completing
their intended actions?). A server that responds to
health checks but serves corrupt data is 100% available
by infrastructure metrics and 0% available by user
experience metrics. Elite HA systems define availability
in terms of successful user operations, not just server
uptime, and use synthetic monitoring (canary requests)
to continuously validate the full user journey.

---

### ⚙️ How It Works (Mechanism)

**The "nines" vocabulary and their real meaning:**

```
┌────────────────────────────────────────────────────┐
│ AVAILABILITY TARGETS - REAL DOWNTIME IMPACT        │
├──────────────┬────────────┬──────────┬─────────────┤
│ Availability │ Downtime/yr│ Downtime │ Required    │
│              │            │ /month   │ Strategy    │
├──────────────┼────────────┼──────────┼─────────────┤
│ 99%          │ 87.6 hours │ 7.3 h    │ Basic HA    │
│ 99.9%        │ 8.7 hours  │ 43.8 min │ Redundancy  │
│ 99.99%       │ 52 minutes │ 4.4 min  │ Auto-failovr│
│ 99.999%      │ 5.3 minutes│ 26 sec   │ Active-activ│
│ 99.9999%     │ 32 seconds │ 2.6 sec  │ Multi-region│
└──────────────┴────────────┴──────────┴─────────────┘
```

**Component availability math:**

Series components (all must work):
```
  A_system = A1 × A2 × A3
  Example: 0.999 × 0.999 × 0.999 = 0.997 (99.7%)
```

Parallel components (any one can work):
```
  A_system = 1 - ((1-A1) × (1-A2))
  Example: 1 - (0.001 × 0.001) = 0.999999 (99.9999%)
```

**The failover sequence:**

```
┌──────────────────────────────────────────────┐
│ HIGH AVAILABILITY FAILOVER SEQUENCE          │
├──────────────────────────────────────────────┤
│ 1. HEALTH CHECK FAILS                        │
│    Load balancer polls /health endpoint      │
│    Primary returns 5xx or times out          │
├──────────────────────────────────────────────┤
│ 2. FAILURE CONFIRMED                         │
│    N consecutive failures confirm failure    │
│    (avoids false positive on transient error)│
├──────────────────────────────────────────────┤
│ 3. TRAFFIC REROUTED                          │
│    Load balancer removes failed instance     │
│    Remaining instances absorb the traffic    │
│    Brief latency spike during transition     │
├──────────────────────────────────────────────┤
│ 4. ALERT TRIGGERED                           │
│    On-call notified of instance loss         │
│    Capacity is now reduced - urgent fix      │
├──────────────────────────────────────────────┤
│ 5. RECOVERY                                  │
│    New instance launched (auto-scaling)      │
│    Health check passes                       │
│    Re-added to load balancer rotation        │
└──────────────────────────────────────────────┘
```

**Database availability (the hard part):**
Application tier availability is straightforward:
add more stateless servers. Database availability is
harder because state must be consistent across replicas.
The two primary strategies are:
- **Active-Passive:** One primary handles writes;
  replica is synchronized. Failover promotes replica
  to primary. Risk: replication lag means some writes
  may be lost during failover.
- **Active-Active:** Multiple primaries accept writes
  with conflict resolution. No failover needed, but
  conflict resolution complexity is high.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[User Request]
    → [DNS / Global LB]
    → [Regional LB ← YOU ARE HERE (routes around failures)]
    → [App Instance Pool (N instances)]
    → [Cache Layer]
    → [Database Primary]
         ↓ (async/sync replication)
    → [Database Replica(s)]
    → [Response]
```

**FAILURE PATH:**
```
App Instance fails
    → LB health check detects (within check_interval)
    → Instance removed from rotation
    → Remaining instances serve traffic
    → Auto-scaling launches replacement
    → New instance passes health check
    → Re-added to rotation
(User impact: some requests 503 during detection window)
```

**WHAT CHANGES AT SCALE:**
At 10x scale, health check storms (all instances polling
DNS or config service simultaneously) can overload
the checked service. At 100x, multi-region deployment
is required, adding DNS failover latency. At 1000x,
global load balancing with anycast routing is needed.

---

### 💻 Code Example

**Example 1 - BAD: Single point of failure in config**
```yaml
# BAD: Single Redis instance - if it fails,
# the entire session store is unavailable
spring:
  redis:
    host: redis-primary.internal
    port: 6379
    # No sentinel, no cluster, no fallback
```

**Example 2 - GOOD: Redis Sentinel for HA**
```yaml
# GOOD: Redis Sentinel detects primary failure
# and promotes a replica automatically.
# Application reconnects to new primary.
spring:
  redis:
    sentinel:
      master: mymaster
      nodes:
        - sentinel1.internal:26379
        - sentinel2.internal:26379
        - sentinel3.internal:26379
    # Minimum 3 sentinels for quorum vote
    # (prevents split-brain during partition)
```

**Example 3 - Production: Health endpoint pattern**
```java
// GOOD: Health endpoint reveals component health,
// not just "is the server alive".
// Load balancer uses this to route traffic.
@RestController
public class HealthController {

    @Autowired
    private DataSource dataSource;

    @Autowired
    private RedisTemplate<?, ?> redisTemplate;

    // Shallow check: fast, low-cost, high frequency
    @GetMapping("/health/live")
    public ResponseEntity<String> liveness() {
        // Returns 200 if JVM is alive
        return ResponseEntity.ok("OK");
    }

    // Deep check: slower, validates dependencies
    @GetMapping("/health/ready")
    public ResponseEntity<Map<String, Object>>
            readiness() {
        Map<String, Object> status = new HashMap<>();
        boolean ready = true;

        // Check DB connection
        try (Connection c = dataSource.getConnection()) {
            c.createStatement().execute("SELECT 1");
            status.put("db", "UP");
        } catch (Exception e) {
            status.put("db", "DOWN: " + e.getMessage());
            ready = false;
        }

        // Check Redis connection
        try {
            redisTemplate.opsForValue().get("__health");
            status.put("redis", "UP");
        } catch (Exception e) {
            status.put("redis", "DOWN: " + e.getMessage());
            ready = false;
        }

        return ready
            ? ResponseEntity.ok(status)
            : ResponseEntity
                .status(503)
                .body(status);
    }
}
```

**Example 4 - Failure: What a split-brain looks like**
```
# Split-brain: network partition separates primary
# from replica. Both think they are the primary.
# Both accept writes. When partition heals:
# - Two divergent write histories exist
# - Conflict resolution chooses one; writes lost
# - Users see data appear and disappear

# Prevention: require majority quorum for primary
# election. With 2 nodes: 1 isolated node cannot
# achieve quorum (1 < 2/2+1=2). Primary role is
# only granted with >= 2 of 3 sentinels agreeing.
```

---

### ⚖️ Comparison Table

| Strategy | Availability | Write Latency | Complexity | Best For |
|---|---|---|---|---|
| Single instance | ~99.9% | Lowest | Lowest | Development |
| **Active-passive** | **99.99%** | **Low** | **Medium** | **Most production** |
| Active-active | 99.999% | Medium | High | Highest write SLA |
| Multi-region | 99.9999% | Medium-high | Very high | Global critical |

**How to choose:**
Active-passive covers most production needs with manageable
complexity. Active-active is needed only when the failover
window of active-passive (30-60 seconds) violates the SLA.
Multi-region is needed only when a full regional outage
must not cause downtime.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 100% availability is achievable | No distributed system can guarantee 100% availability. Even AWS aims for 99.9999% not 100%. |
| More nines are always better | 99.999% costs 10-100x more than 99.9%. Most applications don't need it and the cost is unjustifiable |
| Health check passing = system available | Health checks verify that the server is alive. They do not verify that the application logic is correct or that dependencies are reachable |
| Availability = reliability | Reliability means the system does what it is supposed to do. An available-but-buggy system is available but not reliable |
| Failover is instant | Failover takes time: health check detection (seconds), DNS propagation (seconds to minutes), replica promotion (seconds), connection draining (seconds) |

---

### 🚨 Failure Modes & Diagnosis

**Split-Brain During Failover**

**Symptom:**
Two database nodes both believe they are the primary.
Writes go to both. After partition heals, data conflicts
are detected. Some user data is rolled back silently.
Users see posts/orders/data disappear.

**Root Cause:**
The failover mechanism promoted a replica to primary
without confirming the original primary was unreachable.
Both nodes accepted writes simultaneously. No quorum
requirement was configured.

**Diagnostic Command:**
```bash
# Check if two primaries exist in Redis Sentinel
redis-cli -h sentinel1 -p 26379 \
  SENTINEL masters

# Check PostgreSQL replication state
psql -c "SELECT pg_is_in_recovery(),
  pg_postmaster_start_time(),
  inet_server_addr();"
# If two nodes both return FALSE for pg_is_in_recovery
# you have a split-brain.
```

**Fix:**
Shut down the node with fewer writes. Replay the
missing write-ahead log from the true primary. Configure
quorum-based leader election.

**Prevention:**
Require majority quorum (> N/2 nodes) for any primary
promotion. With 3 nodes, 2 must agree before promotion.

---

**Health Check False Positives**

**Symptom:**
Healthy application instances are repeatedly removed
from the load balancer rotation during traffic spikes.
User requests see elevated error rates. The instances
were not actually failing - they were slow due to load.

**Root Cause:**
The health check timeout was shorter than the p99
response time under load. The LB declared healthy
but slow instances as failed and removed them, reducing
capacity, which increased load on remaining instances,
causing them to also fail health checks. Cascading removal.

**Diagnostic Command:**
```bash
# Check health check config in AWS ALB
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:...

# Check historical health check failure timestamps
# vs traffic spike timestamps in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name UnHealthyHostCount \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T06:00:00Z \
  --period 60 \
  --statistics Maximum
```

**Fix:**
Set health check timeout >= p99 latency under load.
Increase unhealthy threshold to 3 consecutive failures
(reduces false positives). Add circuit breaker to
prevent cascade.

**Prevention:**
Load test to establish p99 under peak load. Set health
check timeout to p99 * 1.5.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Non-Functional Requirements` - availability is the
  most critical NFR for customer-facing systems

**Builds On This (learn these next):**
- `Single Point of Failure` - the specific architectural
  weakness that availability design eliminates
- `Redundancy and Failover` - the mechanism that achieves
  high availability in practice
- `Active-Active` - the highest-availability deployment
  pattern for write-heavy workloads
- `SLA / SLO / SLI` - the operational framework for
  measuring and enforcing availability targets

**Alternatives / Comparisons:**
- `Reliability` - broader concept (correct behavior, not
  just uptime); a system can be available but unreliable

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ % of time the system is operational and  │
│              │ serving users correctly                  │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Single component failure takes the whole │
│ SOLVES       │ system offline without user warning      │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Availability = 1 - (unavailability of all│
│              │ parallel instances). More redundancy     │
│              │ compounds to very high availability.     │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Any user-facing service where downtime   │
│              │ has business cost > cost of redundancy   │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Internal tools with acceptable planned   │
│              │ maintenance windows; dev environments    │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Load balancer without a standby is a SPOF│
│              │ that nullifies all other redundancy      │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Uptime vs cost (hardware + complexity)   │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Design for failure, not uptime.         │
│              │  Hardware fails. Architecture survives." │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ SPOF → Redundancy/Failover → Active-Activ│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Availability = 1 - unavailability. Two 99.9% components
   in parallel give 99.9999%. Redundancy compounds.
2. 99.9% = 8.7 hours downtime/year. 99.99% = 52 minutes.
   Know your nines before designing.
3. Health checks must match reality. A health check that
   passes during overload masks availability problems.

**Interview one-liner:**
"Availability is the percentage of time a system is
operational, achieved by removing every single point of
failure through redundancy and automated failover. The key
metric is how long between failure and automatic recovery -
not whether failures happen, but how quickly the system
routes around them."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Redundancy at each layer compounds to system-wide
availability far exceeding any individual component's
reliability. This principle - that parallel independent
components achieve reliability greater than any single
component - appears in every engineering discipline
where failure has consequences: aircraft have redundant
hydraulic systems, nuclear plants have redundant coolant
loops, and financial systems have redundant settlement
paths. The common insight is: assume failure will occur;
design the failure response, not just the success path.

**Where else this pattern appears:**
- **Networking infrastructure** - BGP routing uses multiple
  paths so that any path failure is automatically routed
  around without manual intervention.
- **Kubernetes pods** - ReplicaSets maintain N running
  pod replicas. When a pod fails, the controller spawns
  a replacement. The application is available because
  the failed pod is one of many.
- **RAID storage** - RAID-1 (mirroring) achieves storage
  availability by writing identical data to two disks.
  When one fails, reads continue from the surviving disk.

**Industry applications:**
- **Payments** - payment processors require 99.999%+
  availability. A single minute of Visa downtime affects
  millions of transactions globally. Multi-region active-
  active with synchronous cross-region replication is
  standard.
- **Healthcare** - hospital patient monitoring systems
  require continuous operation even during software
  updates. Rolling deployments with health-gated rollout
  prevent update-induced downtime.

---

### 💡 The Surprising Truth

The most significant availability failures in cloud
computing history were not caused by hardware failures
or software bugs - they were caused by operational
changes: configuration updates, schema migrations, and
maintenance operations. Amazon's 2017 S3 outage was
caused by a mistyped maintenance command. Facebook's
2021 six-hour outage was caused by a BGP configuration
change. GitHub's 2018 outage was caused by a database
failover that triggered unexpected replication issues.
The pattern is consistent: the most dangerous moment for
a highly available system is when a human operator is
making a change. The counterintuitive implication is
that the highest availability investment is not in
hardware redundancy but in change management tooling:
gradual rollouts, automated rollback, blast radius
limiting, and change approval gates.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Given an availability target (e.g., 99.99%),
   calculate the maximum allowable downtime per year
   and explain what architectural strategy achieves it.
2. [DEBUG] A load balancer is removing healthy instances
   from rotation. Given access to health check logs and
   latency metrics, identify whether this is a false
   positive and what configuration change fixes it.
3. [DECIDE] Given a write-heavy database with 99.99%
   availability target, choose between active-passive
   and active-active replication and justify the trade-off.
4. [BUILD] Configure a Spring Boot application with
   separate liveness and readiness probes that correctly
   reflect the health of upstream dependencies without
   causing false positives under load.
5. [EXTEND] Describe how the availability principles
   that apply to web servers also apply to a batch
   processing pipeline, identifying what "available"
   means for a pipeline that runs nightly.

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service has 99.9% availability for its
application tier and 99.9% availability for its database.
A performance test reveals that the database replica
lags by up to 30 seconds during peak load. Reads are
served from replicas. Explain: what is the actual
availability for read operations that must reflect
committed writes within 5 seconds?

*Hint: Distinguish between infrastructure availability
(the server responds) and application-level availability
(the data is correct). A request served from a lagging
replica may be technically successful but functionally
incorrect for operations requiring read-your-writes
consistency.*

**Q2.** You are designing a chat application where users
expect messages to appear within 1 second of being sent.
The message store has 99.99% availability. Define
"availability" for this specific product: what does
"the system is down" mean for a chat user, and does
the 99.99% infrastructure metric capture it?

*Hint: Think about the difference between "the server
is responding" and "the user successfully received a
message." Consider what happens if messages are being
lost or duplicated vs. if the server is genuinely
unreachable.*

**Q3 (Hands-On):** Take a production system you have
access to. List every single component in the request
path from user to data store. For each component,
identify: is there a redundant copy? If not, what is
the failure mode when that component fails? Pick the
most critical SPOF and sketch the change required to
eliminate it.

*Hint: Common overlooked SPOFs: the load balancer itself,
DNS resolution, the secrets manager, the config service,
and the observability stack. A system where you cannot
detect failures because the monitoring system is down
has a practical availability of 0% during that window.*

---

### 🎯 Interview Deep-Dive

**Q1: How would you achieve 99.99% availability for a
customer-facing API without using managed cloud services
(no AWS RDS Multi-AZ, no managed load balancers)?**
*Why they ask:* Tests depth of HA knowledge beyond
clicking checkboxes in cloud consoles. Can they reason
about the mechanism, not just the abstraction?
*Strong answer includes:*
- Multiple application instances behind HAProxy or
  Nginx configured with health checks and passive failover
- PostgreSQL streaming replication with Patroni for
  automatic primary election using etcd quorum
- Keepalived or VRRP for load balancer high availability
  (virtual IP floats between two LB nodes)
- Health check endpoint that validates DB and cache
  connectivity, not just server liveness

**Q2: Describe a real or hypothetical scenario where a
system had high infrastructure availability (servers
responding) but low application availability (users
experiencing failures). What caused the gap and how
would you detect it?**
*Why they ask:* Tests understanding of the gap between
infrastructure metrics and user experience metrics.
*Strong answer includes:*
- Database read replica lag: server is up, queries return
  stale data, users see missing data (availability
  metric says 100%, user experience says 0%)
- Circuit breaker in open state: server returns 503 fast
  (server is technically responsive), users cannot
  complete operations (application availability = 0%)
- Synthetic monitoring (canary requests) to detect the
  gap: execute a real user journey every 60 seconds and
  alert if the full journey fails

**Q3: How do you test that your high-availability
design actually works before it is needed in production?**
*Why they ask:* Tests engineering rigor - many teams
design HA systems but never validate them until the
real failure occurs, at which point they discover the
failover doesn't work.
*Strong answer includes:*
- Chaos engineering (Chaos Monkey, Gremlin): randomly
  terminate instances in production to validate auto-
  recovery works as designed
- Quarterly DR drills: simulate database primary failure
  and time the failover, validating RTO is within SLA
- Load testing failover path: confirm that when N-1
  instances are running (simulating one failure), the
  remaining instances handle the full load within SLO
- Runbook testing: confirm on-call can execute the
  failover runbook without assistance, within 15 minutes
