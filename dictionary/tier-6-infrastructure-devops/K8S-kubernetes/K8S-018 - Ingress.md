---
layout: default
title: "Ingress"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /kubernetes/ingress/
id: K8S-018
category: "Kubernetes"
difficulty: "★★☆"
depends_on:
  ["Service (K8s)", "ClusterIP / NodePort / LoadBalancer", "Namespace (K8s)"]
used_by: ["Ingress Controller", "API Gateway (AWS)", "mTLS"]
related:
  [
    "Ingress Controller",
    "Service (K8s)",
    "ClusterIP / NodePort / LoadBalancer",
    "Network Policy",
    "mTLS",
  ]
tags: [kubernetes, ingress, http-routing, tls-termination, k8s, nginx]
---

# Ingress

## ⚡ TL;DR

An **Ingress** is a Kubernetes API object that defines L7 (HTTP/HTTPS) routing rules: route `api.example.com/users` → users-service, `api.example.com/orders` → orders-service. An **Ingress Controller** (nginx, Traefik, etc.) reads these rules and implements them.

---

## 🔥 Problem This Solves

You have 10 microservices. Without Ingress, you'd need 10 LoadBalancer Services (10 cloud LBs, 10 external IPs, high cost). Ingress provides one entry point with host/path-based routing to all services behind a single LB.

---

## 📘 Textbook Definition

An Ingress manages external access to Services in a cluster, typically HTTP/HTTPS. Ingress can provide load balancing, SSL/TLS termination, and name-based virtual hosting. Ingress rules are read by an Ingress Controller that implements the actual routing.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: tls-secret # TLS cert in Secret
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /users
            pathType: Prefix
            backend:
              service:
                name: users-service
                port:
                  number: 80
          - path: /orders
            pathType: Prefix
            backend:
              service:
                name: orders-service
                port:
                  number: 80
```

---

## 🔩 First Principles

- **Ingress** = routing rules (Kubernetes object)
- **Ingress Controller** = the process that reads rules and configures the actual proxy (nginx, Traefik, HAProxy, etc.)
- Ingress is L7 (HTTP/HTTPS); for TCP/UDP use a LoadBalancer Service directly
- TLS termination at the Ingress Controller; traffic to Services can be plain HTTP internally
- `ingressClassName` selects which controller handles the Ingress

---

## 🧪 Thought Experiment

You have a React frontend at `app.example.com` and a Spring Boot API at `api.example.com`. Without Ingress: 2 LoadBalancers, 2 external IPs, TLS certs configured in two places. With Ingress: 1 LoadBalancer → Ingress Controller → routes by host to two ClusterIP Services. One TLS cert, one entry point.

---

## 🧠 Mental Model / Analogy

Ingress is like a **hotel concierge**: one entrance (LoadBalancer), but the concierge (Ingress Controller) reads your destination (URL path/host) and directs you to the right floor/room (Service). The hotel has one address, many rooms.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Ingress lets you route HTTP traffic to different services by URL path or hostname.

**Level 2 - Practitioner**: Requires an Ingress Controller to be installed (nginx-ingress-controller is most common). Define rules in Ingress objects. TLS certs stored in Secrets.

**Level 3 - Advanced**: `pathType: Exact` vs `Prefix` vs `ImplementationSpecific`. Annotations configure controller-specific behavior (rate limiting, auth, rewrites). cert-manager automates TLS cert issuance via Let's Encrypt.

**Level 4 - Expert**: `IngressClass` resource (K8s 1.18+) replaces annotation-based class selection. Multiple Ingress controllers can coexist (nginx for HTTP, AWS ALB for WebSockets). Gateway API (next-gen) replaces Ingress with HTTPRoute, GRPCRoute, TCPRoute resources.

---

## ⚙️ How It Works

### Ingress Architecture

```
Internet → LoadBalancer Service (1 cloud LB)
  → Ingress Controller Pod (nginx/traefik)
     Reads Ingress objects → configures proxy rules
  → Routes by host/path:
      api.example.com/users  → users-service:80
      api.example.com/orders → orders-service:80
      app.example.com        → frontend-service:80
  → Each service → ClusterIP → Pods
```

### TLS with cert-manager

```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls # cert-manager auto-creates this Secret
```

### pathType Values

| Value                    | Behavior                              |
| ------------------------ | ------------------------------------- |
| `Exact`                  | Exact path match (`/users` only)      |
| `Prefix`                 | Prefix match (`/users`, `/users/123`) |
| `ImplementationSpecific` | Controller-defined (nginx regex)      |

---

## 🔄 E2E Flow: HTTPS Request

```
Browser → HTTPS api.example.com/users
  → DNS → Cloud LB external IP
  → LB → nginx Ingress Controller Pod (port 443)
  → TLS termination (using cert from Secret)
  → Route match: host=api.example.com, path=/users
  → Forward plain HTTP to users-service:80 (ClusterIP)
  → users-service → users Pod 10.244.x.x:8080
  → Response → nginx → browser (encrypted)
```

---

## ⚖️ Comparison Table

|                  | Ingress               | LoadBalancer Service  | API Gateway                     |
| ---------------- | --------------------- | --------------------- | ------------------------------- |
| **Protocol**     | HTTP/HTTPS (L7)       | Any TCP/UDP (L4)      | HTTP/HTTPS + features           |
| **Routing**      | Host + path           | IP:port only          | Host + path + auth + rate limit |
| **TLS**          | At Ingress Controller | Passthrough or at Pod | At Gateway                      |
| **Cost**         | 1 LB for all services | 1 LB per service      | Managed service cost            |
| **Cloud native** | Kubernetes native     | Kubernetes native     | AWS API GW, Azure APIM          |

---

## ⚠️ Common Misconceptions

| Misconception                     | Reality                                                           |
| --------------------------------- | ----------------------------------------------------------------- |
| "Ingress works out of the box"    | Requires an Ingress Controller to be installed separately         |
| "Ingress = L4 load balancer"      | Ingress is L7 (HTTP/HTTPS); L4 needs LoadBalancer Service type    |
| "One Ingress per service"         | One Ingress can have many rules routing to many services          |
| "TLS in Ingress = end-to-end TLS" | Default: TLS terminates at Ingress; traffic to pods is plain HTTP |

---

## 🚨 Failure Modes

| Failure                | Symptom                       | Fix                                              |
| ---------------------- | ----------------------------- | ------------------------------------------------ |
| No Ingress Controller  | Ingress created but ignored   | Install nginx-ingress or Traefik                 |
| Wrong ingressClassName | Ingress ignored by controller | Match `ingressClassName` to installed controller |
| TLS cert expired       | Browser SSL error             | Use cert-manager for auto-renewal                |
| Path not matching      | 404 from Ingress              | Check `pathType` and leading slashes             |

---

## 🔗 Related Keywords

- [Ingress Controller](/kubernetes/ingress-controller/) - implements Ingress rules
- [Service (K8s)](/kubernetes/service-k8s/) - backend for Ingress rules
- [ClusterIP / NodePort / LoadBalancer](/kubernetes/clusterip-nodeport-loadbalancer/) - Service types
- [mTLS](/kubernetes/mtls/) - mutual TLS between services
- [Network Policy](/kubernetes/network-policy/) - restrict Ingress traffic

---

## 📌 Quick Reference Card

```bash
# Get Ingresses
kubectl get ingress
kubectl describe ingress api-ingress

# Create TLS secret
kubectl create secret tls tls-secret \
  --cert=tls.crt --key=tls.key

# Check Ingress Controller pods
kubectl get pods -n ingress-nginx

# Test from inside cluster
kubectl run test --rm -it --image=curlimages/curl -- \
  curl -H "Host: api.example.com" http://<ingress-controller-ClusterIP>/users

# Port-forward ingress controller for local testing
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
```

---

## 🧠 Think About This

Kubernetes Gateway API (replacing Ingress) splits routing into three objects: GatewayClass (infrastructure provider), Gateway (attachment point), and HTTPRoute (routing rules). This separation allows platform teams to manage Gateways while app teams manage Routes - a much cleaner RBAC boundary than a single Ingress object with mixed concerns. If you're starting fresh, consider Gateway API over classic Ingress.
