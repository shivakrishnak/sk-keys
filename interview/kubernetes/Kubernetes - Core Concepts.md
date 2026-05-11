---
title: "Kubernetes - Core Concepts"
topic: Kubernetes
subtopic: Core Concepts
keywords:
  - Kubernetes Architecture
  - Control Plane
  - etcd
  - kubelet
  - kube-proxy
  - API Server
difficulty_range: medium-hard
status: complete
version: 1
---

# Kubernetes Architecture

**TL;DR** - Kubernetes is a distributed system with a control plane (brain) that manages worker nodes (muscle), using a declarative desired-state model with continuous reconciliation to orchestrate containers at scale.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
You have 200 containers across 50 servers. One server dies - 20 containers vanish. Traffic spikes - nobody adds capacity. A deploy fails - rollback is manual and terrifying.

**THE INVENTION MOMENT:**
"This is exactly why Kubernetes was created."

**EVOLUTION:**
Manual ops + scripts -> Google Borg (internal, 2003) -> Mesos/Marathon (2013) -> Docker Swarm (2014) -> Kubernetes open-sourced (2014) -> CNCF graduation (2018) -> Managed K8s dominates (EKS, GKE, AKS) -> K8s becomes "the operating system of the cloud."

---

### Textbook Definition

Kubernetes is a portable, extensible platform for managing containerized workloads and services that facilitates both declarative configuration and automation. Its architecture consists of a control plane (API server, scheduler, controller manager, etcd) and worker nodes (kubelet, kube-proxy, container runtime), communicating via the API server as the single source of truth.

---

### Understand It in 30 Seconds

**One line:**
Kubernetes is an autopilot for containers - you declare what you want, it makes it happen and keeps it that way.

**One analogy:**

> Kubernetes is like an airline operations center. You file a flight plan (desired state: "3 replicas of service X"). The operations center (control plane) assigns gates (scheduler), monitors flights (controller manager), tracks all data (etcd), and if a plane has issues (pod crashes), it automatically reassigns to a working aircraft.

**One insight:**
The fundamental paradigm is "desired state reconciliation." You never say "start a container." You say "ensure 3 replicas exist." The system continuously compares desired vs actual state and takes corrective action. This is what makes it self-healing.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Single source of truth: etcd stores all cluster state
2. Desired state model: you declare WHAT, controllers figure out HOW
3. Reconciliation loops: controllers continuously drive actual toward desired
4. API-centric: everything goes through the API server (single front door)

**DERIVED DESIGN:**
Because state is centralized (etcd), any component can fail and recover by re-reading state. Because controllers reconcile continuously, failures are self-healing. Because everything is API-driven, automation is native.

**THE TRADE-OFFS:**
**Gain:** Self-healing, auto-scaling, rolling updates, service discovery, declarative management
**Cost:** Complexity (networking, storage, RBAC), operational overhead, learning curve, resource overhead (~1GB for control plane)

---

### Mental Model / Analogy

> K8s is like a thermostat. You set the desired temperature (desired state). The thermostat (controller) continuously measures actual temperature and turns heating/cooling on/off to maintain the target. You don't say "turn on the heater for 10 minutes" - you say "maintain 72F."

Where this analogy breaks down: K8s has dozens of controllers (thermostats) for different resources, not just one.

---

### How It Works

```
Kubernetes Architecture:

+------------------------------------------+
|            CONTROL PLANE                  |
| +------+  +--------+  +-------+         |
| | API  |  |Scheduler|  |Controller|      |
| |Server|  |        |  | Manager |        |
| +--+---+  +---+----+  +---+-----+       |
|    |           |            |            |
|    +--------+--+------------+            |
|             |                            |
|         +---+---+                        |
|         | etcd  |                        |
|         +-------+                        |
+------------------------------------------+
          |
     +----+----+----+
     |    |    |    |
+----+--+ +--+---+ +--+---+
| Node 1| | Node 2| | Node 3|
|kubelet| |kubelet| |kubelet|
|kproxy | |kproxy | |kproxy |
| Pods  | | Pods  | | Pods  |
+-------+ +-------+ +-------+
```

**Component roles:**

- **API Server**: Front door. All communication goes through it. RESTful, authenticated, authorized.
- **etcd**: Distributed key-value store. Only component that stores state. RAFT consensus.
- **Scheduler**: Watches unscheduled pods, assigns them to nodes based on resources/constraints.
- **Controller Manager**: Runs reconciliation loops (Deployment controller, ReplicaSet controller, etc.)
- **kubelet**: Agent on each node. Ensures containers described in PodSpecs are running.
- **kube-proxy**: Manages network rules for Service access (iptables/IPVS).

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
User applies Deployment YAML -> API server validates, stores in etcd -> Deployment controller creates ReplicaSet -> ReplicaSet controller creates Pods -> Scheduler assigns Pods to nodes <- YOU ARE HERE -> kubelet on assigned node starts containers via CRI

**FAILURE PATH:**
Node dies -> controller detects pods missing (heartbeat timeout: 40s) -> creates replacement pods -> scheduler places on healthy nodes -> kubelet starts containers -> service endpoints update -> traffic reroutes (total: ~1-2 min)

---

### Quick Recall

**If you remember only 3 things:**

1. Desired state + continuous reconciliation = self-healing (you declare WHAT, K8s ensures HOW)
2. etcd is the brain (single source of truth), API server is the front door (all comms go through it)
3. Controllers are the workers - each one watches specific resources and drives actual state toward desired

**Interview one-liner:**
"Kubernetes architecture separates the control plane (API server as front door, etcd as persistent state, scheduler for placement, controllers for reconciliation) from worker nodes (kubelet running pods, kube-proxy for networking) - all driven by the desired-state model where you declare intent and controllers continuously reconcile reality."

---

### The Surprising Truth

Kubernetes doesn't actually restart crashed containers - kubelet does. And kubelet doesn't watch for crashes - it's the container runtime (containerd) that detects PID 1 exit. The reconciliation chain is: container exits -> containerd notifies kubelet -> kubelet applies restart policy -> containerd starts new container. Three different systems coordinate, each with their own failure modes.

---

### Interview Deep-Dive

**Q1: Walk me through what happens from `kubectl apply -f deployment.yaml` to a running pod.**

_Why they ask:_ Tests end-to-end understanding of K8s control flow.

**Answer:**

1. `kubectl` sends POST to API server (authenticated, authorized via RBAC)
2. API server validates the Deployment spec, runs admission controllers (mutations, validations)
3. API server writes Deployment object to etcd
4. Deployment controller (watching Deployments) detects new object, creates a ReplicaSet
5. ReplicaSet controller (watching ReplicaSets) detects new RS, creates Pod objects (status: Pending)
6. Scheduler (watching unscheduled Pods) scores nodes based on: resource requests, affinity/anti-affinity, taints/tolerations, spreading
7. Scheduler binds Pod to best node (updates Pod spec with nodeName)
8. kubelet on assigned node (watching its Pods) detects new assignment
9. kubelet calls containerd via CRI: pull image, create sandbox, start container
10. Container starts, kubelet reports status back to API server
11. Once running, probes begin: startup -> liveness -> readiness
12. When readiness passes, EndpointSlice updates -> Service starts routing traffic

Key timing: steps 1-5 take ~1s. Step 6 (scheduling) ~1s. Steps 8-11 depend on image pull (0-60s). Total: 3-65s for a new pod to serve traffic.

---

**Q2: The control plane goes down. What happens to running workloads?**

_Why they ask:_ Tests understanding of K8s failure modes.

**Answer:**
Short answer: **Running pods continue running.** The control plane manages state, not execution.

What continues working:

- Running containers keep running (kubelet and container runtime are on worker nodes)
- Network routing continues (kube-proxy rules are already installed)
- DNS resolution continues (CoreDNS pods are on worker nodes)
- Existing traffic patterns are unaffected

What breaks:

- No new pods can be scheduled (scheduler is down)
- Crashed pods don't get rescheduled to other nodes (controllers are down)
- kubelet still restarts local crashed containers (local restart policy works)
- No new deployments, scaling, or config changes (API server is down)
- kubectl commands fail (can't reach API server)
- Service endpoint updates stop (new pods won't get traffic)

Recovery: When control plane comes back, it reads state from etcd and reconciles. If etcd is lost, the cluster state is gone - this is why etcd backups are critical.

Key insight: K8s is designed so that worker node operation is independent of control plane availability. This is the "split-brain" design - the data plane and control plane are separate.

---

---

# Control Plane

**TL;DR** - The control plane is Kubernetes' brain - API server, scheduler, controller manager, and etcd working together to maintain desired state across the cluster.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Someone must decide where to run containers, restart them when they fail, and coordinate everything. Without a control plane, you're back to manual ops.

---

### Textbook Definition

The Kubernetes control plane is the set of components that make global decisions about the cluster (scheduling, detecting and responding to events, starting new pods when replica counts are unmet) consisting of: kube-apiserver, etcd, kube-scheduler, and kube-controller-manager.

---

### Understand It in 30 Seconds

**One line:**
The control plane decides WHAT runs WHERE and keeps it that way.

**One analogy:**

> The control plane is like a management team: CEO (API server - all communication), CFO (scheduler - resource allocation), COO (controller manager - operations), and secretary (etcd - records everything).

**One insight:**
The control plane is stateless except for etcd. API server, scheduler, and controller manager can be restarted at any time - they just re-read state from etcd and resume. This is why etcd backup is the single most critical operational task.

---

### How It Works

```
Control Plane Components:

API Server (kube-apiserver):
  - REST API front door for ALL operations
  - Authentication + Authorization (RBAC)
  - Admission control (mutating + validating)
  - Only component that talks to etcd

Scheduler (kube-scheduler):
  - Watches for unscheduled Pods
  - Scores nodes: resources, affinity, taints
  - Binds pod to selected node
  - Pluggable scoring/filtering

Controller Manager (kube-controller-manager):
  - ~30 built-in controllers
  - Deployment, ReplicaSet, StatefulSet, Job, Node
  - Each runs a reconciliation loop
  - Watch -> Compare -> Act

etcd:
  - Distributed key-value store
  - RAFT consensus (needs quorum: 3 or 5 nodes)
  - Only persistent state in the entire cluster
  - Critical path: lose etcd = lose cluster
```

---

### Quick Recall

**If you remember only 3 things:**

1. API server is the single front door - ALL communication (kubectl, kubelet, controllers) goes through it
2. etcd is the only persistent state - everything else is derived/reconstructible
3. Controllers are watch loops: observe actual state, compare to desired, take corrective action

**Interview one-liner:**
"The control plane consists of the API server (authenticated REST front door), etcd (distributed persistent state via RAFT), scheduler (pod-to-node placement), and controller manager (reconciliation loops for every resource type) - only etcd is stateful, making the rest trivially restartable."

---

### Interview Deep-Dive

**Q1: How would you make the control plane highly available?**

_Why they ask:_ Tests production architecture knowledge.

**Answer:**
HA control plane design:

1. **etcd**: 3 or 5 node cluster (RAFT needs quorum: 2/3 or 3/5). Spread across availability zones. Regular backups (etcdctl snapshot save).
2. **API server**: Multiple replicas behind load balancer. Stateless - any can serve any request.
3. **Scheduler/Controller Manager**: Multiple replicas with leader election. Only leader acts; followers are standby.
4. **Load balancer**: L4 (TCP) in front of API servers for kubectl and kubelet traffic.

Managed K8s (EKS/GKE/AKS) handles all of this. For self-managed: use kubeadm with stacked etcd (simpler) or external etcd (more resilient, harder to operate).

Key: test control plane failure regularly. Kill one etcd node and verify cluster continues. Simulate API server restart and confirm recovery.

---

---

# etcd

**TL;DR** - etcd is the distributed key-value store that serves as Kubernetes' single source of truth, storing all cluster state with strong consistency via RAFT consensus.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Cluster state (what should run where, what's actually running) needs to survive component restarts, node failures, and network partitions. Without a distributed consistent store, you lose state on failure.

---

### Textbook Definition

etcd is a strongly consistent, distributed key-value store that uses the RAFT consensus algorithm to replicate data across cluster members. In Kubernetes, it stores all cluster state (objects, configs, secrets) and is the only stateful component in the control plane.

---

### Understand It in 30 Seconds

**One line:**
etcd is Kubernetes' database - lose it and you lose the cluster.

**One analogy:**

> etcd is like the official record book in a courtroom. Every decision (state change) is recorded. Multiple copies exist (replicas) and they must agree (consensus). If the book is destroyed with no backup, all rulings are lost.

**One insight:**
etcd is on the critical path for EVERY Kubernetes operation. A slow etcd means slow API responses, slow scheduling, slow everything. This is why etcd performance (SSD storage, low-latency network) is critical and why the recommendation is dedicated nodes for etcd in production.

---

### How It Works

```
etcd Cluster (RAFT consensus):

  Node 1 (Leader)     Node 2 (Follower)    Node 3 (Follower)
  +----------+        +----------+         +----------+
  | WAL      |  raft  | WAL      |  raft   | WAL      |
  | Snapshot |------->| Snapshot |-------->| Snapshot |
  | Data DB  |        | Data DB  |         | Data DB  |
  +----------+        +----------+         +----------+

  Write path:
    Client -> Leader -> Replicate to followers
    -> Majority acknowledge -> Commit -> Response

  Quorum: (N/2)+1 nodes must agree
    3 nodes: quorum = 2 (survives 1 failure)
    5 nodes: quorum = 3 (survives 2 failures)

  K8s data stored as key-value:
    /registry/deployments/default/myapp -> {JSON spec}
    /registry/pods/default/myapp-abc12 -> {JSON spec}
    /registry/secrets/default/db-creds -> {encrypted}
```

---

### Quick Recall

**If you remember only 3 things:**

1. etcd is Kubernetes' ONLY persistent state - back it up regularly (etcdctl snapshot save)
2. Needs quorum to operate: 3-node cluster survives 1 failure, 5-node survives 2
3. Performance-sensitive: requires SSD, low-latency network, dedicated resources. Slow etcd = slow cluster.

**Interview one-liner:**
"etcd is a RAFT-based distributed key-value store serving as Kubernetes' single source of truth - I ensure HA with 3-5 nodes across AZs, regular backups via etcdctl snapshot, SSD storage for the WAL, and monitoring of fsync latency and leader elections."

---

### The Surprising Truth

etcd has a hard limit of 1.5 million key-value pairs (configurable but rarely changed). Large Kubernetes clusters (5000+ nodes) can hit this limit with just Pod objects. This is one reason why very large organizations run multiple smaller clusters rather than one massive cluster, and why Kubernetes has object count limits per namespace.

---

### Interview Deep-Dive

**Q1: etcd is reporting high latency. What's your troubleshooting approach?**

_Why they ask:_ Tests operational debugging of the most critical K8s component.

**Answer:**
Diagnosis steps:

```bash
# Check etcd health and leader
etcdctl endpoint health --cluster
etcdctl endpoint status --cluster

# Check disk latency (most common cause)
# etcd WAL fsync must be < 10ms
etcdctl check perf

# Check for leader changes (instability)
etcdctl endpoint status -w table
# Look at RAFT TERM - increasing = elections
```

Common causes:

1. **Disk I/O** (most common): etcd needs SSD. Shared disk with other workloads causes contention. Fix: dedicated SSD, `ionice`.
2. **Network latency**: RAFT heartbeat (100ms default) fails if network is slow between nodes. Fix: same AZ or low-latency network.
3. **Large objects**: A single Secret or ConfigMap > 1MB causes slow commits. Fix: split into smaller objects.
4. **Too many watchers**: API server watches many keys. Fix: increase etcd quota, consider watch coalescing.
5. **Compaction lag**: Old revisions not cleaned up, DB size grows. Fix: enable auto-compaction (`--auto-compaction-retention=1h`).

Prevention: dedicated nodes for etcd, SSD storage, monitor fsync_duration_seconds, set alerts on leader changes.

---

---

# kubelet

**TL;DR** - kubelet is the agent on every worker node that ensures containers described in PodSpecs are running and healthy, serving as the bridge between the control plane and the container runtime.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
The control plane decides where pods should run, but something must actually start and monitor them on each node. Without kubelet, desired state remains just words in etcd.

---

### Textbook Definition

kubelet is the primary node agent in Kubernetes that runs on every worker node, receiving PodSpecs from the API server and ensuring the described containers are running and healthy using the container runtime (containerd/CRI-O) via the Container Runtime Interface.

---

### Understand It in 30 Seconds

**One line:**
kubelet is the per-node manager that turns PodSpecs into running containers.

**One analogy:**

> kubelet is like a hotel housekeeper. The front desk (API server) assigns rooms (pods) to floors (nodes). The housekeeper (kubelet) ensures rooms are clean and ready (containers running), reports problems (status updates), and cleans up after guests leave (garbage collection).

**One insight:**
kubelet doesn't just start containers - it continuously monitors them via probes (liveness, readiness, startup). This monitoring data flows back to the API server, which updates Service endpoints (only healthy pods get traffic) and triggers restarts for unhealthy containers.

---

### How It Works

```
kubelet operation cycle:

API Server                       Node
+----------+                     +------------------+
| PodSpec: |  watch/sync every   | kubelet:         |
| image:X  | -----10s------->   | 1. Pull image    |
| ports:Y  |                     | 2. Create sandbox|
| probes:Z |                     | 3. Start container|
+----------+                     | 4. Run probes    |
                                 | 5. Report status |
     <--------- status --------- | 6. GC old containers|
                                 +------------------+
                                        |
                                 +------+------+
                                 | containerd  |
                                 | (via CRI)   |
                                 +-------------+

Probe types:
  Startup:  "Is the container initialized?"
  Liveness: "Is the container alive?" (restart if no)
  Readiness:"Can it serve traffic?" (remove from svc)
```

---

### Quick Recall

**If you remember only 3 things:**

1. kubelet runs on EVERY node and is responsible for the actual container lifecycle (start, stop, monitor)
2. It uses probes (startup, liveness, readiness) to determine container health and reports status to API server
3. kubelet continues operating even if the control plane is down (existing containers keep running, local restart policy works)

**Interview one-liner:**
"kubelet is the per-node agent that receives PodSpecs from the API server, manages container lifecycle via CRI (containerd), runs health probes (startup/liveness/readiness), reports status back, and continues operating independently during control plane outages."

---

---

# kube-proxy

**TL;DR** - kube-proxy maintains network rules on each node that enable Service abstraction - translating virtual ClusterIP addresses into actual pod IPs for load-balanced traffic routing.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Pod IPs are ephemeral (change on restart). A Service needs a stable IP (ClusterIP) that routes to whichever pods are currently healthy. Something must translate that virtual IP into actual pod IPs on every node.

---

### Textbook Definition

kube-proxy is a network proxy running on each node that implements Kubernetes Service concepts by maintaining network rules (iptables or IPVS) that route traffic destined for Service ClusterIPs/NodePorts to the appropriate backend pods.

---

### How It Works

```
kube-proxy modes:

1. iptables mode (default):
   ClusterIP 10.96.0.1:80
     -> DNAT to one of:
        - 10.244.1.5:8080 (pod A)
        - 10.244.2.3:8080 (pod B)
        - 10.244.3.7:8080 (pod C)
   Random selection via iptables probability

2. IPVS mode (higher performance):
   ClusterIP -> IPVS virtual server
     -> Real server pool (pods)
     -> Load balancing: rr, lc, sh, etc.
   O(1) lookup vs O(n) for iptables

3. eBPF mode (Cilium, replaces kube-proxy):
   Kernel-level routing without iptables
   Best performance at scale (10k+ services)

EndpointSlice flow:
  Pod becomes Ready -> EndpointSlice updated
    -> kube-proxy detects change
      -> Updates iptables/IPVS rules on ALL nodes
        -> Traffic routed to new pod immediately
```

---

### Quick Recall

**If you remember only 3 things:**

1. kube-proxy translates Service ClusterIPs into actual pod IPs using iptables/IPVS rules on every node
2. iptables mode is default (simple, O(n) rules). IPVS mode for high scale (O(1) lookup, multiple LB algorithms)
3. At very large scale (10k+ services), replace kube-proxy entirely with Cilium eBPF for kernel-level routing

**Interview one-liner:**
"kube-proxy runs on every node implementing Service networking by maintaining iptables or IPVS rules that DNAT ClusterIP traffic to healthy pod endpoints, updated via EndpointSlice watches - with IPVS mode for O(1) performance at scale and eBPF (Cilium) for eliminating kube-proxy entirely."

---

---

# API Server

**TL;DR** - The kube-apiserver is Kubernetes' central hub - the only component that reads/writes etcd, serving as the authenticated, authorized, admission-controlled front door for all cluster operations.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every component (scheduler, controllers, kubelet, kubectl) would need to talk to etcd directly. No access control, no validation, no audit trail. Chaos.

---

### Textbook Definition

The kube-apiserver is the front-end for the Kubernetes control plane, exposing the Kubernetes API via REST. It validates and configures data for API objects (pods, services, deployments), handles authentication, authorization (RBAC), admission control, and is the only component that communicates with etcd.

---

### Understand It in 30 Seconds

**One line:**
API server is the single front door - every K8s operation goes through it.

**One analogy:**

> The API server is like a bank teller. Every transaction (operation) must go through the teller (API server). The teller checks your ID (authentication), verifies you have permission (authorization), validates the transaction (admission control), and then records it in the ledger (etcd).

**One insight:**
The API server is stateless - it just validates and proxies to etcd. This means you can run multiple API server replicas behind a load balancer for HA without any coordination between them.

---

### How It Works

```
Request flow through API Server:

kubectl apply -f deployment.yaml
       |
  [Authentication]  <- Who are you?
       |             (certificates, tokens, OIDC)
  [Authorization]   <- Are you allowed?
       |             (RBAC: can user X verb Y resource Z?)
  [Admission]       <- Should we allow/modify?
       |             (Mutating: inject sidecar)
       |             (Validating: deny privileged)
  [Validation]      <- Is the object well-formed?
       |             (schema check, required fields)
  [etcd Write]      <- Store the object
       |
  [Watch Notify]    <- Tell controllers about change
       |
  [Response]        <- 201 Created
```

---

### Quick Recall

**If you remember only 3 things:**

1. ONLY component that talks to etcd - all other components go through API server
2. Request pipeline: Authentication -> Authorization (RBAC) -> Admission (mutating/validating) -> etcd
3. Stateless and horizontally scalable - multiple replicas behind a load balancer for HA

**Interview one-liner:**
"The API server is Kubernetes' stateless REST front door implementing the full security pipeline - authentication (who), RBAC authorization (can they), admission control (should we allow/mutate), and validation (is it correct) - before persisting to etcd and notifying watchers."

---

### Interview Deep-Dive

**Q1: How do admission controllers work and when would you write a custom one?**

_Why they ask:_ Tests advanced K8s knowledge and extensibility understanding.

**Answer:**
Admission controllers intercept API requests after authentication/authorization but before persistence. Two types:

1. **Mutating admission**: modifies the request (e.g., inject sidecar container, add labels, set defaults)
2. **Validating admission**: accepts/rejects the request (e.g., deny `latest` tag, require resource limits, deny privileged)

Order: Mutating runs first -> Validating runs second (validates the already-mutated object).

Built-in examples:

- `DefaultStorageClass`: adds default SC to PVCs
- `NamespaceLifecycle`: prevents creating objects in terminating namespaces
- `LimitRanger`: applies default resource limits

Custom admission (Webhook):

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: deny-latest-tag
webhooks:
  - name: deny-latest.mycompany.com
    rules:
      - operations: ["CREATE", "UPDATE"]
        resources: ["pods", "deployments"]
    clientConfig:
      service:
        name: webhook-svc
        path: /validate
```

Use custom webhooks when: enforcing org policies (no `latest` tags, require labels, security context requirements). Tools like OPA/Gatekeeper and Kyverno simplify this with policy-as-code.
