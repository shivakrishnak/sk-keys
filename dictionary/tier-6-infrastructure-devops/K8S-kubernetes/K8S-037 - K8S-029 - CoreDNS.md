---
version: 1
layout: default
title: "CoreDNS"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 37
permalink: /kubernetes/coredns/
id: K8S-037
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Service (K8s)", "Namespace (K8s)", "Cluster"]
used_by: ["Service (K8s)", "StatefulSet", "Ingress"]
related: ["Service (K8s)", "kube-proxy", "Namespace (K8s)", "Network Policy"]
tags: [kubernetes, coredns, dns, service-discovery, k8s, networking]
---

# CoreDNS

## ⚡ TL;DR

CoreDNS is the **cluster DNS server** - it resolves `my-service.my-namespace.svc.cluster.local` to the Service's ClusterIP. It runs as a Deployment in `kube-system` and is the reason you can call services by name instead of IP.

---

## 🔥 Problem This Solves

Pods communicate with Services by ClusterIP, but IPs are ephemeral and hard to manage. CoreDNS gives every Service a DNS name so services can find each other by name: `http://orders-service/api` instead of `http://10.96.x.x:8080`.

---

## 📘 Textbook Definition

CoreDNS is the DNS server for Kubernetes clusters. It implements the Kubernetes DNS spec, resolving Service names to ClusterIPs and providing DNS-based service discovery. It replaced kube-dns as the default DNS provider starting in Kubernetes 1.13.

---

## ⏱️ 30 Seconds

```
# From inside any Pod:
curl http://users-service/api/users
  → DNS lookup: users-service.default.svc.cluster.local
  → CoreDNS: returns ClusterIP 10.96.50.100
  → kube-proxy: routes to actual Pod

# Short names work within same namespace:
users-service
users-service.default         # cross-namespace short form
users-service.default.svc.cluster.local  # FQDN

# StatefulSet Pod DNS (headless service):
postgres-0.postgres.default.svc.cluster.local
```

---

## 🔩 First Principles

- Each Pod gets `/etc/resolv.conf` pointing to CoreDNS ClusterIP (e.g., `10.96.0.10`)
- `ndots:5` in resolv.conf → short names add suffix search list before treating as absolute
- CoreDNS watches Services and Endpoints; serves A/AAAA records for ClusterIPs
- Headless Services: CoreDNS returns multiple A records (one per Pod)
- External DNS: CoreDNS forwards non-cluster queries to upstream resolvers

---

## 🧪 Thought Experiment

A Pod queries `orders-service`. CoreDNS applies the search domain `default.svc.cluster.local` and resolves `orders-service.default.svc.cluster.local` → ClusterIP. If the query was `api.external.com`, CoreDNS has no record → forwards to configured upstream (Google 8.8.8.8, VPC DNS, etc.). The same DNS server handles both cluster-internal and external resolution.

---

## 🧠 Mental Model / Analogy

CoreDNS is the cluster's **phone book**: "What's the phone number (IP) for 'orders-service'?" It knows every Service's address and can forward questions about external addresses (google.com) to the internet phone book.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: CoreDNS lets services find each other by name. `http://my-service` just works inside a cluster.

**Level 2 - Practitioner**: DNS search list: `default.svc.cluster.local`, `svc.cluster.local`, `cluster.local`. Short names append these suffixes. Always use FQDNs for cross-namespace calls to avoid extra DNS round trips.

**Level 3 - Advanced**: CoreDNS is configured via `Corefile` (ConfigMap in kube-system). Plugins: `kubernetes` (cluster DNS), `forward` (upstream), `cache` (TTL), `log`, `health`, `ready`. `ndots:5` causes 5+ dots to be treated as absolute; fewer = multiple suffix attempts.

**Level 4 - Expert**: CoreDNS scales with cluster size; run 2+ replicas behind a Service. Memory usage grows with cluster size (caches all Service/Endpoint records). Negative caching: `noerror` TTL for NXDOMAIN prevents repeated lookups. External DNS operator syncs Kubernetes Service/Ingress hostnames to Route53, Azure DNS, etc.

---

## ⚙️ How It Works

### DNS Name Structure

```
<service>.<namespace>.svc.<cluster-domain>
  └─ cluster-domain = cluster.local (default)

Examples:
  users-service.default.svc.cluster.local
  postgres-0.postgres.production.svc.cluster.local  (StatefulSet)

Headless service (returns all Pod IPs):
  postgres.default.svc.cluster.local → [10.244.1.5, 10.244.2.5, 10.244.3.5]
```

### Pod /etc/resolv.conf

```
nameserver 10.96.0.10        # CoreDNS ClusterIP
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

### Corefile ConfigMap

```
# kubectl get configmap coredns -n kube-system -o yaml
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
           ttl 30
        }
        prometheus :9153
        forward . /etc/resolv.conf    # forward to VPC DNS
        cache 30
        loop
        reload
        loadbalance
    }
```

### DNS Resolution Order (with ndots:5)

```
Query: "orders-service"  (2 dots = 0, less than 5)
  → Try: orders-service.default.svc.cluster.local ✅ (match!)
  → Return ClusterIP

Query: "orders-service.default"  (1 dot, less than 5)
  → Try: orders-service.default.default.svc.cluster.local ❌
  → Try: orders-service.default.svc.cluster.local ✅ (match!)

Query: "api.example.com."  (4 dots, but ends with dot = absolute)
  → Directly: api.example.com → forward to upstream
```

---

## 🔄 E2E Flow: Service DNS Lookup

```
Pod in namespace "orders" wants to call "payments-service" in "payments"

1. getaddrinfo("payments-service")
2. /etc/resolv.conf: ndots=5, search: orders.svc.cluster.local ...
3. Try: payments-service.orders.svc.cluster.local → NXDOMAIN (wrong NS)
4. Try: payments-service.svc.cluster.local → NXDOMAIN
5. Try: payments-service.cluster.local → NXDOMAIN
6. Absolute: payments-service → NXDOMAIN

Fix: use FQDN:  payments-service.payments.svc.cluster.local
Or short form:  payments-service.payments
```

---

## ⚖️ Comparison Table

|                 | Short name          | Namespace-qualified | FQDN                       |
| --------------- | ------------------- | ------------------- | -------------------------- |
| **DNS lookups** | Up to 5 attempts    | 2 attempts          | 1 attempt                  |
| **Portability** | Same namespace only | Cross-namespace     | Anywhere                   |
| **Performance** | Worst               | Better              | Best                       |
| **Example**     | `svc`               | `svc.ns`            | `svc.ns.svc.cluster.local` |

---

## ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                         |
| -------------------------------------- | ------------------------------------------------------------------------------- |
| "Short names always resolve"           | Short names only resolve in same namespace; use FQDN cross-namespace            |
| "DNS is instant"                       | `ndots:5` causes multiple DNS queries for short names; use FQDN for performance |
| "CoreDNS handles network policy"       | CoreDNS resolves names; CNI enforces policy                                     |
| "CoreDNS is a single point of failure" | CoreDNS runs as a Deployment with 2+ replicas                                   |

---

## 🚨 Failure Modes

| Failure             | Symptom                            | Fix                                                      |
| ------------------- | ---------------------------------- | -------------------------------------------------------- |
| CoreDNS OOM         | DNS timeouts; Pods fail to resolve | Increase CoreDNS memory limits; check cache size         |
| Wrong search domain | Cross-namespace calls fail         | Use FQDN: `svc.ns.svc.cluster.local`                     |
| ndots=5 latency     | High DNS query latency             | Use FQDNs with trailing dot; tune ndots in Pod dnsConfig |
| CoreDNS ConfigError | `NXDOMAIN` for cluster services    | Check Corefile ConfigMap for errors                      |

---

## 🔗 Related Keywords

- [Service (K8s)](/kubernetes/service-k8s/) - CoreDNS resolves Service names
- [kube-proxy](/kubernetes/kube-proxy/) - routes after DNS resolution
- [Namespace (K8s)](/kubernetes/namespace-k8s/) - namespaces in DNS names
- [StatefulSet](/kubernetes/statefulset/) - per-Pod DNS via headless service

---

## 📌 Quick Reference Card

```bash
# Check CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS config
kubectl get configmap coredns -n kube-system -o yaml

# Test DNS from a Pod
kubectl run dns-test --rm -it --image=busybox -- \
  nslookup kubernetes.default.svc.cluster.local

# Check DNS resolution from Pod
kubectl exec -it my-pod -- cat /etc/resolv.conf
kubectl exec -it my-pod -- nslookup my-service

# Debug DNS issues
kubectl run dnsutils --rm -it \
  --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.3 \
  -- bash
# Inside: dig my-service.default.svc.cluster.local
```

---

## 🧠 Think About This

`ndots:5` causes short DNS names to go through up to 5 suffix attempts before failing. In a busy microservices system with 1000 RPS and each request triggering 3-5 DNS lookups, those extra failed lookups add up. For cross-namespace service calls, always use the fully-qualified name (`service.namespace.svc.cluster.local`) to get it right in the first try. For same-namespace calls, short names are fine (first attempt succeeds).
