"""
create_gap_stubs.py
Creates stub entries for missing keywords identified by deep gap analysis
across all 55 categories. Adds to index.md and creates stub .md files.

Run: pwsh -File tmp/run_gap_stubs.ps1
Or:  python3.14 tmp/create_gap_stubs.py
"""
import os, re
from pathlib import Path

BASE = Path(__file__).parent.parent / "dictionary"

# ── Category metadata ─────────────────────────────────────────────────────
CATS = {
    "CSF": ("CS Fundamentals - Paradigms",    "tier-1-foundations",              "CSF-cs-fundamentals",      "/cs-fundamentals/"),
    "DSA": ("Data Structures & Algorithms",    "tier-1-foundations",              "DSA-data-structures",      "/dsa/"),
    "LNX": ("Linux",                           "tier-1-foundations",              "LNX-linux",                "/linux/"),
    "OSY": ("Operating Systems",               "tier-1-foundations",              "OSY-operating-systems",    "/os/"),
    "NET": ("Networking",                      "tier-2-networking-security",      "NET-networking",           "/networking/"),
    "API": ("HTTP & APIs",                     "tier-2-networking-security",      "API-http-apis",            "/http-apis/"),
    "SEC": ("Security",                        "tier-2-networking-security",      "SEC-security",             "/security/"),
    "IAM": ("Identity & Access Management",    "tier-2-networking-security",      "IAM-iam-access",           "/iam/"),
    "CRY": ("Cryptography",                    "tier-2-networking-security",      "CRY-cryptography",         "/cryptography/"),
    "JVM": ("Java & JVM Internals",            "tier-3-java",                     "JVM-java-jvm-internals",   "/jvm/"),
    "JLG": ("Java Language",                   "tier-3-java",                     "JLG-java-language",        "/java-language/"),
    "JCC": ("Java Concurrency",                "tier-3-java",                     "JCC-java-concurrency",     "/java-concurrency/"),
    "SPR": ("Spring Core",                     "tier-3-java",                     "SPR-spring-core",          "/spring-core/"),
    "JPH": ("JPA & Hibernate",                 "tier-3-java",                     "JPH-jpa-hibernate",        "/jpa-hibernate/"),
    "DBF": ("Database Fundamentals",           "tier-4-data",                     "DBF-database-fundamentals","/database-fundamentals/"),
    "NDB": ("NoSQL & Distributed Databases",   "tier-4-data",                     "NDB-nosql-distributed",    "/nosql-distributed/"),
    "CCH": ("Caching",                         "tier-4-data",                     "CCH-caching",              "/caching/"),
    "DAT": ("Data Fundamentals",               "tier-4-data",                     "DAT-data-fundamentals",    "/data-fundamentals/"),
    "BIG": ("Big Data & Streaming",            "tier-4-data",                     "BIG-bigdata-streaming",    "/bigdata-streaming/"),
    "MSG": ("Messaging & Event Streaming",     "tier-4-data",                     "MSG-messaging-streaming",  "/messaging-streaming/"),
    "DST": ("Distributed Systems",             "tier-5-distributed-architecture", "DST-distributed-systems",  "/distributed-systems/"),
    "MSV": ("Microservices",                   "tier-5-distributed-architecture", "MSV-microservices",        "/microservices/"),
    "SYD": ("System Design",                   "tier-5-distributed-architecture", "SYD-system-design",        "/system-design/"),
    "SAP": ("Software Architecture Patterns",  "tier-5-distributed-architecture", "SAP-software-architecture","/software-architecture/"),
    "DPT": ("Design Patterns",                 "tier-5-distributed-architecture", "DPT-design-patterns",      "/design-patterns/"),
    "ASY": ("Async & Background Processing",   "tier-5-distributed-architecture", "ASY-async-background",     "/async-background/"),
    "CTR": ("Containers",                      "tier-6-infrastructure-devops",    "CTR-containers",           "/containers/"),
    "K8S": ("Kubernetes",                      "tier-6-infrastructure-devops",    "K8S-kubernetes",           "/kubernetes/"),
    "AWS": ("Cloud - AWS",                     "tier-6-infrastructure-devops",    "AWS-cloud-aws",            "/aws/"),
    "AZR": ("Cloud - Azure",                   "tier-6-infrastructure-devops",    "AZR-cloud-azure",          "/azure/"),
    "GCP": ("Cloud - GCP",                     "tier-6-infrastructure-devops",    "GCP-cloud-gcp",            "/gcp/"),
    "CCD": ("CI/CD",                           "tier-6-infrastructure-devops",    "CCD-cicd",                 "/cicd/"),
    "GIT": ("Git & Branching Strategy",        "tier-6-infrastructure-devops",    "GIT-git-branching",        "/git-branching/"),
    "MVN": ("Maven & Build Tools",             "tier-6-infrastructure-devops",    "MVN-maven-build",          "/maven-build/"),
    "CDQ": ("Code Quality",                    "tier-6-infrastructure-devops",    "CDQ-code-quality",         "/code-quality/"),
    "TST": ("Testing",                         "tier-6-infrastructure-devops",    "TST-testing",              "/testing/"),
    "OBS": ("Observability & SRE",             "tier-6-infrastructure-devops",    "OBS-observability-sre",    "/observability-sre/"),
    "IAC": ("Infrastructure as Code",          "tier-6-infrastructure-devops",    "IAC-infrastructure-code",  "/infrastructure-code/"),
    "PLT": ("Platform & Modern SWE",           "tier-6-infrastructure-devops",    "PLT-platform-swe",         "/platform-swe/"),
    "HTM": ("HTML",                            "tier-7-frontend",                 "HTM-html",                 "/html/"),
    "CSS": ("CSS",                             "tier-7-frontend",                 "CSS-css",                  "/css/"),
    "JSC": ("JavaScript",                      "tier-7-frontend",                 "JSC-javascript",           "/javascript/"),
    "TSC": ("TypeScript",                      "tier-7-frontend",                 "TSC-typescript",           "/typescript/"),
    "RCT": ("React",                           "tier-7-frontend",                 "RCT-react",                "/react/"),
    "ANG": ("Angular",                         "tier-7-frontend",                 "ANG-angular",              "/angular/"),
    "NDJ": ("Node.js",                         "tier-7-frontend",                 "NDJ-nodejs",               "/nodejs/"),
    "NPM": ("npm & Package Management",        "tier-7-frontend",                 "NPM-npm-packages",         "/npm-packages/"),
    "WBP": ("Webpack & Build Tools",           "tier-7-frontend",                 "WBP-webpack-build",        "/webpack-build/"),
    "AIF": ("AI Foundations",                  "tier-8-artificial-intelligence",  "AIF-ai-foundations",       "/ai-foundations/"),
    "LLM": ("LLMs & Prompt Engineering",       "tier-8-artificial-intelligence",  "LLM-llms-prompt-eng",      "/llms-prompt-eng/"),
    "RAG": ("RAG & Agents & LLMOps",           "tier-8-artificial-intelligence",  "RAG-rag-agents-llmops",    "/rag-agents-llmops/"),
    "AIP": ("AI Product Engineering",          "tier-8-artificial-intelligence",  "AIP-ai-product",           "/ai-product/"),
    "BHV": ("Behavioral & Leadership",         "tier-9-professional-domain",      "BHV-behavioral-leadership","/behavioral-leadership/"),
    "DGN": ("Document Generation",             "tier-9-professional-domain",      "DGN-document-generation",  "/document-generation/"),
    "FIN": ("Financial Services Domain",       "tier-9-professional-domain",      "FIN-financial-domain",     "/financial-domain/"),
}

# ── Gap keywords: (title, difficulty) ────────────────────────────────────
GAPS = {
# ── Tier 1 ────────────────────────────────────────────────────────────────
"CSF": [
    ("Logic Programming Paradigm (Prolog, Datalog)",          "★★☆"),
    ("Effect Systems and Side Effect Tracking",               "★★★"),
    ("Probabilistic Programming",                             "★★★"),
    ("Type-Driven Development",                               "★★★"),
    ("CS Fundamentals Interview Preparation Guide",           "★☆☆"),
],
"DSA": [
    ("Counting Sort and Bucket Sort",                         "★☆☆"),
    ("Floyd Cycle Detection (Tortoise and Hare)",             "★★☆"),
    ("AVL Tree",                                              "★★☆"),
    ("Red-Black Tree",                                        "★★★"),
    ("Suffix Array",                                          "★★★"),
    ("k-d Tree",                                              "★★★"),
    ("Interval Tree",                                         "★★★"),
    ("Sparse Table and Range Minimum Query",                  "★★★"),
    ("DSA Interview Pattern Catalogue",                       "★★☆"),
    ("Competitive Programming Strategy",                      "★★★"),
],
"LNX": [
    ("Linux Boot Process",                                    "★★☆"),
    ("GRUB Bootloader",                                       "★★☆"),
    ("inotify - File System Event Notification",              "★★★"),
    ("Linux IPC Mechanisms (Shared Memory, Semaphores, MQ)", "★★★"),
    ("LVM and Logical Volume Management",                     "★★☆"),
    ("Linux Network Interface Configuration",                 "★★☆"),
    ("Linux Interview Preparation Guide",                     "★☆☆"),
],
"OSY": [
    ("Interrupt Handling and IRQ",                            "★★☆"),
    ("Boot Process (BIOS, UEFI, Bootloader)",                 "★★☆"),
    ("Copy-on-Write (CoW)",                                   "★★★"),
    ("Memory Overcommit and OOM Strategy",                    "★★★"),
    ("Inter-Process Communication (IPC) Mechanisms",          "★★☆"),
    ("DMA (Direct Memory Access)",                            "★★★"),
    ("Microkernel vs Monolithic Kernel",                      "★★☆"),
    ("OS Concepts Interview Preparation Guide",               "★☆☆"),
],
# ── Tier 2 ────────────────────────────────────────────────────────────────
"NET": [
    ("Network Topology Design Patterns",                      "★★★"),
    ("SD-WAN (Software-Defined WAN)",                         "★★★"),
    ("NTP and Time Synchronization",                          "★★☆"),
    ("IPv6 Addressing and Migration",                         "★★☆"),
    ("Networking Interview Preparation Guide",                "★☆☆"),
],
"API": [
    ("API Design Review Checklist",                           "★★☆"),
    ("REST vs GraphQL vs gRPC Decision Framework",            "★★★"),
    ("OWASP API Security Top 10 Deep Dive",                   "★★★"),
    ("API Load Testing and Performance",                      "★★★"),
    ("HTTP and API Interview Preparation Guide",              "★☆☆"),
],
"SEC": [
    ("Security Interview Preparation Guide",                  "★☆☆"),
    ("OWASP Mobile Security Top 10",                          "★★★"),
    ("Security Architecture Decision Framework",              "★★★"),
],
"IAM": [
    ("SAML 2.0",                                              "★★★"),
    ("Single Sign-On (SSO)",                                  "★★☆"),
    ("Multi-Factor Authentication (MFA)",                     "★★☆"),
    ("Passwordless Authentication",                           "★★☆"),
    ("Passkeys and FIDO2",                                    "★★★"),
    ("OpenID Connect (OIDC)",                                 "★★★"),
    ("LDAP and Active Directory",                             "★★★"),
    ("Role-Based Access Control (RBAC)",                      "★★☆"),
    ("Attribute-Based Access Control (ABAC)",                 "★★★"),
    ("OAuth2 Scopes and Consent",                             "★★☆"),
    ("Service Account Security Patterns",                     "★★★"),
    ("Token Refresh and Revocation",                          "★★★"),
    ("Zero Trust Identity (BeyondCorp Model)",                "★★★"),
    ("Identity Federation",                                   "★★★"),
    ("Privileged Access Management (PAM)",                    "★★★"),
    ("IAM Architecture at Scale",                             "★★★"),
    ("Cloud IAM (AWS IAM, Azure AD, GCP IAM)",                "★★★"),
    ("SCIM Protocol",                                         "★★★"),
    ("Directory Services (Okta, Keycloak, Azure AD)",         "★★★"),
    ("Entitlement Management",                                "★★★"),
    ("Delegation and Impersonation Patterns",                 "★★★"),
    ("IAM Interview Preparation Guide",                       "★☆☆"),
],
"CRY": [
    ("AES (Advanced Encryption Standard)",                    "★★☆"),
    ("RSA Algorithm",                                         "★★☆"),
    ("Diffie-Hellman Key Exchange",                           "★★☆"),
    ("Digital Signatures (RSA, ECDSA)",                       "★★☆"),
    ("Message Authentication Code (HMAC)",                    "★★☆"),
    ("Hash Functions (SHA-256, SHA-3, MD5)",                  "★☆☆"),
    ("Password Hashing (bcrypt, Argon2, scrypt)",             "★★☆"),
    ("Salting and Key Stretching",                            "★★☆"),
    ("Certificate Chain Validation",                          "★★☆"),
    ("TLS Handshake Deep Dive",                               "★★★"),
    ("Perfect Forward Secrecy",                               "★★★"),
    ("Key Derivation Functions (PBKDF2, HKDF)",               "★★★"),
    ("Cipher Modes (ECB, CBC, GCM, CTR)",                     "★★★"),
    ("Padding Attacks (PKCS7, Oracle Padding Attack)",        "★★★"),
    ("Cryptographically Secure Random Number Generation",     "★★☆"),
    ("Key Management and Hardware Security Modules",          "★★★"),
    ("Certificate Revocation (CRL, OCSP Stapling)",           "★★★"),
    ("X.509 Certificate Structure",                           "★★☆"),
    ("Elliptic Curve Diffie-Hellman (ECDH)",                  "★★★"),
    ("Cryptography Interview Preparation Guide",              "★☆☆"),
],
# ── Tier 3 ────────────────────────────────────────────────────────────────
"JVM": [
    ("GraalVM Truffle Framework",                             "★★★"),
    ("JVM Bytecode Instrumentation",                          "★★★"),
    ("JVM Startup Optimization (AppCDS, AOT)",                "★★★"),
    ("JVM Flags Reference and Tuning Guide",                  "★★★"),
    ("JVM Interview Preparation Guide",                       "★☆☆"),
],
"JLG": [
    ("Java Interview Preparation - Core Language",            "★☆☆"),
    ("Sealed Interfaces (Java 17+)",                          "★★☆"),
    ("Java 21 Virtual Threads Practical Patterns",            "★★★"),
    ("Foreign Memory API (Project Panama)",                   "★★★"),
],
"JCC": [
    ("Java Concurrency Interview Preparation Guide",          "★☆☆"),
    ("Async Request Handling with Virtual Threads",           "★★★"),
    ("JMH Benchmarking for Concurrent Code",                  "★★★"),
    ("Project Loom Migration Strategy",                       "★★★"),
],
"SPR": [
    ("Spring Interview Preparation Guide",                    "★☆☆"),
    ("Spring Modulith (Spring 6.1+)",                         "★★★"),
    ("Spring AOT and GraalVM Native Image",                   "★★★"),
],
"JPH": [
    ("JPA Interview Preparation Guide",                       "★☆☆"),
    ("Spring Data JPA vs JOOQ vs MyBatis Decision",           "★★★"),
    ("Hibernate 6 and Jakarta Persistence 3 Migration",       "★★★"),
    ("JPA Auditing (@CreatedDate, @LastModifiedDate)",        "★★☆"),
    ("JPA with Multiple Databases (Routing DataSource)",      "★★★"),
],
# ── Tier 4 ────────────────────────────────────────────────────────────────
"DBF": [
    ("Database Interview Preparation Guide",                  "★☆☆"),
    ("Time-Series Database Concepts",                         "★★★"),
    ("Database Migration (Flyway, Liquibase)",                "★★☆"),
    ("Database Sharding Strategy",                            "★★★"),
    ("Column Store vs Row Store",                             "★★★"),
],
"NDB": [
    ("NoSQL Interview Preparation Guide",                     "★☆☆"),
    ("Document Database Design Patterns",                     "★★★"),
    ("Graph Database (Neo4j)",                                "★★★"),
    ("Vector Database",                                       "★★★"),
    ("NewSQL (CockroachDB, TiDB)",                            "★★★"),
],
"CCH": [
    ("Caching Interview Preparation Guide",                   "★☆☆"),
    ("Cache Penetration, Breakdown, and Avalanche",           "★★★"),
    ("Distributed Cache vs Local Cache Trade-offs",           "★★★"),
    ("Read-Through, Write-Through, Write-Behind Strategies",  "★★★"),
    ("Cache Sizing and Memory Management",                    "★★★"),
],
"DAT": [
    ("Data Engineering Interview Preparation Guide",          "★☆☆"),
    ("Data Lineage and Provenance",                           "★★★"),
    ("Data Mesh Architecture",                                "★★★"),
    ("Data Catalog and Data Governance",                      "★★★"),
    ("Change Data Capture (CDC)",                             "★★★"),
],
"BIG": [
    ("Big Data Interview Preparation Guide",                  "★☆☆"),
    ("Lambda Architecture",                                   "★★★"),
    ("Kappa Architecture",                                    "★★★"),
    ("Data Lakehouse Architecture",                           "★★★"),
    ("Stream Processing Exactly-Once Semantics",              "★★★"),
    ("Data Quality in Streaming Pipelines",                   "★★★"),
    ("Real-Time Analytics Architecture",                      "★★★"),
],
"MSG": [
    ("Messaging Interview Preparation Guide",                 "★☆☆"),
    ("Message Deduplication Patterns",                        "★★★"),
    ("Outbox Pattern",                                        "★★★"),
    ("Message Schema Evolution",                              "★★★"),
    ("Fan-out vs Fan-in Messaging Patterns",                  "★★★"),
    ("Event Sourcing with Kafka",                             "★★★"),
],
# ── Tier 5 ────────────────────────────────────────────────────────────────
"DST": [
    ("Distributed Systems Interview Preparation Guide",       "★☆☆"),
    ("Byzantine Fault Tolerance",                             "★★★"),
    ("Distributed Transactions (2PC and Saga Pattern)",       "★★★"),
    ("Conflict-Free Replicated Data Types (CRDTs)",           "★★★"),
    ("Distributed Systems Reading List (Classics)",           "★★★"),
],
"MSV": [
    ("Microservices Interview Preparation Guide",             "★☆☆"),
    ("Service Mesh Architecture (Istio, Linkerd)",            "★★★"),
    ("Microservices Database Strategy",                       "★★★"),
    ("Microservices Organizational Design (Team Topologies)", "★★★"),
    ("Microservices Migration (Strangler Fig Pattern)",       "★★★"),
],
"SYD": [
    ("System Design Interview Preparation Guide",             "★☆☆"),
    ("System Design Interview Framework",                     "★★☆"),
    ("Back-of-Envelope Estimation",                           "★★☆"),
    ("URL Shortener System Design",                           "★★☆"),
    ("Design a Chat System",                                  "★★★"),
],
"SAP": [
    ("Software Architecture Interview Preparation Guide",     "★☆☆"),
    ("Architecture Decision Records (ADR)",                   "★★☆"),
    ("Fitness Functions (Evolutionary Architecture)",         "★★★"),
    ("Domain Model Design Trade-offs",                        "★★★"),
],
"DPT": [
    ("Design Patterns Interview Preparation Guide",           "★☆☆"),
    ("Anti-Patterns Catalogue",                               "★★☆"),
    ("Decorator Pattern vs Inheritance",                      "★★☆"),
    ("Composite Pattern",                                     "★★☆"),
    ("Visitor Pattern",                                       "★★★"),
],
"ASY": [
    ("Async Interview Preparation Guide",                     "★☆☆"),
    ("Job Queue Architecture Patterns",                       "★★★"),
    ("Dead Letter Queue (DLQ)",                               "★★★"),
    ("Idempotency in Async Systems",                          "★★★"),
    ("Priority Queue and Task Scheduling",                    "★★★"),
    ("Async Error Handling and Retry Patterns",               "★★★"),
    ("Workflow Orchestration (Temporal, Conductor)",          "★★★"),
    ("Backpressure and Flow Control in Async",                "★★★"),
],
# ── Tier 6 ────────────────────────────────────────────────────────────────
"CTR": [
    ("Container Interview Preparation Guide",                 "★☆☆"),
    ("Multi-Stage Docker Builds",                             "★★☆"),
    ("Container Image Signing and Verification",              "★★★"),
    ("Container Runtime Security (gVisor, Kata Containers)",  "★★★"),
    ("Container Networking Deep Dive",                        "★★★"),
],
"K8S": [
    ("Kubernetes Interview Preparation Guide",                "★☆☆"),
    ("Kubernetes Operator Pattern",                           "★★★"),
    ("GitOps with Kubernetes (Flux, ArgoCD)",                 "★★★"),
    ("Kubernetes Multi-Cluster Management",                   "★★★"),
    ("Kubernetes Cost Optimization",                          "★★★"),
    ("Kubernetes Migration Strategy",                         "★★★"),
],
"AWS": [
    ("AWS Interview Preparation Guide",                       "★☆☆"),
    ("AWS Well-Architected Framework",                        "★★★"),
    ("AWS Cost Optimization Strategies",                      "★★★"),
    ("AWS Landing Zone and Account Strategy",                 "★★★"),
    ("AWS Security Architecture Patterns",                    "★★★"),
],
"AZR": [
    ("Azure Interview Preparation Guide",                     "★☆☆"),
    ("Azure DevOps Pipelines",                                "★★☆"),
    ("Azure API Management",                                  "★★★"),
    ("Azure Kubernetes Service (AKS)",                        "★★★"),
    ("Azure Cost Management",                                 "★★★"),
    ("Azure Architecture Best Practices",                     "★★★"),
],
"GCP": [
    ("Cloud Bigtable",                                        "★★★"),
    ("Cloud Memorystore (Redis on GCP)",                      "★★★"),
    ("Cloud SQL",                                             "★★☆"),
    ("Secret Manager",                                        "★★☆"),
    ("Cloud DNS",                                             "★★☆"),
    ("Cloud Interconnect",                                    "★★★"),
    ("Cloud NAT",                                             "★★★"),
    ("Cloud Endpoints",                                       "★★★"),
    ("GCP IAM (Cloud Identity and Access Management)",        "★★★"),
    ("Organization Policy Service",                           "★★★"),
    ("Cloud Operations Suite (Monitoring, Logging)",          "★★☆"),
    ("Cloud Trace and Cloud Profiler",                        "★★★"),
    ("Anthos and Multi-Cloud Strategy",                       "★★★"),
    ("GCP Cost Management and Budgets",                       "★★★"),
    ("GCP Migration Strategy",                                "★★★"),
    ("GCP Architecture Best Practices",                       "★★★"),
    ("Cloud Identity",                                        "★★★"),
    ("GCP vs AWS vs Azure Decision Framework",                "★★★"),
    ("GCP Data Analytics Architecture",                       "★★★"),
    ("GCP Interview Preparation Guide",                       "★☆☆"),
],
"CCD": [
    ("CI/CD Interview Preparation Guide",                     "★☆☆"),
    ("Pipeline Security (Software Supply Chain Security)",    "★★★"),
    ("Feature Flags and Canary Deployment Strategy",          "★★★"),
    ("CI/CD Metrics and DORA Framework",                      "★★★"),
],
"GIT": [
    ("Git Interview Preparation Guide",                       "★☆☆"),
    ("Git Internals (Objects, Refs, Packfiles)",              "★★★"),
    ("Monorepo Strategy (Nx, Turborepo, Bazel)",              "★★★"),
    ("Git LFS (Large File Storage)",                          "★★☆"),
    ("Git Hooks for Automation",                              "★★☆"),
    ("GitHub Actions Deep Dive",                              "★★★"),
],
"MVN": [
    ("Maven Interview Preparation Guide",                     "★☆☆"),
    ("Gradle Build Scripts",                                  "★★☆"),
    ("Dependency Version Management (BOM)",                   "★★★"),
    ("Maven Plugin Development",                              "★★★"),
    ("Multi-Module Maven Project Strategy",                   "★★★"),
],
"CDQ": [
    ("Code Quality Interview Preparation Guide",              "★☆☆"),
    ("Technical Debt Quantification",                         "★★★"),
    ("Code Review Best Practices",                            "★★☆"),
    ("Code Coverage Goals and Anti-Patterns",                 "★★★"),
    ("Continuous Code Quality Strategy",                      "★★★"),
],
"TST": [
    ("Testing Interview Preparation Guide",                   "★☆☆"),
    ("Fuzz Testing",                                          "★★★"),
    ("Property-Based Testing",                                "★★★"),
    ("Test Data Management Strategy",                         "★★★"),
    ("Testing Pyramid Trade-offs",                            "★★★"),
],
"OBS": [
    ("Observability Interview Preparation Guide",             "★☆☆"),
    ("OpenTelemetry",                                         "★★★"),
    ("Service Level Objectives (SLOs) Deep Dive",            "★★★"),
    ("Error Budgets",                                         "★★★"),
    ("Chaos Engineering",                                     "★★★"),
    ("Production On-Call Runbook Design",                     "★★★"),
],
"IAC": [
    ("Infrastructure as Code Interview Preparation Guide",    "★☆☆"),
    ("Terraform State Management",                            "★★★"),
    ("Terraform Modules and Reuse",                           "★★★"),
    ("Pulumi (IaC with Real Languages)",                      "★★★"),
    ("AWS CDK",                                               "★★★"),
    ("IaC Testing Strategies",                                "★★★"),
],
"PLT": [
    ("Platform Engineering Interview Preparation Guide",      "★☆☆"),
    ("Golden Paths and Developer Portals",                    "★★★"),
    ("Backstage Developer Portal",                            "★★★"),
    ("Platform Engineering Metrics",                          "★★★"),
    ("Platform Team Topologies",                              "★★★"),
],
# ── Tier 7 ────────────────────────────────────────────────────────────────
"HTM": [
    ("HTML Interview Preparation Guide",                      "★☆☆"),
    ("Web Components",                                        "★★★"),
    ("Progressive Enhancement",                               "★★☆"),
    ("HTML Email Development",                                "★★★"),
    ("Microdata and JSON-LD for SEO",                         "★★★"),
],
"CSS": [
    ("CSS Interview Preparation Guide",                       "★☆☆"),
    ("CSS Custom Properties (Variables)",                     "★★☆"),
    ("CSS Scroll-Driven Animations",                          "★★★"),
    ("CSS Cascade Layers",                                    "★★★"),
    ("CSS Houdini (Paint API)",                               "★★★"),
],
"JSC": [
    ("JavaScript Interview Preparation Guide",                "★☆☆"),
    ("Generators and Iterators",                              "★★★"),
    ("Proxies and Reflect API",                               "★★★"),
    ("Symbol Type",                                           "★★☆"),
    ("WeakMap and WeakSet",                                   "★★☆"),
    ("ArrayBuffer and TypedArray",                            "★★★"),
    ("JavaScript Module System (ESM, CJS, AMD)",              "★★☆"),
    ("Web Workers",                                           "★★★"),
],
"TSC": [
    ("TypeScript Interview Preparation Guide",                "★☆☆"),
    ("Template Literal Types",                                "★★★"),
    ("Mapped Types",                                          "★★★"),
    ("TypeScript Compiler API",                               "★★★"),
    ("TypeScript Project References",                         "★★★"),
],
"RCT": [
    ("React Interview Preparation Guide",                     "★☆☆"),
    ("React 19 Features (Actions, use() Hook)",               "★★★"),
    ("Micro-Frontends with React",                            "★★★"),
    ("React Testing with React Testing Library",              "★★★"),
    ("React Performance Profiling",                           "★★★"),
],
"ANG": [
    ("Angular Interview Preparation Guide",                   "★☆☆"),
    ("Angular Signals (v17+)",                                "★★★"),
    ("Angular Module Federation (Micro-Frontends)",           "★★★"),
    ("Angular Performance Optimization",                      "★★★"),
    ("Angular 17+ Control Flow Syntax (@if, @for)",           "★★☆"),
],
"NDJ": [
    ("Node.js Interview Preparation Guide",                   "★☆☆"),
    ("Fastify Framework",                                     "★★☆"),
    ("Node.js Streams Deep Dive",                             "★★★"),
    ("Node.js Child Processes and Clustering",                "★★★"),
    ("Node.js Security Best Practices",                       "★★★"),
    ("Node.js Performance Profiling",                         "★★★"),
],
"NPM": [
    ("npm Interview Preparation Guide",                       "★☆☆"),
    ("pnpm (Fast, Disk-Efficient Package Manager)",           "★★☆"),
    ("Yarn Berry and Plug'n'Play",                            "★★★"),
    ("npm Security Auditing",                                 "★★★"),
    ("Package Publishing Strategy",                           "★★★"),
    ("Monorepo Package Management (Nx, Turborepo)",           "★★★"),
],
"WBP": [
    ("Webpack Interview Preparation Guide",                   "★☆☆"),
    ("Vite (Next-Generation Frontend Build Tool)",            "★★☆"),
    ("Rollup for Library Bundling",                           "★★★"),
    ("esbuild",                                               "★★★"),
    ("Module Federation (Webpack 5)",                         "★★★"),
    ("Build Tool Selection Framework",                        "★★★"),
],
# ── Tier 8 ────────────────────────────────────────────────────────────────
"AIF": [
    ("AI Foundations Interview Preparation Guide",            "★☆☆"),
    ("Neural Architecture Search (NAS)",                      "★★★"),
    ("Federated Learning",                                    "★★★"),
    ("AI Ethics and Responsible AI",                          "★★★"),
    ("AI System Design Patterns",                             "★★★"),
],
"LLM": [
    ("LLM Interview Preparation Guide",                       "★☆☆"),
    ("Structured Output Generation",                          "★★★"),
    ("LLM Evaluation Frameworks",                             "★★★"),
    ("LLM Fine-Tuning (LoRA, QLoRA, PEFT)",                  "★★★"),
    ("LLM Observability (LangSmith, Weights and Biases)",    "★★★"),
    ("Prompt Injection Defense Strategies",                   "★★★"),
],
"RAG": [
    ("RAG Interview Preparation Guide",                       "★☆☆"),
    ("RAG Evaluation (RAGAS, TruLens)",                       "★★★"),
    ("Knowledge Graph RAG",                                   "★★★"),
    ("Corrective RAG (CRAG)",                                 "★★★"),
    ("Multi-Agent Orchestration Frameworks",                  "★★★"),
    ("LLMOps Production Monitoring",                          "★★★"),
],
"AIP": [
    ("AI Product Engineering Interview Preparation Guide",    "★☆☆"),
    ("AI Safety and Alignment (Product Perspective)",         "★★★"),
    ("AI Feature Launch Checklist",                           "★★☆"),
    ("Human-in-the-Loop Design",                              "★★★"),
    ("AI Product Metrics",                                    "★★★"),
    ("AI Product Risk Assessment",                            "★★★"),
],
# ── Tier 9 ────────────────────────────────────────────────────────────────
"BHV": [
    ("Behavioral Interview Mastery Guide",                    "★☆☆"),
    ("Technical Leadership Communication",                    "★★★"),
    ("Engineering Manager vs Tech Lead Career Decision",      "★★★"),
    ("Writing Engineering Design Documents",                  "★★☆"),
],
"DGN": [
    ("Document Generation Interview Preparation Guide",       "★☆☆"),
    ("PDF/A Compliance and Document Archival",                "★★★"),
    ("Digital Signatures in Documents",                       "★★★"),
    ("Document Template Engines Comparison",                  "★★☆"),
    ("Document Generation at Scale",                          "★★★"),
],
"FIN": [
    ("Financial Domain Interview Preparation Guide",          "★☆☆"),
    ("High-Frequency Trading Systems",                        "★★★"),
    ("Market Data Processing",                                "★★★"),
    ("Financial Data Compliance (GDPR, MiFID II, SOX)",      "★★★"),
    ("Risk Management Systems Architecture",                  "★★★"),
],
}

# ── Helpers ───────────────────────────────────────────────────────────────
def title_to_slug(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:70]  # truncate for safety

def title_to_filename(title):
    """Strip characters invalid in Windows file names."""
    safe = title.replace("/", "-").replace("\\", "-").replace(":", " -")
    safe = re.sub(r'[<>"|?*]', "", safe)
    safe = re.sub(r"\s+", " ", safe).strip()
    return safe[:120]  # keep filename reasonable

def get_current_max_id(cat_dir, code):
    max_n = 0
    for f in cat_dir.glob("*.md"):
        if f.name == "index.md":
            continue
        m = re.match(rf"^{code}-(\d+)", f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n

def get_index_title(index_path):
    """Read title: from index.md frontmatter."""
    if not index_path.exists():
        return None
    text = index_path.read_text(encoding="utf-8")
    m = re.search(r'^title:\s*"?([^"\n]+)"?', text, re.MULTILINE)
    return m.group(1).strip() if m else None

def create_stub(cat_dir, code, nnn, title, diff, cat_name, tier, folder, permalink_base, parent_title):
    slug = title_to_slug(title)
    fid = f"{code}-{str(nnn).zfill(3)}"
    safe_title = title_to_filename(title)
    filename = f"{fid} - {safe_title}.md"
    filepath = cat_dir / filename

    if filepath.exists():
        print(f"    [SKIP] already exists: {filename}")
        return False

    # Safe YAML title
    yaml_title = f'"{title}"' if ":" in title else title

    content = f"""---
id: {fid}
title: {yaml_title}
category: {cat_name}
tier: {tier}
folder: {folder}
difficulty: {diff}
depends_on:
used_by:
related:
tags:
  - {code.lower()}
  - foundational
status: draft
version: 0
layout: default
parent: "{parent_title}"
grand_parent: "Technical Dictionary"
nav_order: {nnn}
permalink: {permalink_base}{slug}/
---

# {fid} - {title}

> Entry stub. Generate full v4.0 content using the Master Prompt.
"""
    filepath.write_text(content, encoding="utf-8")
    return True

def update_index(index_path, new_rows):
    """Append new_rows to the index.md table and update count line."""
    if not index_path.exists() or not new_rows:
        return
    text = index_path.read_text(encoding="utf-8")

    # Find end of existing table
    table_end_m = re.search(r"(\| *[A-Z]+-\d+ *\|[^\n]*\n)(?!\|)", text)
    if not table_end_m:
        # Fallback: just append rows
        new_text = text.rstrip() + "\n" + "\n".join(new_rows) + "\n"
    else:
        insert_pos = table_end_m.end()
        new_text = text[:insert_pos] + "\n".join(new_rows) + "\n" + text[insert_pos:]

    # Update keywords count line
    all_rows = re.findall(r"^\| *([A-Z]+-\d+) *\|", new_text, re.MULTILINE)
    if all_rows:
        count = len(all_rows)
        first_id = all_rows[0]
        last_id  = all_rows[-1]
        new_text = re.sub(
            r"\*\*Keywords:\*\*[^\n]*",
            f"**Keywords:** {first_id}--{last_id} ({count} terms)",
            new_text)

    index_path.write_text(new_text, encoding="utf-8")

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    total_created = 0
    for code, gaps in GAPS.items():
        cat_name, tier, folder, permalink_base = CATS[code]
        cat_dir = BASE / tier / folder
        if not cat_dir.exists():
            print(f"[WARN] directory not found: {cat_dir}")
            continue

        index_path = cat_dir / "index.md"
        parent_title = get_index_title(index_path) or cat_name

        max_id = get_current_max_id(cat_dir, code)
        print(f"\n{code}: current max={max_id}, adding {len(gaps)} stubs")

        new_index_rows = []
        for title, diff in gaps:
            max_id += 1
            created = create_stub(cat_dir, code, max_id, title, diff,
                                  cat_name, tier, folder, permalink_base, parent_title)
            if created:
                fid = f"{code}-{str(max_id).zfill(3)}"
                new_index_rows.append(f"| {fid} | {title} | {diff} |")
                total_created += 1
                print(f"  + {fid}: {title}")

        if new_index_rows:
            update_index(index_path, new_index_rows)

    print(f"\n=== Total stubs created: {total_created} ===")

if __name__ == "__main__":
    main()
