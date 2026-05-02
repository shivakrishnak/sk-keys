---
layout: default
title: "Progressive Delivery"
parent: "CI/CD"
nav_order: 1028
permalink: /ci-cd/progressive-delivery/
number: "1028"
category: CI/CD
difficulty: ★★★
depends_on: Deployment Pipeline, Feature Flags, Canary Analysis, Continuous Deployment
used_by: Canary Analysis, Rollback Strategy, DORA Metrics
related: Canary Analysis, Feature Flags, Blue-Green Deployment, Rollback Strategy
tags:
  - cicd
  - devops
  - deep-dive
  - deployment
  - advanced
---

# 1028 — Progressive Delivery

⚡ TL;DR — Progressive delivery deploys new code to a gradually increasing subset of production traffic, using real metrics to determine whether to proceed or roll back before full exposure.

| #1028 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Deployment Pipeline, Feature Flags, Canary Analysis, Continuous Deployment | |
| **Used by:** | Canary Analysis, Rollback Strategy, DORA Metrics | |
| **Related:** | Canary Analysis, Feature Flags, Blue-Green Deployment, Rollback Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A deployment pipeline successfully passes all automated tests. The code is deployed to 100% of production traffic instantaneously. Within 3 minutes: the payment service is experiencing 15% error rates. The new code introduced a subtle race condition that only appears under production load with real database data. Pre-production testing never caught it. 100% of users are affected before the first alert fires. 200,000 active sessions are impacted. The rollback takes 8 minutes.

**THE BREAKING POINT:**
No amount of pre-production testing can perfectly simulate production behaviour — production data volume, actual user behaviour patterns, hardware configuration, and concurrent load are unique. An all-or-nothing deployment (0% → 100% instantly) means any bug that only appears in production affects 100% of users immediately.

**THE INVENTION MOMENT:**
This is exactly why progressive delivery was created: use production itself as the final validation environment, but limit exposure — deploy to 1% of traffic, observe real metrics, and only expand exposure when the new code proves itself safe.

---

### 📘 Textbook Definition

**Progressive delivery** is a deployment technique that gradually exposes a new version of software to increasingly larger portions of production traffic, using real production metrics (error rate, latency, conversion rate) as the promotion gate between exposure increments. Delivery progresses from 1% → 5% → 25% → 50% → 100% (or any defined increment sequence). At each stage, automated analysis determines whether the new version is performing within acceptable bounds relative to a baseline. If metrics degrade, the rollout is halted and traffic is returned to the previous version. Progressive delivery encompasses several related patterns: **canary releases** (small fixed percentage), **ring deployments** (geographic or user segment rings), and **blue/green deployments** (instantaneous switch with easy rollback). Tools: Argo Rollouts, Flagger, LaunchDarkly, Flagsmith, AWS CodeDeploy, Spinnaker.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Deploy to 1% of users first, check that nothing breaks, then gradually expand to everyone.

**One analogy:**
> Progressive delivery is like a pharmaceutical drug's clinical trial phases. Phase I: small cohort (1–5%), observe safety. Phase II: larger cohort (25%), observe efficacy and safety. Phase III: pre-full cohort (50%), confirm. Production rollout: 100%. Each phase requires passing defined criteria before advancing. An adverse reaction at Phase I stops the trial — affecting few people. An adverse reaction discovered in Phase III affects few more but production at Phase I scale is halted first.

**One insight:**
Progressive delivery turns production into the most realistic test environment — because it IS the production environment. The key insight is that you're not eliminating production risk; you're partitioning it. By limiting exposure to 1% initially, a bug affects 1% of users before being caught. The same bug in an all-or-nothing deploy affects 100% of users before anyone knows.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Production behaviour cannot be perfectly simulated in pre-production — some bugs only appear with real data and real load.
2. Any new deployment carries risk — progressive delivery partitions that risk across time and percentage rather than exposing it all at once.
3. Automated metric analysis enables faster, more consistent promotion decisions than human judgment, especially at 3am.

**DERIVED DESIGN:**
Progressive delivery requires three components:

1. **Traffic splitting**: ability to send X% of production traffic to the new version and (100-X)% to the old version. Implementation: load balancer weight configuration, service mesh (Istio/Linkerd traffic policies), or feature flag service (LaunchDarkly percentage rollout).

2. **Canary analysis**: automated comparison of new version metrics vs baseline. Tools: Kayenta (Argo Rollouts' analysis provider), Prometheus queries, Datadog monitors. Analysis runs for a defined period at each exposure level before promotion decision.

3. **Automated promotion/rollback**: based on analysis result, the system automatically advances to the next exposure percentage (promote) or reverts traffic to the previous version (rollback). Human intervention is the exception, not the rule.

**THE TRADE-OFFS:**
**Gain:** Limits blast radius of production bugs; uses real production data for validation; enables automated rollback before full user impact.
**Cost:** Operational complexity — requires traffic splitting, analysis tooling, and two running versions simultaneously. Stateful services (databases with schema changes) require careful migration strategy — you can't easily run two DB schema versions in parallel. Takes longer to fully deploy than all-or-nothing.

---

### 🧪 Thought Experiment

**SETUP:**
A recommendation engine update optimises the ML model weights. Pre-production tests show 12% improvement in click-through rate. But the update also has a memory leak that only appears after 4+ hours of production load. Two deployment strategies: all-or-nothing vs progressive delivery.

**WHAT HAPPENS WITHOUT PROGRESSIVE DELIVERY:**
Deploy to 100% instantly. Memory leak undetected in CI (only appears after 4 hours). 4 hours post-deploy: all recommendation service pods begin OOMKilling. Recommendation service down for 1.5 hours affecting all users while investigating and patching.

**WHAT HAPPENS WITH PROGRESSIVE DELIVERY:**
Deploy to 1% of traffic (canary). After 6 hours (allowing memory leak to manifest): canary pods show memory usage 340% above baseline. Automated analysis: FAIL. Rollback: canary traffic returned to old version. 1% of users experienced slow recommendations for 6 hours. Root cause: memory leak. Fixed in next PR. New version re-deployed progressively. Memory stable. Rollout advances to 100% over 24 hours.

**THE INSIGHT:**
Same bug, radically different user impact: 100% × 1.5h vs 1% × 6h. By staging the rollout, a 6-hour monitoring window at 1% catches a bug that only manifests at 4 hours — with only 1% user exposure. All-or-nothing leaves you blind until the bug manifests at full scale.

---

### 🧠 Mental Model / Analogy

> Progressive delivery is like a new restaurant dish being tested through a soft launch. The restaurant doesn't add it to the full menu immediately. First, they offer it to 10 tables as a "chef's surprise." If diners love it and no one gets sick, they offer it to 25% of tables next week. If those results are good, it goes on the permanent menu. If anyone gets sick during the 10-table test, they pull it from service before it reaches the full restaurant — not after 200 plates are served.

- "Chef's surprise to 10 tables" → canary deploy to 1-5% of traffic
- "Positive feedback → expand to 25% of tables" → promote to next stage
- "Sick diner during 10-table test → pull dish" → automated rollback on metric failure
- "Full permanent menu" → 100% traffic promotion
- "200 plates served before discovering issue" → all-or-nothing deployment failure

Where this analogy breaks down: a restaurant can recall physical food. Software bugs may have already corrupted data or sent incorrect transactions for the 1% of affected traffic — you can limit future exposure but not undo what happened during the canary window.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of releasing new software to all users at once, progressive delivery releases it to a small group first. The system watches whether anything goes wrong during that small release. If everything is fine, it gradually expands to more users until everyone has the new version. If something goes wrong with the small group, it rolls back automatically before everyone is affected.

**Level 2 — How to use it (junior developer):**
In Kubernetes: use Argo Rollouts with a canary strategy. Define increments (1% → 5% → 25% → 50% → 100%) and pause durations. Set up analysis runs that check error rate and latency at each stage. For simpler setups: use a feature flag service (LaunchDarkly, Unleash) and gradually increase the percentage of users getting the new feature from 1% to 100% over days, monitoring dashboards manually.

**Level 3 — How it works (mid-level engineer):**
Kubernetes-native progressive delivery with Argo Rollouts: the Rollout resource replaces Deployment and adds canary steps. Each step either sets a specific canary weight and pauses or runs analysis. Analysis: Argo Rollouts queries Prometheus metrics for the canary replica set vs stable replica set. The analysis compares error rate, P99 latency, and success rate during a defined window. If all metrics pass: advance. If any fail: rollback all traffic to stable. Flagger (CNCF) implements the same loop for Kubernetes service mesh environments (Istio, Linkerd) using automatic traffic weight adjustment.

**Level 4 — Why it was designed this way (senior/staff):**
Progressive delivery was coined by James Governor (RedMonk) in 2018 to describe the pattern that Netflix, Facebook, and Amazon were practicing informally. Netflix's "Chaos Monkey" and production experimentation culture drove the need for risk-partitioned deployments. Amazon's "two-pizza teams" principle (small service ownership) enabled independent canary rollouts per service — infeasible in a monolith. The key technical enabler is the service mesh (Istio, Linkerd) — by placing traffic management at the infrastructure level (sidecar proxy), developers can configure progressive delivery policies without modifying application code. Argo Rollouts (CNCF, 2019) made this accessible to Kubernetes-native teams without full service mesh overhead. The emerging pattern is progressive delivery integrated with feature experimentation (A/B testing): the same traffic splitting used for safety can also measure conversion rate, revenue per user, and other business metrics — collapsing "safe deployment" and "feature experiment" into a single infrastructure primitive.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  PROGRESSIVE DELIVERY ROLLOUT               │
├─────────────────────────────────────────────┤
│                                             │
│  NEW version: v2.0 (canary)                 │
│  OLD version: v1.9 (stable)                 │
│                                             │
│  STAGE 1: 1% canary                         │
│  Traffic: 1% → v2.0 | 99% → v1.9           │
│  Wait: 10 minutes                           │
│  Analysis: error_rate(v2.0) / baseline ≤ 2x│
│  PASS → advance to Stage 2                  │
│                                             │
│  STAGE 2: 10% canary                        │
│  Traffic: 10% → v2.0 | 90% → v1.9          │
│  Wait: 30 minutes                           │
│  Analysis: P99 latency, error rate          │
│  PASS → advance to Stage 3                  │
│                                             │
│  STAGE 3: 50% canary                        │
│  Traffic: 50% → v2.0 | 50% → v1.9          │
│  Wait: 60 minutes                           │
│  Analysis: all SLOs passing                 │
│  PASS → advance to 100%                     │
│                                             │
│  STAGE 4: 100% stable                       │
│  v1.9 scaled to 0 replicas                  │
│  v2.0 becomes the stable version            │
│                                             │
│  ROLLBACK (any stage):                      │
│  Analysis FAIL → traffic instantly          │
│  returned 100% to v1.9                      │
│  v2.0 scaled to 0                           │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
CI: build + test → image:sha-abc123
  → Argo Rollouts: rollout begins
  → Stage 1: 1% traffic → sha-abc123
     [← YOU ARE HERE: canary analysis running]
     Kayenta queries Prometheus:
     error_rate: 0.3% (baseline 0.5% — better!)
     P99 latency: 245ms (baseline 252ms — better!)
     ANALYSIS: PASS → promote to 10%
  → Stage 2: 10% traffic → sha-abc123
     Analysis: PASS → promote to 50%
  → Stage 3: 50% traffic → sha-abc123
     Analysis: PASS → promote to 100%
  → Stable: sha-abc123 is new stable
  → Previous version scaled to 0 replicas
```

**FAILURE PATH:**
```
Stage 2 (10% canary):
  → Analysis: error_rate 4.2% vs baseline 0.5%
  → Threshold: 2x baseline = 1.0% → EXCEEDED
  → Automated rollback: 0% → sha-abc123
  → 100% traffic → previous stable
  → Alert: canary rollback executed
  → Engineer investigates canary replica logs
  → Root cause identified → fixed → re-deploy
```

**WHAT CHANGES AT SCALE:**
At Netflix/Amazon scale, progressive delivery is per-region and per-customer-segment. "Ring deployments": employees → beta users → specific regions → all traffic. Automated analysis incorporates business metrics (conversion rate, revenue per session) alongside technical metrics. Failed canaries trigger automated incident creation and root cause correlation with the specific code changes in the failed version. The canary analysis becomes an A/B experiment framework — the same infrastructure that tests safety also measures business impact.

---

### 💻 Code Example

**Example 1 — Argo Rollouts canary strategy:**
```yaml
# rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  replicas: 10
  strategy:
    canary:
      # Analysis at each step
      analysis:
        templates:
          - templateName: error-rate-analysis
        startingStep: 1  # start analysis at step 2
      steps:
        - setWeight: 1    # 1% canary
        - pause: {duration: 10m}
        - analysis: {}   # run analysis
        - setWeight: 10
        - pause: {duration: 30m}
        - analysis: {}
        - setWeight: 50
        - pause: {duration: 60m}
        - analysis: {}
        # Full rollout if no failures
  selector:
    matchLabels:
      app: myapp
  template:
    spec:
      containers:
        - name: myapp
          image: myapp:sha-abc123
```

**Example 2 — Argo Rollouts analysis template:**
```yaml
# analysis-template.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-analysis
spec:
  metrics:
    - name: error-rate
      interval: 5m
      successCondition: result[0] < 0.05
      # Error rate < 5% for canary
      failureLimit: 3  # allow 3 consecutive failures
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{
              status=~"5..",
              version="{{ args.canary-hash }}"
            }[5m]))
            /
            sum(rate(http_requests_total{
              version="{{ args.canary-hash }}"
            }[5m]))

    - name: p99-latency
      successCondition: result[0] < 0.5
      # P99 < 500ms
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            histogram_quantile(0.99,
              rate(http_request_duration_seconds_bucket{
                version="{{ args.canary-hash }}"
              }[5m])
            )
```

**Example 3 — Feature flag-based progressive delivery:**
```typescript
// Progressive rollout via LaunchDarkly
// Week 1: 1% of users
// Week 2: 10% of users
// Week 3: 50% of users
// Week 4: 100% (feature flag removed from code)

// Application code:
const client = LaunchDarkly.init(SDK_KEY);

app.get('/recommendations', async (req, res) => {
  const user = { key: req.userId };

  // Progressive rollout via % flag
  const useNewAlgo = await client.variation(
    'new-recommendation-algo-v2',
    user,
    false  // default: false (old algo)
  );

  const recommendations = useNewAlgo
    ? await newRecommendationEngine.get(req.userId)
    : await legacyRecommendationEngine.get(req.userId);

  res.json(recommendations);
});
```

---

### ⚖️ Comparison Table

| Strategy | Traffic Split | Rollback Speed | Infra Overlap | Best For |
|---|---|---|---|---|
| **Progressive/Canary** | Gradual % | Automatic (< 1min) | Both versions run | Production risk management |
| Blue/Green | Instant switch | Manual flip (fast) | Both versions run | Zero-downtime with instant cutover |
| Feature Flags | Per user segment | Instant flag toggle | Single deployment | Product experiments, incomplete features |
| Rolling Update | Pod-by-pod | Manual rollback | Brief overlap | Simple scenarios, no traffic control |
| A/B Testing | Split by user | Experiment end | Both versions run | Business metric experimentation |

How to choose: Use **progressive/canary** when the deployment risk specifically lies in production behaviour (unknown failure modes). Use **blue/green** when you need instantaneous cutover and equally fast rollback (DNS or load balancer switch). Use **feature flags** when you want to separate deployment from release and control visibility per user. In practice: teams use feature flags for product releases and progressive delivery for infrastructure/performance changes.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Progressive delivery eliminates production incidents | It reduces blast radius, not incidents. A bug that affects 1% of users is still a production incident. Progressive delivery minimises impact duration and scope, not the occurrence of bugs. |
| Blue/green is the same as progressive delivery | Blue/green is an all-or-nothing instant switch with easy rollback. Progressive delivery is a gradual traffic shift with automated metric-gated promotion. Both are deployment patterns; progressive delivery is more conservative. |
| Progressive delivery requires a service mesh (Istio) | Service meshes (Istio, Linkerd) make traffic splitting easy, but they're not required. Kubernetes native: Argo Rollouts with multiple replica sets. Application layer: feature flags. Any mechanism that can route X% of requests to a new version enables progressive delivery. |
| You need 100% test automation before using progressive delivery | Progressive delivery compensates for incomplete test automation by using production metrics as the final gate. Teams with poor test coverage benefit MORE from progressive delivery — it catches what tests missed. |

---

### 🚨 Failure Modes & Diagnosis

**1. Canary Analysis Not Sensitive Enough**

**Symptom:** Canary progresses through all stages and reaches 100%. 20 minutes later, incidents are reported for a bug that was present in the 1% canary but not detected.

**Root Cause:** Canary analysis metrics not sensitive enough (e.g., monitoring P50 latency instead of P99, or monitoring a 10-minute window that was too short for the bug to manifest).

**Diagnostic:**
```bash
# Check what metrics canary analysis monitors
kubectl get analysistemplate error-rate-analysis -o yaml

# Review canary history for the failed rollout
kubectl argo rollouts get rollout myapp --watch
kubectl argo rollouts history myapp

# Check analysis result from the failed rollout
kubectl get analysisrun -l app=myapp \
  --sort-by=.metadata.creationTimestamp | tail -5
```

**Fix:**
- Monitor P99 latency, not P50 (bugs often show as tail latency spikes)
- Extend canary window at each stage (longer soak time catches intermittent bugs)
- Add business metrics (conversion rate, checkout success) to analysis if applicable
- Reduce success threshold for error rate (fail at 1% error, not 5%)

**Prevention:** Red team the canary analysis: "what bug would slip through?" For each production incident in the last 6 months, determine if canary analysis would have caught it. Tune accordingly.

---

**2. Two-Version Database Schema Incompatibility**

**Symptom:** Progressive delivery rollout begins. At 50% canary, users experience data inconsistencies — some see the new data format, some see the old format. Database migration failures cascade.

**Root Cause:** Code change includes a breaking database schema migration (e.g., rename column). During progressive delivery, 50% of traffic goes to new code (reads new column name) and 50% goes to old code (reads old column name). Neither can read data written by the other.

**Diagnostic:**
```bash
# Check if code includes database migrations
ls db/migrations/
git log --oneline -5 -- db/migrations/

# Check if migration is forward-compatible
# (new code must work on OLD schema during transition)
psql -c "DESCRIBE users;"
# If column renamed: old code = broken
```

**Fix:** Use the expand/contract pattern for schema migrations:
1. **Expand**: add new column (old code ignores, new code uses new)
2. **Migrate data**: populate new column while keeping old
3. **Contract**: remove old column (old code must be fully retired first)

This extends the migration across multiple deployments but makes it safe for progressive delivery.

**Prevention:** Policy: any database migration must be forward-compatible (old code version must work on new schema). Review all migrations for backward compatibility before deployment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Deployment Pipeline` — progressive delivery is a deployment strategy executed within the pipeline; understanding pipeline architecture is required
- `Feature Flags` — one of the primary mechanisms for implementing progressive delivery at the user segment level
- `Canary Analysis` — the analysis engine used for automated metric-based promotion/rollback decisions in progressive delivery

**Builds On This (learn these next):**
- `Rollback Strategy` — progressive delivery's automated rollback is a form of rollback strategy; the broader rollback patterns extend this
- `DORA Metrics` — progressive delivery directly improves both CFR (by catching bugs at 1%) and MTTR (automated rollback in < 1 minute)

**Alternatives / Comparisons:**
- `Blue/Green Deployment` — instantaneous full switch vs gradual traffic shift; blue/green prioritises instant rollback, progressive prioritises risk partitioning
- `Feature Flags` — progressive delivery via feature flags operates at application layer; Argo Rollouts operates at infrastructure/Kubernetes layer
- `Canary Analysis` — the analysis component of progressive delivery; canary analysis is a subset of the full progressive delivery framework

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Gradual production traffic exposure       │
│              │ with automated metric-gated promotion     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ All-or-nothing deployments expose 100%    │
│ SOLVES       │ of users to undetected production bugs    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Production is the most realistic test env;│
│              │ limit exposure to limit blast radius      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Services with high production risk (data, │
│              │ payments, recommendation engines)        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Purely additive changes; stateless APIs   │
│              │ where rollback is trivially safe          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Blast radius reduction vs deployment      │
│              │ duration and operational complexity       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Drug trial phases for software — test    │
│              │  safety at small scale before full dose." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary Analysis → Blue/Green →            │
│              │ Argo Rollouts → Flagger → Feature Flags   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your payment processing service handles credit card transactions. You want to deploy a new version using progressive delivery (1% → 10% → 50% → 100%). During the 10% stage, analysis reports a 0.8% error rate (baseline: 0.5%) — above threshold. Automated rollback is executed. The 0.3% error delta represents approximately 15 failed transactions in the 10-minute analysis window, and you're not certain the error is caused by the new code (coincident infrastructure issue is possible). Describe the full decision framework for: (1) whether to rollback was correct, (2) how to investigate root cause, (3) when and how to retry the deployment.

**Q2.** Progressive delivery assumes you can simultaneously run two versions of your service with different code. For stateless APIs, this is straightforward. But your service maintains user session state in memory (not in a separate database), and your new version changes the session data structure format. With 50% of requests going to the old version and 50% to the new version, a user's requests may hit alternating versions, each unable to read the other's session format. How do you redesign either the session architecture or the progressive delivery strategy to handle this state incompatibility, and what does this reveal about the prerequisites for adopting progressive delivery?

