---
layout: default
title: "AWS X-Ray (Distributed Tracing)"
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /observability/aws-x-ray-distributed-tracing/
number: "OBS-005"
category: Observability & SRE
difficulty: ★★★
depends_on: Distributed Tracing, AWS, Microservices
used_by: Observability & SRE, Cloud - AWS
related: OpenTelemetry, Jaeger, AppDynamics
tags:
  - observability
  - aws
  - distributed
  - advanced
  - production
---

# OBS-005 - AWS X-Ray (Distributed Tracing)

⚡ **TL;DR -** AWS X-Ray traces requests end-to-end across AWS services by propagating a trace ID through segments and subsegments, producing a visual service map and timeline for distributed request analysis.

| Field | Value |
|---|---|
| **Depends on** | Distributed Tracing, AWS, Microservices |
| **Used by** | Observability & SRE, Cloud - AWS |
| **Related** | OpenTelemetry, Jaeger, AppDynamics |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user reports that their checkout request failed. Your architecture: API Gateway → Lambda → SQS → Lambda → DynamoDB → SNS. You have CloudWatch Logs for each service, but they have different timestamps and no shared request ID. Correlating a single user's request across 6 hops takes 30 minutes of log archaeology.

**THE BREAKING POINT:**
In a distributed system, a single user-facing operation fans out across many services. Logs tell you what each service did. They do not tell you how those events connect into one causal chain - who called whom, in what order, for how long, and which hop introduced the latency.

**THE INVENTION MOMENT:**
X-Ray assigns a globally unique Trace ID to each request at the entry point and propagates it as an HTTP header (`X-Amzn-Trace-Id`) through every downstream call. Each service records a Segment (its own processing time) and any Subsegments (downstream calls it made). X-Ray assembles these into a complete trace timeline and renders a Service Map showing topology and health.

---

### 📘 Textbook Definition

**AWS X-Ray** is a distributed tracing service that collects trace data from instrumented applications to produce end-to-end request timelines and a visual service map. A **Trace** is the full journey of one request. A **Segment** is one service's contribution to a trace (start time, end time, HTTP info, errors). A **Subsegment** is a child unit within a segment representing downstream calls (DynamoDB, HTTP, SQL). **Annotations** are indexed key-value pairs for filtering traces. **Metadata** is non-indexed arbitrary data attached to segments. The **X-Ray daemon** is a local UDP receiver that batches and forwards segment data to the X-Ray API.

---

### ⏱️ Understand It in 30 Seconds

**One line:** X-Ray stitches the log entries of every service that handled a request into one searchable timeline.

> Like a package tracking system: your parcel (request) gets a tracking number at origin; every sorting facility (service) scans the barcode and records a timestamp; you can see the full journey and exactly where it got delayed.

**One insight:** X-Ray's Service Map is not manually maintained - it is auto-generated from actual trace data, so it reflects your real production topology, including undocumented connections.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **A trace ID is globally unique and propagated** - without a shared identifier, distributed events cannot be causally linked.
2. **Sampling is necessary at scale** - tracing every request at high throughput is prohibitively expensive; sampling captures a representative subset.
3. **Segment assembly is asynchronous** - services emit segments independently; X-Ray assembles them by Trace ID after collection.
4. **Annotations enable search; metadata enables context** - indexed annotations allow you to find traces by business fields; unindexed metadata stores detail without query cost.

**DERIVED DESIGN:**
The X-Ray SDK (Java, Node.js, Python, Go, .NET) intercepts HTTP clients, AWS SDK calls, and SQL clients to auto-create subsegments. The SDK sends segment data via UDP to the X-Ray daemon (port 2000) to minimise application latency impact. The daemon batches and sends to the X-Ray API over HTTPS. Segments are assembled and indexed. The X-Ray console queries assembled traces for the Service Map and trace list.

**THE TRADE-OFFS:**
**Gain:** Zero-setup tracing for AWS-native services (Lambda, ECS, API Gateway, DynamoDB native integration), visual service map, cross-service latency attribution.
**Cost:** Sampling means some traces are not captured; annotation cardinality limits (50 per segment); not portable across clouds without OpenTelemetry bridging.

---

### 🧪 Thought Experiment

**SETUP:** API Gateway → Lambda A → Lambda B → DynamoDB. A user reports a 10-second response time.

**WHAT HAPPENS WITHOUT X-Ray:**
Lambda A logs: "total time 9800ms." Lambda B logs: "processed in 120ms." You subtract and conclude Lambda A took 9680ms. But was that waiting for Lambda B to cold-start? Waiting for DynamoDB? Waiting for the SQS queue? You cannot tell from logs alone - you need timing relationships between services.

**WHAT HAPPENS WITH X-Ray:**
X-Ray shows the trace timeline. Lambda A: 9800ms total. Lambda A → invoke Lambda B (subsegment): 9620ms. Lambda B execution: 120ms. Lambda B → DynamoDB (subsegment): 60ms. Lambda B → DynamoDB (subsegment 2): 9400ms ← cold partition read. The 9.4-second DynamoDB call is the root cause: a cold partition with missing GSI.

**THE INSIGHT:** Timing attribution - knowing exactly how much time each hop contributed - is only possible when you have a shared trace ID and segment assembly. Logs show what happened; traces show where time went.

---

### 🧠 Mental Model / Analogy

> AWS X-Ray is a package tracking system for requests. Each request gets a tracking number (Trace ID) at the entry point. Every service it passes through (Lambda, DynamoDB, SQS) scans the tracking number and records a timestamp (Segment). Sub-deliveries within a service (a DynamoDB GetItem inside a Lambda) are recorded as sub-scans (Subsegments). The tracking system assembles the full journey from all scans.

**Element mapping:**
- Package = request
- Tracking number = Trace ID
- Sorting facility scan = Segment
- Internal facility process = Subsegment
- Delivery attempt notation = Annotation
- Package contents inspection notes = Metadata
- Route map = Service Map

Where this analogy breaks down: package tracking is fully sequential; X-Ray traces can include parallel subsegments representing concurrent downstream calls.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
X-Ray gives every request a unique ID and passes it through every service it visits. Each service records how long it took. X-Ray shows you a timeline of the whole journey and a map of which services talk to which.

**Level 2 - How to use it (junior developer):**
Enable Active Tracing on your Lambda function (console toggle or `Tracing: Active` in SAM template). Add the `aws-xray-sdk` to your dependencies and wrap the AWS SDK: `const AWS = AWSXRay.captureAWS(require('aws-sdk'))`. X-Ray auto-instruments downstream AWS calls. View traces in X-Ray console → Traces. The Service Map shows latency and error rate per service automatically.

**Level 3 - How it works (mid-level engineer):**
The X-Ray SDK creates a `Segment` when an instrumented entry point is invoked (HTTP server, Lambda handler). It creates `Subsegments` for each outbound call (AWS SDK, HTTP, SQL). Segment and subsegment data is serialised to JSON and sent via UDP to the X-Ray daemon on `localhost:2000`. The daemon accumulates, buffers, and sends to `xray.{region}.amazonaws.com` via HTTPS. X-Ray assembles traces by matching `X-Ray-Trace-Id` header across segments. Sampling rules (reservoir + fixed rate) control what fraction of requests are traced.

**Level 4 - Why it was designed this way (senior/staff):**
UDP to a local daemon was chosen for segment emission to decouple trace reporting from application latency - a TCP failure to the X-Ray API should never cause application request failures. The daemon absorbs network variability and provides retry logic. Sampling rules exist at the rule level (not the SDK level) so rules can be updated centrally without redeploying applications - critical when debugging a production issue requires temporarily increasing sampling rate for a specific endpoint. Annotations are indexed (enabling `GetTraceSummaries` filtering) while metadata is not, because unlimited indexing would make trace search prohibitively expensive; this distinction forces engineers to be intentional about what makes a good trace filter.

---

### ⚙️ How It Works (Mechanism)

```
Incoming Request (API Gateway / ALB)
  ↓ X-Amzn-Trace-Id: Root=1-abc;Sampled=1
Lambda / ECS / EC2 application
  ↓ X-Ray SDK intercepts
  ┌──────────────────────────────────────┐
  │  Segment created:                    │
  │    name: "checkout-lambda"           │
  │    start_time, end_time              │
  │    http: method, url, status         │
  │    annotations: {orderId, userId}    │
  │    Subsegments:                      │
  │      DynamoDB.GetItem  (45ms)        │
  │      HTTP → inventory (120ms)        │
  └──────────────────────────────────────┘
  ↓ UDP to localhost:2000
X-Ray Daemon
  ↓ batches, HTTPS
X-Ray Service (AWS)
  ↓ assembles by Trace ID
Trace: full timeline assembled
  ↓ Service Map updated
Console: trace list, timeline, map
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client → API Gateway
  ↓ Trace ID generated: Root=1-abc;Sampled=1
  ↓ X-Amzn-Trace-Id header propagated
Lambda A (checkout)    ← YOU ARE HERE
  │  Segment: 340ms total
  │  Subsegment → DynamoDB: 12ms
  │  Subsegment → Lambda B (async): 5ms
Lambda B (inventory)
  │  Segment: 95ms total
  │  Subsegment → DynamoDB: 45ms
X-Ray assembles trace
  Service Map: healthy (green nodes)
  Trace timeline: 340ms end-to-end
```

**FAILURE PATH:**
```
Client → API Gateway
  ↓ Trace ID: Root=1-xyz;Sampled=1
Lambda A
  │  Segment: 8,500ms
  │  Subsegment → DynamoDB: 8,200ms
  │    Fault: ProvisionedThroughputExceeded
  │    Throttle: true
X-Ray: trace shows fault annotation
  Service Map: DynamoDB node turns RED
  Error rate: 45%
  GetTraceSummaries filter:
    annotation.ThrottleError = true
→ Root cause: DynamoDB write throttle
```

**WHAT CHANGES AT SCALE:**
At high throughput, increase reservoir size in sampling rules for critical endpoints. Use X-Ray Groups to create filtered views (e.g., `fault = true` group for error-only traces). Use X-Ray Analytics to identify latency percentile outliers across millions of traces without manually reviewing individual traces.

---

### 💻 Code Example

**BAD - No trace context propagation (broken traces):**
```javascript
// Downstream call without propagating
// trace header - creates orphaned segments.
const axios = require("axios");

exports.handler = async (event) => {
    // No X-Ray SDK - trace context lost
    const result = await axios.get(
        "http://inventory-service/check"
    );
    return result.data;
};
```

**GOOD - X-Ray SDK with auto-instrumentation:**
```javascript
const AWSXRay = require("aws-xray-sdk-core");
const AWS = AWSXRay.captureAWS(
    require("aws-sdk")
);
const https = AWSXRay.captureHTTPs(
    require("https")
);

exports.handler = async (event) => {
    const segment =
        AWSXRay.getSegment();

    // Add searchable annotations
    segment.addAnnotation(
        "orderId", event.orderId
    );
    segment.addAnnotation(
        "userId", event.userId
    );

    // Add non-indexed metadata
    segment.addMetadata(
        "inputPayload", event
    );

    // AWS SDK calls auto-create subsegments
    const ddb = new AWS.DynamoDB
        .DocumentClient();
    const order = await ddb.get({
        TableName: "Orders",
        Key: { orderId: event.orderId },
    }).promise();

    // Manual subsegment for custom code
    const sub = segment.addNewSubsegment(
        "businessValidation"
    );
    try {
        validateOrder(order.Item);
        sub.close();
    } catch (err) {
        sub.addError(err);
        sub.close();
        throw err;
    }

    return order.Item;
};
```

**Sampling rules (AWS CLI):**
```bash
# Increase sampling for checkout endpoint
# during debug session
aws xray create-sampling-rule \
  --sampling-rule '{
    "RuleName": "CheckoutDebug",
    "Priority": 1,
    "FixedRate": 1.0,
    "ReservoirSize": 100,
    "ServiceName": "checkout-lambda",
    "ServiceType": "AWS::Lambda::Function",
    "Host": "*",
    "HTTPMethod": "POST",
    "URLPath": "/checkout",
    "ResourceARN": "*",
    "Version": 1
  }'
```

---

### ⚖️ Comparison Table

| Feature | AWS X-Ray | Jaeger | Zipkin | OpenTelemetry |
|---|---|---|---|---|
| **Data model** | Segments/Subsegments | Spans | Spans | Spans (OTLP) |
| **AWS integration** | Native (Lambda, ECS, API GW) | Manual | Manual | Via ADOT |
| **Service Map** | Built-in console | Jaeger UI | Zipkin UI | Vendor-dependent |
| **Sampling** | Centralised rules | Head-based | Head-based | Configurable |
| **Backend** | AWS managed | Self-hosted | Self-hosted | Vendor choice |
| **Portability** | AWS-locked | Open-source | Open-source | Vendor-neutral |
| **Best for** | AWS-native apps | Kubernetes OSS | Simple OSS tracing | Multi-cloud/vendor |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "X-Ray traces every request by default" | Default sampling is 1 request/second reservoir + 5% of additional requests; configure sampling rules to capture more |
| "The X-Ray daemon adds latency to requests" | Segments are sent via UDP (fire-and-forget); daemon runs as sidecar; application response time is not blocked by trace emission |
| "Annotations and metadata are equivalent" | Annotations are indexed (filterable in `GetTraceSummaries`); metadata is not indexed; use annotations for searchable business fields, metadata for large payloads |
| "X-Ray works with any HTTP client automatically" | Only AWS SDK calls and explicitly captured HTTP clients are auto-instrumented; plain `fetch`/`axios` calls require `captureHTTPs()` wrapping |
| "Service Map is always accurate" | Service Map reflects only traced traffic; services below the sampling threshold may appear disconnected or missing |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Trace segments not appearing in console**

**Symptom:** Lambda runs but no traces visible in X-Ray console.
**Root Cause:** Active Tracing not enabled on Lambda, X-Ray daemon not running (for EC2/ECS), or IAM role missing `xray:PutTraceSegments`.
**Diagnostic:**
```bash
# Check Lambda tracing config
aws lambda get-function-configuration \
  --function-name checkout-fn \
  | jq '.TracingConfig'
# Expected: {"Mode": "Active"}

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123:role/fn \
  --action-names xray:PutTraceSegments
```
**Fix:** Enable Active Tracing; add `xray:PutTraceSegments` and `xray:PutTelemetryRecords` to the Lambda execution role.
**Prevention:** Include X-Ray permissions and tracing config in all Lambda IaC templates.

---

**Mode 2: Broken traces - segments appear disconnected**

**Symptom:** Trace segments appear as separate orphaned traces instead of one connected trace.
**Root Cause:** Trace ID header (`X-Amzn-Trace-Id`) not propagated across service boundaries (e.g., SQS messages, custom HTTP clients).
**Diagnostic:**
```bash
# Inspect SQS message attributes for
# trace header propagation
aws sqs receive-message \
  --queue-url https://sqs.../queue \
  --message-attribute-names All \
  | jq '.Messages[].MessageAttributes'
# Should contain AWSTraceHeader attribute
```
**Fix:** For SQS → Lambda, enable Lambda Event Source Mapping with `ReportBatchItemFailures` - X-Ray propagates automatically. For custom HTTP clients, use `AWSXRay.captureHTTPs()`.
**Prevention:** Use AWS SDK for all inter-service calls; avoid raw HTTP clients in traced code paths.

---

**Mode 3: X-Ray costs too high**

**Symptom:** X-Ray costs spike unexpectedly with high-throughput services.
**Root Cause:** Sampling rate too high (100% sampling on a 10,000 req/sec service).
**Diagnostic:**
```bash
# Check current sampling rules
aws xray get-sampling-rules

# Check trace count
aws xray get-trace-graph \
  --trace-ids $(aws xray get-trace-summaries \
    --start-time ... --end-time ... \
    | jq -r '.TraceSummaries[].Id')
```
**Fix:** Reduce `FixedRate` to 0.01 (1%) for high-volume endpoints; keep higher rates for critical low-volume paths (checkout, payment). Use X-Ray Groups to analyse only error traces without storing success traces.
**Prevention:** Set sampling rules per endpoint priority; monitor X-Ray costs monthly in Cost Explorer.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Distributed Tracing - the concept X-Ray implements
- AWS CloudWatch Logs - the complementary logging layer for X-Ray traces
- Microservices - the architecture that makes distributed tracing necessary

**Builds On This (learn these next):**
- OpenTelemetry - vendor-neutral instrumentation standard; X-Ray supports OTLP via ADOT
- AppDynamics - enterprise APM with Business Transaction concept
- AWS CloudWatch ServiceLens - combines X-Ray traces with CloudWatch Logs and Metrics

**Alternatives / Comparisons:**
- Jaeger - open-source distributed tracing; Kubernetes-native; no AWS integration
- Zipkin - simple open-source tracing; lighter weight than Jaeger
- OpenTelemetry - instrumentation standard; can export to X-Ray, Jaeger, or Datadog

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════╗
║ WHAT IT IS   AWS distributed request       ║
║              tracing via segment assembly  ║
║ PROBLEM      Can't attribute latency to    ║
║              one hop in multi-service call ║
║ KEY INSIGHT  Trace ID propagated as HTTP   ║
║              header links all segments     ║
║ USE WHEN     AWS-native microservices,     ║
║              Lambda + API Gateway chains   ║
║ AVOID WHEN   Non-AWS or multi-cloud;       ║
║              use OpenTelemetry instead     ║
║ TRADE-OFF    Zero AWS setup vs vendor      ║
║              lock + limited portability    ║
║ ONE-LINER    Package tracking number for   ║
║              distributed AWS requests      ║
║ NEXT EXPLORE OpenTelemetry, ServiceLens    ║
╚════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(A - System Interaction)** X-Ray uses a reservoir + fixed-rate sampling model. A request enters at API Gateway (sampled=1), then invokes Lambda A which invokes Lambda B. Lambda B also receives traffic from a separate SQS queue that has its own sampling decision. How does X-Ray handle the case where the same Lambda B invocation is reached via two different sampled entry points simultaneously, and what does the resulting trace assembly look like?

2. **(C - Design Trade-off)** X-Ray Annotations are indexed and searchable; Metadata is not. An engineer proposes storing the full request payload as an Annotation for every trace to enable searching by any field. What are the technical limits and cost implications of this approach, and what alternative design would provide similar search capability without the drawbacks?

3. **(F - Comparison)** Your team decides to adopt OpenTelemetry (OTEL) for instrumentation instead of the native X-Ray SDK. The application still runs on AWS Lambda. Design the instrumentation architecture: what OTEL components are needed, how does data reach X-Ray (or an alternative backend), and what trace context propagation mechanism replaces the `X-Amzn-Trace-Id` header?
