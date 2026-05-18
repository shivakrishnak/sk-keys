---
id: MSV-080
title: Conway's Law in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-003, MSV-081
used_by: MSV-081, MSV-082
related: MSV-081, MSV-082, MSV-001, MSV-003, MSV-004, MSV-085
tags:
  - microservices
  - architecture
  - deep-dive
  - organization
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/microservices/conways-law-in-microservices/
---

⚡ TL;DR - Conway's Law: "Any organization that
designs a system will produce a design whose
structure is a copy of the organization's
communication structure." (Melvin Conway, 1968).
In microservices: your service boundaries mirror
your team boundaries. If 3 teams build "one" user
service: you get 3 user services with integration
points. Inverse Conway Maneuver: deliberately
design your team structure to produce the desired
microservices architecture. First decide the
service architecture, THEN organize teams around
it. Key insight: microservices adoption without
team restructuring just creates a distributed
monolith (all services owned by the same team
= same coordination overhead).

| #080 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, Domain-Driven Design, Team Topologies | |
| **Used by:** | Team Topologies, Service Ownership Model | |
| **Related:** | Team Topologies, Service Ownership Model, What are Microservices, Domain-Driven Design, Bounded Context, Monolith to Microservices Migration | |

---

### 🔥 The Problem This Solves

**WHY MICROSERVICES FAIL: TEAM STRUCTURE MISMATCH:**
Company adopts microservices. 30 services designed
by a centralized architecture team. 5 development
teams: each owns 6 services (6 services per team).
Services within one team: heavily coupled (same
daily standups, same planning, easy coordination).
Services across teams: friction (JIRA tickets,
meeting requests). After 2 years: the team
boundaries are the real service boundaries. Inter-
team services: loosely coupled (good). Intra-
team services: tightly coupled (distributed
monolith). Conway's Law predicted this.

---

### 📘 Textbook Definition

**Conway's Law** (Melvin Conway, 1968) states:
"Any organization that designs a system (broadly
defined) will produce a design whose structure is
a copy of the organization's communication
structure." In microservices terms: the services
you build will mirror the communication patterns
of the teams that build them. Teams that communicate
frequently: build tightly integrated services.
Teams that have formal handoff processes: build
loosely coupled services with well-defined interfaces.

**Key implications for microservices:**
- Service boundaries that cut across team boundaries:
  create integration friction (inter-team API
  negotiation, coordination overhead)
- Service boundaries that align with team boundaries:
  enable independent deployment (teams own their
  entire domain)
- "Team-first" architecture: design team structure
  FIRST to match desired service architecture

**Inverse Conway Maneuver** (Thoughtworks, 2015):
Deliberately structure your organization to produce
the desired architecture. Example: if you want
"user service" to be a clean domain: create a
"User Team" that owns all user-related concerns
(authentication, profile, preferences). The team
structure enforces the service boundary.

**Two-Pizza Rule** (Amazon): teams should be
small enough to be fed by two pizzas (~6-8 people).
Small teams: forced to define clear service APIs
(can't easily coordinate with many people). This
naturally produces loosely coupled services.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Conway's Law: your software architecture mirrors
your team communication structure. Want better
microservices? Design your team structure first.

**One analogy:**
> Conway's Law is like urban planning following
> social patterns. Cities: develop roads along
> the paths people actually walk (desire paths).
> The paths that get used most become roads; unused
> planned roads become overgrown. Similarly:
> services that teams communicate about daily
> (same team) become tightly integrated; services
> that require formal meetings to coordinate (different
> teams) become loosely coupled. The team communication
> structure becomes the system's API structure.

**One insight:**
Conway's Law is simultaneously a WARNING and a
TOOL. Warning: if your team structure doesn't
align with your desired service architecture,
the architecture will drift toward the team
structure over time (entropy). Tool: use the
Inverse Conway Maneuver to deliberately shape
the system by shaping the team structure. The
most effective way to change a software architecture
is to change the organizational structure first.
Architecture diagrams don't change systems;
team boundaries do.

---

### 🔩 First Principles Explanation

**CONWAY'S LAW IN PRACTICE:**

```
SCENARIO 1: ANTI-PATTERN
  Team structure:
    Backend Team A: order-service, payment-service,
                    inventory-service
    Backend Team B: user-service, auth-service,
                    notification-service
    Frontend Team: UI only
  
  Conway's Law prediction:
    Team A services: tightly coupled with each other
      (easy daily coordination; shared standups)
    Team B services: tightly coupled with each other
    Cross-team calls: order-service -> user-service
      become the loosest coupling point
      (formal API design because different team)
    
  Reality after 2 years:
    Order + Payment + Inventory: effectively one
    distributed system (coordinated deployments,
    shared DB patterns, implicit coupling)
    = Distributed monolith A
    
    User + Auth + Notification: distributed monolith B
    
    Only cross-team interface (order -> user):
    well-defined and loosely coupled
    
  Problem: this is the same as 2 monoliths
  No benefit of microservices

SCENARIO 2: CORRECT APPROACH (Inverse Conway)
  Desired architecture first:
    order-service owned by Order Team
    payment-service owned by Payment Team
    inventory-service owned by Inventory Team
    user-service owned by User Team
    (each service = one team)
  
  Team boundaries = service boundaries:
    Order Team: 1 service (order-service)
    Payment Team: 1 service (payment-service)
    (may be 2-3 closely related services max)
  
  Cross-team communication = cross-service API:
    Must be: formal contract, versioned, CDC tested
    Cannot be: shared DB, implicit coupling
    
  Conway's Law enforces: loose coupling
  by making tight coupling require cross-team
  coordination (expensive, so teams avoid it)
```

**TWO-PIZZA TEAM SIZE AND SERVICE GRANULARITY:**

```
Two-pizza team = 6-8 engineers
Owns: 1-3 closely related services
Runs: services in production (DevOps)
Defines: service API
Decides: technology choices (within guardrails)
Deployable: independently (no coordination)

Too-large team (20 engineers) owning 1 service:
  Sub-teams form internally
  Sub-teams: internally tightly coupled
  The service: becomes a monolith
  (Conway's Law within the team)

Too-small team (1 engineer) owning 10 services:
  Cannot maintain 10 services properly
  Knowledge: siloed (bus factor: 1)
  Services: neglected, security debt
  
Optimal: 5-8 engineers per service team
  Can own: 1-3 services max
  "You build it, you run it" (Amazon)
```

---

### 🧪 Thought Experiment

**AMAZON: CONWAY'S LAW AS COMPETITIVE ADVANTAGE**

```
Amazon's approach (Bezos's two-pizza rule, 2002):
  Mandate: all teams expose services via APIs
  "All service interfaces must be designed from
   the ground up to be externalizable"
  "Teams that do not do this will be fired"
  (Bezos memo, 2002)

Result:
  Each Amazon team: owns a service with a clean API
  Conway's Law: team boundaries = service boundaries
  Services: loosely coupled by organizational design
  
AWS (2006):
  Amazon had already built EC2, S3, SQS for internal
  use (because teams needed to use each other's
  services via APIs). External launch: just make
  the internal APIs public.
  
  AWS: not just a technology achievement
  AWS: a ORGANIZATIONAL achievement
  Conway's Law + Two-Pizza + API mandate
  -> most successful cloud platform in history

Lesson for microservices teams:
  Microservices without team reorganization:
  just creates a distributed monolith
  Team-first design + API mandate + autonomous teams:
  the actual prerequisite for microservices benefits
```

---

### 🧠 Mental Model / Analogy

> Conway's Law is like the game of telephone
> (Chinese whispers). When a message passes through
> many people (cross-team coordination), it gets
> distorted (latency, misunderstanding, formal
> interfaces). When people talk directly (same
> team), information flows freely (tight coupling,
> fast coordination). In software: the services
> that require many telephone-game hops to coordinate
> changes: develop clean APIs. Services that teams
> can change together in one meeting: become a
> distributed monolith. To break the pattern:
> make telephone-game hops the ONLY way to coordinate
> (organizational team boundaries are the service
> boundaries).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Conway's Law: the software architecture matches
the team structure. 3 teams = 3 big services.
1 small team per service = clean microservices.
Change your team structure to change your architecture.

**Level 2 - Inverse Conway Maneuver (junior developer):**
Decide the desired service architecture FIRST.
Then: organize teams around those services. "Payment
Team" owns payment-service. "Order Team" owns
order-service. No team owns more than 2-3 services.
Result: team boundaries naturally enforce service
boundaries and API contracts.

**Level 3 - DDD alignment (mid-level):**
DDD Bounded Contexts: natural team boundaries
in microservices. Each bounded context: one team.
Team: owns the ubiquitous language for their
domain. Terms like "order" mean the same thing
within the team (bounded context) and different
things across teams (different contexts). Team
boundary: Context Map anti-corruption layer.

**Level 4 - Platform teams (senior):**
Team Topologies (Skelton + Pais, 2019): four
team types that produce specific system architectures
(Conway's Law applied). Stream-aligned teams:
own a product stream (e.g., payments). Platform
teams: reduce cognitive load for stream teams
(provide internal developer platform). Enabling
teams: teach new capabilities (temporarily
assist stream teams). Complicated-subsystem teams:
own complex technical domains (ML, security).
Interaction modes between teams: also determine
interaction modes between services.

**Level 5 - Organizational sociotechnical systems (principal):**
The most advanced application of Conway's Law:
architectural evolution follows organizational
evolution. When a company acquires another: the
acquired system architecture doesn't integrate
smoothly (different communication structures).
M&A technical due diligence: analyze the acquired
company's team structure to predict the technical
architecture (and integration complexity). Vice
versa: before proposing a major architectural
change (monolith to microservices): propose the
ORGANIZATIONAL change first. Without organizational
change: the new architecture will revert to the
old one (Conway's Law entropy).

---

### ⚙️ How It Works (Mechanism)

```
CONWAY'S LAW DIAGNOSTIC TOOL:

Step 1: Draw the actual system dependency graph
  Node: each service
  Edge: runtime dependency (calls, shared DB)
  Weight: frequency of change coordination
         (how often do these services deploy together?)

Step 2: Draw the team communication graph
  Node: each team
  Edge: communication channels between teams
  Weight: communication frequency

Step 3: Overlay the two graphs
  ALIGNMENT: service dependencies = team communication
  Dependencies follow team communication: expected,
  healthy if teams are correctly sized
  
  MISALIGNMENT: service dependency across teams
  with high coordination frequency
  = tight coupling across team boundary
  = pain point (deployment coordination needed)
  = should be: same team OR clear stable API

Step 4: Decide remediation
  Option A: MERGE services (they're actually one)
    Merge the two services into one, owned by one team
    If coordination cost > API maintenance cost
  Option B: STABILIZE the API
    Accept the boundary; formalize it with CDC tests
    Reduce coordination with Pact contracts
  Option C: REORGANIZE teams
    Shift team boundaries to match service boundaries
    "Payment Team" takes over inventory-payment interface
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
INVERSE CONWAY MANEUVER: step-by-step

DAY 0: Current state
  3 teams, 9 services (3 per team)
  Problem: high coupling within teams,
  coordination overhead between services

WEEK 1: Desired architecture
  Architecture team: proposes service boundaries
  Based on: DDD bounded contexts
  Result: 6 core bounded contexts:
    Orders, Payments, Inventory, Users, Notifications,
    Catalog
  These become: 6 service team boundaries

WEEK 2-4: Team restructuring
  "Order Team": 6 engineers from Teams A and B
    who work most on order-related code
  "Payment Team": 4 engineers...
  (and so on for each bounded context)

MONTH 2-6: Service boundary reinforcement
  Each team: given clear ownership of their services
  Cross-team dependencies: must go through
  formal API contracts (Pact CDC tests)
  No shared database: enforced by team boundaries
  (different teams can't share DB without formal
  agreement on schema - friction prevents coupling)

MONTH 6+: Architecture mirrors teams
  Conway's Law: now WORKS FOR YOU
  Team boundaries = service boundaries
  Each team: deploys independently
  Cross-team: clean APIs
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: shared DB vs API-first**

```java
// BAD: two "services" sharing a database
// Conway's Law at work: same team owns both
// -> they took the easy path (shared DB)
// This is a distributed monolith

// In order-service:
@Repository
public interface CustomerRepository
        extends JpaRepository<Customer, Long> {
    // ORDER-SERVICE directly reads CUSTOMER table
    // Customer table: owned by customer-service team
    // But: order team has DB access too (no boundary)
    Optional<Customer> findByEmail(String email);
}

// Order-service: couples tightly to Customer schema
// If customer-service changes Customer table:
// order-service's queries break (no notification)
// Deployment: order + customer must be coordinated
// Conway's Law: both in same team -> they can "just"
// change the schema without formal process
```

```java
// GOOD: API-first, team boundaries respected
// Team boundary enforces the API contract

// In order-service: calls customer-service via API
@FeignClient(name = "customer-service")
public interface CustomerClient {
    @GetMapping("/api/v1/customers/{id}")
    CustomerSummary getCustomer(@PathVariable Long id);
    // CustomerSummary: ONLY fields order-service needs
    // NOT the full Customer entity
    // Customer schema changes: invisible to order-service
    // (customer-service translates internally)
    // Team boundary: enforces this API contract
    // Pact CDC test: verifies compatibility
}

// WHY team structure produces this:
// Order Team: daily standups about orders
// Customer Team: daily standups about customers
// Order Team CANNOT change customer DB
//   (different team's deployment)
// Order Team MUST use customer-service API
// Conway's Law: now produces loose coupling
```

---

### ⚖️ Comparison Table

| Team Structure | Conway's Law Prediction | Service Architecture |
|---|---|---|
| **1 large team, all services** | Tight coupling everywhere | Distributed monolith |
| **Teams cut by tech layer (FE/BE/DB)** | Horizontal coupling (FE/BE/DB must coordinate every feature) | 3-tier distributed monolith |
| **Teams by domain (Order/Payment)** | Domain-aligned services | True microservices |
| **Platform team + stream teams** | Platform abstractions + domain services | Team Topologies ideal state |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Conway's Law is a negative phenomenon to overcome | Conway's Law is neutral - it describes HOW things naturally happen, not that it's bad. The Inverse Conway Maneuver USES Conway's Law as a tool: deliberately structure teams to produce the desired architecture. Instead of fighting Conway's Law (failing), use it (successful). |
| Microservices just means decomposing a monolith into small services | Microservices requires BOTH technical decomposition (small services) AND organizational decomposition (small autonomous teams). Technical decomposition without organizational restructuring produces a distributed monolith (same coordination overhead, plus distributed system complexity). "The technical transformation must be accompanied by an organizational transformation" - Sam Newman. |
| The two-pizza rule means every service should have exactly 6-8 engineers | Two-pizza rule: team size, not service count. One team can own 1-3 closely related services. The number of services should follow: (1) natural bounded context boundaries; (2) team cognitive load (can the team understand all their services?). There's no universal "right" number of services per team; there's a right team size and a team structure that produces the desired service coupling. |

---

### 🚨 Failure Modes & Diagnosis

**Distributed monolith: Conway's Law with wrong team structure**

**Symptom:**
50 microservices. But: deployment requires
coordinating 8 teams. Every feature requires:
creating a JIRA epic, scheduling multiple team
meetings, coordinating releases across 4-6 services.
System feels MORE complex than the old monolith,
with no autonomy benefit.

**Root Cause:**
Team structure never changed. 8 backend teams:
each owns 6-7 services. Team members share
daily standups; naturally create tight coupling
within their 6-7 services. Features: span multiple
teams -> require cross-team coordination. This
is a distributed monolith with extra steps.

**Diagnosis:**
```
1. Deployment coordination analysis:
   For the last 20 deployments:
   How many required coordinating > 1 team?
   Expected (healthy): < 20%
   Actual (problem): > 70% = distributed monolith

2. Service coupling analysis:
   Per team: how many of their 6 services deploy
   together in > 50% of deployments?
   If most services in a team deploy together:
   they're actually 1 service (merge them)

3. Team communication graph:
   Does the communication pattern match the
   service dependency graph?
   If not: reorganize (Inverse Conway Maneuver)
```

**Fix:**
```
Inverse Conway Maneuver:
  Step 1: Identify actual bounded contexts
         (DDD context mapping)
  Step 2: Reorganize teams around contexts
         (painful but necessary)
  Step 3: Enforce service-team ownership
         (one team owns each service)
  Result: Conway's Law produces loose coupling
```

---

### 🔗 Related Keywords

**Organizational application:**
- `Team Topologies` - the modern framework
  for applying Conway's Law deliberately
- `Service Ownership Model` - direct consequence
  of Conway's Law: who owns each service?

**Technical context:**
- `What are Microservices` - autonomous teams
  is one of the prerequisite definitions
- `Domain-Driven Design` - bounded contexts
  align with team boundaries (Conway's Law)

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| CONWAY'S LAW | System design mirrors team        |
|              | communication structure           |
+--------------+-----------------------------------+
| INVERSE      | Design teams to produce desired  |
| CONWAY       | service architecture             |
+--------------+-----------------------------------+
| SIGNAL       | > 50% cross-team deploys =       |
| (bad)        | distributed monolith             |
+--------------+-----------------------------------+
| ONE-LINER    | "Want microservices? Reorganize  |
|              |  teams first. Architecture       |
|              |  follows team structure."        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Conway's Law: architecture = communication
   structure. Your services naturally mirror your
   teams. Fighting this is futile.
2. Inverse Conway Maneuver: design team structure
   FIRST to produce the desired service boundaries.
   Each team: owns 1-3 related services max.
3. Distributed monolith symptom: > 50% of deployments
   require cross-team coordination. Fix: reorganize
   teams to align with service boundaries.

**Interview one-liner:**
"Conway's Law: 'organizations design systems
that mirror their communication structure.' In
microservices: your service boundaries follow your
team boundaries. Wrong team structure = distributed
monolith (services tightly coupled within team,
cross-team coordination required for features).
Inverse Conway Maneuver: design desired service
architecture first (DDD bounded contexts), THEN
reorganize teams to match. Result: team boundaries
enforce service boundaries; Conway's Law works
FOR you. Amazon's two-pizza rule + API mandate:
classic Inverse Conway Maneuver that produced AWS."

---

### 💡 The Surprising Truth

Conway's Law is not just descriptive - it's
prescriptive for technology strategy. When evaluating
an acquisition target, experienced CTOs look at
the ORG CHART first, not the architecture diagram.
Why: the org chart tells you the REAL architecture
(through Conway's Law). A clean microservices
architecture diagram but a monolithic team structure:
the services are actually coupled (the diagram
lies). A messy-looking architecture diagram but
clear team ownership (each service owned by one
team): the services are actually independent
(the diagram undersells it). Before any technical
debt analysis: do organizational debt analysis.
The organizational structure is the source of
truth for coupling, not the architecture diagram.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DIAGNOSE** Given a system with 20 services
   and 5 teams: draw the deployment coordination
   graph for the last quarter's releases. Identify
   which service clusters are actually distributed
   monoliths. Explain the Conway's Law cause.
2. **REORGANIZE** Propose a team restructuring
   for the scenario in the failure mode above:
   which engineers move to which teams, what
   service ownership changes, and how do you
   handle the transition period?
3. **DDD MAPPING** Conduct a Context Mapping
   session for an e-commerce platform: identify
   5-6 bounded contexts, propose team boundaries,
   and predict what the service API structure
   will naturally become (Conway's Law prediction).
4. **AMAZON PATTERN** Explain how Amazon's
   "Bezos memo" (API mandate) and two-pizza rule
   are concrete implementations of the Inverse
   Conway Maneuver. What was the org change?
   What was the architectural result?
5. **ACQUISITION** You're doing technical due
   diligence on a startup acquisition. The startup
   has 6 services and 30 engineers in 2 large
   teams. Predict: what is the actual integration
   complexity when merging with your 15-team
   organization? What org changes would reduce
   integration pain?

---

### 🧠 Think About This Before We Continue

**Q1.** Your company has: Order Team (owns
order, cart, checkout services), Product Team
(owns catalog, inventory, pricing services),
and Customer Team (owns user, auth, address
services). A new feature requires: checkout
to reserve inventory (Order Team -> Product
Team) and show product recommendations (Order
Team -> Product Team). Both require cross-team
API changes. Conway's Law is causing pain.
What are your options: (a) keep teams, add
formal API process, (b) merge Order and Product
teams, or (c) restructure around feature streams
(shopping team: cart+catalog+inventory)?

**Q2.** Your company is building a B2B SaaS product.
You have 40 engineers. How do you apply Conway's
Law and Team Topologies to design the team
structure? What are the 4-5 stream-aligned teams,
what is the platform team's responsibility, and
how do you prevent the platform team from becoming
a bottleneck?

**Q3.** Amazon's Bezos API mandate (2002) is cited
as proof of Inverse Conway Maneuver success.
But: the mandate also came with "any team that
does not do this will be fired." Is organizational
change (team restructuring) sufficient for
microservices adoption, or does it also require
top-down mandate + enforcement? What happens
when teams "game the system" (create clean APIs
but still share databases internally)?