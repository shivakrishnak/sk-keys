---
layout: default
title: "GitLab CI"
parent: "CI/CD"
nav_order: 1001
permalink: /ci-cd/gitlab-ci/
number: "1001"
category: CI/CD
difficulty: ★★☆
depends_on: Continuous Integration, Pipeline as Code, Git Basics
used_by: Continuous Delivery, Continuous Deployment, Artifact Registry
related: GitHub Actions, Jenkins, CircleCI
tags:
  - cicd
  - devops
  - git
  - intermediate
---

# 1001 — GitLab CI

⚡ TL;DR — GitLab CI is GitLab's built-in CI/CD engine that defines pipelines in `.gitlab-ci.yml`, tightly integrated with GitLab's merge requests, container registry, and security scanning in a single platform.

| #1001 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Continuous Integration, Pipeline as Code, Git Basics | |
| **Used by:** | Continuous Delivery, Continuous Deployment, Artifact Registry | |
| **Related:** | GitHub Actions, Jenkins, CircleCI | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams hosting code on GitLab still need external CI systems — Jenkins, CircleCI — connected via webhooks, access tokens, and separate accounts. Security scans, dependency checks, and container scanning each require different third-party integrations. The results scatter across multiple dashboards. A merge request shows a code review but you must click 3 links to see test results, security findings, and deployment status.

**THE BREAKING POINT:**
Platform fragmentation means operational overhead, multiple credential management risks, and delayed feedback. When GitLab is the development platform, requiring a separate system for every pipeline stage adds friction that compounds with team size.

**THE INVENTION MOMENT:**
This is exactly why GitLab CI was created: deliver CI/CD, security scanning, container registry, and deployment tracking as native features of the GitLab platform — one tool, one authentication model, one dashboard for code and its delivery pipeline.

---

### 📘 Textbook Definition

**GitLab CI/CD** is the automated build, test, and deployment system built into GitLab (both gitlab.com and self-hosted). Pipelines are defined in `.gitlab-ci.yml` at the repository root. Pipelines are composed of stages (sequential groups) and jobs (parallel execution units within a stage). Jobs run on GitLab Runners — agents that execute pipeline steps in Docker containers, VMs, or Kubernetes pods. GitLab CI is tightly integrated with merge requests, showing pipeline status inline, blocking merges on failure, and providing direct links to job logs, coverage reports, and security scan findings.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GitLab CI runs your pipeline straight from your `.gitlab-ci.yml` — no separate CI server needed.

**One analogy:**
> GitLab CI is like having a test kitchen built into your recipe book. When you write a new recipe (code), the kitchen automatically tries it out using the instructions printed at the back of the book (`.gitlab-ci.yml`). Every recipe book has its own kitchen. You don't need to rent a separate kitchen somewhere else.

**One insight:**
GitLab CI's strength is **platform integration** — security scans, SAST results, merge approval policies, and deployment environments all live in the same GitLab UI. This integration creates visibility that external CI tools can't replicate without significant configuration effort.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Jobs within a stage run in parallel; stages execute sequentially.
2. Each job runs in an isolated environment (Docker container or runner workspace).
3. Artifacts produced by one job can be passed to successive jobs via `artifacts:` and `dependencies:`.

**DERIVED DESIGN:**
The stage/job model maps CI/CD concerns to a clear structure: stages define phase (build, test, deploy) while jobs define execution units within that phase (unit-tests, linting, sast-scan all in the `test` stage and run in parallel). This maximises parallelism within phases while preserving phase ordering guarantees.

GitLab CI's `needs:` keyword breaks the strict stage ordering — a job can depend on any prior job regardless of stage, enabling a fully-optimised DAG execution without artificial stage bottlenecks.

**THE TRADE-OFFS:**
**Gain:** Complete DevSecOps in one platform. Native security scanning (SAST, DAST, dependency scanning) included in licensed tiers. No separate webhook configuration. GitLab Runners can be self-hosted for compliance or cost reasons.
**Cost:** Platform lock-in to GitLab. YAML can become complex for large pipelines. Self-hosted GitLab instances require their own operational management. Advanced features (security dashboard, compliance) require paid tiers.

---

### 🧪 Thought Experiment

**SETUP:**
A security-conscious team runs SAST on every PR. With an external CI tool, SAST results appear in a separate dashboard. With GitLab CI, they appear inline in the merge request.

**WHAT HAPPENS WITHOUT GITLAB CI INTEGRATION:**
Developer opens an MR. CI runs `snyk test` in Jenkins. Jenkins marks the build red. Developer must open Jenkins, find the Snyk report, match CVE IDs back to the merge request's code, and decide if any block the merge. The security engineer has a separate Snyk dashboard they also must monitor. Three tools open simultaneously.

**WHAT HAPPENS WITH GITLAB CI INTEGRATION:**
Developer opens an MR. GitLab SAST job runs. Results appear in the MR's "Security" tab — specific lines of code with findings highlighted in the diff. Security engineer gets a single GitLab notification. Merge blocked automatically if critical finding present. One tool, one view.

**THE INSIGHT:**
Pipeline results are only useful when they're where decisions are made. GitLab CI puts results in the merge request — exactly where the accept/reject decision happens.

---

### 🧠 Mental Model / Analogy

> GitLab CI is like a building with all services under one roof: the code lives on Floor 1, the CI pipeline runs on Floor 2, security scans on Floor 3, the container registry on Floor 4, and the deployment environment on Floor 5. GitHub + Jenkins + Snyk + ECR + Spinnaker is like renting five different buildings across town and coordinating between them.

- "Building's elevator" → GitLab's internal APIs connecting pipeline to MR
- "Floor 1 (code)" → GitLab repository
- "Floor 2 (CI)" → GitLab Runner executing `.gitlab-ci.yml`
- "Floor 4 (container registry)" → GitLab Container Registry
- "Five separate buildings" → GitHub + Jenkins + external tools

Where this analogy breaks down: a single-building setup has single-point-of-failure risk. If GitLab is down, code, CI, and deployment are all unavailable simultaneously.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
GitLab CI runs your tests and deploys your code automatically. You write a recipe file in your project (`.gitlab-ci.yml`), and every time you push code, GitLab follows that recipe — building, testing, and deploying without any extra tools.

**Level 2 — How to use it (junior developer):**
Create `.gitlab-ci.yml` in the repo root. Define `stages:` (e.g., `[build, test, deploy]`). For each job, specify `stage:`, `image:` (Docker image to use), and `script:` (commands to run). Jobs in the same stage run in parallel. Artifacts are passed via `artifacts: paths:` and consumed with `dependencies:`. GitLab Runners must be available (shared runners on gitlab.com, or registered self-hosted runners).

**Level 3 — How it works (mid-level engineer):**
When a pipeline triggers, GitLab's CI coordinator assigns jobs to idle runners matching the job's `tags:`. The runner pulls the specified Docker image, clones the repo at the commit SHA into the container, executes `script:` steps, and reports results back to GitLab. For `needs:` DAG pipelines, the coordinator tracks job completion and releases dependent jobs as soon as their dependencies finish — without waiting for the entire stage. GitLab's pipeline YAML supports `include:` to split large configs across reusable template files, `extends:` for inheritance, and `!reference` for YAML anchors.

**Level 4 — Why it was designed this way (senior/staff):**
GitLab CI was redesigned around 2018 with the `needs:` keyword to move from a strict stage-waterfall model to a DAG (directed acyclic graph). This was motivated by pipelines where a test job that takes 30 minutes was blocked by an lint job that takes 30 seconds in the same stage. The DAG model allows the deploy job to start as soon as the build job finishes, even if slow security scans are still running. GitLab's Auto DevOps feature (2018) takes this further — automatically detecting project type and generating a complete pipeline without any YAML, implementing GitLab's opinionated production pipeline template.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│       GITLAB CI PIPELINE EXECUTION          │
├─────────────────────────────────────────────┤
│  .gitlab-ci.yml defines:                   │
│  stages: [build, test, security, deploy]    │
│                                             │
│  STAGE: build (sequential)                  │
│    job: compile → runs on runner-1          │
│         ↓ artifact: app.jar                 │
│  STAGE: test (parallel jobs)                │
│    job: unit-tests │ linting │ sast-scan    │
│    all run simultaneously on different      │
│    runners; all must pass for next stage    │
│         ↓                                   │
│  STAGE: security (parallel)                 │
│    job: dependency-scan │ container-scan    │
│         ↓                                   │
│  STAGE: deploy                              │
│    job: deploy-staging (manual: false)      │
│    job: deploy-prod (when: manual)          │
└─────────────────────────────────────────────┘
```

**DAG with `needs:` (breaks stage barrier):**
```yaml
# Without needs: deploy waits for ALL test jobs (even slow ones)
# With needs: deploy starts as soon as build completes
deploy-staging:
  stage: deploy
  needs: ["compile"]  # skip waiting for sast-scan (30 min)
  script:
    - ./deploy.sh staging
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer pushes branch → GitLab creates pipeline
  → build stage: compile → app.jar artifact created
  → test stage: [unit-tests ✓ | linting ✓ | sast ✓]
  → security stage: [dependency-scan ✓ | trivy ✓]
  → MR: pipeline PASSED — shows in merge request
  → Security tab: "No critical vulnerabilities found"
  → Merge approved → deploy-staging triggered
  → GitLab Environments page: staging v1.2.3 deployed
  [← YOU ARE HERE]
  → deploy-prod: awaits manual trigger
```

**FAILURE PATH:**
```
sast-scan fails: SQL injection detected in line 47
  → Stage 'security' FAILS
  → deploy stage: blocked
  → MR: pipeline FAILED; Security tab shows finding
  → Developer fixes line 47 → repushes
  → Pipeline reruns from scratch
```

**WHAT CHANGES AT SCALE:**
At 100+ runners, runner registration and maintenance becomes a platform engineering concern. GitLab's runner autoscaling (on AWS/GCP/Azure) provisions runners on-demand and terminates idle ones. Large monorepos use `rules:` to run jobs only when relevant files change — avoiding full pipeline runs for documentation-only changes.

---

### 💻 Code Example

**Example 1 — Complete `.gitlab-ci.yml`:**
```yaml
# .gitlab-ci.yml
image: eclipse-temurin:21-jdk  # default image for all jobs

stages:
  - build
  - test
  - security
  - deploy

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"

cache:
  paths:
    - .m2/repository   # cache Maven deps

compile:
  stage: build
  script:
    - mvn --batch-mode package -DskipTests
  artifacts:
    paths:
      - target/*.jar
    expire_in: 1 hour

unit-tests:
  stage: test
  needs: ["compile"]   # DAG: start as soon as compile passes
  script:
    - mvn --batch-mode test
  artifacts:
    when: always
    reports:
      junit: target/surefire-reports/*.xml

sast:
  stage: security
  # GitLab SAST template (GitLab Ultimate includes this)
  include:
    - template: Security/SAST.gitlab-ci.yml

deploy-staging:
  stage: deploy
  needs: ["unit-tests"]
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - ./scripts/deploy.sh staging $CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-prod:
  stage: deploy
  needs: ["deploy-staging"]
  environment:
    name: production
    url: https://example.com
  script:
    - ./scripts/deploy.sh production $CI_COMMIT_SHA
  when: manual   # requires manual trigger in GitLab UI
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

**Example 2 — Reusable pipeline templates with `include:`:**
```yaml
# .gitlab-ci.yml in application repo
include:
  # Reference a shared template in another repo
  - project: 'platform/ci-templates'
    ref: main
    file: '/templates/java-build.yml'
  - project: 'platform/ci-templates'
    ref: main
    file: '/templates/security-scan.yml'

# Override only what's specific to this service
deploy-prod:
  extends: .deploy-template   # from included file
  environment:
    name: production
    url: https://payments.example.com
```

---

### ⚖️ Comparison Table

| Feature | GitLab CI | GitHub Actions | Jenkins |
|---|---|---|---|
| Platform | GitLab | GitHub | Any |
| Config | YAML (.gitlab-ci.yml) | YAML (.github/workflows/) | Groovy (Jenkinsfile) |
| Built-in security scans | Yes (Ultimate tier) | Via actions | Via plugins |
| Container registry | Built-in | GHCR | Via plugins |
| Self-hosted option | GitLab Runner | Self-hosted runner | Controller + agents |
| Operations burden | Low | None | High |
| Best For | GitLab orgs, DevSecOps | GitHub repos | Air-gapped, complex |

How to choose: Use GitLab CI for GitLab-hosted repositories, especially when security scanning integration matters. Use GitHub Actions for GitHub-hosted repositories. Use Jenkins only for air-gapped or highly customised enterprise pipelines.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GitLab CI requires gitlab.com | GitLab (and thus GitLab CI) can be self-hosted on-premises. GitLab Runners can also be self-hosted independently of gitlab.com |
| Jobs in the same stage wait for each other | Jobs in the same stage run in parallel. Only stages are sequential by default. Use `needs:` for finer DAG control |
| GitLab SAST is free | Basic SAST is included in all tiers, but advanced security dashboards, compliance reports, and vulnerability management require GitLab Ultimate |
| `CI_COMMIT_SHA` always refers to the PR's head | In merge request pipelines, `CI_COMMIT_SHA` is the merge result commit, not just the head — it helps detect integration failures before merge |

---

### 🚨 Failure Modes & Diagnosis

**1. Runner Starvation — Jobs Stuck Pending**

**Symptom:** Jobs show "pending" status for 15+ minutes. No runner picks them up.

**Root Cause:** No runners with a matching tag are available. Or all runners are busy and no autoscaling is configured.

**Diagnostic:**
```bash
# GitLab UI: Settings → CI/CD → Runners
# Check list of registered runners and their status
# Via API:
curl -s --header "PRIVATE-TOKEN: $GL_TOKEN" \
  "https://gitlab.com/api/v4/runners?status=online"
```

**Fix:** Register additional runners. For shared gitlab.com runners: verify the project has access to shared runners. For self-hosted: check runner `concurrent` setting.

**Prevention:** Monitor runner queue depth. Alert when pending job count > threshold. Configure autoscaling for variable load.

---

**2. Artifact Not Found in Dependent Job**

**Symptom:** Job fails with "artifact not found" when trying to use output from a previous job.

**Root Cause:** `dependencies:` not declared in the consuming job. Or artifact `expire_in` set too short and artifact expired before the job ran.

**Diagnostic:**
```bash
# Check the artifacts section in the source job
# UI: Pipeline → Job → Browse artifacts
# If missing: check expire_in setting
```

**Fix:**
```yaml
# BAD: job doesn't declare it needs the artifact
deploy:
  stage: deploy
  script: java -jar target/*.jar  # fails: no jar here

# GOOD: declare dependency explicitly
deploy:
  stage: deploy
  dependencies:
    - compile        # downloads compile job's artifacts
  script: java -jar target/*.jar
```

**Prevention:** Always declare `dependencies:` explicitly. Set `expire_in` conservatively (1 day minimum for cross-stage artifacts).

---

**3. Pipeline Triggered Recursively by CI Commits**

**Symptom:** A pipeline that updates version numbers commits those changes — triggering a new pipeline — which updates version numbers — triggering a new pipeline. Infinite loop.

**Root Cause:** `CI_COMMIT_MESSAGE` check missing. A job that commits to the repo triggers another pipeline run.

**Diagnostic:**
```bash
# GitLab: check pipeline source
# Pipelines triggered by CI commits have source: push
# Add to pipeline that commits:
```

**Fix:**
```yaml
update-version:
  script:
    - git config user.email "ci@example.com"
    - git commit -m "[skip ci] Bump version to $NEW_VERSION"
    # [skip ci] in commit message prevents pipeline trigger
  rules:
    # Skip if this pipeline was already triggered by a CI commit
    - if: '$CI_COMMIT_MESSAGE =~ /\[skip ci\]/'
      when: never
    - when: on_success
```

**Prevention:** Always add `[skip ci]` or `[ci skip]` to automated commit messages. Use `rules:` to exclude CI bot commits.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — GitLab CI implements CI; the practice context is required first
- `Pipeline as Code` — GitLab CI is a Pipeline as Code implementation; the concept guides how to use `.gitlab-ci.yml`
- `Git Basics` — GitLab CI triggers on git events; understanding push and MR mechanics is needed

**Builds On This (learn these next):**
- `Artifact Registry` — GitLab's built-in Container Registry stores Docker artifacts produced by CI jobs
- `SAST (Static Analysis)` — GitLab CI includes SAST templates for automated security scanning
- `Continuous Delivery` — GitLab CI's deploy jobs implement CD pipeline stages

**Alternatives / Comparisons:**
- `GitHub Actions` — equivalent platform for GitHub-hosted repositories
- `Jenkins` — self-hosted CI with more flexibility but higher operational cost
- `CircleCI` — cloud-hosted CI focused on speed, alternative for cloud-agnostic teams

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ GitLab's built-in CI/CD: YAML pipelines   │
│              │ with native security & registry integration│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Platform fragmentation: separate CI, SCM, │
│ SOLVES       │ security scanning, container registry      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ `needs:` breaks stage barriers — enables  │
│              │ fully optimised DAG execution             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ GitLab is your SCM, especially needing    │
│              │ DevSecOps in one platform                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using GitHub — GitHub Actions is better   │
│              │ integrated for GitHub repositories        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ All-in-one convenience vs single point of │
│              │ failure if GitLab is down                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your SCM and CI in the same house —      │
│              │  merge requests and pipelines share a wall"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CircleCI → Tekton → ArgoCD → GitOps       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team migrates from Jenkins to GitLab CI. Their Jenkins pipeline has 3 complex Groovy shared libraries with conditional logic: "if branch starts with `release/`, run extra performance tests; if PR targets `main`, run security scan; if it's a nightly schedule, run full suite." Map each of these conditions to their GitLab CI equivalent (`rules:`, `only/except`, `workflow:`), noting where GitLab CI's YAML DSL is more limiting than Jenkins' Groovy and how you'd work around each limitation.

**Q2.** Your GitLab CI pipeline runs SAST, Dependency Scanning, and Container Scanning on every MR. The scans add 25 minutes to every pipeline. The team starts skipping the security stage with `CI_SKIP_SECURITY=true` environment variable. Design a GitLab CI enforcement mechanism that prevents bypassing required security scans without slowing down the pipeline — considering both the technical enforcement and the user experience for developers waiting on scan results.

