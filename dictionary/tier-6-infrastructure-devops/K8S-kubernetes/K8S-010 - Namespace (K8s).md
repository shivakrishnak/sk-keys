---
layout: default
title: "Namespace (K8s)"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /kubernetes/namespace-k8s/
id: K8S-010
category: "Kubernetes"
difficulty: "★☆☆"
depends_on: ["Cluster", "Kubernetes Architecture"]
used_by: ["Deployment", "Service (K8s)", "ConfigMap", "Secret", "RBAC (K8s)"]
related:
  ["RBAC (K8s)", "Resource Requests / Limits", "Network Policy", "Cluster"]
tags: [kubernetes, namespace, isolation, multi-tenancy, k8s]
---

# Namespace (K8s)

## ⚡ TL;DR

A Namespace is a **logical partition** within a Kubernetes cluster. It scopes resource names, applies RBAC policies, and enforces resource quotas. Default namespaces: `default`, `kube-system`, `kube-public`, `kube-node-lease`.

---

## 🔥 Problem This Solves

Multiple teams or environments sharing a single cluster need isolation: different RBAC permissions, resource quotas, and network policies. Namespaces provide that logical boundary without running separate clusters.

---

## 📘 Textbook Definition

Kubernetes Namespaces provide a mechanism for isolating groups of resources within a single cluster. Names of resources need to be unique within a namespace but not across namespaces.

---

## ⏱️ 30 Seconds

```yaml
# Create namespace
kubectl create namespace team-alpha

# Deploy into namespace
kubectl apply -f deployment.yaml -n team-alpha

# Set default namespace for context
kubectl config set-context --current --namespace=team-alpha
```

Default namespaces:

- `default` - where resources go without -n flag
- `kube-system` - K8s system components (CoreDNS, kube-proxy)
- `kube-public` - public cluster info (readable by all)
- `kube-node-lease` - Node heartbeat leases

---

## 🔩 First Principles

- Namespaces scope **names** - two Deployments called `api` can coexist in different namespaces
- Namespaces scope **RBAC** - RoleBindings apply within a namespace
- Namespaces scope **resource quotas** - limit CPU/memory per namespace
- Namespaces do NOT provide network isolation by default - that requires NetworkPolicies
- Cluster-scoped resources (Nodes, PersistentVolumes, ClusterRoles) are NOT namespace-scoped

---

## 🧪 Thought Experiment

Your org has 10 teams all sharing one cluster. Without namespaces, anyone with `kubectl` access could see/modify any resource. With namespaces + RBAC, each team gets their own partition: they can only see their resources, and resource quotas prevent one team from consuming all cluster CPU.

---

## 🧠 Mental Model / Analogy

Namespaces are like **floors in an office building**: each team has their own floor (namespace), access badges (RBAC) control who enters which floor, and there are limits on how many desks (resources) each floor can have (ResourceQuota).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Namespaces separate your workloads so different teams or environments don't interfere with each other.

**Level 2 - Practitioner**: RBAC Roles and RoleBindings are namespace-scoped. ResourceQuotas limit total CPU/memory in a namespace. LimitRanges set default resource requests/limits.

**Level 3 - Advanced**: DNS within cluster: `<service>.<namespace>.svc.cluster.local`. Cross-namespace calls require FQDN. NetworkPolicies enforce pod-level network isolation within/across namespaces.

**Level 4 - Expert**: Namespace lifecycle hooks (admission webhooks can inject sidecar proxies cluster-wide). `NamespaceTerminating` phase when deleting (waits for all resources to be deleted first). Finalizers can prevent namespace deletion. Hierarchical namespaces (HNC) enable parent-child namespace trees.

---

## ⚙️ How It Works

### ResourceQuota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: team-alpha
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "20"
```

### LimitRange (default requests/limits)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: team-alpha
spec:
  limits:
    - default:
        memory: "256Mi"
        cpu: "500m"
      defaultRequest:
        memory: "128Mi"
        cpu: "250m"
      type: Container
```

### DNS Pattern

```
Service "api" in namespace "team-alpha":
  Within same namespace:     api
  From other namespace:      api.team-alpha.svc.cluster.local
  Short form cross-NS:       api.team-alpha
```

---

## 🔄 E2E Flow: RBAC in Namespace

```
Admin creates namespace "team-alpha"
Admin creates Role with permissions (get,list,create pods)
Admin creates RoleBinding → binds Role to user "alice"

Alice: kubectl get pods -n team-alpha  ✅ allowed
Alice: kubectl get pods -n team-beta   ❌ denied (no RoleBinding there)
Alice: kubectl get nodes               ❌ denied (cluster-scoped resource)
```

---

## ⚖️ Comparison Table

|                       | Namespace Isolation    | Cluster Isolation           |
| --------------------- | ---------------------- | --------------------------- |
| **Cost**              | Free                   | Additional cluster overhead |
| **Network isolation** | Requires NetworkPolicy | Hard boundary               |
| **RBAC blast radius** | ClusterRoles can span  | Fully isolated              |
| **Complexity**        | Simple                 | Higher                      |
| **Use case**          | Teams within org       | Prod/dev, compliance        |

---

## ⚠️ Common Misconceptions

| Misconception                             | Reality                                                           |
| ----------------------------------------- | ----------------------------------------------------------------- |
| "Namespaces = network isolation"          | By default, all Pods can talk cross-namespace; need NetworkPolicy |
| "kube-system is off-limits"               | Anyone with ClusterAdmin can access kube-system                   |
| "Cluster-scoped resources use namespaces" | Nodes, PVs, ClusterRoles, StorageClasses are cluster-scoped       |
| "Deleting namespace is instant"           | Namespace stays in Terminating while resources are cleaned up     |

---

## 🚨 Failure Modes

| Failure                      | Symptom                     | Fix                                                 |
| ---------------------------- | --------------------------- | --------------------------------------------------- |
| Namespace stuck Terminating  | Namespace won't delete      | Check for finalizers: `kubectl get ns <ns> -o yaml` |
| ResourceQuota exceeded       | Pod creation fails          | Increase quota or reduce resource requests          |
| Missing namespace in context | Resources land in `default` | Always use `-n` or set default context namespace    |
| Cross-namespace DNS failure  | Service unreachable         | Use FQDN: `svc.namespace.svc.cluster.local`         |

---

## 🔗 Related Keywords

- [RBAC (K8s)](/kubernetes/rbac-k8s/) - permissions within namespaces
- [Resource Requests / Limits](/kubernetes/resource-requests-limits/) - resource constraints
- [Network Policy](/kubernetes/network-policy/) - namespace network isolation
- [Cluster](/kubernetes/cluster/) - the parent scope

---

## 📌 Quick Reference Card

```bash
# List namespaces
kubectl get namespaces

# Create
kubectl create ns my-namespace

# Get resources in namespace
kubectl get all -n my-namespace

# Get resources across all namespaces
kubectl get pods -A  # or --all-namespaces

# Set default namespace
kubectl config set-context --current --namespace=my-namespace

# Delete namespace (and all resources in it)
kubectl delete ns my-namespace

# Check resource quota
kubectl describe resourcequota -n my-namespace
```

---

## 🧠 Think About This

Namespaces are a soft boundary - a ClusterAdmin can always reach in. For truly separate teams that should never see each other's data, separate clusters are safer. But separate clusters mean separate API Servers, etcd, and operational overhead. Most organizations find that well-configured Namespaces + RBAC + NetworkPolicy provides sufficient isolation for all but the most compliance-sensitive use cases.
