---
layout: default
title: "Docker Networking Modes"
parent: "Containers"
nav_order: 851
permalink: /containers/docker-networking-modes/
number: "0851"
category: Containers
difficulty: ★★★
depends_on: Container, Docker, Container Networking, Linux Namespaces, Networking
used_by: Container Orchestration, Kubernetes Architecture, Container Security
related: Container Networking, Linux Namespaces, Kubernetes Architecture, Overlay Networks, Container Security
tags:
  - containers
  - docker
  - networking
  - advanced
  - internals
---

# 851 — Docker Networking Modes

⚡ TL;DR — Docker networking modes control how a container connects to the network — from fully isolated to sharing the host's network stack — each with distinct security and performance trade-offs.

| #851 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Container, Docker, Container Networking, Linux Namespaces, Networking | |
| **Used by:** | Container Orchestration, Kubernetes Architecture, Container Security | |
| **Related:** | Container Networking, Linux Namespaces, Kubernetes Architecture, Overlay Networks, Container Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer runs a container and wonders: "Why can't I reach my app on `localhost`? Why does my container have a different IP than my host? Why can my container reach the internet but not my other containers? Why is my container's traffic going through a NAT?" These questions all stem from not understanding Docker's network model — which provides multiple distinct modes to suit different connectivity needs.

**THE BREAKING POINT:**
The default Docker network creates network isolation that surprises developers. The host network mode provides performance but removes isolation. The wrong choice leads to security vulnerabilities (using `--network host` in production) or connectivity problems (using bridge when containers need to reference each other by name).

**THE INVENTION MOMENT:**
Docker networking modes were designed to give operators control over the network isolation vs connectivity trade-off — from complete isolation (none) to shared host networking (host), with bridge, overlay, and macvlan in between for different multi-container and multi-host scenarios.

---

### 📘 Textbook Definition

**Docker networking modes** define how a container interacts with the system's network stack. Docker provides five built-in network drivers: **bridge** (default — containers connect to a private virtual bridge network with NAT to the host/internet), **host** (container shares the host's network namespace — no NAT, full host port access), **none** (network namespace created but no interfaces configured, fully isolated), **overlay** (multi-host networking via VXLAN encapsulation for Docker Swarm), and **macvlan** (assigns a real MAC address from the host's physical network, making the container appear as a physical device on the LAN). User-defined bridge networks add DNS-based service discovery between containers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Docker networking modes control how isolated or connected a container is — from completely isolated to sharing the host's full network identity.

**One analogy:**
> Docker networking modes are like office connectivity options. Bridge mode is like working in a shared office with a NAT router — you can reach the internet through a shared IP, but outsiders can't find you unless you configure port forwarding. Host mode is like sitting at your desk with no office network at all — connected directly to the building's internet with your own IP. None mode is like being in a room with no network jack. Overlay networking is like a VPN connecting multiple offices so they can communicate privately.

**One insight:**
The security-performance trade-off is inverted from intuition: host mode (maximum performance, no NAT) has the worst security (container shares host network stack). Bridge mode (moderate performance, NAT) has better isolation. None mode (lowest performance, no connectivity) has the best isolation. Know which you need before choosing.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Network isolation = separate network namespace = container has its own IP stack.
2. Bridge networking = virtual ethernet pair (veth) connecting container to docker0 bridge.
3. Host networking = no network namespace = container processes bind to host ports directly.

**DERIVED DESIGN:**

**Bridge mode (default):**
Docker creates a virtual bridge interface `docker0` on the host (typically `172.17.0.0/16`). Each container gets a `veth` pair: one end in the container's network namespace (appears as `eth0`), one end attached to docker0 on the host. This creates a virtual LAN. Docker uses iptables NAT (MASQUERADE) to route container traffic to the host's network interface. Port publishing (`-p hostPort:containerPort`) adds iptables DNAT rules.

```
Host:
  eth0: 192.168.1.10 (physical NIC)
  docker0: 172.17.0.1 (virtual bridge)

Container A:
  eth0: 172.17.0.2 (veth pair end)
  → can reach internet via NAT through docker0

Container B:
  eth0: 172.17.0.3
  → can reach Container A via 172.17.0.2 (same bridge)
  → cannot be reached from internet unless port published
```

**Host mode:**
The container uses the host's network namespace directly. No virtual interfaces, no NAT. If the container binds to port 80, it is literally the host's port 80. Maximum performance (no veth overhead, no iptables NAT). Zero network isolation.

**None mode:**
A separate network namespace is created (loopback only). No external interfaces. The container can only communicate via its own loopback. Completely network-isolated.

**User-defined bridge network (enhanced bridge):**
`docker network create mynet` creates a user-defined bridge with built-in DNS resolution. Containers on the same user-defined bridge can reach each other by container name: `http://nginx` instead of `http://172.17.0.3`. Essential for multi-container Docker Compose setups.

**Overlay network:**
Uses VXLAN to create a virtual network across multiple Docker hosts. Packets are encapsulated in UDP and sent between hosts. Used by Docker Swarm for multi-host container communication.

**Macvlan:**
Assigns a real MAC address from the host's physical interface to the container. The container appears as a physical device on the LAN with its own real IP. No NAT. Used when containers need to be accessible on the LAN without port publishing (industrial devices, legacy apps).

**THE TRADE-OFFS:**

**Gain:** Flexibility to match network topology to application requirements.

**Cost:** Bridge NAT adds latency (~10μs per hop). Host mode removes isolation. Overlay adds VXLAN encapsulation overhead. Macvlan requires physical network configuration.

---

### 🧪 Thought Experiment

**SETUP:**
A developer builds a monitoring agent container that must run network diagnostics — sniff packets on the host's physical network interface and report host-level network metrics.

**WHAT HAPPENS WITH BRIDGE MODE:**
The container has its own network namespace with a virtual `eth0` (veth). It can only see traffic on its own virtual interface — it cannot sniff the host's `eth0`. Network diagnostics see only the container's own virtual network traffic. The monitoring agent fails to capture host-level metrics.

**WHAT HAPPENS WITH HOST MODE:**
The container shares the host's network namespace. The physical `eth0` is directly visible. `tcpdump -i eth0` captures real host network traffic. The monitoring agent works as intended — but the container now has direct access to all host ports, all host network interfaces, and can bind to any port on the host.

**THE INSIGHT:**
Host networking mode is legitimate for monitoring, performance testing, and network tooling containers that need direct host network access. But using it for regular application containers removes the security boundary that network namespaces provide. Match the networking mode to the container's actual requirements.

---

### 🧠 Mental Model / Analogy

> Bridge mode is like placing containers on a private office LAN behind a NAT router. Containers have their own private IP space. They can reach the internet. Outsiders need port forwarding to reach them. Multiple containers on the same bridge can talk to each other. Host mode is like connecting directly to the public internet — no router, full exposure. None mode is like being in a Faraday cage — completely cut off from all networks.

Mapping:
- "Private office LAN" → docker0 bridge (172.17.0.0/16)
- "NAT router to internet" → iptables MASQUERADE
- "Port forwarding" → `-p 8080:80` iptables DNAT rule
- "Container-to-container on same bridge" → veth pairs through docker0
- "Host mode: direct internet connection" → shared host network namespace
- "Faraday cage" → `--network none` (loopback only)

Where this analogy breaks down: a physical office LAN has broadcast traffic that all devices see. Docker bridge mode filters broadcast between containers — they only see unicast traffic directed to them.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Docker networking modes decide how your container talks to the network. The default (bridge) gives each container its own address on a private network. Host mode means the container uses the computer's network directly, like any other program. None means no network at all.

**Level 2 — How to use it (junior developer):**
`docker run nginx` — default bridge mode. `docker run --network host nginx` — host mode (binds port 80 on the actual host). `docker run --network none nginx` — no network. `docker network create mynet && docker run --network mynet nginx` — user-defined bridge with DNS discovery. In Docker Compose, services share a default user-defined bridge automatically and can reference each other by service name.

**Level 3 — How it works (mid-level engineer):**
Bridge networking uses Linux `veth` pairs (virtual ethernet), `iptables` for NAT and port publishing, and the kernel's virtual bridge (bridge module). When a container starts in bridge mode: Docker creates a `veth` pair, moves one end into the container's network namespace (named `eth0`), and attaches the other end to `docker0`. The kernel bridge learns MAC addresses and forwards frames. iptables rules provide NAT and DNAT for published ports. A user-defined bridge adds a custom DNS server (Docker's embedded DNS at `127.0.0.11`) that resolves container names to IPs. This DNS server is the key difference between default and user-defined bridges.

**Level 4 — Why it was designed this way (senior/staff):**
The bridge mode's default NAT design was an intentional security and UX choice: containers are unreachable from outside without explicit port publishing. This prevents accidental port exposure — a common vulnerability in pre-container environments. The `docker0` bridge was designed to "just work" for single-host development without any configuration. User-defined bridges were added later to address the default bridge's lack of DNS discovery — a significant operational gap for development environments. Host mode exists because some workloads legitimately need host-level network access (monitoring, testing, high-performance UDP services where NAT adds unacceptable latency). Kubernetes completely replaces Docker networking with CNI plugins — the pod network model (every pod gets an IP, all pods can communicate directly without NAT) was designed to eliminate Docker's NAT complexity at the platform level.

---

### ⚙️ How It Works (Mechanism)

**Bridge networking mechanics:**
```
┌──────────────────────────────────────────────────────────┐
│            Docker Bridge Network (default)               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Internet ←→ eth0 (192.168.1.10) → iptables MASQUERADE  │
│                                         ↓                │
│                                    docker0 (172.17.0.1)  │
│                               (virtual bridge)           │
│                                    ↑        ↑            │
│                               veth0a    veth1a           │
│                                 ↓          ↓             │
│  Container A netns    Container B netns                  │
│  eth0: 172.17.0.2     eth0: 172.17.0.3                  │
│                                                          │
│  Port publish (-p 8080:80):                              │
│  iptables DNAT: 0.0.0.0:8080 → 172.17.0.2:80           │
└──────────────────────────────────────────────────────────┘
```

**Host networking mechanics:**
```
┌──────────────────────────────────────────────────────────┐
│            Host Networking                               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Container process: nginx                                │
│  Shares host network namespace                           │
│  Sees: eth0 (192.168.1.10), lo, docker0, etc.            │
│  Binds: port 80 directly on host eth0                    │
│                                                          │
│  No veth. No iptables NAT. No port publishing needed.    │
│  Accessing localhost:80 from anywhere on host            │
│  reaches the container directly.                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (bridge, published port):**
```
Client → request to host:8080
  → host iptables: DNAT 8080 → container:80 ← YOU ARE HERE
  → packet forwarded to docker0 bridge
  → veth pair: to container eth0
  → container nginx processes request
  → response: reverse DNAT/SNAT → client
```

**FAILURE PATH:**
```
Two containers on default bridge cannot connect by name:
  → Container A: curl http://nginx
  → DNS: "nginx" not resolvable
  → Error: "Could not resolve host: nginx"
  → Cause: default bridge has no embedded DNS
  → Fix: create user-defined bridge
    docker network create mynet
    docker run --network mynet --name nginx nginx
    docker run --network mynet curlimages/curl http://nginx
```

**WHAT CHANGES AT SCALE:**
At scale, bridge mode's iptables NAT becomes a bottleneck — every packet traverses the iptables chain. For high-throughput services (>100k connections/second), iptables overhead is measurable. Kubernetes addresses this with kube-proxy (iptables/IPVS mode) or Cilium (eBPF, bypassing iptables entirely). In production Kubernetes, Docker networking modes are irrelevant — CNI plugins (Calico, Cilium, Flannel) replace docker0 with cluster-wide pod networking.

---

### 💻 Code Example

**Example 1 — Default bridge networking:**
```bash
# Default bridge: each container gets 172.17.x.x IP
docker run -d --name web nginx
docker inspect web --format '{{.NetworkSettings.IPAddress}}'
# Output: 172.17.0.2

# Publish port to make accessible from host
docker run -d --name web -p 8080:80 nginx
curl http://localhost:8080   # Reaches nginx
```

**Example 2 — User-defined bridge (DNS discovery):**
```bash
# Create user-defined bridge
docker network create myapp-net

# Containers on same user-defined bridge can reach each other by name
docker run -d --name db --network myapp-net postgres:15
docker run -d --name api --network myapp-net myapi:latest
# Inside api container: connect to "db:5432" -- works via embedded DNS
```

**Example 3 — Host networking:**
```bash
# Host networking: shares host's network namespace
docker run -d --network host nginx
# nginx binds to host port 80 directly (no -p needed or allowed)
curl http://localhost:80   # Reaches nginx via host's network stack

# Check ports on host
ss -tlnp | grep 80
# tcp  LISTEN  0  511  0.0.0.0:80  nginx:worker
```

**Example 4 — None (isolated):**
```bash
# Fully network-isolated container
docker run --network none alpine ip addr
# Only loopback: lo 127.0.0.1
# No external connectivity possible
```

---

### ⚖️ Comparison Table

| Mode | Isolation | Container-to-Container | External Access | Performance | Best For |
|---|---|---|---|---|---|
| **Bridge (default)** | Good | Same bridge (by IP) | Via port publish | Moderate | General development |
| User-defined bridge | Good | By name (DNS) | Via port publish | Moderate | Multi-container apps |
| Host | None | Via localhost | Direct (host ports) | Excellent | Monitoring, perf tools |
| None | Complete | None | None | N/A | Security isolation |
| Overlay | Good | Cross-host (VXLAN) | Via published ports | Moderate | Docker Swarm multi-host |
| Macvlan | Good | By MAC/IP | Direct LAN access | Good | Legacy apps needing LAN IP |

How to choose: user-defined bridge for most Docker Compose development. Host mode for monitoring/diagnostic tools. None for security-sensitive compute workloads. Overlay for Docker Swarm multi-host. Kubernetes replaces all of these with CNI-based pod networking.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Containers on the default bridge can find each other by name" | No. The default `docker0` bridge has no embedded DNS. Use user-defined networks (`docker network create`) for automatic DNS-based discovery. |
| "Host networking is available on Mac/Windows Docker Desktop" | Host networking on Docker Desktop (which runs Linux in a VM) behaves differently — it maps to the Linux VM's network, not the macOS/Windows host. Behaviour differs from Linux. |
| "Publishing a port (-p) creates a direct route to the container" | Publishing creates an iptables DNAT rule. The packet traverses the kernel's iptables chain. There is measurable overhead (typically <1ms), not a direct route. |
| "`--network none` means the container can't communicate at all" | Communication via shared volumes or IPC is still possible. `none` only removes network interfaces — not inter-process communication via other mechanisms. |
| "Kubernetes uses Docker bridge networking" | Kubernetes uses CNI plugins that completely replace Docker networking. Pod-to-pod networking has no NAT (unlike Docker bridge). Every pod gets a unique, routable IP on the cluster network. |

---

### 🚨 Failure Modes & Diagnosis

**Containers on default bridge can't find each other by name**

**Symptom:**
App container: `Could not resolve host: db`. Works fine in docker-compose (where user-defined network is implicit).

**Root Cause:**
Running containers with `docker run` uses the default bridge, which has no DNS resolver. Containers can only reach each other by IP.

**Diagnostic Command / Tool:**
```bash
# Verify which network containers are on
docker inspect <container> | jq '.[0].NetworkSettings.Networks'

# Test DNS resolution from inside container
docker exec <container> nslookup db
# fails on default bridge, works on user-defined network
```

**Fix:**
```bash
docker network create mynet
docker run --network mynet --name db postgres
docker run --network mynet --name app myapp
```

**Prevention:**
Always use user-defined networks for multi-container applications. Never rely on default bridge DNS (it doesn't exist).

---

**Host port conflict (host networking mode)**

**Symptom:**
`docker run --network host nginx` fails with `address already in use: bind`. Port 80 is already bound on the host.

**Root Cause:**
Host networking shares the host's ports. Another service (or another container) is already bound to port 80.

**Diagnostic Command / Tool:**
```bash
ss -tlnp | grep :80
lsof -i :80
```

**Fix:**
Change port binding in nginx config, or stop the conflicting service. Host mode shares ALL ports with the host — no isolation.

**Prevention:**
Use host networking only when genuinely needed. Document which ports a host-networked container uses and ensure they don't conflict with other services.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Container Networking` — Docker networking modes are implementations of container networking concepts
- `Linux Namespaces` — network namespaces are the kernel mechanism behind Docker networking isolation
- `Container` — networking modes are container properties

**Builds On This (learn these next):**
- `Container Orchestration` — Kubernetes replaces Docker networking with CNI; understand Docker first
- `Kubernetes Architecture` — pod networking builds on these concepts with CNI plugins
- `Container Security` — host networking mode is a security risk; understanding why requires networking fundamentals

**Alternatives / Comparisons:**
- `Overlay Networks` — cross-host networking; extends beyond single-host Docker bridge
- `Container Networking` — the broader concept of which Docker modes are implementations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Controls how a container's network        │
│              │ namespace connects to host/internet       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Wrong mode: security holes (host mode)    │
│ SOLVES       │ or connectivity failures (bridge, no DNS) │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Default bridge has NO DNS — containers    │
│              │ can't find each other by name. Use        │
│              │ user-defined networks for DNS discovery.  │
├──────────────┼───────────────────────────────────────────┤
│ USE bridge   │ Default for isolated apps                 │
│ USE host     │ Monitoring tools, high perf/UDP services  │
│ USE none     │ Security-isolated compute (no network)    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ --network host in production app          │
│              │ containers (removes all isolation)        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Isolation vs performance vs reachability  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "bridge=private LAN behind NAT,           │
│              │  host=no network at all, none=Faraday cage"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Container Networking → Overlay Networks → │
│              │ Kubernetes Networking (CNI)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A company runs a high-frequency trading application in a container that makes millions of network calls per second to a market data feed. The team profiles the application and finds 8μs of latency per network call that is attributed to iptables NAT traversal in Docker bridge mode. They consider switching to `--network host`. Analyse: what the precise iptables overhead mechanism is, what security properties are lost with host mode in this specific scenario, and propose an alternative that reduces latency without full host networking (consider MACVLAN, SR-IOV, or DPDK-based alternatives).

**Q2.** In Docker bridge mode, two containers on the same `docker0` bridge can communicate directly (by IP) without any external routing. In a Kubernetes cluster with Calico as the CNI plugin, two pods in different namespaces on different nodes communicate with each other. Trace the full network path in both scenarios: from source container/pod to destination, including every kernel subsystem and network interface traversed. What is the key architectural difference that enables Kubernetes's flat pod network model vs Docker's NAT-based bridge model?

