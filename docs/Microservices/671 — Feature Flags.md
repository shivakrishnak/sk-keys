---
layout: default
title: "Feature Flags"
parent: "Microservices"
nav_order: 671
permalink: /microservices/feature-flags/
number: "671"
category: Microservices
difficulty: ★★☆
depends_on: "Canary Deployment, Blue-Green Deployment"
used_by: "Twelve-Factor App, Versioning Strategy"
tags: #intermediate, #microservices, #devops, #distributed, #reliability
---

# 671 — Feature Flags

`#intermediate` `#microservices` `#devops` `#distributed` `#reliability`

⚡ TL;DR — **Feature Flags** (feature toggles) decouple code deployment from feature release. Code is deployed (with the feature disabled), then the feature is enabled separately — without a new deployment. Enables: dark launches, A/B testing, targeted rollouts (beta users first), and instant kill switches for problematic features.

| #671            | Category: Microservices                  | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Canary Deployment, Blue-Green Deployment |                 |
| **Used by:**    | Twelve-Factor App, Versioning Strategy   |                 |

---

### 📘 Textbook Definition

**Feature Flags** (also called feature toggles, feature switches, or feature gates) are a software engineering technique where code paths are activated or deactivated at runtime based on a configuration flag rather than a code change. Features can be deployed to production in a disabled state, then enabled for specific users, percentages of traffic, geographies, or user cohorts — without redeployment. Pete Hodgson (ThoughtWorks) categorized feature flags into four types: **Release Toggles** (temporary — enable new features during deployment transition), **Experiment Toggles** (A/B testing), **Ops Toggles** (kill switches for operational control), and **Permission Toggles** (long-lived — gating features by user entitlement/tier). In microservices, feature flags serve as the control plane for progressive delivery: deploy code in dark launch mode → enable for 1% of users → observe → enable for 10% → promote to 100%. Feature flag services (LaunchDarkly, Split.io, Unleash, Flipt, AWS AppConfig) provide: real-time flag updates without deployment, user targeting rules, flag analytics, and SDKs for every language.

---

### 🟢 Simple Definition (Easy)

A feature flag is an if-statement connected to a remotely controllable configuration value. `if (featureFlag.isEnabled("new-checkout"))` — the flag is OFF during deployment, flipped ON when ready. No redeployment needed. If the feature breaks, flip the flag OFF. Instant rollback for just that feature, not the whole service.

---

### 🔵 Simple Definition (Elaborated)

New checkout flow: deployed to all servers but flag = OFF. All users see the old checkout flow. Enable for 5% of users. Watch conversion rate and error rate. After 24 hours: metrics good. Enable for 50%. Next day: enable for 100%. No new deploys between these steps. If conversion rate drops: flip flag OFF for everyone instantly — all users back to old checkout. A/B test completed. New flow is better. Full rollout complete.

---

### 🔩 First Principles Explanation

**Feature flag types and lifecycle:**

```
TYPE 1: RELEASE TOGGLE (short-lived: days to weeks)
  Purpose: decouple deployment from release
  Example: new search algorithm deployed but not yet enabled
  Lifecycle: deploy → test dark launch → enable 1% → enable 100% → DELETE FLAG
  IMPORTANT: must be deleted after full rollout to avoid dead code

TYPE 2: EXPERIMENT TOGGLE (short-lived: hours to days)
  Purpose: A/B test
  Example: new pricing display format for 50% of users
  Lifecycle: enable for cohort → measure → winner determined → DELETE FLAG
  Integration: analytics system tracks conversion per flag variant

TYPE 3: OPS TOGGLE (medium-lived: months)
  Purpose: circuit breaker for features (manual kill switch)
  Example: "enable ML recommendations" — disable when recommendation service is slow
  Lifecycle: created → stays enabled in normal ops → toggled during incidents → never truly deleted

TYPE 4: PERMISSION TOGGLE (long-lived: years)
  Purpose: feature entitlement per user tier
  Example: "premium_export_feature" — enabled only for GOLD tier customers
  Lifecycle: permanent (part of the product's entitlement model)
  NOTE: these are not really "feature flags" in the ops sense — more like access control
```

**Flag evaluation patterns — from simple to targeting:**

```
SIMPLE BOOLEAN FLAG (whole population on/off):
  if (featureFlagService.isEnabled("new-checkout")) {
      return newCheckoutService.checkout(request);
  } else {
      return oldCheckoutService.checkout(request);
  }
  Use for: kill switches, ops toggles

PERCENTAGE ROLLOUT (gradual traffic):
  "new-checkout" → enabled for 10% of all users
  Implementation: hash(userId) % 100 < 10 → enabled
  Deterministic: same user always gets same variant (sticky)
  Use for: release toggles, gradual rollout

USER TARGETING (specific cohorts):
  "new-checkout" → enabled for:
    users where attribute "beta_tester" == true
    OR users where attribute "country" == "US"
    AND NOT users where attribute "account_age_days" < 7
  Use for: beta programs, geographic rollouts, new user exclusions

MULTIVARIATE FLAGS (A/B/C testing):
  "checkout-ui-variant" → returns one of: "control", "variant_A", "variant_B"
  Implementation:
    String variant = featureFlagService.getVariant("checkout-ui-variant", userId);
    return switch (variant) {
        case "variant_A" -> newCheckoutA.checkout(request);
        case "variant_B" -> newCheckoutB.checkout(request);
        default -> oldCheckoutService.checkout(request);
    };
  Analytics: track conversion rate per variant → determine winner
```

**LaunchDarkly Java SDK integration:**

```java
// Configuration:
@Bean
LDClient launchDarklyClient(@Value("${launchdarkly.sdk-key}") String sdkKey) {
    LDConfig config = new LDConfig.Builder()
        .events(Components.sendEvents()
            .capacity(10000)
            .flushInterval(Duration.ofSeconds(5)))
        .build();
    return new LDClient(sdkKey, config);
    // LDClient polls LD server for flag updates (or uses streaming)
    // Flags cached locally → evaluation is in-process (~microseconds)
}

// Flag evaluation with user context:
@Service
class CheckoutService {
    @Autowired LDClient ldClient;

    public CheckoutResult checkout(CheckoutRequest request, User user) {
        LDContext context = LDContext.builder(user.getId())
            .set("tier", user.getTier().name())
            .set("country", user.getCountry())
            .set("betaTester", user.isBetaTester())
            .build();

        boolean newCheckoutEnabled = ldClient.boolVariation(
            "new-checkout-flow",  // flag key
            context,
            false                 // default if LD is unavailable
        );

        if (newCheckoutEnabled) {
            return newCheckoutProcessor.process(request);
        }
        return legacyCheckoutProcessor.process(request);
    }
}
```

**Self-hosted feature flags — Unleash (open source):**

```java
// Unleash: self-hosted, no vendor lock-in, GDPR-friendly
@Bean
DefaultUnleash unleash(@Value("${unleash.app-name}") String appName,
                        @Value("${unleash.url}") String url,
                        @Value("${unleash.api-token}") String apiToken) {
    UnleashConfig config = UnleashConfig.builder()
        .appName(appName)
        .instanceId(InetAddress.getLocalHost().getHostName())
        .unleashAPI(url)
        .customHttpHeader("Authorization", apiToken)
        .build();
    return new DefaultUnleash(config);
}

// Usage — with user context for targeting:
UnleashContext context = UnleashContext.builder()
    .userId(user.getId())
    .properties(Map.of("tier", user.getTier().name()))
    .build();

if (unleash.isEnabled("new-checkout-flow", context)) {
    return newCheckoutProcessor.process(request);
}
```

---

### ❓ Why Does This Exist (Why Before What)

Deployments are risky: new code could break production. Traditional mitigation: test more before deploying. The alternative insight: deploy code without enabling features, then enable features separately. This separates deployment risk (the code is deployed and tested in dark) from feature risk (the feature is enabled when confidence is high). It also decouples engineering timelines (code merged whenever ready) from business timelines (feature announced at a specific date/event).

---

### 🧠 Mental Model / Analogy

> Feature flags are like circuit breakers on your home's electrical panel. Every circuit is installed (deployed) when the house is built. But each circuit has a breaker (flag) that controls whether it's live. You can install a new circuit for the hot tub without turning it on until the hot tub is delivered and plumbing is ready. If the hot tub causes the power to flicker, flip its breaker off instantly. The house (service) keeps running normally. Specific features (circuits) can be controlled individually without rewiring the whole house.

---

### ⚙️ How It Works (Mechanism)

**Feature flag in a Spring Boot service with fallback:**

```java
@Service
class RecommendationService {
    @Autowired DefaultUnleash unleash;
    @Autowired MLRecommendationEngine mlEngine;
    @Autowired SimpleRecommendationEngine simpleEngine;

    // OPS TOGGLE: disable ML recommendations if the ML engine is slow
    public List<Product> getRecommendations(String customerId) {
        if (!unleash.isEnabled("ml-recommendations")) {
            // Fallback to simple rule-based recommendations:
            return simpleEngine.recommend(customerId);
        }
        try {
            return mlEngine.recommend(customerId);
        } catch (MLEngineException e) {
            // ML engine error: automatic fallback (don't cascade failure):
            log.warn("ML engine failed, falling back to simple recommendations", e);
            return simpleEngine.recommend(customerId);
        }
    }
}
// Incident: ML engine is slow → engineer disables "ml-recommendations" flag
// → All users instantly switch to simple recommendations, no deployment
// → Incident resolved in seconds
```

---

### 🔄 How It Connects (Mini-Map)

```
Canary Deployment / Blue-Green
(deploy without full exposure)
        │
        ▼
Feature Flags  ◄──── (you are here)
(control feature exposure independently of deployment)
        │
        ├── Twelve-Factor App → flags stored in environment config (Factor III)
        └── Versioning Strategy → flags enable backward-compatible API transitions
```

---

### 💻 Code Example

**Flag cleanup — technical debt prevention:**

```java
// After "new-checkout-flow" is fully rolled out to 100%:
// FLAGS ARE TECHNICAL DEBT IF NOT CLEANED UP.
// Old flag = dead code + confusion for future developers.

// BEFORE cleanup (flag fully enabled, but code still conditional):
public CheckoutResult checkout(CheckoutRequest request) {
    if (unleash.isEnabled("new-checkout-flow")) {  // ← dead conditional (always true)
        return newCheckoutProcessor.process(request);
    }
    return legacyCheckoutProcessor.process(request);  // ← dead code
}

// AFTER cleanup (flag and legacy code removed):
public CheckoutResult checkout(CheckoutRequest request) {
    return newCheckoutProcessor.process(request);  // always use new flow
}
// Also: delete "new-checkout-flow" flag in Unleash/LaunchDarkly
// Also: delete legacyCheckoutProcessor class

// PROCESS: Add "delete flag" ticket to backlog at same time as enabling 100%
// Set reminder: "delete this flag by [date]" as a code comment
```

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Feature flags replace canary deployments     | They are complementary. Canary controls WHICH version of code serves traffic (at the infrastructure level). Feature flags control WHICH features are active within that code. You can use both simultaneously: canary to validate performance of new code version, feature flags to control specific feature exposure |
| Feature flags are just environment variables | Environment variables require a restart to change; feature flags are evaluated at runtime and can change in milliseconds without restart. The real-time update capability is the key differentiator                                                                                                                   |
| Feature flag evaluation is a network call    | Good feature flag SDKs (LaunchDarkly, Unleash) cache flag state locally in-process. Flag evaluation is in-memory (~microseconds). Flag state is synced from the server periodically or via streaming. Zero network latency on the hot path                                                                            |
| Feature flags are only for frontend features | Feature flags are equally valuable for backend: algorithm switches, API version control, operational kill switches, database migration gating, and microservice integration points                                                                                                                                    |

---

### 🔥 Pitfalls in Production

**Flag proliferation — technical debt at scale:**

```
SCENARIO:
  Over 2 years: 150+ flags created across 30 services.
  50 flags: state unknown — nobody knows if they're enabled or disabled in production.
  20 flags: reference deleted code paths (always evaluates to false — dead flags).
  Development: adding a new feature requires understanding 150 flag interactions.
  On-call: incident response slowed — "is this a flag issue?" check for every incident.

  Root cause: no flag lifecycle process.
  Flags created for every feature but never deleted after full rollout.

PREVENTION:
  1. Flag naming convention with type and owner:
     "rl-2024-new-checkout-team-alpha"  (rl=release toggle)
     "ops-2024-ml-recommendations-team-beta"  (ops=operational)
     Type prefix: rl (release), exp (experiment), ops (operational), perm (permission)

  2. Mandatory expiry date:
     Release toggles: max 30 days
     Experiment toggles: max 14 days
     After expiry: automated PR created to remove flag from codebase

  3. Flag inventory review (monthly):
     All team tech leads: review their service's flags
     Mark as: ACTIVE (needed), DEPRECATED (can remove), ZOMBIE (state unknown)

  4. Static analysis:
     Custom lint rule: flag key used in code but not registered in flag service → error
     Flag registered in service but not used in code for >30 days → warning

  5. Treat flags as code:
     Flag creation requires a Jira ticket with: purpose, expected lifetime, owner
     No flag without a deletion plan
```

---

### 🔗 Related Keywords

- `Canary Deployment` — infrastructure-level progressive delivery that feature flags complement
- `Blue-Green Deployment` — deployment strategy that feature flags can augment
- `Twelve-Factor App` — config externalisation principle that feature flags implement
- `Versioning Strategy` — feature flags enable backward-compatible API version transitions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TYPES        │ Release (temp), Experiment (A/B),         │
│              │ Ops (kill switch), Permission (entitlement)│
├──────────────┼───────────────────────────────────────────┤
│ EVALUATION   │ In-process cache (~microseconds), no HTTP  │
│ TARGETING    │ User ID, attributes, percentage, cohort    │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ LaunchDarkly, Unleash (OSS), Split.io,    │
│              │ AWS AppConfig, Flipt                       │
│ DANGER       │ Flag proliferation → delete after rollout │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team is building a new payment feature protected by a feature flag. The feature requires: (a) a new database column that must be present before the flag can be enabled, (b) a new downstream service dependency (PaymentGatewayV2) that must be deployed before the flag is enabled. Describe the complete deployment sequence: when do migrations run, when is the new dependency deployed, when is the flag enabled, and in what order? What happens if the flag is accidentally enabled before all dependencies are ready, and how do you prevent that?

**Q2.** You want to use feature flags for a multivariate A/B test of three checkout UI variants (Control, Variant A, Variant B) targeting 15% of users (5% each variant). The test will run for 14 days. After the test: Variant A wins (15% higher conversion rate). Describe: (a) how the flag variant assignment ensures statistical validity (avoiding novelty effect, ensuring adequate sample size), (b) how you prevent "flag contamination" (users who switch devices seeing different variants), (c) how you measure conversion rate per variant in a way that accounts for the eventual consistency of your event pipeline, and (d) the exact cleanup steps after the test concludes.
