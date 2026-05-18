---
id: NET-024
title: "Subnet and CIDR Notation"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-009
used_by: NET-025, NET-028, NET-045, NET-052
related: NET-009, NET-025, NET-028
tags:
  - networking
  - ip
  - subnetting
  - cidr
  - routing
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/net/subnet-and-cidr-notation/
---

**⚡ TL;DR** - CIDR notation `10.0.0.0/24` means: first
24 bits are the network prefix (shared by all hosts in
this subnet), last 8 bits are the host portion (256
addresses, 254 usable). The prefix length determines the
subnet size. Subnetting enables network segmentation,
routing aggregation, and access control. Every cloud VPC,
firewall rule, and security group uses CIDR.

| #024 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | IP Address | |
| **Used by:** | NAT, Routing Basics, VPN Fundamentals, Network Segmentation and Firewall Rules | |
| **Related:** | IP Address, NAT, Routing Basics | |

---

### 🔥 The Problem This Solves

Without subnetting, the original IPv4 design had three
fixed class sizes (Class A: /8 = 16M hosts, Class B: /16 =
65K hosts, Class C: /24 = 256 hosts). A company needing
1000 IPs had to waste 64K by getting a Class B. This
wasted ~94% of the address space and filled routing tables.
CIDR (Classless Inter-Domain Routing) replaced fixed
classes with variable-length prefix lengths, enabling
exact-fit subnets and route aggregation. Every modern
network uses CIDR.

---

### 📘 Textbook Definition

**CIDR (Classless Inter-Domain Routing)** notation
`A.B.C.D/prefix` represents a network range where the
first `prefix` bits (the **network portion**) are fixed
and the remaining `32-prefix` bits (the **host portion**)
vary across the address range. A **subnet** is a contiguous
block of IP addresses sharing the same network prefix.
The **subnet mask** is the bitmask equivalent:
`/24 = 255.255.255.0`, `/16 = 255.255.0.0`. Subnetting
divides a large address range into smaller segments for
routing isolation, security, and address management.

---

### ⏱️ Understand It in 30 Seconds

**CIDR in binary:**
```
10.0.1.50/24 broken down:

IP:      10.0.1.50
Binary:  00001010.00000000.00000001.00110010
Prefix:  ├─────────── /24 (network) ────────┤├── host ─┤
         00001010.00000000.00000001.00000000  (network)
         00001010.00000000.00000001.11111111  (broadcast)

Network: 10.0.1.0  (first address, reserved)
Host range: 10.0.1.1 to 10.0.1.254 (254 usable hosts)
Broadcast: 10.0.1.255  (last address, reserved)
```

**The key formula:**
```
Hosts per subnet = 2^(32-prefix) - 2
  (subtract 2: network address + broadcast address)

/24: 2^8 - 2 = 254 hosts
/16: 2^16 - 2 = 65,534 hosts
/28: 2^4 - 2 = 14 hosts (smallest useful subnet)
/32: 2^0 - 2 = 0 hosts (single host route)
/0:  entire IPv4 space (default route)
```

---

### 🔩 First Principles Explanation

**Subnet mask and CIDR equivalents:**

```
┌──────────────────────────────────────────────────────────┐
│  CIDR Reference Table                                    │
├────────┬──────────────────┬──────────┬───────────────────┤
│  CIDR  │  Subnet Mask     │  Hosts   │  Typical Use       │
├────────┼──────────────────┼──────────┼───────────────────┤
│  /8    │  255.0.0.0       │  16.7M   │  ISP block (class A)│
│  /16   │  255.255.0.0     │  65,534  │  Large VPC/campus  │
│  /17   │  255.255.128.0   │  32,766  │  Large subnet      │
│  /20   │  255.255.240.0   │  4,094   │  Medium VPC subnet │
│  /22   │  255.255.252.0   │  1,022   │  Office/datacenter │
│  /24   │  255.255.255.0   │  254     │  Standard LAN/VLAN │
│  /25   │  255.255.255.128 │  126     │  Split /24        │
│  /26   │  255.255.255.192 │  62      │  Small segment     │
│  /27   │  255.255.255.224 │  30      │  Very small subnet │
│  /28   │  255.255.255.240 │  14      │  NAT gateway, bastion│
│  /29   │  255.255.255.248 │  6       │  Point-to-point link│
│  /30   │  255.255.255.252 │  2       │  Router-to-router  │
│  /31   │  255.255.255.254 │  2 (no BC)│  P2P (RFC 3021)   │
│  /32   │  255.255.255.255 │  1       │  Single host route │
└────────┴──────────────────┴──────────┴───────────────────┘
```

**How subnetting works - splitting /24 into /25:**

```
┌──────────────────────────────────────────────────────────┐
│  Subnet Split Example                                    │
├──────────────────────────────────────────────────────────┤
│  Parent: 192.168.1.0/24 (256 addresses)                 │
│                                                          │
│  Split into two /25 subnets:                            │
│                                                          │
│  Subnet A: 192.168.1.0/25                               │
│    Range: 192.168.1.0 - 192.168.1.127                   │
│    Hosts: 192.168.1.1 - 192.168.1.126 (126 usable)     │
│    Broadcast: 192.168.1.127                             │
│                                                          │
│  Subnet B: 192.168.1.128/25                             │
│    Range: 192.168.1.128 - 192.168.1.255                 │
│    Hosts: 192.168.1.129 - 192.168.1.254 (126 usable)   │
│    Broadcast: 192.168.1.255                             │
│                                                          │
│  Split one more time (/25 → two /26):                   │
│  192.168.1.0/26   (62 hosts: .1 to .62)                │
│  192.168.1.64/26  (62 hosts: .65 to .126)              │
│  192.168.1.128/26 (62 hosts: .129 to .190)             │
│  192.168.1.192/26 (62 hosts: .193 to .254)             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**AWS VPC design scenario:**

You're designing an AWS VPC with these requirements:
- 3 public subnets (one per AZ) for load balancers
- 3 private subnets (one per AZ) for application servers
- 3 private subnets (one per AZ) for databases
- Room to grow

**Minimum design with 10.0.0.0/16:**

```
VPC: 10.0.0.0/16 (65,534 total IPs)

Public subnets (LB):
  10.0.1.0/24  - AZ-a (254 hosts)
  10.0.2.0/24  - AZ-b (254 hosts)
  10.0.3.0/24  - AZ-c (254 hosts)

Private subnets (app):
  10.0.11.0/24 - AZ-a (254 hosts)
  10.0.12.0/24 - AZ-b
  10.0.13.0/24 - AZ-c

Private subnets (DB):
  10.0.21.0/24 - AZ-a (254 hosts)
  10.0.22.0/24 - AZ-b
  10.0.23.0/24 - AZ-c

Total used: 9 × 256 = 2,304 addresses
Remaining: 65,534 - 2,304 = 63,230 for growth
```

**THE INSIGHT:**
The number pattern (1x, 1x, 2x) creates a visual layout
that makes routing rules and security group descriptions
readable: "allow 10.0.1.0/22 from app subnets" covers
all three app subnets (11, 12, 13). This intentional
alignment of subnet addresses to CIDR boundaries makes
aggregation trivial. Random subnet assignment makes every
firewall rule a list.

---

### 🧠 Mental Model / Analogy

> A subnet is like a city postal code system:
>
> IP address: 10.0.1.50
> is like: Country.State.City.House
>
> /24 subnetting says: "the first 24 bits = postal code"
> Everyone in 10.0.1.0/24 has the same postal code.
> The router delivers mail to the right city (subnet),
> then ARP finds the right house (host within subnet).
>
> /16 is a larger city (65K houses).
> /24 is a neighborhood (254 houses).
> /28 is a cul-de-sac (14 houses).
> /32 is a single address.

---

### ⚙️ How It Works (Mechanism)

**Subnet membership check (how routers decide):**

```bash
# Check if an IP is in a subnet
# 192.168.1.100 in 192.168.1.0/24?
# Network: 192.168.1.100 AND 255.255.255.0 = 192.168.1.0
# Same as subnet network address? YES → in subnet.

# Linux commands for subnet inspection
ip addr show                  # see your IP and prefix
ip route show                 # routing table (CIDR entries)
ip route get 8.8.8.8         # which route handles this IP?

# Python: check if IP in CIDR (without external library)
import ipaddress
net = ipaddress.ip_network('10.0.1.0/24')
ip = ipaddress.ip_address('10.0.1.50')
print(ip in net)              # True

# Check subnet info
print(net.network_address)    # 10.0.1.0
print(net.broadcast_address)  # 10.0.1.255
print(net.num_addresses)      # 256
print(list(net.hosts()))[:3]  # [10.0.1.1, 10.0.1.2, ...]
```

**Wrong vs Right - AWS security group CIDR rules:**

```yaml
# BAD: list every individual IP in security group
# SecurityGroupIngress:
#   - CidrIp: 10.0.1.5/32
#   - CidrIp: 10.0.1.6/32
#   - CidrIp: 10.0.1.7/32
#   ... (100 rules for 100 app servers)
# Maintenance nightmare. EC2 security group limit: 60 rules.

# GOOD: use subnet CIDR - all app servers in one rule
# SecurityGroupIngress:
#   - Description: "Allow from app subnet"
#     IpProtocol: tcp
#     FromPort: 5432
#     ToPort: 5432
#     CidrIp: 10.0.11.0/24   ← entire app subnet
#     # All current AND future app servers allowed
#     # Subnet CIDR is the correct granularity for SG rules
```

**Route aggregation - why CIDR alignment matters:**

```
BAD: Random subnet assignment
  10.0.17.0/24  - app AZ-a
  10.0.43.0/24  - app AZ-b
  10.0.91.0/24  - app AZ-c
Firewall rule: must list all 3 separately
  allow tcp from {10.0.17.0/24, 10.0.43.0/24, 10.0.91.0/24}

GOOD: CIDR-aligned assignment
  10.0.11.0/24  - app AZ-a
  10.0.12.0/24  - app AZ-b
  10.0.13.0/24  - app AZ-c
Firewall rule: aggregate into supernet
  allow tcp from 10.0.12.0/22  (covers .11, .12, .13, .14)
  [Or use 10.0.8.0/21 to cover .8-15 range]
One rule covers all current and future app subnets.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**AWS VPC routing with subnets:**

```
┌──────────────────────────────────────────────────────────┐
│  AWS VPC Routing (simplified)                            │
├──────────────────────────────────────────────────────────┤
│  10.0.0.0/16 VPC                                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Route Table (main)                             │    │
│  │    10.0.0.0/16  →  local (all VPC traffic)     │    │
│  │    0.0.0.0/0    →  nat-gateway (internet via NAT│    │
│  └─────────────────────────────────────────────────┘    │
│  ┌──────────────────────────┐ ┌────────────────────┐    │
│  │ Public RT (for LB subnet)│ │                    │    │
│  │   10.0.0.0/16  → local  │ │  Private Subnet    │    │
│  │   0.0.0.0/0  → igw      │ │  10.0.11.0/24      │    │
│  │                          │ │  (no IGW route)    │    │
│  │ Public Subnet            │ │                    │    │
│  │ 10.0.1.0/24 (LB tier)   │ └────────────────────┘    │
│  └──────────────────────────┘                           │
│                                                          │
│  Key insight: route tables + subnets = network zones    │
│  Public subnet: has 0.0.0.0/0 → IGW (internet-accessible│
│  Private subnet: has 0.0.0.0/0 → NAT (outbound only)   │
│  Isolated subnet: no 0.0.0.0/0 route (DB tier)         │
└──────────────────────────────────────────────────────────┘
```

**WHAT CHANGES AT SCALE:**
At cloud scale, subnet design is done once and is hard to
change (renumbering VPCs is a multi-hour operation). AWS
does not allow overlapping CIDR blocks in a VPC, and VPC
peering requires non-overlapping CIDRs across VPCs. This
is why RFC 1918 address space planning happens before
deployment. Teams that don't plan CIDRs end up with VPCs
that cannot be peered (overlapping 10.0.0.0/16 between
dev and prod is a common mistake that prevents direct VPC
peering).

---

### ⚖️ Comparison Table

| Prefix | Subnet Size | Usable Hosts | Typical Use |
|---|---|---|---|
| /8 | 16.7M | 16.7M | ISP allocation |
| /16 | 65,536 | 65,534 | Large VPC |
| /20 | 4,096 | 4,094 | Medium VPC subnet |
| /24 | 256 | 254 | Standard subnet (most common) |
| /27 | 32 | 30 | Small team subnet |
| /28 | 16 | 14 | NAT GW, bastion |
| /30 | 4 | 2 | Router-to-router |
| /32 | 1 | 1 | Single host, static route |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| /24 always means "a network" | /24 is just a prefix length = 254 usable hosts. Any prefix length is valid: /25, /27, /28. The "natural" class boundaries (8, 16, 24) are historical artifacts from pre-CIDR days. |
| Network address is usable | The network address (first IP) and broadcast address (last IP) are reserved and cannot be assigned to hosts. AWS also reserves 3 more (second, third, last-before-broadcast) for a total of 5 reserved per subnet. |
| Larger prefix = larger subnet | Counterintuitive: SMALLER prefix number = MORE IPs. /8 is huge (16M IPs). /28 is tiny (14 IPs). Think of it as "8 bits fixed = 24 bits variable." |

---

### 🚨 Failure Modes & Diagnosis

**Overlapping CIDR - No VPC Peering Possible**

**Symptom:** VPC peering request fails with "overlapping
CIDR." Instances in the two VPCs cannot communicate
directly. Common in organizations that deployed multiple
teams' VPCs independently.

**Root Cause:** Both VPCs use `10.0.0.0/16`. When peering,
the route `10.0.0.0/16` would match traffic for BOTH VPCs
and the router cannot know which one to use.

**Diagnosis:**
```bash
# AWS CLI: check VPC CIDRs
aws ec2 describe-vpcs --query \
  'Vpcs[*].[VpcId,CidrBlock,Tags]' \
  --output table
```

**Fix:** No easy fix once deployed. Options:
1. Use AWS Transit Gateway with NAT between overlapping CIDRs
2. Re-IP one VPC (large migration effort)
3. Prevention: define a corporate CIDR allocation scheme
   before any team creates VPCs

**Prevention plan:**
```
Corporate RFC 1918 allocation:
  10.0.0.0/8 - all corporate use
  ├── 10.0.0.0/12 - AWS us-east-1 (10.0-15.x.x)
  ├── 10.16.0.0/12 - AWS eu-west-1 (10.16-31.x.x)
  ├── 10.32.0.0/12 - AWS us-west-2 (10.32-47.x.x)
  └── 10.128.0.0/9 - on-premises (10.128-255.x.x)

Per-team VPC (within us-east-1):
  team-a: 10.0.0.0/16  (10.0.x.x)
  team-b: 10.1.0.0/16  (10.1.x.x)
  team-c: 10.2.0.0/16  (10.2.x.x)
  [Never overlaps. Can always peer.]
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IP Address` - IPv4 structure required to understand CIDR

**Builds On This:**
- `NAT` - NAT uses subnet knowledge to route private IPs
- `Routing Basics` - routing table entries are CIDR ranges
- `VPN Fundamentals` - VPN split tunneling uses CIDR routing
- `Network Segmentation and Firewall Rules` - rules use CIDR

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMAT       │ A.B.C.D/prefix - prefix = network bits    │
├──────────────┼───────────────────────────────────────────┤
│ HOSTS        │ 2^(32-prefix) - 2 (network + broadcast)   │
├──────────────┼───────────────────────────────────────────┤
│ COMMON       │ /16=65534, /24=254, /28=14, /32=single    │
├──────────────┼───────────────────────────────────────────┤
│ SPLIT        │ /24 → two /25, /25 → two /26 etc.        │
├──────────────┼───────────────────────────────────────────┤
│ RESERVED     │ Network (first) + Broadcast (last) + AWS  │
│              │ reserves 3 more = 5 reserved per subnet   │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Overlapping VPC CIDRs - prevents peering  │
│              │ Unplanned CIDRs - unaligned aggregation   │
├──────────────┼───────────────────────────────────────────┤
│ CLOUD RULE   │ Plan CIDR allocation before deployment.   │
│              │ Re-numbering a VPC is extremely painful.  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `A.B.C.D/N` = first N bits are shared by all hosts in
   the subnet. Hosts = 2^(32-N) - 2.
2. Smaller number = larger subnet: /16 >> /24 >> /28.
3. CIDR-align your cloud subnets (10.0.11.0/24, 10.0.12.0/24,
   10.0.13.0/24) so they aggregate to one CIDR in firewall
   rules: 10.0.12.0/22 covers all three.

**Interview one-liner:**
"CIDR notation `10.0.1.0/24` means the first 24 bits are
the network prefix (fixed for all hosts in the subnet),
leaving 8 bits for 254 usable host addresses. Subnetting
enables network segmentation (separate public/private zones),
routing aggregation (multiple subnets in one route entry),
and security group rules targeting entire subnets rather
than individual IPs. The critical operational mistake is
overlapping VPC CIDR blocks - two VPCs with the same /16
cannot be directly peered; this requires upfront CIDR
allocation planning before any VPC is created."