---
id: OBS-022
title: Health Check Patterns
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-001, OBS-005, OBS-009
used_by: OBS-031, OBS-039, OBS-042
related: OBS-025, OBS-015, OBS-026
tags:
  - observability
  - reliability
  - devops
  - intermediate
  - pattern
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/obs/health-check-patterns/
---

⚡ TL;DR - Health check patterns let infrastructure automatically
detect unhealthy instances and route traffic away before users
notice - separating "is it alive?" from "is it ready to serve?"

| #022            | Category: Observability & SRE                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | What Is Observability, SRE, Alerting Fundamentals          |                 |
| **Used by:**    | Golden Signals, Observability at Scale, SLO-Based Alerting |                 |
| **Related:**    | Incident Management Process, Prometheus, Runbooks          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine 20 instances of a payment service running behind a load
balancer. Instance 7 has a memory leak - it is still running,
its process is alive, but every request it handles either stalls
for 30 seconds or returns a 500. The load balancer has no way to
know. It keeps sending 5% of traffic to instance 7. Users see
random payment failures. Your on-call engineer gets paged at
3 AM. The failure is invisible until users complain.

**THE BREAKING POINT:**
Without health checks, infrastructure cannot distinguish a healthy
instance from a zombie process. Traffic continues to flow to broken
instances. The only detection mechanism is user complaints or error
rate spikes - which means real users absorbed the failure.

**THE INVENTION MOMENT:**
This is exactly why health check patterns were created - to give
infrastructure a reliable, automated way to ask each service
instance "are you able to handle traffic right now?" before sending
it real requests.

**EVOLUTION:**
Early load balancers used TCP port checks (is port 80 open?) which
only confirmed the process was running. Web frameworks introduced
HTTP `/health` endpoints in the early 2000s, allowing application-
level verification. Kubernetes formalized the three-probe model
(liveness, readiness, startup) around 2016-2018, separating restart
decisions from traffic routing decisions. Modern service meshes like
Istio extend health checks into outlier detection using real traffic
signals, not synthetic probes.

---

### 📘 Textbook Definition

A **health check pattern** is a mechanism through which a service
exposes its operational state to external infrastructure components
(load balancers, orchestrators, service meshes) so they can make
automated routing and restart decisions. The three canonical forms
are: liveness checks (should this instance be restarted?), readiness
checks (should this instance receive traffic?), and startup checks
(has this instance finished initializing?). A well-designed health
check returns a deterministic, fast, and truthful assessment of
service state without itself causing cascading failures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Health checks let your infrastructure ask each service "are you
OK?" before sending it real work.

**One analogy:**

> Think of a restaurant with a kitchen staff indicator light.
> Green means the kitchen can take orders. Red means they are
> slammed or something broke - the host stops seating new tables
> at that station. The restaurant keeps running; that station
> gets time to recover.

**One insight:**
The most important thing to understand is that liveness and
readiness are intentionally separate signals. Liveness means
"restart me" - readiness means "stop sending me traffic." Mixing
them is the single most common and dangerous health check mistake
in production, because it turns a traffic routing decision into
a destructive restart decision.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A service can be running but unable to handle traffic (it is
   alive but not ready - e.g., warming up a cache, loading config)
2. A service can be alive but fundamentally broken and requiring
   restart (e.g., goroutine/thread leak, corrupt internal state)
3. Infrastructure cannot observe application state directly - it
   needs an explicit protocol for the application to self-report
4. Health checks must be cheaper to execute than real requests,
   and must not themselves cause the failure they are detecting

**DERIVED DESIGN:**
Given these invariants, any correct health check system needs at
least two distinct probes:

- One that answers "should I be restarted?" (liveness)
- One that answers "should I receive traffic?" (readiness)

These must be implemented as separate endpoints because the
correct response to each failure is different: liveness failure
triggers a restart (destructive), readiness failure triggers
traffic removal (non-destructive). Combining them into one endpoint
means every readiness failure causes an unnecessary restart.

**THE TRADE-OFFS:**

**Gain:** Automatic fault isolation - broken instances removed from
rotation within seconds, before users experience significant impact.

**Cost:** Health check complexity must be managed carefully - a
health check that is too aggressive or too deep can itself cause
cascading failures.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any distributed system must solve the problem of
detecting partial failure - where some instances are broken but
the cluster is not. This requires a signal from the instance
about its own state, which is irreducibly complex.

**Accidental:** Three separate endpoint paths, separate
initialDelaySeconds tuning for each probe type, and the overhead
of Kubernetes probe configuration YAML - these are artifacts of
the current implementation ecosystem, not fundamental requirements.

---

### 🧪 Thought Experiment

**SETUP:**
You have a Spring Boot service with a database connection pool
of 10 connections. At peak load, a slow query holds all 10
connections for 45 seconds. You have one `/health` endpoint
that checks the database by running a test query.

**WHAT HAPPENS WITHOUT SEPARATE PROBES:**
The load balancer calls `/health`. The health check tries a test
query. All 10 connections are busy. The health check times out.
The load balancer marks the instance unhealthy. Kubernetes
reads "unhealthy from liveness probe" and restarts the pod.
On restart, the pod reconnects to the database - the slow query
is still running. The pool fills again. The pod restarts again.
You now have a restart loop under load. All instances follow the
same pattern. The cluster thrashes. The incident doubles.

**WHAT HAPPENS WITH SEPARATE PROBES:**
The readiness probe calls `/health/ready` which checks if the
connection pool has at least one available connection. Under load,
readiness fails. The pod is removed from the load balancer rotation

- no new traffic arrives. The existing connections drain. Within
  30 seconds, connections free up. Readiness passes. Traffic resumes.
  The pod never restarts. No incident escalation.

**THE INSIGHT:**
Health check design determines whether your system fails gracefully
or catastrophically. The same signal - "DB connection pool full" -
should mean "stop routing to me" not "kill and restart me."

---

### 🧠 Mental Model / Analogy

> Health checks are like a pilot's pre-flight checklist combined
> with an air traffic controller's runway clearance system.
> The pilot (service) self-reports readiness through the
> checklist (health endpoint). The tower (orchestrator) only
> grants takeoff clearance (traffic) when the checklist passes.
> If something fails mid-flight (liveness), the plane declares
> an emergency and returns to base (restart). If the plane is
> fine but the runway ahead is icy (dependency unavailable),
> it holds at the gate (readiness failure) without landing.

Element mapping:

- "Pilot self-reporting" → service exposing health endpoint
- "Pre-flight checklist" → readiness probe checks
- "Tower grants clearance" → load balancer routing decision
- "Emergency return to base" → liveness failure triggers restart
- "Holds at gate" → readiness failure removes from rotation
- "Runway ahead is icy" → downstream dependency unavailable

Where this analogy breaks down: planes are rarely restarted mid-
flight by an external controller - in software, liveness failures
trigger automatic restarts without human intervention, which makes
the consequence of misclassification much more immediate.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A health check is a simple question a computer system asks your
service: "Are you working?" The service answers yes or no.
Infrastructure uses that answer to decide whether to send you
more work or let you rest and recover.

**Level 2 - How to use it (junior developer):**
Expose two HTTP endpoints: `/health/live` returns 200 if the
process is running, `/health/ready` returns 200 only when the
service can handle requests. Configure Kubernetes liveness probe
to `/health/live` and readiness probe to `/health/ready`. Set
conservative failure thresholds (3 consecutive failures before
action) to avoid flapping on transient issues.

**Level 3 - How it works (mid-level engineer):**
The readiness probe should check critical dependencies: can you
reach the database? Is the cache warm? Have startup migrations
completed? The liveness probe should check only internal state:
is the application's event loop still responsive? Has an internal
deadlock occurred? The startup probe buys time for slow-starting
services - it disables liveness/readiness checks until the
startup probe passes, preventing premature restarts.

**Level 4 - Why it was designed this way (senior/staff):**
The three-probe model in Kubernetes was designed to handle a class
of failure that TCP-only checks could not detect: application-level
zombie processes. An earlier single-probe model caused widespread
production incidents because readiness failures (temporary, fixable)
triggered liveness actions (permanent, destructive). The split was
a deliberate decision to map different failure modes to different
remediation actions. The startup probe was added later to handle
the JVM warm-up problem specifically - Java services with slow
class loading were being killed before they could start.

**Level 5 - Mastery (distinguished engineer):**
At scale, health checks become a first-class part of your SLO
infrastructure. The readiness probe is your circuit breaker
signal - when 30% of pods go unready simultaneously, that is
a cascade signal, not individual pod failure. Your alerting
should treat "N% of instances unready" as an incident trigger.
Health check response time itself is a metric worth tracking -
a readiness probe that takes 500ms instead of 5ms is a leading
indicator of database connection pool saturation. Consider
health check aggregation: a `/health/summary` endpoint that
returns component-level status (DB: OK, cache: DEGRADED,
downstream: DOWN) gives on-call engineers instant triage data.

---

### ⚙️ How It Works (Mechanism)

**Step 1 - Request arrives at orchestrator/load balancer:**
At each probe interval (default 10s in Kubernetes), the
orchestrator makes an HTTP GET to the configured health endpoint.
This is a real HTTP request - the service must handle it within
timeoutSeconds (default 1s).

**Step 2 - Service evaluates state:**
The health endpoint handler runs synchronously. For liveness:
check internal state (thread pool alive, event loop responsive).
For readiness: check external dependencies (DB ping, cache ping,
downstream circuit breaker state).

**Step 3 - Response interpretation:**

```
HTTP 200-399 → healthy
HTTP 400-599 → unhealthy
Connection refused/timeout → unhealthy
```

**Step 4 - Threshold evaluation:**
A single failure does not trigger action. The orchestrator counts
consecutive failures against failureThreshold. Only after N
consecutive failures does it take action.

```
┌─────────────────────────────────────────────┐
│       KUBERNETES PROBE DECISION TREE        │
├─────────────────────────────────────────────┤
│ Liveness: N consecutive failures            │
│   → container.spec.restartPolicy applied   │
│   → pod restart (destructive)              │
├─────────────────────────────────────────────┤
│ Readiness: N consecutive failures           │
│   → pod removed from Endpoints object      │
│   → kube-proxy removes from iptables rules │
│   → no new traffic reaches this pod        │
├─────────────────────────────────────────────┤
│ Readiness: N consecutive successes          │
│   → pod re-added to Endpoints              │
│   → traffic resumes automatically          │
└─────────────────────────────────────────────┘
```

**Step 5 - Recovery:**
For readiness, recovery is automatic. Once the probe passes
successThreshold consecutive times, the instance re-enters
rotation. No manual intervention needed.

**DEEP HEALTH CHECK IMPLEMENTATION:**
A deep readiness check probes dependencies actively:

```
┌─────────────────────────────────────────────────┐
│           DEEP READINESS CHECK FLOW             │
├─────────────────────────────────────────────────┤
│ GET /health/ready                               │
│   ├── DB ping (SELECT 1) - timeout: 100ms      │
│   ├── Redis ping - timeout: 50ms               │
│   ├── Circuit breaker state check              │
│   └── Connection pool available? (> 0)         │
│                                                 │
│ ALL pass → 200 {"status":"UP"}                 │
│ ANY fail → 503 {"status":"DOWN",               │
│              "component":"postgres",            │
│              "detail":"connection timeout"}     │
└─────────────────────────────────────────────────┘
```

**PROBE TIMING INTERACTION:**

```
Pod starts
   │
   ├── startupProbe begins (if configured)
   │     checks every periodSeconds
   │     until successThreshold passes
   │     OR failureThreshold exceeded → restart
   │
   ├── startupProbe passes
   │     livenessProbe BEGINS
   │     readinessProbe BEGINS (simultaneously)
   │
   ├── readinessProbe fails
   │     pod removed from service endpoints
   │     no traffic → recovers → re-added
   │
   └── livenessProbe fails (3x consecutive)
         pod RESTARTED
         cycle begins again
```

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
Health endpoint handlers must be designed to be callable at any
time, including during high load. Avoid holding application-level
locks in health handlers. The handler itself should have its own
timeout budget independent of the main request handler's timeout.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Request → Load Balancer → Route to healthy pods only
                │
                ↓ every 10s per pod
         Health Probe sent
                │
         /health/ready  ← YOU ARE HERE
                │
         200 OK ──────────→ pod stays in rotation
         503    ──────────→ pod removed from endpoints
                              traffic drains to other pods
                              pod recovers
                              readiness passes
                              pod re-added
```

**FAILURE PATH:**

```
Pod memory leak builds →
  liveness probe times out (3 consecutive) →
    Kubernetes restarts pod →
      new pod starts →
        startup probe prevents early traffic →
          readiness probe validates →
            pod rejoins rotation
```

**WHAT CHANGES AT SCALE:**
At 100+ pods, health check traffic itself becomes a load source.
With 200 pods each probed every 10s, that is 20 requests/second
to each health endpoint just from probes - factor this into
rate limiting and connection pool sizing. Health check
aggregation at scale means a flapping health check on 5% of
pods may indicate a systemic issue (network partition, dependency
degradation) rather than individual pod failure.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
In a multi-instance deployment, readiness failure on one instance
concentrates load on remaining instances. If 2 of 3 instances go
unready due to a shared dependency timeout, the remaining instance
absorbs 3x load, potentially triggering its own readiness failure.
Design readiness thresholds to account for this concentration risk.

---

### 💻 Code Example

**Example 1 - BAD: Single /health endpoint for both purposes**

```java
// BAD: one endpoint doing double duty
@GetMapping("/health")
public ResponseEntity<String> health() {
    // checks DB - slow DB will cause RESTART
    // when it should only cause traffic removal
    try {
        jdbcTemplate.queryForObject(
            "SELECT 1", Integer.class);
        return ResponseEntity.ok("UP");
    } catch (Exception e) {
        // liveness check kills pod for DB issues!
        return ResponseEntity.status(503).body("DOWN");
    }
}
```

```yaml
# BAD: one probe does everything
livenessProbe:
  httpGet:
    path: /health # DB failure restarts pod!
    port: 8080
  failureThreshold: 3
```

**Example 2 - GOOD: Separate liveness and readiness**

```java
// GOOD: liveness - only internal state
@GetMapping("/health/live")
public ResponseEntity<Map<String, String>> liveness() {
    // Only check if JVM/app is responsive
    // No external calls - fast and safe
    return ResponseEntity.ok(
        Map.of("status", "UP", "pid",
            String.valueOf(
                ProcessHandle.current().pid()))
    );
}

// GOOD: readiness - external dependencies
@GetMapping("/health/ready")
public ResponseEntity<Map<String, Object>> readiness() {
    Map<String, Object> components = new LinkedHashMap<>();
    boolean allUp = true;

    // Check database
    try {
        jdbcTemplate.queryForObject(
            "SELECT 1", Integer.class);
        components.put("database", "UP");
    } catch (Exception e) {
        components.put("database",
            "DOWN: " + e.getMessage());
        allUp = false;
    }

    // Check cache - degraded but not failing
    try {
        redisTemplate.opsForValue().get("health-ping");
        components.put("cache", "UP");
    } catch (Exception e) {
        components.put("cache", "DEGRADED");
    }

    int status = allUp ? 200 : 503;
    return ResponseEntity.status(status)
        .body(Map.of(
            "status", allUp ? "UP" : "DOWN",
            "components", components));
}
```

**Example 3 - Kubernetes probe configuration**

```yaml
# GOOD: separate probes with correct semantics
spec:
  containers:
    - name: payment-service
      livenessProbe:
        httpGet:
          path: /health/live
          port: 8080
        initialDelaySeconds: 0
        periodSeconds: 10
        timeoutSeconds: 2
        failureThreshold: 5
        # 5 * 10s = 50s window before restart
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8080
        initialDelaySeconds: 0
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 3
        successThreshold: 2
        # 3 * 5s = 15s before traffic removal
        # 2 * 5s = 10s to re-enter rotation
      startupProbe:
        httpGet:
          path: /health/live
          port: 8080
        # Allow up to 30 * 10s = 300s to start
        failureThreshold: 30
        periodSeconds: 10
```

**Example 4 - Spring Boot Actuator health groups**

```yaml
# application.yml
management:
  endpoint:
    health:
      show-details: always
      group:
        liveness:
          include: livenessState
        readiness:
          include: readinessState, db, redis
  endpoints:
    web:
      exposure:
        include: health
```

```bash
# /actuator/health/readiness output
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "validationQuery": "isValid()"
      }
    },
    "redis": {"status": "UP"},
    "readinessState": {
      "status": "ACCEPTING_TRAFFIC"
    }
  }
}
```

**How to test / verify correctness:**
Write integration tests that call the health endpoint while
simulating dependency failures (use Testcontainers to stop the
DB container, then assert `/health/ready` returns 503 while
`/health/live` returns 200). Load test the health endpoint
itself to verify it completes within timeoutSeconds under load.

---

### ⚖️ Comparison Table

| Pattern                   | Scope           | Action on Failure | Recovery  |
| ------------------------- | --------------- | ----------------- | --------- |
| **Liveness probe**        | Internal state  | Pod restart       | Automatic |
| Readiness probe           | External deps   | Traffic removal   | Automatic |
| Startup probe             | Init completion | Pod restart       | Automatic |
| TCP port check            | Port open       | Traffic removal   | Automatic |
| Deep health (aggregated)  | All deps        | Traffic removal   | Automatic |
| Passive outlier detection | Real traffic    | Traffic removal   | Automatic |

**How to choose:**
Use liveness for "is the process fundamentally broken and needs
a restart?" - keep it fast and dependency-free. Use readiness for
"can I handle traffic right now?" - check all critical deps.
Add startup probes for any service that takes more than 30 seconds
to initialize to avoid premature liveness failures during boot.

**Decision Tree:**
Service takes >30s to start? → Add startup probe
Check depends on DB/cache? → Put in readiness only
Check is internal state only? → Liveness is appropriate
Need fine-grained component status? → Add /health/detail endpoint
100+ pods with high probe frequency? → Track health check p99 latency

---

### 🔁 Flow / Lifecycle

**READINESS PROBE LIFECYCLE:**

```
Pod Created
    │
    ↓
startupProbe active (if configured)
    │  probe every periodSeconds
    │  max failureThreshold * periodSeconds total
    │
    ├──FAIL (threshold exceeded)──→ Container Killed
    │                                  → Restarted
    └──PASS──→ livenessProbe + readinessProbe ACTIVATE
                    │
    ┌───────────────┘
    │
    ↓
readinessProbe checking
    │
    ├──FAIL (N consecutive)
    │    → Pod removed from Endpoints
    │    → No new traffic
    │    → Pod continues running (not killed)
    │    → Probe keeps checking
    │    → PASS (M consecutive)
    │    → Re-added to Endpoints
    │    → Traffic resumes
    │
    └──PASS continuously
         → Pod stays in rotation
         → Normal operation
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                             |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| Liveness and readiness can share the same endpoint     | They MUST be separate - they trigger different actions; sharing causes pod restarts for temporary dependency issues |
| A passing health check means the service is healthy    | It means the service thinks it is healthy - it cannot detect all failure modes (e.g., returning wrong data)         |
| Health checks should always be deep (check all deps)   | Liveness should NEVER check external deps - only readiness should                                                   |
| Short initialDelaySeconds is better for fast detection | Too-short delay causes healthy pods to be killed during normal startup; use startupProbe instead                    |
| One health check failure means the pod is broken       | Kubernetes requires consecutive failures (failureThreshold) precisely because single transient failures are normal  |
| A 200 response proves the service can handle load      | Health checks test basic responsiveness, not capacity - a service can pass health checks while being overloaded     |

---

### 🚨 Failure Modes & Diagnosis

**Cascading Readiness Failure**

**Symptom:**
All pods simultaneously show `0/1 Ready` in `kubectl get pods`.
Service is completely unavailable. Kubernetes does not restart
pods. Incident escalates because there are no healthy instances.

**Root Cause:**
All pods share the same dependency (DB, Redis, downstream service)
that just became unavailable. All readiness probes fail together.
All pods removed from load balancer simultaneously.

**Diagnostic Command:**

```bash
kubectl get endpoints <service-name>
# Expected during incident: no addresses listed

kubectl describe pod <pod-name> | grep -A5 "Readiness"
# Shows consecutive failure count

kubectl get events \
  --field-selector reason=Unhealthy \
  --sort-by='.lastTimestamp'
```

**Fix:**

```yaml
# BAD: readiness fails immediately on one failure
readinessProbe:
  failureThreshold: 1  # too aggressive

# GOOD: tolerate brief dependency hiccup
readinessProbe:
  failureThreshold: 3
  periodSeconds: 5
  # 15s window before traffic removal
```

**Prevention:**
Set failureThreshold >= 3 for readiness probes; implement
connection pool availability checks rather than direct DB pings
to tolerate transient connectivity blips.

---

**Liveness Restart Loop Under Load**

**Symptom:**
Pods are being restarted repeatedly during peak traffic.
`kubectl get pods` shows high `RESTARTS` count. Each restart
correlates with a traffic spike.

**Root Cause:**
A liveness probe that checks an external dependency (DB, cache)
fails during high load when the dependency is slow. Kubernetes
interprets this as "pod is dead" and restarts it - but the pod
was healthy, just waiting for a slow dependency.

**Diagnostic Command:**

```bash
kubectl get pods -w  # watch restart count increment

kubectl logs <pod> --previous  # logs before last restart

kubectl describe pod <pod> | grep "Liveness probe failed"
```

**Fix:**

```java
// BAD: liveness checks database
@GetMapping("/health/live")
public ResponseEntity<?> liveness() {
    jdbcTemplate.queryForObject(
        "SELECT 1", Integer.class);
    return ResponseEntity.ok().build();
}

// GOOD: liveness checks only internal state
@GetMapping("/health/live")
public ResponseEntity<?> liveness() {
    return ResponseEntity.ok(
        Map.of("status", "UP"));
}
```

**Prevention:**
Never include external I/O calls in liveness probes. Liveness
should complete in under 5ms with no network calls.

---

**Health Check Self-DDoS**

**Symptom:**
Health check endpoint latency is high (>100ms). Health checks
intermittently time out causing flapping readiness state. Each
health check creates a new DB connection.

**Root Cause:**
Health check implementation creates a new connection per probe
instead of reusing the existing pool, or runs an expensive query.

**Diagnostic Command:**

```bash
# Count health check requests vs normal requests
grep "GET /health" /var/log/nginx/access.log | \
  awk '{print $4}' | sort | uniq -c

# Check DB connections from health checks
psql -c "SELECT count(*) FROM pg_stat_activity
         WHERE application_name LIKE '%health%';"
```

**Fix:**

```java
// BAD: new connection per health check
@GetMapping("/health/ready")
public ResponseEntity<?> ready() {
    // Creates new connection on every probe!
    Connection conn = DriverManager.getConnection(url);
    conn.createStatement().execute("SELECT 1");
    conn.close();
    return ResponseEntity.ok().build();
}

// GOOD: use existing connection pool
@GetMapping("/health/ready")
public ResponseEntity<?> ready() {
    // Uses pool connection - fast, no extra load
    return jdbcTemplate.queryForObject(
        "SELECT 1", Integer.class) != null
        ? ResponseEntity.ok().build()
        : ResponseEntity.status(503).build();
}
```

**Prevention:**
Always reuse the application's existing connection pool for
health checks. Set a tight timeout (50-100ms) on health check
DB queries specifically.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - health checks are one input signal
  to the broader observability system
- `SRE` - health checks operationalize SRE reliability goals
- `Alerting Fundamentals` - health check failures feed alerting

**Builds On This (learn these next):**

- `Golden Signals` - readiness state is a signal alongside
  latency, errors, and saturation
- `Incident Management Process` - health check failures trigger
  the incident response process
- `SLO-Based Alerting Strategy` - multi-pod unreadiness is an
  SLO burn rate event, not just a pod event

**Alternatives / Comparisons:**

- `Prometheus - Metrics Collection` - active probing vs passive
  metric scraping; both needed for complete health visibility
- `Distributed Tracing Fundamentals` - tracing reveals WHY
  health checks are failing; health checks detect THAT they fail
- `Runbooks and Playbooks` - document the response to repeated
  health check failures that do not auto-recover

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Probes that report service operational   │
│              │ state to infrastructure for auto-routing │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Infrastructure cannot detect zombie procs│
│ SOLVES       │ or temporarily unavailable dependencies  │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Liveness = restart signal (destructive)  │
│              │ Readiness = traffic signal (safe) - NEVER│
│              │ combine them                             │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Any service behind a load balancer or in │
│              │ an orchestrated environment (Kubernetes) │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Liveness: never check external deps;     │
│              │ Readiness: never check non-critical deps │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Single /health endpoint used for both    │
│              │ liveness and readiness probes            │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Automatic recovery vs cascading isolation│
│              │ risk when shared deps fail simultaneously│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Route around failure, restart around    │
│              │ brokenness - but know the difference."   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Golden Signals → SLO-Based Alerting →    │
│              │ Incident Management Process              │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Liveness and readiness MUST be separate endpoints - liveness
   failure restarts, readiness failure only removes from rotation.
2. Never check external dependencies in liveness probes - only
   check internal application state.
3. A cascading readiness failure (all pods go unready together)
   is often worse than the dependency failure it detects; tune
   failureThreshold and add successThreshold >= 2.

**Interview one-liner:**
"Health checks give infrastructure a way to ask each service
instance 'can you handle traffic right now?' - the key
engineering decision is separating liveness from readiness:
liveness says restart me, readiness says stop sending traffic.
A slow DB query should never cause a pod restart - it should
cause traffic removal. I once saw a restart thrash across an
entire cluster because someone used one endpoint for both."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate signals that trigger irreversible actions (restart) from
signals that trigger reversible actions (traffic removal). Mixing
them amplifies failures instead of containing them - the same
principle governs circuit breakers, database replica failover,
and emergency response triage.

**Where else this pattern appears:**

- **Circuit breakers** - distinguish "service is down" (open
  circuit) from "service is slow" (half-open state) rather than
  treating all failures as permanent
- **Database replica lag detection** - separate "replica is
  lagging" (stop reads, reversible) from "replica is corrupted"
  (remove from pool permanently, irreversible)
- **Human triage in medicine** - "not breathing" (immediate
  intubation, irreversible intervention) vs "breathing but
  labored" (monitor and support, reversible response) are
  separate protocols mapped to failure severity

**Industry applications:**

- **E-commerce platforms** - readiness probes checking inventory
  service availability prevent checkout pages from loading when
  inventory cannot be verified, avoiding silent order failures
- **Financial services** - liveness probes with strict timeouts
  detect stuck transaction processing threads that would cause
  silent data corruption if allowed to continue

---

### 💡 The Surprising Truth

Most engineers think the point of health checks is to detect
failure - but their more important function is enabling safe
deployments. Because readiness probes prevent traffic from
reaching pods that have not yet warmed up, rolling deployments
become safe to automate. Without readiness probes, a Kubernetes
rolling update would send production traffic to a pod still
loading its 500MB JVM class cache, causing request timeouts
during every deployment. Health checks are the technical
foundation that makes zero-downtime continuous delivery possible
at scale - not primarily a failure detection mechanism.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. [EXPLAIN] Explain to a junior why using a single `/health`
   endpoint for both Kubernetes probes causes restart loops under
   load, and what specific failure scenario demonstrates this
2. [DEBUG] Given `kubectl get pods` showing high RESTARTS and
   previous pod logs showing "connection refused to postgres",
   identify whether this is a liveness or readiness
   misconfiguration and explain the exact fix
3. [DECIDE] Your service takes 90 seconds to warm up its ML model
   cache before it can serve predictions - decide which probes
   to configure with which thresholds, and explain why a startup
   probe is required here
4. [BUILD] Implement separate `/health/live` and `/health/ready`
   endpoints in a Spring Boot service where readiness checks DB
   connectivity and liveness checks only that the HTTP thread
   pool is responsive, with appropriate timeouts
5. [EXTEND] Apply the liveness/readiness separation principle to
   a Redis Sentinel setup - explain how "master unavailable"
   (readiness failure) vs "Sentinel process crashed" (liveness
   failure) should be configured as separate signals

---

### 🧠 Think About This Before We Continue

**Q1.** You have a service where readiness checks the database
connection pool. During a traffic spike, all connections are in
use but the service is processing requests successfully. The
readiness probe times out waiting for a pool connection. Your
entire cluster goes unready simultaneously. The traffic that
would have been served now returns 503 to users. At what point
did the health check system make things worse? What alternative
readiness check design would have prevented this?
\*Hint: Think about what "is the service ready for more traffic?"
actually means vs "is the service currently processing traffic?"

- these are genuinely different questions with different answers.\*

**Q2.** At 1,000 pods with readiness probes every 5 seconds, you
are generating 200 health check requests per second against your
database. Each pod runs one connection per health check query.
What concrete failure modes does this introduce at scale, and
how would you redesign the health check to eliminate them while
keeping the dependency verification meaningful?
_Hint: Consider the difference between verifying "can I connect?"
at probe time vs maintaining a background connection whose cached
health state is read by the endpoint handler._

**Q3.** Build a health check aggregation system for a service
with 5 downstream dependencies where 2 are critical (failure
makes the service unready) and 3 are non-critical (failure
degrades but does not remove from rotation). Design the endpoint
contract, the HTTP status codes returned, and the Kubernetes
readiness probe threshold. What does your on-call engineer see
when 1 critical and 2 non-critical deps are down simultaneously?
_Hint: Think about how Kubernetes interprets different HTTP status
codes and how you represent partial degradation in observability
tooling separately from the traffic routing decision._

---

### 🎯 Interview Deep-Dive

**Q1: We had a production incident where pods were restarting in
a loop during peak traffic - the RESTARTS count was climbing
every 10 minutes. The service appeared fine between restarts.
Walk me through how you would diagnose this.**
_Why they ask:_ Tests whether the candidate understands the
liveness probe restart trigger and can trace the failure path
from symptom to root cause without guessing.
_Strong answer includes:_

- First check `kubectl describe pod` for "Liveness probe failed"
  events with the exact error message (timeout? 503? refused?)
- Check if the liveness probe is hitting an external dependency
  that is slow during peak load
- Examine the probe configuration (timeoutSeconds) vs actual
  response time of the health endpoint under load
- The fix is either increasing timeoutSeconds, removing external
  deps from liveness probe, or moving the check to readiness only

**Q2: When would you configure a startup probe separately from
a liveness probe, and what happens if you skip it for a
JVM-based service with heavy class loading?**
_Why they ask:_ Tests understanding of the three-probe model and
the specific JVM startup problem that motivated startup probes.
_Strong answer includes:_

- Without startup probe, liveness probe activates immediately
  after container starts and begins counting failures
- JVM services may take 30-120s to be responsive during class
  loading; liveness will kill them before they can start
- Startup probe disables other probes until it passes, buying
  unlimited startup time (failureThreshold \* periodSeconds)
- Should set startup failureThreshold \* periodSeconds to cover
  worst-case startup with headroom (e.g. 300s for JVM services)

**Q3: You are deploying to 50 pods. Your readiness probe checks
the database. Your DBA reports seeing 50 new connections from
health checks. What is happening, and how do you fix it without
removing the database check?**
_Why they ask:_ Tests understanding of health check resource
impact at scale and pool-reusing vs connection-creating checks.
_Strong answer includes:_

- Health endpoint is creating a new connection per probe instead
  of reusing the existing connection pool
- At 50 pods \* every 5s = 10 connection create/destroy per second
- Fix: use the existing datasource in the health endpoint - let
  the pool manage connections
- Consider reducing probe frequency after initial ready state
  is confirmed, or use a background health refresh pattern

**Q4: Your service has two dependencies: an orders database
(critical) and a recommendation engine (non-critical). How do
you design the readiness probe so DB failure removes you from
rotation but recommendation engine failure does not? Show the
implementation.**
_Why they ask:_ Tests ability to design tiered health checks with
real code and the trade-off between strictness and availability.
_Strong answer includes:_

- Implement readiness endpoint that returns 503 ONLY if orders
  DB check fails; returns 200 even if recommendations fail
- Include component details in response body for observability
  even when returning 200 (degraded state visible in monitoring)
- Add a `/health/detail` endpoint showing all component states
  for dashboards without affecting Kubernetes routing decisions
- Alert on recommendation engine degradation via metrics
  separately from the readiness probe decision

**Q5: You notice your readiness probe success rate drops to 80%
for 30 seconds every hour at exactly the same time. No users
are complaining. What are the possible causes and how would
you investigate each?**
_Why they ask:_ Tests production intuition - distinguishing
benign periodic events from real problems, and diagnostic
methodology for intermittent health check failures.
_Strong answer includes:_

- Correlate timing with: scheduled jobs, cron tasks, GC pauses,
  rate limiting resets, certificate rotation, connection pool
  maintenance
- Check if readiness failures coincide with p99 latency spikes
  using DB activity snapshots at that timestamp
- Check JVM GC logs for full GC pauses exceeding probe
  timeoutSeconds at that exact interval
- Verify health check timeout budget vs actual dependency
  response time during the periodic load spike
