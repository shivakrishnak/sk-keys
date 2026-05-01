---
layout: default
title: "Health Check Patterns"
parent: "Microservices"
nav_order: 638
permalink: /microservices/health-check-patterns/
number: "638"
category: Microservices
difficulty: ★★☆
depends_on: "Service Registry, Service Discovery"
used_by: "Circuit Breaker (Microservices), Zero-Downtime Deployment, Graceful Shutdown (Microservices)"
tags: #intermediate, #microservices, #reliability, #observability, #distributed
---

# 638 — Health Check Patterns

`#intermediate` `#microservices` `#reliability` `#observability` `#distributed`

⚡ TL;DR — **Health Check Patterns** are mechanisms that expose a service's operational status so that load balancers, orchestrators, and service registries can make routing decisions. Three patterns: **Liveness** (is the process alive?), **Readiness** (is it ready to serve traffic?), and **Startup** probes. Kubernetes and Spring Boot Actuator implement all three.

| #638            | Category: Microservices                                                                      | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Service Registry, Service Discovery                                                          |                 |
| **Used by:**    | Circuit Breaker (Microservices), Zero-Downtime Deployment, Graceful Shutdown (Microservices) |                 |

---

### 📘 Textbook Definition

**Health Check Patterns** define standardised endpoints and protocols through which a service exposes its operational health, enabling external systems (load balancers, service registries, container orchestrators) to make routing and lifecycle decisions without application-level knowledge of internal service state. The core patterns are: **Liveness Check** — is the process alive and not in a deadlock/permanent failure state? If unhealthy: restart the container; **Readiness Check** — is the service ready to accept and process traffic? If unhealthy: remove from load balancing pool (do not restart); **Startup Check** — has a slow-starting service finished its initialisation phase? Prevents liveness checks from killing slow-starting containers. In Spring Boot, the Actuator provides `/actuator/health` with automatic component health indicators (database, messaging, cache). In Kubernetes, these map to `livenessProbe`, `readinessProbe`, and `startupProbe` in pod specs. The distinction between liveness and readiness is critical: a service that is alive but not ready (e.g., warming up cache) should not receive traffic but should NOT be restarted.

---

### 🟢 Simple Definition (Easy)

Health checks are "are you okay?" questions asked of a service by its infrastructure. There are two important flavours: (1) Liveness: "Are you alive?" → if not, restart the process; (2) Readiness: "Can you handle requests right now?" → if not, stop sending traffic to you (but don't restart). A service can be alive but not ready (e.g., loading data).

---

### 🔵 Simple Definition (Elaborated)

OrderService starts up. For the first 10 seconds, it is loading 50,000 product rules into an in-memory cache. During this time: Liveness = UP (process is running, no deadlock), Readiness = DOWN (not ready to serve requests yet). Kubernetes sees Readiness DOWN → removes OrderService from the Endpoints → no requests are routed to it during startup. After 10 seconds, cache loaded → Readiness = UP → Kubernetes adds it back to Endpoints → traffic flows. Now the database goes down. OrderService is still running (Liveness = UP), but its database health indicator → Readiness = DOWN → Kubernetes stops routing to it but does NOT restart the container (restarting won't fix the database).

---

### 🔩 First Principles Explanation

**Spring Boot Actuator health endpoints:**

```
GET /actuator/health
→ 200 OK (or 503 Service Unavailable)
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": { "database": "PostgreSQL", "validationQuery": "isValid()" }
    },
    "diskSpace": {
      "status": "UP",
      "details": { "total": 107374182400, "free": 80530137088, "threshold": 10485760 }
    },
    "redis": {
      "status": "UP",
      "details": { "version": "7.0.5" }
    }
  }
}

If ANY component is DOWN:
→ Overall status = DOWN
→ HTTP 503 returned

KUBERNETES INTEGRATION:
  livenessProbe: calls /actuator/health/liveness
  readinessProbe: calls /actuator/health/readiness
  → Spring Boot 2.3+: separate /liveness and /readiness groups
```

**Kubernetes probe types and responses:**

```yaml
# Kubernetes pod spec with all three probes:
containers:
  - name: order-service
    image: order-service:1.0

    startupProbe: # is the app done starting up?
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      failureThreshold: 30 # allow 30 × 10s = 5 minutes to start
      periodSeconds: 10
      # During startup: liveness/readiness probes DISABLED
      # After startupProbe succeeds: enable liveness + readiness probes

    livenessProbe: # is the app alive (not deadlocked)?
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 10
      failureThreshold: 3 # fail 3 consecutive times → RESTART container
      # Action on failure: kill container → kubelet restarts it

    readinessProbe: # is the app ready to serve traffic?
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 5
      failureThreshold: 3 # fail 3 consecutive times → remove from Endpoints
      # Action on failure: remove pod IP from Service Endpoints (no restart)
      # Action on recovery: add pod IP back to Endpoints
```

**Spring Boot 2.3+ Liveness vs Readiness separation:**

```java
// Spring Boot 2.3+ adds explicit Liveness and Readiness health groups:

// application.yml:
// management.endpoint.health.probes.enabled=true
// → Enables /actuator/health/liveness and /actuator/health/readiness

// LIVENESS group - only "application is alive" indicators:
// Does NOT include database, redis, messaging - those don't affect liveness
// Includes: LivenessStateHealthIndicator
//   - UP: normal operation
//   - BROKEN: non-recoverable error (e.g., required startup data corrupt)

// READINESS group - includes external dependencies:
// Includes: ReadinessStateHealthIndicator + db + redis + messaging
//   - UP: ready to accept traffic
//   - REFUSING_TRAFFIC: not ready (startup incomplete, dependency down)

// Manual control from application code:
@Autowired ApplicationContext context;
@Autowired ApplicationAvailability availability;

// Signal that service is not ready (e.g., detected cache warming in progress):
context.publishEvent(new AvailabilityChangeEvent<>(
    this, ReadinessState.REFUSING_TRAFFIC));
// Service removed from load balancer pool immediately

// Signal ready again:
context.publishEvent(new AvailabilityChangeEvent<>(
    this, ReadinessState.ACCEPTING_TRAFFIC));
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Health Checks:

What breaks without it:

1. Load balancer sends traffic to a starting-up instance → requests fail during cold start.
2. Container orchestrator cannot detect deadlocked processes → they run forever consuming resources.
3. Service Registry keeps dead instances → other services call them, get timeouts.
4. Rolling deployments send traffic to new instances before they are ready → errors during deployment.
5. Database failure: restarting the service won't fix the database → restart loops.

WITH Health Checks:
→ Starting instances are isolated from traffic until ready.
→ Deadlocked processes are restarted automatically.
→ Only healthy instances receive traffic.
→ Zero-downtime deployments: new instances join load balancing only when ready.
→ Database failure: service removed from load balancing, not restarted in a loop.

---

### 🧠 Mental Model / Analogy

> Liveness and Readiness checks are like two questions asked before letting a surgeon operate: (1) Liveness: "Is the surgeon conscious and responsive?" — if not, call an ambulance (restart). (2) Readiness: "Is the surgeon scrubbed, gowned, and ready to begin?" — if not, hold the patient in pre-op (don't send traffic), but don't fire the surgeon (no restart). A surgeon might be conscious but not ready (still scrubbing in). A surgeon who collapses mid-surgery needs an ambulance — regardless of readiness.

"Surgeon conscious" = process alive, not deadlocked → Liveness probe
"Scrubbed and gowned" = dependencies healthy, cache loaded → Readiness probe
"Call an ambulance" = container restart (kubelet) → Liveness failure
"Hold in pre-op" = remove from load balancer pool → Readiness failure

---

### ⚙️ How It Works (Mechanism)

**Custom health indicator for a circuit breaker:**

```java
@Component
class CircuitBreakerHealthIndicator implements HealthIndicator {

    @Autowired CircuitBreakerRegistry circuitBreakerRegistry;

    @Override
    public Health health() {
        CircuitBreaker cb = circuitBreakerRegistry.circuitBreaker("payment-service");
        CircuitBreaker.State state = cb.getState();

        if (state == CircuitBreaker.State.OPEN) {
            return Health.down()
                .withDetail("circuit-breaker", "OPEN")
                .withDetail("service", "payment-service")
                .withDetail("action", "refusing traffic - payment service unreachable")
                .build();
        }
        return Health.up()
            .withDetail("circuit-breaker", state.name())
            .build();
    }
}
// When circuit breaker OPENS:
// → /actuator/health/readiness → DOWN
// → Kubernetes readiness probe fails → pod removed from Service Endpoints
// → No new traffic routed to this instance while it cannot reach payment service
```

---

### 🔄 How It Connects (Mini-Map)

```
Service Registry
(deregisters/evicts unhealthy instances)
        │
        ▼
Health Check Patterns  ◄──── (you are here)
(liveness, readiness, startup probes)
        │
        ├── Circuit Breaker → triggers readiness failure when downstream is unhealthy
        ├── Zero-Downtime Deployment → readiness probe gates traffic to new instances
        ├── Graceful Shutdown → readiness goes DOWN before shutdown to drain traffic
        └── Observability → health check data feeds dashboards and alerting
```

---

### 💻 Code Example

**Graceful shutdown using readiness probe:**

```java
// During graceful shutdown:
// 1. SIGTERM received
// 2. Spring sets ReadinessState to REFUSING_TRAFFIC
//    → /actuator/health/readiness → DOWN
//    → Kubernetes removes pod from Endpoints (no new traffic)
// 3. In-flight requests complete (within graceful termination period)
// 4. Application context shuts down
// 5. Process exits

// application.yml configuration:
// server.shutdown=graceful
// spring.lifecycle.timeout-per-shutdown-phase=30s  ← wait 30s for in-flight requests
// management.endpoint.health.probes.enabled=true

// Kubernetes terminationGracePeriodSeconds: 60
// (must be > spring.lifecycle.timeout-per-shutdown-phase + probe polling interval)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                 | Reality                                                                                                                                                                                                                                                 |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Liveness and Readiness probes are just the same endpoint with different names | They must be separate and check different things. Liveness should ONLY check internal state (no external dependency checks) — adding DB checks to liveness causes restart loops when the database is temporarily unavailable                            |
| Health checks eliminate the need for circuit breakers                         | Health probes operate on a polling interval (seconds). Circuit breakers operate on real-time call outcomes (milliseconds). An instance can be healthy per last probe check but experiencing a surge of errors. Both are needed                          |
| A 200 OK from the health endpoint means the service is fully operational      | The HTTP status is binary (UP/DOWN). A service may be operating in degraded mode (some features unavailable) with status UP. Rich health detail fields in the response body provide granularity but most infrastructure only reads the HTTP status code |
| StartupProbe is only needed for very slow JVM applications                    | Any service with a non-trivial startup sequence (loading ML models, database migrations, cache warming) benefits from startup probes. Without them, liveness probes fire before startup completes and kill the container in a restart loop              |

---

### 🔥 Pitfalls in Production

**Liveness probe includes external dependency → restart loop**

```
SCENARIO:
  livenessProbe calls /actuator/health (which includes database check)
  Database goes down for maintenance (5 minutes)
  → /actuator/health → DOWN
  → livenessProbe fails 3 times → Kubernetes KILLS the container
  → Container restarts → database still down → liveness fails again
  → Container restart loop: CrashLoopBackOff
  → Service completely unavailable for duration of DB maintenance
  → AND restart loop adds extra connection pressure when DB comes back

FIX:
  Split liveness and readiness probes:
  livenessProbe: /actuator/health/liveness   ← NO external deps
  readinessProbe: /actuator/health/readiness ← includes DB, cache, etc.

  management:
    health:
      livenessstate:
        enabled: true      # only LivenessStateHealthIndicator
      readinessstate:
        enabled: true      # LivenessState + db + redis + messaging

  During DB outage:
  → Readiness DOWN → pod removed from load balancing (no traffic)
  → Liveness UP  → pod stays alive (no restart)
  → When DB recovers: Readiness UP → pod re-added to load balancing
```

---

### 🔗 Related Keywords

- `Service Registry` — uses health check results to maintain accurate instance lists
- `Zero-Downtime Deployment` — readiness probe gates traffic to new deployment instances
- `Graceful Shutdown (Microservices)` — readiness probe transitions DOWN before shutdown
- `Circuit Breaker (Microservices)` — can drive readiness probe DOWN when downstream fails

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LIVENESS     │ Is process alive and not deadlocked?      │
│ PROBE        │ FAIL → restart container                  │
│              │ ONLY internal state checks               │
├──────────────┼───────────────────────────────────────────┤
│ READINESS    │ Is service ready to handle traffic?       │
│ PROBE        │ FAIL → remove from load balancer pool    │
│              │ Includes external dep checks (DB, cache) │
├──────────────┼───────────────────────────────────────────┤
│ STARTUP      │ Has service finished initialisation?      │
│ PROBE        │ Disables liveness during slow startup     │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ /actuator/health/liveness (2.3+)          │
│ ENDPOINTS    │ /actuator/health/readiness (2.3+)         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice has a readiness probe that checks database connectivity. During a rolling deployment of 10 pods, the new pod version connects to the database and the readiness probe passes. However, the new version has a bug that causes 30% of requests to fail. The readiness probe returns UP, so Kubernetes routes traffic to the new pod. How would you design a more sophisticated readiness check that detects error rates (not just connectivity)? What is the risk of over-engineering readiness probes (making them too sensitive)?

**Q2.** Kubernetes `terminationGracePeriodSeconds` and Spring Boot's `server.shutdown=graceful` must be coordinated. Describe the exact shutdown sequence for a pod receiving SIGTERM: (a) how does the readiness probe transition to REFUSING_TRAFFIC; (b) what is the race condition between Kubernetes removing the pod from Endpoints vs the pod still being sent requests by existing connections in the load balancer; (c) why is adding a `preStop: sleep 5` hook in the pod spec often recommended as a workaround?
