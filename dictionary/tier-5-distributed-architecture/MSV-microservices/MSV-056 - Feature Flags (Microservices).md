---
layout: default
title: "Feature Flags (Microservices)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 56
permalink: /microservices/feature-flags-microservices/
id: MSV-056
category: Microservices
difficulty: ★★☆
depends_on: Canary Deployment (Microservices), Configuration Management, Observability & SRE
used_by: Canary Deployment (Microservices), Blue-Green Deployment, Zero-Downtime Deployment
related: Canary Deployment (Microservices), Blue-Green Deployment, Backward Compatibility
tags:
  - microservices
  - deployment
  - feature-management
  - operations
  - intermediate
---

# MSV-056 - Feature Flags (Microservices)

⚡ TL;DR - Feature flags (also called feature toggles) wrap code paths in conditional checks that can be toggled on/off at runtime - without redeployment - enabling dark launches, gradual rollouts, A/B tests, and instant rollback of individual features.

| #671            | Category: Microservices                                                            | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Canary Deployment (Microservices), Configuration Management, Observability & SRE   |                 |
| **Used by:**    | Canary Deployment (Microservices), Blue-Green Deployment, Zero-Downtime Deployment |                 |
| **Related:**    | Canary Deployment (Microservices), Blue-Green Deployment, Backward Compatibility   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your team finishes a large feature (new checkout flow) after 6 weeks. The feature is merged but not ready for all users - 3 edge cases still being fixed. You can't deploy without releasing the feature; the code is already merged. Your only option: keep the feature in a separate long-lived branch, merge it all at once when complete, then deal with a massive merge conflict. Alternatively, you deploy it and 100% of users see the half-finished feature.

**THE BREAKING POINT:**
Code deployment and feature release should be independent. A deployment should be a safe, low-risk operation. Feature release should be a conscious, controlled decision.

**THE INVENTION MOMENT:**
Feature flags decouple deployment (when code goes to production) from release (when users see the feature). Code is deployed continuously; features are released intentionally, to specific user segments, at a controlled pace.

---

### 📘 Textbook Definition

A **feature flag** (also: feature toggle, feature switch) is a conditional in application code that gates a code path behind a runtime-evaluated boolean. The boolean is controlled by a configuration system (environment variable, config service, or dedicated feature flag platform). At runtime, the service queries the flag system: if flag `new-checkout-flow` is `true` for this user/context, execute the new code path; otherwise execute the old code path. The flag state can be changed without redeployment, enabling: dark launches (code deployed, flag off), gradual rollouts (flag on for 5% of users), targeted releases (flag on for users in beta cohort), and kill switches (instantly disable a problematic feature).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A runtime on/off switch for features - without redeploying code.

**One analogy:**

> Light switches in a new building. The electrical wiring for every room is installed (code is deployed). But each room's lights are controlled by individual switches (feature flags). The building is fully wired before any lights are turned on. Each room's lights are switched on deliberately, one at a time, when ready.

**One insight:**
Feature flags shift the risk boundary. Without flags, deployment = release (high risk). With flags, deployment is low-risk (flag is off; no user impact); release is a deliberate choice (flag is turned on; can be turned off instantly).

---

### 🔩 First Principles Explanation

**FLAG TYPES:**

| Type                  | Purpose                              | Lifespan      |
| --------------------- | ------------------------------------ | ------------- |
| **Release toggle**    | Dark launch; gradual rollout         | Days to weeks |
| **Experiment toggle** | A/B testing                          | Days to weeks |
| **Ops toggle**        | Kill switch for problematic features | Long-lived    |
| **Permission toggle** | Feature for specific user cohort     | Long-lived    |

**FLAG EVALUATION CONTEXT:**

```
Input:  { userId, userCohort, region, environment, requestAttributes }
Flag:   { name: "new-checkout-flow", rules: [...] }
Output: true / false

Rules example:
  - IF userId IN beta_users_list → true
  - IF random(userId) < 0.05 → true (5% rollout)
  - ELSE → false
```

**IMPLEMENTATION OPTIONS:**

| Approach                           | Simplicity    | Power             | Production-Ready           |
| ---------------------------------- | ------------- | ----------------- | -------------------------- |
| Environment variable               | Simple        | Low (binary only) | No (restart needed)        |
| Config file                        | Simple        | Low               | Partial                    |
| Custom config service              | Medium        | Medium            | Yes                        |
| LaunchDarkly / Unleash / Flagsmith | Complex setup | High              | Yes (real-time, targeting) |

**THE CORE LIFECYCLE (Release Toggle):**

```
1. Feature in development: flag off (dark launch)
   All users get old path; new code is deployed but dormant

2. Internal testing: flag on for internal users only
   Engineers and QA test new path in production

3. Beta rollout: flag on for 5% of users
   Monitor metrics; look for errors/regressions

4. Gradual rollout: 5% → 25% → 50% → 100%
   Each step monitored; rollback = toggle flag off

5. General availability: flag on for 100%
   Feature fully released

6. Flag cleanup: remove flag and dead code path
   Critical: stale flags are a maintenance burden
```

**THE TRADE-OFFS:**
**Gain:** Deployment decoupled from release; instant rollback of any feature; dark launches; gradual rollout; A/B testing; trunk-based development enabled.
**Cost:** Code complexity (branching logic everywhere); stale flags become technical debt; test matrix explosion (every flag combination needs testing); flag evaluation latency (if remote); need for flag governance.

---

### 🧪 Thought Experiment

**SETUP:**
You have a `new-checkout-flow` flag. It's been on for 100% of users for 6 months. The original `old-checkout-flow` code path is still in the codebase, wrapped in `if (!flag)`.

**THE ACCIDENTAL EXPERIMENT:**
A new engineer joins. They write a unit test for checkout. They accidentally test the old code path (flag is false in tests by default). The old code path has a critical security bug that was never noticed - because the old path also ran in tests. The bug exists in the deployed binary; it's just never executed in production (flag is always true). But the security scanner finds it.

**THE LESSON:**
Flags that have been 100% for more than a few weeks should be cleaned up (removed from code). Stale flags create dead code with hidden bugs, increase test complexity, and confuse new developers. Flag lifecycle management is as important as flag creation.

---

### 🧠 Mental Model / Analogy

> Feature flags are like theatre stage lighting. A scene (feature) can be fully designed and staged (deployed) in the dark. The director (product team) controls when each light (flag) goes on - one spotlight at a time, for specific parts of the audience (user segments). If a scene isn't working, the light is turned off instantly. The stage crew doesn't need to re-build the set (redeploy) to change the lighting (toggle the flag).

- "Set fully built" → code deployed to production
- "Lights off" → flag disabled (dark launch)
- "Director controls lights" → product/ops team controls flags
- "Specific audience spotlight" → user segment targeting
- "Turn off instantly" → instant rollback via flag toggle

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A feature flag is an on/off switch for a software feature. The feature's code is deployed, but the switch controls whether users see it. You can flip the switch without redeploying the software.

**Level 2 - Implementation in code (junior developer):**
Simplest approach: `if (featureFlagService.isEnabled("new-checkout-flow", userId))`. Use Unleash (open-source) or LaunchDarkly as the flag service. Flags are evaluated per-request; the service queries the flag platform and returns true/false based on configured rules.

**Level 3 - Gradual rollout mechanics (mid-level engineer):**
Gradual rollout uses consistent hashing: `hash(userId + flagName) % 100 < rolloutPercentage`. This ensures the same user always gets the same flag value (stable experience) even without session-level state. For 5% rollout: users whose hash value falls in 0–4 see the new feature. When rollout is increased to 10%, users 0–9 see the new feature - all existing 5% still get it, plus a new 5%.

**Level 4 - Flag governance at scale (senior/staff):**
At hundreds of microservices and thousands of flags, governance becomes critical. Problems: flag evaluation latency (each flag is a remote call); stale flags (technical debt); testing matrix explosion; flag dependency hell (flag A depends on flag B). Solutions: local flag cache with remote sync (LaunchDarkly SDK caches flags locally; changes sync async); flag ownership policy (each flag has an owner + expiry date); automatic stale flag detection; contract testing for flag combinations. Facebook uses a technique called "gating": flags are evaluated during feature development, but a gating system automatically removes them once a feature has been 100% rolled out for N days.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ Feature Flag Evaluation Flow (per request)              │
└─────────────────────────────────────────────────────────┘

Request arrives at Order Service
  ↓
Extract context: { userId: "u123", region: "EU", role: "beta" }
  ↓
Query flag service (cached, local):
  FlagService.isEnabled("new-checkout-flow", context)

  Flag rules (evaluated top-to-bottom, first match wins):
  1. IF userId IN ops_override_list → false  (kill switch)
  2. IF role == "internal" → true            (internal users)
  3. IF region == "EU" AND rollout < 25% → false (not in EU yet)
  4. IF hash(userId + "new-checkout-flow") % 100 < 5 → true
  5. ELSE → false

  Result: false (user u123 not in 5% cohort)
  ↓
Execute old checkout path
  ↓
Return response
```

---

### 💻 Code Example

**Spring Boot + Unleash feature flags:**

```java
@Service
public class CheckoutService {

    private final Unleash unleash;

    public CheckoutService(Unleash unleash) {
        this.unleash = unleash;
    }

    public OrderResult checkout(CartRequest cart, String userId) {
        // Evaluate flag with user context
        UnleashContext context = UnleashContext.builder()
            .userId(userId)
            .build();

        if (unleash.isEnabled("new-checkout-flow", context)) {
            return newCheckoutFlow(cart);
        } else {
            return legacyCheckoutFlow(cart);
        }
    }

    private OrderResult newCheckoutFlow(CartRequest cart) {
        // new implementation
    }

    private OrderResult legacyCheckoutFlow(CartRequest cart) {
        // old implementation
    }
}
```

**Unleash configuration (application.yml):**

```yaml
unleash:
  app-name: order-service
  instance-id: ${POD_NAME}
  unleash-api: http://unleash-service:4242/api
  api-token: ${UNLEASH_API_TOKEN}
  fetch-toggles-interval: 15 # sync every 15 seconds
  synchronous-fetch-on-initialisation: true
```

**Flag rule definition (Unleash UI / API):**

```json
{
  "name": "new-checkout-flow",
  "enabled": true,
  "strategies": [
    {
      "name": "userWithId",
      "parameters": {
        "userIds": "engineer1,engineer2,qa1"
      }
    },
    {
      "name": "gradualRolloutUserId",
      "parameters": {
        "percentage": "5",
        "groupId": "new-checkout-flow"
      }
    }
  ]
}
```

---

### ⚖️ Comparison Table

| Approach             | Decouples Deploy/Release | Gradual Rollout | Instant Rollback        | Complexity   |
| -------------------- | ------------------------ | --------------- | ----------------------- | ------------ |
| **Feature Flags**    | Yes                      | Yes             | Yes (toggle)            | Medium       |
| Canary Deployment    | Partially                | Yes             | Seconds (rollout abort) | High (infra) |
| Blue-Green           | Yes                      | No (0/100%)     | Yes (switch)            | High (infra) |
| Branch-based release | No                       | No              | Re-deploy               | Low (code)   |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                   |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Feature flags replace deployment strategies       | They complement each other; flags control feature visibility, canary/blue-green control deployment safety |
| Feature flags are only for new features           | Ops toggles (kill switches) are long-lived and critical for operational stability                         |
| Once a feature is 100%, the flag can stay forever | Stale flags create dead code, confusion, and hidden bugs; clean up flags within weeks of 100% rollout     |
| Feature flags are free (performance)              | Flag evaluation is per-request; cache locally; avoid remote calls on critical hot paths                   |
| Flag-on and flag-off code paths both stay tested  | Old (flag-off) code paths typically receive less test attention; test both explicitly                     |

---

### 🚨 Failure Modes & Diagnosis

**Flag Service Unavailable - All Flags Default to Off**

**Symptom:** Flag service goes down; all flags evaluate to false; new checkout flow disabled for 100% of users; sudden drop in new-flow metrics.

**Root Cause:** Flag SDK has no local cache; every evaluation is a remote call; when remote is unavailable, evaluation returns default (false).

**Fix:** Configure SDK with local bootstrap cache (flags cached from last sync); set fallback default per flag based on operational meaning: kill switch defaults to false (safe), release toggle defaults to false (safe).

---

**Flag Evaluation Latency Spikes**

**Symptom:** P99 request latency increases from 50ms to 500ms; traced to flag evaluation.

**Root Cause:** Flag evaluation is making a synchronous HTTP call per request; flag service is slow.

**Fix:** Use SDK with background sync (LaunchDarkly, Unleash SDK); flags are cached in-process and updated async; flag evaluation is < 1ms (in-memory map lookup).

---

### 🔗 Related Keywords

**Prerequisites:** `Canary Deployment (Microservices)`, `Configuration Management`, `Observability & SRE`

**Builds On This:** `Canary Deployment (Microservices)`, `Blue-Green Deployment`

**Related Patterns:** `Backward Compatibility`, `Trunk-Based Development`, `A/B Testing`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Runtime on/off switch for code paths;     │
│              │ no redeployment required                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY PROPERTY │ Deploy ≠ Release; instant rollback        │
├──────────────┼───────────────────────────────────────────┤
│ TYPES        │ Release, Experiment, Ops (kill switch),   │
│              │ Permission                                │
├──────────────┼───────────────────────────────────────────┤
│ FLAG LIFECYCLE│ Dark launch → internal → beta → gradual  │
│              │ → 100% → REMOVE FLAG                     │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ LaunchDarkly, Unleash, Flagsmith, Flipt   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ship the code; decide when to release it"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a `new-checkout-flow` flag at 100% rollout for 3 months. A new engineer refactors the checkout service and removes the flag-gating, keeping only the new flow code. This goes through code review and is deployed. Three weeks later, a different team adds a "regression test suite" using the old checkout flow endpoint (from a spec written when the flag was being rolled out). Their tests pass. Why is this risky, and what process would prevent this kind of scenario?

**Q2.** Your team is about to deploy a high-risk new pricing engine to 20 microservices simultaneously. The deployment is a Friday afternoon release (mandatory due to business deadline). Design a feature flag strategy that: (a) ensures all 20 services can deploy safely; (b) allows gradual rollout starting Monday; (c) provides an instant kill switch if the pricing engine produces incorrect prices; (d) ensures consistent flag state across all 20 services during evaluation.
