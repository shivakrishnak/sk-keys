---
layout: default
title: "AWS ECS  Fargate"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /cloud-aws/aws-ecs-fargate/
id: AWS-021
category: Cloud - AWS
difficulty: ★★★
depends_on: Docker, Containers, AWS
used_by: Containers, Cloud - AWS
related: Kubernetes, AWS Lambda, Docker Compose
tags:
  - aws
  - cloud
  - containers
  - advanced
---

# AWS-021 - AWS ECS  Fargate

⚡ **TL;DR -** ECS is AWS's container orchestration service; Fargate is its serverless compute engine - run Docker containers on AWS without managing EC2 instances or Kubernetes clusters.

| | |
|---|---|
| **Depends on** | Docker, Containers, AWS |
| **Used by** | Containers, Cloud - AWS |
| **Related** | Kubernetes, AWS Lambda, Docker Compose |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Running a Docker container in production requires provisioning EC2 instances, installing Docker daemon, writing startup scripts, managing instance scaling separately from container scaling, handling node failures, and patching the OS. A single container requires managing its host machine as a full server.

**THE BREAKING POINT:** At 50 microservices, managing the EC2 fleet for container hosting becomes a full-time job. Which instance is running which container? What happens when an EC2 instance fails? How do you scale containers without over-provisioning or under-provisioning instances?

**THE INVENTION MOMENT:** ECS answered: what if containers were the unit of deployment, not EC2 instances? And Fargate answered: what if there were no EC2 instances at all - just containers with CPU and memory allocations?

---

### 📘 Textbook Definition

**Amazon ECS (Elastic Container Service)** is a fully managed container orchestration service that runs Docker containers on clusters of EC2 instances or AWS Fargate. A **Task Definition** declares container images, CPU/memory, networking, and IAM permissions. A **Service** maintains a desired number of running tasks, integrates with load balancers, and handles replacement on failure. **AWS Fargate** is a serverless compute engine for ECS (and EKS) that eliminates EC2 instance management - you define task CPU/memory and AWS provisions the underlying compute invisibly.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Run Docker containers on AWS - ECS schedules them; Fargate hides the servers entirely.

**One analogy:**
> ECS is like a shipping port that manages cargo containers (Docker containers). You hand over a shipping manifest (Task Definition) and the port manages which dock (EC2 instance) loads each container. Fargate is like an Amazon delivery service - you give them a package (container spec) and they handle the truck, the route, and the driver entirely.

**One insight:** Fargate containers have no persistent host - each task runs in isolated, ephemeral compute. There is no SSH access, no OS to patch, and no cluster capacity to manage.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A Task Definition is the immutable specification of a container workload - image, CPU, memory, env vars, ports, IAM role.
2. A Service is the runtime controller - maintains desired task count, integrates with ALB, replaces failed tasks.
3. Fargate provides serverless compute; EC2 launch type provides host control at the cost of cluster management.
4. Task IAM roles grant AWS API permissions to the container - no EC2 instance profile is involved.

**DERIVED DESIGN:** ECS decouples the container specification (Task Definition) from the runtime state (Service). The cluster scheduler places tasks on capacity (Fargate or EC2 instances). When a task fails, the service controller detects the deviation from desired count and launches a replacement. The ALB target group health check gates traffic to only healthy task instances.

**THE TRADE-OFFS:**
**Gain (Fargate):** No EC2 management, task-level billing (per vCPU/memory per second), per-task networking isolation, faster scaling without capacity planning.
**Cost (Fargate):** Higher unit price than EC2 for sustained workloads; no GPU support; container startup time ~30 seconds; limited OS customisation.

---

### 🧪 Thought Experiment

**SETUP:** You run a Node.js API as a Docker container. You use ECS EC2 launch type with 5 `t3.medium` instances.

**WHAT HAPPENS AT 3 AM:** One EC2 instance crashes. ECS detects 5 tasks should run; only 3 are running. It schedules 2 new tasks - but the remaining 4 instances are at capacity. Auto Scaling must provision a new EC2 instance (3–5 minutes) before the 2 tasks can start.

**WHAT HAPPENS WITH FARGATE:** There are no EC2 instances. The 2 replacement Fargate tasks start within 30 seconds. ECS schedules them directly on Fargate capacity. No Auto Scaling, no cluster capacity management, no 3 AM on-call for instance provisioning.

**THE INSIGHT:** Fargate shifts the scaling unit from EC2 instances to individual containers. This removes an entire operational layer - the container host - and makes ECS a pure container platform rather than a container-on-servers platform.

---

### 🧠 Mental Model / Analogy

> ECS is like a restaurant kitchen management system. The Task Definition is the recipe (ingredients, cooking time, equipment needed). The Service is the kitchen manager who ensures the right number of dishes are being prepared at all times and replaces any that fail quality check. Fargate is like renting a ghost kitchen - you provide the recipe and ingredients; the kitchen, stoves, and staff are someone else's problem.

- **Recipe** = Task Definition (container image, CPU, memory, env)
- **Dishes being cooked** = running task instances
- **Kitchen manager** = ECS Service controller
- **Kitchen** = ECS Cluster + underlying compute
- **Ghost kitchen** = Fargate (serverless compute)
- **Quality check** = ALB health check for target group

Where this analogy breaks down: a real kitchen's capacity is physically limited; Fargate's capacity is virtually unlimited (within account limits) and scales on demand.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
ECS runs your Docker containers in the AWS cloud. Fargate means you don't need to set up any servers - you just tell AWS how much CPU and memory your container needs and it handles everything else.

**Level 2 - How to use it (junior developer):**
Write a Task Definition (JSON) specifying your Docker image, CPU, memory, port mappings, and env vars. Create an ECS Cluster. Create a Service pointing at your Task Definition with desired count 2. Attach it to an ALB Target Group. ECS starts 2 container instances and registers them with the load balancer. If one fails, ECS starts a replacement automatically.

**Level 3 - How it works (mid-level engineer):**
Fargate tasks get a dedicated `awsvpc` network interface with a private IP in your VPC subnet - no sharing with other tasks or hosts. The Task Execution Role grants ECS permissions to pull the container image from ECR, write logs to CloudWatch, and retrieve secrets from Secrets Manager. The Task Role grants the container code AWS API permissions (S3, DynamoDB, etc.). Capacity Providers configure how ECS sources compute: `FARGATE`, `FARGATE_SPOT`, or named EC2 Auto Scaling Groups. Fargate Spot can reduce costs 70% for interruption-tolerant workloads.

**Level 4 - Why it was designed this way (senior/staff):**
The two-role model (Task Execution Role vs Task Role) is a critical security separation. The Execution Role is ECS's role - used by the ECS agent to set up the task (pull image, get secrets, publish logs). The Task Role is the application's role - used by the container process at runtime for AWS API calls. Conflating them would mean every container has broad AWS API access just because it needs to pull from ECR. The separation implements the principle of least privilege at the platform boundary: the container runtime setup is isolated from the container application's permissions.

---

### ⚙️ How It Works (Mechanism)

1. **Task Definition** - versioned JSON document specifying: container image URIs, CPU/memory, port mappings, environment variables, secrets (from Secrets Manager/SSM), log configuration (CloudWatch Logs), volumes, and IAM task role/execution role.
2. **Cluster** - logical grouping of ECS capacity. Can contain Fargate capacity, EC2 instances, or external instances (ECS Anywhere).
3. **Service** - the long-running controller. Specifies desired task count, Task Definition revision, load balancer integration, network configuration (VPC subnets, security groups), and auto-scaling policies.
4. **Task** - a running instance of a Task Definition. For Fargate: isolated compute + network interface. For EC2: process(es) on an EC2 host.
5. **Capacity Providers** - link Services to compute sources. `FARGATE` for on-demand, `FARGATE_SPOT` for spot (up to 70% cheaper, may be interrupted), EC2 ASG for custom instances.
6. **Service Auto Scaling** - scales desired task count based on CloudWatch metrics (CPU, memory, ALB request count, custom metrics) using Application Auto Scaling.
7. **IAM roles** - Task Execution Role (for ECS agent: ECR pull, Secrets Manager, CloudWatch Logs) + Task Role (for app code: S3, DynamoDB, etc.).
8. **Container networking** - `awsvpc` mode gives each Fargate task a dedicated ENI with a private IP. Security groups apply at the task level.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Fargate service deployment):**
```
Developer pushes to Git
     |
     | CI/CD: docker build + push to ECR
     v
New Task Definition revision registered
     |
     | ecs:UpdateService (new task def revision)
     v
ECS Service Controller
  [rolling update: launch new tasks]
  [wait for ALB health check pass]
  [deregister + drain old tasks]     ← YOU ARE HERE
     |
Fargate
  [provision isolated compute]
  [pull image from ECR via VPC endpoint]
  [inject env vars + secrets]
  [start container process]
     |
     v
ALB registers new task target → traffic flows
```

**FAILURE PATH:**
- Container exits non-zero → task marked `STOPPED`; service counts deviation; replacement task launched
- ALB health check fails → task drained from target group; replacement started before old task terminated
- Task Execution Role missing ECR pull permission → task fails to start with `CannotPullContainerError`

**WHAT CHANGES AT SCALE:**
Use `FARGATE_SPOT` for stateless workers (queue processors, batch jobs) to cut costs 70%. For APIs, use `FARGATE` (on-demand) for baseline and a Spot capacity provider for overflow. Enable ECS Service Connect for service-to-service discovery without an external service mesh.

---

### 💻 Code Example

**Task Definition JSON (Fargate):**
```json
{
  "family": "api-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123:role/EcsExecRole",
  "taskRoleArn": "arn:aws:iam::123:role/ApiTaskRole",
  "containerDefinitions": [{
    "name": "api",
    "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/api:latest",
    "portMappings": [{"containerPort": 8080}],
    "environment": [
      {"name": "ENV", "value": "production"}
    ],
    "secrets": [{
      "name": "DB_PASSWORD",
      "valueFrom": "arn:aws:secretsmanager:...:prod/db"
    }],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/api-service",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "healthCheck": {
      "command": [
        "CMD-SHELL",
        "curl -f http://localhost:8080/health || exit 1"
      ],
      "interval": 30,
      "timeout": 5,
      "retries": 3
    }
  }]
}
```

**AWS CDK - ECS Fargate service with ALB:**
```typescript
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from
  'aws-cdk-lib/aws-ecs-patterns';
import * as ecr from 'aws-cdk-lib/aws-ecr';

const cluster = new ecs.Cluster(this, 'Cluster', {
  vpc,
  enableFargateCapacityProviders: true,
});

const service =
  new ecsPatterns.ApplicationLoadBalancedFargateService(
    this, 'ApiService', {
      cluster,
      cpu: 512,
      memoryLimitMiB: 1024,
      desiredCount: 2,
      taskImageOptions: {
        image: ecs.ContainerImage.fromEcrRepository(
          ecr.Repository.fromRepositoryName(
            this, 'Repo', 'my-api'
          )
        ),
        containerPort: 8080,
        environment: { ENV: 'production' },
        secrets: {
          DB_PASSWORD: ecs.Secret.fromSecretsManager(
            secretsManager.Secret.fromSecretNameV2(
              this, 'DbSecret', 'prod/api/db'
            )
          )
        },
        logDriver: ecs.LogDrivers.awsLogs({
          streamPrefix: 'api-service'
        })
      },
      capacityProviderStrategies: [{
        capacityProvider: 'FARGATE',
        weight: 1, base: 2
      }, {
        capacityProvider: 'FARGATE_SPOT',
        weight: 3
      }]
    }
  );

// Auto-scale on CPU utilisation
const scaling = service.service.autoScaleTaskCount({
  minCapacity: 2, maxCapacity: 20
});
scaling.scaleOnCpuUtilization('CpuScaling', {
  targetUtilizationPercent: 70
});
```

**AWS CLI - deploy updated task definition:**
```bash
# Register new task definition revision
aws ecs register-task-definition \
  --cli-input-json file://task-def.json

# Update service to use new revision
aws ecs update-service \
  --cluster my-cluster \
  --service api-service \
  --task-definition api-service:12 \
  --force-new-deployment

# Watch deployment progress
aws ecs describe-services \
  --cluster my-cluster \
  --services api-service \
  --query 'services[0].deployments'
```

---

### ⚖️ Comparison Table

| Feature | ECS + Fargate | ECS + EC2 | Amazon EKS | AWS Lambda |
|---|---|---|---|---|
| **Server management** | None | Full (EC2 fleet) | Partial (node groups) | None |
| **Container orchestration** | ECS scheduler | ECS scheduler | Kubernetes | N/A |
| **Startup time** | ~30 seconds | ~10 seconds | ~30 seconds | ~100ms (warm) |
| **Scaling granularity** | Per task | Per task (limited by instance) | Per pod | Per invocation |
| **Pricing model** | Per vCPU/memory per second | Per EC2 instance hour | Per EC2 node hour | Per request + GB-second |
| **GPU support** | No | Yes | Yes | No |
| **Max container duration** | Unlimited | Unlimited | Unlimited | 15 minutes |
| **Best for** | Microservices, APIs | GPU, custom AMI, cost at scale | Kubernetes workloads | Event-driven, short tasks |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Task Role and Task Execution Role are the same" | Execution Role is ECS's role for infrastructure setup (ECR pull, secrets, logs). Task Role is the application's role for runtime AWS API calls. They must be separate with different permissions. |
| "ECS Fargate is more expensive than Lambda for APIs" | Fargate pricing is vCPU/memory per second with a minimum 1-minute billing. For always-on APIs with steady traffic, Fargate is typically cheaper than Lambda's per-request pricing at scale. |
| "Fargate containers share a host with other customers" | Each Fargate task runs in its own isolated micro-VM (via Firecracker). Tasks from different customers never share kernel resources. |
| "ECS is inferior to Kubernetes because it lacks Kubernetes features" | ECS is simpler to operate and deeply integrated with AWS services (IAM, ALB, CloudWatch, Service Connect). Kubernetes is more powerful for complex scheduling and ecosystem compatibility. Choose based on operational complexity tolerance. |
| "Stopping a task stops the service" | ECS Service detects when a task stops and immediately launches a replacement to maintain the desired count. Stopping individual tasks is for debugging - the service recovers automatically. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: CannotPullContainerError - image pull fails**
**Symptom:** Tasks start and immediately stop with `CannotPullContainerError: failed to pull image`.
**Root Cause:** Task Execution Role lacks `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer`, or there is no VPC endpoint for ECR in a private subnet.
**Diagnostic:**
```bash
# Check task stopped reason
aws ecs describe-tasks \
  --cluster my-cluster \
  --tasks <task-arn> \
  --query 'tasks[0].stoppedReason'

# Check if ECR endpoints exist in VPC
aws ec2 describe-vpc-endpoints \
  --filters \
    Name=service-name,\
Values=com.amazonaws.us-east-1.ecr.api \
  --query 'VpcEndpoints[*].State'
```
**Fix:** Add ECR permissions to the Execution Role. Create PrivateLink endpoints for ECR API and ECR DKR in the task's VPC subnet.
**Prevention:** Use the AWS-managed `AmazonECSTaskExecutionRolePolicy` as the Execution Role baseline. Add ECR PrivateLink endpoints to all private subnets running ECS tasks.

**Mode 2: Task repeatedly cycling - OOM killer**
**Symptom:** Service tasks start, run for 30–60 seconds, then stop with exit code 137 (SIGKILL from OOM killer).
**Root Cause:** Container memory limit in Task Definition is too low. The application is allocating more memory than the `memory` or `memoryReservation` setting.
**Diagnostic:**
```bash
# Check task stop reason
aws ecs describe-tasks \
  --cluster my-cluster \
  --tasks <task-arn> \
  --query 'tasks[0].{
    StoppedReason:stoppedReason,
    ExitCode:containers[0].exitCode
  }'

# Check CloudWatch Container Insights
aws cloudwatch get-metric-statistics \
  --namespace ECS/ContainerInsights \
  --metric-name MemoryUtilized \
  --dimensions \
    Name=ClusterName,Value=my-cluster \
    Name=ServiceName,Value=api-service \
  --period 60 \
  --statistics Maximum \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```
**Fix:** Increase `memory` in the Task Definition. Profile the application's actual memory usage with Container Insights enabled.
**Prevention:** Enable Container Insights for memory and CPU monitoring. Set CloudWatch alarms at 85% memory utilisation to alert before OOM occurs.

**Mode 3: Service deployment hangs - unhealthy replacement tasks**
**Symptom:** `aws ecs update-service` runs but deployment never completes; old tasks keep running; new tasks launch but show as `UNHEALTHY` in ALB target group.
**Root Cause:** New container image has a bug causing health check failures. ECS won't drain old tasks until new tasks pass health checks.
**Diagnostic:**
```bash
# Check deployment status
aws ecs describe-services \
  --cluster my-cluster \
  --services api-service \
  --query 'services[0].deployments'

# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# Check new task logs
aws logs tail /ecs/api-service --follow
```
**Fix:** Roll back to the previous task definition revision: `aws ecs update-service --task-definition api-service:11`. ECS will drain the new broken tasks and restore the previous working version.
**Prevention:** Run integration tests against the new image in staging before updating production. Set deployment circuit breaker on the service to auto-rollback on repeated task failures.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Docker - ECS runs Docker containers; understanding images, registries, `Dockerfile`, and container lifecycle is essential.
- Containers - understand container isolation, namespaces, and networking before ECS networking (awsvpc mode) makes sense.
- AWS VPC Architecture Deep Dive - Fargate tasks run in VPC subnets; understanding security groups, private subnets, and VPC endpoints is prerequisite.

**Builds On This (learn these next):**
- AWS PrivateLink - ECR, Secrets Manager, and CloudWatch Logs require VPC interface endpoints for Fargate tasks in private subnets with no NAT.
- AWS Secrets Manager - inject secrets into containers via the `secrets` field in Task Definitions without environment variable exposure.
- Kubernetes (EKS) - the more complex alternative; if ECS becomes insufficient (custom schedulers, complex affinity rules), EKS is the natural progression.

**Alternatives / Comparisons:**
- Amazon EKS - Kubernetes on AWS; more complex, more ecosystem compatibility, better for organisations already using Kubernetes.
- AWS Lambda - serverless functions; better for event-driven, short-duration workloads; no container image management required.
- Docker Compose (local) - ECS has Compose file import capability; Docker Compose to ECS deployment is a supported migration path.

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS       | Container orchestration (ECS) with |
|                  | serverless compute option (Fargate) |
| PROBLEM IT SOLVES| EC2 management for containers,     |
|                  | container scheduling, scaling,       |
|                  | health replacement                  |
| KEY INSIGHT      | Task Role (app permissions) ≠       |
|                  | Execution Role (ECS infra setup)    |
| USE WHEN         | Microservices, APIs, batch jobs;   |
|                  | avoiding Kubernetes complexity      |
| AVOID WHEN       | GPU workloads; ultra-low latency    |
|                  | starts (use Lambda); full K8s eco   |
| TRADE-OFF        | Simpler than EKS but less flexible;|
|                  | Fargate costs more than EC2 at scale|
| ONE-LINER        | ecs:UpdateService --force-new-dep  |
| NEXT EXPLORE     | EKS, ECS Service Connect, Fargate  |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** ECS Fargate costs approximately 2–3× more per vCPU-hour than an equivalent EC2 instance. However, Fargate tasks scale in 30 seconds while EC2 Auto Scaling takes 3–5 minutes. For a microservice receiving burst traffic 20% of the time and steady traffic 80% of the time, what cost-architecture analysis determines whether Fargate, EC2, or a hybrid capacity provider strategy minimises total cost?

2. **(System Interaction)** A Fargate task in a private subnet needs to pull images from ECR, fetch secrets from Secrets Manager, and write logs to CloudWatch Logs - without internet access. Name the exact VPC interface endpoints required, the IAM permissions needed on the Execution Role, and how DNS resolution ensures the task uses private endpoints rather than public endpoints.

3. **(Scale)** Your ECS service runs 100 tasks during peak load. A canary deployment strategy requires 10% of traffic to go to the new version while 90% goes to the stable version. Describe the ECS Service, Task Definition, and ALB Target Group configuration that implements weighted traffic routing for this canary deployment.
