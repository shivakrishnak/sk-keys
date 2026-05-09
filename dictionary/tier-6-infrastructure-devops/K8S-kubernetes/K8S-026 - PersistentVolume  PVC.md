---
version: 1
layout: default
title: "PersistentVolume  PVC"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 26
permalink: /kubernetes/persistentvolume-pvc/
id: K8S-026
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Pod", "StatefulSet", "StorageClass"]
used_by: ["StatefulSet", "Database per Service"]
related: ["StorageClass", "StatefulSet", "Pod", "Namespace (K8s)"]
tags: [kubernetes, persistentvolume, pvc, storage, k8s, stateful]
---

# PersistentVolume / PVC

## ⚡ TL;DR

**PersistentVolume (PV)** = a piece of cluster storage (AWS EBS, NFS, local disk). **PersistentVolumeClaim (PVC)** = a Pod's request for storage (size, access mode). PV+PVC decouple storage provisioning from consumption. **StorageClass** enables dynamic provisioning (auto-creates PVs on demand).

---

## 🔥 Problem This Solves

Container filesystems are ephemeral - data is lost when a Pod restarts. Databases, file uploads, and application state need durable storage that outlives individual Pods. PV/PVC provides that persistence layer.

---

## 📘 Textbook Definition

A PersistentVolume (PV) is a piece of storage in the cluster provisioned by an administrator or dynamically by a StorageClass. A PersistentVolumeClaim (PVC) is a request for storage by a user. PVCs consume PV resources (like Pods consume node resources).

---

## ⏱️ 30 Seconds

```yaml
# PVC (what a Pod requests)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-storage
spec:
  accessModes:
    - ReadWriteOnce # single node read-write
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 20Gi

# Pod uses PVC
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: db-storage
volumeMounts:
  - name: data
    mountPath: /var/lib/postgresql/data
```

---

## 🔩 First Principles

- **PV** = the actual storage resource (created by admin or StorageClass)
- **PVC** = request for storage (created by developers)
- **Binding**: K8s matches PVC to a suitable PV (capacity ≥ requested, matching access modes)
- **Dynamic provisioning**: StorageClass auto-creates PV when PVC is created (no manual PV creation)
- **Access modes**: `ReadWriteOnce` (1 node R/W), `ReadOnlyMany` (N nodes read), `ReadWriteMany` (N nodes R/W)

---

## 🧪 Thought Experiment

Your Postgres Pod crashes. Without PVC: container filesystem is gone, all data lost. With PVC: the database files are on an EBS volume. New Pod is created, mounts same PVC, finds all data intact. The PVC outlives the Pod lifecycle.

---

## 🧠 Mental Model / Analogy

PVC is like a **storage locker rental request** (size: XL, duration: 1 year). The cluster (facility manager) assigns you a specific locker (PV). The locker contents survive even if you temporarily leave (Pod restarts). StorageClass is the automated locker-assignment system.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: PVC says "I need 20GB of fast storage." Kubernetes finds (or creates) a matching PV and assigns it to your Pod.

**Level 2 - Practitioner**: Access modes: `ReadWriteOnce` (databases, single-writer), `ReadOnlyMany` (shared configs), `ReadWriteMany` (requires NFS/CephFS/EFS). Reclaim policies: `Retain` (keep data after PVC delete), `Delete` (remove cloud volume), `Recycle` (deprecated).

**Level 3 - Advanced**: Dynamic provisioning via StorageClass (CSI drivers for AWS EBS, GCE PD, Azure Disk, Ceph, Longhorn). `volumeMode: Block` for raw block devices (high-performance DBs). `dataSource` for cloning volumes or creating from snapshots.

**Level 4 - Expert**: CSI (Container Storage Interface) is the standard plugin API. CSI drivers run as DaemonSets + controller. `VolumeSnapshot` CRD enables backup/restore. Topology-aware provisioning: `WaitForFirstConsumer` binding mode delays PV creation until Pod is scheduled (ensures same AZ).

---

## ⚙️ How It Works

### PV Lifecycle

```
Available → Bound → Released → Available/Deleted
           (PVC)    (PVC deleted)
```

### Dynamic Provisioning Flow

```
PVC created with storageClassName=fast-ssd
  → Storage Controller sees PVC
  → StorageClass: provisioner=ebs.csi.aws.com
  → CSI driver: AWS API CreateVolume (gp3, 20Gi, us-east-1a)
  → PV object created in K8s, bound to PVC
  → Pod scheduled: kubelet mounts EBS volume to node
  → Container filesystem at /var/lib/postgresql/data
```

### Access Modes

| Mode             | Short | Multiple Pods    | Use case                        |
| ---------------- | ----- | ---------------- | ------------------------------- |
| ReadWriteOnce    | RWO   | No (one node)    | Databases, single-writer        |
| ReadOnlyMany     | ROX   | Yes (read only)  | Shared config, static assets    |
| ReadWriteMany    | RWX   | Yes (read/write) | Shared state (NFS, CephFS, EFS) |
| ReadWriteOncePod | RWOP  | No (one Pod)     | K8s 1.22+; strictest isolation  |

### Reclaim Policies

| Policy    | On PVC Delete                             |
| --------- | ----------------------------------------- |
| `Retain`  | PV stays, data preserved (manual cleanup) |
| `Delete`  | PV and backing storage deleted            |
| `Recycle` | Deprecated (basic scrub)                  |

---

## 🔄 E2E Flow: StatefulSet PVC per Pod

```
StatefulSet postgres (3 replicas) with volumeClaimTemplates
  → Creates PVCs:
      data-postgres-0 (20Gi, RWO)
      data-postgres-1 (20Gi, RWO)
      data-postgres-2 (20Gi, RWO)
  → StorageClass creates 3 EBS volumes
  → Each Pod mounts its own EBS volume

postgres-1 Pod deleted (node failure)
  → New postgres-1 Pod created
  → Kubelet: attach EBS volume for data-postgres-1
  → Mount at /var/lib/postgresql/data
  → Postgres starts with all existing data intact
```

---

## ⚖️ Comparison Table

|                           | emptyDir      | hostPath       | PVC      |
| ------------------------- | ------------- | -------------- | -------- |
| **Survives Pod restart**  | ❌            | ✅ (same node) | ✅       |
| **Survives node failure** | ❌            | ❌             | ✅       |
| **Shareable across Pods** | ❌ (same Pod) | ❌             | ✅ (RWX) |
| **Production databases**  | ❌            | ❌             | ✅       |

---

## ⚠️ Common Misconceptions

| Misconception                        | Reality                                                      |
| ------------------------------------ | ------------------------------------------------------------ |
| "PVC is deleted when Pod is deleted" | PVC lifecycle is independent of Pod lifecycle                |
| "Any access mode works everywhere"   | RWX requires NFS/CephFS; AWS EBS only supports RWO           |
| "PV capacity is enforced"            | Most CSI drivers don't enforce capacity until resize         |
| "StatefulSet PVCs auto-delete"       | PVCs are NOT deleted when StatefulSet is deleted - by design |

---

## 🚨 Failure Modes

| Failure           | Symptom                | Fix                                                     |
| ----------------- | ---------------------- | ------------------------------------------------------- |
| PVC stuck Pending | Pod can't start        | Check StorageClass exists; PV availability; AZ match    |
| RWX not supported | Multi-Pod mount fails  | Use NFS/EFS/CephFS for RWX; EBS is RWO only             |
| PVC in wrong AZ   | Pod can't mount volume | Use `WaitForFirstConsumer` binding mode in StorageClass |
| Volume full       | Container writes fail  | Monitor disk usage; request volume expansion            |

---

## 🔗 Related Keywords

- [StorageClass](/kubernetes/storageclass/) - dynamic provisioning
- [StatefulSet](/kubernetes/statefulset/) - uses PVCs for stable storage
- [Pod](/kubernetes/pod/) - mounts PVCs via volumes
- [Kubernetes Secrets Management](/kubernetes/kubernetes-secrets-management/) - secrets in volumes

---

## 📌 Quick Reference Card

```bash
# List PVCs
kubectl get pvc
kubectl describe pvc db-storage

# List PVs
kubectl get pv

# Check PVC events (why pending)
kubectl describe pvc db-storage
# Look for: "no persistent volumes available" or "no matching StorageClass"

# Expand PVC (requires StorageClass allowVolumeExpansion=true)
kubectl patch pvc db-storage -p '{"spec":{"resources":{"requests":{"storage":"50Gi"}}}}'

# Volume snapshot (if CSI supports it)
kubectl apply -f volumesnapshot.yaml
```

---

## 🧠 Think About This

`WaitForFirstConsumer` binding mode in StorageClass is a subtle but critical setting for multi-AZ clusters. Without it, PVs (and cloud volumes) are created in a random AZ at PVC creation time. If the Pod is later scheduled to a different AZ, it can't mount the volume (EBS volumes are AZ-scoped). With `WaitForFirstConsumer`, volume creation is deferred until the Pod is scheduled - ensuring the volume is created in the same AZ as the Pod.
