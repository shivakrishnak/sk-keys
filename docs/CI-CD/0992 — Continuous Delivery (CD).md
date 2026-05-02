---
layout: default
title: "Continuous Delivery (CD)"
parent: "CI/CD"
nav_order: 992
permalink: /ci-cd/continuous-delivery/
number: "0992"
category: CI/CD
difficulty: ★☆☆
depends_on: Continuous Integration, Pipeline, Automated Testing
used_by: Continuous Deployment, Deployment Pipeline, Environment Promotion
related: Continuous Deployment, Continuous Integration, GitOps
tags:
  - cicd
  - devops
  - deployment
  - foundational
  - bestpractice
---

# 0992 — Continuous Delivery (CD)

⚡ TL;DR — Continuous Delivery ensures every passing CI build produces a deployable release artifact — so the team can deploy to production at any time with a single button press.

| #0992 | Category: CI/CD | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Continuous Integration, Pipeline, Automated Testing | |
| **Used by:** | Continuous Deployment, Deployment Pipeline, Environment Promotion | |
| **Related:** | Continuous Deployment, Continuous Integration, GitOps | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team practises CI — every commit is built and tested. But deploying to production is still a quarterly ritual. Two weeks before the release, a "freeze" kicks in. An ops team manually packages the software, writes a 40-step runbook, schedules a Saturday midnight maintenance window, and crosses fingers. When something goes wrong — and it does — nobody knows if it's a config issue, a code bug, or a deployment procedure error. Roll-back takes hours.

**THE BREAKING POINT:**
The software is technically tested, but the deployment process is untested, manual, and terrifying. The team ships less often than they could, features sit in the repo for weeks waiting for the next release window, and the business can't respond quickly to market changes.

**THE INVENTION MOMENT:**
This is exactly why Continuous Delivery was created: make every build a candidate for production by automating the entire path from commit to release-ready artifact, so deploying is a business decision — not a technical event.

---

### 📘 Textbook Definition

**Continuous Delivery (CD)** is a software engineering practice in which every code change that passes automated tests is automatically built into a release candidate and deployed to production-like environments. The software can be released to production at any time via a single manual trigger. CD extends CI by adding automated deployment stages beyond unit testing, ensuring the deployment process itself is always validated. It is distinct from Continuous Deployment, where releases happen automatically without manual approval.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
After CI checks the code, CD packages it and proves it can deploy — anytime.

**One analogy:**
> Think of a restaurant kitchen. CI is the chef testing each dish's flavour before it leaves the kitchen. CD is the fully plated dish waiting under the heat lamp — ready to go to the table the moment the waiter (business owner) says "send it." The dish is always ready; serving it is a choice.

**One insight:**
The critical distinction: in Continuous Delivery, a human still approves the production release. In Continuous Deployment, that last gate is automated too. CD is the practice of making deployment a boring, repeatable non-event — not the practice of deploying automatically.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every commit that passes CI must produce a deployable artifact.
2. The deployment process must be automated and version-controlled.
3. Production deployment requires only a business decision, not a technical one.

**DERIVED DESIGN:**
CD pipelines extend the CI pipeline with additional stages: package, deploy-to-staging, smoke-test, deploy-to-UAT, acceptance-test. Each stage either promotes the artifact to the next environment or stops the pipeline. The same artifact (same binary, same container image) must travel through every staged environment — never rebuild for each environment. Configuration differences between environments are injected at runtime via environment variables or config maps, not baked into the artifact.

**THE TRADE-OFFS:**
**Gain:** Deployment risk is dramatically reduced — small, frequent releases instead of big-bang quarterly ones. The business can ship features on demand. Rollback is trivial (just deploy the previous artifact).
**Cost:** Requires investment in staging environments, automated acceptance tests, and cultural change. Teams must write "production-safe" code continuously — no half-finished features in releasable builds (requires feature flags).

---

### 🧪 Thought Experiment

**SETUP:**
A team has a 500-line bug fix. Normally they deploy quarterly. With CD, they could deploy this afternoon.

**WHAT HAPPENS WITHOUT CD:**
The fix is complete and CI-green. But deployment requires: (a) manual QA sign-off scheduled for Thursday, (b) ops team to create a deployment runbook, (c) a change approval board meeting next Tuesday. The fix sits in the repo for 11 days. A customer continues hitting the bug.

**WHAT HAPPENS WITH CD:**
The fix passes CI. The CD pipeline automatically deploys to staging, runs smoke tests (2 min), runs acceptance tests (8 min). All pass. The product manager sees a green pipeline badge and clicks "Deploy to Production." Done in 12 minutes. Customer no longer hits the bug today.

**THE INSIGHT:**
CD doesn't remove human judgment from production deploys — it removes the technical fear. When deploying is a 1-minute, reversible operation, the business can make deployment decisions based purely on readiness, not on engineering effort.

---

### 🧠 Mental Model / Analogy

> Continuous Delivery is like a well-stocked vending machine for software. The products (release candidates) are always there, always fresh, always tested. The business can press the button to dispense at any moment. The difference from Continuous Deployment: a human must still press the button.

- "Products stocked in the machine" → build artifacts stored in the artifact registry
- "All products tested before stocking" → CI + automated acceptance tests passed
- "Single button press to dispense" → one-click deploy to production
- "Restocking is automatic" → every CI-passing commit triggers fresh pipeline
- "Expiry date" → artifact versioned to the commit SHA, traceable

Where this analogy breaks down: a vending machine has limited slots; CD pipelines can hold hundreds of staged release candidates simultaneously across branches.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
After developers write code and the computer confirms it works, CD automatically packs it up into a complete release and sends it through tests in systems that look just like production. At any moment, a person can press a button and that release goes live — no manual packaging, no runbooks.

**Level 2 — How to use it (junior developer):**
Your CI pipeline handles build and unit tests. CD adds stages: build a Docker image or JAR, push it to a registry with the commit SHA as the tag, deploy to a staging environment, run smoke tests and E2E tests there, deploy to UAT, wait for human approval, deploy to production. Define all stages in your pipeline YAML. The same image must be used in all stages — never rebuild.

**Level 3 — How it works (mid-level engineer):**
The artifact (Docker image, JAR, ZIP) is the unit of deployment. It's immutable once built — tagged with the Git commit SHA. Secrets and environment-specific config are injected at deploy time via environment variables or a secrets manager (Vault, AWS Secrets Manager). Each stage deploys the artifact to an isolated environment, runs a test suite, and gates the next stage. Blue/green or canary strategies are used in production to reduce deployment risk.

**Level 4 — Why it was designed this way (senior/staff):**
CD was formalised by Jez Humble and David Farley in their 2010 book. The core insight was separating "releasability" from "release decision." Traditional processes conflated the two — the business had to wait for engineering to make the software releasable before deciding to release. CD decouples them: the software is always releasable, so the business decides purely on business grounds. This shift in focus changed the entire economics of software deployment.

---

### ⚙️ How It Works (Mechanism)

A CD pipeline extends CI with additional stages anchored by the principle: **one artifact, many environments**.

```
┌─────────────────────────────────────────────┐
│        CONTINUOUS DELIVERY PIPELINE         │
├─────────────────────────────────────────────┤
│  CI Stage: Build + Unit Tests               │
│         ↓ (artifact created)                │
│  Package: Docker build → push to registry   │
│  Tag: image:sha-a3f8c21                     │
│         ↓                                   │
│  Deploy → STAGING                           │
│  Run: smoke tests (30s)                     │
│  Run: integration tests (5 min)             │
│         ↓ PASS                              │
│  Deploy → UAT / Pre-prod                    │
│  Run: acceptance tests (15 min)             │
│         ↓ PASS                              │
│  ⏸ Manual approval gate                    │
│         ↓ APPROVED                          │
│  Deploy → PRODUCTION                        │
│  Run: production smoke tests                │
│         ↓                                   │
│  Monitor: errors, latency, saturation       │
└─────────────────────────────────────────────┘
```

**The artifact journey:** The Docker image built in the CI stage is pushed to a registry with the commit SHA as its tag. Every subsequent stage pulls that exact image — the staging environment and production run identical code. There is no "rebuild for production."

**Gates:** Each stage is a gate. If smoke tests in staging fail, the pipeline stops. The artifact does not advance to UAT. This prevents a known-broken build from reaching production.

**Manual approval gate:** Between UAT and production, a human must explicitly approve. In tools like GitHub Actions this is an Environment with required reviewers. In ArgoCD it's a manual sync trigger. This gate is the dividing line between CD and Continuous Deployment.

**Rollback:** Because each production deploy references an explicit image tag (commit SHA), rollback is simply re-deploying the previous tag — a 60-second operation, not a 2-hour emergency procedure.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer merges PR → CI pipeline: build + test PASS
  → Docker image built → pushed to registry
  → Deploy to staging [← YOU ARE HERE]
  → Smoke tests pass → Integration tests pass
  → Deploy to UAT → Acceptance tests pass
  → Slack notification: "Build #342 ready for prod"
  → Product manager approves → Deploy to production
  → Production smoke tests pass
  → Feature live in 25 minutes from merge
```

**FAILURE PATH:**
```
Integration tests fail in staging
  → Pipeline halts — no UAT deployment
  → Developer notified with test output
  → Fix committed → CI reruns
  → New artifact promoted through pipeline
  → Previous artifact discarded
```

**WHAT CHANGES AT SCALE:**
At 100+ microservices, each service has its own CD pipeline. Coordinating a multi-service release requires choreography — either sequential pipelines triggered by upstream success or an orchestration layer (ArgoCD, Spinnaker) that manages cross-service deployment sequencing. Feature flags become essential to decouple code deployment from feature activation.

---

### 💻 Code Example

**Example 1 — CD pipeline extending CI (GitHub Actions):**
```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [ main ]  # only main branch triggers CD

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: myorg/myapp
          tags: type=sha  # tag with commit SHA

      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ steps.meta.outputs.tags }}

  deploy-staging:
    needs: build-and-push
    environment: staging   # uses staging secrets
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/myapp \
            app=${{ needs.build-and-push.outputs.image-tag }}
      - name: Smoke test
        run: ./scripts/smoke-test.sh staging

  deploy-production:
    needs: deploy-staging
    environment:
      name: production
      url: https://myapp.example.com
    # environment 'production' has required reviewers configured
    # → manual approval gate
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/myapp \
            app=${{ needs.build-and-push.outputs.image-tag }}
```

**Example 2 — BAD vs GOOD: rebuilding per environment:**
```bash
# BAD: rebuild image for each environment
# Risk: compiled-in differences, untested code paths
docker build -t myapp:staging .   # staging build
# ... test staging ...
docker build -t myapp:prod .      # completely different build!

# GOOD: one image, promoted across environments
# Build once, tag once, promote everywhere
docker build -t myapp:sha-a3f8c21 .
# deploy to staging using sha-a3f8c21
# after UAT pass, deploy SAME sha-a3f8c21 to production
```

---

### ⚖️ Comparison Table

| Practice | Human Gate to Prod | Deployment Frequency | Risk Level | Best For |
|---|---|---|---|---|
| **Continuous Delivery** | Yes (manual approval) | On demand (hours to days) | Low | Teams needing business sign-off |
| Continuous Deployment | No (fully automatic) | Every passing commit | Very Low | High-trust, high-coverage teams |
| Traditional Release | Yes (heavy process) | Quarterly/monthly | High | Regulated industries with audit trails |
| GitOps | Declarative (PR approval) | On PR merge | Low | Kubernetes-native teams |

How to choose: Start with Continuous Delivery — add the manual gate. Evolve to Continuous Deployment only when your test coverage is high enough that the team trusts automated tests to gatekeep production. Regulated industries (finance, healthcare) may require Continuous Delivery even with mature teams.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Continuous Delivery = Continuous Deployment | CD means the software **can** be deployed anytime; Continuous Deployment means it **is** deployed automatically. They differ on the final gate |
| CD removes the need for change management | CD complements change management — it makes deployments safer and faster, but regulated environments still require approval workflows (built into the pipeline) |
| CD requires deploying every commit to production | CD requires every commit to be *deployable* — not that it must be deployed. The business decides when to deploy |
| CD only applies to web applications | CD applies to any software: mobile apps (via TestFlight/Play Store), libraries (via artifact registries), firmware, and infrastructure code |

---

### 🚨 Failure Modes & Diagnosis

**1. Different Code Runs in Staging vs Production**

**Symptom:** Tests pass in staging, production breaks. "But it worked in staging!"

**Root Cause:** Team rebuilds the Docker image for production instead of promoting the same image from staging. Environment-specific behavior is compiled in.

**Diagnostic:**
```bash
# Compare image digests between staging and production
kubectl get deployment myapp -n staging \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get deployment myapp -n production \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
# If digests differ — you have different builds in staging vs prod
```

**Fix:** Enforce image immutability. Tag with commit SHA. Use `imagePullPolicy: Always` to guarantee the exact tagged image is used.

**Prevention:** Make the pipeline fail if the image tag in production does not match the image tag that passed staging tests.

---

**2. Manual Approval Gate Becomes a Bottleneck**

**Symptom:** Pipeline is green, but production deploys queue for days waiting for approver availability. CD becomes "Continuous Delay."

**Root Cause:** Approval process is not streamlined. Approvers are not notified promptly. No SLA on approval.

**Diagnostic:**
```bash
# GitHub Actions: check time between "waiting for approval"
# and "approved" in the environments section
gh run list --workflow=cd.yml --json conclusion,createdAt \
  | jq '.[] | {conclusion, createdAt}'
```

**Fix:** Define an on-call rotation for CD approvals. Use Slack bots to notify approvers with one-click approve links. Set a 4-hour SLA for approval.

**Prevention:** Design approval workflows to match deployment frequency goals. If deploying 10x/day, the approval process must scale accordingly — consider automating approval for non-critical services.

---

**3. Acceptance Tests Too Slow, Teams Bypass CD**

**Symptom:** Developers push directly to production bypassing the pipeline because "tests take 2 hours."

**Root Cause:** Acceptance test suite was never optimised. All tests run sequentially. No parallelism.

**Diagnostic:**
```bash
# Time the acceptance test stage
time ./run-acceptance-tests.sh
# Identify which tests are slowest:
# JUnit: check surefire reports for test duration
grep -r "time=" target/surefire-reports/ \
  | sort -t= -k2 -rn | head -20
```

**Fix:** Parallelise acceptance tests. Split the suite — fast contract tests first, slow UI tests last (non-blocking for merge).

**Prevention:** Set a pipeline time budget. Any stage exceeding the budget triggers an automatic alert to the team.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — CD extends CI; you need CI working before adding deployment automation
- `Pipeline` — CD is implemented as a multi-stage pipeline with gates between stages
- `Artifact Registry` — CD promotes immutable artifacts through environments, requiring a registry to store them

**Builds On This (learn these next):**
- `Continuous Deployment` — removes the manual gate, making every passing build automatically deploy to production
- `Environment Promotion` — the pattern of advancing an artifact through dev → staging → UAT → production
- `GitOps` — a CD implementation where the desired deployment state is declared in Git

**Alternatives / Comparisons:**
- `Continuous Deployment` — fully automated final step vs CD's manual gate
- `Traditional Release Management` — heavyweight, infrequent vs CD's lightweight, frequent deployments

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Every CI-passing build becomes a          │
│              │ one-click-deployable release candidate    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Manual, risky deployments that block      │
│ SOLVES       │ the business from shipping on demand      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ CD ≠ Continuous Deployment. There is      │
│              │ always a human gate before prod           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Team wants to ship on demand but needs    │
│              │ business/compliance sign-off              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Test coverage is too low to trust         │
│              │ automated pipelines as safety nets        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Deployment confidence vs staging          │
│              │ environment and test infrastructure cost  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Deployment becomes a business decision,  │
│              │  not an engineering event"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Continuous Deployment → GitOps → ArgoCD   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A fintech company must comply with SOX audit requirements — every production change needs a separate approver and an audit trail. How would you design a CD pipeline that satisfies both "deploy on demand" business needs and SOX compliance? What specific pipeline components map to each compliance requirement?

**Q2.** Your CD pipeline deploys a monolithic Java application to 3 environments (staging → UAT → production). The team now wants to split the monolith into 12 microservices over 6 months. Trace exactly how the CD pipeline must evolve: which stages remain shared, which become per-service, and what new coordination problem appears when Service A's deployment depends on Service B's updated API being live in production first.

