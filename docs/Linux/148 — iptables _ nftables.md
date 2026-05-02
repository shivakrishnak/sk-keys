---
layout: default
title: "iptables / nftables"
parent: "Linux"
nav_order: 148
permalink: /linux/iptables-nftables/
number: "0148"
category: Linux
difficulty: ★★★
depends_on: Linux Networking (ip, ss, netstat), Networking
used_by: Linux Security Hardening, Kubernetes, Docker
related: Linux Networking (ip, ss, netstat), tcpdump / Wireshark, SELinux / AppArmor
tags:
  - linux
  - networking
  - security
  - deep-dive
---

# 148 — iptables / nftables

⚡ TL;DR — `iptables` and `nftables` are Linux kernel packet filtering frameworks — they intercept every network packet and match it against chains of rules that decide whether to accept, drop, redirect, or modify it.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every packet reaching a Linux machine either gets processed or doesn't — with no middle layer to inspect or redirect it. A malicious port scan hits every open socket. An unwanted service is reachable to the whole internet because someone forgot to configure the application to bind only to localhost. NAT (multiple hosts sharing one IP) is impossible. Rate limiting, port forwarding, and stateful connection tracking don't exist.

**THE BREAKING POINT:**
A developer accidentally opens port 9200 (Elasticsearch) to the internet while testing. Without packet filtering, millions of internet bots will connect directly to the unauthed Elasticsearch instance within hours. The data is exposed and there's nothing between the attacker and the service.

**THE INVENTION MOMENT:**
This is exactly the problem netfilter/iptables solves. A single rule — `iptables -A INPUT -p tcp --dport 9200 -j DROP` — would have blocked all external access immediately. No application code change, no restart, applied in milliseconds.

---

### 📘 Textbook Definition

**iptables** is the user-space command-line interface to the Linux kernel's netfilter packet filtering framework, introduced in kernel 2.4. It organises rules into **tables** (filter, nat, mangle, raw) and **chains** (INPUT, OUTPUT, FORWARD, PREROUTING, POSTROUTING). Each chain is a list of rules; each rule matches packet criteria and specifies a **target** action (ACCEPT, DROP, REJECT, LOG, MASQUERADE, DNAT, etc.). Packets traverse chains in order; the first matching rule wins.

**nftables** is the modern replacement for iptables, introduced in kernel 3.13 and becoming the default in Debian 10, RHEL 8, and later. It provides a single unified framework (replacing four separate iptables tools: iptables, ip6tables, arptables, ebtables) with a cleaner syntax, atomic rule set replacement, and better performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
iptables/nftables intercept every packet at multiple hook points in the kernel network stack and apply ordered rules to decide what happens to each packet.

**One analogy:**

> iptables is a customs checkpoint with multiple inspection lanes. Every car (packet) entering or leaving the country (host) must pass through checkpoints (chains). At each checkpoint, inspectors (rules) check the car's licence plate (source IP), cargo manifest (port), and destination (destination IP). If a car matches a rule, it's either waved through (ACCEPT), turned away (DROP), or redirected (DNAT). The first matching rule decides; if no rule matches, the default policy applies.

**One insight:**
The order of rules matters absolutely. iptables evaluates rules top-to-bottom and stops at the first match. An ACCEPT rule before a DROP rule means the DROP never fires for matching packets. Most security incidents involving iptables misconfigurations involve rule ordering errors.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every packet passes through specific hook points in the network stack.
2. Rules are evaluated in order; the first match wins.
3. If no rule matches, the chain's default policy applies (ACCEPT or DROP).
4. Connection tracking (conntrack) remembers established connections so RELATED/ESTABLISHED traffic can bypass rule evaluation.

**DERIVED DESIGN:**
The Linux kernel's netfilter framework defines 5 hook points in the packet processing path:

- `NF_IP_PRE_ROUTING` → PREROUTING chain (before routing decision)
- `NF_IP_LOCAL_IN` → INPUT chain (destined for local process)
- `NF_IP_FORWARD` → FORWARD chain (being routed between interfaces)
- `NF_IP_LOCAL_OUT` → OUTPUT chain (from local process)
- `NF_IP_POST_ROUTING` → POSTROUTING chain (after routing decision)

Tables are collections of chains:

- **filter** (default): INPUT, FORWARD, OUTPUT — packet allow/deny
- **nat**: PREROUTING, POSTROUTING, OUTPUT — address translation
- **mangle**: all chains — packet header modification
- **raw**: PREROUTING, OUTPUT — connection tracking exemptions

**THE TRADE-OFFS:**
**Gain:** Kernel-level packet filtering with no per-packet context switch; stateful connection tracking; NAT; port forwarding.
**Cost:** Complex rule ordering; poor performance at massive scale (nftables partially solves this); iptables rules are not atomic — nftables `nft -f` is atomic.

---

### 🧪 Thought Experiment

**SETUP:**
You have a host behind NAT (private IP 192.168.1.100) that needs to serve a web service on port 8080, but all external traffic arrives at the router's public IP (203.0.113.1) on port 80.

**THE REDIRECT PROBLEM:**
External users can only reach 203.0.113.1:80. Your service is on 192.168.1.100:8080. How do you connect them without changing the application or the client?

**WHAT HAPPENS WITH iptables DNAT:**

```bash
# On the router, before routing decision:
# Redirect public:80 → internal host:8080
iptables -t nat -A PREROUTING \
  -d 203.0.113.1 -p tcp --dport 80 \
  -j DNAT --to-destination 192.168.1.100:8080

# Allow forwarding to internal host
iptables -A FORWARD \
  -d 192.168.1.100 -p tcp --dport 8080 \
  -j ACCEPT
```

The kernel rewrites the destination IP/port in the packet header before routing. The internal server sees the original client's IP. Replies are automatically SNAT'd back (conntrack handles this). External users are transparently forwarded — they never see the internal address.

**THE INSIGHT:**
iptables NAT is how virtually all home routers work and how Docker port mapping works. The complexity of PREROUTING vs POSTROUTING exists because the routing decision happens between them — to change the destination, you must act before routing (PREROUTING); to change the source, you act after (POSTROUTING/MASQUERADE).

---

### 🧠 Mental Model / Analogy

> iptables is like a series of tollbooths on different roads. PREROUTING is the border checkpoint — packets get examined before they pick their road. INPUT is the toll on the road leading into your city (your host). FORWARD is the toll on the bypass road (packets passing through). OUTPUT is the toll leaving your city. POSTROUTING is the final checkpoint as they merge back onto the highway. At each tollbooth, a list of rules is checked in order.

- "Tollbooth" → chain
- "Road" → routing decision
- "List of rules at tollbooth" → iptables rules in chain
- "Wave through / turn back / redirect" → ACCEPT / DROP / DNAT

Where this analogy breaks down: real tollbooths don't modify packets; iptables mangle table can modify TTL, TOS, and other headers — something no physical tollbooth does.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
iptables is a security gateway for all network traffic on Linux. Like a security guard, it checks every network packet that arrives, leaves, or passes through the computer against a list of rules. If a packet matches a rule, that rule decides what happens — let it through, block it, or redirect it elsewhere.

**Level 2 — How to use it (junior developer):**
Block a port: `iptables -A INPUT -p tcp --dport 8080 -j DROP`. Allow from specific IP: `iptables -A INPUT -s 10.0.0.5 -j ACCEPT`. View rules: `iptables -L -n -v`. Insert at top (highest priority): `iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT`. Save rules (Ubuntu): `iptables-save > /etc/iptables/rules.v4`. The order of rules matters — first match wins.

**Level 3 — How it works (mid-level engineer):**
Each table has a default policy (ACCEPT or DROP) applied when no rule matches. Connection tracking (`-m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT`) allows return traffic for already-established connections without explicit rules. The nat table's MASQUERADE target rewrites the source IP to the outgoing interface's IP — this is how Docker implements container internet access. DNAT in PREROUTING is how `docker run -p 8080:80` works: PREROUTING redirects packets destined for host:8080 to container:80. `-m multiport --dports` matches multiple ports in one rule.

**Level 4 — Why it was designed this way (senior/staff):**
netfilter's hook architecture was designed for extensibility — any kernel module can register a hook at any of the 5 points and insert itself into the packet processing chain. This is how VPN tunnels (WireGuard, OpenVPN), traffic shapers (tc), and container networking plugins (Calico, Cilium) all coexist. The table/chain separation allows different tools (iptables, Docker, Kubernetes kube-proxy) to manage different tables without interfering. The weakness is that at scale (millions of rules in large Kubernetes clusters), linear rule evaluation becomes a performance bottleneck — this drove both nftables (with hash and set-based matching) and eBPF-based solutions (Cilium) that bypass netfilter entirely.

---

### ⚙️ How It Works (Mechanism)

**Packet flow through netfilter:**

```
Incoming packet
       │
       ▼
 [PREROUTING]  ← NAT table: DNAT, redirect
       │
    (routing decision: local or forward?)
       │
   ┌───┴───┐
   │       │
   ▼       ▼
[INPUT]  [FORWARD]  ← filter table
   │       │
   ▼       ▼
local    [POSTROUTING] ← NAT: MASQUERADE/SNAT
process        │
   │           ▼
   ▼       routed out
[OUTPUT]
   │
[POSTROUTING]
```

**Essential iptables commands:**

```bash
# View all rules with packet/byte counts
iptables -L -n -v

# View specific table
iptables -t nat -L -n -v

# Add rules (append to end)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
# Default DROP policy (block everything else)
iptables -P INPUT DROP
iptables -P FORWARD DROP

# Allow established/related traffic (conntrack)
iptables -A INPUT -m conntrack \
  --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Rate limit SSH (prevent brute force)
iptables -A INPUT -p tcp --dport 22 \
  -m recent --update --seconds 60 \
  --hitcount 10 -j DROP
iptables -A INPUT -p tcp --dport 22 \
  -m recent --set -j ACCEPT

# Delete a rule
iptables -D INPUT -p tcp --dport 8080 -j DROP

# Flush all rules in a chain
iptables -F INPUT

# Save/restore (Ubuntu/Debian)
iptables-save > /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4
```

**nftables equivalent syntax:**

```bash
# View current ruleset
nft list ruleset

# Create a table and chain
nft add table inet filter
nft add chain inet filter input \
  { type filter hook input priority 0 \; \
    policy drop \; }

# Add rules
nft add rule inet filter input \
  ct state established,related accept
nft add rule inet filter input \
  iif lo accept
nft add rule inet filter input \
  tcp dport { 22, 80, 443 } accept

# Atomic ruleset load (vs iptables non-atomic)
nft -f /etc/nftables.conf

# List with handles (for deletion)
nft list chain inet filter input -a
# Delete rule by handle
nft delete rule inet filter input handle 5
```

**Docker and iptables interaction:**

```bash
# Docker automatically adds FORWARD rules and nat rules
# View Docker-managed chains:
iptables -t nat -L DOCKER -n -v
iptables -L DOCKER -n -v

# Port mapping: docker run -p 8080:80 → DNAT rule
iptables -t nat -L PREROUTING -n -v
# Shows: DNAT tcp -- 0.0.0.0/0 → 172.17.0.2:80
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  DOCKER PORT MAPPING: host:8080 → container:80│
└────────────────────────────────────────────────┘

External SYN to host-ip:8080
       │
       ▼
 PREROUTING (nat table)
       │  DNAT rule: dest → 172.17.0.2:80
       │  Rewrites packet header
       ▼
 Routing decision
       │  dest is 172.17.0.2 (container)
       │  → FORWARD path
       ▼
 FORWARD (filter table)
       │  Docker's FORWARD rule: ACCEPT to 172.17.0.2:80
       ▼
 POSTROUTING (nat table)
       │  (conntrack remembers original → translated mapping)
       ▼
 Packet arrives at docker0 bridge → container eth0
       │  Container sees source=external-ip, dest=172.17.0.2:80
       ▼
 Response from container
       │  conntrack reverses DNAT automatically
       │  Source rewritten: 172.17.0.2:80 → host-ip:8080
       ▼
 External client receives reply from host-ip:8080
```

**FAILURE PATH:**
If `iptables -P FORWARD DROP` is set without Docker's FORWARD rules, port mappings silently fail. Packets arrive at the host (PREROUTING DNAT succeeds) but are dropped at FORWARD. `tcpdump` on the host shows packets arriving; none reach the container.

**WHAT CHANGES AT SCALE:**
Kubernetes kube-proxy in iptables mode adds thousands of rules — one DNAT chain per Service endpoint. At scale (1000+ services), every new connection must traverse thousands of iptables rules. This drove the adoption of IPVS mode (kube-proxy uses kernel IPVS load balancer with O(1) hash lookups instead of O(n) rule traversal) and eBPF-based solutions (Cilium) that replace iptables entirely with maps.

---

### 💻 Code Example

**Example 1 — Production-ready basic firewall:**

```bash
#!/bin/bash
# Production firewall: default deny, explicit allow
# Run as root

# Flush existing rules and chains
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback (localhost)
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established/related connections
iptables -A INPUT -m conntrack \
  --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (limit to management CIDR)
iptables -A INPUT -s 10.0.0.0/8 \
  -p tcp --dport 22 -j ACCEPT

# Allow web traffic
iptables -A INPUT -p tcp \
  --dport 80 -j ACCEPT
iptables -A INPUT -p tcp \
  --dport 443 -j ACCEPT

# Allow ICMP ping
iptables -A INPUT -p icmp \
  --icmp-type echo-request -j ACCEPT

# Log dropped packets (last rule before DROP)
iptables -A INPUT -j LOG \
  --log-prefix "IPT-DROP: " --log-level 7

echo "Firewall rules applied"
iptables-save > /etc/iptables/rules.v4
```

**Example 2 — Rate limiting with hashlimit:**

```bash
# Rate limit HTTP to 100 req/sec per source IP
# (DDoS mitigation)
iptables -A INPUT -p tcp --dport 80 \
  -m hashlimit \
  --hashlimit-above 100/sec \
  --hashlimit-mode srcip \
  --hashlimit-name http-rate-limit \
  -j DROP
```

**Example 3 — nftables modern equivalent:**

```bash
#!/usr/sbin/nft -f
# /etc/nftables.conf - atomic load with: nft -f

flush ruleset

table inet filter {
  chain input {
    type filter hook input priority 0
    policy drop

    iif lo accept
    ct state established,related accept
    tcp dport { 22, 80, 443 } accept
    ip protocol icmp accept
    log prefix "NFT-DROP: " drop
  }

  chain forward {
    type filter hook forward priority 0
    policy drop
  }

  chain output {
    type filter hook output priority 0
    policy accept
  }
}
```

---

### ⚖️ Comparison Table

| Feature        | iptables              | nftables          | ufw            | firewalld           |
| -------------- | --------------------- | ----------------- | -------------- | ------------------- |
| Syntax         | Verbose               | Clean             | Simple         | XML/zone-based      |
| Atomic updates | No                    | **Yes**           | No             | Partial             |
| IPv4+IPv6      | Separate tools        | **Unified**       | Unified        | Unified             |
| Performance    | O(n) rules            | Hash/set          | O(n)           | O(n)                |
| Default on     | Pre-RHEL8, Ubuntu <20 | RHEL8+, Debian10+ | Ubuntu default | RHEL/Fedora default |
| Kubernetes     | Legacy                | Emerging          | No             | No                  |

How to choose: use nftables for new deployments; use iptables if working with existing tooling or older kernels; use ufw for simple desktop/server firewalls where rules are straightforward; never mix iptables and nftables rules on the same system.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                           |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DROP and REJECT are equivalent              | DROP silently discards (attacker learns nothing); REJECT sends back a "port unreachable" response (tells attacker the port exists but is filtered); use DROP on public interfaces |
| iptables -F removes all rules               | `-F` flushes rules but does NOT reset default policies; if policy was DROP, it stays DROP — potentially locking you out                                                           |
| iptables rules are automatically persistent | Rules live in kernel memory only; without `iptables-save`, a reboot removes all rules                                                                                             |
| nftables is backward compatible             | nftables uses completely different syntax and cannot read iptables rule files; migration requires rewriting rules                                                                 |
| Kubernetes manages iptables rules safely    | kube-proxy manages its own chains but interacts with host iptables; manual `iptables -F` on a Kubernetes node will break cluster networking immediately                           |

---

### 🚨 Failure Modes & Diagnosis

**Locked Out After Setting Default DROP Policy**

**Symptom:**
SSH session drops immediately after running `iptables -P INPUT DROP`.

**Root Cause:**
Setting DROP policy before adding an ACCEPT rule for the current SSH connection drops the existing connection when the TCP keepalive fires or the next packet arrives.

**Recovery:**
If console/KVM access is available:

```bash
iptables -P INPUT ACCEPT  # restore default
# OR
iptables -F              # flush all rules
```

If no console access: most cloud providers have a firewall layer (security groups, NSGs) above the instance that maintains SSH access regardless of in-guest iptables.

**Prevention:**
Always add ACCEPT rules before setting DROP policy. Add a time-limited rule first:

```bash
# Auto-restore if you forget (10 min safety net)
(sleep 600 && iptables -P INPUT ACCEPT \
  && iptables -F) &
# Then set your rules; cancel background job if all OK
```

---

**iptables Rules Disappear After reboot**

**Symptom:**
Rules are applied during the session but missing after reboot; `iptables -L` shows only default policies.

**Root Cause:**
`iptables` modifications are not automatically persisted.

**Diagnostic Command:**

```bash
# Check if persistence package is installed
dpkg -l iptables-persistent   # Debian/Ubuntu
rpm -q iptables-services      # RHEL/CentOS
```

**Fix:**

```bash
# Ubuntu/Debian
apt install iptables-persistent
iptables-save > /etc/iptables/rules.v4
ip6tables-save > /etc/iptables/rules.v6
```

**Prevention:**
Always use `iptables-save` after making changes; add to deployment runbooks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Linux Networking (ip, ss, netstat)` — understanding interfaces, routing, and socket state is required to write correct iptables rules
- `Networking` — TCP/UDP, ports, and packet structure are foundational to understanding rule matching

**Builds On This (learn these next):**

- `Linux Security Hardening` — iptables is a core component of Linux host hardening
- `Kubernetes` — kube-proxy uses iptables or IPVS to implement Service routing; understanding iptables is essential for Kubernetes networking debugging
- `Docker` — Docker's port mapping, network isolation, and inter-container networking all use iptables

**Alternatives / Comparisons:**

- `nftables` — modern replacement with atomic rule updates and unified IPv4/IPv6 support
- `ufw` — simplified front-end for iptables; good for simple use cases
- `firewalld` — zone-based firewall manager used on RHEL/Fedora
- `eBPF/Cilium` — bypasses iptables entirely for high-performance Kubernetes networking

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kernel packet filtering framework with    │
│              │ ordered rules at 5 netfilter hook points  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No gatekeeping layer between the network  │
│ SOLVES       │ and services; no NAT, no port forwarding  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ First matching rule wins; order is        │
│              │ everything; DROP policy is not a rule     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Host-level packet filtering, port         │
│              │ forwarding, NAT/masquerade, rate limiting │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Kubernetes scale (1000+ services) —       │
│              │ use IPVS mode or Cilium/eBPF instead      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Powerful and universal vs complex rule    │
│              │ ordering and non-atomic updates           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A series of customs checkpoints that     │
│              │  every network packet must pass through"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ nftables → conntrack → eBPF / Cilium     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes cluster running kube-proxy in iptables mode has 2,000 Services. You notice new pod creation is taking longer than expected and health check latency has increased. Explain the relationship between the number of Services and iptables rule count, calculate approximately how many iptables rules 2,000 Services generates, and propose two architectural solutions to address this at scale without changing application code.

**Q2.** You are designing a multi-tenant Kubernetes platform where tenants must have network isolation — tenant A's pods must never be able to communicate with tenant B's pods, even if they know each other's pod IPs. You have three options: iptables-based NetworkPolicy, nftables, or Cilium eBPF. Design the isolation strategy for each approach and explain why the performance and operational characteristics differ significantly at 100 tenants with 50 pods each.
