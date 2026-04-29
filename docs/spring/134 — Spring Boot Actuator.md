---
layout: default
title: "Spring Boot Actuator"
parent: "Spring Framework"
nav_order: 134
permalink: /spring/spring-boot-actuator/
---
⚡ TL;DR — Spring Boot Actuator exposes production-ready HTTP endpoints for health checks, metrics, environment inspection, and more — with zero extra code.
## 📘 Textbook Definition
Spring Boot Actuator is a sub-project that adds production-ready features to Spring Boot applications. It provides built-in HTTP and JMX endpoints for monitoring and managing applications — including health checks (`/actuator/health`), metrics (`/actuator/metrics`), environment properties (`/actuator/env`), bean listing (`/actuator/beans`), and condition reports (`/actuator/conditions`).
## 🟢 Simple Definition (Easy)
Actuator adds a "diagnostic panel" to your app. Without writing any code, you get URLs like `/health` (is the app up?), `/metrics` (CPU, memory, request counts), and `/beans` (all Spring beans). It's essential for production monitoring.
## 💻 Code Example
```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,info,env,beans,loggers,conditions
  endpoint:
    health:
      show-details: always  # show component health (DB, Redis, etc.)
  health:
    db:
      enabled: true
# Dependency: spring-boot-starter-actuator
```
```java
// Custom health indicator
@Component
public class PaymentServiceHealthIndicator implements HealthIndicator {
    @Autowired PaymentGateway gateway;
    @Override
    public Health health() {
        if (gateway.isUp()) {
            return Health.up()
                .withDetail("latency", gateway.pingLatency() + "ms")
                .build();
        }
        return Health.down()
            .withDetail("reason", "Payment gateway unreachable")
            .build();
    }
}
// Custom metric
@Component
public class OrderMetrics {
    private final Counter orderCounter;
    public OrderMetrics(MeterRegistry registry) {
        orderCounter = Counter.builder("orders.placed")
            .description("Total orders placed")
            .register(registry);
    }
    public void recordOrder() { orderCounter.increment(); }
}
```
**Key endpoints:**
```
/actuator/health        → UP/DOWN with component details
/actuator/metrics       → list all metric names
/actuator/metrics/jvm.memory.used → specific metric
/actuator/env           → all properties (mask sensitive ones!)
/actuator/beans         → all Spring beans and their dependencies
/actuator/loggers       → view and change log levels at runtime
/actuator/threaddump    → current thread state
/actuator/httptrace     → recent HTTP requests
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Actuator is only for development | It's designed for production — integrate with Prometheus/Grafana |
| /actuator is exposed by default | Only /health and /info are exposed by default — others must be enabled |
| Actuator endpoints have no security risk | /env and /beans can expose sensitive data — secure with Spring Security |
## 🔗 Related Keywords
- **[Spring Boot Startup Lifecycle](./135 — Spring Boot Startup Lifecycle.md)** — Actuator context initialized during startup
- **[Auto-Configuration](./133 — Auto-Configuration.md)** — Actuator endpoints are auto-configured
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| HEALTH      | /actuator/health — liveness/readiness for k8s        |
+------------------------------------------------------------------+
| METRICS     | /actuator/metrics — Micrometer counters/timers/gauges |
+------------------------------------------------------------------+
| SECURITY    | Lock down /actuator with Spring Security              |
+------------------------------------------------------------------+
| CUSTOM      | Implement HealthIndicator or inject MeterRegistry     |
+------------------------------------------------------------------+
```
