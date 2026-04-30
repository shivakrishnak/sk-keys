---
number: "431"
category: Clean Code
difficulty: ★★☆
depends_on: CI/CD, Canary Deployment, Trunk-Based Development
used_by: A/B Testing, Canary Releases, Kill Switches
tags: #cleancode #devops #intermediate
---

# 🧹 431 — Feature Flags

`#cleancode` `#devops` `#intermediate`

⚡ TL;DR — Configuration-driven switches that enable or disable features at runtime without deploying new code.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #431         │ Category: Clean Code                 │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ CI/CD, Canary Deployment, Trunk-Based Development                 │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ A/B Testing, Canary Releases, Kill Switches                       │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

Feature flags (also called feature toggles or feature switches) are a technique that decouples code deployment from feature release. A feature's visibility and behavior is controlled through configuration at runtime — without requiring a new code deployment.

---

## 🟢 Simple Definition (Easy)

Feature flags are **on/off switches for features in running software**. Deploy the code today, flip the switch when you're ready to release — no redeployment needed.

---

## 🔵 Simple Definition (Elaborated)

Feature flags decouple deployment from release. Code can be deployed to production at any time (even if not ready), hidden behind a flag. When ready, the flag is flipped for a subset of users, then gradually rolled out. This enables trunk-based development, dark launches, A/B testing, canary releases, and instant kill switches for broken features.

---

## 🔩 First Principles Explanation

**The core problem:**
Feature branches diverge from main for weeks. Merging is painful. You cannot test a feature in production before full release. When something breaks in prod, you need a redeployment to revert.

**The insight:**
> "Deploy everything to production continuously. Release features deliberately via configuration."

```
// Feature flag in code
if (featureFlags.isEnabled("new-checkout-flow", user)) {
    return newCheckoutService.process(cart);
} else {
    return legacyCheckoutService.process(cart);
}
// Production has both paths. The flag decides which path runs.
```

---

## ❓ Why Does This Exist (Why Before What)

Without feature flags, every incomplete feature needs its own long-lived branch — diverging from main, hard to merge, hidden integration issues. Flags allow continuous integration with all code on main, with features hidden until they're ready.

---

## 🧠 Mental Model / Analogy

> Think of a light switch that someone installed but left off. The wiring (code) is in the wall (production), fully installed. The switch (flag) controls whether the light (feature) is visible. You can inspect and test the wiring without turning on the light for users.

---

## ⚙️ How It Works (Mechanism)

```
Types of feature flags:

  Release Toggle     --> hide incomplete features (short-lived, weeks)
  Experiment Toggle  --> A/B testing, measure user behavior
  Ops Toggle         --> kill switch for production incidents (long-lived)
  Permission Toggle  --> enable for specific users, roles, or plans

Lifecycle:
  Deploy (flag=OFF) --> QA with flag=ON internally
                    --> Gradual rollout: 5% --> 20% --> 50% --> 100%
                    --> Full rollout --> REMOVE the flag (critical!)
```

---

## 🔄 How It Connects (Mini-Map)

```
[Code deployed to prod]
         ↓
  [Feature Flag Service]
   isEnabled("feature-x", user)?
         |
   YES --+-- NO
   |             |
[New Path]   [Old Path]
```

---

## 💻 Code Example

```java
// Feature flag wiring — Spring Boot example
@Service
public class CheckoutService {
    private final FeatureFlagService flags;
    private final NewCheckoutV2 newCheckout;
    private final LegacyCheckout legacyCheckout;

    public OrderResult processCart(Cart cart, User user) {
        if (flags.isEnabled("new-checkout-v2", user)) {
            return newCheckout.process(cart);      // new code path
        }
        return legacyCheckout.process(cart);       // safe fallback
    }
}

// Simple flag service backed by config / database / LaunchDarkly
@Component
public class FeatureFlagService {
    private final Map<String, Boolean> defaults = Map.of(
        "new-checkout-v2", false  // OFF by default
    );

    public boolean isEnabled(String flagName, User user) {
        // Could check: user.isInternal(), rolloutPercentage, etc.
        return defaults.getOrDefault(flagName, false);
    }
}

// Kill switch pattern (ops toggle)
public Payment processPayment(PaymentRequest req) {
    if (!flags.isEnabled("payment-v2-enabled")) {
        throw new ServiceUnavailableException("Payments temporarily unavailable");
    }
    return paymentV2Service.process(req);
}
```

---

## 🔁 Flow / Lifecycle

```
1. Wrap new feature code in flag check (flag=OFF for all)
        ↓
2. Deploy to production — no users see the feature
        ↓
3. Enable flag for internal users only — test in real prod environment
        ↓
4. Gradual rollout: 5% --> 20% --> 50% --> 100% users
        ↓
5. Monitor error rates, latency, and business metrics at each step
        ↓
6. Full rollout confirmed --> REMOVE the flag (eliminate dead code paths)
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Feature flags = environment variables | Env vars are static per deploy; flags are dynamic, per-user, runtime |
| They add significant performance overhead | In-memory map lookup is negligible; remote calls need caching |
| Old flags are fine to keep | Dead flags = permanent technical debt with 2 code paths each |
| Only for large companies with big teams | Any team doing CI/CD benefits from feature flags |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Flag Technical Debt**
Accumulating old, dead flags nobody dares to remove. Each flag means 2 code paths that must both be tested.
Fix: set a TTL for each flag at creation time; remove within one sprint of full rollout.

**Pitfall 2: Testing Matrix Explosion**
N simultaneous flags = up to 2^N code path combinations.
Fix: limit simultaneous active flags; document incompatible combinations explicitly.

**Pitfall 3: Flag in Wrong Layer**
Flag checks in domain/business logic instead of at the service or controller boundary.
Fix: keep flags at entry points; the feature implementation itself should be flag-agnostic.

---

## 🔗 Related Keywords

- **Canary Deployment** — gradual rollout at infrastructure level; flags achieve this at code level
- **A/B Testing** — experiment toggles used for measuring user behavior differences
- **Technical Debt** — every unused flag is debt; remove it promptly after full rollout
- **Trunk-Based Development** — short-lived branches; flags enable this safely at scale
- **Kill Switch** — ops toggle that disables a feature during incidents without redeployment

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Decouple code deployment from feature release  │
│              │ using runtime configuration switches           │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ CI/CD, gradual rollouts, A/B tests, kill      │
│              │ switches, dark launches                        │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Using flags to permanently hide dead code or  │
│              │ to replace proper API versioning              │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Ship code continuously; release features      │
│              │  deliberately and safely"                      │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary Deployment --> A/B Testing --> CI/CD    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** How do feature flags enable trunk-based development for large teams with many parallel features?  
**Q2.** What is the difference between a release toggle and a kill switch (ops toggle)?  
**Q3.** How would you test a feature that is behind a flag — what testing strategy ensures both code paths are covered?

