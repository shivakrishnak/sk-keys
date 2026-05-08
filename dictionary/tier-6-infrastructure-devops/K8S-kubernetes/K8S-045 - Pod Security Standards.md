---
layout: default
title: "Pod Security Standards"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /kubernetes/pod-security-standards/
id: K8S-045
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Pod", "Namespace (K8s)", "Admission Controllers", "RBAC (K8s)"]
used_by: ["K8s Security Hardening", "Admission Controllers"]
related:
  [
    "Admission Controllers",
    "RBAC (K8s)",
    "K8s Security Hardening",
    "Network Policy",
  ]
tags: [kubernetes, pod-security, security, pss, restricted, k8s]
---

# Pod Security Standards

## ⚡ TL;DR

Pod Security Standards (PSS) define **three security profiles** for Pods: `Privileged` (unrestricted), `Baseline` (prevent common exploits), `Restricted` (hardened). Enforced via namespace labels on the built-in `PodSecurity` admission controller (K8s 1.25+). Replaces the deprecated PodSecurityPolicy (PSP).

---

## 🔥 Problem This Solves

Misconfigured Pods running as root, with hostPID, or mounting hostPath can escape the container and compromise the node. PSS provides three ready-made security profiles that prevent these misconfigurations, enforced automatically at the namespace level.

---

## 📘 Textbook Definition

Pod Security Standards define three security profiles - Privileged, Baseline, and Restricted - that cover the security spectrum from unrestricted to hardened. They are enforced via the PodSecurity admission controller using namespace-level labels with enforce, audit, and warn modes.

---

## ⏱️ 30 Seconds

```bash
# Apply restricted profile to namespace (enforce + warn)
kubectl label namespace my-app \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=v1.29 \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/warn-version=v1.29 \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/audit-version=v1.29
```

---

## 🔩 First Principles

- PSS enforced by `PodSecurity` admission plugin (built-in, enabled by default in 1.23+)
- **Three profiles**: Privileged (no restrictions), Baseline (prevent known escapes), Restricted (follows hardening best practices)
- **Three modes**: `enforce` (reject), `warn` (user warning), `audit` (log in audit events)
- Set per-namespace via labels, so different namespaces can have different security levels
- PSS replaced PSP (PodSecurityPolicy) - removed in K8s 1.25

---

## 🧪 Thought Experiment

You label your `production` namespace with `enforce=restricted`. A developer deploys a Pod with `securityContext.runAsRoot: true`. The Pod is rejected immediately with a clear error explaining which policy it violated. The developer fixes the Pod spec. Compare to no PSS: the Pod runs as root silently, creating a security debt discovered months later in a penetration test.

---

## 🧠 Mental Model / Analogy

PSS profiles are like **building codes**: Privileged = no code (anything goes), Baseline = minimum building code (no fire hazards), Restricted = highest standard (earthquake-resistant, energy-efficient). Namespaces choose their code level. Running `kube-system` needs Privileged; your app should aim for Restricted.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: PSS has three security levels. Label your namespace to enforce a security level on all Pods in it.

**Level 2 - Practitioner**: Privileged = everything allowed. Baseline = no hostPID, no hostNetwork, no privileged containers, no unsafe capabilities, no hostPath volumes. Restricted = Baseline + must run as non-root, must drop ALL capabilities, seccompProfile required.

**Level 3 - Advanced**: Use `audit` mode first to discover violations before enforcing. `warn` mode shows warnings on `kubectl apply`. Version pin (`-version=v1.29`) ensures consistent behavior across K8s upgrades. Exemptions: `kube-system` namespace typically needs Privileged exemption.

**Level 4 - Expert**: PSS is coarse-grained (namespace level). For fine-grained policies per Pod/Deployment, use Kyverno or OPA/Gatekeeper. `kubectl-convert` to migrate PSP to PSS + Kyverno. `kubectl label --dry-run=server` to test what would be rejected before applying labels. `--privileged-namespace` flag on kubeadm for system namespaces.

---

## ⚙️ How It Works

### Three Profiles Compared

**Privileged**: No restrictions. Used by: `kube-system`, CNI plugins, DaemonSets for node management.

**Baseline** (blocks common privilege escalations):

```yaml
# These are FORBIDDEN in Baseline:
spec:
  hostPID: true # FORBIDDEN
  hostIPC: true # FORBIDDEN
  hostNetwork: true # FORBIDDEN
  containers:
    - securityContext:
        privileged: true # FORBIDDEN
        allowPrivilegeEscalation: true # FORBIDDEN
        capabilities:
          add: ["NET_ADMIN", "SYS_ADMIN"] # FORBIDDEN
      hostPort: 8080 # FORBIDDEN
  volumes:
    - hostPath: # FORBIDDEN
        path: /etc
```

**Restricted** (Baseline + hardening):

```yaml
# All Baseline restrictions PLUS these requirements:
spec:
  containers:
    - securityContext:
        runAsNonRoot: true # REQUIRED
        runAsUser: 1000 # should be non-zero
        allowPrivilegeEscalation: false # REQUIRED
        seccompProfile: # REQUIRED
          type: RuntimeDefault
        capabilities:
          drop: ["ALL"] # REQUIRED
          add: ["NET_BIND_SERVICE"] # only this add allowed
```

### Compliant Pod for Restricted Namespace

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: compliant-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: my-app:latest
      securityContext:
        allowPrivilegeEscalation: false
        runAsNonRoot: true
        capabilities:
          drop: ["ALL"]
      resources:
        requests:
          memory: 256Mi
          cpu: 100m
        limits:
          memory: 512Mi
```

### Namespace Labels

```bash
# Start with audit (no rejections, just logging)
kubectl label namespace my-app \
  pod-security.kubernetes.io/audit=restricted

# Then add warn (user sees warnings)
kubectl label namespace my-app \
  pod-security.kubernetes.io/warn=restricted

# Finally enforce (rejects non-compliant Pods)
kubectl label namespace my-app \
  pod-security.kubernetes.io/enforce=restricted

# Check current labels
kubectl get namespace my-app --show-labels
```

---

## 🔄 E2E Flow: PSS Enforcement

```
kubectl apply -f deployment.yaml (namespace: my-app, enforce=restricted)
  → PodSecurity admission controller:
      1. Extract pod template from Deployment
      2. Evaluate against restricted profile:
         - runAsNonRoot? ✅
         - allowPrivilegeEscalation: false? ❌ MISSING
      3. Reject with error:
         "pods 'my-app-xxx' is forbidden: violates PodSecurity 'restricted:v1.29':
          allowPrivilegeEscalation != false (container 'app' must set
          securityContext.allowPrivilegeEscalation=false)"
  → Developer sees error, fixes securityContext
  → kubectl apply again → admission passes → stored in etcd
```

---

## ⚖️ Comparison Table

|                           | Privileged       | Baseline          | Restricted              |
| ------------------------- | ---------------- | ----------------- | ----------------------- |
| **hostPID/hostNetwork**   | ✅               | ❌                | ❌                      |
| **Privileged containers** | ✅               | ❌                | ❌                      |
| **Run as root**           | ✅               | ✅ (allowed)      | ❌                      |
| **Capabilities**          | Any              | No dangerous caps | Drop ALL                |
| **Seccomp**               | Optional         | Optional          | Required                |
| **Use case**              | kube-system, CNI | Default apps      | Security-sensitive apps |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                      |
| ----------------------------------- | ---------------------------------------------------------------------------- |
| "PSS replaces all security tools"   | PSS is coarse-grained; Kyverno/OPA add fine-grained per-resource policies    |
| "kube-system should use restricted" | kube-system needs Privileged; CNI/DaemonSets require host access             |
| "PSS audits are visible to kubectl" | Audit events go to audit log, not kubectl output; warn mode sends to kubectl |
| "PSP and PSS are compatible"        | PSP was removed in 1.25; migrate to PSS + Kyverno/Gatekeeper                 |

---

## 🚨 Failure Modes

| Failure                           | Symptom                        | Fix                                                         |
| --------------------------------- | ------------------------------ | ----------------------------------------------------------- |
| kube-system labeled restricted    | Control plane pods rejected    | kube-system must stay Privileged                            |
| Legacy images run as root         | Pods rejected in restricted NS | Update Dockerfile: `USER 1000`; fix securityContext         |
| readOnlyRootFilesystem breaks app | App can't write temp files     | Mount tmpfs volume for /tmp                                 |
| NET_BIND_SERVICE needed           | Port < 1024 app fails          | Use port > 1024 in container; use Service for external port |

---

## 🔗 Related Keywords

- [Admission Controllers](/kubernetes/admission-controllers/) - PodSecurity is a built-in admission controller
- [K8s Security Hardening](/kubernetes/k8s-security-hardening/) - PSS as one layer
- [RBAC (K8s)](/kubernetes/rbac-k8s/) - controls who deploys what
- [Network Policy](/kubernetes/network-policy/) - complements PSS for network isolation

---

## 📌 Quick Reference Card

```bash
# Check namespace labels
kubectl get namespace --show-labels | grep pod-security

# Dry-run to see what would fail
kubectl label namespace my-app \
  pod-security.kubernetes.io/enforce=restricted \
  --dry-run=server

# Find non-compliant pods before enforcing
kubectl get pods -A -o json | \
  kubectl-psachecker --level restricted

# Common fix: add to all containers in deployment
kubectl patch deployment my-app --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/securityContext","value":
    {"runAsNonRoot":true,"seccompProfile":{"type":"RuntimeDefault"}}}]'

# Profiles
# pod-security.kubernetes.io/enforce: privileged|baseline|restricted
# pod-security.kubernetes.io/warn: privileged|baseline|restricted
# pod-security.kubernetes.io/audit: privileged|baseline|restricted
```

---

## 🧠 Think About This

Running containers as root is the single most common Kubernetes security mistake. Even if your app doesn't need root, many base Docker images (Ubuntu, Debian) run as root by default. The fix is two lines in your Dockerfile (`USER 1000`) and two lines in your Pod securityContext (`runAsNonRoot: true`, `runAsUser: 1000`). Applying PSS `restricted` to your app namespaces forces this fix and prevents a whole class of container escape vulnerabilities. Start with `audit` mode to discover issues, then enable `enforce` once all Pods are compliant.
