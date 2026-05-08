---
layout: default
title: "K8s Cost Optimization"
parent: "Kubernetes"
grand_parent: "Technical Dictionary"
nav_order: 63
permalink: /kubernetes/k8s-cost-optimization/
id: K8S-063
category: "Kubernetes"
difficulty: "★★★"
depends_on:
  [
    "Resource Requests / Limits",
    "HPA (Horizontal Pod Autoscaler)",
    "VPA",
    "Node Affinity / Anti-Affinity",
  ]
used_by: ["Spot Instances / Reserved Instances", "AWS Cost Optimization"]
related:
  [
    "Resource Requests / Limits",
    "QoS Classes",
    "Kubernetes Observability",
    "HPA (Horizontal Pod Autoscaler)",
  ]
tags:
  [
    kubernetes,
    cost,
    optimization,
    spot-instances,
    vpa,
    cluster-autoscaler,
    rightsizing,
    k8s,
  ]
---

# K8s Cost Optimization

## ⚡ TL;DR

Kubernetes cost is dominated by **overprovisioned Pods** (too-high requests), **idle nodes** (Cluster Autoscaler is reactive), and **underutilized resources** (teams set high requests "just in case"). Fix with: VPA for right-sizing, Spot instances for non-critical workloads, Cluster Autoscaler to shrink node pools, Goldilocks/Kubecost for visibility, and namespace resource quotas to force teams to think about cost.

---

## 🔥 Problem This Solves

Cloud Kubernetes bills are often 40-60% higher than they need to be. Root causes: engineers set `requests: cpu: 2` for a service that uses 200m, nodes run at 15% utilization, and no one has visibility into which team/namespace is costing what. Cost optimization brings this under control without sacrificing reliability.

---

## 📘 Textbook Definition

Kubernetes cost optimization refers to techniques for reducing cloud infrastructure spend while maintaining application performance and reliability. It involves right-sizing Pod resource requests/limits, using cost-effective instance types (Spot), scaling down idle resources, and attributing costs to teams/namespaces for accountability.

---

## ⏱️ 30 Seconds

```
Cost Optimization Levers:

1. Right-size requests:   VPA recommendations or Goldilocks
2. Idle nodes:            Cluster Autoscaler (scale down empty nodes)
3. Spot instances:        60-90% cheaper; toleration for spot nodes
4. Horizontal scaling:    HPA: scale down to 0 at night (KEDA)
5. Cost visibility:       Kubecost: cost per namespace/team/deployment
6. Reserved capacity:     1yr or 3yr commitment for baseline load
7. Namespace quotas:      Force teams to own their resource usage
```

---

## 🔩 First Principles

- **Billing unit**: Node vCPU + Memory hours (regardless of Pod utilization)
- **Waste sources**: Over-requested Pods (paying for CPU/mem you don't use), over-provisioned nodes, idle replicas
- **Node utilization target**: 60-70% is healthy; <40% = wasteful; >80% = risky
- **Spot savings**: AWS Spot = up to 90% off on-demand; Fargate Spot = 70% off
- **Cost attribution**: Namespaces map to teams → cost per team without custom tooling

---

## 🧪 Thought Experiment

Engineering team is spending $15,000/month on EKS. Kubecost reveals: `ml-training` namespace = 40% of cost but runs only 2 hours/day. `api-servers` namespace = requests 4x actual usage. Action: cron-scale ml-training to 0 at night (KEDA CronScaler); VPA reduces api-servers requests by 70%; Cluster Autoscaler removes 5 idle nodes. New bill: $8,000/month. Same performance.

---

## 🧠 Mental Model / Analogy

Kubernetes cost optimization is like managing a **hotel's room occupancy**: you pay for rooms (nodes) regardless of whether guests (Pods) use the full amenities. The goal is high occupancy (node utilization) with the right room sizes (requests matching actual usage). Spot rooms (Spot instances) are available at 70% off but may be reclaimed on short notice - ideal for guests (jobs) that can check out quickly.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Set resource requests and limits on all Pods. Enable Cluster Autoscaler. Review Grafana node utilization dashboards. Delete unused namespaces.

**Level 2 - Practitioner**: VPA `recommendationOnly` mode: see right-sizing suggestions without disruption. Goldilocks: per-namespace VPA dashboard. Spot instances: dedicated node pool with `spot.kubernetes.io/interruption-handler`. KEDA: scale deployments to 0 replicas overnight.

**Level 3 - Advanced**: Kubecost: cost per namespace/label/deployment. Namespace ResourceQuota enforcement. Bin packing: set PodTopologySpreadConstraints to pack Pods on fewer nodes. Karpenter (AWS): replaces Cluster Autoscaler; provisions exact instance type needed, uses Spot/OD mix intelligently, consolidation mode terminates underutilized nodes automatically.

**Level 4 - Expert**: Karpenter NodePool: specify `karpenter.sh/capacity-type: spot,on-demand` + instance type weight by price. Disruption budget in Karpenter controls how many nodes can be replaced simultaneously. Reserved Instances + Savings Plans for baseline load; Spot for burst. FinOps: showback vs chargeback - attributing costs to business units. Multi-cluster cost comparison (same workload: GKE Autopilot vs EKS Fargate vs AKS Virtual Nodes). Vertical pod autoscaler + HPA: `containerResource` metrics source allows HPA to scale on actual CPU measured, not just requested.

---

## ⚙️ How It Works

### VPA for Right-Sizing

```yaml
# VPA in recommendation-only mode (safe to apply anytime)
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-service-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-service
  updatePolicy:
    updateMode: "Off" # Only recommendations, no auto-update


# Check recommendations:
# kubectl describe vpa my-service-vpa -n production
# Look for:
# Recommendation:
#   Container Recommendations:
#     Container Name: my-service
#       Lower Bound:  cpu: 50m, memory: 64Mi
#       Target:       cpu: 200m, memory: 256Mi
#       Upper Bound:  cpu: 500m, memory: 512Mi
```

### Spot Instance Node Pool

```yaml
# EKS: Spot node group with mixed instances
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: spot-nodepool
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values: [
              "m5.large",
              "m5.xlarge",
              "m4.large",
              "m4.xlarge",
              "m6i.large",
              "m6i.xlarge",
            ] # diversify = fewer interruptions
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s

---
# Pod tolerating Spot
spec:
  tolerations:
    - key: "kubernetes.azure.com/scalesetpriority"
      operator: "Equal"
      value: "spot"
      effect: "NoSchedule"
  nodeSelector:
    kubernetes.azure.com/scalesetpriority: spot
```

### KEDA Scale-to-Zero (Batch Jobs at Night)

```yaml
# Scale deployment to 0 outside business hours
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: ml-training-scaler
spec:
  scaleTargetRef:
    name: ml-training
  minReplicaCount: 0 # can scale to zero
  maxReplicaCount: 10
  triggers:
    - type: cron
      metadata:
        timezone: America/New_York
        start: "0 8 * * MON-FRI" # scale up at 8am weekdays
        end: "0 18 * * MON-FRI" # scale down at 6pm weekdays
        desiredReplicas: "5"
```

### Kubecost Cost Attribution

```yaml
# Add cost labels to Pods for attribution
metadata:
  labels:
    cost-team: "payments"
    cost-product: "checkout"
    cost-environment: "production"

# Kubecost aggregates by these labels
# Dashboard shows: cost per team, per product, per environment
```

### Cluster Autoscaler Tuning

```yaml
# CA aggressive scale-down (for dev clusters)
--scale-down-enabled=true
--scale-down-utilization-threshold=0.5
--scale-down-unneeded-time=2m    # default 10m → faster scale-down in dev
--scale-down-delay-after-add=2m  # default 10m

# CA conservative (for prod)
--scale-down-utilization-threshold=0.5
--scale-down-unneeded-time=10m
--skip-nodes-with-local-storage=true  # don't evict nodes with PVCs
```

### ResourceQuota Per Namespace

```yaml
# Force teams to be resource-conscious
apiVersion: v1
kind: ResourceQuota
metadata:
  name: payments-team-quota
  namespace: payments
spec:
  hard:
    requests.cpu: "20" # Total requests in namespace
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    count/pods: "50"
    count/services: "20"
    persistentvolumeclaims: "10"
```

---

## 🔄 E2E Flow: Monthly Cost Review

```
1. Kubecost report: top 10 highest-cost namespaces
   → ml-experiments: $3,200/mo (idle 70% of time)
   → api-gateway: $2,100/mo (over-requested by 3x)

2. ml-experiments fix:
   → Create KEDA CronScaler (scale to 0 nights/weekends)
   → Move batch jobs to Spot nodes
   → Estimated savings: $2,400/mo

3. api-gateway fix:
   → VPA recommendations: reduce cpu request from 1000m to 300m
   → Apply new requests → Cluster Autoscaler removes 3 nodes
   → Estimated savings: $1,200/mo

4. Reserve baseline:
   → 10 on-demand nodes run 24/7 → buy 1yr Reserved Instances
   → Savings vs on-demand: 40% → $1,800/mo

Total monthly savings: $5,400/mo (36% reduction)
```

---

## ⚖️ Comparison Table

| Tool                   | Purpose                                 | Ease           |
| ---------------------- | --------------------------------------- | -------------- |
| **VPA**                | Right-size requests/limits              | Medium         |
| **Goldilocks**         | VPA recommendation dashboard            | Easy           |
| **Karpenter**          | Smart node provisioning + consolidation | Medium         |
| **Cluster Autoscaler** | Scale nodes up/down                     | Easy           |
| **KEDA**               | Event-driven + scale-to-zero            | Medium         |
| **Kubecost**           | Cost visibility + attribution           | Easy (install) |
| **Spot Instances**     | 60-90% node cost reduction              | Medium         |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------ |
| "Requests are just hints"           | Requests determine which node a Pod lands on and what you're billed for        |
| "More nodes = more cost always"     | 10 small nodes vs 5 large: may be same cost; right-sizing matters more         |
| "Spot is unreliable for production" | With proper PDB + multiple instance types + AZs: Spot interruption rate is <5% |
| "HPA scales efficiently"            | HPA scales replicas but doesn't remove nodes without Cluster Autoscaler        |

---

## 🚨 Failure Modes

| Failure                                | Symptom                                    | Fix                                                         |
| -------------------------------------- | ------------------------------------------ | ----------------------------------------------------------- |
| VPA UpdateMode:Auto + HPA both active  | Conflict: VPA resizes, HPA re-scales       | Use `containerResource` HPA or keep VPA recommendation-only |
| Karpenter consolidation too aggressive | Workloads disrupted by node replacement    | Set `disruption.budgets` in NodePool                        |
| Scale-to-zero breaks on startup        | KEDA scales up but app takes 5min to start | Pre-warm patterns, higher minReadySeconds                   |
| ResourceQuota blocks deployment        | New deployment exceeds quota               | Increase quota or reduce requests                           |

---

## 🔗 Related Keywords

- [Resource Requests / Limits](/kubernetes/resource-requests-limits/) - the foundation of cost management
- [QoS Classes](/kubernetes/qos-classes/) - right-sizing affects QoS class
- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) - horizontal scaling for cost efficiency
- [Kubernetes Observability](/kubernetes/kubernetes-observability/) - metrics drive right-sizing decisions

---

## 📌 Quick Reference Card

```bash
# Check VPA recommendations
kubectl describe vpa <name> -n <namespace>

# Node utilization
kubectl top nodes

# Pod utilization vs requests
kubectl top pods -n <namespace> --containers

# Kubecost (after install)
kubectl port-forward svc/kubecost-cost-analyzer 9090 -n kubecost

# Find Pods without resource requests (risky!)
kubectl get pods -A -o json | jq '.items[] |
  select(.spec.containers[].resources.requests == null) |
  .metadata.name'

# Cluster Autoscaler status
kubectl describe configmap cluster-autoscaler-status -n kube-system

# Karpenter node utilization
kubectl get nodes -L karpenter.sh/capacity-type
```

---

## 🧠 Think About This

The highest-ROI Kubernetes cost action is almost always **fixing resource requests**. Engineers set requests based on worst-case load, peak of peak, with generous safety margins - resulting in cluster utilization of 15-25% while paying for 100%. The process: run VPA in recommendation-only mode for 2 weeks to gather real usage data; then apply P95 usage as requests with 30% safety margin. This alone typically reduces node count by 40-60% without any reliability impact. The cultural challenge: teams are afraid to reduce requests because "what if there's a spike?" - the answer is HPA, which adds replicas on CPU/memory pressure. Teach teams: HPA covers horizontal scaling; requests are not your safety net.
