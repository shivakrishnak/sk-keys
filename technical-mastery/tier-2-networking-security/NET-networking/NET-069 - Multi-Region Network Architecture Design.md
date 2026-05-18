---
id: NET-069
title: "Multi-Region Network Architecture Design"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-043, NET-052, NET-060
used_by: NET-075, NET-083
related: NET-052, NET-060, NET-075
tags:
  - networking
  - multi-region
  - architecture
  - design
  - global-routing
  - vpc-peering
  - transit-gateway
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 69
permalink: /technical-mastery/net/multi-region-network-architecture-design/
---

**⚡ TL;DR** - Multi-region network architecture connects
geographically distributed cloud regions to enable:
global user routing, disaster recovery, data residency
compliance, and latency optimization. Key patterns:
VPC peering (direct, simple, limited scale), Transit
Gateway (hub-and-spoke, scales to 100s of VPCs), Global
Load Balancer (routes users to nearest region), AWS
Global Accelerator (anycast for TCP/UDP). Trade-offs
center on data transfer costs, consistency (data
replication across regions), and routing complexity.

| #069 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | DNS Resolution Deep Dive (NET-043), Network Segmentation (NET-052), Anycast Routing (NET-060) | |
| **Used by:** | Build a Secure Network Platform (NET-075), Networking Career Paths (NET-083) | |
| **Related:** | Network Segmentation, Anycast Routing, Build a Secure Network Platform | |

---

### 🔥 The Problem This Solves

A US-based service has users in Europe and Asia. Without
multi-region: all users hit the US data center (150-200ms
latency from Europe, 250ms from Asia). European users
experience slow response; US data center is the single
point of failure. With multi-region: European users
served from EU region (< 20ms), Asian from Asia region.
Partial outage of one region: automatic failover.
GDPR: data stays in EU. The networking problem: how do
these regions communicate, how do you route users to
the right one, and how do you handle internal traffic?

---

### 🧠 Intuition: The Three Network Problems

```
Multi-region has three distinct networking problems:

1. USER → REGION routing (inbound):
   "Which region serves this user?"
   Solutions: GeoDNS, Global Load Balancer, Anycast
   
2. REGION → REGION traffic (data synchronization):
   "How does region A talk to region B?"
   Solutions: VPC peering, Transit Gateway, VPN, Direct Connect
   
3. SERVICE → SERVICE within a region (lateral):
   "How do microservices in the same region communicate?"
   Solutions: internal LB, service mesh (covered in NET-062)

Each problem needs a different solution.
Don't use the same mechanism for all three.
```

---

### ⚙️ Pattern 1 - User Routing: GeoDNS

```
GeoDNS: DNS returns different A/AAAA records based on
  the requesting resolver's geographic location

CloudFlare/Route53 setup:
  US users → 52.1.2.3 (US load balancer)
  EU users → 54.1.2.3 (EU load balancer)
  AP users → 13.1.2.3 (Asia load balancer)
  
AWS Route53 Geolocation routing:
  Record set: api.example.com
  Record 1: Continent=North America → 52.1.2.3 TTL=60s
  Record 2: Continent=Europe → 54.1.2.3 TTL=60s
  Record 3: Default → 52.1.2.3 (fallback to US)
  
Limitations:
  DNS resolver location ≠ user location
  Corporate proxies in US → all employees get US IP
  VPN users → get VPN exit country's IP
  TTL must be short for fast failover (60-300s)
  
Latency-based routing (Route53 alternative):
  Measures latency from AWS edge to each endpoint
  Returns IP for lowest-latency endpoint per region
  More accurate than geolocation for performance
  
Failover: health check → if endpoint unhealthy, DNS returns backup
  Health check: HTTP probe, configurable interval
  Failover time: TTL + health check interval
  With TTL=60 + check=10s: failover in ~70 seconds
```

---

### ⚙️ Pattern 2 - Global Accelerator (Anycast for TCP)

```
AWS Global Accelerator:
  Provides anycast IP addresses
  User traffic enters AWS backbone at nearest edge PoP
  Routes over AWS's private global backbone to target region
  
Benefits over GeoDNS:
  No DNS TTL propagation delay
  AWS backbone routing (private, faster than internet)
  Automatic failover: no DNS changes (IP stays the same)
  Works for TCP/UDP (not just HTTP)
  
vs Pure anycast (Cloudflare model):
  Cloudflare: CDN infrastructure, web-focused
  Global Accelerator: general TCP/UDP, connects to AWS backends
  
Cost: $0.025/hour per accelerator + data transfer
Use when:
  Non-HTTP services (gaming, custom TCP protocols)
  Need anycast without managing BGP
  Need consistent IP across regions
  Ultra-fast failover (< 30 seconds vs DNS minutes)
  
Example architecture:
  User → anycast IP (GA) → nearest AWS PoP
       → AWS global backbone → us-east-1 ALB
       → Auto Failover: if us-east-1 unhealthy
       → AWS global backbone → eu-west-1 ALB
  
  IP addresses never change for clients
  No cache invalidation problem
  RTT improvement: 20-30% for cross-region users
    (AWS backbone vs public internet)
```

---

### ⚙️ Pattern 3 - Cross-Region VPC Connectivity

**VPC Peering:**

```hcl
# VPC Peering: direct connection between two VPCs
# Simple, low latency, no bandwidth limit (scales with instances)
# Limitation: non-transitive (A-B and B-C ≠ A-C)

resource "aws_vpc_peering_connection" "us_eu" {
  vpc_id        = aws_vpc.us_east.id        # requester
  peer_vpc_id   = aws_vpc.eu_west.id        # accepter
  peer_region   = "eu-west-1"
  auto_accept   = false                     # accepter must accept

  tags = { Name = "us-east-to-eu-west" }
}

# Route table update: tell US VPC to route EU CIDRs via peering
resource "aws_route" "us_to_eu" {
  route_table_id            = aws_route_table.us_private.id
  destination_cidr_block    = "10.1.0.0/16"  # EU VPC CIDR
  vpc_peering_connection_id = aws_vpc_peering_connection.us_eu.id
}

# CIDR requirement: VPCs being peered must have non-overlapping CIDRs
# us-east-1: 10.0.0.0/16
# eu-west-1: 10.1.0.0/16   ← different /16 prefix
# ap-east-1: 10.2.0.0/16
# If CIDRs overlap: peering fails
```

**Transit Gateway:**

```hcl
# Transit Gateway: hub-and-spoke for many VPCs
# N VPCs connect to TGW = fully connected (transitive!)
# 3 VPCs with peering: 3 peering connections needed
# 3 VPCs with TGW: 3 TGW attachments (scales linearly)
# 100 VPCs with TGW: 100 attachments (vs 4,950 peerings)

resource "aws_ec2_transit_gateway" "main" {
  description                     = "Main transit gateway"
  amazon_side_asn                 = 64512
  auto_accept_shared_attachments  = "enable"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  tags = { Name = "main-tgw" }
}

# Attach US VPC to transit gateway
resource "aws_ec2_transit_gateway_vpc_attachment" "us_east" {
  subnet_ids         = [aws_subnet.us_private.id]
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = aws_vpc.us_east.id
  tags               = { Name = "us-east-attachment" }
}

# For cross-region: TGW peering between regions
resource "aws_ec2_transit_gateway_peering_attachment" "us_eu" {
  peer_account_id         = var.account_id
  peer_region             = "eu-west-1"
  peer_transit_gateway_id = aws_ec2_transit_gateway.eu_west.id
  transit_gateway_id      = aws_ec2_transit_gateway.main.id
  tags                    = { Name = "us-eu-tgw-peering" }
}

# Traffic path with TGW:
# us-east pod → TGW → TGW peering link → eu-west TGW → eu-west pod
# All via AWS backbone (private network, encrypted)
```

---

### ⚙️ Data Transfer Costs: The Hidden Constraint

```
AWS data transfer pricing (2024 approximate):
  Within same AZ: free (ec2 to ec2 within AZ via private IP)
  Cross-AZ (same region): $0.01/GB each direction
  Cross-region (us-east-1 to eu-west-1): $0.02/GB
  Internet egress (to users): $0.09/GB (first 10TB/month)
  VPC peering cross-region: same as cross-region transfers
  
Cost example (high-traffic service):
  10TB/month cross-region sync: 10,000 GB × $0.02 = $200/month
  100TB/month cross-region: $2,000/month
  1PB/month: $20,000/month
  
Architecture optimizations to reduce transfer:
  1. Keep hot data local: don't cross-region for every request
  2. Async replication: batch updates rather than per-record sync
  3. Read replicas: serve reads locally, writes to primary
  4. CDN: user-facing content served from edge (not origin)
  5. Data compression: compress before cross-region transfers
  
When cross-region costs dominate budget:
  Review data sync frequency: is every-second sync needed?
  Consider: active-passive instead of active-active
    (active-passive: reads from local, writes only to primary)
  Consider: shard by region (EU data stays in EU)
```

---

### ⚙️ Wrong vs Right: Overlapping CIDR Blocks

```hcl
# BAD: creating VPCs with overlapping CIDRs (common mistake)
resource "aws_vpc" "us_east" {
  cidr_block = "10.0.0.0/16"   # 10.0.0.0 - 10.0.255.255
}

resource "aws_vpc" "eu_west" {
  cidr_block = "10.0.0.0/16"   # SAME range! Cannot peer
}

# Result: VPC peering fails (routing is ambiguous)
# Even TGW attachment fails with overlapping CIDRs
# No way to add routing: both ranges look identical

# BAD: using 10.0.0.0/8 everywhere (very common)
# "Our company standard is 10.x.x.x"
# All teams use 10.x.x.x → when you need to peer, you can't

# GOOD: plan address space before creating VPCs
# Allocate unique /16 or /18 blocks per region/environment:
# 10.0.0.0/16  - us-east-1 production
# 10.1.0.0/16  - eu-west-1 production
# 10.2.0.0/16  - ap-east-1 production
# 10.3.0.0/16  - us-east-1 staging
# 10.4.0.0/16  - eu-west-1 staging
# ...
# Never re-use ranges within any organization
# Store allocation in internal IPAM tool (or Terraform tfvars)

resource "aws_vpc" "us_east" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "eu_west" {
  cidr_block = "10.1.0.0/16"   # different /16 block
}
# Now peering works without routing conflicts
```

---

### 📐 Scale Considerations

```
At 5 VPCs:
  VPC peering works fine: 10 peering connections
  No hub needed
  
At 20 VPCs:
  190 peering connections = unmanageable
  Use: Transit Gateway (20 TGW attachments)
  
At 100 VPCs:
  TGW required: 100 attachments
  Cost: TGW attachment $0.05/hour × 100 + data processing
  Consider: shared services VPC (VPC with shared databases, DNS)
  
At 1,000 VPCs (enterprise):
  Multiple TGWs per region, peered together
  AWS Network Manager: centralized monitoring
  AWS Resource Access Manager (RAM): share TGW across accounts
  
Multi-account vs multi-VPC:
  AWS best practice: separate account per workload/team
  Why: billing, IAM, security blast radius
  Network challenge: connecting 100s of accounts
  Solution: network "hub" account with TGW, share to spoke accounts

Cross-region latency:
  us-east-1 to eu-west-1: ~80ms RTT (AWS backbone)
  vs public internet: ~90ms RTT (similar but with jitter)
  AWS backbone: more predictable, fewer congestion events
  
For distributed databases:
  Write latency: 80ms per write for cross-region replication
  With 2 regions: writes take at least 80ms extra
  Solution: async replication (eventual consistency)
    Or: single-region writes with cross-region reads
```

---

### 🧭 Decision Guide

```
Architecture selection by requirement:

User serving (web traffic):
  < 5 regions: GeoDNS with Route53 + health checks
  > 5 regions: CDN (CloudFront, Cloudflare) + GeoDNS
  Non-HTTP: AWS Global Accelerator (anycast)

Cross-region connectivity:
  < 5 VPCs: VPC Peering (simple, cheap)
  5-100 VPCs: Transit Gateway
  100+ VPCs: Transit Gateway + RAM (multi-account)
  Dedicated bandwidth: Direct Connect (private link to AWS)

Data residency (GDPR, data sovereignty):
  Route EU users to EU region ONLY
  Ensure no EU data flows to US region
  Cross-region replication: may be prohibited
  Solution: shard data by region, no sync across EU/non-EU

Active-active vs Active-passive:
  Active-active:
    Both regions serve traffic simultaneously
    Higher cost (run full infrastructure in both)
    Higher complexity (write conflicts, consistency)
    Use: max availability, cannot tolerate regional failure
    
  Active-passive:
    Primary region handles all traffic
    Secondary: hot standby (same infra, no live traffic)
    Failover: DNS change or Global Accelerator endpoint change
    Lower cost (secondary can be scaled down)
    Use: DR compliance, can tolerate 60-120s failover

Critical planning step:
  Before creating first VPC: design the CIDR allocation
  Document in code (Terraform variables, IPAM system)
  Reserve blocks for future regions and environments
  NEVER re-use address space within the organization
```