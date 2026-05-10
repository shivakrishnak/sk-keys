---
version: 1
layout: default
title: "VPC"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /cloud-aws/vpc/
id: AWS-054
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on:
  ["Region / AZ / Edge Location", "IAM (Identity and Access Management)"]
used_by:
  [
    "Subnets (Public / Private)",
    "Security Groups",
    "NACLs",
    "Internet Gateway / NAT Gateway",
    "VPC Peering",
    "Transit Gateway",
    "EKS",
    "RDS",
  ]
related:
  [
    "Subnets (Public / Private)",
    "Security Groups",
    "NACLs",
    "Internet Gateway / NAT Gateway",
    "VPC Peering",
    "Transit Gateway",
  ]
tags: [aws, vpc, networking, virtual-private-cloud, security, isolation, cloud]
---

# VPC

## ⚡ TL;DR

A **VPC (Virtual Private Cloud)** is your private, isolated network section in AWS. You define the IP address range (CIDR), create subnets (across AZs), control traffic with Security Groups and NACLs, and connect to the internet or other networks as needed. Every AWS account comes with a default VPC. Production: always use custom VPCs. Think of VPC as your virtual data center network.

---

## 🔥 Problem This Solves

Without VPC: all AWS resources share the same flat network - any resource can reach any other, no isolation. VPC provides network isolation: your EC2 instances, RDS databases, and Lambda functions live in your private network. You control all routing, firewall rules, and connectivity.

---

## 📘 Textbook Definition

Amazon Virtual Private Cloud (VPC) is a logically isolated virtual network within the AWS cloud where you can launch AWS resources. You have complete control over the virtual networking environment, including IP address range selection, subnet creation, route table configuration, and network gateways.

---

## ⏱️ 30 Seconds

```
VPC: defines IP range (e.g., 10.0.0.0/16 = 65,536 IPs)
  ├── Subnet (AZ 1a): 10.0.1.0/24 (public - has IGW route)
  ├── Subnet (AZ 1a): 10.0.2.0/24 (private - has NAT route)
  ├── Subnet (AZ 1b): 10.0.3.0/24 (public)
  ├── Subnet (AZ 1b): 10.0.4.0/24 (private)
  ├── Internet Gateway: public internet access
  ├── NAT Gateway: outbound internet for private subnets
  ├── Route Tables: control where traffic goes
  ├── Security Groups: stateful firewall (instance level)
  └── NACLs: stateless firewall (subnet level)
```

---

## 🔩 First Principles

- **CIDR block**: defines IP range; plan carefully (can't shrink; overlap causes peering issues)
- **Subnets are AZ-specific**: one subnet = one AZ; span multiple AZs with multiple subnets
- **Internet access**: public subnet = IGW route; private subnet = NAT Gateway for outbound only
- **Default VPC**: created automatically per region; subnets in all AZs; production: use custom
- **Security is additive**: Security Group (allow list) + NACL (allow/deny, subnet-level)
- **Routing**: route tables determine where traffic goes; longest prefix match wins

---

## 🧪 Thought Experiment

Your VPC is 10.0.0.0/16. You create a public subnet 10.0.1.0/24 (web servers) and private subnet 10.0.2.0/24 (databases). Web server has public IP → reachable from internet via IGW. Database has no public IP, no IGW route → unreachable from internet. Database needs software updates: NAT Gateway in public subnet → private subnet route table sends 0.0.0.0/0 to NAT → outbound internet works, inbound blocked.

---

## 🧠 Mental Model / Analogy

VPC is your **private office building**:

- **CIDR block**: the building's IP address range (address numbers for all rooms)
- **Public subnet**: lobby/reception (accessible from outside)
- **Private subnet**: secure inner offices (no public access)
- **Internet Gateway**: front door to the street
- **NAT Gateway**: staff door for outgoing mail only (internal staff can send mail but strangers can't walk in)
- **Security Groups**: individual office door locks
- **NACLs**: security guards at the floor entrance (check everyone entering/leaving)

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create a VPC with public subnets (web tier) and private subnets (DB tier). Attach Internet Gateway for public access. Use Security Groups to control port access.

**Level 2 - Practitioner**: NAT Gateway per AZ (one NAT Gateway = single AZ failure point). Route tables per subnet group. VPC Flow Logs for network audit. Enable DNS resolution (`enableDnsSupport`, `enableDnsHostnames`).

**Level 3 - Advanced**: VPC peering: connect two VPCs (same or cross-account/region). Transit Gateway: hub-and-spoke for many VPCs. PrivateLink: expose services privately without peering. VPC endpoints: access AWS services (S3, DynamoDB) without internet. IPAM: manage IP address space across org.

**Level 4 - Expert**: IP planning: allocate non-overlapping CIDRs across VPCs at org level (critical for peering/TGW). `/16` per VPC, `/24` per subnet is common. Avoid RFC 1918 overlap with on-prem. Intra-VPC routing: traffic between AZs costs $0.01/GB - co-locate high-volume communicating services in same AZ. Gateway VPC Endpoint: free (no data charge) private route to S3 and DynamoDB. PrivateLink: TCP-level private connectivity exposing a service NLB to consumers without full VPC access.

---

## ⚙️ How It Works

### VPC with Public/Private Subnets (Terraform)

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "production-vpc" }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

# Public Subnets (web tier)
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = { Name = "public-us-east-1a" }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags = { Name = "public-us-east-1b" }
}

# Private Subnets (app/db tier)
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"
  tags = { Name = "private-us-east-1a" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-1b"
  tags = { Name = "private-us-east-1b" }
}

# NAT Gateway (one per AZ for HA)
resource "aws_eip" "nat_a" { domain = "vpc" }
resource "aws_nat_gateway" "nat_a" {
  allocation_id = aws_eip.nat_a.id
  subnet_id     = aws_subnet.public_a.id
}

resource "aws_eip" "nat_b" { domain = "vpc" }
resource "aws_nat_gateway" "nat_b" {
  allocation_id = aws_eip.nat_b.id
  subnet_id     = aws_subnet.public_b.id
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table" "private_a" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_a.id  # AZ-local NAT
  }
}

# Associate subnets with route tables
resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private_a.id
}
```

### VPC Gateway Endpoint (Free S3 Access)

```hcl
# Access S3 from private subnet WITHOUT internet (free!)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-east-1.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.private_a.id,
    aws_route_table.private_b.id
  ]
}
```

### VPC Flow Logs

```hcl
# Log all VPC traffic to CloudWatch
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"   # ACCEPT, REJECT, or ALL
  vpc_id          = aws_vpc.main.id
}
```

---

## 🔄 E2E Flow: HTTP Request Through VPC

```
Browser → www.myapp.com

1. Route53: resolves to ALB DNS name
2. ALB: lives in public subnets (10.0.1.0/24 + 10.0.2.0/24)
   - ALB Security Group: allows 443 from 0.0.0.0/0

3. ALB → EC2 in private subnet (10.0.3.0/24)
   - EC2 Security Group: allows 8080 from ALB Security Group

4. EC2 → RDS (10.0.5.0/24, private subnet)
   - RDS Security Group: allows 5432 from EC2 Security Group

5. EC2 needs to call external API:
   - Route table: 0.0.0.0/0 → NAT Gateway (10.0.1.x)
   - NAT Gateway → Internet Gateway → external API
   - Response returns via same path

Traffic from internet never directly reaches EC2 or RDS.
```

---

## ⚖️ Comparison Table

|                 | Default VPC           | Custom VPC   |
| --------------- | --------------------- | ------------ |
| **Created by**  | AWS automatically     | You          |
| **Subnets**     | All public (1 per AZ) | You design   |
| **IGW**         | Attached              | Add manually |
| **Use case**    | Dev/testing           | Production   |
| **CIDR**        | 172.31.0.0/16         | Your choice  |
| **Recommended** | No (for prod)         | Yes          |

---

## ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                           |
| --------------------------------------- | --------------------------------------------------------------------------------- |
| "Private subnet = secure automatically" | Private subnet = no public IP; still need Security Groups + NACLs                 |
| "One NAT Gateway is enough"             | One NAT = single AZ failure point for private subnet outbound traffic             |
| "VPC = free"                            | VPC is free; NAT Gateway, VPC endpoints (interface), and data transfer have costs |
| "Can expand VPC CIDR freely"            | AWS allows adding secondary CIDRs; cannot modify primary CIDR                     |

---

## 🔗 Related Keywords

- [Subnets (Public / Private)](/cloud-aws/subnets-public-private/) - subnet design in VPC
- [Security Groups](/cloud-aws/security-groups/) - instance-level firewall
- [NACLs](/cloud-aws/nacls/) - subnet-level firewall
- [Internet Gateway / NAT Gateway](/cloud-aws/internet-gateway-nat-gateway/) - internet connectivity

---

## 📌 Quick Reference Card

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# List VPCs
aws ec2 describe-vpcs

# Create subnet
aws ec2 create-subnet \
  --vpc-id vpc-12345 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a

# Create Internet Gateway + attach
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-12345 \
  --vpc-id vpc-12345

# Create route in route table
aws ec2 create-route \
  --route-table-id rtb-12345 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-12345

# Enable VPC Flow Logs
aws ec2 create-flow-logs \
  --resource-ids vpc-12345 \
  --resource-type VPC \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs
```

---

## 🧠 Think About This

The most expensive VPC mistake teams make is **NAT Gateway data charges**. NAT Gateway costs $0.045/hour + $0.045/GB of processed data. A service making heavy API calls through NAT can cost hundreds of dollars per month. Solutions: (1) Use VPC Endpoints for S3 and DynamoDB (free Gateway Endpoints eliminate NAT data charges). (2) Use PrivateLink for other AWS services. (3) Use Interface VPC Endpoints for services like ECR, SQS, SSM to eliminate NAT dependency. Teams that audit their NAT Gateway costs and replace with VPC Endpoints often see 40-70% reduction in networking costs - a quick win that doesn't require architecture changes, just adding VPC endpoints and optionally updating Security Group rules.
