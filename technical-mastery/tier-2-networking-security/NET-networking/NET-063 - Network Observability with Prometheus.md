---
id: NET-063
title: "Network Observability with Prometheus"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-062
used_by: NET-067
related: NET-062, NET-067, NET-068
tags:
  - networking
  - observability
  - prometheus
  - grafana
  - metrics
  - monitoring
  - ebpf
  - blackbox-exporter
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 63
permalink: /technical-mastery/net/network-observability-with-prometheus/
---

**⚡ TL;DR** - Network observability answers: "Are packets
flowing? Are connections succeeding? What is the latency
between services? Are there retransmits? Is DNS working?"
Prometheus collects these metrics via exporters: node
exporter (Linux network stats), blackbox exporter
(probe URLs from outside), kube-state-metrics
(Kubernetes), and Istio/Envoy metrics for service mesh.
Critical metrics: TCP retransmit rate, connection
establishment rate, DNS query latency, HTTP error rate
per service pair, and saturated queue depth.

| #063 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Mesh (NET-062) | |
| **Used by:** | Networking Deep-Dive Interview Questions (NET-067), Production Network Incident Simulation (NET-068) | |
| **Related:** | Service Mesh, Networking Deep-Dive Interview Questions, Production Network Incident Simulation | |

---

### 🔥 The Problem This Solves

A service degrades. Error rate increases. Is it network
retransmits causing timeouts? Is it DNS failing? Is it
a specific upstream service? Application logs show errors
but not causes. Network metrics: `node_netstat_Tcp_RetransSegs`
spikes at 14:32 → correlates exactly with error rate
spike. Root cause: packet loss on a specific network
interface. Without metrics, this takes hours of
investigation; with them, 5 minutes.

---

### 🧠 Intuition: Four Signals for Network Health

```
The four networking observability signals:

1. Connectivity (is traffic flowing?):
   Probe: HTTP/TCP check from outside
   Metric: blackbox_probe_success{job="http", instance="api.example.com"}
   Alert: probe_success == 0 for 1 minute

2. Latency (how slow is it?):
   Probe: HTTP request timing from blackbox exporter
   Metric: blackbox_probe_http_duration_seconds
   Labels: {phase="connect"}, {phase="tls"}, {phase="processing"}
   Alert: P95 > 500ms

3. Error rate (what fraction is failing?):
   Envoy/Istio: istio_requests_total{response_code=~"5.."}
   Application: http_requests_total{status=~"5.."}
   Alert: error_rate > 1% for 5 minutes

4. Saturation (is something overloaded?):
   TCP retransmits: node_netstat_Tcp_RetransSegs
   Connection errors: node_netstat_Tcp_AttemptFails
   Queue depth: netstat_udp_receive_buffer_errors
   Alert: retransmit rate > threshold
```

---

### ⚙️ Node Exporter: Linux Network Metrics

```yaml
# Prometheus scrape config for node exporter
# node_exporter exposes /proc/net/* as Prometheus metrics

# Key metrics from node exporter:

# TCP statistics:
# node_netstat_Tcp_ActiveOpens      - outbound connection attempts/s
# node_netstat_Tcp_PassiveOpens     - accepted connections/s
# node_netstat_Tcp_AttemptFails     - failed connection attempts
# node_netstat_Tcp_RetransSegs      - retransmitted segments (counter)
# node_netstat_Tcp_InErrs           - bad TCP segments received
# node_netstat_Tcp_OutRsts          - RST packets sent

# Network interface:
# node_network_receive_bytes_total   - bytes received per interface
# node_network_transmit_bytes_total  - bytes transmitted per interface
# node_network_receive_drop_total    - receive drops (buffer overflow)
# node_network_transmit_drop_total   - transmit drops
# node_network_receive_errs_total    - receive errors
# node_network_transmit_errs_total   - transmit errors

# Socket stats:
# node_netstat_Tcp_CurrEstab         - currently established connections
# node_sockstat_TCP_tw               - connections in TIME_WAIT
# node_sockstat_TCP_inuse            - in-use TCP sockets
```

```promql
# PromQL: TCP retransmit rate (per second)
rate(node_netstat_Tcp_RetransSegs[5m])

# Alert: retransmit rate > 10/second
- alert: HighTCPRetransmitRate
  expr: rate(node_netstat_Tcp_RetransSegs[5m]) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High TCP retransmit rate on {{ $labels.instance }}"
    description: "{{ $value }} retransmits/second (>10)"

# Network bandwidth utilization (bytes/s to bits/s):
rate(node_network_receive_bytes_total{device="eth0"}[1m]) * 8

# Interface error rate:
rate(node_network_receive_errs_total{device="eth0"}[5m])

# TIME_WAIT count:
node_sockstat_TCP_tw

# Alert: approaching port exhaustion
- alert: HighTimeWaitCount
  expr: node_sockstat_TCP_tw > 20000
  for: 2m
  annotations:
    description: "{{ $value }} TIME_WAIT sockets - port exhaustion risk"
```

---

### ⚙️ Blackbox Exporter: Active Probing

```yaml
# blackbox_exporter: probes endpoints, reports success/latency
# Runs as a separate service, receives probe requests from Prometheus

# prometheus.yml - scrape config
scrape_configs:
  - job_name: "blackbox_http"
    metrics_path: /probe
    params:
      module: [http_2xx]    # probe module (expects 200-299)
    static_configs:
      - targets:
        - https://api.example.com/health
        - https://api.example.com/v1/users
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  - job_name: "blackbox_tcp"
    metrics_path: /probe
    params:
      module: [tcp_connect]
    static_configs:
      - targets:
        - db-host:5432
        - redis-host:6379
        - kafka-host:9092
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - target_label: __address__
        replacement: blackbox-exporter:9115

# blackbox_exporter config.yml
modules:
  http_2xx:
    prober: http
    timeout: 10s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []  # default: 2xx
      method: GET
      tls_config:
        insecure_skip_verify: false
      preferred_ip_protocol: "ip4"

  tcp_connect:
    prober: tcp
    timeout: 5s
    tcp: {}
```

```promql
# Key blackbox metrics:
# blackbox_probe_success: 1=success, 0=failure
# blackbox_probe_duration_seconds: total probe duration
# blackbox_probe_http_duration_seconds{phase="..."}: 
#   phases: dns, connect, tls, processing, transfer
# blackbox_probe_ssl_earliest_cert_expiry: cert expiry timestamp

# HTTP probe breakdown:
blackbox_probe_http_duration_seconds{instance="api.example.com",phase="dns"}
blackbox_probe_http_duration_seconds{instance="api.example.com",phase="connect"}
blackbox_probe_http_duration_seconds{instance="api.example.com",phase="tls"}
blackbox_probe_http_duration_seconds{instance="api.example.com",phase="processing"}

# TLS certificate expiry alert:
- alert: SSLCertExpiringSoon
  expr: >
    (blackbox_probe_ssl_earliest_cert_expiry - time()) / 86400 < 30
  labels:
    severity: warning
  annotations:
    description: "SSL cert on {{ $labels.instance }} expires in {{ $value }} days"

# Service availability dashboard:
# Panel: blackbox_probe_success (1 or 0 per target)
# Panel: http_duration broken down by phase
# Panel: probe latency P95
```

---

### ⚙️ Istio/Envoy Metrics for Service-to-Service

```promql
# Istio provides L7 metrics per service pair (via Envoy)
# Requires: Istio mesh with telemetry enabled

# Total requests per service pair:
istio_requests_total{
  source_workload="frontend",
  destination_service_name="backend",
  response_code=~"2.."
}

# Error rate between two services:
rate(istio_requests_total{
  destination_service_name="payment-service",
  response_code=~"5.."
}[5m])
/
rate(istio_requests_total{
  destination_service_name="payment-service"
}[5m])

# P99 latency between services:
histogram_quantile(0.99,
  sum(rate(
    istio_request_duration_milliseconds_bucket{
      destination_service_name="product-service"
    }[5m]
  )) by (le)
)

# Circuit breaker ejections:
rate(envoy_cluster_outlier_detection_ejections_active[1m])

# Alert: service error rate > 1%
- alert: ServiceErrorRateHigh
  expr: >
    (
      rate(istio_requests_total{response_code=~"5.."}[5m])
      /
      rate(istio_requests_total[5m])
    ) > 0.01
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: >
      Error rate {{ $value | humanizePercentage }} for
      {{ $labels.destination_service_name }}
```

---

### ⚙️ Wrong vs Right: Alerting on Average vs Percentiles

```promql
# BAD: alert on average latency
- alert: HighLatency
  expr: >
    avg(http_request_duration_seconds) > 0.5
  # Average hides tail latency problems
  # 999 requests at 100ms + 1 request at 50s
  # Average = ~150ms (below threshold)
  # But 0.1% of users get 50 second responses!

# GOOD: alert on P99 latency
- alert: HighP99Latency
  expr: >
    histogram_quantile(0.99,
      sum(rate(
        http_request_duration_seconds_bucket[5m]
      )) by (le, service)
    ) > 1
  for: 5m
  # 1% of users experiencing > 1 second → alert
  annotations:
    summary: "P99 latency {{ $value }}s for {{ $labels.service }}"

# GOOD: multi-window alerting (short burn rate)
# Alert only when error rate × time budget is exceeded
- alert: ErrorBudgetBurnHigh
  expr: >
    (
      rate(http_requests_total{status=~"5.."}[1h])
      /
      rate(http_requests_total[1h])
    ) > 14.4 * 0.001  # 14.4x burn rate on 0.1% budget
  for: 5m
  # burns 1 hour of 30-day budget in ~2 hours
  # based on Google SRE book "burn rate" alerting
```

---

### 📐 Scale Considerations

```
Prometheus scaling for network metrics:

Default node exporter: ~200-500 metrics per node
At 100 nodes: 20,000-50,000 time series
Default Prometheus: handles 1-10M time series
At 1,000 nodes: consider:
  - Remote write to Thanos/Cortex/Mimir
  - Recording rules to pre-aggregate
  - Separate Prometheus instances per cluster

Cardinality explosion risk:
  Network metrics by source+destination per service pair:
  50 services × 50 = 2,500 service pairs
  × 5 response codes × 100 HTTP paths = 1.25M series
  
  Mitigation:
  - Drop high-cardinality labels (per-URL → per-service)
  - metric_relabel_configs to drop unused labels
  - Use Istio telemetry v2 (configurable cardinality)

eBPF-based observability (alternative to exporters):
  Cilium Hubble: per-flow metrics from kernel
  No sidecar overhead, no application changes
  Exports: Prometheus-compatible metrics + Hubble UI
  Shows: which pods communicate, which are blocked, latency

High-cardinality tracing vs metrics:
  Prometheus metrics: low cardinality (service → service aggregated)
  Distributed traces (Jaeger/Zipkin): per-request, high cardinality
  Logs: full detail, high cardinality, high cost
  → Use metrics for alerting, traces for root cause
```

---

### 🧭 Decision Guide

```
What to monitor for networking:

Minimum viable monitoring:
  blackbox_probe_success per endpoint
  blackbox_probe_http_duration_seconds P95
  node_network_receive_drop_total rate
  node_netstat_Tcp_RetransSegs rate

Add next:
  node_sockstat_TCP_tw (TIME_WAIT accumulation)
  node_netstat_Tcp_AttemptFails (connection failures)
  DNS probe latency per nameserver
  TLS certificate expiry alerts

With service mesh:
  istio_requests_total error rate per service pair
  istio_request_duration_milliseconds P99 per service pair
  Envoy circuit breaker ejection rate

Alert priorities:
  P1 (page now): probe_success == 0 (service unreachable)
  P1: error_rate > 10% for 1 minute
  P2 (page if sustained): P99 latency > 1s for 5 minutes
  P2: TCP retransmit rate > 100/second for 5 minutes
  P3 (ticket): TLS cert expiry < 30 days
  P3: TIME_WAIT > 20,000 sockets

Grafana dashboard minimum:
  Top-level: probe success/failure per endpoint (traffic light)
  HTTP: request rate, error rate, P50/P95/P99 latency
  Infrastructure: bandwidth utilization per interface
  TCP: established connections, TIME_WAIT, retransmits
  DNS: query success rate, query latency
```