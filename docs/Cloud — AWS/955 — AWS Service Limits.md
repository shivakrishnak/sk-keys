---
layout: default
title: "AWS Service Limits"
parent: "Cloud — AWS"
nav_order: 955
permalink: /cloud-aws/aws-service-limits/
number: "0955"
category: "Cloud — AWS"
difficulty: "★★★"
depends_on: ["AWS Global Infrastructure", "EC2", "Lambda"]
used_by: ["Well-Architected Framework"]
related:
  [
    "Well-Architected Framework",
    "Auto Scaling Groups",
    "Lambda",
    "DynamoDB",
    "SQS",
  ]
tags: [aws, service-limits, quotas, throttling, limits, scaling, cloud]
---

# AWS Service Limits

## ⚡ TL;DR

AWS Service Limits (now called **Service Quotas**) are per-account, per-region caps on how much of an AWS resource you can use. Default limits exist for every service; many can be increased via the **Service Quotas console** or support cases. Critical to know: soft limits (can be raised) vs hard limits (cannot be raised), AWS Lambda concurrency (default 1,000/region), EC2 vCPU limits, DynamoDB table limits, API Gateway throttling. Always request increases **before** you need them.

---

## 🔥 Problem This Solves

Teams hit service limits at the worst possible time — during a product launch, a traffic spike, or a migration. "LimitExceededException" or throttling errors break production. Understanding which limits matter for your workload and proactively requesting increases prevents embarrassing outages caused by AWS quota exhaustion.

---

## 📘 Textbook Definition

AWS Service Quotas are defined limits that govern the number of resources or calls that can be made per account and per AWS Region. AWS sets these defaults to prevent abuse and maintain service stability. Soft limits can be increased by submitting a Service Quotas increase request; hard limits represent absolute technical or policy caps that cannot be modified.

---

## ⏱️ 30 Seconds

```
Critical limits (check before scaling):

Lambda:
  - Concurrent executions: 1,000/region (soft, can increase)
  - Reserved concurrency: 900 available (100 for function throttling)
  - Deployment package: 50MB zipped, 250MB unzipped
  - /tmp storage: 512MB (can increase to 10GB)

EC2:
  - vCPUs per region: varies by instance family (default ~32-96)
  - Elastic IPs: 5 per region (soft)

DynamoDB:
  - Tables per region: 2,500 (soft)
  - Partition throughput: ~3,000 RCU / 1,000 WCU per partition

SQS:
  - Max message size: 256 KB
  - Message retention: 14 days max

API Gateway:
  - Throttle limit: 10,000 RPS per account/region (soft)
  - Burst: 5,000

RDS:
  - DB instances: 40 per region (soft)
  - Snapshots: 100 per region (soft)
```

---

## 🔩 First Principles

- **Limits exist for service stability**: prevent one customer from using all capacity; protect service reliability for all customers
- **Soft vs hard**: soft = increase by request; hard = physical/architectural constraint (e.g., max SQS message size 256KB is hard)
- **Per-account per-region**: most limits are account+region scoped; hitting limit in us-east-1 doesn't affect us-west-2
- **Limits apply independently**: Lambda concurrent executions limit applies regardless of whether you run 1 function or 100
- **Service Quotas API**: programmatically check and request quota increases via AWS SDK or CLI
- **Limits in steady-state vs burst**: many limits have both sustained rate and burst capacity (e.g., API Gateway throttling: 10,000 RPS steady + 5,000 burst)

---

## 🧪 Thought Experiment

Launch day: 100K users sign up simultaneously. Each signup triggers a Lambda. Lambda concurrent executions: 100K concurrent → at default 1,000 limit = 99K throttle errors. Users see "Service Unavailable." If limit increase had been requested to 10,000 before launch → 90K throttled. At 50,000 → 50K throttled. There's no way to handle this without a limit increase + architecture design (SQS buffer to smooth the spike). Proper pre-launch checklist: identify top bottleneck limits → request increases → verify → test with load testing.

---

## 🧠 Mental Model / Analogy

AWS Service Limits are like **highway lane limits**: a highway designed for 10,000 cars per hour can't suddenly handle 100,000 cars — you'd need to build more lanes (request a limit increase) or use alternate routes (architecture changes: SQS queue, pagination). Some limits are permanent road designs (hard limits); others are just current lane count (soft limits). Planning for growth means increasing capacity before the traffic arrives, not after you're gridlocked.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Know the most common limits (Lambda concurrency, EC2 vCPUs, API Gateway throttling). Check current limits in Service Quotas console. Request increases via console or support case. Set up CloudWatch alarms for limit approaching.

**Level 2 — Practitioner**: Service Quotas Dashboard: view all limits + current usage + percentage utilized. Automatic request limit increase where available (Lambda concurrent executions supports automatic increase requests). Trusted Advisor checks: "Service Limits" category shows limits approaching 80% utilization. Architecture to work within limits: SQS buffer before Lambda to prevent concurrency exhaustion.

**Level 3 — Advanced**: Service Quotas API: programmatically query limits + request increases. Bulk limit increases for new accounts/regions. AWS Organizations: quota request propagation. Design for throttling: exponential backoff + jitter for all AWS SDK calls (built into AWS SDK retry logic). Reserve concurrency per Lambda function to prevent noisy neighbor within account.

**Level 4 — Expert**: Multi-region architectures as limit bypass: if one region's limit isn't enough, distribute across regions. Account-per-workload (AWS Organizations): separate accounts give separate limit pools; critical microservices in dedicated accounts avoid cross-service limit sharing. DynamoDB partition limits: understand hot partition exhaustion (not a requestable limit change); solution is partition key design, write sharding, or DAX caching. API Gateway custom domain + usage plans: per-customer throttling so one customer can't exhaust account-level limits. Lambda container images: 10GB image size vs 250MB zip — different size limits.

---

## ⚙️ How It Works

### Check Service Quotas (AWS CLI + SDK)

```bash
# List all Lambda quotas
aws service-quotas list-service-quotas \
  --service-code lambda \
  --query 'Quotas[].{Name:QuotaName,Value:Value,Adjustable:Adjustable}' \
  --output table

# Get specific quota (Lambda concurrent executions)
aws service-quotas get-service-quota \
  --service-code lambda \
  --quota-code L-B99A9384

# Get current usage for a quota
aws service-quotas get-aws-default-service-quota \
  --service-code lambda \
  --quota-code L-B99A9384

# Request a quota increase
aws service-quotas request-service-quota-increase \
  --service-code lambda \
  --quota-code L-B99A9384 \
  --desired-value 10000

# Check status of increase request
aws service-quotas list-requested-service-quota-changes-by-service \
  --service-code lambda \
  --query 'RequestedQuotas[].{Quota:QuotaName,Status:Status,Desired:DesiredValue}'

# Check Trusted Advisor service limit checks
aws support describe-trusted-advisor-check-result \
  --check-id eW7HH0l7J9  # Service Limits check ID

# Get EC2 vCPU limits by instance family
aws service-quotas list-service-quotas \
  --service-code ec2 \
  --query 'Quotas[?contains(QuotaName, `vCPU`)].{Name:QuotaName,Value:Value}'
```

### Lambda Concurrency Management (Java)

```java
// Configure reserved concurrency per function via Terraform
resource "aws_lambda_function_event_invoke_config" "payment" {
  function_name = aws_lambda_function.payment.function_name

  maximum_retry_attempts = 2
  maximum_event_age_in_seconds = 60
}

// Reserved concurrency: protect this function from being throttled
resource "aws_lambda_provisioned_concurrency_config" "payment" {
  function_name                  = aws_lambda_function.payment.function_name
  qualifier                      = aws_lambda_alias.live.name
  provisioned_concurrent_executions = 50  # always warm, never cold start
}

// Reserve concurrency limit: prevent this function from consuming all Lambda concurrency
resource "aws_lambda_function" "payment" {
  function_name    = "payment-processor"
  reserved_concurrent_executions = 200  # max 200 concurrent, protects other functions
  // rest of config...
}
```

### SQS Buffer Pattern (Protect Lambda from Concurrency Limit)

```java
// Architecture: API → SQS → Lambda (bounded concurrency)
// Instead of direct Lambda invocation → SQS absorbs burst

@RestController
public class SignupController {

    @Autowired
    private SqsTemplate sqsTemplate;

    @PostMapping("/signup")
    public ResponseEntity<Void> signup(@RequestBody SignupRequest req) {
        // Never call Lambda directly for bursty workloads
        // SQS absorbs the burst; Lambda processes at its concurrency limit rate
        sqsTemplate.send("signup-queue", req);
        return ResponseEntity.accepted().build();
    }
}

// Lambda processes from SQS with batching
@SqsListener(value = "signup-queue", acknowledgementMode = SqsAcknowledgementMode.ON_SUCCESS)
public void processSignup(SignupRequest request) {
    signupService.process(request);
}

// SQS batch size = 10 + Lambda concurrency = 500
// Effective throughput = 5,000 signups/sec without hitting 1,000 concurrency limit
// because each Lambda invocation processes 10 messages
```

### CloudWatch Alarms for Limit Monitoring

```hcl
# Alert when Lambda concurrent executions > 800 (80% of 1,000 default)
resource "aws_cloudwatch_metric_alarm" "lambda_concurrency" {
  alarm_name          = "lambda-concurrency-limit-warning"
  alarm_description   = "Lambda concurrent executions approaching limit"

  namespace           = "AWS/Lambda"
  metric_name         = "ConcurrentExecutions"
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 5
  threshold           = 800
  comparison_operator = "GreaterThanThreshold"

  alarm_actions = [aws_sns_topic.ops_alerts.arn]
}

# Alert when API Gateway throttle errors > 0
resource "aws_cloudwatch_metric_alarm" "api_throttle" {
  alarm_name          = "api-gateway-throttle"
  alarm_description   = "API Gateway throttling requests"

  namespace           = "AWS/ApiGateway"
  metric_name         = "4XXError"
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 10
  comparison_operator = "GreaterThanThreshold"
}
```

---

## ⚖️ Comparison Table: Common Soft Limits

| Service            | Limit                     | Default       | Request Increase? |
| ------------------ | ------------------------- | ------------- | ----------------- |
| **Lambda**         | Concurrent executions     | 1,000/region  | Yes               |
| **Lambda**         | /tmp storage              | 512 MB        | Yes (to 10 GB)    |
| **EC2**            | On-Demand vCPUs (general) | 32–96/region  | Yes               |
| **EC2**            | Elastic IPs               | 5/region      | Yes               |
| **API Gateway**    | Throttle (REST API)       | 10,000 RPS    | Yes               |
| **API Gateway**    | Burst                     | 5,000 RPS     | Yes               |
| **SQS**            | Max message size          | 256 KB        | No (hard limit)   |
| **RDS**            | DB instances              | 40/region     | Yes               |
| **DynamoDB**       | Tables                    | 2,500/region  | Yes               |
| **CloudFormation** | Stacks                    | 2,000/region  | Yes               |
| **VPC**            | VPCs per region           | 5             | Yes               |
| **SGs**            | Per VPC                   | 2,500         | Yes               |
| **IAM**            | Roles                     | 1,000/account | Yes               |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                            |
| ---------------------------------------- | ---------------------------------------------------------------------------------- |
| "We won't hit limits at our scale"       | Lambda concurrency 1,000 is per region; one viral event can exhaust it             |
| "All limits can be raised"               | Hard limits are architectural (SQS 256KB, Lambda 15min timeout) — cannot be raised |
| "Requesting a limit increase is instant" | Increases may take hours to days for non-standard increases (large increases)      |
| "Limits are global"                      | Most limits are per-account per-region; multi-account/multi-region = more capacity |

---

## 🔗 Related Keywords

- [Well-Architected Framework](/cloud-aws/well-architected-framework/) — Reliability pillar: understand limits
- [Lambda](/cloud-aws/lambda/) — concurrency limits and reserved concurrency
- [API Gateway (AWS)](/cloud-aws/api-gateway-aws/) — throttling and rate limits

---

## 📌 Quick Reference Card

```bash
# Quick: get all lambda quotas
aws service-quotas list-service-quotas --service-code lambda --output table

# Check if Lambda concurrency limit is too low
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --statistics Maximum \
  --start-time 2024-01-01T00:00:00 \
  --end-time 2024-01-08T00:00:00 \
  --period 3600 \
  --query 'sort_by(Datapoints, &Maximum)[-1].Maximum'

# List all services with configurable quotas
aws service-quotas list-services \
  --query 'Services[].{Name:ServiceName,Code:ServiceCode}' \
  --output table

# Check throttle metrics for API Gateway
aws cloudwatch get-metric-data \
  --metric-data-queries '[{"Id":"throttles","MetricStat":{"Metric":{"Namespace":"AWS/ApiGateway","MetricName":"Count","Dimensions":[{"Name":"ApiName","Value":"my-api"}]},"Period":60,"Stat":"Sum"}}]' \
  --start-time 2024-01-01T00:00:00 \
  --end-time 2024-01-08T00:00:00
```

---

## 🧠 Think About This

The sneakiest limit that catches production teams is the **DynamoDB partition throughput limit**. Unlike most AWS limits, it cannot be increased via Service Quotas. Each partition supports ~3,000 RCU and 1,000 WCU. If your DynamoDB partition key design creates a hot partition (one key gets 80% of traffic), you'll hit this limit regardless of how much provisioned/on-demand capacity you've set. This manifests as `ProvisionedThroughputExceededException` on specific items even when overall table throughput is not exceeded. Solutions: (1) use high-cardinality partition keys (UUID, not user status like "active/inactive"); (2) write sharding: append random suffix to key (user#1 → user#1_0 through user#1_9), distribute writes across 10 partitions, aggregate on read; (3) DynamoDB Accelerator (DAX) for read-heavy hot items (moves reads to in-memory cache, eliminates partition read pressure); (4) SQS buffer + batch writes for write-heavy patterns. This is a design constraint that must be addressed in schema design, not just at runtime.
