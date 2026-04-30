---
layout: default
title: "Feature Flags"
parent: "Microservices"
nav_order: 671
permalink: /clean-code/feature-flags/
number: "671"
category: Microservices
difficulty: ★★☆
depends_on: Configuration Management, Deployment, CI-CD Pipeline
used_by: Canary Deployment, A/B Testing, Trunk-Based Development, Blue-Green Deployment
tags: #devops, #architecture, #intermediate, #reliability
---

# 671 — Feature Flags

`#devops` `#architecture` `#intermediate` `#reliability`

⚡ TL;DR — Runtime configuration switches that enable or disable features without deploying new code, decoupling feature release from code deployment.

| #671 | category: Microservices
|:---|:---|:---|
| **Depends on:** | Configuration Management, Deployment, CI-CD Pipeline | |
| **Used by:** | Canary Deployment, A/B Testing, Trunk-Based Development, Blue-Green Deployment | |

---

### 📘 Textbook Definition

**Feature flags** (also called feature toggles, feature switches, or feature bits) are a software delivery technique that uses conditional logic to enable or disable features at runtime without deploying new code. A feature flag is a name-value pair stored in configuration (environment variable, database, remote config service) that gates a code path. They decouple **feature release** (when users see a feature) from **code deployment** (when code reaches production), enabling continuous deployment of incomplete or risky code, controlled rollouts to subsets of users, and instant rollback without redeployment.

---

### 🟢 Simple Definition (Easy)

A feature flag is like a light switch in your code. You deploy the feature to production but keep the switch off. When you're ready, you flip the switch — the feature turns on without a new deployment. If something goes wrong, flip it back.

---

### 🔵 Simple Definition (Elaborated)

Normally, deploying code means releasing it. Feature flags break this coupling: code with the new feature reaches production, but users don't see it because a flag keeps it disabled. You can then enable it for a small percentage of users (1% canary), for specific users (beta testers), or for a specific region — all without redeployment. If a problem is detected, the flag is disabled in seconds — far faster than rolling back a deployment. This enables teams to continuously deploy to production (trunk-based development) while releasing features on their own schedule.

---

### 🔩 First Principles Explanation

**Problem — deployment = release coupling:**

Traditionally, deploying code immediately exposed it to all users. This forced teams to delay deployments until features were complete and tested, creating large, risky batch deployments:

```
┌──────────────────────────────────────────────┐
│  WITHOUT FEATURE FLAGS                       │
│                                             │
│  Feature A (partial) ─┐                     │
│  Feature B (complete)  ├─ Must deploy all   │
│  Feature C (untested) ─┘  at once → big bang│
│                                             │
│  Rollback = redeploy previous version       │
│  → 15-minute outage window                  │
│                                             │
│  Testing in prod: impossible                │
│  → synthetic load tests only               │
└──────────────────────────────────────────────┘
```

**Solution — decouple deployment from release:**

```
WITH FEATURE FLAGS

  All code deploys continuously (trunk-based)
      ↓
  Feature A: flag=OFF → invisible to users
  Feature B: flag=ON for 5% → canary test
  Feature C: flag=ON for beta group → early access
      ↓
  Rollback: flip flag OFF → instant
  No redeployment needed
      ↓
  Feature B passes 5% test: flag=ON for 100%
  → gradual, safe release
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT feature flags:**

```
Problems:
  1. Long-lived feature branches:
     → Branches diverge → painful merges
     → "Integration hell" before each release

  2. All-or-nothing deployments:
     → New pricing algorithm wrong for 0.1% users
     → Must rollback for all 100% → revenue impact

  3. Can't test in production:
     → Synthetic tests miss real traffic patterns
     → "Works on staging" but fails on prod load

  4. Slow incident response:
     → Bad deployment detected → 20-min rollback
     → Every minute costs revenue
```

**WITH feature flags:**

```
→ Trunk-based development: merge daily to main
→ Instant rollback via flag toggle (seconds)
→ A/B test new UI on real users, measure conversion
→ Kill switch for any feature during an incident
→ Progressive delivery: 1% → 10% → 50% → 100%
→ Dark launches: run new code path, log results,
  users see old code — validate without risk
```

---

### 🧠 Mental Model / Analogy

> Feature flags are like **pre-wired electrical circuits** in a new building. When the building is constructed, all rooms have wiring and light fixtures installed — but the switches at the breaker panel are off. The building is fully deployed (all code is there) but features (lights) are OFF. You turn on the lobby lights first, verify they work, then the offices, then the basement. If the basement lights cause a fault, flip the breaker — the rest of the building stays lit.

"Pre-wired building" = all code deployed to production
"Electrical switch off" = feature flag disabled
"Lobby lights first" = progressive rollout (1% → 10%)
"Basement fault → flip breaker" = instant rollback via flag
"Multiple independent circuits" = independently togglable features

---

### ⚙️ How It Works (Mechanism)

**Four categories of feature flags:**

```
┌────────────────────────────────────────────────────────┐
│  FLAG TYPES (by lifecycle and purpose)                 │
├────────────────────────────────────────────────────────┤
│  Release toggles   → enable/disable incomplete feature │
│  Lifespan: days to weeks; remove after full rollout    │
│                                                        │
│  Experiment toggles→ A/B testing, multivariate tests  │
│  Lifespan: days to weeks; statistical significance     │
│                                                        │
│  Ops toggles       → kill switches for incidents      │
│  Lifespan: permanent; disable a feature under load    │
│                                                        │
│  Permission toggles→ features for user segments       │
│  Lifespan: long-lived; premium features, beta users   │
└────────────────────────────────────────────────────────┘
```

**Implementation patterns:**

```java
// Simple: environment variable check
if (System.getenv("FEATURE_NEW_CHECKOUT").equals("true")) {
  return newCheckoutService.process(cart);
} else {
  return legacyCheckoutService.process(cart);
}

// Better: dedicated flag service with user context
if (featureFlags.isEnabled("new-checkout", user)) {
  return newCheckoutService.process(cart);
} else {
  return legacyCheckoutService.process(cart);
}
// featureFlags.isEnabled() checks: user segment,
// percentage rollout, kill-switch, A/B cohort
```

**Percentage rollout implementation:**

```java
// Consistent user assignment (same user always same bucket)
boolean isInRollout(String flagKey, String userId,
                    int percentage) {
  int hash = Math.abs(
    (flagKey + ":" + userId).hashCode()
  ) % 100;
  return hash < percentage;
}
// userId ensures same user gets same flag value on
// every request (no flickering experience)
```

---

### 🔄 How It Connects (Mini-Map)

```
CI/CD Pipeline (continuous deployment)
        ↓
  Code deployed to production
  (trunk-based development)
        ↓
  FEATURE FLAGS  ← you are here
  (decouple release from deployment)
        ↓
  ├── Release Toggles → progressive rollout
  ├── Ops Toggles     → instant kill switch
  ├── Experiment      → A/B test in production
  └── Permission      → segment-based access
        ↓
  Canary Deployment (% cohort via flag)
  Blue-Green Deployment (traffic switch via flag)
        ↓
  Flag service: LaunchDarkly, Unleash,
  AWS AppConfig, GrowthBook
```

---

### 💻 Code Example

**Example 1 — Spring Boot with environment-based flag:**

```java
@Service
public class CheckoutService {
  @Value("${feature.new-checkout:false}")
  private boolean newCheckoutEnabled;

  private final NewCheckoutProcessor newProcessor;
  private final LegacyCheckoutProcessor legacyProcessor;

  public Receipt checkout(Cart cart) {
    if (newCheckoutEnabled) {
      return newProcessor.process(cart);
    }
    return legacyProcessor.process(cart);
  }
}
// application.properties: feature.new-checkout=false
// Override per environment: k8s ConfigMap, env var
```

**Example 2 — Production-grade flag service with context:**

```java
// LaunchDarkly style: user-context aware
@Component
public class FeatureFlagService {
  private final LDClient ldClient;

  public boolean isEnabled(String flagKey, User user) {
    LDUser ldUser = new LDUser.Builder(user.getId())
        .email(user.getEmail())
        .custom("plan", user.getPlan())
        .build();
    return ldClient.boolVariation(flagKey, ldUser, false);
  }
}

// Usage:
if (flags.isEnabled("dark-mode-beta", currentUser)) {
  return darkModeLayout();
}
```

**Example 3 — Flag hygiene — removing stale flags:**

```java
// BAD: flag from 6 months ago still in production
// "new-homepage-v2" was fully released months ago
if (flags.isEnabled("new-homepage-v2", user)) {
  return newHomepage(); // 100% of users see this
} else {
  return oldHomepage(); // dead code — never reached
}

// GOOD: remove flag after 100% rollout
// Ticket: "Remove feature-new-homepage-v2 flag"
// Sprint cleanup: delete flag + delete old code path
public String getHomepage() {
  return newHomepage(); // flag gone, code clean
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Feature flags guarantee zero-risk releases | Flags reduce risk but don't eliminate it. Flag evaluation path must be tested; the flag service itself can fail (have a safe default) |
| Feature flags can stay in the code forever | Stale flags are technical debt. They add cognitive load, require testing both paths, and create confusion. Remove flags after full rollout — treat them as temporary scaffolding |
| Feature flags are only for large companies | Small teams benefit equally — instant rollback and safe progressive rollout are useful at any scale. Open source: Unleash, GrowthBook, Flagsmith |
| Environment variables are good enough for production flags | Env vars require a redeployment to change. Production-grade flags need runtime changeability — a config service or feature flag platform |

---

### 🔥 Pitfalls in Production

**1. Flag evaluation performance — N+1 lookups in loops**

```java
// BAD: flag evaluated inside a loop → N remote calls
for (Product product : products) {
  if (flags.isEnabled("new-pricing", user)) { // N calls!
    product.setPrice(newPricing.calculate(product));
  }
}

// GOOD: evaluate once, use result
boolean useNewPricing = flags.isEnabled("new-pricing", user);
for (Product product : products) {
  if (useNewPricing) {
    product.setPrice(newPricing.calculate(product));
  }
}
// Or: use SDK's in-memory cache with streaming updates
```

**2. Flag service outage → all flags default to false**

```java
// BAD: if flag service is down, disabled defaults break
// critical functionality
if (flags.isEnabled("payment-processing", user)) {
  return processPayment(order); // FLAG DOWN = no payments!
}
// Default false → payment system goes dark

// GOOD: ops kill switches default to TRUE (safe=on)
// Release toggles default to FALSE (safe=off)
// Implement fallback: cache last-known values in Redis
// LDClient uses: in-memory streaming cache always available
```

**3. Testing both paths but only one in production**

```java
// Sneaky bug: the else branch aged 6 months untested
if (flags.isEnabled("new-search", user)) {
  return newSearchService.search(query);  // tested
} else {
  return oldSearchService.search(query);  // bit-rotted
}
// "old-search" has a bug introduced in a dependency
// update 3 months ago — nobody noticed because 99%
// of traffic went through new-search

// GOOD: remove old branch once rollout >99%
// Keep both paths: run both, log differences, compare
// (dark launch / shadow mode pattern)
```

---

### 🔗 Related Keywords

- `CI-CD Pipeline` — feature flags enable continuous deployment by separating release from deploy
- `Canary Deployment` — percentage-based rollout is the primary mechanism; feature flags implement it
- `Blue-Green Deployment` — traffic switching can be driven by a feature flag at the load balancer
- `Technical Debt` — stale feature flags that outlive their purpose are classic technical debt
- `A/B Testing` — experiment flags power A/B tests in production with real user traffic
- `Trunk-Based Development` — feature flags make this possible; incomplete features hidden behind flags

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Decouple deployment from release;         │
│              │ toggle features at runtime without redeploy│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Progressive rollouts, kill switches, A/B  │
│              │ tests, dark launches, trunk-based dev      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long-term permanent flags — remove after  │
│              │ full rollout; they become tech debt       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ship the plane while it's still being   │
│              │  built — flags keep the seats roped off." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary Deployment → A/B Testing →         │
│              │ Trunk-Based Development                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A feature flag system stores flag evaluations in a remote service. Your application evaluates 50 flags per request, and handles 100,000 requests/second. Describe the complete caching strategy required to make this work at scale: where flags should be cached (edge vs application vs SDK), what the cache invalidation mechanism should be (polling vs streaming), and the specific risk that arises when multiple instances of your application have slightly different cached flag states simultaneously.

**Q2.** "Dark launch" is a technique where new code runs on every request in production, but its output is discarded — only the old code's output is served to users. The new code runs silently, its behaviour is logged and compared. Explain how this pattern combines feature flags with shadow mode execution, what infrastructure is required to run both code paths without doubling user-facing latency, and describe the specific class of production bug that dark launch catches that no staging-environment test would reveal.

