---
layout: default
title: "AWS Cost Optimization"
parent: "Cloud — AWS"
nav_order: 60
permalink: /cloud-aws/aws-cost-optimization/
id: AWS-060
category: "Cloud — AWS"
difficulty: "★★★"
depends_on: ["AWS Global Infrastructure", "EC2", "S3", "RDS"]
used_by: ["Spot Instances / Reserved Instances"]
related:
  [
    "Spot Instances / Reserved Instances",
    "S3 Lifecycle Policies",
    "Auto Scaling Groups",
    "CloudWatch",
    "ECS / Fargate",
  ]
tags: [aws, cost, optimization, savings, reserved-instances, spot, cloud]
---

# AWS Cost Optimization

## ⚡ TL;DR

AWS cost optimization is systematic: **right-size** (use Compute Optimizer), **reserve** (Savings Plans/Reserved Instances for predictable workloads), **spot** (Spot Instances/Fargate Spot for fault-tolerant), **cut waste** (idle resources, unattached EBS, old snapshots, data transfer, S3 storage classes). Four pillars: right architecture, right size, right pricing model, eliminate waste. AWS Free Tier + Cost Explorer + Budgets are your starting tools.

---

## 🔥 Problem This Solves

AWS bills are opaque and grow without discipline. Teams over-provision "to be safe," forget to delete development resources, use on-demand pricing for always-on workloads, store data in Standard S3 forever. Systematic cost optimization can reduce AWS spend 30-70% without impacting reliability or performance.

---

## 📘 Textbook Definition

AWS cost optimization is the process of reducing your overall spending on AWS by right-sizing resources, selecting the appropriate pricing models, eliminating waste, and adopting cloud-native architectures. AWS provides Cost Explorer, Trusted Advisor, Compute Optimizer, and the Well-Architected Cost Optimization Pillar as guidance frameworks.

---

## ⏱️ 30 Seconds

```
Top cost drivers (typical workload):
  1. EC2 / Fargate compute        (30-50% of bill)
  2. Data transfer (out to internet, cross-AZ)  (10-20%)
  3. RDS / Aurora storage + I/O   (10-20%)
  4. S3 storage                   (5-15%)
  5. NAT Gateway                  (5-10%)

Quick wins (implement first):
  - Delete unused EC2, EBS, EIP, snapshots
  - Set S3 Intelligent-Tiering on logs/backups
  - gp2 → gp3 EBS migration (free, same cost)
  - Savings Plans (1-year, no upfront) = 30-40% savings
  - Graviton3 instances = 20-40% better price/perf
  - VPC Endpoints for S3/DynamoDB = eliminate NAT Gateway traffic
```

---

## 🔩 First Principles

- **Elasticity = pay for what you use**: auto-scale down to zero when idle (Lambda, Fargate, Aurora Serverless)
- **Pricing models**: On-Demand (most expensive, no commitment) > Savings Plans > Reserved > Spot (cheapest, interruptible)
- **Data transfer costs**: often hidden; cross-AZ ($0.01/GB), cross-region ($0.02/GB), internet egress ($0.09/GB) add up
- **Waste accumulates silently**: unattached EBS volumes, idle EIPs ($0.005/hr), old snapshots, forgotten development environments
- **Right architecture reduces cost**: serverless architectures (Lambda, Fargate Spot, Aurora Serverless) eliminate idle capacity cost

---

## 🧪 Thought Experiment

Company with $50K/month AWS bill. Audit: $15K in EC2 (50% right-sizing opportunity). $8K in data transfer (unnecessary cross-AZ traffic). $5K in RDS I/O (switch to I/O Optimized). $3K in S3 Standard (lifecycle policies). $2K in idle resources. Total reduction opportunity: ~$20K/month. After optimization: $30K/month, 40% savings, same workloads, same SLAs.

---

## 🧠 Mental Model / Analogy

AWS cost optimization is like **managing a restaurant's food cost**: (1) don't over-order ingredients (right-size), (2) buy in bulk for staples you always use (reserved/savings plans), (3) buy fresh when uncertain (on-demand), (4) use deals when available (spot), (5) use food before it expires (lifecycle policies), (6) don't leave the lights on in empty rooms (eliminate idle resources). Systematic discipline beats occasional heroics.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Enable Cost Explorer. Set up AWS Budgets with alerts. Identify top 5 cost drivers. Delete obviously unused resources (stopped EC2, unattached EBS, unused EIPs). Set S3 lifecycle rules on log buckets.

**Level 2 — Practitioner**: Compute Optimizer: view right-sizing recommendations for EC2, Lambda, ECS. Savings Plans: 1-year Compute Savings Plan = 30-40% savings, flexible across EC2/Lambda/Fargate. Graviton migration: switch m5 → m7g (ARM): 20-40% better price/performance. gp2 → gp3 EBS: free migration, decouples IOPS from size.

**Level 3 — Advanced**: Spot Instances for stateless workloads (ECS/EKS worker nodes, batch jobs): 60-90% savings. NAT Gateway optimization: VPC endpoints for S3/DynamoDB (free gateway endpoints eliminate NAT traffic). Data transfer audit: identify cross-AZ traffic, consolidate services in same AZ when possible. S3 Storage Lens: analyze object count, size, access patterns across all buckets.

**Level 4 — Expert**: FinOps practices: tagging strategy (`CostCenter`, `Project`, `Environment`, `Owner`) → cost allocation reports → team-level accountability. Chargeback/showback: AWS Cost Categories map tags to organizational units. Anomaly Detection (AWS Cost Anomaly Detection): ML-based alerts when spend deviates from expected. RDS I/O Optimized pricing: for I/O-heavy Aurora workloads (check if I/O > 25% of total Aurora bill → IO-Optimized saves money). Reserved Instances for RDS: 1-year or 3-year = 36-70% savings vs On-Demand. Cross-AZ data transfer elimination: co-locate tightly coupled services; use endpoints; use same-AZ replica for read-heavy DB workloads.

---

## ⚙️ How It Works

### Cost Optimization Playbook

```bash
# 1. Identify waste: unattached EBS volumes
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query 'Volumes[].{Id:VolumeId,Size:Size,Region:AvailabilityZone}' \
  --output table

# 2. Unattached EIPs (charged when not attached)
aws ec2 describe-addresses \
  --query 'Addresses[?AssociationId==null].{AllocationId:AllocationId,IP:PublicIp}'

# 3. Old, unneeded snapshots (running script to find candidates)
aws ec2 describe-snapshots \
  --owner-ids self \
  --query 'Snapshots[?StartTime<`2023-01-01`].{Id:SnapshotId,Date:StartTime,Size:VolumeSize}' \
  --output table

# 4. Stopped EC2 instances (still paying for EBS)
aws ec2 describe-instances \
  --filters Name=instance-state-name,Values=stopped \
  --query 'Reservations[].Instances[].{Id:InstanceId,Type:InstanceType,Stopped:StateTransitionReason}'

# 5. Find gp2 volumes (migrate to gp3)
aws ec2 describe-volumes \
  --filters Name=volume-type,Values=gp2 \
  --query 'Volumes[].{Id:VolumeId,Size:Size,IOPS:Iops}' \
  --output table

# 6. Migrate gp2 to gp3 (zero downtime)
aws ec2 modify-volume \
  --volume-id vol-xxxxxxxx \
  --volume-type gp3 \
  --iops 3000 \
  --throughput 125

# 7. Find Lambda functions with over-provisioned memory (use Lambda Power Tuning)
aws lambda list-functions \
  --query 'Functions[].{Name:FunctionName,Memory:MemorySize,Runtime:Runtime}' \
  --output table

# 8. Get Savings Plans recommendations
aws savingsplans describe-savings-plans-purchase-recommendation \
  --product-type ComputeSavingsPlans \
  --payment-option NO_UPFRONT \
  --term ONE_YEAR \
  --account-scope PAYER
```

### Savings Plans (Terraform)

```hcl
# Compute Savings Plan: 1-year, no upfront, $1000/hr commitment
resource "aws_savingsplans_savings_plan" "compute" {
  savings_plan_offer_id = "compute-savings-plan-1yr-no-upfront-id"
  # Get offer IDs via: aws savingsplans describe-savings-plans-offering-rates
  commitment            = "1000"  # $/hr
  purchase_time         = "2024-01-01T00:00:00Z"
}
```

### Tagging Strategy (Cost Allocation)

```hcl
# Required tags for all resources (enforced via SCP or AWS Config)
locals {
  required_tags = {
    Environment = var.environment      # dev/staging/prod
    Project     = var.project          # for cost allocation
    Owner       = var.team_email       # accountability
    CostCenter  = var.cost_center      # chargeback
    ManagedBy   = "terraform"
  }
}

# AWS Config rule to detect untagged resources
resource "aws_config_config_rule" "required_tags" {
  name = "required-tags"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "Project"
    tag3Key = "Owner"
    tag4Key = "CostCenter"
  })
}
```

### NAT Gateway Cost Optimization

```hcl
# Replace NAT Gateway traffic for S3/DynamoDB with VPC Endpoints (FREE)
# S3 Gateway Endpoint (free, reduces NAT Gateway charges)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-east-1.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.private_a.id,
    aws_route_table.private_b.id,
  ]
}

# DynamoDB Gateway Endpoint (free)
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.us-east-1.dynamodb"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.private_a.id,
    aws_route_table.private_b.id,
  ]
}
# These two endpoints can eliminate 30-50% of NAT Gateway data charges
# for workloads that heavily use S3 and DynamoDB
```

---

## ⚖️ Comparison Table: Pricing Models

| Model              | Commitment        | Savings vs On-Demand | Best For                     |
| ------------------ | ----------------- | -------------------- | ---------------------------- |
| On-Demand          | None              | 0%                   | Variable, unpredictable      |
| Spot               | None              | 60-90%               | Fault-tolerant, batch        |
| Savings Plan (1yr) | 1 year spend      | 30-40%               | Most predictable workloads   |
| Savings Plan (3yr) | 3 years spend     | 40-66%               | Long-term commitment         |
| Reserved (1yr)     | 1 year, specific  | 36-42%               | Fixed instance type/region   |
| Reserved (3yr)     | 3 years, specific | 56-75%               | Absolutely certain workloads |

---

## ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------ |
| "Right-sizing risks performance"             | Compute Optimizer provides confidence-based recommendations; test before production  |
| "Savings Plans require upfront payment"      | No Upfront option: pay monthly, still get 30-40% discount                            |
| "Spot Instances are unreliable"              | 90% of Spot interruptions are predictable; 2-minute warning; use for stateless/batch |
| "Cost optimization = performance compromise" | Often opposite: Graviton = 20-40% cheaper + same or better performance               |

---

## 🔗 Related Keywords

- [Spot Instances / Reserved Instances](/cloud-aws/spot-instances-reserved-instances/) — pricing models deep-dive
- [S3 Lifecycle Policies](/cloud-aws/s3-lifecycle-policies/) — storage cost optimization
- [Auto Scaling Groups](/cloud-aws/auto-scaling-groups/) — eliminate idle capacity

---

## 📌 Quick Reference Card

```bash
# View cost by service (last 30 days)
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[].{Service:Keys[0],Cost:Metrics.UnblendedCost.Amount}' \
  | sort -t'"' -k4 -n -r | head -20

# Get Trusted Advisor cost checks
aws support describe-trusted-advisor-checks \
  --language en \
  --query 'checks[?category==`cost_optimizing`].{Name:name,Id:id}'

# Get Compute Optimizer recommendations
aws compute-optimizer get-ec2-instance-recommendations \
  --query 'instanceRecommendations[?findingReasonCodes[?contains(@,`OVERPROVISIONED`)]].[instanceArn,finding]'

# Set up budget alert
aws budgets create-budget \
  --account-id 123456789 \
  --budget '{"BudgetName":"Monthly","BudgetLimit":{"Amount":"5000","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \
  --notifications-with-subscribers '[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":80},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"team@example.com"}]}]'
```

---

## 🧠 Think About This

The most common missed cost optimization is cross-AZ data transfer. AWS charges $0.01/GB for data that crosses AZ boundaries within the same region. This seems small, but for high-throughput microservices: 1TB/day cross-AZ = $10/day = $300/month. Multiply by 10 services = $3,000/month in invisible data transfer costs. Sources: application servers in AZ-a calling RDS read replica in AZ-b; ECS tasks in AZ-a writing to ElastiCache in AZ-b; cross-AZ ALB traffic. Solutions: (1) Use ALB cross-zone load balancing disabled (pay per-AZ target) or ensure app pods exist in each AZ. (2) Use AZ-local read replicas. (3) Add AZ label to service and route same-AZ where possible. (4) Use VPC Endpoints for AWS services (S3/DynamoDB gateway endpoints eliminate the traffic entirely). Check Cost Explorer with "Region" dimension → filter for "Data Transfer" service to find your hidden data transfer costs.
