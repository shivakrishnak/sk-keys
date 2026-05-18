---
id: NET-059
title: "MTU Fragmentation and PMTUD"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-020, NET-025
used_by: NET-060, NET-061
related: NET-020, NET-025, NET-050
tags:
  - networking
  - mtu
  - fragmentation
  - pmtud
  - performance
  - vpn
  - tunneling
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/net/mtu-fragmentation-and-pmtud/
---

**⚡ TL;DR** - MTU (Maximum Transmission Unit) is the
largest packet a network link can carry. Ethernet: 1500
bytes. Jumbo frames: 9000 bytes. When a packet is larger
than the MTU, it is either fragmented (split and
reassembled) or dropped (if DF bit is set). Path MTU
Discovery (PMTUD) finds the minimum MTU on a path by
sending DF packets and using ICMP "fragmentation needed"
responses. MTU mismatches cause mysterious failures: VPN
connections drop on large transfers, SSH works but SCP
fails, web pages load partially. Diagnosis: ping with
specific sizes and DF bit set.

| #059 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | TCP Deep Dive (NET-020), Subnets and CIDR Notation (NET-025) | |
| **Used by:** | Anycast Routing (NET-060), DDoS Attack Types (NET-061) | |
| **Related:** | TCP Deep Dive, Subnets and CIDR Notation, Network Performance Testing | |

---

### 🔥 The Problem This Solves

A VPN tunnel is set up. `ping vpn-host` works. SSH works.
But `scp large-file vpn-host:/tmp/` hangs forever after
the TCP handshake. The reason: the VPN adds an IPsec
header (50+ bytes) to each packet. A 1500-byte packet
becomes 1550+ bytes. The VPN endpoint drops packets
over 1500 bytes with a silent DROP (ICMP blocked by
firewall). TCP never learns the MTU limit. Large data
packets are dropped, SCP stalls at zero progress. Fix:
set VPN MTU to 1400 bytes to account for encapsulation.

---

### 🧠 Intuition: The Truck and Tunnel Problem

```
Imagine packets are trucks, network links are roads.
Each road has a maximum truck width (MTU).

Large truck (1500-byte packet) on wide highway: fine.
Same truck tries to enter a tunnel (VPN, GRE, IPsec):
  Tunnel adds overhead → truck is now "wider" than 1500.

Solutions:
  1. Fragment: cut the truck in half, reassemble at end
     Cost: processing, ordering, reassembly overhead
     Problem: one fragment lost = entire truck re-sent

  2. DF bit (Don't Fragment): send back "too big" signal
     Router: "ICMP Fragmentation Needed, MTU=1400"
     Sender: "OK, I'll use 1400-byte packets next time"
     This is PMTUD (Path MTU Discovery)

  3. Clamp MSS (TCP MSS Clamping):
     At tunnel entry, modify TCP SYN to advertise
     smaller MSS → TCP never sends packets over limit
     Router does this automatically: ip tcp adjust-mss
```

---

### ⚙️ MTU Values in Different Environments

```
Link type              MTU     Overhead    Effective payload
Ethernet (standard)    1500    -           1500 bytes
Ethernet (jumbo)       9000    -           9000 bytes
Wi-Fi (802.11)         2346    -           2346 bytes (rarely used)
PPPoE (DSL)            1492    8 bytes     1492 bytes (-8 from PPP)
IPsec tunnel           1500    ~73 bytes   ~1427 bytes
WireGuard VPN          1500    ~60 bytes   ~1420 bytes
OpenVPN (UDP)          1500    ~57 bytes   ~1443 bytes
GRE tunnel             1500    ~24 bytes   ~1476 bytes
VXLAN overlay          1500    ~50 bytes   ~1450 bytes
Kubernetes pod (VXLAN) 1500    ~50 bytes   ~1450 bytes (if not jumbo)

Key insight: every encapsulation adds header bytes.
  Stack: IPv4 + TCP + TLS + HTTP/2 + gRPC + VPN + VXLAN
  Each layer adds bytes. If total > MTU → fragmentation.

Recommended settings:
  Physical hosts with jumbo: set MTU 9000 everywhere
  VPN interface: MTU = physical MTU - encapsulation overhead
  WireGuard: MTU = 1420 (correct for 1500-byte outer)
  Kubernetes CNI (VXLAN): MTU = 1450 or use jumbo frames
```

---

### ⚙️ Diagnosing MTU Problems

```bash
# SYMPTOM: large transfers fail, small ones work
# SYMPTOM: SCP hangs, HTTP loads partially, TCP stalls

# Step 1: Ping with explicit packet sizes and DF bit
# Find the maximum working packet size:
ping -M do -s 1472 gateway_ip    # 1472 + 28 headers = 1500
ping -M do -s 1473 gateway_ip    # 1473 + 28 headers = 1501 > MTU
# -M do: set DF (Don't Fragment) bit
# -s: payload size (headers add 28 bytes: 20 IP + 8 ICMP)
# Working: "64 bytes from ... icmp_seq=1 ttl=64 time=1ms"
# Too big: "Frag needed and DF set (mtu = 1500)"
# Or silent drop: timeout (no response = ICMP blocked)

# Bisect to find exact MTU:
for size in 1400 1450 1472 1480 1490 1500; do
    result=$(ping -M do -s $size -c 1 -W 1 gateway_ip 2>&1)
    echo "$size: $(echo $result | grep -o 'mtu.*\|bytes from\|timeout')"
done

# Step 2: tracepath - shows MTU at each hop
tracepath google.com
# Output:
#  1?: [LOCALHOST]   pmtu 1500
#  1:  router        0.5ms pmtu 1500
#  2:  isp-router    5ms   pmtu 1492
#  3:  ...
# pmtu line = reported MTU at that hop

# Step 3: Check interface MTU
ip link show eth0 | grep mtu
# Expected: mtu 1500 (standard Ethernet)

ip link show wg0 | grep mtu
# WireGuard should be: mtu 1420

# Step 4: TCP MSS in packet capture
sudo tcpdump -i eth0 -n "tcp[tcpflags] & tcp-syn != 0"
# Read MSS option from SYN packet:
# options [mss 1460]: standard Ethernet (1500 - 40 headers)
# options [mss 1380]: VPN/tunnel (1420 - 40 headers)
# Mismatch between peers → fragmentation or drop
```

---

### ⚙️ Wrong vs Right: Ignoring MTU in VPN Setup

```bash
# BAD: WireGuard configured with default interface MTU
[Interface]
Address = 10.0.0.1/24
PrivateKey = ...
# No MTU setting - interface inherits 1500 (or OS default)

# What happens:
# - Outer UDP packet: WireGuard header (~60 bytes) + 1500 inner
# - Total: 1560 bytes sent to ISP
# - ISP MTU: 1500 → drops the packet (DF bit set) OR fragments
# - Fragmentation: causes reassembly issues, drops, high CPU
# - Result: VPN "works" for small data, fails for large transfers
#           Web browsing fails after TCP SYN (large HTML response)
#           SSH works (keystrokes are small)

# GOOD: set correct MTU to account for encapsulation
[Interface]
Address = 10.0.0.1/24
PrivateKey = ...
MTU = 1420  # 1500 - 80 bytes (WireGuard + UDP + IP headers)

[Peer]
# ...
# Inner packets: max 1420 bytes
# Outer UDP: 1420 + ~60 headers = ~1480 < 1500: fits!

# Verify:
ip link show wg0
# wg0: mtu 1420 ...

# Test:
ping -M do -s 1392 10.0.0.2  # 1392 + 28 = 1420 = MTU
# Should work; 1393 should fail with ICMP too big
```

---

### ⚙️ PMTUD and ICMP Black Holes

```bash
# PMTUD requires ICMP "Fragmentation Needed" (type 3 code 4)
# to reach the sender. Firewalls that block ICMP = PMTUD black hole

# Symptom: TCP connection works for small data, hangs for large
# Cause: router drops oversized packets (DF set) but blocks ICMP
# TCP sender never learns to reduce packet size
# Large sends: every packet dropped, infinite retransmit

# Diagnose ICMP black hole:
ping -M do -s 1472 remote_ip   # timeout = ICMP blocked
ping -M dont -s 1472 remote_ip # works = packets ARE flowing

# Fix 1: enable ICMP on firewall (correct fix)
sudo iptables -A INPUT -p icmp --icmp-type fragmentation-needed \
  -j ACCEPT
sudo iptables -A OUTPUT -p icmp --icmp-type fragmentation-needed \
  -j ACCEPT
# Critical: allow ICMP type 3 (destination unreachable)
#           especially code 4 (fragmentation needed)

# Fix 2: TCP MSS clamping at router/tunnel entry
# Modifies TCP SYN MSS option to match tunnel MTU
sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
  -j TCPMSS --clamp-mss-to-pmtu
# OR: explicit MSS:
sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
  -j TCPMSS --set-mss 1380
# This makes TCP negotiate a smaller segment size upfront

# Fix 3: for Kubernetes with VXLAN
# Cilium and Calico automatically clamp MSS
# Or: set jumbo frames (MTU 9000) on underlying network
#     so VXLAN overhead doesn't matter
```

---

### 📐 Scale Considerations

```
Large-scale environments where MTU matters most:

Data centers with jumbo frames (MTU 9000):
  VXLAN adds 50 bytes → effective 8950 bytes: still large
  iSCSI, NFS, storage traffic benefits greatly
  Requirement: ALL switches in path support jumbo frames
  One hop without jumbo → fragmentation → terrible performance

Kubernetes/container networks:
  Calico VXLAN: MTU 1450 (or jumbo if infra supports)
  Flannel VXLAN: MTU 1450
  Cilium with BPF masquerade: MTU 1450
  AWS VPC CNI: native routing, full MTU available
  → AWS VPC: no VXLAN overhead (pods get real VPC IPs)

Cloud provider specifics:
  AWS: EC2 MTU 9001 within VPC (jumbo frames supported)
  AWS: Internet-bound: MTU 1500 (standard Ethernet)
  GCP: MTU 1460 (VPC default, slightly smaller for headers)
  Azure: MTU 1500

Performance impact of fragmentation:
  CPU: fragmentation/reassembly = ~30% CPU overhead
  Loss: one fragment lost = entire packet retransmit
  Latency: reassembly delay + retransmit timeout
  At 10G: fragmentation can halve effective throughput
  Solution: configure correctly to eliminate fragmentation
```

---

### 🧭 Decision Guide

```
When MTU problems are likely:
  New VPN or tunnel configured
  Kubernetes deployment on VXLAN network
  Intermittent failures on large file transfers
  SSH works, SCP doesn't
  Web pages load headers but not body

Diagnosis sequence:
  1. Test with ping -M do -s sizes to find MTU
  2. Check interface MTU with ip link show
  3. Check tcpdump SYN packets for MSS value
  4. Check if ICMP is being blocked (PMTUD black hole)

MTU configuration guide:
  Plain Ethernet: 1500 (standard), 9000 (jumbo)
  Over WireGuard: 1420 (= 1500 - 80)
  Over OpenVPN/UDP: 1443 (= 1500 - 57)
  Over IPsec ESP: 1427 (= 1500 - 73)
  Over GRE: 1476 (= 1500 - 24)
  Over VXLAN: 1450 (= 1500 - 50)

When to use jumbo frames (MTU 9000):
  Internal data center traffic (storage, big data)
  HPC clusters (InfiniBand alternative)
  NOT for internet-facing links (ISP caps at 1500)

Quick fix for MTU mismatch:
  iptables MSS clamping: affects TCP (HTTP, SSH, etc.)
  MTU setting on interface: affects all protocols (UDP too)
  For VPN: always set MTU at VPN interface, not iptables
```