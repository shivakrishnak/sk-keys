---
id: NET-041
title: "gRPC and Protocol Buffers"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-038, NET-040
used_by: NET-048, NET-056
related: NET-038, NET-040, NET-048
tags:
  - networking
  - grpc
  - protobuf
  - http2
  - rpc
  - api
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/net/grpc-and-protocol-buffers/
---

**⚡ TL;DR** - gRPC is Google's open-source RPC framework
that uses HTTP/2 for transport, Protocol Buffers (protobuf)
for serialization, and generates type-safe client/server
code in 10+ languages. It achieves 5-10x lower latency and
3-10x smaller payload size vs REST+JSON for inter-service
communication. The tradeoff: binary format is harder to
debug, requires a protobuf schema compiler, and is not
native in browsers (needs gRPC-Web proxy).

| #041 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | HTTP/2 Multiplexing (NET-038), WebSocket Protocol (NET-040) | |
| **Used by:** | Network Latency Sources and Measurement, HTTP Connection Management | |
| **Related:** | HTTP/2 Multiplexing, WebSocket Protocol, Network Latency Sources | |

---

### 🔥 The Problem gRPC Solves

A microservices system has 30 services calling each other.
REST+JSON: each service writes its own HTTP client, parses
untyped JSON, handles null fields, and hopes the field
name is correct. A field renamed from `user_id` to
`userId` silently breaks callers - no compile-time error.
With gRPC: a `.proto` schema defines the contract, the
compiler generates typed stubs, renaming breaks the build
immediately. 10 languages, one schema, zero ambiguity.

---

### 🧠 Intuition: Contract-First RPC

```
REST: "I have a resource at /users/123, here's its JSON"
gRPC: "I have a UserService with GetUser(UserRequest)→User"

The difference:
  REST is resource-oriented, JSON-typed at runtime
  gRPC is procedure-oriented, schema-typed at compile time

Analogy: REST is like duck typing, gRPC is like Java
  interfaces. Both work, but gRPC catches type errors
  before production.
```

---

### ⚙️ Protocol Buffers: The Serialization Format

**Defining a schema:**

```protobuf
// user.proto
syntax = "proto3";
package com.example;

option java_package = "com.example.grpc";
option java_outer_classname = "UserProto";

// Message definition
message User {
    int64 id = 1;          // field number 1
    string name = 2;       // field number 2
    string email = 3;      // field number 3
    repeated string roles = 4;  // list
    UserStatus status = 5;
    google.protobuf.Timestamp created_at = 6;
}

enum UserStatus {
    USER_STATUS_UNSPECIFIED = 0;  // proto3: 0 is default
    USER_STATUS_ACTIVE = 1;
    USER_STATUS_INACTIVE = 2;
    USER_STATUS_SUSPENDED = 3;
}

// Service definition
service UserService {
    // Unary RPC (standard request/response)
    rpc GetUser(GetUserRequest) returns (User);

    // Server streaming (server sends N responses)
    rpc ListUsers(ListUsersRequest) returns (stream User);

    // Client streaming (client sends N requests)
    rpc BatchCreateUsers(stream CreateUserRequest)
        returns (BatchCreateResponse);

    // Bidirectional streaming (both sides stream)
    rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message GetUserRequest {
    int64 user_id = 1;
}
```

**Protobuf wire encoding (why it's small):**

```
JSON:  {"id": 42, "name": "Alice", "status": "ACTIVE"}
       → 46 bytes, text, includes field names

Protobuf binary encoding:
  Field 1 (id=42):      \x08\x2A  (2 bytes)
  Field 2 (name=Alice): \x12\x05Alice (7 bytes)
  Field 5 (status=1):   \x28\x01  (2 bytes)
  Total: ~11 bytes
  
  Encoding: (field_number << 3) | wire_type
  Wire types: 0=varint, 1=64-bit, 2=length-delimited,
              5=32-bit
  Varint: 42 encodes as 1 byte (< 128), 1000 as 2 bytes
  → Unknown fields are preserved (forward compatibility)
  → Missing fields use default values (0 for int, "" for string)
```

---

### ⚙️ gRPC on HTTP/2

```
gRPC maps to HTTP/2 naturally:
  - Each RPC = 1 HTTP/2 stream
  - Request headers: :method=POST, content-type=application/grpc
  - Request body: 5-byte message framing + protobuf payload
  - Response headers: :status=200
  - Response trailers: grpc-status=0, grpc-message=""
  - Multiplexing: 1000 concurrent RPCs on 1 TCP connection

gRPC message framing (5-byte header + protobuf):
  Byte 0:    Compressed flag (0=not compressed, 1=compressed)
  Bytes 1-4: Message length (big-endian uint32)
  Bytes 5+:  Protobuf-encoded message

HTTP/2 + gRPC frame flow:
  Client → Server:
    HEADERS (stream 1): :method POST, content-type grpc
    DATA (stream 1): [0][0][0][0][11] + protobuf bytes
    DATA (stream 1): END_STREAM flag

  Server → Client:
    HEADERS (stream 1): :status 200
    DATA (stream 1): [0][0][0][0][22] + protobuf response
    TRAILERS (stream 1): grpc-status=0
```

---

### ⚙️ Generated Code: Java Example

```bash
# Generate Java code from proto
protoc --java_out=src/main/java \
       --grpc-java_out=src/main/java \
       src/main/proto/user.proto
```

```java
// Server-side implementation (generated stub + your logic)
public class UserServiceImpl
    extends UserServiceGrpc.UserServiceImplBase {

    @Override
    public void getUser(
        GetUserRequest request,
        StreamObserver<User> responseObserver) {

        long userId = request.getUserId();
        // Fetch from DB
        Optional<UserEntity> entity = userRepo.findById(userId);

        if (entity.isEmpty()) {
            responseObserver.onError(
                Status.NOT_FOUND
                    .withDescription("User " + userId + " not found")
                    .asRuntimeException()
            );
            return;
        }

        User user = User.newBuilder()
            .setId(entity.get().getId())
            .setName(entity.get().getName())
            .setEmail(entity.get().getEmail())
            .setStatus(UserStatus.USER_STATUS_ACTIVE)
            .build();

        responseObserver.onNext(user);
        responseObserver.onCompleted();
    }

    // Server-streaming RPC
    @Override
    public void listUsers(
        ListUsersRequest request,
        StreamObserver<User> responseObserver) {

        // Stream users to client as they're fetched
        userRepo.findAll().forEach(entity -> {
            User user = toProto(entity);
            responseObserver.onNext(user);  // send one
        });
        responseObserver.onCompleted();  // done streaming
    }
}

// Start the server
Server server = ServerBuilder.forPort(50051)
    .addService(new UserServiceImpl())
    .build()
    .start();
```

```java
// Client-side (generated stub)
ManagedChannel channel = ManagedChannelBuilder
    .forAddress("user-service.svc.cluster.local", 50051)
    .usePlaintext()  // no TLS (internal service mesh)
    .build();

UserServiceGrpc.UserServiceBlockingStub stub =
    UserServiceGrpc.newBlockingStub(channel);

// Unary call
User user = stub.getUser(
    GetUserRequest.newBuilder().setUserId(42).build()
);

// Streaming call
Iterator<User> users = stub.listUsers(
    ListUsersRequest.newBuilder().setLimit(100).build()
);
while (users.hasNext()) {
    process(users.next());
}
```

---

### ⚙️ Wrong vs Right: gRPC Error Handling

```java
// BAD: throwing Java exceptions directly
public void getUser(GetUserRequest req, StreamObserver<User> obs) {
    User user = db.findUser(req.getUserId());
    if (user == null) {
        throw new RuntimeException("Not found");
        // gRPC runtime catches this → sends INTERNAL status
        // Client sees "INTERNAL: Not found" - not useful!
    }
    obs.onNext(user);
    obs.onCompleted();
}

// GOOD: use gRPC Status codes explicitly
public void getUser(GetUserRequest req, StreamObserver<User> obs) {
    try {
        User user = db.findUser(req.getUserId());
        if (user == null) {
            obs.onError(
                Status.NOT_FOUND
                    .withDescription("User " + req.getUserId()
                        + " not found")
                    .asRuntimeException()
            );
            return;
        }
        obs.onNext(user);
        obs.onCompleted();
    } catch (DatabaseException e) {
        obs.onError(
            Status.UNAVAILABLE
                .withDescription("Database unavailable")
                .withCause(e)
                .asRuntimeException()
        );
    }
}

// gRPC Status Codes (know these):
// OK(0)            = success
// CANCELLED(1)     = client cancelled
// UNKNOWN(2)       = unexpected error
// INVALID_ARGUMENT(3) = bad request data
// NOT_FOUND(5)     = resource doesn't exist
// ALREADY_EXISTS(6)= create conflict
// PERMISSION_DENIED(7) = authorization failure
// RESOURCE_EXHAUSTED(8) = rate limited / quota
// UNAVAILABLE(14)  = service temporarily down (retry!)
// DEADLINE_EXCEEDED(4) = timeout hit
```

---

### ⚙️ Deadlines and Cancellation

```java
// gRPC deadlines propagate through the call chain
// BAD: no deadline (blocks forever on downstream failure)
User user = stub.getUser(request);

// GOOD: always set deadline
User user = stub
    .withDeadlineAfter(500, TimeUnit.MILLISECONDS)
    .getUser(request);
// Throws StatusRuntimeException with DEADLINE_EXCEEDED if > 500ms

// Deadline propagation across services:
// Service A → deadline 2s → Service B → passes remaining deadline
// If A's deadline is 2s and call to B takes 1.8s, B has
// only 0.2s to respond to any downstream calls it makes
// This prevents cascading slow calls from causing timeouts
// at the root without surfacing in intermediate services

// Server: check if client has cancelled
public void longRunningRpc(
    Request request,
    StreamObserver<Response> obs) {

    Context ctx = Context.current();
    for (WorkItem item : getWorkItems()) {
        if (ctx.isCancelled()) {
            // Client gave up, stop working
            obs.onError(
                Status.CANCELLED.asRuntimeException());
            return;
        }
        process(item);
    }
    obs.onNext(buildResponse());
    obs.onCompleted();
}
```

---

### ⚙️ Diagnosing gRPC in Production

```bash
# gRPC status codes in logs
# UNAVAILABLE = service down or network partition
# DEADLINE_EXCEEDED = timeout (check latency percentiles)
# RESOURCE_EXHAUSTED = rate limited
# INTERNAL = server threw unexpected exception (bug!)

# Test gRPC with grpcurl (like curl for gRPC)
grpcurl -plaintext localhost:50051 list
# Lists available services and methods

grpcurl -plaintext -d '{"user_id": 42}' \
  localhost:50051 com.example.UserService/GetUser
# Returns JSON representation of protobuf response

# Check gRPC reflection is enabled (required for grpcurl)
# Server: ServerBuilder.addService(ProtoReflectionService.newInstance())

# Monitor gRPC metrics (Prometheus via micrometer):
# grpc.server.calls.seconds (call latency histogram)
# grpc.server.calls.total (counter by status code)

# High DEADLINE_EXCEEDED rate:
# Check P99 latency: grpc.server.calls.seconds{quantile="0.99"}
# If P99 > deadline: the service is too slow
# If P99 < deadline: client deadline is too aggressive
```

---

### 📐 Scale Considerations

```
Per-connection overhead:
  HTTP/2 connection: 1 TCP connection, 1-10 streams active
  gRPC channel: manages HTTP/2 connection + reconnect
  1 gRPC channel handles 100+ concurrent RPCs

Connection pool sizing:
  Default: 1 channel → 1 TCP connection
  For high throughput: use channel pool
    ChannelPool size = roundRobinSize
    Each channel has its own congestion window
    → better throughput under high RPC concurrency

At 100K RPS (microservices):
  Service mesh (Istio/Envoy): proxies each call
  Each proxy: ~0.5ms added latency, TLS overhead
  Solution: mTLS via service mesh certificates
            gRPC keepalive to reuse connections

gRPC vs REST benchmark (industry observed):
  Latency: gRPC ~50% faster (no JSON parsing, HTTP/2)
  Payload: gRPC 3-10x smaller (protobuf vs JSON)
  CPU: gRPC uses less CPU per request (binary codec)
  BUT: JSON is human-readable, gRPC needs tooling
```

---

### 🧭 Decision Guide

```
gRPC vs REST:
  Use gRPC for:
  - Internal service-to-service communication
  - Performance-critical paths (ML inference, trading)
  - Multi-language teams (one proto = all languages)
  - Streaming RPCs (real-time data feeds)
  
  Use REST for:
  - Public APIs (browser native, curl-friendly)
  - Simple CRUD with few consumers
  - Teams that don't want protobuf tooling
  - When HTTP caching matters (REST is cacheable)

gRPC vs WebSocket:
  gRPC streaming: structured, typed, generated code
  WebSocket: raw bytes/JSON, manual protocol design
  → Use gRPC streaming for service-to-service
  → Use WebSocket for browser real-time UI

Interview one-liner:
  "gRPC uses HTTP/2 for transport and Protocol Buffers for
  serialization. It generates type-safe stubs in 10+
  languages from a .proto schema. Benefits: 5-10x smaller
  payload vs JSON, compile-time type safety, 4 RPC types
  (unary + 3 streaming). Limitation: binary format is not
  browser-native, requires proxy (gRPC-Web) for browsers.
  Always set deadlines and use Status codes, not exceptions."
```