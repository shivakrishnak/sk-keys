---
layout: default
title: "Adapter Pattern (Microservices)"
parent: "Microservices"
nav_order: 680
permalink: /microservices/adapter-pattern-microservices/
number: "680"
category: Microservices
difficulty: ★★★
depends_on: "Sidecar Pattern, Cross-Cutting Concerns"
used_by: "Service Mesh, Ambassador Pattern"
tags: #advanced, #microservices, #distributed, #architecture, #pattern
---

# 680 — Adapter Pattern (Microservices)

`#advanced` `#microservices` `#distributed` `#architecture` `#pattern`

⚡ TL;DR — The **Adapter Pattern (Microservices)** deploys a sidecar that translates inbound requests from one protocol or format to what the application understands, enabling protocol evolution without modifying the application.

| #680            | Category: Microservices                 | Difficulty: ★★★ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | Sidecar Pattern, Cross-Cutting Concerns |                 |
| **Used by:**    | Service Mesh, Ambassador Pattern        |                 |

---

### 📘 Textbook Definition

The **Adapter Pattern** in microservices is a sidecar-based structural pattern where a co-located proxy container (the adapter) translates inbound requests from an external protocol or format into the protocol and format expected by the primary application container. The adapter sits between the network and the application, abstracting protocol differences: it may translate gRPC to REST, HTTP/1.1 to HTTP/2, JSON to Protobuf, or add/remove headers required by the application. The pattern mirrors the GoF Adapter design pattern but at the infrastructure (container) level rather than the code level. It is particularly valuable for: legacy applications that only understand HTTP/1.1 REST when clients want to use gRPC; or for standardising APIs across heterogeneous services by enforcing a common external protocol regardless of each service's internal protocol. The adapter handles inbound concerns; its complement the Ambassador Pattern handles outbound concerns.

---

### 🟢 Simple Definition (Easy)

An adapter is a sidecar that translates between protocols. Your service speaks REST but clients want gRPC — the adapter converts incoming gRPC calls to REST before passing them to your service. Your service never knows gRPC existed. Like a power plug adapter: the same device, different socket.

---

### 🔵 Simple Definition (Elaborated)

Legacy Order Service only speaks HTTP/1.1 REST. Your mobile app team wants to use gRPC for efficiency (binary, streaming, better performance). Without adapter: rebuild Order Service to support gRPC (months of work, potential regression). With adapter sidecar: deploy a gRPC-to-REST adapter alongside Order Service. Mobile app sends gRPC. Adapter translates to HTTP/1.1 REST. Order Service receives REST — same as before. Mobile app gets gRPC streaming. Both sides get what they need without any code changes to Order Service.

---

### 🔩 First Principles Explanation

**Protocol translation without adapter — the coupling problem:**

```
WITHOUT ADAPTER:
  Service A: legacy REST/HTTP1.1 (cannot be easily changed)
  New requirement: expose gRPC interface for mobile clients

  Option 1: Add gRPC support to Service A code
    - Requires gRPC Java library integration
    - Protobuf schema maintenance
    - Dual protocol testing
    - Risk: changes to stable legacy service
    - Time: 2-4 sprints of engineering effort

  Option 2: Build a separate gRPC facade microservice
    - New service to deploy, monitor, maintain
    - Extra network hop for every call
    - Doubles the services to manage
    - Eventual drift between facade and service

WITH ADAPTER SIDECAR:
  Deploy adapter alongside Service A: zero app code changes.

  Mobile client → gRPC:50051 → Adapter (gRPC → REST translation)
                             → REST:8080 → Service A

  Adapter: pure protocol translation
    Accepts: gRPC (Protobuf binary)
    Translates: Protobuf → JSON, gRPC method → HTTP path+method
    Forwards: HTTP/1.1 REST to localhost:8080
    Returns: REST response → Protobuf, HTTP status → gRPC status

  Service A: zero changes. Still REST.
  Mobile app: gRPC streaming, binary protocol efficiency.
  Adapter: single responsibility — translation only.
```

**Envoy gRPC-JSON transcoder — the standard adapter implementation:**

```yaml
# Envoy config: gRPC → REST adapter
# Intercepts inbound gRPC → translates to REST → forwards to app

static_resources:
  listeners:
    - name: grpc_adapter
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 50051 # gRPC port (external clients connect here)
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/.../HttpConnectionManager
                codec_type: HTTP2 # gRPC requires HTTP/2
                http_filters:
                  # gRPC-JSON transcoder: converts gRPC ↔ REST automatically
                  - name: envoy.filters.http.grpc_json_transcoder
                    typed_config:
                      "@type": type.googleapis.com/.../GrpcJsonTranscoder
                      proto_descriptor: /etc/envoy/api_descriptor.pb
                      # ^ compiled from .proto file: protoc --descriptor_set_out=api_descriptor.pb
                      services: ["com.example.order.OrderService"]
                      print_options:
                        add_whitespace: true
                        preserve_proto_field_names: true
                  - name: envoy.filters.http.router
                route_config:
                  virtual_hosts:
                    - name: order_service_rest
                      domains: ["*"]
                      routes:
                        - match: { prefix: "/" }
                          route:
                            cluster: order_service_rest_cluster

  clusters:
    - name: order_service_rest_cluster
      connect_timeout: 1s
      load_assignment:
        cluster_name: order_service_rest_cluster
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: 127.0.0.1 # localhost: same pod
                      port_value: 8080 # Service A's REST port
```

**Proto definition drives the transcoding mapping:**

```protobuf
// order.proto: defines gRPC API + REST mapping annotations
syntax = "proto3";
package com.example.order;
import "google/api/annotations.proto";

service OrderService {
  rpc GetOrder (GetOrderRequest) returns (OrderResponse) {
    option (google.api.http) = {
      get: "/api/v1/orders/{order_id}"
      // gRPC: OrderService.GetOrder(GetOrderRequest{orderId: "abc"})
      // REST: GET /api/v1/orders/abc
      // Envoy transcoder maps these automatically
    };
  }

  rpc CreateOrder (CreateOrderRequest) returns (OrderResponse) {
    option (google.api.http) = {
      post: "/api/v1/orders"
      body: "*"
      // gRPC: OrderService.CreateOrder(CreateOrderRequest{...})
      // REST: POST /api/v1/orders with JSON body
    };
  }
}
```

**JSON/XML adapter for legacy services:**

```yaml
# Alternative: custom adapter container for JSON↔XML translation
# Legacy service: only understands XML (SOAP)
# New clients: want JSON REST

spec:
  containers:
    - name: legacy-billing-service
      image: legacy-billing:1.0.0 # only understands XML/SOAP
      ports:
        - containerPort: 8080

    - name: json-xml-adapter
      image: json-xml-adapter:1.0.0
      # Custom adapter: nginx + Lua OR a lightweight Go proxy
      # Accepts: JSON REST requests (external clients)
      # Translates: JSON → XML/SOAP
      # Forwards to: localhost:8080 (legacy billing)
      # Translates: XML/SOAP response → JSON
      # Returns: JSON to client
      ports:
        - containerPort: 8081 # external JSON port
      env:
        - name: UPSTREAM_URL
          value: "http://localhost:8080"
        - name: UPSTREAM_CONTENT_TYPE
          value: "application/xml"
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Adapter Pattern:

- Legacy services must be rewritten to support new protocols (high risk, high cost)
- Clients must implement legacy protocols (exposing internal legacy stack to outside)
- Protocol upgrades require coordinated changes to both service and all clients
- Multiple protocol versions accumulate in application code (complexity grows)

WITH Adapter Pattern:
→ Legacy services gain new protocol support with zero application code changes
→ Clients use modern protocol; service stays unchanged (risk minimised)
→ Protocol upgrades are infrastructure changes (adapter swap, no app deployment)
→ Service code stays focused on business logic, not protocol handling

---

### 🧠 Mental Model / Analogy

> An electrical power adapter. When you travel from the US to Europe, your device (service) only accepts US 110V/Type-A plugs. The adapter converts the European 220V/Type-C outlet to US format. Your device never knows it's plugged into a European socket — it just gets the power it expects. The adapter handles the incompatibility transparently.

"US device" = application that speaks one protocol (REST)
"European socket" = external clients using a different protocol (gRPC)
"Power adapter" = sidecar adapter container
"Power (electricity)" = requests and responses flowing through

---

### ⚙️ How It Works (Mechanism)

**Request flow through adapter — gRPC to REST:**

```
INBOUND: Mobile App → gRPC Call

  1. Mobile: OrderService.GetOrder({orderId: "abc-123"})
     Protocol: HTTP/2, binary Protobuf encoding

  2. Adapter receives gRPC request on port 50051
     Transcoder: decodes Protobuf → OrderResponse GetOrder(orderId="abc-123")
     Maps: gRPC method → REST: GET /api/v1/orders/abc-123

  3. Adapter → HTTP/1.1 GET /api/v1/orders/abc-123 → localhost:8080
     App: standard REST call (no knowledge of gRPC client)

  4. App returns: HTTP 200 {"orderId":"abc-123","status":"CONFIRMED"}

  5. Adapter: JSON response → Protobuf encode → gRPC response
     Returns to mobile: OrderResponse{orderId="abc-123", status=CONFIRMED}
     HTTP status: 200 → gRPC status: OK

  Error mapping:
    HTTP 404 → gRPC NOT_FOUND
    HTTP 400 → gRPC INVALID_ARGUMENT
    HTTP 500 → gRPC INTERNAL
    HTTP 503 → gRPC UNAVAILABLE
```

---

### 🔄 How It Connects (Mini-Map)

```
External Clients        Inbound Protocols
(gRPC, SOAP, etc.)      (what clients want to speak)
        │                       │
        └──────────┬────────────┘
                   ▼
        Adapter Pattern  ◄──── (you are here)
        (inbound-focused protocol-translating sidecar)
                   │
        ┌──────────┴──────────────┐
        ▼                         ▼
Application (REST)         Ambassador Pattern
(unchanged, speaks         (outbound: app →
 its own protocol)          external services)
```

---

### 💻 Code Example

**Validating gRPC transcoding works with grpcurl:**

```bash
# Test the adapter: call gRPC endpoint, verify REST translation works

# List available gRPC services via adapter:
grpcurl -plaintext localhost:50051 list
# Output: com.example.order.OrderService

# Call GetOrder via gRPC (adapter translates to REST internally):
grpcurl -plaintext \
  -d '{"orderId": "550e8400-e29b-41d4-a716-446655440000"}' \
  localhost:50051 \
  com.example.order.OrderService/GetOrder

# Expected output:
# {
#   "orderId": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "CONFIRMED",
#   "totalAmount": "149.99"
# }

# Verify: the REST call was made to localhost:8080 (check Envoy access log):
kubectl logs order-service-pod -c json-xml-adapter --tail=5
# {"method":"GET","path":"/api/v1/orders/550e8400...","response_code":200}
# Confirms: gRPC call was translated to REST internally
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Adapter Pattern in microservices is the same as GoF Adapter | GoF Adapter wraps an object in code (class-level). Microservices Adapter Pattern deploys a proxy container (infrastructure-level). Same intent (interface translation) at different layers of abstraction                |
| Adapter always means gRPC-to-REST                           | Adapter applies to any protocol/format translation: JSON↔XML, HTTP/1.1↔HTTP/2, AMQP↔Kafka, REST↔SOAP, binary↔text. The gRPC-to-REST case is the most common modern use case                                              |
| Adapter and Ambassador are interchangeable terms            | Ambassador = outbound proxy (represents service to external world). Adapter = inbound proxy (translates external protocol to internal protocol). Ambassador handles egress; Adapter handles ingress at the service level |
| Adapter adds two network hops per request                   | The adapter is on the same pod (loopback), so the "hop" is ~0.1ms. The external client still makes one network call to the pod's IP. Adapter adds one loopback hop inside the pod, not a separate network hop            |

---

### 🔥 Pitfalls in Production

**Proto descriptor out of sync with application REST API:**

```
PROBLEM:
  Envoy transcoder uses a compiled proto descriptor (api_descriptor.pb)
  that maps gRPC methods to REST paths.

  Developer adds new REST endpoint: POST /api/v1/orders/bulk
  Does NOT update order.proto or recompile descriptor.

  gRPC clients: cannot call bulk create (no method in proto)
  REST clients: bulk create works fine

  6 months later: new developer adds BulkCreateOrders to proto
  Recompiles descriptor. Deploys new adapter config.

  Proto has wrong path annotation: "post: /api/v1/orders/batch" (old name)
  Actual app: POST /api/v1/orders/bulk

  gRPC clients: 404 on BulkCreateOrders → transcoder maps to /batch → 404

FIX:
  1. Treat .proto file as source of truth, not afterthought:
     Proto-first: define proto method WITH http annotation FIRST.
     Generate REST controller stub from proto (openapi-generator or similar).

  2. CI job: recompile proto descriptor and include in Docker image build.
     If proto changes: adapter image auto-rebuilt with correct descriptor.

  3. Integration test: for every gRPC method, test via gRPC AND REST:
     Both paths exercised in CI → mismatch caught before prod.

  4. Shared proto repository:
     api-contracts repo: owns .proto files and generated descriptors.
     Service team: imports from api-contracts (not their own copy).
     Single source of truth for all adapters in the cluster.
```

---

### 🔗 Related Keywords

- `Sidecar Pattern` — the structural parent; Adapter is a sidecar specialised for inbound translation
- `Ambassador Pattern` — the complementary outbound-focused sidecar
- `Cross-Cutting Concerns` — protocol normalisation is a cross-cutting infrastructure concern
- `Service Mesh` — orchestrates adapters and ambassadors at cluster scale
- `Service Contract` — the proto/OpenAPI contract that defines what the adapter must translate to

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Sidecar that translates INBOUND protocol  │
│              │ so app stays unchanged (REST stays REST)  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Legacy app + new protocol clients; adding │
│              │ gRPC to REST-only service without rewrite │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Service can natively support the protocol;│
│              │ translation adds semantic loss/complexity  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A power adapter: your device stays the   │
│              │  same, the socket changes."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sidecar → Ambassador → Service Mesh       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are adding gRPC support to a REST service via the Envoy gRPC-JSON Transcoder adapter. The REST service uses pagination: `GET /api/v1/orders?page=1&pageSize=20&sort=createdAt`. Design the Protobuf message and HTTP annotation for the corresponding `ListOrders` gRPC method. What happens to query parameters in the REST call when mapped from the Protobuf message? How does the transcoder handle the `sort` parameter that contains non-trivial value encoding (e.g., `createdAt:desc`)?

**Q2.** Your adapter pattern deployment has the gRPC-JSON transcoder handling all inbound traffic. A gRPC client sends a streaming RPC: `rpc StreamOrderUpdates (StreamRequest) returns (stream OrderEvent)`. Your REST service does not support streaming — it uses polling (`GET /api/v1/orders/updates?since=timestamp`). Describe whether the Envoy gRPC-JSON transcoder can handle this case, what it would mean to "adapt" a streaming gRPC interface to a polling REST backend, and what alternative architectures you would use instead of a simple adapter for this scenario.
