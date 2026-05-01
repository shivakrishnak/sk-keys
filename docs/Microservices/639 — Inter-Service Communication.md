---
layout: default
title: "Inter-Service Communication"
parent: "Microservices"
nav_order: 639
permalink: /microservices/inter-service-communication/
number: "639"
category: Microservices
difficulty: ★★☆
depends_on: "Monolith vs Microservices, Service Discovery"
used_by: "Synchronous vs Async Communication, API Gateway (Microservices), Service Mesh (Microservices)"
tags: #intermediate, #microservices, #networking, #distributed, #protocol
---

# 639 — Inter-Service Communication

`#intermediate` `#microservices` `#networking` `#distributed` `#protocol`

⚡ TL;DR — **Inter-Service Communication** is how microservices talk to each other across network boundaries. Two fundamental styles: **synchronous** (HTTP/REST, gRPC — caller waits for response) and **asynchronous** (message queues, event streams — caller doesn't wait). The right choice depends on whether the caller needs the response immediately.

| #639            | Category: Microservices                                                                       | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Monolith vs Microservices, Service Discovery                                                  |                 |
| **Used by:**    | Synchronous vs Async Communication, API Gateway (Microservices), Service Mesh (Microservices) |                 |

---

### 📘 Textbook Definition

**Inter-Service Communication** refers to all mechanisms by which separate microservice processes exchange data and coordinate work across network boundaries. Unlike in-process method calls in a monolith, inter-service communication is subject to network failures, latency variance, partial failures, and serialisation overhead. Communication styles are categorised along two axes: **synchrony** (synchronous vs asynchronous) and **message type** (request/response vs event/command). Synchronous communication includes HTTP/REST (text-based, ubiquitous), gRPC (binary, protobuf-based, strongly typed, HTTP/2), and GraphQL (flexible querying). Asynchronous communication includes message queues (point-to-point, guaranteed delivery — RabbitMQ, SQS), event streaming (publish/subscribe with retention — Kafka), and fire-and-forget patterns. The choice between synchronous and asynchronous communication is the most consequential architectural decision in a microservices system — it determines coupling, availability requirements, error handling complexity, and overall system behaviour under failure.

---

### 🟢 Simple Definition (Easy)

When a microservice needs to get data from or trigger an action in another service, it uses inter-service communication. It can either ask and wait (synchronous — like a phone call) or send a message and continue (asynchronous — like sending an email). The choice changes how your system handles failures and how tightly coupled the services are.

---

### 🔵 Simple Definition (Elaborated)

OrderService needs to: (1) validate that a product exists in InventoryService — needs the answer before proceeding → synchronous REST call; (2) notify ShippingService after an order is placed — doesn't need an immediate response → async event on a message queue. The synchronous call means OrderService is temporarily dependent on InventoryService's availability. The async event means ShippingService can be down, and the event will wait in the queue until it restarts — OrderService succeeds regardless. Choosing sync vs async for each interaction is the key design decision.

---

### 🔩 First Principles Explanation

**Protocol comparison — HTTP/REST vs gRPC:**

```
HTTP/REST:
  Payload: JSON (text, ~80-100 bytes overhead per field name)
  Protocol: HTTP/1.1 (one request per connection, unless keep-alive)
  Typing: loosely typed (consumer parses JSON manually)
  Code gen: manual or OpenAPI generator
  Human readable: yes
  Browser support: yes (direct)

  Example:
  POST /api/orders HTTP/1.1
  Content-Type: application/json
  {
    "productId": 12345,
    "quantity": 3,
    "customerId": 67890
  }
  → ~150 bytes

gRPC:
  Payload: Protocol Buffers (binary, field numbers instead of names)
  Protocol: HTTP/2 (multiplexed streams, header compression)
  Typing: strongly typed (proto schema shared between services)
  Code gen: automatic (grpc tools generate stubs)
  Human readable: no (binary)
  Browser support: requires grpc-web proxy

  Example:
  message PlaceOrderRequest {
    int64 product_id = 1;    // field number, not name in binary
    int32 quantity = 2;
    int64 customer_id = 3;
  }
  → ~15 bytes (10x smaller than JSON)
  → HTTP/2 multiplexing: multiple simultaneous RPCs on same connection

WHEN TO USE EACH:
  HTTP/REST: public APIs, browser clients, simple CRUD, team prefers JSON
  gRPC: internal services, high-throughput, strong typing needed, streaming
```

**Synchronous vs Asynchronous — failure modes:**

```
SYNCHRONOUS (HTTP/REST, gRPC):

  OrderService → GET /inventory/12345 → InventoryService
                      ↑ blocks here
  InventoryService DOWN → OrderService gets 503 → OrderService fails

  Temporal coupling: OrderService can only succeed when InventoryService is UP.
  Cascade failure risk: if InventoryService has 500ms latency spike,
    OrderService threads block → OrderService thread pool exhausted → OrderService DOWN

ASYNCHRONOUS (Kafka/RabbitMQ):

  OrderService → publish "OrderPlaced" event → Kafka topic
                 (returns immediately)
  ShippingService may be DOWN:
    → message waits in Kafka (retention: 7 days default)
    → ShippingService restarts → consumes missed events
    → No impact on OrderService

  Temporal decoupling: services can be down, messages accumulate.
  Trade-off: caller cannot know if downstream processed the event.
  Harder to debug: asynchronous flow spans multiple services and time.
```

**Service-to-service authentication — often overlooked:**

```
PROBLEM: OrderService calls PaymentService inside the cluster.
         PaymentService must verify: is this really OrderService?
         (prevent rogue services from calling payment APIs)

SOLUTIONS:
  1. mTLS (mutual TLS) — Service Mesh (Istio) handles this automatically
     → Both services present certificates → identity verified at network level
     → Application code doesn't change

  2. JWT service tokens — OrderService includes JWT in Authorization header
     → PaymentService validates JWT signature (from shared secret or JWKS)
     → Token includes "sub: order-service" (service identity claim)

  3. API Keys — simple but harder to rotate, no expiry
     → Acceptable for internal services, not for external-facing APIs

  KUBERNETES + ISTIO:
    Istio automatically issues certificates to each pod (SPIFFE/X.509)
    mTLS is transparent to application code
    → All inter-service calls are mutually authenticated + encrypted
```

---

### ❓ Why Does This Exist (Why Before What)

In a monolith, calling another module is a method call (nanoseconds, never fails). Between microservices, every call crosses a network boundary:

- Networks fail (packet loss, timeouts).
- Services go down (deployments, crashes, OOM).
- Latency is variable (milliseconds to seconds).
- Serialisation is required (Java objects → JSON/bytes → Java objects).

Inter-service communication patterns exist to handle these realities: resilience patterns (retry, circuit breaker) to handle failures, asynchronous messaging to decouple availability, efficient protocols (gRPC) to reduce overhead.

---

### 🧠 Mental Model / Analogy

> Inter-service communication is like choosing between two ways to send a document to a colleague: (1) Synchronous: you walk to their desk and wait while they review it — you get immediate feedback but are blocked until they finish. If they are in a meeting (unavailable), you cannot proceed. (2) Asynchronous: you put the document in their inbox and return to your work — they process it when available; you get a response later (or never). Choose synchronous when you need their answer before you can continue. Choose asynchronous when you can proceed and handle the response (or failure) later.

---

### ⚙️ How It Works (Mechanism)

**gRPC service definition and Java stub usage:**

```protobuf
// inventory.proto — shared between services:
syntax = "proto3";
package com.example.inventory;

service InventoryService {
  rpc CheckInventory (InventoryRequest) returns (InventoryResponse);
  rpc WatchInventoryChanges (InventoryRequest) returns (stream InventoryUpdate); // server streaming
}

message InventoryRequest { int64 product_id = 1; }
message InventoryResponse { bool in_stock = 1; int32 quantity = 2; }
message InventoryUpdate { int64 product_id = 1; int32 new_quantity = 2; }
```

```java
// Generated stub usage in OrderService:
@Service
class OrderService {

    private final InventoryServiceGrpc.InventoryServiceBlockingStub inventoryStub;

    public OrderService(ManagedChannel channel) {
        this.inventoryStub = InventoryServiceGrpc.newBlockingStub(channel)
            .withDeadlineAfter(500, TimeUnit.MILLISECONDS); // always set deadline
    }

    public void placeOrder(Long productId, int quantity) {
        InventoryResponse response = inventoryStub.checkInventory(
            InventoryRequest.newBuilder().setProductId(productId).build()
        );

        if (!response.getInStock() || response.getQuantity() < quantity) {
            throw new InsufficientInventoryException("Product " + productId);
        }
        // proceed with order...
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Monolith vs Microservices
(forced inter-process communication)
        │
        ▼
Inter-Service Communication  ◄──── (you are here)
(HTTP/REST, gRPC, messaging)
        │
        ├── Synchronous vs Async Communication → core choice
        ├── API Gateway → entry point for sync external calls
        ├── Service Mesh → manages service-to-service communication
        ├── Circuit Breaker → handles failures in sync communication
        └── Event-Driven Microservices → async messaging architecture
```

---

### 💻 Code Example

**OpenFeign HTTP client with timeout and error handling:**

```java
// Feign client: declarative HTTP client with service discovery integration
@FeignClient(
    name = "inventory-service",
    configuration = InventoryClientConfig.class,
    fallbackFactory = InventoryClientFallbackFactory.class
)
interface InventoryClient {
    @GetMapping("/api/inventory/{productId}")
    InventoryResponse checkInventory(@PathVariable Long productId);
}

@Configuration
class InventoryClientConfig {
    @Bean
    Options feignOptions() {
        return new Options(
            1000,  // connectTimeoutMillis
            3000,  // readTimeoutMillis
            true   // followRedirects
        );
    }
}

@Component
class InventoryClientFallbackFactory implements FallbackFactory<InventoryClient> {
    @Override
    public InventoryClient create(Throwable cause) {
        return productId -> InventoryResponse.unavailable(cause.getMessage());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                 | Reality                                                                                                                                                                                                          |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Synchronous HTTP calls between microservices are the default correct choice   | Synchronous calls create temporal coupling and cascade failure risk. Many inter-service interactions (notifications, side effects, workflows) are better modelled as async events                                |
| gRPC is always better than REST for microservices                             | gRPC requires proto schema management, binary tooling, and server-side streaming support. For CRUD APIs consumed by browsers, REST is simpler. gRPC excels for high-throughput internal service-to-service calls |
| Inter-service calls within a cluster are inherently secure (internal network) | Internal network security is insufficient. Services must authenticate each other (mTLS, JWT tokens) to prevent rogue or compromised services from calling sensitive APIs                                         |

---

### 🔥 Pitfalls in Production

**Missing connection timeouts — thread pool exhaustion cascade:**

```java
// DANGEROUS: no timeout → threads block forever on slow downstream:
RestTemplate restTemplate = new RestTemplate(); // default: no timeout!
ResponseEntity<String> response =
    restTemplate.getForEntity("http://slow-service/api", String.class);
// If slow-service takes 60s: all threads blocked → OrderService thread pool
// exhausted → OrderService stops responding → upstream services timeout
// → cascade failure: one slow service brings down the whole cluster

// FIX: always configure explicit timeouts:
@Bean
RestTemplate restTemplate() {
    HttpComponentsClientHttpRequestFactory factory =
        new HttpComponentsClientHttpRequestFactory();
    factory.setConnectTimeout(Duration.ofMillis(1_000));   // connect: 1s
    factory.setReadTimeout(Duration.ofMillis(3_000));      // read: 3s
    return new RestTemplate(factory);
}

// For gRPC, always use withDeadlineAfter():
stub.withDeadlineAfter(500, TimeUnit.MILLISECONDS).callMethod(request);
```

---

### 🔗 Related Keywords

- `Synchronous vs Async Communication` — the core choice for each inter-service interaction
- `API Gateway (Microservices)` — orchestrates and proxies inter-service calls for external clients
- `Service Mesh (Microservices)` — manages, secures, and observes all inter-service communication
- `Circuit Breaker (Microservices)` — protects services from cascade failures in sync communication

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HTTP/REST    │ JSON, HTTP/1.1, universal, browser OK     │
│ gRPC         │ Protobuf binary, HTTP/2, typed, ~10x faster│
│ Messaging    │ Kafka/RabbitMQ, async, decoupled           │
├──────────────┼───────────────────────────────────────────┤
│ SYNC         │ Caller waits. Coupled availability.        │
│ ASYNC        │ Caller continues. Queue buffers failures.  │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS SET   │ Connection timeout + Read timeout         │
│              │ No timeout = cascade failure risk          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment processing system uses synchronous gRPC calls from `CheckoutService` to `PaymentService`. During Black Friday, `PaymentService` degrades to 5-second response times (normally 100ms). Describe the exact cascade failure sequence: thread pool exhaustion in `CheckoutService`, upstream services timing out, and how a circuit breaker would change this scenario. What circuit breaker configuration (failure threshold, slow call threshold, wait duration in OPEN state) would you choose for a payment service?

**Q2.** You are designing a new e-commerce feature: after an order is placed, you need to (a) deduct inventory, (b) send confirmation email, (c) update loyalty points, (d) notify the warehouse. Which of these should be synchronous calls (in the critical path of order placement), and which should be asynchronous events? What happens to the user experience if the email service is down? How does an async event queue change the resilience story for each of these four actions?
