---
id: OSY-118
title: Container-OS Security Model
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-105, OSY-106, OSY-107, OSY-117
used_by: []
related: OSY-105, OSY-106, OSY-117, OSY-119
tags:
  - container
  - security
  - namespace
  - seccomp
  - capabilities
  - defense-in-depth
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 118
permalink: /technical-mastery/osy/container-os-security-model/
---

## TL;DR

Container security relies on OS primitives: namespaces
(visibility isolation), cgroups (resource limits), seccomp
(syscall filtering), and Linux capabilities (fine-grained
privilege). Defense-in-depth: each layer must be configured;
one misconfiguration can enable container escape. Shared
kernel is the fundamental limitation vs VMs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-118 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | container security, namespace, cgroups, seccomp, capabilities, container escape |
| **Prerequisites** | OSY-105, OSY-106, OSY-107, OSY-117 |

---

### The Shared Kernel Reality

```
VM isolation model:
  Host OS
    Hypervisor (VMware, KVM, Xen)
      VM1: Guest OS + kernel 1 (isolated)
        App1
      VM2: Guest OS + kernel 2 (isolated)
        App2
        
  Attack path: App2 -> exploit Guest OS2 kernel
  -> Cannot reach Guest OS1 or Host OS (different kernels)
  -> Hypervisor provides hardware-level isolation

Container isolation model:
  Host OS + Kernel (SHARED by ALL containers)
    Container1 (namespace + cgroup sandbox)
      App1 (sees its own PID/net/mnt namespace)
    Container2 (namespace + cgroup sandbox)
      App2
      
  Attack path: App2 -> exploit kernel bug
  -> Kernel is SHARED -> escape affects Container1 AND Host
  -> Container isolation = software boundary only
  
Implication:
  A critical kernel CVE affects ALL containers on the host
  A VM CVE affects only that VM
  
  For multi-tenant or untrusted workloads:
    Containers alone: insufficient isolation
    Use: gVisor (user-space kernel), Kata Containers (VM-based),
    or Firecracker (microVM) for stronger isolation
```

---

### Defense-in-Depth Layers

```
Layer 1: User Namespace (rootless containers)
  Container process runs as non-root inside its user namespace
  UID 0 inside container maps to UID 65534 (nobody) on host
  
  Without user namespaces:
    Container UID 0 = Host UID 0 (root!)
    File created inside container: owned by root on host
    
  With user namespaces (--userns-remap):
    Container UID 0 = Host UID 100000 (unprivileged)
    Much safer: even if container escape, no host root
    
  Docker: daemon.json: "userns-remap": "default"
  Kubernetes: use SecurityContext.runAsNonRoot: true

Layer 2: Linux Capabilities (fine-grained privilege)
  Traditional UNIX: root = all privileges
  Capabilities: split root privileges into ~40 capabilities
  
  Containers should DROP all, add only needed:
  
  Dangerous capabilities to avoid:
    CAP_SYS_ADMIN: nearly root; enables mount, ptrace, etc.
    CAP_NET_ADMIN: manipulate network interfaces
    CAP_SYS_PTRACE: trace any process (debug other containers!)
    CAP_DAC_OVERRIDE: bypass file permission checks
    CAP_SETUID: change UID (privilege escalation)
    
  Safe minimal set for a typical Java web service:
    CAP_NET_BIND_SERVICE (if binding port < 1024)
    No other capabilities needed in most cases
    
  Docker: --cap-drop ALL --cap-add NET_BIND_SERVICE
  Kubernetes: securityContext.capabilities.drop: ["ALL"]
              securityContext.capabilities.add: ["NET_BIND_SERVICE"]

Layer 3: Seccomp (Syscall Filtering)
  Java default syscalls needed:
    read, write, open*, close, stat, fstat, lstat
    mmap, mprotect, munmap, brk, madvise
    clone, futex (threading)
    socket, connect, bind, listen, accept (networking)
    epoll_*, io_uring (async I/O)
    exit, exit_group, wait4
    
  Syscalls to block for Java containers:
    mount: prevent filesystem mounting
    pivot_root, chroot: prevent FS root change
    kexec_load: prevent kernel loading
    create_module, init_module, finit_module: kernel modules
    ptrace: prevent process tracing (can read secrets)
    perf_event_open: can be used for side-channel attacks
    
  Docker default seccomp profile blocks ~300+ dangerous syscalls
  Custom profiles: start from Docker default, not from scratch

Layer 4: AppArmor / SELinux (MAC)
  Mandatory Access Control: OS enforces access policy
  Even root inside container: limited by MAC policy
  
  AppArmor profile for container:
    deny @{PROC}/sys/kernel/sched_setscheduler r,
    deny /proc/kcore r,
    deny /proc/sysrq-trigger r,
    deny /sys/kernel/debug/** r,
    
  SELinux label: container_t (default Docker label)
    Prevents writing to host filesystem
    Prevents accessing other container namespaces
```

---

### Common Container Escape Vectors

```
Vector 1: Privileged Container
  docker run --privileged myapp
  --privileged: grants ALL capabilities + disables seccomp
  + all host devices visible (/dev/*)
  
  Escape: mount /dev/sda1 inside container -> access host filesystem
  Detection: docker inspect | grep '"Privileged": true'
  Prevention: never use --privileged; use specific cap-add if needed
  
Vector 2: Host Path Volume Mount
  docker run -v /:/host myapp
  Mounts entire host filesystem inside container
  
  Escape: chroot /host; access all host files
  Detection: docker inspect | grep '"Binds"' -> check for "/"
  Prevention: never mount sensitive host paths; use named volumes

Vector 3: Docker Socket Mount
  docker run -v /var/run/docker.sock:/var/run/docker.sock myapp
  Grants control of Docker daemon from inside container
  
  Escape: run new privileged container from inside original container
  docker run --privileged -v /:/host ubuntu chroot /host
  Detection: ls -la /var/run/docker.sock inside container
  Prevention: never mount Docker socket; use sidecar patterns instead

Vector 4: Kernel Exploit
  Exploit unpatched kernel vulnerability from within container
  All containers on host affected
  
  Prevention: keep kernel patched; gVisor/Kata for high-risk workloads
  Detection: kernel integrity monitoring (IMA)
  
Vector 5: Namespace Confusion (user namespace UID mapping)
  Without user namespaces: container root = host root
  Files created inside container owned by host root
  
  Prevention: user namespaces (userns-remap)
  Or: enforce non-root user in container (USER 1000 in Dockerfile)
```

---

### Minimal Secure Container Configuration

```yaml
# Docker Compose secure configuration
version: '3.8'
services:
  myapp:
    image: myapp:latest
    user: "1000:1000"          # non-root
    read_only: true            # read-only root filesystem
    tmpfs:
      - /tmp:mode=1777,size=100m  # writable /tmp in RAM
      - /var/run:mode=755,size=10m
    security_opt:
      - no-new-privileges:true
      - seccomp:./seccomp-profile.json
      - apparmor:docker-default
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE      # only if port < 1024
    volumes:
      - type: volume
        source: app-data      # named volume, not host path
        target: /data
    network_mode: bridge      # NOT host
    environment:
      - JAVA_OPTS=-Xmx512m -Xms256m
```

```yaml
# Kubernetes secure Pod spec
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault    # or Localhost with custom profile
  containers:
  - name: myapp
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: []               # add only what's needed
    resources:
      limits:
        memory: "1Gi"
        cpu: "500m"
      requests:
        memory: "512Mi"
        cpu: "250m"
```

---

### Security Monitoring for Containers

```bash
# Detect privileged containers:
docker ps -q | xargs -I{} docker inspect {} \
  --format '{{.Name}}: Privileged={{.HostConfig.Privileged}}'

# Detect root-running containers:
docker ps -q | xargs -I{} docker inspect {} \
  --format '{{.Name}}: User={{.Config.User}}'
# Empty User = running as root (UID 0)

# Detect excessive capabilities:
docker ps -q | xargs -I{} docker inspect {} \
  --format '{{.Name}}: Caps={{.HostConfig.CapAdd}}'

# Falco rules for runtime anomaly detection:
# Detect shell execution inside container:
- rule: Terminal shell in container
  desc: A shell was used as entrypoint/exec point into a container
  condition: >
    spawned_process and container
    and shell_procs and proc.tty != 0
  output: >
    A shell was spawned (container=%container.name
    user=%user.name image=%container.image.repository
    shell=%proc.name)
  priority: WARNING

# Detect access to sensitive host files:
- rule: Read sensitive host file
  desc: An attempt to read files with sensitive OS or security info
  condition: >
    open_read and container
    and fd.name in (sensitive_file_names)
  output: >
    Sensitive file opened for reading
    (user=%user.name file=%fd.name container=%container.name)
  priority: WARNING
```

---

### Quick Reference Card

| Layer | What It Controls | Key Config |
|-------|----------------|------------|
| User namespace | UID mapping | `--userns-remap=default` |
| Capabilities | Privilege granularity | `--cap-drop ALL` |
| Seccomp | Syscall filtering | `--security-opt seccomp=profile.json` |
| AppArmor/SELinux | File access control | `--security-opt apparmor=docker-default` |
| Read-only FS | Filesystem mutation | `--read-only` |
| no-new-privileges | Privilege escalation | `--security-opt no-new-privileges` |
| cgroups | Resource limits | `--memory`, `--cpus` |
