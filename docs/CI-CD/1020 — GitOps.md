---
layout: default
title: "GitOps"
parent: "CI/CD"
nav_order: 1020
permalink: /ci-cd/gitops/
number: "1020"
category: CI/CD
difficulty: ★★★
depends_on: Git, Kubernetes, Infrastructure as Code, CI/CD Pipeline
used_by: ArgoCD, Environment Promotion, Deployment Pipeline, Progressive Delivery
related: ArgoCD, Flux, Terraform, Deployment Pipeline, Environment Promotion
tags:
  - cicd
  - devops
  - kubernetes
  - deep-dive
  - pattern
---

# 1020 — GitOps

⚡ TL;DR — GitOps uses Git as the single source of truth for infrastructure and application state, with automated agents continuously reconciling running systems to match what's declared in Git.

| #1020 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Git, Kubernetes, Infrastructure as Code, CI/CD Pipeline | |
| **Used by:** | ArgoCD, Environment Promotion, Deployment Pipeline, Progressive Delivery | |
| **Related:** | ArgoCD, Flux, Terraform, Deployment Pipeline, Environment Promotion | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A CI system has `kubectl apply -f manifest.yaml` in its pipeline. It deploys to production when code is merged to main. Six months in, an operator SSH-es into the cluster and manually patches a `ConfigMap` to fix an urgent configuration issue. Three weeks later, the CI pipeline runs again and overwrites the manual fix — silently. A developer manually scales a deployment from 3 replicas to 10 to handle traffic. The next morning, CI reverts it to 3. An on-call engineer removes a canary deployment that was misbehaving using `kubectl delete`. Two days later, no one can answer "what is the intended state of production, and where is it defined?"

**THE BREAKING POINT:**
Push-based CI/CD (CI pushes deployments to clusters) creates an invisible authority problem: the cluster's actual state is the product of CI deployments, manual changes, autoscaler actions, and operator interventions — none of which have a single, auditable, canonical record. Drift is invisible until it causes an incident.

**THE INVENTION MOMENT:**
This is exactly why GitOps was created: make Git the unambiguous single source of truth. Every change to infrastructure or application state must be a Git commit. An automated agent continuously watches Git and reconciles the cluster to match — making manual drift impossible to sustain and every change permanently auditable.

---

### 📘 Textbook Definition

**GitOps** is an operational framework that uses Git repositories as the single source of truth for both application code and infrastructure configuration, with automated agents (ArgoCD, Flux) continuously reconciling the running state of systems (Kubernetes clusters, infrastructure) to match the desired state declared in Git. GitOps has four principles (OpenGitOps standard): (1) declarative — desired system state described declaratively; (2) versioned and immutable — desired state stored in Git with full history; (3) pulled automatically — software agents retrieve and apply desired state continuously; (4) continuously reconciled — agents detect drift and self-heal. GitOps inverts the traditional CI/CD push model: instead of CI pipelines pushing deployments directly, CI updates Git, and cluster agents pull the desired state from Git and apply it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Git is the boss — what's in Git defines what runs, and the system automatically stays in sync with Git.

**One analogy:**
> GitOps is like a self-maintaining garden with a blueprint. The blueprint (Git repository) specifies exactly which plants go where. A team of gardeners (ArgoCD agents) periodically walks the garden, compares it to the blueprint, and removes weeds or replants what's missing. If a visitor moves a plant to a different spot, the gardeners put it back where the blueprint says it should be at the next patrol. The blueprint is authoritative — the garden always converges back to the blueprint.

**One insight:**
The inversion from push to pull is GitOps' most consequential design decision. In push-based CD, the CI server must have credentials to push deployments to clusters — creating a high-value attack target. In pull-based GitOps, the cluster agent reads from Git (read-only access to a public or private repo) — the CI server never has cluster credentials. The blast radius of a compromised CI server is dramatically reduced: it can only modify Git (where every change is auditable) not directly push arbitrary manifests to production.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The desired state of a system is a well-specified document — not a sequence of past commands.
2. Any running system will drift from its intended state over time (operator changes, autoscaler, bugs) — the correction mechanism must be automatic, not manual.
3. An audit trail of every change is necessary for security, compliance, and incident diagnosis — Git provides this for free.

**DERIVED DESIGN:**
GitOps derives from IaC's "desired state in code" principle and extends it with a continuous reconciliation loop. The reconciliation loop has three steps:

1. **Observe**: read actual cluster state (kubectl get all)
2. **Diff**: compare actual vs desired (git HEAD)
3. **Act**: apply changes to converge actual → desired

The loop runs continuously (every few seconds or on Git commit), making drift self-healing. This is the **control loop** pattern from distributed systems: the agent is a controller, the Git-declared state is the spec, the cluster is the object being controlled.

**Pull vs Push model security:**
Push model: CI server holds cluster credentials (kubeconfig, service account token). Any system that can trigger CI can deploy arbitrary code to production. Attack surface: any committer + any third-party action in the pipeline.
Pull model: Only the in-cluster ArgoCD/Flux agent has cluster access. The agent reads from Git using a deploy key (read-only). CI commits to Git — that's all CI can do. The in-cluster agent decides what gets applied, running inside the security boundary of the cluster itself.

**THE TRADE-OFFS:**
**Gain:** No cluster credentials in CI; full audit trail in Git; self-healing drift correction; environment parity through declarative config; PR-based change management for Kubernetes.
**Cost:** The GitOps repo becomes the bottleneck for all deployments — its branching strategy and access controls are critical. Pull model introduces reconciliation latency (seconds to minutes). Debugging requires understanding both Git state and cluster state simultaneously. Secrets management is harder (secrets must be in Git but not as plaintext — requires SealedSecrets or External Secrets Operator).

---

### 🧪 Thought Experiment

**SETUP:**
An operator manually scales a critical production deployment from 3 to 10 replicas to handle a traffic spike at 3am. No code change. They run `kubectl scale deployment/api --replicas=10`. Crisis averted.

**WHAT HAPPENS WITHOUT GITOPS:**
The deployment runs at 10 replicas. The next morning, a developer pushes a minor change. CI deploys by running `kubectl apply -f manifests/api.yaml` — which has `replicas: 3`. The deployment quietly scales back to 3. At 10am peak traffic, the service struggles with only 3 replicas. Incident. Nobody connects it to the CI deployment. The operator's 3am scale is lost forever.

**WHAT HAPPENS WITH GITOPS:**
The operator scales to 10 replicas at 3am. ArgoCD's reconciliation loop runs 5 minutes later. It compares actual state (10 replicas) against Git-declared state (3 replicas) — detects drift. ArgoCD marks the application as "OutOfSync." Options: (A) ArgoCD auto-syncs: reverts to 3 replicas immediately (self-heal). (B) ArgoCD alerts operators but waits. The operator, seeing the alert, updates the Git manifest: `replicas: 10` via a PR — creating an auditable record of the emergency scale. Either way: the intent is in Git. The cluster and Git converge.

**THE INSIGHT:**
GitOps forces the question: "Is this change in Git?" If not, it doesn't exist as authoritative state. The system enforces this by overwriting unrecorded changes. This sounds strict — and it is. But that strictness is exactly what eliminates the class of incidents caused by invisible drift.

---

### 🧠 Mental Model / Analogy

> GitOps is like double-entry bookkeeping for infrastructure. Every transaction (cluster change) must be recorded in both the ledger (Git) and the physical account (the cluster). An automated auditor (ArgoCD) checks regularly that the ledger matches the physical account and flags or corrects discrepancies. You can't have a secret transaction — the auditor will find it.

- "Double-entry ledger" → Git repository (the source of truth)
- "Physical account" → Kubernetes cluster (actual running state)
- "Auditor checking ledger vs account" → ArgoCD reconciliation loop
- "Discrepancy" → drift between Git and cluster
- "Correcting the account to match the ledger" → ArgoCD sync
- "Unauthorized transaction" → manual `kubectl` change without a Git commit

Where this analogy breaks down: a bookkeeper corrects discrepancies only after review. ArgoCD can be configured to auto-correct drift immediately — without human review. This automatic correction is powerful but can interfere with emergency operational changes if the team doesn't have a process for "record first, then act."

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
GitOps means the git repository is the rulebook for your servers and applications. What's in git is what runs. An automated robot checks constantly that reality matches the rulebook and fixes any differences. If you change something manually, the robot puts it back.

**Level 2 — How to use it (junior developer):**
Set up ArgoCD in your Kubernetes cluster. Create a Git repository with your Kubernetes manifests. Create an ArgoCD `Application` resource pointing to the Git repo and the target cluster namespace. ArgoCD watches the repo — when you push a new manifest or update an image tag, ArgoCD applies the change to the cluster automatically. Never use `kubectl apply` directly in production. All changes go through Git PRs. View the sync status in the ArgoCD UI.

**Level 3 — How it works (mid-level engineer):**
ArgoCD's controller watches both the Git repo (via webhook or polling every 3 minutes) and the Kubernetes cluster API. For each managed `Application`, it performs a 3-way diff: (1) live Kubernetes object, (2) Git-declared manifest, (3) last known state (avoids marking externally-managed fields as drift). When diff is non-empty, the application is "OutOfSync." In auto-sync mode, ArgoCD runs the equivalent of `kubectl diff` then `kubectl apply` with the Git manifests. Server-side apply (Kubernetes 1.22+) handles field ownership conflicts. ArgoCD Sync Waves and Hooks enable ordered deployment (wave 1: database, wave 2: app, wave 3: smoke test).

**Level 4 — Why it was designed this way (senior/staff):**
GitOps emerged from WeaveWorks' blog post (2017) "Operations by Pull Request" and was formalised by the OpenGitOps CNCF Working Group (2021). The architectural inversion (pull vs push) solved the credential problem that became acute as clusters became multi-tenant and CI systems were regularly compromised. The control loop pattern directly applied Kubernetes' own reconciliation philosophy (controllers manage resources by declaring desired state) to CD tooling. The emerging challenge in GitOps is scale: at 500+ ArgoCD Applications, the ArgoCD controller becomes a bottleneck. Solutions include ArgoCD ApplicationSets (template-based Application generation), App of Apps pattern (hierarchical Application management), and sharding ArgoCD across multiple instances. The Flux v2 (CNCF project) architecture uses composable controllers and avoids single-process bottlenecks by design.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  GITOPS RECONCILIATION LOOP (ArgoCD)        │
├─────────────────────────────────────────────┤
│                                             │
│  GIT REPO (source of truth):               │
│  apps/myapp/deployment.yaml                 │
│  apps/myapp/service.yaml                    │
│  apps/myapp/ingress.yaml                    │
│                                             │
│  ARGOCD CONTROLLER (in-cluster):            │
│  WATCH: git repo (push webhook / 3min poll) │
│  WATCH: Kubernetes API server               │
│                                             │
│  RECONCILE LOOP (every sync interval):      │
│  1. Fetch: git pull → get latest manifests  │
│  2. Render: Helm/Kustomize to plain YAML    │
│  3. Diff: git manifest vs live cluster obj  │
│  4. Sync status:                            │
│     Synced: live matches git → no action   │
│     OutOfSync: diff detected                │
│     → Auto-sync: apply git state           │
│     → Manual sync: alert and wait          │
│  5. Update: kubectl server-side apply       │
│  6. Verify: health checks pass?             │
│     healthy → DONE                         │
│     degraded → alert                       │
│                                             │
│  DRIFT SELF-HEAL:                           │
│  Manual kubectl change detected             │
│  → OutOfSync within 3 min                  │
│  → Auto-sync reverts to Git state          │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer merges PR with new image tag
  → CI: build → test → push image:sha-abc123
  → CI updates GitOps repo:
     sed -i "s/image:.*/image: myapp:sha-abc123/" \
       deploy/overlays/prod/kustomization.yaml
     git commit + push (to gitops-repo)
  → ArgoCD detects commit (webhook) [← YOU ARE HERE]
  → Renders Kustomize overlay with new image
  → Diff: image changed sha-old → sha-abc123
  → Auto-sync: kubectl apply
  → Deployment rolling update (zero downtime)
  → ArgoCD health: all pods Running
  → Status: Synced + Healthy
```

**FAILURE PATH:**
```
ArgoCD applies new manifest
  → Deployment rolling update starts
  → New pods fail (CrashLoopBackOff: OOMKilled)
  → ArgoCD status: Degraded
  → Auto-rollback (if configured via PreSync hook)
     OR: operator reviews, reverts image tag in Git
  → Git revert → ArgoCD syncs to reverted state
  → Previous version restored
```

**WHAT CHANGES AT SCALE:**
At 200+ Kubernetes applications, ArgoCD ApplicationSets generate `Application` resources from templates — one ApplicationSet for all microservices instead of 200 individual Application manifests. ApplicationSet generators (cluster, git directory, PR-based) enable fleet-wide deployments and per-PR preview environments. ArgoCD's performance scales horizontally (multiple ArgoCD instances sharded by application labels). Secrets management becomes critical: GitOps stores manifests in public or semi-public Git repos, so secrets never appear in plaintext — all teams use either SealedSecrets, External Secrets Operator, or Vault Agent Injector.

---

### 💻 Code Example

**Example 1 — ArgoCD Application manifest:**
```yaml
# argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-production
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/myorg/gitops-config
    targetRevision: HEAD
    path: apps/myapp/overlays/production
    # Kustomize: rendered automatically

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true      # delete resources removed from Git
      selfHeal: true   # auto-revert manual kubectl changes
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true  # Kubernetes 1.22+
```

**Example 2 — Kustomize overlay structure (GitOps repo):**
```
gitops-config/
  apps/
    myapp/
      base/
        deployment.yaml
        service.yaml
        kustomization.yaml
      overlays/
        dev/
          kustomization.yaml   # patches: replicas=1, image=latest
        staging/
          kustomization.yaml   # patches: replicas=2
        production/
          kustomization.yaml   # patches: replicas=5, image=sha-abc
```
```yaml
# apps/myapp/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
patches:
  - target:
      kind: Deployment
      name: myapp
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
images:
  - name: myapp
    newTag: sha-abc123  # Updated by CI pipeline
```

**Example 3 — CI pipeline updating GitOps repo:**
```bash
# In CI pipeline (after building image):
# Update image tag in production GitOps overlay
IMAGE_TAG="${GITHUB_SHA:0:8}"

# Using yq to update image tag
yq e ".images[0].newTag = \"${IMAGE_TAG}\"" \
  -i apps/myapp/overlays/production/kustomization.yaml

# Commit to GitOps repo
git config user.email "ci@example.com"
git config user.name "CI Bot"
git add apps/myapp/overlays/production/kustomization.yaml
git commit -m "chore: deploy myapp ${IMAGE_TAG} to production"
git push origin main
# ArgoCD detects this commit within seconds
```

---

### ⚖️ Comparison Table

| | GitOps (ArgoCD) | Push-based CD | Argo Workflows | Spinnaker |
|---|---|---|---|---|
| Direction | Pull (in-cluster agent) | Push (CI server) | Push (workflow engine) | Push |
| Cluster Creds in CI | No | Yes | Depends | Yes |
| Drift Detection | Yes (continuous) | No | No | No |
| Self-Healing | Yes | No | No | No |
| Source of Truth | Git | CI config | CI config | CI config |
| Best For | K8s, GitOps principle | Simple pipelines | Workflow orchestration | Multi-cloud enterprise |

How to choose: Use **GitOps (ArgoCD/Flux)** for any Kubernetes-based workload where you want drift detection, self-healing, and push-based security. Use **push-based CD** only for non-Kubernetes targets (VMs, serverless) where a GitOps agent can't run in-target. Use **Spinnaker** for complex multi-cloud enterprise deployments with sophisticated canary analysis needs.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GitOps means you can do everything with kubectl via Git commits | GitOps covers application state and configuration. Cluster provisioning (creating the Kubernetes cluster itself via EKS, GKE), network configuration, and cloud resources still require Terraform or Pulumi. GitOps and IaC are complementary, not alternatives. |
| Self-healing means the system fixes bugs automatically | Self-healing means ArgoCD reverts *configuration drift* back to the Git-declared state. It has no ability to fix application bugs, code errors, or resource exhaustion. It only corrects the gap between Git state and cluster state. |
| GitOps requires ArgoCD | GitOps is a principle, not a tool. Flux (CNCF), Rancher Fleet, and Jenkins X also implement GitOps. ArgoCD is the most popular GitOps tool for Kubernetes but is not the definition of GitOps. |
| All changes must wait for the reconciliation loop | Emergency changes can be made directly in Git (not `kubectl`) and ArgoCD picks them up within seconds if configured with webhook triggers. The latency is measured in seconds, not minutes, with proper webhook setup. |
| GitOps requires all manifests in one mono-repo | GitOps repos can be per-service, per-team, or a monorepo. The critical requirement is that the GitOps repo is the source of truth — not which specific structure stores it. |

---

### 🚨 Failure Modes & Diagnosis

**1. Secrets in GitOps Repo Exposed**

**Symptom:** A Kubernetes Secret manifest committed to the GitOps repository contains a plaintext `DB_PASSWORD`. The repo is public or has broad internal access. Credentials are exposed.

**Root Cause:** GitOps requires manifests in Git, but Kubernetes Secret base64-encoding is NOT encryption — it's trivially decodable. Treating b64 as secure and committing Secrets to Git is a common mistake.

**Diagnostic:**
```bash
# Find all Secret resources in GitOps repo
grep -r "kind: Secret" gitops-config/

# Check if any values are not encrypted
grep -r "apiVersion: v1" gitops-config/ | grep Secret

# Check for SealedSecrets or ESO usage
grep -r "SealedSecret\|ExternalSecret" gitops-config/
```

**Fix:**
```yaml
# BAD: plaintext base64 in git
apiVersion: v1
kind: Secret
data:
  password: cGFzc3dvcmQ=  # "password" — trivially decodable

# GOOD: SealedSecret (encrypted, safe to commit to git)
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
spec:
  encryptedData:
    password: AgBkZXZ...  # encrypted with cluster-specific key
```

**Prevention:** Mandate SealedSecrets (`kubeseal`) or External Secrets Operator as the secret management standard. Add a CI lint check: any file with `kind: Secret` and non-encrypted data fails the PR.

---

**2. ArgoCD ApplicationSet Generates 200 Accidental Apps**

**Symptom:** After merging a new `ApplicationSet` using the git directory generator, ArgoCD creates 200 new Application objects (one per directory in the repo) — overwhelming the cluster and ArgoCD controller.

**Root Cause:** Git directory generator configured too broadly (`path: "*"` instead of `path: "apps/*"`). Every directory in the repo becomes an Application.

**Diagnostic:**
```bash
# Check how many Applications ArgoCD is managing
kubectl get applications -n argocd | wc -l

# List apps created in last 5 minutes
kubectl get applications -n argocd \
  --sort-by=.metadata.creationTimestamp | tail -20

# Check ApplicationSet spec
kubectl get applicationset -n argocd -o yaml | grep path
```

**Fix:**
```yaml
# ApplicationSet with safe scope
spec:
  generators:
    - git:
        repoURL: https://github.com/myorg/gitops-config
        revision: HEAD
        directories:
          - path: apps/*/overlays/production  # specific only
          # NOT: path: "*" (too broad)
```

**Prevention:** Test `ApplicationSet` in a development ArgoCD instance first. Use `dryRun: true` in the ApplicationSet spec to preview what Applications would be generated.

---

**3. Manual Emergency Change Immediately Overwritten by ArgoCD**

**Symptom:** Operator scales deployment from 2 to 20 replicas during a DDoS. ArgoCD auto-sync runs 30 seconds later and reverts to 2. Operator scales again. ArgoCD reverts. Loop continues.

**Root Cause:** ArgoCD `selfHeal: true` continuously reverts manual changes. In genuine emergencies, this works against the operator.

**Diagnostic:**
```bash
# Check ArgoCD sync status during incident
kubectl get application myapp -n argocd \
  -o jsonpath='{.status.sync.status}'

# Temporarily pause auto-sync for app
argocd app set myapp --sync-policy none
# Disables auto-sync — manual sync only until re-enabled
```

**Fix:**
```bash
# Disable auto-sync for the affected application
argocd app set myapp --sync-policy none

# Make emergency change directly on cluster
kubectl scale deployment/myapp --replicas=20

# After incident resolves: update git manifest
# git commit -m "fix: scale myapp to 20 for traffic event"

# Re-enable auto-sync
argocd app set myapp --sync-policy automated \
  --auto-prune --self-heal
```

**Prevention:** Define an emergency procedure: before any manual cluster change, pause ArgoCD auto-sync for the affected application. Document the runbook. Use ArgoCD RBAC to ensure only on-call engineers can pause auto-sync.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Git` — GitOps uses Git as the source of truth; understanding branching, commits, and PR workflows is required
- `Kubernetes` — GitOps is primarily used with Kubernetes; understanding Kubernetes objects and controllers is required
- `Infrastructure as Code` — GitOps extends IaC principles with continuous reconciliation; IaC is the foundational concept

**Builds On This (learn these next):**
- `ArgoCD` — the leading GitOps CD tool for Kubernetes; the most common implementation of GitOps principles
- `Environment Promotion` — GitOps implements environment promotion via Git commits to environment-specific overlay directories
- `Progressive Delivery` — canary and blue/green deployments in a GitOps model are orchestrated by ArgoCD Rollouts or Flagger

**Alternatives / Comparisons:**
- `Push-based CI/CD` — CI server directly deploys to targets; simpler setup, no drift detection, cluster credentials in CI
- `ArgoCD` vs `Flux` — both implement GitOps; ArgoCD has a richer UI and RBAC model; Flux has a better multi-cluster and multi-tenant architecture
- `Terraform` — IaC for cloud infrastructure provisioning; GitOps typically uses Terraform for cluster provisioning and GitOps for workload management

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Git as single source of truth — agents    │
│              │ continuously converge cluster to Git state│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Invisible drift between intended and      │
│ SOLVES       │ actual state; no audit trail for changes  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pull model: cluster agent reads Git.      │
│              │ CI never holds cluster credentials.       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Kubernetes-based deployments needing      │
│              │ drift detection and full audit trail      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Non-Kubernetes targets; simple single-env │
│              │ pipelines where drift detection is moot   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Security + auditability + self-healing vs │
│              │ secrets-in-git complexity + strict process│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Self-maintaining garden: the blueprint   │
│              │  (Git) always wins over physical reality."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ArgoCD → Flux → ApplicationSets →         │
│              │ Progressive Delivery → SealedSecrets      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team adopts GitOps with ArgoCD and self-heal enabled. During a major traffic event at 11pm, an on-call engineer needs to immediately scale a deployment from 3 to 50 replicas. ArgoCD keeps reverting the change. The engineer disables ArgoCD auto-sync, makes the emergency change, and forgets to re-enable auto-sync. For the next 3 days, no deployments reach production (PRs merge but ArgoCD doesn't sync). How do you design the operational processes and technical controls to prevent both problems: (1) ArgoCD fighting the engineer during the emergency, and (2) the disabled auto-sync going unnoticed for days?

**Q2.** In a GitOps model, the Git repository is the source of truth. But Kubernetes autoscalers (HPA, KEDA) dynamically change the `replicas` field of deployments based on traffic. If ArgoCD sees `replicas: 3` in Git but the HPA has scaled to `replicas: 20`, ArgoCD will detect "drift" and potentially revert to 3. How do GitOps tools handle this conflict between declared desired state (static) and auto-scaled actual state (dynamic), and what is the correct configuration to allow HPAs and GitOps to coexist without constant revert wars?

