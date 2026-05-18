---
version: 1
layout: default
title: "Helm Chart"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/kubernetes/helm-chart/
id: K8S-027
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Helm", "Deployment", "ConfigMap"]
used_by: ["Helm", "ArgoCD", "GitOps with Kubernetes"]
related: ["Helm", "Kustomize", "ArgoCD", "GitOps with Kubernetes"]
tags: [kubernetes, helm-chart, chart, templates, values, k8s]
---

## ⚡ TL;DR

A Helm **Chart** is a directory of Kubernetes YAML templates + `values.yaml` (defaults) + `Chart.yaml` (metadata). Charts are the unit of distribution for Kubernetes applications. `helm package` bundles it as `.tgz`; repositories host and distribute charts.

---

## 🔥 Problem This Solves

A microservice needs a Deployment, Service, Ingress, ConfigMap, and HPA - 5 YAML files. Sharing and reusing this across teams, environments, and clusters requires packaging. A Helm Chart is that package.

---

## 📘 Textbook Definition

A Helm chart is a collection of files that describe a related set of Kubernetes resources. A single chart might be used to deploy something simple (like a pod), or something complex (like a full web app stack with HTTP servers, databases, caches, and queues).

---

## ⏱️ 30 Seconds

```
my-app/
  Chart.yaml         ← name, version, description
  values.yaml        ← default configuration values
  templates/
    deployment.yaml  ← {{ .Values.replicas }} etc
    service.yaml
    ingress.yaml
    _helpers.tpl     ← named template functions
  charts/            ← dependency subcharts
  .helmignore        ← files to exclude from packaging
```

---

## 🔩 First Principles

- Templates are Go templates with Helm extensions (Sprig functions)
- `{{ .Values.key }}` = replace with value from values.yaml (overridable)
- `{{ .Release.Name }}` = the Helm release name
- `{{ .Chart.Version }}` = chart version from Chart.yaml
- `{{ include "helper" . }}` = call named template from `_helpers.tpl`
- `_helpers.tpl` defines reusable template functions (name, labels, etc.)

---

## 🧪 Thought Experiment

You create a Helm chart for your Spring Boot API. Dev uses 1 replica, 256Mi; prod uses 5 replicas, 1Gi. The chart template is identical - only `values-dev.yaml` and `values-prod.yaml` differ. You package the chart once and publish it to your internal Helm repo. Every team member and CI pipeline deploys the same chart with environment-appropriate values.

---

## 🧠 Mental Model / Analogy

A Helm chart is like a **furniture assembly kit**: all pieces (YAML templates) + instructions (templates logic) + customization options (values.yaml). The same kit assembles a small desk (dev) or large desk (prod) by changing a few parameters. The kit is reusable; the furniture (deployment) varies.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: A chart is a zip file of Kubernetes YAML with configurable parameters.

**Level 2 - Practitioner**: `Chart.yaml` defines name, version, appVersion. `values.yaml` is the default config. Override with `--values` or `--set`. `templates/` contains YAML with `{{ }}` placeholders.

**Level 3 - Advanced**: `_helpers.tpl`: `{{- define "my-app.labels" -}}...{{- end }}`. Used via `{{- include "my-app.labels" . | nindent 4 }}`. Chart dependencies (`Chart.yaml` dependencies block): `helm dependency update` pulls subchart `.tgz` into `charts/`.

**Level 4 - Expert**: Helm hooks: `metadata.annotations: "helm.sh/hook": pre-upgrade` runs a Job before upgrade (database migration pattern). Library charts (`type: library`): pure helpers, no deployable templates. CRD installation: `crds/` directory installs CRDs before regular templates. `helm test`: test Pods run after install to verify deployment.

---

## ⚙️ How It Works

---

### Chart.yaml

```yaml
apiVersion: v2
name: my-app
description: My Spring Boot API
type: application # application or library
version: 1.2.3 # chart version (semantic versioning)
appVersion: "2.0.1" # app version (informational)
dependencies:
  - name: postgresql
    version: "12.5.6"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

---

### Comprehensive values.yaml

```yaml
replicaCount: 2

image:
  repository: registry.example.com/my-app
  tag: "" # defaults to Chart.appVersion
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx
  host: api.example.com
  tls: true

resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    memory: 512Mi

postgresql:
  enabled: true
  auth:
    database: mydb
```

---

### \_helpers.tpl Pattern

```
{{/*
Expand the name of the chart.
*/}}
{{- define "my-app.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "my-app.name" .)
  | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ include "my-app.chart" . }}
{{ include "my-app.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

---

### Pre-upgrade Hook (DB Migration)

```yaml
# templates/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-migration
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migration
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        command: ["./migrate.sh"]
```

---

## 🔄 E2E Flow: Chart Development

```
helm create my-app
  → Scaffold: Chart.yaml, values.yaml, templates/

Edit templates/ and values.yaml

helm lint ./my-app     → check for errors
helm template ./my-app → preview rendered YAML
helm install test-release ./my-app --dry-run --debug

helm package ./my-app  → my-app-1.2.3.tgz
helm repo index .      → index.yaml for repository

# Push to OCI registry
helm push my-app-1.2.3.tgz
  oci://registry.example.com/charts
```

---

## ⚖️ Comparison Table

|                    | Helm Chart          | Kustomize Base | Raw YAML |
| ------------------ | ------------------- | -------------- | -------- |
| **Templating**     | Go templates        | Patches only   | None     |
| **Versioned**      | ✅ (chart versions) | No (Git)       | No       |
| **Reusable**       | ✅ (helm repo)      | Manual copying | Manual   |
| **Complexity**     | Medium              | Low            | Low      |
| **Learning curve** | Moderate            | Low            | Low      |

---

## ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                 |
| --------------------------------------- | ----------------------------------------------------------------------- |
| "`version` in Chart.yaml = app version" | `version` = chart version; `appVersion` = app version (independent)     |
| "Charts must be in a repo to use"       | Can install from local directory: `helm install my-app ./my-app/`       |
| "values.yaml is immutable"              | values.yaml is defaults; any value can be overridden at install/upgrade |
| "chart version must match app version"  | They're independent; many chart versions may package same app version   |

---

## 🚨 Failure Modes

| Failure                   | Symptom                             | Fix                                                     |
| ------------------------- | ----------------------------------- | ------------------------------------------------------- |
| Template syntax error     | `helm install` fails: `parse error` | `helm lint`; `helm template --debug`                    |
| Missing required value    | Empty string in template output     | Use `{{ required "error message" .Values.key }}`        |
| Hook timeout              | Release stuck in pending-upgrade    | Set `activeDeadlineSeconds` on hook Jobs                |
| Subchart version conflict | Dependency pull fails               | Run `helm dependency update`; check version constraints |

---

## 🔗 Related Keywords

- [Helm](/kubernetes/helm/) - the CLI tool that uses charts
- [Kustomize](/kubernetes/kustomize/) - alternative to chart templating
- [ArgoCD](/kubernetes/argocd/) - GitOps deployment of Helm charts
- [GitOps with Kubernetes](/kubernetes/gitops-with-kubernetes/) - charts in GitOps pipelines

---

## 📌 Quick Reference Card

```bash
# Create chart scaffold
helm create my-app

# Lint
helm lint ./my-app

# Render templates (no install)
helm template my-release ./my-app --values values-prod.yaml

# Package chart
helm package ./my-app

# Check chart structure
helm show chart ./my-app
helm show values ./my-app

# Upgrade with new values
helm upgrade my-release ./my-app \
  --values values-prod.yaml \
  --set image.tag=2.0.1

# Get rendered manifests of deployed release
helm get manifest my-release
```

---

## 🧠 Think About This

Semantic versioning for Helm charts has a subtle convention: bump `version` (chart version) whenever the chart templates or defaults change - even if the app version hasn't changed. Bump `appVersion` when the container image version changes. This lets chart consumers understand "I need chart version 2.x.x" (new required field) vs "I need app version 2.0" (new features). GitOps tools like ArgoCD track chart versions for automated upgrades - correct versioning drives correct automation.
