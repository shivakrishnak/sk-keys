---
id: DPT-087
title: Health Check Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-065
used_by: []
related: DPT-086, DPT-089, DPT-044, DPT-065
tags:
  - pattern
  - observability
  - intermediate
  - health-check
  - readiness
  - kubernetes
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 87
permalink: /technical-mastery/design-patterns/health-check-pattern/
---

⚡ TL;DR - Health Check Pattern exposes endpoints that
report the runtime health of a service. Liveness checks
answer "is this instance alive?" Readiness checks answer
"is this instance ready to accept traffic?" Kubernetes,
load balancers, and service meshes use these endpoints
to route traffic only to healthy instances.

| #87 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-065 | |
| **Used by:** | N/A | |
| **Related:** | DPT-086, DPT-089, DPT-044, DPT-065 | |

---

### 🔥 The Problem This Solves

**THE SILENTLY DEGRADED INSTANCE:**
A Kubernetes Pod is running (process is alive, port is
open), but the application has entered a deadlock.
All threads are blocked. New requests time out or return
500. The Pod responds to TCP pings (alive at the network
level) but is completely broken at the application level.

Kubernetes, seeing only the process alive, does not
restart the Pod. The load balancer keeps routing traffic
to it. Users experience partial outages depending on
which Pod their request lands on.

**THE HEALTH CHECK SOLUTION:**
The application exposes `/health/liveness`. Kubernetes
probes this endpoint every 10 seconds. If the application
is deadlocked: the endpoint does not respond (or returns
500). Kubernetes detects the failure and RESTARTS the Pod.
The deadlocked instance is replaced with a fresh one.

---

### 📘 Textbook Definition

The **Health Check Pattern** (Chris Richardson, "Microservices Patterns")
provides runtime health information to infrastructure:

> "A service must report its health to enable infrastructure
> (load balancers, orchestrators, service meshes) to
> route requests only to healthy instances and to replace
> unhealthy instances automatically."

**Three check types:**

1. **Liveness check (`/health/liveness`):**
   "Is this instance alive and not deadlocked?"
   Failure response: Kubernetes restarts the container.
   Should check: application thread pool is responsive,
   no internal deadlock detected.
   Should NOT check: database connectivity (a DB outage
   should not cause a restart - it should cause NOT-READY).

2. **Readiness check (`/health/readiness`):**
   "Is this instance ready to accept traffic?"
   Failure response: Kubernetes removes from Service
   endpoints (no traffic routed here). Instance is NOT restarted.
   Should check: database connectivity, cache connectivity,
   required configuration loaded, warm-up complete.

3. **Startup check (`/health/startup`):**
   "Has this instance finished initializing?"
   Used for slow-starting containers to prevent premature
   liveness probe failures during startup. Once startup
   probe succeeds: liveness and readiness probes take over.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Expose `/liveness` (restart me if broken) and `/readiness`
(send me traffic only if I'm ready). Infrastructure
uses these to automate recovery.

**One analogy:**
> A traffic cop directing cars.
>
> Without health checks: cars are directed to all lanes
> equally, including lanes where the cars are stuck (deadlocked,
> unresponsive, starting up).
>
> With health checks: lanes announce their status.
> Liveness: "is the car moving?" (if not: tow it = restart).
> Readiness: "is the lane open for traffic?" (if not: redirect).
>
> The traffic cop (Kubernetes, load balancer) only routes
> to lanes that self-report as ready. Broken lanes are
> automatically replaced (liveness failure) or avoided
> (readiness failure). No manual intervention needed.

---

### 🔩 First Principles Explanation

**LIVENESS VS READINESS - CRITICAL DISTINCTION:**

**Get this wrong and you will cause outages:**

If the readiness check fails because the DATABASE is down:
- CORRECT: Kubernetes stops routing traffic to this instance
  (readiness failure = "not ready"). Instance stays alive.
  When DB recovers: instance becomes ready again.
- INCORRECT: Kubernetes restarts the instance (liveness failure).
  The restarted instance immediately fails liveness again
  (DB still down). Kubernetes enters a restart loop.
  CrashLoopBackOff. All instances restarted. Full outage.

**Rule**: Liveness checks: application-internal health only
(thread pool, self-contained logic). Readiness checks:
external dependency health (DB, cache, message broker).

**HEALTH CHECK RESPONSE:**
Standard format (Spring Boot Actuator, Kubernetes):
- HTTP 200: healthy
- HTTP 503 (or 500): unhealthy

JSON body (optional but useful):
```json
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    "cache": { "status": "UP" }
  }
}
```

**DEEP VS SHALLOW HEALTH CHECKS:**
- **Shallow**: can the process handle a request? (fast: 1ms)
  Returns 200 if the HTTP handler runs.
- **Deep**: can the service perform its core function?
  Check DB connection, check downstream dependencies.
  (slower: 10-100ms)

For readiness: use DEEP checks (verify actual dependencies).
For liveness: use SHALLOW checks (verify process is responsive).

---

### 🧪 Thought Experiment

**STARTUP WARMUP AND READINESS:**
A Java service with:
- 5-second JVM warmup
- DB connection pool initialization (3 seconds)
- 10,000 cached records preloaded from DB (7 seconds)

Total startup: ~15 seconds.

Without startup probe + readiness probe:
- Kubernetes starts the container.
- After 5 seconds (default): liveness probe fires.
- Application not ready: returns 503.
- Kubernetes: "liveness failed" → restart.
- Restart loop. Service never starts.

With startup probe configured for 30 seconds:
- Startup probe fires every 5 seconds for up to 30 seconds.
- At 15 seconds: application ready. Startup probe succeeds.
- Readiness probe takes over. Confirms DB and cache ready.
- Traffic routes in. Service available.

---

### 🧠 Mental Model / Analogy

> Health checks = self-reporting to the control plane.
>
> A hospital ward where patients self-report their status
> to the nurse station. "I'm fine" (liveness: still alive,
> responsive). "I'm ready to leave" (readiness: ready for
> discharge, no pending tests).
>
> The nurse station (Kubernetes) takes action based on
> reports: a patient not responding (liveness failure)
> gets medical intervention (restart). A patient not ready
> for discharge (readiness failure) stays off the discharge
> list (no traffic routed) but is not moved to ICU (not restarted).
>
> The key: patients (instances) KNOW their own state.
> External observation (TCP ping, process alive) cannot
> see internal state (deadlock, cache not loaded, DB disconnect).
> Only self-reporting provides the necessary information.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Basic liveness and readiness:**
Expose two endpoints. Liveness: returns 200 if the process
is handling requests. Readiness: returns 200 only if
DB connection and key dependencies are available.
Configure in Kubernetes: `livenessProbe` and `readinessProbe`.

**Level 2 - Spring Boot Actuator:**
Spring Boot provides health endpoints at `/actuator/health`,
`/actuator/health/liveness`, and `/actuator/health/readiness`
out of the box. Custom `HealthIndicator` beans add
component-level health information. `management.health.group`
configuration controls which indicators belong to which
group (liveness vs readiness).

**Level 3 - Health aggregation and observability:**
For services with many dependencies: aggregate health
status. If any CRITICAL dependency is unhealthy: readiness
= DOWN. Non-critical dependencies: may be degraded without
failing readiness. Expose detailed component status for
observability. Integrate health check failures with
alerting (PagerDuty, OpsGenie) for manual intervention
when automated recovery fails. Health check data feeds
into SLO dashboards.

---

### ⚙️ How It Works (Mechanism)

```
Kubernetes Health Check Flow
┌─────────────────────────────────────────────────────────┐
│ Pod startup:                                            │
│   startupProbe: /health/startup every 5s (max 30s)    │
│     - FAIL: pod not killed yet (within max)           │
│     - SUCCESS: switch to liveness + readiness probes  │
│                                                         │
│ Running:                                               │
│   livenessProbe: /health/liveness every 10s           │
│     - 2 failures: RESTART pod                         │
│   readinessProbe: /health/readiness every 5s          │
│     - 1 failure: remove from Service endpoints        │
│     - recovery: re-add to Service endpoints           │
│                                                         │
│ Traffic routing:                                       │
│   Service → [Pod-1: READY, Pod-2: NOT READY, Pod-3: READ│
│   Traffic only sent to Pod-1 and Pod-3               │
│   Pod-2 NOT READY: load balancer skips it            │
│   Pod-2 recovery: automatically re-added             │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Spring Boot Actuator health customization:**

```java
// Custom health indicator for a critical dependency:
@Component
class DatabaseHealthIndicator implements HealthIndicator {

    private final DataSource dataSource;

    DatabaseHealthIndicator(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            // Execute lightweight validation query:
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("SELECT 1");
            }
            return Health.up()
                .withDetail("database", "PostgreSQL")
                .withDetail("validationQuery", "SELECT 1")
                .build();
        } catch (SQLException e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

```yaml
# application.yml - configure health groups for K8s probes:
management:
  health:
    group:
      liveness:
        # Liveness = application-internal only.
        # DB outage should NOT cause restart.
        include: livenessState
      readiness:
        # Readiness = dependencies must be available.
        include: readinessState, db, redis, kafkaConsumer
  endpoint:
    health:
      show-details: always  # expose component details
  endpoints:
    web:
      exposure:
        include: health,info,metrics
```

```yaml
# Kubernetes deployment - probe configuration:
spec:
  containers:
    - name: order-service
      image: order-service:1.0.0

      startupProbe:
        httpGet:
          path: /actuator/health/liveness
          port: 8080
        initialDelaySeconds: 10  # wait 10s before first probe
        periodSeconds: 5          # probe every 5s
        failureThreshold: 6       # 6 failures × 5s = 30s max startup

      livenessProbe:
        httpGet:
          path: /actuator/health/liveness
          port: 8080
        periodSeconds: 10
        failureThreshold: 3       # 3 failures → restart

      readinessProbe:
        httpGet:
          path: /actuator/health/readiness
          port: 8080
        periodSeconds: 5
        failureThreshold: 2       # 2 failures → remove from service
```

---

### 🔥 Failure Scenarios

**WRONG: DB FAILURE IN LIVENESS CAUSES RESTART LOOP:**
```yaml
# BAD: liveness includes database check.
# DB goes down: all pods fail liveness.
# Kubernetes: restart all pods.
# Restarted pods: liveness still fails (DB still down).
# Kubernetes: restart again. CrashLoopBackOff.
# Full service outage for entire DB outage duration.

livenessProbe:
  httpGet:
    path: /actuator/health  # includes ALL checks including DB
```

```yaml
# GOOD: liveness only = internal state. DB = readiness only.
livenessProbe:
  httpGet:
    path: /actuator/health/liveness  # internal only
readinessProbe:
  httpGet:
    path: /actuator/health/readiness  # includes DB
# DB outage: pods not restarted, just not ready.
# DB recovery: pods automatically become ready again.
# No restart loop.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Health checks are optional in Kubernetes | Without health checks, Kubernetes routes traffic to pods immediately after container start (even before the app is ready) and never restarts deadlocked pods. Health checks are mandatory for production reliability |
| Liveness should check all dependencies | Liveness should check ONLY application-internal state. External dependency failures should fail readiness (stop traffic), not liveness (trigger restart). This is the most common and most damaging health check misconfiguration |
| Health check endpoints should have auth | Health check endpoints should be unauthenticated (no auth token required). Kubernetes probes do not support authentication. Use network policy or a separate management port to restrict access if needed |
| A 200 response means the service is truly healthy | Health check HTTP 200 means the health check endpoint ran. The check quality depends on what the check actually tests. A health check that only returns "UP" without testing real connectivity provides false assurance |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LIVENESS     │ "Is process alive?" Internal state only.│
│              │ Failure → RESTART. No DB check here!   │
├──────────────┼──────────────────────────────────────────┤
│ READINESS    │ "Ready for traffic?" Check dependencies.│
│              │ Failure → REMOVE from load balancer.   │
│              │ NO restart. Recovers when dep recovers.│
├──────────────┼──────────────────────────────────────────┤
│ STARTUP      │ Slow starters. Prevents premature fail. │
│              │ Once passes: liveness + readiness take  │
│              │ over.                                  │
├──────────────┼──────────────────────────────────────────┤
│ GOLDEN RULE  │ NEVER put DB in liveness check.        │
│              │ DB outage + liveness = CrashLoopBackOff│
├──────────────┼──────────────────────────────────────────┤
│ SPRING BOOT  │ /actuator/health/liveness              │
│              │ /actuator/health/readiness             │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-088: Leader Election Pattern       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Liveness vs Readiness: Liveness = "restart me if broken"
   (internal health only). Readiness = "send me traffic
   only if I'm ready" (external dependencies too). These
   are completely different actions. Confusing them causes
   CrashLoopBackOff under dependency outages.
2. Golden rule: NEVER include external dependency checks
   (DB, cache, downstream services) in the liveness probe.
   External failures → fail readiness (remove from traffic).
   Internal failures → fail liveness (restart). This
   distinction is the most common and most costly mistake.
3. Spring Boot Actuator provides `/actuator/health/liveness`
   and `/actuator/health/readiness` out of the box.
   Custom `HealthIndicator` beans add component checks.
   Configure which indicators belong to which group in
   `application.yml`.

