---
layout: default
title: "Ingress Controller"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /kubernetes/ingress-controller/
id: K8S-019
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Ingress", "Service (K8s)", "Deployment", "DaemonSet"]
used_by: ["mTLS", "API Gateway (Microservices)", "Kubernetes Observability"]
related:
  [
    "Ingress",
    "Service (K8s)",
    "mTLS",
    "Envoy Proxy",
    "Service Mesh (Microservices)",
  ]
tags: [kubernetes, ingress-controller, nginx, traefik, cert-manager, k8s]
---

# Ingress Controller

## ⚡ TL;DR

An Ingress Controller is the **implementation** of Ingress rules — it's a Pod (typically nginx or Traefik) that watches Ingress objects and configures a reverse proxy accordingly. Without an Ingress Controller, Ingress objects do nothing.

---

## 🔥 Problem This Solves

Kubernetes Ingress objects define routing rules, but Kubernetes itself doesn't implement them. An Ingress Controller watches those rules and configures an actual proxy (nginx, Traefik, HAProxy, Istio, AWS ALB) to route traffic.

---

## 📘 Textbook Definition

An Ingress Controller is a specialized load balancer for Kubernetes that implements the Ingress specification. It runs as a Pod in the cluster, watches Ingress resources via the Kubernetes API, and configures itself to route HTTP/HTTPS traffic according to the defined rules.

---

## ⏱️ 30 Seconds

```bash
# Install nginx Ingress Controller via Helm
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# Verify
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
# NAME                       TYPE           EXTERNAL-IP
# ingress-nginx-controller   LoadBalancer   34.105.x.x
```

Then create Ingress objects with `ingressClassName: nginx` — the controller auto-configures itself.

---

## 🔩 First Principles

- Ingress Controller = **watcher + configurator + proxy**
- Watches Ingress objects via K8s API (informer/watch)
- Translates Ingress rules into proxy configuration (nginx.conf, Traefik dynamic config)
- Proxy handles actual traffic (TLS termination, routing, load balancing)
- Hot-reload: config updates apply without proxy restart (nginx with signal, Traefik natively)

---

## 🧪 Thought Experiment

You create an Ingress rule for `api.example.com`. The Ingress Controller's watch fires. It regenerates nginx.conf with a new `server` block and signals nginx to reload (gracefully). New HTTP requests route to the backend Service. Existing connections aren't dropped. Zero-downtime config update.

---

## 🧠 Mental Model / Analogy

Ingress Controller is like a **smart router firmware** that reads routing table definitions (Ingress objects) from a configuration server (K8s API) and updates routing rules in real time. The firmware is nginx or Traefik; the routing table is Ingress objects.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Install nginx-ingress, create Ingress rules. The controller does the routing.

**Level 2 — Practitioner**: Controllers run as Deployments (or DaemonSets). Each controller has its own LoadBalancer Service for external traffic. Annotations customize behavior (rate limits, auth, rewrites) per controller.

**Level 3 — Advanced**: Multiple Ingress Controllers in one cluster using `IngressClass`. `ingressClassName: nginx` goes to nginx controller; `ingressClassName: alb` goes to AWS ALB controller. Each can have different features.

**Level 4 — Expert**: Admission webhooks validate Ingress objects before admission (catch config errors early). NGINX controller uses `lua-resty-balancer` for upstream selection. Canary deployments via annotations (`nginx.ingress.kubernetes.io/canary: "true"`). PROXY Protocol preserves client IP through LB.

---

## ⚙️ How It Works

### Popular Ingress Controllers

| Controller                | Best For                                | Notes                       |
| ------------------------- | --------------------------------------- | --------------------------- |
| **nginx-ingress**         | General purpose, stable                 | Most widely used            |
| **Traefik**               | Dynamic routing, Let's Encrypt built-in | Excellent for dev           |
| **HAProxy Ingress**       | High performance, TCP                   | Financial/low-latency       |
| **AWS ALB Controller**    | AWS native, WAF integration             | EC2/EKS                     |
| **Istio Ingress Gateway** | Service mesh integration                | Advanced traffic management |
| **Envoy (Contour)**       | Envoy-native, HTTP/2                    | High-performance L7         |

### nginx Ingress Architecture

```
LoadBalancer Service (external IP)
  ↓
nginx-ingress-controller Pod
  ├─ nginx worker processes (handle traffic)
  ├─ lua-nginx-module (dynamic upstream selection)
  └─ Kubernetes API Watcher
       Watches Ingress objects → regenerates nginx.conf
       nginx -s reload (graceful config reload)
```

### IngressClass Resource

```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx
spec:
  controller: k8s.io/ingress-nginx
---
# In Ingress:
spec:
  ingressClassName: nginx
```

### Useful nginx Annotations

```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /
  nginx.ingress.kubernetes.io/proxy-body-size: "50m"
  nginx.ingress.kubernetes.io/rate-limit: "100"
  nginx.ingress.kubernetes.io/auth-url: "http://auth-svc/validate"
  nginx.ingress.kubernetes.io/canary: "true"
  nginx.ingress.kubernetes.io/canary-weight: "20"
```

---

## 🔄 E2E Flow: Ingress Rule Update

```
kubectl apply -f new-ingress.yaml
  → API Server persists Ingress object
  → nginx-ingress-controller watcher fires
  → Controller: regenerates nginx.conf
      - New server block for new rule
      - Updated upstream for existing rule
  → nginx graceful reload (kill -HUP)
  → New traffic routed per new rules
  → Old connections complete normally
```

---

## ⚖️ Comparison Table

|                   | nginx Ingress           | Traefik                  | AWS ALB Controller   |
| ----------------- | ----------------------- | ------------------------ | -------------------- |
| **TLS cert mgmt** | External (cert-manager) | Built-in ACME            | ACM (AWS)            |
| **Config style**  | nginx annotations       | Traefik IngressRoute CRD | ALB annotations      |
| **WebSocket**     | Supported               | Supported                | Supported            |
| **gRPC**          | Supported               | Supported                | Supported            |
| **Canary**        | Annotation-based        | Weighted TraefikService  | Target group weights |
| **Cloud lock-in** | None                    | None                     | AWS only             |

---

## ⚠️ Common Misconceptions

| Misconception                               | Reality                                                             |
| ------------------------------------------- | ------------------------------------------------------------------- |
| "Kubernetes provides an Ingress Controller" | Kubernetes defines the API; you must install a controller           |
| "All controllers support same annotations"  | Annotations are controller-specific; nginx ≠ Traefik ≠ ALB          |
| "One Ingress Controller per cluster"        | Multiple IngressClasses → multiple controllers can coexist          |
| "Ingress Controller handles TCP/UDP"        | Default Ingress is HTTP only; nginx has TCP/UDP ConfigMap extension |

---

## 🚨 Failure Modes

| Failure                       | Symptom                               | Fix                                                 |
| ----------------------------- | ------------------------------------- | --------------------------------------------------- |
| Controller not installed      | Ingress ignored; no LB IP             | Install nginx-ingress or Traefik                    |
| Controller OOM                | Requests 502/504                      | Increase controller memory limits                   |
| nginx config error            | Controller logs show error; 500       | Validate Ingress annotations; check controller logs |
| Multiple controllers conflict | Ingress picked up by wrong controller | Use `ingressClassName` to target correctly          |

---

## 🔗 Related Keywords

- [Ingress](/kubernetes/ingress/) — routing rules read by controller
- [Service (K8s)](/kubernetes/service-k8s/) — backend for routing
- [mTLS](/kubernetes/mtls/) — mutual TLS at Ingress layer
- [Envoy Proxy](/kubernetes/envoy-proxy/) — Envoy-based controllers
- [Service Mesh on K8s](/kubernetes/service-mesh-on-k8s/) — alternative to Ingress for advanced traffic

---

## 📌 Quick Reference Card

```bash
# Install nginx-ingress (Helm)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx

# Check controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Get IngressClasses
kubectl get ingressclass

# Debug Ingress not routing
kubectl describe ingress my-ingress
# Look for: "reason: no endpoints for backend"

# Test canary routing (nginx)
for i in $(seq 1 10); do
  curl -s http://api.example.com/test | grep version
done
```

---

## 🧠 Think About This

Why is there no default Ingress Controller in Kubernetes? Because the right choice depends on your infrastructure: nginx for on-prem, ALB for AWS, Istio for service mesh environments. Kubernetes intentionally left this as a pluggable extension point via the IngressClass API. This is the same design philosophy as CNI (network), CSI (storage), and CRI (container runtime) — Kubernetes defines the interface; the ecosystem provides implementations.
