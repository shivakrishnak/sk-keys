---
layout: default
title: "Network Policies"
parent: "Networking"
nav_order: 199
permalink: /networking/network-policies/
number: "0199"
category: Networking
difficulty: ★★★
depends_on: Firewall, Kubernetes, Network Topologies, Zero Trust Networking
used_by: Kubernetes, Platform & Modern SWE, Microservices, Security
related: Zero Trust Networking, mTLS, Service Discovery, Overlay Networks, Firewall
tags:
  - networking
  - network-policies
  - kubernetes
  - firewall
  - micro-segmentation
  - calico
  - cilium
---

# 199 — Network Policies

⚡ TL;DR — Kubernetes Network Policies are namespace-scoped rules that control which pods can talk to which other pods and external endpoints. By default, Kubernetes has no network isolation — every pod can reach every other pod. Network Policies provide **micro-segmentation**: whitelist-based rules (default-deny, then explicitly allow required traffic). Enforced by the CNI plugin (Calico, Cilium, Weave Net — not by kube-apiserver). Essential for Zero Trust within a Kubernetes cluster.

---

### 🔥 The Problem This Solves

By default, if a Kubernetes pod is compromised (RCE exploit), the attacker can make outbound connections to any other pod in the cluster — databases, admin services, payment services. Without Network Policies, a compromised frontend pod can talk directly to the database. Network Policies implement micro-segmentation: "only allow payment-service to connect to postgres on port 5432." This contains breach blast radius to a single service's permissions.

---

### 📘 Textbook Definition

**Kubernetes Network Policy:** A namespace-scoped Kubernetes resource (`networking.k8s.io/v1/NetworkPolicy`) that specifies how groups of pods are allowed to communicate with each other and with network endpoints, using label selectors for pod identification. Policies are additive (OR logic) and whitelist-based. **Requires a CNI plugin** that supports Network Policy enforcement (Calico, Cilium, Weave Net, Antrea). The built-in `kubenet` plugin does NOT enforce Network Policies.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Network Policies = firewall rules for Kubernetes pods, using label selectors instead of IP addresses. Default-deny-all + explicit allows = micro-segmentation.

**One analogy:**

> Without Network Policies, a Kubernetes cluster is like an office building with no internal doors — anyone who gets past security can walk into any room. Network Policies add internal door locks: "only the HR team badge can open the HR server room; only the payments team badge can open the payments vault."

---

### 🔩 First Principles Explanation

**DEFAULT KUBERNETES NETWORKING (NO POLICIES):**

```
Without Network Policies:
  frontend pod (192.168.1.10) → CAN reach → postgres pod (192.168.1.50:5432)
  frontend pod → CAN reach → payment-service (192.168.1.30:8080)
  ANY pod → CAN reach → ANY other pod (flat network)

  If frontend is compromised via SQL injection or XSS+SSRF:
    Attacker can reach postgres directly: SELECT * FROM users
    Attacker can call payment APIs directly: POST /transfer
    No isolation between services
```

**NETWORK POLICY ENFORCEMENT:**

```
With default-deny + explicit allows:

Step 1: Default deny all ingress and egress in namespace
  → No pod can initiate or receive any connection
  → (Production namespace isolation)

Step 2: Allow specific traffic
  → Only payment-service pod can connect to postgres on 5432
  → Only api-gateway can connect to backend-service on 8080
  → Only monitoring namespace pods can scrape metrics (9090)
  → DNS: always allow UDP 53 to kube-dns (or nothing works)

Key concept: Policies are ADDITIVE — multiple policies on the same
  pod are OR'd together (if ANY policy allows, traffic is allowed)
  There is no DENY rule — only ALLOW (whitelist model)

Label-based selection (not IP-based):
  podSelector: { matchLabels: { app: postgres } }
  → Applies to any pod with label app=postgres
  → Works even as pods restart and get new IPs
```

**POLICY TYPES:**

```
policyTypes:
  - Ingress  → controls inbound connections TO selected pods
  - Egress   → controls outbound connections FROM selected pods

Ingress rule components:
  from: → who can connect (podSelector, namespaceSelector, ipBlock)
  ports: → on what ports (port, protocol)

Egress rule components:
  to: → where pods can connect
  ports: → on what ports

Selectors:
  podSelector: {} → matches ALL pods in namespace
  podSelector: matchLabels: {app: postgres} → specific pods
  namespaceSelector: matchLabels: {env: prod} → pods in matching namespaces
  ipBlock: cidr: 10.0.0.0/8 → IP ranges (for external services)
```

**CNI ENFORCEMENT:**

```
Network Policy is just a spec in etcd — the CNI plugin enforces it.

Calico:
  Uses iptables/eBPF to enforce policies
  Also supports GlobalNetworkPolicy (cluster-wide, not namespace-scoped)
  Supports Egress policies with FQDN matching (allow egress to *.amazonaws.com)

Cilium:
  eBPF-based (no iptables)
  Richer policy: Layer 7 (HTTP, Kafka, DNS level policies)
  CiliumNetworkPolicy: L7 rules like "allow HTTP GET /api/products only"
  High performance: kernel-level enforcement

Without compatible CNI (e.g., plain kubenet):
  Network Policy objects ARE accepted by apiserver
  But they have NO EFFECT — traffic not blocked
  This is a common misconfiguration trap!
```

---

### 🧪 Thought Experiment

**THE MISCONFIGURATION TRAP:**
A team applies a default-deny NetworkPolicy in their namespace, then deploys payment-service. They test: "can't reach postgres from other services — good!" Then they add a specific allow rule for payment-service. Six months later, a new service "analytics" needs to read from postgres for reporting. Developer adds a new NetworkPolicy allowing analytics → postgres. It works. But they forgot that they also need an egress policy on analytics — they only wrote ingress. Analytics can send data TO postgres (read queries) but also to any external address. If analytics is compromised, it can exfiltrate data to external endpoints. **Lesson: Always write BOTH ingress (who can connect to me) and egress (where can I connect to) policies.**

---

### 🧠 Mental Model / Analogy

> Network Policies work like a building's access control system using badge types instead of room numbers. Instead of saying "room 204 can enter room 507", you say "anyone with a badge labelled 'payment-team' (podSelector: app=payment) can swipe into the vault (port 5432)". As staff move to new desks (pod IPs change), their badge type (label) stays the same. The access control system uses labels, not desk locations — resilient to office rearrangements. New staff get badges → automatic access to their team's areas.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Kubernetes pods can talk to each other by default (security risk). Network Policies add rules: "only X pod can talk to Y pod on port Z." The CNI plugin (like Calico or Cilium) enforces these rules. Always start with default-deny, then add specific allows.

**Level 2:** Critical rules to remember: (a) Default-deny blocks DNS — always add explicit allow for UDP/TCP port 53 to kube-dns; (b) Policies are additive — multiple policies = OR logic; (c) The CNI must support Network Policies (not all do); (d) Always specify BOTH ingress and egress policies for complete isolation.

**Level 3:** Advanced patterns: (a) Namespace isolation — create production, staging, dev namespaces with deny-all; add label to namespaces (env: prod) and use namespaceSelector; (b) CIDR-based egress for external dependencies (allow egress to AWS RDS CIDR); (c) Calico GlobalNetworkPolicy for cluster-wide rules (applied before namespace-level policies); (d) Cilium L7 policies: restrict to specific HTTP methods and paths, not just ports.

**Level 4:** eBPF vs iptables enforcement (Cilium vs Calico): iptables is evaluated linearly (O(n) rules) — with thousands of pods and network policies, iptables chains can have thousands of rules, adding milliseconds of latency. eBPF loads programs into the kernel that are JIT-compiled and run at near line-rate. Cilium with eBPF adds ~10-30μs per policy lookup vs iptables at ~100-200μs for large rulesets. At 10,000+ pod scale, Cilium's eBPF approach provides significantly better network policy enforcement throughput. Cilium also supports cluster-mesh (multi-cluster), bandwidth management (BPF-based rate limiting), and observability (Hubble: real-time network flow visibility with L7 inspection).

---

### ⚙️ How It Works (Mechanism)

```yaml
# Pattern 1: Default-deny all (namespace isolation)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {} # applies to ALL pods in namespace
  policyTypes:
    - Ingress
    - Egress
---
# Pattern 2: Allow DNS (required for all service communication)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
---
# Pattern 3: Allow payment-service → postgres only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-payment-to-postgres
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: payment-service
      ports:
        - port: 5432
          protocol: TCP
---
# Pattern 4: Allow monitoring namespace to scrape metrics
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-prometheus-scrape
  namespace: production
spec:
  podSelector: {} # all pods
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              purpose: monitoring
      ports:
        - port: 9090
          protocol: TCP
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Network Policy Enforcement — packet-level flow (Cilium/eBPF):

Pod A (app=frontend) tries to connect to Pod B (app=postgres) on 5432

1. kernel intercepts packet leaving Pod A's veth pair
2. eBPF program executes:
   - Lookup: what network policies apply to pod A's identity?
   - Pod A labels: {app: frontend, namespace: production}
   - Egress policy for frontend: only allow → api-service:8080 + DNS
   - postgres:5432 NOT in allow list
3. eBPF program: DROP packet
4. Connection attempt from Pod A fails immediately

Pod B (app=payment-service) tries to connect to Pod C (app=postgres) on 5432

1. kernel intercepts packet leaving payment-service pod
2. eBPF program executes:
   - Egress policy for payment-service: allows postgres:5432
   - Packet allowed to proceed to Pod C
3. Packet arrives at Pod C's veth
4. eBPF program (ingress side):
   - Ingress policy for postgres: allows from payment-service:5432
   - Packet allowed through
5. Connection established
```

---

### 💻 Code Example

```python
# Generate Network Policy YAML programmatically
# Useful for infrastructure-as-code with dynamic service names

from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class AllowRule:
    from_app: str
    to_app: str
    port: int
    namespace: str = "production"
    protocol: str = "TCP"

def generate_network_policy(rule: AllowRule) -> dict:
    """Generate a Kubernetes NetworkPolicy allowing ingress from one app to another."""
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {
            "name": f"allow-{rule.from_app}-to-{rule.to_app}",
            "namespace": rule.namespace,
        },
        "spec": {
            "podSelector": {
                "matchLabels": {"app": rule.to_app}
            },
            "policyTypes": ["Ingress"],
            "ingress": [
                {
                    "from": [
                        {"podSelector": {"matchLabels": {"app": rule.from_app}}}
                    ],
                    "ports": [
                        {"port": rule.port, "protocol": rule.protocol}
                    ]
                }
            ]
        }
    }

# Define service communication graph
service_connections = [
    AllowRule("api-gateway", "user-service", 8080),
    AllowRule("api-gateway", "product-service", 8080),
    AllowRule("order-service", "payment-service", 8443),
    AllowRule("payment-service", "postgres", 5432),
    AllowRule("user-service", "redis", 6379),
]

# Generate all policies
policies = [generate_network_policy(r) for r in service_connections]
# Output to apply: kubectl apply -f policies.yaml
print(yaml.dump_all(policies, default_flow_style=False))
```

---

### ⚖️ Comparison Table

| Feature           | Standard NetworkPolicy | Calico GlobalNetworkPolicy | Cilium L7 Policy       |
| ----------------- | ---------------------- | -------------------------- | ---------------------- |
| Scope             | Namespace              | Cluster-wide               | Namespace              |
| L7 support        | No (L3/L4 only)        | Limited (FQDN egress)      | Yes (HTTP, Kafka, DNS) |
| Enforcement       | CNI (any)              | Calico CNI only            | Cilium CNI only        |
| Performance       | Depends on CNI         | iptables or eBPF           | eBPF (fast)            |
| FQDN egress       | No                     | Yes (\*.amazonaws.com)     | Yes                    |
| Priority/ordering | Not supported          | Yes (order field)          | Not directly           |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                               |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NetworkPolicy works with any CNI                         | NetworkPolicy objects are accepted by K8s API always, but enforced ONLY if CNI supports it. kubenet (default in many setups): NO enforcement. Calico, Cilium, Weave: YES. Always verify with CNI docs |
| Default-deny is the default Kubernetes behaviour         | Opposite: Kubernetes default is allow-all (no isolation). You must explicitly create a default-deny NetworkPolicy                                                                                     |
| NetworkPolicy blocks ALL traffic including health checks | Correctly scoped default-deny blocks kubelet health checks too. Add explicit allow for health check ports, or note that kubelet connects from the node IP (use ipBlock CIDR for node subnet)          |

---

### 🚨 Failure Modes & Diagnosis

**Service Stops Receiving Traffic After Default-Deny Applied**

```bash
# Symptom: service unreachable after applying network policy

# Step 1: check if NetworkPolicy is causing the block
# Temporarily: test connectivity from another pod
kubectl exec -n production deploy/debug-pod -- \
  curl -v http://payment-service:8080/health
# Should return 200; if "connection refused" or timeout: policy issue

# Step 2: list NetworkPolicies affecting the service
kubectl get networkpolicies -n production
kubectl describe networkpolicy allow-payment -n production

# Step 3: check if DNS is blocked (common mistake)
kubectl exec -n production deploy/payment-service -- \
  nslookup postgres.production.svc.cluster.local
# If NXDOMAIN or timeout: DNS egress not allowed in policy
# Fix: add allow-dns NetworkPolicy

# Step 4: Cilium-specific: use Hubble for flow inspection
# hubble observe --namespace production --verdict DROPPED
# Shows exactly which flows are being dropped and by which policy

# Step 5: Calico: use calicoctl to inspect policy status
calicoctl get networkpolicy -n production
calicoctl get globalnetworkpolicy

# Step 6: verify CNI supports NetworkPolicy
kubectl get pods -n kube-system | grep -E "calico|cilium|weave|antrea"
# If none: NetworkPolicy has NO effect
```

---

### 🔗 Related Keywords

**Prerequisites:** `Firewall`, `Kubernetes`, `Zero Trust Networking`

**Related:** `Zero Trust Networking`, `mTLS`, `Service Discovery`, `Overlay Networks`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFAULT K8s  │ All pods can reach all pods (no isolation)│
│ WITH POLICY  │ Whitelist: deny-all + explicit allows      │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS ADD   │ Allow DNS (UDP/TCP 53) or nothing works   │
│ POLICY LOGIC │ Additive: multiple policies = OR          │
├──────────────┼───────────────────────────────────────────┤
│ CNI REQUIRED │ Calico, Cilium, Weave — NOT kubenet        │
│ L7 POLICIES  │ Cilium only (HTTP path/method filtering)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pod-level firewall using label selectors │
│              │ instead of IP addresses"                  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're implementing a Zero Trust network posture for a Kubernetes cluster running a 30-service microservices system with strict PCI-DSS compliance requirements. (a) Design the namespace architecture: how do you isolate payment services (PCI-DSS CDE — Cardholder Data Environment) from non-payment services? (b) Write the network policy set for the CDE namespace: default-deny-all, allow payment-service egress to postgres on 5432, allow payment-service egress to stripe-gateway-service on 443 (external), allow payment-service ingress from order-service on 8443 only. Include the DNS allow rule and explain why it's needed. (c) Explain the gap between Kubernetes NetworkPolicy (L3/L4 only) and true Zero Trust (mTLS + RBAC for East-West): if two pods both have app=payment label, NetworkPolicy allows them to communicate — but mTLS (via Istio AuthorizationPolicy) verifies the SPIFFE identity of the calling workload. How do these two layers complement each other? (d) How does Cilium's L7 NetworkPolicy close the remaining gap: instead of just allowing payment-service → postgres on port 5432 (all SQL), allow ONLY specific SQL verbs (INSERT/SELECT on specific tables)?
