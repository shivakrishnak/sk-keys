---
id: MSV-009
title: Readiness and Liveness Probes
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-008, MSV-002
used_by: MSV-014, MSV-023, MSV-067
related: MSV-008, MSV-069, MSV-023, MSV-067
tags:
  - microservices
  - kubernetes
  - intermediate
  - reliability
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /microservices/readiness-and-liveness-probes/
---

# MSV-009 - Readiness and Liveness Probes

⚡ TL;DR - Readiness and Liveness Probes are Kubernetes
mechanisms that gate traffic routing (readiness) and trigger
pod restarts (liveness) based on service health signals.
Misconfiguring them causes crash loops or traffic to dead pods.

| #009 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Health Check Patterns, Microservices Architecture | |
| **Used by:** | Load Balancing in Microservices, Blue-Green Deployment, Canary Deployment | |
| **Related:** | Health Check Patterns, Graceful Shutdown, Blue-Green Deployment, Canary Deployment | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In Kubernetes, without probes, a pod is considered ready
the moment its container starts. The container starts in
500ms. But the JVM takes 15 seconds to initialise, and the
Spring context takes another 20 seconds. Kubernetes adds
the pod to the load balancer endpoint list at 500ms. For
the next 35 seconds, requests hit a pod that returns
connection refused or 503. During rolling deployments,
every new pod causes a burst of errors until warmed up.

**THE BREAKING POINT:**
Container started != service ready. In a containerised
microservices architecture, these two events are decoupled
by potentially minutes. Without probes, the platform has
no way to know when a pod transitions from "container
started" to "ready to serve traffic". The result: user-facing
errors on every deployment.

**THE INVENTION MOMENT:**
Kubernetes probes are the explicit contract between the service
and the scheduler: "I will tell you when I am ready, when
I am broken, and when I am still starting up - act accordingly."

---

### 📘 Textbook Definition

**Kubernetes Probes** are periodic health checks configured
on a pod's containers that the kubelet executes to determine
the container's operational state. There are three types:

1. **Liveness Probe** - detects if the container is alive.
   Failure causes the kubelet to kill and restart the
   container. Answers: "Is this container stuck?"

2. **Readiness Probe** - detects if the container is ready
   to serve requests. Failure removes the pod from the
   Service endpoints (no traffic). Answers: "Should I route
   traffic here?"

3. **Startup Probe** - protects slow-starting containers from
   liveness probe failures. Gates liveness and readiness until
   startup completes. Answers: "Has this container finished
   starting up?"

Probes support three check mechanisms: `httpGet` (HTTP
endpoint), `tcpSocket` (TCP port open?), and `exec`
(shell command exit code).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Liveness probe = "is this pod broken? (restart it)".
Readiness probe = "is this pod ready to handle requests?
(route traffic to it)".

**One analogy:**
> A new employee (pod) starting a job (deployment):
> Startup probe: "Are you done with onboarding?" (wait)
> Readiness probe: "Are you ready to take customer calls?"
> (route work to them only when YES)
> Liveness probe: "Are you still at your desk and responsive?"
> (if no answer for 3 checks, assume they left - assign someone new)

**One insight:**
Startup probe unlocks the rest: without it, a JVM that takes
60 seconds to start will fail liveness probes and be
restarted in a loop. Startup probe says "be patient during
startup, but still restart if the process hangs indefinitely."

---

### 🔩 First Principles Explanation

**PROBE EXECUTION MODEL:**
The kubelet runs on every node. It polls each configured probe
according to `periodSeconds`. The probe either passes (HTTP 2xx,
TCP connect, command exit 0) or fails. After `failureThreshold`
consecutive failures, the action triggers (restart or endpoint
removal). After `successThreshold` consecutive passes, the
action reverts (pod re-added to endpoints for readiness; no
revert for liveness since it was already restarted).

**TIMING PARAMETERS:**
```
initialDelaySeconds: wait before first probe (default: 0)
periodSeconds:       how often to probe (default: 10s)
timeoutSeconds:      max wait for response (default: 1s)
failureThreshold:    consecutive failures before action
successThreshold:    consecutive successes before recovery
```

**THE DESIGN TENSION:**
Too aggressive: small failureThreshold + short period = probe
failures during minor load spikes cause unnecessary restarts
or temporary endpoint removal. Under load, your probe's DB query
times out → false readiness failure → pod removed during
a traffic spike (exactly when you need it most).
Too lenient: large failureThreshold + long period = a genuinely
dead pod stays in rotation for minutes, degrading user experience.

---

### 🧪 Thought Experiment

**SETUP:**
Order Service has only a liveness probe (no startup probe,
no readiness probe). Startup takes 45 seconds.
`livenessProbe.initialDelaySeconds=10`. 
`livenessProbe.failureThreshold=3`. `periodSeconds=10`.

**TRACE:**
- 0s: container starts
- 10s: first liveness probe. Service not ready → 503 → FAIL 1
- 20s: second liveness probe. Service not ready → 503 → FAIL 2
- 30s: third liveness probe. Service not ready → 503 → FAIL 3
- 30s: kubelet restarts the container (3 consecutive failures)
- 30s: container starts again
- REPEAT FOREVER: service never gets 45 seconds to start

**FIX: Add startup probe**
```yaml
startupProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  failureThreshold: 18  # 18 x 5s = 90s max startup time
  periodSeconds: 5
# Liveness probe only activates after startup probe succeeds
livenessProbe:
  initialDelaySeconds: 0  # startup probe already handled it
```

---

### 🧠 Mental Model / Analogy

> Probes are like the three traffic lights of a pod's lifecycle:
> - Red (not started): startup probe - "not ready yet, wait"
> - Yellow (started, not ready): readiness failing - "running
>   but don't send me traffic yet"
> - Green (live and ready): both probes pass - "send traffic"
> - Flashing red (liveness failed): "broken, needs restart"

The four states and their transitions:
```
STARTING → startup probe fails → stays STARTING (wait)
STARTING → startup probe passes → becomes RUNNING
RUNNING  → readiness probe fails → RUNNING but no traffic
RUNNING  → liveness probe fails 3x → RESTARTING
RUNNING  → readiness probe passes → traffic resumes
```

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Readiness probe: "Am I ready to take requests?" - if NO,
no traffic. Liveness probe: "Am I still alive?" - if NO,
Kubernetes restarts the pod. Startup probe: "Am I still
starting up?" - if YES, be patient with the others.

**Level 2 - How to use it (junior developer):**
Configure in the Deployment spec under `containers`:
```yaml
livenessProbe:
  httpGet: {path: /actuator/health/liveness, port: 8080}
  initialDelaySeconds: 60
readinessProbe:
  httpGet: {path: /actuator/health/readiness, port: 8080}
  initialDelaySeconds: 30
```

**Level 3 - How it works (mid-level engineer):**
The kubelet checks `livenessProbe` and `readinessProbe`
independently. Failed readiness removes the pod from the
`Endpoints` object for all Services that select it. The
kube-proxy watches Endpoints and updates iptables/IPVS rules.
Traffic stops routing to the pod within 1-2 seconds. Failed
liveness increments a counter; at `failureThreshold`, the
kubelet sends SIGTERM to the container and restarts it.

**Level 4 - Why it was designed this way (senior/staff):**
The probe mechanism was designed to be language-agnostic
and non-invasive. `httpGet` works for any HTTP server.
`tcpSocket` works for non-HTTP protocols. `exec` works for
any process that can return an exit code. The kubelet handles
the probe scheduling outside the application code - no SDK
required. This is deliberate: health checking is platform
responsibility, not application responsibility.

**Level 5 - Mastery (distinguished engineer):**
Probes interact with PodDisruptionBudgets (PDB). A PDB ensures
a minimum number of pods remain ready during voluntary
disruptions. If a probe causes too many pods to be in a
non-ready state simultaneously, node drains and rolling
updates will be blocked. At scale, misconfigured probes
interacting with PDBs can halt deployments completely. Staff
engineers design probe configurations holistically with PDBs
and `maxUnavailable` rolling update settings.

---

### ⚙️ How It Works (Mechanism)

**KUBELET PROBE LOOP:**

```
For each container with probes configured:
  every periodSeconds:
    execute probe (httpGet/tcpSocket/exec)

    if probe returns SUCCESS:
      consecutiveSuccesses++
      consecutiveFailures = 0
      if consecutiveSuccesses >= successThreshold:
        mark ready (readiness) or continue (liveness)

    if probe returns FAILURE:
      consecutiveFailures++
      consecutiveSuccesses = 0
      if consecutiveFailures >= failureThreshold:
        for readiness: remove pod from Endpoints
        for liveness: kill container, increment restartCount
        for startup: kill container (if threshold exceeded)
```

**ENDPOINTS UPDATE PROPAGATION:**
```
Readiness probe fails (pod removed from Endpoints)
  → kube-proxy watches Endpoints API (every 1s)
  → kube-proxy updates iptables rules
  → iptables: remove DNAT rule for this pod IP
  → New connections no longer route to the pod
  → Existing connections (TCP) finish naturally
  
Total propagation time: ~1-3 seconds
```

**STARTUP PROBE INTERACTION:**
```
Startup probe configured:
  → liveness probe DISABLED until startup probe passes
  → readiness probe DISABLED until startup probe passes
  → failureThreshold * periodSeconds = max startup time
  
After startup probe passes:
  → startup probe DISABLED
  → liveness + readiness probes ENABLED
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ZERO-DOWNTIME ROLLING DEPLOYMENT:**

```
Rolling update begins: maxSurge=1, maxUnavailable=0
  │
  ▼
New pod created (replicas: 3 → 4)
  │
  ▼
Startup probe: polls /actuator/health/liveness every 5s
  │ Returns 503 for 30s (JVM + Spring context loading)
  │ After 35s: returns 200 → startup probe passes
  ▼
Readiness probe activates: polls /actuator/health/readiness
  │ Returns 200 (DB connection established)
  ▼
Kubernetes: adds new pod to Endpoints
  │
  ▼
Traffic now routed to all 4 pods (old 3 + new 1)
  │
  ▼
Old pod 1: readiness probe returns REFUSING_TRAFFIC
  │ (Spring Boot sets this on SIGTERM)
  ▼
Kubernetes: removes old pod 1 from Endpoints
  │ preStop hook: waits 15s for in-flight requests
  ▼
Old pod 1: graceful shutdown completes
  │
  ▼
Repeat for pods 2 and 3
  → Zero dropped requests throughout
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: probe misconfiguration**

```yaml
# BAD: no startup probe, aggressive liveness
# JVM takes 45s to start. After 30s (3x10s), liveness
# fails → restart → infinite loop. Service never starts.
containers:
  - name: order-service
    livenessProbe:
      httpGet:
        path: /actuator/health
        port: 8080
      initialDelaySeconds: 10  # too short for JVM
      periodSeconds: 10
      failureThreshold: 3
    # NO readinessProbe: traffic hits pod before it's ready
    # NO startupProbe: liveness kills pod during startup
```

```yaml
# GOOD: startup probe gates others, separate readiness
containers:
  - name: order-service
    startupProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      failureThreshold: 18  # 18 x 5s = 90s max startup
      periodSeconds: 5
      timeoutSeconds: 3
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      periodSeconds: 5
      failureThreshold: 3
      successThreshold: 1
    livenessProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      periodSeconds: 10
      failureThreshold: 3
      timeoutSeconds: 3
```

**Spring Boot application.yml configuration:**

```yaml
# Enable separate readiness and liveness health groups
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        readiness:
          include: db,redis,diskSpace
        liveness:
          include: ping  # internal only
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
server:
  shutdown: graceful  # CRITICAL for zero-downtime deploys

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # drain window
```

---

### ⚖️ Comparison Table

| Probe | Failure Action | Check Frequency | Ext. Deps | Failure Risk |
|---|---|---|---|---|
| **Startup** | Restart (if max exceeded) | Aggressive OK (startup only) | Yes (init check) | None if threshold is high enough |
| **Readiness** | Remove from LB | Every 5-10s | Yes | False positive during load |
| **Liveness** | Restart container | Every 10-30s | Never | Restart loop if ext. deps included |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| initialDelaySeconds is sufficient instead of startup probe | initialDelaySeconds is static - slow machines miss it. Startup probe is dynamic - waits until startup actually succeeds, regardless of time. |
| Readiness and liveness can share the same endpoint | They can technically, but shouldn't. Sharing means a DB outage (readiness concern) also triggers pod restart (liveness action). |
| Setting very long failureThreshold on liveness is safe | A liveness probe that never fires is useless. Liveness is for genuine deadlocks/hangs. If you never want a restart, remove the liveness probe. |

---

### 🚨 Failure Modes & Diagnosis

**Traffic errors during rolling deployment**

**Symptom:**
5-10 seconds of 503 errors from the application every time
a new pod starts during a rolling deployment, even with
readiness probes configured.

**Root Cause:**
Two potential causes:
1. `initialDelaySeconds` too short - probe fires before
   service is ready, pod added to endpoints prematurely
2. iptables propagation lag - pod added to Endpoints, then
   iptables rules on some nodes take 2-3 seconds to update,
   during which some nodes still route to the old pod

**Diagnostic Command:**
```bash
# Watch pod readiness transitions
kubectl get pods -w -l app=order-service

# Check endpoint update timing
kubectl get endpoints order-service -w

# Check probe events
kubectl describe pod order-service-xxx | \
  grep -A5 "Readiness\|Liveness"
```

**Fix:**
If cause 1: increase `initialDelaySeconds` or use startup
probe. If cause 2: add `minReadySeconds: 10` to the Deployment
spec - pod is not considered "available" for rolling updates
until it has been ready for 10 consecutive seconds.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Health Check Patterns` - the conceptual foundation of
  what probes implement in Kubernetes

**Builds On This (learn these next):**
- `Blue-Green Deployment` - relies on readiness probes to
  switch traffic between old and new versions
- `Graceful Shutdown` - what happens to in-flight requests
  when readiness fails during pod termination

**Alternatives / Comparisons:**
- `Service Mesh (Istio)` - can inject health checking and
  traffic control via sidecar, complementing Kubernetes probes
- `Circuit Breaker` - caller-side failure detection vs probe-
  based server-side health reporting

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STARTUP      │ failureThreshold*periodSeconds = max      │
│              │ startup window. Gates liveness+readiness  │
├──────────────┼───────────────────────────────────────────┤
│ READINESS    │ Failure → removed from Service endpoints  │
│              │ Success → re-added to endpoints           │
├──────────────┼───────────────────────────────────────────┤
│ LIVENESS     │ failureThreshold failures → container     │
│              │ restart (SIGTERM then SIGKILL)            │
├──────────────┼───────────────────────────────────────────┤
│ GOLDEN RULE  │ Liveness: NEVER check external deps       │
│              │ Use startup probe for slow JVM startups   │
├──────────────┼───────────────────────────────────────────┤
│ ZERO-DOWN    │ server.shutdown=graceful + preStop hook   │
│ DEPLOY       │ + readiness REFUSING_TRAFFIC on SIGTERM   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Startup: be patient. Readiness: route    │
│              │  here? Liveness: restart this?"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Health Check Patterns → Graceful Shutdown │
│              │ → Blue-Green Deployment                   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always add a startup probe for JVM services - without it,
   liveness kills the pod before it finishes starting.
2. `server.shutdown=graceful` in Spring Boot enables zero-
   downtime rolling deploys by marking not-ready on SIGTERM.
3. The `failureThreshold * periodSeconds` calculation
   determines the maximum window for each probe - design
   these deliberately, not with defaults.

**Interview one-liner:**
"Readiness probes gate traffic routing - failure removes
the pod from Kubernetes Service endpoints. Liveness probes
gate container health - failure restarts the container.
Startup probes protect slow-starting containers from liveness
killing them before they finish booting. The most dangerous
mistake is putting external dependency checks in liveness,
which causes restart loops when dependencies are slow."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
In any system with dynamic membership, the mechanism to add
a member to the pool (readiness) must be separate from the
mechanism to remove a broken member (liveness). These are
different state machines with different triggers. Conflating
them causes both over-removal (availability problems) and
under-removal (reliability problems).

**Where else this pattern appears:**
- Load balancer health checks: AWS target group health check
  vs unhealthy threshold = readiness vs liveness equivalent
- Database connection pool validation: `testOnBorrow`
  (readiness - is this connection healthy before using it?)
  vs pool shrink timeout (liveness - has this idle connection
  been dead too long?)

---

### 💡 The Surprising Truth

Kubernetes does not guarantee that in-flight requests complete
before a pod's endpoint is removed. When readiness fails,
the endpoint is removed from the list, preventing new connections.
But existing TCP connections (including those using HTTP keep-alive)
remain open and continue to route requests to the pod. A service
must implement its own graceful drain - completing in-flight
requests within the `terminationGracePeriodSeconds` window -
because Kubernetes only handles the routing layer. The
`preStop` lifecycle hook, combined with `server.shutdown=graceful`,
is the correct mechanism to bridge this gap. Without it, a
pod that passes the readiness check but is receiving a SIGTERM
will silently drop requests that were in-flight on existing
keep-alive connections.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Walk through the complete pod startup sequence
   with all three probe types configured, and describe exactly
   when traffic begins routing to the new pod.
2. **DEBUG** Given a deployment that shows 5-10 seconds of
   503 errors on each rollout, identify the three possible
   root causes and the diagnostic steps to distinguish them.
3. **DESIGN** Design a complete probe configuration for a
   Spring Boot service with a 45-second startup time, a
   critical DB dependency, and a Redis dependency that can
   degrade gracefully.
4. **CALCULATE** Given `failureThreshold=3`, `periodSeconds=10`,
   and `timeoutSeconds=3`, calculate: the maximum time from
   a genuine failure to container restart, and the maximum
   time from an unreachable liveness endpoint to restart.
5. **EXTEND** Design a probe strategy for a batch-processing
   service that is intentionally "not ready" while processing
   (to prevent additional work being assigned) but should not
   be restarted during processing. How do you prevent liveness
   from triggering during a 20-minute batch job?

---

### 🧠 Think About This Before We Continue

**Q1.** A service processes requests via a 10-thread
executor. The readiness probe checks if the executor has
any available threads: if `activeThreads >= maxThreads`,
return NOT_READY. At peak load, all 10 threads are in use
for 30 seconds. `failureThreshold=3`, `periodSeconds=5`.
Trace what happens to routing during this 30-second period.
Is this the correct use of readiness probes? What is the
alternative?

**Q2.** Your team is deploying to a cluster with 100 pods
of a service. `maxUnavailable=10%` (10 pods). The readiness
probe has `failureThreshold=3` and `periodSeconds=5`.
An external dependency goes down for 60 seconds. How many
pods get removed from endpoints? What is the traffic impact?
Does the deployment halt? How does `minReadySeconds` factor in?

**Q3.** You need to support canary deployment: 5% of traffic
to v2, 95% to v1. Both v1 and v2 use Kubernetes readiness
probes. The canary deployment uses a separate Deployment object
with 1 pod (v2) alongside 19 pods (v1). What is wrong with
using only Kubernetes readiness probes for this traffic split?
What additional tool is required for precise 5/95 traffic
splitting? (Hint: explore Istio VirtualService or NGINX
Ingress weighted routing.)