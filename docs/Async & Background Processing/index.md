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

**Keywords:** 1883–1960 (78 terms)

| # | Keyword | Difficulty |
|---|---|---|
| 1883 | Synchronous vs Asynchronous Processing | ★☆☆ |
| 1884 | Why Async Processing Exists | ★☆☆ |
| 1885 | Task / Job | ★☆☆ |
| 1886 | Task Queue | ★☆☆ |
| 1887 | Producer (Task) | ★☆☆ |
| 1888 | Consumer (Task) | ★☆☆ |
| 1889 | Message Broker | ★★☆ |
| 1890 | Worker Process | ★★☆ |
| 1891 | Worker Concurrency | ★★☆ |
| 1892 | Job Scheduling | ★★☆ |
| 1893 | Cron Expression | ★★☆ |
| 1894 | Async vs Sync Decision Criteria | ★★☆ |
| 1895 | Fire-and-Forget Pattern | ★★☆ |
| 1896 | Message Acknowledgement (ACK / NACK) | ★★☆ |
| 1897 | Message Durability | ★★☆ |
| 1898 | At-Least-Once Delivery (Tasks) | ★★☆ |
| 1899 | At-Most-Once Delivery (Tasks) | ★★☆ |
| 1900 | Exactly-Once Delivery (Tasks) | ★★★ |
| 1901 | Task Idempotency | ★★★ |
| 1902 | Poison Pill Message | ★★★ |
| 1903 | Dead Letter Queue (DLQ) in Task Systems | ★★★ |
| 1904 | Message TTL (Time to Live) | ★★☆ |
| 1905 | Task Retry Logic | ★★☆ |
| 1906 | Exponential Backoff (Task) | ★★★ |
| 1907 | Jitter in Retry | ★★★ |
| 1908 | Max Retry Limit | ★★☆ |
| 1909 | Task Timeout | ★★★ |
| 1910 | Partial Failure Handling | ★★★ |
| 1911 | Circuit Breaker for Task Queues | ★★★ |
| 1912 | Task Chaining | ★★★ |
| 1913 | Task Grouping | ★★★ |
| 1914 | Task Chord | ★★★ |
| 1915 | Fan-Out Pattern (Tasks) | ★★★ |
| 1916 | Fan-In Pattern (Tasks) | ★★★ |
| 1917 | Task DAG (Directed Acyclic Graph) | ★★★ |
| 1918 | Scatter-Gather Pattern | ★★★ |
| 1919 | Task Priority Queue | ★★★ |
| 1920 | Delayed Task Execution | ★★★ |
| 1921 | Long-Running Tasks | ★★★ |
| 1922 | Progress Tracking (Task) | ★★★ |
| 1923 | Task Cancellation | ★★★ |
| 1924 | Saga via Task Orchestration | ★★★ |
| 1925 | Redis as Message Broker | ★★☆ |
| 1926 | RabbitMQ | ★★☆ |
| 1927 | RabbitMQ Exchange Types (Direct, Fanout, Topic, Headers) | ★★★ |
| 1928 | RabbitMQ Routing Key | ★★★ |
| 1929 | RabbitMQ Binding | ★★★ |
| 1930 | RabbitMQ Virtual Host | ★★★ |
| 1931 | Celery | ★★☆ |
| 1932 | Celery Worker | ★★☆ |
| 1933 | Celery Beat (Scheduler) | ★★★ |
| 1934 | Celery Result Backend | ★★★ |
| 1935 | Celery Configuration Patterns | ★★★ |
| 1936 | Celery Concurrency Models (prefork, gevent, eventlet) | ★★★ |
| 1937 | BullMQ (Node.js) | ★★★ |
| 1938 | Temporal (Workflow Orchestration) | ★★★ |
| 1939 | Prefect | ★★★ |
| 1940 | Apache Airflow | ★★★ |
| 1941 | Airflow DAG | ★★★ |
| 1942 | Airflow Operator | ★★★ |
| 1943 | Competing Consumers Pattern | ★★★ |
| 1944 | Queue Depth as Autoscaling Signal | ★★★ |
| 1945 | Backpressure in Task Systems | ★★★ |
| 1946 | Task Serialization | ★★★ |
| 1947 | Outbox Pattern for Reliable Task Dispatch | ★★★ |
| 1948 | Transactional Task Dispatch | ★★★ |
| 1949 | Event-Driven vs Task-Driven Architecture | ★★★ |
| 1950 | Webhook vs Task Queue | ★★☆ |
| 1951 | Async API Response Pattern (202 Accepted) | ★★★ |
| 1952 | Polling for Async Result | ★★★ |
| 1953 | Callback Pattern (Async) | ★★★ |
| 1954 | Task Monitoring (Flower) | ★★★ |
| 1955 | Queue Depth Monitoring | ★★★ |
| 1956 | Task Observability | ★★★ |
| 1957 | Worker Health Check | ★★★ |
| 1958 | Worker Capacity Planning | ★★★ |
| 1959 | Task Tracing (OpenTelemetry) | ★★★ |
| 1960 | Task Alerting Patterns | ★★★ |
