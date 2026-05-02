---
layout: default
title: "gRPC Streaming"
parent: "HTTP & APIs"
nav_order: 224
permalink: /http-apis/grpc-streaming/
number: "0224"
category: HTTP & APIs
difficulty: ★★★
depends_on: gRPC, Protocol Buffers, HTTP/2, Reactive Programming
used_by: Real-time Data Pipelines, Microservices, Service Mesh
related: WebSocket, GraphQL Subscriptions, Server-Sent Events
tags:
  - api
  - grpc
  - streaming
  - http2
  - realtime
  - advanced
---

# 224 — gRPC Streaming

⚡ TL;DR — gRPC Streaming extends standard gRPC request/response with three streaming patterns: server streaming (server sends multiple responses), client streaming (client sends multiple requests), and bidirectional streaming (both sides send concurrently) — all over a single multiplexed HTTP/2 connection.

┌──────────────────────────────────────────────────────────────────────────────┐
│ #224 │ Category: HTTP & APIs │ Difficulty: ★★★ │
├──────────────┼────────────────────────────────────────┼────────────────────┤
│ Depends on: │ gRPC, Protocol Buffers, HTTP/2, │ │
│ │ Reactive Programming │ │
│ Used by: │ Real-time Data Pipelines, │ │
│ │ Microservices, Service Mesh │ │
│ Related: │ WebSocket, GraphQL Subscriptions, │ │
│ │ Server-Sent Events │ │
└──────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A client needs to upload 1 million sensor readings to a data ingestion service.
Without streaming, option A: one giant request with 1M readings = huge memory
allocation on both sides, long time to first byte on the server. Option B:
1M separate unary gRPC calls = 1M HTTP/2 streams, 1M serializations, enormous
overhead. Neither is practical.

Similarly, a service needs to deliver a live feed of events to a client —
for example, a log tail, a stock ticker, or game state updates. Without
server streaming, the client must poll. Polling wastes connections and
adds latency. REST doesn't have built-in streaming semantics.

**THE BREAKING POINT:**
A real-time map service needs to continuously receive a vehicle's GPS coordinates
(client → server) while simultaneously pushing traffic updates to the client
(server → client). Two unary endpoints, two WebSocket connections, manual
coordination — complex and brittle. What's needed is a single bidirectional
channel where both sides can independently stream data.

**THE INVENTION MOMENT:**
HTTP/2's multiplexed streams are the foundation. gRPC Streaming builds on top:
a single HTTP/2 stream carries a sequence of length-prefixed protobuf messages
in either direction. The gRPC protocol defines initiation handshake, message
framing within the stream, flow control (via HTTP/2), and graceful termination.
All four patterns (unary + 3 streaming) use the exact same wire format — the
difference is just whether one or many messages are sent on either side.

---

### 📘 Textbook Definition

**gRPC Streaming** is the set of RPC patterns in gRPC that allow one or both
sides of a call to send a sequence of messages over a single HTTP/2 stream.
There are four patterns total:

1. **Unary**: single request → single response (standard gRPC)
2. **Server Streaming**: single request → stream of responses
3. **Client Streaming**: stream of requests → single response
4. **Bidirectional Streaming**: stream of requests ↔ stream of responses, both independently

Defined in `.proto` service blocks using the `stream` keyword. On the server side,
streaming RPCs receive a `StreamObserver` (Java) allowing `onNext()`, `onError()`,
and `onCompleted()` calls. Messages are framed with a 5-byte header within the
HTTP/2 DATA frames, allowing the gRPC layer to delineate individual messages.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
gRPC streaming lets you send a sequence of messages back and forth over one connection — server push, client upload, or full two-way conversation — all with the same typed efficiency as regular gRPC.

**One analogy:**

> Unary gRPC is a single text message exchange. gRPC streaming patterns are:
>
> - Server streaming: you ask a question, they send a long reply word by word
> - Client streaming: you dictate a long message one word at a time, they reply once
> - Bidirectional: a real-time phone call — both speaking and listening simultaneously
>
> All happen over gRPC's "phone network" (HTTP/2) — highly efficient, typed, and
> not needing a new connection for each exchange.

**One insight:**
The `stream` keyword in a `.proto` file is deceptively simple — one word that
completely changes the execution model. `rpc GetData (Request) returns (Response)`
is a function call. `rpc StreamData (Request) returns (stream Response)` is a
channel. The generated code changes from blocking method calls to observer callbacks.
The deployment model changes — server must now handle open HTTP/2 streams lasting
minutes or hours, not milliseconds.

---

### 🔩 First Principles Explanation

**PROTO DEFINITION SYNTAX:**

```protobuf
service DataService {
  // Unary
  rpc GetItem (GetItemRequest) returns (Item);

  // Server streaming: client sends once, server streams N responses
  rpc WatchItems (WatchRequest) returns (stream Item);

  // Client streaming: client streams N requests, server responds once
  rpc UploadReadings (stream SensorReading) returns (UploadSummary);

  // Bidirectional: both stream independently
  rpc Chat (stream ChatMessage) returns (stream ChatMessage);
}
```

**EXECUTION MODELS:**

```
UNARY:
  Client: send req → wait → receive resp
  Server: receive req → process → send resp → done

SERVER STREAMING:
  Client: send req → read until stream closes
  Server: receive req → send msg, send msg, ... → complete()
  Use case: live feeds, log tailing, large dataset downloads

CLIENT STREAMING:
  Client: send msg, send msg, ... → complete() → wait for resp
  Server: read until stream closes → process all → send resp
  Use case: bulk upload, aggregation of inputs

BIDIRECTIONAL:
  Client ↔ Server: both sides can send/receive independently
  Neither side waits for the other to "take a turn"
  Use case: chat, real-time game state, GPS tracking + updates
```

**HTTP/2 MESSAGE FRAMING:**
Within an HTTP/2 DATA frame, gRPC messages are prefixed with 5 bytes:

```
[compression flag: 1 byte] [message length: 4 bytes] [serialized protobuf]
```

This framing allows multiple gRPC messages within a single HTTP/2 DATA frame,
and allows the receiver to reconstruct message boundaries.

**THE TRADE-OFFS:**

- Gain: eliminates polling and repeated connection setup for real-time data.
- Cost: long-lived streams require connection management; server must handle streams lasting minutes/hours.
- Gain: same binary efficiency as unary gRPC for each individual message.
- Cost: bidirectional streaming is complex to implement correctly (ordering, error handling, backpressure).
- Gain: single HTTP/2 connection for both directions in bidirectional streaming.
- Cost: HTTP/2 head-of-line blocking (at TCP level) can affect multiple streams on same connection.

---

### 🧪 Thought Experiment

**SETUP:**
A financial data service delivers real-time stock price updates to client dashboards.
500,000 clients each subscribe to 10 stock symbols. Prices update 100 times/second per symbol.

**POLLING APPROACH:**

```
Requests/second = 500,000 clients × 10 symbols × (1 req / 1 second) = 5,000,000 req/s
Each unary gRPC call: new HTTP/2 stream per call (though reusing TCP connection)
Server must handle: 5,000,000 stream setups + teardowns per second
Memory: manageable (short-lived connections)
Latency: up to 1 second (polling interval)
```

**SERVER STREAMING APPROACH:**

```
Streams: 500,000 clients × 10 symbols = 5,000,000 concurrent open HTTP/2 streams
Stream setup: once per subscription (when client connects)
Server push: when price changes, push to relevant stream
Memory: 5,000,000 stream objects × ~1KB state = ~5GB RAM
Latency: milliseconds (immediate push)
```

**THE INSIGHT:**
Server streaming shifts cost from connection churn (polling) to connection
state (open streams). Which is better depends on update frequency vs subscriber
count. For 100 updates/second, streaming's latency and server-load advantages
dominate. The hard constraint: 5M open streams requires careful server-side
resource management and connection limiting. This is not a design you arrive at
accidentally — you must actively plan for stream lifecycle and resource limits.

---

### 🧠 Mental Model / Analogy

> Unary gRPC = email: you send one message, wait for one reply.
> Server streaming = a radio broadcast: you tune in once, the station
> plays continuously until you change the channel.
> Client streaming = a dictation to a secretary: you speak continuously,
> they take notes, give you one summary at the end.
> Bidirectional streaming = a phone call: both parties talk and listen
> simultaneously, independently, until someone hangs up.

All of these feel like the same "gRPC connection" — but the lifecycle,
error handling, and resource consumption differ dramatically.

- "Tune in" → client sends request, opens stream
- "Station plays" → server calls onNext() for each event
- "Change channel" → client or server calls complete() or cancel()
- "Radio station off air" → server calls onCompleted()
- "Static noise" → server calls onError()

**Where this breaks down:** Unlike a phone call, bidirectional gRPC streams have
no "natural" synchronization — both sides are fully independent. This means you
can have the client still sending messages to a server that has already called
`onCompleted()`. The protocol requires half-close semantics: one side can complete
without requiring the other to immediately close.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Normally, gRPC sends one request and gets one answer. Streaming means you can
send many messages back and forth over the same connection — like a live chat
instead of single emails. The server can keep sending updates, or the client can
keep sending data, while they're both connected.

**Level 2 — How to use it (junior developer):**
Add `stream` keyword in `.proto` to the input, output, or both. Implement the
server using `StreamObserver<ResponseType>`: call `onNext()` to send a message,
`onCompleted()` when done, `onError()` on failure. The client receives responses
via its own `StreamObserver`. For server streaming, client calls the method
and passes a response observer. For client streaming, the method returns a
request observer — the client calls `onNext()` to send messages.

**Level 3 — How it works (mid-level engineer):**
Each gRPC streaming call operates on a single HTTP/2 stream. The HTTP/2 stream
provides bidirectional DATA frames, END_STREAM flags for termination, and RST_STREAM
for immediate cancellation. gRPC adds its own framing within DATA frames for
message delineation (5-byte prefix). Flow control operates at two levels: HTTP/2
window-based flow control (auto-managed, prevents receiver from being overwhelmed)
and application-level flow control (if the consumer can't process fast enough,
you need explicit backpressure — gRPC-java uses `ServerCallStreamObserver.isReady()`
to check if the write buffer is full before calling `onNext()`). Context cancellation
propagates: if the client cancels (drops connection, `Context.cancel()`), the server-side
stream is cancelled and subsequent `onNext()` calls throw `StatusRuntimeException`.

**Level 4 — Why it was designed this way (senior/staff):**
gRPC streaming's use of HTTP/2 streams (rather than WebSocket or custom transport)
was motivated by ecosystem compatibility: HTTP/2 works through load balancers, proxies,
and service meshes that understand HTTP semantics. WebSocket is not proxy-aware in
the same way. However, this choice created gRPC-Web's proxy requirement (browsers
can't access HTTP/2 trailers) and introduced the TCP head-of-line blocking issue:
all gRPC streams on a single HTTP/2 connection share one TCP connection, so TCP
packet loss causes ALL streams to stall (not just the affected one). HTTP/3 (QUIC)
eliminates this by providing true stream-level independence at the transport layer —
gRPC over HTTP/3 is increasingly practical. The bidirectional streaming pattern
reveals a subtle design question: should messages be ordered between client and
server? gRPC provides no ordering guarantee between the two streams — messages
arriving at the server from the client may have been sent before or after server
messages the client received. Application-level sequencing is the developer's
responsibility.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────────┐
│           SERVER STREAMING FLOW                              │
├──────────────────────────────────────────────────────────────┤
│  Client → HTTP/2 HEADERS frame:                             │
│    :method POST, :path /DataService/WatchItems              │
│    content-type: application/grpc                           │
│    + gRPC-framed protobuf request body                     │
│                ↓                                            │
│  Server → HTTP/2 DATA frame (message 1):                    │
│    [0x00][len][protobuf Item 1 bytes]                       │
│  Server → HTTP/2 DATA frame (message 2):                    │
│    [0x00][len][protobuf Item 2 bytes]                       │
│  ... (N messages)                                           │
│  Server → HTTP/2 HEADERS frame (trailers, END_STREAM):      │
│    grpc-status: 0                                           │
│    grpc-message: (empty)                                    │
│  Stream closed                                              │
│                ↓                                            │
│  Client ResponseObserver.onCompleted() called               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│           BIDIRECTIONAL FLOW                                 │
├──────────────────────────────────────────────────────────────┤
│  Client → SERVER: stream of messages (independently)        │
│  Server → CLIENT: stream of messages (independently)        │
│  Both streams run over SAME HTTP/2 stream                   │
│  Either side can call END_STREAM without requiring other    │
│  "Half close": client sends END_STREAM → server reads EOF   │
│   but can continue sending until server also END_STREAMs    │
└──────────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
proto definition with 'stream' keyword
       ↓ protoc generates
StreamObserver-based Java stubs
       ↓
Server implements onNext/onCompleted/onError handlers
       ↓ At runtime:
Client opens HTTP/2 stream
Client sends request (or stream of requests)
Server processes + sends stream of responses
       ↓ Lifecycle:
Client can cancel: RST_STREAM → server Context cancelled
Server completes: HEADERS(trailers+END_STREAM) → client onCompleted
Server errors: HEADERS(grpc-status != 0) → client onError
```

---

### 💻 Code Example

```protobuf
// streaming.proto
syntax = "proto3";
package com.example.streaming;

service LogService {
  // Server streaming: subscribe to log events
  rpc TailLogs (TailLogsRequest) returns (stream LogEntry);

  // Client streaming: upload batch of metrics
  rpc UploadMetrics (stream MetricPoint) returns (UploadSummary);

  // Bidirectional: live GPS tracking with traffic updates
  rpc TrackVehicle (stream GpsCoordinate) returns (stream TrafficUpdate);
}

message TailLogsRequest { string service_name = 1; }
message LogEntry { string message = 1; int64 timestamp = 2; }
message MetricPoint { string name = 1; double value = 2; int64 ts = 3; }
message UploadSummary { int32 processed = 1; int32 errors = 2; }
message GpsCoordinate { double lat = 1; double lng = 2; int64 ts = 3; }
message TrafficUpdate { string segment = 1; int32 delay_seconds = 2; }
```

```java
// Server: server streaming implementation
@GrpcService
public class LogServiceImpl extends LogServiceGrpc.LogServiceImplBase {

    @Autowired private LogEventPublisher logPublisher;

    @Override
    public void tailLogs(TailLogsRequest request,
                         StreamObserver<LogEntry> responseObserver) {
        // ServerCallStreamObserver gives access to flow control
        ServerCallStreamObserver<LogEntry> serverObserver =
            (ServerCallStreamObserver<LogEntry>) responseObserver;

        // Register cancellation handler — MUST clean up resources
        serverObserver.setOnCancelHandler(() -> {
            log.info("Client cancelled log stream for: {}",
                request.getServiceName());
            // Resource cleanup happens here
        });

        // Subscribe to log events and stream to client
        Disposable subscription = logPublisher
            .getLogStream(request.getServiceName())
            .subscribe(
                logEntry -> {
                    // Only send if client is still connected and ready
                    if (!serverObserver.isCancelled()) {
                        if (serverObserver.isReady()) {
                            serverObserver.onNext(logEntry);
                        }
                        // If not ready: backpressure — drop or buffer
                    }
                },
                error -> serverObserver.onError(
                    Status.INTERNAL
                        .withDescription(error.getMessage())
                        .asRuntimeException()),
                serverObserver::onCompleted);
    }
}
```

```java
// Server: bidirectional streaming
@Override
public StreamObserver<GpsCoordinate> trackVehicle(
        StreamObserver<TrafficUpdate> responseObserver) {

    // Return the observer that handles incoming client messages
    return new StreamObserver<GpsCoordinate>() {
        @Override
        public void onNext(GpsCoordinate coordinate) {
            // Process each GPS coordinate from client
            trafficService.getUpdatesForLocation(
                    coordinate.getLat(), coordinate.getLng())
                .forEach(update -> {
                    if (!((ServerCallStreamObserver<TrafficUpdate>)
                            responseObserver).isCancelled()) {
                        responseObserver.onNext(update); // push traffic update
                    }
                });
        }

        @Override
        public void onError(Throwable t) {
            log.error("Client stream error", t);
            // Clean up resources
        }

        @Override
        public void onCompleted() {
            responseObserver.onCompleted(); // close response stream too
        }
    };
}
```

```java
// Client: consuming server streaming
ManagedChannel channel = ManagedChannelBuilder
    .forAddress("log-service", 9090)
    .usePlaintext()
    .build();

LogServiceGrpc.LogServiceStub asyncStub = LogServiceGrpc.newStub(channel);

asyncStub.tailLogs(
    TailLogsRequest.newBuilder().setServiceName("payment-service").build(),
    new StreamObserver<LogEntry>() {
        @Override
        public void onNext(LogEntry entry) {
            System.out.println("[" + entry.getTimestamp() + "] " + entry.getMessage());
        }
        @Override
        public void onError(Throwable t) {
            log.error("Stream error", t); // Handle reconnect logic here
        }
        @Override
        public void onCompleted() {
            log.info("Log stream ended");
        }
    });
```

---

### ⚖️ Comparison Table

| Pattern              | Use Case                        | Server Overhead               | Latency  | Complexity |
| -------------------- | ------------------------------- | ----------------------------- | -------- | ---------- |
| **Unary**            | CRUD, single queries            | Low                           | Low      | Low        |
| **Server Streaming** | Feeds, subscriptions, downloads | Medium (open streams)         | Very Low | Medium     |
| **Client Streaming** | Bulk upload, sensor data        | Low (until final response)    | Low      | Medium     |
| **Bidirectional**    | Chat, real-time collab, GPS     | High (open streams both ways) | Very Low | High       |

**vs WebSocket:**

- gRPC streaming: typed, binary, generated code, connects to service mesh/proxy
- WebSocket: untyped by default, text/binary, manual framing, direct browser support

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                           |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bidirectional streaming means request/response in alternation | Both streams are fully independent — server can send 100 messages before client sends its first                                                   |
| Server streaming is like WebSocket                            | gRPC server streaming is unidirectional (server → client) after the initial request; WebSocket is full duplex from the start                      |
| Cancelling a streaming call is automatic                      | Client cancellation must be explicitly handled server-side: check `isCancelled()` or register `setOnCancelHandler()` to avoid zombie streams      |
| gRPC streaming works through all HTTP proxies                 | HTTP/1.1 proxies don't support HTTP/2 streaming; require HTTP/2-aware proxies (Envoy, nginx with http2 enabled)                                   |
| Flow control is automatic                                     | HTTP/2 window flow control is automatic; application-level flow control (`isReady()`) must be manually checked to prevent overwhelming the client |

---

### 🚨 Failure Modes & Diagnosis

**Zombie Streaming — Server Holds Resources After Client Disconnects**

Symptom:
Memory grows over 48 hours. Heap dump shows thousands of `StreamObserver` objects,
associated subscriptions, and database connections that should have been released.
The objects correspond to clients that disconnected hours ago.

Root Cause:
Server-side streaming code doesn't check `isCancelled()` or register a cancel handler.
When clients disconnect, the gRPC framework marks the stream as cancelled but the
application code continues calling `onNext()` (silently dropped) and holding resources.

Diagnostic Command / Tool:

```java
// Enable gRPC server metrics — monitor active streams:
// With Micrometer + gRPC:
// grpc.server.calls.started_total
// grpc.server.calls.completed_total
// Active = started - completed

// If active streams grows without bound: zombie stream leak

// Heap dump analysis:
// jmap -dump:format=b,file=heap.hprof <pid>
// Look for: ServerCallImpl, io.grpc.stub.ServerCallStreamObserver
```

Fix:
Register `setOnCancelHandler()` in every server streaming method.
Release subscriptions, database connections, and other resources in the handler.
Periodically check `isCancelled()` in streaming loops.

Prevention:
Every server streaming implementation must have explicit cancel handling.
Code review checklist: does every streaming RPC have an `onCancelHandler`?

---

**TCP Head-of-Line Blocking on Busy Server**

Symptom:
Under load, a fast server streaming call (small messages) has high P99 latency
even though server processing is fast. Affects all streaming calls — not just the
one sending large payloads.

Root Cause:
Multiple gRPC connections (or many streams on one connection) share one TCP
connection. A large client-streaming upload using most of the TCP window causes
ALL other streams on the connection to pause — TCP head-of-line blocking.

Diagnostic Command / Tool:

```bash
# Check for TCP retransmits and stalls during gRPC calls:
netstat -s | grep -i retransmit
# Or with ss:
ss -tin dst <grpc-server-ip>
# HIGH retransmit count = TCP congestion affecting all streams

# Solution: use separate channels for high-volume vs low-latency streams
# Or: enable HTTP/3 (QUIC) which eliminates TCP HoL blocking
```

Fix:
Use separate `ManagedChannel` instances for high-volume streaming vs
latency-sensitive unary calls. Each channel creates its own TCP connection.

Prevention:
Profile gRPC channel usage patterns. Don't mix large-payload streaming
with latency-sensitive unary calls on the same channel.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `gRPC` — must understand unary gRPC, proto files, stub generation before streaming
- `Protocol Buffers` — streaming messages are still protobuf-serialized
- `HTTP/2` — streaming is built on HTTP/2 streams; must understand multiplexing and flow control

**Builds On This (learn these next):**

- `Real-time Data Pipelines` — server streaming is a foundation for real-time data delivery
- `Service Mesh` — Envoy and Istio provide observability and traffic management for gRPC streaming
- `Reactive Programming` — bidirectional streaming naturally maps to reactive stream primitives

**Alternatives / Comparisons:**

- `WebSocket` — unstructured bidirectional streaming; browser-native but untyped
- `GraphQL Subscriptions` — typed real-time subscriptions built on WebSocket; for client-facing APIs
- `Server-Sent Events` — simple unidirectional server push; HTTP/1.1 compatible, simpler than gRPC streaming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 3 gRPC patterns beyond unary: server,    │
│              │ client, and bidirectional message streams │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Polling is wasteful; bulk upload is       │
│ SOLVES       │ memory-intensive; real-time needs push    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ `stream` keyword changes execution model │
│              │ from function call to open channel       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Server: live feeds, tailing, subscriptions│
│              │ Client: bulk upload, metrics ingestion   │
│              │ Bidi: chat, GPS, collaborative editing   │
├──────────────┼───────────────────────────────────────────┤
│ WATCH OUT    │ Cancel handlers required — zombie streams │
│              │ Flow control: check isReady() before push │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Low latency + efficiency vs long-lived   │
│              │ stream management complexity             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "gRPC channels that stay open"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Service Mesh → Reactive Programming      │
│              │ → WebSocket comparison                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A bidirectional streaming RPC serves a real-time collaborative document editor.
The client sends keystroke events; the server sends back merged document state.
At 50 active users typing simultaneously, each sending 5 keystrokes/second, how
do you design the server-side data model for conflict resolution, ordering guarantees
for each client's stream, and the backpressure strategy when one client's connection
is slow but others should not be affected?

**Q2.** A server streaming RPC delivers 1 billion financial transactions to a
compliance system. The stream takes 4 hours to complete. Design the error recovery
strategy for: (a) server restart mid-stream, (b) client crash mid-stream,
(c) network partition lasting 30 seconds. What checkpointing mechanism allows
the stream to resume rather than restart from the beginning?
