# Interview Mastery Dictionary - Topic Registry

> This registry maps topics to their interview folders and links them
> to existing dictionary categories where applicable. Start with core
> topics; grow organically as new topics are added.

---

## Spec References

| File                                               | Purpose                                     |
| -------------------------------------------------- | ------------------------------------------- |
| `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md`   | Master keyword generation spec (v4.0)       |
| `.github/prompts/dict-generate-keywords.prompt.md` | Prompt for category/tier keyword processing |
| `interview/_config/INTERVIEW_PROMPT.md`            | Master content generation spec (v3.0)       |

## Design Considerations

1. **New topic (no folder/index.md):** Use `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md` v4.0 to generate keywords. Analyse tier placement. Create folders/files. Generate content.
2. **Brand-new topic (e.g., Angular):** Analyse which tier it belongs to. Generate keywords via `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md`. Create folders/files. Generate content.
3. **New subtopic (e.g., React Hooks, topic exists):** Create file in existing folder. Generate keywords via `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md`. Generate content.
4. **Existing dictionary category (e.g., JVM, JCC):** Scan dictionary `index.md`. Analyse keywords. Check for new folder/file opportunities. Generate content.

---

## Registry Format

| Topic        | Folder         | Dictionary Sources           | Status                                       |
| ------------ | -------------- | ---------------------------- | -------------------------------------------- |
| [Topic Name] | [folder-name/] | [CODE1, CODE2, ...] or "new" | planned / scaffolded / generating / complete |

---

## Active Topics

| Topic                           | Folder             | Dictionary Sources | Status     | Description                                                                   |
| ------------------------------- | ------------------ | ------------------ | ---------- | ----------------------------------------------------------------------------- |
| Java                            | java/              | JVM, JLG           | generating | Core Java language, OOP, collections, modern Java features, JVM internals, GC |
| Java Concurrency                | java-concurrency/  | JCC                | generating | Threading, synchronization, virtual threads, concurrent collections           |
| Spring                          | spring/            | SPR                | complete   | Spring Core, Boot, MVC, Security, Data, Cloud, AOP, Testing                   |
| Hibernate                       | hibernate/         | JPH                | generating | ORM fundamentals, JPA, entity management, performance, locking                |
| SQL and Databases               | sql-and-databases/ | DBF, NDB           | planned    | SQL queries, joins, indexing, transactions, NoSQL, replication                |
| Containers                      | containers/        | CTR                | planned    | Docker fundamentals, images, networking, compose, security                    |
| Kubernetes                      | kubernetes/        | K8S                | planned    | Core resources, networking, storage, security, operations                     |
| System Design                   | system-design/     | DST, MSV, SYD, SAP | complete   | Distributed systems, microservices, architecture, infrastructure              |
| React                           | react/             | RCT                | scaffolded | Components, hooks, state management, performance, testing                     |
| Security                        | security/          | SEC, IAM, CRY      | planned    | Web security, authentication, authorization, cryptography                     |
| Data Structures and Algorithms  | dsa/               | DSA                | planned    | Arrays, trees, graphs, sorting, dynamic programming                           |
| Caching                         | caching/           | CCH                | planned    | Cache patterns, Redis, CDN, invalidation, consistency                         |
| Messaging                       | messaging/         | MSG                | planned    | Kafka, RabbitMQ, event-driven architecture, streaming                         |
| CI/CD and DevOps                | cicd-and-devops/   | CCD, GIT, OBS      | planned    | Pipelines, Git strategies, observability, SRE practices                       |
| AI and RAG                      | ai-and-rag/        | AIF, LLM, RAG      | planned    | LLM fundamentals, prompt engineering, RAG, agents, LLMOps                     |
| Design Patterns                 | design-patterns/   | DPT                | complete   | GoF patterns, SOLID, creational, structural, behavioral, additional           |
| Microservices                   | microservices/     | MSV                | complete   | Service decomposition, communication, resilience, deployment                  |
| Async and Background Processing | async-background/  | ASY                | complete   | Message queues, brokers, event-driven, orchestration, observability           |

---

## Sub-topic File Mapping

Each topic is split into sub-topic files. Below are the planned file
splits for each topic. Files are grouped by relatedness - each file
should be self-sufficient.

### Java (java/)

| File                               | Keywords (approximate)                                                                                                                                                 | Source IDs                          |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Java - Basics.md                   | Variables/Data Types, Operators/Control Flow, Classes/Objects, Inheritance, Interfaces, Access Modifiers, Enums                                                        | JLG-019 to JLG-027                  |
| Java - Collections.md              | Collections Framework, ArrayList/LinkedList, HashMap/TreeMap, HashSet, Queue/Deque, Iterator, Comparable/Comparator, equals/hashCode                                   | JLG-029, JLG-077/078/080            |
| Java - Exceptions and IO.md        | Exception Hierarchy, Checked vs Unchecked, Try-with-Resources, Custom Exceptions, File IO, NIO, Serialization, Logging                                                 | JLG-030/031/040/070/076             |
| Java - Java 8 Features.md          | Lambdas, Functional Interfaces, Stream API, Optional, Method References, Default Methods, DateTime API, Collectors                                                     | JLG-035 to JLG-038, JLG-072/075/079 |
| Java - Java 11 to 17.md            | var, Text Blocks, Switch Expressions, Records, Sealed Classes, Pattern Matching instanceof, JPMS, HttpClient                                                           | JLG-032/039/071/082/083/014         |
| Java - Java 21 and Beyond.md       | Virtual Threads Patterns, Structured Concurrency, Scoped Values, Pattern Matching switch, Record Patterns, Sequenced Collections, String Templates, Foreign Memory API | JLG-049/097/098                     |
| Java - JVM Internals.md            | JVM Architecture, JVM/JRE/JDK, Bytecode, Class Loading, Stack/Heap, Metaspace, JIT (C1/C2), Escape Analysis, GraalVM                                                   | JVM-001 to JVM-057                  |
| Java - Garbage Collection.md       | GC Fundamentals, GC Roots, Generational GC, Serial/Parallel GC, G1GC, ZGC, Shenandoah, GC Tuning/Logs, Reference Types                                                 | JVM-037 to JVM-048                  |
| Java - Diagnostics and Security.md | JFR, Thread Dumps, Heap Dumps, Performance Tuning, GC Selection Framework, Java Security, Version Migration                                                            | JVM-063 to JVM-067, JLG-015/016     |

### Spring (spring/)

| File                        | Keywords (approximate)                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------ |
| Spring - Core and IoC.md    | IoC Container, Dependency Injection, Bean Lifecycle, ApplicationContext, Configuration     |
| Spring - Annotations.md     | Component Scanning, Autowiring, Qualifier, Conditional, Profile, Configuration Annotations |
| Spring - Boot.md            | Auto-Configuration, Starters, Actuator, Properties, Embedded Server, DevTools              |
| Spring - MVC and REST.md    | DispatcherServlet, Controllers, Request Mapping, Exception Handling, Content Negotiation   |
| Spring - Data and JPA.md    | Spring Data Repositories, Query Methods, Specifications, Auditing, Transactions            |
| Spring - Security.md        | Authentication, Authorization, OAuth2, JWT, CORS, CSRF Protection, Method Security         |
| Spring - Cloud.md           | Service Discovery, Config Server, Circuit Breaker, API Gateway, Distributed Tracing        |
| Spring - AOP and Testing.md | Spring AOP, Spring Testing, Spring WebFlux                                                 |

### Java Concurrency (java-concurrency/)

| File                                         | Keywords (approximate)                                                                                                                     | Source IDs                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- |
| Java Concurrency - Thread Basics.md          | Thread/Runnable, Callable/Future, Thread Lifecycle, Executor, ExecutorService, ThreadPoolExecutor, ForkJoinPool, CompletableFuture         | JCC-006 to JCC-017                      |
| Java Concurrency - Synchronization.md        | synchronized, volatile, JMM/Happens-Before, ReentrantLock, ReadWriteLock, StampedLock, Atomics/CAS, ThreadLocal, wait/notify               | JCC-038/056 to JCC-064                  |
| Java Concurrency - Concurrent Collections.md | ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue, CountDownLatch, Semaphore, CyclicBarrier, Phaser, Producer-Consumer, Lock Striping | JCC-042 to JCC-053, JCC-070/071/072/073 |
| Java Concurrency - Virtual Threads.md        | Virtual Threads, Carrier Threads, Structured Concurrency, Scoped Values, Thread Pinning, Loom Migration, Continuations                     | JCC-067 to JCC-069, JCC-076/088/089     |
| Java Concurrency - Diagnostics.md            | Deadlock Detection, Thread Dumps, JMH Benchmarking, Testing Concurrent Code, Lock-Free, False Sharing, ABA Problem, Work-Stealing          | JCC-023 to JCC-036                      |

### Hibernate (hibernate/)

| File                         | Keywords (approximate)                                                                      | Source IDs         |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ------------------ |
| Hibernate - Basics.md        | Session/EntityManager, Entity States, Entity Mapping, Primary Keys, Dirty Checking          | JPH basics range   |
| Hibernate - Relationships.md | OneToMany/ManyToOne, ManyToMany, Fetch Types, Cascade Types, Bidirectional                  | JPH relation range |
| Hibernate - Performance.md   | L1/L2 Cache, N+1 Detection, Batch/Bulk Ops, Query Optimization, Statistics                  | JPH perf range     |
| Hibernate - Advanced.md      | Optimistic/Pessimistic Locking, Inheritance Mapping, JPQL/Criteria/Native, Schema Migration | JPH advanced       |

### Kubernetes (kubernetes/)

| File                              | Keywords (approximate)                                                               |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| Kubernetes - Core Resources.md    | Pods, Deployments, Services, Namespaces, ConfigMaps, Secrets, Labels and Selectors   |
| Kubernetes - Networking.md        | ClusterIP, NodePort, LoadBalancer, Ingress, Network Policies, DNS, Service Mesh      |
| Kubernetes - Storage and State.md | Volumes, PV/PVC, StatefulSets, Storage Classes, CSI Drivers                          |
| Kubernetes - Security and RBAC.md | RBAC, Service Accounts, Security Contexts, Pod Security, Network Policies            |
| Kubernetes - Operations.md        | Scaling, Rolling Updates, Health Probes, Resource Limits, HPA, Monitoring, Debugging |

### SQL and Databases (sql-and-databases/)

| File                             | Keywords (approximate)                                                              |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| SQL - Fundamentals.md            | SELECT, WHERE, GROUP BY, HAVING, ORDER BY, Subqueries, Data Types                   |
| SQL - Joins and Relationships.md | INNER JOIN, LEFT/RIGHT JOIN, CROSS JOIN, Self Join, Foreign Keys, Normalization     |
| SQL - Performance.md             | Indexes, Query Plans, EXPLAIN, Partitioning, Connection Pooling, Query Optimization |
| Databases - Transactions.md      | ACID, Isolation Levels, Locking, MVCC, Deadlocks, Distributed Transactions          |
| Databases - Architecture.md      | Replication, Sharding, CAP Theorem, Consistency Models, LSM Trees, B-Trees          |
| NoSQL - Patterns.md              | Document Stores, Key-Value, Column Family, Graph DBs, When to Use NoSQL             |

### System Design (system-design/)

| File                              | Keywords (approximate)                                                 |
| --------------------------------- | ---------------------------------------------------------------------- |
| System Design - Fundamentals.md   | Scalability, Availability, Reliability, Load Balancing, CDN, DNS       |
| System Design - Patterns.md       | Circuit Breaker, Retry, Bulkhead, Saga, CQRS, Event Sourcing           |
| System Design - Microservices.md  | Service Decomposition, API Gateway, Service Discovery, Data Ownership  |
| System Design - Data at Scale.md  | Sharding, Partitioning, Replication, Consensus, Eventual Consistency   |
| System Design - Case Studies.md   | URL Shortener, Chat System, News Feed, Rate Limiter, Distributed Cache |
| System Design - Infrastructure.md | Load Balancing, CDN, Leader Election, Bloom Filters                    |

---

## Adding New Topics

To add a new topic to this registry:

1. Choose a descriptive topic name and lowercase folder name
2. Check if a dictionary category exists (look at Category Code Registry
   in `dictionary/_config/GENERATOR_PROMPT.md` or
   `.github/instructions/dictionary.instructions.md`)
3. If dictionary source exists: map category codes in "Dictionary Sources"
4. If no dictionary source: set Dictionary Sources to "new"
5. Plan sub-topic file splits (5-20 keywords per file, grouped by relatedness)
6. Add rows to the Active Topics and Sub-topic File Mapping tables
7. Set status to "planned"
8. Run `generate-keywords.ps1` to scaffold the folder

## Status Definitions

| Status     | Meaning                                                        |
| ---------- | -------------------------------------------------------------- |
| planned    | Topic identified, sub-topic files mapped, no files created yet |
| scaffolded | Folder, index.md, and stub files created                       |
| generating | Content generation in progress                                 |
| complete   | All files have complete content                                |

### Design Patterns (design-patterns/)

| File                                | Keywords (approximate)                                                                  |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| Design Patterns - Creational.md     | Singleton, Factory Method, Abstract Factory, Builder, Prototype                         |
| Design Patterns - Structural.md     | Adapter, Decorator, Proxy, Facade, Composite                                            |
| Design Patterns - Behavioral.md     | Strategy, Observer, Command, Template Method, State, Chain of Responsibility            |
| Design Patterns - SOLID.md          | SRP, OCP, LSP, ISP, DIP                                                                 |
| Design Patterns - Anti-Patterns.md  | God Object, Spaghetti Code, Premature Optimization, Circular Dependencies, Feature Envy |
| Design Patterns - Additional GoF.md | Iterator, Visitor, Mediator, Memento                                                    |

### Microservices (microservices/)

| File                                          | Keywords (approximate)                                                               |
| --------------------------------------------- | ------------------------------------------------------------------------------------ |
| Microservices - Foundations.md                | What Are Microservices, Monolith vs Microservices, When NOT to Use, Modular Monolith |
| Microservices - Decomposition and DDD.md      | Service Decomposition, DDD, Bounded Context, Aggregate, Anti-Corruption Layer        |
| Microservices - Communication.md              | Inter-Service Communication, Sync vs Async, API Gateway, Service Discovery, BFF      |
| Microservices - Resilience.md                 | Circuit Breaker, Bulkhead, Timeout/Retry/Fallback, Saga, DLQ, Health Checks          |
| Microservices - Data Management.md            | DB per Service, Shared DB Anti-Pattern, CQRS, Event Sourcing, Eventual Consistency   |
| Microservices - Deployment and Delivery.md    | Blue-Green, Canary, Zero-Downtime, Feature Flags, Graceful Shutdown                  |
| Microservices - Observability.md              | Distributed Logging, Correlation ID, OpenTelemetry, Chaos Engineering                |
| Microservices - Infrastructure.md             | Service Mesh, Sidecar, Istio, Envoy, Platform Engineering, Multi-Tenancy             |
| Microservices - Migration.md                  | Monolith to Microservices, Strangler Fig, Cloud Migration, Technology Migration      |
| Microservices - Contracts and Organization.md | Service Contract, API Versioning, Contract Testing, Team Topologies, FinOps          |

### Async and Background Processing (async-background/)

| File                                                 | Keywords (approximate)                                                                   |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Async and Background Processing - Fundamentals.md    | Sync vs Async vs Parallel, Message Queue vs Event Bus, Delivery Guarantees, Idempotency  |
| Async and Background Processing - Message Brokers.md | RabbitMQ, Apache Kafka, Amazon SQS, Kafka Consumer Groups, Dead Letter Queues            |
| Async and Background Processing - Patterns.md        | Event-Driven Architecture, Saga Pattern, Outbox Pattern, Backpressure, Async API Design  |
| Async and Background Processing - Orchestration.md   | Temporal, AWS Step Functions, Cron Jobs, Distributed Scheduler, Celery, Quartz Scheduler |
| Async and Background Processing - Observability.md   | Async Observability, Consumer Lag, Error Handling, Flow Control, Architecture Selection  |

### React (react/)

| File                                   | Keywords (approximate)                                                                        |
| -------------------------------------- | --------------------------------------------------------------------------------------------- |
| React - Fundamentals.md                | Component Model, Mental Model, JSX, Functional Components, Props, Events, Conditional, Keys   |
| React - Hooks.md                       | useState, useEffect, useRef, useReducer, useMemo, useCallback, Custom Hooks, React 19         |
| React - State Management.md            | Lifting State, Context API, Redux Toolkit, Zustand, React Query, Prop Drilling Anti-Pattern   |
| React - Component Patterns.md          | Composition, Children/Render Props, HOC, Compound Components, TypeScript Patterns, Forms      |
| React - Performance.md                 | React.memo, Code Splitting, Profiling, Optimization Patterns, Concurrent Mode, Suspense       |
| React - Testing.md                     | React Testing Library, Test Strategies, Storybook, a11y Testing, Mocking (MSW)                |
| React - Routing and Styling.md         | React Router v6, Next.js App Router, CSS-in-JS, Tailwind, Accessibility, i18n                 |
| React - Server-Side and Next.js.md     | Next.js SSR/SSG/ISR, Server Components, Hydration, GraphQL, Apollo Client                     |
| React - Architecture and Production.md | Architecture Strategy, Micro-Frontends, Security (XSS/CSP), Trade-offs, Environment Variables |
| React - Internals and Advanced.md      | Fiber Architecture, Reconciliation, React Compiler, Class to Hooks Migration, Ecosystem Map   |
| React - Tooling.md                     | Project Setup (Vite/CRA), DevTools, ESLint, Prettier, Vite Build Config                       |
