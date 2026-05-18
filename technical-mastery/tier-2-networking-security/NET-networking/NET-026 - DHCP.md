---
id: NET-026
title: "DHCP"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-009, NET-025
used_by: NET-027
related: NET-009, NET-025, NET-028
tags:
  - networking
  - dhcp
  - ip
  - address-management
  - protocol
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/net/dhcp/
---

**⚡ TL;DR** - DHCP (Dynamic Host Configuration Protocol)
automatically assigns IP addresses, subnet masks, gateways,
and DNS servers to network hosts via a 4-message UDP
broadcast sequence (DORA: Discover, Offer, Request, Ack).
Without DHCP, every device joining a network would require
manual IP configuration. Problems: silent IP conflicts,
stale leases, and DHCP server outage causing all new
connections to fail.

| #026 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, NAT | |
| **Used by:** | ARP (Address Resolution Protocol) | |
| **Related:** | IP Address, NAT, Routing Basics | |

---

### 🔥 The Problem This Solves

Without DHCP, every device needs a manually configured:
IP address, subnet mask, default gateway, DNS server(s),
and any other network parameters. In a 500-device office
or 10,000-container Kubernetes cluster, manual assignment
is impossible to maintain: IP conflicts, stale assignments,
and configuration drift cause constant connectivity failures.
DHCP automates IP assignment from a managed pool,
preventing conflicts and centralizing network configuration.

---

### 📘 Textbook Definition

**DHCP (Dynamic Host Configuration Protocol)** is defined
in RFC 2131 (IPv4) and RFC 8415 (DHCPv6). A DHCP server
manages a **pool** of IP addresses and assigns them as
time-limited **leases** to clients. Each lease contains:
IP address, subnet mask, default gateway, DNS server IPs,
lease duration, and optional parameters (domain name,
NTP servers, etc.). Clients renew leases before expiry.
DHCP uses UDP: clients broadcast on port 68 → server
listens on port 67. Broadcasts cannot cross routers
without a **DHCP relay agent** (IP helper).

---

### ⏱️ Understand It in 30 Seconds

**The 4-message DORA sequence:**

```
┌──────────────────────────────────────────────────────────┐
│  DORA: The 4 DHCP Messages                               │
├──────────────────────────────────────────────────────────┤
│  D - DISCOVER  │  Client broadcasts: "Is there a DHCP   │
│                │  server? I need an IP address."         │
│                │  Src: 0.0.0.0 Dst: 255.255.255.255     │
├────────────────┼───────────────────────────────────────  │
│  O - OFFER     │  Server replies: "I offer 192.168.1.50, │
│                │  valid for 86400 seconds"               │
│                │  Src: server IP Dst: 255.255.255.255    │
├────────────────┼───────────────────────────────────────  │
│  R - REQUEST   │  Client broadcasts: "I accept the       │
│                │  offer from server X for 192.168.1.50"  │
│                │  (Broadcast so other servers see reject) │
├────────────────┼───────────────────────────────────────  │
│  A - ACK       │  Server confirms: "192.168.1.50 is yours│
│                │  until timestamp T. Here's your gateway │
│                │  and DNS."                              │
└──────────────────────────────────────────────────────────┘
```

---

### 🔩 First Principles Explanation

**Why UDP broadcast?**
The client has no IP yet when it sends DISCOVER. IP
requires a source address to route packets. The workaround:
- Source IP: `0.0.0.0` (unknown)
- Destination IP: `255.255.255.255` (limited broadcast)
- UDP port 67 (server) / 68 (client)
- The broadcast is delivered to ALL hosts on the LAN
  (broadcasts don't cross routers by default)

**What the DHCP ACK delivers:**

```
DHCP ACK contents (example):
  Your IP:        192.168.1.50
  Subnet Mask:    255.255.255.0  (/24)
  Default Gateway: 192.168.1.1
  DNS Server 1:   8.8.8.8
  DNS Server 2:   8.8.4.4
  Lease Time:     86400 seconds (24 hours)
  Domain Name:    corp.example.com
  Renew Time:     43200 seconds (50% of lease, T1)
  Rebind Time:    75600 seconds (87.5% of lease, T2)
```

**Lease renewal states:**

```
┌──────────────────────────────────────────────────────────┐
│  DHCP Lease State Machine                                │
├──────────────────────────────────────────────────────────┤
│  Lease obtained → BOUND state (has valid IP)            │
│                                                          │
│  At T1 (50% of lease = 12h of 24h):                    │
│  Client unicasts RENEW to original server               │
│  Server responds ACK → lease extended                   │
│                                                          │
│  At T2 (87.5% of lease = 21h of 24h):                  │
│  If no ACK to RENEW: client broadcasts REBIND           │
│  (Any DHCP server can respond to rescue the lease)     │
│                                                          │
│  At T3 (100% of lease = 24h):                          │
│  Lease expires → client loses IP → restarts DORA       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP: DHCP server goes down at 3pm.**

What happens to existing hosts?
- Hosts currently BOUND: fine until T1 (typically 12h later)
- At T1: hosts try to RENEW unicast → no response
- At T2 (21h): hosts try to REBIND broadcast → no response
- At T3 (24h): lease expires → hosts lose IP → DORA fails
  → no DHCP server → APIPA (169.254.x.x) self-assigned

**What breaks in practice:**
- Hosts that have their lease expire: lose network connectivity
- New containers/VMs/devices: get 169.254.x.x, cannot route
- Renewing laptops (reconnecting from sleep): fail

**Key insight:**
A 24h lease means a 24h window to restore DHCP before
existing hosts start losing connectivity. Short leases
(1-2 hours) cause faster DHCP server recovery but also
faster connection loss on outage. Cloud DHCP uses short
leases (~3600s) with high-availability DHCP servers.

---

### 🧠 Mental Model / Analogy

> DHCP is a hotel check-in desk that assigns room keys:
>
> Guest arrives (new device): "Any rooms available?"
> (DISCOVER)
>
> Desk offers a room: "Room 150, key valid 24 hours"
> (OFFER)
>
> Guest accepts: "I'll take room 150 from your desk"
> (REQUEST - tells other desks they lost)
>
> Desk confirms: "Room 150 is yours, here's WiFi password,
> breakfast is at 8am, checkout is tomorrow noon"
> (ACK - delivers IP + gateway + DNS + lease time)
>
> At noon tomorrow minus 6 hours (T1): Guest calls desk
> to extend checkout. (RENEW)

---

### ⚙️ How It Works (Mechanism)

**Diagnosing DHCP issues:**

```bash
# Manually trigger DHCP on an interface (Linux)
sudo dhclient eth0     # request lease for eth0
sudo dhclient -r eth0  # release current lease

# See current DHCP lease information
cat /var/lib/dhcp/dhclient.leases
# Shows: fixed-address, subnet-mask, routers, dns, expire

# Or (modern systemd):
networkctl status eth0
# Shows: Address, Gateway, DNS, NTP from DHCP

# Capture DHCP traffic (the DORA sequence)
sudo tcpdump -i eth0 -n "port 67 or port 68" -v
# You'll see: DISCOVER, OFFER, REQUEST, ACK

# Check IP address (was DHCP successful?)
ip addr show eth0
# If you see 169.254.x.x: DHCP failed (APIPA fallback)
# If you see your expected subnet: DHCP succeeded

# Windows equivalent:
# ipconfig /release eth0
# ipconfig /renew eth0
```

**Wrong vs Right - DHCP in cloud-init:**

```yaml
# BAD: hardcode IPs in cloud-init user data
# If you launch more than one instance with same config,
# they all get the same static IPs → conflict
write_files:
  - content: |
      ADDRESS=10.0.1.50    # WRONG: hardcoded
      NETMASK=255.255.255.0
      GATEWAY=10.0.1.1
    path: /etc/sysconfig/network-scripts/ifcfg-eth0

# GOOD: use DHCP (cloud DHCP assigns unique IP per instance)
write_files:
  - content: |
      BOOTPROTO=dhcp       # CORRECT: dynamic assignment
      ONBOOT=yes
    path: /etc/sysconfig/network-scripts/ifcfg-eth0
# AWS/GCP/Azure DHCP servers guarantee unique IPs per instance
```

**DHCP relay agent - crossing subnets:**

```
┌──────────────────────────────────────────────────────────┐
│  DHCP Relay (IP Helper)                                  │
├──────────────────────────────────────────────────────────┤
│  Problem: DHCP uses broadcasts. Broadcasts don't cross   │
│  routers. Remote subnets can't reach central DHCP.      │
│                                                          │
│  Solution: DHCP Relay Agent (ip helper-address in       │
│  Cisco, dhcp-helper in other vendors)                   │
│                                                          │
│  Flow:                                                   │
│  Client DISCOVER (broadcast) →                          │
│  Router receives broadcast →                            │
│  Router forwards as unicast to central DHCP server →    │
│  DHCP server responds with unicast OFFER →              │
│  Router forwards OFFER to original broadcast domain      │
│                                                          │
│  This enables one DHCP server for all subnets.          │
│  The DHCP packet includes "giaddr" (gateway IP) field   │
│  so the server knows which subnet pool to assign from.  │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Kubernetes IPAM (IP Address Management):**

```
┌──────────────────────────────────────────────────────────┐
│  How Kubernetes assigns Pod IPs                          │
├──────────────────────────────────────────────────────────┤
│  Not traditional DHCP - uses CNI (Container Network    │
│  Interface) plugins, but same concept:                  │
│                                                          │
│  Pod scheduled to node:                                 │
│  kubelet → calls CNI plugin → requests IP               │
│  CNI consults IPAM: "next available in 10.244.1.0/24"  │
│  CNI assigns 10.244.1.5 → configures veth interface    │
│  Pod has IP. Connected to cluster network.              │
│                                                          │
│  Pod deleted:                                           │
│  CNI releases 10.244.1.5 → back to IPAM pool           │
│                                                          │
│  Key difference from DHCP:                              │
│  - No lease expiry (IP held until pod deleted)          │
│  - No UDP broadcast (CNI is in-process)                 │
│  - But same fundamental problem: allocate unique IPs   │
│    from a pool without conflicts                        │
└──────────────────────────────────────────────────────────┘
```

**WHAT CHANGES AT SCALE:**
In a Kubernetes cluster with 10,000 pods rotating rapidly
(deployments, autoscaling), the DHCP/IPAM pool must handle
high churn. Short lease times help reclaim IPs faster.
AWS EKS uses VPC CNI which allocates entire /28 blocks
to each node (pre-warming), reducing API calls per pod.
IP address exhaustion in the pod CIDR (running out of
pod IPs in the VPC CIDR) is a common scaling pain point
that requires VPC CIDR expansion or secondary CIDRs.

---

### ⚖️ Comparison Table

| | DHCP | Static IP | Cloud IPAM |
|---|---|---|---|
| **Configuration** | Automatic | Manual | Automatic |
| **Uniqueness** | Managed by server | Human responsibility | Managed by cloud |
| **Conflict risk** | Low (if server works) | High (human error) | None (atomic) |
| **Lease duration** | Hours-days | Permanent | Pod lifetime |
| **Failure mode** | DHCP server outage | IP conflict | IPAM API failure |
| **Use case** | LAN, WiFi, VMs | Servers, routers | Containers, VMs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DHCP assigns the IP | DHCP assigns an IP lease. The IP is temporarily assigned and must be renewed. At lease expiry, the IP may be reassigned to a different host. Use DHCP reservations (MAC → IP mapping) for hosts that need consistent IPs. |
| DHCP is only for client devices | Servers often get IPs via DHCP with reservations (MAC address locked to specific IP). Cloud VMs always use DHCP - AWS assigns IPs via DHCP, and the instance's IP is reserved for its lifetime in AWS's DHCP system. |
| 169.254.x.x means "no network" | 169.254.x.x (APIPA - Automatic Private IP Addressing) means the DHCP request failed and the host self-assigned a link-local address. The physical network may be up, but DHCP is down. Can still communicate with other APIPA hosts on the same LAN. |

---

### 🚨 Failure Modes & Diagnosis

**IP Address Conflict (Two Hosts, Same IP)**

**Symptom:** Intermittent connectivity loss. `ping` works
sometimes, fails others. `arp -n` shows same IP at two
different MAC addresses. Applications connect then drop.

**Root Cause:** Two hosts have the same IP address. Each
sends ARP replies claiming ownership. The network flaps
between them based on most recent ARP.

**Diagnosis:**
```bash
# Find all ARP entries for a specific IP
arp -n | grep 192.168.1.50
# If two MACs → IP conflict

# Send gratuitous ARP to expose conflict
arping -D -I eth0 192.168.1.50
# -D = duplicate address detection mode
# If exit code 1: conflict detected (another host answered)

# Watch ARP table for conflicts
sudo tcpdump -i eth0 -n arp
# Look for: two different src MAC for same src IP
```

**Fix:**
- If static IP conflict: find and remove the duplicate
- If DHCP server assigned duplicate: check lease database
  for corruption; restart DHCP server; check pool range
  doesn't overlap static assignments
- Prevention: reserve DHCP pool separate from static range:
  DHCP pool: 192.168.1.100-200
  Static range: 192.168.1.1-50 (never in DHCP pool)

---

### 🔗 Related Keywords

**Prerequisites:**
- `IP Address` - what DHCP assigns
- `NAT` - uses the IPs that DHCP distributes

**Builds On This:**
- `ARP` - resolves MAC for just-assigned IP

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT DOES │ Auto-assigns IP, mask, GW, DNS to hosts   │
├──────────────┼───────────────────────────────────────────┤
│ DORA         │ Discover → Offer → Request → Ack          │
│              │ UDP broadcast src=0.0.0.0 dst=255.255.255 │
├──────────────┼───────────────────────────────────────────┤
│ RENEW TIMES  │ T1=50% lease (unicast), T2=87.5% (bcast) │
│              │ T3=100% (lease expires, restart DORA)     │
├──────────────┼───────────────────────────────────────────┤
│ APIPA        │ 169.254.x.x = DHCP failed, self-assigned  │
├──────────────┼───────────────────────────────────────────┤
│ RELAY AGENT  │ IP helper forwards broadcast to unicast   │
│              │ for cross-subnet DHCP                     │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSE     │ tcpdump port 67 or 68, dhclient, ip addr  │
│              │ arping -D for IP conflicts                │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ DHCP pool overlapping static IP range:    │
│              │ causes IP conflicts. Keep ranges separate. │
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"DHCP auto-assigns IP, subnet mask, default gateway, and
DNS server via a 4-message UDP broadcast (DORA: Discover,
Offer, Request, Ack). Leases have a duration; clients renew
at 50% (T1) and 87.5% (T2) of lease time. If DHCP fails,
hosts fall back to APIPA (169.254.x.x). Cross-subnet DHCP
requires a relay agent (IP helper) that converts the
broadcast to a unicast. Production anti-patterns: DHCP
pool overlapping static IP assignments (causes IP conflicts),
and not using DHCP reservations for servers that need
consistent IPs (use MAC-to-IP binding instead of static)."