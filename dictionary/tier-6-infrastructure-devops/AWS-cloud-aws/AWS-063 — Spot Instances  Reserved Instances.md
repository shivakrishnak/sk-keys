---
layout: default
title: "Spot Instances  Reserved Instances"
parent: "Cloud — AWS"
grand_parent: "Technical Dictionary"
nav_order: 63
permalink: /cloud-aws/spot-instances-reserved-instances/
id: AWS-063
category: "Cloud — AWS"
difficulty: "★★★"
depends_on: ["EC2", "Auto Scaling Groups", "ECS / Fargate"]
used_by: ["AWS Cost Optimization"]
related:
  ["AWS Cost Optimization", "Auto Scaling Groups", "ECS / Fargate", "EKS"]
tags: [aws, spot, reserved, ec2, cost, pricing, savings-plans, cloud]
---

# Spot Instances / Reserved Instances

## ⚡ TL;DR

**Spot Instances**: up to 90% cheaper than On-Demand; AWS can interrupt with 2-minute notice when capacity needed; best for stateless, fault-tolerant, interruptible workloads (batch jobs, ECS worker nodes, EKS worker nodes). **Reserved Instances (RIs)**: 1 or 3 year commitment for specific instance type/region; 36-75% savings. **Savings Plans** (preferred over RIs): flexible commitment in $/hr; applies to EC2+Lambda+Fargate; 30-66% savings. Mix all three for maximum savings.

---

## 🔥 Problem This Solves

On-Demand pricing is expensive for predictable or fault-tolerant workloads. Teams that run everything On-Demand overpay by 40-70%. AWS provides multiple pricing models to match spending to workload characteristics: commit for predictable → Reserved/Savings Plans; risk interruption for fault-tolerant → Spot; variable → On-Demand.

---

## 📘 Textbook Definition

**Spot Instances** are spare AWS EC2 capacity offered at significant discount with the possibility of interruption. **Reserved Instances** are 1- or 3-year billing commitments for specific instance configurations. **Savings Plans** are flexible commitment-based pricing ($/hr) that apply across multiple services and instance types without the inflexibility of traditional Reserved Instances.

---

## ⏱️ 30 Seconds

```
Spot Instances:
  - Price: 60-90% below On-Demand
  - Risk: 2-minute interruption notice when AWS needs capacity
  - Best for: batch processing, CI/CD workers, ECS/EKS worker nodes
  - Key pattern: Spot + On-Demand fallback; diversify instance types

Reserved Instances:
  - Commitment: 1 or 3 years, specific instance type + region
  - Savings: 36% (1yr no-upfront) to 75% (3yr all-upfront)
  - Types: Standard (fixed, cannot change) / Convertible (flexible)

Savings Plans (preferred over RIs):
  - Commit to $/hr spend (e.g., $1.00/hr)
  - Applies to: EC2, Lambda, Fargate (Compute Savings Plan)
  - Savings: 30-66% vs On-Demand
  - Flexibility: automatically applies to any instance family/region
```

---

## 🔩 First Principles

- **AWS capacity markets**: Spot Instances expose unused AWS capacity at variable market price; when AWS needs the capacity back (scaling burst), your instance gets interrupted
- **Interruption frequency**: historically 5-15% of Spot instances see interruption in a given month; varies hugely by instance type, AZ, and time
- **Diversification**: bid on multiple instance types + multiple AZs → lower interruption risk; Spot Fleet and Auto Scaling do this automatically
- **Stateless is Spot-friendly**: if an instance is lost without data loss or user impact, it's a Spot candidate
- **Savings Plans flexibility vs RI specificity**: Savings Plans can shift to any instance type that needs it; RIs apply to specific instance type (Standard) or allow family changes (Convertible)

---

## 🧪 Thought Experiment

Data pipeline running nightly: 1,000 vCPUs for 4 hours to process events. On-Demand: m5.large at $0.096/hr × 1,000 × 4 = $384/night = $11,520/month. Spot: m5.large Spot at ~$0.028/hr × 1,000 × 4 = $112/night = $3,360/month. With interruption handling (checkpoint to S3, restart from checkpoint), Spot interruptions cost 30 minutes of re-processing 2× per month = $6. Net Spot cost: $3,366. Savings: $8,154/month (71%). Interruption handling code is worth writing.

---

## 🧠 Mental Model / Analogy

Spot Instances are **standby flight seats**: airlines sell empty seats at huge discounts right before departure, but can give those seats to a higher-paying passenger if one shows up. You save enormously but must be willing to be "bumped." Reserved Instances are **annual parking passes**: commit for a year, get a guaranteed spot at a discount. Savings Plans are **multi-restaurant meal vouchers**: commit to spending $X/day, use at any restaurant in the group (any EC2 type, Lambda, Fargate).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Spot for dev/test environments (acceptable interruption). Reserved or Savings Plan for always-on production databases, application servers. 1-year No Upfront Savings Plan: decent savings, no cash commitment, good starting point.

**Level 2 — Practitioner**: Mixed fleet: combine On-Demand base capacity with Spot for burst. Auto Scaling with mixed instances: primary On-Demand + Spot workers. Spot interruption notice handler: catch `EC2 Spot Instance interruption notice` via EventBridge → drain ECS task / checkpoint Lambda / drain EKS node. Fargate Spot: Spot pricing for Fargate containers, same 2-minute interrupt behavior.

**Level 3 — Advanced**: Spot Fleet: launch across multiple instance types + AZs simultaneously; maintain target capacity. EC2 Auto Scaling mixed instances policy: `OnDemandBaseCapacity=2, OnDemandPercentageAboveBaseCapacity=30` → 70% Spot once base On-Demand covered. Spot Rebalancing Recommendation: earlier signal (before interruption notice) → proactive replacement before being interrupted. Instance type diversification strategy: `c5.xlarge, c5a.xlarge, c4.xlarge, m5.xlarge` = ~4x the capacity pools → reduce interruption probability.

**Level 4 — Expert**: Karpenter (EKS): intelligent node provisioning with Spot awareness; automatically picks cheapest Spot instance type; graceful draining. Spot price history analysis: use `describe-spot-price-history` to identify historically stable instance types. EC2 Instance Savings Plans vs Compute Savings Plans: Instance SP = 72% savings (most specific: specific family + region); Compute SP = 66% (flexible: any family, any region, EC2+Fargate+Lambda). RI Marketplace: sell unused Reserved Instances. Convertible RIs: exchange for different instance types during commitment; useful if you're unsure about future instance types.

---

## ⚙️ How It Works

### Spot Instance Interruption Handling (Spring Boot + AWS SDK)

```java
@Service
@Slf4j
public class SpotInterruptionWatcher {

    private final EC2MetadataUtils metadataUtils;
    private final JobCheckpointService checkpointService;

    @Scheduled(fixedDelay = 5000)  // check every 5 seconds
    public void checkForInterruptionNotice() {
        try {
            // Query IMDS v2 for interruption notice
            String token = getImdsToken();
            HttpResponse<String> response = HttpClient.newHttpClient().send(
                HttpRequest.newBuilder()
                    .uri(URI.create("http://169.254.169.254/latest/meta-data/spot/interruption-action"))
                    .header("X-aws-ec2-metadata-token", token)
                    .build(),
                HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() == 200) {
                log.warn("SPOT INTERRUPTION NOTICE: {} - checkpointing immediately", response.body());
                checkpointService.saveCheckpoint();    // save progress
                checkpointService.gracefulShutdown();  // finish current batch
            }
        } catch (Exception e) {
            // No interruption notice (404) = normal, ignore
        }
    }
}
```

### Mixed Instance Auto Scaling Group (Terraform)

```hcl
resource "aws_autoscaling_group" "workers" {
  name               = "workers-mixed"
  vpc_zone_identifier = var.private_subnet_ids
  min_size           = 2
  max_size           = 20
  desired_capacity   = 4

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 2     # always 2 On-Demand
      on_demand_percentage_above_base_capacity = 20    # 20% On-Demand after base
      spot_allocation_strategy                 = "capacity-optimized"  # lowest interruption
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.worker.id
        version            = "$Latest"
      }

      override {
        instance_type = "m5.xlarge"
      }
      override {
        instance_type = "m5a.xlarge"  # same specs, different CPU vendor
      }
      override {
        instance_type = "m4.xlarge"   # previous gen, similar specs
      }
      override {
        instance_type = "c5.2xlarge"  # compute-optimized alternative
      }
    }
  }

  tag {
    key                 = "spot-enabled"
    value               = "true"
    propagate_at_launch = true
  }
}
```

### ECS Service with Fargate Spot

```hcl
resource "aws_ecs_service" "batch_processor" {
  name            = "batch-processor"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.processor.arn
  desired_count   = 10

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 4     # 80% Spot
    base              = 0
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1     # 20% On-Demand
    base              = 2     # always 2 On-Demand minimum
  }
}
```

### Compute Savings Plan (AWS CLI)

```bash
# Step 1: Get recommendations
aws savingsplans describe-savings-plans-purchase-recommendation \
  --product-type ComputeSavingsPlans \
  --payment-option NO_UPFRONT \
  --term ONE_YEAR \
  --query 'Recommendations[0].{Commitment:EstimatedMonthlySavingsAmount,SavedAmount:EstimatedSavingsAmount}'

# Step 2: Check current Spot usage and savings
aws ce get-savings-utilization-details \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --filter '{"Dimensions":{"Key":"PURCHASE_TYPE","Values":["Spot"]}}'

# Step 3: Monitor Spot interruption rates by instance type
aws ec2 describe-spot-price-history \
  --instance-types m5.xlarge m5a.xlarge m4.xlarge \
  --product-descriptions "Linux/UNIX" \
  --start-time 2024-01-01T00:00:00 \
  --query 'SpotPriceHistory[].{Type:InstanceType,Price:SpotPrice,AZ:AvailabilityZone,Time:Timestamp}'
```

---

## ⚖️ Comparison Table: Pricing Models

| Model                   | Savings | Commitment   | Flexibility              | Best For                             |
| ----------------------- | ------- | ------------ | ------------------------ | ------------------------------------ |
| On-Demand               | 0%      | None         | Full                     | Unpredictable, short-term            |
| Spot                    | 60-90%  | None         | Limited (interruptible)  | Batch, stateless, fault-tolerant     |
| Savings Plan (1yr)      | 30-40%  | 1yr $/hr     | High (any instance type) | Predictable, mixed workloads         |
| Savings Plan (3yr)      | 40-66%  | 3yr $/hr     | High (any instance type) | Stable long-term workloads           |
| Reserved Standard (1yr) | 36-42%  | 1yr instance | Low (specific type)      | Fixed instance type/region           |
| Reserved Standard (3yr) | 56-75%  | 3yr instance | Low (specific type)      | Absolutely certain commitment        |
| Reserved Convertible    | 31-66%  | 1-3yr        | Medium (can exchange)    | Predictable but may need flexibility |

---

## ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| "Spot instances are too unreliable"         | 90%+ run without interruption; 2-minute warning; interruptible workloads can handle this cheaply       |
| "Reserved Instances lock me in forever"     | RI Marketplace allows selling unused RIs; Convertible RIs allow family exchanges                       |
| "Savings Plans apply everywhere"            | Compute Savings Plans: EC2, Lambda, Fargate; EC2 Instance Savings Plans: specific instance family only |
| "Spot Instances require immediate shutdown" | 2-minute warning allows graceful shutdown, checkpoint, ECS task draining, EKS node cordon              |

---

## 🔗 Related Keywords

- [AWS Cost Optimization](/cloud-aws/aws-cost-optimization/) — full cost optimization strategy
- [Auto Scaling Groups](/cloud-aws/auto-scaling-groups/) — mixed instance fleet management
- [ECS / Fargate](/cloud-aws/ecs-fargate/) — Fargate Spot configuration

---

## 📌 Quick Reference Card

```bash
# Current Spot price for instance types
aws ec2 describe-spot-price-history \
  --instance-types m5.xlarge c5.xlarge \
  --product-descriptions "Linux/UNIX" \
  --max-results 10

# Check Spot interruption rate by instance type (AWS Spot Advisor = manual)
# Programmatic: use EC2 Spot Instance Advisor recommendations API
aws ec2 describe-instance-type-offerings \
  --filters Name=instance-type,Values=m5.xlarge \
  --location-type availability-zone

# Check your Savings Plans utilization
aws savingsplans describe-savings-plans \
  --states active \
  --query 'savingsPlans[].{Arn:savingsPlanArn,Commitment:commitment,Savings:savingsPlanType}'

# Check Reserved Instance utilization
aws ce get-reservation-utilization \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --query 'UtilizationsByTime[0].Total'
```

---

## 🧠 Think About This

The biggest hidden cost in Spot usage is **not using capacity-optimized allocation strategy**. The default strategy is `lowest-price` — picks the cheapest pool today, but cheapest pools are often cheapest because they have low surplus capacity, meaning higher interruption rates. The `capacity-optimized` strategy picks the pool with the most available surplus capacity, which is more expensive per hour but gets interrupted far less often. In practice: if you run 100 Spot instances for a month, `lowest-price` might interrupt 15-20 of them while `capacity-optimized` interrupts 3-5. The slightly higher hourly rate of `capacity-optimized` is more than offset by the avoided re-processing cost from interruptions. AWS documented this: capacity-optimized reduces interruption rate by 15x on average. Always use `capacity-optimized` for `spot_allocation_strategy` in your Auto Scaling Groups and Spot Fleets.
