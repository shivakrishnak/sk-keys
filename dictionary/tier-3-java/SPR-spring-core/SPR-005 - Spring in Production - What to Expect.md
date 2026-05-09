---
id: SPR-005
title: Spring in Production - What to Expect
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★☆☆
depends_on: SPR-001, SPR-002, SPR-003
used_by:
related: SPR-044, SPR-045, SPR-046
tags:
  - spring
  - java
  - foundational
  - production
  - observability
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /spr/spring-in-production-what-to-expect/
---

# SPR-005 - Spring in Production - What to Expect

⚡ TL;DR - A Spring Boot app in production needs health checks, metrics, graceful shutdown, JVM tuning, and observability instrumentation before it is genuinely production-ready.

| Field          | Value                                                                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-001 - What Is Spring - History and Philosophy]], [[SPR-002 - The Spring Ecosystem Map]], [[SPR-003 - Why Spring Boot Changed Java Development]] |
| **Used by**    | -                                                                                                                                                     |
| **Related**    | [[SPR-044 - Auto-Configuration]], [[SPR-045 - Spring Boot Actuator]], [[SPR-046 - Spring Boot Startup Lifecycle]]                                     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A developer writes a Spring Boot application that works flawlessly on their laptop. They deploy it to a Kubernetes cluster and find: the pod is killed before it finishes starting, the load balancer sends traffic before the database connection pool is ready, out-of-memory errors appear under load, log output is unstructured and unsearchable, no alerts fire when the service degrades, and the application takes 30 seconds to shut down (losing in-flight requests). The gap between "runs locally" and "runs reliably in production" is enormous without deliberate preparation.

**THE BREAKING POINT:**

Microservices multiplied the number of services each team operated from 1 to 20+. Each service needed health checks, metrics, log aggregation, circuit breaking, and graceful lifecycle management. Teams discovered these requirements after deployment, producing a cascade of production incidents.

**THE INVENTION MOMENT:**

Spring Boot Actuator (included since Boot 1.0) provides production endpoints out of the box: `/actuator/health`, `/actuator/metrics`, `/actuator/info`. Spring Boot 2.3 added Kubernetes-specific `liveness` and `readiness` probes. Spring Boot 3.x integrated Micrometer Tracing (distributed tracing) natively. The framework now provides the production scaffolding; teams must activate and configure it deliberately.

**EVOLUTION:**

- **2014:** Spring Boot Actuator 1.0 - `/health`, `/metrics`, `/env`, `/info`
- **2018:** Spring Boot 2.0 - Micrometer metrics abstraction replaces Spring Boot Metrics
- **2020:** Spring Boot 2.3 - liveness/readiness probe separation; graceful shutdown; Docker layer ordering
- **2022:** Spring Boot 3.0 - Micrometer Tracing (replaces Sleuth), OTLP support, AOT + native
- **2024:** Spring Boot 3.2 - `RestClient` replaces `RestTemplate`; virtual thread support GA; improved native image observability

---

### 📘 Textbook Definition

**Spring in Production** refers to the set of non-functional concerns that must be addressed before a Spring Boot application can operate reliably in a cloud or containerised environment. These include: **health probes** (liveness, readiness), **metrics** (JVM, HTTP, custom), **distributed tracing**, **structured logging**, **graceful shutdown**, **JVM memory tuning**, **connection pool sizing**, and **security hardening** of management endpoints. Spring Boot Actuator provides the infrastructure; operators configure and monitor it.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A working Spring Boot app is not production-ready until it can report its health, emit metrics, shut down gracefully, and survive memory pressure.

> Shipping a Spring Boot app without production configuration is like shipping a car without a dashboard. It drives - until something goes wrong, and then you have no idea what.

**One insight:** Most production Spring incidents are not framework bugs - they are misconfigured timeouts, undersized connection pools, missing health checks, or silent out-of-memory conditions. The framework provides the observability tools; you must use them.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A production service must accurately report when it is alive (liveness) and ready for traffic (readiness)
2. All external resource connections (DB, caches, queues) are the primary failure surface
3. Graceful shutdown must drain in-flight requests before accepting SIGTERM
4. JVM heap sizing and GC strategy directly determine throughput and tail latency
5. All telemetry (logs, metrics, traces) must be structured and machine-readable

**DERIVED DESIGN:**

From invariant 1 → `HealthIndicator` beans contribute to `/actuator/health/liveness` and `/actuator/health/readiness` separately.
From invariant 2 → custom `HealthIndicator` beans for every external dependency (DataSource, Redis, RabbitMQ).
From invariant 3 → `server.shutdown=graceful` + `spring.lifecycle.timeout-per-shutdown-phase`.
From invariants 4+5 → `-Xmx` tuning + GC selection + Micrometer + structured JSON logging (Logback).

**THE TRADE-OFFS:**

**Gain:** Observable, resilient, cloud-native behaviour; early warning of degradation before user impact.

**Cost:** Additional configuration complexity; Actuator endpoints expose sensitive operational data if not secured; metrics collection adds ~5-10% CPU overhead.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Production services have complex health states. Expressing those states accurately is inherently complex.

**Accidental:** Before Spring Boot 2.3, developers had to implement liveness/readiness separation manually. Boot now provides this with zero code.

---

### 🧪 Thought Experiment

**SETUP:** Deploy a Spring Boot service to Kubernetes without any production configuration.

**WHAT HAPPENS:**

1. Kubernetes sends traffic immediately after the container starts, before Spring finishes context initialisation. 50% of initial requests fail with `503`.
2. After 2 hours under load, the connection pool exhausts. All requests hang for 30 seconds, then fail. Kubernetes does not know the service is unhealthy (no health check configured).
3. Kubernetes restarts the pod (liveness probe uses default `/` endpoint which returns `404` once pool is exhausted - Kubernetes keeps the "healthy" pod alive but it returns errors).
4. A deployment is triggered. Old pods receive SIGTERM and die immediately, dropping 200 in-flight requests. Users see failures during every deployment.
5. OOM kill occurs overnight when a memory leak fills the heap. Post-mortem: no heap dump, no memory metric history, no alert.

**WHAT HAPPENS WITH production configuration:**

Readiness probe delays traffic until context is ready. Custom `HealthIndicator` marks service unhealthy when pool exhausts. Kubernetes restarts the pod within seconds. Graceful shutdown drains requests before pod terminates. `-XX:HeapDumpOnOutOfMemoryError` captures the OOM state. Micrometer alerts fire on pool exhaustion 10 minutes before user impact.

**THE INSIGHT:**

Production readiness is not about the happy path - it is about the ten failure modes that happen in the first week of real traffic. Spring provides all the tools; you must configure them before the first deployment.

---

### 🧠 Mental Model / Analogy

> A production Spring application is like a commercial aircraft. The engines (Spring container) work reliably. But before commercial service, the aircraft needs instruments (metrics), a cockpit warning system (health checks), an emergency communication system (structured logs), a black box (heap dumps on OOM), and a defined landing procedure (graceful shutdown). Without these, the aircraft flies - until it doesn't, and you have no idea why.

**Element mapping:**

- Aircraft instruments → Micrometer metrics + Actuator endpoints
- Cockpit warning system → health check probes + alerting rules
- Black box flight recorder → heap dump, thread dump, distributed traces
- Landing procedure → graceful shutdown sequence
- Air traffic control communication → structured JSON logs → log aggregation

Where this analogy breaks down: aircraft systems are fixed at manufacture. Spring's production configuration is intentionally flexible - teams must make explicit choices rather than accepting a fixed spec.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before you use a Spring app for real work, you need to tell it: "how do I know if you're healthy? How do I measure if you're fast? Please don't crash without warning." Spring Boot has built-in tools for all of this, but you have to turn them on and configure them.

**Level 2 - How to use it (junior developer):**
Add `spring-boot-starter-actuator`. Set `management.endpoints.web.exposure.include=health,info,metrics`. In `application.yml`, set `management.endpoint.health.probes.enabled=true` and `server.shutdown=graceful`. Configure Kubernetes `livenessProbe` and `readinessProbe` against `/actuator/health/liveness` and `/actuator/health/readiness`.

**Level 3 - How it works (mid-level engineer):**
`HealthEndpoint` aggregates contributions from all registered `HealthIndicator` beans into a single status (UP/DOWN/OUT_OF_SERVICE). The `readinessState` tracks whether the application has completed startup and is ready for traffic. `gracefulShutdown` sets the `webServer` to stop accepting new connections on SIGTERM while allowing in-flight requests to complete up to a timeout. Micrometer's `MeterRegistry` collects JVM, HTTP, DataSource, and custom metrics, forwarding them to the configured backend (Prometheus, Datadog, CloudWatch).

**Level 4 - Why it was designed this way (senior/staff):**
Kubernetes's health probe model (liveness separate from readiness) requires a subtle but critical distinction: liveness means "the process is alive and should not be killed"; readiness means "the process is ready to receive traffic." A service that is starting up should fail readiness (don't send traffic) but pass liveness (don't kill me). A service under memory pressure might fail both. Spring Boot 2.3's separation of these probes was a deliberate response to operators discovering that a combined health endpoint was insufficient for Kubernetes lifecycle management.

**Expert Thinking Cues:**

- `ApplicationAvailability` bean tracks both `LivenessState` and `ReadinessState` separately
- `AvailabilityChangeEvent` allows application code to signal unreadiness without pod restart
- Micrometer's `@Timed` annotation instruments methods with histogram metrics; prefer it over manual timing

---

### ⚙️ How It Works (Mechanism)

Production-critical Spring Boot configuration map:

```
Health Probes (Kubernetes):
  /actuator/health/liveness   → LivenessStateHealthIndicator
  /actuator/health/readiness  → ReadinessStateHealthIndicator
                              + DataSourceHealthIndicator
                              + RedisHealthIndicator + ...

Graceful Shutdown:
  SIGTERM received
  → webServer stops accepting new connections
  → in-flight requests complete (up to timeout)
  → @PreDestroy callbacks run
  → connection pools closed
  → JVM exits 0

Metrics Pipeline:
  Application code → MeterRegistry
                   → PrometheusRegistry (scrape)
                   → DatadogRegistry (push)
                   → CloudWatchRegistry (push)
  Grafana → alert rules → PagerDuty

JVM Tuning:
  -Xmx (max heap) → prevent OOM kill
  -Xms (initial heap) → predictable startup memory
  GC selection: G1GC (default) or ZGC (low latency)
  -XX:+HeapDumpOnOutOfMemoryError → forensics
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Pod starts in Kubernetes]
     |
     ├─ Spring context initialising
     |    ← YOU ARE HERE
     |    ReadinessState = REFUSING_TRAFFIC
     |    (Kubernetes does not send traffic yet)
     |
     ├─ Context refresh complete
     |    ReadinessState = ACCEPTING_TRAFFIC
     |    Kubernetes routes traffic to pod
     |
[Serving requests]
     |
     ├─ Metrics scraped every 15s by Prometheus
     ├─ Health probed every 10s by Kubernetes
     └─ Traces exported to Jaeger/Zipkin
     |
[SIGTERM received - rolling deployment]
     |
     ├─ ReadinessState → REFUSING_TRAFFIC
     |    Kubernetes removes pod from load balancer
     |
     ├─ In-flight requests drain (up to 30s timeout)
     |
     ├─ @PreDestroy → connection pools closed
     └─ JVM exits 0
```

**FAILURE PATH:**

- Liveness probe fails → Kubernetes kills + restarts pod (OOMKill, deadlock, health indicator DOWN)
- Readiness probe fails → traffic removed; pod stays alive (dependency down, warming up)
- Graceful shutdown timeout exceeded → Kubernetes force-kills (`SIGKILL`); in-flight requests dropped
- Actuator not secured → `/actuator/env` leaks secrets to unauthenticated callers

**WHAT CHANGES AT SCALE:**

At scale, the focus shifts from individual service health to _fleet health_: what % of pods are healthy, what is the p99 latency across all instances, is a canary deployment degrading. Prometheus + Grafana (or Datadog/Dynatrace) aggregate Micrometer metrics across all pods into fleet-wide dashboards.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**

Distributed tracing (`spring-boot-starter-actuator` + `micrometer-tracing`) propagates `trace-id` and `span-id` headers across HTTP calls. All logs emitted during a request include the trace-id, enabling correlation across microservices in Kibana or Grafana Loki without any application code changes.

---

### 💻 Code Example

**BAD - no production configuration:**

```yaml
# application.yml - bare minimum (not production-ready)
spring:
  datasource:
    url: jdbc:postgresql://db:5432/app
server:
  port: 8080
# No health probes, no graceful shutdown,
# no metrics, no JVM tuning
```

**GOOD - production-ready configuration:**

```yaml
# application.yml - production profile
spring:
  datasource:
    url: jdbc:postgresql://db:5432/app
    hikari:
      maximum-pool-size: 20
      connection-timeout: 3000
      idle-timeout: 600000

server:
  port: 8080
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      probes:
        enabled: true
      show-details: when-authorized
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
```

```java
// Custom HealthIndicator for a critical dependency
@Component
public class PaymentGatewayHealthIndicator
        implements HealthIndicator {
    private final PaymentClient client;

    public PaymentGatewayHealthIndicator(
            PaymentClient client) {
        this.client = client;
    }

    @Override
    public Health health() {
        try {
            client.ping();
            return Health.up()
                .withDetail("latencyMs",
                    client.lastPingMs())
                .build();
        } catch (Exception e) {
            return Health.down()
                .withException(e)
                .build();
        }
    }
}
```

**How to test / verify correctness:**

```java
@SpringBootTest(webEnvironment =
    SpringBootTest.WebEnvironment.RANDOM_PORT)
class ProductionReadinessTest {
    @Autowired TestRestTemplate rest;

    @Test
    void livenessProbeReturns200() {
        ResponseEntity<String> res =
            rest.getForEntity(
                "/actuator/health/liveness",
                String.class);
        assertThat(res.getStatusCode())
            .isEqualTo(HttpStatus.OK);
    }

    @Test
    void readinessProbeReturns200() {
        ResponseEntity<String> res =
            rest.getForEntity(
                "/actuator/health/readiness",
                String.class);
        assertThat(res.getStatusCode())
            .isEqualTo(HttpStatus.OK);
    }
}
```

---

### ⚖️ Comparison Table

| Concern              | Spring Boot Default | Production Setting                  | Why                      |
| -------------------- | ------------------- | ----------------------------------- | ------------------------ |
| Shutdown             | Immediate           | `server.shutdown=graceful`          | Drain in-flight requests |
| Health probes        | Combined            | Liveness + readiness separate       | Kubernetes lifecycle     |
| Actuator exposure    | `health, info`      | Add `prometheus`, restrict others   | Metrics scraping         |
| Actuator security    | Open                | Require auth on sensitive endpoints | Prevent data leakage     |
| Connection pool size | 10 (HikariCP)       | Size to traffic + DB limits         | Prevent pool exhaustion  |
| JVM heap             | Auto (25% RAM)      | Explicit `-Xmx`                     | Prevent OOM kill         |
| Log format           | Plain text          | JSON structured                     | Log aggregation          |
| Tracing              | Off                 | Enable Micrometer Tracing           | Distributed correlation  |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                                   |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Health endpoint = liveness probe"     | Liveness and readiness are separate states. A single `/health` endpoint mixing both causes incorrect Kubernetes pod management.                                           |
| "Graceful shutdown is automatic"       | `server.shutdown=graceful` must be explicitly set. Default is immediate shutdown.                                                                                         |
| "Actuator is safe to expose publicly"  | `/actuator/env`, `/actuator/heapdump`, `/actuator/threaddump` expose credentials and internal state. Must be secured or excluded in production.                           |
| "Default connection pool size is fine" | HikariCP defaults to 10 connections. Under 50+ concurrent requests with slow queries, this causes connection timeout failures.                                            |
| "The app is healthy if it starts"      | Startup success does not mean health. A service can start, pass liveness, and silently degrade (connection pool exhaustion, memory leak) within minutes of first traffic. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Pod killed during startup (readiness not configured)**

**Symptom:** Kubernetes kills pods repeatedly; logs show context still initialising on kill.

**Root Cause:** No readiness probe configured; Kubernetes defaults assume the service is ready immediately after container start.

**Diagnostic:**

```yaml
# Kubernetes pod spec - misconfigured
livenessProbe:
  httpGet:
    path: /actuator/health # combined! wrong
    port: 8080
  initialDelaySeconds: 30 # guess-based
# No readinessProbe configured
```

**Fix:**

```yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Prevention:** Always configure separate liveness and readiness probes. Test with `kubectl describe pod` to verify probe results.

---

**Mode 2: Connection pool exhausted under load**

**Symptom:** `HikariPool-1 - Connection is not available, request timed out after 30000ms`.

**Root Cause:** `maximumPoolSize` too small for concurrent request rate; slow queries hold connections longer than pool can supply.

**Diagnostic:**

```bash
# Check pool metrics via Actuator
curl http://localhost:8080/actuator/metrics/\
hikaricp.connections.active
curl http://localhost:8080/actuator/metrics/\
hikaricp.connections.pending
```

**Fix:**

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 50 # was 10
      connection-timeout: 3000
      # Add alert when pending > 5
```

**Prevention:** Set `management.metrics.tags.application=${spring.application.name}` and alert on `hikaricp.connections.pending > 0` for more than 60 seconds.

---

**Mode 3: Actuator leaks secrets (Security failure mode)**

**Symptom:** `GET /actuator/env` returns all environment variables including `DATABASE_PASSWORD`, `API_KEY`, `JWT_SECRET`.

**Root Cause:** `management.endpoints.web.exposure.include=*` set (common in dev); copied to production config without review.

**Diagnostic:**

```bash
curl http://your-production-server/actuator/env \
  | grep -i "password\|secret\|key"
# If this returns values: misconfigured
```

**Fix:**

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
        # Never include: env, beans, heapdump
        # in production without auth
```

```java
// Secure remaining actuator endpoints
@Bean
public SecurityFilterChain actuatorSecurity(
        HttpSecurity http) throws Exception {
    http.securityMatcher(
            EndpointRequest.toAnyEndpoint())
        .authorizeHttpRequests(r -> r
            .requestMatchers(
                EndpointRequest.to("health"))
            .permitAll()
            .anyRequest().hasRole("ACTUATOR"));
    return http.build();
}
```

**Prevention:** Treat `/actuator/env` and `/actuator/heapdump` as sensitive as admin console access. Require authentication and audit log access.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-001 - What Is Spring - History and Philosophy]] - the framework being deployed
- [[SPR-003 - Why Spring Boot Changed Java Development]] - Boot features used here
- [[SPR-044 - Auto-Configuration]] - how Actuator and health probes are auto-configured

**Builds On This (learn these next):**

- [[SPR-045 - Spring Boot Actuator]] - Actuator endpoints in depth
- [[SPR-046 - Spring Boot Startup Lifecycle]] - startup phase and readiness state
- [[SPR-048 - HikariCP]] - connection pool tuning detail

**Alternatives / Comparisons:**

- Quarkus health checks (SmallRye Health) - similar probe model, different implementation
- Micrometer documentation - the metrics library underlying Spring Boot metrics
- OpenTelemetry (OTel) - the emerging standard that Micrometer Tracing integrates with

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Spring Boot production readiness checklist|
| PROBLEM       | Gap between "runs locally" and "runs prod"|
| KEY INSIGHT   | The framework provides the tools; you must |
|               | configure them before first deployment    |
| USE WHEN      | Any Spring Boot app before production ship |
| AVOID WHEN    | -                                          |
| TRADE-OFF     | Config complexity vs operational resilience|
| ONE-LINER     | Health + metrics + graceful shutdown +     |
|               | JVM tuning = production-ready             |
| NEXT EXPLORE  | SPR-045 (Actuator), SPR-048 (HikariCP)    |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Separate liveness and readiness probes - they solve different Kubernetes lifecycle problems
2. `server.shutdown=graceful` must be explicit - default is immediate and drops in-flight requests
3. Never expose `/actuator/env` or `/actuator/heapdump` without authentication - they contain secrets

**Interview one-liner:** "A production-ready Spring Boot application configures separate liveness and readiness probes, graceful shutdown, Micrometer metrics, structured logging, JVM memory tuning, and secured Actuator endpoints."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Observability is not optional in production_ - every service must emit health signals, metrics, and traces from day one. Retrofitting observability after a production incident is 10x more expensive than building it in. This principle applies regardless of framework.

**Where else this pattern appears:**

- **AWS Lambda** - function health tracked via CloudWatch metrics; no equivalent of a liveness probe but dead-letter queues serve a similar signal
- **Node.js / Express** - `express-status-monitor` or custom `/healthz` endpoints implement the same liveness/readiness split
- **Kubernetes operators** - `CustomResource` status conditions (Ready, Available, Degraded) are the same liveness/readiness concept at the cluster resource level

---

### 💡 The Surprising Truth

The most common cause of Spring Boot production incidents is not a Spring bug or a Java bug - it is the default HikariCP connection pool size of **10 connections**. HikariCP's creator Bret Wooldridge documented that the optimal pool size formula is not "as large as possible" - it is approximately `(core_count * 2) + effective_spindle_count`, typically 8-20 connections. Teams that blindly increase pool size to 100+ actually _decrease_ throughput due to database connection context switching overhead. The ideal pool is smaller than most engineers expect, and Spring Boot's default of 10 is often correct - the problem is that teams do not alert on pool exhaustion until it causes a visible outage.

---

### 🧠 Think About This Before We Continue

**Question 1 (A - System Interaction):** Spring Boot's readiness probe mechanism depends on `ApplicationAvailability` bean tracking `ReadinessState`. What specific events during Spring context startup change the state from `REFUSING_TRAFFIC` to `ACCEPTING_TRAFFIC`, and what happens if a `CommandLineRunner` throws an exception after the context refreshes?

_Hint:_ Look at `ApplicationReadyEvent` vs `ContextRefreshedEvent` in [[SPR-046 - Spring Boot Startup Lifecycle]] and trace the `ReadinessState` transition sequence.

**Question 2 (D - Root Cause):** A service passes its readiness probe and receives traffic, but 20% of requests return HTTP 503. The logs show `HikariPool-1 - Connection is not available`. The pool size is 20 and the database reports only 15 active connections. What are the two most likely root causes, and how would you distinguish between them using metrics?

_Hint:_ Look at `hikaricp.connections.active` vs `hikaricp.connections.pending` vs query execution time in [[SPR-048 - HikariCP]] and consider both pool sizing and slow query duration.

**Question 3 (C - Design Trade-off):** Graceful shutdown waits for in-flight requests to complete before the JVM exits. If a request takes 5 minutes (e.g., a long-running batch operation triggered via HTTP), graceful shutdown would block for 5 minutes - potentially exceeding Kubernetes `terminationGracePeriodSeconds`. How should long-running HTTP-triggered operations be architectured to be compatible with graceful shutdown?

_Hint:_ Consider offloading to [[ASY-001]] async processing or [[SPR-006 - Spring Batch]] triggered asynchronously, rather than holding an HTTP connection open for the duration.
