---
layout: default
title: Complete Mastery System
nav_order: 1
has_children: true
permalink: /
---

# Technical Dictionary
{: .no_toc }

## 📖 Quick Resources
- **[Setup Status](./STATUS.md)** - Current implementation and deployment info
- **[Technical Dictionary](./docs/TECHNICAL_DICTIONARY.md)** - 500+ technical terms

---

## 📚 Navigation

Explore the Complete Mastery System through the sections below:

### [Java](./docs/java/)
Core JVM concepts, bytecode, memory management, and Java fundamentals.

### [Spring](./docs/spring/)
Enterprise application development with the Spring Framework.

### [Distributed Systems](./docs/distributed-systems/)
Building scalable and reliable systems at scale.

### [Databases](./docs/databases/)
Data persistence, query optimization, and database design.

### [Messaging & Streaming](./docs/messaging-streaming/)
Event-driven architecture and real-time processing.

### [Networking & HTTP](./docs/networking-http/)
Communication protocols and network fundamentals.

### [OS & Systems](./docs/os-systems/)
Operating system concepts and system-level programming.

### [System Design](./docs/system-design/)
Architecting large-scale systems and design patterns.

### [DSA](./docs/dsa/)
Data structures, algorithms, and complexity analysis.

### [Software Design](./docs/software-design/)
Design principles, patterns, and best practices.

### [Cloud & Infrastructure](./docs/cloud-infrastructure/)
Cloud platforms and infrastructure management.

### [DevOps & SDLC](./docs/devops-sdlc/)
Software development lifecycle and DevOps practices.

---

## 📚 Complete Dictionary — All Keywords by Category

### Java & JVM Internals (50 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 001 | JVM | 026 | Parallel GC |
| 002 | JRE | 027 | CMS (Concurrent Mark Sweep) |
| 003 | JDK | 028 | G1GC |
| 004 | Bytecode | 029 | ZGC |
| 005 | Class Loader | 030 | Shenandoah GC |
| 006 | Stack Memory | 031 | GC Tuning |
| 007 | Heap Memory | 032 | GC Logs |
| 008 | Metaspace | 033 | GC Pause |
| 009 | Stack Frame | 034 | Throughput vs Latency (GC) |
| 010 | Operand Stack | 035 | Finalization |
| 011 | Local Variable Table | 036 | JIT Compiler |
| 012 | Object Header | 037 | C1 / C2 Compiler |
| 013 | Escape Analysis | 038 | Tiered Compilation |
| 014 | Memory Barrier | 039 | Method Inlining |
| 015 | Happens-Before | 040 | Deoptimization |
| 016 | GC Roots | 041 | OSR (On-Stack Replacement) |
| 017 | Reference Types | 042 | AOT (Ahead-of-Time Compilation) |
| 018 | Young Generation | 043 | GraalVM |
| 019 | Eden Space | 044 | Native Image |
| 020 | Survivor Space | 045 | TLAB (Thread Local Allocation Buffer) |
| 021 | Minor GC | 046 | Safepoint |
| 022 | Major GC | 047 | Card Table |
| 023 | Full GC | 048 | Write Barrier |
| 024 | Stop-The-World (STW) | 049 | Remembered Set |
| 025 | Serial GC | 050 | String Pool / String Interning |

### Java Language & Concurrency (52 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 051 | Autoboxing / Unboxing | 077 | ReadWriteLock |
| 052 | Integer Cache | 078 | StampedLock |
| 053 | Generics | 079 | ThreadLocal |
| 054 | Type Erasure | 080 | InheritableThreadLocal |
| 055 | Bounded Wildcards | 081 | Deadlock |
| 056 | Covariance / Contravariance | 082 | Livelock |
| 057 | Varargs | 083 | Starvation |
| 058 | Reflection | 084 | Race Condition |
| 059 | Annotation Processing (APT) | 085 | CAS (Compare-And-Swap) |
| 060 | Serialization / Deserialization | 086 | Spin Lock |
| 061 | SerialVersionUID | 087 | Optimistic Locking |
| 062 | Records (Java 16+) | 088 | Executor |
| 063 | Sealed Classes (Java 17+) | 089 | ExecutorService |
| 064 | Pattern Matching (Java 21+) | 090 | ThreadPoolExecutor |
| 065 | invokedynamic | 091 | ForkJoinPool |
| 066 | Thread | 092 | Virtual Threads (Project Loom) |
| 067 | Runnable | 093 | Carrier Thread |
| 068 | Callable | 094 | Continuation |
| 069 | Future | 095 | Semaphore |
| 070 | CompletableFuture | 096 | CountDownLatch |
| 071 | Thread Lifecycle | 097 | CyclicBarrier |
| 072 | Thread States | 098 | Phaser |
| 073 | synchronized | 099 | BlockingQueue |
| 074 | volatile | 100 | ConcurrentHashMap |
| 075 | wait / notify / notifyAll | 101 | CopyOnWriteArrayList |
| 076 | ReentrantLock | 102 | Java Memory Model (JMM) |

### Spring & Spring Boot (37 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 103 | IoC (Inversion of Control) | 120 | Advice |
| 104 | DI (Dependency Injection) | 121 | Pointcut |
| 105 | ApplicationContext | 122 | JoinPoint |
| 106 | BeanFactory | 123 | Weaving |
| 107 | Bean | 124 | DispatcherServlet |
| 108 | Bean Lifecycle | 125 | HandlerMapping |
| 109 | Bean Scope | 126 | Filter vs Interceptor |
| 110 | BeanPostProcessor | 127 | @Transactional |
| 111 | BeanFactoryPostProcessor | 128 | Transaction Propagation |
| 112 | @Autowired | 129 | Transaction Isolation Levels |
| 113 | @Qualifier / @Primary | 130 | N+1 Problem |
| 114 | @Configuration / @Bean | 131 | Lazy vs Eager Loading |
| 115 | Circular Dependency | 132 | HikariCP |
| 116 | CGLIB Proxy | 133 | Auto-Configuration |
| 117 | JDK Dynamic Proxy | 134 | Spring Boot Actuator |
| 118 | AOP (Aspect-Oriented Programming) | 135 | Spring Boot Startup Lifecycle |
| 119 | Aspect | 136 | WebFlux / Reactive |
|  |  | 137 | Mono / Flux |
|  |  | 138 | Backpressure |

### Distributed Systems (57 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 139 | CAP Theorem | 169 | Circuit Breaker |
| 140 | PACELC | 170 | Bulkhead |
| 141 | Consistency | 171 | Rate Limiter |
| 142 | Availability | 172 | Retry with Backoff |
| 143 | Partition Tolerance | 173 | Graceful Degradation |
| 144 | Strong Consistency | 174 | Health Check / Heartbeat |
| 145 | Eventual Consistency | 175 | Partitioning (Horizontal / Vertical) |
| 146 | Causal Consistency | 176 | Sharding |
| 147 | Linearizability | 177 | Shard Key |
| 148 | Serializability | 178 | Hot Shard |
| 149 | BASE | 179 | Consistent Hashing |
| 150 | ACID | 180 | Virtual Nodes |
| 151 | Lamport Clock | 181 | Rebalancing |
| 152 | Vector Clock | 182 | Synchronous vs Asynchronous |
| 153 | Clock Skew / Clock Drift | 183 | Request-Response |
| 154 | Happened-Before | 184 | Pub/Sub |
| 155 | Total Order / Partial Order | 185 | Event-Driven Architecture |
| 156 | Leader Election | 186 | Message Queue |
| 157 | Raft | 187 | Dead Letter Queue (DLQ) |
| 158 | Paxos | 188 | Exactly-Once Delivery |
| 159 | Replication (Sync vs Async) | 189 | At-Least-Once Delivery |
| 160 | Log Replication | 190 | At-Most-Once Delivery |
| 161 | State Machine Replication | 191 | Saga Pattern |
| 162 | Quorum | 192 | Choreography vs Orchestration |
| 163 | Split Brain | 193 | Outbox Pattern |
| 164 | Fencing / Epoch | 194 | Two-Phase Commit (2PC) |
| 165 | Failure Modes |  |  |
| 166 | Timeout |  |  |
| 167 | Retry |  |  |
| 168 | Idempotency |  |  |

### Databases (46 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 195 | ACID | 220 | Prepared Statements |
| 196 | Atomicity | 221 | Read Replica |
| 197 | Consistency (DB) | 222 | Write Amplification |
| 198 | Isolation | 223 | Partitioning (DB) |
| 199 | Durability | 224 | Materialized View |
| 200 | Transaction | 225 | Stored Procedure / Trigger |
| 201 | Commit / Rollback / Savepoint | 226 | Document Store |
| 202 | Isolation Levels | 227 | Key-Value Store |
| 203 | Dirty Read | 228 | Column Family |
| 204 | Non-Repeatable Read | 229 | Graph DB |
| 205 | Phantom Read | 230 | Eventual Consistency in NoSQL |
| 206 | MVCC | 231 | CRDTs |
| 207 | WAL (Write-Ahead Log) | 232 | Cache-Aside |
| 208 | Redo Log / Undo Log | 233 | Read-Through |
| 209 | B-Tree | 234 | Write-Through |
| 210 | B+ Tree | 235 | Write-Behind |
| 211 | LSM Tree | 236 | Cache Invalidation |
| 212 | Index Types | 237 | TTL |
| 213 | Query Planner / Execution Plan | 238 | Eviction Policies (LRU, LFU, FIFO) |
| 214 | EXPLAIN | 239 | Cache Stampede / Thundering Herd |
| 215 | Normalization / Denormalization | 240 | Negative Caching |
| 216 | Foreign Key / Referential Integrity |  |  |
| 217 | Locking (Row, Table, Gap, Next-Key) |  |  |
| 218 | Deadlock Detection |  |  |
| 219 | Connection Pooling |  |  |

### Messaging & Streaming (21 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 241 | Topic | 252 | Consumer Lag |
| 242 | Partition (Kafka) | 253 | Idempotent Producer |
| 243 | Offset | 254 | Transactional Producer |
| 244 | Consumer Group | 255 | Kafka Streams |
| 245 | Producer | 256 | Point-to-Point vs Pub-Sub |
| 246 | Consumer | 257 | Message Broker vs Event Bus |
| 247 | Broker | 258 | Competing Consumers |
| 248 | Replication Factor (Kafka) | 259 | Fan-Out |
| 249 | ISR (In-Sync Replicas) | 260 | Message Ordering |
| 250 | Log Compaction |  |  |
| 251 | Retention Policy |  |  |

### Networking & HTTP (26 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 261 | OSI Model | 274 | REST |
| 262 | TCP | 275 | gRPC |
| 263 | UDP | 276 | Protocol Buffers |
| 264 | QUIC | 277 | WebSocket |
| 265 | TCP Handshake (3-Way) | 278 | Server-Sent Events (SSE) |
| 266 | TCP Teardown | 279 | Long Polling |
| 267 | Congestion Control | 280 | TLS/SSL |
| 268 | Flow Control | 281 | mTLS |
| 269 | DNS | 282 | OAuth2 |
| 270 | CDN | 283 | JWT |
| 271 | HTTP/1.1 | 284 | OIDC |
| 272 | HTTP/2 | 285 | CORS |
| 273 | HTTP/3 | 286 | XSS / CSRF / SQL Injection / SSRF |

### OS & Systems (20 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 287 | Process vs Thread | 297 | Blocking I/O |
| 288 | Context Switch | 298 | Non-Blocking I/O |
| 289 | Scheduler / Preemption | 299 | Async I/O |
| 290 | User Space vs Kernel Space | 300 | epoll / kqueue |
| 291 | System Call (syscall) | 301 | File Descriptor |
| 292 | Virtual Memory | 302 | Page Cache |
| 293 | Paging | 303 | Zero-Copy (sendfile) |
| 294 | Page Fault | 304 | NUMA |
| 295 | TLB | 305 | Cache Line |
| 296 | Memory-Mapped File (mmap) | 306 | False Sharing |

### System Design (34 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 307 | Monolith | 325 | Sticky Sessions |
| 308 | Microservices | 326 | Token Bucket / Leaky Bucket |
| 309 | Modular Monolith | 327 | Autoscaling |
| 310 | Service Mesh | 328 | SLA / SLO / SLI |
| 311 | Sidecar Pattern | 329 | MTTR / MTBF |
| 312 | API Gateway | 330 | RTO / RPO |
| 313 | BFF (Backend for Frontend) | 331 | Redundancy / Failover |
| 314 | CQRS | 332 | Active-Active / Active-Passive |
| 315 | Event Sourcing | 333 | Chaos Engineering |
| 316 | Hexagonal Architecture | 334 | Graceful Shutdown |
| 317 | Clean Architecture | 335 | Logging (Structured) |
| 318 | Domain-Driven Design (DDD) | 336 | Metrics |
| 319 | Aggregate | 337 | Distributed Tracing |
| 320 | Bounded Context | 338 | Span / Trace ID |
| 321 | Ubiquitous Language | 339 | OpenTelemetry |
| 322 | Vertical Scaling | 340 | Alerting / Error Budget |
| 323 | Horizontal Scaling |  |  |
| 324 | Load Balancing |  |  |

### Data Structures & Algorithms (36 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 341 | Array | 359 | Memoization |
| 342 | LinkedList | 360 | Tabulation |
| 343 | Stack | 361 | Divide and Conquer |
| 344 | Queue / Deque | 362 | Greedy |
| 345 | HashMap | 363 | Dynamic Programming |
| 346 | TreeMap | 364 | BFS |
| 347 | Heap (Min/Max) | 365 | DFS |
| 348 | Trie | 366 | Topological Sort |
| 349 | Graph | 367 | Dijkstra |
| 350 | Segment Tree | 368 | Union-Find |
| 351 | Fenwick Tree (BIT) | 369 | Quicksort |
| 352 | Skip List | 370 | Mergesort |
| 353 | Bloom Filter | 371 | Timsort |
| 354 | Consistent Hash Ring | 372 | Two Pointer |
| 355 | Time Complexity / Big-O | 373 | Sliding Window |
| 356 | Space Complexity | 374 | Binary Search |
| 357 | Amortized Analysis | 375 | Backtracking |
| 358 | Recursion | 376 | Bit Manipulation |

### Software Design (35 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 377 | SOLID | 401 | Strategy |
| 378 | SRP (Single Responsibility) | 402 | Observer |
| 379 | OCP (Open/Closed) | 403 | Command |
| 380 | LSP (Liskov Substitution) | 404 | Template Method |
| 381 | ISP (Interface Segregation) | 405 | Chain of Responsibility |
| 382 | DIP (Dependency Inversion) | 406 | State |
| 383 | DRY | 407 | Iterator |
| 384 | KISS | 408 | Mediator |
| 385 | YAGNI | 409 | Memento |
| 386 | Law of Demeter | 410 | Double-Checked Locking |
| 387 | Tell Don't Ask | 411 | Producer-Consumer |
| 388 | Composition over Inheritance |  |  |
| 389 | Fail Fast |  |  |
| 390 | Singleton |  |  |
| 391 | Factory |  |  |
| 392 | Abstract Factory |  |  |
| 393 | Builder |  |  |
| 394 | Prototype |  |  |
| 395 | Adapter |  |  |
| 396 | Decorator |  |  |
| 397 | Facade |  |  |
| 398 | Proxy |  |  |
| 399 | Composite |  |  |
| 400 | Flyweight |  |  |

### Testing & Clean Code (18 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 412 | Unit Test | 423 | Mutation Testing |
| 413 | Integration Test | 424 | Cohesion |
| 414 | Contract Test | 425 | Coupling |
| 415 | E2E Test | 426 | Abstraction |
| 416 | TDD | 427 | Encapsulation |
| 417 | BDD | 428 | Polymorphism |
| 418 | Mocking | 429 | Inheritance |
| 419 | Stubbing | 430 | Command-Query Separation (CQS) |
| 420 | Faking / Spying | 431 | Feature Flags |
| 421 | Test Pyramid | 432 | Technical Debt |
| 422 | Property-Based Testing | 433 | Refactoring |

### Cloud & Infrastructure (17 keywords)
| # | Keyword | # | Keyword |
|---|---|---|---|
| 434 | Docker | 443 | IaaS / PaaS / SaaS / FaaS |
| 435 | Container / Image / Layer | 444 | Serverless / Cold Start |
| 436 | Namespace / Cgroups | 445 | Object Storage |
| 437 | Kubernetes Pod | 446 | Multi-Region / Multi-AZ |
| 438 | Deployment / Service / Ingress | 447 | VPC / Subnet / Security Group |
| 439 | ConfigMap / Secret | 448 | Service Mesh (Istio) |
| 440 | HPA / VPA | 449 | mTLS / East-West Traffic |
| 441 | StatefulSet / DaemonSet |  |  |
| 442 | Service Discovery |  |  |

### DevOps & SDLC (10 keywords)
| # | Keyword |
|---|---|
| 450 | CI/CD Pipeline |
| 451 | Blue-Green Deployment |
| 452 | Canary Deployment |
| 453 | Rolling Update |
| 454 | GitOps |
| 455 | Infrastructure as Code (IaC) |
| 456 | Immutable Infrastructure |
| 457 | Twelve-Factor App |
| 458 | SRE |
| 459 | Error Budget |
| 460 | Toil |

---

## Quick Links

Use the navigation menu on the left to explore each section. Each topic contains comprehensive guides, best practices, and actionable knowledge.
