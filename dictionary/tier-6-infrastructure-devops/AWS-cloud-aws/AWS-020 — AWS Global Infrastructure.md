---
layout: default
title: "AWS Global Infrastructure"
parent: "Cloud — AWS"
nav_order: 20
permalink: /cloud-aws/aws-global-infrastructure/
number: "AWS-020"
category: "Cloud — AWS"
difficulty: "★☆☆"
depends_on: []
used_by: ["Region / AZ / Edge Location", "VPC", "Route 53"]
related:
  ["Region / AZ / Edge Location", "VPC", "Route 53", "AWS Service Limits"]
tags: [aws, infrastructure, global, regions, availability-zones, edge, cloud]
---

# AWS Global Infrastructure

## ⚡ TL;DR

AWS operates **33+ Regions**, each with 2-6 **Availability Zones** (isolated data centers), plus **450+ Edge Locations** (CloudFront CDN + Route53 DNS). Regions are fully independent (separate electricity, cooling, physical security). AZs within a region are connected by low-latency fiber (<2ms). Your workload's resilience, data sovereignty, and latency are determined by which regions and AZs you choose.

---

## 🔥 Problem This Solves

Global applications need: low latency to users worldwide, resilience to data center failures, compliance with data sovereignty requirements (GDPR: EU data must stay in EU), and disaster recovery across failure domains. AWS's global infrastructure provides the building blocks.

---

## 📘 Textbook Definition

AWS Global Infrastructure is the worldwide network of AWS physical data center facilities organized into Regions (geographic areas containing multiple AZs), Availability Zones (isolated data centers with independent power/cooling/networking), Edge Locations (CDN/DNS points of presence), and Local Zones (metro area extensions for ultra-low latency).

---

## ⏱️ 30 Seconds

```
Region:           Geographic area (us-east-1 = N. Virginia)
  ├── AZ a:       us-east-1a (one or more data centers)
  ├── AZ b:       us-east-1b
  ├── AZ c:       us-east-1c
  └── AZ d:       us-east-1d (some regions have 6 AZs)

Edge Location:    CloudFront CDN pop (450+ globally)
Local Zone:       AWS infrastructure in metro areas (e.g., LA, NYC)
Outpost:          AWS hardware in YOUR data center

Data: us-east-1 data does NOT replicate to eu-west-1 automatically
Latency: AZ-to-AZ within region: ~1-2ms
         Region-to-region: 30-200ms
```

---

## 🔩 First Principles

- **Region independence**: failure in one region doesn't affect others
- **AZ isolation**: separate power, cooling, network, and physical security
- **AZ proximity**: <2ms latency within a region; high-bandwidth fiber
- **Data residency**: your data stays in the region you deploy to
- **SLAs**: AWS commits to 99.99% availability for multi-AZ deployments

---

## 🧪 Thought Experiment

Your app is deployed only in us-east-1a. AWS data center maintenance takes down the AZ → your app is down. Solution: deploy in 3 AZs with ALB + Auto Scaling → N-1 AZ failure tolerance. For disaster recovery across regions: deploy in us-east-1 AND eu-west-1 → survive entire region failure.

---

## 🧠 Mental Model / Analogy

Think of AWS as a global franchise network: **Regions** = country offices (independent management), **AZs** = separate buildings within the same city (connected but isolated), **Edge Locations** = local delivery stations (close to customers for fast delivery/CDN), **Outposts** = the franchise bringing their equipment to your location.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Choose a region close to your users. Deploy across at least 2 AZs for resilience. Use CloudFront (Edge Locations) for static content caching.

**Level 2 — Practitioner**: Multi-AZ deployments are the AWS resilience baseline. Use RDS Multi-AZ, ALB (spans AZs), Auto Scaling Groups across AZs. Most AWS managed services are regional and multi-AZ by default.

**Level 3 — Advanced**: Multi-region architecture for disaster recovery (Route53 health checks + failover) or active-active (Route53 latency routing + global tables in DynamoDB). Global Accelerator: routes via AWS backbone to nearest healthy region endpoint. CloudFront: global CDN with 450+ PoPs.

**Level 4 — Expert**: AZ ID vs AZ Name: AZ names (us-east-1a) differ across accounts — use AZ ID (use1-az1) for cross-account coordination. Local Zones: sub-10ms latency for specific metros; launch edge compute in LA, Chicago, etc. Wavelength Zones: AWS compute at telecom 5G tower for <1ms latency. AWS Outposts: AWS rack in your data center for regulatory/latency requirements.

---

## ⚙️ How It Works

### Region Selection Criteria

```
1. Proximity to users:       latency matters for interactive apps
2. Data sovereignty:         GDPR, HIPAA, data residency laws
3. Service availability:     not all services in all regions
4. Disaster recovery:        use paired regions (us-east-1 ↔ us-west-2)
5. Price:                    us-east-1 is typically cheapest
```

### Multi-AZ Architecture

```yaml
# Typical multi-AZ web tier
VPC (us-east-1):
  us-east-1a:
    Public Subnet: NAT Gateway, ALB node
    Private Subnet: EC2 App Servers, RDS Primary

  us-east-1b:
    Public Subnet: ALB node
    Private Subnet: EC2 App Servers, RDS Standby (Multi-AZ)

  us-east-1c:
    Public Subnet: ALB node
    Private Subnet: EC2 App Servers

ALB: spans all 3 AZs → health checks → routes to healthy instances
RDS Multi-AZ: synchronous replication → automatic failover <60s
```

### AWS Regions Reference

```
Americas:
  us-east-1:    N. Virginia (most services launch here first)
  us-east-2:    Ohio
  us-west-1:    N. California
  us-west-2:    Oregon
  ca-central-1: Canada

Europe:
  eu-west-1:    Ireland
  eu-west-2:    London
  eu-central-1: Frankfurt (popular for GDPR compliance)
  eu-north-1:   Stockholm

Asia Pacific:
  ap-southeast-1: Singapore
  ap-northeast-1: Tokyo
  ap-south-1:     Mumbai
  ap-southeast-2: Sydney
```

---

## ⚖️ Comparison Table

|                | Single AZ | Multi-AZ          | Multi-Region              |
| -------------- | --------- | ----------------- | ------------------------- |
| **Resilience** | Low       | High              | Highest                   |
| **Latency**    | Lowest    | Low               | Adds cross-region latency |
| **Cost**       | Baseline  | ~2x data transfer | ~3x+                      |
| **Use case**   | Dev/test  | Production        | DR / global users         |
| **RTO**        | N/A       | Minutes           | Minutes-Hours             |
| **RPO**        | N/A       | Seconds           | Minutes                   |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                             |
| ---------------------------------------- | ----------------------------------------------------------------------------------- |
| "AZ = one data center"                   | AZs may contain multiple data centers; they're isolated fault domains               |
| "Multi-AZ = multi-region"                | Multi-AZ is within a single region; multi-region requires separate VPCs/deployments |
| "AWS handles DR automatically"           | AWS manages infrastructure HA; app-level DR is your responsibility                  |
| "us-east-1a is the same across accounts" | AZ names are shuffled per account; use AZ IDs for cross-account comparisons         |

---

## 🔗 Related Keywords

- [Region / AZ / Edge Location](/cloud-aws/region-az-edge-location/) — detailed breakdown
- [VPC](/cloud-aws/vpc/) — network isolation within a region
- [Route 53](/cloud-aws/route-53/) — global DNS leveraging Edge Locations

---

## 📌 Quick Reference Card

```bash
# List available regions
aws ec2 describe-regions --output table

# List AZs in a region
aws ec2 describe-availability-zones \
  --region us-east-1 \
  --output table

# Get AZ IDs (account-independent)
aws ec2 describe-availability-zones \
  --region us-east-1 \
  --query 'AvailabilityZones[].{Name:ZoneName,ID:ZoneId}' \
  --output table

# Check service availability in a region
aws ssm get-parameters-by-path \
  --path /aws/service/global-infrastructure/services/ec2/regions
```

---

## 🧠 Think About This

The choice of Region is often treated as a one-time decision, but it has long-term implications: data egress costs between regions add up quickly, and migrating data across regions is expensive and operationally complex. The two most impactful architecture decisions for global AWS deployments are: (1) which regions to operate in (and the data replication strategy between them), and (2) whether to use a CDN (CloudFront) to serve content from edge locations close to users rather than from origin regions. For most applications, CloudFront's 450+ PoPs provide better perceived performance improvements than multi-region infrastructure at a fraction of the cost.
