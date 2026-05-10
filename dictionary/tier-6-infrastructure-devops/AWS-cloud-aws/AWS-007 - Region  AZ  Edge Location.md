---
version: 1
layout: default
title: "Region  AZ  Edge Location"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /cloud-aws/region-az-edge-location/
id: AWS-053
category: "Cloud - AWS"
difficulty: "★☆☆"
depends_on: ["AWS Global Infrastructure"]
used_by: ["VPC", "Subnets (Public / Private)", "Route 53", "ELB / ALB / NLB"]
related:
  ["AWS Global Infrastructure", "VPC", "Route 53", "Subnets (Public / Private)"]
tags:
  [aws, region, availability-zone, edge-location, cloudfront, latency, cloud]
---

# Region / AZ / Edge Location

## ⚡ TL;DR

**Region**: isolated geographic area (us-east-1). **Availability Zone (AZ)**: one or more discrete data centers in a region, isolated faults, low-latency interconnects. **Edge Location**: CloudFront CDN / Route53 DNS PoP close to end users (450+ globally). Resources in one region are not visible in another - you choose where to deploy.

---

## 🔥 Problem This Solves

Understanding these three concepts is foundational for: choosing where to deploy resources, achieving high availability (multi-AZ), serving users with low latency (Edge Locations/CloudFront), and meeting data residency requirements (Region selection).

---

## 📘 Textbook Definition

- **Region**: A geographically distinct area consisting of multiple, isolated AZs connected by high-bandwidth, low-latency networking. Regions are independent; a failure in one does not affect another.
- **Availability Zone (AZ)**: One or more discrete data centers with redundant power, networking, and connectivity in an AWS Region. AZs are engineered to be isolated from failures in other AZs.
- **Edge Location**: Points of presence (PoPs) globally for Amazon CloudFront CDN and Route53 DNS, positioned close to end users to minimize latency.

---

## ⏱️ 30 Seconds

```
REGION (e.g., eu-central-1 = Frankfurt)
  ├── AZ: eu-central-1a  ← physical data center(s)
  ├── AZ: eu-central-1b
  └── AZ: eu-central-1c

EDGE LOCATION (e.g., Frankfurt CloudFront PoP)
  → Caches objects from origin (S3/ALB) in eu-central-1
  → End users get <10ms to Edge Location vs ~50ms to region

AZ-to-AZ latency: ~1-2ms (synchronous replication feasible)
Region-to-region: 50-200ms (async replication only)
User-to-Edge:     <10ms in major cities
User-to-Region:   varies (10-200ms depending on proximity)
```

---

## 🔩 First Principles

- **AZs as fault domains**: design your architecture so N-1 AZ failure = 0 downtime
- **AZ assignment is random per account**: `us-east-1a` in your account ≠ `us-east-1a` in a colleague's account; use AZ IDs
- **Edge Locations are not EC2**: you can't run servers there; CDN cache only (unless CloudFront Functions/Lambda@Edge)
- **Most services are regional**: EC2, RDS, S3, Lambda, etc. - you deploy to a region
- **Some services are global**: IAM, Route53, CloudFront - no region selection needed

---

## 🧪 Thought Experiment

User in Singapore connects to your API in us-east-1 (Virginia): ~200ms round-trip latency. Solution 1: add ap-southeast-1 (Singapore) region → 20ms latency. Solution 2: CloudFront Edge Location in Singapore → cache your static API responses → <10ms. For dynamic content: multi-region deployment. For static/cacheable: Edge Location is faster and cheaper.

---

## 🧠 Mental Model / Analogy

- **Region** = a country office (completely independent, manages its own resources)
- **AZ** = separate building in the same city (different utility grids, nearby)
- **Edge Location** = a courier's local pickup station (close to customers, receives packages from the country office for fast last-mile delivery)

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Always deploy across at least 2 AZs. Use CloudFront (Edge Locations) for static websites and assets. Choose a Region close to your users.

**Level 2 - Practitioner**: Multi-AZ: ALB spans AZs automatically. RDS Multi-AZ: sync replication → automatic failover. Auto Scaling Group: distribute instances across AZs. EKS: nodes spread across AZs with TopologySpreadConstraint.

**Level 3 - Advanced**: Regional Services vs Global Services. Cross-region replication for DR: S3 CRR (Cross-Region Replication), RDS read replica in another region. Route53 latency-based routing: sends users to nearest region automatically.

**Level 4 - Expert**: Local Zones: AZ-like extension for sub-10ms in specific metros (LA, NYC, Chicago, Dallas). AWS Wavelength: compute at 5G carrier edge for <1ms (Verizon, T-Mobile zones). AZ IDs: `use1-az1`, `use1-az2` - consistent naming across accounts. PrivateLink: private connectivity between VPCs across AZs without internet traversal. Direct Connect: dedicated network connection from on-premises to a Region.

---

## ⚙️ How It Works

### Service Scope Reference

```
Global (no region):
  IAM, Route53, CloudFront, AWS Organizations, WAF (global)

Regional:
  EC2, ECS, EKS, Lambda, RDS, DynamoDB, S3 (data in region),
  SQS, SNS, ALB, VPC, ElastiCache, Kinesis, API Gateway

AZ-scoped:
  EC2 instance, EBS volume, Subnet, NAT Gateway, RDS instance

  Note: EBS volume must be in same AZ as EC2 instance
  Note: NAT Gateway per AZ (don't share across AZs = single point of failure)
```

### Multi-AZ Best Practices

```yaml
# EC2 Auto Scaling: force AZ distribution
resource "aws_autoscaling_group" "web" {
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  # Or better: use subnets (each subnet is in one AZ)
  vpc_zone_identifier = [
    aws_subnet.private_a.id,  # us-east-1a
    aws_subnet.private_b.id,  # us-east-1b
    aws_subnet.private_c.id   # us-east-1c
  ]
}

# RDS: Multi-AZ = synchronous standby in different AZ
resource "aws_db_instance" "main" {
  multi_az = true  # enables standby in another AZ
  # automatic failover in ~60-120s
}

# ElastiCache: Multi-AZ replication group
resource "aws_elasticache_replication_group" "main" {
  num_cache_clusters = 3  # spread across AZs
  multi_az_enabled   = true
}
```

### Edge Location: CloudFront Configuration

```yaml
# CloudFront distribution with regional origin
resource "aws_cloudfront_distribution" "web" {
  origin {
    domain_name = aws_alb.main.dns_name
    origin_id   = "alb-origin"
  }

  # Cache behavior
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    min_ttl     = 0
    default_ttl = 86400    # 1 day
    max_ttl     = 31536000 # 1 year
  }

  price_class = "PriceClass_All"  # use all Edge Locations globally
}
```

---

## ⚖️ Comparison Table

| Level             | What                    | Failure Domain | Count          |
| ----------------- | ----------------------- | -------------- | -------------- |
| **Edge Location** | CDN PoP                 | Individual PoP | 450+           |
| **Local Zone**    | AZ-like metro extension | Local Zone     | 30+            |
| **AZ**            | Data center cluster     | AZ             | 2-6 per Region |
| **Region**        | Geographic area         | Region         | 33+            |

---

## ⚠️ Common Misconceptions

| Misconception              | Reality                                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| "AZ = single data center"  | AZ = one or more DCs; AWS doesn't disclose exact DC count                                                        |
| "Edge Locations = compute" | Edge = CDN cache; Lambda@Edge/CloudFront Functions add compute                                                   |
| "Multi-AZ costs 2x"        | Multi-AZ adds cost for redundant resources, but data transfer within a region between AZs is not free ($0.01/GB) |
| "S3 is in one AZ"          | S3 automatically replicates data across ≥3 AZs within a region                                                   |

---

## 🔗 Related Keywords

- [AWS Global Infrastructure](/cloud-aws/aws-global-infrastructure/) - the full picture
- [VPC](/cloud-aws/vpc/) - networking within a region, subnets within AZs
- [Route 53](/cloud-aws/route-53/) - uses Edge Locations for DNS + latency routing

---

## 📌 Quick Reference Card

```bash
# AZs in us-east-1
aws ec2 describe-availability-zones --region us-east-1 \
  --query 'AvailabilityZones[].{Name:ZoneName,ID:ZoneId,State:State}'

# Local Zones
aws ec2 describe-availability-zones --region us-east-1 \
  --filters Name=zone-type,Values=local-zone

# CloudFront edge locations count
# (Cannot query via CLI; see: https://aws.amazon.com/cloudfront/features/)

# Check which AZ an EC2 instance is in
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 \
  --query 'Reservations[].Instances[].Placement.AvailabilityZone'

# Nearest region latency test
# https://cloudping.info - browser-based latency test to all AWS regions
```

---

## 🧠 Think About This

The `us-east-1` AZ name shuffle between AWS accounts exists because AWS wants to spread load evenly across physical data centers - if everyone chose AZ "a", one data center would be overloaded. When building multi-account architectures (AWS Organizations), always use AZ IDs (`use1-az1`) to ensure you're talking about the same physical facility. This matters when you're doing cross-account VPC peering, Direct Connect, or capacity planning across accounts. Additionally, note that AWS Regions don't release all services simultaneously - `us-east-1` and `us-west-2` typically get new services months before other regions. If you need cutting-edge services, you may need to design your architecture around availability in specific regions.
