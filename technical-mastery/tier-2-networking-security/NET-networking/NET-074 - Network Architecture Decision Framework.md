---
id: NET-074
title: "Network Architecture Decision Framework"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-053, NET-069, NET-070
used_by: NET-075, NET-083
related: NET-053, NET-069, NET-070, NET-075
tags:
  - networking
  - architecture
  - decision-framework
  - design
  - tradeoffs
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 74
permalink: /technical-mastery/net/network-architecture-decision-framework/
---

**⚡ TL;DR** - Network architecture decisions recur at every
scale: choose a load balancer strategy, decide VPC structure,
select protocol (TCP vs UDP vs QUIC), design security zones,
plan DR strategy. This entry provides structured decision
frameworks for the most common choices with explicit
criteria. The goal is reusable decision logic, not one-
time answers. The frameworks encode: what questions to
ask, what criteria matter, and what the trade-offs are.

| #074 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | Networking System Design Interview Patterns (NET-053), Multi-Region Architecture (NET-069), Zero Trust (NET-070) | |
| **Used by:** | Build a Secure Network Platform (NET-075), Networking Career Paths (NET-083) | |
| **Related:** | System Design Patterns, Multi-Region Architecture, Zero Trust, Build a Secure Network Platform | |

---

### ⚙️ Framework 1 - Load Balancer Strategy Selection

```
Questions to ask:
  1. What layer is needed?
     Need SSL termination, HTTP routing → L7 (ALB, nginx)
     Need raw TCP/UDP, maximum throughput → L4 (NLB, HAProxy)
     
  2. What is the session model?
     Stateless: any backend, round-robin
     Stateful: session affinity needed (sticky sessions)
     
  3. What is the health-check granularity?
     Can a port-up check detect app unhealthiness?
     Need: HTTP health endpoint returning 200 only when healthy
     
  4. What is the failover requirement?
     Active-active: multiple AZs, all serving
     Active-passive: hot standby, DNS-based failover
     
Decision matrix:

  USE L7 (ALB, nginx) when:
    - HTTP/HTTPS traffic
    - Path-based routing (/api → service A, / → service B)
    - Host-based routing (api.example.com vs www.example.com)
    - WebSocket upgrade support
    - SSL termination at the load balancer
    - Header manipulation (add X-Real-IP, etc.)
    
  USE L4 (NLB, HAProxy L4) when:
    - Non-HTTP protocols: gRPC without HTTP/2 termination,
      SMTP, IMAP, database proxy (TCP)
    - Need to preserve source IP without proxy protocol overhead
    - Extremely high throughput (L7 inspection adds overhead)
    - Ultra-low latency (L4 has lower per-packet overhead)
    
  USE DNS-based (Route53 + health checks) when:
    - Global routing (multi-region)
    - Disaster recovery: failover to backup region
    - Geographic routing (EU users → EU region)
    
  USE Anycast (Global Accelerator, Cloudflare) when:
    - Non-HTTP services need global routing
    - Need consistent IP regardless of region failover
    - TCP connection needs to enter AWS backbone ASAP
```

---

### ⚙️ Framework 2 - VPC Design

```
Decision factors:
  A. How many environments?
     Dev + staging + prod → separate VPCs (blast radius)
     B. How many teams?
     One team: one VPC per env
     Multiple teams: consider separate VPCs per team × env
     C. Cross-team communication needed?
     Yes → VPC peering or Transit Gateway
     D. Compliance scope?
     PCI/HIPAA: CDE/PHI in isolated VPC (separate from web tier)

Subnet tier design:
  Minimum tiers:
    Public: ALB, NAT Gateway (exposed to internet)
    Private: application servers (no direct internet)
    Database: database instances (access only from private tier)
    
  Why 3 AZs minimum:
    AZ failure: 1 of 3 AZs = 33% capacity loss (not 50%)
    Even load balancing: 3 AZs = more uniform distribution
    AWS SLA: multi-AZ required for most resilience guarantees
    
  CIDR sizing:
    Don't over-allocate (wastes address space)
    Don't under-allocate (can't expand subnet without recreation)
    Rule of thumb: /21 (2,048 hosts) per subnet tier per AZ
    Typical pattern: VPC = /16 (65,536), subnets = /21 (2,048 each)
    
  Egress routing:
    Public subnets: Internet Gateway (direct internet)
    Private subnets: NAT Gateway (outbound only, no inbound)
    DB subnets: no NAT (databases should not reach internet)
    
CIDR allocation (commit before creating first VPC):
  Organisation-wide IPAM:
  10.0.0.0/16 → prod us-east-1
  10.1.0.0/16 → prod eu-west-1
  10.2.0.0/16 → prod ap-southeast-1
  10.10.0.0/16 → staging us-east-1
  10.11.0.0/16 → staging eu-west-1
  10.20.0.0/16 → dev
  Document this and ENFORCE via code (Terraform variables)
  Never modify after creation
```

---

### ⚙️ Framework 3 - Protocol Selection

```
Application type → protocol selection:

Request-response (web apps, APIs):
  Simple, browser clients → HTTP/1.1 + HTTPS
  Performance matters, modern clients → HTTP/2
  Very high RPS, high latency network → HTTP/3 (QUIC)
  
Service-to-service (internal):
  Typed schema, high throughput → gRPC (HTTP/2 + protobuf)
  Simple integration, JSON everywhere → REST (HTTP/1.1)
  Message queue semantics → AMQP, Kafka (not HTTP)
  
Real-time (bidirectional):
  Browser to server real-time → WebSocket
  Server-sent events (one-way stream) → SSE
  Complex messaging protocol → MQTT (IoT), STOMP
  
Low-latency, unreliable OK:
  Live video streaming → UDP (or RTP over UDP)
  Voice/video call (WebRTC) → DTLS-SRTP (UDP-based)
  Online gaming → UDP with custom reliability layer
  
Between networks / routing:
  External routing (internet between ASNs) → BGP
  Internal routing (within network) → OSPF, IS-IS
  
Decision factors that override defaults:
  Browser as client → must support (no gRPC natively)
  NAT traversal needed → QUIC/HTTP/3 works better
  Streaming large files → HTTP with Range requests
  Very short messages (< 100 bytes) → UDP overhead wins
  Reliable, ordered, large → TCP always
```

---

### ⚙️ Framework 4 - Security Zone Design

```
Zones from least to most trusted:
  Internet → DMZ → Application → Database
  Each boundary: firewall/security group
  
Zone definitions:
  Internet Zone:
    Source: any IP
    Content: public DNS, CDN cached content
    
  DMZ (De-Militarized Zone):
    Components: ALB, WAF, Reverse Proxy
    Allowed in: 80/443 from internet
    Allowed out: app port from DMZ → Application zone
    
  Application Zone:
    Components: app servers, API services
    Allowed in: from DMZ only (no direct internet)
    Allowed out: DB port → Database zone; 443 → internet (via NAT)
    
  Database Zone:
    Components: databases, caches
    Allowed in: DB port from Application zone only
    Allowed out: nothing (databases do not initiate connections)
    
AWS implementation:
  Internet Zone: public subnets with IGW
  DMZ: ALB in public subnet + SG: 443 from 0.0.0.0/0
  Application: private subnets + SG: 8080 from ALB SG
  Database: DB subnets + SG: 5432 from App SG only
  
Compliance overlays:
  PCI-DSS: CDE (card data environment) = its own VPC
    No connection from CDE to non-CDE without explicit firewall rule
  HIPAA: PHI data: encrypted at rest + audit log every access
  SOC 2: evidence of network security controls (Terraform code is evidence)
```

---

### ⚙️ Framework 5 - Disaster Recovery Selection

```
RTO (Recovery Time Objective): how long can you be down?
RPO (Recovery Point Objective): how much data can you lose?

DR Tier selection:

Cold standby (RTO: hours, RPO: hours):
  Backup: snapshots taken daily/hourly
  Recovery: restore snapshots, recreate infrastructure from Terraform
  Cost: low (only storage for snapshots)
  When to use: non-production, internal tools, acceptable 4-hour RTO
  
Warm standby (RTO: minutes, RPO: minutes):
  Infrastructure: exists in secondary region (scaled down)
  Data: async replication (e.g., RDS read replica cross-region)
  Failover: scale up secondary, redirect DNS
  Cost: 20-30% of production (secondary runs at low scale)
  When to use: business-critical, SLA requires < 30 min recovery
  
Active-passive (RTO: < 5 min, RPO: seconds):
  Infrastructure: full production scale in secondary region
  Data: sync or near-sync replication
  Failover: DNS change or Global Accelerator endpoint switch
  Cost: ~2x (full infra in both regions)
  When to use: compliance requires defined RTO/RPO, 24x7 service
  
Active-active (RTO: near-zero, RPO: near-zero):
  Both regions: serving live traffic simultaneously
  Failover: automatic (DNS weighted 50/50, one region becomes 100%)
  Cost: 2x + data synchronization complexity
  When to use: highest criticality, can afford complexity
  Complexity: write conflicts, consistency across regions
  
Calculate: cost of downtime per hour vs cost of DR tier
  If 1 hour of downtime costs $100K:
    Active-active at $50K/month extra: ROI in 2 months
    Active-passive at $20K/month extra: ROI in < 1 month
    Cold standby at $1K/month: acceptable if 4-hour RTO OK
```

---

### 📐 Scale Transitions

```
Scale transitions that require architecture changes:

1 → 10 services:
  Network change: add internal load balancer
  Why: service-to-service DNS (not hardcoded IP)
  
10 → 100 services:
  Network change: consider service mesh
  Why: mTLS, circuit breakers, retries need systematic solution
  Network change: Transit Gateway (too many VPC peers)
  
100 → 1,000 services:
  Network change: ambient mesh (no sidecar overhead)
  Network change: multiple TGW attachments, network account
  Network change: dedicated security VLAN/VPC
  
1,000 → 10,000 services (hyperscale):
  Custom BGP routing, custom hardware
  Google: Andromeda (custom network virtualization)
  Facebook: custom switch firmware
  AWS: Nitro cards (hardware offload for networking)
  
At each transition:
  Complexity increases non-linearly
  Documentation must precede complexity
  Automate before manual becomes impossible
```

---

### 🧭 Decision Guide - Architecture Review Checklist

```
Before any network architecture design review:

Network fundamentals:
  [ ] CIDR allocation documented and non-overlapping
  [ ] Subnet tier rationale (why these tiers)
  [ ] AZ count and failover behavior
  [ ] Egress routing (IGW vs NAT vs private link)
  
Security:
  [ ] Defense-in-depth zones defined
  [ ] Least-privilege SG rules (not 0.0.0.0/0 internally)
  [ ] TLS on all service connections
  [ ] Secrets never in network logs or metrics
  
Reliability:
  [ ] Single points of failure identified
  [ ] RTO/RPO defined and architecture matches
  [ ] Health checks: L7 not just L4
  [ ] Circuit breakers for external dependencies
  
Scalability:
  [ ] Current scale and next 10x scale both work
  [ ] CIDR blocks large enough for 2x growth
  [ ] Load balancer can scale with service (auto-scaling group)
  
Operations:
  [ ] All network config in version control (Terraform)
  [ ] Drift detection enabled
  [ ] Runbook: how to failover (and tested)
  [ ] Network change review process documented
  
Cost:
  [ ] Cross-AZ and cross-region data transfer cost estimated
  [ ] NAT Gateway costs (high egress = high NAT cost)
  [ ] Over-provisioned resources reviewed
```
permalink: /technical-mastery/net/network-architecture-decision-framework/
---