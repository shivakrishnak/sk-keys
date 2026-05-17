---
id: MSV-008
title: Health Check Patterns
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-002, MSV-006
used_by: MSV-009, MSV-014
related: MSV-009, MSV-006, MSV-014, MSV-044
tags:
  - microservices
  - distributed
  - intermediate
  - observability
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /microservices/health-check-patterns/
---

# MSV-008 - Health Check Patterns

⚡ TL;DR - Health Check Patterns are the contracts that
a service exposes to tell the platform whether it is
alive (should it be restarted?) and ready (should it
receive traffic?). Getting these wrong costs production.

| #008 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Microservices Architecture, Service Registry | |
| **Used by:** | Readiness and Liveness Probes, Load Balancing in Microservices | |
| **Related:** | Readiness and Liveness Probes, Service Registry, Load Balancing in Microservices, Circuit Breaker | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your service is running - the process is alive. But its
database connection pool is exhausted. All requests are
queuing indefinitely and timing out. From the outside, your
service looks healthy (port is open, process running).
The load balancer keeps routing traffic to it. Users get
500 errors. The platform does not restart the service
because nothing has crashed. Your service is a zombie:
technically alive, functionally dead.

**THE BREAKING POINT:**
Process-level health (is the port open?) is insufficient for
distributed systems. A JVM process can be alive while its
database connection is broken, its thread pool is exhausted,
its external dependencies are down, or its cache is
corrupted. Routing traffic to such a service is worse than
routing to no service - it creates a queue of failing requests
rather than immediately returning an error the caller can handle.

**THE INVENTION MOMENT:**
This is why health check patterns were designed: explicit
HTTP endpoints that a service exposes to describe its actual
functional state, not just its process state.

**EVOLUTION:**
Early load balancers polled a TCP port. AWS ELB (2009) added
HTTP health checks. Netflix Eureka (2012) used health check
endpoints for registry status. Kubernetes (2015) formalised
the split into liveness probes (restart?), readiness probes
(route traffic?), and later startup probes (allow boot time).
Spring Boot Actuator (2015+) standardised the `/actuator/health`
endpoint with component-level health reporting.

---

### 📘 Textbook Definition

**Health Check Patterns** are a set of API contracts between
a service and its infrastructure - load balancers, service
registries, container orchestrators, and service meshes -
that allow the infrastructure to query the operational state
of a service instance. The three primary patterns are:

1. **Liveness** - is the service in a state from which it
   can recover, or should it be restarted?
2. **Readiness** - is the service ready to accept and
   process requests?
3. **Startup** - has the service completed its initialisation
   phase? (Gate liveness and readiness during long startups)

Each answers a different question for a different consumer.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Health checks are your service's way of saying: "I'm alive
and taking requests" vs "I'm alive but don't route to me
right now" vs "restart me, I'm stuck".

**One analogy:**
> A restaurant has two states: "open" (health check: ready to
> serve customers) and "operating" (health check: lights on,
> people inside). You can have lights on but be closed (process
> running but not ready). You can be open but the kitchen is
> on fire (ready but not actually functional). Customers
> (callers) need accurate information or they waste a trip
> (a failed request).

**One insight:**
Liveness and readiness serve completely different purposes.
Mixing them causes either unnecessary restarts (treating
"database is down" as "restart me") or unnecessary downtime
(treating "not ready" as "needs a restart").

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Infrastructure must never route traffic to an instance
   that cannot handle it successfully.
2. Infrastructure must restart instances that are stuck
   in an unrecoverable state.
3. Health check overhead must not itself harm the service.

**THE THREE CHECKS:**

```
LIVENESS CHECK  → Should the container be restarted?
─────────────────────────────────────────────────────
Answer: NO (200) → service might be busy but recoverable
Answer: YES (500) → deadlock, OOM, stuck process - restart

READINESS CHECK → Should traffic be routed here?
─────────────────────────────────────────────────
Answer: YES (200) → all dependencies healthy, ready
Answer: NO (503) → DB down, warming up - remove from LB

STARTUP CHECK   → Is the service still initialising?
─────────────────────────────────────────────────────
Answer: DONE (200) → begin liveness + readiness checks
Answer: STILL LOADING → wait, don't restart yet
```

**THE TRADE-OFFS:**
**Liveness too sensitive:** Marking DOWN because a dependency
is temporarily slow will cause the container to restart,
losing all in-flight requests, and likely fail to start
again because the dependency is still slow. Cascading restart
loops ensue.
**Readiness too insensitive:** Routing traffic to a
service that has not finished warming up (connection pools
not initialised) causes initial request failures. Routing to
a service with a degraded DB connection means all requests
degrade, not just some.

---

### 🧪 Thought Experiment

**SETUP:**
A service depends on a Redis cache (non-critical, degrades
to slower DB path) and a PostgreSQL database (critical,
cannot serve any requests without it).

**SCENARIO: Redis goes down.**
Liveness: Should restart? No - service can run without Redis.
Readiness: Should take traffic? Yes - service degrades
gracefully (falls through to DB path). Mark Redis as
DEGRADED in health response but overall status UP.

**SCENARIO: PostgreSQL goes down.**
Liveness: Should restart? No - restart won't fix the DB.
Readiness: Should take traffic? No - all requests will
fail. Mark status DOWN to remove from load balancer rotation.
Service waits for DB recovery, then self-heals.

**SCENARIO: Service has a deadlock in a critical thread pool.**
Liveness: Should restart? Yes - the deadlock is unrecoverable
without a restart. Mark status DOWN for liveness.
Result: container restarts, deadlock cleared, service recovers.

**THE INSIGHT:**
Health checks must encode the business logic of what "healthy"
means for each service. A generic "check if port is open"
misses all three scenarios above.

---

### 🧠 Mental Model / Analogy

> A hospital emergency department has two admission states:
> "Accepting ambulances" (readiness - taking new patients)
> and "Functioning as a hospital" (liveness - able to
> operate at all).
> When the ED is full (at capacity), it diverts ambulances
> (readiness = NOT READY) but does not shut down (liveness
> = ALIVE). When the building has a structural failure
> (unrecoverable), it closes entirely (liveness = DOWN, needs restart).

- "Accepting ambulances" - readiness probe
- "Functioning as a hospital" - liveness probe
- "Full, diverting ambulances" - readiness DOWN (no traffic)
  but liveness OK (no restart)
- "Structural failure" - liveness DOWN (restart)

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A health check is an HTTP endpoint on your service that
infrastructure polls to decide: should I send traffic here?
Should I restart it? Is it still starting up?

**Level 2 - How to use it (junior developer):**
With Spring Boot Actuator, add the dependency. The endpoints
`/actuator/health/liveness` and `/actuator/health/readiness`
are available automatically. In `application.yml`, set
`management.endpoint.health.probes.enabled=true`. Kubernetes
readiness probe points to `/actuator/health/readiness`;
liveness probe points to `/actuator/health/liveness`.

**Level 3 - How it works (mid-level engineer):**
Spring Boot Actuator composes a health status from
contributors (database, Redis, disk space, etc.). Each
contributor returns UP, DOWN, or OUT_OF_SERVICE. The
overall status is the worst of all contributors. Custom
contributors implement `HealthIndicator`. Readiness and
liveness are separate groups - a service can mark readiness
DOWN (stop receiving traffic) without marking liveness DOWN
(no restart), e.g., during scheduled maintenance.

**Level 4 - Why it was designed this way (senior/staff):**
The liveness/readiness split was designed to handle the
most dangerous failure mode in Kubernetes: a service that
continuously fails its health check and gets into a crash
loop. If liveness is too sensitive (marks DOWN when any
dependency is slow), every temporary dependency issue
causes a restart cascade. The split ensures only truly
unrecoverable states trigger a restart, while temporary
unavailability is handled by readiness (remove from rotation,
wait for recovery).

**Level 5 - Mastery (distinguished engineer):**
The health check contract extends beyond Kubernetes probes.
Load balancers, service meshes (Envoy), service registries
(Eureka, Consul), and circuit breakers all consume health
state. A sophisticated health check strategy coordinates
all layers: Kubernetes readiness for platform routing,
Consul health for cross-cluster discovery, custom health
events for circuit breaker pre-warming. The health check
endpoint is a service's primary contract with its infrastructure.

---

### ⚙️ How It Works (Mechanism)

**SPRING BOOT ACTUATOR HEALTH CHAIN:**

```
GET /actuator/health/readiness
  │
  ▼
HealthEndpoint
  │ collects from HealthContributorRegistry
  │
  ├─ DataSourceHealthIndicator
  │    → executes: SELECT 1 FROM DUAL
  │    → status: UP
  │
  ├─ RedisHealthIndicator
  │    → executes: PING
  │    → status: DOWN
  │
  └─ DiskSpaceHealthIndicator
       → checks free space threshold
       → status: UP

CompositeHealthContributor
  → worst status = DOWN (because Redis is DOWN)
  → HTTP 503 (OUT_OF_SERVICE / DOWN)
```

**CUSTOM HEALTH INDICATOR:**

```java
@Component
public class ExternalApiHealthIndicator
    implements HealthIndicator {

    private final ExternalApiClient client;

    @Override
    public Health health() {
        try {
            // Check critical dependency
            boolean ok = client.ping();
            if (ok) {
                return Health.up()
                    .withDetail("latency", "12ms")
                    .build();
            }
            return Health.down()
                .withDetail("reason", "ping failed")
                .build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

**KUBERNETES PROBE CONFIGURATION:**

```yaml
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 30  # allow startup
  periodSeconds: 5         # check every 5s
  failureThreshold: 3      # 3 fails → not ready
  successThreshold: 1      # 1 pass → ready again

livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 60  # after startup completes
  periodSeconds: 10
  failureThreshold: 3      # 3 fails → restart
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ROLLING DEPLOYMENT HEALTH FLOW:**

```
New pod starts
  │
  ▼ initialDelaySeconds (30s)
Startup probe polls /actuator/health/liveness
  │ returns 503 (JVM warming, DB not ready)
  ▼ (waits, no restart during startup)
DB connection established, caches populated
  │
  ▼
Readiness probe passes: /actuator/health/readiness → 200
  │
  ▼
Kubernetes adds pod to Endpoints object
  │
  ▼
Load balancer routes traffic to new pod
  │
  ▼
Old pod: readiness probe marked NOT READY
         → removed from Endpoints
         → graceful shutdown (SIGTERM)
         → preStop hook waits 15s (in-flight requests drain)
         → pod terminated
```

**FAILURE PATH:**
```
DB connection pool exhausted
  → DataSourceHealthIndicator returns DOWN
  → Readiness: 503 (removed from load balancer)
  → Liveness: 200 (don't restart - DB is the problem)
  → Service waits for pool recovery
  → On recovery: Readiness returns 200
  → Kubernetes adds back to Endpoints
  → Traffic resumes
  → No data loss, no restart
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: liveness check too sensitive**

```java
// BAD: liveness checks external dependencies
// If Redis is down: pod restarts
// Redis is still down after restart → restart loop
@Component
public class BadLivenessIndicator
    implements HealthIndicator {

    @Autowired
    private RedisTemplate<String, String> redis;

    @Override
    public Health health() {
        // WRONG: external dependency in liveness check
        redis.opsForValue().get("health-key");
        return Health.up().build();
    }
}
```

```java
// GOOD: liveness only checks internal process health
// Readiness checks external dependencies
@Component
// Only contributes to liveness group
@ConditionalOnManifestEntry("liveness")
public class GoodLivenessIndicator
    implements HealthIndicator {

    private final ThreadPoolExecutor executor;

    @Override
    public Health health() {
        // Check: are internal threads responsive?
        int active = executor.getActiveCount();
        int max = executor.getMaximumPoolSize();
        if (active >= max) {
            // Thread pool full - might be stuck
            return Health.down()
                .withDetail("activeThreads", active)
                .withDetail("maxThreads", max)
                .build();
        }
        return Health.up().build();
    }
}
```

**Example 2 - Graceful readiness during deployment**

```java
// Application event listener for controlled readiness
@Component
public class ReadinessController
    implements ApplicationListener<ApplicationEvent> {

    @Autowired
    private ApplicationContext context;

    public void markNotReady() {
        // Used during pre-maintenance window
        AvailabilityChangeEvent.publish(
            context,
            ReadinessState.REFUSING_TRAFFIC);
    }

    public void markReady() {
        AvailabilityChangeEvent.publish(
            context,
            ReadinessState.ACCEPTING_TRAFFIC);
    }
}
// Called by deployment scripts to drain gracefully:
// 1. Mark NOT_READY (readiness probe fails)
// 2. Wait for in-flight requests to complete
// 3. Perform maintenance
// 4. Mark READY (readiness probe passes)
// 5. Traffic resumes
```

---

### ⚖️ Comparison Table

| Check Type | Purpose | Failure Response | Checks External Deps? |
|---|---|---|---|
| **Liveness** | Process stuck/deadlocked? | Container restart | No - internal only |
| **Readiness** | Ready for traffic? | Remove from load balancer | Yes - DB, Redis, etc. |
| **Startup** | Still initialising? | Delay liveness/readiness | Yes - await init |
| Legacy TCP check | Port open? | Remove from LB | No |

**Rule of thumb:**
- Liveness = internal process health only (thread pools,
  internal state)
- Readiness = full dependency chain health
- Startup = set `initialDelaySeconds` equivalent using a
  probe that only succeeds after init is complete

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Liveness probe failure should restart the pod, fixing the problem | If the problem is an external dependency (DB down), restart doesn't fix it. The pod restarts into the same failure → restart loop. Only mark liveness DOWN for internal, unrecoverable failures. |
| A 200 response means the service is fully functional | Only if the health check verifies actual functional state. A naive `@GetMapping("/health") return OK` tells you nothing about whether the service can actually process business requests. |
| Health check frequency doesn't matter | A health check that executes a DB query every second on 1000 pod instances = 1000 DB queries/second from health checks alone. Design health checks to be cheap. |

---

### 🚨 Failure Modes & Diagnosis

**Crash loop caused by liveness checking external dependency**

**Symptom:**
Service is in `CrashLoopBackOff` in Kubernetes. Logs show
the service starts successfully, connects to DB, processes
a few requests, then restarts every 2-3 minutes.

**Root Cause:**
The liveness probe checks the database connection. A network
glitch causes a 2-second DB timeout. Liveness returns 503.
Three consecutive failures → Kubernetes restarts the pod.
The new pod starts but the DB network is still intermittent.
Cycle repeats.

**Diagnostic Command:**
```bash
kubectl describe pod order-service-xxx | grep -A20 Liveness
kubectl logs order-service-xxx --previous | tail -50
kubectl get events --field-selector \
  involvedObject.name=order-service-xxx
```

**Fix:**
Remove DB check from liveness probe. Move to readiness probe.
If liveness truly needs to fail eventually (e.g., after 10
consecutive failures), use a much higher `failureThreshold`
(10+) and longer `periodSeconds` (30s).

**Prevention:**
Liveness checks must never call external services.
Code review gates to enforce this rule.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Microservices Architecture` - why individual service
  health matters for the whole system
- `Service Registry` - registries use health checks to
  determine which instances to include

**Builds On This (learn these next):**
- `Readiness and Liveness Probes` - Kubernetes-specific
  implementation of health check patterns
- `Load Balancing in Microservices` - load balancers use
  health checks to route traffic

**Alternatives / Comparisons:**
- `Circuit Breaker` - reactive to observed failures (not
  self-reported); complementary to health checks
- `Service Mesh` - Envoy proxies can observe and report
  service health without explicit health check endpoints

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LIVENESS     │ Is the service alive and can it recover?  │
│              │ FAIL → restart container                  │
├──────────────┼───────────────────────────────────────────┤
│ READINESS    │ Is the service ready to serve traffic?    │
│              │ FAIL → remove from load balancer          │
├──────────────┼───────────────────────────────────────────┤
│ STARTUP      │ Is initialisation complete?               │
│              │ IN PROGRESS → delay other probes          │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ LIVENESS: internal only (no ext deps)     │
│              │ READINESS: full dependency health         │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ DB check in liveness → crash loop when    │
│              │ DB has a transient blip                   │
├──────────────┼───────────────────────────────────────────┤
│ PERFORMANCE  │ Health check = 1 DB query/second * 1000   │
│              │ pods = 1000 queries/sec overhead          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Liveness: should I restart this?         │
│              │  Readiness: should I route to this?"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Readiness and Liveness Probes (K8s depth) │
│              │ → Load Balancing → Circuit Breaker        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Never check external dependencies in the liveness probe -
   it will cause restart loops when dependencies are slow.
2. Readiness and liveness are different questions with
   different answers. A service can be alive but not ready,
   and ready but degraded.
3. Health check logic must reflect actual business capability.
   A service with a broken DB connection that returns 200
   from `/health` is lying to its infrastructure.

**Interview one-liner:**
"Health check patterns define how a service communicates its
operational state to the platform. Liveness answers 'should
this be restarted?' - only for internal, unrecoverable states.
Readiness answers 'should this receive traffic?' - includes
dependency health. Never put external dependency checks in
the liveness probe or you risk restart cascades."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The health check is a contract between a service and its
infrastructure. Like any contract, it must be precise:
over-reporting (always healthy) breaks routing; under-reporting
(healthy = dependencies reachable) causes restart loops.
Calibrate to your actual failure modes.

**Where else this pattern appears:**
- Database replication: `SHOW SLAVE STATUS` - is the replica
  healthy enough to take reads? Analogous to readiness.
- Load balancer health checks: ELB target health, HAProxy
  backend health - server-side readiness polling
- OS process supervisors (systemd): `ExecStartPost` health
  check gates on service startup - analogous to startup probe

---

### 💡 The Surprising Truth

The Spring Boot `@SpringBootApplication` sets up graceful
shutdown automatically (since Spring Boot 2.3). When a SIGTERM
is received, Spring sets the readiness state to
`REFUSING_TRAFFIC` before the application context begins
shutting down. This means the load balancer sees the service
as not ready and stops routing before shutdown begins -
exactly correct behaviour. But this only works if
`server.shutdown=graceful` is set in `application.yml`. Without
it, the JVM shuts down abruptly while requests are in-flight.
A one-line configuration difference between graceful rolling
deploys (zero failed requests) and dropping live connections.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Walk through the exact failure mode of a
   liveness probe that checks a database connection, and
   trace the events from "DB slow" to "CrashLoopBackOff".
2. **DEBUG** Given a pod in CrashLoopBackOff, determine
   within 3 minutes whether the cause is liveness
   misconfiguration, a startup that exceeds
   `initialDelaySeconds`, or a genuine application crash.
3. **DESIGN** Design a health check strategy for a Spring
   Boot service with 3 dependencies: PostgreSQL (critical),
   Redis (graceful degradation), and an external payment API
   (optional feature). Which dependency goes in which probe?
4. **BUILD** Implement a custom `HealthIndicator` for a
   connection pool that returns DOWN when the pool is 95%
   utilised and DEGRADED when 80% utilised.
5. **EXTEND** Design a health check strategy for a service
   that takes 90 seconds to warm up its ML model on startup.
   How do you prevent premature liveness failures during
   startup without setting `initialDelaySeconds=90` globally?

---

### 🧠 Think About This Before We Continue

**Q1.** A service has `livenessProbe.failureThreshold=3`
and `periodSeconds=10`. The liveness probe checks the
database. At 9:00 AM, the database has a 35-second network
blip. Trace exactly: which seconds the probe fails, when
Kubernetes decides to restart the pod, and what the
user-visible impact is compared to if the liveness probe
only checked internal state.

**Q2.** You have a service that starts in 30 seconds on
a fast machine but takes 120 seconds on the production
JVM with heap initialisation. If you set
`initialDelaySeconds=30`, what happens to the pod on the
slow machine? Design a startup probe configuration that
handles variable startup times gracefully without an
artificial delay.

**Q3.** Your health check endpoint itself becomes a
performance bottleneck: it executes a `SELECT 1` query
for each probe call. With 500 pod instances and a 5-second
probe interval, you are generating 100 DB queries/second
from health checks alone. Design an optimised health
checking strategy that reduces DB overhead without
sacrificing accuracy of the health signal.