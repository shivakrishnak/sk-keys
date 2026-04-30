
const fs = require('fs');
const path = require('path');
const DOCS = 'C:/ASK/MyWorkspace/sk-keys/docs';

function writeIndex(folder, title, slug, navOrder, range, desc, keywords) {
  const dir = path.join(DOCS, folder);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const rows = keywords.map(([n, k, d]) => `| ${n} | ${k} | ${d} |`).join('\n');
  const content = `---
layout: default
title: "${title}"
parent: "Documentation"
nav_order: ${navOrder}
has_children: true
permalink: /${slug}/
---

# ${title}

${desc}

**Keywords:** ${range} (${keywords.length} terms)

| # | Keyword | Difficulty |
|---|---|---|
${rows}
`;
  fs.writeFileSync(path.join(dir, 'index.md'), content, 'utf8');
  console.log(`✓ ${folder}/index.md (${keywords.length} keywords)`);
}

// ── 01 CS Fundamentals ─────────────────────────────────────
writeIndex("CS Fundamentals","CS Fundamentals — Paradigms & Theory","cs-fundamentals",1,"001–030",
"Programming paradigms, type systems, OOP pillars, functional concepts, and theoretical foundations.",[
["001","Imperative Programming","★☆☆"],["002","Declarative Programming","★☆☆"],["003","Object-Oriented Programming (OOP)","★☆☆"],
["004","Functional Programming","★★☆"],["005","Procedural Programming","★☆☆"],["006","Event-Driven Programming","★★☆"],
["007","Reactive Programming","★★☆"],["008","Aspect-Oriented Programming","★★☆"],["009","Metaprogramming","★★★"],
["010","Type Systems (Static vs Dynamic)","★★☆"],["011","Strong vs Weak Typing","★☆☆"],["012","Compiled vs Interpreted Languages","★☆☆"],
["013","Memory Management Models","★★☆"],["014","Concurrency vs Parallelism","★★☆"],["015","Synchronous vs Asynchronous","★☆☆"],
["016","Abstraction","★☆☆"],["017","Encapsulation","★☆☆"],["018","Polymorphism","★☆☆"],["019","Inheritance","★☆☆"],
["020","Composition over Inheritance","★★☆"],["021","Recursion","★★☆"],["022","Tail Recursion","★★★"],
["023","Turing Completeness","★★★"],["024","Church-Turing Thesis","★★★"],["025","Lambda Calculus","★★★"],
["026","First-Class Functions","★★☆"],["027","Higher-Order Functions","★★☆"],["028","Side Effects","★★☆"],
["029","Referential Transparency","★★★"],["030","Idempotency","★★☆"]]);

// ── 02 DSA ──────────────────────────────────────────────────
writeIndex("DSA","Data Structures & Algorithms","dsa",2,"031–090",
"Core data structures, algorithm paradigms, complexity analysis, sorting, and graph algorithms.",[
["031","Array","★☆☆"],["032","LinkedList","★☆☆"],["033","Stack","★☆☆"],["034","Queue / Deque","★☆☆"],["035","HashMap","★☆☆"],
["036","TreeMap","★★☆"],["037","Heap (Min/Max)","★★☆"],["038","Priority Queue","★★☆"],["039","Trie","★★☆"],["040","Graph","★★☆"],
["041","Segment Tree","★★★"],["042","Fenwick Tree (BIT)","★★★"],["043","Skip List","★★★"],["044","Bloom Filter","★★★"],
["045","Consistent Hash Ring","★★★"],["046","LRU Cache","★★☆"],["047","LFU Cache","★★★"],
["048","Time Complexity / Big-O","★★☆"],["049","Space Complexity","★★☆"],["050","Amortized Analysis","★★★"],
["051","Memoization","★★☆"],["052","Tabulation (Bottom-Up DP)","★★☆"],["053","Divide and Conquer","★★☆"],
["054","Greedy Algorithm","★★☆"],["055","Dynamic Programming","★★★"],["056","BFS","★★☆"],["057","DFS","★★☆"],
["058","Topological Sort","★★☆"],["059","Dijkstra","★★☆"],["060","Bellman-Ford","★★★"],["061","A* Search","★★★"],
["062","Union-Find (Disjoint Set)","★★☆"],["063","Kruskal / Prim","★★★"],["064","Quicksort","★★☆"],["065","Mergesort","★★☆"],
["066","Timsort","★★★"],["067","Heapsort","★★★"],["068","Radix Sort","★★★"],["069","Two Pointer","★★☆"],
["070","Sliding Window","★★☆"],["071","Binary Search","★★☆"],["072","Backtracking","★★☆"],["073","Bit Manipulation","★★★"],
["074","String Matching (KMP, Rabin-Karp)","★★★"],["075","Hashing Techniques","★★☆"],["076","Graph Coloring","★★★"],
["077","Minimum Spanning Tree","★★★"],["078","Strongly Connected Components","★★★"],
["079","Longest Common Subsequence","★★★"],["080","Knapsack Problem","★★★"],["081","NP-Complete Problems","★★★"],
["082","P vs NP","★★★"],["083","Complexity Classes","★★★"],["084","Space-Time Trade-off","★★☆"],
["085","Randomized Algorithms","★★★"],["086","Approximation Algorithms","★★★"],
["087","Monte Carlo vs Las Vegas Algorithms","★★★"],["088","Sorting Stability","★★☆"],
["089","In-Place vs Out-of-Place","★★☆"],["090","Recursion vs Iteration Trade-offs","★★☆"]]);

// ── 03 Operating Systems ────────────────────────────────────
writeIndex("Operating Systems","Operating Systems","operating-systems",3,"091–125",
"Processes, threads, memory management, I/O models, synchronization primitives, and OS internals.",[
["091","Process","★☆☆"],["092","Thread","★☆☆"],["093","Fiber / Coroutine","★★☆"],["094","Process vs Thread","★☆☆"],
["095","Context Switch","★★☆"],["096","Scheduler / Preemption","★★☆"],["097","User Space vs Kernel Space","★★☆"],
["098","System Call (syscall)","★★☆"],["099","Virtual Memory","★★☆"],["100","Paging","★★☆"],["101","Page Fault","★★☆"],
["102","TLB (Translation Lookaside Buffer)","★★★"],["103","Memory-Mapped File (mmap)","★★★"],
["104","Blocking I/O","★★☆"],["105","Non-Blocking I/O","★★☆"],["106","Async I/O","★★☆"],
["107","epoll / kqueue / io_uring","★★★"],["108","File Descriptor","★★☆"],["109","Page Cache","★★★"],
["110","Zero-Copy (sendfile)","★★★"],["111","NUMA","★★★"],["112","Cache Line","★★★"],["113","False Sharing","★★★"],
["114","Mutex","★★☆"],["115","Semaphore","★★☆"],["116","Spinlock","★★★"],["117","Condition Variable","★★☆"],
["118","Deadlock","★★☆"],["119","Livelock","★★★"],["120","Starvation","★★☆"],["121","Fork / Exec","★★☆"],
["122","Signal Handling","★★★"],["123","Inode / File System","★★☆"],["124","Swap / Thrashing","★★★"],
["125","Buddy System / Slab Allocator","★★★"]]);

// ── 04 Linux ────────────────────────────────────────────────
writeIndex("Linux","Linux","linux",4,"126–165",
"Linux filesystem, shell scripting, process management, networking tools, performance tuning, and security.",[
["126","Linux File System Hierarchy","★☆☆"],["127","File Permissions (chmod, chown)","★☆☆"],["128","Users and Groups","★☆☆"],
["129","Shell (bash, zsh)","★☆☆"],["130","Shell Scripting","★★☆"],["131","stdin / stdout / stderr","★☆☆"],
["132","Pipes and Redirection","★☆☆"],["133","Process Management (ps, top, kill)","★☆☆"],
["134","Systemd / Init System","★★☆"],["135","Cron Jobs","★☆☆"],["136","Environment Variables (Linux)","★☆☆"],
["137","Package Managers (apt, yum, dnf)","★☆☆"],["138","SSH","★☆☆"],["139","SCP / rsync","★☆☆"],
["140","curl / wget","★☆☆"],["141","grep / awk / sed","★★☆"],["142","find / xargs","★★☆"],
["143","tar / gzip / zip","★☆☆"],["144","Symbolic Links / Hard Links","★★☆"],
["145","/proc File System","★★★"],["146","/sys File System","★★★"],
["147","Linux Networking (ip, ss, netstat)","★★☆"],["148","iptables / nftables","★★★"],
["149","tcpdump / Wireshark","★★★"],["150","strace / ltrace","★★★"],["151","lsof","★★☆"],
["152","ulimit","★★★"],["153","swap Management","★★☆"],["154","Memory (free, vmstat)","★★☆"],
["155","Disk I/O (iostat, iotop)","★★☆"],["156","Kernel Modules","★★★"],["157","Linux Namespaces","★★★"],
["158","Cgroups","★★★"],["159","SELinux / AppArmor","★★★"],["160","Linux Security Hardening","★★★"],
["161","Signals (SIGTERM, SIGKILL, SIGHUP)","★★☆"],["162","Zombie Processes","★★☆"],
["163","/etc/hosts / DNS Resolution","★★☆"],["164","tmux / screen","★☆☆"],["165","Linux Performance Tuning","★★★"]]);

// ── 05 Networking ────────────────────────────────────────────
writeIndex("Networking","Networking","networking",5,"166–205",
"OSI model, TCP/IP, protocols, DNS, load balancing, security, and network observability.",[
["166","OSI Model (7 Layers)","★☆☆"],["167","TCP/IP Stack","★☆☆"],["168","TCP","★★☆"],["169","UDP","★★☆"],
["170","QUIC","★★★"],["171","TCP Handshake (3-Way)","★★☆"],["172","TCP Teardown","★★☆"],
["173","Congestion Control","★★★"],["174","Flow Control","★★★"],["175","Sliding Window","★★★"],
["176","IP Addressing","★☆☆"],["177","Subnet / CIDR","★★☆"],["178","NAT","★★☆"],["179","DNS","★☆☆"],
["180","DNS Resolution Flow","★★☆"],["181","CDN","★★☆"],["182","Anycast","★★★"],
["183","Socket / Port / Ephemeral Port","★★☆"],["184","Firewall","★★☆"],["185","VPN","★★☆"],
["186","Proxy vs Reverse Proxy","★★☆"],["187","Load Balancer (L4 vs L7)","★★☆"],
["188","Packet Loss / Latency / Jitter","★★☆"],["189","Bandwidth vs Throughput","★★☆"],
["190","Network Latency Optimization","★★★"],["191","BGP","★★★"],["192","DHCP","★☆☆"],
["193","ARP","★★☆"],["194","ICMP / ping / traceroute","★☆☆"],["195","Network Topologies","★☆☆"],
["196","Zero Trust Networking","★★★"],["197","East-West vs North-South Traffic","★★★"],
["198","Service Discovery (Network)","★★★"],["199","Network Policies","★★★"],
["200","Overlay Networks","★★★"],["201","VLAN","★★★"],["202","mTLS","★★★"],
["203","TLS/SSL","★★☆"],["204","Certificate Authority (CA)","★★☆"],["205","Network Observability","★★★"]]);

// ── 06 HTTP & APIs ───────────────────────────────────────────
writeIndex("HTTP & APIs","HTTP & APIs","http-apis",6,"206–260",
"HTTP versions, REST, GraphQL, gRPC, WebSocket, API security, authentication, and API design best practices.",[
["206","HTTP/1.1","★☆☆"],["207","HTTP/2","★★☆"],["208","HTTP/3","★★★"],["209","HTTP Methods","★☆☆"],
["210","HTTP Status Codes","★☆☆"],["211","HTTP Headers","★★☆"],["212","Keep-Alive / Connection Pooling","★★☆"],
["213","REST","★☆☆"],["214","RESTful Constraints","★★☆"],["215","HATEOAS","★★★"],
["216","Idempotency in HTTP","★★☆"],["217","GraphQL","★★☆"],["218","GraphQL Schema","★★☆"],
["219","GraphQL Resolvers","★★☆"],["220","GraphQL N+1 Problem","★★★"],["221","GraphQL Subscriptions","★★★"],
["222","gRPC","★★☆"],["223","Protocol Buffers","★★☆"],["224","gRPC Streaming","★★★"],
["225","SOAP","★★☆"],["226","WSDL","★★☆"],["227","WebSocket","★★☆"],
["228","Server-Sent Events (SSE)","★★☆"],["229","Long Polling","★★☆"],["230","Webhook","★★☆"],
["231","API Gateway","★★☆"],["232","API Versioning","★★☆"],["233","API Rate Limiting","★★☆"],
["234","API Authentication","★★☆"],["235","OAuth2","★★☆"],["236","JWT","★★☆"],["237","OIDC","★★★"],
["238","API Keys","★☆☆"],["239","HMAC","★★★"],["240","CORS","★★☆"],["241","XSS","★★☆"],
["242","CSRF","★★☆"],["243","SQL Injection","★★☆"],["244","SSRF","★★★"],
["245","Content Negotiation","★★☆"],["246","OpenAPI / Swagger","★★☆"],
["247","API Contract Testing","★★★"],["248","API Mocking","★★☆"],
["249","API Backward Compatibility","★★★"],["250","BFF (Backend for Frontend)","★★★"],
["251","API Caching","★★☆"],["252","ETag / Cache-Control","★★★"],["253","Pagination","★★☆"],
["254","API Throttling","★★☆"],["255","API Documentation","★☆☆"],
["256","API Design Best Practices","★★☆"],["257","Hypermedia","★★★"],
["258","API Deprecation Strategy","★★★"],["259","API Observability","★★★"],
["260","API Security Best Practices","★★★"]]);

// ── 07 Java JVM ──────────────────────────────────────────────
writeIndex("Java","Java & JVM Internals","java",7,"261–310",
"JVM architecture, memory model, garbage collection algorithms, JIT compilation, GraalVM, and JVM tuning.",[
["261","JVM","★☆☆"],["262","JRE","★☆☆"],["263","JDK","★☆☆"],["264","Bytecode","★★☆"],["265","Class Loader","★★☆"],
["266","Stack Memory","★★☆"],["267","Heap Memory","★★☆"],["268","Metaspace","★★☆"],["269","Stack Frame","★★★"],
["270","Operand Stack","★★★"],["271","Local Variable Table","★★★"],["272","Object Header","★★★"],
["273","Escape Analysis","★★★"],["274","Memory Barrier","★★★"],["275","Happens-Before","★★★"],
["276","GC Roots","★★★"],["277","Reference Types (Strong, Soft, Weak, Phantom)","★★★"],
["278","Young Generation","★★☆"],["279","Eden Space","★★☆"],["280","Survivor Space","★★☆"],
["281","Old Generation","★★☆"],["282","Minor GC","★★☆"],["283","Major GC","★★★"],["284","Full GC","★★★"],
["285","Stop-The-World (STW)","★★★"],["286","Serial GC","★★☆"],["287","Parallel GC","★★☆"],
["288","CMS (Concurrent Mark Sweep)","★★★"],["289","G1GC","★★★"],["290","ZGC","★★★"],
["291","Shenandoah GC","★★★"],["292","GC Tuning","★★★"],["293","GC Logs","★★☆"],["294","GC Pause","★★★"],
["295","Throughput vs Latency (GC)","★★★"],["296","Finalization","★★★"],["297","JIT Compiler","★★★"],
["298","C1 / C2 Compiler","★★★"],["299","Tiered Compilation","★★★"],["300","Method Inlining","★★★"],
["301","Deoptimization","★★★"],["302","OSR (On-Stack Replacement)","★★★"],
["303","AOT (Ahead-of-Time Compilation)","★★★"],["304","GraalVM","★★★"],["305","Native Image","★★★"],
["306","TLAB","★★★"],["307","Safepoint","★★★"],["308","Card Table","★★★"],
["309","Write Barrier","★★★"],["310","Remembered Set","★★★"]]);

// ── 08 Java Language ─────────────────────────────────────────
writeIndex("Java Language","Java Language","java-language",8,"311–330",
"Java language features: generics, reflection, records, sealed classes, pattern matching, and functional APIs.",[
["311","String Pool / String Interning","★★☆"],["312","Autoboxing / Unboxing","★★☆"],
["313","Integer Cache","★★★"],["314","Generics","★★☆"],["315","Type Erasure","★★★"],
["316","Bounded Wildcards","★★★"],["317","Covariance / Contravariance","★★★"],["318","Varargs","★★☆"],
["319","Reflection","★★★"],["320","Annotation Processing (APT)","★★★"],
["321","Serialization / Deserialization","★★☆"],["322","Records (Java 16+)","★★☆"],
["323","Sealed Classes (Java 17+)","★★★"],["324","Pattern Matching (Java 21+)","★★★"],
["325","invokedynamic","★★★"],["326","Optional","★★☆"],["327","Stream API","★★☆"],
["328","Functional Interfaces","★★☆"],["329","Method References","★★☆"],["330","Lambda Expressions","★★☆"]]);

// ── 09 Java Concurrency ──────────────────────────────────────
writeIndex("Java Concurrency","Java Concurrency","java-concurrency",9,"331–370",
"Java threading, synchronization, concurrent data structures, executors, virtual threads, and the Java Memory Model.",[
["331","Thread (Java)","★☆☆"],["332","Runnable","★☆☆"],["333","Callable","★★☆"],["334","Future","★★☆"],
["335","CompletableFuture","★★★"],["336","Thread Lifecycle","★★☆"],["337","Thread States","★★☆"],
["338","synchronized","★★☆"],["339","volatile","★★★"],["340","wait / notify / notifyAll","★★★"],
["341","ReentrantLock","★★★"],["342","ReadWriteLock","★★★"],["343","StampedLock","★★★"],
["344","ThreadLocal","★★★"],["345","Java Memory Model (JMM)","★★★"],["346","Race Condition","★★☆"],
["347","CAS (Compare-And-Swap)","★★★"],["348","Optimistic Locking (Java)","★★★"],["349","Executor","★★☆"],
["350","ExecutorService","★★☆"],["351","ThreadPoolExecutor","★★★"],["352","ForkJoinPool","★★★"],
["353","Virtual Threads (Project Loom)","★★★"],["354","Carrier Thread","★★★"],["355","Continuation","★★★"],
["356","Semaphore (Java)","★★☆"],["357","CountDownLatch","★★☆"],["358","CyclicBarrier","★★★"],
["359","Phaser","★★★"],["360","BlockingQueue","★★☆"],["361","ConcurrentHashMap","★★★"],
["362","CopyOnWriteArrayList","★★★"],["363","Atomic Classes","★★★"],["364","VarHandle","★★★"],
["365","Structured Concurrency","★★★"],["366","Scoped Values","★★★"],["367","Thread Dump Analysis","★★★"],
["368","Deadlock Detection (Java)","★★★"],["369","Lock Striping","★★★"],["370","Actor Model","★★★"]]);

// ── 10 Spring Core ───────────────────────────────────────────
writeIndex("Spring","Spring Core","spring",10,"371–410",
"Spring IoC/DI, AOP, MVC, data access, transactions, Boot auto-configuration, and reactive programming.",[
["371","IoC (Inversion of Control)","★☆☆"],["372","DI (Dependency Injection)","★☆☆"],
["373","ApplicationContext","★★☆"],["374","BeanFactory","★★☆"],["375","Bean","★☆☆"],
["376","Bean Lifecycle","★★☆"],["377","Bean Scope","★★☆"],["378","BeanPostProcessor","★★★"],
["379","BeanFactoryPostProcessor","★★★"],["380","@Autowired","★★☆"],
["381","@Qualifier / @Primary","★★☆"],["382","@Configuration / @Bean","★★☆"],
["383","Circular Dependency","★★★"],["384","CGLIB Proxy","★★★"],["385","JDK Dynamic Proxy","★★★"],
["386","AOP (Aspect-Oriented Programming)","★★☆"],["387","Aspect","★★☆"],["388","Advice","★★☆"],
["389","Pointcut","★★☆"],["390","JoinPoint","★★☆"],["391","Weaving","★★★"],
["392","DispatcherServlet","★★☆"],["393","HandlerMapping","★★★"],["394","Filter vs Interceptor","★★☆"],
["395","@Transactional","★★☆"],["396","Transaction Propagation","★★★"],
["397","Transaction Isolation Levels","★★★"],["398","N+1 Problem","★★★"],
["399","Lazy vs Eager Loading","★★☆"],["400","HikariCP","★★☆"],["401","Auto-Configuration","★★★"],
["402","Spring Boot Actuator","★★☆"],["403","Spring Boot Startup Lifecycle","★★★"],
["404","WebFlux / Reactive","★★★"],["405","Mono / Flux","★★★"],["406","Backpressure (Spring)","★★★"],
["407","Spring Security","★★★"],["408","Spring Data JPA","★★☆"],
["409","Spring Cloud","★★★"],["410","Spring Boot Testing","★★☆"]]);

// ── 11 Databases ─────────────────────────────────────────────
writeIndex("Databases","Database Fundamentals","databases",11,"411–450",
"ACID, transaction isolation, indexing, locking, replication, sharding, and schema evolution.",[
["411","ACID","★☆☆"],["412","Atomicity","★☆☆"],["413","Consistency (DB)","★☆☆"],["414","Isolation","★★☆"],
["415","Durability","★★☆"],["416","Transaction","★☆☆"],["417","Commit / Rollback / Savepoint","★☆☆"],
["418","Isolation Levels","★★☆"],["419","Dirty Read","★★☆"],["420","Non-Repeatable Read","★★☆"],
["421","Phantom Read","★★☆"],["422","MVCC","★★★"],["423","WAL (Write-Ahead Log)","★★★"],
["424","Redo Log / Undo Log","★★★"],["425","B-Tree","★★☆"],["426","B+ Tree","★★★"],
["427","LSM Tree","★★★"],["428","Index Types (B-Tree, Hash, Composite, Covering)","★★☆"],
["429","Query Planner / Execution Plan","★★★"],["430","EXPLAIN","★★☆"],["431","Normalization","★★☆"],
["432","Denormalization","★★☆"],["433","Foreign Key / Referential Integrity","★★☆"],
["434","Locking (Row, Table, Gap, Next-Key)","★★★"],["435","Deadlock Detection (DB)","★★★"],
["436","Connection Pooling (DB)","★★☆"],["437","Prepared Statements","★★☆"],["438","Read Replica","★★☆"],
["439","Write Amplification","★★★"],["440","Partitioning (DB)","★★★"],["441","Materialized View","★★★"],
["442","Stored Procedure / Trigger","★★☆"],["443","ORM Patterns","★★☆"],
["444","Optimistic vs Pessimistic Locking","★★★"],["445","Database Replication","★★★"],
["446","Master-Slave Replication","★★☆"],["447","Multi-Master Replication","★★★"],
["448","Database Sharding","★★★"],["449","Database Migration","★★☆"],["450","Schema Evolution","★★★"]]);

// ── 12 NoSQL ─────────────────────────────────────────────────
writeIndex("NoSQL","NoSQL & Distributed Databases","nosql",12,"451–475",
"Document stores, key-value, column-family, graph DBs, vector databases, and distributed data patterns.",[
["451","Document Store","★★☆"],["452","Key-Value Store","★★☆"],["453","Column Family","★★★"],
["454","Graph DB","★★★"],["455","Time-Series DB","★★★"],["456","Search Engine (Elasticsearch)","★★★"],
["457","Eventual Consistency in NoSQL","★★★"],["458","CRDTs","★★★"],["459","Vector Database","★★★"],
["460","NewSQL","★★★"],["461","MongoDB Patterns","★★☆"],["462","Redis Data Structures","★★☆"],
["463","Redis Persistence","★★★"],["464","Cassandra Data Modeling","★★★"],["465","DynamoDB Patterns","★★★"],
["466","Hot Partition Problem","★★★"],["467","Wide Column vs Document","★★★"],
["468","Polyglot Persistence","★★★"],["469","CAP Theorem (DB)","★★★"],
["470","Distributed Transactions","★★★"],["471","Two-Phase Commit (2PC)","★★★"],
["472","Saga Pattern (DB)","★★★"],["473","Change Data Capture (CDC)","★★★"],
["474","Database Proxy (PgBouncer)","★★★"],["475","Data Locality","★★★"]]);

// ── 13 Caching ───────────────────────────────────────────────
writeIndex("Caching","Caching","caching",13,"476–495",
"Cache patterns, eviction policies, stampede prevention, distributed caching, and Redis internals.",[
["476","Cache-Aside","★★☆"],["477","Read-Through","★★☆"],["478","Write-Through","★★☆"],
["479","Write-Behind","★★★"],["480","Cache Invalidation","★★★"],["481","TTL","★☆☆"],
["482","Eviction Policies (LRU, LFU, FIFO)","★★☆"],["483","Cache Stampede","★★★"],
["484","Thundering Herd","★★★"],["485","Negative Caching","★★★"],["486","Distributed Cache","★★★"],
["487","Cache Coherence","★★★"],["488","Multi-Level Cache","★★★"],["489","Cache Warming","★★★"],
["490","Write-Around","★★★"],["491","Cache Aside vs Read-Through Comparison","★★★"],
["492","Consistent Hashing in Cache","★★★"],["493","Redis Cluster","★★★"],
["494","Memcached vs Redis","★★☆"],["495","Local Cache vs Distributed Cache","★★☆"]]);

// ── 14 Data Engineering ──────────────────────────────────────
writeIndex("Data Engineering","Data Fundamentals","data-engineering",14,"496–530",
"Data formats, storage models, data lake/warehouse/lakehouse architectures, modeling, and governance.",[
["496","Data Types (Primitive, Complex, Semi-Structured)","★☆☆"],
["497","Structured vs Unstructured Data","★☆☆"],["498","Semi-Structured Data","★☆☆"],
["499","Data Formats (JSON, XML, YAML, CSV)","★☆☆"],
["500","Binary Formats (Avro, Parquet, ORC, Protobuf)","★★☆"],
["501","Columnar vs Row Storage","★★☆"],["502","Avro","★★☆"],["503","Parquet","★★☆"],["504","ORC","★★☆"],
["505","Delta Lake","★★★"],["506","Apache Iceberg","★★★"],["507","Hudi","★★★"],
["508","Data Compression (gzip, snappy, zstd, lz4)","★★☆"],["509","Serialization Formats","★★☆"],
["510","Schema Registry","★★★"],["511","Schema Evolution (Data)","★★★"],["512","Data Modeling","★★☆"],
["513","Star Schema","★★☆"],["514","Snowflake Schema","★★☆"],["515","Data Vault","★★★"],
["516","Dimensional Modeling","★★☆"],["517","Fact Table vs Dimension Table","★★☆"],
["518","SCD (Slowly Changing Dimension)","★★★"],["519","Data Lake","★★☆"],
["520","Data Warehouse","★★☆"],["521","Data Lakehouse","★★★"],["522","Data Mesh","★★★"],
["523","Data Fabric","★★★"],["524","Data Lineage","★★★"],["525","Data Catalog","★★★"],
["526","Data Quality","★★★"],["527","Data Governance","★★★"],["528","Master Data Management","★★★"],
["529","OLTP vs OLAP","★★☆"],["530","ETL vs ELT","★★☆"]]);

// ── 15 Big Data & Streaming ──────────────────────────────────
writeIndex("Big Data & Streaming","Big Data & Streaming","big-data-streaming",15,"531–570",
"Distributed computing, MapReduce, Spark, Kafka, Flink, stream processing patterns, and messaging architectures.",[
["531","Distributed Computing","★★☆"],["532","MapReduce","★★☆"],["533","Apache Hadoop","★★☆"],
["534","HDFS","★★★"],["535","Apache Spark","★★★"],["536","Spark RDD","★★★"],
["537","Spark DataFrame / Dataset","★★★"],["538","Spark Streaming","★★★"],["539","Apache Flink","★★★"],
["540","Apache Kafka","★★☆"],["541","Kafka Topic / Partition / Offset","★★☆"],
["542","Consumer Group","★★☆"],["543","ISR (In-Sync Replicas)","★★★"],["544","Log Compaction","★★★"],
["545","Exactly-Once Semantics","★★★"],["546","Kafka Streams","★★★"],["547","KSQL","★★★"],
["548","Consumer Lag","★★★"],["549","Idempotent Producer","★★★"],["550","Transactional Producer","★★★"],
["551","Dead Letter Queue (DLQ)","★★☆"],["552","Fan-Out Pattern","★★☆"],["553","Message Ordering","★★★"],
["554","Windowing (Tumbling, Sliding, Session)","★★★"],["555","Watermark","★★★"],
["556","Event Time vs Processing Time","★★★"],["557","Lambda Architecture","★★★"],
["558","Kappa Architecture","★★★"],["559","Batch vs Stream Processing","★★☆"],
["560","Backpressure (Streaming)","★★★"],["561","Apache Beam","★★★"],["562","Pulsar","★★★"],
["563","RabbitMQ","★★☆"],["564","Message Broker vs Event Bus","★★☆"],
["565","Point-to-Point vs Pub-Sub","★★☆"],["566","Competing Consumers","★★☆"],
["567","Outbox Pattern","★★★"],["568","Transactional Outbox","★★★"],
["569","Event-Driven Architecture","★★★"],["570","Change Data Capture (CDC)","★★★"]]);

// ── 16 Distributed Systems ───────────────────────────────────
writeIndex("Distributed Systems","Distributed Systems","distributed-systems",16,"571–625",
"CAP theorem, consistency models, consensus algorithms, distributed locking, failure modes, and resilience patterns.",[
["571","CAP Theorem","★★☆"],["572","PACELC","★★★"],["573","Consistency Models","★★★"],
["574","Strong Consistency","★★★"],["575","Eventual Consistency","★★☆"],
["576","Causal Consistency","★★★"],["577","Linearizability","★★★"],["578","Serializability","★★★"],
["579","BASE","★★☆"],["580","Lamport Clock","★★★"],["581","Vector Clock","★★★"],
["582","Clock Skew / Clock Drift","★★★"],["583","Total Order / Partial Order","★★★"],
["584","Happened-Before","★★★"],["585","Leader Election","★★★"],["586","Raft","★★★"],
["587","Paxos","★★★"],["588","Replication Strategies","★★★"],["589","Log Replication","★★★"],
["590","State Machine Replication","★★★"],["591","Quorum","★★★"],["592","Split Brain","★★★"],
["593","Fencing / Epoch","★★★"],["594","Failure Modes (Crash, Byzantine)","★★★"],
["595","Two-Phase Commit (2PC)","★★★"],["596","Three-Phase Commit (3PC)","★★★"],
["597","Distributed Locking","★★★"],["598","Consistent Hashing","★★★"],["599","Virtual Nodes","★★★"],
["600","Gossip Protocol","★★★"],["601","Heartbeat","★★☆"],["602","Circuit Breaker","★★☆"],
["603","Bulkhead","★★☆"],["604","Retry with Backoff","★★☆"],["605","Idempotency (Distributed)","★★☆"],
["606","Timeout","★★☆"],["607","Fallback","★★☆"],["608","Graceful Degradation","★★★"],
["609","Saga Pattern","★★★"],["610","Choreography vs Orchestration","★★★"],
["611","Distributed Tracing","★★★"],["612","Correlation ID","★★☆"],["613","Service Mesh","★★★"],
["614","Sidecar Pattern","★★★"],["615","CQRS","★★★"],["616","Event Sourcing","★★★"],
["617","Outbox Pattern","★★★"],["618","Two Generals Problem","★★★"],
["619","Byzantine Fault Tolerance","★★★"],["620","FLP Impossibility","★★★"],
["621","CRDT","★★★"],["622","Conflict Resolution Strategies","★★★"],["623","Anti-Entropy","★★★"],
["624","Read Repair","★★★"],["625","Hinted Handoff","★★★"]]);

// ── 17 Microservices ─────────────────────────────────────────
writeIndex("Microservices","Microservices","microservices",17,"626–680",
"Service decomposition, DDD, discovery, resilience patterns, CQRS, event sourcing, and deployment strategies.",[
["626","Monolith vs Microservices","★☆☆"],["627","Modular Monolith","★★☆"],
["628","Service Decomposition","★★☆"],["629","Domain-Driven Design (DDD)","★★★"],
["630","Bounded Context","★★★"],["631","Aggregate","★★★"],["632","Ubiquitous Language","★★★"],
["633","Anti-Corruption Layer","★★★"],["634","Strangler Fig Pattern","★★★"],
["635","Service Registry","★★☆"],["636","Service Discovery","★★☆"],
["637","Client-Side vs Server-Side Discovery","★★★"],["638","Health Check Patterns","★★☆"],
["639","Inter-Service Communication","★★☆"],["640","Synchronous vs Async Communication","★★☆"],
["641","API Gateway (Microservices)","★★☆"],["642","Backend for Frontend (BFF)","★★★"],
["643","Service Mesh (Microservices)","★★★"],["644","Istio","★★★"],["645","Envoy Proxy","★★★"],
["646","Resilience4j","★★★"],["647","Circuit Breaker (Microservices)","★★★"],
["648","Bulkhead Pattern","★★★"],["649","Rate Limiting (Microservices)","★★☆"],
["650","Timeout Strategy","★★☆"],["651","Retry Strategy","★★☆"],["652","Fallback Strategy","★★☆"],
["653","Saga Pattern (Microservices)","★★★"],["654","Distributed Transaction","★★★"],
["655","Event-Driven Microservices","★★★"],["656","Eventual Consistency (Microservices)","★★★"],
["657","Data Isolation per Service","★★★"],["658","CQRS in Microservices","★★★"],
["659","Event Sourcing in Microservices","★★★"],["660","Shared Database Anti-Pattern","★★★"],
["661","Database per Service","★★★"],["662","Consumer-Driven Contract Testing","★★★"],
["663","Pact (Contract Testing)","★★★"],["664","Cross-Cutting Concerns","★★★"],
["665","Distributed Logging","★★★"],["666","Correlation ID (Microservices)","★★☆"],
["667","OpenTelemetry (Microservices)","★★★"],["668","Chaos Engineering","★★★"],
["669","Canary Deployment (Microservices)","★★★"],["670","Blue-Green Deployment","★★☆"],
["671","Feature Flags (Microservices)","★★☆"],["672","Graceful Shutdown (Microservices)","★★★"],
["673","Zero-Downtime Deployment","★★★"],["674","Service Contract","★★★"],
["675","Backward Compatibility","★★★"],["676","Versioning Strategy","★★★"],
["677","Twelve-Factor App","★★☆"],["678","Sidecar Pattern (Microservices)","★★★"],
["679","Ambassador Pattern","★★★"],["680","Adapter Pattern (Microservices)","★★★"]]);

// ── 18 System Design ─────────────────────────────────────────
writeIndex("System Design","System Design","system-design",18,"681–725",
"Scaling, load balancing, rate limiting, distributed locks, sharding, and classic system design problems.",[
["681","Vertical Scaling","★☆☆"],["682","Horizontal Scaling","★☆☆"],["683","Load Balancing","★★☆"],
["684","Round Robin","★☆☆"],["685","Least Connections","★★☆"],
["686","Consistent Hashing (Load Balancing)","★★★"],["687","Sticky Sessions","★★☆"],
["688","Session Affinity","★★☆"],["689","Auto Scaling","★★☆"],["690","SLA / SLO / SLI","★★☆"],
["691","Error Budget","★★★"],["692","MTTR / MTBF","★★☆"],["693","RTO / RPO","★★★"],
["694","Redundancy / Failover","★★☆"],["695","Active-Active","★★★"],["696","Active-Passive","★★☆"],
["697","Disaster Recovery","★★★"],["698","Geo-Replication","★★★"],["699","Multi-Region Architecture","★★★"],
["700","Thundering Herd (System)","★★★"],["701","Back-of-Envelope Estimation","★★☆"],
["702","Capacity Planning","★★★"],["703","Rate Limiting (System)","★★☆"],
["704","Token Bucket","★★★"],["705","Leaky Bucket","★★★"],["706","Sharding (System)","★★★"],
["707","Hot Shard","★★★"],["708","Read-Heavy vs Write-Heavy Design","★★★"],
["709","Denormalization for Scale","★★★"],["710","Fan-Out on Write vs Read","★★★"],
["711","Push vs Pull Architecture","★★★"],["712","Polling vs Webhooks","★★☆"],
["713","Idempotency Key","★★★"],["714","Distributed Locks","★★★"],
["715","Leader-Follower Pattern","★★★"],["716","Write-Ahead Logging (System)","★★★"],
["717","Data Partitioning Strategies","★★★"],["718","URL Shortener Design","★★☆"],
["719","Rate Limiter Design","★★★"],["720","News Feed Design","★★★"],
["721","Search Autocomplete Design","★★★"],["722","Notification System Design","★★★"],
["723","Chat System Design","★★★"],["724","Video Streaming Design","★★★"],
["725","Ride-Sharing System Design","★★★"]]);

// ── 19 Software Architecture ─────────────────────────────────
writeIndex("Software Architecture","Software Architecture Patterns","software-architecture",19,"726–765",
"Layered, hexagonal, clean, CQRS, event sourcing, DDD patterns, SOLID, and coupling/cohesion principles.",[
["726","Layered Architecture","★☆☆"],["727","Hexagonal Architecture","★★★"],
["728","Clean Architecture","★★★"],["729","Onion Architecture","★★★"],
["730","Vertical Slice Architecture","★★★"],["731","CQRS Pattern","★★★"],
["732","Event Sourcing Pattern","★★★"],["733","Ports and Adapters","★★★"],
["734","Repository Pattern","★★☆"],["735","Unit of Work Pattern","★★★"],
["736","Domain Model","★★★"],["737","Anemic Domain Model","★★★"],["738","Rich Domain Model","★★★"],
["739","Service Layer","★★☆"],["740","Transaction Script","★★☆"],["741","Active Record","★★☆"],
["742","Data Mapper","★★★"],["743","Aggregate Root","★★★"],["744","Domain Events","★★★"],
["745","Value Objects","★★★"],["746","Entities","★★☆"],["747","Anti-Corruption Layer","★★★"],
["748","Context Map","★★★"],["749","Shared Kernel","★★★"],["750","Open Host Service","★★★"],
["751","Published Language","★★★"],["752","Modular Monolith Patterns","★★★"],
["753","Plugin Architecture","★★★"],["754","Pipe and Filter","★★★"],["755","Blackboard Pattern","★★★"],
["756","SOLID Principles","★★☆"],["757","DRY","★☆☆"],["758","KISS","★☆☆"],
["759","YAGNI","★★☆"],["760","Law of Demeter","★★☆"],["761","Tell Don't Ask","★★☆"],
["762","Command-Query Separation (CQS)","★★★"],["763","Cohesion","★★☆"],["764","Coupling","★★☆"],
["765","Connascence","★★★"]]);

// ── 20 Design Patterns ───────────────────────────────────────
writeIndex("Design Patterns","Design Patterns","design-patterns",20,"766–820",
"GoF creational, structural, behavioral patterns, concurrency patterns, and common anti-patterns.",[
["766","Singleton","★☆☆"],["767","Factory Method","★★☆"],["768","Abstract Factory","★★☆"],
["769","Builder","★★☆"],["770","Prototype","★★☆"],["771","Object Pool","★★★"],["772","Adapter","★★☆"],
["773","Bridge","★★★"],["774","Composite","★★☆"],["775","Decorator","★★☆"],["776","Facade","★★☆"],
["777","Flyweight","★★★"],["778","Proxy","★★☆"],["779","Chain of Responsibility","★★☆"],
["780","Command","★★☆"],["781","Interpreter","★★★"],["782","Iterator","★★☆"],
["783","Mediator","★★★"],["784","Memento","★★★"],["785","Observer","★★☆"],["786","State","★★☆"],
["787","Strategy","★★☆"],["788","Template Method","★★☆"],["789","Visitor","★★★"],
["790","Null Object","★★☆"],["791","Double-Checked Locking","★★★"],["792","Producer-Consumer","★★☆"],
["793","Thread Pool Pattern","★★★"],["794","Scheduler Pattern","★★★"],
["795","Read-Write Lock Pattern","★★★"],["796","Active Object Pattern","★★★"],
["797","Event Bus Pattern","★★★"],["798","Service Locator","★★☆"],
["799","Dependency Injection Pattern","★★☆"],["800","Specification Pattern","★★★"],
["801","Decorator vs Proxy vs Adapter","★★★"],["802","Anti-Patterns Overview","★★☆"],
["803","God Object Anti-Pattern","★★☆"],["804","Spaghetti Code","★☆☆"],
["805","Golden Hammer Anti-Pattern","★★☆"],["806","Cargo Cult Programming","★★☆"],
["807","Premature Optimization","★★☆"],["808","Magic Numbers Anti-Pattern","★☆☆"],
["809","Lava Flow Anti-Pattern","★★☆"],["810","Copy-Paste Programming","★☆☆"],
["811","Boat Anchor Anti-Pattern","★★☆"],["812","CQRS Pattern","★★★"],
["813","Outbox Pattern","★★★"],["814","Saga Pattern","★★★"],["815","Strangler Fig","★★★"],
["816","Bulkhead Pattern","★★★"],["817","Circuit Breaker Pattern","★★★"],
["818","Sidecar Pattern","★★★"],["819","Ambassador Pattern","★★★"],["820","Retry Pattern","★★☆"]]);

// ── 21 Containers ────────────────────────────────────────────
writeIndex("Containers","Containers","containers",21,"821–855",
"Docker images, layers, multi-stage builds, container security, OCI standards, and container runtime internals.",[
["821","Container","★☆☆"],["822","Docker","★☆☆"],["823","Docker Image","★☆☆"],
["824","Docker Layer","★★☆"],["825","Dockerfile","★☆☆"],["826","Docker Build Context","★★☆"],
["827","Multi-Stage Build","★★☆"],["828","Docker Compose","★★☆"],["829","Container Registry","★★☆"],
["830","Linux Namespaces","★★★"],["831","Cgroups","★★★"],["832","Container Networking","★★★"],
["833","Volume Mounts","★★☆"],["834","Container Security","★★★"],["835","Distroless Images","★★★"],
["836","Image Scanning","★★★"],["837","OCI Standard","★★★"],["838","containerd","★★★"],
["839","Container Orchestration","★★☆"],["840","Docker vs VM","★☆☆"],
["841","Ephemeral Container","★★★"],["842","Init Container","★★★"],["843","Sidecar Container","★★★"],
["844","Container Resource Limits","★★☆"],["845","Container Health Check","★★☆"],
["846","Image Tag Strategy","★★☆"],["847","Docker BuildKit","★★★"],["848","Podman","★★★"],
["849","Buildah","★★★"],["850","Slim / Minimal Images","★★★"],
["851","Docker Networking Modes","★★★"],["852","Container Logging","★★☆"],
["853","Docker Secrets","★★★"],["854","Image Provenance / SBOM","★★★"],
["855","Container Runtime Interface (CRI)","★★★"]]);

// ── 22 Kubernetes ────────────────────────────────────────────
writeIndex("Kubernetes","Kubernetes","kubernetes",22,"856–915",
"K8s architecture, workloads, networking, storage, autoscaling, security, GitOps, and multi-cluster operations.",[
["856","Kubernetes Architecture","★☆☆"],["857","Pod","★☆☆"],["858","Node","★☆☆"],
["859","Cluster","★☆☆"],["860","Namespace (K8s)","★☆☆"],["861","Deployment","★★☆"],
["862","ReplicaSet","★★☆"],["863","StatefulSet","★★☆"],["864","DaemonSet","★★☆"],
["865","Job / CronJob","★★☆"],["866","Service (K8s)","★★☆"],
["867","ClusterIP / NodePort / LoadBalancer","★★☆"],["868","Ingress","★★☆"],
["869","Ingress Controller","★★★"],["870","ConfigMap","★★☆"],["871","Secret","★★☆"],
["872","HPA (Horizontal Pod Autoscaler)","★★☆"],["873","VPA (Vertical Pod Autoscaler)","★★★"],
["874","Cluster Autoscaler","★★★"],["875","KEDA","★★★"],["876","PersistentVolume / PVC","★★☆"],
["877","StorageClass","★★★"],["878","kube-proxy","★★★"],["879","CoreDNS","★★★"],
["880","etcd","★★★"],["881","API Server","★★★"],["882","Scheduler (K8s)","★★★"],
["883","Controller Manager","★★★"],["884","kubelet","★★★"],["885","kubeadm","★★☆"],
["886","kubectl","★★☆"],["887","Helm","★★☆"],["888","Helm Chart","★★☆"],
["889","Kustomize","★★★"],["890","Operators","★★★"],["891","CRD (Custom Resource Definition)","★★★"],
["892","Admission Controllers","★★★"],["893","RBAC (K8s)","★★★"],["894","Network Policy","★★★"],
["895","Pod Security Standards","★★★"],["896","Resource Requests / Limits","★★☆"],
["897","QoS Classes","★★★"],["898","Node Affinity / Anti-Affinity","★★★"],
["899","Taints and Tolerations","★★★"],["900","Pod Disruption Budget","★★★"],
["901","Rolling Update Strategy","★★☆"],["902","Readiness vs Liveness vs Startup Probe","★★☆"],
["903","Service Account","★★★"],["904","Kubernetes Secrets Management","★★★"],
["905","GitOps with Kubernetes","★★★"],["906","ArgoCD","★★★"],["907","FluxCD","★★★"],
["908","Kubernetes Networking (CNI)","★★★"],["909","Calico / Cilium","★★★"],
["910","Kubernetes Observability","★★★"],["911","K8s Multi-Cluster","★★★"],
["912","Service Mesh on K8s","★★★"],["913","K8s Cost Optimization","★★★"],
["914","K8s Security Hardening","★★★"],["915","K8s Upgrade Strategy","★★★"]]);

// ── 23 Cloud - AWS ───────────────────────────────────────────
writeIndex("Cloud - AWS","Cloud — AWS","cloud-aws",23,"916–955",
"AWS global infrastructure, core services (EC2, S3, RDS, Lambda, EKS), IaC, security, and cost optimization.",[
["916","AWS Global Infrastructure","★☆☆"],["917","Region / AZ / Edge Location","★☆☆"],
["918","IAM (Identity and Access Management)","★★☆"],["919","IAM Roles / Policies","★★☆"],
["920","VPC","★★☆"],["921","Subnets (Public / Private)","★★☆"],["922","Security Groups","★★☆"],
["923","NACLs","★★★"],["924","Internet Gateway / NAT Gateway","★★☆"],["925","VPC Peering","★★★"],
["926","Transit Gateway","★★★"],["927","Route 53","★★☆"],["928","EC2","★☆☆"],
["929","EC2 Instance Types","★★☆"],["930","Auto Scaling Groups","★★☆"],
["931","ELB / ALB / NLB","★★☆"],["932","S3","★☆☆"],["933","S3 Storage Classes","★★☆"],
["934","S3 Lifecycle Policies","★★★"],["935","EBS / EFS","★★☆"],["936","RDS","★★☆"],
["937","Aurora","★★★"],["938","DynamoDB","★★★"],["939","ElastiCache","★★☆"],
["940","SQS","★★☆"],["941","SNS","★★☆"],["942","Kinesis","★★★"],["943","Lambda","★★☆"],
["944","API Gateway (AWS)","★★☆"],["945","ECS / Fargate","★★☆"],["946","EKS","★★★"],
["947","CloudFormation","★★★"],["948","CDK","★★★"],["949","CloudWatch","★★☆"],
["950","X-Ray","★★★"],["951","AWS Cost Optimization","★★★"],
["952","AWS Security Best Practices","★★★"],["953","Well-Architected Framework","★★★"],
["954","Spot Instances / Reserved Instances","★★★"],["955","AWS Service Limits","★★★"]]);

// ── 24 Cloud - Azure ─────────────────────────────────────────
writeIndex("Cloud - Azure","Cloud — Azure","cloud-azure",24,"956–990",
"Azure global infrastructure, core services, DevOps, security, cost management, and hybrid connectivity.",[
["956","Azure Global Infrastructure","★☆☆"],["957","Azure Resource Manager (ARM)","★★☆"],
["958","Resource Groups","★☆☆"],["959","Azure Active Directory (Entra ID)","★★☆"],
["960","Azure RBAC","★★☆"],["961","Azure Virtual Network (VNet)","★★☆"],
["962","Subnets / NSG / UDR","★★☆"],["963","Azure Load Balancer","★★☆"],
["964","Application Gateway","★★★"],["965","Azure Front Door","★★★"],
["966","Azure Virtual Machines","★☆☆"],["967","VMSS (Virtual Machine Scale Sets)","★★☆"],
["968","Azure Blob Storage","★☆☆"],["969","Azure Files","★★☆"],["970","Azure SQL","★★☆"],
["971","Cosmos DB","★★★"],["972","Azure Cache for Redis","★★☆"],
["973","Azure Service Bus","★★☆"],["974","Azure Event Hub","★★★"],
["975","Azure Event Grid","★★★"],["976","Azure Functions","★★☆"],
["977","Azure API Management","★★★"],["978","AKS (Azure Kubernetes Service)","★★★"],
["979","Azure Container Instances","★★☆"],["980","Azure DevOps","★★☆"],
["981","Azure Pipelines","★★★"],["982","Bicep / ARM Templates","★★★"],
["983","Azure Monitor","★★☆"],["984","Application Insights","★★★"],
["985","Azure Key Vault","★★★"],["986","Azure Policy","★★★"],
["987","Azure Landing Zones","★★★"],["988","Azure Cost Management","★★★"],
["989","Azure Security Center","★★★"],["990","Azure Hybrid Connectivity","★★★"]]);

// ── 25 CI/CD ─────────────────────────────────────────────────
writeIndex("CI-CD","CI/CD","ci-cd",25,"991–1030",
"Continuous integration, delivery, deployment pipelines, GitOps, IaC, DORA metrics, and progressive delivery.",[
["991","Continuous Integration (CI)","★☆☆"],["992","Continuous Delivery (CD)","★☆☆"],
["993","Continuous Deployment","★★☆"],["994","Pipeline","★☆☆"],["995","Build Stage","★☆☆"],
["996","Test Stage","★☆☆"],["997","Artifact","★☆☆"],["998","Artifact Registry","★★☆"],
["999","Jenkins","★★☆"],["1000","GitHub Actions","★★☆"],["1001","GitLab CI","★★☆"],
["1002","CircleCI","★★☆"],["1003","Tekton","★★★"],["1004","ArgoCD","★★★"],
["1005","Pipeline as Code","★★☆"],["1006","Shift Left Testing","★★☆"],
["1007","SAST (Static Analysis)","★★☆"],["1008","DAST (Dynamic Analysis)","★★★"],
["1009","SCA (Software Composition Analysis)","★★★"],["1010","Dependency Scanning","★★☆"],
["1011","Container Scanning","★★★"],["1012","Secret Scanning","★★★"],
["1013","SBOM (Software Bill of Materials)","★★★"],["1014","Deployment Pipeline","★★☆"],
["1015","Environment Promotion","★★☆"],["1016","Infrastructure as Code (IaC)","★★☆"],
["1017","Terraform","★★★"],["1018","Pulumi","★★★"],["1019","Ansible","★★☆"],
["1020","GitOps","★★★"],["1021","Trunk-Based Development","★★☆"],
["1022","Feature Branch Workflow","★★☆"],["1023","Deployment Frequency","★★☆"],
["1024","Lead Time for Changes","★★☆"],["1025","Change Failure Rate","★★★"],
["1026","Mean Time to Recovery (MTTR)","★★★"],["1027","DORA Metrics","★★★"],
["1028","Progressive Delivery","★★★"],["1029","Canary Analysis","★★★"],
["1030","Rollback Strategy","★★★"]]);

// ── 26 Git ───────────────────────────────────────────────────
writeIndex("Git","Git & Branching Strategy","git",26,"1031–1065",
"Git fundamentals, branching strategies, merge vs rebase, monorepo vs polyrepo, and release management.",[
["1031","Git Basics (init, clone, add, commit)","★☆☆"],["1032","Git Staging Area","★☆☆"],
["1033","Git Remote","★☆☆"],["1034","Branch","★☆☆"],["1035","Merge","★☆☆"],
["1036","Rebase","★★☆"],["1037","Cherry-Pick","★★☆"],["1038","Stash","★★☆"],
["1039","Git Reset (soft, mixed, hard)","★★☆"],["1040","Git Revert","★★☆"],
["1041","Git Reflog","★★★"],["1042","Detached HEAD","★★★"],
["1043","Merge Conflict Resolution","★★☆"],["1044","Fast-Forward Merge","★★☆"],
["1045","Squash Merge","★★☆"],["1046","Merge vs Rebase Trade-offs","★★★"],
["1047","Git Tag","★★☆"],["1048","Semantic Versioning","★★☆"],["1049","Git Flow","★★☆"],
["1050","GitHub Flow","★★☆"],["1051","Trunk-Based Development","★★★"],
["1052","Feature Flags for Branching","★★★"],["1053","Release Branch","★★☆"],
["1054","Hotfix Branch","★★☆"],["1055","Monorepo vs Polyrepo","★★★"],
["1056","Git Hooks","★★★"],["1057","Pull Request / Code Review Workflow","★★☆"],
["1058","Protected Branches","★★☆"],["1059","CODEOWNERS","★★★"],
["1060","Signed Commits","★★★"],["1061","Git Blame","★★☆"],["1062","Git Bisect","★★★"],
["1063","Submodules","★★★"],["1064","Release Strategy","★★★"],["1065","Changelog Automation","★★★"]]);

// ── 27 Maven & Build Tools ───────────────────────────────────
writeIndex("Maven & Build Tools","Maven & Build Tools","maven-build",27,"1066–1095",
"Maven lifecycle, Gradle, dependency management, BOM, profiles, multi-module builds, and build optimization.",[
["1066","Maven Overview","★☆☆"],["1067","pom.xml","★☆☆"],
["1068","Maven Lifecycle (validate, compile, test, package, install, deploy)","★★☆"],
["1069","Maven Goals","★★☆"],["1070","Maven Phases","★★☆"],["1071","Maven Plugins","★★☆"],
["1072","Maven Dependencies","★☆☆"],
["1073","Dependency Scope (compile, test, provided, runtime)","★★☆"],
["1074","Transitive Dependencies","★★☆"],["1075","Dependency Exclusion","★★★"],
["1076","Dependency Convergence","★★★"],["1077","Maven BOM (Bill of Materials)","★★★"],
["1078","Maven Repository (local, central, remote)","★★☆"],["1079","Nexus / Artifactory","★★☆"],
["1080","SNAPSHOT vs RELEASE","★★☆"],["1081","Maven Profiles","★★★"],
["1082","Maven Multi-Module Project","★★★"],["1083","Maven Wrapper (mvnw)","★★☆"],
["1084","Gradle vs Maven","★★☆"],["1085","Gradle Build Script","★★★"],
["1086","Gradle Tasks","★★★"],["1087","Gradle Incremental Build","★★★"],
["1088","Gradle Build Cache","★★★"],["1089","Gradle Convention Plugins","★★★"],
["1090","Build Reproducibility","★★★"],["1091","Maven Release Plugin","★★★"],
["1092","Maven Enforcer Plugin","★★★"],["1093","OWASP Dependency Check","★★★"],
["1094","Source vs Binary Distribution","★★★"],["1095","Build Performance Optimization","★★★"]]);

// ── 28 Code Quality ──────────────────────────────────────────
writeIndex("Code Quality","Code Quality","code-quality",28,"1096–1130",
"Code standards, static analysis, code smells, refactoring, cyclomatic complexity, and architecture fitness.",[
["1096","Code Standards","★☆☆"],["1097","Coding Conventions","★☆☆"],["1098","Style Guide","★☆☆"],
["1099","Linting","★☆☆"],["1100","Static Analysis","★★☆"],["1101","SonarQube","★★☆"],
["1102","Checkstyle","★★☆"],["1103","PMD","★★☆"],["1104","SpotBugs","★★☆"],
["1105","Code Review","★★☆"],["1106","Code Review Best Practices","★★☆"],
["1107","Pair Programming","★★☆"],["1108","Code Coverage","★★☆"],["1109","Line Coverage","★★☆"],
["1110","Branch Coverage","★★★"],["1111","Mutation Testing","★★★"],["1112","Code Smell","★★☆"],
["1113","Long Method","★★☆"],["1114","God Class","★★☆"],["1115","Feature Envy","★★★"],
["1116","Data Clumps","★★★"],["1117","Primitive Obsession","★★★"],
["1118","Shotgun Surgery","★★★"],["1119","Divergent Change","★★★"],
["1120","Technical Debt","★★☆"],["1121","Refactoring","★★☆"],["1122","Extract Method","★★☆"],
["1123","Extract Class","★★☆"],["1124","Rename Refactoring","★☆☆"],["1125","Dead Code","★☆☆"],
["1126","Cyclomatic Complexity","★★★"],["1127","Cognitive Complexity","★★★"],
["1128","Dependency Analysis","★★★"],["1129","Architecture Fitness Functions","★★★"],
["1130","ArchUnit","★★★"]]);

// ── 29 Testing ───────────────────────────────────────────────
writeIndex("Testing","Testing","testing",29,"1131–1175",
"Unit, integration, contract, E2E, TDD, BDD, mocking, test pyramid, performance testing, and test tooling.",[
["1131","Unit Test","★☆☆"],["1132","Integration Test","★★☆"],["1133","Contract Test","★★★"],
["1134","E2E Test","★★☆"],["1135","Smoke Test","★☆☆"],["1136","Regression Test","★★☆"],
["1137","Performance Test","★★☆"],["1138","Load Test","★★☆"],["1139","Stress Test","★★★"],
["1140","Chaos Test","★★★"],["1141","Security Test (SAST/DAST)","★★★"],["1142","TDD","★★☆"],
["1143","BDD","★★☆"],["1144","Mocking","★★☆"],["1145","Stubbing","★★☆"],["1146","Faking","★★☆"],
["1147","Spying","★★★"],["1148","Test Pyramid","★★☆"],["1149","Test Diamond","★★★"],
["1150","Test Isolation","★★☆"],["1151","Test Fixtures","★★☆"],
["1152","Property-Based Testing","★★★"],["1153","Snapshot Testing","★★☆"],
["1154","Testcontainers","★★★"],["1155","WireMock","★★★"],["1156","JUnit 5","★★☆"],
["1157","Mockito","★★☆"],["1158","AssertJ","★★☆"],["1159","Pact (Contract Testing)","★★★"],
["1160","Test Data Management","★★★"],["1161","Test Environments","★★☆"],
["1162","Flaky Tests","★★★"],["1163","Test Parallelization","★★★"],
["1164","Approval Testing","★★★"],["1165","A/B Testing","★★★"],
["1166","Test-Driven Infrastructure","★★★"],["1167","Golden Path Testing","★★★"],
["1168","Test Coverage Targets","★★☆"],["1169","Penetration Testing","★★★"],
["1170","API Testing","★★☆"],["1171","Postman / REST Assured","★★☆"],
["1172","Selenium / Playwright","★★☆"],["1173","Gatling / k6 (Load Testing)","★★★"],
["1174","SonarQube Quality Gate","★★★"],["1175","Test Reporting","★★☆"]]);

// ── 30 Observability ─────────────────────────────────────────
writeIndex("Observability","Observability & SRE","observability",30,"1176–1210",
"Logging, metrics, distributed tracing, OpenTelemetry, Prometheus, Grafana, alerting, and SRE principles.",[
["1176","Observability","★★☆"],["1177","Monitoring vs Observability","★★☆"],["1178","Logging","★☆☆"],
["1179","Structured Logging","★★☆"],["1180","Log Levels","★☆☆"],["1181","Log Aggregation","★★☆"],
["1182","ELK Stack","★★☆"],["1183","Loki","★★★"],["1184","Metrics","★★☆"],
["1185","Counter","★★☆"],["1186","Gauge","★★☆"],["1187","Histogram","★★★"],
["1188","Summary","★★★"],["1189","Prometheus","★★☆"],["1190","Grafana","★★☆"],
["1191","Alerting","★★☆"],["1192","SLO-Based Alerting","★★★"],["1193","Distributed Tracing","★★★"],
["1194","Span","★★★"],["1195","Trace ID","★★★"],["1196","OpenTelemetry","★★★"],
["1197","Jaeger","★★★"],["1198","Zipkin","★★★"],["1199","Correlation ID","★★☆"],
["1200","Three Pillars of Observability","★★☆"],["1201","Cardinality (Metrics)","★★★"],
["1202","RED Method","★★★"],["1203","USE Method","★★★"],["1204","Golden Signals","★★★"],
["1205","Dashboards Best Practices","★★★"],["1206","On-Call Practices","★★★"],
["1207","Incident Management","★★★"],["1208","Post-Mortem / Blameless Culture","★★★"],
["1209","Chaos Engineering","★★★"],["1210","SRE Principles","★★★"]]);

// ── 31 HTML ──────────────────────────────────────────────────
writeIndex("HTML","HTML","html",31,"1211–1240",
"HTML structure, semantics, accessibility, Web Components, performance, and progressive web apps.",[
["1211","HTML Document Structure","★☆☆"],["1212","DOCTYPE","★☆☆"],
["1213","DOM (Document Object Model)","★★☆"],["1214","Semantic HTML","★★☆"],
["1215","Block vs Inline Elements","★☆☆"],["1216","HTML Attributes vs Properties","★★☆"],
["1217","Forms & Input Types","★☆☆"],["1218","Form Validation (Native)","★★☆"],
["1219","data- Attributes","★★☆"],["1220","Meta Tags","★☆☆"],["1221","Viewport Meta Tag","★★☆"],
["1222","Web Accessibility (ARIA)","★★☆"],["1223","srcset / Responsive Images","★★☆"],
["1224","lazy loading","★★☆"],["1225","Shadow DOM","★★★"],["1226","Web Components","★★★"],
["1227","Custom Elements","★★★"],["1228","HTML Parsing & Render Blocking","★★★"],
["1229","defer vs async","★★☆"],["1230","Critical Rendering Path","★★★"],
["1231","Reflow vs Repaint","★★★"],["1232","Content Security Policy (CSP)","★★★"],
["1233","Preload / Prefetch / Preconnect","★★★"],["1234","Canvas","★★☆"],["1235","SVG","★★☆"],
["1236","Template Element","★★★"],["1237","HTTP Cache Headers","★★★"],
["1238","Service Worker","★★★"],["1239","Progressive Web App (PWA)","★★★"],
["1240","Web Vitals (LCP, FID, CLS)","★★★"]]);

// ── 32 CSS ───────────────────────────────────────────────────
writeIndex("CSS","CSS","css",32,"1241–1290",
"CSS cascade, specificity, Flexbox, Grid, animations, preprocessors, CSS architecture, and modern CSS features.",[
["1241","CSS Specificity","★★☆"],["1242","CSS Cascade","★★☆"],["1243","CSS Inheritance","★★☆"],
["1244","Box Model","★☆☆"],["1245","Box Sizing","★★☆"],["1246","Display Property","★☆☆"],
["1247","Position","★★☆"],["1248","Flexbox","★★☆"],["1249","CSS Grid","★★☆"],
["1250","CSS Variables","★★☆"],["1251","Pseudo-classes","★★☆"],["1252","Pseudo-elements","★★☆"],
["1253","Media Queries","★★☆"],["1254","Responsive Design","★★☆"],
["1255","Mobile-First Design","★★☆"],["1256","CSS Units","★★☆"],
["1257","Stacking Context / z-index","★★★"],["1258","CSS Transitions","★★☆"],
["1259","CSS Animations","★★☆"],["1260","CSS Transform","★★☆"],["1261","BEM","★★☆"],
["1262","CSS Modules","★★☆"],["1263","CSS-in-JS","★★★"],["1264","Tailwind CSS","★★☆"],
["1265","SASS / SCSS","★★☆"],["1266","Container Queries","★★★"],["1267","CSS Layers (@layer)","★★★"],
["1268","CSS Nesting","★★★"],["1269",":has() Selector","★★★"],["1270","CSS Subgrid","★★★"],
["1271","CSS Clamp / min / max","★★★"],["1272","Scroll Snap","★★★"],
["1273","View Transitions API","★★★"],["1274","CSS Performance","★★★"],
["1275","Critical CSS","★★★"],["1276","Dark Mode","★★☆"],["1277","Reduced Motion","★★★"],
["1278","CSS Houdini","★★★"],["1279","Anchor Positioning","★★★"],
["1280","Logical Properties","★★★"],["1281","PostCSS","★★★"],
["1282","CSS Reset vs Normalize","★★☆"],["1283","Font Loading Strategy","★★★"],
["1284","will-change","★★★"],["1285","CSS Containment","★★★"],["1286","Print Styles","★★☆"],
["1287","CSS Custom Properties Advanced","★★★"],["1288","Accessibility in CSS","★★★"],
["1289","CSS Architecture Strategies","★★★"],["1290","Atomic CSS","★★★"]]);

// ── 33 JavaScript ────────────────────────────────────────────
writeIndex("JavaScript","JavaScript","javascript",33,"1291–1370",
"JS engine, event loop, closures, prototypes, async patterns, modules, memory, and V8 internals.",[
["1291","JavaScript Engine (V8)","★★☆"],["1292","Call Stack (JS)","★★☆"],
["1293","Event Loop","★★★"],["1294","Task Queue (Macrotask)","★★★"],
["1295","Microtask Queue","★★★"],["1296","var / let / const","★☆☆"],["1297","Hoisting","★★☆"],
["1298","Temporal Dead Zone","★★★"],["1299","Scope","★★☆"],["1300","Closure","★★★"],
["1301","Prototype Chain","★★★"],["1302","Prototypal Inheritance","★★★"],
["1303","this keyword","★★★"],["1304","Binding (call, apply, bind)","★★★"],
["1305","Arrow Functions","★★☆"],["1306","Execution Context","★★★"],
["1307","Closure Patterns","★★★"],["1308","Higher-Order Functions (JS)","★★☆"],
["1309","Pure Functions (JS)","★★☆"],["1310","Immutability (JS)","★★☆"],
["1311","Currying","★★★"],["1312","Memoization (JS)","★★★"],["1313","Promise","★★☆"],
["1314","async / await","★★☆"],["1315","Promise.all / race / allSettled","★★★"],
["1316","Generator Functions","★★★"],["1317","Iterator Protocol","★★★"],["1318","Symbol","★★★"],
["1319","WeakMap / WeakSet","★★★"],["1320","Map vs Object","★★☆"],
["1321","Destructuring","★★☆"],["1322","Spread / Rest","★★☆"],
["1323","Optional Chaining","★★☆"],["1324","Nullish Coalescing","★★☆"],
["1325","Type Coercion","★★★"],["1326","Proxy / Reflect","★★★"],
["1327","Property Descriptor","★★★"],["1328","Class (ES6+)","★★☆"],
["1329","Private Fields","★★★"],["1330","Modules (ESM)","★★☆"],["1331","CommonJS","★★☆"],
["1332","Dynamic Import","★★★"],["1333","Tree Shaking","★★★"],
["1334","Memory Leaks (JS)","★★★"],["1335","Garbage Collection (JS)","★★★"],
["1336","Debounce","★★☆"],["1337","Throttle","★★☆"],
["1338","requestAnimationFrame","★★★"],["1339","Web Workers","★★★"],
["1340","SharedArrayBuffer","★★★"],["1341","Service Worker (JS)","★★★"],
["1342","IndexedDB","★★★"],["1343","Fetch API","★★☆"],["1344","AbortController","★★★"],
["1345","Intl API","★★★"],["1346","BigInt","★★★"],["1347","Top-Level Await","★★★"],
["1348","Error Handling Patterns","★★☆"],["1349","Design Patterns in JS","★★★"],
["1350","JavaScript Runtime Environments","★★★"],["1351","V8 JIT Compilation","★★★"],
["1352","Hidden Classes (V8)","★★★"],["1353","Inline Caching (V8)","★★★"],
["1354","Deoptimization (V8)","★★★"],["1355","ArrayBuffer / TypedArray","★★★"],
["1356","Atomics (JS)","★★★"],["1357","Structured Clone","★★★"],
["1358","Object.freeze / seal","★★★"],["1359","Temporal API","★★★"],
["1360","Observability in JS","★★★"],["1361","JavaScript Security","★★★"],
["1362","Content Security Policy (JS)","★★★"],["1363","Trusted Types","★★★"],
["1364","IIFE","★★☆"],["1365","Module Pattern","★★★"],["1366","Revealing Module Pattern","★★★"],
["1367","Observer Pattern (JS)","★★★"],["1368","Reactive Programming (JS)","★★★"],
["1369","RxJS","★★★"],["1370","JavaScript Performance Optimization","★★★"]]);

// ── 34 TypeScript ────────────────────────────────────────────
writeIndex("TypeScript","TypeScript","typescript",34,"1371–1420",
"TypeScript type system, generics, utility types, mapped types, conditional types, and compiler internals.",[
["1371","TypeScript vs JavaScript","★☆☆"],["1372","Static Typing","★☆☆"],
["1373","Type Inference","★★☆"],["1374","Type Annotation","★☆☆"],["1375","Primitive Types","★☆☆"],
["1376","any / unknown / never","★★☆"],["1377","Union Types","★★☆"],
["1378","Intersection Types","★★☆"],["1379","Literal Types","★★☆"],["1380","Type Alias","★★☆"],
["1381","Interface","★★☆"],["1382","Type Alias vs Interface","★★★"],
["1383","Optional / Readonly","★★☆"],["1384","Generics (TS)","★★★"],
["1385","Generic Constraints","★★★"],["1386","Utility Types","★★★"],
["1387","Mapped Types","★★★"],["1388","Conditional Types","★★★"],["1389","infer Keyword","★★★"],
["1390","Template Literal Types","★★★"],["1391","Discriminated Union","★★★"],
["1392","Type Narrowing","★★★"],["1393","Type Guard","★★★"],["1394","satisfies Operator","★★★"],
["1395","Enum","★★☆"],["1396","Declaration Files (.d.ts)","★★★"],["1397","tsconfig.json","★★☆"],
["1398","strict Mode","★★☆"],["1399","Structural Typing","★★★"],
["1400","Excess Property Checking","★★★"],["1401","Index Signatures","★★★"],
["1402","Function Overloading (TS)","★★★"],["1403","Decorators (TS)","★★★"],
["1404","Abstract Classes","★★★"],["1405","keyof / typeof","★★★"],
["1406","ReturnType / Parameters","★★★"],["1407","Awaited Utility Type","★★★"],
["1408","Variance (TS)","★★★"],["1409","Declaration Merging","★★★"],
["1410","Module Augmentation","★★★"],["1411","TS Compiler Pipeline","★★★"],
["1412","Type-Level Programming","★★★"],["1413","Branded Types","★★★"],
["1414","Opaque Types","★★★"],["1415","Type Assertions","★★☆"],
["1416","Non-null Assertion","★★☆"],["1417","Project References","★★★"],
["1418","Monorepo TypeScript Setup","★★★"],["1419","TypeScript Performance","★★★"],
["1420","Type Compatibility Rules","★★★"]]);

// ── 35 React ─────────────────────────────────────────────────
writeIndex("React","React","react",35,"1421–1480",
"React hooks, fiber architecture, reconciliation, Server Components, SSR, state management, and performance.",[
["1421","JSX","★☆☆"],["1422","Component","★☆☆"],["1423","Props","★☆☆"],["1424","State","★☆☆"],
["1425","Controlled vs Uncontrolled","★★☆"],["1426","useState","★★☆"],["1427","useEffect","★★☆"],
["1428","useRef","★★☆"],["1429","useContext","★★☆"],["1430","useReducer","★★☆"],
["1431","useMemo","★★★"],["1432","useCallback","★★★"],["1433","useLayoutEffect","★★★"],
["1434","useTransition","★★★"],["1435","useDeferredValue","★★★"],["1436","Custom Hooks","★★★"],
["1437","Context API","★★☆"],["1438","React.memo","★★★"],["1439","Virtual DOM","★★☆"],
["1440","Reconciliation","★★★"],["1441","Diffing Algorithm","★★★"],
["1442","Fiber Architecture","★★★"],["1443","Concurrent Mode","★★★"],["1444","Suspense","★★★"],
["1445","React.lazy","★★☆"],["1446","Error Boundaries","★★★"],["1447","Portals","★★★"],
["1448","Keys in Lists","★★☆"],["1449","Lifting State Up","★★☆"],["1450","Prop Drilling","★★☆"],
["1451","Render Props","★★★"],["1452","Higher-Order Components","★★★"],
["1453","Compound Components","★★★"],["1454","Forwarding Refs","★★★"],
["1455","Server Components (RSC)","★★★"],["1456","Server Actions","★★★"],
["1457","Hydration","★★★"],["1458","SSR","★★★"],["1459","SSG","★★★"],["1460","ISR","★★★"],
["1461","Streaming SSR","★★★"],["1462","Next.js App Router","★★★"],["1463","React Query","★★★"],
["1464","Zustand","★★☆"],["1465","Redux Toolkit","★★★"],["1466","React Performance","★★★"],
["1467","React 19 Features","★★★"],["1468","use() Hook","★★★"],
["1469","Code Splitting (React)","★★★"],["1470","Storybook","★★☆"],
["1471","React Testing Library","★★☆"],["1472","React Router","★★☆"],
["1473","Client-Side Routing","★★☆"],["1474","Atomic State (Jotai/Recoil)","★★★"],
["1475","React Hook Form","★★☆"],["1476","Accessibility in React","★★★"],
["1477","React DevTools Profiler","★★★"],["1478","Micro-Frontend with React","★★★"],
["1479","Module Federation (React)","★★★"],["1480","Islands Architecture","★★★"]]);

// ── 36 Node.js ───────────────────────────────────────────────
writeIndex("Node.js","Node.js","nodejs",36,"1481–1510",
"Node.js event loop internals, streams, backpressure, worker threads, Express, Fastify, NestJS, and observability.",[
["1481","Node.js Architecture","★★☆"],["1482","libuv","★★★"],["1483","Node Event Loop","★★★"],
["1484","Phases of Node Event Loop","★★★"],
["1485","setImmediate vs setTimeout vs nextTick","★★★"],
["1486","Non-Blocking I/O (Node)","★★☆"],["1487","Streams","★★★"],
["1488","Backpressure (Node)","★★★"],["1489","Buffer","★★☆"],["1490","EventEmitter","★★☆"],
["1491","CommonJS vs ESM in Node","★★☆"],["1492","Cluster Module","★★★"],
["1493","Worker Threads","★★★"],["1494","Child Process","★★★"],["1495","Express.js","★★☆"],
["1496","Middleware (Express)","★★☆"],["1497","Fastify","★★★"],["1498","NestJS","★★★"],
["1499","GraphQL in Node","★★★"],["1500","tRPC","★★★"],["1501","Memory Leaks (Node)","★★★"],
["1502","Node.js Profiling","★★★"],["1503","AsyncLocalStorage","★★★"],
["1504","BullMQ (Job Queues)","★★★"],["1505","Graceful Shutdown (Node)","★★★"],
["1506","Deno","★★★"],["1507","Bun","★★★"],["1508","OpenTelemetry in Node","★★★"],
["1509","node:test","★★★"],["1510","Node.js Security","★★★"]]);

// ── 37 npm ───────────────────────────────────────────────────
writeIndex("npm","npm & Package Management","npm",37,"1511–1530",
"npm, pnpm, yarn, semantic versioning, lock files, monorepo tooling, and package security.",[
["1511","package.json","★☆☆"],["1512","Semantic Versioning","★★☆"],
["1513","dependencies vs devDependencies","★★☆"],["1514","Lock Files","★★☆"],
["1515","npm workspaces","★★★"],["1516","pnpm","★★★"],["1517","yarn","★★☆"],
["1518","Phantom Dependencies","★★★"],["1519","Dependency Hell","★★★"],
["1520","npm audit","★★☆"],["1521","Monorepo Tooling (Turborepo, Nx)","★★★"],
["1522","Changesets","★★★"],["1523","Private Registry","★★★"],
["1524","npm Lifecycle Scripts","★★★"],["1525","overrides / resolutions","★★★"],
["1526","Maven BOM equivalent in npm","★★★"],["1527","npm Provenance","★★★"],
["1528","Hoisting (npm)","★★★"],["1529","Scoped Packages","★★☆"],
["1530",".npmrc Configuration","★★★"]]);

// ── 38 Webpack & Build Tools ─────────────────────────────────
writeIndex("Webpack & Build Tools","Webpack & Build Tools","webpack-build",38,"1531–1580",
"Webpack, Vite, ESBuild, Rollup, code splitting, tree shaking, module federation, and build optimization.",[
["1531","Module Bundler","★☆☆"],["1532","Webpack Entry / Output","★★☆"],
["1533","Webpack Loaders","★★☆"],["1534","Webpack Plugins","★★☆"],
["1535","Code Splitting (Webpack)","★★★"],["1536","Tree Shaking (Webpack)","★★★"],
["1537","Source Maps","★★☆"],["1538","Hot Module Replacement","★★★"],
["1539","Module Federation","★★★"],["1540","Bundle Analysis","★★★"],["1541","Vite","★★☆"],
["1542","Vite vs Webpack","★★★"],["1543","ESBuild","★★★"],["1544","Rollup","★★★"],
["1545","Turbopack","★★★"],["1546","SWC","★★★"],["1547","Babel","★★☆"],
["1548","Polyfills","★★☆"],["1549","Browserslist","★★★"],
["1550","Content Hash (Cache Busting)","★★★"],["1551","Chunk / Chunk Splitting","★★★"],
["1552","Dynamic Chunks","★★★"],["1553","Vendor Chunk","★★★"],["1554","ESM vs CJS Output","★★★"],
["1555","Native ESM in Browser","★★★"],["1556","Import Maps","★★★"],
["1557","Microfrontends","★★★"],["1558","Monorepo Build Strategy","★★★"],
["1559","Incremental Builds","★★★"],["1560","TypeScript Build (tsc vs esbuild)","★★★"],
["1561","Build Time vs Runtime","★★★"],["1562","Production vs Development Build","★★☆"],
["1563","Asset Optimization","★★★"],["1564","Critical CSS Extraction","★★★"],
["1565","Deploy Previews","★★☆"],["1566","CI Build Pipeline (Frontend)","★★★"],
["1567","Storybook Build","★★★"],["1568","PostCSS Pipeline","★★★"],
["1569","Environment Variables (Build)","★★☆"],
["1570","Build Performance Optimization","★★★"],
["1571","Persistent Cache (Webpack 5)","★★★"],["1572","IIFE / UMD Format","★★★"],
["1573","Dependency Externals","★★★"],["1574","CSS Extraction","★★★"],
["1575","Minification","★★☆"],["1576","Compression (Brotli, gzip)","★★★"],
["1577","Lazy Loading (Build)","★★★"],["1578","Preloading Strategy","★★★"],
["1579","Web Performance Budget","★★★"],["1580","Lighthouse CI","★★★"]]);

// ── 39 AI Foundations ────────────────────────────────────────
writeIndex("AI Foundations","AI Foundations","ai-foundations",39,"1581–1620",
"ML basics, neural networks, transformer architecture, attention, embeddings, fine-tuning, and model evaluation.",[
["1581","Machine Learning Basics","★☆☆"],["1582","Supervised vs Unsupervised Learning","★☆☆"],
["1583","Neural Network","★★☆"],["1584","Deep Learning","★★☆"],
["1585","Transformer Architecture","★★★"],["1586","Attention Mechanism","★★★"],
["1587","Self-Attention","★★★"],["1588","Embedding","★★★"],["1589","Tokenization","★★☆"],
["1590","Token","★★☆"],["1591","Context Window","★★☆"],["1592","Temperature","★★☆"],
["1593","Top-p / Top-k Sampling","★★★"],["1594","Hallucination","★★☆"],
["1595","Grounding","★★★"],["1596","Model Parameters","★★★"],["1597","Model Weights","★★★"],
["1598","Inference","★★☆"],["1599","Training","★★★"],["1600","Fine-Tuning","★★★"],
["1601","RLHF (Reinforcement Learning from Human Feedback)","★★★"],
["1602","Pre-training","★★★"],["1603","Transfer Learning","★★★"],
["1604","Few-Shot Learning","★★★"],["1605","Zero-Shot Learning","★★★"],
["1606","In-Context Learning","★★★"],["1607","Overfitting / Underfitting","★★☆"],
["1608","Bias in AI","★★☆"],["1609","Latency vs Throughput (AI)","★★★"],
["1610","Model Quantization","★★★"],["1611","Model Pruning","★★★"],
["1612","Distillation","★★★"],["1613","Multimodal Models","★★★"],
["1614","Vision Language Models","★★★"],["1615","Foundation Models","★★★"],
["1616","Open Source vs Proprietary Models","★★☆"],
["1617","Model Evaluation Metrics","★★★"],["1618","Benchmark (AI)","★★★"],
["1619","AI Safety","★★★"],["1620","Responsible AI","★★★"]]);

// ── 40 LLMs ──────────────────────────────────────────────────
writeIndex("LLMs","LLMs & Prompt Engineering","llms",40,"1621–1660",
"LLM architectures, prompt engineering, function calling, fine-tuning (LoRA, QLoRA), guardrails, and LLM observability.",[
["1621","LLM (Large Language Model)","★☆☆"],["1622","GPT Architecture","★★★"],
["1623","BERT","★★★"],["1624","Prompt","★☆☆"],["1625","Prompt Engineering","★★☆"],
["1626","System Prompt","★★☆"],["1627","User Prompt","★☆☆"],["1628","Few-Shot Prompting","★★☆"],
["1629","Chain-of-Thought (CoT)","★★★"],["1630","Tree-of-Thought","★★★"],
["1631","ReAct Prompting","★★★"],["1632","Structured Output","★★★"],
["1633","Function Calling","★★★"],["1634","Tool Use","★★★"],["1635","Prompt Injection","★★★"],
["1636","Jailbreak","★★★"],["1637","Output Parsing","★★★"],["1638","Streaming Response","★★☆"],
["1639","Token Counting","★★☆"],["1640","Cost Optimization (LLM)","★★★"],
["1641","Caching (LLM)","★★★"],["1642","Prompt Versioning","★★★"],
["1643","Prompt Testing","★★★"],["1644","LLM Evaluation","★★★"],
["1645","Constitutional AI","★★★"],["1646","RLHF (LLM)","★★★"],
["1647","Instruction Tuning","★★★"],
["1648","PEFT (Parameter Efficient Fine-Tuning)","★★★"],
["1649","LoRA","★★★"],["1650","QLoRA","★★★"],["1651","Model Merging","★★★"],
["1652","Guardrails","★★★"],["1653","Toxicity Detection","★★★"],["1654","PII Detection","★★★"],
["1655","LLM Observability","★★★"],["1656","LLM Tracing","★★★"],
["1657","LLM Latency Optimization","★★★"],["1658","Batching (LLM)","★★★"],
["1659","Speculative Decoding","★★★"],["1660","KV Cache (LLM)","★★★"]]);

// ── 41 RAG & Agents ──────────────────────────────────────────
writeIndex("RAG & Agents","RAG & Agents","rag-agents",41,"1661–1700",
"RAG pipelines, vector search, agentic AI, multi-agent systems, MCP, LangChain, LlamaIndex, and LLMOps.",[
["1661","RAG (Retrieval-Augmented Generation)","★★☆"],["1662","Vector Search","★★★"],
["1663","Embedding Model","★★★"],["1664","Chunking Strategy","★★★"],
["1665","Semantic Search","★★★"],["1666","Hybrid Search","★★★"],["1667","Re-ranking","★★★"],
["1668","Retrieval Quality","★★★"],["1669","Context Stuffing","★★★"],
["1670","Knowledge Graph RAG","★★★"],["1671","GraphRAG","★★★"],["1672","Agentic RAG","★★★"],
["1673","AI Agent","★★★"],["1674","Agent Loop","★★★"],["1675","Tool Calling Agent","★★★"],
["1676","ReAct Agent","★★★"],["1677","Multi-Agent System","★★★"],
["1678","Agent Orchestration","★★★"],["1679","Planning Agent","★★★"],
["1680","Memory (Agent)","★★★"],["1681","Long-Term vs Short-Term Memory","★★★"],
["1682","Tool Registry","★★★"],["1683","MCP (Model Context Protocol)","★★★"],
["1684","LangChain","★★★"],["1685","LlamaIndex","★★★"],["1686","LangGraph","★★★"],
["1687","CrewAI","★★★"],["1688","AutoGen","★★★"],["1689","Agent Evaluation","★★★"],
["1690","Agent Safety","★★★"],["1691","LLMOps","★★★"],["1692","Model Registry","★★★"],
["1693","Experiment Tracking","★★★"],["1694","MLflow","★★★"],
["1695","Prompt Management","★★★"],["1696","Model Deployment (AI)","★★★"],
["1697","AI Gateway","★★★"],["1698","Java AI Stack (Spring AI, LangChain4j)","★★★"],
["1699","AI System Design","★★★"],["1700","AI Ethics & Governance","★★★"]]);

// ── 42 Platform Engineering ──────────────────────────────────
writeIndex("Platform Engineering","Platform & Modern SWE","platform-engineering",42,"1701–1730",
"Platform engineering, IDP, golden paths, FinOps, WebAssembly, edge computing, DORA metrics, and team topologies.",[
["1701","Platform Engineering","★★★"],["1702","Internal Developer Platform (IDP)","★★★"],
["1703","Golden Path","★★★"],["1704","Developer Experience (DX)","★★★"],
["1705","Self-Service Infrastructure","★★★"],["1706","Backstage","★★★"],
["1707","Service Catalog","★★★"],["1708","Software Templates","★★★"],["1709","FinOps","★★★"],
["1710","Cloud Cost Optimization","★★★"],["1711","Green Software Engineering","★★★"],
["1712","Carbon Aware Computing","★★★"],["1713","WebAssembly (WASM)","★★★"],
["1714","Edge Computing","★★★"],["1715","Serverless Edge Functions","★★★"],
["1716","Developer Productivity Metrics","★★★"],["1717","SPACE Framework","★★★"],
["1718","DORA Metrics","★★★"],["1719","Technical Excellence","★★★"],
["1720","Engineering Culture","★★★"],["1721","Feature Teams vs Component Teams","★★★"],
["1722","Conway's Law","★★★"],["1723","Team Topologies","★★★"],
["1724","Stream-Aligned Team","★★★"],["1725","Enabling Team","★★★"],
["1726","Platform Team","★★★"],["1727","Complicated Subsystem Team","★★★"],
["1728","Technical Strategy","★★★"],["1729","Architecture Decision Records (ADR)","★★★"],
["1730","RFC Process","★★★"]]);

// ── 43 Leadership ────────────────────────────────────────────
writeIndex("Leadership","Behavioral & Leadership","leadership",43,"1731–1770",
"Technical leadership, staff engineering, stakeholder communication, agile practices, and career development.",[
["1731","STAR Method","★☆☆"],["1732","Situational Leadership","★★☆"],
["1733","Technical Leadership","★★☆"],["1734","Engineering Manager vs Tech Lead","★★☆"],
["1735","Staff Engineer vs Principal Engineer","★★★"],["1736","Scope of Influence","★★★"],
["1737","Mentoring vs Coaching","★★☆"],["1738","Technical Roadmap","★★★"],
["1739","Stakeholder Communication","★★☆"],["1740","Technical Debt Management","★★★"],
["1741","Prioritization (MoSCoW, RICE)","★★☆"],["1742","Estimation Techniques","★★☆"],
["1743","Risk Management","★★★"],["1744","Incident Command","★★★"],
["1745","Blameless Culture","★★★"],["1746","Psychological Safety","★★☆"],
["1747","Feedback (Giving and Receiving)","★★☆"],
["1748","Cross-Functional Collaboration","★★☆"],["1749","Conflict Resolution","★★☆"],
["1750","Agile Principles","★★☆"],["1751","Scrum","★☆☆"],["1752","Kanban","★☆☆"],
["1753","Sprint Planning","★☆☆"],["1754","Retrospective","★☆☆"],["1755","OKRs","★★☆"],
["1756","Engineering Strategy","★★★"],["1757","Build vs Buy vs Outsource","★★★"],
["1758","Technical Interview Preparation","★★☆"],["1759","System Design Interview","★★★"],
["1760","Behavioral Interview Patterns","★★☆"],
["1761","Failure Stories (Learning from Mistakes)","★★☆"],
["1762","Project Leadership","★★★"],["1763","Driving Adoption","★★★"],
["1764","Influence Without Authority","★★★"],["1765","Negotiation in Engineering","★★★"],
["1766","Documentation Culture","★★☆"],["1767","Writing for Engineers","★★☆"],
["1768","Presentations for Technical Audiences","★★★"],["1769","Career Laddering","★★★"],
["1770","Personal Brand (Engineering)","★★★"]]);

console.log('\n✅ All 43 category index.md files created successfully.');

