---
layout: default
title: "gRPC"
parent: "HTTP & APIs"
nav_order: 222
permalink: /http-apis/grpc/
number: "0222"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP/2, Protocol Buffers, REST, RPC
used_by: Microservices, Service Mesh, gRPC Streaming, Protocol Buffers
related: REST, GraphQL, Protocol Buffers, WebSocket
tags:
  - api
  - grpc
  - rpc
  - http2
  - microservices
  - intermediate
---

# 222 — gRPC

⚡ TL;DR — gRPC is a high-performance, open-source RPC framework by Google that uses Protocol Buffers for binary serialization and HTTP/2 for transport, providing strongly typed service contracts, auto-generated clients, and streaming support for internal service-to-service communication.

| #222 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/2, Protocol Buffers, REST, RPC | |
| **Used by:** | Microservices, Service Mesh, gRPC Streaming, Protocol Buffers | |
| **Related:** | REST, GraphQL, Protocol Buffers, WebSocket | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A microservices platform has 50 internal services. They communicate over
REST/JSON. Each service must manually serialize/deserialize JSON,
write HTTP client boilerplate, maintain handwritten documentation of
request/response shapes, handle versioning, and implement retry logic.
JSON serialization is slow for high-volume inter-service traffic.
Adding a new field to a response means updating documentation, notifying
all consumer teams, and waiting for them to update their models. Without a
contract-first typed interface definition, type mismatches are silent bugs
discovered at runtime.

**THE BREAKING POINT:**
A payment service calls the account service 50,000 times per second.
JSON parsing is consuming 15% of payment service CPU. A schema mismatch
introduces a null field that wasn't in the docs, breaking the payment service
silently for 3 hours before anyone notices. The team has to manually generate
client libraries for each language (Go, Java, Python, Node.js) — and they're
always out of sync.

**THE INVENTION MOMENT:**
Google had this problem at massive scale — Stubby, their internal RPC system,
handled tens of billions of inter-service calls per second. They open-sourced
the design as gRPC in 2015: define the service interface in a `.proto` file
(Protocol Buffers), generate type-safe client and server stubs in any language
automatically, use HTTP/2 for multiplexed binary transport. The `.proto` file
is the contract — generated code is never out of sync.

---

### 📘 Textbook Definition

**gRPC** (gRPC Remote Procedure Calls) is an open-source, high-performance
framework for defining and calling remote services. Clients call remote methods
as if they were local function calls. Service interfaces are defined in `.proto`
files using Protocol Buffer IDL (Interface Definition Language). The `protoc`
compiler generates type-safe client stubs and server skeletons in 10+ languages.
gRPC uses Protocol Buffers for binary serialization (smaller, faster than JSON)
and HTTP/2 as transport (multiplexed, header-compressed streams). It supports
four communication patterns: unary (request/response), server streaming,
client streaming, and bidirectional streaming.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
gRPC lets services call each other's methods like local function calls — with auto-generated type-safe clients, binary serialization, and built-in streaming.

**One analogy:**

> REST is texting with someone: you write a message (JSON), send it, wait for a
> text back. gRPC is having a direct phone call: immediate voice connection,
> both sides can talk, much faster, but requires you both to have a phone
> (generated stub code). The phone number directory (`.proto` file) tells
> everyone how to reach each service and what to say.

**One insight:**
The `.proto` file is the source of truth. It defines not just the request/response
structure, but the service contract itself. When you change the `.proto`, all
generated clients and servers are updated automatically. You can never have a
client calling with the wrong types — the compiler rejects it. This eliminates
an entire class of integration bugs that REST APIs suffer from daily.

---

### 🔩 First Principles Explanation

**ARCHITECTURE COMPONENTS:**

```
.proto file
  (service definition + message types)
       ↓
protoc compiler
  (generates code in target language)
       ↓
┌─────────────────────────────────────┐
│  Generated                          │
│  Client Stub  ←── caller uses this  │
│  Server Skeleton ← Server implements this│
└─────────────────────────────────────┘
       ↓ HTTP/2 binary transport
```

**COMMUNICATION PATTERNS:**

```
1. UNARY (like REST):
   Client → one request → Server → one response

2. SERVER STREAMING:
   Client → one request → Server → stream of responses
   (e.g., real-time updates, file download)

3. CLIENT STREAMING:
   Client → stream of requests → Server → one response
   (e.g., file upload, sensor data ingestion)

4. BIDIRECTIONAL STREAMING:
   Client ⟷ Server: both send streams simultaneously
   (e.g., chat, real-time collaborative editing)
```

**WHY HTTP/2 MATTERS FOR gRPC:**

- **Multiplexing:** multiple gRPC calls on one TCP connection concurrently
- **Header compression (HPACK):** repeated header fields compressed across requests
- **Binary framing:** data sent in binary frames (not text) — smaller, faster
- **Flow control:** per-stream flow control prevents fast sender overwhelming slow receiver
- **Server push:** server can proactively send data (used by gRPC streaming)

**THE TRADE-OFFS:**

- Gain: binary serialization → 3–10× smaller payload, faster CPU for ser/deser.
- Cost: unreadable with curl/Postman — requires gRPC clients (grpcurl, Postman gRPC mode).
- Gain: auto-generated stubs in 10+ languages from single `.proto` source of truth.
- Cost: `.proto` toolchain required — adds build step complexity.
- Gain: HTTP/2 multiplexing → many concurrent calls on one connection.
- Cost: HTTP/2 required — harder to test locally, not supported by all proxies.
- Gain: built-in streaming (4 modes) vs SSE/WebSocket workarounds in REST.
- Cost: less browser-friendly — gRPC-Web proxy needed for browser clients.

---

### 🧪 Thought Experiment

**SETUP:**
A recommendation engine service is called by 20 other microservices,
averaging 100,000 calls per second. The current REST/JSON implementation:

- Average request size: 2KB JSON
- Average response size: 5KB JSON
- JSON serialization: 0.8ms per call
- Total CPU for ser/deser: significant

**WITH GRPC/PROTOBUF:**

- Average request size: ~400 bytes (5× smaller)
- Average response size: ~1KB (5× smaller)
- Binary ser/deser: 0.08ms per call (10× faster)
- HTTP/2 multiplexing: 100 concurrent calls on same connection vs 100 separate TCP connections

**IMPACT AT 100,000 req/s:**

- Network: 2KB × 100,000 = 200MB/s → 400KB × 100,000 = 40MB/s (5× reduction)
- CPU: 0.8ms × 100,000 = 80 CPU-seconds/s → 0.08ms × 100,000 = 8 CPU-seconds/s
- Connection overhead: eliminated by multiplexing

**THE INSIGHT:**
For high-throughput internal service calls, gRPC's binary transport and
multiplexing make a measurable hardware cost difference. At Google scale, this
is the difference between 100 servers and 20 servers for the same traffic.
For external APIs, REST remains better due to browser support and debuggability.

---

### 🧠 Mental Model / Analogy

> Think of gRPC as a strongly typed function call that happens to cross a network.
> Calling `userService.getUser("42")` in gRPC looks and feels like a local method
> call. The compiler verifies types. The generated stub handles HTTP/2, framing,
> serialization, headers, retries. You just call the function. In REST, you'd
> manually compose a URL string, serialize a JSON body, parse the response, and
> hope the types match.

- ".proto file" → function signatures in typed language
- "protoc compiler" → compiler that generates type-safe wrappers
- "Generated stub" → local proxy that handles network transparent to caller
- "HTTP/2 channel" → underlying transmission mechanism
- "Protocol Buffers" → the binary serialization format (like a very efficient JSON)

**Where this breaks down:** gRPC's abstraction of "just like a local call" can
hide network realities — you must still handle timeouts, retries, partial failures,
and latency. Treating gRPC calls like local function calls leads to
distributed system fallacies: assuming the network is reliable, fast, and zero-latency.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
gRPC lets two services call each other's functions directly over the network,
with both sides automatically getting code that handles the communication.
It's faster than REST because it uses a compact binary format instead of text,
and uses a newer, more efficient version of HTTP.

**Level 2 — How to use it (junior developer):**
Write a `.proto` file defining your service methods and message types. Run
`protoc` to generate Java (or other language) code. The generated code gives
you: (a) a server base class to implement, (b) a client stub to call. Implement
the server methods, start the server, create the client stub, call the methods.
For Spring Boot: use `grpc-spring-boot-starter`. Server: `@GrpcService`.
Client: inject the stub.

**Level 3 — How it works (mid-level engineer):**
The client stub serializes the request message using Protocol Buffers into
a binary byte array, adds gRPC framing headers (5 bytes: 1 flag byte + 4 length
bytes), and sends the frame over an HTTP/2 DATA frame on an existing HTTP/2
stream (or creates one). The server's HTTP/2 layer receives the DATA frame,
the gRPC layer unframes and deserializes the message, dispatches to the
registered service method. Response follows the reverse path. Status codes
are in `grpc-status` trailer headers (not HTTP status codes). Interceptors
wrap the call chain on both client and server — used for auth, tracing, logging,
retry, compression. The Channel abstraction manages the underlying HTTP/2
connection pool, load balancing, and reconnection.

**Level 4 — Why it was designed this way (senior/staff):**
gRPC's use of HTTP/2 rather than a custom protocol was a strategic choice
to leverage existing infrastructure (load balancers, proxies, firewalls) that
support HTTP/2. A custom binary protocol would have been slightly more efficient
but would break most network infrastructure. Protocol Buffers were chosen over
alternatives (Thrift, Avro, MessagePack) for their Google-proven stability,
backward/forward compatibility model (field numbers), and code generation
maturity. The decision to use trailing headers for gRPC status (rather than
HTTP status) means a gRPC "error" returns HTTP 200 with `grpc-status: 5`
(NOT_FOUND) in the trailer — this surprises every developer who first sees it
and breaks HTTP-layer monitoring that only looks at status codes. The 4
streaming patterns were motivated by Google's internal use cases: server streaming
for log delivery, client streaming for high-frequency sensor data, bidirectional
for Google Directions API trajectory updates. gRPC-Web (for browsers) is a
separate protocol because browsers can't access HTTP/2 trailers (where gRPC
status lives) — gRPC-Web encodes that data differently, requiring a gateway.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────────┐
│           GRPC CALL FLOW                                     │
├──────────────────────────────────────────────────────────────┤
│  Client code:                                                │
│  UserResponse resp = stub.getUser(UserRequest.of("42"))      │
│              ↓                                               │
│  Client stub: serialize request to protobuf byte[]          │
│  Add gRPC frame: [0x00][0x00 0x00 0x00 0x08][bytes...]      │
│  (flag + 4-byte length + data)                              │
│              ↓                                               │
│  HTTP/2 stream opened (or reused from pool)                 │
│  Headers frame: :method POST, :path /UserService/GetUser    │
│  DATA frame: [gRPC-framed protobuf bytes]                   │
│              ↓                                               │
│  Server HTTP/2 layer receives DATA frame                    │
│  gRPC layer unframes: strips 5-byte header, gets proto bytes│
│  Deserialize protobuf → UserRequest POJO                    │
│  Dispatch to registered UserService.getUser()               │
│  Handler runs, returns UserResponse POJO                    │
│  Serialize → protobuf bytes → gRPC frame → HTTP/2 DATA      │
│              ↓                                               │
│  HTTP/2 HEADERS frame (trailers):                           │
│    grpc-status: 0 (OK) or error code                        │
│    grpc-message: optional error detail                      │
│              ↓                                               │
│  Client deserialization: proto bytes → UserResponse         │
│  Return to caller                                           │
└──────────────────────────────────────────────────────────────┘
```

**gRPC Status Codes ≠ HTTP Status Codes:**

```
grpc-status: 0  = OK
grpc-status: 1  = CANCELLED
grpc-status: 2  = UNKNOWN
grpc-status: 5  = NOT_FOUND
grpc-status: 7  = PERMISSION_DENIED
grpc-status: 14 = UNAVAILABLE
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Developer workflow:
  Write user.proto (schema)
       ↓ protoc generates
  UserServiceGrpc.java (stubs)
       ↓
  Implement UserServiceImpl extends UserServiceGrpc.UserServiceImplBase
  Start gRPC server on port 9090
       ↓
  Client: UserServiceBlockingStub stub = UserServiceGrpc.newBlockingStub(channel)
  UserResponse r = stub.getUser(UserRequest.newBuilder().setId("42").build())

Runtime:
  HTTP/2 connection established (TLS in production)
  Binary request → network → binary response
  Trailer headers carry gRPC status
```

---

### 💻 Code Example

```protobuf
// user.proto — service definition
syntax = "proto3";
package com.example.user;

option java_package = "com.example.grpc.user";
option java_outer_classname = "UserProto";

service UserService {
  rpc GetUser (GetUserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream UserResponse); // server streaming
  rpc CreateUser (CreateUserRequest) returns (UserResponse);
}

message GetUserRequest {
  string user_id = 1;
}

message UserResponse {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4; // epoch millis
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}
```

```java
// Server implementation — Spring Boot with grpc-spring-boot-starter
@GrpcService
public class UserServiceImpl
        extends UserServiceGrpc.UserServiceImplBase {

    @Autowired private UserRepository userRepository;

    @Override
    public void getUser(GetUserRequest request,
                        StreamObserver<UserResponse> responseObserver) {
        userRepository.findById(request.getUserId())
            .ifPresentOrElse(
                user -> {
                    responseObserver.onNext(toProto(user));
                    responseObserver.onCompleted();
                },
                () -> responseObserver.onError(
                    Status.NOT_FOUND
                        .withDescription("User not found: " + request.getUserId())
                        .asRuntimeException()));
    }

    @Override
    public void listUsers(ListUsersRequest request,
                          StreamObserver<UserResponse> responseObserver) {
        // Server streaming: send each user as a separate message
        userRepository.findAll(PageRequest.of(0, request.getPageSize()))
            .forEach(user -> responseObserver.onNext(toProto(user)));
        responseObserver.onCompleted();
    }

    private UserResponse toProto(User user) {
        return UserResponse.newBuilder()
            .setId(user.getId())
            .setName(user.getName())
            .setEmail(user.getEmail())
            .setCreatedAt(user.getCreatedAt().toEpochMilli())
            .build();
    }
}
```

```java
// Client — inject stub
@Service
public class UserLookupService {

    // Injected by grpc-spring-boot-starter
    @GrpcClient("user-service")
    private UserServiceGrpc.UserServiceBlockingStub userStub;

    public UserResponse getUser(String userId) {
        return userStub.getUser(
            GetUserRequest.newBuilder()
                .setUserId(userId)
                .build());
        // Throws StatusRuntimeException on error:
        // NOT_FOUND, UNAVAILABLE, DEADLINE_EXCEEDED, etc.
    }
}
```

---

### ⚖️ Comparison Table

| Feature             | gRPC                         | REST/JSON              | GraphQL               |
| ------------------- | ---------------------------- | ---------------------- | --------------------- |
| **Serialization**   | Binary (Protobuf)            | Text (JSON)            | Text (JSON)           |
| **Performance**     | Highest                      | Medium                 | Medium                |
| **Type safety**     | Auto-generated, compile-time | Optional (OpenAPI)     | Runtime schema        |
| **Streaming**       | Built-in (4 modes)           | SSE/WebSocket only     | Subscriptions         |
| **Browser support** | gRPC-Web (proxy needed)      | Native                 | Native                |
| **Schema**          | .proto (required)            | OpenAPI (optional)     | SDL (required)        |
| **Tooling**         | grpcurl, Evans, Postman      | curl, Postman, browser | GraphiQL, Postman     |
| **Best for**        | Internal services            | External/public APIs   | Complex data fetching |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                          |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| gRPC errors return non-200 HTTP status codes              | gRPC always returns HTTP 200; actual status is in `grpc-status` trailing header                                                                  |
| gRPC doesn't support browser clients                      | gRPC-Web is the browser-compatible subset, requiring a proxy (Envoy, grpc-gateway)                                                               |
| gRPC is only for Google-scale systems                     | gRPC is beneficial for any microservices system where type safety and performance matter                                                         |
| REST and gRPC can't coexist                               | Many systems serve both: gRPC for internal services, REST for public APIs — `grpc-gateway` auto-generates REST from `.proto`                     |
| Protobuf removes need for backward compatibility planning | Removing or renumbering fields in `.proto` is a breaking change; you must follow protobuf evolution rules (add-only fields, don't reuse numbers) |

---

### 🚨 Failure Modes & Diagnosis

**gRPC UNAVAILABLE / Connection Refused at Scale**

Symptom:
Service intermittently returns `StatusRuntimeException: UNAVAILABLE` under load.
Reducing RPS makes the error disappear.

Root Cause:
gRPC uses HTTP/2, which limits concurrent streams per connection
(`MAX_CONCURRENT_STREAMS`, default 100 in many servers). A single channel
with one HTTP/2 connection at 100+ concurrent calls will fail.

Diagnostic Command / Tool:

```bash
# Check channel pool size — grpc-java:
# In GrpcChannelBuilder, see if only one channel/connection created

# gRPC reflection + grpcurl to test status:
grpcurl -plaintext localhost:9090 list

# Increase max concurrent streams and use a connection pool:
ManagedChannel channel = ManagedChannelBuilder
    .forAddress(host, port)
    .usePlaintext()  // remove for TLS
    // Use per-RPC executor + multiple channels for high concurrency
    .build();
```

Fix:
Create multiple channels (connection pool) or use a client load balancer
that distributes calls across multiple connections/server replicas.

Prevention:
Load test gRPC endpoints before production. Monitor `grpc_client_started_total`
and `grpc_server_started_total` Prometheus metrics for connection saturation.

---

**Proto Schema Breaking Change**

Symptom:
After deploying a new service version, old clients receive garbled or missing
field values. No errors — just wrong data.

Root Cause:
A developer renamed a field or reused a field number in the `.proto` file.
Protobuf serializes by field number, not name — renaming is safe; reusing
a number for a different type is a breaking binary incompatibility.

Diagnostic Command / Tool:

```bash
# Use buf (proto lint + breaking change detection):
buf breaking --against '.git#branch=main'
# Output: "Field "1" on message "UserResponse" changed type from string to int64"

# Legacy: compare manually:
git diff main -- user.proto
# Look for changed field numbers
```

Fix:
Never reuse field numbers. To "remove" a field: use `reserved` keyword.
New fields must always use new, unused field numbers.

Prevention:
Run `buf breaking` in CI pipeline. Fail builds that introduce breaking changes.
Maintain a `.proto` change review process.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HTTP/2` — gRPC runs over HTTP/2; must understand multiplexing, streams, header compression
- `Protocol Buffers` — gRPC's serialization format; must understand `.proto` schema and binary encoding
- `RPC` — gRPC is an RPC framework; understand the remote procedure call concept

**Builds On This (learn these next):**

- `Protocol Buffers` — the serialization layer that makes gRPC fast and type-safe
- `gRPC Streaming` — the 4 streaming patterns (server, client, bidirectional, unary)
- `Service Mesh` — Envoy/Istio integrate deeply with gRPC for observability and traffic management

**Alternatives / Comparisons:**

- `REST` — the default alternative; better for public APIs, browser clients
- `GraphQL` — better for complex client-driven data fetching; single endpoint
- `WebSocket` — raw bidirectional streaming; less structured than gRPC streaming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ RPC framework: .proto schema → auto-gen  │
│              │ clients + servers; HTTP/2 + Protobuf      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ HTTP/JSON is slow, untyped, manual-coded; │
│ SOLVES       │ gRPC is fast, typed, auto-generated       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ .proto is the single source of truth —    │
│              │ compile-time type safety across languages │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Internal microservice communication;      │
│              │ high throughput; polyglot environments    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Public API, browser clients (use REST);   │
│              │ teams unfamiliar with protobuf toolchain  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Performance + type safety vs debugging    │
│              │ difficulty (binary, not curl-friendly)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Function calls across the network"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Protocol Buffers → gRPC Streaming        │
│              │ → Service Mesh                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team is migrating 50 microservices from REST/JSON to gRPC.
Service A (Java) calls Service B (Go) which calls Service C (Python).
Design the migration strategy given that: services can't all be migrated
simultaneously, some services need both REST and gRPC for different callers,
and the existing monitoring system only understands HTTP status codes.
What are the transitional architecture patterns and their trade-offs?

**Q2.** gRPC's HTTP/2 multiplexing means a long-running server-streaming RPC
shares an HTTP/2 connection with other unary RPCs on the same channel.
A streaming RPC that delivers a large file (10GB) at 100MB/s starts at the same
time as a time-critical unary RPC. Analyze HTTP/2 flow control interaction:
does the large stream starve the unary call? How do you prevent this? What
gRPC configuration and infrastructure changes address this?
