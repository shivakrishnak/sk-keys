---
layout: default
title: "Pipeline"
parent: "CI/CD"
nav_order: 994
permalink: /ci-cd/pipeline/
number: "0994"
category: CI/CD
difficulty: ★☆☆
depends_on: Continuous Integration, Version Control, Automated Testing
used_by: Continuous Delivery, Continuous Deployment, Build Stage, Test Stage
related: Build Stage, Test Stage, Deployment Pipeline
tags:
  - cicd
  - devops
  - build
  - foundational
  - pattern
---

# 0994 — Pipeline

⚡ TL;DR — A CI/CD pipeline is an automated sequence of stages that transforms every code commit into a verified, deployable release — catching failures at the earliest possible stage.

| #0994 | Category: CI/CD | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Continuous Integration, Version Control, Automated Testing | |
| **Used by:** | Continuous Delivery, Continuous Deployment, Build Stage, Test Stage | |
| **Related:** | Build Stage, Test Stage, Deployment Pipeline | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team merges code and manually: runs tests locally, builds a JAR, SFTPs it to a staging server, SSHs in to restart the service, then emails the QA team to start testing. Each person does this slightly differently. Sometimes tests are skipped to save time. Sometimes the wrong version gets deployed to staging. The developer forgets to update the changelog. Four hours later, staging has unknown code from an unclear commit.

**THE BREAKING POINT:**
Manual steps are inconsistent, skippable, and invisible. There's no audit trail. Mistakes compound. The process doesn't scale — adding the 5th developer means 5 slightly different mental models of how to deploy.

**THE INVENTION MOMENT:**
This is exactly why the CI/CD Pipeline was created: encode the entire software delivery process as a sequence of automated, version-controlled, reproducible stages — one definition, executed identically every time.

---

### 📘 Textbook Definition

A **CI/CD pipeline** is a sequence of automated stages that code must pass through from commit to deployment. Each stage has a defined trigger, a set of actions (build, test, scan, deploy), and a pass/fail gate. Stages execute sequentially or in parallel; a failing stage stops the pipeline and prevents downstream stages from running. The pipeline definition is stored as code (YAML or similar) alongside the application source, making it version-controlled and auditable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A pipeline is a series of checkpoints that code must pass before it can be deployed.

**One analogy:**
> Think of airport security: separate queues for ID check, X-ray, and boarding pass scan. Each checkpoint either lets you through or stops you there. If you fail the X-ray, you don't reach the gate. The pipeline is the same — each stage either passes your code forward or stops it.

**One insight:**
The pipeline's most important rule: **fail fast, fail early**. The cheapest place to catch a bug is in the first stage (unit tests, 30 seconds). The most expensive place is production (hours of incident response). A well-designed pipeline orders stages by cost and speed — cheapest/fastest first.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Stages execute in a defined order with gates between them.
2. A failing gate stops the pipeline — downstream stages are skipped.
3. The same pipeline definition runs for every commit — no manual variation.

**DERIVED DESIGN:**
These invariants force a structure: stages must be independent (each stage starts from a clean state), deterministic (same input always produces same output), and observable (pass/fail must be clearly visible). The pipeline is defined as code because it is the specification of the delivery process — changes to it are as significant as code changes.

Parallel stages accelerate the pipeline: linting, security scanning, and unit tests can often run simultaneously, then wait for all to complete before proceeding to the next sequential stage.

**THE TRADE-OFFS:**
**Gain:** Every delivery step is automated, auditable, and consistent. Failures surface early when they're cheapest to fix.
**Cost:** Upfront investment to define and maintain the pipeline. Tests must be automated for the pipeline to be meaningful. A slow pipeline becomes a bottleneck in itself.

---

### 🧪 Thought Experiment

**SETUP:**
A team of 6 developers merges 15 changes per day. Without a pipeline, each developer manually runs tests and deploys.

**WHAT HAPPENS WITHOUT A PIPELINE:**
Developer A forgets to run tests before pushing. Developer B assumes A tested. Code reaches staging with a broken endpoint. QA finds it 3 hours later. No one knows which of the 15 commits caused it. The integration branch is now suspect for the entire afternoon.

**WHAT HAPPENS WITH A PIPELINE:**
Developer A pushes. The pipeline runs unit tests automatically. The specific commit fails at Stage 2 — test. Pipeline blocks: staging deployment does not happen. Developer A sees the failure notification in Slack within 4 minutes. No other developer is affected. The broken endpoint never reaches staging.

**THE INSIGHT:**
The pipeline doesn't write better code — it makes the code's quality immediately visible to the whole team, and stops broken code from advancing to the next environment before it can contaminate it.

---

### 🧠 Mental Model / Analogy

> A CI/CD pipeline is like a car assembly line with quality inspections at each station. At Station 1, the frame is measured. If it's out of spec, the car stops there — no engine is installed in a bad frame. Each subsequent station adds value and verifies the previous station's work.

- "Assembly line station" → pipeline stage (build, test, deploy)
- "Quality inspection" → automated gate (pass/fail)
- "Out-of-spec frame stops the line" → failing stage halts the pipeline
- "Each station assumes previous passed" → stages depend on upstream success
- "Every car goes through same stations" → every commit uses the same pipeline definition

Where this analogy breaks down: an assembly line makes identical products; each code commit is unique — the quality checks must be general-purpose tests, not fixed measurements.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you save your code, a computer automatically runs it through a series of checks — does it build? do the tests pass? does it deploy to the test environment? If any check fails, the code is stopped there. If all checks pass, the code moves toward production.

**Level 2 — How to use it (junior developer):**
Define your pipeline in a YAML file committed to your repo (`.github/workflows/ci.yml`, `.gitlab-ci.yml`, `Jenkinsfile`). Each stage lists the commands to run. Stages run top-to-bottom by default; you can specify `needs:` (GitHub Actions) or `needs` (GitLab) to define dependencies. If any step exits non-zero, the stage fails and downstream stages are skipped.

**Level 3 — How it works (mid-level engineer):**
The pipeline runner (GitHub Actions, GitLab Runner, Jenkins agent) picks up the job from a queue, provisions a clean environment (Docker container or VM), clones the repo at the commit SHA, executes stages in order, and reports results back via the API. Artifacts (compiled JARs, Docker images) are passed between stages via artifact stores or container registries. Caching is keyed on stable inputs (lock files) to speed up repeated runs.

**Level 4 — Why it was designed this way (senior/staff):**
Pipeline-as-Code (storing the pipeline definition in the repo) was a major advancement over UI-configured pipelines (early Jenkins). It solved: version history (who changed the pipeline and why?), PR review for pipeline changes (the delivery process is as important as the code), and multi-branch pipelines (each branch can have its own pipeline variant). The `Jenkinsfile` in 2014 pioneered this; GitHub Actions and GitLab CI normalised it. The key design tension: generic pipelines (reusable across services) vs specific pipelines (optimised per service).

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│          CI/CD PIPELINE STAGES              │
├─────────────────────────────────────────────┤
│  TRIGGER: code pushed to branch             │
│         ↓                                   │
│  STAGE 1: Build                             │
│   - Compile / assemble                      │
│   - Lint / format check                     │
│   Output: JAR / Docker image                │
│         ↓ PASS                              │
│  STAGE 2: Unit Tests                        │
│   - Fast, isolated, no I/O                  │
│   - Target: < 5 minutes                     │
│         ↓ PASS                              │
│  STAGE 3: Static Analysis                   │
│   - SAST, dependency vulnerabilities        │
│   - Code coverage threshold                 │
│         ↓ PASS                              │
│  STAGE 4: Integration Tests                 │
│   - Containerised dependencies              │
│   - API contract tests                      │
│         ↓ PASS                              │
│  STAGE 5: Deploy → Staging                  │
│  STAGE 6: Acceptance Tests                  │
│         ↓ PASS                              │
│  STAGE 7: Deploy → Production               │
│         (manual approval or automatic)      │
└─────────────────────────────────────────────┘
```

**Stage isolation:** Each stage runs in a fresh container. This prevents state leakage between stages — a test that passes because of a previous stage's side effect is a false positive. Configuration is injected via environment variables, not files left behind by prior stages.

**Artifact passing:** The compiled JAR built in Stage 1 is uploaded to an artifact store or cached in the pipeline. Stage 4 downloads it — no recompilation. This ensures the same binary is tested in all stages.

**Fast-first ordering:** Unit tests (seconds) run before integration tests (minutes) which run before E2E tests (tens of minutes). This means the 90% of failures that are unit test failures are caught in 5 minutes, not after waiting 45 minutes for E2E tests to confirm the same thing.

**Parallelism:** Lint, security scan, and unit tests can run in parallel if they don't depend on each other. This shrinks wall-clock time without reducing coverage.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer pushes commit to feature branch
  → GitHub webhook fires
  → GitHub Actions runner picks up job
  → Stage 1: build succeeds → artifact cached
  → Stage 2: 247 unit tests pass (3m 12s)
  → Stage 3: no security vulnerabilities
  → Stage 4: integration tests pass (7m 04s)
  → Stage 5: deploy to staging [← YOU ARE HERE]
  → Stage 6: acceptance tests pass (11m 30s)
  → PR: all checks green ✓
  → Merge approved → production deploy
```

**FAILURE PATH:**
```
Stage 2: 3 unit tests fail
  → Pipeline halts immediately
  → Stages 3–7 do NOT run
  → PR shows ✗ — merge blocked
  → Slack: "@alice: CI failed on PR #847 — 3 unit tests"
  → Developer fixes → pushes again → pipeline reruns
```

**WHAT CHANGES AT SCALE:**
At 100+ services, each with its own pipeline, the total pipeline infrastructure becomes a platform. A Platform Engineering team owns the pipeline templates and shared infrastructure. Individual teams customise stages via parameters, not by forking pipeline files. Build cache hit rates become a critical metric — a 20% cache miss rate can add 20 minutes to the entire system's total build time.

---

### 💻 Code Example

**Example 1 — Basic multi-stage GitHub Actions pipeline:**
```yaml
name: CI Pipeline

on: [ push, pull_request ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', cache: maven }
      - run: mvn compile

  unit-test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', cache: maven }
      - run: mvn test
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: target/surefire-reports/

  integration-test:
    needs: unit-test   # only runs if unit-test passes
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', cache: maven }
      - run: mvn verify -P integration-tests
```

**Example 2 — BAD vs GOOD: stage ordering:**
```yaml
# BAD: slow E2E tests run before fast unit tests
# 45-minute wait to discover a 10-second fix
stages:
  - e2e-tests     # 45 min
  - unit-tests    # 3 min
  - build         # 2 min

# GOOD: fail fast — cheapest/fastest first
stages:
  - build         # 2 min — fail fast on compile errors
  - unit-tests    # 3 min — catch most bugs here
  - integration   # 8 min — catch service-boundary bugs
  - e2e-tests     # 45 min — only runs if all above pass
```

---

### ⚖️ Comparison Table

| Pipeline Style | Definition | Reusability | Visibility | Best For |
|---|---|---|---|---|
| **Pipeline-as-Code (YAML)** | In repo file | Template inheritance | PR diff visible | All modern teams |
| UI-configured (classic Jenkins) | In Jenkins UI | Limited | Hidden, no diff | Legacy systems |
| Scripted pipeline (Groovy/shell) | In repo | Low (custom per repo) | Code review possible | Complex conditional logic |
| Makefile-based | In repo | Medium | Simple | Small projects, local dev |

How to choose: Always prefer Pipeline-as-Code (YAML) for new projects — it provides version history, PR review, and team visibility. Only use scripted pipelines when YAML DSL lacks the conditional logic you need.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A pipeline is just a build script | A pipeline is an ordered sequence of gated stages with artifact passing, environment management, and deployment. A build script is one stage inside a pipeline |
| All stages should run in parallel for speed | Stages with dependencies must be sequential. Running tests before the build completes produces no artifact to test — parallel is only valid for independent stages |
| A passing pipeline means the software is production-ready | A pipeline is only as good as its stages. A pipeline with no security scanning and no integration tests produces false confidence |
| The pipeline definition doesn't need code review | Pipeline changes are as critical as application code changes. A pipeline change that removes the security stage is a security vulnerability |

---

### 🚨 Failure Modes & Diagnosis

**1. Pipeline Takes Too Long — Feedback Loop Destroyed**

**Symptom:** Developers commit and walk away. By the time the result arrives, they're in a meeting. The fast feedback loop is gone.

**Root Cause:** No parallelism, no caching, E2E tests in the fast-feedback stage.

**Diagnostic:**
```bash
# GitHub Actions: view step timing
gh run view <run-id> --log | grep "##[timing]"
# Or view in the web UI under each job's step breakdown
```

**Fix:** Parallelise independent stages. Move E2E tests to post-merge. Add dependency caching.

**Prevention:** Set a 10-minute budget for the PR-blocking stage. Alert if any run exceeds it.

---

**2. Secrets Leaked in Pipeline Logs**

**Symptom:** Pipeline logs visible to all team members contain database passwords or API keys printed during a debug step.

**Root Cause:** Secrets passed as environment variables get echoed by careless `echo` or build tool output. Pipeline logs are often world-readable inside the org.

**Diagnostic:**
```bash
# Search pipeline logs for patterns
gh run view <run-id> --log | grep -E \
  "(password|secret|key|token).*=" -i
```

**Fix:**
```yaml
# BAD: hardcoded secret in pipeline
env:
  DB_PASSWORD: "5up3rS3cr3t"

# GOOD: reference from secrets store
env:
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
# GitHub Actions masks secrets in logs automatically
```

**Prevention:** Never echo environment variables in pipeline steps. Use secret scanning tools on pipeline definitions.

---

**3. Inconsistent Environments Cause "Works in CI, Fails in Prod"**

**Symptom:** Every CI run passes, but the app crashes in production citing a missing library or wrong Java version.

**Root Cause:** CI runner uses a different OS image or tool version than the production environment. Dependency installed globally on the runner, not declared in the project.

**Diagnostic:**
```bash
# Compare CI environment
echo "Java: $(java -version 2>&1)"
echo "OS: $(uname -a)"
# Compare against production:
ssh prod-host "java -version; uname -a"
```

**Fix:** Use Docker-based pipeline runners with the exact same base image as production. Define all tool dependencies in the pipeline, not relying on runner globals.

**Prevention:** Enforce a "container-first" pipeline policy — every stage runs in a defined Docker image.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — the practice that pipelines implement; CI is the goal, pipeline is the mechanism
- `Automated Testing` — tests are the content of the test stages; without them, a pipeline has nothing meaningful to verify
- `Version Control` — pipelines are triggered by commits and are themselves stored in version control

**Builds On This (learn these next):**
- `Build Stage` — the first pipeline stage: compiling code and producing artifacts
- `Test Stage` — the gating stage that validates correctness before deployment
- `Deployment Pipeline` — the extended pipeline that includes deployment to production environments

**Alternatives / Comparisons:**
- `Makefile` — a simpler, single-machine alternative for small projects without multi-environment deployment needs
- `Jenkins` — a popular pipeline server with scripted and declarative pipeline DSLs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Ordered automated stages from commit      │
│              │ to deployable release                     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Manual, inconsistent, unskippable-by-     │
│ SOLVES       │ accident delivery steps                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Fail fast: order stages cheapest/fastest  │
│              │ first — catch 90% of bugs in 5 min        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any team shipping code to any environment │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — pipelines apply universally         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Consistency + visibility vs upfront       │
│              │ investment in pipeline infrastructure     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Security checkpoints between code and    │
│              │  production — each one costs nothing to   │
│              │  pass, everything to fail"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Build Stage → Test Stage → Artifact       │
│              │ → Deployment Pipeline                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team's pipeline has these stages in order: Build (2m) → Security Scan (15m) → Unit Tests (4m) → Integration Tests (10m) → Deploy Staging (3m) → E2E Tests (30m). A developer pushes a typo fix. What is the actual problem with this ordering, and how would you redesign it? Consider both speed and the types of failures most likely to occur at each stage.

**Q2.** Your company just acquired a startup whose entire product is deployed by manually running a shell script on a server. You have 3 months to implement a proper CI/CD pipeline for their 5-service architecture. Design the minimal first pipeline that provides real safety gates but can be built in 2 weeks — then describe the evolution over months 2 and 3.

