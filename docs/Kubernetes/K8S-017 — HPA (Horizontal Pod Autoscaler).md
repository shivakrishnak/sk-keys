---
layout: default
title: "HPA (Horizontal Pod Autoscaler)"
parent: "Kubernetes"
nav_order: 17
permalink: /kubernetes/hpa-horizontal-pod-autoscaler/
number: "K8S-017"
category: "Kubernetes"
difficulty: "★★☆"
depends_on: ["Deployment", "ReplicaSet", "Pod", "Resource Requests / Limits"]
used_by: ["KEDA", "Cluster Autoscaler"]
related:
  [
    "VPA (Vertical Pod Autoscaler)",
    "Cluster Autoscaler",
    "KEDA",
    "Resource Requests / Limits",
    "Deployment",
  ]
tags: [kubernetes, hpa, autoscaling, horizontal-scaling, metrics, k8s]
---

# HPA (Horizontal Pod Autoscaler)

## ⚡ TL;DR

HPA automatically **scales the number of Pod replicas** based on observed metrics (CPU, memory, or custom). It watches metrics and adjusts `Deployment.spec.replicas`. Requires **Metrics Server** (for CPU/memory) or custom metrics adapter (for request rate, queue depth, etc.).

---

## 🔥 Problem This Solves

Traffic is not constant — peaks at lunch, valleys at 3am. Manual replica counts waste resources or under-provision during spikes. HPA automatically scales out during high load and scales in during low load.

---

## 📘 Textbook Definition

The HorizontalPodAutoscaler automatically scales the number of Pod replicas in a workload resource (Deployment, ReplicaSet, StatefulSet) based on observed CPU utilization, memory utilization, or custom metrics.

---

## ⏱️ 30 Seconds

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70 # target 70% CPU
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 🔩 First Principles

- HPA computes: `desiredReplicas = ceil(currentReplicas × (currentMetric / targetMetric))`
- **Resource requests must be set** for CPU/memory HPA to work (HPA calculates % of request)
- Metrics Server is required for CPU/memory metrics (not pre-installed)
- Scale-out: fast (default 15s evaluation, 3 minute stabilization)
- Scale-in: slow (default 5-minute stabilization window) — prevents thrashing

---

## 🧪 Thought Experiment

You have 3 replicas using 210% CPU (70% target × 3 = 210% total allowed). Load spikes to 420%. HPA: `ceil(3 × 420/210) = ceil(6) = 6 replicas`. After load drops to 60%: `ceil(6 × 60/70) = ceil(5.1) = 6` (within 10% tolerance = no scale). Eventually drops below tolerance → scales down, but waits 5 min to confirm.

---

## 🧠 Mental Model / Analogy

HPA is like a **restaurant manager** who watches how busy the kitchen is (CPU %). When orders pile up, they call in more cooks (scale out). When it's slow, they send cooks home (scale in) — but not immediately, they wait a few minutes to ensure it's not just a brief lull.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: HPA adds or removes Pods based on how busy they are (CPU usage).

**Level 2 — Practitioner**: Set `minReplicas` and `maxReplicas`. Resource requests MUST be defined. Install Metrics Server. Monitor with `kubectl get hpa`.

**Level 3 — Advanced**: Multiple metrics supported (CPU + memory + custom). Scale-up and scale-down stabilization windows configurable. `scaleDown.stabilizationWindowSeconds` (default 300s). `scaleUp.stabilizationWindowSeconds` (default 0s).

**Level 4 — Expert**: Custom metrics via Prometheus Adapter (HPA v2 External/Object metrics). KEDA extends HPA with 50+ event sources (Kafka lag, SQS queue depth, cron schedules). Behavior API (autoscaling/v2) controls scale-up/down policies: `periodSeconds`, `value`, `type: Pods|Percent`.

---

## ⚙️ How It Works

### HPA Control Loop

```
Every 15 seconds (default):
  1. Fetch current metrics from Metrics Server
  2. Calculate desired replicas:
     desiredReplicas = ceil(current × (currentMetric / target))
  3. Apply stabilization window (prevent thrashing)
  4. Clamp to [minReplicas, maxReplicas]
  5. Update Deployment.spec.replicas if different
```

### Advanced Behavior Policy

```yaml
spec:
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 4 # max 4 Pods added per period
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10 # max 10% removed per period
          periodSeconds: 60
```

### Custom Metrics (Prometheus Adapter)

```yaml
metrics:
  - type: External
    external:
      metric:
        name: http_requests_per_second
        selector:
          matchLabels:
            service: my-app
      target:
        type: AverageValue
        averageValue: "100" # 100 RPS per Pod
```

---

## 🔄 E2E Flow: CPU Spike

```
Normal: 3 replicas, 30% CPU average
Traffic spike: 3 replicas, 120% CPU average
  → HPA: desired = ceil(3 × 120/70) = ceil(5.14) = 6
  → Updates Deployment replicas=6
  → Scheduler places 3 new Pods
  → Load distributes: ~60% CPU per Pod
  → Stabilization: 15s later, still high → hold

Traffic drops: 6 replicas, 20% CPU
  → HPA: desired = ceil(6 × 20/70) = ceil(1.7) = 2
  → Within 10% threshold? No → wants to scale down
  → Wait stabilizationWindowSeconds=300
  → Still low → scale to max(minReplicas=2, 2) = 2
```

---

## ⚖️ Comparison Table

|                       | HPA            | VPA            | Cluster Autoscaler | KEDA                         |
| --------------------- | -------------- | -------------- | ------------------ | ---------------------------- |
| **What scales**       | Pod replicas   | Pod CPU/memory | Node count         | Pod replicas (event-driven)  |
| **Metric**            | CPU/mem/custom | CPU/mem        | Pending Pods       | Kafka, SQS, cron, HTTP, etc. |
| **Use case**          | Stateless apps | Right-sizing   | Node capacity      | Event-driven workloads       |
| **Conflict with VPA** | Use separately | Use separately | Complementary      | Replaces HPA                 |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                               |
| ------------------------------------- | ------------------------------------------------------------------------------------- |
| "HPA works without resource requests" | CPU/memory HPA requires resource requests to calculate % utilization                  |
| "HPA reacts instantly"                | 15s scrape + stabilization window = minutes to scale                                  |
| "HPA + VPA can be used together"      | VPA and HPA conflict on CPU/memory; use VPA for memory, HPA for CPU, or KEDA for both |
| "HPA scales to 0"                     | HPA minimum is 1 replica; KEDA can scale to 0                                         |

---

## 🚨 Failure Modes

| Failure                      | Symptom                               | Fix                                         |
| ---------------------------- | ------------------------------------- | ------------------------------------------- |
| Metrics Server not installed | HPA shows `<unknown>` metrics         | Install metrics-server                      |
| Missing resource requests    | HPA: `unable to get metrics`          | Add CPU/memory requests to Pod spec         |
| Scale ceiling hit            | `maxReplicas` reached, still high CPU | Increase maxReplicas; optimize app          |
| Thrashing                    | Replicas oscillate up/down            | Tune stabilization windows; adjust target % |

---

## 🔗 Related Keywords

- [VPA (Vertical Pod Autoscaler)](/kubernetes/vpa-vertical-pod-autoscaler/) — size individual Pods
- [Cluster Autoscaler](/kubernetes/cluster-autoscaler/) — add/remove nodes
- [KEDA](/kubernetes/keda/) — event-driven autoscaling
- [Resource Requests / Limits](/kubernetes/resource-requests-limits/) — required for HPA
- [Deployment](/kubernetes/deployment/) — HPA target

---

## 📌 Quick Reference Card

```bash
# Create HPA
kubectl autoscale deployment my-app --cpu-percent=70 --min=2 --max=20

# Check HPA status
kubectl get hpa
kubectl describe hpa my-app-hpa

# Watch HPA in real time
kubectl get hpa -w

# Install Metrics Server (required for CPU/mem)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View current resource usage
kubectl top pods
kubectl top nodes
```

---

## 🧠 Think About This

Why is scale-in deliberately slow (5-minute default)? Consider a batch spike: CPU hits 90% for 2 minutes, then drops to 10%. If scale-in was instant, you'd spin up 10 Pods, then immediately kill 8 of them — wasting startup time and connections. The stabilization window absorbs short fluctuations. For apps with expensive startup (JVM warm-up), set even longer scale-down windows to avoid repeated cold starts.
