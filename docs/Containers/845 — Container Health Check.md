---
layout: default
title: "Container Health Check"
parent: "Containers"
nav_order: 845
permalink: /containers/container-health-check/
number: "0845"
category: Containers
difficulty: ★★☆
depends_on: Container, Docker, Container Orchestration, Container Resource Limits
used_by: Kubernetes Architecture, Readiness vs Liveness vs Startup Probe, Container Orchestration
related: Readiness vs Liveness vs Startup Probe, Container Resource Limits, Container Orchestration, Init Container, Kubernetes Architecture
tags:
  - containers
  - kubernetes
  - reliability
  - intermediate
  - production
---

# 845 — Container Health Check

⚡ TL;DR — Container health checks tell the orchestrator whether a container is alive, ready for traffic, or needs time to start — preventing traffic from reaching broken containers.

| #845 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Container, Docker, Container Orchestration, Container Resource Limits | |
| **Used by:** | Kubernetes Architecture, Readiness vs Liveness vs Startup Probe, Container Orchestration | |
| **Related:** | Readiness vs Liveness vs Startup Probe, Container Resource Limits, Container Orchestration, Init Container, Kubernetes Architecture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your application container starts, the process launches, and Kubernetes immediately routes traffic to it — even though the Spring Boot application takes 15 seconds to fully initialise (database connections, caches warm-up). For those 15 seconds, every request returns HTTP 503. Then at 2 AM, a memory leak causes the application to enter a deadlocked state: the process is running (the kernel sees it as alive), but every HTTP request hangs indefinitely. Without health checks, Kubernetes has no way to know the container is broken — it never restarts it, traffic continues flowing in, and users get hanging requests until someone wakes up and manually kills the pod.

**THE BREAKING POINT:**
Container orchestrators can only know a container is running at the process level. But "process running" ≠ "application healthy" ≠ "ready to serve traffic." These are three distinct states that require three different signals.

**THE INVENTION MOMENT:**
This is exactly why container health checks (Kubernetes probes) were developed — three distinct probe types (startup, liveness, readiness) that let the application tell the orchestrator its health state, enabling automatic recovery from hangs, delayed traffic until ready, and protection against crashing apps receiving deployment traffic prematurely.

---

### 📘 Textbook Definition

A **container health check** (in Kubernetes: a *probe*) is a periodic diagnostic action performed by the kubelet on a container to determine its health state. Kubernetes defines three probe types: **liveness probe** (is the container alive or should it be restarted?), **readiness probe** (should this container receive traffic?), and **startup probe** (has the container fully started — used to protect slow-starting containers from premature liveness checks). Each probe can be implemented as an HTTP GET request, TCP socket check, or arbitrary exec command. Probe outcomes affect container state: liveness failure triggers restart; readiness failure removes the container from Service endpoints; startup failure prevents other probes from running.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Health checks are the container's way of telling its orchestrator: "I'm alive, I'm ready, or I'm still starting."

**One analogy:**
> A hospital monitoring system measures three different things. (1) Is the patient breathing? (liveness — if not, emergency resuscitation/restart). (2) Is the patient stable enough to see visitors? (readiness — if not, no new visitors/traffic). (3) Has the patient woken up from surgery yet? (startup — if not, don't apply the other tests yet). Container health checks answer the same three questions about your application. Each answer determines a different course of action.

**One insight:**
The three probe types solve three different problems at different lifecycle stages. Conflating them leads to misconfiguration: using only a liveness probe means the app can receive traffic while starting (should be readiness), and using a readiness probe to replace liveness means a deadlocked app is never restarted (should be liveness). All three do different jobs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Process alive ≠ application healthy ≠ ready for traffic — these are logically distinct states.
2. "Restart" is the recovery mechanism for permanent failures; "remove from load balancer" is recovery for temporary unavailability.
3. Slow-starting applications need protection from premature liveness probe failures that cause restart loops before the application ever fully starts.

**DERIVED DESIGN:**

**Liveness Probe:**
- Question: "Is the application in an unrecoverable state that requires a restart?"
- Action on failure: restart the container (killed + restarted per `restartPolicy`)
- Purpose: recover from deadlocks, stuck threads, infinite loops
- Warning: liveness probe failures that can be caused by temporary overload cause disruptive cascade restarts — liveness checks should only fail on truly unrecoverable states

**Readiness Probe:**
- Question: "Is the application ready to receive traffic?"
- Action on failure: remove container from Service endpoints (no new requests routed to it)
- Purpose: prevent traffic during startup, during dependency unavailability, during self-reported overload
- Key: readiness failure does NOT restart the container — it just stops traffic

**Startup Probe:**
- Question: "Has the application finished its startup sequence?"
- Action on failure: restart the container (same as liveness)
- Purpose: protect slow-starting apps (30–180 second startups) by disabling liveness/readiness checks until startup succeeds
- While startup probe is running: liveness and readiness probes are suspended

```
┌──────────────────────────────────────────────────────────┐
│           Container Lifecycle: Probe Timeline            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Container starts                                        │
│  │                                                       │
│  ├── Startup probe runs (startup phase)                  │
│  │   ├── initial delay: 10s                              │
│  │   ├── runs every: 5s                                  │
│  │   ├── failureThreshold: 30 (max 150s total)           │
│  │   └── → success: switches to liveness/readiness       │
│  │                                                       │
│  ├── Readiness probe runs (traffic gate)                 │
│  │   ├── passes → pod added to Service endpoints         │
│  │   └── fails → pod removed from Service endpoints      │
│  │                                                       │
│  └── Liveness probe runs (crash detection)               │
│      ├── passes → container continues                    │
│      └── fails N times → container restarted            │
└──────────────────────────────────────────────────────────┘
```

**Probe mechanics:**
- `initialDelaySeconds`: wait N seconds before first probe (legacy — startup probe is preferred)
- `periodSeconds`: how often to probe
- `timeoutSeconds`: probe timeout
- `failureThreshold`: consecutive failures before action
- `successThreshold`: consecutive successes before marking healthy

**THE TRADE-OFFS:**

**Gain:** Automatic recovery from app hangs (liveness). Zero-downtime rolling updates (readiness prevents traffic to unready pods). Slow-start protection (startup).

**Cost:** Misconfigured probes cause worse behaviour than no probes: liveness probes that fire on temporary load cause cascade restarts; readiness probes that never fail hide broken apps. Probe checks themselves consume resources.

---

### 🧪 Thought Experiment

**SETUP:**
A Kubernetes Deployment rolls out a new version. The new image has a bug — on 1 in 50 requests, it hangs indefinitely (goroutine deadlock in a specific code path). Process is running. No errors in logs. CPU is near zero.

**WHAT HAPPENS WITHOUT HEALTH CHECKS:**
Kubernetes sees the container process is running. It completes the rolling update. All replicas now run the buggy version. 2% of requests hang indefinitely. Users see hanging requests. SRE team gets paged 30 minutes later. Manual rollback required.

**WHAT HAPPENS WITH LIVENESS PROBE:**
The liveness probe is: `GET /health → 200 within 3s`. The deadlocked goroutine is holding a lock; the /health handler also needs that lock → /health hangs → timeout → liveness failure. After 3 consecutive failures (36 seconds), kubelet restarts the container. The restart clears the deadlock. The container comes back up. Liveness probe passes. Service is degraded for 36 seconds but self-recovers without human intervention.

**WHAT HAPPENS WITH READINESS PROBE (ROLLING UPDATE):**
During rollout, each new pod only receives traffic after its readiness probe passes. The buggy pod's readiness probe uses a different code path and passes. However — the deployment can be configured `maxUnavailable: 0` meaning old pods are only taken down after new pods are fully Ready. This prevents the buggy rollout from taking down old pods before the new pods are serving correctly. Any readiness probe failure during rollout pauses the rollout automatically.

**THE INSIGHT:**
Liveness probes are your automated recovery operator. Readiness probes are your zero-downtime deployment guard. Use both — they protect against different failure modes.

---

### 🧠 Mental Model / Analogy

> Think of three traffic lights at the container entrance. The first light (startup probe) is red until the application has finished booting — "not ready yet, don't even check." The second light (readiness probe) is red when the application can't handle traffic — "running but closed." The third light (liveness probe) is a fire alarm — it kills and restarts the entire container when it goes off. You want the startup light to turn green as fast as possible. You want the readiness light to be red only when genuinely unavailable. You want the liveness alarm to fire only when restarting is better than continuing.

Mapping:
- "Startup red light" → startup probe must pass before other probes activate
- "Readiness red light" → removes from Service endpoints (no traffic)
- "Liveness alarm" → restarts container
- "Restaurant 'Open / Closed' sign" → readiness probe
- "Smoke detector" → liveness probe (triggers evacuation/restart)

Where this analogy breaks down: traffic lights are manual; probes are automatic and periodic. A smoke detector stops an alarm when smoke clears; a liveness probe restarts the container every time the threshold is exceeded.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Health checks are periodic tests Kubernetes runs on your container to check if it's working. If the test fails repeatedly, Kubernetes either stops sending traffic to that container (readiness) or restarts it (liveness). This is how Kubernetes automatically recovers from broken containers without human intervention.

**Level 2 — How to use it (junior developer):**
Add probes to your container spec. For a Spring Boot app with actuator: liveness → `GET /actuator/health/liveness`, readiness → `GET /actuator/health/readiness`. Configure `initialDelaySeconds` to be slightly longer than your app's startup time (or use a startup probe instead). Set `failureThreshold: 3` for liveness so one slow response doesn't trigger a restart.

**Level 3 — How it works (mid-level engineer):**
Kubelet runs probes directly from the node — not via the Kubernetes API. For HTTP probes: kubelet makes an HTTP GET request to the container's IP and port. For TCP probes: kubelet opens a TCP connection to the port. For exec probes: kubelet runs the specified command inside the container and checks exit code. Results are stored per-container and reflected in pod status conditions. Readiness affects `Endpoints` objects (Service endpoint selection). Liveness failure triggers `ContainerKill` + restart.

**Level 4 — Why it was designed this way (senior/staff):**
The three-probe model is the result of operational experience revealing that "is it running?" (liveness) and "should it receive traffic?" (readiness) are fundamentally different questions that need different responses. The startup probe was added later (Kubernetes 1.16 stable) because `initialDelaySeconds` on liveness was a blunt instrument — it required knowing the exact startup time upfront, and any regression in startup time could cause liveness failures before the app was ready. The startup probe replaces `initialDelaySeconds` with a dynamic mechanism: run until success, and only then activate liveness. The split between probe types also enables graceful degradation: a service under extreme load can mark itself not-ready (readiness probe fails) causing load balancer traffic to shift to healthy replicas, without triggering a restart. This is self-protecting under load — a capability that liveness-probe-only designs cannot provide.

---

### ⚙️ How It Works (Mechanism)

**Probe execution flow (Kubernetes):**
```
┌──────────────────────────────────────────────────────────┐
│       Probe Execution Flow (kubelet perspective)         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Every periodSeconds (e.g., 10s):                        │
│                                                          │
│  kubelet → HTTP GET container:8080/health                │
│    ├── response 200–399 within timeoutSeconds:           │
│    │     probe SUCCESS → successor counter=1             │
│    │     (after successThreshold: mark healthy)          │
│    └── response 4xx/5xx/timeout:                         │
│          probe FAILURE → failure counter++               │
│          after failureThreshold failures:                │
│           liveness: ContainerSigkill + restart           │
│           readiness: remove from Endpoints               │
│           startup: ContainerSigkill + restart            │
│                                                          │
│  Restart backoff (liveness failure):                     │
│  0, 10s, 20s, 40s, 80s, 160s... up to 300s cap           │
│  (exponential backoff per container in pod)              │
└──────────────────────────────────────────────────────────┘
```

**Probe types comparison:**

| Probe Type | Failure Action | Traffic Stops? | Container Restarts? | Use For |
|---|---|---|---|---|
| `livenessProbe` | restart container | No (until restarted) | Yes | Deadlock, irrecoverable state |
| `readinessProbe` | remove from Service | Yes | No | Startup, temp unavailability, backpressure |
| `startupProbe` | restart container | Yes (no traffic yet) | Yes | Slow startup protection |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (rolling update with readiness probe):**
```
kubectl apply updated deployment
  → new pod starts → startup probe running ← YOU ARE HERE
  → startup probe passes (app started)
  → readiness probe passes (app healthy)
  → pod added to Service Endpoints (traffic starts)
  → old pod: readiness removed first → no traffic
  → old pod terminated → rolling update complete
  → zero traffic interruption
```

**FAILURE PATH (liveness probe failure):**
```
container enters deadlocked state (goroutine stuck)
  → liveness GET /health: timeout
  → kubelet: failure count = 1, 2, 3 → failureThreshold
  → kubelet: terminates container (SIGKILL after grace period)
  → container restarts
  → startup probe runs → readiness probe runs
  → pod recovers → traffic resumes
  → Prometheus shows restart_count++ → alert fires
```

**WHAT CHANGES AT SCALE:**
At scale, probe overhead accumulates: 1,000 pods × 3 probes × every 10s = 300 probe requests/second to the application just for health checks. Design `/health` endpoints to be extremely cheap — no database calls, no dependency checks. Reserve heavy health checks for readiness, and only when returning from not-ready state.

---

### 💻 Code Example

**Example 1 — Spring Boot Actuator probes:**
```yaml
containers:
- name: spring-app
  image: myapp:1.0.0
  ports:
  - containerPort: 8080

  startupProbe:
    httpGet:
      path: /actuator/health/liveness  # Spring Actuator liveness group
      port: 8080
    failureThreshold: 30   # 30 failures × 5s period = 150s max startup
    periodSeconds: 5

  livenessProbe:
    httpGet:
      path: /actuator/health/liveness
      port: 8080
    initialDelaySeconds: 0  # startup probe handles startup delay
    periodSeconds: 10
    timeoutSeconds: 3
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /actuator/health/readiness  # Spring readiness group
      port: 8080
    periodSeconds: 5
    failureThreshold: 3
    successThreshold: 1
```

**Example 2 — TCP probe (for non-HTTP services):**
```yaml
livenessProbe:
  tcpSocket:
    port: 6379    # Redis port
  initialDelaySeconds: 5
  periodSeconds: 10
```

**Example 3 — Exec probe (custom check):**
```yaml
livenessProbe:
  exec:
    command:
    - sh
    - -c
    - "redis-cli ping | grep PONG"
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
```

**Example 4 — Readiness probe for backpressure:**
```java
// Application exposes readiness based on queue depth
@GetMapping("/health/readiness")
public ResponseEntity<Map<String, String>> readiness() {
    if (requestQueue.size() > 900) {
        // Tell orchestrator not to send more traffic
        return ResponseEntity.status(503)
            .body(Map.of("status", "overloaded"));
    }
    return ResponseEntity.ok(Map.of("status", "ready"));
}
```

---

### ⚖️ Comparison Table

| Probe Method | Best For | Works With Distroless | Overhead |
|---|---|---|---|
| **HTTP GET** | REST APIs, web services | Yes (no shell needed) | Minimal |
| TCP socket | TCP services without HTTP (Redis, Kafka, DB) | Yes | Minimal |
| Exec command | Custom logic, script-based checks | No (needs shell) | Medium (fork + exec) |
| gRPC health protocol | gRPC services | Yes | Minimal |

How to choose: HTTP GET for any HTTP service — it's the most informative. TCP for non-HTTP services. Exec only when HTTP/TCP cannot represent the health check, and only in images that have a shell. Avoid exec probes in distroless images.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A liveness probe failure stops traffic before the restart" | No. Liveness failure causes an immediate restart without removing from Service endpoints first. Readiness probe failure removes from endpoints without restarting. For graceful traffic removal before restart, you need both probes (or `preStop` hook). |
| "I only need a liveness probe" | Liveness alone means traffic is sent to containers from the moment they start — before initialisation is complete. Always add a readiness probe to gate traffic on application readiness. |
| "Health checks should verify all downstream dependencies" | No. A liveness probe that fails because a downstream database is temporarily unavailable will restart ALL instances, even though the application itself is healthy. This amplifies the downstream outage into your service. |
| "Setting failureThreshold: 1 gives faster recovery" | Dangerously aggressive — one slow probe response (network hiccup, momentary GC pause) triggers a restart. Use 3+ failures threshold. |
| "initialDelaySeconds is the right way to handle slow starts" | `initialDelaySeconds` is a fixed guess that requires tuning. Startup probes are the correct mechanism: dynamic, retry until success, no need to know the exact startup time. |

---

### 🚨 Failure Modes & Diagnosis

**Cascade restarts from liveness probe misconfiguration**

**Symptom:**
Under load, many pods restart simultaneously. `kubectl get events` shows repeated `Killing container with id: ...` events. Application appears to restart during every peak traffic period.

**Root Cause:**
Liveness probe timeout (`timeoutSeconds`) is set too low. During load, GC pause or CPU throttling causes the health endpoint to take > timeoutSeconds. Multiple consecutive "failures" trigger restart.

**Diagnostic Command / Tool:**
```bash
kubectl get events --field-selector reason=Killing -n production

kubectl logs <pod> --previous | tail -50
# Are there GC pauses or CPU throttle events before restart?

# Check probe config
kubectl describe pod <pod> | grep -A10 "Liveness"
```

**Fix:**
Increase `timeoutSeconds` to 5–10 seconds. Increase `failureThreshold` to 5. If the app is under CPU throttling causing probe timeouts, fix the root cause (increase CPU limit or scale horizontally).

**Prevention:**
Test liveness probe response time under peak load. Set timeouts conservatively. Monitor `kube_pod_container_status_restarts_total`.

---

**Readiness probe never passes on startup → pod stuck in CrashLoopBackOff**

**Symptom:**
New deployment pods never transition to Ready. `kubectl describe pod` shows readiness probe failing indefinitely. Service gets no traffic from new pods.

**Root Cause:**
Readiness probe fires before startup completes (no startup probe, `initialDelaySeconds` too short), or readiness check endpoint is broken (wrong path, wrong port).

**Diagnostic Command / Tool:**
```bash
kubectl describe pod <pod> | grep -A15 "Readiness"
# Check Events for probe failure messages

# Test probe manually from inside cluster
kubectl exec -it <debug-pod> -- \
  curl -v http://<pod-ip>:8080/health/readiness
```

**Fix:**
Add startup probe. Fix probe path/port. Check application logs for startup errors.

**Prevention:**
Test probe endpoints with `curl` before deploying. Use startup probes for any application with startup time > 10 seconds.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Container` — health checks are applied to containers; understand containers first
- `Container Orchestration` — orchestrators use health check results to route traffic and restart containers
- `Container Resource Limits` — OOMKills look like container failures; understand limits before diagnosing false probe failures

**Builds On This (learn these next):**
- `Readiness vs Liveness vs Startup Probe` — the Kubernetes-specific deep dive into all three probe types
- `Kubernetes Architecture` — how kubelet executes probes and reports results
- `Container Orchestration` — health checks enable self-healing in orchestrated deployments

**Alternatives / Comparisons:**
- `Init Container` — setup guarantee before startup (not health monitoring); different purpose
- `Readiness vs Liveness vs Startup Probe` — the same concept, Kubernetes-specific and more detailed
- `Container Resource Limits` — resource exhaustion causes health check failures; both are production robustness concerns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Periodic diagnostic probes that tell the  │
│              │ orchestrator a container's health state   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ "Process running" ≠ "app healthy" —       │
│ SOLVES       │ orchestrators need application-level      │
│              │ health signals to recover automatically   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Three probes, three different actions:    │
│              │ startup (protect slow boot),              │
│              │ readiness (gate traffic),                 │
│              │ liveness (restart deadlocked app)         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every production Kubernetes container —   │
│              │ no exceptions                             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Liveness probe: never check downstream    │
│              │ dependencies (amplifies outages)          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Self-healing + zero-downtime deploys vs   │
│              │ misconfiguration risk + probe overhead    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Is it alive? Is it ready? Is it started? │
│              │  Three questions, three different answers" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Readiness vs Liveness vs Startup Probe →  │
│              │ Container Resource Limits → HPA           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service has three replicas behind a Kubernetes Service. Replica A's readiness probe fails (not ready). Replicas B and C are ready. Traffic redistributes to B and C, doubling their load. B's liveness probe now starts failing due to CPU throttling under double load. B is restarted. Now only C handles all traffic, which is 3x its designed capacity. C's liveness probe fails and it restarts too. Describe the cascade failure mechanism, identify the exact design decision that caused it, and propose two independent architectural changes that would prevent this cascade while preserving the benefits of health checks.

**Q2.** You are designing health check endpoints for a microservice that has four dependencies: a PostgreSQL database (required for 100% of requests), a Redis cache (required for 60% of requests, with fallback to DB), a third-party payment API (required for 5% of requests), and an internal recommendation service (optional enrichment). Design the liveness and readiness probe logic for each dependency state, explaining why each dependency should or should not influence each probe type, and what the observable Kubernetes behaviour should be when each dependency fails.

