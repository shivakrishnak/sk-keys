---
version: 1
layout: default
title: "X-Ray"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /cloud-aws/x-ray/
id: AWS-065
category: "Cloud - AWS"
difficulty: "★★★"
depends_on: ["CloudWatch", "Lambda", "ECS / Fargate", "EKS"]
used_by: ["AWS Cost Optimization", "CloudWatch"]
related: ["CloudWatch", "Lambda", "ECS / Fargate", "EKS"]
tags: [aws, x-ray, tracing, distributed-tracing, observability, cloud]
---

# X-Ray

## ⚡ TL;DR

**AWS X-Ray** is distributed tracing for AWS applications. Traces end-to-end requests across Lambda, ECS, EKS, EC2, API Gateway, SQS, DynamoDB, and more. Generates service map (visual dependency graph). Identifies bottlenecks (slow segments), errors, and throttling across services. Complements CloudWatch (metrics/logs) as the tracing pillar. Also integrates with **CloudWatch Application Signals** for automatic instrumentation (no code changes required).

---

## 🔥 Problem This Solves

Request to `POST /orders` takes 2 seconds. Is it the API Gateway? Lambda cold start? DynamoDB write? RDS query? External payment API? CloudWatch metrics show "something is slow" but not where. X-Ray shows the full trace: 50ms API Gateway + 800ms Lambda init (cold start) + 20ms DynamoDB + 1100ms payment API call. Root cause: payment API is slow.

---

## 📘 Textbook Definition

AWS X-Ray is a service that collects data about requests that your application serves and provides tools to view, filter, and gain insights into that data to identify issues and opportunities for optimization. X-Ray provides a complete picture of requests as they travel through an application, correlating data across Lambda functions, EC2 instances, DynamoDB, SQS, SNS, and other services.

---

## ⏱️ 30 Seconds

```
Core concepts:
  Trace:    end-to-end record of a single request (collection of segments)
  Segment:  work done by one service/component (has subsegments)
  Subsegment: work within a segment (DB call, HTTP request, function call)
  Sampling: % of requests traced (default: 5% + 1 req/sec = cost control)

Trace header: X-Amzn-Trace-Id propagated across service calls
Service Map: visual graph of services + latency/error rates

Pricing:
  Free tier: 100K traces/month
  Recording: $5.00 per 1M traces recorded
  Retrieval: $0.50 per 1M traces retrieved
  CloudWatch traces: $1.00 per GB
```

---

## 🔩 First Principles

- **Sampling**: tracing ALL requests = high cost; default sampling = 5% (configurable); always trace errors
- **Trace context propagation**: `X-Amzn-Trace-Id` header; AWS services auto-propagate; custom code must forward
- **Active vs passive tracing**: Lambda/API Gateway: enable active tracing (X-Ray daemon auto-started); EC2/ECS: install X-Ray daemon sidecar
- **X-Ray SDK**: instrument code to add custom segments/subsegments; add annotations (indexed, searchable) and metadata (not indexed)
- **CloudWatch Application Signals**: zero-code-change auto-instrumentation via OpenTelemetry agent; newer and preferred

---

## 🧪 Thought Experiment

Microservices: API Gateway → Order Lambda → SQS → Fulfillment Lambda → DynamoDB + HTTP external. X-Ray service map: shows all nodes + latency % + error %. Find: Fulfillment Lambda p95=3s; click → trace waterfall. Segment breakdown: 2.5s is `external.api.call`. Add annotation `vendor=ShippingCo`. Filter traces: `annotation.vendor = "ShippingCo" AND responseTime > 2`. 100% of slow traces have this segment. Root cause: shipping API degraded. Fix: add timeout + circuit breaker.

---

## 🧠 Mental Model / Analogy

X-Ray is like a **GPS tracking system for package delivery**: each package (request) gets a tracking number (trace ID). Every time the package passes through a facility (service), it's scanned (segment recorded) with arrival time and departure time. The tracking website (service map) shows all facilities the package visited, how long it spent at each, and if any facility had issues (errors/throttling). Without tracking, you can only guess where the delay happened.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Enable X-Ray active tracing on Lambda and API Gateway. View service map. Click on a slow node → view traces → see segment waterfall.

**Level 2 - Practitioner**: Add X-Ray SDK to Java application. Create custom subsegments for important operations (DB calls, external API calls). Add annotations for filtering (`userId`, `orderId`, `environment`). Sampling rules: trace 100% of errors, 5% of successful requests.

**Level 3 - Advanced**: X-Ray groups: filter traces by expression (`annotation.environment = "prod" AND error = true`). Insights: automatic anomaly detection on trace patterns. X-Ray with SQS: producer adds trace header, consumer continues trace. Cross-account tracing: share X-Ray across accounts.

**Level 4 - Expert**: CloudWatch Application Signals: auto-instrumentation using ADOT (AWS Distro for OpenTelemetry) agent. SLOs in Application Signals: define latency/availability SLOs; CloudWatch monitors against them automatically. OpenTelemetry compatibility: X-Ray accepts OTLP traces (open standard); migrate from X-Ray SDK to OpenTelemetry SDK for vendor portability. X-Ray sampling rules via console: dynamic rules without code deployment (rule priority, reservoir, rate). Insights: X-Ray automatically detects root-cause segments for traces with faults - groups anomalous traces and shows common elements.

---

## ⚙️ How It Works

### X-Ray with Lambda (Terraform + Java)

```hcl
# Enable X-Ray active tracing on Lambda
resource "aws_lambda_function" "api" {
  # ... other config

  tracing_config {
    mode = "Active"  # PassThrough or Active
  }
}

# Enable X-Ray on API Gateway
resource "aws_api_gateway_stage" "prod" {
  # ...
  xray_tracing_enabled = true
}
```

### X-Ray SDK (Java Spring Boot)

```java
// Add X-Ray Spring Boot dependency
// io.opentelemetry.instrumentation:opentelemetry-spring-boot-starter
// or
// com.amazonaws:aws-xray-recorder-sdk-spring

@Configuration
@EnableXRay  // Spring Boot X-Ray auto-configuration
public class XRayConfig {

    @Bean
    public AWSXRayServletFilter xrayFilter() {
        return new AWSXRayServletFilter("my-service");
    }
}

// Custom subsegments for important operations
@Service
public class OrderService {

    public Order createOrder(CreateOrderRequest request) {
        // X-Ray automatically captures HTTP requests and AWS SDK calls
        // Add custom subsegment for business logic profiling

        return AWSXRay.createSubsegment("validateOrder", () -> {
            validateOrder(request);
            return null;
        }).andThen(() ->
            AWSXRay.createSubsegment("persistOrder", () -> {

                // Add annotations (indexed for filtering)
                AWSXRay.getCurrentSegment().putAnnotation("userId", request.getUserId());
                AWSXRay.getCurrentSegment().putAnnotation("orderType", request.getOrderType());

                // Add metadata (not indexed, for debugging)
                AWSXRay.getCurrentSegment().putMetadata("orderDetails",
                    Map.of("items", request.getItems().size(), "total", request.getTotal()));

                return orderRepository.save(buildOrder(request));
            })
        );
    }

    // X-Ray SDK automatically traces HTTP client calls
    // Use AWSXRayRestTemplate or enable Apache HTTP client tracing
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();  // X-Ray auto-instruments if using AWSXRay
    }
}
```

### CloudWatch Application Signals (Zero-Code Auto-Instrumentation)

```yaml
# ECS Task Definition: add OpenTelemetry agent as sidecar
# (CloudWatch Application Signals)
{
  "family": "my-app",
  "containerDefinitions":
    [
      {
        "name": "app",
        "image": "my-app:latest",
        "environment":
          [
            {
              "name": "JAVA_TOOL_OPTIONS",
              "value": "-javaagent:/otel/aws-opentelemetry-agent.jar",
            },
            {
              "name": "OTEL_EXPORTER_OTLP_ENDPOINT",
              "value": "http://localhost:4317",
            },
            { "name": "OTEL_AWS_APPLICATION_SIGNALS_ENABLED", "value": "true" },
            { "name": "OTEL_SERVICE_NAME", "value": "order-service" },
          ],
        "volumesFrom": [{ "sourceContainer": "init-agent" }],
      },
      {
        "name": "init-agent",
        "image": "public.ecr.aws/aws-observability/aws-otel-collector:latest",
        "essential": false,
      },
    ],
}
```

### Sampling Rules

```hcl
# Custom sampling rules
resource "aws_xray_sampling_rule" "errors" {
  rule_name      = "SampleAllErrors"
  priority       = 1     # lower = higher priority
  version        = 1
  reservoir_size = 10    # minimum traces/sec regardless of rate
  fixed_rate     = 1.0   # 100% sampling rate
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "*"
  resource_arn   = "*"

  # This rule only applies to requests that result in errors
  # Use X-Ray group filter: 'error = true OR fault = true'
}

resource "aws_xray_sampling_rule" "default" {
  rule_name      = "DefaultLowRate"
  priority       = 10000
  version        = 1
  reservoir_size = 5    # 5 traces/sec guaranteed
  fixed_rate     = 0.05 # 5% sampling for non-error requests
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "*"
  resource_arn   = "*"
}
```

---

## ⚖️ Comparison Table: X-Ray vs Alternatives

|                  | X-Ray                           | Jaeger              | Datadog APM      |
| ---------------- | ------------------------------- | ------------------- | ---------------- |
| **Integration**  | AWS native                      | Open source         | Any              |
| **Setup**        | SDK/auto-instrument             | Sidecar collector   | Agent            |
| **AWS services** | Native spans (Lambda, DDB, SQS) | Via exporters       | Via exporters    |
| **Service map**  | ✅                              | ✅                  | ✅               |
| **Cost**         | $5/million traces               | Infrastructure only | Per host/service |
| **Retention**    | 30 days                         | Configurable        | 15 days          |
| **OTLP support** | ✅                              | ✅                  | ✅               |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                     |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| "X-Ray traces all requests"              | Default sampling = 5% + 1 req/sec; configure sampling rules explicitly                                                      |
| "X-Ray works automatically without code" | Lambda/API GW: active tracing covers AWS service calls; custom code segments require SDK; Application Signals for zero-code |
| "X-Ray and CloudWatch are redundant"     | Complementary: CloudWatch for metrics/logs/alarms; X-Ray for request-level distributed traces                               |
| "X-Ray traces are retained forever"      | 30-day retention only; no long-term trace storage                                                                           |

---

## 🔗 Related Keywords

- [CloudWatch](/cloud-aws/cloudwatch/) - metrics and logs companion to X-Ray tracing
- [Lambda](/cloud-aws/lambda/) - enables X-Ray active tracing via single config
- [ECS / Fargate](/cloud-aws/ecs-fargate/) - X-Ray daemon as sidecar container

---

## 📌 Quick Reference Card

```bash
# Get service map (last 1 hour)
aws xray get-service-graph \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s)

# Get traces (errors only)
aws xray get-trace-summaries \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --filter-expression 'fault = true OR error = true'

# Get specific trace
aws xray batch-get-traces \
  --trace-ids 1-xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx

# List sampling rules
aws xray get-sampling-rules

# Get trace statistics
aws xray get-trace-graph \
  --trace-ids <trace-id>
```

---

## 🧠 Think About This

X-Ray's most underused feature is Annotations for filtering. Most teams enable X-Ray but never add annotations to their code, making traces useful only for individual debugging (click a slow trace) but not for pattern analysis (find all traces for user X, or all slow traces with error code Y). Adding `orderId`, `userId`, `customerId`, `tenantId`, and `featureFlag` as X-Ray annotations costs nothing (annotations are indexed), but enables a completely new class of investigation: "show me all traces for this customer in the last hour" or "compare p99 latency for requests with featureFlag=enabled vs disabled." This turns X-Ray from a debugging tool into a behavioral analysis tool. Implement annotations in your base service class so they're automatically included in every trace without developer effort.
