---
version: 1
layout: default
title: "GitOps with Kubernetes"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 56
permalink: /kubernetes/gitops-with-kubernetes/
id: K8S-056
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["kubectl", "Helm", "Kustomize", "Deployment"]
used_by: ["ArgoCD", "FluxCD", "Kubernetes Secrets Management"]
related:
  [
    "ArgoCD",
    "FluxCD",
    "Helm Chart",
    "Kustomize",
    "Kubernetes Secrets Management",
  ]
tags: [kubernetes, gitops, argocd, fluxcd, ci-cd, deployment, k8s]
---

# GitOps with Kubernetes

## ⚡ TL;DR

**GitOps** treats Git as the single source of truth for cluster state. A GitOps operator (ArgoCD, FluxCD) continuously reconciles the cluster to match what's in Git. No `kubectl apply` by humans in production. All changes via pull requests. Immediate drift detection and auto-correction.

---

## 🔥 Problem This Solves

Manual `kubectl apply` commands create drift: cluster state diverges from what anyone thinks it is. Who deployed what? When? Why? GitOps answers: everything is in Git, audited, reviewed, versioned. Rollback = git revert. Disaster recovery = git clone + point controller at repo.

---

## 📘 Textbook Definition

GitOps is an operational framework where the desired state of a Kubernetes cluster is fully described in a Git repository. An automated operator continuously compares desired state (Git) with actual state (cluster) and reconciles differences. Changes are made through Git operations (PR, merge) rather than direct cluster access.

---

## ⏱️ 30 Seconds

```
Git repo (desired state):
  apps/
    my-service/
      deployment.yaml (replicas: 3, image: v1.2.0)
      service.yaml

ArgoCD/FluxCD (GitOps operator):
  Every 3 minutes:
    1. Fetch Git repo
    2. Compare to cluster state
    3. Cluster has replicas: 2 (drift!) → apply deployment.yaml
    4. Cluster now matches Git ✅

Developer wants to deploy v1.3.0:
  → Open PR: change image: v1.3.0 in deployment.yaml
  → CI validates the YAML
  → PR approved + merged
  → GitOps operator detects change → applies → done
```

---

## 🔩 First Principles

- Git = declarative desired state; GitOps operator = reconciliation loop
- Pull-based: operator PULLS from Git (vs push-based CI/CD where CI pushes to cluster)
- Drift detection: any manual change to cluster is detected and reverted (or alerted)
- `sync` = reconcile Git → cluster; `diff` = show what differs
- Separate repos: app code (developers) vs cluster config (platform team) → GitOps repo
- Secret management: SOPS/Sealed Secrets for secrets in Git

---

## 🧪 Thought Experiment

Production incident: someone runs `kubectl scale deployment my-app --replicas=1` during an outage to free up resources. Without GitOps: cluster state diverges from YAML; it's unclear what's "true". With GitOps: within 3 minutes, ArgoCD detects the drift, reverts to 3 replicas (or alerts if auto-sync is off). The Git history always reflects what's actually running.

---

## 🧠 Mental Model / Analogy

GitOps is like **infrastructure treated as a thermostat**: Git is the desired temperature, the cluster is the room, the GitOps operator is the thermostat controller. If someone opens a window (manual kubectl change), the thermostat detects the drift and corrects it (auto-sync) or alerts you (manual sync mode). The desired state (Git) is always the authority.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: GitOps = Git controls what runs in Kubernetes. Change Git → cluster changes. No direct kubectl in production.

**Level 2 - Practitioner**: ArgoCD/FluxCD watch a Git repo. When you merge a PR, the operator applies the changes. Rollback = git revert + merge = cluster reverts. Drift detection shows if cluster has been manually modified.

**Level 3 - Advanced**: Multi-cluster: one GitOps operator managing multiple clusters with environment directories. Image update automation: FluxCD ImageUpdateAutomation commits new image tags to Git automatically (CD automation). Helm releases via GitOps: `HelmRelease` CRD references a chart and values. Progressive delivery: ArgoCD Rollouts or Flagger for canary deployments with automated metric-based promotion.

**Level 4 - Expert**: GitOps repo structure patterns: monorepo (all clusters) vs polyrepo (per team). Environment promotion: Git branching (dev/staging/prod branches) vs Kustomize overlays vs directory-per-cluster. ApplicationSet (ArgoCD): template-based app generation for hundreds of apps/clusters from a single CRD. GitOps and compliance: every change is a commit (who, what, when, approved by whom), satisfies SOC2/PCI-DSS change management requirements.

---

## ⚙️ How It Works

### GitOps Repo Structure (Kustomize)

```
gitops-repo/
  clusters/
    production/
      kustomization.yaml    # points to apps
      apps/
        my-service/
          kustomization.yaml
          base/             # links to app's base
          overlays/prod/    # prod-specific patches
    staging/
      apps/
        my-service/
          overlays/staging/

  base/                     # shared across clusters
    my-service/
      deployment.yaml
      service.yaml
      kustomization.yaml
```

### ArgoCD Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/gitops-repo
    targetRevision: main
    path: clusters/production/apps/my-service
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true # delete resources removed from Git
      selfHeal: true # revert manual changes
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
```

### FluxCD HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: my-service
  namespace: production
spec:
  interval: 10m
  chart:
    spec:
      chart: my-service
      version: ">=1.0.0 <2.0.0"
      sourceRef:
        kind: HelmRepository
        name: my-charts
  values:
    replicaCount: 3
    image:
      tag: v1.2.0
  install:
    remediation:
      retries: 3
  upgrade:
    remediation:
      remediateLastFailure: true
```

### CI/CD + GitOps Pipeline

```
Developer pushes code:
  1. CI: build + test
  2. CI: docker build → push image:sha256-abc123
  3. CI: PR to GitOps repo:
     change deployment.yaml image tag to sha256-abc123
  4. Platform team reviews PR
  5. Merge to main
  6. ArgoCD detects change within polling interval
  7. ArgoCD applies to cluster
  8. Rolling update deploys new image

No human runs kubectl in production.
CI pipeline cannot directly modify cluster (no kubeconfig in CI).
```

---

## 🔄 E2E Flow: Emergency Rollback

```
Production incident: new v1.3.0 has memory leak

Option 1 (GitOps rollback):
  git revert <commit that changed to v1.3.0>
  git push → merge PR
  ArgoCD: detected, applies, rolling update to v1.2.0
  Time: ~5 minutes (review + apply)

Option 2 (ArgoCD rollback):
  ArgoCD UI → History → select revision 42 → Rollback
  ArgoCD re-syncs to revision 42 state
  Time: ~2 minutes (no PR needed)

Both approaches:
  - Full audit trail in ArgoCD
  - Git history unchanged (option 1) or noted (option 1)
  - Next PR review will show the revert
```

---

## ⚖️ Comparison Table

|                     | Push-based CI/CD           | GitOps (Pull-based)             |
| ------------------- | -------------------------- | ------------------------------- |
| **Cluster access**  | CI pipeline has kubeconfig | Only GitOps operator has access |
| **Drift detection** | ❌                         | ✅                              |
| **Rollback**        | Re-run CI pipeline         | git revert or UI rollback       |
| **Audit trail**     | CI logs                    | Git history + GitOps events     |
| **Multi-cluster**   | kubeconfig per cluster     | Single GitOps operator          |
| **Security**        | CI has cluster credentials | Git has no cluster access       |

---

## ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                            |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| "GitOps means no kubectl ever"  | kubectl still used for debugging (get/describe/logs); only apply/delete restricted |
| "GitOps is complex to set up"   | ArgoCD installs in 5 minutes; FluxCD bootstraps in `flux bootstrap github ...`     |
| "GitOps requires Helm"          | Works with raw YAML, Kustomize, Helm, or custom tools                              |
| "GitOps slows down deployments" | PR merge to deployment in 2-3 minutes; can be automated for staging                |

---

## 🚨 Failure Modes

| Failure                       | Symptom                         | Fix                                                                       |
| ----------------------------- | ------------------------------- | ------------------------------------------------------------------------- |
| GitOps repo branch deleted    | ArgoCD/Flux can't sync          | Set branch protection; use specific targetRevision                        |
| Secrets in Git                | Credential exposure             | Use SOPS/Sealed Secrets; never commit plaintext secrets                   |
| Auto-sync + accidental delete | `prune: true` deletes resources | Review diffs before enabling prune; use `syncOptions: ApplyOutOfSyncOnly` |
| GitOps operator goes down     | Cluster drifts, no corrections  | Monitor operator health; it's stateless, easy to restore                  |

---

## 🔗 Related Keywords

- [ArgoCD](/kubernetes/argocd/) - most popular GitOps operator
- [FluxCD](/kubernetes/fluxcd/) - CNCF GitOps operator
- [Helm Chart](/kubernetes/helm-chart/) - packaged apps deployed via GitOps
- [Kustomize](/kubernetes/kustomize/) - environment config management in GitOps
- [Kubernetes Secrets Management](/kubernetes/kubernetes-secrets-management/) - secrets in GitOps

---

## 📌 Quick Reference Card

```bash
# ArgoCD quick setup
kubectl create namespace argocd
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Port forward ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Login
argocd login localhost:8080 --username admin

# Create app
argocd app create my-service \
  --repo https://github.com/myorg/gitops-repo \
  --path clusters/prod/my-service \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production \
  --sync-policy automated

# Sync status
argocd app list
argocd app get my-service
argocd app diff my-service    # show what would change
argocd app sync my-service    # manual sync
```

---

## 🧠 Think About This

The biggest GitOps organizational challenge isn't technical - it's the **separation between app repo and GitOps repo**. Should developers own their GitOps manifests? Should a platform team? The emerging pattern: developers own app code AND the GitOps manifests for their service in the same repo (or a service-owned GitOps repo), but the platform team controls the cluster registration and environment promotion gates. This gives developers deployment autonomy while platform team maintains control over production environment standards. The PR-based promotion workflow is the key: staging deploys automatically, production requires PR approval.
