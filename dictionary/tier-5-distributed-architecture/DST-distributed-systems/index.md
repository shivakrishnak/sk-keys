---
layout: default
title: "Distributed Systems"
parent: "Technical Dictionary"
nav_order: 21
has_children: true
permalink: /distributed-systems/
---

# Distributed Systems

CAP theorem, consistency models, consensus algorithms, distributed locking, failure modes, and resilience patterns.

**Keywords:** DST-001–DST-085 (85 terms)

| ID      | Keyword                                              | Difficulty |
| ------- | ---------------------------------------------------- | ---------- |
| DST-001 | What Is a Distributed System                         | ★☆☆        |
| DST-002 | Why Distribution Is Hard                             | ★☆☆        |
| DST-003 | The Distributed Systems Landscape -- A Map           | ★☆☆        |
| DST-004 | The Fallacies of Distributed Computing               | ★☆☆        |
| DST-005 | The Distributed Systems Ecosystem Map                | ★☆☆        |
| DST-006 | CAP Theorem                                          | ★★☆        |
| DST-007 | PACELC                                               | ★★★        |
| DST-008 | Consistency Models                                   | ★★★        |
| DST-009 | Strong Consistency                                   | ★★★        |
| DST-010 | Eventual Consistency                                 | ★★☆        |
| DST-011 | Causal Consistency                                   | ★★★        |
| DST-012 | Linearizability                                      | ★★★        |
| DST-013 | Serializability                                      | ★★★        |
| DST-014 | BASE                                                 | ★★☆        |
| DST-015 | Lamport Clock                                        | ★★★        |
| DST-016 | Vector Clock                                         | ★★★        |
| DST-017 | Clock Skew - Clock Drift                             | ★★☆        |
| DST-018 | Hybrid Logical Clocks (HLC)                          | ★★★        |
| DST-019 | Total Order - Partial Order                          | ★★★        |
| DST-020 | Total Order Broadcast                                | ★★★        |
| DST-021 | Happened-Before                                      | ★★★        |
| DST-022 | Leader Election                                      | ★★★        |
| DST-023 | Raft                                                 | ★★★        |
| DST-024 | Paxos                                                | ★★★        |
| DST-025 | Replication Strategies                               | ★★★        |
| DST-026 | Log Replication                                      | ★★★        |
| DST-027 | State Machine Replication                            | ★★★        |
| DST-028 | Quorum                                               | ★★★        |
| DST-029 | Split Brain                                          | ★★★        |
| DST-030 | Fencing - Epoch                                      | ★★★        |
| DST-031 | Network Partition                                    | ★★☆        |
| DST-032 | Failure Modes                                        | ★★★        |
| DST-033 | Two-Phase Commit (2PC)                               | ★★★        |
| DST-034 | XA Transactions                                      | ★★★        |
| DST-035 | Three-Phase Commit (3PC)                             | ★★★        |
| DST-036 | Optimistic Concurrency Control (Distributed)         | ★★★        |
| DST-037 | Distributed Locking                                  | ★★★        |
| DST-038 | Consistent Hashing                                   | ★★★        |
| DST-039 | Virtual Nodes                                        | ★★★        |
| DST-040 | Gossip Protocol                                      | ★★★        |
| DST-041 | Heartbeat                                            | ★★☆        |
| DST-042 | Circuit Breaker                                      | ★★☆        |
| DST-043 | Bulkhead                                             | ★★☆        |
| DST-044 | Retry with Backoff                                   | ★★☆        |
| DST-045 | Idempotency (Distributed)                            | ★★☆        |
| DST-046 | Timeout                                              | ★★☆        |
| DST-047 | Fallback                                             | ★★☆        |
| DST-048 | Graceful Degradation                                 | ★★★        |
| DST-049 | Saga Pattern                                         | ★★★        |
| DST-050 | Choreography vs Orchestration                        | ★★★        |
| DST-051 | Distributed Tracing                                  | ★★★        |
| DST-052 | Correlation ID                                       | ★★☆        |
| DST-053 | Service Mesh                                         | ★★★        |
| DST-054 | Sidecar Pattern                                      | ★★★        |
| DST-055 | CQRS                                                 | ★★★        |
| DST-056 | Event Sourcing                                       | ★★★        |
| DST-057 | Outbox Pattern                                       | ★★★        |
| DST-058 | Two Generals Problem                                 | ★★★        |
| DST-059 | Byzantine Fault Tolerance                            | ★★★        |
| DST-060 | FLP Impossibility                                    | ★★★        |
| DST-061 | CRDT                                                 | ★★★        |
| DST-062 | Conflict Resolution Strategies                       | ★★★        |
| DST-063 | Anti-Entropy                                         | ★★★        |
| DST-064 | Read Repair                                          | ★★☆        |
| DST-065 | Hinted Handoff                                       | ★★☆        |
| DST-066 | Distributed System Architecture Strategy             | ★★★        |
| DST-067 | Consistency Model Selection Framework                | ★★★        |
| DST-068 | Failure Domain Design                                | ★★★        |
| DST-069 | Distributed Tracing Architecture                     | ★★★        |
| DST-070 | Global Distribution Strategy                         | ★★★        |
| DST-071 | Distributed Consensus Algorithm Design (Raft, Paxos) | ★★★        |
| DST-072 | Distributed Transaction Theory                       | ★★★        |
| DST-073 | Formal Models for Distributed Systems (TLA+)         | ★★★        |
| DST-074 | Research Frontiers in Distributed Systems            | ★★★        |
| DST-075 | Failure-First Thinking                               | ★★★        |
| DST-076 | Consistency Trade-off Framing                        | ★★★        |
| DST-077 | Distribution Necessity Assessment                    | ★★★        |
| DST-078 | Replication Lag                                          | ★★★        |
| DST-079 | Write-Ahead Log (Distributed)                            | ★★★        |
| DST-080 | Distributed Rate Limiting                                | ★★★        |
| DST-081 | Phi Accrual Failure Detector                             | ★★★        |
| DST-082 | Global Sequence Number                                   | ★★★        |
| DST-083 | Distributed Cache Coherence                              | ★★★        |
| DST-084 | Compaction in Distributed Logs                           | ★★★        |
| DST-085 | Deterministic Simulation Testing                         | ★★★        |
