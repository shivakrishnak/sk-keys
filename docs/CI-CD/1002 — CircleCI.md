---
layout: default
title: "CircleCI"
parent: "CI/CD"
nav_order: 1002
permalink: /ci-cd/circleci/
number: "1002"
category: CI/CD
difficulty: ★★☆
depends_on: Continuous Integration, Pipeline as Code, Docker
used_by: Continuous Delivery, Continuous Deployment, Artifact Registry
related: GitHub Actions, GitLab CI, Jenkins
tags:
  - cicd
  - devops
  - docker
  - intermediate
---

# 1002 — CircleCI

⚡ TL;DR — CircleCI is a cloud-hosted CI/CD platform optimised for speed, with Docker-first execution, first-class parallelism, and an orbs marketplace for reusable configuration — paid per compute usage.

| #1002 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Continuous Integration, Pipeline as Code, Docker | |
| **Used by:** | Continuous Delivery, Continuous Deployment, Artifact Registry | |
| **Related:** | GitHub Actions, GitLab CI, Jenkins | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams in 2014–2018 using GitHub needed CI. Jenkins required server management. GitHub Actions didn't exist. The gap: a hosted, developer-friendly CI service that could be set up in minutes, ran in Docker containers natively, and provided enough flexibility for production-scale pipelines without the Jenkins operational burden.

**THE BREAKING POINT:**
Jenkins was too heavy. Simple CI tools (Travis CI) lacked advanced features. Teams needed: fast Docker-based execution, parallelism across multiple machines, SSH debugging of builds, and context-based secrets management — without running their own infrastructure.

**THE INVENTION MOMENT:**
This is exactly why CircleCI was created: a developer-first hosted CI service combining speed (Docker-native, parallelism), flexibility (YAML config + orbs), and zero infrastructure management — billing only for what you use.

---

### 📘 Textbook Definition

**CircleCI** is a cloud-hosted CI/CD platform that executes automated build, test, and deployment pipelines. Configuration is defined in `.circleci/config.yml` using CircleCI's YAML DSL. Pipelines consist of workflows containing jobs; jobs run in Docker containers, Linux/macOS VMs, or Arm machines. CircleCI's key features include: built-in test parallelism (auto-splitting tests across multiple containers), SSH access for debugging failing builds, orbs (reusable, versioned configuration packages from CircleCI's public registry), and contexts (encrypted environment variable groups applied to jobs). CircleCI integrates with GitHub and Bitbucket via OAuth.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CircleCI runs your pipelines in Docker containers in the cloud — fast, configurable, zero servers to manage.

**One analogy:**
> CircleCI is like a professional car service: you describe the journey (pipeline YAML), tell it what vehicle you need (Docker image), and it drives for you. You don't maintain a fleet. You're billed by the journey. If you need to arrive faster, order multiple cars (parallelism). If the drive goes wrong, you can briefly ride along and debug (SSH access).

**One insight:**
CircleCI's defining technical feature is **resource class granularity** — you specify exactly how much CPU and RAM each job gets. A memory-intensive integration test gets `xlarge` (8 vCPU, 16 GB RAM); a simple linting job gets `small` (1 vCPU, 2 GB RAM). This makes build cost/performance tuning explicit, not accidental.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Jobs run in Docker containers — the executor is always declared, never assumed.
2. Workflows orchestrate job dependencies — jobs can fan out (parallel) and fan in (join).
3. Contexts provide secrets — sensitive variables are scoped to orgs and applied per workflow.

**DERIVED DESIGN:**
Every job declares its executor: a Docker image, a machine (VM), or a macOS instance. This explicitness prevents environment drift — the config file fully specifies the execution environment. Caching (via `save_cache`/`restore_cache`) is explicit too — the developer defines what to cache and keyed on what file hash. Nothing is implicit.

Orbs solve the DRY problem: instead of copying 20 lines of Docker Hub authentication YAML into every project's config, `docker/login@3.0` is one line. Orbs are versioned and auditable.

**THE TRADE-OFFS:**
**Gain:** Fast builds (parallelism, caching). Zero ops. SSH debugging. Fine-grained resource classes.
**Cost:** Per-credit billing can be expensive at scale. Orb supply chain risk (third-party code in your pipeline). GitHub/Bitbucket only — no GitLab integration. Limited free tier.

---

### 🧪 Thought Experiment

**SETUP:**
A team has a 25-minute test suite. Without parallelism, every PR waits 25 minutes before merge is possible. With CircleCI parallelism, the same tests run in 5 minutes.

**WHAT HAPPENS WITHOUT PARALLELISM:**
Developer pushes PR at 10:00 AM. CI starts test run. 10:25 AM: tests pass. Review can begin. If the reviewer is busy until 10:30 AM, the developer has been idle for 30 minutes. Twenty PRs per day = 500 minutes (8+ hours) of waiting time across the team daily.

**WHAT HAPPENS WITH CIRCLECI PARALLELISM (5 containers):**
Developer pushes PR at 10:00 AM. CircleCI splits 500 tests across 5 containers (100 tests each). 10:05 AM: all containers finish. PR can be reviewed at 10:05 AM. Five minutes saved per PR × 20 PRs = 100 minutes per day returned to the team.

**THE INSIGHT:**
Fast CI feedback isn't a luxury — it's a throughput multiplier. A 5x speedup in test time multiplied across 20 PRs per day has a larger productivity impact than 20 individual hours of developer time.

---

### 🧠 Mental Model / Analogy

> CircleCI's workflow is like an airport with gates and connections. Your pipeline is a flight itinerary: first leg (build job) → fanout (parallel test gates) → connection wait (all gates must depart) → final leg (deploy job). Orbs are like airline partnerships — established connections you don't have to negotiate yourself.

- "Flight legs" → pipeline jobs
- "Gate departures in parallel" → parallel test jobs
- "Connection wait (all gates)" → fan-in join after parallel jobs
- "Airline partnership" → orb (reusable third-party integration)
- "Flight itinerary" → workflow definition in `config.yml`

Where this analogy breaks down: unlike airport gates, CircleCI jobs don't require physical proximity — any number of parallel jobs can run simultaneously without a physical constraint.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CircleCI runs your tests in the cloud automatically. You write a config file telling it what Docker image to use and what commands to run. It runs those commands whenever you push code and reports pass or fail.

**Level 2 — How to use it (junior developer):**
Create `.circleci/config.yml`. Set `version: 2.1`. Define jobs with `docker:` executor and `steps:`. Define a `workflows:` section to connect jobs. Use `persist_to_workspace`/`attach_workspace` to share files between jobs. Use `save_cache`/`restore_cache` for dependency caching keyed on lock file hash. Use CircleCI's web UI to see job status, logs, and timing. Enable SSH with "Rerun job with SSH" for debugging.

**Level 3 — How it works (mid-level engineer):**
CircleCI's pipeline engine is event-driven — GitHub/Bitbucket webhooks trigger pipeline execution. The pipeline config is fetched from `.circleci/config.yml` at the triggering commit SHA. Jobs are dispatched to CircleCI's compute fleet. Docker executor creates a container from the specified image on CircleCI-managed hardware. Steps execute as shell commands in the container. Workspace volumes persist files across jobs within a workflow. Test splitting uses CircleCI's timing data from previous runs to create equal-duration shards.

**Level 4 — Why it was designed this way (senior/staff):**
CircleCI's orbs system (2018) was designed to solve the "copy-paste CI boilerplate" problem that plagued teams with multiple repositories. An orb is a package for CircleCI configuration — it can define jobs, commands, and executors that any project can reference by name and version. The orbs registry provides auditable, versioned third-party integrations. The design tension: convenience (use trusted orbs) vs security (orbs execute arbitrary code in your pipeline). CircleCI addresses this with an orb certification program and the ability to restrict to certified-only orbs in org settings.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│      CIRCLECI WORKFLOW EXECUTION            │
├─────────────────────────────────────────────┤
│  Trigger: push to GitHub                    │
│         ↓                                   │
│  CircleCI fetches .circleci/config.yml      │
│  Workflow: build → [parallel tests] → deploy│
│                                             │
│  JOB: build                                 │
│    Executor: docker: eclipse-temurin:21-jdk │
│    Steps:                                   │
│      - checkout                             │
│      - restore_cache (key: pom-{{checksum}})│
│      - run: mvn package -DskipTests         │
│      - save_cache: .m2/repository           │
│      - persist_to_workspace: target/*.jar   │
│                                             │
│  JOB: test (parallelism: 4)                 │
│    Run on 4 containers simultaneously       │
│    Each runs 1/4 of the test suite          │
│    Auto-split by previous timing data       │
│                                             │
│  JOB: deploy (requires: build + test)       │
│    attach_workspace: retrieve jar           │
│    run: ./deploy.sh production              │
└─────────────────────────────────────────────┘
```

**Test splitting mechanism:**
CircleCI stores timing data from previous runs. When `parallelism: 4` is set, it divides the test list into 4 shards with approximately equal total duration. Container 1 runs the tests that historically take the longest; container 4 runs the quickest. All 4 finish at approximately the same time — minimising total wall-clock duration.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Push to GitHub → CircleCI webhook
  → build job: mvn package (3 min, medium: 2vCPU)
  → persist jar to workspace
  → test job ×4 parallel [← YOU ARE HERE]
    container 1: tests 1–125 (4m 50s)
    container 2: tests 126–250 (4m 55s)
    container 3: tests 251–375 (4m 52s)
    container 4: tests 376–500 (4m 48s)
  → all pass → deploy job
  → GitHub PR: ✓ pipeline passed (8 total minutes)
```

**FAILURE PATH:**
```
container 2 test fails: OrderServiceTest#refund
  → CircleCI marks test job FAILED
  → deploy job: not triggered (requires test)
  → UI shows which container + which test
  → "Rerun with SSH" → developer SSHes into
    container 2's environment for live debugging
```

**WHAT CHANGES AT SCALE:**
At 1000 pipeline runs per day, CircleCI credits become a cost centre. Teams implement: (1) skip CI for docs/config-only changes; (2) reduce resource classes where sufficient; (3) maximise cache hit rate (cache metrics visible in dashboard); (4) split test files more granularly for smaller per-container time variance.

---

### 💻 Code Example

**Example 1 — Complete CircleCI config with orbs and parallelism:**
```yaml
# .circleci/config.yml
version: 2.1

orbs:
  docker: circleci/docker@2.4.0  # docker login/build/push

jobs:
  build:
    docker:
      - image: cimg/openjdk:21.0
    resource_class: medium  # 2 vCPU, 4 GB RAM
    steps:
      - checkout
      - restore_cache:
          keys:
            - v1-deps-{{ checksum "pom.xml" }}
            - v1-deps-
      - run:
          name: Build
          command: mvn --batch-mode package -DskipTests
      - save_cache:
          key: v1-deps-{{ checksum "pom.xml" }}
          paths: [ ~/.m2 ]
      - persist_to_workspace:
          root: .
          paths: [ target ]

  test:
    docker:
      - image: cimg/openjdk:21.0
      - image: postgres:15-alpine   # sidecar DB for integration tests
        environment:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: test
    resource_class: medium
    parallelism: 4
    steps:
      - checkout
      - attach_workspace: { at: . }
      - restore_cache:
          keys: [ "v1-deps-{{ checksum \"pom.xml\" }}" ]
      - run:
          name: Run tests (shard {{ .Inputs.circleci_split }})
          command: |
            # Split test list by timing history
            TESTS=$(circleci tests glob "src/test/**/*.java" \
              | circleci tests split --split-by=timings)
            mvn test -Dtest="$TESTS"
      - store_test_results:
          path: target/surefire-reports

  build-and-push-image:
    docker:
      - image: cimg/base:stable
    steps:
      - checkout
      - attach_workspace: { at: . }
      - docker/check   # verify Docker Hub credentials
      - docker/build:
          image: myorg/myapp
          tag: $CIRCLE_SHA1
      - docker/push:
          image: myorg/myapp
          tag: $CIRCLE_SHA1

workflows:
  ci-cd:
    jobs:
      - build
      - test:
          requires: [ build ]
      - build-and-push-image:
          requires: [ test ]
          context: docker-hub-creds  # contains DOCKER_LOGIN, DOCKER_PASSWORD
          filters:
            branches:
              only: main   # only build image on main
```

---

### ⚖️ Comparison Table

| Feature | CircleCI | GitHub Actions | GitLab CI | Jenkins |
|---|---|---|---|---|
| Hosting | Cloud | GitHub-hosted | Self/Cloud | Self-hosted |
| Test parallelism | Built-in + auto-split | Matrix strategy | parallel: | Plugin |
| SSH debugging | Built-in | Via tmate action | None native | Via plugin |
| Resource classes | Granular (credit-based) | Fixed sizes | Runner-dependent | Custom |
| Orbs/Actions | Orbs registry | Actions marketplace | Templates | Plugins |
| Best For | Speed-focused cloud teams | GitHub repos | GitLab repos | Air-gapped, complex |

How to choose: CircleCI's SSH debugging and fine-grained resource classes make it attractive when build speed and developer experience are priorities. Use GitHub Actions if your source is on GitHub and you prefer tighter integration. CircleCI is particularly strong for mobile/iOS builds via macOS executors.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CircleCI's free tier covers most OSS projects | Free tier has limited weekly credits. Large OSS projects may need the CircleCI Open Source plan — separate from the standard free tier |
| `parallelism: N` automatically splits tests correctly | `parallelism:` provisions N containers; you must call `circleci tests split` explicitly to distribute tests. Without it, all N containers run the full suite |
| Contexts are equivalent to GitHub secrets | Contexts are org-level secret groups with access controls. A context can be restricted to specific branches or approval workflows — more powerful than simple repository secrets |
| SSH debugging persists the environment indefinitely | SSH sessions expire after 10 minutes of inactivity or 2 hours maximum — plan accordingly when debugging slow test failures |

---

### 🚨 Failure Modes & Diagnosis

**1. Cache Miss on Every Run — Build 3x Slower**

**Symptom:** Every build downloads all Maven dependencies from scratch. Cache key always misses.

**Root Cause:** Cache key is based on a file that changes on every commit (e.g., `package.json` with a dynamic timestamp in the `version` field).

**Diagnostic:**
```bash
# Check the cache key being generated
# CircleCI UI: Job → Steps → Restore Cache → key used
# Compare with actual pom.xml checksum:
echo -n "v1-deps-$(shasum pom.xml | cut -d' ' -f1)"
```

**Fix:** Key should be keyed on the lock file's stable content, not the file's mtime:
```yaml
restore_cache:
  keys:
    - v1-deps-{{ checksum "pom.xml" }}  # stable hash of content
    - v1-deps-     # fallback: any existing cache
```

**Prevention:** Always provide a fallback key prefix (e.g., `v1-deps-`) that matches any cache with the same prefix — used when the exact key misses.

---

**2. Credit Overrun From Large Resource Class**

**Symptom:** Monthly bill unexpectedly high. Credits consumed 3x faster than expected.

**Root Cause:** All jobs using `xlarge` resource class when `medium` would suffice. Or long-running jobs keeping xl instances alive waiting for manual approval.

**Diagnostic:**
```bash
# CircleCI: Insights → Pipelines → Job metrics
# View: average resource_class per job, credit consumption per run
# Check which jobs consume the most credits
```

**Fix:** Audit resource class per job. Use `small` for linting, `medium` for builds, `large`/`xlarge` only for memory-intensive tests.

**Prevention:** Set a monthly credit budget alert in CircleCI organisation settings. Review resource class assignment during pipeline design.

---

**3. Test Split Not Balanced — One Container Much Slower**

**Symptom:** Parallel test job takes 12 minutes despite `parallelism: 4`. Three containers finish in 3 minutes; one runs for 12 minutes.

**Root Cause:** No timing data for the test split (first run) or tests have highly uneven durations. The slow container got all the heavy integration tests.

**Diagnostic:**
```bash
# Check each container's test output timing
# CircleCI: parallel job → individual container steps
# UI shows per-container duration for each step
```

**Fix:** Use `--split-by=timings` after a baseline run. For first run, use `--split-by=filesize` as a proxy:
```bash
circleci tests glob "src/test/**/*.java" \
  | circleci tests split \
    --split-by=timings \  # uses historical data after first run
    --timings-type=filename
```

**Prevention:** Store test results with `store_test_results` — CircleCI uses this to build timing history for future splits.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Continuous Integration` — CircleCI implements CI; the practice is the context
- `Pipeline as Code` — CircleCI's YAML config is an implementation of Pipeline as Code
- `Docker` — CircleCI's primary executor is Docker; understanding containers is required to configure jobs

**Builds On This (learn these next):**
- `Continuous Delivery` — CircleCI workflows extend to CD deployment stages
- `Artifact Registry` — Docker images built in CircleCI are pushed to registries for deployment
- `Test Parallelization` — CircleCI's `parallelism:` + `circleci tests split` implements this pattern

**Alternatives / Comparisons:**
- `GitHub Actions` — integrated with GitHub; zero-ops alternative for GitHub repositories
- `GitLab CI` — GitLab's built-in CI for GitLab-hosted repositories
- `Jenkins` — self-hosted alternative with more flexibility but high operational cost

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Cloud-hosted CI/CD: Docker-native, fast   │
│              │ parallelism, zero infrastructure ops      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Need fast, hosted CI with parallelism     │
│ SOLVES       │ and no server management overhead         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ `parallelism:` alone does nothing —       │
│              │ you MUST call `circleci tests split`      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Speed-focused cloud teams, mobile CI      │
│              │ (macOS), or needing SSH debug capability  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ GitHub-hosted repos (use GitHub Actions); │
│              │ air-gapped environments (use Jenkins)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Dev experience + speed vs credit billing  │
│              │ cost at high build volume                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Professional car service for builds:     │
│              │  describe the journey, pay per mile"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tekton → ArgoCD → GitOps                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** CircleCI bills by compute credits. Your team has 50 engineers merging 5 PRs each per week, with a pipeline averaging 12 minutes on `medium` resource class (10 credits/minute). Calculate monthly cost at $0.0006/credit. Then design three technical changes to cut this cost by 40% without reducing test coverage, and calculate the new estimate for each change.

**Q2.** Your iOS mobile app CI runs on CircleCI macOS executors (more expensive than Linux) because tests require Xcode. The test suite includes: 200 unit tests (no Xcode needed), 50 snapshot tests (need Xcode simulator), and 20 UI tests (need full iOS simulator). Design a hybrid pipeline that minimises macOS executor usage while maintaining full test coverage — and calculate the cost reduction assuming macOS credits cost 5x Linux credits.

