---
layout: default
title: "Async & Background Processing"
parent: "Technical Dictionary"
nav_order: 45
has_children: true
permalink: /async-background/
---

# Async & Background Processing

Task queues, message brokers, workers, retry patterns, fan-out/fan-in, Celery, RabbitMQ, Airflow, and async observability.

**Keywords:** ASY-001–ASY-044 (44 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| ASY-001 | What Is Async and Background Processing | ★☆☆ |
| ASY-002 | The Async Mental Model (Sync vs Async vs Parallel) | ★☆☆ |
| ASY-003 | Message Queue vs Event Bus vs Task Queue -- Map | ★☆☆ |
| ASY-004 | The Async Ecosystem Map (RabbitMQ, Kafka, Celery, SQS) | ★☆☆ |
| ASY-005 | Async in Production -- What Engineers Face | ★☆☆ |
| ASY-006 | Message Queues Fundamentals (Producer, Consumer, Queue) | ★☆☆ |
| ASY-007 | At-Least-Once vs Exactly-Once vs At-Most-Once Delivery | ★☆☆ |
| ASY-008 | Idempotency in Async Systems | ★☆☆ |
| ASY-009 | Job Queues and Worker Patterns | ★☆☆ |
| ASY-010 | RabbitMQ Fundamentals (Exchange, Queue, Binding) | ★☆☆ |
| ASY-011 | Apache Kafka Fundamentals | ★☆☆ |
| ASY-012 | AWS SQS and SNS | ★☆☆ |
| ASY-013 | Dead Letter Queues (DLQ) | ★★☆ |
| ASY-014 | Message Retry Strategies (Exponential Backoff) | ★★☆ |
| ASY-015 | Event-Driven Architecture Patterns | ★★☆ |
| ASY-016 | Celery (Python Task Queue) | ★★☆ |
| ASY-017 | Quartz Scheduler (Java) | ★★☆ |
| ASY-018 | Cron Jobs and Scheduled Tasks | ★★☆ |
| ASY-019 | Saga Pattern (Distributed Transactions) | ★★☆ |
| ASY-020 | Outbox Pattern | ★★☆ |
| ASY-021 | Consumer Group and Partition Strategy (Kafka) | ★★☆ |
| ASY-022 | Kafka Consumer Lag and Monitoring | ★★☆ |
| ASY-023 | Message Schema Evolution (Avro, Protobuf) | ★★☆ |
| ASY-024 | Poison Pill Messages and Circuit Breaker | ★★☆ |
| ASY-025 | Async API Design (Webhooks, Callbacks, Polling) | ★★☆ |
| ASY-026 | Priority Queues | ★★☆ |
| ASY-027 | Message Deduplication | ★★☆ |
| ASY-028 | Temporal (Workflow Orchestration) | ★★☆ |
| ASY-029 | AWS Step Functions | ★★☆ |
| ASY-030 | Kafka Exactly-Once Semantics (EOS) | ★★★ |
| ASY-031 | Kafka Streams and KSQL | ★★★ |
| ASY-032 | Async System Observability (Lag, Throughput, Error Rate) | ★★★ |
| ASY-033 | Backpressure in Async Systems | ★★★ |
| ASY-034 | Distributed Scheduler Design | ★★★ |
| ASY-035 | Message Broker Selection Strategy | ★★★ |
| ASY-036 | Async Architecture Pattern Selection (Queue vs Stream vs Choreography) | ★★★ |
| ASY-037 | Workflow Orchestration Architecture (Temporal vs Step Functions) | ★★★ |
| ASY-038 | Kafka Internals Deep Dive (Replication, ISR, Log Compaction) | ★★★ |
| ASY-039 | Message Queue Algorithm Research | ★★★ |
| ASY-040 | Distributed Consensus in Message Systems | ★★★ |
| ASY-041 | Async Trade-off Framing (Decoupling vs Complexity) | ★★★ |
| ASY-042 | Message Delivery Guarantee Mental Model | ★★★ |
| ASY-043 | Event-Driven vs Request-Response Thinking | ★★★ |
| ASY-044 | Async Observability Mental Model | ★★★ |
