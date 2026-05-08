---
layout: default
title: "SQS"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /cloud-aws/sqs/
id: AWS-049
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on:
  ["AWS Global Infrastructure", "IAM (Identity and Access Management)"]
used_by: ["SNS", "Lambda", "ECS / Fargate"]
related: ["SNS", "Kinesis", "Lambda", "ECS / Fargate"]
tags: [aws, sqs, messaging, queue, decoupling, async, cloud]
---

# SQS

## ⚡ TL;DR

**SQS (Simple Queue Service)** is managed message queuing. Producers send messages; consumers poll and process; messages deleted after processing. Two types: **Standard** (at-least-once, unordered, unlimited throughput) and **FIFO** (exactly-once, ordered, 3000 msg/sec). Key features: visibility timeout (prevents duplicate processing), dead-letter queues (failed messages), long polling (efficient). The backbone of AWS async decoupling.

---

## 🔥 Problem This Solves

Service A calls Service B synchronously: B is slow/down → A fails. Solution: A writes to SQS queue, returns immediately. B polls queue, processes at its own pace. Services are decoupled: B's slowness doesn't affect A, B can scale independently, and messages survive B's downtime.

---

## 📘 Textbook Definition

Amazon SQS is a fully managed message queuing service that decouples and scales microservices, distributed systems, and serverless applications. SQS eliminates the complexity and overhead associated with managing and operating message-oriented middleware, enabling developers to focus on differentiating work.

---

## ⏱️ 30 Seconds

```
Standard Queue:
  - At-least-once delivery (duplicates possible)
  - Best-effort ordering
  - Unlimited throughput
  - Price: $0.40/million messages

FIFO Queue:
  - Exactly-once processing
  - Strict ordering per Message Group ID
  - 3000 msg/sec (with batching), 300/sec without
  - Price: $0.50/million messages

Key settings:
  Visibility Timeout: 30s (how long message hidden after read)
  Message Retention: 4 days default (max 14 days)
  Max Message Size: 256KB (use S3 for larger)
  Long Polling: ReceiveMessageWaitTimeSeconds=20 (efficient)
```

---

## 🔩 First Principles

- **Pull model**: consumers poll SQS; SQS does NOT push to consumers (SNS does)
- **Visibility timeout**: when consumer reads message, it becomes invisible; if processing fails and consumer crashes, timeout expires → message reappears for retry
- **At-least-once**: Standard queues can deliver message more than once; design consumers to be idempotent
- **Dead-letter queue (DLQ)**: after N failed processing attempts, message moved to DLQ for inspection
- **Long polling**: `ReceiveMessageWaitTimeSeconds=20` waits up to 20s for messages (reduces empty polls = cheaper)
- **Message deduplication**: FIFO queues deduplicate based on `MessageDeduplicationId` within 5-minute window

---

## 🧪 Thought Experiment

Order service receives 10K orders/min at peak. Payment service can process 1K orders/min. Without SQS: payment service would need to scale 10x. With SQS: order service enqueues all 10K messages instantly, payment service processes at its 1K/min rate, queue builds up during peak, drains during off-peak. No messages lost, no synchronous blocking, payment service scales to queue depth.

---

## 🧠 Mental Model / Analogy

SQS is a **postal mailbox**: sender (producer) drops a letter (message) in the mailbox and walks away. The postal service (SQS) holds it safely. Recipient (consumer) checks the mailbox at their own pace, takes the letter, signs for it (visibility timeout), and throws it away after reading (delete message). If the recipient doesn't sign, the letter goes back in the mailbox (message reappears after timeout). Too many reappearances → letter forwarded to dead letter department (DLQ).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Create standard queue. Producer sends messages. Consumer polls, processes, deletes messages. Enable DLQ for failed messages. Use long polling.

**Level 2 - Practitioner**: Visibility timeout: set to max expected processing time + buffer. DLQ: set `maxReceiveCount=5` (retry 5 times before DLQ). Lambda → SQS trigger: Lambda polls automatically, scales to queue depth. Batch size: Lambda can process 1-10 messages per invocation.

**Level 3 - Advanced**: FIFO queue: `MessageGroupId` = ordering key (all messages with same GroupId processed in order). `MessageDeduplicationId` for idempotency. Large message handling: store payload in S3, send S3 key in SQS message. SQS Extended Client Library (Java): handles S3 offloading automatically. Fan-out pattern: SNS topic → multiple SQS queues.

**Level 4 - Expert**: SQS backpressure: monitor `ApproximateNumberOfMessagesVisible` CloudWatch metric → auto-scale consumers via target tracking (queue depth per instance). SQS message attributes: metadata (type, priority) without parsing message body. Priority queues: use multiple SQS queues with different consumer counts (no native priority). Poison pill prevention: DLQ + alarm → alert team, inspect malformed messages. Message ordering in Standard queues: not guaranteed; if strict order needed, use FIFO or include sequence number in message + idempotent processing.

---

## ⚙️ How It Works

### SQS (Terraform)

```hcl
# Dead-letter queue
resource "aws_sqs_queue" "dlq" {
  name                        = "orders-dlq"
  message_retention_seconds   = 1209600  # 14 days
  kms_master_key_id           = "alias/aws/sqs"
}

# Main queue with DLQ
resource "aws_sqs_queue" "orders" {
  name                        = "orders"
  visibility_timeout_seconds  = 300        # 5 min (match Lambda max timeout)
  message_retention_seconds   = 86400      # 1 day
  receive_wait_time_seconds   = 20         # long polling

  # Server-side encryption
  kms_master_key_id           = aws_kms_key.sqs.arn
  kms_data_key_reuse_period_seconds = 300

  # Dead-letter queue config
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5    # retry 5x before DLQ
  })
}

# Queue policy: allow SNS to send
resource "aws_sqs_queue_policy" "orders" {
  queue_url = aws_sqs_queue.orders.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "sns.amazonaws.com" }
      Action    = "SQS:SendMessage"
      Resource  = aws_sqs_queue.orders.arn
      Condition = {
        ArnLike = { "aws:SourceArn" = aws_sns_topic.orders.arn }
      }
    }]
  })
}

# FIFO Queue (for ordered processing)
resource "aws_sqs_queue" "payments_fifo" {
  name                        = "payments.fifo"    # FIFO: must end with .fifo
  fifo_queue                  = true
  content_based_deduplication = true               # auto-dedup by content hash
  visibility_timeout_seconds  = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.payments_dlq.arn  # DLQ also .fifo
    maxReceiveCount     = 3
  })
}
```

### SQS Producer (Java Spring Boot)

```java
@Service
public class OrderEventPublisher {

    private final SqsTemplate sqsTemplate;   // Spring Cloud AWS

    @Value("${aws.sqs.orders-queue-url}")
    private String ordersQueueUrl;

    public void publishOrderCreated(Order order) {
        OrderEvent event = OrderEvent.builder()
            .eventType("ORDER_CREATED")
            .orderId(order.getId())
            .userId(order.getUserId())
            .amount(order.getAmount())
            .timestamp(Instant.now())
            .build();

        // Spring Cloud AWS SQS
        sqsTemplate.send(ordersQueueUrl, event);
    }

    // With message attributes for routing
    public void publishWithAttributes(Order order) {
        sqsTemplate.send(to -> to
            .queue(ordersQueueUrl)
            .payload(order)
            .header("eventType", "ORDER_CREATED")
            .header("priority", "HIGH")
        );
    }
}
```

### SQS Consumer (Spring Boot with @SqsListener)

```java
@Service
public class OrderEventConsumer {

    // Spring Cloud AWS automatically handles:
    // - Long polling
    // - Message deletion after successful processing
    // - Retry on exception (message reappears after visibility timeout)
    @SqsListener(value = "${aws.sqs.orders-queue-url}",
                 maxNumberOfMessages = "10",          // batch up to 10
                 visibilityTimeout = "300")
    public void processOrderEvent(OrderEvent event,
                                   @Header("eventType") String eventType) {
        log.info("Processing {} for order {}", eventType, event.getOrderId());

        try {
            switch (eventType) {
                case "ORDER_CREATED" -> processNewOrder(event);
                case "ORDER_CANCELLED" -> cancelOrder(event);
                default -> log.warn("Unknown event type: {}", eventType);
            }
        } catch (RetryableException e) {
            // Throw to let message reappear for retry
            throw e;
        } catch (PoisonPillException e) {
            // Log + do NOT rethrow; let message go to DLQ after maxReceiveCount
            log.error("Poison pill detected for order {}: {}", event.getOrderId(), e);
        }
    }

    // Idempotent processing (critical for at-least-once delivery)
    private void processNewOrder(OrderEvent event) {
        // Check if already processed using idempotency key
        if (orderProcessingRepository.isProcessed(event.getOrderId())) {
            log.info("Order {} already processed, skipping", event.getOrderId());
            return;
        }

        // Process...
        // Mark as processed
        orderProcessingRepository.markProcessed(event.getOrderId());
    }
}
```

---

## ⚖️ Comparison Table: SQS vs SNS vs Kinesis

|               | SQS                    | SNS                    | Kinesis              |
| ------------- | ---------------------- | ---------------------- | -------------------- |
| **Pattern**   | Queue (pull)           | Pub/Sub (push)         | Stream               |
| **Consumers** | Competing consumers    | Fan-out to many        | Multiple independent |
| **Ordering**  | FIFO option            | No                     | Shard-level          |
| **Retention** | 14 days                | None                   | 24hr-365 days        |
| **Replay**    | ❌                     | ❌                     | ✅                   |
| **Use case**  | Task queue, decoupling | Notifications, fan-out | Real-time analytics  |

---

## ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                             |
| ---------------------------------------- | ----------------------------------------------------------------------------------- |
| "SQS at-least-once = rarely duplicate"   | Duplicates can happen; always design consumers to be idempotent                     |
| "FIFO guarantees global ordering"        | FIFO ordering is per MessageGroupId; different group IDs process independently      |
| "Long polling is always enabled"         | Default `ReceiveMessageWaitTimeSeconds=0` (short polling); explicitly set to 20     |
| "DLQ messages are automatically retried" | DLQ is a holding area; you must manually inspect and redrive (or set up automation) |

---

## 🔗 Related Keywords

- [SNS](/cloud-aws/sns/) - fan-out from one topic to multiple SQS queues
- [Kinesis](/cloud-aws/kinesis/) - streaming alternative for ordered, replayable events
- [Lambda](/cloud-aws/lambda/) - serverless SQS consumer

---

## 📌 Quick Reference Card

```bash
# Send message
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/orders \
  --message-body '{"orderId":"123","userId":"user-456"}'

# Receive messages (long poll)
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/orders \
  --max-number-of-messages 10 \
  --wait-time-seconds 20

# Delete message after processing
aws sqs delete-message \
  --queue-url https://... \
  --receipt-handle "AQEBwJnKyrHigUMZj6reyNurG..."

# Get queue depth
aws sqs get-queue-attributes \
  --queue-url https://... \
  --attribute-names ApproximateNumberOfMessages

# Redrive DLQ messages back to source
aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:123456789:orders-dlq \
  --destination-arn arn:aws:sqs:us-east-1:123456789:orders
```

---

## 🧠 Think About This

The visibility timeout is the most misunderstood SQS parameter. Set it too short: processing takes longer than timeout → message reappears → another consumer picks it up → duplicate processing. Set it too long: a consumer crashes at the start of processing → message is invisible to other consumers for the full timeout duration → system appears stuck with no visible sign. Rule: `visibilityTimeout = max(expected processing time) × 1.5`. If processing time is variable, use `ChangeMessageVisibility` to extend the timeout dynamically during long processing. And always design for idempotency in consumers - the at-least-once delivery guarantee means duplicates WILL happen in distributed systems. An idempotent consumer processes the same message 1 or 100 times with the same result.
