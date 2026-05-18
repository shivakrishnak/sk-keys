---
id: OSY-106
title: Linux Namespaces Deep Dive
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-023, OSY-105
used_by: []
related: OSY-105, OSY-107, OSY-118
tags:
  - namespaces
  - Linux
  - containers
  - isolation
  - PID
  - network
  - mount
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 106
permalink: /technical-mastery/osy/linux-namespaces/
---

## TL;DR

Linux namespaces isolate kernel resources per process group:
PID (process IDs), network (interfaces, routes, iptables),
mount (filesystem view), UTS (hostname), IPC (SysV IPC),
user (UID mapping), cgroup, and time. Docker container =
all 8 namespaces + cgroups. Namespaces provide the isolation
illusion; cgroups provide the resource limits. Understanding
each namespace's purpose reveals what containers DO and
DON'T protect.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-106 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | namespaces, PID namespace, network namespace, mount namespace, container isolation |
| **Prerequisites** | OSY-023, OSY-105 |

---

### The 8 Linux Namespaces

```
Namespace  | Kernel flag      | Isolates
-----------|------------------|------------------------------------------
PID        | CLONE_NEWPID     | Process ID numbers
Network    | CLONE_NEWNET     | Network interfaces, routes, iptables
Mount      | CLONE_NEWNS      | Filesystem mount points
UTS        | CLONE_NEWUTS     | hostname, domainname
IPC        | CLONE_NEWIPC     | SysV IPC, POSIX message queues
User       | CLONE_NEWUSER    | UID/GID mappings
cgroup     | CLONE_NEWCGROUP  | cgroup root view
Time       | CLONE_NEWTIME    | clock offsets (Linux 5.6+)
```

---

### PID Namespace

```
PID namespace:
  Each namespace has its own PID 1 (init process)
  Processes inside: see PIDs starting from 1
  
  Container perspective:
    PID 1: the container's init or main process
    PID 2, 3...: container's children
    Cannot see: host's other processes
    
  Host perspective:
    Container's PID 1 appears as: PID 54321 (arbitrary host PID)
    All container processes: visible to host with real PIDs
    Host can: kill -9 <container_PID> (from outside the namespace)
    
  Nested namespaces:
    Host -> Container -> Container (docker-in-docker)
    Each level has its own PID numbering
    
  Why it matters for security:
    Container CANNOT kill host processes (no visibility)
    But: host CAN see and kill container processes
    Privileged container: can escape and see host PIDs
    
  Example (what a container sees vs host):
    Inside container: ps aux shows PID 1 = java
    Outside container:
      ps aux | grep java -> shows PID 54321 = java
      ls -la /proc/54321/ns/pid -> symlink to pid:[4026532456]
      # The number identifies the specific PID namespace
```

---

### Network Namespace

```
Network namespace: complete isolation of networking stack
  
  Each namespace has:
    Separate: network interfaces (eth0, lo)
    Separate: IP addresses
    Separate: routing table
    Separate: iptables rules
    Separate: TCP/UDP socket space
    
  Container networking:
    Container created: gets its own network namespace
    Docker: creates a "veth pair" (virtual ethernet cable):
      One end: container's eth0 (in container namespace)
      Other end: vethXXXXXX (in host namespace, attached to bridge)
    Host bridge (docker0 or CNI bridge): routes between containers
    
  Port mapping:
    docker run -p 8080:80: 
      Host iptables rule: REDIRECT :8080 -> container_IP:80
      OR: DNAT: NAT rule changes destination IP
    Container: listens on :80 in its own network namespace
    Host: :8080 is the external entry point
    
  Kubernetes pods:
    All containers in a pod SHARE the same network namespace
    Same pod -> same IP address -> communicate via localhost
    This is why sidecar pattern works: app + proxy on localhost
    
  Network namespace inspection:
    ip netns list       # List named network namespaces
    ip netns exec ns1 ip addr  # Run command in namespace
    
    nsenter -t $PID --net ip addr  # Enter container's netns
    # Shows container's network view from host
    # Useful for debugging container networking
```

---

### Mount Namespace

```
Mount namespace: each process sees its own filesystem tree
  
  Without mount namespace:
    Process mounts /dev/sdb1 at /data
    ALL processes on system see /data
    
  With mount namespace:
    Container mounts its overlay filesystem at /
    Host still has its root filesystem
    Container's / is completely separate from host's /
    
  Overlay filesystem (used by Docker/containers):
    Layer 1 (lowest): base image (debian, ubuntu)
    Layer 2: installed software
    Layer N: latest changes
    Mount: merged view (overlayfs)
    Writes: go to upperdir (container's private layer)
    Reads: search from top layer down
    
  Mount namespace operations:
    # See container's mount namespace from host:
    nsenter -t $PID --mount ls -la /
    # Shows container's root filesystem (not host's)
    
    # See container's mounts:
    cat /proc/$PID/mounts
    # Shows: overlayfs, tmpfs, devpts, etc. for the container
    
  Mount propagation (shared subtrees):
    MS_SHARED: mounts propagate both ways (host <-> container)
    MS_PRIVATE: mounts don't propagate (default for containers)
    MS_SLAVE: changes from host propagate in; not out
    MS_UNBINDABLE: cannot be bind-mounted into other namespaces
    
  Security implications:
    /proc mount in container: filtered version (no host info)
    /sys mount in container: limited view
    Privileged container: can access host /proc and /sys
    -> Container escape possible via /proc/sysrq-trigger etc.
```

---

### User Namespace

```
User namespace: map container UIDs to different host UIDs
  
  Without user namespaces:
    Container root (UID 0) = HOST root (UID 0)!
    Container escape -> you're root on the host
    
  With user namespaces (rootless containers):
    Container root (UID 0) -> host UID 100000
    Container UID 1 -> host UID 100001
    Container UID 65535 -> host UID 165535
    
    If container process escapes:
      It's UID 100000 on the host (not root)
      Cannot write to system files (owned by root/UID 0)
      Significant privilege reduction
      
  Podman: user namespaces by default (rootless containers)
  Docker: user namespaces available but not default
    Enable: "userns-remap": "default" in /etc/docker/daemon.json
    
  Check namespace of a process:
    ls -la /proc/$PID/ns/
    # Shows: cgroup, ipc, mnt, net, pid, time, user, uts
    # Each: symlink to namespace identifier
    # "user:[4026531837]" = initial user namespace (host)
    # Different number = separate user namespace (container)
    
  Limitation:
    User namespaces: reduce damage from escape
    But: kernel exploits (Dirty COW, etc.) bypass user namespace protections
    Defense in depth: user namespaces + seccomp + AppArmor
```

---

### What Namespaces Don't Protect

```
Common misunderstanding: containers are "fully isolated VMs"
  
  Namespaces provide ILLUSION of isolation, not complete isolation:
  
  SHARED kernel:
    All containers share the HOST kernel
    Kernel exploit: affects ALL containers on the host
    CVE-2016-5195 (Dirty COW): exploitable FROM inside any container
    Fix: keep host kernel patched; use gVisor for untrusted containers
    
  SHARED hardware:
    CPU: shared (cgroups limits, but no hardware isolation)
    Noisy neighbor: one container spinning CPU affects all via scheduling
    
  Namespace escape routes (privileged containers):
    --privileged: disables almost all namespace protection
    CAP_SYS_ADMIN: can manipulate namespaces, mount filesystems
    CAP_NET_ADMIN: can modify host network configuration
    --pid=host: shares host PID namespace
    --network=host: shares host network namespace
    
  Rule: container security = namespaces + cgroups + seccomp + AppArmor + no privileges
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Docker provides full VM-level isolation" | Docker uses kernel namespaces + cgroups. Shared kernel means any kernel vulnerability affects all containers. VMs have their own kernel and hardware virtualization; a guest kernel exploit doesn't affect the host. For untrusted workloads: use Kata Containers, gVisor, or actual VMs. |
| "Containers can't see each other's processes" | By default yes - PID namespaces isolate process visibility. But if two containers are in the SAME PID namespace (e.g., pods with shared PID namespace in Kubernetes), they can see each other's processes. Also: from the HOST, all container processes are visible. |
| "A rootless container is completely safe" | Rootless containers (user namespace) significantly reduce risk. But kernel vulnerabilities can still be exploited by mapping back to real UID. Rootless + seccomp + no CAP_SYS_ADMIN = good security posture. Still: kernel must be kept patched. |

---

### Quick Reference Card

| Namespace | Isolation | Key File |
|-----------|-----------|---------|
| PID | Process IDs | `/proc/PID/ns/pid` |
| Network | Network stack | `/proc/PID/ns/net` |
| Mount | Filesystem view | `/proc/PID/ns/mnt` |
| UTS | Hostname | `/proc/PID/ns/uts` |
| IPC | SysV IPC | `/proc/PID/ns/ipc` |
| User | UID/GID mapping | `/proc/PID/ns/user` |
| cgroup | cgroup root | `/proc/PID/ns/cgroup` |
| Time | Clock offsets | `/proc/PID/ns/time` |
| Enter namespace | - | `nsenter -t $PID --net ...` |
