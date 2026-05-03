---
layout: default
title: "Container Logging"
parent: "Containers"
nav_order: 852
permalink: /containers/container-logging/
number: "0852"
category: Containers
difficulty: ★★☆
depends_on: Container, Docker, Sidecar Container, Container Orchestration
used_by: Observability & SRE, Kubernetes Architecture, Container Health Check
related: Sidecar Container, Structured Logging, Observability, ELK Stack, Loki
tags:
  - containers
  - docker
  - observability
  - logging
  - intermediate
---

# 852 — Container Logging

⚡ TL;DR — Container logging captures application output from ephemeral containers to durable log storage, using stdout/stderr as the universal interface between application and logging infrastructure.

| #852 | Category: Containers | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Container, Docker, Sidecar Container, Container Orchestration | |
| **Used by:** | Observability & SRE, Kubernetes Architecture, Container Health Check | |
| **Related:** | Sidecar Container, Structured Logging, Observability, ELK Stack, Loki | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Traditional applications write logs to files: `/var/log/app/app.log`. The file persists on disk. When something breaks, you SSH in and `grep` the log file. Containers are ephemeral — when a container restarts or is rescheduled to a different node, its local filesystem is destroyed. A pod crashes at 2 AM, you wake up at 9 AM to investigate, but the pod has restarted — all logs from the crash are gone. On Kubernetes, the pod may have been rescheduled to a different node, and the original node's container logs are inaccessible.

**THE BREAKING POINT:**
Ephemeral container storage + distributed scheduling = log files are unreliable. Any crash loses the logs from that crash. Any reschedule loses the logs from that node. Investigating production incidents becomes impossible without a log collection strategy designed for container environments.

**THE INVENTION MOMENT:**
This is exactly why container logging patterns were developed — a combination of stdout/stderr standardisation, log driver plugins, sidecar log forwarders, and node-level log agents that collect logs from all containers on a node and ship them to durable, centralised log storage regardless of container lifecycle events.

---

### 📘 Textbook Definition

**Container logging** refers to the collection, forwarding, and storage of log output from containerised applications. The canonical approach: applications write logs to **stdout and stderr** (treating the container as the log transport layer), while the container runtime captures this output. In Kubernetes, log access is provided by the kubelet via the `kubectl logs` API, which reads from the node-level log files in `/var/log/pods/`. For durable, cluster-wide log aggregation, **node-level log agents** (Fluentd, Fluent Bit as DaemonSet) or **sidecar log shippers** collect from pod stdout/stderr and forward to centralised log storage (Elasticsearch, Loki, Splunk, Datadog).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Container logging means writing to stdout and letting the infrastructure handle log collection — because containers are too ephemeral to own their own log files.

**One analogy:**
> A hotel guest (container) should not write diary entries on hotel notepads that stay in the room (local filesystem). When the guest checks out (container restarts), the notes are lost. Instead, the guest sends messages to the hotel's central messenger (stdout → log agent), who records everything in the hotel's permanent archive (centralised log storage). The guest never even thinks about logging — they just speak, and the infrastructure records.

**One insight:**
The stdout convention is the most important container logging principle. Writing to stdout is not "unprofessional" or "primitive" — it is the correct interface for a container. It decouples the application from the logging implementation: today you ship to ELK, tomorrow to Loki, the day after to Datadog, and the application never changes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Containers' local filesystems are ephemeral — any data written locally is lost on restart.
2. stdout/stderr are captured by the container runtime and stored on the node (temporarily).
3. Node-level log rotation means even stdout logs are eventually lost — durable storage requires active forwarding.

**DERIVED DESIGN:**

**The log pipeline:**
```
Application
  → writes to stdout/stderr
  → container runtime (Docker/containerd) captures
  → stored as JSON log files on node:
    /var/log/pods/<pod-uid>/<container>/<N>.log
  → kubelet serves via: kubectl logs <pod>
  → log agent (Fluent Bit DaemonSet) reads from node log files
  → enriches with pod metadata (name, namespace, labels)
  → forwards to: Elasticsearch / Loki / Splunk
  → accessible in: Kibana / Grafana / Splunk UI
```

**Three logging architectures:**

**1. Node-level log agent (DaemonSet) — recommended:**
A Fluent Bit or Fluentd pod runs on every node (DaemonSet). It reads container log files from `/var/log/pods/`, parses them, enriches with Kubernetes metadata (pod name, namespace, labels, node), and forwards to storage.
- Pro: no application changes, one agent per node
- Con: brief window of log loss if node fails before forwarding

**2. Sidecar log shipper:**
Each pod has a Fluent Bit/Fluentd sidecar that reads from a shared volume where the app writes logs.
- Pro: per-service log format customisation
- Con: additional container per pod, resource overhead

**3. Application-direct forwarding:**
Application writes directly to log service API (Datadog API, Splunk HEC).
- Pro: guaranteed delivery (no intermediate files)
- Con: application coupled to log service, network calls in app

**Log drivers in Docker:**
Docker supports pluggable log drivers: `json-file` (default — writes to node-local JSON files), `syslog`, `awslogs` (CloudWatch), `gelf` (Graylog), `splunk`, `fluentd` (send directly to Fluentd). Configure with `--log-driver` flag or in `daemon.json`.

**THE TRADE-OFFS:**

**Gain:** stdout/stderr decouples app from log infrastructure. Node-level agents have minimal per-pod overhead.

**Cost:** Brief log loss window if node fails between write and forwarding. Centralized log storage costs money. Need to handle log format parsing (JSON vs plaintext).

---

### 🧪 Thought Experiment

**SETUP:**
A Java Spring Boot API writes logs to a file `/app/logs/app.log` inside the container. A pod crashes.

**WHAT HAPPENS WITH FILE-BASED LOGGING (NO FORWARDING):**
Pod crashes. Container restarts. The previous container's filesystem is discarded — `app.log` is gone. You try `kubectl logs my-pod --previous` — this reads the kubelet's captured stdout, but the app never wrote to stdout. There are no logs from the crash. You have no idea what caused the failure.

**WHAT HAPPENS WITH STDOUT LOGGING + FLUENTBIT DAEMONSET:**
Spring Boot writes logs to stdout (Logback configured with `ConsoleAppender`). The kubelet captures stdout to `/var/log/pods/<uid>/app/<N>.log`. Fluent Bit DaemonSet reads this file in real time and forwards to Elasticsearch. 10 seconds after the INFO and WARN lines, the FATAL exception that caused the crash is ingested into Elasticsearch. Even after the pod restarts, the logs from the crash are in Kibana. `kubectl logs my-pod --previous` also shows the last stdout output from the crashed container.

**THE INSIGHT:**
stdout is the contract between the application and the logging infrastructure. It ensures logs survive container restarts — because they are captured by the runtime and shipped by the infrastructure, not held inside the container's ephemeral filesystem.

---

### 🧠 Mental Model / Analogy

> Container logging with stdout is like a telephone operator intercepting all calls. The application speaks into the phone (stdout). The operator (container runtime) records the conversation. A transcription service (Fluent Bit) reads the recording and files it in a permanent archive (Elasticsearch/Loki). The caller (application) has no idea where their words end up — they just speak. The logging infrastructure handles everything else.

Mapping:
- "Speaking into the phone" → application writes to stdout/stderr
- "Operator recording" → container runtime captures stdout to node log file
- "Transcription service" → Fluent Bit DaemonSet reading node log files
- "Permanent archive" → Elasticsearch / Loki / Splunk
- "Caller doesn't manage storage" → application is decoupled from log storage

Where this analogy breaks down: phone recordings are stored sequentially. Container logs can arrive out of order when multiple containers on a node write simultaneously. Log timestamps and sequence numbers are critical for correct ordering.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Container logging is how your application's output (logs, errors, status messages) gets collected and stored permanently. Instead of writing to a file inside the container (which gets deleted on restart), applications write to the screen (stdout), and infrastructure tools collect and store those messages safely.

**Level 2 — How to use it (junior developer):**
Configure your application to write logs to stdout (System.out in Java, console.log in Node, print in Python). For Java/Spring Boot: configure Logback with `ConsoleAppender`. In Kubernetes, `kubectl logs <pod>` shows recent stdout. Set up a Fluent Bit DaemonSet (or use your Kubernetes distribution's built-in log collection) to forward logs to your log storage. Use structured logging (JSON) for better searchability.

**Level 3 — How it works (mid-level engineer):**
In Kubernetes: containerd writes container stdout/stderr to `/var/log/pods/<pod-uid>/<container-name>/<rotation-index>.log` as JSON-formatted log entries (`{"log":"...","stream":"stdout","time":"..."})`). kubelet manages log rotation (default: 10 files × 10MB = 100MB per container). `kubectl logs` reads from these files via kubelet's log endpoint. Fluent Bit DaemonSet mounts `/var/log/pods/` via hostPath volume, tails the files using inotify, parses the JSON, enriches with Kubernetes metadata from the API server (pod name, namespace, labels), and forwards to the configured output (Loki, Elasticsearch, etc.).

**Level 4 — Why it was designed this way (senior/staff):**
The stdout/stderr convention follows the Unix philosophy: every process should write output to stdout, and the shell/OS decides what to do with it (redirect, pipe, store). Docker and Kubernetes extend this: the container runtime is the "shell" that captures stdout and the logging infrastructure decides what to do with it. This design is correct for immutable, ephemeral containers because it makes the logging mechanism part of the infrastructure rather than part of the application — consistent with the 12-Factor App's log handling principle. The DaemonSet pattern for log collection is preferred over sidecar because it doesn't require application teams to manage a log agent — the platform team owns the DaemonSet and all pods on the cluster automatically benefit. The trade-off (sidecar offers more flexibility, DaemonSet less overhead) makes DaemonSet correct for most enterprise platforms.

---

### ⚙️ How It Works (Mechanism)

**Log flow in Kubernetes:**
```
┌──────────────────────────────────────────────────────────┐
│           Container Log Collection Flow                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Container: app writes to stdout                         │
│       ↓                                                  │
│  containerd: captures stdout via FIFO/pipe               │
│       ↓                                                  │
│  containerd: writes to node file:                        │
│  /var/log/pods/<uid>/<container>/0.log                   │
│  (JSON format: {log:"...", stream:"stdout", time:"..."}) │
│       ↓                                                  │
│  kubelet: rotates logs (max 10 files × 10MB/file)        │
│       ↓                                                  │
│  Fluent Bit (DaemonSet, one per node):                   │
│    → tail /var/log/pods/*/*.log (inotify watch)          │
│    → parse JSON log entries                              │
│    → enrich: add kubernetes.pod_name, namespace, labels  │
│    → forward: HTTP POST to Loki / Elasticsearch          │
│       ↓                                                  │
│  Log storage: indexed, searchable, retained per policy   │
└──────────────────────────────────────────────────────────┘
```

**Docker log driver default (json-file):**
```bash
# Where Docker stores container logs (standard json-file driver)
cat /var/lib/docker/containers/<id>/<id>-json.log
# {"log":"2024-01-01T00:00:00Z INFO Starting server\n",
#  "stream":"stdout","time":"2024-01-01T00:00:00.000Z"}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Application: System.out.println(json-log) → stdout
  → containerd: write to /var/log/pods/... ← YOU ARE HERE
  → kubelet: rotate log files (100MB max per container)
  → Fluent Bit DaemonSet: tail files via inotify
  → Fluent Bit: parse + enrich with K8s metadata
  → Fluent Bit: forward to Loki/Elasticsearch
  → Grafana/Kibana: queryable within seconds
```

**FAILURE PATH:**
```
Fluent Bit pod unavailable on a node:
  → logs continue to /var/log/pods/ (kubelet-managed)
  → logs accumulate in node log files (up to rotation limit)
  → when Fluent Bit restarts: reads from last checkpoint
  → at most a few minutes of log loss (if rotation fills buffer)
  → critical fix: ensure Fluent Bit has sufficient resources
```

**WHAT CHANGES AT SCALE:**
At 10,000 pods on 500 nodes, log volume can reach terabytes per day. Strategies: log sampling (not all DEBUG logs need storage), log level filtering at agent level (only INFO+ in prod), index tiering (hot/warm/cold in Elasticsearch), log partitioning by namespace/service. Fluent Bit's buffering and backpressure configuration become critical to prevent OOM under log bursts.

---

### 💻 Code Example

**Example 1 — Spring Boot: structured logs to stdout:**
```xml
<!-- logback-spring.xml: output JSON to stdout -->
<configuration>
  <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <!-- Outputs JSON: {"@timestamp":...,"level":...,"message":...} -->
    </encoder>
  </appender>
  <root level="INFO">
    <appender-ref ref="STDOUT" />
  </root>
</configuration>
```

**Example 2 — Fluent Bit DaemonSet (Kubernetes):**
```yaml
# fluent-bit-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
data:
  fluent-bit.conf: |
    [INPUT]
        Name              tail
        Path              /var/log/pods/*/*.log
        multiline.parser  docker, cri
        Tag               kube.*
        Refresh_Interval  5
        Mem_Buf_Limit     5MB

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Merge_Log           On  # Parse JSON logs from app

    [OUTPUT]
        Name   loki
        Match  *
        Host   loki.monitoring.svc.cluster.local
        Port   3100
        Labels job=fluentbit
```

**Example 3 — kubectl log commands:**
```bash
# View current pod logs (stdout/stderr)
kubectl logs my-pod
kubectl logs my-pod -c my-container  # specific container

# Previous container logs (after restart)
kubectl logs my-pod --previous

# Stream live logs
kubectl logs my-pod -f

# Last 100 lines
kubectl logs my-pod --tail=100

# Logs since 1 hour ago
kubectl logs my-pod --since=1h

# From multiple pods matching label
kubectl logs -l app=myapp --all-containers --tail=50
```

**Example 4 — Node.js: structured stdout logging:**
```javascript
// Good: structured JSON logging to stdout
const log = (level, message, meta = {}) => {
  process.stdout.write(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    ...meta,
    service: 'my-api'
  }) + '\n');
};

// Usage:
log('INFO', 'Request received', { method: 'GET', path: '/api/users' });
log('ERROR', 'Database connection failed', { error: err.message });
```

---

### ⚖️ Comparison Table

| Logging Architecture | Overhead | Flexibility | Log Loss Risk | Best For |
|---|---|---|---|---|
| **Node-level DaemonSet (Fluent Bit)** | Low (1 pod/node) | Low (shared format) | Low (buffered) | Most clusters |
| Sidecar log shipper | Medium (1 sidecar/pod) | High (per-service config) | Very low | Custom formats |
| Application-direct (Datadog API) | Low (in-app) | High | Very low | SaaS-first teams |
| Docker log driver (awslogs, etc.) | Varies | Medium | Varies | Single-cloud environments |

How to choose: DaemonSet (Fluent Bit/Fluentd) for most Kubernetes clusters — consistent, low overhead, platform-managed. Sidecar when you have diverse log formats or need per-service log pipelines. Application-direct for simplicity in small teams using a unified SaaS platform.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "kubectl logs shows all historical logs" | kubectl logs reads kubelet's node-side log files with a limited rotation buffer (default: 100MB per container). Logs older than the rotation window are gone. Use centralised log storage (Loki, ELK) for historical queries. |
| "Writing to a log file in a volume is fine" | While technically possible, it couples the application to volume management, makes log collection inconsistent, and still requires a log shipper to read from the file. stdout is simpler and universal. |
| "Structured logs (JSON) are harder to read" | Human readability is for development; structured logs are for production. JSON logs enable powerful query operators (`level:ERROR AND service:auth AND duration>1000`). Use pretty-print logging in dev, JSON in production. |
| "More logs are always better" | Log volume directly impacts storage costs, query latency, and Fluent Bit resource usage. Appropriate log levels in production (INFO and above) are correct. DEBUG logs in production are expensive and often unnecessary. |
| "The DaemonSet approach guarantees zero log loss" | DaemonSet forwarding is near-zero loss but not zero. If a node crashes after writing to the node-local file but before Fluent Bit forwards it, those logs are lost. For guaranteed log delivery, use application-direct or at-least-once delivery with durable queues. |

---

### 🚨 Failure Modes & Diagnosis

**kubectl logs returns nothing (empty output)**

**Symptom:**
`kubectl logs my-pod` returns empty output despite the application running.

**Root Cause:**
Application is writing to a log file inside the container instead of stdout/stderr. kubelet only captures stdout/stderr.

**Diagnostic Command / Tool:**
```bash
# Check if container is writing to stdout
kubectl exec my-pod -- cat /proc/1/fd/1 | head -20
# fd/1 = stdout; if empty → app not writing to stdout

# Check if logs exist in a file
kubectl exec my-pod -- ls -la /var/log/
kubectl exec my-pod -- tail -f /var/log/app/app.log
```

**Fix:**
Reconfigure application logging to write to stdout. For Java: use `ConsoleAppender`. For Node: use `process.stdout.write`. For Python: use `logging.StreamHandler()`.

**Prevention:**
Validate stdout logging in development environment: `docker run myapp 2>&1 | head` should show log output immediately.

---

**Log storage overwhelmed by noisy log output**

**Symptom:**
Elasticsearch disk fills up. Loki ingestion rate exceeded alerts. High log storage costs. Kibana queries time out.

**Root Cause:**
One or more containers outputting DEBUG logs at high volume (millions of lines/minute). Unbounded log volume.

**Diagnostic Command / Tool:**
```bash
# Find top log-producing pods
kubectl top pods --all-namespaces | sort -k4 -nr | head

# Check specific pod log rate
kubectl logs my-pod --since=1m | wc -l
```

**Fix:**
Set appropriate log level for production: `LOG_LEVEL=INFO`. Add sampling in Fluent Bit (output 1 in 100 DEBUG lines). Add namespace/label-based filtering in Fluent Bit to drop DEBUG from prod.

**Prevention:**
Policy: no DEBUG logging in production by default. Fluent Bit sampling rules for high-volume services. Log volume alerting when per-service log rate exceeds threshold.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Container` — logging is a container concern; understand containers first
- `Docker` — Docker captures stdout/stderr and provides log drivers
- `Sidecar Container` — sidecar pattern implements one logging architecture

**Builds On This (learn these next):**
- `Observability & SRE` — logging is one pillar of the three pillars of observability (logs, metrics, traces)
- `Structured Logging` — structured (JSON) log format enables powerful log queries
- `ELK Stack` — Elasticsearch/Kibana is a common destination for container logs

**Alternatives / Comparisons:**
- `Structured Logging` — the format recommendation for container logs
- `Loki` — lightweight, labels-based log storage alternative to Elasticsearch
- `Observability` — logging in context of the broader observability triad

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ System for capturing ephemeral container  │
│              │ stdout/stderr to durable log storage      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Container restarts destroy local log      │
│ SOLVES       │ files — incidents undiagnosable           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ stdout = universal log interface.         │
│              │ Application writes; infrastructure        │
│              │ collects. Decoupled by design.            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every containerised application.          │
│              │ stdout + DaemonSet (Fluent Bit) = default │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Writing to application log files inside   │
│              │ container (use volumes + sidecar instead) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplicity (stdout) vs flexibility        │
│              │ (sidecar) vs coupling (app-direct)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "stdout is the /dev/null of logging:      │
│              │  not nothing — everything, captured       │
│              │  by infrastructure, not the app"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Structured Logging → ELK Stack / Loki →   │
│              │ Observability & SRE                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your cluster has 500 pods. Each pod logs 10,000 lines per minute in JSON format (average 200 bytes/line). Calculate: the total cluster log volume per day, the storage cost at $0.02/GB/month, and the network bandwidth consumed by Fluent Bit forwarding to a centralised Loki cluster. Then design a log sampling and filtering policy that reduces storage cost by 80% while retaining 100% of ERROR and WARN logs, and explain how you would implement this in Fluent Bit configuration.

**Q2.** You are building a financial services application where all transaction logs must be immutable, tamper-evident, and retained for 7 years for regulatory compliance. Stdout-to-Elasticsearch is your current logging stack. Analyse: does your current stack satisfy the immutability and tamper-evidence requirements? What attack vectors exist (who can delete or modify logs)? Design a logging architecture that satisfies the regulatory requirements, specifying exactly which component provides each property: immutability, tamper-evidence, retention, and auditability.

