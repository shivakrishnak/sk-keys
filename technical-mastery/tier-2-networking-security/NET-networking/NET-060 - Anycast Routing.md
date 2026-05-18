---
id: NET-060
title: "Anycast Routing"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-028, NET-057
used_by: NET-061, NET-064
related: NET-028, NET-061, NET-064
tags:
  - networking
  - anycast
  - bgp
  - routing
  - cdn
  - ddos
  - global-load-balancing
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/net/anycast-routing/
---

**⚡ TL;DR** - Anycast routes a single IP address to
multiple physical locations via BGP. Each location
announces the same IP prefix. Internet routers direct
traffic to the nearest location (measured by BGP hop
count/metric). Used by: DNS root servers (all 13 have
anycast), Cloudflare (1.1.1.1), Google (8.8.8.8), CDNs,
DDoS mitigation. The result: users worldwide reach the
nearest PoP (Point of Presence), and volumetric DDoS
attacks are distributed across all PoPs instead of
overwhelming one. No load balancer hardware required.

| #060 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | BGP Basics (NET-028), epoll and io_uring (NET-057) | |
| **Used by:** | DDoS Attack Types (NET-061), Cloudflare BGP Incident (NET-064) | |
| **Related:** | BGP Basics, DDoS Attack Types, Cloudflare BGP Incident | |

---

### 🔥 The Problem This Solves

Without anycast: a user in Tokyo makes a DNS query to
1.1.1.1. The packet travels to Cloudflare's US data
center (150ms RTT). With anycast: the same IP 1.1.1.1
is announced from Cloudflare's Tokyo PoP. Tokyo's BGP
routers see a closer announcement. The query goes to
Tokyo (< 5ms RTT). Cloudflare has 300+ PoPs all
announcing 1.1.1.1. Every user reaches the nearest one.
No application code changes needed - the IP stays the
same, BGP routing does the work.

---

### 🧠 Intuition: One Address, Many Locations

```
Unicast (normal): one IP → one server
  192.168.1.1 → only one machine responds

Broadcast: one message → all machines
  255.255.255.255 → everyone on subnet

Multicast: one IP → subscribed group
  224.0.0.1 → machines that joined the group

Anycast: one IP → nearest machine
  1.1.1.1 → nearest Cloudflare PoP
  (different users get different physical servers,
   but all see the same IP address)

How BGP makes it work:
  BGP is the internet routing protocol
  Each Cloudflare PoP: "I can reach 1.1.1.1/32"
  Internet routers collect these announcements
  For each user's router: "which PoP is closest?"
  Route to closest PoP (fewest BGP hops or shortest AS path)
  Result: automatic geographic routing without DNS tricks
```

---

### ⚙️ How Anycast Works at the BGP Level

```
Anycast setup for 1.1.1.1 (simplified):

Cloudflare's ASN: AS13335
PoP locations: Frankfurt, Singapore, Tokyo, New York, ...

Each PoP's BGP announcement:
  "AS13335 announces 1.1.1.0/24 (which includes 1.1.1.1)"

Internet backbone routers receive ALL announcements:
  Frankfurt router: "I can reach 1.1.1.0/24 via Frankfurt PoP"
  Singapore router: "I can reach 1.1.1.0/24 via Singapore PoP"

User in Amsterdam sends packet to 1.1.1.1:
  Amsterdam ISP router: looks up 1.1.1.1
  BGP table shows: Frankfurt (2 hops), Singapore (8 hops)
  Route to: Frankfurt (nearest)

User in Jakarta sends packet to 1.1.1.1:
  Jakarta ISP router: looks up 1.1.1.1
  BGP table shows: Singapore (2 hops), Frankfurt (9 hops)
  Route to: Singapore (nearest)

Same IP, different physical servers.
No DNS involved. No application changes needed.

BGP attributes affecting routing:
  AS path length (primary: fewer hops = preferred)
  BGP local preference (operator tuning)
  MED (Multi-Exit Discriminator: fine-tuning)
  Community strings (BGP communities: route policies)
```

---

### ⚙️ Anycast for DNS Root Servers

```
The 13 DNS root servers (A-root, B-root, ..., M-root):
  Named: a.root-servers.net through m.root-servers.net
  Total PHYSICAL servers: 1,800+ worldwide
  Total IP addresses: 13 (anycast)

Each letter (A through M) is ONE anycast IP address.
Each IP is announced from 100+ physical locations.

Why 13? Original IPv4 DNS response limit (512 bytes)
  Could fit 13 NS records
  With EDNS0 (RFC 6891): larger responses possible
  13 is now historical, not a hard limit

DNS query flow:
  User's resolver sends to 198.41.0.4 (a.root-servers.net)
  BGP routes to nearest PoP announcing 198.41.0.4
  Physical server: any of 100+ servers worldwide
  Response: same regardless of which PoP answers
  (DNS responses are stateless - any server knows the data)

Result:
  < 5ms DNS resolution from most places in the world
  Resilient: PoP failure → BGP reconverges, next nearest answers
  DDoS resilient: attack against root server is distributed
```

---

### ⚙️ Anycast for DDoS Mitigation

```
Volumetric DDoS: attacker sends 1 Tbps to target IP.
  Without anycast: 1 Tbps hits ONE data center. Saturated.

  With anycast: 1 Tbps is distributed across PoPs
  Cloudflare has 300 PoPs, total capacity: 100+ Tbps
  1 Tbps / 300 PoPs = ~3.3 Gbps per PoP
  Well within capacity of each PoP

Real example - Cloudflare (2024):
  Largest DDoS mitigated: 3.8 Tbps
  PoPs: 300+ globally
  Per-PoP: ~12 Gbps average load
  All clean traffic continued unaffected

XDP + Anycast combination:
  Anycast routes to nearest PoP
  XDP drops volumetric attack at line rate
  Clean traffic passes to application servers
  Application servers never see the attack

BGP withdrawal for failover:
  PoP fails or becomes unreachable
  BGP announcement withdrawn from that PoP
  Routers see it as "no longer reachable"
  Traffic reconverges to next-nearest PoP
  Convergence time: ~30-60 seconds (BGP is slow)
  Fast enough for DDoS; not fast enough for application errors
```

---

### ⚙️ Wrong vs Right: Using GeoDNS Instead of Anycast

```
BAD: GeoDNS for sub-millisecond latency
  GeoDNS: DNS server returns different A records
  based on user's IP location (geoIP lookup)
  
  User in Tokyo → DNS returns Tokyo server IP
  User in US → DNS returns US server IP
  
  Problems:
  1. DNS TTL: minimum practical TTL is 30-60 seconds
     During failover: users get stale IPs for 60+ seconds
  2. DNS resolver location ≠ user location
     Corporate DNS resolver in US → Tokyo user gets US IP
  3. Recursive resolver caching: ignores TTL minimums
  4. CDN vs origin: CDN edge servers need anycast for CDN
  5. Every new user: DNS round-trip adds to latency

GOOD: Anycast for latency-sensitive services
  No DNS lookup needed for routing
  BGP-level routing: fastest possible path
  Failover: BGP withdrawal (~30s convergence)
  DDoS resistant: attack distributed
  Used for: DNS resolver, CDN edge, DDoS scrubbing

GOOD: GeoDNS when you MUST use different IP per region
  Load balancers with different IPs per region
  Regional compliance (data must stay in region)
  Gaming: low-latency region selection with longer TTL
  
BEST: Both together
  Anycast for CDN edge and DNS
  GeoDNS to route to nearest anycast region
  Anycast within region for local distribution
```

---

### ⚙️ Anycast vs Load Balancer Comparison

```
Traditional Load Balancer:
  Single IP, single server (or HA pair)
  Layer 4/7 forwarding to backend pool
  All traffic through one point → single bottleneck
  Requires: hardware, management, health checking
  
Anycast:
  Same IP, many servers worldwide
  BGP routing handles distribution
  No central choke point
  Scales: add new PoP → announce IP → traffic flows
  
Hybrid (common in practice):
  Anycast frontend: routes to nearest PoP
  LB at each PoP: distributes within PoP
  
  [User] → [Anycast IP] → [Nearest PoP LB] → [Backend Pool]

Failure handling comparison:
  LB: health check detects failure, removes from pool
    - Fast: 1-5 seconds
    - Local: only affects one PoP
  Anycast: BGP withdrawal when PoP fails
    - Slower: 30-60 seconds BGP convergence
    - Global: removes entire PoP from routing
    
Best practice for anycast services:
  Health check BEFORE withdrawing BGP announcement
  Keep BGP up only when service is healthy
  BGP communities for controlled failover
```

---

### 📐 Scale Considerations

```
Anycast at different scales:

Small (1-5 PoPs):
  Manual BGP configuration per PoP
  Simple: announce /24 or /32 from each PoP
  Works: if you have ASN and IP space

Medium (10-50 PoPs):
  Automated BGP management (Bird2, FRR)
  Route reflectors for iBGP within AS
  Health-check driven announcement/withdrawal
  
Large (100+ PoPs, Cloudflare/Google scale):
  Custom BGP software and route management
  Traffic engineering: adjust BGP attributes per PoP
  Per-PoP capacity management
  Real-time traffic shifting (drain a PoP for maintenance)
  Anycast + ECMP: multiple paths within a PoP (per-flow)

Anycast and TCP (challenge):
  TCP is connection-oriented → packets must reach same server
  BGP route changes during connection → route flap → TCP RST
  Solution: BGP route stability at all costs during sessions
  DNS (UDP): anycast works perfectly (stateless)
  TCP: works well when routes are stable
    - Connection affinity maintained by ECMP hash
    - Route change → TCP RST → client reconnects
    - Acceptable for web (browser retries)
    - Not acceptable for long-lived connections (gaming, VoIP)
  
Anycast for gaming/VoIP:
  Route users to nearest PoP
  But: forward to dedicated game server from PoP
  Anycast = edge entry point, not the game server itself
```

---

### 🧭 Decision Guide

```
When to use anycast:
  Global service with latency requirements
  DNS resolvers (always anycast)
  CDN edge nodes
  DDoS mitigation services
  Public infrastructure (NTP, STUN, TURN servers)

When NOT to use anycast:
  Single region: no benefit, more complexity
  TCP-only with long-lived connections: route stability risk
  Without BGP access (hosting-only environments):
    → Use GeoDNS or global LB (AWS Global Accelerator) instead

Anycast requirements:
  Your own ASN (autonomous system number) - apply to ARIN/RIPE/APNIC
  Your own IP address space (/24 minimum for global routing)
  BGP sessions with upstream providers at each PoP
  
Getting started without your own infrastructure:
  Cloudflare: protects any origin → provides anycast IP
  AWS Global Accelerator: anycast for AWS backends
  Google Cloud CDN: anycast for GCP backends
  These services give you anycast benefits without BGP management

Interview system design:
  "How would you design a global DNS service?"
  → Anycast IPs, BGP, 100+ PoPs, stateless, UDP
  
  "How would you handle DDoS?"
  → Anycast (distribute volume), XDP (drop at line rate),
    rate limiting (per-IP, per-ASN), challenge pages
  
  "How would you design a CDN?"
  → Anycast entry, GeoDNS backup, origin pull,
    cache eviction, TLS termination at edge
```