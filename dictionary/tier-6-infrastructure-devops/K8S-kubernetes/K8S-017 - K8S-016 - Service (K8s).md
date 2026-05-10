---
version: 1
layout: default
title: "Service (K8s)"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /kubernetes/service-k8s/
id: K8S-017
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "Deployment", "Namespace (K8s)"]
used_by: ["Ingress", "ClusterIP / NodePort / LoadBalancer", "StatefulSet"]
related:
  [
    "ClusterIP / NodePort / LoadBalancer",
    "Ingress",
    "kube-proxy",
    "CoreDNS",
    "Network Policy",
  ]
tags: [kubernetes, service, clusterip, nodeport, loadbalancer, dns, k8s]
---

# Service (K8s)

## ⚡ TL;DR

A Kubernetes Service provides a **stable virtual IP and DNS name** for a set of Pods, enabling load balancing and discovery. Pods come and go; the Service IP stays constant. Types: ClusterIP (internal), NodePort (node-level), LoadBalancer (cloud LB), ExternalName.

---

## 🔥 Problem This Solves

Pod IPs change every time a Pod is replaced. Hardcoding Pod IPs breaks when Pods restart. A Service gives a stable DNS name and IP that routes to healthy Pods regardless of their individual IPs.

---

## 📘 Textbook Definition

A Service is an abstraction that defines a logical set of Pods and a policy for accessing them. The set of Pods is determined by a label selector. Services provide stable networking (virtual IP + DNS) and load balancing.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: default
spec:
  selector:
    app: my-app # routes to Pods with this label
  ports:
    - protocol: TCP
      port: 80 # Service port (virtual)
      targetPort: 8080 # Pod port
  type: ClusterIP # internal-only
```

DNS: `my-app.default.svc.cluster.local` → ClusterIP → kube-proxy → Pod

---

## 🔩 First Principles

- A Service = **virtual IP** (ClusterIP) + **Endpoint** objects (list of healthy Pod IPs)
- kube-proxy programs iptables/IPVS rules on every node: ClusterIP → random Pod IP
- CoreDNS resolves Service name to ClusterIP
- **Endpoints** are automatically updated as Pods become Ready/NotReady
- Label selector defines which Pods are included

---

## 🧪 Thought Experiment

Three instances of `my-app` are running. One fails its readiness probe. The Service has three endpoints, but the failing Pod is automatically removed from endpoints - traffic only goes to healthy Pods. When it recovers and passes readiness, it's re-added. No configuration change needed.

---

## 🧠 Mental Model / Analogy

A Service is like a **load balancer DNS entry in a corporate directory**: instead of knowing each employee's desk phone (Pod IP), you call the department's main number (Service ClusterIP). The receptionist (kube-proxy) routes to whoever is available.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: A Service gives your app a stable address (DNS name) that doesn't change when Pods restart.

**Level 2 - Practitioner**: Three types: ClusterIP (internal), NodePort (external via node), LoadBalancer (cloud LB). `selector` determines which Pods receive traffic. Endpoints updated automatically.

**Level 3 - Advanced**: Headless Service (`clusterIP: None`) returns all Pod IPs via DNS A records (no proxying). Used by StatefulSets. `sessionAffinity: ClientIP` enables sticky sessions. `externalTrafficPolicy: Local` preserves client IPs at cost of uneven distribution.

**Level 4 - Expert**: kube-proxy IPVS mode provides O(1) routing vs O(n) iptables. `EndpointSlices` (replaces Endpoints) shard large endpoint lists for scale. Topology-aware routing (`trafficDistribution: PreferClose`) routes to same zone first. Services without selectors + manual Endpoints enable routing to external services.

---

## ⚙️ How It Works

### Service Types

| Type              | Accessibility         | Use case                        |
| ----------------- | --------------------- | ------------------------------- |
| `ClusterIP`       | Within cluster only   | Default; inter-service comms    |
| `NodePort`        | Node IP + static port | Dev/testing, simple exposure    |
| `LoadBalancer`    | External via cloud LB | Production external traffic     |
| `ExternalName`    | CNAME to external DNS | Route to external service       |
| Headless (`None`) | Per-Pod DNS records   | StatefulSets, direct Pod access |

### kube-proxy (iptables mode)

```
Request to ClusterIP:80
  → iptables DNAT rule (matches ClusterIP:80)
  → Randomly select from Endpoints list
  → DNAT to PodIP:8080
  → Response back to caller
```

### DNS Resolution (CoreDNS)

```
my-app                             → ClusterIP (same namespace)
my-app.default                     → ClusterIP
my-app.default.svc                 → ClusterIP
my-app.default.svc.cluster.local   → ClusterIP (FQDN)
```

---

## 🔄 E2E Flow: Service Request

```
Client Pod → DNS lookup "my-app"
  → CoreDNS: returns ClusterIP 10.100.0.50
  → Client connects to 10.100.0.50:80
  → kube-proxy iptables on client's node:
      DNAT 10.100.0.50:80 → 10.244.2.15:8080 (Pod)
  → TCP connection to actual Pod
  → Response returns to client
```

---

## ⚖️ Comparison Table

|              | ClusterIP     | NodePort         | LoadBalancer          |
| ------------ | ------------- | ---------------- | --------------------- |
| **Access**   | Internal only | Node:30000-32767 | External IP via cloud |
| **Cost**     | Free          | Free             | Cloud LB cost         |
| **Use case** | Inter-service | Dev/testing      | Production HTTP/TCP   |
| **DNS**      | Yes           | Yes              | Yes                   |

---

## ⚠️ Common Misconceptions

| Misconception                        | Reality                                                          |
| ------------------------------------ | ---------------------------------------------------------------- |
| "Service selects Pods by name"       | Services use **label selectors**, not Pod names                  |
| "Service routes to all Pods equally" | Routes to Ready Pods only; failed readiness probes excluded      |
| "LoadBalancer works anywhere"        | `LoadBalancer` type requires a cloud provider or MetalLB         |
| "Headless = no load balancing"       | Headless returns all Pod IPs; client does its own load balancing |

---

## 🚨 Failure Modes

| Failure                    | Symptom                             | Fix                                              |
| -------------------------- | ----------------------------------- | ------------------------------------------------ |
| Wrong label selector       | No endpoints, 503                   | Match selector to Pod labels exactly             |
| All Pods fail readiness    | Empty Endpoints, connection refused | Fix app health; check readiness probe            |
| NodePort out of range      | Service creation fails              | NodePort must be 30000-32767                     |
| Session affinity + scaling | Uneven distribution                 | Use with caution; defeats load balancing purpose |

---

## 🔗 Related Keywords

- [ClusterIP / NodePort / LoadBalancer](/kubernetes/clusterip-nodeport-loadbalancer/) - Service type details
- [Ingress](/kubernetes/ingress/) - HTTP routing on top of Services
- [kube-proxy](/kubernetes/kube-proxy/) - implements Service routing
- [CoreDNS](/kubernetes/coredns/) - DNS resolution for Services
- [Network Policy](/kubernetes/network-policy/) - restrict traffic to Services

---

## 📌 Quick Reference Card

```bash
# Create Service
kubectl expose deployment my-app --port=80 --target-port=8080

# Get Services
kubectl get services
kubectl get svc my-app -o yaml

# Endpoints (healthy Pods)
kubectl get endpoints my-app

# Test from inside cluster
kubectl run test --image=busybox --rm -it -- wget -O- my-app

# Port-forward for local testing
kubectl port-forward svc/my-app 8080:80

# Service DNS pattern
# <service>.<namespace>.svc.cluster.local
```

---

## 🧠 Think About This

Why does Kubernetes use a virtual IP (ClusterIP) instead of just using DNS round-robin to Pod IPs? DNS clients cache responses, so stale IPs from dead Pods would cause failures. The ClusterIP is always valid - kube-proxy dynamically routes to healthy Pods. DNS points to one stable ClusterIP; load balancing happens at the network layer, not the DNS layer.
