---
id: OBS-026
title: Runbooks and Playbooks
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-005, OBS-009, OBS-025
used_by: OBS-037, OBS-043, OBS-056
related: OBS-036, OBS-040, OBS-022
tags:
  - observability
  - reliability
  - devops
  - intermediate
  - pattern
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 26
permalink: /obs/runbooks-and-playbooks/
---

# OBS-026 - Runbooks and Playbooks

⚡ TL;DR - A runbook is a pre-written decision tree for a
specific known failure; a playbook is the broader guide for
a class of incidents - together they convert expert knowledge
into executable on-call documentation that works at 3 AM.

| #026 | Category: Observability & SRE | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SRE, Alerting Fundamentals, Incident Management Process | |
| **Used by:** | Toil Reduction Strategy, Observability-Driven Development, Production On-Call Runbook Design | |
| **Related:** | Post-Mortem and Blameless Culture, SRE Book Core Principles, Health Check Patterns | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A new on-call engineer gets paged at 2 AM: "High error rate on
payment-api." They log in. They see logs full of "connection
refused to postgres." They do not know the connection pool size.
They do not know if this has happened before. They do not know
the rollback procedure. They Slack the lead engineer who is
asleep. Thirty minutes later, the lead engineer wakes up, joins,
and resolves it in 3 minutes - because they have seen this exact
failure before and know exactly what to do. The 3-minute fix
took 33 minutes because all that knowledge was in one person's
head.

**THE BREAKING POINT:**
Institutional knowledge that exists only in the minds of senior
engineers is a single point of failure. It does not scale.
It burns out senior engineers who are paged for things that
could be fixed by anyone with the right documentation.

**THE INVENTION MOMENT:**
This is exactly why runbooks were created - to externalise
tacit expert knowledge into executable documentation that any
engineer can follow under pressure, without requiring expert
judgment for known failure modes.

**EVOLUTION:**
Early operations runbooks were physical binders - literally
"books" kept in the operations control room. Data center
operations teams maintained these for mainframe management
in the 1970s-1990s. Modern SRE practice moved runbooks to
wikis, then to code-adjacent documentation. The current
generation of runbooks are executable: automated runbooks
trigger directly from alerts, execute diagnostic steps, and
even apply remediations programmatically using tools like
AWS Systems Manager Run Command, Ansible, or PagerDuty
Process Automation.

---

### 📘 Textbook Definition

A **runbook** is a set of standardized procedures documenting
the steps required to detect, diagnose, and resolve a specific
known operational issue or perform a routine operational task.
A **playbook** is a broader operational guide that covers a
class of incidents or scenarios, typically containing multiple
runbooks or decision trees. In modern SRE practice, runbooks
are attached directly to monitoring alerts so that the engineer
who receives the alert immediately has access to the diagnostic
and remediation steps for that specific alert condition.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A runbook is the manual for a specific failure, written by
whoever fixed it last so the next person can fix it faster.

**One analogy:**
> A runbook is like the maintenance manual in a cockpit.
> When a warning light activates, the pilot does not figure
> out the solution from first principles - they open the
> quick reference card for that specific warning light,
> follow the checklist, and land safely. The knowledge of
> every engineer who ever debugged that issue is encoded
> in the checklist. Expertise is accessible even when
> the expert is not in the cockpit.

**One insight:**
The most important thing to understand about runbooks is that
a runbook is not documentation for documentation's sake - it
is a cognitive offload mechanism for high-stress situations.
Under stress, human working memory degrades. A well-structured
runbook with yes/no decision branches requires almost no
working memory to follow, freeing the engineer's cognitive
resources for the novel aspects of the incident that the
runbook does not cover.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Tacit expert knowledge that is not externalized is a
   single point of failure for operational resilience
2. Under stress (2 AM, production down, users affected),
   cognitive load must be minimized for the engineer to
   perform effectively
3. Known failure modes repeat - every repeated incident
   handled without a runbook is wasted recovery time
4. A runbook that is stale is worse than no runbook - it
   creates false confidence and leads engineers down wrong
   paths

**DERIVED DESIGN:**
These invariants lead to three runbook design principles:
- **Alert-attached**: runbooks must be linked directly to
  the alert that triggers them; a runbook nobody can find
  is useless at 3 AM
- **Decision-tree structured**: each step should have a
  yes/no branch; "if this, then that" eliminates ambiguity
- **Executable**: runbook steps should be copy-pasteable
  commands, not descriptions of what commands to research

**THE TRADE-OFFS:**
**Gain:** Lower MTTR for known failures, reduced senior
engineer interrupt burden, faster on-boarding of new on-call
engineers, institutional knowledge preservation.
**Cost:** Runbooks require maintenance - a stale runbook
is actively harmful. Writing good runbooks takes time and
expertise. Runbooks cannot cover truly novel incidents.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Externalizing knowledge requires capturing
both the what (commands to run) and the why (what this tells
you) - you cannot simplify away the diagnostic context.
**Accidental:** Lengthy prose documentation that requires
reading paragraphs before finding the command, and runbooks
stored in a separate wiki requiring authentication steps
before access.

---

### 🧪 Thought Experiment

**SETUP:**
Your team has two runbooks. Runbook A covers connection pool
exhaustion and was written 6 months ago - but the connection
pool was migrated from HikariCP to PgBouncer 3 months ago.
Runbook B covers database failover and was written last week
by the engineer who just completed the PgBouncer migration.
A connection pool exhaustion incident fires at 2 AM.

**WHAT HAPPENS WITH STALE RUNBOOK A:**
The on-call engineer opens the runbook. Step 3: "Check
HikariCP metrics at /actuator/metrics/hikaricp.connections."
The endpoint returns 404. The engineer spends 15 minutes
figuring out why the endpoint is missing. They conclude
the runbook is wrong. They abandon the runbook and start
investigating from scratch. Total time to resolution: 45 min.

**WHAT HAPPENS WITH FRESH RUNBOOK B:**
The on-call engineer opens the runbook. Step 1: Check
PgBouncer admin console for active vs idle connections. The
command is copy-pasteable. Step 3: If pool_mode is session
and client_wait_time > 30s, execute the restart command
(also copy-pasteable). Resolution: 8 minutes.

**THE INSIGHT:**
A stale runbook that confidently gives wrong instructions
is more dangerous than no runbook, because it costs the
engineer the 15 minutes of discovering it is wrong before
they can start real investigation. Runbook freshness is
a reliability property, not a documentation quality property.

---

### 🧠 Mental Model / Analogy

> A runbook library is like a chef's recipe collection.
> A master chef can improvise anything from ingredients;
> but having a trusted recipe for the most common dishes
> means line cooks can execute without the chef's oversight.
> The recipe encodes the chef's expertise in a form that
> is reproducible, consistent, and scalable across the
> kitchen team. The chef still needs to be called for truly
> novel situations - but routine "dishes" should not require
> the chef.

Element mapping:
- "Master chef" → senior SRE or lead engineer
- "Line cooks" → on-call engineers including new joiners
- "Recipe" → runbook for a specific known failure mode
- "Recipe collection" → runbook library attached to alerts
- "Novel dish" → new/unknown incident type requiring expert
- "Restaurant running without chef" → 24/7 on-call coverage

Where this analogy breaks down: a recipe produces a fixed
output from fixed inputs; a runbook ends at "incident
resolved" which may require judgment calls if the failure
pattern deviates from the documented scenario.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A runbook is a step-by-step guide for fixing a specific
problem. When something breaks, instead of having to figure
it out from scratch, you open the runbook for that problem
and follow the steps. It is like a repair manual for your
software system.

**Level 2 - How to use it (junior developer):**
When on-call, every alert should have a linked runbook.
Open the runbook immediately when an alert fires - before
doing anything else. Follow each step in order. If a step
does not work as documented, note it and continue to the
next step. After the incident, update the runbook if you
found a step was wrong or missing.

**Level 3 - How it works (mid-level engineer):**
A high-quality runbook has five components: (1) Alert trigger
- which exact alert links here, (2) Symptoms - what the user
is seeing, (3) Diagnostic commands - copy-pasteable commands
to determine severity and scope, (4) Decision tree - "if
command output shows X, do step 4a; if it shows Y, do step
4b", (5) Remediation steps - the actual fix with rollback
option. The runbook is linked directly from the PagerDuty
or alerting platform alert, requiring zero navigation to find.

**Level 4 - Why it was designed this way (senior/staff):**
The decision-tree format was deliberately chosen over prose
because prose requires sequential reading under stress -
a decision tree can be entered at any point and provides
a direct path without reading the context sections. The
"alert-attached" requirement emerged from studying MTTD
patterns: engineers who had to search for the runbook took
3-7 minutes longer than engineers who clicked a link from
the alert. The "copy-pasteable commands" rule emerged from
observing errors introduced when engineers retyped commands
from prose descriptions - fat-finger errors under stress
caused secondary incidents.

**Level 5 - Mastery (distinguished engineer):**
At scale, runbooks become the foundation for toil elimination.
When the same runbook is executed more than 3 times per
quarter without modification, that runbook is a candidate for
automation. The runbook becomes the specification for the
automated remediation. Engineering organizations that
systematically convert runbooks to automated remediations
reduce on-call interrupt burden by 40-60%. The runbook
library also becomes a technical debt indicator: a runbook
that describes workarounds for a known architectural flaw
is documentation of technical debt, not just operational
documentation. Tracking which runbooks are executed most
frequently guides the engineering backlog prioritization.

---

### ⚙️ How It Works in Practice

**RUNBOOK STRUCTURE (standard template):**

```
┌─────────────────────────────────────────────────┐
│  RUNBOOK: [Alert Name] - [Service Name]         │
│  Last updated: [date] | Owner: [team]           │
├─────────────────────────────────────────────────┤
│  ALERT TRIGGER                                  │
│  Alert: payment-api high error rate             │
│  Threshold: error_rate > 5% for 5 min          │
│  Link: [PagerDuty alert URL]                    │
├─────────────────────────────────────────────────┤
│  SYMPTOM CHECK (what users are seeing)          │
│  - Checkout failures                            │
│  - Payment timeout errors                       │
├─────────────────────────────────────────────────┤
│  DIAGNOSTIC STEPS                               │
│  Step 1: Check error type distribution          │
│  kubectl exec payment-api-xxx -- \              │
│    curl localhost:8080/actuator/metrics/        │
│    http.server.requests?tag=status:500          │
│                                                 │
│  Step 2: Check DB connection status             │
│  kubectl exec payment-api-xxx -- \              │
│    psql $DB_URL -c                              │
│    "SELECT count(*) FROM pg_stat_activity       │
│     WHERE state='active';"                      │
├─────────────────────────────────────────────────┤
│  DECISION TREE                                  │
│  Connection count > 90? → Go to Step 3a        │
│  Error type = "timeout"? → Go to Step 3b       │
│  Error type = "503"? → Go to Step 3c           │
├─────────────────────────────────────────────────┤
│  REMEDIATION                                    │
│  3a: Connection pool exhaustion                 │
│    kubectl rollout restart deploy/payment-api  │
│    Monitor: error rate should drop in 2 min    │
│    Escalate if not resolved in 5 min           │
├─────────────────────────────────────────────────┤
│  ESCALATION                                     │
│  If not resolved in 15 min: page @db-team      │
│  If data loss risk: page @incident-commander   │
└─────────────────────────────────────────────────┘
```

**PLAYBOOK vs RUNBOOK DISTINCTION:**

```
PLAYBOOK (class of incidents)
├── "Database Incidents Playbook"
│     ├── Runbook: Connection pool exhaustion
│     ├── Runbook: Replication lag > 30s
│     ├── Runbook: Deadlock storm
│     └── Runbook: Disk space critical
│
RUNBOOK (specific known failure)
└── "Connection pool exhaustion"
      ├── Trigger: pg_stat_activity.active > 90
      ├── Diagnostic: 3 specific commands
      └── Remediation: 2 specific options
```

---

### 🔄 How It Flows in an Organization

**RUNBOOK LIFECYCLE:**

```
Incident occurs →
  No runbook exists →
    Senior engineer resolves it →
      Postmortem identifies it as a candidate →
        Senior engineer writes runbook →
          Runbook linked to alert in PagerDuty →
            Next occurrence: junior resolves in 10 min
                           (vs 45 min previously)

OR

Runbook exists →
  Engineer follows runbook →
    Runbook step is stale (wrong) →
      Engineer notes it, continues investigation →
        Postmortem includes "update runbook step 3" →
          Updated runbook deployed
```

**WHERE IT BREAKS DOWN:**
The most common failure is runbooks written at incident
resolution time and never updated. A runbook written during
an adrenaline-fueled postmortem at 4 AM will have gaps.
Runbooks should be reviewed in a calm postmortem, not
written in the heat of the incident. The second failure
is the "runbook dump" - a wiki folder with 200 runbooks
that are not linked to alerts, have no owners, and have
not been updated in 2 years. A runbook that requires a
wiki search to find provides near-zero value at 3 AM.

**HEALTHY vs DEGRADED:**
Healthy: Every alert has a linked runbook that is updated
whenever the alert fires. Runbooks are executable, not
descriptive. New engineers can handle SEV3 incidents solo
in their first month.
Degraded: Runbooks exist in theory but engineers routinely
skip them ("easier to ask someone"). Stale runbooks are
found during incidents. Senior engineers are still paged
for known failures.

---

### 💻 Code Example

**Example 1 - BAD: Prose runbook that requires reading**

```markdown
# BAD Runbook: Database Issues

If there are database issues, the engineer should first
investigate the database connection health. This can be
done by examining the Prometheus metrics for connection
pool utilization. If the pool utilization is high, this
may indicate that the application is not releasing
connections properly, or that the pool size is too small
for the current load. In that case, consider restarting
the application pods or adjusting the pool size.
```
This requires 3 minutes of reading under stress to extract
one command. The command is not even present.

**Example 2 - GOOD: Decision-tree runbook with commands**

```markdown
# GOOD Runbook: payment-api-high-error-rate

**Alert**: payment-api error rate > 5% for 5 min
**Updated**: 2024-11-15 | **Owner**: payments-team

## STEP 1: Get error breakdown (30 seconds)
Copy-paste this command:
kubectl exec -n production \
  $(kubectl get pod -n production -l app=payment-api \
  -o jsonpath='{.items[0].metadata.name}') -- \
  curl -s localhost:8080/actuator/metrics/\
http.server.requests | jq '.measurements'

Is error type "ConnectException"? → Go to Step 2a
Is error type "ReadTimeoutException"? → Go to Step 2b
Is error type "5xx from downstream"? → Go to Step 2c

## STEP 2a: Database connection issue
Check active connections:
psql $PAYMENT_DB_URL -c \
  "SELECT count(*), state FROM pg_stat_activity \
   GROUP BY state;"

Active connections > 80? → Execute Step 3a
Active connections < 80? → Execute Step 3b
```

**Example 3 - Automated runbook (PagerDuty + AWS SSM)**

```yaml
# PagerDuty automation action linked to alert
# Automatically runs on SEV3 alerts before paging engineer
name: "Restart payment-api pods"
trigger_condition: "error_rate > 5% AND error_type = ConnectException"
steps:
  - action: aws_ssm_run_command
    target: ecs-cluster/payment-api
    command: "kubectl rollout restart deploy/payment-api -n production"
  - wait: 120s
  - action: check_metric
    metric: "payment_api.error_rate"
    condition: "< 1%"
    on_success: "resolve_alert"
    on_failure: "escalate_to_human"
```

**How to test / verify correctness:**
Run "game days" - scheduled exercises where engineers follow
runbooks on non-production environments to verify each step
works. After every incident where a runbook was used, review
each step: did it work as documented? Did any step take longer
than 2 minutes to find the result? Update immediately.

---

### ⚖️ Comparison Table

| Approach | Creation Time | Maintenance | On-call Effectiveness | Best For |
|---|---|---|---|---|
| **Decision-tree runbook** | 1-2h to write | Medium (update after each incident) | High | Known, repeating failures |
| Prose wiki documentation | 30m to write | Low (rarely updated) | Low | Reference only, not on-call use |
| Automated runbook | 4-8h to build | High (code maintenance) | Very high | High-frequency, well-understood failures |
| No runbook | None | None | Very low | Solo projects only |
| AI-assisted runbook | 1h to generate | Medium | Medium-High | Early-stage teams |

**How to choose:**
Start with decision-tree runbooks for all SEV1/2 alert types.
Convert to automated runbooks for any runbook executed more
than once a week. Use prose documentation only for background
context, not for on-call procedures.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A good runbook covers every possible scenario | Runbooks cover KNOWN scenarios; they explicitly call for escalation when the situation deviates from the documented pattern |
| Runbooks reduce the need for experienced engineers | Runbooks handle the 80% of known failures; novel incidents still require expert judgment - runbooks free experts for novel work |
| Once written, a runbook is done | A runbook that is not updated after each use will become stale and dangerous; runbook maintenance is an ongoing commitment |
| Detailed prose runbooks are more helpful than short ones | Under stress, shorter is better; decision trees with copy-pasteable commands outperform detailed explanations every time |
| Runbooks can only be used by the team that wrote them | Cross-team runbook access is a reliability property; any on-call engineer should be able to use another team's runbook without prior knowledge |

---

### 🚨 Failure Modes & Diagnosis

**Stale Runbook Leading to Wrong Actions**

**Symptom:**
Engineer follows a runbook step that does not work (endpoint
returns 404, command is not found, metric has been renamed).
Time is wasted discovering the runbook is wrong before
real investigation begins. Engineer abandons the runbook.

**Root Cause:**
Runbook was written at incident time and never updated when
the system was refactored. No owner assigned to the runbook.
No runbook review process exists.

**Warning Signs:**
Runbook "Last Updated" date is more than 6 months old. No
owner is listed. Runbook steps reference deprecated tooling
or removed endpoints.

**Fix:**
Every runbook must have: Last Updated date, Owner team,
Review-by date. Add a "Report outdated step" link at the
top of every runbook. After each incident where a runbook
was used, the on-call engineer's first post-incident task
is to verify each step and update if needed.

**Prevention:**
Add runbook review to sprint planning quarterly. Automate
runbook health checks by scripting each diagnostic command
and verifying it returns expected output in staging.

---

**Runbook Burial (Unfindable at Alert Time)**

**Symptom:**
Engineers know runbooks exist but cannot find them quickly
during incidents. They fall back to asking senior engineers
instead. The runbook library is underutilized.

**Root Cause:**
Runbooks are stored in a wiki with no direct link from the
alert. Engineers must search, authenticate, and navigate
to find the relevant runbook under stress.

**Warning Signs:**
Ask "how long does it take to find the runbook for your
most recent alert?" Answer > 60 seconds = runbook burial.

**Fix:**
```yaml
# PagerDuty alert annotation (direct link to runbook)
annotations:
  runbook: "https://wiki.company.com/runbooks/payment-api-errors"
  severity: "SEV2"
  owner: "payments-team"
```
Every alert in PagerDuty/Opsgenie must have a `runbook`
annotation containing a direct URL to the runbook.

**Prevention:**
Make runbook linkage a required field in alert configuration.
Fail CI/CD if any alert definition is missing a runbook URL.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `SRE` - runbooks operationalize SRE practices into
  executable on-call documentation
- `Alerting Fundamentals` - alerts are the trigger that
  activates runbook usage
- `Incident Management Process` - runbooks support the
  response phase of incident management

**Builds On This (learn these next):**
- `Toil Reduction Strategy` - runbooks identify toil;
  automation converts runbooks into code
- `Production On-Call Runbook Design` - advanced patterns
  for runbook structure at enterprise scale
- `Observability-Driven Development Strategy` - design
  services with runbooks in mind from the start

**Alternatives / Comparisons:**
- `Post-Mortem and Blameless Culture` - postmortems generate
  runbook requirements; runbooks encode postmortem learnings
- `SRE Book - Core Principles Deep Dive` - the theoretical
  foundation that established runbooks as SRE practice
- `Health Check Patterns` - health check output is often
  the first diagnostic input for runbook decision trees

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Pre-written decision tree for a specific  │
│              │ known failure, linked directly to alert   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Tacit expert knowledge creates SPOF;      │
│ SOLVES       │ unknown engineers cannot fix known fails  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ A stale runbook is worse than no runbook  │
│              │ - it creates false confidence and wastes  │
│              │ time discovering it is wrong              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any alert that fires more than once;      │
│              │ any task performed by on-call engineers   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Novel incidents with no established       │
│              │ pattern - force expert judgment instead   │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Prose runbooks that require reading 3     │
│              │ paragraphs to find the first command      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reduced MTTD/MTTR vs ongoing maintenance  │
│              │ burden and staleness risk                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Encode expertise into checklist;         │
│              │ don't page the expert for known failures."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Toil Reduction → Automated Runbooks →    │
│              │ Production On-Call Runbook Design         │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Every alert must have a direct link to its runbook - not
   a wiki home page, not a folder link, a direct URL to the
   specific runbook for that specific alert.
2. A runbook must be updated within 24 hours of any incident
   where a step did not work as documented - staleness is
   the most dangerous runbook failure mode.
3. Short decision trees with copy-pasteable commands
   outperform detailed prose explanations under stress every
   single time.

**Interview one-liner:**
"A runbook is a decision tree with copy-pasteable commands
attached directly to a specific alert. It externalized the
expert's muscle memory so any on-call engineer can resolve
known failures without waking the expert. The discipline
of keeping runbooks current - updating them within 24 hours
of any incident where a step failed - is more important than
the initial quality of the runbook content."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Expert knowledge that is not externalized into reproducible
procedures is a single point of failure. Any system that
requires expert judgment for routine operations cannot scale
and creates unsustainable key-person dependency. This
principle applies to any domain where the same situation
recurs and the resolution requires specific knowledge.

**Where else this pattern appears:**
- **Aviation checklists** - every cockpit emergency procedure
  is a runbook; even master pilots use checklists because
  stress degrades recall under high cognitive load
- **Surgical protocols** - the WHO Surgical Safety Checklist
  reduced post-operative complications by 36% by converting
  expert knowledge into mandatory checklists for routine steps
- **Manufacturing SOPs (Standard Operating Procedures)** -
  assembly line procedures that encode process expertise
  so any trained operator can produce consistent quality

**Industry applications:**
- **Financial services trading desks** - market data feed
  failure runbooks are regulatory requirements; they must be
  tested quarterly and maintained to a documented standard
- **Healthcare IT** - EHR downtime runbooks specify manual
  workflows for each clinical process during system outages,
  required for HIPAA compliance and patient safety

---

### 💡 The Surprising Truth

Research from studying on-call engineering patterns shows
that engineers who write their own runbooks resolve subsequent
incidents from those runbooks 70% faster than engineers
following someone else's runbook - not because their runbook
is better written, but because the act of writing the runbook
encodes the diagnostic reasoning process into long-term memory.
This means runbook authorship itself is a training mechanism,
not just documentation production. Organizations that rotate
runbook authorship across the team (every engineer writes
runbooks for incidents they resolve) achieve faster incident
resolution across the entire team compared to organizations
where only senior engineers write runbooks.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Explain to a team manager why maintaining runbooks
   is an engineering task, not a documentation task, and quantify
   the MTTR cost of a 6-month-stale runbook in a specific
   incident scenario
2. [DEBUG] You are given a runbook that engineers consistently
   skip in favor of asking senior engineers. Diagnose the
   specific failure in the runbook's design that makes it
   unusable under on-call conditions
3. [DECIDE] You have a runbook that fires 3 times per week.
   Describe the threshold and criteria for deciding to
   automate this runbook, and what the automation architecture
   would look like
4. [BUILD] Write a complete runbook for a known failure in your
   current system - including alert trigger, diagnostic commands
   with expected output formats, a decision tree with at least
   3 branches, and remediation steps with rollback procedure
5. [EXTEND] Design a runbook governance system for a 15-team
   engineering organization - including ownership model,
   freshness requirements, review cadence, and the CI/CD
   validation that enforces alert-runbook linkage

---

### 🧠 Think About This Before We Continue

**Q1.** Your organization has 150 runbooks in a wiki. Usage
data shows that 80% of on-call incidents are resolved using
only 12 of those runbooks. The other 138 runbooks have not
been accessed in 12 months. What does this distribution tell
you about your system reliability and your on-call alert
design? What would you do with the 138 unused runbooks, and
what would you invest in for the 12 high-use runbooks?
*Hint: Think about the 80/20 principle applied to runbooks
and what "high-use runbook" means as a reliability signal.*

**Q2.** A junior engineer joins your on-call rotation after
2 weeks. At the end of their first month, they have
successfully resolved 8 incidents solo using runbooks.
They report that 3 of the runbooks had stale steps they had
to work around. At 10x scale - 100 engineers, 500 services,
daily on-call incidents - design the runbook freshness system
that ensures staleness is detected and corrected automatically
before it causes MTTR degradation.
*Hint: Think about how you could make the runbook validation
automated - not just dependent on engineers reporting stale
steps after an incident.*

**Q3.** Design an "automated runbook" for the following scenario:
a Kubernetes pod's memory usage exceeds 90% of its limit.
The automation should: diagnose the cause (memory leak vs
traffic spike vs configuration error), apply the appropriate
remediation (pod restart vs HPA scaling vs alert for human
review), and notify the on-call engineer with the action taken
and the diagnostic data that led to the decision. What tooling
would you use? What safety guardrails would prevent the
automation from making the situation worse?
*Hint: Consider what "safe to automate" means - what actions
can be taken without human approval and what requires
escalation.*

---

### 🎯 Interview Deep-Dive

**Q1: You join a team with no runbooks. How do you build a
runbook library from scratch in 90 days without disrupting
the team's delivery commitments?**
*Why they ask:* Tests ability to implement SRE practices
incrementally without becoming a blocker.
*Strong answer includes:*
- Start with the top 5 most frequent alerts - write runbooks
  for these first; 20% of the work, 80% of the value
- "Write it while you fix it": any engineer who resolves an
  incident without a runbook writes the runbook immediately
  after resolution (postmortem action item)
- Attach runbooks to alerts in PagerDuty within the first 2
  weeks; visibility is more important than completeness
- Define the runbook template and quality bar upfront; bad
  runbooks are worse than none

**Q2: How do you ensure runbooks stay current as the system
evolves?**
*Why they ask:* Tests understanding that runbook maintenance
is an ongoing operational discipline, not a one-time task.
*Strong answer includes:*
- Every runbook has a required "Last Updated" field and an
  Owner team; orphaned runbooks are archived, not deleted
- After every incident where a runbook was used, the resolver
  is required to review each step and mark it valid/invalid
- Quarterly "game day" exercise: run diagnostic commands from
  runbooks in staging to verify they still work
- CI/CD check: if a service component is changed (endpoint
  renamed, metric removed), scan runbooks for references
  and flag them for review

**Q3: What is the difference between a runbook and a playbook
and when would you use each?**
*Why they ask:* Tests precision in operational vocabulary and
understanding of when each document type is appropriate.
*Strong answer includes:*
- Runbook: specific, atomic, for one known failure mode -
  a decision tree with commands that can be executed in 15-30
  minutes to resolve a specific known issue
- Playbook: broader guide covering a class of incidents -
  contains multiple runbooks, escalation logic, and context
  for a domain (e.g., "Database Incidents Playbook")
- Use runbook when: the failure is specific and repeating;
  the resolution path is deterministic
- Use playbook when: multiple related failures need to be
  grouped; on-call engineers need context to choose between
  runbooks for an unfamiliar failure class

> Entry stub. Generate full content using Master Prompt v3.0.
