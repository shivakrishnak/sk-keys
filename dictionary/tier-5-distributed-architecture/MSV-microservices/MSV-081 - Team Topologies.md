---
id: MSV-081
title: Team Topologies
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-080, MSV-082, MSV-001
used_by: MSV-080
related: MSV-080, MSV-082, MSV-001, MSV-003, MSV-085
tags:
  - microservices
  - architecture
  - deep-dive
  - organization
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 81
permalink: /microservices/team-topologies/
---

# MSV-081 - Team Topologies

⚡ TL;DR - Team Topologies (Skelton + Pais,
2019): a framework for organizing engineering
teams to produce fast flow of software delivery.
Four team types: (1) Stream-aligned: owns a
product stream end-to-end (e.g., Payments). (2)
Platform: provides internal developer platform
to reduce cognitive load. (3) Enabling: temporarily
helps stream teams adopt new capabilities (e.g.,
Kubernetes migration). (4) Complicated-subsystem:
owns a complex domain (e.g., ML recommendation
engine). Three interaction modes: Collaboration
(short-term joint work), X-as-a-Service (consume
a platform API), Facilitating (enabling team
teaches). Goal: minimize cognitive load per team
so each stream-aligned team can deploy independently
at high frequency. Conway's Law applied deliberately.

| #081 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Conway's Law in Microservices, Service Ownership Model, What are Microservices | |
| **Used by:** | Conway's Law in Microservices | |
| **Related:** | Conway's Law in Microservices, Service Ownership Model, What are Microservices, Domain-Driven Design, Monolith to Microservices Migration | |

---

### 🔥 The Problem This Solves

**WHY MOST MICROSERVICES TEAMS FAIL: COGNITIVE OVERLOAD:**
Org has 20 microservices. 4 development teams.
Each team: responsible for 5 services. Also:
1 platform team that maintains CI/CD, K8s,
monitoring. But: developers interrupt platform
team constantly ("my deployment is broken",
"need a new namespace", "prometheus alert
firing"). Platform team: becomes a bottleneck.
Stream teams: wait 2 days for platform team
help. Speed of delivery: slows. Root cause:
no clear interaction model between platform
and stream teams. Team Topologies: solves this
with explicit interaction modes and team types.

---

### 📘 Textbook Definition

**Team Topologies** (Matthew Skelton and Manuel
Pais, 2019) is a framework for designing team
structures that optimize software delivery
flow. It defines four fundamental team types
and three interaction modes:

**Four Team Types:**
- **Stream-aligned team**: aligned to a single
  flow of business or technical work (e.g.,
  checkout flow, payments, user registration).
  The primary team type; all others exist to
  support stream-aligned teams.
- **Platform team**: provides internal products
  (internal developer platform - IDP) consumed
  by stream-aligned teams as self-service. Goal:
  reduce cognitive load of stream teams.
  Example: CI/CD pipelines, K8s namespace
  provisioning, observability dashboards.
- **Enabling team**: specialist team that helps
  other teams adopt new capabilities. Temporary
  engagement: works WITH a stream team, then
  steps back. Example: cloud migration team,
  security champions, SRE guild.
- **Complicated-subsystem team**: owns a technical
  domain with high intrinsic complexity that
  requires specialist knowledge. Example: ML
  recommendation engine, financial risk models,
  real-time rendering engine.

**Three Interaction Modes:**
- **Collaboration**: two teams work closely together
  on a problem (for a limited time; ongoing
  collaboration = impedance mismatch).
- **X-as-a-Service**: one team consumes a service
  provided by another (minimal interaction; platform
  team -> stream team).
- **Facilitating**: enabling team helps another
  team learn or adopt a new practice.

**Cognitive load**: the KEY metric. Teams should
not be cognitively overloaded (too many services,
too many technologies, too many responsibilities).
When a team is overloaded: all Team Topologies
principles exist to reduce cognitive load.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Team Topologies: 4 team types + 3 interaction
modes. Goal: stream-aligned teams can deploy
independently without bottlenecks. Conway's
Law used deliberately.

**One analogy:**
> Team Topologies is like an orchestra. Stream-
> aligned teams: the musicians (playing the
> actual music = delivering features). Platform
> team: the stage crew (microphone setup, lighting,
> instruments in tune - without the crew's work,
> musicians can't perform). Enabling team: the
> conductor's assistant (teaches musicians a
> new technique temporarily). Complicated-subsystem
> team: the solo virtuoso (unique skill required
> for one complex piece). Without good stage
> crew (platform team) and clear roles, musicians
> waste 50% of their time tuning their own
> microphones instead of playing music (features).

**One insight:**
The most important idea in Team Topologies is
X-as-a-Service interaction mode. Platform team
+ X-as-a-Service interaction: breaks the bottleneck
pattern. Stream team should NEVER have to ask
platform team for help; they should be able to
self-serve. If stream teams constantly ask:
platform team is not providing X-as-a-Service
(it's providing X-as-a-project, which has lead
time). The metric: if a stream team needs a new
K8s namespace, how long does it take? X-as-a-
Service target: < 1 minute (self-serve). Current
reality: if > 1 day: platform team is a bottleneck.

---

### 🔩 First Principles Explanation

**COGNITIVE LOAD: THE CORE CONSTRAINT**

```
Cognitive load = amount of mental effort required
to understand and work on a software system

Types of cognitive load per team:
1. Intrinsic: complexity of the domain itself
   (payments, risk, ML - high intrinsic load)
2. Extraneous: accidental complexity from tools,
   environments, processes (bad CI/CD, manual
   deployments, unclear ownership)
3. Germane: learning and building mental models
   (good learning = good germane load)

Team Topologies goal:
  Reduce EXTRANEOUS cognitive load (platform team
    handles K8s, CI/CD, monitoring so stream team
    doesn't have to)
  Allow team to focus on INTRINSIC load (their
    domain complexity)
  Enable GERMANE load (team gets better at their
    domain)

Cognitive overload signals:
  Team: doesn't know all services they own
  Oncall: can't diagnose issues ("I didn't
    write that service")
  Documentation: out of date (no time)
  PR review: delayed (overwhelmed)
  Technical debt: growing fast
  
Recognize: if your team is showing these signals,
it's cognitively overloaded. Solution: reduce
number of services, add platform capabilities,
or split the team.
```

**FOUR TEAM TYPES: WHEN TO USE EACH**

```
Stream-aligned team:
  Size: 5-9 engineers (two-pizza)
  Owns: 1-3 closely related services
  Deployment: independent (no external approval)
  Metrics: deployment frequency, lead time,
           customer satisfaction
  Example: "Checkout Team" - owns checkout flow,
           payment integration UI, cart

Platform team:
  Size: 5-12 engineers
  Provides: internal developer platform (IDP)
  Success metric: self-service rate
    (% of stream team needs met without asking)
  Common IDP capabilities:
    - K8s namespace creation: self-service
    - CI/CD pipeline templates: self-service
    - Database provisioning: self-service
    - Observability dashboards: self-service
    - Secret management: self-service
  Anti-pattern: platform team that must be
    consulted for every deployment
    (not a platform, a gatekeeper)

Enabling team:
  Duration: temporary (3-6 months max)
  Purpose: upskill stream teams
  Examples:
    - Cloud migration: help stream teams
      containerize their services (then leave)
    - Security: teach security practices
      (then stream teams self-sufficient)
    - Observability: help teams add tracing
      (then teams do it themselves)
  NOT: permanent consultants embedded in teams
  NOT: a team that does the work for others

Complicated-subsystem team:
  Size: small, specialist (3-6 engineers)
  Owns: complex domain requiring specialist skill
  Examples:
    - ML recommendation engine
    - Real-time fraud detection model
    - Financial risk calculation engine
  Interaction: X-as-a-Service (other teams
    consume their API; don't need to understand
    the internals)
```

---

### 🧪 Thought Experiment

**SPOTIFY MODEL vs TEAM TOPOLOGIES**

```
Spotify Model (2012):
  Squads: stream-aligned teams (similar)
  Tribes: groups of squads (similar to stream teams)
  Chapters: horizontal skill communities
  Guilds: informal communities of practice
  
  Problem: Spotify model is misunderstood and
  misapplied. Companies copied the org chart
  without copying the culture.
  Spotify themselves: abandoned parts of the
  model by 2020.
  "Spotify doesn't use the Spotify model."

Team Topologies vs Spotify Model:
  Team Topologies: more explicit about
  interaction modes (X-as-a-Service vs
  Collaboration vs Facilitating)
  Team Topologies: cognitive load as primary
  constraint (Spotify model: doesn't name this)
  Team Topologies: enables/platform distinction
  more nuanced (Spotify: chapters/guilds)
  Team Topologies: avoids the "copy the org
  chart" trap with explicit interaction rules

Lesson:
  Don't copy org charts.
  Copy the PRINCIPLES:
  (1) stream teams deploy independently
  (2) platform reduces cognitive load
  (3) enabling is temporary
  (4) interaction modes are explicit
```

---

### 🧠 Mental Model / Analogy

> Team Topologies is like a franchise restaurant
> model. Stream-aligned teams: individual franchise
> locations (run their business autonomously).
> Platform team: corporate headquarters (provides:
> supply chain, brand standards, marketing,
> common systems - so each location doesn't build
> them independently). Enabling team: the corporate
> trainer (comes to a location for 2 months,
> teaches new cooking technique, then leaves;
> location is now self-sufficient). Complicated-
> subsystem team: the corporate chef (creates
> signature recipes that all locations use;
> locations don't need to know how to create
> the recipe, just how to execute it). Without
> the franchise model (platform team): each
> location reinvents everything. With it: each
> location focuses on its customers (stream).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Team Topologies: 4 types of teams, 3 ways teams
interact. Goal: each product team can deploy
features independently without waiting for other
teams. A platform team provides tools; product
teams use them self-service.

**Level 2 - Platform team basics (junior developer):**
Platform team provides: a "golden path" for
new service creation. New service: run a CLI
command to get a new K8s namespace, CI/CD pipeline,
monitoring dashboard, and service template
(pre-configured with security, observability).
Developer: focuses on business logic; never
needs to understand Kubernetes internals.

**Level 3 - Interaction mode selection (mid-level):**
When to use Collaboration vs X-as-a-Service:
- Collaboration: when problem is novel and
  neither team has the full solution (short-term).
  Cost: high cognitive load, lots of meetings.
- X-as-a-Service: when problem is well-understood
  and can be packaged as a product. Cost: low
  ongoing interaction. Benefit: scale without
  coordination.
Rule: start with Collaboration to discover
the right API; then evolve to X-as-a-Service
when the interface stabilizes.

**Level 4 - Team size and cognitive load (senior):**
Team cognitive load budget: ~5-9 microservices
max per team (rough). This drives service
counting differently. Instead of asking "how
many services?" ask: "how many teams do we need
and what can each team reasonably own?" 50
developers, 7 services per team (max): max
7-8 stream-aligned teams. 50 microservices:
requires 50 / 5-7 = 7-10 stream teams. This
is the capacity planning model for microservices.
If your microservices count exceeds team capacity:
cognitive overload is inevitable.

**Level 5 - Dynamic topology evolution (principal):**
Team topology is not static. As product matures:
interaction modes change. New capability: stream
team + enabling team Collaborate (early) -> stream
team self-sufficient + platform team adds to
IDP (X-as-a-Service) -> enabling team moves
on. Platform team itself grows: may need to be
streamed (different platform teams for different
capabilities: infra platform, data platform,
security platform). Anti-pattern: topology
frozen at initial design. Good CTOs review
team topology quarterly: is cognitive load
still acceptable? Are interaction modes working?

---

### ⚙️ How It Works (Mechanism)

```
PLATFORM TEAM GOLDEN PATH: what it looks like

# Developer creates a new service:
$ platform new-service checkout-v2
  Creating K8s namespace: checkout-v2
  Creating CI/CD pipeline: Jenkins pipeline
  Adding observability: Prometheus/Grafana
  Adding distributed tracing: Zipkin
  Creating service from template:
    checkout-v2/
      src/main/java/.../  (Spring Boot template)
      Dockerfile (golden image base)
      k8s/ (deployment + service + hpa yamls)
      .github/workflows/ci.yml
      pom.xml (standard dependencies)

# Result: developer writes business logic;
# infrastructure is pre-configured
# No K8s knowledge required by developer
# All golden path services: compliant by default
# (security, observability, resource limits)

# Platform team success metrics:
  self-service rate: 95%+ (stream teams
    can provision everything without platform
    team involvement)
  lead time for new service: < 30 minutes
  oncall pages to platform team:
    < 5% from stream team infra issues
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
TEAM TOPOLOGIES FOR A 40-ENGINEER ORG:

  Stream-aligned teams (24 engineers):
    Checkout Team (6): cart, checkout, confirmation
    Payments Team (6): payment, refund, billing
    Catalog Team (6): product, search, recommendations
    User Team (6): user, auth, notifications
    
  Platform team (8 engineers):
    Provides: K8s, CI/CD, observability, secret mgmt
    Interaction: X-as-a-Service
    Success metric: stream teams self-serve 95%+
    
  Enabling team (4 engineers, rotating quarterly):
    Current focus: help all stream teams adopt
    OpenTelemetry + distributed tracing
    Duration: 3 months; then stream teams
    handle tracing independently
    
  Complicated-subsystem team (4 engineers):
    ML recommendation engine
    Interaction: X-as-a-Service via API
    Stream teams: consume recommendations API;
    don't need ML knowledge
    
  INTERACTION MAP:
    Checkout Team ---X-as-a-Svc---> Platform
    Payments Team ---X-as-a-Svc---> Platform
    Enabling Team ---Facilitating-> All stream teams
    Catalog Team <--X-as-a-Svc---- ML Subsystem
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Platform team as gatekeeper vs X-as-a-Service**

```yaml
# BAD: Platform team as gatekeeper
# Developer needs a new Kubernetes namespace:
# 1. Open JIRA ticket: "Create namespace for checkout-v2"
# 2. Wait 2 days for platform team to review
# 3. Platform team creates namespace manually
# 4. Developer continues
# 
# Problem: Platform team is a bottleneck
# Not X-as-a-Service; it's X-as-a-project
# Stream team: blocked, frustrated
# Platform team: overwhelmed with tickets
# Interaction mode: Collaboration (expensive)
```

```bash
# GOOD: Platform team provides self-service CLI
# Developer creates namespace in 30 seconds:

# platform CLI (built by platform team)
$ platform-cli namespace create checkout-v2 \
  --team checkout \
  --environment staging

# OUTPUT:
# Creating namespace: checkout-v2
# Applying RBAC: checkout team members have access
# Creating ResourceQuota: cpu=4, memory=8Gi
# Creating NetworkPolicy: deny-all (allow-listed)
# Creating ServiceAccount: checkout-v2-sa
# Namespace ready in 15 seconds

# Stream team: no JIRA ticket, no waiting
# Platform team: built the tool once; no ongoing
# involvement per namespace creation
# Interaction mode: X-as-a-Service (scalable)

# Platform team success metric:
# # of namespace requests: 50/month
# # that required human involvement: < 3
# self-service rate: 94% ✓
```

---

### ⚖️ Comparison Table

| Team Type | Primary Goal | Success Metric | Interaction Mode |
|---|---|---|---|
| **Stream-aligned** | Deliver features fast | Deploy frequency, lead time | Any |
| **Platform** | Reduce cognitive load | Self-service rate > 95% | X-as-a-Service |
| **Enabling** | Upskill other teams | Time to team self-sufficiency | Facilitating |
| **Complicated-subsystem** | Encapsulate complexity | API quality; no "how does it work?" questions | X-as-a-Service |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Team Topologies means every team is independent with no dependencies | Team Topologies doesn't eliminate dependencies - it makes them explicit and manageable. Platform team: stream teams DO depend on it. The difference: dependencies are managed via X-as-a-Service (self-service, low friction) rather than ad-hoc requests (high friction, bottleneck). |
| Platform team should own all shared infrastructure and be a central authority | Platform team: provides capabilities as self-service products. It does NOT own or control stream team deployments. Stream teams deploy their own services; platform team provides the tooling. Central authority over deployments: creates a bottleneck (not Team Topologies). |
| Enabling teams are permanent (like Centers of Excellence) | Enabling teams: intentionally temporary. A successful enabling team makes itself obsolete: the target team becomes self-sufficient. If an enabling team is permanent: it's become a dependency (complicated-subsystem team) or a gatekeeper. 3-6 month engagements are the norm. After that: enabling team moves to next team/capability. |

---

### 🚨 Failure Modes & Diagnosis

**Platform team bottleneck: too much collaboration, too little X-as-a-Service**

**Symptom:**
Platform team has 200 open JIRA tickets from
stream teams. Average resolution time: 3 days.
Stream team lead: "We can't deploy because
we're waiting for the platform team." Platform
team: "We're drowning in requests, can't build
new capabilities."

**Root Cause:**
Platform team: operating in Collaboration mode
(tickets, manual work) instead of X-as-a-Service
mode. Stream teams: have learned to ask platform
team for every infrastructure task (no self-
service capability). Platform team: built
infrastructure (K8s, CI/CD) but not a PRODUCT
(self-service platform).

**Diagnosis:**
```
Measure self-service rate:
  Total stream team infra requests last month: 200
  Stream team self-served (no platform involvement): 30
  Self-service rate: 30/200 = 15%
  
  Target: > 90%
  Current: 15% = platform team is a gatekeeper
  
Identify the most common ticket types:
  Top 5 requests (volume): namespace creation,
  pipeline creation, alert rule addition,
  service account creation, secret creation
  These 5: account for 70% of all tickets
  These 5: should all be self-service
```

**Fix:**
```
QUARTER 1: self-service for top 5 request types
  Build: platform CLI for each
  Success: top 5 tickets drop to 0
  Platform team: freed to build next capability
  
QUARTER 2: golden path for new services
  Build: `platform new-service` command
  Reduces: new service setup from 2 days to
  30 minutes
  
Result: self-service rate > 90%
  Platform team: building new capabilities,
  not handling tickets
```

---

### 🔗 Related Keywords

**Organizational context:**
- `Conway's Law in Microservices` - Team Topologies
  is the practical implementation of Inverse
  Conway Maneuver
- `Service Ownership Model` - Team Topologies
  defines WHO owns services

**Technical context:**
- `What are Microservices` - Team Topologies
  is a prerequisite for microservices success

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| STREAM     | Delivers features; deploys          |
| ALIGNED    | independently; 5-9 engineers        |
+------------+-------------------------------------+
| PLATFORM   | Provides IDP; X-as-a-Service;       |
|            | metric: 95%+ self-service rate      |
+------------+-------------------------------------+
| ENABLING   | Upskills (temporary, 3-6 months)    |
+------------+-------------------------------------+
| SUBSYSTEM  | Complex domain; API only            |
+------------+-------------------------------------+
| ONE-LINER  | "Organize teams to produce          |
|            |  desired architecture (Conway).     |
|            |  Platform removes bottlenecks."     |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Four team types: Stream-aligned (delivers
   features), Platform (reduces cognitive load),
   Enabling (temporary upskilling), Complicated-
   subsystem (specialist domain).
2. X-as-a-Service interaction: platform team
   builds self-service products. Stream teams
   self-serve. No JIRA tickets for infra. 95%+
   self-service = healthy.
3. Cognitive load: the primary constraint. If
   a team is cognitively overloaded (too many
   services, too many technologies): split the
   team or add platform capabilities.

**Interview one-liner:**
"Team Topologies (Skelton + Pais, 2019): four
team types - Stream-aligned (owns product stream,
deploys independently), Platform (provides internal
developer platform as X-as-a-Service), Enabling
(temporary upskilling of other teams), Complicated-
subsystem (encapsulates complex specialist domain).
Three interaction modes: Collaboration (short-term
joint work), X-as-a-Service (self-service consumption),
Facilitating (enabling team teaches). Core metric:
cognitive load per team - platform team success =
95%+ self-service rate; stream teams deploy
independently with no platform team involvement
per deployment."

---

### 💡 The Surprising Truth

The most dangerous anti-pattern in Team Topologies
is the "too-helpful platform team." A platform
team that answers every stream team question,
participates in every incident, helps with every
configuration change: creates dependency, not
capability. Stream teams learn to ASK rather
than self-serve. Platform team: burns out
from supporting 5 stream teams' every need.
The BETTER platform team: sometimes says "no,
use the self-service tool" even when it's faster
for them to just do it manually. The investment
in building the self-service tool (painful short-
term) pays off when the platform team can support
20 stream teams instead of 5 (long-term scale).
Saying "no" to direct help is how platform teams
scale. It requires discipline and buy-in from
leadership.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DIAGNOSIS** Given an org with 40 engineers:
   describe the team topology you'd recommend
   (how many stream teams, what platform team,
   any enabling teams needed). Justify cognitive
   load calculations.
2. **PLATFORM PRODUCT** Design the minimum viable
   internal developer platform for a 5-stream-team
   org: what 5 self-service capabilities would
   reduce the most friction? How do you measure
   success?
3. **INTERACTION MODE** A new stream team needs
   to implement OpenTelemetry distributed tracing.
   Design a 3-month enabling team engagement:
   week 1-4 plan, success criteria, and what
   self-service capability the platform team
   should build to make future teams self-sufficient.
4. **BOTTLENECK FIX** Your platform team has
   a 3-day SLA on all requests. Analyze: what
   percentage of requests can be self-service?
   Design the first 3 self-service tools to
   build. Estimate the impact on SLA.
5. **EVOLUTION** An org starts with 2 stream
   teams and 1 platform team. After 2 years:
   10 stream teams. How should the topology
   evolve? What new team types emerge? When
   should the platform team split into sub-teams?

---

### 🧠 Think About This Before We Continue

**Q1.** Your company has: 1 Platform Team (8
engineers) providing K8s, CI/CD, monitoring for
6 stream-aligned teams. Platform team receives
150 JIRA tickets/month from stream teams. Average
ticket resolution: 2.5 days. The CTO says: "Platform
team is not delivering value." You say: "The
platform team IS delivering value; the INTERACTION
MODE is wrong." What is the wrong interaction
mode, what is the right one, and what specifically
should the platform team build to fix it?

**Q2.** A company has: ML Team (complicated-
subsystem), providing recommendations via API.
But every stream team that integrates with the
ML API requires 2 weeks of ML team involvement
(understanding the API, debugging issues). What's
the Team Topologies problem? Is the ML team
interaction mode correct? What should change:
(a) the API design, (b) the documentation, (c)
the interaction mode, or (d) the team type?

**Q3.** A startup with 15 engineers is growing
to 60 engineers in 12 months. Design the Team
Topologies evolution: current state (15 engineers),
6-month state (35 engineers), 12-month state
(60 engineers). At what size does a dedicated
platform team make sense? At what size does an
enabling team become necessary? What are the
triggers for topology changes (specific metrics
or events, not just headcount)?