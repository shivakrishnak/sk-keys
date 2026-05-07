---
layout: default
title: "Kustomize"
parent: "Kubernetes"
nav_order: 34
permalink: /kubernetes/kustomize/
number: "K8S-034"
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["kubectl", "Deployment", "ConfigMap"]
used_by: ["GitOps with Kubernetes", "ArgoCD", "FluxCD"]
related: ["Helm", "Helm Chart", "kubectl", "ArgoCD", "GitOps with Kubernetes"]
tags: [kubernetes, kustomize, configuration-management, overlays, k8s, gitops]
---

# Kustomize

## ⚡ TL;DR

Kustomize is a **template-free Kubernetes configuration management tool** built into kubectl. It uses a `base/` of YAML + `overlays/` (patches per environment) without templates. `kubectl apply -k ./overlays/prod` applies the merged result. No variables, no templates — pure YAML patching.

---

## 🔥 Problem This Solves

You have the same Deployment for dev/staging/prod but with different replica counts, image tags, and resource limits. Maintaining three copies invites drift. Helm templates add complexity. Kustomize overlays patch a shared base without duplication or templating language.

---

## 📘 Textbook Definition

Kustomize is a Kubernetes-native configuration management tool that provides a way to customize application configuration without modifying original YAML files. It uses overlays with patches to layer environment-specific configuration on top of a common base.

---

## ⏱️ 30 Seconds

```
base/
  kustomization.yaml
  deployment.yaml
  service.yaml

overlays/prod/
  kustomization.yaml  ← references base, applies patches
  replicas-patch.yaml ← scale to 5 replicas
  image-patch.yaml    ← set prod image tag
```

```bash
# Apply prod overlay
kubectl apply -k overlays/prod

# Preview rendered YAML
kubectl kustomize overlays/prod
```

---

## 🔩 First Principles

- Kustomize generates final Kubernetes YAML by merging base + patches
- **No templates**: patches are valid YAML (strategic merge patch or JSON 6902 patch)
- `kustomization.yaml` is the manifest: declares resources, patches, transformers
- Patches: strategic merge patch (same YAML structure as original, merged deeply) or JSON Patch (RFC 6902, explicit path operations)
- Built into kubectl 1.14+: `kubectl apply -k` works without installing anything

---

## 🧪 Thought Experiment

Your base Deployment has 1 replica for dev. For prod you need 5 replicas, a different image tag, and `resources.limits.memory: 1Gi`. With Kustomize overlays, you write 3 small patch files for prod. The base stays unchanged. When you need to update the base (add a new env variable), you change it once — all overlays inherit it automatically.

---

## 🧠 Mental Model / Analogy

Kustomize is like **Git patches**: the base is the main branch, overlays are patches. A prod patch says "for this file, change these lines." The final result is base + patch applied. Unlike Git patches which work on text, Kustomize patches work on structured YAML and understand Kubernetes objects.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Kustomize has a `base/` (shared YAML) and `overlays/` (per-environment changes). kubectl applies the merged result.

**Level 2 — Practitioner**: `kustomization.yaml` in base lists `resources:`. Overlay `kustomization.yaml` references `bases:` and lists `patches:`. `images:` transformer overrides image tags globally without patching.

**Level 3 — Advanced**: Strategic merge patch: same YAML structure as target, only differing fields needed. JSON 6902 patch: precise path operations (`replace`, `add`, `remove`). `configMapGenerator` and `secretGenerator`: generate ConfigMap/Secret from files with hash suffix for auto-rolling updates. `namePrefix`/`nameSuffix`: prepend/append to all resource names.

**Level 4 — Expert**: `transformers:` section: apply common labels, annotations, namespace. `generators:` for custom resource generation via plugins. Component Kustomize: reusable kustomization snippets (e.g., RBAC module). Kustomize with GitOps: FluxCD and ArgoCD both natively support `kubectl kustomize`-compatible directories.

---

## ⚙️ How It Works

### Directory Structure

```
my-app/
  base/
    kustomization.yaml
    deployment.yaml
    service.yaml
  overlays/
    dev/
      kustomization.yaml
      replica-patch.yaml
    prod/
      kustomization.yaml
      replica-patch.yaml
      resources-patch.yaml
```

### base/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
commonLabels:
  app: my-app
```

### overlays/prod/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base

# Override image tag
images:
  - name: my-registry/my-app
    newTag: "v2.0.1"

# Apply patches
patches:
  - path: replica-patch.yaml
  - path: resources-patch.yaml

# Add prod-specific namespace
namespace: production
```

### Strategic Merge Patch (replica-patch.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 5 # override replicas
  template:
    spec:
      containers:
        - name: my-app
          resources:
            requests:
              memory: 512Mi
            limits:
              memory: 1Gi
```

### JSON 6902 Patch (resources-patch.yaml)

```yaml
- op: replace
  path: /spec/replicas
  value: 5
- op: add
  path: /spec/template/spec/containers/0/env/-
  value:
    name: ENV
    value: production
```

### ConfigMap Generator (auto-rolling updates)

```yaml
# kustomization.yaml
configMapGenerator:
  - name: app-config
    files:
      - application.properties
    literals:
      - LOG_LEVEL=INFO
```

→ Creates `app-config-<hash>` ConfigMap. Deployment references it by base name; Kustomize resolves to hashed name. New config = new hash = rolling update triggered automatically.

---

## 🔄 E2E Flow: kubectl apply -k

```
kubectl apply -k overlays/prod/
  → Read overlays/prod/kustomization.yaml
  → Load base resources (../../base)
  → Apply transformers (namespace, labels, images)
  → Apply patches (strategic merge + JSON 6902)
  → Resolve configMapGenerator/secretGenerator
  → Final merged YAML → API Server (kubectl apply)
```

---

## ⚖️ Comparison Table

|                                           | Kustomize         | Helm                 |
| ----------------------------------------- | ----------------- | -------------------- |
| **Templating**                            | No (patches only) | Go templates         |
| **Learning curve**                        | Low               | Moderate             |
| **Complexity for simple env differences** | Low               | High                 |
| **Third-party charts**                    | Not applicable    | Helm Hub/ArtifactHub |
| **Versioning**                            | Git history       | Chart versions       |
| **kubectl integration**                   | Built-in          | Separate CLI         |

---

## ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                            |
| ----------------------------------------------- | ---------------------------------------------------------------------------------- |
| "Kustomize is only for environment differences" | Also used for namespace injection, label standardization, image tag management     |
| "Kustomize doesn't support templating at all"   | True — it's a feature, not a bug; use vars sparingly for cross-resource references |
| "Kustomize can't manage secrets securely"       | Use `secretGenerator` + SOPS or External Secrets Operator for secure secrets       |
| "Helm replaces Kustomize"                       | Many teams use both: Helm for 3rd-party, Kustomize for own apps                    |

---

## 🚨 Failure Modes

| Failure                            | Symptom                                | Fix                                                                           |
| ---------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------- |
| Patch targets wrong resource       | Patch not applied silently             | Ensure `name`, `kind`, `apiVersion` in patch match target exactly             |
| Strategic merge removes list items | Array fields clobbered                 | Use `$patch: replace` directive or JSON 6902 patch                            |
| ConfigMap hash mismatch            | App not rolling after config change    | Ensure Deployment references ConfigMap by base name (Kustomize resolves hash) |
| Overlay base path wrong            | `build error: must build at directory` | Check relative path in `bases:`                                               |

---

## 🔗 Related Keywords

- [Helm](/kubernetes/helm/) — alternative with full templating
- [ArgoCD](/kubernetes/argocd/) — GitOps tool supporting Kustomize natively
- [FluxCD](/kubernetes/fluxcd/) — GitOps tool with Kustomize controller
- [GitOps with Kubernetes](/kubernetes/gitops-with-kubernetes/) — Kustomize in GitOps pipelines

---

## 📌 Quick Reference Card

```bash
# Preview final YAML (no apply)
kubectl kustomize ./overlays/prod

# Apply
kubectl apply -k ./overlays/prod

# Delete
kubectl delete -k ./overlays/prod

# Validate patch structure
kubectl kustomize ./overlays/prod | kubectl apply --dry-run=server -f -

# Update image tag without editing files
cd overlays/prod
kustomize edit set image my-registry/my-app:v3.0.0

# Set namespace
kustomize edit set namespace production
```

---

## 🧠 Think About This

The `configMapGenerator` + hash suffix pattern solves a real problem: Kubernetes doesn't roll Deployments when a ConfigMap changes (only when the Pod spec changes). By appending a content hash to the ConfigMap name, Kustomize ensures every config change creates a new ConfigMap name, which changes the Deployment spec, which triggers a rolling update. This is the correct, idiomatic way to handle config-driven rolling updates in Kubernetes — no annotations, no manual triggers needed.
