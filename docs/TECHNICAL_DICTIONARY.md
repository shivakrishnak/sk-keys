---
layout: default
title: Technical Dictionary
parent: Documentation
nav_order: 14
has_children: false
permalink: /docs/technical-dictionary/
---

# 🗂️ Software Engineering & CS Technical Dictionary

A comprehensive master keyword list organized by domain for quick reference and learning.

---

## 🧠 1. Java & JVM Internals

### Memory & Execution
- **JVM** - Java Virtual Machine
- **JRE** - Java Runtime Environment
- **JDK** - Java Development Kit
- **Bytecode** - Compiled Java code format
- **Class Loader** - Dynamic class loading mechanism
- **ClassPath** - Path for class discovery
- **Stack Memory** - LIFO memory for method calls
- **Heap Memory** - Shared object storage
- **Metaspace** - Class metadata storage (Java 8+)
- **PermGen** - Permanent Generation (pre-Java 8)
- **Stack Frame** - Call stack entry for method
- **Operand Stack** - Stack for bytecode operations
- **Local Variable Table** - Method local variables
- **Object Header** - Metadata before object data
- **Mark Word** - Object synchronization state
- **Klass Pointer** - Reference to Class object
- **Escape Analysis** - Optimization for object allocation
- **Object Allocation** - Heap memory allocation
- **TLAB** - Thread Local Allocation Buffer
- **Memory Barrier** - Synchronization primitive
- **Happens-Before** - Memory visibility guarantees

### Garbage Collection
- **GC Roots** - Starting points for reachability analysis
- **Reference Types** - Strong, Soft, Weak, Phantom references
- **Young Generation** - Short-lived object storage
- **Old Generation** - Long-lived object storage
- **Eden Space** - Where new objects are allocated
- **Survivor Space** - Objects surviving minor GC
- **Minor GC** - Young generation collection
- **Major GC** - Old generation collection
- **Full GC** - Complete heap collection
- **Stop-The-World (STW)** - GC pause when app stops
- **Serial GC** - Single-threaded garbage collector
- **Parallel GC** - Multi-threaded garbage collector
- **CMS** - Concurrent Mark Sweep collector
- **G1GC** - Garbage First collector
- **ZGC** - Low-latency garbage collector
- **Shenandoah** - Ultra-low pause GC
- **GC Tuning** - Performance optimization
- **GC Logs** - Garbage collection diagnostics
- **GC Pause** - Time application is suspended
- **Throughput vs Latency** - GC trade-offs
- **Finalization** - Object cleanup mechanism
- **Reference Queue** - Finalized object queue

### Concurrency & Threading
- **Thread** - Unit of execution
- **Runnable** - No-return task interface
- **Callable** - Task with return value
- **Future** - Asynchronous computation result
- **CompletableFuture** - Promise-like async construct
- **Thread Lifecycle** - States and transitions
- **Thread States** - New, Runnable, Blocked, Waiting, Timed Waiting, Terminated
- **synchronized** - Java synchronization keyword
- **volatile** - Memory visibility keyword
- **wait/notify** - Thread coordination primitives
- **ReentrantLock** - Reentrant mutual exclusion lock
- **ReadWriteLock** - Multiple readers, exclusive writer
- **StampedLock** - Optimistic lock variant
- **ThreadLocal** - Thread-specific variable storage
- **InheritableThreadLocal** - ThreadLocal inheritance
- **Memory Visibility** - Shared state synchronization
- **Reordering** - Instruction reordering by JVM
- **Deadlock** - Circular wait condition
- **Livelock** - Threads mutually prevent progress
- **Starvation** - Thread never gets resources
- **Race Condition** - Unsynchronized shared state access
- **CAS** - Compare-And-Swap atomic operation
- **Spin Lock** - Busy-wait lock
- **Optimistic Locking** - Conflict detection on write
- **Executor** - Task submission framework
- **ExecutorService** - Enhanced executor with lifecycle
- **ThreadPoolExecutor** - Configurable thread pool
- **ForkJoinPool** - Work-stealing thread pool
- **Virtual Threads** - Lightweight threads (Project Loom)
- **Carrier Thread** - Thread running virtual thread
- **Continuation** - Suspendable computation unit
- **Semaphore** - Counting synchronization primitive
- **CountDownLatch** - One-time synchronization barrier
- **CyclicBarrier** - Reusable synchronization barrier
- **Phaser** - Flexible synchronization barrier
- **BlockingQueue** - Thread-safe bounded queue
- **ConcurrentHashMap** - Thread-safe hash map
- **CopyOnWriteArrayList** - Thread-safe copy-on-write list

### JIT & Performance
- **JIT Compiler** - Just-In-Time compilation
- **C1/C2 Compiler** - Tiered JIT compilation levels
- **Tiered Compilation** - Multi-level JIT strategy
- **Hotspot** - JVM optimization system
- **Method Inlining** - Function call elimination
- **Loop Unrolling** - Loop optimization
- **Deoptimization** - Reverting optimized code
- **OSR** - On-Stack Replacement for long loops
- **AOT** - Ahead-of-Time compilation
- **GraalVM** - Polyglot VM platform
- **Native Image** - Compiled native executable

### Java Language & Type System
- **Autoboxing** - Primitive to wrapper conversion
- **Unboxing** - Wrapper to primitive conversion
- **Integer Cache** - Cached wrapper instances
- **Generics** - Parametric polymorphism
- **Type Erasure** - Generic type removal at runtime
- **Bounded Wildcards** - Constrained generic types
- **Varargs** - Variable number of arguments
- **Covariance** - Subtype substitution in return
- **Contravariance** - Supertype substitution in parameters
- **Reflection** - Runtime type inspection
- **Annotation Processing** - Compile-time annotation handling
- **APT** - Annotation Processing Tool
- **Serialization** - Object to byte stream conversion
- **Deserialization** - Byte stream to object conversion
- **SerialVersionUID** - Serialization version identifier
- **String Pool** - Interned string storage
- **String Interning** - Shared string optimization
- **Records** - Immutable data classes (Java 14+)
- **Sealed Classes** - Restricted inheritance (Java 15+)
- **Pattern Matching** - Expression matching (Java 17+)

---

## 🌱 2. Spring & Spring Boot

### Core
- **IoC** - Inversion of Control principle
- **DI** - Dependency Injection pattern
- **ApplicationContext** - Spring container
- **BeanFactory** - Low-level bean factory
- **Bean** - Managed component instance
- **Bean Lifecycle** - Initialization and destruction phases
- **Bean Scope** - Singleton, Prototype, Request, Session, Global
- **BeanPostProcessor** - Bean customization hook
- **BeanFactoryPostProcessor** - Factory customization hook
- **@Component** - Generic component annotation
- **@Service** - Service layer annotation
- **@Repository** - Data access layer annotation
- **@Controller** - Web controller annotation
- **@Autowired** - Dependency injection annotation
- **@Qualifier** - Bean selection annotation
- **@Primary** - Default bean selection
- **@Configuration** - Configuration class annotation
- **@Bean** - Bean factory method annotation
- **@Import** - Import configuration class
- **Circular Dependency** - Mutual bean dependency
- **Proxy** - AOP proxy pattern
- **CGLIB** - Code generation library for proxies
- **JDK Dynamic Proxy** - Reflection-based proxy

### Spring AOP
- **AOP** - Aspect-Oriented Programming
- **Aspect** - Modularized cross-cutting concern
- **Advice** - Action taken at join point
- **Pointcut** - Join point selection expression
- **JoinPoint** - Program execution point
- **Weaving** - Aspect integration into code
- **@Before** - Pre-execution advice
- **@After** - Post-execution advice
- **@Around** - Wrapping advice
- **@AfterReturning** - Post-return advice
- **@AfterThrowing** - Exception handling advice
- **AspectJ** - Full-featured AOP framework
- **Spring AOP** - Spring-specific AOP implementation

### Spring MVC & Web
- **DispatcherServlet** - Front controller servlet
- **HandlerMapping** - Request to handler mapping
- **HandlerAdapter** - Handler invocation adapter
- **@RequestMapping** - URL mapping annotation
- **@RestController** - REST endpoint controller
- **Filter** - Request/response filter chain
- **Interceptor** - Handler interceptor
- **HandlerExceptionResolver** - Exception resolution
- **ContentNegotiation** - Response format negotiation
- **MessageConverter** - HTTP message conversion
- **Reactive** - Non-blocking reactive programming
- **WebFlux** - Reactive web framework
- **Mono** - Single element reactive publisher
- **Flux** - Multiple element reactive publisher
- **Backpressure** - Flow control in reactive streams

### Spring Data & Transactions
- **@Transactional** - Transaction demarcation
- **Transaction Propagation** - Transaction inheritance behavior
- **Isolation Levels** - ACID isolation guarantees
- **EntityManager** - JPA entity management
- **JPA** - Java Persistence API
- **Hibernate** - JPA implementation
- **JPQL** - Java Persistence Query Language
- **HQL** - Hibernate Query Language
- **Spring Data JPA** - JPA abstraction layer
- **Repository Pattern** - Data access abstraction
- **N+1 Problem** - Inefficient query pattern
- **Lazy Loading** - Deferred data loading
- **Eager Loading** - Immediate data loading
- **Connection Pool** - Database connection pooling
- **HikariCP** - High-performance connection pool
- **Optimistic Lock** - Version-based locking
- **Pessimistic Lock** - Database row locking

### Spring Boot Internals
- **Auto-Configuration** - Automatic Spring configuration
- **@ConditionalOn*** - Conditional configuration annotations
- **spring.factories** - Spring SPI configuration file
- **Actuator** - Production-ready endpoints
- **Health Indicators** - Health check endpoints
- **Metrics** - Application metrics collection
- **Spring Boot Startup Lifecycle** - Boot startup phases
- **Embedded Server** - Tomcat/Netty embedded
- **Servlet Container** - Embedded web server

---

## 🔗 3. Distributed Systems

### Core Concepts
- **CAP Theorem** - Consistency, Availability, Partition Tolerance
- **PACELC** - Extended CAP theorem
- **Consistency** - All nodes see same data
- **Availability** - System responds to requests
- **Partition Tolerance** - Survives network partition
- **Strong Consistency** - Immediate consistency
- **Eventual Consistency** - Converges to consistency
- **Causal Consistency** - Causally related events ordered
- **Linearizability** - Atomic consistency model
- **Serializability** - Transaction isolation property
- **Sequential Consistency** - Total order of operations
- **BASE** - Basically Available, Soft State, Eventually Consistent
- **ACID** - Atomicity, Consistency, Isolation, Durability

### Time & Ordering
- **Logical Clock** - Lamport or vector clock
- **Lamport Clock** - Sequential logical time
- **Vector Clock** - Causal ordering timestamps
- **Wall Clock** - Physical time
- **Logical Time** - Event ordering time
- **Clock Skew** - Instantaneous clock difference
- **Clock Drift** - Rate of clock divergence
- **Total Order** - Complete ordering of events
- **Partial Order** - Incomplete event ordering
- **Happened-Before Relationship** - Causality relation

### Replication & Consensus
- **Leader Election** - Designating primary replica
- **Raft** - Consensus algorithm
- **Paxos** - Consensus algorithm
- **Replication** - Data duplication across nodes
- **Synchronous Replication** - Blocking write replication
- **Asynchronous Replication** - Non-blocking replication
- **Log Replication** - Command log distribution
- **State Machine Replication** - Deterministic state sync
- **Quorum** - Majority-based decision making
- **Read Quorum** - Minimum reads for consistency
- **Write Quorum** - Minimum writes for consistency
- **Split Brain** - Partitioned cluster conflict
- **Fencing** - Preventing split-brain writes
- **Epoch** - Leadership term identifier

### Fault Tolerance
- **Failure Modes** - Crash, Byzantine, Omission, Timing failures
- **Timeout** - Request timeout mechanism
- **Retry** - Request retry strategy
- **Idempotency** - Safe request retries
- **Circuit Breaker** - Failure prevention pattern
- **Bulkhead** - Resource isolation pattern
- **Rate Limiter** - Request rate limiting
- **Retry with Backoff** - Exponential retry delays
- **Fallback** - Degraded operation fallback
- **Graceful Degradation** - Partial service reduction
- **Health Check** - Component health verification
- **Heartbeat** - Periodic health signal

### Data Distribution
- **Partitioning** - Data distribution strategy
- **Horizontal Partitioning** - Row-based data split
- **Vertical Partitioning** - Column-based data split
- **Functional Partitioning** - Feature-based data split
- **Sharding** - Distributed data partitioning
- **Shard Key** - Data routing key
- **Hot Shard** - Unbalanced partition
- **Consistent Hashing** - Minimal rehashing strategy
- **Virtual Nodes** - Replica placement strategy
- **Rebalancing** - Data redistribution after topology change

### Communication Patterns
- **Synchronous Communication** - Blocking request-response
- **Asynchronous Communication** - Non-blocking messaging
- **Request-Response** - Direct communication pattern
- **Pub/Sub** - Publish-Subscribe pattern
- **Event-Driven** - Event-based communication
- **Message Queue** - Asynchronous message buffer
- **Dead Letter Queue (DLQ)** - Failed message storage
- **Exactly-Once Delivery** - Single message delivery
- **At-Least-Once Delivery** - At minimum one delivery
- **At-Most-Once Delivery** - At maximum one delivery
- **Saga Pattern** - Long-running transaction pattern
- **Choreography** - Decentralized orchestration
- **Orchestration** - Centralized coordination
- **Outbox Pattern** - Transactional messaging
- **Two-Phase Commit (2PC)** - Distributed transaction protocol

---

## 💾 4. Databases

### Core DB Concepts
- **ACID** - Atomicity, Consistency, Isolation, Durability
- **Atomicity** - All-or-nothing transaction
- **Consistency** - Valid state transition
- **Isolation** - Transaction independence
- **Durability** - Persistent data storage
- **Transaction** - Logical work unit
- **Commit** - Transaction acceptance
- **Rollback** - Transaction reversal
- **Savepoint** - Partial transaction rollback marker
- **Isolation Levels** - Read Uncommitted, Read Committed, Repeatable Read, Serializable
- **Dirty Read** - Reading uncommitted data
- **Non-Repeatable Read** - Data change between reads
- **Phantom Read** - New rows appearing in re-read
- **MVCC** - Multi-Version Concurrency Control
- **WAL** - Write-Ahead Log
- **Redo Log** - Forward recovery log
- **Undo Log** - Backward recovery log
- **B-Tree** - Balanced tree data structure
- **B+ Tree** - B-Tree variant with pointers
- **LSM Tree** - Log-Structured Merge tree
- **Index** - Query acceleration structure
- **B-Tree Index** - Tree-based index
- **Hash Index** - Hash table-based index
- **Composite Index** - Multi-column index
- **Covering Index** - Index containing all query data
- **Partial Index** - Subset row index
- **Query Planner** - Query optimization engine
- **Execution Plan** - Query execution strategy
- **EXPLAIN** - Query plan inspection
- **Normalization** - Schema organization principle
- **Denormalization** - Data redundancy for performance
- **1NF–5NF** - Normalization forms
- **Foreign Key** - Referential constraint
- **Referential Integrity** - Foreign key enforcement
- **Cascade** - Foreign key action option

### Advanced DB
- **Locking** - Row, Table, Gap, Next-Key locks
- **Row Lock** - Single-row locking
- **Table Lock** - Entire table locking
- **Gap Lock** - Range between rows locking
- **Next-Key Lock** - Row plus gap locking
- **Deadlock Detection** - Circular dependency detection
- **Lock Wait Timeout** - Lock acquisition timeout
- **Stored Procedure** - Database-stored program
- **Trigger** - Event-driven database action
- **View** - Virtual table
- **Materialized View** - Cached view
- **Partitioning** - Table partitioning strategy
- **Range Partitioning** - Value range-based split
- **List Partitioning** - Discrete value-based split
- **Hash Partitioning** - Hash function-based split
- **Composite Partitioning** - Multiple strategy combination
- **Connection Pooling** - Database connection reuse
- **Prepared Statements** - Precompiled query statements
- **Replication** - Master-Slave, Multi-Master setups
- **Master-Slave Replication** - Primary to replica copy
- **Multi-Master Replication** - Multiple primary replicas
- **Read Replica** - Read-only copy
- **Write Amplification** - Multiple disk writes per logical write

### NoSQL & NewSQL
- **Document Store** - JSON document database
- **Key-Value Store** - Simple key-value storage
- **Column Family** - Column-oriented storage
- **Graph DB** - Relationship-focused storage
- **MongoDB** - Document database
- **Redis** - In-memory key-value store
- **Cassandra** - Distributed column store
- **DynamoDB** - AWS managed NoSQL database
- **Eventual Consistency** - Time-dependent consistency
- **CRDTs** - Conflict-free Replicated Data Types
- **HBase** - Distributed column store
- **BigTable** - Google's distributed database
- **Spanner** - Google's globally distributed database

### Caching
- **Cache-Aside** - Application-managed caching
- **Read-Through** - Cache-managed read
- **Write-Through** - Synchronous write caching
- **Write-Behind** - Asynchronous write caching
- **Cache Invalidation** - Removing stale cache data
- **TTL** - Time-to-Live cache expiration
- **Eviction Policies** - LRU, LFU, FIFO removal strategies
- **LRU** - Least Recently Used eviction
- **LFU** - Least Frequently Used eviction
- **FIFO** - First-In-First-Out eviction
- **Cache Stampede** - Thundering herd on expiration
- **Thundering Herd** - Simultaneous cache miss spike
- **Negative Caching** - Caching absence
- **Distributed Cache** - Redis, Hazelcast, Memcached
- **Cache Coherence** - Data consistency across caches
- **Stale Data** - Outdated cached values

---

## 📨 5. Messaging & Streaming

### Kafka
- **Topic** - Message category
- **Partition** - Topic division for parallelism
- **Offset** - Message position in partition
- **Consumer Group** - Coordinated consumers
- **Producer** - Message publisher
- **Consumer** - Message subscriber
- **Broker** - Kafka server node
- **Zookeeper** - Legacy coordination service
- **KRaft** - New consensus mechanism
- **Replication Factor** - Replica count
- **ISR** - In-Sync Replicas
- **Log Compaction** - Keeping latest version only
- **Retention Policy** - Message retention duration
- **At-Least-Once Delivery** - Minimum delivery guarantee
- **Exactly-Once Delivery** - Single delivery guarantee
- **Kafka Streams** - Stream processing framework
- **KSQL** - Stream SQL queries
- **Consumer Lag** - Consumer behind producer
- **Backpressure** - Flow control mechanism
- **Idempotent Producer** - Duplicate-free producing
- **Transactional Producer** - Atomic multi-partition writes

### General Messaging
- **Point-to-Point** - One-to-one messaging
- **Publish-Subscribe** - One-to-many messaging
- **Message Broker** - Centralized message hub
- **Event Bus** - Distributed event propagation
- **RabbitMQ** - Erlang-based message broker
- **ActiveMQ** - Java message broker
- **SQS** - AWS managed message queue
- **Competing Consumers** - Multiple consumer pattern
- **Fan-Out** - Message replication to multiple destinations
- **Message Ordering** - Sequential message delivery
- **Message Deduplication** - Removing duplicate messages

---

## 🌐 6. Networking & HTTP

### Fundamentals
- **OSI Model** - Seven-layer network model
- **TCP/IP Stack** - Network protocol stack
- **TCP** - Transmission Control Protocol
- **UDP** - User Datagram Protocol
- **QUIC** - Quick UDP Internet Connection
- **TCP Handshake** - Three-way connection establishment
- **TCP Teardown** - Connection termination
- **Congestion Control** - Network saturation management
- **Flow Control** - Sender-receiver speed matching
- **Sliding Window** - Flow control mechanism
- **IP** - Internet Protocol
- **Subnet** - IP address range
- **CIDR** - Classless Inter-Domain Routing
- **NAT** - Network Address Translation
- **DNS** - Domain Name System
- **CDN** - Content Delivery Network
- **Anycast** - One-to-nearest routing
- **Socket** - Network communication endpoint
- **Port** - Process communication endpoint
- **Ephemeral Port** - Temporary client-side port

### HTTP & REST
- **HTTP/1.1** - Persistent connection HTTP
- **HTTP/2** - Multiplexed HTTP
- **HTTP/3** - QUIC-based HTTP
- **Request/Response** - HTTP message pattern
- **Headers** - HTTP message metadata
- **Body** - HTTP message content
- **Status Codes** - HTTP response codes
- **Keep-Alive** - Connection persistence
- **Connection Pooling** - Reusing HTTP connections
- **REST** - Representational State Transfer
- **RESTful Constraints** - REST architectural principles
- **HATEOAS** - Hypermedia links in responses
- **HTTP Methods** - GET, POST, PUT, PATCH, DELETE
- **Idempotency** - Multiple requests same effect
- **gRPC** - High-performance RPC framework
- **Protocol Buffers** - Binary message format
- **Thrift** - Cross-language RPC framework
- **WebSocket** - Bidirectional communication
- **Server-Sent Events (SSE)** - Unidirectional server push
- **Long Polling** - Simulated server push

### Security
- **TLS/SSL** - Transport Layer Security
- **Handshake** - TLS connection setup
- **Certificate** - X.509 digital certificate
- **CA** - Certificate Authority
- **mTLS** - Mutual TLS authentication
- **OAuth2** - Authorization delegation protocol
- **JWT** - JSON Web Token
- **OIDC** - OpenID Connect authentication
- **API Key** - Simple API authentication
- **HMAC** - Hash-based message authentication
- **CORS** - Cross-Origin Resource Sharing
- **XSS** - Cross-Site Scripting vulnerability
- **CSRF** - Cross-Site Request Forgery vulnerability
- **SQL Injection** - Database injection attack
- **SSRF** - Server-Side Request Forgery
- **Rate Limiting** - Request rate control
- **Throttling** - Bandwidth limiting
- **DDoS** - Distributed Denial of Service attack

---

## 🖥️ 7. OS & Systems

### Processes & Threads
- **Process** - Independent program execution
- **Thread** - Lightweight execution unit
- **Fiber** - Cooperative multitasking unit
- **Coroutine** - Resumable computation unit
- **Process vs Thread** - Memory model differences
- **Context Switch** - CPU switching between tasks
- **Scheduler** - Task scheduling logic
- **Preemption** - Forced task switching
- **User Space** - Application execution space
- **Kernel Space** - Operating system space
- **System Call (syscall)** - User to kernel transition
- **Trap** - Synchronous exception mechanism
- **Fork** - Process creation
- **Exec** - Process replacement

### Memory Management
- **Virtual Memory** - Address space abstraction
- **Physical Memory** - Hardware memory
- **MMU** - Memory Management Unit
- **Paging** - Fixed-size memory blocks
- **Page Table** - Virtual to physical mapping
- **TLB** - Translation Lookaside Buffer
- **Page Fault** - Missing page handling
- **Swapping** - Disk-based memory extension
- **Thrashing** - Excessive paging
- **Stack vs Heap** - Memory allocation types
- **Memory-Mapped File (mmap)** - File to memory mapping
- **Buddy System** - Power-of-two allocation
- **Slab Allocator** - Cache-friendly allocation

### I/O & Files
- **Blocking I/O** - Synchronous I/O operations
- **Non-Blocking I/O** - Asynchronous I/O operations
- **Async I/O** - Asynchronous completion notification
- **select** - I/O multiplexing mechanism
- **poll** - Event polling mechanism
- **epoll** - Linux I/O multiplexing
- **kqueue** - BSD I/O multiplexing
- **File Descriptor** - Open file reference
- **inode** - File metadata structure
- **Buffer** - I/O buffering mechanism
- **Page Cache** - Disk block caching
- **Dirty Pages** - Modified cache pages
- **Zero-Copy** - Avoiding data duplication
- **sendfile** - Kernel-level file transmission

### Concurrency (OS Level)
- **Mutex** - Mutual exclusion lock
- **Semaphore** - Resource counting primitive
- **Spinlock** - Busy-wait lock
- **Condition Variable** - Thread coordination primitive
- **Atomic Operations** - Indivisible operations
- **Memory Ordering** - Operation sequencing guarantees
- **NUMA** - Non-Uniform Memory Architecture
- **Cache Line** - CPU cache allocation unit
- **False Sharing** - Unrelated data in same cache line

---

## 🏗️ 8. System Design

### Architecture Patterns
- **Monolith** - Single deployment unit
- **Microservices** - Multiple independent services
- **Modular Monolith** - Modular single deployment
- **Service Mesh** - Microservice networking layer
- **Sidecar Pattern** - Co-located helper service
- **API Gateway** - Request routing and translation
- **BFF** - Backend for Frontend pattern
- **CQRS** - Command Query Responsibility Segregation
- **Event Sourcing** - Event-based state tracking
- **Hexagonal Architecture** - Ports and adapters
- **Clean Architecture** - Layered architecture principle
- **Onion Architecture** - Concentric layer architecture
- **Domain-Driven Design (DDD)** - Domain-focused design
- **Aggregate** - DDD consistency boundary
- **Bounded Context** - DDD service boundary
- **Ubiquitous Language** - Domain-shared terminology

### Scalability
- **Vertical Scaling** - Single machine enhancement
- **Horizontal Scaling** - Adding more machines
- **Load Balancing** - Distributing load across servers
- **L4 Load Balancing** - Transport layer balancing
- **L7 Load Balancing** - Application layer balancing
- **Round Robin** - Sequential server selection
- **Least Connections** - Connects to least-busy server
- **Sticky Sessions** - Client affinity to server
- **Session Affinity** - Maintaining client-server mapping
- **Rate Limiting** - Request rate control
- **Token Bucket** - Rate limiting algorithm
- **Leaky Bucket** - smoothed rate limiting
- **Autoscaling** - Automatic capacity adjustment
- **HPA** - Kubernetes Horizontal Pod Autoscaler
- **Thundering Herd** - Simultaneous resource request
- **Backpressure** - Flow control mechanism

### Reliability
- **SLA** - Service Level Agreement
- **SLO** - Service Level Objective
- **SLI** - Service Level Indicator
- **MTTR** - Mean Time to Recovery
- **MTBF** - Mean Time Between Failures
- **RTO** - Recovery Time Objective
- **RPO** - Recovery Point Objective
- **Redundancy** - Duplicate component placement
- **Failover** - Automatic failure recovery
- **Active-Active** - Multiple active instances
- **Active-Passive** - Single active instance
- **Chaos Engineering** - Resilience testing
- **Game Days** - Failure simulation exercises
- **Graceful Shutdown** - Controlled service termination
- **Rolling Restart** - Sequential instance restart

### Observability
- **Logging** - Event recording
- **Structured Logging** - Formatted log entries
- **Log Levels** - DEBUG, INFO, WARN, ERROR, FATAL
- **Metrics** - Quantitative measurements
- **Counter** - Monotonically increasing metric
- **Gauge** - Point-in-time snapshot metric
- **Histogram** - Value distribution metric
- **Summary** - Distribution summary metric
- **Tracing** - Request flow visualization
- **Distributed Tracing** - Cross-service request tracing
- **Span** - Individual operation in trace
- **Trace ID** - Request identifier across services
- **OpenTelemetry** - Standardized observability framework
- **Jaeger** - Distributed tracing platform
- **Zipkin** - Distributed tracing system
- **Prometheus** - Metrics collection system
- **Grafana** - Metrics visualization
- **Alerting** - Exception condition notification
- **SLO-Based Alerting** - SLO-driven alerting
- **Error Budget** - Allocated downtime allowance

---

## 🔧 9. Data Structures & Algorithms

### Core Data Structures
- **Array** - Contiguous element storage
- **LinkedList** - Pointer-based node storage
- **Stack** - LIFO data structure
- **Queue** - FIFO data structure
- **Deque** - Double-ended queue
- **HashMap** - Key-value hash table
- **LinkedHashMap** - Insertion-order hash map
- **TreeMap** - Sorted key-value map
- **HashSet** - Key hash set
- **TreeSet** - Sorted set
- **Heap** - Complete binary tree
- **Min Heap** - Minimum element at root
- **Max Heap** - Maximum element at root
- **Priority Queue** - Priority-based queue
- **Trie** - Prefix tree structure
- **Suffix Tree** - Suffix-based tree
- **Graph** - Vertex and edge structure
- **Directed Graph** - Directed edges
- **Undirected Graph** - Bidirectional edges
- **Weighted Graph** - Edge weight assignment
- **Segment Tree** - Range query tree
- **Fenwick Tree (BIT)** - Binary Indexed Tree
- **Skip List** - Probabilistic search structure
- **Bloom Filter** - Probabilistic set membership
- **Consistent Hash Ring** - Distributed hashing

### Algorithm Concepts
- **Time Complexity** - Runtime growth rate
- **Space Complexity** - Memory growth rate
- **Big-O** - Asymptotic complexity notation
- **Amortized Analysis** - Average operation cost
- **Recursion** - Self-referential computation
- **Memoization** - Caching recursive results
- **Tabulation** - Bottom-up dynamic programming
- **Divide and Conquer** - Problem decomposition
- **Greedy** - Optimal local choice strategy
- **Dynamic Programming** - Overlapping subproblems
- **BFS** - Breadth-First Search
- **DFS** - Depth-First Search
- **Topological Sort** - Directed acyclic graph ordering
- **Dijkstra** - Shortest path algorithm
- **Bellman-Ford** - Single-source shortest path
- **A*** - Heuristic pathfinding algorithm
- **Union-Find** - Disjoint set union structure
- **Disjoint Set** - Set membership tracking
- **Kruskal** - Minimum spanning tree algorithm
- **Prim** - Minimum spanning tree algorithm
- **Quicksort** - Divide-and-conquer sort
- **Mergesort** - Merge-based sort
- **Timsort** - Hybrid sort algorithm
- **Heapsort** - Heap-based sort
- **Two Pointer** - Dual pointer technique
- **Sliding Window** - Fixed-size window technique
- **Binary Search** - Logarithmic search
- **Backtracking** - Constraint-based search
- **Bit Manipulation** - Binary operation techniques

---

## 🧩 10. Software Design & Engineering Excellence

### Design Principles
- **SOLID** - Design principle collection
- **SRP** - Single Responsibility Principle
- **OCP** - Open/Closed Principle
- **LSP** - Liskov Substitution Principle
- **ISP** - Interface Segregation Principle
- **DIP** - Dependency Inversion Principle
- **DRY** - Don't Repeat Yourself
- **KISS** - Keep It Simple, Stupid
- **YAGNI** - You Aren't Gonna Need It
- **Law of Demeter** - Minimize object coupling
- **Tell Don't Ask** - Command-based design
- **Composition over Inheritance** - Object composition preference
- **Fail Fast** - Early error detection
- **Defensive Programming** - Assumption validation

### Design Patterns
- **Singleton** - Single instance creation
- **Factory** - Object creation abstraction
- **Abstract Factory** - Family object creation
- **Builder** - Complex object construction
- **Prototype** - Object cloning
- **Adapter** - Interface compatibility
- **Decorator** - Feature addition wrapper
- **Facade** - Simplified interface wrapper
- **Proxy** - Surrogate access control
- **Composite** - Tree composition structure
- **Bridge** - Abstraction implementation separation
- **Flyweight** - Shared object optimization
- **Strategy** - Algorithm selection
- **Observer** - Change notification pattern
- **Command** - Request encapsulation
- **Template Method** - Algorithm skeleton
- **Chain of Responsibility** - Request handler chain
- **State** - State-based behavior switching
- **Visitor** - Operation visiting pattern
- **Iterator** - Sequential access pattern
- **Mediator** - Object interaction coordinator
- **Memento** - State snapshot pattern
- **Double-Checked Locking** - Lazy initialization
- **Producer-Consumer** - Async queue pattern
- **Thread Pool** - Worker thread pool pattern

### Testing
- **Unit Test** - Single component testing
- **Integration Test** - Component interaction testing
- **Contract Test** - Interface contract validation
- **E2E Test** - End-to-end workflow testing
- **TDD** - Test-Driven Development
- **BDD** - Behavior-Driven Development
- **Mocking** - Object behavior simulation
- **Stubbing** - Fixed response provision
- **Faking** - Lightweight implementation
- **Spying** - Call tracking wrapper
- **Test Pyramid** - Testing strategy levels
- **Test Diamond** - Diamond-shaped test strategy
- **Property-Based Testing** - Generative testing
- **Mutation Testing** - Test quality verification

### Clean Code & Architecture
- **Cohesion** - Related functionality grouping
- **Coupling** - Component dependency degree
- **Abstraction** - Concept generalization
- **Encapsulation** - Data hiding and exposure control
- **Polymorphism** - Subtype substitution
- **Inheritance** - Hierarchical type relation
- **Command-Query Separation (CQS)** - Separating mutations from queries
- **Feature Flags** - Conditional feature enabling
- **Dark Launch** - Hidden production testing
- **Canary Release** - Gradual rollout strategy
- **Technical Debt** - Accumulated design shortcuts
- **Refactoring** - Code improvement without behavior change

---

## ☁️ 11. Cloud & Infrastructure

### Containers & Orchestration
- **Docker** - Container platform
- **Container** - Isolated application package
- **Image** - Container template
- **Layer** - Container image layer
- **Dockerfile** - Container definition file
- **Namespace** - Process isolation mechanism
- **Cgroups** - Resource limiting groups
- **Kubernetes** - Container orchestration platform
- **Pod** - Smallest Kubernetes unit
- **Node** - Kubernetes worker machine
- **Deployment** - Declarative pod management
- **Service** - Pod network abstraction
- **Ingress** - External traffic routing
- **ConfigMap** - Configuration data storage
- **Secret** - Sensitive data storage
- **HPA** - Horizontal Pod Autoscaler
- **VPA** - Vertical Pod Autoscaler
- **Cluster Autoscaler** - Node autoscaling
- **StatefulSet** - Stateful pod management
- **DaemonSet** - Node-resident pod management
- **Job** - One-time task execution
- **CronJob** - Scheduled task execution
- **Service Discovery** - Dynamic service location
- **kube-proxy** - Kubernetes network proxy
- **CoreDNS** - Kubernetes DNS service

### Cloud Patterns
- **IaaS** - Infrastructure as a Service
- **PaaS** - Platform as a Service
- **SaaS** - Software as a Service
- **FaaS** - Functions as a Service
- **Serverless** - Managed execution environment
- **Cold Start** - Initial function invocation delay
- **Object Storage** - S3-compatible storage
- **S3** - Amazon Simple Storage Service
- **Block Storage** - Persistent block device
- **File Storage** - Network file system
- **CDN** - Content Delivery Network
- **Edge Computing** - Distributed edge processing
- **Multi-Region** - Multiple geographic deployment
- **Multi-AZ** - Multiple availability zones
- **Active-Active** - Multiple active regions

### Networking in Cloud
- **VPC** - Virtual Private Cloud
- **Subnet** - VPC network partition
- **Security Group** - Stateful firewall
- **NACLs** - Network Access Control Lists
- **Load Balancer** - Traffic distribution
- **ALB** - Application Load Balancer
- **NLB** - Network Load Balancer
- **CLB** - Classic Load Balancer
- **Service Mesh** - Microservice networking
- **Istio** - Service mesh platform
- **Linkerd** - Lightweight service mesh
- **mTLS** - Mutual TLS encryption
- **East-West Traffic** - Internal service traffic
- **North-South Traffic** - External ingress/egress

---

## 🔄 12. DevOps & SDLC

- **CI/CD** - Continuous Integration/Deployment
- **Pipeline** - Automated workflow stage
- **Artifact** - Build output package
- **Registry** - Container image repository
- **Blue-Green Deployment** - Zero-downtime releases
- **Canary** - Gradual rollout strategy
- **Rolling Update** - Sequential instance updates
- **GitOps** - Git-driven infrastructure
- **Infrastructure as Code (IaC)** - Code-based infrastructure
- **Terraform** - Infrastructure provisioning tool
- **Helm** - Kubernetes package manager
- **Immutable Infrastructure** - Unchangeable deployments
- **Twelve-Factor App** - App development principles
- **Feature Flags** - Conditional feature enabling
- **Kill Switch** - Feature disable mechanism
- **SRE** - Site Reliability Engineering
- **Error Budget** - Downtime allowance
- **Toil** - Repetitive manual work
- **Version Control** - Source code management
- **Git** - Distributed version control
- **Branching Strategy** - Branch management approach
- **Build System** - Automated build tooling
- **Artifact Management** - Build output storage

---

## 📚 References & Cross-Domain Topics

This dictionary covers essential terminology across:
- **Backend Development** - Java and Spring frameworks
- **Distributed Computing** - Systems, consensus, and scalability
- **Data Management** - Databases and caching strategies
- **System Architecture** - Design patterns and implementation
- **Operations** - Cloud, containers, and DevOps practices
- **Software Quality** - Testing, design, and reliability

**Last Updated**: April 28, 2026

