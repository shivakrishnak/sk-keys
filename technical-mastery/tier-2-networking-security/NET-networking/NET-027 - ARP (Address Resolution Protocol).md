---
id: NET-027
title: "ARP (Address Resolution Protocol)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-011, NET-009
used_by: NET-052
related: NET-011, NET-009, NET-026
tags:
  - networking
  - arp
  - mac
  - layer2
  - address-resolution
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/net/arp/
---

**⚡ TL;DR** - ARP translates IP addresses to MAC addresses
within a local network segment by broadcasting "Who has
IP X? Tell me your MAC." The answer is cached in the ARP
table for performance. ARP is stateless, unauthenticated,
and operates at Layer 2 - making ARP spoofing (poisoning
the cache with false mappings) a fundamental LAN security
threat that all network security courses cover.

| #027 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | MAC Address, IP Address | |
| **Used by:** | Network Segmentation and Firewall Rules | |
| **Related:** | MAC Address, IP Address, DHCP | |

---

### 🔥 The Problem This Solves

IP routing gets a packet to the right network segment
(subnet). But within a subnet, Ethernet frames need a
MAC address (hardware address) to deliver to the correct
physical host. When your machine knows `192.168.1.10`
is the destination, it doesn't know what Ethernet MAC
address to put in the frame. ARP resolves this by asking
the entire local network: "Who has this IP? Tell me your
MAC so I can send frames to you directly."

---

### 📘 Textbook Definition

**ARP (Address Resolution Protocol)** is defined in
RFC 826 (1982). It operates at the Layer 2/3 boundary
to map IPv4 addresses to Ethernet MAC addresses. ARP
uses two message types: **ARP Request** (broadcast to
all hosts on segment: "Who has IP X?") and **ARP Reply**
(unicast from the IP owner: "I have IP X, my MAC is Y").
Results are cached in the **ARP table** (also called ARP
cache) with a TTL (typically 60-120 seconds on Linux,
20-30 seconds expired entries are flushed). ARP operates
only within a single broadcast domain (subnet) - packets
destined for different subnets go through the default
gateway's MAC, not the remote host's MAC.

---

### ⏱️ Understand It in 30 Seconds

**The ARP exchange:**

```
Host A wants to send to 192.168.1.10:

Step 1: Check ARP cache
  ip neigh show | grep 192.168.1.10
  Nothing → must ARP

Step 2: Broadcast ARP Request
  Ethernet frame:
    Src MAC: aa:bb:cc:dd:ee:ff (Host A's MAC)
    Dst MAC: ff:ff:ff:ff:ff:ff (broadcast to everyone)
  ARP payload:
    "Who has 192.168.1.10? Tell 192.168.1.5"

Step 3: Target replies (only 192.168.1.10 replies)
  Ethernet frame:
    Src MAC: 11:22:33:44:55:66 (Host B's MAC)
    Dst MAC: aa:bb:cc:dd:ee:ff (unicast to requester)
  ARP payload:
    "192.168.1.10 is at 11:22:33:44:55:66"

Step 4: Host A caches the mapping
  ARP table: 192.168.1.10 → 11:22:33:44:55:66 REACHABLE

Step 5: Host A sends data frame with Host B's MAC
```

---

### 🔩 First Principles Explanation

**Why only the gateway MAC in ARP table for remote hosts?**

```
┌──────────────────────────────────────────────────────────┐
│  ARP and Routing Combined                                │
├──────────────────────────────────────────────────────────┤
│  Scenario: Host A (192.168.1.5) sends to 8.8.8.8        │
│                                                          │
│  Step 1: Is 8.8.8.8 in my subnet (192.168.1.0/24)?     │
│          No → must route through default gateway         │
│                                                          │
│  Step 2: What is the gateway IP? (from routing table)   │
│          ip route: default via 192.168.1.1 dev eth0     │
│                                                          │
│  Step 3: ARP for GATEWAY IP (192.168.1.1), not 8.8.8.8 │
│          "Who has 192.168.1.1?"                         │
│          Reply: "192.168.1.1 is at aa:00:11:22:33:44"  │
│                                                          │
│  Step 4: Send IP packet to 8.8.8.8 in Ethernet frame:  │
│          Ethernet: Dst=aa:00:11:22:33:44 (gateway MAC)  │
│          IP: Dst=8.8.8.8 (unchanged, final destination) │
│                                                          │
│  Key insight: MAC address changes at EVERY HOP          │
│  IP address stays constant end-to-end                   │
│  This is Layer 2 vs Layer 3 separation                  │
└──────────────────────────────────────────────────────────┘
```

**ARP table states:**

```
ARP Table States (Linux):
REACHABLE  - Recently confirmed active (full ARP reply)
STALE      - Entry aged out; will re-ARP on next use
DELAY      - Currently re-probing (sent unicast probe)
PROBE      - Sending ARP request to verify
FAILED     - ARP failed (host unreachable)
PERMANENT  - Manually added (never evicted)
NOARP      - No ARP needed (virtual/tunnel interfaces)
```

---

### 🧪 Thought Experiment

**SETUP: ARP spoofing attack**

Attacker sends unsolicited ARP replies:
"192.168.1.1 (the gateway) is at AA:BB:CC:DD:EE:FF
(attacker's MAC)"

**What happens:**
- All hosts update their ARP cache: gateway → attacker's MAC
- All traffic destined for the gateway (internet traffic)
  is now sent to the attacker's MAC
- Attacker receives and forwards traffic (man-in-the-middle)
  or drops it (denial of service)

**Why it works:**
ARP has no authentication. Any host can send an ARP reply
claiming any IP. The most recent ARP reply "wins" - it
overwrites the ARP cache entry. This is why gratuitous ARP
(claiming your own IP) is used by load balancers and
failover systems: the new active node sends gratuitous ARP
to update all hosts' ARP caches immediately.

**Detection:**
```bash
# Watch for duplicate IP claiming different MAC
sudo tcpdump -i eth0 -n arp
# Look for: two ARP replies for same IP with different MACs

# Check ARP table for anomalies
ip neigh show | awk '{print $1, $5}' | sort | uniq -d
# Duplicate IP = ARP spoofing in progress
```

---

### 🧠 Mental Model / Analogy

> ARP is "shouting across the room":
>
> You know someone's name (IP address) but not their face
> (MAC address). You shout across the room:
> "Hey, is '192.168.1.10' here?"
>
> The person with that name raises their hand and shows
> you their face (MAC address). You remember their face
> for the next hour (ARP cache TTL).
>
> Problem: anyone in the room can raise their hand and
> say "That's me!" (ARP spoofing - no authentication).
> The ARP protocol has no way to verify identity.

---

### ⚙️ How It Works (Mechanism)

**ARP diagnostic commands:**

```bash
# View current ARP table
ip neigh show
# 192.168.1.1  dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE
# 192.168.1.50 dev eth0 lladdr 11:22:33:44:55:66 STALE

# Show only reachable entries
ip neigh show nud reachable

# Clear ARP table (force re-ARP on next access)
sudo ip neigh flush all

# Delete specific ARP entry
sudo ip neigh del 192.168.1.50 dev eth0

# Add static ARP entry (prevent spoofing for critical IPs)
sudo ip neigh add 192.168.1.1 \
  lladdr aa:bb:cc:dd:ee:ff dev eth0 nud permanent

# Duplicate address detection (APIPA/DHCP conflict check)
arping -D -I eth0 192.168.1.50
# Exit code 1 = duplicate found (another host has this IP)

# Capture ARP packets
sudo tcpdump -i eth0 -n arp -v
# Shows full ARP request and reply details
```

**Wrong vs Right - ARP spoofing defense:**

```bash
# BAD: rely on ARP protocol to be correct (no defense)
# Default network has zero ARP authentication.
# Any host on LAN can spoof any IP → MITM possible.

# GOOD: static ARP for critical infrastructure IPs
# Lock gateway MAC to prevent ARP poison for gateway:
sudo ip neigh add 192.168.1.1 \
  lladdr aa:bb:cc:dd:ee:ff \
  dev eth0 nud permanent
# Now attacker's ARP replies for 192.168.1.1 are ignored.

# BETTER: Dynamic ARP Inspection (DAI) on managed switches
# Switch validates ARP replies against DHCP snooping table
# If ARP reply doesn't match DHCP-assigned MAC:IP → drop
# Requires managed switch with DAI feature support.

# BEST: Network segmentation + VLANs
# ARP is broadcast - only hosts on same VLAN see each other
# Segmenting untrusted devices into separate VLANs
# limits ARP spoofing blast radius.
```

**Gratuitous ARP - used by failover systems:**

```
┌──────────────────────────────────────────────────────────┐
│  Gratuitous ARP (GARP)                                   │
├──────────────────────────────────────────────────────────┤
│  Sent without a request. ARP reply claiming your own IP. │
│                                                          │
│  When used:                                              │
│  - VM or container starts: "I have IP 10.0.1.5"         │
│    → all hosts update ARP cache (avoids delay)           │
│  - HA failover: new primary sends GARP to redirect       │
│    traffic from old primary's MAC to new primary         │
│  - Load balancer VIP failover: "VIP 10.0.1.100 is now   │
│    at this MAC" → all clients update instantly           │
│  - AWS elastic IP reassignment triggers GARP             │
│                                                          │
│  The same mechanism used for failover is also used for   │
│  ARP spoofing attacks. There is no way to authenticate   │
│  gratuitous ARP at the protocol level.                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ARP in cloud environments:**

```
┌──────────────────────────────────────────────────────────┐
│  AWS VPC ARP Behavior                                    │
├──────────────────────────────────────────────────────────┤
│  AWS VPC uses a proxy ARP model:                        │
│  - EC2 instances don't see true ARP broadcasts          │
│  - AWS hypervisor responds to ARP requests on behalf    │
│    of all IPs in the VPC                                │
│  - Security groups filter at hypervisor level           │
│  - ARP spoofing attacks are blocked by VPC              │
│    (cannot impersonate another instance's IP)           │
│                                                          │
│  This is why ARP is "simpler" in AWS:                   │
│  - You rarely see ARP conflicts in VPCs                 │
│  - AWS IPAM prevents duplicate IP assignment            │
│  - IP source checking (anti-spoofing) is enforced       │
│    unless explicitly disabled (for NAT instances)       │
└──────────────────────────────────────────────────────────┘
```

---

### ⚖️ Comparison Table

| | ARP (IPv4) | NDP (IPv6) |
|---|---|---|
| **Protocol** | ARP (Layer 2/3) | NDP via ICMPv6 |
| **Discovery** | Who has IP X? | Neighbor Solicitation |
| **Reply** | I have IP X at MAC Y | Neighbor Advertisement |
| **Cache** | ARP table | Neighbor cache |
| **GARP equivalent** | Gratuitous ARP | Unsolicited NA |
| **Security** | No authentication | SEcure Neighbor Discovery (SEND) optional |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ARP works across subnets | ARP is strictly L2 (broadcast domain). You will never see an ARP for an IP on a different subnet. Traffic to different subnets always goes through the gateway, and only the gateway's MAC appears in your ARP table for those destinations. |
| ARP cache is always fresh | ARP entries go STALE after ~30s on Linux (then removed after another 30s). Stale entries are re-probed lazily. If a host changes MAC (NIC replacement, VM migration), traffic continues using old MAC until ARP cache expires. |
| ARP only works with Ethernet | ARP was designed for Ethernet. Other link layers have equivalent protocols (Frame Relay has InARP, ATM has LANE). WiFi uses ARP the same way. The principle is universal: L3 address needs an L2 address for delivery. |

---

### 🚨 Failure Modes & Diagnosis

**ARP Cache Stale - Connectivity Drops After VM Migration**

**Symptom:** After a VM migrates to a new host (different
physical server), clients that were connected get RST or
timeout errors for 30-60 seconds. After 60 seconds, traffic
resumes. Happens during live VM migration or container
restart on different node.

**Root Cause:** VM has same IP but new MAC address (different
physical host NIC). Existing clients have old MAC in ARP
cache. Send frames to old MAC → dropped. After ARP cache
expires (60s default), clients re-ARP and get new MAC.

**Diagnosis:**
```bash
# Check ARP entry age
ip neigh show
# 192.168.1.100 dev eth0 lladdr old:mac:address STALE
# STALE = not recently confirmed

# Force re-ARP immediately
sudo ip neigh del 192.168.1.100 dev eth0
# Next packet will trigger ARP request and get new MAC

# Or watch for gratuitous ARP from migrated VM
sudo tcpdump -i eth0 -n arp
# Migrated VM should send GARP on startup
```

**Prevention:**
Configure VM/container orchestration to send gratuitous
ARP on startup (most do this by default). Kubernetes
pods send gratuitous ARP via their CNI plugin. For VMware:
enable gratuitous ARP after vMotion (default).

---

### 🔗 Related Keywords

**Prerequisites:**
- `MAC Address` - ARP resolves to MAC addresses
- `IP Address` - ARP resolves from IP addresses

**Builds On This:**
- `Network Segmentation and Firewall Rules` - DAI
  (Dynamic ARP Inspection) is a firewall-level ARP defense

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT DOES │ Maps IP → MAC within a subnet             │
├──────────────┼───────────────────────────────────────────┤
│ HOW          │ Broadcast "who has IP X?" → unicast reply │
│              │ "I have X, my MAC is Y" → cache entry     │
├──────────────┼───────────────────────────────────────────┤
│ CACHE TTL    │ ~30s (REACHABLE → STALE → re-probe)       │
├──────────────┼───────────────────────────────────────────┤
│ COMMANDS     │ ip neigh show, arping -D, tcpdump arp     │
├──────────────┼───────────────────────────────────────────┤
│ GARP         │ Unsolicited ARP claiming own IP. Used for │
│              │ HA failover. Same mechanism as spoofing.  │
├──────────────┼───────────────────────────────────────────┤
│ SECURITY     │ ARP spoofing: send fake ARP replies to    │
│              │ redirect traffic. Defense: static ARP,    │
│              │ DAI on managed switches, VLAN segmentation│
├──────────────┼───────────────────────────────────────────┤
│ LIMIT        │ Same broadcast domain only. Cannot ARP    │
│              │ across subnets (uses gateway MAC instead) │
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"ARP resolves IPv4 addresses to MAC addresses within a
subnet by broadcasting 'Who has IP X?' and caching the
reply. When sending to a different subnet, you ARP for
the gateway's MAC (not the remote host's MAC), which
is why your ARP table only shows local neighbors. ARP
has no authentication - the most recent reply wins - making
ARP spoofing (fake ARP replies redirect traffic to an
attacker) a fundamental LAN security threat. Defenses:
static ARP for critical IPs, Dynamic ARP Inspection (DAI)
on managed switches, and VLAN segmentation to limit blast
radius. Gratuitous ARP (claiming your own IP) is used
legitimately by HA failover and VM migration to update
all ARP caches immediately."