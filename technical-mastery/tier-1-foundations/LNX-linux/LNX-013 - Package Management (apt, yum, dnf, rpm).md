---
id: LNX-013
title: "Package Management (apt, yum, dnf, rpm)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006
used_by: LNX-031, LNX-048
related: LNX-061, LNX-031, CTR-001
tags: [apt, yum, dnf, rpm, package-management, debian, redhat, repositories]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/lnx/package-management/
---

## TL;DR

Package managers install, update, and remove software. Debian/Ubuntu
use `apt` (`.deb` packages). RHEL/CentOS/Rocky use `dnf`/`yum`
(`.rpm` packages). They resolve dependencies automatically, fetch from
repositories, and verify integrity via GPG signatures. In containers:
`apt-get install -y --no-install-recommends` is the standard pattern.
Package manager choice is determined by your Linux distribution.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-013 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | apt, yum, dnf, rpm, packages, Debian, RHEL, repositories |
| **Prerequisites** | LNX-006 |

---

### The Problem This Solves

Installing software manually: download tarball, extract, compile,
handle missing dependencies, repeat for each dependency, ensure
correct version for the OS, manage updates. Multiply by 50 servers.
This is error-prone and slow. Package managers automate the entire
process: dependency resolution, download, integrity verification,
installation, and updates. They also provide a consistent uninstall
path (no leftover files).

---

### Textbook Definition

A **package manager** is a tool that automates: (1) locating software
in remote repositories, (2) verifying integrity via GPG signatures,
(3) resolving and installing dependencies, (4) tracking installed
packages for update and removal. A **package** is a compressed archive
(.deb or .rpm) containing: binaries, libraries, config files, metadata
(name, version, dependencies), and pre/post-install scripts.

Two major ecosystems:
- **Debian/Ubuntu (APT ecosystem)**: apt, apt-get, dpkg, .deb packages
- **Red Hat/CentOS/RHEL/Fedora (RPM ecosystem)**: dnf, yum, rpm, .rpm packages

---

### Understand It in 30 Seconds

```bash
# DEBIAN/UBUNTU (apt):
apt update               # refresh package list from repos
apt install nginx        # install nginx
apt remove nginx         # remove nginx
apt upgrade              # upgrade all installed packages
apt search nginx         # search for nginx package
apt show nginx           # show package details and dependencies
dpkg -l                  # list all installed packages
dpkg -l | grep nginx     # check if nginx is installed

# RHEL/CENTOS/ROCKY (dnf, modern replacement for yum):
dnf update               # refresh metadata and show updates
dnf install nginx        # install nginx
dnf remove nginx         # remove nginx
dnf upgrade              # upgrade all packages
dnf search nginx         # search
dnf info nginx           # show details and dependencies
rpm -qa                  # list all installed packages
rpm -qa | grep nginx     # check if nginx is installed

# One-liner equivalents:
# Ubuntu:  apt install -y nginx
# RHEL:    dnf install -y nginx
```

---

### First Principles

**Repositories:**
Package managers don't download from arbitrary URLs. They fetch from
**repositories** - curated collections of packages. Repository
definitions:
- Ubuntu: `/etc/apt/sources.list` and `/etc/apt/sources.list.d/*.list`
- RHEL: `/etc/yum.repos.d/*.repo`

GPG signature verification: every package is signed. apt/dnf verify
the signature before installing. If signature doesn't match, installation
is refused. This prevents supply chain attacks via compromised mirrors.

**Dependency resolution:**
`apt install myapp` also installs: libssl3, python3-minimal, and 15
other packages that myapp depends on. The package manager reads the
dependency metadata and resolves the full dependency tree.
SAT solver (apt uses aptitude's SAT solver): finds the set of package
versions that satisfies all constraints (version ranges, conflicts).

---

### Thought Experiment

You need OpenSSL on 100 servers. Manual approach: download OpenSSL
source, check version compatibility with your OS libraries, compile
with correct flags, distribute the binary, handle library paths.
6 hours for the first server. 100 hours total (or you write automation).
Update next month: repeat.

With a package manager: `apt install openssl` on all 100 servers.
Done in 2 minutes (concurrent via Ansible). Update: `apt upgrade openssl`.
Same package, tested against your OS version, dependencies resolved,
config migration handled by package scripts.

This is why package managers are foundational to Linux administration
and why every Dockerfile starts with `apt-get update && apt-get install`.

---

### Mental Model / Analogy

Package management is like an **app store** but for server software:

```
Repository = app store catalog
  (curated, versioned, signed packages for your OS version)
  
apt install nginx = "buy and install nginx from the app store"
  (resolves: nginx needs libpcre3, openssl - installs those too)
  
apt update = "refresh the app store catalog"
  (download the latest list of available versions)
  
apt upgrade = "update all installed apps to latest versions"
  (like iOS "update all" button)
  
dpkg = "app installed on THIS device" (local package database)
apt = "app store client" (remote + local)
```

---

### Gradual Depth - Five Levels

**Level 1:**
apt/dnf installs software. Always run `apt update` before `apt install`
to get the latest package lists. apt for Debian/Ubuntu. dnf for RHEL/Fedora.
In Dockerfiles: combine update + install in one RUN to avoid stale
cache layers.

**Level 2:**
Add third-party repositories: `add-apt-repository ppa:deadsnakes/ppa`
(Ubuntu PPA). Import GPG key: `curl -fsSL https://packages.redis.io/gpg | gpg --dearmor > /etc/apt/keyrings/redis.gpg`. Then add repo definition. This is how you install software not in the official repos (Docker, Node.js, Redis, MongoDB all provide their own repos).

**Level 3:**
apt pinning: hold packages at specific versions to prevent
unintended upgrades. `apt-mark hold nginx`. Check held packages:
`apt-mark showhold`. For RHEL: `dnf versionlock add nginx`.
Package cache management: `/var/cache/apt/archives/` stores downloaded .debs.
`apt clean` removes cached packages. `apt autoremove` removes unused
dependency packages (important for disk space management).

**Level 4:**
Package internals: .deb is an ar archive containing control.tar.gz
(metadata, scripts) and data.tar.gz (actual files). dpkg --extract
unpacks without installing. Package scripts: preinst, postinst, prerm,
postrm run at installation/removal phases. APT pinning priorities:
`/etc/apt/preferences.d/` overrides version selection.
Local package installation: `dpkg -i package.deb` (no dependency
resolution - use apt for that).

**Level 5:**
Custom package repositories: create your own Debian repo with
reprepro or aptly for internal artifact distribution. Sign with
your GPG key. Internal Yum/DNF repos with createrepo. This is how
enterprises distribute internal software packages at scale. Package
build: `debbuild` for .deb, `rpmbuild` for .rpm - builds packages from
source with spec files. Immutable infrastructure: instead of
`apt upgrade` on running servers, bake updated packages into a new
AMI/container image and replace instances.

---

### Code Example

**BAD - common Dockerfile mistakes:**
```dockerfile
# BAD 1: apt update in separate layer - stale cache bug
RUN apt-get update
RUN apt-get install -y nginx  # uses cached (possibly stale) list!

# BAD 2: no --no-install-recommends - bloats image size
RUN apt-get update && apt-get install -y python3
# Installs 50+ recommended packages you don't need

# BAD 3: leaving apt cache in image - wastes space
RUN apt-get update && apt-get install -y nginx
# /var/cache/apt/archives/*.deb still in the layer!

# BAD 4: installing unnecessary packages in production
RUN apt-get install -y build-essential gcc python3-dev
# These are build tools - not needed in final production image
```

**GOOD - correct Dockerfile pattern:**
```dockerfile
# GOOD: single RUN layer with cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nginx=1.22.* \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# GOOD: pin versions for reproducible builds
# nginx=1.22.* - matches any 1.22.x version
# curl         - any version (less critical)

# GOOD: multi-stage build to separate build and runtime
FROM ubuntu:22.04 AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc build-essential && \
    rm -rf /var/lib/apt/lists/*
# ... build your app ...

FROM ubuntu:22.04 AS runtime
# ONLY runtime dependencies, not build tools:
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libssl3 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/myapp /usr/local/bin/myapp
```

```bash
# GOOD: host package management best practices
# Always update metadata before installing:
apt-get update && apt-get install -y nginx

# Check what would be installed (dry run):
apt-get install --dry-run nginx

# Install specific version (for reproducibility):
apt-get install -y nginx=1.22.0-1ubuntu3

# Hold a package at current version:
apt-mark hold nginx
# Remove hold:
apt-mark unhold nginx

# Check which package provides a file:
dpkg -S /usr/sbin/nginx   # -> nginx: /usr/sbin/nginx
# (useful when error says: "library libssl.so.3 not found")
# Or for not-yet-installed packages:
apt-file search libssl.so.3
```

---

### Comparison Table

| Feature | apt (Debian/Ubuntu) | dnf/yum (RHEL/CentOS) |
|---------|--------------------|-----------------------|
| Install | `apt install pkg` | `dnf install pkg` |
| Remove | `apt remove pkg` | `dnf remove pkg` |
| Update list | `apt update` | `dnf check-update` |
| Upgrade all | `apt upgrade` | `dnf upgrade` |
| Search | `apt search pkg` | `dnf search pkg` |
| Info | `apt show pkg` | `dnf info pkg` |
| List installed | `dpkg -l` | `rpm -qa` |
| Low-level | dpkg | rpm |
| Repo config | /etc/apt/sources.list.d/ | /etc/yum.repos.d/ |
| Cache dir | /var/cache/apt/ | /var/cache/dnf/ |
| Log | /var/log/apt/ | /var/log/dnf.log |
| Package format | .deb | .rpm |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "apt update upgrades packages" | `apt update` only refreshes the package index (what's available). `apt upgrade` actually upgrades installed packages. Always run update before install/upgrade. |
| "dpkg and apt are the same" | dpkg is the low-level package manager (installs .deb files directly, no dependency resolution). apt is the high-level tool (uses dpkg + handles dependencies + manages repos). |
| "Package from source is better than package manager" | Compile-from-source means: you're responsible for security patches, library compatibility, and uninstallation. Package manager packages are tested against your OS version, auto-updated, and tracked for removal. |
| "yum and dnf are the same" | dnf replaced yum in RHEL 8/Fedora 22+. dnf has better dependency resolution (SAT solver), better performance, and proper Python 3 support. yum is a compatibility wrapper around dnf on modern RHEL. |
| "apt install is idempotent" | Nearly: if the package is already installed at the requested version, apt does nothing. But NOT fully idempotent if you specify no version (upgrading existing). Use configuration management (Ansible, Chef) for true idempotency. |

---

### Failure Modes & Diagnosis

**E: Unable to locate package (common in Docker):**
```bash
# Error: E: Unable to locate package mypackage
# Cause 1: didn't run apt update first
apt-get update
apt-get install mypackage

# Cause 2: wrong Ubuntu version / package name changed
apt search nginx   # find the correct package name

# Cause 3: package in a repo that's not configured
# Example: Docker requires Docker's own repo:
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor > /etc/apt/keyrings/docker.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu focal stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install docker-ce
```

**Broken package database:**
```bash
# Error: dpkg: error processing package ... (interrupted installation)
# Fix:
dpkg --configure -a    # finish interrupted configurations
apt-get install -f     # fix broken dependencies

# Nuclear option (last resort):
apt-get clean          # clear package cache
apt-get update
apt-get dist-upgrade   # upgrade with dependency resolution
```

**Security: GPG key expiration:**
```bash
# Warning: NO_PUBKEY B1998361219BD9C9
# Package install blocked because GPG key expired/missing

# Diagnosis:
apt-key list           # list imported GPG keys

# Fix: re-import the key for the repository
curl -fsSL https://packages.example.com/gpg.key \
  | gpg --dearmor > /etc/apt/keyrings/example.gpg
# Update sources.list to reference the key file
# This is the signed-by= syntax in modern apt
```

---

### Related Keywords

**Foundational:**
LNX-006 (Terminal), LNX-061 (Shared Libraries)

**Builds on this:**
LNX-031 (systemd Services), LNX-048 (Boot Process)

**Related:**
CTR-001 (Containers), MVN-001 (Maven - Java package management)

---

### Quick Reference Card

| Action | Debian/Ubuntu | RHEL/CentOS/Fedora |
|--------|--------------|---------------------|
| Refresh repos | `apt update` | `dnf check-update` |
| Install | `apt install pkg` | `dnf install pkg` |
| Remove | `apt remove pkg` | `dnf remove pkg` |
| Purge (+ configs) | `apt purge pkg` | `dnf remove pkg` |
| Upgrade all | `apt upgrade` | `dnf upgrade` |
| List installed | `dpkg -l` | `rpm -qa` |
| Which package has file? | `dpkg -S /path` | `rpm -qf /path` |
| Clean cache | `apt clean` | `dnf clean all` |
| Show pkg info | `apt show pkg` | `dnf info pkg` |

**3 things to remember:**
1. `apt update` then `apt install` - always update metadata first
2. In Dockerfiles: combine update+install+cleanup in ONE RUN layer
3. --no-install-recommends keeps Docker images smaller

---

### Transferable Wisdom

Package managers are the Linux equivalent of:
- Java: Maven/Gradle (manages JAR dependencies)
- Node.js: npm/yarn (manages node_modules)
- Python: pip (manages site-packages)
- Rust: cargo (manages crates)

The core concepts are identical: (1) declare what you need,
(2) resolve the full dependency tree, (3) fetch from a trusted
registry, (4) verify integrity. The Linux package manager is the
OS-level version of the same problem that every language ecosystem
has solved independently.

**Reproducible builds** are a common challenge across all package
managers: pin exact versions (apt pin, package-lock.json, pom.xml
exact versions) to prevent "works on my machine" build differences.

---

### The Surprising Truth

When you run `apt upgrade` on a production server, it can automatically
restart running services if their libraries were updated. For example,
upgrading libssl3 (the OpenSSL library) restarts nginx, Apache, sshd,
and anything else linked against it. This is the "needrestart" behavior
(enabled by default on many Ubuntu installations). In production, this
means `apt upgrade` can cause service interruptions. Controlled upgrade
workflows: (1) upgrade during maintenance windows, (2) use `DEBIAN_FRONTEND=noninteractive` to suppress prompts, (3) check what would restart with `needrestart -r l` before upgrading, (4) prefer rolling upgrades via new container images rather than in-place package upgrades.

---

### Mastery Checklist

- [ ] Can install, update, and remove packages on both Debian and RHEL systems
- [ ] Can add a third-party repository with GPG key verification
- [ ] Can write correct Dockerfile RUN instructions for package installation
- [ ] Can diagnose and fix common package manager errors
- [ ] Can explain the difference between dpkg/rpm and apt/dnf

---

### Think About This

1. When you run `apt upgrade` on a server with a running nginx process,
   what happens? If libssl3 is upgraded, does nginx automatically use
   the new version? Or does it continue using the old version until
   restarted? What Linux mechanism determines this?

2. Your Dockerfile has `RUN apt-get install -y nginx`. Docker builds
   and caches this layer. Two weeks later, you rebuild without changing
   the Dockerfile. Will you get the same nginx version you had two weeks
   ago, or a newer one? What are the implications for production image
   reproducibility?

3. A developer says "I'll just compile OpenSSL from source - it's more
   up to date than the distro package." What are the hidden costs and
   risks of this approach compared to using the distribution's package?

**TYPE G:** Design a software distribution system for a 500-node
production cluster where: (1) all package installs must go through
an internal mirror (no direct internet access), (2) packages must be
tested before fleet-wide deployment, (3) rollback must be possible
if a package causes issues, (4) you need audit logs of who installed
what on which server. What architecture would you build on top of
the existing apt/dnf ecosystem?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between `apt update` and `apt upgrade`?
A: `apt update` downloads the package index from configured repositories - it updates the LOCAL DATABASE of what packages are available and at what versions. No packages are installed or changed. `apt upgrade` reads the local package database (updated by apt update) and upgrades installed packages to newer versions if available, while not removing any currently installed packages. `apt dist-upgrade` is more aggressive: it will also add and remove packages if needed to satisfy dependencies for upgrades. Best practice: always run `apt update` before `apt install` or `apt upgrade` to work with current package information.

**Intermediate:**
Q: Why is it important to combine `apt-get update`, `apt-get install`, and `rm -rf /var/lib/apt/lists/*` in a single Dockerfile RUN instruction?
A: Docker builds images in layers. Each RUN instruction creates a new layer. If `apt-get update` is in one layer and `apt-get install` in another, when you rebuild the Dockerfile (with the install layer changed), Docker uses the CACHED `apt-get update` layer from days/weeks ago. This means you're installing packages from a stale index and potentially get old package versions - a cache staleness bug. By combining them in a single RUN, the index is always fresh when packages are installed. The `rm -rf /var/lib/apt/lists/*` at the end removes the package index from the layer, reducing image size (the index can be 50-100MB). --no-install-recommends prevents installing recommended-but-not-required packages, further reducing image size.

**Expert:**
Q: How do enterprise teams manage package updates at scale without disrupting production, given that `apt upgrade` can restart running services?
A: The modern approach is immutable infrastructure: instead of updating packages on running servers, build new server images (AMI for EC2, container images for Kubernetes) with the updated packages. Rollout strategy: (1) build new image in CI/CD with updated packages, run automated tests; (2) stage rollout with canary (replace 5% of fleet first, monitor error rates); (3) if healthy, roll out to remaining instances (blue-green or rolling); (4) if problems, roll back by redirecting traffic to old instances. For OS-level patches on bare metal or VMs: (1) use a package mirror to test packages before they reach production; (2) configure maintenance windows in config management (Ansible/Chef); (3) use `apt-get install --only-upgrade pkg` for targeted updates; (4) use `needrestart -r l` to identify what services need restart; (5) plan service restarts during low-traffic periods. The key insight: package management and service continuity are separate concerns - treat them as such in your deployment strategy.
