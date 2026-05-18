---
id: LNX-106
title: "Container Platform Architecture on Linux"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-053, LNX-092, LNX-093
used_by: LNX-107, LNX-108
related: LNX-053, LNX-092, LNX-093, LNX-107, LNX-108
tags: [containers, linux-namespaces, cgroups, overlay-filesystem, oci-spec, container-runtime, runc, containerd, cri-o, docker, podman, veth-pairs, cni-plugins, seccomp, apparmor, selinux, capabilities, rootless-containers, container-escape, user-namespaces, overlayfs, union-mount, container-storage-interface, kubernetes-container-runtime, oci-image-spec, kata-containers, gvisor]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 106
permalink: /technical-mastery/lnx/container-platform-architecture-linux/
---

## TL;DR

Containers are Linux kernel primitives assembled together, NOT virtualization.
The three kernel primitives: (1) **namespaces** - process isolation (pid, net,
mnt, uts, ipc, user, cgroup namespaces isolate view of system resources),
(2) **cgroups v2** - resource limits (CPU shares, memory limit, I/O throttle),
(3) **overlay filesystem** - layered storage (Union Mount: image layers stacked,
copy-on-write for modifications). Runtime stack: OCI image spec defines image
format -> `runc` is the low-level OCI container runtime (does the actual namespace/
cgroup setup) -> `containerd` or `CRI-O` are high-level CRI runtimes (manage
lifecycle, images, snapshots) -> `kubelet` uses CRI to manage containers.
Container networking: kernel creates `veth` pair (virtual cable), one end in
container network namespace, one end on host bridge. CNI plugins (Calico, Cilium,
Flannel) handle IP assignment, routing, network policy. Security layers: seccomp
(syscall filtering), AppArmor/SELinux (MAC), capability dropping. Container escapes
happen when these security layers are misconfigured (privileged containers, hostPID,
dangerous capabilities).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-106 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | containers, namespaces, cgroups, overlayfs, OCI, runc, containerd, seccomp, CNI, container escape |
| **Prerequisites** | LNX-053 (filesystems), LNX-092 (namespaces), LNX-093 (cgroups) |

---

### The Problem This Solves

**Problem 1**: A developer writes "but it works on my machine" after an application
fails in production. The problem: different OS versions, different library versions,
different environment variables, different file paths. Containers solve this by
packaging the application WITH its dependencies (user-space libraries, configuration,
runtime) into an OCI image. The image runs identically on any Linux kernel that
supports the OCI runtime spec, regardless of host OS version.

**Problem 2**: Running 50 applications on one server. Without containers: each
application might have conflicting library versions (application A needs Python 3.8,
application B needs Python 3.11). With VMs: 50 VMs, each with full OS overhead
(1GB+ RAM, seconds to boot). With containers: shared kernel, isolated user-space.
50 containers start in <1 second, use only the memory their processes actually need.

---

### Textbook Definition

**Containers**: User-space isolation achieved by combining Linux kernel features.
A container is a process (or group of processes) that has:
- Isolated view of system resources via **namespaces**
- Resource limits via **cgroups**
- Isolated filesystem via **overlay filesystem**

**OCI (Open Container Initiative)**: Linux Foundation project defining:
- **Image spec**: how container images are layered, hashed, and stored
- **Runtime spec**: the interface for running containers (what runc implements)
- **Distribution spec**: how images are pushed/pulled from registries

**Container runtime stack (from Kubernetes perspective):**

```
kubelet (Kubernetes node agent)
    |
    v  [CRI gRPC interface]
containerd or CRI-O  (high-level runtime: manages images, snapshots, lifecycle)
    |
    v  [OCI runtime interface]
runc  (low-level runtime: actually creates namespaces, cgroups, runs process)
    |
    v
Linux kernel (namespaces, cgroups, overlayfs)
```

---

### Understand It in 30 Seconds

```bash
# === Container primitives: what runc actually does ===

# Create a new namespace (this is what 'container start' does underneath):

# See your current namespace IDs:
ls -la /proc/self/ns/
# lrwxrwxrwx ... mnt -> mnt:[4026531840]
# lrwxrwxrwx ... net -> net:[4026531992]
# lrwxrwxrwx ... pid -> pid:[4026531836]

# Create new namespaces (the 'unshare' command = manual container creation):
unshare --pid --net --mount --uts --ipc --fork bash

# In this new shell: we have new namespace IDs!
ls -la /proc/self/ns/
# different inode numbers = different namespaces

# Hostname is now separate from host:
hostname container-test  # only affects UTS namespace (our namespace)
exit  # host hostname is unchanged!

# === cgroup resource limits ===

# Create a cgroup for a container:
mkdir /sys/fs/cgroup/container1
echo "524288000" > /sys/fs/cgroup/container1/memory.max  # 500MB limit
echo "500000 1000000" > /sys/fs/cgroup/container1/cpu.max  # 50% of one CPU

# Run a process in this cgroup:
cgexec -g memory,cpu:container1 bash

# === overlayfs: container storage ===

# Container filesystem = layered images + writable layer on top
# Structure: lowerdir (image layers, read-only) + upperdir (writable) = merged view

mkdir -p /tmp/container-demo/{lower1,lower2,upper,work,merged}
echo "from layer1" > /tmp/container-demo/lower1/file1.txt
echo "from layer2" > /tmp/container-demo/lower2/file2.txt

mount -t overlay overlay \
    -o lowerdir=/tmp/container-demo/lower2:/tmp/container-demo/lower1,\
upperdir=/tmp/container-demo/upper,\
workdir=/tmp/container-demo/work \
    /tmp/container-demo/merged

ls /tmp/container-demo/merged/
# file1.txt  file2.txt  <- BOTH files visible!

# Modify a file (copy-on-write):
echo "modified" > /tmp/container-demo/merged/file1.txt
ls /tmp/container-demo/upper/
# file1.txt  <- modified copy in upper (writable layer)
cat /tmp/container-demo/lower1/file1.txt
# "from layer1"  <- original unchanged!

# This is exactly what Docker/containerd do:
# Image layers = lowerdir (read-only)
# Container writable layer = upperdir (discarded on container delete)
# Container sees merged view as its root filesystem

# === OCI runtime spec ===

# What 'docker run ubuntu bash' actually does:
# 1. Pull ubuntu image (layers to overlayfs lower dirs)
# 2. Create upper (writable) layer
# 3. Create config.json (OCI bundle: namespaces, cgroups, mounts, seccomp)
# 4. Call runc: runc run <bundle-dir>
# 5. runc: creates namespaces, sets up cgroup, mounts overlayfs, exec bash

# runc can be used directly:
mkdir -p bundle/rootfs
cd bundle
# Create OCI config:
runc spec  # generates config.json template
# Edit config.json: specify process, namespaces, mounts, seccomp...
runc run mycontainer  # runc directly starts the container

# containerd example (without docker):
ctr images pull docker.io/library/ubuntu:latest
ctr run docker.io/library/ubuntu:latest mytest bash

# === Container networking ===

# What happens when a container starts:
ip link show  # host view

# containerd/runc creates:
# 1. New network namespace for container
# 2. veth pair: 'veth0' (host) <-> 'eth0' (container)
# 3. Connects host-end to bridge 'docker0' or CNI bridge
# 4. Assigns IP to container eth0

# See veth pairs:
ip link show type veth
# vethXXXXXX@if2: ...  <- host end of veth pair
# Container's view: 'eth0' is the other end

# Container IP routing:
# Container eth0 -> veth pair -> host bridge -> NAT/routing
ip route show table main
# 172.17.0.0/16 dev docker0 proto kernel ...  <- docker bridge
```

---

### First Principles

```
Container = process + namespace + cgroup + overlayfs

Step 1: Process isolation (namespaces)

Seven namespace types in Linux:

  PID namespace:
    Container processes have their own PID number space
    Container PID 1 = actual PID 12345 on host
    Container cannot see/signal host processes
    Container init (PID 1) receives SIGTERM on stop
    
  Network namespace:
    Separate network stack: interfaces, routing, iptables
    Container sees only its own network interface (eth0)
    Host sees veth pair endpoint
    No network namespace = container shares host network (hostNetwork: true)
    Risk: container can sniff host traffic, bind to host ports
    
  Mount namespace:
    Container has its own mount point table
    Changes to mounts inside container not visible to host
    Image rootfs mounted at "/" of container, not at "/" of host
    
  UTS namespace:
    Separate hostname and NIS domain name
    Container can have its own hostname without affecting host
    
  IPC namespace:
    Separate System V IPC: message queues, semaphores, shared memory
    Container IPC cannot access host IPC objects
    
  User namespace:
    Map container user IDs to host user IDs
    UID 0 (root) inside container = UID 65534 (nobody) on host
    Foundation for rootless containers (no host root required!)
    Security: even if container escape, limited host privileges
    
  Cgroup namespace:
    Container sees only its own cgroup hierarchy
    Cannot escape to parent cgroup or see sibling limits

Step 2: Resource limits (cgroups v2)

  cgroups v2 unified hierarchy (replaced v1 in kernel 4.5, default in RHEL9):
  
  /sys/fs/cgroup/
    container1/
      memory.max    <- 500MB limit (OOM kill if exceeded)
      memory.high   <- 400MB soft limit (throttle before OOM)
      cpu.max       <- "500000 1000000" = 50% of one CPU
      io.max        <- I/O bandwidth limit: "8:0 rbps=1048576"
      pids.max      <- max process count (prevents fork bombs)
      cgroup.procs  <- list of PIDs in this cgroup
  
  Key cgroup v1 vs v2 differences:
  v1: separate hierarchies per resource type (one tree for cpu, one for memory)
  v2: unified hierarchy, single tree for all resources
  v2: better delegation (non-root can manage sub-cgroup)
  v2: better resource accounting across multiple controllers

Step 3: Filesystem isolation (overlayfs)

  Container image = set of read-only layers (stacked)
  Container writable layer = added on top (copy-on-write)
  
  Layer benefits:
  - ubuntu base layer shared across all ubuntu containers
  - Only modified files stored in each container's upper layer
  - 100 containers based on ubuntu: ubuntu layer downloaded ONCE
  
  overlayfs = kernel filesystem merging multiple directories:
  lowerdir: image layers (comma-separated, bottom to top)
  upperdir: container writable layer
  workdir: overlayfs internal use (must be empty, same filesystem as upper)
  merged: the container sees this as "/"
  
  Copy-on-write: reading lowerdir file = no copy (fast)
  Writing/modifying lower file = kernel copies to upperdir FIRST, then modifies
  
  Whiteout files: when container deletes a lower-layer file,
  overlayfs creates ".wh.filename" in upperdir to "hide" the lower file

Step 4: Container networking (OCI network model)

  Container network namespace is empty at creation (no interfaces)
  CNI plugin called with: container netns path + config
  CNI creates: veth pair, bridge, sets IP, routes, iptables rules
  
  Standard bridge mode:
  [container]--eth0--veth--[docker0 bridge]--iptables NAT--[host eth0]--[network]
  
  Pod-to-pod (Kubernetes overlay):
  [pod1]--veth--[cni0 bridge]--[flannel VXLAN]--[cni0 on node2]--[pod2]
  
  CNI plugin options:
  flannel: simple VXLAN overlay, no network policy
  Calico: BGP-based routing + Netfilter network policy
  Cilium: eBPF-based (XDP drop for network policy), best performance

Security layer: seccomp, AppArmor, capabilities

  Default Docker seccomp profile: blocks ~44 dangerous syscalls
  (keyctl, ptrace, mount, kexec_load, etc.)
  
  Without seccomp:
  Container process can call ANY syscall (mount, kexec_load, modify kernel)
  Container is just a process with different namespaces, still has full syscall access
  
  Capability dropping:
  Root process has 37 capabilities in Linux
  Containers should run with minimal capabilities
  CAP_NET_ADMIN: needed to configure networks (should not be in containers)
  CAP_SYS_ADMIN: grants many privileged operations (NEVER in containers)
  
  Docker default: drops 14 capabilities from root
  Best practice: --cap-drop=ALL --cap-add=CAP_NET_BIND_SERVICE (only what's needed)
  
  Container escape paths (when security is misconfigured):
  1. Privileged container (--privileged): full CAP_SYS_ADMIN, can remount host fs
  2. hostPID=true: can see all host processes, send signals to host PID 1
  3. hostNetwork=true: can sniff host traffic, bind any port
  4. Mounted Docker socket: can start privileged containers from inside container
  5. CAP_SYS_PTRACE: can ptrace (inspect memory of) any process in PID namespace
  6. Kernel exploit: container kernel is shared with host; CVE in kernel = escape
```

---

### Thought Experiment

Building a Kubernetes container runtime from first principles:

```bash
# === Trace what happens when 'kubectl run nginx --image=nginx' fires ===

# Step 1: kubelet receives pod spec from API server

# Step 2: kubelet calls containerd CRI to create sandbox (pause container):
crictl runp /tmp/sandbox-config.json
# Sandbox = shared network namespace for all containers in pod
# pause container: small process that holds the network/IPC namespace open
# All containers in pod share this network namespace (same IP!)

# Step 3: kubelet calls containerd to pull nginx image:
crictl pull nginx:latest
# containerd: fetches OCI image layers from registry
# Verifies SHA256 hashes of each layer
# Extracts layers to overlay snapshot storage

# Step 4: containerd prepares container filesystem (overlayfs):
# Layer setup (conceptually):
# lower1: nginx/config layer (sha256:abc123)
# lower2: nginx/bin layer (sha256:def456)
# lower3: debian base layer (sha256:789ghi)
# upper: new empty writable layer for this container
# Merged: container's root filesystem

# Step 5: containerd calls runc to run container:
# runc reads config.json (OCI runtime bundle):
cat /run/containerd/.../bundle/config.json | python3 -m json.tool | head -50
# {
#   "ociVersion": "1.0.2",
#   "process": {
#     "user": {"uid": 0, "gid": 0},
#     "args": ["nginx", "-g", "daemon off;"],
#     "env": ["PATH=/usr/local/sbin:..."]
#   },
#   "root": {"path": "rootfs"},  <- overlayfs merged dir
#   "linux": {
#     "namespaces": [
#       {"type": "pid"}, {"type": "network"}, {"type": "mount"},
#       {"type": "uts"}, {"type": "ipc"}
#       # Note: shares POD network namespace from pause container
#     ],
#     "cgroupsPath": "/kubepods/pod-abc123/container-xyz",
#     "seccomp": {...},  <- syscall filtering
#     "capabilities": {
#       "bounding": ["CAP_NET_BIND_SERVICE", "CAP_CHOWN", ...]  <- minimal set
#     }
#   }
# }

# Step 6: runc executes:
# a. Create namespaces: clone(CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWUTS|CLONE_NEWIPC)
# b. Join pod's network namespace: setns(sandbox_netns_fd, CLONE_NEWNET)
# c. Apply cgroup limits: write PIDs to cgroup
# d. Mount overlayfs as rootfs
# e. Set seccomp filter: prctl(PR_SET_SECCOMP)
# f. Drop capabilities
# g. chroot or pivot_root into container rootfs
# h. exec nginx -g "daemon off;"

# Step 7: CNI plugin called for networking (in sandbox creation):
# CNI plugin: flannel / Calico / Cilium
# Input: container network namespace path, pod IP from IPAM
# CNI creates:
# - veth pair: host side + container side
# - Container: eth0 (veth end), IP assigned
# - Host: vethXXXX connected to cni0 bridge
# - Routes added in both host and container namespaces

# Verify container is running:
crictl ps
# CONTAINER  IMAGE  CREATED  STATE    NAME
# abc123     nginx  5s ago   Running  nginx

# See container's PID on host:
crictl inspect abc123 | grep '"pid"'
# "pid": 12345

# See container's namespaces from host:
ls -la /proc/12345/ns/
# mnt -> mnt:[4026532123]  <- different from host!
# net -> net:[4026532456]  <- pod network namespace
# pid -> pid:[4026532789]  <- container PID namespace

# Container is just a process with different namespace pointers!
cat /proc/12345/status | grep Cap
# CapPrm: 00000000000004e0  <- minimal capabilities!
# CapEff: 00000000000004e0

# Decode capabilities:
capsh --decode=00000000000004e0
# = cap_chown,cap_net_bind_service,cap_setgid,cap_setuid,cap_kill
```

---

### Mental Model / Analogy

```
Container = apartment in an apartment building:

Apartment building = Linux host server
Kernel = building foundation, shared by all apartments
Operating system = building infrastructure (plumbing, electrical, elevators)

Traditional VM = separate house:
  Has its own foundation (guest kernel)
  Complete isolation: fire in one house doesn't affect others
  Slow to build (minutes to start), expensive (full house resources)
  
Container = apartment:
  Shares building foundation and infrastructure (kernel)
  Has walls (namespaces: each apartment has own address)
  Has utility meters (cgroups: each apartment billed separately)
  Has own key/lock (isolated filesystem)
  
Namespaces = apartment walls:
  PID namespace: can't hear neighbors through walls (can't see their processes)
  Network namespace: own mailbox/address (own IP, own ports)
  Mount namespace: own interior layout (own filesystem view)
  UTS namespace: own nameplate on door (own hostname)
  
cgroups = utility meters and circuit breakers:
  Memory limit: apartment cannot use more than N% of building water
  CPU limit: apartment circuit breaker limits power draw
  I/O limit: elevator usage cap for moving goods
  
overlayfs = apartment renovation model:
  Building has standard apartment template (image layers)
  Your apartment starts as a copy of the template
  You change decor, furniture (modifications go to your writable layer)
  Template unchanged for next tenant (lower layers read-only)
  Other apartments share the same template (base layers shared)
  
veth pair = door with mailbox:
  Container has internal door (eth0)
  Host sees external door (vethXXXX)
  Both connected: mail (packets) flow through this connection
  
CNI plugin = building postal service:
  Assigns apartment mailbox number (IP address)
  Routes mail to correct apartment (routing)
  Can enforce mail filtering rules (network policy)
  
Seccomp = internal apartment security guard:
  Guards the phone (syscall interface)
  Allows: "order pizza" (normal syscalls)
  Blocks: "install new plumbing" (dangerous syscalls like kexec, mount)
  
Container escape = finding a maintenance door in the wall:
  Privileged container = "maintenance mode" with master key (full kernel access)
  hostPID = floor plan shows ALL apartments' residents (all host processes)
  Mounted Docker socket = phone line to building manager to let anyone in
```

---

### Gradual Depth - Five Levels

**Level 1:**
What containers are: process isolation on Linux. Three building blocks:
namespaces (isolation), cgroups (limits), overlayfs (filesystem). Why
containers vs VMs (speed, density, shared kernel). Docker as the
popularizer. Basic container lifecycle: pull image, run, stop, rm.

**Level 2:**
Namespace types and what each isolates. cgroups v2 hierarchy and key
controllers (memory, cpu, io). overlayfs layer model and copy-on-write.
OCI image spec and runtime spec. runc as low-level runtime. containerd
as high-level runtime. Container networking: bridge mode, veth pairs.
CNI concept. Seccomp and capability dropping basics.

**Level 3:**
Container runtime stack details: kubelet -> CRI -> containerd -> runc.
OCI runtime bundle: config.json structure. Network namespace sharing in
Kubernetes pods. CNI plugin implementation (how Calico/Cilium configure
networking). AppArmor and SELinux for containers. User namespace for
rootless containers. Container storage drivers: overlay2 vs devicemapper.
CRI-O as alternative to containerd.

**Level 4:**
Rootless containers: user namespace UID mapping, subuid/subgid, running
containers without root on host. Kata Containers: VM-backed containers
for hardware isolation (security use cases). gVisor: user-space kernel
intercepting syscalls. Container storage: CSI (Container Storage Interface)
for persistent volumes. Multi-stage builds for minimal image sizes.
containerd snapshotter plugins (native, stargz/lazy pull). Pod security
policies vs Pod Security Admission.

**Level 5:**
Linux kernel features enabling containers: clone() flags, unshare(),
setns(), pivot_root(). eBPF for container security (Tetragon, Falco with
eBPF). Container escape techniques and mitigations: kernel CVEs, dangerous
capabilities analysis. Kubernetes admission controllers for security policy.
Supply chain security: image signing (Cosign, Notary), SBOM generation,
distroless images. CRI spec evolution and alternatives (WasmEdge for
WebAssembly workloads). Container-level eBPF networking (Cilium internals).

---

### Code Example

**BAD - insecure container deployment patterns:**
```yaml
# BAD: Kubernetes pod spec with multiple security vulnerabilities
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-app
spec:
  hostPID: true          # BAD: can see ALL host processes!
  hostNetwork: true      # BAD: can sniff ALL host network traffic!
  hostIPC: true          # BAD: can access ALL host IPC objects!
  
  containers:
  - name: app
    image: myapp:latest  # BAD: no digest pin, tag is mutable!
    
    securityContext:
      privileged: true   # BAD: full kernel access = container escape trivial!
      # No drop capabilities: gets all root capabilities
      allowPrivilegeEscalation: true  # BAD: can gain more privileges
      runAsRoot: true     # BAD: runs as UID 0
      
    volumeMounts:
    - name: docker-socket  # BAD: mounting Docker socket = trivial escape!
      mountPath: /var/run/docker.sock
  
  volumes:
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock  # BAD: full control of Docker daemon!

# Attacker with this pod can:
# 1. Use Docker socket to run: docker run -v /:/host --privileged ubuntu
#    Then chroot /host: full host filesystem access!
# 2. Kill any host process (hostPID)
# 3. Bind to any host port (hostNetwork)
```

```yaml
# GOOD: Hardened Kubernetes pod security context
apiVersion: v1
kind: Pod
metadata:
  name: hardened-app
spec:
  # No hostPID, hostNetwork, hostIPC: default false
  
  securityContext:
    runAsNonRoot: true      # Pod level: must not run as root
    runAsUser: 1000         # Specific non-root UID
    runAsGroup: 3000
    fsGroup: 2000           # Filesystem group for volumes
    seccompProfile:
      type: RuntimeDefault  # Apply default seccomp profile
    
  containers:
  - name: app
    image: myapp@sha256:abc123...def456  # Pin to immutable digest
    
    securityContext:
      allowPrivilegeEscalation: false  # Cannot gain more privileges
      readOnlyRootFilesystem: true     # Filesystem immutable at runtime
      
      capabilities:
        drop: ["ALL"]                  # Drop ALL capabilities first
        add: ["NET_BIND_SERVICE"]      # Add ONLY what's needed
    
    resources:              # Always set resource limits (cgroup enforcement)
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"     # OOM kill if exceeded
        cpu: "200m"         # CPU throttle (cfs_quota)
    
    # No hostPath volumes, no Docker socket mounts
    volumeMounts:
    - name: tmp
      mountPath: /tmp       # writable temp if needed
  
  volumes:
  - name: tmp
    emptyDir: {}            # ephemeral, isolated, no host path
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Containers provide the same isolation as VMs" | Containers and VMs have fundamentally different isolation boundaries. VMs: separate kernel, hardware virtualization boundary (QEMU/KVM, Hyper-V). Kernel vulnerability in guest VM does NOT affect host (different kernel). Containers: shared kernel. A kernel CVE that allows privilege escalation in the kernel = container escape for ALL containers on that host. This is why PCI-DSS, HIPAA, and government security standards often require VMs for tenant isolation. For multi-tenant environments with untrusted workloads: either use VMs, or use container-in-VM solutions (Kata Containers: each container in a lightweight QEMU-KVM VM; gVisor: user-space kernel intercepting syscalls). The attacker model matters: for trusted internal workloads, containers are fine. For running untrusted user code (cloud function platforms, CI/CD), VM isolation is needed. |
| "Docker IS containers (without Docker, no containers)" | Docker popularized containers but is a build tool + registry client + runtime stack, not a Linux feature. Containers are Linux kernel primitives (namespaces, cgroups, overlayfs) that existed before Docker (LXC, OpenVZ, Solaris Zones). Docker's contribution: OCI image format, easy-to-use image build (Dockerfile), registry ecosystem (Docker Hub), user-friendly CLI. The container runtime world post-Docker: `containerd` (Docker's runtime, donated to CNCF, now used by Kubernetes directly), `CRI-O` (Red Hat's minimal CRI runtime, no Docker dependency), `podman` (Docker-compatible CLI, rootless by default, no daemon). Kubernetes removed Docker as a runtime (dockershim removed in 1.24) because Kubernetes uses the CRI interface and containerd/CRI-O implement it directly. Docker can still be used to BUILD images (which are OCI-compatible), but is no longer the runtime in most Kubernetes clusters. |
| "A container with resource limits (requests/limits) cannot starve other containers" | CPU limits in Kubernetes (and Docker) use CFS (Completely Fair Scheduler) quota mechanism, NOT hard caps. Setting cpu.max = "100000 1000000" (100ms per 1s = 10% CPU) means the container's CFS period is 1 second with 100ms quota. The container CAN burst above the limit briefly (within a CFS period), then gets throttled. Memory limits ARE enforced: exceeding memory.max triggers OOM kill. CPU throttling can cause P99 latency spikes: a container doing processing that takes 101ms of CPU will be throttled, causing up to 900ms of extra latency. In Kubernetes, the "CPU request" (cpu.weight in cgroups v2) governs priority during contention, while "CPU limit" governs maximum usage. Practical recommendation: set memory limits always. Consider setting no CPU limits (only requests/weights) for latency-sensitive workloads to avoid CFS throttling. |
| "Container image layers are always deduped, storage is never a problem" | Container image deduplication works only within the same container runtime storage. overlayfs deduplication: two containers using the same ubuntu base layer share that layer's disk blocks. But: different image registries, different pull policies, or different storage drivers may not deduplicate. Common production problems: (1) containerd image store: default namespace isolation means same image in "k8s.io" and "default" namespaces stored twice. (2) Image sprawl: 200 different application images each with their own base layer (not using a shared base) = 200 full copies of the OS layer. (3) Build cache invalidation: adding a new dependency in the wrong Dockerfile line invalidates all subsequent layers for every rebuild. Best practices: use a minimal shared base image, pin to specific digest, order Dockerfile layers with least-changing first (OS -> dependencies -> code). `docker system df` shows actual disk usage breakdown. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: Container OOMKilled ===
# Pod keeps restarting with OOMKilled status

kubectl describe pod my-app-xyz
# Containers:
#   app:
#     Last State:    Terminated
#     Reason:        OOMKilled
#     Exit Code:     137
#     Started:       Mon, 01 Jan 2024 10:05:00
#     Finished:      Mon, 01 Jan 2024 10:05:45

# 137 = killed by signal (128 + 9 = SIGKILL from OOM killer)

# Check memory limit vs actual usage:
kubectl top pod my-app-xyz
# NAME          CPU(cores)   MEMORY(bytes)
# my-app-xyz    150m         245Mi   <- at limit of 256Mi

# From node: see kernel OOM log:
journalctl -n 100 | grep -i "out of memory"
# kernel: Out of memory: Kill process 12345 (java) score 956 or...
# kernel: Killed process 12345 (java) total-vm:524288kB, anon-rss:262144kB

# Fix: increase memory limit OR fix memory leak:
# kubectl set resources deployment my-app --limits=memory=512Mi

# === Failure: Container escape via privileged + hostPath ===
# Security audit finding: container can access host filesystem

kubectl get pods -o json | \
    python3 -c "
import sys, json
pods = json.load(sys.stdin)['items']
for p in pods:
    for c in p['spec']['containers']:
        sc = c.get('securityContext', {})
        if sc.get('privileged'):
            print('PRIVILEGED:', p['metadata']['name'], c['name'])
        for v in c.get('volumeMounts', []):
            if 'docker.sock' in v.get('mountPath', ''):
                print('DOCKER SOCKET:', p['metadata']['name'])
"

# Audit: find pods with dangerous settings:
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}: privileged={.spec.containers[*].securityContext.privileged}{"\n"}{end}' | grep "true"

# === Failure: Container cannot bind to port 80 ===
# App logs: "bind: permission denied" when trying to listen on port 80

# Port 80 < 1024: requires CAP_NET_BIND_SERVICE capability
# Check current capabilities of container process:
kubectl exec myapp -- cat /proc/1/status | grep Cap
# CapPrm: 0000000000000000  <- all capabilities dropped! Can't bind port 80

# Fix: add NET_BIND_SERVICE:
# In pod spec securityContext:
# capabilities:
#   drop: ["ALL"]
#   add: ["NET_BIND_SERVICE"]  <- add this

# OR (better): run app on port 8080, use Kubernetes Service to expose as 80:
# containerPort: 8080  (no special capabilities needed)
# Service: port: 80, targetPort: 8080 (kube-proxy handles translation)
```

---

### Related Keywords

**Foundational:**
LNX-053 (filesystems), LNX-092 (namespaces), LNX-093 (cgroups)

**Builds on this:**
LNX-107 (immutable Linux), LNX-108 (multi-tenant security)

**Related:**
LNX-107 (immutable infrastructure), LNX-108 (multi-tenant security)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `crictl ps` | List running containers (CRI level) |
| `crictl inspect <id>` | Container details, PID, namespaces |
| `runc spec` | Generate OCI config.json template |
| `runc run <bundle>` | Run container from OCI bundle |
| `unshare --pid --net --mount --fork bash` | Manual namespace creation |
| `nsenter -t <pid> -n ip addr` | Enter container network namespace |
| `cat /proc/<pid>/ns/` | View process namespace links |
| `ctr run <image> <name> bash` | Run container with containerd |

**3 things to remember:**
1. Containers are three Linux primitives combined: namespaces (isolate view), cgroups (limit resources), overlayfs (layer filesystem). No kernel virtualization: containers share the host kernel. A kernel CVE = all containers at risk.
2. The container runtime stack: `kubelet` -> CRI -> `containerd` -> OCI -> `runc` -> Linux kernel. Docker is not involved in Kubernetes since 1.24 (dockershim removed). `containerd` and `CRI-O` are the standard CRI runtimes.
3. Container security requires all layers: seccomp (syscall filtering), capability dropping (`cap-drop: ALL, cap-add: only what's needed`), non-root user, read-only root filesystem, no privileged flag. Missing any layer creates an escape vector.

---

### Transferable Wisdom

Container primitives map directly to: macOS App Sandbox (similar isolation model
using different OS mechanisms), Windows Containers (Windows Server Silos - NTFS
junction points vs overlayfs, Windows Job Objects vs cgroups), Java security
manager (software-layer capability restriction, now deprecated in favor of OS-level
containers), chroot jails (ancestral mount namespace isolation, weaker than containers).
The OCI runtime spec pattern (define spec, multiple implementations) transfers to:
CSI (Container Storage Interface - define spec, any storage provider), CNI (Container
Network Interface - define spec, any network plugin), CRI (Container Runtime Interface
- define spec, containerd and CRI-O implement it). The overlayfs copy-on-write model
is identical to: git working tree (index = staging = overlayfs upper), database
MVCC (old page + new page, transaction sees snapshot), ZFS snapshots (copy-on-write
block storage). The "defense in depth" security model (seccomp + capabilities +
SELinux + user namespace = multiple layers that must ALL fail for escape) is the
same principle as: WAF + network firewall + OS firewall + application auth (web
security), TLS + certificate pinning + HSTS (transport security). The resource
limit model (requests = guaranteed, limits = maximum, burst allowed briefly) maps
to: cloud VM burstable instance types (T3), CPU throttling in OS schedulers, QoS
bandwidth shaping in networking.

---

### The Surprising Truth

Containers are NOT a Linux invention. The concept predates Linux containers
by decades: IBM OS/360 in the 1960s had virtual machines, and the Multics
operating system (1969, which inspired Unix) had strong process isolation.
FreeBSD Jails (1999) and Solaris Zones (2004) implemented the "container"
concept years before Linux had comparable features. Linux had chroot (1979)
but it was weak isolation. Real Linux containers started with Linux-VServer
(2001), then OpenVZ (2005), then LXC (2008). Docker (2013) was the fourth
major Linux container technology.

Docker's real innovation was not containers themselves but the developer
experience: the Dockerfile (reproducible build), the layer model (fast
incremental builds), and the Docker Hub registry (easy sharing). These three
UX improvements turned a niche sysadmin tool into a revolution that changed
how software is built and deployed. The lesson: technical capability matters
less than user experience in technology adoption.

---

### Mastery Checklist

- [ ] Can explain the three Linux primitives (namespaces, cgroups, overlayfs) and what each provides
- [ ] Understands the container runtime stack: kubelet -> containerd -> runc -> kernel
- [ ] Can identify security risks in a Kubernetes pod spec (privileged, hostPID, Docker socket mount)
- [ ] Understands overlayfs layer model and copy-on-write behavior
- [ ] Can explain why container isolation is weaker than VM isolation and when that matters

---

### Think About This

1. You are tasked with running untrusted user-submitted code on a multi-tenant
   platform (similar to AWS Lambda or GitHub Actions). What is your isolation
   architecture? Containers alone are not sufficient (shared kernel). How do
   you choose between: KVM VMs, Kata Containers (container-in-VM), gVisor
   (user-space kernel), WebAssembly sandboxing? What are the performance,
   operational complexity, and security trade-offs of each? How do you handle
   the resource isolation (CPU, memory, network) for billing purposes?

2. A container running your Java application keeps getting OOMKilled despite
   having a 1GB memory limit. The JVM heap is configured at 512MB. Walk
   through your diagnosis: What is using the non-heap memory? (JVM native
   memory: metaspace, code cache, thread stacks, JNI allocations, GC overhead,
   off-heap NIO buffers). How does the Linux OOM killer decide which process
   to kill? How do you set JVM flags to stay within the container memory limit
   (-XX:MaxRAMPercentage vs -Xmx)? What monitoring would you add to prevent
   future OOMKill events?

3. Your security team mandates: "All containers must run as non-root."
   Your application binds to port 443 (HTTPS). Your application writes to
   /var/log/app.log (requires write access). Your application reads TLS
   certificates from /etc/ssl/private/ (requires root to read). How do you
   satisfy all three application requirements while running as non-root?
   (Hint: consider capabilities, volume permissions, init containers,
   Kubernetes Secrets for certificates, port remapping)

---

### Interview Deep-Dive

**Foundational:**
Q: Explain how containers work at the Linux kernel level. What are the three building blocks?
A: NAMESPACE ISOLATION - WHAT THE PROCESS SEES: Namespaces change what a process sees, not what it can do. Seven namespace types: (1) PID namespace: container process thinks it's PID 1 (init), but on the host it might be PID 12345. Processes in different PID namespaces cannot send signals to each other. (2) Network namespace: each container gets its own network stack - own interfaces, own routing table, own iptables rules, own port number space. Two containers can both listen on port 8080 without conflict. (3) Mount namespace: container has its own mount point table. Container's "/" is the image filesystem, not the host filesystem. (4) UTS namespace: separate hostname. Container can have its own hostname. (5) IPC namespace: separate System V IPC. (6) User namespace: map container UID 0 to non-root host UID (rootless containers). (7) cgroup namespace: container sees only its own cgroup tree. CGROUP RESOURCE LIMITS - WHAT THE PROCESS GETS: cgroups enforce resource limits. memory.max: hard memory limit (OOM kill if exceeded). cpu.max: CPU quota (throttle if exceeded). io.max: disk I/O bandwidth limit. pids.max: maximum process count (prevent fork bomb). These limits are enforced by the kernel scheduler and memory allocator; they're not advisory. OVERLAYFS FILESYSTEM LAYERS: Container image is a stack of read-only layers (each layer = one Dockerfile instruction). The container gets an additional writable layer on top. overlayfs presents the union as the container's root filesystem. When a container modifies a file from a lower layer: kernel copies the file to the writable upper layer (copy-on-write), modifies the copy. Original lower layer files are unchanged - shared with other containers. Container deletes a file: kernel creates a "whiteout" file in upper layer to hide the lower-layer file. ASSEMBLY: A container is created by: calling clone() with namespace flags, applying cgroup limits, mounting overlayfs as rootfs, then exec()ing the process. That's fundamentally all it is - no virtualization, no hypervisor, just kernel resource accounting and namespacing.

**Expert:**
Q: What are the common container escape techniques and how do you prevent each?
A: ESCAPE 1 - PRIVILEGED CONTAINER: A container started with --privileged or securityContext.privileged=true gets CAP_SYS_ADMIN plus access to all host devices. Exploit: mount host filesystem `nsenter --mount=/proc/1/ns/mnt -- mount /dev/sda1 /mnt` or `mkdir /tmp/host; mount /dev/sda1 /tmp/host`. Prevention: NEVER allow privileged containers. Use Pod Security Admission (PSA) with Restricted profile to enforce this. ESCAPE 2 - DOCKER SOCKET MOUNT: Container with `/var/run/docker.sock` mounted can issue Docker API commands. Exploit: `docker run -v /:/host --rm -it ubuntu chroot /host sh` = full host access. Prevention: NEVER mount Docker socket in pods. Use Trivy/Falco to detect this pattern. ESCAPE 3 - hostPID + dangerous capabilities: hostPID=true + CAP_SYS_PTRACE allows ptrace injection into host processes. Exploit: `nsenter -t 1 -m -u -i -n -p -- sh` (enter init's namespaces = host shell). Prevention: no hostPID, drop CAP_SYS_PTRACE. ESCAPE 4 - WRITABLE HOST PATH VOLUME: Container with host's /etc or /proc mounted writable. Exploit: write a new `/etc/cron.d/escape` with root cron job. Prevention: PSA Restricted prohibits hostPath volumes. Use audit policy to detect hostPath mount requests. ESCAPE 5 - KERNEL CVE: Shared kernel means any kernel privilege escalation CVE affects ALL containers. Historical examples: Dirty COW (2016), runc CVE-2019-5736 (writing to `/proc/self/exe` to overwrite runc binary). Prevention: keep kernel patched, use gVisor or Kata Containers for untrusted workloads (adds an isolation layer). SYSTEMIC PREVENTION: (1) Pod Security Admission (PSA) with "Restricted" profile enforces: no privileged, no hostPID/Net/IPC, no hostPath volumes, drops all capabilities, requires non-root, requires seccomp. (2) OPA Gatekeeper/Kyverno policies for additional custom policies. (3) Runtime monitoring: Falco watches for container escape indicators (unexpected syscalls, new shell in container, unexpected network connections). (4) Distroless images: no shell, no package manager, minimal attack surface even if code execution is achieved.
