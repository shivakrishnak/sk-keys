---
id: OBS-016
title: "Grafana -- Dashboards"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-015, OBS-006, OBS-007
used_by: OBS-009, OBS-010
related: OBS-015, OBS-010, OBS-017, OBS-009
tags:
  - observability
  - metrics
  - devops
  - pattern
  - intermediate
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/obs/grafana-dashboards/
---

⚡ TL;DR - Grafana is the open-source visualisation
layer that turns raw time-series data (Prometheus,
Loki, Elasticsearch, CloudWatch) into operational
dashboards and SLO status pages. A well-designed
Grafana dashboard answers the question "is everything
OK right now?" in under 10 seconds.

| #016            | Category: Observability & SRE                          | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Prometheus, Metrics Types, Logging Fundamentals        |                 |
| **Used by:**    | Alerting Fundamentals, Dashboards and Viz Basics       |                 |
| **Related:**    | Prometheus, Dashboards Basics, OpenTelemetry, Alerting |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without Grafana, engineers debug incidents by running
raw PromQL queries in the Prometheus UI, switching
to Kibana for logs, and maintaining separate custom
dashboards written in HTML. The on-call engineer
during a 3 AM incident is running the same 5 queries
from memory, context-switching between three tools,
and trying to correlate timestamps manually. There
is no standard view of "service health." Every incident
requires reinventing the investigation process.

**THE INVENTION:**
Grafana (open-sourced 2014) provides a single pane
of glass: one UI that connects to all data sources
(Prometheus, Loki, Elasticsearch, InfluxDB, CloudWatch,
Jaeger) and lets engineers build, share, and version-
control dashboards. When an alert fires at 3 AM,
the runbook points to a Grafana dashboard URL. The
on-call engineer opens one page and sees everything
they need: error rate, latency, traffic, saturation,
recent deployments, and related service health.

---

### 📘 Textbook Definition

**Grafana** is an open-source analytics and
visualisation platform that connects to multiple
data sources and renders metrics, logs, and traces
as configurable dashboards. Key concepts:

- **Data source:** a backend that Grafana queries -
  Prometheus, Loki, Elasticsearch, InfluxDB, Tempo,
  MySQL, CloudWatch, and 50+ others.
- **Panel:** a single visualisation (graph, stat,
  gauge, table, heatmap) with one or more queries.
- **Dashboard:** a collection of panels, shareable
  by URL, version-controlled as JSON.
- **Variable:** a dashboard template variable
  (e.g., `$service`, `$env`) that lets users switch
  between services/environments without editing queries.
- **Alerting (Grafana Alerts):** alert rules defined
  directly in Grafana, routing to Slack/PagerDuty
  (separate from Prometheus Alertmanager).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Grafana takes data from Prometheus (and other sources)
and turns it into dashboards that show whether a
service is healthy - accessible to the whole team,
not just engineers who know PromQL.

> Think of a hospital patient monitor. The raw data
> is the same sensor values - heart rate, blood
> pressure, oxygen saturation (Prometheus metrics).
> The patient monitor (Grafana) converts those numbers
> into colour-coded displays, trend graphs, and alarm
> thresholds that any nurse can interpret at a glance.
> The doctor (SRE) can configure what the monitor
> displays and which values trigger alarms. Without
> the monitor, every nurse would need to run the
> sensor query directly and interpret raw numbers.
> With the monitor, the status is visible to the
> whole team in real time.

---

### 🔩 First Principles Explanation

**THE DASHBOARD HIERARCHY:**

```
Organisation (Grafana org)
  └── Folders (team namespaces)
       └── Dashboards (service health views)
            └── Rows (sections: Overview, DB, Cache)
                 └── Panels (individual visualisations)
                      └── Queries (PromQL / LogQL / SQL)
```

**DASHBOARD DESIGN PRINCIPLES:**

**1. Golden signals first:**
Every service dashboard should start with the four
golden signals: latency (P50, P95, P99), traffic
(requests/second), errors (error rate %), saturation
(CPU, memory, queue depth). These are the first
panels in the first row.

**2. Drill-down layers:**

- Row 1: summary (is it OK? one stat per signal)
- Row 2: trend (how is it behaving over time?)
- Row 3: component detail (database, cache, upstream)

**3. Correlate by time:**
All panels should share the same time range. A
deployment marker annotation on all panels lets
engineers instantly see "did the error rate increase
after the 14:30 deployment?"

**4. Template variables for reuse:**
A single dashboard template with `$service` and `$env`
variables replaces 50 service-specific dashboards.
Teams select their service from a dropdown.

---

### 🧪 Thought Experiment

**THE 10-SECOND RULE:**

At 3 AM, an alert fires. The on-call engineer opens
the runbook link. It points to a Grafana dashboard.

**Dashboard A (BAD design):**

- 30 panels, no rows, no hierarchy
- Red/amber/green indicators using absolute thresholds
  set years ago, no longer relevant
- Panels for metrics that were important in 2021 but
  not today
- No time correlation between panels
- No deployment markers

**What happens:** The engineer spends 15 minutes
trying to understand what they're looking at. They
cannot find the signal in the noise. They start
running individual PromQL queries instead of using
the dashboard.

**Dashboard B (GOOD design):**

- Row 1: "SLO Status" - three stat panels: current
  SLI vs target, budget remaining %, burn rate
- Row 2: "Golden Signals" - error rate, P99 latency,
  RPS, saturation - 4 time-series panels
- Row 3: "Upstream Dependencies" - database,
  cache, payment gateway health
- Deployment markers on all graphs
- Template variables: `$service`, `$env`

**What happens:** In 10 seconds the engineer sees
"error rate spiked at 14:30, correlates with deployment
marker, upstream payment gateway health is red."
Root cause identified. Mitigation: rollback.

---

### 🧠 Mental Model / Analogy

> An aircraft cockpit is designed for exactly this
> use case: critical information visible at a glance,
> non-critical information accessible on demand,
> no information that is irrelevant to flight safety.
> The pilot does not need to look at every instrument
> to know if the flight is OK - the critical instruments
> are prominently positioned and lit red when outside
> safe ranges.
>
> A Grafana dashboard should follow the same design
> philosophy. The most critical signal (is the SLO
> being met?) should be the largest, most prominent
> panel. Supporting information (golden signals,
> upstream health) should be visible but not competing
> for attention. Historical or debug information should
> be accessible but not cluttering the primary view.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Grafana is a website that shows graphs of your service's
health. When something goes wrong, you open Grafana
to see what's broken.

**Level 2 - How to use it (junior):**
Open the dashboard URL from the runbook. Use time range
controls to zoom into the incident window. Check the
error rate panel. Hover over the spike to see the
timestamp. Look for deployment markers. Use the
`$service` variable to switch to upstream services.

**Level 3 - How to build (mid-level):**
Create panels with PromQL queries. Use `legend_format`
for readable series labels. Apply colour thresholds
(green/yellow/red) based on SLO targets. Add template
variables for service/environment/region. Add annotation
queries to show deployments. Version-control dashboard
JSON in git.

**Level 4 - Dashboard as code (senior):**
Use Grafonnet (Jsonnet library) or Grafana Terraform
provider to manage dashboards as code. Deploy dashboard
changes through CI/CD. Use dashboard folders per team
with RBAC. Store dashboards in the grafonnet-generated
JSON in the same git repo as the service code.

**Level 5 - Platform engineering (staff):**
Grafana in a multi-tenant organisation: RBAC per team,
dashboard provisioning via ConfigMaps in Kubernetes,
dashboard organisation conventions (per-service,
per-tier, SLO overview). Alerting consolidation:
when to use Grafana Alerts vs Prometheus Alertmanager.
Grafana OnCall for on-call scheduling and escalation
policies (if using Grafana's full platform).

---

### ⚙️ How It Works (Mechanism)

**QUERY EXECUTION FLOW:**

```
[Browser: user opens dashboard]
  ↓
[Grafana UI: sends queries to Grafana backend]
  Panel 1 query: rate(checkout_errors[5m])
  Time range: last 1 hour
        ↓
[Grafana backend: queries data source]
  POST /api/v1/query_range to Prometheus
  {
    "query": "rate(checkout_errors_total[5m])",
    "start": 1681234000,
    "end":   1681237600,
    "step":  "15s"
  }
        ↓
[Prometheus returns: time-series data points]
  [{ts: 1681234000, val: 0.002}, ...]
        ↓
[Grafana UI: renders time-series graph]
  Applies colour thresholds (red if > 0.01)
  Adds deployment annotation markers
  Shows legend: "error_rate"
```

**ANNOTATION QUERIES:**

```json
{
  "datasource": "Prometheus",
  "expr": "changes(deploy_timestamp{service=\"checkout\"}[1m]) > 0",
  "step": "60s",
  "title": "Deployment",
  "text": "{{version}}"
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**INCIDENT INVESTIGATION FLOW:**

```
[02:47 AM: PagerDuty alert fires]
  "CheckoutSLOFastBurn: error rate 14.4x above SLO"
        ↓
[On-call opens runbook → Grafana dashboard link]
  Dashboard: "Checkout Service - SLO Overview"
        ↓
[Row 1 - SLO Status]
  Budget remaining: -3% (BREACHED)
  Current SLI: 98.5% (SLO target: 99.9%)
  Burn rate: 14.4x
        ↓
[Row 2 - Golden Signals]
  Error rate: 1.5% (spike at 02:44)
  P99 latency: 2,340ms (normal: 180ms)
  Traffic: 450 rps (normal: 460 rps → not a traffic spike)
  CPU saturation: 62% (normal)
        ↓
[Correlate: deployment marker visible at 02:44]
  Version: checkout-api:v1.47.2 deployed
        ↓
[Row 3 - Upstream dependencies]
  payment-gateway: RED (error rate 15%)
  database: GREEN
  cache: GREEN
        ↓
[Conclusion: v1.47.2 deployment introduced payment-gateway
 integration bug. Mitigation: rollback to v1.47.1]
  Time to diagnosis: 4 minutes
```

---

### 💻 Code Example

**Example 1 - BAD: Hardcoded thresholds without SLO context:**

```json
// BAD: threshold set to an arbitrary 500ms
// with no connection to the SLO target or baseline
{
  "type": "graph",
  "title": "Checkout Latency",
  "thresholds": [{ "value": 500, "colorMode": "critical" }]
  // Problem 1: Is 500ms bad? What's the SLO target?
  // Problem 2: Same threshold for P50 and P99?
  // Problem 3: No context about normal behavior
}
```

**Example 2 - GOOD: SLO-aware dashboard JSON:**

```json
{
  "type": "stat",
  "title": "SLO Compliance (30d)",
  "description": "Target: 99.9%. Current availability",
  "targets": [
    {
      "datasource": "prometheus",
      "expr": "sum(increase(
          checkout_requests_total{status=~\"2..\"}[30d])) / sum(
              increase(
                  checkout_requests_total{status!~\"4..\"}[30d]))",
      "legendFormat": "30d SLI"
    }
  ],
  "thresholds": {
    "steps": [
      { "color": "red", "value": null },
      { "color": "yellow", "value": 0.995 },
      { "color": "green", "value": 0.999 }
    ]
  },
  "mappings": [],
  "unit": "percentunit"
}
```

**Example 3 - Dashboard as code (Grafonnet):**

```jsonnet
// dashboard.jsonnet
local grafana = import 'github.com/grafana/grafonnet-lib/grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local graphPanel = grafana.graphPanel;
local prometheus = grafana.prometheus;

dashboard.new(
  'Checkout Service - Golden Signals',
  schemaVersion=27,
  time_from='now-1h',
  refresh='30s',
  tags=['sre', 'checkout'],
)
.addTemplate(
  grafana.template.datasource(
    'datasource', 'prometheus', 'Prometheus', hide=''
  )
)
.addTemplate(
  grafana.template.new(
    'env', '$datasource',
    'label_values(up, environment)',
    label='Environment',
  )
)
.addPanel(
  graphPanel.new(
    'Error Rate',
    datasource='$datasource',
    min=0,
    max=0.05,
  )
  .addTarget(
    prometheus.target(
      'sum(rate(checkout_errors_total{env="$env"}[5m])) / sum(rate(
          checkout_requests_total{env="$env"}[5m]))',
      legendFormat='error rate',
    )
  ),
  gridPos={x: 0, y: 8, w: 12, h: 8}
)
```

---

### ⚖️ Comparison Table

| Feature           | Grafana OSS                          | Grafana Cloud                         | Datadog Dashboards | CloudWatch Dashboards |
| ----------------- | ------------------------------------ | ------------------------------------- | ------------------ | --------------------- |
| Data sources      | 50+ plugins                          | 50+ (managed)                         | Datadog only       | AWS only              |
| Dashboard as code | JSON / Grafonnet                     | JSON / Grafonnet                      | Terraform          | CloudFormation        |
| Alerting          | Grafana Alerts                       | Grafana Alerts                        | Datadog Monitors   | CloudWatch Alarms     |
| Multi-tenancy     | Manual RBAC                          | Managed                               | Managed            | IAM-based             |
| Cost              | Free (self-hosted)                   | Free tier + paid                      | Per host/metric    | AWS pricing           |
| Best for          | Kubernetes-native, open-source stack | Managed Grafana with low ops overhead | All-in-one SaaS    | AWS-only workloads    |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Grafana is just for graphs"                                   | Grafana also provides alerting, on-call management (Grafana OnCall), incident management (Grafana Incident), and log exploration (via Loki). It has evolved from a visualisation tool to a full observability platform.                                                               |
| "More panels = better dashboard"                               | Dashboard overload causes alert fatigue and slower incident diagnosis. The 10-second rule: the primary health signal should be readable in 10 seconds. Fewer, more meaningful panels outperform dense dashboards.                                                                     |
| "Grafana stores the data"                                      | Grafana is a visualisation layer only. It queries data sources (Prometheus, Loki, Elasticsearch) but does not store the underlying time-series. If Prometheus is down, Grafana shows "No data."                                                                                       |
| "Dashboard JSON in git is optional"                            | Dashboards not in git will be recreated from scratch after a Grafana rebuild. Grafana provisioning (ConfigMaps or provisioning directories) ensures dashboards are restored automatically. Version control enables rollback when a dashboard change breaks an investigation workflow. |
| "Grafana alerting and Prometheus alerting are interchangeable" | Prometheus Alertmanager has more mature routing, inhibition, and deduplication logic. Grafana Alerts are more accessible for non-Prometheus data sources. In Prometheus-heavy stacks, Alertmanager is typically preferred.                                                            |

---

### 🚨 Failure Modes & Diagnosis

**Dashboard shows "No data" during an active incident**

**Symptom:**
Alert fires at 3 AM. On-call opens the Grafana
dashboard. All panels show "No data" or "Last value:
N/A." The incident cannot be investigated visually.
The engineer resorts to running raw PromQL queries.

**Root Cause candidates:**

1. Prometheus data source is down (Prometheus crashed
   - common if cardinality explosion caused OOM)
2. Time range mismatch: dashboard default time range
   is "last 5 minutes" but the scrape gap is longer
3. The metric name in the panel query changed after
   a service update

**Diagnostic:**

```bash
# Check Grafana data source health
# Grafana UI: Configuration → Data Sources → Test

# Check if Prometheus is responding
curl http://prometheus:9090/api/v1/query \
  '?query=up'

# Check if specific metric exists in Prometheus
curl http://prometheus:9090/api/v1/series \
  '?match[]=checkout_requests_total'
```

**Fix:**

- For Prometheus down: resolve Prometheus first,
  dashboards will recover automatically
- For time range: set dashboard default to "last 1h"
  (wider than scrape interval)
- For renamed metrics: update panel queries to match
  current metric names; add metric existence alert

---

**Dashboard drift: saved dashboard diverges from code**

**Symptom:**
An engineer notices that the production Grafana
dashboard for the checkout service has been modified
by someone during an incident. The panels no longer
match the dashboard JSON in git. The next Grafana
rebuild will overwrite the changes (or the changes
are lost forever if not in git).

**Root Cause:**
Dashboard changes made in the UI during incidents
are not reflected in git. The team has no policy
for dashboard updates (UI vs code).

**Fix:**

1. Enable Grafana provisioning from git:
```yaml
   # grafana.ini
   [paths]
   provisioning = /etc/grafana/provisioning
```
```yaml
   # provisioning/dashboards/provider.yaml
   apiVersion: 1
   providers:
     - name: default
       folder: SRE
       type: file
       options:
         path: /var/lib/grafana/dashboards
         # mounted from ConfigMap sourced from git
```
2. Add an automated test that exports the Grafana
   dashboard JSON and diffs it against git after
   each incident to detect drift.

**Prevention:**
Policy: all dashboard changes must go through a PR.
The provisioning pipeline deploys dashboard changes.
Direct UI edits in production are explicitly prohibited.

---

**High-cardinality template variable kills Grafana**

**Symptom:**
A new `$user_id` template variable is added to a
dashboard. The variable query loads all user IDs
(2 million values) from Prometheus. The Grafana
browser tab freezes while loading the dropdown.
The dashboard becomes unusable.

**Root Cause:**
Template variable queries that return high-cardinality
label values are executed when the dashboard loads.
2 million values in a dropdown is not renderable.

**Fix:**
Replace high-cardinality template variables with
bounded categorical variables:

```yaml
# BAD: all user IDs (2M values)
query: label_values(checkout_requests_total, user_id)

# GOOD: bounded service/env variables
query: label_values(up, service)   # 50 values
query: label_values(up, environment)  # 4 values
```

For user-specific investigation, link to a Kibana
or log exploration dashboard that accepts a free-text
user ID filter.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Prometheus Metrics Collection` - the primary data
  source for Grafana in Kubernetes-native stacks.
  Grafana is the visualisation layer for Prometheus.
- `Metrics Types (Counter, Gauge, Histogram)` - the
  data types that Grafana renders in different panel types

**Builds On This (learn these next):**

- `Alerting Fundamentals` - Grafana can define alerts
  directly on dashboard panels, or visualise alerts
  from Prometheus Alertmanager
- `Dashboards and Visualisation Basics` - the broader
  context of dashboard design principles

**Alternatives / Comparisons:**

- `Kibana` - Elasticsearch-native visualisation.
  Better for log-centric investigation; weaker for
  metrics-based SLO dashboards.
- `Datadog Dashboards` - managed SaaS alternative.
  Less flexible but lower operational overhead.
  All data must be in Datadog.
- `CloudWatch Dashboards` - AWS-native, limited to
  AWS data sources, no Prometheus integration.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Visualisation layer: connects to         │
│              │ Prometheus, Loki, ES, CloudWatch, etc.   │
├──────────────┼──────────────────────────────────────────┤
│ DASHBOARD    │ Row 1: SLO status (stat panels)          │
│ STRUCTURE    │ Row 2: Golden signals (time-series)      │
│              │ Row 3: Component/dependency health       │
├──────────────┼──────────────────────────────────────────┤
│ 10-SECOND    │ On-call must know "is it OK?"            │
│ RULE         │ in 10 seconds without running queries    │
├──────────────┼──────────────────────────────────────────┤
│ TEMPLATE     │ $service, $env, $region                  │
│ VARIABLES    │ Never: $user_id (high cardinality)       │
├──────────────┼──────────────────────────────────────────┤
│ ANNOTATIONS  │ Deployment markers: see if error spike   │
│              │ correlates with deploy time              │
├──────────────┼──────────────────────────────────────────┤
│ AS CODE      │ Dashboard JSON in git. Provision via     │
│              │ ConfigMap or provisioning dir.           │
├──────────────┼──────────────────────────────────────────┤
│ COMMON BUG   │ No data = Prometheus down or metric      │
│              │ renamed. Check data source health first. │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ 30-panel dashboard with no hierarchy.    │
│              │ Fewer, better panels > more panels.      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Alerting → Loki log queries → Tempo trace│
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Observability tools are only valuable if they are
used under pressure. A dashboard that takes 15 minutes
to understand during an incident is worse than no
dashboard - it wastes time that could be spent
on direct investigation. Design every observability
artifact (dashboard, runbook, alert) for the 3 AM,
half-awake, high-stress use case. Ask: can a
junior engineer who has never seen this service
diagnose a P1 incident from this dashboard alone
within 10 minutes? If not, redesign.

---

### 💡 The Surprising Truth

The most counterintuitive truth about Grafana: the
best Grafana dashboards are not built by the engineers
who know the most about the system - they are built
by engineers who have been on-call for the system.
The on-call engineer knows exactly what information
is missing at 3 AM. They know which query takes 5
minutes to remember and run manually. They know
which upstream service health check is never on the
dashboard but is always the first thing to check.
Post-incident dashboard improvements (adding the
missing check, adding the deployment marker, adding
the upstream dependency panel) are among the most
valuable reliability investments a team can make.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[DESIGN]** Design a Grafana dashboard for a new
   microservice: specify the panel layout, the PromQL
   for each panel, the thresholds, the template
   variables, and the annotation queries.
2. **[BUILD]** Implement the dashboard as code using
   Grafonnet or the Grafana API, check the JSON into
   git, and configure Grafana provisioning to deploy
   it automatically.
3. **[DEBUG]** Given a dashboard showing "No data"
   during an incident, diagnose whether the problem
   is Prometheus down, metric renamed, or time range
   mismatch - using only the Grafana UI and curl to
   the Prometheus API.
4. **[CRITIQUE]** Review a colleague's 40-panel
   Grafana dashboard and propose a redesign that
   applies the 10-second rule, golden signals first,
   and template variables for reuse.
5. **[EXPLAIN]** Explain to a product manager why
   dashboards should be in git and deployed via CI/CD,
   using the "dashboard drift during incident" failure
   mode as the motivating example.

---

### 🧠 Think About This Before We Continue

**Q1.** You are building the checkout service dashboard.
You want to show the P99 latency for each payment
method (visa, mastercard, paypal, crypto). Should
you create 4 separate panels (one per payment method)
or one panel with a `$payment_method` variable?
What is the tradeoff? When is each approach better?
_Hint: 4 panels = always visible, can compare side
by side during incident. 1 panel with variable =
less visual clutter, but requires switching to see
each payment method. For incident investigation where
you need to compare all at once: 4 panels. For routine
monitoring where you check one at a time: variable.
Consider: use a heatmap that shows all payment methods
at once as stacked series._

**Q2.** Your team has 15 microservices. The current
approach is one dashboard per service (15 dashboards),
all manually created in the Grafana UI with no version
control. You are tasked with "getting dashboards into
git." What is your migration plan? How do you prevent
dashboard drift going forward? What are the risks
of the migration?
_Hint: Step 1: export existing dashboards via Grafana
API as JSON. Step 2: review and clean up (remove
stale panels, standardise naming). Step 3: check into
git. Step 4: set up provisioning. Step 5: lock down
UI edits (require PR for changes). Risk: if provisioning
overwrites a dashboard with an older git version,
investigation context built during incidents is lost.
Mitigation: snapshot dashboards before provisioning
changes._

**Q3 (TYPE G):** You are the SRE lead at a 200-person
engineering org with 80 microservices. The current
state: each team maintains their own Grafana dashboards
in their own folders, using different conventions,
different metric naming, and different panel types.
The on-call rotation covers all 80 services. On-call
engineers cannot quickly find or interpret dashboards
for services they did not build. Design the Grafana
dashboard standards for the organisation: what
conventions, what minimum required panels, what
provisioning strategy, how to enforce standards
without blocking teams.
_Hint: Minimum required panels: SLO compliance, 4
golden signals, upstream dependencies, recent
deployments. Convention: use standard template
variables ($service, $env, $region). Provisioning:
a platform team maintains a "golden template" per
service type (API, batch, database). Teams fork
the template and add service-specific panels.
Enforcement: CI/CD lint that checks dashboard JSON
against a schema (does it have the required panels?).
Not: blocking teams from adding custom panels._

---

### 🎯 Interview Deep-Dive

**Q1: "How would you design a Grafana dashboard for
an API service? What panels would you include?"**
_Why they ask:_ Tests practical observability design
and understanding of the golden signals model.
_Strong answer includes:_

- Start with the purpose: what question does the
  dashboard answer? ("Is the service healthy right now?")
- Row 1: SLO status - current SLI vs target, error
  budget remaining, burn rate
- Row 2: Golden signals - error rate, P50/P99 latency,
  RPS (traffic), saturation (CPU, memory, queue depth)
- Row 3: Upstream dependencies - each downstream
  service the API calls, their health status
- Annotations: deployment markers, SLO events
- Template variables: $service, $env for reuse
- 10-second rule: the on-call must know "is it OK?"
  without running any queries

**Q2: "Dashboards stored in git vs created in UI -
what are the tradeoffs?"**
_Why they ask:_ Tests understanding of operational
discipline and reliability practice.
_Strong answer includes:_

- UI: fast iteration, accessible to all engineers,
  no tooling required. Risk: no history, lost on
  rebuild, no review, drift between teams.
- Git + provisioning: version history, code review,
  automated deployment, consistent across all envs.
  Cost: requires Grafonnet/JSON knowledge, slower
  iteration.
- Recommendation: git for permanent dashboards,
  UI for incident-time exploratory panels (with
  a policy to commit any keeper to git post-incident)

**Q3: "During an incident, the Grafana dashboard shows
'No data' for all panels. How do you debug this?"**
_Why they ask:_ Tests both tool knowledge and systematic
debugging under pressure.
_Strong answer includes:_

- Step 1: check if Prometheus data source is healthy
  (Grafana UI: Configuration → Data Sources → Test)
- Step 2: query Prometheus directly to confirm it's
  responding: `curl http://prometheus:9090/api/v1/query?query=up`
- Step 3: check if the specific metric still exists:
  `curl http://prometheus:9090/api/v1/series?match[]=checkout_requests_total`
- Step 4: check if the dashboard time range includes
  data (if the incident started 1 minute ago but the
  time range is "last 5 minutes", the panel may show
  no data if scrape interval is 1m)
- Critical: don't waste 10 minutes fixing Grafana
  during an active incident. Open Prometheus directly
  and run queries there while investigating the
  Grafana issue in parallel.

> Entry stub. Generate full content using Master Prompt v3.0.
