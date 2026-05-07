---
layout: default
title: "Helm"
parent: "Kubernetes"
nav_order: 32
permalink: /kubernetes/helm/
number: "K8S-032"
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["kubectl", "Deployment", "ConfigMap", "Secret"]
used_by: ["Helm Chart", "Kustomize", "GitOps with Kubernetes", "ArgoCD"]
related:
  ["Helm Chart", "Kustomize", "kubectl", "ArgoCD", "GitOps with Kubernetes"]
tags: [kubernetes, helm, package-manager, charts, k8s, deployment]
---

# Helm

## ⚡ TL;DR

Helm is the **package manager for Kubernetes**. Charts bundle all Kubernetes YAML for an app (Deployment, Service, ConfigMap, etc.) with templating and versioning. `helm install` deploys a chart; `helm upgrade` updates it; `helm rollback` reverts. Think: `apt/brew` for Kubernetes.

---

## 🔥 Problem This Solves

Deploying a complex app (Nginx, PostgreSQL, Prometheus) requires 10+ Kubernetes YAML files. Customizing them per environment requires manual editing. Helm packages them into charts with templating (values.yaml), versioning, and lifecycle management.

---

## 📘 Textbook Definition

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. It uses charts (packages of pre-configured Kubernetes resources) with Go templates to enable parameterized, versioned application deployments.

---

## ⏱️ 30 Seconds

```bash
# Add a chart repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install a chart
helm install my-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --values my-values.yaml

# List releases
helm list -A

# Upgrade
helm upgrade my-nginx ingress-nginx/ingress-nginx --values my-values.yaml

# Rollback
helm rollback my-nginx 1

# Uninstall
helm uninstall my-nginx
```

---

## 🔩 First Principles

- **Chart** = directory of YAML templates + values.yaml + Chart.yaml (metadata)
- **Release** = an instance of a chart installed in a cluster (can install same chart multiple times)
- **Values** = configuration passed to templates; override with `--values` or `--set key=value`
- **Repository** = HTTP server hosting packaged charts (ArtifactHub.io is the central registry)
- Helm 3 (current): no Tiller, RBAC-native, release stored as Secrets in cluster

---

## 🧪 Thought Experiment

Your team needs to deploy the same app to dev, staging, and prod with different replica counts, image tags, and database URLs. Without Helm: three copies of 10 YAML files, manual editing, copy-paste errors. With Helm: one chart, three `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml` files. `helm upgrade --install my-app ./chart --values values-prod.yaml`.

---

## 🧠 Mental Model / Analogy

Helm is like **macOS Homebrew**: `brew install redis` = `helm install redis bitnami/redis`. Charts are like formulae — someone has packaged the software with sensible defaults. You customize via values; Homebrew handles installation and upgrades.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Helm installs complex apps with one command. `helm install my-postgres bitnami/postgresql`.

**Level 2 — Practitioner**: Customize with `--values values.yaml` or `--set key=value`. `helm upgrade` applies changes. `helm rollback` reverts. `helm status` shows what's deployed.

**Level 3 — Advanced**: Create your own chart: `helm create my-chart`. Template functions: `{{ .Values.replicas }}`, `{{ include "chart.name" . }}`, `{{ if .Values.ingress.enabled }}`. Dependencies: `Chart.yaml` dependencies block with `helm dependency update`.

**Level 4 — Expert**: Helm hooks: `pre-install`, `post-install`, `pre-upgrade`, `pre-delete` — execute Jobs at lifecycle events (e.g., db migration as pre-upgrade hook). Tests: `helm test` runs test Pods. OCI registry support: `helm push/pull` from OCI-compliant registries (AWS ECR, GCR). `helm plugin` ecosystem (helm-diff, helm-secrets, helm-docs).

---

## ⚙️ How It Works

### Chart Structure

```
my-app/
  Chart.yaml        # name, version, appVersion, dependencies
  values.yaml       # default values
  templates/
    deployment.yaml
    service.yaml
    ingress.yaml
    configmap.yaml
    _helpers.tpl    # named templates and helper functions
  charts/           # subcharts (dependencies)
```

### Template Example

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: { { include "my-app.fullname" . } }
  labels: { { - include "my-app.labels" . | nindent 4 } }
spec:
  replicas: { { .Values.replicaCount } }
  selector:
    matchLabels: { { - include "my-app.selectorLabels" . | nindent 6 } }
  template:
    spec:
      containers:
        - name: { { .Chart.Name } }
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          resources: { { - toYaml .Values.resources | nindent 10 } }
```

### values.yaml

```yaml
replicaCount: 3
image:
  repository: my-registry/my-app
  tag: "1.2.0"
  pullPolicy: IfNotPresent
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    memory: 512Mi
ingress:
  enabled: true
  host: api.example.com
```

---

## 🔄 E2E Flow: Helm Install

```
helm install my-app ./my-chart --values values-prod.yaml
  → Render templates: merge values.yaml + values-prod.yaml
  → Substitute {{ .Values.* }} with final values
  → Apply rendered YAML to API Server (like kubectl apply)
  → Store release state as Secret in cluster namespace
  → helm list shows: my-app, deployed, revision 1

helm upgrade my-app ./my-chart --values values-prod.yaml
  → Re-render templates
  → Apply changes to cluster
  → Increment revision: 2
  → Previous release stored for rollback

helm rollback my-app 1
  → Retrieve revision 1 from Secret
  → Apply to cluster
  → Revision 3 (rollback is also a revision)
```

---

## ⚖️ Comparison Table

|                     | Helm                          | Kustomize               | Raw kubectl           |
| ------------------- | ----------------------------- | ----------------------- | --------------------- |
| **Templating**      | Go templates                  | Overlays (no templates) | None                  |
| **Versioning**      | Chart versions + app versions | None (Git history)      | None                  |
| **Rollback**        | `helm rollback`               | Git revert + apply      | Manual                |
| **Package sharing** | Helm repositories             | None                    | None                  |
| **Complexity**      | Medium                        | Low                     | High for complex apps |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                               |
| ------------------------------------- | ------------------------------------------------------------------------------------- |
| "Helm is always better than raw YAML" | For simple apps, Helm adds complexity; raw YAML or Kustomize is simpler               |
| "Helm manages Kubernetes RBAC"        | Helm installs RBAC resources but doesn't manage cluster-level security                |
| "helm install is idempotent"          | Use `helm upgrade --install` for idempotency (create if not exists, update if exists) |
| "Helm 3 requires Tiller"              | Helm 3 removed Tiller; direct client-to-API Server without server component           |

---

## 🚨 Failure Modes

| Failure                            | Symptom                                   | Fix                                          |
| ---------------------------------- | ----------------------------------------- | -------------------------------------------- | ------------------------- | ---------------- |
| Template render error              | `helm install` fails before applying      | `helm template --debug` to see rendered YAML |
| Release stuck in "pending-upgrade" | upgrade blocked                           | `helm rollback` or `helm uninstall`          |
| Values type mismatch               | Unexpected template output                | Use `                                        | quote`for string values;` | int` for numbers |
| Chart version conflicts            | Helm install fails with API version error | Update chart to support current K8s version  |

---

## 🔗 Related Keywords

- [Helm Chart](/kubernetes/helm-chart/) — the chart package structure
- [Kustomize](/kubernetes/kustomize/) — alternative to Helm templating
- [ArgoCD](/kubernetes/argocd/) — GitOps tool that deploys Helm charts
- [GitOps with Kubernetes](/kubernetes/gitops-with-kubernetes/) — Helm in GitOps workflows

---

## 📌 Quick Reference Card

```bash
# Search for charts
helm search hub postgresql
helm search repo bitnami/

# Inspect chart before installing
helm show values bitnami/postgresql
helm show chart bitnami/postgresql

# Dry run (show what would be applied)
helm install my-app ./chart --dry-run --debug

# Diff before upgrade (helm-diff plugin)
helm diff upgrade my-app ./chart --values values.yaml

# Get values of deployed release
helm get values my-app

# List all releases including failed
helm list -A --all

# Lint chart
helm lint ./my-chart
```

---

## 🧠 Think About This

When should you write a Helm chart vs use Kustomize? Helm shines for reusable, shareable charts with many configuration dimensions (Bitnami charts). Kustomize shines for environment-specific overlays of existing Kubernetes YAML where you own the base manifests. Many teams use both: Helm for third-party apps, Kustomize for their own apps. ArgoCD supports both deployment models natively.
