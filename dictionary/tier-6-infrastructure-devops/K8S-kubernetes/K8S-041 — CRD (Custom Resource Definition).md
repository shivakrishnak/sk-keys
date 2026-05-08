---
layout: default
title: "CRD (Custom Resource Definition)"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 41
permalink: /kubernetes/crd-custom-resource-definition/
id: K8S-041
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["API Server", "RBAC (K8s)", "Operators"]
used_by: ["Operators", "KEDA", "Admission Controllers"]
related: ["Operators", "API Server", "Admission Controllers", "RBAC (K8s)"]
tags: [kubernetes, crd, custom-resource, api-extension, k8s]
---

# CRD (Custom Resource Definition)

## ⚡ TL;DR

A **CRD** extends the Kubernetes API with a new resource type. After installing a CRD, you can create objects of that type just like Deployments or Services. CRDs are the foundation for Kubernetes extensibility — Operators, KEDA, cert-manager, Prometheus, ArgoCD all install CRDs.

---

## 🔥 Problem This Solves

Kubernetes has ~50 built-in resource types. Complex applications need more: `PostgreSQLCluster`, `KafkaTopic`, `Certificate`, `ScaledObject`. Without CRDs, you'd need custom external systems. CRDs extend the Kubernetes API declaratively, using the same etcd, RBAC, kubectl, and API Server for custom types.

---

## 📘 Textbook Definition

A Custom Resource Definition (CRD) is a Kubernetes API extension mechanism that allows users to register custom resource types in the API Server. Once a CRD is installed, instances (Custom Resources) can be created, read, updated, and deleted using standard Kubernetes API conventions.

---

## ⏱️ 30 Seconds

```yaml
# 1. Install CRD (defines the type)
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.databases.example.com
spec:
  group: databases.example.com
  names:
    kind: PostgreSQLCluster
    plural: postgresclusters
    singular: postgrescluster
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
    schema: ...

# 2. Use the custom resource (instance)
apiVersion: databases.example.com/v1
kind: PostgreSQLCluster
metadata:
  name: my-postgres
spec:
  replicas: 3
```

---

## 🔩 First Principles

- CRDs are stored in etcd just like any other Kubernetes object
- After CRD installation, the API Server serves a new REST endpoint: `/apis/<group>/<version>/<resource>`
- Custom Resources require an Operator (controller) to have any operational effect — CRD alone just stores data
- Schema (OpenAPI v3) in CRD validates custom resources at admission time
- CRDs support multiple versions with conversion webhooks for migration

---

## 🧪 Thought Experiment

You install cert-manager. It creates 3 CRDs: `Certificate`, `ClusterIssuer`, `CertificateRequest`. Now `kubectl get certificates` works, you can apply `Certificate` YAML, and cert-manager's controller watches those objects and automatically provisions TLS certs from Let's Encrypt. The CRD made Certificate a first-class Kubernetes citizen — no external cert management database needed.

---

## 🧠 Mental Model / Analogy

CRDs are like **adding new words to a language dictionary**: the dictionary is the Kubernetes API Server. Once you add the word `PostgreSQLCluster`, everyone in the ecosystem (kubectl, RBAC, GitOps tools, audit logs) understands that word. Before the CRD, the word didn't exist; after, it's a first-class citizen with full API support.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: CRDs let you create custom resource types in Kubernetes that work just like built-in types.

**Level 2 — Practitioner**: Install a CRD YAML → kubectl can now `get`/`create`/`delete` that resource type. An Operator watches those objects and takes action. `kubectl api-resources` shows all installed types.

**Level 3 — Advanced**: Structural schema (OpenAPI v3): validates spec at admission, enables `kubectl explain`, generates client code. Status subresource: operators update `.status` separately from `.spec` (RBAC-separated, no resourceVersion conflict). `additionalPrinterColumns`: custom columns in `kubectl get` output.

**Level 4 — Expert**: Multi-version CRDs with conversion webhooks: maintain v1alpha1 and v1 simultaneously, conversion webhook translates between versions. `x-kubernetes-preserve-unknown-fields: true` for dynamic schemas. Aggregated API Server (AA): advanced alternative to CRDs for full API group control with custom storage backends.

---

## ⚙️ How It Works

### Full CRD Specification

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.databases.example.com
spec:
  group: databases.example.com
  scope: Namespaced # or Cluster
  names:
    kind: PostgreSQLCluster
    listKind: PostgreSQLClusterList
    plural: postgresclusters
    singular: postgrescluster
    shortNames:
      - pgcluster
    categories:
      - all
  versions:
    - name: v1
      served: true # this version accepts API requests
      storage: true # this version stored in etcd
      subresources:
        status: {} # enable status subresource
        scale: # enable scale subresource (for HPA)
          specReplicasPath: .spec.replicas
          statusReplicasPath: .status.replicas
      additionalPrinterColumns:
        - name: Replicas
          type: integer
          jsonPath: .spec.replicas
        - name: Ready
          type: string
          jsonPath: .status.ready
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: [replicas]
              properties:
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
                version:
                  type: string
                  enum: ["14", "15", "16"]
                storage:
                  type: string
                  pattern: "^[0-9]+Gi$"
            status:
              type: object
              properties:
                ready:
                  type: boolean
                primary:
                  type: string
```

### Custom Resource Instance

```yaml
apiVersion: databases.example.com/v1
kind: PostgreSQLCluster
metadata:
  name: my-postgres
  namespace: data
spec:
  replicas: 3
  version: "15"
  storage: "100Gi"
# status set by operator:
status:
  ready: true
  primary: my-postgres-0
```

### API Endpoints After CRD Install

```
GET  /apis/databases.example.com/v1/namespaces/{ns}/postgresclusters
POST /apis/databases.example.com/v1/namespaces/{ns}/postgresclusters
GET  /apis/databases.example.com/v1/namespaces/{ns}/postgresclusters/{name}
PUT  /apis/databases.example.com/v1/namespaces/{ns}/postgresclusters/{name}
DEL  /apis/databases.example.com/v1/namespaces/{ns}/postgresclusters/{name}
GET  /apis/databases.example.com/v1/namespaces/{ns}/postgresclusters/{name}/status
PUT  /apis/databases.example.com/v1/namespaces/{ns}/postgresclusters/{name}/status
```

---

## 🔄 E2E Flow: CRD Lifecycle

```
Admin installs CRD:
  kubectl apply -f postgres-crd.yaml
  → CRD stored in etcd
  → API Server registers new REST group
  → kubectl api-resources shows PostgreSQLCluster

Operator starts:
  → Registers Watch for PostgreSQLCluster objects
  → Sets up informer cache

User creates resource:
  kubectl apply -f postgres-cluster.yaml
  → Validation against CRD schema (rejects if invalid)
  → Stored in etcd
  → Operator receives Watch event
  → Reconcile loop executes

kubectl get pgcluster
NAME          REPLICAS   READY   AGE
my-postgres   3          true    5m
(additionalPrinterColumns from CRD)
```

---

## ⚖️ Comparison Table

|                        | CRD               | Built-in Resource | ConfigMap (for custom data) |
| ---------------------- | ----------------- | ----------------- | --------------------------- |
| **Type safety**        | ✅ OpenAPI schema | ✅ Strong typing  | ❌ freeform                 |
| **RBAC**               | ✅ Per-resource   | ✅                | Only at ConfigMap level     |
| **kubectl support**    | ✅ Full           | ✅                | ✅                          |
| **Custom validation**  | ✅ + webhook      | ✅                | ❌                          |
| **Status subresource** | ✅                | ✅                | ❌                          |

---

## ⚠️ Common Misconceptions

| Misconception              | Reality                                                                           |
| -------------------------- | --------------------------------------------------------------------------------- |
| "CRD alone does something" | CRD defines type; you need a controller/operator to act on instances              |
| "CRDs are namespaced"      | CRDs themselves are cluster-scoped; instances can be namespaced or cluster-scoped |
| "CRD deletion is safe"     | Deleting a CRD deletes ALL instances of that type — very destructive!             |
| "CRD schemas are optional" | Required from K8s 1.22+; structural schema enables validation and kubectl explain |

---

## 🚨 Failure Modes

| Failure                                | Symptom                           | Fix                                                                |
| -------------------------------------- | --------------------------------- | ------------------------------------------------------------------ |
| Schema validation rejects valid object | `invalid: spec.replicas`          | Check CRD schema enums/patterns; use `kubectl explain`             |
| CRD deleted accidentally               | All custom objects gone           | Restore from etcd backup; re-install CRD; restore objects from Git |
| Version mismatch                       | Controller can't read old objects | Add conversion webhook; add new version to CRD                     |
| Too many CRDs                          | API Server slowdown               | Each CRD adds API endpoints; limit to necessary ones               |

---

## 🔗 Related Keywords

- [Operators](/kubernetes/operators/) — use CRDs to define and manage applications
- [API Server](/kubernetes/api-server/) — registers and serves CRD endpoints
- [Admission Controllers](/kubernetes/admission-controllers/) — validate CRD instances via webhooks
- [RBAC (K8s)](/kubernetes/rbac-k8s/) — fine-grained access control on custom resources

---

## 📌 Quick Reference Card

```bash
# List all CRDs in cluster
kubectl get crds

# Get description of custom resource fields
kubectl explain postgresclusters.spec

# List all instances of a CRD
kubectl get postgresclusters -A

# Watch a custom resource
kubectl get postgresclusters -w

# Get full YAML
kubectl get postgrescluster my-postgres -o yaml

# Check CRD versions
kubectl get crd postgresclusters.databases.example.com -o jsonpath='{.spec.versions[*].name}'
```

---

## 🧠 Think About This

CRDs have become so prevalent that a typical production Kubernetes cluster has 50+ CRDs installed (Prometheus Operator, cert-manager, KEDA, ArgoCD, Istio, etc. each install many). This means the Kubernetes API is not "Kubernetes" anymore — it's a platform foundation that each team extends for their domain. The Kubernetes API machinery (RBAC, etcd, informers, admission webhooks) becomes a universal control plane for any distributed system concern, not just container orchestration.
