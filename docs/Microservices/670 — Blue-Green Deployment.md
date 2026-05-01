---
layout: default
title: "Blue-Green Deployment"
parent: "Microservices"
nav_order: 670
permalink: /microservices/blue-green-deployment/
number: "670"
category: Microservices
difficulty: ★★☆
depends_on: "Zero-Downtime Deployment, Load Balancing"
used_by: "Canary Deployment, Graceful Shutdown"
tags: #intermediate, #microservices, #devops, #distributed, #reliability
---

# 670 — Blue-Green Deployment

`#intermediate` `#microservices` `#devops` `#distributed` `#reliability`

⚡ TL;DR — **Blue-Green Deployment** maintains two identical production environments (Blue = current, Green = new). Traffic is cut over from Blue to Green in one switch. Blue remains live as instant rollback. Eliminates downtime during deployment; provides sub-second rollback. Cost: double the infrastructure during transition.

| #670            | Category: Microservices                  | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Zero-Downtime Deployment, Load Balancing |                 |
| **Used by:**    | Canary Deployment, Graceful Shutdown     |                 |

---

### 📘 Textbook Definition

**Blue-Green Deployment** is a release strategy (Martin Fowler, 2010) that reduces deployment risk and downtime by maintaining two identical production environments — **Blue** (the currently live version) and **Green** (the new version to deploy). At any time, only one environment receives live traffic. The deployment process: deploy the new version to the inactive environment (Green); run smoke tests and acceptance tests against Green in isolation; perform the traffic switch — update the load balancer to route 100% of traffic from Blue to Green; Blue is kept running but idle as a hot rollback target; once Green is validated, Blue can be decommissioned or kept as the staging slot for the next deployment. Blue-Green provides: **zero-downtime deployments** (traffic switch is milliseconds); **instant rollback** (switch traffic back to Blue); **validated production-identical testing** (Green tested against production data and configuration before switch). Trade-offs: **cost** (maintaining two full environments simultaneously doubles infrastructure cost during transition); **database schema management** (both environments share or must simultaneously handle the database).

---

### 🟢 Simple Definition (Easy)

Run the current version (Blue) and deploy the new version (Green). Test Green thoroughly. Then flip the switch: all traffic goes to Green instantly. If Green breaks, flip back to Blue. Zero downtime, instant rollback.

---

### 🔵 Simple Definition (Elaborated)

Blue: `order-service:v1.4` running in production, 100% traffic. Green: deploy `order-service:v1.5` to an identical environment. Green has: same number of pods, same configuration, connects to the same (or a copy of) the production database. Run smoke tests against Green's URL. Everything passes. Switch: load balancer now routes 100% traffic to Green. Blue: still running but receives no traffic. 10 minutes later: a bug discovered in v1.5. Switch: load balancer routes 100% back to Blue. Rollback time: 5 seconds. No incident. Fix the bug, redeploy to Green, repeat.

---

### 🔩 First Principles Explanation

**Blue-Green infrastructure pattern — two approaches:**

```
APPROACH 1: TWO SEPARATE DEPLOYMENTS (Kubernetes):

  Blue Deployment (active):
    name: order-service-blue
    image: order-service:v1.4
    replicas: 10
    labels: app=order-service, version=blue

  Green Deployment (staged):
    name: order-service-green
    image: order-service:v1.5
    replicas: 10
    labels: app=order-service, version=green

  Service (load balancer pointer):
    selector: version=blue  ← currently pointing to Blue

  SWITCH: Change Service selector:
    kubectl patch service order-service -p '{"spec":{"selector":{"version":"green"}}}'
    → All new requests now route to Green (existing Blue connections drain)

  ROLLBACK:
    kubectl patch service order-service -p '{"spec":{"selector":{"version":"blue"}}}'
    → All traffic back to Blue within seconds

APPROACH 2: AWS ALB + TWO TARGET GROUPS (cloud-native):

  ALB Listener Rule:
    Target Group Blue: order-service v1.4 (weight=100)
    Target Group Green: order-service v1.5 (weight=0)

  SWITCH (one CLI command):
    aws elbv2 modify-rule \
      --rule-arn arn:aws:elasticloadbalancing:... \
      --actions '{"Type":"forward","ForwardConfig":{"TargetGroups":[
        {"TargetGroupArn":"...green-arn...","Weight":100},
        {"TargetGroupArn":"...blue-arn...","Weight":0}
      ]}}'

  ROLLBACK: reverse the weights.
  No Kubernetes changes needed — pure load balancer configuration.

APPROACH 3: AWS ELASTIC BEANSTALK / RENDER / RAILWAY:
  "Swap environments" button in UI
  → Platform handles DNS/load balancer swap internally
  CNAME swap: domain points to Blue CNAME → flipped to Green CNAME
  LIMITATION: DNS TTL propagation delay (30-60 seconds for full propagation)
              Not truly instant like direct load balancer weight change
```

**Database handling — the critical challenge:**

```
DATABASE CHALLENGE:
  Blue and Green share the same database.
  v1.5 requires schema changes.
  If you run migration on switch: v1.4 (Blue, for rollback) won't work with new schema.

STRATEGIES:

STRATEGY 1: Backward-compatible migration (safest):
  Before deployment:
    Add new column/table (NULLABLE)
    Blue (v1.4) ignores new column → works fine
    Green (v1.5) uses new column → works fine
  After rollback period:
    If no rollback needed: add constraints, drop old columns
    If rolled back to Blue: reverse-compatible (Green changes were additive)

STRATEGY 2: Separate database per color:
  Blue has own DB with v1.4 schema
  Green has own DB with v1.5 schema
  Traffic switch: load balancer switch
  Data sync: new writes replicated to both DBs during transition period
  COMPLEXITY: high — dual-write during transition, eventual consistency
  USE WHEN: schema changes are breaking (cannot be made backward-compatible)

STRATEGY 3: Feature flags for schema-dependent features:
  Deploy v1.5 (with new code + schema) to Green.
  New feature: DISABLED by default (feature flag OFF).
  Switch to Green.
  Migration runs on shared database.
  v1.4 rollback: safe (new column nullable, v1.4 ignores it).
  After stability period: enable feature flag → new feature available.
  Drop old columns only after v1.4 is decommissioned.
```

**Blue-Green vs Canary — decision matrix:**

```
                  BLUE-GREEN        CANARY
Risk detection    Before switch     During gradual rollout
Traffic exposure  0% until switch   5% → 25% → 100%
Rollback speed    Seconds (instant) Seconds (instant at any %)
Blast radius      0% or 100%        1% to current canary %
Cost              2× infrastructure ~1.1× infrastructure (few canary pods)
Best for:         High-risk releases that must not partially deploy
                  Strict compliance (no partial feature state in production)
                  When: release is all-or-nothing (payment protocol change)
Avoid when:       Long-running state in service (active sessions, in-flight transactions)
```

---

### ❓ Why Does This Exist (Why Before What)

Traditional deployments: stop old version, deploy new version. Downtime = deployment time (minutes to hours). Blue-Green eliminates downtime by having the new version ready and tested before the traffic switch. The switch itself takes milliseconds. Before Blue-Green, maintenance windows during off-peak hours (2am Saturday) were necessary for significant releases. Blue-Green enables deploys at any time, any day.

---

### 🧠 Mental Model / Analogy

> Blue-Green deployment is like building a bypass road before redirecting traffic. You build the new highway (Green) next to the old one (Blue) — both complete and functional. You test the new highway with emergency vehicles (smoke tests). When confirmed safe, you open the new highway (traffic switch) and close the old one. If the new highway has a pothole discovered after opening: reopen the old highway (rollback) while you repair. Both roads existed simultaneously, briefly, to enable the zero-downtime transition.

---

### ⚙️ How It Works (Mechanism)

**Kubernetes blue-green with service selector:**

```yaml
# Blue Deployment (currently serving traffic):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-blue
spec:
  replicas: 10
  selector:
    matchLabels: { app: order-service, slot: blue }
  template:
    metadata:
      labels: { app: order-service, slot: blue }
    spec:
      containers:
        - name: order-service
          image: myrepo/order-service:v1.4.0

---
# Green Deployment (staged, not yet receiving traffic):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-green
spec:
  replicas: 10
  selector:
    matchLabels: { app: order-service, slot: green }
  template:
    metadata:
      labels: { app: order-service, slot: green }
    spec:
      containers:
        - name: order-service
          image: myrepo/order-service:v1.5.0

---
# Service: points to Blue (currently):
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
    slot: blue # ← SWITCH: change to "green" to cut over
```

---

### 🔄 How It Connects (Mini-Map)

```
Zero-Downtime Deployment
(overarching goal)
        │
        ▼
Blue-Green Deployment  ◄──── (you are here)
(two environments, instant switch)
        │
        ├── Canary Deployment → gradual alternative to blue-green's all-or-nothing
        ├── Feature Flags → control feature exposure independently of deployment
        └── Load Balancing → the mechanism for the blue-green traffic switch
```

---

### 💻 Code Example

**GitHub Actions workflow — automated blue-green deployment:**

```yaml
# .github/workflows/deploy.yml
- name: Deploy to Green
  run: |
    kubectl set image deployment/order-service-green \
      order-service=$IMAGE_TAG

- name: Wait for Green rollout
  run: kubectl rollout status deployment/order-service-green --timeout=300s

- name: Run smoke tests against Green
  run: ./scripts/smoke-test.sh $GREEN_URL
  env:
    GREEN_URL: http://order-service-green.internal

- name: Switch traffic to Green
  run: |
    kubectl patch service order-service \
      -p '{"spec":{"selector":{"slot":"green"}}}'

- name: Monitor for 5 minutes
  run: |
    for i in {1..30}; do
      sleep 10
      ERROR_RATE=$(kubectl exec deploy/prometheus -- \
        promtool query instant \
        'sum(rate(http_server_requests_total{slot="green",status=~"5.."}[1m]))/
         sum(rate(http_server_requests_total{slot="green"}[1m]))')
      if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
        echo "Error rate too high: $ERROR_RATE. Rolling back."
        kubectl patch service order-service -p '{"spec":{"selector":{"slot":"blue"}}}'
        exit 1
      fi
    done

- name: Decommission Blue (optional — keep for manual rollback period)
  run: kubectl scale deployment order-service-blue --replicas=0
```

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                                                                                                                                                                  |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Blue-Green means you always have two running environments permanently | The idle environment (Blue, after Green becomes active) can be scaled to zero to save costs, with replicas brought back only when needed for rollback. Many organisations keep it at 0 replicas (not deleted) for fast restoration if needed             |
| Blue-Green solves all deployment risks                                | Blue-Green ensures zero-downtime switch and fast rollback. It does not protect against bugs that only manifest under production load (use canary for that) or against data issues introduced by the new version before rollback                          |
| Stateful services can always use blue-green                           | Services with local state (in-memory caches, active WebSocket connections, in-progress transactions) require careful handling. Active sessions on Blue at switch time may be disrupted. Use connection draining and graceful shutdown to minimize impact |

---

### 🔥 Pitfalls in Production

**Long-running transactions during traffic switch:**

```
SCENARIO:
  Blue: currently processing 50 in-flight payment transactions.
  Traffic switch executed: 100% of new requests go to Green.
  Blue: still processing its 50 in-flight transactions.
  After 30 seconds: Blue is force-stopped.
  20 of 50 transactions: interrupted mid-processing.
  → Partial payments, inconsistent order state, customer double-charges.

FIX: Connection draining before decommissioning Blue.

  Kubernetes terminationGracePeriodSeconds: 60
  → Pod receives SIGTERM → stops accepting new requests → finishes in-flight requests
  → After 60 seconds (or all connections closed): SIGKILL

  Application: handle SIGTERM gracefully:
  @PreDestroy
  void shutdown() {
      log.info("Shutdown signal received — draining in-flight requests");
      // Stop accepting new transactions
      // Wait for current transactions to complete (with timeout)
      Duration maxWait = Duration.ofSeconds(30);
      // ... drain logic
      log.info("All in-flight requests completed. Shutting down.");
  }

  ALB deregistration: AWS ALB allows 60 seconds for connection draining
  before deregistering Blue instances from target group.
  → New requests: go to Green only
  → Old requests: complete on Blue within draining window
```

---

### 🔗 Related Keywords

- `Canary Deployment` — gradual alternative to blue-green's instant switch
- `Zero-Downtime Deployment` — the broader goal blue-green achieves
- `Graceful Shutdown` — critical for safe traffic cutover without dropping in-flight requests
- `Feature Flags` — complement to blue-green for controlled feature exposure

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGY     │ Two environments → instant traffic switch │
│ BLUE         │ Currently live (v1)                       │
│ GREEN        │ New version (v2) — tested before switch   │
├──────────────┼───────────────────────────────────────────┤
│ SWITCH       │ Load balancer selector/weight change      │
│ ROLLBACK     │ Switch traffic back to Blue (seconds)     │
├──────────────┼───────────────────────────────────────────┤
│ DB           │ Expand-contract migration (backward compat)│
│ COST         │ 2× infra during transition window         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You use blue-green deployment for `CustomerService`. The v2 (Green) deployment includes a database migration that renames the `email` column to `contact_email`. You switch traffic to Green. 15 minutes later: you discover Green has a bug unrelated to the migration — the password reset endpoint is broken. You roll back to Blue. But Blue's code reads the `email` column which was renamed to `contact_email` by the migration. Blue is now broken too. How do you recover? Design a migration strategy that would have prevented this situation.

**Q2.** Your blue-green deployment uses DNS cutover (old school approach: change DNS A record from Blue IP to Green IP). The DNS TTL is set to 300 seconds. Describe the user experience during the 300-second propagation window: what percentage of users see Blue vs Green at different points during propagation, and how does this create a "split-brain" period? Compare this to load balancer weight-based cutover. Why do most modern blue-green implementations prefer load balancer cutover over DNS cutover?
