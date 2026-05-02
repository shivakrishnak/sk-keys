---
layout: default
title: "ArgoCD"
parent: "CI/CD"
nav_order: 1004
permalink: /ci-cd/argocd/
number: "1004"
category: CI/CD
difficulty: ★★★
depends_on: Kubernetes, GitOps, Continuous Delivery
used_by: Progressive Delivery, Continuous Deployment, Rollback Strategy
related: Flux, Tekton, GitOps
tags:
  - cicd
  - kubernetes
  - devops
  - advanced
  - gitops
---

# 1004 — ArgoCD

⚡ TL;DR — ArgoCD is a Kubernetes-native GitOps continuous delivery tool that continuously reconciles cluster state with the desired state declared in Git, automatically deploying any drift.

| #1004 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Kubernetes, GitOps, Continuous Delivery | |
| **Used by:** | Progressive Delivery, Continuous Deployment, Rollback Strategy | |
| **Related:** | Flux, Tekton, GitOps | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team runs `kubectl apply` or `helm upgrade` from CI pipelines to deploy to Kubernetes. Over time: an engineer directly patches a deployment in production to fix an urgent bug (bypassing the pipeline). A Kubernetes upgrade silently changes a default setting. A ConfigMap is manually edited in staging but not committed to Git. Three months later, nobody knows what's actually running in production — the cluster state has drifted from the Git-defined state. Deploying becomes risky because the delta between "what Git says" and "what's running" is unknown.

**THE BREAKING POINT:**
Imperative deployments (CI runs `kubectl apply`) have no drift detection, no audit trail of who changed what directly in the cluster, and no automatic reconciliation. The cluster is a stateful system that gradually diverges from its intended configuration.

**THE INVENTION MOMENT:**
This is exactly why ArgoCD was created: continuously compare the desired state (Git) with the actual state (cluster), automatically sync any divergence, and make every cluster change traceable to a Git commit.

---

### 📘 Textbook Definition

**ArgoCD** is a declarative, GitOps-based continuous delivery tool for Kubernetes. It watches specified Git repositories for changes to Kubernetes manifests (plain YAML, Helm charts, Kustomize overlays, or Jsonnet). When the desired state in Git changes, or when the cluster drifts from the desired state, ArgoCD can automatically or manually sync — reconciling the cluster to match Git. ArgoCD runs as a set of Kubernetes controllers in the target cluster. It provides a web UI, CLI (`argocd`), and REST API. Access is managed via SSO, RBAC policies, and project-level constraints on source repos and destination clusters.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ArgoCD watches Git and keeps your Kubernetes cluster matching what Git says — always.

**One analogy:**
> ArgoCD is like a vigilant quality control inspector on a production line. The engineering blueprints (Git) define exactly what each product should look like. The inspector (ArgoCD) continuously checks every product on the line (cluster resources) against the blueprint. If a product deviates, the inspector immediately corrects it or alerts, and logs the deviation with a timestamp.

**One insight:**
ArgoCD's core insight: **Git is the only source of truth**. Manual `kubectl edit` is an anti-pattern that ArgoCD directly opposes. When ArgoCD is in auto-sync mode, manually applied changes are automatically reverted. This is not a bug — it's the point: the cluster's state is immutably defined by Git history.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Desired state lives in Git — never in the cluster, never in CI pipeline scripts.
2. The cluster is continuously compared against Git state; divergence triggers reconciliation.
3. Every deployment traces back to a Git commit — full audit trail by design.
4. ArgoCD never touches source code — it is a pure deployment tool, not CI.

**DERIVED DESIGN:**
ArgoCD's reconciliation loop polls Git (default: 3 minutes) or receives webhooks from GitHub/GitLab. When a diff is detected, ArgoCD computes the delta between desired and actual resources and either syncs automatically (auto-sync enabled) or marks the app as "OutOfSync" (manual sync required). Sync operations use server-side apply or client-side apply depending on configuration.

RBAC is split between ArgoCD RBAC (who can sync/delete AppProject-scoped applications) and Kubernetes RBAC (what ArgoCD's service account can do in the target cluster). The `AppProject` CRD enforces source repository restrictions, destination namespace whitelisting, and cluster resource allow-lists.

**THE TRADE-OFFS:**
**Gain:** Drift detection, automatic reconciliation, Git-based audit trail, rollback by reverting a Git commit.
**Cost:** Requires a Git repository per environment (or branches per environment). Operators must understand Git merge/revert as deployment mechanisms. Auto-sync can revert emergency hot-patches — requires deliberate process for urgent fixes. Multi-cluster management adds complexity.

---

### 🧪 Thought Experiment

**SETUP:**
Production has a bug in `Deployment/payment-service`. An engineer manually edits it with `kubectl edit` at 2 AM — changing the replica count does nothing, but they also change an env variable that fixes the bug.

**WHAT HAPPENS WITHOUT ARGOCD:**
The fix works. The deployment shows the fix. But Git still has the old env variable. Next time someone runs the pipeline or applies the Helm chart, the fix is overwritten. The bug returns in production. The 2 AM fix is lost. No one knows what changed between the broken state and the fixed state.

**WHAT HAPPENS WITH ARGOCD (auto-sync):**
The engineer edits the deployment. Within 3 minutes, ArgoCD detects drift. Auto-sync reverts the change. The bug returns. But: the engineer now knows the right way — commit the fix to Git. The commit is reviewed, merged, ArgoCD syncs it. The fix is permanent, traceable, and permanent.

**THE INSIGHT:**
ArgoCD's auto-revert feels hostile to operators used to direct kubectl access. But it enforces a discipline that makes production auditable. The emergency fix that "sticks" is always the one in Git.

---

### 🧠 Mental Model / Analogy

> ArgoCD is like a building's master blueprint system with a lock-state enforcer. The architect's blueprints (Git) define exactly what's in the building. A custodian (engineer) moves a wall manually — the lock-state enforcer (ArgoCD) immediately detects the change in the blueprint scanner, compares it to the blueprint, and restores the original wall configuration. If you want to move the wall permanently, update the blueprint.

- "Architect's blueprints" → Kubernetes manifests in Git
- "Building's actual state" → running cluster resources
- "Blueprint scanner" → ArgoCD's comparison engine
- "Lock-state enforcer" → ArgoCD auto-sync
- "Restoring the wall" → ArgoCD sync reverts manual cluster changes

Where this analogy breaks down: in real buildings, maintaining blueprint fidelity might prevent emergency repairs. ArgoCD's solution is `argocd app set --self-heal false` + sync windows — allowing brief periods of deliberate drift for emergencies while preserving the Git-as-truth model.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
ArgoCD watches a folder on GitHub. When you change files there (like "deploy 3 copies of this service"), ArgoCD automatically changes your Kubernetes cluster to match. If someone manually changes the cluster without updating GitHub, ArgoCD changes it back. GitHub is always right.

**Level 2 — How to use it (junior developer):**
Install ArgoCD in your cluster. Create an `Application` resource specifying: source (Git repo URL + path + branch), destination (cluster + namespace), and sync policy (manual or auto). Use the ArgoCD UI to see sync status, diffs between Git and cluster, and sync history. Use `argocd app sync myapp` to manually trigger a sync. Use `argocd rollout` for rollback — or just `git revert` the breaking commit and let ArgoCD auto-sync.

**Level 3 — How it works (mid-level engineer):**
ArgoCD's `application-controller` computes the diff between the desired state (generated by hydrating the source — plain YAML, Helm template execution, Kustomize build) and the live state (current cluster resources). The comparison is resource-by-resource — ArgoCD knows which fields are ArgoCD-managed vs externally-managed (e.g., HPA sets `replicas` — ArgoCD ignores that field if `ignoreDifferences` is configured for it). Sync operations use `kubectl apply` (server-side or client-side). Resource ordering is controlled by sync waves (annotations) and sync phases.

**Level 4 — Why it was designed this way (senior/staff):**
ArgoCD's controller-per-cluster architecture (one ArgoCD per cluster, or hub-and-spoke with ArgoCD managing remote clusters via kubeconfig) was a deliberate security decision — the blast radius of compromised ArgoCD credentials is limited to the managed cluster's access. The ApplicationSet controller (v2.0+) generalised the multi-cluster problem: a single ApplicationSet definition can generate Applications for all clusters matching a generator (list, cluster, git directory). This solved the scaling problem of managing 50+ clusters without 50 Application CRDs. The design debate continues: "app of apps" (Applications that deploy Application CRDs) vs ApplicationSet is an ongoing architectural tension in the ArgoCD community.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│         ARGOCD RECONCILIATION LOOP          │
├─────────────────────────────────────────────┤
│  1. DESIRED STATE: fetch from Git           │
│     - git clone app-config-repo             │
│     - helm template values/ (if Helm)       │
│     - kustomize build (if Kustomize)        │
│     → Set of Kubernetes manifest objects    │
│                                             │
│  2. ACTUAL STATE: query Kubernetes API      │
│     - kubectl get all -n production         │
│     → Set of running Kubernetes objects     │
│                                             │
│  3. DIFF: compare desired vs actual         │
│     - Deployment replicas: 3 vs 3 ✓         │
│     - Deployment image: v1.2 vs v1.1 ✗ DRIFT│
│     - ConfigMap data: matches ✓             │
│                                             │
│  4. STATUS: Synced / OutOfSync              │
│     If auto-sync enabled:                   │
│     → kubectl apply updated Deployment      │
│     → Cluster reconciled                    │
│     If manual:                              │
│     → Alert: "App OutOfSync" in UI          │
└─────────────────────────────────────────────┘
```

**Application CRD:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service
  namespace: argocd
spec:
  project: production-apps  # AppProject restricting access
  source:
    repoURL: https://github.com/myorg/k8s-config
    targetRevision: HEAD
    path: services/payment-service
    helm:
      releaseName: payment
      valueFiles:
        - values-production.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # delete resources removed from Git
      selfHeal: true   # revert manual cluster changes
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

**Sync waves** for ordered deployment:
```yaml
# ArgoCD deploys resources in wave order (lowest first)
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"  # DB migration Job: first
    # Default wave: "0" (most resources)
    # Wave "1": deploy after wave 0 is healthy
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer merges PR: bump image tag in values.yaml
  → Git commit SHA: abc123
  → ArgoCD polls Git (or receives webhook)
  → Desired state: payment-service image v1.3
  → Actual state: payment-service image v1.2
  → DIFF DETECTED: OutOfSync [← YOU ARE HERE]
  → Auto-sync: kubectl apply Deployment
  → Kubernetes rolls out new pods (rolling update)
  → ArgoCD watches: rollout health check
  → All pods running v1.3 → health: Healthy
  → App status: Synced + Healthy
  → Slack: "payment-service synced to abc123"
```

**FAILURE PATH:**
```
New pods crash (CrashLoopBackOff)
  → ArgoCD health check: Degraded
  → Auto-sync: will not apply further
  → Alert: "payment-service Degraded"
  → Dev: git revert abc123 → new commit def456
  → ArgoCD detects new desired state (v1.2 image)
  → Sync: rolls back to v1.2 automatically
  → Status: Healthy (rollback via Git)
```

**WHAT CHANGES AT SCALE:**
At 200+ clusters, ArgoCD's hub-and-spoke model uses a central ArgoCD instance managing remote clusters via kubeconfig secrets. ApplicationSet controllers generate Applications for all clusters dynamically. Sync performance becomes critical — ArgoCD's application-controller has a sync rate limit. Sharding (multiple application-controller replicas, each owning a subset of Applications) is required above ~1000 managed applications.

---

### 💻 Code Example

**Example 1 — ApplicationSet for multi-environment deployment:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: payment-service-envs
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - env: staging
            cluster: https://staging-k8s.internal
          - env: production
            cluster: https://prod-k8s.internal
  template:
    metadata:
      name: "payment-service-{{env}}"
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/k8s-config
        path: "services/payment/{{env}}"
        targetRevision: HEAD
      destination:
        server: "{{cluster}}"
        namespace: payment
      syncPolicy:
        automated:
          prune: true
          selfHeal: "{{env == \"staging\"}}"  # no auto-heal in prod
```

**Example 2 — Progressive delivery with Argo Rollouts:**
```yaml
# Argo Rollouts (separate CRD) for canary
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-service
spec:
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: { duration: 5m }
        - analysis:
            templates:
              - templateName: error-rate-check
        - setWeight: 100
  selector:
    matchLabels:
      app: payment-service
  template:
    # ... pod template
```

---

### ⚖️ Comparison Table

| Tool | GitOps Model | Multi-Cluster | UI | Deployment Strategies | Best For |
|---|---|---|---|---|---|
| **ArgoCD** | Pull (cluster pulls from Git) | Yes (hub-spoke) | Rich web UI | Rollouts (canary/blue-green) | Kubernetes CD, GitOps |
| Flux | Pull | Yes (multi-tenant) | Minimal | Basic rolling | K8s CD, multi-tenant |
| Jenkins X | Pull + pipeline | Yes | Moderate | Basic | Opinionated K8s CI/CD |
| Spinnaker | Push + pipeline | Yes | Complex | All strategies | Multi-cloud CD, large orgs |

How to choose: Use ArgoCD for Kubernetes GitOps CD with a strong UI and progressive delivery via Argo Rollouts. Use Flux for pure GitOps with multi-tenant isolation. Combine with Tekton (CI) for a complete Kubernetes-native CI/CD platform.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ArgoCD is a CI tool | ArgoCD is purely CD — it deploys pre-built artifacts. It does not build, test, or compile code. CI (building images) must be handled by GitHub Actions, Tekton, or Jenkins |
| Rolling back with ArgoCD requires a special rollback command | The correct rollback is `git revert` — creating a new commit that undoes the breaking change, which ArgoCD syncs automatically. `argocd app rollback` reverts to a previous revision without a Git commit — useful for emergencies but creates Git vs cluster drift |
| Auto-sync makes manual hot-patches impossible | Auto-sync can be temporarily disabled with a sync window pause. Or use `argocd.argoproj.io/compare-options: IgnoreExtraneous` annotation on resources that need emergency patching |
| ArgoCD manages secrets directly | ArgoCD syncs Kubernetes Secrets, but for GitOps, secrets should not be stored in Git as plaintext. Use Sealed Secrets, External Secrets Operator, or Vault agent to manage secrets in a GitOps-compatible way |

---

### 🚨 Failure Modes & Diagnosis

**1. App Stuck in "Progressing" — Rollout Never Completes**

**Symptom:** ArgoCD shows app as `Progressing` for 30+ minutes. Pods are not rolling out. No errors visible.

**Root Cause:** Kubernetes rolling update stalled because new pods fail readiness probes. Old pods are not terminated because the rolling update strategy requires N healthy new pods before terminating old ones.

**Diagnostic:**
```bash
# Check pod readiness
kubectl get pods -n production -l app=payment-service
# Check failing pod logs
kubectl logs -n production \
  deployment/payment-service --previous
# Check readiness probe configuration
kubectl describe deployment payment-service -n production \
  | grep -A10 "Readiness"
```

**Fix:** Fix the readiness probe failure (usually a health check endpoint returning 500). Or update the image to fix the startup bug. Or configure a readiness probe timeout.

**Prevention:** Test readiness probes in staging before production deployment. Set appropriate `failureThreshold` to avoid premature failure marking.

---

**2. Manual Cluster Changes Immediately Reverted**

**Symptom:** Operations engineer patches a ConfigMap in production for an urgent fix. ArgoCD reverts it 3 minutes later. Fix is lost.

**Root Cause:** `selfHeal: true` in auto-sync policy means any manual change is automatically reverted.

**Diagnostic:**
```bash
# Check sync history to confirm revert
argocd app history payment-service
# Check what triggered the sync
argocd app get payment-service -o yaml \
  | grep -A10 "lastSyncResult"
```

**Fix (process):** Commit the fix to Git immediately. Use `argocd app set payment-service --sync-policy none` temporarily during the emergency window.

**Prevention:** Define a runbook for emergency direct patching: (1) pause self-heal, (2) apply fix, (3) commit to Git, (4) verify ArgoCD syncs the Git version, (5) re-enable self-heal.

---

**3. Sync Fails Due to Helm Rendering Error**

**Symptom:** Git commit was merged. ArgoCD shows `OutOfSync` but every sync attempt fails: "helm template failed: error rendering chart."

**Root Cause:** A values.yaml change introduced an invalid Helm value (missing required field, type error). The chart renders successfully locally but fails in ArgoCD's server-side rendering with different Helm value resolution.

**Diagnostic:**
```bash
# Preview what ArgoCD would apply (without syncing)
argocd app diff payment-service
# Or render the manifest directly
argocd app manifests payment-service

# Run helm template directly with ArgoCD's values
helm template payment ./charts/payment \
  -f values-production.yaml
```

**Fix:** Fix the invalid value in the values file. Commit and push. ArgoCD picks up the correction.

**Prevention:** Add a CI step that runs `helm template` against production values before merging to the config repo. Catch Helm rendering errors before they reach ArgoCD.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Kubernetes` — ArgoCD runs as Kubernetes controllers; deep K8s understanding is required
- `GitOps` — ArgoCD is an implementation of GitOps; the principle must be understood first
- `Continuous Delivery` — ArgoCD automates the deployment stages of CD; understanding CD pipeline structure is foundational

**Builds On This (learn these next):**
- `Progressive Delivery` — Argo Rollouts (companion project) adds canary and blue/green deployment strategies on top of ArgoCD
- `Canary Analysis` — analysis templates in Argo Rollouts evaluate traffic metrics to determine whether to promote or roll back
- `GitOps` — ArgoCD is a GitOps tool; understanding GitOps principles deepens ArgoCD usage

**Alternatives / Comparisons:**
- `Flux` — alternative GitOps CD tool with stronger multi-tenant support and a simpler architecture
- `Tekton` — handles CI (build), while ArgoCD handles CD (deploy) — they complement rather than compete
- `Spinnaker` — a more complex CD platform with broader multi-cloud support and manual approval pipelines

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ GitOps CD: continuously syncs Kubernetes  │
│              │ cluster to desired state declared in Git  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Cluster drift: `kubectl edit` in prod,    │
│ SOLVES       │ no audit trail, no automatic reconciliation│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Rollback = `git revert`. Git is the only  │
│              │ source of truth — not the cluster         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Kubernetes deployments where auditability,│
│              │ drift detection, and GitOps matter        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Non-Kubernetes deployments; teams not     │
│              │ ready to adopt Git-as-truth discipline    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Git-enforced auditability vs loss of      │
│              │ direct kubectl emergency access           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "kubectl apply from Git, forever — the    │
│              │  cluster is always what Git says"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Argo Rollouts → Progressive Delivery      │
│              │ → Canary Analysis → DORA Metrics          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team deploys a Kubernetes Secret via ArgoCD that contains a database password. For GitOps compliance, the secret must be in Git. But storing plaintext secrets in Git is a critical security violation. Three engineers propose different solutions: (A) Sealed Secrets (encrypts with the cluster's public key), (B) External Secrets Operator (fetches from AWS Secrets Manager), (C) Vault Agent Injector (injects at pod startup). How does each solution interact with ArgoCD's sync model, and what are the specific failure modes of each that could leave pods without secrets?

**Q2.** Your ArgoCD manages 150 Applications across 5 clusters. A new security requirement mandates that all cluster changes in production must have a second human reviewer as evidence, even for ArgoCD auto-sync operations. How would you design an ArgoCD architecture that:  (1) maintains auto-sync for non-production environments, (2) requires manual approval for production syncs, (3) provides a Git-traceable audit trail, while (4) still allowing rapid emergency deploys when needed?

