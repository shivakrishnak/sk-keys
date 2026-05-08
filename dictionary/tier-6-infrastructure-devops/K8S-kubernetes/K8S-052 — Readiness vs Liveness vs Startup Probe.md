---
layout: default
title: "Readiness vs Liveness vs Startup Probe"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /kubernetes/readiness-vs-liveness-vs-startup-probe/
id: K8S-052
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "kubelet", "Rolling Update Strategy"]
used_by: ["Deployment", "Rolling Update Strategy", "Service (K8s)"]
related: ["Pod", "kubelet", "Rolling Update Strategy", "Service (K8s)"]
tags:
  [
    kubernetes,
    readiness-probe,
    liveness-probe,
    startup-probe,
    health-checks,
    k8s,
  ]
---

# Readiness vs Liveness vs Startup Probe

## ⚡ TL;DR

Three health check types in Kubernetes: **Readiness** (should this Pod receive traffic?), **Liveness** (is this Pod alive or should it be restarted?), **Startup** (has this Pod finished starting?). kubelet runs these probes and takes action based on results. Misconfigured probes cause cascading failures.

---

## 🔥 Problem This Solves

A container may be running (process alive) but not yet ready to serve requests (still loading data). Or it may be alive but stuck in a deadlock (needs restart). Or it may be a slow-starting app incorrectly killed by liveness before it finishes booting. Three probes handle three distinct concerns.

---

## 📘 Textbook Definition

Kubernetes probes are diagnostic actions periodically executed by kubelet on containers. Readiness probes determine traffic eligibility (endpoint inclusion/exclusion). Liveness probes determine if a container should be restarted. Startup probes give slow-starting apps time to initialize before liveness begins.

---

## ⏱️ 30 Seconds

```yaml
containers:
  - name: app
    # Startup: is the app done initializing? (runs first)
    startupProbe:
      httpGet:
        path: /health/ready
        port: 8080
      failureThreshold: 30 # allow up to 30 × 10s = 5 min startup
      periodSeconds: 10

    # Liveness: is the app alive? (restart if fails)
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 15
      failureThreshold: 3 # 3 failures → restart

    # Readiness: ready for traffic? (remove from Service endpoints)
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      periodSeconds: 5
      failureThreshold: 3 # 3 failures → remove from endpoints
```

---

## 🔩 First Principles

- **Probe types**: `httpGet` (HTTP status 200-399 = success), `tcpSocket` (connection = success), `exec` (exit code 0 = success), `grpc` (gRPC health check)
- **Readiness failure**: Pod removed from Service EndpointSlices (no traffic), NOT restarted
- **Liveness failure**: Container restarted (SIGTERM, then SIGKILL); Pod stays on node
- **Startup failure**: Container restarted if failureThreshold × periodSeconds exceeded
- Startup probe DISABLES liveness probe while running
- All probes run on kubelet, NOT from an external service

---

## 🧪 Thought Experiment

Spring Boot app with 2 million entities to load into cache at startup (30 seconds). Without startup probe: liveness probe starts immediately, app hasn't loaded cache, liveness check fails → restart → infinite restart loop. With startup probe: liveness deactivated for first 5 minutes, app loads cache successfully, startup passes, liveness and readiness begin. App is healthy.

---

## 🧠 Mental Model / Analogy

Think of opening a restaurant: **Startup** = "is the kitchen ready to start service?" (one-time initialization). **Liveness** = "is the chef still alive?" (ongoing health). **Readiness** = "is the kitchen ready to accept new orders right now?" (can fluctuate — during lunch rush peak, temporarily unready to take more orders without losing chef).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Readiness = can I send traffic here? Liveness = is this alive (restart if not)? Startup = is it done starting?

**Level 2 — Practitioner**: Use different endpoints: `/health/ready` (includes dependency checks) vs `/health/live` (minimal check). Startup probe: `failureThreshold × periodSeconds` = max startup time. Readiness failure = traffic removed; liveness failure = restart.

**Level 3 — Advanced**: Spring Boot Actuator: `/actuator/health/liveness` and `/actuator/health/readiness` auto-provided. Customize readiness groups: add database ping, cache check to readiness only. Don't add expensive checks to liveness (causes restart loops under load).

**Level 4 — Expert**: Probe execution costs: each probe consumes CPU/memory; high-frequency probes on many Pods strain kubelet. `grpc` probe: uses grpc-health-probe or built-in gRPC health checking protocol. Liveness probe and connection draining: liveness restart kills connections immediately; use `preStop` hook + `terminationGracePeriodSeconds` for graceful drain before restart. Startup probe with Jobs: not applicable (Jobs run to completion, not steady-state).

---

## ⚙️ How It Works

### Probe Execution Timeline

```
Container starts:
  │
  ├─ startupProbe begins (if configured)
  │   ├─ livenessProbe DISABLED while startupProbe running
  │   ├─ readinessProbe DISABLED while startupProbe running
  │   └─ If failureThreshold reached → container restart
  │   → If startup succeeds → startupProbe stops
  │
  ├─ livenessProbe begins (after startup or initialDelaySeconds)
  │   └─ failureThreshold consecutive failures → restart container
  │
  └─ readinessProbe begins (after startup or initialDelaySeconds)
      └─ failure → removed from Service endpoints
         success → added to Service endpoints
```

### Spring Boot Actuator Configuration

```java
// Spring Boot 2.3+ supports Kubernetes probes natively
// application.properties:
management.health.livenessState.enabled=true
management.health.readinessState.enabled=true

// Readiness group (includes dependencies)
management.endpoint.health.group.readiness.include=readinessState,db,redis

// Custom readiness indicator
@Component
public class CacheReadinessIndicator implements HealthIndicator {
    @Autowired
    private CacheService cache;

    @Override
    public Health health() {
        if (cache.isWarmed()) {
            return Health.up().build();
        }
        return Health.down()
            .withDetail("reason", "cache not warmed")
            .build();
    }
}
```

### Probe Types

```yaml
# HTTP GET
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
    httpHeaders:
    - name: Accept
      value: application/json

# TCP Socket (port open = alive)
livenessProbe:
  tcpSocket:
    port: 5432    # useful for databases

# Exec command (exit 0 = success)
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy

# gRPC (Kubernetes 1.24+)
livenessProbe:
  grpc:
    port: 50051
    service: liveness
```

### Production Configuration

```yaml
containers:
  - name: app
    image: my-app:v1.0

    startupProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      failureThreshold: 30 # 30 × 10s = 5 min max startup
      periodSeconds: 10
      successThreshold: 1

    livenessProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      periodSeconds: 10
      failureThreshold: 3 # 30s before restart
      successThreshold: 1
      timeoutSeconds: 3

    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      periodSeconds: 5
      failureThreshold: 3 # 15s before removed from endpoints
      successThreshold: 2 # must succeed 2x before re-added
      initialDelaySeconds: 5
      timeoutSeconds: 3
```

---

## 🔄 E2E Flow: Readiness During Rolling Update

```
kubectl set image deployment/my-app app=my-app:v2.0

1. New Pod created with v2.0
2. startupProbe: app initializing, returns 503 → retry
3. startupProbe: app ready → startup complete
4. readinessProbe: /health/ready → 200 OK
5. Endpoint added to Service: new Pod receives traffic
6. Rolling update proceeds to next Pod

Failed scenario:
1. New Pod created with v2.0-broken
2. readinessProbe: /health/ready → 500
3. Pod stays NotReady
4. Rolling update PAUSED (maxSurge reached, no new Pods until current Ready)
5. Old Pods continue serving all traffic
6. After progressDeadlineSeconds → DeadlineExceeded
7. kubectl rollout undo → old Pods restored
```

---

## ⚖️ Comparison Table

|                           | Readiness             | Liveness                | Startup                     |
| ------------------------- | --------------------- | ----------------------- | --------------------------- |
| **Action on failure**     | Remove from endpoints | Restart container       | Restart container           |
| **Action on success**     | Add to endpoints      | Nothing (keep running)  | Enable liveness + readiness |
| **Can fluctuate**         | ✅ Yes                | No (restart)            | No (once only)              |
| **Use case**              | Traffic control       | Deadlock/hung detection | Slow startup apps           |
| **Disables other probes** | No                    | No                      | Liveness + Readiness        |

---

## ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                |
| ----------------------------------------------- | ---------------------------------------------------------------------- |
| "Liveness failure removes from Service"         | Readiness removes from Service; liveness restarts the container        |
| "No probes = K8s manages traffic intelligently" | Without probes, K8s routes traffic to containers the moment they start |
| "Startup probe is for all apps"                 | Only needed for slow-starting apps; fast apps don't need it            |
| "Readiness failure = Pod terminated"            | Pod stays running; only removed from load balancer rotation            |

---

## 🚨 Failure Modes

| Failure                       | Symptom                                                 | Fix                                                         |
| ----------------------------- | ------------------------------------------------------- | ----------------------------------------------------------- |
| Liveness probe too aggressive | CrashLoopBackOff under load (GC pause triggers restart) | Increase `failureThreshold` and `timeoutSeconds`            |
| No startup probe for slow app | App killed before it finishes starting                  | Add startup probe with sufficient failureThreshold          |
| Readiness checks liveness     | App removed from endpoints during GC pause              | Separate readiness (/ready) from liveness (/live) endpoints |
| Probe creates thundering herd | Every probe hits database → overload                    | Implement lightweight health endpoint (cache status)        |

---

## 🔗 Related Keywords

- [Rolling Update Strategy](/kubernetes/rolling-update-strategy/) — readiness gates update progress
- [Service (K8s)](/kubernetes/service-k8s/) — readiness controls endpoint inclusion
- [Pod](/kubernetes/pod/) — probes are container-level
- [kubelet](/kubernetes/kubelet/) — executes all probes

---

## 📌 Quick Reference Card

```bash
# Check probe status in pod
kubectl describe pod my-pod | grep -A 10 "Liveness\|Readiness\|Startup"

# Check why pod not ready
kubectl describe pod my-pod | grep -B 5 "Unhealthy"
kubectl get events --field-selector involvedObject.name=my-pod

# Check endpoints (does pod appear?)
kubectl get endpoints my-service

# Spring Boot actuator health
curl http://localhost:8080/actuator/health/liveness
curl http://localhost:8080/actuator/health/readiness

# Probe config fields
# initialDelaySeconds: seconds to wait before first probe
# periodSeconds: how often to probe
# timeoutSeconds: probe timeout
# successThreshold: consecutive successes to pass
# failureThreshold: consecutive failures to fail
```

---

## 🧠 Think About This

The most dangerous probe antipattern is making your **liveness probe check the same things as your readiness probe**. If your readiness probe includes a database connectivity check (correct: temporarily remove from traffic if DB is unreachable) and your liveness probe also checks DB connectivity, then a DB outage causes liveness failures → all Pods restart → which makes the DB outage worse (reconnection storms). Liveness should check only: "is my process alive and not stuck?" Use a minimal heartbeat endpoint. Readiness can be more thorough: "am I ready to handle requests including my dependencies?"
