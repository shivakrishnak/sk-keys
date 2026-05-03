---
layout: default
title: "DHCP"
parent: "Networking"
nav_order: 192
permalink: /networking/dhcp/
number: "0192"
category: Networking
difficulty: ★☆☆
depends_on: IP Addressing, UDP, DNS
used_by: Networking, Linux, Cloud — AWS, Kubernetes
related: IP Addressing, DNS, ARP, NAT, Subnet & CIDR
tags:
  - networking
  - dhcp
  - ip-assignment
  - automatic-configuration
---

# 192 — DHCP

⚡ TL;DR — DHCP (Dynamic Host Configuration Protocol) automatically assigns IP addresses, subnet masks, default gateways, and DNS servers to devices on a network — eliminating manual IP configuration. Works via 4-message UDP broadcast: DISCOVER → OFFER → REQUEST → ACK (DORA). Used in home networks, enterprise LANs, cloud VPCs (AWS assigns IPs via DHCP to EC2 instances), and Kubernetes (pods get IPs from CNI plugin acting as DHCP-like allocator).

---

### 🔥 The Problem This Solves

Without DHCP, every device joining a network needs a manually configured IP address, subnet mask, gateway, and DNS server. In a home with 20 devices, an office with 500 laptops, or a Kubernetes cluster with 10,000 pods — manual IP assignment is operationally impossible. DHCP automates this: devices announce themselves, a DHCP server assigns configuration, and the device is ready in seconds.

---

### 📘 Textbook Definition

**DHCP (Dynamic Host Configuration Protocol):** A network management protocol (RFC 2131) that automatically assigns IP configuration to network clients. Uses UDP: client port 68, server port 67. Key configuration provided: IP address (from a pool), subnet mask, default gateway (router IP), DNS server IPs, DHCP lease time. Also optional: NTP server, domain suffix, static routes, TFTP server (for PXE boot).

**DHCP Lease:** The time period for which an IP address is assigned. Client must renew before expiry (at 50% of lease time by default). After expiry without renewal, IP is returned to the pool and may be reassigned.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DHCP automatically assigns IP addresses and network configuration to devices — the four-step DORA dance (Discover, Offer, Request, ACK) happens in milliseconds when your laptop joins a network.

**One analogy:**

> DHCP is like a hotel reception desk. When you arrive (join the network), you announce your presence. The receptionist (DHCP server) assigns you a room number (IP address) and gives you the breakfast time (gateway, DNS). Your room is reserved for a limited time (lease). If you stay longer, you renew. When you check out (disconnect), the room becomes available for the next guest.

---

### 🔩 First Principles Explanation

**DORA FOUR-STEP PROCESS:**

```
┌─────────────────────────────────────────────────────────┐
│  DHCP DORA Exchange                                     │
└─────────────────────────────────────────────────────────┘

Client (no IP)                         DHCP Server (192.168.1.1)

1. DISCOVER (broadcast):
   src: 0.0.0.0:68 dst: 255.255.255.255:67
   "I'm a new device (MAC: aa:bb:cc:dd:ee:ff), anyone have an IP for me?"
   All devices on subnet receive this broadcast

2. OFFER (unicast/broadcast):
   src: 192.168.1.1:67 dst: 255.255.255.255:68
   "I offer you 192.168.1.50, with mask 255.255.255.0,
    gateway 192.168.1.1, DNS 8.8.8.8, lease 24 hours"

3. REQUEST (broadcast):
   src: 0.0.0.0:68 dst: 255.255.255.255:67
   "I accept the offer of 192.168.1.50 from server 192.168.1.1"
   (broadcast so other DHCP servers know this offer was accepted)

4. ACK (unicast/broadcast):
   src: 192.168.1.1:67 dst: 255.255.255.255:68
   "Confirmed: 192.168.1.50 is yours until [timestamp]"

Client now has:
  IP: 192.168.1.50/24
  Gateway: 192.168.1.1
  DNS: 8.8.8.8
  Lease: 86400 seconds (24 hours)
```

**DHCP LEASE RENEWAL:**

```
T=0:       IP assigned, lease = 86400s
T=43200s:  (50% of lease) → DHCP Request to server (unicast)
           Server: DHCP ACK → lease renewed for another 86400s
T=64800s:  (87.5% of lease, if renewal failed) → broadcast Request
T=86400s:  Lease expired → client must release IP and DORA again
```

**STATIC DHCP ASSIGNMENT (RESERVATION):**

```
DHCP server config (dnsmasq):
  # Always assign same IP to specific MAC address
  dhcp-host=aa:bb:cc:dd:ee:ff,192.168.1.100,printer

  # IP pool for dynamic assignment
  dhcp-range=192.168.1.50,192.168.1.200,24h

  # Gateway and DNS for all clients
  dhcp-option=3,192.168.1.1   # option 3 = default gateway
  dhcp-option=6,8.8.8.8,8.8.4.4  # option 6 = DNS servers
```

**DHCP RELAY (cross-subnet):**

```
Problem: DHCP uses broadcasts (255.255.255.255)
         Broadcasts don't cross router boundaries
         Multiple subnets → each needs a DHCP server?

Solution: DHCP Relay Agent
  Router at subnet boundary intercepts DHCP DISCOVER broadcasts
  Unicasts them to central DHCP server (with relay agent info)
  DHCP server responds to relay agent, which forwards to client

AWS: DHCP Relay not needed — AWS DHCP service is VPC-scoped
     All EC2 instances in VPC use AWS-managed DHCP
```

---

### 🧪 Thought Experiment

**AWS EC2 DHCP:**
When you launch an EC2 instance, AWS provides network configuration via DHCP. The instance runs a DHCP client (usually cloud-init or dhclient); AWS DHCP server (per-VPC, hidden infrastructure) responds with: private IP from the subnet's CIDR, default gateway (the VPC router at subnet .1), DNS resolver (169.254.169.253 — AWS provided DNS). The lease is essentially infinite while the instance runs. The IP is pre-allocated by AWS before the instance starts — the DHCP exchange is just the mechanism for the OS to receive the already-determined IP.

---

### 🧠 Mental Model / Analogy

> DHCP is like a conference name badge system. When you arrive (connect to network), you go to registration (DHCP server): "I'm new here." They hand you a badge (IP address) with your name, table assignment (gateway), and session schedule (DNS). The badge expires tomorrow (lease time) — come back to renew if you're staying. If you leave without returning your badge, it goes back into the pool after expiry and gets issued to the next attendee.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** DHCP automatically gives your device an IP address when you join a network. Without it, you'd have to manually type in IP address, subnet mask, gateway, and DNS for every device.

**Level 2:** DHCP options: `dhclient -v eth0` shows the DORA exchange on Linux. `/var/lib/dhcp/dhclient.leases` stores current lease. `dhclient -r` releases; `dhclient` re-requests. Useful for debugging: `tcpdump -i eth0 port 67 or port 68` to capture DHCP traffic.

**Level 3:** DHCP exhaustion attack: an attacker sends many DISCOVER messages with spoofed MAC addresses, exhausting the DHCP pool. Legitimate clients get no IP. Protection: DHCP snooping (switch feature — only trust DHCP responses from known server ports; rate-limit DISCOVER messages per port). DHCP lease time selection: too short (high DHCP traffic), too long (depletes pool for dynamic environments). For Kubernetes: pods get IPs from CNI (Calico, Flannel, Cilium) which implements its own IP allocation (similar to DHCP but at pod level).

**Level 4:** DHCP security concerns: (1) DHCP spoofing — rogue server answers DISCOVER first with malicious gateway/DNS → man-in-the-middle. Mitigation: DHCP snooping + Dynamic ARP Inspection. (2) DHCP starvation — flood server with fake clients to exhaust pool. (3) No authentication in DHCPv4 — any server on the network can answer (DHCPv6 has authentication options via DUID). Zero trust response: treat the IP assignment process as untrusted; authenticate at the application layer (mTLS, JWT) regardless of what IP you received.

---

### ⚙️ How It Works (Mechanism)

```bash
# Linux: request IP via DHCP
dhclient -v eth0

# View current DHCP lease
cat /var/lib/dhcp/dhclient.leases
# lease {
#   interface "eth0";
#   fixed-address 192.168.1.50;
#   option subnet-mask 255.255.255.0;
#   option routers 192.168.1.1;
#   option domain-name-servers 8.8.8.8, 8.8.4.4;
#   expire 1 2025/01/01 12:00:00;
# }

# Release and renew
dhclient -r eth0   # release
dhclient eth0      # acquire new lease

# Capture DHCP traffic
tcpdump -i eth0 -n port 67 or port 68

# Check current IP and gateway
ip addr show eth0
ip route show

# Server: dnsmasq DHCP config
# /etc/dnsmasq.conf
cat /etc/dnsmasq.conf | grep -E "dhcp|interface"

# View dnsmasq DHCP leases
cat /var/lib/misc/dnsmasq.leases
# 1704067200 aa:bb:cc:dd:ee:ff 192.168.1.50 my-laptop *
# (expire_time MAC IP hostname)

# AWS: check instance DHCP config
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Device powers on, no IP:
  1. DISCOVER: broadcast to 255.255.255.255:67
     All servers receive (multiple DHCP servers possible)

  2. OFFER: each server offers an IP
     Client picks first (or preferred) offer

  3. REQUEST: broadcast to signal chosen server
     Other servers see this and reclaim their offered IPs

  4. ACK: server confirms, client configures IP stack

  5. ARP probe: client ARPs its own IP to check for conflicts
     (RFC 5227 Conflict Detection)
     If collision: DHCP DECLINE → start over

  6. IP configured: routing, DNS, gateway operational
```

---

### 💻 Code Example

```python
# Simple DHCP lease parser
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class DhcpLease:
    interface: str
    ip: str
    subnet_mask: str
    gateway: str
    dns_servers: list[str]
    expires: str

def parse_dhclient_leases(leases_file: str) -> list[DhcpLease]:
    """Parse /var/lib/dhcp/dhclient.leases file."""
    content = Path(leases_file).read_text()
    leases = []

    for lease_block in re.findall(r'lease \{([^}]+)\}', content, re.DOTALL):
        def extract(pattern: str) -> str:
            m = re.search(pattern, lease_block)
            return m.group(1).rstrip(';') if m else ""

        ip = extract(r'fixed-address ([^;]+)')
        mask = extract(r'subnet-mask ([^;]+)')
        gw = extract(r'routers ([^;]+)')
        dns = extract(r'domain-name-servers ([^;]+)')
        iface = extract(r'interface "([^"]+)"')
        exp = extract(r'expire \d+ ([^;]+)')

        if ip:
            leases.append(DhcpLease(
                interface=iface, ip=ip, subnet_mask=mask,
                gateway=gw.split(',')[0].strip() if gw else "",
                dns_servers=[s.strip() for s in dns.split(',') if s.strip()],
                expires=exp
            ))

    return leases

# Usage (Linux with active DHCP lease)
try:
    leases = parse_dhclient_leases("/var/lib/dhcp/dhclient.leases")
    for lease in leases:
        print(f"Interface: {lease.interface}")
        print(f"  IP: {lease.ip} ({lease.subnet_mask})")
        print(f"  Gateway: {lease.gateway}")
        print(f"  DNS: {', '.join(lease.dns_servers)}")
        print(f"  Expires: {lease.expires}")
except FileNotFoundError:
    print("No DHCP leases found (not Linux or different path)")
```

---

### ⚖️ Comparison Table

| Aspect               | DHCP Dynamic           | DHCP Reservation       | Static IP         |
| -------------------- | ---------------------- | ---------------------- | ----------------- |
| IP changes over time | Yes (on lease renewal) | No (same IP always)    | No                |
| Configuration effort | Zero (auto)            | Per-device MAC entry   | Manual per device |
| Use case             | Laptops, phones        | Printers, servers      | Bare-metal, VMs   |
| DNS reliability      | Requires dynamic DNS   | Reliable (predictable) | Reliable          |

---

### ⚠️ Common Misconceptions

| Misconception                    | Reality                                                                                                                                                         |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DHCP assigns permanent IPs       | IPs are leased for a time period. The same MAC usually gets the same IP (server caches the assignment), but it's not guaranteed without a reservation           |
| DHCP is only for home networks   | AWS, Azure, GCP all use DHCP to assign IPs to VMs. Kubernetes uses DHCP-like protocols for pod IP assignment. Enterprise networks use DHCP for 1000s of devices |
| Short lease time = more security | Shorter lease = more DHCP traffic + faster IP exhaustion during attacks. Security comes from DHCP snooping, not lease duration                                  |

---

### 🚨 Failure Modes & Diagnosis

**DHCP Pool Exhaustion: New Devices Can't Join Network**

```bash
# Symptom: new devices get 169.254.x.x (APIPA = no DHCP response)
# 169.254.x.x = "link-local" address assigned by OS when DHCP fails

# Check DHCP server pool utilisation (dnsmasq)
cat /var/lib/misc/dnsmasq.leases | wc -l
# Compare to total pool size in config

# Check for stale leases
cat /var/lib/misc/dnsmasq.leases
# Look for expired leases still holding IPs

# Extend pool range (if subnet allows)
# /etc/dnsmasq.conf: increase dhcp-range

# Check for duplicate DHCP servers (causing conflicts)
# Capture and check: is OFFER coming from unexpected source?
tcpdump -i eth0 -n port 67 | grep BOOTREPLY

# Reduce lease time to reclaim IPs faster
# dhcp-range=192.168.1.50,192.168.1.200,1h  (1 hour instead of 24h)

# For AWS: VPC CIDR too small → no IPs left for new EC2 instances
# Check: AWS Console → Subnet → Available IPv4 Addresses
aws ec2 describe-subnets --subnet-ids subnet-xxx \
  --query 'Subnets[*].[SubnetId,AvailableIpAddressCount,CidrBlock]'
# If AvailableIpAddressCount = 0 → expand subnet or add secondary CIDR
```

---

### 🔗 Related Keywords

**Prerequisites:** `IP Addressing`, `UDP`, `DNS`

**Related:** `ARP` (address resolution on same subnet), `NAT` (shares one public IP across DHCP-assigned private IPs), `Subnet & CIDR` (defines the pool DHCP assigns from)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DORA         │ Discover → Offer → Request → ACK          │
│              │ UDP broadcast, ports 67 (server) / 68 (cl)│
├──────────────┼───────────────────────────────────────────┤
│ ASSIGNS      │ IP, subnet mask, gateway, DNS, lease time  │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ dhclient -v eth0; tcpdump port 67 or 68   │
│              │ cat /var/lib/dhcp/dhclient.leases          │
├──────────────┼───────────────────────────────────────────┤
│ EXHAUSTION   │ 169.254.x.x (APIPA) = no DHCP reply       │
│              │ Fix: expand pool or reduce lease time      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hotel receptionist: assigns you a room    │
│              │ (IP) automatically when you check in"     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kubernetes uses a CNI (Container Network Interface) plugin (Calico, Flannel, Cilium) to assign IPs to pods. (a) Explain how this compares to traditional DHCP: the CNI plugin acts as an IP address management (IPAM) system, allocating IPs from a per-node subnet without broadcasting. (b) Why broadcasting doesn't work in Kubernetes (pods in different namespaces, different nodes — no shared Layer 2 broadcast domain). (c) How Calico uses BGP to distribute pod IP routes across nodes (each node announces its pod CIDR via BGP; other nodes route pod-destined packets directly to the correct node). (d) Explain the AWS VPC CNI plugin for EKS: pods get actual VPC IPs (not an overlay), assigned via AWS ENIs (Elastic Network Interfaces) — each EC2 instance can have multiple ENIs with multiple IPs, and the CNI pre-allocates them. (e) The scaling constraint of AWS VPC CNI: max pods per node = (ENIs × IPs per ENI - 1) — a limiting factor for pod density on small instance types (e.g., t3.small: 3 ENIs × 4 IPs - 1 = 11 pods max).
