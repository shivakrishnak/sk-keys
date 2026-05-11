---
layout: default
title: "Async and Background Processing - Observability"
parent: "Async and Background Processing"
grand_parent: "Interview Mastery"
nav_order: 5
permalink: /interview/async-background/observability/
topic: Async and Background Processing
subtopic: Observability
keywords:
  - Async Observability
  - Consumer Lag Monitoring
  - Async Error Handling
  - Async Trade-offs
  - Event-Driven vs Request-Response
  - Flow Control
  - Async Architecture Selection
difficulty_range: mixed
status: complete
version: 1
---

# Async Observability

**TL;DR** - Async observability means tracking messages across decoupled services using correlation IDs, distributed tracing, and queue-specific metrics to diagnose issues in systems where there's no request-response to trace.

---

### The Problem This Solves

**WORLD WITHOUT ASYNC OBSERVABILITY:**
A customer reports their order never shipped. The order service shows "created." Kafka has 12 million messages across 50 partitions. The shipping consumer has 3 instances. Which message is the order? Did it reach the consumer? Did the consumer fail? Where in the pipeline did it stop? You have no way to trace an async flow.

---

### How It Works

```
SYNC OBSERVABILITY (easy):
[Request] -> [Service A] -> [Service B] -> [Response]
  Single trace ID follows the entire call chain

ASYNC OBSERVABILITY (hard):
[Producer] -> [Broker] -> [Consumer 1]
                       -> [Consumer 2]
  No response to trace back
  Message might sit in queue for hours
  Consumer might fail silently

SOLUTION:
[Producer]          [Broker]        [Consumer]
  correlationId=X     msg.header=X    correlationId=X
  traceId=Y           --              traceId=Y (new span)
  span: "publish"     --              span: "consume"
     |                                    |
  [Distributed Trace: Y]
    publish --delay-- consume -- process
```

**Three pillars for async:**

1. **Correlation IDs:** Thread a unique ID through every message so you can trace a business flow
2. **Distributed tracing:** Propagate trace context (OpenTelemetry) in message headers
3. **Queue metrics:** Consumer lag, processing time, DLQ depth, error rates

---

### Code Example

```java
// Producer: propagate trace context
public void publish(OrderCreatedEvent event) {
    String correlationId = UUID.randomUUID()
        .toString();
    ProducerRecord<String, Object> record =
        new ProducerRecord<>(
            "order-events", event.orderId(), event);
    // Inject trace context into headers
    record.headers().add("correlationId",
        correlationId.getBytes());
    record.headers().add("traceparent",
        Span.current().getSpanContext()
            .getTraceId().getBytes());
    kafkaTemplate.send(record);
    log.info("Published order event "
        + "correlationId={}", correlationId);
}

// Consumer: extract and continue trace
@KafkaListener(topics = "order-events")
public void handle(ConsumerRecord<String, Object>
        record) {
    String correlationId = new String(
        record.headers()
            .lastHeader("correlationId").value());
    MDC.put("correlationId", correlationId);
    try {
        processOrder(record.value());
        log.info("Processed order "
            + "correlationId={}", correlationId);
    } catch (Exception e) {
        log.error("Failed correlationId={} "
            + "partition={} offset={}",
            correlationId,
            record.partition(),
            record.offset(), e);
        throw e;
    } finally {
        MDC.remove("correlationId");
    }
}
```

---

### Essential Metrics Dashboard

| Metric                 | Source          | Alert threshold          |
| ---------------------- | --------------- | ------------------------ |
| Consumer lag           | Kafka/Burrow    | > 10,000 messages        |
| Processing latency p99 | Consumer app    | > 5s for critical topics |
| DLQ depth              | DLQ topic/queue | > 0 (investigate)        |
| Error rate             | Consumer app    | > 1% of messages         |
| End-to-end latency     | Trace system    | > SLA threshold          |
| Queue depth            | Broker metrics  | Sustained growth         |

---

### Quick Recall

**If you remember only 3 things:**

1. Always propagate correlation IDs and trace context in message headers
2. Consumer lag is the #1 metric for async health - monitor it before anything else
3. DLQ depth > 0 means messages are failing silently - alert immediately

**Interview one-liner:**
"I make async systems observable by propagating correlation IDs and OpenTelemetry trace context in message headers, monitoring consumer lag as the primary health metric, and alerting on DLQ depth for silent failures."

---

---

# Consumer Lag Monitoring

**TL;DR** - Consumer lag measures how many messages a consumer group hasn't processed yet, revealing whether consumers are keeping pace with producers.

---

### The Problem This Solves

Your Kafka consumers process 5,000 msg/sec, but producers suddenly spike to 15,000 msg/sec during a flash sale. Without lag monitoring, you don't know consumers are falling behind until customers report orders not processing.

---

### How It Works

```
KAFKA PARTITION (topic: order-events)
Messages: [0][1][2][3][4][5][6][7][8][9]
                          ^              ^
                    consumer offset    log end offset
                    (last committed)   (latest message)

Consumer Lag = Log End Offset - Consumer Offset
             = 9 - 5 = 4 messages behind

HEALTHY:   lag = 0-100 (caught up)
WARNING:   lag = 1,000+ and growing
CRITICAL:  lag = 100,000+ or growing 1K/min
```

---

### Monitoring Tools

```bash
# Native Kafka tool
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group shipping-service

# Output:
# TOPIC      PARTITION  CURRENT  LOG-END  LAG
# orders     0          4523     4530     7
# orders     1          8901     12450    3549  <-- ALERT!
# orders     2          6780     6782     2
```

```java
// Programmatic lag check with Spring Kafka
@Component
public class LagMonitor {
    private final ConsumerFactory<?, ?> factory;

    @Scheduled(fixedRate = 30_000)
    public void checkLag() {
        try (Consumer<?, ?> consumer =
                factory.createConsumer()) {
            Map<TopicPartition, Long> endOffsets =
                consumer.endOffsets(partitions);
            // Compare with committed offsets
            for (var entry : endOffsets.entrySet()) {
                long committed = consumer.committed(
                    Set.of(entry.getKey()))
                    .get(entry.getKey()).offset();
                long lag =
                    entry.getValue() - committed;
                if (lag > THRESHOLD) {
                    alertService.fire(
                        "High consumer lag: " + lag);
                }
            }
        }
    }
}
```

---

### Remediation Strategies

| Lag cause            | Fix                                        |
| -------------------- | ------------------------------------------ |
| Slow processing      | Optimize consumer logic, batch processing  |
| Not enough consumers | Add consumers (up to partition count)      |
| Uneven partitions    | Rebalance partitions, fix key distribution |
| Consumer crash loop  | Fix the bug, check DLQ                     |
| Producer burst       | Auto-scale consumers, backpressure         |

---

### Quick Recall

**If you remember only 3 things:**

1. Consumer lag = log end offset - consumer committed offset
2. Growing lag means consumers can't keep up - scale consumers or optimize processing
3. Max useful consumers = number of partitions (Kafka assigns one partition per consumer)

**Interview one-liner:**
"Consumer lag is the difference between the latest message offset and the consumer's committed offset - I monitor it as the primary Kafka health metric and scale consumers up to partition count when lag grows."

---

---

# Async Error Handling

**TL;DR** - Async error handling addresses failures that occur outside the request-response cycle, where there's no caller waiting for a response to receive the error.

---

### The Problem This Solves

In sync processing, errors propagate up the call stack. The HTTP response carries the error to the client. In async processing, the producer is long gone when the consumer fails. There's nobody to report the error to. Failed messages disappear unless you explicitly handle them.

---

### Error Handling Strategies

```
STRATEGY 1: Retry with backoff
  Message -> Process FAIL
    -> Retry 1 (1s delay)
    -> Retry 2 (5s delay)
    -> Retry 3 (30s delay)
    -> Dead Letter Queue

STRATEGY 2: Dead Letter Queue (DLQ)
  [Main Queue] -> Consumer -> FAIL
                    -> [DLQ] -> Manual review
                             -> Automated retry later
                             -> Alert on DLQ growth

STRATEGY 3: Error topic/queue
  [Main Queue] -> Consumer -> FAIL
                    -> [Error Topic] with error details
                    -> [Error Handler Service]
                    -> Compensating action
```

---

### Code Example

```java
// Spring Kafka error handling
@Configuration
public class KafkaConfig {
    @Bean
    public ConcurrentKafkaListenerContainerFactory
            <String, Object> kafkaListenerFactory() {
        var factory = new ConcurrentKafka
            ListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        // Retry 3 times with backoff
        factory.setCommonErrorHandler(
            new DefaultErrorHandler(
                new DeadLetterPublishingRecoverer(
                    kafkaTemplate),
                new FixedBackOff(1000L, 3)));
        return factory;
    }
}

// RabbitMQ with retry + DLQ
@RabbitListener(queues = "orders")
public void handle(Order order, Channel ch,
        @Header(AmqpHeaders.DELIVERY_TAG) long tag)
        throws IOException {
    try {
        processOrder(order);
        ch.basicAck(tag, false);
    } catch (TransientException e) {
        // Requeue for retry
        ch.basicNack(tag, false, true);
    } catch (PermanentException e) {
        // Don't requeue, goes to DLQ
        ch.basicNack(tag, false, false);
        log.error("Permanent failure, "
            + "sending to DLQ: {}", order.getId());
    }
}
```

---

### Decision Matrix

| Error type         | Strategy        | Example                     |
| ------------------ | --------------- | --------------------------- |
| Transient          | Retry + backoff | Network timeout, DB lock    |
| Permanent          | DLQ immediately | Invalid data, missing field |
| Poison message     | DLQ + alert     | Causes consumer crash       |
| Business rule fail | Error topic     | Insufficient funds          |
| Unknown            | Retry then DLQ  | Default safe behavior       |

---

### Quick Recall

**If you remember only 3 things:**

1. Distinguish transient errors (retry) from permanent errors (DLQ immediately)
2. Always have a DLQ - it's your safety net for messages that can't be processed
3. Set max retry limits to prevent infinite loops; alert on DLQ growth

**Interview one-liner:**
"I classify async errors as transient (retry with exponential backoff) or permanent (send to DLQ immediately) - every queue must have a DLQ as a safety net, with alerts on DLQ depth."

---

---

# Async Trade-offs

**TL;DR** - Async processing gains throughput, resilience, and decoupling at the cost of complexity, eventual consistency, and harder debugging.

---

### The Complete Trade-off Matrix

| Dimension      | Sync                        | Async                                       |
| -------------- | --------------------------- | ------------------------------------------- |
| Latency        | Immediate response          | Delayed result                              |
| Throughput     | Limited by slowest call     | Producers and consumers scale independently |
| Coupling       | Tight (caller knows callee) | Loose (producer doesn't know consumers)     |
| Consistency    | Strong (immediate)          | Eventual                                    |
| Error handling | In call chain               | DLQ, compensation, retries                  |
| Debugging      | Stack trace                 | Distributed tracing, correlation IDs        |
| Ordering       | Guaranteed (call order)     | Must be engineered (partitioning)           |
| Availability   | All services must be up     | Producer works even if consumer is down     |
| Complexity     | Simple                      | More moving parts (broker, consumers, DLQ)  |
| Testing        | Unit/integration            | Contract tests, async assertions            |

---

### When to Go Async

**YES - go async when:**

- Operation takes > 1 second and user doesn't need immediate result
- Multiple services need to react to the same event
- Producer and consumer have different scaling needs
- System must work even when downstream is temporarily unavailable
- You need to smooth out traffic spikes

**NO - stay sync when:**

- User needs immediate confirmation (login, validation)
- Operation is fast (< 100ms)
- Strong consistency is required (financial debit/credit)
- Simple request-response with one downstream service
- Adding a broker adds more complexity than the problem warrants

---

### Quick Recall

**If you remember only 3 things:**

1. Async trades simplicity and consistency for throughput and resilience
2. Go async when operations are slow, multiple consumers exist, or services have different scaling needs
3. Stay sync for fast operations, immediate feedback, and strong consistency requirements

**Interview one-liner:**
"Async is worth the complexity when operations are slow or multiple services need to react independently - I stay sync for fast operations requiring immediate confirmation and strong consistency."

---

---

# Event-Driven vs Request-Response

**TL;DR** - Request-response uses direct synchronous calls between services; event-driven uses asynchronous events through a broker, each suited for different interaction patterns.

---

### Comparison

```
REQUEST-RESPONSE:
[Service A] ---HTTP---> [Service B]
            <--Response--
  A waits for B's response
  A knows about B (coupled)
  If B is down, A fails

EVENT-DRIVEN:
[Service A] --event--> [Broker] --event--> [Service B]
                                --event--> [Service C]
  A doesn't wait
  A doesn't know about B or C
  If B is down, events queue up
```

| Aspect         | Request-Response     | Event-Driven                  |
| -------------- | -------------------- | ----------------------------- |
| Communication  | Synchronous, direct  | Asynchronous, indirect        |
| Coupling       | A knows B's API      | A only knows event schema     |
| Failure impact | Cascading failures   | Isolated failures             |
| New consumers  | Modify producer      | Subscribe independently       |
| Debugging      | Trace one call chain | Trace across async boundaries |
| Data freshness | Real-time            | Eventually consistent         |
| Best for       | Queries, validations | Notifications, workflows      |

---

### Hybrid Approach (Common in Practice)

```
[API Gateway]
  |
  |-- sync --> [Order Service]  (create order)
  |               |
  |               |-- async --> [Event Bus]
  |                               |
  |                          [Shipping] (react)
  |                          [Analytics] (react)
  |                          [Email] (react)
  |
  |-- sync --> [Product Service] (get product)
```

Most real systems use both: sync for queries and commands requiring immediate feedback, async for notifications and reactions to state changes.

---

### Quick Recall

**If you remember only 3 things:**

1. Use request-response for queries and operations needing immediate results
2. Use events for notifications, multi-consumer reactions, and decoupling
3. Real systems are hybrid - sync for commands/queries, async for reactions

**Interview one-liner:**
"I use request-response for queries and immediate-feedback operations, and event-driven for multi-consumer notifications and decoupling - most production systems are hybrid, using both where each fits."

---

---

# Flow Control

**TL;DR** - Flow control manages the rate of data flow between producer and consumer to prevent overwhelming either party, using techniques like backpressure, rate limiting, buffering, and throttling.

---

### Techniques

```
RATE LIMITING:
  [Producer] --max 1000/sec--> [Consumer]
  Hard cap on production rate

THROTTLING:
  [Consumer] processes 100/batch, pauses 1s
  Self-imposed pace

BUFFERING:
  [Producer] --> [Buffer 10K] --> [Consumer]
  Absorbs bursts, defers processing

BACKPRESSURE:
  [Consumer] --> "slow down" --> [Producer]
  Consumer controls the pace

LOAD SHEDDING:
  [Consumer at capacity] --> DROP low-priority
  Graceful degradation
```

| Technique     | Where applied        | Trade-off                        |
| ------------- | -------------------- | -------------------------------- |
| Rate limiting | Producer side        | Caps throughput, predictable     |
| Throttling    | Consumer side        | Self-regulated, simple           |
| Buffering     | Between              | Absorbs spikes, memory cost      |
| Backpressure  | Consumer to producer | Optimal, complex to implement    |
| Load shedding | Consumer side        | Drops messages, preserves system |

---

### Quick Recall

**If you remember only 3 things:**

1. Backpressure is the most effective but hardest to implement
2. Buffering absorbs bursts but only delays the problem if consumers can't catch up
3. Load shedding is the last resort - drop low-priority work to protect the system

**Interview one-liner:**
"I implement flow control by combining rate limiting at producers, buffering for burst absorption, and backpressure for sustained overload - with load shedding as the last-resort safety valve."

---

---

# Async Architecture Selection

**TL;DR** - Choosing the right async architecture depends on message ordering needs, throughput requirements, consumer patterns, and operational complexity tolerance.

---

### Decision Framework

```
START
  |
  v
Need ordering guarantees?
  |-- Yes --> Need high throughput?
  |             |-- Yes --> KAFKA (partitioned log)
  |             |-- No --> RABBITMQ (single queue)
  |
  |-- No --> Need routing/filtering?
              |-- Yes --> RABBITMQ (exchanges)
              |-- No --> Need cloud-native simplicity?
                          |-- Yes --> SQS/SNS
                          |-- No --> RABBITMQ
```

### Architecture Patterns by Use Case

| Use case                | Pattern           | Tools                         |
| ----------------------- | ----------------- | ----------------------------- |
| Task queue              | Work queue        | RabbitMQ, Celery, SQS         |
| Event streaming         | Pub/sub log       | Kafka, Kinesis, Pulsar        |
| Microservice decoupling | Event-driven      | Kafka, RabbitMQ, SNS+SQS      |
| Long-running workflows  | Orchestration     | Temporal, Step Functions      |
| Periodic jobs           | Scheduling        | Quartz, ShedLock, k8s CronJob |
| Real-time analytics     | Stream processing | Kafka Streams, Flink          |
| Order processing        | Saga              | Temporal, Kafka + Outbox      |

---

### Interview Deep-Dive

**Q1: You're designing an async system for an e-commerce platform. Walk through your architecture decisions.**

_Why they ask:_ Tests ability to synthesize multiple async concepts into a coherent architecture.

**Answer:**

1. **Order creation:** Synchronous API returns order ID immediately. Outbox pattern writes event to outbox table atomically with order.

2. **Event backbone:** Kafka for event streaming - ordered by order ID (partition key), high throughput, replay capability for rebuilding read models.

3. **Downstream processing:** Shipping, inventory, notification services consume from Kafka with independent consumer groups. Each processes at its own pace.

4. **Saga for fulfillment:** Temporal orchestrates the multi-step fulfillment: reserve inventory -> charge payment -> schedule shipping. Compensating actions on failure.

5. **Error handling:** DLQ for each consumer group. Transient errors retry 3x with backoff. Permanent errors go to DLQ immediately. Alert on DLQ depth > 0.

6. **Observability:** Correlation ID propagated in Kafka headers. OpenTelemetry for distributed tracing. Consumer lag monitoring with Burrow. Dashboard with lag, DLQ depth, processing latency p99.

7. **Scheduling:** Quartz with ShedLock for daily reports and cleanup. Kubernetes CronJobs for infrastructure tasks.

---

### Quick Recall

**If you remember only 3 things:**

1. Kafka for high-throughput ordered event streaming; RabbitMQ for routing and task queues
2. Every async system needs: correlation IDs, DLQ, consumer lag monitoring, and retry strategy
3. Start simple (SQS/RabbitMQ) and evolve to Kafka only when you need ordering, replay, or high throughput

**Interview one-liner:**
"I select async architecture based on ordering needs (Kafka for ordered streams, RabbitMQ for flexible routing, SQS for simplicity), always ensuring DLQs, correlation IDs, and consumer lag monitoring are in place from day one."
