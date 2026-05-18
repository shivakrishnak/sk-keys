---
id: LNX-080
title: "Container Internals on Linux (overlayfs, runc)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-071, LNX-072, LNX-078, LNX-073
used_by: LNX-106, LNX-108
related: LNX-071, LNX-072, LNX-078, LNX-079
tags: [overlayfs, runc, containerd, oci, container-runtime, image-layers, copy-on-write, union-mount, container-lifecycle, cgroup, namespace, seccomp, container-internals]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/lnx/container-internals-overlayfs-runc/
---

## TL;DR

Linux containers are NOT a single kernel feature but a COMBINATION:
**namespaces** (isolation), **cgroups** (resource limits), **overlayfs**
(layered filesystem), **capabilities** (privilege), **seccomp** (syscall
filtering), and **LSM** (AppArmor/SELinux). **overlayfs**: stacks read-only
image layers (lowerdir) + writable layer (upperdir) into a merged view.
Copy-on-write: writes go to upperdir only. `docker inspect` shows layers.
**runc**: the OCI reference runtime that creates containers from OCI bundles
(`runc spec`, `runc run`). **containerd**: higher-level runtime daemon used
by Docker and Kubernetes. Container creation: pull image -> create overlayfs
mount -> `clone()` with namespace flags -> set up cgroups -> exec entrypoint.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-080 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | overlayfs, runc, containerd, OCI, container internals, copy-on-write, image layers, namespaces, cgroups |
| **Prerequisites** | LNX-071 (Namespaces), LNX-072 (Cgroups), LNX-078 (Capabilities/seccomp) |

---

### The Problem This Solves

**Problem 1**: How do containers share base images efficiently? An Ubuntu
22.04 base image is 75MB. If 50 containers all use it: naive approach = 50
copies = 3.75GB. With overlayfs: 1 shared read-only copy (75MB) + 50 small
writable layers (each just the diff). 50 Ubuntu containers use ~75MB shared
base + small per-container overhead. This is why `docker pull ubuntu` is
fast for the second time: the layers are already cached.

**Problem 2**: What ACTUALLY happens when you run `docker run`? Understanding
the full stack from user command to running process is essential for:
debugging startup failures, security analysis, performance troubleshooting,
and building alternative container tools. This entry answers: what syscalls
are made, what kernel features are used, what each layer provides.

---

### Textbook Definition

**OCI (Open Container Initiative)**: Industry standards body (Linux Foundation,
2015). Publishes: Image Spec (how container images are structured: layers +
manifest + config), Runtime Spec (how runtimes create containers from OCI
bundles). OCI compliance: any OCI-compliant image runs on any OCI-compliant
runtime.

**runc**: Reference implementation of the OCI Runtime Spec. Written in Go.
Given an OCI bundle (root filesystem directory + `config.json`): creates a
container by calling Linux kernel APIs (namespaces, cgroups, etc.).

**containerd**: An industry-standard container runtime daemon (originally
from Docker Inc., now CNCF). Manages: image pulling/pushing, storage (overlayfs
layers), container lifecycle (create/start/stop). Used by: Docker (as its
runtime backend since Docker 1.11), Kubernetes (as the default CRI runtime).

**overlayfs**: A union filesystem (merged into kernel 3.18). Presents a
unified view of multiple directories stacked on top of each other. Read-only
layers at the bottom (image layers), writable layer on top (container layer).
Copy-on-write: files written to the container go to the writable layer (upperdir)
only; original (lowerdir) files are untouched.

---

### Understand It in 30 Seconds

```bash
# === See container internals directly ===

# View overlayfs mounts for running containers:
mount | grep overlay
# overlay on /var/lib/docker/overlay2/HASH/merged
# type overlay
# (lowerdir=LOWER:LOWER2,upperdir=UPPER,workdir=WORK)

# Find the overlay mount for a specific container:
CONTAINER_ID=abc123
docker inspect $CONTAINER_ID | python3 -c "
import json, sys
data = json.load(sys.stdin)[0]
gd = data['GraphDriver']
print('Type:', gd['Name'])
for k,v in gd['Data'].items():
    print(f'{k}:')
    print(f'  {v}')
"
# Type: overlay2
# LowerDir:
#   /var/lib/docker/overlay2/HASH_1/diff:
#   /var/lib/docker/overlay2/HASH_2/diff:...
# UpperDir:
#   /var/lib/docker/overlay2/HASH_upper/diff
# WorkDir:
#   /var/lib/docker/overlay2/HASH_upper/work
# MergedDir:
#   /var/lib/docker/overlay2/HASH_upper/merged

# View image layers (from image perspective):
docker inspect ubuntu:22.04 | python3 -c "
import json, sys
data = json.load(sys.stdin)[0]
for i, layer in enumerate(data['RootFS']['Layers']):
    print(f'Layer {i}: {layer[:20]}...')
"
# Layer 0: sha256:a2ef8ca...  <- OS base layer
# Layer 1: sha256:d8bc7...    <- apt packages layer
# (Ubuntu 22.04 has ~1-2 layers)

# View how many layers a Docker image has:
docker history ubuntu:22.04
# IMAGE          CREATED    CREATED BY               SIZE
# 3b418d7b466a   4 weeks    /bin/sh -c #(nop) CMD   0B
# <missing>      4 weeks    /bin/sh -c apt-get...   75.1MB

# View overlayfs on disk directly:
ls /var/lib/docker/overlay2/ | head -5
# HASH1/
#   diff/     <- layer contents (the actual files)
#   link      <- short ID for this layer
#   lower     <- reference to parent layer(s)
#   merged/   <- union mount point (only for top/container layer)
#   work/     <- overlayfs internal workdir

# === runc: create a container manually ===
# This is what Docker/containerd does internally:

# Create an OCI bundle:
mkdir -p mycontainer/rootfs
# Extract Ubuntu root filesystem:
docker export $(docker create ubuntu:22.04) | tar -C mycontainer/rootfs -xf -

# Generate default OCI config (spec):
cd mycontainer
runc spec
# Creates: config.json
# Edit config.json to customize: process, args, env, mounts, hooks

# Run the container:
runc run mycontainer
# Inside a namespaced environment!

# === containerd: the runtime daemon ===
# Check containerd state:
systemctl status containerd
ctr version    # containerd CLI

# List namespaces (containerd namespaces, not Linux namespaces):
ctr namespace list
# NAME      LABELS
# moby      <- Docker uses this namespace
# k8s.io    <- Kubernetes uses this namespace

# List containers (in moby namespace):
ctr -n moby containers list

# List images:
ctr -n moby images list | head -5

# === Container creation syscall trace ===
# strace the container start:
strace -f -e trace=clone,unshare,mount,execve \
    docker run --rm ubuntu echo "hello" 2>&1 | grep -E "clone|unshare|mount|execve"
# clone(... CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWPID|CLONE_NEWNS
#          |CLONE_NEWNET|CLONE_NEWUSER...) = NEW_PID
# mount("overlay", "...", "overlay", ...)   <- overlayfs
# execve("/bin/echo", ["echo", "hello"], ...) <- the container process
```

---

### First Principles

**The complete container creation sequence:**
```
docker run ubuntu:22.04 /bin/bash
              |
              v
     [Docker CLI]
     Sends API request to:
              |
              v
     [Docker Daemon (dockerd)]
     Communicates via gRPC to:
              |
              v
     [containerd daemon]
     Performs:
       1. IMAGE PULL (if not cached)
          - Check if image layers exist in overlay2 cache
          - Pull missing layers from registry
          - Verify SHA256 digest of each layer
          - Store decompressed tar in:
            /var/lib/docker/overlay2/HASH/diff/
       
       2. CONTAINER FILESYSTEM SETUP (overlayfs)
          Create a new writable layer:
            /var/lib/docker/overlay2/CONTAINER-HASH/
              diff/     <- writable (upperdir)
              work/     <- overlayfs workdir
          
          Mount overlayfs:
            mount -t overlay overlay \
              -o lowerdir=LAYER_N:...:LAYER_1,  <- stack of image layers
                 upperdir=CONTAINER-HASH/diff,  <- writable container layer
                 workdir=CONTAINER-HASH/work \
              CONTAINER-HASH/merged             <- container's /
          
          Now CONTAINER-HASH/merged/ looks like a complete Ubuntu filesystem
          Writes go to CONTAINER-HASH/diff/ (copy-on-write)
          Reads come from lowerdir layers (image, read-only)
       
       3. OCI BUNDLE PREPARATION
          Creates config.json with:
            - root: {path: "merged"}
            - process: {args: ["/bin/bash"], env: [...]}
            - linux.namespaces: [pid, net, ipc, uts, mount, ...]
            - linux.resources.memory: (from --memory flag)
            - linux.resources.cpu: (from --cpu flags)
            - linux.seccomp: (default Docker seccomp profile)
            - linux.capabilities: (default Docker capability set)
       
       4. DELEGATES TO RUNC (OCI runtime shim)
          runc receives the OCI bundle path
          
       5. RUNC EXECUTES:
          a. CLONE (create new namespaces):
             new_pid = clone(
               CLONE_NEWPID |    <- new PID namespace (container = PID 1)
               CLONE_NEWNET |    <- new network namespace
               CLONE_NEWIPC |    <- new IPC namespace
               CLONE_NEWUTS |    <- new UTS (hostname) namespace
               CLONE_NEWNS  |    <- new mount namespace
               CLONE_NEWUSER|    <- new user namespace (optional/rootless)
               SIGCHLD
             )
          
          b. CGROUP SETUP (resource limits):
             mkdir /sys/fs/cgroup/CONTAINER/
             echo memory_limit > memory.max
             echo cpu_quota > cpu.max
             echo child_pid > cgroup.procs
          
          c. NETWORK SETUP (typically via CNI plugin):
             Create veth pair: veth0 (host) <-> eth0 (container)
             Assign IP to container eth0
             Add to bridge/overlay network
          
          d. CAPABILITY DROPS:
             Drop most capabilities
             Keep: NET_BIND_SERVICE, etc. as configured
          
          e. SECCOMP FILTER INSTALLATION:
             prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, docker_profile)
          
          f. ROOTFS SETUP:
             mount --bind /proc -> container /proc
             mount --bind /sys -> container /sys
             pivot_root or chroot to the merged overlayfs
          
          g. EXEC the entrypoint:
             execve("/bin/bash", ..., clean_env)
             <- this is now PID 1 in the container
             <- all security controls are now active
```

**overlayfs copy-on-write in detail:**
```
Image layers (read-only, shared between containers):
  Layer 3 (top):  /app/config.json
  Layer 2:        /usr/bin/myapp
  Layer 1:        /etc/apt/sources.list, /usr/lib/...
  Layer 0 (base): /bin/bash, /lib/x86_64-linux-gnu/...

Container writable layer (per-container):
  upperdir: (empty initially)

Merged view (what the container sees):
  /bin/bash          <- from Layer 0 (lowerdir)
  /etc/apt/          <- from Layer 1 (lowerdir)
  /usr/bin/myapp     <- from Layer 2 (lowerdir)
  /app/config.json   <- from Layer 3 (lowerdir)

Container writes /etc/hosts:
  1. overlayfs: check if /etc/hosts exists in upperdir -> NO
  2. overlayfs: copy /etc/hosts from lowerdir to upperdir (copy-on-write)
  3. overlayfs: write changes to upperdir copy
  
  Result:
    upperdir: /etc/hosts (modified copy)
    lowerdir: /etc/hosts (original, unchanged)
  
  Merged view: /etc/hosts -> comes from upperdir (modified version)
  Original image layer: UNCHANGED (other containers still see original)

Container creates /data/myfile:
  1. /data/ doesn't exist in lowerdir
  2. /data/myfile created directly in upperdir
  
  upperdir: /data/myfile (new file)
  Merged view: /data/myfile visible

Container stops and is removed:
  upperdir directory is DELETED
  All container writes are LOST (ephemeral by default)
  lowerdir layers: UNCHANGED (still shared by other containers)

Container commits (docker commit):
  upperdir contents become a new image LAYER
  New layer sits on top of existing lowerdir stack
  New image = original image + new layer
```

---

### Thought Experiment

Debugging a container startup failure using kernel-level tools:

```bash
# Scenario: container starts but exits immediately with code 1
# docker run myapp -> exits immediately

# Step 1: Check the obvious (logs):
docker logs myapp_container
# exit code 1, no output -> process crashes at startup

# Step 2: Use nsenter to inspect the container's namespaces:
# Start a long-running version:
docker run -d --name debug_container myapp sleep 3600 || true
# If it exits, use --entrypoint:
docker run -d --name debug_container \
    --entrypoint sleep myapp 3600

# Get the PID:
CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' debug_container)

# Enter the container's namespaces:
nsenter --target $CONTAINER_PID \
    --mount --uts --ipc --net --pid \
    -- /bin/sh
# Now in the container's namespace context (as root)

# Check what's failing:
/app/myapp --check-config 2>&1

# Step 3: Look at the overlayfs for the container:
docker inspect debug_container | python3 -c "
import json, sys
gd = json.load(sys.stdin)[0]['GraphDriver']['Data']
print('Merged:', gd['MergedDir'])
"

# Browse the merged filesystem:
ls /var/lib/docker/overlay2/HASH/merged/app/

# Step 4: Trace the container startup:
strace -f -p $CONTAINER_PID 2>&1 | grep -E "ENOENT|EACCES|EPERM" | head -20
# strace: open("/etc/myapp/config.yaml", ...) = -1 ENOENT
# ^ Missing config file!

# Step 5: Root cause: config.yaml not included in image
# Fix: add to Dockerfile:
# COPY config.yaml /etc/myapp/config.yaml

# Step 6: Verify namespace isolation:
# Container PID namespace:
cat /proc/$CONTAINER_PID/status | grep NSpid
# NSpid: 12345   2    <- host PID = 12345, container PID = 2 (init = 1)
# ^ Container process IS PID 2 inside its namespace, 12345 from host perspective

# Container network namespace:
ip netns identify $CONTAINER_PID   # or:
ls -la /proc/$CONTAINER_PID/ns/net
# -> /proc/CONTAINER_PID/ns/net -> net:[4026531234]
# Different inode from host:
ls -la /proc/self/ns/net
# -> net:[4026531992]  <- different! isolated
```

---

### Mental Model / Analogy

```
Containers = specially-prepared hotel rooms with shared infrastructure

Hotel building = Linux kernel
Floors (shared infrastructure) = base image layers

Hotel room = container
  Room view (merged overlayfs):
    Furniture comes from the hotel's standard set (lowerdir layers)
    Your personal items are added on top (upperdir)
    When you check out: your items removed, room restored to original
  
  Room facilities:
    Wall outlet = capabilities (specific, limited privileges)
    Key card = namespace isolation (only your room)
    Noise limiter = cgroup (resource limits)
    Security camera = seccomp (allowed actions monitored)
    Fire door (stays closed) = AppArmor/SELinux (MAC policy)
  
overlayfs layers = hotel room starting state:
  Layer 0 (Ubuntu base): bed, bathroom, standard fixtures
  Layer 1 (apt-get install): desk, wifi router added
  Layer 2 (application): TV with your app's streaming service
  Container layer (upperdir): your luggage, personal settings
  
  Each room (container) shares the same base furniture (layers)
  But each has their own luggage (upperdir)
  
  "docker commit" = hotel keeping your luggage as the new room standard

runc = the hotel manager who prepares the room:
  1. Get the room's standard fixtures from storage (pull image layers)
  2. Set up the room (mount overlayfs)
  3. Install the security systems (namespaces, cgroups, seccomp)
  4. Give you the key card (capabilities)
  5. Welcome you in (exec the entrypoint)

containerd = the hotel's operations department:
  Coordinates with room manager (runc)
  Manages the image library (layer cache)
  Handles room bookings (container lifecycle)

Docker = the travel agency:
  Takes your booking (docker run)
  Coordinates with hotel operations (containerd)
  Hides all the complexity (CLI)

Kubernetes = the corporate travel manager:
  Makes bulk bookings across many hotels (cluster)
  Sets corporate travel policy (Pod Security Standards)
  Manages budgets (resource quotas)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Containers as isolated processes. Docker workflow: pull, run, exec, stop.
`docker inspect` to see container details. Image layers concept. Containers
are ephemeral (writes lost on remove).

**Level 2:**
overlayfs: lowerdir (image layers) + upperdir (container writable layer).
Copy-on-write behavior. `docker history` to see image layers. OCI: image
spec and runtime spec. containerd as Docker's runtime. runc as OCI reference
runtime. Container lifecycle: create -> start -> running -> stop -> remove.
`docker save`/`docker export` differences.

**Level 3:**
Container creation sequence: namespaces (clone()), cgroups, overlayfs mount,
seccomp, capabilities, exec. `nsenter` to enter container namespaces.
`runc spec` to generate OCI config. CNI (Container Network Interface) plugins.
`/proc/PID/ns/` to see namespace inodes. `docker commit` and layer creation.
Rootless containers (user namespaces).

**Level 4:**
overlayfs kernel mechanics: `lowerdir` stacking limit (500 layers, AuFS had 42).
whiteout files (deleted files in overlayfs). `pivot_root` vs `chroot` for
container rootfs. runc hooks: `createRuntime`, `createContainer`, `startContainer`.
OCI image manifest format (JSON, content-addressable layers). Rootless mode:
user namespace UID mapping, `newuidmap`/`newgidmap`. Kata Containers (OCI-
compatible VM containers using QEMU/firecracker). gVisor (user-space kernel
for containers, syscall interception).

**Level 5:**
overlayfs VFS layer implementation in kernel (`fs/overlayfs/`). NFS + overlayfs
limitations (overlayfs requires a tmpfs or ext4/btrfs upper layer). Container
storage drivers: overlay2 (default), btrfs, zfs, devicemapper (legacy).
Performance comparison: overlay2 (best general) vs btrfs (reflink, subvolumes)
vs zfs (snapshots, checksums). OCI hooks protocol (POSIX state on stdin/stdout
for hook executors). containerd plugins and the CRI (Container Runtime Interface)
gRPC spec. WASM containers (WasmEdge as OCI runtime via runwasi). Confidential
containers (Intel TDX, AMD SEV for encrypted container memory).

---

### Code Example

**BAD - container anti-patterns:**
```bash
# BAD 1: Dockerfile that creates too many layers (large image):
# Each RUN = new layer, each COPY = new layer
FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y curl wget git
RUN apt-get install -y python3 python3-pip
RUN pip3 install requests flask
RUN mkdir -p /app
COPY . /app
RUN cd /app && pip3 install -r requirements.txt
# Result: 8 layers, many containing apt cache bloat

# GOOD: combine RUN commands, clean up in same layer:
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
# Result: 4 layers, no apt cache bloat, smaller image

# BAD 2: Writing to overlayfs path that's shared (race condition):
# Container A writes /shared/file.txt (overlayfs upperdir)
# Container B reads /shared/file.txt (sees its own upperdir, not A's)
# Containers do NOT share writable layers!
docker run -d myapp  # Container A
docker run -d myapp  # Container B
# A and B have SEPARATE upperdirs - writes not visible to each other

# GOOD: Use shared volume for inter-container communication:
docker volume create shared-data
docker run -d -v shared-data:/shared myapp_writer
docker run -d -v shared-data:/shared myapp_reader
# Both see the same /shared directory

# BAD 3: Running without resource limits in production:
docker run myapp     # no memory, no CPU limits
# Container can consume all host memory (OOM killer hits OTHER processes)
# Container can consume all CPUs (other containers starved)

# GOOD: Always set resource limits:
docker run \
    --memory=512m \
    --memory-reservation=256m \
    --cpus=1.0 \
    --pids-limit=100 \
    myapp
```

**GOOD - overlayfs investigation and container internals:**
```bash
# Inspect overlayfs layer structure for a container:
inspect_container_layers() {
    local container=$1
    
    echo "=== Container: $container ==="
    
    # Get graph driver info:
    GDATA=$(docker inspect "$container" | \
        python3 -c "import json,sys; gd=json.load(sys.stdin)[0]['GraphDriver']['Data']; [print(k,'=',v) for k,v in gd.items()]")
    
    echo "$GDATA" | while IFS='=' read -r key val; do
        echo ""
        echo "--- ${key} ---"
        case "$key" in
            LowerDir)
                echo "$val" | tr ':' '\n' | while read -r layer; do
                    size=$(du -sh "$layer" 2>/dev/null | cut -f1)
                    echo "  Layer: $size $layer"
                done
                ;;
            UpperDir)
                size=$(du -sh "${val}" 2>/dev/null | cut -f1)
                echo "  Writable layer: $size $val"
                echo "  Changed files:"
                find "${val}" -type f 2>/dev/null | head -10 | \
                    sed 's|.*/merged||; s|^|    |'
                ;;
        esac
    done
}

inspect_container_layers myapp_container

# Create a minimal OCI container manually (what runc does):
create_oci_container() {
    local name=$1
    local image=$2
    
    # Create bundle directory:
    mkdir -p /tmp/$name/rootfs
    
    # Export Docker image to get rootfs:
    docker export $(docker create --name tmp_$name $image) | \
        tar -C /tmp/$name/rootfs -xf -
    docker rm tmp_$name
    
    # Generate OCI spec:
    cd /tmp/$name
    runc spec
    
    # Modify spec: change command
    python3 -c "
import json
with open('config.json') as f:
    config = json.load(f)
config['process']['args'] = ['/bin/sh']
config['process']['terminal'] = True
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
    echo "OCI bundle ready at /tmp/$name"
    echo "Run with: runc run $name"
}

# View running containers' namespace details:
show_container_namespaces() {
    local container=$1
    local pid=$(docker inspect --format '{{.State.Pid}}' "$container")
    
    echo "Container $container namespaces (host PID: $pid):"
    for ns in /proc/$pid/ns/*; do
        ns_name=$(basename "$ns")
        ns_inode=$(readlink "$ns")
        host_ns_inode=$(readlink /proc/self/ns/$ns_name 2>/dev/null)
        
        if [[ "$ns_inode" == "$host_ns_inode" ]]; then
            echo "  $ns_name: SHARED with host ($ns_inode)"
        else
            echo "  $ns_name: ISOLATED ($ns_inode)"
        fi
    done
}

show_container_namespaces myapp_container
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Containers are like lightweight VMs" | Containers are isolated PROCESSES on the HOST KERNEL. VMs have their own kernel. Key difference: containers share the host kernel (Linux), VMs have their own kernel (any OS). Containers start in milliseconds (it's just process isolation + overlayfs mount). VMs take seconds to boot (full OS init). Security difference: kernel vulnerabilities affect ALL containers on a host (they share the kernel). A VM escape requires a hypervisor vulnerability (much harder). The "container = lightweight VM" mental model causes dangerous security assumptions. Correct model: container = isolated process group + isolated filesystem + resource limits. |
| "Docker images store complete filesystems for every layer" | Docker image layers are INCREMENTAL DIFFS (like git commits), not complete filesystem snapshots. Each layer contains only the files that CHANGED relative to the previous layer. `FROM ubuntu:22.04` = ~75MB (the Ubuntu base layer). `RUN apt-get install python3` = ~50MB (only the new/modified files from installing python3, not a full OS copy). The total image size = sum of all layer sizes (which CAN be large if layers are poorly structured). `docker history myimage` shows the size contribution of each layer. This is why you should: combine RUN commands, clean up apt cache IN THE SAME RUN command (the cleanup must happen in the same layer as the install). Cleanup in a separate RUN layer DOES NOT help - the large files still exist in the previous layer. |
| "Stopping a container preserves your data" | Container file writes go to the WRITABLE LAYER (overlayfs upperdir). When you `docker stop` then `docker start` the SAME container: writable layer preserved. When you `docker rm` then `docker run` a NEW container: writable layer DELETED. Data is ephemeral by default in containers. For persistent data: use Docker volumes (`docker volume create`) or bind mounts (`-v /host/path:/container/path`). The confusion: people `docker stop` and `docker start` the same container (works, data preserved). But deploying a new image version requires `docker rm` + new `docker run` (data lost). Kubernetes pods are designed to be replaced: ALWAYS use PersistentVolumes for any data that must survive pod restarts. |
| "containerd and runc are just Docker components" | containerd and runc are independent, CNCF-hosted projects used by many container systems besides Docker. containerd is the default CRI (Container Runtime Interface) for Kubernetes - kubelet talks directly to containerd without any Docker daemon. runc is the OCI reference runtime used by containerd (and by podman, buildah, crun, and others). Docker is ONE application built on top of containerd + runc. Kubernetes has been using containerd directly (without Docker) since the dockershim was removed in Kubernetes 1.24. The ecosystem: OCI spec (standard) -> runc (reference runtime) -> containerd (production daemon) -> Docker (user-facing tool) / kubelet (Kubernetes integration). |

---

### Failure Modes & Diagnosis

**Container startup and overlayfs issues:**
```bash
# Symptom: container fails to start with "no such file or directory"
# Could be: missing file in image, missing volume mount, wrong entrypoint

# Step 1: Check what's in the image:
docker run --entrypoint /bin/sh -it myimage -c "ls /app"
# If /app doesn't exist in image: fix Dockerfile

# Step 2: Check overlayfs is mounted correctly:
CONTAINER_ID=$(docker inspect --format '{{.Id}}' mycontainer)
mount | grep $CONTAINER_ID
# If no overlay mount: container filesystem not set up

# Step 3: Inspect merged directory directly:
docker inspect mycontainer | python3 -c "
import json, sys
gd = json.load(sys.stdin)[0]['GraphDriver']['Data']
print(gd.get('MergedDir', 'Not mounted'))
"
ls /var/lib/docker/overlay2/HASH/merged/

# Symptom: "too many levels of symbolic links" during container ops
# Cause: circular symlinks in overlayfs layers, or too many layers
# overlayfs has a ~500 lower directory limit (kernel param):
cat /proc/sys/fs/inotify/max_user_watches
# Increase if needed: sysctl fs.inotify.max_user_watches=524288

# Symptom: "device or resource busy" on container removal
# A volume or bind mount is still in use:
lsof | grep /var/lib/docker/overlay2/HASH
# If a process has the directory open: kill it first
# Common cause: leftover mount points

# Step to force-cleanup:
docker stop mycontainer
docker rm mycontainer
# If still fails:
umount /var/lib/docker/overlay2/HASH/merged 2>/dev/null
docker rm -f mycontainer

# Symptom: container runs as root inside but can't write to volume
# SELinux label issue (RHEL) or wrong ownership:
# Check volume:
ls -laZ /host/path  # -Z for SELinux context
# Wrong SELinux context: add :z flag
docker run -v /host/path:/container/path:z myapp
# :z = label as container_file_t (shared)
# :Z = label as unique container type (private)

# Symptom: cgroup limits not applying (container ignores --memory)
# Check if cgroup v2 is enabled but Docker uses cgroup v1 API:
stat /sys/fs/cgroup/memory    # cgroup v1 hierarchy
ls /sys/fs/cgroup/            # cgroup v2 = unified hierarchy (no memory dir)

# For cgroup v2 support:
docker info | grep -i cgroup
# Check: "Cgroup Version: 2" with "Cgroup Driver: systemd" (correct for cgroupv2)
# Old: "Cgroup Version: 1", "Cgroup Driver: cgroupfs"
```

---

### Related Keywords

**Foundational:**
LNX-071 (Namespaces), LNX-072 (Cgroups), LNX-078 (Capabilities/seccomp), LNX-073 (eBPF)

**Builds on this:**
LNX-106 (Container platform architecture), LNX-108 (Multi-tenant security)

**Related:**
LNX-079 (LSM/SELinux/AppArmor), LNX-081 (KVM/QEMU virtualization)

---

### Quick Reference Card

| Concept | Command / Location |
|---------|-------------------|
| View container overlayfs | `docker inspect C \| grep -A5 GraphDriver` |
| Container merged dir | `/var/lib/docker/overlay2/HASH/merged/` |
| Container writable layer | `overlay2/HASH/diff/` (upperdir) |
| Image layers on disk | `/var/lib/docker/overlay2/*/diff/` |
| Enter container namespace | `nsenter --target PID --mount --net --pid -- /bin/sh` |
| OCI bundle generation | `runc spec` (creates config.json) |
| Run with runc | `runc run CONTAINER_NAME` |
| Container PID | `docker inspect --format '{{.State.Pid}}' C` |
| Check namespace isolation | `/proc/PID/ns/` inodes |

**3 things to remember:**
1. Container = namespaces + cgroups + overlayfs + capabilities + seccomp + LSM - not a single feature
2. overlayfs: lowerdir = read-only image layers (shared), upperdir = writable (per-container); writes copy-on-write to upperdir
3. Container writes are ephemeral: `docker rm` deletes the upperdir; use volumes for persistent data

---

### Transferable Wisdom

overlayfs copy-on-write appears in: git (objects are immutable content-
addressed blobs, working tree is the "writable layer"), ZFS/btrfs snapshots
(snapshot = read-only base, clone = writable layer on top), database MVCC
(Postgres MVCC: old tuple = lowerdir, new version = upperdir, readers see
consistent snapshot). The OCI standardization (image spec + runtime spec
+ distribution spec) is a case study in successful open standardization
of a complex ecosystem: Docker had proprietary lock-in (only Docker ran
Docker images), OCI standardization created competition (containerd, cri-o,
podman, runc, kata containers, gVisor all interoperate). The same pattern
appears in: OpenAPI (API spec standardization), OTel (observability spec),
WebAssembly (runtime portability). Container creation sequence (namespaces,
cgroups, overlayfs, seccomp, capabilities, exec) represents the synthesis
of all Linux kernel isolation mechanisms - understanding this sequence is
understanding container security holistically. Platform engineers: Kubernetes
CRI (Container Runtime Interface) abstracts over containerd/cri-o, allowing
runtime replacement without changing Kubernetes. The same separation-of-
concerns pattern appears in Kubernetes CSI (storage), CNI (networking),
and CRI (compute).

---

### The Surprising Truth

The entire container revolution was built on Linux kernel features that
existed BEFORE Docker was invented in 2013. Namespaces date to 2002
(mount namespace) with the key additions in 2006-2012. cgroups were
added in 2007. overlayfs was added in kernel 3.18 (2014), but AuFS
(a userspace predecessor) predates Docker. Docker's actual innovation
was NOT new kernel technology - it was PACKAGING: a user-friendly CLI,
the Dockerfile format for reproducible builds, the image registry (Docker
Hub), and a daemon that orchestrated all the existing kernel features.
This is why LXC (Linux Containers) existed before Docker but didn't achieve
Docker's adoption: LXC exposed the raw kernel complexity. Docker hid it
behind `docker run`. The container revolution was a packaging and UX
revolution built on a decade of kernel work. The second surprising truth:
runc (the reference OCI runtime) was extracted from Docker's internals
in 2015 and donated to the OCI. Kubernetes initially used Docker as its
runtime (via dockershim) but by 2020 was deprecating it in favor of
containerd directly - because Docker is an extra abstraction layer that
Kubernetes didn't need. Today, a standard Kubernetes cluster: kubelet ->
containerd (CRI-gRPC) -> runc (OCI) -> container. Docker itself is now
optional for both container runtime AND image building (buildkit, buildah,
kaniko build images without a Docker daemon).

---

### Mastery Checklist

- [ ] Understands the 6 kernel features that combine to create containers (namespaces, cgroups, overlayfs, capabilities, seccomp, LSM)
- [ ] Can explain overlayfs: lowerdir (image layers), upperdir (writable), copy-on-write
- [ ] Knows the container creation sequence: image pull -> overlayfs mount -> clone() namespaces -> cgroups -> exec
- [ ] Can use `docker inspect`, `nsenter`, and `/proc/PID/ns/` to inspect container internals
- [ ] Understands OCI: image spec, runtime spec, runc vs containerd distinction

---

### Think About This

1. You're building a container image for a Python web application. The
   current Dockerfile has 12 RUN instructions. The image is 1.8GB. Explain
   exactly why many RUN instructions cause a large image (using overlayfs
   layer mechanics), write an improved Dockerfile that achieves the same
   result in 3-4 layers with a much smaller image, and explain what happens
   at the overlayfs level when you `apt-get clean` in a separate RUN vs.
   the same RUN as `apt-get install`.

2. A container exits immediately after starting. Describe your complete
   diagnosis procedure using the kernel-level tools covered in this entry:
   what overlayfs paths you'd inspect, how you'd use `nsenter` to enter
   the container namespaces, what `strace` command you'd run against the
   container's PID, and how you'd distinguish between "file not found in
   image" vs. "permission denied by capabilities" vs. "blocked by seccomp"
   vs. "SELinux denial" as root causes.

3. Design an architecture question: you need to run 1000 containers on a
   single Linux host, all using the same base Ubuntu 22.04 image (75MB).
   Calculate the storage impact with and without overlayfs layer sharing.
   What are the overlayfs performance implications at 1000 containers
   (consider: how many lowerdir layers can overlayfs support, what happens
   at write-heavy workloads with deep layer stacks, what alternative storage
   drivers might you consider at this scale)?

---

### Interview Deep-Dive

**Foundational:**
Q: What Linux kernel features combine to create a container, and what does each provide?
A: A container is NOT a single kernel feature but a combination of 6 mechanisms: (1) NAMESPACES: isolation - each namespace type isolates a different resource. PID namespace: container gets its own PID space (PID 1 inside container). Network namespace: isolated network stack (interfaces, routing, iptables). Mount namespace: isolated filesystem mounts. UTS namespace: isolated hostname. IPC namespace: isolated shared memory, semaphores. User namespace (optional): UID mapping (container UID 0 = host UID 1000 for rootless). Created via `clone()` syscall with `CLONE_NEW*` flags. (2) CGROUPS: resource limits - cgroup v2 hierarchy at `/sys/fs/cgroup/`. `memory.max` = container OOM boundary. `cpu.max` = CPU bandwidth limit (quota/period). `pids.max` = fork bomb prevention. Resources accounted per-container process tree. (3) OVERLAYFS: filesystem - stacks read-only image layers (lowerdir) with writable container layer (upperdir). Copy-on-write for modified files. Shared image layers across containers (storage efficiency). (4) CAPABILITIES: privilege - drop most capabilities (`--cap-drop=ALL`), add specific ones (`--cap-add=NET_BIND_SERVICE`). Prevents full-root privilege even for UID=0 container processes. (5) SECCOMP: syscall filtering - Docker default profile blocks ~44 dangerous syscalls (kexec_load, init_module, etc.). BPF filter installed via `prctl()` before exec. (6) LSM: mandatory access control - AppArmor (Ubuntu): `docker-default` profile for all containers. SELinux (RHEL): `svirt_lxc_net_t` type for container processes. Independent enforcement layer even if other mechanisms are bypassed. Together: isolation (namespaces) + resource fairness (cgroups) + storage efficiency (overlayfs) + least privilege (capabilities + seccomp + LSM) = containers.

**Expert:**
Q: Walk through the complete lifecycle of `docker run ubuntu:22.04 /bin/bash`, from CLI command to running process, at the Linux kernel level.
A: Complete lifecycle: (1) CLI: Docker CLI parses the command, sends a REST API call to dockerd (`POST /containers/create` then `/start`). (2) dockerd -> containerd: Docker daemon forwards to containerd via gRPC (containerd API). (3) IMAGE: containerd checks local cache for ubuntu:22.04. If missing: pull from registry. Each layer is a gzipped tar, verified by SHA256 digest, stored decompressed in `/var/lib/docker/overlay2/HASH/diff/`. (4) OVERLAYFS SETUP: containerd creates a new writable layer directory: `/var/lib/docker/overlay2/CONTAINER-HASH/diff/` (upperdir). Executes: `mount -t overlay overlay -o lowerdir=LAYER_3:LAYER_2:LAYER_1:LAYER_0,upperdir=CONTAINER-HASH/diff,workdir=CONTAINER-HASH/work CONTAINER-HASH/merged`. The merged directory now looks like a complete Ubuntu 22.04 filesystem. (5) OCI BUNDLE: containerd generates `config.json` (OCI Runtime Spec) specifying: process command (`/bin/bash`), namespaces to create (pid, net, ipc, uts, mount, cgroup), resource limits, seccomp profile (Docker's default BPF program), capabilities to drop/keep, mounts (/proc, /sys, /dev). (6) RUNC: containerd calls runc (`runc create`, `runc start`). runc performs: `clone(CLONE_NEWPID|CLONE_NEWNET|CLONE_NEWIPC|CLONE_NEWUTS|CLONE_NEWNS|SIGCHLD)` - creates child process in new namespaces. Child process: calls `unshare(CLONE_NEWNS)` in the new mount namespace. `mount -t proc proc /proc` (container's /proc). `pivot_root` or `chroot` to the merged overlayfs directory. The container's root `/` is now the overlayfs merged view. Sets up cgroups: writes PID to `/sys/fs/cgroup/CONTAINER/cgroup.procs`. Memory/CPU limits applied. Capability drops: calls `capset()` to remove dangerous capabilities. Seccomp installation: `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &bpf_prog)`. CNI network setup: creates veth pair (veth0 host side, eth0 container side), assigns IP, adds to bridge. (7) EXEC: `execve("/bin/bash", ["/bin/bash"], env)` replaces the runc child process with the container entrypoint. The process is now PID 1 in its PID namespace, with the isolated filesystem, network, and all security controls active. Host sees it as PID XXXXX. Container sees it as PID 1. The full sequence is: 5-15ms typically (overlayfs mount + namespace creation is the dominant cost).
