---
version: 1
layout: default
title: "Lambda"
parent: "Cloud - AWS"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/cloud-aws/lambda/
id: AWS-045
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on: ["IAM (Identity and Access Management)", "VPC", "SQS", "SNS"]
used_by: ["API Gateway (AWS)", "ECS / Fargate", "AWS Cost Optimization"]
related: ["API Gateway (AWS)", "SQS", "SNS", "Kinesis", "ECS / Fargate"]
tags: [aws, lambda, serverless, functions, faas, event-driven, cloud]
---

## ⚡ TL;DR

**Lambda** is AWS's serverless function execution. Write code; AWS runs it on demand - zero server management. Triggered by 200+ event sources (API Gateway, SQS, S3, DynamoDB Streams, Kinesis, SNS, EventBridge). Scales automatically from zero to thousands of concurrent executions. Billing: per invocation ($0.20/million) + duration ($0.0000166667/GB-second). Cold starts are the main tradeoff.

---

## 🔥 Problem This Solves

Traditional EC2: pay 24/7 even when idle. For event-driven, sporadic workloads (file processing, notifications, scheduled jobs, API handlers), Lambda pays only when code runs. Auto-scaling without configuration. No patching, no capacity planning.

---

## 📘 Textbook Definition

AWS Lambda is a serverless compute service that runs code in response to events. Lambda manages the compute infrastructure, automatically scaling from zero to thousands of concurrent instances. Code is packaged as a function (deployment package or container image). Execution environments are ephemeral; state must be stored externally.

---

## ⏱️ 30 Seconds

```
Limits:
  Max execution time:  15 minutes
  Memory:              128MB to 10GB
  Ephemeral storage:   512MB to 10GB (/tmp)
  Deployment size:     50MB zip, 250MB unzipped, 10GB
    container
  Concurrent exec:     1000 default (regional, soft limit)

Pricing (x86):
  Requests:  $0.20/million
  Duration:  $0.0000166667 per GB-second
  Free tier: 1M requests + 400,000 GB-seconds/month

Cold start:
  First invocation (or after idle): download + init code =
    extra latency
  Java: 1-5s; Node.js/Python: <1s
  Mitigation: Provisioned Concurrency, SnapStart (Java 11+)
```

---

## 🔩 First Principles

- **Stateless by design**: each invocation gets a fresh environment; no shared memory between invocations
- **Execution environment reuse**: AWS reuses warm containers (global scope init runs once); don't rely on it
- **IAM execution role**: Lambda runs with a role; defines what AWS services it can access
- **Event source mapping**: Lambda polls SQS/Kinesis/DynamoDB Streams; other triggers (S3, SNS) push to Lambda
- **Concurrency**: each concurrent invocation uses one execution environment; scale by parallelism not throughput

---

## 🧪 Thought Experiment

Image processing: user uploads photo to S3. S3 event triggers Lambda. Lambda: read original, resize to 3 thumbnails, write to S3, update DynamoDB record. Cost: 1 invocation × 3s × 1GB = $0.00005. At 100K uploads/day: $5/day. EC2 equivalent for same: m5.large 24/7 = $75/day. Lambda wins 15x on cost for sporadic workloads.

---

## 🧠 Mental Model / Analogy

Lambda is a **vending machine**: you press a button (event), the machine does something (function runs), you get a result. The machine is always ready but costs nothing when idle. 1000 people press buttons simultaneously: 1000 machines appear instantly. Contrast with EC2 (hiring a chef full-time): always ready, always being paid, whether or not anyone orders food.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Write a handler function. Deploy to Lambda. Configure trigger (e.g., S3 bucket event). Test invocation. Monitor in CloudWatch Logs.

**Level 2 - Practitioner**: Environment variables for configuration. Layers: shared libraries and dependencies (up to 5 layers, 250MB). Lambda with VPC: can access RDS/ElastiCache in private subnets (adds ~100ms cold start). RDS Proxy: pool connections (Lambda creates new connection per cold start without proxy). Lambda Destinations: route async invocation results to SQS/SNS/EventBridge/Lambda.

**Level 3 - Advanced**: Lambda SnapStart (Java 11+): snapshot initialized execution environment → cold start from snapshot (~1s vs 5s for Java). Provisioned Concurrency: pre-warm N environments; zero cold starts for that capacity. Lambda Power Tuning (open source): find optimal memory/cost tradeoff. Lambda Container Images: package as OCI image (up to 10GB); use for complex dependencies.

**Level 4 - Expert**: Lambda concurrency limits: reserved concurrency (cap function max); provisioned concurrency (pre-warm); account limit (1000 default, increase via Support). Recursive loop detection (2023): Lambda detects infinite recursion and stops. Lambda Extensions: third-party tooling (APM, secrets) injected alongside function. ARM64 (Graviton2): 20% cheaper than x86 for same compute + often faster. Lambda SnapStart: invoke published version; SNAPSHOT_RESTORE_ON_RESUME lifecycle hook for state restoration. Async invocation retries: automatic 2 retries on function error; use Destinations for failure handling. Cold start anatomy: download code, init execution env, run init code, run handler. Only handler runs on warm invoke; init code runs once per environment.

---

## ⚙️ How It Works

---

### Lambda Function (Java Spring Boot via Spring Cloud Function)

```java
// Spring Cloud Function: adapt Spring Boot app to Lambda
// Dependency: spring-cloud-function-adapter-aws

@SpringBootApplication
public class OrderProcessorApplication {

    // Function as Spring bean: auto-adapted to Lambda handler
    @Bean
    public Function<OrderEvent, ProcessingResult> processOrder() {
        return event -> {
            log.info("Processing order {}", event.getOrderId());

            // Validate
            if (event.getOrderId() == null) {
                throw new IllegalArgumentException(
                    "Order ID required");
            }

            // Process
            Order order =
                orderService.processOrder(event.getOrderId());

            return ProcessingResult.builder()
                .orderId(order.getId())
                .status(order.getStatus())
                .build();
        };
    }

    // Lambda initialization code (runs once per cold start, reused on
    // warm invoke)
    // Spring ApplicationContext is initialized here
}
```

---

### Lambda Terraform

```hcl
# Lambda Function
resource "aws_lambda_function" "order_processor" {
  function_name    = "order-processor"

  # Package options: zip or container image
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  handler =
      "org.springframework.cloud.function.adapter.aws.FunctionInvoker"
  runtime = "java21"

  # Performance
  memory_size  = 1024       # 1GB
  timeout      = 300        # 5 minutes
  architectures = ["arm64"] # Graviton2: cheaper

  # Execution role
  role = aws_iam_role.lambda_exec.arn

  # VPC config (for RDS access)
  vpc_config {
    subnet_ids         = [aws_subnet.private_a.id,
        aws_subnet.private_b.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  # Environment variables
  environment {
    variables = {
      SPRING_PROFILES_ACTIVE = "prod"
      DB_HOST                = aws_rds_cluster.main.endpoint
      REDIS_ENDPOINT         = aws_elasticache_replication_group.main.primary_endpoint_address
    }
  }

  # SnapStart for Java (reduces cold start)
  snap_start {
    apply_on = "PublishedVersions"
  }

  # CloudWatch Logs
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.lambda.name
  }
}

# Provisioned Concurrency (zero cold starts for N concurrent requests)
resource "aws_lambda_provisioned_concurrency_config" "main" {
  function_name                  =
      aws_lambda_function.order_processor.function_name
  qualifier                      = aws_lambda_alias.live.name
  provisioned_concurrent_executions = 10  # keep 10 warm
}

# SQS Event Source Mapping
resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn = aws_sqs_queue.orders.arn
  function_name    = aws_lambda_function.order_processor.arn
  batch_size       = 10

  # Scale based on queue depth
  scaling_config {
    maximum_concurrency = 100  # limit max concurrent Lambda instances
  }

  # Report batch item failures (partial success)
  function_response_types = ["ReportBatchItemFailures"]
}
```

---

### Lambda IAM Execution Role

```hcl
resource "aws_iam_role" "lambda_exec" {
  name = "order-processor-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_permissions" {
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage", "sqs:DeleteMessage",
          "sqs:GetQueueAttributes", "sqs:ChangeMessageVisibility"
        ]
        Resource = aws_sqs_queue.orders.arn
      },
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.app.arn}/*"
      },
      {
        Effect = "Allow"
        Action = ["logs:CreateLogGroup", "logs:CreateLogStream",
            "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# VPC execution requires ENI permissions
resource "aws_iam_role_policy_attachment" "vpc" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
```

---

## ⚖️ Comparison Table: Lambda vs ECS Fargate vs EC2

|                  | Lambda                    | ECS Fargate              | EC2                 |
| ---------------- | ------------------------- | ------------------------ | ------------------- |
| **Management**   | Zero                      | Minimal                  | Full                |
| **Cold start**   | Yes (50ms-5s)             | Slower startup           | N/A                 |
| **Max duration** | 15 min                    | Unlimited                | Unlimited           |
| **Scaling**      | Instant (concurrency)     | ~1-2 min                 | ~3-5 min            |
| **State**        | Stateless                 | Stateless (optional)     | Stateful            |
| **Cost (idle)**  | $0                        | $0                       | $$$                 |
| **Use case**     | Event-driven, short tasks | Long-running, containers | Full control needed |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------- |
| "Lambda always cold starts"         | Warm containers are reused; only first invocation after idle cold starts        |
| "Lambda can't run Spring Boot"      | Spring Boot + Spring Cloud Function works; use SnapStart to reduce cold start   |
| "Lambda can't access VPC resources" | Lambda supports VPC config for RDS/ElastiCache access                           |
| "Lambda concurrency = threads"      | Each concurrent invocation = separate execution environment (not a thread pool) |

---

## 🔗 Related Keywords

- [API Gateway (AWS)](/cloud-aws/api-gateway-aws/) - HTTP trigger for Lambda
- [SQS](/cloud-aws/sqs/) - queue-based trigger
- [ECS / Fargate](/cloud-aws/ecs-fargate/) - container alternative for long-running tasks

---

## 📌 Quick Reference Card

```bash
# Deploy Lambda from zip
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip

# Invoke function
aws lambda invoke \
  --function-name my-function \
  --payload '{"key":"value"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# Check logs (last 30 minutes)
aws logs tail /aws/lambda/my-function \
  --since 30m --follow

# List all Lambda functions
aws lambda list-functions \
  --query 'Functions[].{Name:FunctionName,Runtime:Runtime,
      Memory:MemorySize}'

# Check concurrent executions
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 60 --statistics Maximum
```

---

## 🧠 Think About This

Lambda cold starts matter, but most teams over-optimize for them. The typical customer journey through a web app: page load (served from CloudFront, zero Lambda), user searches (5-20ms ElastiCache hit, 100-200ms on miss), user clicks (few hundred ms per API call). A 1-second Lambda cold start is catastrophic for a login endpoint, but irrelevant for a nightly report job. Target your cold start mitigation: Provisioned Concurrency for the p99 latency-sensitive paths only (not all functions). For Java Spring Boot, SnapStart gives ~80% of cold start reduction for free (just publish a version). Lambda Power Tuning is worth running on every Lambda function - often 512MB is faster AND cheaper than 256MB because the function finishes in half the time despite twice the memory cost (duration cost dominates request cost).
