---
layout: default
title: "K8s Multi-Cluster"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /kubernetes/k8s-multi-cluster/
id: K8S-061
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Cluster", "Kubernetes Architecture", "Service (K8s)"]
used_by: ["ArgoCD", "GitOps with Kubernetes", "K8s Cost Optimization"]
related: ["ArgoCD", "GitOps with Kubernetes", "Service Mesh on K8s", "Cluster"]
tags: [kubernetes, multi-cluster, federation, cluster-api, eks, k8s]
---

# K8s Multi-Cluster

## ⚡ TL;DR

Running multiple Kubernetes clusters is the norm for large organizations: separate clusters per environment (dev/staging/prod), per cloud region (HA across AZs and regions), per team (isolation), or per regulatory boundary. Multi-cluster management tools: ArgoCD (GitOps), Cluster API (provisioning), Cilium Mesh (networking), and kubefed/Liqo (federation).

---

## 🔥 Problem This Solves

A single cluster has blast radius concerns (one misconfiguration can affect all workloads), regional failure risk, multi-tenant isolation issues, and version upgrade coupling. Multi-cluster enables environment isolation, geographic distribution, independent upgrade cycles, and team autonomy.

---

## 📘 Textbook Definition

Multi-cluster Kubernetes refers to architectures where multiple Kubernetes clusters are used together to meet requirements of isolation, geographic distribution, disaster recovery, or multi-tenancy. It requires solutions for cluster provisioning, workload deployment, service discovery across clusters, and unified observability.

---

## ⏱️ 30 Seconds

```
Common multi-cluster patterns:

1. Environment isolation:
   dev-cluster → staging-cluster → prod-cluster
   (ArgoCD manages all three from one control plane)

2. Regional HA:
   us-east-cluster + eu-west-cluster
   (Global load balancer routes to nearest healthy cluster)

3. Team isolation:
   team-a-cluster + team-b-cluster
   (Independent upgrade cycles, blast radius isolation)

4. Active-active:
   Both clusters serve traffic; failover if one goes down
```

---

## 🔩 First Principles

- Each cluster is an independent control plane (separate etcd, API server)
- Cross-cluster communication: not built-in; requires service mesh or DNS federation
- Multi-cluster management tools: ArgoCD (deploy to many), Cluster API (provision many), Flux (GitOps for many)
- Kubeconfig contexts: switching clusters requires context switch or kubeconfig merge
- No shared namespaces across clusters — isolation is real

---

## 🧪 Thought Experiment

Black Friday: your single-cluster e-commerce platform is at capacity. You need to spin up 3 more clusters in different AZs and distribute load. With Cluster API: `ClusterClass` template → `MachinePool` scale up → 3 new clusters provisioned by cloud provider in 10 minutes, each bootstrapped with kubeadm, registered with ArgoCD, GitOps-managed. Traffic routed via Route53 weighted DNS or a global ALB.

---

## 🧠 Mental Model / Analogy

Multi-cluster is like **running a chain of restaurants** vs one large restaurant. Each location (cluster) has independent kitchen (control plane), staff (nodes), and operations. The franchise headquarters (ArgoCD/GitOps) ensures all locations follow the same recipes (GitOps manifests). Supply chain (registry) is shared. Central monitoring (Thanos) sees all locations' metrics.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Most orgs have dev/staging/prod clusters. ArgoCD manages deployments to all. Keep configs in Git with environment-specific overlays.

**Level 2 — Practitioner**: kubectx for switching contexts. ArgoCD multi-cluster: add cluster credentials, create Applications targeting different clusters. Cluster API: provision clusters declaratively using K8s objects.

**Level 3 — Advanced**: Cilium Cluster Mesh: cross-cluster service discovery + load balancing. Pods in cluster-A can call Services in cluster-B by name. VPC peering / Transit Gateway for network connectivity between clusters. Single ArgoCD with multiple cluster registrations.

**Level 4 — Expert**: Active-active: same workload runs in 2+ clusters; global load balancer (Route53, Cloudflare) routes based on health/latency. KubeVIP / MetalLB for bare-metal multi-cluster load balancing. Multi-cluster observability: Thanos (Prometheus federation across clusters), Loki multi-cluster. Multi-cluster RBAC: unified identity (OIDC) across clusters so same token works everywhere. Cluster API ClusterClass: template-based cluster provisioning with topology enforcement.

---

## ⚙️ How It Works

### ArgoCD Multi-Cluster

```bash
# Register remote cluster with ArgoCD
argocd cluster add my-prod-context

# ArgoCD Application targeting remote cluster
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service-prod
  namespace: argocd
spec:
  destination:
    server: https://prod-cluster-api.example.com:6443   # remote cluster
    namespace: production
  source:
    path: apps/my-service/overlays/prod
    ...
```

### ApplicationSet for Multi-Cluster

```yaml
# Auto-generate Application per cluster
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
spec:
  generators:
    - clusters: # iterate over all registered ArgoCD clusters
        selector:
          matchLabels:
            environment: production # only prod clusters
  template:
    spec:
      destination:
        server: "{{server}}"
        namespace: my-service
      source:
        path: apps/my-service/overlays/{{metadata.labels.region}}
```

### Cluster API (CAPI)

```yaml
# Provision a new cluster declaratively
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-us-east-1
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["10.244.0.0/16"]
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: AWSCluster # AWS-specific (CAPA provider)
    name: prod-us-east-1
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: prod-us-east-1-cp

---
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: AWSCluster
metadata:
  name: prod-us-east-1
spec:
  region: us-east-1
  sshKeyName: my-ssh-key

---
# MachinePool for worker nodes
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachinePool
spec:
  replicas: 5
  template:
    spec:
      bootstrap:
        configRef:
          kind: KubeadmConfig
      infrastructureRef:
        kind: AWSMachinePool
```

### Cilium Cluster Mesh

```bash
# Connect two clusters
cilium clustermesh enable --cluster-id 1 --cluster-name cluster-a
cilium clustermesh connect --destination-context cluster-b

# Global Service: accessible from both clusters
kubectl annotate service my-service \
  service.cilium.io/global=true \
  service.cilium.io/affinity=local  # prefer local cluster
```

### Multi-Region Traffic (Route53 + ALB)

```
Route53 health check policy:
  us-east-1 ALB (weight: 50, health check: ✅)
  eu-west-1 ALB (weight: 50, health check: ✅)

  → Traffic split 50/50

If us-east-1 fails health check:
  → Route53 routes 100% to eu-west-1
  → Recovery: health check passes → routes balanced again

No K8s awareness needed for this failover
(K8s handles Pod scheduling within each cluster)
```

---

## 🔄 E2E Flow: Multi-Cluster Deployment with ArgoCD

```
GitOps repo structure:
  clusters/
    prod-us-east/
      kustomization.yaml (my-service, overlays/prod-us-east)
    prod-eu-west/
      kustomization.yaml (my-service, overlays/prod-eu-west)

Developer PR: update image tag to v1.5.0
  → Merge to main

ArgoCD ApplicationSet (clusters generator):
  → Detects change in both cluster paths
  → Application prod-us-east: OutOfSync
  → Application prod-eu-west: OutOfSync

ArgoCD sync (manual or automated):
  → Apply to prod-us-east cluster → rolling update
  → Monitor health (5 min)
  → Apply to prod-eu-west cluster → rolling update

Result: v1.5.0 running in both regions, sequentially
```

---

## ⚖️ Comparison Table

|                          | Single Large Cluster            | Multi-Cluster            |
| ------------------------ | ------------------------------- | ------------------------ |
| **Blast radius**         | High (all workloads)            | Low (per cluster)        |
| **Upgrade risk**         | High                            | Low (cluster by cluster) |
| **Operational overhead** | Low                             | High                     |
| **Cross-service calls**  | Simple (cluster-internal)       | Complex (mesh/DNS)       |
| **Regional HA**          | Requires multi-AZ (same region) | True multi-region        |
| **Cost**                 | Lower                           | Higher (control planes)  |

---

## ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------------------ |
| "Multi-cluster = multi-region"                       | Multi-cluster within a single region is common for isolation                   |
| "Services communicate across clusters automatically" | Cross-cluster service discovery requires Cilium Mesh, Istio, or DNS federation |
| "One control plane can manage everything"            | ArgoCD manages deployments; each cluster still has its own control plane       |
| "Multi-cluster is only for large companies"          | Many mid-sized teams use 2-3 clusters (dev/staging/prod) effectively           |

---

## 🚨 Failure Modes

| Failure                            | Symptom                                     | Fix                                                      |
| ---------------------------------- | ------------------------------------------- | -------------------------------------------------------- |
| Cluster registration lost (ArgoCD) | Apps show Unknown cluster                   | Re-add cluster credentials                               |
| Cross-cluster latency              | Service mesh connections slow               | Ensure clusters are co-located or use regional endpoints |
| kubeconfig proliferation           | Engineers confused which cluster they're on | kubectx + shell prompt showing context; CI validation    |
| Divergent cluster versions         | Incompatible APIs between clusters          | Use Cluster API to standardize versions                  |

---

## 🔗 Related Keywords

- [ArgoCD](/kubernetes/argocd/) — manages GitOps across multiple clusters
- [GitOps with Kubernetes](/kubernetes/gitops-with-kubernetes/) — multi-cluster GitOps patterns
- [Service Mesh on K8s](/kubernetes/service-mesh-on-k8s/) — cross-cluster service communication
- [Cluster](/kubernetes/cluster/) — the fundamental isolation unit

---

## 📌 Quick Reference Card

```bash
# Manage multiple clusters with kubectx
brew install kubectx
kubectx                      # list contexts
kubectx prod-us-east         # switch context
kubens production            # switch namespace

# Merge kubeconfigs
KUBECONFIG=~/.kube/config:~/new-cluster.yaml kubectl config view --merge --flatten \
  > ~/.kube/merged-config

# ArgoCD: list clusters
argocd cluster list
argocd cluster add <context-name>

# Check current context in all commands
kubectl config current-context

# Flux: multi-cluster with separate kustomization per cluster
# Each cluster runs its own Flux instance
# Each monitors its own cluster-specific path in Git
```

---

## 🧠 Think About This

The "right" number of clusters involves a genuine tradeoff between isolation/safety and operational overhead. A useful heuristic: one cluster per environment (dev, staging, prod) is the minimum. Add clusters when you need: regulatory compliance (data sovereignty requires EU data to stay in EU cluster), team autonomy (team runs their own cluster), or risk isolation (ML training shouldn't affect production latency). The hidden cost of more clusters is proportional operational overhead — monitoring, upgrading, cost management. Kubernetes control plane costs ($72-150/month on EKS/GKE/AKS) add up. Design your cluster topology based on actual isolation requirements, not fear.
