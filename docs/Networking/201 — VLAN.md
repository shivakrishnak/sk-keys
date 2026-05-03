---
layout: default
title: "VLAN"
parent: "Networking"
nav_order: 201
permalink: /networking/vlan/
number: "0201"
category: Networking
difficulty: ★★★
depends_on: IP Addressing, Network Topologies, OSI Model
used_by: Cloud — AWS, Networking, Distributed Systems
related: Overlay Networks, Subnet & CIDR, Firewall, Network Policies, VPN
tags:
  - networking
  - vlan
  - 802.1q
  - network-segmentation
  - trunking
  - layer2
---

# 201 — VLAN

⚡ TL;DR — A VLAN (Virtual Local Area Network) segments a single physical switch into multiple isolated broadcast domains. Traffic from different VLANs cannot reach each other at Layer 2 without routing (Layer 3). Implemented via 802.1Q tagging: a 4-byte tag added to Ethernet frames identifies the VLAN (12-bit ID → 4096 VLANs max). Used for: isolating departments (HR, Finance, Engineering), separating environments (prod/dev), and reducing broadcast traffic. VXLANs extended this concept to 24-bit IDs (16M virtual networks) for cloud scale.

---

### 🔥 The Problem This Solves

Without VLANs, all devices on the same switch are in the same broadcast domain. ARP requests, DHCP, and other broadcast traffic reach ALL devices. Security: an employee on floor 1 can sniff traffic from the accounting server on the same switch. Scale: a switch with 500 devices processes broadcasts from all 500 — CPU waste. VLANs solve both: segment devices into isolated groups so broadcasts are contained to groups, and Layer 2 isolation prevents devices in different VLANs from communicating without going through a router (where ACLs can be applied).

---

### 📘 Textbook Definition

**VLAN (Virtual Local Area Network):** A logical partition of a physical network at Layer 2, creating separate broadcast domains on the same physical switch infrastructure. Defined by IEEE 802.1Q standard. Each VLAN behaves as if it were a separate physical network; traffic between VLANs requires Layer 3 routing (inter-VLAN routing).

**802.1Q Tagging:** A 4-byte field inserted into Ethernet frame headers (after source MAC), containing: TPID (0x8100 identifying 802.1Q frame) + TCI (Tag Control Information) including 3-bit PCP (priority) and 12-bit VID (VLAN ID, 0-4095).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
VLAN = logical partition of a physical switch into isolated groups. Different VLANs can't talk to each other at Layer 2 — they need routing. 802.1Q tags Ethernet frames with a VLAN ID.

**One analogy:**

> A physical switch with VLANs is like a large office building that shares physical walls, ceilings, and floors, but has different ventilation and intercom systems per floor. Sound (broadcast traffic) only travels within one floor's intercom (VLAN). To communicate between floors, you need the building's central communication system (router/Layer 3 switch). Someone on floor 3 (VLAN 30) can't eavesdrop on floor 5's conversations (VLAN 50).

---

### 🔩 First Principles Explanation

**BROADCAST DOMAINS WITHOUT VLAN:**

```
All devices on a switch share one broadcast domain.
When PC-A sends ARP: "Who has 10.0.0.5?" → broadcast to ALL ports.
200 devices on switch = 200 devices process EVERY ARP/DHCP broadcast.
Problems:
  - Wasted CPU on all devices for irrelevant broadcasts
  - Security: any device can see (and spoof) L2 traffic
  - ARP poisoning attacks possible across entire network
```

**VLAN SEGMENTATION:**

```
VLAN 10 (HR):      PC-HR1 (10.0.10.5) ─── VLAN 10 group
VLAN 20 (Finance): PC-Finance1 (10.0.20.5) ─── VLAN 20 group
VLAN 30 (Eng):     PC-Eng1 (10.0.30.5) ─── VLAN 30 group

ARP from PC-HR1: only reaches VLAN 10 members
Finance and Engineering devices: never see VLAN 10 broadcasts
Traffic between VLANs: MUST go through L3 router
  → Router can apply ACLs: "Finance cannot reach Engineering VLAN"
```

**802.1Q FRAME TAGGING:**

```
Standard Ethernet frame:
[Dest MAC (6)] [Src MAC (6)] [Type (2)] [Payload] [FCS]

802.1Q Tagged frame:
[Dest MAC (6)] [Src MAC (6)] [TPID: 0x8100 (2)] [TCI (2)] [Type (2)] [Payload] [FCS]

TCI breakdown (2 bytes = 16 bits):
  Bits 15-13: PCP (Priority Code Point) — QoS priority 0-7
  Bit 12:     DEI (Drop Eligible Indicator) — congestion discard
  Bits 11-0:  VID (VLAN Identifier) — 0-4095 (4096 VLANs)
  Reserved:   VID 0 (priority frame), VID 1 (default), VID 4095

Access port vs Trunk port:
  Access port: untagged; belongs to exactly ONE VLAN
    → End device (PC, server) connects to access port
    → Switch adds VLAN tag internally; strips it before sending to device
    → Device doesn't know it's on a VLAN

  Trunk port: tagged; carries traffic for MULTIPLE VLANs
    → Switch-to-switch connections use trunks
    → Traffic for all VLANs travels on same physical link, differentiated by tag
    → Native VLAN: one VLAN that sends untagged on trunk (backward compat.)
```

**INTER-VLAN ROUTING:**

```
Option 1: Router-on-a-stick
  Single router with sub-interfaces, one per VLAN
  Router: eth0.10 (VLAN 10), eth0.20 (VLAN 20), eth0.30 (VLAN 30)
  All traffic between VLANs routes through router
  Bottleneck: all inter-VLAN traffic goes through one physical link

Option 2: Layer 3 Switch (SVIs — Switched Virtual Interfaces)
  Modern enterprise switches include L3 routing capability
  Each VLAN has an SVI: virtual interface with IP address
  Routing happens inside the switch at hardware speed
  Better performance: no external router hairpin
  Example:
    interface Vlan10
      ip address 10.0.10.1 255.255.255.0
    interface Vlan20
      ip address 10.0.20.1 255.255.255.0

Option 3: Separate router per VLAN (expensive, for isolated environments)
  When VLANs need completely separate routing tables (security isolation)
```

**VLAN IN DATA CENTERS AND CLOUD:**

```
Problem: 12-bit VID = max 4096 VLANs. A large cloud provider needs
  millions of isolated tenant networks. 4096 is nowhere near enough.

Solution: VXLAN (Virtual Extensible LAN)
  24-bit VNI (Virtual Network Identifier) = 16 million overlay networks
  Encapsulates L2 frames in UDP
  Works at scale in AWS VPC, Azure VNet, OpenStack Neutron

AWS VPC ↔ VLAN relationship:
  Physical AWS underlay uses VLANs internally (or proprietary equiv.)
  You see VPCs as your isolated network (equivalent of VLAN concept)
  AWS Nitro hypervisor enforces isolation via hardware (SR-IOV + custom ASIC)
  VPC Peering / Transit Gateway: inter-VPC routing (equiv. of inter-VLAN routing)
```

---

### 🧪 Thought Experiment

**VLAN HOPPING ATTACK:**
VLAN hopping: an attacker on VLAN 10 attempts to reach VLAN 20 by sending double-tagged 802.1Q frames. Frame is tagged with VLAN 20 outer tag and VLAN 10 inner tag. When the first switch strips the outer tag, it sees VLAN 10 — but doesn't forward to VLAN 20. However, if the attacker connects to a port configured as a trunk port (misconfiguration), the switch treats the outer VLAN tag as legitimate. Prevention: never put user devices on trunk ports; use dedicated native VLANs (not VLAN 1); explicitly disable DTP (Dynamic Trunking Protocol) on access ports.

---

### 🧠 Mental Model / Analogy

> VLANs are like virtual office partitions that are invisible but acoustically isolating. All teams sit in the same physical open-plan office (same switch), but each team (VLAN) has an invisible soundproof bubble. They can see each other but can't hear each other (no L2 broadcast cross-VLAN). To pass a memo between teams (inter-VLAN traffic), it must go through the receptionist (router), who can check if the teams are allowed to communicate and apply access rules. 802.1Q tags are like sticky notes on envelopes identifying which team's mail this belongs to.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** VLANs split a physical switch into isolated groups. Devices in different VLANs can't communicate without routing through a router. Used for: isolating departments, separating environments (prod/dev), security. 802.1Q adds a tag to Ethernet frames to identify the VLAN.

**Level 2:** Switch port types: access port (one VLAN, device doesn't know) vs trunk port (multiple VLANs, tagged). Inter-VLAN routing: router-on-a-stick (inefficient) or Layer 3 switch with SVIs (better). Native VLAN: the one VLAN that travels untagged on trunk ports (legacy; security concern if misconfigured).

**Level 3:** Spanning Tree Protocol (STP) per VLAN: without STP, VLANs could form loops (broadcast storm). IEEE 802.1D STP and Rapid STP (RSTP 802.1w) prevent loops by blocking redundant paths. Per-VLAN STP: Cisco PVST+ runs separate STP instance per VLAN, enabling load balancing across redundant links (different VLANs use different active paths). MSTP (802.1s): maps VLANs to STP instances for better scalability (100 VLANs can share 2 STP instances instead of 100).

**Level 4:** Hardware ASIC implementation: modern switch ASICs (Broadcom Trident/Tomahawk) process VLAN tagging at line-rate in dedicated hardware. A 128-port 100G switch can process 12.8 Tbps of VLAN-tagged traffic without CPU involvement. VLAN tables in TCAM (Ternary Content-Addressable Memory) for O(1) VLAN lookup. Q-in-Q (802.1ad): double-tagging for provider bridges — service provider adds outer VLAN tag (S-VLAN) while customer's tag (C-VLAN) remains intact. Allows providers to deliver VLAN services across their network while customers keep their own VLAN numbering. This is the Layer 2 equivalent of NAT in IP networking.

---

### ⚙️ How It Works (Mechanism)

```bash
# Linux: create VLAN sub-interface (802.1Q)
# Useful for connecting Linux to a trunk port or for testing

# Load 802.1Q kernel module
modprobe 8021q

# Create VLAN 10 sub-interface on eth0
ip link add link eth0 name eth0.10 type vlan id 10
ip addr add 10.0.10.100/24 dev eth0.10
ip link set eth0.10 up

# Check VLAN configuration
cat /proc/net/vlan/eth0.10

# Capture 802.1Q tagged traffic
tcpdump -i eth0 -e vlan
# Shows: 802.1Q vlan#10, src MAC, dst MAC, payload

# Linux bridge with VLANs (useful for VM networking)
brctl addbr br0
ip link set br0 up
bridge vlan add dev eth0 vid 10 pvid untagged master  # access port
bridge vlan add dev veth0 vid 10 pvid untagged master  # VM on VLAN 10
bridge vlan add dev veth1 vid 20 pvid untagged master  # VM on VLAN 20
bridge vlan show  # show VLAN membership

# OpenVSwitch (used in OpenStack, KVM): VLAN config
ovs-vsctl add-br br0
ovs-vsctl add-port br0 eth0 trunk=10,20,30  # trunk port carrying VLANs 10,20,30
ovs-vsctl add-port br0 vnet0 tag=10  # VM access port on VLAN 10
ovs-vsctl show  # show bridge config
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Inter-VLAN routing via Layer 3 switch:

PC-HR (VLAN 10, 10.0.10.5) pings Finance-Server (VLAN 20, 10.0.20.5)

1. PC-HR sends: src=10.0.10.5, dst=10.0.20.5
2. PC's default GW: 10.0.10.1 (SVI for VLAN 10 on L3 switch)
   → ARP: "who has 10.0.10.1?"
3. Switch SVI responds (proxy ARP): "10.0.10.1 is at [switch mac]"
4. PC sends frame to switch mac (untagged on access port)
5. Switch receives on VLAN 10 access port → adds VLAN 10 tag internally
6. L3 switch: dst IP 10.0.20.5 → route: via VLAN 20 SVI (10.0.20.1)
7. Switch: outgoing VLAN 20 → find Finance-Server's MAC (ARP if needed)
8. Switch forwards frame to Finance-Server's access port (VLAN 20)
   → strips VLAN 20 tag before sending (access port = untagged to device)
9. Finance-Server receives: src=10.0.10.5 (HR PC's IP)

Across switch trunks:
  If switches are connected via trunk port:
  Switch 1 sends 802.1Q tagged frame (VLAN=10 tag) across trunk link
  Switch 2 receives tagged frame → identifies VLAN 10 → forwards to VLAN 10 ports
```

---

### 💻 Code Example

```python
# Parse 802.1Q VLAN-tagged Ethernet frames (educational)
import struct

def parse_ethernet_frame(raw_bytes: bytes) -> dict:
    """Parse Ethernet frame, detecting 802.1Q VLAN tags."""
    if len(raw_bytes) < 14:
        return {"error": "Too short"}

    dst_mac = ':'.join(f'{b:02x}' for b in raw_bytes[0:6])
    src_mac = ':'.join(f'{b:02x}' for b in raw_bytes[6:12])
    ethertype = struct.unpack('>H', raw_bytes[12:14])[0]

    vlan_tag = None
    offset = 14

    # Check for 802.1Q tag (TPID = 0x8100)
    if ethertype == 0x8100:
        tci = struct.unpack('>H', raw_bytes[14:16])[0]
        vlan_id = tci & 0x0FFF           # last 12 bits
        pcp = (tci >> 13) & 0x07         # first 3 bits (priority)
        dei = (tci >> 12) & 0x01         # bit 12 (drop eligible)
        vlan_tag = {"vlan_id": vlan_id, "pcp": pcp, "dei": dei}

        # Real ethertype is next 2 bytes
        ethertype = struct.unpack('>H', raw_bytes[16:18])[0]
        offset = 18

    payload = raw_bytes[offset:]

    return {
        "dst_mac": dst_mac,
        "src_mac": src_mac,
        "ethertype": hex(ethertype),
        "vlan_tag": vlan_tag,
        "payload_length": len(payload),
        "is_tagged": vlan_tag is not None,
    }

# Example: 802.1Q tagged frame (VLAN ID=10, PCP=0)
# Dest MAC + Src MAC + 0x8100 (802.1Q) + TCI(VLAN=10) + IP type (0x0800)
example_frame = bytes([
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # dst MAC (broadcast)
    0x00, 0x11, 0x22, 0x33, 0x44, 0x55,  # src MAC
    0x81, 0x00,                           # TPID: 802.1Q
    0x00, 0x0a,                           # TCI: PCP=0, DEI=0, VID=10
    0x08, 0x00,                           # real EtherType: IPv4
    # payload...
])

result = parse_ethernet_frame(example_frame)
print(f"VLAN ID: {result['vlan_tag']['vlan_id']}")  # VLAN ID: 10
print(f"Tagged: {result['is_tagged']}")              # Tagged: True
```

---

### ⚖️ Comparison Table

| Feature                         | VLAN (802.1Q)                          | VXLAN                    | VPC (AWS/GCP)                |
| ------------------------------- | -------------------------------------- | ------------------------ | ---------------------------- |
| ID space                        | 12-bit: 4096 VLANs                     | 24-bit: 16M VNIs         | Unlimited (software-defined) |
| Layer                           | L2 (Ethernet)                          | L2 over L3 (UDP)         | L3 (IP routing)              |
| Scope                           | Within datacenter/campus               | Datacenter + cloud       | Cloud-native                 |
| Routing required between groups | Yes (inter-VLAN routing)               | Yes (L3 gateway)         | Yes (VPC routing tables)     |
| Broadcast domain                | Per VLAN                               | Per VNI                  | Per VPC subnet               |
| Use case                        | Corporate LAN, datacenter segmentation | Cloud overlay networking | Multi-tenant cloud           |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| VLANs provide security by themselves        | VLANs provide L2 isolation (broadcast domain separation) but are vulnerable to VLAN hopping if trunks misconfigured. Real security = VLANs + L3 ACLs + proper trunk port configuration (no DTP, dedicated native VLAN) |
| VLAN 1 is the management VLAN best practice | VLAN 1 is the default VLAN on most switches and carries CDP/STP/DTP by default. Best practice: use a dedicated management VLAN (e.g., VLAN 99), not VLAN 1 (which is too widely trusted)                               |
| Each subnet must be a separate VLAN         | Usually true (one subnet per VLAN), but secondary IP addresses on SVIs can allow multiple subnets per VLAN. However, different VLANs for different subnets is cleaner and the standard practice                        |

---

### 🚨 Failure Modes & Diagnosis

**Native VLAN Mismatch — Trunk Link Drops Traffic**

```bash
# Symptom: devices on VLAN 10 lose connectivity when trunk is configured
# Root cause: native VLAN mismatch between two switches on trunk link

# Cisco CLI to check native VLAN:
# Switch 1: show interfaces trunk | include Native
# Switch 2: show interfaces trunk | include Native
# If Native VLAN differs: 802.1Q de-tagging happens at wrong VLAN

# Linux: check 802.1Q configuration
bridge vlan show
# PORT  VLAN-ID  FLAGS
# eth0     1     PVID Egress Untagged  ← default native VLAN=1

# Fix: ensure both switches use same native VLAN on trunk
# Cisco:
# interface GigabitEthernet0/1
#   switchport trunk native vlan 99  ← match on both sides!
#   switchport mode trunk

# Detect untagged frames on wrong VLAN:
tcpdump -i eth0 'not vlan'  # capture untagged frames on trunk
# Should be empty (or only native VLAN traffic)

# VLAN allowed list mismatch (trunk not carrying all VLANs):
# Check: show interfaces trunk | include VLANs allowed and active
# If VLAN 30 not in allowed list on one end → VLAN 30 traffic dropped
```

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`, `OSI Model`, `Network Topologies`

**Related:** `Overlay Networks`, `Subnet & CIDR`, `Firewall`, `VPN`, `Network Policies`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ VLAN         │ Logical switch partition; broadcast domain │
│ 802.1Q TAG   │ 4 bytes: TPID(0x8100) + TCI(12-bit VID)  │
├──────────────┼───────────────────────────────────────────┤
│ ACCESS PORT  │ One VLAN; untagged to device              │
│ TRUNK PORT   │ Multiple VLANs; tagged; switch-to-switch  │
├──────────────┼───────────────────────────────────────────┤
│ INTER-VLAN   │ Needs L3 routing (router or L3 switch SVI)│
│ MAX VLANS    │ 4094 (802.1Q); vs VXLAN 16M (24-bit VNI) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Virtual partition of a switch into       │
│              │ isolated broadcast domains"               │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design the VLAN architecture for a financial institution's datacenter serving 3 security zones: (a) Public Zone (web servers, load balancers), (b) Application Zone (internal app servers), (c) Restricted Zone (core banking databases, HSMs — Hardware Security Modules). (a) Assign VLAN IDs and subnets for each zone. (b) Design the inter-VLAN routing: explain why a stateful firewall (NOT just an ACL on a L3 switch) is required between zones (stateful inspection tracks TCP connections, stateful packet inspection for application-layer attacks). (c) Describe the PCI-DSS implications: PCI-DSS requires network segmentation between the CDE (Cardholder Data Environment) and other systems — how does your VLAN design satisfy this? (d) Explain how a penetration tester would attempt VLAN hopping (double-tagging attack, DTP negotiation) against your design, and what technical controls prevent each vector. (e) Describe how this physical VLAN design maps to an equivalent cloud architecture in AWS: Public Zone = public subnets, Application Zone = private subnets, Restricted Zone = isolated subnets with no route table path to internet.
