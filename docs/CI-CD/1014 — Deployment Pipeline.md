---
layout: default
title: "Deployment Pipeline"
parent: "CI/CD"
nav_order: 1014
permalink: /ci-cd/deployment-pipeline/
number: "1014"
category: CI/CD
difficulty: ★★☆
depends_on: CI/CD Pipeline, Continuous Delivery, Artifact, Build Stage
used_by: Environment Promotion, GitOps, Progressive Delivery, Rollback Strategy
related: Pipeline, Continuous Deployment, Environment Promotion, GitOps
tags:
  - cicd
  - devops
  - intermediate
  - deployment
---

# 1014 — Deployment Pipeline

⚡ TL;DR — A deployment pipeline is the automated sequence of stages that safely moves a validated build artefact from version control through every environment until it reaches production.

| #1014 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Continuous Delivery, Artifact, Build Stage | |
| **Used by:** | Environment Promotion, GitOps, Progressive Delivery, Rollback Strategy | |
| **Related:** | Pipeline, Continuous Deployment, Environment Promotion, GitOps | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team of eight engineers deploys their application manually. Each deployment means an engineer SSHes into five servers, runs a unique update script for each, verifies the application started, manually runs a smoke test, and updates the deployment log in a spreadsheet. Deployments take 90 minutes. They happen once a month because they're so painful. Two engineers know the exact steps — if they're sick, the team can't deploy. One forgotten step on server 3 of 5 means server 3 runs an old version for weeks before anyone notices. The release cycle is the bottleneck for the entire business.

**THE BREAKING POINT:**
Manual deployment processes don't scale. As teams grow, as services multiply, as deployment frequency expectations increase from monthly to weekly to daily, the manual approach collapses under its own complexity. Humans executing 47-step deployment runbooks is a recipe for drift, inconsistency, and outages from missed steps.

**THE INVENTION MOMENT:**
This is exactly why the deployment pipeline was created: encode the entire path from a validated build artefact to a running production service as a repeatable, automated, auditable sequence — making deployment a click (or a push) rather than a ceremony.

---

### 📘 Textbook Definition

A **deployment pipeline** is an automated sequence of stages that takes a built and tested software artefact and systematically deploys it through pre-production environments (development, staging, pre-production) before releasing to production. Unlike a CI pipeline (which builds and tests code), the deployment pipeline operates on immutable artefacts that have already passed CI gates. It implements environment-specific configuration injection, smoke testing, integration testing, approval gates, and rollback mechanisms. The deployment pipeline embodies the Continuous Delivery principle: the artefact produced by CI is deployable to production at any time, and the pipeline is the mechanism that actually performs that deployment safely. Tools include Jenkins Pipelines, GitHub Actions workflows, GitLab CI/CD, Spinnaker, and ArgoCD.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The automated conveyor belt that takes a tested build and safely moves it to production.

**One analogy:**
> A deployment pipeline is like an assembly line quality checkpoint system. A car leaves the assembly line and passes through inspection stations: first mechanical check, then electrical, then safety test, then road test, then final approval. Each checkpoint can halt the line if something's wrong. The final checkpoint is approval to ship. A deployment pipeline does the same: each environment is a checkpoint, and each stage verifies the artefact is safe to move forward.

**One insight:**
The key insight separating someone who knows the term from someone who understands it: CI and the deployment pipeline operate on different objects. CI operates on source code (build and test). The deployment pipeline operates on artefacts (deploy and verify). Once CI produces a validated artefact, the deployment pipeline should never rebuild from source — it promotes the same binary through environments, ensuring what was tested is exactly what's deployed to production.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The same artefact (image/binary) must travel through every environment — rebuilding from source at each stage breaks the "what we tested is what we deployed" guarantee.
2. Each environment exists to answer a specific question: dev = "does it run?", staging = "does it work with real data?", production = "is it serving real users safely?"
3. Any stage failure must propagate immediately — a broken staging deployment must block production deployment automatically, not via manual coordination.

**DERIVED DESIGN:**
The deployment pipeline separates concerns:
- **CI pipeline**: source code → artefact (build + test)
- **Deployment pipeline**: artefact → deployed service (promote through environments)

Environments receive configuration differently — a Docker image is identical in staging and production; the difference is environment variables (DB connection strings, feature flags, resource limits) injected at deploy time, not baked into the image.

Approval gates exist at promotion boundaries that carry risk: automated tests can validate pre-production, but the final production promotion may require a human sign-off (especially for regulated industries or large-scale changes).

**THE TRADE-OFFS:**
**Gain:** Consistent, repeatable, auditable deployments; faster deployment frequency; reduced human error; rollback capability.
**Cost:** Pipeline setup and maintenance overhead; potential bottleneck if pipeline stages are slow; false sense of security if tests are inadequate.

---

### 🧪 Thought Experiment

**SETUP:**
A payment service team deploys to production. They have 3 environments: dev, staging, production. Consider two scenarios: manual deployment vs an automated deployment pipeline.

**WHAT HAPPENS WITHOUT A DEPLOYMENT PIPELINE:**
Engineer deploys v2.1.0 to dev (works). Manually updates staging config (slightly different ENV var by typo). Staging tests pass because the typo doesn't affect tests. Engineer manually deploys to production — same typo, now propagated. Production payment processing silently fails for 3% of requests due to the wrong API endpoint. Alert fires 2 hours later. Rollback requires running 6 manual script steps from memory at 2am.

**WHAT HAPPENS WITH A DEPLOYMENT PIPELINE:**
v2.1.0 artefact tagged by CI. Deployment pipeline triggers. Dev deploy: automated smoke tests pass. Staging promotion: same artefact + environment-specific config from config store (no manual config editing). Integration tests run. Production promotion gate: requires approval + passes automated canary tests. Same artefact lands in production with correct config. Rollback is a single button press that replays the previous artefact in the pipeline.

**THE INSIGHT:**
The deployment pipeline eliminates the class of errors caused by manual steps, environment-specific script variations, and human memory under pressure. Automation doesn't eliminate bugs — but it eliminates the meta-bugs introduced by the deployment process itself.

---

### 🧠 Mental Model / Analogy

> A deployment pipeline is like a pharmaceutical drug approval process. A drug candidate is produced in the lab (CI: build the artefact). Then it moves through preclinical trials, Phase I, Phase II, Phase III, and FDA review before reaching patients (deployment pipeline: dev → staging → pre-prod → production). Each phase is mandatory, runs in sequence, and any failure stops progression. The same compound goes through every phase — you don't make a new batch for each stage.

- "Drug compound" → immutable build artefact (Docker image + SHA)
- "Trial phases" → environment stages (dev, staging, pre-prod, prod)
- "Phase failure" → integration test failures, smoke test failures
- "FDA review" → manual approval gate before production
- "Reaching patients" → production deployment serving real users

Where this analogy breaks down: drug trials happen once per drug. Software deployment pipelines run dozens of times per day. Speed is essential — stages that take hours are a problem, unlike pharmaceutical phases that take years by design.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A deployment pipeline is the automatic series of steps that takes a tested version of an app and moves it through test environments all the way to production, checking that everything works at each step before going further.

**Level 2 — How to use it (junior developer):**
In GitHub Actions, a deployment pipeline is a workflow triggered on `workflow_dispatch` or after a CI workflow succeeds. Use environment protection rules (Settings → Environments) to require manual approvals before production deployment. Store environment-specific config in GitHub Secrets or an external config store — never bake config into the artefact. Use `needs:` to chain stages and ensure each stage completes before the next begins.

**Level 3 — How it works (mid-level engineer):**
A production-grade deployment pipeline separates "deploy" from "verily." Each environment stage: (1) deploy the artefact (Helm upgrade / kubectl apply / Terraform apply); (2) run environment-specific health probes (readiness endpoints, smoke tests); (3) run integration tests against the newly deployed environment; (4) check deployment success metrics (error rate, latency) if post-deploy monitoring is integrated. Promotion gates can be automated (pass all tests → auto-promote to next stage) or manual (human signs off). Rollback is implemented as re-running the pipeline with the previous artefact tag — not as a separate emergency procedure.

**Level 4 — Why it was designed this way (senior/staff):**
The deployment pipeline pattern emerged from Jez Humble and David Farley's "Continuous Delivery" (2010) as a formalisation of what high-performing teams were doing informally. The critical design decision — operate on artefacts, not source — came from the observation that rebuilding from source at each stage breaks environment parity and creates subtle "it worked in staging" bugs from compiler/dependency version drift. The modern evolution is GitOps: rather than the pipeline pushing deployments to environments, the pipeline updates a Git repository of deployment state (Helm values, Kustomize overlays), and an agent (ArgoCD, Flux) in each cluster pulls the desired state. This inverts the trust model — the cluster pulls from source of truth rather than accepting pushes from a CI server — improving auditability and disaster recovery.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  DEPLOYMENT PIPELINE — STAGE SEQUENCE       │
├─────────────────────────────────────────────┤
│                                             │
│  TRIGGER: CI completes → artefact ready     │
│  myapp:sha-abc123 pushed to registry        │
│                                             │
│  STAGE 1: Deploy to DEV                     │
│  → helm upgrade myapp ./chart               │
│     --set image.tag=sha-abc123              │
│  → Smoke test: GET /health → 200 OK         │
│  → Pass → auto-promote to STAGING           │
│                                             │
│  STAGE 2: Deploy to STAGING                 │
│  → Same artefact + staging config           │
│  → Integration tests run (50 test cases)   │
│  → Performance baseline check              │
│  → Pass → gate: MANUAL APPROVAL            │
│                                             │
│  APPROVAL GATE:                             │
│  → Release engineer reviews metrics        │
│  → Approves: Promote to PRODUCTION          │
│                                             │
│  STAGE 3: Deploy to PRODUCTION              │
│  → Canary: 10% traffic → new version       │
│  → Monitor error rate + latency (15 min)   │
│  → Metrics OK → full rollout 100%          │
│  → Smoke test: critical paths              │
│  → DONE: deployment record logged          │
│                                             │
│  FAILURE AT ANY STAGE:                      │
│  → Halt pipeline                           │
│  → Alert: Slack / PagerDuty                │
│  → Auto-rollback if production affected    │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer merges PR → main branch
  → CI pipeline: build + test → myapp:sha-abc123
  → Image pushed to registry
  → Deployment pipeline triggered [← YOU ARE HERE]
     → Dev: deploy → smoke test → pass
     → Staging: deploy → integration tests → pass
     → Approval gate: release engineer approves
     → Production: canary → metrics OK → full rollout
  → Version deployed and monitoring
```

**FAILURE PATH:**
```
Integration tests fail in staging
  → Pipeline halted at staging stage
  → Slack alert: "Deploy sha-abc123 blocked in staging"
  → Production unaffected (still running previous version)
  → Developer investigates staging logs
  → Fixes bug → new commit → CI → new artefact
  → New pipeline run picks up from dev
```

**WHAT CHANGES AT SCALE:**
At 50+ services each with their own deployment pipeline, pipeline management becomes a platform concern. Teams adopt a "golden path" — a standardised pipeline template deployed as a reusable composite GitHub Action or Tekton Pipeline. Individual teams customise parameters (test commands, environment names) without implementing pipeline logic themselves. Deployment frequency metrics (DORA metrics) are tracked centrally across all pipelines to identify bottlenecks. Long-running integration test suites become the primary bottleneck — teams invest in parallelisation and test suite optimisation to keep pipeline duration under 15 minutes.

---

### 💻 Code Example

**Example 1 — GitHub Actions multi-environment deployment pipeline:**
```yaml
# .github/workflows/deploy.yml
name: Deploy Pipeline
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

jobs:
  deploy-dev:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to dev
        run: |
          helm upgrade --install myapp ./helm/myapp \
            --namespace dev \
            --set image.tag=${{ github.sha }}
      - name: Smoke test
        run: |
          sleep 10
          curl -f https://dev.myapp.com/health

  deploy-staging:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: |
          helm upgrade --install myapp ./helm/myapp \
            --namespace staging \
            --set image.tag=${{ github.sha }}
      - name: Integration tests
        run: npm run test:integration

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    # environment with required reviewers = manual gate
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: |
          helm upgrade --install myapp ./helm/myapp \
            --namespace production \
            --set image.tag=${{ github.sha }}
      - name: Post-deploy smoke test
        run: curl -f https://myapp.com/health
```

**Example 2 — Rollback on failure:**
```yaml
  deploy-production:
    # ...
    steps:
      - name: Deploy
        id: deploy
        run: helm upgrade myapp ./helm --set image.tag=$TAG

      - name: Post-deploy verification
        id: verify
        run: |
          sleep 30
          ERROR_RATE=$(curl -s https://metrics/error-rate)
          if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
            echo "Error rate too high: $ERROR_RATE"
            exit 1
          fi

      - name: Rollback on failure
        if: failure() && steps.deploy.conclusion == 'success'
        run: |
          helm rollback myapp 0
          # 0 = roll back to previous release
          echo "Rolled back to previous version"
```

---

### ⚖️ Comparison Table

| Tool | Pipeline Type | GitOps | Approval Gates | Best For |
|---|---|---|---|---|
| **GitHub Actions** | Push-based | No (native) | Yes (environments) | GitHub repos, quick setup |
| GitLab CI/CD | Push-based | No (native) | Yes (manual jobs) | GitLab repos, built-in |
| ArgoCD | Pull-based (GitOps) | Yes | Yes | Kubernetes, GitOps model |
| Spinnaker | Push-based | No | Yes (complex) | Multi-cloud, enterprise |
| Tekton | Push-based | No | Limited | Kubernetes-native, flexible |
| Jenkins | Push-based | No | Yes | Legacy, self-hosted |

How to choose: Use **GitHub Actions** for teams on GitHub needing simplicity and fast setup. Use **ArgoCD** when adopting GitOps with Kubernetes — it's the de-facto GitOps CD tool. Use **Spinnaker** only for complex multi-cloud enterprise deployments requiring sophisticated canary analysis and pipeline management.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The CI pipeline and deployment pipeline are the same | CI produces artefacts from source. The deployment pipeline promotes artefacts through environments. They can be part of the same CI/CD tool but serve different purposes and operate on different inputs. |
| Deployment pipelines are only for large teams | Even a solo developer benefits from an automated deployment pipeline — it eliminates the "works on my machine" class of deployment failures and enables fearless frequent releases. |
| Manual approval gates are always needed before production | For low-risk changes (dependency patches, minor features with feature flags), automatic production promotion with post-deploy monitoring is safer than a human approval bottleneck that delays security patches by days. |
| A failed deployment means the pipeline is broken | A failed deployment is the pipeline working correctly — catching an issue before production is the pipeline's success, not a failure. The metric to watch is "time to detect" (deploy → failure detected), not "zero pipeline failures." |

---

### 🚨 Failure Modes & Diagnosis

**1. Configuration Drift Between Environments**

**Symptom:** Staging passes; production fails immediately after deploy. Investigation reveals a Kubernetes resource limit in production (256Mi) not set in staging (1Gi). OOMKilled.

**Root Cause:** Environment-specific configuration managed manually in each environment with no single source of truth. Staging and production drift over time.

**Diagnostic:**
```bash
# Compare Helm values across environments
helm get values myapp -n staging > staging-values.yaml
helm get values myapp -n production > prod-values.yaml
diff staging-values.yaml prod-values.yaml

# Compare actual running pod specs
kubectl get pod myapp-xxx -n staging -o json | \
  jq '.spec.containers[].resources'
kubectl get pod myapp-xxx -n production -o json | \
  jq '.spec.containers[].resources'
```

**Fix:** Store all environment configurations in Git (Helm values files, Kustomize overlays, Terraform vars). Each environment has its own values file: `values-staging.yaml`, `values-prod.yaml`. The pipeline injects the correct values file at deploy time — no manual config editing.

**Prevention:** Never manually edit environment configurations on running clusters. All config changes must go through the deployment pipeline via Git. Use Kustomize or Helm overlays to express environment differences as code diffs.

---

**2. Long-Running Pipelines Block Deployments**

**Symptom:** Deployment pipeline takes 75 minutes from trigger to production. Teams wait over an hour for hotfixes to reach production. Developer velocity suffers.

**Root Cause:** Integration tests run sequentially (50 tests × 1.5 minutes each = 75 minutes). No parallelisation. All tests run even for trivial changes.

**Diagnostic:**
```bash
# Profile CI step durations
# In GitHub Actions: click each step to see duration
# API query:
gh api /repos/{owner}/{repo}/actions/runs/{run_id}/jobs \
  --jq '.jobs[] | {name, duration: .completed_at}'

# Find the slowest test suites:
# Review test runner output for suite timings
```

**Fix:**
```yaml
  integration-tests:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]  # run 4 shards in parallel
    steps:
      - run: |
          npm run test:integration \
            --shard=${{ matrix.shard }}/4
```

**Prevention:** Set pipeline duration SLA (e.g., < 15 minutes to staging, < 30 minutes total). Run test suite profiling monthly. Invest in test parallelisation for suites above the SLA threshold.

---

**3. Artefact Tag Ambiguity — Wrong Version Deployed**

**Symptom:** Post-deploy verification shows the new feature is not live. Investigation reveals the `latest` tag was used — and pointed to a 3-hour-old image because a parallel branch also pushed to `latest`.

**Root Cause:** Using mutable image tags (`latest`, `main`, `v1.0`) in deployment pipelines. Mutable tags change over time — what `latest` points to can change between pipeline stages.

**Diagnostic:**
```bash
# Check what digest 'latest' currently resolves to
docker manifest inspect myregistry/myapp:latest | \
  jq '.config.digest'

# Check what digest the pipeline actually deployed
kubectl get pod -n production -l app=myapp \
  -o jsonpath='{.items[0].spec.containers[0].image}'
# Should show: myregistry/myapp@sha256:...
# If shows: myregistry/myapp:latest → ambiguous
```

**Fix:**
```yaml
# BAD: mutable tag
--set image.tag=latest

# GOOD: immutable tag (git SHA)
--set image.tag=${{ github.sha }}

# BEST: image digest (most immutable)
--set image.digest=sha256:abc123...
```

**Prevention:** Never use mutable image tags in deployment pipelines. Tag images with the git commit SHA. Optionally also tag semantic versions (v1.2.3), but deploy using the SHA tag, not the version.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `CI/CD Pipeline` — the deployment pipeline extends the CI pipeline; understanding CI pipeline structure is required
- `Artifact` — the deployment pipeline operates on artefacts; understanding what an artefact is and how it's stored is foundational
- `Continuous Delivery` — the deployment pipeline is the technical implementation of Continuous Delivery principles

**Builds On This (learn these next):**
- `Environment Promotion` — the specific mechanics of how an artefact moves between environments within the deployment pipeline
- `GitOps` — an alternative deployment pipeline model where the pipeline pushes to a Git state store instead of directly to targets
- `Progressive Delivery` — advanced deployment techniques (canary, blue/green) that run within the production stage of the deployment pipeline
- `Rollback Strategy` — the mechanism for safely reversing a deployment that the pipeline also automates

**Alternatives / Comparisons:**
- `GitOps` — pull-based CD where clusters sync from Git state vs push-based deployment pipelines
- `Continuous Deployment` — fully automated end-to-end (no manual gates); in contrast, many deployment pipelines include manual approval before production

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Automated stage sequence promoting a      │
│              │ build artefact through environments       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Manual deployments: inconsistent, slow,   │
│ SOLVES       │ error-prone and knowledge-bottlenecked    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The pipeline operates on artefacts —      │
│              │ never rebuild from source between stages  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any software deployed to more than one    │
│              │ environment (everyone, always)            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ No skip — but remove unnecessary stages   │
│              │ and gates that slow critical hotfixes     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Consistency + speed vs setup overhead     │
│              │ and pipeline maintenance burden           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The assembly line that tests and approves│
│              │  before the product reaches the customer."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Environment Promotion → GitOps →          │
│              │ Progressive Delivery → DORA Metrics       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your deployment pipeline currently runs: dev → staging → production, with a mandatory manual approval before production. Total pipeline time is 45 minutes. A critical security patch needs to reach production in under 30 minutes. Design an "emergency fast-track" pipeline path: what stages can be safely skipped or parallelised, what controls must remain even under urgency, and how do you prevent the emergency path from becoming the default path out of laziness?

**Q2.** Your staging environment is routinely 3–4 weeks behind production in terms of data — it has a subset of production schemas and test data. Integration tests pass in staging but three different bugs have been detected in production (not in staging) over the past quarter. What does this tell you about the quality of your staging environment as a proxy for production, and how would you redesign the pipeline gate strategy to catch these bugs without requiring full production data in staging?

