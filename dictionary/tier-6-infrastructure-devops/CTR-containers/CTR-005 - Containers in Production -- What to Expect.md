---
id: CTR-005
title: Containers in Production - What to Expect
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★☆☆
depends_on: CTR-001, CTR-002, CTR-003
used_by: CTR-027
related: CTR-003, CTR-027, CTR-028
tags:
  - containers
  - production
  - foundational
  - bestpractice
  - reliability
status: complete
version: 2
layout: default
parent: "Containers"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /containers/containers-in-production-what-to-expect/
---

# CTR-005 - Containers in Production - What to Expect

⚡ **TL;DR -** Production containers require orchestration, health checks,
resource limits, logging, security hardening, and image lifecycle management
that local development never demands.

| | |
|---|---|
| **Depends on** | CTR-001, CTR-002, CTR-003 |
| **Used by** | CTR-027 |
| **Related** | CTR-003, CTR-027, CTR-028 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A developer successfully runs their app in a Docker
container locally. They tell their manager "it's containerised - just run
`docker run`!" Six weeks later the container crashes at 3 AM. Nobody notices
for four hours because there is no health check. When it restarts, it tries
to write logs to the container filesystem, which is full. The logs expose
a database connection string. Half the team didn't know containers needed
persistent storage configuration.

**THE BREAKING POINT:** Local development containers and production
containers are fundamentally different contexts. Locally you restart
manually, logs print to a terminal, resources are generous, security
is relaxed, and availability doesn't matter. Production demands the
opposite on every dimension.

**THE INVENTION MOMENT:** The operational patterns for production containers
emerged from Kubernetes, Docker Swarm, and early container-at-scale adopters
(Google, Netflix, Twitter) between 2014-2017. They codified: containers must
be ephemeral, health-checked, resource-limited, log-to-stdout, and run as
non-root. These are not optional best practices - they are requirements for
reliable container operations.

**EVOLUTION:** Early Docker production use (2014-2016): ad-hoc `docker run`
on single servers with upstart/systemd restart scripts. 2016-2018: Docker
Compose and Swarm for multi-container coordination. 2018+: Kubernetes becomes
the dominant production pattern. 2020+: Security hardening (non-root,
distroless, seccomp, SBOM) and supply-chain requirements added by regulated
industries and cloud providers. Today: GitOps (ArgoCD, Flux) automates the
full image-to-production promotion pipeline.

---

### 📘 Textbook Definition

**Containers in production** refers to the operational requirements and
architectural patterns for running OCI container images in environments
where availability, security, resource efficiency, and observability are
mandatory. Production containers must be: orchestrated (scheduled and
managed by a platform like Kubernetes), ephemeral (stateless; state in
external stores), resource-limited (CPU/memory via cgroups), health-checked
(liveness/readiness probes), observable (structured logs to stdout, metrics
via sidecar or SDK), hardened (non-root, read-only FS, minimal image,
scanned), and immutably deployed (new image per release, never patched in place).

---

### ⏱️ Understand It in 30 Seconds

**One line:** A container in production is not just `docker run` - it needs
orchestration, limits, health checks, logging, and security from day one.

> A container in local dev is like a prototype car in a garage: you can
> tweak it freely, restart it manually, and the stakes are low. A container
> in production is a car on a motorway at 100 mph: it needs seat belts,
> crash sensors, GPS, fuel gauges, and a roadside recovery plan before
> you put it on the road.

**One insight:** Every container will eventually fail. Production readiness
means designing for failure recovery, not failure prevention.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Containers are ephemeral - they will be stopped, killed, and replaced
2. State must live outside the container (database, object storage, volumes)
3. Health must be self-reported (health endpoints) not externally guessed
4. Resource consumption must be bounded or containers become noisy neighbours

**DERIVED DESIGN:** Because containers are ephemeral, they must be stateless.
Because they run in shared environments (many on one host), they must have
resource limits. Because they fail, they must expose health status so the
orchestrator can replace them. Because their filesystem is ephemeral, logs
must go to stdout (captured by the runtime) not to files.

**THE TRADE-OFFS:**
**Gain:** Horizontal scalability; zero-downtime deploys; automated recovery;
infrastructure-as-code deployment.
**Cost:** Operational complexity (need an orchestrator); state management
is harder (external persistence required); debugging requires new skills
(ephemeral filesystem, distributed logs).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Ephemeral processes with external state, health signalling,
and resource isolation are inherent in multi-tenant, highly available systems.
**Accidental:** YAML configuration verbosity, kubectl command learning curve,
and Helm chart complexity are implementation details of Kubernetes, not
inherent to production containerisation.

---

### 🧪 Thought Experiment

**SETUP:** You deploy a Java Spring Boot service as a container to production.
You don't set resource limits, health checks, or external logging.

**WHAT HAPPENS:** A memory leak causes the container's heap to grow. It
consumes all available RAM on the host. The host becomes unresponsive. The
Kubernetes node goes NotReady. All other containers on the node are evicted.
The Spring Boot container keeps logging to its filesystem. The filesystem
fills (Docker's default layer size is unbounded). No alerting fires because
there are no metrics or health checks configured. Incident duration: 4+ hours.

**WHAT HAPPENS WITH PRODUCTION PATTERNS:** The container has `-memory=512Mi`.
The cgroup OOM killer terminates the container. Kubernetes detects the
termination, restarts the container (liveness probe), and the alerting fires
on OOMKilled events. RCA is clear from the structured logs (in Loki/ELK).
The incident is self-healing in 30 seconds; post-mortem finds the memory leak.

**THE INSIGHT:** Production container patterns are not "nice to have" - they
are the mechanism by which containers self-heal and the platform remains
stable under failure conditions.

---

### 🧠 Mental Model / Analogy

> A production container is like an employee in a large company. The company
> (orchestrator) assigns them a workspace (compute), gives them a budget
> (resource limits), checks they are healthy each morning (health probes),
> and trains a replacement if they leave (restart policy). Logs go to the
> company's central archive (stdout → centralised logging), not in the
> employee's personal drawer (container filesystem).

- **Orchestrator** → HR + management system (assigns, monitors, replaces)
- **Resource limits** → the office floor space and equipment budget allocated
- **Health checks** → the daily check-in system
- **Stdout logging** → messages go to company records, not personal files
- **External state** → the company's shared file server (not the employee's desk)

Where this analogy breaks down: Unlike employees, containers can be
instantiated thousands of times simultaneously with identical configuration.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Running a container in production is like publishing an app to the app store
instead of just using it yourself. You need to think about what happens when
it crashes, how people find it, how it gets updated, and who can access what.

**Level 2 - How to use it (junior developer):**
For production: set a `--memory` and `--cpu` limit. Add a `HEALTHCHECK` in
your `Dockerfile`. Log with `System.out.println` or structured logger to
stdout. Never write to the container filesystem for persistent data - use
a database or mounted volume. Use an orchestrator (Kubernetes or ECS) to
manage replicas and restarts.

**Level 3 - How it works (mid-level engineer):**
Kubernetes runs your container by fetching the image, creating a pod spec
that defines resource `requests` and `limits`, `livenessProbe` and
`readinessProbe`, environment variables (from `ConfigMap` and `Secret`), and
volume mounts (for persistent state). Liveness probes send HTTP GET or exec
commands; if they fail N times, Kubernetes restarts the container. Readiness
probes gate traffic routing - unhealthy pods are removed from the load
balancer while remaining running. Resource limits via cgroups prevent one
container from starving others. The container's stdout is captured by the
kubelet and forwarded to the log aggregation system.

**Level 4 - Why it was designed this way (senior/staff):**
The ephemeral container pattern is a consequence of the CAP theorem applied
to compute units: for a distributed system to tolerate node failures and
enable horizontal scaling, compute must be stateless and replaceable. The
"12-factor app" methodology (Heroku, 2012) codified this before Kubernetes
existed. Kubernetes operationalised it as pod specs. The decision to route
logs via stdout (not files) was pragmatic: the orchestrator knows the
container's PID and can attach to its stdio streams, but it cannot reliably
access the container's filesystem (it may be ephemeral overlay FS). This
stdout convention also enables uniform log handling across all runtimes.

**Expert Thinking Cues:**
- "Production-ready" is a spectrum, not a binary. Prioritise: resource limits
  and health checks first (prevents host instability); then logging and
  metrics (observability); then security hardening.
- Pod `requests` (Kubernetes) affect scheduling; `limits` affect runtime
  enforcement. A pod with no `requests` will be scheduled onto any node and
  can starve others. A pod with no `limits` can consume unbounded resources.

---

### ⚙️ How It Works (Mechanism)

**PRODUCTION CONTAINER REQUIREMENTS MAP:**

```
┌─────────────────────────────────────────────┐
│  SECURITY          OBSERVABILITY            │
│  Non-root user     Stdout logging           │
│  Read-only FS      Health endpoints         │
│  Scanned image     Metrics (Prometheus)     │
│  Minimal base      Tracing (OTEL)           │
├─────────────────────────────────────────────┤
│  RELIABILITY       RESOURCE MANAGEMENT      │
│  Liveness probe    CPU requests + limits    │
│  Readiness probe   Memory requests + limits │
│  Graceful shutdown PodDisruptionBudget      │
│  Restart policy    HPA (autoscaling)        │
├─────────────────────────────────────────────┤
│  STATE             DEPLOYMENT               │
│  External DB       Immutable image per ver  │
│  External cache    Rolling update strategy  │
│  Volume mounts     Rollback capability      │
└─────────────────────────────────────────────┘
```

**KUBERNETES POD SPEC ESSENTIALS:**
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  periodSeconds: 5
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
New image built + scanned
         │
         ▼
CD pipeline triggers deploy  ← YOU ARE HERE
         │
         ▼
Kubernetes rolling update
  Old pod: traffic drained
  New pod: scheduled + started
  New pod: readiness probe passes
  New pod: enters load balancer
         │
         ▼
Old pod terminated
(SIGTERM → graceful shutdown → SIGKILL)
         │
         ▼
New version serving traffic
```

**FAILURE PATH:**
- Liveness probe fails → container restarted; `kubectl describe pod`
- Readiness probe fails → removed from service; `kubectl get endpoints`
- OOM kill → `kubectl get events | grep OOMKilled`; increase memory limit
- Image pull error → check registry auth; `kubectl describe pod`
- CrashLoopBackOff → inspect logs; `kubectl logs --previous`

**WHAT CHANGES AT SCALE:**
At 1,000 pods, health probe traffic itself becomes significant (adjust period
and timeout). Rolling updates need PodDisruptionBudgets to prevent all pods
being updated simultaneously. Log volume requires structured logging with
sampling for high-frequency events. HPA (Horizontal Pod Autoscaler) requires
custom metrics for effective scaling.

---

### ⚖️ Comparison Table

| Concern | Local Dev Container | Production Container |
|---------|-------------------|---------------------|
| Restart on crash | Manual | Automatic (liveness probe) |
| Resource limits | None | CPU + memory limits |
| Logging | Terminal stdout | Centralised (ELK/Loki) |
| Health checks | None | Liveness + readiness probes |
| State persistence | Container FS | External DB/volumes |
| Security | Run as root OK | Non-root, read-only FS |
| Image tags | `latest` | Exact version/digest |
| Replicas | 1 | 2+ (HA) |
| Graceful shutdown | Kill -9 OK | SIGTERM → drain → exit |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "The container handles its own restarts" | Containers don't restart themselves. The orchestrator (Kubernetes, ECS) restarts them based on health probes. |
| "Logs are in the container" | Container filesystems are ephemeral. Logs must go to stdout to be captured by the runtime and forwarded to a persistent store. |
| "Setting no resource limits is safer (lets it use what it needs)" | No limits = one container can starve the entire host. Limits protect neighbours and trigger predictable OOM recovery. |
| "image:latest is fine for production" | `latest` is a mutable tag - the image it points to can change. Production must pin to an exact digest or immutable tag. |
| "The container is stateful if we write to /data inside it" | That data is lost when the container restarts. Persistent state must use mounted volumes backed by a storage class. |

---

### 🚨 Failure Modes & Diagnosis

**1. CrashLoopBackOff - Container Keeps Restarting**

**Symptom:** Pod status is `CrashLoopBackOff`; app unavailable.
**Root Cause:** Container exits immediately after start (missing env var,
startup error, OOM).
**Diagnostic:**
```bash
kubectl describe pod <name>
kubectl logs <name> --previous
kubectl get events --sort-by='.lastTimestamp' | tail -20
```
**Fix:** Identify the crash cause from previous logs. Common causes: missing
config env var, OOM, bad entrypoint.
**Prevention:** Validate all required env vars at app startup and exit with
a descriptive error message.

---

**2. OOMKilled - Container Hits Memory Limit**

**Symptom:** Pod restarts periodically; `kubectl describe pod` shows
`OOMKilled` in last state.
**Root Cause:** Container exceeds its memory `limit` - kernel OOM killer
terminates it.
**Diagnostic:**
```bash
kubectl describe pod <name> | grep -A3 "Last State"
# OOMKilled exit code 137
kubectl top pod <name>   # live memory usage
```
**Fix:** Increase memory limit or fix the memory leak. Use a Java heap
dump or Go pprof for leak analysis.
**Prevention:** Set limits 20-30% above expected peak; add memory usage
alerting at 80% of limit.

---

**3. Security - Container Running as Root in Production**

**Symptom:** Security audit: "containers running as root in production
cluster"; compliance fail.
**Root Cause:** No `USER` instruction in `Dockerfile`; no Pod Security
Standards enforced.
**Diagnostic:**
```bash
kubectl exec <pod> -- id
# uid=0(root) - BAD
kubectl get psp,psa  # check admission policies
```
**Fix:** Add `USER nonroot` to `Dockerfile`; enforce `restricted`
PodSecurityAdmission in namespace.
**Prevention:** Enforce `runAsNonRoot: true` in security context at the
namespace level via OPA Gatekeeper or Kyverno.

---

**4. Graceful Shutdown Failure - Lost In-Flight Requests**

**Symptom:** HTTP 5xx spike during rolling updates; some requests fail.
**Root Cause:** Container receives SIGTERM but doesn't drain in-flight
requests before exiting.
**Diagnostic:**
```bash
kubectl describe pod <name> | grep "terminationGracePeriodSeconds"
# check if too short
```
**Fix:** Handle SIGTERM in app code to stop accepting new requests,
complete in-flight ones, then exit. Set `terminationGracePeriodSeconds`
to 60+ seconds for long-lived requests.
**Prevention:** Load test rolling updates to verify zero 5xx before
deploying to production.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `[[CTR-001 - What Is Containerization and Why It Matters]]`
- `[[CTR-002 - VMs vs Containers - A Mental Model]]`
- `[[CTR-003 - The Container Ecosystem Map]]`

**Builds On This (learn these next):**
- `[[CTR-027 - Container Orchestration]]` - how orchestrators manage containers
- `[[CTR-028 - Container Resource Limits]]` - CPU and memory limits in depth
- `[[CTR-017 - Container Health Check]]` - liveness/readiness probes
- `[[CTR-030 - Container Logging]]` - stdout logging patterns
- `[[CTR-035 - Container Security]]` - production security hardening

**Alternatives / Comparisons:**
- AWS ECS - managed container orchestration alternative to Kubernetes
- AWS Fargate - serverless containers (no node management)
- Docker Swarm - simpler orchestrator (deprecated at most orgs)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────┐
│ WHAT IT IS    Operational requirements for   │
│               containers in live production  │
│ PROBLEM       Dev containers lack limits,    │
│               health checks, security,       │
│               and observability              │
│ KEY INSIGHT   Design for failure: every      │
│               container will be killed;      │
│               the system must self-heal      │
│ USE WHEN      Deploying any container to a   │
│               shared or customer-facing env  │
│ AVOID WHEN    N/A - these are requirements,  │
│               not optional patterns          │
│ TRADE-OFF     Operational complexity vs      │
│               reliability at scale           │
│ ONE-LINER     Resource limits + health       │
│               checks + stdout logs + non-    │
│               root = minimum viable prod     │
│ NEXT EXPLORE  CTR-027, CTR-028, CTR-017      │
└──────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Set CPU and memory resource limits - always, without exception
2. Log to stdout, not filesystem files - the filesystem is ephemeral
3. Health probes are how the platform knows when to restart or reroute

**Interview one-liner:** "A production container needs resource limits to
prevent host starvation, liveness and readiness probes for self-healing,
stdout logging for observability, external state for persistence, and a
non-root user for security - none of which matter in local development."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Every process in a distributed system
must be designed as if it will fail randomly and be restarted automatically.
State must be externalised, failure must be detectable, and recovery must be
automated - because human intervention at 3 AM at scale is not viable.

**Where else this pattern appears:**
- **Serverless functions (Lambda)** - inherently ephemeral; external state
  in DynamoDB/S3; cold start = container startup equivalent
- **Database connection pools** - connections fail; the pool must detect
  dead connections (health checks) and replace them (restarts)
- **Circuit breaker pattern** - services must detect unhealthy backends
  (health probes) and stop routing to them (readiness equivalent) until
  they recover

---

### 💡 The Surprising Truth

The "12-factor app" methodology that defines modern container best practices
(stateless, stdout logging, external config) was published by Heroku in
2012 - a full year before Docker existed. The container revolution didn't
invent these production patterns; it operationalised them at scale. The
reason containers work so well with Kubernetes is that both were designed
around the same philosophy: treat compute as cattle, not pets. Every
practice in this entry existed before containers; containers just made
violating them more immediately painful and visible.

---

### 🧠 Think About This Before We Continue

1. **(Type D - Root Cause)** A container in a Kubernetes cluster enters
   `CrashLoopBackOff` with a 1-minute backoff delay after each restart.
   A human-facing feature depends on this service. What is the sequence of
   diagnostic steps that identify the root cause in under 5 minutes without
   access to the application developer?

   *Hint:* Work from `kubectl describe pod` (events), to `kubectl logs
   --previous` (last crash output), to `kubectl get events` (cluster events),
   to node-level `journalctl -u kubelet` if the pod isn't scheduling at all.

2. **(Type B - Scale)** At 10,000 pods across 500 nodes, each with a
   liveness probe polling `/health` every 10 seconds, the health endpoint
   receives ~1M requests/minute. How does this probe load affect the
   application, and what configuration options does Kubernetes provide to
   tune probe behaviour?

   *Hint:* Look at `periodSeconds`, `timeoutSeconds`, `failureThreshold`,
   and `initialDelaySeconds` in the Kubernetes probe spec. Consider whether
   the health endpoint should be a separate lightweight process.

3. **(Type C - Design Trade-off)** Kubernetes offers both liveness probes
   (restart when unhealthy) and readiness probes (remove from load balancer
   when not ready). Some teams implement only liveness, skipping readiness.
   What specific production scenario does the absence of a readiness probe
   cause, and why is it very hard to detect without load testing?

   *Hint:* Consider what happens during a rolling update when a new pod
   starts serving traffic before its database connection pool is warmed
   up or its local caches are populated.
