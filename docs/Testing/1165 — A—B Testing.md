---
layout: default
title: "A/B Testing"
parent: "Testing"
nav_order: 1165
permalink: /testing/a-b-testing/
number: "1165"
category: Testing
difficulty: ★★★
depends_on: Feature Flags, Statistical Significance, Metrics
used_by: Product Managers, Developers, Data Scientists
related: Feature Flags, Canary Deployment, Blue-Green Deployment, Observability
tags:
  - testing
  - a-b-testing
  - experimentation
  - product
---

# 1165 — A/B Testing

⚡ TL;DR — A/B testing is a controlled experiment that splits users into groups, shows each group a different variant (A or B), and uses statistical analysis to determine which variant performs better on a target metric.

| #1165           | Category: Testing                                                      | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Feature Flags, Statistical Significance, Metrics                       |                 |
| **Used by:**    | Product Managers, Developers, Data Scientists                          |                 |
| **Related:**    | Feature Flags, Canary Deployment, Blue-Green Deployment, Observability |                 |

### 🔥 The Problem This Solves

OPINION-DRIVEN PRODUCT DECISIONS:
"The checkout button should be green." "No, it should be red." "I think we should show the price before the product image." These debates happen constantly and are resolved by: (a) HiPPO (Highest Paid Person's Opinion), (b) A/B test. Option (b) is the data-driven approach. Without A/B testing, product decisions are based on intuition, which is wrong ~50% of the time.

NOT THE SAME AS SOFTWARE TESTING:
A/B testing is NOT a software testing technique (like unit tests). It's a **product experimentation technique** — testing product hypotheses against real users in production to make data-driven decisions. It requires live traffic, real users, and statistical rigor.

### 📘 Textbook Definition

**A/B testing** (also called split testing or bucket testing) is a randomized controlled experiment run in production: users are randomly assigned to a **control group** (variant A — current behavior) or a **treatment group** (variant B — new behavior). Both groups are measured on a **primary metric** (e.g., conversion rate, click-through rate, session duration). After collecting sufficient data (determined by power analysis), statistical significance testing determines whether the observed difference is real or due to chance. If statistically significant AND practically significant, the winning variant is rolled out to all users.

### ⏱️ Understand It in 30 Seconds

**One line:**
A/B test = two groups, two variants, real users, data decides — not opinion.

**One analogy:**

> A/B testing is a **randomized clinical trial for product decisions**: Group A gets the placebo (current design), Group B gets the treatment (new design). After N weeks, measure outcomes. If the treatment group shows statistically significant improvement — roll it out. Same scientific rigor as medicine, applied to software products.

### 🔩 First Principles Explanation

STATISTICAL FOUNDATIONS:

```
1. HYPOTHESIS:
   H₀ (null): Variant B has no effect on conversion rate
   H₁ (alternative): Variant B increases conversion rate

2. SAMPLE SIZE (power analysis):
   Before starting: calculate minimum users needed

   Inputs:
   - Baseline conversion rate: 5% (current)
   - Minimum Detectable Effect (MDE): 1% (we want to detect ≥1% improvement)
   - Statistical power: 80% (80% chance of detecting a real effect)
   - Significance level: α = 0.05 (5% false positive rate)

   Result: ~7,500 users per variant (15,000 total)

   DON'T run the test until you have this sample size
   (peeking at results early and stopping = p-hacking)

3. RANDOMIZATION:
   User assignment: hash(user_id + experiment_id) % 100
   → Deterministic: same user always in same group
   → Roughly 50/50 split

   Criteria:
   - Assignment is sticky (user doesn't flip between groups)
   - Assignment is independent of behavior (not biased by user characteristics)

4. MEASUREMENT:
   Primary metric: checkout_completed / users_shown_checkout_page
   Guard rails: don't let B improve conversion but break page load time

5. STATISTICAL SIGNIFICANCE:
   After required sample size is collected:
   p-value < 0.05 → statistically significant

   p-value = probability of observing this result if H₀ is true
   p = 0.02 → "2% chance this result is just random variation"
   → Reject H₀ → Variant B has a real effect

6. PRACTICAL SIGNIFICANCE:
   Statistical significance ≠ practical significance
   p = 0.001, effect = +0.01% conversion → statistically real but not worth shipping

   Always check: "Is the effect size worth the engineering cost?"
```

IMPLEMENTATION:

```java
// Feature flag drives A/B variant assignment
@GetMapping("/checkout")
public String checkout(HttpServletRequest request) {
    String userId = getCurrentUserId(request);

    // Experiment service: consistent assignment based on userId
    Variant variant = experimentService.assign(userId, "checkout-button-color");

    if (variant == Variant.TREATMENT) {
        return "checkout_green_button";  // Variant B
    } else {
        return "checkout_red_button";    // Variant A (control)
    }
}

// Track conversion event
@PostMapping("/order")
public ResponseEntity<?> placeOrder(...) {
    Order order = orderService.createOrder(...);

    // Track experiment event for metrics
    analyticsService.track(userId, "order_placed", Map.of(
        "experiment", "checkout-button-color",
        "variant", experimentService.getVariant(userId, "checkout-button-color").name()
    ));

    return ResponseEntity.ok(order);
}
```

### 🧪 Thought Experiment

THE MULTIPLE TESTING PROBLEM:

```
Team runs 20 A/B tests simultaneously.
Each test uses α=0.05 (5% false positive rate).
All 20 tests show no real effect (H₀ is true for all).

Expected false positives: 20 × 0.05 = 1 test will appear significant by chance.
Team ships Variant B of that test.
Result: shipped a "winner" that has no real effect.

Solutions:
  1. Bonferroni correction: α_adjusted = α / n_tests (more conservative)
  2. False Discovery Rate (FDR): Benjamini-Hochberg procedure
  3. Sequential testing with pre-registered hypotheses
  4. Replicate: if a result is truly significant, it should replicate in a new test

This is why discipline matters: pre-register hypothesis, don't peek, correct for multiple testing.
```

### 🧠 Mental Model / Analogy

> A/B testing is **democracy for product decisions**: instead of a single decision-maker (HiPPO), thousands of users "vote" through their behavior. The statistical test is the vote-counting mechanism — it separates real preferences from noise. Like democracy, it requires rules (proper randomization, sufficient turnout/sample size) to produce valid results.

### 📶 Gradual Depth — Four Levels

**Level 1:** Split users 50/50 randomly. Show A to half, B to other half. Measure clicks/conversions. If B is better and difference is statistically significant — ship B.

**Level 2:** Pre-calculate sample size (power analysis) before starting. Don't stop early ("peeking problem" = inflated false positive rate). Use statistical significance (p < 0.05) AND practical significance (effect size matters). Track guard rail metrics (don't improve conversion while breaking performance).

**Level 3:** Implementation: feature flag service (LaunchDarkly, Optimizely, custom) assigns users deterministically using hash of user ID + experiment ID. Events tracked to analytics (Segment, Mixpanel, custom data pipeline). Analysis: t-test for means, chi-squared for proportions, Mann-Whitney U for non-normal distributions. Multiple variant testing (A/B/C/D): ANOVA + post-hoc tests for multiple comparisons.

**Level 4:** Industry-scale A/B testing: Google runs 10,000+ experiments per year; Netflix runs 200+ simultaneously. Challenges: (1) network effects — users interact, so A group behavior is influenced by B group (e.g., social features); (2) novelty effect — new features get inflated engagement initially; measure long-term; (3) holdout groups — a small % of users permanently excluded from all experiments to measure the cumulative effect of shipped changes; (4) Bayesian A/B testing — alternative to frequentist (provides probability B beats A rather than p-values; allows continuous monitoring without peeking problem); (5) multi-armed bandit — dynamically allocate more traffic to winning variant during the experiment (trading statistical purity for faster deployment of winners).

### 💻 Code Example

```python
# Sample size calculation (Python, scipy)
from scipy import stats
import math

def calculate_sample_size(baseline_rate, mde, alpha=0.05, power=0.8):
    """
    baseline_rate: current conversion rate (e.g., 0.05 for 5%)
    mde: minimum detectable effect (e.g., 0.01 for 1% absolute improvement)
    """
    treatment_rate = baseline_rate + mde

    # Pooled standard error
    pooled_p = (baseline_rate + treatment_rate) / 2

    z_alpha = stats.norm.ppf(1 - alpha/2)  # 1.96 for alpha=0.05
    z_beta = stats.norm.ppf(power)          # 0.84 for power=0.8

    n = (z_alpha + z_beta)**2 * (2 * pooled_p * (1 - pooled_p)) / (mde**2)
    return math.ceil(n)

n = calculate_sample_size(baseline_rate=0.05, mde=0.01)
print(f"Users needed per variant: {n:,}")  # ~7,500
print(f"Total users needed: {n*2:,}")     # ~15,000
```

```java
// Deterministic user assignment
public class ExperimentService {
    public Variant assign(String userId, String experimentId) {
        // Deterministic hash: same userId always → same variant
        int hash = Math.abs((userId + experimentId).hashCode()) % 100;
        return hash < 50 ? Variant.CONTROL : Variant.TREATMENT;
    }
}
```

### ⚖️ Comparison Table

|                    | A/B Test                     | Canary Deployment              | Feature Flag            |
| ------------------ | ---------------------------- | ------------------------------ | ----------------------- |
| Purpose            | Measure user behavior metric | Validate stability/correctness | Control feature rollout |
| Primary metric     | Business metric (conversion) | Error rate, latency            | N/A                     |
| Statistical rigor  | Required                     | Not required                   | Not required            |
| Who decides winner | Statistics (p-value)         | Engineer (error rate)          | Product/business        |

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                      |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| "Stop the test when p < 0.05"                  | "Peeking" inflates false positive rate — run to predetermined sample size                                    |
| "A/B test everything"                          | Only test decisions with high uncertainty and sufficient traffic; low-traffic pages can't reach significance |
| "Statistical significance = we should ship it" | Also requires practical significance — a 0.01% improvement isn't worth shipping                              |

### 🚨 Failure Modes & Diagnosis

**1. Sample Ratio Mismatch (SRM)**
Cause: Assignment isn't actually 50/50 — users who see B are systematically different from users who see A (e.g., caching bug exposes B only to logged-in users).
Detection: Check if A:B ratio deviates significantly from 50:50 (chi-squared test).
Impact: Invalidates the entire experiment — results are not causal.

**2. Novelty Effect**
Cause: New experience gets extra attention/engagement due to novelty, not because it's better.
Detection: Check if B's advantage decays over time (plot metric by days since exposure).
Fix: Run experiment longer; analyze returning users separately.

**3. Interaction Effects Between Simultaneous Experiments**
Cause: User in experiment 1 Treatment × experiment 2 Treatment — interaction unknown.
Fix: Mutual exclusivity for related experiments; interaction analysis for known interactions.

### 🔗 Related Keywords

- **Prerequisites:** Feature Flags, Statistical Significance, Metrics
- **Related:** Canary Deployment, Blue-Green Deployment, LaunchDarkly, Optimizely, Bayesian Statistics

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Controlled experiment: A vs B, real users │
├──────────────┼───────────────────────────────────────────┤
│ PROCESS      │ Hypothesis → sample size → run →         │
│              │ p-value → practical significance → ship  │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Pre-calculate sample size; don't peek     │
├──────────────┼───────────────────────────────────────────┤
│ NOT SAME AS  │ Canary (stability) or feature flags      │
│              │ (rollout) — those don't measure metrics  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Data beats opinion: let users vote      │
│              │  through behavior, not humans through    │
│              │  meetings"                               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The "peeking problem" in A/B testing: standard t-tests assume a fixed sample size known in advance. When you check results repeatedly during an experiment and stop when p < 0.05, the actual false positive rate is much higher than 5%. Describe: (1) mathematically why sequential peeking inflates false positive rate (each "peek" is an independent chance to get p < 0.05 by chance — with 20 peeks, false positive rate approaches 30%), (2) sequential testing methods that allow continuous monitoring without inflation: the Sequential Probability Ratio Test (SPRT), always-valid p-values (anytime inference), and Bayesian approaches (posterior probability), and (3) why these methods are increasingly used at high-traffic companies (Airbnb, Netflix) where waiting for fixed sample sizes means slow decision velocity.

**Q2.** A/B testing in a recommendation system: the recommendation algorithm affects what products users see, which affects what they buy, which affects what the algorithm recommends next. This is a "feedback loop" — A and B groups interact with the system differently over time. Describe: (1) why standard A/B testing assumptions (independence between users, stable treatment effect) are violated in recommendation systems, (2) how "interleaving" (a variant where items from both algorithms are interleaved and clicks indicate preference) addresses this, (3) the holdout group strategy for measuring long-term recommendation quality (permanently holding out 1% from algorithm improvements), and (4) how to properly measure the business value of a recommendation change 90 days after deployment vs. at experiment conclusion.
