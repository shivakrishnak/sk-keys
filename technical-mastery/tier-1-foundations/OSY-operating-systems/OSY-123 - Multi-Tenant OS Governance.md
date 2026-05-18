---
id: OSY-123
title: Multi-Tenant OS Governance
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-105, OSY-118, OSY-122
used_by: []
related: OSY-118, OSY-122, OSY-124
tags:
  - multi-tenant
  - governance
  - isolation
  - resource
  - security
  - policy
  - platform
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 123
permalink: /technical-mastery/osy/multi-tenant-os-governance/
---

## TL;DR

Multi-tenant OS governance: enforcing resource fairness,
security isolation, and operational accountability when
multiple teams or customers share the same OS/cluster.
Key policies: cgroup hierarchies (resource limits per
tenant), RBAC for system access, audit logging per
tenant, cost allocation, and noisy neighbor prevention.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-123 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | multi-tenant, governance, cgroups, RBAC, noisy neighbor, resource fairness |
| **Prerequisites** | OSY-105, OSY-118, OSY-122 |

---

### Multi-Tenant Failure Modes

```
Without governance: shared OS = uncontrolled competition

Failure mode 1: Noisy Neighbor CPU
  Team A's service: CPU-bound spike (bad query, batch job)
  Result: consumes all 8 CPUs
  Team B's service: starved; request latency 10x
  
  Diagnosis:
    top: Team A's PID consuming 800% CPU
    Team B: CPU utilization 0% (waiting in run queue)
    
  Prevention: CPU cgroup limits per tenant
    Team A cgroup: max 400% CPU (4 cores)
    Team B cgroup: min 400% CPU guaranteed
    Ensures: Team A spike cannot take Team B's allocation

Failure mode 2: Memory Exhaustion Cascade
  Team A's service: memory leak
  RSS grows to consume all host RAM
  OOM killer: starts killing OTHER tenants' processes
  Team B: OOM killed without warning; unrelated to their code
  
  Prevention: cgroup memory limits
    Team A: memory.limit_in_bytes = 4GB (hard limit)
    OOM kill: only Team A's processes
    Team B: protected by their own cgroup

Failure mode 3: Disk I/O Starvation
  Team A: bulk data export job (sequential reads, 500MB/s)
  Team B: real-time API (random 4KB reads, latency-sensitive)
  Team A saturates disk; Team B's p99 latency spikes
  
  Prevention: cgroup blkio limits
    Team A: blkio.throttle.read_bps_device = 100MB/s
    Team B: protected bandwidth

Failure mode 4: File Descriptor Exhaustion
  Team A: connection leak (never closes sockets)
  /proc/sys/fs/file-max reached on host
  All processes: cannot open new file descriptors
  Multiple tenants: failures
  
  Prevention: ulimit per process (RLIMIT_NOFILE)
    Each container: nofile = 65536
    One tenant leak: cannot exceed their fd limit
```

---

### cgroup Hierarchy Design

```
cgroups v2 (unified hierarchy):

  /sys/fs/cgroup/
  ├── prod/              (production workloads)
  │     ├── team-a/      (Team A's production)
  │     │     ├── service-api/     (API service)
  │     │     └── service-worker/  (Background workers)
  │     └── team-b/      (Team B's production)
  │           └── service-api/
  └── staging/           (staging workloads; lower priority)
        └── team-a/
        └── team-b/
        
Resource allocation (cgroup v2 parameters):

  # CPU: proportional shares (not hard limit unless needed)
  echo "200" > /sys/fs/cgroup/prod/team-a/cpu.weight
  echo "200" > /sys/fs/cgroup/prod/team-b/cpu.weight
  # Equal weight: each gets ~50% when competing
  
  # CPU: hard limit (max N CPUs)
  echo "400000 1000000" > \
    /sys/fs/cgroup/prod/team-a/cpu.max
  # Format: quota period = 400ms/1000ms = 40% CPU max
  
  # Memory: hard limit
  echo "4294967296" > \
    /sys/fs/cgroup/prod/team-a/memory.max
  # 4GB hard limit; exceeding -> OOM in that cgroup
  
  # Memory: OOM group kill (kill entire container on OOM)
  echo "1" > \
    /sys/fs/cgroup/prod/team-a/service-api/memory.oom.group
  
  # I/O: throttle by device
  DEVNO=$(ls -l /dev/nvme0n1 | awk '{print $5$6}' | tr ',' ':')
  echo "$DEVNO rbps=104857600" > \
    /sys/fs/cgroup/prod/team-a/io.max
  # 100MB/s read limit

Kubernetes resource quotas (cluster-level governance):
  
  # ResourceQuota per namespace (Kubernetes tenant boundary):
  apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: team-a-quota
    namespace: team-a
  spec:
    hard:
      requests.cpu: "8"        # total CPU request
      requests.memory: 16Gi   # total memory request
      limits.cpu: "16"        # total CPU limit
      limits.memory: 32Gi     # total memory limit
      pods: "50"              # max pods
      services: "20"          # max Services
      
  # LimitRange: default limits per pod (prevent quota bypass):
  apiVersion: v1
  kind: LimitRange
  metadata:
    name: default-limits
    namespace: team-a
  spec:
    limits:
    - default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      type: Container
```

---

### Security Governance

```
Access Control:
  Multi-tenant principle: each tenant manages their namespace
  Platform team manages: cluster, infrastructure, quotas
  
  Kubernetes RBAC:
    Team A: admin role in namespace "team-a"
    Team A: cannot access namespace "team-b"
    Team A: cannot modify ClusterRole, PodSecurityPolicy
    
  OS-level:
    Each container runs as different UID (user namespaces)
    Team A's UID range: 100000-101000
    Team B's UID range: 101001-102000
    File access: Team A's files owned by 100000+; Team B cannot read
    
Audit and Accountability:
  Every tenant action logged with tenant identity
  Kubernetes: API server audit log with user/namespace
  OS: auditd rules scoped to cgroup path
  
  Correlation:
    Alert: "Container X in namespace team-a consumed 10GB disk"
    Trace: kubectl events -n team-a | grep disk
    Bill: S3 storage cost attributed to team-a

Network Isolation:
  Kubernetes NetworkPolicy: whitelist-only between namespaces
  Default: deny all cross-namespace traffic
  Allow: only explicitly listed services
  
  # NetworkPolicy: Team A's API can only receive from team-a namespace
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: team-a-isolation
    namespace: team-a
  spec:
    podSelector: {}  # applies to all pods in namespace
    policyTypes:
    - Ingress
    - Egress
    ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: team-a
    egress:
    - to:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: team-a
    - to:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: kube-system
      ports:
      - protocol: UDP
        port: 53  # DNS
```

---

### Cost Attribution

```
Goal: charge back OS resource consumption to tenants

Metrics to collect per namespace:
  CPU: sum(rate(container_cpu_usage_seconds_total{namespace="team-a"}[1h]))
  Memory: sum(container_memory_working_set_bytes{namespace="team-a"})
  Network: sum(rate(container_network_transmit_bytes_total{namespace="team-a"}[1h]))
  Storage: sum(kubelet_volume_stats_used_bytes{namespace="team-a"})
  
Cost calculation:
  CPU price: $0.048/vCPU-hour
  Memory: $0.006/GB-hour
  
  Team A hourly cost:
    CPU: 2.3 vCPUs * $0.048 = $0.11/hour
    Memory: 8.2 GB * $0.006 = $0.049/hour
    Total: $0.159/hour
    
Tools:
  Kubecost: Kubernetes cost allocation (open source + paid)
  OpenCost: CNCF project for cost attribution
  Custom Grafana dashboards from Prometheus metrics
```

---

### Governance Runbook

```
When a noisy neighbor is detected:

1. Identify the tenant:
   kubectl top pods -A --sort-by=cpu | head -20
   # Shows: namespace, pod, CPU, memory
   
2. Verify cgroup limits exist:
   cat /sys/fs/cgroup/kubepods/burstable/pod$POD_UID/cpu.max
   
3. If no limits: enforce immediately
   kubectl -n team-a set resources deployment/my-service \
     --limits=cpu=2000m,memory=2Gi \
     --requests=cpu=500m,memory=512Mi
   
4. If limits exist but resource exhaustion:
   Check: is this legitimate burst or runaway process?
   
5. For runaway: notify team, scale down if not responsive:
   kubectl -n team-a scale deployment/my-service --replicas=1
   
6. Document: incident ticket, cost attribution
7. Post-incident: update LimitRange defaults to prevent recurrence
```

---

### Quick Reference

| Control | Mechanism | Scope |
|---------|-----------|-------|
| CPU isolation | cgroup cpu.weight / cpu.max | Per container |
| Memory protection | cgroup memory.max | Per container |
| I/O fairness | cgroup io.max | Per container per device |
| Network isolation | Kubernetes NetworkPolicy | Per namespace |
| Access control | Kubernetes RBAC | Per namespace |
| File isolation | User namespaces (UID ranges) | Per container |
| Audit logging | auditd + Kubernetes audit | Per action |
| Cost attribution | Kubecost / OpenCost | Per namespace |
