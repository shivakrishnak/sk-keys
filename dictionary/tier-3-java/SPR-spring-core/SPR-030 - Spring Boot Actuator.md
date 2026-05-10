---
version: 1
layout: default
title: "Spring Boot Actuator"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /spring/spring-boot-actuator/
id: SPR-019
category: Spring Core
difficulty: ★★☆
depends_on: Spring Boot, Auto-Configuration, HTTP & APIs
used_by: Observability, Prometheus, Grafana, Kubernetes Health Probes
related: Micrometer, Health Checks, Metrics
tags:
  - spring
  - springboot
  - observability
  - api
  - intermediate
---

# SPR-030 - Spring Boot Actuator

⚡ TL;DR - Spring Boot Actuator exposes production-ready HTTP endpoints for health checks, metrics, and diagnostics, letting Kubernetes, Prometheus, and ops teams see inside your running service without code changes.

| #402            | Category: Spring Core                                        | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Spring Boot, Auto-Configuration, HTTP & APIs                 |                 |
| **Used by:**    | Observability, Prometheus, Grafana, Kubernetes Health Probes |                 |
| **Related:**    | Micrometer, Health Checks, Metrics                           |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A microservice is running in Kubernetes. Is it healthy? Is the database connection alive? Is memory usage spiking? How many requests have been served in the last minute? To answer these questions without Actuator, you'd need to: write a custom `/health` endpoint, instrument metrics manually, add a JVM stats collector, and expose a /info endpoint - every service, every team, slightly differently, all at risk of leaking sensitive internals.

**THE BREAKING POINT:**
Kubernetes readiness and liveness probes need `/health` endpoints to decide whether to route traffic. Prometheus needs metrics endpoints in the right format. If each team implements these differently, the monitoring stack breaks when a team changes their custom implementation.

**THE INVENTION MOMENT:**
"This is exactly why Spring Boot Actuator was created."

---

### 📘 Textbook Definition

**Spring Boot Actuator** is a Spring Boot sub-module that automatically exposes HTTP (and JMX) endpoints for monitoring and managing a running application. Key built-in endpoints include `/actuator/health` (liveness/readiness state), `/actuator/metrics` (application and JVM metrics via Micrometer), `/actuator/info` (app metadata), `/actuator/env` (environment properties), `/actuator/beans` (all registered Spring beans), and `/actuator/loggers` (runtime log level changes). Endpoints are auto-configured based on classpath presence and enabled via `management.endpoints.web.exposure.include` in `application.properties`. Metrics are backed by Micrometer, which can export to Prometheus, Datadog, CloudWatch, and other backends.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Actuator adds a built-in dashboard of `/actuator/*` endpoints that tell you everything happening inside your running Spring Boot app.

**One analogy:**

> Actuator is like a car's OBD-II diagnostic port. The car manufacturer builds it in by default. You plug in a diagnostic tool (Prometheus, Grafana, Kubernetes) and instantly see engine RPM, oil pressure, error codes - without opening the hood yourself.

**One insight:**
The power is not in the endpoints themselves - it's in standardization. When every Spring Boot service uses Actuator, every monitoring tool, Kubernetes probe, and on-call playbook works identically across all services.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Actuator endpoints are auto-configured when `spring-boot-starter-actuator` is on the classpath.
2. Only `/actuator/health` and `/actuator/info` are exposed over HTTP by default; all others must be explicitly enabled for security.
3. Health indicators are composable - individual components (DB, Redis, disk space) each contribute to an overall UP/DOWN status.

**DERIVED DESIGN:**
The security-first default (only health and info exposed) exists because endpoints like `/actuator/env` can reveal passwords in environment variables and `/actuator/beans` reveals the full application structure. The opt-in model for other endpoints ensures developers consciously choose to expose sensitive data.

Health endpoint composition uses the `HealthIndicator` pattern: each subsystem implements `HealthIndicator.health()` and returns `Health.up()` or `Health.down(details)`. The `HealthAggregator` combines all indicators into a single composite status - if any one is DOWN, the overall status is DOWN. This drives Kubernetes readiness probes: a DOWN status removes the pod from load balancer rotation.

**THE TRADE-OFFS:**
**Gain:** Production-ready observability with zero code; standardized metrics; Kubernetes-native health probes; runtime diagnostics.
**Cost:** Security risk if endpoints are over-exposed (env, beans, dump endpoints reveal sensitive data); slight startup overhead from metrics instrumentation; metrics cardinality explosion if custom tags are misused.

---

### 🧪 Thought Experiment

**SETUP:**
Your Spring Boot service is deployed in Kubernetes. The DB connection pool is exhausted. All 10 HikariCP connections are in use and new requests are waiting. What does the Kubernetes operator see, and what happens next?

**TRACE THE FLOW:**

1. HikariCP is waiting > `connection-timeout` (3s) to acquire a connection.
2. The `DataSourceHealthIndicator` calls `connection.isValid()` on a test connection.
3. If acquiring that test connection also times out, it returns `Health.down("DataSource not available")`.
4. `GET /actuator/health` returns `{"status":"DOWN", "components": {"db": {"status":"DOWN"}}}` with HTTP 503.
5. Kubernetes readiness probe polls `/actuator/health/readiness` and gets HTTP 503.
6. Kubernetes marks the pod as NOT READY and removes it from the service's endpoint slice.
7. Load balancer stops routing new traffic to the struggling pod.
8. Pod is not restarted (liveness probe still passes - the JVM is alive).

**THE INSIGHT:**
The readiness/liveness split is critical: readiness says "I can serve traffic right now"; liveness says "I'm not stuck in an infinite loop." Kubernetes handles each differently. Actuator's split health groups map directly to this distinction.

---

### 🧠 Mental Model / Analogy

> Think of Spring Boot Actuator as the instrument cluster on a modern aircraft. Pilots (ops teams, Kubernetes) need standardized gauges - altitude, airspeed, fuel - without having to build custom meters for each aircraft type. The instrument cluster is built in by the manufacturer, standardized, and exposed through a common interface. You read what you need; the rest is accessible when diagnosing a problem.

- "Built-in instrument cluster" → Actuator auto-configured by adding one dependency
- "Altitude/airspeed gauges" → `/health`, `/metrics` endpoints
- "Reading what you need" → selective endpoint exposure via `management.endpoints.web.exposure.include`
- "Detailed diagnostics during incident" → `/actuator/env`, `/actuator/threaddump`, `/actuator/heapdump`

Where this analogy breaks down: unlike a physical gauge, Actuator endpoints can reveal sensitive configuration details if not properly secured - the aircraft analogy assumes pilots are trusted; Actuator endpoints face the internet.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Add one dependency to your Spring Boot project and your service automatically has a `/health` URL that tools like Kubernetes can poll to see if your app is healthy, plus a `/metrics` URL for performance data.

**Level 2 - How to use it (junior developer):**
Add `spring-boot-starter-actuator` to your `pom.xml`. The `/actuator/health` endpoint is immediately available. To expose more endpoints, add to `application.properties`: `management.endpoints.web.exposure.include=health,metrics,info,loggers`. To change log level at runtime: `POST /actuator/loggers/com.mypackage` with `{"configuredLevel": "DEBUG"}`. Spring Security, if present, secures all `/actuator/**` endpoints.

**Level 3 - How it works (mid-level engineer):**
Actuator endpoints are registered as `@Endpoint`-annotated beans auto-configured by `EndpointAutoConfiguration`. Each endpoint has a unique ID and exposes `@ReadOperation` (HTTP GET), `@WriteOperation` (POST/PUT), and `@DeleteOperation` methods. The `WebEndpointMediaTypes` determines serialization format. Health endpoints use `CompositeHealthContributor` which aggregates `HealthIndicator` beans (auto-configured for each detected component: `DataSourceHealthIndicator`, `DiskSpaceHealthIndicator`, etc.). Metrics are powered by `MeterRegistry` (Micrometer) - each component auto-registers meters (counters, timers, gauges) when instrumented.

**Level 4 - Why it was designed this way (senior/staff):**
The decision to make health/liveness separate from health/readiness (Spring Boot 2.3+) was driven by Kubernetes adoption: liveness probe failure causes pod restart (expensive), readiness probe failure only removes from load balancer (cheap and reversible). Before this split, teams used a single `/health` endpoint for both, leading to restart storms when a backing service was temporarily unavailable. The Micrometer abstraction layer was added because different teams used Prometheus, Datadog, and CloudWatch - writing metrics once and letting Micrometer export to any backend prevents vendor lock-in in the metrics layer.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ /actuator/health EVALUATION FLOW                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  GET /actuator/health                                   │
│    │                                                    │
│    ↓                                                    │
│  HealthEndpoint.health()                                │
│    │                                                    │
│    ├── DataSourceHealthIndicator                        │
│    │   └── SELECT 1 via HikariCP → UP / DOWN           │
│    │                                                    │
│    ├── DiskSpaceHealthIndicator                        │
│    │   └── free space > threshold? → UP / DOWN         │
│    │                                                    │
│    ├── PingHealthIndicator → always UP (JVM alive)      │
│    │                                                    │
│    └── [custom HealthIndicators you define]             │
│                                                         │
│  HealthAggregator: any DOWN → overall DOWN              │
│                                                         │
│  Response: {"status":"UP"} HTTP 200                     │
│         OR {"status":"DOWN","components":{...}} HTTP 503│
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Essential configuration:**

```properties
# application.properties

# Expose specific endpoints (default: only health,info)
management.endpoints.web.exposure.include=health,metrics,info,loggers,env

# Show full health details (default: never - security risk)
# Only expose detail to authenticated users in production
management.endpoint.health.show-details=when_authorized

# Kubernetes probes: split liveness and readiness
management.endpoint.health.probes.enabled=true
# GET /actuator/health/liveness  → 200 or 503
# GET /actuator/health/readiness → 200 or 503

# Separate management port (isolate from app traffic)
management.server.port=8081
```

**Example 2 - Custom health indicator:**

```java
@Component
public class ExternalApiHealthIndicator
        implements HealthIndicator {

    private final ExternalApiClient client;

    public ExternalApiHealthIndicator(
            ExternalApiClient client) {
        this.client = client;
    }

    @Override
    public Health health() {
        try {
            // Lightweight ping to external dependency
            String status = client.ping();
            return Health.up()
                .withDetail("response", status)
                .withDetail("latencyMs", client.lastLatency())
                .build();
        } catch (Exception ex) {
            return Health.down()
                .withDetail("error", ex.getMessage())
                .build();
        }
    }
}
// Result in /actuator/health:
// "externalApi": {"status": "UP", "details": {...}}
```

**Example 3 - Custom metric with Micrometer:**

```java
@Service
public class OrderService {

    private final Counter orderCounter;
    private final Timer orderTimer;

    public OrderService(MeterRegistry registry) {
        // auto-injected MeterRegistry from Actuator
        this.orderCounter = Counter.builder("orders.created")
            .tag("region", "us-east")
            .description("Total orders created")
            .register(registry);

        this.orderTimer = Timer.builder("orders.processing.time")
            .tag("type", "standard")
            .register(registry);
    }

    public Order createOrder(OrderRequest req) {
        return orderTimer.record(() -> {
            Order order = processOrder(req);
            orderCounter.increment();
            return order;
        });
    }
}
// Exposed at: GET /actuator/metrics/orders.created
// Scraped by Prometheus: orders_created_total{region="us-east"}
```

---

### ⚖️ Comparison Table

| Endpoint               | HTTP Method | Default Exposed | Use Case                         |
| ---------------------- | ----------- | --------------- | -------------------------------- |
| `/actuator/health`     | GET         | ✅ Yes          | Kubernetes probes, load balancer |
| `/actuator/metrics`    | GET         | ❌ No           | Prometheus scrape, dashboards    |
| `/actuator/info`       | GET         | ✅ Yes          | App version, build metadata      |
| `/actuator/loggers`    | GET/POST    | ❌ No           | Runtime log level change         |
| `/actuator/env`        | GET         | ❌ No           | Inspect active properties        |
| `/actuator/beans`      | GET         | ❌ No           | Debug ApplicationContext         |
| `/actuator/threaddump` | GET         | ❌ No           | Diagnose thread issues           |
| `/actuator/heapdump`   | GET         | ❌ No           | Memory analysis                  |

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                          |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exposing all Actuator endpoints is safe on the internal network   | `/actuator/env` shows all properties including passwords; `/actuator/heapdump` dumps full heap memory. Always require authentication even internally.                            |
| `/actuator/health` returning UP means the app is fully functional | Health checks test what you've instrumented - an unhealthy microservice downstream can cause failures without affecting `/health` unless you've added a `HealthIndicator` for it |
| Actuator metrics ARE Prometheus metrics                           | Actuator metrics use Micrometer; to export to Prometheus you need `micrometer-registry-prometheus` dependency AND expose `/actuator/prometheus`                                  |
| Liveness and readiness probes should check the same things        | No - liveness = "is the JVM alive and not deadlocked"; readiness = "can I serve traffic right now (are deps available)". Combining them causes unnecessary pod restarts.         |
| Custom HealthIndicators run synchronously                         | Yes - health checks are synchronous by default; a slow database ping in a `HealthIndicator` delays `/health` response; use timeouts or async health checks for slow dependencies |

---

### 🚨 Failure Modes & Diagnosis

**1. Kubernetes Restart Loop from Liveness Probe**

**Symptom:** Pod is repeatedly restarted by Kubernetes; logs show app started successfully but pod is killed shortly after; liveness probe URL returns 503.

**Root Cause:** Liveness probe is pointed at `/actuator/health` which includes database health. When the DB is down, liveness returns DOWN → Kubernetes kills and restarts the pod → pod restart doesn't fix the DB → restart loop. Should be using `/actuator/health/liveness` (checks only JVM health).

**Diagnostic:**

```bash
# Check probe configuration
kubectl describe pod <pod-name> | grep -A5 "Liveness"

# Test probe endpoint directly
kubectl exec <pod-name> -- \
  wget -O- http://localhost:8080/actuator/health/liveness
```

**Fix:**

```yaml
# kubernetes deployment.yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness # NOT /actuator/health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /actuator/health/readiness # includes DB check
    port: 8080
  periodSeconds: 5
```

**Prevention:** Always separate liveness and readiness probe endpoints. Enable probe groups: `management.endpoint.health.probes.enabled=true`.

---

**2. Sensitive Data Exposed via `/actuator/env`**

**Symptom:** Security audit finds database passwords or API keys visible at `GET /actuator/env`.

**Root Cause:** `/actuator/env` was included in `management.endpoints.web.exposure.include=*` without security restriction.

**Diagnostic:**

```bash
curl http://myservice/actuator/env | \
  python -m json.tool | grep -i "password\|secret\|key"
```

**Fix:**

```properties
# NEVER expose env, beans, or heapdump publicly
management.endpoints.web.exposure.include=health,metrics,info

# If env is needed internally, secure with Spring Security
# and serve on a separate management port
management.server.port=8081
```

```java
// Secure management endpoints with Spring Security
@Configuration
public class ActuatorSecurityConfig
        extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.requestMatcher(
            EndpointRequest.toAnyEndpoint())
            .authorizeRequests()
            .anyRequest().hasRole("ACTUATOR_ADMIN")
            .and().httpBasic();
    }
}
```

**Prevention:** Never use `management.endpoints.web.exposure.include=*` in production. Explicitly list only the endpoints required by your monitoring stack.

---

**3. Metrics Cardinality Explosion**

**Symptom:** Prometheus memory usage grows unbounded; application slows down; Prometheus reports "too many time series"; `/actuator/metrics` response is enormous.

**Root Cause:** Custom metrics use high-cardinality tags (user IDs, order IDs, request URLs with path parameters).

**Diagnostic:**

```bash
# Check metric cardinality via Prometheus
curl http://prometheus/api/v1/label/__name__/values | \
  python -m json.tool | wc -l

# In application: check number of active meters
curl http://localhost:8080/actuator/metrics | \
  python -m json.tool | jq '.names | length'
```

**Fix:**

```java
// BAD: user ID as tag - cardinality = number of users
Counter.builder("orders.created")
    .tag("userId", userId) // millions of unique values!
    .register(registry);

// GOOD: use low-cardinality tags only
Counter.builder("orders.created")
    .tag("region", region)      // ~5 values
    .tag("orderType", orderType) // ~3 values
    .register(registry);
// Log user ID separately for tracing, not metrics
```

**Prevention:** Tags must be low-cardinality (< 100 distinct values). Never use IDs, URLs with path variables, or free-form strings as metric tags.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Spring Boot` - Actuator is a Spring Boot module; understand the boot context before the observability layer
- `Auto-Configuration` - Actuator endpoints are auto-configured; understanding conditions explains why some endpoints don't appear
- `HTTP & APIs` - Actuator exposes HTTP endpoints; understanding HTTP status codes (200/503) is prerequisite

**Builds On This (learn these next):**

- `Micrometer` - Actuator's metrics layer; enables export to Prometheus, Datadog, CloudWatch
- `Observability & SRE` - Actuator is the foundation for SRE practices (SLOs, error rates, saturation)
- `Kubernetes` - Actuator health endpoints are the bridge between Spring and Kubernetes pod lifecycle management

**Alternatives / Comparisons:**

- `Custom /health endpoint` - hand-written health checks; non-standardized; duplicates effort across services
- `Micrometer without Actuator` - possible but unusual; Actuator provides the HTTP exposition layer
- `Prometheus JMX Exporter` - for non-Actuator JVM apps; Actuator + Micrometer is preferred for Spring

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Auto-configured HTTP endpoints exposing   │
│              │ health, metrics, and diagnostics          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Every service needs health/metrics;       │
│ SOLVES       │ Actuator provides them for free           │
├──────────────┼───────────────────────────────────────────┤
│ KEY ENDPOINTS│ /health (K8s probes), /metrics (Prom),    │
│              │ /loggers (runtime debug), /env (inspect)  │
├──────────────┼───────────────────────────────────────────┤
│ SECURE IT    │ Only expose: health, metrics, info        │
│              │ Require auth for env, beans, heapdump     │
├──────────────┼───────────────────────────────────────────┤
│ K8s PATTERN  │ liveness → /health/liveness (JVM only)   │
│              │ readiness → /health/readiness (deps too)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Free observability vs. security risk if   │
│              │ sensitive endpoints over-exposed          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "It's the OBD-II port for your service -  │
│              │  plug in any monitoring tool instantly"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Micrometer → Prometheus → SRE/Observability│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE B - Scale) A payment service has 100 pods, each running Spring Boot Actuator. Every 5 seconds, Kubernetes probes `/actuator/health` on each pod - which triggers a `SELECT 1` on the shared PostgreSQL database (via `DataSourceHealthIndicator`). Calculate the total health-check queries per minute hitting the database. Is this a concern? What configuration change minimizes DB load from health probes while preserving readiness detection capability?

**Q2.** (TYPE C - Trade-off) A team wants to use `/actuator/env` in production to diagnose a configuration issue affecting only one pod in a 50-pod deployment. The security team says exposing `/actuator/env` is a violation of policy. What is the minimum-risk alternative approach that lets the engineer access the same information without enabling the env endpoint on any production pod?
