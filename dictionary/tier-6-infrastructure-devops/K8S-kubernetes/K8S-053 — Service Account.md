---
layout: default
title: "Service Account"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /kubernetes/service-account/
id: K8S-053
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["RBAC (K8s)", "Pod", "Namespace (K8s)"]
used_by:
  [
    "RBAC (K8s)",
    "Operators",
    "GitOps with Kubernetes",
    "Kubernetes Secrets Management",
  ]
related:
  [
    "RBAC (K8s)",
    "Kubernetes Secrets Management",
    "Pod",
    "Admission Controllers",
  ]
tags: [kubernetes, service-account, rbac, identity, irsa, k8s]
---

# Service Account

## ⚡ TL;DR

A **ServiceAccount** provides an identity for Pods within the cluster. Pods use ServiceAccount tokens to authenticate to the API Server. Combined with RBAC, it grants fine-grained permissions. Every Pod gets the `default` ServiceAccount if none specified. Used for Operators, CI pipelines, cloud IAM federation (IRSA).

---

## 🔥 Problem This Solves

Pods often need to call the Kubernetes API (operators watching resources) or AWS APIs (pods reading from S3). Without ServiceAccounts, you'd embed static credentials. ServiceAccounts provide rotating, cluster-managed identity tokens that can be federated to cloud IAM roles.

---

## 📘 Textbook Definition

A ServiceAccount provides an identity for processes running in Pods. It is namespaced, and its tokens are mounted into pods by default. ServiceAccounts bind to RBAC roles/clusterroles, granting those processes specific Kubernetes API permissions, and can be federated to external identity systems.

---

## ⏱️ 30 Seconds

```yaml
# Create ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-operator
  namespace: my-app

---
# Assign to Pod
spec:
  serviceAccountName: my-operator
  automountServiceAccountToken: false # opt-out if no API access needed
```

---

## 🔩 First Principles

- Every namespace has a `default` ServiceAccount — mounted by default in all Pods
- Token automatically mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`
- Token is a signed JWT; API Server validates it
- K8s 1.21+: **Bound Service Account Tokens** (short-lived, audience-bound, automatically rotated)
- `automountServiceAccountToken: false` prevents mounting the token (best practice for non-API Pods)
- RBAC binds Roles to ServiceAccounts to grant permissions

---

## 🧪 Thought Experiment

You're building an operator that watches `PostgreSQLCluster` CRDs and creates StatefulSets. The operator Pod needs API access. Create a ServiceAccount `postgres-operator-sa`, bind it to a ClusterRole with permissions to watch `postgresclusters` and manage `statefulsets`. The Pod's process authenticates automatically using the mounted token. No passwords, no static credentials.

---

## 🧠 Mental Model / Analogy

A ServiceAccount is like an **employee badge**: each employee (Pod) has a badge (ServiceAccount) that identifies who they are. The badge grants access to certain doors (RBAC). The badge management system (K8s) automatically issues, rotates, and revokes badges. You never hardcode door codes (static credentials) — you just issue the right badge.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: ServiceAccount = identity for Pods. Default SA is auto-created in every namespace. Operators and tools that call the K8s API use a ServiceAccount.

**Level 2 — Practitioner**: Create custom SA per workload. Bind RBAC Role to SA. Set `serviceAccountName` in Pod spec. Use `automountServiceAccountToken: false` for Pods that don't call the K8s API.

**Level 3 — Advanced**: Bound Service Account Tokens (K8s 1.20+): short-lived (1h), audience-specific, auto-rotated. `TokenRequest` API for custom tokens. OIDC projection: SA tokens can be used for OIDC federation.

**Level 4 — Expert**: IRSA (IAM Roles for Service Accounts) on EKS: SA with annotation `eks.amazonaws.com/role-arn` → EKS OIDC provider issues SA tokens → AWS STS exchanges for AWS credentials → Pod can call AWS APIs without instance metadata. Similar: GKE Workload Identity, Azure Workload Identity. This eliminates node IAM role abuse (all nodes sharing one IAM role). TokenProjection volumes: mount tokens for specific audiences (e.g., Vault) alongside the default K8s token.

---

## ⚙️ How It Works

### ServiceAccount with RBAC

```yaml
# ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: config-reader
  namespace: monitoring

---
# ClusterRole: read configmaps cluster-wide
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: configmap-reader
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]

---
# RoleBinding: in monitoring namespace only
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-configmaps
  namespace: monitoring
subjects:
  - kind: ServiceAccount
    name: config-reader
    namespace: monitoring
roleRef:
  kind: ClusterRole
  name: configmap-reader
  apiGroup: rbac.authorization.k8s.io

---
# Pod using ServiceAccount
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: config-reader
  containers:
    - name: app
      image: my-app
```

### Token at Runtime

```bash
# Inside a Pod
cat /var/run/secrets/kubernetes.io/serviceaccount/token
# → JWT token

# Verify token contents
kubectl exec -it my-pod -- cat /var/run/secrets/kubernetes.io/serviceaccount/token | \
  cut -d. -f2 | base64 -d | python3 -m json.tool
# Shows: sub, aud, namespace, serviceAccountName, exp

# Call K8s API from within Pod using mounted token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
CA=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
curl --cacert $CA -H "Authorization: Bearer $TOKEN" \
  https://kubernetes.default.svc/api/v1/namespaces/default/pods
```

### IRSA Setup (EKS)

```yaml
# ServiceAccount with IAM role annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-reader
  namespace: data-processing
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/S3ReadRole

---
# Pod using this SA
spec:
  serviceAccountName: s3-reader
  containers:
    - name: app
      image: my-app
      env:
        - name: AWS_REGION
          value: us-east-1
      # No AWS credentials needed! SDK auto-uses IRSA token
```

### Projected Token Volume (Custom Audience)

```yaml
# Mount SA token for Vault audience
volumes:
  - name: vault-token
    projected:
      sources:
        - serviceAccountToken:
            path: token
            expirationSeconds: 7200
            audience: vault # audience-specific token
containers:
  - name: app
    volumeMounts:
      - name: vault-token
        mountPath: /var/run/secrets/vault
```

---

## 🔄 E2E Flow: IRSA Authentication

```
Pod starts with serviceAccountName: s3-reader (annotated with IAM role ARN)
  → EKS OIDC provider: issue SA token with audience=sts.amazonaws.com
  → Token mounted at /var/run/secrets/eks.amazonaws.com/serviceaccount/token

AWS SDK in Pod:
  → SDK reads mounted IRSA token
  → Calls STS AssumeRoleWithWebIdentity:
      token=<mounted JWT>
      role-arn=arn:aws:iam::123456789012:role/S3ReadRole
  → STS validates JWT against EKS OIDC endpoint
  → STS returns short-lived AWS credentials (1h)
  → SDK uses credentials for S3 operations

Security:
  - Credentials never stored on node
  - Per-pod identity (not per-node)
  - OIDC validation ensures only that specific SA can assume that role
```

---

## ⚖️ Comparison Table

|                        | default SA              | Custom SA         | IRSA SA               |
| ---------------------- | ----------------------- | ----------------- | --------------------- |
| **Auto-created**       | ✅                      | Manual            | Manual                |
| **Mounted by default** | ✅ (if not disabled)    | If specified      | If specified          |
| **K8s API access**     | Needs RBAC              | Needs RBAC        | Needs RBAC            |
| **AWS access**         | ❌                      | ❌                | ✅ via STS            |
| **Best practice**      | Disable mount if unused | ✅ For API access | ✅ For cloud services |

---

## ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| "default SA is safe to use"                | default SA has no permissions by default but having a token mounted is a risk (token theft) |
| "ServiceAccount tokens are permanent"      | K8s 1.21+: bound tokens expire (default 1h) and auto-rotate                                 |
| "IRSA requires instance metadata disabled" | IRSA is additive; disable IMDSv1 on nodes for security (prevent token theft from node role) |
| "One SA per namespace is enough"           | Use one SA per workload for least-privilege isolation                                       |

---

## 🚨 Failure Modes

| Failure                                        | Symptom                                        | Fix                                                                  |
| ---------------------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------- |
| automountServiceAccountToken: false + SDK call | `unable to load in-cluster configuration`      | Set to true; or provide explicit kubeconfig                          |
| IRSA token expired                             | `ExpiredTokenException` from AWS               | K8s auto-rotates; ensure SDK retries token refresh                   |
| Wrong SA namespace in RoleBinding              | API calls get 403                              | SA namespace in RoleBinding subject must match SA's actual namespace |
| SA deleted with running pods                   | Pods continue with cached token; new pods fail | Don't delete SAs with running pods                                   |

---

## 🔗 Related Keywords

- [RBAC (K8s)](/kubernetes/rbac-k8s/) — binds permissions to ServiceAccounts
- [Kubernetes Secrets Management](/kubernetes/kubernetes-secrets-management/) — SA tokens are secrets
- [Pod](/kubernetes/pod/) — where SA token is mounted and used
- [Operators](/kubernetes/operators/) — use SAs to interact with API Server

---

## 📌 Quick Reference Card

```bash
# Create ServiceAccount
kubectl create serviceaccount my-sa -n my-namespace

# List SAs
kubectl get serviceaccounts -n my-namespace

# Check what a SA can do
kubectl auth can-i --list --as=system:serviceaccount:my-ns:my-sa

# Disable auto-mount on default SA (security best practice)
kubectl patch serviceaccount default -n my-ns \
  -p '{"automountServiceAccountToken": false}'

# Create token manually (for testing)
kubectl create token my-sa -n my-ns --duration=1h

# Inspect SA token
kubectl get secret -n my-ns | grep my-sa
kubectl describe secret <sa-token-secret> -n my-ns

# Check SA annotations (IRSA)
kubectl describe sa s3-reader -n data-processing | grep Annotations
```

---

## 🧠 Think About This

`automountServiceAccountToken: false` should be the default for any Pod that doesn't need to call the Kubernetes API. Most application Pods don't — they call your own APIs, databases, and cloud services. The mounted SA token is a Kubernetes credential that can be stolen if a Pod is compromised. By disabling auto-mount, a compromised Pod can't use the token to move laterally within the cluster (calling K8s API to list secrets, create new pods, etc.). Set `automountServiceAccountToken: false` on the ServiceAccount itself as a namespace-wide default, and selectively enable it for Pods that need API access.
