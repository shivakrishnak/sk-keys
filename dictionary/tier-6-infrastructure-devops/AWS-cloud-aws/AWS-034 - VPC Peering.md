---
layout: default
title: "VPC Peering"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 34
permalink: /cloud-aws/vpc-peering/
id: AWS-034
category: "Cloud - AWS"
difficulty: "★★★"
depends_on:
  ["VPC", "Subnets (Public / Private)", "Internet Gateway / NAT Gateway"]
used_by: ["Transit Gateway", "EKS", "RDS"]
related:
  [
    "VPC",
    "Transit Gateway",
    "Internet Gateway / NAT Gateway",
    "Security Groups",
  ]
tags: [aws, vpc-peering, networking, cross-account, connectivity, cloud]
---

# VPC Peering

## ⚡ TL;DR

**VPC Peering** connects two VPCs (same or different accounts/regions) via a private network link. Traffic stays on AWS backbone - no internet, no VPN. Non-transitive: A↔B and B↔C does NOT mean A can reach C. Requires non-overlapping CIDR blocks. Best for: 2-3 VPCs with simple topology. For many VPCs: use Transit Gateway instead.

---

## 🔥 Problem This Solves

Services in different VPCs (different accounts, regions, or teams) need to communicate privately without going through the public internet. VPC Peering provides direct, private connectivity with low latency.

---

## 📘 Textbook Definition

VPC Peering is a networking connection between two VPCs that enables routing traffic between them using private IPv4 or IPv6 addresses. Peered VPCs can be in the same or different AWS accounts and in the same or different regions. VPC peering is non-transitive: peering relationships do not extend through intermediary VPCs.

---

## ⏱️ 30 Seconds

```
VPC A (10.0.0.0/16) ←--peering--→ VPC B (172.16.0.0/16)

Requirements:
  - Non-overlapping CIDRs (critical!)
  - Requester creates peering request
  - Accepter accepts request
  - Route tables updated in BOTH VPCs
  - Security Groups updated in BOTH VPCs

Non-transitive:
  A ←→ B, B ←→ C  ≠  A can reach C
  Each pair needs its own peering connection

Cost: Free within same region
      $0.01/GB cross-region (+ region data transfer)
```

---

## 🔩 First Principles

- **Layer 3 routing**: AWS updates routing; no tunneling, no encryption overhead
- **Non-transitive**: strictly point-to-point; no hub-and-spoke via single VPC
- **CIDR non-overlap**: overlapping CIDRs = invalid peering (plan CIDRs at org level)
- **Bidirectional route updates**: routes must be added to route tables in BOTH VPCs
- **Security Groups**: after peering, SG rules can reference the peer's SG ID (same account same region only)

---

## 🧪 Thought Experiment

You have a shared-services VPC (monitoring, logging) and 5 team VPCs. VPC peering: 5 connections from shared-services to each team VPC. But teams also need to communicate? N × (N-1) / 2 peering connections (10 for 5 teams). Now a 6th team joins: 5 more connections. Operationally complex → use Transit Gateway.

---

## 🧠 Mental Model / Analogy

VPC Peering is a **direct private phone line** between two offices: fast, direct, no intermediary. But it's point-to-point - you need a separate line for each pair. If 10 offices all want to talk to each other, you need 45 direct lines. At that point, a switchboard (Transit Gateway) makes more sense.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create peering request, accept it, add routes in both VPCs, update Security Groups. Non-overlapping CIDRs required.

**Level 2 - Practitioner**: Cross-account peering: requester sends request, accepter (different account) accepts. Cross-region: same process, higher latency + data transfer cost. Cannot reference Security Group IDs cross-account in SG rules - use CIDR instead.

**Level 3 - Advanced**: CIDR planning matters: plan at org level before creating VPCs. Use 10.0.0.0/8 range, allocate /16 per VPC. With Transit Gateway: more flexible but more cost. Peering vs TGW decision: ≤3 VPCs = peering; >3 = TGW.

**Level 4 - Expert**: Longest prefix match: with both peering route and internet route, traffic uses most specific route. Route table limit: 100 routes per route table (soft limit 1000) - many peerings = many routes. DNS resolution for peered VPCs: must enable `enableDnsResolution` and `enableDnsHostnames` on both VPCs for private DNS to work across peering. Resource Access Manager (RAM): alternative to peering for sharing specific resources (subnets, Transit Gateway) without full VPC access.

---

## ⚙️ How It Works

### Creating VPC Peering (Terraform)

```hcl
# Same-account, same-region peering
resource "aws_vpc_peering_connection" "app_to_shared" {
  vpc_id        = aws_vpc.app.id
  peer_vpc_id   = aws_vpc.shared.id
  auto_accept   = true  # auto-accept for same account

  accepter {
    allow_remote_vpc_dns_resolution = true
  }
  requester {
    allow_remote_vpc_dns_resolution = true
  }

  tags = { Name = "app-to-shared-services" }
}

# Add route in APP VPC: to reach SHARED VPC (172.16.0.0/16) via peering
resource "aws_route" "app_to_shared" {
  route_table_id            = aws_route_table.app_private.id
  destination_cidr_block    = "172.16.0.0/16"   # SHARED VPC CIDR
  vpc_peering_connection_id = aws_vpc_peering_connection.app_to_shared.id
}

# Add route in SHARED VPC: to reach APP VPC (10.0.0.0/16) via peering
resource "aws_route" "shared_to_app" {
  route_table_id            = aws_route_table.shared_private.id
  destination_cidr_block    = "10.0.0.0/16"     # APP VPC CIDR
  vpc_peering_connection_id = aws_vpc_peering_connection.app_to_shared.id
}
```

### Cross-Account Peering (CLI)

```bash
# Account A (requester)
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-aaaaaaaa \
  --peer-vpc-id vpc-bbbbbbbb \
  --peer-owner-id 123456789012 \  # Account B's account ID
  --region us-east-1

# Account B (accepter)
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-12345 \
  --region us-east-1

# Both accounts: add routes
aws ec2 create-route \
  --route-table-id rtb-aaaaa \
  --destination-cidr-block 172.16.0.0/16 \   # peer VPC CIDR
  --vpc-peering-connection-id pcx-12345
```

### Non-Transitive Limitation

```
Network topology with peering:
  VPC-A (10.0.0.0/16) ←→ VPC-B (10.1.0.0/16)
  VPC-B (10.1.0.0/16) ←→ VPC-C (10.2.0.0/16)

VPC-A → VPC-B: ✅ (direct peering)
VPC-B → VPC-C: ✅ (direct peering)
VPC-A → VPC-C: ❌ (no direct peering; non-transitive)

Fix Option 1: Create VPC-A ←→ VPC-C peering (2 VPCs = 3 connections)
Fix Option 2: Transit Gateway (attach all 3 VPCs; transitive routing enabled)
```

---

## ⚖️ Comparison Table

|                           | VPC Peering            | Transit Gateway             |
| ------------------------- | ---------------------- | --------------------------- |
| **Topology**              | Point-to-point         | Hub and spoke               |
| **Transitive**            | ❌                     | ✅                          |
| **Cost (per attachment)** | Free (same region)     | $0.05/hr + $0.02/GB         |
| **Best for**              | ≤3 VPCs, simple        | ≥4 VPCs, complex            |
| **Cross-region**          | ✅ ($0.01/GB)          | ✅ (TGW peering)            |
| **Cross-account**         | ✅                     | ✅                          |
| **Route management**      | Manual per route table | Centralized TGW route table |

---

## ⚠️ Common Misconceptions

| Misconception                | Reality                                                                 |
| ---------------------------- | ----------------------------------------------------------------------- |
| "Peering = VPN"              | Peering uses AWS backbone directly; no encryption overhead (unlike VPN) |
| "A↔B + B↔C means A↔C"        | Non-transitive; A needs direct peering with C                           |
| "Can peer overlapping CIDRs" | Overlapping CIDRs: invalid peering connection                           |
| "Peering is free"            | Same-region: free. Cross-region: $0.01/GB each direction                |

---

## 🔗 Related Keywords

- [Transit Gateway](/cloud-aws/transit-gateway/) - scalable alternative for many VPCs
- [VPC](/cloud-aws/vpc/) - the component being peered
- [Internet Gateway / NAT Gateway](/cloud-aws/internet-gateway-nat-gateway/) - alternative outbound mechanisms

---

## 📌 Quick Reference Card

```bash
# Create peering connection
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-aaaaaaaa \
  --peer-vpc-id vpc-bbbbbbbb

# Accept peering connection
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-12345

# List peering connections
aws ec2 describe-vpc-peering-connections \
  --filters Name=status-code,Values=active

# Delete peering connection
aws ec2 delete-vpc-peering-connection \
  --vpc-peering-connection-id pcx-12345

# Check routes for peering
aws ec2 describe-route-tables \
  --filters Name=route.vpc-peering-connection-id,Values=pcx-12345
```

---

## 🧠 Think About This

The critical VPC Peering pre-condition is **non-overlapping CIDR blocks** - and this must be planned before creating any VPC. Teams that create VPCs ad-hoc (using default 10.0.0.0/16 everywhere) eventually face the painful situation where VPC peering is impossible because all their VPCs have the same CIDR. Fixing this requires: migrating workloads to new VPCs with unique CIDRs, which is a significant operational effort. The solution is an organization-wide CIDR allocation strategy: assign a /8 (e.g., 10.0.0.0/8), divide into /12 per business unit, divide into /16 per VPC. Document this in a CIDR registry (spreadsheet or AWS IPAM). Teams should request CIDR allocations before creating VPCs, not after - the same way you'd plan IP addressing before cabling a physical data center.
