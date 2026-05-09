---
version: 1
layout: default
title: "KEDA"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /kubernetes/keda/
id: K8S-025
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["HPA (Horizontal Pod Autoscaler)", "Deployment", "Job / CronJob"]
used_by: ["Cluster Autoscaler", "K8s Cost Optimization"]
related:
  [
    "HPA (Horizontal Pod Autoscaler)",
    "Cluster Autoscaler",
    "VPA (Vertical Pod Autoscaler)",
    "Job / CronJob",
    "Kafka",
  ]
tags:
  [kubernetes, keda, event-driven-scaling, kafka-scaling, scale-to-zero, k8s]
---

# KEDA

## ⚡ TL;DR

KEDA (Kubernetes Event-Driven Autoscaling) extends HPA to scale based on **external event sources** - Kafka consumer lag, SQS queue depth, HTTP request rate, Prometheus metrics, cron schedules, and 50+ more. Critically: KEDA can **scale to 0** (HPA cannot).

---

## 🔥 Problem This Solves

HPA only scales on CPU/memory or basic custom metrics. Event-driven workloads need to scale based on queue depth, Kafka lag, or scheduled times - not CPU. KEDA provides these event source integrations with scale-to-zero support for cost efficiency.

---

## 📘 Textbook Definition

KEDA is a Kubernetes-based Event Driven Autoscaler. It allows Kubernetes workloads to scale based on the number of events needing to be processed. KEDA acts as a Kubernetes Metrics Adapter, providing HPA-compatible metrics from external event sources.

---

## ⏱️ 30 Seconds

```yaml
# Scale consumer based on Kafka lag
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-consumer-scaler
spec:
  scaleTargetRef:
    name: kafka-consumer
  pollingInterval: 15
  cooldownPeriod: 300
  minReplicaCount: 0 # scale to ZERO
  maxReplicaCount: 30
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka:9092
        consumerGroup: my-group
        topic: orders
        lagThreshold: "100" # 100 messages per replica
```

---

## 🔩 First Principles

- KEDA installs a **ScaledObject** CRD and a metrics adapter
- ScaledObject creates/manages an HPA object automatically
- KEDA polls external sources (Kafka, SQS, Redis, etc.) and feeds metrics to HPA
- `minReplicaCount: 0` → KEDA (not HPA) manages the 0→1 transition (HPA min is 1)
- `cooldownPeriod`: how long to wait before scaling to 0 after queue empties

---

## 🧪 Thought Experiment

You have a batch processor consuming Kafka. At 2am there are zero messages - you want 0 replicas (zero cost). At 9am, 10,000 messages queue up - you need 100 replicas fast. KEDA: at 2am → scales to 0. At 9am → detects lag=10,000, triggers 0→1 immediately, then HPA scales to 100. Cost drops to zero during off-hours.

---

## 🧠 Mental Model / Analogy

KEDA is like a **factory floor manager** who watches the assembly line queue (Kafka lag). No parts to assemble? Send workers home (scale to 0). Queue piling up? Call in more workers (scale out). The manager watches the queue directly, not just worker busyness.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: KEDA scales your app based on how full a queue is (not just CPU). Can scale to zero when idle.

**Level 2 - Practitioner**: Install KEDA via Helm. Create `ScaledObject` with triggers. KEDA auto-creates and manages the underlying HPA. `pollingInterval` = how often to check the event source.

**Level 3 - Advanced**: `ScaledJob` scales Kubernetes Jobs for batch processing (each job handles N messages). Authentication via `TriggerAuthentication` (references Secrets for credentials). `ScaledObject` can have multiple triggers (scale based on whichever is highest).

**Level 4 - Expert**: KEDA metrics adapter implements the `external.metrics.k8s.io` API. At `minReplicaCount: 0`, KEDA activates the deployment (0→1) before HPA takes over. `activation` threshold separate from `lagThreshold` - activate at lag>0, scale at lag per `lagThreshold`. Fallback: if scaler fails to connect, KEDA uses fallback replicas.

---

## ⚙️ How It Works

### KEDA Architecture

```
External Source (Kafka, SQS, Redis...)
  → KEDA Operator polls metrics
  → Feeds to Custom Metrics Server
  → HPA reads metrics from Custom Metrics Server
  → HPA adjusts Deployment replicas

Scale to Zero (KEDA-managed):
  Replicas=1 → lag=0 for cooldownPeriod → KEDA sets replicas=0
  lag>activationThreshold → KEDA sets replicas=1 → HPA takes over
```

### Popular Triggers (50+ available)

| Trigger             | Scale Based On                               |
| ------------------- | -------------------------------------------- |
| `kafka`             | Consumer group lag                           |
| `aws-sqs-queue`     | Queue message count                          |
| `redis-lists`       | List length                                  |
| `prometheus`        | Any PromQL metric                            |
| `cron`              | Schedule (min/max replicas per time window)  |
| `http`              | Pending HTTP requests (requires http-add-on) |
| `azure-service-bus` | Queue/topic message count                    |
| `rabbitmq`          | Queue depth                                  |

### ScaledJob (Batch Processing)

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledJob
metadata:
  name: batch-processor
spec:
  jobTargetRef:
    template:
      spec:
        containers:
          - name: processor
            image: batch-proc:1.0
        restartPolicy: OnFailure
  triggers:
    - type: kafka
      metadata:
        topic: batch-jobs
        lagThreshold: "1" # 1 Job per message
  maxReplicaCount: 50
  scalingStrategy:
    strategy: accurate # or default
```

---

## 🔄 E2E Flow: Kafka-Driven Scale

```
Off-hours: Kafka lag = 0
  → KEDA: replicas already = 0, no action
  → Zero Pods running, zero cost for this service

9:00 AM: lag = 500 messages
  → KEDA activation: lag > 0 → set replicas = 1
  → HPA takes over: 500/100 = 5 replicas
  → CA: if nodes full, adds nodes
  → 5 consumer Pods processing messages

10:00 AM: lag = 0, cooldownPeriod=300s passes
  → KEDA: scale replicas = 0
  → Nodes potentially removed by CA
```

---

## ⚖️ Comparison Table

|                        | KEDA      | HPA                        | Manual Scaling     |
| ---------------------- | --------- | -------------------------- | ------------------ |
| **Scale-to-zero**      | ✅        | ❌ (min 1)                 | ✅ (manual effort) |
| **Kafka lag**          | ✅ Native | ❌ (custom metrics needed) | ❌                 |
| **Cron schedule**      | ✅        | ❌                         | ❌                 |
| **Event source count** | 50+       | CPU/mem + custom           | N/A                |
| **Complexity**         | Medium    | Low                        | None               |

---

## ⚠️ Common Misconceptions

| Misconception            | Reality                                                              |
| ------------------------ | -------------------------------------------------------------------- |
| "KEDA replaces HPA"      | KEDA creates and manages an HPA; they coexist                        |
| "KEDA works instantly"   | `pollingInterval` (default 30s) adds latency to scaling decisions    |
| "Scale-to-zero = free"   | 0→1 cold start may drop messages/requests; use `activationThreshold` |
| "KEDA is only for Kafka" | 50+ scalers: HTTP, Redis, Prometheus, cron, cloud queues, etc.       |

---

## 🚨 Failure Modes

| Failure             | Symptom                          | Fix                                                 |
| ------------------- | -------------------------------- | --------------------------------------------------- |
| Scaler auth failure | Replicas stuck at fallback count | Check TriggerAuthentication credentials             |
| Cold start latency  | First messages processed slowly  | Use `activationThreshold` or keep min 1 replica     |
| HPA conflict        | Replicas fighting KEDA           | Don't create HPA manually; KEDA manages it          |
| Wrong lag threshold | Over/under scaling               | Monitor and tune `lagThreshold` per partition count |

---

## 🔗 Related Keywords

- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) - KEDA extends HPA
- [Cluster Autoscaler](/kubernetes/cluster-autoscaler/) - scales nodes as KEDA scales Pods
- [Job / CronJob](/kubernetes/job-cronjob/) - ScaledJob for batch
- [Kafka](/big-data-streaming/apache-kafka/) - most common KEDA trigger
- [K8s Cost Optimization](/kubernetes/k8s-cost-optimization/) - scale-to-zero saves cost

---

## 📌 Quick Reference Card

```bash
# Install KEDA (Helm)
helm repo add kedacore https://kedacore.github.io/charts
helm install keda kedacore/keda -n keda --create-namespace

# Check KEDA operator
kubectl get pods -n keda

# Check ScaledObjects
kubectl get scaledobjects
kubectl describe scaledobject kafka-consumer-scaler

# Check current metric value
kubectl get --raw "/apis/external.metrics.k8s.io/v1beta1" | jq

# TriggerAuthentication for Kafka credentials
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: kafka-trigger-auth
spec:
  secretTargetRef:
  - parameter: sasl
    name: kafka-secret
    key: sasl
```

---

## 🧠 Think About This

Scale-to-zero sounds perfect for cost savings but has a hidden challenge: the first consumer Pod needs ~30-60 seconds to start (image pull, JVM startup, Kafka partition rebalance). During this cold start, messages queue up. For SLA-sensitive workloads, keep `minReplicaCount: 1` during business hours (use cron trigger) and scale to 0 only at night. KEDA's cron trigger enables exactly this pattern: `{ desiredReplicas: 1, start: "0 8 * * 1-5", end: "0 20 * * 1-5" }`.
