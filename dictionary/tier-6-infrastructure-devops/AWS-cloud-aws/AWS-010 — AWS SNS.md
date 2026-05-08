---
layout: default
title: "AWS SNS"
parent: "Cloud — AWS"
nav_order: 10
permalink: /cloud-aws/aws-sns/
id: AWS-010
category: Cloud — AWS
difficulty: ★★☆
depends_on: Pub/Sub Pattern, AWS, Distributed Systems
used_by: AWS SNS + SQS Fan-Out Pattern, Cloud — AWS
related: AWS SQS, AWS Kinesis, EventBridge
tags:
  - aws
  - cloud
  - messaging
  - intermediate
  - distributed
---

# AWS-010 — AWS SNS

⚡ **TL;DR —** AWS's managed pub/sub service that pushes a single message to multiple subscribers simultaneously, enabling fan-out without producer coupling to each consumer.

| Attribute    | Value                                        |
|--------------|----------------------------------------------|
| Depends on   | Pub/Sub Pattern, AWS, Distributed Systems    |
| Used by      | AWS SNS + SQS Fan-Out Pattern, Cloud — AWS   |
| Related      | AWS SQS, AWS Kinesis, EventBridge            |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Service A processes an order. It must notify: the fulfilment service, the email service, the analytics service, and the fraud-detection service. Service A calls each synchronously — four HTTP calls, four possible failures, four retry loops. Adding a fifth consumer requires changing Service A's code. A is tightly coupled to every downstream system.

**THE BREAKING POINT:** The fraud-detection team wants to subscribe to order events. They cannot deploy their service until Service A is updated. Service A's team is busy. The change is delayed three sprints. Meanwhile, fulfilment and email are coupled together in A's retry logic — a slow email service degrades order processing. Every new consumer multiplies A's blast radius.

**THE INVENTION MOMENT:** What if Service A published to a single topic and every interested system subscribed independently? A sends one message. SNS fans it out to all subscribers immediately. Adding a new subscriber requires no change to Service A. Slow or failing subscribers do not affect each other or the producer.

---

### 📘 Textbook Definition

**AWS Simple Notification Service (SNS)** is a fully managed publish/subscribe messaging service that decouples message producers from consumers through topics. Publishers send a single message to a **topic**; SNS delivers that message to all confirmed **subscriptions** simultaneously. Supported subscriber protocols include Amazon SQS, AWS Lambda, HTTP/S endpoints, email, SMS, and mobile push (APNS, FCM). SNS supports **subscription filter policies** (JSON attribute matching) so subscribers receive only the messages they care about. SNS Standard topics offer unlimited throughput; FIFO topics provide strict ordering and deduplication at up to 300 msg/s. Messages are not durably stored — SNS delivers immediately or drops; subscribers must use SQS for durability.

---

### ⏱️ Understand It in 30 Seconds

**One line:** SNS is a broadcast tower — publish once, deliver simultaneously to every subscriber.

> Think of a public address system at a stadium: the announcer speaks once into the microphone, and every section of the stadium hears it simultaneously — even though each section is listening on its own speaker.

**One insight:** SNS is not a queue — it does not store messages. If a subscriber is unavailable when SNS attempts delivery, the message is lost (unless the subscriber is an SQS queue, which provides its own durability). SNS + SQS together give you both fan-out and durability.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A message published once should be deliverable to N subscribers without the producer managing N connections.
2. Producers should not know about consumers — adding subscribers is a subscriber-side concern.
3. Fan-out throughput must not degrade as subscriber count grows — delivery is parallelised.
4. Messages are ephemeral — durable storage is a concern for the subscriber (SQS), not the broker.

**DERIVED DESIGN:**

SNS decouples topic publication from subscriber delivery. When a message is published to a topic ARN, SNS internally fans it out to all confirmed subscriptions in parallel. Each delivery attempt is independent — a failure for one HTTP endpoint does not affect SQS delivery. Subscription filter policies are evaluated at the SNS layer — subscribers that do not match receive nothing, reducing noise and cost downstream.

**THE TRADE-OFFS:**

**Gain:** Zero producer code changes when adding or removing subscribers. Independent failure domains per subscriber. Subscription filter policies reduce downstream load. Supports heterogeneous subscriber types in a single fan-out (Lambda + SQS + email from one message).

**Cost:** No message durability in SNS itself — use SQS subscriptions for persistence. SNS HTTP delivery has limited retry logic (23 retries over 23 days, exponential backoff). SNS FIFO is limited to SQS FIFO subscribers only. Message size limit is 256 KB.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce platform processes order events. Three consumers need order data: fulfilment (SQS), analytics (Lambda), fraud detection (HTTPS endpoint). New consumer requirement: a loyalty-points service.

**WHAT HAPPENS WITHOUT SNS:** Order service has a list of three HTTP endpoints and calls each in sequence. Adding loyalty-points requires: (1) code change in order service, (2) code review, (3) deployment. A slow fraud-detection endpoint makes the order service wait. If analytics endpoint is down, the order service retries and blocks order confirmation.

**WHAT HAPPENS WITH SNS:** Order service publishes to `orders-topic`. Three subscriptions exist. Loyalty-points team creates a new SQS subscription to the same topic — zero changes to order service. SNS delivers to all four subscriptions in parallel. Slow fraud-detection does not affect fulfilment delivery timing. Downstream failures are invisible to the producer.

**THE INSIGHT:** SNS inverts the dependency direction. Instead of the producer maintaining a list of consumers, consumers register their interest. The producer's code is frozen while the system's capability grows.

---

### 🧠 Mental Model / Analogy

> SNS is like a newspaper publisher. The publisher prints one edition and distributes it simultaneously to all subscribers. Each subscriber (home delivery, newsstands, digital) receives their copy independently. A missed delivery at one newsstand does not affect home delivery. Adding a new subscriber does not require reprinting the newspaper.

- **Newspaper publisher** → Your application (SNS publisher)
- **Newspaper edition** → The SNS message payload
- **Distribution channels** → SNS subscriptions (SQS, Lambda, HTTP, email, SMS)
- **Subscribers** → Consumer services
- **Subscription filter** → "Only deliver sports section to sports subscribers"
- **Out-of-stock newsstand** → Unavailable HTTP endpoint (delivery fails; others unaffected)

Where this analogy breaks down: unlike a physical newspaper, SNS delivery is near-instantaneous to all subscribers simultaneously, not sequential. And SNS does not store the newspaper — if you miss delivery, there is no back-issue.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
SNS is a megaphone: you say something once, and everyone who signed up to listen hears it at the same time.

**Level 2 — How to use it (junior developer):**
Create an SNS topic. Subscribe an SQS queue or Lambda to it. Publish a message using the AWS SDK or CLI:
```bash
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789:orders \
  --message '{"orderId":"abc","total":99.99}' \
  --message-attributes \
    '{"eventType":{"DataType":"String","StringValue":"OrderCreated"}}'
```
All subscriptions with matching filter policies receive the message.

**Level 3 — How it works (mid-level engineer):**
SNS topics store subscription metadata (ARNs, protocols, filter policies). On `Publish`, SNS evaluates each subscription's `FilterPolicy` (a JSON map of attribute → value matchers). Matching subscriptions receive a delivery attempt in parallel. SQS subscriptions use the SQS `SendMessage` API — failures are retried per SQS guarantees. Lambda subscriptions invoke the function asynchronously — SNS retries on Lambda throttle or error (up to 3 attempts, then optional DLQ on the subscription). HTTP/S subscriptions have a configurable retry policy (up to 23 retries over 23 days). SNS does not retry for email or SMS — best-effort only.

**Level 4 — Why it was designed this way (senior/staff):**
SNS's fire-and-forget model is intentional: the service is optimised for fan-out throughput, not delivery guarantees. Durable delivery is delegated to the subscriber type — SQS provides durability, Lambda provides async invocation with its own retry. This separation of concerns means SNS can fan out to thousands of subscriptions without becoming a bottleneck on persistence writes. The 256 KB message size limit exists because SNS is a notification service — it signals that something happened, not a data transfer mechanism. For large payloads, the SNS-to-S3 extended client pattern stores the payload in S3 and passes a reference. FIFO topics limit subscribers to SQS FIFO because ordered delivery requires a receiver that can enforce per-group ordering — Lambda and HTTP endpoints cannot guarantee in-order processing.

---

### ⚙️ How It Works (Mechanism)

```
+-----------------------------------------------+
| Publisher: sns.publish(topicArn, message,     |
|            messageAttributes)                 |
|       |                                       |
|       v                                       |
| SNS Topic: evaluate all subscriptions         |
|  -> FilterPolicy match?                       |
|  -> YES: attempt delivery per protocol        |
|  -> NO:  skip subscriber                      |
|       |                                       |
|  Parallel delivery to:                        |
|   [SQS Queue A] -> SendMessage                |
|   [Lambda B]    -> InvokeFunction (async)     |
|   [HTTPS C]     -> HTTP POST                  |
|   [Email D]     -> SMTP (best-effort)         |
|       |                                       |
| Failed delivery:                              |
|   SQS: retried by SQS                        |
|   Lambda: 3 retries then sub DLQ             |
|   HTTP: 23 retries over 23 days              |
+-----------------------------------------------+
```

**Topic ARN format:** `arn:aws:sns:<region>:<account>:<topic-name>`

**Message Attributes** (for filter policy matching):

```json
{
  "eventType": { "DataType": "String", "StringValue": "OrderCreated" },
  "amount":    { "DataType": "Number", "StringValue": "99.99" },
  "region":    { "DataType": "String", "StringValue": "EU" }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Order Service
  |
  v
sns.publish(topic, message, attributes)  <- YOU ARE HERE
  |
  v
SNS evaluates 4 subscriptions in parallel:
  |
  +-> SQS:orders-fulfilment (no filter)
  |     -> SendMessage -> fulfilment Lambda polls
  |
  +-> Lambda:analytics (filter: eventType=OrderCreated)
  |     -> InvokeFunction async
  |
  +-> HTTPS:fraud-api (filter: amount > 500)
  |     -> HTTP POST to fraud-detection endpoint
  |
  +-> SQS:loyalty-points (filter: region=EU)
        -> SendMessage -> loyalty Lambda polls
  |
  v
All deliveries complete independently
Order service receives publish confirmation
(does not wait for subscriber processing)
```

**FAILURE PATH:** HTTPS endpoint returns 5xx → SNS retries with exponential backoff (23 retries over 23 days). SQS unavailable → SNS retries (SQS is highly available, rarely fails). Lambda throttled → SNS retries 3 times; if all fail, message goes to subscription DLQ (if configured). Email → no retry; best-effort only.

**WHAT CHANGES AT SCALE:** SNS parallelises delivery per subscription, so adding subscribers does not increase per-message publish latency. At very high publish rates (>100k msg/s), Lambda subscriber invocations can cause Lambda concurrency limits to be hit — use SQS as a buffer between SNS and Lambda to absorb bursts.

---

### 💻 Code Example

**BAD — Producer directly calls all downstream services:**
```python
# Order service coupled to every downstream consumer
# Adding fraud-detection required changing this function
def process_order(order):
    complete_order(order)
    # Tightly coupled - any failure here = order fails
    fulfilment_client.notify(order)
    analytics_client.track(order)
    fraud_client.check(order)      # slow -> blocks order
    # Adding loyalty requires deploying order service
```

**GOOD — Publish to SNS topic; subscribers self-register:**
```python
import boto3, json

sns = boto3.client('sns')
TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:orders'

def process_order(order):
    complete_order(order)
    # Single publish - downstream teams subscribe independently
    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(order),
        MessageAttributes={
            'eventType': {
                'DataType': 'String',
                'StringValue': 'OrderCreated'
            },
            'region': {
                'DataType': 'String',
                'StringValue': order['region']
            },
            'amount': {
                'DataType': 'Number',
                'StringValue': str(order['total'])
            }
        }
    )
    # Returns immediately; fan-out is SNS's responsibility
```

```yaml
# CloudFormation: SNS + SQS fan-out with filter policy
FraudSubscription:
  Type: AWS::SNS::Subscription
  Properties:
    TopicArn: !Ref OrdersTopic
    Protocol: sqs
    Endpoint: !GetAtt FraudQueue.Arn
    FilterPolicy:
      amount:
        - numeric: [">=", 500]
      region:
        - "EU"
        - "US"
```

---

### ⚖️ Comparison Table

| Feature             | AWS SNS          | AWS SQS          | AWS EventBridge  | AWS Kinesis      |
|---------------------|------------------|------------------|------------------|------------------|
| Pattern             | Pub/Sub (push)   | Queue (pull)     | Event bus (routing)| Streaming (pull)|
| Message storage     | No (ephemeral)   | Yes (up to 14d)  | No               | Yes (up to 365d) |
| Fan-out             | Yes (native)     | 1 consumer/msg   | Yes (rules)      | Via fan-out      |
| Ordering            | FIFO topic (300/s)| FIFO queue      | No guarantee     | Per shard        |
| Replay              | No               | No               | Archive + replay | Yes              |
| Filter/routing      | Attribute filter | No               | Content-based    | Partition key    |
| Subscriber types    | SQS,Lambda,HTTP  | Pull consumers   | Lambda,SQS,HTTP  | KCL, Lambda      |
| Max msg size        | 256 KB           | 256 KB           | 256 KB           | 1 MB/shard       |

---

### 🔁 Flow / Lifecycle

**Message Delivery Lifecycle:**

```
+-----------------------------------------------+
| 1. PUBLISHED  -> sns.publish() called;        |
|               message accepted by SNS         |
| 2. EVALUATED  -> FilterPolicy checked per sub |
| 3. DISPATCHED -> Delivery attempt per         |
|               matching subscription (parallel)|
| 4. DELIVERED  -> Subscriber confirms receipt  |
|               (SQS/Lambda acknowledge)        |
| 5. RETRYING   -> Delivery failed; retry per   |
|               protocol retry policy           |
| 6. DEAD       -> Retries exhausted; message   |
|               sent to subscription DLQ        |
|               (if configured) or dropped      |
+-----------------------------------------------+
```

**Subscription Confirmation Lifecycle (HTTP/S):**

1. **Subscribe** — Create subscription with HTTPS endpoint URL
2. **Pending Confirmation** — SNS sends `SubscriptionConfirmation` POST to endpoint
3. **Confirm** — Endpoint must GET the `SubscribeURL` from the payload
4. **Active** — Subscription confirmed; messages delivered
5. **Unsubscribe** — `Unsubscribe` URL in each message or explicit API call

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "SNS is a queue like SQS" | SNS has no message storage. It is a push-based fan-out broker. Messages not delivered are lost unless an SQS subscription provides durability. |
| "SNS delivers in order" | Standard topics do not guarantee ordering. Only FIFO topics guarantee ordering, but only to SQS FIFO subscribers. |
| "All subscribers receive every message" | Subscription filter policies mean a subscriber only receives messages whose attributes match its filter. No filter = receives all messages. |
| "SNS retries failed HTTP delivery forever" | HTTP/S retries are capped at 23 retries over ~23 days. After exhaustion the message is dropped (unless a subscription DLQ is configured). |
| "SNS fan-out increases publish latency" | SNS delivers to all subscriptions in parallel. Publish latency is the time to accept the message, not the time to deliver to all subscribers. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 — Subscribers not receiving messages (filter policy mismatch)**

**Symptom:** Messages published to topic but specific SQS queue receives nothing; other queues receive normally.
**Root Cause:** Subscription FilterPolicy does not match the published message attributes — attribute name typo, value mismatch, or publisher not sending required attributes.
**Diagnostic:**
```bash
# Check the subscription filter policy
aws sns get-subscription-attributes \
  --subscription-arn \
    arn:aws:sns:us-east-1:123:orders:abc-def-123 \
  | jq '.Attributes.FilterPolicy'

# Check what attributes the publisher sends
# by temporarily subscribing an SQS queue with no filter
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123:orders \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:...:debug-queue
```
**Fix:** Verify attribute names and values in FilterPolicy match exactly (case-sensitive) what the publisher sends. Test with a no-filter subscription to confirm messages are published.
**Prevention:** Document and enforce message attribute schema. Use SNS message validation in integration tests.

---

**Mode 2 — HTTP subscriber receives duplicate messages**

**Symptom:** HTTPS endpoint receives the same SNS notification multiple times within seconds.
**Root Cause:** Endpoint returns 5xx or times out on the first delivery; SNS retries. Endpoint processed the first delivery but SNS timed out before receiving the 200 response.
**Diagnostic:**
```bash
# Check SNS delivery status logs (enable in topic config)
aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123:orders \
  --attribute-name HTTPSuccessFeedbackRoleArn \
  --attribute-value arn:aws:iam::123:role/sns-feedback
# Then check CloudWatch log group: sns/<region>/<account>/orders
```
**Fix:** Implement idempotency on the HTTP endpoint using the SNS `MessageId` header as a deduplication key. Store processed `MessageId` values with TTL in DynamoDB or Redis.
**Prevention:** Every SNS HTTP subscriber must be idempotent. SNS guarantees at-least-once delivery — duplicates are possible on success, not just on failure.

---

**Mode 3 — Messages lost when Lambda subscriber throttled**

**Symptom:** Under high load, some SNS-triggered Lambda invocations are silently dropped; no DLQ captures them.
**Root Cause:** Lambda is throttled (concurrency limit hit). SNS retries 3 times; all fail. No subscription DLQ configured — messages are dropped silently.
**Diagnostic:**
```bash
# Check Lambda throttle metric
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions \
    Name=FunctionName,Value=my-sns-consumer \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 60 --statistics Sum
```
**Fix:** Configure a Dead Letter Queue on the SNS subscription (`RedrivePolicy`). Better: subscribe an SQS queue to SNS instead of subscribing Lambda directly — SQS provides durability and Lambda processes from SQS at a sustainable rate.
**Prevention:** For any critical SNS→Lambda integration, insert an SQS queue between SNS and Lambda. This provides durability, backpressure, and controllable Lambda concurrency.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Pub/Sub Pattern — the general messaging pattern SNS implements
- AWS — IAM, topic ARN format, resource policies, AWS SDK
- Distributed Systems — fan-out, event-driven architecture, loose coupling

**Builds On This (learn these next):**
- AWS SQS — combine with SNS for durable fan-out (SNS+SQS fan-out pattern)
- AWS EventBridge — content-based routing with richer filtering and schema registry
- AWS Lambda — most common SNS subscriber for serverless event processing

**Alternatives / Comparisons:**
- AWS EventBridge — richer event routing with schema registry, archive/replay; use for complex event-driven architectures
- AWS Kinesis — use when consumers need ordered, replayable streams rather than fan-out notifications
- Google Pub/Sub — GCP equivalent with message storage and pull/push options

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Managed pub/sub fan-out service   |
| PROBLEM      | Producer coupled to N consumers   |
| KEY INSIGHT  | Publish once; SNS fans out in     |
|              | parallel; consumers self-register |
| USE WHEN     | Fan-out, event notification       |
| AVOID WHEN   | Need durable storage or ordering  |
| TRADE-OFF    | Decoupling vs no message storage  |
| ONE-LINER    | SNS push + SQS pull = durable     |
|              | fan-out (SNS+SQS pattern)         |
| NEXT EXPLORE | AWS SQS, EventBridge              |
+--------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** You need to fan out order events to 5 services. Three are internal (SQS + Lambda), one is an external partner (HTTPS webhook), one is an analytics system that can only consume from Kinesis. How do you design the SNS subscriptions, and what durability gaps does each subscriber type introduce?

2. **(System Interaction)** You configure an SNS FilterPolicy on an SQS subscription: only messages with `eventType = OrderShipped` should be delivered. Your publisher sends `eventType = order_shipped` (snake_case). What happens, and how would you detect this misconfiguration before it reaches production?

3. **(Scale)** Your SNS topic fans out to 50 Lambda subscribers. A sudden spike of 100 000 messages/minute is published. Each Lambda has a reserved concurrency of 100. Describe the failure cascade, the SNS behaviour, and the architectural pattern that prevents message loss.
