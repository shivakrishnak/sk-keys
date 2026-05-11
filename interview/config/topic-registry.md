# Interview Mastery Dictionary - Topic Registry

> This registry maps topics to their interview folders and links them
> to existing dictionary categories where applicable. Start with core
> topics; grow organically as new topics are added.

---

## Registry Format

| Topic        | Folder         | Dictionary Sources           | Status                                       |
| ------------ | -------------- | ---------------------------- | -------------------------------------------- |
| [Topic Name] | [folder-name/] | [CODE1, CODE2, ...] or "new" | planned / scaffolded / generating / complete |

---

## Active Topics

| Topic                          | Folder             | Dictionary Sources | Status  | Description                                                         |
| ------------------------------ | ------------------ | ------------------ | ------- | ------------------------------------------------------------------- |
| Java                           | java/              | JVM, JLG           | planned | Core Java language, OOP, collections, modern Java features          |
| Java Concurrency               | java-concurrency/  | JCC                | planned | Threading, synchronization, virtual threads, concurrent collections |
| Spring                         | spring/            | SPR                | planned | Spring Core, Boot, MVC, Security, Data, Cloud                       |
| Hibernate                      | hibernate/         | JPH                | planned | ORM fundamentals, JPA, entity management, performance tuning        |
| SQL and Databases              | sql-and-databases/ | DBF, NDB           | planned | SQL queries, joins, indexing, transactions, NoSQL, replication      |
| Containers                     | containers/        | CTR                | planned | Docker fundamentals, images, networking, compose, security          |
| Kubernetes                     | kubernetes/        | K8S                | planned | Core resources, networking, storage, security, operations           |
| System Design                  | system-design/     | DST, MSV, SYD, SAP | planned | Distributed systems, microservices, architecture patterns           |
| React                          | react/             | RCT                | planned | Components, hooks, state management, performance, testing           |
| Security                       | security/          | SEC, IAM, CRY      | planned | Web security, authentication, authorization, cryptography           |
| Data Structures and Algorithms | dsa/               | DSA                | planned | Arrays, trees, graphs, sorting, dynamic programming                 |
| Caching                        | caching/           | CCH                | planned | Cache patterns, Redis, CDN, invalidation, consistency               |
| Messaging                      | messaging/         | MSG                | planned | Kafka, RabbitMQ, event-driven architecture, streaming               |
| CI/CD and DevOps               | cicd-and-devops/   | CCD, GIT, OBS      | planned | Pipelines, Git strategies, observability, SRE practices             |
| AI and RAG                     | ai-and-rag/        | AIF, LLM, RAG      | planned | LLM fundamentals, prompt engineering, RAG, agents, LLMOps           |

---

## Sub-topic File Mapping

Each topic is split into sub-topic files. Below are the planned file
splits for each topic. Files are grouped by relatedness - each file
should be self-sufficient.

### Java (java/)

| File                         | Keywords (approximate)                                                                    | Source IDs              |
| ---------------------------- | ----------------------------------------------------------------------------------------- | ----------------------- |
| Java - Basics.md             | Variables, Data Types, Operators, Control Flow, OOP Basics, Classes, Interfaces           | JLG-001 to JLG-020      |
| Java - Collections.md        | ArrayList, LinkedList, HashMap, TreeMap, HashSet, Queue, Iterator, Comparable             | JLG collections range   |
| Java - Exceptions and IO.md  | Exception Hierarchy, Checked vs Unchecked, Try-with-Resources, IO Streams, NIO            | JLG exceptions/IO range |
| Java - Java 8 Features.md    | Lambdas, Streams API, Optional, Functional Interfaces, Method References, Default Methods | JLG Java 8 range        |
| Java - Java 11 to 17.md      | Records, Sealed Classes, Pattern Matching, Text Blocks, Switch Expressions                | JLG modern range        |
| Java - Java 21 and Beyond.md | Virtual Threads Preview, Scoped Values, Structured Concurrency, String Templates          | JLG latest range        |
| Java - JVM Internals.md      | JVM Architecture, Class Loading, Memory Model, JIT Compilation, GC Overview               | JVM core range          |
| Java - Garbage Collection.md | GC Algorithms, G1, ZGC, Shenandoah, GC Tuning, Memory Leaks                               | JVM GC range            |

### Spring (spring/)

| File                     | Keywords (approximate)                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| Spring - Core and IoC.md | IoC Container, Dependency Injection, Bean Lifecycle, ApplicationContext, Configuration     |
| Spring - Annotations.md  | Component Scanning, Autowiring, Qualifier, Conditional, Profile, Configuration Annotations |
| Spring - Boot.md         | Auto-Configuration, Starters, Actuator, Properties, Embedded Server, DevTools              |
| Spring - MVC and REST.md | DispatcherServlet, Controllers, Request Mapping, Exception Handling, Content Negotiation   |
| Spring - Data and JPA.md | Spring Data Repositories, Query Methods, Specifications, Auditing, Transactions            |
| Spring - Security.md     | Authentication, Authorization, OAuth2, JWT, CORS, CSRF Protection, Method Security         |
| Spring - Cloud.md        | Service Discovery, Config Server, Circuit Breaker, API Gateway, Distributed Tracing        |

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

| File                             | Keywords (approximate)                                                 |
| -------------------------------- | ---------------------------------------------------------------------- |
| System Design - Fundamentals.md  | Scalability, Availability, Reliability, Load Balancing, CDN, DNS       |
| System Design - Patterns.md      | Circuit Breaker, Retry, Bulkhead, Saga, CQRS, Event Sourcing           |
| System Design - Microservices.md | Service Decomposition, API Gateway, Service Discovery, Data Ownership  |
| System Design - Data at Scale.md | Sharding, Partitioning, Replication, Consensus, Eventual Consistency   |
| System Design - Case Studies.md  | URL Shortener, Chat System, News Feed, Rate Limiter, Distributed Cache |

---

## Adding New Topics

To add a new topic to this registry:

1. Choose a descriptive topic name and lowercase folder name
2. Check if a dictionary category exists (look at Category Code Registry
   in `GENERATOR_PROMPT.md` or `copilot-instructions.md`)
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
