---
id: OBS-025
title: Incident Management Process
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-005, OBS-009, OBS-012
used_by: OBS-036, OBS-026, OBS-042
related: OBS-022, OBS-037, OBS-040
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
nav_order: 25
permalink: /obs/incident-management-process/
---

# OBS-025 - Incident Management Process

⚡ TL;DR - Incident management is the structured process for
detecting, responding to, resolving, and learning from production
failures - the difference between a 15-minute recovery and a
4-hour war room where everyone is guessing.

| #025            | Category: Observability & SRE                                                          | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | SRE, Alerting Fundamentals, SLO                                                        |                 |
| **Used by:**    | Post-Mortem and Blameless Culture, Runbooks and Playbooks, SLO-Based Alerting Strategy |                 |
| **Related:**    | Health Check Patterns, Toil Reduction Strategy, SRE Book Core Principles               |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
At 2 AM, an alert fires. Three engineers join a Slack channel.
One starts checking metrics. Another restarts a service "just
to see." A third contacts the database team. Nobody knows
who is in charge. Two engineers independently make conflicting
configuration changes. The DBA team joins and demands to know
who changed the replication config. The original engineer who
restarted the service forgot to document it. The incident
resolves 3 hours later - but nobody knows exactly what fixed
it, and the same failure happens again two weeks later.

**THE BREAKING POINT:**
Without a defined incident management process, failures become
improvised, chaotic, and slow to resolve. Duplicate efforts
waste time. Lack of ownership creates gaps. Missing documentation
means lessons are not learned. The same incident recurs.

**THE INVENTION MOMENT:**
This is exactly why incident management processes were created -
to provide a structured, repeatable framework that transforms
a chaotic emergency response into an efficient, coordinated,
learning operation.

**EVOLUTION:**
Early incident management borrowed from ITIL (Information
Technology Infrastructure Library), introduced in the late
1980s for enterprise IT service management. Google's SRE
book (2016) popularized the modern engineering-centric approach:
blameless postmortems, error budgets, and SLO-based severity
classification. PagerDuty, Opsgenie, and Incident.io
operationalized these practices into tooling. Modern incident
management now includes automated runbooks, AI-assisted
triage, and continuous improvement pipelines fed by
structured postmortem data.

---

### 📘 Textbook Definition

**Incident management** is the structured organizational
process for detecting, triaging, responding to, resolving, and
learning from unplanned service disruptions or degradations
that affect users or business operations. It defines clear
roles (incident commander, communications lead, responders),
communication protocols, escalation paths, severity levels,
and post-incident review processes. Effective incident
management minimizes Mean Time To Detect (MTTD), Mean Time
To Respond (MTTR), and recurrence rate by converting each
incident into documented learning.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Incident management turns a chaotic production crisis into a
structured, owned, documented recovery operation.

**One analogy:**

> Think of incident management like a hospital's emergency
> response protocol. When a patient arrives in cardiac arrest,
> there is no debate about who does what - the doctor leads,
> the nurse manages medication, the technician runs the ECG.
> Everyone knows their role because they practiced the protocol.
> Without that protocol, everyone would rush the patient and
> get in each other's way. The protocol does not slow the
> response - it makes it faster and more effective.

**One insight:**
The most important thing to understand is that incident
management is not about fixing the incident - it is about
coordinating the people who fix the incident. The technical
work is done by responders. The incident commander's job is
to remove coordination overhead so responders can move fast.
This role separation is what prevents the "too many cooks"
failure mode.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Under stress, human coordination degrades - explicit roles
   and protocols compensate for cognitive load
2. The highest-value action during an incident is reducing
   user impact (MTTR), not finding root cause (MTTR-RCA can
   happen after)
3. Every incident generates information that can prevent the
   next incident - this information must be captured
4. Blame destroys the psychological safety needed for honest
   post-incident analysis; blameless culture is not optional

**DERIVED DESIGN:**
These invariants lead to the canonical incident management
structure:

- **Incident Commander (IC)**: single decision-maker authority
  to prevent coordination chaos
- **Severity levels**: severity determines response speed,
  escalation, and communication frequency
- **Runbooks**: pre-written decision trees that offload
  cognitive load from responders during high-stress moments
- **Blameless postmortem**: structured learning that separates
  system failure analysis from individual blame

**THE TRADE-OFFS:**
**Gain:** Reduced MTTR, lower recurrence rate, organizational
learning from failures, reduced on-call burnout.
**Cost:** Process overhead, time investment in writing runbooks
and postmortems, cultural change required to implement
blameless culture effectively.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Incident response requires role coordination
and information capture - these are irreducibly complex for
any distributed system failure.
**Accidental:** Heavyweight ITIL processes, mandatory change
management boards, and multi-day approval workflows for
post-incident configuration changes are accidental complexity
that slows recovery and discourages honesty.

---

### 🧪 Thought Experiment

**SETUP:**
A payment service goes down on Black Friday. Revenue is losing
$50,000 per minute. Ten engineers are available. No incident
management process exists.

**WHAT HAPPENS WITHOUT INCIDENT MANAGEMENT:**
Engineers flood into a Slack channel. Five start investigating
different theories simultaneously. Two restart services without
telling others. One escalates to the VP without context. Three
engineers wait for direction that never comes. The database
engineer fixes the actual root cause at minute 47 - but two
of the restarts introduced a second issue that takes another
23 minutes to untangle. Total downtime: 70 minutes.
Revenue lost: $3.5M.

**WHAT HAPPENS WITH INCIDENT MANAGEMENT:**
IC is automatically paged (SEV1 trigger). IC joins within
2 minutes, declares incident severity, appoints a tech lead,
and a communications lead. IC posts: "All non-investigation
actions must be approved by me." Tech lead narrows to three
hypotheses and assigns one engineer per hypothesis. At minute
8, DB engineer identifies root cause. IC approves the fix.
Communications lead updates stakeholder status page. Fix
deployed at minute 15. IC runs cleanup checklist. Postmortem
scheduled within 48 hours. Total downtime: 15 minutes.
Revenue lost: $750K. $2.75M saved.

**THE INSIGHT:**
The process does not slow the engineers - it coordinates them.
Ten engineers working in parallel without coordination is
slower than five engineers working with explicit coordination.
The bottleneck in incident response is rarely technical
capability; it is organizational coherence under pressure.

---

### 🧠 Mental Model / Analogy

> Incident management is like ICS (Incident Command System)
> used by firefighters. When multiple fire companies respond
> to a large fire, there is one incident commander who does
> not hold a hose - their job is to coordinate all companies,
> manage resources, communicate with dispatch, and make
> strategic decisions. Fighters work faster when they have
> clear commands and boundaries because they are not wasting
> cognitive load on coordination.

Element mapping:

- "Incident Commander" → IC role in software incidents
- "Firefighters holding hoses" → technical responders
- "Fire dispatch" → communications lead / status page
- "Fire intensity levels" → incident severity levels (SEV1-4)
- "Fire station runbooks" → pre-written diagnostic runbooks
- "Post-fire report" → blameless postmortem

Where this analogy breaks down: fire is physical and visible;
software incidents are invisible and require instrumentation
to observe. An incident commander in software must rely entirely
on dashboards and engineer reports, not direct observation.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Incident management is the plan your team follows when
something breaks in production. Instead of everyone panicking
and doing random things, one person leads, everyone knows
their role, and the team works together efficiently to fix
the problem and make sure it does not happen again.

**Level 2 - How to use it (junior developer):**
Know your team's severity definitions (SEV1 = service down,
SEV2 = major degradation, SEV3 = minor impact). Know how
to join an incident channel and how to take actions during
an incident (always announce changes in the channel). Read
your team's runbooks before you are on-call. After each
incident you were involved in, contribute to the postmortem.

**Level 3 - How it works (mid-level engineer):**
Effective incident management has five phases: Detection
(alert fires or user reports), Triage (severity assessment,
IC assignment), Response (investigation, hypothesis testing,
fix), Recovery (verify fix, drain rollback risk), and
Retrospective (blameless postmortem, action items). Each
phase has an expected time budget. MTTD and MTTR are the
primary performance metrics. SLO error budget consumption
rate during an incident determines escalation urgency.

**Level 4 - Why it was designed this way (senior/staff):**
The IC model was deliberately borrowed from aviation and
emergency management, where its effectiveness under pressure
has been proven over decades. The single IC with veto power
was specifically designed to prevent the "too many cooks"
failure mode - where multiple senior engineers with competing
opinions cause decision paralysis. The blameless postmortem
design reflects Google SRE's insight that blame causes
information hiding: engineers will not report their own
mistakes honestly if they fear punishment. Without honest
reporting, organizational learning is impossible.

**Level 5 - Mastery (distinguished engineer):**
At organizational scale, incident management becomes a
feedback loop for engineering quality. Tracking recurring
incident categories reveals systemic problems in architecture,
deployment practices, or monitoring coverage. An organization
that has the same incident twice without structural change
has failed its incident process. Mature organizations measure
"incident recurrence rate" as a quality metric. They also
measure "time to declare incident" - because teams with
fear of declaring incidents too early normalize a culture of
heroism where problems fester before becoming formal incidents,
increasing MTTR. At scale, the incident process must be
sufficiently low-friction that declaring a SEV3 incident is
faster than "informally handling it," which requires trust
in the process and low bureaucratic overhead.

---

### ⚙️ How It Works in Practice

**FIVE PHASES OF INCIDENT MANAGEMENT:**

```
┌─────────────────────────────────────────────────┐
│          INCIDENT MANAGEMENT LIFECYCLE          │
├─────────────────────────────────────────────────┤
│ PHASE 1: DETECTION (target: <5 min)             │
│   Alert fires → IC paged → Incident declared   │
│   OR: User report → triage engineer → SEV?     │
│                                                 │
│ PHASE 2: TRIAGE (target: <10 min)               │
│   IC assigned → severity declared              │
│   Initial scope: what is broken, who is affected│
│   Stakeholders notified per severity SLA        │
│                                                 │
│ PHASE 3: RESPONSE (target: varies by severity)  │
│   IC coordinates responders                     │
│   Hypotheses formed → tested sequentially      │
│   All changes announced in incident channel    │
│   Status page updated                          │
│                                                 │
│ PHASE 4: RECOVERY (target: <30 min post-fix)    │
│   Fix deployed → metrics verified              │
│   Rollback risk drained → incident resolved    │
│   All-clear: stakeholders notified             │
│                                                 │
│ PHASE 5: RETROSPECTIVE (target: within 48h)     │
│   Blameless postmortem written                 │
│   Action items assigned with owners + deadlines│
│   Patterns tracked across incident history     │
└─────────────────────────────────────────────────┘
```

**ROLES AND RESPONSIBILITIES:**

| Role                    | Primary Responsibility                      | Key Behavior                                      |
| ----------------------- | ------------------------------------------- | ------------------------------------------------- |
| Incident Commander (IC) | Coordinate, make decisions, remove blockers | Does NOT investigate; delegates technical work    |
| Tech Lead               | Investigate root cause, direct responders   | Reports findings to IC, not to everyone           |
| Communications Lead     | Status page, stakeholder updates            | Shields responders from stakeholder interruptions |
| Scribe                  | Document timeline, actions, hypotheses      | Real-time record for postmortem                   |
| Responders              | Technical investigation and fixes           | Announce all actions in incident channel          |

**SEVERITY LEVELS:**

| Severity | Definition                                 | Response Time           | Example                                   |
| -------- | ------------------------------------------ | ----------------------- | ----------------------------------------- |
| SEV1     | Service down, revenue impact               | Immediate, 24/7         | Payment API completely unavailable        |
| SEV2     | Major degradation, significant user impact | <15 min, business hours | 50% error rate, checkout broken           |
| SEV3     | Minor degradation, limited user impact     | <1 hour                 | Recommendation service returning defaults |
| SEV4     | No immediate user impact                   | Next business day       | Background job running slow               |

---

### 🔄 How It Flows in an Organization

**INCIDENT TRIGGER TO RESOLUTION CHAIN:**

```
Alert fires / User report
   │
   ↓
On-call engineer triages severity
   │
   ├── SEV3/4 → engineer handles solo, logs in tracker
   │
   └── SEV1/2 → INCIDENT DECLARED
                    │
                    ↓
             IC joins incident channel
                    │
                    ↓
             Stakeholder notification sent
             (auto or manual per severity SLA)
                    │
                    ↓
             Responders organized with clear roles
                    │
                    ↓
             Hypothesis → Test → Announce → Repeat
                    │
                    ↓
             Fix deployed → metrics confirm recovery
                    │
                    ↓
             Incident resolved, all-clear sent
                    │
                    ↓
             Postmortem scheduled (within 48 hours)
```

**WHERE IT BREAKS DOWN IN PRACTICE:**
The most common failure point is the handoff between
"someone noticed something is wrong" and "incident formally
declared." Teams that stigmatize false alarms or early
declarations develop a culture where engineers spend 20 minutes
investigating before declaring, turning a 5-minute MTTD into
a 25-minute one. The second most common failure is postmortem
action items without owners - action items that say "the team
should improve X" reliably never get done.

**HEALTHY vs DEGRADED:**
Healthy: Incidents are declared early, postmortems are shipped
within 48 hours, action items have owners, and the same
category of incident decreases over time.
Degraded: Engineers "handle it themselves" without declaring,
postmortems are written days later, action items have no owners,
and recurring incidents are treated as normal.

---

### 💻 Code Example

Not applicable - incident management is a behavioral and
organizational process with no code API.

---

### ⚖️ Comparison Table

| Approach                         | Speed               | Learning           | Scalability | Best For                          |
| -------------------------------- | ------------------- | ------------------ | ----------- | --------------------------------- |
| **Structured ICS-based**         | Fast (role clarity) | High (postmortems) | High        | Teams >5 engineers, SaaS products |
| Ad-hoc heroics                   | Variable            | Low (no docs)      | Low         | Sole developer, hobby projects    |
| ITIL-based heavyweight           | Slow (process)      | Medium             | Medium      | Regulated industries              |
| Chaos engineering proactive      | N/A (preventive)    | Very high          | High        | Mature SRE orgs                   |
| AI-assisted (automated runbooks) | Fastest             | Medium             | Very high   | High incident volume orgs         |

**How to choose:**
Structured ICS-based incident management is appropriate for
any team that serves external users and has multiple engineers.
ITIL is appropriate when regulatory compliance (SOX, PCI) requires
formal change management. Start structured; add AI-assisted
tooling when incident volume justifies it.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                          |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The IC should be the most technical person on the call | The IC's job is coordination, not investigation - the most technical person should investigate, not coordinate                                                   |
| Blameless means no accountability                      | Blameless means no personal punishment for honest mistakes; individuals are still accountable for their action items and for not repeating systemic errors       |
| Postmortems are only for SEV1 incidents                | High-value learning often comes from SEV2/3 incidents that are early warning signs of systemic issues                                                            |
| Declaring an incident is admitting failure             | Declaring an incident early prevents failure from becoming larger; a culture that shames early declarations increases MTTR systematically                        |
| Incident management slows down recovery                | Studies show structured IC processes consistently reduce MTTR compared to ad-hoc responses, especially for incidents involving 3+ engineers                      |
| Runbooks eliminate the need for expert judgment        | Runbooks handle known failure modes; novel incidents still require expert judgment - runbooks reduce cognitive load for the 80% of cases, not the 20% edge cases |

---

### 🚨 Failure Modes & Diagnosis

**IC Bottleneck Under Load**

**Symptom:**
Responders are waiting for IC approval for every action. The
incident drags because one person is a decision bottleneck.
Engineers become frustrated and start making changes without
approval, introducing coordination chaos anyway.

**Root Cause:**
IC scope is too narrow - they are approving every change
instead of delegating authority to a tech lead for routine
diagnostic actions. The IC role was designed to prevent
chaotic parallel changes, not to require approval for every
`kubectl get pod` command.

**Warning Signs:**
IC is on every call being asked "can I check X?" Tech lead
exists in name but defers all decisions to IC. Incident
timeline shows long waits between actions.

**Fix:**
Redefine IC authority: IC approves production changes
(deployments, config changes, traffic shifting). Diagnostic
actions (read-only investigation, log inspection) are
delegated to tech lead without IC approval required.

**Prevention:**
Document the IC authority boundary explicitly in your
incident playbook. Train ICs to delegate diagnostic
authority immediately at incident start.

---

**Postmortem Action Item Graveyard**

**Symptom:**
The same incident category occurs repeatedly. Postmortems
are written but action items are never completed. Team morale
degrades as recurring incidents burn down the on-call team.

**Root Cause:**
Action items are assigned to "the team" rather than named
individuals. They have no deadlines. No one reviews them.
There is no connection between action item completion and
engineering quarterly goals.

**Warning Signs:**
Postmortem tracker has items from 6+ months ago marked open.
Incident retrospective meetings discuss the same patterns from
previous incidents without noting that last month's fix was
not deployed.

**Fix:**
Every action item must have: one named owner (not "the team"),
a specific deadline, a ticket in the engineering backlog with
a priority, and a review date in the next incident retrospective.
Senior engineers review action item completion status quarterly.

**Prevention:**
Integrate postmortem action items into sprint planning.
Track "action item completion rate" as an engineering health
metric alongside MTTD and MTTR.

---

**Late Incident Declaration (Heroism Culture)**

**Symptom:**
Engineers spend 30-60 minutes investigating before declaring
an incident, even for user-impacting failures. MTTD is
consistently high despite monitoring coverage.

**Root Cause:**
Engineers fear being seen as "overreacting" if they declare
an incident that resolves quickly. Culture treats incident
declarations as evidence of poor engineering rather than as
healthy early-warning system usage.

**Warning Signs:**
Post-incident reviews reveal incidents were known to engineers
20-40 minutes before declaration. Engineers describe
"handling it myself" before deciding to escalate.

**Fix:**
Leadership explicitly celebrates early incident declarations.
Track "time from first alert to incident declaration" as a
metric. Reward engineers who declare early, even if the
incident resolves in 5 minutes.

**Prevention:**
Explicitly state in your incident playbook: "When in doubt,
declare. A 5-minute incident that resolves immediately is
a better outcome than a 30-minute unrecognized outage."

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SRE` - incident management is a core SRE practice
- `Alerting Fundamentals` - alerts are the detection layer
  that initiates incident management
- `SLO (Service Level Objective)` - SLO burn rate determines
  incident severity and escalation priority

**Builds On This (learn these next):**

- `Post-Mortem and Blameless Culture` - the retrospective
  phase of incident management
- `Runbooks and Playbooks` - operational documentation that
  supports the response phase
- `SLO-Based Alerting Strategy` - uses SLO burn rate to
  determine when to escalate incident severity

**Alternatives / Comparisons:**

- `Toil Reduction Strategy` - incident management learns
  from incidents; toil reduction eliminates the recurring
  ones through automation
- `SRE Book - Core Principles Deep Dive` - the foundational
  text that established modern incident management practices
- `Health Check Patterns` - provides the detection signal
  that initiates the incident management process

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Structured process: detect, triage,      │
│              │ respond, recover, learn from failures     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Chaotic ad-hoc responses to production   │
│ SOLVES       │ failures waste time and prevent learning  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ IC coordinates people; IC does NOT fix   │
│              │ the problem. Role separation is the       │
│              │ entire point of the IC model              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any unplanned production event affecting  │
│              │ users or approaching SLO violation        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Planned maintenance (use change mgmt     │
│              │ process instead); solo developer context  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Waiting 30 minutes to "handle it myself" │
│              │ before declaring - heroism culture        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Process overhead vs reduced MTTR and     │
│              │ lower incident recurrence rate            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Structure under pressure is not         │
│              │ bureaucracy - it is how you think faster."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Runbooks → Post-Mortem Culture →         │
│              │ SLO-Based Alerting Strategy               │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The IC coordinates; the IC does not investigate. Assign
   the most senior technical engineer as tech lead, not as IC.
2. Blameless does not mean no accountability - it means no
   personal punishment for honest mistakes in system design.
3. Postmortem action items without named owners and deadlines
   are guaranteed to never be completed.

**Interview one-liner:**
"Incident management is the structured process of detecting,
coordinating response to, and learning from production failures.
The IC model separates coordination from technical investigation

- the IC's only job is to ensure the right people are working
  on the right hypotheses without stepping on each other. The
  blameless postmortem is the learning mechanism that prevents
  the same incident from happening twice."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Under stress, human coordination fails without explicit role
assignment and communication protocols. Any high-stakes,
time-pressured, multi-person operation - whether a production
incident, a surgical team, or a military operation - performs
better with explicit roles and a single decision authority
than with democratic consensus under pressure.

**Where else this pattern applies:**

- **Aviation crew resource management** - captains have final
  authority but are trained to solicit co-pilot input; the same
  IC model with explicit authority and explicit voice channels
- **Emergency surgery** - surgeon leads, anesthesiologist owns
  their domain, nurses execute specific tasks; no coordination
  overhead during a critical moment
- **Nuclear plant emergency response** - shift supervisor is
  the IC with veto power over all actions; prevents individual
  operator decisions from conflicting under panic

**Industry applications:**

- **Financial trading systems** - trading desk incident
  commanders coordinate regulatory notification, customer
  communication, and technical fix simultaneously
- **Healthcare IT** - EHR system outages require patient safety
  coordination alongside technical resolution; IC manages both
  tracks under incident management discipline

---

### 💡 The Surprising Truth

The most important factor in incident MTTR is not the quality
of monitoring tooling, the experience of the responders, or
the complexity of the root cause - it is whether the on-call
engineer has read the runbook for that failure mode in the
last 30 days. Research from PagerDuty's incident data shows
that the same engineer resolves the same class of incident
50% faster when they recently reviewed the runbook vs when
they have not reviewed it for 3+ months. This means that
runbook maintenance and regular runbook review drills are
a higher-value investment in MTTR reduction than better
dashboards or more powerful observability tooling.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. [EXPLAIN] Explain to a junior engineer why the IC should
   not be the most technical person on the call, and what
   specific coordination failures occur when a senior engineer
   tries to both investigate and command simultaneously
2. [DEBUG] A postmortem review reveals that the same database
   connection pool exhaustion incident has occurred 4 times in
   6 months - each time with a postmortem but no recurrence
   prevention. Diagnose why the process is failing and what
   structural changes would fix it
3. [DECIDE] A SEV2 incident is ongoing. The tech lead proposes
   a 30-minute config change to fix the issue. An engineer
   suggests a faster but riskier 5-minute rollback. As IC,
   explain how you evaluate this decision and what information
   you need before deciding
4. [BUILD] Design the complete incident management process for
   a 20-person engineering team including: severity definitions,
   IC rotation schedule, communication protocol, runbook
   structure, and postmortem template
5. [EXTEND] Apply the IC model to a multi-team incident where
   3 separate teams each own a failing component. Design the
   coordination structure, escalation paths, and communication
   model that prevents each team from acting in isolation

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has an incident management process but MTTD
consistently exceeds 20 minutes despite having comprehensive
monitoring. Engineers report that alerts fire but are noisy -
the on-call engineer dismisses the first 3-5 alerts as "false
positives" before investigating seriously. What systemic change
to your alerting strategy would fix this pattern, and how does
the SLO error budget model help here vs threshold-based alerting?
_Hint: Think about the signal-to-noise problem in alerting and
how SLO burn rate alerts differ from individual threshold alerts
in terms of false positive rate and actionability._

**Q2.** At 10x scale - 100 engineers, 200 services, 50+
incidents per month - how does the incident management process
itself need to evolve? What breaks with the single IC model
when incidents are happening simultaneously? What does "incident
management at scale" look like structurally?
_Hint: Consider how companies like Stripe, Netflix, and Google
manage concurrent incidents and what role automated runbooks,
incident classification, and team-level vs org-level incident
processes play._

**Q3.** Design a 30-day "incident management bootcamp" for a
new SRE team at a company that currently has no formal incident
process. The team has 8 engineers, handles a fintech product
with SOC2 compliance requirements, and currently averages
90-minute MTTR. Specify the training components, the process
rollout sequence, the tooling requirements, and the success
metrics you would use to evaluate the program's effectiveness
after 90 days.
_Hint: Consider what cultural changes must happen alongside
process changes, how you measure "blameless culture" adoption,
and how compliance requirements affect the postmortem format._

---

### 🎯 Interview Deep-Dive

**Q1: Walk me through how you would handle a SEV1 incident where
the payment service is returning 100% errors and you have just
joined the incident channel with 8 other engineers.**
_Why they ask:_ Tests whether the candidate has internalized
the IC model and can apply it under pressure vs defaulting to
individual technical investigation.
_Strong answer includes:_

- First: identify if an IC has been assigned; if not, volunteer
  or ask for assignment before any investigation
- Establish communication norms: "All changes must be announced
  here before execution"
- Ask tech lead to summarize current hypotheses; ask scribe to
  document the timeline
- As IC: focus on: who is investigating, what is the blast
  radius, who needs to be notified, what is the rollback plan
- Do NOT: start investigating metrics yourself as IC

**Q2: A postmortem revealed that the same database connection
pool issue caused 3 incidents in 4 months. The action items
from the previous postmortems are still open. What would you
do as the on-call lead?**
_Why they ask:_ Tests whether the candidate understands incident
management as a learning feedback loop, not just a response
process.
_Strong answer includes:_

- This is a process failure, not just a technical failure -
  the postmortem process did not close the loop
- Immediate: prioritize the open action items in next sprint;
  escalate to engineering manager with specific completion dates
- Structural: add "review open postmortem AIs" as a standing
  agenda item in engineering all-hands or incident review
- Systematic: track "action item completion rate" alongside
  MTTR as an engineering health metric

**Q3: How do you define severity levels for a new product,
and what principles guide the classification?**
_Why they ask:_ Tests ability to operationalize abstract
incident severity principles into specific, usable definitions.
_Strong answer includes:_

- Severity should map to user impact, not to technical complexity
- SEV1: complete service unavailability or data loss risk for
  all users; direct revenue or regulatory impact
- SEV2: significant degradation for a substantial percentage
  of users; major feature broken
- SEV3: minor degradation, workaround available; limited user
  impact
- SEV4: no user impact; internal systems or non-critical
  background jobs
- The test: any engineer must be able to classify a new incident
  in under 30 seconds using just the definitions

**Q4: What is "blameless culture" and how do you create it
without removing individual accountability?**
_Why they ask:_ Tests nuanced understanding of psychological
safety vs accountability, a common SRE interview topic.
_Strong answer includes:_

- Blameless means: we do not punish individuals for honest
  mistakes that reveal systemic problems; we fix the system
- Accountability remains: individuals ARE responsible for
  completing their action items, for not knowingly repeating
  errors, and for escalating uncertainty promptly
- Creating it: leadership must model blameless behavior by
  NOT shaming engineers in public postmortems; engineers who
  report their own mistakes honestly must be praised not punished
- The test: would an engineer feel safe writing "I accidentally
  deleted the production database" in a postmortem? If no,
  blameless culture does not exist yet

> Entry stub. Generate full content using Master Prompt v3.0.
