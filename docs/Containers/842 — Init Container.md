---
layout: default
title: "Init Container"
parent: "Containers"
nav_order: 842
permalink: /containers/init-container/
number: "0842"
category: Containers
difficulty: ★★★
depends_on: Container, Pod, Kubernetes Architecture, Linux Namespaces
used_by: Pod, Sidecar Container, Kubernetes Architecture
related: Sidecar Container, Ephemeral Container, Pod, Container Health Check, Kubernetes Architecture
tags:
  - containers
  - kubernetes
  - pattern
  - advanced
  - architecture
---

# 842 — Init Container

⚡ TL;DR — Init containers run to completion before any application container starts, providing a guaranteed setup and dependency-check phase with a different image and permissions.

| #842 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Container, Pod, Kubernetes Architecture, Linux Namespaces | |
| **Used by:** | Pod, Sidecar Container, Kubernetes Architecture | |
| **Related:** | Sidecar Container, Ephemeral Container, Pod, Container Health Check, Kubernetes Architecture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your Java application needs a database schema migrated before it starts. Without init containers, you have three bad options. Option 1: Bake the migration into the application startup — the application runs migrations then starts serving traffic. Problem: if two replicas start simultaneously, both run migrations concurrently, causing race conditions in the migration scripts. Option 2: Add a shell script in the application container that waits for the DB via a retry loop before migrating — but the application image now requires a shell and DB migration tooling, bloating the image and adding unnecessary dependencies. Option 3: Run migrations via a separate Job before the Deployment — but coordinating Job completion with Deployment rollout requires custom orchestration logic.

**THE BREAKING POINT:**
Any ordered "must complete before the app starts" operation — schema migration, config fetch, permission setup, service availability check — requires a well-defined pre-start phase. Baking it into the application is incorrect separation of concerns. Coordinating it externally is fragile. A native mechanism is needed.

**THE INVENTION MOMENT:**
This is exactly why Kubernetes init containers were designed — they run sequentially before any application container in a pod, run to completion, restart on failure, and block application startup until all pass. They solve the "setup before running" problem with a clean, native Kubernetes mechanism.

---

### 📘 Textbook Definition

An **init container** is a specialised container in a Kubernetes Pod that runs to completion before any of the regular (application) containers start. A pod may have one or more init containers, and they execute sequentially in the order declared. If any init container exits with a non-zero exit code, the pod's restart policy is applied (restart the failed init container) and no application container starts until all init containers succeed. Init containers have no `livenessProbe` or `readinessProbe` fields — they are either running or complete. They share the pod's volumes, network namespace, and can communicate with services. From Kubernetes 1.29, init containers can also be declared as "sidecar init containers" with `restartPolicy: Always` to run alongside application containers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Init containers are mandatory setup steps that run and complete before the main application is allowed to start.

**One analogy:**
> A production kitchen has prep cooks who arrive before the restaurant opens. They chop vegetables, make sauces, and set up workstations. The main chefs cannot start cooking service until all the prep work is done. If a prep cook doesn't finish (runs out of ingredients), service is delayed until resolved. Init containers are prep cooks: they do the necessary setup work, and the application (main chefs) only starts when every setup step has been verified complete.

**One insight:**
Init containers are structurally different from readiness probes. A readiness probe says "is the application ready to serve traffic?" An init container says "has setup work that MUST happen before the application starts been completed?" The timing guarantee is fundamentally different: init containers block the container start, not just traffic routing.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Some operations must complete atomically before an application can safely start — no application code can run until they succeed.
2. The setup environment (tools, permissions, images) may differ from the application environment.
3. Setup failures must prevent the application from starting, not silently degrade it.

**DERIVED DESIGN:**

Init containers are sequentially executed and a phase gate for pod startup:

```
┌──────────────────────────────────────────────────────────┐
│            Pod Startup with Init Containers              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Init Container 1: wait-for-db                          │
│    → exit 0 (DB ready) ────────────────────────→        │
│                                                          │
│  Init Container 2: run-migrations                        │
│    → exit 0 (migrations done) ─────────────────→        │
│    ← exit 1 (migration failed): POD RESTARTS             │
│                                                          │
│  Init Container 3: fetch-config                          │
│    → exit 0 (config pulled) ───────────────────→        │
│                                                          │
│  App Container 1: my-app   ← STARTS ONLY AFTER ALL      │
│  App Container 2: sidecar    INIT CONTAINERS PASS        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Pod resource calculation:**
Kubernetes calculates pod resource requests as: `max(max(all init containers), sum(all app containers))`. Init containers run serially. App containers run concurrently. This means an init container can use more resources than the app itself without increasing the pod's total resource request (a large migration init container doesn't inflate the ongoing pod resource cost).

**Separate image, separate privilege:**
Init containers can use a different image from the application. A `python:3.12` init container can run DB migrations while the application runs on a distroless Java image. Init containers can also have different security contexts — for example, running with elevated privileges for setup tasks that the application container should not have.

**THE TRADE-OFFS:**

**Gain:** Guaranteed sequential setup. Clean separation of setup from application. Failure prevents application start (not silent degradation).

**Cost:** Slower pod startup (each init container adds latency). No liveness probes — a stuck init container hangs indefinitely (mitigate with pod-level `activeDeadlineSeconds`). Serial execution — parallelism is not native (use workarounds for parallel init).

---

### 🧪 Thought Experiment

**SETUP:**
A web application connects to a PostgreSQL database. Three replicas are deployed simultaneously via a Kubernetes Deployment. The database has a schema that must be migrated before the app can run.

**WHAT HAPPENS WITHOUT INIT CONTAINERS:**
All three replicas start simultaneously. Each replica has startup code that checks if migrations are needed and runs them. Two of the three replicas both detect the migration is needed and start executing the same Flyway migration script simultaneously. Migration step V3 creates a column — both replicas try to add the column concurrently. One succeeds; the other fails with `column already exists`. The failed replica crashes and restarts, then succeeds because the column now exists. But during the window where both were running migrations, the database was in an inconsistent intermediate state. If any app code ran during this window, it might have encountered the broken state.

**WHAT HAPPENS WITH INIT CONTAINERS:**
An init container runs Flyway migrations. All three replicas start simultaneously — all three run only the init container, not the application. Init containers are identical and Flyway uses a distributed lock (migration history table). One instance acquires the lock, runs migrations, commits. The other two instances wait for the lock, detect migrations already completed, exit 0 immediately. All three init containers complete. All three application containers start — against a fully migrated, consistent schema.

**THE INSIGHT:**
Init containers guarantee a pre-condition is met before the application runs, but they do not solve distributed coordination (multiple init containers running concurrently for the same setup task). The application logic (Flyway locking) is still required. Init containers provide the timing guarantee — one-time setup should happen before the app; coordination is still application responsibility.

---

### 🧠 Mental Model / Analogy

> An init container is a preflight checklist for pilots. Before any plane takes off, the entire checklist must be completed: oil checked, flaps configured, instruments calibrated, charts loaded. Only when every item is checked off does the pilot receive clearance to start engines. If an item fails (low oil), the plane does not take off, no matter how urgent the departure. Init containers are that preflight checklist — required steps that gate the application's "takeoff."

Mapping:
- "Preflight checklist items" → init containers (each sequential check)
- "Oil checked" → init container 1: database available check
- "Charts loaded" → init container 2: configuration fetched
- "Clearance to start engines" → application containers start
- "Low oil → no takeoff" → init container fails → pod restarts
- "Checklists run sequentially, in order" → init containers execute serially

Where this analogy breaks down: pilots can pause a checklist and retry an individual item. Init containers in a pod restart the entire pod's init sequence from container 1 when any init container fails (with the default restartPolicy). Kubernetes 1.29+ "sidecar init containers" add more nuanced restart behaviour.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Init containers are setup steps that must run successfully before your application starts. If a setup step fails, the application never starts — which is safer than starting an application in a broken state. You can have multiple setup steps, and they run in order.

**Level 2 — How to use it (junior developer):**
Define init containers in the pod spec under `initContainers:`. Each has the same structure as a regular container (image, command, env, volumeMounts). They run in order and must exit 0 before the next starts. Common uses: wait for a dependency (`nc -z db 5432`), run database migrations (`flyway migrate`), fetch credentials from Vault, download configuration files.

**Level 3 — How it works (mid-level engineer):**
The kubelet processes init containers through the pod's lifecycle state machine. The pod transitions through `Pending → Init:0/N → Init:1/N → ... → Running`. Each init container is started via CRI (same as regular containers), but kubelet blocks progression to the next container until the current one exits with code 0. On failure, kubelet applies `restartPolicy` (default: Always — restarts the failing init container with exponential backoff). Init containers share the pod's volumes but have independent process, filesystem namespaces. The app containers are not created until all init containers succeed.

**Level 4 — Why it was designed this way (senior/staff):**
The serial execution model was chosen for simplicity and determinism. Most init scenarios are naturally sequential: "wait for DB" must precede "run migrations." Supporting parallel init execution would require a DAG-based dependency model (complex) while most users only need a simple sequence. The blocking startup behaviour is a deliberate safety property — it is better to have visible pod startup failure than a silently misconfigured application. The resource model (max of init containers, not sum) was a deliberate optimisation — init containers are transient and their resource usage doesn't overlap with app container usage, so charging the sum would over-provision. Kubernetes 1.28/1.29 introduced "sidecar init containers" (init containers with `restartPolicy: Always`) — these start but don't block the pod; they are primarily for logging/proxy sidecars that need to start before the app but run alongside it continuously.

---

### ⚙️ How It Works (Mechanism)

**Pod lifecycle state machine:**
```
┌──────────────────────────────────────────────────────────┐
│           Pod Lifecycle with Init Containers             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Pod scheduled → Pending                                 │
│       ↓                                                  │
│  Init Container 1 starts → Init:0/2                      │
│  ├── exit 0 → Init Container 2 starts → Init:1/2        │
│  └── exit N (failure) → restart (backoff) → retry       │
│       ↓ (all init containers exit 0)                     │
│  App containers start → Running                          │
│       ↓                                                  │
│  All app containers ready → Pod Ready                    │
│                                                          │
│  activeDeadlineSeconds: if set, pod fails after N sec    │
│  (prevents indefinitely stuck init containers)           │
└──────────────────────────────────────────────────────────┘
```

**Volume sharing between init and app containers:**
Init containers can write to shared volumes, making data available to app containers:

```
┌──────────────────────────────────────────────────────────┐
│     Init Container Volume Data Flow                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  emptyDir volume: /etc/config                            │
│                                                          │
│  Init Container:                                         │
│    curl -o /etc/config/app.conf vault.example.com/...   │
│    (writes config to shared volume)                      │
│                                                          │
│  App Container:                                          │
│    reads /etc/config/app.conf                            │
│    (guaranteed to exist before app starts)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
kubectl apply deployment.yaml
  → scheduler assigns pod to node
  → kubelet: pull init container image
  → init container 1: wait for DB (exit 0) ← YOU ARE HERE
  → init container 2: run migrations (exit 0)
  → app container: starts → Ready
  → traffic routed via Service
```

**FAILURE PATH:**
```
init container 2 fails (DB migration error, exit 1):
  → pod status: Init:CrashLoopBackOff (or Init:Error)
  → kubelet restarts init container 2 with backoff
  → app container never starts
  → kubectl describe pod shows reason + logs
  → fix migration error → pod recovers
```

**WHAT CHANGES AT SCALE:**
With 100 pod replicas, 100 init containers run simultaneously. If each init container runs a DB migration, you have 100 parallel migration attempts against the database connection pool. Use a Kubernetes Job for actual migrations (runs once) and a simple read-only health check as the init container for the Deployment pods.

---

### 💻 Code Example

**Example 1 — Wait for service dependency:**
```yaml
# Wait for PostgreSQL before starting the app
initContainers:
- name: wait-for-db
  image: busybox:1.35
  command:
  - sh
  - -c
  - |
    until nc -z postgres-service 5432; do
      echo "Waiting for PostgreSQL..."
      sleep 2
    done
    echo "PostgreSQL ready"
```

**Example 2 — Database migration init container:**
```yaml
initContainers:
- name: run-migrations
  image: flyway/flyway:9.22   # different image from app
  args:
  - -url=jdbc:postgresql://postgres:5432/mydb
  - -user=$(DB_USER)
  - -password=$(DB_PASSWORD)
  - migrate
  env:
  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: username
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: password
  volumeMounts:
  - name: migration-scripts
    mountPath: /flyway/sql
```

**Example 3 — Fetch config from Vault into shared volume:**
```yaml
initContainers:
- name: fetch-vault-config
  image: vault:1.15
  command:
  - sh
  - -c
  - |
    vault agent -config=/etc/vault/agent.hcl \
      -exit-after-auth
    # Writes secrets to /etc/secrets/ shared volume
  volumeMounts:
  - name: secrets-volume
    mountPath: /etc/secrets
  - name: vault-config
    mountPath: /etc/vault

containers:
- name: my-app
  image: gcr.io/distroless/java21-debian12
  volumeMounts:
  - name: secrets-volume
    mountPath: /etc/secrets  # secrets written by init container
```

**Example 4 — Kubernetes 1.29+ sidecar init container:**
```yaml
# Sidecar init container: starts before app, runs alongside it
initContainers:
- name: log-forwarder
  image: fluent-bit:3.0
  restartPolicy: Always    # runs continuously alongside app
  # This sidecar starts before app containers, but doesn't block them
  # on exit. It runs for the lifetime of the pod.
```

---

### ⚖️ Comparison Table

| Container Type | When It Runs | Block App Start | Restart on Exit | Use Case |
|---|---|---|---|---|
| **Init Container** | Before app, sequential | Yes | Yes (pod restarts) | Setup, migration, config fetch |
| Regular Container | Alongside app, concurrent | No | Per restartPolicy | Application logic |
| Sidecar Container | Alongside app, concurrently | No | Per restartPolicy | Logging, proxy, metrics |
| Sidecar Init (K8s 1.29+) | Starts before app, runs alongside | No (blocks then converts) | Always | Logging sidecar that starts first |
| Ephemeral Container | On-demand after pod start | No | Never | Debugging |

How to choose: init containers for anything that must complete before the app runs (DB migrations, dependency checks, config population). Regular containers for the application. Sidecar containers for cross-cutting concerns (logging, service mesh proxy).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Init containers share the filesystem of app containers" | Init containers have their own filesystem (from their own image). Data sharing between init and app containers requires explicit shared volumes (`emptyDir`). |
| "If an init container fails, the pod is deleted" | No. The pod stays (in Init:Error / Init:CrashLoopBackOff state) and Kubernetes restarts the failing init container with exponential backoff. The pod is retried indefinitely (unless `activeDeadlineSeconds` is set). |
| "Init containers are good for running one-time DB migrations in a Deployment" | Risky — if a Deployment has 50 replicas, 50 init containers run the migration simultaneously. Use a Kubernetes Job for migrations, and use init containers only for lightweight checks. |
| "Init containers can have liveness probes" | No — init containers can only `run to completion` or fail. Liveness and readiness probes are only for regular containers. |
| "Init containers slow down pod startup significantly" | Only if they are slow themselves. A simple `nc -z db 5432` check takes milliseconds. A 10-second DB wait adds 10 seconds. Design init containers to be fast and idempotent. |

---

### 🚨 Failure Modes & Diagnosis

**Pod stuck in Init:CrashLoopBackOff**

**Symptom:**
Pod shows `Init:CrashLoopBackOff` or `Init:Error` and never starts the application container.

**Root Cause:**
An init container is repeatedly failing (exit code non-zero). Common causes: dependency not available, migration failure, credentials invalid, command/image misconfiguration.

**Diagnostic Command / Tool:**
```bash
# See which init container is failing
kubectl describe pod <pod-name>

# Get logs of the failing init container
kubectl logs <pod-name> -c <init-container-name>

# Get logs from previous (crashed) init container
kubectl logs <pod-name> -c <init-container-name> --previous
```

**Fix:**
Read the init container logs. Fix the underlying issue (dependency not ready, script bug, invalid credentials). The pod will automatically retry.

**Prevention:**
Add a timeout to dependency-wait init containers (`timeout 300 -- nc -z db 5432`). Set `activeDeadlineSeconds` on the pod to prevent infinite retry. Alert on pods stuck in Init phase > 5 minutes.

---

**Init container image pull failure blocking entire pod**

**Symptom:**
Pod stuck in `Init:0/2` with `ImagePullBackOff` on the init container image.

**Root Cause:**
Init container image not available in registry or wrong credentials for private registry. Blocks the entire pod from starting.

**Diagnostic Command / Tool:**
```bash
kubectl describe pod <pod> | grep -A5 "Events"
# Look for "Failed to pull image"
```

**Fix:**
Fix the image reference or add the correct `imagePullSecrets` to the pod spec or service account.

**Prevention:**
Test init container images independently. Use the same registry and pull secret pattern as application containers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Pod` — init containers are part of pod spec; understand pod structure first
- `Kubernetes Architecture` — understand kubelet's role in executing init containers
- `Container` — init containers are containers; understand container basics

**Builds On This (learn these next):**
- `Sidecar Container` — next pattern after init containers; runs alongside app permanently
- `Container Health Check` — readiness/liveness probes that complement init container setup checks
- `Kubernetes Architecture` — deep understanding of how kubelet processes pod lifecycle

**Alternatives / Comparisons:**
- `Ephemeral Container` — for debugging, not setup; temporary vs pre-start
- `Sidecar Container` — runs at the same time as the app; permanent vs one-time setup
- `Container Health Check` — monitors health after start; init containers verify preconditions before start

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Ordered pre-start containers that must    │
│              │ exit 0 before app containers start        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Setup/migration/config tasks must run     │
│ SOLVES       │ before app starts, in a clean way         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Different image + different permissions    │
│              │ than app — clean separation of roles      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ DB migrations, dependency waits, config   │
│              │ fetch, permission setup before app start  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long-running alongside-app tasks (use     │
│              │ sidecar) or debugging (use ephemeral)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Guaranteed pre-conditions vs slower pod   │
│              │ startup + no parallel execution natively  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The preflight checklist your app can't   │
│              │  skip: every step done or no takeoff"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sidecar Container → Container Health      │
│              │ Check → Pod Disruption Budget             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Deployment has 100 replicas. An init container runs a database migration using Flyway. If all 100 pods start simultaneously (e.g., after a cluster node failure forces a reschedule), describe precisely what happens to your database: how many connection attempts are made, how does Flyway's locking mechanism interact with 100 concurrent init containers, and what is the correct architecture to run migrations exactly once while still using init containers for dependency readiness checks?

**Q2.** Kubernetes 1.29 introduced "sidecar init containers" — init containers with `restartPolicy: Always` that start before the app but run throughout the pod's lifetime. Before this feature, how did teams implement "a sidecar that must be ready before the app starts" (e.g., an Envoy proxy sidecar)? What are the failure modes of those workarounds? How does the new sidecar init container feature solve those failures, and what new failure modes does it introduce?

