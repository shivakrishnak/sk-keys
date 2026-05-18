---
id: OSY-072
title: Linux Namespaces Container Foundation
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-004, OSY-005, OSY-030
used_by: OSY-105, OSY-106, OSY-118
related: OSY-071, OSY-105, OSY-106
tags:
  - namespaces
  - containers
  - Docker
  - process-isolation
  - cgroups
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 72
permalink: /technical-mastery/osy/linux-namespaces/
---

## TL;DR

Linux namespaces are the kernel feature that makes
containers possible. Each namespace type isolates a
specific OS resource (PID, network, mount, UTS, IPC,
user). A container is simply a process inside a set of
namespaces. `docker run` = unshare() + clone() to create
new namespaces + execve() inside them. No hypervisor
needed; shares the host kernel.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-072 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | namespaces, containers, PID namespace, network namespace, unshare |
| **Prerequisites** | OSY-004, OSY-005, OSY-030 |

---

### Eight Linux Namespace Types

```
Namespace   Isolates                        Since
----------  ------------------------------  ------
Mount (mnt) File system mount points        2.4.19
UTS         Hostname, domain name           2.6.19
IPC         SysV IPC, POSIX message queues  2.6.19
PID         Process IDs                     2.6.24
Network     Network interfaces, ports, ips  2.6.24
User        User/group IDs                  3.8
cgroup      cgroup root directory           4.6
Time        Clock offsets (BOOTTIME, MONO)  5.6

Every running process is in exactly one instance of each namespace type.
A "container" = a process in a set of new namespace instances.
```

---

### PID Namespace (Container Process Isolation)

```
PID namespace: each namespace has its own PID space
  PID 1 inside namespace = init process of the container
  Same process: different PIDs in host vs container
  
  Host sees:          Container sees:
  PID 1234 = dockerd  PID 1 = /bin/sh (container's init)
  PID 1235 = /bin/sh  PID 2 = app.jar
  PID 1236 = app.jar
  
  Container cannot see host's PIDs (or other containers)
  Process in container: kill -9 5555 -> can only kill container PIDs
  
  PID 1 significance in containers:
    Traditional: init handles orphaned processes and signals
    Container: your app IS PID 1 (sh, java, nginx, etc.)
    
    If PID 1 exits: container stops immediately (all procs killed)
    SIGTERM sent to container: goes to PID 1
    If your app doesn't handle SIGTERM: container hangs, force-killed after 30s
    
  Java and PID 1:
    java process as PID 1: should handle SIGTERM for graceful shutdown
    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
        // Graceful cleanup
    }));
    This hook fires on SIGTERM (PID 1 receives it)
```

---

### Network Namespace (Container Networking)

```
Network namespace: each has its own:
  - Network interfaces (lo, eth0, etc.)
  - IP addresses
  - Routing table
  - Iptables rules
  - Port space (each container has its own 0-65535 range)
  
  Container port 8080 is separate from host port 8080
  Port mapping (Docker -p 80:8080):
    Creates a veth pair (virtual Ethernet pair)
    One end: container's eth0 (namespace A)
    Other end: host veth interface (default namespace)
    iptables DNAT: host:80 -> container:8080
    
  Container-to-container communication (Docker bridge):
    Default Docker bridge: 172.17.0.0/16
    Each container: one IP in this range
    Communication: through docker0 bridge (layer 2 switch)
    
  Kubernetes pod networking:
    Pod = shared network namespace for all containers in pod
    All containers in pod: same IP, same port space
    -> Containers communicate via localhost!
    -> Port conflicts between containers in same pod = real issue

Network namespace commands:
  ip netns list        # list network namespaces
  ip netns add myns    # create network namespace
  ip netns exec myns ip addr   # run command in namespace
  
  # What container sees:
  docker exec mycontainer ip addr
  # What host sees about container's namespace:
  nsenter --target $(docker inspect -f '{{.State.Pid}}' mycontainer) \
          --net ip addr
```

---

### Mount Namespace and Container Filesystem

```
Mount namespace: isolates the view of the filesystem
  Each namespace has its own mount table
  Container: sees its own root filesystem (from image)
  Host: sees its own root; container mounts appear under /proc/*/mounts
  
Container image layers (overlay2 filesystem):
  /lower (read-only image layers, merged):
    Ubuntu base layer
    App layer (JAR file, config)
    
  /upper (writable container layer):
    Files modified by container (COW copy-up)
    
  /merged (union view):
    /lower + /upper merged = what container sees as /
    Writes: go to /upper
    
  When container is deleted: /upper is discarded
  Image layers: remain cached (multiple containers share them)
  
  bind mount (-v in Docker):
    docker run -v /host/path:/container/path image
    bind mounts /host/path into container's mount namespace
    Container sees host files; changes persist after container stops
    
  tmpfs mount:
    docker run --tmpfs /tmp:size=100m image
    In-memory filesystem; fast; destroyed on container stop
    Use for: temp files, session data
```

---

### User Namespace (Rootless Containers)

```
User namespace: map user IDs between namespaces
  Container: runs as UID 0 (root) INSIDE the namespace
  Host: same process runs as UID 1000 (unprivileged)
  
  This enables rootless containers:
    docker run --user 1000 (running as non-root in container)
    Podman rootless: no root required at all
    
  UID mapping:
    Container UID 0   -> Host UID 1000
    Container UID 1-N -> Host UID 1001 to 1000+N
    
  Benefit: even if container breakout, attacker gets UID 1000 on host
    (not root = much less damage)
    
  Check if rootless:
    cat /proc/self/uid_map
    # "      0    1000       1" = container root = host uid 1000
    
  Kubernetes: rootless pods (experimental)
    Snapshotter must support user namespaces
    containerd 1.7+ supports user namespace
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Containers are more secure than VMs because they are lighter" | Containers share the host kernel. A kernel vulnerability exploitable from a container namespace can compromise the entire host. VMs have a hypervisor layer (smaller attack surface) between VM and host. Containers are lighter and faster but the security boundary is the kernel, which is shared |
| "A container's PID 1 is always a special init process" | In traditional Linux, PID 1 is init (systemd/sysvinit). In containers, PID 1 is whatever process you start - your app, a shell, a custom init. If your app is PID 1 and doesn't handle SIGTERM, `docker stop` will wait 30 seconds then SIGKILL. Use `tini` or `dumb-init` as PID 1 if your app isn't signal-aware |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| 8 namespace types | mnt, uts, ipc, pid, net, user, cgroup, time |
| Container definition | Process in a set of new namespace instances |
| PID 1 in container | Receives SIGTERM on `docker stop`; must handle gracefully |
| Network namespace | Each container gets its own IP + port range |
| User namespace | Map container root to unprivileged host UID |
| Mount namespace | Union filesystem (overlay2): layers + COW write layer |
