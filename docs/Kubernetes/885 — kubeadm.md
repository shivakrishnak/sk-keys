---
layout: default
title: "kubeadm"
parent: "Kubernetes"
nav_order: 885
permalink: /kubernetes/kubeadm/
number: "0885"
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Kubernetes Architecture", "Cluster", "kubelet"]
used_by: ["K8s Upgrade Strategy", "Cluster"]
related: ["kubectl", "Cluster", "K8s Upgrade Strategy", "RBAC (K8s)", "etcd"]
tags: [kubernetes, kubeadm, cluster-bootstrap, k8s-setup, node-join]
---

# kubeadm

## ⚡ TL;DR

`kubeadm` is the **official cluster bootstrapping tool** — it sets up a production-grade Kubernetes control plane and joins worker nodes with a single command. It handles TLS cert generation, etcd setup, static pod manifests, and kubeconfig creation.

---

## 🔥 Problem This Solves

Setting up a Kubernetes cluster manually requires generating dozens of TLS certificates, configuring etcd, creating static pod manifests for control plane components, and configuring networking. kubeadm automates all of this into `kubeadm init` and `kubeadm join`.

---

## 📘 Textbook Definition

kubeadm is a tool for bootstrapping Kubernetes clusters. It performs the actions necessary to get a minimum viable cluster up and running. It manages TLS certificate provisioning, component configuration, token-based node joining, and cluster upgrades.

---

## ⏱️ 30 Seconds

```bash
# 1. Initialize control plane
kubeadm init --pod-network-cidr=10.244.0.0/16

# 2. Configure kubectl
mkdir -p $HOME/.kube
cp /etc/kubernetes/admin.conf $HOME/.kube/config

# 3. Install CNI (e.g., Flannel)
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# 4. Join worker nodes (token from init output)
kubeadm join <control-plane>:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

---

## 🔩 First Principles

- kubeadm doesn't provision VMs — you provide the machines, kubeadm configures Kubernetes on them
- kubeadm generates all PKI (Certificate Authority, API Server cert, etcd cert, etc.)
- All certs stored in `/etc/kubernetes/pki/`
- kubeadm config is declarative (`kubeadm-config.yaml`) for reproducibility
- kubeadm handles upgrades: `kubeadm upgrade apply v1.29.0`

---

## 🧪 Thought Experiment

Before kubeadm: manually create CA, sign 10+ certificates, write etcd systemd units, write static pod manifests with exact flags, configure kubeconfig. Half a day of work, many things to get wrong. With kubeadm: `kubeadm init` — 5 minutes, production-grade, correct by construction.

---

## 🧠 Mental Model / Analogy

kubeadm is like a **construction contractor**: you provide the land and materials (VMs + container runtime), and the contractor builds the structure (Kubernetes control plane) correctly, handling all the tricky details (TLS, certs, static pods, kubeconfig).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: `kubeadm init` sets up the control plane. `kubeadm join` adds worker nodes.

**Level 2 — Practitioner**: kubeadm creates PKI, configures kubelet on control plane, writes static pod manifests to `/etc/kubernetes/manifests/`. Generates kubeconfig at `/etc/kubernetes/admin.conf`. Token has a TTL (default 24h).

**Level 3 — Advanced**: HA control plane: `kubeadm init --upload-certs` for multiple control plane nodes. Certificate management: `kubeadm certs renew all`. Phase-by-phase: `kubeadm init phase certs all`, `kubeadm init phase control-plane all`.

**Level 4 — Expert**: `KubeadmConfig` API (v1beta3): customize API Server flags, etcd external endpoint, image repository mirror. `ClusterConfiguration` and `InitConfiguration` drive fully declarative cluster setup. Cluster API uses kubeadm as bootstrap provider for machine lifecycle management.

---

## ⚙️ How It Works

### kubeadm init phases

```
1. preflight              → system checks (ports, kernel params)
2. certs                  → generate PKI (CA, apiserver, etcd certs)
3. kubeconfig             → admin.conf, controller-manager.conf, scheduler.conf
4. etcd                   → write /etc/kubernetes/manifests/etcd.yaml
5. control-plane          → write apiserver, controller-manager, scheduler manifests
6. kubelet-start          → write kubelet config, start kubelet
7. wait-control-plane     → wait for API Server to be healthy
8. upload-config          → store kubeadm config in ConfigMap
9. mark-control-plane     → taint control plane node
10. bootstrap-token       → create join token
11. addon                 → install CoreDNS + kube-proxy
```

### kubeadm Config (declarative)

```yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.29.0
controlPlaneEndpoint: "k8s-api.example.com:6443" # HA LB
networking:
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.96.0.0/12"
apiServer:
  extraArgs:
    audit-log-path: /var/log/audit.log
    encryption-provider-config: /etc/kubernetes/encryption.yaml
etcd:
  local:
    extraArgs:
      auto-compaction-retention: "1"
```

### HA Control Plane Setup

```bash
# First control plane
kubeadm init --config=kubeadm-config.yaml --upload-certs

# Additional control planes
kubeadm join k8s-api.example.com:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane \
  --certificate-key <cert-key>
```

---

## 🔄 E2E Flow: Cluster Creation

```
kubeadm init:
  1. Preflight: check Docker running, ports free, swap off
  2. Generate /etc/kubernetes/pki/ (CA, certs, keys)
  3. Write /etc/kubernetes/manifests/ (etcd, apiserver, ...)
  4. kubelet starts, reads manifests, starts control plane containers
  5. Wait for API Server healthy
  6. Apply CoreDNS and kube-proxy
  7. Print: "kubeadm join" command for workers

Worker: kubeadm join <cp>:6443 --token <t> --discovery-token-ca-cert-hash sha256:<h>
  1. Discovery: fetch cluster CA from API Server using token
  2. TLS bootstrap: kubelet generates key, sends CSR to API Server
  3. API Server approves CSR (auto-approval via token)
  4. kubelet: registered as Node in cluster
```

---

## ⚖️ Comparison Table

|                     | kubeadm               | Minikube   | k3s              | Cluster API               |
| ------------------- | --------------------- | ---------- | ---------------- | ------------------------- |
| **Purpose**         | Production bootstrap  | Local dev  | Lightweight K8s  | Infrastructure automation |
| **Scope**           | Setup only            | All-in-one | All-in-one       | Lifecycle management      |
| **HA**              | ✅                    | ❌         | ✅               | ✅                        |
| **Cert management** | ✅                    | Auto       | Auto             | Via kubeadm bootstrap     |
| **Target env**      | Bare metal, cloud VMs | Local      | IoT, edge, small | Cloud, bare metal         |

---

## ⚠️ Common Misconceptions

| Misconception                        | Reality                                                           |
| ------------------------------------ | ----------------------------------------------------------------- |
| "kubeadm sets up networking"         | CNI must be installed separately after kubeadm init               |
| "kubeadm manages VMs"                | kubeadm runs on existing machines; Cluster API manages VMs        |
| "kubeadm tokens don't expire"        | Default token TTL is 24h; re-generate with `kubeadm token create` |
| "kubeadm is only for small clusters" | kubeadm is production-grade; GKE/EKS use similar initialization   |

---

## 🚨 Failure Modes

| Failure            | Symptom                              | Fix                                           |
| ------------------ | ------------------------------------ | --------------------------------------------- |
| Swap enabled       | Preflight fails: "swap enabled"      | `swapoff -a`; remove from /etc/fstab          |
| Join token expired | Worker can't join                    | `kubeadm token create --print-join-command`   |
| Cert expired       | kubectl fails: "certificate expired" | `kubeadm certs renew all` (do before expiry!) |
| Wrong pod CIDR     | Pods can't communicate               | Match pod-network-cidr to CNI config          |

---

## 🔗 Related Keywords

- [Cluster](/kubernetes/cluster/) — what kubeadm creates
- [kubectl](/kubernetes/kubectl/) — CLI tool that works with kubeadm clusters
- [K8s Upgrade Strategy](/kubernetes/k8s-upgrade-strategy/) — `kubeadm upgrade apply`
- [etcd](/kubernetes/etcd/) — kubeadm sets up etcd

---

## 📌 Quick Reference Card

```bash
# Check certificate expiry
kubeadm certs check-expiration

# Renew certificates
kubeadm certs renew all

# Create new join token
kubeadm token create --print-join-command

# List tokens
kubeadm token list

# Upgrade
kubeadm upgrade plan
kubeadm upgrade apply v1.29.0

# Reset node (destructive!)
kubeadm reset
```

---

## 🧠 Think About This

kubeadm certificates expire after 1 year by default. Many teams forget this and discover it the hard way when the cluster breaks in production. Set a calendar reminder for 30, 60, 90 days before expiry. `kubeadm certs check-expiration` shows all cert expiry dates. Renewals (`kubeadm certs renew all`) are non-disruptive if done before expiry, but if certs are already expired, recovering the cluster can be complex. This is one of the top causes of unexpected Kubernetes outages.
