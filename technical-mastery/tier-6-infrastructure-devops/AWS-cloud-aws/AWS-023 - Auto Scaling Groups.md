---
version: 1
layout: default
title: "Auto Scaling Groups"
parent: "Cloud - AWS"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/cloud-aws/auto-scaling-groups/
id: AWS-029
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on: ["EC2", "EC2 Instance Types", "ELB / ALB / NLB"]
used_by: ["ELB / ALB / NLB", "CloudWatch", "ECS / Fargate"]
related:
  [
    "EC2",
    "ELB / ALB / NLB",
    "Spot Instances / Reserved Instances",
    "HPA (Horizontal Pod Autoscaler)",
  ]
tags: [aws, auto-scaling, asg, ec2, elasticity, scaling, cloud]
---

## ⚡ TL;DR

**Auto Scaling Groups (ASG)** automatically add or remove EC2 instances based on demand. Policies: target tracking (maintain 70% CPU), step scaling, or scheduled. Integrates with ALB (registers/deregisters instances). Key settings: `min`, `desired`, `max` instance count. Supports Spot + On-Demand mix for cost optimization. Health checks replace unhealthy instances automatically.

---

## 🔥 Problem This Solves

Manual capacity management: provisioning for peak load wastes money off-peak; under-provisioning causes performance issues at peak. ASG solves this: scale out automatically when demand rises, scale in when it drops. Also replaces failed instances automatically (self-healing).

---

## 📘 Textbook Definition

An Auto Scaling Group is a collection of Amazon EC2 instances that are treated as a logical grouping for the purposes of automatic scaling and management. ASGs maintain a specified number of instances, automatically scale in response to changing conditions, and integrate with load balancers to distribute traffic across healthy instances.

---

## ⏱️ 30 Seconds

```
ASG configuration:
  min:     minimum instances (always running)
  desired: current target count
  max:     maximum instances (cost cap)

Scaling policies:
  Target Tracking:  maintain metric (CPU=70%)  -
    recommended
  Step Scaling:     add N instances when CPU > 80%
  Scheduled:        8am add 5 instances, 6pm remove 5

Health checks:
  EC2:  instance responds to status check
  ALB:  target group health check (more thorough;
    recommended)

Launch Template: defines instance config (AMI, type, SG,
  user data)
```

---

## 🔩 First Principles

- **Launch Template**: blueprint for new instances; versioned; supports mixed instance types
- **Health check replacement**: unhealthy instance → ASG terminates → launches replacement
- **Scale-out fast, scale-in slow**: AWS default: wait 300s before scale-in (prevents thrashing)
- **Lifecycle hooks**: run custom actions on launch (register with service mesh) or terminate (drain connections)
- **Warm pool**: pre-initialized instances ready to launch quickly (reduce cold start time)

---

## 🧪 Thought Experiment

E-commerce site: normal traffic = 4 instances. Black Friday: traffic × 10. Without ASG: site crashes at 3x normal traffic. With ASG (max=40, target CPU=70%): traffic rises → CPU climbs → target tracking fires → 5→10→20→35 instances launched → CPU stabilizes at 70% → all requests served. After peak: traffic drops → ASG scales in over 20 minutes → back to 4 instances.

---

## 🧠 Mental Model / Analogy

ASG is a **self-adjusting assembly line**: based on how backed up the line gets (CPU/request count), the factory manager (ASG) automatically hires more workers (launches instances) or sends some home (terminates instances). Minimum crew size stays (min), maximum crew cap set for budget (max), and daily optimal team size targeted (desired).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create ASG with Launch Template, min/desired/max, target tracking policy (CPU 70%), attach to ALB target group.

**Level 2 - Practitioner**: Mixed instances policy: combine Spot + On-Demand (spot for burst, on-demand for baseline). Capacity Rebalancing: replace spot instances proactively before interruption. ALB health checks (preferred over EC2 health checks). Cooldown period to prevent scaling thrashing.

**Level 3 - Advanced**: Lifecycle hooks: `autoscaling:EC2_INSTANCE_LAUNCHING` → run bootstrap script, register with service mesh. `autoscaling:EC2_INSTANCE_TERMINATING` → drain connections (complement ALB connection draining). Warm pool: pre-launch instances in Stopped state → scale-out = just start (seconds, not minutes). Instance weighting in mixed instances: give different weights to different instance types (1 xlarge = 2 large in scaling calculations).

**Level 4 - Expert**: Predictive scaling: ML-based; analyzes patterns (Monday 9am traffic spike) → pre-scales 14 minutes before predicted load. Capacity providers in ECS: ASG-backed capacity providers for ECS with managed scaling. Dynamic scaling policies with CloudWatch Composite Alarms: AND/OR conditions for more precise scaling decisions. ASG + Launch Template mixed instances: define base capacity (2 on-demand) + spot instances for everything above, with multiple instance types for spot availability.

---

## ⚙️ How It Works

---

### ASG with Mixed Instance Policy (Terraform)

```hcl
# Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "my-app-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "m7g.large"   # default type

  iam_instance_profile {
    arn = aws_iam_instance_profile.app.arn
  }

  vpc_security_group_ids = [aws_security_group.app.id]

  # IMDSv2 required
  metadata_options {
    http_tokens = "required"
  }

  user_data = base64encode(file("bootstrap.sh"))
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "my-app-asg"
  vpc_zone_identifier = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
    aws_subnet.private_c.id
  ]

  min_size         = 2
  desired_capacity = 4
  max_size         = 20

  health_check_type         = "ELB"   # ALB health check (preferred)
  health_check_grace_period = 300
  # wait 5min before checking health

  # ALB target group registration
  target_group_arns = [aws_lb_target_group.app.arn]

  # Mixed instances: Spot + On-Demand
  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 2
      # always 2 on-demand
      on_demand_percentage_above_base_capacity = 0
      # rest = all spot
      spot_allocation_strategy                 =
          "capacity-optimized-prioritized"
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.app.id
        version            = "$Latest"
      }

      # Multiple instance types for spot availability
      override {
        instance_type = "m7g.large"
      }
      override {
        instance_type = "m7g.xlarge"
        weighted_capacity = "2"   # 1 xlarge counts as 2 units
      }
      override {
        instance_type = "m6g.large"
      }
    }
  }

  # Tag instances launched by this ASG
  tag {
    key                 = "Environment"
    value               = "production"
    propagate_at_launch = true
  }
}

# Target Tracking Scaling Policy (recommended)
resource "aws_autoscaling_policy" "cpu_target" {
  name                   = "cpu-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

---

### Lifecycle Hook for Graceful Shutdown

```python
# Lambda triggered by ASG termination lifecycle hook
import boto3

def handler(event, context):
    asg = boto3.client('autoscaling')

    instance_id = event['detail']['EC2InstanceId']
    lifecycle_action_token = event['detail']['LifecycleActionToken']

    # Custom logic: drain connections, deregister from service mesh
    ec2 = boto3.client('ec2')

    # Send SSM command to gracefully stop app
    ssm = boto3.client('ssm')
    ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': ['systemctl stop myapp']}
    )

    # Wait for connections to drain (30 seconds)
    import time
    time.sleep(30)

    # Complete lifecycle action: allow termination to proceed
    asg.complete_lifecycle_action(
        LifecycleHookName='my-termination-hook',
        AutoScalingGroupName=event['detail']['AutoScalingGroupName'],
        LifecycleActionToken=lifecycle_action_token,
        LifecycleActionResult='CONTINUE'
    )
```

---

## 🔄 E2E Flow: Scale-Out Event

```
Black Friday 8:59 AM:
  Current: 4 instances running
  CloudWatch: ASGAverageCPUUtilization = 45%

9:00 AM: Traffic spike
  CPUUtilization: 45% → 68% → 82% → 91%

9:01 AM: Target tracking policy triggers
  Target 70% CPU, actual 91% → scale out
  ASG calculates: need ~5.2 more instances → launches 6

9:02-9:07 AM: New instances launch
  User data bootstraps app (~3-4 min)
  ALB health checks pass
  Instances registered in target group

9:07 AM: 10 instances healthy
  CPUUtilization: 91% → 62% (all 10 serving traffic)

12:00 PM: Traffic normalizes
  CPUUtilization: 62% → 35%
  Target tracking: scale in (default cooldown 300s)

12:05 PM: ASG begins scale-in
  Terminates 2 instances (most recently launched first)
  → 8 instances, CPU still below 70%
  Terminates 2 more → 6 instances
  Terminates 2 more → 4 instances at 68% CPU ≈ target
```

---

## ⚖️ Comparison Table: Scaling Policies

| Policy              | How                                     | Best For                            |
| ------------------- | --------------------------------------- | ----------------------------------- |
| **Target Tracking** | Maintain metric at value                | CPU, ALB request rate               |
| **Step Scaling**    | Add N instances at each alarm threshold | Custom multi-step                   |
| **Simple Scaling**  | +N on alarm, cooldown                   | Legacy; use target tracking instead |
| **Scheduled**       | At specific times                       | Known traffic patterns              |
| **Predictive**      | ML-predicted load                       | Daily/weekly patterns               |

---

## ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                       |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| "Scale-in is instant"                             | Default cooldown 300s; scale-in checks if instance can be removed without going below desired |
| "ASG works without ALB"                           | ASG can work standalone; ALB integration is optional but recommended                          |
| "All instances terminate immediately on scale-in" | ALB connection draining: waits for in-flight requests (default 300s) before terminating       |
| "Desired = min"                                   | Desired is a target; can be manually set or automatically adjusted; min is floor              |

---

## 🔗 Related Keywords

- [EC2](/cloud-aws/ec2/) - instances managed by ASG
- [ELB / ALB / NLB](/cloud-aws/elb-alb-nlb/) - distributes traffic to ASG instances
- [Spot Instances / Reserved Instances](/cloud-aws/spot-instances-reserved-instances/) - cost strategies for ASG
- [HPA (Horizontal Pod Autoscaler)](/kubernetes/hpa-horizontal-pod-autoscaler/) - analogous in Kubernetes

---

## 📌 Quick Reference Card

```bash
# Create ASG
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name my-asg \
  --launch-template LaunchTemplateId=lt-12345,Version='$Latest' \
  --min-size 2 \
  --max-size 20 \
  --desired-capacity 4 \
  --vpc-zone-identifier "subnet-a,subnet-b,subnet-c"

# Set desired capacity manually
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name my-asg \
  --desired-capacity 6

# Describe ASG status
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names my-asg

# Suspend processes (for maintenance)
aws autoscaling suspend-processes \
  --auto-scaling-group-name my-asg \
  --scaling-processes Launch Terminate

# Resume
aws autoscaling resume-processes \
  --auto-scaling-group-name my-asg

# Instance refresh (rolling replacement of all instances)
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name my-asg \
  --preferences '{"MinHealthyPercentage": 90}'
```

---

## 🧠 Think About This

The most underused ASG feature is **Instance Refresh**, which performs a rolling replacement of all instances in an ASG. This is the proper way to deploy an updated AMI to all ASG instances: rather than draining and replacing manually, Instance Refresh replaces instances one by one (maintaining MinHealthyPercentage), with health checks ensuring new instances are healthy before proceeding. This enables blue-green-like deployments for ASG-based infrastructure without a separate target group swap. Combined with Warm Pools, Instance Refresh can perform rolling AMI updates with near-zero impact on capacity. Most teams who built their EC2-based apps before ECS/EKS became mainstream should evaluate Instance Refresh as their deployment mechanism - it's often the missing piece between "deploy by SSH" and "containerized CI/CD."
