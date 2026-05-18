---
id: SYD-004
title: Single Point of Failure
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: SYD-003
used_by: SYD-019, SYD-020, SYD-021
related: SYD-003, SYD-019, SYD-008
tags:
  - reliability
  - foundational
  - architecture
  - mental-model
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 4
permalink: /technical-mastery/syd/single-point-of-failure/
---

⚡ TL;DR - A single point of failure (SPOF) is any component
whose failure alone takes down the entire system, and the
core goal of availability design is to eliminate every one.

| #004 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Availability | |
| **Used by:** | Redundancy and Failover, Active-Active, Active-Passive | |
| **Related:** | Availability, Redundancy and Failover, Load Balancing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2003, a software bug in an alarm system at a power
management facility in Ohio caused a cascade. One power
line tripped. Without the alarm, operators did not
re-route load. More lines tripped. Within 90 minutes,
55 million people across the northeastern United States
and Canada lost power. The alarm system was a single
point of failure. When it failed, operators lost
situational awareness. The cascade proceeded unchecked.

**THE BREAKING POINT:**
Any system with a component that, if it fails, causes
total system failure has an availability ceiling equal
to that component's reliability. If your database has
99% availability and there is no replica, your entire
system has a maximum of 99% availability regardless
of how resilient everything else is.

**THE INVENTION MOMENT:**
This is exactly why identifying and eliminating SPOFs
is the foundational practice of reliability engineering.
Before adding features, before optimizing performance,
before any other reliability work: find every SPOF
and introduce redundancy.

**EVOLUTION:**
Early systems had obvious SPOFs (single servers, single
disks). RAID (1988) eliminated disk SPOFs. Clustering
eliminated server SPOFs. The challenge moved from
physical hardware to software: a single config server,
a single certificate authority, a single DNS record.
Modern SPOFs are increasingly software and operational:
a single human who knows how to do a critical task,
a single runbook that covers an incident type.

---

### 📘 Textbook Definition

A single point of failure (SPOF) is any component,
resource, or process in a system such that its failure
causes the entire system to stop functioning. SPOFs
are identified through fault tree analysis or failure
mode and effects analysis (FMEA), which trace the
consequences of each component failure through the
system. Eliminating a SPOF requires introducing
redundancy - a parallel component that can assume
the failed component's function - combined with
automated detection and failover mechanisms.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A SPOF is the one thing that, if broken, breaks
everything - and finding them is job one in reliability.

**One analogy:**
> A chain is only as strong as its weakest link.
> A SPOF is that weak link. No matter how robust every
> other component is, one weak link can break the
> entire system. Reliability engineering is the
> practice of systematically adding parallel links
> until no single link can break the chain.

**One insight:**
SPOFs hide in plain sight. Engineers intuitively add
redundancy to obvious components (databases, servers)
while missing less obvious ones (the load balancer
itself, the DNS server, the certificate service, the
single developer who knows the deployment process).
A complete SPOF analysis traces EVERY component that
participates in request handling.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A system's availability cannot exceed the lowest
   availability of any single component in the critical
   path with no redundant alternative.
2. Redundancy transforms a serial dependency into a
   parallel one - raising the combined availability
   to near-certainty.
3. Redundancy without automated failover is not true
   redundancy - manual failover adds minutes to hours
   of human response time.

**DERIVED DESIGN:**
To eliminate SPOFs in a system, apply this process:
1. Map every component in the request's critical path
2. For each component: "if this fails, what happens?"
3. Any component whose failure causes total system
   failure is a SPOF
4. For each SPOF: add a redundant parallel component
   and an automated failover mechanism
5. Repeat until no single component failure causes
   total system failure

**THE TRADE-OFFS:**

**Gain:** Higher system availability; failure of any
individual component does not cascade to total failure.

**Cost:** More components to operate, monitor, and update;
consistency challenges across redundant components.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Some redundancy introduces real consistency
challenges - two database replicas can diverge during
a network partition. This is inherent to distributed
systems.

**Accidental:** Most SPOFs exist because nobody mapped
the critical path and asked "what fails here?" It is
not a physics problem - it is an analysis gap.

---

### 🧪 Thought Experiment

**SETUP:**
A 3-tier web application: user → load balancer → 3 app
servers → database primary → (database replica for reads).

**WHAT HAPPENS WITHOUT SPOF ANALYSIS:**
The team is proud: 3 app servers means no SPOF there.
Database replica for reads. But: they have one load
balancer. One Tuesday, the LB's memory fills due to a
connection leak bug. It stops accepting new connections.
All 3 app servers are healthy. The replica is healthy.
The database primary is healthy. Nothing matters - the
LB is the only path from users to the system. Total outage.

**WHAT HAPPENS WITH SPOF ANALYSIS:**
The team maps the full request path: DNS → LB → app
servers → database. They ask for each: "if this fails?"
For the LB: "total outage." They deploy two LBs in
active-passive with a virtual IP managed by Keepalived.
When LB-1 fails, LB-2 acquires the VIP within 2 seconds.
Users experience a 2-second blip. Not an outage.

**THE INSIGHT:**
SPOF analysis is most valuable before deployment.
Finding and eliminating SPOFs after a production outage
is expensive and happens under pressure. The thought
experiment "what fails here?" is free, fast, and should
be applied to every component diagram before implementation.

---

### 🧠 Mental Model / Analogy

> A SPOF is the "governor" of a colonial governor's
> office: if the governor is the only person with
> the authority to sign documents, and the governor
> goes on vacation, every government function stops.
> Availability engineering is distributing authority
> so that no single person's absence breaks the system.

- "Governor" → SPOF component
- "Vacation" → component failure or maintenance
- "Government functions stop" → user-visible outage
- "Deputy governor" → redundant component
- "Distributed authority" → no single component owns
  the only critical path

**Where this analogy breaks down:**
Human organizations distribute authority through trust
and training. Distributed systems distribute authority
through replication and consensus algorithms - which
introduce their own failure modes (split-brain, quorum
loss) that human organizations rarely face.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A SPOF is the one piece of your system that, if it breaks,
breaks everything. Like a single bridge across a river -
if it collapses, nobody gets across regardless of what
is on the other side.

**Level 2 - How to use it (junior developer):**
When designing any system, ask for each component:
"if this one thing fails, what happens?" If the answer
is "everything fails", you have found a SPOF. Add a
redundant backup component that can take over, and
configure an automated health check to detect failure
and switch traffic.

**Level 3 - How it works (mid-level engineer):**
SPOF analysis uses fault tree analysis: start from the
top (system failure) and trace backward through
component failures. Any component that is the sole
cause of system failure is a SPOF. Eliminate each by
adding a parallel component with: (1) data/state
replication so the backup is ready, (2) health monitoring
to detect failure, and (3) automated failover to switch
traffic without manual intervention.

**Level 4 - Why it was designed this way (senior/staff):**
The deeper challenge with SPOFs is that they exist at
multiple layers: hardware (single server), network
(single switch), software (single config service),
data (single database), operational (single developer
with knowledge), and organizational (single team without
runbook). Infrastructure SPOFs are easy to find and fix.
Operational and knowledge SPOFs are invisible until
the incident they cause. Elite reliability engineering
includes blameless postmortems specifically to surface
knowledge SPOFs: "only Alice knew how to do this - that
is a SPOF."

**Level 5 - Mastery (distinguished engineer):**
The meta-SPOF pattern: even redundant systems can have
a common cause failure that takes out all redundant
components simultaneously. Two database replicas in
the same availability zone share the same power feed.
Two app servers running the same buggy code version
will both fail when the bug is triggered. Expert
reliability engineers look for common cause failures:
shared power, shared network, shared software version,
shared configuration source. The fix is not just
redundancy - it is independence of failure modes.

---

### ⚙️ How It Works (Mechanism)

**SPOF identification methodology:**

```
┌────────────────────────────────────────────────┐
│ SPOF ANALYSIS PROCESS                          │
├────────────────────────────────────────────────┤
│  1. DRAW THE REQUEST PATH                      │
│     Every component from user to data store    │
│     and back. Include every hop.               │
├────────────────────────────────────────────────┤
│  2. FOR EACH COMPONENT: SIMULATE FAILURE       │
│     "If this is unreachable for 5 minutes,     │
│     what does the user experience?"            │
├────────────────────────────────────────────────┤
│  3. CLASSIFY RESULTS                           │
│     SPOF: user experiences total failure       │
│     Degraded: user experience worsens          │
│     Isolated: user is unaffected               │
├────────────────────────────────────────────────┤
│  4. PRIORITIZE BY IMPACT                       │
│     SPOF with high failure rate → fix first    │
│     SPOF with low failure rate → fix second    │
│     Degraded path → fix if budget allows       │
├────────────────────────────────────────────────┤
│  5. ADD REDUNDANCY + FAILOVER                  │
│     Parallel component (standby/active)        │
│     Health check mechanism                     │
│     Automated failover trigger                 │
├────────────────────────────────────────────────┤
│  6. VERIFY WITH CHAOS TEST                     │
│     Actually kill the SPOF in staging          │
│     Confirm failover works within SLA          │
└────────────────────────────────────────────────┘
```

**Common SPOFs by layer:**

```
NETWORK LAYER:
  - Single load balancer
  - Single DNS resolver
  - Single network switch/router
  - Single internet uplink

APPLICATION LAYER:
  - Single API gateway
  - Single config service
  - Single secrets manager
  - Single auth service

DATA LAYER:
  - Single database primary (no replica)
  - Single cache (no replica)
  - Single message broker

OPERATIONAL LAYER:
  - Single developer with root access
  - Unwritten deployment knowledge
  - Single person who knows the on-call runbook
  - Single manual step in automated pipeline
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[User]
  → [DNS] (SPOF if no secondary DNS)
  → [Load Balancer] (SPOF if single instance)
  → [App Server Pool] (not SPOF if 2+ instances)
  → [Config Service] (SPOF if single instance)
  → [Cache] (SPOF if single node, no fallback)
  → [Database Primary] (SPOF if no replica+failover)
  → [Response]

← YOU ARE EXAMINING EACH ARROW FOR SPOF
```

**FAILURE PATH (SPOF present):**
```
Load Balancer fails (SPOF)
  → ALL requests fail immediately
  → App servers are healthy but unreachable
  → Database is healthy but irrelevant
  → Full outage until LB is manually replaced
  → Manual replacement takes 30-120 minutes
```

**FAILURE PATH (SPOF eliminated):**
```
Load Balancer 1 fails (now NOT a SPOF)
  → VIP floats to Load Balancer 2 (Keepalived, 2s)
  → Requests continue through LB-2
  → App servers are unaffected
  → Brief connection reset for in-flight requests
  → Alert fires: "LB-1 down, LB-2 active"
```

**WHAT CHANGES AT SCALE:**
At 10x scale, the SPOF analysis must include the
redundancy mechanism itself: is the Keepalived process
a SPOF? Is the etcd cluster used for leader election
resilient to node failure? SPOFs exist recursively -
the thing that eliminates a SPOF can itself be a SPOF.

---

### 💻 Code Example

**Example 1 - BAD: Single Redis with no SPOF protection**
```yaml
# BAD: One Redis instance. If it fails, all
# session data is lost and all users are logged out.
redis:
  url: redis://redis-single:6379
```

**Example 2 - GOOD: Redis with replica and sentinel**
```yaml
# GOOD: Three sentinels provide quorum. Primary
# failure is automatically detected. Replica is
# promoted. Application reconnects to new primary.
redis:
  sentinel:
    master-name: "prod-cache"
    nodes:
      - sentinel-1:26379
      - sentinel-2:26379
      - sentinel-3:26379
  # If ALL sentinels fail (common cause SPOF),
  # fall back to local in-memory cache with TTL
  fallback:
    type: caffeine
    max-size: 10000
    ttl-seconds: 60
```

**Example 3 - Production: Circuit breaker as SPOF guard**
```java
// GOOD: Even with Redis Sentinel, if the sentinel
// cluster has issues, the circuit breaker prevents
// the SPOF from causing cascading failures.
@Service
public class SessionService {

    @Autowired
    private RedisTemplate<String, String> redis;

    private CircuitBreaker cb = CircuitBreaker
        .ofDefaults("redis-session");

    public Optional<String> getSession(String id) {
        return Try.ofSupplier(
            CircuitBreaker.decorateSupplier(cb,
                () -> redis.opsForValue().get(id))
        )
        .recover(throwable -> {
            // Fallback: DB session or reject request
            log.warn("Redis unavailable, "
                + "falling back to DB session");
            return dbSessionStore.get(id);
        })
        .toJavaOptional();
    }
}
```

---

### ⚖️ Comparison Table

| SPOF Type | Discovery | Fix Complexity | Failure Impact | Example |
|---|---|---|---|---|
| **Hardware** | Easy (visible) | Low | High | Single server |
| Network | Medium | Medium | High | Single LB, switch |
| Software | Hard (needs analysis) | Medium | Variable | Single config svc |
| Operational | Very hard | High (org change) | Very high | Single expert |
| Data | Medium | High | Critical | No DB replica |

**How to choose priority:**
Fix the SPOF with the highest product of (failure
probability × blast radius). A database primary with no
replica and high write volume is more urgent than a
manually-operated service used once per week.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Multiple instances eliminate SPOFs | Multiple instances behind a single load balancer still have the LB as a SPOF |
| Cloud providers eliminate SPOFs | Managed services have availability guarantees, but selecting a single availability zone creates SPOFs within those services |
| SPOFs are only hardware components | Operational knowledge, runbooks, and credentials stored in one place are SPOFs |
| Eliminating all SPOFs makes a system 100% available | Redundant components can fail simultaneously (common cause). 100% availability is not achievable. |
| SPOF analysis is a one-time activity | Systems evolve. New components are added. SPOF analysis must be repeated on every significant architectural change. |

---

### 🚨 Failure Modes & Diagnosis

**Hidden SPOF: Config Service**

**Symptom:**
During a routine config service restart, all application
instances begin returning 500 errors. The config service
was down for 4 minutes for a rolling update.

**Root Cause:**
All application instances reload config on startup and
on a 60-second refresh interval. The config service
was a SPOF - when unreachable, instances couldn't
refresh config and started failing health checks,
causing the LB to remove all instances simultaneously.

**Diagnostic Command:**
```bash
# Check config service dependency
grep -r "configService\|consul\|vault" \
  src/ --include="*.java" | \
  grep -v "fallback\|default\|cache"

# Find all components that fail if config unreachable
docker inspect app-container | \
  jq '.Config.Env[] | select(contains("CONFIG"))'

# Check if config is cached locally
kubectl exec app-pod -- \
  ls /tmp/config-cache/ 2>/dev/null || \
  echo "No local config cache - SPOF risk"
```

**Fix:**
Cache config locally on each instance. Use stale config
rather than failing when config service is unreachable.
Set a maximum stale age (e.g., 1 hour) after which the
instance gracefully removes itself from rotation.

**Prevention:**
Require every external dependency to have a defined
behavior when unavailable. Cached stale value? Degraded
mode? Reject requests? The answer must be explicit.

---

**Common Cause SPOF**

**Symptom:**
Two database replicas fail simultaneously during a
routine OS security patch that is applied to all
instances in the same maintenance window.

**Root Cause:**
The replicas shared the same OS version, same patch
schedule, and same physical host cluster. A bug in
the patch caused a kernel panic on all three nodes
simultaneously. The "redundancy" was illusory because
all redundant components shared a common failure mode.

**Diagnostic Command:**
```bash
# Check if all replicas share same OS/kernel version
for host in db-primary db-replica-1 db-replica-2; do
  ssh $host "uname -r && lsb_release -r"
done

# Check if all are in same availability zone
aws ec2 describe-instances \
  --filters "Name=tag:Role,Values=database" \
  --query 'Reservations[].Instances[].[
    InstanceId, Placement.AvailabilityZone
  ]'
```

**Fix:**
Stagger maintenance windows across redundant components.
Use different availability zones. Consider different
OS distributions for primary vs replica to eliminate
common cause failure.

**Prevention:**
In the availability zone / maintenance window plan,
require that no two replicas of the same service share
a maintenance window, an availability zone, or a
physical host cluster.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Availability` - SPOF is the primary cause of
  availability failures; understanding availability
  targets first gives context for SPOF severity

**Builds On This (learn these next):**
- `Redundancy and Failover` - the mechanism used to
  eliminate SPOFs once identified
- `Active-Active` - highest-availability pattern that
  eliminates write-path SPOFs
- `Load Balancing` - the first layer where SPOFs
  commonly hide

**Alternatives / Comparisons:**
- `Bulkhead Pattern` - prevents SPOFs from causing
  cascading failures across service boundaries
- `Circuit Breaker` - isolates SPOF impact to callers
  of a failing component

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Any component whose failure alone causes │
│              │ total system failure                     │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ One hardware or software failure brings  │
│ SOLVES       │ down an entire system serving thousands  │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ SPOFs hide beyond hardware: the single   │
│              │ load balancer, single config service, and│
│              │ single knowledgeable engineer are all SPO│
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Every system design review - ask "what   │
│              │ single failure causes total outage?"     │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ N/A - SPOF analysis is always applicable │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Redundant components in the same AZ with │
│              │ the same maintenance schedule = common   │
│              │ cause SPOF (pseudo-redundancy)           │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Reliability (no single failure = outage) │
│              │ vs cost and complexity of redundancy     │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Every SPOF is a countdown timer.        │
│              │  Find them before production does."      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Redundancy/Failover → Active-Passive →   │
│              │ Active-Active                            │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. A system's availability cannot exceed the availability
   of its worst SPOF. Fix SPOFs before optimizing anything.
2. SPOFs exist at every layer: hardware, network, software,
   data, and operational (knowledge/process).
3. Redundancy without independence is pseudo-redundancy.
   Two instances in the same AZ on the same maintenance
   schedule can fail together.

**Interview one-liner:**
"A single point of failure is any component whose failure
alone takes down the system. Eliminating SPOFs requires
mapping every component in the request path, adding
a redundant parallel component for each SPOF, and
configuring automated failover - because manual failover
adds hours of downtime to what should be seconds."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any system whose components must all succeed is bounded
by the least reliable component. Any system where at
least one of N parallel components must succeed achieves
reliability far exceeding any individual component. This
principle applies to every engineered system: aircraft
engines (any engine can fail; the plane still lands),
RAID storage (any disk can fail; data is preserved),
and TCP/IP routing (any path can fail; packets re-route).
The design principle is: eliminate serial dependencies,
introduce parallel alternatives.

**Where else this pattern appears:**
- **RAID storage** - RAID-1 mirrors data to two disks.
  Either disk is a SPOF alone; mirrored, they are not.
- **Kubernetes DaemonSet vs Deployment** - a Deployment
  with 1 replica is a SPOF. A Deployment with 3 replicas
  tolerates 2 simultaneous failures.
- **DNS failover** - primary DNS record points to primary
  server; secondary record provides failover. Single DNS
  record is a SPOF; dual-record is not.

**Industry applications:**
- **Aviation** - every critical aircraft system has
  triple redundancy: primary, secondary, tertiary.
  Any two can fail; the third maintains control.
  SPOFs in aviation are design defects, not acceptable
  trade-offs.
- **Nuclear power** - cooling systems have SPOF analysis
  mandated by regulation. No single valve, pump, or
  sensor can be the sole mechanism preventing meltdown.

---

### 💡 The Surprising Truth

The most consequential SPOF in engineering history
was not a hardware component - it was a design
assumption. The Challenger Space Shuttle disaster (1986)
was caused by a SPOF in the O-ring sealing mechanism:
a single ring design that would fail at low temperatures.
Engineers at Morton Thiokol had identified the risk
in writing 12 months before the disaster, but the
escalation path itself was a SPOF - a single management
decision gate that overruled engineering concerns with
schedule pressure. The physical SPOF (the O-ring) was
identified. The organizational SPOF (no independent
safety authority with veto power) was not. The lesson
that the SPOF most likely to kill your system is the
one embedded in your organization's decision-making
structure, not in its hardware, is still underappreciated
in software engineering.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Given a 3-tier web application diagram,
   identify every SPOF and explain why each represents
   a total-failure risk, not just a degradation risk.
2. [DEBUG] A production incident is caused by a SPOF
   failing. Given the incident timeline and component
   logs, identify the SPOF, the detection latency, and
   the manual recovery time. Define what automated
   failover would have reduced that to.
3. [DECIDE] Given budget for one redundancy improvement,
   choose between: making the LB highly available,
   adding a DB replica, or adding an app server. Justify
   using failure probability × blast radius reasoning.
4. [BUILD] Draw the current architecture of a system
   you work on. Circle every SPOF. Estimate the MTBF
   (mean time between failures) for each SPOF component.
5. [EXTEND] Identify a SPOF in a non-technical system
   you interact with (a supply chain, a hospital, a
   government process). Map the technical SPOF elimination
   pattern to the non-technical domain.

---

### 🧠 Think About This Before We Continue

**Q1.** A microservices system has 20 services, each with
2 instances behind a load balancer. The team is proud
of their redundancy. On investigation, all 20 services
are deployed via a single CI/CD pipeline that uses one
Jenkins master. What is the SPOF, what is the blast
radius of its failure, and what is the fix that
preserves the team's deployment workflow?

*Hint: Think about what "Jenkins master fails during
a critical deployment" means for the entire system.
The SPOF is not the service instances - it is the
deployment infrastructure. Consider whether a deployment
system failure is a total outage or just a capability
outage (existing instances still serve traffic).*

**Q2.** You eliminate every hardware SPOF in your system:
HA load balancers, database primaries with replicas,
multiple app servers. Six months later you have an
outage. The post-mortem reveals the root cause was
a TLS certificate expiry that took down every service
simultaneously. What class of SPOF does this represent
and what would a systematic solution look like?

*Hint: Think about what "TLS certificate" is in the
context of the request path - it is a credential that
every HTTPS connection depends on. Certificate expiry
is a time-based SPOF with perfect predictability.
What automated process eliminates this class of SPOF?*

**Q3 (Hands-On):** Draw the complete request path of
a system you use daily (e.g., a checkout flow, a
login flow, a search). For each component, ask:
"What is the failure rate of this type of component?"
(Use: servers ~0.1%/day, LBs ~0.01%/day, databases
~0.05%/day.) Calculate the combined availability
assuming series components. Then identify the two
highest-impact SPOFs and sketch the fix for each.

*Hint: Use the series availability formula:
A_total = A1 × A2 × ... × An. Then compare with the
parallel formula for redundant components:
A_pair = 1 - (1-A1)(1-A2). The math will reveal which
SPOFs most reduce total availability.*

---

### 🎯 Interview Deep-Dive

**Q1: How do you identify single points of failure
in a system you are reviewing for the first time?**
*Why they ask:* Tests whether the candidate has a
systematic methodology or just looks for obvious issues.
*Strong answer includes:*
- Request path tracing: follow a user request from
  browser to data store, listing every component
- For each component: failure mode analysis
  ("if this fails, what does the user experience?")
- Blast radius classification: total failure vs
  degraded vs isolated
- Layer-by-layer analysis: network, application,
  data, operational

**Q2: Your system has two database replicas for read
traffic and one primary for writes. A senior engineer
says the write primary is a SPOF. Do you agree,
and if so how would you fix it?**
*Why they ask:* Tests depth of database HA knowledge
and trade-off awareness.
*Strong answer includes:*
- Yes, the single write primary is a SPOF: its failure
  means no writes until failover completes (could be
  30-60 seconds with automated failover, or minutes
  with manual)
- Fix options: synchronous replica with automated
  promotion (active-passive, lower complexity), or
  multi-master with conflict resolution (active-active,
  higher complexity but zero downtime on primary failure)
- The right answer depends on write volume, consistency
  requirements, and tolerated write downtime window

**Q3: How do you distinguish between a true SPOF and
a component that merely degrades the system when it fails?**
*Why they ask:* Tests precision of thinking - not every
dependency failure is a SPOF.
*Strong answer includes:*
- SPOF: failure causes zero successful user operations
  (binary - system either works or does not)
- Degraded path: failure causes reduced quality or
  partial feature set (non-binary - some operations
  still succeed)
- Examples: cache failure = degraded (slower reads,
  but reads succeed from DB); LB failure = SPOF
  (no reads or writes succeed at all)
- Prioritize SPOFs over degraded paths; both matter
  but SPOFs violate availability SLOs, degraded paths
  violate latency or feature SLOs
