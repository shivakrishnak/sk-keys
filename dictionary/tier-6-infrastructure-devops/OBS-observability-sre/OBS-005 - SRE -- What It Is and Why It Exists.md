---
id: OBS-005
title: "SRE -- What It Is and Why It Exists"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-001
used_by: OBS-011, OBS-012, OBS-013
related: OBS-001, OBS-011, OBS-012
tags:
  - observability
  - reliability
  - foundational
  - mental-model
  - devops
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /obs/sre-what-it-is-and-why-it-exists/
---

# OBS-005 - SRE -- What It Is and Why It Exists

⚡ TL;DR - SRE is the discipline of applying software
engineering principles to operations so that reliability
becomes a measurable, improvable system property rather than
a reactive heroic effort.

| #005 | Category: Observability & SRE | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | What Is Observability and Why It Matters | |
| **Used by:** | SLI (Service Level Indicator), SLO (Service Level Objective), SLA (Service Level Agreement) | |
| **Related:** | What Is Observability and Why It Matters, SLI - Service Level Indicator, SLO - Service Level Objective | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before SRE existed at Google, the operations team and the
development team were separate organisations with conflicting
incentives. Developers shipped features as fast as possible.
Operations was responsible for keeping the system stable.
Every deployment was a battle: developers wanted to release;
operations wanted to freeze. The operations team accumulated
tribal knowledge about production systems that developers
never understood. When something broke at 3 AM, the same
operations heroes scrambled through the same manual runbooks.
Reliability was not improving - it was being sustained
through individual effort and heroics.

**THE BREAKING POINT:**
At Google's scale (billions of search queries per day by
2003), the traditional ops model was failing in two
directions. First, the ops team could not scale - hiring
more operators to manually manage more servers was not
sustainable. Second, reliability could not be measured or
improved because it was not treated as an engineering
problem with defined metrics and systematic solutions.

**THE INVENTION MOMENT:**
In 2003, Google's Ben Treynor Sloss was given a small
software engineering team and asked to run Google's production
operations. His insight: if operations is a software problem,
it should be solved with software engineering. This created
Site Reliability Engineering - a discipline that treats
reliability as a feature to be engineered, not a condition
to be hoped for.

**EVOLUTION:**
Google practiced SRE internally from 2003. The Google SRE
Book (2016) published the practice for the first time,
introducing SLIs, SLOs, error budgets, toil, and
blameless post-mortems. The concepts spread rapidly:
by 2020, most major tech companies had SRE teams.
DevOps (which emerged in 2009) shares philosophical
overlaps but differs in practice: DevOps is a cultural
movement; SRE is Google's specific implementation of
that culture with precise engineering tools.

---

### 📘 Textbook Definition

**Site Reliability Engineering (SRE)** is a discipline in
which software engineers are responsible for the reliability,
availability, and performance of production systems. SRE
applies software engineering practices - automation,
measurement, and systematic problem-solving - to operations
tasks that were historically performed manually.

The defining principle: reliability is a feature that must
be designed, measured, and improved using the same
engineering rigour applied to any other system property.
SRE teams define reliability using Service Level Indicators
(SLIs), set targets using Service Level Objectives (SLOs),
and manage the trade-off between reliability and velocity
using error budgets.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SRE treats reliability as an engineering problem with
measurable targets, not as a heroic operational effort.

> Think of civil engineering. A bridge is not "reliable"
> because a dedicated bridge-maintenance hero inspects it
> every night. It is reliable because it was designed to
> precise load tolerances, inspected against defined
> standards, and monitored with instruments. SRE applies
> the same principle to software: design for reliability,
> measure it precisely, and automate the repetitive work
> that would otherwise require human heroes.

**One insight:**
The most important SRE concept is the error budget: if your
SLO is 99.9% uptime, you have 8.7 hours of downtime per year
to spend. This budget is shared between reliability failures
and planned maintenance. The key insight: reliability and
velocity are in tension, and the error budget makes that
tension explicit and manageable rather than political.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. 100% reliability is neither achievable nor desirable - the
   cost approaches infinity as you approach 100%
2. Reliability must be measured to be improved - without an
   SLI, "the service is reliable" is meaningless
3. Operations work that can be automated should be automated
   (toil reduction) - repetitive manual work does not scale
4. When something fails, the system is to blame, not the
   individual (blameless post-mortems)

**DERIVED DESIGN:**
Given that reliability is measurable and has a cost, the
optimal design is: set a reliability target (SLO), measure
current reliability (SLI), calculate the gap (error budget),
and invest in reliability improvements proportional to the
budget consumed. When the error budget is abundant, invest in
velocity (ship features). When the error budget is depleted,
freeze deployments and invest in reliability.

**THE TRADE-OFFS:**
**Gain:** Reliability becomes a measurable engineering
property. The ops/dev tension is resolved by a shared
metric (error budget). Repetitive work is automated.
Incidents produce learning rather than blame.
**Cost:** SRE requires software engineers, not operators -
a more expensive hire. SLO definition and instrumentation
require upfront investment. Blameless culture is hard to
build and maintain.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The tension between reliability and velocity
is fundamental. Any organisation that ships software to
production must manage this tension. SRE makes it explicit.
**Accidental:** The specific Google implementations (error
budget policy, toil calculation, production readiness
reviews) are accidental. Other organisations adapt these
practices to their own context.

---

### 🧪 Thought Experiment

**SETUP:**
Two companies run identical payment services. Company A uses
traditional ops (a separate operations team running manual
processes). Company B uses SRE (software engineers running
automated systems with defined SLOs).

**WHAT HAPPENS WITH TRADITIONAL OPS (Company A):**
A payment service degrades on Black Friday. The operations
team is paged. They manually SSH into servers, check logs,
restart processes. They have been through this before. 45
minutes of manual work restores the service. The incident
is written up as "resolved - operator restarted service."
No root cause analysis. Same incident recurs in 3 months.

**WHAT HAPPENS WITH SRE (Company B):**
The payment service's error budget is 0.1% monthly errors.
An automated alert fires when the burn rate exceeds 5x the
sustainable rate. The on-call engineer opens the runbook
(automated, linked from the alert). The runbook identifies
the root cause from structured signals in 8 minutes. The
service auto-scales and a fix is deployed. A post-mortem
is scheduled to identify why the system allowed this to
occur. Action items prevent recurrence. The same incident
does not recur.

**THE INSIGHT:**
SRE treats each incident as a data point in a systematic
improvement process, not as a one-off emergency to survive.
The error budget makes the cost of reliability failures
visible and shared between development and operations.

---

### 🧠 Mental Model / Analogy

> A Formula 1 pit crew does not succeed through heroics.
> They train every procedure until it is automated muscle
> memory. They measure every metric: tyre wear rate, fuel
> consumption per lap, component temperature thresholds.
> When a component approaches its failure threshold, they
> act before failure - not after. Post-race debriefs are
> blameless: "the front-left wheel nut took 0.3s longer
> than target - why? What was the system failure?" No
> driver is blamed for a pit crew timing miss.

Mapping:
- "Pit crew muscle memory" - SRE automation (runbooks,
  auto-scaling, automated remediation)
- "Tyre wear rate, fuel metrics" - SLIs (measurable
  reliability indicators)
- "Performance threshold" - SLO (reliability target)
- "Acts before failure" - proactive SRE (toil reduction,
  capacity planning)
- "Blameless debrief" - post-mortem culture

**Where this analogy breaks down:** An F1 pit crew acts in
seconds on a fixed, well-understood problem. SRE deals with
unanticipated failure modes in complex distributed systems.
The planning rigour is similar; the response time and
uncertainty are very different.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
SRE is a job role and a discipline where software engineers
are responsible for keeping services reliable and fast. They
automate repetitive operations work and measure reliability
with numbers so it can be improved.

**Level 2 - How to use it (junior developer):**
SRE teams define SLOs (e.g., 99.9% of checkout requests
succeed), measure SLIs (the actual success rate), and track
the error budget (how much downtime is left before the SLO
is breached). When the error budget is low, new feature
deployments are paused until reliability improves.

**Level 3 - How it works (mid-level engineer):**
The SRE practice is built on five concepts:
- SLI: the metric that measures reliability (error rate)
- SLO: the target for that metric (error rate < 0.1%)
- Error budget: the allowed failures before SLO breach
- Toil: repetitive, manual operations work to be automated
- Blameless post-mortem: systematic root cause analysis
  without blame attribution

**Level 4 - Why it was designed this way (senior/staff):**
SRE solves the classic ops-dev conflict. Developers want to
deploy frequently (velocity). Operations wants stability
(reliability). Without SRE, these teams fight political
battles. With SRE and an error budget, the conflict becomes
a data problem: "we have 8.7 hours of downtime left this
month - should we deploy this risky feature?" The answer is
objective, not political. The error budget policy also
creates a natural incentive: when development deploys
reliable code, the error budget is preserved and velocity
is maintained. When deployments cause failures, the budget
is consumed and velocity must slow.

**Level 5 - Mastery (distinguished engineer):**
The most sophisticated SRE debate is the right SLO level.
Setting an SLO too high (99.999%) forces over-investment in
reliability at the cost of velocity, and users may not
perceive the difference between 99.99% and 99.999%. Setting
it too low (99%) creates poor user experience. The art is
setting SLOs at the level where improving further would not
noticeably improve user satisfaction - the point of
diminishing returns. Google calls this "the right SLO is
the minimum that keeps users happy." Staff engineers also
recognise that SRE culture is harder to establish than SRE
tooling. A team can implement error budgets and still fight
politically about them if the culture of data-driven
decision-making is not established first.

**EXPERT THINKING CUES:**
- Red flag: SLOs set without measurement of current
  performance. An SLO of 99.9% on a service currently at
  95% reliability is not an SLO - it is aspirational fiction.
- Decision heuristic: the SLO level should reflect what
  users actually need, not what is technically impressive.
- At scale, the error budget policy is the key governance
  tool. Who decides when to freeze deployments? The policy,
  not the SRE team.

---

### ⚙️ How It Works (Mechanism)

**The SRE operating model has six practices:**

**1. Defining SLIs:**
Choose the metric that best represents user experience for
this service. For a web API: request success rate, request
latency P99. For a batch job: job success rate, job
completion time. SLIs must be measurable and correlated
with user satisfaction.

**2. Setting SLOs:**
Set a target for the SLI based on user expectations and
current system capability. 99.9% success rate means 0.1%
error budget. SLOs must be achievable - an SLO higher than
current performance requires a reliability investment before
it can be set.

**3. Calculating error budgets:**
Monthly error budget = (1 - SLO) x seconds in month.
At 99.9% SLO: 0.001 x 2,592,000 seconds = 2,592 seconds
(43.2 minutes) of downtime allowed per month.

**4. Toil reduction:**
Identify and measure toil: manual, repetitive, automatable
operations work. Track toil as a percentage of SRE
engineer time. Target: less than 50% of SRE time on toil;
remainder on engineering improvements.

**5. On-call management:**
SREs rotate on-call duty. Response time SLOs (15 minutes
for P1 incidents) are measured. On-call load is tracked
and balanced. Excessive on-call load is a signal that toil
is too high and automation investment is needed.

**6. Blameless post-mortems:**
After every significant incident, hold a structured
post-mortem. Document: timeline, contributing factors,
impact, action items. Never attribute cause to individual
error. Focus on: what system conditions allowed the human
error to have this impact?

```
┌─────────────────────────────────────────┐
│  SRE Operating Model                    │
├─────────────────────────────────────────┤
│                                         │
│  SLI defined → SLO set → Budget calc   │
│       │                                 │
│       ↓                                 │
│  Measure SLI continuously               │
│       │                                 │
│       ↓                                 │
│  Budget OK? → Deploy freely             │
│  Budget low? → Freeze deploys           │
│  Budget exhausted? → Incident review    │
│                                         │
│  Every incident → Blameless post-mortem │
│  Repetitive work → Automate (toil)     │
│                                         │
└─────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[SLI measured continuously from production signals]
    ↓
[Error budget calculated: remaining budget this month]
    ↓
[Development team deploys feature]
    ↓
[SRE monitors SLI burn rate after deployment]
    ↓
[SRE team ← YOU ARE HERE: alert if burn rate > threshold]
    ↓
[Budget OK: deployment proceeds, no action]
    ↓
[Budget low: deployment freeze, reliability sprint]
```

**FAILURE PATH:**
SLO is breached. Error budget hits zero. Deployment freeze
triggered. Post-mortem scheduled. Action items assigned to
development and SRE. Feature deployments resume only after
reliability improvements are shipped and validated.

**WHAT CHANGES AT SCALE:**
At scale, error budget management becomes a governance
process. Multiple teams share a service SLO. The error
budget policy must define who can override a freeze and
under what conditions. Multi-region SLOs require careful
definition: is 99.9% measured globally or per region?

---

### 💻 Code Example

**Example 1 - BAD: Vague, unmeasured reliability target:**

```yaml
# BAD: "highly available" with no measurement
# This is a goal, not an SLO - cannot be monitored or enforced
services:
  checkout:
    description: "Highly available checkout service"
    reliability: "Best effort"
    # How do you know if you are meeting this?
    # You cannot - because it is not measurable
```

**Example 2 - GOOD: Measurable SLI with clear SLO:**

```yaml
# GOOD: measurable SLO with defined error budget policy
slo:
  service: checkout
  sli:
    metric: checkout_requests_success_ratio
    # success = HTTP 2xx / total requests
    good_events: "rate(checkout_requests_total{status='2xx'}[5m])"
    total_events: "rate(checkout_requests_total[5m])"
  objective: 0.999         # 99.9% success rate
  window: 30d               # monthly rolling window
  error_budget_policy:
    # Freeze deploys when 50% of monthly budget is consumed
    # in less than 10% of the month (5x burn rate)
    fast_burn_threshold: 5.0
    action: freeze_deployments
    notify: [sre-oncall, dev-team-lead]
```

**Example 3 - Burn rate alert in Prometheus:**

```yaml
# Prometheus rule: page when error budget burns too fast
groups:
- name: checkout-slo
  rules:
  - alert: CheckoutSLOFastBurn
    expr: |
      (
        rate(checkout_requests_total{status!~"2.."}[1h])
        / rate(checkout_requests_total[1h])
      ) > 5 * (1 - 0.999)
    for: 5m
    labels:
      severity: page
    annotations:
      summary: "Checkout error budget burning at 5x rate"
      runbook: "https://wiki/runbooks/checkout-slo"
```

---

### ⚖️ Comparison Table

| Practice | Reliability measure | Ops/dev alignment | Automation focus | Best For |
|---|---|---|---|---|
| **SRE** | SLI/SLO/error budget | Error budget policy | High (toil reduction) | Large tech companies |
| Traditional Ops | Uptime (binary) | Conflict | Low | Small stable systems |
| DevOps | Deployment frequency | Cultural unity | Medium | Developer-led orgs |
| ITIL/ITSM | Change success rate | Process gates | Low | Enterprise/regulated |
| Platform Engineering | Developer experience | Self-service | High | Scale-up orgs |

**How to choose:** SRE is appropriate when reliability
failures have significant user or business impact and when
the team has the engineering capacity to instrument,
measure, and automate. DevOps is a good starting point
for smaller teams. Traditional ops is appropriate only
for very simple, low-criticality systems.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| SRE is just a job title for DevOps engineers | SRE is a specific engineering discipline with defined practices (SLIs, SLOs, error budgets, toil). Calling an ops engineer an "SRE" without these practices changes nothing. |
| 100% availability is the goal | 100% availability is unachievable and unnecessary. The right SLO is the minimum level that keeps users happy. Chasing 100% wastes resources and freezes feature development. |
| SRE replaces the development team | SRE is responsible for reliability; development is responsible for features. SREs are embedded with development teams but do not own the application code. |
| Error budgets make reliability worse | Error budgets make the reliability/velocity trade-off explicit and data-driven. Teams without error budgets make the same trade-off implicitly and politically. |
| Post-mortems assign blame | Blameless post-mortems focus on system conditions, not individual actions. The same human error in a well-designed system has no impact; in a poorly-designed system it causes an outage. The system, not the human, is to blame. |
| SRE only applies to web services | Any system with measurable reliability - databases, data pipelines, ML models, CI/CD systems - can benefit from SRE practices. |

---

### 🚨 Failure Modes & Diagnosis

**SLO set without baseline measurement**

**Symptom:**
SLO of 99.9% was set 6 months ago. The error budget
is always consumed in the first week of the month. Every
month ends with a deployment freeze and conflict between
SRE and development.

**Root Cause:**
The SLO was set aspirationally, not based on what the
system can currently achieve. Current performance is at
99.5%. Setting 99.9% as an SLO before investing in
reliability improvements creates a permanently negative
error budget.

**Diagnostic Command:**
```bash
# Measure actual reliability over the last 30 days
# to determine if the SLO is achievable
curl -sg "localhost:9090/api/v1/query_range?\
query=sum(rate(checkout_requests_total{status='2xx'}[5m]))\
/sum(rate(checkout_requests_total[5m]))&\
start=$(date -d '30 days ago' +%s)&\
end=$(date +%s)&step=3600" \
  | jq '.data.result[0].values | map(.[1] | tonumber)
    | add / length'
```

**Fix:**
Set the initial SLO based on the measured P50 reliability
over the last 30 days. Then progressively raise the SLO
as reliability improvements are made.

**Prevention:**
Never set an SLO without first measuring the current SLI
for at least 30 days. An SLO must be achievable on day 1.

---

**Toil exceeds 50% of SRE team capacity**

**Symptom:**
SRE team is exhausted. Every sprint is dominated by
manual incident response, manual deployments, and manual
capacity adjustments. No engineering improvement work
is being completed. Attrition in the SRE team increases.

**Root Cause:**
Toil (repetitive, manual, automatable work) has been
allowed to accumulate without systematic elimination.
The team is in a reactive mode: fixing incidents faster
than automating them.

**Diagnostic Command:**
```bash
# Track toil percentage using time recording
# Week 1: team members log all activities as:
# - toil (manual, repetitive) or
# - project (engineering improvement)
# Calculate: toil_hours / total_hours
# Target: < 50% toil. Alert if > 50%

# Minimum: count pager duty pages per week
# and identify which are automatable
pd incidents list --since 30d --status resolved \
  | jq '[.[] | select(.manually_resolved == true)] | length'
```

**Fix:**
Dedicate at minimum one sprint per quarter to toil
elimination. Target the highest-frequency manual tasks
first. Build automated runbooks for the top 5 most
common incident types.

**Prevention:**
Track toil as a first-class metric. Report toil percentage
in every sprint retrospective. Treat toil > 50% as a
team health emergency.

---

**Post-mortem culture replaced by blame culture**

**Symptom:**
Engineers hesitate to raise incidents for fear of blame.
Post-mortems focus on "who made the mistake" rather than
"what system conditions allowed this". High-severity
incidents are under-reported. Experienced engineers leave.

**Root Cause:**
Leadership is using post-mortems as performance review
input. Individuals are called out in incident reports
by name with negative connotation. The blameless principle
is stated but not practiced.

**Diagnostic Command:**
```bash
# Audit post-mortem language for blame patterns
# (assumes post-mortems stored as markdown files)
grep -rE "mistake|fault|negligence|should have|failed to" \
  post-mortems/ | wc -l
# Non-zero result suggests blame language is present
```

**Fix:**
Review all post-mortem templates and remove fields that
invite blame (e.g., "which engineer caused the incident?").
Replace with system-focused fields: "what system conditions
allowed this human action to cause an outage?"

**Prevention:**
SRE leadership must actively model blameless behaviour.
When a post-mortem draft contains blame language, return
it for revision. Celebrate engineers who file post-mortems,
not penalise them.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What Is Observability and Why It Matters` - SRE uses
  observability as its primary tool for measuring and
  diagnosing reliability

**Builds On This (learn these next):**
- `SLI (Service Level Indicator)` - the metric that SRE
  uses to measure reliability
- `SLO (Service Level Objective)` - the reliability target
  that defines the error budget
- `SLA (Service Level Agreement)` - the contractual promise
  to users derived from SLOs
- `Error Budget` - the actionable consequence of SLO
  measurement
- `Alerting Fundamentals` - SRE uses SLO burn rate alerts
  as the primary alerting mechanism

**Alternatives / Comparisons:**
- `Toil Reduction Strategy` - the SRE practice of automating
  repetitive manual work
- `Post-Mortem and Blameless Culture` - the SRE incident
  learning practice in detail

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Software engineering applied to ops:      │
│              │ reliability as a measurable feature       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Ops/dev conflict, heroic operations,      │
│ SOLVES       │ unmeasurable reliability, no improvement  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Error budget makes reliability vs         │
│              │ velocity a data problem, not a political  │
│              │ one - shared by dev and ops               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Running services where reliability        │
│              │ failures have significant user/business   │
│              │ impact and engineering investment is      │
│              │ available                                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Teams too small for dedicated SRE role    │
│              │ or for non-critical batch systems         │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Calling ops engineers "SREs" without      │
│              │ implementing SLIs, SLOs, error budgets,   │
│              │ or blameless post-mortems                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Engineering investment in reliability     │
│              │ vs feature velocity (explicit via budget) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "100% reliability is wrong. The right     │
│              │  SLO is the minimum that keeps users      │
│              │  happy."                                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SLI → SLO → Error Budget → Post-Mortems  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Reliability is not "up or down" - it is a measurable
   property (SLI) with a target (SLO) and a budget (error
   budget) that balances reliability investment against
   feature velocity.
2. The error budget makes the ops/dev conflict a data
   problem: budget remaining means ship features; budget
   exhausted means fix reliability first.
3. Blameless post-mortems treat incidents as system failures,
   not individual failures - this is the cultural foundation
   that allows honest reporting and systematic improvement.

**Interview one-liner:**
"SRE applies software engineering principles to operations:
define reliability with SLIs, set targets with SLOs, manage
the reliability/velocity trade-off with error budgets, and
learn from failures through blameless post-mortems. The key
insight is that reliability is a feature to be engineered,
not a condition to be hoped for."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Make trade-offs explicit and data-driven rather than implicit
and political. The error budget converts the reliability vs
velocity tension from a negotiation between teams into a
shared, measurable constraint. This principle applies to
any resource-constrained trade-off: technical debt budget,
testing coverage target, security review SLA.

**Where else this pattern appears:**
- **Technical debt management** - defining a "technical debt
  budget" (X% of sprint velocity) and enforcing it with the
  same rigour as an error budget converts the invisible
  "we should pay down debt" into an explicit constraint.
- **Security engineering** - defining a vulnerability SLO
  (P1 vulnerabilities remediated within 24 hours, P2 within
  7 days) converts security work from reactive heroics to
  a measured, improvable process.
- **Manufacturing quality** - Six Sigma defines acceptable
  defect rates (SLOs), measures actual defect rates (SLIs),
  and invests in process improvement proportional to the
  gap. Same framework, different domain.

**Industry applications:**
- **Financial services** - SRE practices are mandatory for
  payment systems where downtime has direct regulatory and
  financial consequences. SLOs for settlement systems are
  defined contractually with counterparties.
- **Healthcare IT** - SRE provides the measurement framework
  to demonstrate reliability to regulators. An EHR system
  with a measured 99.95% uptime SLO is demonstrably more
  reliable than one with "highly available" documentation.

---

### 💡 The Surprising Truth

The most counterintuitive SRE principle is that 100%
reliability is the wrong goal and that having an error
budget - a defined allowance for failures - actually
improves reliability over time. Here is why: organisations
that target 100% availability become so afraid of
deployments that they stop shipping. When they do ship,
after months of accumulation, they ship massive changes that
are impossible to debug when they fail. Organisations with
error budgets ship small, frequent changes. They discover
failures early, fix them cheaply, and maintain the
engineering discipline to improve continuously. The
reliability of a system that never ships is not being
measured - it is decaying.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **[EXPLAIN]** Explain the error budget concept to a product
   manager who has never heard of SRE, and explain how it
   affects their team's deployment schedule for the next
   sprint.
2. **[DEBUG]** Given a Prometheus query showing that a
   service's SLO burn rate is 3x the sustainable rate,
   calculate how many days of error budget remain and
   recommend whether to trigger a deployment freeze.
3. **[DECIDE]** For a payment processing service, set an
   appropriate SLO (not aspirational, not under-committed),
   explain how you derived the number, and define the error
   budget policy for what happens when 50% of the budget
   is consumed.
4. **[BUILD]** Write a Prometheus alert rule that fires a
   page when a service's error budget is burning at more
   than 5x the sustainable rate over a 1-hour window.
5. **[EXTEND]** Apply SRE principles to a data pipeline:
   define the SLI, set an SLO, calculate the error budget,
   and describe what a blameless post-mortem would look like
   for a pipeline that produced incorrect output data.

---

### 🧠 Think About This Before We Continue

**Q1.** Your payment service has an SLO of 99.9% success rate
with a monthly error budget of 43.2 minutes. On day 5 of the
month, an incident consumed 38 minutes of budget. Your
development team wants to deploy a major feature on day 7.
The SRE team wants to freeze deployments. The deployment
contains a critical security patch. How does SRE error budget
policy handle this situation? What override mechanisms exist,
and what are the risks of overriding vs not overriding?
*Hint: Think about what the error budget policy document
should specify about security patches vs feature deployments.
Is the error budget a hard stop or a decision framework?*

**Q2.** You are asked to set the SLO for a new service before
it launches to production. You have no historical performance
data. Describe the process you would use to determine the
right initial SLO, the instrumentation you would need before
launch, and how you would adjust the SLO over the first
three months of operation.
*Hint: Consider user expectations (what does a user notice?
A 500ms slowdown? A 2-second slowdown?), competitive
benchmarks, and the cost of reliability at different levels
(99% vs 99.9% vs 99.99% have very different infrastructure
and engineering costs).*

**Q3.** Design a blameless post-mortem for this scenario:
An engineer deleted the production database instead of the
staging database during routine maintenance. The deletion
was irreversible and caused 4 hours of downtime. The
engineer had done this procedure 20 times before with no
incident. Write the post-mortem timeline, contributing
factors, and at least three system-level (not human-level)
action items that would prevent recurrence.
*Hint: Blameless means the action items must not be "the
engineer should be more careful." They must identify what
system design, tooling, process, or environment made it
possible for a routine procedure to cause an irreversible
production outage.*

---

### 🎯 Interview Deep-Dive

**Q1: "Explain the relationship between SLIs, SLOs, and
error budgets. How do they work together in practice?"**
*Why they ask:* Tests whether the candidate understands
SRE's core measurement framework, not just the terminology.
*Strong answer includes:*
- SLI is the metric (checkout success rate, measured in real
  time from production signals)
- SLO is the target (99.9% success rate over 30 days)
- Error budget = (1 - SLO target) x time window = 43.2
  minutes of allowed downtime per month
- In practice: SLI is measured continuously by Prometheus;
  burn rate alerts fire when the budget is consumed too fast;
  when budget is low, development freezes deployments and
  SRE invests in reliability improvements

**Q2: "How would you set an SLO for a service that has never
had one before? Walk me through the process."**
*Why they ask:* Tests practical SRE experience - candidates
who have actually set SLOs know this is hard and involves
measurement, user research, and iteration.
*Strong answer includes:*
- First: measure current SLI for 30 days minimum - without
  baseline data, any SLO is aspirational fiction
- Second: identify what users notice - 500ms p99 latency
  increase vs 2-second increase have very different user
  visibility thresholds
- Third: set the initial SLO slightly below current
  performance (not aspirational, not under-committed)
- Fourth: review after 3 months - if the error budget is
  never touched, the SLO is too loose; if it is always
  exhausted, it is too tight
- Key: SLOs should be the minimum reliability that keeps
  users satisfied, not the highest achievable level

**Q3: "A deployment caused an outage that consumed 80% of
the monthly error budget in 2 hours. The post-mortem finds
that a configuration change was deployed without a rollback
plan. What action items do you write, and why are they
system-level, not human-level?"**
*Why they ask:* Tests understanding of blameless culture
and whether the candidate can distinguish between human
errors and system conditions.
*Strong answer includes:*
- BAD action item: "Engineer must check rollback plan before
  deploying" - this is human-level and will not prevent
  recurrence
- GOOD action items: (1) CI pipeline must require rollback
  plan documentation before a production deploy is allowed
  (system enforces it), (2) deployment tooling must support
  one-click rollback for all configuration changes (system
  enables recovery), (3) add automated canary deployment
  for configuration changes that checks SLI before
  proceeding to full rollout (system detects the problem
  before it causes an outage)
- The key: action items must make it impossible or much
  harder for the same failure to occur, regardless of which
  human performs the procedure next time
