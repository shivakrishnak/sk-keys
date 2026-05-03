---
layout: default
title: "Build vs Buy vs Outsource"
parent: "Behavioral & Leadership"
nav_order: 1757
permalink: /leadership/build-vs-buy-vs-outsource/
number: "1757"
category: Behavioral & Leadership
difficulty: ★★★
depends_on: Engineering Strategy, Technical Roadmap
used_by: Engineering Strategy, Technical Roadmap, OKRs
related: Engineering Strategy, Technical Roadmap, OKRs
tags:
  - leadership
  - strategy
  - advanced
  - build-vs-buy
  - decision-making
---

# 1757 — Build vs Buy vs Outsource

⚡ TL;DR — Build vs Buy vs Outsource is a recurring architectural and strategic decision framework that determines whether a capability should be internally developed (Build), purchased from a vendor (Buy), or delivered by an external team or agency (Outsource) — the decision hinges on whether the capability is a core differentiator vs. commodity, the real total cost of ownership (TCO) including hidden operational costs, vendor lock-in risk, and how much control the organisation needs over the capability's evolution.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineering teams build everything from scratch — authentication, search infrastructure, email delivery, payment processing — because "we can build it ourselves" and "we'll have more control." Result: 80% of engineering effort is spent on undifferentiated, commodity work. The authentication system the team built has 4 known vulnerabilities. The email delivery service the team maintains has a 92% delivery rate (Mailgun: 99%+). The team is so busy maintaining infrastructure they built that they can't ship the features customers actually need. Meanwhile: the competition has shipped a product that is genuinely better in the ways customers care about.

**THE BREAKING POINT:**
The inverse error also exists: buying everything means vendor dependency and eventual commoditisation of capabilities that were actually differentiating. The organisation that outsourced its recommendation algorithm to a vendor discovers the vendor can't iterate fast enough to match competitive requirements, and switching costs are enormous.

**THE INVENTION MOMENT:**
The build-or-buy question has existed as long as organisations have faced it. The analytical framework evolved through software architecture practice. The "core vs context" framework (Geoffrey Moore, "Dealing with Darwin," 2005) provides the foundational concept: core capabilities drive competitive differentiation and should be built; context capabilities are necessary but not differentiating and should be bought.

---

### 📘 Textbook Definition

**Build:** Internally develop and maintain the capability using the organisation's own engineering team. Requires time, people, and ongoing maintenance. Provides maximum control and customisation. Cost: high initial investment + ongoing maintenance burden.

**Buy:** Purchase a vendor product, SaaS, or open-source solution. Provides faster time-to-value, proven reliability, and reduced maintenance burden. Cost: licensing/subscription fees + vendor dependency + integration overhead.

**Outsource:** Engage an external agency or contractor team to develop the capability. Provides access to specialised skills without permanent headcount. Cost: contractor rates + coordination overhead + quality risk + knowledge transfer cost.

**Total Cost of Ownership (TCO):** The real cost of a capability over its lifetime, including: initial development/licensing cost, ongoing maintenance (engineering time), operational cost (infrastructure), upgrade and migration cost, and opportunity cost (what else could the team be building?).

**Vendor lock-in:** The degree to which switching away from a vendor is expensive. High lock-in: proprietary data formats, deep API integration, vendor-specific features. Low lock-in: open standards, data portability, thin integration layer.

**Core vs Context (Moore):**

- **Core:** capabilities that directly differentiate you from competitors; customers would pay more for excellence here
- **Context:** necessary capabilities that customers expect as a baseline but don't differentiate; commodity work

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Build when the capability differentiates you from competitors; buy when it is commodity work that vendors do better and cheaper; outsource when you need temporary specialised skills without permanent headcount — and always calculate TCO honestly, including operational overhead and opportunity cost.

**One analogy:**

> A restaurant doesn't build its own ovens or make its own plates. Those are commodity inputs — industrial manufacturers produce them better and cheaper than any restaurant could. But the restaurant does develop its own recipes, train its own chefs, and create its own dining experience — because those are the differentiating capabilities that determine whether customers choose this restaurant over the one across the street. "Build vs Buy" is the same question: what is your oven (buy it), and what is your recipe (build it)? The mistake is spending chef time on oven manufacturing.

**One insight:**
The hidden cost of building is almost always maintenance. An authentication system takes 2 months to build and 5 years to maintain securely. The TCO of "we'll build our own auth" vs "use Auth0/$50/month" is rarely favourable to building — unless authentication is your core business. The upfront build cost is visible; the 5-year maintenance burden is invisible until the engineer who built it leaves.

---

### 🔩 First Principles Explanation

**THE DECISION FRAMEWORK:**

```
STEP 1: CORE VS CONTEXT

Is this capability core to our competitive differentiation?
  → Core: customers choose us partly because of excellence here
  → Context: customers expect it as baseline; excellence here
              is invisible; failure is visible

QUESTION: "If we were 10x better at this than any competitor,
           would that drive customer acquisition/retention?"
  Yes → core (strong bias toward Build)
  No  → context (strong bias toward Buy)

EXAMPLES:
  Core (build):
    Netflix: recommendation algorithm (their competitive moat)
    Shopify: checkout experience (core to merchant success)
    Stripe: payment routing and reliability (their product)

  Context (buy):
    Netflix: email delivery → buy (SendGrid/Mailgun)
    Shopify: authentication → buy (Auth0 / Cognito)
    Stripe: internal analytics dashboards → buy (Looker/Grafana)

STEP 2: TCO ANALYSIS (be honest)

BUILD COSTS:
  Initial: [engineers × weeks × loaded_hourly_cost]
  Maintenance: [engineers × hours/year × years × loaded_cost]
  Incident cost: [P1 incidents/year × avg_resolution_time × cost]
  Upgrade cost: [major_upgrades × engineer_weeks × cost]
  Knowledge transfer: [turnover_rate × onboarding_cost]
  Opportunity cost: [what else could these engineers build?]

BUY COSTS:
  Licensing: [$/month × 12 × years]
  Integration: [engineer_weeks × loaded_cost] (one-time)
  Customisation limits: [workarounds × ongoing_engineer_time]
  Vendor risk: [probability_of_vendor_failure × switching_cost]
  Lock-in premium: [migration_cost_if_switching × probability]

OUTSOURCE COSTS:
  Contractor rate: [rate × hours × duration]
  Coordination: [internal_engineer_hours × loaded_cost]
  Quality review: [review_cycles × engineer_time × cost]
  Knowledge transfer: [documentation + pairing cost]
  Re-engagement: [cost_to_re-engage_if_changes_needed]

STEP 3: CONTROL REQUIREMENTS

How much do you need to control this capability's evolution?
  High control need:
    - Changes needed faster than vendors can provide
    - Security requirements exceed what vendor can offer
    - Deep integration with proprietary internal systems
  Low control need:
    - Vendor roadmap aligns with your needs
    - Commodity capability unlikely to need customisation
    - Vendor reliability SLA exceeds what you'd achieve

STEP 4: VENDOR RISK ASSESSMENT

  Lock-in level:
    Low: open standards, data portability, thin integration
    High: proprietary APIs, vendor-specific data formats

  Vendor stability:
    Is this a well-capitalised, mature vendor?
    What is the switching cost if the vendor is acquired/shut down?
    Is there a viable open-source alternative as an escape hatch?

STEP 5: TEAM CAPABILITY

  Do we have the skills to build and maintain this?
    No expertise → strong bias toward Buy
    Deep expertise → Build is more viable

  Can we maintain it safely?
    Security-critical (auth, payments, encryption):
    Unless this is your core business, the maintenance
    burden and security risk of building internally is high.
```

---

### 🧪 Thought Experiment

**SETUP:**
A 15-person Series A startup needs a search capability for their product (a developer tooling platform). Two senior engineers are debating:

**Engineer A — Build:** "Elasticsearch is complex to operate. We'll build a simple inverted index — it'll take 3 weeks and we'll have full control."

**Engineer B — Buy:** "Algolia is $500/month. We spend 3 weeks building, then maintain it forever. Our core differentiator is the IDE integration, not search infrastructure."

**TCO analysis:**

```
BUILD option:
  Initial: 3 weeks × 2 engineers = 6 engineer-weeks = ~$18,000
  Annual maintenance: 2h/week × 2 engineers × $150/h × 52 weeks = $31,200/year
  3-year TCO: $18,000 + (3 × $31,200) = ~$111,600
  Opportunity cost: 3 engineer-weeks of IDE integration not built

BUY (Algolia) option:
  Integration: 1 week × 1 engineer = $7,500 (one-time)
  Annual: $500/month × 12 = $6,000/year
  3-year TCO: $7,500 + (3 × $6,000) = ~$25,500
  Opportunity cost: 1 engineer-week of IDE integration not built

BUILD wins only if:
  - Algolia fails in a way that disrupts your business
  - You need customisation Algolia can't provide
  - Search is your core differentiator (unlikely for a dev tools startup)
```

**Verdict:** Buy. The 3-year TCO delta ($111,600 vs $25,500) pays for two additional engineer-months of work on actual differentiating capabilities. Unless search IS the product, build is the wrong choice here.

---

### 🧠 Mental Model / Analogy

> Build vs Buy is a make-or-buy analysis from manufacturing. Toyota manufactures its own powertrains because engine performance is core to Toyota's competitive identity. But Toyota doesn't manufacture its own seat fabric, radio units, or tyres — those are commodities where suppliers have better economies of scale, more expertise, and lower unit costs. Toyota's competitive advantage is in powertrains (build) + supply chain management (build) + assembly quality (build). Everything else: buy from best-in-class suppliers. Engineering teams should apply the same logic: what is your powertrain (build it), and what is your seat fabric (buy it)?

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your team needs a capability, you have three options: build it yourself, buy a product that provides it, or hire an outside team to build it. The right choice depends on: whether this capability is what makes you special compared to competitors (if yes: build), how much it would really cost to build vs buy over several years (including maintenance), and how much control you need over how it evolves.

**Level 2 — How to use it (engineer):**
When you propose building something new: run the TCO calculation. Include maintenance time — not just initial build time. Ask: "Is this capability core to our competitive differentiation?" If not: find the best vendor and evaluate integration effort vs. cost. Present both options (build vs buy) in the RFC with honest TCO estimates. Engineers systematically underestimate maintenance burden — it's the cost you don't feel until year 2.

**Level 3 — How it works (tech lead):**
At the tech lead level, the build-vs-buy decision feeds directly into the engineering strategy. Every engineering strategy should contain a guiding policy for the build/buy decision — so individual engineers aren't relitigating it for every capability. Example policy: "Build when: (a) the capability is core to competitive differentiation; (b) no vendor meets our reliability requirements; (c) TCO analysis favours build over 3 years. Buy otherwise." The policy should resolve 80% of decisions; the remaining 20% are escalated.

**Level 4 — Why it was designed this way (principal/staff):**
At the principal/staff level, the build-vs-buy decision is a strategic question about focus and leverage. Every capability built internally consumes engineering capacity that could be applied to core differentiating work. The opportunity cost of "we built our own auth system" is not just the $100k in engineering time — it's the features that weren't built, the bugs that weren't fixed, the customers who were slower to convert because the product didn't move fast enough. Opportunity cost is the most important cost in the build-vs-buy decision, and it is the most systematically underestimated. The principal engineer's job is to make opportunity cost visible: "If we build this ourselves, what are we not building? Is that tradeoff worth it given our current situation?"

---

### ⚙️ How It Works (Mechanism)

```
BUILD VS BUY VS OUTSOURCE DECISION PROCESS:

IDENTIFY CAPABILITY REQUIREMENT
  "We need [capability X] to achieve [outcome Y]"
    ↓
CORE VS CONTEXT CHECK
  Is this capability core to competitive differentiation?
  → Core: default BUILD
  → Context: evaluate BUY options first
    ↓
OPTION IDENTIFICATION
  Build: team builds internally
  Buy (SaaS): managed vendor product
  Buy (OSS): open-source + self-host
  Outsource: external agency/contractor
    ↓
TCO ANALYSIS (each option)
  Initial cost + ongoing cost × years + opportunity cost
    ↓
CONTROL ASSESSMENT
  How much customisation control do we need?
  How fast do we need to iterate on this?
    ↓
VENDOR RISK ASSESSMENT
  Lock-in level; vendor stability; exit strategy
    ↓
RECOMMENDATION + RFC
  Present options with honest TCO
  Recommend with explicit reasoning
  Note key risks for each option
    ↓
DECISION + ENGINEERING STRATEGY UPDATE
  If pattern: add to engineering strategy as a guiding policy
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Business need identified (product / engineering)
    ↓
[BUILD vs BUY vs OUTSOURCE ← YOU ARE HERE]
Core vs context analysis
    ↓
Option identification (build / buy / OSS / outsource)
    ↓
TCO analysis per option
    ↓
Control + vendor risk assessment
    ↓
RFC or architecture decision record (ADR)
    ↓
Decision made → Engineering strategy updated
    ↓
If BUILD: work enters roadmap as initiative
If BUY: procurement + integration work in roadmap
If OUTSOURCE: SOW + onboarding + handoff plan
    ↓
Ongoing: monitor TCO; reassess at major context change
```

---

### 💻 Code Example

**Build vs Buy TCO calculator:**

```python
from dataclasses import dataclass

LOADED_HOURLY_RATE = 150  # USD; adjust per team

@dataclass
class BuildOption:
    name: str
    initial_weeks: float       # engineer-weeks to build
    maintenance_hours_per_week: float   # ongoing maintenance
    engineers_on_maintenance: int
    years: int = 3

    def initial_cost(self) -> float:
        return self.initial_weeks * 40 * LOADED_HOURLY_RATE

    def maintenance_cost(self) -> float:
        return (self.maintenance_hours_per_week
                * self.engineers_on_maintenance
                * LOADED_HOURLY_RATE
                * 52
                * self.years)

    def tco(self) -> float:
        return self.initial_cost() + self.maintenance_cost()

@dataclass
class BuyOption:
    name: str
    integration_weeks: float   # engineer-weeks to integrate
    monthly_cost: float        # vendor cost
    years: int = 3

    def integration_cost(self) -> float:
        return self.integration_weeks * 40 * LOADED_HOURLY_RATE

    def subscription_cost(self) -> float:
        return self.monthly_cost * 12 * self.years

    def tco(self) -> float:
        return self.integration_cost() + self.subscription_cost()

def compare_options(*options, years: int = 3) -> None:
    print(f"\nTCO Comparison ({years}-year)\n" + "=" * 50)
    results = sorted(options, key=lambda o: o.tco())
    for opt in results:
        print(f"  {opt.name:<30} ${opt.tco():>10,.0f}")
    winner = results[0]
    print(f"\n  Recommendation: {winner.name} (lowest TCO)")

compare_options(
    BuildOption(
        name="Build custom search",
        initial_weeks=3,
        maintenance_hours_per_week=2,
        engineers_on_maintenance=1,
    ),
    BuyOption(
        name="Buy Algolia",
        integration_weeks=1,
        monthly_cost=500,
    ),
    BuyOption(
        name="Buy Elasticsearch (managed)",
        integration_weeks=2,
        monthly_cost=300,
    ),
)
```

---

### ⚖️ Comparison Table

|                   | Build                | Buy (SaaS)             | Buy (OSS Self-Host) | Outsource                  |
| ----------------- | -------------------- | ---------------------- | ------------------- | -------------------------- |
| **Time to value** | Slowest              | Fastest                | Medium              | Medium                     |
| **Control**       | Highest              | Lowest                 | High                | Medium                     |
| **Maintenance**   | Highest (internal)   | None                   | Medium (ops burden) | Low (then high at handoff) |
| **Cost**          | High TCO             | Predictable opex       | Medium TCO          | High (per project)         |
| **Vendor risk**   | None                 | High                   | Low                 | Medium                     |
| **Best for**      | Core differentiators | Commodity capabilities | Between build/SaaS  | Specialised, temporary     |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                        |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Building gives more control"                | Building gives control in the short term and a maintenance burden forever. Vendor products often evolve faster than internal builds because they have dedicated teams.                                                         |
| "Vendor costs are high compared to building" | Vendor costs are visible; build costs (maintenance, incidents, upgrades, opportunity cost) are mostly invisible until year 2. TCO analysis almost always favours buying commodity capabilities.                                |
| "Open source is free"                        | Open-source software has no licensing cost but has operational cost (hosting, upgrades, security patches, oncall), integration cost, and the risk of abandoned projects. "Free" OSS has a real TCO.                            |
| "Outsourcing is cheaper"                     | Outsourcing has high coordination overhead, quality risk, and a handoff cost that makes it expensive for ongoing capabilities. It's most cost-effective for well-scoped, time-limited projects with clear acceptance criteria. |
| "We should own our core infrastructure"      | "Core infrastructure" is often context, not core. Unless your competitive advantage is infrastructure, managed infrastructure (RDS vs self-hosted Postgres, EKS vs self-hosted Kubernetes) almost always has lower TCO.        |

---

### 🚨 Failure Modes & Diagnosis

**"Not Invented Here" Syndrome — Building Commodity Capabilities**

**Symptom:** The team has built (and maintains): their own authentication system (1 engineer-month to build; 3h/week to maintain); their own email delivery service (P1 incident once a quarter; 94% delivery rate vs. 99%+ for SendGrid); their own feature flag system (reasonable, but reinventing LaunchDarkly); their own analytics event pipeline (instead of Segment). 40% of engineering capacity is spent maintaining infrastructure that vendors provide as a service for $2,000/month total. The feature backlog is 18 months long.

**Root Cause:** No principled build-vs-buy framework. Each capability was built because an engineer had an afternoon, or because "we can build this ourselves," or because the team didn't evaluate vendor options. TCO was never calculated. Opportunity cost was never made visible.

**Fix:**

```
1. AUDIT EXISTING INTERNAL TOOLS:
   List every internal capability the team maintains
   For each: estimate annual maintenance hours × loaded cost
   For each: find best-in-class vendor; get pricing
   Calculate 3-year build TCO vs buy TCO

2. IDENTIFY QUICK WINS:
   Capabilities where buy TCO < build TCO by > 50%
   AND not core to competitive differentiation
   → These are candidates for replacement

3. MIGRATION PLAN (for top 3 quick wins):
   Integration effort; data migration; cutover plan
   Stop maintaining internal version after cutover

4. ADD BUILD-VS-BUY POLICY TO ENGINEERING STRATEGY:
   "Default: evaluate best-in-class vendor before building.
    Build only if: (a) core differentiator; (b) no vendor
    meets reliability requirements; (c) TCO analysis over
    3 years favours build."

5. RFC TEMPLATE INCLUDES:
   "What vendor/OSS options were evaluated?"
   "What is the 3-year TCO comparison?"
   "Why does this capability require building internally?"
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Engineering Strategy` — the build-vs-buy decision should be a guiding policy in the engineering strategy
- `Technical Roadmap` — build/buy decisions determine what goes on the roadmap

**Builds On This (learn these next):**

- `Engineering Strategy` — the build/buy/outsource policy belongs in the engineering strategy
- `Technical Roadmap` — decisions feed directly into initiative prioritisation
- `OKRs` — the opportunity cost of building vs buying affects which OKRs can be achieved

**Alternatives / Comparisons:**

- `Engineering Strategy` — strategy provides the context; build-vs-buy is one recurring decision type the strategy should resolve

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE TEST   │ "If 10x better, would customers pay more?" │
│             │ Yes → Build. No → Buy.                    │
├─────────────┼──────────────────────────────────────────-─┤
│ TCO         │ Build: initial + maintenance + opportunity │
│             │ Buy: integration + subscription            │
│             │ Maintenance always underestimated.        │
├─────────────┼──────────────────────────────────────────-─┤
│ BUILD WHEN  │ Core differentiator; no vendor meets SLA; │
│             │ TCO favours build over 3 years            │
├─────────────┼──────────────────────────────────────────-─┤
│ BUY WHEN    │ Commodity capability; vendor TCO better;  │
│             │ low customisation need                    │
├─────────────┼──────────────────────────────────────────-─┤
│ OUTSOURCE   │ Time-limited; specialised skills needed;  │
│ WHEN        │ clear scope; knowledge transfer planned   │
├─────────────┼──────────────────────────────────────────-─┤
│ NEXT EXPLORE│ Engineering Strategy →                    │
│             │ Technical Roadmap                        │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 50-person startup is evaluating whether to build or buy a real-time notification system (email, push, in-app). The team's current pain: they send about 2M notifications/month; their in-house system has 87% delivery rate and breaks monthly. A senior engineer proposes rebuilding it from scratch with a better architecture. The VP of Engineering proposes moving to a vendor (Courier.com or Braze). Conduct a full build-vs-buy analysis: calculate TCO for both options (make reasonable assumptions and state them explicitly), assess lock-in risk, assess maintenance burden, and make a recommendation. Defend it against the strongest counterargument.

**Q2.** "We should own our search capability because search is core to our user experience" is an argument often made for building internally. But Netflix owns recommendation (core differentiator) while buying search infrastructure (Elasticsearch). Shopify owns checkout (core) but buys fraud detection (vendor). Identify the principle that explains when "core to user experience" is a valid reason to build vs. when it is a rationalisation for "Not Invented Here" syndrome. Apply that principle to three specific capabilities in a hypothetical e-commerce company and justify whether each should be built or bought.
