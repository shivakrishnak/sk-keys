---
layout: default
title: "CI/CD Pipeline"
parent: "CI/CD"
nav_order: 991
permalink: /ci-cd/ci-cd-pipeline/
---
# 991 — CI/CD Pipeline

`#devops` `#sdlc` `#cicd` `#intermediate`

⚡ TL;DR — An automated pipeline that integrates code changes continuously and deploys them to production reliably and repeatedly.

| #991 | category: CI/CD
|:---|:---|:---|
| **Depends on:** | Version Control, Build Tools, Automated Testing | |
| **Used by:** | Blue-Green Deployment, Canary Deployment, GitOps | |

---

### 📘 Textbook Definition

A CI/CD Pipeline is an automated sequence of stages that transforms source code into a deployed, running application. **CI (Continuous Integration)** automatically builds and tests every code change. **CD (Continuous Delivery/Deployment)** automatically delivers tested code to production or a production-like environment, ensuring software is always in a releasable state.

---

### 🟢 Simple Definition (Easy)

CI/CD is an **automated assembly line for software**. Every time a developer commits code, the pipeline automatically builds it, tests it, and (if everything passes) ships it to production — no manual steps needed.

---

### 🔵 Simple Definition (Elaborated)

Without CI/CD, developers integrate code infrequently, leading to "integration hell" when merging. With CI, every commit triggers an automated build and test run — catching bugs immediately in the context that introduced them. CD extends this by automating the release to staging and production environments, making deployment a routine, low-risk event rather than a stressful manual operation.

---

### 🔩 First Principles Explanation

**The core problem:**
Manual integration and deployment are slow, error-prone, and create long feedback loops. Bugs discovered days later are expensive to fix.

**The insight:**
> "If something is painful, do it more often — until the pain disappears through automation."

```
Without CI/CD:
  Code written --> weeks pass --> big merge --> integration errors
  Manual deploy --> missed steps --> prod broken --> 2am hotfix

With CI/CD:
  Every commit --> automated pipeline --> fast feedback --> confidence
  Deploy is automatic, identical every time --> no surprises
```

---

### ❓ Why Does This Exist (Why Before What)

Without CI/CD, teams avoid deploying frequently because deployments are risky. This creates a vicious cycle: infrequent deploys → large batches of changes → higher risk → even more reluctance to deploy. CI/CD breaks this cycle by making every deploy small and automated.

---

### 🧠 Mental Model / Analogy

> Think of a car assembly line. Each station does one specific job automatically — weld, paint, inspect — in the same order every time. No car leaves the line uninspected. CI/CD is the assembly line for software: build → test → package → deploy, every time, automatically.

---

### ⚙️ How It Works (Mechanism)

```
Typical pipeline stages:

  1. Source    -- developer pushes code to git repo
        ↓
  2. Build     -- compile, package (jar/docker image)
        ↓
  3. Unit Test -- fast, isolated tests (< 5 minutes)
        ↓
  4. Integration Test -- test with real dependencies
        ↓
  5. Static Analysis -- linting, SAST, code quality gates
        ↓
  6. Artifact  -- publish versioned artifact to registry
        ↓
  7. Deploy Staging -- deploy to staging environment
        ↓
  8. Smoke Test -- quick sanity check on staging
        ↓
  9. Deploy Prod -- automated (CD) or manual approval gate (CDelivery)
        ↓
  10. Monitor  -- observe metrics; auto-rollback if threshold breached
```

---

### 🔄 How It Connects (Mini-Map)

```
[Git Push]
    ↓
[CI: Build + Test]  --> FAIL --> notify developer immediately
    ↓ PASS
[CD: Stage --> Prod]
    ↓
[Feature Flags] + [Blue-Green] + [Canary] + [Monitoring]
```

---

### 💻 Code Example

```yaml
# GitHub Actions CI/CD pipeline — .github/workflows/pipeline.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Build & Unit Test
        run: mvn clean verify

      - name: Build Docker Image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Push to Registry
        run: |
          docker tag myapp:${{ github.sha }} registry.io/myapp:${{ github.sha }}
          docker push registry.io/myapp:${{ github.sha }}

  deploy-staging:
    needs: build-and-test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Staging
        run: kubectl set image deployment/myapp myapp=registry.io/myapp:${{ github.sha }}

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production          # requires manual approval
    steps:
      - name: Deploy to Production
        run: kubectl set image deployment/myapp myapp=registry.io/myapp:${{ github.sha }}
```

---

### 🔁 Flow / Lifecycle

```
1. Developer pushes code to feature branch
        ↓
2. CI triggered: build + unit tests (fast feedback, < 10 min)
        ↓
3. Pull request opened → integration tests + code review
        ↓
4. Merge to main → full pipeline triggered
        ↓
5. Deploy to staging → automated acceptance tests
        ↓
6. (Manual approval gate for Continuous Delivery)
   OR  (Automatic for Continuous Deployment)
        ↓
7. Deploy to production
        ↓
8. Monitor: error rate, latency, business metrics
        ↓
9. Auto-rollback if SLO breached
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| CI/CD = just running tests | CI/CD includes build, test, package, security scan, deploy, monitor |
| Continuous Delivery = Continuous Deployment | Delivery requires manual approval; Deployment is fully automatic |
| CI/CD makes deployment risky | Small, frequent deployments are LESS risky than large infrequent ones |
| Only large teams need CI/CD | A solo developer benefits from automated testing and deployment |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Slow Pipeline (> 30 minutes)**
Developers stop waiting for feedback and push more changes, defeating the purpose.
Fix: parallelize test suites; use test containers; separate fast (unit) and slow (integration) stages.

**Pitfall 2: Flaky Tests**
Tests that randomly pass/fail destroy trust in the pipeline.
Fix: quarantine flaky tests; fix or delete them immediately; track flakiness rate as a metric.

**Pitfall 3: No Rollback Strategy**
Deployment succeeds but new version has a bug — no way to revert quickly.
Fix: always keep the previous artifact; automate rollback on SLO breach; use blue-green or canary.

**Pitfall 4: Pipeline as a Bottleneck**
One shared pipeline for all teams creates merge queue congestion.
Fix: trunk-based development with feature flags; independent pipeline per service/team.

---

### 🔗 Related Keywords

- **Blue-Green Deployment** — zero-downtime deployment strategy enabled by CD
- **Canary Deployment** — gradual rollout strategy used in CD
- **GitOps** — extending CD where git state drives infrastructure
- **Feature Flags** — decouple code deployment from feature release within a CD pipeline
- **IaC (Infrastructure as Code)** — provision environments automatically in the pipeline
- **SRE** — defines SLOs that trigger auto-rollback in the CD stage

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Automate the entire path from commit to       │
│              │ production — build, test, deploy, monitor     │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Always — any software project benefits        │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Skipping stages to "go faster" — that defeats │
│              │ the purpose and creates risk                  │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Every commit is a potential release —         │
│              │  the pipeline decides, not a person"          │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Blue-Green --> Canary --> GitOps --> IaC       │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between Continuous Delivery and Continuous Deployment?  
**Q2.** How do you measure the health of a CI/CD pipeline? What metrics matter?  
**Q3.** How do feature flags complement CI/CD when a feature is not yet ready for all users?

