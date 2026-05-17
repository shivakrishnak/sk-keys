---
id: OBS-013
title: "SLA (Service Level Agreement)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-011, OBS-012
used_by:
related: OBS-011, OBS-012, OBS-020
tags:
  - observability
  - reliability
  - foundational
  - sre
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /obs/sla-service-level-agreement/
---

# OBS-013 - SLA (Service Level Agreement)

⚡ TL;DR - An SLA is the customer-facing contractual
promise about service reliability, always looser than
the internal SLO to provide buffer, with defined
financial consequences for breach.

| #013            | Category: Observability & SRE     | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------- | :-------------- |
| **Depends on:** | SLI, SLO                          |                 |
| **Used by:**    | (external customer relationships) |                 |
| **Related:**    | SLI, SLO, Error Budget            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An enterprise customer pays $500,000/year for a payment
processing platform. The platform experiences 6 hours
of degradation in one month. The customer demands a
refund. The vendor says: "We had an incident but our
terms say 'best effort reliability.'" The customer has
no recourse. Trust is destroyed. The contract is not
renewed. Without an SLA, there is no agreed measure
of "good enough service" and no consequence for
failing to deliver it.

**WHY IT MATTERS:**
An SLA creates a contractual measurement framework.
Both parties agree upfront: what is measured (the SLI),
what target is required (the SLO in contractual form),
what constitutes a breach (measured against the SLA
threshold), and what compensation is provided (service
credits, termination rights).

---

### 📘 Textbook Definition

**A Service Level Agreement (SLA)** is a contractual
commitment between a service provider and a customer
that specifies the minimum reliability level the
provider guarantees to deliver, along with the
consequences (service credits, penalties) if the
guarantee is not met.

**SLA structure:**

- **Metric:** what is measured (availability %, P99
  latency, data freshness)
- **Target:** the contractual minimum (e.g., 99.5%)
- **Measurement period:** monthly, quarterly, or annual
- **Exclusions:** planned maintenance windows, force
  majeure events, customer-caused failures
- **Remedy:** service credits (typically 10-30% of
  monthly fee per 0.1% availability below target)

**SLA vs SLO vs SLI:**

```
SLI  → the measurement (current availability: 99.93%)
SLO  → internal target (internal goal: 99.9%)
SLA  → customer contract (external promise: 99.5%)

Relationship: SLI >= SLO >= SLA (always)
Buffer:       SLO - SLA >= 0.1% (provides operational
              margin before contractual breach)
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An SLA is the reliability promise written into a
customer contract - always looser than what your
internal SLO targets, with service credits as the
consequence of breaking it.

> Think of an airline selling Business Class seats.
> The ticket says "guaranteed to arrive within 2 hours
> of scheduled time or full refund." This is the SLA.
> Internally, the airline targets "arrive within 30
> minutes of scheduled time" - the SLO. The SLA
> guarantee is loose enough that the airline almost
> never needs to issue refunds. The internal SLO keeps
> operations disciplined. Customers see the SLA;
> operations runs against the SLO.

**One insight:**
The SLA threshold must always be meaningfully below
the SLO target. If they are equal, the team has no
buffer: every SLO breach is an SLA breach - a
contractual failure with financial consequences. The
gap between SLO and SLA is the "safety margin."

---

### 🔩 First Principles Explanation

**THE SLA HIERARCHY:**

```
Internal SLI target (aspirational): 99.97%
     ↓ (operational buffer)
Internal SLO target: 99.9%
     ↓ (contractual buffer)
Customer SLA: 99.5%
     ↓ (legal minimum, breach = penalty)
Worst-case SLA with exclusions: ~98.5%
```

**WHY THE MULTIPLE LAYERS:**

- SLO breach (99.9% target missed): internal alarm,
  deployment freeze, reliability sprint. No external
  consequence.
- SLA breach (99.5% target missed): contractual
  consequence. Service credits are issued. Customer
  relationship is affected.
- The gap (99.9% SLO - 99.5% SLA = 0.4%) means the
  team can have multiple SLO breaches and reliability
  incidents in a month before the SLA is at risk.

**THE EXCLUSION CHALLENGE:**
SLAs typically exclude:

- Planned maintenance windows (announced in advance)
- Force majeure (acts of God, major infrastructure
  failures outside provider's control)
- Customer-caused failures (misconfigured client,
  DDoS attack originating from customer network)

The challenge: agreeing on what counts as an exclusion
is often contentious. A cloud provider experiencing
a region outage may argue it is an infrastructure
failure outside their control. The customer argues
the provider is responsible for their infrastructure
resilience.

**TRADE-OFFS:**
**Tight SLA (99.99%):**
Competitive differentiation. Attracts enterprise
customers who need reliability guarantees. Requires
significant engineering investment. High financial
risk if breached.

**Loose SLA (99%):**
Low financial risk. Less competitive for enterprise.
May attract only cost-sensitive customers who do not
care about reliability.

---

### 🧪 Thought Experiment

**SETUP:**
Two cloud storage vendors compete for the same $2M/year
enterprise contract.

**Vendor A:**
SLA: 99.9% availability/month. Service credit: 10%
of monthly fee per 0.1% below target.
Measurement: request success rate measured by vendor's
internal monitoring.

**Vendor B:**
SLA: 99.5% availability/month. Service credit: 25%
of monthly fee per 0.1% below target (up to 100%).
Measurement: measured by independent third-party
probe from customer's network.

**THE DEBATE:**
Vendor A has a better availability target (99.9% vs
99.5%) but lower credit (10%) and measures from their
own infrastructure (self-reported). Vendor B's target
is weaker but the remedy is stronger (25%) and the
measurement is independent.

**ANALYSIS:**
An enterprise customer might prefer Vendor B: the
independent measurement is more trustworthy (no
conflict of interest), and the higher credit rate
provides real financial protection if the SLA is
breached. The 99.5% vs 99.9% difference amounts to:
99.9% = 43.2 min/month vs 99.5% = 3.6 hours/month -
a meaningful difference for critical systems.

**THE INSIGHT:**
SLA negotiation is not just about the threshold. The
measurement method, the exclusions list, and the
remedy structure are equally important. A 99.9% SLA
with weak measurement and low credits may be worth
less to a customer than a 99.5% SLA with independent
measurement and strong credits.

---

### 🧠 Mental Model / Analogy

> A car manufacturer offers a warranty: "free repairs
> for manufacturing defects for 3 years or 36,000 miles."
> This is the SLA - a contractual promise to the
> customer with a defined measurement (defect?), scope
> (manufacturing vs owner damage), and remedy (free
> repair). Internally, the manufacturer's quality
> standards target a much lower defect rate than the
> warranty threshold - that is the SLO. The warranty
> does not represent the manufacturer's internal quality
> target; it represents the minimum acceptable quality
> that the customer can hold them legally accountable for.

The SLA, like a warranty, defines the floor of quality,
not the ceiling. A good manufacturer (or service
provider) rarely triggers the warranty (or SLA credits)
because their internal standards are well above the
contractual floor.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
An SLA is a promise in a contract. If the service is
not as reliable as promised, the customer gets money
back or can leave the contract.

**Level 2 - How to use it (engineer):**
When building a service with an SLA, the internal SLO
must be set tighter than the SLA. Monitor the SLI
continuously. If the SLI approaches the SLA threshold,
alert immediately - an SLA breach has financial
consequences.

**Level 3 - How it works (mid-level):**
SLA compliance is typically measured monthly. The SLA
report computes availability (or latency) over the
calendar month. Planned maintenance windows are excluded.
If the measured availability is below the SLA threshold,
the provider issues service credits automatically or
the customer requests them per the contract terms.

**Level 4 - Why it matters (senior/staff):**
The most important SLA design decision is the measurement
method. A vendor that measures availability from their
internal health check (which may not reflect customer-
facing failures) is self-reporting. A customer-side
probe (synthetic monitoring from the customer's network)
measures what the customer actually experiences. In
enterprise contracts, negotiating for independent or
customer-side measurement is a key protection.
Additionally, SLA exclusions are a significant source
of dispute. Tight exclusion language protects the
customer ("provider infrastructure failures are not
excluded"); broad exclusions protect the vendor
("any failure not caused by provider's direct systems
is excluded").

**Level 5 - Mastery (distinguished engineer):**
Staff engineers understand that SLAs drive architecture
decisions. If a service must maintain 99.99% SLA,
multi-region active-active deployment is required.
Single-region deployment cannot achieve 99.99% because
AWS us-east-1 has experienced multiple 1-4 hour
regional outages. Engineering for SLA compliance means
designing for the failure modes that can breach the
SLA: data centre failure, DNS failure, cloud provider
region failure. The SLA threshold determines the
required blast radius containment.

---

### ⚙️ How It Works (Mechanism)

**SLA COMPLIANCE MEASUREMENT FLOW:**

```
[Month start: April 1]
  SLA baseline established: 100% compliance
        ↓
[April 8: 45-minute partial outage]
  Availability drops to 98% for 45 minutes
  In context of full month:
  SLI impact = 45/(30x24x60) = 0.1% downtime
  Running SLI = 99.9% → above SLA threshold (99.5%)
        ↓
[April 15: 4-hour degradation (payment partial failure)]
  SLI impact = 240/(30x24x60) = 0.56% downtime
  Running SLI = 99.34% → breaches SLA (99.5%)!
  SRE team ← YOU ARE HERE: SLA breach detected
        ↓
[April 15: Emergency response]
  SLO has been breached for 2 weeks
  SLA breach means credit is due to customer
        ↓
[Month end: SLA report generated]
  Total uptime: 99.34%
  SLA threshold: 99.5%
  Breach: 0.16%
  Credit due: 10% x 0.16/0.1 = 16% of monthly fee
  Customer receives: $26,666 credit on $200,000 bill
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SLA LIFECYCLE:**

```
[Contract negotiation]
  Customer: "We need 99.9% availability"
  Vendor: "We offer 99.5% with 10% credit per 0.1%"
  Agreed: 99.5% SLA, monthly measurement
        ↓
[Engineering sets SLO]
  SLO = 99.9% (buffer above 99.5% SLA)
  Instrumentation: SLI measurement implemented
        ↓
[Normal operations]
  SLI measured continuously
  Monthly SLA report auto-generated from SLI data
        ↓
[SLO breach (but not SLA)]
  SLI drops to 99.7% for 2 days (incident)
  Above SLA threshold - no contractual consequence
  Internal: deployment freeze, post-mortem
        ↓
[SLA breach event]
  SLI drops to 99.2% (major incident)
  Below SLA threshold - credit due
  Customer notified per contract terms
  Credit calculated and applied
        ↓
[Post-breach review]
  Root cause analysis
  Architecture improvements to prevent recurrence
  Contract renewal discussion: was SLA appropriate?
```

---

### 💻 Code Example

**Example 1 - SLA measurement query (monthly compliance):**

```promql
# Monthly SLA compliance: total success rate
# Use increase() over calendar month for SLA reporting
# (different from rate() used in operational alerts)

# Availability SLA compliance
(
  sum(increase(checkout_requests_total{
    status=~"2.."}[30d]))
  / sum(increase(checkout_requests_total{
    status!~"4.."}[30d]))
) * 100
# Returns: 99.93 (availability as %)
# Compare to SLA threshold: 99.5%
```

**Example 2 - SLA breach detection alert:**

```yaml
# Alert when SLA threshold is at risk
# (SLI approaching SLA, not just SLO breach)
groups:
  - name: sla-protection
    rules:
      # Critical: SLI approaching SLA threshold
      # This is a business-level alert (not just SRE)
      - alert: CheckoutSLAAtRisk
        expr: |
          (
            sum(increase(checkout_requests_total{
              status=~"2.."}[30d]))
            / sum(increase(checkout_requests_total{
              status!~"4.."}[30d]))
          ) < 0.997   # SLA is 0.995, alert at 0.997
        labels:
          severity: critical
          escalation: vp-engineering
        annotations:
          summary: "Checkout SLA at risk - SLI approaching SLA"
          description: >-
            Monthly SLI is {{ $value | humanizePercentage }}.
            SLA threshold: 99.5%.
            Immediate action required to prevent SLA breach.
          runbook: "https://wiki/runbooks/sla-breach"
```

**Example 3 - Service credit calculation:**

```python
# Service credit calculation per SLA terms
def calculate_service_credit(
    monthly_fee: float,
    sla_threshold: float,      # e.g. 0.995
    measured_availability: float,   # e.g. 0.992
    credit_rate_per_tenth_percent: float = 0.10
) -> float:
    """
    Calculate service credit owed to customer.
    Credit: credit_rate per 0.1% below SLA threshold.
    """
    if measured_availability >= sla_threshold:
        return 0.0  # SLA not breached - no credit

    breach_amount = sla_threshold - measured_availability
    credit_units = breach_amount / 0.001  # per 0.1%
    credit = monthly_fee * credit_rate_per_tenth_percent\
        * credit_units
    return min(credit, monthly_fee)  # cap at monthly fee

# Example:
# monthly_fee = 100_000
# sla_threshold = 0.995
# measured = 0.992 (breach of 0.3%)
# credit = 100000 * 0.10 * 3 = $30,000
```

---

### ⚖️ Comparison Table

| SLA level | Downtime/month | Engineering requirement                    | Customer tier           |
| --------- | -------------- | ------------------------------------------ | ----------------------- |
| 99.0%     | 7.2 hours      | Single region, basic failover              | Startup, free tier      |
| 99.5%     | 3.6 hours      | Multi-AZ, auto-failover                    | SMB customers           |
| 99.9%     | 43.2 minutes   | Multi-AZ, health checks, fast failover     | Standard enterprise     |
| 99.95%    | 21.6 minutes   | Multi-region active-passive                | Premium enterprise      |
| 99.99%    | 4.3 minutes    | Multi-region active-active, chaos testing  | Financial, regulated    |
| 99.999%   | 26 seconds     | Five-nines engineering, massive investment | Telecom, critical infra |

**Key SLA contract terms to negotiate:**

| Term               | Customer-friendly           | Vendor-friendly                 |
| ------------------ | --------------------------- | ------------------------------- |
| Measurement method | Independent probe           | Vendor self-report              |
| Exclusions         | Narrow (only force majeure) | Broad (infra failures excluded) |
| Credit remedy      | 25-50% of monthly fee       | 5-10% of monthly fee            |
| Credit cap         | 100% of monthly fee         | 10% of monthly fee              |
| Response time SLA  | Part of the SLA             | Separate best-effort            |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                              |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "SLA = SLO"                                         | SLAs are customer contracts; SLOs are internal targets. SLOs must be tighter. If they are equal, every SLO breach is contractually punished - no margin for operational learning.                                                                                                                    |
| "99.9% uptime is five nines"                        | 99.9% = three nines. Five nines = 99.999% = 26 seconds downtime/month. The "nines" count matters enormously for engineering cost.                                                                                                                                                                    |
| "SLA credits are sufficient compensation"           | Service credits (typically 10-30% of monthly fee) rarely cover the customer's actual losses from downtime. Enterprise SLAs are a signalling mechanism and a vendor accountability tool, not full financial compensation.                                                                             |
| "SLAs protect the vendor from unreasonable demands" | SLAs primarily protect the customer - they define the minimum acceptable service. The vendor's protection comes from well-defined exclusions (planned maintenance, force majeure).                                                                                                                   |
| "SLA compliance means great service"                | SLA compliance means the service met the contractual floor. The floor is typically set well below what users actually want. A 99.5% SLA with consistent 99.95% performance is excellent service; consistent 99.51% performance (just above SLA floor) is poor service even if technically compliant. |

---

### 🚨 Failure Modes & Diagnosis

**SLA breach discovered during contract renewal, not in real time**

**Symptom:**
At contract renewal, the customer produces their own
availability records showing 98.9% uptime over the year

- below the 99.5% SLA. The vendor's internal records
  show 99.7%. The discrepancy is $240,000 in disputed
  service credits. The customer threatens contract
  termination.

**Root Cause:**
The vendor measures availability from their internal
health check endpoints. The customer measures from a
synthetic probe in their own network. The vendor's
internal check passed during a period when the customer's
network could not reach the service (CDN misconfiguration).
The measurement disagreement was never detected because
SLA compliance was not monitored in real time.

**Prevention:**
Implement two SLI measurement streams: (1) internal
measurement (from the service's perspective) and (2)
external measurement (synthetic probes from external
networks that simulate customer access). Alert when
the two measurements diverge by > 0.1%. Resolve
discrepancies before they accumulate into a dispute.

---

**Planned maintenance not excluded from SLA calculation**

**Symptom:**
A 4-hour planned maintenance window for database
migration consumed most of the month's SLA budget.
The SLA threshold was breached. Service credits were
issued automatically to customers. The maintenance
was pre-announced 2 weeks in advance. The vendor
contests the credits, arguing planned maintenance
should be excluded.

**Root Cause:**
The SLA contract contains an exclusion for planned
maintenance, but the automated SLA compliance system
was not configured to exclude maintenance windows.
It calculated availability including the maintenance
period.

**Fix:**
Implement a maintenance window annotation system.
All planned maintenance must be registered in advance.
The SLA compliance calculation must filter out
registered maintenance periods from the denominator
(total events).

**Prevention:**
Test the maintenance exclusion logic quarterly with
a simulated maintenance window. Verify that the
SLA compliance report correctly excludes the window.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SLI (Service Level Indicator)` - the measurement
  that SLAs are expressed in terms of
- `SLO (Service Level Objective)` - the internal target
  that must be set tighter than the SLA threshold

**Builds On This (learn these next):**

- `Error Budget` - the operational consequence of the
  SLO/SLA framework

**Alternatives / Comparisons:**

- `SLO` - the internal equivalent of the SLA. SLOs
  drive daily operations; SLAs drive business
  relationships. Same concept, different audience.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Customer-facing contractual reliability   │
│              │ promise with defined breach remedies      │
├──────────────┼───────────────────────────────────────────┤
│ HIERARCHY    │ SLI (measurement) → SLO (internal target) │
│              │ → SLA (customer contract, loosest)        │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ SLO must be tighter than SLA by >= 0.1%   │
│              │ to provide operational buffer             │
├──────────────┼───────────────────────────────────────────┤
│ BREACH       │ SLO breach: internal warning, deploy freeze│
│ CONSEQUENCE  │ SLA breach: service credits, churn risk   │
├──────────────┼───────────────────────────────────────────┤
│ TYPICAL      │ 99.9% SLO on 99.5% SLA provides 43.2-    │
│ BUFFER       │ 216 min buffer per month                  │
├──────────────┼───────────────────────────────────────────┤
│ MEASUREMENT  │ Negotiate: independent probe > vendor     │
│              │ self-report. Clarify exclusions upfront.  │
├──────────────┼───────────────────────────────────────────┤
│ CREDITS      │ Typically 10-30% of monthly fee per       │
│              │ 0.1% availability below threshold         │
├──────────────┼───────────────---------------------------------------------------------------- ┤
│ ANTI-PATTERN │ SLO = SLA: no buffer. Every SLO breach    │
│              │ is a contractual failure.                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Error Budget → On-Call Mgmt → Post-Mortem │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Always maintain buffer between internal quality targets
and external commitments. The SLO/SLA gap is an example
of this principle. Without buffer, every operational
failure immediately becomes a customer commitment
failure, eliminating time to detect, respond, and
recover. This applies to: API response time SLAs
(internal P99 targets vs customer-facing guarantees),
delivery commitments (internal sprint velocity vs
sprint commitments), and financial reporting (internal
forecasts vs public guidance).

---

### 💡 The Surprising Truth

The most counterintuitive SLA insight: a well-designed
SLA that is never triggered is more valuable than one
that is frequently triggered and paid. Frequent service
credit payouts signal to customers that reliability
is poor. Customers use credits as evidence in vendor
selection reviews. The strategic goal is not to minimise
the credit amount - it is to never breach the SLA at
all, which requires an SLO set far enough above the
SLA that routine incidents never reach the contractual
threshold.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain to a legal team drafting a
   customer contract why the SLA threshold should be
   set at 99.5% when the engineering team's SLO target
   is 99.9%, including the buffer calculation.
2. **[DEBUG]** Given a dispute where the vendor shows
   99.7% availability and the customer shows 99.2%,
   identify at least three measurement method differences
   that could explain the discrepancy.
3. **[DECIDE]** For a new SaaS product with a 99.9% SLO,
   design the SLA including: the threshold, the
   measurement method, the exclusions list, and the
   credit structure. Justify each choice.
4. **[BUILD]** Implement the SLA compliance monitoring
   system: a PromQL query that computes monthly SLA
   compliance excluding planned maintenance windows,
   an alert that fires when SLI approaches SLA threshold,
   and automated service credit calculation.
5. **[EXTEND]** Design a tiered SLA structure for an
   enterprise SaaS product with three customer tiers
   (standard, premium, enterprise). Define the SLA
   threshold, measurement method, and credit structure
   for each tier, and explain what engineering
   investment is required to support each tier.

---

### 🧠 Think About This Before We Continue

**Q1.** You are negotiating a 99.9% availability SLA
with an enterprise customer. The customer wants
independent measurement (synthetic probe from their
network). Your internal monitoring shows 99.95%
availability. You estimate that independent probes
will show 0.1-0.2% lower availability due to network
path differences. Should you agree to independent
measurement? What changes to your SLA threshold or
architecture would you need to make to be comfortable
with independent measurement?
_Hint: If internal = 99.95% and independent shows 0.2%
lower = 99.75%, you are well above a 99.5% SLA but
below a 99.9% SLA. Agreeing to independent measurement
with a 99.9% SLA is risky. Options: lower SLA to 99.5%
(safe with independent), or invest in CDN and anycast
routing to reduce network path variance._

**Q2.** Your SaaS platform has a 99.5% monthly SLA.
In February (28 days), your service experienced:

- 8 hours of planned maintenance (pre-announced)
- 2 hours of unplanned degradation (incident)
- 45 minutes of partial outage (30% of requests failed)

Calculate: is the SLA breached? Show your calculation
step by step, applying exclusions. If service credits
are due, calculate the amount on a $50,000/month fee
with 10% credit per 0.1% below threshold.
\*Hint: Total available time = 28 x 24 x 60 = 40,320 min.
Exclude planned maintenance: denominator = 40,320 - 480
= 39,840 min. Unplanned downtime: 120 min full outage

- 45 min x 0.3 (partial) = 120 + 13.5 = 133.5 min of
  "equivalent downtime." Availability = (39,840 - 133.5)
  / 39,840 = 99.67%. Above 99.5% SLA → no breach.\*

**Q3 (TYPE G):** You are the head of engineering at a
cloud storage vendor. Three of your 50 largest enterprise
customers are threatening non-renewal, citing reliability
concerns. Your current SLA is 99.9% availability/month
with 10% credit per 0.1% below threshold. Your internal
SLO is 99.99%. Your actual measured availability over
the last year has been 99.94% average, with one month
at 99.7% (a major incident). Design a revised SLA
package that addresses customer concerns without over-
committing: include the threshold, measurement method,
exclusions, credit structure, and any pro-active
communication strategy. Justify each decision.
_Hint: The customers' concern is the 99.7% month (below
99.9% SLA threshold). Consider: raising SLA to 99.95%
(demonstrates confidence), adopting independent
measurement (demonstrates transparency), raising credit
rate to 25% (demonstrates commitment to compensation),
adding a proactive incident notification SLA (customer
is told within 15 minutes of a P1 incident). The
business case: $2M in at-risk contracts vs $200K in
potential credits at higher credit rate._

---

### 🎯 Interview Deep-Dive

**Q1: "What is the relationship between SLI, SLO, and
SLA? Which is the most important from an engineering
perspective?"**
_Why they ask:_ Tests precision of understanding of
the three-tier measurement system.
_Strong answer includes:_

- SLI = measurement, SLO = internal target, SLA =
  customer contract
- Engineering controls the SLI and SLO. The SLA is
  negotiated with business and legal input.
- Most important from engineering perspective: SLO.
  It drives daily operations (error budget policy,
  deployment gates, reliability investment). The SLA
  is important for business but is rarely breached
  in a well-run SRE org because the SLO provides
  a substantial buffer.
- The critical relationship: SLO must be tighter than
  SLA. If equal, every SLO breach is contractual
  damage.

**Q2: "A customer is reporting 99.2% availability
in their monitoring but your internal metrics show
99.8%. How do you resolve the discrepancy?"**
_Why they ask:_ Tests practical SLA dispute resolution
and measurement methodology understanding.
_Strong answer includes:_

- First: do not immediately concede or contest. Get
  the raw data: their probe timestamps, your metric
  data, for the same period.
- Likely causes: (1) measurement method difference
  (they measure from their network, you from your
  data centre - CDN or network path failures are not
  visible internally), (2) different metric definitions
  (they count any slow response as downtime; you count
  only 5xx), (3) sampling rate differences (their
  probe tests every 30 seconds; yours every 15 seconds)
- Resolution: identify which measurement method the
  SLA contract specifies. If it specifies the vendor's
  measurement, your 99.8% is contractually correct.
  If it specifies independent or customer measurement,
  their 99.2% may be correct.
- Learning: negotiate measurement method upfront.
  Proactively set up external probes to match the
  customer's perspective before a dispute arises.

**Q3: "How do you set up an SLA for a new SaaS product?
Walk me through the key decisions."**
_Why they ask:_ Tests end-to-end understanding of SLA
design, not just the definition.
_Strong answer includes:_

- Step 1: define the SLI (what is being measured -
  availability, latency, data freshness?)
- Step 2: set the SLO first. The SLA must be derived
  from the SLO, not set independently.
- Step 3: determine the buffer (SLO - SLA gap). Minimum
  0.1%; typical 0.3-0.5% for a new service.
- Step 4: define the measurement method (vendor
  internal, independent third party, customer probe).
  External probe is more trustworthy for customers.
- Step 5: define exclusions - planned maintenance,
  force majeure. Keep exclusions narrow to build
  customer trust.
- Step 6: set the credit structure: typically 10-25%
  of monthly fee per 0.1% below threshold, capped
  at 50-100% of monthly fee.
- Critical: measure current performance for 30 days
  before committing to an SLA. Never set an aspirational
  SLA for a new service.
