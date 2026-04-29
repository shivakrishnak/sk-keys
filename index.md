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

### Spring & Spring Boot (39 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 103 | IoC (Inversion of Control) | 122 | JoinPoint |
| 104 | DI (Dependency Injection) | 123 | Weaving |
| 105 | ApplicationContext | 124 | DispatcherServlet |
| 106 | BeanFactory | 125 | HandlerMapping |
| 107 | Bean | 126 | Filter vs Interceptor |
| 108 | Bean Lifecycle | 127 | @Transactional |
| 109 | Bean Scope | 128 | Transaction Propagation |
| 110 | BeanPostProcessor | 129 | Transaction Isolation Levels |
| 111 | BeanFactoryPostProcessor | 130 | N+1 Problem |
| 112 | @Autowired | 131 | Lazy vs Eager Loading |
| 113 | @Qualifier / @Primary | 132 | HikariCP |
| 114 | @Configuration / @Bean | 133 | Auto-Configuration |
| 115 | Circular Dependency | 134 | Spring Boot Actuator |
| 116 | CGLIB Proxy | 135 | Spring Boot Startup Lifecycle |
| 117 | JDK Dynamic Proxy | 136 | WebFlux / Reactive |
| 118 | AOP (Aspect-Oriented Programming) | 137 | Mono / Flux |
| 119 | Aspect | 138 | Backpressure |
| 120 | Advice | 139 | |
| 121 | Pointcut | 140 | |

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
| 165 | Failure Modes | 195 | |
| 166 | Timeout | 196 | |
| 167 | Retry | 197 | |
| 168 | Idempotency | 198 | |

### Databases (46 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 199 | ACID | 222 | Write Amplification |
| 200 | Atomicity | 223 | Partitioning (DB) |
| 201 | Consistency (DB) | 224 | Materialized View |
| 202 | Isolation | 225 | Stored Procedure / Trigger |
| 203 | Durability | 226 | Document Store |
| 204 | Transaction | 227 | Key-Value Store |
| 205 | Commit / Rollback / Savepoint | 228 | Column Family |
| 206 | Isolation Levels | 229 | Graph DB |
| 207 | Dirty Read | 230 | Eventual Consistency in NoSQL |
| 208 | Non-Repeatable Read | 231 | CRDTs |
| 209 | Phantom Read | 232 | Cache-Aside |
| 210 | MVCC | 233 | Read-Through |
| 211 | WAL (Write-Ahead Log) | 234 | Write-Through |
| 212 | Redo Log / Undo Log | 235 | Write-Behind |
| 213 | B-Tree | 236 | Cache Invalidation |
| 214 | B+ Tree | 237 | TTL |
| 215 | LSM Tree | 238 | Eviction Policies (LRU, LFU, FIFO) |
| 216 | Index Types | 239 | Cache Stampede / Thundering Herd |
| 217 | Query Planner / Execution Plan | 240 | Negative Caching |
| 218 | EXPLAIN | 241 | |
| 219 | Normalization / Denormalization | 242 | |
| 220 | Foreign Key / Referential Integrity | 243 | |
| 221 | Locking (Row, Table, Gap, Next-Key) | 244 | |

### Messaging & Streaming (20 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 241 | Topic | 253 | Idempotent Producer |
| 242 | Partition (Kafka) | 254 | Transactional Producer |
| 243 | Offset | 255 | Kafka Streams |
| 244 | Consumer Group | 256 | Point-to-Point vs Pub-Sub |
| 245 | Producer | 257 | Message Broker vs Event Bus |
| 246 | Consumer | 258 | Competing Consumers |
| 247 | Broker | 259 | Fan-Out |
| 248 | Replication Factor (Kafka) | 260 | Message Ordering |
| 249 | ISR (In-Sync Replicas) | 261 | |
| 250 | Log Compaction | 262 | |
| 251 | Retention Policy | 263 | |
| 252 | Consumer Lag | 264 | |

### Networking & HTTP (26 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 265 | OSI Model | 280 | REST |
| 266 | TCP | 281 | gRPC |
| 267 | UDP | 282 | Protocol Buffers |
| 268 | QUIC | 283 | WebSocket |
| 269 | TCP Handshake (3-Way) | 284 | Server-Sent Events (SSE) |
| 270 | TCP Teardown | 285 | Long Polling |
| 271 | Congestion Control | 286 | TLS/SSL |
| 272 | Flow Control | 287 | mTLS |
| 273 | DNS | 288 | OAuth2 |
| 274 | CDN | 289 | JWT |
| 275 | HTTP/1.1 | 290 | OIDC |
| 276 | HTTP/2 | 291 | CORS |
| 277 | HTTP/3 | 292 | XSS / CSRF / SQL Injection / SSRF |
| 278 | | 293 | |
| 279 | | 294 | |

### OS & Systems (20 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 295 | Process vs Thread | 308 | Async I/O |
| 296 | Context Switch | 309 | epoll / kqueue |
| 297 | Scheduler / Preemption | 310 | File Descriptor |
| 298 | User Space vs Kernel Space | 311 | Page Cache |
| 299 | System Call (syscall) | 312 | Zero-Copy (sendfile) |
| 300 | Virtual Memory | 313 | NUMA |
| 301 | Paging | 314 | Cache Line |
| 302 | Page Fault | 315 | False Sharing |
| 303 | TLB | 316 | |
| 304 | Memory-Mapped File (mmap) | 317 | |
| 305 | Blocking I/O | 318 | |
| 306 | Non-Blocking I/O | 319 | |

### System Design (34 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 320 | Monolith | 339 | Span / Trace ID |
| 321 | Microservices | 340 | OpenTelemetry |
| 322 | Modular Monolith | 341 | Alerting / Error Budget |
| 323 | Service Mesh | 342 | |
| 324 | Sidecar Pattern | 343 | |
| 325 | API Gateway | 344 | |
| 326 | BFF (Backend for Frontend) | 345 | |
| 327 | CQRS | 346 | |
| 328 | Event Sourcing | 347 | |
| 329 | Hexagonal Architecture | 348 | |
| 330 | Clean Architecture | 349 | |
| 331 | Domain-Driven Design (DDD) | 350 | |
| 332 | Aggregate | 351 | |
| 333 | Bounded Context | 352 | |
| 334 | Ubiquitous Language | 353 | |
| 335 | Vertical Scaling | 354 | |
| 336 | Horizontal Scaling | 355 | |
| 337 | Load Balancing | 356 | |
| 338 | Sticky Sessions | 357 | |

### Data Structures & Algorithms (36 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 358 | Array | 378 | DFS |
| 359 | LinkedList | 379 | Topological Sort |
| 360 | Stack | 380 | Dijkstra |
| 361 | Queue / Deque | 381 | Union-Find |
| 362 | HashMap | 382 | Quicksort |
| 363 | TreeMap | 383 | Mergesort |
| 364 | Heap (Min/Max) | 384 | Timsort |
| 365 | Trie | 385 | Two Pointer |
| 366 | Graph | 386 | Sliding Window |
| 367 | Segment Tree | 387 | Binary Search |
| 368 | Fenwick Tree (BIT) | 388 | Backtracking |
| 369 | Skip List | 389 | Bit Manipulation |
| 370 | Bloom Filter | 390 | |
| 371 | Consistent Hash Ring | 391 | |
| 372 | Time Complexity / Big-O | 392 | |
| 373 | Space Complexity | 393 | |
| 374 | Amortized Analysis | 394 | |
| 375 | Recursion | 395 | |
| 376 | Memoization | 396 | |
| 377 | Tabulation | 397 | |

### Software Design (35 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 398 | SOLID | 418 | Chain of Responsibility |
| 399 | SRP (Single Responsibility) | 419 | State |
| 400 | OCP (Open/Closed) | 420 | Iterator |
| 401 | LSP (Liskov Substitution) | 421 | Mediator |
| 402 | ISP (Interface Segregation) | 422 | Memento |
| 403 | DIP (Dependency Inversion) | 423 | Double-Checked Locking |
| 404 | DRY | 424 | Producer-Consumer |
| 405 | KISS | 425 | |
| 406 | YAGNI | 426 | |
| 407 | Law of Demeter | 427 | |
| 408 | Tell Don't Ask | 428 | |
| 409 | Composition over Inheritance | 429 | |
| 410 | Fail Fast | 430 | |
| 411 | Singleton | 431 | |
| 412 | Factory | 432 | |
| 413 | Abstract Factory | 433 | |
| 414 | Builder | 434 | |
| 415 | Prototype | 435 | |
| 416 | Adapter | 436 | |
| 417 | Decorator | 437 | |

### Testing & Clean Code (18 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 438 | Unit Test | 450 | Abstraction |
| 439 | Integration Test | 451 | Encapsulation |
| 440 | Contract Test | 452 | Polymorphism |
| 441 | E2E Test | 453 | Inheritance |
| 442 | TDD | 454 | Command-Query Separation (CQS) |
| 443 | BDD | 455 | Feature Flags |
| 444 | Mocking | 456 | Technical Debt |
| 445 | Stubbing | 457 | Refactoring |
| 446 | Faking / Spying | 458 | |
| 447 | Test Pyramid | 459 | |
| 448 | Property-Based Testing | 460 | |
| 449 | Mutation Testing | 461 | |

### Cloud & Infrastructure (17 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 462 | Docker | 473 | Multi-Region / Multi-AZ |
| 463 | Container / Image / Layer | 474 | VPC / Subnet / Security Group |
| 464 | Namespace / Cgroups | 475 | Service Mesh (Istio) |
| 465 | Kubernetes Pod | 476 | mTLS / East-West Traffic |
| 466 | Deployment / Service / Ingress | 477 | |
| 467 | ConfigMap / Secret | 478 | |
| 468 | HPA / VPA | 479 | |
| 469 | StatefulSet / DaemonSet | 480 | |
| 470 | Service Discovery | 481 | |
| 471 | IaaS / PaaS / SaaS / FaaS | 482 | |
| 472 | Serverless / Cold Start | 483 | |

### DevOps & SDLC (11 keywords)

| # | Keyword |
|---|---|
| 484 | CI/CD Pipeline |
| 485 | Blue-Green Deployment |
| 486 | Canary Deployment |
| 487 | Rolling Update |
| 488 | GitOps |
| 489 | Infrastructure as Code (IaC) |
| 490 | Immutable Infrastructure |
| 491 | Twelve-Factor App |
| 492 | SRE |
| 493 | Error Budget |
| 494 | Toil |

---

## Quick Links

Use the navigation menu on the left to explore each section. Each topic contains comprehensive guides, best practices, and actionable knowledge.
