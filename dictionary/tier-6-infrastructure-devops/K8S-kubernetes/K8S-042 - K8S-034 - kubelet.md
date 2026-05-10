---
version: 1
layout: default
title: "kubelet"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /kubernetes/kubelet/
id: K8S-042
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Pod", "Node", "Kubernetes Architecture"]
used_by:
  [
    "Readiness vs Liveness vs Startup Probe",
    "Resource Requests / Limits",
    "ConfigMap",
    "Secret",
  ]
related:
  [
    "Node",
    "Kubernetes Architecture",
    "kube-proxy",
    "Container Runtime",
    "DaemonSet",
  ]
tags: [kubernetes, kubelet, node-agent, pod-lifecycle, cri, k8s]
---

# kubelet

## ⚡ TL;DR

The kubelet is the **node agent** on every worker node. It watches the API Server for Pods assigned to its node, calls the container runtime (containerd via CRI) to start/stop containers, runs probes, reports node and Pod status back to the API Server, and manages volumes.

---

## 🔥 Problem This Solves

Once the Scheduler assigns a Pod to a node, something on that node must actually start the containers, manage their lifecycle, run health probes, and report status. That's the kubelet's job.

---

## 📘 Textbook Definition

The kubelet is an agent that runs on each node in the cluster. It ensures that containers are running in a Pod by monitoring PodSpecs and communicating with the container runtime. The kubelet reports node and Pod status to the control plane via the API Server.

---

## ⏱️ 30 Seconds

```
kubelet responsibilities:
  1. Watch API Server: "what Pods are assigned to my node?"
  2. Call CRI (containerd):
     - Pull images
     - Create containers
     - Start/stop containers
  3. Run probes:
     - Liveness → kill container if failing
     - Readiness → remove from Service endpoints if failing
     - Startup → hold liveness probe until app starts
  4. Manage volumes:
     - Mount ConfigMaps, Secrets, PVCs
  5. Report status:
     - Node conditions (Ready, MemoryPressure, ...)
     - Pod phase, container status
     - Resource usage (to Metrics Server)
```

---

## 🔩 First Principles

- kubelet is the only control plane component that runs on worker nodes
- kubelet uses **CRI (Container Runtime Interface)** to talk to containerd/CRI-O
- kubelet does NOT talk to etcd directly - only to API Server
- Static Pods: kubelet can start Pods from local files (`/etc/kubernetes/manifests/`) - used for control plane components
- kubelet caches PodSpecs - can manage Pods even if API Server is temporarily unreachable

---

## 🧪 Thought Experiment

You remove the `kubectl apply` and try to start a Pod by writing a file to `/etc/kubernetes/manifests/my-pod.yaml` on a node. The kubelet reads this "static pod manifest" and starts the container without any interaction with the API Server or Scheduler. This is exactly how kube-apiserver, etcd, and kube-scheduler are bootstrapped on control plane nodes.

---

## 🧠 Mental Model / Analogy

The kubelet is like the **factory floor manager**: the corporate office (API Server/Scheduler) decides which jobs to assign to which factory (node), and the floor manager (kubelet) on each factory floor executes those jobs - managing workers (containers), checking quality (probes), and reporting production status (Pod status) back to headquarters.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: kubelet makes containers actually run on a node, following orders from the API Server.

**Level 2 - Practitioner**: kubelet → containerd (via CRI) → container. Runs liveness/readiness/startup probes. Reports container status. Handles image pulls, volume mounts.

**Level 3 - Advanced**: CRI: kubelet calls `RunPodSandbox`, `CreateContainer`, `StartContainer`. Device plugins: GPUs, FPGAs via kubelet plugin API. `--pod-manifest-path` for static pods. Eviction manager: kubelet evicts Pods when node is under memory/disk pressure.

**Level 4 - Expert**: `maxPods` (default 110 per node) limits Pod density. `kubelet-reserved` and `system-reserved` resources subtracted from allocatable. `syncPeriod` (10s): how often kubelet syncs Pod state. CRI uses gRPC (`/var/run/containerd/containerd.sock`). `evictionHard` thresholds trigger Pod eviction before OOMKill.

---

## ⚙️ How It Works

### CRI (Container Runtime Interface)

```
kubelet
  ↓ gRPC
CRI shim (containerd / CRI-O)
  ↓
OCI runtime (runc / kata-containers / gVisor)
  ↓
Container process
```

### Probe Types

```yaml
containers:
  - name: app
    livenessProbe: # restart container if fails
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe: # remove from Service endpoints if fails
      httpGet:
        path: /ready
        port: 8080
      periodSeconds: 5
      failureThreshold: 3
    startupProbe: # hold liveness until app starts
      httpGet:
        path: /health
        port: 8080
      failureThreshold: 30 # 30 × 10s = 5 min startup budget
      periodSeconds: 10
```

### Static Pods (Control Plane Bootstrap)

```
/etc/kubernetes/manifests/
  kube-apiserver.yaml     ← kubelet reads, starts API Server
  etcd.yaml               ← kubelet reads, starts etcd
  kube-controller-manager.yaml
  kube-scheduler.yaml
```

---

## 🔄 E2E Flow: Pod Creation on Node

```
Scheduler: binds Pod to Node-2 (sets pod.spec.nodeName=node-2)
  → kubelet on Node-2 watches API Server: "new Pod assigned to me!"
  → kubelet: check Pod spec
  → CRI: RunPodSandbox (pause container, network namespace)
  → CRI: PullImage (if not cached)
  → CRI: CreateContainer + StartContainer
  → Volumes: mount ConfigMap/Secret/PVC
  → Start probes (startupProbe first, then liveness/readiness)
  → readinessProbe passes → kubelet updates Pod status: Ready=True
  → Endpoints Controller: adds Pod to Service endpoints
```

---

## ⚖️ Comparison Table

|              | kubelet                                   | kube-proxy                    | Container Runtime   |
| ------------ | ----------------------------------------- | ----------------------------- | ------------------- |
| **Role**     | Pod lifecycle                             | Service networking            | Container execution |
| **Runs on**  | Every node                                | Every node                    | Every node          |
| **Talks to** | API Server, CRI, volume plugins           | API Server, kernel (iptables) | Not K8s directly    |
| **Type**     | DaemonSet (managed K8s) / systemd service | DaemonSet                     | systemd service     |

---

## ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                                 |
| ------------------------------- | --------------------------------------------------------------------------------------- |
| "kubelet = Docker"              | kubelet calls containerd via CRI; Docker is no longer supported directly                |
| "kubelet talks to etcd"         | Only API Server talks to etcd; kubelet uses API Server                                  |
| "kubelet runs on control plane" | Yes (for static pods); also on all worker nodes                                         |
| "Probes are optional"           | Optional but critical for production: without readiness, traffic goes to unhealthy Pods |

---

## 🚨 Failure Modes

| Failure              | Symptom                           | Fix                                           |
| -------------------- | --------------------------------- | --------------------------------------------- |
| kubelet crash        | Node: NotReady; Pods not starting | Restart kubelet (`systemctl restart kubelet`) |
| containerd crash     | Pods crash; kubelet errors        | Restart containerd                            |
| Image pull fails     | Pod: ImagePullBackOff             | Check imagePullSecrets, registry access       |
| Eviction loop        | Pods repeatedly evicted           | Set resource requests; add node capacity      |
| `max-pods` limit hit | New Pods stay Pending             | Increase `--max-pods` or add nodes            |

---

## 🔗 Related Keywords

- [Node](/kubernetes/node/) - where kubelet runs
- [Pod](/kubernetes/pod/) - what kubelet manages
- [Readiness vs Liveness vs Startup Probe](/kubernetes/readiness-vs-liveness-vs-startup-probe/) - probes run by kubelet
- [DaemonSet](/kubernetes/daemonset/) - kubelet manages DaemonSet Pods too
- [Kubernetes Architecture](/kubernetes/kubernetes-architecture/) - overall picture

---

## 📌 Quick Reference Card

```bash
# kubelet status (on node)
systemctl status kubelet
journalctl -u kubelet -f

# kubelet configuration
cat /var/lib/kubelet/config.yaml

# Static pod manifests
ls /etc/kubernetes/manifests/

# kubelet metrics
curl http://localhost:10248/healthz
curl http://localhost:10255/metrics   # read-only port

# Check kubelet's Pod list
curl --cert /var/lib/kubelet/pki/kubelet-client-current.pem \
     --key /var/lib/kubelet/pki/kubelet-client-current.pem \
     -k https://localhost:10250/pods
```

---

## 🧠 Think About This

Why does Kubernetes bootstrap the control plane using static pods? It's a chicken-and-egg problem: the API Server needs to be running before kubelet can get its Pod specs from it. Static pods (read from local filesystem) solve this: kubelet starts etcd and kube-apiserver as static pods before the cluster is fully running. Once API Server is up, kubeadm can register the static pod specs as regular Pod objects in etcd - giving you visibility into control plane components via `kubectl get pods -n kube-system`.
