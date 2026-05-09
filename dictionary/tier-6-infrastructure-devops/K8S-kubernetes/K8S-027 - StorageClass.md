---
version: 1
layout: default
title: "StorageClass"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /kubernetes/storageclass/
id: K8S-027
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["PersistentVolume / PVC", "Node"]
used_by: ["StatefulSet", "Database per Service"]
related:
  ["PersistentVolume / PVC", "StatefulSet", "CSI", "K8s Cost Optimization"]
tags: [kubernetes, storageclass, csi, dynamic-provisioning, k8s, storage]
---

# StorageClass

## ⚡ TL;DR

A StorageClass defines **how storage is provisioned dynamically**. It specifies the CSI provisioner (e.g., `ebs.csi.aws.com`), parameters (volume type, IOPS), and binding mode. PVCs reference a StorageClass to auto-provision cloud volumes without admin intervention.

---

## 🔥 Problem This Solves

Before StorageClass, admins had to manually pre-create PersistentVolumes for each storage request. StorageClass enables **dynamic provisioning** - PVCs automatically create cloud volumes (EBS, GCE PD, Azure Disk) on demand.

---

## 📘 Textbook Definition

A StorageClass provides a way to describe the "classes" of storage offered in a cluster. Different classes might map to different quality-of-service levels, backup policies, or arbitrary policies determined by cluster administrators. StorageClasses enable dynamic volume provisioning.

---

## ⏱️ 30 Seconds

```yaml
# AWS EBS StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
```

---

## 🔩 First Principles

- `provisioner`: which CSI driver creates the volume (cloud-provider-specific)
- `parameters`: provisioner-specific settings (disk type, IOPS, encryption)
- `volumeBindingMode: WaitForFirstConsumer`: don't create volume until Pod is scheduled (AZ-aware)
- `reclaimPolicy: Delete` (default): volume deleted when PVC deleted
- `allowVolumeExpansion: true`: PVCs can be resized after creation

---

## 🧪 Thought Experiment

Your cluster has two storage classes: `standard` (magnetic HDD, low cost) and `fast-ssd` (NVMe, high IOPS). Postgres gets `fast-ssd`. Log archival gets `standard`. The developer just puts `storageClassName: fast-ssd` in their PVC - StorageClass handles the rest, selecting the right AWS volume type automatically.

---

## 🧠 Mental Model / Analogy

StorageClass is like a **hardware catalog** for storage. Instead of ordering a specific hard drive model (PV), you pick a storage tier ("fast-ssd" or "standard"). The infrastructure team (CSI provisioner) fulfills the order with the right hardware.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: StorageClass tells Kubernetes how to create storage automatically. Pick "fast" or "cheap" and let it provision.

**Level 2 - Practitioner**: `is-default-class` annotation means PVCs without `storageClassName` get this class. `WaitForFirstConsumer` prevents AZ mismatches in multi-zone clusters.

**Level 3 - Advanced**: Multiple StorageClasses per cluster (different tiers, AZs, backup policies). CSI drivers support snapshots (`VolumeSnapshotClass`). Topology constraints: restrict provisioning to specific zones.

**Level 4 - Expert**: CSI driver consists of a controller plugin (Deployment) and node plugin (DaemonSet). Controller handles volume create/delete/snapshot. Node plugin handles attach/mount. StorageClass `volumeBindingMode: Immediate` vs `WaitForFirstConsumer` affects PV creation timing and AZ placement.

---

## ⚙️ How It Works

### Popular CSI Provisioners

| Cloud   | Provisioner             | Volume Types                            |
| ------- | ----------------------- | --------------------------------------- |
| AWS     | `ebs.csi.aws.com`       | gp2, gp3, io1, io2, st1, sc1            |
| GCP     | `pd.csi.storage.gke.io` | pd-standard, pd-ssd, pd-balanced        |
| Azure   | `disk.csi.azure.com`    | Standard_LRS, Premium_LRS, UltraSSD_LRS |
| On-prem | `cephfs.csi.ceph.com`   | CephFS, RBD                             |
| On-prem | `driver.longhorn.io`    | Longhorn distributed storage            |
| NFS     | `nfs.csi.k8s.io`        | NFS shares                              |

### StorageClass Parameters (AWS EBS)

```yaml
parameters:
  type: gp3 # gp2, gp3, io1, io2, st1, sc1
  iops: "3000" # gp3: 3000-16000
  throughput: "125" # gp3: 125-1000 MB/s
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:..." # optional KMS key
```

### Volume Binding Modes

```
Immediate:            PV created when PVC is created
                      Volume in random AZ → Pod may land in different AZ ❌

WaitForFirstConsumer: PV created when Pod using PVC is scheduled
                      Volume created in same AZ as Pod ✅
```

---

## 🔄 E2E Flow: Dynamic Provisioning

```
Developer creates PVC (storageClassName=fast-ssd, 20Gi)
  → K8s: PVC pending, storageClass=fast-ssd
  → CSI driver controller (ebs.csi.aws.com):
      - Calls AWS API: CreateVolume(type=gp3, 20Gi, az=us-east-1a)
      - Volume ID: vol-0abc123
      - Creates PV object referencing vol-0abc123
      - PVC bound to PV
  → Pod scheduled to node in us-east-1a
  → kubelet: node plugin attaches EBS volume to EC2 instance
  → kubelet: mounts volume at /var/data
  → Container starts with persistent storage
```

---

## ⚖️ Comparison Table

|                  | gp3 (default) | io2 (high IOPS)     | st1 (throughput) | sc1 (cheap) |
| ---------------- | ------------- | ------------------- | ---------------- | ----------- |
| **IOPS**         | 3000 baseline | Up to 64,000        | 500              | 250         |
| **Cost**         | Low           | High                | Low              | Lowest      |
| **Use case**     | General DB    | High-transaction DB | Sequential reads | Archive     |
| **StorageClass** | `fast-ssd`    | `high-iops`         | `throughput`     | `archive`   |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                              |
| ------------------------------------- | ------------------------------------------------------------------------------------ |
| "Default StorageClass is always best" | Default may be slow HDD; always check what default means in your cluster             |
| "Any volume can be resized"           | `allowVolumeExpansion: true` required in StorageClass AND CSI driver must support it |
| "WaitForFirstConsumer is optional"    | Required for multi-AZ; without it, volumes may land in wrong AZ                      |
| "StorageClass is cluster-wide"        | StorageClass is cluster-scoped (not namespaced); PVCs are namespaced                 |

---

## 🚨 Failure Modes

| Failure                  | Symptom                                    | Fix                                                                   |
| ------------------------ | ------------------------------------------ | --------------------------------------------------------------------- |
| StorageClass not found   | PVC stuck Pending: `no StorageClass found` | Create StorageClass or fix PVC `storageClassName`                     |
| Wrong AZ                 | Pod can't mount volume                     | Use `WaitForFirstConsumer` volumeBindingMode                          |
| CSI driver not installed | PVC stuck: `waiting for a volume`          | Install AWS EBS CSI driver or relevant driver                         |
| Resize fails             | PVC stays at old size                      | Check `allowVolumeExpansion: true`; node-side resize may need restart |

---

## 🔗 Related Keywords

- [PersistentVolume / PVC](/kubernetes/persistentvolume-pvc/) - consumes StorageClass
- [StatefulSet](/kubernetes/statefulset/) - `volumeClaimTemplates` reference StorageClass
- [K8s Cost Optimization](/kubernetes/k8s-cost-optimization/) - right-size storage tiers

---

## 📌 Quick Reference Card

```bash
# List StorageClasses
kubectl get storageclass
kubectl describe sc fast-ssd

# Set default StorageClass
kubectl patch storageclass gp2 \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
kubectl patch storageclass gp3 \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# Check which StorageClass PVC uses
kubectl get pvc db-storage -o jsonpath='{.spec.storageClassName}'

# Expand PVC (requires allowVolumeExpansion=true)
kubectl edit pvc db-storage
# Change storage: 20Gi → 50Gi
```

---

## 🧠 Think About This

In AWS, the old default StorageClass used `gp2` volumes. `gp3` volumes are cheaper AND faster (same baseline IOPS but 20% cheaper, configurable up to 16,000 IOPS separately from size). Many clusters still default to `gp2` because nothing forces an upgrade. Audit your default StorageClass - switching from gp2 to gp3 on all new PVCs is free savings with better performance.
