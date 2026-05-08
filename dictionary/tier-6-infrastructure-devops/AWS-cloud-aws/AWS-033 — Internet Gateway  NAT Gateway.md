---
layout: default
title: "Internet Gateway  NAT Gateway"
parent: "Cloud — AWS"
nav_order: 33
permalink: /cloud-aws/internet-gateway-nat-gateway/
id: AWS-033
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on: ["VPC", "Subnets (Public / Private)"]
used_by: ["Security Groups", "NACLs", "EKS", "EC2", "Lambda"]
related:
  [
    "VPC",
    "Subnets (Public / Private)",
    "Security Groups",
    "VPC Peering",
    "Transit Gateway",
  ]
tags: [aws, internet-gateway, nat-gateway, networking, vpc, egress, cloud]
---

# Internet Gateway / NAT Gateway

## ⚡ TL;DR

**Internet Gateway (IGW)**: one per VPC; enables bidirectional internet access for resources with public IPs. **NAT Gateway**: managed service in public subnet; enables outbound-only internet for private subnet resources (no inbound). NAT Gateway: $0.045/hr + $0.045/GB processed — one per AZ for HA. For production: private subnets + NAT Gateway for most resources; public subnets + IGW for load balancers only.

---

## 🔥 Problem This Solves

Private subnet resources need to download software updates, call external APIs, pull container images — but should not be directly reachable from the internet. NAT Gateway solves this: outbound internet works, no inbound connections possible.

---

## 📘 Textbook Definition

**Internet Gateway (IGW)**: A horizontally scaled, redundant, highly available VPC component that allows communication between resources in a VPC and the internet. It performs NAT for resources with public IPv4 addresses.
**NAT Gateway**: A managed network address translation service that enables instances in a private subnet to initiate outbound connections to the internet while preventing inbound connections from the internet.

---

## ⏱️ 30 Seconds

```
Internet Gateway (IGW):
  - Attached to VPC (one per VPC)
  - Enables INBOUND + OUTBOUND internet
  - Resource must have public IP or EIP
  - Public subnet: route 0.0.0.0/0 → IGW
  - Free (no hourly charge, but data transfer costs)

NAT Gateway:
  - Deployed in PUBLIC subnet
  - Enables OUTBOUND internet for PRIVATE subnet
  - No inbound connections possible
  - Cost: $0.045/hr (~$32/mo) + $0.045/GB
  - One NAT GW per AZ (HA)
  - Private subnet route: 0.0.0.0/0 → NAT GW
```

---

## 🔩 First Principles

- **IGW = two-way door**: public IP required on resource; bidirectional internet
- **NAT = one-way valve**: private resources go out; internet can't come in; IGW is behind NAT GW
- **NAT GW has Elastic IP**: its public IP for outbound connections; fixed IP for whitelisting
- **NAT GW is AZ-specific**: deploy one per AZ; cross-AZ traffic = extra cost + AZ dependency
- **NAT GW is managed**: AWS handles scaling, redundancy; no EC2 management
- **Egress-Only IGW**: for IPv6 (stateful, outbound-only for IPv6; NAT GW doesn't support IPv6)

---

## 🧪 Thought Experiment

EKS node in private subnet needs to pull container image from ECR. Without NAT Gateway: no route to internet → image pull fails. With NAT Gateway: node sends request → private subnet route table → NAT Gateway (in public subnet) → IGW → ECR. Response flows back same path. Node stays unreachable from internet. Alternatively: VPC Endpoint for ECR eliminates NAT Gateway dependency (cheaper for high-volume pulls).

---

## 🧠 Mental Model / Analogy

Think of a private office complex: **Internet Gateway = the main public entrance** (visitors and employees can use it). **NAT Gateway = the employees-only back door**: employees can go out (outbound internet), but the door only opens from inside — delivery people (internet) can't use it. NAT Gateway has a registered return address (Elastic IP) so replies know where to go back.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Public subnets need IGW in route table. Private subnets need NAT Gateway in route table for outbound internet. Deploy NAT Gateway in public subnet with EIP.

**Level 2 — Practitioner**: One NAT GW per AZ for HA. Private route tables use AZ-local NAT GW. Use VPC Endpoints for S3 and DynamoDB to avoid NAT GW charges. Monitor NAT GW CloudWatch metrics: `ErrorPortAllocation`, `PacketsDropCount`.

**Level 3 — Advanced**: NAT Gateway limits: 55,000 simultaneous connections per destination IP. If Lambda or ECS scales massively → port exhaustion. Solution: multiple NAT Gateways, or VPC endpoints. Cost reduction: replace NAT with Interface VPC Endpoints for AWS services (ECR, SQS, SSM, etc.). NAT Gateway: 45 Gbps bandwidth (was 10 Gbps before 2022 upgrade).

**Level 4 — Expert**: Egress-only Internet Gateway: IGW for IPv6 outbound only (IPv6 doesn't do NAT natively — all addresses are public, but EIGW prevents inbound). NAT Instance (legacy): EC2 instance performing NAT; cheaper but requires management, not HA. Gateway Load Balancer: transparently insert security appliances in traffic path. VPC endpoints save money but require updating app configs to use private DNS. PrivateLink cost: ~$0.01/hr per endpoint + $0.01/GB — still cheaper than NAT for high-volume same-region AWS service calls.

---

## ⚙️ How It Works

### IGW + NAT Gateway Setup (Terraform)

```hcl
# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "main-igw" }
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat_a" {
  domain = "vpc"
  depends_on = [aws_internet_gateway.main]  # EIP requires IGW first
}

resource "aws_eip" "nat_b" {
  domain = "vpc"
  depends_on = [aws_internet_gateway.main]
}

# NAT Gateways — one per AZ in public subnets
resource "aws_nat_gateway" "a" {
  allocation_id = aws_eip.nat_a.id
  subnet_id     = aws_subnet.public_a.id  # public subnet!
  tags          = { Name = "nat-us-east-1a" }
}

resource "aws_nat_gateway" "b" {
  allocation_id = aws_eip.nat_b.id
  subnet_id     = aws_subnet.public_b.id
  tags          = { Name = "nat-us-east-1b" }
}

# Route table for PUBLIC subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

# Route table for PRIVATE subnet in AZ a
resource "aws_route_table" "private_a" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.a.id  # AZ-local NAT
  }
}

# Route table for PRIVATE subnet in AZ b
resource "aws_route_table" "private_b" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.b.id  # AZ-local NAT
  }
}

# Associate route tables with subnets
resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private_a.id
}
```

### Cost Optimization: VPC Endpoints vs NAT Gateway

```bash
# Scenario: EKS cluster pulling from ECR via NAT Gateway
# 100 pods × 1GB image = 100GB/day × 30 days = 3TB/month
# NAT cost: 3000 GB × $0.045 = $135/month just for ECR pulls

# Solution: Interface VPC Endpoint for ECR
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.us-east-1.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_group_ids  = [aws_security_group.vpc_endpoint.id]
  private_dns_enabled = true  # ECR DNS → private endpoint
}

resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.us-east-1.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_group_ids  = [aws_security_group.vpc_endpoint.id]
  private_dns_enabled = true
}

# ECR Interface endpoint cost: $0.01/hr × 2 AZs + $0.01/GB
# Monthly: ~$15 + $30 (3TB) = $45 vs $135 via NAT
# Savings: $90/month (~67% reduction for ECR traffic)
```

### Traffic Flow Diagram

```
OUTBOUND from private EC2:
  EC2 (10.0.3.5) → route 0.0.0.0/0 → NAT GW (10.0.1.10)
  → NAT GW translates src IP to EIP (52.1.2.3)
  → IGW → Internet (api.example.com)
  ← Response to 52.1.2.3 → IGW → NAT GW (translates back to 10.0.3.5)
  ← EC2 receives response

INBOUND to public EC2 (with EIP):
  Internet → IGW
  → Route to public subnet
  → ALB (if ALB, or directly to EC2 EIP)
  → Security Group check
  → EC2

Private EC2 from Internet: IMPOSSIBLE
  Internet → IGW → route to private subnet?
  No route to private subnet from IGW → drops
```

---

## ⚖️ Comparison Table

|               | Internet Gateway        | NAT Gateway             | VPC Endpoint        |
| ------------- | ----------------------- | ----------------------- | ------------------- |
| **Direction** | Both                    | Outbound only           | Service-specific    |
| **Cost**      | Free                    | $32/mo + $0.045/GB      | $7-15/mo + $0.01/GB |
| **HA**        | Built-in                | Per-AZ                  | Built-in            |
| **IP type**   | Public IP required      | Private subnet          | Private only        |
| **Use case**  | Public-facing resources | Private subnet internet | AWS service access  |

---

## ⚠️ Common Misconceptions

| Misconception                  | Reality                                                                 |
| ------------------------------ | ----------------------------------------------------------------------- |
| "One NAT Gateway is enough"    | One NAT = AZ dependency; private subnets in other AZs need AZ-local NAT |
| "NAT Gateway = free like IGW"  | $0.045/hr = ~$32/month minimum plus data charges                        |
| "Private subnet = no internet" | Private + NAT GW = outbound internet works; just no inbound             |
| "NAT Gateway handles IPv6"     | NAT Gateway is IPv4 only; use Egress-Only IGW for IPv6                  |

---

## 🔗 Related Keywords

- [VPC](/cloud-aws/vpc/) — NAT GW and IGW are VPC components
- [Subnets (Public / Private)](/cloud-aws/subnets-public-private/) — IGW in public, NAT GW for private
- [VPC Peering](/cloud-aws/vpc-peering/) — alternative to internet for VPC-to-VPC
- [Transit Gateway](/cloud-aws/transit-gateway/) — hub for multiple VPCs without internet

---

## 📌 Quick Reference Card

```bash
# Create Internet Gateway and attach to VPC
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --igw-id igw-12345 --vpc-id vpc-12345

# Create EIP for NAT
aws ec2 allocate-address --domain vpc

# Create NAT Gateway
aws ec2 create-nat-gateway \
  --subnet-id subnet-public-a \
  --allocation-id eipalloc-12345

# Check NAT Gateway status
aws ec2 describe-nat-gateways \
  --filter Name=vpc-id,Values=vpc-12345

# Add NAT route to private route table
aws ec2 create-route \
  --route-table-id rtb-private-a \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id nat-12345

# Monitor NAT Gateway errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/NATGateway \
  --metric-name ErrorPortAllocation \
  --dimensions Name=NatGatewayId,Value=nat-12345 \
  --start-time 2024-01-01T00:00:00 \
  --end-time 2024-01-02T00:00:00 \
  --period 3600 \
  --statistics Sum
```

---

## 🧠 Think About This

NAT Gateway billing surprises are one of the most common AWS cost complaints. Teams set up `0.0.0.0/0 → NAT Gateway` in private subnet route tables and forget about it. Every S3 GetObject, every ECR image pull, every SQS message, every API call to AWS services flows through NAT — at $0.045/GB each way. The remedy is systematic VPC endpoint adoption. Start with S3 and DynamoDB (free Gateway endpoints, zero data charge, zero config change for most apps). Then add Interface endpoints for ECR, SQS, SNS, SSM, and Secrets Manager. The VPC endpoint hourly cost ($0.01/hr ≈ $7/mo per endpoint per AZ) is typically recovered in the first day of eliminated NAT Gateway data charges for busy services. Run this analysis monthly: `aws ce get-cost-and-usage` filtered to `NatGateway` and `VpcEndpoint` to see your savings opportunity.
