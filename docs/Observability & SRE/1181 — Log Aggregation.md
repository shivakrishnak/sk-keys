---
layout: default
title: "Log Aggregation"
parent: "Observability & SRE"
nav_order: 1181
permalink: /observability/log-aggregation/
number: "1181"
category: Observability & SRE
difficulty: ★★☆
depends_on: "Logging, Structured Logging"
used_by: "ELK Stack, Loki, Observability, incident response"
tags: #observability, #log-aggregation, #centralized-logging, #fluentd, #logstash, #elk
---

# 1181 — Log Aggregation

`#observability` `#log-aggregation` `#centralized-logging` `#fluentd` `#logstash` `#elk`

⚡ TL;DR — **Log aggregation** collects logs from all services and instances into a centralized, searchable store. In distributed systems with 50 services × 10 instances each = 500 log streams — you can't SSH into each instance and grep. Aggregation tools (Fluentd, Logstash, Fluent Bit) ship logs from every instance to a central store (Elasticsearch, Loki) where they can be searched, filtered, and alerted on.

| #1181           | Category: Observability & SRE                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Logging, Structured Logging                       |                 |
| **Used by:**    | ELK Stack, Loki, Observability, incident response |                 |

---

### 📘 Textbook Definition

**Log aggregation**: the practice of collecting, normalizing, and centralizing log data from multiple sources (services, instances, containers, infrastructure) into a single searchable system. In distributed systems, logs are generated on every container/pod/VM — there is no single log file. Log aggregation solves the distributed log problem: (1) **Collection**: log shippers (Fluentd, Fluent Bit, Logstash, Vector) run on every node/pod and forward logs to the central store; (2) **Parsing/normalization**: extract structured fields from logs (parse JSON, or apply grok patterns to unstructured logs); (3) **Storage**: an indexing system that enables full-text search and field-value queries (Elasticsearch, or Loki for label-based indexing); (4) **Query and visualization**: Kibana (for Elasticsearch), Grafana (for Loki) — search, filter, create dashboards, alert. Architectures: (a) **ELK Stack** (Elasticsearch + Logstash + Kibana): full-featured; Logstash as log processor; Elasticsearch as store; Kibana for visualization; (b) **Grafana Loki**: lightweight; Fluent Bit as shipper; Loki stores compressed logs indexed by labels only (not full-text); Grafana for querying; cost-effective for high log volumes; (c) **Cloud-managed**: AWS CloudWatch Logs, Google Cloud Logging, Azure Monitor — no infrastructure to manage; (d) **Commercial**: Datadog Logs, Splunk, New Relic Logs — full-stack observability with logs integrated with metrics and traces. Key consideration: structured JSON logs from all services make aggregation most effective — no custom parsers needed.

---

### 🟢 Simple Definition (Easy)

You have 20 microservices running on 50 servers. Each writes logs to its own file. During an incident, you need to find what happened — but you'd need to SSH into 50 servers and grep 20 log files simultaneously. Log aggregation solves this: all 50 servers send their logs to one central place automatically. You search once in Kibana or Grafana; logs from all services appear together.

---

### 🔵 Simple Definition (Elaborated)

Log aggregation pipeline:

```
App container → stdout/stderr
                    ↓
    [Log shipper: Fluent Bit]  (sidecar or DaemonSet per node)
                    ↓
    [Log processor: optional — Logstash for transformation]
                    ↓
    [Log store: Elasticsearch or Loki]
                    ↓
    [Query/Visualization: Kibana or Grafana]
```

**Fluent Bit vs Logstash vs Fluentd**:
| Tool | Resource usage | Use case |
|---|---|---|
| **Fluent Bit** | Very low (~450KB RAM) | Edge collection (Kubernetes DaemonSet per node) |
| **Fluentd** | Medium (~40MB RAM) | Aggregation layer (fan-in from multiple sources) |
| **Logstash** | High (JVM, ~500MB) | Complex transformation pipelines; lots of plugins |
| **Vector** | Low (Rust-based) | Modern alternative; high performance |

**Elasticsearch vs Loki**:
| | **Elasticsearch** | **Loki** |
|---|---|---|
| Indexing | Full-text index on all fields | Label-based index only |
| Query | Powerful full-text + field queries | Label filters + regex on log line |
| Storage cost | High (large indexes) | Low (compressed log chunks) |
| Query speed | Very fast (indexed fields) | Depends on log line scan |
| Best for | Complex search; compliance | Cost-effective; already using Grafana |

---

### 🔩 First Principles Explanation

```yaml
# KUBERNETES LOG AGGREGATION SETUP
# Fluent Bit DaemonSet: one log shipper per Kubernetes node

apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    spec:
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:2.1
          volumeMounts:
            - mountPath: /var/log
              name: varlog
            - mountPath: /var/lib/docker/containers
              name: varlibdockercontainers
              readOnly: true
          envFrom:
            - configMapRef:
                name: fluent-bit-config

      volumes:
        - hostPath: { path: /var/log }
          name: varlog
        - hostPath: { path: /var/lib/docker/containers }
          name: varlibdockercontainers
```

```yaml
# fluent-bit.conf: collect → parse → forward

[SERVICE]
    Flush        5
    Log_Level    info
    Parsers_File parsers.conf

[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker                      # parse Docker JSON log format
    Tag               kube.*
    Refresh_Interval  5
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On

[FILTER]
    Name                kubernetes
    Match               kube.*
    Kube_URL            https://kubernetes.default.svc:443
    Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
    Merge_Log           On       # merge JSON log body with Fluent Bit record
    K8S-Logging.Parser  On       # use parser annotations if set on pod
    Annotations         Off
    Labels              On       # include pod labels (app=order-service, etc.)

[FILTER]
    Name  grep
    Match kube.*
    # Drop health check spam from logs
    Exclude log /health|/actuator/health

[OUTPUT]
    Name            loki
    Match           kube.*
    Host            loki.logging.svc.cluster.local
    Port            3100
    Labels          job=fluentbit, app=$kubernetes['labels']['app'],
                    namespace=$kubernetes['namespace_name'],
                    pod=$kubernetes['pod_name']
    Remove_keys     kubernetes, stream
    Auto_Kubernetes_Labels On
```

```
LOG AGGREGATION QUERY EXAMPLES (Grafana/Loki):

  FIND ALL ERRORS FOR ORDER SERVICE IN LAST HOUR:
  {app="order-service"} | json | level="ERROR"

  FIND ALL EVENTS FOR A SPECIFIC TRACE (correlate across services):
  {} | json | traceId="abc123"    ← searches ALL services for this trace

  FIND SLOW OPERATIONS (over 1 second):
  {app=~"order-service|inventory-service"} | json | duration_ms > 1000

  COUNT ERRORS PER SERVICE (metrics from logs):
  sum by (app) (count_over_time({} | json | level="ERROR" [5m]))

  SEARCH LOG AGGREGATION PIPELINE HEALTH:
  {job="fluentbit"} | logfmt | level="error"  ← check if shipper has errors

LOG RETENTION POLICIES:
  ─────────────────────────────────────────────────────────────
  Production logs: 30 days hot storage, 1 year cold storage
  Compliance logs: 7 years (PCI-DSS, HIPAA requirements)
  Debug logs: 7 days (high volume, low value long-term)
  Audit logs (security events): 1-3 years

  Cost optimization: tiered storage
  → Last 7 days: fast SSD (frequent queries during incidents)
  → 7-30 days: warm storage (occasional queries)
  → 30+ days: S3/cold storage (compliance; rare queries)
```

---

### ❓ Why Does This Exist (Why Before What)

Pre-containerization: a service ran on 2-5 servers; `tail -f /var/log/app.log` and SSH were sufficient. With containers and microservices: a service runs on 50 pods; each pod writes to stdout; pods are ephemeral (deleted after restart, taking their logs with them). Without aggregation, all logs are lost when a pod crashes — exactly when you need them most. Log aggregation emerged as an operational necessity for distributed systems: centralize logs before they're lost, make them searchable across services, retain them for compliance.

---

### 🧠 Mental Model / Analogy

> **Log aggregation is like a central mailroom**: instead of visiting each of 50 offices to collect mail individually, the mailroom collects all mail from all offices, sorts it centrally, and enables efficient retrieval. The Fluent Bit DaemonSet is the mail carrier visiting each office (node); Elasticsearch/Loki is the mailroom's sorted filing system; Kibana/Grafana is the search interface that lets you find any piece of mail instantly.

---

### 🔄 How It Connects (Mini-Map)

```
Multiple services on multiple instances each generate log streams
        │
        ▼
Log Aggregation ◄── (you are here)
(collect → parse → store → query; centralized search across all services)
        │
        ├── Structured Logging: JSON logs require no parsing in aggregation pipeline
        ├── ELK Stack: Elasticsearch + Logstash + Kibana — classic aggregation stack
        ├── Loki: Grafana's log aggregation — label-indexed, cost-effective
        └── Observability: log aggregation is the infrastructure for the "logs" pillar
```

---

### 💻 Code Example

```yaml
# LOKI CONFIGURATION: minimal production-ready Loki setup

auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      replication_factor: 1
  chunk_idle_period: 5m
  max_chunk_age: 1h
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: s3 # store log chunks in S3 for cost efficiency
      schema: v11
      index:
        prefix: loki_index_
        period: 24h # one index per day

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    shared_store: s3
    cache_location: /loki/cache
  aws:
    s3: s3://my-loki-bucket/loki
    region: us-east-1

limits_config:
  ingestion_rate_mb: 32 # per-tenant rate limit
  max_query_length: 721h # max 30 days query window
  retention_period: 720h # 30 day retention
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Log aggregation means storing all logs forever         | Log storage is expensive. Without retention policies, logs accumulate indefinitely. Define tiered retention: last 7 days in hot storage (fast queries), 7-30 days in warm, 30+ days in cold/S3 (compliance only). Most incidents are investigated within 7 days; compliance retention (1-7 years) can use cheap cold storage.                                            |
| Logstash should be used for collection from Kubernetes | Logstash is resource-heavy (JVM, ~500MB per instance). As a DaemonSet on every node, it multiplies infrastructure cost. Use Fluent Bit (lightweight, ~450KB RAM, Rust-like efficiency) for collection on each node. Use Logstash only if you have complex transformation needs — and then as an aggregation layer, not a per-node shipper.                               |
| Log aggregation is real-time                           | Log aggregation has inherent latency: Fluent Bit buffers logs (5-30 second flush intervals), Loki/Elasticsearch index log ingestion takes seconds. Log aggregation is near-real-time (typically 5-60 second delay), not instantaneous. For real-time alerting, use metrics (which are scraped every 15-30 seconds by Prometheus) rather than log-based alerts which lag. |

---

### 🔗 Related Keywords

- `Structured Logging` — JSON logs are directly indexable; no custom parsers needed
- `ELK Stack` — Elasticsearch + Logstash + Kibana: the classic aggregation stack
- `Loki` — Grafana's lightweight log aggregation: label-indexed, cost-effective
- `Logging` — the source of data for log aggregation
- `Observability` — log aggregation implements the "logs" pillar of observability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LOG AGGREGATION PIPELINE:                               │
│  App → stdout → Fluent Bit → Loki/Elasticsearch        │
│                                                          │
│ SHIPPERS: Fluent Bit (lightweight K8s) | Logstash (heavy)│
│ STORES: Elasticsearch (full-text) | Loki (labels, cheap)│
│ QUERY: Kibana (ES) | Grafana (Loki)                    │
│                                                          │
│ STRUCTURED LOGS → no parsing needed → faster ingest   │
│ RETENTION: 7d hot | 30d warm | 1yr cold (compliance)  │
│                                                          │
│ K8s: Fluent Bit DaemonSet (one per node, auto-collect) │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Log aggregation at scale (10,000+ pods, 1 TB/day of logs) creates infrastructure challenges: the aggregation backend (Elasticsearch cluster) becomes a critical dependency — if it goes down, you lose observability during an incident. How do you design a resilient log aggregation architecture? Consider: buffering at the shipper to handle backend outages (Fluent Bit local buffer to disk); multiple log stores (primary Loki for recent logs; secondary S3 for durable storage); log aggregation high availability (Elasticsearch cluster with replicas; Loki with replication factor > 1). What's the trade-off between resilience and cost?

**Q2.** Security and compliance for log aggregation: logs contain sensitive data (IP addresses, user IDs, session tokens, error messages with PII). Log aggregation centralizes this data into a high-value target. Security requirements: (a) encryption in transit (TLS between shipper and store); (b) encryption at rest (Elasticsearch encrypted storage, S3 SSE); (c) access control (who can query which logs — should developers see production payment logs?); (d) audit logging of log access itself (who queried what, when); (e) PII redaction (filter out email addresses, IP addresses before storing). Design the security architecture for a GDPR-compliant log aggregation system serving 20 development teams with different data access requirements.
