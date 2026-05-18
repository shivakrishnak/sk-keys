---
version: 1
layout: default
title: "kube-proxy"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/kubernetes/kube-proxy/
id: K8S-036
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Service (K8s)", "Node", "DaemonSet"]
used_by:
  ["Service (K8s)", "ClusterIP / NodePort / LoadBalancer", "Network Policy"]
related:
  [
    "Service (K8s)",
    "CoreDNS",
    "Calico / Cilium",
    "Network Policy",
    "Kubernetes Networking (CNI)",
  ]
tags: [kubernetes, kube-proxy, iptables, ipvs, service-networking, k8s]
---

## ⚡ TL;DR

kube-proxy runs on every node as a DaemonSet and implements **Service networking**. It watches Service and Endpoint objects, then programs **iptables** (or **IPVS**) rules to route packets from ClusterIPs to Pod IPs. It's the reason `ClusterIP:port` actually reaches a Pod.

---

## 🔥 Problem This Solves

A Service has a virtual ClusterIP that doesn't exist on any network interface. Someone must translate `ClusterIP:80` into real `PodIP:8080` connections. kube-proxy programs the OS network stack (iptables/IPVS) to do this transparently.

---

## 📘 Textbook Definition

kube-proxy is a network proxy that runs on each node in the cluster. It maintains network rules on nodes to allow network communication to Pods from inside or outside the cluster. It implements the Service concept by programming iptables or IPVS rules.

---

## ⏱️ 30 Seconds

```
Service: my-app (ClusterIP: 10.96.100.50:80)
Endpoints: [10.244.1.5:8080, 10.244.2.8:8080,
  10.244.3.2:8080]

kube-proxy iptables rules (on every node):
  -A KUBE-SERVICES -d 10.96.100.50/32 -p tcp --dport 80 \
    -j KUBE-SVC-MY-APP

  # Load balance 1/3 to each Pod
  -A KUBE-SVC-MY-APP -m statistic --mode random
    --probability 0.333 \
    -j KUBE-SEP-POD1   # → DNAT to 10.244.1.5:8080
  -A KUBE-SVC-MY-APP -m statistic --mode random
    --probability 0.5 \
    -j KUBE-SEP-POD2   # → DNAT to 10.244.2.8:8080
  -A KUBE-SVC-MY-APP \
    -j KUBE-SEP-POD3   # → DNAT to 10.244.3.2:8080
```

---

## 🔩 First Principles

- kube-proxy does NOT proxy network traffic itself (despite the name) - it programs the kernel
- iptables mode: rules evaluated for every packet - O(n) complexity, slow at large scale
- IPVS mode: O(1) lookup via kernel hash table - recommended for large clusters (1000+ Services)
- eBPF mode (Cilium, replacing kube-proxy): XDP/TC hook, even faster, more features
- Endpoints update → kube-proxy updates iptables rules on all nodes (eventual consistency)

---

## 🧪 Thought Experiment

A Pod sends a request to ClusterIP `10.96.100.50:80`. This IP doesn't exist on any interface in the cluster. How does it work? The kernel hits an iptables DNAT rule added by kube-proxy: "when you see this destination IP:port, rewrite it to this Pod IP:port." The Pod never knows it was translated.

---

## 🧠 Mental Model / Analogy

kube-proxy is like a **traffic redirector** painted on the road. When you drive toward address 10.96.100.50, you see "REDIRECT → 10.244.1.5." The redirector doesn't physically move your car (it's not in the traffic path) - it just changes your GPS destination at the kernel level.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: kube-proxy makes Services work by setting up routing rules on every node.

**Level 2 - Practitioner**: Runs as DaemonSet in `kube-system`. Two modes: iptables (default, simpler) and IPVS (high performance). Watches Services and Endpoints via API Server.

**Level 3 - Advanced**: iptables: O(n) per packet (linear scan through rules). IPVS: O(1) hash table lookup. Load balancing algorithms in IPVS: rr (round-robin), lc (least connection), sh (source hash), wrr (weighted round-robin).

**Level 4 - Expert**: iptables synchronization: on endpoint change, kube-proxy atomically replaces all rules (iptables-restore). At 10,000 Services with 10 endpoints = 100,000 iptables rules - rule sync takes seconds. IPVS doesn't have this problem. Cilium can replace kube-proxy entirely using eBPF: faster, observability-rich, supports network policies natively.

---

## ⚙️ How It Works

---

### iptables Mode (default)

```
Packet to 10.96.100.50:80
  → iptables PREROUTING chain
  → KUBE-SERVICES chain
  → Match: dest 10.96.100.50:80
  → KUBE-SVC-XXX chain (load balance)
  → Random selection (statistic module)
  → KUBE-SEP-YYY chain
  → DNAT: 10.96.100.50:80 → 10.244.1.5:8080
  → Connection proceeds to Pod
```

---

### IPVS Mode

```yaml
# Enable IPVS in kube-proxy ConfigMap
data:
  config.conf: |
    mode: "ipvs"
    ipvs:
      scheduler: "rr"    # rr, lc, dh, sh, sed, nq
```

```
IPVS virtual server: 10.96.100.50:80
  Real servers: 10.244.1.5:8080
                10.244.2.8:8080
                10.244.3.2:8080
  Algorithm: round-robin (O(1) kernel hash table lookup)
```

---

### Replacing kube-proxy with Cilium

```bash
# Deploy Cilium with kube-proxy replacement
helm install cilium cilium/cilium \
  --set kubeProxyReplacement=true \
  --set k8sServiceHost=<api-server-ip> \
  --set k8sServicePort=6443
```

---

## 🔄 E2E Flow: Endpoint Update

```
Pod "my-app-abc" fails readiness probe
  → Endpoints controller removes PodIP from Endpoints
    object
  → API Server: Endpoints updated
  → kube-proxy watch fires on all nodes
  → kube-proxy: regenerate iptables rules (remove
    KUBE-SEP-ABC)
  → iptables-restore: atomic rule update
  → No new connections routed to failed Pod
  (In-flight connections may still be affected)
```

---

## ⚖️ Comparison Table

|                             | iptables mode  | IPVS mode          | eBPF (Cilium)   |
| --------------------------- | -------------- | ------------------ | --------------- |
| **Lookup**                  | O(n)           | O(1)               | O(1)            |
| **Scale**                   | <1000 Services | 1000+ Services     | Any scale       |
| **Load balance algorithms** | Random only    | rr, lc, sh, wrr... | Maglev, etc.    |
| **Observability**           | None           | Limited            | Rich (BPF maps) |
| **Complexity**              | Low            | Medium             | High            |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                 |
| ------------------------------------- | --------------------------------------------------------------------------------------- |
| "kube-proxy proxies traffic"          | kube-proxy programs iptables; traffic goes directly Pod→Pod without touching kube-proxy |
| "kube-proxy is optional"              | Required for Services to work (unless using Cilium kube-proxy replacement)              |
| "iptables is always fast enough"      | At 10,000+ Services, iptables sync takes seconds; IPVS/eBPF recommended                 |
| "kube-proxy handles network policies" | Network policy is enforced by CNI (Calico/Cilium), not kube-proxy                       |

---

## 🚨 Failure Modes

| Failure                 | Symptom                          | Fix                                     |
| ----------------------- | -------------------------------- | --------------------------------------- |
| kube-proxy Pod crash    | Services unreachable             | Check `kubectl get pods -n kube-system` |
| iptables sync storm     | Node CPU spike during deployment | Switch to IPVS mode                     |
| Stale rules after crash | Connections to dead Pods         | kube-proxy restores rules on restart    |
| Missing kernel modules  | IPVS mode fails                  | Load `ip_vs`, `ip_vs_rr` kernel modules |

---

## 🔗 Related Keywords

- [Service (K8s)](/kubernetes/service-k8s/) - what kube-proxy implements
- [CoreDNS](/kubernetes/coredns/) - DNS layer above kube-proxy
- [Calico / Cilium](/kubernetes/calico-cilium/) - CNI that can replace kube-proxy
- [Kubernetes Networking (CNI)](/kubernetes/kubernetes-networking-cni/) - overall network stack
- [DaemonSet](/kubernetes/daemonset/) - kube-proxy runs as DaemonSet

---

## 📌 Quick Reference Card

```bash
# Check kube-proxy mode
kubectl get configmap kube-proxy -n kube-system -o yaml | grep mode

# kube-proxy logs
kubectl logs -n kube-system -l k8s-app=kube-proxy

# Check iptables rules (on node)
iptables -t nat -L KUBE-SERVICES | head -20
iptables -t nat -L | grep KUBE | wc -l  # rule count

# IPVS rules (if IPVS mode)
ipvsadm -ln

# kube-proxy metrics
curl http://localhost:10249/metrics | grep kubeproxy
```

---

## 🧠 Think About This

kube-proxy iptables mode updates rules atomically - it replaces ALL iptables rules at once using `iptables-restore`. In a cluster with 5,000 Services and 20,000 endpoints, that's potentially 100,000 rules replaced on every endpoint change. A single deployment rolling update can trigger dozens of iptables rebuilds across hundreds of nodes simultaneously. This "thundering herd" on the control plane is why large clusters must use IPVS or migrate to Cilium's eBPF mode.
