---
number: "454"
category: DevOps & SDLC
difficulty: ★★☆
depends_on: CI/CD Pipeline, IaC, Kubernetes
used_by: CI/CD Pipeline, IaC, Kubernetes
tags: #devops #sdlc #intermediate #gitops
---

# 454 — GitOps

`#devops` `#sdlc` `#intermediate` `#gitops`

⚡ TL;DR — Use git as the single source of truth for both application code and infrastructure; automated agents reconcile the running system to match the git state.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #454         │ Category: DevOps & SDLC              │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ CI/CD Pipeline, IaC, Kubernetes                                   │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ CI/CD Pipeline, IaC, Kubernetes                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

GitOps is an operational framework that takes DevOps best practices (version control, collaboration, compliance, CI/CD) and applies them to infrastructure automation. The desired state of the entire system — applications, configuration, and infrastructure — is declared in git. An automated operator continuously watches git and reconciles the live environment to match, making git the single source of truth.

---

## 🟢 Simple Definition (Easy)

GitOps means **"git is the source of truth for what's running in production"**. You commit a change to git; an automated agent reads it and makes production match — no manual `kubectl apply` or `terraform apply` needed.

---

## 🔵 Simple Definition (Elaborated)

Traditional CD pushes changes to production (pipeline triggers deploy). GitOps inverts this: an agent running inside the cluster continuously pulls the desired state from git and reconciles any divergence. If someone manually changes a pod in production, the agent detects the drift and reverts it to match git. This creates an immutable, auditable, and self-healing system.

---

## 🔩 First Principles Explanation

**The core problem:**
CI/CD pipelines need credentials to push changes to production (push model). This creates a large blast radius if the pipeline is compromised. Manual changes to production diverge from the intended state and are not tracked.

**The insight:**
> "Don't let CI push to production. Instead, let production pull from git. Git is the contract; the cluster enforces it continuously."

```
PUSH model (traditional CI/CD):
  Git --> CI Pipeline --> kubectl apply --> cluster
  Problem: pipeline needs cluster credentials (security risk)

PULL model (GitOps):
  Git <-- ArgoCD watches --> detects diff --> reconciles cluster
  Benefit: cluster credentials stay IN the cluster (no external access needed)
```

---

## ❓ Why Does This Exist (Why Before What)

Without GitOps, production state drifts from git over time (manual patches, hotfixes). Auditing what's actually running is hard. Security requires giving CI pipelines cluster credentials. GitOps eliminates all three problems by using a pull-based reconciliation loop.

---

## 🧠 Mental Model / Analogy

> GitOps is like a thermostat for your infrastructure. The thermostat has a desired state (e.g., 22°C = what's in git). If the room temperature drifts (manual change, failure), the thermostat automatically corrects it — without anyone manually turning on the heater. Git declares the desired temperature; the GitOps operator is the thermostat.

---

## ⚙️ How It Works (Mechanism)

```
GitOps reconciliation loop:

  1. Developer commits change to git (desired state)
  2. ArgoCD / Flux detects change (polls or webhook)
  3. Compares desired state (git) vs actual state (cluster)
  4. Applies diff: cluster converges to desired state
  5. Reports sync status (in sync / out of sync)

  If manual change made directly to cluster:
  - Agent detects drift
  - Reverts to git state (or alerts if manual override allowed)

  Key properties:
  - Declarative: describe WHAT, not HOW
  - Versioned: every change is a git commit with full history
  - Automated: no manual deploy commands
  - Continuously reconciled: drift is detected and corrected
```

---

## 🔄 How It Connects (Mini-Map)

```
[Developer git push]
       ↓
[Git Repo: desired state]
       ↓ watched by
[ArgoCD / Flux operator]
       ↓ compares
[Live Cluster State]
       ↓ reconciles
[Cluster matches git] <-- continuous loop
```

---

## 💻 Code Example

```yaml
# ArgoCD Application — watches git repo, syncs to cluster
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp-config
    targetRevision: main
    path: k8s/production          # folder with K8s manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true                  # delete resources removed from git
      selfHeal: true               # revert manual changes to cluster
    syncOptions:
    - CreateNamespace=true
```

```bash
# GitOps workflow: no kubectl apply in production
# Developer workflow:
git clone myapp-config
# edit k8s/production/deployment.yaml — change image tag
git commit -m "deploy: update myapp to v2.0.0"
git push origin main
# ArgoCD detects change, automatically syncs cluster — done.

# Check sync status
argocd app get myapp
argocd app sync myapp   # manual sync if needed

# Rollback = git revert
git revert HEAD
git push origin main
# ArgoCD reverts cluster automatically
```

---

## 🔁 Flow / Lifecycle

```
1. Developer pushes desired state to git
        ↓
2. CI runs: build image, push to registry, update image tag in config repo
        ↓
3. ArgoCD detects config repo change
        ↓
4. ArgoCD diffs desired (git) vs actual (cluster)
        ↓
5. ArgoCD applies diff — cluster converges
        ↓
6. Continuous monitoring: any drift → auto-reconcile
        ↓
7. Rollback: git revert → ArgoCD reconciles → old version live
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| GitOps = CI/CD | GitOps is a CD model (pull-based); CI is still push-based |
| GitOps only works with Kubernetes | GitOps principles apply to any infra with a declarative API |
| All changes go through git PRs slowly | Automated image tag updates make this fast; only config changes need PRs |
| Self-healing means no incidents | Self-healing reverts drift; it doesn't prevent application bugs |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Secrets in Git**
Storing application secrets directly in git is a critical security error.
Fix: use sealed secrets (Bitnami Sealed Secrets), Vault + External Secrets Operator, or SOPS encryption.

**Pitfall 2: Config Repo and App Repo Same Repo**
CI that builds images should not commit directly to the repo that ArgoCD watches — this creates circular triggers.
Fix: separate app repo (source code) from config repo (K8s manifests); CI updates config repo after image push.

**Pitfall 3: Ignoring Sync Alerts**
ArgoCD "OutOfSync" warnings left unresolved for days.
Fix: treat OutOfSync as an incident; alert on-call; investigate and resolve immediately.

---

## 🔗 Related Keywords

- **CI/CD Pipeline** — CI builds; GitOps handles the CD (pull-based)
- **IaC (Infrastructure as Code)** — GitOps applies IaC principles to application delivery
- **ArgoCD / Flux** — the most common GitOps operators for Kubernetes
- **Immutable Infrastructure** — GitOps enforces this: no manual changes survive reconciliation
- **Sealed Secrets** — the solution for storing secrets safely in a GitOps git repo

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Git is the single source of truth; an agent  │
│              │ continuously reconciles the cluster to match  │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Kubernetes environments; need auditability,   │
│              │ drift detection, secure CD                    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Stateful systems where git state alone is     │
│              │ insufficient to describe the full system      │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Don't deploy to production — declare what    │
│              │  should be there and let git enforce it"      │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ ArgoCD --> Flux --> IaC --> Sealed Secrets    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** How does the pull-based GitOps model improve security compared to the push-based CI/CD model?  
**Q2.** What is the "drift detection and self-healing" property of GitOps, and why is it valuable in production?  
**Q3.** How do you handle secrets in a GitOps workflow without storing them in plaintext in git?

