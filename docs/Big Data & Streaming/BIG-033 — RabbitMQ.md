---
layout: default
title: "RabbitMQ"
parent: "Big Data & Streaming"
nav_order: 33
permalink: /big-data-streaming/rabbitmq/
number: "BIG-033"
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Message Broker vs Event Bus, Point-to-Point vs Pub-Sub
used_by: Task Queues, Event Routing, Microservices Messaging
related: Message Broker vs Event Bus, Apache Kafka, Dead Letter Queue
tags:
  - rabbitmq
  - amqp
  - exchange
  - queue
  - message-broker
---

# BIG-033 — RabbitMQ

⚡ TL;DR — **RabbitMQ** is a message broker based on the **AMQP protocol** (Advanced Message Queuing Protocol); messages flow: **Producer → Exchange → Queue → Consumer**; exchange types: **direct** (routing key exact match), **fanout** (broadcast to all bound queues), **topic** (pattern routing: `logs.*.error`, `events.#`), **headers** (attribute-based); Spring Boot integration: `@RabbitListener`, `RabbitTemplate`; key features: message TTL, dead letter exchange (DLX), durable queues, manual acknowledgements, prefetch count.

| #563            | Category: Big Data & Streaming                               | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Message Broker vs Event Bus, Point-to-Point vs Pub-Sub       |                 |
| **Used by:**    | Task Queues, Event Routing, Microservices Messaging          |                 |
| **Related:**    | Message Broker vs Event Bus, Apache Kafka, Dead Letter Queue |                 |

---

### 🔥 The Problem This Solves

**FLEXIBLE MESSAGE ROUTING BETWEEN SERVICES:**
Three services (email, SMS, push notifications) all need to receive the same "user registered" event. But orders need to go to ONE of five order processors (round-robin for load balancing), not all five. And error events need separate routing from info events. A simple point-to-point queue can't do flexible routing. RabbitMQ's exchange model: one message → exchange → routing logic → one or many queues, depending on exchange type and routing key. Different exchange types handle different routing patterns in the same broker.

---

### 📘 Textbook Definition

**RabbitMQ** is an open-source message broker that implements **AMQP 0-9-1** (Advanced Message Queuing Protocol). It provides reliable message delivery with flexible routing.

**Core Components:**

- **Producer**: sends messages to an exchange with a routing key.
- **Exchange**: receives messages from producers. Routes to zero or more queues based on exchange type and bindings.
- **Binding**: link between exchange and queue, with optional binding key.
- **Queue**: stores messages until consumed. Can be durable (survive broker restart), exclusive, auto-delete.
- **Consumer**: reads from a queue. Acknowledges or nacks messages.

**Exchange Types:**

- `direct`: route message to queues where binding key EXACTLY matches routing key. E.g., routing key `"order.created"` → only queues bound with key `"order.created"`.
- `fanout`: route to ALL queues bound to the exchange, regardless of routing key. Broadcast.
- `topic`: route by routing key pattern. `*` = one word, `#` = zero or more words. `"logs.*.error"` matches `"logs.app.error"`, `"logs.db.error"`. `"events.#"` matches `"events"`, `"events.a"`, `"events.a.b.c"`.
- `headers`: route based on message header attributes (rarely used; headers are expensive to match vs string keys).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
RabbitMQ = producer → exchange → routing logic → queues → consumers; exchange types control routing: direct (exact key), fanout (broadcast), topic (pattern).

**One analogy:**

> Exchange = a post office sorting system. **Direct exchange**: letter with address "123 Main St" → only goes to mailbox "123 Main St." **Fanout exchange**: newspaper delivery → ALL subscribers get a copy. **Topic exchange**: subscription by topic (`*.sports.*` → anyone subscribed to sports section). Same letter, different routing depending on exchange type.

**One insight:**
RabbitMQ excels at **task/work queues** and **flexible routing** — patterns Kafka handles less naturally. Kafka is append-log (replay), RabbitMQ is work queue (consume and delete). If you need: "one of N workers picks up this task" → RabbitMQ. "All N consumers see every event" → Kafka (or RabbitMQ fanout). "Replay past events" → Kafka only. RabbitMQ does NOT retain messages after acknowledgement by default.

---

### 🔩 First Principles Explanation

**SPRING BOOT + RABBITMQ SETUP:**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  rabbitmq:
    host: rabbitmq
    port: 5672
    username: admin
    password: secret
    virtual-host: /
```

**EXCHANGE + QUEUE CONFIGURATION:**

```java
@Configuration
public class RabbitMQConfig {

    // DIRECT EXCHANGE: exact routing key matching
    public static final String DIRECT_EXCHANGE = "orders.direct";
    public static final String ORDER_QUEUE = "orders.processing";
    public static final String ORDER_ROUTING_KEY = "order.created";

    // TOPIC EXCHANGE: pattern routing
    public static final String TOPIC_EXCHANGE = "logs.topic";
    public static final String ERROR_QUEUE = "logs.errors";
    public static final String ALL_LOGS_QUEUE = "logs.all";

    // FANOUT EXCHANGE: broadcast to all
    public static final String FANOUT_EXCHANGE = "notifications.fanout";
    public static final String EMAIL_QUEUE = "notifications.email";
    public static final String SMS_QUEUE = "notifications.sms";

    // Dead Letter Exchange (DLX) for failed messages
    public static final String DLX_EXCHANGE = "orders.dlx";
    public static final String DLQ = "orders.dead-letter";

    @Bean
    public DirectExchange ordersDirectExchange() {
        return new DirectExchange(DIRECT_EXCHANGE, true, false);
        // durable=true: survives broker restart
        // autoDelete=false: don't delete when no bindings
    }

    @Bean
    public TopicExchange logsTopicExchange() {
        return new TopicExchange(TOPIC_EXCHANGE);
    }

    @Bean
    public FanoutExchange notificationsFanoutExchange() {
        return new FanoutExchange(FANOUT_EXCHANGE);
    }

    // Dead Letter Exchange:
    @Bean
    public DirectExchange dlxExchange() {
        return new DirectExchange(DLX_EXCHANGE);
    }

    // Order processing queue with DLX routing:
    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable(ORDER_QUEUE)
            .withArgument("x-dead-letter-exchange", DLX_EXCHANGE)
            .withArgument("x-dead-letter-routing-key", "dead.order")
            .withArgument("x-message-ttl", 300_000)  // 5 min TTL
            // Message not consumed in 5 min → expires → sent to DLX
            .build();
    }

    @Bean
    public Queue deadLetterQueue() {
        return QueueBuilder.durable(DLQ).build();
    }

    @Bean
    public Queue errorLogsQueue() {
        return QueueBuilder.durable(ERROR_QUEUE).build();
    }

    @Bean
    public Queue allLogsQueue() {
        return QueueBuilder.durable(ALL_LOGS_QUEUE).build();
    }

    @Bean
    public Queue emailQueue() {
        return QueueBuilder.durable(EMAIL_QUEUE).build();
    }

    @Bean
    public Queue smsQueue() {
        return QueueBuilder.durable(SMS_QUEUE).build();
    }

    // BINDINGS:

    // Direct: order.created routing key → orderQueue
    @Bean
    public Binding orderBinding() {
        return BindingBuilder.bind(orderQueue())
            .to(ordersDirectExchange())
            .with(ORDER_ROUTING_KEY);
    }

    // Topic: "logs.*.error" → errorLogsQueue
    @Bean
    public Binding errorLogBinding() {
        return BindingBuilder.bind(errorLogsQueue())
            .to(logsTopicExchange())
            .with("logs.*.error");  // matches: logs.app.error, logs.db.error
    }

    // Topic: "logs.#" → allLogsQueue (everything)
    @Bean
    public Binding allLogBinding() {
        return BindingBuilder.bind(allLogsQueue())
            .to(logsTopicExchange())
            .with("logs.#");  // matches: logs, logs.info, logs.app.info, logs.a.b.c
    }

    // Fanout: no routing key (fanout ignores routing keys)
    @Bean
    public Binding emailNotificationBinding() {
        return BindingBuilder.bind(emailQueue()).to(notificationsFanoutExchange());
    }

    @Bean
    public Binding smsNotificationBinding() {
        return BindingBuilder.bind(smsQueue()).to(notificationsFanoutExchange());
    }

    @Bean
    public Binding dlqBinding() {
        return BindingBuilder.bind(deadLetterQueue())
            .to(dlxExchange())
            .with("dead.order");
    }

    // Jackson message converter (JSON):
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    // RabbitTemplate with JSON converter:
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory factory) {
        RabbitTemplate template = new RabbitTemplate(factory);
        template.setMessageConverter(jsonMessageConverter());
        return template;
    }

    // SimpleRabbitListenerContainerFactory with manual ack + prefetch:
    @Bean
    public SimpleRabbitListenerContainerFactory rabbitListenerContainerFactory(
            ConnectionFactory factory) {
        SimpleRabbitListenerContainerFactory containerFactory =
            new SimpleRabbitListenerContainerFactory();
        containerFactory.setConnectionFactory(factory);
        containerFactory.setMessageConverter(jsonMessageConverter());
        containerFactory.setAcknowledgeMode(AcknowledgeMode.MANUAL);
        containerFactory.setPrefetchCount(10);
        // prefetchCount=10: consumer fetches 10 unacked messages at a time
        // Fair dispatch: don't send more until previous 10 are acked
        // prefetchCount=1: strictest fairness (send 1, wait for ack, send next)
        return containerFactory;
    }
}
```

**PRODUCER:**

```java
@Service
public class OrderProducer {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    public void publishOrderCreated(Order order) {
        // Direct exchange: routing key "order.created"
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.DIRECT_EXCHANGE,
            RabbitMQConfig.ORDER_ROUTING_KEY,
            order
        );
    }

    public void publishLogEvent(String service, String level, String message) {
        // Topic exchange: routing key "logs.{service}.{level}"
        // e.g., "logs.payment-service.error"
        String routingKey = "logs." + service + "." + level;
        Map<String, Object> logEvent = Map.of(
            "service", service,
            "level", level,
            "message", message,
            "timestamp", System.currentTimeMillis()
        );
        rabbitTemplate.convertAndSend(RabbitMQConfig.TOPIC_EXCHANGE, routingKey, logEvent);
        // "logs.payment-service.error" → matches both:
        //   "logs.*.error" → errorLogsQueue
        //   "logs.#" → allLogsQueue
        // Message COPIES sent to both queues
    }

    public void publishNotification(String userId, String message) {
        // Fanout exchange: routing key ignored (broadcast to all queues)
        Map<String, Object> notification = Map.of("userId", userId, "message", message);
        rabbitTemplate.convertAndSend(RabbitMQConfig.FANOUT_EXCHANGE, "", notification);
        // Goes to: emailQueue AND smsQueue
    }
}
```

**CONSUMER (MANUAL ACK):**

```java
@Service
public class OrderConsumer {

    @RabbitListener(
        queues = RabbitMQConfig.ORDER_QUEUE,
        containerFactory = "rabbitListenerContainerFactory"  // manual ack
    )
    public void processOrder(Order order, Channel channel,
                              @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag) {
        try {
            orderService.process(order);

            // Manual acknowledgement: remove from queue
            channel.basicAck(deliveryTag, false);
            // false = ack only this message (not all unacked up to this tag)

        } catch (RetryableException e) {
            // Requeue: message goes back to queue for retry
            channel.basicNack(deliveryTag, false, true);  // true = requeue
            // WARNING: if exception is permanent → infinite requeue loop
            // Use DLX + retry count (x-death header) to limit retries

        } catch (PermanentException e) {
            // Don't requeue: message goes to DLX (dead letter exchange)
            channel.basicNack(deliveryTag, false, false);  // false = don't requeue
        }
    }

    @RabbitListener(queues = RabbitMQConfig.DLQ)
    public void processDeadLetter(Order order) {
        // Handle failed orders: alert, store in DB, manual review
        log.error("Dead letter order: {}", order.getOrderId());
        deadLetterService.record(order);
    }
}
```

**PREFETCH COUNT (FAIR DISPATCH):**

```
Prefetch count controls message distribution to consumers:

prefetchCount=0 (unlimited):
  Consumer 1: gets ALL 1000 queued messages immediately
  Consumer 2: waits idle
  Problem: uneven distribution

prefetchCount=1:
  Consumer 1: gets msg1 → processes (slow, 5s)
  Consumer 2: gets msg2 → processes (fast, 0.1s) → gets msg3, msg4, msg5...
  Fast consumer gets more work: fair dispatch based on processing speed
  Maximum fairness, lowest throughput (ack before next)

prefetchCount=10:
  Compromise: batch of 10 in flight per consumer
  Consumer fetches 10, processes, acks, fetches next 10
  Good for high-throughput with reasonable fairness
```

---

### 🧪 Thought Experiment

**RABBITMQ vs KAFKA: TASK QUEUE SCENARIO:**

100 orders in queue. 5 order processors. Each order takes 1 second.

- RabbitMQ: queue → 5 consumers → each gets ~20 orders → done in ~20 seconds. Messages deleted after ack. No retention needed.
- Kafka: topic with 5 partitions → 5 consumers → each partition gets ~20 messages → done in ~20 seconds. BUT: messages retained for 7 days. On crash: re-reads from committed offset. Replay possible.

For pure task processing (no replay needed): RabbitMQ is simpler and more memory-efficient. For event streaming (replay required): Kafka.

---

### 🧠 Mental Model / Analogy

> RabbitMQ exchange types are like **mail routing rules**:
>
> - **Direct**: package with address "Bob Smith" → only Bob's mailbox.
> - **Fanout**: broadcast email → ALL employees get it.
> - **Topic**: subscribe to "_.technology._" → all technology-related emails.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** RabbitMQ = producer → exchange → queue → consumer. Exchange types: direct (exact key), fanout (all), topic (pattern). Spring: `@RabbitListener`, `RabbitTemplate`.

**Level 2:** DLX for failed messages: queue configured with `x-dead-letter-exchange` → nacked/expired messages → DLX → DLQ. Message TTL (`x-message-ttl`): expire if not consumed. Prefetch count: fair dispatch. Manual ack: prevents message loss.

**Level 3:** Virtual hosts: logical isolation within one RabbitMQ broker (separate exchanges, queues, users). Publisher confirms: async ack from broker when message is safely persisted (like Kafka acks). Quorum queues (RabbitMQ 3.8+): Raft-based replicated queues for HA (replaces classic mirrored queues). Lazy queues: store messages to disk instead of memory (handles large queue backlogs without OOM).

**Level 4:** AMQP 0-9-1 protocol details: `basic.publish`, `basic.deliver`, `basic.ack`, `basic.nack`, channel multiplexing (one TCP connection, multiple channels). Federation and Shovel: cross-broker message forwarding (RabbitMQ's answer to Kafka MirrorMaker). RabbitMQ Streams (3.9+): append-only log semantics (like Kafka), with replay support — bridging the gap with Kafka for event streaming use cases. For new projects deciding between Kafka and RabbitMQ: if replay/event sourcing needed → Kafka; if complex routing/task queues → RabbitMQ; if both → evaluate Pulsar or dual-broker architecture.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ RABBITMQ MESSAGE ROUTING                             │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Producer: publish("order.created", {order})         │
│    ↓ to DIRECT EXCHANGE                              │
│ Exchange: routing key = "order.created"             │
│    ↓ binding: "order.created" → ORDER_QUEUE         │
│ Queue: ORDER_QUEUE (durable, DLX configured)        │
│    ↓ consumer fetch (prefetch=10)                   │
│ Consumer: orderService.process(order)               │
│    ↓ success → channel.basicAck(tag, false)         │
│ Queue: message removed                              │
│    ↓ failure → channel.basicNack(tag, false, false) │
│ DLX: message routed to DEAD_LETTER_QUEUE            │
│                                                      │
│ FANOUT EXCHANGE:                                     │
│ publish("", {notification}) → ALL bound queues     │
│   → emailQueue AND smsQueue (both get copies)       │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
E-commerce order placed:

1. Order service → OrderProducer.publishOrderCreated(order)
   RabbitTemplate.convertAndSend(DIRECT_EXCHANGE, "order.created", order)

2. Direct exchange routes "order.created" → ORDER_QUEUE

3. OrderConsumer @RabbitListener (5 instances, prefetch=10):
   Instance 1: picks up order1, order6, order11... (round-robin)
   Instance 2: picks up order2, order7, order12...
   Processing: all 5 processors in parallel

4. Order3 fails (payment timeout):
   basicNack(tag, false, true) → requeue → retried 3 times
   Still fails → basicNack(tag, false, false) → DLX → DLQ
   Dead letter handler: alert ops team, store in manual_review DB

5. Notification fanout:
   publishNotification(userId, "Order confirmed!")
   → emailQueue: EmailService sends email
   → smsQueue: SMSService sends SMS
   Both run independently, in parallel

Retention: none. Messages consumed = gone. No replay.
For audit trail: save orders to DB in @RabbitListener before basicAck.
```

---

### ⚖️ Comparison Table

| Feature           | RabbitMQ                     | Apache Kafka                          |
| ----------------- | ---------------------------- | ------------------------------------- |
| Message retention | Deleted after ack (default)  | Retained (configurable, days-forever) |
| Routing           | Flexible (4 exchange types)  | Consumer group (limited routing)      |
| Replay            | NO (no log retention)        | YES (seek to offset)                  |
| Order guarantee   | Per-queue, single consumer   | Per-partition                         |
| Throughput        | High (100K+ msg/s)           | Very high (millions/s)                |
| Consumer push     | Yes (AMQP push)              | Consumer pull                         |
| Best for          | Task queues, complex routing | Event streaming, replay, high volume  |

---

### ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                                                                                                                                                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "RabbitMQ is just a simpler Kafka" | Different tools for different patterns. RabbitMQ: flexible routing, work queues, message lifecycle (TTL, DLX). Kafka: event log, replay, high throughput. Using Kafka as a task queue is awkward; using RabbitMQ for event sourcing is impossible |
| "Prefetch=1 is always safest"      | prefetch=1 maximizes fairness but destroys throughput for fast consumers. For most use cases: prefetch=10-50 is the right balance. Use prefetch=1 only when processing time varies wildly and you need strict fair dispatch                       |
| "Auto-ack is fine for most cases"  | Auto-ack acknowledges before processing. If consumer crashes during processing, message is lost. Always use manual ack for business-critical messages. Auto-ack only for idempotent, loss-tolerant workloads                                      |

---

### 🚨 Failure Modes & Diagnosis

**1. Infinite Requeue Loop (Poison Message)**

**Symptom:** Consumer repeatedly processes same message, CPU spikes, queue never drains.

**Root Cause:** Exception handler does `basicNack(..., requeue=true)` on non-retryable error. Message never removed from queue.

**Fix:**

```java
// Check x-death header to count retry attempts:
@RabbitListener(queues = "order-queue")
public void process(Order order, Channel channel,
                    @Header(AmqpHeaders.DELIVERY_TAG) long tag,
                    @Headers Map<String, Object> headers) throws IOException {
    try {
        orderService.process(order);
        channel.basicAck(tag, false);

    } catch (Exception e) {
        // Check retry count via x-death header
        List<Map<String, Object>> xDeath = (List<Map<String, Object>>) headers.get("x-death");
        long retryCount = xDeath == null ? 0 :
            xDeath.stream().mapToLong(d -> (Long) d.get("count")).sum();

        if (retryCount >= 3) {
            log.error("Max retries exceeded, sending to DLQ: {}", order.getOrderId());
            channel.basicNack(tag, false, false);  // dead-letter
        } else {
            channel.basicNack(tag, false, true);  // requeue for retry
        }
    }
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Message Broker vs Event Bus, Point-to-Point vs Pub-Sub
**Builds On This:** Dead Letter Queue, Task Queues
**Related:** Message Broker vs Event Bus, Apache Kafka, Dead Letter Queue

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PROTOCOL    │ AMQP 0-9-1                                │
│ DIRECT      │ Exact routing key match                   │
│ FANOUT      │ Broadcast to all bound queues             │
│ TOPIC       │ Pattern matching (* = 1 word, # = many)   │
│ DLX         │ Dead Letter Exchange for failed messages  │
│ TTL         │ Message/queue expiry (x-message-ttl)      │
│ PREFETCH    │ Fair dispatch (10 = good default)         │
│ ACK         │ Manual: ack/nack; Auto: before processing │
│ vs KAFKA    │ RabbitMQ: routing+tasks; Kafka: streaming │
│ POISON MSG  │ Check x-death header → max retry → DLQ   │
│ ONE-LINER   │ "Exchange routes to queues: direct=exact, │
│             │  fanout=all, topic=pattern; manual ack"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What are the four exchange types in RabbitMQ? For each, describe the routing logic and give a concrete use case where you would choose that exchange type over the others.

**Q2.** (TYPE B — Bug Hunt) Your RabbitMQ queue has 10,000 messages and is not draining. Consumer CPU is at 100%. After investigation, you notice the same 50 message IDs appearing repeatedly in logs. What is the root cause and how do you fix it?
