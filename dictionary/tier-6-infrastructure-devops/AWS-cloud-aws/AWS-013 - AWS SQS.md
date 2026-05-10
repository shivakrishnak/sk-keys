---
version: 2
layout: default
title: "AWS SQS"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /cloud-aws/aws-sqs/
id: AWS-023
category: Cloud - AWS
difficulty: ★★☆
depends_on: Message Queue, AWS, Distributed Systems
used_by: AWS SNS + SQS Fan-Out Pattern, Cloud - AWS
related: AWS SNS, AWS Kinesis, RabbitMQ
tags:
  - aws
  - cloud
  - messaging
  - intermediate
  - reliability
---

# AWS-039 - AWS SQS

⚡ **TL;DR -** AWS's fully managed message queue that decouples producers from consumers, guaranteeing at-least-once delivery with configurable retention, visibility timeouts, and dead-letter queues.

| Attribute    | Value                                         |
|--------------|-----------------------------------------------|
| Depends on   | Message Queue, AWS, Distributed Systems       |
| Used by      | AWS SNS + SQS Fan-Out Pattern, Cloud - AWS    |
| Related      | AWS SNS, AWS Kinesis, RabbitMQ                |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Service A calls Service B synchronously via HTTP. If B is slow, A waits. If B crashes, A's request is lost. If traffic spikes 10×, B is overwhelmed and A starts failing too. A and B must both be running simultaneously - a hard temporal coupling that makes independent scaling, deployment, and failure impossible.

**THE BREAKING POINT:** Black Friday. Service A (checkout) generates orders at 10× normal rate. Service B (fulfilment) cannot scale fast enough. Orders are dropped. You add a retry loop in A - but B is now flooded with duplicate requests. You add a circuit breaker - but now A returns errors to users. Every solution to protect B hurts A, and every solution to protect A loses data.

**THE INVENTION MOMENT:** What if orders were written to a durable buffer that B consumes at its own pace? A succeeds as soon as the message is written. B processes when it can. If B crashes, the message waits in the queue until B recovers. Backpressure is natural - the queue grows; B scales; the queue drains.

---

### 📘 Textbook Definition

**AWS Simple Queue Service (SQS)** is a fully managed message queuing service that enables asynchronous, durable decoupling between distributed components. SQS offers two queue types: **Standard** (unlimited throughput, at-least-once delivery, best-effort ordering) and **FIFO** (exactly-once processing, strict message ordering, up to 3 000 messages/s with batching). Key mechanisms include **visibility timeout** (hides in-flight messages from competing consumers), **Dead Letter Queues** (DLQ, captures messages that fail processing beyond `maxReceiveCount`), and **long polling** (reduces empty API responses by waiting up to 20 s for messages).

---

### ⏱️ Understand It in 30 Seconds

**One line:** SQS is a durable buffer between services - producers write fast, consumers read at their own pace.

> Think of it as a post office sorting room: senders drop letters at any time; postal workers process the pile at their speed; if a worker gets sick, letters wait in the pile until someone picks them up.

**One insight:** SQS does not push messages - consumers must poll. This is not a limitation; it means consumers control their own throughput and cannot be overwhelmed by producer bursts.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Temporal decoupling: producer and consumer do not need to be available simultaneously.
2. Load levelling: a spike in producer rate fills the queue; consumers drain it at a sustainable rate.
3. At-least-once delivery: SQS may deliver a message more than once; consumers must be idempotent.
4. Exactly-once processing requires FIFO queues and consumer-side deduplication.

**DERIVED DESIGN:**

When a consumer calls `ReceiveMessage`, SQS returns up to 10 messages and sets them **in-flight** for the visibility timeout duration. Other consumers cannot receive these messages during this window. If the consumer successfully processes and calls `DeleteMessage`, the messages are permanently removed. If the consumer crashes or times out without deleting, the messages become visible again after the visibility timeout expires - enabling automatic recovery from consumer failure.

**THE TRADE-OFFS:**

**Gain:** Infinite horizontal scaling of producers without affecting consumers. Automatic retry on consumer failure. Spike absorption with no message loss. Fully managed - no broker to operate.

**Cost:** At-least-once delivery means consumers must be idempotent. FIFO queues cap at 3 000 msg/s. Standard queues offer only best-effort ordering - do not rely on order for sequential business logic. Polling adds latency (minimised with long polling) and API call costs.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce checkout service writes order events. A fulfilment service processes them (calls a 3PL API, slow: 2 s/order). Normal rate: 100 orders/min. Flash sale rate: 5 000 orders/min.

**WHAT HAPPENS WITHOUT SQS:** Checkout calls fulfilment synchronously. At 5 000 orders/min, fulfilment receives 83 requests/s each taking 2 s - needing 166 concurrent threads. The service is overwhelmed, returns 503s. Checkout retries → thundering herd. Orders are lost.

**WHAT HAPPENS WITH SQS:** Checkout writes order messages to SQS in <1 ms. SQS accepts unlimited throughput - no backpressure to checkout. Fulfilment polls SQS, processes at 30 orders/min (limited by 3PL API), and auto-scales Lambda consumers to process faster. The queue depth grows during the flash sale and drains over the next hour. No orders are lost. Checkout never sees fulfilment failures.

**THE INSIGHT:** SQS converts a synchronous failure-propagating dependency into an asynchronous, decoupled flow where producer and consumer failures are completely isolated from each other.

---

### 🧠 Mental Model / Analogy

> SQS is like a physical inbox tray on a shared desk. Anyone can drop work in at any speed. The worker processes items from the tray at their own pace. If the worker leaves for lunch, work accumulates in the tray - nothing is lost. If they're out sick, a colleague takes over the tray.

- **Inbox tray** → SQS queue (durable message store)
- **Dropping work in** → `SendMessage` (producer)
- **Picking up an item** → `ReceiveMessage` (consumer)
- **Working on it** → Visibility timeout window (item removed from view)
- **Finishing and filing** → `DeleteMessage` (permanent removal)
- **Colleague taking over** → Another consumer instance receives the message after visibility timeout expires

Where this analogy breaks down: unlike a physical tray, SQS can serve multiple consumers simultaneously, and the same item can appear in multiple workers' hands if the first worker doesn't finish in time (visibility timeout expiry) - requiring idempotent processing.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
SQS is a bucket you put messages in. One service puts messages in; another service takes them out and processes them. If the second service crashes, messages stay in the bucket until it recovers.

**Level 2 - How to use it (junior developer):**
Create a queue (Standard or FIFO). Use the AWS SDK to `SendMessage` from producers. Use `ReceiveMessage` + `DeleteMessage` in consumers. Set visibility timeout longer than your maximum processing time. Create a DLQ and set `maxReceiveCount` to catch messages that keep failing.

**Level 3 - How it works (mid-level engineer):**
SQS distributes messages across redundant servers. `ReceiveMessage` performs a short-poll or long-poll (`WaitTimeSeconds=20`). Long polling waits up to 20 s for a message - reduces empty responses and costs. Up to 10 messages can be received per call. Visibility timeout defaults to 30 s; extend it during processing with `ChangeMessageVisibility`. Standard queues may deliver a message more than once (at-least-once) due to distributed storage - idempotency is mandatory. FIFO queues use a `MessageGroupId` for ordering and a `MessageDeduplicationId` (or content-based deduplication SHA-256) for exactly-once. FIFO throughput: 300 msg/s without batching, 3 000 msg/s with batching (10 msg/batch).

**Level 4 - Why it was designed this way (senior/staff):**
Standard queue at-least-once delivery is a deliberate trade-off for unlimited throughput and multi-AZ redundancy. SQS stores messages across multiple AZ servers - occasionally, a consumer receives a message from one server replica while another server replica briefly resurfaces the same message before replication synchronises. Enforcing exactly-once at this scale would require global locking - prohibitive. FIFO queues pay for exactly-once with a throughput cap. The visibility timeout model - rather than message locking - is stateless: any consumer can extend any message's visibility, enabling distributed workers without a central lock server. The DLQ is a separate queue (not a special storage tier) - this is intentional; it allows independent processing, monitoring, and alerting on failed messages without touching the main queue's operational path.

---

### ⚙️ How It Works (Mechanism)

```
+-----------------------------------------------+
| Producer                                      |
|  SendMessage(body, delay=0)                   |
|       |                                       |
|       v                                       |
| SQS Queue (multi-AZ durable storage)          |
|  [msg1][msg2][msg3]...                        |
|       |                                       |
|       v                                       |
| Consumer calls ReceiveMessage                 |
|  -> msg1 becomes INVISIBLE (vis. timeout)     |
|  -> Consumer processes msg1                   |
|  -> Success: DeleteMessage(receipt_handle)    |
|  -> Failure/timeout: msg1 becomes VISIBLE     |
|     -> Another consumer can receive it        |
|       |                                       |
| After maxReceiveCount failures:               |
|  -> msg1 moved to Dead Letter Queue (DLQ)     |
+-----------------------------------------------+
```

**Key Parameters:**

| Parameter            | Default  | Max      | Notes                        |
|----------------------|----------|----------|------------------------------|
| Visibility Timeout   | 30 s     | 12 hr    | Must exceed processing time  |
| Message Retention    | 4 days   | 14 days  | Messages deleted after expiry|
| Receive Wait Time    | 0 s      | 20 s     | 0=short poll, >0=long poll   |
| Max Message Size     | 256 KB   | 256 KB   | Use S3 pointer for larger    |
| Delay Seconds        | 0 s      | 15 min   | Per-queue or per-message      |
| maxReceiveCount      | n/a      | n/a      | DLQ trigger threshold        |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Producer (checkout service)
  |
  v
SendMessage(orderId, items, total)  <- YOU ARE HERE
  |
  v
SQS Standard Queue (3 AZ replicas)
  |
  v
Consumer (fulfilment Lambda) polls ReceiveMessage
  -> Up to 10 messages, WaitTimeSeconds=20
  |
  v
Message becomes INVISIBLE (visibility timeout: 60s)
  |
  v
Consumer processes order (calls 3PL API, ~2s)
  |
  +-- Success: DeleteMessage(receiptHandle)
  |   Message permanently removed
  |
  +-- Failure/crash: visibility timeout expires
      Message becomes VISIBLE again
      -> Another consumer receives it
```

**FAILURE PATH:** If a message fails `maxReceiveCount` times (e.g. 3), it is moved to the DLQ. DLQ messages retain original attributes. Trigger a Lambda on the DLQ for alerting or dead-letter reprocessing. DLQ messages expire after their own retention period - monitor DLQ depth as a critical metric.

**WHAT CHANGES AT SCALE:** SQS auto-scales with no configuration. Consumer scaling is the operator's responsibility - use Lambda event source mapping (automatically scales consumers based on queue depth) or manually scale EC2/ECS consumers by monitoring the `ApproximateNumberOfMessagesVisible` CloudWatch metric.

---

### 💻 Code Example

**BAD - Short polling with immediate delete (data loss on processing failure):**
```python
import boto3
sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/orders'

# BAD: delete before processing - lose message if crash
response = sqs.receive_message(QueueUrl=QUEUE_URL)
for msg in response.get('Messages', []):
    # Delete immediately - if processing fails, message is gone
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=msg['ReceiptHandle']
    )
    process_order(msg['Body'])  # crash here = lost order
```

**GOOD - Long polling, process then delete, with DLQ:**
```python
import boto3, json, logging
sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123/orders'

def poll_and_process():
    # Long poll: wait up to 20s for messages (reduces costs)
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20,          # long polling
        VisibilityTimeout=120        # 2x max processing time
    )
    for msg in response.get('Messages', []):
        try:
            order = json.loads(msg['Body'])
            process_order(order)     # business logic
            # Only delete AFTER successful processing
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )
        except Exception as e:
            logging.error(f"Processing failed: {e}")
            # Do NOT delete - message reappears after timeout
            # After maxReceiveCount failures -> moved to DLQ
```

```bash
# CloudFormation: queue with DLQ
# aws cloudformation deploy --template-file sqs.yaml
```
```yaml
Resources:
  OrdersDLQ:
    Type: AWS::SQS::Queue
    Properties:
      MessageRetentionPeriod: 1209600  # 14 days
  OrdersQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 120
      ReceiveMessageWaitTimeSeconds: 20
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt OrdersDLQ.Arn
        maxReceiveCount: 3
```

---

### ⚖️ Comparison Table

| Feature              | SQS Standard     | SQS FIFO         | RabbitMQ         | AWS Kinesis      |
|----------------------|------------------|------------------|------------------|------------------|
| Throughput           | Unlimited        | 3 000 msg/s      | Limited by broker| 1 MB/s/shard     |
| Delivery guarantee   | At-least-once    | Exactly-once     | At-least-once    | At-least-once    |
| Ordering             | Best-effort      | Strict per group | Per-queue        | Per-shard        |
| Retention            | Up to 14 days    | Up to 14 days    | Until consumed   | 24 hr - 365 days |
| Message replay       | No               | No               | No               | Yes              |
| Consumer model       | Pull (poll)      | Pull (poll)      | Push or pull     | Pull (checkpoint)|
| Managed service      | Yes              | Yes              | Self or Amazon MQ| Yes              |
| Dead letter support  | Yes              | Yes              | Yes              | No (DLQ via Lambda)|

---

### 🔁 Flow / Lifecycle

**Message Lifecycle:**

```
+-----------------------------------------------+
| 1. SENT      -> SendMessage; stored in queue  |
| 2. DELAYED   -> Delay seconds active          |
|               (message not receivable yet)    |
| 3. AVAILABLE -> Visible in queue              |
| 4. IN-FLIGHT -> ReceiveMessage called;        |
|               invisible for visibility timeout|
| 5. DELETED   -> DeleteMessage; permanently    |
|               removed (success path)          |
| 6. VISIBLE   -> Visibility timeout expired;   |
|               message returns to queue        |
|               (failure/crash recovery)        |
| 7. DLQ       -> maxReceiveCount exceeded;     |
|               moved to dead letter queue      |
| 8. EXPIRED   -> Retention period elapsed;     |
|               message silently deleted        |
+-----------------------------------------------+
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "SQS guarantees message ordering" | Standard queues are best-effort only. Only FIFO queues with a `MessageGroupId` guarantee strict ordering per group. |
| "Deleting before processing is safe" | It causes data loss if processing fails after deletion. Always delete only after successful processing. |
| "Visibility timeout is a lock" | It is a soft invisibility window, not a hard lock. Any consumer (or the same one) can extend it via `ChangeMessageVisibility`. |
| "Long polling is always better" | Long polling reduces empty responses and costs for low-volume queues. For high-volume queues always returning messages, short polling achieves similar throughput. |
| "DLQ messages are processed automatically" | DLQ is just another queue. You must separately monitor it and build consumers or alerting - AWS does not auto-retry DLQ messages. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Messages processed multiple times (duplicate processing)**

**Symptom:** Orders fulfilled twice; database records duplicated; idempotency violations.
**Root Cause:** Visibility timeout too short - processing takes longer than the timeout, message becomes visible again, a second consumer picks it up before the first finishes.
**Diagnostic:**
```bash
# Check ApproximateNumberOfMessagesNotVisible (in-flight)
# vs queue depth to estimate processing time vs timeout
aws cloudwatch get-metric-statistics \
  --namespace AWS/SQS \
  --metric-name \
    ApproximateNumberOfMessagesNotVisible \
  --dimensions Name=QueueName,Value=orders \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 60 --statistics Average
```
**Fix:** Set `VisibilityTimeout` to at least 2× the maximum expected processing time. Use `ChangeMessageVisibility` to heartbeat-extend visibility for long-running jobs.
**Prevention:** Implement idempotency keys in consumers (store processed message IDs in DynamoDB with TTL matching queue retention).

---

**Mode 2 - Queue depth grows unboundedly (consumer not keeping up)**

**Symptom:** `ApproximateNumberOfMessagesVisible` grows continuously; processing latency increases.
**Root Cause:** Producer rate exceeds consumer processing rate. Consumer auto-scaling not configured or insufficient.
**Diagnostic:**
```bash
# Monitor queue depth trend
aws cloudwatch get-metric-statistics \
  --namespace AWS/SQS \
  --metric-name ApproximateNumberOfMessagesVisible \
  --dimensions Name=QueueName,Value=orders \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 --statistics Maximum
```
**Fix:** Scale Lambda consumers (increase reserved concurrency or batch size). For EC2/ECS consumers, configure auto-scaling policies based on `ApproximateNumberOfMessagesVisible`. Check if consumer is blocked on a downstream dependency (DB connection limit, 3PL API rate limit).
**Prevention:** Set a CloudWatch alarm on `ApproximateNumberOfMessagesVisible` exceeding a threshold (e.g. > 1 000). Perform load testing to determine maximum sustainable consumer throughput.

---

**Mode 3 - Messages silently lost (no DLQ configured)**

**Symptom:** Orders missing from fulfilment; producers confirm writes but consumers never see them.
**Root Cause:** Processing fails repeatedly; messages expire after retention period (4 days default) with no DLQ to capture them. Or retention period too short for queue consumer outage.
**Diagnostic:**
```bash
# Check NumberOfMessagesSent vs NumberOfMessagesDeleted
aws cloudwatch get-metric-statistics \
  --namespace AWS/SQS \
  --metric-name NumberOfMessagesSent \
  --dimensions Name=QueueName,Value=orders \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 --statistics Sum
# Compare to NumberOfMessagesDeleted
# Discrepancy = unprocessed/expired messages
```
**Fix:** Configure DLQ with `maxReceiveCount: 3` and maximum retention (14 days). Alert on DLQ depth > 0.
**Prevention:** Always create a DLQ for every production SQS queue. Treat DLQ messages as high-priority incidents - they represent work that failed processing multiple times.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Message Queue - the general pattern SQS implements; queue semantics, at-least-once delivery
- AWS - IAM policies for queue access; Lambda event source mapping
- Distributed Systems - partial failure modes that motivate asynchronous decoupling

**Builds On This (learn these next):**
- AWS SNS - fan-out pattern (SNS topic → multiple SQS queues) for parallel processing pipelines
- AWS Lambda - most common SQS consumer with native event source mapping
- AWS Kinesis - ordered streaming alternative when replay and ordering are required

**Alternatives / Comparisons:**
- AWS Kinesis - use when message replay, strict ordering, or stream processing is needed
- RabbitMQ - use when push-based delivery, topic routing, or dead-letter exchanges are required
- Apache Kafka - use for high-throughput, ordered, replayable event streaming at scale

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Managed pull-based message queue  |
| PROBLEM      | Synchronous coupling + overload   |
| KEY INSIGHT  | Decouple rate; consumer controls  |
|              | its own throughput via polling    |
| USE WHEN     | Async work, spike absorption      |
| AVOID WHEN   | Strict ordering at high throughput|
| TRADE-OFF    | At-least-once vs exactly-once     |
|              | (Standard vs FIFO)                |
| ONE-LINER    | SendMessage / ReceiveMessage +    |
|              | DeleteMessage after success       |
| NEXT EXPLORE | AWS SNS fan-out, DLQ monitoring   |
+--------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** SQS Standard guarantees at-least-once delivery. Your consumer inserts a record into a database using the SQS `MessageId` as the primary key. A duplicate message arrives. What happens, and is this a safe idempotency strategy? What edge case could still cause a problem?

2. **(Scale)** Your Lambda SQS consumer processes 10 messages per batch. Processing takes 45 s per batch. Your queue has 10 000 messages. The visibility timeout is 30 s. Describe the failure cascade that occurs and the two parameters you must change to fix it.

3. **(Design Trade-off)** A financial transaction system requires that each payment is processed exactly once, in the order it was received per account. You have two options: SQS FIFO with one message group per account, or SQS Standard with database-level idempotency. What are the throughput implications of each, and which would you choose for 1 million accounts?
