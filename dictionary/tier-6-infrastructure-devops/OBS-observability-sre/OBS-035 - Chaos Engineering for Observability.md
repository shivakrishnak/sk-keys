---
id: OBS-035
title: Chaos Engineering for Observability
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-009, OBS-012, OBS-020
used_by: OBS-036, OBS-044, OBS-045
related: OBS-009, OBS-012, OBS-020, OBS-036, OBS-044
tags:
  - observability
  - reliability
  - chaos-engineering
  - testing
  - advanced
  - production
  - deep-dive
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /obs/chaos-engineering-for-observability/
---

# OBS-035 - Chaos Engineering for Observability

⚡ TL;DR - Chaos engineering for observability is the
practice of deliberately injecting faults into a system
to verify that your monitoring, alerting, and runbooks
actually detect and respond to those faults correctly.
It answers: "Do our alerts fire when they should?"
before a real incident answers it for you.

| #035            | Category: Observability & SRE                                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Observability Fundamentals, Alerting Design, Incident Response, Error Budgets |                 |
| **Used by:**    | Post-Mortem Process, Platform Observability Engineering                       |                 |
| **Related:**    | Alerting Design, Incident Response, Error Budgets, Post-Mortem                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every team writes metrics dashboards and alerts with
confidence that "when the database goes down, we'll
see it." But in a real incident:

- The alert fires 8 minutes after the outage began.
  The SLA requires page in < 5 minutes.
- The runbook says "check the database connection
  pool." Nobody has verified whether connection pool
  metrics are actually being collected in production.
- The Grafana dashboard shows "No Data" for 3 of
  the 6 services affected - their metrics exporters
  stopped working 2 months ago. Nobody noticed.
- The alert threshold fires, but it fires for a
  different service than the one that failed, because
  the metrics correlation assumes service A drives
  service B's latency.

These are called "observability blind spots": gaps
between what your team believes the monitoring covers
and what it actually covers. They are only discovered
during real incidents, at the worst possible time.

**THE INVENTION:**
Chaos engineering for observability applies the same
discipline used for resilience testing (Chaos Monkey,
Chaos Toolkit) specifically to the observability stack:
deliberately inject failures and verify that dashboards
show the correct state, alerts fire within the required
time, runbooks lead to correct actions, and on-call
engineers are notified correctly. Done in a controlled
way (on non-production, during GameDay exercises, with
rollback plans), it identifies blind spots before
they become costly production incidents.

---

### 📘 Textbook Definition

**Chaos engineering** is the discipline of experimenting
on a system to build confidence in its ability to
withstand turbulent conditions. Applied to observability:
it verifies that the monitoring system correctly observes
and alerts on faults.

**Key concepts:**

- **Hypothesis-driven**: formulate a specific prediction
  before injecting the fault. "When the database
  connection pool exhausts, the alert
  `HighDatabaseConnectionPoolUsage` should fire within
  2 minutes." After the experiment: did it? If not:
  fix the alert.

- **GameDay**: a scheduled event where an engineering
  team runs chaos experiments in a controlled environment
  (staging, canary, or production with customer traffic
  isolated), validates observability coverage, and
  documents findings.

- **Blast radius control**: start with the smallest
  possible fault (single instance, short duration)
  and escalate only if the system handles it as expected.
  Always have a rollback command ready.

- **Steady state hypothesis**: define the system's
  normal behaviour before the experiment. The experiment
  is valid only if the system starts in steady state
  and returns to it after fault injection.

**Fault types for observability validation:**

| Fault type                   | What it tests                          |
| ---------------------------- | -------------------------------------- |
| Kill a pod/service           | Service discovery, upstream alerts     |
| Introduce latency (tc netem) | P99 latency alerts, RED metric alerts  |
| Drop network packets         | Timeout alerts, retry metric alerts    |
| Exhaust connection pool      | Database alert coverage                |
| Fill disk                    | Storage monitoring coverage            |
| Spike CPU (stress-ng)        | CPU saturation alerts                  |
| Return HTTP 500 errors       | Error rate alerts                      |
| Kill metrics exporter        | Monitoring system itself (absent data) |

**Tools:**

- **Chaos Monkey** (Netflix): randomly terminates
  instances in production. Tests resilience AND
  monitoring response simultaneously.
- **Chaos Toolkit**: open-source chaos platform.
  Declarative YAML experiments with rollback.
- **Litmus Chaos** (CNCF): Kubernetes-native chaos
  engineering. Pre-built fault types for Kubernetes.
- **Gremlin**: commercial chaos platform with
  observability integrations.
- **toxiproxy** (Shopify): network proxy that injects
  latency, packet loss, bandwidth limits for testing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Chaos engineering for observability is a fire drill
for your monitoring: deliberately start a fire to
prove that the smoke detector works, the alarm rings,
and the evacuation plan is posted on the wall.

> The difference between chaos engineering for
> resilience and chaos engineering for observability:
>
> Resilience chaos: "Does the system keep working
> when a component fails?" Verifies the system's
> fault tolerance.
>
> Observability chaos: "Does the MONITORING SYSTEM
> correctly detect when a component fails?" Verifies
> the monitoring stack's coverage and accuracy.
>
> A system can be both resilient AND invisible to
> monitoring. Observability chaos engineering tests
> the visibility, not the resilience.

---

### 🔩 First Principles Explanation

**THE OBSERVABILITY VERIFICATION CYCLE:**

```
Step 1: Define the hypothesis
  "When fault X occurs, alert Y should fire within
  Z minutes, showing metric M exceeding threshold T"

Step 2: Measure steady state
  Record baseline: request rate, error rate, latency,
  alert state = OK. Verify all metrics are present.

Step 3: Inject fault (controlled)
  Apply the minimum fault that should trigger the alert.
  Start timer: t=0.

Step 4: Observe the monitoring system
  - Does the metric change as expected?
  - Does the alert fire?
  - At what t does the alert fire?
  - Does the dashboard show the correct state?
  - Does the on-call page arrive?

Step 5: Verify
  Alert fired? → Pass
  Alert fired late? → Adjust scrape interval or
                      alert evaluation interval
  Alert did not fire? → Fix alert condition or
                        metric collection

Step 6: Rollback
  Remove the fault. Verify system returns to steady state.
  Verify alert resolves.

Step 7: Document
  "We tested: kill checkout-api pod.
   Expected: ServiceDown alert in < 2 min.
   Actual: ServiceDown alert in 7 min.
   Finding: scrape_interval=60s + for:5m too slow.
   Fix: reduce scrape_interval to 15s for critical services."
```

**COMMON OBSERVABILITY BLIND SPOTS FOUND BY CHAOS:**

```
Blind Spot 1: Missing absent-data alerts
  Fault: kill the metrics exporter
  Expected: "No data received from service X" alert
  Actual: Grafana shows "No Data". No alert fires.
  Teams assume NO DATA = healthy. It often means
  the monitoring itself is broken.
  Fix: add absent() alert rule in Prometheus:
    ALERT MetricsExporterDown
      IF absent(up{job="checkout-api"}) == 1
      FOR 2m

Blind Spot 2: Slow alert detection
  Fault: CPU spiked to 95% on payment-service
  Expected: CPUHighAlert fires in < 3 minutes
  Actual: Alert fires in 9 minutes (scrape_interval=60s,
          for:5m alert evaluation delay)
  Impact: SLA breach before engineer is paged
  Fix: reduce scrape_interval to 15s for critical
       services; reduce for: to 2m for critical alerts

Blind Spot 3: Wrong alert target
  Fault: database becomes unreachable from service A
  Expected: DatabaseConnectionFailed alert for service A
  Actual: Alert fires for service B (which is downstream
          of A and fails because A failed first)
  Finding: alert topology does not match dependency
           topology
  Fix: add service A connection pool alert; add
       alert dependency graph in Grafana

Blind Spot 4: Runbook does not match reality
  Fault: service restart causes 30-second gap in metrics
  Expected: runbook says "check metrics for service
            restart events in last 5 minutes"
  Actual: metrics gap during restart makes this
          impossible - no data exists for that window
  Fix: update runbook to check deployment events
       (kubectl rollout history) instead of metrics
```

---

### 🧪 Thought Experiment

**THE GAMEDAY EXERCISE:**

A payments team runs a quarterly GameDay with
observability focus. Participants: 2 SREs, 1 on-call
engineer, 1 service owner. Duration: 4 hours.
Scope: staging environment (identical to production
configuration).

**Experiment 1: Kill payment-api pod**
Hypothesis: `PaymentServiceDown` alert fires in < 2m.
Inject: `kubectl delete pod payment-api-xyz`
Observed: alert fires in 6 minutes.
Finding: probe_success metric has 60s scrape interval;
alert has `for: 5m`. Total = 6m minimum. SLA requires
2m page response.
Fix: reduce scrape to 15s; reduce `for:` to 1m.

**Experiment 2: Introduce 500ms latency to DB**
Tool: toxiproxy
Hypothesis: `PaymentHighLatency` alert fires in < 3m.
Inject: add 500ms toxic to DB connection.
Observed: P99 latency alert fires in 2 min 30 sec.
Finding: within SLA - but flame graph shows 80% of
the latency is from a missing DB connection pool.
Fix: add connection pool health metric as a leading
indicator to alert before P99 degrades.

**Experiment 3: Kill Prometheus scrape target**
Hypothesis: `PrometheusTargetDown` or `MetricsAbsent`
alert fires.
Inject: block metrics endpoint port with iptables.
Observed: NO ALERT FIRES. Grafana shows "No Data"
for that service. On-call has no indication.
Finding: critical observability blind spot. Service
could be completely down and monitoring would show
"No Data" (which looks the same as "healthy but
metrics loading").
Fix: Add `absent()` alert for all critical services.
Priority: P0 fix before next on-call rotation.

**Result of 4-hour GameDay:**
3 critical monitoring gaps found and documented.
2 fixed immediately (alert thresholds). 1 requires
platform change (Prometheus absent alerting) - tracked
as P0 with 2-week SLA.

---

### 🧠 Mental Model / Analogy

> Chaos engineering for observability is like testing
> a hospital's patient monitoring system. Before
> relying on it to catch cardiac events, you want
> to verify: does the monitor alarm when the sensor
> disconnects? (absent data alert). Does the alarm
> reach the nurses' station within 30 seconds? (alert
> routing). Does the nurse know which room to go to?
> (runbook quality). Does the alarm distinguish "patient
> data missing" from "patient stable"? (absent vs
> normal baseline).
>
> You would never want to discover these gaps during
> an actual cardiac event. A controlled drill (attach
> the sensor to a test mannequin, verify the alarm
> fires, verify the nurse responds correctly) finds
> these gaps safely. This is exactly what observability
> chaos engineering does for production services.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Chaos engineering for observability means deliberately
breaking things in a controlled way to check that
your monitoring and alerts work correctly. If you
kill a service, does your alert fire? If it fires,
does it fire fast enough? This practice finds gaps
in your monitoring before real incidents do.

**Level 2 - Starting point (junior):**
Begin with the simplest experiment: kill one pod in
staging and verify your ServiceDown alert fires.
Check the time from kill to page. Compare to your
SLA requirement. If the alert is slow, investigate:
what is the scrape interval? What is the `for:`
duration in the alert rule? Run this experiment for
your top-5 most critical services.

**Level 3 - GameDay planning (mid-level):**
Plan a structured GameDay: define 5-10 hypothesis
statements before the day. One hypothesis per fault
type: latency, error rate, service down, disk full,
metrics absent. Run in staging with production-
equivalent configurations. Document every finding.
Prioritise fixes by impact: anything that causes
a monitoring blind spot during a real incident is
a P0 fix.

**Level 4 - Systematic coverage (senior):**
Build a chaos experiment catalogue: every alert in
your alerting rules has a corresponding chaos experiment
that validates it. Use Litmus Chaos or Chaos Toolkit
to run experiments automatically in CI/CD (after
deploying to staging: run the ServiceDown experiment,
verify the alert fires). Track "observability coverage
score": percentage of alerts that have been validated
by a successful chaos experiment in the last 90 days.

**Level 5 - Platform strategy (staff):**
Design an organisation-wide observability chaos
programme. Quarterly mandatory GameDay for all service
teams. Automated chaos experiment registry integrated
with Grafana (experiment results shown in runbook).
Observability coverage score as a platform metric.
Correlate with incident metrics: teams with higher
observability coverage scores have shorter MTTD (mean
time to detect) and MTTR (mean time to recover) in
real incidents. Use this data to justify investment
in the chaos programme. Define a production chaos
policy: which experiments can run in production, at
what time, with what rollback plans.

---

### ⚙️ How It Works (Mechanism)

**LITMUS CHAOS - KUBERNETES FAULT INJECTION:**

```yaml
# LitmusChaos ChaosExperiment: pod-delete
# Tests: does ServiceDown alert fire when pod killed?

apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: checkout-pod-kill-experiment
  namespace: staging
spec:
  appinfo:
    appns: staging
    applabel: "app=checkout-api"
    appkind: deployment
  chaosServiceAccount: litmus-chaos-serviceaccount
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            # Kill 1 pod from the deployment
            - name: TOTAL_CHAOS_DURATION
              value: "120" # seconds to observe
            - name: CHAOS_INTERVAL
              value: "10" # seconds between kills
            - name: FORCE
              value: "false" # graceful termination
            - name: PODS_AFFECTED_PERC
              value: "25" # kill 25% of pods

  # Hypothesis probe: verify alert fires
  probes:
    - name: checkout-alert-fired
      type: promProbe
      mode: Continuous
      promProbe/inputs:
        endpoint: "http://prometheus:9090"
        query: >
          ALERTS{alertname="CheckoutServiceDown",
                 alertstate="firing"}
        comparator:
          type: int
          criteria: "=="
          value: "1"
      runProperties:
        probeTimeout: 300s
        interval: 10s
        # If alert does not fire within 300s: experiment FAILS
```

**TOXIPROXY - NETWORK FAULT INJECTION:**

```bash
# toxiproxy: inject network faults between services
# Use case: test that latency alerts fire correctly

# Start toxiproxy
docker run -d --name toxiproxy \
  -p 8474:8474 -p 5432:5432 \
  ghcr.io/shopify/toxiproxy

# Create a proxy: app → toxiproxy → real postgres
curl -X POST http://localhost:8474/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres",
    "listen": "0.0.0.0:5432",
    "upstream": "real-postgres:5432",
    "enabled": true
  }'

# Experiment: inject 500ms latency
curl -X POST http://localhost:8474/proxies/postgres/toxics \
  -H "Content-Type: application/json" \
  -d '{
    "name": "latency_test",
    "type": "latency",
    "attributes": {
      "latency": 500,  // 500ms added to every request
      "jitter": 50     // ±50ms jitter
    }
  }'

# Observe: does P99 latency alert fire within 3 minutes?
# Prometheus: query ALERTS{alertname="HighDbLatency"}

# Rollback: remove the toxic
curl -X DELETE \
  http://localhost:8474/proxies/postgres/toxics/latency_test

# Verify: P99 returns to baseline. Alert resolves.
```

**PROMETHEUS ABSENT ALERTING (fix for blind spot 3):**

```yaml
# Fix: alert when metrics are absent
# Catches: exporter down, network partition, misconfiguration

groups:
  - name: observability-coverage
    rules:
      # Alert when a critical service stops reporting metrics
      - alert: CriticalServiceMetricsAbsent
        expr: |
          absent(
            up{
              job=~"checkout-api|payment-api|order-api",
              instance=~".+"
            }
          ) == 1
        for: 2m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "Critical service metrics absent"
          description: >
            Metrics from {{ $labels.job }} have not been
            received for 2 minutes. This may indicate a
            monitoring blind spot or service crash.
            Check: kubectl get pods -n {{ $labels.namespace }}
            and verify metrics endpoint is reachable.
          runbook_url: "https://runbooks/monitoring/absent-metrics"

      # Alert when Prometheus scrape target is down
      - alert: ScrapetargetDown
        expr: up == 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Prometheus scrape target down"
          description: >
            Target {{ $labels.instance }} (job={{ $labels.job }})
            is not responding to Prometheus scrapes.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CHAOS-DRIVEN ALERT VALIDATION WORKFLOW:**

```
[Define Alert Rules]
  In Prometheus rules or Grafana alerting:
  alertname: CheckoutServiceDown
  expr: absent(up{job="checkout-api"}) or
        up{job="checkout-api"} == 0
  for: 2m
  → Alert rule deployed

[Create Corresponding Chaos Experiment]
  For each alert: create a matching experiment
  Experiment: kill checkout-api pod
  Hypothesis: "CheckoutServiceDown fires in < 3m"
  → Experiment registered in chaos catalogue

[Run Experiment (GameDay or automated CI)]
  Staging environment (matching production config)
  t=0: Kill pod
  t=30s: check - metrics still reporting (via replicas)
  t=60s: kill remaining replicas
  t=90s: check - alert evaluating
  t=120s: check - ALERTS{alertname=CheckoutServiceDown}
  t=150s: page received by on-call simulation
  → Alert fired at t=120s (< 3m threshold: PASS)

[Record Result]
  Experiment: checkout-service-down-v2
  Date: 2024-01-15
  Result: PASS
  Alert fire time: 120s
  Page received: 145s
  Notes: within SLA. Runbook link correct.

[Update Coverage Metric]
  observability_experiment_last_success_days{
    service="checkout-api",
    alert="CheckoutServiceDown"
  } = 0  # last passed 0 days ago

[Quarterly Review]
  Any alert not validated in 90 days = coverage gap
  Report: 94% of critical alerts validated this quarter
  6% gaps: assigned as action items to service teams
```

---

### 💻 Code Example

**Example 1 - BAD: Untested alert rule:**

```yaml
# BAD: alert written but never tested
# Team believes this works - but has never verified it
groups:
  - name: checkout
    rules:
      - alert: CheckoutServiceDown
        # expr references a metric that may not exist
        # in production (only exists in staging config)
        expr: checkout_service_up == 0
        for: 5m
        # Problem 1: "checkout_service_up" metric was
        #   in the original service but was renamed to
        #   "app_service_health" 6 months ago during
        #   a framework migration. Nobody updated the alert.
        # Problem 2: for: 5m means 5 minutes pass before
        #   alert fires. SLA requires page in 2 minutes.
        # Problem 3: metric was never present in production.
        #   This alert has never fired. Ever.
        # This is "zombie alerting": looks real on paper,
        # does nothing in practice.
```

**Example 2 - GOOD: Alert with corresponding chaos test:**

```yaml
# GOOD: alert rule with validated behaviour

# Alert rule (Prometheus)
groups:
  - name: checkout-slo
    rules:
      - alert: CheckoutServiceDown
        expr: |
          absent(up{job="checkout-api"}) == 1
          or up{job="checkout-api"} == 0
        for: 1m
        labels:
          severity: critical
          validated: "2024-01-15" # Last chaos test date
          experiment: "checkout-pod-kill-v3"
        annotations:
          summary: "Checkout service is down or unreachable"
          runbook_url: "https://runbooks/checkout/service-down"
          # Runbook VERIFIED to work during chaos test

# Corresponding chaos experiment result (documentation)
# chaos-catalogue/checkout-service-down.yaml:
#
# experiment: checkout-service-down-v3
# alert_tested: CheckoutServiceDown
# last_run: 2024-01-15
# result: PASS
# alert_fire_time_seconds: 73
# page_delivery_time_seconds: 91
# sla_requirement_seconds: 120
# notes: "Pass. Runbook correct. On-call acknowledged."
# next_run: 2024-04-15 (quarterly)
```

**Example 3 - Observability chaos script (bespoke):**

```bash
#!/usr/bin/env bash
# Minimal chaos script: test ServiceDown alert
# Usage: ./test_alert.sh checkout-api CheckoutServiceDown

SERVICE=$1
ALERT_NAME=$2
PROM_URL="http://prometheus:9090"
MAX_WAIT_SECONDS=120
NAMESPACE="staging"

echo "=== Chaos Experiment: $SERVICE down ==="

# Step 1: Verify steady state
echo "Step 1: Checking steady state..."
POD=$(kubectl get pods -n $NAMESPACE \
  -l app=$SERVICE \
  -o jsonpath='{.items[0].metadata.name}')
echo "Target pod: $POD"

# Verify no existing alert firing
EXISTING=$(curl -s "$PROM_URL/api/v1/query" \
  --data-urlencode \
  "query=ALERTS{alertname=\"$ALERT_NAME\",alertstate=\"firing\"}" \
  | jq -r '.data.result | length')
if [ "$EXISTING" -gt 0 ]; then
  echo "ERROR: Alert already firing before experiment."
  echo "Aborting. Fix steady state first."
  exit 1
fi
echo "Steady state: OK (no existing alert)"

# Step 2: Inject fault
echo "Step 2: Injecting fault (killing pod)..."
START_TIME=$(date +%s)
kubectl delete pod -n $NAMESPACE $POD

# Step 3: Wait for alert to fire
echo "Step 3: Waiting for alert '$ALERT_NAME' to fire..."
for i in $(seq 1 $MAX_WAIT_SECONDS); do
  sleep 1
  ALERT_STATE=$(curl -s "$PROM_URL/api/v1/query" \
    --data-urlencode \
    "query=ALERTS{alertname=\"$ALERT_NAME\",alertstate=\"firing\"}" \
    | jq -r '.data.result | length')
  if [ "$ALERT_STATE" -gt 0 ]; then
    ELAPSED=$(($(date +%s) - START_TIME))
    echo "PASS: Alert fired after ${ELAPSED}s"
    break
  fi
  if [ "$i" -eq "$MAX_WAIT_SECONDS" ]; then
    echo "FAIL: Alert did not fire within ${MAX_WAIT_SECONDS}s"
    echo "Check: alert rule expr, metric collection, for: duration"
  fi
done
```

---

### ⚖️ Comparison Table

| Tool                   | Type                       | Kubernetes native? | Observability focus          | Blast radius control                         |
| ---------------------- | -------------------------- | ------------------ | ---------------------------- | -------------------------------------------- |
| Litmus Chaos (CNCF)    | Kubernetes fault injection | Yes                | Probes verify alerts         | Good (per-experiment config)                 |
| Chaos Toolkit          | Declarative YAML           | Via plugins        | Built-in Prometheus probes   | Good (pause/rollback)                        |
| Chaos Monkey (Netflix) | Random instance kill       | No (VM-level)      | Implicit (tests resilience)  | Low (random)                                 |
| toxiproxy (Shopify)    | Network fault injection    | Via proxy          | Network latency/error alerts | Excellent (per-toxic control)                |
| Gremlin                | Commercial, full-featured  | Yes                | Dashboard integration        | Excellent (time limits, blast radius config) |
| tc netem               | Linux native               | Via pod exec       | Any network-level alert      | Manual (must revert manually)                |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Chaos engineering is for resilience, not observability"     | Chaos engineering tests both. When you inject a fault, you test resilience (does the system keep working?) AND observability (does the monitoring detect it?). Treating them as separate misses the combined value.                                                                                                                                                                     |
| "We test alerts in staging - that's enough"                  | Staging only validates if the metric exists and the alert rule is correct. It does not validate: page routing (PagerDuty config), on-call response time, runbook accuracy against real production traffic, or whether the alert is meaningful in context. Full validation requires testing the end-to-end alerting pipeline in production-equivalent conditions.                        |
| "Chaos in staging is safe, chaos in production is dangerous" | Both require blast radius control. Staging chaos can destroy your staging environment's reliability, making staging useless for other testing. Production chaos with small blast radius (1% of traffic, single pod, feature-flagged) is often safer than it sounds. Netflix and Amazon routinely run chaos in production. Start with staging but have a plan for production validation. |
| "If the alert fires, the runbook is fine"                    | The alert firing is step 1. The runbook is what the engineer does after the alert fires. Chaos experiments should also validate the runbook: run through the runbook during the experiment. Does it lead to the correct diagnosis? Does the runbook assume metrics that are absent? Does it point to the right service?                                                                 |
| "Chaos engineering requires a chaos platform tool"           | The simplest chaos experiment is `kubectl delete pod`. No tool required. Start with basic fault injection commands and manual hypothesis documentation before investing in Litmus Chaos or Gremlin.                                                                                                                                                                                     |

---

### 🚨 Failure Modes & Diagnosis

**Chaos experiment causes a real production incident**

**Symptom:**
A chaos experiment in staging uses a shared database
(staging and production share one DB cluster to reduce
cost). The experiment exhausted the connection pool.
Production services also connecting to the same DB
start failing. A real production incident is triggered
by the chaos experiment.

**Root Cause:**
Blast radius was not controlled. The experiment's
scope extended beyond the intended staging boundary
due to shared infrastructure.

**Prevention:**

```bash
# Pre-experiment checklist:
# 1. Map ALL infrastructure that staging services touch
#    (shared DBs, shared message queues, shared caches)
kubectl get configmap -n staging db-connection-config \
  -o jsonpath='{.data.DB_HOST}'
# If output matches production DB host: STOP.
# Fix: create isolated staging DB before running experiments.

# 2. Define rollback command BEFORE starting
ROLLBACK_CMD="kubectl scale deploy checkout-api \
  --replicas=3 -n staging"
# Write this down. Know how to execute it in < 30 seconds.

# 3. Set experiment time limit
# Litmus: TOTAL_CHAOS_DURATION=120 (2 minutes max)
# After 2 minutes: experiment auto-rolls back

# 4. Monitor blast radius metric during experiment
# watch -n1 kubectl get pods -n staging
# If pods in production namespace appear affected: execute ROLLBACK_CMD immediately
```

---

**Alert validated in staging, fails in production**

**Symptom:**
The chaos experiment for `PaymentServiceDown` passes
in staging: alert fires in 90 seconds. During a real
production incident, the alert fires in 9 minutes.
P0 SLA breach.

**Root Cause:**
Production Prometheus configuration differs from staging:
`scrape_interval: 15s` in staging vs `scrape_interval:
60s` in production (cost savings decision). The alert
`for: 5m` means: staging (15s scrape) can detect in
~75 seconds. Production (60s scrape) takes 5+ minutes
minimum.

**Fix:**

```yaml
# Prometheus scrape config for critical services
# in production:
scrape_configs:
  - job_name: "payment-api"
    scrape_interval: 15s # Critical service: 15s not 60s
    scrape_timeout: 10s

  # Alert rule: ensure for: matches scrape_interval
  - alert: PaymentServiceDown
    expr: up{job="payment-api"} == 0
    for: 45s # 3x scrape interval, not 5m
    # At 15s scrape: first detect at 15s + 45s = 60s max

# Lesson learned: chaos tests must mirror EXACT
# production configuration. The scrape_interval is
# a critical parameter that changes alert timing.
# Add to staging config parity checklist.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Alerting Design and Best Practices` - before
  validating alerts, understand how to design them:
  correct thresholds, for: durations, routing
- `Incident Response and On-Call Practices` - the
  full alerting → page → response pipeline that
  chaos experiments test
- `Error Budget Policies` - chaos experiments consume
  error budget. Have a policy for how much budget
  experiments can consume.

**Builds On This (learn these next):**

- `Post-Mortem and Blameless Culture` - chaos
  experiments produce findings that feed into
  structured improvement processes
- `Platform Observability Engineering` - chaos
  experiment programmes run at platform level,
  covering all services systematically

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Deliberate fault injection to verify that │
│              │ monitoring, alerts, and runbooks work     │
│              │ correctly before real incidents do        │
├──────────────┼───────────────────────────────────────────┤
│ HYPOTHESIS   │ "When X fails, alert Y fires in < Z min"  │
│              │ Must be written BEFORE injection          │
├──────────────┼───────────────────────────────────────────┤
│ FAULT TYPES  │ Pod kill, latency injection, packet loss  │
│              │ Connection pool exhaustion, disk fill     │
│              │ Metrics exporter kill (blind spot test)   │
├──────────────┼───────────────────────────────────────────┤
│ KEY TOOLS    │ Litmus Chaos: Kubernetes-native, CRD-based│
│              │ Chaos Toolkit: YAML experiments, rollback │
│              │ toxiproxy: network fault injection        │
│              │ kubectl delete pod: simplest starting pt  │
├──────────────┼───────────────────────────────────────────┤
│ BLIND SPOTS  │ Missing absent() alerts (no data = blind) │
│ FOUND        │ Slow alert detection (scrape interval)    │
│              │ Wrong service targeted by alert           │
│              │ Runbook assumes absent metrics            │
├──────────────┼───────────────────────────────────────────┤
│ GAMEDAY      │ Scheduled experiment day. 5-10 hypotheses │
│              │ Staging env. Document all findings.       │
│              │ Fix P0 gaps before next on-call rotation  │
├──────────────┼───────────────────────────────────────────┤
│ SAFETY RULES │ Blast radius: minimum fault, short duration│
│              │ Rollback command ready before injection   │
│              │ Production-isolated staging infrastructure │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Post-Mortem and Blameless Culture         │
│              │ Platform Observability Engineering        │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Trust but verify" for monitoring becomes "never trust

- always verify." An alert rule that has not been
  exercised is a hypothesis, not a fact. The same
  principle applies across engineering: automated tests
  for code (unit tests verify code behaviour), load
  tests for infrastructure (verify behaviour under
  stress), penetration tests for security (verify
  controls under attack). Observability chaos engineering
  applies this "experimental validation" discipline to
  the monitoring stack itself. In every engineering
  domain, the cost of discovering a gap in production
  (during a real incident, with real customer impact)
  is orders of magnitude higher than the cost of
  discovering it in a controlled experiment. The practice
  of systematic experimental validation of safety
  mechanisms - whether smoke detectors, circuit breakers,
  or alert rules - is a universal engineering discipline.

---

### 💡 The Surprising Truth

The most counterintuitive finding from observability
chaos engineering programmes: the most common alerting
failure is not "the alert threshold is wrong" or
"the metric is noisy." It is "the metric is missing
entirely in production." Teams discover that 20-40%
of their alert rules target metrics that were:
(1) renamed during a framework migration and nobody
updated the alert, (2) only collected in staging
but never in production, (3) collected but with a
different label name than the alert expects (e.g.,
`service_name` vs `service`), or (4) only present
when the service is healthy (ironic: the metric
that should fire when the service crashes also
disappears when the service crashes, so the alert
never fires). Category (4) is particularly insidious:
a metric like `checkout_service_is_up = 1` that is
only emitted by a healthy service will produce
"No Data" when the service crashes - and "No Data"
does not trigger an `== 0` alert. This is why
`absent()` based alerts are superior to `metric == 0`
alerts for service health, and why chaos engineering
tests both approaches.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Describe the difference between
   chaos engineering for resilience and chaos engineering
   for observability. Why must observability itself
   be tested?
2. **[IDENTIFY]** List the four most common observability
   blind spots that chaos engineering reveals. For
   each, explain why it occurs and how to fix it.
3. **[DESIGN]** Write a complete chaos experiment
   including: hypothesis statement, fault injection
   command, observability verification query (PromQL),
   rollback command, pass/fail criteria, and
   documentation format.
4. **[SAFEGUARD]** Explain the blast radius controls
   required before running a chaos experiment in
   a staging environment that shares infrastructure
   with production.
5. **[PROGRAM]** Design a quarterly GameDay programme
   for a team of 5 services. Include: how many
   experiments, which fault types, how findings are
   prioritised and tracked, and what metrics
   demonstrate programme value over time.

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has 50 Prometheus alert rules.
You want to validate them with chaos experiments.
You have 1 day per quarter for chaos work. How do
you prioritise which alerts to test first? What
criteria determine priority? How do you handle alerts
that cannot be safely tested?
_Hint: Priority criteria: (1) P0/P1 incidents - any
alert that, if incorrect, causes customer-impacting
delay in detection = top priority. Test these every
quarter. (2) Alerts that have never fired in production
(could be correct but never tested, or zombie alerts
targeting missing metrics). Check: `ALERTS_FOR_STATE`
metric shows alerts that are pending or firing. Zero
firing history = suspect. (3) Alerts for services
with highest revenue or customer exposure. (4) Alerts
that were recently changed (code review may not catch
semantic errors in PromQL). For alerts that cannot
be safely tested (production-only metrics, no staging
equivalent): test in production with minimal blast
radius (1 pod, 30 seconds, during low-traffic window)
with pre-approved change management._

**Q2.** During a chaos experiment, you discover that
the `PaymentServiceDown` alert fires correctly in
staging (72 seconds), but the alert never reached
the on-call engineer in PagerDuty during the test.
The alert fired in Prometheus. Where are the possible
failure points between "alert fires in Prometheus"
and "on-call engineer receives page"? How do you
test each failure point?
_Hint: The pipeline: Prometheus fires alert → Alertmanager
receives alert → Alertmanager routes to correct route →
Alertmanager sends to PagerDuty (or similar) → PagerDuty
creates incident → PagerDuty pages on-call schedule →
On-call engineer receives notification. Failure points:
(1) Alertmanager config: correct routing rule matches
alert labels (severity=critical, team=payments)?
Test: `amtool check-config alertmanager.yaml`.
(2) Alertmanager → PagerDuty: correct API key? Network
connectivity? Test: Alertmanager test fire endpoint.
(3) PagerDuty schedule: is someone on-call right now?
Test: view schedule in PagerDuty UI during experiment.
(4) Escalation: if no acknowledgement in 5 min, escalates
to manager? Test: ignore the page during experiment and
verify escalation fires. Most teams only test step 1
(Prometheus → Alertmanager). The full pipeline from
alert to human requires end-to-end testing._

**Q3 (TYPE G):** Build the business case for a quarterly
observability chaos programme for a 50-engineer
engineering organization with 30 services. Include:
(a) the gap being addressed (what problem exists
without this programme), (b) the time investment
required per quarter, (c) the measurable outcomes
that justify the investment, (d) the first-quarter
execution plan, (e) the metrics that demonstrate
ROI to the VP of Engineering after 4 quarters.
_Hint: (a) Gap: untested alert rules. Study: ~30% of
alert rules target missing or incorrect metrics (common
finding). Example: a P0 incident goes undetected for
12 minutes because the ServiceDown alert was targeting
a renamed metric. Customer SLA breach. Revenue impact.
(b) Time: 4 hours per service team per quarter (GameDay
day). For 5 service teams = 20 engineer-hours/quarter.
Plus 2 hours platform SRE coordination. Total: ~22
engineer-hours/quarter. (c) Measurable outcomes: MTTD
(mean time to detect) decreasing quarter over quarter;
"alert fire time vs SLA requirement" metric improving;
percentage of alerts validated (coverage score). (d)
Q1 plan: week 1 educate teams on hypothesis format and
tool (Litmus/kubectl delete pod). Week 2-3 each team
runs 3-5 experiments for their critical alerts. Week 4
review findings, fix P0 gaps, establish catalogue. (e)
After 4 quarters: MTTD reduced from Xmin to Ymin (measured
from incident post-mortems), number of "blind spot
discoveries in production incidents" decreasing,
alert coverage score > 90%, specific incidents that
GameDay prevented (before the quarter's real incidents
occur, the blind spots were fixed in GameDay). Present
one "incident that almost happened" story: "In Q2
GameDay, we discovered X was not alerting on Y. In
Q3, Y actually happened in production - but the alert
fired correctly in 68 seconds because we fixed it
in GameDay. Before the programme: this would have
been a 15-minute detection gap."_

---

### 🎯 Interview Deep-Dive

**Q1: "What is chaos engineering for observability
and how does it differ from standard resilience testing?"**
_Why they ask:_ Tests understanding of observability
as a first-class discipline, not just an afterthought.
_Strong answer includes:_

- Resilience testing asks: "Does the system SURVIVE
  this fault?" Observability chaos asks: "Does the
  monitoring DETECT this fault correctly?"
- A system can be resilient (auto-heals in 30 seconds)
  AND have a monitoring gap (takes 8 minutes to alert).
  The auto-healing does not prevent the MTTD SLA breach.
- The hypothesis format: "When X fails, alert Y fires
  in < Z minutes, runbook R leads to correct diagnosis."
- Key finding type: "zombie alerts" - alerts that
  reference metrics that no longer exist in production.
  Only discovered through deliberate testing.

**Q2: "What is the most critical observability blind
spot you have discovered or know about? How would
you test for it systematically?"**
_Why they ask:_ Tests practical experience with
monitoring gaps, not just theoretical knowledge.
_Strong answer includes:_

- "Absent data = healthy" assumption. Grafana shows
  "No Data" - teams assume the service is fine.
  Actually the metrics exporter crashed.
- Test: `kubectl delete pod <metrics-exporter>` or
  block the metrics scrape endpoint with iptables.
  Does an alert fire? If not: add `absent()` rule
  for all critical services.
- Systematic approach: for every critical service,
  add to the chaos catalogue: "kill the metrics exporter,
  verify MetricsAbsent alert fires within 2 minutes."
  Validate quarterly.

**Q3: "Describe how you would run a chaos engineering
GameDay for your team to validate observability coverage."**
_Why they ask:_ Tests practical execution capability,
not just theoretical knowledge.
_Strong answer includes:_

- Preparation: write 5-10 hypothesis statements.
  Define blast radius limits. Write rollback commands.
  Verify staging is production-equivalent in config.
  Pick a low-traffic window.
- Execution: run each experiment one at a time.
  Start with pod kill (simplest). Observe the full
  pipeline: metric change → alert state → page received.
  Record: did it fire? How long? Any mismatches?
- Findings: categorise by severity. P0 = monitoring
  blind spot (alert does not fire). P1 = SLA violation
  (fires too slowly). P2 = cosmetic (wrong runbook link).
- Follow-up: P0 and P1 fixes before next on-call rotation.
  Schedule next GameDay for 3 months.
- Success metric: observability coverage score
  (% of critical alerts validated in last 90 days).

# OBS-030 - Chaos Engineering for Observability

> Entry stub. Generate full content using Master Prompt v3.0.
