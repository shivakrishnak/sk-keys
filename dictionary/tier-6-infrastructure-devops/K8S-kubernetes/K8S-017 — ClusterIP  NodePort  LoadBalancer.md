---
layout: default
title: "ClusterIP  NodePort  LoadBalancer"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /kubernetes/clusterip-nodeport-loadbalancer/
id: K8S-017
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Service (K8s)", "Node", "Namespace (K8s)"]
used_by: ["Ingress", "API Gateway (Microservices)"]
related:
  [
    "Service (K8s)",
    "Ingress",
    "kube-proxy",
    "Ingress Controller",
    "Network Policy",
  ]
tags:
  [
    kubernetes,
    clusterip,
    nodeport,
    loadbalancer,
    service-types,
    k8s,
    networking,
  ]
---

# ClusterIP / NodePort / LoadBalancer

## ⚡ TL;DR

Three primary Kubernetes Service types: **ClusterIP** (internal-only virtual IP), **NodePort** (exposes on each node's IP at a static port), **LoadBalancer** (cloud LB with external IP). For HTTP production traffic, use **Ingress** on top of ClusterIP instead of LoadBalancer per service.

---

## 🔥 Problem This Solves

Different workloads need different exposure levels: internal microservices need cluster-internal access, admin tools need node-level access for testing, and public APIs need external internet access. The three Service types address each scenario.

---

## 📘 Textbook Definition

Kubernetes Service types control how a Service is exposed: ClusterIP creates a cluster-internal virtual IP; NodePort exposes the Service on each Node's IP at a static port; LoadBalancer provisions a cloud-provider load balancer. Each type builds on the previous.

---

## ⏱️ 30 Seconds

```yaml
# ClusterIP (default) — internal only
spec:
  type: ClusterIP
  # clusterIP: 10.96.0.100 (auto-assigned)

# NodePort — accessible at NodeIP:30080
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080    # 30000-32767

# LoadBalancer — cloud LB with external IP
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
  # EXTERNAL-IP assigned by cloud (e.g., 34.105.x.x)
```

---

## 🔩 First Principles

- **ClusterIP**: only reachable from within the cluster; kube-proxy DNAT to Pod IPs
- **NodePort**: opens a port on **every** node; external traffic → NodeIP:NodePort → ClusterIP → Pod
- **LoadBalancer**: cloud provider creates LB; LB → NodePort → ClusterIP → Pod (3 hops)
- Each type is a superset of the previous (LoadBalancer has a NodePort has a ClusterIP)

---

## 🧪 Thought Experiment

You have 10 microservices. If you create one LoadBalancer Service per microservice, you get 10 cloud load balancers at significant cost. Better: use one LoadBalancer for an Ingress Controller, then ClusterIP for all services — Ingress routes by path/host to each ClusterIP internally.

---

## 🧠 Mental Model / Analogy

Think of access levels:

- **ClusterIP** = internal extension number (only colleagues can call)
- **NodePort** = direct desk phone (anyone who knows the number can call)
- **LoadBalancer** = published company phone number (goes through receptionist/LB)

---

## 📶 Gradual Depth

**Level 1 — Beginner**: ClusterIP = private, NodePort = semi-public (test), LoadBalancer = public.

**Level 2 — Practitioner**: LoadBalancer creates a NodePort internally. NodePort creates a ClusterIP internally. They stack. `kubectl get svc` shows all three IPs.

**Level 3 — Advanced**: `externalTrafficPolicy: Local` on NodePort/LoadBalancer preserves source IP but means only nodes with local Pods will forward traffic — uneven load. `externalTrafficPolicy: Cluster` (default) load-balances but does SNAT, losing client IP.

**Level 4 — Expert**: MetalLB provides LoadBalancer type in bare-metal clusters (BGP or ARP mode). Cloud controller manager watches Service type=LoadBalancer and provisions cloud LB. `loadBalancerSourceRanges` restricts source IPs to whitelist at LB level.

---

## ⚙️ How It Works

### Traffic Flow

```
LoadBalancer (34.105.x.x:80)
  ↓ cloud LB
NodePort (NodeIP:30080) — every node
  ↓ iptables/IPVS
ClusterIP (10.96.0.100:80)
  ↓ iptables/IPVS
Pod (10.244.x.x:8080)
```

### Service Type Comparison

| Type           | External       | Cluster Internal  | Port Range  | Cost          |
| -------------- | -------------- | ----------------- | ----------- | ------------- |
| `ClusterIP`    | ❌             | ✅ ClusterIP      | N/A         | Free          |
| `NodePort`     | ✅ NodeIP:port | ✅ ClusterIP      | 30000-32767 | Free          |
| `LoadBalancer` | ✅ External IP | ✅ ClusterIP      | Any         | Cloud LB cost |
| `ExternalName` | CNAME only     | ✅                | N/A         | Free          |
| Headless       | ❌             | Pod DNS A records | N/A         | Free          |

### Best Practice for HTTP Traffic

```
Public HTTP/HTTPS:
  1 LoadBalancer Service → nginx-ingress or traefik
  → Ingress rules → ClusterIP Services → Pods

Instead of:
  10 LoadBalancer Services (one per microservice) ← expensive!
```

---

## 🔄 E2E Flow: LoadBalancer Request

```
Browser → 34.105.x.x:443 (cloud LB external IP)
  → Cloud LB routes to any healthy node
  → Node: NodePort 30443 → iptables DNAT
  → ClusterIP 10.96.0.100:443 → iptables DNAT
  → Pod 10.244.2.15:8443
  → Response returns same path
```

---

## ⚖️ Comparison Table

|                  | Use When                                                  | Avoid When                                |
| ---------------- | --------------------------------------------------------- | ----------------------------------------- |
| **ClusterIP**    | Internal microservice comms                               | Needs external access                     |
| **NodePort**     | Dev/testing, on-prem, specific port                       | Production HTTP (no TLS, no path routing) |
| **LoadBalancer** | Ingress controller, TCP services, bare-metal with MetalLB | One per service (expensive)               |
| **Ingress**      | HTTP/HTTPS with host/path routing                         | TCP/UDP (use LoadBalancer directly)       |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                           |
| ---------------------------------------- | --------------------------------------------------------------------------------- |
| "LoadBalancer = Ingress"                 | LoadBalancer is L4; Ingress is L7 (HTTP routing)                                  |
| "NodePort is only for dev"               | Valid for on-prem/bare-metal production if you handle LB externally               |
| "ClusterIP is a real IP"                 | ClusterIP is a virtual IP; kube-proxy rewrites packets; it never appears on a NIC |
| "One Service = one LoadBalancer is fine" | Each LB costs money; use one LB for Ingress controller instead                    |

---

## 🚨 Failure Modes

| Failure              | Symptom                          | Fix                                                |
| -------------------- | -------------------------------- | -------------------------------------------------- |
| LoadBalancer pending | `EXTERNAL-IP: <pending>` forever | No cloud provider or MetalLB installed             |
| NodePort conflict    | Service creation fails           | NodePort range 30000-32767 only; port may be taken |
| Client IP lost       | Logs show node IP not client IP  | Use `externalTrafficPolicy: Local` (with caveats)  |
| NodePort unreachable | Firewall blocks node ports       | Open 30000-32767 in security group/firewall        |

---

## 🔗 Related Keywords

- [Service (K8s)](/kubernetes/service-k8s/) — Service abstraction
- [Ingress](/kubernetes/ingress/) — L7 HTTP routing
- [kube-proxy](/kubernetes/kube-proxy/) — implements Service routing
- [Network Policy](/kubernetes/network-policy/) — restrict Service access
- [Ingress Controller](/kubernetes/ingress-controller/) — receives external traffic

---

## 📌 Quick Reference Card

```bash
# Check Service type and IPs
kubectl get svc -o wide

# Test ClusterIP from inside cluster
kubectl run test --rm -it --image=busybox -- wget -O- http://my-svc

# Test NodePort from outside
curl http://<NODE_IP>:30080

# Test LoadBalancer
curl http://<EXTERNAL_IP>:80

# Change Service type
kubectl patch svc my-svc -p '{"spec":{"type":"LoadBalancer"}}'
```

---

## 🧠 Think About This

Why does `EXTERNAL-IP: <pending>` happen even on cloud clusters? The Kubernetes cloud-controller-manager must be configured and authenticated to provision cloud load balancers. On EKS, you need the AWS Load Balancer Controller. On GKE/AKS, it's automatic. In bare-metal environments, you need MetalLB or a similar layer — Kubernetes doesn't provision hardware LBs itself.
