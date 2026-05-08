---
layout: default
title: "K8s Upgrade Strategy"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 65
permalink: /kubernetes/k8s-upgrade-strategy/
id: K8S-065
category: "Kubernetes"
difficulty: "★★★"
depends_on:
  [
    "Pod Disruption Budget",
    "Rolling Update Strategy",
    "kubeadm",
    "Node Affinity / Anti-Affinity",
  ]
used_by: ["K8s Security Hardening", "K8s Multi-Cluster"]
related:
  [
    "kubeadm",
    "Pod Disruption Budget",
    "Rolling Update Strategy",
    "K8s Multi-Cluster",
  ]
tags: [kubernetes, upgrade, kubeadm, eks, managed-kubernetes, cluster-api, k8s]
---

# K8s Upgrade Strategy

## ⚡ TL;DR

Kubernetes releases every ~4 months; each version supported ~14 months. Upgrade strategy: **one minor version at a time** (1.27 → 1.28 → 1.29; never skip). Control plane first, then worker nodes (rolling). Test in dev/staging first. For managed K8s (EKS/GKE/AKS): managed upgrades handle control plane; node groups require node rotation. PDBs protect workloads during node drain.

---

## 🔥 Problem This Solves

Running outdated K8s: security vulnerabilities (CVEs in API server, kubelet), missing features, API deprecations that break manifests, no vendor support. But upgrades are risky: API changes, container runtime changes, feature flags behavior changes. Strategy turns risky big-bang upgrades into routine, low-risk operations.

---

## 📘 Textbook Definition

Kubernetes upgrade strategy refers to the planning and execution process for upgrading Kubernetes cluster components (API server, scheduler, controller manager, kubelet, kube-proxy) to newer versions while maintaining application availability. Kubernetes follows semantic versioning, and the supported upgrade path is sequential minor-version increments.

---

## ⏱️ 30 Seconds

```
Upgrade order (CRITICAL - never out of order):
  1. etcd (must match kube-apiserver)
  2. kube-apiserver (control plane)
  3. kube-controller-manager, kube-scheduler (≤ 1 minor behind apiserver)
  4. kubelet (≤ 2 minors behind apiserver) - one node at a time
  5. kube-proxy (≤ 2 minors behind apiserver) - alongside kubelet
  6. kubectl (±1 minor of apiserver)

Node upgrade options:
  - In-place:   drain → upgrade kubelet → uncordon
  - Blue-green: new node group → drain old → delete old nodes
```

---

## 🔩 First Principles

- **Version skew policy**: API server must be the newest component; others lag by at most 2 minors
- **One minor version at a time**: K8s only certifies N→N+1 upgrades; skipping minors is unsupported
- **Control plane first**: workers must not be newer than the API server
- **PDB respected during drain**: `kubectl drain` honors Pod Disruption Budgets
- **API deprecations**: each K8s version removes some API versions (check `kubectl deprecations`)
- **Test matrix**: upgrade dev first, validate, then staging, then prod

---

## 🧪 Thought Experiment

You're on K8s 1.24, and you need to reach 1.28 (4 minor versions). You cannot upgrade directly: 1.24 → 1.25 (validate, 1 week) → 1.26 (validate, 1 week) → 1.27 (validate, 1 week) → 1.28. Each step: check API deprecations, upgrade tools, upgrade control plane, upgrade nodes. 4 upgrade cycles over 4 weeks. This is why staying within 1-2 minor versions of latest is strongly recommended.

---

## 🧠 Mental Model / Analogy

Upgrading K8s is like **upgrading a live aircraft's engine mid-flight**. You can't take the entire plane offline; individual components must be swapped while others keep flying. The order matters critically (you can't upgrade the wings before the fuselage). Each component has a compatibility matrix with adjacent components. Test in the flight simulator (dev cluster) first.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Upgrade dev first. One minor version at a time. Check API deprecations before upgrading. PDBs protect workloads during node drain.

**Level 2 - Practitioner**: kubeadm upgrade plan → kubeadm upgrade apply (control plane) → drain node → upgrade kubelet → uncordon. For managed K8s (EKS): upgrade control plane in console/CLI, then upgrade managed node groups (rolling replacement). Check `kubectl deprecations` with pluto or `kubectl api-versions`.

**Level 3 - Advanced**: Pre-upgrade checklist: review changelog + breaking changes, check deprecated API usage (pluto), validate RBAC/PSS changes, test PVCs, verify admission webhooks work with new API versions. Blue-green node upgrade: create new node group with updated AMI + new K8s version → migrate workloads → delete old node group. Minimizes in-place risk. Cluster API: automated cluster upgrades via MachineDeployment roll.

**Level 4 - Expert**: EKS managed node group upgrade: `aws eks update-nodegroup-version` - replaces nodes rolling, respects PDB, max unavailable configurable. EKS add-on compatibility matrix: VPC CNI, CoreDNS, kube-proxy must be compatible with K8s version - update add-ons after control plane upgrade. Feature gate transitions: GA features in N+1 may remove `--feature-gate` flag → audit feature gates before upgrade. etcd upgrades: critical path, always backup before upgrade, check etcd K8s compatibility matrix. `kubeadm upgrade diff` shows what config changes will be applied before applying.

---

## ⚙️ How It Works

### kubeadm Upgrade Flow

```bash
# PRE-UPGRADE CHECKLIST:
# 1. Backup etcd
ETCDCTL_API=3 etcdctl snapshot save snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key

# 2. Check deprecated APIs
kubectl deprecations --k8s-version v1.29  # or use: pluto detect-all-in-cluster

# 3. Review release notes
# https://kubernetes.io/docs/setup/release/notes/

# PHASE 1: Upgrade control plane node
# On control plane node:
apt-get update
apt-get install -y kubeadm=1.29.0-00

# Preview changes
kubeadm upgrade plan

# Apply upgrade
kubeadm upgrade apply v1.29.0

# Upgrade kubelet on control plane node
kubectl drain controlplane --ignore-daemonsets
apt-get install -y kubectl=1.29.0-00 kubelet=1.29.0-00
systemctl daemon-reload
systemctl restart kubelet
kubectl uncordon controlplane

# PHASE 2: Upgrade worker nodes (one at a time)
# From control plane:
kubectl drain worker-01 --ignore-daemonsets --delete-emptydir-data

# On worker-01:
apt-get update
apt-get install -y kubeadm=1.29.0-00
kubeadm upgrade node         # updates node-specific config
apt-get install -y kubelet=1.29.0-00 kubectl=1.29.0-00
systemctl daemon-reload
systemctl restart kubelet

# From control plane:
kubectl uncordon worker-01

# Verify
kubectl get nodes
# Should show v1.29.0 for all nodes
```

### EKS Upgrade (Managed)

```bash
# 1. Upgrade control plane
aws eks update-cluster-version \
  --name my-cluster \
  --kubernetes-version 1.29 \
  --region us-east-1

# Wait for completion
aws eks wait cluster-active --name my-cluster

# 2. Update add-ons (MUST do after control plane)
aws eks update-addon --cluster-name my-cluster \
  --addon-name vpc-cni \
  --addon-version v1.16.0-eksbuild.1

aws eks update-addon --cluster-name my-cluster \
  --addon-name coredns \
  --addon-version v1.11.1-eksbuild.4

aws eks update-addon --cluster-name my-cluster \
  --addon-name kube-proxy \
  --addon-version v1.29.0-eksbuild.1

# 3. Upgrade managed node group (rolling replacement)
aws eks update-nodegroup-version \
  --cluster-name my-cluster \
  --nodegroup-name standard-workers \
  --kubernetes-version 1.29 \
  --force    # respects PDBs; fails if PDB blocks drain

# 4. Monitor node group upgrade
aws eks describe-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name standard-workers \
  --query 'nodegroup.status'
```

### Blue-Green Node Upgrade

```bash
# 1. Create new node group with new K8s version
eksctl create nodegroup \
  --cluster my-cluster \
  --name workers-1-29 \
  --kubernetes-version 1.29 \
  --nodes 5

# 2. Taint old node group to stop new Pod scheduling
kubectl taint nodes -l eks.amazonaws.com/nodegroup=workers-1-28 \
  oldnodegroup=true:NoSchedule

# 3. Drain old nodes (workloads move to new nodes)
for node in $(kubectl get nodes -l eks.amazonaws.com/nodegroup=workers-1-28 \
             -o name); do
  kubectl drain $node --ignore-daemonsets --delete-emptydir-data
done

# 4. Verify all workloads on new nodes
kubectl get pods -A -o wide | grep workers-1-28  # should be empty

# 5. Delete old node group
eksctl delete nodegroup \
  --cluster my-cluster \
  --name workers-1-28
```

### API Deprecation Check with pluto

```bash
# Install pluto
brew install FairwindsOps/tap/pluto

# Check live cluster
pluto detect-all-in-cluster --target-versions k8s=v1.29.0

# Example output:
# NAME              NAMESPACE    KIND         VERSION          REPLACEMENT     DEPRECATED  REMOVED
# my-ingress        default      Ingress      extensions/v1beta1  networking.k8s.io/v1  true    true
# → networking.k8s.io/v1 is the replacement; update your manifest

# Check Helm charts
helm template my-release my-chart/ | pluto detect - --target-versions k8s=v1.29.0
```

---

## 🔄 E2E Flow: Quarterly Production Upgrade

```
T-4 weeks: Planning
  - Identify target version (K8s N+1)
  - Review changelog: breaking changes, deprecations
  - Run pluto: find deprecated API usage in cluster manifests
  - Identify add-ons + their compatible versions (VPC CNI, etc.)
  - Update runbook

T-3 weeks: Dev environment
  - Upgrade dev cluster (kubeadm or AWS console)
  - Update deprecated API manifests (found by pluto)
  - Run full integration test suite
  - Validate all Helm chart deployments work
  - Fix any issues

T-2 weeks: Staging environment
  - Upgrade staging cluster
  - Load test for 1 week
  - Monitor for regressions in metrics

T-0: Production upgrade
  - Schedule maintenance window (or upgrade with 0-downtime)
  - Take etcd snapshot
  - Upgrade control plane (EKS: update-cluster-version or kubeadm)
  - Upgrade add-ons (EKS: update-addon)
  - Upgrade node groups (EKS: update-nodegroup-version)
  - Monitor for 30 minutes
  - Sign off

T+1 week: Validation
  - All KPIs normal?
  - Any new alerts?
  - Document lessons learned
```

---

## ⚖️ Comparison Table

| Upgrade Method                    | Cluster Type  | Risk     | Downtime        |
| --------------------------------- | ------------- | -------- | --------------- |
| **kubeadm in-place**              | Self-managed  | Medium   | Zero (with PDB) |
| **kubeadm blue-green nodes**      | Self-managed  | Low      | Zero            |
| **EKS managed upgrade**           | EKS           | Low      | Zero            |
| **Cluster API MachineDeployment** | CAPI clusters | Low      | Zero            |
| **EKS Fargate**                   | Serverless    | Very Low | Zero            |

---

## ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                           |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| "Skip minor versions to save time"                    | Unsupported and risky; API changes are cumulative                                                 |
| "Control plane upgrade handles workers automatically" | No - worker nodes must be upgraded separately                                                     |
| "Managed K8s upgrades are automatic"                  | Control plane auto-upgrade optional; nodes require manual or auto nodegroup upgrade               |
| "Upgrading is only for security patches"              | Feature gates graduate to GA, alpha features removed - staying current is about compatibility too |

---

## 🚨 Failure Modes

| Failure                          | Symptom                         | Fix                                                    |
| -------------------------------- | ------------------------------- | ------------------------------------------------------ |
| etcd version mismatch            | API server crashes post-upgrade | Check etcd compatibility matrix; rollback etcd         |
| Deprecated API used in manifests | Deployments fail after upgrade  | Run pluto pre-upgrade; fix manifests                   |
| PDB blocks node drain            | Drain times out                 | Check PDB `disruptionsAllowed`; fix `minAvailable`     |
| Add-on incompatible with new K8s | CNI crashes, DNS broken         | Update add-ons immediately after control plane upgrade |

---

## 🔗 Related Keywords

- [kubeadm](/kubernetes/kubeadm/) - self-managed cluster upgrade tool
- [Pod Disruption Budget](/kubernetes/pod-disruption-budget/) - protects workloads during node drain
- [K8s Multi-Cluster](/kubernetes/k8s-multi-cluster/) - blue-green at cluster level
- [Rolling Update Strategy](/kubernetes/rolling-update-strategy/) - same principles for workloads

---

## 📌 Quick Reference Card

```bash
# Check current versions
kubectl version
kubectl get nodes

# Find version skew issues
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.nodeInfo.kubeletVersion}{"\n"}{end}'

# kubeadm: plan upgrade
kubeadm upgrade plan

# Check deprecated APIs
pluto detect-all-in-cluster --target-versions k8s=v1.29.0

# EKS: check available versions
aws eks describe-addon-versions --kubernetes-version 1.29

# Check node drain safety
kubectl get pdb -A  # ensure all PDBs have disruptionsAllowed > 0

# Watch nodes during upgrade
kubectl get nodes -w

# EKS: check node group status
aws eks describe-nodegroup --cluster-name my-cluster --nodegroup-name my-nodes \
  --query 'nodegroup.{Status:status,Version:version}'
```

---

## 🧠 Think About This

The best K8s upgrade strategy is one you practice quarterly. Teams that upgrade every 6 months or annually face a much harder upgrade path - accumulated deprecations, drift from current practices, and rusty runbooks. Teams that upgrade quarterly have simple, well-practiced runbooks and rarely face breaking changes. The second most important factor is **automated testing**: if your integration test suite can validate a fresh cluster in 15 minutes, you have high confidence in every upgrade. Without automated tests, every upgrade is manual validation dread. Invest in the test suite; it pays dividends on every upgrade. For managed K8s (EKS/GKE/AKS): enable auto-upgrade for the control plane - cloud providers handle it safely, and it keeps you from falling too far behind.
