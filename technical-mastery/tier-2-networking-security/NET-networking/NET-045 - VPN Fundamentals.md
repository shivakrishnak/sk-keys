---
id: NET-045
title: "VPN Fundamentals"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-044
used_by: NET-064, NET-068
related: NET-044, NET-025, NET-068
tags:
  - networking
  - vpn
  - tunnel
  - ipsec
  - wireguard
  - split-tunnel
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/net/vpn-fundamentals/
---

**⚡ TL;DR** - A VPN creates an encrypted tunnel between
two endpoints, allowing private network traffic to flow
securely over the public internet. Site-to-site VPNs
connect data centers or offices. Remote-access VPNs
connect individual users to a network. The two dominant
modern protocols: WireGuard (fast, simple, uses UDP) and
IPsec (complex, enterprise-standard). Split-tunnel routes
only private traffic through the VPN; full-tunnel routes
everything - the choice matters for performance and
privacy.

| #045 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | TLS Handshake Deep Dive (NET-044) | |
| **Used by:** | Network Security Layers, Zero Trust Network Architecture | |
| **Related:** | TLS Handshake Deep Dive, NAT, Zero Trust Network Architecture | |

---

### 🔥 The Problem VPN Solves

A developer works from a coffee shop. The company's
internal database at `db.internal.company.com` is not
accessible from the public internet - it has no public IP.
Without VPN: impossible to connect. With VPN: the
developer's machine creates an encrypted tunnel to the
company's VPN gateway. The OS routes traffic for
`10.0.0.0/8` through the tunnel. `db.internal.company.com`
resolves to `10.0.5.100`, traffic flows through the tunnel,
arrives at the database server as if the developer is on
the office network.

---

### 🧠 Intuition: A Tunnel Inside the Network

```
Normal traffic:
  Laptop → Coffee shop WiFi → Internet → (blocked) → DB

VPN traffic:
  Laptop → Coffee shop WiFi → Internet → VPN Gateway
              (encrypted tunnel)           → Internal network
                                                     → DB

The tunnel:
  1. Original packet: [src: 192.168.1.10] → [dst: 10.0.5.100]
  2. VPN encapsulates: [src: 1.2.3.4] → [dst: VPN-GW-IP]
     Payload: encrypted original packet
  3. VPN gateway decapsulates, forwards to internal network
  4. Response travels reverse path

To the DB server: the connection appears to come from
the VPN gateway's internal IP, not the laptop.
```

---

### ⚙️ VPN Types

**Site-to-Site VPN:**

```
Purpose: Connect two private networks over internet
Use case: HQ ↔ Branch office, AWS VPC ↔ On-premise data center

Architecture:
  HQ: 10.0.0.0/16  ←→  Branch: 192.168.0.0/16
  VPN GW (HQ)  ←── encrypted tunnel ──→  VPN GW (Branch)
  
  All traffic between 10.0.0.0/16 and 192.168.0.0/16
  automatically routes through the tunnel

AWS VPN Connection:
  Virtual Private Gateway (on AWS side)
  Customer Gateway (on premise side)
  Two tunnels (active/standby for HA)
  IPsec protocol with IKEv2
```

**Remote Access VPN:**

```
Purpose: Individual user → private network
Use case: Remote work, contractor access, mobile workforce

Architecture:
  User laptop → VPN client → VPN concentrator → Internal network
  
  Each user gets a virtual IP from VPN pool (e.g., 172.16.0.0/16)
  Traffic destined for internal IPs routes through tunnel
  
Split-tunnel mode:
  10.0.0.0/8 → VPN tunnel (internal traffic)
  0.0.0.0/0  → direct internet (everything else)
  → Lower VPN load, better performance
  → Security: internet traffic NOT monitored by company

Full-tunnel mode:
  0.0.0.0/0 → VPN tunnel (ALL traffic)
  → Higher VPN load (company internet traffic routed through GW)
  → Security: company can inspect/filter all traffic
  → Compliance: required in some regulated industries
```

---

### ⚙️ VPN Protocols Comparison

```
┌──────────────────────────────────────────────────────────┐
│  Protocol    │ Transport│ Overhead │ Setup  │ Best for   │
├──────────────┼──────────┼──────────┼────────┼────────────┤
│ WireGuard    │ UDP      │ ~32 bytes│ Simple │ Modern VPN │
│ OpenVPN      │ UDP/TCP  │ ~38 bytes│ Medium │ Flexibility│
│ IPsec/IKEv2  │ UDP      │ Variable │ Complex│ Enterprise │
│ IPsec/L2TP   │ UDP      │ Higher   │ Complex│ Legacy     │
│ PPTP         │ TCP      │ Low      │ Simple │ NEVER*     │
└──────────────┴──────────┴──────────┴────────┴────────────┘
* PPTP is cryptographically broken. Do not use.
```

---

### ⚙️ WireGuard: The Modern Standard

```
WireGuard design principles:
  - Minimal codebase: ~4,000 lines of code
    (vs OpenVPN: 100,000+ lines, IPsec stack: similar)
  - Single cipher suite: ChaCha20-Poly1305, Curve25519 ECDH
    (no cipher negotiation = no downgrade attacks)
  - Built into Linux kernel since 5.6 (2020)
  - UDP only: works on any port (commonly 51820)
  - Stateless-ish: no connection state table
    (but does track handshake timing)

WireGuard configuration (server side):
  [Interface]
  PrivateKey = [server private key]
  Address = 10.0.0.1/24  ← VPN subnet
  ListenPort = 51820

  [Peer]  ← one section per client
  PublicKey = [client public key]
  AllowedIPs = 10.0.0.2/32  ← this client's VPN IP
  # Multiple AllowedIPs = routes from client to internal

WireGuard configuration (client side):
  [Interface]
  PrivateKey = [client private key]
  Address = 10.0.0.2/24
  DNS = 10.0.0.1  ← use VPN DNS for split-DNS

  [Peer]
  PublicKey = [server public key]
  Endpoint = vpn.company.com:51820
  AllowedIPs = 10.0.0.0/8  ← route internal traffic via VPN
  # Use 0.0.0.0/0 for full tunnel
  PersistentKeepalive = 25  ← send keepalive every 25s (for NAT)
```

---

### ⚙️ IPsec: Enterprise Standard

```
IPsec = IP Security: suite of protocols for authenticating
and encrypting IP packets.

Components:
  IKE (Internet Key Exchange): negotiates keys (IKEv2 = current)
  ESP (Encapsulating Security Payload): encrypts + authenticates
  AH (Authentication Header): authenticates only (rarely used)

Two modes:
  Transport mode: encrypts payload only, original IP header intact
    → used for host-to-host (e.g., mTLS alternative)
  Tunnel mode: encrypts entire packet, wraps in new IP header
    → used for site-to-site VPN (standard VPN mode)

IKEv2 handshake phases:
  Phase 1 (IKE_SA_INIT):
    Exchange DH public keys, establish shared secret
    Derive IKE session keys (for phase 2 protection)
    
  Phase 2 (IKE_AUTH):
    Authenticate each side (certificates or pre-shared key)
    Negotiate IPsec SA (Security Association) parameters:
    algorithm, lifetime, selectors (which traffic to encrypt)

Security Association (SA):
  One-directional: need 2 SAs per tunnel (one each way)
  Contains: algorithm, keys, sequence numbers, SPI
  Identified by: (SPI, destination IP, protocol)
```

---

### ⚙️ Wrong vs Right: Full Tunnel for All Employees

```
# BAD: force all traffic through VPN (full tunnel) for all users
# AllowedIPs = 0.0.0.0/0 (all traffic through VPN)
#
# Effects:
# - 1,000 employees all browse internet through VPN gateway
# - VPN gateway must handle 1,000 × ~50 Mbps = 50 Gbps
# - All internet latency += RTT to corporate data center
# - Video calls (Zoom/Teams) route: laptop → London DC → NYC Zoom
#   instead of: laptop → NYC Zoom  (add 150ms RTT)
# - Company sees all personal browsing (privacy concern)
# - VPN becomes single point of failure for work AND personal traffic

# GOOD: split-tunnel with specific internal routes
# AllowedIPs = 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
# → Only RFC 1918 (private) traffic goes through VPN
# → Internet traffic: direct from user's ISP (fast)
# → Video calls: direct to Zoom/Teams infrastructure
# → VPN carries: only internal service traffic

# Even better: DNS-based split tunnel
# Route only DNS queries for *.internal.company.com via VPN
# DNS responds with internal IPs → those routes use VPN
# Everything else: direct internet
```

---

### ⚙️ VPN and NAT: The Keepalive Requirement

```
Problem: user laptop is behind NAT (home router, office NAT)
  VPN uses UDP → UDP NAT entries expire after ~30s of inactivity
  VPN connection appears idle (no data) → NAT drops entry
  Next VPN packet arrives → NAT has no mapping → packet dropped
  VPN appears "disconnected" after idle period

Solution: PersistentKeepalive
  WireGuard: PersistentKeepalive = 25  (seconds)
  → Sends small UDP packet every 25s even if idle
  → Keeps NAT entry alive (30s expiry never triggered)
  → Cost: ~40 bytes/25s = negligible bandwidth

For IPsec:
  IKEv2 DEAD PEER DETECTION (DPD):
  dpd-delay = 30s, dpd-timeout = 150s
  → Both sides probe each other if no traffic
  → Detects dead connections faster than waiting for TCP timeout
```

---

### ⚙️ Diagnosing VPN Issues

```bash
# 1. Is WireGuard interface up?
wg show wg0
# Interface: wg0
# public key: ...
# listening port: 51820
# peer: CLIENT_PUBLIC_KEY
#   endpoint: 1.2.3.4:12345
#   allowed ips: 10.0.0.2/32
#   latest handshake: 1 minute, 30 seconds ago  ← recent = connected
#   transfer: 1.23 MiB received, 4.56 MiB sent

# 2. Can you reach VPN gateway? (reachability test)
ping -c 4 vpn.company.com
# Timeout = routing problem before reaching VPN gateway

# 3. Is traffic routing through VPN? (route check)
ip route get 10.0.5.100
# Should show: via 10.0.0.1 dev wg0

# 4. Can you reach internal hosts?
ping -c 4 10.0.5.100

# 5. DNS resolution via VPN
dig internal-host.company.com @10.0.0.1
# Should resolve to internal IP

# 6. WireGuard handshake not occurring
sudo wg set wg0 peer PEER_PUBKEY endpoint vpn.company.com:51820
sudo wg show  # check "latest handshake" updates

# 7. IPsec IKE negotiation failure
sudo journalctl -u strongswan -f
# Look for: "no proposal chosen" = cipher suite mismatch
#            "INVALID_KEY_INFORMATION" = DH group mismatch
#            "AUTH_FAILED" = pre-shared key mismatch
```

---

### 📐 Scale Considerations

```
WireGuard at scale:
  Single WireGuard peer handles ~1 Gbps (kernel optimized)
  10 Gbps: need multiple WireGuard interfaces or kernel bypass
  Cloud VPN (AWS, GCP): managed service, scales automatically

IPsec at scale:
  Hardware VPN appliances: Cisco ASA, Palo Alto, Fortinet
  Throughput: 10-100 Gbps on dedicated hardware
  Cluster mode for HA: active/standby or active/active

Limitations of traditional VPN at scale:
  All traffic must traverse central gateway
  Gateway becomes bottleneck and single point of failure
  10K+ remote workers → VPN gateway overwhelmed
  
  Solution: Zero Trust Network Access (ZTNA) / BeyondCorp
  Instead of "connect to network, trust everything inside",
  per-resource authentication + authorization
  No single VPN gateway → scales horizontally
  See NET-068 (Zero Trust Network Architecture)
```

---

### 🧭 Decision Guide

```
WireGuard vs IPsec?
  WireGuard: new deployments, cloud, developer VPNs
    (+) Simple config, fast, modern crypto, Linux kernel native
    (+) Tailscale, Cloudflare WARP, AWS Client VPN use WireGuard
    (-) Not enterprise-certified (no FIPS 140-2 for some use cases)

  IPsec: enterprise, regulated industries, hardware appliances
    (+) FIPS-certified implementations available
    (+) Universal compatibility (Cisco, Palo Alto, mobile built-in)
    (+) IKEv2 + MOBIKE = connection migration (mobile handover)
    (-) Complex config, many moving parts, harder to debug

Remote access VPN vs Zero Trust:
  < 500 users, single office: VPN is fine
  > 500 users, or cloud-native, or SaaS: consider ZTNA
  Highly regulated: VPN with MFA + endpoint compliance checks

Full tunnel vs split tunnel:
  Compliance requirement to monitor all traffic → full tunnel
  Otherwise: split tunnel (better performance, less VPN load)

Interview one-liner:
  "VPN creates an encrypted tunnel between endpoints.
  WireGuard (modern) uses ChaCha20+Curve25519 over UDP,
  4,000 lines of kernel code. IPsec uses IKEv2 for key
  exchange and ESP for packet encryption - enterprise standard.
  Split-tunnel routes only private IPs through VPN;
  full-tunnel routes everything (worse latency, higher load)."
```