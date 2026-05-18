---
id: CTR-012
title: Containerization Necessity Assessment
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-001, CTR-047, CTR-056
used_by:
related: CTR-050, CTR-056
tags:
  - containers
  - architecture
  - mental-model
  - bestpractice
  - tradeoff
status: complete
version: 2
layout: default
parent: "Containers"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/ctr/containerization-necessity-assessment/
---

⚡ TL;DR - Containerization necessity assessment is the structured question "does containerising this specific workload create net value?" - evaluating the concrete gains against the concrete costs before committing to migration.

| Metadata        |                            |     |
| :-------------- | :------------------------- | :-- |
| **Depends on:** | CTR-001, CTR-047, CTR-056   |     |
| **Used by:**    |                            |     |
| **Related:**    | CTR-050, CTR-056           |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A platform engineering team declares "all services must be containerised
by Q4." Teams comply. A monolithic billing service is containerised.
The service runs fine in the container but now requires: a CI/CD pipeline
for images, a container registry, a Kubernetes deployment manifest, a
PersistentVolume for its local filesystem dependencies, and 3 months
of migration effort. The service's behaviour is identical before and
after. The containerisation created no user-visible value and added
permanent operational overhead.

**THE BREAKING POINT:**
The "containerise everything" mandate reaches a legacy COBOL batch
system that runs on a mainframe emulator, requires specific hardware
timing, and processes overnight payroll. The containerisation attempt
fails after 6 months. The original mandate never included a "should
we containerise?" question - only a "how do we containerise?" question.

**THE INVENTION MOMENT:**
Containerization necessity assessment separates the strategic question
("should we?") from the tactical question ("how do we?"). It prevents
containerisation from becoming a technology mandate that ignores workload
suitability.

**EVOLUTION:**
2015: Containers first adopted selectively for suitable workloads.
2017: Kubernetes maturity drives blanket adoption mandates. 2019:
Post-adoption retrospectives reveal that ~20% of containerised workloads
gained no net value from containerisation. 2021: Platform engineering
matures to include "golden path" selection (not every workload follows
the container path). 2023: FinOps analysis adds cost-benefit to
necessity assessment - some workloads cost more to run containerised
(managed services often cheaper for databases).

---

### 📘 Textbook Definition

**Containerization necessity assessment** is a structured evaluation
framework that determines whether a specific workload should be
containerised by explicitly weighing the concrete gains (portability,
density, deployment consistency, autoscaling) against the concrete
costs (migration effort, operational complexity, storage complexity,
team training). The assessment produces one of three outcomes: STRONG
FIT (containerise now), WEAK FIT (containerise with caveats), or
NOT RECOMMENDED (use alternative: managed service, VM, or bare metal).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Ask "what specific problem does containerising this workload solve?"
before containerising it.

**One analogy:**

> Containerization necessity assessment is like a home renovation
> proposal review. Before demolishing a perfectly functional kitchen
> to install an open-plan design, you ask: what problem are we solving?
> Who benefits? What is the cost? What is the disruption? If the answers
> are "we saw it on a design show, no one specifically, $80,000, and
> 3 months of living in chaos," you reconsider.

**One insight:**
The most important question in containerization necessity assessment
is not "can we containerise this?" but "what specific, measurable
problem does containerisation solve for this workload?" If the answer
is "it's the standard" or "everyone else is doing it," that is not a
problem statement - it is social pressure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Containerisation must solve a specific, identified problem** -
   "environment consistency," "faster deployments," "higher density,"
   or "easier rollback" are valid problems. "It's the standard" is not.
2. **Migration cost is non-zero** - every containerisation migration
   requires engineering time, CI/CD changes, and operational learning.
   The net value must exceed this cost.
3. **Not all workloads benefit equally** - stateless, multi-environment
   workloads benefit most. Stateful, hardware-specific, or single-
   environment workloads benefit least.
4. **Alternative paths have lower cost for some workloads** - a managed
   database service solves the operational complexity of running a database
   at lower total cost than containerising it, with less migration effort.

**DERIVED DESIGN:**
Given invariant 1: define the problem statement before beginning
assessment. Given invariant 4: include managed services as an alternative
in the assessment, not just VM vs. container.

**THE TRADE-OFFS:**

**Gain from assessment:** Prevents wasted migration effort on workloads
that gain no net value. Identifies the right alternative for unsuitable
workloads.

**Cost of assessment:** Time to conduct the assessment. This is always
less than the time wasted on an unnecessary migration.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Every technology decision requires a problem statement
and a value/cost analysis.

**Accidental:** Technology mandate without assessment. Social pressure
driving technical decisions.

---

### 🧪 Thought Experiment

**SETUP:**
Three workloads awaiting "containerisation" as per the platform mandate:
(A) A Node.js API service, deployed to 3 environments (dev/staging/prod)
(B) A self-hosted Elasticsearch cluster (stateful, 500GB data)
(C) A cron job that runs nightly reports (5 minutes duration, once per day)

**NECESSITY ASSESSMENT:**

Workload A (Node.js API):
- Problem solved: environment inconsistency, slow deployment, no autoscaling
- Gain: consistent image, faster CI, HPA autoscaling
- Cost: CI/CD pipeline (1 week), K8s manifest (2 days)
- Alternative: AWS Lambda? No - long-running service, Lambda cold start
- Verdict: STRONG FIT - containerise

Workload B (Elasticsearch):
- Problem solved: want to use K8s for everything
- Gain: K8s scheduling (minimal), portability (not needed - single env)
- Cost: Elasticsearch operator complexity, PV management, backup strategy
- Alternative: Amazon OpenSearch Service (managed, no ops overhead)
- Verdict: NOT RECOMMENDED - use managed service

Workload C (Cron Job):
- Problem solved: inconsistent execution environment
- Gain: consistent environment (same as VM cron)
- Cost: K8s CronJob + image + CI pipeline
- Alternative: AWS EventBridge + Lambda, or VM cron
- Verdict: WEAK FIT - K8s CronJob viable but Lambda may be simpler

**THE INSIGHT:**
The same platform mandate produces three different answers for three
workloads. Necessity assessment prevents blanket compliance with a
mandate that is right for A, wasteful for B, and debatable for C.

---

### 🧠 Mental Model / Analogy

> Containerization necessity assessment is like a building permit
> process. Before starting construction, you must answer: what are
> you building, why do you need it, and does the benefit justify the
> cost and disruption? The permit board does not approve construction
> just because "it's a building standard" - they approve it when there
> is a justified need and a viable plan.

Element mapping:

- **Building permit** = necessity assessment gate
- **Construction plans** = containerisation plan
- **Permit board** = platform team / architecture review
- **What are you building?** = workload characteristics
- **Why do you need it?** = problem statement
- **Cost and disruption** = migration effort and ops complexity

Where this analogy breaks down: a building permit is a regulatory
requirement; necessity assessment is a voluntary engineering discipline.
Without organisational commitment, teams bypass it under deadline pressure.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Containerization necessity assessment is asking "should we?" before
"how do we?" when deciding whether to put an application in a container.

**Level 2 - How to use it (junior developer):**
For each workload, answer three questions before containerising:
(1) What specific problem does containerisation solve for this workload?
(2) What is the estimated migration effort in engineer-days?
(3) Is there a simpler alternative (managed service, keep on VM)?
If question 1 has no specific answer, stop and reconsider.

**Level 3 - How it works (mid-level engineer):**
Apply a four-step assessment: (1) Problem statement - what does
containerisation specifically solve? (2) Gain quantification - which
container benefits apply (portability, density, consistency, autoscaling,
fast startup)? (3) Cost quantification - migration effort, operational
complexity, storage complexity, team training. (4) Alternative comparison -
managed service, VM, FaaS. The output is a recommendation with the
trade-off stated explicitly.

**Level 4 - Why it was designed this way (senior/staff):**
Containerization necessity assessment exists as a corrective to the
"technology mandate" problem. When a platform team mandates containers
for all workloads, teams optimise for compliance, not for value.
Assessment gates prevent compliance-driven containerisation of unsuitable
workloads. The framework forces a problem statement, which prevents
technology from becoming an end in itself. The inclusion of alternatives
(managed services) prevents false binary thinking (container or VM only).

**Expert Thinking Cues:**

- "What specific metric improves when this workload is containerised?
  Deployment frequency? MTTR? Resource utilisation? If no metric
  improves, the value is unclear."
- "What is the total cost of ownership comparison: containerised
  workload (image + registry + K8s + operator + on-call) vs. managed
  service (SLA + cost per unit)?"
- "Who is the primary beneficiary of containerisation? Developer DX?
  Ops team? The application's users? If no one benefits specifically,
  the value is unclear."

---

### ⚙️ How It Works (Mechanism)

**NECESSITY ASSESSMENT DECISION TREE:**

```
Step 1: Problem Statement
  "Containerising [workload] solves: ____________"
  If blank -> STOP. Reconsider or defer.

Step 2: Gains Apply?
  [ ] Environment consistency across 2+ envs?
  [ ] Autoscaling is needed?
  [ ] Fast startup (<5s) is needed?
  [ ] Higher density needed (many instances/host)?
  [ ] Faster deployment cycle needed?
  Any YES -> gains exist. Continue.
  All NO  -> WEAK FIT or NOT RECOMMENDED.

Step 3: Costs Acceptable?
  Migration effort:  _____ engineer-days
  Ops complexity:    LOW / MEDIUM / HIGH
  Storage complexity: LOW / MEDIUM / HIGH (stateful)
  Team training:     _____ engineer-days
  Total cost: _____
  If HIGH cost + LOW gains -> NOT RECOMMENDED.

Step 4: Alternative Comparison
  Managed service (RDS, OpenSearch) better?
  FaaS (Lambda, Cloud Run) better?
  Stay on VM (simpler, sufficient) better?
  If alternative is clearly better -> use alternative.

Output: STRONG FIT / WEAK FIT / NOT RECOMMENDED
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Platform mandate: "containerise workload X"
  |
  v
Step 1: Define problem statement
  |         ← YOU ARE HERE
  v
Step 2: Score gains (portability, density, etc.)
  |
  v
Step 3: Estimate costs (effort, ops complexity)
  |
  v
Step 4: Compare to alternatives
  |
  v
Recommendation: STRONG/WEAK/NOT RECOMMENDED
  |
  ├─ STRONG: proceed to CTR-050 migration strategy
  ├─ WEAK: proceed with documented caveats
  └─ NOT RECOMMENDED: document and escalate
```

**FAILURE PATH:**
Assessment skipped under deadline pressure. Workload containerised
on mandate. 6 months later: the team spends 20% of sprint capacity
on container-specific operational issues (PV management, image
vulnerability remediation) that add no user-visible value.

**WHAT CHANGES AT SCALE:**
At scale, individual assessments are replaced by workload type
classification: pre-approved patterns (stateless APIs: STRONG FIT
by default; OLTP databases: NOT RECOMMENDED by default; batch jobs:
evaluate individually). The classification document reduces per-
workload assessment time from hours to minutes.

---

### ⚖️ Comparison Table

| Workload Type | Typical Gains | Typical Costs | Default Verdict |
|---|---|---|---|
| Stateless API (multi-env) | High (portability, autoscale) | Low-Medium | STRONG FIT |
| Batch/cron job | Medium (consistency) | Low | WEAK FIT (K8s CronJob) |
| OLTP database | Low (portability minimal) | High (PV, backup, ops) | NOT RECOMMENDED |
| Message queue (self-hosted) | Low-Medium | High (operator, PV) | NOT RECOMMENDED (managed) |
| ML model serving | High (GPU scheduling, scale) | Medium | STRONG FIT |
| Legacy monolith (single env) | Low (no multi-env benefit) | High (refactor) | WEAK FIT at best |
| Real-time control system | None (<1ms jitter incompatible) | High | NOT RECOMMENDED |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Containerisation always improves developer experience" | Container DX is better for deployment consistency and reproducibility. But containers add cognitive load (Dockerfile, K8s YAML, registry management) that can worsen DX for teams not familiar with the toolchain. |
| "If we can containerise it, we should" | Technical feasibility is not the same as business necessity. A PostgreSQL database can be containerised; in most cases, a managed database service (RDS, Cloud SQL) is a better alternative with lower operational cost. |
| "Containerisation is free if we have Kubernetes already" | The platform cost is shared, but the per-workload migration effort (Dockerfile, CI/CD, K8s manifests, secrets management) is non-zero for every workload. |
| "Not containerising means we're behind" | Technology decisions should be made based on value delivered, not industry trend compliance. A well-operated VM running a legacy service that generates value is better than a poorly containerised service that generates operational debt. |
| "Necessity assessment slows down containerisation" | A 2-hour necessity assessment that prevents a 3-month failed migration effort is the fastest path. Assessment reduces total time spent; it only appears to slow down by adding a front-loaded step. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Cargo Cult Containerisation**
**Symptom:** A service is containerised because "the platform mandate
says so," but post-migration metrics show no improvement in deployment
frequency, MTTR, resource utilisation, or developer satisfaction.

**Root Cause:** No problem statement defined before migration. The
containerisation was driven by compliance with a mandate, not by a
specific engineering problem.

**Diagnostic:**

```bash
# Compare deployment metrics before and after
# (requires DORA metrics tracking)
# Key questions:
# - Did deployment frequency change? (git log --since=<pre-date>)
# - Did MTTR change? (incident log comparison)
# - Did resource utilisation change? (kubectl top pods vs. VM metrics)
# - Did on-call incidents change? (PagerDuty comparison)

# Check operational overhead added post-containerisation
# How many hours/week spent on container-specific ops?
# (image scanning, PVC management, pod restarts investigation)
```

**Fix:** Retrospective analysis: identify what value was expected and
what was delivered. Document as a lesson learned for future assessments.
If ongoing operational overhead exceeds benefit, consider reversing the
migration.

**Prevention:** Require a defined problem statement and measurable
success metrics before approving containerisation. Review metrics 90
days post-migration.

---

**Failure Mode 2: Managed Service Overlooked in Assessment**
**Symptom:** Team spends 3 months containerising a self-hosted Redis
cluster with Kubernetes Operator, PersistentVolumes, backup automation,
and cross-AZ replication. 6 months later, the platform team reviews
cost and finds ElastiCache Redis would have been 60% cheaper with zero
operational overhead.

**Root Cause:** The necessity assessment compared only "container vs.
VM" and did not include managed services as an alternative.

**Diagnostic:**

```bash
# Calculate true cost of self-hosted containerised Redis:
# - EC2 instance cost (3x for Redis cluster)
# - EBS volume cost (PersistentVolumes)
# - Platform team time (operator maintenance)
# - On-call time (Redis cluster incidents)
# - Developer time (backup/restore testing)

# Compare to managed service:
# - ElastiCache pricing: aws elasticache describe-cache-clusters
# - Total: instance cost only, no ops overhead
```

**Fix:** Document the cost delta as a lesson learned. Evaluate migration
to managed service. If migration cost < (ops overhead savings * 12 months),
migrate.

**Prevention:** Always include managed services in the necessity
assessment's alternative comparison step. For any stateful workload,
the first comparison should be "managed service vs. self-hosted container."

---

**Failure Mode 3: Assessment Bypassed Under Deadline**
**Symptom:** A team containerises a workload in 2 weeks to meet a
platform deadline, skipping the necessity assessment. The containerisation
introduces a previously unknown dependency on a host-level kernel module
that is not available in the container environment.

**Root Cause:** The assessment step was skipped. The pre-migration
dependency audit (part of necessity assessment) would have identified
the kernel module dependency.

**Diagnostic:**

```bash
# Identify kernel module dependencies
lsmod | grep <module_name>

# Check if module is available in container
kubectl exec <pod> -- lsmod 2>/dev/null | grep <module>
# If not available, the workload needs the host kernel module
# (requires privileged container or host module loading)
```

**Fix:** Add `privileged: true` temporarily (security risk) OR extract
the kernel-module-dependent component to a separate workload on a
dedicated host. Long-term: refactor to remove the kernel module dependency.

**Prevention:** Necessity assessment includes a pre-migration dependency
audit. Kernel module dependencies are a hard blocker for standard
containerisation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-001 - What Is Containerization and Why It Matters]] - container basics
- [[CTR-047 - Container Platform Strategy]] - platform selection context
- [[CTR-056 - Container Trade-off Framing]] - the trade-off framework this assessment uses

**Builds On This (learn these next):**

- [[CTR-050 - Containerization Migration Strategy]] - how to migrate after a positive assessment

**Alternatives / Comparisons:**

- [[CTR-050 - Containerization Migration Strategy]] - migration after positive assessment
- [[CTR-056 - Container Trade-off Framing]] - the theoretical framework behind assessment

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ "Should we containerise?" framework │
│ PROBLEM     │ Cargo cult containerisation         │
│ KEY INSIGHT │ Problem statement first, always     │
│ USE WHEN    │ Any workload containerisation decision│
│ AVOID WHEN  │ N/A - always ask "should we?" first │
│ TRADE-OFF   │ Assessment time vs. wasted migration│
│ ONE-LINER   │ What problem? What gain? What cost? │
│ NEXT EXPLORE│ CTR-050 Migration Strategy          │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Define the problem statement first: "containerising this workload
   solves X" - if X is blank, stop.
2. Always include managed services as an alternative - for stateful
   workloads, managed services often beat self-hosted containers.
3. Measure success 90 days post-migration against the original problem
   statement metrics - no measurement = no learning.

**Interview one-liner:**
"Containerization necessity assessment separates 'should we?' from
'how do we?' by requiring a specific problem statement, gain quantification,
cost estimation, and alternative comparison before any containerisation
migration begins."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Technology adoption decisions must be driven by specific problem
statements, not by industry trend or mandate compliance. "Everyone
is doing it" and "it's the standard" are social proof, not engineering
justification. The right question is always "what specific, measurable
problem does this technology solve for this specific workload?"

**Where else this pattern appears:**

- **Microservices adoption:** "Should we split this monolith into
  microservices?" requires the same assessment: what specific problem
  does it solve (deployment independence? team autonomy? scaling
  isolation?), and does the distributed systems overhead justify it?
- **GraphQL adoption:** "Should we replace our REST API with GraphQL?"
  requires: what over-fetching problem do clients have, what is the
  migration cost, and is a REST API with sparse fieldsets a simpler
  alternative?
- **Event sourcing adoption:** "Should we use event sourcing for this
  service?" requires: what audit trail, temporal query, or replay
  requirement justifies the operational complexity of an event store?

---

### 💡 The Surprising Truth

The 2023 CNCF Annual Survey found that 26% of respondents who had
containerised workloads reported that at least some of their containerised
workloads "should not have been containerised" in retrospect. The most
common reason: "the operational complexity added did not justify the
portability or consistency benefits." The second most common reason:
"a managed service would have been more cost-effective." These are
exactly the findings a necessity assessment would have surfaced before
migration. The survey data suggests that approximately 1 in 4 container
migrations globally could have been avoided or redirected to managed
services with a pre-migration assessment, saving millions of engineering-
hours industry-wide.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A team has a legacy Java EE monolith
(EJB-based, requires a full JEE application server). Two options:
(A) Containerise the monolith as-is (lift-and-shift, JBoss in a
container), or (B) Modernise to Spring Boot before containerising.
What does the necessity assessment reveal about option A, and what
are the hidden costs that make option A less attractive than it first
appears?
*Hint:* Consider: a containerised JBoss starts slower (30s+) than a
Spring Boot service (<5s). The image is larger (1GB+ vs. 200MB). The
portability gain is the same. The hidden cost of option A is carrying
forward EJB complexity into the container era. What is the long-term
cost of maintaining a containerised EJB monolith?

**Q2 (B - Scale):** A platform team must assess 150 workloads for
containerisation in a 3-month planning cycle. Individual necessity
assessments take 4 hours each. The total assessment time (600 engineer-
hours) exceeds the available capacity (160 hours across 2 architects).
How do you scale the assessment process without eliminating it?
*Hint:* Consider workload type classification (all stateless APIs: STRONG
FIT by default, no per-workload assessment required; all OLTP databases:
NOT RECOMMENDED by default). How many workload types cover 80% of the
portfolio? What is the residual that requires individual assessment?

**Q3 (A - System Interaction):** A containerised Node.js service uses
the host's `/var/run/secrets/corporate-ca.crt` file to trust a corporate
CA for internal TLS connections. On VMs, this file exists by default.
In containers, the file does not exist. The necessity assessment did
not identify this dependency. At what phase of the migration would this
dependency have been discoverable, and what is the proper container-
native way to provide CA certificates to container workloads?
*Hint:* The dependency audit in the necessity assessment is the right
phase. For the fix: Kubernetes ConfigMaps can inject CA certificates
as mounted files. How does the workload discover the certificate path?
Hardcoded path vs. environment variable configuration.