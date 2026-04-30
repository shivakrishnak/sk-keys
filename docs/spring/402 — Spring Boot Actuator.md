---
layout: default
title: "Spring Boot Actuator"
parent: "Spring & Spring Boot"
nav_order: 134
permalink: /spring/spring-boot-actuator/
number: "134"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "Auto-Configuration, Spring MVC, Spring Boot, Micrometer"
used_by: "Kubernetes health probes, Prometheus scraping, Tracing, Admin UI"
tags: #java, #spring, #springboot, #intermediate, #observability, #devops
---

# 134 — Spring Boot Actuator

`#java` `#spring` `#springboot` `#intermediate` `#observability` `#devops`

⚡ TL;DR — A Spring Boot library that exposes production-ready HTTP and JMX endpoints for health checks, metrics, environment inspection, thread dumps, and application info.

| #134 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Auto-Configuration, Spring MVC, Spring Boot, Micrometer | |
| **Used by:** | Kubernetes health probes, Prometheus scraping, Tracing, Admin UI | |

---

### 📘 Textbook Definition

**Spring Boot Actuator** is a sub-project that adds production-ready management endpoints to a Spring Boot application. It provides built-in endpoints exposed over HTTP (`/actuator/*`) or JMX including: `health` (readiness/liveness for Kubernetes), `metrics` (Micrometer-backed instrumentation), `info` (application metadata), `env` (bound configuration properties), `loggers` (runtime log-level changes), `threaddump`, `heapdump`, `beans`, `mappings`, and `conditions`. Security and exposure are controlled via `management.endpoints.web.exposure.include` and Spring Security integration. Actuator auto-configures itself when `spring-boot-starter-actuator` is on the classpath.

---

### 🟢 Simple Definition (Easy)

Actuator is a set of built-in "peek inside the app" endpoints. You get `/actuator/health` (is the app working?), `/actuator/metrics` (how fast is it?), `/actuator/loggers` (change log levels live), and more — all without writing any code.

---

### 🔵 Simple Definition (Elaborated)

Running an application in production means you need to ask it "are you healthy?", "how much memory are you using?", "which configuration values are active?", and "can you handle traffic right now?" Actuator answers all of these over HTTP. Kubernetes uses `/actuator/health/liveness` and `/actuator/health/readiness` to decide whether to route traffic to a pod. Prometheus scrapes `/actuator/prometheus` for metrics. Developers use `/actuator/loggers/com.example.payment=DEBUG` to enable debug logging at runtime without a deployment. All of this ships out of the box with `spring-boot-starter-actuator`.

---

### 🔩 First Principles Explanation

**The observability gap without Actuator:**

```
Without Actuator:

  Kubernetes liveness probe:
    curl /health → 404 (not implemented)
    → K8s doesn't know if app is alive
    → Keeps sending traffic to broken pod

  Metrics:
    Custom: manually expose /metrics endpoint
    → 20 different implementations across 20 services
    → Inconsistent metric names, different formats
    → Grafana dashboards break when service changes

  Debug:
    Enable logging for one service in prod:
    → Requires restart → 30s downtime
    → Changes lose all in-flight state

  Config audit:
    "What value does my-service use for timeout?"
    → Must shell into container, read env vars
    → Error-prone, time consuming
```

**The two pillars: health and metrics:**

```
┌─────────────────────────────────────────────────────┐
│  HEALTH PROBES (Kubernetes integration)             │
│                                                     │
│  /actuator/health/liveness                          │
│  → is the JVM alive? (not deadlocked/OOM)           │
│  → K8s restarts pod if this fails                   │
│                                                     │
│  /actuator/health/readiness                         │
│  → is the app ready to serve traffic?               │
│  → K8s removes pod from load balancer if DOWN       │
│  → Composite: DB + cache + downstream deps          │
│                                                     │
│  METRICS (Micrometer → Prometheus/Datadog/etc.)     │
│  /actuator/prometheus → Prometheus text format      │
│  /actuator/metrics/jvm.heap.used → JSON             │
│  /actuator/metrics/http.server.requests → latency   │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITH Actuator:**

```
→ Zero-code Kubernetes health probes:
  livenessProbe: GET /actuator/health/liveness
  readinessProbe: GET /actuator/health/readiness

→ Prometheus scraping: add spring-boot-starter-actuator
  + micrometer-registry-prometheus → metrics exposed

→ Live log level changes (zero downtime):
  POST /actuator/loggers/com.example.order
  {"configuredLevel": "DEBUG"}

→ Audit current config: GET /actuator/env
  (shows every property source, value, origin)

→ Thread dump as-needed (production debugging)
  GET /actuator/threaddump → stack traces
  GET /actuator/heapdump → .hprof file

→ Beans/mappings introspection for troubleshooting
  GET /actuator/beans → full bean list
  GET /actuator/mappings → all HTTP routes
```

---

### 🧠 Mental Model / Analogy

> Actuator is like the **cockpit instrument panel** of a plane. Pilots (engineers) need live data on altitude (memory), fuel level (connection pool), engine health (liveness), landing gear status (readiness). Without the panel, pilots fly blind. Actuator exposes all these gauges. Ground control (Kubernetes, Prometheus, Grafana) can read the panel remotely and take action — reroute traffic, restart engines, alert crew.

"Cockpit instruments" = Actuator endpoints
"Altitude gauge" = JVM memory metrics
"Engine health indicator" = liveness probe
"Landing gear status" = readiness probe
"Ground control reading the panel" = Kubernetes + Prometheus
"Adjusting dials remotely" = POST /actuator/loggers

---

### ⚙️ How It Works (Mechanism)

**Configuration and security:**

```yaml
management:
  endpoints:
    web:
      exposure:
        # Expose only these endpoints (security!)
        include: health, info, metrics, prometheus, loggers
        # NEVER expose: env, beans, heapdump in production
        # without authentication — they leak secrets!
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true  # liveness + readiness sub-paths
    info:
      enabled: true
  # Separate port for management (restrict firewall rules)
  server:
    port: 8081
```

**Health indicator composition:**

```java
// Actuator aggregates all HealthIndicators:
// Built-in: DB, Disk Space, Redis, Kafka, RabbitMQ

// Custom health indicator:
@Component
public class PaymentGatewayHealthIndicator
    implements HealthIndicator {

  private final StripeClient stripe;

  @Override
  public Health health() {
    try {
      boolean connected = stripe.ping();
      return connected
          ? Health.up()
              .withDetail("latency", "12ms")
              .build()
          : Health.down()
              .withDetail("error", "timeout")
              .build();
    } catch (Exception e) {
      return Health.down(e).build();
    }
  }
}
// Visible at: GET /actuator/health
// → {"status":"UP","components":{"paymentGateway":{"status":"UP"},...}}
```

**Kubernetes probe configuration:**

```yaml
# k8s deployment.yaml
spec:
  containers:
  - name: order-service
    livenessProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 3
```

---

### 🔄 How It Connects (Mini-Map)

```
spring-boot-starter-actuator on classpath
        ↓
  Auto-Configuration (133) registers ActuatorEndpoints
        ↓
  SPRING BOOT ACTUATOR (134)  ← you are here
  Endpoints: /actuator/{id}
        ↓
  Health: HealthIndicator aggregation
  Metrics: Micrometer MeterRegistry → backends
  Loggers: LoggingSystem integration
  Env: PropertySources inspection
        ↓
  Consumed by:
  Kubernetes: liveness + readiness probes
  Prometheus: /actuator/prometheus scraping
  Grafana: dashboards from Prometheus metrics
  Spring Boot Admin: UI over Actuator APIs
```

---

### 💻 Code Example

**Example 1 — Metrics with Micrometer (Prometheus export):**

```java
// Add dependencies:
// spring-boot-starter-actuator
// micrometer-registry-prometheus

@Service
public class OrderService {
  private final Counter orderCounter;
  private final Timer orderTimer;

  public OrderService(MeterRegistry registry) {
    this.orderCounter = Counter.builder("orders.placed")
        .tag("region", "eu-west")
        .description("Total orders placed")
        .register(registry);
    this.orderTimer = Timer.builder("orders.processing.time")
        .register(registry);
  }

  @Transactional
  public Order place(OrderRequest req) {
    return orderTimer.recordCallable(() -> {
      Order order = orderRepo.save(Order.from(req));
      orderCounter.increment();
      return order;
    });
  }
}
// Prometheus scrapes at /actuator/prometheus:
// orders_placed_total{region="eu-west"} 1247.0
// orders_processing_time_seconds_sum 3.47
```

**Example 2 — Dynamic log level change:**

```bash
# Enable DEBUG for a package without restart:
curl -X POST http://app:8080/actuator/loggers/com.example.payment \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel": "DEBUG"}'

# Check current level:
curl http://app:8080/actuator/loggers/com.example.payment
# {"configuredLevel":"DEBUG","effectiveLevel":"DEBUG"}

# Reset to default (null = inherit from parent):
curl -X POST http://app:8080/actuator/loggers/com.example.payment \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel": null}'
```

**Example 3 — Custom Info contributor:**

```java
@Component
public class BuildInfoContributor
    implements InfoContributor {

  @Override
  public void contribute(Info.Builder builder) {
    builder.withDetail("build", Map.of(
        "version",   "2.3.1",
        "commit",    System.getenv("GIT_COMMIT"),
        "timestamp", Instant.now().toString(),
        "team",      "platform-engineering"
    ));
  }
}
// GET /actuator/info →
// {"build":{"version":"2.3.1","commit":"a4b3c2d1",...}}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All Actuator endpoints are exposed by default | Spring Boot 2.x+ exposes only `health` and `info` by default. All others must be explicitly included via `management.endpoints.web.exposure.include` |
| /actuator/health returning UP means the app works correctly | Health only checks configured HealthIndicators (DB, disk, custom). A logically broken application (wrong business logic) may still return UP |
| Actuator has no security by default | Endpoints are secured by Spring Security if it's on the classpath. Without Security, ALL exposed endpoints are publicly reachable — a major risk if env/beans/heapdump are exposed |
| Liveness and readiness probe on the same path is fine | They serve different purposes: liveness = JVM alive (restart on fail), readiness = can serve traffic (remove from LB on fail). They must be separate paths with different conditions |

---

### 🔥 Pitfalls in Production

**1. Exposing env or beans without authentication**

```yaml
# DANGEROUS: exposes all environment variables,
# including secrets, passwords, API keys!
management:
  endpoints:
    web:
      exposure:
        include: "*"  # NEVER in production without auth!

# GOOD: minimal exposure + management port + network policy
management:
  server:
    port: 8081  # Only accessible from internal network
  endpoints:
    web:
      exposure:
        include: health, info, prometheus, loggers
  endpoint:
    health:
      show-details: when-authorized
```

**2. Slow HealthIndicator blocking all health checks**

```java
// BAD: HealthIndicator calls external service synchronously
@Component
class ExternalApiHealthIndicator implements HealthIndicator {
  @Override
  public Health health() {
    // Times out after 30s → delays K8s health check
    return externalApi.ping() ? Health.up().build()
                               : Health.down().build();
  }
}
// K8s probe times out → marks pod NotReady → traffic drops!

// GOOD: async health check with timeout
@Override
public Health health() {
  try {
    boolean up = externalApi.ping()
        .get(2, TimeUnit.SECONDS); // 2s timeout max
    return up ? Health.up().build() : Health.down().build();
  } catch (TimeoutException e) {
    return Health.unknown()
        .withDetail("reason", "timeout").build();
  }
}
```

---

### 🔗 Related Keywords

- `Auto-Configuration` — Actuator is auto-configured from `spring-boot-starter-actuator`
- `Micrometer` — the metrics facade powering `/actuator/metrics` and `/actuator/prometheus`
- `Kubernetes` — primary consumer of liveness and readiness health probes
- `Prometheus` — scrapes `/actuator/prometheus` for time-series metric data
- `Spring Boot Admin` — UI that aggregates Actuator data from multiple Spring Boot applications
- `HealthIndicator` — the interface for contributing custom checks to `/actuator/health`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Production-ready HTTP endpoints for       │
│              │ health, metrics, env, logs, threads       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always add actuator to production apps;   │
│              │ configure probes for Kubernetes           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never expose env/beans/heapdump without   │
│              │ authentication — they leak credentials    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Actuator is the cockpit instrument panel │
│              │  — read all gauges without touching code."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring Boot Startup Lifecycle (135) →     │
│              │ Micrometer → Kubernetes health probes     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kubernetes uses liveness and readiness probes to manage pod lifecycle. A common misconfiguration is wiring an external dependency (like a downstream microservice) into the liveness probe. Explain why this is dangerous — what failure cascade occurs when the downstream service is down: pod restarts, cache clearing, warm-up time, thundering herd — and explain why the readiness probe is the correct place for external dependency checks while liveness should only reflect JVM-internal state.

**Q2.** Spring Boot Actuator's `/actuator/health` endpoint aggregates `HealthIndicator` results and returns a composite status. The status aggregation algorithm uses `StatusAggregator` with a default priority order: `DOWN > OUT_OF_SERVICE > UP > UNKNOWN`. Describe the race condition scenario where a `@Transactional` health check method attempts to query the database within a `HealthIndicator`, the connection pool is exhausted at that moment, and the health check blocks for `connectionTimeout` (30s) — how does this interact with Kubernetes' `failureThreshold × periodSeconds` timeout, and what configuration prevents this from cascading into a pod restart storm.

