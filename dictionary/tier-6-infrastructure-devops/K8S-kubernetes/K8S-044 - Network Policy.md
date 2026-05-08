---
layout: default
title: "Network Policy"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /kubernetes/network-policy/
id: K8S-044
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Kubernetes Networking (CNI)", "Pod", "Namespace (K8s)"]
used_by: ["K8s Security Hardening", "Pod Security Standards"]
related:
  [
    "Kubernetes Networking (CNI)",
    "Calico / Cilium",
    "Namespace (K8s)",
    "K8s Security Hardening",
  ]
tags: [kubernetes, network-policy, networking, security, isolation, k8s]
---

# Network Policy

## ⚡ TL;DR

A `NetworkPolicy` is a Kubernetes resource that defines **firewall rules for Pod-to-Pod communication**. Without NetworkPolicy, all Pods can talk to all Pods. NetworkPolicy restricts ingress/egress by pod labels, namespace labels, and IP blocks. Requires a CNI plugin that supports it (Calico, Cilium, Weave).

---

## 🔥 Problem This Solves

By default, any Pod in a Kubernetes cluster can communicate with any other Pod. A compromised frontend Pod can reach the database directly. NetworkPolicy implements micro-segmentation: frontend can only talk to backend, backend can only talk to database, database cannot initiate connections.

---

## 📘 Textbook Definition

A NetworkPolicy is a Kubernetes resource that specifies how groups of pods are allowed to communicate with each other and with other network endpoints. NetworkPolicies use label selectors to select pods and define rules to allow specific ingress and egress traffic.

---

## ⏱️ 30 Seconds

```yaml
# Allow only frontend → backend traffic on port 8080
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-ingress
  namespace: my-app
spec:
  podSelector:
    matchLabels:
      app: backend # applies to backend pods
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend # only from frontend pods
      ports:
        - protocol: TCP
          port: 8080
```

---

## 🔩 First Principles

- NetworkPolicy is **additive**: no policy = allow all; one policy = restrict to what's allowed
- When a Pod is selected by ANY NetworkPolicy (for ingress or egress), all traffic NOT explicitly allowed by that policy is **denied**
- `podSelector: {}` (empty) = select all pods in namespace
- NetworkPolicy is namespaced: cross-namespace requires `namespaceSelector`
- CNI plugins must support NetworkPolicy (kube-proxy does NOT enforce it)
- Policies don't affect traffic on the host network namespace

---

## 🧪 Thought Experiment

Imagine your K8s cluster as an open office floor. By default, anyone can walk to any desk (talk to any Pod). You add `NetworkPolicy` fences: the backend desk can only receive visitors from the frontend section (matching labels), and can only send visitors to the database section. The database can only receive from the backend. Now even if an attacker gets into the frontend, they can't reach the database directly.

---

## 🧠 Mental Model / Analogy

NetworkPolicy is **iptables rules for Pods**, but declarative. Instead of writing IP-based firewall rules, you write label-based rules: "pods with label `app=backend` can receive TCP:8080 only from pods with label `app=frontend`." The CNI plugin translates this to actual kernel-level rules on each node.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: NetworkPolicy restricts which Pods can talk to which other Pods. Like a firewall for your cluster's internal network.

**Level 2 - Practitioner**: Select target pods with `podSelector`. Define `ingress` (who can connect TO target) and `egress` (what target can connect TO). Match sources by `podSelector`, `namespaceSelector`, or `ipBlock`.

**Level 3 - Advanced**: Default deny all ingress: `podSelector: {}` with `policyTypes: [Ingress]` and no `ingress` rules. Namespace isolation: `namespaceSelector` with `matchLabels`. Combining selectors: `podSelector` AND `namespaceSelector` in same `from` entry vs separate entries (AND vs OR).

**Level 4 - Expert**: Cilium Network Policy extends NetworkPolicy with L7 (HTTP method, path) rules. `CiliumNetworkPolicy` CRD allows `HTTP{method: GET, path: /api}` rules. Calico `GlobalNetworkPolicy` applies across all namespaces. Egress to external IPs via `ipBlock` with `except` for internal subnets. Node-to-pod communication bypass: NodePort traffic often bypasses NetworkPolicy (depends on CNI).

---

## ⚙️ How It Works

### Default Deny Patterns

```yaml
# 1. Default deny all ingress (apply to namespace)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: my-app
spec:
  podSelector: {} # select all pods
  policyTypes:
    - Ingress
  # no ingress rules = deny all

---
# 2. Default deny all egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: my-app
spec:
  podSelector: {}
  policyTypes:
    - Egress
  # no egress rules = deny all egress

---
# 3. Allow DNS (required if denying all egress)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: my-app
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### AND vs OR in Selectors

```yaml
# AND: pod must be in namespace AND have label
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        team: frontend
    podSelector:             # same list item = AND
      matchLabels:
        app: ui

# OR: pod in namespace OR pod has label
ingress:
- from:
  - namespaceSelector:       # separate list item = OR
      matchLabels:
        team: frontend
  - podSelector:
      matchLabels:
        app: ui
```

### Three-Tier App Isolation

```yaml
# Frontend: ingress from internet (LoadBalancer), egress to backend
# Backend: ingress only from frontend
# Database: ingress only from backend

# backend-network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              tier: frontend
      ports:
        - port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              tier: database
      ports:
        - port: 5432
    - to: # allow DNS
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - port: 53
          protocol: UDP
```

---

## 🔄 E2E Flow: Network Policy Enforcement

```
kubectl apply -f network-policy.yaml
  → Stored in etcd
  → CNI plugin (Calico/Cilium) Watch event
  → CNI translates to node-level rules:
      Calico:  Felix agent programs iptables/eBPF on each node
      Cilium:  Cilium agent programs eBPF maps on each node

Pod A (frontend) → Pod B (backend) on port 8080:
  → Packet leaves Pod A → checked against Pod A's egress rules
  → Packet arrives at Pod B node → checked against Pod B's ingress rules
  → Both rules allow → packet delivered

Pod C (monitoring) → Pod B on port 8080:
  → Pod B has NetworkPolicy; Pod C not in allowed selectors
  → Packet arrives at Pod B node → dropped by CNI rules
  → Pod C sees: connection timed out (not RST)
```

---

## ⚖️ Comparison Table

|                      | NetworkPolicy         | Calico GlobalNetworkPolicy | Cilium L7 Policy  |
| -------------------- | --------------------- | -------------------------- | ----------------- |
| **Scope**            | Namespace             | Cluster                    | Namespace/Cluster |
| **L4 (port)**        | ✅                    | ✅                         | ✅                |
| **L7 (HTTP)**        | ❌                    | ❌                         | ✅                |
| **Standard K8s API** | ✅                    | ❌ (Calico CRD)            | ❌ (Cilium CRD)   |
| **Cross-namespace**  | Via namespaceSelector | ✅                         | ✅                |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                   |
| ------------------------------------- | ----------------------------------------------------------------------------------------- |
| "NetworkPolicy works with any CNI"    | Only CNIs that support it: Calico, Cilium, Weave, Canal. kube-proxy ignores it            |
| "Applying NetworkPolicy is immediate" | CNI agents must propagate rules; brief window of no enforcement                           |
| "NetworkPolicy = namespace isolation" | Namespaces don't isolate network by default; you must add NetworkPolicy                   |
| "Empty podSelector denies everything" | Empty `podSelector: {}` selects ALL pods - combined with policy type, it defaults to deny |

---

## 🚨 Failure Modes

| Failure                             | Symptom                                              | Fix                                                  |
| ----------------------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| CNI doesn't support NetworkPolicy   | Policy applied, no enforcement                       | Verify CNI supports it; `calico`, `cilium` do        |
| Forgot DNS allow on deny-all egress | DNS resolution fails → all external connections fail | Add egress allow for UDP/TCP port 53 to kube-system  |
| AND vs OR confusion                 | Unexpected allow/deny                                | Review: same list entry = AND, separate entries = OR |
| Missing namespace label             | Cross-namespace policy doesn't work                  | Ensure target namespace has correct labels           |

---

## 🔗 Related Keywords

- [Kubernetes Networking (CNI)](/kubernetes/kubernetes-networking-cni/) - CNI enforces NetworkPolicy
- [Calico / Cilium](/kubernetes/calico-cilium/) - CNI plugins with NetworkPolicy support
- [Namespace (K8s)](/kubernetes/namespace-k8s/) - NetworkPolicy scope
- [K8s Security Hardening](/kubernetes/k8s-security-hardening/) - NetworkPolicy as security control

---

## 📌 Quick Reference Card

```bash
# Get all NetworkPolicies
kubectl get networkpolicies -A

# Describe a policy
kubectl describe networkpolicy backend-policy -n my-app

# Test connectivity (using netshoot pod)
kubectl run test --image=nicolaka/netshoot -it --rm -- curl http://backend:8080

# Visualize policies (Cilium Hubble)
hubble observe --namespace my-app

# Check if CNI enforces NetworkPolicy
kubectl get pods -n kube-system | grep -E "calico|cilium|weave"

# Label namespace (for namespaceSelector)
kubectl label namespace my-namespace team=frontend
```

---

## 🧠 Think About This

The most common NetworkPolicy mistake is forgetting that **default is allow-all** until a policy selects a pod. A single NetworkPolicy that selects a pod and specifies only ingress rules still allows ALL egress from that pod. To truly lock down a pod, you need to explicitly define both `policyTypes: [Ingress, Egress]` with appropriate rules. Start with "default deny all" in every namespace and explicitly allow what's needed - this is defense in depth and will catch compromised pods before they can exfiltrate data or lateral move to databases.
