#!/usr/bin/env python3
"""Upgrade MSV-046 through MSV-055 from v2.1 to v3.0."""
import pathlib

BASE = pathlib.Path(
    r"c:\ASK\MyWorkspace\sk-keys\dictionary"
    r"\tier-5-distributed-architecture\MSV-microservices"
)

def upgrade(filename, evo, tw_principle, tw_bullets, st,
            q1_hint, q2_hint, q3_text, q3_hint):
    fp = BASE / filename
    c = fp.read_text(encoding="utf-8")
    if "status: draft" in c:
        c = c.replace("status: draft", "status: complete")
    elif "status: complete" not in c:
        fm_end = c.index("\n---\n", 3)
        c = c[:fm_end] + "\nstatus: complete" + c[fm_end:]
    inv_pos = c.find("**THE INVENTION MOMENT:**")
    if inv_pos >= 0:
        sep_pos = c.find("\n---", inv_pos)
        c = c[:sep_pos] + f"\n\n**EVOLUTION:**\n{evo}" + c[sep_pos:]
    else:
        print(f"  WARNING: INVENTION MOMENT not found in {filename}")
    tw_block = (
        "### \U0001f48e Transferable Wisdom\n\n"
        f"**Reusable Engineering Principle:**\n{tw_principle}\n\n"
        "**Where else this pattern appears:**\n" + tw_bullets
    )
    st_block = f"### \U0001f4a1 The Surprising Truth\n\n{st}"
    think_header = "### \U0001f9e0 Think About This Before We Continue"
    think_pos = c.find(think_header)
    if think_pos >= 0:
        dash_before = c.rfind("\n---\n", 0, think_pos)
        if dash_before >= 0:
            c = (c[:dash_before]
                 + "\n\n---\n\n" + tw_block
                 + "\n\n---\n\n" + st_block
                 + c[dash_before:])
        else:
            print(f"  WARNING: sep before Think not found in {filename}")
    else:
        print(f"  WARNING: Think section not found in {filename}")

    def insert_hint(text, q_marker, next_marker, hint):
        q_pos = text.find(q_marker)
        if q_pos < 0:
            return text
        next_pos = text.find(next_marker, q_pos + len(q_marker))
        if next_pos < 0:
            return text.rstrip() + f"\n\n*Hint:* {hint}\n"
        insert_at = text.rfind("\n\n", q_pos, next_pos)
        if insert_at < 0:
            insert_at = next_pos
        return text[:insert_at] + f"\n\n*Hint:* {hint}" + text[insert_at:]

    c = insert_hint(c, "**Q1.**", "**Q2.**", q1_hint)
    c = insert_hint(c, "**Q2.**", "**Q3.**", q2_hint)
    c = c.rstrip() + f"\n\n{q3_text}\n\n*Hint:* {q3_hint}\n"
    fp.write_text(c, encoding="utf-8")
    print(f"OK: {filename}")


upgrade(
    "MSV-046 - Database per Service.md",
    evo=(
        "Database per Service emerged as the defining constraint of microservices "
        "architecture, formalised by Sam Newman in 'Building Microservices' "
        "(2015). This was a direct reaction against SOA's integration database "
        "pattern where multiple services shared tables and foreign keys. Netflix, "
        "Amazon, and other early adopters independently discovered that shared "
        "databases were the primary source of deployment coupling. The Twelve-"
        "Factor App (Adam Wiggins, 2011) established database as a 'backing "
        "service' attached to a single application. The discipline evolved from "
        "'one big database' to 'each service owns its database, optimised for "
        "its specific access patterns.'"
    ),
    tw_principle=(
        "Each service should use the database type best suited to its access "
        "patterns. An inventory service (point lookups, write-heavy) may be "
        "optimally served by a key-value store. A search service (full-text "
        "queries) by Elasticsearch. A recommendation service (graph traversals) "
        "by a graph database. Forcing all services to use the same database "
        "type means most services use a suboptimal tool. Freedom to choose "
        "the right database per service is a key benefit of data isolation."
    ),
    tw_bullets=(
        "- **Polyglot persistence:** Each microservice chooses the database "
        "type best suited to its workload (PostgreSQL for transactions, Redis "
        "for caching, Elasticsearch for search) - data isolation enables "
        "optimisation per service.\n"
        "- **Team autonomy:** Each team owns its schema and evolves it without "
        "coordinating with other teams - data isolation enables independent "
        "deployment.\n"
        "- **Independent scaling:** A high-read service scales its read replicas "
        "independently of a high-write service's primary - data isolation enables "
        "independent capacity management."
    ),
    st=(
        "Database per Service has a hidden cost teams rarely plan for: "
        "operational overhead grows linearly with service count. 20 services "
        "= 20 database instances to monitor, backup, patch, and tune. AWS "
        "RDS for 20 independent instances with proper HA and backup can cost "
        "$10-50K/month. Teams that start with 5 services (cheap) find the "
        "cost prohibitive at 50 services (expensive). The practical solution "
        "is a multi-tenant database platform (AWS Aurora clusters with schema "
        "isolation, or Kubernetes database operators) that provides logical "
        "isolation with reduced physical resource overhead."
    ),
    q1_hint=(
        "Think about what 'platform-level investment' means for reducing "
        "per-database operational overhead: (1) a Kubernetes Database Operator "
        "(CloudNativePG, Percona XtraDB) that automates deployment, backup, "
        "and scaling using consistent CRDs - one operator manages all 20 DBs; "
        "(2) centralised secret management (HashiCorp Vault) that automates "
        "credential rotation for all 20 databases without per-DB manual work; "
        "(3) unified observability (Prometheus database exporters + single "
        "Grafana dashboard template) that monitors all 20 databases from one "
        "interface with one alerting configuration."
    ),
    q2_hint=(
        "Think about what the data flow should look like: Customer Service "
        "(authoritative) publishes CustomerEvent to Kafka (durable, replicated) "
        "→ Analytics Service consumes from Kafka and writes to ClickHouse. "
        "If ClickHouse is down for 4 hours: events accumulate in the Kafka "
        "topic (no data loss, Kafka retains based on retention config). When "
        "ClickHouse recovers, Analytics Service resumes consuming from the "
        "committed offset automatically. Explore whether Kafka's retention "
        "period (default 7 days) is sufficient for the maximum expected "
        "ClickHouse downtime."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A compliance requirement says all 40 "
        "service databases must be encrypted at rest and use TLS in transit, "
        "with certificates rotated quarterly. Managing this manually for 40 "
        "databases is infeasible. Design the platform architecture that enforces "
        "these controls at the platform level without requiring each team "
        "to manage encryption and certificate rotation independently."
    ),
    q3_hint=(
        "Think about where encryption and certificate management can be "
        "enforced uniformly: managed database services (AWS RDS with at-rest "
        "encryption enabled by policy, TLS enforced by parameter groups), "
        "database operators (CloudNativePG with cert-manager integration for "
        "automatic TLS certificate rotation), and central PKI (HashiCorp Vault "
        "PKI engine generates short-lived TLS certificates for each database, "
        "rotated automatically without human intervention). Explore whether a "
        "'secure by default' database provisioning template enforces all "
        "compliance controls at creation time."
    ),
)

upgrade(
    "MSV-047 - Consumer-Driven Contract Testing.md",
    evo=(
        "Consumer-Driven Contract Testing (CDCT) was formalised by Ian Robinson "
        "in his 2006 article 'Consumer-Driven Contracts: A Service Evolution "
        "Pattern' and implemented as the Pact framework (DiUS, 2013). Before "
        "CDCT, teams used either no inter-service API testing (discover breakage "
        "in production) or full integration tests against running services "
        "(expensive, slow, brittle). CDCT introduced a middle ground: consumers "
        "define what they need from providers, providers verify they fulfill "
        "all consumer contracts in CI. The discipline evolved from 'test against "
        "running services' to 'test against consumer-defined contracts.'"
    ),
    tw_principle=(
        "The consumer defines what it needs; the provider verifies it delivers "
        "what each consumer uses. This inversion of traditional API testing "
        "(provider defines the contract, consumers test against it) is the "
        "core insight of CDCT. Instead of 'does the provider return what it "
        "says it returns?' the question is 'does the provider return what "
        "each consumer actually uses?' These are different questions with "
        "different answers, and CDCT answers the more operationally useful one."
    ),
    tw_bullets=(
        "- **Database schema migration:** A migration that checks whether "
        "columns being removed are used by any application query is CDCT "
        "applied to schema evolution - consumer-driven schema change safety.\n"
        "- **API documentation:** Documentation that only describes fields "
        "consumers actually use (not all fields the provider returns) is "
        "consumer-driven documentation rather than provider-defined.\n"
        "- **Feature flags:** Removing a feature flag only after verifying "
        "all consumers have stopped referencing it is CDCT applied to "
        "feature flag lifecycle management."
    ),
    st=(
        "Consumer-Driven Contract Testing has a subtle failure mode: it cannot "
        "test non-functional requirements. A CDCT contract verifies that the "
        "provider returns `{ id, name, price }` with correct types. It cannot "
        "verify the provider returns this in under 50ms, handles 1000 concurrent "
        "consumers, or handles malformed input correctly. Teams that adopt "
        "CDCT sometimes reduce or eliminate integration and performance testing, "
        "assuming CDCT covers everything. CDCT covers functional contract "
        "compatibility only - it is not a replacement for integration, "
        "performance, or security testing."
    ),
    q1_hint=(
        "Think about what CDCT workflow means for field removal: does any "
        "consumer pact mention `stockCount`? The Order Service pact specifies "
        "only `{ id, name, price }` - no `stockCount`. The CI pipeline checks "
        "ALL consumer pacts in the Pact Broker. If no pact includes `stockCount` "
        "in its expectations, removing it does not break any consumer contract. "
        "The pipeline should ALLOW this change. If another consumer pact (e.g., "
        "Warehouse Service) had specified `stockCount`, the pipeline would "
        "BLOCK the removal until that consumer updates its pact."
    ),
    q2_hint=(
        "Think about when CDCT is not the right tool: (1) the contract is "
        "a binary protocol or stateful workflow that cannot be expressed as "
        "request/response pairs; (2) the consumer is a third-party that cannot "
        "publish Pact contracts (public APIs for external developers); (3) the "
        "interaction is time-dependent or stateful (sequential workflows that "
        "require a running environment). Explore whether the 5 non-adopting "
        "teams have legitimate technical reasons (binary protocols, external "
        "consumers) or whether the barrier is tooling setup complexity that "
        "a shared Pact library could address."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your CDCT setup has 20 consumer teams "
        "publishing contracts to the Pact Broker. A governance requirement "
        "adds human review of contract changes before CI can proceed. Currently "
        "contracts are automatically verified. Design the governance model "
        "that adds human review without breaking the CI/CD feedback loop."
    ),
    q3_hint=(
        "Think about what 'human review without breaking CI/CD' means: "
        "automated verification (does the contract still pass?) should always "
        "run without waiting for human input. Human review (is this contract "
        "change intended?) should be required only for specific categories "
        "of breaking change (new required field, removing a field, changing "
        "a type). Explore whether a separate deployment gate (automated CI "
        "verification always runs; human approval required only for changes "
        "that match a 'breaking change' detection rule) achieves both "
        "automated feedback and governance without blocking the pipeline for "
        "non-breaking changes."
    ),
)

upgrade(
    "MSV-048 - Pact (Contract Testing).md",
    evo=(
        "Pact was created at DiUS (Australia) in 2013 as an open-source "
        "implementation of Consumer-Driven Contract Testing for REST APIs. "
        "Initially Java and Ruby only, the framework expanded to JavaScript, "
        "Python, Go, PHP, and Scala by 2016. PactFlow (commercial Pact Broker "
        "as a service) launched in 2019. Pact messaging (async/event contracts) "
        "and bi-directional contract testing (comparing OpenAPI specs against "
        "consumer contracts) were added in 2020-2022. The discipline evolved "
        "from 'REST contract testing only' to 'contract testing for any "
        "protocol or message format including Kafka events.'"
    ),
    tw_principle=(
        "Pact makes consumer dependencies explicit, versioned, and testable. "
        "Before Pact, what each consumer needed from a provider was implicit "
        "(reading source code) or separately documented (OpenAPI specs that "
        "diverged from reality). Pact makes the consumer's actual usage the "
        "test case, providing a continuously verified contract between every "
        "consumer-provider pair. The same principle applies to dependency "
        "management: actual used dependencies are more accurate than declared "
        "dependencies."
    ),
    tw_bullets=(
        "- **OpenAPI specifications:** OpenAPI is provider-driven (the provider "
        "says what it returns). Pact is consumer-driven (each consumer says "
        "what it uses). Both describe the same API from different perspectives.\n"
        "- **GraphQL schemas:** A GraphQL query is a consumer-driven contract "
        "- the consumer specifies exactly what fields it needs. The schema "
        "type system verifies the provider can fulfill all queries.\n"
        "- **Feature flags:** A feature flag dependency (flag X must exist "
        "with boolean type) is the same pattern as a Pact field contract - "
        "consumer declares what it depends on."
    ),
    st=(
        "Pact's most counterintuitive failure mode is test pollution from "
        "overly specific matchers. A consumer that uses `equalTo('John')` "
        "instead of `type(String)` in their Pact contract will cause provider "
        "verification to fail every time test data changes - even if the "
        "contract is still satisfied. The correct practice is to use type "
        "matchers (`type`, `eachLike`, `regex`) rather than exact value "
        "matchers. Teams that don't learn this lesson spend significant time "
        "debugging failing Pact tests caused by overly specific test data, "
        "not real API compatibility issues."
    ),
    q1_hint=(
        "Think about what 'Order Service adds a new field to their product "
        "pact' means for the CI pipeline: Order Service publishes updated pact "
        "to Pact Broker → Product Service CI runs pact verification → Product "
        "Service fails verification (it doesn't yet return the new field) → "
        "'can-i-deploy' check fails for Order Service (its pact is not "
        "verified against the current production Product Service). Explore "
        "whether 'pending pacts' (Order Service's new pact is marked pending, "
        "doesn't block Product Service deployment, but does block Order Service "
        "deployment until Product Service has verified it) is the correct tool "
        "for managing this contract evolution."
    ),
    q2_hint=(
        "Think about what the migration sequence must be: consumers must "
        "remove their dependency before the provider removes the field. "
        "Deployment order: (1) identify all consumer pacts referencing "
        "`categoryId`; (2) each consumer team updates their code and pact "
        "to use Category Service instead; (3) consumers deploy without "
        "`categoryId` in their pact; (4) Pact Broker shows zero consumer "
        "pacts reference `categoryId`; (5) Product Service removes `categoryId` "
        "from its response and deploys. The Pact Broker's 'can-i-deploy' "
        "check at step 5 confirms no consumer pact references the removed "
        "field before the deploy is allowed."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** 15 consumer services publish contracts for "
        "5 provider services. After 6 months you have 200 historical pact "
        "versions in the Pact Broker. Provider CI pipelines verify all "
        "200 versions, slowing CI significantly. Design the Pact Broker "
        "maintenance strategy that keeps CI fast without losing the "
        "protection CDCT provides."
    ),
    q3_hint=(
        "Think about which pact versions actually need verification: the "
        "version currently deployed in production (always), the version being "
        "deployed now (always), and the latest version on each consumer's "
        "main branch (for catching issues before production). Explore whether "
        "Pact Broker's 'consumer version selectors' (verify only "
        "'deployedOrReleased' + 'mainBranch' + 'matchingBranch' rather than "
        "all historical versions) eliminate the need to verify 200 versions, "
        "and what the minimum set of versions is that maintains the contractual "
        "safety guarantee."
    ),
)

upgrade(
    "MSV-049 - Cross-Cutting Concerns.md",
    evo=(
        "Cross-cutting concerns became a recognised category in software "
        "engineering with Aspect-Oriented Programming (AOP, Gregor Kiczales, "
        "1997), providing language-level mechanisms for separating logging, "
        "security, and transaction management from business logic. In "
        "microservices, the problem intensified: each service independently "
        "implementing security, observability, and resilience created "
        "proliferating inconsistent implementations. Netflix's Prana sidecar "
        "(2012) and Lyft's Envoy (2016) formalised the sidecar pattern for "
        "cross-cutting concerns. Service meshes (Istio, 2017) centralised "
        "management at the platform level. The discipline evolved from "
        "'implement in each service' to 'delegate to infrastructure.'"
    ),
    tw_principle=(
        "Cross-cutting concerns (authentication, logging, tracing, retry, "
        "rate limiting) should be applied uniformly and managed centrally. "
        "When each service implements them independently, consistency is "
        "impossible to enforce. A single bug in custom authentication logic "
        "exists in N different implementations. A logging format change "
        "requires N deployments. Centralising into a shared layer (service "
        "mesh, API gateway, shared libraries) means changes propagate "
        "automatically without per-service action."
    ),
    tw_bullets=(
        "- **OS kernel:** The kernel handles cross-cutting concerns for all "
        "user programs (memory management, file I/O, scheduling). Applications "
        "don't implement their own memory allocators.\n"
        "- **Spring AOP:** @Transactional, @Cacheable, and @Secured apply "
        "cross-cutting concerns to any method via AOP without code duplication "
        "in business logic.\n"
        "- **Kubernetes admission controllers:** Enforce cross-cutting policies "
        "(resource limits, pod security standards, label requirements) on all "
        "pods without requiring each manifest to include them explicitly."
    ),
    st=(
        "Service meshes, which were designed to centralise cross-cutting "
        "concerns, often require each service to still implement some concerns "
        "at the application level. Authentication with complex business rules "
        "(multi-tenant access, per-resource permissions, dynamic ABAC policies) "
        "cannot be delegated to a service mesh because the mesh doesn't have "
        "access to the application's business context. Teams that try to "
        "implement all authentication in the mesh discover this limit and end "
        "up with hybrid implementations - which is often the correct design "
        "but requires explicit documentation of what is handled where."
    ),
    q1_hint=(
        "Think about prioritisation criteria: impact (how many services "
        "affected), risk (how often does the inconsistency cause incidents), "
        "and leverage (how much benefit does centralisation provide). JWT "
        "validation is highest priority: inconsistent implementations create "
        "security vulnerabilities across all services simultaneously. "
        "Distributed tracing is second: without consistent correlation IDs, "
        "incident investigation is impossible. Retry logic is third: "
        "inconsistent retries cause retry storms. Migration path for JWT "
        "centralisation: deploy API gateway JWT validation → keep per-service "
        "validation as fallback → verify no false positives → remove per-"
        "service validation."
    ),
    q2_hint=(
        "Think about the clean separation between gateway and service "
        "concerns: the gateway handles infrastructure authentication (is the "
        "JWT valid? is the token expired? is the signature correct?) and passes "
        "claims in headers (X-User-Id, X-Tenant-Id, X-Roles). The service "
        "handles authorization (does this user have permission to access this "
        "specific resource with this tenant context?) using its own business "
        "logic and the claims provided by the gateway. The service never "
        "validates the JWT itself - it trusts the gateway's claims passed "
        "in headers."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A critical security bug is found in the "
        "JWT validation code in your shared cross-cutting concerns library. "
        "All 25 services must upgrade within 24 hours. Currently, upgrading "
        "requires each team to update the dependency version, run tests, and "
        "deploy. Design a process to patch all 25 services within the SLA."
    ),
    q3_hint=(
        "Think about what controls the upgrade time: dependency version pinning "
        "(each service has `library: 1.2.3` hardcoded), CI pipeline duration "
        "(if each service's pipeline takes 30 min, 25 services takes 12.5 "
        "hours sequentially), and human approval gates (blocking automated "
        "deployment). Explore whether an automated bot that opens dependency "
        "bump PRs across all 25 repositories simultaneously, combined with "
        "pre-approved emergency deployment gates (bypass normal review for "
        "security patches in a defined emergency window), reduces the actual "
        "time to under 24 hours."
    ),
)

upgrade(
    "MSV-050 - Distributed Logging.md",
    evo=(
        "Distributed logging evolved from per-host log files (1990s) to "
        "centralised log aggregation as distributed systems multiplied the "
        "number of hosts. Splunk (2004) introduced centralised search. The "
        "ELK Stack (Elasticsearch, Logstash, Kibana, 2010-2013) made "
        "centralised aggregation open-source and accessible. Structured "
        "logging (logs as JSON rather than unstructured text) became standard "
        "with Logback/Log4j2 in Java and Winston in Node.js. OpenTelemetry "
        "Logs (2021) standardised log format across platforms. The discipline "
        "evolved from 'grep through log files on each server' to 'centralised, "
        "structured, correlated, searchable logs across all services.'"
    ),
    tw_principle=(
        "A log line is only useful if it can be found. A log line in a format "
        "that can't be indexed, or lacking a correlation ID linking it to "
        "other log lines, might as well not exist. The discipline of structured "
        "logging (consistent field names, consistent formats, correlation IDs "
        "in every log line) is not about aesthetics - it is about making log "
        "lines findable in under 60 seconds during a production incident."
    ),
    tw_bullets=(
        "- **Database slow query logs:** A database's slow query log is "
        "structured logging applied to query execution - consistent records "
        "of events that can be analysed centrally to find performance issues.\n"
        "- **Web server access logs:** Apache/nginx access logs in combined "
        "format are an early form of structured logging - consistent fields "
        "(IP, method, URL, status, time) enabling programmatic analysis.\n"
        "- **Security audit logs:** An immutable audit log with consistent "
        "fields (who, what, when, where) is structured distributed logging "
        "applied to security compliance requirements."
    ),
    st=(
        "The correlation ID, which seems like a simple string to thread through "
        "all services, is one of the hardest things to implement correctly in "
        "a distributed system. Services receive the correlation ID from HTTP "
        "headers, store it in thread-local storage, pass it to async threads "
        "via context propagation, include it in Kafka message headers, "
        "reconstruct it when consuming from Kafka, and propagate it to all "
        "downstream calls. Every step is an opportunity to lose it. Teams that "
        "carefully implement correlation ID propagation in synchronous HTTP "
        "calls frequently find that their Kafka consumers don't propagate it "
        "at all, breaking the trace at every async boundary."
    ),
    q1_hint=(
        "Think about 5 root causes for missing correlation ID results in "
        "Kibana: (1) service doesn't propagate the correlation ID header to "
        "the next service in the chain (omission in the HTTP client "
        "interceptor); (2) different field names across services (some use "
        "`correlationId`, others `requestId` or `traceId` - Kibana search "
        "finds only the exact field name queried); (3) log aggregation lag "
        "(logs from 2 services haven't been indexed yet - check most recent "
        "log timestamp per service); (4) log format mismatch (service logs "
        "correlation ID as a nested JSON field, not top-level, making it not "
        "directly searchable by Kibana); (5) log shipping failure (Filebeat "
        "on that service's host is down)."
    ),
    q2_hint=(
        "Think about the log volume difference: INFO = 50,000 req/s * 10 "
        "lines = 500,000 lines/s. DEBUG = 50,000 * 100 = 5,000,000 lines/s "
        "(10x more). At 1KB/line: INFO = 500 MB/s, DEBUG = 5 GB/s. For 7 "
        "days: DEBUG = ~3 PB. Explore whether Spring Boot's "
        "`/actuator/loggers` endpoint (allows runtime log level changes per "
        "class or package without restart), combined with a feature-flag-"
        "based log sampling (enable DEBUG only for requests matching a "
        "specific user ID or session ID header), provides targeted debug "
        "visibility without the 10x cost."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your ELK log pipeline processes 500,000 "
        "lines/second. Logstash is the bottleneck, taking 2 seconds to process "
        "each batch. During incidents, engineers need log results within 5 "
        "seconds. Design the pipeline architecture that achieves sub-5-second "
        "log availability without replacing ELK."
    ),
    q3_hint=(
        "Think about what Logstash processing overhead includes: parsing "
        "unstructured log text (regex patterns), field extraction, and "
        "enrichment. If logs are already structured JSON, Logstash processing "
        "is minimal (passthrough routing). Explore whether (a) moving to "
        "structured JSON logging eliminates Logstash parsing overhead entirely, "
        "(b) Filebeat's direct Elasticsearch output (bypassing Logstash for "
        "structured logs while keeping Logstash for legacy unstructured logs), "
        "or (c) Kafka as a buffer between services and Logstash decouples log "
        "emission latency from Logstash processing latency so engineers see "
        "logs in Kafka immediately even if Logstash is behind."
    ),
)

upgrade(
    "MSV-051 - Correlation ID (Microservices).md",
    evo=(
        "Correlation IDs emerged as a practical response to debugging complexity "
        "in distributed systems. Early distributed systems (1990s) had no "
        "standardised way to link related log entries across services. Financial "
        "transaction systems began using reference numbers to link related "
        "operations. The microservices movement (2012-2015) made correlation "
        "IDs standard practice. Zipkin's trace ID (2012) and Jaeger's (2015) "
        "formalised distributed tracing as a superset. HTTP headers "
        "(X-Request-Id, X-Correlation-Id, X-B3-TraceId) became de facto "
        "standards. OpenTelemetry (2019) standardised trace context propagation "
        "across all communication protocols."
    ),
    tw_principle=(
        "A correlation ID is a causal link between distributed events. Every "
        "log line, every trace span, and every metric data point that belongs "
        "to the same user request should share the same correlation ID. The "
        "correlation ID transforms a distributed system (many independent log "
        "streams) into a single traceable workflow visible in one search. The "
        "same principle governs financial reference numbers, email thread IDs, "
        "and distributed database transaction IDs."
    ),
    tw_bullets=(
        "- **Financial transaction reference numbers:** A wire transfer "
        "reference links all related banking operations (debit, credit, "
        "confirmation, audit) across multiple bank systems - correlation ID "
        "applied to financial workflows.\n"
        "- **Email thread IDs:** The References and In-Reply-To email headers "
        "link all messages in a conversation thread - correlation ID applied "
        "to asynchronous messaging.\n"
        "- **Database transaction IDs:** A transaction ID links all SQL "
        "operations across multiple connections and nodes - correlation ID "
        "at the database engine level."
    ),
    st=(
        "Correlation IDs have a fundamental edge case teams rarely handle: "
        "what happens when one user request generates multiple asynchronous "
        "workflows? An e-commerce checkout generates an immediate "
        "OrderConfirmed response AND triggers async OrderProcessing, async "
        "InventoryReservation, and async EmailNotification - each potentially "
        "running hours later. The original correlation ID links to the user's "
        "checkout request, but the async workflows may run after that request "
        "is long forgotten. The correct solution is a hierarchical trace model: "
        "the original correlation ID (parent span) spawns child spans for each "
        "async workflow. This is exactly what distributed tracing (OpenTelemetry, "
        "Jaeger) implements."
    ),
    q1_hint=(
        "Think about 3 reasons why 2 services might be missing: (1) the "
        "service does not forward the correlation ID header to downstream "
        "services (omission in the HTTP client configuration - fix: add MDC "
        "propagation + outgoing header injection in the HTTP client interceptor); "
        "(2) the service uses a different field name for the correlation ID in "
        "its log output (fix: standardise field name across all services via "
        "shared logging configuration or library); (3) log aggregation failure "
        "for that service (Filebeat/Fluentd agent on the host is down - fix: "
        "check agent status, restart if needed)."
    ),
    q2_hint=(
        "Think about what the Kafka message header must contain: a "
        "`correlationId` header with the originating request's correlation ID. "
        "Consumer implementation: extract the header "
        "(`record.headers().lastHeader('correlationId')`), put it in MDC "
        "(`MDC.put('correlationId', id)`), propagate it to all downstream "
        "HTTP calls via an interceptor that adds `X-Correlation-Id: "
        "${MDC.get('correlationId')}` to every outbound request. Clear MDC "
        "after processing completes (`MDC.clear()`) to prevent ID leakage "
        "to subsequent messages."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your correlation ID implementation works "
        "correctly for synchronous HTTP calls. A batch job processes 1 million "
        "records overnight, each triggering downstream service calls. You need "
        "each record's processing to have a unique correlation ID linking all "
        "downstream calls for that record. Design the correlation ID strategy "
        "for batch processing."
    ),
    q3_hint=(
        "Think about what 'correlation ID per record' means for a batch job: "
        "each record gets a unique ID generated at batch start (UUID or derived "
        "from the record's natural key). This ID is set in MDC at the start "
        "of each record's processing and cleared at the end. Downstream HTTP "
        "calls include the ID in headers. Explore whether the batch job's "
        "progress logs (started processing record X at time T) should also "
        "include the same correlation ID, linking the batch job's operational "
        "metrics to each individual record's downstream traces for "
        "end-to-end visibility."
    ),
)

upgrade(
    "MSV-052 - OpenTelemetry (Microservices).md",
    evo=(
        "OpenTelemetry (OTel) was formed in 2019 from the merger of OpenTracing "
        "(2016) and OpenCensus (2018). OpenTracing provided a vendor-neutral "
        "tracing API; OpenCensus provided vendor-neutral metrics. The merger "
        "created a single observability framework covering traces, metrics, "
        "and logs with one SDK per language. CNCF graduated OpenTelemetry in "
        "2023. The discipline evolved from vendor-specific observability SDKs "
        "(Datadog agent, Jaeger SDK, Prometheus SDK) to a single vendor-neutral "
        "SDK that exports to any backend via the standardised OTLP protocol."
    ),
    tw_principle=(
        "Vendor-neutral observability is a strategic investment. Locking into "
        "a vendor-specific observability SDK means switching backends requires "
        "code changes across every service. OpenTelemetry separates the "
        "instrumentation (SDK in the service) from the backend (Datadog, "
        "Jaeger, Prometheus) via a standardised protocol (OTLP). The same "
        "principle governs JDBC (separates SQL code from DB vendor), JMS "
        "(separates messaging code from broker vendor), and Terraform "
        "(separates infrastructure code from cloud provider)."
    ),
    tw_bullets=(
        "- **JDBC database drivers:** JDBC separates application SQL code from "
        "the database vendor - switch databases by changing the driver, not "
        "the application code. Same principle as OTel separating "
        "instrumentation from the observability backend.\n"
        "- **JMS messaging:** JMS separates messaging code from the broker "
        "vendor (ActiveMQ, RabbitMQ) - switch brokers by changing JMS "
        "configuration, not application code.\n"
        "- **Kubernetes CSI drivers:** Container Storage Interface separates "
        "Kubernetes storage claims from the underlying storage provider - same "
        "vendor-neutral abstraction pattern."
    ),
    st=(
        "Adding OTel instrumentation to a service increases its memory usage "
        "significantly at high throughput - not because of the traces "
        "themselves, but because of the span batching buffer. OTel SDKs buffer "
        "spans in memory before exporting to the collector. At 10,000 spans/s "
        "with a 5-second export interval and 1KB per span, the in-memory buffer "
        "contains 50MB of spans at any moment. If the OTel Collector is "
        "unavailable, the buffer fills and spans are dropped - not retried, "
        "just dropped. Teams that monitor their OTel SDK buffer fill rate "
        "discover this failure mode before it causes span loss; teams that "
        "don't discover it only during a Collector outage."
    ),
    q1_hint=(
        "Think about the migration sequence with no big-bang cutover: (a) "
        "deploy OTel Collector alongside existing Zipkin; (b) configure OTel "
        "Collector to export to BOTH Zipkin AND the new OTel backend in "
        "parallel; (c) instrument one service with OTel SDK (replace Zipkin "
        "SDK), configure it to export to OTel Collector; (d) verify that "
        "service's traces appear in Zipkin (via Collector forwarding) and in "
        "OTel backend; (e) migrate remaining services one by one with the "
        "same validation; (f) when all services are migrated, retire the "
        "Zipkin SDK dependency and optionally the Zipkin backend."
    ),
    q2_hint=(
        "Think about what 2.5M spans/second at 1KB means: 2.5 GB/second. "
        "At 7-day retention: 2.5 * 86400 * 7 = ~1.5 PB. At $0.02/GB-month: "
        "~$30M/month. Tail-based sampling in OTel Collector requires keeping "
        "all spans in memory until the trace is complete, then applying the "
        "sampling decision. The Tail Sampling Processor policies: "
        "`status_code: ERROR` (100% of errors), `latency: threshold_ms=500` "
        "(100% of slow traces), `probabilistic: sampling_percentage=0.5` "
        "(0.5% of remaining). Policies are evaluated in order; first match wins."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your single OTel Collector instance "
        "processing all 25 services' spans becomes a bottleneck at peak load "
        "(50,000 req/s) and drops 15% of spans. Design the OTel Collector "
        "deployment architecture that eliminates the bottleneck without "
        "over-provisioning infrastructure."
    ),
    q3_hint=(
        "Think about OTel Collector scaling options: (a) scale up (larger "
        "instance, more CPU for parallel pipeline stages); (b) scale out "
        "(multiple Collector instances, services load-balance span export "
        "across them via a load balancer); (c) two-tier (per-node agent "
        "DaemonSet for initial collection from services on the same node - "
        "localhost export, no network overhead - plus a small number of "
        "gateway Collectors for final enrichment and export to the backend). "
        "Explore whether the per-node agent pattern eliminates the network "
        "bottleneck while the gateway Collectors can be independently scaled "
        "for the export workload."
    ),
)

upgrade(
    "MSV-053 - Chaos Engineering.md",
    evo=(
        "Chaos Engineering was pioneered by Netflix with Chaos Monkey (2010), "
        "which randomly terminated EC2 instances in production to build "
        "resilience. The approach was formalised in the 'Principles of Chaos "
        "Engineering' paper (Basiri et al., Netflix, 2016). Netflix's Simian "
        "Army expanded chaos to network latency (Latency Monkey), entire "
        "availability zones (Chaos Gorilla), and security vulnerabilities. "
        "Gremlin (2016) and LitmusChaos (2019, CNCF) made chaos engineering "
        "tooling accessible beyond Netflix. The discipline evolved from "
        "'randomly terminate instances' to 'systematically test failure "
        "hypotheses with controlled experiments and measured steady-state metrics.'"
    ),
    tw_principle=(
        "Systems that have never been tested under failure conditions will "
        "fail unexpectedly in production. Chaos engineering is the practice "
        "of deliberately introducing failure in controlled conditions to verify "
        "that the system behaves as designed - before an uncontrolled failure "
        "does. The same principle governs fire drills (test evacuation before "
        "a fire), disaster recovery testing (restore backups before a real "
        "disaster), and penetration testing (attack your own security before "
        "real attackers do)."
    ),
    tw_bullets=(
        "- **Fire drills:** An organisation that only plans evacuations without "
        "testing them will perform badly in a real fire. Chaos engineering is "
        "the fire drill for distributed systems.\n"
        "- **Disaster recovery testing:** A backup that has never been "
        "successfully restored is a backup that might not work. Chaos "
        "engineering applied to data recovery.\n"
        "- **Security penetration testing:** Deliberately attacking your own "
        "security controls (with authorisation) before attackers do - chaos "
        "engineering applied to security posture verification."
    ),
    st=(
        "The most counterintuitive finding about chaos engineering is that "
        "the most valuable experiments are the ones that pass, not the ones "
        "that fail. An experiment that passes confirms your system is resilient "
        "to that specific failure mode. An experiment that fails reveals a gap "
        "in your resilience design. Both results are valuable. Teams that run "
        "chaos experiments only when they expect to pass (to demonstrate "
        "resilience) are missing the point. The correct posture is to "
        "hypothesise resilience, design an experiment to test the hypothesis, "
        "and accept either outcome as useful data."
    ),
    q1_hint=(
        "Think about what a 'complete chaos experiment' requires structurally: "
        "steady state definition (Order Service error rate < 0.1%, P99 < 200ms, "
        "circuit breaker: closed), failure injection (block all network traffic "
        "to Inventory Service pods for 60 seconds using LitmusChaos "
        "NetworkChaos or Gremlin), abort condition (Order Service error rate "
        "> 5%, stop immediately), monitoring list (Order Service error rate, "
        "circuit breaker state, fallback activation rate, no cascading "
        "failures to Payment Service), pass criteria (CB opens within 5s, "
        "error rate < 1% after CB opens)."
    ),
    q2_hint=(
        "Think about what the experiment was designed to verify: zero downtime "
        "during pod restarts (0% error rate). The 3.2% error rate during "
        "restarts means the hypothesis is WRONG. This is a FAIL. Root causes "
        "to investigate: (1) are readiness probes configured to wait until "
        "the new pod is actually ready before routing traffic? (2) is "
        "`terminationGracePeriodSeconds` long enough for in-flight requests "
        "to complete before the pod is killed? (3) is a Pod Disruption Budget "
        "(PDB: maxUnavailable=0) preventing simultaneous pod replacements "
        "that cause momentary capacity drops?"
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your team runs chaos experiments only in "
        "staging. A product manager argues: 'Why not in production? Staging "
        "doesn't reflect real traffic.' Design the governance model and "
        "technical safeguards that make production chaos experiments safe."
    ),
    q3_hint=(
        "Think about what makes production chaos safe: steady-state definition "
        "with specific abort conditions (automatically stop if error rate "
        "exceeds X%), blast radius limits (experiment affects only N% of "
        "traffic via feature flags or canary routing), rollback capability "
        "(instant reversal of the injected failure), and time boundaries "
        "(run only during business hours when engineers are monitoring). "
        "Explore whether starting with planned, coordinated 'game days' "
        "(full team available, short windows, pre-defined rollback plan) "
        "before automated production chaos provides the right risk/benefit "
        "balance."
    ),
)

upgrade(
    "MSV-054 - Canary Deployment (Microservices).md",
    evo=(
        "Canary deployment is named after the historical practice of using "
        "canary birds in coal mines to detect dangerous gases before miners "
        "were exposed. The deployment pattern was popularised by Google's "
        "'Site Reliability Engineering' book (2016) and practiced at scale "
        "by Facebook, Netflix, and Amazon. Kubernetes added native canary "
        "support through Argo Rollouts (2019) and Flagger (2019), enabling "
        "automated progressive delivery. The discipline evolved from 'deploy "
        "to a small subset of servers, monitor manually, expand' to 'automated "
        "progressive delivery with statistical analysis and automated rollback "
        "based on configurable error rate and latency thresholds.'"
    ),
    tw_principle=(
        "Deploying to 100% of users is a risky bet. A canary deployment "
        "is the practice of making small, measurable bets: test with 1%, "
        "verify, scale to 10%, verify, scale to 100%. Each verification "
        "reduces the risk of the final 100% deployment. The same principle "
        "governs A/B testing (test features with 5% of users), feature flags "
        "(enable for 1% first), and infrastructure staged rollouts (update "
        "10% of nodes before all nodes)."
    ),
    tw_bullets=(
        "- **Feature flags:** A feature flag enabling a new feature for 1% "
        "of users before 100% is a canary deployment at the feature level - "
        "same progressive rollout, different mechanism.\n"
        "- **Database migrations (Expand-Contract):** Running a new database "
        "query for 5% of traffic and verifying correctness before expanding "
        "is canary deployment applied to data access patterns.\n"
        "- **DNS-based routing:** Weighted DNS records (1% to new IP, 99% to "
        "old IP) implement canary deployment at the network layer."
    ),
    st=(
        "Canary deployments have a statistical confidence problem teams rarely "
        "address: 5% traffic means you need 20x more total requests to achieve "
        "the same statistical significance as a full-population test. An error "
        "rate measurement at 5% traffic with 200 total canary requests means "
        "only 0.6 errors expected at 0.3% - not enough to distinguish from "
        "noise. Teams making rollback decisions based on raw error rate "
        "percentages at low canary traffic are making decisions based on "
        "statistically insignificant data. The correct approach is to define "
        "a minimum sample size (e.g., 1000 canary requests) before making "
        "any rollback decision."
    ),
    q1_hint=(
        "Think about statistical significance for error rates at 5% traffic: "
        "with 200 total canary requests and 0.3% error rate, you observe "
        "approximately 0.6 errors - effectively 0 or 1 error. This is not "
        "statistically distinguishable from the stable 0.05% rate. You need "
        "at least 1000-2000 canary requests before the difference between "
        "0.3% and 0.05% is statistically significant. At 5% traffic, that "
        "requires 20,000-40,000 total requests. Explore whether a minimum "
        "sample size threshold (wait for 2000 canary requests before evaluating "
        "error rate) combined with a Chi-squared or Wilson confidence interval "
        "provides a reliable automated rollback signal."
    ),
    q2_hint=(
        "Think about what 'old pods return errors for new pods' data means: "
        "new pods write a `discountCode` column; old pods have cached ORM "
        "entity classes without this column; when an old pod reads an order "
        "record written by a new pod, the ORM may throw an unmapped column "
        "error. The fix is the Expand-Contract pattern: (1) add `discountCode` "
        "column as nullable with default (expand - old pods still work); "
        "(2) deploy new pods that write `discountCode`; (3) wait for all old "
        "pods to be replaced; (4) remove nullable constraint (contract). "
        "Never deploy schema changes and application changes simultaneously."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A canary at 10% traffic shows 0% errors "
        "and identical P99 latency to stable. After automated promotion to "
        "100%, a bug is reported: new version processes promotional orders "
        "incorrectly, but only on Tuesdays (today is not Tuesday). How do "
        "you design a canary evaluation strategy that would catch "
        "time-dependent bugs?"
    ),
    q3_hint=(
        "Think about evaluation criteria beyond error rate and latency: "
        "business metrics (order value distribution, promotional code "
        "application rate, discount amounts) that would show anomalous "
        "values even on non-Tuesday orders if promo logic is wrong. Explore "
        "whether 'shadow comparison' (run both versions on identical orders, "
        "compare outputs) during canary would catch behavioral divergence "
        "before it affects users, and whether a minimum canary duration of "
        "7 days (covering all day-of-week traffic patterns) would catch "
        "time-dependent bugs before full promotion."
    ),
)

upgrade(
    "MSV-055 - Blue-Green Deployment.md",
    evo=(
        "Blue-Green deployment was described by Martin Fowler and popularised "
        "in Jez Humble and David Farley's 'Continuous Delivery' (2010) as a "
        "pattern for zero-downtime deployments. The pattern pre-dates "
        "microservices (used with monoliths and SOA) but became prominent with "
        "microservices due to higher deployment frequency. Cloud infrastructure "
        "made it operationally feasible by making duplicate environments cheap. "
        "Kubernetes Service objects and load balancer integrations made "
        "blue-green a native platform capability. The discipline evolved from "
        "a manual 'swap the load balancer' operation to automated, tested, "
        "rollback-capable deployment pipelines."
    ),
    tw_principle=(
        "Blue-green deployment separates the deployment step (deploy to green) "
        "from the release step (switch traffic from blue to green). This "
        "separation is the key insight: you can deploy without releasing, "
        "test in production without serving users, and roll back without "
        "redeploying. The same separation appears in feature flags (deploy "
        "with flag off, release by enabling it) and Expand-Contract database "
        "migrations (deploy schema change separately from application change)."
    ),
    tw_bullets=(
        "- **DNS TTL switching:** Changing an A record to point to a new IP "
        "is blue-green deployment at the DNS layer - deploy new servers, "
        "switch DNS, keep old servers for the rollback period.\n"
        "- **AWS Route 53 weighted routing:** Weighted records implement blue-"
        "green at the network layer - 0% to green until ready, then flip "
        "to 100%.\n"
        "- **Kubernetes Service selectors:** Changing a Service's `selector` "
        "from `version: blue` to `version: green` is blue-green at the "
        "Kubernetes platform level."
    ),
    st=(
        "Blue-green deployment has a hidden state problem teams discover in "
        "production: the two environments share stateful infrastructure "
        "(databases, caches, message queues). When traffic switches, green "
        "starts writing to the same database blue was writing to. Blue is still "
        "running as rollback. If green writes data in a format blue cannot read "
        "(new columns, changed semantics), rolling back to blue may fail because "
        "blue cannot process green's data. Teams assuming blue-green provides "
        "database state isolation discover this is false - blue-green for "
        "applications sharing stateful backends requires careful Expand-Contract "
        "database migration strategy."
    ),
    q1_hint=(
        "Think about what backward-compatible migration means for a new "
        "`promotionDetails` JSON column: (1) add the column as nullable with "
        "no default (expand); (2) green (v2) writes `promotionDetails` when "
        "available; (3) blue (v1) uses `SELECT *` which now includes "
        "`promotionDetails` - if v1's ORM has no mapping for this field it "
        "may throw an unmapped column error. The fix: use explicit column "
        "selection (not `SELECT *`) so v1 ignores new columns, OR ensure v1's "
        "ORM uses lenient deserialization that ignores unknown JSON fields. "
        "Contract phase: make `promotionDetails` required only after v1 "
        "is fully retired."
    ),
    q2_hint=(
        "Think about what the 30-second investigation window should reveal: "
        "(1) check green access logs for which specific requests fail (which "
        "payment provider? which request path?); (2) check green application "
        "logs for the specific error (null pointer, timeout, HTTP 400 from "
        "payment provider?); (3) check if the issue is a missing environment "
        "variable in green (payment provider API key not included in green's "
        "deployment config); (4) check if it's a code bug in how green "
        "handles the payment provider's callback. Rollback: switch Kubernetes "
        "Service selector back to blue, verify blue error rate returns to "
        "baseline within 30 seconds."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** 10 services use blue-green deployment. "
        "A database migration is required: add a new `order_analytics` table "
        "written by the Order Service and read by the Analytics Service. The "
        "migration must be zero-downtime and support rollback. Design the "
        "complete deployment sequence."
    ),
    q3_hint=(
        "Think about what zero-downtime database migration means with blue-"
        "green: (1) run migration to add `order_analytics` table to the shared "
        "database (backward compatible - adding a table doesn't affect existing "
        "services); (2) deploy green Order Service that writes to the new "
        "table; (3) deploy green Analytics Service that reads from it; "
        "(4) switch traffic to green services; (5) rollback to blue: blue "
        "Order Service simply doesn't write to `order_analytics` (the table "
        "exists but is unused, blue works normally). Explore whether the "
        "migration should run before deploying green services (so the table "
        "exists when green starts) rather than after."
    ),
)

print("\nBatch 5 (MSV-046 to MSV-055) complete.")
