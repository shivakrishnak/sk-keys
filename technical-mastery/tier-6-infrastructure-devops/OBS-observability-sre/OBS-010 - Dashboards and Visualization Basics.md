---
id: OBS-010
title: Dashboards and Visualization Basics
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-006, OBS-007, OBS-009
used_by: OBS-014, OBS-018, OBS-019
related: OBS-006, OBS-009, OBS-011
tags:
  - observability
  - metrics
  - foundational
  - first-principles
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/obs/dashboards-and-visualization-basics/
---

⚡ TL;DR - Effective dashboards show the current health
of a system at a glance using the right chart type for
each signal, following a top-down hierarchy from service
health to component details to infrastructure metrics.

| #010            | Category: Observability & SRE                              | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Metrics Types, Logging Fundamentals, Alerting Fundamentals |                 |
| **Used by:**    | SLO Dashboard Design, Incident Response Dashboards         |                 |
| **Related:**    | Metrics Types, Alerting Fundamentals, SLI/SLO              |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An incident is in progress. The on-call engineer runs:

```bash
kubectl top pods -n production
kubectl logs payment-service-7d8f9 --tail=100
curl payment-service:8080/metrics | grep error
curl checkout-service:8080/metrics | grep latency
```

Four commands, four terminal windows, raw text output.
The engineer is mentally aggregating: the checkout error
rate looks high but it might be normal for this time
of day. The payment metrics show some errors but the
format is different from the checkout metrics. Latency
looks elevated but the engineer does not know what
"elevated" means without historical context.

**THE BREAKING POINT:**
Without dashboards, incident response requires manual
correlation across multiple data sources with no
shared time axis, no historical context, and no visual
pattern recognition. The engineer cannot answer "is this
worse than usual?" because "usual" requires either memory
or separate historical queries.

**THE INVENTION MOMENT:**
Graphite (2008) was the first widely-used time series
graphing system. Grafana (2014) made the open-source
dashboard ecosystem accessible. The key insight: a time
series graph with a visible baseline enables instant
pattern recognition that raw numbers cannot provide.
A human eye can spot a spike in a graph in 0.1 seconds.
Detecting the same spike in raw metric output requires
reading and interpreting numbers.

---

### 📘 Textbook Definition

**A dashboard** is a collection of visualisations
(panels) that display the current and historical state
of a system, organised to support a specific workflow
(incident response, capacity planning, SLO review).

**Key concepts:**

- **Panel:** a single visualisation unit (graph, stat,
  table, gauge, heatmap)
- **Time range:** the window displayed (last 1 hour,
  last 7 days)
- **Refresh rate:** how often the dashboard updates
  (30 seconds for incident response, 5 minutes for
  daily review)
- **Variables:** template parameters that allow
  selecting service, environment, or instance to
  filter the dashboard without duplication
- **Annotations:** vertical markers on graphs showing
  deployments, incidents, or configuration changes

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A dashboard converts raw time series data into visual
patterns that a human can interpret in seconds rather
than minutes.

> Think of an aircraft cockpit. The pilots do not read
> raw sensor data from 200 instruments sequentially.
> The instruments are arranged by priority: altitude
> and speed are the largest and most prominent dials.
> Secondary instruments (engine temperature) are smaller.
> Warning lights summarise complex conditions. The layout
> is designed for rapid situation assessment, not for
> comprehensive data access.

**One insight:**
The most important property of a dashboard is what it
does NOT show. A dashboard that shows everything is as
useless as no dashboard. Effective dashboard design is
a series of decisions about what to exclude. The rule:
each panel must answer a specific question that is
relevant to the dashboard's workflow.

---

### 🔩 First Principles Explanation

**THE THREE DASHBOARD TYPES:**

1. **Service health dashboards** (operational, real-time):
   - Who: on-call engineers during incidents
   - Shows: top-line SLO metrics, error rate, latency P99,
     request volume
   - Time range: last 1-2 hours, auto-refresh 30s
   - Design: large stat panels for current values,
     time series graphs with SLO thresholds marked

2. **SLO / error budget dashboards** (weekly review):
   - Who: SRE team, service owners
   - Shows: SLI vs SLO targets, error budget remaining,
     budget consumption rate, deployment annotations
   - Time range: last 30 days
   - Design: budget burn gauge, SLI trend line,
     deployment event markers

3. **Infrastructure dashboards** (capacity planning):
   - Who: SRE team, platform engineers
   - Shows: CPU, memory, disk, network per node/pod
   - Time range: last 7-30 days
   - Design: heatmaps for fleet-wide distribution,
     trend lines for capacity forecasting

**CHART TYPE SELECTION RULES:**

- **Time series graph:** any metric that changes over time
  (the default choice for metrics)
- **Stat panel:** single current value with threshold
  colour (green/amber/red) - for SLO status at a glance
- **Gauge / bar gauge:** current value within a range
  (error budget remaining as %)
- **Table:** multi-dimensional comparison (multiple
  services, multiple metrics in one view)
- **Heatmap:** distribution over time (latency histogram
  buckets - see how P50/P95/P99 evolve)
- **Logs panel:** recent log entries filtered by query

**TRADE-OFFS:**

**Gain:** Rapid visual pattern recognition. Historical
context for current values. Shared team reference during
incidents.

**Cost:** Dashboards require maintenance. Charts become
stale if metric names change. Over-engineered dashboards
with 40 panels become as unreadable as raw data.

---

### 🧪 Thought Experiment

**SETUP:**
Two SRE teams respond to the same checkout service
degradation incident.

**TEAM A - NO DASHBOARD:**
Engineer runs kubectl and curl commands. After 8 minutes
they have established: error rate is 3%, latency P99 is
1.8s, payment service has recent deployment. But they
cannot tell if the deployment is correlated with the
latency spike because they would need to query the
deployment timestamp from a separate system and compare
it to the metric timestamps manually.

**TEAM B - GOOD DASHBOARD:**
Engineer opens the checkout service dashboard. At a
glance (5 seconds):

- Top-left stat panel: SLO status = AMBER (error budget
  burning at 12x)
- Centre time series: latency P99 jumps from 200ms to
  1.8s at exactly 14:22
- Annotation on the graph: "payment-service v2.3.1
  deployed at 14:21"
  Correlation is visual and instant. Root cause hypothesis
  (deployment caused latency spike) takes 5 seconds, not
  8 minutes.

**THE INSIGHT:**
Dashboards compress the cognitive work of multi-source
data correlation into a single visual representation.
The annotation feature (marking deployments on graphs)
is one of the highest-value dashboard features for
incident response: it converts a temporal correlation
question ("is this spike related to that deployment?")
into a visual inspection.

---

### 🧠 Mental Model / Analogy

> Think of a patient's vital signs monitor in an ICU.
> The monitor does not show raw sensor data. It shows
> the data visualised as continuous waveforms (ECG,
> SpO2), large numerical readouts (heart rate, blood
> pressure), and threshold indicators (alarms at 95%
> SpO2). The layout is designed for a nurse who needs
> to assess 8 patients in 30 seconds. Abnormalities
> are visually obvious.

The dashboard design principles from ICU monitors:

- Most critical metrics are largest and most prominent
- Current value and trend are shown simultaneously
- Thresholds are marked so deviation is visually instant
- The layout is standard across all patients so the
  nurse does not need to re-learn each one

**Where this breaks down:** ICU monitors show a few
vital signs with well-understood normal ranges (heart
rate 60-100). Service dashboards show metrics whose
normal ranges vary by service, time of day, and traffic
pattern. The threshold management in service dashboards
is more dynamic and context-dependent.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
A dashboard is a web page that shows charts about how
your system is performing. Instead of running commands
to check if things are working, you open a page and
look at graphs.

**Level 2 - How to use it (junior developer):**
Use Grafana with Prometheus as a data source. Create a
time series panel with PromQL queries. Add a stat panel
showing current error rate with colour thresholds
(green < 0.1%, amber 0.1-0.5%, red > 0.5%). Add the
dashboard as the first link in your runbook.

**Level 3 - How it works (mid-level):**
Grafana queries the data source (Prometheus, Loki,
Jaeger) on each dashboard load and refresh. Panels
contain PromQL or LogQL expressions. Variables are
template parameters rendered as dropdowns that modify
the query (e.g., `{service="$service"}` where `$service`
is selected from a dropdown). Annotations query a
Prometheus metric or a Grafana annotation API to
display event markers on time series graphs.

**Level 4 - Why it matters (senior/staff):**
The key dashboard design principle is hierarchy: USE
method (Utilisation, Saturation, Errors) for
infrastructure, RED method (Rate, Errors, Duration) for
services. Service dashboards should be structured:
(1) top row: SLO status and error budget (overall
health), (2) second row: RED metrics (rate, errors,
duration), (3) third row: dependency health (database,
external APIs), (4) bottom rows: infrastructure
(CPU, memory, pods). This hierarchy allows rapid
triage: check the top row first. If SLO is green,
stop. If amber, check the RED metrics to understand
the nature of the degradation. If red, check
dependencies to understand if it is a downstream issue.

**Level 5 - Mastery (distinguished engineer):**
Dashboard-as-code is the production maturity level.
All dashboards are defined as JSON (Grafana's native
format) or as Grafonnet/Jsonnet code, stored in git,
and deployed via CI/CD. This prevents dashboard drift
(manual changes that are not tracked), enables review
and approval of dashboard changes, and allows dashboard
templating across services. At large scale (50+ services
with identical dashboard structures), Jsonnet templating
generates service-specific dashboards from a shared
template, ensuring consistency. Staff engineers also
recognise that dashboards represent institutional
knowledge: an undocumented dashboard is a liability
(no one knows what the panels mean). Good dashboards
have panel titles that are questions ("Is the error
rate above SLO?") and descriptions that explain the
metric and the expected range.

---

### ⚙️ How It Works (Mechanism)

**GRAFANA ARCHITECTURE:**

```
[Browser]
  Opens dashboard at time range: now-1h to now
        ↓
[Grafana server]
  Reads dashboard JSON (panel configs, queries)
  For each panel:
    Sends query to configured data source
        ↓
[Prometheus data source]
  Receives PromQL query + time range
  Evaluates against time series database
  Returns: [{metric labels, [timestamp, value]...}]
        ↓
[Grafana rendering]
  Renders time series as SVG/canvas chart
  Applies thresholds (colour bands)
  Applies annotations (deployment markers)
        ↓
[Browser displays rendered panels]
  Auto-refreshes every 30s (incident mode)
```

**VARIABLE INTERPOLATION:**

```
Dashboard variable: service = "checkout"

Panel query:
  sum(rate(${service}_requests_total{
    env="${env}"}[5m]))
  ← Grafana replaces ${service} with "checkout"
  ← Grafana replaces ${env} with selected value

Result: dropdown in top of dashboard allows changing
  service without editing any query.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**INCIDENT RESPONSE DASHBOARD WORKFLOW:**

```
[Alert fires: CheckoutSLOFastBurn]
  Alert links to: https://grafana/d/checkout
        ↓
[Engineer opens checkout dashboard]
  Current time range: auto-set to last 1 hour
        ↓
[Top row: health summary - 5 seconds to read]
  SLO Status: RED (error rate 3%, SLO is 99.9%)
  Error budget: 72% consumed this month
  Current burn rate: 30x
        ↓
[SRE team ← YOU ARE HERE]
[Second row: RED metrics - 30 seconds to read]
  Rate: 1,200 req/s (normal)
  Errors: 3% error rate (spike at 14:21)
  Duration: P99 = 1.8s (spike at 14:21)
  ← Annotation marker: "payment v2.3.1 deployed 14:21"
        ↓
[Third row: dependencies - 2 minutes to investigate]
  Payment service error rate: 15%
  Payment service P99: 4.2s (elevated)
  ← Root cause hypothesis: payment service deployment
        ↓
[Action: roll back payment-service v2.3.1]
  Deployment annotation marker appears on graph
  Error rate returns to 0.1% - incident resolved
```

**WHAT CHANGES AT SCALE:**
At 50+ services, a service catalogue dashboard becomes
critical: one row per service showing SLO status as
a coloured stat panel. A fleet-wide view (red = SLO
breach, amber = burn rate elevated, green = healthy)
allows scanning 50 services in 5 seconds. Drill-down
dashboards for each service are linked from the
catalogue row.

---

### 💻 Code Example

**Example 1 - BAD: Dashboard with wrong chart types:**

```json
{
  "panels": [
    {
      "title": "Request Count",
      "type": "stat",
      "targets": [
        {
          "expr": "checkout_requests_total"
        }
      ]
    }
  ]
}
// BAD: showing a raw counter (ever-increasing total)
// as a stat panel. The number means nothing without
// context. Should be request RATE (per second).
// Should be a time series graph, not a stat.
// Current value of a counter is not actionable.
```

**Example 2 - GOOD: Correct panel types per metric:**

```json
{
  "panels": [
    {
      "title": "SLO Status",
      "description": "Is error rate within SLO budget?",
      "type": "stat",
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              { "color": "green", "value": null },
              { "color": "yellow", "value": 0.001 },
              { "color": "red", "value": 0.005 }
            ]
          }
        }
      },
      "targets": [
        {
          "expr": "sum(rate(
              checkout_requests_total{status!~'2..'}[5m])) / sum(rate(
                  checkout_requests_total[5m]))",
          "legendFormat": "Error Rate"
        }
      ]
    },
    {
      "title": "Request Rate (req/s)",
      "description": "Requests per second. Expected: 1000-1500 during business hours.",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum(rate(checkout_requests_total[5m]))",
          "legendFormat": "requests/s"
        }
      ]
    },
    {
      "title": "Latency P99 vs SLO (500ms)",
      "description": "P99 should stay below SLO threshold (red line)
          .",
      "type": "timeseries",
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              { "color": "green", "value": null },
              { "color": "red", "value": 0.5 }
            ]
          }
        }
      },
      "targets": [
        {
          "expr": "histogram_quantile(0.99,
              sum(rate(checkout_duration_seconds_bucket[5m])) by (
                  le))",
          "legendFormat": "P99 latency"
        }
      ]
    }
  ]
}
```

**Example 3 - Dashboard variable for service selection:**

```json
{
  "templating": {
    "list": [
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(up, job)",
        "label": "Service",
        "current": { "value": "checkout" }
      },
      {
        "name": "env",
        "type": "custom",
        "options": [{ "value": "production" }, { "value": "staging" }]
      }
    ]
  }
}
// Usage in panel query:
// sum(rate(${service}_requests_total{env="${env}"}[5m]))
```

---

### ⚖️ Comparison Table

| Chart type      | Best for                                   | Bad for              |
| --------------- | ------------------------------------------ | -------------------- |
| **Time series** | Any metric over time                       | Single current value |
| **Stat panel**  | Current value with threshold               | Trends and patterns  |
| **Gauge**       | Value within a bounded range (budget %)    | Time series          |
| **Bar gauge**   | Top-N comparison                           | Trend analysis       |
| **Table**       | Multi-service, multi-metric comparison     | Single metric        |
| **Heatmap**     | Histogram distribution over time (latency) | Simple rate metrics  |
| **Logs panel**  | Recent log entries with level filter       | Aggregated metrics   |

**Dashboard tooling comparison:**

| Tool                      | Strengths                                            | Weaknesses                       |
| ------------------------- | ---------------------------------------------------- | -------------------------------- |
| **Grafana**               | Open source, multi-datasource, extensive panel types | Complex to configure at scale    |
| **Datadog**               | Unified platform, automatic service maps             | Expensive, vendor lock-in        |
| **CloudWatch Dashboards** | Zero setup on AWS                                    | AWS-only, limited visualisations |
| **Kibana**                | Best for log-heavy dashboards (ELK)                  | Less suited for metrics          |
| **Honeycomb**             | Best query experience for traces                     | Not a general-purpose dashboard  |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "More panels = more visibility"                  | A dashboard with 40 panels is unreadable during an incident. 8-12 panels covering the most important questions is the target. Discard panels that are never consulted.                                                          |
| "Average latency is sufficient"                  | Average latency hides outliers. A P99 of 3 seconds can coexist with an average of 200ms. Always show P95 and P99. Use heatmaps to see the full latency distribution.                                                            |
| "Dashboards are for post-incident review only"   | The most valuable use of dashboards is real-time incident response. The dashboard is the first thing an on-call engineer should open, not the last.                                                                             |
| "Raw counter values on stat panels are useful"   | A checkout_requests_total stat showing 1,234,567 tells you nothing. Show the rate (requests/second). Show rate vs a known baseline. The raw counter is noise.                                                                   |
| "Time range doesn't matter"                      | The time range shapes the visual story. A 10-second spike invisible at "last 7 days" scale is obvious at "last 1 hour" scale. Match the time range to the question: incidents use 1-2 hours; capacity planning uses 30-90 days. |
| "Dashboards in the UI are fine (no code needed)" | Dashboards created manually in the UI are lost on Grafana reinstallation, cannot be code-reviewed, and diverge across environments. All production dashboards should be stored in git as JSON or Jsonnet.                       |

---

### 🚨 Failure Modes & Diagnosis

**Dashboard shows misleading "healthy" signal during incident**

**Symptom:**
The SLO status panel shows "GREEN" while users are
experiencing 10% error rate. The on-call engineer
trusts the dashboard and escalates without investigating.
Users wait 20 minutes for the engineer to realise the
dashboard is wrong.

**Root Cause:**
The SLO status panel query uses `avg(rate(errors[5m]))`
instead of `sum(rate(errors[5m])) / sum(rate(requests[5m]))`.
The `avg()` averages across service instances. One
instance is healthy; three are in error state. The
average masks the failure.

**Diagnostic Command:**

```promql
# Check per-instance error rates to reveal masking
sum by (instance) (
  rate(checkout_requests_total{status!~"2.."}[5m])
) / sum by (instance) (
  rate(checkout_requests_total[5m])
)
```

**Fix:**
Replace `avg(rate(...))` with `sum(rate(...)) / sum(rate(...))`.
Always aggregate error rate by computing the total error
count divided by the total request count, not by averaging
per-instance rates.

**Prevention:**
Dashboard queries should be reviewed using the same
rigour as application code. Add a query correctness
checklist: (1) no avg() on counters, (2) error rate
= error_sum / total (not avg per instance), (3) latency
uses histogram_quantile, not avg.

---

**Deployment annotations missing from incident timeline**

**Symptom:**
A post-mortem review finds a deployment that caused
an incident, but the Grafana graph does not show the
deployment as an annotation. Engineers cannot use the
graph to confirm the correlation. The timeline
reconstruction is manual and time-consuming.

**Root Cause:**
The CI/CD pipeline does not send deployment events to
Grafana's annotation API. Annotations must be explicitly
sent by the deployment tool; they do not appear
automatically from deployment records.

**Diagnostic Command:**

```bash
# Verify annotations API is receiving events
curl -s "http://grafana:3000/api/annotations?
  type=annotation&from=$(date -d '7 days ago' +%s000)
  &to=$(date +%s000)" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  | jq '[.[] | {id, text, time}]'
# Empty result = no annotations being sent
```

**Fix:**
Add a deployment annotation step to the CI/CD pipeline:

```bash
# Send deployment annotation to Grafana
curl -X POST http://grafana:3000/api/annotations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -d "{
    \"text\": \"$SERVICE v$VERSION deployed to $ENV\",
    \"tags\": [\"deployment\",\"$SERVICE\"],
    \"time\": $(date +%s000)
  }"
```

**Prevention:**
Include the annotation step in all deployment pipeline
templates. Test that annotations appear in staging
dashboards after every staging deployment.

---

**Dashboard query timeout during high-load incident**

**Symptom:**
During a high-traffic incident (when you most need
the dashboard), Grafana panels show "query timed out"
errors instead of data. The dashboard that is supposed
to help with incident response is unavailable exactly
when needed.

**Root Cause:**
The dashboard queries use expensive PromQL expressions
that scan the full metric history. During high load,
Prometheus is under memory and CPU pressure. Complex
queries timeout because Prometheus cannot process
them within the 30-second query timeout.

**Diagnostic Command:**

```bash
# Test query duration outside of incident
time curl -sg "localhost:9090/api/v1/query_range?\
query=sum(rate(checkout_requests_total[5m]))&
start=$(date -d '1 hour ago' +%s)&
end=$(date +%s)&step=15" > /dev/null
```

**Fix:**
Simplify dashboard queries. Use recording rules to
pre-compute expensive aggregations:

```yaml
# Prometheus recording rule:
# pre-compute expensive aggregation every 15s
groups:
  - name: checkout.rules
    rules:
      - record: job:checkout_error_rate:rate5m
        expr: |
          sum(rate(checkout_requests_total{
            status!~"2.."}[5m]))
          / sum(rate(checkout_requests_total[5m]))
```

**Prevention:**
Load test all dashboard queries under Prometheus stress
conditions. Use recording rules for any query that
takes > 2 seconds in normal conditions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Metrics Types (Counter, Gauge, Histogram)` - PromQL
  query correctness depends on knowing the metric type;
  using wrong operations produces misleading charts
- `Alerting Fundamentals` - dashboards are the visual
  complement to alerts; the same PromQL expressions
  used in alerts should appear on dashboards for context

**Builds On This (learn these next):**

- `Grafana Fundamentals` - the primary open-source
  tool for building observability dashboards
- `SLO Dashboard Patterns` - specific dashboard designs
  for SLO measurement and error budget tracking
- `Dashboard as Code (Grafonnet)` - Jsonnet-based
  approach to managing dashboards in version control

**Alternatives / Comparisons:**

- `Datadog Dashboards` - SaaS alternative with automatic
  service topology maps and APM integration
- `CloudWatch Dashboards` - AWS-native dashboard tool
  for AWS service metrics

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ HIERARCHY    │ Row 1: SLO status + error budget         │
│              │ Row 2: RED (rate, errors, duration)      │
│              │ Row 3: Dependencies                      │
│              │ Row 4+: Infrastructure (CPU/mem/disk)    │
├──────────────┼──────────────────────────────────────────┤
│ CHART RULES  │ Time series: metrics over time (default) │
│              │ Stat: current value with colour threshold│
│              │ Heatmap: latency histogram distribution  │
│              │ Table: multi-service comparison          │
├──────────────┼──────────────────────────────────────────┤
│ QUERY RULES  │ Error rate: sum(errors) / sum(total)     │
│              │ Latency: histogram_quantile(0.99, ...)   │
│              │ NEVER: avg() on a counter                │
├──────────────┼──────────────────────────────────────────┤
│ ANNOTATIONS  │ Mark every deployment + config change    │
│              │ Use CI/CD annotation API call            │
├──────────────┼──────────────────────────────────────────┤
│ TIME RANGES  │ Incident response: last 1-2 hours        │
│              │ SLO review: last 30 days                 │
│              │ Capacity planning: last 90 days          │
├──────────────┼──────────────────────────────────────────┤
│ VARIABLES    │ service, env dropdowns → one dashboard   │
│              │ works for all services + environments    │
├──────────────┼──────────────────────────────────────────┤
│ PANEL COUNT  │ Aim for 8-12 panels per dashboard.       │
│              │ 40+ panels = unreadable = useless        │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Raw counter totals on stat panels.       │
│              │ Averages on counters. No baseline context│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Grafana → SLO Dashboards → Dashboard Code│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Organize dashboards top-down: SLO status (top row) →
   RED metrics → dependencies → infrastructure. Check
   the top row first. If green, stop. If not, drill down.
2. Use the correct chart type: time series for trends,
   stat panel for current SLO status, heatmap for
   latency distribution. Never show raw counter totals.
3. Mark every deployment with an annotation on the time
   axis. This turns incident timeline reconstruction
   from a 20-minute manual exercise into a 5-second
   visual correlation.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Design information displays for the highest-pressure
use case (incident response), not the average use case
(routine review). The layout, chart types, and panel
ordering should be optimised for a stressed engineer
who needs to assess system health in 10 seconds.
This principle applies to: status pages (customers
assess impact in seconds), deployment pipelines (did
this deploy succeed? - one stat, not 40 logs), and
financial trading terminals (prices front-and-centre,
not buried in tables).

**Where else this pattern appears:**

- **Information radiators in agile** - Kanban boards and
  sprint velocity charts are physical dashboards designed
  for rapid team situation assessment. The principle is
  the same: visible, at-a-glance, action-oriented.
- **Network operations centres (NOC)** - large wall
  displays showing network topology with colour-coded
  health indicators. The same RED/GREEN/AMBER design
  pattern applied to network nodes instead of services.
- **Medical clinical dashboards** - patient overview
  dashboards in hospitals prioritise acute observations
  (abnormal vitals) over routine data, same hierarchy
  principle as SLO status first, infrastructure last.

---

### 💡 The Surprising Truth

The most counterintuitive dashboard insight: the best
dashboards are the ones that engineers use to prove
everything is working, not just to detect failures.
A dashboard that is only consulted during incidents is
a tool that gets used 0.01% of the time and is never
optimised. A dashboard that the team reviews in every
morning standup, that shows up on the TV screen in the
office, that everyone looks at before each deployment -
this dashboard gets refined, corrected, and improved
continuously. It becomes a shared mental model of how
the system behaves. The 10 minutes per day spent
reviewing a healthy system dashboard saves 2 hours per
incident because the team has built intuition about
normal patterns that makes anomalies obvious.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Given a Grafana dashboard where the
   SLO status panel shows "healthy" but users are
   reporting errors, identify three possible reasons
   why the panel is showing incorrect data and write
   the corrected PromQL query for each.
2. **[DEBUG]** During an incident, a Grafana dashboard
   shows "query timed out" for all panels. Diagnose the
   likely cause and describe the immediate workaround
   (recording rules or simplified queries) and the long-
   term prevention strategy.
3. **[DECIDE]** Given the requirement to build a single
   dashboard for a checkout service that supports both
   incident response (real-time, last 1 hour) and SLO
   review (monthly error budget), decide whether to
   build one dashboard or two, justify the decision,
   and describe the panel layout for each.
4. **[BUILD]** Create a Grafana dashboard for the checkout
   service with: (1) SLO status stat panel (error rate
   threshold), (2) request rate time series, (3) error
   rate time series with SLO threshold line, (4) P99
   latency heatmap, (5) deployment annotations. Use
   dashboard variables for service and environment.
5. **[EXTEND]** Design a service catalogue dashboard
   that shows SLO health for 50 services in a single
   view. Each service shows: SLO status (colour), current
   error rate, error budget remaining. Describe the
   Grafana data structure (table panel or stat panel
   grid), the PromQL query that produces one row per
   service, and how to maintain this at scale using
   dashboard-as-code.

---

### 🧠 Think About This Before We Continue

**Q1.** You are on-call. An alert fires at 2 AM:
"CheckoutSLOFastBurn". You open the checkout dashboard.
The top row shows RED for error rate. The time series
shows the error rate spiked at exactly 1:52 AM. The
deployment annotation shows "payment-service v2.4.0
deployed at 1:51 AM". The payment service dependency
panel shows payment error rate at 25%. What is your
next action? What do you need to determine before
rolling back vs investigating further? How does the
dashboard help you make this decision in the next
60 seconds?
_Hint: Correlation is not causation. The deployment
at 1:51 AM is suspicious but is it the cause? Check
the payment service's own dashboard. Did the payment
service deployment also coincide with an increase in
payment-specific errors? Or did something else change
at 1:52 AM (traffic spike, downstream service outage)?
The dashboard gives you the correlation; investigation
confirms causation._

**Q2.** Your checkout service dashboard shows these
metrics simultaneously: request rate is 2x higher than
usual, error rate is at 0.05% (below SLO), P99 latency
is at 480ms (near the 500ms SLO threshold), and CPU
is at 85%. Is this a crisis, a warning, or normal?
How do you use the dashboard to decide whether to wake
up an engineer, create a ticket, or do nothing?
What additional context from the dashboard would help
you make this decision?
_Hint: High traffic + near-SLO latency + elevated CPU
during a traffic spike might be normal scaling behaviour
(2x traffic → 2x CPU, latency scaling linearly). Check:
is there a deployment annotation? Is this a predictable
traffic pattern (Monday morning, promotion event)? The
error rate at 0.05% is well within SLO. Decision:
create a ticket for capacity review if this is unexpected;
monitor if it matches a known traffic pattern._

**Q3 (TYPE G):** Design a complete dashboard strategy
for a platform with 100 microservices. You cannot create
100 individual dashboards manually. You need: (1) a
service catalogue view showing health of all 100
services, (2) a per-service drill-down dashboard that
auto-generates for any new service, (3) a fleet-wide
infrastructure dashboard. Describe the dashboard-as-code
approach: what tool (Grafonnet, Jsonnet, or Terraform),
what template parameters, how new services are onboarded
automatically, and how you ensure all 100 service
dashboards stay in sync with new metric name changes.
_Hint: Grafonnet/Jsonnet allows a single template that
takes `service_name` as a parameter and generates the
full dashboard JSON. CI/CD generates one dashboard per
service from the template. When the template changes
(e.g., new panel added), regenerating all 100 dashboards
is a single CI run. Service onboarding = add service
name to a list, regenerate. This is the dashboard-as-code
principle applied at scale._

---

### 🎯 Interview Deep-Dive

**Q1: "What is the RED method and how do you apply it
to a service dashboard?"**
_Why they ask:_ Tests knowledge of dashboard design
methodology, not just tool proficiency.
_Strong answer includes:_

- RED = Rate, Errors, Duration. These three metrics
  capture the user-visible health of any service.
- Rate: requests per second (is the service receiving
  traffic as expected?)
- Errors: error rate as percentage of total requests
  (are users experiencing failures?)
- Duration: P99 latency (are users experiencing slow
  responses?)
- Application: the RED row on the service dashboard
  is the second row (after the SLO status summary).
  It shows time series for all three metrics. For
  latency, use a histogram heatmap not an average.
- Complement: RED is for services (request-driven).
  USE method (Utilisation, Saturation, Errors) is for
  infrastructure (resource-driven: CPU, memory, disk).

**Q2: "Why should you never show a raw counter value
on a dashboard stat panel?"**
_Why they ask:_ Tests whether the candidate understands
metric types and their correct visualisation.
_Strong answer includes:_

- A raw counter (e.g., `requests_total = 1,234,567`)
  is an ever-increasing number with no intrinsic meaning
  without context: what time period? What baseline?
- What you actually want to know: "how many requests
  are happening right now?" = requests per second =
  `rate(requests_total[5m])`
- Showing the counter total on a stat panel provides
  no actionable information. It does not tell you if
  traffic is high, low, or normal.
- The correct stat panel: show `rate()` with colour
  thresholds. Green = 900-1500 req/s (normal), yellow =
  < 900 or > 2000 (anomalous), red = 0 or > 5000.
- A counter's value is only useful for deriving rates
  and increases, not for direct display.

**Q3: "How would you structure a dashboard for a checkout
service to support an on-call engineer during an incident
at 3 AM?"**
_Why they ask:_ Tests practical dashboard design thinking,
specifically for the most demanding use case.
_Strong answer includes:_

- First principle: the engineer needs to assess health
  in < 10 seconds and identify the degraded component
  in < 2 minutes
- Row 1 (top): SLO status (stat panel with RED/GREEN),
  error budget remaining (gauge), current burn rate (stat)
  - "Is this an emergency?" question answered in 5 seconds
- Row 2: RED metrics as time series (rate, error rate,
  P99 latency), all with the last 2 hours as default
  time range, deployment annotations enabled
  - "What is the nature of the problem?" answered in 30s
- Row 3: Dependency health - downstream services (payment,
  inventory) error rates and latency - "Is this our fault
  or a dependency?" answered in 1 minute
- Row 4+: Infrastructure (CPU, memory, pods) - only
  consulted if rows 1-3 don't reveal the cause
- Key feature: direct links from the dashboard to
  the runbook, to recent logs filtered for errors,
  and to a recent trace sampled for errors
