---
id: MSV-024
title: Feature Flags
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-023, MSV-002
used_by: MSV-018
related: MSV-023, MSV-067, MSV-068, MSV-018, MSV-027
tags:
  - microservices
  - devops
  - intermediate
  - deployment
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 24
permalink: /microservices/feature-flags/
---

# MSV-024 - Feature Flags

⚡ TL;DR - Feature Flags are runtime boolean conditions
that control whether a feature is active, enabling
new code to be deployed but not yet activated, and
activated for specific users or a percentage of traffic
without redeployment. They decouple deployment from
release.

| #024 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Blue-Green Deployment, Microservices Architecture | |
| **Used by:** | Fallback Strategy | |
| **Related:** | Blue-Green Deployment, Canary Deployment, Zero-Downtime Deployment, Fallback Strategy, Versioning Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Deploy = Release. The moment you deploy code, every
user sees the change. A new checkout redesign: all
users see it simultaneously on deployment. If the redesign
increases abandonment by 20%, there is no way to roll
back without a full redeployment (minutes, with potential
downtime).

You want to A/B test the redesign on 5% of users. Without
feature flags, this requires maintaining two separate
deployments, two codebases, two routing rules at the
load balancer. Operationally complex.

A critical service has a performance issue that only
affects a specific user cohort. To disable that feature
for affected users: without feature flags, you need
a code change, a build, and a deployment cycle.

**THE INVENTION MOMENT:**
Feature flags separate code deployment from feature
activation. Deploy code with the new feature behind a
flag (flag=off). Activate for 5% of users by changing
the flag value (no deployment). Deactivate in 30 seconds
for the affected cohort. The flag is a runtime switch
that product managers and oncall engineers can control
without touching code.

---

### 📘 Textbook Definition

**Feature Flags** (also: Feature Toggles, Feature Switches)
are a software development technique where functionality
is controlled by a conditional check against a named
"flag" value retrieved from a configuration store
(database, config service, or environment variable).
The flag can be: boolean (on/off), percentage-based
(activate for X% of users), user-segment-based (activate
for beta users), or time-based (activate after a date).
Changing a flag value takes effect without code deployment.
Feature flags implement "dark launches" (code deployed
but not active) and "canary releases" (code active for
subset of users).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Feature Flag is a runtime on/off switch for a feature:
deploy code with the switch off, turn it on for specific
users or a percentage of traffic without redeployment.

**One analogy:**
> A light switch on a newly installed light fixture.
> The electrician wires the fixture (deploys the code)
but leaves the circuit breaker off. When the room is
> ready, anyone can flip the switch (change the flag)
> without calling the electrician. If the light flickers
> (bug), flip the switch back off. No electrician needed.

**One insight:**
Feature flags enable continuous deployment practices:
commit and deploy every code change to production (without
activating it). Features accumulate behind flags until
they are ready for release. Release becomes a business
decision ("turn on the Black Friday feature at 9 AM"),
not a technical operation.

---

### 🔩 First Principles Explanation

**TYPES OF FEATURE FLAGS:**

```
RELEASE FLAGS (temporary, most common):
  Purpose: dark launch, gradual rollout
  Lifecycle: created before feature, deleted after 100%
  Example: new-checkout-ui-enabled
  Default: off -> gradually increase to 100% -> delete

EXPERIMENT FLAGS (A/B testing):
  Purpose: measure user behaviour differences
  Lifecycle: created per experiment, deleted after result
  Example: checkout-cta-button-text ("Buy Now" vs "Checkout")
  Allocation: 50% see A, 50% see B
  Result: measure conversion rate per variant

OPS FLAGS (permanent or long-lived):
  Purpose: operational control, kill switch
  Lifecycle: permanent (or until system changed)
  Example: enable-fraud-ml-scoring (vs rule-based)
  Example: use-new-recommendation-engine
  Use for: fallback switches, rate limiting bypasses

PERMISSION FLAGS (user segment):
  Purpose: graduated access (beta users, paid tier)
  Lifecycle: long-lived
  Example: advanced-analytics-dashboard
    (enabled for: Enterprise tier users)
```

**FLAG EVALUATION LOGIC:**

```
SIMPLE BOOLEAN:
  if (flags.isEnabled("new-checkout")) {
    return newCheckoutService.process(order);
  } else {
    return legacyCheckoutService.process(order);
  }

PERCENTAGE ROLLOUT:
  flag value: {percentage: 10, sticky: true}
  evaluation: hash(userId) % 100 < 10 ?
    -> consistent per user (sticky)
    -> user always sees same variant (not random per request)

USER SEGMENT:
  flag value: {segments: ["beta_testers", "employees"]}
  evaluation: user.segments intersects flag.segments ?

COMPLEX (LaunchDarkly-style):
  if user.country == "US" AND
     user.accountAge > 30 days AND
     random_bucket(userId) < 25%:
    -> enable feature
```

---

### 🧪 Thought Experiment

**GRADUAL ROLLOUT STRATEGY:**

```
New recommandation engine deployment timeline:

Day 1:  flag = 0% (code deployed, feature inactive)
        Team tests in staging using flag=100% in staging

Day 2:  flag = 1% (100 users out of 10,000)
        Monitor: click-through rate, conversion, errors
        Baseline metrics match old engine: OK

Day 3:  flag = 10%
        Monitor: CTR +3% (good!), no latency increase
        Observation: recommendation engine faster

Day 5:  flag = 50%
        Monitor: CTR +3.5%, latency P99 +20ms (investigate)
        Find: ML model cold start adding 20ms
        Fix: pre-warm ML model at startup

Day 6:  flag = 100% (after fix deployed)
        Monitor: CTR +3.5%, latency normal
        Delete flag from codebase (cleanup)

WITHOUT FLAGS:
  Deploy directly to 100% of users on Day 1
  Same CTR increase AND latency spike for all users
  Rollback affects all users, causes downtime
  Fix takes longer under pressure
```

---

### 🧠 Mental Model / Analogy

> Feature flags are like the phased opening of a new
> theme park attraction. The ride is built and tested
> (code deployed). First: invited guests only (beta
> users, flag by segment). Then: annual passholders
> (10% rollout). Then: all guests (100% rollout). At
> any point: close the ride for safety (disable flag
> in 30 seconds). No construction (deployment) needed
> to close it. The ride exists; the flag controls access.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A feature flag is an if-statement that checks a config
value instead of a hardcoded true/false. When the config
is "on", users see the new feature. When it's "off",
they see the old behaviour. Changing the config happens
without redeployment.

**Level 2 - How to use it (junior developer):**
```java
// Spring Boot + Unleash/FF4J/LaunchDarkly
bool isEnabled = featureFlags.isEnabled(
    "new-payment-flow", userId);
if (isEnabled) {
    return newPaymentService.process(req);
}
return legacyPaymentService.process(req);
```
In staging: flag=100%. In production: flag starts at 1%,
gradually increases to 100% over several days.

**Level 3 - How it works (mid-level engineer):**
Feature flag evaluation: SDK evaluates flag against user
context (userId, segments, country). Sticky evaluation:
`hash(userId, flagName) % 100 < percentage` ensures
the same user always sees the same variant (not random
per request). Flag values are cached in-process (reduce
latency), refreshed from flag service every 30 seconds.
Flag changes propagate to all SDK instances within 30s
(Unleash), or instantly via SSE (LaunchDarkly).

**Level 4 - Why it was designed this way (senior/staff):**
Feature flags introduce "flag debt" - every flag in
the codebase is a branch that must be tested and maintained.
10 flags = 2^10 = 1024 possible code paths. Technical
discipline: each flag must have an expiry date or cleanup
criteria defined at creation. When a flag reaches 100%
and has been stable for 2+ weeks: remove the flag and
the dead code path (the old implementation). This is
as important as the feature itself - flag debt compounds
like code debt.

**Level 5 - Mastery (distinguished engineer):**
At scale, feature flag evaluation adds latency. LaunchDarkly
SDK evaluates flags in-process (cached local evaluation,
microseconds per flag). Unleash: similar in-process cache.
The failure mode: flag service goes down. With in-process
caching, the last known flag state is used (stale but
functional). With remote evaluation (each request calls
flag service): flag service outage = all feature flag
checks fail or default to safe values. Always use in-
process caching with a fallback default value that
represents the safe state (usually: flag=off = old behavior).

---

### ⚙️ How It Works (Mechanism)

**UNLEASH JAVA SDK - FEATURE FLAG EVALUATION:**

```java
@Component
public class FeatureFlagService {

    @Autowired
    private Unleash unleash;

    // Simple boolean check
    public boolean isNewCheckoutEnabled(String userId) {
        UnleashContext context =
            UnleashContext.builder()
                .userId(userId)
                .build();
        return unleash.isEnabled(
            "new-checkout-flow", context);
    }

    // Percentage rollout: consistent per user
    // Unleash FlexibleRolloutStrategy:
    //   stickiness: userId
    //   rollout: 10 (10% of users)
    //   hash(userId, featureName) % 100 < 10
}

@Service
public class CheckoutService {

    @Autowired
    private FeatureFlagService flags;
    @Autowired
    private NewCheckoutService newCheckout;
    @Autowired
    private LegacyCheckoutService legacyCheckout;

    public Order checkout(
        CheckoutRequest req, String userId) {
        if (flags.isNewCheckoutEnabled(userId)) {
            return newCheckout.process(req);
        }
        return legacyCheckout.process(req);
    }
}
```

**FF4J SPRING BOOT (lightweight alternative):**

```java
@Autowired
private FF4j ff4j;

// In code
if (ff4j.check("new-recommendation-engine")) {
    return mlRecommendationEngine.recommend(userId);
}
return ruleBasedEngine.recommend(userId);

// Configuration (can be stored in DB, Redis, YAML)
// ff4j.getFeatureStore().saveFeature(
//   new Feature("new-recommendation-engine", false))

// Or in application.yml:
// ff4j:
//   features:
//     new-recommendation-engine:
//       enable: false
//       flippingStrategy:
//         class: GradualRolloutRandomStrategy
//         initParams:
//           percentage: 10
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FEATURE FLAG SYSTEM ARCHITECTURE:**

```
Product Manager / Engineer:
  LaunchDarkly Dashboard / Unleash UI
    -> Update flag: "new-checkout" = 10%
    -> Propagates to SDK instances: <30s

Application (SDK in-process):
  Local cache: {"new-checkout": {rollout: 10}}
  Updated: 30s TTL, refreshed from flag service
  Evaluation: hash(userId, "new-checkout") % 100 < 10
    -> true: new checkout
    -> false: legacy checkout

Monitoring:
  Flag event: track which variant each user saw
  Metrics: compare conversion rate between variants
  Alert: if error rate > 1% for new-checkout variant:
    auto-disable flag (via webhook to flag service)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: environment variable flag**

```java
// BAD: hardcoded environment variable
// Changes require redeployment + env var update
// Cannot do percentage rollout
// No user-segment targeting
bool enabled = Boolean.parseBoolean(
    System.getenv("NEW_CHECKOUT_ENABLED"));
// True or false: all users, no gradual rollout
```

```java
// GOOD: feature flag service with targeting
// Changes without redeployment (30s propagation)
// Percentage rollout, user segments, A/B testing
UnleashContext context = UnleashContext.builder()
    .userId(user.getId())
    .addProperty("accountTier", user.getTier())
    .addProperty("country", user.getCountry())
    .build();
bool enabled = unleash.isEnabled(
    "new-checkout-flow", context);
// Flag configured in Unleash UI:
//   10% of users, stickiness by userId
//   Extra condition: country=US AND tier=premium
// Changes in UI: active in <30s, no deploy
```

**Example 2 - Flag debt anti-pattern**

```java
// BAD: flag that was never cleaned up (flag debt)
// Created 18 months ago, feature at 100% for 14 months
// Original feature code is dead code
public Order process(OrderRequest req) {
    if (flags.isEnabled("new-order-engine-v2")) {
        return newOrderEngine.process(req);  // live
    }
    return legacyOrderEngine.process(req);  // DEAD CODE
    // legacyOrderEngine still tested, maintained,
    // dependency updated - all wasted work
}

// GOOD: flag removed after 100% rollout + stability
// Step 1: verify flag is at 100%, has been for 2 weeks
// Step 2: remove if-statement, delete legacy code
// Step 3: delete flag from flag service
public Order process(OrderRequest req) {
    return newOrderEngine.process(req);  // clean
}
```

---

### ⚖️ Comparison Table

| Tool | Target Scale | Hosting | Pricing | Key Feature |
|---|---|---|---|---|
| **LaunchDarkly** | Enterprise | SaaS | Paid | Instant propagation, data export |
| **Unleash** | Any | Self-hosted/SaaS | Free (OSS) | GitOps, audit log |
| **FF4J** | Spring Boot | Self-hosted | Free | Spring integration, annotation |
| **Spring Cloud Config** | Basic flags | Self-hosted | Free | Simple, not purpose-built |
| **AWS AppConfig** | AWS-native | Managed | Pay-per-use | Built-in validation, rollback |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Feature flags can replace testing | Feature flags enable gradual rollout which catches issues in production. They don't replace unit, integration, or contract tests. The gradual rollout reduces blast radius - it doesn't validate correctness. Test before flagging. |
| Flags are temporary by definition | Ops flags (kill switches, capability toggles) are intentionally permanent. Example: `enable-new-payment-provider` may be permanent as a fallback switch. Distinguish: release flags (delete after 100%), experiment flags (delete after result), ops flags (permanent). |
| Flag evaluation is always fast | If the flag service is unavailable and in-process caching is not configured, every flag check is a network call. Design flag evaluation to be: (a) in-process cached, (b) with a safe default when service is unavailable. A missing flag should default to OFF (old behavior), not throw an exception. |

---

### 🚨 Failure Modes & Diagnosis

**Flag service outage cascades to application**

**Symptom:**
All feature flag checks start returning errors. 50% of
service endpoints fail (those behind flags). Flag service
was deployed and has a startup bug.

**Root Cause:**
Flag evaluation uses remote call per request (no caching).
Flag service down = every flag check throws exception.
Service not handling the exception: 500 to users.

**Diagnostic:**
```bash
# Check flag service health
curl http://unleash-service:4242/health

# Check if SDK is using in-process cache
# In application logs:
grep "unleash.*cache" app.log
# Should see: "Using cached flag values"
# If: "Fetching flags from server" per request = no cache
```

**Fix:**
```java
// Always have a fallback default
bool enabled = unleash.isEnabled(
    "new-checkout",
    context,
    false);  // default=false if flag service down
// SDK uses in-process cache
// If cache expired and service down: use false (safe)

// Or: check for FallbackStrategy
unleash.isEnabled("flag", ctx, (name, ctx2) -> false);
// Custom fallback: lambda returns safe default
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Blue-Green Deployment` - Feature flags and blue-green
  are complementary release strategies. Blue-green handles
  the deployment mechanism; feature flags handle activation.

**Related Patterns:**
- `Canary Deployment` - Blue-Green + Feature Flags enable
  canary: deploy to a subset of servers (blue-green) +
  activate for subset of users (feature flag)
- `Fallback Strategy` - Ops feature flags are permanent
  fallback switches: disable new integration, revert
  to old implementation at runtime

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY TYPES    │ Release (temp), Experiment (A/B),        │
│              │ Ops (permanent kill switch)              │
├──────────────┼───────────────────────────────────────────┤
│ FLAG DEBT    │ Release flags: delete after 100% + 2wks  │
│              │ Each flag = extra code path to maintain   │
├──────────────┼───────────────────────────────────────────┤
│ RELIABILITY  │ Always in-process cache (SDK local)      │
│              │ Default=OFF if flag service unavailable   │
├──────────────┼───────────────────────────────────────────┤
│ STICKY       │ Percentage: hash(userId, flagName)%100   │
│              │ Same user always sees same variant        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Runtime switch: deploy code,            │
│              │  activate for users without redeployment" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary Deployment → Zero-Downtime Deploy │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Feature flags decouple deployment from release. Deploy
   code with flag=off. Activate flag for users without
   redeployment.
2. Use sticky evaluation: hash(userId, flagName) % 100
   < rolloutPct. Same user always sees same experience.
3. Clean up release flags after reaching 100% + 2 weeks
   stable. Uncleaned flags are flag debt: extra code
   paths to test, maintain, and reason about.

**Interview one-liner:**
"Feature Flags separate deployment from release: deploy
code with flag=off, then activate for 1%->10%->100%
of users without redeployment. Types: release flags
(temporary, delete after 100%), experiment flags (A/B
testing), ops flags (permanent kill switches). Production
rules: in-process SDK caching (flag service unavailability
doesn't break app), sticky evaluation (consistent per
user), and mandatory cleanup of release flags to prevent
flag debt."

---

### 💡 The Surprising Truth

Feature flags seem like a purely technical pattern but
are fundamentally an organisational pattern. Their full
value is only realised when product managers, not just
engineers, can manage flags. If only engineers can change
flag values, you've just moved the gating from "deploy"
to "submit a ticket to an engineer to flip the flag".
The transformative version: PM wants to launch the new
checkout at Black Friday 9 AM. PM logs into LaunchDarkly,
schedules the flag activation at 9:00 AM. No engineer
involved. The organisation gains release-on-demand
capability without engineering bottlenecks. This is
why platform investment in feature flag tooling (LaunchDarkly,
Unleash) has high ROI beyond just the technical capability.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** A percentage-based feature flag with
   sticky user evaluation (hash-based) using Unleash or
   LaunchDarkly SDK, with in-process caching and safe
   fallback defaults.
2. **DESIGN** A flag lifecycle policy: when flags are
   created (before feature code), maximum age before
   cleanup, who can modify flags in each environment.
3. **DETECT FLAG DEBT** Audit a codebase for feature
   flags: identify flags that should be removed (at
   100% rollout for >2 weeks), and calculate the
   number of test permutations created by all active
   flags.
4. **EMERGENCY USE** Demonstrate using an ops flag as
   an emergency kill switch: a new payment integration
   has a bug, disable it and revert to legacy in 30s.
5. **MEASURE** Design the metrics pipeline to measure
   A/B test results: assign users to variants, track
   conversion per variant, achieve statistical
   significance.

---

### 🧠 Think About This Before We Continue

**Q1.** You have a feature flag at 50% rollout. User
A is in the 50% that sees the new checkout. User A logs
out and logs back in. Does User A see the new checkout
still? (Hint: depends on sticky evaluation - what is
the stickiness key?) What happens when User A clears
their browser cache? What happens when User A uses
a different device?

**Q2.** Your team has 50 feature flags in production.
20 are release flags that should have been deleted months
ago. Each flag creates 2 code paths. How many total
code paths exist? What is the minimum number of test
cases needed for full coverage? Design a governance
process that prevents this flag debt accumulation.

**Q3.** You want to use feature flags to test a new ML
pricing model on 5% of users. The ML model affects
the displayed price. What are the ethical and regulatory
considerations of showing different prices to different
users? (Hint: consider price discrimination laws, GDPR
consent, and the difference between A/B testing for UX
vs pricing experiments.)