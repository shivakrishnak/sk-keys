---
layout: default
title: "CloudWatch"
parent: "Cloud — AWS"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /cloud-aws/cloudwatch/
id: AWS-058
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on:
  ["AWS Global Infrastructure", "IAM (Identity and Access Management)"]
used_by: ["Lambda", "ECS / Fargate", "EKS", "RDS", "X-Ray"]
related: ["X-Ray", "Lambda", "ECS / Fargate", "SNS", "AWS Cost Optimization"]
tags: [aws, cloudwatch, monitoring, logs, metrics, alarms, observability, cloud]
---

# CloudWatch

## ⚡ TL;DR

**CloudWatch** is AWS's monitoring and observability platform. Three pillars: **Metrics** (time-series data from AWS services + custom), **Logs** (centralized log storage, query with Logs Insights), **Alarms** (metric thresholds → SNS/Auto Scaling/Lambda actions). Also: Container Insights, Lambda Insights, Application Signals. The unified observability layer for all AWS services.

---

## 🔥 Problem This Solves

You need to know: Is my application healthy? What's my database CPU? Are my Lambda functions erroring? CloudWatch automatically collects metrics from 150+ AWS services. You add custom metrics and logs. Set alarms to alert on anomalies. No separate monitoring infrastructure to manage.

---

## 📘 Textbook Definition

Amazon CloudWatch is a monitoring and observability service that provides data and actionable insights for AWS, hybrid, and on-premises applications and infrastructure resources. CloudWatch collects monitoring and operational data in the form of logs, metrics, and events, providing a unified view of operational health and enabling resource optimization.

---

## ⏱️ 30 Seconds

```
CloudWatch Metrics:
  Namespace: service name (AWS/EC2, AWS/RDS, etc.)
  Metric name: e.g., CPUUtilization
  Dimensions: filters (InstanceId=i-xxx)
  Resolution: standard (1min), high-resolution (1s, extra cost)
  Retention: 3hr (1-sec), 15days (1-min), 63days (5-min), 455days (1-hr)

CloudWatch Logs:
  Log Group: collection of log streams (e.g., /aws/lambda/my-function)
  Log Stream: sequence of log events from one source
  Retention: 1 day to never expire (set explicitly)
  Logs Insights: query language for log analysis

CloudWatch Alarms:
  Threshold: metric > X for N periods → alarm state
  Actions: SNS notification, Auto Scaling, EC2 recovery
  States: OK, ALARM, INSUFFICIENT_DATA
```

---

## 🔩 First Principles

- **Pull model for EC2**: CloudWatch Agent must be installed to collect memory/disk metrics (not automatic)
- **Custom metrics**: `PutMetricData` API; max 1000 metric dimensions per namespace; high-res = $0.30/metric-month
- **Log Insights**: SQL-like query language; `fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20`
- **Metric Math**: create derived metrics (error rate = errors/requests) without storing new metrics
- **CloudWatch Synthetics**: Canary scripts that continuously test URLs/APIs (like Datadog Synthetics)
- **Composite alarms**: AND/OR logic across multiple alarms → reduce alert noise

---

## 🧪 Thought Experiment

SLA: 99.9% uptime, p99 < 500ms. CloudWatch: custom metric for request duration from Lambda (histogram). Alarm: p99 > 500ms for 3 consecutive minutes → SNS → PagerDuty. Auto Scaling: alarm on CPU > 70% → scale out ECS service. Logs Insights query on `/aws/lambda/my-function`: `filter @message like /Exception/ | stats count() by bin(5m)` → spike at 14:30 → correlated with deployment. Root cause in 5 minutes.

---

## 🧠 Mental Model / Analogy

CloudWatch is the **hospital monitoring system**: all patients (AWS resources) have sensors automatically attached (metrics). Nurses (alarms) watch the monitors and page doctors (SNS/PagerDuty) when values exceed thresholds. Medical records (logs) capture everything happening. Specialists (Logs Insights) can query records to diagnose: "show me all instances where heart rate exceeded 120 in the last 6 hours."

---

## 📶 Gradual Depth

**Level 1 — Beginner**: View metrics for EC2/RDS/Lambda in console. Create alarm on CPU utilization with SNS email notification. View Lambda logs in Logs console. Set log retention (avoid infinite storage costs).

**Level 2 — Practitioner**: CloudWatch Agent: collect OS metrics (memory, disk) from EC2. Structured logging (JSON) for effective Logs Insights queries. Custom dashboards: combine metrics from multiple services. Metric Math: compute error rates, percentiles from raw counters.

**Level 3 — Advanced**: CloudWatch Logs Insights: `stats avg(duration) by bin(1h)` for latency trends. CloudWatch Container Insights: ECS/EKS container-level CPU/memory. CloudWatch Lambda Insights: cold start, initialization duration, memory utilization per invocation. Embedded Metrics Format (EMF): write metrics as structured JSON logs → CloudWatch auto-extracts them as metrics (avoid PutMetricData API calls).

**Level 4 — Expert**: CloudWatch Anomaly Detection: ML-based expected range → alarm when metric deviates from expected pattern (adapts to hourly/daily patterns automatically). CloudWatch Cross-Account Observability (CloudWatch OAM): centralize metrics/logs from many AWS accounts into an observability account. CloudWatch Logs subscription filters: stream logs in real-time to Lambda, Kinesis, or Firehose. Contributor Insights: analyze top N contributors to high metrics (e.g., top 10 IP addresses causing 4xx errors). CloudWatch Application Signals: auto-instrumented RED metrics (Requests, Errors, Duration) + service map from SDK-instrumented apps.

---

## ⚙️ How It Works

### Custom Metrics (Java Spring Boot)

```java
// Option 1: PutMetricData API (explicit)
@Service
public class OrderMetrics {

    private final CloudWatchClient cloudWatch;

    @Value("${app.name}")
    private String appName;

    public void recordOrderProcessingTime(String orderId, long durationMs, boolean success) {
        List<MetricDatum> metrics = List.of(
            MetricDatum.builder()
                .metricName("OrderProcessingDuration")
                .unit(StandardUnit.MILLISECONDS)
                .value((double) durationMs)
                .dimensions(
                    Dimension.builder().name("Service").value(appName).build(),
                    Dimension.builder().name("Success").value(String.valueOf(success)).build()
                )
                .storageResolution(60)  // 1-minute resolution
                .build(),
            MetricDatum.builder()
                .metricName("OrdersProcessed")
                .unit(StandardUnit.COUNT)
                .value(1.0)
                .dimensions(
                    Dimension.builder().name("Service").value(appName).build()
                )
                .build()
        );

        cloudWatch.putMetricData(PutMetricDataRequest.builder()
            .namespace("MyApp/Orders")
            .metricData(metrics)
            .build());
    }
}

// Option 2: Embedded Metrics Format (EMF) - more efficient
// Writes metrics as structured JSON logs → CW extracts metrics
// Use AWS Lambda Powertools (recommended)
@Service
public class OrderService {

    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);

    public void processOrder(Order order) {
        long startTime = System.currentTimeMillis();
        boolean success = false;

        try {
            // ... process order
            success = true;
        } finally {
            long duration = System.currentTimeMillis() - startTime;

            // Structured log with metrics embedded (EMF format for Lambda)
            logger.info("""
                {"_aws":{"Timestamp":{},"CloudWatchMetrics":[{"Namespace":"MyApp/Orders","Dimensions":[["Service"]],"Metrics":[{"Name":"OrderDuration","Unit":"Milliseconds"},{"Name":"OrderSuccess","Unit":"Count"}]}]},"Service":"OrderService","OrderDuration":{},"OrderSuccess":{}}
                """,
                System.currentTimeMillis(), duration, success ? 1 : 0);
        }
    }
}
```

### CloudWatch Alarms (Terraform)

```hcl
# SNS topic for alarm notifications
resource "aws_sns_topic" "alarms" {
  name = "production-alarms"
}

# P99 latency alarm for Lambda
resource "aws_cloudwatch_metric_alarm" "lambda_p99" {
  alarm_name          = "lambda-p99-latency-high"
  alarm_description   = "P99 Lambda duration exceeds 500ms"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  threshold           = 500
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "p99"
    expression  = "PERCENTILE(m1, 99)"
    label       = "P99 Latency"
    return_data = true
  }

  metric_query {
    id = "m1"
    metric {
      namespace   = "AWS/Lambda"
      metric_name = "Duration"
      dimensions  = { FunctionName = "my-function" }
      period      = 60
      stat        = "SampleCount"
    }
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
  ok_actions    = [aws_sns_topic.alarms.arn]
}

# Error rate alarm using Metric Math
resource "aws_cloudwatch_metric_alarm" "error_rate" {
  alarm_name          = "lambda-error-rate-high"
  alarm_description   = "Lambda error rate > 1%"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 1  # 1%
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "error_rate"
    expression  = "errors/invocations*100"
    label       = "Error Rate %"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      namespace   = "AWS/Lambda"
      metric_name = "Errors"
      dimensions  = { FunctionName = "my-function" }
      period      = 60
      stat        = "Sum"
    }
  }

  metric_query {
    id = "invocations"
    metric {
      namespace   = "AWS/Lambda"
      metric_name = "Invocations"
      dimensions  = { FunctionName = "my-function" }
      period      = 60
      stat        = "Sum"
    }
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# Composite alarm (reduce noise)
resource "aws_cloudwatch_composite_alarm" "critical" {
  alarm_name = "production-critical"
  alarm_description = "Multiple critical issues simultaneously"

  alarm_rule = join(" AND ", [
    "ALARM(${aws_cloudwatch_metric_alarm.lambda_p99.alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.error_rate.alarm_name})",
  ])

  alarm_actions = [aws_sns_topic.pagerduty.arn]  # only page if BOTH alarms trigger
}

# Log group with retention
resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/lambda/my-function"
  retention_in_days = 30  # critical: set retention or pay forever

  kms_key_id = aws_kms_key.logs.arn
}
```

### Logs Insights Queries

```
# Find errors in last 1 hour
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

# Lambda cold starts
fields @timestamp, @type, @duration, @initDuration
| filter @type = "REPORT"
| stats count(@initDuration) as coldStarts, avg(@initDuration) as avgInitMs by bin(1h)

# P99/P95/P50 latency over time
fields @timestamp, @duration
| filter @type = "REPORT"
| stats pct(@duration, 50) as p50, pct(@duration, 95) as p95, pct(@duration, 99) as p99 by bin(5m)

# Top exceptions
fields @timestamp, @message
| filter @message like /Exception/
| parse @message "Exception: *\n" as exceptionType
| stats count() as occurrences by exceptionType
| sort occurrences desc
| limit 10
```

---

## ⚖️ Comparison Table: CloudWatch vs Other Monitoring Tools

|                  | CloudWatch          | Datadog         | Prometheus+Grafana |
| ---------------- | ------------------- | --------------- | ------------------ |
| **Integration**  | Native AWS          | AWS + any       | Any (pull model)   |
| **Setup**        | Zero (AWS services) | Agent needed    | Scrape config      |
| **Cost**         | Pay-per-use         | Per host/metric | Open source        |
| **AWS coverage** | Complete            | Good            | Via exporters      |
| **Log analysis** | Logs Insights       | Log Analytics   | Loki               |
| **Alerting**     | Alarms              | Monitors        | Alertmanager       |
| **Dashboards**   | Basic               | Rich            | Grafana            |

---

## ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                              |
| -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| "CloudWatch collects memory metrics automatically" | CPU only by default; install CloudWatch Agent for memory/disk on EC2                 |
| "Log Groups never expire"                          | Default is no expiration; set retention or logs accumulate costs indefinitely        |
| "CloudWatch alarms react instantly"                | Minimum evaluation period = 1 minute; fastest alarm = 1 minute                       |
| "Logs Insights is free"                            | Logs Insights charges per GB scanned ($0.005/GB); optimize queries with time windows |

---

## 🔗 Related Keywords

- [X-Ray](/cloud-aws/x-ray/) — distributed tracing complementary to CloudWatch metrics/logs
- [Lambda](/cloud-aws/lambda/) — automatic CloudWatch Logs integration
- [SNS](/cloud-aws/sns/) — alarm notification delivery

---

## 📌 Quick Reference Card

```bash
# List metrics for Lambda function
aws cloudwatch list-metrics \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=my-function

# Get metric statistics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 300 --statistics Average,p99

# Query logs
aws logs start-query \
  --log-group-name /aws/lambda/my-function \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | limit 20'

# Get query results
aws logs get-query-results --query-id <query-id>

# Tail logs (real-time)
aws logs tail /aws/lambda/my-function --follow --since 5m
```

---

## 🧠 Think About This

The most impactful CloudWatch cost optimization is setting log retention on ALL log groups. New log groups (auto-created by Lambda, ECS, API Gateway) default to "Never expire." At scale, this compounds: Lambda writes logs, never cleaned up, bill grows. One-time audit: `aws logs describe-log-groups --query 'logGroups[?retentionInDays==null].logGroupName'` — find all log groups without retention. Set to 30 days for debug logs, 90 days for operational logs, 365 days for audit logs. The second highest CloudWatch cost: high-resolution custom metrics ($0.30/metric/month vs $0.01 for standard). Only use 1-second resolution for metrics that require sub-minute alerting (like sudden spike detection for security events). Most operational metrics work fine at 1-minute granularity.
