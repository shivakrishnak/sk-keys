---
layout: default
title: "GraphQL Subscriptions"
parent: "HTTP & APIs"
nav_order: 221
permalink: /http-apis/graphql-subscriptions/
number: "0221"
category: HTTP & APIs
difficulty: ★★★
depends_on: GraphQL, GraphQL Resolvers, WebSocket, Pub/Sub Pattern
used_by: Real-time APIs, Event-Driven Architecture, GraphQL Federation
related: WebSocket, Server-Sent Events, Long Polling
tags:
  - api
  - graphql
  - realtime
  - subscriptions
  - websocket
  - advanced
---

# 221 — GraphQL Subscriptions

⚡ TL;DR — GraphQL Subscriptions allow clients to receive real-time data updates by maintaining a persistent connection to the server; the client declares what events it wants using the same query syntax, and the server pushes matching data whenever those events occur.

| #221 | Category: HTTP & APIs | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | GraphQL, GraphQL Resolvers, WebSocket, Pub/Sub Pattern | |
| **Used by:** | Real-time APIs, Event-Driven Architecture, GraphQL Federation | |
| **Related:** | WebSocket, Server-Sent Events, Long Polling | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A dashboard shows live order status updates. Without subscriptions, the client
polls `GET /orders/{id}` every 2 seconds hoping for a status change.
At 10,000 concurrent users, that's 5,000 requests/second for data that changes
maybe once per minute. 99% of these requests return unchanged data.
The server is hammered; the client wastes bandwidth; status changes still
have up to 2-second latency.

**THE BREAKING POINT:**
A trading platform needs sub-100ms latency for price updates. Polling every
100ms at scale melts the server. A chat app needs messages delivered instantly
to N recipients — polling each recipient independently is O(N × interval) load.
Neither polling nor REST can deliver real-time push semantics efficiently.

**THE INVENTION MOMENT:**
GraphQL Subscriptions bring GraphQL's query model to real-time events.
Instead of polling, the client declares: "I want to receive a notification every
time [this event occurs], and when it does, give me [these specific fields]."
The server pushes matching events over a persistent connection. The same
schema that describes queries describes subscriptions — no new language needed.

---

### 📘 Textbook Definition

**GraphQL Subscriptions** are a GraphQL operation type that establishes a
long-lived connection between client and server, over which the server
pushes data events to the client in real-time. Defined in the GraphQL
specification, subscriptions use the `subscription` keyword in SDL and
queries. The transport layer is typically WebSocket (graphql-ws or
subscriptions-transport-ws protocol), though SSE (Server-Sent Events) is
also used. Subscription resolvers return an `AsyncIterable` (Java: `Flux`
or `Publisher`) rather than a single value. The GraphQL engine subscribes
to the stream, executes the field selection set against each emitted event,
and pushes the result to the client.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of the client asking "what's the latest?" repeatedly, the server says "I'll tell you as soon as something changes" — pushed over a persistent connection.

**One analogy:**

> Without subscriptions, checking for news is like refreshing a newspaper website
> every minute. With subscriptions, it's like having a news alert set up on your
> phone — the publisher notifies you the moment something happens. You set up the
> alert once (subscribe), and news arrives the moment it's published, not when
> you next think to check.

**One insight:**
Subscriptions reuse GraphQL's schema and query language for real-time events.
The same type system, field selection, and argument filtering that work for
queries work for subscriptions — there's no new language to learn. The power:
a client subscribing to `orderUpdated(orderId: "42") { status, estimatedDelivery }`
gets exactly those two fields pushed whenever order #42 changes, nothing more.

---

### 🔩 First Principles Explanation

**COMPONENTS:**

1. **Schema subscription type:**

   ```graphql
   type Subscription {
     orderUpdated(orderId: ID!): Order!
     newMessage(channelId: ID!): Message!
     priceChanged(symbol: String!): StockPrice!
   }
   ```

2. **Subscription resolver returns a Publisher/stream:**
   Unlike query/mutation resolvers that return a single value,
   subscription resolvers return a reactive stream (`Flux<T>` in Java,
   `AsyncIterable<T>` in JS).

3. **Execution:** For each event emitted by the stream, GraphQL executes
   the field selection set against the event object (same as a query),
   producing a shaped result that is pushed to the client.

4. **Transport:** Persistent connection over WebSocket or SSE carries
   the pushed results.

**LIFECYCLE:**

```
1. Client opens WebSocket connection
2. Client sends subscription query
3. Server: resolver creates event stream (subscribes to message broker)
4. Server streams GraphQL-shaped results to client for each event
5. Client receives real-time updates
6. Client or server closes connection → stream disposed
```

**THE TRADE-OFFS:**

- Gain: push model → zero polling overhead, instant delivery.
- Cost: stateful connections → horizontal scaling requires shared pub/sub (Redis, Kafka).
- Gain: field selection → client gets exactly what it needs from each event.
- Cost: WebSocket connection count = concurrent subscribed users → memory + connection limits.
- Gain: GraphQL schema validation applies to subscription queries.
- Cost: error handling is more complex — errors mid-stream don't have HTTP status codes.

---

### 🧪 Thought Experiment

**SETUP:**
10,000 concurrent users each watching a different order's status on a
live tracking page. Each order updates ~5 times total over 30 minutes.

**POLLING APPROACH (2-second intervals):**

```
Requests/second = 10,000 users × (1 request / 2 seconds) = 5,000 req/s
Useful responses = ~10,000 orders × 5 updates / 1800 seconds ≈ 28 useful/s
Wasted requests = 5,000 - 28 = 4,972 req/s (99.4% wasted)
DB reads = 5,000/s (many redundant reads for unchanged orders)
```

**SUBSCRIPTION APPROACH:**

```
Connections = 10,000 (one per user, persistent WebSocket)
Events pushed = ~28/s (only actual status changes)
Server-to-client messages = 28/s (only to relevant subscribers)
DB reads = only on actual order state change (near zero vs polling)
Memory cost = 10,000 WebSocket connection objects
```

**THE INSIGHT:**
Subscriptions replace a polling load of 5,000 req/s with 10,000 persistent
connections and ~28 push events per second. The connection overhead is a
one-time cost; polling overhead compounds with scale. At 10,000 users,
subscriptions are orders of magnitude more efficient — but they require
connection management infrastructure that pooled HTTP does not.

---

### 🧠 Mental Model / Analogy

> Think of GraphQL Subscriptions as a publish-subscribe newspaper delivery
> service operated at the field-selection level. You (client) subscribe with a
> specific form: "Deliver me the morning edition, but only the Sports section,
> and only when Liverpool scores." The city desk (subscription resolver) watches
> the newswire. When Liverpool scores, it publishes an event. The delivery
> system (GraphQL engine) takes that event, extracts the fields you specified
> in your subscription query, and delivers just those fields to your door over
> your standing open connection (WebSocket). Cancel at any time.

- "Subscription form" → subscription operation with field selection
- "City desk watching the newswire" → subscription resolver returning a Publisher/stream
- "Liverpool scores" → event emitted on the stream
- "Extracting only the Sports section" → GraphQL executing field selection on event
- "Your open connection" → WebSocket connection

**Where this breaks down:** Real-time systems push events to subscribers at
the server's pace. If the client can't process events fast enough (slow processing,
unreliable mobile network), backpressure management becomes critical. WebSocket
doesn't have built-in backpressure — you need application-level flow control.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
With subscriptions, instead of constantly asking "is there anything new?", you
tell the server "notify me when something happens." The server then sends you
updates automatically. Like push notifications for your API — delivered the instant
the event occurs.

**Level 2 — How to use it (junior developer):**
In the GraphQL schema, add a `Subscription` type with event fields. On the client,
open a WebSocket connection and send a subscription operation using the `subscription`
keyword. The server sends back GraphQL-shaped data for each event. On the server
(Spring for GraphQL): annotate a method with `@SubscriptionMapping`, return
a `Flux<T>` that emits events. The engine handles the rest.

**Level 3 — How it works (mid-level engineer):**
When a client subscribes, the resolver is called once, returning a `Publisher<T>`
(Java) or `AsyncIterable<T>` (JS). The GraphQL engine subscribes to this stream.
For each item emitted, the engine executes the subscription's selection set against
it — exactly like a query resolver, but using the emitted item as the root value.
The resulting shaped object is serialized and sent to the client over the WebSocket.
At scale: multiple server instances can't share in-memory streams — each server
only knows about connections established with it. Solution: use a shared pub/sub
broker (Redis Pub/Sub, Kafka) as the event source. Each server subscribes to the
broker and delivers events to locally connected clients. This converts stateful
per-server streams into stateless per-event delivery.

**Level 4 — Why it was designed this way (senior/staff):**
GraphQL Subscriptions were added late (2017, after queries and mutations) and
show the seams. The spec says subscriptions run over WebSocket but doesn't
mandate a specific protocol — this led to fragmentation: `subscriptions-transport-ws`
(legacy, deprecated) and `graphql-ws` (modern) are incompatible wire protocols.
The decision to execute field selection on each event (rather than pushing raw events)
was deliberate: it keeps subscriptions type-safe and compatible with the schema,
allowing clients to select fields just like queries. The cost: every event triggers
resolver execution, which includes field selection evaluation overhead. At very high
event rates, this creates CPU pressure. Alternative pattern: "thin subscriptions"
(just push an ID) + client re-queries for full data; avoids resolver overhead at
the cost of an extra query per update. The fundamental tension in subscriptions
is the mismatch between GraphQL's request/response model and reactive stream
semantics — the spec requires subscription resolvers to be called once to get
the stream, not once per event. This distinction is frequently misunderstood.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────────────┐
│           GRAPHQL SUBSCRIPTION LIFECYCLE                       │
├────────────────────────────────────────────────────────────────┤
│  Client opens WebSocket                                        │
│  Client sends: {type:"subscribe", payload:{query:"..."}}       │
│                    ↓                                           │
│  Server validates subscription query against schema            │
│                    ↓                                           │
│  Subscription resolver called ONCE:                           │
│    orderUpdated(null, {orderId: "42"}, ctx, info)              │
│    → returns Flux<Order> (event stream)                        │
│                    ↓                                           │
│  GraphQL engine subscribes to Flux                            │
│                    ↓ (on each Order event emitted)            │
│  Field selection execution:                                    │
│    run query selection set against emitted Order object       │
│    → {status: "SHIPPED", estimatedDelivery: "2024-01-15"}     │
│                    ↓                                           │
│  Push result to client over WebSocket:                        │
│  {type:"next", payload:{data:{orderUpdated:{status:"SHIPPED"}}}}
│                    ↓                                           │
│  Repeat for each event — until client unsubscribes or         │
│  connection closes                                             │
└────────────────────────────────────────────────────────────────┘
```

**Scaling with Redis Pub/Sub:**

```
Client 1 (server A) subscribes to orderUpdated(orderId: "42")
  → Server A's resolver subscribes to Redis channel "order:42"

Order 42 status changes → app publishes to Redis "order:42"
  → Server A receives message → executes selection → pushes to Client 1
  → Server B (no relevant connections) receives+ignores message
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT                    SERVER A             REDIS/KAFKA     │
├─────────────────────────────────────────────────────────────────┤
│  Open WebSocket ────────→  Accept connection                   │
│  Send subscription ─────→  Validate + call resolver            │
│                             resolver returns Flux               │
│                             subscribes to Redis channel         │
│                                               ←── order event   │
│                             execute selection set               │
│  ←── receive event ─────   push via WebSocket                  │
│  Receives: {status:...}                                         │
│                                               ←── another event │
│  ←── receive event ─────   push via WebSocket                  │
│  Close WebSocket ───────→  Unsubscribe from Redis channel      │
│                             dispose Flux                        │
└─────────────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

```graphql
# Schema subscription definition
type Subscription {
  orderUpdated(orderId: ID!): Order!
  newComment(postId: ID!): Comment!
}

# Client subscription query
subscription TrackOrder($orderId: ID!) {
  orderUpdated(orderId: $orderId) {
    status
    estimatedDelivery
    lastUpdateAt
  }
}
```

```java
// Spring for GraphQL — subscription resolver
@Controller
public class OrderSubscriptionController {

    @Autowired private OrderEventPublisher eventPublisher;

    // Called ONCE per subscription setup — returns a stream
    @SubscriptionMapping
    public Flux<Order> orderUpdated(@Argument String orderId) {
        // Validate access before subscribing
        // Return a Flux that emits Order objects when they change
        return eventPublisher
            .getOrderEvents()                           // all order events
            .filter(event -> event.getOrderId()
                .equals(orderId))                       // filter to this order
            .map(OrderEvent::getOrder)                  // extract Order
            .timeout(Duration.ofMinutes(30))            // auto-close stale subs
            .doOnSubscribe(s -> log.info(
                "Client subscribed to order {}", orderId))
            .doOnCancel(() -> log.info(
                "Client unsubscribed from order {}", orderId));
    }
}
```

```java
// Event publisher — bridges domain events to subscription stream
@Component
public class OrderEventPublisher {

    private final Sinks.Many<OrderEvent> sink =
        Sinks.many().multicast().onBackpressureBuffer();

    // Called by order service when an order changes
    public void publishOrderUpdate(Order order) {
        sink.tryEmitNext(new OrderEvent(order.getId(), order));
    }

    public Flux<OrderEvent> getOrderEvents() {
        return sink.asFlux();
    }
}
```

```java
// With Redis Pub/Sub for multi-instance scaling
@Component
public class RedisOrderSubscriptionSource {

    @Autowired private ReactiveRedisMessageListenerContainer container;

    public Flux<Order> subscribeToOrder(String orderId) {
        return container
            .receive(ChannelTopic.of("order:" + orderId))
            .map(message -> deserialize(message.getMessage(), Order.class));
    }
}

// Publisher (in OrderService):
@Autowired private ReactiveRedisTemplate<String, Order> redisTemplate;

public Mono<Void> updateOrder(Order order) {
    return orderRepository.save(order)
        .then(redisTemplate.convertAndSend("order:" + order.getId(), order))
        .then();
}
```

---

### ⚖️ Comparison Table

| Transport                  | Bidirectional | Reconnect | Server → Client | Use Case                 |
| -------------------------- | ------------- | --------- | --------------- | ------------------------ |
| **WebSocket (graphql-ws)** | ✓             | Manual    | Push            | Chat, live dashboards    |
| **SSE (HTTP/2)**           | ✗ (read-only) | Auto      | Push            | Notifications, feeds     |
| **Long Polling**           | ✗             | Built-in  | Simulated push  | Fallback, simple updates |
| **gRPC Streaming**         | Bidirectional | Manual    | Push            | Service-to-service       |
| **Regular Polling**        | ✗             | N/A       | Client pull     | Simple, low-frequency    |

**When to use GraphQL Subscriptions:** When clients need real-time updates on
specific entities, when the data shape varies per client (use field selection),
and when you're already using GraphQL queries/mutations. Avoid if the event
rate is very high (use SSE or raw WebSocket for firehoses).

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Subscription resolver is called on every event        | The resolver is called ONCE to get the stream; GraphQL executes the selection set on each emitted event                                                       |
| Subscriptions work on a single server out of the box  | Single server works; multiple servers require shared pub/sub (Redis, Kafka) — otherwise clients on different servers miss events                              |
| HTTP status codes work for subscription errors        | Subscriptions run over WebSocket; errors come as `{type:"error"}` messages in the graphql-ws protocol, not HTTP status codes                                  |
| The old `subscriptions-transport-ws` protocol is fine | Deprecated and has known bugs; migrate to `graphql-ws` protocol wherever possible                                                                             |
| Subscriptions replace polling for all use cases       | Subscriptions are for user-facing real-time; service-to-service real-time often uses Kafka/RabbitMQ; polling is still valid for low-frequency background jobs |

---

### 🚨 Failure Modes & Diagnosis

**Subscriptions Not Scaling Across Multiple Server Instances**

**Symptom:**
After deploying 3 server instances behind a load balancer, only ~33% of
subscription clients receive events. Some clients receive all events,
most receive none.

**Root Cause:**
Event publishing and subscription resolvers are in-memory (using local
`Sinks.Many` / `ApplicationEventPublisher`). Events published on instance A
don't reach clients connected to instance B or C.

**Diagnostic Command / Tool:**

```bash
# Check if clients are consistently routed to one server:
# If using AWS ALB with sticky sessions — some clients see all events (lucky)
# Without sticky sessions — random distribution → missed events

# Verify by publishing an event and checking which server receives the WebSocket message:
# Enable subscription connection logging:
logging.level.org.springframework.web.socket=DEBUG
```

**Fix:**
Replace in-memory `Sinks.Many` with Redis Pub/Sub or Kafka as the event bus.
All server instances subscribe to the same Redis channel and deliver events
to locally connected clients.

**Prevention:**
Always test subscription delivery with multiple server instances in staging.
Never use in-memory event buses for subscriptions in horizontally-scaled services.

---

**Memory Leak from Abandoned Subscriptions**

**Symptom:**
Server memory grows steadily over hours. Heap dumps show thousands of Flux
objects and associated state that never get garbage collected.

**Root Cause:**
Clients disconnect without sending a proper unsubscribe message (e.g., mobile
app backgrounded, browser tab closed abruptly). The server-side Flux is never
disposed — it holds onto resources (DB connections, Redis subscriptions) forever.

**Diagnostic Command / Tool:**

```java
// Log subscription disposals to check if cancel is being called:
return eventFlux
    .doOnSubscribe(s -> log.info("Sub started: {}", subscriptionId))
    .doOnCancel(() -> log.info("Sub cancelled: {}", subscriptionId))
    .doOnTerminate(() -> log.info("Sub terminated: {}", subscriptionId));
// If "Sub started" appears without corresponding cancel/terminate → leak
```

**Fix:**
Add `.timeout(Duration.ofMinutes(30))` to all subscription streams.
Use `graphql-ws` protocol which has proper connection management.
Ensure WebSocket close events trigger Flux disposal.

**Prevention:**
Always set a maximum subscription duration. Monitor active subscription count
as a Prometheus gauge — spikes indicate abandoned subscriptions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `GraphQL` — must understand GraphQL fundamentals; subscriptions are the third operation type
- `GraphQL Resolvers` — subscription resolver returns a stream, not a single value; must understand how resolvers work
- `WebSocket` — the primary transport for subscriptions; must understand full-duplex persistent connections
- `Pub/Sub Pattern` — subscriptions are a client-server pub/sub; must understand the pattern

**Builds On This (learn these next):**

- `Real-time APIs` — GraphQL Subscriptions are one implementation; compare with SSE and WebSocket
- `Event-Driven Architecture` — the server-side event model that powers subscriptions
- `GraphQL Federation` — how subscriptions work across a federated GraphQL schema

**Alternatives / Comparisons:**

- `WebSocket` — raw WebSocket without GraphQL for firehose or binary streams
- `Server-Sent Events` — simpler unidirectional push; auto-reconnects, no WebSocket overhead
- `Long Polling` — fallback technique; simulates push via repeated polling with long timeout

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Real-time push: server delivers events to │
│              │ subscribed clients over persistent conn   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Polling wastes resources; REST can't push │
│ SOLVES       │ → subscriptions push exactly what changed │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Resolver called ONCE to get stream;       │
│              │ selection set runs once per event emitted │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Live dashboards, chat, order tracking,    │
│              │ notifications, collaborative editing      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Very high event rate (use raw WebSocket); │
│              │ simple low-frequency batch jobs           │
├──────────────┼───────────────────────────────────────────┤
│ SCALING KEY  │ Redis/Kafka pub/sub required for multi-   │
│              │ instance — in-memory buses don't scale    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "I'll tell you when it changes"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WebSocket → Server-Sent Events            │
│              │ → Event-Driven Architecture               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A live sports score app has 500,000 concurrent subscribers watching
a championship game. A goal is scored — one event must be delivered to all
500,000 clients within 200ms. Design the complete delivery architecture from
the score database update to the last mobile client receiving the WebSocket
message. Where are the bottlenecks? What infrastructure decisions determine
whether you hit 200ms?

**Q2.** A client subscribes to `orderUpdated(orderId: "42")` with a field
selection of `{ status, paymentMethod { last4 } }`. The `paymentMethod`
resolver makes an external API call. If order 42 updates 300 times per second
(high-frequency trading pattern), analyze every failure mode: what breaks first —
the external API, the GraphQL engine, the WebSocket, or the server memory?
Design a throttling strategy that protects all layers.
