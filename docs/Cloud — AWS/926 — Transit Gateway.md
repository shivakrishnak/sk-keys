---
layout: default
title: "Transit Gateway"
parent: "Cloud — AWS"
nav_order: 926
permalink: /cloud-aws/transit-gateway/
number: "0926"
category: "Cloud — AWS"
difficulty: "★★★"
depends_on: ["VPC", "VPC Peering", "Region / AZ / Edge Location"]
used_by: ["K8s Multi-Cluster"]
related:
  [
    "VPC Peering",
    "VPC",
    "Subnets (Public / Private)",
    "Internet Gateway / NAT Gateway",
  ]
tags: [aws, transit-gateway, networking, vpc, hub-spoke, cloud, connectivity]
---

# Transit Gateway

## ⚡ TL;DR

**Transit Gateway (TGW)** is a managed hub for connecting many VPCs and on-premises networks. Attach VPCs + VPN + Direct Connect → they all route through TGW. Solves the N × (N-1)/2 peering problem: N VPCs need only N attachments to TGW. **Cost**: $0.05/hr per attachment + $0.02/GB processed. Worth it when you have ≥4 VPCs requiring interconnectivity.

---

## 🔥 Problem This Solves

VPC Peering is non-transitive and point-to-point. With 20 VPCs all needing interconnectivity: 190 peering connections, 190 × 2 route table entries each, no centralized control. Transit Gateway: 20 attachments, centralized route tables, transitive routing, on-premises connectivity via one connection.

---

## 📘 Textbook Definition

AWS Transit Gateway is a regional network transit hub that connects multiple VPCs, AWS accounts, and on-premises networks. It uses a hub-and-spoke architecture where each network (VPC, VPN connection, Direct Connect Gateway) attaches to the TGW. Routing between attachments is controlled via TGW route tables.

---

## ⏱️ 30 Seconds

```
VPC A ─┐
VPC B ─┤
VPC C ─┼─→ Transit Gateway ←─ VPN (on-premises)
VPC D ─┤                  ←─ Direct Connect
VPC E ─┘

All VPCs can communicate via TGW.
On-premises can reach all VPCs via single VPN connection.
Transitive routing: A can reach C (unlike VPC peering).

Cost: $0.05/hr per attachment × 20 VPCs = $1/hr = $720/mo
      + $0.02/GB processed data
```

---

## 🔩 First Principles

- **Hub-and-spoke**: TGW is the hub; VPCs/VPN/DX are spokes
- **Transitive routing**: unlike peering; VPC-A to VPC-C works through TGW
- **TGW route tables**: control which attachments can reach which (segmentation)
- **Regional**: one TGW per region; cross-region via TGW peering
- **Supports**: VPC, VPN, Direct Connect, SD-WAN (via VPN), other TGWs

---

## 🧪 Thought Experiment

Company has 15 teams, each with a prod VPC and dev VPC = 30 VPCs. Need: (1) all prod VPCs can talk to each other, (2) dev VPCs can talk to each other, (3) dev cannot reach prod. VPC Peering: 435 connections, complex rules. TGW with two route tables: "prod-rt" and "dev-rt" — prod attachments associated with prod-rt, dev attachments with dev-rt. No prod↔dev routes in either table. Clean isolation.

---

## 🧠 Mental Model / Analogy

Transit Gateway is an **airport hub** (vs VPC Peering's direct flights): instead of direct flights between every pair of cities (peering), all flights connect through a central hub (TGW). The hub controls routing: "flights between international terminals are allowed; domestic ↔ international requires customs/separate route table."

---

## 📶 Gradual Depth

**Level 1 — Beginner**: TGW replaces complex peering meshes. Attach VPCs + VPN, get full connectivity. More expensive than peering but operationally simpler at scale.

**Level 2 — Practitioner**: TGW route tables for network segmentation: create multiple route tables, associate attachments to control who can reach whom. Propagation: TGW automatically learns VPC CIDRs (can disable for manual control). VPN + TGW: single VPN to on-premises, all VPCs reachable.

**Level 3 — Advanced**: Centralized egress: one NAT Gateway in "egress VPC" → all private VPCs route 0.0.0.0/0 → TGW → egress VPC → NAT GW → internet. Reduces NAT GW cost (one instead of one per VPC per AZ). Centralized inspection: Network Firewall VPC → all traffic routes through for inspection before reaching destination. TGW peering: connect TGWs across regions.

**Level 4 — Expert**: Equal-cost multi-path (ECMP) routing: multiple VPN tunnels to same TGW for bandwidth aggregation (up to 50 Gbps with 25 tunnels). ECMP for Site-to-Site VPN: each tunnel is 1.25 Gbps; 4 ECMP VPN connections = 5 Gbps aggregate. TGW Connect: higher-performance SD-WAN appliance connectivity using GRE tunnels (up to 20 Gbps per Connect attachment). Flow logs: enable per-attachment traffic visibility. AWS Network Manager: global network management across TGWs and on-premises.

---

## ⚙️ How It Works

### TGW with Segmented Route Tables

```hcl
# Transit Gateway
resource "aws_ec2_transit_gateway" "main" {
  description                     = "Main TGW"
  default_route_table_association = "disable"  # custom route tables
  default_route_table_propagation = "disable"
  auto_accept_shared_attachments  = "disable"

  tags = { Name = "main-tgw" }
}

# TGW Route Tables
resource "aws_ec2_transit_gateway_route_table" "prod" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  tags = { Name = "prod-route-table" }
}

resource "aws_ec2_transit_gateway_route_table" "dev" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  tags = { Name = "dev-route-table" }
}

# Attach Prod VPCs
resource "aws_ec2_transit_gateway_vpc_attachment" "prod_vpc" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = aws_vpc.prod.id
  subnet_ids         = [aws_subnet.prod_tgw_a.id, aws_subnet.prod_tgw_b.id]
}

# Associate prod VPC attachment with prod route table
resource "aws_ec2_transit_gateway_route_table_association" "prod_vpc" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.prod_vpc.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.prod.id
}

# Propagate prod VPC routes to prod route table
resource "aws_ec2_transit_gateway_route_table_propagation" "prod_vpc" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.prod_vpc.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.prod.id
}

# VPC route table: send to TGW for all VPC-to-VPC traffic
resource "aws_route" "prod_to_tgw" {
  route_table_id         = aws_route_table.prod_private.id
  destination_cidr_block = "10.0.0.0/8"   # entire org CIDR
  transit_gateway_id     = aws_ec2_transit_gateway.main.id
}
```

### Centralized Egress Architecture

```
Traditional (costly):
  Each VPC has its own NAT Gateway ($32/mo per AZ per VPC)
  10 VPCs × 2 AZs × $32 = $640/mo just for NAT Gateways

Centralized Egress with TGW (cheaper at scale):
  "egress-vpc" has NAT Gateway
  All private VPCs → TGW → egress-vpc → NAT Gateway → internet

TGW cost: 11 attachments × $0.05/hr = $0.55/hr = $396/mo
NAT Gateway: 2 AZs × $32 = $64/mo
Total: $460/mo (vs $640/mo)
Breakeven: ~6 VPCs

But also: single routing policy point for internet access controls
```

### Cross-Account TGW (AWS RAM)

```bash
# Share TGW via Resource Access Manager
aws ram create-resource-share \
  --name "shared-tgw" \
  --resource-arns arn:aws:ec2:us-east-1:123456789012:transit-gateway/tgw-12345 \
  --principals 987654321098  # target account ID

# Target account: accept the RAM invitation
aws ram accept-resource-share-invitation \
  --resource-share-invitation-arn arn:aws:ram:...
```

---

## ⚖️ Comparison Table

| Scenario                     | VPC Peering         | Transit Gateway |
| ---------------------------- | ------------------- | --------------- |
| **2 VPCs**                   | ✅ Preferred (free) | Overkill        |
| **3-5 VPCs**                 | ✅ Manageable       | Optional        |
| **6+ VPCs**                  | Complex mesh        | ✅ Preferred    |
| **On-premises connectivity** | N/A                 | ✅              |
| **Network segmentation**     | Complex             | ✅ Route tables |
| **Cross-region**             | ✅                  | ✅ TGW peering  |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                           |
| ----------------------------------- | ----------------------------------------------------------------- |
| "TGW makes routing automatic"       | Still need routes in each VPC's route table pointing to TGW       |
| "TGW = free like internet gateway"  | $0.05/hr per attachment = real cost at scale                      |
| "One TGW serves all regions"        | TGW is regional; use TGW peering for cross-region                 |
| "Attaching VPC = full connectivity" | Must configure route table association + propagation + VPC routes |

---

## 🔗 Related Keywords

- [VPC Peering](/cloud-aws/vpc-peering/) — simpler alternative for small networks
- [VPC](/cloud-aws/vpc/) — the component being attached to TGW
- [Internet Gateway / NAT Gateway](/cloud-aws/internet-gateway-nat-gateway/) — TGW enables centralized egress

---

## 📌 Quick Reference Card

```bash
# Create TGW
aws ec2 create-transit-gateway \
  --description "Main Transit Gateway" \
  --options AmazonSideAsn=64512

# Attach VPC
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-12345 \
  --vpc-id vpc-aaaaaaaa \
  --subnet-ids subnet-a subnet-b

# List attachments
aws ec2 describe-transit-gateway-attachments \
  --filters Name=transit-gateway-id,Values=tgw-12345

# Describe TGW route tables
aws ec2 describe-transit-gateway-route-tables \
  --filters Name=transit-gateway-id,Values=tgw-12345

# Get routes in TGW route table
aws ec2 search-transit-gateway-routes \
  --transit-gateway-route-table-id tgw-rtb-12345 \
  --filters Name=state,Values=active
```

---

## 🧠 Think About This

The centralized egress pattern with Transit Gateway is one of those architectural decisions where you're trading one type of cost for another — and the math matters. With fewer than 6 VPCs, individual NAT Gateways per VPC are cheaper than a Transit Gateway + centralized NAT. Beyond 6-8 VPCs, the centralized model wins on cost and gains operational advantages: one place to see all internet-bound traffic, one place to add Network Firewall inspection, one place to manage egress security policies. More importantly: when your organization has 50+ VPCs (common in enterprises using AWS Organizations), the Transit Gateway becomes not just cost-effective but architecturally essential — the alternative is an unmanageable mesh of peering connections that no human can reason about or maintain safely.
