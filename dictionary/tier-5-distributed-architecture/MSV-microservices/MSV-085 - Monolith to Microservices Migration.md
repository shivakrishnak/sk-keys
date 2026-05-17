---
id: MSV-085
title: Monolith to Microservices Migration
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-003, MSV-080, MSV-081
used_by: MSV-001
related: MSV-001, MSV-003, MSV-080, MSV-081, MSV-082, MSV-004, MSV-086
tags:
  - microservices
  - architecture
  - deep-dive
  - migration
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 85
permalink: /microservices/monolith-to-microservices-migration/
---

# MSV-085 - Monolith to Microservices Migration

⚡ TL;DR - Monolith to Microservices Migration:
the process of incrementally extracting
functionality from a monolith into independent
microservices. Key patterns: Strangler Fig
(route new traffic to extracted service;
monolith: handles remaining; gradually strangle
all traffic), Branch by Abstraction (abstract
monolith component -> new service implements
abstraction -> remove abstraction), Database
Decomposition (most dangerous step: extract
service's data from shared DB). Golden rule:
never do a Big Bang rewrite. Always incremental.
Key prerequisite: observability + CI/CD must
exist in the monolith BEFORE starting extraction.
Without these: migration creates instability
with no way to detect or fix it.

| #085 | Category: Microservices | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, Domain-Driven Design, Conway's Law in Microservices, Team Topologies | |
| **Used by:** | What are Microservices | |
| **Related:** | What are Microservices, Domain-Driven Design, Conway's Law in Microservices, Team Topologies, Service Ownership Model, Bounded Context, On-Premises to Cloud Migration | |

---

### 🔥 The Problem This Solves

**MONOLITH SCALING AND DEPLOYMENT PROBLEMS:**
E-commerce monolith: 500,000 lines of Java.
40 developers: all work in one codebase. Daily
deployment: requires full regression test suite
(4 hours). Any team's change: can break any
other team's feature. Black Friday: needs to
scale checkout; but must scale the entire monolith
(including admin, reporting, recommendations
- all wasteful). A new developer: needs 3 months
to understand the codebase enough to make a
safe change. Two causes: tight coupling and
shared deployment unit. Migration: extract
high-value domains into independent services.

---

### 📘 Textbook Definition

**Monolith to Microservices Migration** is the
incremental process of extracting bounded contexts
from a monolithic application into independently
deployable microservices. Key patterns:

**Strangler Fig Pattern** (Martin Fowler, 2004):
Named after the Strangler Fig tree that grows
around and eventually replaces its host. In
microservices: add a proxy/router in front of
the monolith. New or extracted features: route
to the new microservice. Remaining features:
still route to the monolith. Gradually: extract
more features until the monolith handles nothing;
then remove it. The monolith is "strangled" over
time without a Big Bang rewrite.

**Branch by Abstraction**:
1. Create an abstraction (interface) for the
   component to be extracted.
2. Monolith: uses the abstraction (not the
   concrete implementation).
3. Build the new microservice implementing
   the abstraction.
4. Swap the implementation (now calls the
   service via HTTP/Feign).
5. Delete the old implementation.

**Database Decomposition Strategies:**
- **Shared DB (first)**: new service reads
  from the monolith's DB. Temporary; breaks
  DDD isolation. Used during transition.
- **Database per service**: the goal. Extract
  the service's tables to its own DB.
  Steps: synchronize data (CDC), cut over
  reads to new DB, stop writing to old
  tables, remove old tables.
- **Dual write**: service writes to both old
  and new DB during transition (with reconciliation).

**Big Bang Rewrite** (anti-pattern):
Rewrite the entire monolith as microservices
from scratch. Famous failures: Netscape 6.0,
FedEx ground. Reasons it fails: (1) business
continues on old system while rewrite happens
(old system gets new features; rewrite falls
behind); (2) team underestimates accumulated
business logic (edge cases); (3) rewrite takes
2-3x longer than estimated; (4) new system
launches with less functionality than old.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Monolith to microservices: strangler fig
pattern. Route traffic to new service
incrementally. Never Big Bang rewrite.
DB decomposition is the hardest step.

**One analogy:**
> Monolith-to-microservices migration is like
> renovating a house while living in it. You
> can't tear down all walls at once (Big Bang
> rewrite) - you'd have no shelter. Instead:
> renovate one room at a time (Strangler Fig).
> Family: continues to live in the house during
> renovation. Each room: extracted cleanly with
> its own new foundation (independent DB).
> The plumbing (shared database): the most
> complex part to separate (two bathrooms
> sharing one pipe; must split the pipe while
> both bathrooms still work). Final state:
> new house (microservices) built around the
> old structure which is then demolished (monolith
> removed).

**One insight:**
The order of extraction matters enormously.
Always extract the LEAST COUPLED and MOST
BUSINESS-VALUABLE domain first. Why: (1)
less coupled = easier to extract (fewer
dependencies to handle); (2) most business
valuable = the team immediately sees the
benefit of faster, independent deployment;
(3) the team: builds the extraction skill and
process on an easier service before tackling
the hard ones. Teams that try to extract the
most complex domain first: get burned, lose
morale, and often abandon the migration.

---

### 🔩 First Principles Explanation

**STRANGLER FIG: STEP-BY-STEP**

```
STARTING STATE:
  All traffic -> Monolith
  Monolith: handles Orders, Payments,
            Catalog, Users, Notifications

STEP 1: Add routing proxy
  Traffic -> [Nginx / API Gateway] -> Monolith
  No change to users; proxy passes all traffic
  Proxy: can now redirect individual paths

STEP 2: Extract Notifications service
  (chosen: least coupled; no DB dependencies
  beyond sending events)
  Build: notification-service
  Test: in parallel with monolith
  Route: POST /api/notifications -> new service
  Monolith: still handles all other routes

STEP 3: Extract Catalog service
  Build: catalog-service
  DB: extract catalog tables
  Route: /api/catalog/* -> catalog-service
  Monolith: still handles Orders, Payments, Users

STEP 4: Extract User service
  Most complex: User tied to auth (JWT)
  Build: user-service + auth-service
  DB: user tables migrated
  Route: /api/users/*, /api/auth/* -> new services

STEP 5: Extract Payment service
  PCI compliance: requires careful DB migration
  Dual write: payment data to both old + new DB
  Verify: reconciliation pass (0 discrepancies)
  Cutover: reads to new DB
  Remove: from monolith

STEP 6: Extract Order service
  Last: most coupled in this example
  Monolith: now only has Order logic
  Extract: order-service
  Remove: monolith entirely

FINAL STATE:
  Traffic -> [API Gateway] -> 6 microservices
  Monolith: decommissioned
  Duration: typically 12-24 months for large monolith
```

**DATABASE DECOMPOSITION: THE CRITICAL PATH**

```
Most complex step: extracting the shared database

PROBLEM:
  Monolith: one big DB
  Example: orders table references users table
  (foreign key constraint)
  
  Order service extracted:
  but still needs user data.
  Can't just take the users table
  (monolith still uses it)

PATTERN 1: SHARED DB (transitional)
  Order service: reads from shared monolith DB
  Fast to start; but:
  - Coupling maintained (shared schema)
  - Order team: can't change schema independently
  - Acceptable ONLY as transitional step
  Duration: 1-2 sprints max

PATTERN 2: DATABASE PER SERVICE (target)
  Step 1: Identify order-service's data
    Tables: orders, order_items, order_status
  Step 2: Create orders-db (new DB)
  Step 3: Sync data: CDC (Debezium) or ETL
    Change Data Capture: streams changes
    from old DB to new DB in real time
  Step 4: Dual write (new order service:
    writes to BOTH old and new DB)
    Reconciliation: verify parity
  Step 5: Switch reads to new DB
    Gradual: 1% -> 10% -> 50% -> 100%
    Monitor: data discrepancies
  Step 6: Stop writing to old DB
  Step 7: Remove old tables from monolith DB
  
Foreign key references:
  BEFORE: orders.user_id -> users.id (FK in DB)
  AFTER: application-level join
    order-service: calls user-service API
    to get user data for an order
    No DB-level FK constraint
    (eventual consistency accepted)
```

---

### 🧪 Thought Experiment

**AMAZON'S MONOLITH-TO-MICROSERVICES: THE REAL STORY**

```
Amazon (2001-2004):
  Started as: Perl/C++ monolith ("obidos")
  Problem: 500+ engineers, one codebase
  Deployment: 2-week release cycle
  Scale: millions of users, growing fast
  The monolith: could not scale independently
  (must scale all of it for any component)

Amazon's approach:
  Not a Big Bang rewrite.
  Strangler Fig: extract service by service.
  "Two-pizza team" mandate: each team
  owns their service end-to-end.
  API mandate: all team interactions via APIs.
  
  Order of extraction:
  1. Easy/independent services first
     (recommendations, search)
  2. Then: more coupled services
     (cart, checkout, fulfillment)
  3. Duration: 3+ years

Result (2006):
  Amazon: had services with clean APIs
  These services: productized as AWS
  (EC2, S3, SQS, SimpleDB)
  AWS: not a planned product;
  a consequence of the microservices journey

Lesson:
  The microservices migration itself:
  can produce platform capabilities
  (internal developer platform -> external AWS)
  The journey: has unexpected upside if done right
```

---

### 🧠 Mental Model / Analogy

> Strangler Fig migration is like a software
> version of ship of Theseus. The original ship
> (monolith): plank by plank (service by service)
> replaced with new wood (microservices) while
> the ship still sails. At some point: every
> original plank has been replaced; the ship
> continues to sail throughout. If you took the
> ship to dry dock and replaced everything at
> once (Big Bang rewrite): the ship doesn't sail
> for 18 months, and when it relaunches: some
> planks are the wrong shape. The incremental
> replacement: ensures continuity of business
> while modernizing the architecture.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Monolith-to-microservices: extract one part
of the monolith at a time into its own service.
Never rebuild everything at once. Business
continues during migration.

**Level 2 - Strangler Fig basics (junior developer):**
Add an API Gateway in front of the monolith.
Build a new service for one domain. Route one
set of URLs to the new service. Test it. Verify
everything works. Then route more URLs. The
monolith: handles less and less until it's empty.

**Level 3 - Branch by Abstraction (mid-level):**
For a tightly coupled module (e.g., email sending
embedded throughout the monolith):
1. Create `NotificationService` interface.
2. `MonolithNotificationService` implements it
   (existing code, wrapped in interface).
3. All call sites: use `NotificationService`
   interface (not the concrete class).
4. Build `ExternalNotificationService` implements
   same interface (calls notification-service API).
5. Feature flag: toggle between old and new.
6. Verify: both implementations produce same
   results in production (shadowing).
7. Switch to new; delete old implementation.

**Level 4 - CDC for DB migration (senior):**
Debezium + Kafka: CDC (Change Data Capture)
for incremental DB migration. Debezium:
connects to PostgreSQL WAL (Write-Ahead Log);
streams every INSERT/UPDATE/DELETE as a Kafka
event. New service: consumes these events to
build its own DB. Allows: both old DB and new
DB to stay in sync during transition window
(hours to days). Cut-over: switch reads to new
DB when sync is verified. This is the safest
DB migration approach for microservices.

**Level 5 - Organizational prerequisites (principal):**
The technical migration will fail without
organizational prerequisites: (1) CI/CD pipeline
for the monolith (must be able to deploy multiple
times per day safely - if not, extraction testing
is impossible); (2) observability (distributed
tracing, metrics, alerting) - without this,
you can't tell if the extracted service works
correctly under production traffic; (3) team
structure aligned to target service boundaries
(Conway's Law): if teams don't change, services
will re-couple; (4) error budget culture: teams
must be willing to accept some production incidents
as learning during migration (zero-tolerance
culture makes migration too slow). These
prerequisites: take 6-12 months to establish.
Migration without them: high failure rate.

---

### ⚙️ How It Works (Mechanism)

```java
// BRANCH BY ABSTRACTION: notification extraction

// STEP 1: Create interface (already exists
// conceptually - now make it explicit)
public interface NotificationService {
    void sendOrderConfirmation(Order order);
    void sendShipmentUpdate(Shipment shipment);
    void sendPasswordReset(User user, String token);
}

// STEP 2: Monolith implementation (existing code,
// refactored to implement interface)
@Service
@ConditionalOnProperty(
    name = "notification.implementation",
    havingValue = "monolith")
public class MonolithNotificationService
        implements NotificationService {
    // Existing SMTP email code - just extracted
    // into a class implementing the interface
    @Override
    public void sendOrderConfirmation(Order order) {
        // existing SMTP code
    }
}

// STEP 3: New microservice client (calls
// notification-service via Feign)
@Service
@ConditionalOnProperty(
    name = "notification.implementation",
    havingValue = "service")
public class RemoteNotificationService
        implements NotificationService {
    private final NotificationClient client;
    
    @Override
    public void sendOrderConfirmation(Order order) {
        client.sendNotification(
            NotificationRequest.builder()
                .type("ORDER_CONFIRMATION")
                .orderId(order.getId())
                .recipientEmail(order.getEmail())
                .build());
    }
}

// STEP 4: Feature flag in application.yaml
// notification.implementation: monolith
// -> notification.implementation: service
// (after testing in production)
// No code change required to switch
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
MIGRATION ROADMAP FOR 500KLOC JAVA MONOLITH:

MONTH 0-3: Prerequisites (non-negotiable)
  [ ] CI/CD: automated tests + deploy to prod
      (deploy without fear < 30 min pipeline)
  [ ] Observability: structured logging,
      Prometheus metrics, distributed tracing
  [ ] Team restructuring: align to target domains
  [ ] API Gateway: added in front of monolith
      (proxy pass: all traffic still goes through)
  [ ] Service catalog: for all future services

MONTH 3-6: First extraction (low complexity)
  [ ] Extract: notification-service
      (few inbound dependencies; no DB tables)
  [ ] Route: /api/notifications to new service
  [ ] Validate: production traffic (2 weeks)
  [ ] Decommission: notification code in monolith
  RESULT: team builds migration muscle

MONTH 6-12: Mid-complexity extractions
  [ ] Extract: catalog-service
      (read-heavy; DB extraction: straightforward)
  [ ] Extract: user-service
      (complex: auth integration; high dependency)
  DB migration: CDC for both

MONTH 12-18: Complex extractions
  [ ] Extract: payment-service
      (PCI scope; dual-write; strict reconciliation)
  [ ] Extract: order-service
      (most coupled; last)

MONTH 18-24: Decommission
  [ ] Monolith: routes 0% traffic
  [ ] Remove: monolith deployment
  [ ] Celebrate: but maintain vigilance
  (distributed systems: new failure modes)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Big Bang rewrite vs Strangler Fig**

```java
// BAD: Big Bang rewrite decision
// "We'll rewrite everything in microservices in 6 months"
// Month 1: design all 15 services
// Month 2-5: build all 15 services simultaneously
// Month 6: attempt to cut over
//
// Reality:
// - Old monolith: got 200 new features during rewrite
//   (business didn't pause for the rewrite)
// - New system: missing 200 features + undiscovered
//   edge cases from 8 years of bug fixes
// - Data migration: 3 months more (not 1 month)
// - Cut over: delayed 4 months; then partial
// - Result: 18-month project, 2x budget, partial
//   success
// This happens. Every. Time.

// anti-pattern signaled by these words:
// "We'll rewrite everything..."
// "Clean slate..."
// "The old system is unmaintainable..."
// (often true, but not solved by full rewrite)
```

```java
// GOOD: Strangler Fig with API Gateway
// Incremental; business continues; risk bounded

// Step 1: Add routing config (no code change to monolith)
// Spring Cloud Gateway routing:

spring:
  cloud:
    gateway:
      routes:
      # Extracted service: notifications
      - id: notification-service
        uri: lb://notification-service
        predicates:
        - Path=/api/v1/notifications/**
        # All notification paths: new service

      # Everything else: still goes to monolith
      - id: monolith-fallback
        uri: http://monolith-service:8080
        predicates:
        - Path=/**  # catch-all
        # Monolith: handles all unextracted routes

# Business: continues to work
# notification-service: handles notification paths
# All other traffic: monolith (unchanged)
# Risk: bounded to notification domain
# Rollback: change one routing rule (minutes)

# Next sprint: extract catalog-service
# Add catalog route; monolith: handles the rest
# Migration: 1 bounded context per sprint
# Low risk. Reversible. Incremental.
```

---

### ⚖️ Comparison Table

| Migration Strategy | Risk | Duration | Business Continuity | Recommendation |
|---|---|---|---|---|
| **Big Bang Rewrite** | Very High | 12-24+ months | Disrupted | Never |
| **Strangler Fig** | Low (bounded) | 12-24 months | Continuous | Always |
| **Branch by Abstraction** | Low | Per module | Continuous | For tightly coupled modules |
| **Strangler + Branch combo** | Low | 12-24 months | Continuous | Best for most monoliths |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Migrating to microservices solves the monolith's problems | Microservices CHANGES the problems, not eliminates them. Monolith problems: tight coupling, slow deployment, shared DB contention. Microservices problems: distributed system complexity, network failures, eventual consistency, distributed tracing, service discovery, operational overhead. Before migrating: honestly assess whether the microservices problems are better than the monolith problems for YOUR team's current capability. Netflix, Amazon: invested years in tooling before their microservices worked reliably. |
| Database decomposition is straightforward: just move the tables | Database decomposition is the most dangerous and complex step in microservices migration. Risks: (1) foreign key constraints across services (must become application-level joins); (2) distributed transactions (monolith used single DB transactions; now need sagas or 2PC); (3) data consistency during migration window (dual write + reconciliation required); (4) performance (cross-service joins via API are slower than DB joins). Plan 2-3x more time for DB migration than service code extraction. |
| Strangler Fig means you can just route traffic between old and new | Strangler Fig also requires: (1) both systems handling the same data consistently (dual write or event sync during transition); (2) feature parity (new service handles ALL edge cases the monolith handled); (3) observability in both (can't tell if new service is worse without metrics); (4) rollback plan (what happens when new service fails?). Routing is the easy part; ensuring data consistency and feature parity during the transition window is the hard part. |

---

### 🚨 Failure Modes & Diagnosis

**Data inconsistency during extraction: dual write gone wrong**

**Symptom:**
Order service extracted (Strangler Fig, month
12). For 3 weeks: everything fine. Then: Finance
team reports 127 orders appear twice in the
monthly report. Some orders: in old DB + new
DB with different status (old: "pending",
new: "completed"). Customer support: receiving
calls about duplicate charges.

**Root Cause:**
Dual write during transition: order-service
writes to both old (monolith) DB and new
(order-service) DB. A race condition: monolith
writebacks an order update (from a background
job) to old DB after order-service already
updated new DB. Reconciliation: not catching
because both DBs show "latest" but different
transactions.

**Diagnosis:**
```sql
-- Find inconsistencies between old and new DB:
-- Run on both DBs; compare
SELECT order_id, status, updated_at
FROM orders
WHERE updated_at > '2024-01-01'
ORDER BY order_id, updated_at;

-- Cross-DB comparison (via Debezium CDC):
-- Check Kafka topic for both old DB and new DB events
-- Find orders where event sequences diverge
-- (old DB: 3 updates; new DB: 2 updates for same order)
```

**Fix:**
```
Immediate: stop writes to old DB for orders
  (order-service is the source of truth now)
  Update routing: all order writes -> order-service only
  Monolith background jobs: read from order-service API
  (not directly from shared DB)
  
Reconciliation:
  Run reconciliation script: compare all
  orders in old DB vs new DB
  For conflicts: order-service DB is source of truth
  Update old DB to match (for reports that
  still query old DB during transition)
  
Prevention:
  Dual write: write to NEW DB first (source of truth)
  Old DB: async replication only (read-only replica)
  Monolith: switch to read-only mode for migrated
  domains before extraction complete
```

---

### 🔗 Related Keywords

**Migration context:**
- `Conway's Law in Microservices` - team
  restructuring is the prerequisite for
  successful migration
- `Domain-Driven Design` - bounded contexts
  guide which parts to extract first
- `Team Topologies` - org design that enables
  independent service ownership post-migration

**Technical context:**
- `On-Premises to Cloud Migration` - migration
  often happens concurrently with cloud adoption

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| PATTERN      | Strangler Fig (always preferred) |
|              | Branch by Abstraction (tight     |
|              | coupling; feature flags)         |
+--------------+----------------------------------+
| ORDER        | Least coupled + most valuable    |
|              | first. Complex domains: last.    |
+--------------+----------------------------------+
| DB STEP      | Hardest: CDC + dual write +      |
|              | reconciliation. Plan 3x time.    |
+--------------+----------------------------------+
| NEVER        | Big Bang rewrite                 |
+--------------+----------------------------------+
| ONE-LINER    | "Strangle incrementally. Route   |
|              |  traffic per domain. DB last.    |
|              |  Never big bang."                |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Strangler Fig: proxy in front, route one
   domain at a time to new service. Monolith:
   handles the rest. Decommission when empty.
2. Order matters: extract least coupled + most
   business valuable first. Build migration
   skill on easy services before tackling
   complex ones.
3. Database decomposition: hardest step. Use
   CDC (Debezium) for dual-DB sync during
   transition. Plan 3x more time than expected.
   Dual write + reconciliation required.

**Interview one-liner:**
"Monolith to Microservices Migration: incremental,
never Big Bang rewrite. Primary pattern: Strangler
Fig - add API Gateway in front of monolith, route
extracted domain traffic to new microservice, monolith
handles remaining routes, gradually extract all domains
until monolith is empty. Branch by Abstraction: for
tightly coupled modules (interface + feature flag).
Database decomposition: most dangerous step - CDC
(Debezium/Kafka) for incremental sync, dual write
during transition, reconciliation before cutover.
Prerequisites before starting: CI/CD automation,
observability, team restructuring to align with
target service boundaries (Conway's Law)."

---

### 💡 The Surprising Truth

The most dangerous migration failure is not
technical - it's the "migration never ends"
phenomenon. Teams extract 10 of 15 bounded
contexts. The remaining 5: are the most complex
and most tightly coupled (they were left for
last intentionally). Leadership: declares
"migration complete" at 10/15 (political pressure).
The monolith: reduced but not eliminated. It
continues to receive features ("just this once").
Over 2 years: the monolith regenerates as
teams take the easy path of adding to the
monolith instead of the hard path of extracting.
5 years later: back to 80% of the original
problem. Prevention: set a hard decommission
date for the monolith and HOLD TO IT. The
monolith should be read-only (no new features)
from day 1 of migration. This forces extraction
and prevents the "monolith zombie" failure mode.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **STRANGLER FIG** Given a monolith with 8
   bounded contexts: create the migration roadmap.
   What are the extraction order and justification?
   What does the API Gateway routing config
   look like after 3 extractions? After all 8?
2. **BRANCH BY ABSTRACTION** Implement Branch
   by Abstraction for an email service embedded
   throughout a monolith. Show: interface definition,
   monolith implementation, remote service client
   implementation, and feature flag configuration.
3. **DB MIGRATION** Design the database migration
   for extracting user-service from a monolith
   where the `users` table has 15 FK references
   from other tables. What is the step-by-step
   plan? How do you handle the FK references
   during and after migration?
4. **CDC PIPELINE** Describe how Debezium +
   Kafka is used for CDC during DB migration.
   What is the exact flow from PostgreSQL WAL
   to the new service's DB? What are the failure
   modes (Debezium connector fails, Kafka lag
   increases) and how do you detect them?
5. **PREREQUISITES** A team wants to start
   monolith-to-microservices migration immediately.
   Their current state: manual deployments (weekly),
   no distributed tracing, 40 engineers in 2
   teams. List the 6-month prerequisite plan
   (what must be true before extraction starts)
   and justify each prerequisite.

---

### 🧠 Think About This Before We Continue

**Q1.** You are 6 months into a Strangler Fig
migration. You've extracted 4 services. The
Next service to extract: payment-service.
The CTO says: "Let's also rewrite it in Go
(it's currently Java) since we're extracting
it anyway." You advise against this. List
4 specific risks of combining technology
migration with service extraction. What is
the rule about scope during Strangler Fig?

**Q2.** During DB decomposition for order-
service: you're using dual write (writes to
both old monolith DB and new order-service DB).
During a 3-hour window: the order-service DB
is 30 seconds behind the monolith DB (Debezium
lag). A customer queries their order status
via the new service: sees "pending" (old status).
The monolith: shows "shipped." How do you
detect this discrepancy in real time? What
is the customer experience impact? How do
you shorten or eliminate the inconsistency
window?

**Q3.** Your monolith has 15 bounded contexts.
After 18 months: you've extracted 10. The
remaining 5 are the most complex (heavily
coupled, shared DB, complex transactions).
The team: is fatigued. The business: is
pressuring you to declare the migration
"done." What do you do? How do you quantify
the remaining value vs cost of extracting
the last 5? Is it ever acceptable to stop
a migration before 100% completion?