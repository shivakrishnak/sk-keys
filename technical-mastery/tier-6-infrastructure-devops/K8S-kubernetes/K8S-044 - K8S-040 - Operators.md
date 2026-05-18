---
version: 1
layout: default
title: "Operators"
parent: "Kubernetes"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/kubernetes/operators/
id: K8S-044
category: "Kubernetes"
difficulty: "★★★"
depends_on:
  [
    "CRD (Custom Resource Definition)",
    "Controller Manager",
    "API Server",
    "RBAC (K8s)",
  ]
used_by: ["ArgoCD", "FluxCD", "KEDA"]
related:
  [
    "CRD (Custom Resource Definition)",
    "Controller Manager",
    "Admission Controllers",
    "RBAC (K8s)",
  ]
tags: [kubernetes, operators, controller, crd, automation, k8s]
---

## ⚡ TL;DR

A Kubernetes **Operator** is a custom controller that encodes operational domain knowledge about a stateful application (database, message broker, ML model) into Kubernetes-native code. It watches custom resources (CRDs) and automates complex Day 2 operations: backups, failover, scaling, config changes, upgrades.

---

## 🔥 Problem This Solves

Stateful applications like PostgreSQL, Kafka, or Elasticsearch require complex lifecycle management: initial configuration, cluster expansion, leader election recovery, backups, rolling upgrades preserving quorum. Helm can install them, but can't react to events. Operators automate Day 2 operations continuously.

---

## 📘 Textbook Definition

An Operator is a method of packaging, deploying, and managing a Kubernetes application that extends the Kubernetes API using Custom Resource Definitions and controllers. The controller continuously reconciles observed cluster state with the desired state described in custom resources.

---

## ⏱️ 30 Seconds

```yaml
# You define this custom resource
apiVersion: databases.example.com/v1
kind: PostgreSQLCluster
metadata:
  name: my-postgres
spec:
  replicas: 3
  version: "15"
  storage: 100Gi
  backupSchedule: "0 2 * * *"

# Operator reacts:
#  → Creates 3 StatefulSet Pods
#  → Configures replication
#  → Schedules backups
#  → Promotes replica if primary fails
```

---

## 🔩 First Principles

- **Operator = CRD + Controller**: CRD defines new resource type, Controller watches it and acts
- Reconcile loop: `Observe desired state → Observe actual state → Diff → Act to converge`
- Operators run inside the cluster as Deployments
- Operators have RBAC permissions to manage cluster resources on your behalf
- Maturity levels: Basic Install → Seamless Upgrades → Full Lifecycle → Deep Insights → Auto Pilot

---

## 🧪 Thought Experiment

Your PostgreSQL primary fails at 2am. Without an Operator: PagerDuty alert → DBA wakes up → manually promotes replica → updates connection strings → restarts app pods. With the CloudNativePG operator: automatic failover in 30 seconds, new primary elected, existing connections rerouted. On-call team sleeps through it.

---

## 🧠 Mental Model / Analogy

An Operator is the **DevOps expertise encoded as code**: a senior DBA who never sleeps, knows every runbook by heart, and executes it in seconds. The CRD is the order form ("I want a 3-node PostgreSQL cluster with daily backups"); the Operator is the expert who fulfills it and keeps it running.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Operators automate complex apps on Kubernetes. Popular ones: Prometheus Operator, Strimzi (Kafka), CloudNativePG.

**Level 2 - Practitioner**: An Operator watches CRDs. When you create a `PostgreSQLCluster` object, the Operator creates the underlying StatefulSets, Services, ConfigMaps, and manages their lifecycle. OperatorHub.io catalogs hundreds of operators.

**Level 3 - Advanced**: Operator SDK (Go) / Kubebuilder for building operators. Reconcile function signature: `Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error)`. Controller-runtime library handles: caching (informers), watching, queuing, leader election. Finalizers: block deletion until cleanup completes.

**Level 4 - Expert**: Operator maturity model (OLM levels): Level 1 (install) → Level 5 (auto-pilot: self-scaling, self-healing, auto-tuning). Operator Lifecycle Manager (OLM): manages operator install, upgrade, dependency resolution in clusters. Cluster API operators manage Kubernetes node lifecycle. Multi-tenant operators: single operator instance managing resources across namespaces with RBAC delegation.

---

## ⚙️ How It Works

---

### Operator Architecture

```
User creates:
  PostgreSQLCluster CRD instance

Operator watches:
  → Informer cache sees new event
  → Puts into reconcile queue

Reconcile function runs:
  1. Fetch current state of PostgreSQLCluster
  2. Compute desired state
  3. Create/Update/Delete subordinate resources:
     - StatefulSet (Postgres pods)
     - Services (primary, replica)
     - ConfigMaps (postgresql.conf)
     - Secrets (passwords)
     - CronJobs (backups)
  4. Update status subresource with observed state
  5. Return: reconcile after 60s (re-queue)
```

---

### Simple Operator in Go (controller-runtime)

```go
//
// +kubebuilder:rbac:groups=databases.example.com,resources=postgresclusters,verbs=get;list;watch;create;update;patch;delete
//
// +kubebuilder:rbac:groups=apps,resources=statefulsets,verbs=get;list;watch;create;update;patch

type PostgreSQLClusterReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *PostgreSQLClusterReconciler) Reconcile(ctx context.Context,
    req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // Fetch the PostgreSQLCluster instance
    cluster := &databasesv1.PostgreSQLCluster{}
    if err := r.Get(ctx, req.NamespacedName, cluster); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Reconcile StatefulSet
    sts := r.buildStatefulSet(cluster)
    if err := controllerutil.CreateOrUpdate(ctx, r.Client, sts,
        func() error {
        sts.Spec.Replicas = &cluster.Spec.Replicas
        return controllerutil.SetControllerReference(cluster, sts,
            r.Scheme)
    }); err != nil {
        return ctrl.Result{}, err
    }

    // Update status
    cluster.Status.Ready = true
    r.Status().Update(ctx, cluster)

    // Requeue after 60s to catch drift
    return ctrl.Result{RequeueAfter: 60 * time.Second}, nil
}
```

---

### CRD with Status Subresource

```yaml
apiVersion: databases.example.com/v1
kind: PostgreSQLCluster
metadata:
  name: my-postgres
spec:
  replicas: 3
  version: "15"
status: # Operator writes here
  ready: true
  primary: my-postgres-0
  replicas:
    - my-postgres-1
    - my-postgres-2
  lastBackup: "2024-01-15T02:00:00Z"
```

---

## 🔄 E2E Flow: Operator Reconciliation

```
User: kubectl apply -f postgres-cluster.yaml
  → API Server stores PostgreSQLCluster object

Operator (running in cluster):
  → Informer detects new object
  → Event in reconcile queue

Reconcile loop iteration 1:
  → Get desired: 3 replicas, version 15
  → Get actual: 0 pods exist
  → Create StatefulSet with 3 replicas
  → K8s creates 3 PostgreSQL pods
  → Update status: ready=false, waiting

Reconcile loop iteration 2 (after pods start):
  → Get actual: 3 pods running
  → Configure replication (exec init commands)
  → Update status: ready=true, primary=my-postgres-0

Ongoing:
  → Primary crashes → operator promotes my-postgres-1 →
    updates status
  → User sets spec.replicas=5 → operator scales StatefulSet
  → CronJob triggers backup → operator records lastBackup
    in status
```

---

## ⚖️ Comparison Table

|                       | Operator      | Helm Chart | StatefulSet (manual) |
| --------------------- | ------------- | ---------- | -------------------- |
| **Day 2 operations**  | ✅ Automated  | ❌ Manual  | ❌ Manual            |
| **Failover**          | ✅ Automatic  | ❌         | ❌                   |
| **Backup automation** | ✅ CRD-driven | ❌         | ❌                   |
| **Complexity**        | High          | Medium     | Medium               |
| **Custom logic**      | ✅ Full       | ❌         | Limited              |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                             |
| ----------------------------------- | --------------------------------------------------------------------------------------------------- |
| "Operators are only for databases"  | Operators exist for networking (Calico), observability (Prometheus), GitOps (ArgoCD), ML (Kubeflow) |
| "Operators replace StatefulSets"    | Operators use StatefulSets under the hood                                                           |
| "Building an operator is simple"    | Controller-runtime helps, but production-quality operators require deep domain expertise            |
| "Operators run outside the cluster" | Operators run inside the cluster as Deployments with RBAC permissions                               |

---

## 🚨 Failure Modes

| Failure                | Symptom                       | Fix                                                                                                    |
| ---------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------ |
| Reconcile panic        | Operator crashes in loop      | Add recover(); check for nil pointers in reconcile                                                     |
| Missing RBAC           | "cannot list pods" error      | Ensure operator ServiceAccount has correct ClusterRole                                                 |
| Finalizer deadlock     | Object stuck in "Terminating" | Manually remove finalizer: `kubectl patch <resource> -p '{"metadata":{"finalizers":[]}}' --type=merge` |
| Status update conflict | `resource version conflict`   | Use optimistic locking retry; use `Status().Update()` not `Update()`                                   |

---

## 🔗 Related Keywords

- [CRD (Custom Resource Definition)](/kubernetes/crd-custom-resource-definition/) - the custom type operators manage
- [Controller Manager](/kubernetes/controller-manager/) - same reconcile loop pattern
- [Admission Controllers](/kubernetes/admission-controllers/) - webhooks operators use
- [RBAC (K8s)](/kubernetes/rbac-k8s/) - operators need RBAC permissions

---

## 📌 Quick Reference Card

```bash
# Popular operators
# PostgreSQL: CloudNativePG
# Kafka: Strimzi
# Prometheus: kube-prometheus-stack
# Elasticsearch: ECK (Elastic Cloud on K8s)
# Cert management: cert-manager
# GitOps: ArgoCD, FluxCD

# OperatorHub catalog
https://operatorhub.io

# Operator SDK
operator-sdk init --domain example.com --repo github.com/example/myoperator
operator-sdk create api --group databases --version v1 --kind PostgreSQLCluster

# Check operator status
kubectl get pods -n operators
kubectl logs deployment/my-operator -n operators
```

---

## 🧠 Think About This

The "Don't use Kubernetes for stateful apps" advice is outdated. With mature operators (CloudNativePG for Postgres, Strimzi for Kafka, ECK for Elasticsearch), running stateful workloads in Kubernetes is production-grade. The key insight is that these operators encode years of operational expertise - the same knowledge that SREs apply manually. The question isn't "can Kubernetes run stateful apps" - it's "does a mature operator exist for your specific technology?" For major technologies in 2024, the answer is usually yes.
