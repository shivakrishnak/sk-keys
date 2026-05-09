---
id: SYD-036
title: Push vs Pull Architecture
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-033, SYD-035
used_by: SYD-037, SYD-047
related: SYD-035, SYD-037, SYD-047
tags:
  - architecture
  - distributed
  - pattern
  - intermediate
  - networking
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /syd/push-vs-pull-architecture/
---

# SYD-036 - Push vs Pull Architecture

⚡ TL;DR - A fundamental data delivery pattern: push proactively sends data to consumers when available; pull has consumers request data when ready - each optimises for different latency, coupling, and load characteristics.

| SYD-036         | Category: System Design     | Difficulty: ★★☆ |
| :-------------- | :-------------------------- | :-------------- |
| **Depends on:** | SYD-033, SYD-035            |                 |
| **Used by:**    | SYD-037, SYD-047            |                 |
| **Related:**    | SYD-035, SYD-037, SYD-047   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to update a mobile client when new data is available. You have two options: clients poll your API every 30 seconds (wasting 99.9% of API calls if data rarely changes), or you try to send updates directly to clients (requiring persistent connections, server tracking of connected clients). Neither feels right. Without a clear push/pull framework, you pick one without understanding the trade-offs and regret it at scale.

**THE BREAKING POINT:**
Push and pull have opposite strengths. Push minimises latency (instant delivery) but requires server-side state (track all consumers) and creates backpressure problems. Pull is stateless and backpressure-friendly but wastes bandwidth on empty polls. The wrong choice for your use case produces either severe latency problems or severe infrastructure waste.

**THE INVENTION MOMENT:**
Networking protocols formalised push vs pull in the 1990s. RSS (Really Simple Syndication, 1999) was a pull protocol for news aggregation - clients poll for updates. XMPP (Jabber, 1999) was a push protocol for instant messaging - server pushes messages to connected clients. These two protocols embodied the fundamental choice.

**EVOLUTION:**
Modern systems rarely use pure push or pull. HTTP/2 server push (push embedded in pull protocol), WebSockets (bidirectional persistent connection enabling both), Server-Sent Events (server push over HTTP), and long polling (pull that blocks until data available) are all hybrids. Cloud services like FCM/APNs solve mobile push delivery at scale.

---

### 📘 Textbook Definition

**Push architecture:** The server (or data producer) proactively delivers data to consumers when an event occurs. The server maintains a registry of active consumers and initiates delivery. Latency is minimised; server bears the fan-out cost. **Pull architecture:** Consumers query the server (or data source) when they want data. The server is stateless regarding consumers; each consumer controls its own consumption rate. Consumers bear the polling cost; latency is bounded by polling interval. The choice affects: server statefulness, client implementation complexity, network efficiency, and flow control.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Push = server delivers data to you; Pull = you ask the server for data.

**One analogy:**
> News alert app (push) vs newspaper (pull). The app sends you a notification when breaking news happens - server proactively delivers. A newspaper delivers daily at 6am - you consume on a fixed schedule. For breaking news, push is essential; for stable daily updates, pull is efficient.

**One insight:**
Push minimises latency; pull minimises server complexity. Hybrid (long poll, WebSocket) captures benefits of both at the cost of implementation complexity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Push requires server to track consumer state (who is connected, where to deliver) - the server bears fan-out cost.
2. Pull requires consumers to manage their own schedule - the consumer bears polling cost.
3. Push latency = event-to-delivery time (milliseconds to seconds); pull latency = polling interval (seconds to minutes typically).
4. Push creates backpressure challenge: fast producer + slow consumer requires server to buffer or drop.
5. Pull provides natural backpressure: consumer controls consumption rate; producer queue absorbs excess.

**DERIVED DESIGN:**
Choose push for: real-time low-latency requirements, events that are infrequent (notifications), streaming data. Choose pull for: data consumers at variable processing speeds (Kafka consumers), stateless servers preferred, consumer-controlled pacing.

**THE TRADE-OFFS:**
**Push:** Gain: real-time delivery, efficient (no polling waste). Cost: server statefulness, fan-out complexity, backpressure management.
**Pull:** Gain: stateless server, natural backpressure, simple implementation. Cost: polling overhead, latency proportional to interval, wasted bandwidth on empty polls.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Time-critical events genuinely require push; batch processing genuinely benefits from pull pacing.
**Accidental:** Many systems use polling for convenience (easy to implement) when push would provide far better user experience - this is unnecessary latency.

---

### 🧪 Thought Experiment

**SETUP:**
A stock trading platform shows real-time stock prices. Current architecture: clients poll `/api/prices` every 5 seconds.

**WHAT HAPPENS WITH PURE PULL (polling):**
100K active traders × poll every 5 seconds = 20,000 API requests/second. Only 1% of polls return a price change (markets move 1% of the time). 99% of API calls return "no change" - wasted compute. During a market crash, prices update every millisecond - a 5-second poll interval means traders see prices 5 seconds late.

**WHAT HAPPENS WITH PURE PUSH (WebSocket):**
100K traders establish persistent WebSocket connections. Server pushes price updates as they occur - sub-100ms latency. But server must maintain 100K open connections, track all subscribed symbols per connection, and handle disconnections/reconnections. Infrastructure cost: dedicated WebSocket server cluster.

**WHAT HAPPENS WITH HYBRID (long poll):**
Clients request: "give me next update after timestamp T." Server holds the request until a price change occurs, then returns immediately. Simulates push with stateless HTTP. Slightly more latency than WebSocket; much simpler than managing persistent connections.

**THE INSIGHT:**
The right model depends on: event frequency (rare events → pull is wasteful → push better), update latency requirement (strict real-time → push), server connection management capability.

---

### 🧠 Mental Model / Analogy

> Push vs pull is like waiting for a package. Pull: you check your mailbox every hour (polling). Push: the courier rings your doorbell the moment they arrive. Long poll: you sit in the lobby until the courier arrives (blocking pull). WebSocket: you open a phone call with the courier who speaks whenever they have information.

**Mapping:**
- Checking mailbox → polling API
- Courier ringing doorbell → server-sent event or WebSocket push
- Sitting in lobby → long poll (blocking request)
- Open phone call → persistent WebSocket connection
- Mailbox full → consumer queue full (backpressure)

Where this analogy breaks down: real couriers can be rescheduled; server push requires the consumer to be reachable (have a persistent connection or registered endpoint).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Does your app check for updates (pull) or does the server tell you when something changes (push)? Email is mostly pull (you check your inbox). Text messages are push (your phone receives them immediately). For urgent alerts, push matters; for casual updates, pull is fine.

**Level 2 - How to use it (junior developer):**
For a chat application: use WebSockets (push) for real-time message delivery. For a dashboard that shows metrics updated every minute: use polling (pull) every 30 seconds. For notifications: use FCM/APNs (mobile push infrastructure). Rule of thumb: events per minute < 1 and latency < 10s required → use push. Events per minute >> 1 or latency tolerance > 30s → pull is fine.

**Level 3 - How it works (mid-level engineer):**
Push implementations: WebSocket (RFC 6455) - persistent TCP connection, bidirectional, server pushes frames; Server-Sent Events (SSE) - one-way HTTP stream, server sends event stream, browser reconnects automatically; WebPush (RFC 8030) - push to mobile/browser via intermediary (FCM, APNs). Pull implementations: short poll - HTTP request/response cycle; long poll - request held open until data available or timeout.

**Level 4 - Why it was designed this way (senior/staff):**
Push vs pull is ultimately about who bears the coordination burden. In push, the server coordinates delivery to N consumers - it must track their addresses, handle reconnections, manage backpressure. In pull, each consumer independently manages its own read position (e.g., Kafka consumer group offset) - the server is stateless and scales horizontally without coordination. This is why Kafka chose pull: consumer-managed offsets allow arbitrary replay, independent consumer progress, and zero server-side per-consumer state. Push architectures (like traditional message queues - RabbitMQ) are simpler for simple cases but harder to scale and debug at high consumer counts.

**Expert Thinking Cues:**
- "How often does the data actually change? If rarely, push is more efficient; if constantly, pull or streaming."
- "Can consumers be reached directly (mobile apps, browsers with open connections)?"
- "What is the backpressure story: can producers outrun consumers?"
- "Is consumer position tracking required (replay, offset management)?"

---

### ⚙️ How It Works (Mechanism)

```
PULL ARCHITECTURE
═════════════════
Consumer         Server
    │                │
    ├─GET /data──────►│
    │◄──200 (data)───┤
    │  (wait 30s)    │
    ├─GET /data──────►│
    │◄──200 (empty)──┤  ← YOU ARE HERE
    │  (wait 30s)    │
    (repeat forever)

PUSH ARCHITECTURE (WebSocket)
══════════════════════════════
Consumer         Server
    │                │
    ├─WS CONNECT─────►│
    │◄──WS ACK───────┤
    │  (connected)   │
    │   [data event] │
    │◄──WS PUSH──────┤  ← YOU ARE HERE
    │   [data event] │
    │◄──WS PUSH──────┤
    │  (persistent)  │

LONG POLL (hybrid)
══════════════════
Consumer         Server
    │                │
    ├─GET /data──────►│
    │  (held open)   │
    │   [event fires]│
    │◄──200 (data)───┤  immediate response
    ├─GET /data──────►│  next request
    (repeat with each event)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Event occurs on server
    │
    ▼
PUSH: server identifies   ← YOU ARE HERE
registered consumers
    │
    ▼
Deliver to each via
WebSocket/SSE/FCM

OR:

PULL: consumer timer fires
    │
    ▼
Consumer polls server
    │
    ▼
Server returns data (or empty)
```

**FAILURE PATH:**
Push: consumer disconnects → server detects via heartbeat → delivery fails → retry with exponential backoff → no recovery if consumer unable to reconnect (devices offline). Pull: server outage → consumer gets 502/503 → retries with backoff → misses events during outage if server lacks event at-least-once queue.

**WHAT CHANGES AT SCALE:**
Push at scale requires a dedicated real-time infrastructure tier (Socket.io, Centrifugo, Pusher) with sticky session routing (ensure WebSocket connections route to same server) or a pub-sub broker to broadcast pushes across the server cluster. Pull at scale benefits from horizontal scaling of stateless API servers.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Push servers must handle thousands of simultaneous open connections. Node.js, Go, and async Java are better suited for this than thread-per-connection models (Tomcat blocking threads). Each WebSocket connection holds a file descriptor - servers must be configured for high FD limits (`ulimit -n`).

---

### 💻 Code Example

```javascript
// BAD: Short polling - wastes bandwidth
setInterval(async () => {
    const res = await fetch('/api/messages');
    const data = await res.json();
    if (data.length > 0) updateUI(data);
    // Sends request even if no new messages
}, 3000);

// GOOD - Option A: WebSocket push for real-time
const ws = new WebSocket('wss://api.example.com/ws');

ws.onopen = () => {
    ws.send(JSON.stringify({type: 'subscribe',
                            channel: 'messages'}));
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    updateUI(msg);  // Instant delivery, no polling
};

ws.onerror = () => reconnect();  // Handle disconnects

// GOOD - Option B: Server-Sent Events (simpler)
const evtSource = new EventSource(
    '/api/messages/stream');

evtSource.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    updateUI(msg);
};
// Browser auto-reconnects on disconnect
```

**How to test / verify correctness:**
- Latency test: measure time from server event to client receipt - WebSocket should be < 100ms.
- Efficiency test: count API requests per hour for polling vs push - push should be orders of magnitude fewer.
- Reconnection test: disconnect client; verify it reconnects and receives missed events.

---

### ⚖️ Comparison Table

| Model | Latency | Server Complexity | Bandwidth | Best For |
|---|---|---|---|---|
| **Short poll** | High (= interval) | Low (stateless) | Wasteful | Admin dashboards, low-frequency updates |
| **Long poll** | Low | Medium | Efficient | Chat, notifications on HTTP-only |
| **WebSocket** | Very low (<100ms) | High (stateful) | Efficient | Real-time chat, games, trading |
| **SSE** | Low | Medium | Efficient | One-way push (feeds, notifications) |
| **Mobile push (FCM)** | Low | Low (delegates) | Efficient | Mobile notifications |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "WebSockets replace REST" | WebSockets only make sense for ongoing bidirectional streams. REST is still correct for request-response operations. |
| "Push is always better than poll" | For infrequent events with high latency tolerance, polling is simpler and fine. Push complexity is only justified by strict latency requirements. |
| "Long polling is obsolete" | Long polling is still widely used as a fallback when WebSockets are unavailable (corporate proxies, firewalls). |
| "Push eliminates scaling concerns" | Push at scale requires a broker tier to fan out across server nodes. A single server cannot maintain 1M WebSocket connections. |
| "Pull is less reliable" | With proper retry, pull can provide at-least-once delivery; push requires additional reliability guarantees (ack/retry) to be at-least-once. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: WebSocket Connection Exhaustion**
**Symptom:** New clients cannot connect; existing clients get dropped; server memory spikes.
**Root Cause:** Server maintaining too many concurrent WebSocket connections; file descriptor limit hit.
**Diagnostic:**
```bash
# Check open connections
ss -s | grep ESTABLISHED
# Check file descriptor limit
ulimit -n
# Check current FD usage
lsof | wc -l
```
**Fix:** Increase `ulimit -n` to 100K+. Scale WebSocket server horizontally. Use Nginx for connection load balancing.
**Prevention:** Capacity plan: each WebSocket connection uses ~10-50KB RAM. 1M connections = 10-50GB RAM minimum.

**Mode 2: Push Missed Events During Disconnect**
**Symptom:** Client reconnects after network outage; misses all events that occurred while disconnected.
**Root Cause:** Server-side event buffer has TTL; events expired before client reconnected.
**Diagnostic:**
```bash
# Check event buffer retention
redis-cli TTL stream:events
# Compare last client consume time vs event creation time
```
**Fix:** Store events in a durable queue (Kafka, Redis Streams) with retention; on reconnect, replay from last-seen event ID.
**Prevention:** Always implement event replay for push channels; use sequence numbers or event IDs for client resume.

**Mode 3: Poll Rate Too High**
**Symptom:** API server overwhelmed by polling clients; 95%+ of requests return empty responses.
**Root Cause:** Polling interval too short; many clients polling for data that rarely changes.
**Diagnostic:**
```bash
# Check empty response rate
grep "200 {}" /var/log/app.log | wc -l
# vs total requests
grep "GET /api/poll" /var/log/app.log | wc -l
```
**Fix:** Switch to long poll or WebSocket. Alternatively, increase polling interval with adaptive backoff (increase interval when consecutive empty responses).
**Prevention:** Calculate cost/benefit: if expected_updates_per_hour < polls_per_hour * 0.1, polling is wasteful; use push.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-033 - Read-Heavy vs Write-Heavy Design]] - Push and pull are delivery model variants of this classification
- [[SYD-035 - Fan-Out on Write vs Read]] - Social feed specific version of push/pull

**Builds On This (learn these next):**
- [[SYD-037 - Polling vs Webhooks]] - Specific push/pull patterns for server-to-server communication
- [[SYD-047 - Notification System Design]] - Real-world application of push architecture

**Alternatives / Comparisons:**
- [[SYD-037 - Polling vs Webhooks]] - Webhooks as the server-to-server push model

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Data delivery pattern:      ║
║               server delivers (push) vs   ║
║               client requests (pull)      ║
╠══════════════════════════════════════════╣
║ PROBLEM       Wrong model causes latency  ║
║ IT SOLVES     or bandwidth waste          ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   Push = low latency+complex; ║
║               Pull = simple+poll overhead ║
╠══════════════════════════════════════════╣
║ PUSH WHEN     Real-time required <1s;     ║
║               events are infrequent       ║
╠══════════════════════════════════════════╣
║ PULL WHEN     Latency tolerance >30s;     ║
║               consumer sets own pace      ║
╠══════════════════════════════════════════╣
║ TRADE-OFF     Latency vs server           ║
║               statefulness burden         ║
╠══════════════════════════════════════════╣
║ ONE-LINER     Push: instant delivery;     ║
║               Pull: scheduled retrieval   ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-037: Polling/Webhooks   ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Push gives low latency but requires server-side consumer state (connections, registers, fan-out management).
2. Pull is stateless and gives natural backpressure control - consumer never overwhelmed by fast producer.
3. Long poll and WebSocket are hybrids that capture push-like latency with pull-like reconnect simplicity.

**Interview one-liner:**
"Push proactively delivers data when ready (low latency, server manages state); pull has consumers request on their schedule (simple server, polling overhead); hybrids like WebSocket and long polling combine the strengths of both."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Match the delivery model to the update frequency and latency requirement. Push is justified when: (a) data changes frequently enough that polling wastes bandwidth, or (b) latency requirements are strict. Pull is preferred when: (a) consumer pacing matters (avoid overwhelming slow consumers), (b) simplicity is valued, (c) event ordering and replay are required.

**Where else this pattern appears:**
- **Git fetch vs remote hooks:** `git fetch` is pull (you ask for changes); CI/CD webhooks are push (repo notifies CI on push event).
- **Iterator pattern vs observer pattern:** Iterator (pull - consumer calls next()) vs Observer (push - subject notifies observers).
- **Kafka vs RabbitMQ:** Kafka is pull-based (consumers maintain offset); RabbitMQ is push-based (broker delivers to consumers).

---

### 💡 The Surprising Truth

Kafka's choice of pull-based consumption (consumers poll the broker) over push-based delivery (broker pushes to consumers) is the primary reason Kafka scales to millions of consumers without broker state explosion. In a push-based message queue like RabbitMQ, the broker must track each consumer's delivery state, acknowledgements, and redelivery queues. In Kafka, the consumer tracks its own offset - the broker is stateless relative to consumers. This makes Kafka horizontally scalable in a way that push-based brokers cannot match.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A chat application uses WebSockets for message delivery. A user's phone loses network for 2 minutes. When they reconnect, how do you ensure they receive all messages sent during the outage, and how does this requirement change your server architecture?
*Hint:* Think about what state the server needs to maintain to enable replay (message store with per-user high-watermark), and explore how this requirement makes your push server more similar to a pull system in terms of the state it must maintain.

**Q2 (Scale):** Your WebSocket server handles 100K concurrent connections. You need to send a message to all users in a specific geographic region (1M users, 40% currently connected). How do you route the push to the right WebSocket server instances, and what happens to the 60% who are disconnected?
*Hint:* Explore pub-sub brokers (Redis Pub/Sub, Kafka) for cross-server fan-out to connected clients, and the undelivered message store that must be queried when offline users reconnect.

**Q3 (Design Trade-off):** GitHub sends webhook notifications to third-party integrations when a repository is pushed to. A large enterprise customer's webhook endpoint is sometimes slow (5-10 second responses) or down. Should GitHub use push (webhooks) or pull (third party polls GitHub's API) for this integration? What failure modes does each choice create?
*Hint:* Consider what happens when webhook delivery fails (retry queue, back pressure on GitHub's outbound queue), contrast with polling's stateless simplicity (GitHub needs no outbound delivery state), and look at GitHub's actual webhook retry policy.
