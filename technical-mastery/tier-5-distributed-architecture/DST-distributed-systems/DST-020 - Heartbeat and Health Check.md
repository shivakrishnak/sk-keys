---
id: DST-020
title: Heartbeat and Health Check
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-008, DST-011, DST-009
used_by: DST-034, DST-038, DST-046
related: DST-011, DST-034, DST-038, DST-046
tags:
  - distributed
  - reliability
  - observability
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/distributed-systems/heartbeat-health-check/
---

⚡ TL;DR - A heartbeat is a periodic signal sent by a node
to indicate it is alive; a health check is a probe sent by
an external observer to verify a node is alive and functional;
both are the foundation of failure detection - without them,
a cluster cannot know which nodes are available to receive
traffic.

---

### 📋 Entry Metadata

| #020 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Node, Fault Tolerance, Message Passing | |
| **Used by:** | Failure Detector, Gossip Protocol, Leader Election | |
| **Related:** | Fault Tolerance, Failure Detector, Gossip Protocol, Leader Election | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A load balancer routes traffic to three backend nodes.
Node B crashes silently. There is no heartbeat or health
check system. The load balancer continues sending 33% of
traffic to Node B. All requests routed to Node B fail with
connection refused. Users experience 33% error rate. The
on-call engineer is paged. The engineer logs in, discovers
Node B is crashed, manually removes it from the load
balancer rotation, restarts it, and adds it back. Duration:
15 minutes. With heartbeat and health checks, the load
balancer detects the failure in 10 seconds and removes
the node automatically.

**THE DETECTION PROBLEM:**
In a distributed system, a failed node does not announce
its failure. It simply stops responding. Other nodes must
detect the failure by the absence of expected signals
(heartbeats) or by actively probing (health checks).
The detection mechanism directly determines: how quickly
failures are detected, how often healthy nodes are falsely
detected as failed, and how the cluster responds.

---

### 📘 Textbook Definition

A **heartbeat** is a periodic message sent by a node to
its peers or to a monitoring system, indicating that the
node is alive and reachable. The recipient expects a
heartbeat within a defined interval; if the interval
expires without a heartbeat, the sender is assumed to have
failed. A **health check** is the inverse: an external
observer (load balancer, service mesh, orchestration system)
sends a probe to a node and evaluates the response to
determine the node's health status. Health checks evaluate:
**liveness** (is the process running and responding?) and
**readiness** (is the process ready to serve traffic?).
The combination of heartbeats and health checks forms the
foundation of **failure detection** - the mechanism that
allows a distributed system to identify and route around
failed components automatically.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A heartbeat says "I'm alive" periodically; a health check
asks "are you alive and ready?" - together they let the
cluster detect and react to failures automatically.

**One analogy:**
> A security guard in a building checks in by radio every
> 30 minutes (heartbeat). If no check-in for 45 minutes,
> dispatch sends someone to verify (health check). If the
> guard does not respond to the verification, dispatch
> assumes an emergency and sends help. The guard system
> works because: normal heartbeats = no action; missed
> heartbeat = escalate to active verification; no response
> to verification = failure declared.

**One insight:**
The critical design parameter is the **detection timeout**:
too short → false positives (healthy nodes declared failed
due to network jitter or GC pauses); too long → slow failure
detection (traffic routes to dead nodes for minutes). The
optimal timeout is specific to the system's network behavior
and the acceptable false positive rate.

---

### 🔩 First Principles Explanation

**HEARTBEAT vs HEALTH CHECK:**

```
┌────────────────────────────────────────────────────────┐
│  HEARTBEAT (node pushes)                               │
│                                                        │
│  Node A ──── [alive!] ──→ Coordinator                  │
│  Node A ──── [alive!] ──→ Coordinator   (every 1s)    │
│  Node A ──── [alive!] ──→ Coordinator                  │
│  ... 10 seconds of silence ...                         │
│  Coordinator: "Node A timeout. Declare failed."        │
│                                                        │
│  HEALTH CHECK (coordinator pulls)                      │
│                                                        │
│  Coordinator ── GET /health ──→ Node A                 │
│  Node A ── 200 OK {status:healthy} ──→ Coordinator     │
│  Coordinator ── GET /health ──→ Node A  (every 5s)    │
│  Node A: [crashed - no response]                       │
│  Coordinator: timeout. Retry 2 more times.             │
│  Coordinator: "Node A failed. Remove from rotation."  │
└────────────────────────────────────────────────────────┘
```

**LIVENESS vs READINESS:**

**Liveness check:** Is the process alive (not crashed)?
If liveness fails: restart the process. A process can be
"live" (running) but stuck in an infinite loop.

**Readiness check:** Is the process ready to serve traffic?
If readiness fails: remove from load balancer rotation
but do NOT restart. A process can be "live" but not "ready"
during startup (loading config), during a dependency failure
(database unreachable), or during high load.

```
┌────────────────────────────────────────────────────────┐
│  KUBERNETES HEALTH CHECK TYPES:                        │
│                                                        │
│  livenessProbe:                                        │
│    What: "Is the container running?"                   │
│    Failure action: RESTART the container               │
│    Example: GET /healthz → 200                         │
│                                                        │
│  readinessProbe:                                       │
│    What: "Can the container serve requests?"           │
│    Failure action: REMOVE from Service endpoints       │
│    (don't send traffic, don't restart)                 │
│    Example: GET /ready → check DB connection           │
│                                                        │
│  startupProbe (Kubernetes 1.16+):                     │
│    What: "Has the application finished starting?"      │
│    Failure action: KILL and restart                    │
│    Disables liveness probe until startup succeeds     │
└────────────────────────────────────────────────────────┘
```

**THE FALSE POSITIVE PROBLEM:**

A slow GC pause can make a node appear failed:
1. Node enters a 5-second GC pause
2. Heartbeat is not sent during the pause
3. Timeout threshold (3 seconds) fires
4. Node declared failed; traffic rerouted
5. GC pause ends; node resumes
6. Two leaders now exist (if this was a leader election
   timeout triggering a new election)

Mitigation strategies:
- Set timeout significantly above max observed GC pause
- Use adaptive failure detectors (Phi Accrual detector)
- Use multiple missed heartbeats before declaring failure
- Combine heartbeat with lease-based leadership to prevent
  split-brain on false positives

---

### 🧠 Mental Model / Analogy

> A health check is like an HTTP API for a node's internal
> state. Instead of asking the node "can you compute X?"
> (which exercises only computation), you ask "are you
> healthy?" - and the node responds with a structured
> assessment: "Yes, my database connection is healthy,
> my memory is at 70%, and I have processed 1000 requests
> in the last minute." This is richer information than
> "process is running" and allows for smarter routing
> decisions (remove from rotation before running out of
> memory rather than after crashing).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Heartbeats are periodic "I'm alive" signals from nodes.
Health checks are "are you alive?" probes from load
balancers. Together they let the system automatically
detect and route around failed nodes without human
intervention.

**Level 2 - How to use it (junior developer):**
Implement a `/health` endpoint in every service that returns
HTTP 200 with a JSON body describing the service's status
(dependencies reachable, disk space, last processed request
time). Configure your load balancer to call this endpoint
every 5 seconds; mark the node as unhealthy after 2
consecutive failures; remove it from rotation.

**Level 3 - How it works (mid-level engineer):**
The load balancer maintains a health state per backend.
Health checks run on a configurable interval. Failures
increment a failure counter. When the counter exceeds
the threshold (e.g., 2 consecutive failures), the backend
is removed from the rotation. Successes decrement the
counter; when it reaches 0, the backend is added back.
Hysteresis (requiring N successes to restore, not just 1)
prevents flapping.

**Level 4 - Why it was designed this way (senior/staff):**
The liveness/readiness separation (popularized by Kubernetes)
was designed because two different failure modes require
different responses. A crashed process requires restart.
A process that is running but cannot serve traffic
(overloaded, dependency failed) must not be restarted
(it would loop-crash). Removing from rotation allows the
process to recover (dependencies become available again)
while preventing new traffic from aggravating the issue.
This separation encodes operational knowledge into the
deployment platform.

**Level 5 - Mastery (distinguished engineer):**
The Phi Accrual failure detector (Hayashibara et al., 2004)
models the heartbeat arrival time distribution and outputs
a "suspicion level" (Phi) rather than a binary alive/dead
decision. As heartbeat intervals grow longer, Phi increases
continuously. The consumer sets a threshold Phi above which
the node is considered failed. This adaptive approach
outperforms fixed-timeout detectors: in stable networks,
the threshold is exceeded quickly; in variable networks,
the detector adapts to avoid false positives. Used by
Cassandra and Akka for their gossip-based failure detection.

---

### ⚙️ Mechanism - Health Check Implementation

**TIERED HEALTH CHECK (shallow to deep):**

```
SHALLOW (process alive):
  GET /ping → 200 OK
  Cost: ~1ms
  What it checks: process is running and responding

STANDARD (dependencies reachable):
  GET /health → {
    "status": "healthy",
    "checks": {
      "database": "ok",
      "cache": "ok",
      "queue": "ok"
    }
  }
  Cost: ~5-50ms (one round-trip per dependency)
  What it checks: process + dependencies are functional

DEEP (business-level sanity):
  GET /ready → {
    "status": "ready",
    "last_processed": "2024-01-15T10:00:01Z",
    "queue_depth": 42,
    "error_rate_1m": 0.001
  }
  Cost: ~10-100ms
  What it checks: service is processing work correctly
  CAUTION: expensive deep checks used too frequently
  can themselves cause load issues
```

**HEARTBEAT TIMEOUT CALCULATION:**

```
Network P99 latency:       10ms
Max GC pause observed:   2000ms
Safety margin (2x):      2x

Recommended timeout:
  = max(2x × P99 latency, 2x × max_GC_pause)
  = max(2x × 10ms, 2x × 2000ms)
  = max(20ms, 4000ms)
  = 4 seconds

Heartbeat interval:  1 second
Declare failed after: 3 missed heartbeats
Effective detection time: ~7 seconds
(3 misses × 1s interval + 4s timeout grace)
```

---

### 💻 Code Example

**Health Check Endpoint (Wrong vs Right)**

```python
# BAD: Shallow liveness-only health check
from fastapi import FastAPI

@app.get("/health")
def health():
    # Always returns 200. Doesn't check anything.
    return {"status": "ok"}

# Problem: Returns 200 even when:
# - Database is unreachable (all queries fail)
# - Queue is full (no messages being processed)
# - Service is out of memory (about to crash)
# Load balancer routes traffic to unhealthy service.
```

```python
# GOOD: Layered health check with liveness vs readiness
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import time

app = FastAPI()

# Liveness: is the process alive?
@app.get("/healthz")
def liveness():
    """
    Simple: just confirm process is responding.
    Kubernetes kills and restarts if this fails.
    Keep it VERY simple: no DB calls here.
    """
    return {"status": "alive", "timestamp": time.time()}

# Readiness: is the process ready for traffic?
@app.get("/ready")
def readiness():
    """
    Check all dependencies.
    Kubernetes removes from Service if this fails.
    Does NOT restart.
    """
    checks = {}
    overall_healthy = True

    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        overall_healthy = False

    # Check cache
    try:
        cache.ping()
        checks["cache"] = "ok"
    except Exception as e:
        checks["cache"] = f"error: {e}"
        # Cache failure is non-critical: warn but stay ready
        checks["cache_warning"] = True

    # Check queue consumer lag
    lag = queue.consumer_lag("my-group", "events")
    checks["queue_lag"] = lag
    if lag > 10000:  # 10k messages behind = unhealthy
        checks["queue"] = "lagging"
        overall_healthy = False
    else:
        checks["queue"] = "ok"

    status_code = (
        status.HTTP_200_OK
        if overall_healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(
        content={"status": "ready" if overall_healthy
                 else "not ready", "checks": checks},
        status_code=status_code
    )
```

**Kubernetes Health Check Configuration**

```yaml
# kubernetes deployment with proper health checks
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: payment-service
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 10   # wait for startup
            periodSeconds: 10         # check every 10s
            failureThreshold: 3       # 3 failures = restart
            timeoutSeconds: 2         # probe timeout

          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5    # start checking sooner
            periodSeconds: 5          # more frequent
            failureThreshold: 2       # 2 failures = no traffic
            successThreshold: 1       # 1 success = add traffic
            timeoutSeconds: 3

          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            failureThreshold: 30      # 30 × 10s = 5 min startup
            periodSeconds: 10
```

---

### ⚖️ Comparison Table

| Approach | Direction | What It Detects | Action on Failure |
|---|---|---|---|
| **Heartbeat** | Node → Monitor | Node stopped sending | Declare node failed |
| **Health Check** | Monitor → Node | Node not responding or unhealthy | Remove from rotation |
| **Liveness Probe** | Monitor → Node | Process unresponsive | Restart process |
| **Readiness Probe** | Monitor → Node | Service not ready for traffic | Remove from load balancing |
| **Gossip Protocol** | Node → Peers | Peer failure (distributed detection) | Update membership list |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A passing health check means the service is healthy" | A shallow health check only confirms the process is running. A deep health check is needed to verify business-level functionality. Many outages involve services that pass health checks while failing all real requests. |
| "The same endpoint for liveness and readiness" | Using the same endpoint loses the distinction. If your database is down, readiness should fail (stop traffic), but liveness should still pass (don't restart - restarting won't fix the database). |
| "Shorter timeout = faster failure detection" | Shorter timeout = more false positives. A process in a GC pause or under high load may appear failed. Balance detection speed against false positive rate. |
| "Health checks don't need to be fast" | A 30-second timeout on a health check that runs every 5 seconds will accumulate and starve the health check thread pool. Health check endpoints must respond in <100ms. |

---

### 🚨 Failure Modes & Diagnosis

**Cascading Failure from Health Check Under Load**

**Symptom:** Service is under high load. Some instances
start failing readiness checks due to high response latency.
Load balancer removes them. More traffic routes to remaining
instances. They also start failing readiness checks. Eventually
all instances are removed from rotation. Complete outage.

**Root Cause:** Readiness check uses the same thread pool
as request processing. Under high load, request threads
are saturated and health check requests time out. The health
check itself triggers the failure it is trying to detect.

**Diagnosis:**
```bash
# Check instance removal events in load balancer logs:
aws elb describe-instance-health \
  --load-balancer-name my-alb \
  --output text | grep OutOfService

# Check health check response time during incident:
grep "GET /ready" access.log | awk '{print $NF}' \
  | sort -n | tail -20
# If times > health check timeout: this is the cause
```

**Fix:**
1. Use separate thread pool for health check endpoints
   (Kotlin: @Scheduled with dedicated executor; Java:
   dedicated HTTP server port for health)
2. Keep health check endpoints extremely lightweight
3. Increase health check timeout to match P99 latency
   under high load (not P50)

---

**False Positive Leader Demotion**

**Symptom:** The database leader is demoted due to heartbeat
timeout. A new leader is elected. The original leader comes
back online. Users report brief data inconsistency (some
data from original leader's final writes appears and
disappears).

**Root Cause:** The leader entered a 3-second GC pause.
The heartbeat timeout (2 seconds) fired. A new leader was
elected. When the GC pause ended, the original leader
rejoined as a follower with unrecognized writes.

**Diagnosis:**
```bash
# Check GC logs for pauses around the time of failover:
grep "GC pause" service.log | grep "2024-01-15 10:30"
# Pause > 2 seconds = false positive timeout

# Check JVM GC metrics:
jstat -gcutil <pid> 1000 10
# Look for "FGC" (full GC) with "FGCT" > timeout threshold
```

**Fix:** Set heartbeat timeout to 5x the P99.9 GC pause
duration. Tune GC to reduce pause duration. Use G1GC
or ZGC (low-pause garbage collectors). Use adaptive
failure detectors that account for GC variability.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Node` - The unit being monitored
- `Fault Tolerance` - The goal that heartbeats and health
  checks serve
- `Message Passing` - The mechanism for sending heartbeats

**Builds On This (learn these next):**
- `Failure Detector` - The formal abstraction that health
  checks implement (completeness and accuracy)
- `Gossip Protocol` - Distributed failure detection
  without a central health monitor
- `Leader Election` - The process triggered when a leader's
  heartbeat times out

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ HEARTBEAT    │ Node sends periodic "I'm alive" signal   │
│              │ Timeout = declare failed                 │
├──────────────┼──────────────────────────────────────────┤
│ HEALTH CHECK │ Monitor probes node, evaluates response  │
│              │ Failure = remove from rotation           │
├──────────────┼──────────────────────────────────────────┤
│ LIVENESS     │ "Is process alive?" → restart if failed  │
│ vs READINESS │ "Can it serve traffic?" → stop routing   │
├──────────────┼──────────────────────────────────────────┤
│ TIMEOUT RULE │ Set timeout > 5x P99.9 GC pause          │
│              │ Too short = false positives              │
│              │ Too long = slow failure detection        │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Same endpoint for liveness + readiness   │
│              │ Deep check in liveness (causes restarts) │
│              │ Health check uses request thread pool    │
├──────────────┼──────────────────────────────────────────┤
│ GOOD PRACTICE│ /healthz: ultra-lightweight liveness     │
│              │ /ready: check dependencies, return 503   │
│              │   if any critical dep is unreachable     │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Liveness: am I alive? Readiness: am I   │
│              │  ready to help? Both needed, different   │
│              │  failure responses."                     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Failure Detector → Gossip Protocol →     │
│              │ Leader Election                          │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The liveness vs readiness distinction is a general principle:
different failure modes require different responses. "Is
the system alive?" and "Is the system ready for work?" are
different questions. Conflating them leads to restarts
when what you need is traffic shaping, or traffic shaping
when what you need is a restart. This distinction applies
in: microservice health checks, connection pool management
(is the connection alive? vs is a connection available
in the pool?), and worker processes (is the worker alive?
vs is the worker ready for the next job?).

---

### 💡 The Surprising Truth

Amazon's EC2 instance health checks run continuously, and
unhealthy instances are automatically replaced. But Amazon
discovered a subtle failure mode: EC2 instances can pass
health checks while being in a "degraded" state where
they process requests slowly (10x normal latency). The
instance is "alive" and "responding to health checks" but
terrible for users. This led to the introduction of
"enhanced health reporting" in Elastic Beanstalk, which
reports HTTP 2xx rate AND latency as health metrics - not
just "did the health check endpoint respond." The lesson:
a health check that only measures "did it respond?" is
insufficient. Health checks should measure "did it respond
well?" - incorporating latency, error rate, and resource
utilization into the health signal.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [IMPLEMENT] Build a production-grade readiness check
   for a service with database, cache, and queue
   dependencies, distinguishing critical vs non-critical
   dependency failures.
2. [CONFIGURE] Set Kubernetes liveness, readiness, and
   startup probes with appropriate timeouts for a service
   that takes 30 seconds to start and has occasional
   5-second GC pauses.
3. [DEBUG] A service is experiencing periodic traffic
   drops with no error rate increase. Diagnose whether
   this is caused by readiness probe failures due to
   high-latency health check responses.
4. [EXPLAIN] Why using the same endpoint for liveness
   and readiness is dangerous, using a concrete example
   of the failure mode it introduces.
5. [DESIGN] Design a health check strategy for a batch
   processing service that: starts slowly (5 minutes),
   processes messages for 1 hour, and then shuts down.
   The service should not receive traffic until ready
   and should drain gracefully on shutdown.
