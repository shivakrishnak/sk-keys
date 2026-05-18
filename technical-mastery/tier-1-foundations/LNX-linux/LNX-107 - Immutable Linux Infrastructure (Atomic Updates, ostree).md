---
id: LNX-107
title: "Immutable Linux Infrastructure (Atomic Updates, ostree)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-053, LNX-106
used_by: LNX-108
related: LNX-053, LNX-106, LNX-108
tags: [immutable-infrastructure, ostree, rpm-ostree, atomic-updates, flatcar, fedora-coreos, bottlerocket, talos-linux, a-b-partition, read-only-rootfs, configuration-drift, kpatch, live-patching, cattle-not-pets, gitops-infrastructure, nix-os, immutable-os, coreos, container-host-os, declarative-os]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 107
permalink: /technical-mastery/lnx/immutable-linux-infrastructure-atomic-ostree/
---

## TL;DR

**Immutable Linux infrastructure** treats OS installations as read-only artifacts
that are replaced atomically rather than modified in-place. Key mechanism:
**ostree** (libostree) is a "git for OS filesystems" - it versions the OS tree as
content-addressed objects, allowing atomic switch between versions and guaranteed
rollback. **rpm-ostree** adds RPM packaging on top (used by Fedora CoreOS,
Red Hat CoreOS). **A/B partition scheme**: two OS partitions (A and B), new
version installed to inactive partition while current runs, reboot switches;
bad boot automatically falls back. **Benefits**: zero configuration drift (root
filesystem is read-only, cannot be modified at runtime), atomic rollback (if
update fails to boot: automatic rollback to previous working version), reproducible
(every node with same commit hash has identical state). **Tradeoffs**: apps must
run from containers or designated writable paths, no ad-hoc package installs.
**Implementations**: Fedora CoreOS (container host), Bottlerocket (AWS container
host), Talos Linux (Kubernetes-specific, no SSH), NixOS (Nix package manager,
declarative OS config).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-107 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | immutable infrastructure, ostree, rpm-ostree, Fedora CoreOS, Bottlerocket, Talos Linux, atomic updates, A/B partitions |
| **Prerequisites** | LNX-053 (filesystems), LNX-106 (containers) |

---

### The Problem This Solves

**Problem 1**: Configuration drift. 500 production servers. Over two years:
engineers SSH'd to individual servers to "fix" things, installed packages,
modified config files, applied patches ad-hoc. Server #127 is now subtly
different from servers #128-500 in ways no one fully knows. Application that
worked on #128 fails on #127 with cryptic errors. Forensics takes days.

Immutable OS: root filesystem is mounted read-only. No one can modify it
interactively. Every change requires a new OS commit, tested, deployed
uniformly to all servers. Result: if same commit hash is on all nodes, they
ARE identical, by definition.

**Problem 2**: Failed OS update leaves a server in an inconsistent state.
Traditional: partial package update fails midway. System has mix of old and
new library versions. Rolling back requires knowing exactly what changed.
Often: "just reinstall and restore from backup."

Atomic update: new OS version installed to inactive partition while current
version is running. Reboot switches to new version. If boot fails: bootloader
detects failure (failed to reach systemd.default.target), automatically
selects previous partition. No inconsistent state possible.

---

### Textbook Definition

**Immutable infrastructure**: A deployment model where servers are never
modified after deployment. To change configuration: deploy a new server
(or boot a new OS image), retire the old one. "Cattle, not pets."

**ostree (libostree)**: A content-addressed object store for Linux filesystem
trees. Similar to git: each unique file content is stored once (by SHA256
hash), filesystem tree is a Merkle tree of content hashes. A deployment is
a reference to a specific tree commit. Switching deployments: atomically
updates symlinks, no files replaced in-place.

**A/B partition scheme**: Physical disk has two system partitions (A and B).
Current OS runs from partition A. Update installs new OS to partition B (while
A is running). On reboot: bootloader tries partition B. If successful: B is now
"current." If failed: bootloader retries B once then falls back to A.

---

### Understand It in 30 Seconds

```bash
# === ostree / Fedora CoreOS workflow ===

# Fedora CoreOS: container-optimized, immutable Linux
# Default state: root filesystem is READ-ONLY

# On a Fedora CoreOS node:
rpm-ostree status
# State: idle
# Deployments:
# * fedora-coreos:fedora/x86_64/stable
#     Version: 38.20231110.3.2 (2023-11-10T18:40:02Z)
#     Commit: abc123def456...
#     GPGSignature: Valid signature by...
#
# Notice the '*': this is the ACTIVE deployment

# Try to install a package normally - it WORKS differently:
sudo rpm-ostree install htop
# (not modifying running system!)
# (creates NEW deployment with htop added)
# (reboot to switch to new deployment)
rpm-ostree status
# Deployments:
#   fedora-coreos:fedora/x86_64/stable  <- NEW deployment (with htop)
# * fedora-coreos:fedora/x86_64/stable  <- CURRENT deployment (without htop)

# Reboot to activate new deployment:
systemctl reboot
# After reboot: htop is available (new deployment active)

# Check OS update:
rpm-ostree upgrade
# Downloading new deployment...
# Pulling commit: abc...
# Creating new deployment

# Rollback (if something breaks after update):
rpm-ostree rollback
# (instantly - just switches to previous deployment)
# (no uninstalling, no package rollback - entire OS tree atomic)

# === A/B partition: how it works ===

lsblk
# sda
# ├── sda1  /boot/efi  (EFI partition)
# ├── sda2  /boot      (bootloader + grub.cfg)
# ├── sda3  /sysroot   (ostree repo = both deployments)
# └── sda4  /var       (WRITABLE: application data, logs)

# ostree stores both deployments in /sysroot/ostree/
ls /sysroot/ostree/deploy/fedora-coreos/deploy/
# abc123.0/  <- deployment 1 (current)
# def456.0/  <- deployment 2 (previous, kept for rollback)

# Current deployment bind-mounted to /:
# /sysroot/ostree/deploy/fedora-coreos/deploy/abc123.0 -> /

# /var is WRITABLE and persistent across deployments:
# Logs, container data, application state lives here

# === Bottlerocket (AWS): API-only management ===

# Bottlerocket has no shell access by default!
# Managed via API:
apiclient get /
# {
#   "os": {"version": "1.15.0"},
#   "settings": {...}
# }

# Update Bottlerocket node: via SSM Session Manager (no SSH):
aws ssm start-session --target i-0abc123...
# (enters admin container - limited access)

# Or via Kubernetes update operator:
# Bottlerocket Update Operator watches for new versions
# Drains node -> updates -> reboots -> rejoins cluster

# === Talos Linux: Kubernetes OS, no SSH ===

# Talos has NO SSH, NO shell, NO package manager
# Configured entirely via API (talosctl)

talosctl get nodes --nodes 192.168.1.100
# NODE            HOSTNAME  TYPE    READY
# 192.168.1.100   worker1   worker  true

# Apply new configuration:
talosctl apply-config --nodes 192.168.1.100 --file worker.yaml

# Upgrade Talos:
talosctl upgrade --nodes 192.168.1.100 --image ghcr.io/siderolabs/talos:v1.6.0
# Drains node, upgrades, reboots

# Check current version:
talosctl version --nodes 192.168.1.100
# Tag:  v1.6.0  Commit: abc123
```

---

### First Principles

```
WHY traditional OS management breaks at scale:

Traditional OS management model:
  1. Install OS (known state)
  2. Apply patches, install packages (state drifts)
  3. Edit config files (more drift)
  4. "Fix" production issues with ad-hoc commands (even more drift)
  5. After 2 years: state is unknowable without full audit
  
  "But we have Ansible!" - Ansible can CONVERGE state but:
  a. Convergence requires defining desired state for EVERY possible change
  b. Ansible can't undo unknown ad-hoc changes
  c. Idempotency is aspirational, not guaranteed (complex playbooks drift)
  d. Ansible itself must be versioned and managed (turtles all the way down)

THE INSIGHT: If the root filesystem is READ-ONLY, drift is physically impossible:
  
  Immutable OS design:
  - Root filesystem (/) mounted read-only at boot
  - Only specific paths writable: /var (data), /etc/hosts, /tmp
  - ALL changes require: (1) build new OS image, (2) deploy atomically
  
  State model:
  OLD: "server state = OS packages + all interactive changes ever made"
  NEW: "server state = git commit hash" (fully reproducible, fully auditable)

How ostree achieves this:

  ostree = content-addressed object store for filesystems
  
  Each file stored by SHA256 hash:
  Object store: /sysroot/ostree/objects/
    ab/cdef123...  <- file with hash abcdef123...
    
  Filesystem tree = tree of references:
  Commit -> tree -> subtrees -> file hashes
  
  Identical files across deployments: stored ONCE
  (like git dedup: multiple commits referencing same unchanged file)
  
  Deployment switch = update a symlink:
  /ostree/deploy/fedora-coreos/current -> deploy/abc123.0
  Changed to:
  /ostree/deploy/fedora-coreos/current -> deploy/def456.0
  
  This symlink switch is atomic (single rename syscall)
  Result: either old OR new deployment active, never in-between state
  
  If new deployment fails to boot:
  Bootloader counts boot attempts per deployment
  GRUB: "if bootcount > 2: load fallback deployment"
  systemd-boot: similar mechanism
  No manual intervention needed for rollback!

WHY A/B partition is simpler but less flexible than ostree:

  A/B partitions:
  Partition A: current OS (running)
  Partition B: next OS (installing)
  
  Update:
  1. Write new OS image to partition B (while A is running)
  2. Reboot: bootloader switches to B
  3. If B boots: mark B as "good," B is new current
  4. If B fails: bootloader falls back to A (automatic)
  
  Simple and reliable: used by Android, Chrome OS, Bottlerocket
  
  Limitation: always exactly 2 deployments
  Cannot keep deployment history, cannot do incremental updates
  Entire OS image written on every update (vs ostree deduplication)
  
  ostree advantage: can keep 3+ deployments (rollback to any of last N)
  Delta updates: only download changed files (git-like)

READ-ONLY rootfs implementation:

  /: read-only mount (overlayfs or direct read-only mount)
  
  Writable paths (specific exceptions):
  /var -> persistent data (container storage, logs, databases)
  /tmp -> temp files (tmpfs, cleared on reboot)
  /run -> runtime state (tmpfs, cleared on reboot)
  /etc -> configuration (special: ostree uses 3-way merge on updates!)
  
  /etc 3-way merge in ostree:
  Problem: /etc has OS defaults (in ostree) + user customizations
  Merge strategy:
  base: original /etc from old OS commit
  user: changes made by user/Ignition/cloud-init
  target: new /etc from new OS commit
  Result: user changes PRESERVED, OS changes APPLIED, conflicts flagged
```

---

### Thought Experiment

Migrating a traditional Linux fleet to immutable infrastructure:

```bash
# === Fedora CoreOS provisioning with Butane/Ignition ===

# Traditional: SSH, run commands, install packages
# Immutable CoreOS: provision with Ignition config (JSON), applied at first boot ONLY

# Write Butane config (human-readable YAML):
cat node-config.yaml
# variant: fcos
# version: 1.5.0
#
# passwd:
#   users:
#     - name: core
#       groups: [sudo, docker]
#       ssh_authorized_keys:
#         - ssh-rsa AAAA... admin@company.com
#
# storage:
#   files:
#     - path: /etc/hostname
#       contents:
#         inline: worker-node-01
#     - path: /etc/containers/systemd/my-app.container
#       contents:
#         inline: |
#           [Container]
#           Image=myapp:v1.2.3
#           PublishPort=8080:8080
#           Environment=DATABASE_URL=postgresql://...
#           [Service]
#           Restart=always
#           [Install]
#           WantedBy=multi-user.target
#
# systemd:
#   units:
#     - name: my-app.service
#       enabled: true

# Compile Butane to Ignition JSON:
butane --strict node-config.yaml > node.ign

# Provision: pass node.ign to cloud-init or VMware vSphere or bare metal PXE
# At first boot: Ignition reads node.ign, configures system ONCE
# After that: system is IMMUTABLE (Ignition never runs again)

# === Day 2 operations: updating applications ===

# Application updates do NOT require OS changes:
# Update .container file in /etc/containers/systemd/
# systemd --user daemon-reload
# Container pulls new image, restarts service

# OS layer updates (kernel, base OS, drivers):
rpm-ostree rebase fedora-coreos:fedora/x86_64/stable

# OR: Zincati (CoreOS auto-updater) handles this automatically:
cat /etc/zincati/config.d/90-updates.toml
# [updates]
# enabled = true
# strategy = "periodic"
#
# [updates.periodic]
# time_zone = "UTC"
# [[updates.periodic.window]]
# days = [ "Sat", "Sun" ]
# start_time = "22:00"  <- only update Saturday/Sunday nights
# length_minutes = 120

# Zincati:
# 1. Checks for new Fedora CoreOS release
# 2. Downloads atomically (rpm-ostree)
# 3. Reboots (coordinated with control plane - one node at a time)
# 4. If reboot fails: auto-rollback

# === NixOS: declarative configuration ===

# NixOS takes immutability further: the ENTIRE system configuration
# (installed packages, systemd units, kernel params) in one file

cat /etc/nixos/configuration.nix
# { config, pkgs, ... }:
# {
#   # Kernel version:
#   boot.kernelPackages = pkgs.linuxPackages_6_6;
#   
#   # Packages installed:
#   environment.systemPackages = with pkgs; [
#     htop vim curl git
#   ];
#   
#   # Services enabled:
#   services.nginx.enable = true;
#   services.postgresql.enable = true;
#   services.postgresql.package = pkgs.postgresql_15;
#   
#   # SSH:
#   services.openssh.enable = true;
#   users.users.admin.openssh.authorizedKeys.keys = [
#     "ssh-rsa AAAA..."
#   ];
# }

# Apply configuration:
nixos-rebuild switch
# Builds new system configuration
# Atomically switches (symlinks /run/current-system)
# Old generation available for rollback

# List generations:
nix-env --list-generations --profile /nix/var/nix/profiles/system
# 100 2024-01-01 10:00:00
# 101 2024-01-15 14:30:00  (current)

# Rollback:
nixos-rebuild switch --rollback
# OR: at boot: select previous generation in bootloader
```

---

### Mental Model / Analogy

```
Traditional OS management = ship undergoing constant repairs at sea:

Ship = Linux server
Crew making repairs = engineers SSHing and making changes
State: ship + every repair ever made + every improvisation + every workaround
After 5 years: nobody knows the exact state of the ship
When something breaks: "which of the 500 repairs caused this?"
Rollback: "undo the last repair" = very hard if repairs were interleaved

Immutable OS = naval vessel with standardized replacement parts:

Instead of repairing at sea: sail to dry dock (deploy new instance)
Replace ENTIRE component (OS deployment) not individual parts
Every vessel of same class has IDENTICAL configuration
Problem: swap the vessel out from the fleet

ostree = naval vessel registry with git-like versioning:
  Every vessel configuration stored by hash
  "Version ABC123": every ship with this ID has identical OS state
  Deploy new version: swap out one vessel at a time
  Rollback: bring back vessel version ABC122 from storage

A/B partitions = ship with two engines:
  Engine A: current (running)
  Engine B: maintenance/staging
  Update: fix engine B while A is running
  Switch: if B works, use B; if B fails, continue with A

Ignition/cloud-init = ship commissioning document:
  Document defines exact configuration at launch
  Read ONCE at commissioning, never changed
  If you need different config: commission a new ship (new instance)

/var = ship's cargo hold (writable, persistent):
  OS is the hull (immutable)
  Cargo (application data, logs) lives in the hold
  New OS version = new hull, same cargo
  Update doesn't affect cargo

Zincati = fleet maintenance coordinator:
  "All vessels will receive engine update during weekend maintenance window"
  "One vessel at a time: wait for vessel to rejoin fleet before updating next"
  "If vessel fails to restart after update: automatic revert to previous engine"
```

---

### Gradual Depth - Five Levels

**Level 1:**
What "immutable" means for OS: read-only root filesystem. Why: prevents
configuration drift. A/B partition concept. The trade-off: flexibility vs
consistency. Use cases: container host nodes (CoreOS, Bottlerocket), Kubernetes
nodes (Talos), edge devices.

**Level 2:**
ostree: git-for-OS concept, content-addressed storage, atomic deployment switch.
rpm-ostree: package management for CoreOS. Fedora CoreOS: container-optimized,
Ignition for provisioning. Bottlerocket: AWS container host, API-managed. Talos:
no SSH, full API control. NixOS: declarative OS. Rollback mechanisms.

**Level 3:**
Ignition config format (Butane + compile to JSON). Zincati auto-updater and
update strategies. ostree delta updates: only transfer changed files. /etc
3-way merge in ostree (how user config changes survive OS updates). Layered
packages in rpm-ostree (rpm-ostree install: creates overlay). Container-native
application delivery (Quadlet, systemd container units in CoreOS).

**Level 4:**
ostree internals: object store, commit graph, refs. Building custom ostree
images (osbuild, COSA - CoreOS Assembler). NixOS flakes for reproducible
configurations across machines. Fedora CoreOS/RHCOS in Kubernetes (OpenShift
RHCOS automatic cluster upgrade coordination). Bottlerocket ECS/EKS
integration and update operator. Talos API surface: machine config, certificates.

**Level 5:**
ostree as base for RPM-OSTree, Flatpak, and Snap (convergence of technology).
Image-based OS design philosophy: GNOME OS, Steam Deck SteamOS as consumer
immutable Linux. Cross-architecture immutable builds (x86_64, ARM64, RISC-V).
Air-gapped fleet management with ostree mirrors. Security analysis: immutable
OS prevents persistent malware (rootkits) but what about /var? eBPF for
runtime integrity checking on immutable hosts. OSTree in embedded Linux
(Automotive Grade Linux uses ostree for OTA vehicle updates).

---

### Code Example

**BAD - traditional mutable OS management that creates drift:**
```bash
# BAD: Ad-hoc server management that creates untracked state

# Engineer 1 SSHs to server, installs debugging tool:
ssh server-01
sudo yum install -y strace  # now on server-01, not on server-02-500

# Engineer 2 "fixes" a config:
sudo vim /etc/systemd/system/myapp.service  # untracked change
sudo systemctl daemon-reload
sudo systemctl restart myapp

# Engineer 3 applies "temporary" workaround:
sudo sysctl -w net.ipv4.tcp_tw_reuse=1  # not in /etc/sysctl.conf
# Lost after reboot... but someone will "fix" it again manually

# Six months later: server-01 has strace, unique systemd config,
# different sysctl settings, plus 47 other untracked changes
# Server-01 != Server-02 != Server-03... 
# "Why does the app work on server-02 but not server-01?"
# Answer: unknown (no one knows the full diff)
```

```yaml
# GOOD: Immutable CoreOS with Butane/Ignition - 
# all configuration is declarative and version-controlled

# butane-config.yaml (store in git)
variant: fcos
version: 1.5.0

storage:
  # System configuration via files (not ad-hoc SSH commands):
  files:
    - path: /etc/sysctl.d/99-custom.conf
      mode: 0644
      contents:
        inline: |
          net.ipv4.tcp_tw_reuse = 1
          vm.max_map_count = 262144
    
    # Application container defined declaratively:
    - path: /etc/containers/systemd/myapp.container
      contents:
        inline: |
          [Container]
          Image=myapp:v2.1.0@sha256:abc...
          PublishPort=8080:8080
          Volume=/var/data/myapp:/data
          [Service]
          Restart=always

systemd:
  units:
    # Enable the container unit:
    - name: myapp.service
      enabled: true

# To change: edit this file, rebuild Ignition, re-provision nodes
# OR: add to existing deployment via rpm-ostree:
# rpm-ostree install strace
# (creates NEW deployment, not in-place modification)
# (recorded in ostree commit history - always auditable)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Immutable OS means you can't install software or change configuration" | Immutable OS means you cannot modify the base OS layer at runtime. But: (1) Applications are delivered as containers (the whole point - containers run on top of the read-only OS), (2) rpm-ostree install <package> creates a new OS deployment (with package added) that activates on next reboot, (3) NixOS's `nix-shell -p htop` provides a temporary environment with htop without modifying the system, (4) Writable paths (/var, /etc) allow data and configuration changes, (5) Ignition/cloud-init configure the system at first boot. The constraint is: OS changes require a new deployment/reboot, not runtime package installs (which create drift). This forces discipline: application requirements are explicitly declared, not accumulated ad-hoc. |
| "Immutable OS makes debugging harder because you can't install debug tools" | For Container-based workloads, debugging tools can be run as containers: `kubectl debug -it <pod> --image=busybox` or `crictl run debug:latest`. For host-level debugging: `toolbox` (Fedora CoreOS feature) starts a privileged container with full package management access (dnf, yum) without modifying the host OS. Toolbox gives a mutable shell on an immutable host, mounted to host namespaces for debugging. Bottlerocket: admin container provides a privileged shell. Talos: `talosctl dmesg`, `talosctl logs`, `talosctl inspect` provide diagnostic data without shell. The actual debugging experience with modern tooling is often BETTER than traditional: logs are centralized (no ssh-to-each-node), crashloops auto-restart, tracing tools work via eBPF without installation. |
| "Atomic updates always guarantee successful rollback" | Automatic rollback requires a successful boot before declaring the update successful. Rollback happens if: the system doesn't reach its target boot state (systemd fails, essential services don't start). But: (1) If the new OS boots successfully but application data is corrupted by the new version (database schema incompatibility), rollback to old OS won't fix the data corruption. (2) If the update changes the format of /var data (e.g., database format upgrade), rolling back the OS may leave the data in a format the old OS can't read. (3) Firmware/BIOS bugs may prevent rollback at hardware level. True reliable rollback requires: application-level version compatibility (backward/forward compatibility), data migration strategies, and stateful component (database) version pinning separate from OS versioning. |
| "Immutable infrastructure means servers never need patching (just rebuild)" | Immutable doesn't eliminate security patching - it changes HOW you patch. Instead of: `yum update --security` on each server (in-place). You: build a new OS image with the security patch, deploy the image to all nodes (atomic rollout). The security patch cadence can actually be FASTER with immutable infrastructure: a new image can be rolled out to 1000 nodes in 30 minutes with coordinated rolling reboot, vs manually SSHing to patch each node. Live kernel patching (kpatch on RHEL, livepatch on Ubuntu) is an option for critical CVEs requiring immediate response without reboot - but this is a temporary measure until the full OS image update can be deployed. Immutable infrastructure improves patch compliance because: every node running the same commit hash is patched to the same level - no drifted nodes that missed a patch. |

---

### Failure Modes & Diagnosis

```bash
# === Failure: rpm-ostree update gets stuck ===
# 'rpm-ostree upgrade' hangs or fails with lock error

# Check status:
rpm-ostree status
# State: busy  <- stuck in transaction!

# Check what's holding the lock:
systemctl status rpm-ostreed
# rpm-ostreed: Active (running)
# Is it actually doing something? Check logs:
journalctl -u rpm-ostreed -n 50 --no-pager

# Force cancel (if safe):
rpm-ostree cancel

# If stuck due to corrupt transaction:
# Check pending deployment:
ls -la /sysroot/ostree/repo/state/
# Remove partial transaction:
rpm-ostree cleanup --pending

# === Failure: Node stuck in boot loop after update ===
# Bottlerocket/CoreOS node reboots after update but keeps cycling

# On Fedora CoreOS: check boot entries:
# At GRUB menu: two entries visible
# One should be marked "bad" if auto-rollback triggered

# From running node (after it falls back to old deployment):
rpm-ostree status
# State: idle
# Deployments:
#   fedora-coreos (bad, attempted)  <- new deployment, marked bad
# * fedora-coreos (current, rolled back)  <- old deployment, restored

# See boot failure reason:
journalctl -b -1 -p err  # errors from PREVIOUS boot
# (The failed boot's journal is preserved)

# Fix the issue in new deployment, or:
rpm-ostree rollback --reboot  # explicitly rollback (removes bad deployment)

# === Failure: Application can't write to filesystem ===
# App fails with "read-only file system" error

# Check which path:
# /etc/: some files writable (provisioned by Ignition), some not
# /usr/: read-only (OS files)
# /var/: should be writable

# Check if /var is mounted correctly:
mount | grep /var
# /dev/sda4 on /var type xfs (rw,...)  <- should be rw

# If app writes to /usr/local/: WRONG! Must use /var/
# Fix: configure app to use /var/data/ or /home/ for writable data

# Check SELinux context (CoreOS has SELinux enforcing):
ls -laZ /var/data/myapp/
# If SELinux context is wrong: container can't access it
ausearch -m avc -ts today | grep denied | head -20

# Fix SELinux context:
chcon -R -t container_file_t /var/data/myapp/
```

---

### Related Keywords

**Foundational:**
LNX-053 (filesystems), LNX-106 (containers)

**Builds on this:**
LNX-108 (multi-tenant security)

**Related:**
LNX-108 (multi-tenant security)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `rpm-ostree status` | Show current and pending deployments |
| `rpm-ostree upgrade` | Download and stage OS update |
| `rpm-ostree rollback` | Rollback to previous deployment |
| `rpm-ostree install <pkg>` | Add package to new deployment layer |
| `rpm-ostree cleanup --pending` | Remove pending (unstaged) deployment |
| `butane --strict config.yaml > ignition.json` | Compile Butane to Ignition |
| `toolbox enter` | Enter mutable debugging container on CoreOS |
| `talosctl upgrade --nodes <ip> --image <ref>` | Upgrade Talos node |

**3 things to remember:**
1. The root filesystem (/) is read-only; /var is writable. Applications and container data must live in /var. OS changes (package installs, config changes) require a new deployment that activates on reboot - they NEVER modify the running system.
2. Rollback is atomic and automatic. If a new deployment fails to boot (doesn't reach boot target), the bootloader automatically falls back to the previous deployment. No manual intervention required, and the previous deployment's state is always preserved.
3. Immutable OS eliminates configuration drift by making drift physically impossible. If two nodes have the same ostree commit hash, they have identical OS state - not "probably similar," literally identical, provably so by hash comparison.

---

### Transferable Wisdom

Immutable infrastructure philosophy transfers to: immutable deployment artifacts
in software (Docker images tagged by digest, not mutable tags; Lambda function
versions; Kubernetes ConfigMap immutability flag), database migration strategy
(forward-only migrations, never "fix" data in place), Terraform/Pulumi
infrastructure (define desired state, let tool reconcile, never manually edit
cloud resources), functional programming (pure functions, immutable data structures
- same correctness guarantee: given same inputs, same outputs, no side effects).
The ostree content-addressed model is identical to: git object store, content-
addressed storage (IPFS, Docker image layers), Nix/Guix functional package
management. A/B deployment pattern is used in: application deployment (blue-green,
canary), Android system updates, Chrome OS updates, automotive ECU firmware
updates (OTA). The "cattle not pets" philosophy (replace, don't repair) extends to:
Kubernetes pod lifecycle (pods are ephemeral, replace don't repair), microservice
instances (restart on failure, not patch), cloud instance replacement (auto-scaling
groups replacing unhealthy instances automatically). The NixOS declarative model
maps to: Kubernetes declarative API (desired state, controller reconciles),
Ansible idempotent playbooks, Terraform providers.

---

### The Surprising Truth

Immutable infrastructure was popularized for SERVERS by the "cattle not pets"
concept from Randy Bias (2012) and the containers wave (2014+). But the concept
is much older and most pervasive in consumer devices: every iPhone update
installs a complete, cryptographically signed, read-only OS image to the inactive
partition while the current OS runs. Android has had A/B updates since Android
7.0 (2016). Chromebooks have had immutable, auto-updating OS since 2011.

The irony: consumer devices (billions of them) had robust immutable OS updates
for a decade while enterprise Linux servers were still SSH-and-patch. The
complexity that enterprise Linux brought (thousands of package permutations,
ad-hoc configuration, manual state) was never necessary. Consumer device vendors
forced simplicity because user-visible failures are unacceptable. Enterprise
Linux is now converging on the same model (CoreOS, Bottlerocket, Talos) that
consumer devices implemented a decade earlier - because reliability requirements
at scale demand it.

---

### Mastery Checklist

- [ ] Understands why immutable OS prevents configuration drift and when it matters
- [ ] Can explain ostree's model (content-addressed, atomic switch, rollback)
- [ ] Knows the difference between Fedora CoreOS, Bottlerocket, and Talos Linux use cases
- [ ] Understands what IS writable on an immutable OS (/var, /tmp, /run) and why
- [ ] Can reason about the trade-offs: immutable OS vs traditional mutable Linux for different workload types

---

### Think About This

1. Your organization runs 2000 Kubernetes worker nodes on traditional Ubuntu
   VMs. The current patch process: Ansible runs `apt upgrade` on 50 nodes
   per night. It takes 5 weeks to fully patch the fleet, and you regularly
   find nodes that drifted (SSH key changes, manual config modifications).
   Design a migration plan to Fedora CoreOS or Bottlerocket. What are the
   challenges of migrating stateful services? How do you handle applications
   that currently write to /usr/local? What is your rollback plan if CoreOS
   is incompatible with an application?

2. Security team identifies a critical kernel CVE affecting all 2000 nodes.
   The CVE is being actively exploited in the wild. The proper fix requires
   a kernel update (reboot required). Using kpatch for live patching vs
   rolling reboot on immutable OS nodes - compare the approaches. For
   immutable infrastructure: what is the fastest path from "CVE announced"
   to "all 2000 nodes patched"? What metrics would you monitor during the
   rolling update to detect any nodes that failed to upgrade?

3. NixOS's declarative model (entire OS state described in configuration.nix)
   is philosophically similar to Kubernetes' declarative API (desired state
   in YAML). Both use a "reconciler" that converges actual state toward desired
   state. But there's a fundamental difference: NixOS applies the entire
   configuration atomically at once (rebuild + switch), while Kubernetes
   applies changes incrementally. What are the implications of each approach
   for correctness, debuggability, and failure handling? When would you prefer
   atomic all-or-nothing configuration vs incremental convergence?

---

### Interview Deep-Dive

**Foundational:**
Q: What is immutable infrastructure and why does it solve configuration drift?
A: DEFINITION: Immutable infrastructure is a model where servers (or OS deployments) are never modified after initial provisioning. To make changes: build a new artifact (OS image, container image), deploy it, retire the old version. The key property: if two servers have the same artifact ID (ostree commit hash, AMI ID, container image digest), they are IDENTICAL - not approximately the same, provably identical. CONFIGURATION DRIFT PROBLEM: In traditional Linux management, servers accumulate changes over time: (1) Package updates applied on different days to different servers (different library versions). (2) Engineers SSH to "fix" production issues with ad-hoc commands (state not recorded). (3) Configuration management tools (Ansible, Chef) run idempotent playbooks but: complex playbooks have bugs, new playbook runs may not fix all state from previous runs, manually changed files that Ansible doesn't manage remain drifted. Result: server #127 is "slightly different" from server #128-500 in ways that only matter when something fails. IMMUTABLE SOLUTION: If the root filesystem is read-only (mounted read-only at boot), drift is physically impossible. An engineer cannot `vim /etc/hosts` (read-only). An engineer cannot `yum install strace` and have it persist (or it goes into a new deployment, tracked in ostree commit). OSTREE MECHANISM: ostree is a content-addressed object store for filesystems. Each deployment is a commit (SHA256 hash) referencing a specific filesystem tree. Switching deployments = updating a symlink (atomic). If the new deployment fails to boot: bootloader automatically falls back to previous deployment. PRACTICAL BENEFIT: "What version of the OS is running on all 2000 nodes?" becomes answerable by a single API call (all should return the same commit hash). "Why does node #127 behave differently?" is diagnosable: its commit hash differs from the expected value.

**Expert:**
Q: Compare Fedora CoreOS, Bottlerocket, and Talos Linux for running Kubernetes worker nodes. When would you choose each?
A: ALL THREE are immutable, container-optimized Linux distributions designed specifically for running Kubernetes workloads. They represent different points on the usability vs. security/simplicity spectrum. FEDORA COREOS: Based on rpm-ostree + FCOS ostree format. Provisioning: Ignition config (declarative JSON applied at first boot). Shell access: yes (SSH, full bash). Package installation: `rpm-ostree install <pkg>` (creates new deployment). Updates: Zincati auto-updater, atomic rolling reboots. Debugging: full shell + toolbox for privileged container. Use when: migrating from traditional Linux (familiar tools), need to install custom packages or daemons, want flexibility with stability. Community-supported (Red Hat controls CoreOS). BOTTLEROCKET: Amazon's container host OS. Based on A/B partition model. Provisioning: user-data (toml config) applied at boot. Shell access: NO default SSH - managed via SSM Session Manager or admin container. Package installation: NOT supported (immutable, API-only). Updates: Bottlerocket Update Operator (BUE) for EKS, automated. Debugging: admin container (limited shell). Use when: running EKS on AWS, want maximum simplicity, Amazon-managed security patching, willing to trade flexibility for manageability. TALOS LINUX: Kubernetes-specific OS, most security-hardened. NO shell at all (no SSH, no bash, no shell access). Full API: all management via talosctl. Provisioning: machine config YAML applied via API. Updates: atomic API-driven, managed by Talos API. Debugging: API-only (talosctl logs, talosctl inspect). Use when: highest security requirements (no shell = no shell-based attack vector), treating nodes as truly cattle (all operations via Kubernetes API or Talos API), GitOps-first environment, okay with talosctl learning curve. DECISION MATRIX: AWS EKS? -> Bottlerocket. Maximum security/lockdown? -> Talos. Migration from traditional Linux, need flexibility? -> CoreOS. On-premises with Red Hat support? -> RHCOS (Red Hat CoreOS, same technology, subscription support). All three eliminate drift, provide atomic updates, and reduce attack surface compared to Ubuntu/CentOS. The differences are operational model (SSH vs API) and ecosystem (AWS-native vs CNCF vs Fedora).
