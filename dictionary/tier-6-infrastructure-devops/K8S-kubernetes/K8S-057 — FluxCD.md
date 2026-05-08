---
layout: default
title: "FluxCD"
parent: "Kubernetes"
nav_order: 57
permalink: /kubernetes/fluxcd/
id: K8S-057
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["GitOps with Kubernetes", "Helm", "Kustomize", "RBAC (K8s)"]
used_by: ["GitOps with Kubernetes"]
related: ["GitOps with Kubernetes", "ArgoCD", "Helm Chart", "Kustomize"]
tags: [kubernetes, fluxcd, gitops, continuous-delivery, k8s, flux]
---

# FluxCD

## ⚡ TL;DR

**FluxCD** is a CNCF-graduated GitOps operator for Kubernetes. It uses controller-native CRDs: `GitRepository`, `Kustomization`, `HelmRelease`, `ImageAutomation`. Flux watches Git/Helm repos and reconciles the cluster. CLI-based, lightweight, naturally multi-tenant. The GitOps Toolkit (flux2) architecture is highly composable.

---

## 🔥 Problem This Solves

Same problem as ArgoCD: continuous delivery without push-based CI, drift detection, declarative cluster state from Git. FluxCD differentiates with CNCF graduation, CLI-native workflow, automatic image update automation (commit new image tag to Git automatically), and composable controller architecture.

---

## 📘 Textbook Definition

FluxCD is a CNCF-graduated, pull-based GitOps operator. Its GitOps Toolkit consists of specialized controllers (source, kustomize, helm, image, notification) that compose into a complete GitOps pipeline. Flux reconciles cluster state with desired state in Git and OCI repositories.

---

## ⏱️ 30 Seconds

```bash
# Bootstrap Flux on cluster (GitHub)
flux bootstrap github \
  --owner=myorg \
  --repository=gitops-repo \
  --branch=main \
  --path=clusters/production \
  --personal

# This:
# 1. Creates flux-system namespace + controllers
# 2. Creates GitRepository watching your repo
# 3. Creates Kustomization applying clusters/production/
# 4. Commits Flux install manifests to your repo
```

---

## 🔩 First Principles

- **GitOps Toolkit**: 5 separate controllers, each a focused reconcile loop
- **Source controller**: fetches Git/Helm/OCI repos → generates Artifacts
- **Kustomize controller**: applies Kustomize directories using Artifacts
- **Helm controller**: manages HelmRelease CRDs (install/upgrade/rollback)
- **Image Automation controller**: updates image tags in Git automatically
- **Notification controller**: sends alerts to Slack/PagerDuty; receives webhooks
- Everything is a CRD; `kubectl get all -n flux-system` shows all components

---

## 🧪 Thought Experiment

You push a new Docker image `my-app:sha-abc1234`. Without image automation: someone must manually update the Git repo with the new tag. With Flux ImageAutomation: Flux watches the container registry, detects the new tag matching pattern `main-*`, commits the updated image tag to Git automatically, which triggers another reconcile to deploy it. Full automation from push to deploy.

---

## 🧠 Mental Model / Analogy

FluxCD is like **a set of specialized couriers**: Source controller fetches the package (Git), Kustomize controller delivers Kustomize packages, Helm controller delivers Helm packages, Image automation controller checks for new package versions. Each courier is independent but they cooperate through shared Artifacts (staging area on a PVC).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Flux watches Git, applies changes. Bootstrap with `flux bootstrap`. Check status with `flux get all`.

**Level 2 — Practitioner**: `GitRepository` → source. `Kustomization` → applies path from source. `HelmRelease` → manages Helm chart. `flux reconcile` → trigger immediate reconcile.

**Level 3 — Advanced**: `dependsOn`: Kustomization dependency ordering (apps waits for infrastructure). `postBuild.substituteFrom`: variable substitution from ConfigMap/Secret into Kustomize manifests. SOPS decryption: `spec.decryption.provider: sops`. `interval` per resource: different poll rates for different sources.

**Level 4 — Expert**: Image Update Automation: `ImageRepository` (watch registry) + `ImagePolicy` (version filter: semver, regex) + `ImageUpdateAutomation` (commit policy). Multi-tenancy: Flux multi-tenancy lockdown — each team has their own namespace, `ServiceAccount`, and `Kustomization` pointing to team Git repo. `flux-multi-tenancy` blueprint. OCI sources: pull Helm charts and Kustomize configs directly from OCI registries (air-gapped environments). Webhook receiver: GitHub/GitLab webhook → instant reconcile instead of polling.

---

## ⚙️ How It Works

### Flux Architecture

```
                    [Git Repository]
                         ↓ (poll/webhook)
           [Source Controller]
              ├─ GitRepository (fetches git, stores artifact)
              ├─ HelmRepository (fetches helm index)
              └─ OCIRepository (fetches OCI artifact)
                         ↓ (artifact notification)
           ┌─────────────┼─────────────┐
           ↓             ↓             ↓
[Kustomize Controller] [Helm Controller] [Image Controller]
  Kustomization         HelmRelease       ImageRepository
  (apply YAML)         (helm install)    ImagePolicy
                                         ImageUpdateAutomation
                         ↓
           [Notification Controller]
              Alert, Provider, Receiver
```

### GitRepository + Kustomization

```yaml
# GitRepository: fetch source
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-gitops
  namespace: flux-system
spec:
  interval: 5m
  url: https://github.com/myorg/gitops-repo
  ref:
    branch: main
  secretRef:
    name: github-token # for private repos

---
# Kustomization: apply path from GitRepository
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-service
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: my-gitops
  path: ./clusters/production/apps/my-service
  prune: true
  decryption:
    provider: sops # decrypt SOPS-encrypted secrets
    secretRef:
      name: sops-age-key
  postBuild:
    substituteFrom:
      - kind: ConfigMap
        name: cluster-vars # substitution variables
```

### HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: my-app
  namespace: production
spec:
  interval: 15m
  chart:
    spec:
      chart: my-app
      version: ">=1.0.0 <2.0.0"
      sourceRef:
        kind: HelmRepository
        name: my-charts
        namespace: flux-system
  values:
    replicaCount: 3
  valuesFrom:
    - kind: Secret
      name: my-app-secrets # merge secrets into values
  install:
    remediation:
      retries: 3
  upgrade:
    remediation:
      remediateLastFailure: true
      retries: 3
```

### Image Update Automation

```yaml
# Watch container registry
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: my-app
spec:
  image: my-registry/my-app
  interval: 5m

---
# Policy: which tag to use
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: my-app
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    semver:
      range: ">=1.0.0" # or tag filter pattern

---
# Auto-commit new tag to Git
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageUpdateAutomation
metadata:
  name: my-app
spec:
  interval: 30m
  sourceRef:
    kind: GitRepository
    name: my-gitops
  git:
    commit:
      author:
        email: fluxbot@myorg.com
        name: FluxBot
      messageTemplate: |
        Auto-update my-app to {{range .Updated.Images}}{{println .}}{{end}}
  update:
    path: ./clusters/production
    strategy: Setters # uses # {"$imagepolicy": "..."}
```

---

## 🔄 E2E Flow: Image Update Pipeline

```
Developer pushes code → CI builds my-app:v1.3.0 → pushed to registry

Flux Image Controller (every 5m):
  → Checks my-registry/my-app for new tags
  → Detects v1.3.0 matches semver policy >=1.0.0
  → ImagePolicy: latest = v1.3.0

Image Update Automation (every 30m or immediate):
  → Finds marker in Git: # {"$imagepolicy": "flux-system:my-app"}
    # In deployment.yaml: image: my-registry/my-app:v1.2.0 # {"$imagepolicy": "flux-system:my-app"}
  → Updates to: image: my-registry/my-app:v1.3.0
  → Git commit + push: "Auto-update my-app to v1.3.0"

GitRepository Source (webhook/5m polling):
  → Detects new commit
  → Fetches new state

Kustomization controller:
  → Renders Kustomize with new image tag
  → Applies Deployment to cluster
  → Rolling update: v1.2.0 → v1.3.0

Notification:
  → Slack: "my-app updated to v1.3.0 in production ✅"
```

---

## ⚖️ Comparison Table

|                          | FluxCD                    | ArgoCD                   |
| ------------------------ | ------------------------- | ------------------------ |
| **CNCF status**          | Graduated                 | Incubating               |
| **Web UI**               | ❌ (use CLI/Grafana)      | ✅ Rich UI               |
| **Image automation**     | ✅ Built-in               | Via argocd-image-updater |
| **Multi-tenancy**        | ✅ Native namespace model | Via Projects             |
| **Bootstrap**            | `flux bootstrap` CLI      | Helm install             |
| **OCI support**          | ✅                        | ✅                       |
| **Progressive delivery** | Flagger                   | Argo Rollouts            |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                        |
| ---------------------------------------- | ------------------------------------------------------------------------------ |
| "FluxCD has no UI"                       | Grafana dashboards available; Weave GitOps (OSS) adds UI                       |
| "FluxCD is harder to use than ArgoCD"    | Flux is CLI-native; ArgoCD has a UI; complexity depends on workflow preference |
| "Flux requires a specific Git structure" | Flux is flexible; any Kustomize/Helm/YAML structure works                      |
| "prune: true always deletes resources"   | Prune only deletes resources previously owned by that Kustomization            |

---

## 🚨 Failure Modes

| Failure                      | Symptom                        | Fix                                                               |
| ---------------------------- | ------------------------------ | ----------------------------------------------------------------- |
| GitRepository auth fails     | `failed to clone`              | Check git secret (SSH key or token)                               |
| HelmRelease install fails    | `status: failed` after retries | `flux get helmrelease`; check Helm errors with `flux logs`        |
| SOPS decryption fails        | `decryption failed`            | Check SOPS key in secret; key age must match                      |
| ImageUpdateAutomation stalls | No git commits for new tags    | Check ImagePolicy matches tag format; check git write permissions |

---

## 🔗 Related Keywords

- [GitOps with Kubernetes](/kubernetes/gitops-with-kubernetes/) — paradigm Flux implements
- [ArgoCD](/kubernetes/argocd/) — alternative GitOps operator with UI
- [Helm Chart](/kubernetes/helm-chart/) — managed by HelmRelease
- [Kustomize](/kubernetes/kustomize/) — managed by Kustomization

---

## 📌 Quick Reference Card

```bash
# Bootstrap
flux bootstrap github --owner=<org> --repository=<repo> --path=clusters/prod

# Check status
flux get all -n flux-system
flux get kustomizations
flux get helmreleases -A

# Force reconcile
flux reconcile source git my-gitops
flux reconcile kustomization my-service

# Check logs
flux logs --all-namespaces --follow --level=error

# Suspend/resume (maintenance mode)
flux suspend kustomization my-service
flux resume kustomization my-service

# Export (show all Flux resources)
flux export all -n flux-system

# Trace an image
flux get image repository my-app
flux get image policy my-app
```

---

## 🧠 Think About This

The choice between Flux and ArgoCD often comes down to team preference and workflow. ArgoCD wins for teams that value visual oversight (the web UI showing 50 apps at once in red/green status is invaluable for an SRE team during incidents). Flux wins for platform engineers who prefer code-native, composable tools (each controller is independently upgradeable, testable). Many large organizations use both: Flux for infrastructure layer (CRD installation, cert-manager, Prometheus), ArgoCD for application layer. The key insight: these are not mutually exclusive, and both implement the same GitOps reconcile loop.
