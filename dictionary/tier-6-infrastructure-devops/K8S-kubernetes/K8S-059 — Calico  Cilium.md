---
layout: default
title: "Calico  Cilium"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /kubernetes/calico-cilium/
id: K8S-059
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Kubernetes Networking (CNI)", "Network Policy", "kube-proxy"]
used_by: ["Network Policy", "K8s Security Hardening", "Service Mesh on K8s"]
related:
  [
    "Kubernetes Networking (CNI)",
    "Network Policy",
    "kube-proxy",
    "Service Mesh on K8s",
  ]
tags: [kubernetes, calico, cilium, cni, ebpf, networking, network-policy, k8s]
---

# Calico / Cilium

## ⚡ TL;DR

**Calico** is a CNI plugin using BGP routing or VXLAN for Pod networking, with full Kubernetes NetworkPolicy support and its own `GlobalNetworkPolicy` CRD for cluster-wide rules. **Cilium** uses Linux eBPF for networking (replacing iptables/kube-proxy), offering L7-aware NetworkPolicy, Hubble flow observability, and optional service mesh capabilities. Cilium = more powerful; Calico = more mature and widely deployed.

---

## 🔥 Problem This Solves

Basic CNIs (Flannel) provide Pod networking but no NetworkPolicy enforcement. Calico and Cilium add: network security policies, advanced routing, observability, and (for Cilium) eBPF-based dataplane that scales better than iptables at thousands of Pods.

---

## 📘 Textbook Definition

Calico is a CNI plugin that provides Pod networking via BGP or VXLAN and implements Kubernetes NetworkPolicy and its own extended policy API. Cilium is a CNI plugin using eBPF technology to provide networking, security, and observability for Kubernetes with L7-aware policies and a built-in network flow visibility tool (Hubble).

---

## ⏱️ 30 Seconds

```
Calico strengths:
  ✅ BGP routing (no overlay, lower overhead)
  ✅ GlobalNetworkPolicy (cross-namespace)
  ✅ Mature, widely deployed
  ✅ WireGuard encryption between nodes
  ✅ IPAM flexibility

Cilium strengths:
  ✅ eBPF dataplane (O(1) vs iptables O(n))
  ✅ Replaces kube-proxy entirely
  ✅ L7 NetworkPolicy (HTTP, gRPC, Kafka)
  ✅ Hubble: real-time network flow observability
  ✅ Service mesh capabilities (Cilium Service Mesh)
  ✅ Transparent encryption (WireGuard)
```

---

## 🔩 First Principles

**Calico architecture:**

- Felix: DaemonSet on every node; programs iptables/eBPF for routing and NetworkPolicy
- BIRD: BGP daemon on each node; advertises pod CIDR routes
- calico-kube-controllers: watches K8s API, syncs to Felix
- Typha: scales by caching API for Felix in large clusters

**Cilium architecture:**

- cilium-agent: DaemonSet; programs eBPF maps for networking, security, observability
- eBPF programs: attached to network interfaces, kernel hooks — process packets in kernel
- Hubble relay + UI: collects flow data from agents → L7 visibility
- No more iptables for Service routing (kube-proxy replacement mode)

---

## 🧪 Thought Experiment

Cluster with 10,000 Pods and 5,000 Services. With kube-proxy + iptables: each node has ~50,000 iptables rules. Adding a new Service = update all 10,000 nodes with new iptables rules. Lookup = O(n) linear scan. With Cilium + eBPF: Service lookup via eBPF hash maps = O(1) constant time. Adding Service = update eBPF map entries (microseconds). Significant latency difference at scale.

---

## 🧠 Mental Model / Analogy

Calico is like a **traditional postal network**: sorting offices (Felix) maintain routing tables (iptables), mail carriers (BGP routes) know which district has which addresses. Cilium is like a **GPS-connected smart delivery system**: routes stored in fast-lookup hash tables (eBPF maps), with real-time traffic monitoring (Hubble), able to understand package contents (L7) to make smart routing decisions.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Both provide Pod networking and NetworkPolicy. Cilium is newer and more feature-rich with eBPF.

**Level 2 — Practitioner**: Calico: install with `kubectl apply -f calico.yaml`. Use `calicoctl` for GlobalNetworkPolicy. Cilium: install with `cilium install`. `cilium status` / `cilium connectivity test` to verify. Both integrate with existing NetworkPolicy YAML.

**Level 3 — Advanced**: Calico GlobalNetworkPolicy applies across all namespaces. Cilium CiliumNetworkPolicy adds L7 rules (HTTP methods/paths, gRPC services). Cilium BPF Host Routing mode: bypass iptables completely for Service routing. Hubble: `hubble observe` to see live flows between Pods.

**Level 4 — Expert**: Calico Enterprise: threat detection, compliance reporting, UI. Cilium Mesh: multi-cluster service discovery + east-west traffic encryption (Wireguard). Cilium + Envoy: L7 policy implemented via embedded Envoy sidecar-less proxy. Cilium mutual TLS via SPIFFE/SPIRE: cryptographic identity without service mesh sidecars. Calico performance: eBPF mode available as alternative to iptables for Calico too. Dual-stack (IPv4 + IPv6): both Calico and Cilium support.

---

## ⚙️ How It Works

### Calico — BGP Mode

```
Each node runs BIRD BGP daemon
Node 1 (Pod CIDR: 10.244.1.0/24):
  BIRD advertises: "I have 10.244.1.0/24"
  → peers with Node 2, Node 3 (or via BGP route reflector)

Node 2 routing table (programmed by Felix):
  10.244.1.0/24 via 192.168.0.1 (Node 1's IP)

Pod-to-pod:
  Pod A (10.244.1.5) → veth → Node 1 kernel → IP routing →
  → 10.244.2.x goes to Node 2 (BGP route) → Node 2 → Pod B
  No encapsulation overhead!
```

### Calico — GlobalNetworkPolicy

```yaml
# Cluster-wide: deny all non-system traffic by default
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: default-deny-all
spec:
  selector: all()
  types:
    - Ingress
    - Egress
  egress:
    - action: Allow
      destination:
        selector: k8s-app == 'kube-dns' # allow DNS
    - action: Allow
      destination:
        nets: ["169.254.169.254/32"] # allow metadata service

---
# Allow specific app-to-app communication
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  selector: tier == 'backend'
  types:
    - Ingress
  ingress:
    - action: Allow
      source:
        selector: tier == 'frontend'
      destination:
        ports: [8080]
```

### Cilium — L7 NetworkPolicy

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: allow-get-only
spec:
  endpointSelector:
    matchLabels:
      app: backend
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: "GET" # only GET allowed
                path: "/api/v1/.*" # only this path prefix
```

### Cilium Hubble Observability

```bash
# Install Hubble relay
cilium hubble enable --ui

# Observe live network flows
hubble observe --namespace my-app --follow

# Example output:
# Apr 15 10:23:01.234: my-app/frontend-pod → my-app/backend-pod
#   to-endpoint FORWARDED (HTTP/1.1 GET /api/v1/users)
# Apr 15 10:23:01.235: my-app/frontend-pod → my-app/backend-pod
#   to-endpoint FORWARDED (HTTP/1.1 200 OK)
# Apr 15 10:23:02.100: my-app/monitor-pod → my-app/backend-pod
#   to-endpoint DROPPED (Policy denied)

# Flows per service
hubble observe --service my-app/backend --last 100

# Hubble UI
cilium hubble ui   # opens browser
```

### Cilium eBPF vs iptables Performance

```
iptables (kube-proxy):
  - Linear O(n) lookup through chain rules
  - 10,000 services = 100,000+ iptables rules
  - Rule update: lock entire table → brief packet drops
  - CPU: significant at high packet rates

eBPF (Cilium):
  - Hash map O(1) lookup
  - Updates atomic (no traffic impact)
  - Programs run in kernel (no context switch to userspace)
  - CPU: 30-50% lower at scale

Benchmark (Cilium): 100Gbps line rate on 10GbE with < 10% CPU
```

---

## 🔄 E2E Flow: Cilium L7 Policy Enforcement

```
frontend-pod: curl -X DELETE http://backend:8080/api/v1/users/123

Cilium agent on frontend's node:
  eBPF hook on frontend-pod veth egress:
    1. Identify source identity: frontend-pod (label app=frontend)
    2. Identify destination: backend (label app=backend), port 8080
    3. L3/L4 policy: frontend → backend:8080 allowed? ✅
    4. L7 policy check needed? YES (HTTP policy exists)
    5. Redirect to Envoy proxy (embedded in node, not sidecar)

Envoy proxy:
    6. Parse HTTP: method=DELETE, path=/api/v1/users/123
    7. Check CiliumNetworkPolicy: only GET /api/v1/.* allowed
    8. DELETE is not in allowed methods → DROP
    9. Return 403 to frontend-pod

frontend-pod: receives HTTP 403 Forbidden
```

---

## ⚖️ Comparison Table

| Feature                    | Calico                          | Cilium                   |
| -------------------------- | ------------------------------- | ------------------------ |
| **Dataplane**              | iptables (default) / eBPF (opt) | eBPF native              |
| **kube-proxy replacement** | Partial                         | ✅ Full                  |
| **NetworkPolicy L3/L4**    | ✅                              | ✅                       |
| **NetworkPolicy L7**       | ❌                              | ✅ (HTTP, gRPC, Kafka)   |
| **Observability**          | Basic                           | Hubble (flow + topology) |
| **BGP routing**            | ✅ Native                       | ✅ (Cilium BGP)          |
| **Maturity**               | Very mature                     | Mature (CNCF graduated)  |
| **Service mesh**           | ❌                              | Cilium Service Mesh      |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                          |
| ----------------------------------- | ---------------------------------------------------------------- |
| "Cilium requires eBPF expertise"    | Install is simple; eBPF complexity is hidden; CLI is intuitive   |
| "Calico is outdated"                | Calico is actively developed; enterprise version is feature-rich |
| "L7 policy requires a service mesh" | Cilium provides L7 policy without sidecars                       |
| "Changing CNI is easy"              | Almost impossible post-cluster-setup without full reinstall      |

---

## 🚨 Failure Modes

| Failure                       | Symptom                                   | Fix                                               |
| ----------------------------- | ----------------------------------------- | ------------------------------------------------- | --------------------------------------- |
| Calico BIRD BGP peering fails | Pods on different nodes can't communicate | Check BGP peering status: `calicoctl node status` |
| Cilium eBPF maps full         | New connections dropped silently          | Check: `cilium bpf ct list global                 | wc -l`; tune connection tracking limits |
| Hubble relay OOM              | Hubble observe fails                      | Increase Hubble relay memory limits               |
| Calico Felix crash            | NetworkPolicy not enforced                | Restart calico-node DaemonSet pod                 |

---

## 🔗 Related Keywords

- [Kubernetes Networking (CNI)](/kubernetes/kubernetes-networking-cni/) — CNI spec both implement
- [Network Policy](/kubernetes/network-policy/) — what both enforce
- [kube-proxy](/kubernetes/kube-proxy/) — Cilium can replace kube-proxy
- [Service Mesh on K8s](/kubernetes/service-mesh-on-k8s/) — Cilium offers mesh capabilities

---

## 📌 Quick Reference Card

```bash
# Calico
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
calicoctl get nodes
calicoctl get felixconfiguration default
calicoctl get globalnetworkpolicies

# Cilium
cilium install [--version 1.14.0]
cilium status
cilium connectivity test
hubble observe --namespace my-app --follow
hubble status

# Check which CNI is installed
ls /etc/cni/net.d/
kubectl get pods -n kube-system -l k8s-app=calico-node
kubectl get pods -n kube-system -l k8s-app=cilium

# Debug pod connectivity
cilium policy trace --src-endpoint <id> --dst-endpoint <id>
calicoctl get networkpolicies -A
```

---

## 🧠 Think About This

Cilium's eBPF approach represents a fundamental shift in Linux kernel networking for containers. Traditional networking (iptables, IPVS) was designed for the pre-container era. eBPF allows Cilium to attach custom programs to every network event in the kernel — packet entering a veth, TCP connection establishment, HTTP request parsing — with near-zero overhead. The Hubble flow data this generates (which pod talked to which, what HTTP methods, which connections were dropped by policy) is invaluable for security auditing, troubleshooting, and compliance. For new clusters in 2024, Cilium is the default choice for teams that care about security, observability, and performance at scale.
