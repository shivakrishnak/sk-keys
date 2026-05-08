---
layout: default
title: "ArgoCD"
parent: "Kubernetes"
nav_order: 56
permalink: /kubernetes/argocd/
id: K8S-056
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["GitOps with Kubernetes", "Helm", "Kustomize", "RBAC (K8s)"]
used_by: ["GitOps with Kubernetes", "K8s Multi-Cluster"]
related:
  [
    "GitOps with Kubernetes",
    "FluxCD",
    "Helm Chart",
    "Kustomize",
    "ApplicationSet",
  ]
tags: [kubernetes, argocd, gitops, continuous-deployment, k8s, argo]
---

# ArgoCD

## ⚡ TL;DR

**ArgoCD** is a declarative GitOps continuous delivery tool for Kubernetes. It watches Git repositories, compares desired state to cluster state, and syncs. Features: multi-cluster, Helm/Kustomize/raw YAML support, web UI with diff visualization, RBAC, SSO, and ApplicationSet for templated multi-app management.

---

## 🔥 Problem This Solves

You need to deploy dozens of microservices across dev/staging/prod Kubernetes clusters, track what's deployed where, detect drift, roll back failed deployments, and give developers visibility — without giving CI pipelines direct cluster access.

---

## 📘 Textbook Definition

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It follows the GitOps pattern by using Git repositories as the source of truth for defining the desired application state and automates the synchronization between the desired state and the running state in Kubernetes clusters.

---

## ⏱️ 30 Seconds

```yaml
# Install ArgoCD
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Define an Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: guestbook
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
```

---

## 🔩 First Principles

- **Application**: ArgoCD's unit of deployment — maps a Git path to a cluster namespace
- **Project**: grouping of Applications with access policies and source/destination restrictions
- **Sync**: reconcile Git → cluster (auto or manual)
- **Health**: ArgoCD checks Application health (Pod status, Deployment rollout) independently from sync
- **Components**: argocd-server (API/UI), argocd-repo-server (Git cache), argocd-application-controller (reconcile loop), argocd-dex-server (SSO)

---

## 🧪 Thought Experiment

100 microservices, 3 clusters (dev/staging/prod). Without ArgoCD: 100 × 3 = 300 CI pipeline configurations, each with cluster credentials, each doing `kubectl apply`. With ArgoCD: one ArgoCD per cluster (or one with multi-cluster), 300 Application CRDs in Git. Single control plane, UI shows all 300 deployments and their health. One SSO-integrated RBAC model.

---

## 🧠 Mental Model / Analogy

ArgoCD is like **a GPS navigator for your cluster**: you tell it where you want to go (Git), it continuously compares current position (cluster) with destination (Git), and reroutes if you drift. The UI is the navigation dashboard — it shows you where every service is, the route, and any detours needed.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: ArgoCD watches your Git repo. When you push changes, it applies them to your cluster. The UI shows green (synced) or red (out of sync).

**Level 2 — Practitioner**: `syncPolicy.automated`: auto-sync on Git change. `selfHeal: true`: auto-revert manual cluster changes. `prune: true`: delete resources removed from Git. Sync waves: order resource creation. Resource hooks: PreSync/PostSync Jobs (DB migrations).

**Level 3 — Advanced**: AppProject: restrict which repos, clusters, namespaces an Application can use. RBAC: `argocd-rbac-cm` ConfigMap with Casbin policies. SSO: OIDC/SAML via dex. ApplicationSet: generate Applications from templates (Git generator, cluster generator, list generator). Resource health customization via Lua scripts.

**Level 4 — Expert**: Argo Rollouts: extension for progressive delivery (canary, blue-green with automated analysis). `AnalysisTemplate` + Prometheus metrics for automated canary promotion/rollback. ArgoCD Notifications: Slack, PagerDuty, GitHub PR status on sync events. `argocd-image-updater`: watches container registry, commits new image tags to Git. Multi-tenancy: multiple teams, each with own AppProject, RBAC, and namespace restrictions. Sharding: multiple application controllers for > 1000 applications.

---

## ⚙️ How It Works

### ArgoCD Architecture

```
Git Repository (source of truth)
    ↓ (polling / webhook)
argocd-repo-server
    - Clones/caches repos
    - Renders templates (Helm, Kustomize)
    - Returns manifest list
    ↓
argocd-application-controller
    - Reconcile loop: desired (Git) vs actual (cluster)
    - Calculates diff
    - Applies sync (if auto-sync or manual trigger)
    - Reports Application status
    ↓
argocd-server (API + UI)
    - REST/gRPC API
    - Web UI + argocd CLI
    - SSO via dex
    ↓
Target cluster (same or remote)
    - Resources applied via kubectl
    - Health checked via K8s API
```

### ApplicationSet (Multi-App Management)

```yaml
# Generate an Application per cluster per environment
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-service
  namespace: argocd
spec:
  generators:
    - matrix:
        generators:
          - clusters:
              selector:
                matchLabels:
                  environment: production
          - git:
              repoURL: https://github.com/myorg/gitops-repo
              revision: main
              directories:
                - path: apps/*
  template:
    metadata:
      name: "{{path.basename}}-{{name}}" # app-name-cluster-name
    spec:
      project: production
      source:
        repoURL: https://github.com/myorg/gitops-repo
        targetRevision: main
        path: "{{path}}/overlays/{{metadata.labels.environment}}"
      destination:
        server: "{{server}}"
        namespace: "{{path.basename}}"
      syncPolicy:
        automated:
          selfHeal: true
```

### Sync Waves and Resource Hooks

```yaml
# Wave -1: Install CRDs first
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"

# Wave 0 (default): Regular resources

# PostSync Job (run after sync completes)
metadata:
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: smoke-test
        image: my-test:latest
        command: ["./run-smoke-tests.sh"]
```

### ArgoCD RBAC

```yaml
# argocd-rbac-cm ConfigMap
data:
  policy.default: role:readonly
  policy.csv: |
    # Developers can sync their apps
    p, role:developer, applications, sync, */*, allow
    p, role:developer, applications, get, */*, allow

    # Platform team is admin
    p, role:platform, applications, *, */*, allow
    p, role:platform, clusters, *, *, allow

    # Group bindings
    g, developers-team, role:developer
    g, platform-team, role:platform
```

---

## 🔄 E2E Flow: Automated CD Pipeline

```
1. Developer merges PR to main branch
   → Image: my-app:1.2.3 → registry

2. CI pipeline (GitHub Actions):
   → Build + test
   → Push image: my-registry/my-app:1.2.3
   → Update GitOps repo: overlays/prod/kustomization.yaml
     images:
     - name: my-app
       newTag: "1.2.3"
   → Open PR to GitOps repo

3. Platform team reviews + merges GitOps PR

4. ArgoCD (polling every 3 min or webhook):
   → Detects change in overlays/prod/
   → Renders Kustomize: final YAML with image 1.2.3
   → Diff: current cluster has 1.2.0
   → auto-sync: applies updated Deployment
   → Kubernetes: rolling update to 1.2.3

5. ArgoCD health check:
   → Deployment rollout complete, all pods Ready
   → Application status: Healthy + Synced ✅

6. Notification: Slack "#deploys" → "my-app 1.2.3 deployed to prod ✅"
```

---

## ⚖️ Comparison Table

|                          | ArgoCD         | FluxCD               | Spinnaker          |
| ------------------------ | -------------- | -------------------- | ------------------ |
| **UI**                   | ✅ Rich web UI | ❌ (CLI + Grafana)   | ✅                 |
| **Multi-cluster**        | ✅             | ✅                   | ✅                 |
| **ApplicationSet**       | ✅             | Flux `Kustomization` | Pipeline templates |
| **Progressive delivery** | Argo Rollouts  | Flagger              | Built-in           |
| **CNCF**                 | Incubating     | Graduated            | ❌                 |
| **Learning curve**       | Medium         | Low                  | High               |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                 |
| ------------------------------------- | ----------------------------------------------------------------------- |
| "ArgoCD replaces CI (build, test)"    | ArgoCD is CD only; CI (build, test, push image) is separate             |
| "ArgoCD needs to be in every cluster" | ArgoCD can manage multiple remote clusters from one instance            |
| "prune: true is always safe"          | prune can delete resources not in Git; review manifests before enabling |
| "ArgoCD syncs continuously"           | Polls Git (3 min default) or uses webhooks for near-instant sync        |

---

## 🚨 Failure Modes

| Failure            | Symptom                                    | Fix                                                           |
| ------------------ | ------------------------------------------ | ------------------------------------------------------------- |
| Sync failed        | Application shows OutOfSync + error        | Check sync error; fix YAML; use `argocd app logs`             |
| Health degraded    | Pod CrashLoopBackOff, Application Degraded | Check Pod logs; rollback to previous revision                 |
| ArgoCD itself down | No sync, UI unreachable                    | ArgoCD is stateless (state in K8s); `kubectl rollout restart` |
| SSO misconfigured  | "Login failed"                             | Check dex config; use local admin account as backup           |

---

## 🔗 Related Keywords

- [GitOps with Kubernetes](/kubernetes/gitops-with-kubernetes/) — the paradigm ArgoCD implements
- [FluxCD](/kubernetes/fluxcd/) — alternative GitOps operator
- [Helm Chart](/kubernetes/helm-chart/) — ArgoCD deploys Helm charts natively
- [Kustomize](/kubernetes/kustomize/) — ArgoCD renders Kustomize natively
- [K8s Multi-Cluster](/kubernetes/k8s-multi-cluster/) — ArgoCD manages multiple clusters

---

## 📌 Quick Reference Card

```bash
# Install ArgoCD CLI
brew install argocd
# or: https://github.com/argoproj/argo-cd/releases

# Login
argocd login <argocd-server> --sso
# or: argocd login localhost:8080

# App management
argocd app list
argocd app get my-app
argocd app diff my-app
argocd app sync my-app
argocd app rollback my-app 5   # rollback to revision 5

# Create app
argocd app create my-app \
  --repo https://github.com/myorg/gitops \
  --path apps/my-service/overlays/prod \
  --dest-namespace production

# Refresh (force re-fetch from Git)
argocd app get my-app --refresh

# Delete app (not resources)
argocd app delete my-app --cascade=false
```

---

## 🧠 Think About This

ArgoCD's `selfHeal: true` is powerful but requires trust in your Git repo. If `selfHeal` is on and someone accidentally merges a bad manifest to Git, ArgoCD will immediately apply it and keep healing back to it — preventing manual fixes. Production best practice: `selfHeal: true` on staging (fast feedback), manual sync on production (human approval gate). Use ArgoCD's "sync window" feature to restrict automatic syncs to off-peak hours in production. This combines GitOps automation benefits with the safety of change windows.
