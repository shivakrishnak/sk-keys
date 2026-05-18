---
version: 1
layout: default
title: "API Server"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/kubernetes/api-server/
id: K8S-039
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Kubernetes Architecture", "etcd", "RBAC (K8s)"]
used_by: ["kubectl", "Admission Controllers", "RBAC (K8s)", "Operators"]
related:
  [
    "etcd",
    "RBAC (K8s)",
    "Admission Controllers",
    "Kubernetes Architecture",
    "Service Account",
  ]
tags: [kubernetes, api-server, kube-apiserver, rbac, admission-webhook, k8s]
---

## ⚡ TL;DR

The API Server (`kube-apiserver`) is the **single front door to the Kubernetes control plane**. Every operation goes through it: authentication → authorization → admission control → persist to etcd → notify watchers. It's stateless - all state lives in etcd.

---

## 🔥 Problem This Solves

Kubernetes needs a centralized, secure entry point that enforces authentication, authorization, validation, and mutation for all cluster state changes. The API Server provides this with a RESTful + watch API backed by etcd.

---

## 📘 Textbook Definition

The Kubernetes API Server is the central management entity and the only component that directly communicates with etcd. It exposes the Kubernetes API, processes REST operations, validates and configures data for API objects, and serves as the frontend for the cluster's shared state.

---

## ⏱️ 30 Seconds

```
Request pipeline for every kubectl apply:
  1. Authentication  → who is this? (cert, token, OIDC)
  2. Authorization   → can they do this? (RBAC, ABAC)
  3. Admission       → should we allow/mutate this?
     a. Mutating admission webhooks (modify object)
     b. Validating admission webhooks (accept/reject)
  4. Persist         → write to etcd
  5. Watch events    → notify controllers, schedulers

Port: 6443 (HTTPS, authenticated)
      8080 (HTTP, insecure, local only - deprecated)
```

---

## 🔩 First Principles

- API Server is **stateless** - scale horizontally; all state is in etcd
- API Server is the **only** component that reads/writes etcd
- All components (kubelet, controller-manager, scheduler, kubectl) talk to API Server
- Watch mechanism: clients register watches and get push notifications (not polling)
- Every resource is versioned (`v1`, `apps/v1`, `networking.k8s.io/v1`)

---

## 🧪 Thought Experiment

What happens when the API Server is down? kubectl commands fail. No new Pods can be scheduled. But existing Pods keep running! kubelet caches the last known PodSpec and continues managing containers. This is by design - the data plane (running workloads) is decoupled from the control plane (API Server). Recovery = API Server restart + reconnection of all watchers.

---

## 🧠 Mental Model / Analogy

The API Server is like a **government registry office**: every birth (create), death (delete), and change (update) of any citizen (resource) must be registered here. The registry enforces who can make which changes (RBAC), validates the paperwork (admission), and records it officially (etcd). All other government departments (controllers) watch the registry for changes.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: API Server is the main entry point to Kubernetes. kubectl talks to it. It stores everything in etcd.

**Level 2 - Practitioner**: REST API: `GET /api/v1/namespaces/default/pods`. `kubectl proxy` exposes API locally. kubeconfig authenticates you. API groups: `core` (v1), `apps` (Deployments), `networking.k8s.io` (Ingress).

**Level 3 - Advanced**: Admission webhooks: `MutatingAdmissionWebhook` (modify), `ValidatingAdmissionWebhook` (validate). Server-side apply (SSA): field manager tracking for GitOps. `--audit-log-path` enables audit logging of all API operations.

**Level 4 - Expert**: Aggregated API server: CRD/Operator can register custom API groups served by the operator's own server (Metrics Server, custom admission). Request routing: API Server proxies to aggregated APIs. API server pagination: `limit` + `continue` token for large resource lists. Protobuf encoding (faster than JSON) between K8s components.

---

## ⚙️ How It Works

---

### Request Lifecycle

```
kubectl apply -f pod.yaml
  1. HTTPS request (TLS, port 6443)
  2. Authentication:
     - X.509 client cert (kubectl, kubeadm)
     - Bearer token (service accounts)
     - OIDC (external IdP: Okta, Dex)
  3. Authorization (RBAC):
     - User/Group → RoleBinding/ClusterRoleBinding → Role
     - verb: "create", resource: "pods", allowed?
  4. Admission:
     - Mutating webhooks (add labels, inject sidecars, set
       defaults)
     - OPA/Gatekeeper validation (reject policy violations)
     - Validate (schema, required fields)
  5. Persist to etcd
  6. Return 201 Created
  7. Watch event: Scheduler, Controllers notified
```

---

### API Resource Paths

```
/api/v1/namespaces/{ns}/pods
/api/v1/namespaces/{ns}/services
/api/v1/nodes
/apis/apps/v1/namespaces/{ns}/deployments
/apis/networking.k8s.io/v1/namespaces/{ns}/ingresses
/apis/batch/v1/namespaces/{ns}/jobs
```

---

### Service Account Token Authentication

```yaml
# Pod gets auto-mounted token at:
/var/run/secrets/kubernetes.io/serviceaccount/token
# Used by in-cluster components to authenticate to API Server
```

---

## 🔄 E2E Flow: Admission Webhook

```
kubectl apply -f pod.yaml (with label team=frontend)
  → API Server: authenticate + authorize
  → MutatingAdmissionWebhook (sidecar-injector):
      Pod template → add Envoy sidecar container
  → MutatingAdmissionWebhook (label-defaulter):
      Add default labels if missing
  → ValidatingAdmissionWebhook (OPA Gatekeeper):
      Check: pod has required "owner" label → ✅
  → Persist mutated Pod to etcd
  → Return to kubectl: 201 Created (with injected sidecar)
```

---

## ⚖️ Comparison Table

|                    | kubectl                 | Controller          | kubelet               |
| ------------------ | ----------------------- | ------------------- | --------------------- |
| **Talk to**        | API Server              | API Server          | API Server            |
| **Authentication** | kubeconfig (cert/token) | Service Account     | Node cert (bootstrap) |
| **Authorization**  | User RBAC               | ServiceAccount RBAC | Node authorizer       |
| **What they do**   | CRUD operations         | Watch + reconcile   | Node/Pod management   |

---

## ⚠️ Common Misconceptions

| Misconception                          | Reality                                                             |
| -------------------------------------- | ------------------------------------------------------------------- |
| "API Server failure = cluster failure" | Running Pods continue; only control plane operations fail           |
| "etcd is accessible directly"          | Only API Server has etcd access (by design)                         |
| "Admission webhooks are optional"      | Mutating webhooks are critical for service mesh (sidecar injection) |
| "API Server is slow"                   | API Server is highly optimized; bottleneck is usually etcd I/O      |

---

## 🚨 Failure Modes

| Failure                   | Impact                 | Mitigation                                                             |
| ------------------------- | ---------------------- | ---------------------------------------------------------------------- |
| API Server down           | No cluster operations  | HA: 2-3 API Server replicas behind LB                                  |
| Admission webhook timeout | API calls fail or slow | Set webhook `timeoutSeconds`; `failurePolicy: Ignore` for non-critical |
| etcd connection lost      | API Server returns 503 | Monitor etcd health; multiple etcd members                             |
| Certificate expired       | TLS handshake fails    | Monitor cert expiry; auto-renew with cert-manager                      |

---

## 🔗 Related Keywords

- [etcd](/kubernetes/etcd/) - state store for API Server
- [RBAC (K8s)](/kubernetes/rbac-k8s/) - authorization enforced by API Server
- [Admission Controllers](/kubernetes/admission-controllers/) - request pipeline
- [Service Account](/kubernetes/service-account/) - Pod authentication to API Server
- [Kubernetes Architecture](/kubernetes/kubernetes-architecture/) - overall picture

---

## 📌 Quick Reference Card

```bash
# Check API Server pod
kubectl get pods -n kube-system -l component=kube-apiserver

# API Server URL
kubectl cluster-info

# Access API directly (with auth)
kubectl proxy &
curl http://localhost:8001/api/v1/namespaces

# Check API resources
kubectl api-resources
kubectl api-versions

# Audit logs (on control plane node)
cat /var/log/kubernetes/audit.log | jq '.user.username'

# Test API Server auth
curl -k https://<api-server>:6443/version
```

---

## 🧠 Think About This

Why is the API Server stateless? So you can run multiple replicas behind a load balancer for HA. Each API Server instance handles requests independently, using etcd as the shared state. If one API Server dies, others continue. This "stateless API + stateful storage" pattern is the foundation of Kubernetes' control plane design - and the reason the API Server can be horizontally scaled while etcd cannot (etcd is stateful with Raft consensus requirements).
