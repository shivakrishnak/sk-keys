---
version: 1
layout: default
title: "Subnets (Public  Private)"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 18
permalink: /cloud-aws/subnets-public-private/
id: AWS-018
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on: ["VPC", "Region / AZ / Edge Location"]
used_by:
  [
    "Security Groups",
    "NACLs",
    "Internet Gateway / NAT Gateway",
    "ELB / ALB / NLB",
    "RDS",
    "EKS",
  ]
related: ["VPC", "Security Groups", "NACLs", "Internet Gateway / NAT Gateway"]
tags: [aws, vpc, subnets, networking, public, private, cloud]
---

# Subnets (Public / Private)

## ⚡ TL;DR

A **subnet** is a range of IP addresses within your VPC, confined to a single AZ. **Public subnet**: route table has a route to the Internet Gateway → resources can have public IPs. **Private subnet**: no IGW route → resources have only private IPs. Pattern: ALBs and Bastion hosts in public subnets; EC2 app servers, RDS, and EKS nodes in private subnets.

---

## 🔥 Problem This Solves

You need resources with different internet exposure in the same VPC: load balancers face the public internet, but databases must be completely hidden. Subnets with different route tables solve this - same VPC, different network boundaries.

---

## 📘 Textbook Definition

A subnet is a subdivision of a VPC's IP address range, associated with a specific Availability Zone. Subnets are classified as public (has a default route to an Internet Gateway, allowing direct internet connectivity) or private (no direct internet route; uses NAT Gateway for outbound internet if needed). Each subnet belongs to exactly one AZ.

---

## ⏱️ 30 Seconds

```
Public subnet characteristics:
  ✅ Route: 0.0.0.0/0 → Internet Gateway
  ✅ Resources can have public IP / Elastic IP
  ✅ Resources reachable from internet (if Security Group allows)
  Use for: ALB, NAT Gateway, Bastion host

Private subnet characteristics:
  ❌ No route to Internet Gateway
  ❌ No public IPs (resources only have private IPs)
  ✅ Outbound internet via NAT Gateway in public subnet
  Use for: EC2 app servers, EKS nodes, RDS, ElastiCache

Isolated subnet (database tier):
  ❌ No IGW route
  ❌ No NAT Gateway route
  ❌ Completely isolated from internet
  Use for: RDS, most secure databases
```

---

## 🔩 First Principles

- **Subnet = CIDR slice of VPC**: VPC is 10.0.0.0/16 → subnet can be 10.0.1.0/24
- **AZ-scoped**: one subnet = one AZ; for multi-AZ HA, create one subnet per AZ
- **5 reserved IPs per subnet**: AWS reserves first 4 + last 1 (e.g., /24 = 251 usable IPs, not 256)
- **Route table determines public/private**: it's not a subnet property; it's the route table
- **Resource placement**: where a resource goes determines its reachability

---

## 🧪 Thought Experiment

You have a 3-tier web app. Without subnets: all resources on same network - database IP accessible from internet. With proper subnets: ALB in public subnet (accepts port 443 from 0.0.0.0/0), EC2 in private subnet (accepts port 8080 from ALB's SG only), RDS in isolated subnet (accepts port 5432 from EC2's SG only). Attacker cannot reach database even if web server is compromised.

---

## 🧠 Mental Model / Analogy

Subnets within a VPC are like **floors in an office building**: the public subnet is the ground floor with reception (accessible to visitors), private subnets are upper floors (employees only, visitors need escort), isolated subnets are the vault floor (only certain employees, no visitors, no outside calls). Each floor has its own security rules (route table).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create at least 2 public + 2 private subnets (one per AZ). Put load balancers in public, application servers and databases in private.

**Level 2 - Practitioner**: Separate subnet per tier: public (DMZ), private-app, private-db. This lets you apply different NACLs per tier. Size subnets correctly: `/24` (251 IPs) per subnet is common; EKS may need larger (/21 or /22) for Pod IP space.

**Level 3 - Advanced**: EKS networking: VPC CNI assigns Pod IPs from the VPC subnet. Worker nodes in private subnets need enough IPs for Pods (default: 30 Pods per m5.large = 30 IPs used). Separate "pod subnets" for EKS CIDR expansion. RDS and ElastiCache require a DB Subnet Group (list of subnets across AZs).

**Level 4 - Expert**: Subnet CIDR planning at org level: allocate non-overlapping ranges across accounts for future VPC peering/Transit Gateway. Shared VPC (Resource Access Manager): central networking account owns VPC and shares specific subnets with workload accounts. IPv6 subnets: /64 per subnet; Egress-Only Internet Gateway for IPv6. Secondary CIDR blocks: add 100.64.0.0/10 (CGNAT) to VPC for more IP space without RFC 1918 exhaustion.

---

## ⚙️ How It Works

### Subnet Design for 3-Tier App

```
VPC: 10.0.0.0/16

AZ us-east-1a:
  Public:  10.0.0.0/24   → ALB nodes, NAT Gateway
  Private: 10.0.10.0/24  → EC2 App servers, EKS nodes
  DB:      10.0.20.0/24  → RDS, ElastiCache

AZ us-east-1b:
  Public:  10.0.1.0/24   → ALB nodes, NAT Gateway
  Private: 10.0.11.0/24  → EC2 App servers, EKS nodes
  DB:      10.0.21.0/24  → RDS standby, ElastiCache replica

AZ us-east-1c:
  Public:  10.0.2.0/24   → ALB nodes
  Private: 10.0.12.0/24  → EC2 App servers, EKS nodes
  DB:      10.0.22.0/24  → Optional

Route Tables:
  public-rt:   0.0.0.0/0 → igw
  private-rt-a: 0.0.0.0/0 → nat-a (AZ a NAT)
  private-rt-b: 0.0.0.0/0 → nat-b (AZ b NAT)
  db-rt:       (no 0.0.0.0/0 route - isolated)
```

### EKS Subnet Sizing Consideration

```
Problem: AWS VPC CNI assigns an IP from subnet to each Pod
         m5.large: max 29 Pods (enis × ips_per_eni - 1)

With /24 subnet (251 IPs):
  30 EKS nodes × 29 Pods = 870 Pods needed
  But only 251 IPs available → IP exhaustion!

Solution 1: Larger subnets (/21 = 2,046 IPs per AZ)
Solution 2: VPC CNI prefix delegation (allocates /28 blocks)
Solution 3: Separate pod subnets with secondary CIDR

# Enable prefix delegation (EKS)
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name vpc-cni \
  --configuration-values '{"env":{"ENABLE_PREFIX_DELEGATION":"true"}}'
```

### DB Subnet Group

```hcl
# RDS requires a subnet group (multi-AZ subnets)
resource "aws_db_subnet_group" "main" {
  name = "production-db-subnet-group"

  subnet_ids = [
    aws_subnet.db_a.id,  # us-east-1a
    aws_subnet.db_b.id,  # us-east-1b
    aws_subnet.db_c.id   # us-east-1c
  ]
}

resource "aws_db_instance" "main" {
  db_subnet_group_name = aws_db_subnet_group.main.name
  multi_az             = true  # uses subnets in different AZs
}
```

---

## ⚖️ Comparison Table

| Tier     | Subnet Type | Internet                | Use Case                |
| -------- | ----------- | ----------------------- | ----------------------- |
| **DMZ**  | Public      | Inbound + Outbound      | ALB, NAT GW, Bastion    |
| **App**  | Private     | Outbound only (via NAT) | EC2, ECS, EKS nodes     |
| **Data** | Isolated    | None                    | RDS, ElastiCache, Kafka |

---

## ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------- |
| "'Private' is a subnet property"             | Public/private is determined by route table, not a subnet attribute                   |
| "Private subnet = no internet"               | Private subnet = no inbound; outbound works via NAT Gateway                           |
| "/24 is always enough"                       | EKS clusters easily exhaust /24; plan subnet size for Pod density                     |
| "One NAT Gateway serves all private subnets" | One NAT per AZ needed for HA; cross-AZ NAT = AZ failure = internet outage for that AZ |

---

## 🔗 Related Keywords

- [VPC](/cloud-aws/vpc/) - the parent network
- [Internet Gateway / NAT Gateway](/cloud-aws/internet-gateway-nat-gateway/) - internet connectivity
- [Security Groups](/cloud-aws/security-groups/) - per-resource firewall
- [NACLs](/cloud-aws/nacls/) - per-subnet firewall

---

## 📌 Quick Reference Card

```bash
# List subnets with AZ and CIDR
aws ec2 describe-subnets \
  --filters Name=vpc-id,Values=vpc-12345 \
  --query 'Subnets[].{ID:SubnetId,AZ:AvailabilityZone,CIDR:CidrBlock,Public:MapPublicIpOnLaunch}' \
  --output table

# Create subnet
aws ec2 create-subnet \
  --vpc-id vpc-12345 \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a

# Make public (auto-assign public IP)
aws ec2 modify-subnet-attribute \
  --subnet-id subnet-12345 \
  --map-public-ip-on-launch

# Check available IPs in subnet
aws ec2 describe-subnets \
  --subnet-ids subnet-12345 \
  --query 'Subnets[].AvailableIpAddressCount'

# Check which route table is associated
aws ec2 describe-route-tables \
  --filters Name=association.subnet-id,Values=subnet-12345
```

---

## 🧠 Think About This

A subtle but common mistake: teams run EKS in `us-east-1a` private subnet with a `/24` CIDR (251 IPs). After scaling to 10 nodes × 29 Pods each = 290 Pods plus 10 node IPs = 300 IPs needed but only 251 available. The cluster can't schedule Pods despite nodes having available CPU/memory - the bottleneck is IP address exhaustion. IP exhaustion in AWS VPC is hard to debug because the error message often surfaces as "insufficient resources" rather than clearly stating "no IPs available." Plan your subnet sizes up front: `/21` (2,046 IPs) for EKS worker subnets is a safe starting point for medium-sized clusters. For large clusters, use VPC CNI prefix delegation which dramatically increases Pod density per node.
