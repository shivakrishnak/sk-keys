---
id: MSV-038
title: Decomposition by Subdomain
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-031, MSV-032, MSV-037
used_by: MSV-005
related: MSV-031, MSV-032, MSV-037, MSV-080, MSV-081
tags:
  - microservices
  - architecture
  - deep-dive
  - ddd
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/microservices/decomposition-by-subdomain/
---

⚡ TL;DR - Decomposition by Subdomain uses Domain-Driven
Design (DDD) subdomains as service boundaries. DDD
classifies subdomains into Core (competitive advantage),
Supporting (enables core), and Generic (commodity).
Core subdomains get the most investment - custom built,
full microservice. Generic subdomains use off-the-shelf
tools. Supporting subdomains get lightweight custom
build. This classification guides where to invest
microservice complexity vs where to buy/simplify.

| #038 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain-Driven Design (DDD), Bounded Context, Decomposition by Business Capability | |
| **Used by:** | Service Decomposition | |
| **Related:** | Domain-Driven Design (DDD), Bounded Context, Decomposition by Business Capability, Conway's Law in Microservices, Team Topologies | |

---

### 🔥 The Problem This Solves

**TREATING ALL SERVICES EQUALLY:**
A team builds 20 microservices with equal investment.
Authentication service: same architecture, same team
allocation, same custom development as the core pricing
algorithm. Result: over-engineering for commodity
functions (authentication, email, file storage) and
under-investment in the core differentiating logic
(pricing, recommendation engine, fraud detection).
Competitors use Auth0 for authentication and build
better pricing algorithms. The uniform investment
decision is a strategic mistake.

Subdomain decomposition solves this: classify each
subdomain. Core subdomain (your competitive advantage):
custom, invested microservice. Generic subdomain
(commodity available off-the-shelf): buy, don't build.
Supporting subdomain (necessary but not differentiating):
simple, pragmatic solution.

---

### 📘 Textbook Definition

**Decomposition by Subdomain** uses DDD's strategic
design patterns to identify service boundaries. A
subdomain is an area of business knowledge. DDD defines
three types: (1) Core Subdomain - the unique competitive
advantage of the business; complex, constantly evolving,
build custom. (2) Supporting Subdomain - necessary to
support the core, but not differentiating; build simply
or buy if possible. (3) Generic Subdomain - commodity
functionality available in off-the-shelf solutions;
buy, don't build. Each subdomain maps to one or more
Bounded Contexts, which become microservices.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Not all services are equally valuable: core subdomains
are your competitive edge (build custom); generic
subdomains are commodity (use off-the-shelf).

**One analogy:**
> A restaurant's core subdomain: the chef's unique recipes
> (competitive advantage). Generic subdomain: the dishwasher
> (commodity - hire a dishwashing company or use a
> dishwashing machine). Supporting subdomain: the
> reservations system (necessary, not differentiating -
> use OpenTable rather than building custom). The restaurant
> owner invests ALL creative energy in the recipes, not
> in building a better dishwasher.

**One insight:**
The most important outcome of subdomain classification
is the BUILD vs BUY decision. A company building a
custom authentication system when Auth0, Okta, and
Cognito exist is wasting engineering resources that
should go to the core subdomain. Every hour spent on
authentication engineering is an hour NOT spent on
the pricing algorithm that wins customers.

---

### 🔩 First Principles Explanation

**THREE SUBDOMAIN TYPES - E-COMMERCE EXAMPLE:**

```
CORE SUBDOMAIN (build custom, invest heavily):
  Definition: unique value, competitive advantage
  Cannot buy off-the-shelf (by definition)
  Examples:
    - Personalization / Recommendation Engine
      (Amazon's core: better recommendations = more sales)
    - Dynamic Pricing Algorithm
      (Uber surge: core IP)
    - Fraud Detection
      (Stripe's core: better detection = lower fraud loss)
    - Search Relevance
      (Google's core: better search = more users)
  Architecture: Complex microservices, ML models,
    best engineers, significant investment
  Team: Senior engineers, domain experts, data scientists

SUPPORTING SUBDOMAIN (build simply, minimal investment):
  Definition: necessary but not differentiating
  Could buy but often too specific to business needs
  Examples:
    - Order Management (for non-ecommerce companies)
    - Notification Service
    - Report Generation
    - Admin Tools
  Architecture: Simple CRUD services, standard patterns,
    no complex domain logic
  Team: Mid-level engineers, standard implementation

GENERIC SUBDOMAIN (buy off-the-shelf):
  Definition: commodity, available as SaaS/library
  Examples:
    - Authentication/Authorization -> Auth0, Okta, Cognito
    - Email -> SendGrid, SES
    - SMS -> Twilio
    - File Storage -> S3
    - Full-text Search -> Elasticsearch, Algolia
    - Payments -> Stripe, Braintree
    - Analytics -> Mixpanel, Segment
  Architecture: Third-party integration; thin adapter layer
  Team: Minimal - configuration, not coding
```

**SUBDOMAIN vs BOUNDED CONTEXT:**

```
Subdomain:      Problem space (what the business needs)
Bounded Context: Solution space (how we model/build it)

Subdomain:         Recommendations (Core)
Bounded Context 1: User Behavior Tracking
Bounded Context 2: Recommendation Engine
Bounded Context 3: Recommendation Delivery API

Three Bounded Contexts serve one Core Subdomain.
Each Bounded Context becomes a microservice.

Ideally: 1 subdomain = 1 bounded context = 1 service
Reality: core subdomains often need multiple bounded
contexts due to complexity.
```

---

### 🧪 Thought Experiment

**BUILD vs BUY DECISION MATRIX:**

```
SCENARIO: Startup building a fintech lending platform

Subdomain: Authentication
  Type: Generic
  Build custom? Engineering cost: 3 months
                Maintenance: forever (security patches)
  Buy? Auth0: $1000/month, enterprise-grade security
  Decision: BUY. This is not your competitive advantage.

Subdomain: Credit Scoring
  Type: Core
  Buy? FICO score: available, but everyone uses it
       No differentiation - competitors use same score
  Build custom? ML model trained on your customer data:
               Better risk prediction -> lower default rate
               -> competitive pricing -> more customers
  Decision: BUILD CUSTOM. This IS your competitive
    advantage.

Subdomain: Document Management
  Type: Supporting
  Build custom? 2 months engineering
  Buy? DocuSign for e-signatures (Generic part)
       Custom storage logic needed (Supporting part)
  Decision: BUY for generic parts, simple custom for rest

MISTAKE TO AVOID:
  Building custom authentication (3 months)
  while using a commodity credit score (FICO)
  = investing in the wrong subdomain
  = competitor builds better credit model in those 3 months
```

---

### 🧠 Mental Model / Analogy

> Subdomain classification is like deciding what a
> restaurant should own vs rent vs outsource. Own the
> kitchen (core: recipes are your IP). Rent the location
> (supporting: necessary, but not unique to your
> business - pay a landlord). Outsource dishwashing
> (generic: commodity service, focus on food). A
> restaurant that owns its own dishwashing factory
> is misallocating capital. A restaurant that rents
> kitchen space and cooks in a shared facility loses
> its competitive advantage. Decomposition by subdomain
> is the make-vs-buy analysis applied to software.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Figure out which parts of the system are unique to
your business (core), which are needed but not unique
(supporting), and which are commodity (generic). Build
custom only what is truly unique. Buy the rest.

**Level 2 - How to use it (junior developer):**
For each potential service, ask: "Could we replace
this with a third-party tool in 3 months?" If yes:
it's generic (buy). "Does this directly create revenue
or competitive advantage?" If yes: it's core (build
with maximum investment). Otherwise: supporting (build
simply).

**Level 3 - How it works (mid-level engineer):**
Use Event Storming to discover bounded contexts. Then
classify each: does this context contain unique domain
knowledge that competitors can't replicate? Core. Does
it support operations? Supporting. Is there a SaaS
equivalent? Generic. The classification drives team
allocation: senior engineers on core, standard teams
on supporting, ops/DevOps on generic integrations.

**Level 4 - Why it was designed this way (senior/staff):**
DDD's subdomain classification reflects the economic
reality of software: not all code delivers equal business
value. The strategic investment of engineering talent
should be proportional to business value. Core
subdomains demand richly modeled domain layers (DDD
aggregates, domain events, ubiquitous language). Generic
subdomains need a thin adapter (Adapter Pattern) over
the third-party tool. The error is applying rich domain
modeling to generic subdomains (over-engineering) or
applying CRUD patterns to core subdomains (under-engineering).

**Level 5 - Mastery (distinguished engineer):**
Subdomain boundaries are not static. A capability that
is generic today may become core tomorrow (and vice
versa). Example: fraud detection was generic for small
fintechs (use third-party rules engines). As transaction
volume grew and fraud patterns became more sophisticated,
fraud detection became a core subdomain requiring
custom ML models. The migration: start with Stripe
Fraud (generic/SaaS), accumulate transaction data,
build internal ML model, eventually sunset Stripe Fraud.
This evolution requires the boundary to be drawn so
that the generic-to-core migration is possible without
affecting other services (Bounded Context isolation).

---

### ⚙️ How It Works (Mechanism)

**SUBDOMAIN CLASSIFICATION PROCESS:**

```
STEP 1: DOMAIN DISCOVERY (Event Storming)
  Map all domain events in 2-day workshop
  Identify aggregates, bounded contexts
  Output: context map showing all subdomains

STEP 2: CLASSIFY EACH SUBDOMAIN
  For each bounded context:
  Q1: Is this our unique competitive advantage?
      -> Yes: CORE subdomain
  Q2: Can we buy an off-the-shelf solution today?
      -> Yes: GENERIC subdomain  
  Q3: Is it needed but neither core nor generic?
      -> SUPPORTING subdomain

STEP 3: INVESTMENT DECISION
  Core:      -> Build custom, richly modeled service
             -> Best engineers, DDD aggregates
             -> High test coverage, documentation
  Supporting -> Build simply (CRUD, standard patterns)
             -> Mid-level engineers, pragmatic approach
             -> Candidate for buy as SaaS matures
  Generic    -> Buy (SaaS/library)
             -> Thin adapter + configuration
             -> Replace freely: it's a commodity

STEP 4: BUILD ANTI-CORRUPTION LAYERS
  For generic/third-party: wrap in ACL
  Isolates services from third-party APIs
  Migration: swap vendor without changing consumers
```

---

### 🔄 The Complete Picture - End-to-End Flow

**E-COMMERCE SUBDOMAIN MAP:**

```
CORE SUBDOMAINS (build, invest):
  Personalization Engine
    -> recommendation-service (in-house ML team)
    -> user-behavior-service (custom event tracking)
  Dynamic Pricing
    -> pricing-engine-service (PhD-level ML model)
    -> competitor-price-monitor (custom crawler)

SUPPORTING SUBDOMAINS (build, simply):
  Order Management
    -> order-service (standard CRUD + workflow)
  Inventory
    -> inventory-service (standard stock tracking)
  Customer Profile
    -> profile-service (standard data management)

GENERIC SUBDOMAINS (buy):
  Authentication -> Auth0
    Service: auth-adapter (thin wrapper for token
      validation)
  Email -> SendGrid
    Service: notification-service (adapter over SendGrid)
  Payment Processing -> Stripe
    Service: payment-service (ACL over Stripe API)
  File Storage -> AWS S3
    Service: storage-service (thin S3 wrapper)
  Full-text Search -> Elasticsearch
    Service: search-service (Elasticsearch + index mgmt)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: treating generic as core**

```java
// BAD: Building custom authentication (Generic subdomain)
// 3 months of engineering to build JWT auth from scratch
// Ongoing: security patches, PKCE, MFA, SSO support
// Competitor uses Auth0 ($500/month)
// -> competitor spent 3 months building better
//    recommendation engine (Core subdomain)
@Configuration
public class CustomAuthConfig {
    // 5000 lines of JWT, session management,
    // password hashing, MFA, SSO integration...
    // Every line is NOT spent on core domain
}
```

```java
// GOOD: Generic subdomain -> buy; invest in core

// Generic: authentication via Auth0
// 2 weeks to integrate, not 3 months to build
@Component
public class Auth0TokenValidator {
    // Thin ACL over Auth0
    public DecodedJWT validate(String token) {
        return JWT.decode(token); // Auth0 public key verify
    }
}

// Core: recommendation engine (same 3 months)
// -> competitive advantage
@Service
public class PersonalizationEngine {
    // Custom ML model trained on user behavior
    // This is where your engineering talent creates value
    public List<Product> recommend(
            UserId userId, ProductContext context) {
        // Your proprietary algorithm here
        // No off-the-shelf tool does this for your domain
        return mlModel.predict(userId, context);
    }
}
```

---

### ⚖️ Comparison Table

| Subdomain Type | Investment | Build/Buy | Team Level | Examples |
|---|---|---|---|---|
| **Core** | Maximum | Build custom | Senior/Staff | Pricing, Recommendations, Fraud Detection |
| **Supporting** | Moderate | Build simply | Mid-level | Order Management, Notifications |
| **Generic** | Minimal | Buy (SaaS) | DevOps/Config | Auth, Email, Payments |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Subdomain classification is permanent | Classification changes as the business evolves. Fraud detection was generic for most companies 10 years ago; now many large fintechs treat it as core. Regularly re-evaluate: is our core subdomain still core? Is a supporting subdomain mature enough for a SaaS solution? |
| Generic means unimportant | Generic means commodity - it's still critical to operations. Authentication being generic doesn't mean it can be down. It means the DECISION to build vs buy: Auth0 has better uptime SLAs than most in-house auth systems. Generic = buy the best commodity. |
| Every subdomain needs a microservice | Generic subdomains often don't need a service at all - just a library call or direct SaaS integration. Only build a service adapter when you need isolation from the third-party API (vendor swap protection). |

---

### 🚨 Failure Modes & Diagnosis

**Building custom for generic subdomain (over-engineering)**

**Symptom:**
Team spent 4 months building a custom notification
system (email, SMS, push). The system handles 10,000
notifications/day. Engineering is now maintaining:
custom SMTP handling, SMS gateway integrations,
handlebars templates, bounce handling, unsubscribe
management. Three engineers are permanently dedicated.

**Root Cause:**
Notification is a generic subdomain. SendGrid, SES,
and Twilio handle exactly these requirements at scale.
The 4-month build and 3-engineer maintenance is a
resource misallocation: those engineers could be
working on the core recommendation engine.

**Diagnostic:**
```
Misallocation check:
1. Does this subdomain directly create revenue or
   competitive advantage? Notification -> No.
   (Customers don't choose us because of our email system)
2. Does a mature SaaS exist? SendGrid, SES -> Yes.
3. What is the maintenance cost? 3 engineers = $600K/year
4. What is the SaaS cost? SendGrid at 10K emails/day:
  ~$200/month
5. Delta: $600K engineering vs $2,400/year SaaS
   Engineering opportunity cost: 3 engineers on core domain
```

**Fix:**
1. Replace custom notification with SendGrid/SES
2. Build thin ACL: NotificationPort interface,
   SendGridAdapter implementation
3. Migrate templates to SendGrid
4. Decommission custom system
5. Redeploy 3 engineers to core subdomain work

---

### 🔗 Related Keywords

**Prerequisites:**
- `Domain-Driven Design (DDD)` - subdomains are a DDD
  strategic design concept
- `Bounded Context` - each subdomain contains one or
  more bounded contexts
- `Decomposition by Business Capability` - capability-based
  decomposition; subdomains and capabilities often align

**Organisational:**
- `Conway's Law in Microservices` - team structure
  should match subdomain ownership
- `Team Topologies` - stream-aligned teams on core
  subdomains; platform teams on generic subdomains

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE         │ Competitive advantage -> Build custom    │
│ SUPPORTING   │ Necessary, not unique -> Build simply    │
│ GENERIC      │ Commodity -> Buy off-the-shelf           │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Every hour on generic = hour NOT on core │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Classify subdomains: build only what    │
│              │  differentiates; buy the commodity"      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Conway's Law -> Team Topologies          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Three types: Core (unique, build), Supporting (necessary,
   build simply), Generic (commodity, buy).
2. Build custom ONLY for core subdomains. Every hour
   spent on generic/supporting is an hour not spent on
   competitive differentiation.
3. Classification changes: a generic subdomain can
   become core as scale and competition change. Review
   annually.

**Interview one-liner:**
"Decomposition by Subdomain uses DDD's Core/Supporting/Generic
classification. Core subdomains (competitive advantage:
pricing algorithm, fraud detection) get rich custom
microservices and the best engineers. Generic subdomains
(commodity: auth, email, payments) use SaaS/off-the-shelf
with thin ACL adapters. This drives the build-vs-buy
decision: every engineering hour spent on Auth0-replaceable
authentication is an hour NOT spent on the pricing engine
that wins customers."

---

### 💡 The Surprising Truth

The most counterintuitive lesson from subdomain decomposition:
"generic" doesn't mean "easy to replace". Authentication
is generic (it's a commodity), but migrating from a
custom-built auth system to Auth0 is a 3-month project
because every service that validates tokens is coupled
to the implementation. This is why Anti-Corruption
Layer matters even for generic subdomains: wrap Auth0
behind a port (interface), not called directly. When
you decide to switch from Auth0 to Cognito: change
one adapter, not 15 services. The ACL is the insurance
policy for the "generic is replaceable" promise.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CLASSIFY** Given a list of 20 proposed services,
   classify each as Core, Supporting, or Generic; justify
   each classification.
2. **INVEST** Allocate a team of 20 engineers across a
   subdomain map: how many on core, supporting, generic?
3. **BUY vs BUILD** Given a specific subdomain (e.g.,
   "full-text search"), make the build-vs-buy case with
   cost analysis.
4. **EVOLVE** Describe how a generic subdomain becomes
   core over time. Give a real example. What triggers
   the reclassification?
5. **ACL** Design the ACL that wraps a generic subdomain
   vendor so that migrating vendors requires changing
   only one class.

---

### 🧠 Think About This Before We Continue

**Q1.** A Series B startup has 25 engineers building
a B2B SaaS HR platform. They have built custom:
authentication, email service, PDF generation, and
their core product (workforce analytics). Classify
these four as Core/Supporting/Generic and calculate
the opportunity cost of the wrong classifications.

**Q2.** Netflix's recommendation engine was a generic
subdomain in 2005 (they used a third-party recommendation
engine). Today it is a massive core subdomain. What
event or scale threshold typically triggers the
classification change from generic to core?

**Q3.** Your company has decided to build a custom
ML-based fraud detection system (previously used a
third-party rules engine). Design the migration from
generic to core: how do you run both in parallel? How
do you validate the new system? How do you retire the
generic solution? What are the service boundaries?