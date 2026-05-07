---
layout: default
title: "Health Check Patterns"
parent: "Microservices"
nav_order: 18
permalink: /microservices/health-check-patterns/
number: "MSV-018"
category: Microservices
difficulty: ★★☆
depends_on: Service Registry, Service Discovery, HTTP & APIs
used_by: Service Discovery, Circuit Breaker, Kubernetes
related: Liveness Probe, Readiness Probe, Circuit Breaker
tags:
  - microservices
  - observability
  - distributed
  - intermediate
  - pattern
---

# MSV-018 — Health Check Patterns

⚡ TL;DR — Health check patterns define how services report their current operational state, enabling registries, orchestrators, and load balancers to route traffic only to fully functional instances.

| #638 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Service Registry, Service Discovery, HTTP & APIs | |
| **Used by:** | Service Discovery, Circuit Breaker, Kubernetes | |
| **Related:** | Liveness Probe, Readiness Probe, Circuit Breaker | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A payment service pod is running and responding to health checks with HTTP 200. But 3 minutes ago its connection pool to the database was exhausted — every actual payment attempt fails with "could not acquire connection." The load balancer routes calls to this pod because it is "healthy." Every customer hitting this instance gets an error. The pod is alive but useless.

**THE BREAKING POINT:**
A process that is alive is not the same as a process that is ready to serve. Without rich health checks that verify actual dependencies — database, cache, message broker — infrastructure tools cannot distinguish "alive but broken" from "alive and functional."

**THE INVENTION MOMENT:**
This is exactly why structured health check patterns were developed — to provide infrastructure with accurate, actionable signals about each service instance's true ability to handle requests.

---

### 📘 Textbook Definition

**Health Check Patterns** define mechanisms by which a service exposes its current operational state to external observers (service registries, orchestrators, load balancers). The three primary patterns are: (1) **Liveness** — is the process alive and not deadlocked? (2) **Readiness** — is the process ready to accept and successfully handle requests? (3) **Startup** — has the process completed its initialization? Each pattern serves a different consumer: liveness drives restart decisions; readiness drives traffic routing; startup protects slow-starting services from premature traffic.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Health checks are services saying "I'm alive," "I'm ready," or "I'm still starting up" — each signal means something different to the infrastructure.

**One analogy:**
> A restaurant has three states: "we're open" (liveness — the building exists), "we're seating customers" (readiness — kitchen is running and tables are available), and "we're still setting up" (startup — not ready yet, come back in 10 minutes). A health check system is the sign on the door that shows which state the restaurant is currently in.

**One insight:**
The most common health check mistake is returning 200 for liveness and readiness from the same endpoint without checking dependencies. This produces a pod that "looks healthy" but fails every real request — the worst kind of failure because it is invisible to routing decisions.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A running process is alive (liveness) but may not be functional (readiness).
2. Readiness requires checking ALL dependencies that affect the service's ability to handle requests.
3. Liveness and readiness require different responses to failure: liveness failure → restart; readiness failure → remove from routing.

**DERIVED DESIGN:**
Given Invariant 3, conflating liveness and readiness into one endpoint is dangerous. If the readiness check fails and Kubernetes interprets it as a liveness failure, it restarts the pod. But the pod may be temporarily unready (database overloaded) — a restart makes things worse, creating a pod restart cascade.

**Health check types:**

| Check Type | Question | Failure Action | Checks |
|---|---|---|---|
| Liveness | Is the process stuck/deadlocked? | Restart pod | Process thread, critical loop |
| Readiness | Can this pod serve requests now? | Remove from traffic | DB, cache, downstream services |
| Startup | Has initialization completed? | Block liveness/readiness | Migration, warmup, cache fill |

**THE TRADE-OFFS:**
**Gain:** Infrastructure can automatically route traffic to healthy instances and restart truly broken ones.
**Cost:** Health check overhead (called every 5–30s per pod), risk of false positives causing unnecessary restarts, dependency checks can cascade failures (one slow DB makes all pods unready simultaneously).

---

### 🧪 Thought Experiment

**SETUP:**
A service has one health endpoint `/health` returning 200. Both liveness and readiness probes point to it. The database becomes temporarily overloaded.

**WITHOUT SEPARATE PROBES:**
DB is slow → readiness check fails → Kubernetes reads this as liveness failure (same endpoint!) → restarts pod → pod starts, hits DB during startup → DB still overloaded → startup fails → pod restarts again → pod restart loop begins → all pods restarting simultaneously → total service outage

**WITH SEPARATE PROBES:**
DB is slow → readiness check fails → Kubernetes removes pod from Service Endpoints (traffic stops routing to it) → pod is NOT restarted (liveness check passes because process is alive) → DB recovers → readiness check passes again → pod added back to Endpoints → traffic resumes — zero restarts, 30-second traffic pause per pod

**THE INSIGHT:**
The distinction between liveness and readiness prevents a temporary downstream problem from cascading into pod restart storms. Readiness says "pause traffic to me." Liveness says "I'm fundamentally broken — restart me."

---

### 🧠 Mental Model / Analogy

> Think of a surgeon's status. Liveness: "Is the surgeon alive and not unconscious?" Readiness: "Is the surgeon scrubbed in, gowned, and standing at the operating table ready to cut?" Startup: "Is the surgeon still in the changing room getting ready?" Each status drives a different action: an unconscious surgeon (liveness failure) needs an ambulance. A surgeon who isn't ready yet (readiness failure) just needs the patient to wait.

- "Surgeon alive" → process running, no deadlock
- "Surgeon ready to operate" → all dependencies connected, warm cache loaded
- "Surgeon in changing room" → startup phase (slow app initialization)
- "Patient waits" → pod removed from load balancer routing

Where this analogy breaks down: surgeons transition through these states once. Services move back and forth between ready and not-ready dynamically — a readiness failure during operation (DB spike) is temporary and expected.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Health checks are a service's way of telling the system whether it is working properly. The system uses these signals to decide: send traffic here, don't send traffic here, or restart this service.

**Level 2 — How to use it (junior developer):**
Spring Boot Actuator exposes `/actuator/health` automatically. Configure `management.health.db.enabled=true` to include database connectivity. In Kubernetes, point `livenessProbe` to a lightweight endpoint (just HTTP 200 if the process is up), point `readinessProbe` to the full health endpoint that checks DB and dependencies.

**Level 3 — How it works (mid-level engineer):**
Kubernetes polls each probe independently on a configurable interval. Liveness failure after `failureThreshold` consecutive checks → `kubelet` kills and restarts the container. Readiness failure → `kubelet` removes the pod IP from the Service's Endpoints slice → kube-proxy removes it from routing rules → no new traffic reaches the pod. Startup probe: Kubernetes won't run liveness or readiness until startup succeeds, preventing restart loops on slow-starting apps.

**Level 4 — Why it was designed this way (senior/staff):**
Kubernetes adopted three separate probe types after observing failure patterns from simpler systems: Spring Actuator `UP/DOWN` was too coarse — a single `DOWN` triggered the wrong response depending on context. The three-probe design reflects operational reality: a service can be fundamentally alive (process running), temporarily unavailable (dependency down), or still initializing — three completely different conditions requiring three completely different responses. The Spring Boot 2.3+ actuator health groups (`liveness` and `readiness`) map directly to these Kubernetes concepts. The `startup` probe was added in Kubernetes 1.16 specifically to support JVM services that take 30–60 seconds to start but should not be killed by liveness probes during that window.

---

### ⚙️ How It Works (Mechanism)

**Kubernetes probe configuration:**

```yaml
spec:
  containers:
  - name: payments-service
    image: payments:1.0.0
    startupProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      failureThreshold: 30    # 30 × 10s = 5 min startup window
      periodSeconds: 10
    livenessProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      initialDelaySeconds: 0  # startup probe guards this
      periodSeconds: 10
      failureThreshold: 3     # restart after 3 failures
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      periodSeconds: 10
      failureThreshold: 3     # remove from routing
      successThreshold: 1     # back to routing after 1 success
```

**Spring Boot Actuator health configuration:**

```yaml
# application.yml
management:
  endpoint:
    health:
      show-details: always
      group:
        liveness:          # maps to /actuator/health/liveness
          include: livenessState  # only checks process state
        readiness:         # maps to /actuator/health/readiness
          include: >
            readinessState,
            db,            # database connectivity
            redis,         # cache connectivity
            rabbit         # message broker connectivity
```

**Custom health indicator:**

```java
@Component
public class PaymentGatewayHealthIndicator
    implements HealthIndicator {

    private final PaymentGatewayClient gatewayClient;

    @Override
    public Health health() {
        try {
            // Check if payment gateway is reachable
            GatewayStatus status = gatewayClient.ping();
            if (status == GatewayStatus.OK) {
                return Health.up()
                    .withDetail("gateway", "reachable")
                    .build();
            }
            return Health.down()
                .withDetail("gateway", "degraded")
                .build();
        } catch (Exception e) {
            return Health.down()
                .withException(e)
                .build();
        }
    }
}
```

**Health response structure:**

```json
// GET /actuator/health → overall status
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": { "database": "PostgreSQL", "validationQuery": "isValid()" }
    },
    "redis": { "status": "UP" },
    "paymentGateway": { "status": "UP", "details": { "gateway": "reachable" } }
  }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
Service starts → Startup probe polled → Startup probe passes → Liveness + Readiness probes begin → All green → Pod added to Service Endpoints ← YOU ARE HERE → Traffic routed to pod

**READINESS FAILURE PATH:**
DB pool exhausted → Readiness probe returns `DOWN` → 3 consecutive failures → kube-proxy removes pod from routing → Traffic shifts to remaining healthy pods → DB pool recovers → Readiness probe returns `UP` → Pod added back to routing

**LIVENESS FAILURE PATH:**
Deadlock in thread pool → Process hangs → Liveness probe times out → 3 consecutive timeouts → kubelet kills and restarts container → Pod starts fresh, joins Endpoints → Traffic resumes

**WHAT CHANGES AT SCALE:**
At 100 pods, health check traffic becomes significant — 100 pods × 2 endpoints × every 10s = 20 probe requests/second to the service. Health endpoints must be cheap (no DB calls in liveness probe) and fast. At 1000 pods, a cascading dependency failure (central DB down) makes all pods simultaneously not-ready — the entire service vanishes from routing. Design readiness probes for dependency degradation: if DB is slow but not down, stay ready with reduced capacity.

---

### 💻 Code Example

**Example 1 — BAD: Single health endpoint for both liveness and readiness:**

```yaml
# BAD: same endpoint used for both — conflates two different signals
livenessProbe:
  httpGet:
    path: /health   # same path!
    port: 8080
readinessProbe:
  httpGet:
    path: /health   # same path!
    port: 8080
# Problem: DB unavailability → readiness fails →
# interpreted as liveness fail → restart cascade
```

**Example 2 — GOOD: Separate liveness and readiness:**

```yaml
# GOOD: separate concerns
livenessProbe:
  httpGet:
    path: /actuator/health/liveness  # checks only process state
    port: 8080
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /actuator/health/readiness # checks DB, cache, etc.
    port: 8080
  periodSeconds: 10
  failureThreshold: 3
```

**Example 3 — Graceful degradation in readiness:**

```java
@Component
public class CacheHealthIndicator implements HealthIndicator {

    private final RedisTemplate<?,?> redis;

    @Override
    public Health health() {
        try {
            redis.opsForValue().get("health-check");
            return Health.up().build();
        } catch (RedisConnectionFailureException e) {
            // Cache down: service can still function without cache
            // DO NOT fail readiness — service is degraded, not broken
            return Health.up()
                .withDetail("cache", "degraded — operating without cache")
                .withDetail("impact", "increased DB load")
                .build();
        }
    }
}
// Cache failure → service still routes traffic (slower)
// DB failure → service fails readiness (cannot process requests)
```

---

### ⚖️ Comparison Table

| Probe Type | Checks | Failure Effect | Frequency |
|---|---|---|---|
| **Liveness** | Process alive, no deadlock | Pod restart | Every 10–30s |
| **Readiness** | All dependencies reachable | Remove from routing | Every 5–10s |
| **Startup** | Initialization complete | Block liveness/readiness | Every 5–10s during startup |
| External health check (AWS ELB) | HTTP 200 response | Remove from target group | Every 30s |

How to choose: always implement all three probes in Kubernetes environments; configure liveness conservatively (high failure threshold, long period) to avoid unnecessary restarts; tune readiness aggressively (fast failure, fast recovery) for smooth traffic management.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A single `/health` endpoint is sufficient | You need separate liveness and readiness for correct Kubernetes behaviour; a combined endpoint maps the wrong response to the wrong action |
| Liveness probe should check downstream dependencies | Liveness should check ONLY the process itself. Dependency failures should fail readiness (stop routing), not liveness (trigger restart) |
| A DOWN health status always means the service is unusable | Some dependencies can be degraded without making the service completely unavailable. Design health indicators with levels: UP, DEGRADED (still routing), DOWN (stop routing) |
| Health checks add significant overhead | A simple in-process check returning a cached status takes microseconds. Health probe calls every 10 seconds are negligible overhead |
| Startup probes are optional | In JVM services with 30+ second startup times, startup probes are essential — without them, liveness probes trigger restart loops before the app finishes starting |

---

### 🚨 Failure Modes & Diagnosis

**1. Pod Restart Loop from Misconfigured Liveness Probe**

**Symptom:** Pods in `CrashLoopBackOff` state. Each successful start is followed by a restart within 2 minutes. Memory usage and CPU look normal.

**Root Cause:** Liveness probe points to a readiness-style endpoint that checks the database. DB connection pool saturation during high traffic causes the liveness probe to fail, triggering unnecessary restarts.

**Diagnostic:**
```bash
# Check restart count and reason
kubectl get pods -l app=payments
kubectl describe pod payments-xxx | grep -A20 "Last State"
# Look for: Reason: OOMKilled vs health probe timeout
kubectl logs payments-xxx --previous  # logs from crashed container
```

**Fix:** Change liveness probe to a truly lightweight endpoint that only confirms the JVM is alive (no DB calls). Move DB checks to the readiness probe.

**Prevention:** Liveness probe endpoints must complete in <1 second and never call external dependencies.

**2. Cascading Readiness Failure**

**Symptom:** A spike in DB response time causes all pods simultaneously to fail readiness probes → all pods removed from routing → all traffic fails → no pods can serve requests.

**Root Cause:** Readiness probe failures are all-or-nothing. When all instances fail simultaneously, there are zero healthy instances.

**Diagnostic:**
```bash
# Check endpoint count (should not reach zero)
watch kubectl get endpoints payments-service
# Zero endpoints = total service unavailability

# Check why probes are failing
kubectl describe pod payments-xxx | grep -A10 "Readiness:"
```

**Fix:** Implement Pod Disruption Budgets to prevent Kubernetes from removing all pods simultaneously. Use circuit breakers and connection pool health caps (rather than probe failures) to degrade gracefully under DB load.

**Prevention:**
```yaml
# PodDisruptionBudget: ensure minimum availability
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payments-pdb
spec:
  minAvailable: 2   # keep at least 2 pods in routing at all times
  selector:
    matchLabels:
      app: payments
```

**3. Health Endpoint Never Updated**

**Symptom:** Health endpoint returns 200/UP but requests consistently fail with 500. Health check is green, real traffic is red.

**Root Cause:** Health endpoint returns hardcoded 200 without actually checking any dependencies.

**Diagnostic:**
```bash
# Check health endpoint response vs application error rate
curl http://payments:8080/actuator/health
# Shows UP

# But application error rate is high
kubectl logs payments-xxx | grep "ERROR\|Exception" | \
  tail -20
```

**Fix:** Implement real dependency checks in the readiness health indicator. Every dependency that can cause request failures must have a health indicator.

**Prevention:** Test health checks against actual failures in staging. Disable a dependency deliberately and confirm the health endpoint reports DOWN.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Registry` — health checks feed the registry with instance status, determining which instances are included in discovery results
- `Service Discovery` — health check status directly controls which instances are eligible for traffic routing

**Builds On This (learn these next):**
- `Circuit Breaker (Microservices)` — complements health checks by tracking call success rates at the client level, providing faster failure detection than probe polling
- `Kubernetes` — the primary consumer of Kubernetes liveness, readiness, and startup probes in modern deployments
- `Observability & SRE` — health check metrics (available instances, probe failure counts) are key SRE signals

**Alternatives / Comparisons:**
- `Circuit Breaker (Microservices)` — client-side health detection that complements server-side health checks; circuit breaker detects failures faster than probe polling intervals

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Three probe types that let infrastructure │
│              │ know when to restart, route, or wait for  │
│              │ a service instance                        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Running ≠ ready. Infrastructure needs     │
│ SOLVES       │ accurate signals — not just "is the       │
│              │ process alive?"                           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Liveness failure → restart.               │
│              │ Readiness failure → stop routing.         │
│              │ Conflating them causes restart storms     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every microservice running in    │
│              │ Kubernetes needs all three probe types    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Do not include slow external dependency   │
│              │ checks in liveness probes                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Accurate health signals vs complexity of  │
│              │ maintaining accurate health indicators    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Alive means the light is on. Ready means │
│              │  the shop is actually open."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Service Registry →      │
│              │ Observability & SRE                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your payments service has 10 pods. The readiness probe checks DB connectivity. During a scheduled DB maintenance window, DB becomes unavailable for 2 minutes. All 10 pods fail their readiness check simultaneously — all are removed from routing. New requests pile up at the load balancer with no healthy backend. Design a resilient health check strategy that maintains partial service availability during planned and unplanned dependency outages, including how to handle the case where the DB is slow (high latency) but not completely unreachable.

**Q2.** A team discovers their service has a subtle memory leak — after 6 hours of production traffic, heap usage reaches 90% and GC pauses cause P99 to spike from 50ms to 2 seconds. The service does not crash, so liveness probes never fail. Design a liveness probe strategy that detects this degraded state and triggers a pod restart before it affects users, while avoiding false positives that would cause unnecessary restarts under normal high-traffic conditions.

