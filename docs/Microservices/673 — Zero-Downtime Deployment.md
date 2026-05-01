---
layout: default
title: "Zero-Downtime Deployment"
parent: "Microservices"
nav_order: 673
permalink: /microservices/zero-downtime-deployment/
number: "673"
category: Microservices
difficulty: ★★★
depends_on: "Graceful Shutdown, Load Balancing"
used_by: "Canary Deployment, Blue-Green Deployment"
tags: #advanced, #microservices, #devops, #distributed, #reliability
---

# 673 — Zero-Downtime Deployment

`#advanced` `#microservices` `#devops` `#distributed` `#reliability`

⚡ TL;DR — **Zero-Downtime Deployment** means releasing a new version of a service without any user-visible outage. Achieved through: rolling updates (gradually replace old pods), graceful shutdown (drain in-flight requests), backward-compatible database migrations (Expand-Contract pattern), and API versioning. The hardest part is not the infrastructure — it's ensuring the database schema change doesn't break old pods while new pods are running.

| #673            | Category: Microservices                  | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Graceful Shutdown, Load Balancing        |                 |
| **Used by:**    | Canary Deployment, Blue-Green Deployment |                 |

---

### 📘 Textbook Definition

**Zero-Downtime Deployment** (ZDD) is a deployment strategy where new code versions are released without any period during which the service is unavailable or returning errors. In Kubernetes, ZDD is implemented through rolling updates: new pods (with the new code version) are started, pass health checks, receive traffic, and old pods are gradually terminated — ensuring at least one healthy pod is always serving requests. ZDD requires: (1) **Graceful shutdown** — old pods drain in-flight requests before terminating; (2) **Backward-compatible API changes** — old clients work with new server version and vice versa during the transition; (3) **Database migration strategy** — the Expand-Contract (or Parallel Change) pattern ensures schema changes are compatible with both old and new code versions simultaneously. The critical insight: during a rolling update, both old and new versions of your service run simultaneously. Any schema change (dropping a column, renaming a field, changing a data type) that is not backward-compatible will cause old pods to fail while new pods serve new schema — violating ZDD.

---

### 🟢 Simple Definition (Easy)

Zero-downtime deployment means "deploy the new version without taking the service offline." Old pods continue serving traffic until new pods are healthy. New pods start, pass health checks, get traffic. Then old pods are killed gracefully (they finish current requests first). At no point are ALL pods offline. Users see no interruption.

---

### 🔵 Simple Definition (Elaborated)

Rolling update: 4 old pods running. Deploy new version. Kubernetes starts Pod 5 (new). Passes readiness probe. Kubernetes kills Pod 1 (old) — gracefully: Pod 1 drains its requests, then exits. Now: 3 old + 1 new. Starts Pod 6 (new). Kills Pod 2 (old). Now: 2 old + 2 new. Repeats until 4 new pods. Zero time with zero healthy pods. But during this: both old and new versions process requests simultaneously. If the database migration dropped a column that old code expects → old pods crash → user errors → NOT zero-downtime. The infra was fine. The database migration broke it.

---

### 🔩 First Principles Explanation

**Kubernetes Rolling Update configuration:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0 # Never go below 4 healthy pods (no degraded capacity)
      maxSurge: 1 # Allow 1 extra pod (max 5 pods during update)
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: order-service
          image: order-service:v2.0.0
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 10 # Allow Spring Boot startup time
            periodSeconds: 5
            failureThreshold: 3
            # Pod only receives traffic when readiness probe passes
            # maxUnavailable: 0 ensures old pods are NOT removed until new pod is ready
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
            # Kubernetes restarts pod if liveness fails
            # Liveness: "is the process alive?" (not deadlocked)
            # Readiness: "is the pod ready to serve traffic?" (startup completed)
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
                # Allow kube-proxy to propagate endpoint removal before SIGTERM
```

**THE HARD PART: Database migrations with zero downtime — Expand-Contract pattern:**

```
ANTI-PATTERN: Breaking migration (causes downtime):
  Step 1: Deploy DB migration: DROP COLUMN "customer_name"
  Problem: Old pods still running expect "customer_name" to exist → crash
  Old pods: 500 errors during rolling update → NOT zero-downtime

CORRECT PATTERN: Expand-Contract (3 separate deployments):

PHASE 1 — EXPAND (make the DB compatible with BOTH old and new code):
  Goal: add new column, make old code tolerant of new schema

  Option A: renaming a column (example: customer_name → full_name)

  Migration 001 (expand): ADD COLUMN full_name VARCHAR(255)
  Code v1.1: writes BOTH customer_name AND full_name. Reads from customer_name.
  Deploy code v1.1 (rolling update). All pods now run v1.1.
  Wait for: all old pods (v1.0) terminated and all new pods (v1.1) healthy.

PHASE 2 — MIGRATE:
  Migration 002 (data migration): UPDATE orders SET full_name = customer_name WHERE full_name IS NULL
  (backfill existing rows with new column data)
  Code v1.2: writes BOTH columns (idempotent). Reads from full_name (new column).
  Deploy code v1.2 (rolling update).

PHASE 3 — CONTRACT (remove old column when no code uses it):
  Migration 003 (contract): DROP COLUMN customer_name
  Code v1.3: writes only full_name. Reads only full_name. (old column removed from code)
  Deploy code v1.3 (rolling update).

RULE: each migration must be backward-compatible with the PREVIOUS code version
  Migration 001: compatible with v1.0 (adding a nullable column is always safe)
  Migration 002: compatible with v1.1 (UPDATE doesn't break v1.1's reads)
  Migration 003: safe only after v1.2 is fully deployed (no code reads customer_name)
```

**Liquibase migration example — expand phase:**

```xml
<!-- liquibase changelog (runs automatically on startup if Liquibase autoRun=true) -->
<!-- PHASE 1 EXPAND: add new column (backward compatible - old code ignores it) -->
<changeSet id="2024-001-add-full-name" author="dev-team">
    <addColumn tableName="orders">
        <column name="full_name" type="varchar(255)">
            <constraints nullable="true"/>
        </column>
    </addColumn>
    <!-- NOT NULL would break old code that doesn't set this column -->
    <!-- Nullable is backward-compatible: old code inserts without this column = NULL -->
</changeSet>
```

**Code compatibility: writing to both columns during transition:**

```java
// Code v1.1: transition version — writes BOTH old and new column
@Entity
class Order {
    private String customerName;  // old column: still present for old pod compatibility
    private String fullName;      // new column: written for new pod consumption

    // JPA: both columns mapped to DB columns
}

@Service
class OrderService {
    OrderRepository orderRepository;

    OrderDto createOrder(CreateOrderRequest request) {
        Order order = Order.builder()
            .customerName(request.getCustomerName())  // write old column (old pods read this)
            .fullName(request.getCustomerName())       // write new column (new pods will read)
            .build();
        orderRepository.save(order);
        return toDto(order);
    }

    OrderDto getOrder(Long orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        // READ from old column (new column not yet reliable - might be NULL for old rows)
        return OrderDto.builder()
            .customerName(order.getCustomerName())
            .build();
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

Maintenance windows (scheduled downtime: "deploy at 2 AM Sunday") impose real costs: engineering team on-call at odd hours, user-visible outages, loss of business. As deployment frequency increased (from monthly to daily to multiple times per day), maintenance windows became impossible. Zero-downtime deployment is the technical capability that enables high deployment frequency without SLO violations.

---

### 🧠 Mental Model / Analogy

> Zero-downtime deployment is like resurfacing a highway while traffic is moving. You close one lane at a time, resurface it, then reopen it — traffic always has at least one lane. If you close all lanes simultaneously (stop all pods at once), traffic stops completely. The database migration is the challenge: like changing the lane markings while cars are driving on them. You don't change the markings directly (old cars get confused). Instead: first add new markings alongside old ones (expand), then switch drivers to use new markings (migrate), then remove old markings when no car follows them (contract).

---

### ⚙️ How It Works (Mechanism)

**Monitoring a rolling update:**

```bash
# Watch rolling update progress:
kubectl rollout status deployment/order-service --watch
# Output:
# Waiting for deployment "order-service" rollout to finish: 1 out of 4 new replicas have been updated...
# Waiting for deployment "order-service" rollout to finish: 2 out of 4 new replicas have been updated...
# ...
# deployment "order-service" successfully rolled out

# Rollback if new version has issues:
kubectl rollout undo deployment/order-service
# Kubernetes immediately starts rolling back to previous pod spec
# This is why: keep previous image available in registry

# Check rollout history:
kubectl rollout history deployment/order-service
# Shows: REVISION  CHANGE-CAUSE
#        1         initial deployment
#        2         feat: add payment gateway v2
#        3         feat: add loyalty points

# Rollback to specific revision:
kubectl rollout undo deployment/order-service --to-revision=2
```

---

### 🔄 How It Connects (Mini-Map)

```
Graceful Shutdown          Load Balancing
(drain requests cleanly)   (distributes traffic across pods)
        │                          │
        └──────────┬───────────────┘
                   ▼
        Zero-Downtime Deployment  ◄──── (you are here)
        (rolling update + DB expand-contract)
                   │
        ┌──────────┴──────────────┐
        ▼                         ▼
Canary Deployment         Blue-Green Deployment
(gradual traffic shift)   (instant traffic cutover)
```

---

### 💻 Code Example

**PodDisruptionBudget — ensure minimum availability during voluntary disruptions:**

```yaml
# PodDisruptionBudget: prevents Kubernetes from taking down too many pods
# Applies to: kubectl drain node, cluster upgrades, rolling updates
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
spec:
  minAvailable: 3 # At least 3 pods must be available at all times
  selector:
    matchLabels:
      app: order-service
# With 4 replicas and minAvailable: 3:
#   Kubernetes can only kill 1 pod at a time → conservative rolling update
#   Prevents cluster upgrade from killing all order-service pods simultaneously
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                          |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zero-downtime deployment is just a Kubernetes configuration | Kubernetes handles the infrastructure layer. The application must also handle: graceful shutdown (drain requests), backward-compatible API changes, and Expand-Contract database migrations. Kubernetes alone cannot prevent errors if DB schema breaks old pods |
| Rolling updates mean both versions never run simultaneously | During a rolling update, both old and new versions run simultaneously (up to `maxUnavailable + maxSurge` pods in transition). This is the exact reason backward compatibility is mandatory — HTTP requests may hit either version                                |
| Zero-downtime means zero performance impact                 | ZDD means zero user-visible errors, not zero resource overhead. During rolling update: extra pods (maxSurge) run simultaneously → higher CPU/memory. DB migrations may cause table locks affecting query performance                                             |
| Adding a NOT NULL column is backward compatible             | NOT NULL without a DEFAULT breaks old pods immediately: old code INSERT without the new column → constraint violation → 500 error. Always add columns as nullable, or with a DEFAULT value, during the expand phase                                              |

---

### 🔥 Pitfalls in Production

**Schema migration invalidates JPA entity cache — invisible race condition:**

```
SCENARIO:
  v1.0: Order entity has field "status" as VARCHAR ('PENDING', 'CONFIRMED', 'SHIPPED')
  v2.0: Add "CANCELLED" as valid status value

  This seems safe: adding a new ENUM value is backward compatible?

  PROBLEM: PostgreSQL ENUM type:
    v1.0 JPA entity: status mapped to @Enumerated(EnumType.STRING)
    enum OrderStatus { PENDING, CONFIRMED, SHIPPED }

    Database migration: ALTER TYPE order_status ADD VALUE 'CANCELLED'

    Old pods (v1.0): read a row with status='CANCELLED'
    JPA: tries to map 'CANCELLED' to OrderStatus enum
    Java: IllegalArgumentException: No enum constant OrderStatus.CANCELLED
    Old pod: 500 error reading that order

    Even with @Enumerated(EnumType.STRING): JPA throws on unknown enum value

  FIX: Expand-Contract applies to ENUM values too:
    Phase 1: Add CANCELLED to old code's enum first, deploy old code
    Phase 2: Add DB migration to add CANCELLED enum value
    Phase 3: v2.0 code uses CANCELLED status

  LESSON: "backward compatible schema changes" must be validated against
          what the OLD code does when it READS the new data, not just when it writes.
```

---

### 🔗 Related Keywords

- `Graceful Shutdown` — required for pods to drain requests before termination
- `Load Balancing` — distributes traffic across pod versions during rolling update
- `Canary Deployment` — incremental traffic shift (complement to rolling updates)
- `Blue-Green Deployment` — instant cutover alternative to rolling updates

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ K8S CONFIG   │ maxUnavailable: 0, maxSurge: 1            │
│              │ readinessProbe + terminationGracePeriod   │
├──────────────┼───────────────────────────────────────────┤
│ DB STRATEGY  │ Expand-Contract (3 deployments):          │
│              │ 1. Add new column (nullable)              │
│              │ 2. Migrate data, switch reads             │
│              │ 3. Drop old column                        │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ During rolling update: both versions run  │
│ ROLLBACK     │ kubectl rollout undo deployment/svc       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service stores a field `address` as a single VARCHAR column (e.g. "123 Main St, Springfield, IL 62701"). The new version splits this into separate columns: `street`, `city`, `state`, `zip`. Design the complete Expand-Contract migration: write the three migration SQL statements, describe what the v1.1, v1.2, and v1.3 code versions do differently (what they read vs write), and identify the exact risk window during which data inconsistency is possible.

**Q2.** Your Kubernetes rolling update has `maxUnavailable: 0` and `maxSurge: 1` with 4 replicas. A developer deploys v2.0 which has a bug: it starts successfully and passes readiness probes, but after 60 seconds crashes (liveness probe failure). Describe exactly what Kubernetes does: how many pods run at each phase, when does the rollout appear "successful" vs when does Kubernetes detect the failure, and will any of the 4 replicas be running v1.0 or will all 4 be v2.0 (crashing) pods?
