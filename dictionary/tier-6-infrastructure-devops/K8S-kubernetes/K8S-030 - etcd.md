---
layout: default
title: "etcd"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /kubernetes/etcd/
id: K8S-030
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Kubernetes Architecture", "Cluster"]
used_by: ["API Server", "Kubernetes Architecture", "K8s Upgrade Strategy"]
related:
  ["API Server", "Kubernetes Architecture", "Cluster", "K8s Security Hardening"]
tags: [kubernetes, etcd, distributed-storage, raft, cluster-state, k8s]
---

# etcd

## ⚡ TL;DR

etcd is a **distributed key-value store** that holds all Kubernetes cluster state (Pods, Services, ConfigMaps, Secrets, RBAC, etc.). It uses **Raft consensus** for consistency. Losing etcd without backup = losing the entire cluster. Back it up regularly.

---

## 🔥 Problem This Solves

A distributed cluster needs a single source of truth that is consistent, fault-tolerant, and watchable. etcd provides strong consistency (linearizability), automatic leader election via Raft, and watch semantics that the API Server uses to notify controllers of changes.

---

## 📘 Textbook Definition

etcd is an open-source, distributed, reliable key-value store used as Kubernetes' backing store for all cluster data. It uses the Raft distributed consensus algorithm to ensure data consistency across multiple replicas.

---

## ⏱️ 30 Seconds

```
etcd stores (in /registry/):
  /registry/pods/default/my-pod
  /registry/services/specs/default/my-service
  /registry/configmaps/default/my-config
  /registry/secrets/default/my-secret
  /registry/deployments/apps/default/my-deploy

Endpoints:
  Client: 2379  (API Server → etcd)
  Peer:   2380  (etcd members ↔ etcd members)

Quorum for writes: (n/2) + 1 members
  3 members → tolerate 1 failure
  5 members → tolerate 2 failures
```

---

## 🔩 First Principles

- All K8s state lives in etcd - it's the single source of truth
- API Server is the **only** component that talks to etcd directly
- Raft requires a majority (quorum) to commit writes - prevents split-brain
- Watch API: clients can watch for changes (controllers poll etcd via watch, not polling)
- etcd is strongly consistent - all reads see latest committed data (linearizable)

---

## 🧪 Thought Experiment

Three etcd members. Member-3 goes down. You still have a quorum of 2/3 → reads and writes succeed. Member-2 also goes down. Only 1/3 members up → NO quorum → writes fail → cluster state frozen → Pods keep running (kubelet caches state) but no new Pods can be scheduled. This is why 3-member etcd is the minimum for HA.

---

## 🧠 Mental Model / Analogy

etcd is like the **city planning office's blueprint archive**: every building permit, zoning rule, and infrastructure plan is stored there. The city (cluster) can only function if the archive is available and accurate. If the archive burns down without backup, you don't know what the city is supposed to look like.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: etcd is where Kubernetes stores everything. Lose it, lose the cluster.

**Level 2 - Practitioner**: Runs as a Deployment (managed K8s) or on control plane nodes directly. Backup with `etcdctl snapshot save`. Restore with `etcdctl snapshot restore`. 3 or 5 members for HA.

**Level 3 - Advanced**: Raft: leader receives writes, replicates to followers, commits when majority acknowledges. Watch API: clients register watches and get notifications (not polling). Compaction: etcd must periodically compact old revisions to prevent unbounded growth.

**Level 4 - Expert**: etcd WAL (write-ahead log) ensures durability. Snapshot + WAL = full recovery point. Defragmentation reclaims space after compaction. etcd quota: default 2GB; must increase for large clusters. `ETCD_HEARTBEAT_INTERVAL` and `ETCD_ELECTION_TIMEOUT` tune leader election latency. BBolt (boltdb) is the underlying storage engine.

---

## ⚙️ How It Works

### Raft Consensus

```
Write request arrives at leader
  → Leader appends to local WAL
  → Sends AppendEntries RPC to all followers
  → Majority (quorum) acknowledge
  → Leader commits, applies to state machine
  → Returns to client
  → Followers commit on next heartbeat
```

### etcd Watch (API Server pattern)

```
Controller → API Server → etcd Watch(key="/registry/pods/")
                          etcd: sends event on change
API Server → Controller: "Pod my-pod was created/updated/deleted"
                          (not polling - event-driven)
```

### etcd Cluster Health

```bash
etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  endpoint health

etcdctl endpoint status --write-out=table
```

### etcd Backup

```bash
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-$(date +%Y%m%d).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

---

## 🔄 E2E Flow: kubectl apply

```
kubectl apply -f deployment.yaml
  → HTTPS to API Server (:6443)
  → API Server: authenticate, authorize, admit
  → API Server: serialize Deployment object to protobuf
  → etcd: PUT /registry/deployments/apps/default/my-deploy
  → etcd: Raft consensus (majority acknowledge)
  → etcd: commit
  → API Server: returns 201 Created to kubectl
  → API Server Watch: "Deployment created" event
  → Deployment Controller: notified, creates ReplicaSet
  → Scheduler: notified, assigns Pod to node
```

---

## ⚖️ Comparison Table

|                | etcd       | ZooKeeper                        | Consul          |
| -------------- | ---------- | -------------------------------- | --------------- |
| **Consensus**  | Raft       | ZAB (Zookeeper Atomic Broadcast) | Raft            |
| **API**        | gRPC/HTTP2 | ZK protocol                      | HTTP/gRPC       |
| **Watch**      | ✅ Native  | ✅ Native                        | ✅              |
| **K8s usage**  | Default    | Legacy (deprecated)              | Not used by K8s |
| **Simplicity** | High       | Lower                            | Medium          |

---

## ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                       |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| "etcd is backed up by managed K8s" | GKE/EKS/AKS manage etcd, but you should have your own backup strategy         |
| "etcd can run on worker nodes"     | etcd should ONLY run on control plane nodes (or dedicated etcd nodes)         |
| "More etcd members = better"       | Odd numbers only (3, 5, 7); more members = slower writes (more quorum needed) |
| "etcd encryption is automatic"     | Encryption at rest requires explicit `EncryptionConfiguration` on API Server  |

---

## 🚨 Failure Modes

| Failure                 | Impact                              | Mitigation                                       |
| ----------------------- | ----------------------------------- | ------------------------------------------------ |
| Quorum loss             | Cluster writes fail; reads may work | 3+ members; separate failure domains             |
| etcd disk full          | Writes fail; cluster frozen         | Monitor disk; increase quota; compact/defrag     |
| etcd slow disk          | Leader timeouts; elections          | Use SSD for etcd; separate etcd from worker disk |
| Backup corruption       | No recovery possible                | Test restore procedures regularly                |
| etcd compaction missing | Unbounded growth, OOM               | Set `--auto-compaction-retention=1`              |

---

## 🔗 Related Keywords

- [Kubernetes Architecture](/kubernetes/kubernetes-architecture/) - etcd in the control plane
- [API Server](/kubernetes/api-server/) - the only component that talks to etcd
- [Cluster](/kubernetes/cluster/) - etcd stores all cluster state
- [K8s Security Hardening](/kubernetes/k8s-security-hardening/) - etcd encryption at rest

---

## 📌 Quick Reference Card

```bash
# Check etcd pods
kubectl get pods -n kube-system -l component=etcd

# Backup
ETCDCTL_API=3 etcdctl snapshot save snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status snapshot.db --write-out=table

# Cluster health
ETCDCTL_API=3 etcdctl endpoint health \
  --cluster --write-out=table

# Defragment (after major deletions)
ETCDCTL_API=3 etcdctl defrag --cluster

# List all keys (useful for debugging)
ETCDCTL_API=3 etcdctl get "" --prefix --keys-only | head -20
```

---

## 🧠 Think About This

Why does Kubernetes only allow the API Server to talk to etcd directly? Because etcd is the crown jewel - raw access to etcd means bypassing all authentication, authorization, admission control, and audit logging. The API Server is the gatekeeper. If any component could write to etcd directly, a compromised component could corrupt cluster state undetectably. The API-server-only access pattern is a critical security design decision.
