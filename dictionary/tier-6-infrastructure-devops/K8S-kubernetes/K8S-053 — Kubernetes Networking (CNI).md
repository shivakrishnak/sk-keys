---
layout: default
title: "Kubernetes Networking (CNI)"
parent: "Kubernetes"
nav_order: 53
permalink: /kubernetes/kubernetes-networking-cni/
number: "K8S-053"
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Pod", "Node", "kube-proxy", "CoreDNS"]
used_by: ["Network Policy", "Calico / Cilium", "Service Mesh on K8s"]
related:
  [
    "Calico / Cilium",
    "Network Policy",
    "kube-proxy",
    "CoreDNS",
    "Service (K8s)",
  ]
tags:
  [kubernetes, cni, networking, pod-networking, flannel, calico, cilium, k8s]
---

# Kubernetes Networking (CNI)

## ⚡ TL;DR

The **Container Network Interface (CNI)** is the plugin spec for Kubernetes pod networking. CNI plugins (Flannel, Calico, Cilium, Weave) implement the K8s networking model: every Pod gets a unique routable IP, all Pods can reach each other without NAT. kube-proxy handles Service IPs; CNI handles Pod-to-Pod routing.

---

## 🔥 Problem This Solves

Containers inside the same Pod share a network namespace. But how do Pods on different nodes communicate? How are unique IPs assigned? How are NetworkPolicy firewall rules enforced? CNI plugins solve all of this — without CNI, Pods can't communicate across nodes.

---

## 📘 Textbook Definition

The Container Network Interface (CNI) is a specification and libraries for writing plugins to configure network interfaces in Linux containers. In Kubernetes, a CNI plugin is responsible for: assigning Pod IP addresses, setting up Pod network interfaces, routing inter-pod traffic, and implementing NetworkPolicy rules.

---

## ⏱️ 30 Seconds

```
Kubernetes Networking Model:
  1. Every Pod gets a unique IP address
  2. Any Pod can communicate with any other Pod (without NAT)
  3. Nodes can communicate with all Pods
  4. Pod IPs are routable on the cluster network

CNI is responsible for implementing rules 1-4.
Popular CNIs: Flannel (simple), Calico (BGP + policy), Cilium (eBPF + L7)
```

---

## 🔩 First Principles

- CNI plugin called by kubelet when Pod is created/deleted
- CNI assigns IP from `--pod-network-cidr` (set at cluster init)
- CNI sets up `veth` pair: one end in Pod's network namespace, one in host network
- Cross-node routing: varies by CNI (tunneling, BGP, host-routing)
- `ip addr show` in a Pod shows the CNI-assigned IP
- CNI config at `/etc/cni/net.d/` on each node

---

## 🧪 Thought Experiment

Pod A on Node 1 (10.244.1.2) wants to talk to Pod B on Node 2 (10.244.2.3). Without CNI, Node 1 has no idea how to route 10.244.2.3. The CNI plugin creates routes: Node 1 knows "10.244.2.0/24 is on Node 2 at 192.168.0.2". Packet: Pod A → veth → Node 1 routing table → Node 2 → veth → Pod B. CNI makes this work.

---

## 🧠 Mental Model / Analogy

CNI is like the **telephone network infrastructure** for Pods: it assigns each Pod a unique phone number (IP), installs phone lines (veth pairs), and sets up the routing exchange (routing tables or BGP) so any phone can call any other phone. Without CNI, Pods are isolated islands with no way to communicate.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: CNI gives Pods IP addresses and makes them able to talk to each other. You install one CNI plugin when setting up a cluster.

**Level 2 — Practitioner**: Main CNI options: Flannel (simple overlay, VXLAN), Calico (BGP routing or VXLAN, NetworkPolicy), Cilium (eBPF-based, L7 policy, Hubble observability). Must install CNI after `kubeadm init` before nodes become Ready.

**Level 3 — Advanced**: VXLAN tunneling: encapsulates Pod packets in UDP packets between nodes (overlay). BGP (Calico): nodes advertise Pod CIDRs to BGP peers → native routing without tunneling (lower overhead). eBPF (Cilium): replaces kube-proxy + adds L7 policy, Hubble flow observability, Wireguard encryption.

**Level 4 — Expert**: Multi-NIC: CNI chains (MULTUS) for multiple network interfaces per Pod (SR-IOV, DPDK for telco/HPC). IPAM plugins: host-local (per-node ranges), AWS VPC CNI (VPC-native IPs, each Pod gets a real VPC IP address, no overlay). Azure CNI: same VNet-native IPs. CNI performance: eBPF-based CNIs (Cilium) have significantly lower latency and CPU overhead than iptables-based kube-proxy + VXLAN at scale.

---

## ⚙️ How It Works

### Pod Network Setup (per Pod creation)

```
kubelet creates Pod sandbox (pause container):
  1. Creates network namespace: /proc/<pid>/ns/net
  2. Calls CNI plugin via: /etc/cni/net.d/10-flannel.conflist
  3. CNI plugin:
     a. Allocate IP from IPAM (host-local, IPAM server)
     b. Create veth pair: eth0 (Pod ns) ↔ vethXXX (host ns)
     c. Set IP on eth0 in Pod namespace
     d. Add default route in Pod: 0.0.0.0/0 via 10.244.0.1
     e. Add ARP/route entry on host for this Pod
     f. Return: IP, gateway, routes to kubelet

Pod networking:
  Pod has: eth0 → 10.244.1.5/24, gw 10.244.1.1
  Host has: vethXXX on bridge cni0 (10.244.1.1)
```

### Cross-Node Communication Models

**VXLAN (Flannel default):**

```
Pod A (10.244.1.2) → eth0 → veth → cni0 bridge → flannel.1 (VTEP)
  → VXLAN encapsulate: original packet wrapped in UDP port 4789
  → Node1 physical NIC → network → Node2 physical NIC
  → VXLAN decapsulate → flannel.1 → Pod B routing → eth0 → Pod B
```

**BGP (Calico):**

```
Each node advertises its Pod CIDR via BGP:
  Node1: "I own 10.244.1.0/24" → BGP route to all nodes/routers
  Node2: "I own 10.244.2.0/24"

Pod A → eth0 → cali... (veth) → kernel routing:
  Destination 10.244.2.0/24 via Node2 (192.168.0.2) → direct IP routing
  No encapsulation overhead
```

**AWS VPC CNI (VPC-native):**

```
Each Node (EC2 instance) gets multiple ENIs
Each ENI gets multiple secondary IPs from VPC subnet

Pod gets a real VPC IP (e.g., 172.16.1.15)
  No overlay needed
  Pod traffic = VPC-native routing
  Security groups apply to Pod IPs directly
```

### CNI Comparison

```
Flannel:
  - Simple VXLAN overlay
  - No NetworkPolicy support (need Calico or others)
  - Good for: development, simple deployments

Calico:
  - BGP routing (no overlay) or VXLAN
  - Full NetworkPolicy support
  - GlobalNetworkPolicy for cluster-wide rules
  - Good for: production, BGP-capable network infra

Cilium:
  - eBPF-based (no iptables)
  - L7-aware NetworkPolicy (HTTP, gRPC, Kafka)
  - Hubble: built-in network observability
  - Service mesh features (Cilium Service Mesh)
  - Good for: high-performance, security-conscious, observability

AWS VPC CNI:
  - VPC-native Pod IPs
  - No overlay overhead
  - Integrates with VPC SecurityGroups for pods
  - Limited to AWS (EKS-native)
```

---

## 🔄 E2E Flow: Pod-to-Pod Communication (Cilium/eBPF)

```
Pod A (10.244.1.5) → curl http://10.244.2.10 (Pod B)

On Node 1:
  1. Pod A sends packet to 10.244.2.10
  2. eBPF hook on veth ingress:
     - Check NetworkPolicy: is Pod A allowed to send to Pod B? ✅
     - Lookup: where is 10.244.2.10? → Node 2 (192.168.0.2)
  3. Cilium encapsulates (VXLAN) or routes natively (Wireguard tunnel)

On Node 2:
  1. eBPF hook on host network ingress:
     - Decapsulate
     - Check NetworkPolicy: is Pod A allowed to talk to Pod B? ✅
  2. Route to Pod B's network namespace
  3. Pod B receives packet

Zero iptables involved. O(1) eBPF map lookups vs O(n) iptables chains.
```

---

## ⚖️ Comparison Table

|                   | Flannel | Calico    | Cilium      | AWS VPC CNI    |
| ----------------- | ------- | --------- | ----------- | -------------- |
| **Dataplane**     | VXLAN   | BGP/VXLAN | eBPF        | VPC routing    |
| **NetworkPolicy** | ❌      | ✅        | ✅ + L7     | Partial        |
| **Performance**   | Medium  | Good      | Best        | Best (AWS)     |
| **Observability** | Basic   | ✅        | Hubble ✅✅ | VPC Flow Logs  |
| **Complexity**    | Low     | Medium    | Medium-High | Low (AWS-only) |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| "kube-proxy is the CNI"                  | kube-proxy handles Service IPs (virtual); CNI handles Pod IPs (real)   |
| "Any CNI enforces NetworkPolicy"         | Only CNIs with NetworkPolicy support (Calico, Cilium); Flannel doesn't |
| "Pod IPs are stable"                     | Pod IPs change when Pod restarts; use Services for stable access       |
| "CNI can be changed after cluster setup" | Extremely difficult and risky; choose carefully at setup time          |

---

## 🚨 Failure Modes

| Failure                             | Symptom                                               | Fix                                                                |
| ----------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------ |
| No CNI installed                    | Nodes NotReady: `container runtime network not ready` | Install CNI plugin (kubectl apply -f <cni-manifest>)               |
| Pod CIDR overlaps with host network | Pod IPs unreachable or routing conflicts              | Choose non-overlapping pod-network-cidr                            |
| CNI plugin crashloop                | Pods stuck in Init: NetworkNotReady                   | Check CNI pod logs in kube-system                                  |
| MTU mismatch                        | TCP connections fail with large payloads              | Match CNI MTU to physical network MTU (VPC: 8950 for jumbo frames) |

---

## 🔗 Related Keywords

- [Calico / Cilium](/kubernetes/calico-cilium/) — two leading CNI implementations
- [Network Policy](/kubernetes/network-policy/) — firewall rules enforced by CNI
- [kube-proxy](/kubernetes/kube-proxy/) — Service IP routing (separate from CNI)
- [CoreDNS](/kubernetes/coredns/) — DNS for Pods (uses Pod IPs assigned by CNI)

---

## 📌 Quick Reference Card

```bash
# Check CNI installed
kubectl get pods -n kube-system | grep -E "flannel|calico|cilium|weave"

# Check pod networking
kubectl exec -it my-pod -- ip addr
kubectl exec -it my-pod -- ip route

# Node pod CIDR
kubectl get node <node> -o jsonpath='{.spec.podCIDR}'

# Check connectivity
kubectl exec -it my-pod -- ping <other-pod-ip>
kubectl exec -it my-pod -- curl http://<pod-ip>:<port>

# Cilium status
cilium status
cilium connectivity test

# Calico status
calicoctl get nodes
calicoctl get felixconfigurations
```

---

## 🧠 Think About This

Choosing a CNI plugin is one of the most consequential infrastructure decisions you'll make — it's very hard to change later. The key questions: (1) Do you need NetworkPolicy? → Rule out Flannel. (2) Do you want maximum observability? → Cilium + Hubble. (3) Do you need minimum overhead at extreme scale? → Cilium eBPF replaces kube-proxy, removing O(n) iptables chains. (4) Are you on EKS and want VPC-native pod IPs? → AWS VPC CNI. The industry momentum in 2024 is clearly toward Cilium: eBPF-based, kube-proxy replacement, L7 policy, built-in service mesh capabilities, and Hubble flow visualization make it the most capable platform CNI.
