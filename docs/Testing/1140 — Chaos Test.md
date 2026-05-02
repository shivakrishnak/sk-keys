---
layout: default
title: "Chaos Test"
parent: "Testing"
nav_order: 1140
permalink: /testing/chaos-test/
number: "1140"
category: Testing
difficulty: ★★★
depends_on: Stress Test, Distributed Systems, Observability
used_by: SRE, Resilience Engineering, Netflix, Google
related: Chaos Monkey, GameDay, Fault Injection, Circuit Breaker, Chaos Engineering
tags:
  - testing
  - chaos-engineering
  - resilience
  - sre
  - distributed-systems
---

# 1140 — Chaos Test

⚡ TL;DR — Chaos testing deliberately injects failures (kill a pod, saturate a network, corrupt a dependency) into a running system to verify resilience mechanisms work and discover unknown failure modes before users do.

| #1140 | Category: Testing | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Stress Test, Distributed Systems, Observability | |
| **Used by:** | SRE, Resilience Engineering, Netflix, Google | |
| **Related:** | Chaos Monkey, GameDay, Fault Injection, Circuit Breaker, Chaos Engineering | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A distributed system has 20 microservices, each with 99.9% uptime. The probability of at least one service failing in any hour: 1 - (0.999)^20 = 2%. At 2% hourly failure rate, the system experiences a service failure approximately every 2 days. The team has circuit breakers and retry logic — but they've never been tested with real failures. Do the circuit breakers actually prevent cascade failures? Do retries have jitter? Does the system recover automatically? Without chaos testing, you only know when a real failure hits production.

THE BREAKING POINT:
Distributed systems fail in ways that are impossible to reason about statically. A network partition between two services in the same datacenter might trigger a behavior that was never considered in the circuit breaker configuration. The only way to know how the system responds to a failure is to inject that failure and observe. "Hope for resilience" is not a strategy; "verify resilience" is.

THE INVENTION MOMENT:
Netflix's Chaos Monkey (2010) by Yury Izrailevsky and Ariel Tseitlin was the first automated chaos tool: it randomly terminates production instances during business hours. The thesis: if you know that instances can die randomly, you engineer for it. Systems that can survive random instance death are fundamentally more resilient than systems that assume instances never die.

### 📘 Textbook Definition

**Chaos engineering** is the discipline of experimenting on a system to build confidence in its ability to withstand turbulent conditions in production. A **chaos test** (chaos experiment) follows the scientific method: (1) define the **steady state** (measurable normal behavior — e.g., p99 < 200ms, error rate < 0.1%); (2) hypothesize that the steady state continues when a specific **failure is injected**; (3) inject the failure in a controlled environment; (4) observe whether steady state is maintained; (5) document the finding. Chaos engineering is NOT about breaking things randomly — it's about controlled, hypothesis-driven failure injection to verify resilience.

### ⏱️ Understand It in 30 Seconds

**One line:**
Chaos test = deliberately break something, verify the system survives, find out what you didn't know you didn't know.

**One analogy:**
> A fire drill is chaos engineering: you deliberately trigger the fire alarm (inject a failure), verify people evacuate safely (steady state maintained), and discover weaknesses before a real fire (the blocked stairwell, the broken exit sign). Chaos engineering is the fire drill for distributed systems.

**One insight:**
Chaos engineering is not just about the failures you can think of — it's about discovering **unknown unknowns**. The most valuable chaos experiments reveal failure modes that the architects never considered. "We didn't know the health check endpoint queried the database and timing out under load caused the circuit breaker to open on healthy services."

### 🔩 First Principles Explanation

CHAOS EXPERIMENT PROTOCOL (scientific method):
```
1. DEFINE STEADY STATE:
   - p99 API latency < 200ms
   - Error rate < 0.1%
   - All services returning 200 on /health
   
2. FORM HYPOTHESIS:
   "Steady state continues when the payment service is unavailable"
   
3. INJECT FAILURE:
   - Kill payment service pods (kubectl delete pod payment-service-*)
   - OR: network partition (iptables DROP on payment service port)
   - OR: CPU saturation (stress-ng --cpu 100%)
   - OR: disk full (fill /var/log with junk)
   - OR: high latency (tc netem delay 500ms)
   
4. OBSERVE:
   - Does the product listing page still work? (expected: yes, degraded)
   - Does checkout still work? (expected: graceful error "payment unavailable")
   - Does the system recover after payment service returns?
   - Any cascade failures to unrelated services?
   
5. VERIFY OR FALSIFY:
   PASS: checkout shows graceful error, other features unaffected, recovery in 10s
   FAIL: cascade to product service, OR recovery required manual restart
   
6. DOCUMENT AND FIX:
   Finding: Cache service not isolated from payment timeout → cascade
   Fix: Add bulkhead for payment service calls
```

CHAOS TOOLS:
```
Kubernetes:
  - Chaos Mesh (CNCF): pod kill, network partition, disk I/O
  - Litmus Chaos (CNCF): workflow-based chaos experiments
  - Gremlin: enterprise SaaS chaos platform
  
Netflix OSS:
  - Chaos Monkey: random EC2 instance termination
  - Chaos Kong: terminate entire AWS regions
  
AWS:
  - Fault Injection Simulator (FIS): AWS-native chaos for EC2, RDS, ECS

Application level:
  - Toxiproxy: controllable proxy that injects latency, errors
  - Failsafe: Java library for resilience with testable failure modes
```

THE TRADE-OFFS:
Gain: Discover unknown failure modes before production; verify resilience mechanisms work; build organisational confidence in system reliability.
Cost: Risk of unintended impact (blast radius must be controlled); requires mature observability to know if steady state is maintained; organisational maturity (must be ready to not panic when failures are injected).

### 🧪 Thought Experiment

THE HEALTH CHECK CASCADE BUG:
```
System: 5 microservices, each with /health endpoint
Health check implementation:
  /health → SELECT 1 FROM users LIMIT 1  (DB connectivity check)
  
Chaos experiment: saturate order-service DB (inject slow queries)
  Expected: order-service degrades, other services unaffected
  Actual: ALL services degrade
  
Root cause:
  order-service DB slow → order-service /health times out
  Load balancer health check fails → removes order-service instances
  User service /health: also queries DB, and users DB is on same cluster
  DB cluster hit by massive load from all health checks → cascade

This was NEVER in the architecture documentation.
The chaos experiment revealed an undocumented cross-dependency.

Fix: health check should NOT query the database
      Use application-level check: /health → return OK if app is running
      Separate readiness check for DB: /ready (only used by Kubernetes)
```

### 🧠 Mental Model / Analogy

> Chaos engineering is **vaccination**: you introduce a controlled, weakened version of a pathogen (failure) so the system (immune system = resilience mechanisms) can develop an appropriate response. The goal is not to cause disease — it's to prepare the response so that when the real pathogen arrives, the reaction is known, practiced, and effective.

> The Simian Army (Netflix's suite of chaos tools: Chaos Monkey, Latency Monkey, Conformity Monkey, Security Monkey) is the systematic program of injecting different "pathogens" — not just instance death, but also latency, security misconfigurations, and conformity violations.

Where the analogy breaks down: vaccines provide full immunity; chaos experiments reduce blast radius and improve recovery, but don't eliminate all failure scenarios.

### 📶 Gradual Depth — Four Levels

**Level 1:** Chaos testing means deliberately breaking things in your system to see if your safety nets work. Like pulling a fire alarm — not during a real fire, but to test that the alarms ring and people know how to evacuate.

**Level 2:** Start small: inject failures in staging, not production. Begin with simple experiments: kill one pod (`kubectl delete pod`), verify the deployment auto-heals in < 60 seconds. Progress to: network partition, service dependency failures, database failures. Define steady state before each experiment (what does "working" look like in metrics?). Use GameDays: team exercises where specific failures are injected and teams respond in real time.

**Level 3:** Chaos Mesh setup in Kubernetes: define `PodChaos` (kill pods), `NetworkChaos` (partition, latency, bandwidth limit), `IOChaos` (disk failure), `StressChaos` (CPU/memory pressure) as Kubernetes CRDs. Schedule experiments: run chaos experiments in CI (staging) on every release. Blast radius control: namespace scoping, pod label selectors. Observability requirement: chaos experiments are useless without metrics to observe — you need Prometheus/Grafana dashboards showing steady state before you can know if steady state is maintained during chaos.

**Level 4:** Chaos engineering maturity model: (1) Reactive: incidents happen → fix → no test; (2) Proactive: GameDays → manual chaos; (3) Continuous: automated chaos in staging on every deployment; (4) Production chaos: automated experiments in production with blast radius control (Netflix, Google). The key insight from Google's SRE book: "Hope is not a strategy." The reliability of a distributed system cannot be mathematically derived from the reliability of its components (due to correlated failures, cascade effects, partial failures). Empirical validation through chaos engineering is the only reliable method. AWS re:Invent 2022: "We chaos test every service before it handles real customer traffic. Our production readiness review requires proof of chaos experiment results."

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│               CHAOS MESH EXPERIMENT FLOW                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Steady state: p99 < 200ms, error rate < 0.1%           │
│  Measured via: Prometheus/Grafana                       │
│                                                          │
│  PodChaos CR applied:                                   │
│  apiVersion: chaos-mesh.org/v1alpha1                    │
│  kind: PodChaos                                         │
│  spec:                                                   │
│    action: pod-kill                                     │
│    selector:                                             │
│      namespaces: [staging]                              │
│      labelSelectors:                                    │
│        app: payment-service                             │
│    scheduler: {cron: '@every 5m'}  # kill every 5 min  │
│                                                          │
│  Observation window (30 min):                           │
│    - Kubernetes: detects pod missing → reschedule       │
│    - Other services: payment circuit breaker opens      │
│    - Checkout: returns "payment temporarily unavailable"│
│    - Other features: unaffected                         │
│    - Recovery: new pod ready in 45s                     │
│                                                          │
│  Result: steady state maintained → PASS                 │
└──────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

```
CHAOS GAMEDAY: "What happens when our primary database is unavailable?"

Pre-game (1 week before):
  1. Define steady state: homepage loads (200), search works, login works
  2. Hypothesis: checkout fails gracefully; browsing continues; recovery in < 2 min
  3. Set up Grafana dashboard with steady state metrics

GameDay:
  9:00 AM: Team assembles, roles assigned (chaos engineer, SRE, developer, PM)
  9:05 AM: Baseline verified (all green)
  9:10 AM: CHAOS INJECTED: network partition to primary DB (iptables)
  9:10-9:20: Observe:
    - DB failover triggered: replica promoted (30s) ← longer than expected
    - During failover: checkout fails with 500 (not 503!) ← BUG FOUND
    - Connection pool not releasing during failover ← root cause
    - 95% of traffic recovered after 35s ← acceptable
  9:20 AM: Chaos removed (iptables rule deleted)
  9:20-9:30: Observe recovery:
    - All services recover fully in 2 min ← acceptable

Findings:
  BUG 1: Checkout returns 500 during DB failover (should be 503)
  BUG 2: Connection pool holds connections during failover (should detect failure)
  PASS: Recovery in 2 min as hypothesised
  PASS: Browsing and search continued (read replica not affected)

Action items:
  Fix connection pool detection (HikariCP: keepAliveTime + connectionTimeout)
  Fix error handling: DB exception → 503 not 500
  Schedule follow-up chaos experiment to verify fixes
```

### 💻 Code Example

```yaml
# Chaos Mesh: PodChaos - kill payment service pods
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: kill-payment-pods
  namespace: staging
spec:
  action: pod-kill
  mode: one          # kill one pod at a time
  selector:
    namespaces: [staging]
    labelSelectors:
      "app": "payment-service"
  scheduler:
    cron: "@every 2m"  # kill a pod every 2 minutes

---
# Chaos Mesh: NetworkChaos - inject 500ms latency + 10% packet loss
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: degrade-order-service
  namespace: staging
spec:
  action: delay
  mode: all
  selector:
    namespaces: [staging]
    labelSelectors:
      "app": "order-service"
  delay:
    latency: "500ms"
    correlation: "25"   # 25% correlated with previous latency
    jitter: "100ms"
  loss:
    loss: "10"          # 10% packet loss
  duration: "10m"
```

```bash
# Toxiproxy: controllable proxy for integration test chaos
# Install toxiproxy-server, create proxy for your service
toxiproxy-cli create order-service -l localhost:8001 -u order-service:8080

# Normal: no toxics
curl http://localhost:8001/api/orders  # direct pass-through

# Inject: 1000ms latency with 100ms jitter
toxiproxy-cli toxic add order-service -t latency -a latency=1000 -a jitter=100

# Inject: 30% packet loss (for TCP: causes connection drops)
toxiproxy-cli toxic add order-service -t latency -n packet_loss -a latency=0 -d 0.3

# Inject: reset connection every 10000 bytes (simulate network resets)
toxiproxy-cli toxic add order-service -t reset_peer -a timeout=5000

# Remove toxic (recovery)
toxiproxy-cli toxic remove order-service -n packet_loss
```

### ⚖️ Comparison Table

| Testing Type | What is Tested | Failure Mode | Goal |
|---|---|---|---|
| Unit test | Function logic | Incorrect output | Correctness |
| Integration test | Component interaction | Integration bug | Correctness |
| Load test | Performance at scale | SLA breach | Performance |
| Stress test | Performance beyond max | Breaking point | Capacity |
| **Chaos test** | Resilience under failure | Unknown failure modes | Resilience |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Chaos testing = breaking things randomly" | Chaos engineering is hypothesis-driven and controlled; not random destruction |
| "Chaos tests should have pass/fail criteria" | Chaos tests document what happens; the finding may be "PASS: resilient" or "FAIL: cascade" — both are valuable |
| "Only large companies need chaos testing" | Any distributed system with > 3 services benefits; the simpler the experiment, the more accessible |
| "Chaos testing is only for production" | Start in staging; progress to production only after staging experiments pass |

### 🚨 Failure Modes & Diagnosis

**1. Chaos Experiment Causes Unrecoverable State**

Symptom: After chaos removed, system doesn't recover; requires manual restart.
Prevention: Define and test recovery procedures before chaos experiments. Have rollback plan (re-inject chaos? restore from snapshot?). Run in staging, not production, until recovery procedures are proven.

**2. Chaos Experiment Too Destructive (No Blast Radius Control)**

Symptom: Intended to test payment service; accidentally took down entire cluster.
Prevention: Use Kubernetes namespace selectors. Start with `mode: one` (one pod), not `mode: all`. Test chaos configuration on a single non-critical pod before scheduling.

### 🔗 Related Keywords

- **Prerequisites:** Stress Test, Distributed Systems, Observability, Circuit Breaker
- **Builds on:** Chaos Mesh, Gremlin, Netflix Simian Army, SRE, GameDay
- **Related:** Fault Injection Testing, Property-Based Testing, Resilience Engineering

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Hypothesis-driven failure injection to   │
│              │ verify resilience and find unknown modes  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ You don't know if resilience works until  │
│              │ you test it; unknown unknowns only found  │
│              │ by deliberately causing failure          │
├──────────────┼───────────────────────────────────────────┤
│ PROTOCOL     │ Steady state → Hypothesis → Inject →     │
│              │ Observe → Document → Fix                 │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Chaos Mesh, Litmus (CNCF), Toxiproxy,    │
│              │ Gremlin (enterprise), AWS FIS            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Controlled risk (chaos test) vs          │
│              │ uncontrolled risk (production incident)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Inject failure deliberately to discover │
│              │  what you don't know you don't know"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Bulkhead → SRE/SLO     │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** Netflix's Chaos Kong terminates an entire AWS availability zone (AZ) to test multi-AZ resilience. To run this experiment safely, Netflix requires: (1) circuit breakers verified, (2) graceful degradation proven, (3) AZ-independent data replication, (4) traffic shifting automation tested. Describe the exact sequencing of what happens when an AZ goes down: at t=0, the AZ's EC2 instances stop responding. Describe: (a) how the ELB health checks detect the AZ failure and over what time period, (b) how Route 53 weighted routing shifts traffic to healthy AZs, (c) why DynamoDB global tables (eventual consistency) behave differently from RDS Multi-AZ (synchronous replication) during this failure, and (d) the "recovery" phase — what prevents thundering herd when the AZ comes back online.

**Q2.** Chaos engineering requires observability to know if steady state is maintained. The Principles of Chaos Engineering (principlesofchaos.org) state: "Vary real-world events" — inject CPU saturation, network latency, disk failures, process kills. But the biggest source of unknown unknowns in distributed systems is **partial failure** — a service that is up but degraded (responding with 200 but incorrect data, or with 200 but taking 10× longer for 5% of requests). Describe: (1) why standard health checks (/health → 200) don't detect partial failures, (2) how synthetic transactions (production verification tests) detect partial failures, (3) the concept of "grey failure" in distributed systems research and why it's harder to detect than hard failures, and (4) what chaos experiment you would design specifically to test detection of grey failures.
