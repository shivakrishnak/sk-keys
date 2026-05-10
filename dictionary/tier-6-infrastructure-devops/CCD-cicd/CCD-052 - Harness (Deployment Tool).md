---
version: 2
layout: default
title: "Harness (Deployment Tool)"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /ci-cd/harness-deployment-tool/
id: CCD-061
category: CI/CD
difficulty: ★★★
depends_on: CI-CD, Continuous Deployment, GitOps
used_by: CI-CD
related: Spinnaker, ArgoCD, Jenkins
tags:
  - cicd
  - devops
  - advanced
---

# CCD-058 - Harness (Deployment Tool)

⚡ **TL;DR -** Harness is an AI-powered software delivery platform that automates deployments, enforces governance gates, and auto-rolls back using live metric verification.

| Field | Value |
|-------|-------|
| **Depends on** | CI-CD, Continuous Deployment, GitOps |
| **Used by** | CI-CD |
| **Related** | Spinnaker, ArgoCD, Jenkins |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Teams deploy by SSHing into servers, running custom Bash scripts, and watching Grafana dashboards manually. Each environment is a snowflake. A failed deployment means engineers scramble through logs at 2 AM with no automated rollback path.

**THE BREAKING POINT:** As microservice counts grow and deployment frequency rises, manual handoffs collapse. A canary deployment requires monitoring 20 metrics, writing bespoke glue scripts, and hoping an engineer notices degradation before 100% traffic shifts. This does not scale beyond a handful of services.

**THE INVENTION MOMENT:** Harness was built to codify the entire delivery pipeline as a first-class, versioned object - with governance gates, metric-based verification, and ML-powered rollback - so engineers define delivery policy rather than maintain deployment scripts.

---

### 📘 Textbook Definition

**Harness** is a commercial Software Delivery Platform that models deployments as pipelines of Stages and Steps, supports multiple deployment strategies (blue-green, canary, rolling), integrates with observability providers for **Continuous Verification (CV)**, and applies machine-learning baselines to automatically promote or roll back each deployment based on real-time service health signals.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Harness turns deployment into a governed, observable, self-healing pipeline instead of a shell script.

> Think of Harness as an airport control tower: it coordinates every flight (deployment), enforces separation rules (governance gates), monitors radar (metrics verification), and automatically diverts planes that go off course (auto-rollback).

**One insight:** The critical innovation is **Continuous Verification** - Harness queries your APM (Datadog, New Relic, Prometheus) during a canary phase and applies ML baselines to decide automatically whether to promote or roll back, removing humans from the critical decision path.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A deployment is a state transition from version N to version N+1 across an environment.
2. That transition can fail at infrastructure, application, or behavioral layers.
3. The only reliable safety net is observable signals compared against a known-good baseline.
4. Human vigilance does not scale; policy and automation must replace ad-hoc decision-making.

**DERIVED DESIGN:** Harness models the delivery process as a directed graph of Stages (phases) containing Steps (atomic actions). Governance is layered as approval gates between stages. Verification is a CV step that polls metrics and computes a risk score against a historical baseline window.

**THE TRADE-OFFS:**
**Gain:** Deployment safety, speed, and auditability at scale - teams deploy 10× faster with fewer production incidents.
**Cost:** Harness is a complex platform requiring instrumented services (metrics, logs) to deliver verification value. The enterprise feature tier carries significant licensing cost.

---

### 🧪 Thought Experiment

**SETUP:** You run 50 microservices. Each has a deployment pipeline built from Bash + Jenkins + manual Slack approvals. A canary deployment means shifting 10% traffic and watching a Grafana dashboard for 30 minutes.

**WHAT HAPPENS WITHOUT HARNESS:** The on-call engineer watches the dashboard manually. They get distracted. A memory leak in the new version spikes p99 latency - but the alert fires 15 minutes too late. 100% traffic has already shifted. A full incident is declared.

**WHAT HAPPENS WITH HARNESS:** A Continuous Verification step automatically queries Datadog during the 10% canary window. The ML baseline detects p99 latency is 3σ above normal. Harness auto-rolls back within 4 minutes, pages the engineer with annotated metric diffs, and writes a full audit log of the failed run.

**THE INSIGHT:** The value of Harness is not automating the happy path - Jenkins already does that. The value is automated **failure detection and recovery** on the unhappy path, before damage reaches users at scale.

---

### 🧠 Mental Model / Analogy

> Think of Harness as a **smart assembly line with quality-control checkpoints**. Each station (Stage) does work. Between stations, quality inspectors (Verification steps) measure output against specification. If a part fails inspection, the line stops and reverses automatically.

- Assembly line = the Harness Pipeline
- Stations = Stages (Deploy, Verify, Approve)
- Atomic operations = Steps within each stage
- Quality inspectors = Continuous Verification steps
- Specification sheets = governance policies and approval gates
- Auto-reverse = AI-powered rollback to previous version

Where this analogy breaks down: A factory line processes identical parts; Harness pipelines handle heterogeneous services with different SLOs, making baseline comparison fundamentally more complex.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Harness is a tool that automatically deploys your software to production, watches whether it's working correctly, and rolls it back if something goes wrong - without requiring humans to watch dashboards overnight.

**Level 2 - How to use it (junior developer):**
You define a Pipeline with Stages. A Deploy Stage targets an environment using a strategy like canary. You add a Verify step pointing to your Datadog connector and define a Service Level Indicator (e.g., error rate < 1%). Harness runs the canary, queries Datadog, and either promotes or rolls back automatically based on the ML risk score.

**Level 3 - How it works (mid-level engineer):**
Harness uses a delegate model: a lightweight agent (the Harness Delegate) runs inside your infrastructure and executes pipeline steps against your Kubernetes cluster or cloud provider. Pipelines are YAML-defined and version-controlled. CV steps invoke the Harness ML service, which builds a baseline from historical metric windows and computes an anomaly risk score (0–100). Scores above threshold trigger automatic rollback.

**Level 4 - Why it was designed this way (senior/staff):**
The Delegate pattern solves a fundamental enterprise security problem: the Harness control plane never needs direct inbound access to your infrastructure - all connectivity is outbound from the Delegate. The CV ML model was designed to eliminate false positives from deployment-correlated metric changes (e.g., latency always spikes during canary warm-up). It uses the canary period itself as a calibration window, comparing against the equivalent prior historical window rather than a static threshold. This is the key algorithmic innovation that separates Harness CV from naive alert-based rollback systems.

---

### ⚙️ How It Works (Mechanism)

Harness executes pipelines through the **Delegate** model:

```
┌─────────────────────────────────────────┐
│         Harness Control Plane           │
│  Pipeline │ Stage │ Step execution      │
│  CV ML Service │ Governance Engine      │
└────────────┬────────────────────────────┘
             │ outbound HTTPS only
             ▼
┌─────────────────────────────────────────┐
│      Harness Delegate (your VPC)        │
│  Runs: kubectl, helm, terraform         │
│  Queries: Datadog, Prometheus, NR       │
│  Reports results → control plane        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        Your Infrastructure              │
│  K8s cluster / ECS / Lambda / VMs       │
└─────────────────────────────────────────┘
```

**Pipeline execution sequence:**
1. Trigger (webhook, schedule, API) starts a Pipeline run
2. Stages execute sequentially or in parallel as configured
3. Deploy Stage: Delegate runs Helm/kubectl against target env
4. Verify Stage: CV step queries APM; ML scores risk (0–100)
5. Approval Stage (optional): human sign-off before prod
6. Rollback: auto on CV failure or triggered manually

**Key concepts:** `Service` (what), `Environment` (where), `Infrastructure Definition` (how), `Pipeline` (sequence), `Delegate` (executor).

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Code Push
    │
    ▼
CI Pipeline (build + push image)
    │
    ▼ artifact: myapp:v2.1.0
Harness Trigger ← YOU ARE HERE
    │
    ▼
Deploy Stage: canary 10% traffic
    │
    ▼
Verify Stage: CV queries Datadog 10 min
    │  ML risk score < 30 → healthy
    ▼
Promote Stage: shift to 100% traffic
    │
    ▼
Approval Gate: manual or auto
    │
    ▼
Deploy to Production (rolling)
    │
    ▼
Post-deploy Verify: monitor 15 min
    │
    ▼
Pipeline Complete - audit log written
```

**FAILURE PATH:**
```
Verify Stage: ML risk score > 75
    │  anomaly detected in p99 latency
    ▼
Auto-rollback: myapp:v2.0.9 redeployed
    │
    ▼
Alert fired + audit log entry created
    │
    ▼
Failed run retained for root-cause analysis
```

**WHAT CHANGES AT SCALE:**
At high scale, governance gates become mandatory - multi-approver chains, JIRA-linked change tickets, deploy freeze windows. Pipeline Templates let platform teams define golden paths that product teams instantiate. OPA policies enforce compliance rules across all pipelines centrally. Delegate pooling distributes execution load across multiple agents.

---

### 💻 Code Example

**BAD - manual canary with no verification:**
```bash
# No CV, no rollback, pure hope-driven deployment
kubectl set image deploy/api api=myapp:v2
sleep 600
# manually check Grafana, then:
kubectl set image deploy/api api=myapp:v2
```

**GOOD - Harness Pipeline YAML (abbreviated):**
```yaml
pipeline:
  name: deploy-api
  stages:
    - stage:
        name: Deploy Canary
        type: Deployment
        spec:
          deploymentType: Kubernetes
          service: api-service
          environment: staging
          execution:
            steps:
              - step:
                  type: K8sCanaryDeploy
                  spec:
                    instanceSelection:
                      type: Count
                      spec:
                        count: 1
    - stage:
        name: Verify
        type: Verify
        spec:
          type: Canary
          spec:
            monitoredService:
              type: Default
            healthSources:
              - identifier: datadog_connector
            duration: 10m
            sensitivity: MEDIUM
    - stage:
        name: Promote
        type: Deployment
        spec:
          execution:
            steps:
              - step:
                  type: K8sCanaryDelete
              - step:
                  type: K8sRollingDeploy
```

---

### ⚖️ Comparison Table

| Feature | Harness | Spinnaker | ArgoCD | Jenkins |
|---------|---------|-----------|--------|---------|
| **Deployment model** | Pipeline-first | Pipeline-first | GitOps pull | Script-based |
| **Continuous Verification** | ML-native | Plugin only | None | None |
| **Governance gates** | Built-in | Basic | OPA plugin | Manual |
| **AI/ML rollback** | Yes (core feature) | No | No | No |
| **Kubernetes native** | Yes | Yes | Primary focus | Plugin |
| **Hosting** | SaaS + self-hosted | Self-hosted only | Self-hosted | Self-hosted |
| **Learning curve** | High | Very high | Medium | Medium |
| **Cost** | $$$ (enterprise) | Free (ops burden) | Free | Free |
| **Audit trail** | Enterprise-grade | Basic | Git history | Build logs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Harness is a CI tool like Jenkins" | Harness is a CD platform. It handles deployment, verification, and governance - not source compilation. Most teams use Jenkins or GitHub Actions for CI and Harness for CD. |
| "Harness replaces ArgoCD" | They are complementary. Harness excels at multi-cloud CD with ML verification; ArgoCD excels at GitOps-native Kubernetes sync. Many enterprises run both. |
| "CV requires Harness-specific instrumentation" | CV uses standard APM connectors (Datadog, New Relic, Prometheus, AppDynamics). No Harness SDK is needed in your application. |
| "Auto-rollback guarantees zero downside" | Rollback restores the previous container image but cannot undo side effects: database migrations, events published, or external API calls made during the failed deployment. |
| "Harness only supports Kubernetes" | Harness supports ECS, Lambda, Helm, VM-based, and multi-cloud deployments in addition to Kubernetes. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: CV false positive rolls back healthy deployments**
**Symptom:** Engineers lose trust in CV; healthy canaries are routinely rolled back.
**Root Cause:** The baseline window includes a previous deployment spike; the ML model treats inflated latency as "normal," causing healthy traffic to score as anomalous.
**Diagnostic:**
```bash
# Inspect CV risk breakdown via Harness API
curl -s -H "x-api-key: $HARNESS_API_KEY" \
  "https://app.harness.io/cv/api/verify-step/\
${VERIFY_STEP_ID}/logs" | jq '.data.logRecords'
```
**Fix:**
BAD - Disable CV entirely to stop false positives.
GOOD - Tune the baseline window to exclude deploy spikes; use ≥7-day baseline; add metric exclusion filters for warmup noise.
**Prevention:** Run at least 2 weeks of steady-state traffic before enabling CV. Start with `sensitivity: LOW`.

**Failure Mode 2: Delegate connectivity loss hangs pipelines**
**Symptom:** Pipeline steps hang indefinitely with "No eligible delegates found."
**Root Cause:** Delegate pod evicted, crashed, or outbound HTTPS to `app.harness.io` blocked by network policy change.
**Diagnostic:**
```bash
kubectl get pods -n harness-delegate
kubectl logs -n harness-delegate \
  $(kubectl get pods -n harness-delegate \
  -o name | head -1) --tail=50
# Check last heartbeat in Harness UI:
# Settings → Delegates → [name] → heartbeat
```
**Fix:**
BAD - Restart the pipeline and hope the delegate recovers.
GOOD - Fix root cause (network policy, resource limits, image pull); verify `app.harness.io:443` egress; re-register if certificate expired.
**Prevention:** Run ≥2 Delegate replicas with pod anti-affinity. Enable auto-upgrade. Alert on delegate heartbeat gap > 5 minutes.

**Failure Mode 3: Approval gate blocks urgent hotfix**
**Symptom:** P0 hotfix pipeline blocks in approval stage; approvers unreachable.
**Root Cause:** Approval step has no timeout and no bypass group defined.
**Diagnostic:**
```bash
curl -s -H "x-api-key: $HARNESS_API_KEY" \
  "https://app.harness.io/pipeline/api/approvals/\
aggregate?accountId=${ACCOUNT_ID}" \
  | jq '.data[] | select(.status=="WAITING")'
```
**Fix:**
BAD - Remove all approval gates to unblock hotfixes.
GOOD - Add a `timeoutAction: AUTO_APPROVE` with a 15-minute timeout for hotfix pipelines; define a break-glass bypass user group for P0 incidents.
**Prevention:** Model approval gates by change risk tier. Hotfixes: 15-min timeout + auto-approve. Major releases: 2-approver requirement with no bypass.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- CI-CD - the foundational concept Harness implements as a platform
- Continuous Deployment - the automated delivery model Harness operationalises
- GitOps - the source-of-truth model Harness integrates with for artifact sourcing

**Builds On This (learn these next):**
- Spinnaker - open-source CD predecessor Harness was designed to supersede
- ArgoCD - complementary GitOps tool frequently paired with Harness
- Open Policy Agent (OPA) - used for centralised governance policy in Harness pipelines

**Alternatives / Comparisons:**
- Jenkins - CI-focused; requires heavy plugin work for production-grade CD
- Spinnaker - open-source CD, higher operational burden, no ML verification
- ArgoCD - GitOps-native K8s CD, no built-in ML-based health verification

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS     │ AI-powered CD delivery platform   │
│ PROBLEM        │ Manual, unverified deployments    │
│ KEY INSIGHT    │ ML CV = automated risk scoring    │
│ USE WHEN       │ Multi-env CD with governance      │
│ AVOID WHEN     │ Simple single-service CI-only     │
│ TRADE-OFF      │ Safety + speed vs cost + setup    │
│ ONE-LINER      │ Deploy → CV verify → auto-rollback│
│ NEXT EXPLORE   │ Spinnaker, ArgoCD, OPA            │
└────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Scale)** With 200 microservices each owning a Harness pipeline, how do you prevent pipeline configuration drift - and which Harness primitives (Templates, Pipeline Chaining, Input Sets) address this at platform scale?

2. **(Design Trade-off)** Harness CV uses your own canary window as part of the baseline comparison. What class of failure does this approach miss that a static error-budget threshold would catch immediately?

3. **(System Interaction)** When Harness auto-rolls back a deployment that already executed a non-reversible database migration, what is the resulting system state - and what contract must exist between your migration strategy and your rollback strategy to handle this safely?
