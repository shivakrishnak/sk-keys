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

### [Java & JVM Internals](./docs/Java/)
JVM architecture, bytecode, class loading, memory management, GC algorithms, JIT compilation.

### [Java Language](./docs/Java%20Language/)
Generics, type erasure, reflection, records, sealed classes, and modern Java language features.

### [Java Concurrency](./docs/Java%20Concurrency/)
Threads, locks, synchronization primitives, executors, virtual threads (Project Loom), and the Java Memory Model.

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

### [Testing](./docs/Testing/)
Testing strategies and methodologies — Unit, Integration, TDD, BDD, Mutation Testing.

### [Clean Code](./docs/Clean Code/)
Clean code principles — Cohesion, Coupling, Abstraction, Refactoring, Technical Debt.

### [Cloud & Infrastructure](./docs/cloud-infrastructure/)
Cloud platforms and infrastructure management.

### [DevOps & SDLC](./docs/DevOps & SDLC/)
Software development lifecycle and DevOps practices — CI/CD, GitOps, SRE, IaC.

### [HTML](./docs/HTML/)
HTML document structure, semantics, accessibility, and browser rendering.

### [CSS](./docs/CSS/)
Styling, layout, responsive design, and modern CSS features.

### [JavaScript](./docs/JavaScript/)
JS engine, event loop, async patterns, and modern language features.

### [TypeScript](./docs/TypeScript/)
Static typing, type system, generics, and TypeScript tooling.

### [React](./docs/React/)
React fundamentals, hooks, performance, and ecosystem.

### [Node.js](./docs/Node.js/)
Server-side JavaScript, event loop, streams, and Node ecosystem.

### [npm](./docs/npm/)
Package management, dependency resolution, and monorepo tooling.

### [Webpack & Build Tools](./docs/Webpack/)
Bundling, code splitting, transpilation, and build optimization.

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

### Java Language (15 keywords)

| # | Keyword |
|---|---|
| 051 | [Autoboxing / Unboxing](<docs/Java Language/051 — Autoboxing-Unboxing.md>) |
| 052 | [Integer Cache](<docs/Java Language/052 — Integer Cache.md>) |
| 053 | [Generics](<docs/Java Language/053 — Generics.md>) |
| 054 | [Type Erasure](<docs/Java Language/054 — Type Erasure.md>) |
| 055 | [Bounded Wildcards](<docs/Java Language/055 — Bounded Wildcards.md>) |
| 056 | [Covariance / Contravariance](<docs/Java Language/056 — Covariance-Contravariance.md>) |
| 057 | [Varargs](<docs/Java Language/057 — Varargs.md>) |
| 058 | [Reflection](<docs/Java Language/058 — Reflection.md>) |
| 059 | [Annotation Processing (APT)](<docs/Java Language/059 — Annotation Processing (APT).md>) |
| 060 | [Serialization / Deserialization](<docs/Java Language/060 — Serialization-Deserialization.md>) |
| 061 | [SerialVersionUID](<docs/Java Language/061 — SerialVersionUID.md>) |
| 062 | [Records (Java 16+)](<docs/Java Language/062 — Records (Java 16+).md>) |
| 063 | Sealed Classes (Java 17+) |
| 064 | Pattern Matching (Java 21+) |
| 065 | invokedynamic |

### Java Concurrency (37 keywords)

| # | Keyword |
|---|---|
| 066 | Thread |
| 067 | Runnable |
| 068 | Callable |
| 069 | Future |
| 070 | CompletableFuture |
| 071 | Thread Lifecycle |
| 072 | Thread States |
| 073 | synchronized |
| 074 | volatile |
| 075 | wait / notify / notifyAll |
| 076 | ReentrantLock |
| 077 | ReadWriteLock |
| 078 | StampedLock |
| 079 | ThreadLocal |
| 080 | InheritableThreadLocal |
| 081 | Deadlock |
| 082 | Livelock |
| 083 | Starvation |
| 084 | Race Condition |
| 085 | CAS (Compare-And-Swap) |
| 086 | Spin Lock |
| 087 | Optimistic Locking |
| 088 | Executor |
| 089 | ExecutorService |
| 090 | ThreadPoolExecutor |
| 091 | ForkJoinPool |
| 092 | Virtual Threads (Project Loom) |
| 093 | Carrier Thread |
| 094 | Continuation |
| 095 | Semaphore |
| 096 | CountDownLatch |
| 097 | CyclicBarrier |
| 098 | Phaser |
| 099 | BlockingQueue |
| 100 | ConcurrentHashMap |
| 101 | CopyOnWriteArrayList |
| 102 | Java Memory Model (JMM) |

### Spring & Spring Boot (36 keywords)

| # | Keyword |
|---|---|
| 103 | [IoC (Inversion of Control)](<docs/Spring/103 — IoC (Inversion of Control).md>) |
| 104 | [DI (Dependency Injection)](<docs/Spring/104 — DI (Dependency Injection).md>) |
| 105 | [ApplicationContext](<docs/Spring/105 — ApplicationContext.md>) |
| 106 | [BeanFactory](<docs/Spring/106 — BeanFactory.md>) |
| 107 | [Bean](<docs/Spring/107 — Bean.md>) |
| 108 | [Bean Lifecycle](<docs/Spring/108 — Bean Lifecycle.md>) |
| 109 | [Bean Scope](<docs/Spring/109 — Bean Scope.md>) |
| 110 | [BeanPostProcessor](<docs/Spring/110 — BeanPostProcessor.md>) |
| 111 | [BeanFactoryPostProcessor](<docs/Spring/111 — BeanFactoryPostProcessor.md>) |
| 112 | [@Autowired](<docs/Spring/112 — @Autowired.md>) |
| 113 | [@Qualifier / @Primary](<docs/Spring/113 — @Qualifier @Primary.md>) |
| 114 | [@Configuration / @Bean](<docs/Spring/114 — @Configuration @Bean.md>) |
| 115 | [Circular Dependency](<docs/Spring/115 — Circular Dependency.md>) |
| 116 | [CGLIB Proxy](<docs/Spring/116 — CGLIB Proxy.md>) |
| 117 | [JDK Dynamic Proxy](<docs/Spring/117 — JDK Dynamic Proxy.md>) |
| 118 | [AOP (Aspect-Oriented Programming)](<docs/Spring/118 — AOP (Aspect-Oriented Programming).md>) |
| 119 | [Aspect](<docs/Spring/119 — Aspect.md>) |
| 120 | [Advice](<docs/Spring/120 — Advice.md>) |
| 121 | [Pointcut](<docs/Spring/121 — Pointcut.md>) |
| 122 | [JoinPoint](<docs/Spring/122 — JoinPoint.md>) |
| 123 | [Weaving](<docs/Spring/123 — Weaving.md>) |
| 124 | [DispatcherServlet](<docs/Spring/124 — DispatcherServlet.md>) |
| 125 | [HandlerMapping](<docs/Spring/125 — HandlerMapping.md>) |
| 126 | [Filter vs Interceptor](<docs/Spring/126 — Filter vs Interceptor.md>) |
| 127 | [@Transactional](<docs/Spring/127 — @Transactional.md>) |
| 128 | [Transaction Propagation](<docs/Spring/128 — Transaction Propagation.md>) |
| 129 | [Transaction Isolation Levels](<docs/Spring/129 — Transaction Isolation Levels.md>) |
| 130 | [N+1 Problem](<docs/Spring/130 — N+1 Problem.md>) |
| 131 | [Lazy vs Eager Loading](<docs/Spring/131 — Lazy vs Eager Loading.md>) |
| 132 | [HikariCP](<docs/Spring/132 — HikariCP.md>) |
| 133 | [Auto-Configuration](<docs/Spring/133 — Auto-Configuration.md>) |
| 134 | [Spring Boot Actuator](<docs/Spring/134 — Spring Boot Actuator.md>) |
| 135 | [Spring Boot Startup Lifecycle](<docs/Spring/135 — Spring Boot Startup Lifecycle.md>) |
| 136 | [WebFlux / Reactive](<docs/Spring/136 — WebFlux Reactive.md>) |
| 137 | [Mono / Flux](<docs/Spring/137 — Mono Flux.md>) |
| 138 | [Backpressure](<docs/Spring/138 — Backpressure.md>) |

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

### Testing (12 keywords)

| # | Keyword |
|---|---|
| 412 | [Unit Test](<docs/Testing/412 — Unit Test.md>) |
| 413 | [Integration Test](<docs/Testing/413 — Integration Test.md>) |
| 414 | [Contract Test](<docs/Testing/414 — Contract Test.md>) |
| 415 | [E2E Test](<docs/Testing/415 — E2E Test.md>) |
| 416 | [TDD](<docs/Testing/416 — TDD.md>) |
| 417 | [BDD](<docs/Testing/417 — BDD.md>) |
| 418 | [Mocking](<docs/Testing/418 — Mocking.md>) |
| 419 | [Stubbing](<docs/Testing/419 — Stubbing.md>) |
| 420 | [Faking / Spying](<docs/Testing/420 — Faking-Spying.md>) |
| 421 | [Test Pyramid](<docs/Testing/421 — Test Pyramid.md>) |
| 422 | [Property-Based Testing](<docs/Testing/422 — Property-Based Testing.md>) |
| 423 | [Mutation Testing](<docs/Testing/423 — Mutation Testing.md>) |

### Clean Code (10 keywords)

| # | Keyword |
|---|---|
| 424 | [Cohesion](<docs/Clean Code/424 — Cohesion.md>) |
| 425 | [Coupling](<docs/Clean Code/425 — Coupling.md>) |
| 426 | [Abstraction](<docs/Clean Code/426 — Abstraction.md>) |
| 427 | [Encapsulation](<docs/Clean Code/427 — Encapsulation.md>) |
| 428 | [Polymorphism](<docs/Clean Code/428 — Polymorphism.md>) |
| 429 | [Inheritance](<docs/Clean Code/429 — Inheritance.md>) |
| 430 | [Command-Query Separation (CQS)](<docs/Clean Code/430 — Command-Query Separation (CQS).md>) |
| 431 | [Feature Flags](<docs/Clean Code/431 — Feature Flags.md>) |
| 432 | [Technical Debt](<docs/Clean Code/432 — Technical Debt.md>) |
| 433 | [Refactoring](<docs/Clean Code/433 — Refactoring.md>) |

### Cloud & Infrastructure (16 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 434 | Docker | 442 | Service Discovery |
| 435 | Container / Image / Layer | 443 | IaaS / PaaS / SaaS / FaaS |
| 436 | Namespace / Cgroups | 444 | Serverless / Cold Start |
| 437 | Kubernetes Pod | 445 | Object Storage |
| 438 | Deployment / Service / Ingress | 446 | Multi-Region / Multi-AZ |
| 439 | ConfigMap / Secret | 447 | VPC / Subnet / Security Group |
| 440 | HPA / VPA | 448 | Service Mesh (Istio) |
| 441 | StatefulSet / DaemonSet | 449 | mTLS / East-West Traffic |

### DevOps & SDLC (11 keywords)

| # | Keyword |
|---|---|
| 450 | [CI/CD Pipeline](<docs/DevOps & SDLC/450 — CI-CD Pipeline.md>) |
| 451 | [Blue-Green Deployment](<docs/DevOps & SDLC/451 — Blue-Green Deployment.md>) |
| 452 | [Canary Deployment](<docs/DevOps & SDLC/452 — Canary Deployment.md>) |
| 453 | [Rolling Update](<docs/DevOps & SDLC/453 — Rolling Update.md>) |
| 454 | [GitOps](<docs/DevOps & SDLC/454 — GitOps.md>) |
| 455 | [Infrastructure as Code (IaC)](<docs/DevOps & SDLC/455 — Infrastructure as Code (IaC).md>) |
| 456 | [Immutable Infrastructure](<docs/DevOps & SDLC/456 — Immutable Infrastructure.md>) |
| 457 | [Twelve-Factor App](<docs/DevOps & SDLC/457 — Twelve-Factor App.md>) |
| 458 | [SRE](<docs/DevOps & SDLC/458 — SRE.md>) |
| 459 | [Error Budget](<docs/DevOps & SDLC/459 — Error Budget.md>) |
| 460 | [Toil](<docs/DevOps & SDLC/460 — Toil.md>) |

---

### HTML (30 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 461 | HTML Document Structure | 476 | Web Accessibility (ARIA) |
| 462 | DOCTYPE | 477 | tabindex |
| 463 | DOM (Document Object Model) | 478 | srcset / picture (Responsive Images) |
| 464 | Semantic HTML | 479 | lazy loading (loading=lazy) |
| 465 | Block vs Inline Elements | 480 | Template Element |
| 466 | HTML Attributes vs Properties | 481 | Shadow DOM |
| 467 | Forms & Input Types | 482 | Web Components |
| 468 | Form Validation (Native) | 483 | Custom Elements |
| 469 | data- Attributes | 484 | HTML Parsing & Render Blocking |
| 470 | Meta Tags | 485 | defer vs async (Script Loading) |
| 471 | Viewport Meta Tag | 486 | Critical Rendering Path |
| 472 | HTML Entities | 487 | Reflow vs Repaint |
| 473 | iframe | 488 | Content Security Policy (CSP) |
| 474 | Canvas | 489 | Preload / Prefetch / Preconnect |
| 475 | SVG in HTML | 490 | HTTP Cache Headers (Cache-Control) |

### CSS (50 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 491 | CSS Specificity | 516 | CSS Modules |
| 492 | CSS Cascade | 517 | CSS-in-JS |
| 493 | CSS Inheritance | 518 | Styled Components |
| 494 | Box Model | 519 | Tailwind CSS |
| 495 | Box Sizing | 520 | SASS / SCSS |
| 496 | Display Property | 521 | PostCSS |
| 497 | Position (static, relative, absolute, fixed, sticky) | 522 | CSS Reset vs Normalize |
| 498 | Flexbox | 523 | Logical Properties |
| 499 | CSS Grid | 524 | CSS Subgrid |
| 500 | Float & Clear (Legacy) | 525 | Container Queries |
| 501 | CSS Variables (Custom Properties) | 526 | :has() Selector |
| 502 | Pseudo-classes | 527 | CSS Layers (@layer) |
| 503 | Pseudo-elements | 528 | Font Loading (font-display) |
| 504 | CSS Selectors (Combinators) | 529 | CSS Performance (Paint, Layout, Composite) |
| 505 | Media Queries | 530 | Critical CSS |
| 506 | Responsive Design | 531 | CSS Clamp / min / max |
| 507 | Mobile-First Design | 532 | Aspect Ratio |
| 508 | CSS Units (px, em, rem, vw, vh, %) | 533 | Scroll Snap |
| 509 | Stacking Context / z-index | 534 | CSS Nesting (Native) |
| 510 | CSS Transitions | 535 | Dark Mode (prefers-color-scheme) |
| 511 | CSS Animations (@keyframes) | 536 | Reduced Motion (prefers-reduced-motion) |
| 512 | CSS Transform | 537 | CSS Scope |
| 513 | will-change | 538 | Houdini (Paint API) |
| 514 | CSS Containment | 539 | CSS Anchor Positioning |
| 515 | BEM (Block Element Modifier) | 540 | View Transitions API |

### JavaScript (80 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 541 | JavaScript Engine (V8) | 581 | Set |
| 542 | Call Stack | 582 | Destructuring |
| 543 | Heap (JS) | 583 | Spread / Rest Operator |
| 544 | Event Loop | 584 | Optional Chaining (?.) |
| 545 | Task Queue (Macrotask) | 585 | Nullish Coalescing (??) |
| 546 | Microtask Queue | 586 | Short-Circuit Evaluation |
| 547 | Web APIs | 587 | Type Coercion |
| 548 | var / let / const | 588 | == vs === |
| 549 | Hoisting | 589 | typeof / instanceof |
| 550 | Temporal Dead Zone (TDZ) | 590 | Truthy / Falsy |
| 551 | Scope (Global, Function, Block) | 591 | Object.freeze / seal |
| 552 | Closure | 592 | Proxy / Reflect |
| 553 | Lexical Environment | 593 | Property Descriptor |
| 554 | Prototype Chain | 594 | Getter / Setter |
| 555 | Prototypal Inheritance | 595 | Class (ES6+) |
| 556 | this keyword | 596 | Class Inheritance |
| 557 | Binding (call, apply, bind) | 597 | Private Fields (#) |
| 558 | Arrow Functions | 598 | Static Methods / Properties |
| 559 | Execution Context | 599 | Modules (ESM) |
| 560 | IIFE | 600 | CommonJS (require) |
| 561 | First-Class Functions | 601 | Dynamic Import |
| 562 | Higher-Order Functions | 602 | Tree Shaking |
| 563 | Pure Functions | 603 | Memory Leaks (JS) |
| 564 | Side Effects | 604 | Garbage Collection (JS) |
| 565 | Immutability | 605 | Debounce |
| 566 | Currying | 606 | Throttle |
| 567 | Partial Application | 607 | requestAnimationFrame |
| 568 | Memoization (JS) | 608 | Web Workers |
| 569 | Callback | 609 | SharedArrayBuffer |
| 570 | Callback Hell | 610 | Atomics |
| 571 | Promise | 611 | Service Worker |
| 572 | Promise Chaining | 612 | IndexedDB |
| 573 | Promise.all / race / allSettled / any | 613 | localStorage / sessionStorage |
| 574 | async / await | 614 | Fetch API |
| 575 | Error Handling (try/catch/finally) | 615 | AbortController |
| 576 | Generator Functions | 616 | Structured Clone |
| 577 | Iterator Protocol | 617 | Intl API |
| 578 | Symbol | 618 | Temporal API |
| 579 | WeakMap / WeakSet | 619 | BigInt |
| 580 | Map vs Object | 620 | Top-Level Await |

### TypeScript (50 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 621 | TypeScript vs JavaScript | 646 | Type Guard |
| 622 | Static Typing | 647 | Assertion Functions |
| 623 | Type Inference | 648 | as (Type Assertion) |
| 624 | Type Annotation | 649 | satisfies Operator |
| 625 | Primitive Types | 650 | Enum |
| 626 | any / unknown / never | 651 | Const Enum |
| 627 | void | 652 | Namespace |
| 628 | Union Types | 653 | Declaration Merging |
| 629 | Intersection Types | 654 | Module Augmentation |
| 630 | Literal Types | 655 | Declaration Files (.d.ts) |
| 631 | Type Alias | 656 | tsconfig.json |
| 632 | Interface | 657 | strict Mode |
| 633 | Type Alias vs Interface | 658 | Structural Typing (Duck Typing) |
| 634 | Optional Properties | 659 | Excess Property Checking |
| 635 | Readonly | 660 | Index Signatures |
| 636 | Generics (TS) | 661 | Function Overloading (TS) |
| 637 | Generic Constraints | 662 | Decorators (TS) |
| 638 | Utility Types (Partial, Required, Pick, Omit) | 663 | Abstract Classes |
| 639 | Record Type | 664 | Access Modifiers (public, private, protected) |
| 640 | Mapped Types | 665 | ReturnType / Parameters Utility |
| 641 | Conditional Types | 666 | Awaited Utility Type |
| 642 | infer Keyword | 667 | Variance (Covariance / Contravariance in TS) |
| 643 | Template Literal Types | 668 | keyof / typeof |
| 644 | Discriminated Union | 669 | Type Widening / Narrowing |
| 645 | Type Narrowing | 670 | TS Compiler Pipeline (tsc) |

### React (60 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 671 | JSX | 701 | Lifting State Up |
| 672 | Component (Function vs Class) | 702 | Prop Drilling |
| 673 | Props | 703 | Render Props |
| 674 | State | 704 | Higher-Order Components (HOC) |
| 675 | Controlled vs Uncontrolled Components | 705 | Compound Components |
| 676 | useState | 706 | Forwarding Refs |
| 677 | useEffect | 707 | Imperative Handle (useImperativeHandle) |
| 678 | useRef | 708 | Strict Mode |
| 679 | useContext | 709 | React DevTools |
| 680 | useReducer | 710 | React Router |
| 681 | useMemo | 711 | Client-Side Routing |
| 682 | useCallback | 712 | Code Splitting |
| 683 | useLayoutEffect | 713 | Server Components (RSC) |
| 684 | useId | 714 | Server Actions |
| 685 | useTransition | 715 | Hydration |
| 686 | useDeferredValue | 716 | SSR (Server-Side Rendering) |
| 687 | Custom Hooks | 717 | SSG (Static Site Generation) |
| 688 | Context API | 718 | ISR (Incremental Static Regeneration) |
| 689 | React.memo | 719 | Next.js App Router |
| 690 | Virtual DOM | 720 | Streaming SSR |
| 691 | Reconciliation | 721 | React Query / TanStack Query |
| 692 | Diffing Algorithm | 722 | Zustand |
| 693 | Fiber Architecture | 723 | Redux Toolkit |
| 694 | Concurrent Mode | 724 | Jotai / Recoil (Atomic State) |
| 695 | Suspense | 725 | Form Libraries (React Hook Form, Formik) |
| 696 | Lazy Loading (React.lazy) | 726 | Testing React (RTL, Vitest) |
| 697 | Error Boundaries | 727 | Storybook |
| 698 | Portals | 728 | React Performance Profiling |
| 699 | Fragments | 729 | React 19 Features |
| 700 | Keys in Lists | 730 | use() Hook |

### Node.js (60 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 731 | Node.js Architecture | 761 | CORS in Node |
| 732 | V8 Engine in Node | 762 | Helmet.js (Security) |
| 733 | libuv | 763 | Database Connections (Node + Postgres/Mongo) |
| 734 | Node Event Loop | 764 | ORM / Query Builder (Prisma, Knex) |
| 735 | Phases of Event Loop (Node) | 765 | Caching in Node (Redis) |
| 736 | setImmediate vs setTimeout vs process.nextTick | 766 | WebSockets in Node |
| 737 | Non-Blocking I/O | 767 | File Uploads (Multer) |
| 738 | Streams | 768 | Process Management (PM2) |
| 739 | Readable / Writable / Transform Streams | 769 | Graceful Shutdown (Node) |
| 740 | Backpressure (Node Streams) | 770 | Memory Leaks in Node |
| 741 | Buffer | 771 | Node.js Profiling (--inspect) |
| 742 | EventEmitter | 772 | Fastify |
| 743 | fs Module | 773 | NestJS |
| 744 | path Module | 774 | Dependency Injection (NestJS) |
| 745 | os Module | 775 | GraphQL (Node) |
| 746 | http / https Module | 776 | tRPC |
| 747 | process Object | 777 | Deno |
| 748 | Environment Variables | 778 | Bun |
| 749 | CommonJS vs ESM in Node | 779 | Node.js Security Best Practices |
| 750 | Module Resolution | 780 | OpenTelemetry in Node |
| 751 | Cluster Module | 781 | Testing Node (Jest, Supertest) |
| 752 | Worker Threads (Node) | 782 | Microservices with Node |
| 753 | Child Process | 783 | Message Queues (Bull, BullMQ) |
| 754 | Express.js | 784 | Cron Jobs in Node |
| 755 | Middleware (Express) | 785 | File System Watchers |
| 756 | Error Handling (Express) | 786 | Hot Module Replacement (HMR) |
| 757 | Request / Response Lifecycle | 787 | Node.js Release Versioning (LTS) |
| 758 | REST API Design in Node | 788 | node:test (Native Test Runner) |
| 759 | Authentication (JWT + Node) | 789 | Async Context Tracking (AsyncLocalStorage) |
| 760 | Rate Limiting (Node) | 790 | REPL |

### npm (30 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 791 | package.json | 806 | Phantom Dependencies |
| 792 | package-lock.json | 807 | Dependency Hell |
| 793 | node_modules | 808 | Security Auditing (npm audit) |
| 794 | Semantic Versioning (semver) | 809 | Scoped Packages |
| 795 | dependencies vs devDependencies vs peerDependencies | 810 | .npmrc |
| 796 | npm install / ci | 811 | Lifecycle Scripts (preinstall, postinstall) |
| 797 | npm scripts | 812 | Monorepo Tooling (Turborepo, Nx) |
| 798 | npx | 813 | Changesets |
| 799 | npm publish / registry | 814 | npm link |
| 800 | Private Registry | 815 | Shrinkwrap |
| 801 | npm workspaces (Monorepo) | 816 | Provenance (npm) |
| 802 | yarn | 817 | Bundled Dependencies |
| 803 | pnpm | 818 | Optional Dependencies |
| 804 | Lock Files | 819 | overrides / resolutions |
| 805 | Hoisting (npm) | 820 | npm Caching |

### Webpack & Build Tools (50 keywords)

| # | Keyword | # | Keyword |
|---|---|---|---|
| 821 | Module Bundler | 846 | SWC (Speedy Web Compiler) |
| 822 | Webpack Entry / Output | 847 | Babel |
| 823 | Webpack Loaders | 848 | Babel Presets and Plugins |
| 824 | Webpack Plugins | 849 | Polyfills |
| 825 | webpack.config.js | 850 | Browserslist |
| 826 | Code Splitting (Webpack) | 851 | ESM Output Format |
| 827 | Lazy Loading (Webpack) | 852 | CJS Output Format |
| 828 | Tree Shaking (Webpack) | 853 | UMD Format |
| 829 | Hot Module Replacement (Webpack) | 854 | IIFE Format |
| 830 | Source Maps | 855 | Chunk / Chunk Splitting |
| 831 | Bundle Analysis (webpack-bundle-analyzer) | 856 | Dynamic Chunks |
| 832 | Asset Modules | 857 | Vendor Chunk |
| 833 | Module Federation | 858 | Content Hash (Cache Busting) |
| 834 | Persistent Caching (Webpack 5) | 859 | Build Optimisation |
| 835 | Webpack Dev Server | 860 | Production vs Development Build |
| 836 | Environment Variables in Webpack | 861 | CI Build Pipeline |
| 837 | DefinePlugin | 862 | Storybook Build |
| 838 | MiniCssExtractPlugin | 863 | Microfrontends |
| 839 | TerserPlugin (Minification) | 864 | Import Maps |
| 840 | Vite | 865 | Native ESM in Browser |
| 841 | Vite vs Webpack | 866 | Build Time vs Runtime |
| 842 | ESBuild | 867 | TypeScript Build (tsc vs esbuild vs swc) |
| 843 | Rollup | 868 | Monorepo Build Strategy |
| 844 | Parcel | 869 | Incremental Builds |
| 845 | Turbopack | 870 | Deploy Previews (Vercel, Netlify) |

---

## Quick Links

Use the navigation menu on the left to explore each section. Each topic contains comprehensive guides, best practices, and actionable knowledge.

---

## 📊 Coverage Stats

| Category | Range | Count |
|---|---|---|
| Java & JVM Internals | 001–050 | 50 |
| Java Language | 051–065 | 15 |
| Java Concurrency | 066–102 | 37 |
| Spring & Spring Boot | 103–138 | 36 |
| Distributed Systems | 139–194 | 56 |
| Databases | 195–240 | 46 |
| Messaging & Streaming | 241–260 | 20 |
| Networking & HTTP | 261–286 | 26 |
| OS & Systems | 287–306 | 20 |
| System Design | 307–340 | 34 |
| Data Structures & Algorithms | 341–376 | 36 |
| Software Design | 377–411 | 35 |
| Testing | 412–423 | 12 |
| Clean Code | 424–433 | 10 |
| Cloud & Infrastructure | 434–449 | 16 |
| DevOps & SDLC | 450–460 | 11 |
| HTML | 461–490 | 30 |
| CSS | 491–540 | 50 |
| JavaScript | 541–620 | 80 |
| TypeScript | 621–670 | 50 |
| React | 671–730 | 60 |
| Node.js | 731–790 | 60 |
| npm | 791–820 | 30 |
| Webpack & Build Tools | 821–870 | 50 |
| **Total** | **001–870** | **870** |

