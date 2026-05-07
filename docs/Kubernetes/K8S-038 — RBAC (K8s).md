---
layout: default
title: "RBAC (K8s)"
parent: "Kubernetes"
nav_order: 38
permalink: /kubernetes/rbac-k8s/
number: "K8S-038"
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["API Server", "Namespace (K8s)", "Service Account"]
used_by:
  ["kubectl", "Operators", "Admission Controllers", "Pod Security Standards"]
related:
  [
    "Service Account",
    "API Server",
    "Namespace (K8s)",
    "K8s Security Hardening",
    "Admission Controllers",
  ]
tags: [kubernetes, rbac, authorization, roles, service-accounts, security, k8s]
---

# RBAC (K8s)

## ⚡ TL;DR

Kubernetes RBAC controls **who can do what on which resources**. Four objects: `Role` (namespace-scoped permissions), `ClusterRole` (cluster-wide), `RoleBinding` (binds a Role to a subject), `ClusterRoleBinding` (binds a ClusterRole cluster-wide). Subjects: User, Group, or ServiceAccount.

---

## 🔥 Problem This Solves

A cluster has developers, operators, CI pipelines, and automated controllers — each needing different access. Without RBAC, everyone is admin or nothing. RBAC provides least-privilege access control: developers can deploy in their namespace; operators can't touch other teams' namespaces; CI pipelines can only push images.

---

## 📘 Textbook Definition

Role-Based Access Control (RBAC) in Kubernetes is an authorization mechanism that regulates access to the Kubernetes API based on the roles assigned to users or service accounts. RBAC uses Roles, ClusterRoles, RoleBindings, and ClusterRoleBindings to define and enforce permissions.

---

## ⏱️ 30 Seconds

```yaml
# Role: can get/list/watch Pods in namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: my-app
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

# RoleBinding: give the role to a service account
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: my-app
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: my-app
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

---

## 🔩 First Principles

- **Role vs ClusterRole**: Role is namespace-scoped; ClusterRole is cluster-wide (and can be bound namespace-scoped via RoleBinding)
- **Verbs**: `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`
- **Resources**: by API group and resource name; subresources: `pods/exec`, `pods/log`, `deployments/scale`
- **resourceNames**: restrict to specific named resources
- **Subjects**: `User` (certificate CN), `Group` (certificate O), `ServiceAccount` (automated workloads)
- **Deny rules don't exist**: RBAC is additive — no explicit deny, only allow

---

## 🧪 Thought Experiment

Your CI pipeline creates Docker images and deploys to the `staging` namespace. It shouldn't be able to touch `production`. RBAC solution: create a ServiceAccount `ci-deployer`, bind it to a Role in `staging` only with verbs `create`, `update`, `patch` on deployments. The pipeline's ServiceAccount has no permissions in `production` — rejected by RBAC even if the pipeline is compromised.

---

## 🧠 Mental Model / Analogy

RBAC in K8s is like a **hotel keycard system**: the Role is the access level (floor 3 only), the RoleBinding gives a specific guest (ServiceAccount) that access level. ClusterRole is a master key (all floors). The hotel system (API Server) checks keycards (RBAC) before letting anyone through any door (API call).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: RBAC controls who can perform actions (get, create, delete) on which resources (pods, deployments) in which namespace.

**Level 2 — Practitioner**: Role + RoleBinding (namespace). ClusterRole + ClusterRoleBinding (whole cluster). ClusterRole + RoleBinding = namespace-scoped access to a shared role definition.

**Level 3 — Advanced**: `kubectl auth can-i create pods --as=system:serviceaccount:my-ns:my-sa` — test permissions. Aggregated ClusterRoles: combine multiple ClusterRoles using label selectors (`aggregationRule`). `admin`, `edit`, `view` default ClusterRoles.

**Level 4 — Expert**: IRSA (IAM Roles for Service Accounts, AWS): ServiceAccount annotation maps to AWS IAM role, workload identity federation. Impersonation: `--as` flag, `system:impersonator` ClusterRole for service accounts to act as others. OIDC-based user management: dex/OIDC provider → OIDC token → API Server validates → RBAC applies to email/groups from token. Audit logs correlate RBAC subject to every API call.

---

## ⚙️ How It Works

### RBAC Object Types

```
Role          → permissions within a namespace
ClusterRole   → permissions cluster-wide (or reusable for RoleBinding)
RoleBinding   → grants Role or ClusterRole to subject in a namespace
ClusterRoleBinding → grants ClusterRole to subject cluster-wide
```

### Common Role Patterns

```yaml
# Developer: read/write in namespace (not secrets)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
  namespace: team-a
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["*"]
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["*"]
  - apiGroups: [""]
    resources: ["pods/exec", "pods/portforward"]
    verbs: ["create"]
# No secrets access!

---
# Operator: can manage its CRD
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: postgres-operator
rules:
  - apiGroups: ["databases.example.com"]
    resources: ["postgresclusters", "postgresclusters/status"]
    verbs: ["*"]
  - apiGroups: ["apps"]
    resources: ["statefulsets"]
    verbs: ["create", "get", "list", "update", "patch", "watch"]
  - apiGroups: [""]
    resources: ["services", "configmaps", "secrets"]
    verbs: ["create", "get", "list", "update", "patch", "watch"]
```

### ClusterRole + RoleBinding (namespace-scoped)

```yaml
# ClusterRole defined once
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
---
# RoleBinding scopes it to a namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: team-a # scoped to this namespace only
subjects:
  - kind: ServiceAccount
    name: monitoring-agent
    namespace: monitoring
roleRef:
  kind: ClusterRole # references ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Service Account with IRSA (AWS)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-reader
  namespace: data
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/S3ReadRole
```

---

## 🔄 E2E Flow: RBAC Check

```
kubectl delete pod my-pod --as=system:serviceaccount:my-ns:my-sa
  → API Server:
      1. Authentication: validate SA token → identity: system:serviceaccount:my-ns:my-sa
      2. Authorization (RBAC):
           - Find all RoleBindings in my-ns with subject = my-sa
           - Find all ClusterRoleBindings with subject = my-sa
           - Collect all allowed verbs/resources from bound Roles
           - Check: verb=delete, resource=pods, namespace=my-ns → allowed?
           - YES → proceed
           - NO → 403 Forbidden: "pods is forbidden: User system:serviceaccount:my-ns:my-sa
                    cannot delete resource pods in API group"
```

---

## ⚖️ Comparison Table

|                      | Role             | ClusterRole                           | Default Roles            |
| -------------------- | ---------------- | ------------------------------------- | ------------------------ |
| **Scope**            | Namespace        | Cluster                               | Cluster                  |
| **Reusable**         | Within namespace | Via ClusterRoleBinding or RoleBinding | Yes                      |
| **Use case**         | App-specific     | Cross-namespace, cluster admin        | Built-in admin/edit/view |
| **Custom resources** | ✅               | ✅                                    | Need to add manually     |

---

## ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                |
| ------------------------------------------- | -------------------------------------------------------------------------------------- |
| "ClusterRoleBinding + Role is valid"        | RoleBinding can reference a ClusterRole; ClusterRoleBinding cannot reference a Role    |
| "RBAC deny rules exist"                     | No deny rules — only additive allows; deny by not having a rule                        |
| "User RBAC applies to service accounts"     | ServiceAccounts use `kind: ServiceAccount` subjects; User subjects are for human users |
| "default ServiceAccount has no permissions" | default SA can list pods in some clusters — always review default SA permissions       |

---

## 🚨 Failure Modes

| Failure                               | Symptom                         | Fix                                                                |
| ------------------------------------- | ------------------------------- | ------------------------------------------------------------------ |
| Too permissive (`verbs: ["*"]`)       | Security audit fails            | List specific verbs needed                                         |
| Missing subresource                   | Cannot exec into pods           | Add `pods/exec` as separate resource                               |
| ClusterRoleBinding for namespace task | Grants access to all namespaces | Use RoleBinding scoped to namespace                                |
| SA not in correct namespace           | Binding doesn't apply           | SA namespace in RoleBinding subject must match SA actual namespace |

---

## 🔗 Related Keywords

- [Service Account](/kubernetes/service-account/) — primary non-human RBAC subject
- [API Server](/kubernetes/api-server/) — enforces RBAC
- [Namespace (K8s)](/kubernetes/namespace-k8s/) — RBAC scope for Roles
- [K8s Security Hardening](/kubernetes/k8s-security-hardening/) — RBAC is foundational

---

## 📌 Quick Reference Card

```bash
# Check permissions
kubectl auth can-i create deployments -n my-ns
kubectl auth can-i create deployments -n my-ns \
  --as=system:serviceaccount:my-ns:my-sa

# List roles in namespace
kubectl get roles,rolebindings -n my-ns

# Show what a SA can do (kubectl access matrix plugin)
kubectl access-matrix --sa my-sa -n my-ns

# Get permissions for current user
kubectl auth whoami

# Default ClusterRoles
# admin    - namespace admin (CRUD on most resources)
# edit     - create/update/delete pods/deployments/services, no RBAC
# view     - read-only (no secrets)
# cluster-admin - full cluster access
```

---

## 🧠 Think About This

The **least-privilege principle** is easy to state but hard to implement correctly. Many teams give operators too much access because it's easier than debugging 403 errors. A practical approach: run your operator/CI pipeline with no RBAC, watch the audit logs for `Forbidden` errors, then add exactly the permissions needed. `kubectl auth can-i --list` and the `kubectl access-matrix` plugin help audit what a service account can actually do. Over-permissioned service accounts are one of the top Kubernetes security risks in production clusters.
