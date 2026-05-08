---
layout: default
title: "StatefulSet"
parent: "Kubernetes"
nav_order: 13
permalink: /kubernetes/statefulset/
id: K8S-013
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "Deployment", "PersistentVolume / PVC"]
used_by: ["Database per Service", "Event Sourcing in Microservices"]
related:
  [
    "Deployment",
    "PersistentVolume / PVC",
    "StorageClass",
    "Headless Service",
    "DaemonSet",
  ]
tags: [kubernetes, statefulset, stateful, persistent-storage, k8s, database]
---

# StatefulSet

## ⚡ TL;DR

A StatefulSet manages **stateful Pods** with stable network identities (`pod-0`, `pod-1`), stable persistent storage (each Pod gets its own PVC), and ordered deployment/scaling. Use for databases, message queues, and clustered applications.

---

## 🔥 Problem This Solves

Databases and clustered apps (Kafka, Zookeeper, Cassandra) need stable hostnames, ordered startup/shutdown, and dedicated persistent storage that survives Pod restarts. A Deployment's random Pod names and shared storage can't support this.

---

## 📘 Textbook Definition

A StatefulSet manages the deployment and scaling of a set of Pods, and provides guarantees about ordering and uniqueness. Unlike a Deployment, a StatefulSet maintains a sticky identity for each Pod: stable network identity and persistent storage.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: "postgres" # must match Headless Service name
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: "fast-ssd"
        resources:
          requests:
            storage: 20Gi
```

Pod names: `postgres-0`, `postgres-1`, `postgres-2`
DNS: `postgres-0.postgres.default.svc.cluster.local`

---

## 🔩 First Principles

- **Stable Pod name**: `<statefulset>-<ordinal>` — survives restarts
- **Stable network identity**: requires a **Headless Service** (`clusterIP: None`)
- **Stable storage**: `volumeClaimTemplates` creates a unique PVC per Pod; PVC survives Pod deletion
- **Ordered operations**: scale-up goes 0→1→2; scale-down goes 2→1→0

---

## 🧪 Thought Experiment

A Kafka cluster has 3 brokers. Broker-0 is the leader for partition 1. If you use a Deployment, broker-0 could restart as a random hostname — Kafka's peer discovery breaks. With StatefulSet, `kafka-0` is always `kafka-0`, and peers connect via `kafka-0.kafka.default.svc.cluster.local`. Stable identity = stable clustering.

---

## 🧠 Mental Model / Analogy

StatefulSet is like **numbered library shelves**: shelf-0, shelf-1, shelf-2. Each shelf has its own books (PVC). When you move a shelf, the books stay on that specific numbered shelf, not randomly redistributed. And you always fill shelf-0 before shelf-1 (ordered startup).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Use StatefulSet for anything that needs to remember its data and identity after a restart — like a database.

**Level 2 — Practitioner**: Each Pod gets its own PVC (not shared). Pods are named `<name>-0`, `<name>-1`. Requires a Headless Service for DNS. Delete Pod → new Pod with same name gets same PVC.

**Level 3 — Advanced**: `podManagementPolicy: Parallel` overrides ordered startup for faster deployments when ordering isn't needed. `updateStrategy: RollingUpdate` with `partition` for canary updates (only update Pods with ordinal ≥ partition).

**Level 4 — Expert**: PVCs are NOT deleted when StatefulSet is deleted — manual cleanup required. `Retain` reclaim policy prevents data loss. Headless Service enables per-Pod DNS. `readinessGates` and `preStop` hooks enable clean cluster membership removal before Pod stops.

---

## ⚙️ How It Works

### Headless Service (Required)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  clusterIP: None # headless
  selector:
    app: postgres
  ports:
    - port: 5432
```

DNS record per Pod:

```
postgres-0.postgres.default.svc.cluster.local → Pod-0 IP
postgres-1.postgres.default.svc.cluster.local → Pod-1 IP
postgres-2.postgres.default.svc.cluster.local → Pod-2 IP
```

### VolumeClaimTemplates

```
StatefulSet creates PVCs automatically:
  data-postgres-0
  data-postgres-1
  data-postgres-2

If postgres-1 Pod is deleted → new postgres-1 Pod mounts data-postgres-1 PVC
```

### Ordered Startup/Shutdown

```
Scale UP:   0 → 1 → 2 (each waits for previous to be Ready)
Scale DOWN: 2 → 1 → 0 (reverse order)
Update:     N → N-1 → ... → 0 (reverse order, each waits for Ready)
```

---

## 🔄 E2E Flow: Database Recovery

```
postgres-1 Pod crashes
  → StatefulSet creates new postgres-1 Pod
  → Same name: postgres-1
  → Same DNS: postgres-1.postgres.default.svc.cluster.local
  → Same PVC: data-postgres-1 (with existing data!)
  → App reconnects using stable hostname
  → No data loss, no peer reconfiguration needed
```

---

## ⚖️ Comparison Table

|                   | StatefulSet               | Deployment            |
| ----------------- | ------------------------- | --------------------- |
| **Pod names**     | Stable (`pod-0`, `pod-1`) | Random (`pod-abc123`) |
| **Storage**       | Unique PVC per Pod        | Shared or ephemeral   |
| **Startup**       | Ordered (0, 1, 2, ...)    | Parallel (random)     |
| **Use case**      | Databases, queues, caches | Stateless services    |
| **PVC lifecycle** | Separate from Pod         | Deleted with Pod      |

---

## ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                |
| -------------------------------------------- | ---------------------------------------------------------------------- |
| "Deleting StatefulSet deletes PVCs"          | PVCs are NOT deleted automatically — manual cleanup needed             |
| "StatefulSet = Deployment with storage"      | StatefulSet has ordered ops, stable identity — fundamentally different |
| "Any Service works with StatefulSet"         | Headless Service (`clusterIP: None`) required for per-Pod DNS          |
| "StatefulSet Pods auto-heal like Deployment" | Yes, but ordered and with same stable identity                         |

---

## 🚨 Failure Modes

| Failure                        | Symptom                                | Fix                                                |
| ------------------------------ | -------------------------------------- | -------------------------------------------------- |
| Headless Service missing       | Pods can't discover each other         | Create `clusterIP: None` Service                   |
| PVC not provisioned            | Pods stuck Pending                     | Check StorageClass, PV availability                |
| Split-brain in ordered startup | Pod-1 tries to join before Pod-0 ready | Use readiness probes; StatefulSet waits by default |
| Data lost on PVC deletion      | Data gone after manual PVC delete      | Use `Retain` reclaim policy                        |

---

## 🔗 Related Keywords

- [PersistentVolume / PVC](/kubernetes/persistentvolume-pvc/) — storage backing
- [StorageClass](/kubernetes/storageclass/) — dynamic volume provisioning
- [Deployment](/kubernetes/deployment/) — for stateless workloads
- [Service (K8s)](/kubernetes/service-k8s/) — Headless Service requirement

---

## 📌 Quick Reference Card

```bash
# Get StatefulSets
kubectl get statefulsets
kubectl describe sts postgres

# Scale
kubectl scale sts postgres --replicas=5

# Check PVCs created
kubectl get pvc | grep postgres

# Delete StatefulSet (PVCs remain!)
kubectl delete sts postgres

# Delete PVCs manually
kubectl delete pvc -l app=postgres

# Rolling update with partition (canary: only pod-2+)
kubectl patch sts postgres -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":2}}}}'
```

---

## 🧠 Think About This

Why do StatefulSet PVCs outlive the StatefulSet? Data durability. If a StatefulSet is accidentally deleted (perhaps a `kubectl delete -f` gone wrong), the data should survive. This "safe by default" behavior means you must manually clean up PVCs — which is intentional friction to prevent accidental data loss.
