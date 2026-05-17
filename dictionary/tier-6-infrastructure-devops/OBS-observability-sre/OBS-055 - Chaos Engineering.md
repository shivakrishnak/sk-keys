---
id: OBS-055
title: Chaos Engineering
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-001, OBS-012, OBS-020, OBS-035, OBS-054
used_by: OBS-051
related: OBS-030, OBS-040, OBS-047
tags:
  - observability
  - reliability
  - devops
  - sre
  - intermediate
  - operational
  - chaos-engineering
  - production
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /observability-sre/chaos-engineering/
---

# OBS-055 - Chaos Engineering

⚡ TL;DR - Chaos engineering is the discipline of
deliberately injecting controlled failures into a
system to discover weaknesses before production
incidents do. The core loop: form a hypothesis ("the
system handles database failover within 30s"), design
a minimal blast-radius experiment, run it, observe
whether the hypothesis holds, and fix what breaks.

> **See also:** OBS-035 (Chaos Engineering for Observability)
> focuses on validating that your observability stack
> detects and surfaces failures correctly. This entry
> covers the general chaos engineering practice: GameDays,
> fault injection, hypothesis-driven experiments, blast
> radius management, and the organizational maturity model.

| #055            | Category: Observability & SRE                                                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | What Is Observability, SLO, Error Budget, Chaos Engineering for Observability, Error Budgets |                 |
| **Used by:**    | Reliability Mental Model                                                                     |                 |
| **Related:**    | Alerting Fundamentals, SRE Book Core Principles, Distributed Tracing System Architecture     |                 |

---

### 🔥 The Problem This Solves

**THE RESILIENCE TESTING GAP:**
Software teams write unit tests (does this function work?),
integration tests (do these components work together?),
and load tests (does this handle the expected volume?).
None of these answer: "What happens when a downstream
service hangs for 60 seconds? When the database leader
election takes 45 seconds? When a network partition
isolates one availability zone?"

These failure modes are rare in normal operation but
devastating when they happen. The system architecture
may theoretically handle them (circuit breakers are
configured, retries are implemented) but the actual
behavior under these conditions has never been observed.

**THE DISCOVERY MOMENT:**
Netflix (2011) coined "chaos engineering" when they built
Chaos Monkey - a tool that randomly terminates production
instances. The forcing function: if instances can fail
randomly in production, and they do periodically, then
the system must be designed to tolerate it. The only
way to know it actually tolerates it is to test it.
This was a radical departure: from "avoid failure" to
"inject failure under controlled conditions to learn."

**THE CORE INSIGHT:**
Chaos engineering is not about "breaking things for fun."
It is about the risk-reduction argument: a controlled
experiment in a maintenance window with blast radius
limited to < 1% of traffic is far lower risk than the
first time the failure happens unexpectedly at 2am on
a Friday during peak load. The controlled experiment
has a prepared observer, defined rollback plan, and
constrained scope. The uncontrolled production failure
has none of these.

---

### 📘 Textbook Definition

**Chaos engineering** is the discipline of experimenting
on a distributed system to build confidence in the
system's ability to withstand turbulent conditions in
production. Coined by Netflix, it formalizes the process
of injecting failures - network latency, pod termination,
CPU saturation, dependency unavailability - under controlled
conditions to discover weaknesses before they manifest as
production incidents. The practice follows a hypothesis-
driven scientific method: define steady state, hypothesize
behavior under failure, run a minimal blast-radius experiment,
observe whether the hypothesis holds, and harden the system
against discovered weaknesses. At organizational scale,
chaos engineering progresses through maturity levels from
manual game days to automated continuous chaos in production.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Chaos engineering is deliberately breaking your system in
a controlled way to find the weaknesses before production
finds them for you, uncontrolled.

**One analogy:**

> Chaos engineering is like fire drills. Fires are rare
> but catastrophic. Fire drills expose whether evacuation
> routes are blocked, whether people know the assembly point,
> whether the alarm is audible. The drill is uncomfortable
> and mildly disruptive (blast radius: 15 minutes of lost
> productivity). The alternative is discovering these
> failures during an actual fire. The chaos experiment
> is the fire drill for your distributed system.

---

### 🔩 First Principles Explanation

**THE HYPOTHESIS-DRIVEN EXPERIMENT MODEL:**

```
Five-step experiment process:

1. DEFINE STEADY STATE
   What does "normal" look like?
   Measurable: p99 latency < 200ms, SLI > 99.9%
   Baseline: record steady state metrics for 30 min before

2. FORM HYPOTHESIS
   "We believe that if [failure condition], then
    [observable behavior], because [mechanism]."

   Example:
   "We believe that if the payment-processor service
    becomes unavailable (HTTP 503 for all requests),
    then checkout will return a cached result within
    500ms for 90% of users, because the circuit breaker
    opens after 5 failures and the 5s fallback cache
    activates, and the SLI will remain > 99.5%, because
    the fallback serves the majority of traffic."

3. DESIGN EXPERIMENT
   Define:
   - Failure type (network partition, latency, HTTP error,
     pod kill, CPU saturation, disk fill)
   - Blast radius (1 pod, 1 AZ, 10% of requests)
   - Duration (2 minutes, 5 minutes)
   - Rollback trigger (if SLI drops below 99.0%: abort)
   - Observer role (who watches and calls abort if needed)

4. RUN EXPERIMENT
   Inject failure → observe metrics → record results
   Rollback immediately if rollback trigger fires.

5. LEARN AND HARDEN
   Did hypothesis hold?
   YES → confidence increased, document results
   NO  → VULNERABILITY FOUND. Fix before re-running.
         Root cause: circuit breaker not triggering?
                     Cache TTL too short?
                     Retry storm amplifying failures?
```

**THE BLAST RADIUS MATRIX:**

```
               IMPACT TO USERS
               Low          Medium       High
CONTROL    ┌───────────┬────────────┬───────────┐
High       │ START HERE│ Careful    │ NEVER     │
(staged)   │ 1 pod kill │ 1 AZ down  │ Multi-AZ  │
           ├───────────┼────────────┼───────────┤
Medium     │ OK with   │ Risky,     │ NEVER     │
(limited)  │ monitoring│ with SRE   │           │
           ├───────────┼────────────┼───────────┤
Low        │ Risky     │ NEVER      │ NEVER     │
(uncontrolled│        │            │           │
           └───────────┴────────────┴───────────┘

Rule: start in the bottom-left (high control, low impact)
      and progressively move up-right as confidence grows.
      NEVER move diagonally more than one cell per experiment.
```

**FAULT INJECTION TAXONOMY:**

```
Network-level faults:
  - Latency injection (add 100ms, 500ms, 2s)
  - Packet loss (drop 1%, 10% of packets)
  - Network partition (block traffic between services)
  - DNS failure (return NXDOMAIN for service discovery)
  - Bandwidth limitation (throttle to 10% of capacity)

Compute-level faults:
  - Pod/container termination
  - CPU stress (burn 80% CPU for 60 seconds)
  - Memory pressure (allocate until OOM)
  - Disk fill (write large files until disk full)
  - Clock skew (advance time by 60 seconds)

Application-level faults:
  - HTTP error injection (return 500 for N% of requests)
  - Response delay injection (delay by X ms)
  - Dependency unavailability (kill downstream service)
  - Queue depth injection (insert N messages in dead letter)
  - Database connection pool saturation

State-level faults:
  - Leader election forced (kill primary pod)
  - Cache eviction (flush Redis/Memcached)
  - Configuration invalidation (delete ConfigMap)
  - Secret rotation (rotate credentials mid-operation)
```

---

### 🧪 Thought Experiment

**THE DATABASE FAILOVER EXPERIMENT:**

Hypothesis: "The checkout service handles PostgreSQL primary
failover within 30 seconds with < 5% error rate spike
because: (1) the read replica provides read fallback,
(2) the connection pool retries within 30s,
(3) the Patroni leader election completes within 15s."

**EXPERIMENT DESIGN:**

```
Blast radius: minimal
  Target: checkout-db-primary pod (single pod kill)
  Impact scope: write operations to checkout DB only
               (read operations route to replica)
  Duration: self-recovering (Patroni re-elects in ~15s)

Observer: SRE engineer watching checkout_latency and
          checkout_error_rate dashboards

Rollback trigger: error_rate > 5% for > 2 minutes
  (manual: SRE force-kills the pod restart if needed)

Steady state baseline (30 min prior):
  p99 latency: 180ms
  error rate: 0.1%

Injection: kubectl delete pod checkout-db-primary
```

**RESULTS OBSERVED:**

```
T+0s:  kubectl delete executed
T+2s:  Connection pool detects primary unavailable
T+4s:  New writes start failing (no primary available)
T+4s:  Error rate spikes to 8% (ABOVE 5% ROLLBACK TRIGGER)
T+6s:  Observer DOES NOT abort (wants to see resolution)
       [MISTAKE: rollback trigger should be automated]
T+14s: Patroni leader election completes
T+15s: Connection pool reconnects to new primary
T+17s: Error rate recovers to 0.2%

Total affected window: 13 seconds
Total error rate spike: 8% peak

HYPOTHESIS FAILED:
  Expected: < 5% error rate spike
  Actual: 8% error rate spike

ROOT CAUSE: Connection pool has 20 connections, all trying
  to reconnect to old primary simultaneously.
  Thundering herd: 20 simultaneous reconnect attempts
  amplify the 4-17s gap to 8% error rate.

FIX: Add jitter to connection pool reconnect timeout
  (exponential backoff: 100ms ± 50ms jitter per connection)
  Re-run experiment after fix. Expect < 2% error rate.
```

---

### 🧠 Mental Model / Analogy

> Chaos engineering is like a medical stress test before
> surgery. Before high-risk surgery, cardiologists run a
> stress test to understand how the heart behaves under
> load. The stress test is uncomfortable and monitored -
> but vastly safer than discovering a problem during surgery.
> The chaos experiment is the stress test for your system.
> The goal is not to make the system fail - it is to expose
> how the system behaves under stress in a setting where you
> can observe, control, and reverse the experiment.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Chaos engineering is deliberately breaking something in
your system in a controlled, small-scale way to see if
it recovers properly. If it does: great, you have evidence
it works. If it doesn't: you found a bug before a real
incident did.

**Level 2 - How to use it (junior developer):**
Start with manual experiments in staging. Kill one pod.
Check if the service remains available. Check the health
check endpoint. Check the Grafana dashboard. Did the SLI
stay above the target? Did the alert fire as expected?
Document the hypothesis and results. If it failed: fix
the issue before running in production.

**Level 3 - How it works (mid-level engineer):**
Use a chaos engineering tool (Chaos Monkey, Litmus Chaos,
Chaos Mesh, Gremlin) to inject failures programmatically.
Define experiments as code: YAML spec with fault type,
target selector, duration, abort conditions. Run with
a dedicated observer who has authority to abort if
the rollback trigger fires. Always measure steady state
before injection to establish baseline. Record all results
in a chaos experiment log.

**Level 4 - Why it was designed this way (senior/staff):**
The hypothesis-driven model is what separates chaos
engineering from random destruction. A hypothesis makes
the experiment falsifiable: you know in advance what
"success" means (hypothesis holds) and what "failure"
means (vulnerability found). This transforms the experiment
from "let's see what happens" to "we expected X, observed
Y, and the gap is the learning." The blast radius constraint
is the safety mechanism: limiting scope ensures that
experiments cannot cascade into full outages. The formal
scientific method makes chaos engineering defensible to
leadership - not "we're breaking production" but "we're
running a controlled experiment with defined rollback
conditions."

**Level 5 - Mastery (distinguished engineer):**
At organizational maturity level 4 (automated continuous
chaos), experiments run continuously in production as
background processes, validating steady-state assumptions
continuously. This requires: (1) automated experiment
selection (which experiments are safe to run given current
budget and load); (2) automated rollback (not manual observer);
(3) experiment library version control; (4) metrics correlation
(experiment run was correlated with SLI change, enabling
root cause without manual inspection). The organizational
enabler: a "chaos engineering platform" maintained by the
SRE or platform team, with a self-service experiment catalog
for application teams.

---

### ⚙️ How It Works (Mechanism)

**LITMUS CHAOS (Kubernetes-native fault injection):**

```
Architecture:

  Litmus Chaos Operator (controller)
    Watches: ChaosEngine CRDs (experiment specs)
    Creates: ExperimentJob pods (fault injectors)
    Updates: ChaosResult CRDs (experiment outcomes)

  Experiment execution flow:
    1. Engineer creates ChaosEngine YAML
    2. Operator detects ChaosEngine, validates blast radius
    3. Operator creates pre-chaos check job
       → verifies steady state (SLI > target)
    4. Operator creates chaos job
       → injects fault (network delay, pod kill, etc.)
    5. Chaos job runs for specified duration
    6. Operator creates post-chaos check job
       → verifies recovery (SLI > target again)
    7. ChaosResult updated with PASS/FAIL verdict
    8. Prometheus metrics emitted:
       litmuschaos_experiment_verdict{result="pass|fail"}
       litmuschaos_experiment_count

  Integration with SLO:
    Pre-chaos check: query Prometheus for SLI value
    Abort condition: SLI < abort_threshold → cancel experiment
    Post-chaos check: SLI recovered? → PASS
```

**GAMEDAY ORGANIZATION:**

```
GameDay is a structured chaos exercise (half/full day):

  Pre-GameDay (1 week before):
    - Define scenario: "Payment processor goes dark for 10min"
    - List participating services and owners
    - Document expected behaviors from each team
    - Define success criteria and rollback plan
    - Notify all teams (GameDay is not a surprise)
    - Ensure monitoring is healthy before the day

  GameDay execution:
    10:00 - Pre-flight checks: all dashboards healthy
    10:15 - Inject failure as planned
    10:15-10:25 - Observe: each team monitors their service
    10:25 - Remove failure (or self-recovers)
    10:25-10:40 - Observe recovery
    10:40 - Discussion: what happened vs. expected?
    11:00 - Document findings: vulnerabilities found,
            action items, timeline for fixes

  Post-GameDay (1 week after):
    - Engineering action items tracked in sprint backlog
    - Follow-up experiment: re-run after fixes applied
    - Results documented in chaos engineering log
```

---

### 💻 Code Example

**Example 1 - BAD: Uncontrolled chaos (no hypothesis, no rollback)**

```bash
# BAD: random pod killing with no hypothesis or rollback plan
# This is not chaos engineering - it's just breaking things

kubectl delete pod $(
  kubectl get pods -n production | shuf | head -1 | awk '{print $1}'
)

# Problems:
# 1. No hypothesis about expected behavior
# 2. No blast radius control (random pod selection)
# 3. No rollback plan (no abort trigger)
# 4. No observer watching for cascading failures
# 5. No documentation of results
# This is how you cause a production incident,
# not how you prevent one.
```

**Example 2 - GOOD: Hypothesis-driven Litmus Chaos experiment**

```yaml
# chaos-experiment.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: checkout-db-failover-test
  namespace: production
  annotations:
    # Document the hypothesis
    hypothesis: >
      Checkout handles DB failover in < 30s with
      < 5% error rate spike due to Patroni re-election
      completing within 15s and connection pool retry.
    blast-radius: "single pod - checkout-db-primary only"
    rollback-trigger: "checkout error_rate > 5% for 2m"
spec:
  appinfo:
    appns: production
    applabel: "app=checkout-db"
    appkind: statefulset

  # CRITICAL: abort if steady state is already unhealthy
  jobCleanUpPolicy: delete

  monitoring: true
  engineState: active

  components:
    runner:
      image: litmuschaos/chaos-runner:latest

  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            # Target ONLY the primary (label: role=primary)
            - name: TARGET_PODS
              value: "checkout-db-primary-0"
            - name: CHAOS_INTERVAL
              value: "60" # wait 60s, then re-check
            - name: TOTAL_CHAOS_DURATION
              value: "30" # inject fault for 30 seconds
            - name: FORCE
              value: "false" # graceful shutdown (not SIGKILL)

            # BLAST RADIUS CONTROL
            - name: PODS_AFFECTED_PERC
              value: "100" # 100% of matched pods (= 1 pod)

        probe:
          # Pre-chaos steady state check
          - name: checkout-sli-check
            type: promProbe
            mode: Edge # check before AND after
            promProbe/inputs:
              endpoint: >
                http://prometheus:9090
              query: >
                sum(rate(
                  http_requests_total{
                    job="checkout",
                    status!~"5.."
                  }[5m]
                ))
                /
                sum(rate(
                  http_requests_total{job="checkout"}[5m]
                ))
              comparator:
                type: float
                criteria: ">="
                value: "0.995" # abort if SLI < 99.5%
            runProperties:
              probeTimeout: 10
              interval: 30
              attempt: 2
```

**Example 3 - Chaos Mesh network latency injection**

```yaml
# network-chaos.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: payment-latency-test
  namespace: production
spec:
  action: delay
  mode: fixed
  value: "1" # affect exactly 1 pod
  selector:
    namespaces:
      - production
    labelSelectors:
      "app": "payment-processor"
  delay:
    latency: "2000ms" # inject 2s latency
    correlation: "100" # 100% of packets affected
    jitter: "500ms" # ±500ms variance
  duration: "5m" # run for 5 minutes
  scheduler:
    cron: "@once" # run once, not recurring


# MONITOR DURING THIS EXPERIMENT:
# watch 'curl -s http://grafana:3000/api/datasources/...'
# Expected: circuit breaker fires after 5 failures (5 × 2s)
# Expected: checkout falls back to cached payment result
# Expected: SLI recovers to > 99.9% after circuit opens
```

**Example 4 - FAILURE: Blast radius escaped (no abort trigger)**

```
Scenario:
  Team runs a chaos experiment: "kill one payment pod."
  No automated abort trigger configured.
  No observer watching during the experiment.

What happened:
  T+0s:  Payment pod killed
  T+5s:  Kubernetes scheduler tries to reschedule pod
  T+5s:  Image pull fails (Docker Hub rate limit hit)
  T+30s: All retries exhausted, pod stays in ImagePullBackOff
  T+90s: Circuit breaker not configured - requests keep failing
  T+5m:  Error rate at 100% for payment-requiring flows
  T+8m:  On-call engineer notices (was not watching)
  T+10m: Manual fix: use cached image, pod recovers

Blast radius escaped: 1 pod kill → 10 minutes of outage.

ROOT CAUSE: Chained failure. Chaos experiment assumed
  pod would restart immediately. Did not account for
  image pull dependency. No abort trigger to catch
  the escalation.

FIX: Always configure automated abort triggers:
  if SLI drops below abort_threshold for > 2 minutes:
    → automated rollback (restore pod from backup)
  if experiment duration > max_duration:
    → automated stop
  NEVER rely solely on human observers for abort.
```

---

### ⚖️ Comparison Table

| Resilience Validation Method              | Realism                    | Control             | Learning                   | Effort                  |
| ----------------------------------------- | -------------------------- | ------------------- | -------------------------- | ----------------------- |
| **Chaos engineering (hypothesis-driven)** | High (production behavior) | High (blast radius) | High (specific hypotheses) | High (design + observe) |
| Load testing                              | Medium (volume only)       | High                | Medium                     | Medium                  |
| Tabletop exercise (GameDay lite)          | Low (theoretical)          | Full                | Medium                     | Low                     |
| Waiting for production incidents          | Very high                  | None                | High (expensive)           | Zero prep               |
| Integration tests                         | Low (mocked deps)          | Full                | Low (synthetic)            | Medium                  |

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                                                                                                                                 |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chaos engineering = randomly breaking production                 | Chaos engineering is a scientific discipline with defined hypotheses, controlled blast radius, and abort triggers. Random destruction is not chaos engineering - it is recklessness                     |
| Chaos engineering requires specialized tooling                   | GameDays can start with `kubectl delete pod` and a Grafana dashboard. Tooling (Litmus Chaos, Chaos Mesh, Gremlin) adds automation and observability but is not required to start                        |
| You need mature infrastructure before starting chaos engineering | The opposite: start when infrastructure is young, before bad assumptions calcify into production debt. Discovering that your circuit breaker isn't configured is better before your first traffic spike |
| Chaos engineering is for Netflix-scale organizations             | The blast radius principle works at any scale. A 5-person startup running 10 services can run `kubectl delete pod` in staging to validate recovery behavior                                             |

---

### 🚨 Failure Modes & Diagnosis

**Hypothesis Never Fails (Experiments Too Easy)**

**Symptom:**
The team runs chaos experiments every sprint. Every experiment
passes. The team feels confident. Then a real production
incident discovers a failure mode that no experiment covered.

**Root Cause:**
Experiments are designed to pass, not to discover. The
team tests only failure modes they already know the system
handles. They avoid experiments with uncertain outcomes
because a failed experiment reflects badly on the team.
"Success theater" - running experiments to prove resilience
rather than to find weaknesses.

**Fix:**
Follow the "30% failure rate" heuristic: if fewer than 30%
of new experiments reveal a vulnerability, the experiments
are too safe. Aggressively explore unknown territory:
"What happens when two dependencies fail simultaneously?"
"What happens when the experiment runs during peak load
instead of off-hours?" "What happens after 5 minutes instead
of 2 minutes?" Celebrate failed hypotheses as valuable
findings, not as failures of the team.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - the monitoring stack used to
  observe experiments
- `SLO` - the steady state definition for abort triggers
- `Error Budget` - chaos experiments consume error budget;
  plan experiments when budget is healthy
- `Chaos Engineering for Observability` (OBS-035) - the
  observability-specific variant
- `Error Budgets` - the budget governance that determines
  when chaos experiments are safe to run

**Builds On This (learn these next):**

- `Reliability Mental Model` - chaos engineering as the
  "learning force" in the four-force reliability model

**Alternatives / Comparisons:**

- `Alerting Fundamentals` - the detection layer that chaos
  experiments validate
- `SRE Book Core Principles` - the organizational model
  chaos engineering is part of
- `Distributed Tracing System Architecture` - the
  observability instrumentation that makes chaos results
  visible

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ FIVE STEPS    │ 1. Define steady state (measurable)   │
│               │ 2. Form hypothesis (if X then Y)      │
│               │ 3. Design experiment (blast radius)   │
│               │ 4. Run with automated abort trigger   │
│               │ 5. Learn: fix if hypothesis fails     │
├───────────────┼────────────────────────────────────────┤
│ BLAST RADIUS  │ Start: 1 pod, staging, off-peak       │
│ PROGRESSION   │ Then: 1 pod, production, with observer│
│               │ Then: 1 AZ, production, with SLO gate │
│               │ NEVER: multi-AZ without full rehearsal│
├───────────────┼────────────────────────────────────────┤
│ ABORT TRIGGER │ MUST be automated, not manual observer │
│               │ Trigger: SLI < abort_threshold for 2m │
│               │ Trigger: experiment > max_duration    │
├───────────────┼────────────────────────────────────────┤
│ FAULT TYPES   │ Network: latency, partition, loss     │
│               │ Compute: pod kill, CPU/mem stress     │
│               │ App: HTTP error %, response delay     │
│               │ State: leader kill, cache flush       │
├───────────────┼────────────────────────────────────────┤
│ HEALTH CHECK  │ Run experiments only when error budget │
│               │ > 50% remaining. Never during an      │
│               │ active incident.                      │
├───────────────┼────────────────────────────────────────┤
│ SUCCESS METRIC│ 30%+ of new experiments should fail   │
│               │ (find vulnerabilities). Below 30%:   │
│               │ experiments are too safe.             │
├───────────────┼────────────────────────────────────────┤
│ ONE-LINER     │ "Inject failure under control before  │
│               │ production injects it without control"│
├───────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE  │ Reliability Mental Model              │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Always form a hypothesis before running an experiment.
   A hypothesis makes the experiment falsifiable: you know
   what success looks like before you start.
2. Automated abort trigger is non-negotiable. Manual observer
   is not sufficient. Blast radius escapes happen in seconds.
3. Celebrate failed hypotheses. If 100% of your experiments
   pass, you're proving what you already know - not discovering
   what you don't.

**Interview one-liner:**
"Chaos engineering is hypothesis-driven failure injection:
define steady state, hypothesize how the system handles
a specific failure (e.g., 'checkout survives DB failover
in < 30s with < 5% error rate spike'), design minimal
blast-radius experiment (1 pod, 1 AZ, N% of requests),
run with automated abort trigger (SLI < threshold for 2m:
cancel), and learn: failed hypothesis = vulnerability found,
fix it. Key principle: controlled 5-minute experiment in
maintenance window is lower risk than first uncontrolled
production failure at 2am. Start in staging, graduate to
production with SLO gates. 30% failure rate for new
experiments is a healthy sign - too few failures means
experiments are too safe."
