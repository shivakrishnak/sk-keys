---
id: ATZ-045
title: "Authorization in Event-Driven Systems"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-017, ATZ-030, ATZ-033, ATZ-040
used_by: ATZ-049, ATZ-050, ATZ-054
related: ATZ-033, ATZ-040, ATZ-049
tags:
  - security
  - authorization
  - event-driven
  - messaging
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/authorization/authorization-in-event-driven-systems/
---

⚡ **TL;DR** - In event-driven systems (Kafka, RabbitMQ, SQS),
the producer who emits an event and the consumer who acts on it
are decoupled in time and space. Authorization is harder: the
consumer must decide whether to act on an event without the
original user's context. Solutions: embed authorization context
in the event payload (user claims, scopes), enforce access
control at the event source (only authorized producers can emit
to a topic), and re-validate permissions at consumption time
for high-risk operations.

---

### 📊 Entry Metadata

| #045 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-017 OAuth Scopes, ATZ-030 Externalized Authz, ATZ-033 Cross-Service Authz, ATZ-040 Distributed Authz | |
| **Used by:** | ATZ-049, ATZ-050, ATZ-054 | |
| **Related:** | ATZ-033 Cross-Service, ATZ-040 Distributed Authz, ATZ-049 Microservices Fleet | |

---

### 📘 Textbook Definition

Event-driven architecture (EDA) introduces unique authorization
challenges because the request-response model (where the user's
token is present for authorization) does not apply. Instead,
an event carries instructions that may be executed much later
by a consumer service that has no connection to the original
request. Authorization must be preserved across this temporal
gap. Three approaches: context propagation (embed user JWT or
claims in event headers), producer-time authorization (only
allow authorized entities to produce to a topic or channel),
and consumer-time re-validation (consumer fetches current
permissions from a PDP before acting on the event).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│        Authorization in Event-Driven Systems           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  APPROACH 1: Context Propagation                       │
│  Producer embeds user JWT (or claims) in event headers │
│  Consumer validates JWT when consuming event           │
│  Problem: JWT may expire before event is consumed      │
│  Fix: use long-lived claims, not the raw access token  │
│                                                        │
│  APPROACH 2: Producer Authorization                    │
│  Kafka ACL: only order-service can write to            │
│             "payment.requested" topic                  │
│  Consumer trusts: anything on this topic = authorized  │
│  Shift authorization left to the producer layer        │
│  Problem: what if order-service is compromised?        │
│                                                        │
│  APPROACH 3: Consumer Re-Validation                    │
│  Consumer: before executing event, call PDP            │
│  PDP checks: "can this user do this action now?"       │
│  Problem: latency + PDP availability = critical path   │
│  Use for high-risk operations (money transfer, delete) │
│                                                        │
│  BEST PRACTICE: combine approaches                     │
│  - ACLs: only authorized producers per topic           │
│  - Propagate user claims (not token) in event headers  │
│  - For high-risk: re-validate at consumption time      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Propagating authorization context in Kafka events**

```java
// Producer: embed user claims in Kafka headers
public void publishOrderEvent(Order order,
                               Authentication auth) {
    ProducerRecord<String, OrderEvent> record =
        new ProducerRecord<>("order.created",
            order.getId().toString(),
            OrderEvent.from(order));

    // Embed user context - NOT the full JWT
    // JWT may expire before consumer processes event
    // Embed stable claims instead
    record.headers()
        .add("x-user-id",
            auth.getName().getBytes(UTF_8))
        .add("x-user-roles",
            String.join(",", getUserRoles(auth))
                .getBytes(UTF_8))
        .add("x-correlation-id",
            UUID.randomUUID().toString()
                .getBytes(UTF_8));

    kafkaTemplate.send(record);
}

// Consumer: read and validate user context from headers
@KafkaListener(topics = "order.created")
public void onOrderCreated(
        ConsumerRecord<String, OrderEvent> record) {
    String userId = new String(record.headers()
        .lastHeader("x-user-id").value(), UTF_8);
    String[] roles = new String(record.headers()
        .lastHeader("x-user-roles").value(), UTF_8)
        .split(",");

    OrderEvent event = record.value();

    // For high-risk: re-validate against current perms
    if (event.getAmount()
            .compareTo(HIGH_VALUE_THRESHOLD) > 0) {
        boolean allowed = authzClient.check(
            userId, "order:high-value", event.getId());
        if (!allowed) {
            // Log, dead-letter, alert security team
            deadLetterQueue.send(record);
            return;
        }
    }
    processOrder(event, userId);
}
```

---

*Authorization category: ATZ | Entry: ATZ-045 | v5.0*