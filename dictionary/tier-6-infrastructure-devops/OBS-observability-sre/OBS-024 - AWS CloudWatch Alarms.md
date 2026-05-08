---
layout: default
title: "AWS CloudWatch Alarms"
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 2
permalink: /observability/aws-cloudwatch-alarms/
number: "OBS-002"
category: Observability & SRE
difficulty: ★★★
depends_on: Metrics, Alerting, AWS
used_by: Observability & SRE, Cloud - AWS
related: AWS CloudWatch Dashboards, Actionable Alerting Patterns, PagerDuty
tags:
  - observability
  - aws
  - advanced
  - production
---

# OBS-002 - AWS CloudWatch Alarms

⚡ **TL;DR -** AWS CloudWatch Alarms monitor a single metric or math expression against a threshold and trigger automated actions (SNS, Auto Scaling, EC2) when the ALARM state is reached.

| Field | Value |
|---|---|
| **Depends on** | Metrics, Alerting, AWS |
| **Used by** | Observability & SRE, Cloud - AWS |
| **Related** | AWS CloudWatch Dashboards, Actionable Alerting Patterns, PagerDuty |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your Lambda function starts throttling at 3am. Nobody notices until a customer reports missing orders at 9am. By then 6 hours of events are lost. You had the metrics - you just had no automated response.

**THE BREAKING POINT:**
AWS generates thousands of metrics automatically (CPU, latency, error rate, throttles). Without alarms, these metrics are dashboards you stare at - not signals that act. Human review of dashboards does not scale and does not catch 3am incidents.

**THE INVENTION MOMENT:**
CloudWatch Alarms evaluate a metric against a threshold over a rolling time window, transition between ALARM/OK/INSUFFICIENT_DATA states, and trigger actions automatically - scaling a fleet, sending an SNS notification, or rebooting an EC2 instance - without human involvement.

---

### 📘 Textbook Definition

An **AWS CloudWatch Alarm** monitors a CloudWatch metric or math expression over a specified evaluation period. When the metric breaches the defined threshold for a required number of consecutive periods, the alarm transitions to `ALARM` state and triggers configured actions. Three states exist: `OK` (metric within threshold), `ALARM` (threshold breached), and `INSUFFICIENT_DATA` (not enough data points). Composite Alarms combine multiple alarms using Boolean logic for higher-fidelity alerting.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A CloudWatch Alarm is a watchdog that fires an action when a metric crosses a threshold for long enough.

> Like a thermostat: you set a temperature (threshold); if the room is too hot for more than a set time (evaluation periods), it triggers the air conditioning (action) - and resets when the temperature returns to normal.

**One insight:** The power is not the alert itself but the automated action - an alarm can scale your fleet, invoke a Lambda, or create a Systems Manager OpsItem with zero human intervention.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Metrics are time-series data points** - an alarm operates on the aggregated value (Average, Sum, Maximum, Minimum, p99) over a period.
2. **State machines reduce noise** - a threshold breach for 1 data point is noise; requiring N of M consecutive breaches before transitioning to ALARM reduces flapping.
3. **Actions must be idempotent** - alarms can re-enter ALARM state; SNS notifications and scaling actions must tolerate repeated triggers.
4. **Missing data has semantics** - `INSUFFICIENT_DATA` is not OK; how missing data is treated (`missing`, `ignore`, `breaching`, `notBreaching`) materially changes alarm sensitivity.

**DERIVED DESIGN:**
Each alarm specifies: metric namespace + name + dimensions, statistic (Average/Sum/p99), period (60–86400s), evaluation periods (N), datapoints to alarm (M ≤ N), comparison operator, threshold, and treat-missing-data policy. State transitions evaluate every period. Anomaly detection bands replace fixed thresholds by using ML to define expected range.

**THE TRADE-OFFS:**
**Gain:** Automated response, fine-grained control over evaluation windows, composite logic.
**Cost:** Per-alarm pricing, static thresholds require manual tuning, composite alarms add complexity.

---

### 🧪 Thought Experiment

**SETUP:** Your API's error rate normally sits at 0.1%. You want to alert when it hits 5%.

**WHAT HAPPENS WITHOUT CloudWatch Alarms:**
The error rate spikes to 8% at 2am during a deployment. Logs accumulate. The on-call engineer is not paged. At 6am, the morning shift sees 4 hours of failures in the dashboard.

**WHAT HAPPENS WITH CloudWatch Alarms:**
You create an alarm on `5XX ErrorRate > 5%` for 3 of 3 evaluation periods (each 1 minute). At 2:03am the alarm enters ALARM state, publishes to an SNS topic, and PagerDuty pages the on-call engineer. The deployment is rolled back by 2:10am. Total impact: 10 minutes.

**THE INSIGHT:** The evaluation window (N of M periods) is the key design decision. Too short → flapping alerts. Too long → slow detection. The right window is determined by the SLO error budget burn rate.

---

### 🧠 Mental Model / Analogy

> A CloudWatch Alarm is a traffic light with a timer. The light only turns red if the road has been over-capacity for a minimum number of consecutive measurement intervals - not just a single spike. Once red, it triggers an automated response (close a lane, divert traffic). When congestion clears, it returns to green.

**Element mapping:**
- Road traffic level = metric value
- Over-capacity threshold = alarm threshold
- Consecutive intervals = evaluation periods / datapoints to alarm
- Red light = ALARM state
- Divert traffic response = SNS action / Auto Scaling policy
- Green light = OK state

Where this analogy breaks down: traffic lights affect all drivers; CloudWatch Alarms act on backend infrastructure, not end users directly.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A CloudWatch Alarm watches a number (like error count or CPU) and sends a notification or takes an action when it gets too high - automatically, any time of day.

**Level 2 - How to use it (junior developer):**
In the AWS Console → CloudWatch → Alarms → Create Alarm. Select a metric (e.g., `AWS/Lambda Errors`), set a threshold (e.g., `> 10`), set evaluation period (1 minute), evaluation count (3 of 3). Add an SNS action pointing to a topic that emails you. The alarm is created in `INSUFFICIENT_DATA` state until enough data points arrive.

**Level 3 - How it works (mid-level engineer):**
CloudWatch evaluates the alarm every `period` seconds. It collects the last `evaluation_periods` data points and computes the chosen statistic. If `datapoints_to_alarm` of the last `evaluation_periods` breach the threshold, the alarm transitions to `ALARM`. On state change, CloudWatch publishes to configured action targets (SNS ARN, Auto Scaling policy ARN, EC2 action). Anomaly detection trains an ML model on historical data and sets dynamic upper/lower bands as the threshold.

**Level 4 - Why it was designed this way (senior/staff):**
The N-of-M evaluation model exists because metrics have inherent statistical noise; requiring consecutive breaches before action filters transient spikes. The `INSUFFICIENT_DATA` state is a first-class citizen because in distributed systems, metric delivery is not guaranteed - treating missing data as `notBreaching` hides actual outages. Composite Alarms were introduced because individual metric alarms generate too much noise; a CPU spike alone is not an incident - CPU spike AND latency spike AND error rate spike together are. The separation of alarm state from action execution means the same alarm can drive multiple downstream systems (SNS, Auto Scaling, OpsCenter) simultaneously.

---

### ⚙️ How It Works (Mechanism)

```
CloudWatch Metric
  (namespace/name/dimensions)
  ↓ every [period] seconds
Statistic computed
  (Average / Sum / p99 / etc.)
  ↓
Evaluation Window
  [datapoints_to_alarm of evaluation_periods]
  ↓
  ┌──────────────────────────────────────┐
  │  Threshold comparison                │
  │  GreaterThan / LessThan /            │
  │  GreaterThanOrEqualTo /              │
  │  LessThanLowerOrGreaterUpperThreshold│
  └──────────────────────────────────────┘
  ↓
State: OK → ALARM → OK
  (or INSUFFICIENT_DATA)
  ↓
Actions triggered on state change:
  • SNS Topic → Email/PagerDuty/Lambda
  • Auto Scaling Policy
  • EC2 Action (stop/terminate/reboot)
  • Systems Manager OpsItem
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Lambda function executes
  ↓ emits ErrorCount metric (0)
CloudWatch receives data point
  ↓ statistic: Sum over 60s = 0
Evaluation: 0 < threshold 10
  ↓ Alarm state: OK ← YOU ARE HERE
No action triggered
Dashboard shows green
```

**FAILURE PATH:**
```
Lambda function throttles
  ↓ emits ErrorCount = 15 (period 1)
  ↓ emits ErrorCount = 12 (period 2)
  ↓ emits ErrorCount = 18 (period 3)
Evaluation: 3 of 3 breach threshold 10
  ↓ Alarm transitions: OK → ALARM
SNS publishes to PagerDuty topic
  ↓ PagerDuty pages on-call engineer
  ↓ Alarm enters ALARM state (persists)
Engineer investigates → fixes throttle
  ↓ ErrorCount drops to 0 (3 periods)
  ↓ Alarm transitions: ALARM → OK
```

**WHAT CHANGES AT SCALE:**
At high-volume systems, use high-resolution metrics (1-second period) for faster detection. Use math expressions (e.g., `error_rate = errors / (errors + successes)`) instead of raw counts to avoid volume-correlated false alarms. Composite Alarms reduce SNS fan-out noise across hundreds of individual metric alarms.

---

### 💻 Code Example

**BAD - Static threshold on raw error count:**
```python
# Alarm on raw count - fires during high
# traffic even if error RATE is healthy.
# Also fires on single-period spikes.
# aws cloudwatch put-metric-alarm
aws_cloudwatch_metric_alarm = {
    "AlarmName": "LambdaErrors",
    "MetricName": "Errors",
    "Namespace": "AWS/Lambda",
    "Statistic": "Sum",
    "Period": 60,
    "EvaluationPeriods": 1,   # too short
    "Threshold": 10,
    "ComparisonOperator":
        "GreaterThanThreshold",
}
```

**GOOD - Math expression on error rate with N-of-M:**
```python
# Alarm on error rate (errors / requests).
# 3-of-3 evaluation prevents flapping.
# treat_missing_data=breaching ensures
# cold/dead Lambdas are caught too.
import boto3

cw = boto3.client("cloudwatch")

cw.put_metric_alarm(
    AlarmName="LambdaErrorRate-High",
    Metrics=[
        {
            "Id": "errors",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/Lambda",
                    "MetricName": "Errors",
                    "Dimensions": [{
                        "Name": "FunctionName",
                        "Value": "checkout-fn",
                    }],
                },
                "Period": 60,
                "Stat": "Sum",
            },
        },
        {
            "Id": "invocations",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/Lambda",
                    "MetricName": "Invocations",
                    "Dimensions": [{
                        "Name": "FunctionName",
                        "Value": "checkout-fn",
                    }],
                },
                "Period": 60,
                "Stat": "Sum",
            },
        },
        {
            "Id": "error_rate",
            "Expression":
                "errors / invocations * 100",
            "Label": "ErrorRatePct",
        },
    ],
    ComparisonOperator":
        "GreaterThanThreshold",
    Threshold=5.0,
    EvaluationPeriods=3,
    DatapointsToAlarm=3,
    TreatMissingData="breaching",
    AlarmActions=[
        "arn:aws:sns:us-east-1:123:oncall"
    ],
)
```

---

### ⚖️ Comparison Table

| Capability | Standard Alarm | Composite Alarm | Anomaly Detection Alarm |
|---|---|---|---|
| **Based on** | Single metric or math expr | Multiple alarm states | ML band around metric |
| **Threshold type** | Static value | Boolean (AND/OR/NOT) | Dynamic upper/lower |
| **Best for** | Single KPI monitoring | Reducing noise, compound conditions | Seasonal metrics, no clear threshold |
| **Cost** | Per alarm | Per composite alarm | Per alarm + model cost |
| **Alert on missing data** | Configurable | Inherits child alarms | Configurable |
| **Actions** | SNS/ASG/EC2/SSM | SNS only | SNS/ASG/EC2/SSM |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "INSUFFICIENT_DATA means the metric is fine" | It means CloudWatch has not received enough data points to evaluate - could indicate a dead service or metric emission failure |
| "Alarms fire on every threshold breach" | Alarms transition state only; if already in ALARM, a continued breach does not re-fire actions - use `AlarmActions` vs `OKActions` carefully |
| "Setting period=60 is always fine" | For fast-moving metrics like Lambda errors, use high-resolution metrics (10s or 1s period) for sub-minute detection |
| "Composite alarms replace individual alarms" | Composite alarms reference child alarms - child alarms must still exist and be evaluated; composite only controls notification routing |
| "Math expressions work with any metric" | Math expressions only work with metrics in the same AWS account and region unless using cross-account metric sharing |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Alarm stuck in INSUFFICIENT_DATA**

**Symptom:** Newly created alarm never transitions to OK or ALARM.
**Root Cause:** Metric not being emitted (service not running), wrong dimensions, or period longer than metric granularity.
**Diagnostic:**
```bash
# Check if metric data exists
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=fn \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 60 \
  --statistics Sum
```
**Fix:** Verify dimensions match exactly (case-sensitive). Invoke the Lambda function once to generate a data point.
**Prevention:** Add alarm state validation to deployment pipelines; alert on `INSUFFICIENT_DATA` duration > 5 minutes.

---

**Mode 2: Alert fatigue from flapping alarms**

**Symptom:** On-call receives dozens of ALARM→OK→ALARM notifications per hour.
**Root Cause:** `EvaluationPeriods=1` or threshold set too close to normal variance.
**Diagnostic:**
```bash
# View alarm history for state transitions
aws cloudwatch describe-alarm-history \
  --alarm-name "MyAlarm" \
  --history-item-type StateUpdate \
  --max-records 20
```
**Fix:**
```bash
# BAD: Single period, fires on any spike
EvaluationPeriods: 1
DatapointsToAlarm: 1

# GOOD: 3-of-5 window absorbs transients
EvaluationPeriods: 5
DatapointsToAlarm: 3
```
**Prevention:** Use anomaly detection for metrics with variable baselines; set `TreatMissingData=ignore` for bursty metrics.

---

**Mode 3: Auto Scaling action not triggering**

**Symptom:** Alarm transitions to ALARM but EC2 fleet does not scale.
**Root Cause:** Auto Scaling policy ARN wrong, IAM role missing CloudWatch permissions, or cooldown period active.
**Diagnostic:**
```bash
# Check scaling activity log
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name my-asg \
  --max-records 10
```
**Fix:** Verify the alarm's `AlarmActions` contains the exact ARN of the scaling policy, not the Auto Scaling Group.
**Prevention:** Test alarms with `set-alarm-state` to simulate ALARM state and verify actions fire in a staging environment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Metrics - the time-series data points alarms operate on
- Alerting - the discipline of signal design and routing
- AWS CloudWatch - the platform that hosts alarms

**Builds On This (learn these next):**
- AWS CloudWatch Dashboards - visualise the metrics your alarms monitor
- Actionable Alerting Patterns - design principles for low-noise, high-signal alerts
- AWS CloudWatch Log Insights - correlate alarm fires with log data

**Alternatives / Comparisons:**
- PagerDuty - alert routing and on-call management layer above CloudWatch
- Datadog Monitors - cross-cloud alternative with richer query language
- Prometheus Alertmanager - open-source equivalent for self-managed metrics

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════╗
║ WHAT IT IS   AWS metric watchdog with      ║
║              automated action triggers     ║
║ PROBLEM      Metrics go unnoticed at 3am   ║
║              without automated response    ║
║ KEY INSIGHT  N-of-M evaluation window      ║
║              prevents flapping alerts      ║
║ USE WHEN     AWS-native alerting on any    ║
║              CloudWatch metric or expr     ║
║ AVOID WHEN   Need cross-cloud alerting or  ║
║              complex routing logic         ║
║ TRADE-OFF    Tight detection vs false      ║
║              positive rate (period tuning) ║
║ ONE-LINER    AWS metric threshold guard    ║
║              with automated remediation    ║
║ NEXT EXPLORE Composite Alarms,             ║
║              Anomaly Detection Alarms      ║
╚════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(E - First Principles)** A CloudWatch Alarm using `EvaluationPeriods=3, DatapointsToAlarm=3` with `Period=60s` has a minimum detection latency of 3 minutes. For a payment service with a 99.9% SLO (43 minutes error budget per month), is this detection window acceptable? How would you redesign the alarm to reduce Time-to-Detect without increasing false-positive rate?

2. **(B - Scale)** You have 500 Lambda functions each with an individual error-rate alarm. Composite Alarms can combine them but only support SNS actions. Design an alerting architecture that uses Composite Alarms to reduce on-call noise while still preserving function-level drill-down for root cause analysis.

3. **(C - Design Trade-off)** Anomaly detection alarms adapt their threshold automatically. In what operational scenario would this adaptability become a liability - where a static threshold would catch an incident that anomaly detection would silently accept?
