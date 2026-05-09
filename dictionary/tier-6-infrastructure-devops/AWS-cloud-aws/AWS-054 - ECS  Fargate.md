---
version: 1
layout: default
title: "ECS  Fargate"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /cloud-aws/ecs-fargate/
id: AWS-054
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on:
  [
    "Containers",
    "VPC",
    "IAM (Identity and Access Management)",
    "ELB / ALB / NLB",
  ]
used_by: ["EKS", "AWS Cost Optimization"]
related: ["EKS", "Lambda", "ELB / ALB / NLB", "AWS Cost Optimization"]
tags: [aws, ecs, fargate, containers, docker, orchestration, cloud]
---

# ECS / Fargate

## ⚡ TL;DR

**ECS (Elastic Container Service)** is AWS's container orchestration service. Run containers as **Tasks** grouped into **Services**. Launch types: **EC2** (you manage underlying instances) or **Fargate** (serverless: no EC2 to manage, pay per vCPU/memory per second). Fargate = simplest path to production containers on AWS. EKS = more power/control but more complexity.

---

## 🔥 Problem This Solves

You have a Docker container and need it running reliably: auto-restarts on failure, scale up/down, load-balanced traffic, health checks, rolling deployments. Without ECS: manage EC2 fleet, run container daemon, write restart scripts, set up your own LB integration. ECS/Fargate: declare desired count, ECS keeps it running.

---

## 📘 Textbook Definition

Amazon ECS is a fully managed container orchestration service. Task Definitions define containers (image, CPU, memory, env vars, volumes). Services maintain a desired number of Task replicas and integrate with ELBs for traffic. Fargate launch type removes the need to provision and manage EC2 instances - AWS manages the underlying compute.

---

## ⏱️ 30 Seconds

```
Core concepts:
  Task Definition:  blueprint (Docker image, CPU, memory, env, ports)
  Task:             running instance of Task Definition
  Service:          maintains N tasks, integrates with ALB
  Cluster:          logical grouping of tasks/services

Launch types:
  EC2:     you manage instances; cheaper at steady-state; more control
  Fargate: serverless; no EC2; pay per vCPU-second + GB-second

Fargate pricing (us-east-1):
  vCPU: $0.04048/vCPU-hr
  Memory: $0.004445/GB-hr
  Example: 0.5 vCPU + 1GB = ~$0.025/hr (vs t3.small EC2 $0.023/hr)

Scaling:
  ECS Service Auto Scaling: target tracking (CPU/mem/ALB req count)
  Application Auto Scaling API (same as EC2 ASG)
```

---

## 🔩 First Principles

- **Task = container(s)**: one or more containers sharing network namespace (localhost) and optional shared volumes
- **Service = desired count**: ECS continuously reconciles actual running count to desired
- **Task role vs execution role**: task role = what your app can access (S3, DynamoDB); execution role = what ECS can do (pull ECR image, write logs)
- **awsvpc networking mode**: Fargate requires it; each task gets its own ENI + private IP in VPC (like a micro-VM)
- **Service discovery**: Cloud Map integration; DNS-based service-to-service communication

---

## 🧪 Thought Experiment

Spring Boot microservice: package as Docker image, push to ECR. Task Definition: 0.5 vCPU, 1GB memory, image=ECR URI, port 8080, env vars from Secrets Manager. Service: desired 3 tasks, ALB target group, health check on `/actuator/health`. Service Auto Scaling: scale out when CPU>70%. Rolling deployment: ECS replaces tasks one by one. Total operational overhead: minimal. Compare to EKS: no YAML Deployments/Services/Ingress/HPA to manage.

---

## 🧠 Mental Model / Analogy

ECS is a **restaurant manager**: you describe the dish (Task Definition), set the number of tables that should be served (desired count), and the manager ensures that many dishes are always being served. If a cook drops a dish (task crashes), the manager immediately makes a new one (restarts task). Fargate = the kitchen equipment is also provided and maintained by the restaurant franchise (AWS) - you just bring the recipe (container image).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create ECR repository, push Docker image. Create Task Definition. Create ECS Cluster (Fargate). Create Service. Access via ALB.

**Level 2 - Practitioner**: Task Definition environment variables from Secrets Manager (no secrets in ECR image). CloudWatch Container Insights: CPU/memory per container. Service Connect: easy service-to-service DNS (replaces manual Cloud Map setup). ECS rolling deployments: configure minimum healthy percent (100%) and maximum percent (200%) for zero-downtime.

**Level 3 - Advanced**: ECS Capacity Providers: mix EC2 + Fargate Spot for cost optimization. Fargate Spot: up to 70% discount, can be interrupted (2-min warning); suitable for batch jobs. ECS task placement constraints: spread across AZs, avoid same instance. Sidecar containers: run logging/monitoring agent alongside app container in same task.

**Level 4 - Expert**: ECS Anywhere: run ECS tasks on-premises hardware registered as external instances. ECS Exec: shell into running Fargate task for debugging (`aws ecs execute-command`). ECS Service Connect vs App Mesh: Service Connect for simple L4 connectivity; App Mesh for Envoy-based L7 routing (canary, retries, circuit breaking). ECS task metadata endpoint: container can query its own metadata (task ID, cluster, CPU/mem limits) via 169.254.170.2. ECS Firelens: custom log routing via Fluent Bit sidecar to multiple destinations (S3, OpenSearch, Splunk) without app code changes.

---

## ⚙️ How It Works

### ECS Fargate Service (Terraform)

```hcl
# ECR Repository
resource "aws_ecr_repository" "app" {
  name                 = "my-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true  # vulnerability scan on push
  }
}

# Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "my-app"
  network_mode             = "awsvpc"    # required for Fargate
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"       # 0.5 vCPU
  memory                   = "1024"      # 1 GB

  # IAM roles
  task_role_arn      = aws_iam_role.task.arn        # app permissions
  execution_role_arn = aws_iam_role.task_exec.arn   # ECS permissions

  container_definitions = jsonencode([{
    name      = "app"
    image     = "${aws_ecr_repository.app.repository_url}:latest"
    essential = true

    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
      name          = "app"        # for Service Connect
    }]

    environment = [
      { name = "SPRING_PROFILES_ACTIVE", value = "prod" },
      { name = "SERVER_PORT",            value = "8080" }
    ]

    # Secrets from Secrets Manager (inject as env vars)
    secrets = [
      {
        name      = "DB_PASSWORD"
        valueFrom = "${aws_secretsmanager_secret.db.arn}:password::"
      },
      {
        name      = "REDIS_AUTH_TOKEN"
        valueFrom = aws_secretsmanager_secret.redis.arn
      }
    ]

    # Health check
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8080/actuator/health || exit 1"]
      interval    = 30
      timeout     = 10
      retries     = 3
      startPeriod = 60  # allow 60s for JVM startup
    }

    # CloudWatch Logs
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/my-app"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "app"
      }
    }

    # Resource limits
    cpu    = 512
    memory = 1024
  }])
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "main-cluster"

  # Enable Container Insights
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "my-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  # Networking
  network_configuration {
    subnets          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false   # private subnets
  }

  # Load balancer
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8080
  }

  # Zero-downtime deployments
  deployment_circuit_breaker {
    enable   = true
    rollback = true   # auto-rollback on failure
  }
  deployment_maximum_percent         = 200   # can go to 200% during deployment
  deployment_minimum_healthy_percent = 100   # never go below 100% capacity

  # Service Connect (service-to-service DNS)
  service_connect_configuration {
    enabled   = true
    namespace = aws_service_discovery_http_namespace.main.arn

    service {
      port_name      = "app"
      discovery_name = "my-app"

      client_alias {
        port     = 8080
        dns_name = "my-app"
      }
    }
  }
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 20
  min_capacity       = 3
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "cpu-target-tracking"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

---

## ⚖️ Comparison Table: ECS Fargate vs EKS vs Lambda

|                     | ECS Fargate       | EKS                  | Lambda       |
| ------------------- | ----------------- | -------------------- | ------------ |
| **Orchestration**   | ECS native        | Kubernetes           | None         |
| **Mgmt complexity** | Low               | High                 | None         |
| **Cold start**      | 1-5s per task     | 1-5s per pod         | ms-seconds   |
| **Max duration**    | Unlimited         | Unlimited            | 15 min       |
| **Portability**     | AWS-specific      | Industry standard    | AWS-specific |
| **Cost (idle)**     | Per second        | Per second + cluster | Zero         |
| **Best for**        | AWS teams, simple | Kubernetes shops     | Event-driven |

---

## ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                        |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| "Fargate = slow startup"                    | Fargate task startup: 20-60s (image pull + initialization); not a cold start like Lambda                                       |
| "ECS is less capable than EKS"              | ECS covers 90% of container workloads; EKS needed for K8s ecosystem or specific requirements                                   |
| "Task role and execution role are the same" | Task role: permissions for your app code. Execution role: permissions for ECS to run the task (ECR pull, Secrets access, logs) |
| "Fargate is always more expensive than EC2" | Fargate saves on EC2 management overhead; Fargate Spot can reduce cost by 70%                                                  |

---

## 🔗 Related Keywords

- [EKS](/cloud-aws/eks/) - Kubernetes-based container orchestration
- [Lambda](/cloud-aws/lambda/) - serverless alternative for short-running tasks
- [ELB / ALB / NLB](/cloud-aws/elb-alb-nlb/) - load balancer for ECS services

---

## 📌 Quick Reference Card

```bash
# List services in cluster
aws ecs list-services --cluster main-cluster

# Describe service
aws ecs describe-services \
  --cluster main-cluster \
  --services my-app \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'

# Force new deployment (rolling restart)
aws ecs update-service \
  --cluster main-cluster \
  --service my-app \
  --force-new-deployment

# Shell into running Fargate task (ECS Exec)
TASK_ID=$(aws ecs list-tasks \
  --cluster main-cluster --service-name my-app \
  --query 'taskArns[0]' --output text | awk -F/ '{print $NF}')

aws ecs execute-command \
  --cluster main-cluster \
  --task $TASK_ID \
  --container app \
  --interactive \
  --command "/bin/bash"

# View task logs
aws logs tail /ecs/my-app --since 30m --follow

# Scale service manually
aws ecs update-service \
  --cluster main-cluster \
  --service my-app \
  --desired-count 5
```

---

## 🧠 Think About This

The most common ECS operational mistake is setting `deployment_minimum_healthy_percent=50` (the default), which allows ECS to stop half your tasks before starting new ones during a deployment. For a service with 4 tasks: ECS stops 2, starts 2 new → at 50% capacity during deployment → increased latency or errors under load. Set `minimum_healthy_percent=100` and `maximum_percent=200` for zero-downtime deployments (requires double capacity briefly). Also enable the Deployment Circuit Breaker with rollback - this automatically rolls back if the new task fails health checks, saving you from a manual rollback. Without the circuit breaker, a bad deployment with an app that fails to start will kill all tasks as ECS keeps replacing healthy tasks with broken ones. The circuit breaker caught this and made ECS automatically revert to the last stable task definition.
